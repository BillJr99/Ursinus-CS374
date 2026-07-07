<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://github.com/BillJr99/Ursinus-CS374-Fall2026/blob/gh-pages/_pages/Activities/liascript-course-arc.md

import: https://raw.githubusercontent.com/liascript/CodeRunner/master/README.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

# The Arc of This Course: From Symbols to Languages

Think of building a programming language the way you would build a house: first you need blueprints (formal specifications — grammars, type rules, reduction rules), then the right materials (language features — lambdas, closures, type environments), and finally the tools to put it all together (implementation — scanners, parsers, interpreters). You cannot move in before the foundation is poured, and you cannot pour the foundation before you understand what you are building. This course follows that same sequence — each unit is load-bearing for the one that follows, and by the end you will have a finished, habitable language of your own design.

## Learning Goals

By the end of this activity, you will be able to:

- Trace the arc from lambda calculus through grammars, parsing, type systems, and interpreter construction, and explain how each stage builds on the previous
- Encode Church booleans, Church numerals, and basic arithmetic in pure lambda calculus, demonstrating that computation requires no primitives beyond functions
- Identify the three phases of a language implementation pipeline (lexing, parsing, evaluation) and describe the data structure each phase produces
- Explain why the theoretical machinery of this course (grammar rules, type judgments, reduction rules) and the engineering artifacts (parsers, type checkers, interpreters) are the same ideas at different levels of abstraction
- Formulate at least one substantive question about a topic previewed today that you do not yet understand

By December, you will have built a working programming language — a language you designed, with syntax you chose, with semantics you defined, that runs real programs. Today, on the first day, we will preview every major idea you will need to get there, condensed into 90 minutes of exploration. You will not understand everything today — that is the point. These are the questions this course answers.

The course begins with beauty: lambda calculus, the mathematical theory of computation published by Alonzo Church in 1936 — before computers existed — showing that all of computation can be built from a single idea (functions) and three rules (variables, abstraction, application). From there it moves through theory: grammars that define the shape of legal programs, parsing algorithms (LL, LR, and the tools Flex and Bison) that turn source text into structured data, and type systems that reason about program correctness without running a single line. The course ends with engineering: building a real interpreter, transpiler, or compiler for a language you have designed yourself. The magic is that the theory and the engineering are the same thing at different levels of abstraction — the grammar rules you write in Week 7 become the parser functions you write in Week 10, which become the type-checker you extend in Week 12, which becomes the interpreter you complete in Week 15.

> **Before You Begin:** This activity assumes you can:
> - Write and call basic Python functions, including functions that take other functions as arguments (higher-order functions)
> - Read recursive code — a function that calls itself — and trace what it returns for a small input
> - Describe, in plain English, the difference between syntax (what a program looks like) and semantics (what a program means)
>
> If any of these feel shaky, review them first.

---

## Directions and Group Roles

Work in your POGIL team with rotated roles (**Manager**, **Recorder**, **Presenter**, **Reflector**). Read each model carefully before attempting the Critical Thinking Questions. The goal today is not to understand everything — it is to ask good questions about what you do not yet understand.

---

# Part I: The Foundation

Before any real structure can be built, someone has to prove the ground can support it. Lambda calculus is that proof: a mathematician showed in 1936, before electronic computers existed, that a single idea — the function — is sufficient to express every computation. Everything else in this course (types, parsers, interpreters) rests on that foundation.

## Model 1: Everything Starts Here — Lambda Calculus in 10 Lines

Lambda calculus is the theory of computation from 1936. It has **three rules**: a variable is an expression; `lambda x. E` is a function; and `E1 E2` is applying `E1` to `E2`. That is the entire language. No numbers. No booleans. No loops. No `if`. Yet it is computationally universal — anything a modern computer can compute, lambda calculus can compute. The code below shows this: we build booleans, natural numbers, arithmetic, and even recursion entirely from `lambda`.

```python  liascript
# Lambda calculus: the theory of computation from 1936.
# THREE rules: variables, functions, application.
# ZERO primitives: no numbers, no booleans, no loops. Just functions.

# Yet here are Church booleans — built from nothing:
TRUE  = lambda x: lambda y: x   # select first
FALSE = lambda x: lambda y: y   # select second
IF    = lambda b: lambda t: lambda f: b(t)(f)

print("Church booleans:")
print(f"  TRUE  selects first:  {IF(TRUE)('yes')('no')}")
print(f"  FALSE selects second: {IF(FALSE)('yes')('no')}")

# Church numerals — natural numbers as functions:
ZERO  = lambda f: lambda x: x        # apply f 0 times
ONE   = lambda f: lambda x: f(x)     # apply f 1 time
TWO   = lambda f: lambda x: f(f(x))  # apply f 2 times
SUCC  = lambda n: lambda f: lambda x: f(n(f)(x))  # add one more application
ADD   = lambda m: lambda n: lambda f: lambda x: m(f)(n(f)(x))

to_int = lambda n: n(lambda x: x+1)(0)  # decode: apply successor to 0, n times

THREE = SUCC(TWO)
FIVE  = ADD(TWO)(THREE)

print(f"\nChurch numerals:")
print(f"  to_int(ZERO)  = {to_int(ZERO)}")
print(f"  to_int(THREE) = {to_int(THREE)}")
print(f"  to_int(FIVE)  = {to_int(FIVE)}")
print(f"  2 + 3 = {to_int(ADD(TWO)(THREE))}")

# Y combinator — recursion from scratch:
Y = lambda f: (lambda x: f(lambda v: x(x)(v)))(lambda x: f(lambda v: x(x)(v)))
factorial_logic = lambda self: lambda n: 1 if n <= 0 else n * self(n-1)
factorial = Y(factorial_logic)
print(f"\nY combinator factorial(5) = {factorial(5)}")

print("\n>>> This is where the course begins.")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

**Critical Thinking Questions (CTQs)**

> **CTQ 1** `TRUE = lambda x: lambda y: x` takes two arguments and returns the first. `IF = lambda b: lambda t: lambda f: b(t)(f)`. Verify by hand: what does `IF(TRUE)('yes')('no')` compute? Write each substitution step.

> **CTQ 2** `ONE = lambda f: lambda x: f(x)`. It applies `f` exactly once to `x`. Verify `to_int(ONE) == 1` by tracing: `to_int(ONE) = ONE(lambda x: x+1)(0) = (lambda x: x+1)(0) = 1`. Now trace `to_int(TWO)` the same way.

> **CTQ 3** Everything here uses only `lambda`. There are no numbers, strings, if-statements, or loops built into Python's lambda syntax. What does this tell you about the power of lambda abstraction?

> **Watch out!** Python's `lambda` keyword is just syntax sugar for defining a function — it is not the same thing as lambda calculus. In Model 1, we are using Python `lambda` as a convenient notation to *simulate* lambda calculus, but the real lambda calculus has no numbers, no `print`, and no Python runtime underneath it. When you see `TRUE = lambda x: lambda y: x`, mentally replace "Python lambda" with "mathematical function abstraction" — the Python is just a vehicle for the idea.

> **CTQ 4** This preview was 30 lines. By Week 3 of this course, you will understand every line. Write one question about something here you do not yet understand. Keep it — it is a learning goal.

---

# Part II: The Shape of Programs

A blueprint is useless if nobody can read it — it has to follow a standard notation everyone agrees on. Grammars play the same role for programming languages: they are the precise, written-down rules for what a legal program looks like, the same way a blueprint specifies exactly where every wall and door must go. Once you have a grammar written down, a parser can read programs the way a contractor reads blueprints — mechanically and unambiguously.

## Model 2: Grammars — The Shape of Language

A grammar defines what strings are **legal programs**. It is a set of recursive rules — a formal description of syntax. The grammar below defines arithmetic expressions, and the parser is a direct translation of the grammar into code: each grammar rule becomes a function. This connection between grammars and parsers is the core insight of Weeks 10–14.

```python  liascript
import re

# A grammar defines what strings are legal programs.
# Here is a grammar for simple arithmetic:
#
#   expr   -> term (('+' | '-') term)*
#   term   -> factor (('*' | '/') factor)*
#   factor -> NUMBER | '(' expr ')'
#   NUMBER -> [0-9]+
#
# A "recursive descent parser" directly translates this grammar to code.

class Parser:
    def __init__(self, text):
        self.tokens = re.findall(r'\d+|[+\-*/()]|\s+', text)
        self.tokens = [t for t in self.tokens if t.strip()]
        self.pos = 0

    def peek(self):
        return self.tokens[self.pos] if self.pos < len(self.tokens) else None

    def consume(self):
        t = self.tokens[self.pos]; self.pos += 1; return t

    def parse_expr(self):
        left = self.parse_term()
        while self.peek() in ('+', '-'):
            op = self.consume()
            right = self.parse_term()
            left = (op, left, right)
        return left

    def parse_term(self):
        left = self.parse_factor()
        while self.peek() in ('*', '/'):
            op = self.consume()
            right = self.parse_factor()
            left = (op, left, right)
        return left

    def parse_factor(self):
        if self.peek() == '(':
            self.consume()
            e = self.parse_expr()
            self.consume()  # ')'
            return e
        return float(self.consume())

def evaluate(ast):
    if isinstance(ast, float): return ast
    op, l, r = ast
    l, r = evaluate(l), evaluate(r)
    return {'+': l+r, '-': l-r, '*': l*r, '/': l/r}[op]

tests = ["3 + 4 * 2", "(3 + 4) * 2", "10 / 2 + 3 * 4 - 1"]
for t in tests:
    p = Parser(t)
    ast = p.parse_expr()
    result = evaluate(ast)
    print(f"  {t:25} = {result}")

# Show the AST structure:
p = Parser("3 + 4 * 2")
ast = p.parse_expr()
print(f"\nAST for '3 + 4 * 2': {ast}")
print("Notice: ('+', 3.0, ('*', 4.0, 2.0)) -- multiplication binds tighter!")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

**Critical Thinking Questions (CTQs)**

> **CTQ 5** The grammar has `term → factor (('*'|'/') factor)*` nested inside `expr → term (('+'|'-') term)*`. How does this nesting enforce that `*` has higher precedence than `+`?

> **CTQ 6** The `parse_expr` method calls `parse_term`, which calls `parse_factor`. This is "recursive descent." What happens when `parse_factor` sees `(`? Trace through the parsing of `(3 + 4) * 2` step by step.

> **CTQ 7** The AST for `3 + 4 * 2` is `('+', 3.0, ('*', 4.0, 2.0))` — addition is the ROOT, multiplication is a subtree. Draw this tree. Why does the root being `+` correctly represent that `+` is evaluated LAST?

> **Watch out!** Students often say "the root of the AST is evaluated first," but that is backwards. The root is the *last* thing evaluated — it depends on its children being evaluated first, just as a `+` node cannot add until both its left and right subtrees have been computed. Think of an AST as a recipe: the root is the final dish, and evaluation works from the leaves (ingredients) upward to the root (the finished result).

> **CTQ 8** This parser is about 30 lines. By Week 11, you will write a full parser that handles an entire programming language. What features would you need to add to handle variables, function definitions, and loops?

---

# Part III: The Contracts of Programs

A building inspector reviews the blueprints before a single beam is cut — they are looking for violations of the building code, not for whether the house will be pretty. A type checker does the same thing for programs: it reads the structure of your code and flags certain classes of errors before the program ever runs. Just as an inspector cannot catch every future problem (they cannot tell you if the paint will fade), a type system has limits — but the errors it does catch are guaranteed, structural, and caught early.

## Model 3: Types — The Contracts of Programming

A type system prevents entire classes of errors by reasoning about programs **before they run**. The code below is a tiny type checker for a small expression language. It walks the AST and either confirms the program is well-typed or reports a type error — without executing a single expression. This previews Weeks 6–9.

```python  liascript
from dataclasses import dataclass
from typing import Any

# A tiny typed expression language:
@dataclass
class Num:   value: float
@dataclass
class Bool_: value: bool
@dataclass
class Add:   left: Any; right: Any   # requires both children to be Int
@dataclass
class If:    cond: Any; then_e: Any; else_e: Any  # Bool cond, same-type branches
@dataclass
class Not:   expr: Any  # requires Bool

def infer_type(expr) -> str:
    """Simple type inference for our tiny language."""
    if isinstance(expr, Num):   return "Int"
    if isinstance(expr, Bool_): return "Bool"

    if isinstance(expr, Add):
        lt = infer_type(expr.left)
        rt = infer_type(expr.right)
        if lt != "Int": raise TypeError(f"Add: left must be Int, got {lt}")
        if rt != "Int": raise TypeError(f"Add: right must be Int, got {rt}")
        return "Int"

    if isinstance(expr, Not):
        t = infer_type(expr.expr)
        if t != "Bool": raise TypeError(f"Not: requires Bool, got {t}")
        return "Bool"

    if isinstance(expr, If):
        tc = infer_type(expr.cond)
        if tc != "Bool": raise TypeError(f"If: condition must be Bool, got {tc}")
        tt = infer_type(expr.then_e)
        te = infer_type(expr.else_e)
        if tt != te: raise TypeError(f"If: branches must have same type, got {tt} and {te}")
        return tt

    raise TypeError(f"Unknown: {type(expr).__name__}")

def run_eval(expr):
    if isinstance(expr, Num):   return expr.value
    if isinstance(expr, Bool_): return expr.value
    if isinstance(expr, Add):   return run_eval(expr.left) + run_eval(expr.right)
    if isinstance(expr, Not):   return not run_eval(expr.expr)
    if isinstance(expr, If):    return run_eval(expr.then_e) if run_eval(expr.cond) else run_eval(expr.else_e)

def run(expr):
    t = infer_type(expr)
    v = run_eval(expr)
    print(f"  Type: {t:6}  Value: {v}")

print("Type-checked expressions:")
run(Add(Num(1), Num(2)))
run(If(Bool_(True), Num(1), Num(2)))
run(Not(Bool_(False)))

print("\nType ERRORS caught before execution:")
for expr, desc in [
    (Add(Num(1), Bool_(True)),             "Add(Int, Bool)"),
    (If(Num(1), Num(1), Num(2)),           "If(Int cond, ...)"),
    (If(Bool_(True), Num(1), Bool_(True)), "If branches: Int vs Bool"),
]:
    try:
        infer_type(expr)
    except TypeError as e:
        print(f"  {desc}: {e}")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

**Critical Thinking Questions (CTQs)**

> **CTQ 9** `infer_type` returns a string (`"Int"` or `"Bool"`) without running the expression. What does it mean to "check types without executing"? What kinds of errors can a static type checker NOT detect?

> **CTQ 10** `Add(Num(1), Bool_(True))` raises a TypeError. In Python (without our type checker), what does `1 + True` actually compute? What should a well-designed type system do about this — and why?

> **CTQ 11** `If` requires both branches to have the same type. Why? (Hint: the caller needs to know what type `if-then-else` returns — can it be either `Int` or `Bool` depending on the condition at runtime?)

> **Watch out!** A static type checker runs *before* the program executes — it reasons about types without ever computing a value. This means it cannot catch errors that depend on runtime data, like dividing by a variable that happens to be zero, or accessing an array at an index that is only known when the user types it. Do not confuse "type safe" with "bug free": a well-typed program can still crash or produce wrong answers; it just cannot crash in certain specific structural ways that the type system forbids.

> **CTQ 12** This type checker handles only `Int` and `Bool`. What would you need to add to support variables and functions? (Preview: the answer involves "type environments" and a rule called "unification.")

---

# Part IV: Running a Language You Designed

Once the blueprints are drawn, the materials are certified, and the inspector has signed off, it is time to actually build. An interpreter is the construction crew: it takes the structured plan (an AST) and turns it into a real, running result. The trickiest part is that functions remember where they were born — like a contractor who carries their own tool belt from job site to job site rather than borrowing whatever tools happen to be at the new location.

## Model 4: The Interpreter — Running a Language You Designed

An interpreter evaluates an AST directly. The one below handles variables, arithmetic, conditionals, lambda functions, function application, and let-bindings — the core of a real functional language. The key insight is **closures**: when a function is created, it captures the environment at the point of creation, not the environment at the point of call. This is the destination of Weeks 11–15.

```python  liascript
from dataclasses import dataclass, field
from typing import Any, Optional

# AST for a mini language with: numbers, variables, arithmetic,
# let-binding, lambda, function application, and if-then-else.
@dataclass
class Num:   value: float
@dataclass
class Var:   name: str
@dataclass
class BinOp: op: str; left: Any; right: Any
@dataclass
class If:    cond: Any; then_e: Any; else_e: Any
@dataclass
class Lam:   param: str; body: Any
@dataclass
class App:   func: Any; arg: Any
@dataclass
class Let:   name: str; val: Any; body: Any

@dataclass
class Closure:
    param: str; body: Any; env: Any

class Env:
    def __init__(self, bindings=None, parent=None):
        self.bindings = bindings or {}
        self.parent   = parent
    def lookup(self, name):
        if name in self.bindings: return self.bindings[name]
        if self.parent:           return self.parent.lookup(name)
        raise NameError(f"Undefined: '{name}'")
    def extend(self, name, value):
        return Env({name: value}, self)

def interp(expr, env: Env) -> Any:
    if isinstance(expr, Num):    return expr.value
    if isinstance(expr, Var):    return env.lookup(expr.name)
    if isinstance(expr, BinOp):
        l, r = interp(expr.left, env), interp(expr.right, env)
        return {'+': l+r, '-': l-r, '*': l*r, '/': l/r,
                '>': l>r, '==': l==r}[expr.op]
    if isinstance(expr, If):
        return interp(expr.then_e, env) if interp(expr.cond, env) else interp(expr.else_e, env)
    if isinstance(expr, Lam):
        return Closure(expr.param, expr.body, env)   # capture current env
    if isinstance(expr, App):
        fn  = interp(expr.func, env)
        arg = interp(expr.arg, env)
        if not isinstance(fn, Closure): raise TypeError(f"Not a function: {fn}")
        return interp(fn.body, fn.env.extend(fn.param, arg))  # call with closure's env
    if isinstance(expr, Let):
        val = interp(expr.val, env)
        return interp(expr.body, env.extend(expr.name, val))
    raise ValueError(f"Unknown: {type(expr)}")

global_env = Env()

# Higher-order function: make_adder returns a closure
make_adder = Lam('n', Lam('x', BinOp('+', Var('n'), Var('x'))))
add5 = App(make_adder, Num(5))
result = interp(App(add5, Num(3)), global_env)
print(f"make_adder(5)(3) = {result}")

# let x = 10 in let f = lambda y. x + y in f(7)
prog = Let('x', Num(10),
       Let('f', Lam('y', BinOp('+', Var('x'), Var('y'))),
       App(Var('f'), Num(7))))
print(f"let x=10 in let f=lambda y. x+y in f(7) = {interp(prog, global_env)}")

# if-then-else
cond_prog = If(BinOp('>', Num(5), Num(3)), Num(100), Num(0))
print(f"if 5>3 then 100 else 0 = {interp(cond_prog, global_env)}")

print("\n>>> By Week 12, you will have built this interpreter from scratch.")
print(">>> By Week 15, you will have added YOUR OWN features.")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

**Critical Thinking Questions (CTQs)**

> **CTQ 13** `Lam` creates a `Closure` when evaluated. What does a `Closure` capture (besides the parameter name and body)? Why is that captured value so important?

> **CTQ 14** In `App`, after calling `interp(fn.body, fn.env.extend(fn.param, arg))`, we use `fn.env` (the closure's captured environment) not the current `env`. Why? What would happen if we used `env` instead — give a concrete example where the behavior would differ.

> **CTQ 15** This interpreter handles: numbers, variables, +/-/*//, if-then-else, lambda, application, and let. What is it MISSING that a real language would need? List at least five things.

> **CTQ 16** The entire interpreter is 35 lines. What does this tell you about the core complexity of an interpreter vs its full feature set? Where does the real complexity live?

---

# Part V: The Whole Picture

The blueprints, the materials, the inspector, and the construction crew all have to work together in a specific order — you cannot frame walls before the foundation cures. The language implementation pipeline enforces the same discipline: raw source text flows through a scanner, then a parser, then a type checker, then an interpreter, with each stage handing a well-defined data structure to the next. This model shows all four stages in sequence so you can see, for the first time, how everything you have explored today fits into a single chain.

## Model 5: The Full Pipeline — Scanning → Parsing → Typing → Interpreting

Every programming language implementation is a **pipeline**: source text enters one end, and meaning comes out the other. The stages are scanning (breaking text into tokens), parsing (building an AST from tokens), type-checking (verifying the AST is well-typed), and interpreting or compiling (producing a result). The code below shows all four stages working together.

```python  liascript
import re
from dataclasses import dataclass, field
from typing import Any

# === STAGE 1: SCANNER ===
@dataclass
class Token:
    type: str; value: str; line: int

def scan(source: str) -> list:
    patterns = [
        ('NUMBER', r'\d+(\.\d+)?'), ('NAME',   r'[a-zA-Z_]\w*'),
        ('PLUS',   r'\+'),          ('MINUS',  r'-'),
        ('STAR',   r'\*'),          ('SLASH',  r'/'),
        ('EQEQ',   r'=='),          ('GT',     r'>'),
        ('EQ',     r'='),
        ('LPAREN', r'\('),          ('RPAREN', r'\)'),
        ('SKIP',   r'[ \t]+'),      ('NL',     r'\n'),
    ]
    keywords = {'if', 'then', 'else', 'let', 'in', 'lambda', 'true', 'false'}
    master = '|'.join(f'(?P<{n}>{p})' for n, p in patterns)
    tokens, line = [], 1
    for m in re.finditer(master, source):
        kind = m.lastgroup
        if kind == 'NL':   line += 1
        elif kind != 'SKIP':
            typ = 'KEYWORD' if m.group() in keywords else kind
            tokens.append(Token(typ, m.group(), line))
    tokens.append(Token('EOF', '', line))
    return tokens

# === STAGE 2 + 3: INTERPRETER (abbreviated from Model 4) ===
@dataclass
class Num2:   value: float
@dataclass
class Var2:   name: str
@dataclass
class BinOp2: op: str; left: Any; right: Any
@dataclass
class Lam2:   param: str; body: Any
@dataclass
class App2:   func: Any; arg: Any
@dataclass
class Let2:   name: str; val: Any; body: Any

class Env2:
    def __init__(self, b=None, p=None): self.b = b or {}; self.p = p
    def lookup(self, n):
        if n in self.b: return self.b[n]
        if self.p:      return self.p.lookup(n)
        raise NameError(n)
    def extend(self, n, v): return Env2({n: v}, self)

@dataclass
class Closure2: param: str; body: Any; env: Any

def run2(e, env):
    if isinstance(e, Num2):   return e.value
    if isinstance(e, Var2):   return env.lookup(e.name)
    if isinstance(e, BinOp2):
        l, r = run2(e.left, env), run2(e.right, env)
        return {'+':l+r,'-':l-r,'*':l*r,'/':l/r,'>':l>r,'==':l==r}[e.op]
    if isinstance(e, Lam2):   return Closure2(e.param, e.body, env)
    if isinstance(e, App2):
        fn, arg = run2(e.func, env), run2(e.arg, env)
        return run2(fn.body, fn.env.extend(fn.param, arg))
    if isinstance(e, Let2):
        v = run2(e.val, env)
        return run2(e.body, env.extend(e.name, v))

# === FULL PIPELINE DEMO ===
source = "let add = lambda x lambda y x + y in add 3 4"
print(f"Source: {source!r}")

tokens = scan(source)
tok_summary = [(t.type, t.value) for t in tokens if t.type != 'EOF']
print(f"\nStage 1 - Tokens ({len(tok_summary)} total):")
print(f"  {tok_summary}")

# Pre-built AST (what the parser would produce from the tokens above):
ast = Let2('add',
           Lam2('x', Lam2('y', BinOp2('+', Var2('x'), Var2('y')))),
           App2(App2(Var2('add'), Num2(3)), Num2(4)))
print(f"\nStage 2 - AST:")
print(f"  Let(add, Lambda(x, Lambda(y, x+y)), App(App(add,3),4))")

result = run2(ast, Env2())
print(f"\nStage 3 - Result: {result}")
print(f"\nThe pipeline: {source!r}")
print(f"           -> {int(result)}")

print("\n" + "="*50)
print("COURSE ROADMAP:")
print("  Weeks 1-4:  Functional programming + lambda calculus  (Model 1)")
print("  Weeks 5-8:  Types + grammars + scanning              (Models 2-3)")
print("  Weeks 9-15: Parsing + interpreting + YOUR language   (Models 4-5)")
print("="*50)
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

**Critical Thinking Questions (CTQs)**

> **CTQ 17** The scanner (Stage 1) converts `"let add = lambda x lambda y x + y in add 3 4"` into a list of tokens. What information is LOST during scanning (compared to the original source text)? Does any of that information matter for the meaning of the program?

> **CTQ 18** Stage 2 shows "what the parser would produce" — an AST. The AST for `add 3 4` is `App(App(add, 3), 4)`. Why is function application left-associative and nested, rather than a flat `App(add, [3, 4])`? What does this nesting tell you about how the language treats multi-argument functions?

> **CTQ 19** Stage 3 runs the interpreter. Trace through `run2(App2(App2(Var2('add'), Num2(3)), Num2(4)), env)` step by step: what is evaluated first, and what does the environment contain at each step?

> **CTQ 20** Looking at the Course Roadmap printed at the end: which part of the pipeline do you feel most confident about from prior courses? Which part is most unfamiliar? Write one concrete learning goal for yourself for the semester.

---

# Multiple Choice

[[MC]] In Model 1, `TRUE = lambda x: lambda y: x`. What is the type of `TRUE` in Haskell's type notation?

[(X)] `a -> b -> a` — it takes any type `a`, then any type `b`, and returns the `a` value
[( )] `Bool -> Bool -> Bool` — it takes two booleans and returns a boolean
[( )] `Int -> Int -> Int` — it takes two integers and returns an integer
[( )] `Any -> Any -> Any` — it takes two values of any type and returns one of them

---

[[MC]] In Model 2, the grammar has `expr → term (('+'|'-') term)*`. What does the `*` mean?

[( )] The `+` and `-` operators are optional and can appear at most once
[(X)] Zero or more occurrences of `(('+'|'-') term)` — the expression can have any number of additions or subtractions
[( )] The grammar is ambiguous and should be resolved with precedence rules
[( )] The `*` applies to the entire grammar rule, allowing any number of `expr` repetitions

---

[[MC]] Which of the following would a static type checker (Model 3) catch?

[(X)] `Add(Num(1), Bool_(True))` — adding an integer to a boolean
[( )] Dividing by a variable that might be zero at runtime
[( )] Accessing an array out of bounds when the index is not known at compile time
[( )] An infinite loop

---

[[MC]] In Model 4, a `Closure` captures the environment at the time the `lambda` is created. What is this called?

[( )] Dynamic scoping — variables are looked up in the caller's environment
[(X)] Lexical (static) scoping — variables are looked up in the environment where the function was defined
[( )] Early binding — all variable references are resolved at parse time
[( )] Late binding — all variable references are resolved at first call

---

# Exercises

**Exercise 1.** Add a `Print` statement to the interpreter in Model 4: define a `@dataclass class Print_: expr: Any` that evaluates `expr`, prints the result, and returns it. Test with:

```
Let('x', Num(42), Print_(BinOp('+', Var('x'), Num(1))))
```

Expected output: `43` printed, and the overall value returned should be `43.0`.

**Exercise 2.** Extend the scanner in Model 5 to handle string literals (text between double quotes). Add a `STRING` token type whose pattern is `r'"[^"]*"'`. Verify with:

```
scan('"hello" + "world"')
```

What tokens are produced? What would you need to add to the interpreter to evaluate `Add` on strings?

**Exercise 3.** Write a `depth(ast)` function that computes the maximum depth of an AST from Model 4. Define: the depth of `Num(1)` is 1; the depth of `BinOp('+', Num(1), Num(2))` is 2; the depth of `BinOp('+', BinOp('+', Num(1), Num(2)), Num(3))` is 3. What is the depth of the `make_adder` program from Model 4?

**Exercise 4.** Write a `count_nodes(ast)` function that counts how many AST nodes a program has. Compare:

- `BinOp('+', Num(2), Num(3))` — 3 nodes
- `Num(5)` — 1 node

If an optimizer replaces the first with the second (constant folding), how much does the tree shrink? What fraction of nodes were eliminated? This is the simplest compiler optimization — look for constants and pre-compute them.

---

# Reflection

> You have just seen the entire arc of the course in one session. Looking back at the four Models — lambda calculus, grammars, type systems, interpreters — and forward to your final project: **what kind of language do you want to build?** What syntax would you use? What features matter most to you? What would make someone WANT to use a language you designed? Write a paragraph. Keep it — you will return to it in Week 15 and see how your thinking has changed.

---

# Further Reading

- *Structure and Interpretation of Computer Programs* (Abelson, Sussman) — free online at https://mitp-content-server.mit.edu/books/content/sectbyfn/books_pubs/6515/sicp.pdf — considered by many to be the finest programming languages textbook ever written; Chapters 1 and 3 are directly relevant to the first half of this course.

- *Programming Languages: Application and Interpretation* (Shriram Krishnamurthi) — the PLAI textbook used in this course; builds an interpreter incrementally from first principles, exactly as we will.

- Gabriel Lebec, "Lambda as JS, or A Flock of Functions" — https://speakerdeck.com/glebec/lambda-as-js-or-a-flock-of-functions-combinators-lambda-calculus-and-church-encodings-in-javascript — a direct visual preview of Weeks 2–4; Church encodings in JavaScript with beautiful diagrams.

- *Types and Programming Languages* (Pierce) — the graduate-level type theory text; Chapters 3–10 align with Weeks 6–9 of this course. Challenging but rewarding.

- Peter Norvig, "Lispy" — a Scheme interpreter in Python in 90 lines: http://norvig.com/lispy.html — if you finish the exercises early, read this; it is a compressed version of the entire second half of this course.
