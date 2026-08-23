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

## Learning Goals

By the end of this tutorial, you will have:

- Written a working Flex lexer file (`.l`) that tokenizes arithmetic expressions including integers, floats, identifiers, and operators
- Written a working Bison grammar file (`.y`) that parses expressions with correct operator precedence and associativity
- Built and run a complete calculator language that evaluates arithmetic expressions and stores variables
- Extended the calculator grammar with at least one new construct (e.g., comparison operators or a print statement)
- Connected the Flex/Bison toolchain to the hand-written lexer and recursive-descent parser you built in earlier assignments

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
/* hello.l - the simplest possible flex file */
%%
[0-9]+   printf("NUMBER: %s\n", yytext);
[a-z]+   printf("WORD: %s\n",   yytext);
.        /* ignore everything else */
%%
int main() { return yylex(); }
```

A flex file has three sections separated by `%%`:
1. **Definitions**: `%option` directives, named patterns, C headers
2. **Rules**: pattern -> action pairs
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
/* calc.l - lexer for a simple calculator */
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
- `.` matches any character except newline: use it as a catch-all error handler

---

# Part 3: Bison Grammar

## 3.1 The Grammar File `calc.y`

```c
/* calc.y - Bison grammar for the calculator */
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
/* %token <type> name - associates a union member with a token */
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
/* ast.c - implementation */
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

With this rule, a syntax error on one line does not abort the entire session; the parser recovers and tries the next line.

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
|-- Makefile
|-- lexer.l      (Flex)
|-- parser.y     (Bison)
|-- ast.h
|-- ast.c
|-- eval.c
|-- symtable.h
|-- symtable.c
`-- main.c       (optional: if main is not in parser.y)
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
- Aho, Lam, Sethi, Ullman. *Compilers* (Dragon Book), Chapter 4: the theory behind what flex/bison generate.

---

# Appendix: How Bison Builds Its Tables, LR(0) Items and the Canonical Collection

This appendix is the theory behind the `--report=all` output you met in Part 7 and behind the generator-toolchain directions of the Lexer and Parser assignments: how Bison turns your grammar into the ACTION and GOTO tables that drive `yyparse`.

## A.1 How Yacc Parses: LR Items, States, and the LALR(1) Idea

**Yacc builds a shift-reduce parser driven by a finite automaton over grammar items.** An **LR(0) item** is a production with a dot marking parsing progress, such as

$$
\texttt{expr} \rightarrow \texttt{expr} \cdot \texttt{'*'}\ \texttt{expr}
$$

which reads "we have parsed the left operand and will accept this production if `'*'` and another `expr` come next." The parser generator closes sets of items into **states**, connects them with transitions on grammar symbols, and emits two tables: an **action** table (shift, reduce, accept, or error, indexed by state and lookahead token) and a **goto** table (next state after a reduction). At run time the parser is breathtakingly simple, which is the point: a loop, a stack, and table lookups, running in $O(n)$ time and using stack space proportional to the deepest nesting in the input.

### Pseudocode

```
function LR-PARSE(tokens):
    push state 0
    a = first token
    loop:
        s = state on top of stack
        if ACTION[s, a] = shift t:
            push a, push state t
            a = next token
        else if ACTION[s, a] = reduce (A -> beta):
            pop 2 * |beta| entries
            t = state now on top
            push A, push GOTO[t, A]
            (run the semantic action for A -> beta here)
        else if ACTION[s, a] = accept:
            return the finished parse
        else:
            report syntax error at a
```

## A.2 A Shift-Reduce Parse You Can Watch

**What you are about to see:** The pseudocode above describes LR parsing in the abstract; this model makes it concrete by running it step by step for a small arithmetic grammar. You will see the two-stack (state stack + symbol stack) loop in action and read a printed trace of every shift and reduce decision. Pay attention to the moment when the parser chooses to shift `*` rather than reducing an already-complete `+` expression; that single decision is where operator precedence lives in an LR parser, and spotting it in the trace will make the conflict discussion that follows much easier to understand.

Before reading the bison output, run the algorithm yourself on a tiny grammar. The code below simulates a shift-reduce parser for simple arithmetic expressions (`n + n * n`) with an explicit stack and action trace, the same algorithm bison generates for the calculator, just with a hand-written action table instead of a generated one.

```python
# Shift-reduce parser trace for: E -> E+T | T,  T -> T*F | F,  F -> (E) | n
# ACTION table and GOTO table are encoded as dicts (state, symbol) -> action.
# Actions: ("shift", next_state), ("reduce", rule), "accept", "error"

# Grammar rules: name -> (symbols_to_pop, nonterminal_to_push)
RULES = {
    "E->E+T": (3, "E"),  # pop E, +, T  -> push E
    "E->T":   (1, "E"),
    "T->T*F": (3, "T"),
    "T->F":   (1, "T"),
    "F->n":   (1, "F"),
    "F->(E)": (3, "F"),  # pop (, E, )  -> push F
}

# Minimal LR(0) action table for this grammar (hand-constructed, state 0-11)
ACTION = {
    (0,"n"):  ("shift",5),  (0,"("):  ("shift",4),
    (1,"+"):  ("shift",6),  (1,"$"):  "accept",
    (2,"+"):  ("reduce","E->T"), (2,"*"): ("shift",7), (2,"$"): ("reduce","E->T"),
    (3,"+"):  ("reduce","T->F"), (3,"*"): ("reduce","T->F"), (3,"$"): ("reduce","T->F"),
    (4,"n"):  ("shift",5),  (4,"("):  ("shift",4),
    (5,"+"):  ("reduce","F->n"), (5,"*"): ("reduce","F->n"), (5,"$"): ("reduce","F->n"),
    (6,"n"):  ("shift",5),  (6,"("):  ("shift",4),
    (7,"n"):  ("shift",5),  (7,"("):  ("shift",4),
    (8,"+"):  ("shift",6),  (8,")"):  ("shift",11),
    (9,"+"):  ("reduce","E->E+T"), (9,"*"): ("shift",7),
              (9,")"): ("reduce","E->E+T"), (9,"$"): ("reduce","E->E+T"),
    (10,"+"): ("reduce","T->T*F"), (10,"*"): ("reduce","T->T*F"),
              (10,")"): ("reduce","T->T*F"), (10,"$"): ("reduce","T->T*F"),
    (11,"+"): ("reduce","F->(E)"), (11,"*"): ("reduce","F->(E)"),
              (11,")"): ("reduce","F->(E)"), (11,"$"): ("reduce","F->(E)"),
}
GOTO = {
    (0,"E"):1, (0,"T"):2, (0,"F"):3,
    (4,"E"):8, (4,"T"):2, (4,"F"):3,
    (6,"T"):9, (6,"F"):3,
    (7,"F"):10,
}

def lr_parse(tokens):
    tokens = tokens + ["$"]
    stack = [0]        # state stack
    sym_stack = []     # symbol stack (for display)
    pos = 0

    print(f"{'Stack':35} {'Remaining':18} Action")
    print("-" * 75)

    while True:
        state = stack[-1]
        tok   = tokens[pos]
        disp_stack = " ".join(str(x) for x in sym_stack) or "⊥"
        disp_rest  = " ".join(tokens[pos:])
        action = ACTION.get((state, tok), "error")

        if action == "accept":
            print(f"{disp_stack:35} {disp_rest:18} ACCEPT OK")
            return
        elif action == "error":
            print(f"{disp_stack:35} {disp_rest:18} ERROR at {tok!r}")
            return
        elif action[0] == "shift":
            _, next_state = action
            print(f"{disp_stack:35} {disp_rest:18} SHIFT  {tok} -> state {next_state}")
            sym_stack.append(tok); stack.append(next_state); pos += 1
        elif action[0] == "reduce":
            rule = action[1]
            pop_n, lhs = RULES[rule]
            for _ in range(pop_n): sym_stack.pop(); stack.pop()
            top = stack[-1]
            goto_state = GOTO[(top, lhs)]
            sym_stack.append(lhs); stack.append(goto_state)
            print(f"{disp_stack:35} {disp_rest:18} REDUCE {rule}")

print("=== n + n * n (right operand tighter) ===")
lr_parse(["n", "+", "n", "*", "n"])
print()
print("=== n * n + n (left operand tighter) ===")
lr_parse(["n", "*", "n", "+", "n"])
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

### Questions to Consider

- In the first trace (`n + n * n`), at what point does the parser shift `*` instead of reducing the first `n + n`? What state and lookahead determine this decision?
- In the RULES table, `"E->E+T": (3, "E")` pops 3 symbols. What are those 3 symbols, and why does popping them from the stack correspond to "recognizing a complete E+T"?
- If you added `"E->E+E"` to the grammar (making addition left-recursive in a second way), which `ACTION` table entry would conflict with an existing one? This is a shift/reduce conflict; identify the state and the competing actions.

---

**LALR(1) is LR(1) with merged states.** Full LR(1) tables distinguish states by lookahead and grow large; LALR(1) merges LR(1) states that share the same item cores, keeping the table compact at the cost of accepting a slightly smaller family of grammars. The calculator grammar from Part 3 builds cleanly under LALR(1): the grammar is deliberately ambiguous (`expr '+' expr` and friends), but every conflict is resolved by the `%left`/`%right` precedence declarations. You can verify with `bison -v calc.y`, which writes the full automaton, every state and item set, to `calc.output`, the same report `--report=all` produces in Part 7.1. Reading that file once, slowly, will teach you more about LR parsing than any lecture, and the experiment below has you do exactly that.

**Conflicts are the diagnostic signal.** A **shift/reduce conflict** means some state sees a lookahead for which both shifting and reducing are table-legal; a **reduce/reduce conflict** means two completed productions compete. (Part 7.1 covers Bison's default resolution, shift, and how to inspect conflicts with `--report=all`.) The calculator grammar produces no unresolved conflicts, but you will manufacture one, deliberately, in a moment, because learning to read conflict reports is the practical skill that separates people who can use parser generators from people who fight them.

> **Watch out!** Bison resolves shift/reduce conflicts silently by defaulting to *shift*, but it still prints a warning. Never ignore that warning: if your grammar has a conflict you did not anticipate, the silent default resolution may produce parse trees that are subtly wrong and very difficult to debug downstream. Always read the `.output` file and confirm that the chosen resolution matches your intent.

---

### Try It: Manufacture a Conflict

Make exactly one of the following edits to `calc.y` from Part 3, then rebuild with `bison -v calc.y`:

1. Comment out the `%left '+' '-'` and `%left '*' '/'` precedence declarations.
2. Add a redundant second copy of the production `expr : '(' expr ')'`.

Using only bison's stderr output and the `.output` file, identify which conflict type each edit produces (shift/reduce or reduce/reduce), and point to the state and item set where it arises. Record the state number and one sentence of explanation, then undo the edit and confirm the conflicts disappear.

---

## A.3 LR(0) Items and the Canonical Collection

An LR(0) item is a production with a bookmark (the dot) that says "I have seen this much of the right-hand side so far." The set of all possible bookmarked states the parser could be in, connected by transitions, forms a finite automaton, the "canonical collection." Understanding this automaton is the key to understanding what shift-reduce conflicts mean and why some grammars are hard to parse.

Two item positions matter most:

$$
E' \to E\ \bullet \qquad \text{(E has been seen; we might reduce)}
$$
$$
E' \to \bullet\ E \qquad \text{(we are about to see E)}
$$

The **closure** of a set of items: if $[A \to \alpha \bullet B \beta]$ is in the set and $B \to \gamma$ is a production, add $[B \to \bullet \gamma]$.

The **goto** function: $\mathrm{goto}(I, X)$ = closure of all items in $I$ where the dot is advanced over $X$.

> **Watch out!** The closure operation adds items for every production of each nonterminal that appears after a dot, including transitively. A single starting item can generate a large closure. Students often compute closure for only the directly referenced nonterminal and miss the transitive additions.

```python
# LR(0) item construction for a simpler grammar: S' -> S, S -> ( S ) | x
simple_grammar = {
    "S'": [["S"]],
    "S":  [["(", "S", ")"], ["x"]],
}

def closure(items, grammar):
    result = set(items)
    changed = True
    while changed:
        changed = False
        for (nt, prod, dot) in list(result):
            if dot < len(prod):
                sym = prod[dot]
                if sym in grammar:
                    for p in grammar[sym]:
                        item = (sym, tuple(p), 0)
                        if item not in result:
                            result.add(item)
                            changed = True
    return frozenset(result)

def goto_set(items, sym, grammar):
    advanced = set()
    for (nt, prod, dot) in items:
        if dot < len(prod) and prod[dot] == sym:
            advanced.add((nt, prod, dot + 1))
    return closure(advanced, grammar) if advanced else frozenset()

# Build all item sets
start_item = ("S'", tuple(simple_grammar["S'"][0]), 0)
start_set  = closure({start_item}, simple_grammar)
states     = [start_set]
state_map  = {start_set: 0}
transitions= {}

to_process = [start_set]
all_syms   = list(simple_grammar.keys()) + ['(', ')', 'x']

while to_process:
    current = to_process.pop()
    s_id    = state_map[current]
    for sym in all_syms:
        g = goto_set(current, sym, simple_grammar)
        if g:
            if g not in state_map:
                state_map[g] = len(states)
                states.append(g)
                to_process.append(g)
            transitions[(s_id, sym)] = state_map[g]

print(f"LR(0) automaton: {len(states)} states")
for sid, items in enumerate(states):
    print(f"\nState {sid}:")
    for nt, prod, dot in sorted(items):
        before = " ".join(prod[:dot])
        after  = " ".join(prod[dot:])
        print(f"  {nt} -> {before} . {after}")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

The ACTION and GOTO tables Bison emits are read straight off this automaton: transitions on terminals become shift entries, transitions on nonterminals become goto entries, and any state containing a dot-at-the-end item becomes a reduce, with the LALR(1) lookahead sets deciding *which* lookahead tokens trigger each reduction. When two of those rules claim the same table cell, you get exactly the shift/reduce and reduce/reduce conflicts described in Part 7.1 and manufactured in the experiment above.
