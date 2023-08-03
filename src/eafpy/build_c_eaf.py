"""C library compilation config

This script is part of the compilation of the C library using CFFi. 

Every time a new C function is created, its prototype must be added to the `ffibuilder.cdef` function call

The header files required must be placed in the first argument of `ffibuilder.set_source`, and any additional `.C` files must be added to the `sources` argument of `ffibuilder.set_source`

"""
import os
import cffi

ffibuilder = cffi.FFI()

# FIXME: Can we generate this automatically or read it from a pyeaf.h file?
ffibuilder.cdef(
    """
    int read_datasets_(const char * filename, double **data_p, int *ncols_p, int *datasize_p);
    double fpli_hv(const double *data, int d, int n, const double *ref);
    double igd_C (const double *data, int nobj, int npoints, const double *ref, int ref_size, const bool * maximise);
    double igd_plus_C (const double *data, int nobj, int npoints, const double *ref, int ref_size, const bool * maximise);
    double avg_Hausdorff_dist_C (const double *data, int nobj, int npoints, const double *ref, int ref_size, const bool * maximise, unsigned int p);
    bool * is_nondominated_(const double * data, int nobj, int npoint, const bool * maximise, bool keep_weakly);
    double epsilon_ (const double *data, int nobj, int data_npoints, const double *ref, int ref_npoints, const bool * maximise, bool is_add);
    void normalise_(double *data, int nobj, int npoints, const bool * maximise, const double lower_range, const double upper_range, const double * lbounds, const double * ubounds);
    double * get_eaf_(double *data, int ncols, int npoints, double * percentiles, int npercentiles, bool choose_percentiles, int nsets, int * eaf_npoints, int * sizeof_eaf);
    """
)

file_path = os.path.dirname(os.path.realpath(__file__))


libeaf_path = os.path.join(file_path, "libeaf")
ffibuilder.set_source(
    "eafpy.c_bindings",
    """
    #include "io.h"   // the C header of the library
    #include "hv.h"   
    #include "igd.h" 
    #include "nondominated.h"
    #include "epsilon.h"
    #include "eaf.h"
""",
    sources=[
        "src/eafpy/libeaf/io.c",
        "src/eafpy/libeaf/hv.c",
        # "src/eafpy/libeaf/avl.c",
        "src/eafpy/libeaf/eaf.c",
        # "src/eafpy/libeaf/eaf3d.c",
    ],
    include_dirs=[libeaf_path],
)

if __name__ == "__main__":
    ffibuilder.compile(verbose=True)
