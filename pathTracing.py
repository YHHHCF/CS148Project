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

    # Determint whether the photon will be absorbed
    # Or already diffused/reflected/transmissed enough of times
    k_a = 0.1  # rate of abosorbtion, hard coded
    if photon.depth >= depth or sample_bernoulli(k_a):
        return  # absorbed

    # Get intersection material information
    mat = hit_obj.simpleRT_material

    # Update hit_norm and ray_inside_object
    ray_inside_object = False
    if hit_norm.dot(photon_dir) > 0:
        hit_norm = -hit_norm
        ray_inside_object = True

    # Create a diffuse photon if the material is diffusive
    diffuse_color = Vector(mat.diffuse_color).xyz
    k_d = max(diffuse_color)  # TODO: add 3 channels
    if sample_bernoulli(k_d):
        photon_diffuse = photon.copy()
        D_diffuse = sample_dirs(1, photon_dir, 0.5)[0]  # Hemisphere sampling
        photon_diffuse.direction = np.array(D_diffuse)  # Create a copy for diffusion
        trace_photon(scene, depth, photon_diffuse, photon_map)
    
    # Determine k_r, rate of reflection, range [0, 1]
    if mat.use_fresnel:
        # calculate k_r using schlick’s approximation
        R_0 = ((1 - mat.ior) / (1 + mat.ior)) ** 2
        k_r = R_0 + (1 - R_0) * (1 + hit_norm.dot(photon_dir)) ** 5
    else:
        k_r = mat.mirror_reflectivity

    # Update photon direction
    if sample_bernoulli(k_r):
        # reflection
        D_reflect = photon_dir - 2 * photon_dir.dot(hit_norm) * hit_norm
        photon.direction = np.array(D_reflect)
    else:
        # transmission
        n1_by_n2 = 1 / mat.ior

        if ray_inside_object:
            n1_by_n2 = mat.ior

        D_dot_N = photon_dir.dot(hit_norm)
        inside_root = 1 - (n1_by_n2 ** 2) * (1 - D_dot_N ** 2)
        if inside_root > 0:
            D_transmiss = photon_dir * n1_by_n2 - hit_norm * (n1_by_n2 * D_dot_N + inside_root ** 0.5)
            photon.direction = np.array(D_transmiss)

    # Call recursively for reflection or transmission
    trace_photon(scene, depth, photon, photon_map)

    


if __name__ == "__main__":
    pass
