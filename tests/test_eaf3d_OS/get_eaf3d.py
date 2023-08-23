import eafpy as eaf
import platform
import numpy as np

os_name = platform.system()
datasets = eaf.read_datasets("spherical-250-10-3d.txt"), eaf.read_datasets(
    "uniform-250-10-3d.txt"
)
spherical = eaf.get_eaf(datasets[0])
uniform = eaf.get_eaf(datasets[1])
np.save(f"{os_name}_spherical_eaf3d", spherical)
np.save(f"{os_name}_uniform_eaf3d", uniform)
