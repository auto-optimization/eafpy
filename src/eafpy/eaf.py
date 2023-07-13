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
    """Identify, and remove dominated points according to Pareto optimality.
    Reads an input dataset file, parsing the file and returning a numpy array

    Parameters
    ----------
    filename : string
        Filename of the dataset file. Each row of the table appears as one line of the file.
        If it does not contain an absolute path, the file name is relative to the current working directory.
        If the filename has extension '.xz', it is decompressed to a temporary file before reading it.

    Returns
    -------
    numpy array
        An array containing a representation of the data in the file.
        The first n-1 columns contain the numerical data for each of the objectives
        The last column contains an identifier for which set the data is relevant to.

    Examples
    --------
    >>> eaf.read_dataset("input1.dat")
    np.array([
       [ 8.07559653,  2.40702554,  1.   ],
       [ 8.66094446,  3.64050144,  1.   ],
       [ 0.20816431,  4.62275469,  1.   ],
       [ 4.8814328 ,  9.09473137,  1.   ], ...
    ])

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
    return np.ascontiguousarray(maximise).astype(bool)


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
    """Inverted Generational Distance (IGD and IGD+) and Averaged Hausdorff Distance
    Functions to compute the inverted generational distance (IGD and IGD+) and the \
    averaged Hausdorff distance between nondominated sets of points.

    ::
    
        igd(data, reference, maximise = FALSE)

        igd_plus(data, reference, maximise = FALSE)

        avg_hausdorff_dist(data, ref, maximise = FALSE, p = 1L)
    

    Parameters
    ----------
    data : numpy array
        Numpy array of numerical values, where each row gives the coordinates of a point in objective space.
        If the array is created from the :func:`read_datasets` function, remove the last (set) column
    ref : numpy array or list
        Reference point set as a numpy array or list. Must have same number of columns as a single point in the \
        dataset
    maximise : single bool, or list of booleans
        Whether the objectives must be maximised instead of minimised. \
        Either a single boolean value that applies to all objectives or a list of booleans, with one value per objective. \
        Also accepts a 1d numpy array with value 0/1 for each objective
    P : Hausdorff distance parameter (default: 1L).

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
    data_p = ffi.from_buffer("double []", data)
    nobj = ffi.cast("int", data.shape[1])
    npoints = ffi.cast("int", data.shape[0])
    ref_p = ffi.from_buffer("double []", ref)
    ref_size = ffi.cast("int", ref.shape[0])
    maximise_p = ffi.from_buffer("bool []", maximise)
    return lib.igd_C(data_p, nobj, npoints, ref_p, ref_size, maximise_p)


def igd_plus(data, ref, maximise=False):
    """Calculate igd+ indicator

    See :func:`igd`
    """
    data, ref, maximise = _unary_refset_common(data, ref, maximise)
    data_p = ffi.from_buffer("double []", data)
    nobj = ffi.cast("int", data.shape[1])
    npoints = ffi.cast("int", data.shape[0])
    ref_p = ffi.from_buffer("double []", ref)
    ref_size = ffi.cast("int", ref.shape[0])
    maximise_p = ffi.from_buffer("bool []", maximise)
    return lib.igd_plus_C(data_p, nobj, npoints, ref_p, ref_size, maximise_p)


def avg_hausdorff_dist(data, ref, maximise=False, p=1):
    """Calculate average Hausdorff distance

    See :func:`igd`
    """
    if p <= 0:
        raise ValueError(f"'p' must be larger than zero")

    data, ref, maximise = _unary_refset_common(data, ref, maximise)
    data_p = ffi.from_buffer("double []", data)
    nobj = ffi.cast("int", data.shape[1])
    npoints = ffi.cast("int", data.shape[0])
    ref_p = ffi.from_buffer("double []", ref)
    ref_size = ffi.cast("int", ref.shape[0])
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
    data : numpy array
        Numpy array of numerical values, where each row gives the coordinates of a point in objective space.
        If the array is created from the `read_dataset()` function, remove the last column
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

    >>> dat = read_datasets("input1.dat")
     # Select Set 1 of dataset, and remove set number column
    >>> set1 = dat[dat[:,2]==1, :2]
     # This set contains dominated points so remove them
    >>> set1 = eaf.filter_dominiated(set1)
    >>> hv = eaf.hypervolume(set1, ref= [10, 10])
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
    data_p = ffi.from_buffer("double []", data)
    data_points = ffi.cast("int", data.shape[0])
    data_objs = ffi.cast("int", data.shape[1])
    hv = lib.fpli_hv(data_p, data_objs, data_points, ref_buf)
    return hv


def is_nondominated(data, maximise=False, keep_weakly=False):
    """Identify, and remove dominated points according to Pareto optimality.

    Parameters
    ----------
    data : numpy array
        Numpy array of numerical values, where each row gives the coordinates of a point in objective space.
        If the array is created from the `read_dataset()` function, remove the last column.
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
    **nondominated** examples
        >>> S = np.array([[1,1], [0,1], [1,0], [1,0]])
        >>> eaf.is_nondominated(S)
        [False, True, false, True]

        >>> eaf.is_nondominated(S, maximise = True)
        [True, False, False, False]

        >>> eaf.filter_dominated(S)
        np.array([0,1], [1,0])

        >>> eaf.filter_dominated(S, keep_weakly = True)
        np.array([0,1], [1,0], [1,0])
    """
    data = np.asfarray(data)
    nobj = data.shape[1]
    maximise = _parse_maximise(maximise, nobj)

    data_p = ffi.from_buffer("double []", data)
    nobj = ffi.cast("int", nobj)
    npoints = ffi.cast("int", data.shape[0])
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
    >>> dataset = eaf.read_datasets("input1")
    >>> subset = eaf.subset(dataset, range = [3,5])
    >>> normal_sets = eaf.filter_dominated_sets(subset)
    np.array([[...]]) # Returns sets 3,4,5 with dominated points within each set removed

    See Also
    --------
    This function for data without set numbers - :func:`filter_dominated` 
    """
    new_sets = []
    for set in np.unique(dataset[:, -1]):
        set_data = dataset[dataset[:, -1] == set, :-1]
        filter_set = filter_dominated(set_data, maximise, keep_weakly)
        set_nums = np.full(filter_set.shape[0], set).reshape(-1, 1)
        new_set = np.hstack((filter_set, set_nums))
        new_sets.append(new_set)
    return np.vstack(new_sets)


def _epilison_select(data, ref, maximise=False, add_or_mult="add"):
    # epsilon_ selects either episilon additive or multiplicative based on char is_add
    if add_or_mult == "add":
        epilson_type = 0
    elif add_or_mult == "mult":
        epilson_type = 1
    else:
        raise ValueError("Enter add or mult")

    data, ref, maximise = _unary_refset_common(data, ref, maximise)
    data_p = ffi.from_buffer("double []", data)
    nobj = ffi.cast("int", data.shape[1])
    npoints = ffi.cast("int", data.shape[0])
    ref_p = ffi.from_buffer("double []", ref)
    ref_size = ffi.cast("int", ref.shape[0])
    maximise_p = ffi.from_buffer("bool []", maximise)
    is_add = ffi.cast("char", epilson_type)  # Select between add multiply
    return lib.epsilon_(data_p, nobj, npoints, ref_p, ref_size, maximise_p, is_add)


def epsilon_additive(data, ref, maximise=False):
    """Epsilon metric
    Computes the epsilon metric, either additive or multiplicative.


    ::
    
        epsilon_additive(data, reference, maximise = FALSE)

        epsilon_mult(data, reference, maximise = FALSE)
        # Data and reference must all be > 0 for epsilon_mult


    Parameters
    ----------
    data : numpy array
        Numpy array of numerical values, where each row gives the coordinates of a point in objective space.
        If the array is created from the :func:`read_datasets` function, remove the last (set) column
    ref : numpy array or list
        Reference point set as a numpy array or list. Must have same number of columns as a single point in the \
        dataset
    maximise : single bool, or list of booleans
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
    return _epilison_select(data, ref, maximise=maximise, add_or_mult="add")


def epsilon_mult(data, ref, maximise=False):
    """multiplicative Epsilon metric

    See :func:`epsilon_additive`

    """
    return _epilison_select(data, ref, maximise=maximise, add_or_mult="mult")


def normalise(data, range=[0, 1], lower="na", upper="na", maximise=False):
    """Normalise
    Normalise points per coordinate to a range, e.g., range = [1,2], where the minimum value will correspond to 1 and the maximum to 2.\

    ::
    
        normalise(data, to.range = c(1, 2), lower = NA, upper = NA, maximise = FALSE)

    Parameters
    ----------
    data : numpy array
        A single set : A Numpy array of numerical values, where each row gives the coordinates of a point in objective space.
        See :func:`normalise_sets` to normalise data that includes set numbers (Multiple sets)
    range : numpy array or list of 2 points
        Normalise values to this range. If the objective is maximised, it is normalised to c(to.range[1], to.range[0]) instead.

    upper, lower: list or np array
        Bounds on the values. If NA, the maximum and minimum values of each coordinate are used.
        
    maximise : single bool, or list of booleans
        Whether the objectives must be maximised instead of minimised. \
        Either a single boolean value that applies to all objectives or a list of booleans, with one value per objective. \
        Also accepts a 1d numpy array with value 0/1 for each objective

    Returns
    -------
    numpy array
        Returns normalised data input. **Note this will pass the array by reference, so the original data array **  

    Examples
    --------
    >>> dat = np.array([[3.5,5.5], [3.6,4.1], [4.1,3.2], [5.5,1.5]])
    >>> eaf.normalise(dat)
    np.array([[0.   , 1.   ],
              [0.05 , 0.65 ],
              [0.3  , 0.425],
              [1.   , 0.   ]])

    # TODO add more examples showing different arguments

    See Also
    --------
    This function for muliple sets - :func:`normalise_sets` 

    """
    data = np.asfarray(data)
    objects = data.shape[1]
    points = data.shape[0]
    range = np.asfarray(range)
    if range.shape[0] != 2:
        raise ValueError("Range must be an array like with 2 entries")
    if objects == 1:
        raise ValueError("function only suitable for 2 dimensions or higher")

    if isinstance(lower, str) or isinstance(upper, str):
        # If bounds not set, assume calculate bounds in C code
        # Set values to 0 so the function can still call
        lower = np.zeros(objects, dtype=np.double)
        upper = np.zeros(objects, dtype=np.double)
        use_bound_calc = True
    else:
        use_bound_calc = False
        lower = np.asfarray(lower)
        upper = np.asfarray(upper)
        if lower.shape[0] != objects or upper.shape[0] != objects:
            raise ValueError(
                "upper or lower bound arg has different number of objectives to data"
            )

    maximise = _parse_maximise(maximise, data.shape[1])

    data_p = ffi.from_buffer("double *", data)

    nobj = ffi.cast("int", objects)
    npoints = ffi.cast("int", points)
    maximise_p = ffi.from_buffer("bool []", maximise)
    lbound_p = ffi.from_buffer("double []", lower)
    ubound_p = ffi.from_buffer("double []", upper)
    use_bound_calc = ffi.cast("bool", use_bound_calc)

    lib.normalise_(
        data_p,
        nobj,
        npoints,
        maximise_p,
        range[0],
        range[1],
        lbound_p,
        ubound_p,
        use_bound_calc,
    )

    data_buf = ffi.buffer(data_p, ffi.sizeof("double") * points * objects)
    data_nparray = np.frombuffer(data_buf)

    return data_nparray.reshape(-1, objects)


def normalise_sets(dataset, range=[0, 1], lower="na", upper="na", maximise=False):
    """Normalise dataset with multiple sets

    Executes the :func:`normalise` function for every set in a dataset (Performs normalise on every set seperately)

    Examples
    --------
    >>> dataset = eaf.read_datasets("input1")
    >>> subset = eaf.subset(dataset, range = [3,5])
    >>> normal_sets = eaf.normalise_sets(subset)
    np.array([[...]]) # Returns sets 3,4,5

    See Also
    --------
    This function for data without set numbers - :func:`normalise`
    """
    for set in np.unique(dataset[:, -1]):
        setdata = dataset[dataset[:, -1] == set, :-1]
        dataset[dataset[:, -1] == set, :-1] = normalise(
            setdata, range=[0, 1], lower="na", upper="na", maximise=False
        )
    return dataset


def subset(dataset, set=-2, range=[]):
    """Subset is a convienance function for extracting a set or range of sets from a larger dataset. 
    It takes a dataset with multiple set numbers, and returns 1 or more sets (with their set numbers)
    
    Use the :func:`data_subset` to choose a single set and use set numbers
    

    Parameters
    ----------
    dataset : numpy array
        Numpy array of numerical values and set numbers, containing multiple sets. For example the output \
         of the :func:`read_datasets` function
    Set : integer
        Select a single set from the dataset, where the selected set is equal to this argument

    range: list (length 2)
        Select sets from the dataset with an inequality. range[0] <= Set_num <= Range[1] 
        
    Returns
    -------
    numpy array
        returns back a numpy array with the same columns as the input, with certain datasets selected

    Examples
    --------
    >>> dataset = read_datasets("input1")
    >>> subset = subset(dataset, set = 1)
    np.array([[...]]) # Returns 1 set from dataset, where set number = 1
    

    >>> subset = subset(dataset, range =[4, 7])
    np.array([[...]]) # Return 4 set from dataset, including sets (4,5,6,7) 

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
    >>> dataset = eaf.read_datasets("input1.dat")
    >>> data1 = eaf.data_subset(dataset, set = 1)
    # Select dataset 1 and remove the set number so it can be used for function such as :func:`subset`
    >>> eaf.hypervolume(data1, [10, 10])
    90.46272764755885

    See Also
    --------
    :func:`subset`

    """
    return np.ascontiguousarray(subset(dataset, set, range=[])[:, :-1])
