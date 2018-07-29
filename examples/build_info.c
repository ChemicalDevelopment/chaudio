
/*

basic example to print info

*/

#include "chaudio.h"

#include <stdlib.h>
#include <stdio.h>

// getopt
#include <unistd.h>
#include <getopt.h>

#include <string.h>


int main(int argc, char ** argv) {

    chaudio_init();

    printf("build info: %s\n", chaudio_get_build_info());

    return 0;
}



