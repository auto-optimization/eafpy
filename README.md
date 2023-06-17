[![Test Status](https://github.com/auto-optimization/eafpy/actions/workflows/tests.yaml/badge.svg)](https://github.com/auto-optimization/eafpy/actions/workflows/tests.yaml)

# eaf


## TODO basic Python setup
- [x] basic Python package structure (https://packaging.python.org/en/latest/tutorials/packaging-projects/)
- [x] setup for testing (https://mathspp.com/blog/how-to-create-a-python-package-in-2022)
- [x] github actions that build the package run the testsuite (https://mathspp.com/blog/how-to-create-a-python-package-in-2022)
  - [x] for Linux
  - [x] for Windows
  - [x] for macOS
- [x] setup for C extensions (see below)
- [ ] Rename the package to just `eaf`
- [ ] Move all `*.c` and `*.h` files to `libeaf/` so that the C code is separated from the Python code.
- [ ] Other nice things to have (but lower priority):
  - [ ] Coverage: https://github.com/codecov/example-python (see also: https://mathspp.com/blog/how-to-create-a-python-package-in-2022#running-coverage-py-with-tox)
  - [ ] Documentation: (short intro: https://docs.python-guide.org/writing/documentation/) Longer: https://py-pkgs.org/06-documentation.html
  - [ ] Tutorial showing how to use the package: add it to the documentation or as a jupyter notebook.
  - [ ] Source of good ideas: https://github.com/anyoptimization/pymoo/tree/main

## TODO Setup for C extensions

We want to do the following in Python:

```python
import eaf
x = eaf.read_datasets("input1.dat")
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
  - [x] The function `read_datasets` will call the C function `read_double_data()` either directly or via another C function (see next point) and setup everything that it needs to return a NumPy matrix.
  - [x] You may need to add additional C code to interface between Python and C. This is OK (see how I did it in R: https://github.com/MLopez-Ibanez/eaf/blob/5be4108dc02c10f48ea5ebedbeaaccf504531791/src/Reaf.c#L329)
  - [x] Investigate options available (ctype, CFFI or something else): What are the positives and negatives of each option?
  - [x] Add a few tests to make sure it is working as expected.
  - [x] Setup github actions / package build for Windows, macOS and Linux.
  - [ ] Next function is `fpli_hv` in `hv.h`
  
      ```python
       import eaf
       x = eaf.read_datasets("tests/test_data/input1.dat")
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
       z = hv(X[X[:,2] == 1, :2], ref = np.array([10, 10]))
       print(z)
       # It should be a single number: 90.4627276475589
      ```
  
  - [ ] Once the above is working, we will add more C functions.
  
## Developer instructions
### Quick start

```sh
pip install -r requirements_dev.txt
pre-commit install
py -m build
pip install -e .
# Run tests
py -m pytest-cov
```

It's not strictly neccesary to use a virtualenv for the dev requirements (setuptools makes its own virtualenv when building) but it is generally reccomend. I have skipped it for brevity. 

### Full instructions
Pip package manager is required. Ensure and upgrade pip:

`python3 -m ensurepip --upgrade`

#### Install required development packages

It is reccomended to create a new virtual environment for development. You can do this using virtual env:

`pip install virtualenv`

Create and activate a new virtual environment (You can do this in the repo root. It will create a `.gitignore`):

```sh
virtualenv -p python3 eaf_env
cd eaf_env/scripts 
activate
```

Now you can install the development packages in this fresh environment. You will need to make sure you have the environment activated every time you develop.

```sh
# cd to the repo root
pip install -r requirements_dev.txt
```

#### Install the pre-commit hooks for the repo

Pre-commit is a package that should now be installed, it adds some hooks that will execute when you make a new git commit, such as formatting the code with `black`.The `.pre-commmit-config.yaml` configures which hooks are used. You need to install these hooks locally using:

`pre-commit install`

#### Make sure you have a reccomended C compiler

This package uses the CFFI package to compile a C extension module, so if you want to build the project you need have one of the reccomended C compilers installed.
1. Windows: [MSVC - install Visual studio](https://visualstudio.microsoft.com/vs/features/cplusplus/)
2. Linux - get gcc 

    ```sh
    sudo apt update
    sudo apt install build-essential
    ```
    
3. MacOS - get gcc

   ```sh
   brew update
   brew upgrade
   brew install gcc
   ```

If you have more trouble with the compilation you can visit [this CFFI doc](https://cffi.readthedocs.io/en/latest/installation.html#:~:text=Requirements%3A,to%20compile%20C%20extension%20modules.)

#### Build the project
In order to test the package you need to build the project and install it. 

```sh
# CD to the repo root

# For windows
py -m build

# For Linux/ Macos
python3 -m build
```

You can now install the package. Use this command:
`pip install -e .`
It is reccomended to reinstall  the package every time you want to test an update
You can now test the installation worked by running the tests 

#### Run the tests
If you have installed the package, you can run the tests by simply going to package root and executing:

`pytest --cov`

(Note that `pytest` will not work if the package is not installed, even if the C files are compiled. This is because of the way the imports work)

You can run the test suite that is executed in the github actions by running tox

```sh
cd /repo_root
tox
```

Some of these tests may fail because `tox` is setup to test several different python version that you might not have installed. `tox.ini` is used to configure `tox`.

#### Developing C extension without full package build

You can test the c extension without doing the entire build, this can speed up developing the C extension. (You need to have the development requirements installed)

```sh
cd src/eafpy/
# Compile the C extension with CFFI
py build_c_eaf.py
# Now you can open an interpretor and import the package c_bindings
```
