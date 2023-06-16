import sys
import os
import numpy as np
import pytest

# ROONEY: We should rename the package to just eaf
import eafpy as eaf


def test_read_datasets_data():
    """
    Check that the eaf.read_datasets() functions returns the same array as the
    one that I pre-calculated earlier.
    """
    testdata = eaf.read_datasets("tests/test_data/read_datasets.dat")
    check_data = np.load("tests/test_data/read_datasets.npy")
    assert (testdata == check_data).all()


def test_read_datasets_badname():
    """
    Check that the eaf.read_datasets() functions fails correctly after a
    bad file name is input
    """
    incorrect_filename = "nonexistent_file.txt"
    with pytest.raises(AssertionError) as excinfo:
        eaf.read_datasets(
            incorrect_filename
        )  # Call the function that contains the assertion

    assert str(excinfo.value) == f"file {incorrect_filename} not found"
