import os
import cffi

ffibuilder = cffi.FFI()

ffibuilder.cdef(
    """
    int read_datasets_(const char * filename, double **data_p, int *ncols_p, int *datasize_p);
    double fpli_hv(const double *data, int d, int n, const double *ref);
    double igd_C (const double *data, int nobj, int npoints, const double *ref, int ref_size, const int *maximise);
    double igd_plus_C (const double *data, int nobj, int npoints, const double *ref, int ref_size, const int *maximise);
    """
)

file_path = os.path.dirname(os.path.realpath(__file__))
libeaf_path = os.path.join(file_path, "libeaf")
ffibuilder.set_source(
    "eafpy.c_bindings",
    """
    #include "io.h"   // the C header of the library
    #include "hv.h"   //
    #include "igd.h" //
""",
    sources=[
        "src/eafpy/libeaf/io.c",
        "src/eafpy/libeaf/hv.c",
    ],
    # sources=["io.c"], #comment above and uncomment this if testing without build
    include_dirs=[libeaf_path],
)

if __name__ == "__main__":
    ffibuilder.compile(verbose=True)
