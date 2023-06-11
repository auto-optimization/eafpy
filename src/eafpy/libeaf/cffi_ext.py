from cffi import FFI

ffibuilder = FFI()

# cdef() expects a single string declaring the C types, functions and
# globals needed to use the shared object. It must be in valid C syntax.
ffibuilder.cdef(
    """
    void test_print(int to_print);
    int read_datasets(const char *filename, double **returndata);
    
"""
)

# set_source() gives the name of the python extension module to
# produce, and some C source code as a string.  This C code needs
# to make the declarated functions, types and globals available,
# so it is often just the "#include".
ffibuilder.set_source(
    "ex_cffi",
    """
     #include "io.h"   // the C header of the library
""",
    sources=["io.c"],
)

if __name__ == "__main__":
    ffibuilder.compile(verbose=True)
