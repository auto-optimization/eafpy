#include "io.h"

int main(){
    const char * filename ="input1.dat";
    double * return_data = 0;
    int num_obj=10;
    int * cumsizes;
    int numsets=10;
    int x = read_double_data(filename, &return_data,&num_obj, &cumsizes, &numsets);
    printf("%d", &x);



    return 0;
}