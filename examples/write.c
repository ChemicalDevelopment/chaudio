
#include "chaudio.h"

#include <stdlib.h>

#include <unistd.h>
#include <string.h>


int main(int argc, char ** argv) {

    chaudio_init();

    // what is our input/output?
    char * input_file = NULL;
    char * output_file = NULL;

    int i;
    char c;

    while ((c = getopt (argc, argv, "i:o:h")) != (char)-1) {
        if (c == 'h') {
            printf("chaudio write, writing a file to disc\n");
            printf("Usage: write [options...] [input]\n");
            printf("\n");
            printf("  -i          input file (default is stdin)\n");
            printf("  -o          output file (default is stdin)\n");
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
        audio = chaudio_audio_create_wav_fp(stdin);
    } else {
        audio = chaudio_audio_create_wav(input_file);
    }


    // output it
    if (output_file == NULL || strcmp(output_file, "-") == 0) {
        chaudio_audio_output_wav_fp(stdout, audio, CHAUDIO_WAVFMT_16I);
    } else {
        chaudio_audio_output_wav(output_file, audio, CHAUDIO_WAVFMT_16I);
    }


    chaudio_audio_free(&audio);

    return 0;
}



