# Render a photon map
import bpy

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
def render_map(map_path, img_path, channel):
    scene = bpy.context.scene
    scale = scene.render.resolution_percentage / 100.0
    objs = scene.objects

    photon_map = PhotonMap(map_path)
    photon_map.build_tree()
    radius = 0.3 # TODO: tune the retrieval radius

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

    buf = gaussian(buf, sigma=1, multichannel=True)  # smooth the photon rendering
    buf = buf / np.max(buf)

    io.imsave(img_path, buf)


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
    for photon_id in photon_ids:
        p = photon_map.map[photon_id]

        # Only consider the photon if can be seen from camera
        photon_camera_dir = normalize(p.location - cam_location)
        has_hit_shadow, hit_loc_shadow, _, _, _, _ = \
            ray_cast(scene, cam_location, photon_camera_dir)
        if not has_hit_shadow:
            can_see_photon = True
        else:
            dis_photon = np.dot(p.location - cam_location, p.location - cam_location)
            dis_shadow_hit = np.dot(hit_loc_shadow - cam_location, \
                                hit_loc_shadow - cam_location)
            can_see_photon = dis_photon <= dis_shadow_hit + eps

        if can_see_photon:
            color += np.abs(np.dot(hit_norm, p.direction)) * \
                        hit_obj.simpleRT_material.diffuse_color[channel]
    return color


# Combine the intensity of a list of images (M, N, 3) by averaging them
# decay_ratio is used to decay the effect of larger index image if needed
# decay_ratio should be one if we are combining RGB channels
def combine_image(paths, export_path, decay_ratio):
    img = io.imread(paths[0]).astype(np.float32) / 255
    sum_coefficient = 1.0
    exp_r = decay_ratio

    for path in paths[1:]:
        img[:,:,:3] += (io.imread(path).astype(np.float32) / 255) * exp_r
        sum_coefficient += exp_r
        exp_r *= decay_ratio

    img[:,:,:3] /= sum_coefficient
    img = (img * 255).astype(np.uint8)

    io.imsave(export_path, img)


if __name__ == "__main__":
    pass
