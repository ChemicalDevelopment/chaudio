/*

a sample showing pipeline processing in chaudio

*/


#include "chaudio.h"

#include <stdlib.h>
#include <stdio.h>

// getopt
#include <unistd.h>
#include <getopt.h>

#include <string.h>


#include <signal.h>

// use this to capture CTRL-C
static volatile int signal_val = 0;

void signal_handler(int val) {
    if (signal_val != 0) exit(0);

    signal_val = 1;
}

// waits how_long, or never if how_long < 0
bool stop_func() {
    return signal_val != 0;
}


int main(int argc, char ** argv) {

    chaudio_init();

    // our input/output is default pulseaudio

    int i;
    char c;

    int32_t bufsize = CHAUDIO_DEFAULT_BUFFER_SIZE;

    char * ckey = malloc(4096);
    char * cval_str = malloc(4096);
    double cval = 0.0; 
    
    chaudio_pipeline_t pipeline = chaudio_pipeline_create(1, 44100);

    chaudio_generator_t gen;
    chaudio_output_t out;



    while ((c = getopt (argc, argv, "b:i:p:D:S:o:h")) != (char)-1) {
        if (c == 'h') {
            printf("Pipeline audio processing\n");
            printf("Usage: ch_pipeline [options...]\n");
            printf("\n");
            printf("  -b [N]                      processing buffer size\n");
            printf("  -i [gen.so]                 generator to use for input\n");
            printf("  -p [plg.so]                 plugin library file\n");
            printf("  -D [k=v]                    set a double value for a plugin\n");
            printf("  -S [k=v]                    set a string value for a plugin\n");
            printf("  -o [out.so]                 output library\n");
            printf("  -h                          show this help message\n");
            printf("%s", chaudio_get_build_info());
            printf("\n");
            return 0;
        } else if (c == 'b') {
            sscanf(optarg, "%d", &bufsize);
        } else if (c == 'i') {
            gen = chaudio_generator_load(optarg);
            if (!CHAUDIO_GENERATOR_ISVALID(gen)) {
                printf("generator is invalid: '%s'\n", optarg);
                return -1;
            }
            pipeline.generator = &gen;
        } else if (c == 'p') {
            chaudio_plugin_t cplug = chaudio_plugin_load(optarg);
            if (!CHAUDIO_PLUGIN_ISVALID(cplug)) {
                printf("plugin is invalid: '%s'\n", optarg);
                return -1;
            }
            chaudio_pipeline_add(&pipeline, cplug);
        } else if (c == 'o') {
            out = chaudio_output_load(optarg);
            if (!CHAUDIO_OUTPUT_ISVALID(out)) {
                printf("output is invalid: '%s'\n", optarg);
                return -1;
            }
            pipeline.output = &out;
        } else if (c == 'S' || c == 'D') {
            // do nothing, these are handled later
        } else {
            printf("ERROR: incorrect argument: -%c\n", optopt);
            return 1;
        }

    }


    // capture so we finish and write if we use CTRL-C
    signal(SIGINT, signal_handler);

    chaudio_pipeline_init(&pipeline);

    // reset once we've initialized, then set parameters
    optind = 1;

    // 0=generator, 1=plugin, 2=output
    int last_loaded = -1;
    int cur_plugin = -1;

    while ((c = getopt (argc, argv, "b:i:p:D:S:o:h")) != (char)-1) {

        if (c == 'i') {
            last_loaded = 0;
        } else if (c == 'p') {
            last_loaded = 1;
            cur_plugin++;
        } else if (c == 'o') {
            last_loaded = 2;
        } else if (c == 'D') {
            
            sscanf(optarg, "%[^=]=%lf", ckey, &cval);
            if (last_loaded == 0) {
                // this is a param for the input
                pipeline.generator->params.set_double(pipeline.generator->generator_data, ckey, cval);
            } else if (last_loaded == 1) {
                // param for the last plugin
                chaudio_plugin_t plg = pipeline.plugins[cur_plugin];
                plg.params.set_double(plg.plugin_data, ckey, cval);
            } else if (last_loaded == 2) {
                // param for the output
                pipeline.output->params.set_double(pipeline.output->output_data, ckey, cval);
            } else {
                printf("You specified -D before loading anything! Nothing to set!\n");
                exit(1);
            }
        } else if (c == 'S') {
            sscanf(optarg, "%[^=]=%s", ckey, cval_str);
            if (last_loaded == 0) {
                // this is a param for the input
                pipeline.generator->params.set_string(pipeline.generator->generator_data, ckey, cval_str);
            } else if (last_loaded == 1) {
                // param for the last plugin
                chaudio_plugin_t plg = pipeline.plugins[cur_plugin];
                plg.params.set_string(plg.plugin_data, ckey, cval_str);
            } else if (last_loaded == 2) {
                // param for the output
                pipeline.output->params.set_string(pipeline.output->output_data, ckey, cval_str);
            } else {
                printf("'%s'='%s'\n", ckey, cval_str);
                printf("You specified -S before loading anything! Nothing to set!\n");
                exit(1);
            }
        }

    }


    chaudio_pipeline_runstream(&pipeline, bufsize, -1.0, stop_func);

    chaudio_pipeline_free(&pipeline);

    return 0;
}



