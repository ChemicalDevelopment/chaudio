/*

chaudio generator header file for development

*/


#ifndef __CHAUDIOGENERATOR_H__
#define __CHAUDIOGENERATOR_H__

#ifndef GENERATOR_NAME
#error Please define GENERATOR_NAME before including chaudiogenerator.h
#endif

// define this so chaudio.h knows how to handle it
#define IS_CHAUDIO_GENERATOR


#include "chaudio.h"

#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <string.h>
#include <math.h>

// chaudio dynamic link values
chaudio_dl_init_t _cdl;

// forward declaration. This should be defined in the plugin itself
chaudio_generator_t register_generator();

// should be called internally
chaudio_generator_t chaudiogenerator_export(chaudio_dl_init_t _v) {
    _cdl = _v;
    return register_generator();
}


/* utility macros/functions */
#define streq(a, b) (strcmp((a), (b)) == 0)
#define strkeep(a, b) a = realloc(a, strlen(b) + 1); strcpy(a, b);
#define chaudio_time (_cdl.chaudio_time)
#define chaudio_paraminterface_create (_cdl.chaudio_paraminterface_create)

/* generator-specific functions */
#define chaudio_generator_create (_cdl.chaudio_generator_create)
#define chaudio_read_wav_samples (_cdl.chaudio_read_wav_samples)

#endif

