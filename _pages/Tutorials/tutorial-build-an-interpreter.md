---
layout: tutorial
permalink: /Tutorials/BuildAnInterpreter
title: "CS374: Build a Complete Interpreter in Python, Step by Step"

info:
  coursenum: CS374
  goals:
    - "Built a hand-written lexer that converts Mini source code into a typed token stream with line and column positions"
    - "Built a recursive-descent parser that converts the token stream into a typed AST with one class per node type"
    - "Implemented a tree-walking evaluator with a lexical environment chain that correctly handles nested `let` bindings"
    - "Implemented first-class functions and closures so that inner functions capture and carry their enclosing environments"
    - "Implemented recursive definitions (`letrec`), error reporting, and a working REPL and file-runner"

tags:
  - interpreter
  - assignment-companion

---
# Tutorial: Build a Complete Interpreter in Python, Step by Step

## Learning Goals

By the end of this tutorial, you will have:

- Built a hand-written lexer that converts Mini source code into a typed token stream with line and column positions
- Built a recursive-descent parser that converts the token stream into a typed AST with one class per node type
- Implemented a tree-walking evaluator with a lexical environment chain that correctly handles nested `let` bindings
- Implemented first-class functions and closures so that inner functions capture and carry their enclosing environments
- Implemented recursive definitions (`letrec`), error reporting, and a working REPL and file-runner

This tutorial walks you through every line of a complete interpreter for a small programming language called **Mini**.  Mini supports integers, booleans, arithmetic, comparisons, let-bindings, conditionals, first-class functions, and recursive definitions.  By the end you will have a working REPL and a file-runner, and you will understand how each piece connects to the theory covered in class.

**What you will build, in order:**
1.  A hand-written lexer (tokenizer)
2.  A recursive descent parser that produces an AST
3.  A tree-walking evaluator with proper lexical scoping
4.  First-class functions and closures
5.  Recursive definitions (`letrec`)
6.  Error reporting with line/column information
7.  A REPL and file-runner

**The language design:**

```
expr ::= NUMBER | BOOL
       | IDENT
       | expr op expr          (op: + - * / < > <= >= == !=)
       | "if" expr "then" expr "else" expr
       | "let" IDENT "=" expr "in" expr
       | "letrec" IDENT "=" expr "in" expr
       | "fun" IDENT "->" expr
       | expr expr              (function application, left-associative)
       | "(" expr ")"
```

---

# Stage 1: The Lexer

## 1.1 Tokens

A **token** is the smallest meaningful unit in our language.  Every token has a **type** and a **value**, plus source position for error reporting.

```python
# tokens.py
from dataclasses import dataclass
from typing import Any, Optional

@dataclass
class Token:
    type:   str
    value:  Any
    line:   int
    col:    int

    def __repr__(self):
        return f"Token({self.type}, {self.value!r}, {self.line}:{self.col})"

# Token types
TK_NUMBER  = "NUMBER"
TK_BOOL    = "BOOL"
TK_IDENT   = "IDENT"
TK_PLUS    = "+"
TK_MINUS   = "-"
TK_STAR    = "*"
TK_SLASH   = "/"
TK_LPAREN  = "("
TK_RPAREN  = ")"
TK_EQ      = "=="
TK_NEQ     = "!="
TK_LT      = "<"
TK_GT      = ">"
TK_LEQ     = "<="
TK_GEQ     = ">="
TK_ASSIGN  = "="
TK_ARROW   = "->"
TK_LET     = "let"
TK_LETREC  = "letrec"
TK_IN      = "in"
TK_IF      = "if"
TK_THEN    = "then"
TK_ELSE    = "else"
TK_FUN     = "fun"
TK_EOF     = "EOF"

KEYWORDS = {"let": TK_LET, "letrec": TK_LETREC, "in": TK_IN,
            "if": TK_IF, "then": TK_THEN, "else": TK_ELSE,
            "fun": TK_FUN, "true": TK_BOOL, "false": TK_BOOL}

print("Token types defined.")
```

---

## 1.2 The Lexer

```python
# lexer.py
class LexError(Exception):
    def __init__(self, msg, line, col):
        super().__init__(f"[lexer:{line}:{col}] {msg}")

class Lexer:
    def __init__(self, source: str):
        self.source = source
        self.pos    = 0
        self.line   = 1
        self.col    = 1

    def error(self, msg):
        raise LexError(msg, self.line, self.col)

    def peek(self) -> Optional[str]:
        return self.source[self.pos] if self.pos < len(self.source) else None

    def advance(self) -> str:
        ch = self.source[self.pos]
        self.pos += 1
        if ch == '\n':
            self.line += 1
            self.col   = 1
        else:
            self.col  += 1
        return ch

    def skip_whitespace_and_comments(self):
        while self.peek() in (' ', '\t', '\n', '\r', '#'):
            if self.peek() == '#':   # line comment
                while self.peek() and self.peek() != '\n':
                    self.advance()
            else:
                self.advance()

    def read_number(self) -> Token:
        start_line, start_col = self.line, self.col
        digits = []
        while self.peek() and self.peek().isdigit():
            digits.append(self.advance())
        return Token(TK_NUMBER, int("".join(digits)), start_line, start_col)

    def read_ident_or_keyword(self) -> Token:
        start_line, start_col = self.line, self.col
        chars = []
        while self.peek() and (self.peek().isalnum() or self.peek() == '_'):
            chars.append(self.advance())
        word = "".join(chars)
        if word in KEYWORDS:
            val = True if word == "true" else (False if word == "false" else word)
            return Token(KEYWORDS[word], val, start_line, start_col)
        return Token(TK_IDENT, word, start_line, start_col)

    def next_token(self) -> Token:
        self.skip_whitespace_and_comments()
        if self.peek() is None:
            return Token(TK_EOF, None, self.line, self.col)

        start_line, start_col = self.line, self.col
        ch = self.peek()

        if ch.isdigit():
            return self.read_number()
        if ch.isalpha() or ch == '_':
            return self.read_ident_or_keyword()

        self.advance()  # consume ch
        two = ch + (self.peek() or '')

        if two == '==': self.advance(); return Token(TK_EQ,    '==', start_line, start_col)
        if two == '!=': self.advance(); return Token(TK_NEQ,   '!=', start_line, start_col)
        if two == '<=': self.advance(); return Token(TK_LEQ,   '<=', start_line, start_col)
        if two == '>=': self.advance(); return Token(TK_GEQ,   '>=', start_line, start_col)
        if two == '->': self.advance(); return Token(TK_ARROW, '->', start_line, start_col)

        singles = {'+': TK_PLUS, '-': TK_MINUS, '*': TK_STAR, '/': TK_SLASH,
                   '(': TK_LPAREN, ')': TK_RPAREN, '=': TK_ASSIGN,
                   '<': TK_LT, '>': TK_GT}
        if ch in singles:
            return Token(singles[ch], ch, start_line, start_col)

        self.error(f"Unexpected character: {ch!r}")

    def tokenize(self):
        tokens = []
        while True:
            tok = self.next_token()
            tokens.append(tok)
            if tok.type == TK_EOF:
                break
        return tokens

# Quick test
lexer = Lexer("let x = 3 + 4 in x * 2")
for tok in lexer.tokenize():
    print(tok)
```

---

# Stage 2: The AST

## 2.1 AST Node Classes

```python
# ast_nodes.py
from dataclasses import dataclass, field
from typing import Optional, List

@dataclass
class Num:
    value: int
    line:  int = 0

@dataclass
class Bool:
    value: bool
    line:  int = 0

@dataclass
class Var:
    name: str
    line: int = 0

@dataclass
class BinOp:
    op:    str
    left:  object
    right: object
    line:  int = 0

@dataclass
class IfExpr:
    cond:  object
    then_: object
    else_: object
    line:  int = 0

@dataclass
class Let:
    name:  str
    value: object
    body:  object
    line:  int = 0

@dataclass
class LetRec:
    name:  str
    value: object
    body:  object
    line:  int = 0

@dataclass
class Fun:
    param: str
    body:  object
    line:  int = 0

@dataclass
class App:
    func: object
    arg:  object
    line: int = 0

print("AST node classes defined.")
```

---

# Stage 3: The Recursive Descent Parser

## 3.1 Parser Structure

```python
# parser.py
class ParseError(Exception):
    def __init__(self, msg, line, col):
        super().__init__(f"[parser:{line}:{col}] {msg}")

class Parser:
    """
    Grammar (with precedences encoded in the call hierarchy):
      expr   ::= let_expr | letrec_expr | fun_expr | if_expr | cmp
      cmp    ::= arith (("==" | "!=" | "<" | ">" | "<=" | ">=") arith)*
      arith  ::= term (("+"|"-") term)*
      term   ::= app (("*"|"/") app)*
      app    ::= atom atom*         (left-associative application)
      atom   ::= NUMBER | BOOL | IDENT | "(" expr ")"
    """

    def __init__(self, tokens):
        self.tokens = tokens
        self.pos    = 0

    def peek(self) -> Token:
        return self.tokens[self.pos]

    def advance(self) -> Token:
        tok = self.tokens[self.pos]
        if tok.type != TK_EOF:
            self.pos += 1
        return tok

    def expect(self, type_: str) -> Token:
        tok = self.advance()
        if tok.type != type_:
            raise ParseError(
                f"Expected {type_!r}, got {tok.type!r} ({tok.value!r})",
                tok.line, tok.col)
        return tok

    def match(self, *types) -> Optional[Token]:
        if self.peek().type in types:
            return self.advance()
        return None

    # ---- Entry point ----
    def parse(self):
        node = self.parse_expr()
        self.expect(TK_EOF)
        return node

    def parse_expr(self):
        tok = self.peek()
        if tok.type == TK_LET:
            return self.parse_let()
        if tok.type == TK_LETREC:
            return self.parse_letrec()
        if tok.type == TK_FUN:
            return self.parse_fun()
        if tok.type == TK_IF:
            return self.parse_if()
        return self.parse_cmp()

    def parse_let(self):
        tok  = self.expect(TK_LET)
        name = self.expect(TK_IDENT).value
        self.expect(TK_ASSIGN)
        val  = self.parse_expr()
        self.expect(TK_IN)
        body = self.parse_expr()
        return Let(name, val, body, tok.line)

    def parse_letrec(self):
        tok  = self.expect(TK_LETREC)
        name = self.expect(TK_IDENT).value
        self.expect(TK_ASSIGN)
        val  = self.parse_expr()
        self.expect(TK_IN)
        body = self.parse_expr()
        return LetRec(name, val, body, tok.line)

    def parse_fun(self):
        tok   = self.expect(TK_FUN)
        param = self.expect(TK_IDENT).value
        self.expect(TK_ARROW)
        body  = self.parse_expr()
        return Fun(param, body, tok.line)

    def parse_if(self):
        tok   = self.expect(TK_IF)
        cond  = self.parse_expr()
        self.expect(TK_THEN)
        then_ = self.parse_expr()
        self.expect(TK_ELSE)
        else_ = self.parse_expr()
        return IfExpr(cond, then_, else_, tok.line)

    CMP_OPS = {TK_EQ, TK_NEQ, TK_LT, TK_GT, TK_LEQ, TK_GEQ}

    def parse_cmp(self):
        left = self.parse_arith()
        while self.peek().type in self.CMP_OPS:
            op   = self.advance()
            right = self.parse_arith()
            left = BinOp(op.value, left, right, op.line)
        return left

    def parse_arith(self):
        left = self.parse_term()
        while self.peek().type in (TK_PLUS, TK_MINUS):
            op    = self.advance()
            right = self.parse_term()
            left  = BinOp(op.value, left, right, op.line)
        return left

    def parse_term(self):
        left = self.parse_app()
        while self.peek().type in (TK_STAR, TK_SLASH):
            op    = self.advance()
            right = self.parse_app()
            left  = BinOp(op.value, left, right, op.line)
        return left

    def parse_app(self):
        """Left-associative function application."""
        func = self.parse_atom()
        while self.peek().type in (TK_NUMBER, TK_BOOL, TK_IDENT, TK_LPAREN):
            arg  = self.parse_atom()
            func = App(func, arg, func.line)
        return func

    def parse_atom(self):
        tok = self.peek()
        if tok.type == TK_NUMBER:
            self.advance()
            return Num(tok.value, tok.line)
        if tok.type == TK_BOOL:
            self.advance()
            return Bool(tok.value, tok.line)
        if tok.type == TK_IDENT:
            self.advance()
            return Var(tok.value, tok.line)
        if tok.type == TK_LPAREN:
            self.advance()
            node = self.parse_expr()
            self.expect(TK_RPAREN)
            return node
        raise ParseError(
            f"Unexpected token: {tok.type!r} ({tok.value!r})",
            tok.line, tok.col)

def parse(source: str):
    tokens = Lexer(source).tokenize()
    return Parser(tokens).parse()

# Test the parser
ast = parse("let x = 3 in x + 1")
print(ast)
```

---

# Stage 4: The Evaluator

## 4.1 Values and Environments

```python
# evaluator.py
from dataclasses import dataclass

class RuntimeError_(Exception):
    def __init__(self, msg, line=0):
        prefix = f"[eval:{line}]" if line else "[eval]"
        super().__init__(f"{prefix} {msg}")

@dataclass
class Closure:
    """A function value: captures its defining environment."""
    param: str
    body:  object
    env:   dict

    def __repr__(self):
        return f"<closure:{self.param}>"

class Environment:
    """Linked-list environment for lexical scoping."""
    def __init__(self, parent=None):
        self.bindings = {}
        self.parent   = parent

    def lookup(self, name: str, line=0):
        if name in self.bindings:
            return self.bindings[name]
        if self.parent:
            return self.parent.lookup(name, line)
        raise RuntimeError_(f"Undefined variable: {name!r}", line)

    def bind(self, name: str, value):
        self.bindings[name] = value
        return self

    def extend(self, name: str, value):
        """Create a child environment with one new binding."""
        child = Environment(parent=self)
        child.bind(name, value)
        return child

print("Value types and Environment defined.")
```

---

## 4.2 The Evaluator

```python
class Evaluator:
    def evaluate(self, node, env: Environment):
        method = f"eval_{type(node).__name__}"
        handler = getattr(self, method, None)
        if handler is None:
            raise RuntimeError_(f"Unknown node type: {type(node).__name__}")
        return handler(node, env)

    def eval_Num(self, node, env):
        return node.value

    def eval_Bool(self, node, env):
        return node.value

    def eval_Var(self, node, env):
        return env.lookup(node.name, node.line)

    def eval_BinOp(self, node, env):
        left  = self.evaluate(node.left,  env)
        right = self.evaluate(node.right, env)
        ops = {
            '+':  lambda a, b: a + b,
            '-':  lambda a, b: a - b,
            '*':  lambda a, b: a * b,
            '/':  lambda a, b: a // b if b != 0 else (_ for _ in ()).throw(
                       RuntimeError_(f"Division by zero", node.line)),
            '==': lambda a, b: a == b,
            '!=': lambda a, b: a != b,
            '<':  lambda a, b: a <  b,
            '>':  lambda a, b: a >  b,
            '<=': lambda a, b: a <= b,
            '>=': lambda a, b: a >= b,
        }
        if node.op not in ops:
            raise RuntimeError_(f"Unknown operator: {node.op!r}", node.line)
        return ops[node.op](left, right)

    def eval_IfExpr(self, node, env):
        cond = self.evaluate(node.cond, env)
        if not isinstance(cond, bool):
            raise RuntimeError_(f"Condition must be boolean, got {type(cond).__name__}", node.line)
        return self.evaluate(node.then_ if cond else node.else_, env)

    def eval_Let(self, node, env):
        val     = self.evaluate(node.value, env)
        new_env = env.extend(node.name, val)
        return self.evaluate(node.body, new_env)

    def eval_Fun(self, node, env):
        return Closure(node.param, node.body, env)

    def eval_App(self, node, env):
        func = self.evaluate(node.func, env)
        arg  = self.evaluate(node.arg,  env)
        if not isinstance(func, Closure):
            raise RuntimeError_(f"Not a function: {func!r}", node.line)
        call_env = func.env.extend(func.param, arg)
        return self.evaluate(func.body, call_env)

    def eval_LetRec(self, node, env):
        """
        For letrec, the binding must be in scope while the value is evaluated.
        We use a mutable placeholder and patch it after evaluation.
        This handles the common case of recursive function definitions.
        """
        # Create the child env with a placeholder
        rec_env = Environment(parent=env)
        # Evaluate the value in the recursive environment
        val = self.evaluate(node.value, rec_env)
        # Now bind the name to the value (closures will capture rec_env)
        rec_env.bind(node.name, val)
        # Evaluate the body in the recursive environment
        return self.evaluate(node.body, rec_env)

print("Evaluator defined.")
```

---

## 4.3 Testing the Evaluator

```python
def run(source: str, env=None):
    """Parse and evaluate a Mini expression."""
    if env is None:
        env = Environment()
    tree = parse(source)
    return Evaluator().evaluate(tree, env)

# Basic arithmetic
print(run("3 + 4 * 2"))           # 11 (precedence: * before +)
print(run("(3 + 4) * 2"))         # 14
print(run("10 / 3"))              # 3 (integer division)

# Let binding
print(run("let x = 5 in x * x"))  # 25

# Conditionals
print(run("if 3 > 2 then 10 else 20"))   # 10
print(run("if 3 < 2 then 10 else 20"))   # 20

# Functions
print(run("(fun x -> x * x) 7"))  # 49

# Higher-order functions
print(run("let double = fun x -> x * 2 in let apply = fun f -> fun x -> f x in apply double 5"))  # 10

# Recursion with letrec
factorial_src = """
letrec fact = fun n -> if n <= 0 then 1 else n * fact (n - 1)
in fact 6
"""
print(run(factorial_src))   # 720

# Fibonacci
fib_src = """
letrec fib = fun n -> if n <= 1 then n else fib (n - 1) + fib (n - 2)
in fib 10
"""
print(run(fib_src))   # 55
```

---

# Stage 5: The REPL

## 5.1 Read-Eval-Print Loop

```python
def repl():
    """A simple REPL for the Mini language."""
    print("Mini Language Interpreter")
    print("Type an expression and press Enter. Type 'quit' to exit.")
    print()
    env = Environment()

    while True:
        try:
            line = input("mini> ").strip()
            if not line:
                continue
            if line == "quit":
                break
            result = run(line, env)
            print(f"=> {result!r}")
        except (LexError, ParseError, RuntimeError_) as e:
            print(f"Error: {e}")
        except KeyboardInterrupt:
            print("\nInterrupted.")
            break
        except Exception as e:
            import traceback
            print(f"[repl:unexpected] {e}")
            traceback.print_exc()

# Uncomment to run the REPL interactively:
# repl()

print("REPL defined. Call repl() to start it.")
```

---

## 5.2 File Runner

```python
import sys

def run_file(filename: str):
    """Read and evaluate a Mini source file."""
    try:
        with open(filename) as f:
            source = f.read()
    except FileNotFoundError:
        print(f"[runner] File not found: {filename!r}")
        sys.exit(1)

    try:
        result = run(source)
        print(result)
    except (LexError, ParseError, RuntimeError_) as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

# Usage: run_file("program.mini")
print("File runner defined.")
```

---

# Stage 6: What to Try Next

## 6.1 Extension Ideas

Now that your interpreter works, here are natural extensions to explore:

**Type checking (pre-evaluation pass):**

```python
class TypeChecker(Evaluator):
    """
    Instead of values, carry types. Catch type errors before running.
    Replace int values with the string "Int", bool values with "Bool", etc.
    """
    pass
```

**Multi-argument functions (syntactic sugar):**

```
fun x y z -> body  =>  fun x -> fun y -> fun z -> body
```

**Lists and pattern matching:**

```
let xs = [1, 2, 3] in
match xs with
| [] -> 0
| h :: t -> h + sum t
```

**Tail-call optimization:** The `eval_App` call above will blow Python's stack on deeply recursive functions.  Trampolining converts tail calls to iteration, research "trampoline in Python" for a clean implementation.

**Print / IO:** Add a `print` built-in function to the global environment.

---

## 6.2 Key Takeaways

| Concept | Where it appears |
|---|---|
| Lexical analysis | `Lexer.next_token()`; character-by-character |
| Token types | `TK_*` constants, the vocabulary |
| Recursive descent | Each grammar rule -> one `parse_*` method |
| Operator precedence | Call hierarchy: `parse_expr > parse_cmp > parse_arith > parse_term > parse_app > parse_atom` |
| Abstract Syntax Tree | `Num`, `BinOp`, `Let`, `Fun`, `App`, etc. |
| Tree-walking evaluation | `evaluate()`, dispatches by node type |
| Lexical scoping | `Environment` linked list, each `let` creates a child |
| Closures | `Closure` captures the defining `env` |
| Recursion | `LetRec`, value evaluated in an environment that includes the binding |

---

## 6.3 Suggested Exercises

1.  **Add `and` and `or`** as short-circuit operators.  Add them to the lexer, parser (between `parse_cmp` and `parse_arith`), and evaluator.

2.  **Add `let x = e` without `in`** for a top-level definition form.  The evaluator should update the global environment.

3.  **Add string literals** `"hello"`.  Update the lexer to scan quoted strings and the evaluator to handle them in `==` and `+` (string concatenation).

4.  **Add a built-in `print`** function by adding a `Builtin` value class and pre-populating the global environment with `print = Builtin(lambda x: (print(x), x)[1])`.

5.  **Implement a pretty-printer** that converts an AST back to Mini source code.  This is an `Unparser` visitor, the inverse of the parser.  Use it to verify your parser: `parse(unparse(parse(src)))` should equal `parse(src)` for well-formed programs.

---

## Further Reading

- Nystrom, Robert.  *Crafting Interpreters* (free online).  The Lox interpreter follows this exact arc; Chapters 4-11 correspond to the stages above.
- Krishnamurthi, Shriram.  *Programming Languages: Application and Interpretation* (PLAI) (free online).  Chapters 1-8 cover the same interpreter with formal semantics.
- Abelson and Sussman.  *Structure and Interpretation of Computer Programs* (SICP) (free online).  Chapter 4 builds a metacircular evaluator in Scheme, an interpreter written in the language it interprets.

---

# Advanced: A Metacircular Scheme Evaluator, Scheme in Python

This advanced section deepens the same lexer -> parser -> environment -> evaluator architecture you built for Mini above, and it backs Direction G of the Functional assignment (contributing to mal: Make-a-Lisp) for students heading that way.

An interpreter written in the very language it interprets sounds like a paradox, but it is actually one of the most clarifying ideas in computer science: it proves that the language's evaluation rules are self-consistent and complete.  Think of it like a dictionary that defines every word using other words in the same dictionary: the circularity is the point here, because it shows the system is closed.  Building this evaluator in Python forces every semantic choice to become explicit code, revealing the machinery that the Mini interpreter you just built already contains.

## Learning Goals

By the end of this section, you will be able to:

- Parse Scheme s-expressions into Python data structures and traverse them to implement `eval` and `apply`
- Implement lexical scoping using a linked chain of environment frames that correctly handles closures
- Build a trampoline-based tail-call optimizer that runs deeply recursive Scheme programs without stack overflow
- Explain the relationship between the metacircular evaluator and this tutorial's Mini-language interpreter, identifying where the two designs converge and diverge

> **Before You Begin:** This section assumes you can:
> - Write and trace through a recursive Python function that processes nested lists
> - Explain what a Python dictionary is and how you would use one to map variable names to values
> - Describe what a closure is: a function paired with the environment in which it was created
>
> If any of these feel shaky, review them first.

> **"To understand the evaluator is to understand computation."**, SICP

A **metacircular evaluator** is an interpreter for a language written in (or very close to) that language itself.  In SICP Chapter 4, Abelson and Sussman build a Scheme interpreter *in Scheme*, revealing that the evaluation rules almost write themselves, because the host language and the implemented language share the same underlying ideas.  Here, we build a Scheme interpreter in Python.  Python is close enough that the translation is direct; different enough that we must make every semantic choice explicit.

You have just built a Mini-language interpreter in this tutorial.  That experience carries over completely.  The arc of this section: **Scheme code as data (s-expressions)** -> **the environment model** -> **the evaluator dispatch loop** -> **the global environment** -> **tail-call optimization via trampoline**.

By the end you will have a working evaluator that can run recursive Scheme programs of arbitrary depth.

**A working norm worth keeping:** predict every code cell's output *before* running it.  If the result surprises you, explain why before moving to the next question.

---

## Part I: S-Expressions, Code as Data

### Model 1: S-Expressions

In most languages, source code is text and data is something else entirely.  Scheme collapses this distinction: a program is a list, and lists are data.  This means a Scheme program can construct and run another Scheme program using the same `car`, `cdr`, and `cons` operations it uses on ordinary lists.  Before you can build the evaluator, you need to be comfortable reading nested Python lists as Scheme programs; the translation table in this model is your Rosetta Stone.

> **Watch out!**  In our representation, Scheme symbols (like variable names `x`, `y`, operator names `+`) and Scheme strings (like `"hello"`) are both Python `str` values.  The evaluator distinguishes them by context: a string that starts with `"` is a literal; anything else is a symbol to look up.  This is a shortcut that would not work in a production system, but it simplifies the parser significantly.

Scheme's defining design choice: **program text and data share the same representation.**  Every Scheme expression is an *s-expression* (symbolic expression): either an **atom** (number, boolean, string, or symbol) or a **pair** `(head . tail)`, where tail is usually another pair, recursively, giving a list.  The surface syntax `(op arg1 arg2 ...)` is just a printed list.

This is not a curiosity; it is what makes Scheme's macros, `eval`, and `quote` work: a program can construct and execute another program using the same list operations it uses on ordinary data.

#### Mapping Scheme to Python

For our interpreter we represent s-expressions as nested Python lists of atoms.  The correspondence:

| Scheme source | Python representation |
|---------------|-----------------------|
| `(+ 1 2)` | `['+', 1, 2]` |
| `(define x 42)` | `['define', 'x', 42]` |
| `(lambda (x) (* x x))` | `['lambda', ['x'], ['*', 'x', 'x']]` |
| `(if #t 1 0)` | `['if', True, 1, 0]` |
| `(let ((x 5)) (+ x 1))` | `['let', [['x', 5]], ['+', 'x', 1]]` |
| `'foo` | `['quote', 'foo']` |

Atoms map to: Python `int`/`float`, `bool`, `str` (for Scheme strings), or Python `str` (for Scheme symbols; we distinguish symbol from string by context).

#### The Parser

The parser has two stages: a **tokenizer** that splits the input string into a flat list of token strings, then a **recursive descent** step that folds those tokens into nested Python lists.

```python
import re

def tokenize(s):
    """
    Split a Scheme source string into a list of token strings.
    Handles: parentheses, strings, #t/#f, numbers, symbols.
    """
    # Insert spaces around parens, then split; handle quoted strings carefully
    token_pattern = r'\"[^\"]*\"|\(|\)|[^\s()\"]+' 
    return re.findall(token_pattern, s)

def parse_atom(token):
    """Convert a single token string to its Python atom value."""
    if token == '#t':
        return True
    if token == '#f':
        return False
    if token.startswith('"') and token.endswith('"'):
        return token[1:-1]            # strip quotes; store as Python str
    try:
        return int(token)
    except ValueError:
        pass
    try:
        return float(token)
    except ValueError:
        pass
    return token                      # symbol: just keep the string

def parse_tokens(tokens):
    """
    Consume tokens (a list used as a mutable queue via pop(0)) and return
    the next complete s-expression as a nested Python list/atom.
    """
    if not tokens:
        raise SyntaxError("Unexpected EOF")
    token = tokens.pop(0)
    if token == '(':
        result = []
        while tokens[0] != ')':
            result.append(parse_tokens(tokens))
        tokens.pop(0)                 # consume ')'
        return result
    elif token == ')':
        raise SyntaxError("Unexpected ')'")
    elif token == "'":                # shorthand quote
        return ['quote', parse_tokens(tokens)]
    else:
        return parse_atom(token)

def parse_sexp(s):
    """Parse a Scheme source string and return its Python representation."""
    tokens = tokenize(s)
    return parse_tokens(tokens)

# --- Demo ---
examples = [
    "(+ 1 2)",
    "(define x 42)",
    "(lambda (x) (* x x))",
    "(if #t 1 0)",
    "(let ((x 5)) (+ x 1))",
]
for src in examples:
    print(f"{src!s:40s} => {parse_sexp(src)}")
```

---

#### Questions to Consider, Model 1

**Question 1.**  What Python type represents a Scheme pair/list in our encoding?  What Python type represents a Scheme symbol?  How does the evaluator distinguish a symbol `"x"` (which should be looked up) from a Scheme string `"hello"` (which is a literal value)?

**Question 2.**  What does `parse_sexp("(+ (* 2 3) 4)")` return?  Trace through `parse_tokens` step by step, listing the state of `tokens` at each recursive call.

**Question 3.**  Numbers and booleans are stored as Python `int`, `float`, and `bool` rather than as strings.  What advantage does this give the evaluator?  What would break if `(+ 1 2)` were stored as `['+', '1', '2']`?

---

## Part II: Environments

### Model 2: The Environment as a Linked Chain of Frames

Scoping rules determine which variable binding wins when the same name exists in multiple contexts.  Lexical scoping (the rule Scheme and Python both use) answers "which binding?" by looking at where the code was written, not where it was called.  The linked chain of frames implements this: each frame holds the bindings introduced at one scope level, and the `outer` pointer to the enclosing scope forms the lookup chain.  This structure is the heart of closures.

An **environment** in our interpreter is a dictionary that may have a pointer to an **outer** (enclosing) environment.  Variable lookup walks the chain until the name is found or the outermost frame is exhausted.

```python
class SchemeError(Exception):
    pass

class Env(dict):
    """
    A single environment frame.
    Inherits from dict so frame[var] = val works directly.
    outer: the enclosing environment, or None for the global frame.
    """
    def __init__(self, params=(), args=(), outer=None):
        super().__init__()
        self.outer = outer
        if len(params) != len(args):
            raise SchemeError(
                f"Arity mismatch: expected {len(params)} args, got {len(args)}"
            )
        self.update(zip(params, args))   # bind each param to its arg

    def find(self, var):
        """
        Return the innermost frame that contains var.
        Raises SchemeError if var is unbound anywhere in the chain.
        """
        if var in self:
            return self
        if self.outer is None:
            raise SchemeError(f"Unbound variable: {var!r}")
        return self.outer.find(var)

# --- Demo: manual environment construction ---
global_env = Env()
global_env['y'] = 10

# Simulate (lambda (x) (+ x y)) called with x=3
call_env = Env(params=['x'], args=[3], outer=global_env)

print("x in call_env:", call_env.find('x')['x'])   # 3
print("y via outer:  ", call_env.find('y')['y'])   # 10
```

The chain for `(define f (lambda (x) (+ x y)))` where `y = 10` in the global environment looks like this:

```
Global frame:  { y: 10, f: <Procedure> }
                        ^
                        | outer
Call frame:    { x: 3  }
```

When the body `(+ x y)` is evaluated in the call frame, `x` resolves immediately; `y` requires walking up one link to the global frame.

---

#### Questions to Consider, Model 2

**Question 4.**  What happens when `find` reaches the outermost environment (where `outer is None`) and the variable still has not been found?  Write the exact exception that would be raised for `(+ x undefined-var)`.

**Question 5.**  Lexical (static) scope vs. dynamic scope differs entirely in *which frame becomes the `outer`* of a new call frame.  In lexical scope, which environment is passed as `outer` when a closure is called?  In dynamic scope, which environment would be passed instead?

**Question 6.**  Trace the full environment chain for the following interaction:

```scheme
(define y 10)
(define f (lambda (x) (+ x y)))
(f 5)
```

Draw the frames that exist when `(+ x y)` is being evaluated.  Label every `outer` pointer.  Then answer: if `y` were rebound to `20` *after* `f` was defined, would `(f 5)` return 15 or 25?  Why?

---

## Part III: The Evaluator Core

### Model 3: `scheme_eval`, Dispatch on Form

The entire evaluator fits in one function because every Scheme expression falls into one of three categories: a self-evaluating atom (numbers, booleans), a symbol to look up, or a list.  Lists are further divided into special forms (keywords like `if`, `define`, `lambda` that have their own evaluation rules) and procedure calls.  This dispatch-on-shape pattern is the same pattern you used in the Mini evaluator above; seeing it made explicit here should feel familiar.

> **Watch out!**  In Scheme, only `#f` (the boolean false) is falsy.  Everything else (including `0`, the empty list, and the empty string) is truthy.  The line `branch = x[2] if test is not False else ...` implements this rule.  Students frequently miss this and write `if not test`, which would treat `0` as false and produce wrong results for numeric conditions.

The evaluator is a single function that **dispatches** on the type and shape of the expression.  Atoms evaluate to themselves or to their binding.  Lists beginning with a keyword are **special forms** handled directly.  Any other list is a **procedure call**.

```python
# Env and SchemeError are the same as in Model 2,
# repeated here so this cell runs standalone.

class SchemeError(Exception):
    pass

class Env(dict):
    """
    A single environment frame.
    outer: the enclosing environment, or None for the global frame.
    """
    def __init__(self, params=(), args=(), outer=None):
        super().__init__()
        self.outer = outer
        if len(params) != len(args):
            raise SchemeError(
                f"Arity mismatch: expected {len(params)} args, got {len(args)}"
            )
        self.update(zip(params, args))   # bind each param to its arg

    def find(self, var):
        """Return the innermost frame that contains var."""
        if var in self:
            return self
        if self.outer is None:
            raise SchemeError(f"Unbound variable: {var!r}")
        return self.outer.find(var)


class Procedure:
    """
    A first-class Scheme procedure (closure).
    params: list of parameter name strings
    body:   s-expression (the body, a single expression or begin-list)
    env:    the defining environment (captured at lambda creation)
    """
    def __init__(self, params, body, env):
        self.params = params
        self.body   = body
        self.env    = env           # lexical environment - the closure

    def __call__(self, args):
        """Create a new frame on the *defining* environment, then evaluate body."""
        call_env = Env(self.params, args, self.env)
        return scheme_eval(self.body, call_env)

    def __repr__(self):
        return f"#<procedure ({' '.join(self.params)})>"


def scheme_eval(x, env):
    """
    Evaluate s-expression x in environment env.
    Returns a Python value representing the Scheme result.
    """

    # --- Self-evaluating atoms ---
    if isinstance(x, (int, float, bool)):
        return x
    if isinstance(x, str) and x.startswith('"'):
        return x                          # Scheme string literal

    # --- Symbol lookup ---
    if isinstance(x, str):
        return env.find(x)[x]

    # --- Special forms and procedure calls (x is a list) ---
    if not isinstance(x, list) or len(x) == 0:
        raise SchemeError(f"Cannot evaluate: {x!r}")

    head = x[0]

    # (quote datum)
    if head == 'quote':
        return x[1]

    # (if test consequent [alternate])
    if head == 'if':
        test = scheme_eval(x[1], env)
        # In Scheme only #f is false; everything else (including 0) is truthy
        branch = x[2] if test is not False else (x[3] if len(x) > 3 else False)
        return scheme_eval(branch, env)

    # (define symbol value)  or  (define (name params...) body)
    if head == 'define':
        if isinstance(x[1], list):
            # Syntactic sugar: (define (f x y) body) => (define f (lambda (x y) body))
            name   = x[1][0]
            params = x[1][1:]
            body   = x[2]
            env[name] = Procedure(params, body, env)
        else:
            env[x[1]] = scheme_eval(x[2], env)
        return None

    # (set! symbol value)
    if head == 'set!':
        env.find(x[1])[x[1]] = scheme_eval(x[2], env)
        return None

    # (lambda (params...) body)
    if head == 'lambda':
        params = x[1]
        body   = x[2] if len(x) == 3 else ['begin'] + x[2:]
        return Procedure(params, body, env)

    # (begin expr1 expr2 ...)
    if head == 'begin':
        result = None
        for expr in x[1:]:
            result = scheme_eval(expr, env)
        return result

    # (let ((var val) ...) body)
    if head == 'let':
        bindings = x[1]          # list of [var, val] pairs
        body     = x[2]
        params   = [b[0] for b in bindings]
        args     = [scheme_eval(b[1], env) for b in bindings]
        # Desugar: ((lambda (params...) body) args...)
        proc = Procedure(params, body, env)
        return proc(args)

    # (and expr ...)
    if head == 'and':
        result = True
        for expr in x[1:]:
            result = scheme_eval(expr, env)
            if result is False:
                return False
        return result

    # (or expr ...)
    if head == 'or':
        for expr in x[1:]:
            result = scheme_eval(expr, env)
            if result is not False:
                return result
        return False

    # --- Procedure call: (proc arg1 arg2 ...) ---
    proc = scheme_eval(head, env)
    args = [scheme_eval(a, env) for a in x[1:]]
    if callable(proc):
        return proc(args)
    raise SchemeError(f"Not a procedure: {proc!r}")


# --- Minimal global environment for the demo ---
import operator, math

def make_global_env():
    env = Env()
    env.update({
        '+':  lambda args: args[0] + args[1],
        '-':  lambda args: args[0] - args[1],
        '*':  lambda args: args[0] * args[1],
        '/':  lambda args: args[0] / args[1],
        '<':  lambda args: args[0] < args[1],
        '>':  lambda args: args[0] > args[1],
        '<=': lambda args: args[0] <= args[1],
        '>=': lambda args: args[0] >= args[1],
        '=':  lambda args: args[0] == args[1],
        'not':       lambda args: args[0] is False,
        'display':   lambda args: print(args[0], end=''),
        'newline':   lambda args: print(),
    })
    return env

# --- Tokenizer / parser (abbreviated; same as Model 1) ---
import re

def tokenize(s):
    return re.findall(r'\"[^\"]*\"|\(|\)|[^\s()\"]+', s)

def parse_atom(t):
    if t == '#t': return True
    if t == '#f': return False
    if t.startswith('"'): return t
    try: return int(t)
    except ValueError: pass
    try: return float(t)
    except ValueError: pass
    return t

def parse_tokens(tokens):
    if not tokens: raise SyntaxError("EOF")
    t = tokens.pop(0)
    if t == '(':
        lst = []
        while tokens[0] != ')':
            lst.append(parse_tokens(tokens))
        tokens.pop(0)
        return lst
    elif t == "'":
        return ['quote', parse_tokens(tokens)]
    else:
        return parse_atom(t)

def parse_sexp(s):
    return parse_tokens(tokenize(s))

# --- Run some expressions ---
genv = make_global_env()

tests = [
    "(+ 2 3)",
    "(if #t 42 0)",
    "(if #f 42 99)",
    "(define x 10)",
    "(+ x 5)",
    "(define square (lambda (n) (* n n)))",
    "(square 7)",
    "(let ((a 3) (b 4)) (+ (* a a) (* b b)))",
    "(and #t #t #f)",
    "(or  #f #f 7)",
    "(begin (define y 100) (+ y 1))",
]

for src in tests:
    ast    = parse_sexp(src)
    result = scheme_eval(ast, genv)
    if result is not None:
        print(f"{src!s:50s} => {result}")
```

---

#### Questions to Consider, Model 3

**Question 7.**  Why does `define` store into `env` directly with `env[x[1]] = ...` while `set!` uses `env.find(x[1])[x[1]] = ...`?  What would happen if `set!` used `env[x[1]] = ...` instead?  Give a concrete example where the behavior would differ.

**Question 8.**  Show the complete desugaring of `(let ((x 5) (y 3)) (+ x y))` into a lambda application.  Write out both the s-expression that `scheme_eval` actually evaluates and the equivalent Python call tree that results.

**Question 9.**  Consider:

```scheme
(define fact
  (lambda (n)
    (if (<= n 1)
        1
        (* n (fact (- n 1))))))
(fact 5)
```

Does this work in our evaluator?  Trace through why `fact` is visible inside its own body even though it is being defined *right now*.  (Hint: look at how `define` stores the procedure into `env` *before* the body is ever called.)

---

## Part IV: The Global Environment

### Model 4: `make_global_env`, The Built-In World

Every language has a layer of operations that the interpreter cannot define in terms of itself: the bedrock primitives.  In Scheme these are things like `+`, `cons`, `car`, and `display`.  In our interpreter they are Python lambdas sitting in the global environment frame.  Everything else the user writes builds on top of this layer, which is why getting the primitive set right matters: it is the entire foundation.

The global environment pre-loads all the primitive operations.  In real Scheme these are implemented in a low-level language for speed; in our interpreter they are just Python lambdas.

```python
import operator, math

def make_global_env():
    """Return an Env pre-loaded with standard Scheme primitives."""
    env = Env()
    env.update({
        # --- Arithmetic ---
        '+':  lambda a: sum(a),
        '-':  lambda a: a[0] - a[1] if len(a) == 2 else -a[0],
        '*':  lambda a: a[0] * a[1],
        '/':  lambda a: a[0] / a[1],
        '%':  lambda a: a[0] % a[1],

        # --- Comparison ---
        '<':  lambda a: a[0] <  a[1],
        '>':  lambda a: a[0] >  a[1],
        '<=': lambda a: a[0] <= a[1],
        '>=': lambda a: a[0] >= a[1],
        '=':  lambda a: a[0] == a[1],

        # --- List operations ---
        # We represent Scheme pairs as Python 2-tuples (head, tail).
        # The empty list is None (representing Scheme's '()).
        'cons':   lambda a: (a[0], a[1]),
        'car':    lambda a: a[0][0],
        'cdr':    lambda a: a[0][1],
        'list':   lambda a: _make_list(a),
        'null?':  lambda a: a[0] is None,
        'pair?':  lambda a: isinstance(a[0], tuple),
        'length': lambda a: _length(a[0]),
        'append': lambda a: _append(a[0], a[1]),
        'map':    lambda a: _map(a[0], a[1]),

        # --- Boolean ---
        'not':      lambda a: a[0] is False,
        'boolean?': lambda a: isinstance(a[0], bool),

        # --- Type predicates ---
        'number?':    lambda a: isinstance(a[0], (int, float)) and not isinstance(a[0], bool),
        'symbol?':    lambda a: isinstance(a[0], str) and not a[0].startswith('"'),
        'string?':    lambda a: isinstance(a[0], str) and a[0].startswith('"'),
        'procedure?': lambda a: callable(a[0]),

        # --- I/O ---
        'display':  lambda a: (print(a[0], end=''), None)[1],
        'newline':  lambda a: (print(), None)[1],
    })
    return env

# --- Helpers for list operations ---
def _make_list(items):
    result = None
    for item in reversed(items):
        result = (item, result)
    return result

def _length(pair):
    count = 0
    while pair is not None:
        count += 1
        pair = pair[1]
    return count

def _append(p1, p2):
    if p1 is None:
        return p2
    return (p1[0], _append(p1[1], p2))

def _map(proc, lst):
    if lst is None:
        return None
    return (proc([lst[0]]), _map(proc, lst[1]))

def scheme_list_to_python(pair):
    """Convert our pair-based list to a Python list for display."""
    result = []
    while pair is not None:
        result.append(pair[0])
        pair = pair[1]
    return result

# --- Test the global environment ---
# (Re-define tokenizer, parser, Env, Procedure, scheme_eval here - abbreviated)
import re

class SchemeError(Exception): pass

class Env(dict):
    def __init__(self, params=(), args=(), outer=None):
        super().__init__()
        self.outer = outer
        self.update(zip(params, args))
    def find(self, var):
        if var in self: return self
        if self.outer is None: raise SchemeError(f"Unbound: {var!r}")
        return self.outer.find(var)

class Procedure:
    def __init__(self, params, body, env):
        self.params, self.body, self.env = params, body, env
    def __call__(self, args):
        return scheme_eval(self.body, Env(self.params, args, self.env))
    def __repr__(self): return f"#<procedure>"

def scheme_eval(x, env):
    if isinstance(x, (int, float, bool)): return x
    if isinstance(x, str) and x.startswith('"'): return x
    if isinstance(x, str): return env.find(x)[x]
    if not isinstance(x, list) or not x: raise SchemeError(f"Bad expr: {x!r}")
    head = x[0]
    if head == 'quote': return x[1]
    if head == 'if':
        test = scheme_eval(x[1], env)
        branch = x[2] if test is not False else (x[3] if len(x) > 3 else False)
        return scheme_eval(branch, env)
    if head == 'define':
        if isinstance(x[1], list):
            env[x[1][0]] = Procedure(x[1][1:], x[2], env)
        else:
            env[x[1]] = scheme_eval(x[2], env)
        return None
    if head == 'set!':
        env.find(x[1])[x[1]] = scheme_eval(x[2], env); return None
    if head == 'lambda':
        body = x[2] if len(x)==3 else ['begin']+x[2:]
        return Procedure(x[1], body, env)
    if head == 'begin':
        result = None
        for e in x[1:]: result = scheme_eval(e, env)
        return result
    if head == 'let':
        params = [b[0] for b in x[1]]; args = [scheme_eval(b[1],env) for b in x[1]]
        return Procedure(params, x[2], env)(args)
    if head == 'and':
        r = True
        for e in x[1:]:
            r = scheme_eval(e, env)
            if r is False: return False
        return r
    if head == 'or':
        for e in x[1:]:
            r = scheme_eval(e, env)
            if r is not False: return r
        return False
    proc = scheme_eval(head, env); args = [scheme_eval(a,env) for a in x[1:]]
    if callable(proc): return proc(args)
    raise SchemeError(f"Not a procedure: {proc!r}")

def tokenize(s): return re.findall(r'\"[^\"]*\"|\(|\)|[^\s()\"]+', s)
def parse_atom(t):
    if t=='#t': return True
    if t=='#f': return False
    if t.startswith('"'): return t
    try: return int(t)
    except: pass
    try: return float(t)
    except: pass
    return t
def parse_tokens(tokens):
    if not tokens: raise SyntaxError("EOF")
    t = tokens.pop(0)
    if t=='(':
        lst=[]
        while tokens[0]!=')': lst.append(parse_tokens(tokens))
        tokens.pop(0); return lst
    elif t=="'": return ['quote',parse_tokens(tokens)]
    else: return parse_atom(t)
def parse_sexp(s): return parse_tokens(tokenize(s))

genv = make_global_env()

tests = [
    ("(cons 1 2)",           None),
    ("(car (cons 1 2))",     None),
    ("(cdr (cons 1 2))",     None),
    ("(null? (list))",       None),
    ("(pair? (cons 1 2))",   None),
    ("(number? 42)",         None),
    ("(boolean? #t)",        None),
    ("(procedure? car)",     None),
]

for src, _ in tests:
    result = scheme_eval(parse_sexp(src), genv)
    print(f"{src!s:40s} => {result}")

# List demo
lst = scheme_eval(parse_sexp("(list 1 2 3 4)"), genv)
print("(list 1 2 3 4) as Python:", scheme_list_to_python(lst))
```

---

#### Questions to Consider, Model 4

**Question 10.**  Our `cons` returns a Python 2-tuple `(head, tail)`, not a Python list.  This means `(list 1 2 3)` produces `(1, (2, (3, None)))`.  Name two operations from Model 3 that would break if we used Python lists instead of tuples for pairs.  Why would the `null?` check fail?

---

## Part V: Tail Call Optimization

### Model 5: The Stack Overflow Problem and the Trampoline

A properly tail-recursive Scheme program should run in constant stack space; that is the Scheme specification's guarantee.  But our Python evaluator grows a Python stack frame for every recursive `scheme_eval` call, even when the Scheme call is in tail position.  The trampoline fixes this without changing Python's runtime: instead of recursing, tail calls return a "do this next" object (a `Thunk`), and a top-level loop bounces on those thunks until a real value appears.  It converts recursion into iteration by making "what to do next" explicit.

> **Watch out!**  The TCO evaluator uses a `while True` loop with `continue` for self-tail-calls.  This is only an optimization for calls where the current function calls itself.  Calls to a *different* procedure still need to update `x` and `env` and `continue` the loop, which is what the `Procedure call` branch does.  Missing the `continue` after updating `env` and `x` would send execution to the bottom of the loop body instead of restarting from the top.

Python has a default recursion limit of about 1000 frames.  A naive Scheme-in-Python evaluator will hit this limit when evaluating deeply recursive Scheme programs, even if the Scheme program is *tail recursive* and should need no stack at all.

Consider:

```scheme
(define count-down
  (lambda (n)
    (if (= n 0)
        'done
        (count-down (- n 1)))))
(count-down 10000)   ; Should work in Scheme; crashes in naive Python evaluator
```

The fix is a **trampoline**: instead of calling the recursive eval directly, return a *thunk* (a zero-argument lambda that will do the work) from tail positions.  The trampoline loop bounces on thunks until a real value emerges.

```python
# Trampoline-based TCO evaluator

class Thunk:
    """A deferred computation: a zero-argument callable."""
    def __init__(self, thunk_fn):
        self.thunk_fn = thunk_fn
    def __call__(self):
        return self.thunk_fn()

def trampoline(val):
    """Repeatedly call val() while val is a Thunk; return the final value."""
    while isinstance(val, Thunk):
        val = val()
    return val

# In scheme_eval_tco we return Thunk objects at tail positions.
# Here is the key part of the TCO evaluator - only the changed branches shown:

def scheme_eval_tco(x, env):
    """
    TCO variant: tail calls return Thunk instead of recursing.
    Call via trampoline(scheme_eval_tco(expr, env)).
    """
    while True:   # Use a loop for self-tail-calls to avoid Python stack growth
        if isinstance(x, (int, float, bool)):
            return x
        if isinstance(x, str) and x.startswith('"'):
            return x
        if isinstance(x, str):
            return env.find(x)[x]
        if not isinstance(x, list) or not x:
            raise SchemeError(f"Bad expr: {x!r}")

        head = x[0]

        if head == 'quote':
            return x[1]

        # (if ...) - only the taken branch is a tail position
        if head == 'if':
            test = trampoline(scheme_eval_tco(x[1], env))
            branch = x[2] if test is not False else (x[3] if len(x) > 3 else False)
            x = branch          # tail position: loop instead of recurse
            continue

        if head == 'define':
            if isinstance(x[1], list):
                env[x[1][0]] = ProcedureTCO(x[1][1:], x[2], env)
            else:
                env[x[1]] = trampoline(scheme_eval_tco(x[2], env))
            return None

        if head == 'set!':
            env.find(x[1])[x[1]] = trampoline(scheme_eval_tco(x[2], env))
            return None

        if head == 'lambda':
            body = x[2] if len(x)==3 else ['begin']+x[2:]
            return ProcedureTCO(x[1], body, env)

        # (begin ...) - last expression is in tail position
        if head == 'begin':
            for expr in x[1:-1]:
                trampoline(scheme_eval_tco(expr, env))
            x = x[-1]          # tail position: loop
            continue

        if head == 'let':
            params = [b[0] for b in x[1]]
            args   = [trampoline(scheme_eval_tco(b[1], env)) for b in x[1]]
            env = Env(params, args, env)
            x   = x[2]         # tail position: loop
            continue

        # Procedure call
        proc = trampoline(scheme_eval_tco(head, env))
        args = [trampoline(scheme_eval_tco(a, env)) for a in x[1:]]
        if isinstance(proc, ProcedureTCO):
            env = Env(proc.params, args, proc.env)
            x   = proc.body    # tail call: loop
            continue
        elif callable(proc):
            return proc(args)
        raise SchemeError(f"Not a procedure: {proc!r}")


class ProcedureTCO:
    def __init__(self, params, body, env):
        self.params, self.body, self.env = params, body, env
    def __repr__(self): return "#<procedure-tco>"


# --- We need supporting code from previous models here ---
import re

class SchemeError(Exception): pass

class Env(dict):
    def __init__(self, params=(), args=(), outer=None):
        super().__init__(); self.outer = outer; self.update(zip(params, args))
    def find(self, var):
        if var in self: return self
        if self.outer is None: raise SchemeError(f"Unbound: {var!r}")
        return self.outer.find(var)

def tokenize(s): return re.findall(r'\"[^\"]*\"|\(|\)|[^\s()\"]+', s)
def parse_atom(t):
    if t=='#t': return True
    if t=='#f': return False
    if t.startswith('"'): return t
    try: return int(t)
    except: pass
    try: return float(t)
    except: pass
    return t
def parse_tokens(tokens):
    if not tokens: raise SyntaxError("EOF")
    t = tokens.pop(0)
    if t=='(':
        lst=[]
        while tokens[0]!=')': lst.append(parse_tokens(tokens))
        tokens.pop(0); return lst
    elif t=="'": return ['quote', parse_tokens(tokens)]
    else: return parse_atom(t)
def parse_sexp(s): return parse_tokens(tokenize(s))

def make_global_env_tco():
    env = Env()
    env.update({
        '+':  lambda a: a[0]+a[1], '-': lambda a: a[0]-a[1],
        '*':  lambda a: a[0]*a[1], '/': lambda a: a[0]/a[1],
        '<=': lambda a: a[0]<=a[1], '>=': lambda a: a[0]>=a[1],
        '<':  lambda a: a[0]<a[1],  '>':  lambda a: a[0]>a[1],
        '=':  lambda a: a[0]==a[1],
        'display': lambda a: (print(a[0], end=''), None)[1],
        'newline': lambda a: (print(), None)[1],
    })
    return env

def run(src):
    genv = make_global_env_tco()
    exprs = []
    tokens = tokenize(src)
    while tokens:
        exprs.append(parse_tokens(tokens))
    result = None
    for expr in exprs:
        result = trampoline(scheme_eval_tco(expr, genv))
    return result

# --- Demo: deep recursion without stack overflow ---
prog = """
(define count-down
  (lambda (n)
    (if (= n 0)
        0
        (count-down (- n 1)))))
"""
print("count-down 100000 =>", run(prog + "(count-down 100000)"))

# Tail-recursive sum
prog2 = """
(define sum-iter
  (lambda (n acc)
    (if (= n 0)
        acc
        (sum-iter (- n 1) (+ acc n)))))
"""
print("sum 0..1000 =>", run(prog2 + "(sum-iter 1000 0)"))
```

---

#### Questions to Consider, Model 5

**Question 11.**  In the expression `(if test then-branch else-branch)`, which sub-expressions are in **tail position** and which are not?  Justify your answer by explaining what computation (if any) must happen *after* that sub-expression returns.

**Question 12.**  Python does not automatically optimize tail calls, even when the programmer writes a tail-recursive function.  Name two language design decisions in Python that make automatic tail-call optimization difficult or undesirable (consider stack traces, debugging, and Python's object model).

---

## Part VI: Multiple Choice Comprehension Check

Answer these to check your understanding before moving on.

**Question 1.**  What does evaluating `(lambda (x) x)` return in our interpreter?

- The number `0`
- A `Procedure` object (a closure)
- The symbol `x`
- A `SchemeError` because `x` is unbound

<details><summary>Answer</summary>

A `Procedure` object (a closure)

</details>

**Question 2.**  The expression `(let ((x 5)) (+ x 1))` desugars to which of the following?

- `(define x 5) (+ x 1)`
- `((lambda (x) (+ x 1)) 5)`
- `(set! x 5) (+ x 1)`
- `(begin (define x 5) (+ x 1))`

<details><summary>Answer</summary>

`((lambda (x) (+ x 1)) 5)`

</details>

**Question 3.**  In `(define (square n) (* n n))`, the list `(square n)` as the first argument to `define` is:

- A syntax error in standard Scheme
- A pair of a function name and its return type
- Syntactic sugar that expands to `(define square (lambda (n) (* n n)))`
- A call to the `square` function before it is defined

<details><summary>Answer</summary>

Syntactic sugar that expands to `(define square (lambda (n) (* n n)))`

</details>

**Question 4.**  Which component of the evaluator is directly responsible for implementing **lexical scope**?

- The tokenizer, which preserves symbol names
- The `scheme_eval` dispatch loop
- The `Env` chain: each `Procedure` captures and stores its *defining* environment, which becomes the `outer` of each call frame
- The `trampoline` function

<details><summary>Answer</summary>

The `Env` chain: each `Procedure` captures and stores its *defining* environment, which becomes the `outer` of each call frame

</details>

---

## Part VII: Exercises

Work through these exercises at your own pace.  Each builds directly on the evaluator code from Parts I-V.

---

### Exercise 1: Add `cond`

Scheme's `cond` is a multi-way conditional:

```scheme
(cond
  ((< x 0) 'negative)
  ((= x 0) 'zero)
  (else    'positive))
```

It evaluates each test in order; the first truthy test causes its associated expression to be evaluated and returned.  The `else` clause (if present) is always truthy.

**Task:** Add a `cond` branch to `scheme_eval` (or `scheme_eval_tco`).  The clause list is `x[1:]`; each clause is a two-element list `[test, expr]`.  The special symbol `'else'` should be treated as always true.

```python
# Starter: fill in the cond branch inside scheme_eval

# if head == 'cond':
#     for clause in x[1:]:
#         test_expr, result_expr = clause[0], clause[1]
#         if test_expr == 'else' or scheme_eval(test_expr, env) is not False:
#             return scheme_eval(result_expr, env)
#     return None   # no matching clause

# Test with:
# (cond ((< 3 0) 'neg) ((= 3 0) 'zero) (else 'pos))
# Expected: 'pos'
```

Write the complete working implementation and verify it handles the test case above, plus a case where the first clause matches and the others are never evaluated.

---

### Exercise 2: Add Scheme `do` Loops

Scheme's `do` loop is a structured iteration form:

```scheme
(do ((i 0 (+ i 1))     ; var init step
     (sum 0 (+ sum i)))
    ((= i 5) sum)       ; termination test, result
  (display i))          ; body (side effect only; run each iteration)
```

Each binding is `(var init step)`.  On each iteration: evaluate all `step` expressions (using the *current* bindings, not the updated ones), then rebind.  When `test` is true, evaluate `result` and return it.

**Task:** Implement `do` as a special form in `scheme_eval`.  You will need to:
1.  Extract bindings, the termination clause, and the body.
2.  Create an initial environment with `var = init` for each binding.
3.  Loop: check the test; if true, evaluate and return the result expression.  Otherwise evaluate the body, compute all new step values simultaneously, rebind, repeat.

---

### Exercise 3: Tail-Recursive `map` in Pure Scheme

The built-in `map` uses Python recursion.  Write a **pure Scheme** `map` that is tail-recursive using an accumulator, then reverses the result.

```scheme
(define my-reverse
  (lambda (lst acc)
    (if (null? lst)
        acc
        (my-reverse (cdr lst) (cons (car lst) acc)))))

(define my-map
  (lambda (f lst)
    ; YOUR CODE HERE
    ; Use my-reverse and an accumulator
    ))

(my-map (lambda (x) (* x x)) (list 1 2 3 4 5))
; Expected: (1 4 9 16 25) as a Scheme list
```

Verify that your implementation produces the correct result by running it in the TCO evaluator.  Then explain: is your `my-map` call to `my-map` in the recursive case actually in tail position?  Draw the call to convince yourself.

---

### Exercise 4: The Y Combinator

Without `define`, a lambda cannot refer to itself by name.  The **Y combinator** makes anonymous recursion possible.  In our evaluator (which uses applicative-order evaluation), the Z combinator (the strict variant) works:

```scheme
(define Z
  (lambda (f)
    ((lambda (x) (f (lambda (v) ((x x) v))))
     (lambda (x) (f (lambda (v) ((x x) v)))))))

(define fact
  (Z (lambda (self)
       (lambda (n)
         (if (<= n 1)
             1
             (* n (self (- n 1))))))))

(fact 6)
; Expected: 720
```

**Task:**
1.  Run the Z combinator in your evaluator.  Verify `(fact 6) = 720`.
2.  Explain in one paragraph why the *eager Y combinator* `(lambda (f) ((lambda (x) (f (x x))) (lambda (x) (f (x x)))))` diverges under applicative-order evaluation but the Z combinator above does not.
3.  *Challenge:* Define `fib` using `Z` without `define`.  Test `(fib 10)`.

---

## Part VIII: Reflection

Answer these questions in your course notebook after completing this section.

**Reflection 1.**  The word "metacircular" implies the evaluator is defined in terms of itself.  Our evaluator is written in Python, not Scheme; so in what sense is it still "metacircular"?  What would it take to port our evaluator from Python into the Scheme subset our evaluator understands, and what would that accomplish?

**Reflection 2.**  The course's project assignments ask you to build and extend a language interpreter.  Identify **three specific features** from this evaluator (the `Env` chain, `Procedure` as a closure, or TCO via trampoline) that map directly to something you will need in your own interpreter.  For each, write one sentence explaining the connection.

**Reflection 3.**  Our evaluator has no type system: `(+ 1 "hello")` raises a Python `TypeError` that leaks through the abstraction boundary.  Describe at minimum **two changes** you would make to add a static type system to this evaluator.  Consider: where would type annotations appear in the s-expression representation?  Where in `scheme_eval` would you insert a type-checking pass?  What new data structure would represent a type error vs. a value?

---

## Further Reading on Metacircular Evaluation

- **Runnable example archive**: [SchemeInterpreter.zip](https://www.billmongan.com/Ursinus-CS374-Fall2026/files/replit/SchemeInterpreter.zip): a complete reference implementation of this section's evaluator, worth exploring after you have worked through this section yourself.

- **SICP Chapter 4**: Abelson & Sussman, *Structure and Interpretation of Computer Programs*, 2nd ed.  The original metacircular evaluator.  MIT Press open access: [https://mitp-content-server.mit.edu/books/content/sectbyfn/books_pubs/6515/sicp.pdf](https://mitp-content-server.mit.edu/books/content/sectbyfn/books_pubs/6515/sicp.pdf)

- **"The Art of the Interpreter"**: Guy Steele & Gerald Sussman (1978).  The foundational paper on meta-circular evaluation, environments, and the relationship between interpreters and compilers.  [MIT AI Memo 452.](https://dspace.mit.edu/handle/1721.1/6094)

- **Norvig's `lis.py`**: Peter Norvig's "How to Write a (Lisp) Interpreter in Python."  Norvig's version is compact and elegant; ours extends it with TCO and a fuller special-form set.  Search for "Norvig lis.py" to find his blog post.

- **R7RS Scheme specification**: The current small Scheme standard.  Section 4 (Expressions) maps directly to our `scheme_eval` dispatch table.  Available at [https://small.r7rs.org/](https://small.r7rs.org/).

- **"Proper Tail Recursion and Space Efficiency"**: Will Clinger (PLDI 1998).  A careful treatment of what tail-call optimization guarantees and how to implement it correctly.

# From the Closures Activity: Closures in Your Interpreter

Twenty lines that give your interpreter first-class functions, plus why closures are what make recursion work.  Previously part of the Closures class session.

# Part II: Closures in Your Interpreter

Building an interpreter that supports closures requires translating the abstract idea ("a function carries its birth environment") into concrete data structures.  Think of it like building a passport system: when a function is created, you stamp its passport with the environment it was born in; when it is called later, you open a new room that is connected back to that stamped environment, not to wherever the function happens to be called from.  This section shows exactly how `Environment`, `Closure`, and `eval_call` work together to implement that passport stamp.

## 2.  Twenty Lines to First-Class Functions

Adding closures to Mini requires:
1.  A `FunDef` node and a `Call` node from the parser
2.  A `Closure` value created at **definition time**, capturing the *current* environment
3.  A call rule that builds the new environment parented on the **closure's captured environment**

```python
# Closure-based interpreter for Mini (simplified)

class Environment:
    def __init__(self, parent=None):
        self._vars = {}
        self.parent = parent

    def define(self, name, value):
        self._vars[name] = value

    def lookup(self, name):
        if name in self._vars:
            return self._vars[name]
        if self.parent is not None:
            return self.parent.lookup(name)
        raise NameError(f"Undefined: {name}")

    def assign(self, name, value):
        if name in self._vars:
            self._vars[name] = value
        elif self.parent is not None:
            self.parent.assign(name, value)
        else:
            raise NameError(f"Undefined: {name}")

class Closure:
    def __init__(self, params, body, env):
        self.params = params
        self.body   = body
        self.env    = env   # THE CAPTURED ENVIRONMENT - static scope lives here

class ReturnSignal(Exception):
    def __init__(self, value): self.value = value

def execute_fundef(name, params, body, env):
    """Create a closure and bind it to name in env."""
    closure = Closure(params, body, env)   # capture env HERE
    env.define(name, closure)

def eval_call(callee_val, arg_vals, evaluate_body, env):
    """Call a closure with evaluated argument values."""
    fn = callee_val
    if not isinstance(fn, Closure):
        raise TypeError(f"Not callable: {fn!r}")
    if len(arg_vals) != len(fn.params):
        raise TypeError(f"Expected {len(fn.params)} args, got {len(arg_vals)}")
    # *** THE ONE LINE THAT CHOOSES LEXICAL SCOPE ***
    local = Environment(parent=fn.env)   # parent = DEFINING env, not calling env!
    for name, val in zip(fn.params, arg_vals):
        local.define(name, val)
    try:
        evaluate_body(fn.body, local)
    except ReturnSignal as r:
        return r.value
    return None

# -----------------------------------------------------------------------
# STEP-BY-STEP TRACE: what happens when we define and call make_adder(5)
#
# Step 1 (DEFINITION - execute_fundef called):
#   current env = global_env  { }
#   closure = Closure(params=["n"], body=..., env=global_env)
#   global_env.define("make_adder", closure)
#   Result: global_env = { make_adder -> <Closure env=global_env> }
#
# Step 2 (CALL make_adder(5) - eval_call called):
#   fn       = global_env.lookup("make_adder")  -> the Closure from Step 1
#   arg_vals = [5]
#   local    = Environment(parent=fn.env)        # parent = global_env (lexical!)
#   local.define("n", 5)
#   Result: local = { n -> 5, parent -> global_env }
#   evaluate_body runs and creates the inner 'adder' closure:
#     inner_closure = Closure(params=["x"], body=..., env=local)  # captures local!
#     local.define("adder", inner_closure)
#     ReturnSignal(inner_closure) raised and caught
#   eval_call returns inner_closure
#
# Step 3 (CALL add5(3), where add5 = inner_closure from Step 2):
#   fn       = add5  (inner_closure, env=local where n=5)
#   arg_vals = [3]
#   call_env = Environment(parent=fn.env)   # parent = local (n=5), NOT global!
#   call_env.define("x", 3)
#   body evaluates x + n:
#     call_env.lookup("x") -> 3 (found in call_env)
#     call_env.lookup("n") -> not in call_env -> tries parent (local) -> 5
#   return 3 + 5 = 8  OK
#
# The key: Step 3 uses fn.env (local, where n=5) as parent, NOT the caller's env.
# That single parent= choice IS lexical scope.
# -----------------------------------------------------------------------

# Demo: make_adder in this closure system
global_env = Environment()

execute_fundef("make_adder", ["n"],
    # body: return lambda x: x + n  (simulated as a nested closure)
    [("fundef", "adder", ["x"], [("return", ("add", ("var", "x"), ("var", "n")))])],
    global_env)

# Verify the closure was created and captured the right env
ma = global_env.lookup("make_adder")
print(f"make_adder is a Closure: {isinstance(ma, Closure)}")
print(f"make_adder captured env has 'make_adder': {'make_adder' in ma.env._vars}")
```

**CTQs**

> **CTQ 3.1** Find the single line `local = Environment(parent=fn.env)` that decides static-versus-dynamic scope.  Write the one-token change that would make your language dynamically scoped.  (Hint: what if you used `env` instead of `fn.env`?)

> **CTQ 3.2** Arguments are evaluated in `env` (the caller's environment) but bound in `local` (parented on the *definer's* environment).  Construct a program where these two environments differ and where confusing them would change the output.

> **CTQ 3.3** `ReturnSignal` rides an exception out of nested blocks to the call boundary.  What would happen if `eval_call` caught *all* exceptions rather than only `ReturnSignal`?

---

For a function to call itself recursively, it must be able to look up its own name at the moment it runs.  This is not automatic; it requires the function's name to be bound in the environment *before* the function body executes.  Think of it like a business that must be registered with the government before it can issue contracts referencing itself.  This model shows the precise ordering: bind the name first, then use the closure, so that recursive lookup through the captured environment succeeds.

## Model 3: Closures Enable Recursion

```python
# Recursion requires the function to see itself in its own closure.
# execute_fundef binds the name BEFORE returning, so:

class Environment:
    def __init__(self, parent=None):
        self._vars = {}
        self.parent = parent
    def define(self, name, val):   self._vars[name] = val
    def lookup(self, name):
        if name in self._vars: return self._vars[name]
        if self.parent: return self.parent.lookup(name)
        raise NameError(name)

class Closure:
    def __init__(self, params, body_fn, env):
        self.params = params; self.body_fn = body_fn; self.env = env
    def __call__(self, *args):
        local = Environment(parent=self.env)
        for p, a in zip(self.params, args):
            local.define(p, a)
        return self.body_fn(local)

global_env = Environment()

# Define factorial using our closure mechanism
# fact(n) = if n <= 0 then 1 else n * fact(n-1)
def fact_body(env):
    n = env.lookup('n')
    if n <= 0: return 1
    return n * env.lookup('fact')(n - 1)   # looks up 'fact' via captured env!

fact_closure = Closure(['n'], fact_body, global_env)
global_env.define('fact', fact_closure)    # bind BEFORE any calls

print(f"fact(0) = {global_env.lookup('fact')(0)}")
print(f"fact(5) = {global_env.lookup('fact')(5)}")
print(f"fact(10) = {global_env.lookup('fact')(10)}")
```

> **CTQ 4.1** `execute_fundef` defines the name in the *current* environment before any calls.  When `fact_body` runs and looks up `'fact'`, it finds the closure in `global_env`.  Trace the environment chain: call frame -> captured `global_env` -> finds `fact`.  What would break if we didn't define the name until after creating the closure?

> **CTQ 4.2** `make_adder` creates a new closure for each call. `fact` is a single closure that calls itself.  Draw the environment chain for `fact(3)` calling `fact(2)` calling `fact(1)` calling `fact(0)`.  How deep does the chain grow?

---

Every closure question becomes answerable the moment you draw the boxes.  Here we take the classic **counter factory** (the "hello world" of stateful closures) and draw every environment box and arrow it creates, then verify the picture by peeking at Python's actual closure cells.

## Model 4: The Counter Factory, Drawn as Environment Boxes

**Worked example.**  Trace this program by hand before running anything:

```python
def make_counter():
    count = 0
    def increment():
        nonlocal count
        count += 1
        return count
    return increment

c1 = make_counter()   # call #1
c2 = make_counter()   # call #2
c1(); c1(); c2()
```

Step by step:

1.  **Call #1 to `make_counter`** creates environment box **E1** (parent: global) holding `count = 0`.
2.  The `def increment` inside that call creates **closure A** = ⟨code of `increment`, E1⟩, which is returned and bound to `c1`. `make_counter` has returned, but E1 survives: closure A still points to it (lifetime follows reachability).
3.  **Call #2** repeats the story with a *fresh* box **E2** and **closure B**, bound to `c2`.
4.  **`c1()`** creates a call frame whose parent is **E1** (the captured environment, not the caller's!). `nonlocal count` makes `count += 1` an *assignment into E1*: E1's count becomes 1.  The second `c1()` makes it 2.
5.  **`c2()`** assigns into **E2**: its count becomes 1.  E1 is untouched.

The final picture:

```
                +---------------------------+
                | global                    |
                |   make_counter -> <fn>    |
                |   c1 -> closure A         |
                |   c2 -> closure B         |
                +---------------------------+
                     ^                ^
             parent  |                |  parent
        +-----------------+    +-----------------+
        | E1 (call #1)    |    | E2 (call #2)    |
        |   count = 2     |    |   count = 1     |
        +-----------------+    +-----------------+
                 ^                      ^
        captured |             captured |
        closure A = <increment, E1>   closure B = <increment, E2>
             (bound to c1)                 (bound to c2)
```

And the same history as a table:

| Action | E1's `count` | E2's `count` | Return value |
|--------|--------------|--------------|--------------|
| `c1 = make_counter()` | 0 | - | closure A |
| `c2 = make_counter()` | 0 | 0 | closure B |
| `c1()` | 1 | 0 | 1 |
| `c1()` | 2 | 0 | 2 |
| `c2()` | 2 | 1 | 1 |

```python
def make_counter():
    count = 0
    def increment():
        nonlocal count
        count += 1
        return count
    return increment

c1 = make_counter()
c2 = make_counter()

print(c1(), c1())     # 1 2  - both assignments land in E1
print(c2())           # 1    - E2 is a separate box

# Verify the boxes are real: Python exposes them as closure "cells"
print("c1's captured count:", c1.__closure__[0].cell_contents)   # 2
print("c2's captured count:", c2.__closure__[0].cell_contents)   # 1
print("same box?", c1.__closure__[0] is c2.__closure__[0])       # False - E1 is not E2
```

After `c1 = make_counter()`, `c2 = make_counter()`, then `c1(); c1(); c2()`, the returned values are 1, 2, 1 because:

- Each call to `c1` creates a fresh environment with `count = 0`
- Each *call to `make_counter`* created its own environment box, so `c1` and `c2` increment different `count` bindings
- Python copies the value of `count` into each closure at definition time
- `c2` reset the shared counter

<details><summary>Answer</summary>

Each *call to `make_counter`* created its own environment box, so `c1` and `c2` increment different `count` bindings

</details>

**Critical Thinking Questions (CTQs)**

> **CTQ 5.1** The diagram shows two separate boxes, E1 and E2, each holding its own `count`.  What single fact about *when* environment boxes are created explains why `c1` and `c2` never interfere?

> **CTQ 5.2** `make_counter` returned long ago, yet the table shows E1's `count` still changing.  Using the phrase "lifetime follows reachability," name exactly what is keeping E1 alive, and predict what would have to happen for Python to reclaim it.

> **CTQ 5.3** `nonlocal count` makes `count += 1` an **assign** into E1 rather than a **define** of a new local.  Connect this to the environments module: without `nonlocal`, which operation would `count += 1` attempt, and why does it fail here?  (Delete the `nonlocal` line in the cell and read the error.)

> **CTQ 5.4** Redraw the boxes for the `make_counter` of Model 1, which returns *two* closures (`increment` and `reset`).  How many E-boxes does one call create, and which arrows in your drawing explain why the pair shares state?

---

