import argparse
from PIL import Image
import numpy as np
from tqdm import tqdm

from camera import Camera
from light import Light
from material import Material
from scene_settings import SceneSettings
from surfaces.cube import Cube
from surfaces.infinite_plane import InfinitePlane
from surfaces.sphere import Sphere

from multiprocessing import Pool
import functools


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

    pixel_point = camera.screen_center + (x_centered * pixel_scale_x * camera.right_vector) - (
        y_centered * pixel_scale_y * camera.true_up_vector)

    ray_direction = pixel_point - camera.position
    ray_direction = ray_direction / np.linalg.norm(ray_direction)

    return ray_direction


def compute_light_intensity(hit_surface, point, light: Light, light_dir, surfaces, num_shadow_rays):
    if num_shadow_rays == 1:
        # Fast path for hard shadows
        shadow_ray_dir = light_dir
        for surface in surfaces:
            if surface == hit_surface:
                continue
            t = surface.intersect(point + 1e-4 * light_dir, shadow_ray_dir)
            if t is not None and t > 0:
                return 1 - light.shadow_intensity
        return 1.0
    # find perpendicular vectors to light_dir
    up = np.array([0, 1, 0]) if abs(
        light_dir[1]) < 0.9 else np.array([1, 0, 0])
    right = np.cross(light_dir, up)
    right = right / np.linalg.norm(right)

    # divide into a square grid of cells centered around the light, with size light.radius
    cell_size = light.radius / num_shadow_rays
    rays_hit = 0
    for i in range(num_shadow_rays):
        for j in range(num_shadow_rays):
            # select a random point in the cell
            offset_x = (i + np.random.rand()) * cell_size - (light.radius / 2)
            offset_y = (j + np.random.rand()) * cell_size - (light.radius / 2)

            shadow_ray_origin = light.position + offset_x * right + offset_y * up
            shadow_ray_dir = (point - shadow_ray_origin) / \
                np.linalg.norm(point - shadow_ray_origin)

            hit = False
            max_t = np.linalg.norm(point - shadow_ray_origin)
            for surface in surfaces:
                if surface == hit_surface:
                    continue
                t = surface.intersect(shadow_ray_origin, shadow_ray_dir)
                if t is not None and t < max_t:
                    hit = True
                    break  # in shadow
            if not hit:
                rays_hit += 1  # not in shadow

    return (1 - light.shadow_intensity) + light.shadow_intensity * rays_hit / (num_shadow_rays * num_shadow_rays)


def get_color_for_ray(ray_origin, ray_direction, surfaces, materials: list[Material], lights: list[Light], scene_settings: SceneSettings, depth=0):
    if depth > scene_settings.max_recursions:
        return scene_settings.background_color

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
    material: Material = materials[hit_surface.material_index - 1]
    hit_point = ray_origin + min_t * ray_direction
    normal = hit_surface.get_normal(hit_point)

    diffuse_total = np.zeros(3)
    specural_total = np.zeros(3)
    for light in lights:
        light_dir = light.position - hit_point
        light_dir = light_dir / np.linalg.norm(light_dir)
        # Soft shadows
        light_intensity = compute_light_intensity(
            hit_surface, hit_point, light, light_dir, surfaces, scene_settings.root_number_shadow_rays)

        d = max(np.dot(normal, light_dir), 0.0)
        diffuse_component = d * light_intensity * material.diffuse_color * light.color
        diffuse_total = diffuse_total + diffuse_component

        reflection_dir = 2 * np.dot(normal, light_dir) * normal - light_dir
        reflection_dir = reflection_dir / np.linalg.norm(reflection_dir)
        view_dir = ray_origin - hit_point
        view_dir = view_dir / np.linalg.norm(view_dir)
        s = max(np.dot(reflection_dir, view_dir), 0.0) ** material.shininess
        specular_component = s * material.specular_color * light.color * light_intensity * light.specular_intensity
        specural_total = specural_total + specular_component
        
    # reflection
    reflection_contrib = np.zeros(3)
    if any(material.reflection_color):
        reflection_origin = hit_point + 1e-4 * normal
        reflection_dir = ray_direction - 2 * \
            np.dot(ray_direction, normal) * normal
        reflecion_color = get_color_for_ray(reflection_origin, reflection_dir,
                                            surfaces, materials, lights, scene_settings, depth + 1)
        reflection_contrib = reflecion_color * material.reflection_color

    transparency_background = np.zeros(3)
    if material.transparency > 0:
        transparency_origin = hit_point + 1e-4 * ray_direction
        transparency_dir = ray_direction
        transparency_background = get_color_for_ray(transparency_origin, transparency_dir,
                                                    surfaces, materials, lights, scene_settings, depth + 1)
    
    surface_color = (diffuse_total + specural_total) * (1 - material.transparency)
    final_color = transparency_background * material.transparency + surface_color + reflection_contrib

    return final_color


def render_row(y, width, height, camera, surfaces, materials, lights, settings):
    row_colors = []
    for x in range(width):
        pixel_direction = get_pixel_direction(x, y, camera, width, height)
        color = get_color_for_ray(camera.position, pixel_direction,
                                  surfaces, materials, lights, settings)
        row_colors.append(color)
    return y, row_colors


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

    image_array = np.zeros((args.height, args.width, 3))
    # Result
    with Pool() as pool:
        # Create partial function with fixed arguments
        worker_func = functools.partial(render_row, width=args.width, height=args.height,
                                        camera=camera, surfaces=surfaces,
                                        materials=materials, lights=lights, settings=scene_settings)

        # Map the function over all Y rows
        results = pool.map(worker_func, tqdm(range(args.height)))

    # Reassemble image_array from results
    for y, row_data in tqdm(results):
        for x, color in enumerate(row_data):
            image_array[y, x] = [255 if c >= 1 else c * 255 for c in color]
    # # Rendering loop
    # for y in range(args.height):
    #     for x in range(args.width):
    #         pixel_direction = get_pixel_direction(
    #             x, y, camera, args.width, args.height)
    #         pixel_color = get_color_for_ray(camera.position, pixel_direction,
    #                                         surfaces, materials, lights, scene_settings)
    #         image_array[y, x] = [c * 255 for c in pixel_color]
    #         print(
    #             f"Rendered pixel ({x+1},{y+1})/{args.width}x{args.height}", end='\r')

    # Save the output image
    save_image(image_array, args.output_image)


if __name__ == '__main__':
    main()
