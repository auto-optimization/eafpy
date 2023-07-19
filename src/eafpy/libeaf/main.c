/* In Linux, I can compile this with:
   
   gcc -o main main.c io.c
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
    int* cumsizes_test = get_cumsizes_(return_data, num_obj, cumsizes[num_sets - 1] ,num_sets);
    printf("\n");
    for(int i = 0; i< num_sets; i++){
        printf("%d ", cumsizes[i]);
    }
    // printf("\nCalculated cumsizes: \n");
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



int main()
{   
   test_read_double_data();
   double db = 123.5;
   int in = 23;
   printBinaryData(&db, sizeof(db));
   printf("\ninteger data: ");
   printBinaryData(&in, sizeof(db));

    return 0;
}
