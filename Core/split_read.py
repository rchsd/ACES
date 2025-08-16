import trimesh
import numpy as np

def split_read(file):
    """
    SPLITREAD Reads *.stl in *.split format
    """
    try:
        # Read split file
        pgon_struct, mask = stlread(file)  # Assume stlread returns pgon and mask

        # Read header tags
        tags = stlreadh(file).split(':')  # Assume stlreadh returns header tags as a string

    except Exception as ex:
        raise ex  # Reformat and rethrow exceptions

    # If 'split' tag not found, process as normal stl
    if len(tags) < 2 or tags[0] or tags[1] != 'split':
        # Set mask, step, and tags
        pgon_struct['mask'] = np.ones(len(pgon_struct['faces']), dtype=int)
        pgon_struct['step'] = np.ones_like(pgon_struct['mask'], dtype=bool)
        pgon_struct['tags'] = []

    else:
        # Set mask, step, and tags
        pgon_struct['mask'] = (mask >> 8) + 1
        pgon_struct['step'] = np.bitwise_and(mask[:, None], np.uint32(1 << np.arange(7, -1, -1))) != 0
        pgon_struct['tags'] = tags[2:]

        # Remove extra steps
        last_nonzero = np.max(np.nonzero(np.any(pgon_struct['step'], axis=0)))
        pgon_struct['step'] = pgon_struct['step'][:, :last_nonzero + 1]

    mesh = trimesh.Trimesh(vertices=pgon_struct['vertices'], faces=pgon_struct['faces'])
    pgon_struct['mesh'] = mesh

    return pgon_struct

def stlread(mesh):
    # Implement or replace this function to read the STL and return pgon and mask
    # Example using trimesh
    pgon = {
        'vertices': mesh.vertices,
        'faces': mesh.faces,
        'normals': mesh.face_normals
    }
    mask = np.zeros(len(mesh.faces), dtype=np.uint32)  # Example mask, adjust as needed
    return pgon, mask

def stlreadh(file):
    # Implement or replace this function to read header tags from the file
    # Example: return header as a string
    return "Header:split:tag1:tag2"  # Example header, adjust as needed

#mesh = trimesh.load('c:\\Users\\bbeasley\\Documents\\Python Projects\\Matlab-GUI\\Tests\Schmitz\\transformed_mesh.stl')
#pgon = splitread(mesh)
#print(pgon['step'])