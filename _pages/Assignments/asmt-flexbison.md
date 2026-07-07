---
layout: assignment
permalink: /Assignments/FlexBison
title: "CS374: Principles of Programming Languages - Flex and Bison"

info:
  coursenum: CS374
  purpose: "To build a small but complete language, Calc, with the industrial tools Flex and Bison — a scanner, a precedence-correct grammar, an AST, and a tree-walking evaluator in C with variables, functions, and recursion."
  tilt:
    task: "Write a Flex scanner and a conflict-free Bison grammar for Calc, build a tagged-union AST and tree-walking evaluator in C with a scoped symbol table, and drive it all from a Makefile with tests."
    criteria: "Assessed on a complete scanner, a precedence- and associativity-correct grammar with no unresolved conflicts, a correct AST evaluator with scoping, and a reproducible build and test suite; see the rubric below for the full breakdown."
  points: 100
  goals:
    - To implement a scanner with Flex that handles all token types including strings, comments, and numeric literals
    - To implement a parser with Bison that produces a correct precedence and associativity hierarchy
    - To build an AST in C and evaluate it with a tree-walking interpreter
    - To handle variables, user-defined functions, and recursive definitions in Flex/Bison
  rubric:
    - weight: 30
      description: Flex Scanner
      preemerging: The scanner does not compile or fails to tokenize the provided test programs
      beginning: The scanner tokenizes most token types but fails on strings, line counting, or multi-character operators
      progressing: The scanner tokenizes all token types correctly with a minor defect such as incorrect line counting or missing a maximal-munch case
      proficient: The scanner correctly handles all token types including strings with escape sequences, single-line and multi-line comments, multi-character operators, and reports line numbers in all error messages; passes all provided test inputs
    - weight: 35
      description: Bison Parser and Precedence
      preemerging: The grammar does not compile or produces shift-reduce conflicts for the provided grammar
      beginning: The grammar compiles but has precedence or associativity errors
      progressing: The grammar handles all operators with correct precedence and associativity but fails on function definitions or block statements
      proficient: The grammar implements the full language with correct precedence (unary minus tightest, then mul/div, then add/sub, then comparison, then logic), correct left-associativity for arithmetic, correct right-associativity for assignment and exponentiation, and produces no unresolved shift-reduce conflicts; handles all provided test programs
    - weight: 25
      description: AST and Evaluator
      preemerging: No AST is constructed; evaluation is done in-line in semantic actions
      beginning: An AST is constructed but the evaluator fails on conditionals, loops, or function calls
      progressing: The AST and evaluator work for all construct types with a minor defect such as incorrect scoping or missing return value handling
      proficient: The AST is a proper recursive data structure with one union-tagged node type per construct; the tree-walking evaluator correctly evaluates all node types including function definitions and recursive calls, with a linked-list symbol table implementing static scope; all provided test programs produce correct output
    - weight: 10
      description: Makefile, Testing, and Writeup
      preemerging: No Makefile; tests are missing; submission is incomplete
      beginning: A Makefile exists but does not correctly chain Flex and Bison; a test exists
      progressing: The Makefile builds correctly from scratch with `make`; tests cover major cases
      proficient: "`make` builds from scratch; `make test` runs all test programs and verifies output against expected files; the README explains the language semantics, lists the token types, and gives the full EBNF grammar as implemented"
  readings:
    - rtitle: "Tutorial: Flex and Bison (Complete)"
      rlink: "https://liascript.github.io/course/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374-Fall2026/gh-pages/_pages/Tutorials/tutorial-flex-bison-complete.md"
    - rtitle: "LL/LR Parsing Activity"
      rlink: "https://liascript.github.io/course/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374-Fall2026/gh-pages/_pages/Activities/liascript-parsertable.md"

tags:
  - flex
  - bison
  - scanner
  - parser
  - languages

---

This assignment builds a calculator language called **Calc** using the industrial tools Flex and Bison, and extends it with variables, user-defined functions, and recursion. The result is a small but complete language implementation in C — the same foundation used by major compilers.

## The Language

**Calc** supports:
- Integer and floating-point arithmetic: `+`, `-`, `*`, `/`, `%`, `^` (right-associative exponentiation)
- Unary minus: `-x`
- Comparison: `< <= > >= == !=` (returning 0 or 1)
- Logic: `&&`, `||`, `!`
- Variables: `x = expr` (assignment expression, like C)
- Conditionals: `if (expr) { stmts }` and `if (expr) { stmts } else { stmts }`
- While loops: `while (expr) { stmts }`
- User-defined functions: `def square(x) { return x * x; }`
- Function calls: `square(5)`
- Print: `print expr;`
- Comments: `# to end of line` and `/* block */`
- String literals for print: `print "hello\n";`

**Operator precedence (tightest first):**
1. Unary `-`, `!`
2. `^` (right-associative)
3. `*`, `/`, `%` (left-associative)
4. `+`, `-` (left-associative)
5. `< <= > >= == !=` (left-associative, non-chaining)
6. `&&` (left-associative)
7. `||` (left-associative)
8. `=` (right-associative, lowest)

## Setup

```
calc/
  calc.l       (Flex scanner)
  calc.y       (Bison grammar)
  ast.h        (AST node declarations)
  ast.c        (AST node constructors and evaluator)
  symtab.h     (symbol table declarations)
  symtab.c     (symbol table implementation)
  Makefile
  tests/       (test programs)
  expected/    (expected outputs for tests)
```

Build: `make` should run `bison -d calc.y`, then `flex calc.l`, then `gcc calc.tab.c lex.yy.c ast.c symtab.c -o calc -lm`.

## Part 1: The Flex Scanner (25 points)

Write `calc.l` handling:

**1a.** Numeric literals: integers (`[0-9]+`) and floats (`[0-9]+\.[0-9]*` and `[0-9]*\.[0-9]+`). Store as `double` in `yylval.dval`.

**1b.** String literals in double quotes with `\"`, `\\`, `\n`, `\t` escape sequences. Store the decoded string in `yylval.sval` (use `strdup`).

**1c.** Identifiers: `[a-zA-Z_][a-zA-Z0-9_]*`. Check against the keyword table; return `IDENT` for non-keywords with `yylval.sval = strdup(yytext)`.

**1d.** Keywords: `if`, `else`, `while`, `def`, `return`, `print` — return their own token types.

**1e.** Multi-character operators: `<=`, `>=`, `==`, `!=`, `&&`, `||` — each a single token. Single-character operators return their character.

**1f.** Single-line comments (`#` to `\n`) and block comments (`/* ... */` — not nested) — skip both.

**1g.** Whitespace — skip. Count newlines for `yylineno` (use `%option yylineno`).

**Test 1:** Run the provided test input through `flex calc.l && gcc lex.yy.c -lfl -o scanner && ./scanner < tests/tokens.txt` and verify every token type and line number.

## Part 2: The Bison Grammar (30 points)

Write `calc.y` with the full language grammar.

**2a.** Declare the `%union` with fields `dval` (double), `sval` (char*), and `node` (your AST node pointer).

**2b.** Declare token types with types: `%token <dval> NUMBER`, `%token <sval> IDENT STRING`, `%token IF ELSE WHILE DEF RETURN PRINT`.

**2c.** Declare operator associativity and precedence using `%left`, `%right`, and `%nonassoc` (use `%right UMINUS` for unary minus). The precedence declarations resolve all shift-reduce conflicts; you should have zero unresolved conflicts.

**2d.** Write the grammar rules bottom-up (tightest binding first): `primary` → `unary` → `power` → `muldiv` → `addsub` → `comparison` → `logic_and` → `logic_or` → `assignment` → `expr`. Each rule's semantic action builds an AST node.

**2e.** Statement rules: `stmt` for each statement type; `block` for `{ stmt_list }`; `program` for the top-level sequence.

**Test 2:** `echo "print 2 + 3 * 4;" | ./calc` should print `14.000000`. `echo "print 2 ^ 3 ^ 2;" | ./calc` should print `512.000000` (right-associative: `2^(3^2) = 2^9`).

## Part 3: The AST in C (30 points)

Define `ast.h` with a tagged union:

```c
// ast.h
typedef enum {
    AST_NUM, AST_STR, AST_VAR, AST_BINOP, AST_UNOP,
    AST_ASSIGN, AST_IF, AST_WHILE, AST_BLOCK, AST_SEQ,
    AST_PRINT, AST_RETURN, AST_CALL, AST_DEF, AST_PROGRAM
} AstKind;

typedef struct Ast {
    AstKind kind;
    int     line;
    union {
        double  numval;
        char   *strval;
        struct { char op[4]; struct Ast *left; struct Ast *right; } binop;
        struct { char op[4]; struct Ast *operand; }               unop;
        struct { struct Ast *cond; struct Ast *then; struct Ast *els; } ifnode;
        struct { struct Ast *cond; struct Ast *body; }              whilenode;
        struct { struct Ast **stmts; int count; }                   block;
        struct { char *name; char **params; int nparams; struct Ast *body; } def;
        struct { char *name; struct Ast **args; int nargs; }        call;
    } u;
} Ast;

Ast *ast_num(double val, int line);
Ast *ast_str(char *val, int line);
Ast *ast_var(char *name, int line);
Ast *ast_binop(char *op, Ast *left, Ast *right, int line);
Ast *ast_unop(char *op, Ast *operand, int line);
Ast *ast_assign(char *name, Ast *val, int line);
Ast *ast_if(Ast *cond, Ast *then, Ast *els, int line);
Ast *ast_while(Ast *cond, Ast *body, int line);
Ast *ast_block(Ast **stmts, int count, int line);
Ast *ast_print(Ast *val, int line);
Ast *ast_return(Ast *val, int line);
Ast *ast_call(char *name, Ast **args, int nargs, int line);
Ast *ast_def(char *name, char **params, int nparams, Ast *body, int line);
```

Implement `ast_eval(Ast *node, SymTab *env)` in `ast.c` that walks the tree and returns a `double` (strings print directly via `print`). For function calls: look up the `AST_DEF` node in the symbol table, bind parameters to arguments in a new scope, evaluate the body, and catch `RETURN` signals via `longjmp` (or a return-value global).

**Test 3:** The provided test programs including recursive Fibonacci must produce correct output.

## Part 4: Symbol Table (5 points)

Implement `symtab.h`/`symtab.c` as a linked-list chain of scopes (exactly the Environment from your Python interpreter, in C):

```c
typedef struct Frame { char *name; double value; struct Frame *next; } Frame;
typedef struct SymTab { Frame *vars; struct SymTab *parent; } SymTab;

SymTab *symtab_new(SymTab *parent);
void    symtab_define(SymTab *env, char *name, double val);
double  symtab_lookup(SymTab *env, char *name, int line);
void    symtab_assign(SymTab *env, char *name, double val, int line);
void    symtab_free(SymTab *env);
```

**Test 4:** The shadowing program (nested scopes with same-named variables) must produce correct output as documented in the test suite.

## Part 5: Makefile and Tests (10 points)

Provide a `Makefile` with:
- `make` builds `./calc` from scratch
- `make test` runs every `.calc` file in `tests/` and diffs output against `expected/`
- `make clean` removes all generated files

Provide at least eight test programs:
1. Arithmetic with all operators and precedence verification
2. Variables and assignment
3. If/else (including dangling-else resolution — document your choice)
4. While loop with accumulator
5. Recursive function (Fibonacci)
6. Function with multiple parameters
7. Nested function calls
8. String printing and escape sequences

## Deliverables

Submit a ZIP containing all `.l`, `.y`, `.h`, `.c` files, the `Makefile`, the `tests/` and `expected/` directories, and a `README.md` of approximately one page that:
- Lists all token types with their patterns
- Gives the complete EBNF grammar as implemented
- Documents the dangling-else resolution decision
- Explains how recursion is handled in the AST evaluator

## Reflection Prompts

- Flex and Bison's `%union` required you to decide the types of all semantic values up front. How did this constraint differ from Python's duck typing, and which approach made which bugs easier to catch?
- You implemented the same precedence rules your Python parser enforced via grammar layers. Compare the two approaches: which felt more natural, and which was easier to change after the fact?
- Your C symbol table and your Python `Environment` implement the same data structure. What did you gain from the strongly-typed C version, and what did you lose?
- If collaboration with a buddy was permitted, did you work with a buddy on this assignment? If so, who? If not, do you certify that this submission represents your own original work? Please identify any and all portions of your submission that were not originally written by you.
- Approximately how many hours did this assignment take?
