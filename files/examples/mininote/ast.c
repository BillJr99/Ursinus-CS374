/* ast.c : constructors and printer for the mini-notation AST.
   NOTE: the class activity declares these functions in ast.h but does not
   list their bodies; this file supplies the obvious implementations so the
   example builds end to end.                                              */

#include <stdio.h>
#include <stdlib.h>
#include "ast.h"

static Node *node_new(NodeType type) {
    Node *n = calloc(1, sizeof(Node));
    if (n == NULL) { fprintf(stderr, "[ast] out of memory\n"); exit(1); }
    n->type = type;
    return n;
}

Node *node_atom(char *name) {
    Node *n = node_new(N_ATOM);
    n->name = name;                     /* already strdup'd by the lexer */
    return n;
}

Node *node_rest(void) {
    return node_new(N_REST);
}

Node *seq_new(Node *first) {
    Node *n = node_new(N_SEQ);
    n->children = malloc(sizeof(Node *));
    n->children[0] = first;
    n->nchildren = 1;
    return n;
}

Node *seq_append(Node *seq, Node *next) {
    seq->children = realloc(seq->children,
                            (seq->nchildren + 1) * sizeof(Node *));
    seq->children[seq->nchildren++] = next;
    return seq;
}

Node *node_group(Node *seq) {
    Node *n = node_new(N_GROUP);
    n->child = seq;
    return n;
}

Node *node_fast(Node *child, int k) {
    Node *n = node_new(N_FAST);
    n->child = child;
    n->factor = k;
    return n;
}

Node *node_slow(Node *child, int k) {
    Node *n = node_new(N_SLOW);
    n->child = child;
    n->factor = k;
    return n;
}

Node *node_degrade(Node *child) {
    Node *n = node_new(N_DEGRADE);
    n->child = child;
    return n;
}

void ast_print(Node *n, int depth) {
    for (int i = 0; i < depth; i++) printf("  ");
    switch (n->type) {
    case N_ATOM:    printf("ATOM %s\n", n->name); break;
    case N_REST:    printf("REST\n");             break;
    case N_SEQ:
        printf("SEQ\n");
        for (int i = 0; i < n->nchildren; i++)
            ast_print(n->children[i], depth + 1);
        break;
    case N_GROUP:
        printf("GROUP\n");
        ast_print(n->child, depth + 1);
        break;
    case N_FAST:
        printf("FAST %d\n", n->factor);
        ast_print(n->child, depth + 1);
        break;
    case N_SLOW:
        printf("SLOW %d\n", n->factor);
        ast_print(n->child, depth + 1);
        break;
    case N_DEGRADE:
        printf("DEGRADE\n");
        ast_print(n->child, depth + 1);
        break;
    }
}
