import numpy as np

def parse_inputs(args):
    # Default parameter values
    params = {
        'SamplePoints': 5000,
        'RadiusRange': [15, 35],
        'GridSize': 10,
        'GridAdjustmentFactor': 3,
        'GridCycles': 2,
        'FitCycles': 2,
        'WeightCycles': 2,
        'DistanceCutoff': 1.2,
        'AngleCutoff': 60
    }

    # Update parameters with provided arguments
    for key, value in args.items():
        if key in params:
            if key == 'SamplePoints':
                if not (isinstance(value, (int, float)) and value > 0 and value.is_integer()):
                    raise ValueError(f"{key} must be a positive integer.")
            elif key in ['RadiusRange', 'GridSize', 'GridAdjustmentFactor', 'DistanceCutoff', 'AngleCutoff']:
                if not (isinstance(value, (list, np.ndarray)) and len(value) == 2 and all(isinstance(v, (int, float)) and v > 0 for v in value)):
                    raise ValueError(f"{key} must be a list of two positive real numbers.")
            elif key in ['GridCycles', 'FitCycles', 'WeightCycles']:
                if not (isinstance(value, (int, float)) and value > 0 and value.is_integer()):
                    raise ValueError(f"{key} must be a positive integer.")
            params[key] = value

    return params

'''
mesh = dict()
params = parse_inputs(mesh)
print(params['RadiusRange'][1])'''