
#include "chaudio.h"


int main(int argc, char ** argv) {

    audio_t audio;

    chaudio_create_audio_from_wav_file(&audio, "../data/sin_110.wav");

    chaudio_to_wav_file("../data/OUTPUT.wav", audio, CHAUDIO_WAVFMT_16I);

    chaudio_destroy_audio(&audio);

    return 0;
}



