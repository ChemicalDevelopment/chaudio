
#include "chplug.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>

#define NUM_TYPES 4

char * types[NUM_TYPES] = { "int", "double", "string", "audio" };

char * _starts_with_type(char * v) {
    int i;
    for (i = 0; i < NUM_TYPES; ++i) {
        if (strncmp(v, types[i], strlen(types[i])) == 0) {
            if (strlen(v) > strlen(types[i])) {
                if (v[strlen(types[i])] == ' ') {
                    return types[i];
                }
            } else {
                return types[i];
            }
        }
    }
    return NULL;
}

#define _PARSEERROR(reason, ...) printf("ERROR while parsing '%s', on line '%s': " reason "\n", filename, line, __VA_ARGS__); chp.status = -1; return chp;
#define _PARSEERROR_NOARGS(reason) printf("ERROR while parsing '%s', on line '%s': " reason "\n", filename, line); chp.status = -1; return chp;

#define _ISALPHA(x) (x >= 'a' && x <= 'z') || (x >= 'A' && x <= 'Z')
#define ISALPHA(x) (_ISALPHA((x)))

chplug_t chplug_create(char * filename) {
    chplug_t chp;
    chp.status = 0;

    // keep track
    chp.globals.int_n = 0;
    chp.globals.int_k = NULL;
    chp.globals.int_v = NULL;

    chp.initfunc.int_n = 0;
    chp.initfunc.int_k = NULL;
    chp.initfunc.int_v = NULL;

    FILE * fp = fopen(filename, "r");
    if (fp == NULL) {
        printf("file '%s' doesn't exist!\n", filename);
        exit(1);
    }

    fseek(fp, 0, SEEK_END);
    long fsize = ftell(fp);
    fseek(fp, 0, SEEK_SET);  //same as rewind(f);

    chp.src = malloc(fsize + 1);
    chp.trav = malloc(fsize + 1);

    fread(chp.src, fsize, 1, fp);
    fclose(fp);

    chp.src[fsize] = 0;
    strcpy(chp.trav, chp.src);

    char * delim = "\n";

    char * line = strtok(chp.trav, delim);

    // current seek
    char * sk;
    int src_line_num = 0;

    char * tmp = NULL, *tmp2 = NULL;

    // 0 = init
    int method_in = -1;

    while (line != NULL) {
        // strip, process, take out comments, etc
        src_line_num++;

        while (*line == ' ') line++;

        sk = line;
        while (sk < line + strlen(line)) {
            if (*sk == '#') {
                *sk = '\0';
                break;
            }
            sk++;
        }

        // always wanna have enough room
        tmp = realloc(tmp, strlen(line) + 1);
        tmp2 = realloc(tmp2, strlen(line) + 1);
        sk = line;

        if (strlen(line) > 0) {
            //printf("'%s'\n", line);

            char * starting_type = _starts_with_type(line);
            if (starting_type == NULL) {
                if (*sk == ':') {
                    sk++;
                    int i = 0;
                    while (ISALPHA(*sk)) {
                        tmp[i++] = *sk;
                        sk++;
                    }
                    tmp[i] = '\0';

                    while (*sk == ' ') sk++;

                    if (strcmp(tmp, "init") == 0) {
                        if (*sk != '(') {
                            _PARSEERROR_NOARGS("function should have '(' after it");
                        }
                        sk++;
                        if (!_starts_with_type(sk)) {
                            _PARSEERROR_NOARGS("argument does not have a valid type!");
                        }
                        if (strcmp(_starts_with_type(sk), "int") != 0) {
                            _PARSEERROR_NOARGS("argument[0] to 'init' function should be 'int'");
                        }
                        sk += strlen(_starts_with_type(sk));
                        while (*sk == ' ') sk++;
                        i = 0;
                        while (ISALPHA(*sk)) {
                            tmp[i++] = *sk;
                            sk++;
                        }
                        tmp[i] = '\0';

                        chp.initfunc.int_n++;
                        chp.initfunc.int_k = realloc(chp.initfunc.int_k, sizeof(char *) * chp.initfunc.int_n);
                        chp.initfunc.int_v = realloc(chp.initfunc.int_v, sizeof(int) * chp.initfunc.int_n);

                        chp.initfunc.int_k[chp.initfunc.int_n - 1] = malloc(strlen(tmp) + 1);
                        strcpy(chp.initfunc.int_k[chp.initfunc.int_n - 1], tmp);
                        chp.initfunc.int_v[chp.initfunc.int_n - 1] = 0;

                        if (*sk != ',') {
                            _PARSEERROR_NOARGS("expected ',' right after parameter name\n");
                        }
                        sk++;
                        while (*sk == ' ') sk++;

                        if (!_starts_with_type(sk)) {
                            _PARSEERROR_NOARGS("argument does not have a valid type!");
                        }
                        if (strcmp(_starts_with_type(sk), "int") != 0) {
                            _PARSEERROR_NOARGS("argument[1] to 'init' function should be 'int'");
                        }
                        sk += strlen(_starts_with_type(sk));
                        while (*sk == ' ') sk++;
                        i = 0;
                        while (ISALPHA(*sk)) {
                            tmp[i++] = *sk;
                            sk++;
                        }
                        tmp[i] = '\0';

                        chp.initfunc.int_n++;
                        chp.initfunc.int_k = realloc(chp.initfunc.int_k, sizeof(char *) * chp.initfunc.int_n);
                        chp.initfunc.int_v = realloc(chp.initfunc.int_v, sizeof(int) * chp.initfunc.int_n);

                        chp.initfunc.int_k[chp.initfunc.int_n - 1] = malloc(strlen(tmp) + 1);
                        strcpy(chp.initfunc.int_k[chp.initfunc.int_n - 1], tmp);
                        chp.initfunc.int_v[chp.initfunc.int_n - 1] = 0;

                        if (*sk != ')') {
                            _PARSEERROR_NOARGS("init function only takes two arguments");
                        }
                        sk++;

                        while (*sk == ' ') sk++;

                        if (*sk != '{') {
                            _PARSEERROR_NOARGS("was expecting a '{' to indicate start of method\n");
                        }
                        sk++;
                        if (strlen(sk) > 0) {
                            _PARSEERROR_NOARGS("leftover characters!\n");
                        }

                    } else {
                        _PARSEERROR("unknown function '%s'", tmp);
                    }

                } else {
                    if (2 == sscanf(sk, "%s = %s", tmp, tmp2)) {
                        // we have an assignment
                        printf("'%s'='%s'\n", tmp, tmp2);
                       chast_d_t *lhs, *rhs;
                       chast_d_t *assign = malloc(sizeof(chast_d_t))
                    } else {
                        _PARSEERROR_NOARGS("wasn't expecting this");
                    }
                }
            } else if (method_in < 0) {
                // global variable declarations

                sk += strlen(starting_type);
                // skip spaces
                while (*sk == ' ') sk++;
                if (*sk != '@') {
                    _PARSEERROR_NOARGS("all variables defined outside of a method must begin with '@'");
                }
                sk++;
                int i = 0;
                while (ISALPHA(*sk)) {
                    tmp[i++] = *sk;
                    sk++;
                }
                tmp[i] = '\0';
                if (*sk != ';') {
                    _PARSEERROR_NOARGS("was expecting a ';' right after the variable name");
                }

                chp.globals.int_n++;
                chp.globals.int_k = realloc(chp.globals.int_k, sizeof(char *) * chp.globals.int_n);
                chp.globals.int_v = realloc(chp.globals.int_v, sizeof(int) * chp.globals.int_n);
                chp.globals.int_k[chp.globals.int_n - 1] = malloc(strlen(tmp) + 1);
                strcpy(chp.globals.int_k[chp.globals.int_n - 1], tmp);
                chp.globals.int_v[chp.globals.int_n - 1] = 0;
            } else {
                _PARSEERROR_NOARGS("uncaught syntax error");
            }
 
        }

        // go through other lines
        line = strtok(0, delim);
    }

    return chp;    

}



/*

AST library

*/

double chast_d_val(chast_d_t * node, int N, char ** keys, double * vals) {
    if (node->op == COP_NONE) {
        return node->val;
    } else if (node->op == COP_DICTSET_AVAL) {
        // set the dictionary entry of 'tag' to the value of A
        if (node->tag == NULL) return 0.0;
        double A_v = chast_d_val(node->A, N, keys, vals);
        // simple lookup
        int i; 
        for (i = 0; i < N; ++i) {
            if (strcmp(node->tag, keys[i]) == 0) {
                vals[i] = A_v;
            }
        }
        return A_v;
    } else if (node->op == COP_DICTGET) {
        if (node->tag == NULL) return 0.0;
        // simple lookup
        int i; 
        for (i = 0; i < N; ++i) {
            if (strcmp(node->tag, keys[i]) == 0) {
                return vals[i];
            }
        }
        return 0.0;
    } else {
        double A_v = chast_d_val(node->A, N, keys, vals);
        double B_v = chast_d_val(node->B, N, keys, vals);
        if (node->op == COP_ADD) {
            return A_v + B_v;
        } else if (node->op == COP_SUB) {
            return A_v - B_v;
        } else if (node->op == COP_MUL) {
            return A_v * B_v;
        } else if (node->op == COP_DIV) {
            return A_v / B_v;
        } else {
            printf("ERROR: unknown operation\n");
            return 0.0;
        }
    }
}

