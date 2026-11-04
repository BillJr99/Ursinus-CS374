/* CS374 Interpreter assignment: the scanner.  This file is complete. */
%option noyywrap noinput nounput yylineno
%{
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "ast.h"
#include "parser.tab.h"
%}
%%
[ \t\n]+                  { /* skip whitespace */ }
#[^\n]*                   { /* skip a comment */ }
[0-9]+(\.[0-9]+)?         { yylval.num = atof(yytext); return NUM; }
"let"                     { return LET; }
"print"                   { return PRINT; }
"if"                      { return IF; }
"else"                    { return ELSE; }
"while"                   { return WHILE; }
"break"                   { return BREAK; }
"continue"                { return CONTINUE; }
"true"                    { return TRUE; }
"false"                   { return FALSE; }
"and"                     { return AND; }
"or"                      { return OR; }
"not"                     { return NOT; }
[A-Za-z_][A-Za-z0-9_]*    { yylval.name = strdup(yytext); return ID; }
"<="                      { return LE; }
">="                      { return GE; }
"=="                      { return EQEQ; }
"!="                      { return NE; }
[-+*/<>=;(){}]            { return yytext[0]; }
.                         { printf("Lexical error at line %d: unexpected character '%s'\n", yylineno, yytext); exit(1); }
%%
