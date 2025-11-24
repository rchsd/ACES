import math
import csv

def format_and_export_to_csv(result, filename='coverage.csv'):
    with open(filename, mode='w', newline='') as file:
        header_1, header_2, row_1 = print_general(result)
        row_header_1, row_header_2, row_header_3, results_header = print_supine_coverage(result)

        writer = csv.writer(file)
        writer.writerows([header_1, header_2, row_1, [], [], [], row_header_1, row_header_2, row_header_3, results_header])

def print_general(result):
    rw = 4 * math.pi * result['right_radius'] ** 2
    lw = 4 * math.pi * result['left_radius'] ** 2
    tw = 4 * math.pi * ((result['right_radius'] + result['left_radius']) ** 2) / 4

    header_1 = (['PatientID'] + [''] * 3 + ['Right'] + [''] * 9 + ['Left'] + [''] * 7 + ['Total'])
    header_2 = ['', 'Pel. Width', 'Ace. Tilt', 'Ace. Spread',
                'Radius', 'Version', 'Tilt', 'W.B. Area', 'F. Area', 'T. Area',
                'W.B. Norm', 'F. Norm', 'T. Norm', 'Volume',
                'Radius', 'Version', 'Tilt', 'W.B. Area', 'F. Area', 'T. Area',
                'W.B. Norm', 'F. Norm', 'T. Norm', 'Volume',
                'Radius', 'Version', 'Tilt', 'W.B. Area', 'F. Area', 'T. Area',
                'W.B. Norm', 'F. Norm', 'T. Norm', 'Volume']

    row = [
        result['name'],
        result['width'], result['tilt'], result['spread'],
        result['right_radius'], result['right_version'], result['right_tilt'],
        result['right_total_area'] - result['right_fossa_area'],
        result['right_fossa_area'], result['right_total_area'],
        (result['right_total_area'] - result['right_fossa_area']) / rw,
        result['right_fossa_area'] / rw, result['right_total_area'] / rw,
        result['right_volume'],
        result['left_radius'], result['left_version'], result['left_tilt'],
        result['left_total_area'] - result['left_fossa_area'],
        result['left_fossa_area'], result['left_total_area'],
        (result['left_total_area'] - result['left_fossa_area']) / lw,
        result['left_fossa_area'] / lw, result['left_total_area'] / lw, result['left_volume'],
        (result['right_radius'] + result['left_radius']) / 2, (result['right_version'] + result['left_version']) / 2,
        (result['right_tilt'] + result['left_tilt']) / 2,
        (result['right_total_area'] + result['left_total_area'] -
         result['right_fossa_area'] - result['left_fossa_area']) / 2,
        (result['right_fossa_area'] + result['left_fossa_area']) / 2,
        (result['right_total_area'] + result['left_total_area']) / 2,
        (result['right_total_area'] + result['left_total_area'] - result['right_fossa_area'] - result['left_fossa_area']) / 2 / tw,
        (result['right_fossa_area'] + result['left_fossa_area']) / 2 / tw,
        (result['right_total_area'] + result['left_total_area']) / 2 / tw,
        (result['right_volume'] + result['left_volume']) / 2
    ]

    return header_1, header_2, row


def print_supine_coverage(result):
    # Header rows
    empty = ''
    header_1 = ['Right'] + [empty]*23 + ['Left'] + [empty]*23 + ['Total']
    header_2 = (
        ['Weight Bearing'] + [empty]*7 + ['Fossa'] + [empty]*7 + ['Total'] + [empty]*7 +
        ['Weight Bearing'] + [empty]*7 + ['Fossa'] + [empty]*7 + ['Total'] + [empty]*7 +
        ['Weight Bearing'] + [empty]*7 + ['Fossa'] + [empty]*7 + ['Total']
    )
    header_3 = ['S', 'SA', 'A', 'IA', 'I', 'IP', 'P', 'SP',
                          'S', 'SA', 'A', 'IA', 'I', 'IP', 'P', 'SP',
                          'S', 'SA', 'A', 'IA', 'I', 'IP', 'P', 'SP',
                          'S', 'SA', 'A', 'IA', 'I', 'IP', 'P', 'SP',
                          'S', 'SA', 'A', 'IA', 'I', 'IP', 'P', 'SP',
                          'S', 'SA', 'A', 'IA', 'I', 'IP', 'P', 'SP']
    
    row = [result['right_total_supine_coverage'] - result['right_fossa_supine_coverage'], result['right_fossa_supine_coverage'], result['right_total_supine_coverage'],
           result['left_total_supine_coverage'] - result['left_fossa_supine_coverage'], result['left_fossa_supine_coverage'], result['left_total_supine_coverage'],
           (result['right_total_supine_coverage'] + result['left_total_supine_coverage'] - result['right_fossa_supine_coverage'] - result['left_fossa_supine_coverage']) / 2,
           (result['right_fossa_supine_coverage'] + result['left_fossa_supine_coverage']) / 2, 
           (result['right_total_supine_coverage'] + result['left_total_supine_coverage']) / 2]

    # Result row
    right_total = result['right_total_supine_coverage']
    right_fossa = result['right_fossa_supine_coverage']
    left_total = result['left_total_supine_coverage']
    left_fossa = result['left_fossa_supine_coverage']

    right_weight = right_total - right_fossa
    left_weight = left_total - left_fossa
    total_weight = (right_weight + left_weight) / 2
    total_fossa = (right_fossa + left_fossa) / 2
    total_total = (right_total + left_total) / 2

    result_row = [
        right_weight, right_fossa, right_total,
        left_weight, left_fossa, left_total,
        total_weight, total_fossa, total_total
    ]

    flattened_result_row = [value for array in result_row for value in array]

    return header_1, header_2, header_3, flattened_result_row