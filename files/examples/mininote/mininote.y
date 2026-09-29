/* mininote.y : bison/yacc specification with AST-building actions.
   Compile chain:
     bison -d mininote.y      -> mininote.tab.c, mininote.tab.h
     flex  mininote.l         -> lex.yy.c
     cc -o mininote mininote.tab.c lex.yy.c ast.c eval.c main.c     */

%{
#include <stdio.h>
#include <stdlib.h>
#include "ast.h"

int  yylex(void);
void yyerror(const char *msg) {
    fprintf(stderr, "[parser] %s\n", msg);
}

Node *ast_root = NULL;
%}

%union {
    char *str;
    int   num;
    struct Node *node;
}

%token <str> WORD
%token <num> NUMBER
%token REST LBRACK RBRACK STAR SLASH QMARK

%type <node> pattern sequence term atom

%%

pattern  : sequence                      { ast_root = $1; }
         ;

sequence : sequence term                 { $$ = seq_append($1, $2); }
         | term                          { $$ = seq_new($1);        }
         ;

term     : term STAR NUMBER              { $$ = node_fast($1, $3);  }
         | term SLASH NUMBER             { $$ = node_slow($1, $3);  }
         | term QMARK                    { $$ = node_degrade($1);   }
         | atom                          { $$ = $1;                 }
         ;

atom     : WORD                          { $$ = node_atom($1);      }
         | REST                          { $$ = node_rest();        }
         | LBRACK sequence RBRACK        { $$ = node_group($2);     }
         ;

%%
