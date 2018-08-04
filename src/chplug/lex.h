


#ifndef __LEX_H__
#define __LEX_H__


#include "ast.h"

typedef struct _token {

    enum { TOKEN_TYPE, TOKEN_NAME, TOKEN_ASSIGN, TOKEN_CONST_INT, TOKEN_CONST_DOUBLE, TOKEN_OP, TOKEN_SEMICOLON, TOKEN_LPAREN, TOKEN_RPAREN, TOKEN_NEWLINE, TOKEN_EOF, TOKEN_ERROR } type;

    union {

        ast_type type;

        char * name;

        double const_double;

        int const_int;

        ast_op op;

    } data;

} token_t;

token_t token_peek(char * _line);

token_t token_read(char ** line);

#endif
