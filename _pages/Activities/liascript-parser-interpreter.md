# Parsing and Interpreting: Putting It All Together
<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://github.com/BillJr99/Ursinus-CS374-Fall2026/blob/gh-pages/_pages/Activities/liascript-parser-interpreter.md

import: https://raw.githubusercontent.com/liascript/CodeRunner/master/README.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

# Parsing and Interpreting: Putting It All Together

## Learning Goals

By the end of this activity, you will be able to:

- Trace a source string through the complete tokenizer → parser → evaluator pipeline and explain the data structure produced at each stage
- Implement a recursive descent parser that constructs an abstract syntax tree from a token stream for arithmetic and boolean expressions
- Construct an environment-passing interpreter that evaluates an AST, correctly handling variable lookup, function application, and nested scopes
- Identify and fix common interpreter bugs: incorrect precedence, wrong scoping rules, missing base cases in recursive evaluation
- Extend the pipeline with a new language feature — new syntax, new AST node, and new evaluation rule — end-to-end

**CS374 Principles of Programming Languages — Weeks 11–14**

**References:** Compilers (Dragon Book) Ch. 4–5 | PLAI Ch. 15–17

Over the past weeks you have studied grammars, tokens, scanning, recursive descent parsing, and LL/LR table construction. This activity brings those pieces together into a complete pipeline: **source text → tokens → abstract syntax tree → evaluated result**. By the end you will have a working mini-interpreter built from first principles.

---

## Directions and Group Roles

This is a **POGIL** (Process-Oriented Guided Inquiry Learning) activity. Work in groups of 3–4 and assign the following roles before you begin. Rotate roles between models.

| Role | Responsibilities |
|------|-----------------|
| **Manager** | Keeps the group on task; tracks time; ensures everyone participates. |
| **Recorder** | Writes down group answers to Critical Thinking Questions (CTQs). |
| **Presenter** | Shares the group's answers with the class during discussion. |
| **Reflector** | Monitors group process; notes what is working and what is not. |

**How to use this activity:**

1. Read each Model's prose introduction carefully.
2. Run the code and observe the output.
3. Answer the CTQs in your group — discuss before writing.
4. Do not move to the next Model until the group agrees on answers.
5. Complete the Multiple Choice, Exercises, and Reflection at the end.

---

## Model 1: The Complete Pipeline — From Source to Result

A programming language implementation transforms source text through several **stages**. Each stage produces a data structure that the next stage consumes:

```
Source string  →  [Tokenizer]  →  Token list
Token list     →  [Parser]     →  Abstract Syntax Tree (AST)
AST            →  [Evaluator]  →  Result value
```

The code below implements the first stage — the **tokenizer** (also called a *lexer* or *scanner*). It uses Python's `re` module to match patterns left-to-right across the source string, producing a list of typed tokens.

```python
import re
from dataclasses import dataclass
from typing import Any, Optional

# === TOKENIZER ===
@dataclass
class Token:
    type: str
    value: str
    line: int

def tokenize(source: str) -> list:
    patterns = [
        ('NUMBER',  r'\d+(\.\d+)?'),
        ('STRING',  r'"[^"]*"'),
        ('PLUS',    r'\+'),
        ('MINUS',   r'-'),
        ('STAR',    r'\*'),
        ('SLASH',   r'/'),
        ('LPAREN',  r'\('),
        ('RPAREN',  r'\)'),
        ('EQ',      r'=='),
        ('ASSIGN',  r'='),
        ('NAME',    r'[a-zA-Z_]\w*'),
        ('SKIP',    r'[ \t]+'),
        ('NEWLINE', r'\n'),
    ]
    master = '|'.join(f'(?P<{name}>{pat})' for name, pat in patterns)
    tokens = []
    line = 1
    for m in re.finditer(master, source):
        kind = m.lastgroup
        if kind == 'NEWLINE':
            line += 1
        elif kind != 'SKIP':
            tokens.append(Token(kind, m.group(), line))
    tokens.append(Token('EOF', '', line))
    return tokens

# Test tokenizer
source = "x = 3 + 4 * 2"
tokens = tokenize(source)
print("Tokens:")
for t in tokens:
    print(f"  {t.type:10} {t.value!r}")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

**Critical Thinking Questions — Model 1**

1. What does the tokenizer's `SKIP` pattern do, and why is it necessary? What would happen if whitespace were not explicitly handled?

   [[___ your answer here ___]]

2. The `EQ` pattern (`==`) is listed **before** `ASSIGN` (`=`) in the patterns list. Why does this order matter? What would go wrong if they were reversed?

   [[___ your answer here ___]]

3. What does the `EOF` sentinel token signal to downstream stages, and why is it useful to represent end-of-input explicitly as a token rather than relying on an empty list?

   [[___ your answer here ___]]

4. How does the `line` counter assist with error messages? Trace through what happens when the tokenizer encounters a `\n` character.

   [[___ your answer here ___]]

---

## Model 2: Recursive Descent Parser

The tokenizer gives us a flat list of tokens. The **parser** imposes grammatical structure by grouping tokens into an **Abstract Syntax Tree (AST)**. A recursive descent parser encodes the grammar directly as a set of mutually recursive functions.

The grammar for our expression language is:

```
expr    → add
add     → mul ( ('+' | '-') mul )*
mul     → primary ( ('*' | '/') primary )*
primary → NUMBER | NAME | '(' expr ')'
```

Notice that `add` calls `mul`, and `mul` calls `primary`. This nesting is how the grammar enforces **operator precedence**: multiplication binds more tightly than addition because `mul` sits deeper in the call stack.

```python
from dataclasses import dataclass
from typing import Any, Optional

# AST nodes
@dataclass
class Num:
    value: float

@dataclass
class Str:
    value: str

@dataclass
class Var:
    name: str
    line: int

@dataclass
class BinOp:
    op: str
    left: Any
    right: Any

@dataclass
class Assign:
    name: str
    value: Any

# Re-use Token from above for demonstration
class Token:
    def __init__(self, type_, value, line=0):
        self.type = type_; self.value = value; self.line = line
    def __repr__(self): return f"Token({self.type!r}, {self.value!r})"

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def peek(self): return self.tokens[self.pos]
    def advance(self):
        t = self.tokens[self.pos]
        self.pos += 1
        return t
    def expect(self, type_):
        t = self.advance()
        if t.type != type_:
            raise SyntaxError(f"Expected {type_}, got {t.type} ({t.value!r}) at line {t.line}")
        return t

    def parse_expr(self):
        return self.parse_add()

    def parse_add(self):
        left = self.parse_mul()
        while self.peek().type in ('PLUS', 'MINUS'):
            op = self.advance().value
            right = self.parse_mul()
            left = BinOp(op, left, right)
        return left

    def parse_mul(self):
        left = self.parse_primary()
        while self.peek().type in ('STAR', 'SLASH'):
            op = self.advance().value
            right = self.parse_primary()
            left = BinOp(op, left, right)
        return left

    def parse_primary(self):
        t = self.peek()
        if t.type == 'NUMBER':
            self.advance()
            return Num(float(t.value))
        if t.type == 'NAME':
            self.advance()
            return Var(t.value, t.line)
        if t.type == 'LPAREN':
            self.advance()
            expr = self.parse_expr()
            self.expect('RPAREN')
            return expr
        raise SyntaxError(f"Unexpected token: {t.type} ({t.value!r}) at line {t.line}")

# Test the parser
import re
def tokenize_simple(source):
    patterns = [('NUMBER',r'\d+'),('PLUS',r'\+'),('MINUS',r'-'),('STAR',r'\*'),
                ('SLASH',r'/'),('LPAREN',r'\('),('RPAREN',r'\)'),
                ('NAME',r'[a-zA-Z_]\w*'),('SKIP',r'\s+')]
    master = '|'.join(f'(?P<{n}>{p})' for n,p in patterns)
    toks = [Token(m.lastgroup, m.group()) for m in re.finditer(master, source) if m.lastgroup != 'SKIP']
    toks.append(Token('EOF', ''))
    return toks

tokens = tokenize_simple("3 + 4 * (2 - 1)")
parser = Parser(tokens)
tree = parser.parse_expr()

def pprint(node, indent=0):
    prefix = "  " * indent
    if isinstance(node, Num): print(f"{prefix}Num({node.value})")
    elif isinstance(node, Var): print(f"{prefix}Var({node.name})")
    elif isinstance(node, BinOp):
        print(f"{prefix}BinOp({node.op!r})")
        pprint(node.left, indent+1)
        pprint(node.right, indent+1)

print("AST for '3 + 4 * (2 - 1)':")
pprint(tree)
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

**Critical Thinking Questions — Model 2**

1. Why does `parse_add` call `parse_mul` rather than `parse_primary`? Draw the call chain for parsing `3 + 4 * 2` and explain how the tree structure encodes precedence.

   [[___ your answer here ___]]

2. How does the grammar structure in the parser enforce that `*` binds more tightly than `+`? Would the precedence change if you swapped the bodies of `parse_add` and `parse_mul`?

   [[___ your answer here ___]]

3. What happens step-by-step when the parser sees `(` in `parse_primary`? Why does the parser call `parse_expr` recursively rather than `parse_primary`?

   [[___ your answer here ___]]

4. What specific error does `expect('RPAREN')` catch? Write an example input that would trigger this error and predict the error message.

   [[___ your answer here ___]]

---

## Model 3: Tree-Walking Evaluator

The parser produces an AST. The **evaluator** (also called an *interpreter*) walks that tree recursively, computing a result. This is the simplest evaluation strategy: **tree-walking interpretation**.

The evaluator needs an **environment** — a mapping from variable names to their current values. Environments can be chained: a child environment delegates to its parent when a name is not found locally. This chain implements **lexical scoping**.

```python
from dataclasses import dataclass, field
from typing import Any, Optional

@dataclass
class Num: value: float
@dataclass
class Var: name: str
@dataclass
class BinOp: op: str; left: Any; right: Any
@dataclass
class Assign: name: str; value_expr: Any
@dataclass
class If: cond: Any; then_branch: Any; else_branch: Any
@dataclass
class Print: expr: Any

@dataclass
class Env:
    bindings: dict = field(default_factory=dict)
    parent: Optional['Env'] = None

    def define(self, name, value): self.bindings[name] = value
    def lookup(self, name):
        if name in self.bindings: return self.bindings[name]
        if self.parent: return self.parent.lookup(name)
        raise NameError(f"Undefined variable: '{name}'")

def evaluate(node, env: Env) -> Any:
    if isinstance(node, Num):
        return node.value
    if isinstance(node, Var):
        return env.lookup(node.name)
    if isinstance(node, Assign):
        val = evaluate(node.value_expr, env)
        env.define(node.name, val)
        return val
    if isinstance(node, BinOp):
        l, r = evaluate(node.left, env), evaluate(node.right, env)
        match node.op:
            case '+': return l + r
            case '-': return l - r
            case '*': return l * r
            case '/':
                if r == 0: raise ZeroDivisionError("division by zero")
                return l / r
            case '==': return l == r
            case '<': return l < r
            case '>': return l > r
        raise ValueError(f"Unknown operator: {node.op}")
    if isinstance(node, If):
        return evaluate(node.then_branch, env) if evaluate(node.cond, env) \
               else evaluate(node.else_branch, env)
    if isinstance(node, Print):
        val = evaluate(node.expr, env)
        print(val)
        return val
    raise ValueError(f"Unknown node: {type(node).__name__}")

# Test: if 3 > 2 then x = 10 else x = 0; print(x)
env = Env()
program = [
    If(BinOp('>', Num(3), Num(2)),
       Assign("x", Num(10)),
       Assign("x", Num(0))),
    Print(Var("x")),
]
for stmt in program:
    evaluate(stmt, env)
print(f"x = {env.lookup('x')}")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

**Critical Thinking Questions — Model 3**

1. What does `evaluate` return for an `Assign` node? Why is it useful for assignment to return a value rather than `None`?

   [[___ your answer here ___]]

2. The `If` node only evaluates **one** branch — either `then_branch` or `else_branch`, but never both. Why is this the correct behavior? Give an example where evaluating both branches would produce incorrect or harmful results.

   [[___ your answer here ___]]

3. How would you add a `While` loop node to this interpreter? Sketch the dataclass definition and the case in `evaluate`. What could go wrong if the loop condition never becomes `False`?

   [[___ your answer here ___]]

4. What would happen if the `Env` class were removed entirely and the interpreter used a single global Python dictionary? Describe a program that would behave differently.

   [[___ your answer here ___]]

---

## Model 4: A Complete REPL

A **REPL** (Read-Eval-Print Loop) is an interactive shell that processes one expression or statement at a time. REPLs are invaluable for exploring a language interactively — Python's `>>>` prompt is one example.

The REPL maintains a persistent **environment** across inputs: a variable assigned in one line is still accessible in subsequent lines. Each iteration of the loop:

1. **Reads** a line of input,
2. **Evaluates** it (tokenize → parse → evaluate),
3. **Prints** the result,
4. **Loops** back to read the next line.

```python
import re
from dataclasses import dataclass, field
from typing import Any, Optional

# Abbreviated versions (assume tokenizer + parser + evaluator from above)
@dataclass
class Num: value: float
@dataclass
class Var: name: str
@dataclass
class BinOp: op: str; left: Any; right: Any
@dataclass
class Assign: name: str; value: Any
@dataclass
class Env:
    bindings: dict = field(default_factory=dict)
    def define(self, n, v): self.bindings[n] = v
    def lookup(self, n):
        if n in self.bindings: return self.bindings[n]
        raise NameError(f"Undefined: {n}")

def mini_eval(node, env):
    if isinstance(node, Num): return node.value
    if isinstance(node, Var): return env.lookup(node.name)
    if isinstance(node, Assign):
        v = mini_eval(node.value, env); env.define(node.name, v); return v
    if isinstance(node, BinOp):
        l, r = mini_eval(node.left, env), mini_eval(node.right, env)
        return {'+': l+r, '-': l-r, '*': l*r, '/': l/r}[node.op]
    raise ValueError(f"Unknown: {type(node)}")

def quick_parse(expr_str):
    """Parse: NAME=NUM, NAME, NUM, or NUM OP NUM."""
    expr_str = expr_str.strip()
    m = re.match(r'([a-z]+)\s*=\s*(.+)', expr_str)
    if m:
        return Assign(m.group(1), quick_parse(m.group(2)))
    m = re.match(r'(\d+(?:\.\d+)?)\s*([+\-*/])\s*(\d+(?:\.\d+)?)', expr_str)
    if m:
        ops = {'+': '+', '-': '-', '*': '*', '/': '/'}
        return BinOp(ops[m.group(2)], Num(float(m.group(1))), Num(float(m.group(3))))
    m = re.match(r'\d+(?:\.\d+)?$', expr_str)
    if m: return Num(float(m.group()))
    m = re.match(r'[a-z]+$', expr_str)
    if m: return Var(m.group())
    raise SyntaxError(f"Cannot parse: {expr_str!r}")

# Simulate a REPL session
env = Env()
session = [
    "x = 10",
    "y = 3",
    "x + y",
    "z = x * y",
    "z",
    "w = z + 1",
    "w",
]

print("Mini REPL session:")
for line in session:
    try:
        result = mini_eval(quick_parse(line), env)
        print(f">>> {line}")
        print(f"    {result}")
    except Exception as e:
        print(f">>> {line}")
        print(f"    Error: {e}")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

**Critical Thinking Questions — Model 4**

1. What does **REPL** stand for? Identify exactly which line(s) of the simulation above correspond to each of the four letters.

   [[___ your answer here ___]]

2. Why is a REPL especially useful when developing an interpreter? What kinds of bugs or design decisions become immediately visible in a REPL that are harder to see through batch testing?

   [[___ your answer here ___]]

3. What **state** persists between REPL lines in this simulation? Trace through the session and list the contents of `env.bindings` after each line executes.

   [[___ your answer here ___]]

4. How would you implement a special REPL command — say `env` — that prints all current variable bindings? Sketch the change to the REPL loop needed to support it.

   [[___ your answer here ___]]

---

## Model 5: Error Recovery and Diagnostics

A correct interpreter is not enough — users need **useful error messages**. The gold standard is to report the line number, the relevant source text, and a pointer to the exact location of the problem, just as modern compilers like Rust or Clang do.

To achieve this, AST nodes carry **source location** metadata (line number, column, original source text). When the evaluator detects an error, it constructs an exception that includes this location and formats it into a human-readable message.

```python
from dataclasses import dataclass
from typing import Any, Optional

@dataclass
class SourceLocation:
    line: int
    col: int = 0
    source_line: str = ""

    def format(self) -> str:
        pointer = " " * self.col + "^"
        return f"  Line {self.line}: {self.source_line}\n  {pointer}"

@dataclass
class InterpreterError(Exception):
    message: str
    location: Optional[SourceLocation] = None

    def __str__(self):
        if self.location:
            return f"Error at line {self.location.line}: {self.message}\n{self.location.format()}"
        return f"Error: {self.message}"

class UndefinedVariable(InterpreterError): pass
class TypeError_(InterpreterError): pass
class DivisionByZero(InterpreterError): pass

@dataclass
class Num:
    value: float
    loc: SourceLocation = None

@dataclass
class Var:
    name: str
    loc: SourceLocation = None

@dataclass
class BinOp:
    op: str
    left: Any
    right: Any
    loc: SourceLocation = None

def safe_eval(node, env: dict) -> Any:
    if isinstance(node, Num): return node.value
    if isinstance(node, Var):
        if node.name not in env:
            raise UndefinedVariable(f"'{node.name}' is not defined", node.loc)
        return env[node.name]
    if isinstance(node, BinOp):
        l = safe_eval(node.left, env)
        r = safe_eval(node.right, env)
        if node.op == '/' and r == 0:
            raise DivisionByZero("division by zero", node.loc)
        if node.op in ('+', '-', '*', '/') and not (isinstance(l, (int,float)) and isinstance(r, (int,float))):
            raise TypeError_(f"Cannot apply '{node.op}' to {type(l).__name__} and {type(r).__name__}", node.loc)
        return {'+': l+r, '-': l-r, '*': l*r, '/': l/r}[node.op]
    raise InterpreterError(f"Unknown node: {type(node).__name__}")

# Test error messages
source_lines = ["x = 10", "y = x / 0", "z = undefined_var"]
loc1 = SourceLocation(2, 4, source_lines[1])
loc2 = SourceLocation(3, 4, source_lines[2])

env = {"x": 10.0}

tests = [
    (BinOp('/', Var('x'), Num(0), loc1), "x / 0"),
    (Var('undefined_var', loc2), "undefined_var"),
    (BinOp('+', Num(1.0), Num(2.0)), "1 + 2"),
]

for node, desc in tests:
    try:
        result = safe_eval(node, env)
        print(f"OK  {desc} = {result}")
    except InterpreterError as e:
        print(f"ERR {desc}:\n{e}")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

**Critical Thinking Questions — Model 5**

1. Why should error messages include line numbers and the original source text? Describe a real-world debugging scenario where the difference between a vague error and a located error saves significant time.

   [[___ your answer here ___]]

2. What information does `SourceLocation` track? Where in a real tokenizer or parser would you construct `SourceLocation` objects and attach them to AST nodes?

   [[___ your answer here ___]]

3. How does attaching `loc` fields to AST nodes help error reporting in the evaluator, even though the evaluator runs long after tokenizing and parsing are complete?

   [[___ your answer here ___]]

4. What is the difference in user experience between `NameError: 'x'` (Python's default) and a detailed location message with a source pointer? When might the simpler message actually be preferable?

   [[___ your answer here ___]]

---

## Model 6: Adding Functions and Closures

Functions are the most powerful abstraction in programming languages. To implement them correctly, we must distinguish two things:

- A **Lambda** is a *syntactic* AST node: `lambda params: body`. It is part of the program text.
- A **Closure** is a *runtime value*: the function together with the **environment at the point of definition**. The captured environment is what makes closures powerful.

When a closure is called, we create a **new environment** that (a) extends the closure's captured environment and (b) binds the parameters to the call's arguments. This is **static (lexical) scoping**: the function sees the variables that were in scope where it was defined, not where it is called.

```python
from dataclasses import dataclass, field
from typing import Any, Optional

@dataclass
class Env:
    bindings: dict = field(default_factory=dict)
    parent: Optional['Env'] = None
    def define(self, n, v): self.bindings[n] = v
    def lookup(self, n):
        if n in self.bindings: return self.bindings[n]
        if self.parent: return self.parent.lookup(n)
        raise NameError(f"Undefined: '{n}'")

@dataclass
class Num: value: float
@dataclass
class Var: name: str
@dataclass
class BinOp: op: str; left: Any; right: Any
@dataclass
class Lambda: params: list; body: Any  # anonymous function
@dataclass
class Call: func: Any; args: list      # function call
@dataclass
class Closure:                          # runtime value: function + its env
    params: list
    body: Any
    env: Env

def interp(node, env: Env) -> Any:
    if isinstance(node, Num): return node.value
    if isinstance(node, Var): return env.lookup(node.name)
    if isinstance(node, BinOp):
        l, r = interp(node.left, env), interp(node.right, env)
        return {'+': l+r, '-': l-r, '*': l*r, '/': l/r}[node.op]
    if isinstance(node, Lambda):
        return Closure(node.params, node.body, env)  # captures current env
    if isinstance(node, Call):
        fn = interp(node.func, env)
        args = [interp(a, env) for a in node.args]
        if not isinstance(fn, Closure):
            raise TypeError(f"Not a function: {fn}")
        # Create new env extending the closure's captured env
        call_env = Env(parent=fn.env)
        for param, arg in zip(fn.params, args):
            call_env.define(param, arg)
        return interp(fn.body, call_env)
    raise ValueError(f"Unknown: {type(node).__name__}")

# Test: (lambda x, y: x + y)(3, 4)
add_fn = Lambda(["x", "y"], BinOp('+', Var("x"), Var("y")))
call = Call(add_fn, [Num(3), Num(4)])
env = Env()
print(f"(lambda x,y: x+y)(3,4) = {interp(call, env)}")

# Test closure: make_adder
# let make_adder = lambda n: lambda x: n + x
make_adder = Lambda(["n"], Lambda(["x"], BinOp('+', Var("n"), Var("x"))))
add5_expr = Call(make_adder, [Num(5)])
env.define("make_adder", interp(make_adder, env))
add5 = interp(add5_expr, env)
print(f"make_adder(5) is a Closure, params={add5.params}")
result = interp(Call(Lambda(["x"], BinOp('+', Var("n"), Var("x"))), [Num(3)]),
                Env(bindings={"n": 5}))
print(f"add5(3) = {result}")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

**Critical Thinking Questions — Model 6**

1. What is the difference between a `Lambda` (an AST node) and a `Closure` (a runtime value)? At what point in execution does a `Lambda` become a `Closure`?

   [[___ your answer here ___]]

2. Why does a `Closure` capture `env` at **definition time** rather than at **call time**? Give an example where using the call-time environment would produce a different — and wrong — result.

   [[___ your answer here ___]]

3. How does `Call` create a new environment that extends the closure's captured environment? Trace through the `make_adder(5)` call step-by-step, showing the chain of environments.

   [[___ your answer here ___]]

4. What is **static (lexical) scoping** and how does the `Closure`'s `env` field implement it? Contrast with **dynamic scoping** — what would change in the interpreter to implement dynamic scoping instead?

   [[___ your answer here ___]]

---

## Multiple Choice

**Question 1**

In a recursive descent parser, how is operator precedence encoded?

[[MC]]
- [( )] By checking operator precedence tables at each parse step
- [(X)] By the nesting of parse functions — higher-precedence operators are parsed deeper in the call stack
- [( )] By sorting tokens by precedence before parsing begins
- [( )] By the order of tokens in the token stream

**Question 2**

What does a REPL do after it evaluates an expression?

[[MC]]
- [( )] It discards all variable bindings and starts fresh
- [( )] It saves the expression to a file for batch processing
- [(X)] It prints the result and loops back to read the next input, keeping the environment
- [( )] It compiles the expression to machine code before printing

**Question 3**

When a `Closure` is created by evaluating a `Lambda` node, what environment does it capture?

[[MC]]
- [( )] The global environment at program startup
- [(X)] The environment that is current at the moment the `Lambda` is evaluated
- [( )] The environment that will be current when the closure is eventually called
- [( )] A fresh empty environment with no bindings

**Question 4**

In the tree-walking evaluator for `If`, why is it correct to evaluate only one branch?

[[MC]]
- [( )] The other branch is evaluated later when the condition changes
- [( )] Both branches are evaluated but only one result is returned
- [(X)] The unevaluated branch may have side effects that should not occur when its condition is false
- [( )] The parser already removed the false branch from the AST

---

## Exercises

**Exercise 1 — Let Expressions**

Add a `Let` expression to the interpreter. A `Let` node has three fields: `name` (a string), `value_expr` (an AST node), and `body_expr` (an AST node). Evaluating `Let(name, value_expr, body_expr)` should:

1. Evaluate `value_expr` in the current environment.
2. Create a **new** child environment that extends the current one.
3. Bind `name` to the result in the new environment.
4. Evaluate and return `body_expr` in the new environment.

The key difference from `Assign` is that `Let` creates a new scope — the binding is not visible outside `body_expr`.

```
Let("x", Num(5), BinOp('+', Var("x"), Num(3)))   # should return 8
```

Implement the `Let` dataclass and add a case to `evaluate` or `interp`. Test it with at least two examples: one where the `Let`-bound variable shadows an outer binding.

**Exercise 2 — Cond (if-elif-else Chain)**

Add a `Cond` node that represents a multi-way conditional:

```
Cond(clauses=[(cond1, result1), (cond2, result2), ...], else_result=...)
```

Evaluating `Cond` should scan through `clauses` in order. The first clause whose condition evaluates to a truthy value determines the result. If no clause matches, `else_result` is evaluated and returned.

Implement `Cond` and demonstrate it on an example that classifies a number as `"negative"`, `"zero"`, or `"positive"`.

**Exercise 3 — Recursive Functions with LetRec**

Ordinary `Lambda`/`Closure` cannot refer to themselves because the binding is not in scope when the function body is defined. Add a `LetRec(name, func_expr, body)` node that enables recursion:

1. Create a new child environment.
2. Evaluate `func_expr` to get a `Closure`.
3. Bind `name` to the closure **in the closure's own captured environment** (mutating it after creation).
4. Evaluate `body` in the new environment.

**Hint:** You may need to update `closure.env` after creating it. Test with a recursive factorial or Fibonacci function expressed as a `LetRec`.

**Exercise 4 — Pretty-Printer**

Implement a function `pretty(node) -> str` that converts an AST back into a human-readable infix expression string. Examples:

```
pretty(Num(3))                        # "3"
pretty(Var("x"))                      # "x"
pretty(BinOp('+', Num(3), Num(4)))    # "(3 + 4)"
pretty(BinOp('*', Num(2),
             BinOp('+', Num(1), Num(5))))  # "(2 * (1 + 5))"
pretty(Lambda(["x"], Var("x")))       # "(lambda x: x)"
pretty(Call(Var("f"), [Num(1), Num(2)]))   # "f(1, 2)"
```

The pretty-printer is useful for debugging (round-trip: parse then pretty-print) and for generating readable output from transformed ASTs.

---

## Reflection

You have now built a complete interpreter pipeline from scratch: a tokenizer that turns source text into tokens, a recursive descent parser that builds an AST, and a tree-walking evaluator that computes results. You also saw how to report errors with source locations and how to implement closures.

Respond to the following prompt in 3–4 sentences:

*Which stage of the pipeline was the most surprising to you, and why? What would you add — beyond lexical scoping, arithmetic, and conditionals — to turn this toy interpreter into a practical programming language?*

[[___ your reflection here ___]]

---

## Further Reading

- **Compilers: Principles, Techniques, and Tools** (Aho, Lam, Sethi, Ullman) — Chapter 4: Syntax Analysis; Chapter 5: Syntax-Directed Translation
- **Programming Languages: Application and Interpretation** (Krishnamurthi) — Chapter 15: Interpreting Variables; Chapter 16: Functions; Chapter 17: Closures and Higher-Order Functions
- **Crafting Interpreters** (Nystrom) — Free online at https://craftinginterpreters.com — a complete, annotated implementation of a full language in Java and C
- **Let's Build A Simple Interpreter** (Ruslan Spivak) — Blog series building a Pascal interpreter in Python, excellent complement to this activity
- **Structure and Interpretation of Computer Programs** (Abelson & Sussman) — Chapter 4: Metalinguistic Abstraction — the classic treatment of building evaluators in Scheme
