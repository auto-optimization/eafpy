import os
import cffi

ffibuilder = cffi.FFI()

ffibuilder.cdef(
    """
    int read_datasets_(const char * filename, double **data_p, int *ncols_p, int *datasize_p);
    double fpli_hv(const double *data, int d, int n, const double *ref);
    double igd_C (const double *data, int nobj, int npoints, const double *ref, int ref_size, const int *maximise);
    double igd_plus_C (const double *data, int nobj, int npoints, const double *ref, int ref_size, const int *maximise);
    double avg_Hausdorff_dist_C (const double *data, int nobj, int npoints, const double *ref, int ref_size, const int *maximise, unsigned int p);
    bool * is_nondominated_(const double * data, int nobj, int npoint, const bool * maximise, bool keep_weakly);
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
""",
    sources=[
        "src/eafpy/libeaf/io.c",
        "src/eafpy/libeaf/hv.c",
    ],
    include_dirs=[libeaf_path],
)

if __name__ == "__main__":
    ffibuilder.compile(verbose=True)
