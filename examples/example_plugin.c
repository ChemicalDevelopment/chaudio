
#include "chaudio.h"

#include <stdlib.h>

// getopt
#include <unistd.h>

#include <string.h>


int main(int argc, char ** argv) {

    chaudio_init();

    // what is our input/output?
    char * input_file = NULL;
    char * output_file = NULL;

    int i;
    char c;

    double gain = 10.0;

    while ((c = getopt (argc, argv, "i:o:h")) != (char)-1) {
        if (c == 'h') {
            printf("chaudio plugin\n");
            printf("Usage: ch_plugin [options...] [input]\n");
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

    chaudio_plugin_t plugin = chaudio_plugin_gain;
    chaudio_plugin_init(&plugin, (int32_t)2, (int32_t)44100);

    chdict_set(plugin.dict, "gain", chdictobj_double(gain));

    audio_t audio;

    // read in the file
    if (input_file == NULL || strcmp(input_file, "-") == 0) {
        audio = chaudio_audio_create_wav_fp(stdin);
    } else {
        audio = chaudio_audio_create_wav(input_file);
    }

    audio_t res = chaudio_plugin_transform(&plugin, audio, 256, NULL);

    // output it
    if (output_file == NULL || strcmp(output_file, "-") == 0) {
        chaudio_audio_output_wav_fp(stdout, res, CHAUDIO_WAVFMT_16I);
    } else {
        chaudio_audio_output_wav(output_file, res, CHAUDIO_WAVFMT_16I);
    }


    chaudio_audio_free(&audio);
    chaudio_audio_free(&res);

    return 0;
}



