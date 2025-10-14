import trimesh
import numpy as np


def split_read(file):
    """
    SPLITREAD Reads *.stl in *.split format, simplified to ignore step decoding.
    """
    try:
        # Read split file
        pgon_struct, mask = stlread(file['mesh'])

        # Read header tags
        tags = stlreadh(file).split(':')  # Assume stlreadh returns header tags as a string

    except Exception as ex:
        raise ex  # Reformat and rethrow exceptions

    # If 'split' tag not found, process as normal STL
    if len(tags) < 2 or tags[0] != '' or tags[1] != 'split':
        # Set mask, step, and tags
        pgon_struct['mask'] = np.ones(len(pgon_struct['faces']), dtype=int)
        pgon_struct['step'] = np.ones((len(pgon_struct['faces']), 1), dtype=bool)
        pgon_struct['tags'] = []
    else:
        # Decode mask from bit-shifted format
        pgon_struct['mask'] = (mask >> 8) + 1

        # Set a placeholder step array (ignoring bitwise step encoding)
        pgon_struct['step'] = np.ones((len(pgon_struct['faces']), 1), dtype=bool)

        # Extract tags
        pgon_struct['tags'] = tags[2:]

    # Create mesh object
    mesh = trimesh.Trimesh(vertices=pgon_struct['vertices'], faces=pgon_struct['faces'])
    pgon_struct['mesh'] = mesh

    return pgon_struct

def stlread(mesh):
    pgon = {
        'vertices': mesh.vertices,
        'faces': mesh.faces,
        'normals': mesh.face_normals
    }
    # array is full of ones since matlab function returns attributes
    # and since attributes will always be empty, should return ones
    mask = np.ones(len(mesh.faces), dtype=np.uint32) 
    return pgon, mask

def stlreadh(file):
    # Implement or replace this function to read header tags from the file
    # Example: return header as a string
    return "Header:split:tag1:tag2"  # Example header, adjust as needed

#mesh = trimesh.load('c:\\Users\\bbeasley\\Documents\\Python Projects\\Matlab-GUI\\Tests\Schmitz\\transformed_mesh.stl')
#pgon = splitread(mesh)
#print(pgon['step'])