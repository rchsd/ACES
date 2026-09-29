import numpy as np
from helper_functions import pgon_separation, find_barys_and_norms, pgon_props, fossa_selection_points_qt, fossa_selection_lasso, fossa_selection
from helper_functions import reflection, translation, pgon_upe, find_plane_contours, plot_sphere
import pandas as pd
import numpy_groupies as ng

def default(pgon, mask, centers, radii):

    print('Calculating coverage angles.')
    # Define indexes
    r_fossa = 0
    l_fossa = 2
    r_hip = 1
    l_hip = 3
    
    angles = np.zeros((360, 4))
    
    _r_cup_in = pgon_separation.pgon_mask(pgon, (mask & 3) == 2)
    _l_cup_in = pgon_separation.pgon_mask(pgon, (mask & 3) == 3)
 
    _, _r_ids = fossa_selection.select_submesh_3d(_r_cup_in, centers[0].copy())
    _, _l_ids = fossa_selection.select_submesh_3d(_l_cup_in, centers[1].copy())
 
    print(f"[fossa] R {len(_r_ids)} of {len(_r_cup_in.faces)} faces, max idx {_r_ids.max() if len(_r_ids) else -1}")
    print(f"[fossa] L {len(_l_ids)} of {len(_l_cup_in.faces)} faces, max idx {_l_ids.max() if len(_l_ids) else -1}")
 
    r_fossa_mesh, _ = pgon_separation.pgon_mask_index(_r_cup_in, _r_ids)
    l_fossa_mesh, _ = pgon_separation.pgon_mask_index(_l_cup_in, _l_ids)
    print(f"[chck] R cup {_r_cup_in.centroid.round(1)} -> fossa {r_fossa_mesh.centroid.round(1)}")
    print(f"[chck] L cup {_l_cup_in.centroid.round(1)} -> fossa {l_fossa_mesh.centroid.round(1)}")
    
    
    angles[:, r_fossa] = coverage_angles(r_fossa_mesh.copy(), centers[0]) 
    angles[:, l_fossa] = coverage_angles(l_fossa_mesh.copy(), centers[1]) 
    angles[:, r_hip] = coverage_angles(pgon_separation.pgon_mask(pgon, (mask & 3) == 2), centers[0])
    angles[:, l_hip] = coverage_angles(pgon_separation.pgon_mask(pgon, (mask & 3) == 3), centers[1])
     
    
    # Calculate surface areas
    areas = np.zeros((2, 2))

    # Right fossa
    areas.flat[r_fossa] = r_fossa_mesh.area

    # Left fossa
    areas.flat[l_fossa] = l_fossa_mesh.area

    # Right hip
    selected_faces = (mask & 3) == 2
    masked_mesh = pgon.submesh([selected_faces], append=True)
    areas.flat[r_hip] = masked_mesh.area

    # Left hip
    selected_faces = (mask & 3) == 3
    masked_mesh = pgon.submesh([selected_faces], append=True)
    areas.flat[l_hip] = masked_mesh.area

    # Calculate orientations
    selected = (mask & 3) == 2
    _, normals, _, _ = find_barys_and_norms.find_barys_norms(pgon, selected)
    summed = np.sum(normals, axis=0)
    unit_vector = summed / np.linalg.norm(summed)
    orient = np.zeros((2, 3))
    orient[0, :] = unit_vector
    # needed for image generation in snapshot code
    right_ace_normals = normals

    selected = (mask & 3) == 3
    _  , normals, _, _ = find_barys_and_norms.find_barys_norms(pgon, selected)
    summed = np.sum(normals, axis=0)
    unit_vector = summed / np.linalg.norm(summed)
    orient[1, :] = unit_vector
    # needed for image generation in snapshot code
    left_ace_normals = normals

    elevation = np.cross(orient[0], orient[1])
    elevation /= np.linalg.norm(elevation)

    # Calculate orientation angles
    spread = np.degrees(np.arccos(np.dot(orient[0], orient[1])))
    tilt = np.degrees(np.arctan2(elevation[2], elevation[0]))

    # Get masks
    mask1 = np.roll(np.ceil(np.arange(1, 361) / 45).astype(int), -22)
    mask2 = np.roll(mask1, -round(tilt))

    # Create result dictionary
    result = dict()
    # To Do: give user option to type out filename
    result.update({'name': 'final_pelvis', 'width': (np.linalg.norm(np.diff(centers, axis=0), axis=1)[0]), 'spread': spread, 'tilt': tilt})

    # Create right result dictionary
    right_supine = pd.Series(angles[:, r_hip]).groupby(mask1).sum().div(45).to_numpy()
    right_fossa = pd.Series(angles[:, r_fossa]).groupby(mask1).sum().div(45).to_numpy()
    right_total_tilt = pd.Series(angles[:, r_hip]).groupby(mask2).sum().div(45).to_numpy()
    right_fossa_tilt = pd.Series(angles[:, r_fossa]).groupby(mask2).sum().div(45).to_numpy()

    result.update({ 'right_center': centers[0], 
                    'right_radius': radii[0], 
                    'right_total_area': areas.flat[r_hip], 
                    'right_fossa_area': areas.flat[r_fossa], 
                    'right_orientation': orient[0], 
                    'right_version': np.degrees(np.arctan2(orient[0, 0], -orient[0, 1]))
                    
                    })

    result.update({ 'right_tilt': np.degrees(np.arctan2(-orient[0, 2], -orient[0, 1])), 
                    'right_total_supine_coverage': right_supine, 
                    'right_fossa_supine_coverage': right_fossa
                    
                    })

    result.update({ 'right_total_tilt_coverage': right_total_tilt, 
                    'right_fossa_tilt_coverage': right_fossa_tilt
                    
                    })

    selected_faces = (mask & 3) == 2
    new_mesh = pgon_separation.pgon_mask(pgon, selected_faces)
    _r_cup_vol = pgon_props.compute_mesh_volume(new_mesh, centers[0])
    _r_fossa_vol = pgon_props.compute_mesh_volume(r_fossa_mesh, centers[0])
    
    _rc_in = pgon_separation.pgon_mask(pgon, (mask & 3) == 2)
    print(f"[R] cup    centroid {_rc_in.centroid.round(1)}  bounds {_rc_in.bounds.round(1).tolist()}")
    print(f"[R] fossa  centroid {r_fossa_mesh.centroid.round(1)}  bounds {r_fossa_mesh.bounds.round(1).tolist()}")
    print(f"[R] center {centers[0].round(1)}")

    print(f"[R] cup {len(new_mesh.faces)} faces vol {_r_cup_vol:.0f} | "
          f"fossa {len(r_fossa_mesh.faces)} faces area {r_fossa_mesh.area:.0f} vol {_r_fossa_vol:.0f}")
    result.update({'right_volume': _r_cup_vol - _r_fossa_vol,
                   'right_cup_volume': _r_cup_vol,
                   'right_fossa_volume': _r_fossa_vol})
    print(f"[R] right_volume written = {_r_cup_vol - _r_fossa_vol:.0f}")

    
    # Create left result dictionary
    left_supine = pd.Series(angles[:, l_hip]).groupby(mask1).sum().div(45).to_numpy()
    left_fossa = pd.Series(angles[:, l_fossa]).groupby(mask1).sum().div(45).to_numpy()
    left_total_tilt = pd.Series(angles[:, l_hip]).groupby(mask2).sum().div(45).to_numpy()
    left_fossa_tilt = pd.Series(angles[:, l_fossa]).groupby(mask2).sum().div(45).to_numpy()

    result.update({ 'left_center': centers[1], 
                    'left_radius': radii[1], 
                    'left_total_area': areas.flat[l_hip], 
                    'left_fossa_area': areas.flat[l_fossa], 
                    'left_orientation': orient[1], 
                    'left_version': np.degrees(np.arctan2(orient[1, 0], orient[1, 1]))
                    
                    })

    result.update({ 'left_tilt': np.degrees(np.arctan2(-orient[1, 2], orient[1, 1])), 
                    'left_total_supine_coverage': left_supine, 
                    'left_fossa_supine_coverage': left_fossa
                    
                    })

    result.update({ 'left_total_tilt_coverage': left_total_tilt, 
                    'left_fossa_tilt_coverage': left_fossa_tilt
                    
                    })

    selected_faces = (mask & 3) == 3
    new_mesh = pgon_separation.pgon_mask(pgon, selected_faces)
    _l_cup_vol = pgon_props.compute_mesh_volume(new_mesh, centers[1])
    _l_fossa_vol = pgon_props.compute_mesh_volume(l_fossa_mesh, centers[1])
    
    _lc_in = pgon_separation.pgon_mask(pgon, (mask & 3) == 3)
    print(f"[L] cup    centroid {_lc_in.centroid.round(1)}  bounds {_lc_in.bounds.round(1).tolist()}")
    print(f"[L] fossa  centroid {l_fossa_mesh.centroid.round(1)}  bounds {l_fossa_mesh.bounds.round(1).tolist()}")
    print(f"[L] center {centers[1].round(1)}")
    
    _ld = np.linalg.norm(l_fossa_mesh.vertices - centers[1], axis=1)
    print(f"[L] fossa dist {_ld.min():.1f}/{np.median(_ld):.1f}/{_ld.max():.1f} "
          f"area {l_fossa_mesh.area:.0f} vol {_l_fossa_vol:.0f} "
          f"-> implied {3*_l_fossa_vol/l_fossa_mesh.area:.1f}")

    print(f"[L] cup {len(new_mesh.faces)} faces vol {_l_cup_vol:.0f} | "
          f"fossa {len(l_fossa_mesh.faces)} faces area {l_fossa_mesh.area:.0f} vol {_l_fossa_vol:.0f}")
    result.update({'left_volume': _l_cup_vol - _l_fossa_vol,
                   'left_cup_volume': _l_cup_vol,
                   'left_fossa_volume': _l_fossa_vol})
    print(f"[L] left_volume written = {_l_cup_vol - _l_fossa_vol:.0f}")
    
    # ---------------- VOLUME TEST ----------------
    
 
    def _vol_diag(label, cup, fossa, center, radius):
        V = cup.vertices - center
        F = cup.faces
        tet = np.einsum('ij,ij->i',
                        V[F[:, 0]],
                        np.cross(V[F[:, 1]], V[F[:, 2]])) / 6.0
 
        print(f"\n--- {label} ---")
        print(f"  faces                 {len(F)}")
        print(f"  area                  {cup.area:10.0f}")
        print(f"  fit radius            {radius:10.2f}")
 
        # 1. current method
        print(f"1 cone-to-center (now)  {abs(tet.sum()):10.0f}")
 
        # 2. winding check - if these differ a lot, the mesh winding is inconsistent
        print(f"2 signed / abs-summed   {tet.sum():10.0f} / {np.abs(tet).sum():10.0f}"
              f"   negatives={int((tet < 0).sum())}/{len(tet)}")
 
        # 3. articular only (fossa removed)
        if fossa is not None and len(fossa.faces):
            Vf = fossa.vertices - center
            Ff = fossa.faces
            tf = np.einsum('ij,ij->i', Vf[Ff[:, 0]],
                           np.cross(Vf[Ff[:, 1]], Vf[Ff[:, 2]])) / 6.0
            print(f"3 fossa alone           {abs(tf.sum()):10.0f}")
            print(f"  cup minus fossa       {abs(tet.sum()) - abs(tf.sum()):10.0f}")
            print(f"  fossa area            {fossa.area:10.0f}")
 
        # 4. convex hull of the cup surface
        try:
            print(f"4 convex hull           {cup.convex_hull.volume:10.0f}")
        except Exception as e:
            print(f"4 convex hull           failed: {e}")
 
        # 5. capped at the rim plane: project the boundary, close it, take the
        #    enclosed volume. This is the other common definition.
        try:
            capped = cup.copy()
            capped.fill_holes()
            if capped.is_watertight:
                print(f"5 hole-filled watertight{abs(capped.volume):10.0f}")
            else:
                print(f"5 hole-filled           not watertight after fill")
        except Exception as e:
            print(f"5 hole-filled           failed: {e}")
 
        # 6. reference: sphere and hemisphere at the fit radius
        print(f"6 hemisphere at r       {2/3*np.pi*radius**3:10.0f}")
        print(f"  (1/3)*area*r          {cup.area * radius / 3:10.0f}")
    
    _r_cup = pgon_separation.pgon_mask(pgon, (mask & 3) == 2)
    _l_cup = pgon_separation.pgon_mask(pgon, (mask & 3) == 3)
    _vol_diag("RIGHT", _r_cup, r_fossa_mesh, centers[0], radii[0])
    _vol_diag("LEFT",  _l_cup, l_fossa_mesh, centers[1], radii[1])
    # ---------------- TEST ----------------


    # needed for image generation in snapshot code, stored in dictionary for later processing
    fossa_dict = dict()
    fossa_dict.update({'right_ace_normals': right_ace_normals, 'left_ace_normals': left_ace_normals})

    _, r_normals, _, _ = find_barys_and_norms.find_barys_norms(r_fossa_mesh)
    _, l_normals, _, _ = find_barys_and_norms.find_barys_norms(l_fossa_mesh)
    
    fossa_dict.update({'right_fossa_normals': r_normals, 'left_fossa_normals': l_normals})
    

    return result, fossa_dict


def coverage_angles(pgon, center):
    # Flip and translate right-side
    pgon = pgon.copy()
    if center[1] < 0:
        pgon = pgon.apply_transform(reflection.reflection(np.array([0, 1, 0])) @ translation.translate(-center))
    # Translate only left-side
    else:
        pgon = pgon.apply_transform(translation.translate(-center))

    # Get open edges
    _, _, _, _, edge = pgon_upe.unpaired_edges_pgon(pgon)

    # Create sampling vector
    th = np.arange(540) * np.pi / 540
    coefs = np.zeros(th.shape)

    # Create normals
    norms = np.column_stack((np.cos(th), coefs, -np.sin(th)))

    # Locate sample points
    points, _, in_mask = find_plane_contours.compute_contours_with_trimesh(edge, norms, coefs)
    # Extract faces and vertices
    faces = points['faces'][:, 0]
    vertices = points['vertices']

    # Zero out x where in_mask == 1
    vertices[faces[in_mask == 1], 0] = 0
    # Extract subset of vertices
    subset = vertices[faces, :]

    # Get angles about y-axis
    around = np.arctan2(subset[:, 0], subset[:, 2])
    around[around < 0] += 2 * np.pi

    signs = 2 * (around < np.pi) - 1
    xy_mag = np.linalg.norm(subset[:, [0, 2]], axis=1)
    result = np.arctan2(signs * xy_mag, -subset[:, 1])
    
    pos = ng.aggregate(in_mask, result, size=540, func='max')
    neg = -ng.aggregate(in_mask, result, size=540, func='min')

    # Reshaping for accurate results
    pos = pos.reshape(-1, 1)
    neg = neg.reshape(-1, 1)

    combined = np.reshape(np.vstack((pos, neg)), (3, -1), order='F')
    result = np.mean(combined, axis=0) * 180 / np.pi
   
    return result