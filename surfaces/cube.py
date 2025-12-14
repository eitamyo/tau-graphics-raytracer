import numpy as np

class Cube:
    def __init__(self, position, scale, material_index):
        self.position = np.array(position)
        self.scale = scale
        self.material_index = material_index
        self.min_bound = self.position - scale / 2
        self.max_bound = self.position + scale / 2

    def intersect(self, ray_origin: np.ndarray, ray_direction: np.ndarray):
        t_near = float('-inf')
        t_far = float('inf')
        
        for i in range(3):
            if abs(ray_direction[i]) < 1e-6:
                if ray_origin[i] < self.min_bound[i] or ray_origin[i] > self.max_bound[i]:
                    return None  # No intersection, ray is parallel and outside the slab
            else:
                # Compute intersection t values for the slabs
                t1 = (self.min_bound[i] - ray_origin[i]) / ray_direction[i]
                t2 = (self.max_bound[i] - ray_origin[i]) / ray_direction[i]
                
                t_entry = min(t1, t2)
                t_exit = max(t1, t2)

                t_near = max(t_near, t_entry)
                t_far = min(t_far, t_exit)
                
                if t_near > t_far or t_far < 0:
                    return None  # No intersection

        return t_near if t_near >= 0 else None
    
    def get_normal(self, point):
        # Determine which face of the cube the point is on
        for i in range(3):
            if abs(point[i] - self.min_bound[i]) < 1e-6:
                normal = np.array([0, 0, 0])
                normal[i] = -1
                return normal
            elif abs(point[i] - self.max_bound[i]) < 1e-6:
                normal = np.array([0, 0, 0])
                normal[i] = 1
                return normal
        return None  # Should not reach here if point is on the surface