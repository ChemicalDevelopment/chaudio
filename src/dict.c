
#include "chaudio.h"





chdictobj_t chdictobj_double(double val) {
    return (chdictobj_t){ .type = CHAUDIO_OBJTYPE_DOUBLE, .val.dval = val, .param_info = (chparam_t) {.is_applied = 0 }};
}

chdictobj_t chdictobj_double_info(double val, double minimum, double maximum, int32_t scale) {
    return (chdictobj_t){ .type = CHAUDIO_OBJTYPE_DOUBLE, .val.dval = val, .param_info = (chparam_t) { .minimum = minimum, .maximum = maximum, .scale = scale, .is_applied = 1 }};
}

chdictobj_t chdictobj_int(int32_t val) {
    return (chdictobj_t){ .type = CHAUDIO_OBJTYPE_INT, .val.ival = val, .param_info = (chparam_t) {.is_applied = 0 }};
}

chdictobj_t chdictobj_string(char * val) {
    char * res = malloc(strlen(val) + 1);
    strcpy(res, val);
    return (chdictobj_t){ .type = CHAUDIO_OBJTYPE_STRING, .val.sval = res, .param_info = (chparam_t) {.is_applied = 0 }};
}

chdictobj_t chdictobj_audio(audio_t val) {
    return (chdictobj_t){ .type = CHAUDIO_OBJTYPE_AUDIO, .val.aval = chaudio_copy(val, NULL), .param_info = (chparam_t) {.is_applied = 0 }};
}

chdictobj_t chdictobj_any(void * val) {
    return (chdictobj_t){ .type = CHAUDIO_OBJTYPE_ANY, .val.pval = val, .param_info = (chparam_t) {.is_applied = 0 }};
}

void chdictobj_free(chdictobj_t * x) {
    if (x->type == CHAUDIO_OBJTYPE_STRING) {
        free(x->val.sval);
    } else if (x->type == CHAUDIO_OBJTYPE_AUDIO) {
        chaudio_audio_free(&x->val.aval);
    }
}

void chdict_init(chdict_t * dict) {
    dict->len = 0;
    dict->keys = NULL;
    dict->vals = NULL;
}

void chdict_free(chdict_t * dict) {
    int i;

    if (dict->keys != NULL) {
        for (i = 0; i < dict->len; ++i) {
            free(dict->keys[i]);
        }
        free(dict->keys);
    }
    if (dict->vals != NULL) {
        for (i = 0; i < dict->len; ++i) {
            chdictobj_free(&dict->vals[i]);
        }
        free(dict->vals);
    }

    dict->len = 0;

}

int _chdict_idx(chdict_t * dict, char * key) {
    int i;
    for (i = 0; i < dict->len; ++i) {
        if (strcmp(dict->keys[i], key) == 0) {
            return i;
        }
    }
    return -1;
}

chdictobj_t chdict_get(chdict_t * dict, char * key) {
    int idx = _chdict_idx(dict, key);
    if (idx < 0) return (chdictobj_t){ .type = CHAUDIO_OBJTYPE_NOTFOUND, .val.pval = NULL };
    else return dict->vals[idx];
}


double chdict_get_double(chdict_t * dict, char * key) {
    int idx = _chdict_idx(dict, key);
    if (idx < 0 || dict->vals[idx].type != CHAUDIO_OBJTYPE_DOUBLE) return 0.0;
    else return dict->vals[idx].val.dval;
}


char * chdict_get_string(chdict_t * dict, char * key) {
    int idx = _chdict_idx(dict, key);
    if (idx < 0 || dict->vals[idx].type != CHAUDIO_OBJTYPE_STRING) return NULL;
    else return dict->vals[idx].val.sval;
}


void chdict_set(chdict_t * dict, char * key, chdictobj_t val) {
    int idx = _chdict_idx(dict, key);
    if (idx < 0) {
        // creating new entry
        dict->len++;
        dict->keys = (char *)realloc(dict->keys, sizeof(char *) * dict->len);
        dict->vals = (chdictobj_t *)realloc(dict->vals, sizeof(chdictobj_t) * dict->len);

        idx = dict->len - 1;
        dict->keys[idx] = malloc(strlen(key) + 1);
        strcpy(dict->keys[idx], key);
    } else {
        chdictobj_free(&dict->vals[idx]);
    }

    dict->vals[idx] = val;
}

void chdict_set_any(chdict_t * dict, char * key, void * val) {
    chdict_set(dict, key, chdictobj_any(val));    
}


