
# -*- coding: utf-8 -*-
import numpy as np
import trimesh
import pyvista as pv

# --- Matplotlib setup (Qt backend) ---
import matplotlib
# For Matplotlib >= 3.6, 'QtAgg' auto-selects the Qt binding.
# If you are strictly on PyQt5, 'Qt5Agg' is also fine.
matplotlib.use('QtAgg')

import matplotlib.pyplot as plt
from matplotlib import colors

# --- PyQt imports for dialog embedding ---
from PyQt5.QtWidgets import (
    QApplication, QDialog, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel
)
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


# =============================================================================
# Utilities
# =============================================================================
def _harden_plotter(pl: pv.Plotter) -> pv.Plotter:
    """Windows stability: disable MSAA and depth peeling before any rendering."""
    try:
        pl.ren_win.SetMultiSamples(0)
    except Exception:
        pass
    try:
        pl.renderer.SetUseDepthPeeling(False)
    except Exception:
        pass
    return pl


def prepare_mesh(mesh):
    """Triangulate & clean meshes (handles degenerate cells, duplicate points)."""
    mesh = pv.wrap(mesh)
    try:
        mesh = mesh.triangulate()
    except Exception:
        pass
    try:
        mesh = mesh.clean()
    except Exception:
        pass
    return mesh


def camera_from_normal_fit_full(mesh, normal, view_angle_deg=30.0, margin=1.08, orthographic=False):
    """
    Compute (position, focal_point, view_up) oriented along `normal` while fitting the full mesh.
    - focal_point is the mesh center (prevents zooming into local area).
    - distance fits the bounding sphere for the given view_angle.
    """
    center = np.asarray(mesh.center, dtype=float)
    n = np.asarray(normal, dtype=float)
    n /= (np.linalg.norm(n) + 1e-12)

    # Make an orthonormal up vector to the view direction
    up_hint = np.array([0, 1, 0], dtype=float)
    up = up_hint - up_hint.dot(n) * n
    if np.linalg.norm(up) < 1e-12:
        alt = np.array([0.0, 0.0, 1.0])
        up = alt - alt.dot(n) * n
    up /= (np.linalg.norm(up) + 1e-12)

    # Bounding sphere radius ~ half of bounding-box diagonal
    R = float(mesh.length) / 2.0
    if orthographic:
        # For orthographic projection, distance doesn't affect scale; use a reasonable separation.
        position = center + n * (R * 3.0)
        focal_point = center
        return (position, focal_point, up), {"parallel_scale": R * margin}
    else:
        # Perspective: choose distance so the sphere of radius R fits at view_angle
        half = np.deg2rad(view_angle_deg / 2.0)
        d = (R / np.sin(half)) * margin
        position = center + n * d
        focal_point = center
        return (position, focal_point, up), {}


def point_in_polygon_count(pt, poly):
    """
    'Count' (ray crossing) method for point-in-polygon.
    pt: (x, y), poly: Nx2 array in the same coordinate system.
    Returns True if inside; False otherwise.
    """
    x, y = pt
    inside = False
    n = len(poly)
    for i in range(n):
        x1, y1 = poly[i]
        x2, y2 = poly[(i + 1) % n]
        crosses = ((y1 > y) != (y2 > y)) and (x < (x2 - x1) * (y - y1) / (y2 - y1 + 1e-12) + x1)
        if crosses:
            inside = not inside
    return inside


def world_to_display(renderer, xyz):
    """
    Convert world coordinates to VTK display (pixel) coords (TOP-LEFT origin).
    Returns (x_disp, y_disp) in device pixels of the render window.
    """
    renderer.SetWorldPoint(float(xyz[0]), float(xyz[1]), float(xyz[2]), 1.0)
    renderer.WorldToDisplay()
    x = renderer.GetDisplayPoint()[0]
    y = renderer.GetDisplayPoint()[1]
    return x, y


def sample_depth_at_points(points_xyz, renderer, depth, rwW, rwH, sx, sy):
    """
    Sample the Matplotlib depth image at projected point locations.
    Returns an array of per-point depth scalars (NaN where out-of-bounds).
    """
    H, W = depth.shape
    vals = np.full(points_xyz.shape[0], np.nan, dtype=float)
    for i, p in enumerate(points_xyz):
        xd, yd = world_to_display(renderer, p)  # VTK display (top-left, device px)
        # Map to Matplotlib depth pixels (origin='lower' -> flip Y)
        x_img = int(round(xd / sx))
        y_img = int(round((rwH - 1 - yd) / sy))
        if 0 <= x_img < W and 0 <= y_img < H:
            vals[i] = depth[y_img, x_img]
    return vals


# =============================================================================
# Dialog: Matplotlib embedded in PyQt for polygon picking
# =============================================================================
class SubmeshPickerDialog(QDialog):
    """
    Modal dialog that shows a 2D image (depth or RGB) and lets the user click a polygon.
    On 'Finish' (or Enter), it computes selected face IDs using provided pixel-space geometry.
    """
    def __init__(self, W, H, *,
                 depth_masked, use_rgb, rgb, extent,
                 vertices_px, centroids_px, centroid_depths,
                 vmin, vmax, select_mode: str, visible_only: bool,
                 overlay_points: bool, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Pick Submesh (2D projection)")
        self.W, self.H = W, H
        self.use_rgb = use_rgb
        self.select_mode = select_mode
        self.visible_only = visible_only
        self.vertices_px = vertices_px
        self.centroids_px = centroids_px
        self.centroid_depths = centroid_depths
        self.depth_masked = depth_masked
        self.vmin, self.vmax = vmin, vmax
        self.overlay_points = overlay_points
        self.extent = extent
        self.rgb = rgb

        # Outputs
        self.polygon = None
        self.selected_ids = None

        v = QVBoxLayout(self)

        # Figure/Canvas
        self.figure = Figure(figsize=(7, 7), tight_layout=True)
        self.canvas = FigureCanvas(self.figure)
        self.ax = self.figure.add_subplot(111)
        v.addWidget(self.canvas)

        # Controls
        h = QHBoxLayout()
        self.status = QLabel("0 points")
        btn_clear = QPushButton("Clear")
        btn_cancel = QPushButton("Cancel")
        btn_finish = QPushButton("Finish")
        h.addWidget(self.status); h.addStretch(1)
        h.addWidget(btn_clear); h.addWidget(btn_cancel); h.addWidget(btn_finish)
        v.addLayout(h)

        btn_clear.clicked.connect(self._on_clear)
        btn_cancel.clicked.connect(self.reject)
        btn_finish.clicked.connect(self._on_finish)

        # Draw background image (depth or RGB)
        if self.use_rgb and self.rgb is not None:
            self.ax.imshow(self.rgb, origin='upper', extent=self.extent)
            self.ax.set_title("RGB fallback (depth unavailable)")
        else:
            im = self.ax.imshow(self.depth_masked, cmap="coolwarm",
                                origin='lower', extent=self.extent,
                                vmin=self.vmin, vmax=self.vmax)
            self.figure.colorbar(im, ax=self.ax, label="Depth (distance to camera)")
            self.ax.set_title("Depth map (deeper = red, nearer = blue)")

        self.ax.set_xlabel("Pixel X")
        self.ax.set_ylabel("Pixel Y")
        self.ax.set_xlim(0, W - 1)
        self.ax.set_ylim(0, H - 1)
        self.ax.set_aspect('equal')

        # Optional: overlay projected faces as filled polygons
        from matplotlib.collections import PolyCollection
        if self.overlay_points:
            if self.use_rgb:
                pc = PolyCollection(self.vertices_px, facecolors='red',
                                    edgecolors='none', alpha=0.6, closed=True)
                self.ax.add_collection(pc)
            else:
                facecolors = plt.cm.coolwarm(
                    colors.Normalize(vmin=self.vmin, vmax=self.vmax)(self.centroid_depths)
                )
                pc = PolyCollection(self.vertices_px, facecolors=facecolors,
                                    edgecolors='none', linewidths=0.5, alpha=0.85, closed=True)
                self.ax.add_collection(pc)

        # Interactive state
        self._poly_pts = []   # [(x, y), ...]
        self._poly_line = None
        self._poly_scatter = None

        # Matplotlib event connections on the embedded canvas
        self._cid_click = self.canvas.mpl_connect('button_press_event', self._on_click)
        self._cid_key   = self.canvas.mpl_connect('key_press_event',   self._on_key)

        self.resize(960, 900)

    # --- Interaction handlers ---
    def _on_click(self, event):
        if event.inaxes != self.ax: return
        x, y = event.xdata, event.ydata
        if x is None or y is None: return
        if not (0 <= x < self.W and 0 <= y < self.H): return

        if event.button == 1:      # left-click: add point
            self._poly_pts.append((x, y))
            self._redraw_polygon()
        elif event.button == 3:    # right-click: undo
            if self._poly_pts:
                self._poly_pts.pop()
                self._redraw_polygon()

    def _on_key(self, event):
        k = (event.key or '').lower()
        if k in ('z', 'backspace', 'delete'):
            if self._poly_pts:
                self._poly_pts.pop()
                self._redraw_polygon()
        elif k == 'c':
            self._poly_pts.clear()
            self._redraw_polygon()
        elif k in ('enter', 'return'):
            self._on_finish()
        elif k in ('q', 'escape'):
            self.reject()

    def _on_clear(self):
        self._poly_pts.clear()
        self._redraw_polygon()

    def _redraw_polygon(self):
        # remove old artists
        if self._poly_line is not None:
            self._poly_line.remove()
            self._poly_line = None
        if self._poly_scatter is not None:
            self._poly_scatter.remove()
            self._poly_scatter = None

        if self._poly_pts:
            poly = np.array(self._poly_pts, dtype=float)
            closed = np.vstack([poly, poly[0]]) if len(poly) > 1 else poly
            self._poly_line, = self.ax.plot(closed[:, 0], closed[:, 1], '-o', color='C1')
            self._poly_scatter = self.ax.scatter(poly[:, 0], poly[:, 1], s=30, color='C1', zorder=3)

        self.status.setText(f"{len(self._poly_pts)} points")
        self.canvas.draw_idle()

    def _on_finish(self):
        if len(self._poly_pts) < 3:
            self.status.setText("Polygon needs ≥3 points")
            return

        poly_xy = np.array(self._poly_pts, dtype=float)
        poly_xy[:, 0] = np.clip(poly_xy[:, 0], 0, self.W - 1)
        poly_xy[:, 1] = np.clip(poly_xy[:, 1], 0, self.H - 1)

        # Selection (reusing 'count' method)
        selected_ids = []
        if self.select_mode == "centroid":
            for cid, (x, y) in enumerate(self.centroids_px):
                if 0 <= x < self.W and 0 <= y < self.H and point_in_polygon_count((x, y), poly_xy):
                    selected_ids.append(cid)
        elif self.select_mode == "vertex_any":
            for cid, vp in enumerate(self.vertices_px):
                inside_any = False
                for (x, y) in vp:
                    if 0 <= x < self.W and 0 <= y < self.H and point_in_polygon_count((x, y), poly_xy):
                        inside_any = True
                        break
                if inside_any:
                    selected_ids.append(cid)
        else:
            # fallback to centroid
            for cid, (x, y) in enumerate(self.centroids_px):
                if 0 <= x < self.W and 0 <= y < self.H and point_in_polygon_count((x, y), poly_xy):
                    selected_ids.append(cid)

        # Optional visibility filter (when depth available)
        if self.visible_only and not self.use_rgb and self.depth_masked is not None:
            # keep faces whose centroid (or any vertex) maps to a finite depth
            depth = self.depth_masked
            filt = []
            if self.select_mode == "centroid":
                for cid in selected_ids:
                    x, y = self.centroids_px[cid]
                    px, py = int(round(x)), int(round(y))
                    if 0 <= px < self.W and 0 <= py < self.H and np.isfinite(depth[py, px]):
                        filt.append(cid)
                selected_ids = filt
            else:
                # vertex_any
                filt = []
                for cid in selected_ids:
                    ok = False
                    for (x, y) in self.vertices_px[cid]:
                        px, py = int(round(x)), int(round(y))
                        if 0 <= px < self.W and 0 <= py < self.H and np.isfinite(depth[py, px]):
                            ok = True
                            break
                    if ok:
                        filt.append(cid)
                selected_ids = filt

        self.polygon = poly_xy
        self.selected_ids = selected_ids
        self.accept()


# =============================================================================
# Dialog-driven selection (Qt)
# =============================================================================
def points_select_depth_colored_qt(
    mesh_or_path,
    normal=None,                # Optional camera normal (len-3)
    pick_normal_first=True,     # ignored when `normal` provided
    window_size=(1280, 960),
    orthographic=False,
    select_mode="centroid",     # "centroid" or "vertex_any"
    visible_only=False,
    overlay_points=True,
    export_path=None            # Optional: save ROI via PyVista
):
    """
    PyQt dialog-driven selection.
    Returns:
        {
          "roi_pyvista": pv.PolyData or None,
          "selected_cell_ids": List[int],
          "points_polygon": np.ndarray (Mx2) pixel coords or None
        }
    """
    # Ensure single QApplication (not at import time)
    app = QApplication.instance()
    if app is None:
        app = QApplication([])

    # --- (A) Prepare mesh & camera ---
    mesh_in = pv.read(mesh_or_path) if isinstance(mesh_or_path, str) else pv.wrap(mesh_or_path)
    mesh_pv = mesh_in.copy(deep=True)
    mesh_pv = prepare_mesh(mesh_pv)  # triangulate/clean

    # normal selection
    def _is_valid_normal(n):
        try:
            n = np.asarray(n, dtype=float)
            return (n.size == 3) and (np.linalg.norm(n) > 1e-12)
        except Exception:
            return False

    chosen_normal = np.array([0.0, 0.0, 1.0], dtype=float)
    if _is_valid_normal(normal):
        chosen_normal = np.asarray(normal, dtype=float)
    else:
        if pick_normal_first:
            pl_pick = pv.Plotter()
            _harden_plotter(pl_pick)
            pl_pick.add_mesh(mesh_pv, color=True, show_edges=False)
            pl_pick.add_text("Left-click a point (camera aims along its normal), then close.", font_size=12)
            picked = {"pid": None, "xyz": None}

            def on_pick(point_xyz):
                if point_xyz is None:
                    return
                pid = mesh_pv.find_closest_point(point_xyz)
                picked["pid"] = pid
                picked["xyz"] = mesh_pv.points[pid].copy()
                pl_pick.add_points(np.array([picked["xyz"]]), color="yellow",
                                   render_points_as_spheres=True, point_size=12)
                pl_pick.render()

            pl_pick.enable_point_picking(callback=on_pick, left_clicking=True,
                                         pickable_window=False, show_point=False)
            try:
                pl_pick.show()  # blocking
            finally:
                pl_pick.close()

            if picked["xyz"] is not None:
                m_norm = mesh_pv.compute_normals(point_normals=True, inplace=False)
                n_arr = m_norm.point_data.get("Normals", None)
                if n_arr is None:
                    n_arr = getattr(m_norm, "point_normals", None)
                if n_arr is None:
                    m_norm = mesh_pv.compute_normals(point_normals=True, inplace=False)
                    n_arr = m_norm.point_data["Normals"]
                chosen_normal = np.asarray(n_arr[picked["pid"]], dtype=float)

    # --- (B) Off-screen render for depth & projection ---
    pl = pv.Plotter(off_screen=True, window_size=window_size)
    _harden_plotter(pl)
    pl.add_mesh(mesh_pv, color=True, show_edges=False, opacity=1.0)
    view_angle_deg = getattr(pl.camera, "view_angle", 30.0)
    cam_pos, extras = camera_from_normal_fit_full(
        mesh_pv, chosen_normal, view_angle_deg=view_angle_deg, margin=1.08, orthographic=orthographic
    )
    pl.camera_position = cam_pos
    if orthographic:
        pl.enable_parallel_projection()
        ps = extras.get("parallel_scale", float(mesh_pv.length) / 2.0)
        try:
            pl.camera.parallel_scale = ps
        except Exception:
            pass

    # Clip range safety
    length = mesh_pv.length
    near = max(1e-5, length * 1e-6)
    far = max(10.0 * length, 1.0)
    try:
        pl.camera.clipping_range = (near, far)
    except Exception:
        pass

    # Show and get depth
    try:
        import inspect
        if "store_image_depth" in inspect.signature(pl.show).parameters:
            pl.show(store_image_depth=True, auto_close=False)
        else:
            raise TypeError
    except Exception:
        pl.show(auto_close=False)
    depth = pl.get_image_depth(fill_value=np.nan)

    # RGB fallback
    rgb = None
    use_rgb = False
    if not np.isfinite(depth).any():
        try:
            pl.reset_camera_clipping_range()
            pl.render()
            depth = pl.get_image_depth(fill_value=np.nan)
        except Exception:
            pass
    if not np.isfinite(depth).any():
        try:
            rgb = pl.screenshot(return_img=True)
            use_rgb = True
        except Exception:
            pass

    H, W = depth.shape
    rwW, rwH = pl.ren_win.GetSize()
    sx = rwW / float(W) if W > 0 else 1.0
    sy = rwH / float(H) if H > 0 else 1.0

    # Depth visualization scaling
    if not use_rgb:
        finite_vals = depth[np.isfinite(depth)]
        if finite_vals.size:
            vmin, vmax = np.percentile(finite_vals, [2, 98])
            if vmax <= vmin:
                vmin, vmax = finite_vals.min(), finite_vals.max()
        else:
            vmin, vmax = 0.0, 1.0
        depth_masked = np.ma.masked_invalid(depth)
    else:
        vmin, vmax = 0.0, 1.0
        depth_masked = None

    # Project helpers
    def project_to_depth_image(xd, yd):
        # VTK display (top-left) -> Matplotlib image pixels (origin lower)
        return xd / sx, (rwH - 1 - yd) / sy

    # Precompute projected centroids (detached copy)
    cell_centers = mesh_pv.cell_centers().points.copy()
    centroids_px = np.empty((mesh_pv.n_cells, 2), dtype=float)
    for cid, c in enumerate(cell_centers):
        xd, yd = world_to_display(pl.renderer, c)
        x_img, y_img = project_to_depth_image(xd, yd)
        centroids_px[cid] = (x_img, y_img)

    # Project all cell vertices for polygon overlay (detached copies)
    vertices_px = []
    for i in range(mesh_pv.n_cells):
        ids = mesh_pv.get_cell(i).point_ids
        pts = mesh_pv.points[np.array(ids)].copy()
        proj = []
        for p in pts:
            xd, yd = world_to_display(pl.renderer, p)
            x_img, y_img = project_to_depth_image(xd, yd)
            proj.append((x_img, y_img))
        vertices_px.append(np.array(proj, dtype=float))

    # Sample depth at centroids (for face colors)
    centroid_depths = np.full(mesh_pv.n_cells, np.nan, dtype=float)
    if not use_rgb:
        for cid, (x, y) in enumerate(centroids_px):
            px, py = int(round(x)), int(round(y))
            if 0 <= px < W and 0 <= py < H:
                centroid_depths[cid] = depth[py, px]

    # --- (C) Open modal dialog and let user pick polygon ---
    dlg = SubmeshPickerDialog(
        W, H,
        depth_masked=depth_masked, use_rgb=use_rgb, rgb=rgb, extent=[0, W - 1, 0, H - 1],
        vertices_px=vertices_px, centroids_px=centroids_px, centroid_depths=centroid_depths,
        vmin=vmin, vmax=vmax,
        select_mode=select_mode, visible_only=visible_only,
        overlay_points=overlay_points, parent=None
    )
    accepted = (dlg.exec() == QDialog.Accepted)

    result = {"roi_pyvista": None, "selected_cell_ids": [], "points_polygon": None}

    if not accepted or not dlg.selected_ids:
        # user canceled or no selection
        try:
            pl.close()
        except Exception:
            pass
        result["roi_pyvista"] = None
        result["selected_cell_ids"] = []
        result["points_polygon"] = dlg.polygon
        return result

    selected_ids = dlg.selected_ids
    result["selected_cell_ids"] = selected_ids
    result["points_polygon"] = dlg.polygon

    # --- (D) Build ROI and (optionally) show / export ---
    roi = mesh_pv.extract_cells(selected_ids).clean()
    result["roi_pyvista"] = roi

    # Optional: show ROI (opens a VTK window)
    show = pv.Plotter()
    _harden_plotter(show)
    show.add_mesh(mesh_pv, color="lightgray", show_edges=False, opacity=0.15)
    if not use_rgb:
        roi_depth = sample_depth_at_points(roi.points, pl.renderer, depth, rwW, rwH, sx, sy)
        roi.point_data['Depth'] = roi_depth
        show.add_mesh(roi, scalars='Depth', cmap='coolwarm',
                      nan_color='black', show_edges=True, name="ROI")
    else:
        show.add_mesh(roi, color="red", show_edges=True, name="ROI")
    show.add_text(f"Selected faces: {roi.n_cells}", font_size=12)
    show.reset_camera()
    try:
        show.show()
    finally:
        show.close()

    if export_path:
        try:
            roi_surface = roi.extract_surface().clean().triangulate()
            roi_surface.save(export_path)
            print(f"Saved ROI to: {export_path}")
        except ValueError as e:
            try:
                pv.save_meshio(export_path, roi_surface)
                print(f"Saved ROI via meshio to: {export_path}")
            except Exception as e2:
                print(f"Failed to export ROI: {e} / {e2}")

    # Cleanup off-screen plotter
    try:
        pl.close()
    except Exception:
        pass

    return result


# =============================================================================
# Faces buffer parse helper
# =============================================================================
def vtk_faces_to_triangles_from_flat(faces_flat: np.ndarray):
    """
    Parse VTK PolyData faces buffer (flat array) into (n_tri, 3) triangle indices.
    Keeps only triangles (n == 3), skips other primitives.
    """
    tris = []
    i, N = 0, faces_flat.size
    while i < N:
        n = int(faces_flat[i])  # number of indices for this face
        j = i + 1
        if n <= 0 or j + n > N:
            break  # malformed/truncated record -> stop
        if n == 3:
            tris.append([int(faces_flat[j]), int(faces_flat[j + 1]), int(faces_flat[j + 2])])
        # advance to next face record
        i = j + n
    return np.asarray(tris, dtype=np.int64) if tris else np.empty((0, 3), dtype=np.int64)


# =============================================================================
# Public entries: build a Trimesh from selected ROI
# =============================================================================
def find_fossa_qt(mesh: trimesh.Trimesh, normal):
    """
    Launch interactive ROI selection via a PyQt modal dialog. Return a `trimesh.Trimesh`.
    """
    # DETACH: Trimesh -> new instance, then wrap to PyVista
    mesh_ui = pv.wrap(mesh.copy())  # safe detachment from analysis mesh
    result = points_select_depth_colored_qt(
        mesh_or_path=mesh_ui,
        normal=normal,
        pick_normal_first=True,
        window_size=(1280, 960),
        orthographic=False,
        select_mode="centroid",
        visible_only=False,
        overlay_points=True,
        export_path=None
    )
    roi = result["roi_pyvista"]
    if roi is None:
        return None

    tri_surface = roi.extract_surface().clean().triangulate()
    vertices = np.asarray(tri_surface.points, dtype=np.float64).copy()
    faces_vtk = np.asarray(tri_surface.faces, dtype=np.int64).ravel().copy()
    faces_tri = vtk_faces_to_triangles_from_flat(faces_vtk)
    if faces_tri.size == 0:
        raise ValueError("No triangular faces found (after extract_surface/triangulate).")
    tmesh = trimesh.Trimesh(vertices=vertices, faces=faces_tri, process=False)
    return tmesh


def find_fossa(mesh: trimesh.Trimesh, normal):
    """
    Backward-compatible entry that now uses the PyQt modal dialog.
    Your external modules can keep calling `find_fossa(mesh, normal)` as before.
    """
    return find_fossa_qt(mesh, normal)