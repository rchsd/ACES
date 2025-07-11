import numpy as np

def unitize(A, axis=None):
    # Calculate the magnitude along the specified axis
    magnitude = np.linalg.norm(A, axis=axis, keepdims=True)
    
    # Divide input by magnitude using broadcasting
    B = A / magnitude
    
    return B


# Example usage
'''
A = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]], dtype=float)
B = unitize(A, axis=0)
print("Unitized array:\n", B)'''