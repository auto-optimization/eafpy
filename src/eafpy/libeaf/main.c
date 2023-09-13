/* 
    This is a file used for debugging the C code more easily


   Compile this file with:
   gcc main.c io.c eaf.c eaf3d.c avl.c
*/
#include "io.h"
// #include "hv.h"
// #include "nondominated.h"
#include "eaf.h"
#include <stdint.h>

void test_read_double_data(){
    const char * filename ="input1.dat";
    double * return_data = NULL;
    int num_obj = 0;
    int *cumsizes = NULL;
    int num_sets=0;


    int x = read_double_data(filename, &return_data, &num_obj, &cumsizes, &num_sets);
    
    // printf("return value: %d\nnum_obj: %d\nnum_sets: %d\n", x, num_obj, num_sets);
    // printf("cumsizes: {");
    // for (int i = 0; i < num_sets; i++) {
    //     printf("%d ", cumsizes[i]);
    // }
    // printf("}\n");
    // for (int j = 0; j < num_obj; j++) {
    //     printf("obj%-12d ", j+1);
    // }
    // printf("set\n");
    // int set = 1;
    // int i = 0;
    // while (i < cumsizes[num_sets - 1]) {
    //     for (int j = 0; j < num_obj; j++) {
    //         printf("%-15g ", return_data[i * num_obj + j]);
    //     }
    //     printf("%d\n", set);
    //     i++;
    //     if (i == cumsizes[set - 1])
    //         set++;
    // }
    
    printf("pre-made cumsizes: ");
    for(int i = 0; i< num_sets; i++){
        printf("%d ", cumsizes[i]);
    }
    // int* cumsizes_test = get_cumsizes_(return_data, 3, cumsizes[num_sets-1] ,num_sets);
    // printf("\nCalculated cumsizes: ");
    // for(int i = 0; i< num_sets; i++){
    //     printf("%d ", cumsizes_test[i]);
    // }
}

void printBinaryData(void* address, size_t size) {
    unsigned char* data = (unsigned char*) address;
    printf("\n");
    for (size_t i = 0; i < size; i++) {
        unsigned char byte = data[i];
        for (int bit = 7; bit >= 0; bit--) {
            printf("%d", (byte >> bit) & 1);
        }
        printf(" ");
    }
    printf("\n");
}

void test_cumsizes(){
    double * data = NULL;
    int ncols = 0;
    int datasize_p = 0;
    const char * filename ="input1.dat";
    int x = read_datasets_(filename, &data, &ncols, &datasize_p);
    int nrows = datasize_p/(ncols*sizeof(double));
    printf("nrows: %d, ",nrows);

    int* cumsizes_test = get_cumsizes_(data, ncols, nrows,10);
    printf("Cumsizes from get_cumsizes_\n");
    for(int i = 0; i< 10; i++){
        printf("%d ", cumsizes_test[i]);
    }

    double * return_data = NULL;
    int num_obj = 0;
    int *cumsizes = NULL;
    int num_sets=0;
    int xs= read_double_data(filename, &return_data, &num_obj, &cumsizes, &num_sets);
    printf("Cumsizes from read_double_data\n");
    for(int i = 0; i< 10; i++){
        printf("%d ", cumsizes[i]);
    }
}

// double * copy_data_no_setnums(double * data, int ncols, int npoints){
//     int data_ncols = ncols-1;
//     double *data_no_sets = malloc(sizeof(double)* data_ncols*npoints);
    
//     for(int i=0;i<npoints;i++){ 
//         data_no_sets[data_ncols*i] = data[ncols*i];
//         data_no_sets[data_ncols*i+1] = data[ncols*i+1];
//     }
//     return data_no_sets;
// }

void test_eaf(){
    // gcc main.c io.c eaf.c eaf3d.c avl.c
    double * data = NULL;
    int ncols = 0;
    int datasize_p = 0;
    const char * filename ="input1.dat";
    int x = read_datasets_(filename, &data, &ncols, &datasize_p);
    int npoints = datasize_p/(ncols *sizeof(double));
    printf("Ncols: %d\n ", ncols);
    // double *newdat = copy_data_no_setnums(data, ncols, npoints);

    // for (size_t i = 0; i < npoints; i++)
    // {
    //     printf("%f %f\n", newdat[2*i],  newdat[2*i+1]);
    // }


    int eaf_size_p = 0;
    int eaf_points = 0;
    printf("npoints %d\n", npoints);
    double * eaf = get_eaf_(data, 3, npoints, 0, 0, FALSE, 10,
                &eaf_points,
                &eaf_size_p,
                TRUE
                );  /*-> Returns pointer to row major order array containing the EAF data points and relevant percentiles  */

    printf("\nEAF data\n");
    for (size_t i = 0; i < eaf_points; i++)
    {
        printf("%f %f %f \n", eaf[3*i],  eaf[3*i+1],  eaf[3*i+2]);
    }
}





int main()
{   
   test_eaf();

    return 0;
}
