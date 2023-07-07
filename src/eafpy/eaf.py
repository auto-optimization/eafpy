import numpy as np
import os
from eafpy.c_bindings import lib, ffi


class ReadDatasetsError(Exception):
    """
    Custom exception class for an error returned by the read_datasets function

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

import lzma
import shutil
import tempfile


def read_datasets(filename):
    """
    Reads an input dataset and returns a 2d numpy array.
    The first n-1 columns contain the numerical data for each of the objectives
    The last column contains an identifier for which set the data is relevant to.

    If the filename has extension '.xz', it is decompressed to a temporary file before reading it.

    For example:
    Objective 1  |  Objective 2 | Set number
    [ 8.7475454  |  1.71575862  | 1.        ]
    [ 0.58799475 |  0.73891181  | 1.        ]
    [ 8.58848772 |  3.69781313  | 2.        ]
    [ 1.5964888  |  5.98825094  | 2.        ]
    """

    filename = os.path.expanduser(filename)
    if not os.path.isfile(filename):
        raise FileNotFoundError(f"file {filename} not found")

    if filename.endswith(".xz"):
        with lzma.open(filename, "rb") as fsrc:
            with tempfile.NamedTemporaryFile(delete=False) as fdst:
                shutil.copyfileobj(fsrc, fdst)
        filename = fdst.name
    else:
        fdst = None

    # Encode filename to a binary string
    _filename = filename.encode("utf-8")
    # Create return pointers for function
    data_p = ffi.new("double **", ffi.NULL)
    ncols_p = ffi.new("int *", 0)
    datasize_p = ffi.new("int *", 0)
    err_code = lib.read_datasets_(_filename, data_p, ncols_p, datasize_p)
    if fdst:
        os.remove(fdst.name)
    if err_code != 0:
        raise ReadDatasetsError(err_code)

    # Create buffer with the correct array size in bytes
    data_buf = ffi.buffer(data_p[0], datasize_p[0])
    # Convert 1d numpy array to 2d array with (n obj... , sets) columns
    array = np.frombuffer(data_buf).reshape((-1, ncols_p[0]))
    return array


def _parse_maximise(maximise, nobj):
    # Converts maximise array or single bool to ndarray format
    # I.E if 3 objectives, maximise = True -> maximise = (1,1,1)
    # eg. 3 objectives, maximise = [True, False, True] -> maximise = (1,0,1)
    maximise = np.atleast_1d(maximise).astype(int)
    if len(maximise) == 1:
        maximise = np.full((nobj), maximise[0])
    else:
        if maximise.shape[0] != nobj:
            raise ValueError(
                "Maximise array must have same # of cols as data"
                f"{maximise.shape[0]} != {nobj}"
            )
    return maximise


def _unary_refset_common(data, ref, maximise):
    # Convert to numpy.array in case the user provides a list.  We use
    # np.asfarray to convert it to floating-point, otherwise if a user inputs
    # something like ref = np.array([10, 10]) then numpy would interpret it as
    # an int array.
    data = np.asfarray(data)
    ref = np.atleast_2d(np.asfarray(ref))
    nobj = data.shape[1]
    if nobj != ref.shape[1]:
        raise ValueError(
            f"data and ref need to have the same number of columns ({nobj} != {ref.shape[1]})"
        )
    maximise = _parse_maximise(maximise, nobj)

    return data, ref, maximise


def igd(data, ref, maximise=False):
    """TODO: Take documentation from: https://mlopez-ibanez.github.io/eaf/reference/igd.html"""

    data, ref, maximise = _unary_refset_common(data, ref, maximise)
    data_p = ffi.cast("double *", ffi.from_buffer(data))
    nobj = ffi.cast("int", data.shape[1])
    npoints = ffi.cast("int", data.shape[0])
    ref_p = ffi.cast("double *", ffi.from_buffer(ref))
    ref_size = ffi.cast("int", ref.shape[0])
    maximise_p = ffi.cast("int *", ffi.from_buffer(maximise))
    print(maximise)
    return lib.igd_C(data_p, nobj, npoints, ref_p, ref_size, maximise_p)


def igd_plus(data, ref, maximise=False):
    """TODO: Take documentation from: https://mlopez-ibanez.github.io/eaf/reference/igd.html"""
    data, ref, maximise = _unary_refset_common(data, ref, maximise)
    data_p = ffi.cast("double *", ffi.from_buffer(data))
    nobj = ffi.cast("int", data.shape[1])
    npoints = ffi.cast("int", data.shape[0])
    ref_p = ffi.cast("double *", ffi.from_buffer(ref))
    ref_size = ffi.cast("int", ref.shape[0])
    maximise_p = ffi.cast("int *", ffi.from_buffer(maximise))
    return lib.igd_plus_C(data_p, nobj, npoints, ref_p, ref_size, maximise_p)


def avg_hausdorff_dist(data, ref, maximise=False, p=1):
    """TODO: Take documentation from: https://mlopez-ibanez.github.io/eaf/reference/igd.html"""
    if p <= 0:
        raise ValueError(f"'p' must be larger than zero")

    data, ref, maximise = _unary_refset_common(data, ref, maximise)
    data_p = ffi.cast("double *", ffi.from_buffer(data))
    nobj = ffi.cast("int", data.shape[1])
    npoints = ffi.cast("int", data.shape[0])
    ref_p = ffi.cast("double *", ffi.from_buffer(ref))
    ref_size = ffi.cast("int", ref.shape[0])
    maximise_p = ffi.cast("int *", ffi.from_buffer(maximise))
    p = ffi.cast("unsigned int", p)
    return lib.avg_Hausdorff_dist_C(
        data_p, nobj, npoints, ref_p, ref_size, maximise_p, p
    )


def hv(data, ref):
    """
    Calculates hypervolume of reference + dataset
    the reference must be a 1-d numpy array with the same
    Number of objectives as the dataset.
    """
    # Convert to numpy.array in case the user provides a list.  We use
    # np.asfarray to convert it to floating-point, otherwise if a user inputs
    # something like ref = np.array([10, 10]) then numpy would interpret it as
    # an int array.
    data = np.asfarray(data)
    ref = np.asfarray(ref)

    if data.shape[1] != ref.shape[0]:
        raise ValueError(
            f"data and ref need to have the same number of objectives ({data.shape[1]} != {ref.shape[0]})"
        )

    ref_buf = ffi.cast("double *", ffi.from_buffer(ref))
    data_p = ffi.cast("double *", ffi.from_buffer(data))
    data_points = ffi.cast("int", data.shape[0])
    data_objs = ffi.cast("int", data.shape[1])
    hv = lib.fpli_hv(data_p, data_objs, data_points, ref_buf)
    return hv


def is_nondominated(data, maximise=False, keep_weakly=False):
    """TODO: https://mlopez-ibanez.github.io/eaf/reference/nondominated.html"""
    data = np.asfarray(data)
    nobj = data.shape[1]
    maximise = _parse_maximise(maximise, nobj)

    data_p = ffi.cast("double *", ffi.from_buffer(data))
    nobj = ffi.cast("int", nobj)
    npoints = ffi.cast("int", data.shape[0])
    maximise_p = ffi.cast("int *", ffi.from_buffer(maximise))
    keep_weakly = ffi.cast("bool", bool(keep_weakly))
    nondom = lib.is_nondominated_(data_p, nobj, npoints, maximise_p, keep_weakly)
    nondom = ffi.buffer(nondom, data.shape[0])
    return np.frombuffer(nondom, dtype=bool)
