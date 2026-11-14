%{
#include <stdio.h>
#include <ctype.h>
int yylex(void);
void yyerror(const char *s) { fprintf(stderr, "error: %s\n", s); }
int registers[26];          /* one slot per letter: the whole symbol table */
%}
%union { int number; int slot; }
%token <number> NUM
%token <slot>   LETTER
%token LET PRINT
%type  <number> expr
%left '+'
%left '*'
%%
input: /* nothing */ | input stmt '\n' ;
stmt:  LET LETTER '=' expr  { registers[$2] = $4; }   /* assignment */
     | PRINT expr           { printf("%d\n", $2); }
     ;
expr:  expr '+' expr        { $$ = $1 + $3; }
     | expr '*' expr        { $$ = $1 * $3; }
     | NUM                  { $$ = $1; }
     | LETTER               { $$ = registers[$1]; }   /* lookup */
     ;
%%
int yylex(void) {
    int c = getchar();
    while (c == ' ') c = getchar();
    if (isdigit(c)) { ungetc(c, stdin); scanf("%d", &yylval.number); return NUM; }
    if (islower(c)) {
        int next = getchar();
        if (islower(next)) {        /* two or more letters: a keyword */
            int first = c;
            while (islower(next)) next = getchar();
            ungetc(next, stdin);
            return first == 'l' ? LET : PRINT;
        }
        ungetc(next, stdin);
        yylval.slot = c - 'a';
        return LETTER;
    }
    return c == EOF ? 0 : c;
}
int main(void) { return yyparse(); }
