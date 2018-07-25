/*

basic plugin interface

*/

#ifndef __CH_PLUGIN_H__
#define __CH_PLUGIN_H__


#include "ch_defs.h"


// audio plugin
// init defaults
void chaudio_plugin_create_defaults();

chaudio_plugin_t chaudio_plugin_create(chaudio_PluginInit _init, chaudio_PluginProcess _process, chaudio_PluginFree _free);

void chaudio_plugin_init(chaudio_plugin_t * plugin, uint32_t channels, uint32_t sample_rate);


audio_t chaudio_plugin_transform(chaudio_plugin_t * plugin, audio_t from, int32_t bufsize, audio_t * output);

int32_t chaudio_plugin_free(chaudio_plugin_t * plugin);



/* examples */

chaudio_plugin_t chaudio_plugin_gain;


#endif
