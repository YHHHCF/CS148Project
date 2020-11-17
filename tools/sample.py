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
	x_axis = np.array([1, 0, 0])
	if np.abs(np.dot(x_axis, norm)) > 0.9:
		x_axis = np.array([0, 1, 0])

	x_axis -= np.dot(x_axis, norm) * norm
	x_axis = normalize(x_axis)

	y_axis = np.cross(x_axis, norm)

	for i in range(n):
		# theta is altitute cos(theta): [-1, 1]
		cos_theta = np.random.rand() * 2 * ratio + (1 - 2 * ratio)
		sin_theta = np.sqrt(1 - cos_theta * cos_theta)

		# phi is longitute [0, 2*pi]
		phi = 2 * np.pi * np.random.rand()

		# res[i][0] = sin_theta * np.cos(phi) * x_axis
		# res[i][1] = sin_theta * np.sin(phi) * y_axis
		# res[i][2] = cos_theta * norm
		res[i] = sin_theta * np.cos(phi) * x_axis + sin_theta * np.sin(phi) * y_axis + cos_theta * norm

	return res

# Sample on a 2D circle area
# 
def sample_2d_circle(n):
	pass

# Return a boolean result with probability of p to be True
def sample_bernoulli(p):
	return np.random.binomial(1, p, 1)[0] == 1

# Normalize a 1D numpy array
def normalize(arr):
	return arr / np.linalg.norm(arr)

if __name__ == "__main__":
	norm = np.array([0, 0, 1])
	dirs = sample_dirs(10000, norm, 0.8)
	np.save("./dirs.npy", dirs)

	visualize("./dirs.npy")
