import numpy as np

# Sample n 3D direction uniformly on sphere
# Return n normalized dir samples
def sample_dirs(n):
	res = np.zeros((n, 3))

	for i in range(n):
		# theta is altitute cos(theta): [-1, 1]
		cos_theta = np.random.rand() * 2 - 1
		sin_theta = np.sqrt(1 - cos_theta * cos_theta)

		# phi is longitute [0, 2*pi]
		phi = 2 * np.pi * np.random.rand()

		res[i][0] = sin_theta * np.cos(phi)
		res[i][1] = sin_theta * np.sin(phi)
		res[i][2] = cos_theta

	return res

if __name__ == "__main__":
	dirs = sample_dirs(10000)
	np.save("./dirs.npy", dirs)

	from visualize import visualize
	visualize("./dirs.npy")
