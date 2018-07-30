
#include "chaudio.h"

#include <stdlib.h>
#include <stdio.h>

// getopt
#include <unistd.h>
#include <getopt.h>

#include <string.h>



int main(int argc, char ** argv) {

    chaudio_init();

    // what is our input/output?
    char * input_file = NULL;
    char * plugin_name = NULL;
    char * output_file = NULL;

    int i;
    char c;

    // for setting parameters
    int n_sets = 0;
    char ** keys = NULL;
    double * vals = NULL;

    int32_t bufsize = CHAUDIO_DEFAULT_BUFFER_SIZE;

    while ((c = getopt (argc, argv, "i:o:p:D:b:h")) != (char)-1) {
        if (c == 'h') {
            printf("chaudio plugin processing\n");
            printf("Usage: plugin [options...] [input]\n");
            printf("\n");
            printf("  -i [in.wav]        input file (default: stdin)\n");
            printf("  -o [out.wav]       output file (default: stdout)\n");
            printf("  -p [plg.so]        plugin name (full path to library file)\n");
            printf("  -D [param=val]     set a parameter for the plugin to a value (doubles only)\n");
            printf("  -b [N]             processing buffer sample size (default=%d)\n", CHAUDIO_DEFAULT_BUFFER_SIZE);
            printf("  -h              show this help message\n");
            printf("\n");
            return 0;
        } else if (c == 'i') {
            input_file = optarg;
        } else if (c == 'o') {
            output_file = optarg;
        } else if (c == 'p') {
            plugin_name = optarg;
        } else if (c == 'D') {
            n_sets++;
            keys = realloc(keys, sizeof(char *) * n_sets);
            vals = realloc(vals, sizeof(double) * n_sets);
            keys[n_sets-1] = malloc(strlen(optarg) + 1);
            sscanf(optarg, "%[^=]=%lf", keys[n_sets - 1], &vals[n_sets - 1]);
        } else {
            printf("ERROR: incorrect argument: -%c\n", optopt);
            return 1;
        }
    }

    // read in the file
    audio_t audio;

    if (input_file == NULL || strcmp(input_file, "-") == 0) {
        audio = chaudio_audio_create_wav_fp(stdin);
    } else {
        audio = chaudio_audio_create_wav(input_file);
    }


    // the path (right now) has to be the actual `.so`, or `.dylib`
    chaudio_plugin_t plugin = chaudio_plugin_load(plugin_name);


    if (plugin.init == NULL) {
        printf("ERROR finding plugin '%s'\n", plugin_name);
        exit(1);
    }

    chaudio_plugin_init(&plugin, audio.channels, audio.sample_rate);

    for (i = 0; i < n_sets; ++i) {
        chdict_set(plugin.dict, keys[i], chdictobj_double(vals[i]));
    }


    // transform the result in buffer sizes
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



