def get_forward_vector(cam):
    forward = [cam.look_at[i] - cam.position[i] for i in range(3)]
    return normalize(forward)

def get_right_vector(cam):
    right = [cam.up_vector[i] - cam.position[i] for i in range(3)]
    return normalize(right)

def get_up_vector(cam):
    up = [cam.up_vector[i] - cam.position[i] for i in range(3)]
    return normalize(up)

def get_screen_center(cam):
    forward = cam.forward_vector
    screen_center = [cam.position[i] + forward[i] * cam.screen_distance for i in range(3)]
    return screen_center

def normalize(vector):
    norm = sum([x**2 for x in vector]) ** 0.5
    return [x / norm for x in vector]

class Camera:
    def __init__(self, position, look_at, up_vector, screen_distance, screen_width):
        self.position = position
        self.look_at = look_at
        self.up_vector = up_vector
        self.screen_distance = screen_distance
        self.screen_width = screen_width
        self.forward_vector = get_forward_vector(self)
        self.right_vector = get_right_vector(self)
        self.up_vector = get_up_vector(self)
        self.screen_center = get_screen_center(self)