/*

chaudio generator header file for development

*/


#ifndef __CHAUDIOOUTPUT_H__
#define __CHAUDIOOUTPUT_H__

#ifndef OUTPUT_NAME
#error Please define OUTPUT_NAME before including chaudiooutput.h
#endif

// define this so chaudio.h knows how to handle it
#define IS_CHAUDIO_OUTPUT


#include "chaudio.h"

#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <string.h>
#include <math.h>

// chaudio dynamic link values
chaudio_dl_init_t _cdl;

// forward declaration. This should be defined in the plugin itself
chaudio_output_t register_output();

// should be called internally
chaudio_output_t chaudiooutput_export(chaudio_dl_init_t _v) {
    _cdl = _v;
    return register_output();
}

/* utility macros/functions */
#define streq(a, b) (strcmp((a), (b)) == 0)
#define strkeep(a, b) a = realloc(a, strlen(b) + 1); strcpy(a, b);
#define chaudio_time (_cdl.chaudio_time)
#define chaudio_paraminterface_create (_cdl.chaudio_paraminterface_create)

/* output-specific functions */
#define chaudio_output_create (_cdl.chaudio_output_create)
#define chaudio_audio_output_wav (_cdl.chaudio_audio_output_wav)

#endif

