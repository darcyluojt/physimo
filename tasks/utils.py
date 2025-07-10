import math
from typing import Tuple

def calculate_angle(
    a: Tuple[float, float, float],
    b: Tuple[float, float, float],
    c: Tuple[float, float, float]
) -> float:
    """
    Compute the angle at point B formed by points A–B–C in 3D space.
    Each point is an (x, y, z) tuple.
    Returns the angle in degrees.
    """
    # Build vectors BA and BC
    v1 = (a[0] - b[0], a[1] - b[1], a[2] - b[2])
    v2 = (c[0] - b[0], c[1] - b[1], c[2] - b[2])

    # Dot product and magnitudes
    dot  = v1[0]*v2[0] + v1[1]*v2[1] + v1[2]*v2[2]
    mag1 = math.sqrt(v1[0]**2 + v1[1]**2 + v1[2]**2)
    mag2 = math.sqrt(v2[0]**2 + v2[1]**2 + v2[2]**2)

    # Clamp and compute arccos
    cos_ = max(-1.0, min(1.0, dot / (mag1 * mag2)))


    # Log axis:
    vec_prod = (
        v1[1] * v2[2] - v1[2] * v2[1],
        v1[2] * v2[0] - v1[0] * v2[2],
        v1[0] * v2[1] - v1[1] * v2[0]
    )
    vec_prod_mag = math.sqrt(vec_prod[0]**2 + vec_prod[1]**2 + vec_prod[2]**2)
    normed_vec_prod = (
        vec_prod[0] / vec_prod_mag,
        vec_prod[1] / vec_prod_mag,
        vec_prod[2] / vec_prod_mag
    )
    print(f'Axis of rotation: {normed_vec_prod}')


    return (180 - math.degrees(math.acos(cos_)))


# import numpy as np
# def calciluate_angle(a: np.ndarray, b: np.ndarray, c: np.ndarray) -> float:
#     """
#     Compute the angle at point B formed by points A–B–C in 3D space.
#     Each point is a numpy array of shape (3,).
#     Returns the angle in degrees.
#     """
#     v1 = a - b
#     v2 = c - b

#     dot = v1 @ v2  # Dot product
#     mag1 = np.linalg.norm(v1)
#     mag2 = np.linalg.norm(v2)

#     cos = np.clip(dot / (mag1 * mag2), -1.0, 1.0) # numerical stability
#     return np.degrees(np.arccos(cos))