import numpy as np
import pyvista as pv
import trimesh
import vtk
from matplotlib.path import Path

CLOSE_PX = 15   # Distance threshold in screen pixels to trigger auto-close indicator

# Windows stability: disable MSAA and depth peeling before any rendering.
def _harden_plotter(pl: pv.Plotter) -> pv.Plotter:
    
    try:
        pl.ren_win.SetMultiSamples(0)
    except Exception:
        pass
    try:
        pl.renderer.SetUseDepthPeeling(False)
    except Exception:
        pass
    return pl

# Triangulate & clean meshes (handles degenerate cells, duplicate points).
def prepare_mesh(mesh):
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


def select_submesh_3d(mesh_or_path, *args, window_size=(1280, 960), export_path=None, **kwargs):
  
    # Load and prepare geometric structures safely
    pv_mesh = pv.read(mesh_or_path) if isinstance(mesh_or_path, str) else mesh_or_path
    pv_mesh = prepare_mesh(pv_mesh)
    
    # Cache centroids and calculate normals for selection math
    raw_faces = pv_mesh.faces.reshape(-1, 4)[:, 1:].astype(np.int64)
    vertices = np.asarray(pv_mesh.points, dtype=float)
    centroids = vertices[raw_faces].mean(axis=1) #now we have the center point of every face in the mesh
    
    # Calculate cell normals
    v0, v1, v2 = vertices[raw_faces[:, 0]], vertices[raw_faces[:, 1]], vertices[raw_faces[:, 2]]
    face_normals = np.cross(v1 - v0, v2 - v0)
    norms = np.linalg.norm(face_normals, axis=1, keepdims=True)
    norms[norms == 0] = 1.0
    face_normals /= norms

    # Interaction State Tracks
    state = {
        "selected": set(),  # A Set() tracking selected face integer indices 
        "poly_3d": [],     # 3D points resting on the mesh face topology
        "press_pos": None, # Used for click-vs-drag tracking filters
    }

    if isinstance(window_size, (np.ndarray, list)) and len(window_size) == 3:
        # If a 3D coordinate point (like centers[0]) slipped into this parameter slot, reset window layout defaults
        window_size = (1280, 960)
    elif window_size is not None:
        window_size = (int(window_size[0]), int(window_size[1]))
    else:
        window_size = (1280, 960)

    plotter = pv.Plotter(window_size=window_size)
    _harden_plotter(plotter)
    
    # Instantiate a native standalone VTK picker for ray-mesh intersections
    prop_picker = vtk.vtkPropPicker()

    # Customize the mesh here
    plotter.add_mesh(
        pv_mesh, 
        color="#EAE6DF", # off-white
        show_edges=True, 
        edge_color="gray",
        opacity=0.9,
        ambient=0.2,              # Soft base lighting 
        diffuse=0.7,              # Matte surface illumination
        specular=0.3,             # Mirroring organic bone tissue
        specular_power=20.0,      # Non-metallic highlights
        name="base"
    )
    
    plotter.set_background(color="black", top="darkgray")
    plotter.title = "Fossa Selection"

    plotter.add_text(
        "Sticky 3D Lasso Mode:\n"
        "• ROTATE/ZOOM: Left-Click & Drag normally anywhere and Scroll Wheel to zoom in or out\n"
        "• ADD 3D POINT: Single Left-Click directly on the object's surface\n"
        "• DELETE PREVIOUS 3D POINT: Right-Click to delete previous marked point\n"
        "• CLOSE THE LOOP: Press RETURN or SPACE to lock in your boundary loop\n"
        "• SELECTION CONTROLS: 'c' to clear selection 's' to quick-save | ESC to discard current loop",
        font_size=11, 
        position="upper_left", 
        color="black"
    )
    
    # ----------- 3D Drawing Engine
    # Native VTK alternative to get_vector_2d for projecting 3D points to 2D pixels.
    def _world_to_screen(world_pt):
       
        coord = vtk.vtkCoordinate()
        coord.SetCoordinateSystemToWorld()
        coord.SetValue(float(world_pt[0]), float(world_pt[1]), float(world_pt[2]))
        val = coord.GetComputedDoubleDisplayValue(plotter.renderer)
        return [val[0], val[1]]

    # Handles drawing the points and the lines connecting those points as well until it makes a loop and connects to the beginning
    def redraw(cursor_3d=None):
        pts_3d = list(state["poly_3d"])
        

        # Render anchor dots at the 3D surface vertices
        if len(pts_3d) >= 1:
            dots_mesh = pv.PolyData(np.array(pts_3d))
            plotter.add_mesh(dots_mesh, color="orange", point_size=10, render_points_as_spheres=True, name="_lasso_dots")
        else:
            plotter.remove_actor("_lasso_dots")

        # Render primary committed boundary lines in 3D
        if len(pts_3d) >= 2:
            lines_mesh = pv.lines_from_points(pts_3d)
            plotter.add_mesh(lines_mesh, color="yellow", line_width=4, render_lines_as_tubes=True, name="_lasso_lines")
        else:
            plotter.remove_actor("_lasso_lines")

        # Render rubber-band trail from the last placed point to current cursor location in 3D
        if pts_3d and cursor_3d is not None:
            band_mesh = pv.lines_from_points([pts_3d[-1], cursor_3d])
            plotter.add_mesh(band_mesh, color="yellow", line_width=2, opacity=0.7, name="_lasso_band")
        else:
            plotter.remove_actor("_lasso_band")

        # Process green snap-to-close helper indicator on the first vertex
        if len(pts_3d) >= 3:
            pos_2d = plotter.iren.get_event_position()# position of cursor
            start_2d = _world_to_screen(pts_3d[0])  # position of the first point [0]
            
            # If cursor is visually hovering close to point 0, trigger green snap sphere
            if np.linalg.norm(np.array(pos_2d) - np.array(start_2d)) <= CLOSE_PX:
                snap_mesh = pv.PolyData(np.array([pts_3d[0]]))
                plotter.add_mesh(snap_mesh, color="green", point_size=16, render_points_as_spheres=True, name="_lasso_snap")
            else:
                plotter.remove_actor("_lasso_snap")
        else:
            plotter.remove_actor("_lasso_snap")

        plotter.render()

    # -------------- Selection Logic
    # Converts an array of 3D points into 2D display screen-space pixels
    def get_screen_points(world_points):
        out = []
        for pt in world_points:
            out.append(_world_to_screen(pt))
        return np.array(out)
    # True for faces pointing toward the active camera view position
    def front_facing_mask():
        """True for faces pointing toward the active camera view position."""
        cam_pos = np.array(plotter.camera.position)
        to_cam = cam_pos - centroids          
        dots = np.einsum("ij,ij->i", face_normals, to_cam)
        return dots > 0

    def close_polygon():
        pts_3d = state["poly_3d"]
        if len(pts_3d) >= 3:
            # Project both our 3D loop boundary and 3D face centers into temporary 2D screen positions
            pts_2d = get_screen_points(pts_3d)
            centroids_2d = get_screen_points(centroids)
            
            path = Path(pts_2d)
            inside = path.contains_points(centroids_2d)
            visible = front_facing_mask()
            
            # Append selection intersections
            state["selected"].update(int(i) for i in np.where(inside & visible)[0])
            
        state["poly_3d"].clear()
        redraw()
        refresh_highlight()

    def cancel_polygon():
        state["poly_3d"].clear()
        redraw()

    def clear_selection():
        state["selected"].clear()
        refresh_highlight()

    def refresh_highlight():
        if state["selected"]:
            sub = pv_mesh.extract_cells(np.array(sorted(state["selected"])))
            plotter.add_mesh(sub, color="red", name="highlight")
        else:
            plotter.remove_actor("highlight")
        plotter.render()

    # ------------ Event Interceptors

    def on_left_press(*_):
        state["press_pos"] = list(plotter.iren.get_event_position())

    def on_left_release(*_):
        if state["press_pos"] is None:
            return
        pos = list(plotter.iren.get_event_position())
        press = state["press_pos"]
        state["press_pos"] = None

        # Filter tracking jitter to distinguish camera rotations from selection clicks
        drag = ((pos[0] - press[0]) ** 2 + (pos[1] - press[1]) ** 2) ** 0.5
        if drag > 5:
            return

        # Explicitly use native VTK prop_picker calculation
        prop_picker.Pick(pos[0], pos[1], 0, plotter.renderer)
        click_3d = prop_picker.GetPickPosition()
        
        # If user clicks outside or off the mesh boundary entirely, disregard the interaction
        if click_3d is None or np.allclose(click_3d, [0.0, 0.0, 0.0]):
            return

        pts_3d = state["poly_3d"]

        # Loop closure checking via 2D visual layout checking
        if len(pts_3d) >= 3:
            start_2d = _world_to_screen(pts_3d[0])
            d = ((pos[0] - start_2d[0]) ** 2 + (pos[1] - start_2d[1]) ** 2) ** 0.5
            if d <= CLOSE_PX:
                close_polygon()
                return

        pts_3d.append(click_3d)
        redraw(cursor_3d=click_3d)

    def on_right_press(*_):
        pts_3d = state["poly_3d"]
        if len(pts_3d) >= 1:
            pts_3d.pop()
        redraw()

    def on_mouse_move(*_):
        if not state["poly_3d"]:
            return
        
        pos_2d = plotter.iren.get_event_position()
        
        # Explicitly use native VTK prop_picker calculation
        prop_picker.Pick(pos_2d[0], pos_2d[1], 0, plotter.renderer)
        cursor_3d = prop_picker.GetPickPosition()
        
        redraw(cursor_3d=cursor_3d)

    def save_selection():
        if not state["selected"]:
            print("Nothing selected.")
            return
        if export_path is not None:
            try:
                ids = np.array(sorted(state["selected"]))
                sub = pv_mesh.extract_cells(ids).extract_surface().triangulate()
                sub.save(export_path)
                print(f"[SUCCESS] Submesh successfully exported onto: {export_path}")
            except Exception as e:
                print(f"[ERROR] Failed to execute manual step export action: {e}")

    # Register observer callback bindings
    plotter.iren.add_observer("LeftButtonPressEvent", on_left_press)
    plotter.iren.add_observer("LeftButtonReleaseEvent", on_left_release)
    plotter.iren.add_observer("RightButtonPressEvent", on_right_press)
    plotter.iren.add_observer("MouseMoveEvent", on_mouse_move)
    plotter.add_key_event("Return", close_polygon)
    plotter.add_key_event("space", close_polygon)
    plotter.add_key_event("Escape", cancel_polygon)
    plotter.add_key_event("c", clear_selection)
    plotter.add_key_event("s", save_selection)
    
    # Execute blocking interactive display loop
    plotter.show()
    
    # Process the collected indices post window closure
    extracted_roi = None
    if state["selected"]:
        try:
            ids = np.array(sorted(state["selected"]))
            # Extract precise selected submesh indices and clean topological bounds
            extracted_roi = pv_mesh.extract_cells(ids).extract_surface(algorithm = 'dataset_surface').triangulate()
        except Exception as e:
            print(f"[RECOVERY PATH] Failed extraction sequence: {e}")
    # Save to disk if user requested export_path parameters on runtime call
        if extracted_roi is not None and extracted_roi.n_cells > 0:
            if export_path is not None:
                try:
                    extracted_roi.save(export_path)
                except Exception as e:
                    print(f"[ERROR] Failed to save geometry output: {e}")
        
        # --- PYVISTA TO TRIMESH CONVERSION ---
        roi_vertices = np.asarray(extracted_roi.points, dtype=float)
        roi_raw_faces = extracted_roi.faces
        roi_faces = roi_raw_faces.reshape(-1, 4)[:, 1:].astype(np.int64)
        trimesh_roi = trimesh.Trimesh(vertices=roi_vertices,faces=roi_faces,process=True)
    else:
        print("[WARNING] No custom boundary lasso region was committed. Returning empty mesh placeholder.")
        fallback_vertices = np.asarray(pv_mesh.points[:3], dtype=float)
        fallback_faces = np.array([], dtype=np.int64)
        trimesh_roi = trimesh.Trimesh(vertices=fallback_vertices, faces=fallback_faces, process=False)
    
    return trimesh_roi, np.array(sorted(state["selected"]), dtype=np.int64)