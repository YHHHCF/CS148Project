# Functions for ray tracing

import numpy as np
from mathutils import Vector
from math import sqrt

def ray_cast(scene, origin, direction):
   """wrapper around Blender's Scene.ray_cast() API

   Parameters
   ----------
   scene ： bpy.types.Scene
       The Blender scene we will cast a ray in
   origin : Vector, float array of 3 items
       Origin of the ray
   direction : Vector, float array of 3 items
       Direction of the ray

   Returns
   -------
   has_hit : bool
       The result of the ray cast, i.e. if the ray hits anything in the scene
   hit_loc : Vector, float array of 3 items
       The hit location of this ray cast
   hit_norm : Vector, float array of 3 items
       The face normal at the ray cast hit location
   index : int
       The face index of the hit face of the hit object
       -1 when original data isn’t available
   hit_obj : bpy_types.Object
       The hit object
   matrix: Matrix, float 4 * 4
       The matrix_world of the hit object
   """
   return scene.ray_cast(scene.view_layers[0], origin, direction)


def RT_trace_ray(scene, ray_orig, ray_dir, lights, depth=0):
    """Cast a single ray into the scene

    Parameters
    ----------
    scene : bpy.types.Scene
        The scene that will be rendered
        It stores information about the camera, lights, objects, and material
    ray_orig : Vector, float array of 3 items
        Origin of the current ray
    ray_dir : Vector, float array of 3 items
        Direction of the current ray
    lights : list of bpy_types.Object
        The list of lights in the scene
    depth: int
        The recursion depth of raytracing
        i.e. the number that light bounces in the scene

    Returns
    -------
    color : Vector, float array of 3 items
        Color of the pixel
    """
    
    eps = 0.0003

    # cast a ray into the scene using Blender's built-in function
    has_hit, hit_loc, hit_norm, _, hit_obj, _ = ray_cast(scene, ray_orig, ray_dir)

    color = np.zeros(3)

    if not has_hit:
        return color
    
    ray_inside_object = False
    if hit_norm.dot(ray_dir) > 0:
        hit_norm = -hit_norm
        ray_inside_object = True

    ambient_color = scene.simpleRT.ambient_color
    mat = hit_obj.simpleRT_material
    diffuse_color = Vector(mat.diffuse_color).xyz
    specular_color = Vector(mat.specular_color).xyz
    specular_hardness = mat.specular_hardness
    
    no_light_hit = True # true if none of the lights hits the location

    for light in lights:
        light_color = np.array(light.data.color * light.data.energy / (4 * np.pi))
        
        if light.data.type == "AREA":
            # CKPT 1
            light_normal = Vector((0, 0, -1))
            light_normal.rotate(light.rotation_euler)
            
            light_color =  light_color * max(0, light_normal.dot((hit_loc - light.location).normalized()))
            
            r = sqrt(np.random.rand())
            theta = 2 * np.pi * np.random.rand()
            emit_loc_local = Vector((r * np.cos(theta), r * np.sin(theta), 0)) * light.data.size / 2
            emit_loc_global = light.matrix_world @ emit_loc_local
            
        # the direction from hit location to the light
        light_vec = emit_loc_global - hit_loc
        light_dir = light_vec.normalized()

        # the origin of the shadow ray
        new_orig = hit_loc + hit_norm * eps

        # cast the shadow ray from hit location to the light
        has_light_hit, light_hit_loc, _, _, _, _ = ray_cast(
            scene, new_orig, light_dir
        )  # do not change
        
        # compute the vector from light to hit location 
        light_to_hit = light_hit_loc - emit_loc_global
        
        # do nothing if the hit point is closer than light (its dot product with light vector should be negative)
        if has_light_hit and np.dot(light_vec, light_to_hit) < 0:
            continue
        # shade with Blinn-Phong model
        color += np.array(diffuse_color) * np.array((light_color / light_vec.dot(light_vec))) * light_dir.dot(hit_norm)
        # calculate half_vector
        half_vector = (light_dir - ray_dir).normalized()
        # calculate specular component, add that to the pixel color
        color += np.array(specular_color) * np.array((light_color / light_vec.dot(light_vec))) * (hit_norm.dot(half_vector)**specular_hardness)
        
        no_light_hit = False

    # if none of the lights hit the object, add the ambient component I_ambient to the pixel color
    if no_light_hit:
        color += np.array(diffuse_color) * np.array(ambient_color)
    
    if mat.use_fresnel:
        # calculate k_r using schlick’s approximation
        R_0 = ((1-mat.ior)/(1+mat.ior))**2
        k_r = R_0 + (1-R_0) * (1+hit_norm.dot(ray_dir))**5
    else:
        k_r = mat.mirror_reflectivity
    
    # recursion
    if depth > 0:
        # reflection
        D_reflect = ray_dir - 2 * ray_dir.dot(hit_norm) * hit_norm
        color += k_r * RT_trace_ray(scene, hit_loc + hit_norm * eps, D_reflect, lights, depth - 1)
        
        # transmission
        n1_by_n2 = 1 / mat.ior
        if ray_inside_object:
            n1_by_n2 = mat.ior

        D_dot_N = ray_dir.dot(hit_norm)
        inside_root = 1 - (n1_by_n2 ** 2) * (1 - D_dot_N ** 2)
        if inside_root > 0:
            D_transmit = ray_dir * n1_by_n2 - hit_norm * (n1_by_n2 * D_dot_N + inside_root ** 0.5)
            color += (1 - k_r) * mat.transmission * RT_trace_ray(scene, hit_loc - hit_norm * eps, D_transmit, lights, depth - 1)
    
        # CKPT 3
        # set hit_norm to be z axis and find x and y axis
        x_axis =  Vector((0, 0, 1))

        if np.abs(hit_norm.dot(x_axis)) > 0.9:
            x_axis = Vector((0, 1, 0))
        
        x_axis -= x_axis.dot(hit_norm) * hit_norm
        x_axis = x_axis.normalized()
        y_axis = np.cross(x_axis, hit_norm)
        y_axis = Vector((y_axis[0], y_axis[1], y_axis[2]))
        
        # sample a direction from the hemisphere which points at hit_norm direction
        cos_theta = np.random.rand()
        sin_theta = sqrt(1 - cos_theta * cos_theta)
        phi = 2 * np.pi * np.random.rand()
        rand_dir_local = Vector((sin_theta * np.cos(phi), sin_theta * np.sin(phi), cos_theta))
        
        # calculate global direction
        rand_dir_global = x_axis * rand_dir_local[0] + y_axis * rand_dir_local[1] + hit_norm * rand_dir_local[2]
        
        # calculate the contribution
        color += RT_trace_ray(scene, hit_loc + hit_norm * eps, rand_dir_global, lights, depth - 1) * cos_theta * diffuse_color
    
    return color
