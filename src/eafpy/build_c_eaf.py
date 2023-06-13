from cffi import FFI

ffibuilder = FFI()
import os


# set_source() gives the name of the python extension module to
# produce, and some C source code as a string.  This C code needs
# to make the declarated functions, types and globals available,
# so it is often just the "#include".
ffibuilder.set_source(
    "c_bindings",
    """
     #include "io.h"   // the C header of the library
""",
    sources=["io.c"],
    include_dirs=[os.path.dirname(os.path.realpath(__file__))],
)
# cdef() expects a single string declaring the C types, functions and
# globals needed to use the shared object. It must be in valid C syntax.
ffibuilder.cdef(
    """
    void test_print(int to_print);
    int read_double_data (const char *filename, double **data_p, 
                  int *nobjs_p, int **cumsizes_p, int *nsets_p);
"""
)

if __name__ == "__main__":
    ffibuilder.compile(verbose=True)
