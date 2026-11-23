%{
/* tiny.l - the scanner for tiny.y, written in flex instead of by hand */
#include <stdio.h>
#include <stdlib.h>
#include "tiny.tab.h"
%}
%option noyywrap noinput nounput
%%
[0-9]+     { yylval = atoi(yytext); return NUM; }
[+*\n]     { return yytext[0]; }
[ \t]+     { /* skip blanks */ }
.          { fprintf(stderr, "unexpected character: %s\n", yytext); }
%%
