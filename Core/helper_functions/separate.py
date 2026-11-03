import numpy as np
import trimesh
import logging as log
from helper_functions import pgon_parts, pgon_separation, unitize, pgon_track_split


def separate(pgon, combined_mesh, centers, radii):
    # Get polygon parts
    parts = pgon_parts.find_parts(None, method='vertex', mesh=combined_mesh, max_angle=None)

    # Compute volumes of each part
    vols = pgon_parts.compute_part_volumes(combined_mesh, parts)

    # Identify large pieces
    threshold = (4 * np.pi * np.mean(radii) ** 3) / 3

    # Adding 1 because parts should return 1s and 2s. ii will return 0 and 1 so half of the parts will be ignored
    ii = np.where(10 * abs(vols) > threshold)[0] + 1

    if len(ii) == 2:
        # Keep only the two large pieces
        keep = np.isin(parts, ii)
        mesh = pgon_separation.pgon_mask(combined_mesh, keep)
        sub_parts = np.asarray(pgon_parts.find_parts(None, method='vertex', mesh=mesh, max_angle=None))
        cent = pgon_parts.compute_part_centroids(mesh, sub_parts)

        #determine left/right orientation
        distances = np.linalg.norm(centers - cent[0], axis=1)
        im = np.argmin(distances)
        if im != 0:
            sub_parts = 3 - sub_parts  # Flip labels

        #expand back to the full face count so mask length matches pgon['faces']
        parts = np.zeros(len(combined_mesh.faces), dtype=int)
        parts[keep] = sub_parts

        #attach any small stray components to whichever side they sit closest to
        stray = np.where(parts == 0)[0] #parts assigned as 0 and not 1 or 2
        log.debug(f"this is stray - > {stray}")
        if len(stray):
            face_center = combined_mesh.triangles_center #coords of every face center

            #global average center for the two large parts in the mesh
            center_p1 = face_center[parts == 1].mean(axis=0)
            center_p2 = face_center[parts == 2].mean(axis=0)
            log.debug(f"this is c1 -> {center_p1} \n this is c2 -> {center_p2}\n")

            #calculates the distance of the stray faces to the large part it's closest to
            distance_p1 = np.linalg.norm(face_center[stray] - center_p1, axis=1)
            distance_p2 = np.linalg.norm(face_center[stray] - center_p2, axis=1)
            log.debug(f"this is d1 -> {distance_p1} \n this is d2 -> {distance_p2}\n")

            #reassign the stray face to the large part it sits closest to each face will get a 1 or 2
            parts[stray] = np.where(distance_p1 <= distance_p2, 1, 2)
            log.debug(f"In seperate, {len(stray)} faces in small components assigned to nearest side.")

        log.debug(f"this is mask -> {pgon['mask'].shape[0]} and this is faces -> {pgon['faces'].shape[0]} \n")
        # Update step and mask
        pgon['step'] = np.ones((pgon['faces'].shape[0], 2), dtype=bool)
        pgon['mask'] = parts.astype(int)

        mesh = trimesh.Trimesh(vertices=pgon['vertices'], faces=pgon['faces'])
        pgon['mesh'] = mesh

    elif len(ii) == 1:
        # Keep the one large piece and split it
        pgon = pgon_separation.pgon_mask(pgon, parts == ii[0])
        norm = unitize.unitize(np.diff(centers, axis=0)[0])
        pgon = pgon_track_split.track_split(pgon, verts=[], plane=norm, coef=np.dot(norm, np.mean(centers, axis=0)))

    else:
        raise ValueError("Model could not be resolved into right and left halves.")

    return pgon
