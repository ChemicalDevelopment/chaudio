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

chaudioplugin_init_t _chaudioplugin_init_vals;

// forward declaration. This should be defined in the plugin itself
chaudio_plugin_t register_plugin();

// should be called internally
chaudio_plugin_t chaudioplugin_init(chaudioplugin_init_t __v) {
    _chaudioplugin_init_vals = __v;
    return register_plugin();
}


/* utility macros/functions */

#define streq(a, b) (strcmp((a), (b)) == 0)

/*  */
#define chaudio_plugin_create (_chaudioplugin_init_vals.chaudio_plugin_create)
#define chaudio_time (_chaudioplugin_init_vals.chaudio_time)


#endif

