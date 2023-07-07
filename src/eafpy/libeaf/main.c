/* In Linux, I can compile this with:
   
   gcc -o main main.c io.c
*/
#include "io.h"
#include "hv.h"

void test_read_double_data(){
    const char * filename ="uniform-250-10-3d.txt";
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
}

void print_read_datsets(const char * filename){
    // const char * filename ="uniform-250-10-3d.txt";
    // const char * filename ="test1.dat";
    double * return_data = NULL;
    int num_obj = 0;
    int num_rows = 0;
    int datasize = 0;

    int x = read_datasets_(filename, &return_data, &num_obj, &num_rows, &datasize);
    if(x != 0){
        printf("error detected %d", x);
    }

}


int main()
{   
   

    return 0;
}
