# Modern Language Features
<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://github.com/BillJr99/Ursinus-CS374-Fall2026/blob/gh-pages/_pages/Activities/liascript-modernfeatures.md or locally via https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374-Fall2026/gh-pages/_pages/Activities/liascript-modernfeatures.md

import: https://raw.githubusercontent.com/liascript/CodeRunner/master/README.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

# Modern Language Features

> **Opening Hook:** Modern programming language features are not invented randomly or for aesthetic reasons — each one solves a concrete expressivity or safety problem that practitioners encountered at scale. Pattern matching exists because nested if-else chains and field accesses made tree-walking code unreadable and error-prone at the scale of production compilers. Generics exist because the alternative — writing the same `sort` function separately for every element type — was both tedious and unsafe. Ownership exists because C's manual memory management caused security vulnerabilities in billions of lines of deployed code. Async/await exists because callback-based I/O shredded programs into pieces so small that the control flow became impossible to follow. The through-line: language features are engineering responses to pain points, and understanding the pain explains the solution.

## Learning Goals

By the end of this activity, you will be able to:

- Apply pattern matching to dissect structured data and explain how exhaustiveness checking improves reliability over chained conditionals
- Define parametric generics with type variables and identify the variance and constraint issues that arise in practice
- Explain Rust's ownership and borrowing model and contrast it with garbage collection and manual memory management as approaches to memory safety
- Describe how `async`/`await` concurrency differs from OS threads and identify the performance tradeoffs of each model
- Evaluate which modern features are appropriate candidates for inclusion in a language design project and justify the choice using the problem/mechanism/cost framework

---

> **Before You Begin**
>
> This module assumes you are comfortable with:
> - Writing Python functions, classes, and basic control flow (if/else, for, while)
> - What an AST (Abstract Syntax Tree) is and how a tree-walking evaluator works — you should have built one in an earlier module
> - The idea that a *type* constrains what operations are valid on a value
> - Basic familiarity with at least one language besides Python (Java, C, JavaScript, or Rust)
>
> You do **not** need prior experience with Rust, Haskell, or async programming. All features are introduced with Python examples before any cross-language comparisons.

---

Language design did not stop with the features your interpreter implements; it accelerated. Today we survey four ideas that define the current generation (pattern matching, generics, memory safety through ownership, and async concurrency), each through the lenses you have built: what problem it solves, what it costs, and which evaluation criterion it serves. Your project pitches a feature menu next week; today stocks the menu. The arc: **pattern matching $\rightarrow$ generics $\rightarrow$ ownership $\rightarrow$ async $\rightarrow$ choosing for your language**.

---

## Directions and Group Roles

Work in your POGIL team with rotated roles (**Manager**, **Recorder**, **Presenter**, **Reflector**). Today runs as a jigsaw: each pair takes one feature as primary, then teaches it back using the three-lens template (problem, mechanism, cost). After class, respond to the reflective prompt individually in your notebook.

---

# Part I: The Features

> **Intuition:** Each of the four features in this part is presented through the same three-lens template: the *problem* it solves (what was painful before), the *mechanism* (the language construct that solves it), and the *cost* (what the programmer gives up to get the benefit). As you read, keep connecting back to your own interpreter project — several of these features apply directly to the code you have already written.

## 1. Pattern Matching: Branching on Shape

**The problem.** Code that dissects structured data degenerates into nested ifs and field accesses. **The mechanism.** A `match` tests a value against *patterns* that simultaneously check shape and bind variables; Python (3.10) joined Rust, Scala, and the ML family:

```python
def describe(node):
    try:
        match node:
            case ("num", n):
                return f"the number {n}"
            case ("+", left, right):
                return f"a sum of ({describe(left)}) and ({describe(right)})"
            case ("neg", inner):
                return f"the negation of {describe(inner)}"
            case _:
                return "something unrecognized"
    except Exception as e:
        print(f"[modern:describe] {e}")
        import traceback; traceback.print_exc()
        return ""

print(describe(("+", ("num", 2), ("neg", ("num", 3)))))
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

**The cost and the criterion.** A new syntactic form (readability spent up front, repaid in every dissection), and questions of exhaustiveness: ML-family compilers *prove* you handled every case, a reliability win your `evaluate`'s if-chain never gets. Notice the example: pattern matching is practically purpose-built for tree walks like yours.

## 2. Generics: Abstraction over Types

**The problem.** A statically typed list-of-int and list-of-string need the same code twice, or an unsafe any-type escape hatch. **The mechanism.** Parameterize the *type itself*: `List[T]`, `def first(items: list[T]) -> T`. The checker verifies the code once *for all* T, and call sites stay fully checked. **The cost and the criterion.** Type-system complexity (Java's wildcards, variance puzzles) traded for reliability-with-reuse; dynamically typed languages get the reuse for free and the checking never. Connect to the types module: generics exist precisely to keep static typing's early binding without its duplication.

## 3. Ownership: Memory Safety without a Garbage Collector

**The problem.** C frees memory manually (use-after-free, leaks, security holes); Java collects garbage at runtime (safe, but with pauses and overhead). **The mechanism.** Rust's third way: every value has exactly **one owner**; assignment *moves* ownership; **borrows** lend access temporarily (many readers or one writer, never both); the compiler proves at compile time that no reference outlives its value, so the program needs neither `free` nor a collector. **The cost and the criterion.** A famously steep learning curve ("fighting the borrow checker"): writability spent for reliability *and* performance simultaneously, which is why Rust keeps winning systems-programming converts. Binding-time lens: Rust moved memory-correctness from runtime (GC) or never (C) to compile time.

## 4. Async/Await: Concurrency as Syntax

**The problem.** Programs that wait (network, disk) waste their wait, and callback-based solutions shred control flow. **The mechanism.** `async` functions are *pausable*: `await` yields control at a wait point and resumes when the result arrives, letting one thread interleave thousands of waiting tasks; the compiler transforms your straight-line code into a state machine (a *desugaring*, industrial grade). **The cost and the criterion.** The "function color" problem: async functions can only be awaited from async functions, splitting the ecosystem in two; writability and performance for I/O-bound work, bought with a pervasive design constraint.

---

## Model 1: Three Lenses, Four Features

### Critical Thinking Questions

1. Complete the jigsaw grid as a class: for each feature, the problem, the mechanism in one sentence, the criterion served, and the criterion taxed.
2. Run the pattern-matching cell, then rewrite *your interpreter's* `evaluate` dispatch as a `match` on node classes (`case Num(value=n):` works on your classes!). Report: lines saved, readability verdict, and one behavior the if-chain allowed that match's structure discourages.
3. Ownership and garbage collection are both answers to "when may memory be reclaimed?" Place C, Java/Python, and Rust on a binding-time axis for that decision, and state each position's billion-dollar risk.
4. Which of the four features could a *tree-walking interpreter team* plausibly implement a slice of in three weeks, and which are out of reach? Justify with reference to which pipeline stage each feature lives in (parser? evaluator? a checker between them?).

[[MC]]
Rust achieves memory safety without a garbage collector primarily by:
- ( ) Forbidding heap allocation
- ( ) Checking every pointer at runtime
- (x) Compile-time ownership and borrowing rules that prove references cannot outlive the values they point to
- ( ) Running a collector only at program exit

---

# Part II: Runnable Models

## Model 2: Pattern Matching (Python 3.10+ match/case)

Python's `match` statement (PEP 634) goes far beyond a simple switch: it matches on *structure*, destructures into bindings, supports guards, and handles class patterns. The cell below walks through each capability with your CS374 AST as the running example.

```python
import sys

# Represent AST nodes as named tuples for clean pattern matching
from collections import namedtuple

Num   = namedtuple('Num',   ['value'])
BinOp = namedtuple('BinOp', ['op', 'left', 'right'])
Var   = namedtuple('Var',   ['name'])
Let   = namedtuple('Let',   ['name', 'value', 'body'])
If    = namedtuple('If',    ['cond', 'then', 'else_'])

def evaluate(node, env=None):
    """Tree-walking evaluator using match/case."""
    if env is None:
        env = {}
    match node:
        case Num(value=n):
            return n
        case Var(name=name):
            if name not in env:
                raise NameError(f"Unbound variable: {name}")
            return env[name]
        case BinOp(op='+', left=l, right=r):
            return evaluate(l, env) + evaluate(r, env)
        case BinOp(op='-', left=l, right=r):
            return evaluate(l, env) - evaluate(r, env)
        case BinOp(op='*', left=l, right=r):
            return evaluate(l, env) * evaluate(r, env)
        case BinOp(op='/', left=l, right=r):
            denom = evaluate(r, env)
            if denom == 0:
                raise ZeroDivisionError("division by zero in AST")
            return evaluate(l, env) / denom
        case Let(name=name, value=val, body=body):
            new_env = {**env, name: evaluate(val, env)}
            return evaluate(body, new_env)
        case If(cond=c, then=t, else_=e):
            return evaluate(t, env) if evaluate(c, env) else evaluate(e, env)
        case _:
            raise TypeError(f"Unknown node type: {type(node).__name__}")

# Test: (let x = 5 in x * x + 2)
ast1 = Let('x', Num(5), BinOp('+', BinOp('*', Var('x'), Var('x')), Num(2)))
print("let x=5 in x*x+2 =", evaluate(ast1))

# Test: if 0 then 1 else 42  (0 is falsy)
ast2 = If(Num(0), Num(1), Num(42))
print("if 0 then 1 else 42 =", evaluate(ast2))

# Test: 2 + 3 * 4  (precedence encoded in AST structure)
ast3 = BinOp('+', Num(2), BinOp('*', Num(3), Num(4)))
print("2 + (3 * 4) =", evaluate(ast3))

print()
print("--- Demonstrating exhaustiveness gap ---")
# Add a new node type NOT handled by match
Call = namedtuple('Call', ['func', 'arg'])
ast4 = Call('f', Num(1))
try:
    result = evaluate(ast4)
except TypeError as e:
    print(f"Caught: {e}")
    print("A match with no wildcard arm would be a silent no-op in Python.")
    print("ML compilers warn at compile time — Python warns only at runtime.")

print()
print("--- Guard patterns (match + if) ---")
def categorize(n):
    match n:
        case x if x < 0:
            return f"{x} is negative"
        case 0:
            return "zero"
        case x if x % 2 == 0:
            return f"{x} is positive even"
        case x:
            return f"{x} is positive odd"

for val in [-3, 0, 4, 7]:
    print(f"  categorize({val}) = {categorize(val)}")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

### Critical Thinking Questions

5. The `evaluate` function uses `case Num(value=n)` to match a namedtuple. What does Python check to decide this pattern matches — the type, the field name, the value, or all three? Contrast with a plain `isinstance` check.
6. The `case _:` wildcard arm raises a `TypeError`. Remove it and run the `Call` test. What does Python return silently? Explain why an ML compiler's exhaustiveness check is a stronger reliability guarantee than Python's runtime behavior.
7. The `Let` arm creates `new_env = {**env, name: ...}`. Why does it use a *copy* of the environment rather than mutating `env` directly? Connect this to the distinction between static and dynamic scope.
8. Rewrite `categorize` using `if/elif/else` chains. Count the lines. Then describe one pattern-match capability (structural decomposition, guard, variable binding) that the `if` version cannot express without additional code.

---

## Model 3: Dataclasses and __post_init__

Python's `@dataclass` decorator (PEP 557) auto-generates `__init__`, `__repr__`, and `__eq__` from field annotations. The `__post_init__` hook runs *after* the generated `__init__`, allowing validation and derived fields — a lightweight version of the invariant-checking constructors common in strongly typed languages.

```python
from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class Token:
    kind: str
    value: str
    line: int = 0
    col:  int = 0

    def __post_init__(self):
        # Invariant: kind must be one of the recognized types
        valid_kinds = {'NUM', 'ID', 'OP', 'LPAREN', 'RPAREN', 'EOF'}
        if self.kind not in valid_kinds:
            raise ValueError(f"Invalid token kind {self.kind!r}; expected one of {valid_kinds}")
        # Normalize: strip whitespace from value
        self.value = self.value.strip()

@dataclass
class ASTNode:
    """Base node — not instantiated directly."""
    pass

@dataclass
class NumNode(ASTNode):
    value: float

    def __post_init__(self):
        self.value = float(self.value)   # coerce int input to float

@dataclass
class BinOpNode(ASTNode):
    op:    str
    left:  ASTNode
    right: ASTNode

    def __post_init__(self):
        if self.op not in {'+', '-', '*', '/'}:
            raise ValueError(f"Unknown operator: {self.op!r}")

@dataclass(frozen=True)   # immutable: __hash__ is auto-generated
class Symbol:
    """An interned symbol — useful as a dict key."""
    name: str

    def __post_init__(self):
        if not self.name.isidentifier():
            raise ValueError(f"{self.name!r} is not a valid identifier")

# Demonstrate auto-generated methods
t1 = Token('NUM', '  42  ', line=3, col=7)
t2 = Token('ID',  'x',      line=3, col=10)
t3 = Token('OP',  '+',      line=3, col=12)

print("Token repr:", t1)           # __repr__ auto-generated
print("Tokens equal?", t1 == t2)   # __eq__  auto-generated
print("Value after strip:", repr(t1.value))  # __post_init__ stripped spaces

print()
ast = BinOpNode('+', NumNode(2), NumNode(3))
print("AST node:", ast)
print("Left operand:", ast.left)

print()
s1 = Symbol('x')
s2 = Symbol('x')
print("Symbol('x') == Symbol('x'):", s1 == s2)
print("Same hash (frozen=True enables this):", hash(s1) == hash(s2))
print("Can use as dict key:", {s1: 'the variable x'}[s2])

print()
print("--- Invariant violation ---")
try:
    bad = Token('UNKNOWN', 'oops')
except ValueError as e:
    print(f"Caught ValueError: {e}")

try:
    bad2 = Symbol('not-valid!')
except ValueError as e:
    print(f"Caught ValueError: {e}")

print()
print("Key insight: __post_init__ moves invariant checks to object construction,")
print("ensuring no Token or ASTNode can exist in an invalid state.")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

### Critical Thinking Questions

9. `@dataclass` generates `__init__` from the annotated fields. What is the advantage of having the generated `__init__` call `__post_init__` rather than placing validation in a separate `validate()` method you call manually?
10. `@dataclass(frozen=True)` makes instances immutable and auto-generates `__hash__`. Explain why mutability and hashability conflict, and name a use case in your CS374 project where an immutable, hashable AST node would be useful.
11. The `NumNode.__post_init__` coerces `self.value` to `float`. This is a *type coercion* at construction time. Compare this to a statically typed language where the field type annotation would prevent a non-float from being passed at all. Which approach is more *writable*? Which is more *reliable*?
12. Design a `FunctionDef` dataclass for your interpreter with fields `name`, `params` (a list of strings), and `body` (an `ASTNode`). Write the `__post_init__` that enforces: at least one parameter, no duplicate parameter names, and `body` is actually an `ASTNode`. Write only the class definition, not the full interpreter.

---

## Model 4: Type Annotations, Generators, and Context Managers

Python's type system, generators, and context managers are three orthogonal features that each address a distinct design concern: **static documentation**, **lazy computation**, and **resource safety**. The cell explores all three in the context of a token stream — a structure your compiler pipeline uses.

```python
from typing import Iterator, Generator, List, Optional, TypeVar
from contextlib import contextmanager
import time

T = TypeVar('T')

# ── Type annotations ────────────────────────────────────────────────────────
# Annotations do not change runtime behavior in Python, but they document
# intent and enable type-checker tools (mypy, pyright) to catch errors early.

def tokenize(source: str) -> List[tuple[str, str]]:
    """Return a flat list of (kind, value) pairs."""
    tokens: List[tuple[str, str]] = []
    i = 0
    while i < len(source):
        if source[i].isspace():
            i += 1
        elif source[i].isdigit():
            j = i
            while j < len(source) and source[j].isdigit():
                j += 1
            tokens.append(('NUM', source[i:j]))
            i = j
        elif source[i].isalpha():
            j = i
            while j < len(source) and source[j].isalnum():
                j += 1
            tokens.append(('ID', source[i:j]))
            i = j
        elif source[i] in '+-*/()':
            tokens.append(('OP', source[i]))
            i += 1
        else:
            tokens.append(('UNKNOWN', source[i]))
            i += 1
    tokens.append(('EOF', ''))
    return tokens

tokens = tokenize("2 + foo * 3")
print("Tokenize result:", tokens)
print()

# ── Generators ───────────────────────────────────────────────────────────────
# A generator function uses 'yield' instead of 'return'.
# It produces values lazily — only when the caller asks for the next one.
# This is ideal for token streams: no need to materialise the whole list.

def tokenize_lazy(source: str) -> Generator[tuple[str, str], None, None]:
    """Yield tokens one at a time — O(1) memory, regardless of source length."""
    i = 0
    while i < len(source):
        if source[i].isspace():
            i += 1
            continue
        elif source[i].isdigit():
            j = i
            while j < len(source) and source[j].isdigit():
                j += 1
            yield ('NUM', source[i:j])
            i = j
        elif source[i].isalpha():
            j = i
            while j < len(source) and source[j].isalnum():
                j += 1
            yield ('ID', source[i:j])
            i = j
        elif source[i] in '+-*/()':
            yield ('OP', source[i])
            i += 1
        else:
            yield ('UNKNOWN', source[i])
            i += 1
    yield ('EOF', '')

print("Lazy tokenizer (consuming one at a time):")
gen = tokenize_lazy("x + 42")
for tok in gen:
    print(f"  next token: {tok}")
print()

# Generator as infinite stream — only possible with lazy evaluation
def integers_from(n: int) -> Generator[int, None, None]:
    while True:
        yield n
        n += 1

def take(n: int, it) -> List:
    return [next(it) for _ in range(n)]

print("First 5 integers from 10:", take(5, integers_from(10)))
print()

# ── Context managers ─────────────────────────────────────────────────────────
# 'with' guarantees cleanup (the __exit__ method) even if an exception occurs.
# @contextmanager lets you write a generator-based context manager.

@contextmanager
def parse_session(source: str):
    """
    A context manager that sets up and tears down a parse session.
    Guarantees: the token stream is always closed on exit.
    """
    print(f"[session] Opening parse session for: {source!r}")
    tokens = list(tokenize_lazy(source))
    session = {'tokens': tokens, 'pos': 0, 'errors': []}
    try:
        yield session
    except Exception as e:
        session['errors'].append(str(e))
        print(f"[session] Error during parse: {e}")
    finally:
        print(f"[session] Closing session. Errors: {session['errors'] or 'none'}")
        print(f"[session] Tokens consumed: {session['pos']}/{len(tokens)}")

with parse_session("2 + 3") as s:
    print("Inside session, tokens:", s['tokens'])
    s['pos'] = len(s['tokens'])   # simulate consuming all tokens

print()
with parse_session("bad $ input") as s:
    print("Inside session with bad input")
    raise ValueError("unexpected token at position 4")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

### Critical Thinking Questions

13. The return type annotation `Generator[tuple[str, str], None, None]` has three type parameters. Look up what each means (yield type, send type, return type). Why is the send type `None` for a tokenizer, and when would a non-`None` send type be useful?
14. Compare `tokenize` (returns a list) with `tokenize_lazy` (yields tokens). For a 1 GB source file, which is preferable and why? Identify the specific trade-off in terms of memory usage versus random access capability.
15. The `@contextmanager` decorator wraps a generator function with a single `yield`. The code *before* `yield` is `__enter__`; code *after* is `__exit__`. Rewrite `parse_session` as a class with explicit `__enter__` and `__exit__` methods. Which form is more readable, and which is more explicit about the resource lifecycle?
16. Python's type annotations are not enforced at runtime (without a separate checker). Name one scenario in your CS374 project where a type error that annotations would expose at type-check time actually caused a runtime bug during testing. If you cannot recall one, invent a plausible example involving mismatched AST node types.

---

## 2. Exercises

1. *Feature pitch.* Each pair writes a half-page pitch for adding their jigsaw feature (or an honest slice of it) to the team language: the construct's syntax in your grammar's EBNF, the node it adds, the evaluator rule, and the criterion it serves. The team votes one pitch onto the project's "stretch goals" list.
2. *Exhaustiveness by hand.* Add a new node type to your AST but not to your match-based evaluate. Run it; read the failure. Now add a `case _:` that raises a located error listing the node type. You have hand-built the safety net ML compilers automate; one sentence on the difference.
3. *Color audit.* Sketch (no implementation) what adding async to your language would split: which built-ins become awaitable, which functions change color, what the REPL does with a pending value. Conclude with a recommendation and its rationale.
4. *Feature archaeology.* Each teammate picks one feature that *arrived* in a mainstream language during their lifetime (Python match 2021, Java records 2020, JS async 2017, C++ lambdas 2011) and reports the proposal document's stated motivation versus what we identified today.

---

## Reflection Prompt

In your notebook: every feature today moved some check or transformation to an earlier binding time at the price of language complexity. Is there a complexity budget beyond which a language should stop adding features, and who in a language community should hold that budget? Answer as the designer you are about to be.

---

## 3. Further Reading

- The Rust Book, chapter 4 (ownership): https://doc.rust-lang.org/book/
- PEP 634 through 636 (Python structural pattern matching), especially 636, the tutorial.
- Bob Nystrom. "What Color is Your Function?" (online essay), the async critique, vividly argued.
