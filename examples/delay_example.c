
#include "chaudio.h"
#include "ch_plugin.h"

#include <stdlib.h>

int main(int argc, char ** argv) {

    audio_t audio;

    chaudio_create_audio_from_wav_file(&audio, "../data/sin_110.wav");

    // create a plugin
    audio_plugin_t delayer;
    chaudio_plugin_init(&delayer, chaudio_plugin_DELAY, audio.channels, audio.length, audio.sample_rate);
    chaudio_plugin_param_add(&delayer, "delay", chaudio_param_create_double(0.0));
    chaudio_plugin_param_add(&delayer, "feedback", chaudio_param_create_double(0.0));

    // now control it
    chaudio_plugin_param_set_double(&delayer, "delay", 1.0);
    chaudio_plugin_param_set_double(&delayer, "feedback", 0.5);


    // get our result
    audio_t * result = chaudio_plugin_process(&delayer, NULL, audio);


    chaudio_to_wav_file("./OUTPUT_delayed.wav", *result, CHAUDIO_WAVFMT_16I);

    chaudio_destroy_audio(&audio);

    return 0;
}



