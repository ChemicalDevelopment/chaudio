/*

a sample showing a realtime pipeline implementation in Chaudio

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

    // our input/output is default pulseaudio

    int i;
    char c;


    int32_t sample_rate = CHAUDIO_DEFAULT_SAMPLE_RATE;
    int32_t bufsize = 256;// for raeltime

    char * ckey = malloc(4096);
    double cval = 0.0; 
    

    chaudio_pipeline_t pipeline = chaudio_pipeline_create(1, 44100);

    chaudio_generator_t gen;

    while ((c = getopt (argc, argv, "b:i:p:D:r:h")) != (char)-1) {
        if (c == 'h') {
            printf("Realtime audio processing\n");
            printf("Usage: ch_realtime_pipeline [options...]\n");
            printf("\n");
            printf("  -b [N]                      processing buffer size\n");
            printf("  -r [N]                      set sample rate\n");
            printf("  -i [gen.so]                 generator to use for input\n");
            printf("  -p [plg.so]                 plugin library file\n");
            printf("  -D [k=v]                    set a value for a plugin\n");
            printf("  -h                          show this help message\n");
            printf("%s", chaudio_get_build_info());
            printf("\n");
            return 0;
        } else if (c == 'r') {
	    sscanf(optarg, "%d", &sample_rate);
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
        } else if (c == 'D') {
            sscanf(optarg, "%[^=]=%lf", ckey, &cval);
            chaudio_plugin_t plg = pipeline.plugins[pipeline.plugins_len-1];
            plg.params.set_double(plg.plugin_data, ckey, cval);
        } else {
            printf("ERROR: incorrect argument: -%c\n", optopt);
            return 1;
        }
    }

    //chaudio_pipeline_runforever(&pipeline, bufsize);
#ifdef HAVE_PORTAUDIO
    chaudio_portaudio_realtime_process(&pipeline, bufsize, sample_rate);
#else
    printf("To use ch_realtime_pipline, you need to recompile with PortAudio!\n");
    return 1;
#endif


    return 0;
}



