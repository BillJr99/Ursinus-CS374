/* main.c : end-to-end driver.
   Example session:
     $ echo "bd [sn sn] hh*2 ~" | ./mininote
     SEQ
       ATOM bd
       GROUP
         SEQ
           ATOM sn
           ATOM sn
       FAST 2
         ATOM hh
       REST
     events in cycle [0,1):
       bd   [0.000, 0.250)
       sn   [0.250, 0.375)
       sn   [0.375, 0.500)
       hh   [0.500, 0.625)
       hh   [0.625, 0.750)                                            */

#include <stdio.h>
#include "ast.h"

extern int yyparse(void);
extern Node *ast_root;

void ast_print(Node *n, int depth);             /* in ast.c  */
void eval_pattern(Node *n, double t0, double t1); /* in eval.c */

int main(void) {
    if (yyparse() != 0 || ast_root == NULL) {
        fprintf(stderr, "[main] parse failed\n");
        return 1;
    }
    ast_print(ast_root, 0);
    printf("events in cycle [0,1):\n");
    eval_pattern(ast_root, 0.0, 1.0);
    return 0;
}
