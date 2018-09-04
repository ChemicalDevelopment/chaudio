/*

chaudio plugin header file utility


*/


#ifndef __CHAUDIOPLUGIN_H__
#define __CHAUDIOPLUGIN_H__

#ifndef PLUGIN_NAME
#error Please define PLUGIN_NAME before including chaudioplugin.h
#endif

// define this so chaudio.h knows how to handle it
#define IS_CHAUDIO_PLUGIN


#include "chaudio.h"

#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <string.h>
#include <math.h>

chaudio_dl_init_t _cdl;

// forward declaration. This should be defined in the plugin itself
chaudio_plugin_t register_plugin();

// should be called internally
chaudio_plugin_t chaudioplugin_export(chaudio_dl_init_t _v) {
    _cdl = _v;
    return register_plugin();
}

/* utility macros/functions */
#define streq(a, b) (strcmp((a), (b)) == 0)
#define strkeep(a, b) a = realloc(a, strlen(b) + 1); strcpy(a, b);
#define chaudio_time (_cdl.chaudio_time)
#define chaudio_paraminterface_create (_cdl.chaudio_paraminterface_create)
#define chfft_plan_free (_cdl.chfft_plan_free)
#define chfft_fft_plan (_cdl.chfft_fft_plan)
#define chfft_ifft_plan (_cdl.chfft_ifft_plan)
#define chfft_doplan (_cdl.chfft_doplan)

/* plugin-specific */
#define chaudio_plugin_create (_cdl.chaudio_plugin_create)
#define chaudio_read_wav_samples (_cdl.chaudio_read_wav_samples)


#endif

