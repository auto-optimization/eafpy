import numpy as np
import os

print("Eaf.py root directories: ")
print(os.listdir())
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

    # THis is not working -> It is pointing to the eafpy script,
    # Not the    script thag called it originally
    script_dir = os.path.dirname(os.path.abspath(__file__))
    print(script_dir)
    file_path = os.path.join(script_dir, filename)

    print(file_path)

    assert os.path.isfile(file_path), f"{file_path} was not found"

    # Encode filename to a binary string
    _filename = file_path.encode("utf-8")
    # Create return pointers for function
    returndata_p = ffi.new("double **", ffi.NULL)
    num_obj_p = ffi.new("int *", 0)
    cumulative_size_p = ffi.new("int **", ffi.NULL)
    num_sets_p = ffi.new("int *", 0)
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

    # I could not get the ffi buffer to work for cumsize so I copy manually
    np_cumulative_size = np.empty(num_sets_p[0])
    for i in range(num_sets_p[0]):
        np_cumulative_size[i] = cumulative_size_p[0][i]

    # Assign set numbers for each row of the data based on the cumulative size
    set_numbers = np.digitize(np.arange(dataset_np_2d.shape[0]), np_cumulative_size) + 1
    # Add a third column including the set number
    return_data = np.hstack((dataset_np_2d, set_numbers.reshape(data_rows, 1)))
    return return_data
