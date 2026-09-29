import numpy as np
from helper_functions import pgon_separation, pgon_parts

def fill_hole(pgon):

    # Get current polygon
    temp = pgon_separation.pgon_mask(pgon['mesh'], pgon['step'][:, -1])
    mask = pgon['mask'][pgon['step'][:, -1]]

    # Mark largest non-masked piece
    index = np.where(mask == 1)[0]
    left, _ = pgon_separation.pgon_mask_index(temp, index)
    parts = pgon_parts.find_parts(None, 'edge', left)
    im = np.argmax(pgon_parts.max_part_area(left, parts))
    mask[index[parts != im]] = 3

    # Mark largest masked piece
    index = np.where(mask == 3)[0]
    left, _ = pgon_separation.pgon_mask_index(temp, index)
    parts = pgon_parts.find_parts(None, 'edge', left)
    im = np.argmax(pgon_parts.max_part_area(left, parts))
    mask[index[parts != im]] = 1

    # Mark largest non-masked piece
    index = np.where(mask == 2)[0]
    left, _ = pgon_separation.pgon_mask_index(temp, index)            
    parts = pgon_parts.find_parts(None, 'edge', left)
    im = np.argmax(pgon_parts.max_part_area(left, parts))
    mask[index[parts != im]] = 4

    # Mark largest masked piece
    index = np.where(mask == 4)[0]
    left, _ = pgon_separation.pgon_mask_index(temp, index)
    parts = pgon_parts.find_parts(None, 'edge', left)
    im = np.argmax(pgon_parts.max_part_area(left, parts))
    mask[index[parts != im]] = 2

    print(f'this is the mask after fill hole: {mask} \n\n')

    # Update mask
    pgon['mask'][pgon['step'][:, -1]] = mask

    return pgon


def fill_holes(pgon):

    # Get current polygon
    temp = pgon_separation.pgon_mask(pgon['mesh'], pgon['step'][:, -1])
    mask = pgon['mask'][pgon['step'][:, -1]]

    # Mark largest non-masked piece (Mask == 1)
    index = np.where(mask == 1)[0]
    if len(index) > 0:  
        left, _ = pgon_separation.pgon_mask_index(temp, index)
        parts = pgon_parts.find_parts(None, 'edge', left)
        if len(parts) > 0:
            im = np.argmax(pgon_parts.max_part_area(left, parts))
            mask[index[parts != im]] = 3

    # Mark largest masked piece (Mask == 3)
    index = np.where(mask == 3)[0]
    if len(index) > 0:  
        left, _ = pgon_separation.pgon_mask_index(temp, index)
        parts = pgon_parts.find_parts(None, 'edge', left)
        if len(parts) > 0:
            im = np.argmax(pgon_parts.max_part_area(left, parts))
            mask[index[parts != im]] = 1

    # Mark largest non-masked piece (Mask == 2)
    index = np.where(mask == 2)[0]
    if len(index) > 0:  
        left, _ = pgon_separation.pgon_mask_index(temp, index)            
        parts = pgon_parts.find_parts(None, 'edge', left)
        if len(parts) > 0:
            im = np.argmax(pgon_parts.max_part_area(left, parts))
            mask[index[parts != im]] = 4

    # Mark largest masked piece (Mask == 4)
    index = np.where(mask == 4)[0]
    if len(index) > 0:  
        left, _ = pgon_separation.pgon_mask_index(temp, index)
        parts = pgon_parts.find_parts(None, 'edge', left)
        if len(parts) > 0:
            im = np.argmax(pgon_parts.max_part_area(left, parts))
            mask[index[parts != im]] = 2

    # Update mask
    pgon['mask'][pgon['step'][:, -1]] = mask

    return pgon
