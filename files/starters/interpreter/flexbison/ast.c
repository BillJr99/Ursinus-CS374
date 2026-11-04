/* CS374 Interpreter assignment: node constructors.  This file is complete. */
#include <stdlib.h>
#include "ast.h"

Node *program = NULL;

Node *new_node(Kind kind, int line) {
    Node *n = calloc(1, sizeof(Node));
    n->kind = kind;
    n->line = line;
    return n;
}

Node *new_num(double value, int line) {
    Node *n = new_node(N_NUM, line);
    n->num = value;
    return n;
}

Node *new_bool(int value, int line) {
    Node *n = new_node(N_BOOL, line);
    n->num = value;
    return n;
}

Node *new_name(Kind kind, char *name, Node *value, int line) {
    Node *n = new_node(kind, line);
    n->name = name;
    n->a = value;
    return n;
}

Node *new_binop(Op op, Node *a, Node *b, int line) {
    Node *n = new_kids(N_BINOP, a, b, NULL, line);
    n->op = op;
    return n;
}

Node *new_kids(Kind kind, Node *a, Node *b, Node *c, int line) {
    Node *n = new_node(kind, line);
    n->a = a;
    n->b = b;
    n->c = c;
    return n;
}

Node *append_stmt(Node *list, Node *stmt) {
    if (list == NULL) return stmt;
    Node *last = list;
    while (last->next != NULL) last = last->next;
    last->next = stmt;
    return list;
}
