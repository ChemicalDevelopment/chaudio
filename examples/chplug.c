

#include "chplug/chplug.h"

#include "chplug/ast.h"
#include "chaudio.h"

#include "chplug/lex.h"
#include "chplug/parser.h"

#include <stdio.h>
#include <stdlib.h>

#include <math.h>

ast_val_t ast_sqrt(int params_num, ast_val_t * params) {
    if (params_num != 1) {
        printf("sqrt() expected 1 parameter!\n");
    }
    ast_val_t r;
    r.type = AST_TYPE_DOUBLE;
    r.val._double = sqrt(params[0].val._double);
    return r;
}


// basic shunting yard algorithm
ast_t ast_parse_shuntingyard(char ** line) {
    token_t t;
    int output_num = 0;
    ast_t * output_stack = NULL;

    int operator_num = 0;
    token_t * operator_stack = NULL;
    while ((t = token_read(line)).type != TOKEN_EOF && t.type != TOKEN_SEMICOLON) {
        if (t.type == TOKEN_CONST_DOUBLE) {
            output_num++;
            output_stack = realloc(output_stack, sizeof(ast_t) * output_num);
            output_stack[output_num - 1] = ast_val_double(t.data.const_double);
        } else if (t.type == TOKEN_OP) {
            // we have an operator
            while (operator_num > 0) {
                operator_num--;
                token_t oper = operator_stack[operator_num];

                ast_t RHS = output_stack[output_num - 1], LHS = output_stack[output_num - 2];
                output_num--;
                output_stack[output_num - 1] = ast_binop(oper.data.op, LHS, RHS);
            }
            operator_num++;
            operator_stack = realloc(operator_stack, sizeof(token_t) * operator_num);
            operator_stack[operator_num - 1] = t;
        } else if (t.type == TOKEN_LPAREN) {
            operator_num++;
            operator_stack = realloc(operator_stack, sizeof(token_t) * operator_num);
            operator_stack[operator_num - 1] = t;
        } else if (t.type == TOKEN_RPAREN) {
            while (true) {
                if (operator_num == 0) {
                    printf("unbalanced parens!\n");
                    return AST_NULL;
                }

                token_t cur_op = operator_stack[operator_num - 1];
                operator_num--;

                if (cur_op.type == TOKEN_LPAREN) {
                    break;
                }

                if (output_num < 2) {
                    printf("WEIRD\n");
                    return AST_NULL;
                }

                ast_t RHS = output_stack[output_num - 1], LHS = output_stack[output_num - 2];

                output_num--;

                output_stack[output_num - 1] = ast_binop(cur_op.type, LHS, RHS);
            }

        } else {
            printf("UNHANDLED CASE in SHUNTINGYARD\n");
        }
    }
    while (operator_num > 0) {
        operator_num--;
        if (operator_stack[operator_num].type == TOKEN_LPAREN) {
            printf("unbalanced parens!\n");
        }

        ast_t RHS = output_stack[output_num - 1], LHS = output_stack[output_num - 2];
        output_num--;
        output_stack[output_num - 1] = ast_binop(operator_stack[operator_num].data.op, LHS, RHS);
    }

    if (output_num != 1) printf("IDK\n");
    printf("%d\n", output_num);
    return *output_stack; 
}

int main(int argc, char ** argv) {
    /*
    char * fname = "./gain.chplug";
    printf("chplug example: %s\n", fname);

    chplug_t gain = chplug_create(fname);
    if (gain.status != 0) {
        printf("failed to create the plugin!\n");
    }

    int i;
    for (i = 0; i < gain.globals.int_n; ++i) {
        printf("@'%s' = '%d'\n", gain.globals.int_k[i], gain.globals.int_v[i]);
    }*/
   // printf("source: \n%s\n", gain.src);


    /*

    X = (A + B) * C
    Y = sqrt(X)

    */

    ast_eval_stats_t stats;


/*
    ast_t sqrt_func = ast_val_function(ast_sqrt);

    ast_t X = ast_binop(BIN_MUL, ast_binop(BIN_ADD, ast_lookup("A"), ast_lookup("B")), ast_lookup("C"));

    ast_t assign_Y = ast_assign("Y", ast_func(sqrt_func, 1, &X));
    
    ast_dict_set(&lookup, "A", ast_val_double(2.0));
    ast_dict_set(&lookup, "B", ast_val_double(3.0));
    ast_dict_set(&lookup, "C", ast_val_double(1.5));


    double res = ast_eval(assign_Y, &lookup, &stats).val._double;
    
    printf("evals called: %d, max recursion: %d\n", stats.evals_called, stats.maximum_recursion);

*/
    ast_program_t parsed = ast_parse("double cade = 1.0; double brown = 2.0; cade = 5.0;");

    ast_run_program(&parsed);

    ast_val_t cade_val = ast_eval(ast_dict_get(&parsed.dict, "cade"), &parsed.dict, &stats, NULL);
    
    printf("'cade': %lf\n", cade_val.val._double);
    printf("(stats: evals: %d, recursion: %d)\n", stats.evals_called, stats.maximum_recursion);

    ast_dict_dump(&parsed.dict);

}

