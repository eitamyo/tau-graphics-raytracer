import argparse
from PIL import Image
import numpy as np

from camera import Camera
from light import Light
from material import Material
from scene_settings import SceneSettings
from surfaces.cube import Cube
from surfaces.infinite_plane import InfinitePlane
from surfaces.sphere import Sphere


def parse_scene_file(file_path):
    objects = []
    camera = None
    scene_settings = None
    with open(file_path, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split()
            obj_type = parts[0]
            params = [float(p) for p in parts[1:]]
            if obj_type == "cam":
                camera = Camera(params[:3], params[3:6],
                                params[6:9], params[9], params[10])
            elif obj_type == "set":
                scene_settings = SceneSettings(
                    params[:3], params[3], params[4])
            elif obj_type == "mtl":
                material = Material(
                    params[:3], params[3:6], params[6:9], params[9], params[10])
                objects.append(material)
            elif obj_type == "sph":
                sphere = Sphere(params[:3], params[3], int(params[4]))
                objects.append(sphere)
            elif obj_type == "pln":
                plane = InfinitePlane(params[:3], params[3], int(params[4]))
                objects.append(plane)
            elif obj_type == "box":
                cube = Cube(params[:3], params[3], int(params[4]))
                objects.append(cube)
            elif obj_type == "lgt":
                light = Light(params[:3], params[3:6],
                              params[6], params[7], params[8])
                objects.append(light)
            else:
                raise ValueError("Unknown object type: {}".format(obj_type))
    return camera, scene_settings, objects


def save_image(image_array, output_path):
    image = Image.fromarray(np.uint8(image_array))

    # Save the image to a file
    image.save(output_path)

def get_pixel_direction(x, y, camera, image_width, image_height):
    aspect_ratio = image_width / image_height
    screen_height = camera.screen_width / aspect_ratio

    x_centered = (x + 0.5) - (image_width / 2)
    y_centered = (y + 0.5) - (image_height / 2)

    pixel_scale_x = camera.screen_width / image_width
    pixel_scale_y = screen_height / image_height

    pixel_point = [
        camera.screen_center[i] + (x_centered * pixel_scale_x * camera.right_vector[i]) - (
            y_centered * pixel_scale_y * camera.true_up_vector[i])
        for i in range(3)
    ]

    ray_direction = [pixel_point[i] - camera.position[i] for i in range(3)]

    norm = sum([d**2 for d in ray_direction]) ** 0.5
    ray_direction = [d / norm for d in ray_direction]

    return ray_direction

def get_color_for_ray(ray_origin, ray_direction, surfaces, materials, lights, scene_settings):
    hit_surface = None
    min_t = float('inf')
    for surface in surfaces:
        t = surface.intersect(ray_origin, ray_direction)
        if t is not None and t < min_t:
            min_t = t
            hit_surface = surface
    if hit_surface is None:
        return scene_settings.background_color
    # Placeholder: return the diffuse color of the first intersected surface
    # TODO: Implement full shading model
    material = materials[hit_surface.material_index - 1]
    color = [c * 255 for c in material.diffuse_color]
    # if isinstance(hit_surface, Sphere):
    #     print("Hit sphere at t =", min_t, "with material color =", color)
    # print("Hit surface:", hit_surface, "with material color =", material.diffuse_color)
    return color

def main():
    # python ray_tracer.py scenes/pool.txt output/pool.png −−width 500 −−height 500
    parser = argparse.ArgumentParser(description='Python Ray Tracer')
    parser.add_argument('scene_file', type=str, help='Path to the scene file')
    parser.add_argument('output_image', type=str,
                        help='Name of the output image file')
    parser.add_argument('--width', type=int, default=500, help='Image width')
    parser.add_argument('--height', type=int, default=500, help='Image height')
    args = parser.parse_args()

    # Parse the scene file
    camera, scene_settings, objects = parse_scene_file(args.scene_file)

    lights = [obj for obj in objects if isinstance(obj, Light)]
    materials = [obj for obj in objects if isinstance(obj, Material)]
    surfaces = [obj for obj in objects if isinstance(
        obj, (Sphere, InfinitePlane, Cube))]

    # Result
    image_array = np.zeros((500, 500, 3))
    # Rendering loop
    for y in range(args.height):
        for x in range(args.width):
            pixel_direction = get_pixel_direction(
                x, y, camera, args.width, args.height)
            pixel_color = get_color_for_ray(camera.position, pixel_direction,
                                           surfaces, materials, lights, scene_settings)
            image_array[y, x] = pixel_color

    # Save the output image
    save_image(image_array, args.output_image)


if __name__ == '__main__':
    main()
