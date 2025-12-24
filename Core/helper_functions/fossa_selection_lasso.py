import trimesh
import numpy as np
import pyvista as pv
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.widgets import LassoSelector
from matplotlib import colors
from matplotlib.collections import PolyCollection

# --------- Utilities ---------
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
    Compute (position, focal_point, view_up) oriented along `normal` while fitting the *full mesh*.
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
        position = center + n * (R * 3.0)
        focal_point = center
        return (position, focal_point, up), {"parallel_scale": R * margin}
    else:
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

# --------- Main: Lasso selection with optional camera normal ---------
def lasso_select_depth_colored(
    mesh_or_path,
    normal=None,                # <--- NEW: optional camera normal (length-3). If None, use mouse pick.
    pick_normal_first=True,     # kept for backward-compat; ignored when `normal` is provided.
    window_size=(1280, 960),
    orthographic=False,
    select_mode="centroid",     # "centroid" or "vertex_any"
    visible_only=False,         # keep False until mapping looks good
    overlay_points=True,        # filled polygon overlay (solid shape) colored by depth
    export_path=None,           # optional: save ROI with PyVista (e.g., ".stl", ".ply", ".obj")
):
    """
    Workflow:
      1) (Optional) Camera orientation:
         - If `normal` is provided (length-3), use it.
         - Else, open PyVista picker: left-click a point; camera aims along that point's normal.
      2) Off-screen PyVista renders a depth image and projects geometry to pixel coords.
      3) Matplotlib shows the depth map + projected filled polygons; user draws a lasso.
      4) On select, we extract faces inside it and build/show ROI in PyVista.

    Returns
    -------
    result : dict
        {
          "roi_pyvista": pv.PolyData or None,
          "selected_cell_ids": list[int],
        }
    """
    # --- Load/prepare mesh ---
    mesh = pv.read(mesh_or_path) if isinstance(mesh_or_path, str) else mesh_or_path
    mesh = prepare_mesh(mesh)

    # --- (1) Camera orientation: use `normal` if provided; else mouse-pick ---
    chosen_normal = np.array([0.0, 0.0, 1.0], dtype=float)

    def _is_valid_normal(n):
        try:
            n = np.asarray(n, dtype=float)
            return (n.size == 3) and (np.linalg.norm(n) > 1e-12)
        except Exception:
            return False

    if _is_valid_normal(normal):
        chosen_normal = np.asarray(normal, dtype=float)
    else:
        if pick_normal_first:
            pl_pick = pv.Plotter()
            _harden_plotter(pl_pick)
            pl_pick.add_mesh(mesh, color=True, show_edges=False)
            pl_pick.add_text(
                "Left-click a point (camera aims along its normal), then close this window.",
                font_size=12,
            )
            picked = {"pid": None, "xyz": None}

            def on_pick(point_xyz):
                if point_xyz is None:
                    return
                pid = mesh.find_closest_point(point_xyz)
                picked["pid"] = pid
                picked["xyz"] = mesh.points[pid]
                pl_pick.add_points(
                    np.array([picked["xyz"]]),
                    color="yellow",
                    render_points_as_spheres=True,
                    point_size=12,
                )
                pl_pick.render()

            pl_pick.enable_point_picking(
                callback=on_pick, left_clicking=True, pickable_window=False, show_point=False
            )
            try:
                pl_pick.show()  # BLOCKING
            finally:
                pl_pick.close()
            if picked["xyz"] is not None:
                m_norm = mesh.compute_normals(point_normals=True, inplace=False)
                n_arr = m_norm.point_data.get("Normals", None)
                if n_arr is None:
                    n_arr = getattr(m_norm, "point_normals", None)
                if n_arr is None:
                    m_norm = mesh.compute_normals(point_normals=True, inplace=False)
                    n_arr = m_norm.point_data["Normals"]
                chosen_normal = np.asarray(n_arr[picked["pid"]], dtype=float)

    # --- (2) Off-screen plotter oriented by chosen normal, fitted to full mesh (no zoom-in) ---
    pl = pv.Plotter(off_screen=True, window_size=window_size)
    _harden_plotter(pl)
    pl.add_mesh(mesh, color=True, show_edges=False, opacity=1.0)

    # Fit full mesh while oriented along the chosen normal
    view_angle_deg = getattr(pl.camera, "view_angle", 30.0)
    cam_pos, extras = camera_from_normal_fit_full(
        mesh, chosen_normal, view_angle_deg=view_angle_deg, margin=1.08, orthographic=orthographic
    )
    pl.camera_position = cam_pos
    if orthographic:
        pl.enable_parallel_projection()
        ps = extras.get("parallel_scale", float(mesh.length) / 2.0)
        try:
            pl.camera.parallel_scale = ps
        except Exception:
            pass

    # Clip range safety
    length = mesh.length
    near = max(1e-5, length * 1e-6)
    far = max(10.0 * length, 1.0)
    try:
        pl.camera.clipping_range = (near, far)
    except Exception:
        pass

    # Depth retrieval
    try:
        import inspect
        if "store_image_depth" in inspect.signature(pl.show).parameters:
            pl.show(store_image_depth=True, auto_close=False)
        else:
            raise TypeError
    except Exception:
        pl.show(auto_close=False)

    depth = pl.get_image_depth(fill_value=np.nan)
    if not np.isfinite(depth).any():
        try:
            pl.reset_camera_clipping_range()
            pl.render()
            depth = pl.get_image_depth(fill_value=np.nan)
        except Exception:
            pass

    rgb = None
    use_rgb = False
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

    if not use_rgb:
        finite_vals = depth[np.isfinite(depth)]
        if finite_vals.size:
            vmin, vmax = np.percentile(finite_vals, [2, 98])
            if vmax <= vmin:
                vmin, vmax = finite_vals.min(), finite_vals.max()
        else:
            vmin, vmax = 0.0, 1.0
        cmap_depth = plt.cm.coolwarm
        cmap_depth = cmap_depth.copy()
        cmap_depth.set_bad(color='black', alpha=1.0)
        norm_depth = colors.Normalize(vmin=vmin, vmax=vmax)
        depth_masked = np.ma.masked_invalid(depth)

    def project_to_depth_image(xd, yd):
        # Map VTK display coords to Matplotlib depth pixels (origin='lower' -> flip Y)
        return xd / sx, (rwH - 1 - yd) / sy

    # Precompute projected centroids
    cell_centers = mesh.cell_centers().points
    centroids_px = np.empty((mesh.n_cells, 2), dtype=float)
    for cid, c in enumerate(cell_centers):
        xd, yd = world_to_display(pl.renderer, c)
        x_img, y_img = project_to_depth_image(xd, yd)
        centroids_px[cid] = (x_img, y_img)

    # Project all cell vertices for polygon overlay
    vertices_px = []
    for i in range(mesh.n_cells):
        ids = mesh.get_cell(i).point_ids
        pts = mesh.points[np.array(ids)]
        proj = []
        for p in pts:
            xd, yd = world_to_display(pl.renderer, p)
            x_img, y_img = project_to_depth_image(xd, yd)
            proj.append((x_img, y_img))
        vertices_px.append(np.array(proj, dtype=float))

    # Sample depth at centroids (for face colors)
    centroid_depths = np.full(mesh.n_cells, np.nan, dtype=float)
    if not use_rgb:
        for cid, (x, y) in enumerate(centroids_px):
            px, py = int(round(x)), int(round(y))
            if 0 <= px < W and 0 <= py < H:
                centroid_depths[cid] = depth[py, px]

    # --- Matplotlib lasso UI (BLOCKING) ---
    fig, ax = plt.subplots(figsize=(7, 7))
    if use_rgb and rgb is not None:
        ax.imshow(rgb, origin='upper', extent=[0, W - 1, 0, H - 1])
        ax.set_title("RGB fallback (depth unavailable)")
    else:
        im = ax.imshow(
            depth_masked,
            cmap=cmap_depth,
            norm=norm_depth,
            origin='lower',
            extent=[0, W - 1, 0, H - 1]
        )
        ax.set_title("Depth map (deeper = red, nearer = blue)")
        plt.colorbar(im, ax=ax, label="Depth (distance to camera)")

    ax.set_xlabel("Pixel X")
    ax.set_ylabel("Pixel Y")

    # Show full image extent (no Matplotlib zoom)
    ax.set_xlim(0, W - 1)
    ax.set_ylim(0, H - 1)
    ax.set_aspect('equal')

    # Filled polygon overlay (solid shape) colored by depth
    if overlay_points and not use_rgb:
        facecolors = plt.cm.coolwarm(colors.Normalize(vmin=vmin, vmax=vmax)(centroid_depths))
        pc = PolyCollection(
            vertices_px,
            facecolors=facecolors,
            edgecolors='none',
            linewidths=0.5,
            alpha=0.85,
            closed=True
        )
        ax.add_collection(pc)
    elif overlay_points and use_rgb:
        pc = PolyCollection(
            vertices_px,
            facecolors='red',
            edgecolors='none',
            alpha=0.6,
            closed=True
        )
        ax.add_collection(pc)

    result = {"roi_pyvista": None, "selected_cell_ids": []}

    def onselect(verts):
        poly_xy = np.array(verts, dtype=float)
        # Clip lasso polygon to image bounds
        poly_xy[:, 0] = np.clip(poly_xy[:, 0], 0, W - 1)
        poly_xy[:, 1] = np.clip(poly_xy[:, 1], 0, H - 1)
        plt.close(fig)  # close Matplotlib UI

        selected_ids = []
        if select_mode == "centroid":
            # Include a cell if its centroid is inside the polygon
            for cid, (x, y) in enumerate(centroids_px):
                if 0 <= x < W and 0 <= y < H and point_in_polygon_count((x, y), poly_xy):
                    if visible_only and not use_rgb:
                        d = depth[int(round(y)), int(round(x))]
                        if not np.isfinite(d):
                            continue
                    selected_ids.append(cid)

        elif select_mode == "vertex_any":
            # Include a cell if ANY of its vertices is inside the polygon
            for cid, vp in enumerate(vertices_px):
                inside_any = False
                for (x, y) in vp:
                    if 0 <= x < W and 0 <= y < H and point_in_polygon_count((x, y), poly_xy):
                        inside_any = True
                        break
                if inside_any:
                    if visible_only and not use_rgb:
                        ok = False
                        for (x, y) in vp:
                            px, py = int(round(x)), int(round(y))
                            if 0 <= px < W and 0 <= py < H and np.isfinite(depth[py, px]):
                                ok = True
                                break
                        if not ok:
                            continue
                    selected_ids.append(cid)
        else:
            print(f"Unknown select_mode={select_mode}. Use 'centroid' or 'vertex_any'.")
            pl.close()
            return

        if not selected_ids:
            print("No cells selected. Try orthographic=True, increase window_size, "
                  "or set select_mode='vertex_any'.")
            result["roi_pyvista"] = None
            result["selected_cell_ids"] = []
        else:
            roi = mesh.extract_cells(selected_ids).clean()
            result["roi_pyvista"] = roi
            result["selected_cell_ids"] = selected_ids

            # Show result in PyVista, colored by sampled depth
            if not use_rgb:
                roi_depth = sample_depth_at_points(roi.points, pl.renderer, depth, rwW, rwH, sx, sy)
                roi.point_data['Depth'] = roi_depth
                show = pv.Plotter()
                _harden_plotter(show)
                show.add_mesh(mesh, color="lightgray", show_edges=False, opacity=0.15)
                show.add_mesh(
                    roi,
                    scalars='Depth',
                    cmap='coolwarm',
                    nan_color='black',
                    show_edges=True,
                    name="ROI",
                )
            else:
                show = pv.Plotter()
                _harden_plotter(show)
                show.add_mesh(mesh, color="lightgray", show_edges=False, opacity=0.15)
                show.add_mesh(roi, color="red", show_edges=True, name="ROI")
                show.add_text(f"Selected faces: {roi.n_cells}", font_size=12)

            show.reset_camera()
            try:
                show.show()
            finally:
                show.close()

            # Optional: export selected faces via PyVista (triangulated surface)
            if export_path:
                try:
                    roi_surface = roi.extract_surface().clean().triangulate()
                    roi_surface.save(export_path)  # native VTK writer if available
                    print(f"Saved ROI to: {export_path}")
                except ValueError as e:
                    # Fallback via meshio if VTK STL/OBJ/PLY writer isn't available
                    try:
                        pv.save_meshio(export_path, roi_surface)
                        print(f"Saved ROI via meshio to: {export_path}")
                    except Exception as e2:
                        print(f"Failed to export ROI: {e} / {e2}")

        # Cleanup off-screen plotter
        pl.close()

    # Keep strong reference; run BLOCKING show
    lasso = LassoSelector(ax, onselect=onselect)
    plt.show(block=False)

    # If user closes lasso without selecting, ensure cleanup
    try:
        pl.close()
    except Exception:
        pass

    return result

def vtk_faces_to_triangles_from_flat(faces_flat: np.ndarray):
    """
    Parse VTK PolyData faces buffer (flat array) into (n_tri, 3) triangle indices.
    Keeps only triangles (n == 3), skips other primitives.
    """
    tris = []
    i, N = 0, faces_flat.size
    while i < N:
        n = int(faces_flat[i])           # number of indices for this face
        j = i + 1
        if n <= 0 or j + n > N:
            break                        # malformed/truncated record -> stop
        if n == 3:
            tris.append([int(faces_flat[j]), int(faces_flat[j+1]), int(faces_flat[j+2])])
        # advance to next face record
        i = j + n
    return np.asarray(tris, dtype=np.int64) if tris else np.empty((0, 3), dtype=np.int64)

def find_fossa(tri_mesh:trimesh.Trimesh, normal):
    mesh = pv.wrap(tri_mesh)
    result = lasso_select_depth_colored(
        mesh_or_path=mesh,
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
    
    tri_surface = roi.extract_surface().clean().triangulate()
    vertices = np.asarray(tri_surface.points, dtype=np.float64)
    faces_vtk = np.asarray(tri_surface.faces, dtype=np.int64).ravel()

    faces_tri = vtk_faces_to_triangles_from_flat(faces_vtk)
    if faces_tri.size == 0:
        raise ValueError("No triangular faces found (after extract_surface/triangulate).")

    tmesh = trimesh.Trimesh(vertices=vertices, faces=faces_tri, process=False)
    return tmesh