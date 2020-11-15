# Scipy implementation deprecated
# Will use mathutils KDTree, which is better supported in Blender

from scipy.spatial import KDTree
import numpy as np
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
from random import random
from time import time

# get the hash value of a location
def hash_loc(location):
    return hash(str(location))

# check whether 2 locatiosn are the same
def same_loc(loc1, loc2):
    eps = 1e-6
    diff = abs(loc1 - loc2)
    if diff[0] <= eps and diff[1] <= eps and diff[2] <= eps:
        print("Value equals!")
    else:
        print("Value not equals!")

    if hash_loc(loc1) == hash_loc(loc2):
        print("Hash equals!")
    else:
        print("Hash not equals!")

class Photon():
    def __init__(self):
        self.location = None  # photon location
        self.id = None  # hash of photon location
        self.direction = None  # photon direction

    def update_loc(self, x, y, z):
        self.location = np.array([x, y, z])
        self.id = hash_loc(self.location)

    def update_dir(self, x, y, z):
        self.direction = np.array([x, y, z])

    def print_photon(self):
        assert(self.id)
        assert(self.location)
        assert(self.direction)
        print(f'ID: {self.id} \
            Location: {self.location[0]:.3f}, {self.location[1]:.3f}, {self.location[2]:.3f}; \
            Direction: {self.direction[0]:.3f}, {self.direction[1]:.3f}, {self.direction[2]:.3f}.')

class PhotonMap():
    def __init__(self):
        self.kdtree = None  # KDTree to store locations

        # HashTable to store all photons
        # key is the hash of location
        # value is photon object
        self.map = {}

    def build_tree(self):
        loc_tmp = np.zeros((len(self.map), 3))
        idx = 0
        for k in self.map.keys():
            photon = self.map[k]
            loc_tmp[idx] = photon.location
            idx += 1
        self.kdtree = KDTree(loc_tmp)

    def add_photon(self, p):
        self.map[p.id] = p

    # return all the photon ids given a query (loc and radius)
    def query_photons(self, query_loc, query_radius):
        l = self.kdtree.query_ball_point(query_loc, query_radius)
        ids = []
        for i in range(len(l)):
            loc = self.kdtree.data[l[i]]
            ids.append(hash_loc(loc))
            # assert(hash_loc(loc) in self.map.keys())  # for debug
        return ids

    # show all the photons' locations in the map
    def show_photons(self):
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')

        x =[]
        y =[]
        z =[]

        for loc in self.kdtree.data:
            x.append(loc[0])
            y.append(loc[1])
            z.append(loc[2])

        ax.scatter(x, y, z, s=0.01, c='r', marker='o')

        ax.set_xlabel('X Label')
        ax.set_ylabel('Y Label')
        ax.set_zlabel('Z Label')

        plt.show()

    def check_correctness(self):
        assert(self.kdtree)
        assert(self.kdtree.n == len(self.map))

        # each location in KDtree should match location of one photon
        for loc in self.kdtree.data:
            assert(hash_loc(loc) in self.map.keys())

        # each photon's id should match it's location
        for photon_id in self.map.keys():
            assert(photon_id == hash_loc(self.map[photon_id].location))


def profile(map_size, num_query, query_radius, visualize=False):
    map_size = int(map_size)
    num_query = int(num_query)

    photon_map = PhotonMap()

    t0 = time()

    for i in range(map_size):
        p = Photon()
        p.update_loc(random(), random(), random())
        photon_map.add_photon(p)

    t1 = time()

    photon_map.build_tree()

    t2 = time()

    for i in range(num_query):
        photon_map.query_photons(np.random.rand(3), query_radius)

    t3 = time()

    print("==========================")
    print(f'Profile result of map_size {map_size}, num_query {num_query}, query_radius {query_radius:.2f}')
    print(f'Map contruction: {t1 - t0: .2f} seconds.')
    print(f'Build KDTree: {t2 - t1: .2f} seconds.')
    print(f'Query KDTree: {t3 - t2: .2f} seconds.')
    print("==========================")

    photon_map.check_correctness()

    if visualize:
        photon_map.show_photons()


if __name__ == "__main__":
    # profile(map_size=1e5, num_query=10, query_radius=0.1)
    # profile(map_size=1e5, num_query=50, query_radius=0.1)
    # profile(map_size=1e5, num_query=10, query_radius=0.2)
    # profile(map_size=1e6, num_query=10, query_radius=0.1)
    profile(map_size=1e5, num_query=10, query_radius=0.1, visualize=True)
