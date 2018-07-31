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

    int32_t bufsize = CHAUDIO_DEFAULT_BUFFER_SIZE;

    char * ckey = malloc(4096);
    double cval = 0.0; 
    

    chaudio_pipeline_t pipeline = chaudio_pipeline_create();

    while ((c = getopt (argc, argv, "b:p:D:h")) != (char)-1) {
        if (c == 'h') {
            printf("Realtime audio processing\n");
            printf("Usage: ch_realtime_pipeline [options...]\n");
            printf("\n");
            printf("  -b [N]                      processing buffer size\n");
            printf("  -p [plg.so]                 plugin library file\n");
            printf("  -D [k=v]                    set a value for a plugin\n");
            printf("  -h                          show this help message\n");
            printf("%s", chaudio_get_build_info());
            printf("\n");
            return 0;
        } else if (c == 'b') {
            sscanf(optarg, "%d", &bufsize);
        } else if (c == 'p') {
            chaudio_plugin_t cplug = chaudio_plugin_load(optarg);
            chaudio_plugin_init(&cplug, 1, 44100);
            chaudio_pipeline_add(&pipeline, cplug);
        } else if (c == 'D') {
            sscanf(optarg, "%[^=]=%lf", ckey, &cval);
            pipeline.plugins[pipeline.plugins_len-1].set_double(pipeline.plugins[pipeline.plugins_len-1].plugin_data, ckey, cval);
        } else {
            printf("ERROR: incorrect argument: -%c\n", optopt);
            return 1;
        }
    }

    //chaudio_pipeline_runforever(&pipeline, bufsize);
#ifdef HAVE_PORTAUDIO
    chaudio_portaudio_realtime_process(&pipeline, bufsize);
#else
    printf("To use ch_realtime_pipline, you need to recompile with PortAudio!\n");
    return 1;
#endif


    return 0;
}



