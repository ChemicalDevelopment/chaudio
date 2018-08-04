
#include "ast.h"
#include "parser.h"


ast_dict_t ast_dict_create() {
    ast_dict_t r;
    r.num = 0;
    r.keys = NULL;
    r.vals = NULL;
    return r;
}

int _ast_dict_idx(ast_dict_t * d, char * key) {
    int i;
    for (i = 0; i < d->num; ++i) {
        if (strcmp(key, d->keys[i]) == 0) return i;
    }
    return -1;
}

void ast_dict_set(ast_dict_t * d, char * key, ast_t val) {
    int idx = _ast_dict_idx(d, key);
    if (idx < 0) {
        d->num++;
        d->keys = realloc(d->keys, sizeof(char *) * d->num);
        d->vals = realloc(d->vals, sizeof(ast_t) * d->num);
        idx = d->num - 1;
        d->keys[idx] = malloc(strlen(key) + 1);
        strcpy(d->keys[idx], key);
    }
    d->vals[idx] = val;
}

bool ast_dict_contains(ast_dict_t * d, char * key) {
    return _ast_dict_idx(d, key) >= 0;
}

ast_t ast_dict_get(ast_dict_t * d, char * key) {
    int idx = _ast_dict_idx(d, key);
    if (idx < 0) {
        return AST_NULL;
    } else {
        return d->vals[idx];
    }
}


void ast_dict_dump(ast_dict_t * d) {
    int i;
    for (i = 0; i < d->num; ++i) {
        printf("'%s'=", d->keys[i]);
        ast_t v = d->vals[i];
        if (v.op == U_VAL) {
            ast_val_t vv = v.data.val;
            if (vv.type == AST_TYPE_DOUBLE) {
                printf("<double>%lf", vv.val._double);
            } else {
                printf("<other type>");
            }
        } else {
            printf("(AST)");
        }

        printf("\n");
    }
}

ast_val_t _ast_val_create(int type, void * val) {
    ast_val_t r;
    r.type = type;
    r.val._null = NULL;
    if (type == AST_TYPE_DOUBLE) {
        r.val._double = *(double *)val;
    } else if (type == AST_TYPE_INT) {
        r.val._int = *(int *)val;
    } else {
        printf("Unknown type: '%d'\n", type);
    }
    return r;
}

ast_val_t _ast_val_function_create(ast_C_function val) {
    ast_val_t r;
    r.type = AST_TYPE_FUNCTION;
    r.val._function = val;
    return r;
}

ast_t ast_val(int type, void * val) {
    ast_t r;
    r.op = U_VAL;
    r.data.val = _ast_val_create(type, val);
    return r;
}
ast_t ast_val_create(ast_val_t val) {
    ast_t r;
    r.op = U_VAL;
    r.data.val = val;
    return r;
}

ast_t ast_val_double(double val) {
    return ast_val(AST_TYPE_DOUBLE, &val);
}

// lookup for variables
ast_t ast_lookup(char * symbol) {
    ast_t r;
    r.op = U_LOOKUP;
    r.data.symbol = malloc(strlen(symbol) + 1);
    strcpy(r.data.symbol, symbol);
    return r;
}


ast_t ast_assign(char * symbol, ast_t v) {
    ast_t r;
    r.op = BIN_ASSIGN;
    r.data.subtree.num = 2;
    r.data.subtree.nodes[0] = ast_lookup(symbol);
    r.data.subtree.nodes[1] = v;
    return r;
}

ast_t ast_val_function(ast_C_function val) {
    ast_t r;
    r.op = U_VAL;
    r.data.val = _ast_val_function_create(val);
    return r;
}


ast_t ast_binop(int op, ast_t left, ast_t right) {
    ast_t r;
    r.op = op;
    r.data.subtree.num = 2;    
    r.data.subtree.nodes = malloc(2 * sizeof(ast_t));
    r.data.subtree.nodes[0] = left;
    r.data.subtree.nodes[1] = right;
    return r;
}

ast_t ast_uop(int op, ast_t v) {
    ast_t r;
    r.op = op;
    if (op == U_VAL) {
        r.data.val = v.data.val;
    } else {
        printf("Invalid unary operator: %d\n", op);
    }
    return r;
}


#define _RECURSE(myv) _ast_eval_recurse(myv, lookup, stats, level, err); if (*err != 0) return AST_VAL_NULL;
ast_val_t _ast_eval_recurse(ast_t v, ast_dict_t * lookup, ast_eval_stats_t * stats, int level, int * err) {
    //printf("eval\n");
    level++;
    stats->evals_called++;
    if (level > stats->maximum_recursion) stats->maximum_recursion = level;
    if (v.op == U_VAL) {
        return v.data.val;
    } else if (v.op == U_LOOKUP) {
        ast_val_t r = _RECURSE(ast_dict_get(lookup, v.data.symbol));
        return r;
    } else if (v.op == BIN_ADD) {
        ast_val_t Lval = _RECURSE(v.data.subtree.nodes[0]); ast_val_t Rval = _RECURSE(v.data.subtree.nodes[1]);
        ast_val_t r; r.type = AST_TYPE_DOUBLE; r.val._double = Lval.val._double + Rval.val._double;
        return r;
    } else if (v.op == BIN_SUB) {
        ast_val_t Lval = _RECURSE(v.data.subtree.nodes[0]); ast_val_t Rval = _RECURSE(v.data.subtree.nodes[1]);
        ast_val_t r; r.type = AST_TYPE_DOUBLE; r.val._double = Lval.val._double - Rval.val._double;
        return r;
    } else if (v.op == BIN_MUL) {
        ast_val_t Lval = _RECURSE(v.data.subtree.nodes[0]); ast_val_t Rval = _RECURSE(v.data.subtree.nodes[1]);
        ast_val_t r; r.type = AST_TYPE_DOUBLE; r.val._double = Lval.val._double * Rval.val._double;
        return r;
    } else if (v.op == BIN_DIV) {
        ast_val_t Lval = _RECURSE(v.data.subtree.nodes[0]); ast_val_t Rval = _RECURSE(v.data.subtree.nodes[1]);
        ast_val_t r; r.type = AST_TYPE_DOUBLE; r.val._double = Lval.val._double / Rval.val._double;
        return r;
    } else if (v.op == BIN_ASSIGN) {
        ast_val_t res = _RECURSE(v.data.subtree.nodes[1]);
        ast_t assign_to = v.data.subtree.nodes[0];
        if (assign_to.op != U_LOOKUP) {
            printf("ast: trying to assign to something that is not a lookup!\n");
            *err = 1;
        }
        
        ast_dict_set(lookup, assign_to.data.symbol, ast_val_create(res));
        return res;
    } else if (v.op == VAR_FUNC) {
        ast_val_t func = v.data.callable.func;
        int num_params = v.data.callable.num_params;
        ast_val_t * params = malloc(sizeof(ast_val_t) * num_params);
        int i;
        for (i = 0; i < num_params; ++i) {
            params[i] = _RECURSE(v.data.callable.params[i]);
        }
        ast_val_t result = func.val._function(num_params, params);
        if (params != NULL) free(params);
        return result;
    } else {
        printf("ast: invalid op %d\n", v.op);
        *err = 1;
        return AST_VAL_NULL;
    }
}

ast_val_t ast_eval(ast_t v, ast_dict_t * lookup, ast_eval_stats_t * stats, int * err) {
    stats->maximum_recursion = 0;
    stats->evals_called = 0;
    int my_err = 0; 
    ast_val_t r = _ast_eval_recurse(v, lookup, stats, 0, &my_err);
    if (err != NULL) *err = my_err;
    return r;
}


ast_t ast_func(ast_t func, int num_params, ast_t * params) {
    ast_t r;
    r.op = VAR_FUNC;
    if (func.data.val.type != AST_TYPE_FUNCTION) {
        printf("error: argument to 'ast_func' should be VAR_FUNC\n");
    }
    r.data.callable.func = func.data.val;
    r.data.callable.num_params = num_params;
    r.data.callable.params = malloc(sizeof(ast_t) * num_params);
    memcpy(r.data.callable.params, params, sizeof(ast_t) * num_params);
    
    return r;
}


void ast_run_program(ast_program_t * prg) {
    int i;
    int err = 0;
    for (i = 0; i < prg->instructions.num; ++i) {
        ast_eval_stats_t stats;
        ast_eval(prg->instructions.nodes[i], &prg->dict, &stats, &err);
        if (err != 0) printf("error!\n");
    }
}

