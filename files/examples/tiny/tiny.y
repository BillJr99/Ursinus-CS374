%{
#include <stdio.h>
#include <ctype.h>
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
int yylex(void) {
    int c = getchar();
    while (c == ' ') c = getchar();
    if (isdigit(c)) { ungetc(c, stdin); scanf("%d", &yylval); return NUM; }
    return c == EOF ? 0 : c;
}
int main(void) { return yyparse(); }
