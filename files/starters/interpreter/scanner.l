%{
/* CS374 Interpreter assignment: the Scheme scanner. */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "scheme.h"
#include "parser.tab.h"
%}

%option noyywrap noinput nounput

%%

;[^\n]*                 { /* a comment runs to the end of the line */ }
[ \t\n]+                { /* skip whitespace */ }
"("                     { return '('; }
")"                     { return ')'; }
#t                      { return TRUE_LITERAL; }
#f                      { return FALSE_LITERAL; }
-?[0-9]+(\.[0-9]+)?     { yylval.number = atof(yytext); return NUMBER_LITERAL; }
[^ \t\n()';]+           { yylval.text = strdup(yytext); return SYMBOL_LITERAL; }
.                       { fprintf(stderr, "unexpected character: %s\n", yytext); exit(1); }

%%
