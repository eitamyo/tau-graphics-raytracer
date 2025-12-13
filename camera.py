from vectors import normalize, cross

def get_forward_vector(cam):
    forward = [cam.look_at[i] - cam.position[i] for i in range(3)]
    return normalize(forward)

def get_right_vector(cam):
    right = cross(cam.forward_vector, cam.up_vector)
    return normalize(right)

def get_true_up_vector(cam):
    up = cross(cam.right_vector, cam.forward_vector)
    return normalize(up)

def get_screen_center(cam):
    forward = cam.forward_vector
    screen_center = [cam.position[i] + forward[i] * cam.screen_distance for i in range(3)]
    return screen_center

class Camera:
    def __init__(self, position, look_at, up_vector, screen_distance, screen_width):
        self.position = position
        self.look_at = look_at
        self.up_vector = up_vector
        self.screen_distance = screen_distance
        self.screen_width = screen_width
        self.forward_vector = get_forward_vector(self)
        self.right_vector = get_right_vector(self)
        self.true_up_vector = get_true_up_vector(self)
        self.screen_center = get_screen_center(self)