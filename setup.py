from setuptools import setup

setup(
    setup_requires=["cffi>=1.0.0"],
    cffi_modules=["src/eafpy/build_c_eaf.py:ffibuilder"],
    install_requires=["cffi>=1.0.0"],
    package_data={"": ["*.h", "*.c"]},
)
