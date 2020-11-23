# The baseline implemented in HW3 and HW5
import bpy

import importlib
import photonMap
importlib.reload(photonMap)
from photonMap import *

import rayTracing
importlib.reload(rayTracing)
from rayTracing import *


def RT_render_scene(scene, width, height, depth, num_sample, buf):
    """Main function for rendering the scene

    Parameters
    ----------
    scene : bpy.types.Scene
        The scene that will be rendered
        It stores information about the camera, lights, objects, and material
    width : int
        Width of the rendered image
    height : int
        Height of the rendered image
    depth : int
        The recursion depth of raytracing
        i.e. the number that light bounces in the scene
    buf: numpy.ndarray
        the buffer that will be populated to store the calculated color
        for each pixel
    """

    # get all the lights from the scene
    scene_lights = [o for o in scene.objects if o.type == "LIGHT"]

    # get the location and orientation of the active camera
    cam_location = scene.camera.location
    cam_orientation = scene.camera.rotation_euler

    # get camera focal length
    focal_length = scene.camera.data.lens / scene.camera.data.sensor_width
    aspect_ratio = height / width
    
    # CKPT 2.2
    dx = 1 / width
    dy = aspect_ratio / height
    corput_x = [corput(i, 2) * dx for i in range(num_sample)]
    corput_y = [corput(i, 3) * dy for i in range(num_sample)]
    
    # CKPT 2.1
    # iterate through all the pixels, cast a ray for each pixel
    for y in range(height):
        # get screen space coordinate for y
        screen_y = ((y - (height / 2)) / height) * aspect_ratio
        for x in range(width):
            # get screen space coordinate for x
            screen_x = (x - (width / 2)) / width
            
            # populate the alpha component of the buffer
            # to make the pixel not transparent
            buf[y, x, 3] = 1
            
            for n in range(num_sample):
                # calculate the ray direction
                ray_dir = Vector((screen_x + corput_x[n], screen_y + corput_y[n], - focal_length))
                ray_dir.rotate(cam_orientation)
                ray_dir = ray_dir.normalized()
                
                # populate the RGB component of the buffer with ray tracing result
                buf[y, x, 0:3] += RT_trace_ray(scene, cam_location, ray_dir, scene_lights, depth) 

    buf[:, :, 0:3] /= num_sample
    return buf

# CKPT 2.2
def corput(n, base):
    q, denom = 0, 1
    while n:
        denom *= base
        n, remainder = divmod(n, base)
        q += remainder / denom
    return q - 0.5

# modified from https://docs.blender.org/api/current/bpy.types.RenderEngine.html
class SimpleRTRenderEngine(bpy.types.RenderEngine):
    # These three members are used by blender to set up the RenderEngine
    # define its internal name, visible name and capabilities.
    bl_idname = "simple_RT"
    bl_label = "SimpleRT"
    bl_use_preview = False

    # Init is called whenever a new render engine instance is created. Multiple
    # instances may exist at the same time, for example for a viewport and final
    # render.
    def __init__(self):
        self.draw_data = None

    # When the render engine instance is destroy, this is called. Clean up any
    # render engine data here, for example stopping running render threads.
    def __del__(self):
        pass

    # This is the method called by Blender for both final renders (F12) and
    # small preview for materials, world and lights.
    def render(self, depsgraph):
        scene = depsgraph.scene
        scale = scene.render.resolution_percentage / 100.0
        self.size_x = int(scene.render.resolution_x * scale)
        self.size_y = int(scene.render.resolution_y * scale)
        
        self.samples = depsgraph.scene.simpleRT.samples

        if self.is_preview:
            pass
        else:
            self.render_scene(scene)

        # #============== for project debug
        # dir_path = "./profile"
        # profile(map_size=1e5, num_query=10, query_radius=0.2, dir_path=dir_path)

        # from os.path import join
        # map_path = join(dir_path, "map.pkl")
        # test_load_map(map_path)
        # #============== for project debug

    def render_scene(self, scene):
        # create a buffer to store the calculated intensities
        # buffer is has four channels: Red, Green, Blue, and Alpha
        # default is set to (0, 0, 0, 0), which means black and fully transparent
        height, width = self.size_y, self.size_x
        buf = np.zeros((height, width, 4))

        result = self.begin_result(0, 0, self.size_x, self.size_y)
        layer = result.layers[0].passes["Combined"]

        # get the maximum ray tracing recursion depth
        depth = scene.simpleRT.recursion_depth

        RT_render_scene(scene, width, height, depth, self.samples, buf)
        
        self.update_result(result)
        layer.rect = buf.reshape(-1, 4).tolist()

        # tell Blender all pixels have been set and are final
        self.end_result(result)

if __name__ == "__main__":
    pass
