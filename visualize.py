import numpy as np
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt

# show all the photons' locations in the npy file
# used for debug
def visualize(path):
    locations = np.load(path)

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

if __name__ == "__main__":
	photon_map = visualize("./profile/locations.npy")
