%{
/* tiny.y - the same grammar as the course's tiny.y, with yylex now coming from tiny.l */
#include <stdio.h>
int yylex(void);
void yyerror(const char *s) { fprintf(stderr, "error: %s\n", s); }
%}
%token NUM
%left '+'
%left '*'
%%
input: /* nothing */ | input expr '\n' { printf("%d\n", $2); } ;
expr:  expr '+' expr  { $$ = $1 + $3; }
     | expr '*' expr  { $$ = $1 * $3; }
     | NUM            { $$ = $1; }
     ;
%%
int main(void) { return yyparse(); }
