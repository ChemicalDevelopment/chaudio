
#include "chaudio.h"
#include "ch_plugin.h"

#include <stdlib.h>

int main(int argc, char ** argv) {

    audio_t audio;

    chaudio_create_audio_from_wav_file(&audio, "../data/sin_110.wav");

    // create a plugin
    audio_plugin_t gainer;
    chaudio_plugin_init(&gainer, chaudio_plugin_GAIN, audio.channels, audio.length, audio.sample_rate);
    chaudio_plugin_param_add(&gainer, "gain", chaudio_param_create_double(0.0));



    // now control it
    chaudio_plugin_param_set_double(&gainer, "gain", -10.0);


    // get our result
    audio_t * result = chaudio_plugin_process_chunks(&gainer, NULL, audio, 16);


    chaudio_to_wav_file("./OUTPUT_plugin_chunked.wav", *result, CHAUDIO_WAVFMT_16I);

    chaudio_destroy_audio(&audio);

    return 0;
}



