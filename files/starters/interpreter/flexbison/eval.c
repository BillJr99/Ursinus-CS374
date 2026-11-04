/* CS374 Interpreter assignment: the evaluator.  The scanner, parser, and AST are complete,
   so this is the file you write.  Every TODO is yours, and the assignment page walks
   through them in order. */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "ast.h"

/* --- Values: a number or a boolean --------------------------------------- */
typedef struct {
    int is_bool;
    double num;      /* the number, or 1 or 0 for a boolean */
} Value;

static Value make_num(double n)  { Value v = {0, n}; return v; }
static Value make_bool(int b)    { Value v = {1, b ? 1 : 0}; return v; }
static const char *type_name(Value v) { return v.is_bool ? "bool" : "num"; }

static void print_value(Value v) {
    if (v.is_bool) printf("%s\n", v.num ? "true" : "false");
    else printf("%.15g\n", v.num);
}

/* Print a staged error line, and stop the program. */
#define RUNTIME_ERROR(line, ...) \
    do { printf("Runtime error at line %d: ", (line)); printf(__VA_ARGS__); printf("\n"); exit(1); } while (0)

/* --- Environments: one scope is a linked list of bindings, plus a parent --- */
typedef struct Binding {
    char *name;
    Value value;
    struct Binding *next;
} Binding;

typedef struct Env {
    Binding *bindings;
    struct Env *parent;
} Env;

static Env *env_new(Env *parent) {
    Env *env = calloc(1, sizeof(Env));
    env->parent = parent;
    return env;
}

static void env_define(Env *env, char *name, Value value) {
    /* TODO (Step 4): make a new Binding and put it at the front of THIS scope's list.
       A second let of the same name in one scope then hides the first. */
    (void) env; (void) name; (void) value;
}

static Binding *env_find(Env *env, char *name) {
    /* TODO (Step 4): search this scope's list, then the parent's, and so on.
       Return the Binding, or NULL if no scope has the name. */
    (void) env; (void) name;
    return NULL;
}

/* --- Expressions produce a Value ------------------------------------------ */
static int truthy(Value v) {
    /* TODO (Step 3): false and 0 are false, and everything else is true. */
    (void) v;
    return 0;
}

static Value eval(Node *n, Env *env) {
    switch (n->kind) {
    case N_NUM:
        return make_num(n->num);
    /* TODO (Step 1): N_BOOL */
    /* TODO (Step 2): N_NEG, and the arithmetic operators of N_BINOP */
    /* TODO (Step 3): the comparison operators of N_BINOP, N_AND, N_OR, and N_NOT */
    /* TODO (Step 4): N_VAR */
    default:
        RUNTIME_ERROR(n->line, "no case yet for expression kind %d", n->kind);
    }
}

/* --- Statements run for their effect, and report how they finished --------- */
typedef enum { S_NORMAL, S_BREAK, S_CONTINUE } Signal;
static int signal_line = 0;      /* where a break or continue was, for the stray message */

static Signal exec_list(Node *stmt, Env *env);

static Signal exec(Node *n, Env *env) {
    switch (n->kind) {
    /* TODO (Step 1): N_PRINT */
    /* TODO (Step 4): N_LET, N_ASSIGN, and N_BLOCK */
    /* TODO (Step 5): N_IF and N_WHILE */
    /* TODO (Step 6): N_BREAK and N_CONTINUE */
    default:
        RUNTIME_ERROR(n->line, "no case yet for statement kind %d", n->kind);
    }
    return S_NORMAL;
}

/* Run the statements in order.  Stop early if one reports a break or a continue. */
static Signal exec_list(Node *stmt, Env *env) {
    for (; stmt != NULL; stmt = stmt->next) {
        Signal s = exec(stmt, env);
        if (s != S_NORMAL) return s;
    }
    return S_NORMAL;
}

/* main.c calls this with the parsed program. */
void run_program(Node *first) {
    Env *globals = env_new(NULL);
    Signal s = exec_list(first, globals);
    /* TODO (Step 7): a break or continue that reaches here is outside any loop. */
    (void) s; (void) signal_line;
}
