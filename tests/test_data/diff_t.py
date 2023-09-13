import eafpy as eaf
import numpy as np

diff1 = np.loadtxt("100_diff_points_1.txt")
diff2 = np.loadtxt("100_diff_points_2.txt")

diff = eaf.get_diff_eaf(diff1, diff2)
np.savetxt("python_diffeaf.txt", diff)
print(diff)
print(diff.shape)
