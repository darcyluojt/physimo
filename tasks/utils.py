import math
from typing import Tuple
import numpy as np

def calculate_angle_3d(mark1, mark2, mark3):

    A = np.array([mark1.x, mark1.y, mark1.z])
    B = np.array([mark2.x, mark2.y, mark2.z])
    C = np.array([mark3.x, mark3.y, mark3.z])


    # build direction vectors BA and BC
    v1 = A - B
    v2 = C - B

    # compute unit‐cross for the rotation axis
    axis = np.cross(v1, v2)
    axis /= np.linalg.norm(axis)
    print(f"3D Axis of rotation: {axis}")

    # dot / (|v1|*|v2|) → clamp → arccos → interior angle
    cosθ = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))
    cosθ = np.clip(cosθ, -1.0, 1.0)
    θ = np.degrees(np.arccos(cosθ))

    # if you really want the *supplementary* (180–θ), do: return 180-θ
    return (180-θ)


def calculate_angle_2d(mark1, mark2, mark3):
    # build NumPy vectors from landmark objects
    A = np.array([mark1.x, mark1.y])
    B = np.array([mark2.x, mark2.y])
    C = np.array([mark3.x, mark3.y])

    # direction vectors BA and BC
    v1 = A - B
    v2 = C - B

    axis = np.cross(v1, v2)
    axis /= np.linalg.norm(axis)
    print(f"2D Axis of rotation: {axis}")

    # compute cosine of the angle, clamp to [-1,1]
    cosθ = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))
    cosθ = np.clip(cosθ, -1.0, 1.0)

    # θ in degrees
    θ = np.degrees(np.arccos(cosθ))

    # return supplementary angle (180°−θ)
    return 180.0 - θ
