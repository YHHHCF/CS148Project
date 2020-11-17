import numpy as np
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt

# Show all the photons' locations in the npy file
# Plot in matplotlib, used for debug
def visualize(path):
    locations = np.load(path, allow_pickle=True)

    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    print(f'Visualize{locations.shape[0]: d} locations.')
    x = locations[:, 0]
    y = locations[:, 1]
    z = locations[:, 2]

    ax.scatter(x, y, z, s=0.01, c='r', marker='o')

    ax.set_xlabel('X Label')
    ax.set_ylabel('Y Label')
    ax.set_zlabel('Z Label')

    plt.show()


# Translate the photon map file to a ply file
# Can be loaded in Blender for better visaulization
def save_as_ply(path):
    pass

if __name__ == "__main__":
	visualize("../profile/locations.npy")
