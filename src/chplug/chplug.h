/*

chplug.h -- basic plugin language

*/


#ifndef __CHPLUG_H__
#define __CHPLUG_H__


// AST tree for `double` (d)
typedef struct _chdast_d_s {

#define COP_NONE 0x0
#define COP_VALUE COP_NONE
#define COP_ADD 0x1
#define COP_SUB 0x2
#define COP_MUL 0x3
#define COP_DIV 0x4

// get the value from the dictionary
#define COP_DICTGET 0x101
#define COP_DICTSET_AVAL 0x102
// what operator to do with 'other->val'
    int op;

// if both NULL,or op == COP_NONE, use .val instead
    struct _chdast_d_s * A, * B;

    double val;

    char * tag;

} chast_d_t;

/*
ex:
// constants
chast_d_t C_1, C_2;
C_1.op = COP_NONE; // or COP_VALUE
C_2.op = COP_NONE;
C_1.val = 1.0;
C_2.val = 2.0;

chast_d_t added;
added.op = COP_ADD;
added.A = &C_1;
added.B = &C_2;

printf("val(added)=%lf\n", chast_d_val(added));

*/


typedef struct chplug_t {

    char * src;

    // to traverse with strtok
    char * trav;

    int status;

    struct {

        int int_n;
        char ** int_k;
        int * int_v;

    } globals;

    struct {

        // all registered int variables
        char int_n;
        char ** int_k;
        int * int_v;

    } initfunc;

} chplug_t;

chplug_t chplug_create(char * filename);

// dictionary params
double chast_d_val(chast_d_t * node, int N, char ** keys, double * vals);

#endif

