/* ast.h : tagged-union AST for mini-notation.
   Compare with a Haskell ADT, which says the same thing in five lines:
     data Node = Atom String | Rest | Seq [Node] | Group Node
               | Fast Node Int | Slow Node Int | Degrade Node        */

#ifndef AST_H
#define AST_H

typedef enum { N_ATOM, N_REST, N_SEQ, N_GROUP,
               N_FAST, N_SLOW, N_DEGRADE } NodeType;

typedef struct Node {
    NodeType type;
    char *name;              /* N_ATOM: sample name                  */
    int factor;              /* N_FAST / N_SLOW: the integer operand */
    struct Node **children;  /* N_SEQ: ordered children              */
    int nchildren;
    struct Node *child;      /* unary wrappers: GROUP, FAST, SLOW,
                                DEGRADE                              */
} Node;

Node *node_atom(char *name);
Node *node_rest(void);
Node *seq_new(Node *first);
Node *seq_append(Node *seq, Node *next);
Node *node_group(Node *seq);
Node *node_fast(Node *child, int k);
Node *node_slow(Node *child, int k);
Node *node_degrade(Node *child);

#endif
