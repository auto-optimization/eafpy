from cffi import FFI

ffibuilder = FFI()
import os


ffibuilder.cdef(
    """
    int read_double_data (const char *filename, double **data_p, 
                  int *nobjs_p, int **cumsizes_p, int *nsets_p);
"""
)

ffibuilder.set_source(
    "eafpy.c_bindings",
    """
     #include "io.h"   // the C header of the library
""",
    sources=["src/eafpy/io.c"],
    include_dirs=[os.path.dirname(os.path.realpath(__file__))],
)

if __name__ == "__main__":
    ffibuilder.compile(verbose=True)
