# Debug tools to convert photon points in the map to PLY file
# Visualize in either blender or pyntcloud
# PLY writer from https://github.com/dranjan/python-plyfile
# Point cloud visualizer from https://github.com/daavoo/pyntcloud
import numpy as np
from plyfile import PlyData, PlyElement
from pyntcloud import PyntCloud
from sample import normalize

# Create n ply vertex
def create_ply_vertex(n, ply_path):
    # x, y, z for location; nx, ny, nz for norm
    points = np.array([],dtype=[('x','f4'), ('y','f4'), ('z','f4'), \
        ('nx','f4'), ('ny','f4'),('nz','f4')])

    for i in range(n):
        l = np.random.rand(3)  # location
        n = np.random.rand(3)  # norm
        n = normalize(n)
        point = np.array([(l[0], l[1], l[2], n[0], n[1], n[2])], \
        dtype=[('x','f4'), ('y','f4'), ('z','f4'), \
        ('nx','f4'), ('ny','f4'), ('nz','f4')])
        points = np.append(points, point)

    desc = PlyElement.describe(points, 'vertex')
    PlyData([desc], text=True).write(ply_path)

# Convert the photon map photon locations to a PLY file
# Can be loaded in Blender for better visaulization
def convert_map_to_ply(map_path, ply_path, depth_filter=None):
    import sys
    sys.path.append("../")
    from photonMap import PhotonMap

    photon_map = PhotonMap(map_path)
    photons = np.array([],dtype=[('x','f4'), ('y','f4'), ('z','f4'), \
        ('nx','f4'), ('ny','f4'),('nz','f4')])

    for i in range(len(photon_map.map)):
        # Can only save photons with specific depth
        if depth_filter:
            if photon_map.map[i].depth != depth_filter:
                continue

        l = photon_map.map[i].location
        n = photon_map.map[i].direction
        photon = np.array([(l[0], l[1], l[2], n[0], n[1], n[2])], \
        dtype=[('x','f4'), ('y','f4'), ('z','f4'), \
        ('nx','f4'), ('ny','f4'), ('nz','f4')])
        photons = np.append(photons, photon)
    desc = PlyElement.describe(photons, 'vertex')
    PlyData([desc], text=True).write(ply_path)

# Show all the photons' locations in the PLY file
# Can also visulize PLY file in Blender using the following tool
# https://github.com/uhlik/bpy/blob/master/space_view3d_point_cloud_visualizer.py
# https://www.youtube.com/watch?v=eXct_7k779Q
def visualize_ply(ply_path):
    plydata = PyntCloud.from_file(ply_path)
    plydata.plot()

if __name__ == "__main__":
    # map_path = "../profile/SingleMap.pkl"
    # ply_path = "../profile/SingleMap.ply"
    # convert_map_to_ply(map_path, ply_path)
    # visualize_ply(ply_path)

    test_ply_path = "./test.ply"
    create_ply_vertex(1000, test_ply_path)
    visualize_ply(test_ply_path)