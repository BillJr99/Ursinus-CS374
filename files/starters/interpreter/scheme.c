/* CS374 Interpreter assignment: values, scopes, primitives, and eval. */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "scheme.h"

int yyparse(void);

static void die(const char *message, const char *detail) {
    fprintf(stderr, "error: %s %s\n", message, detail);
    exit(1);
}

/* --- Values ------------------------------------------------------------- */

static Value *new_value(Type type) {
    Value *v = calloc(1, sizeof(Value));
    v->type = type;
    return v;
}

Value *make_number(double n)  { Value *v = new_value(NUMBER); v->number = n; return v; }
Value *make_boolean(int b)    { Value *v = new_value(BOOLEAN); v->number = b; return v; }
Value *make_symbol(const char *name) { Value *v = new_value(SYMBOL); v->name = name; return v; }

Value *nil(void) {
    static Value *the_nil = NULL;
    if (the_nil == NULL) the_nil = new_value(NIL);
    return the_nil;
}

Value *cons(Value *car, Value *cdr) {
    Value *v = new_value(PAIR);
    v->car = car;
    v->cdr = cdr;
    return v;
}

static Value *first(Value *list)  { return list->car; }
static Value *second(Value *list) { return list->cdr->car; }
static Value *third(Value *list)  { return list->cdr->cdr->car; }

void print_value(Value *v) {
    switch (v->type) {
        case NUMBER:    printf("%g", v->number); break;
        case BOOLEAN:   printf(v->number != 0 ? "#t" : "#f"); break;
        case SYMBOL:    printf("%s", v->name); break;
        case NIL:       printf("()"); break;
        case PRIMITIVE: printf("<primitive %s>", v->name); break;
        case CLOSURE:   printf("<function>"); break;
        case PAIR:
            printf("(");
            for (; v->type == PAIR; v = v->cdr) {
                print_value(v->car);
                if (v->cdr->type == PAIR) printf(" ");
            }
            printf(")");
            break;
    }
}

/* --- Scopes: a linked list of scopes, each holding a linked list of names --- */

typedef struct Binding {
    const char *name;
    Value *value;
    struct Binding *next;
} Binding;

struct Env {
    Binding *bindings;
    Env *parent;
};

static Env *new_env(Env *parent) {
    Env *env = calloc(1, sizeof(Env));
    env->parent = parent;
    return env;
}

static void define(Env *env, const char *name, Value *value) {
    Binding *b = calloc(1, sizeof(Binding));
    b->name = name;
    b->value = value;
    b->next = env->bindings;
    env->bindings = b;
}

static Value *lookup(Env *env, const char *name) {
    for (; env != NULL; env = env->parent) {
        for (Binding *b = env->bindings; b != NULL; b = b->next) {
            if (strcmp(b->name, name) == 0) return b->value;
        }
    }
    die("undefined name", name);
    return NULL;
}

/* --- Primitives: each takes its evaluated arguments as a list --------------- */

static Value *prim_add(Value *a) { return make_number(first(a)->number + second(a)->number); }
static Value *prim_sub(Value *a) { return make_number(first(a)->number - second(a)->number); }
static Value *prim_mul(Value *a) { return make_number(first(a)->number * second(a)->number); }
static Value *prim_div(Value *a) { return make_number(first(a)->number / second(a)->number); }
static Value *prim_eq(Value *a)  { return make_boolean(first(a)->number == second(a)->number); }
static Value *prim_lt(Value *a)  { return make_boolean(first(a)->number < second(a)->number); }
static Value *prim_gt(Value *a)  { return make_boolean(first(a)->number > second(a)->number); }
static Value *prim_car(Value *a) { return first(a)->car; }
static Value *prim_cdr(Value *a) { return first(a)->cdr; }
static Value *prim_cons(Value *a) { return cons(first(a), second(a)); }
static Value *prim_null(Value *a) { return make_boolean(first(a)->type == NIL); }

/* To add a primitive: write a function above, and add one line to this table. */
static struct { const char *name; Value *(*function)(Value *); } PRIMITIVES[] = {
    {"+", prim_add}, {"-", prim_sub}, {"*", prim_mul}, {"/", prim_div},
    {"=", prim_eq},  {"<", prim_lt},  {">", prim_gt},
    {"car", prim_car}, {"cdr", prim_cdr}, {"cons", prim_cons}, {"null?", prim_null},
};

Env *global_env(void) {
    static Env *global = NULL;
    if (global == NULL) {
        global = new_env(NULL);
        for (size_t i = 0; i < sizeof(PRIMITIVES) / sizeof(PRIMITIVES[0]); i++) {
            Value *p = new_value(PRIMITIVE);
            p->name = PRIMITIVES[i].name;
            p->function = PRIMITIVES[i].function;
            define(global, p->name, p);
        }
    }
    return global;
}

/* --- eval ----------------------------------------------------------------- */

static int is_form(Value *x, const char *name) {
    return x->car->type == SYMBOL && strcmp(x->car->name, name) == 0;
}

static int is_true(Value *v) {
    return !(v->type == BOOLEAN && v->number == 0);
}

static Value *eval_list(Value *list, Env *env) {
    if (list->type == NIL) return nil();
    Value *head = eval(list->car, env);
    return cons(head, eval_list(list->cdr, env));
}

static Value *apply(Value *f, Value *args) {
    if (f->type == PRIMITIVE) return f->function(args);
    if (f->type != CLOSURE) die("not a function:", "the first item of a call");

    /* A call gets a new scope whose parent is the scope the function was created in. */
    Env *scope = new_env(f->env);
    Value *p = f->params;
    for (; p->type == PAIR && args->type == PAIR; p = p->cdr, args = args->cdr) {
        define(scope, p->car->name, args->car);
    }
    if (p->type != args->type) die("wrong number of arguments", "in a call");
    return eval(f->body, scope);
}

Value *eval(Value *x, Env *env) {
    switch (x->type) {
        case NUMBER: case BOOLEAN: case NIL: case PRIMITIVE: case CLOSURE:
            return x;                       /* these evaluate to themselves */
        case SYMBOL:
            return lookup(env, x->name);
        case PAIR:
            break;
    }

    /* Special forms decide for themselves which parts to evaluate. */
    if (is_form(x, "quote")) {              /* (quote datum) */
        return second(x);
    }
    if (is_form(x, "if")) {                 /* (if test then else) */
        if (is_true(eval(second(x), env))) return eval(third(x), env);
        return eval(x->cdr->cdr->cdr->car, env);
    }
    if (is_form(x, "define")) {             /* (define name expr) */
        define(env, second(x)->name, eval(third(x), env));
        return NULL;                        /* a define prints nothing */
    }
    if (is_form(x, "lambda")) {             /* (lambda (params) body) */
        Value *f = new_value(CLOSURE);
        f->params = second(x);
        f->body = third(x);
        f->env = env;
        return f;
    }

    /* Anything else is a call: evaluate the function and its arguments, then apply. */
    return apply(eval(x->car, env), eval_list(x->cdr, env));
}

int main(void) {
    return yyparse();
}
