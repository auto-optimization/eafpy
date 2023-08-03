from .eaf import read_datasets, ReadDatasetsError
from .eaf import (
    hypervolume,
    igd,
    igd_plus,
    avg_hausdorff_dist,
    is_nondominated,
    filter_dominated,
    epsilon_additive,
    epsilon_mult,
    normalise,
    subset,
    data_subset,
    normalise_sets,
    filter_dominated_sets,
    get_eaf,
)
from .plot import plot_datasets, plot_eaf

import importlib.metadata as _metadata

__version__ = _metadata.version(__package__ or __name__)
