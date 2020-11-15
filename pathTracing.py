# Functions for path tracing which builds the photon map
import bpy

import importlib
import photonMap
importlib.reload(photonMap)
from photonMap import *

# Show the objects in the scene for debug
def print_scene():
	print("============= Scene Objects =============")
	scene = bpy.context.scene

	objs = scene.objects

	for o in objs:
		print(o.type, o.name)

	print("=========================================")



if __name__ == "__main__":
	pass
