# The implementation of Photon and PhotonMap
# PhotonMap is based on mathutils.kdtree.KDTree
# https://docs.blender.org/api/2.90/mathutils.kdtree.html
# This script should be run from Blender render() method
from mathutils.kdtree import KDTree
import numpy as np
from random import random
from time import time


# The class for one photon
class Photon():
    def __init__(self, photon_id=None):
        self.id = photon_id  # photon id, starting from 0
        self.location = None  # photon location
        self.direction = None  # photon direction
        self.depth = 0 # Set to n to represent it is the nth intersection

    def set_loc(self, x, y, z):
        self.location = np.array([x, y, z])

    def set_dir(self, x, y, z):
        self.direction = np.array([x, y, z])

    def copy(self):  # copy every field except for id
        copy = Photon()
        copy.location = self.location
        copy.direction = self.direction
        copy.depth = self.depth
        return copy

    def print_photon(self):
        assert(self.id)
        assert(self.location)
        assert(self.direction)
        print(f'ID: {self.id} \
            Location: {self.location[0]:.3f}, {self.location[1]:.3f}, {self.location[2]:.3f}; \
            Direction: {self.direction[0]:.3f}, {self.direction[1]:.3f}, {self.direction[2]:.3f}.')


# The class for a photon map, size will never decrease
class PhotonMap():
    def __init__(self, map_path=None):
        # HashTable to store all photons
        # key is photon id
        # value is the photon object corresponding to the id
        if (map_path):
            import pickle
            file = open(map_path, "rb")
            self.map = pickle.load(file)
            file.close()
            print("Load photon map of size: ", len(self.map))
        else:
            self.map = {}
            print("Init an empty photon map")

        # KDTree to store photon locations
        self.kdtree = None

        self.depth = 0 # max photon depth in the map

    # build the KDTree and balance it
    # call it after finishing all add_photon()
    def build_tree(self):
        self.kdtree = KDTree(len(self.map))
        for p in self.map.values():
            self.kdtree.insert(p.location, p.id)
        self.kdtree.balance()
        print("Build tree of size: ", len(self.map))

    # return an available id for a new photon
    def get_id(self):
        return len(self.map)

    # add each single photon to the map
    # call build_tree() after all add_photon()
    def add_photon(self, p):
        self.map[p.id] = p

    # find n nearest photons to a given location
    # return the photons' ids
    # need build_tree() before calling this function
    def find_photons_n(self, loc, n):
        # built-in function returns a list of tuples: (location, id, distance)
        results = self.kdtree.find_n(loc, n)
        ids = []
        for result in results:
            ids.append(result[1])
        # print("Query results size: ", len(ids))
        return ids

    # find all photons within a radius of a given location
    # return the photons' ids
    # need build_tree() before calling this function
    def find_photons_r(self, loc, r):
        results = self.kdtree.find_range(loc, r)
        ids = []
        for result in results:
            ids.append(result[1])
        # print("Query results size: ", len(ids))
        return ids

    # save self.map to a file
    # for separate map building and rendering
    def save_map(self, path):
        import pickle
        file = open(path, "wb")
        pickle.dump(self.map, file)
        file.close()

    # save all the photon locations
    # for debug and visualization
    def save_locations(self, path):
        locations = np.zeros((len(self.map), 3))
        for i in range(len(self.map)):
            locations[i][:] = self.map[i].location
        np.save(path, locations)

    # check the correctness of photon map
    def check_correctness(self):
        assert(self.map)
        assert(self.kdtree)

        # each photon show match a location in KDTree
        for photon_id in self.map.keys():
            p = self.map[photon_id]
            assert(photon_id == self.kdtree.find_n(p.location, 1)[0][1])
        print("Check correctness success!")


def profile(map_size, num_query, query_radius, dir_path=None):
    map_size = int(map_size)
    num_query = int(num_query)

    photon_map = PhotonMap()

    t0 = time()

    for i in range(map_size):
        p = Photon(photon_map.get_id())
        p.set_loc(random(), random(), random())
        p.set_dir(random(), random(), random())
        photon_map.add_photon(p)

    t1 = time()

    photon_map.build_tree()

    t2 = time()

    for i in range(num_query):
        photon_map.find_photons_r(np.random.rand(3), query_radius)

    t3 = time()

    print("==========================")
    print(f'Profile result of map_size {map_size}, num_query {num_query}, query_radius {query_radius:.2f}')
    print(f'Map contruction: {t1 - t0: .2f} seconds.')
    print(f'Build KDTree: {t2 - t1: .2f} seconds.')
    print(f'Query KDTree: {t3 - t2: .2f} seconds.')
    print("==========================")

    photon_map.check_correctness()

    if (dir_path):
        from os.path import join
        map_path = join(dir_path, "map.pkl")
        loc_path = join(dir_path, "locations.npy")
        photon_map.save_map(map_path)
        photon_map.save_locations(loc_path)

def test_load_map(map_path):
    photon_map = PhotonMap(map_path)
    photon_map.build_tree()
    photon_map.check_correctness()

if __name__ == "__main__":
    pass
