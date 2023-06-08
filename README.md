[![Package Build Status](https://github.com/auto-optimization/eafpy/actions/workflows/tests.yaml/badge.svg)](https://github.com/auto-optimization/eafpy/actions/workflows/tests.yaml) [![Test Status](https://github.com/auto-optimization/eafpy/actions/workflows/tests.yaml/badge.svg)](https://github.com/auto-optimization/eafpy/actions/workflows/tests.yaml)

# eafpy
# TODO basic Python setup
- [x] basic Python package structure (https://packaging.python.org/en/latest/tutorials/packaging-projects/)
- [x] setup for testing (https://mathspp.com/blog/how-to-create-a-python-package-in-2022)
- [x] github actions that build the package run the testsuite (https://mathspp.com/blog/how-to-create-a-python-package-in-2022)
  - [x] for Linux
  - [x] for Windows
  - [x] for macOS
- [ ] setup for C extensions (see below)
- [ ] Other nice things to have (but lower priority):
  - [ ] Documentation: (short intro: https://docs.python-guide.org/writing/documentation/) Longer: https://py-pkgs.org/06-documentation.html
  - [ ] Tutorial showing how to use the package: add it to the documentation or as a jupyter notebook.

# TODO Setup for C extensions

We want to do the following in Python:
```python
import eaf
x = eaf.read_datasets("input1.data")
# x is now a Numpy matrix with 3 columns and 100 rows. The first three rows are:
# 8.0755965 2.4070255   1
# 8.6609445 3.6405014   1
# 0.2081643 4.6227547   1
...
# The last three rows are:
# 1.2223439 5.6895031  10
# 7.9946696 2.8112254  10
# 2.1270029 2.4311417  10
print(x)
```
  - [ ] The function `read_datasets` will call the C function `read_double_data()` either directly or via another C function (see next point) and setup everything that it needs to return a NumPy matrix.
  - [ ] You may need to add additional C code to interface between Python and C. This is OK (see how I did it in R: https://github.com/MLopez-Ibanez/eaf/blob/5be4108dc02c10f48ea5ebedbeaaccf504531791/src/Reaf.c#L329)
  - [ ] Investigate options available (ctype, CFFI or something else): What are the positives and negatives of each option?
  - [ ] Add a few tests to make sure it is working as expected.
  - [ ] Setup github actions / package build for Windows, macOS and Linux.
  - [ ] Once the above is working, we will add more C functions.

