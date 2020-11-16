# Debug tools to convert photon points in the map to PLY file
# Visualize in either blender or pyntcloud
# PLY writer from https://github.com/dranjan/python-plyfile
# Point cloud visualizer from https://github.com/daavoo/pyntcloud
import numpy as np
from plyfile import PlyData, PlyElement
from pyntcloud import PyntCloud

import sys
sys.path.append("../")
from photonMap import PhotonMap

# Convert the photon map photon locations to a PLY file
# Can be loaded in Blender for better visaulization
def convert_map_to_ply(map_path, ply_path, depth_filter=None):
    photon_map = PhotonMap(map_path)
    locs = np.array([],dtype=[('x','f4'), ('y','f4'),('z','f4')])

    for i in range(len(photon_map.map)):
        # Can only save photons with specific depth
        if depth_filter:
            if photon_map.map[i].depth != depth_filter:
                continue

        l = photon_map.map[i].location
        loc = np.array([(l[0], l[1], l[2])], \
        dtype=[('x','f4'), ('y','f4'),('z','f4')])
        locs = np.append(locs, loc)
    desc = PlyElement.describe(locs, 'vertex')
    PlyData([desc], text=True).write(ply_path)

# Show all the photons' locations in the PLY file
# Can also visulize PLY file in Blender using the following tool
# https://github.com/uhlik/bpy/blob/master/space_view3d_point_cloud_visualizer.py
# https://www.youtube.com/watch?v=eXct_7k779Q
def visualize_ply(ply_path):
    plydata = PyntCloud.from_file(ply_path)
    plydata.plot()

if __name__ == "__main__":
    map_path = "../profile/SingleMap.pkl"
    ply_path = "../profile/SingleMap.ply"
    convert_map_to_ply(map_path, ply_path)
    visualize_ply(ply_path)
