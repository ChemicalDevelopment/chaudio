
#include "chaudio.h"

#include <stdlib.h>

// getopt
#include <unistd.h>

#include <string.h>


int main(int argc, char ** argv) {


    //printf("asdasdf\n");

    // what is our input?
    char * data_file = NULL;

    char * output_file = NULL;

    int i;

    char c;

    while ((c = getopt (argc, argv, "o:h")) != (char)-1) {
        if (c == 'h') {
            printf("chaudio write\n");
            printf("Usage: ch_write [options...] [input]\n");
            printf("\n");
            printf("  -o          output file (if nothing, uses stdout)\n");
            printf("  -h          show this help message\n");
            printf("\n");
            return 0;
        } else if (c == 'o') {
            output_file = optarg;
        } else {
            printf("ERROR: incorrect argument: -%c\n", optopt);
            return 1;
        }
    }


    if (optind < argc) {
        data_file = argv[optind];
    } else {
        printf("ERROR: require argument for input file (- for stdin)\n");
        return 2;
    }

    audio_t audio;

    // read in the file
    if (data_file == NULL || strcmp(data_file, "-") == 0) {
        chaudio_create_audio_from_wav_fp(&audio, stdin);
    } else {
        chaudio_create_audio_from_wav_file(&audio, data_file);
    }

    // output it
    if (output_file == NULL || strcmp(output_file, "-") == 0) {
        
        chaudio_to_wav_fp(stdout, audio, CHAUDIO_WAVFMT_16I);
    } else {
        chaudio_to_wav_file(output_file, audio, CHAUDIO_WAVFMT_16I);
    }


    chaudio_destroy_audio(&audio);

    return 0;
}



