import numpy as np
import os

from eafpy.c_bindings import lib, ffi


"""
Libeaf contains wrapper functions for the EAF C library. 
The CFFI library is used to create C binding
"""


def read_datasets(filename):
    """
    read_input_data reads an input `.dat` dataset and returns a 2d numpy array.
    The first n-1 columns contain the numerical data for each of the objectives
    The last column contains an identifier for which set the data is relevant to.

    For example:
    Objective 1  |  Objective 2 | Set number
    [ 8.7475454  |  1.71575862  | 1.        ]
    [ 0.58799475 |  0.73891181  | 1.        ]
    [ 8.58848772 |  3.69781313  | 2.        ]
    [ 1.5964888  |  5.98825094  | 2.        ]
    """

    # ROONEY: Instead of assert you should raise the appropriate exception: https://docs.python.org/3/library/exceptions.html In this case FileNotFoundError.
    # ROONEY: Did you add a test for this error?
    assert os.path.isfile(filename), f"file {filename} not found"
    
    # Encode filename to a binary string
    _filename = filename.encode("utf-8")
    # Create return pointers for function
    returndata_p = ffi.new("double **", ffi.NULL)
    num_obj_p = ffi.new("int *", 0)
    cumulative_size_p = ffi.new("int **", ffi.NULL)
    num_sets_p = ffi.new("int *", 0)
    # ROONEY: You need to check the error code and if it is != 0, raise an error. Add a test for this.
    err_code = lib.read_double_data(
        _filename, returndata_p, num_obj_p, cumulative_size_p, num_sets_p
    )
    # Get the number of rows in the dataset
    data_rows = cumulative_size_p[0][num_sets_p[0] - 1]
    # Size of return data buffer in bytes
    data_size = num_obj_p[0] * data_rows * ffi.sizeof("double")
    return_buff = ffi.buffer(returndata_p[0], data_size)
    dataset_np_1d = np.frombuffer(return_buff)
    # Split 1d array into 2d array depending on number of objectives
    dataset_np_2d = dataset_np_1d.reshape(-1, num_obj_p[0])

    ## ROONEY: Do you really need to do all this here? It seems simpler to do
    ## it directly in C and have a C function that returns the correct data,
    ## nobjs and nrows, which is the only info that you actually need. I added
    ## a C function read_datasets_.
    
    # I could not get the ffi buffer to work for cumsize so I copy manually
    np_cumulative_size = np.empty(num_sets_p[0])
    for i in range(num_sets_p[0]):
        np_cumulative_size[i] = cumulative_size_p[0][i]

    # Assign set numbers for each row of the data based on the cumulative size
    set_numbers = np.digitize(np.arange(dataset_np_2d.shape[0]), np_cumulative_size) + 1
    # Add a third column including the set number
    return_data = np.hstack((dataset_np_2d, set_numbers.reshape(data_rows, 1)))
    return return_data
