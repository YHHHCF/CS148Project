# Render a photon map
import bpy

import importlib
import photonMap
importlib.reload(photonMap)
from photonMap import *

from skimage import io

# Render a single channel photon map to an image
def render_map(map_path, img_path):
    scene = bpy.context.scene
    objs = scene.objects
    photon_map = PhotonMap(map_path)
    radius = 0.1 # TODO: tune the retrieval radius

    # Cast rays from camera


    # Retrieve the nearby photons


    # Compute the illumination from the photons


# Combine the intensity of a list of images (M, N, 3) by averaging them
# decay_ratio is used to decay the effect of larger index image if needed
# decay_ratio should be one if we are combining RGB channels
def combine_image(paths, export_path, decay_ratio):
    img = io.imread(paths[0]).astype(np.float32) / 255
    sum_coefficient = 1.0
    exp_r = decay_ratio

    for path in paths[1:]:
        img += (io.imread(path).astype(np.float32) / 255) * exp_r
        sum_coefficient += exp_r
        exp_r *= decay_ratio

    img /= sum_coefficient
    img = (img * 255).astype(np.uint8)

    io.imsave(export_path, img)


if __name__ == "__main__":
    pass
