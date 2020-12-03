import bpy

import sys
sys.path.append("./tools")

import importlib
import sample
importlib.reload(sample)
from sample import *

import rayTracing
importlib.reload(rayTracing)
from rayTracing import *

from skimage import io
from skimage.filters import gaussian
import numpy as np


# TODO: support any light direction
def trace_light(scene, light_loc, radius, intensity, cam_location, ray_dir):
    # Get hit location
    has_hit, hit_loc, hit_norm, _, hit_obj, _ = ray_cast(scene, cam_location, ray_dir)

    res = np.zeros(3)

    if has_hit and hit_obj.name == 'walls':
        dist = np.dot(light_loc - hit_loc, light_loc - hit_loc)
        dist = np.sqrt(dist)
        if (dist <= radius):
            res = intensity

    return res

def render_light(npy_path):
    scene = bpy.context.scene
    scale = scene.render.resolution_percentage / 100.0
    objs = scene.objects

    # Compute camera parameters
    height = int(scene.render.resolution_x * scale)
    width = int(scene.render.resolution_y * scale)

    buf = np.zeros((height, width, 3))

    cam_location = scene.camera.location
    cam_orientation = scene.camera.rotation_euler

    focal_length = scene.camera.data.lens / scene.camera.data.sensor_width
    aspect_ratio = height / width

    # iterate through all the pixels, cast a ray for each pixel
    for y in range(height):
        print(f'Render progress: {(y + 1): d} /{height: d}')
        # get screen space coordinate for y
        screen_y = ((y - (height / 2)) / height) * aspect_ratio
        for x in range(width):
            # get screen space coordinate for x
            screen_x = (x - (width / 2)) / width

            # calculate the ray direction
            ray_dir = Vector((screen_x, screen_y, -focal_length))
            ray_dir.rotate(cam_orientation)
            ray_dir = ray_dir.normalized()


            # get light location and direction (TODO: support multiple lights)
            area_lights = [o for o in scene.objects if \
                            (o.type == "LIGHT" and o.data.type == "AREA")]
            light = area_lights[0]
            light_loc = light.location
            light_radius = light.data.size / 2
            light_intensity = np.array(light.data.color * light.data.energy / (4 * np.pi))

            # trace all rays to see if it intersects with light
            buf[height - 1 - y, x] = trace_light(scene, light_loc, light_radius,\
                                                light_intensity, cam_location, ray_dir)

    buf = gaussian(buf, sigma=0.1, multichannel=True)  # smooth the light

    np.save(npy_path, buf)

def add_light(img_path, light_path, export_path):
    img = io.imread(img_path).astype(np.float32) / 255
    light = io.imread(light_path).astype(np.float32) / 255

    w, h, _ = img.shape

    for i in range(w):
        for j in range(h):
            for c in range(3):
                if light[i][j][c] > 0:
                    img[i][j][c] = light[i][j][c]

    img = (img * 255).astype(np.uint8)
    io.imsave(export_path, img)

if __name__ == "__main__":
    pass
