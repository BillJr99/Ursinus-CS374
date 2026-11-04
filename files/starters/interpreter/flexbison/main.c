/* CS374 Interpreter assignment: the file runner.  This file is complete.
   ./mylang program.ml runs a file.  With no file name, it reads standard input. */
#include <stdio.h>
#include "ast.h"

extern FILE *yyin;
int yyparse(void);
void run_program(Node *first);

int main(int argc, char **argv) {
    if (argc > 1) {
        yyin = fopen(argv[1], "r");
        if (yyin == NULL) {
            printf("cannot open %s\n", argv[1]);
            return 2;
        }
    }
    yyparse();              /* a lexical or syntax error prints its line and stops here */
    run_program(program);
    return 0;
}
