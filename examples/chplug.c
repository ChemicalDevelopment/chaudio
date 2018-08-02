

#include "chplug/chplug.h"

#include <stdio.h>
#include <stdlib.h>

int main(int argc, char ** argv) {
    char * fname = "./gain.chplug";
    printf("chplug example: %s\n", fname);

    chplug_t gain = chplug_create(fname);
    if (gain.status != 0) {
        printf("failed to create the plugin!\n");
    }

    int i;
    for (i = 0; i < gain.globals.int_n; ++i) {
        printf("@'%s' = '%d'\n", gain.globals.int_k[i], gain.globals.int_v[i]);
    }
   // printf("source: \n%s\n", gain.src);
    chast_d_t C_1, C_2;

    C_1.op = COP_NONE; // or COP_VALUE
    C_2.op = COP_NONE;
    C_1.val = 1.0;
    C_2.val = 2.0;

    chast_d_t added;
    added.op = COP_ADD;
    added.A = &C_1;
    added.B = &C_2;

    printf("val(added)=%lf\n", chast_d_val(&added, 0, NULL, NULL));


}

