import numpy as np

import sys
sys.path.append("../deprecated")
from visualize_loc import visualize


# Sample n 3D direction uniformly on sphere
# norm is the sphere direction, np array
# ratio [0, 1] is the ratio of theta we are sampling
# ratio = 1 is sphere, 0.5 is hemisphere, 0 is single point
# Return n normalized dir samples
def sample_dirs(n, norm, ratio):
	res = np.zeros((n, 3))

	# compute 2 orthogonal directions (x, y) to norm
	x_axis, y_axis = build_coordinate(norm)

	for i in range(n):
		# theta is altitute cos(theta): [-1, 1]
		cos_theta = np.random.rand() * 2 * ratio + (1 - 2 * ratio)
		sin_theta = np.sqrt(1 - cos_theta * cos_theta)

		# phi is longitute [0, 2*pi]
		phi = 2 * np.pi * np.random.rand()

		# Compute the sampled direction based on x, y and z (norm) axis
		res[i] = sin_theta * np.cos(phi) * x_axis + \
		sin_theta * np.sin(phi) * y_axis + cos_theta * norm

	return res

# Sample on a 2D disk area defined by norm and radius
# return the n sample positions
def sample_disk_loc(n, norm, radius):
	res = np.zeros((n, 3))

	# compute 2 orthogonal directions (x, y) to norm
	x_axis, y_axis = build_coordinate(norm)

	for i in range(n):
		r = np.sqrt(np.random.rand()) * radius
		theta = 2 * np.pi * np.random.rand()
		res[i] = r * np.cos(theta) * x_axis + \
		 r * np.sin(theta) * y_axis

	return res


# Return a boolean result with probability of p to be True
def sample_bernoulli(p):
	return np.random.binomial(1, p, 1)[0] == 1

# Normalize a 1D numpy array
def normalize(arr):
	return arr / np.linalg.norm(arr)

# Compute 2 normalized orthogonal axis given one direction
def build_coordinate(norm):
	# Choose a good x direction
	x_axis = np.array([1., 0., 0.])
	if np.abs(np.dot(x_axis, norm)) > 0.9:
		x_axis = np.array([0., 1., 0.])

	x_axis -= np.dot(x_axis, norm) * norm
	x_axis = normalize(x_axis)

	# Compute y direction from cross product
	y_axis = np.cross(x_axis, norm)

	return x_axis, y_axis


if __name__ == "__main__":
	norm = np.array([1., 2., 3.])
	norm = normalize(norm)

	sphere_dirs = sample_dirs(10000, norm, 0.2)
	np.save("./sphere_dirs.npy", sphere_dirs)
	visualize("./sphere_dirs.npy")

	disk_locs = sample_disk_loc(10000, norm, 1)
	np.save("./disk_locs.npy", disk_locs)
	visualize("./disk_locs.npy")
