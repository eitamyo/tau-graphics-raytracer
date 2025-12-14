import numpy as np

def get_forward_vector(cam):
    forward = cam.look_at - cam.position
    return forward / np.linalg.norm(forward)

def get_right_vector(cam):
    right = np.cross(cam.forward_vector, cam.up_vector)
    return right / np.linalg.norm(right)

def get_true_up_vector(cam):
    up = np.cross(cam.right_vector, cam.forward_vector)
    return up / np.linalg.norm(up)

def get_screen_center(cam):
    forward = cam.forward_vector
    screen_center = cam.position + forward * cam.screen_distance
    return screen_center

class Camera:
    def __init__(self, position, look_at, up_vector, screen_distance, screen_width):
        self.position = np.array(position)
        self.look_at = np.array(look_at)
        self.up_vector = np.array(up_vector)
        self.screen_distance = screen_distance
        self.screen_width = screen_width
        self.forward_vector = get_forward_vector(self)
        self.right_vector = get_right_vector(self)
        self.true_up_vector = get_true_up_vector(self)
        self.screen_center = get_screen_center(self)