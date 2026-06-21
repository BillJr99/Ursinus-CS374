# Tutorial: Build a Complete Interpreter in Python — Step by Step

<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374-Fall2026/gh-pages/_pages/Tutorials/tutorial-build-an-interpreter.md

import: https://raw.githubusercontent.com/liascript/CodeRunner/master/README.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

# Tutorial: Build a Complete Interpreter in Python — Step by Step

This tutorial walks you through every line of a complete interpreter for a small programming language called **Mini**. Mini supports integers, booleans, arithmetic, comparisons, let-bindings, conditionals, first-class functions, and recursive definitions. By the end you will have a working REPL and a file-runner, and you will understand how each piece connects to the theory covered in class.

**What you will build, in order:**
1. A hand-written lexer (tokenizer)
2. A recursive descent parser that produces an AST
3. A tree-walking evaluator with proper lexical scoping
4. First-class functions and closures
5. Recursive definitions (`letrec`)
6. Error reporting with line/column information
7. A REPL and file-runner

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

A **token** is the smallest meaningful unit in our language. Every token has a **type** and a **value**, plus source position for error reporting.

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

**Tail-call optimization:** The `eval_App` call above will blow Python's stack on deeply recursive functions. Trampolining converts tail calls to iteration — research "trampoline in Python" for a clean implementation.

**Print / IO:** Add a `print` built-in function to the global environment.

---

## 6.2 Key Takeaways

| Concept | Where it appears |
|---|---|
| Lexical analysis | `Lexer.next_token()` — character-by-character |
| Token types | `TK_*` constants — the vocabulary |
| Recursive descent | Each grammar rule → one `parse_*` method |
| Operator precedence | Call hierarchy: `parse_expr > parse_cmp > parse_arith > parse_term > parse_app > parse_atom` |
| Abstract Syntax Tree | `Num`, `BinOp`, `Let`, `Fun`, `App`, etc. |
| Tree-walking evaluation | `evaluate()` — dispatches by node type |
| Lexical scoping | `Environment` linked list — each `let` creates a child |
| Closures | `Closure` captures the defining `env` |
| Recursion | `LetRec` — value evaluated in an environment that includes the binding |

---

## 6.3 Suggested Exercises

1. **Add `and` and `or`** as short-circuit operators. Add them to the lexer, parser (between `parse_cmp` and `parse_arith`), and evaluator.

2. **Add `let x = e` without `in`** for a top-level definition form. The evaluator should update the global environment.

3. **Add string literals** `"hello"`. Update the lexer to scan quoted strings and the evaluator to handle them in `==` and `+` (string concatenation).

4. **Add a built-in `print`** function by adding a `Builtin` value class and pre-populating the global environment with `print = Builtin(lambda x: (print(x), x)[1])`.

5. **Implement a pretty-printer** that converts an AST back to Mini source code. This is an `Unparser` visitor — the inverse of the parser. Use it to verify your parser: `parse(unparse(parse(src)))` should equal `parse(src)` for well-formed programs.

---

## Further Reading

- Nystrom, Robert. *Crafting Interpreters* (free online). The Lox interpreter follows this exact arc; Chapters 4–11 correspond to the stages above.
- Krishnamurthi, Shriram. *Programming Languages: Application and Interpretation* (PLAI) (free online). Chapters 1–8 cover the same interpreter with formal semantics.
- Abelson and Sussman. *Structure and Interpretation of Computer Programs* (SICP) (free online). Chapter 4 builds a metacircular evaluator in Scheme — an interpreter written in the language it interprets.
