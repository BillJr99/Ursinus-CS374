/* eval.c : structural recursion implementing the semantics from the
   activity. Each case implements exactly one displayed equation; the SEQ
   case implements the first equation, and the FAST case the second.      */

#include <stdio.h>
#include "ast.h"

void eval_pattern(Node *n, double t0, double t1) {
    double span = t1 - t0;
    switch (n->type) {

    case N_ATOM:                       /* E[[ATOM s]](t0,t1) = {(s,t0,t1)} */
        printf("  %-4s [%.3f, %.3f)\n", n->name, t0, t1);
        break;

    case N_REST:                       /* E[[REST]] = empty set            */
        break;

    case N_SEQ:                        /* subdivide the span evenly        */
        for (int i = 0; i < n->nchildren; i++) {
            double a = t0 + span * i       / n->nchildren;
            double b = t0 + span * (i + 1) / n->nchildren;
            eval_pattern(n->children[i], a, b);
        }
        break;

    case N_GROUP:                      /* transparent: same span           */
        eval_pattern(n->child, t0, t1);
        break;

    case N_FAST:                       /* m copies, each on span/m         */
        for (int j = 0; j < n->factor; j++) {
            double a = t0 + span * j       / n->factor;
            double b = t0 + span * (j + 1) / n->factor;
            eval_pattern(n->child, a, b);
        }
        break;

    case N_SLOW:
        /* Scaffolded for you: SLOW stretches its child across `factor`
           cycles, so within THIS cycle you play a 1/factor "window" of
           the child. Decide which window, and justify your choice in a
           comment. Hint: you will need a notion of the current cycle
           number; consider passing it as a parameter.                  */
        fprintf(stderr, "[eval_pattern:N_SLOW] not yet implemented\n");
        break;

    case N_DEGRADE:
        /* Scaffolded for you: with probability 1/2, evaluate the child;
           otherwise emit nothing. For reproducible grading, seed the
           generator deterministically: srand(42) once in main.         */
        fprintf(stderr, "[eval_pattern:N_DEGRADE] not yet implemented\n");
        break;
    }
}
