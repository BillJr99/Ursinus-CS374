%{
/* CS374 Parser assignment, Part 2: the calculator's scanner.
   This file is complete for Part 2.  Part 3 adds two rules. */
#include <stdio.h>
#include <stdlib.h>
#include "calc.tab.h"
%}

%option noyywrap noinput nounput

%%

[0-9]+      { yylval.number = atof(yytext); return NUM; }
[-+*/()\n]  { return yytext[0]; }
[ \t]+      { /* skip spaces and tabs */ }
.           { fprintf(stderr, "unexpected character: %s\n", yytext); exit(1); }

%%
