
#include "chaudio.h"

#include <stdlib.h>

// getopt
#include <unistd.h>

#include <string.h>


int main(int argc, char ** argv) {


    //printf("asdasdf\n");

    // what is our input/output?
    char * input_file = NULL;
    char * output_file = NULL;

    int i;
    char c;

    while ((c = getopt (argc, argv, "i:o:h")) != (char)-1) {
        if (c == 'h') {
            printf("chaudio write\n");
            printf("Usage: ch_write [options...] [input]\n");
            printf("\n");
            printf("  -i          input file (if nothing, uses stdin)\n");
            printf("  -o          output file (if nothing, uses stdout)\n");
            printf("  -h          show this help message\n");
            printf("\n");
            return 0;
        } else if (c == 'i') {
            input_file = optarg;
        } else if (c == 'o') {
            output_file = optarg;
        } else {
            printf("ERROR: incorrect argument: -%c\n", optopt);
            return 1;
        }
    }

    audio_t audio;

    // read in the file
    if (input_file == NULL || strcmp(input_file, "-") == 0) {
        chaudio_create_audio_from_wav_fp(&audio, stdin);
    } else {
        chaudio_create_audio_from_wav_file(&audio, input_file);
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



