
#ifndef __PARSER_H__
#define __PARSER_H__

#include "ast.h"


/*

holds all info neccesary to execute it

*/

typedef struct _ast_program {

    ast_dict_t dict;

    struct {

        int num;
        ast_t * nodes;

    } instructions;

} ast_program_t;

ast_program_t ast_parse(char * line);

void ast_run_program(ast_program_t * prg);


#endif

