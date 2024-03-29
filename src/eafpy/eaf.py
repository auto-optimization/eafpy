import os
import numpy as np

## Libeaf contains wrapper functions for the EAF C library.
## The CFFI library is used to create C binding
from eafpy.c_bindings import lib, ffi
from ._utils import *
import lzma
import shutil
import tempfile
import random


class ReadDatasetsError(Exception):
    """Custom exception class for an error returned by the read_datasets function

    Parameters
    ----------
    error_code : int
        Error code returned by read_datasets C function, which maps to a string from
    """

    _error_strings = [
        "NO_ERROR",
        "READ_INPUT_FILE_EMPTY",
        "READ_INPUT_WRONG_INITIAL_DIM",
        "ERROR_FOPEN",
        "ERROR_CONVERSION",
        "ERROR_COLUMNS",
    ]

    def __init__(self, error_code):
        self.error = error_code
        self.message = self._error_strings[abs(error_code)]
        super().__init__(self.message)


def read_datasets(filename):
    """Reads an input dataset file, parsing the file and returning a numpy array

    Parameters
    ----------
    filename : str
        Filename of the dataset file. Each row of the table appears as one line of the file. Datasets are separated by an empty line.
        If it does not contain an absolute path, the file name is relative to the current working directory.
        If the filename has extension `'.xz'`, it is decompressed to a temporary file before reading it.

    Returns
    -------
    numpy.ndarray
        An array containing a representation of the data in the file.
        The first n-1 columns contain the numerical data for each of the objectives.
        The last column contains an identifier for which set the data is relevant to.

    Examples
    --------
    >>> eaf.read_datasets("./doc/examples/input1.dat") # doctest: +ELLIPSIS
    array([[ 8.07559653,  2.40702554,  1.        ],
           [ 8.66094446,  3.64050144,  1.        ],
           [ 0.20816431,  4.62275469,  1.        ],
           ...
           [ 4.92599726,  2.70492519, 10.        ],
           [ 1.22234394,  5.68950311, 10.        ],
           [ 7.99466959,  2.81122537, 10.        ],
           [ 2.12700289,  2.43114174, 10.        ]])

    The numpy array represents this data:

    +-------------+-------------+------------+
    | Objective 1 | Objective 2 | Set Number |
    +-------------+-------------+------------+
    | 8.07559653  | 2.40702554  | 1.0        |
    +-------------+-------------+------------+
    | 8.66094446  | 3.64050144  | 1.0        |
    +-------------+-------------+------------+
    | etc.        | etc.        | etc.       |
    +-------------+-------------+------------+
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
    return np.frombuffer(data_buf).reshape((-1, ncols_p[0]))


def _parse_maximise(maximise, nobj):
    # Converts maximise array or single bool to ndarray format
    return atleast_1d_of_length_n(maximise, nobj).astype(bool)


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
    """Inverted Generational Distance (IGD and IGD+) and Averaged Hausdorff Distance.

    Functions to compute the inverted generational distance (IGD and IGD+) and the
    averaged Hausdorff distance between nondominated sets of points.

    See the full documentation here: https://mlopez-ibanez.github.io/eaf/reference/igd.html

    Parameters
    ----------
    data : numpy.ndarray
        Numpy array of numerical values, where each row gives the coordinates of a point in objective space.
        If the array is created from the :func:`read_datasets` function, remove the last (set) column.

    ref : numpy.ndarray or list
        Reference point set as a numpy array or list. Must have same number of columns as the dataset.

    maximise : bool or or list of bool
        Whether the objectives must be maximised instead of minimised.
        Either a single boolean value that applies to all objectives or a list of booleans, with one value per objective.
        Also accepts a 1d numpy array with value 0/1 for each objective.

    p : float, default 1
        Hausdorff distance parameter. Must be larger than 0.

    Returns
    -------
    float
        A single numerical value

    Examples
    --------
    >>> dat =  np.array([[3.5,5.5], [3.6,4.1], [4.1,3.2], [5.5,1.5]])
    >>> ref = np.array([[1, 6], [2,5], [3,4], [4,3], [5,2], [6,1]])
    >>> eaf.igd(dat, ref = ref)
    1.0627908666722465

    >>> eaf.igd_plus(dat, ref = ref)
    0.9855036468106652

    >>> eaf.avg_hausdorff_dist(dat, ref)
    1.0627908666722465

    """
    data, ref, maximise = _unary_refset_common(data, ref, maximise)
    data_p, npoints, nobj = np2d_to_double_array(data)
    ref_p, ref_size = np1d_to_double_array(ref)
    maximise_p = ffi.from_buffer("bool []", maximise)
    return lib.igd_C(data_p, nobj, npoints, ref_p, ref_size, maximise_p)


def igd_plus(data, ref, maximise=False):
    """Calculate IGD+ indicator

    See :func:`igd`
    """
    data, ref, maximise = _unary_refset_common(data, ref, maximise)
    data_p, npoints, nobj = np2d_to_double_array(data)
    ref_p, ref_size = np1d_to_double_array(ref)
    maximise_p = ffi.from_buffer("bool []", maximise)
    return lib.igd_plus_C(data_p, nobj, npoints, ref_p, ref_size, maximise_p)


def avg_hausdorff_dist(data, ref, maximise=False, p=1):
    """Calculate average Hausdorff distance

    See :func:`igd`
    """
    if p <= 0:
        raise ValueError(f"'p' must be larger than zero")

    data, ref, maximise = _unary_refset_common(data, ref, maximise)
    data_p, npoints, nobj = np2d_to_double_array(data)
    ref_p, ref_size = np1d_to_double_array(ref)
    maximise_p = ffi.from_buffer("bool []", maximise)
    p = ffi.cast("unsigned int", p)
    return lib.avg_Hausdorff_dist_C(
        data_p, nobj, npoints, ref_p, ref_size, maximise_p, p
    )


def hypervolume(data, ref):
    """Hypervolume indicator

    Computes the hypervolume metric with respect to a given reference point assuming minimization of all objectives.

    Parameters
    ----------
    data : numpy.ndarray
        Numpy array of numerical values, where each row gives the coordinates of a point in objective space.
        If the array is created from the `read_datasets()` function, remove the last column
    ref : numpy array or list
        Reference point set as a numpy array or list. Must be same length as a single point in the \
        dataset

    Returns
    -------
    float
        A single numerical value, the hypervolume indicator

    Examples
    --------
    >>> dat = np.array([[5,5],[4,6],[2,7], [7,4]])
    >>> eaf.hypervolume(dat, ref = [10, 10])
    38.0

    Select Set 1 of dataset, and remove set number column
    >>> dat = eaf.read_datasets("./doc/examples/input1.dat")
    >>> set1 = dat[dat[:,2]==1, :2]
    
    This set contains dominated points so remove them
    >>> set1 = eaf.filter_dominated(set1)
    >>> eaf.hypervolume(set1, ref= [10, 10])
    90.46272764755885

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

    ref_buf = ffi.from_buffer("double []", ref)
    data_p, npoints, nobj = np2d_to_double_array(data)
    hv = lib.fpli_hv(data_p, nobj, npoints, ref_buf)
    return hv


def is_nondominated(data, maximise=False, keep_weakly=False):
    """Identify, and remove dominated points according to Pareto optimality.

    Parameters
    ----------
    data : numpy array
        Numpy array of numerical values, where each row gives the coordinates of a point in objective space.
        If the array is created from the `read_datasets()` function, remove the last column.
    maximise : single bool, or list of booleans
        Whether the objectives must be maximised instead of minimised. \
        Either a single boolean value that applies to all objectives or a list of boolean values, with one value per objective. \
        Also accepts a 1d numpy array with value 0/1 for each objective
    keep_weakly: bool
        If FALSE, return FALSE for any duplicates of nondominated points

    Returns
    -------
    bool array
        `is_nondominated` returns a boolean list of the same length as the number of rows of data,\
        where TRUE means that the point is not dominated by any other point.

        `filter_dominated` returns a numpy array with only mutually nondominated points.

        
    Examples
    --------
    >>> S = np.array([[1,1], [0,1], [1,0], [1,0]])
    >>> eaf.is_nondominated(S)
    array([False,  True, False,  True])

    >>> eaf.is_nondominated(S, maximise = True)
    array([ True, False, False, False])

    >>> eaf.filter_dominated(S)
    array([[0, 1],
           [1, 0]])

    >>> eaf.filter_dominated(S, keep_weakly = True)
    array([[0, 1],
           [1, 0],
           [1, 0]])
    """
    data = np.asfarray(data)
    nobj = data.shape[1]
    maximise = _parse_maximise(maximise, nobj)
    data_p, npoints, nobj = np2d_to_double_array(data)
    maximise_p = ffi.from_buffer("bool []", maximise)
    keep_weakly = ffi.cast("bool", bool(keep_weakly))
    nondom = lib.is_nondominated_(data_p, nobj, npoints, maximise_p, keep_weakly)
    nondom = ffi.buffer(nondom, data.shape[0])
    return np.frombuffer(nondom, dtype=bool)


def filter_dominated(data, maximise=False, keep_weakly=False):
    """Remove dominated points according to Pareto optimality.
    See: :func:`is_nondominated` for details
    """
    return data[is_nondominated(data, maximise, keep_weakly)]


def filter_dominated_sets(dataset, maximise=False, keep_weakly=False):
    """Filter dominated sets for multiple sets

    Executes the :func:`filter_dominated` function for every set in a dataset \
    and returns back a dataset, preserving set 

    Examples
    --------
    >>> dataset = eaf.read_datasets("./doc/examples/input1.dat")
    >>> subset = eaf.subset(dataset, range = [3,5])
    >>> eaf.filter_dominated_sets(subset)
    array([[2.60764118, 6.31309852, 3.        ],
           [3.22509709, 6.1522834 , 3.        ],
           [0.37731545, 9.02211752, 3.        ],
           [4.61023932, 2.29231998, 3.        ],
           [0.2901393 , 8.32259412, 4.        ],
           [1.54506255, 0.38303122, 4.        ],
           [4.43498452, 4.13150648, 5.        ],
           [9.78758589, 1.41238277, 5.        ],
           [7.85344142, 3.02219054, 5.        ],
           [0.9017068 , 7.49376946, 5.        ],
           [0.17470556, 8.89066343, 5.        ]])

    The above returns sets 3,4,5 with dominated points within each set removed.

    See Also
    --------
    This function for data without set numbers - :func:`filter_dominated` 
    """
    # FIXME: it will be faster to stack filter_set, then do:
    # dataset[filter_set, :]
    # to filter in one go.
    new_sets = []
    for set in np.unique(dataset[:, -1]):
        set_data = dataset[dataset[:, -1] == set, :-1]
        filter_set = filter_dominated(set_data, maximise, keep_weakly)
        set_nums = np.full(filter_set.shape[0], set).reshape(-1, 1)
        new_set = np.hstack((filter_set, set_nums))
        new_sets.append(new_set)
    return np.vstack(new_sets)


def _epsilon_select(data, ref, maximise, is_add):
    data, ref, maximise = _unary_refset_common(data, ref, maximise)
    data_p, npoints, nobj = np2d_to_double_array(data)
    ref_p, ref_size = np1d_to_double_array(ref)
    maximise_p = ffi.from_buffer("bool []", maximise)
    is_add = ffi.cast("bool", is_add)  # Select between add multiply
    return lib.epsilon_(data_p, nobj, npoints, ref_p, ref_size, maximise_p, is_add)


def epsilon_additive(data, ref, maximise=False):
    """Computes the epsilon metric, either additive or multiplicative. 

    `data` and `reference` must all be larger than 0 for `epsilon_mult`.

    Parameters
    ----------
    data : numpy.ndarray
        Numpy array of numerical values, where each row gives the coordinates of a point in objective space.
        If the array is created from the :func:`read_datasets` function, remove the last (set) column
    ref : numpy.ndarray or list
        Reference point set as a numpy array or list. Must have same number of columns as a single point in the \
        dataset
    maximise : bool or list of bool
        Whether the objectives must be maximised instead of minimised. \
        Either a single boolean value that applies to all objectives or a list of booleans, with one value per objective. \
        Also accepts a 1d numpy array with value 0/1 for each objective

    Returns
    -------
    float
        A single numerical value  

    Examples
    --------
    >>> dat = np.array([[3.5,5.5], [3.6,4.1], [4.1,3.2], [5.5,1.5]])
    >>> ref = np.array([[1, 6], [2,5], [3,4], [4,3], [5,2], [6,1]])
    >>> eaf.epsilon_additive(dat, ref = ref)
    2.5

    >>> eaf.epsilon_mult(dat, ref = ref)
    3.5
    """
    return _epsilon_select(data, ref, maximise=maximise, is_add=True)


def epsilon_mult(data, ref, maximise=False):
    """multiplicative epsilon metric

    See :func:`epsilon_additive`

    """
    return _epsilon_select(data, ref, maximise=maximise, is_add=False)


def normalise(data, to_range=[0.0, 1.0], lower=np.nan, upper=np.nan, maximise=False):
    """Normalise points per coordinate to a range, e.g., `to_range = [1,2]`, where the minimum value will correspond to 1 and the maximum to 2.

    Parameters
    ----------
    data : numpy.ndarray
        Numpy array of numerical values, where each row gives the coordinates of a point in objective space.
        See :func:`normalise_sets` to normalise data that includes set numbers (Multiple sets)

    to_range : numpy array or list of 2 points
        Normalise values to this range. If the objective is maximised, it is normalised to `(to_range[1], to_range[0])` instead.

    upper, lower: list or np array
        Bounds on the values. If `np.nan`, the maximum and minimum values of each coordinate are used.
        
    maximise : single bool, or list of booleans
        Whether the objectives must be maximised instead of minimised. \
        Either a single boolean value that applies to all objectives or a list of booleans, with one value per objective. \
        Also accepts a 1D numpy array with values 0 or 1 for each objective

    Returns
    -------
    numpy array
        Returns the data normalised as requested.

    Examples
    --------
    >>> dat = np.array([[3.5,5.5], [3.6,4.1], [4.1,3.2], [5.5,1.5]])
    >>> eaf.normalise(dat)
    array([[0.   , 1.   ],
           [0.05 , 0.65 ],
           [0.3  , 0.425],
           [1.   , 0.   ]])

    >>> eaf.normalise(dat, to_range = [1,2], lower = [3.5, 3.5], upper = 5.5)
    array([[1.  , 2.  ],
           [1.05, 1.3 ],
           [1.3 , 0.85],
           [2.  , 0.  ]])

    See Also
    --------
    This function for muliple sets - :func:`normalise_sets` 

    """
    # Normalise modifies the data, so we need to create a copy.
    data = np.asfarray(data).copy()
    npoints, nobj = data.shape
    if nobj == 1:
        raise ValueError("'data' must have at least two columns")
    to_range = np.asfarray(to_range)
    if to_range.shape[0] != 2:
        raise ValueError("'to_range' must have length 2")
    lower = atleast_1d_of_length_n(lower, nobj).astype(float)
    upper = atleast_1d_of_length_n(upper, nobj).astype(float)
    if np.any(np.isnan(lower)):
        lower = np.where(np.isnan(lower), data.min(axis=0), lower)
    if np.any(np.isnan(upper)):
        upper = np.where(np.isnan(upper), data.max(axis=0), upper)

    maximise = _parse_maximise(maximise, data.shape[1])
    data_p, npoints, nobj = np2d_to_double_array(data)
    maximise_p = ffi.from_buffer("bool []", maximise)
    lbound_p = ffi.from_buffer("double []", lower)
    ubound_p = ffi.from_buffer("double []", upper)
    lib.normalise_(
        data_p, nobj, npoints, maximise_p, to_range[0], to_range[1], lbound_p, ubound_p
    )
    data_buf = ffi.buffer(data_p, ffi.sizeof("double") * data.shape[0] * data.shape[1])
    data = np.frombuffer(data_buf).reshape(data.shape)
    return data


def normalise_sets(dataset, range=[0, 1], lower="na", upper="na", maximise=False):
    """Normalise dataset with multiple sets

    Executes the :func:`normalise` function for every set in a dataset (Performs normalise on every set seperately)

    Examples
    --------
    >>> dataset = eaf.read_datasets("./doc/examples/input1.dat")
    >>> subset = eaf.subset(dataset, range = [4,5])
    >>> eaf.normalise_sets(subset)
    array([[1.        , 0.38191742, 4.        ],
           [0.70069111, 0.5114669 , 4.        ],
           [0.12957487, 0.29411141, 4.        ],
           [0.28059067, 0.53580626, 4.        ],
           [0.32210885, 0.21797067, 4.        ],
           [0.39161668, 0.92106178, 4.        ],
           [0.        , 1.        , 4.        ],
           [0.62293227, 0.11315216, 4.        ],
           [0.76936124, 0.58159784, 4.        ],
           [0.12957384, 0.        , 4.        ],
           [0.82581672, 0.66566917, 5.        ],
           [0.44318444, 0.35888982, 5.        ],
           [0.80036477, 0.23242446, 5.        ],
           [0.88550836, 0.51482968, 5.        ],
           [0.89293026, 1.        , 5.        ],
           [1.        , 0.        , 5.        ],
           [0.79879657, 0.21247419, 5.        ],
           [0.07562783, 0.80266586, 5.        ],
           [0.        , 0.98703813, 5.        ],
           [0.6229605 , 0.8613516 , 5.        ]])

    See Also
    --------
    This function for data without set numbers - :func:`normalise`
    """
    for set in np.unique(dataset[:, -1]):
        setdata = dataset[dataset[:, -1] == set, :-1]
        dataset[dataset[:, -1] == set, :-1] = normalise(
            setdata, to_range=range, lower=np.nan, upper=np.nan, maximise=False
        )
    return dataset


def subset(dataset, set=-2, range=[]):
    """Subset is a convenience function for extracting a set or range of sets from a larger dataset. 
    It takes a dataset with multiple set numbers, and returns 1 or more sets (with their set numbers)
    
    Use the :func:`data_subset` to choose a single set and use set numbers.
    

    Parameters
    ----------
    dataset : numpy array
        Numpy array of numerical values and set numbers, containing multiple sets. For example the output \
         of the :func:`read_datasets` function
    set : integer
        Select a single set from the dataset, where the selected set is equal to this argument

    range: list (length 2)
        Select sets from the dataset with an inequality. range[0] <= Set_num <= Range[1] 
        
    Returns
    -------
    numpy array
        returns back a numpy array with the same columns as the input, with certain datasets selected

    Examples
    --------
    >>> dataset = read_datasets("./doc/examples/input1.dat")
    >>> subset(dataset, set = 1)
    array([[8.07559653, 2.40702554, 1.        ],
           [8.66094446, 3.64050144, 1.        ],
           [0.20816431, 4.62275469, 1.        ],
           [4.8814328 , 9.09473137, 1.        ],
           [0.22997367, 1.11772205, 1.        ],
           [1.51643636, 3.07933731, 1.        ],
           [6.08152841, 4.58743853, 1.        ],
           [2.3530968 , 0.79055172, 1.        ],
           [8.7475454 , 1.71575862, 1.        ],
           [0.58799475, 0.73891181, 1.        ]])
    >>> subset(dataset, range =[4, 6])
    array([[9.9751443 , 3.41528862, 4.        ],
           [7.07633622, 4.44385483, 4.        ],
           [1.54507257, 2.71814725, 4.        ],
           [3.00766139, 4.63709876, 4.        ],
           [3.40976512, 2.1136231 , 4.        ],
           [4.08294878, 7.69585918, 4.        ],
           [0.2901393 , 8.32259412, 4.        ],
           [6.32324143, 1.28140989, 4.        ],
           [7.74140672, 5.00066389, 4.        ],
           [1.54506255, 0.38303122, 4.        ],
           [8.11318284, 6.45581597, 5.        ],
           [4.43498452, 4.13150648, 5.        ],
           [7.86851636, 3.17334347, 5.        ],
           [8.68699143, 5.3129827 , 5.        ],
           [8.75833731, 8.98886885, 5.        ],
           [9.78758589, 1.41238277, 5.        ],
           [7.85344142, 3.02219054, 5.        ],
           [0.9017068 , 7.49376946, 5.        ],
           [0.17470556, 8.89066343, 5.        ],
           [6.1631503 , 7.93840121, 5.        ],
           [4.10476852, 9.67891782, 6.        ],
           [8.57911868, 0.35169752, 6.        ],
           [4.96525837, 1.94353305, 6.        ],
           [8.17231096, 9.76977853, 6.        ],
           [6.78498493, 0.56380796, 6.        ],
           [2.71891214, 6.94327481, 6.        ],
           [3.4186965 , 9.38437467, 6.        ],
           [6.45431955, 4.06044388, 6.        ],
           [1.13096306, 9.72645436, 6.        ],
           [8.34008115, 5.70698919, 6.        ]])

    See Also
    --------
    :func:`data_subset`

    """
    if (not range and set == -2) or (range and set != -2):
        raise ValueError("Enter a range or set")
    elif set != -2:
        return np.ascontiguousarray(dataset[dataset[:, -1] == set])
    elif range:
        if len(range) != 2:
            raise ValueError("Range must be a list with an inequality")
        setnames = dataset[:, -1]
        return np.ascontiguousarray(
            dataset[(setnames >= range[0]) & (setnames <= range[1])]
        )
    else:
        raise NotImplementedError()


def data_subset(dataset, set):
    """Select data points from a specific dataset. Returns a single set, without the set number column

    This can be used to parse data for inputting to functions such as :func:`igd` and :func:`hypervolume`. 
    
    Similar to the :func:`subset` function, but can only return 1 set and removes the last column (set number)

    Parameters
    ----------
    dataset : numpy array
        Numpy array of numerical values and set numbers, containing multiple sets. For example the output \
         of the :func:`read_datasets` function
    Set : integer
        Select a single set from the dataset, where the selected set is equal to this argument

    Returns
    -------
    numpy array
        returns back a single set with only the objective data. (set numbers are excluded)

    Examples
    --------
    >>> dataset = eaf.read_datasets("./doc/examples/input1.dat")
    >>> data1 = eaf.data_subset(dataset, set = 1)
    
    The above selects dataset 1 and removes the set number so it can be used as an input to functions such as :func:`hypervolume`
    >>> eaf.hypervolume(data1, [10, 10])
    90.46272764755885

    See Also
    --------
    :func:`subset`

    """
    return np.ascontiguousarray(subset(dataset, set, range=[])[:, :-1])


def get_eaf(data, percentiles=[], debug=False):
    """Empiracal attainment function (EAF) calculation
    
    Calculate EAF in 2d or 3d from the input dataset

    Parameters
    ----------
    dataset : numpy array
        Numpy array of numerical values and set numbers, containing multiple sets. For example the output \
         of the :func:`read_datasets` function
    percentiles : list
        A list of percentiles to calculate. If empty, all possible percentiles are calculated. Note the maximum 
    debug : bool
        (For developers) print out debugging information in the C code

    Returns
    -------
    numpy array
        Returns a numpy array containing the EAF data points, with the same number of columns as the input argument, \
        but a different number of rows. The last column represents the EAF percentile for that data point

    Examples
    --------
    >>> dataset = eaf.read_datasets("./doc/examples/input1.dat")
    >>> subset = eaf.subset(dataset, range = [7,10])
    >>> eaf.get_eaf(subset)
    array([[  0.62230271,   3.56945324,  25.        ],
           [  0.86723965,   1.58599089,  25.        ],
           [  6.43135537,   1.00153569,  25.        ],
           [  9.7398055 ,   0.36688707,  25.        ],
           [  0.6510164 ,   9.42381213,  50.        ],
           [  0.79293574,   6.46605414,  50.        ],
           [  1.30291449,   4.50417698,  50.        ],
           [  1.58498886,   2.87955367,  50.        ],
           [  7.04694467,   1.83484358,  50.        ],
           [  9.7398055 ,   1.00153569,  50.        ],
           [  0.99008784,   8.84691923,  75.        ],
           [  1.06855707,   6.7102429 ,  75.        ],
           [  3.34035397,   2.89377444,  75.        ],
           [  9.30137043,   2.14328532,  75.        ],
           [  9.7398055 ,   1.83484358,  75.        ],
           [  9.94332713,   1.50186503,  75.        ],
           [  1.06855707,   8.84691923, 100.        ],
           [  3.34035397,   6.7102429 , 100.        ],
           [  4.93663823,   6.20957074, 100.        ],
           [  7.92511295,   3.92669598, 100.        ]])

    """
    data = np.asfarray(data)
    num_data_columns = data.shape[1]
    if num_data_columns != 3:
        assert NotImplementedError(
            "Only 2d Datasets are currently supported for calculating eaf"
        )

    percentiles = np.asfarray(percentiles)
    # Get C pointers + matrix size for calling CFFI generated extension module
    data_p, npoints, ncols = np2d_to_double_array(data)

    # If percentiles array is empty, calculate all the levels in C code from the data
    # Else use the percentiles argument to calculate the levels
    choose_percentiles = True if len(percentiles) != 0 else False
    choose_percentiles = ffi.cast("bool", choose_percentiles)

    percentile_p, npercentiles = np1d_to_double_array(percentiles)
    eaf_npoints = ffi.new("int *", 0)
    sizeof_eaf = ffi.new("int *", 0)
    nsets = ffi.cast("int", len(np.unique(data[:, -1])))  # Get nu,m of sets from data
    debug = ffi.cast("bool", debug)
    eaf_data = lib.get_eaf_(
        data_p,
        ncols,
        npoints,
        percentile_p,
        npercentiles,
        choose_percentiles,
        nsets,
        eaf_npoints,
        sizeof_eaf,
        debug,
    )

    eaf_buf = ffi.buffer(eaf_data, sizeof_eaf[0])
    eaf_arr = np.frombuffer(eaf_buf)
    return np.reshape(eaf_arr, (-1, num_data_columns))


def get_diff_eaf(x, y, intervals=None, debug=False):
    x = np.asfarray(x)
    y = np.asfarray(y)

    if np.min(x[:, -1]) != 1 or np.min(y[:, -1]) != 1:
        raise ValueError("x and y should contain set numbers starting from 1")
    ycopy = np.copy(
        y
    )  # Do hard copy so that the matrix is not corrupted. This could be optimised
    ycopy[:, -1] = ycopy[:, -1] + np.max(
        x[:, -1]
    )  # Make Y sets start from end of X sets

    data = np.vstack((x, ycopy))  # Combine X and Y datasets to one matrix
    nsets = len(np.unique(data[:, -1]))
    if intervals is None:
        intervals = nsets / 2.0
    else:
        intervals = min(intervals, nsets / 2.0)
    intervals = int(intervals)

    data = np.ascontiguousarray(
        np.asfarray(data)
    )  # C function requires contiguous data
    num_data_columns = data.shape[1]
    data_p, npoints, ncols = np2d_to_double_array(data)
    eaf_npoints = ffi.new("int *", 0)
    sizeof_eaf = ffi.new("int *", 0)
    nsets = ffi.cast("int", nsets)  # Get num of sets from data
    intervals = ffi.cast("int", intervals)
    debug = ffi.cast("bool", debug)
    eaf_diff_data = lib.compute_eafdiff_(
        data_p, ncols, npoints, nsets, intervals, eaf_npoints, sizeof_eaf, debug
    )

    eaf_buf = ffi.buffer(eaf_diff_data, sizeof_eaf[0])
    eaf_arr = np.frombuffer(eaf_buf)
    # The C code gets diff EAF in Column Major order so I return it in column major order than transpose to fix into row major order
    return np.reshape(eaf_arr, (num_data_columns, -1)).T


def rand_non_dominated_sets(num_points, num_sets=10, shape=3, scale=1):
    """Create randomised non-dominated sets

    Create a dataset of random non-dominated sets following a gamma distribution. This is slow \
    for higher number of points (> 100)
    
    Parameters
    ----------
    num_points : integer
        Number of points in the resulting dataset
    num_sets : integer
        Number of datapoints per set. There should be an equal number of points per set so \
        num_points % num_sets should = 0
    shape, scale : float
        Shape and Scale parameters for the gamma distribution
    Returns
    -------
    np.ndarray (n, 3)
        An (n, 3) numpy array containing non dominated points and set numbers. The last column represents the set numbers
    """
    if num_points % num_sets != 0:
        raise ValueError("Number of points should be divisible by number of sets")

    points = []
    while len(points) < num_points:
        x = np.random.gamma(shape, scale)
        y = np.random.gamma(shape, scale)
        point = (x, y)
        dominated = False
        for p in points:
            if (
                p[0] <= point[0]
                and p[1] <= point[1]
                and (p[0] < point[0] or p[1] < point[1])
            ):
                dominated = True
                break
        if not dominated:
            points.append(point)
    points = np.array(points)
    set_nums = np.arange(0, num_points) // num_sets + 1
    return np.column_stack((points, set_nums))
