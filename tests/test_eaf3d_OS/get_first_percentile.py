import eafpy as eaf
import numpy as np

dataset = eaf.read_datasets("spherical-250-10-3d.txt")
first_level = eaf.filter_dominated(np.ascontiguousarray(dataset[:, :3]))
np.savetxt("output/filter_dominated_spherical_250-10-3d.txt", first_level)
