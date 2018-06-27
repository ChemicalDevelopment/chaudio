
#include "chaudio.h"

#include "ch_plugin.h"

#include <stdlib.h>

// getopt
#include <unistd.h>

#include <string.h>


int main(int argc, char ** argv) {

    // what is our input/output?
    char * data_file = NULL;
    char * output_file = NULL;

    char * _tmp_key = (char *)malloc(CHAUDIO_MAX_PARAMETER_LENGTH);
    

    double _tmp_double;

    int i;
    char c;

    audio_plugin_t plugin;

    chaudio_plugin_init(&plugin, NULL, 0, 0, CHAUDIO_DEFAULT_SAMPLE_RATE);


    while ((c = getopt (argc, argv, "p:D:o:h")) != (char)-1) {
        if (c == 'h') {
            printf("chaudio write\n");
            printf("Usage: ch_write [options...] [input]\n");
            printf("\n");
            printf("  -o [file]             output file (if nothing, uses stdout)\n");
            printf("  -p [name]             plugin name\n");
            printf("  -D [name=val]         set double parameter\n");
            printf("  -h                    show this help message\n");
            printf("\n");
            return 0;
        } else if (c == 'p') {
            if (strcmp(optarg, "gain") == 0) {
                plugin.plugin_func = chaudio_plugin_GAIN;
            } else if (strcmp(optarg, "delay") == 0) {
                plugin.plugin_func = chaudio_plugin_DELAY;
            } else {
                fprintf(stderr, "ERROR: unknown plugin name: '%s'\n", optarg);
                return 1;
            }
        } else if (c == 'D') {
            sscanf(optarg, "%[^=]=%lf", _tmp_key, &_tmp_double);
            chaudio_plugin_param_set_double(&plugin, _tmp_key, _tmp_double);
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


    audio_t * result = chaudio_plugin_process(&plugin, NULL, audio);

    // output it
    if (output_file == NULL || strcmp(output_file, "-") == 0) {
        
        chaudio_to_wav_fp(stdout, *result, CHAUDIO_WAVFMT_16I);
    } else {
        chaudio_to_wav_file(output_file, *result, CHAUDIO_WAVFMT_16I);
    }


    chaudio_destroy_audio(&audio);
    chaudio_destroy_audio(result);
    chaudio_plugin_free(&plugin);

    return 0;
}



