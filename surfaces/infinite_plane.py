import numpy as np
# from numba import njit

# @njit
def intersect_plane(normal, offset, ray_origin: np.ndarray, ray_direction: np.ndarray):
    # Plane equation: normal · (P) = offset
    # Ray equation: P = ray_origin + t * ray_direction
    # Substitute ray equation into plane equation:
    # normal · (ray_origin + t * ray_direction) = offset
    # => normal · ray_origin + t * (normal · ray_direction) = offset
    # => t = (offset - normal · ray_origin) / (normal · ray_direction)

    denom = np.dot(normal, ray_direction)
    if abs(denom) < 1e-6:
        return None  # Ray is parallel to the plane

    numer = offset - np.dot(normal, ray_origin)
    t = numer / denom
    if t >= 0:
        return t
    else:
        return None # Intersection is behind the ray origin
      

class InfinitePlane:
    def __init__(self, normal, offset, material_index):
        self.normal = np.array(normal)
        self.offset = offset
        self.material_index = material_index

    def intersect(self, ray_origin: np.ndarray, ray_direction: np.ndarray):
        return intersect_plane(self.normal, self.offset, ray_origin, ray_direction)
        
    def get_normal(self, point):
        return self.normal
