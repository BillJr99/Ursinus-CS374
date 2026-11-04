/* CS374 Interpreter assignment: the parser.  This file is complete. */
%{
#include <stdio.h>
#include <stdlib.h>
#include "ast.h"
extern int yylineno;
int yylex(void);
void yyerror(const char *message) {
    (void) message;
    printf("Syntax error at line %d\n", yylineno);
    exit(1);
}
%}
%union { double num; char *name; struct Node *node; }
%token <num> NUM
%token <name> ID
%token LET PRINT IF ELSE WHILE BREAK CONTINUE TRUE FALSE AND OR NOT LE GE EQEQ NE
%type <node> stmts stmt block if_stmt expr or_expr and_expr not_expr comparison addsub muldiv unary primary
%%
program    : stmts                       { program = $1; }
           ;
stmts      : /* empty */                 { $$ = NULL; }
           | stmts stmt                  { $$ = append_stmt($1, $2); }
           ;
stmt       : LET ID '=' expr ';'         { $$ = new_name(N_LET, $2, $4, $4->line); }
           | ID '=' expr ';'             { $$ = new_name(N_ASSIGN, $1, $3, $3->line); }
           | PRINT expr ';'              { $$ = new_kids(N_PRINT, $2, NULL, NULL, $2->line); }
           | if_stmt                     { $$ = $1; }
           | WHILE expr block            { $$ = new_kids(N_WHILE, $2, $3, NULL, $2->line); }
           | BREAK ';'                   { $$ = new_node(N_BREAK, yylineno); }
           | CONTINUE ';'                { $$ = new_node(N_CONTINUE, yylineno); }
           | block                       { $$ = $1; }
           ;
if_stmt    : IF expr block               { $$ = new_kids(N_IF, $2, $3, NULL, $2->line); }
           | IF expr block ELSE block    { $$ = new_kids(N_IF, $2, $3, $5, $2->line); }
           | IF expr block ELSE if_stmt  { $$ = new_kids(N_IF, $2, $3, $5, $2->line); }
           ;
block      : '{' stmts '}'               { $$ = new_kids(N_BLOCK, $2, NULL, NULL, yylineno); }
           ;
expr       : or_expr                     { $$ = $1; }
           ;
or_expr    : and_expr                    { $$ = $1; }
           | or_expr OR and_expr         { $$ = new_kids(N_OR, $1, $3, NULL, yylineno); }
           ;
and_expr   : not_expr                    { $$ = $1; }
           | and_expr AND not_expr       { $$ = new_kids(N_AND, $1, $3, NULL, yylineno); }
           ;
not_expr   : comparison                  { $$ = $1; }
           | NOT not_expr                { $$ = new_kids(N_NOT, $2, NULL, NULL, yylineno); }
           ;
comparison : addsub                      { $$ = $1; }
           | addsub '<' addsub           { $$ = new_binop(OP_LT, $1, $3, yylineno); }
           | addsub LE addsub            { $$ = new_binop(OP_LE, $1, $3, yylineno); }
           | addsub '>' addsub           { $$ = new_binop(OP_GT, $1, $3, yylineno); }
           | addsub GE addsub            { $$ = new_binop(OP_GE, $1, $3, yylineno); }
           | addsub EQEQ addsub          { $$ = new_binop(OP_EQ, $1, $3, yylineno); }
           | addsub NE addsub            { $$ = new_binop(OP_NE, $1, $3, yylineno); }
           ;
addsub     : muldiv                      { $$ = $1; }
           | addsub '+' muldiv           { $$ = new_binop(OP_ADD, $1, $3, yylineno); }
           | addsub '-' muldiv           { $$ = new_binop(OP_SUB, $1, $3, yylineno); }
           ;
muldiv     : unary                       { $$ = $1; }
           | muldiv '*' unary            { $$ = new_binop(OP_MUL, $1, $3, yylineno); }
           | muldiv '/' unary            { $$ = new_binop(OP_DIV, $1, $3, yylineno); }
           ;
unary      : primary                     { $$ = $1; }
           | '-' unary                   { $$ = new_kids(N_NEG, $2, NULL, NULL, yylineno); }
           ;
primary    : NUM                         { $$ = new_num($1, yylineno); }
           | TRUE                        { $$ = new_bool(1, yylineno); }
           | FALSE                       { $$ = new_bool(0, yylineno); }
           | ID                          { $$ = new_name(N_VAR, $1, NULL, yylineno); }
           | '(' expr ')'                { $$ = $2; }
           ;
%%
