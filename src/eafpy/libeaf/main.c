/* In Linux, I can compile this with:
   
   gcc -o main main.c io.c
*/
#include "io.h"

int main()
{
    const char * filename ="input1.dat";
    double * return_data = NULL;
    int num_obj = 0;
    int *cumsizes = NULL;
    int num_sets=0;
    int x = read_double_data(filename, &return_data, &num_obj, &cumsizes, &num_sets);
    printf("return value: %d\nnum_obj: %d\nnum_sets: %d\n", x, num_obj, num_sets);
    printf("cumsizes: {");
    for (int i = 0; i < num_sets; i++) {
        printf("%d ", cumsizes[i]);
    }
    printf("}\n");
    for (int j = 0; j < num_obj; j++) {
        printf("obj%-12d ", j+1);
    }
    printf("set\n");
    int set = 1;
    int i = 0;
    while (i < cumsizes[num_sets - 1]) {
        for (int j = 0; j < num_obj; j++) {
            printf("%-15g ", return_data[i * num_obj + j]);
        }
        printf("%d\n", set);
        i++;
        if (i == cumsizes[set - 1])
            set++;
    }
    return 0;
}
