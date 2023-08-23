import numpy as np
import os


names = (
    "Windows_spherical_eaf3d.npy",
    "Windows_uniform_eaf3d.npy",
    "Linux_spherical_eaf3d.npy",
    "Linux_uniform_eaf3d.npy",
)
files_found = False not in [os.path.isfile(name) for name in names]
assert files_found

load_files = {
    name: file for (name, file) in zip(names, [np.load(filename) for filename in names])
}
spherical_windows_minus_linux = (
    load_files["Windows_spherical_eaf3d.npy"] - load_files["Linux_spherical_eaf3d.npy"]
)
uniform_windows_minus_linux = (
    load_files["Windows_uniform_eaf3d.npy"] - load_files["Linux_uniform_eaf3d.npy"]
)

np.savetxt("spherical_windows_minus_linux.txt", spherical_windows_minus_linux)
np.savetxt("uniform_windows_minus_linux.txt", uniform_windows_minus_linux)

if not np.allclose(
    load_files["Windows_uniform_eaf3d.npy"], load_files["Linux_uniform_eaf3d.npy"]
):
    raise ValueError("Uniform dataset EAF3d values different for Windows and linux")

if not np.allclose(
    load_files["Windows_spherical_eaf3d.npy"], load_files["Linux_spherical_eaf3d.npy"]
):
    raise ValueError("Spherical dataset EAF3d values different for Windows and linux")
