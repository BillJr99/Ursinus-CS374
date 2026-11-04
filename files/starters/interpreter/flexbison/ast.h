/* CS374 Interpreter assignment: the AST.  This file is complete. */
#ifndef AST_H
#define AST_H

typedef enum {
    N_NUM, N_BOOL, N_VAR, N_BINOP, N_NEG, N_NOT, N_AND, N_OR,
    N_LET, N_ASSIGN, N_PRINT, N_BLOCK, N_IF, N_WHILE, N_BREAK, N_CONTINUE
} Kind;

/* The operators of N_BINOP. */
typedef enum { OP_ADD, OP_SUB, OP_MUL, OP_DIV, OP_LT, OP_LE, OP_GT, OP_GE, OP_EQ, OP_NE } Op;

/* One struct holds every kind of node, and each kind uses the fields it needs:
     N_NUM     num                  N_LET, N_ASSIGN  name, a (the value)
     N_BOOL    num (1 or 0)         N_PRINT          a (the value)
     N_VAR     name                 N_BLOCK          a (the first statement)
     N_BINOP   op, a, b             N_IF             a (condition), b (then), c (else, or NULL)
     N_NEG     a                    N_WHILE          a (condition), b (body)
     N_NOT     a                    N_BREAK, N_CONTINUE  nothing
     N_AND, N_OR   a, b
   Statements in a list are linked through next. */
typedef struct Node {
    Kind kind;
    int line;
    double num;
    char *name;
    Op op;
    struct Node *a, *b, *c;
    struct Node *next;
} Node;

Node *new_node(Kind kind, int line);
Node *new_num(double value, int line);
Node *new_bool(int value, int line);
Node *new_name(Kind kind, char *name, Node *value, int line);
Node *new_binop(Op op, Node *a, Node *b, int line);
Node *new_kids(Kind kind, Node *a, Node *b, Node *c, int line);
Node *append_stmt(Node *list, Node *stmt);

extern Node *program;   /* the first top-level statement, set by the parser */

#endif
