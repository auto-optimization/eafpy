import sys
import os
import numpy as np
import pytest
import math

# ROONEY: We should rename the package to just eaf
import eafpy as eaf


def test_read_datasets_data():
    """
    Check that the eaf.read_datasets() functions returns the same array as the
    one that I pre-calculated earlier.
    """
    test_names = [
        "input1.dat",
        "spherical-250-10-3d.txt",
        "uniform-250-10-3d.txt",
        "wrots_l10w100_dat",
        "wrots_l100w10_dat",
    ]
    expected_names = [
        "input1.npy",
        "spherical-250-10-3d.npy",
        "uniform-250-10-3d.npy",
        "wrots_l10w100_dat.npy",
        "wrots_l100w10_dat.npy",
    ]
    expected_shapes = [(100, 3), (2500, 4), (2500, 4), (3262, 3), (888, 3)]

    for i, test in enumerate(test_names):
        testdata = eaf.read_datasets(f"tests/test_data/{test}")
        check_data = np.load(f"tests/test_data/expected_output/{expected_names[i]}")
        expected_shape = expected_shapes[i]
        assert (
            testdata.shape == expected_shape
        ), f"Read data array has incorrect shape, should be {expected_shape} but is {testdata.shape}"
        assert (
            testdata == check_data
        ).all(), f"read_datasets does not produce expected array for file {test}"


def test_read_datasets_badname():
    """
    Check that the eaf.read_datasets() functions fails correctly after a
    bad file name is input
    """
    with pytest.raises(Exception) as expt:
        eaf.read_datasets("nonexistent_file.txt")

    assert str(expt.value) == f"file nonexistent_file.txt not found"
    assert expt.type == FileNotFoundError


def test_read_datasets_errorcode():
    """
    Checks that an exception is raised when read_datasets() returns an
    error code, as well as checking specific error types
    from the ReadDatasetsError type
    """

    with pytest.raises(Exception) as expt:
        eaf.read_datasets("tests/test_data/empty")
    assert expt.type == eaf.ReadDatasetsError
    assert expt.value.message == "READ_INPUT_FILE_EMPTY"

    with pytest.raises(Exception) as expt:
        eaf.read_datasets("tests/test_data/column_error.dat")
    assert expt.type == eaf.ReadDatasetsError
    assert expt.value.message == "ERROR_COLUMNS"


def test_hv_output():
    """
    Checks the hypervolume calculation produces the correct value
    """
    X = eaf.read_datasets(f"tests/test_data/input1.dat")
    hv = eaf.hv(X[X[:, 2] == 1, :2], ref=np.array([10, 10]))
    assert math.isclose(hv, 90.46272765), "input1.dat hypervolume produces wrong output"

    hv = eaf.hv(X[X[:, 2] == 1, :2], ref=[10, 10])
    assert math.isclose(hv, 90.46272765), "input1.dat hypervolume produces wrong output"


def test_hv_wrong_ref():
    """
    Check that the eaf.hv() functions fails correctly after a ref with the wrong
    dimensions is input
    """
    X = eaf.read_datasets(f"tests/test_data/input1.dat")

    with pytest.raises(Exception) as expt:
        hv = eaf.hv(X[X[:, 2] == 1, :2], ref=np.array([10, 10, 10]))
    assert expt.type == ValueError


def test_plt_dta_types():
    """
    Check that the eaf.plot_datasets() functions has the right input handling
    """
    X = eaf.read_datasets(f"tests/test_data/input1.dat")
    with pytest.raises(Exception) as expt:
        eaf.plot_datasets(datasets="Wrong input")
        assert expt.type == TypeError
    with pytest.raises(Exception) as expt:
        eaf.plot_datasets(datasets=np.ndarray([50, 1]))
        assert expt.type == ValueError
    with pytest.raises(Exception) as expt:
        eaf.plot_datasets(datasets=np.ndarray([50, 5]))
        assert expt.type == ValueError
    with pytest.raises(Exception) as expt:
        eaf.plot_datasets(X, type="Bugel horn")
        assert expt.type == ValueError
    eaf.plot_datasets(X, type="points,lines")
    eaf.plot_datasets(X, type="p,l")
    eaf.plot_datasets(X, type="l  ,p")
    eaf.plot_datasets(X, type="points,l")
    eaf.plot_datasets(X, type="point ,lines")
    eaf.plot_datasets(X, type="LiNe ,  PoInTs")
