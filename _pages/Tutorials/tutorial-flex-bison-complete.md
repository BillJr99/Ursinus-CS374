# Tutorial: Flex and Bison from Zero to a Working Language

<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374-Fall2026/gh-pages/_pages/Tutorials/tutorial-flex-bison-complete.md

import: https://raw.githubusercontent.com/liascript/CodeRunner/master/README.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

# Tutorial: Flex and Bison from Zero to a Working Language

This tutorial builds a complete, running calculator language step by step using **Flex** (fast lexer generator) and **Bison** (parser generator). No prior knowledge of either tool is assumed. By the end you will have:

1. A working `flex` lexer that tokenizes arithmetic expressions
2. A working `bison` grammar that parses them with correct precedence
3. A complete calculator that evaluates expressions including variables
4. The knowledge to extend this into a full language

**Why Flex and Bison?** Your hand-written lexer and recursive-descent parser give you deep understanding, but real languages use generated parsers for reliability and speed. GCC used Bison until recently; PostgreSQL uses Bison for SQL; PHP, Ruby, and many other interpreters were born from Flex/Bison grammars.

---

# Part 1: Installation and "Hello, Flex"

## 1.1 Check Your Installation

```bash
flex --version    # should show 2.6.x or later
bison --version   # should show 3.x or later
gcc --version     # any recent version
```

On Debian/Ubuntu: `sudo apt-get install flex bison gcc`
On macOS: `brew install flex bison`

## 1.2 The Simplest Flex File

Create `hello.l`:

```c
/* hello.l — the simplest possible flex file */
%%
[0-9]+   printf("NUMBER: %s\n", yytext);
[a-z]+   printf("WORD: %s\n",   yytext);
.        /* ignore everything else */
%%
int main() { return yylex(); }
```

A flex file has three sections separated by `%%`:
1. **Definitions**: `%option` directives, named patterns, C headers
2. **Rules**: pattern → action pairs
3. **User code**: C functions, including `main` if desired

Build and test:
```bash
flex -o hello.c hello.l
gcc -o hello hello.c -lfl
echo "hello 42 world 99" | ./hello
```

Expected output:
```
WORD: hello
NUMBER: 42
WORD: world
NUMBER: 99
```

## 1.3 Key Flex Variables and Functions

| Variable/Function | Meaning |
|---|---|
| `yytext` | The matched text as a C string |
| `yyleng` | Length of the match |
| `yylex()` | Call to get the next token |
| `yylval` | The semantic value passed to Bison |
| `yylineno` | Current line number (with `%option yylineno`) |
| `ECHO` | Default action: print the match |
| `BEGIN(state)` | Switch to a named start condition |

---

# Part 2: Flex for a Calculator

## 2.1 The Lexer File `calc.l`

```c
/* calc.l — lexer for a simple calculator */
%{
/* C code in %{ ... %} is copied verbatim to the output */
#include <stdio.h>
#include <stdlib.h>
#include "calc.tab.h"   /* Bison-generated header: defines token codes */
%}

%option yylineno
%option noyywrap         /* don't try to open more files after EOF */

%%

[ \t\r]+        { /* skip whitespace */ }
\n              { return '\n'; }            /* newlines matter (end of expression) */
[0-9]+          { yylval.ival = atoi(yytext); return NUMBER; }
[0-9]*\.[0-9]+  { yylval.dval = atof(yytext); return FLOAT;  }
[a-zA-Z_][a-zA-Z0-9_]*  { yylval.sval = strdup(yytext); return IDENT; }
"+"             { return '+'; }
"-"             { return '-'; }
"*"             { return '*'; }
"/"             { return '/'; }
"^"             { return '^'; }
"("             { return '('; }
")"             { return ')'; }
"="             { return '='; }
.               { fprintf(stderr, "[lexer:%d] Unexpected char: %c\n",
                           yylineno, yytext[0]); }

%%
```

**Important pattern rules:**
- Patterns are tried in order; the *longest match* wins (if ties, first rule wins)
- `[0-9]+` matches one or more digits; `[0-9]*` matches zero or more
- `.` matches any character except newline — use it as a catch-all error handler

---

# Part 3: Bison Grammar

## 3.1 The Grammar File `calc.y`

```c
/* calc.y — Bison grammar for the calculator */
%{
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <string.h>

/* Forward declarations */
void yyerror(const char *msg);
int  yylex(void);
extern int yylineno;

/* Symbol table: a simple fixed-size array for demo purposes */
#define MAX_VARS 64
typedef struct { char *name; double value; } Var;
Var symtable[MAX_VARS];
int num_vars = 0;

double var_get(char *name) {
    for (int i = 0; i < num_vars; i++)
        if (strcmp(symtable[i].name, name) == 0)
            return symtable[i].value;
    fprintf(stderr, "[eval] Undefined variable: %s\n", name);
    return 0.0;
}

void var_set(char *name, double value) {
    for (int i = 0; i < num_vars; i++)
        if (strcmp(symtable[i].name, name) == 0) {
            symtable[i].value = value;
            return;
        }
    if (num_vars >= MAX_VARS) { fprintf(stderr, "Symbol table full\n"); return; }
    symtable[num_vars].name  = strdup(name);
    symtable[num_vars].value = value;
    num_vars++;
}
%}

/* === Type declarations === */
/* yylval can hold any of these types */
%union {
    int     ival;
    double  dval;
    char   *sval;
}

/* === Token declarations === */
/* %token <type> name — associates a union member with a token */
%token <ival>  NUMBER
%token <dval>  FLOAT
%token <sval>  IDENT

/* === Precedence and associativity ===
   Lower declarations = lower precedence.
   These resolve all shift-reduce conflicts for the usual rules. */
%left  '+' '-'
%left  '*' '/'
%right '^'         /* exponentiation: right-associative (a^b^c = a^(b^c)) */
%right UMINUS      /* unary minus: a pseudo-token for %prec */

/* === Result type for non-terminals === */
%type <dval> expr

%%

/* === Grammar rules === */
program:
    /* empty */
  | program stmt '\n'
  ;

stmt:
    expr              { printf("= %g\n", $1); }
  | IDENT '=' expr    { var_set($1, $3); printf("%s = %g\n", $1, $3); free($1); }
  | /* empty */
  ;

expr:
    NUMBER              { $$ = (double)$1; }
  | FLOAT               { $$ = $1; }
  | IDENT               { $$ = var_get($1); free($1); }
  | expr '+' expr       { $$ = $1 + $3; }
  | expr '-' expr       { $$ = $1 - $3; }
  | expr '*' expr       { $$ = $1 * $3; }
  | expr '/' expr       {
        if ($3 == 0.0) { yyerror("division by zero"); $$ = 0; }
        else           { $$ = $1 / $3; }
    }
  | expr '^' expr       { $$ = pow($1, $3); }
  | '-' expr %prec UMINUS  { $$ = -$2; }
  | '(' expr ')'        { $$ = $2; }
  ;

%%

/* === User code section === */
void yyerror(const char *msg) {
    fprintf(stderr, "[parser:%d] %s\n", yylineno, msg);
}

int main(void) {
    printf("Mini Calculator. Enter expressions (Ctrl-D to quit).\n");
    return yyparse();
}
```

---

## 3.2 The Makefile

```makefile
# Makefile for the calculator

CC      = gcc
CFLAGS  = -Wall -g
LDFLAGS = -lfl -lm

calc: calc.tab.c lex.yy.c
	$(CC) $(CFLAGS) -o calc calc.tab.c lex.yy.c $(LDFLAGS)

calc.tab.c calc.tab.h: calc.y
	bison -d calc.y           # -d generates the header file calc.tab.h

lex.yy.c: calc.l calc.tab.h
	flex calc.l

clean:
	rm -f calc calc.tab.c calc.tab.h lex.yy.c
```

Build:
```bash
make
```

Test:
```bash
echo "3 + 4 * 2" | ./calc          # = 11
echo "x = 5" | ./calc              # x = 5
echo -e "x = 5\nx * x" | ./calc    # x = 5, = 25
echo "2 ^ 10" | ./calc             # = 1024
echo "-3 * -4" | ./calc            # = 12
```

---

# Part 4: Building an Abstract Syntax Tree

## 4.1 Why Build an AST?

The calculator above evaluates expressions *during parsing* (embedded actions). For a real language, you want to:
- Check for errors across the whole program before running anything
- Optimize the tree before evaluating
- Generate code rather than evaluate directly

To do this, the grammar rules must **build a tree** rather than compute a value.

## 4.2 AST in C

```c
/* ast.h */
#ifndef AST_H
#define AST_H

typedef enum {
    AST_NUM, AST_VAR,
    AST_BINOP, AST_UNARY,
    AST_ASSIGN, AST_SEQ
} AstKind;

typedef struct Ast {
    AstKind kind;
    union {
        double       num;
        char        *var;
        struct { char op; struct Ast *left, *right; } binop;
        struct { char op; struct Ast *operand; }      unary;
        struct { char *name; struct Ast *value; }     assign;
        struct { struct Ast *first, *rest; }          seq;
    };
} Ast;

Ast *ast_num(double val);
Ast *ast_var(char *name);
Ast *ast_binop(char op, Ast *left, Ast *right);
Ast *ast_unary(char op, Ast *operand);
Ast *ast_assign(char *name, Ast *value);

void ast_print(Ast *node, int indent);
double ast_eval(Ast *node);
void ast_free(Ast *node);

#endif
```

```c
/* ast.c — implementation */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include "ast.h"

Ast *ast_num(double val) {
    Ast *n = malloc(sizeof(Ast));
    n->kind = AST_NUM; n->num = val; return n;
}

Ast *ast_var(char *name) {
    Ast *n = malloc(sizeof(Ast));
    n->kind = AST_VAR; n->var = strdup(name); return n;
}

Ast *ast_binop(char op, Ast *left, Ast *right) {
    Ast *n = malloc(sizeof(Ast));
    n->kind = AST_BINOP; n->binop.op = op;
    n->binop.left = left; n->binop.right = right; return n;
}

void ast_print(Ast *node, int indent) {
    if (!node) return;
    for (int i = 0; i < indent; i++) printf("  ");
    switch (node->kind) {
        case AST_NUM:   printf("Num(%g)\n", node->num); break;
        case AST_VAR:   printf("Var(%s)\n", node->var); break;
        case AST_BINOP: printf("BinOp(%c)\n", node->binop.op);
                        ast_print(node->binop.left,  indent+1);
                        ast_print(node->binop.right, indent+1); break;
        default:        printf("???\n");
    }
}
```

## 4.3 Grammar Rules That Build Trees

```c
/* In the .y file, change the expr rules: */

%type <ast_ptr> expr stmt

expr:
    NUMBER              { $$ = ast_num((double)$1); }
  | FLOAT               { $$ = ast_num($1); }
  | IDENT               { $$ = ast_var($1); free($1); }
  | expr '+' expr       { $$ = ast_binop('+', $1, $3); }
  | expr '-' expr       { $$ = ast_binop('-', $1, $3); }
  | expr '*' expr       { $$ = ast_binop('*', $1, $3); }
  | expr '/' expr       { $$ = ast_binop('/', $1, $3); }
  | expr '^' expr       { $$ = ast_binop('^', $1, $3); }
  | '-' expr %prec UMINUS  { $$ = ast_unary('-', $2); }
  | '(' expr ')'        { $$ = $2; }
  ;
```

---

# Part 5: Error Recovery

## 5.1 The `error` Token

Bison provides a special `error` token for error recovery. When a syntax error occurs, Bison pops the stack until it finds a state where `error` can shift, then discards tokens until it finds one the grammar expects.

```c
stmt:
    expr '\n'           { printf("= %g\n", $1); }
  | error '\n'          {
        /* Recover at end of line: discard the bad expression */
        fprintf(stderr, "[parser] Skipping bad expression\n");
        yyerrok;         /* reset error state */
    }
  ;
```

With this rule, a syntax error on one line does not abort the entire session — the parser recovers and tries the next line.

---

# Part 6: Adding More Language Features

## 6.1 Comparison Operators

```c
/* Add to the .y precedence declarations: */
%left  '<' '>' LE GE EQ NEQ
%token LE GEQ EQ NEQ       /* two-character operators */

/* Add to grammar rules: */
| expr '<'  expr  { $$ = ($1 <  $3) ? 1.0 : 0.0; }
| expr '>'  expr  { $$ = ($1 >  $3) ? 1.0 : 0.0; }
| expr LE   expr  { $$ = ($1 <= $3) ? 1.0 : 0.0; }
| expr GEQ  expr  { $$ = ($1 >= $3) ? 1.0 : 0.0; }
| expr EQ   expr  { $$ = ($1 == $3) ? 1.0 : 0.0; }
| expr NEQ  expr  { $$ = ($1 != $3) ? 1.0 : 0.0; }
```

## 6.2 If-Then-Else

```c
%token IF THEN ELSE

/* Add to grammar: */
| IF expr THEN expr ELSE expr  { $$ = ($2 != 0.0) ? $4 : $6; }
```

## 6.3 While Loops (with AST approach)

```c
/* AST node for while: */
typedef struct { Ast *cond; Ast *body; } WhileNode;

/* Grammar: */
| WHILE expr DO stmt_list END  {
    $$ = ast_while($2, $4);
}
```

---

# Part 7: Common Pitfalls and Debugging

## 7.1 Shift-Reduce Conflicts

When Bison reports "N shift/reduce conflicts", it means the grammar is ambiguous in a way that one token of lookahead cannot resolve. Bison's default is to **shift** (which is usually right for operator precedence, left recursion, and dangling else).

**To see what's happening:** add `--report=all` to your bison command; it generates a `.output` file showing every state and every conflict.

```bash
bison -d --report=all calc.y
cat calc.output | grep -A5 "State "
```

## 7.2 Dangling Else

The grammar `if expr then stmt | if expr then stmt else stmt` has a classic shift-reduce conflict at `else`. Bison's shift default is the right behavior (match else with nearest if), but it is cleaner to make it explicit:

```c
%precedence THEN
%precedence ELSE    /* higher: shifts else before reducing the inner if */
```

## 7.3 Memory in Semantic Values

When you `strdup` a string in the lexer (`yylval.sval = strdup(yytext)`), the grammar rules that consume it are responsible for `free`-ing it. Failing to do so is a memory leak. In the AST approach, the AST takes ownership and `ast_free` handles deallocation.

## 7.4 Debugging Flex Rules

Add `%option debug` to your flex file and set the environment variable `FLEXDBG=1` before running. This prints every rule that fires.

---

# Part 8: Complete Example Makefile and Directory Layout

```
mylan/
├── Makefile
├── lexer.l      (Flex)
├── parser.y     (Bison)
├── ast.h
├── ast.c
├── eval.c
├── symtable.h
├── symtable.c
└── main.c       (optional: if main is not in parser.y)
```

```makefile
CC      = gcc
CFLAGS  = -Wall -Wextra -g -I.
LDFLAGS = -lfl -lm

SRCS    = parser.tab.c lex.yy.c ast.c symtable.c
TARGET  = mylan

$(TARGET): $(SRCS)
	$(CC) $(CFLAGS) -o $@ $^ $(LDFLAGS)

parser.tab.c parser.tab.h: parser.y
	bison -d -o parser.tab.c parser.y

lex.yy.c: lexer.l parser.tab.h
	flex -o lex.yy.c lexer.l

clean:
	rm -f $(TARGET) parser.tab.c parser.tab.h lex.yy.c
```

---

# Part 9: From Calculator to Language

The calculator is one step from a complete language. The progression:

| Addition | Flex Change | Bison Change |
|---|---|---|
| String literals | `\"[^\"]*\"` rule | `STRING` token type, `%token <sval>` |
| Boolean literals | `"true"` / `"false"` rules | `BOOL` token, separate type |
| Function definitions | `"fun"`, `"->"` | `fun_def` production, AST node |
| Function calls | no change | `expr expr` (left-associative `app`) |
| Blocks / sequencing | `";"` or newline | `stmt_list` production |
| Lists | `"["`, `"]"`, `","` | `list_expr` production |

Each addition requires: (1) updating the lexer rules, (2) updating the grammar, (3) adding AST node types, (4) adding eval cases. The structure remains the same.

---

## Further Reading

- Levine, John. *Flex & Bison* (O'Reilly, 2009). The definitive practical reference; covers everything in this tutorial and much more.
- The Bison manual: `info bison` or online. Covers LALR, GLR, push parsers, named references, and error recovery in depth.
- The Flex manual: `info flex` or online. Covers start conditions, multiple input files, `%option`, and C++ lexers.
- Johnson, Stephen C. "Yacc: Yet Another Compiler-Compiler." Bell Labs, 1975. The original yacc paper; still readable and historically illuminating.
- Aho, Lam, Sethi, Ullman. *Compilers* (Dragon Book), Chapter 4 — the theory behind what flex/bison generate.
