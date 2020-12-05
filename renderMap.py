# Render a photon map
import bpy
import sys
sys.path.append("./tools")

import importlib
import photonMap
importlib.reload(photonMap)
from photonMap import *

import rayTracing
importlib.reload(rayTracing)
from rayTracing import *

from skimage import io
from skimage.filters import gaussian
import numpy as np

import sample
importlib.reload(sample)
from sample import *

# Render a single channel photon map to an image
def render_map(map_path, npy_path, channel):
    scene = bpy.context.scene
    scale = scene.render.resolution_percentage / 100.0
    objs = scene.objects

    photon_map = PhotonMap(map_path)
    photon_map.build_tree()
    radius = 0.25 # TODO: tune the retrieval radius

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

            # trace global illumination corresponding to that pixel
            # need to flip y, since screen origin starts from left bottom
            # while image origin starts from left top
            buf[height - 1 - y, x, channel] = \
                trace_diffuse(scene, channel, cam_location, ray_dir, photon_map, radius)

    buf = gaussian(buf, sigma=0.5, multichannel=True)  # smooth the photon rendering

    np.save(npy_path, buf)


def trace_diffuse(scene, channel, cam_location, ray_dir, photon_map, radius):
    eps = 0.0003

    # Get hit location
    has_hit, hit_loc, hit_norm, _, hit_obj, _ = ray_cast(scene, cam_location, ray_dir)

    color = 0

    if not has_hit:
        return color

    # Retrieve the nearby photons
    hit_loc = np.array(hit_loc)
    photon_ids = photon_map.find_photons_r(hit_loc, radius)
    
    # Compute the illumination from the photons
    for photon_id, distance in photon_ids:
        p = photon_map.map[photon_id]

        # Only consider the photon is above hit surface
        hit_to_photon = p.location - hit_loc
        if np.dot(hit_to_photon, hit_norm) >= 0:
            dot = np.dot(hit_norm, p.direction)
            if (dot < 0):
                color += -dot * \
                        hit_obj.simpleRT_material.diffuse_color[channel] / (0.25 + distance) ** 2
    return color


# Combine the intensity of a list of images (M, N, 3) by averaging them
# decay_ratio is used to decay the effect of larger index image if needed
def combine_image(paths, export_path, decay_ratio):
    img = io.imread(paths[0]).astype(np.float32) / 255
    # sum_coefficient = 1.0
    exp_r = decay_ratio

    for path in paths[1:]:
        tmp = (io.imread(path).astype(np.float32) / 255)
        img[:,:,:3] += tmp[:,:,:3] * exp_r
        # sum_coefficient += exp_r
        exp_r *= decay_ratio

    img[:,:,:3] /= np.max(img)
    img = (img * 255).astype(np.uint8)

    io.imsave(export_path, img)

# Combine 3 images of RGB channels
def combine_channels(paths, export_path):
    img = np.load(paths[0]) + np.load(paths[1]) + np.load(paths[2])
    io.imsave(export_path, img)

if __name__ == "__main__":
    pass
