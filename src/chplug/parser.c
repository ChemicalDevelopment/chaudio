
#include "ast.h"
#include "lex.h"
#include "parser.h"
#include <stdio.h>
#include <stdlib.h>


int _op_precedence(ast_op op) {
    if (op == BIN_ADD || op == BIN_SUB) {
        return 10;
    } else if (op == BIN_MUL || op == BIN_DIV) {
        return 20;
    } else if (op == BIN_ASSIGN) {
        return 100;
    } else {
        printf("ast: unknown op! (%d)\n", op);
        return 0;
    }
}

ast_t ast_parse_expr(char ** _line) {
#define line (*_line)
    struct {
        int num;
        token_t * tokens;
    } operator_stack = {
        .num = 0,
        .tokens = NULL
    };

    struct {
        int num;
        ast_t * nodes;
    } output_queue = {
        .num = 0,
        .nodes = NULL
    };

    token_t t;

    while ((t = token_read(&line)).type != TOKEN_EOF && t.type != TOKEN_SEMICOLON) {
        if (t.type == TOKEN_NEWLINE) {
            continue; // skip
        } else if (t.type == TOKEN_CONST_DOUBLE) {
            output_queue.num++; output_queue.nodes = realloc(output_queue.nodes, sizeof(ast_t) * output_queue.num);
            output_queue.nodes[output_queue.num - 1] = ast_val_double(t.data.const_double);
        } 
         
        else if (t.type == TOKEN_NAME) {
            // TODO: detect if it's a function somehow, probably look at the stack if its a left parenthesis
            output_queue.num++; output_queue.nodes = realloc(output_queue.nodes, sizeof(ast_t) * output_queue.num);
            output_queue.nodes[output_queue.num - 1] = ast_lookup(t.data.name);
        } 
        else if (t.type == TOKEN_OP || t.type == TOKEN_ASSIGN) {
            while (operator_stack.num > 0 && (operator_stack.tokens[operator_stack.num - 1].type == TOKEN_OP || operator_stack.tokens[operator_stack.num - 1].type == TOKEN_ASSIGN) && (/* TODO: FUNCTION */ _op_precedence(operator_stack.tokens[operator_stack.num - 1].data.op) == _op_precedence(t.data.op) )) {
                ast_op cur_op = operator_stack.tokens[operator_stack.num - 1].data.op;
                ast_t LHS = output_queue.nodes[output_queue.num - 2], RHS = output_queue.nodes[output_queue.num - 1];

                output_queue.num -= 2;
                operator_stack.num -= 1;

                ast_t joined = ast_binop(cur_op, LHS, RHS);

                output_queue.num += 1;
                output_queue.nodes[output_queue.num - 1] = joined;
            }
            operator_stack.num++;
            operator_stack.tokens = realloc(operator_stack.tokens, operator_stack.num * sizeof(token_t));
            operator_stack.tokens[operator_stack.num - 1] = t;
        } else if (t.type == TOKEN_LPAREN) {
            operator_stack.num++;
            operator_stack.tokens = realloc(operator_stack.tokens, operator_stack.num * sizeof(token_t));
            operator_stack.tokens[operator_stack.num - 1] = t;
        } else if (t.type == TOKEN_RPAREN) {
            //TODO: check for parenthesis mismatch
            while (operator_stack.num > 0 && (operator_stack.tokens[operator_stack.num - 1].type != TOKEN_LPAREN)) {
                ast_op cur_op = operator_stack.tokens[operator_stack.num - 1].data.op;
                ast_t LHS = output_queue.nodes[output_queue.num - 2], RHS = output_queue.nodes[output_queue.num - 1];

                output_queue.num -= 2;
                operator_stack.num -= 1;

                ast_t joined = ast_binop(cur_op, LHS, RHS);

                output_queue.num += 1;
                output_queue.nodes[output_queue.num - 1] = joined;
            }

            operator_stack.num--;
        } else {
            printf("ast: unhandled token! (%d)\n", t.type);
        }
    }

    while (operator_stack.num > 0) {
        ast_op cur_op = operator_stack.tokens[operator_stack.num - 1].data.op;
        ast_t LHS = output_queue.nodes[output_queue.num - 2], RHS = output_queue.nodes[output_queue.num - 1];

        output_queue.num -= 2;
        operator_stack.num--;

        ast_t joined = ast_binop(cur_op, LHS, RHS);

        output_queue.num += 1;
        output_queue.nodes[output_queue.num - 1] = joined;
    }

    if (output_queue.num != 1) {printf("ast: for some reason the output queue had .num != 1 (num==%d) '%s'\n", output_queue.num, line);
    }

#undef line
    return output_queue.nodes[0];
}



ast_program_t ast_parse(char * line) {

    ast_program_t r;

    r.dict = ast_dict_create();
    r.instructions.num = 0;
    r.instructions.nodes = NULL;

    token_t t;

    while ((t = token_peek(line)).type != TOKEN_EOF) {

        if (t.type == TOKEN_TYPE) {
            // consume the type
            t = token_read(&line);

            char * before_name = line;
            token_t name = token_read(&line);

            if (name.type != TOKEN_NAME) {
                printf("expected name after type\n");
            } else {
                
                if (t.data.type == AST_TYPE_DOUBLE) {
                    ast_dict_set(&r.dict, name.data.name, ast_val_double(0.0));
                } else {
                    printf("ast: unknown type! (%d)\n", t.data.type);
                }

                token_t semicolon_or_assign = token_peek(line);

                if (semicolon_or_assign.type == TOKEN_SEMICOLON) {
                    // consume it
                    token_read(&line);
                } else if (semicolon_or_assign.type == TOKEN_ASSIGN) {
                    line = before_name;
                    r.instructions.num++; r.instructions.nodes = realloc(r.instructions.nodes, sizeof(ast_t) * r.instructions.num);
                    r.instructions.nodes[r.instructions.num - 1] = ast_parse_expr(&line);
                } else {
                    printf("ast: expected ';' or '=' after variable declaration\n");
                }
            }
        } else if (t.type == TOKEN_NAME) {
            // dont consume here, because its just an expr
            //t = token_read(&line);
            r.instructions.num++; r.instructions.nodes = realloc(r.instructions.nodes, sizeof(ast_t) * r.instructions.num);
            r.instructions.nodes[r.instructions.num - 1] = ast_parse_expr(&line);
        } else {
            printf("UNHANDLED!\n");
        }
    }
    return r;
}

