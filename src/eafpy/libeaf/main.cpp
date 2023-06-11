#include <pybind11/pybind11.h>
namespace py = pybind11;

extern "C" {
    #include "io.h"
}


PYBIND11_MODULE(example, m) {
    m.doc() = "pybind11 example plugin"; // optional module docstring

    m.def("test_print", &test_print, "A function that prints a number");

    m.def("read_datasets", [](const std::string& filename) {
        double* data;
        int nobjs, *cumsizes, nsets;
        read_double_data(filename.c_str(), &data, &nobjs, &cumsizes, &nsets);

        // Create a Python list to store the data
        pybind11::list data_list;

        // Convert the data array to a Python list
        for (int i = 0; i < nobjs; ++i) {
            pybind11::list obj_data_list;
            for (int j = 0; j < cumsizes[i]; ++j) {
                obj_data_list.append(data[j]);
            }
            data_list.append(obj_data_list);
            data += cumsizes[i];
        }

        // Create a dictionary to store the result
        pybind11::dict result;
        result["data"] = data_list;
        result["nobjs"] = nobjs;
        result["cumsizes"] = cumsizes;
        result["nsets"] = nsets;

        return result;
    });

}

