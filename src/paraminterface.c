

#include "chaudio.h"


chaudio_paraminterface_t chaudio_paraminterface_create(chaudio_SetDouble set_double, chaudio_SetInt set_int, chaudio_SetString set_string, chaudio_SetAudio set_audio) {
    chaudio_paraminterface_t r;

    r.set_double = set_double;
    r.set_int = set_int;
    r.set_string = set_string;
    r.set_audio = set_audio;

    return r;
}

