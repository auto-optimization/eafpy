import os
import cffi

ffibuilder = cffi.FFI()

ffibuilder.cdef(
    """
    int read_datasets_(const char * filename, double **data_p, int *ncols_p, int *datasize_p);
    """
)

ffibuilder.set_source(
    "eafpy.c_bindings",
    """
     #include "io.h"   // the C header of the library
""",
    sources=["src/eafpy/io.c"],
    # sources=["io.c"], #comment above and uncomment this if testing without build
    include_dirs=[os.path.dirname(os.path.realpath(__file__))],
)

if __name__ == "__main__":
    ffibuilder.compile(verbose=True)
