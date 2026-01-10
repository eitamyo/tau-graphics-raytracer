# from numba import njit
import numpy as np

# @njit
def intersect_sphere(ray_origin: np.ndarray, ray_direction: np.ndarray, sphere_pos: np.ndarray, sphere_radius: float):
    # ||(ray_origin + t*ray_direction - pos)||^2 = radius^2
    # <=> (ray_origin + t*ray_direction - pos)·(ray_origin + t*ray_direction - pos) = radius^2
    # <=> (ray_direction·ray_direction)t^2 + 2(ray_direction·(ray_origin - pos))t + (ray_origin - pos)·(ray_origin - pos) - radius^2 = 0
    # At^2 + Bt + C = 0
    oc = ray_origin - sphere_pos
    A = 1  # ray_direction is normalized
    B = 2 * np.dot(oc, ray_direction)
    C = np.dot(oc, oc) - sphere_radius ** 2
    discriminant = B ** 2 - 4 * A * C
    if discriminant < 0:
        return None
    sqrt_disc = discriminant ** 0.5
    t1 = (-B - sqrt_disc) / (2 * A)
    t2 = (-B + sqrt_disc) / (2 * A)
    if t1 >= 0:
        return t1
    elif t2 >= 0:
        return t2
    else:
        return None

class Sphere:
    def __init__(self, position, radius, material_index):
        self.position = np.array(position)
        self.radius = radius
        self.material_index = material_index
        
    def intersect(self, ray_origin: np.ndarray, ray_direction: np.ndarray):
        return intersect_sphere(ray_origin, ray_direction, self.position, self.radius)
    
    def get_normal(self, point):
        normal = (point - self.position) / self.radius
        return normal
