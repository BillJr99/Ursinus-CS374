/* CS374 Interpreter assignment: a small Scheme.  Every value is a Value. */
#ifndef SCHEME_H
#define SCHEME_H

typedef enum { NUMBER, BOOLEAN, SYMBOL, NIL, PAIR, PRIMITIVE, CLOSURE } Type;

typedef struct Env Env;
typedef struct Value Value;

struct Value {
    Type type;
    double number;                 /* NUMBER, and BOOLEAN as 0 or 1 */
    const char *name;              /* SYMBOL, and PRIMITIVE's name */
    Value *car, *cdr;              /* PAIR */
    Value *(*function)(Value *);   /* PRIMITIVE: takes its evaluated arguments as a list */
    Value *params, *body;          /* CLOSURE */
    Env *env;                      /* CLOSURE: the scope it was created in */
};

Value *make_number(double n);
Value *make_boolean(int b);
Value *make_symbol(const char *name);
Value *nil(void);
Value *cons(Value *car, Value *cdr);

Env *global_env(void);
Value *eval(Value *x, Env *env);
void print_value(Value *v);

#endif
