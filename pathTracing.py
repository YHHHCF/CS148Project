# Functions for path tracing which builds the photon map
import bpy

import importlib
import photonMap
importlib.reload(photonMap)
from photonMap import *

import sys
sys.path.append("./tools")

import sample
importlib.reload(sample)
from sample import *

# Show the objects in the scene for debug
def print_scene():
    print("============= Scene Objects =============")
    scene = bpy.context.scene
    objs = scene.objects
    for o in objs:
        print(o.type, o.name)
    print("=========================================")


# Given the scene and max photon depth (#hitting)
# Return the photon map
def trace_photons(depth):
    emission_intensity = 100  # To be tuned

    print("Start Building Photon Map!")
    scene = bpy.context.scene
    lights = [o for o in scene.objects if o.type == "LIGHT"]

    # Build photon map
    photon_map = PhotonMap()
    photon_map.depth = depth

    # Determine #photons for each light source
    for light in lights:
        # Determine emission pattern from light property
        if light.data.type == "AREA":
            pass
        else:
            pass

        for i in range(int(light.data.energy * emission_intensity)):
            # Create a photon (original) from the emission pattern
            photon = Photon()
            photon.set_loc(light.location[0], light.location[1], light.location[2])
            direction = sample_dirs(1)
            photon.set_dir(direction[0][0], direction[0][1], direction[0][2])

            # Trace the photon recursively
            trace_photon(scene, depth, photon, photon_map)
            
    print("Finished Building Photon Map!")
    return photon_map

# Trace one photon recursively
def trace_photon(scene, depth, photon, photon_map):
    # Get photon location and direction

    # Find intersection using ray casting

    # Get intersection material information

    # Determint the next photon location and direction

    # Call recursively
    pass

if __name__ == "__main__":
    pass
