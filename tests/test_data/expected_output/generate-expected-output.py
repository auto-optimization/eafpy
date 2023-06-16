from eafpy import eaf
import numpy as np

# DON'T RE-RUN!
# Here I generate the files for test comparison and manually check that they are correct, for read_dataset function
# It would be better if I had another method for testing their contents.

ds2 = eaf.read_datasets("spherical-250-10-3d.txt")
ds3 = eaf.read_datasets("uniform-250-10-3d.txt")
ds4 = eaf.read_datasets("wrots_l10w100_dat")
ds5 = eaf.read_datasets("wrots_l100w10_dat")

np.save("spherical-250-10-3d", ds2)
np.save("uniform-250-10-3d", ds3)
np.save("wrots_l10w100_dat", ds4)
np.save("wrots_l100w10_dat", ds5)


print(ds2[-1, :])
print(ds3[-1, :])
print(ds4[-1, :])
print(ds5[-1, :])

print(ds2.shape)
print(ds3.shape)
print(ds4.shape)
print(ds5.shape)
