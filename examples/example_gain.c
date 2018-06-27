
#include "chaudio.h"

#include <stdlib.h>

// getopt
#include <unistd.h>

#include <string.h>


int main(int argc, char ** argv) {


    // what is our input/output?
    char * data_file = NULL;
    char * output_file = NULL;

    int i;
    char c;

    double gain = 0.0;

    while ((c = getopt (argc, argv, "g:o:h")) != (char)-1) {
        if (c == 'h') {
            printf("chaudio write\n");
            printf("Usage: ch_write [options...] [input]\n");
            printf("\n");
            printf("  -o [file]   output file (if nothing, uses stdout)\n");
            printf("  -db [n]     decibels to gain\n");
            printf("  -h          show this help message\n");
            printf("\n");
        } else if (c == 'g') {
            sscanf(optarg, "%lf", &gain);
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

    audio_t * result = chaudio_gain(NULL, audio, gain);

    // output it
    if (output_file == NULL || strcmp(output_file, "-") == 0) {
        
        chaudio_to_wav_fp(stdout, *result, CHAUDIO_WAVFMT_16I);
    } else {
        chaudio_to_wav_file(output_file, *result, CHAUDIO_WAVFMT_16I);
    }


    chaudio_destroy_audio(&audio);
    chaudio_destroy_audio(result);

    return 0;
}



