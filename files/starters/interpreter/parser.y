%{
/* CS374 Interpreter assignment: the Scheme grammar.
   A program is a sequence of data, and each one is evaluated as soon as it is read. */
#include <stdio.h>
#include <stdlib.h>
#include "scheme.h"

int yylex(void);
void yyerror(const char *message) { fprintf(stderr, "error: %s\n", message); exit(1); }
%}

%union {
    double number;
    char *text;
    Value *value;
}

%token <number> NUMBER_LITERAL
%token <text>   SYMBOL_LITERAL
%token TRUE_LITERAL FALSE_LITERAL
%type  <value>  datum items

%%

program:
      /* nothing */
    | program datum         { Value *result = eval($2, global_env());
                              if (result != NULL) { print_value(result); printf("\n"); } }
    ;

datum:
      NUMBER_LITERAL        { $$ = make_number($1); }
    | SYMBOL_LITERAL        { $$ = make_symbol($1); }
    | TRUE_LITERAL          { $$ = make_boolean(1); }
    | FALSE_LITERAL         { $$ = make_boolean(0); }
    | '(' items ')'         { $$ = $2; }
    ;

items:
      /* nothing */         { $$ = nil(); }
    | datum items           { $$ = cons($1, $2); }
    ;

%%
