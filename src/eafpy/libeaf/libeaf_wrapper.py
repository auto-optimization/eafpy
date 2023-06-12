import libeaf
import numpy as np
from libeaf import lib, ffi

"""


"""


def read_input_data(filename):
    # Encode filename to a binary string
    _filename = filename.encode("utf-8")
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


read_input_data("input1.dat")
