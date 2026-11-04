%{
/* CS374 Parser assignment, Part 2: the calculator's grammar.
   Every action computes its value directly, with no tree. */
#include <stdio.h>
#include <stdlib.h>

int yylex(void);
void yyerror(const char *message) { fprintf(stderr, "error: %s\n", message); }
%}

%union {
    double number;
}

%token <number> NUM
%type  <number> expr term factor

%%

input:
      /* nothing */
    | input line
    ;

line:
      '\n'
    | expr '\n'             { printf("%g\n", $1); }
    ;

expr:
      expr '+' term         { $$ = $1 + $3; }
    /* TODO: subtraction */
    | term                  { $$ = $1; }
    ;

term:
      /* TODO: multiplication and division */
      factor                { $$ = $1; }
    ;

factor:
      NUM                   { $$ = $1; }
    /* TODO: parentheses */
    ;

%%

int main(void) {
    return yyparse();
}
