

/*

basic chaudio dictionary object

*/

#ifndef __DICT_H__
#define __DICT_H__

#include "ch_defs.h"


// create parameters here
chdictobj_t chdictobj_double(double val);
// variant to use 'info'
chdictobj_t chdictobj_double_info(double val, double minimum, double maximum, int32_t scale);
chdictobj_t chdictobj_int(int val);
chdictobj_t chdictobj_string(char * val);
chdictobj_t chdictobj_audio(audio_t val);
chdictobj_t chdictobj_any(void * val);

void chdictobj_free(chdictobj_t * x);

void chdict_init(chdict_t * dict);

void chdict_set(chdict_t * dict, char * key, chdictobj_t val);

void chdict_set_any(chdict_t * dict, char * key, void * val);

// check for error here!
// it will return OBJTYPE_NOTFOUND as the .type if it was invalid
chdictobj_t chdict_get(chdict_t * dict, char * key);


double chdict_get_double(chdict_t * dict, char * key);
char * chdict_get_string(chdict_t * dict, char * key);

void chdict_free(chdict_t * dict);

#endif
