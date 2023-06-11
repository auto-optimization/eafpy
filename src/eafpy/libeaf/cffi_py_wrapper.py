import ex_cffi
import numpy as np
from ex_cffi import lib, ffi

filename = "input1.dat".encode("utf-8")

double_array = np.zeros((2, 100), dtype=np.double)
ffi_double_array = ffi.cast("double **", ffi.from_buffer(double_array))

doubleptr = ffi.new("double *", 5)
outputdata = ffi.new("double **", doubleptr)

lib.read_datasets(filename, ffi_double_array)
print(outputdata)
