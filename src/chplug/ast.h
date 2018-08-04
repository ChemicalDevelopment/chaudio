/*

basic ast library

*/


#ifndef __AST_H__
#define __AST_H__

#include <stdbool.h>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>

// types
typedef enum _ast_type { AST_TYPE_INT, AST_TYPE_DOUBLE, AST_TYPE_FUNCTION, AST_TYPE_NULL } ast_type;

typedef enum _ast_op {
    U_VAL, // this is special case, and if this is set, vals should == NULL, and instead, use .val in the union
    U_LOOKUP, // special lookup case, use .symbol union

    BIN_ASSIGN, // assigns

    BIN_ADD, BIN_SUB, BIN_MUL, BIN_DIV, // use .subtree union

    // call it on a function
    VAR_FUNC // use .callable in the union

} ast_op; 

// value store
typedef struct _ast_val {

    ast_type type;

    // used for all array types
    union {
        int _int;
        double _double;

        struct {
            int num;
            double * data;
        } _double_array;

        struct _ast_val (*_function)(int, struct _ast_val *);

        void * _null;
    } val;

} ast_val_t;

typedef ast_val_t (*ast_C_function)(int params_num, ast_val_t * params);

#define AST_VAL_NULL ((ast_val_t) { .type = AST_TYPE_NULL })

// callable
typedef struct _ast_function {
/*
    struct {
        int num;
        // ordered array of types
        ast_type * types;
    } signature;
*/

    ast_C_function call;
    
} ast_function_t;

// abstract syntax tree

typedef struct _ast {
    // BIN_ = binary (so 2 vals), U_ = unary (so 1 val)
    ast_op op;

    union {
        // used for BIN_ operations
        struct {
            int num;
            struct _ast * nodes;

        } subtree;

        struct {
            ast_val_t func;

            int num_params;
            struct _ast * params;
        } callable;

        // used for U_VAL
        ast_val_t val;

        // used for U_LOOKUP
        char * symbol;

    } data;

} ast_t;

#define AST_NULL ((ast_t) { .op = U_VAL , .data = { .val = AST_VAL_NULL } })

typedef struct _ast_dict {

    int num;

    char ** keys;
    ast_t * vals;

} ast_dict_t;


ast_dict_t ast_dict_create();

bool ast_dict_contains(ast_dict_t * d, char * key);

void ast_dict_set(ast_dict_t * d, char * key, ast_t val);
ast_t ast_dict_get(ast_dict_t * d, char * key);
void ast_dict_dump(ast_dict_t * d);




ast_t ast_val(int type, void * val);

ast_t ast_val_create(ast_val_t val);

// easier ways to do it
ast_t ast_val_double(double val);
// special for function
ast_t ast_val_function(ast_C_function val);

ast_t ast_lookup(char * symbol);
ast_t ast_assign(char * symbol, ast_t v);

ast_t ast_uop(int op, ast_t v);

ast_t ast_binop(int op, ast_t l, ast_t r);

// represent a function call
ast_t ast_func(ast_t func, int num_params, ast_t * params);


typedef struct _ast_eval_stats {

    int maximum_recursion;
    int evals_called;

} ast_eval_stats_t;

ast_val_t ast_eval(ast_t v, ast_dict_t * lookup, ast_eval_stats_t * stats, int * err);

#endif

