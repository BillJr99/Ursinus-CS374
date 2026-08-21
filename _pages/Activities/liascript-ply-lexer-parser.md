<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374/gh-pages/_pages/Activities/liascript-ply-lexer-parser.md or locally via https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374/gh-pages/_pages/Activities/liascript-ply-lexer-parser.md

import: https://raw.githubusercontent.com/liascript/CodeRunner/master/README.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

# Interactive Lexing and Parsing with PLY (Python Lex-Yacc)

> **Note:** this activity's code cells install PLY at runtime; in the browser CodeRunner this may fail without network access; download and run locally if cells error. This activity is a companion to the [Flex and Bison tutorial](https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374/gh-pages/_pages/Tutorials/tutorial-flex-bison-complete.md).

PLY (Python Lex-Yacc) is Flex and Bison reimplemented in pure Python: you write the same declarative grammar rules and get the same LALR(1) parsing power, but without a C toolchain, a build step, or generated `.c` files to manage. Think of it as Flex/Bison with Python as the host language; the concepts translate one-to-one, and every rule you write here has a direct counterpart in a `.l` or `.y` file. That makes PLY ideal for rapid prototyping in this course: you can explore a grammar idea, run it instantly in the browser, and see the token stream or AST before committing to a full C-based toolchain.

## Learning Goals

By the end of this activity, you will be able to:

- Write PLY lexer rules using regular-expression strings and docstring-regex functions, and explain how PLY selects among competing rules
- Write PLY parser rules as LALR(1) grammar productions with semantic actions that construct an AST
- Declare operator precedence and associativity in PLY to resolve shift-reduce conflicts without rewriting the grammar
- Trace a PLY-generated parser on a given input token stream and predict the AST it produces
- Translate an equivalent Flex/Bison grammar into its PLY form and identify the structural correspondences between the two tools
- Implement error recovery in a PLY parser and explain how error tokens allow parsing to resume after a syntax error

## Before You Begin

Make sure you are comfortable with the following before starting this activity:

- **Python decorators and docstrings**: PLY uses docstrings as the grammar-rule specification language, and it relies on Python's function-object mechanism to collect rules at module load time. If docstrings feel unfamiliar, review how `def f(): """..."""` exposes `f.__doc__` before proceeding.
- **BNF / EBNF grammar notation**: You should be able to read a production such as `expr : expr PLUS term | term` and identify the non-terminal on the left, the terminals on the right, and what "alternative" means. PLY's docstrings use this notation directly.
- **What a token is**: A token is a (type, value) pair produced by the lexer. For example, the string `42` becomes `(NUMBER, 42.0)`. The parser never sees raw characters; it works entirely with the token stream.

## Overview

This POGIL activity teaches lexical analysis and parsing using **PLY (Python Lex-Yacc)**, a pure-Python library that implements the same algorithms as the classic Flex and Bison tools you have studied. Every code example in this activity runs directly in your browser, letting you experiment with grammars, tokens, and abstract syntax trees without a C compiler or build system.

By the end of this activity you will be able to:

- Write PLY lexer rules using regex strings and function docstrings
- Write PLY parser rules using LALR(1) grammar productions
- Declare operator precedence to resolve shift-reduce conflicts
- Build and traverse an Abstract Syntax Tree (AST)
- Translate a Flex/Bison grammar to its PLY equivalent
- Implement basic error recovery and diagnostics in a parser

**How to use this activity.** Work in groups of 3-4. Read each Model carefully, run the code, observe the output, and then answer the Critical Thinking Questions (CTQs) before moving to the next Model. The Exercises at the end require you to write new code.

---

## Model 1: Lexer Basics, Token Recognition

In this model you will write your first PLY lexer: the component that reads raw source text and produces a stream of typed tokens. Picture the lexer as a bouncer at a door: it looks at each character, decides what "kind" of thing it is (a number, an identifier, an operator), and stamps it with a type before passing it on to the parser. The code below is the direct Python equivalent of a Flex `.l` file: string variables play the role of bare Flex patterns, and functions with docstrings play the role of Flex pattern-action pairs.

A **lexer** (or scanner) converts a raw character stream into a sequence of **tokens**. In Flex you write rules in a `.l` file; in PLY you write them as Python variables and functions inside a normal `.py` file.

The two mechanisms PLY provides are:

- **String variables** (`t_PLUS = r'\+'`) for simple tokens that need no extra processing.
- **Functions with docstring regexes** (`def t_NUMBER(t): r'\d+(\.\d+)?'`) when you need to transform the matched value or take a special action.

> **Watch out!** PLY uses a function's **docstring** as its grammar or lexer rule: `def t_NUMBER(t): r'\d+'` means the docstring `r'\d+'` *is* the regex pattern. This is unusual Python; it has nothing to do with documentation. If you accidentally put the pattern in a comment or a regular string variable, PLY will silently ignore the rule.

PLY always tries the **longest match first**. When two rules could match the same input, PLY chooses the one whose regex is defined first (for function rules) or whose pattern is longer (for string rules).

```python
import subprocess
subprocess.run(["pip", "install", "ply", "-q"], capture_output=True)
import ply.lex as lex

# All token names must appear in the tokens tuple
reserved = {
    'if': 'IF',
    'else': 'ELSE',
    'while': 'WHILE',
    'return': 'RETURN',
}

tokens = (
    'NUMBER', 'ID',
    'PLUS', 'MINUS', 'TIMES', 'DIVIDE',
    'LPAREN', 'RPAREN', 'ASSIGN',
) + tuple(reserved.values())

# Simple string rules - PLY compiles these into the master regex
t_PLUS   = r'\+'
t_MINUS  = r'-'
t_TIMES  = r'\*'
t_DIVIDE = r'/'
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_ASSIGN = r'='

# t_ignore is a special string: characters to silently skip
t_ignore = ' \t'

# Function rule: docstring is the regex; gives us a chance to convert the value
def t_NUMBER(t):
    r'\d+(\.\d+)?'
    t.value = float(t.value)   # convert matched string to a Python float
    return t

# Function rule for identifiers - checks against the reserved word dict
def t_ID(t):
    r'[a-zA-Z_][a-zA-Z0-9_]*'
    t.type = reserved.get(t.value, 'ID')   # promote reserved words to their own type
    return t

# Error handler - called when no rule matches the current character
def t_error(t):
    print(f"Illegal character {t.value[0]!r} at position {t.lexpos}")
    t.lexer.skip(1)

lexer = lex.lex()

# Tokenize a sample expression
source = 'x = 3 + 4.5 * (y - 1)'
lexer.input(source)

print(f"Tokenizing: {source!r}\n")
print(f"{'TYPE':<12} {'VALUE'}")
print("-" * 25)
for tok in lexer:
    print(f"{tok.type:<12} {repr(tok.value)}")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

### CTQs, Model 1

1. In Flex, lexer rules are regex patterns written in a `.l` file with the form `pattern   { action }`. How does PLY represent the same information, and where does the "action" live in PLY's approach?

2. Why does PLY use function-based rules (with docstrings) for some tokens and string variables for others? When would you choose each form?

3. What does PLY do with the `reserved` dictionary inside `t_ID`? Without it, how would PLY treat the word `if` in the input stream?

4. What does the `t_error` function allow you to do with an illegal character? What happens if you remove the `t.lexer.skip(1)` call?

---

## Model 2: Handling Whitespace, Comments, and Strings

Every real source file contains text the parser should never see: spaces, newlines, comments, and the quotation marks around string literals. This model shows the three PLY techniques for silently consuming that "noise" before tokens reach the parser. It also demonstrates line-number tracking, something PLY does not do automatically, so you have to maintain it yourself using `t.lexer.lineno`. Getting this right pays off immediately when error messages need to tell a user which line of their program is wrong.

Real source files contain characters that the parser never sees: whitespace, comments, and sometimes the quotes surrounding string literals. A lexer must handle these gracefully without crashing or leaking junk tokens to the parser.

PLY provides three mechanisms for silent consumption:

- `t_ignore`: a string of single characters; each is skipped with no function call.
- A function rule that returns `None` (or falls off the end): the token is consumed but not emitted.
- A function rule that modifies `t.value` before returning: useful for stripping delimiters from string literals.

> **Watch out!** Both `t_error` (in the lexer) and `p_error` (in the parser) are **mandatory**. If either is missing, PLY will raise an exception the moment it encounters an unrecognized character or an unexpected token. You do not get a helpful message; you get a crash. Always define both, even if the body is just `pass` or a `print` statement.

Observe how the code below tracks line numbers using the `t.lexer.lineno` attribute, which PLY does *not* manage automatically.

```python
import subprocess
subprocess.run(["pip", "install", "ply", "-q"], capture_output=True)
import ply.lex as lex

reserved = {'if': 'IF', 'else': 'ELSE', 'def': 'DEF', 'return': 'RETURN'}
tokens = ('NUMBER', 'STRING', 'ID', 'PLUS', 'MINUS', 'EQ', 'NEWLINE') + tuple(reserved.values())

t_PLUS   = r'\+'
t_MINUS  = r'-'
t_EQ     = r'='
t_ignore = ' \t'

def t_NEWLINE(t):
    r'\n+'
    t.lexer.lineno += len(t.value)
    # No return statement - the token is consumed but not emitted to the parser

def t_COMMENT(t):
    r'\#[^\n]*'
    pass   # discard: return None implicitly

def t_STRING(t):
    r'"[^"]*"'
    t.value = t.value[1:-1]   # strip the surrounding double-quotes
    return t

def t_NUMBER(t):
    r'\d+(\.\d+)?'
    t.value = float(t.value)
    return t

def t_ID(t):
    r'[a-zA-Z_][a-zA-Z0-9_]*'
    t.type = reserved.get(t.value, 'ID')
    return t

def t_error(t):
    print(f"Illegal character {t.value[0]!r} at line {t.lexer.lineno}")
    t.lexer.skip(1)

lexer = lex.lex()

source = '''
# This is a comment
x = 42
message = "hello world"  # inline comment
if x
'''

lexer.input(source)
print(f"{'LINE':>4}  {'TYPE':<12} {'VALUE'}")
print("-" * 35)
for tok in lexer:
    print(f"{tok.lineno:>4}  {tok.type:<12} {repr(tok.value)}")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

### CTQs, Model 2

1. How does `t_ignore` simplify whitespace handling compared to writing an explicit rule? What kinds of characters are *not* suitable for `t_ignore`?

2. The `t_COMMENT` function has `pass` instead of `return t`. Why does this cause the comment to disappear from the token stream? What would happen if you wrote `return t` instead?

3. PLY orders function-based rules by the order they appear in the source file and string rules by pattern length (longest first). Given that both `t_ID` and `t_NUMBER` can match at the start of a new input position, how does PLY decide which one to try first for the input `42`?

4. The `t_NEWLINE` function increments `t.lexer.lineno`. Why is tracking line numbers important for error messages produced later, during parsing?

---

## Model 3: A Recursive Descent in PLY, Arithmetic Expressions

Now that the lexer can produce tokens, you need a parser to enforce grammatical structure. This model introduces PLY's parser, which works exactly like Bison: you write grammar productions (here, as docstrings), declare operator precedence, and PLY generates an LALR(1) parse table behind the scenes. For now the parser evaluates arithmetic directly (no AST yet) so you can focus on reading the grammar rules and precedence declarations before adding the extra layer of tree construction in Model 4.

A **parser** checks that a token stream conforms to a grammar and (optionally) computes a value or builds a data structure. PLY implements **LALR(1)** parsing, the same algorithm used inside GNU Bison.

Each grammar rule is a Python function whose **docstring** is the production. The body sets `p[0]` (the left-hand side) from the indexed components `p[1]`, `p[2]`, ... (the right-hand side symbols, left to right).

**Operator precedence** is declared as a tuple of tuples. Earlier entries have *lower* precedence; later entries have *higher* precedence. This exactly mirrors the `%left` / `%right` / `%nonassoc` declarations in a Bison file.

> **Watch out!** Token type names in PLY are **case-sensitive** and must match exactly between the lexer and the parser. If you name a token `Plus` in the `tokens` tuple but write `t_PLUS = r'\+'` in the lexer, PLY will silently define two different tokens and your grammar rules will never fire. The convention is ALL_CAPS for token names throughout.

```python
import subprocess
subprocess.run(["pip", "install", "ply", "-q"], capture_output=True)
import ply.lex as lex
import ply.yacc as yacc

# --- Lexer ---
tokens = ('NUMBER', 'PLUS', 'MINUS', 'TIMES', 'DIVIDE', 'LPAREN', 'RPAREN')
t_PLUS    = r'\+'
t_MINUS   = r'-'
t_TIMES   = r'\*'
t_DIVIDE  = r'/'
t_LPAREN  = r'\('
t_RPAREN  = r'\)'
t_ignore  = ' \t\n'

def t_NUMBER(t):
    r'\d+(\.\d+)?'
    t.value = float(t.value)
    return t

def t_error(t):
    t.lexer.skip(1)

lexer = lex.lex()

# --- Precedence (low -> high) ---
precedence = (
    ('left', 'PLUS', 'MINUS'),      # lowest
    ('left', 'TIMES', 'DIVIDE'),    # higher
    ('right', 'UMINUS'),            # highest (phantom token for unary minus)
)

# --- Parser rules ---
def p_expr_binop(p):
    '''expr : expr PLUS expr
            | expr MINUS expr
            | expr TIMES expr
            | expr DIVIDE expr'''
    ops = {'+': p[1] + p[3], '-': p[1] - p[3],
           '*': p[1] * p[3], '/': p[1] / p[3]}
    p[0] = ops[p[2]]

def p_expr_uminus(p):
    'expr : MINUS expr %prec UMINUS'
    p[0] = -p[2]

def p_expr_number(p):
    'expr : NUMBER'
    p[0] = p[1]

def p_expr_group(p):
    'expr : LPAREN expr RPAREN'
    p[0] = p[2]

def p_error(p):
    if p:
        print(f"Syntax error at token {p.type!r} ({p.value!r})")
    else:
        print("Syntax error at end of input")

parser = yacc.yacc(debug=False, write_tables=False, errorlog=yacc.NullLogger())

# --- Run tests ---
tests = [
    "3 + 4 * 2",          # precedence: 3 + (4*2) = 11
    "(3 + 4) * 2",        # grouping overrides: 7 * 2 = 14
    "10 / 2 - 1",         # left-assoc: (10/2) - 1 = 4
    "-(3 + 4)",           # unary minus: -7
    "2 * 3 + 4 * 5",      # 6 + 20 = 26
]

print(f"{'Expression':<24} {'Result'}")
print("-" * 35)
for expr in tests:
    result = parser.parse(expr)
    print(f"{expr:<24} {result}")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

### CTQs, Model 3

1. In the grammar rule `expr : expr PLUS expr`, both `expr` sub-expressions look identical. How does PLY know which one is the left operand and which is the right? Why would this rule be ambiguous without the `precedence` tuple?

2. What does `%prec UMINUS` do in `'expr : MINUS expr %prec UMINUS'`? Why is a "phantom token" needed to handle unary minus, rather than a token that actually appears in the input?

3. How do the entries `('left', 'PLUS', 'MINUS')` and `('left', 'TIMES', 'DIVIDE')` in the `precedence` tuple resolve a shift-reduce conflict? Trace what happens when the parser has seen `3 + 4` on its stack and sees `*` as the next token.

4. PLY uses LALR(1) parsing internally, just like Bison. What does "LALR(1)" stand for? What does the "(1)" mean in practical terms?

---

## Model 4: Building an AST with PLY

Direct evaluation in parser actions (as in Model 3) is convenient for a pocket calculator, but it throws away all structure the moment it computes a number. An Abstract Syntax Tree preserves that structure as a Python object you can inspect, transform, or evaluate multiple times. This model replaces the arithmetic in `p[0] = p[1] + p[3]` with `p[0] = BinOp('+', p[1], p[3])`, a tiny change in code that has a large impact on what you can do with the result downstream.

Evaluating an expression directly in parser actions works for a calculator, but real compilers and interpreters need a data structure they can analyze, optimize, or interpret later. An **Abstract Syntax Tree (AST)** captures the hierarchical structure of a program without the concrete syntax details (parentheses, commas, keywords as punctuation).

PLY is well suited to AST construction: each `p_*` function sets `p[0]` to whatever Python object you like, including a dataclass node. The parent rule receives that object through its own `p[i]` slot.

```python
import subprocess
subprocess.run(["pip", "install", "ply", "-q"], capture_output=True)
import ply.lex as lex
import ply.yacc as yacc
from dataclasses import dataclass
from typing import Any

# --- AST node types ---
@dataclass
class Num:
    value: float

@dataclass
class Var:
    name: str

@dataclass
class BinOp:
    op: str
    left: Any
    right: Any

@dataclass
class Assign:
    name: str
    expr: Any

# --- Pretty-printer ---
def pprint_ast(node, indent=0):
    pad = "  " * indent
    if isinstance(node, Num):
        print(f"{pad}Num({node.value})")
    elif isinstance(node, Var):
        print(f"{pad}Var({node.name!r})")
    elif isinstance(node, BinOp):
        print(f"{pad}BinOp({node.op!r})")
        pprint_ast(node.left,  indent + 1)
        pprint_ast(node.right, indent + 1)
    elif isinstance(node, Assign):
        print(f"{pad}Assign({node.name!r})")
        pprint_ast(node.expr, indent + 1)

# --- Lexer ---
tokens = ('NUMBER', 'ID', 'PLUS', 'MINUS', 'TIMES', 'DIVIDE',
          'LPAREN', 'RPAREN', 'ASSIGN')

t_PLUS   = r'\+'
t_MINUS  = r'-'
t_TIMES  = r'\*'
t_DIVIDE = r'/'
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_ASSIGN = r'='
t_ignore = ' \t\n'

def t_NUMBER(t):
    r'\d+(\.\d+)?'
    t.value = float(t.value)
    return t

def t_ID(t):
    r'[a-zA-Z_]\w*'
    return t

def t_error(t):
    t.lexer.skip(1)

lexer = lex.lex()

# --- Parser (builds AST nodes instead of evaluating) ---
precedence = (
    ('left', 'PLUS', 'MINUS'),
    ('left', 'TIMES', 'DIVIDE'),
)

def p_stmt_assign(p):
    'stmt : ID ASSIGN expr'
    p[0] = Assign(p[1], p[3])

def p_stmt_expr(p):
    'stmt : expr'
    p[0] = p[1]

def p_expr_binop(p):
    '''expr : expr PLUS expr
            | expr MINUS expr
            | expr TIMES expr
            | expr DIVIDE expr'''
    p[0] = BinOp(p[2], p[1], p[3])

def p_expr_num(p):
    'expr : NUMBER'
    p[0] = Num(p[1])

def p_expr_var(p):
    'expr : ID'
    p[0] = Var(p[1])

def p_expr_group(p):
    'expr : LPAREN expr RPAREN'
    p[0] = p[2]

def p_error(p):
    print(f"Syntax error near {p}")

parser = yacc.yacc(debug=False, write_tables=False, errorlog=yacc.NullLogger())

# --- Parse and display trees ---
sources = ["x = 3 + 4 * 2", "(a + b) * c", "y = (x - 1) / 2"]
for src in sources:
    print(f"\nAST for: {src!r}")
    ast = parser.parse(src)
    pprint_ast(ast)
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

### CTQs, Model 4

1. Why is building an AST generally better than evaluating immediately inside parser actions? Give at least two reasons that matter for a real programming language implementation.

2. In `p_expr_binop`, `p[0]` is assigned a `BinOp` node. How does PLY pass this value up to a rule that references `expr` as one of its right-hand-side symbols?

3. The AST for `x = 3 + 4 * 2` should be `Assign('x', BinOp('+', Num(3.0), BinOp('*', Num(4.0), Num(2.0))))`. Verify this by tracing the precedence rules. Which sub-tree is constructed first, and why?

4. What would you need to add to this grammar (lexer tokens, parser rules, and AST nodes) to handle an `if/else` expression of the form `if cond then a else b`?

---

## Model 5: A Complete Mini Language, Flex/Bison -> PLY Translation

This model ties everything together into a small but complete language: lexer, parser, AST, and evaluator all working as a unit. Its main purpose is to make the Flex/Bison-to-PLY translation concrete: inline comments in the code label every PLY construct with its Bison or Flex counterpart, so you can cross-reference the two tool families side by side. After working through this model you should be able to take a `.l`/`.y` grammar you have already written and port it to PLY, or vice versa, with confidence.

This model shows the **direct correspondence** between Flex/Bison syntax and PLY. Comments in the code mark each Flex or Bison equivalent so you can see exactly what changed.

The mini language supports variables, `let` bindings, `if-else` conditionals, and a `print` statement. After parsing, an evaluator walks the AST and computes the result, cleanly separated from the parser, exactly as the Dragon Book prescribes.

```python
import subprocess
subprocess.run(["pip", "install", "ply", "-q"], capture_output=True)
import ply.lex as lex
import ply.yacc as yacc
from dataclasses import dataclass
from typing import Any, Optional

# ===== AST NODES =====
@dataclass
class Num:   value: float
@dataclass
class Var:   name: str
@dataclass
class BinOp: op: str; left: Any; right: Any
@dataclass
class IfExpr: cond: Any; then_e: Any; else_e: Any
@dataclass
class Let:   name: str; val: Any; body: Any
@dataclass
class Print: expr: Any

# ===== LEXER =====
# Flex equivalent:
#   "let"         { return LET; }
#   "if"          { return IF; }
#   "else"        { return ELSE; }
#   "in"          { return IN; }
#   "print"       { return PRINT; }
#   [0-9]+        { yylval.fval = atof(yytext); return NUMBER; }
#   [a-zA-Z_]\w*  { yylval.sval = strdup(yytext); return ID; }
# PLY equivalent: (reserved dict + t_ID below)
reserved = {
    'let':   'LET',
    'if':    'IF',
    'else':  'ELSE',
    'in':    'IN',
    'print': 'PRINT',
}
tokens = ['NUMBER', 'ID', 'PLUS', 'MINUS', 'TIMES',
          'EQ', 'EQEQ', 'LT', 'LPAREN', 'RPAREN'] + list(reserved.values())

# Flex: "+"  { return PLUS; }    PLY:
t_PLUS   = r'\+'
t_MINUS  = r'-'
t_TIMES  = r'\*'
t_EQEQ   = r'=='    # must come before t_EQ (longer match wins for strings)
t_EQ     = r'='
t_LT     = r'<'
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_ignore = ' \t\n'

def t_NUMBER(t):
    r'\d+(\.\d+)?'
    # Flex: yylval.fval = atof(yytext);
    t.value = float(t.value)
    return t

def t_ID(t):
    r'[a-zA-Z_]\w*'
    # Flex handles this with separate rules per keyword;
    # PLY uses a single rule + dict lookup:
    t.type = reserved.get(t.value, 'ID')
    return t

def t_error(t):
    t.lexer.skip(1)

lexer = lex.lex()

# ===== PARSER =====
# Bison equivalent:
#   %left  PLUS MINUS
#   %left  TIMES
#   %left  EQEQ LT
# PLY equivalent:
precedence = (
    ('left', 'PLUS', 'MINUS'),
    ('left', 'TIMES'),
    ('left', 'EQEQ', 'LT'),
)

# Bison: stmt : PRINT expr  { $$ = make_print($2); }
def p_stmt_print(p):
    'stmt : PRINT expr'
    p[0] = Print(p[2])

def p_stmt_expr(p):
    'stmt : expr'
    p[0] = p[1]

# Bison: expr : LET ID '=' expr IN expr  { $$ = make_let($2,$4,$6); }
def p_expr_let(p):
    'expr : LET ID EQ expr IN expr'
    p[0] = Let(p[2], p[4], p[6])

# Bison: expr : IF expr expr ELSE expr  { $$ = make_if($2,$3,$5); }
def p_expr_if(p):
    'expr : IF expr expr ELSE expr'
    p[0] = IfExpr(p[2], p[3], p[5])

def p_expr_binop(p):
    '''expr : expr PLUS  expr
            | expr MINUS expr
            | expr TIMES expr
            | expr EQEQ  expr
            | expr LT    expr'''
    p[0] = BinOp(p[2], p[1], p[3])

def p_expr_num(p):
    'expr : NUMBER'
    p[0] = Num(p[1])

def p_expr_var(p):
    'expr : ID'
    p[0] = Var(p[1])

def p_expr_paren(p):
    'expr : LPAREN expr RPAREN'
    p[0] = p[2]

def p_error(p):
    print(f"Syntax error: {p}")

# yacc.NullLogger() suppresses the conflict warnings printed to stderr
parser = yacc.yacc(debug=False, write_tables=False, errorlog=yacc.NullLogger())

# ===== EVALUATOR =====
def evaluate(node, env=None):
    if env is None:
        env = {}
    if isinstance(node, Num):
        return node.value
    if isinstance(node, Var):
        if node.name not in env:
            raise NameError(f"Unbound variable: {node.name!r}")
        return env[node.name]
    if isinstance(node, BinOp):
        l, r = evaluate(node.left, env), evaluate(node.right, env)
        return {'+': l+r, '-': l-r, '*': l*r,
                '==': float(l == r), '<': float(l < r)}[node.op]
    if isinstance(node, IfExpr):
        return (evaluate(node.then_e, env)
                if evaluate(node.cond, env)
                else evaluate(node.else_e, env))
    if isinstance(node, Let):
        v = evaluate(node.val, env)
        return evaluate(node.body, {**env, node.name: v})
    if isinstance(node, Print):
        v = evaluate(node.expr, env)
        print(v)
        return v
    raise ValueError(f"Unknown node type: {type(node)}")

# ===== TEST PROGRAMS =====
tests = [
    "let x = 3 in let y = 4 in x + y",      # nested let -> 7.0
    "if 5 < 10 6 else 0",                    # if-else -> 6.0
    "print 3 + 4 * 2",                       # print -> 11.0
    "let a = 2 in let b = 3 in a * b + 1",  # -> 7.0
]

for prog in tests:
    try:
        ast = parser.parse(prog)
        result = evaluate(ast)
        print(f"  {prog!r}")
        print(f"    => {result}\n")
    except Exception as e:
        print(f"  {prog!r} => Error: {e}\n")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

### CTQs, Model 5

1. The code comments show Flex/Bison equivalents side by side with their PLY counterparts. For the `let` expression rule, map each element of the Bison action `$$ = make_let($2,$4,$6)` to the corresponding PLY code. What are `$2`, `$4`, and `$6` in PLY notation?

2. In the `p_expr_if` rule `'expr : IF expr expr ELSE expr'`, there is no explicit delimiter between the condition and the "then" branch. How does PLY (and Bison) determine where the condition expression ends and the then-expression begins? When would this be ambiguous?

3. What does `yacc.NullLogger()` suppress, and why is suppressing it acceptable here but might be a bad idea during grammar development?

4. The language currently has no `lambda` expression. Write the PLY grammar rule (the function with docstring) for a lambda of the form `fun x -> body`. What new tokens would you need to add to the lexer?

---

## Model 6: Error Recovery and Diagnostics

So far every model assumed the input was valid. Real programs are not: users make typos, forget closing parentheses, and write `3 + * 2` by accident. This model shows how PLY's built-in `error` token lets your parser absorb a mistake, emit a diagnostic, and keep parsing the rest of the input rather than crashing on the first problem. The mechanism is the same one Bison uses: PLY's error-recovery machinery is one of the closest structural parallels between the two tools.

A production compiler does not stop at the first syntax error: it tries to **recover** and continue parsing so it can report multiple errors in one run. PLY supports error recovery through a special `error` token that can appear on the right-hand side of grammar rules.

When PLY's parser encounters an unexpected token:

1. It calls `p_error(p)` with the offending token.
2. It enters "error mode" and pops states off the parse stack until it finds a state that can shift an `error` token.
3. If a rule like `'expr : error'` matches, parsing resumes from that point.
4. Calling `p.parser.errok()` resets the error state so the next error will also be reported.

```python
import subprocess
subprocess.run(["pip", "install", "ply", "-q"], capture_output=True)
import ply.lex as lex
import ply.yacc as yacc

tokens = ('NUMBER', 'PLUS', 'MINUS', 'TIMES',
          'LPAREN', 'RPAREN', 'SEMICOLON', 'ID')

t_PLUS      = r'\+'
t_MINUS     = r'-'
t_TIMES     = r'\*'
t_LPAREN    = r'\('
t_RPAREN    = r'\)'
t_SEMICOLON = r';'
t_ignore    = ' \t\n'

errors_found = []

def t_NUMBER(t):
    r'\d+(\.\d+)?'
    t.value = float(t.value)
    return t

def t_ID(t):
    r'[a-zA-Z_]\w*'
    return t

def t_error(t):
    errors_found.append(
        f"Illegal character {t.value[0]!r} at position {t.lexpos}"
    )
    t.lexer.skip(1)

lexer = lex.lex()

precedence = (
    ('left', 'PLUS', 'MINUS'),
    ('left', 'TIMES'),
)

def p_program_multi(p):
    'program : program SEMICOLON stmt'
    p[0] = (p[1] or []) + p[3]

def p_program_single(p):
    'program : stmt'
    p[0] = p[1]

def p_stmt(p):
    'stmt : expr'
    p[0] = [p[1]]

def p_expr_binop(p):
    '''expr : expr PLUS  expr
            | expr MINUS expr
            | expr TIMES expr'''
    ops = {'+': p[1] + p[3], '-': p[1] - p[3], '*': p[1] * p[3]}
    p[0] = ops[p[2]]

def p_expr_num(p):
    'expr : NUMBER'
    p[0] = p[1]

def p_expr_group(p):
    'expr : LPAREN expr RPAREN'
    p[0] = p[2]

def p_expr_error(p):
    'expr : error'
    # Error recovery: use 0 as a placeholder so parsing can continue
    errors_found.append(f"Bad expression (recovered with placeholder 0)")
    p[0] = 0

def p_error(p):
    if p:
        errors_found.append(
            f"Syntax error at token {p.type!r} ({p.value!r})"
        )
        p.parser.errok()   # allow the next error to be reported too
    else:
        errors_found.append("Syntax error at end of input")

parser = yacc.yacc(debug=False, write_tables=False, errorlog=yacc.NullLogger())

programs = [
    "3 + 4 ; 10 * 2",        # valid - two statements
    "3 + ; 5 * 2",            # syntax error: missing right operand
    "3 + 4 ; @ ; 5",          # lex error (@), then valid statement
    "( 1 + 2",                # unmatched parenthesis
]

for prog in programs:
    errors_found.clear()
    result = parser.parse(prog, lexer=lexer.clone())
    print(f"Input:  {prog!r}")
    print(f"Result: {result}")
    if errors_found:
        for e in errors_found:
            print(f"  ERROR: {e}")
    else:
        print("  (no errors)")
    print()
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

### CTQs, Model 6

1. What is "error recovery" in parsing, and why is it preferable to stopping at the first error when compiling a large source file?

2. The rule `'expr : error'` allows the parser to consume a bad expression and substitute a placeholder value. What does PLY do internally when it encounters the special `error` token in a rule's right-hand side?

3. What does `p.parser.errok()` do, and what would happen if you removed it? Run the code with it removed (you can add a `# ` to comment out that line) to observe the difference.

4. When would you want a parser to **stop immediately** on the first error (as an interpreter might), rather than recovering and continuing (as a batch compiler does)?

---

## Multiple Choice

Which statement best describes what `t_ignore = ' \t'` does in a PLY lexer?

[( )] It raises an error whenever a space or tab is found in the input.
[(X)] It silently discards space and tab characters without calling any rule function.
[( )] It converts spaces and tabs into WHITESPACE tokens.
[( )] It causes PLY to report an illegal-character warning for spaces and tabs.

---

Given the PLY declaration `precedence = (('left', 'PLUS', 'MINUS'), ('left', 'TIMES', 'DIVIDE'))`, what does PLY do when parsing `3 + 4 * 2` and the parser has `3 + 4` on its stack with `*` as the lookahead token?

[( )] It reduces `3 + 4` immediately because `+` was seen first.
[(X)] It shifts `*` because `TIMES` has higher precedence than `PLUS`.
[( )] It reports a shift-reduce conflict and halts.
[( )] It shifts `*` because all tokens shift before any reduction.

---

LALR(1) and LL(1) are both parsing strategies that use one token of lookahead. Which statement correctly distinguishes them?

[( )] LL(1) is bottom-up; LALR(1) is top-down.
[( )] Both are top-down; LALR(1) uses a larger lookahead set.
[(X)] LL(1) is top-down (predictive); LALR(1) is bottom-up (shift-reduce) and handles a larger class of grammars.
[( )] LALR(1) requires the grammar to be right-recursive; LL(1) requires left-recursion.

---

Why is building an Abstract Syntax Tree (AST) in the parser generally better than evaluating expressions directly in parser actions?

[( )] ASTs are faster to build than direct evaluation.
[( )] Direct evaluation in parser actions is impossible in PLY.
[(X)] An AST can be traversed multiple times for different purposes (type checking, optimization, code generation), while direct evaluation discards structure immediately.
[( )] ASTs are required by the LALR(1) algorithm.

---

## Exercises

### Exercise 1: Add a `while` Loop

The mini language from Model 5 has `let` and `if-else` but no looping construct. Add a `while` loop with the syntax `while cond do body`.

1. Add the lexer rule (or reserved word entry) for `while` and `do`.
2. Add the parser rule `p_expr_while`.
3. Add a `While` dataclass with fields `cond` and `body`.
4. Add the `While` case to the `evaluate` function.

Hint: `while` is an expression in this language; it should return the value of the last iteration of `body`, or `0.0` if the condition is never true.

Test your solution with: `while x < 5 let x = x + 1 in x do x`
(This syntax will require you to think carefully about where the condition ends.)

### Exercise 2: Strings and Concatenation

Starting from Model 5, add:

1. A string literal token `STRING` matching `"[^"]*"` (strip the quotes in the action).
2. A `CONCAT` operator `++` that concatenates two strings.
3. A `STREQ` operator `~=` that tests string equality (returns `1.0` if equal, `0.0` otherwise).
4. A `StrLit` AST node and the corresponding evaluator case.

Test with: `let s = "hello" in s ++ " world"` and `"abc" ~= "abc"`.

### Exercise 3: A Type-Checking Pass

The parser from Model 4 builds an AST over `Num`, `Var`, `BinOp`, and `Assign` nodes. Write a function `type_check(node, env=None)` that walks the AST and raises a `TypeError` if:

- A `BinOp` with `+`, `-`, `*`, or `/` has a non-numeric operand (where "numeric" means the operand's inferred type is `float`).
- A `Var` is referenced but not in `env`.

The function should return the Python type (`float` or `str`) of the expression it checks, so that the parent rule can verify compatibility.

Demonstrate your type checker on:
- `x = 3 + 4 * 2` (should pass)
- An AST you manually construct where `+` is applied to a `StrLit` and a `Num` (should raise `TypeError`).

### Exercise 4: Collect All Errors

The error-recovery code in Model 6 already collects errors in `errors_found`. Extend the approach so that:

1. Each error entry in `errors_found` is a dictionary with keys `type` (`'lex'` or `'parse'`), `message` (string), and `position` (the character offset or token position from PLY).
2. After parsing, print a summary in the form:

   ```
   Found 2 error(s):
     [lex]   pos 12: Illegal character '@'
     [parse] pos 18: Syntax error at token 'SEMICOLON'
   ```

3. Test your solution on at least three input strings that contain a mix of lexer and parser errors.

---

## Reflection

PLY uses the same LALR(1) algorithm as Bison, but expressed entirely in Python using functions and docstrings instead of a separate specification language compiled by a dedicated tool. What does this tell you about the relationship between the algorithm and the implementation language? Consider: does the choice of Python vs. C vs. a custom DSL change what grammars you can express, or only how you express them? How does the interactive, browser-runnable nature of PLY change your ability to experiment with and understand the parsing algorithm compared to the Flex/Bison workflow?

---

## Further Reading

- PLY Documentation: https://www.dabeaz.com/ply/ply.html
- Flex Manual: https://westes.github.io/flex/manual/
- Bison Manual: https://www.gnu.org/software/bison/manual/
- This course's companion activity: Scanners and Parsers with Flex and Yacc (see `liascript-parsertable.md`)
- Compilers: Principles, Techniques, and Tools (Dragon Book), Chapter 4: Syntax Analysis
- Modern Compiler Implementation in ML/Java/C (Appel), Chapter 3: Parsing
