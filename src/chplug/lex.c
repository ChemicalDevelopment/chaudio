#include "lex.h"
#include <string.h>
#include <stdio.h>
#include <ctype.h>



token_t token_peek(char * _line) {
    token_t r;

    char ** _tmp_line = malloc(sizeof(char *));
    *_tmp_line = _line;

    r = token_read(_tmp_line);

    free(_tmp_line);
    return r;
}



token_t token_read(char **_line) {

#define line (*_line)
    while (*line == ' ') line++; 

    token_t r;

    if (*line == '\0') {
        r.type = TOKEN_EOF;
        return r;
    }
    //printf("'%s'\n", line);

    if (isalpha(*line)) {
        int i = 0;
        while (isalpha(line[i])) {
            i++;
        }

        if (strncmp(line, "double", strlen("double")) == 0) {
            r.type = TOKEN_TYPE;
            r.data.type = AST_TYPE_DOUBLE;
        } else {
            r.type = TOKEN_NAME;
            r.data.name = malloc(i + 1);
            strncpy(r.data.name, line, i);
            r.data.name[i] = '\0';
        }

        line += i;

        return r;
    } else if (*line == '=' && (line[1] == '\0' || line[1] != '=')) {
        // assign (NOT double equals)
        line += 1;
        r.type = TOKEN_ASSIGN;
        r.data.op = BIN_ASSIGN;
        return r;

    } else if (*line == '.' || (*line >= '0' && *line <= '9')) {
        bool has_had_period = false;
        int i = 0;
        while (line[i] != '\0' && ((line[i] == '.' && !has_had_period) || (line[i] >= '0' && line[i] <= '9'))) {
            if (line[i] == '.') has_had_period = true;
            i++;
        }
        if (has_had_period) {
            // double
            double d;
            sscanf(line, "%lf", &d);
            r.type = TOKEN_CONST_DOUBLE;
            r.data.const_double = d;
        } else {
            // int
            int j;
            int result = 0;
            for (j = 0; j < i; ++j) {
                result *= 10;
                result += line[j] - '0';
            }
            r.type = TOKEN_CONST_INT;
            r.data.const_int = result;
        }
        line += i;
        return r;
    } else if (*line == '+') {
        line += 1;
        r.type = TOKEN_OP;
        r.data.op = BIN_ADD;
        return r;
    } else if (*line == '-') {
        line += 1;
        r.type = TOKEN_OP;
        r.data.op = BIN_SUB;
        return r;
    } else if (*line == '*') {
        line += 1;
        r.type = TOKEN_OP;
        r.data.op = BIN_MUL;
        return r;
    } else if (*line == '/') {
        line += 1;
        r.type = TOKEN_OP;
        r.data.op = BIN_DIV;
        return r;
    } else if (*line == '=') {
        line += 1;
        r.type = TOKEN_OP;
        r.data.op = BIN_ASSIGN;
        return r;
    } else if (*line == '(') {
        line += 1;
        r.type = TOKEN_LPAREN;
        return r;
    } else if (*line == ')') {
        line += 1;
        r.type = TOKEN_RPAREN;
        return r;
    } else if (*line == '\n') {
        line += 1;
        r.type = TOKEN_NEWLINE;
        return r;
    } else if (*line == ';') {
        line += 1;
        r.type = TOKEN_SEMICOLON;
        return r;
    } else {
        printf("ast: error parsing '%s'\n", line);
        r.type = TOKEN_ERROR;
        return r;
    }
#undef line
}

