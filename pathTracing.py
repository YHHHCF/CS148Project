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

import rayTracing
importlib.reload(rayTracing)
from rayTracing import *

eps = 0.0003

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
            is_area_light = True
            ratio = 0.5
        else:
            ratio = 1.0  # Can use ratio < 0.5 for spotlights
            is_area_light = False

        light_dir = np.array([0, 0, -1]) # Use any direction (TODO)

        for i in range(int(light.data.energy * emission_intensity)):
            # Create a photon (original) from the emission pattern
            photon = Photon()

            light_loc = np.array(light.location)

            # Sample the photon location if it is area light
            if is_area_light:
                radius = light.data.size / 2
                light_loc += sample_disk_loc(1, light_dir, radius)[0]
            photon.set_loc(light_loc[0], light_loc[1], light_loc[2])


            direction = sample_dirs(1, light_dir, ratio)
            photon.set_dir(direction[0][0], direction[0][1], direction[0][2])

            # Trace the photon recursively
            trace_photon(scene, depth, photon, photon_map)
            
    print("Finished Building Photon Map!")
    return photon_map


# Trace one photon recursively
# Add a copy of it to photon map each time it reflects
def trace_photon(scene, depth, photon, photon_map):
    # Get photon location and direction
    photon_loc = Vector(photon.location)
    photon_dir = Vector(photon.direction)

    # Find intersection using ray casting
    has_hit, hit_loc, hit_norm, _, hit_obj, _ = ray_cast(scene, photon_loc, photon_dir)

    if not has_hit:
        return

    # If hit, update depth, location of original photon
    new_loc = hit_loc + hit_norm * eps
    photon.set_loc(new_loc[0], new_loc[1], new_loc[2])
    photon.depth = photon.depth + 1

    # Add a copy of original photon to photon map
    photon_copy = photon.copy()
    photon_copy.id = photon_map.get_id()
    photon_map.add_photon(photon_copy)

    # Get intersection material information (TODO: base the reflection direction on material)
    mat = hit_obj.simpleRT_material
    reflectivity = mat.mirror_reflectivity # range [0, 1]

    # Determint whether the photon will be bounced or absorbed
    if not sample_bernoulli(reflectivity):
        return  # absorbed

    # Update photon direction (TODO: implement BRDF table, now simply use reflection)
    photon_dir = photon_dir - 2 * photon_dir.dot(hit_norm) * hit_norm
    photon.direction = np.array(photon_dir)

    # Call recursively if this photon has not reached depth limit
    if (photon.depth < depth):
        trace_photon(scene, depth, photon, photon_map)


if __name__ == "__main__":
    pass
