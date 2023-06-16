import numpy as np
import os
from enum import Enum
from eafpy.c_bindings import lib, ffi


class ReadDatasetsError(Exception):
    """
    Custom exception class for an error returned by

    Attributes:
    Error - Error code returned by C library
    """

    errors = [
        "NO_ERROR",
        "READ_INPUT_FILE_EMPTY",
        "READ_INPUT_WRONG_INITIAL_DIM",
        "ERROR_FOPEN",
        "ERROR_CONVERSION",
        "ERROR_COLUMNS",
    ]

    def __init__(self, error):
        self.error = error
        self.message = self.errors[abs(error)]
        super().__init__(self.message)


"""
Libeaf contains wrapper functions for the EAF C library. 
The CFFI library is used to create C binding
"""


def read_datasets(filename):
    """
    read_input_data reads an input dataset and returns a 2d numpy array.
    The first n-1 columns contain the numerical data for each of the objectives
    The last column contains an identifier for which set the data is relevant to.

    For example:
    Objective 1  |  Objective 2 | Set number
    [ 8.7475454  |  1.71575862  | 1.        ]
    [ 0.58799475 |  0.73891181  | 1.        ]
    [ 8.58848772 |  3.69781313  | 2.        ]
    [ 1.5964888  |  5.98825094  | 2.        ]
    """
    if not os.path.isfile(filename):
        raise FileNotFoundError(f"file {filename} not found")

    # Encode filename to a binary string
    _filename = filename.encode("utf-8")
    # Create return pointers for function
    data_p = ffi.new("double **", ffi.NULL)
    num_obj_p = ffi.new("int *", 0)
    nrows_p = ffi.new("int *", 0)
    datasize_p = ffi.new("int *", 0)
    err_code = lib.read_datasets_(_filename, data_p, num_obj_p, nrows_p, datasize_p)
    if err_code != 0:
        raise ReadDatasetsError(err_code)

    # Create buffer with the correct array size in bytes
    data_buf = ffi.buffer(data_p[0], datasize_p[0])
    flat_data = np.frombuffer(data_buf)
    # Convert 1d numpy array to 2d array with (n obj... , sets) columns
    shaped_data = np.reshape(flat_data, (-1, (num_obj_p[0] + 1)))
    return shaped_data
