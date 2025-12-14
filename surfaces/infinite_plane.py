import numpy as np

class InfinitePlane:
    def __init__(self, normal, offset, material_index):
        self.normal = np.array(normal)
        self.offset = offset
        self.material_index = material_index
    
    def intersect(self, ray_origin: np.ndarray, ray_direction: np.ndarray):
        # Plane equation: normal · (P) = offset
        # Ray equation: P = ray_origin + t * ray_direction
        # Substitute ray equation into plane equation:
        # normal · (ray_origin + t * ray_direction) = offset
        # => normal · ray_origin + t * (normal · ray_direction) = offset
        # => t = (offset - normal · ray_origin) / (normal · ray_direction)

        denom = np.dot(self.normal, ray_direction)
        if abs(denom) < 1e-6:
            return None  # Ray is parallel to the plane

        numer = self.offset - np.dot(self.normal, ray_origin)
        t = numer / denom
        if t >= 0:
            return t
        else:
            return None # Intersection is behind the ray origin
        
    def get_normal(self, point):
        return self.normal
