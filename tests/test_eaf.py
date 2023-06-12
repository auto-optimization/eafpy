import sys
import os
import numpy as np
import pytest

import eafpy
from eafpy.eafpy import read_datasets


def test_libeaf_read_datasets():
    """
    Check that the libeaf.read_datasets() functions returns the same array as the
    one that I pre-calculated earlier.
    """
    testdata = read_datasets("test_data/read_datasets.dat")
    check_data = np.load("test_data/read_datasets.npy")
    assert testdata == check_data
