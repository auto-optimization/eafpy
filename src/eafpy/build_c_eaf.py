import os
import cffi

ffibuilder = cffi.FFI()

ffibuilder.cdef(
    """
    int read_datasets_(const char * filename, double **data_p, int *ncols_p, int *datasize_p);
    double hv_(const double *data_p, int dataObjs, int dataPoints, const double *ref, int refObjs);
    """
)
file_path = os.path.dirname(os.path.realpath(__file__))
libeaf_path = os.path.join(file_path, "libeaf")
ffibuilder.set_source(
    "eafpy.c_bindings",
    """
    #include "io.h"   // the C header of the library
    #include "hv.h"   //
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
