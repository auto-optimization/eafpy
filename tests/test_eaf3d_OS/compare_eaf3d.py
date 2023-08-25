import numpy as np
import os


names = (
    "Windows_spherical_eaf3d.txt",
    "Windows_uniform_eaf3d.txt",
    "Linux_spherical_eaf3d.txt",
    "Linux_uniform_eaf3d.txt",
)
files_found = False not in [os.path.isfile(f"output/{name}") for name in names]
assert files_found

load_files = {
    name: file
    for (name, file) in zip(
        names, [np.loadtxt(f"output/{filename}") for filename in names]
    )
}
spherical_windows_minus_linux = (
    load_files["Windows_spherical_eaf3d.txt"] - load_files["Linux_spherical_eaf3d.txt"]
)
uniform_windows_minus_linux = (
    load_files["Windows_uniform_eaf3d.txt"] - load_files["Linux_uniform_eaf3d.txt"]
)

np.savetxt("output/spherical_windows_minus_linux.txt", spherical_windows_minus_linux)
np.savetxt("output/uniform_windows_minus_linux.txt", uniform_windows_minus_linux)

if not np.allclose(
    load_files["Windows_uniform_eaf3d.txt"], load_files["Linux_uniform_eaf3d.txt"]
):
    raise ValueError("Uniform dataset EAF3d values different for Windows and linux")

if not np.allclose(
    load_files["Windows_spherical_eaf3d.txt"], load_files["Linux_spherical_eaf3d.txt"]
):
    raise ValueError("Spherical dataset EAF3d values different for Windows and linux")
