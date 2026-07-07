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

> **Intuition:** The three-lens template (problem / mechanism / cost) is a general framework for evaluating *any* language feature, not just the four covered here. When you encounter a new feature in the wild — Python's walrus operator `:=`, JavaScript's optional chaining `?.`, Kotlin's coroutines — you can immediately ask these three questions to understand it. Notice that "cost" is not always a drawback: sometimes you are deliberately spending writability to buy reliability, or spending simplicity to buy performance. The interesting question is always *whether the trade is worth it* in your target use case.

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

> **Watch out!** Python's `match` is **not** a switch statement. A switch matches on a single value (like an integer or string). Python's `match` matches on *structure*: it can simultaneously check the type of an object, destructure it into named components, and bind those components to variables — all in one pattern. If you find yourself writing `match x: case 1: ... case 2: ...` you are using only a small fraction of what `match` can do.

## Model 2: Pattern Matching (Python 3.10+ match/case)

> **Intuition:** Before `match`, writing a tree-walking evaluator in Python meant chains of `if isinstance(node, Num):` checks, followed by manual attribute accesses (`node.value`), all nested inside each other. With `match`, you write `case Num(value=n):` and in one line you have checked the type, extracted the field, and bound it to a local variable. The code mirrors the structure of the data it processes — which is exactly what you want when the data *is* a tree.

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

> **Watch out!** Python's `match` does **not** enforce exhaustiveness at compile time. If no arm matches, Python silently returns `None` — it does not raise an error. In Rust, OCaml, and Haskell, a non-exhaustive `match` is a *compile error* or at least a warning. This means that in Python, if you add a new AST node type and forget to add a case for it, your evaluator will silently return `None` and the bug may not surface until much later. The `case _: raise ...` wildcard arm is your manual safety net.

## Model 3: Dataclasses and __post_init__

> **Intuition:** A `@dataclass` is Python's shortcut for a class whose job is primarily to hold data. Instead of writing `__init__`, `__repr__`, and `__eq__` by hand — all of which are boilerplate that mirrors the field list you already wrote as annotations — `@dataclass` generates them for you. The `__post_init__` hook is the place to add any validation logic that goes beyond "assign these fields": it runs after the generated `__init__`, so you can check invariants and raise errors before the object escapes into the rest of the program.

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

> **Watch out!** `@dataclass(frozen=True)` makes an instance *immutable after construction*, but it is not the same as a deeply immutable object. If a frozen dataclass has a field that holds a mutable list, the list's contents can still change — `frozen` prevents reassignment of the field itself (`obj.field = new_value` will raise `FrozenInstanceError`), but does not prevent mutation of the object the field points to (`obj.field.append(x)` still works). For true immutability, all fields must themselves be immutable.

## Model 4: Type Annotations, Generators, and Context Managers

> **Intuition:** This model covers three Python features that look unrelated but share a common theme: each one lets you express a program's *intent* more precisely without changing its runtime behavior. Type annotations document the expected shapes of data. Generators let you describe a lazy sequence without materializing it. Context managers let you express "this block needs setup and guaranteed teardown" as a first-class construct rather than a try/finally pattern you must remember to write. All three are about making the code's intent visible and verifiable — to other programmers, to type checkers, and to the runtime.

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

## Going Deeper (Optional Appendices)

The core lesson above stands on its own. The optional deep dives below expand on it — read whichever interest you:

- Objects and OOP: From Closures to Vtables
- Macros and Metaprogramming: Code that Writes Code
- The Expression Problem

## Going Deeper: Objects and OOP: From Closures to Vtables

Think of a TV remote. It has **buttons** — methods you can call (`channel_up()`, `mute()`). It has **internal state** — which channel you're on, the current volume. And it **hides the implementation details** — you don't need to understand infrared encoding to change the channel. That bundle of state + behavior + hidden internals is an object. OOP is a *language design decision* that promotes this pattern to first-class status: the language gives you syntax, dispatch rules, and inheritance machinery specifically built around it. This activity asks: where does that machinery come from, and what trade-offs did the language designers make?

#### Learning Goals

By the end of this activity, you will be able to:

- Implement an object with encapsulated mutable state using only closures, without any class machinery, and explain why the two approaches are semantically equivalent
- Describe how a vtable (virtual dispatch table) enables dynamic polymorphism, and trace method resolution for a given class hierarchy by hand
- Predict Python's method resolution order (MRO) for a multiple-inheritance diamond hierarchy and verify the prediction using `ClassName.__mro__`
- Compare the OOP models of Python, Java, and C++ across the dimensions of single vs. multiple inheritance, dynamic vs. static dispatch, and interface vs. abstract-class design

> **Prerequisites:** Basic Python classes, functional programming activity
> **Goal:** See objects as a special case of closures, understand how vtables implement dynamic dispatch, and explore the OOP design space across Python, Java, and C++.

**POGIL Roles:** Driver · Recorder · Reporter · Manager

---

> **Before You Begin**
>
> This activity builds on two earlier topics:
>
> - **Closures and higher-order functions** — you should be comfortable with the idea that a function can capture variables from its enclosing scope and carry them along after the enclosing function returns.
> - **Basic Python classes** — you should know how to define a class with `__init__`, instance variables (`self.x`), and instance methods.
>
> If either of those feels shaky, skim the functional-programming activity before continuing here.

---

#### Model 1: Objects Are Closures

**Intuition.** Before `class` syntax existed in languages like Python and Java, programmers who wanted to bundle state with behavior had exactly one tool: closures. A closure is a function that "closes over" variables in its surrounding scope — those variables persist as long as the closure exists. If you return *multiple* closures that all close over the *same* variable, you have something that behaves exactly like an object: shared private state and a set of operations on it. This model shows the two approaches side-by-side so you can see they are semantically identical — `class` syntax is convenience, not new power.

Before classes existed, programmers built "objects" using closures — a function that captures mutable state and returns a bundle of operations.

**Counter as a closure (no class):**

```python
def make_counter(start=0):
    count = [start]   # mutable cell — list trick because int is immutable

    def get():
        return count[0]

    def increment(by=1):
        count[0] += by

    def reset():
        count[0] = start

    return {"get": get, "increment": increment, "reset": reset}

c = make_counter(10)
c["increment"]()
c["increment"](5)
print(c["get"]())   # 16
c["reset"]()
print(c["get"]())   # 10
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

**Exact same behavior as a class:**

```python
class Counter:
    def __init__(self, start=0):
        self._start = start
        self._count = start

    def get(self):
        return self._count

    def increment(self, by=1):
        self._count += by

    def reset(self):
        self._count = self._start

c = Counter(10)
c.increment()
c.increment(5)
print(c.get())   # 16
c.reset()
print(c.get())   # 10
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

> **Watch out!** The `count = [start]` list trick is a workaround for Python's scoping rules: plain assignment inside a nested function (`count = count + 1`) creates a *new local* variable rather than updating the enclosing one. Wrapping the value in a list makes the container immutable (you never rebind `count`) while the *contents* are mutable. Python 3 lets you use `nonlocal count` to declare that you mean the enclosing binding — the exercise at the end of this activity asks you to do exactly that.

**Key insight:** `self` is just the *captured environment* — the dict of instance variables. A class is syntactic sugar over a closure that:

1. Collects state into a named record (`self.__dict__`)
2. Associates methods with that record through the class namespace
3. Adds inheritance and the MRO

> **Critical Thinking Questions 1–3**

**CTQ 1.** In the closure version, `count` is a list rather than a plain `int`. Why? (What would go wrong with `count = start` followed by `count += by` inside `increment`?)

[[___ your answer here ___]]

**CTQ 2.** The closure version uses a dictionary of functions (`{"get": get, ...}`). In the class version, where is the equivalent dictionary stored? Use Python's introspection tools in your answer.

[[___ your answer here ___]]

**CTQ 3.** A functional programmer says: "Classes are just closures with nicer syntax." An OOP programmer says: "Closures are just classes without identity or inheritance." What does each side mean, and which features does each version lack?

[[___ your answer here ___]]

---

#### Model 2: Python's Object Model

**Intuition.** In Python, "everything is an object" is not a slogan — it is literally true at the implementation level. Every object carries a `__dict__`: a plain Python dictionary mapping attribute names to values. When you write `p.x = 3`, Python is doing `p.__dict__['x'] = 3`. Methods are *not* stored per-instance; they live in the *class's* `__dict__` and are looked up through the class when you access them on an instance. Understanding this lookup chain — instance dict first, then class dict, then base classes — explains virtually every surprising behavior in Python's object model.

Every Python object is backed by a dictionary. Understanding `__dict__` unlocks the whole object model.

```python
class Point:
    class_var = "I am shared"   # class-level attribute

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __repr__(self):
        return f"Point({self.x}, {self.y})"

    def __eq__(self, other):
        return isinstance(other, Point) and self.x == other.x and self.y == other.y

    def __hash__(self):
        return hash((self.x, self.y))

p = Point(3, 4)
q = Point(3, 4)

print("Instance dict:", p.__dict__)
print("Class dict keys:", list(type(p).__dict__.keys()))
print("p == q:", p == q)          # True — uses __eq__
print("p is q:", p is q)          # False — different objects
print("hash(p):", hash(p))
print("MRO:", type(p).__mro__)
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

##### Attribute Lookup Order

When you write `p.x`, Python does:

```
1. Check type(p).__mro__ for data descriptors (like property)
2. Check p.__dict__
3. Check type(p).__dict__ and each class in MRO for non-data descriptors
4. Raise AttributeError
```

The **descriptor protocol** is how methods work: `Point.distance` is a function (a descriptor). When accessed through an instance, it becomes a *bound method* that prepends `self`.

> **Critical Thinking Questions 4–5**

**CTQ 4.** What is stored in `p.__dict__` vs `type(p).__dict__`? Which one holds instance variables, and which holds methods?

[[___ your answer here ___]]

**CTQ 5.** If you write `p.class_var = "new"`, what happens to `Point.class_var`? What happens to `q.class_var`? Why?

[[___ your answer here ___]]

---

#### Model 3: Inheritance and the MRO

**Intuition.** Inheritance lets a subclass *reuse* a superclass's methods without copying them. Single inheritance is simple: when Python can't find a method on `Dog`, it checks `Animal`, then `object`. Multiple inheritance is where things get tricky: if both `B` and `C` define the same method and `D` inherits from both, which one wins? Python's answer is the **C3 linearization algorithm**, which produces a single ordered list — the MRO — that determines the search order. The key guarantee: a class always appears in the MRO *before* any of its parents, and the left-to-right order you specify in the class definition is respected wherever possible.

**Single inheritance** is straightforward: `Dog` extends `Animal`, so `Dog.__mro__` is `[Dog, Animal, object]`.

**Multiple inheritance** creates ambiguity. Python uses the **C3 linearization** algorithm to produce a consistent Method Resolution Order (MRO).

```python
class A:
    def hello(self): print("A.hello")

class B(A):
    def hello(self): print("B.hello")

class C(A):
    def hello(self): print("C.hello")

class D(B, C):
    pass

# Diamond: D → B → C → A → object
print([cls.__name__ for cls in D.__mro__])
# ['D', 'B', 'C', 'A', 'object']

d = D()
d.hello()   # B.hello — first in MRO with hello defined
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

##### The Diamond Problem

Without C3 linearization, `D.hello()` could go to either `B.hello` or `C.hello`. Python's rule: left-to-right depth-first, but each class appears only *after* all its subclasses — this is the C3 constraint.

> **Watch out!** `super()` does **not** mean "call my parent class." It means "call the *next class in the MRO*." In a multiple-inheritance hierarchy, that next class may be a sibling class, not a parent. If any class in the chain calls `super()` but one of its MRO-siblings does not, the chain breaks and some classes are skipped entirely. The cooperative multiple-inheritance pattern only works when *every* class in the hierarchy uses `super()` consistently.

##### `super()` Follows the MRO

```python
class A:
    def greet(self): print("A")

class B(A):
    def greet(self):
        print("B")
        super().greet()   # calls next in MRO, not necessarily A

class C(A):
    def greet(self):
        print("C")
        super().greet()

class D(B, C):
    def greet(self):
        print("D")
        super().greet()

D().greet()   # D → B → C → A  (each super() follows MRO)
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

> **Critical Thinking Questions 6–8**

**CTQ 6.** What is the MRO for `class E(C, B)` (reversed order from D)? How does changing the order of base classes affect which method is called?

[[___ your answer here ___]]

**CTQ 7.** Why does `super()` in cooperative multiple inheritance work correctly only when *every* class in the hierarchy calls `super()`? What breaks if one class skips it?

[[___ your answer here ___]]

**CTQ 8.** Java and C# do not allow multiple inheritance of classes (only interfaces). What problem does this avoid? What does it make harder?

[[___ your answer here ___]]

---

#### Model 4: Virtual Dispatch and Vtables

**Intuition.** When you write `s.area()` and `s` might be a `Circle` or a `Square`, how does the runtime know which `area` method to call? In statically compiled languages like C++, the compiler can't always know the runtime type at the call site — so instead of hardcoding a function address, it creates a **vtable** (virtual dispatch table): a small array of function pointers, one per virtual method, stored per *class*. Each object carries a hidden pointer to its class's vtable. Calling a virtual method means: load the vtable pointer, index into it, call the function at that slot. Python achieves the same effect through dictionary lookup — more flexible, but with more overhead.

In C++, when a class has `virtual` methods, the compiler creates a **vtable** — a table of function pointers — one per class.

```
C++ memory layout for a virtual class:

Object in memory:
┌──────────────┐
│   vptr       │──────────────────→ vtable for Shape
│   (8 bytes)  │                   ┌──────────────────┐
├──────────────┤                   │  &Shape::draw    │  [0]
│   x = 3.0    │                   │  &Shape::area    │  [1]
│   y = 4.0    │                   │  &Shape::~Shape  │  [2]
└──────────────┘                   └──────────────────┘

Circle object (inherits Shape):
┌──────────────┐
│   vptr       │──────────────────→ vtable for Circle
│   (8 bytes)  │                   ┌──────────────────┐
├──────────────┤                   │  &Circle::draw   │  [0] ← overridden
│   x, y       │                   │  &Circle::area   │  [1] ← overridden
│   radius     │                   │  &Shape::~Shape  │  [2]
└──────────────┘                   └──────────────────┘
```

**Every virtual call:**

1. Load `vptr` from object header (one memory read)
2. Index into vtable to get function pointer (another memory read + possible cache miss)
3. Indirect call through the function pointer

**Python's equivalent:**

```python
class Shape:
    def area(self):
        return 0.0

class Circle(Shape):
    def __init__(self, r):
        self.r = r
    def area(self):
        return 3.14159 * self.r ** 2

class Square(Shape):
    def __init__(self, s):
        self.s = s
    def area(self):
        return self.s ** 2

shapes = [Circle(5), Square(4), Circle(3)]
for s in shapes:
    print(f"{type(s).__name__}: area = {s.area():.2f}")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

##### Abstract Base Classes Enforce the Interface

```python
from abc import ABC, abstractmethod

class Shape(ABC):
    @abstractmethod
    def area(self) -> float: ...

    @abstractmethod
    def perimeter(self) -> float: ...

class Circle(Shape):
    def __init__(self, r: float):
        self.r = r
    def area(self) -> float:
        return 3.14159 * self.r ** 2
    def perimeter(self) -> float:
        return 2 * 3.14159 * self.r

# Shape()        # TypeError: Can't instantiate abstract class
print(Circle(5).area())
print(Circle(5).perimeter())
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

> **Critical Thinking Questions 9–11**

**CTQ 9.** What is the cost of a virtual function call vs a direct (non-virtual) call in C++? Name one scenario where this cost matters and one where it does not.

[[___ your answer here ___]]

**CTQ 10.** Python method dispatch does not use a C-style vtable. Instead, it looks up the method name as a string key in the class's `__dict__`. What are the trade-offs of this approach vs a fixed-index vtable?

[[___ your answer here ___]]

**CTQ 11.** What happens in Python if you try to instantiate a class that inherits from `ABC` but does not implement all `@abstractmethod` methods? What is the analogous mechanism in Java and C++?

[[___ your answer here ___]]

---

#### Model 5: Protocols, Duck Typing, and Interfaces

**Intuition.** Once you have objects, you face a new design question: how do you write code that works with *any* object that has a certain set of methods, without knowing the exact type in advance? This is the **interface problem**. Python answers it three different ways, each representing a different philosophy. Duck typing says "just try it — if it quacks, it's a duck." ABCs say "declare your intent explicitly by inheriting from a contract class." Protocols say "describe the required *shape* structurally — if an object has the right methods, it satisfies the contract, even if it never heard of this protocol." Each approach shifts the burden of checking (runtime vs. static analysis) and the coupling between the contract and its implementers.

Python offers three ways to define an interface contract:

| Approach | Mechanism | Checked when |
|---|---|---|
| Duck typing | Implicit — just call the method | Runtime (AttributeError) |
| `ABC` + `abstractmethod` | Nominal — inherit from ABC | Instantiation time |
| `Protocol` | Structural — shape matching | Static analysis (mypy) / runtime with `@runtime_checkable` |

```python
from typing import Protocol, runtime_checkable

@runtime_checkable
class Drawable(Protocol):
    def draw(self) -> None: ...
    def bounding_box(self) -> tuple: ...

class Sprite:
    def draw(self) -> None:
        print("Drawing sprite")
    def bounding_box(self) -> tuple:
        return (0, 0, 100, 100)

class Particle:
    def draw(self) -> None:
        print("Drawing particle")
    def bounding_box(self) -> tuple:
        return (50, 50, 52, 52)

class AudioClip:
    def play(self) -> None:
        print("Playing audio")

items = [Sprite(), Particle(), AudioClip()]
for item in items:
    if isinstance(item, Drawable):
        item.draw()
    else:
        print(f"{type(item).__name__} is not Drawable")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

##### Mixins — Reuse Without Inheritance Chains

A **mixin** is a class that provides methods to be mixed into other classes without being a standalone base class:

```python
class JsonMixin:
    def to_json(self):
        import json
        return json.dumps(self.__dict__)

class LogMixin:
    def log(self, msg):
        print(f"[{type(self).__name__}] {msg}")

class User(JsonMixin, LogMixin):
    def __init__(self, name, age):
        self.name = name
        self.age = age

u = User("Alice", 30)
print(u.to_json())
u.log("created")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

##### `__slots__` for Memory Optimization

> **Watch out!** `__slots__` and inheritance interact in a subtle way. If a *parent* class does not define `__slots__`, it still has a `__dict__`, and subclasses will inherit it — meaning the memory savings you wanted are lost. For `__slots__` to eliminate `__dict__` across the whole hierarchy, *every* class in the inheritance chain must declare `__slots__`. Additionally, defining `__slots__` prevents you from adding arbitrary attributes at runtime, which can break mixins or third-party code that expects a `__dict__`.

By default, every object has a `__dict__`, which is a Python dict — flexible but memory-heavy. `__slots__` replaces `__dict__` with fixed C-level attributes:

```python
class PointSlots:
    __slots__ = ("x", "y")
    def __init__(self, x, y):
        self.x = x
        self.y = y

p = PointSlots(3, 4)
print(p.x, p.y)
# p.z = 5  # AttributeError — no __dict__, no dynamic attributes
try:
    p.__dict__
except AttributeError as e:
    print(f"No __dict__: {e}")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

> **Critical Thinking Questions 12–15**

**CTQ 12.** `isinstance(obj, Protocol)` with `@runtime_checkable` checks only that the object has the right *method names*, not that their signatures match. Give a scenario where this leads to a false positive.

[[___ your answer here ___]]

**CTQ 13.** Mixins in Python are just regular classes mixed into the MRO. What discipline must you follow when writing a mixin to avoid breaking the cooperative `super()` chain?

[[___ your answer here ___]]

**CTQ 14.** When would you use `__slots__`? What functionality do you lose when you add it to a class?

[[___ your answer here ___]]

**CTQ 15.** Compare Java interfaces, Python Protocols, and Python ABCs. For each, state: (a) how compatibility is determined, (b) when errors are detected, and (c) one use case it handles best.

[[___ your answer here ___]]

---

#### Multiple Choice Review

**Question 1.** In C++, the primary purpose of a vtable is to:

- [( )] Store instance variable values for each object
- [(X)] Enable dynamic dispatch — calling the correct overridden method at runtime
- [( )] Implement multiple inheritance layout adjustments
- [( )] Provide metadata for the garbage collector

**Question 2.** Python's `super()` in a multiple-inheritance hierarchy follows:

- [( )] The first base class listed in the class definition
- [( )] The class named explicitly as the superclass
- [(X)] The next class in the MRO (C3 linearization order)
- [( )] The `object` base class directly

**Question 3.** Which of the following is the key difference between `ABC` with `@abstractmethod` and `Protocol` in Python?

- [( )] `ABC` is structural; `Protocol` is nominal
- [(X)] `ABC` requires explicit inheritance; `Protocol` uses structural subtyping
- [( )] `Protocol` can only be used for runtime checks; `ABC` works statically
- [( )] `ABC` supports multiple inheritance; `Protocol` does not

---

#### Exercises

**Exercise 1.** Rewrite the `make_counter` closure from Model 1 using `nonlocal` instead of the list trick. Verify that `increment`, `get`, and `reset` all work correctly:

```python
# Your solution here

```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

**Exercise 2.** Create a class `Vector2D` with `__add__`, `__mul__` (scalar), `__repr__`, `__eq__`, and `__abs__` (magnitude). Inspect its `__dict__` and `type(v).__dict__`:

```python
# Your solution here

```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

**Exercise 3.** Build a diamond hierarchy where classes `B` and `C` both override `describe()` and both call `super().describe()`. Show the complete call chain by printing inside each method:

```python
# Your solution here

```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

**Exercise 4.** Implement an abstract base class `Animal` with abstract methods `speak()` and `move()`. Create three concrete subclasses. Then iterate a list of mixed animals and call both methods:

```python
from abc import ABC, abstractmethod
# Your solution here

```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

**Exercise 5.** Define a `Serializable` Protocol with methods `to_dict(self) -> dict` and `from_dict(cls, d: dict)`. Implement it in two unrelated classes and verify `isinstance` checks:

```python
from typing import Protocol, runtime_checkable
# Your solution here

```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

---

#### Reflection

Answer each in 2–3 sentences:

1. This activity argued that objects are a special case of closures. Does the reverse hold — are closures a special case of objects? Defend your answer with a specific example.

2. Python's vtable equivalent (dict-based lookup) is more flexible than C++'s fixed vtable, but slower. Describe one programming pattern that is possible in Python because of this flexibility but impossible (or extremely awkward) in C++.

3. The MRO exists to solve the diamond problem. Describe in your own words what the C3 linearization rule guarantees, and explain why that guarantee matters for correctness.

---

*End of Activity — Objects and OOP: From Closures to Vtables*

## Going Deeper: Macros and Metaprogramming: Code that Writes Code

> Picture a pastry chef who, before turning on the oven, sits down with the recipe and rewrites every "1 cup sugar" as "200 grams sugar," every "1 stick butter" as "113 grams butter," and so on. The *transformation* happens before baking begins — the chef does not weigh things mid-recipe, they transform the recipe first. Macros work the same way: before the program runs, the macro system rewrites certain pieces of your code into different, fully expanded code. By the time execution starts, every macro call has already been replaced by ordinary code.

#### Learning Goals

By the end of this activity, you will be able to:

- Define macros and explain how they differ from functions by operating on unevaluated syntax rather than values
- Identify hygiene problems in naive macros and explain how hygienic macro systems prevent variable capture
- Implement a simple macro expander that transforms AST nodes before evaluation in a mini interpreter
- Compare macro systems across languages (Lisp, Rust, Julia, Elixir) and evaluate the expressiveness-versus-safety tradeoffs each makes
- Apply metaprogramming techniques to define new control-flow constructs that cannot be expressed as ordinary functions

> **Before You Begin**
>
> This activity assumes you are comfortable with:
>
> - **Abstract Syntax Trees (ASTs)** — programs are represented as nested data structures (tuples/dicts) before they are executed. If you have not seen an AST before, think of it as a parse tree: `1 + 2 * 3` becomes `('add', ('num', 1), ('mul', ('num', 2), ('num', 3)))`.
> - **Higher-order functions and decorators** — Model 5 registers macros using a `@defmacro` decorator. A decorator is just a function that takes a function and returns a (possibly modified) function.
> - **Python's `match`/`case` statement** — Model 3 uses structural pattern matching to destructure AST nodes. The pattern `case ('call', ('var', name), args)` succeeds when the tuple has exactly that shape and binds `name` and `args`.
> - **Evaluation order** — the key distinction in this activity is *when* arguments are evaluated: before a function call (eager evaluation) versus not at all until the macro expander decides (macro expansion time).
>
> No prior knowledge of Lisp or Scheme is required, though examples from those languages will appear for comparison.

> **"Macros are the most powerful feature in Lisp — and the most dangerous."**
>
> Languages like Lisp, Rust, Julia, and Elixir give programmers the ability to extend the language itself at compile time. Today you'll discover *why* macros are powerful, *what* hygienic macros solve, and *how* to implement a macro system in Mini.

#### Directions and Roles

Work in groups of 3–4. Rotate roles every 20 minutes.

- **Facilitator**: Keeps discussion on track; ensures everyone contributes.
- **Recorder**: Writes down answers and code that the group agrees on.
- **Reporter**: Presents findings to the class; explains the group's reasoning.
- **Reflector**: Monitors group process; writes the reflection at the end.

---

#### Model 1 — What is a Macro?

**Intuition.** The root difference between a function and a macro is *when* the arguments are evaluated. When you call `f(expensive_computation())`, Python evaluates `expensive_computation()` first, then passes the result to `f` — no matter what `f` does with it. A macro receives the *unevaluated expression* `expensive_computation()` as a chunk of syntax. It can choose to insert that expression into its output zero times (never run it), once, or multiple times. This is exactly why `and`/`or` can short-circuit but a function `my_and` cannot: `and` is macro-like, receiving unevaluated operands.

A **function** receives *values* as arguments and returns a value. A **macro** receives *syntax* (unevaluated AST nodes) as arguments and returns *syntax* that replaces the macro call at compile time.

```
            Function:   arguments evaluated BEFORE the call
            Macro:      arguments NOT evaluated; macro produces new syntax
```

Example — Python's `assert` is macro-like: `assert cond, msg` evaluates differently than a function call would, because if `cond` is False, it raises with the *expression text* of `cond`.

In languages without macros, you cannot define `assert` yourself — it requires compiler support. With macros, you can define `assert`, `while`, `or`, `and`, and even new loop constructs as library code.

```python  liascript
# The problem: Python's "and" short-circuits, but a function "my_and" does not
def my_and(a, b):
    return a and b   # evaluates b even if a is False!

def side_effect():
    print("Side effect!")
    return True

# With 'and': side effect only runs if first arg is True
print("Testing short-circuit:")
result1 = False and side_effect()  # side_effect NOT called
print(f"False and side_effect() = {result1}")

# With function: side effect ALWAYS runs
result2 = my_and(False, side_effect())  # side_effect IS called!
print(f"my_and(False, side_effect()) = {result2}")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

**Critical Thinking Questions (CTQs)**

> **CTQ 1.1** Python's `and`/`or` short-circuit but `my_and(a, b)` does not. Why? What would need to change about Python's evaluation strategy to allow `my_and` to short-circuit?

> **CTQ 1.2** `assert cond, msg` works by accessing the *source text* of `cond`. Could you implement this as a regular Python function? Why or why not?

> **CTQ 1.3** Name three features in Python that are "macro-like" (i.e., they have special evaluation rules that can't be replicated with a function). Examples: `with`, `yield`, `@decorator`.

---

> **Watch out!** The C preprocessor is shockingly literal. It substitutes text tokens with no understanding of operator precedence, parentheses, or statement boundaries. The traditional fix — wrapping every parameter and the whole body in parentheses (`((x) * (x))`) — is a workaround for the fact that the preprocessor cannot *understand* the code it is rewriting. Keep this in mind when you run the model below: the danger examples are real bugs that appear in production C code.

#### Model 2 — Textual Macros: The C Preprocessor

The simplest macros are **textual substitution** (C's `#define`):

```c
#define SQUARE(x)   ((x) * (x))
#define MAX(a, b)   ((a) > (b) ? (a) : (b))
#define DEBUG_PRINT(x) printf("%s = %d\n", #x, (x))
```

Textual macros are powerful but dangerous because they operate on *text*, not *syntax*:

```python  liascript
# Simulate C-style textual macro expansion in Python
import re

def expand_macros(code: str, macros: dict) -> str:
    """Simple textual macro expander (like C preprocessor)."""
    for name, (params, body) in macros.items():
        pattern = rf'{re.escape(name)}\(([^)]+)\)'
        def replacer(m):
            args = [a.strip() for a in m.group(1).split(',')]
            result = body
            for param, arg in zip(params, args):
                result = result.replace(param, arg)
            return result
        code = re.sub(pattern, replacer, code)
    return code

macros = {
    'SQUARE': (['x'], '((x) * (x))'),
    'MAX':    (['a', 'b'], '((a) > (b) ? (a) : (b))'),
}

# Safe usage
print(expand_macros('int s = SQUARE(5);', macros))

# DANGEROUS: SQUARE(1+2) → ((1+2) * (1+2)) — fine with parens
print(expand_macros('int s = SQUARE(1+2);', macros))

# MAX with side effects — double evaluation!
# MAX(f(), g()) → ((f()) > (g()) ? (f()) : (g()))
# f() is called TWICE!
print(expand_macros('int m = MAX(f(), g());', macros))
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

**CTQs**

> **CTQ 2.1** What is the double-evaluation problem with `MAX(f(), g())`? Why is this a problem in C code?

> **CTQ 2.2** Without the extra parentheses in `((x) * (x))`, what goes wrong with `SQUARE(1+2)`? Try it by removing the parens.

> **CTQ 2.3** The C preprocessor is called "textual" because it operates on source text, not AST nodes. What bug can occur with `MAX(a, b)` if `a` contains a newline? (Hint: think about multi-line expressions.)

---

#### Model 3 — AST Macros: Quoting and Quasiquoting

**Intuition.** The step from textual macros to AST macros is the step from text-editor find-and-replace to a real program transformation. Once you represent code as a *tree*, you can navigate it, inspect it, and build new trees from parts — all without worrying about parentheses or operator precedence, because the tree already encodes the structure. Quasiquote is a template-filling mechanism for trees: you write the output shape you want and mark the "holes" where computed values get spliced in, just like a string template but operating on tree nodes instead of characters.

Proper macro systems operate on **AST nodes**, not text. This requires two operations:

- **Quote** (`'`): freeze an expression as data — don't evaluate it
- **Quasiquote** (`` ` ``): like quote, but with **unquote** (`,`) holes that ARE evaluated

In Scheme/Lisp notation:
```scheme
'(1 2 3)          ; quoted list — the data [1, 2, 3]
`(1 ,(+ 1 1) 3)   ; quasiquoted — evaluates the unquoted part → [1, 2, 3]
`(let ,x ,val)    ; builds a let-node with x and val substituted in
```

```python  liascript
# Implementing quasiquote for our tuple-based AST
def quote(expr):
    """Return expr as data (don't evaluate)."""
    return expr

def quasiquote(template, bindings):
    """
    Fill in 'holes' (strings starting with '$') in a nested tuple template.
    $name → look up name in bindings dict.
    """
    match template:
        case str() if template.startswith('$'):
            return bindings[template[1:]]
        case tuple():
            return tuple(quasiquote(item, bindings) for item in template)
        case list():
            return [quasiquote(item, bindings) for item in template]
        case _:
            return template

# Example: build an AST for "while cond do body" using quasiquote
# Our tuple AST: ('while', condition, body_block)

def make_while_macro(cond_ast, body_ast):
    """Macro: while(cond, body) → ('while', cond, body)"""
    return quasiquote(('while', '$cond', '$body'), 
                      {'cond': cond_ast, 'body': body_ast})

# Build: while (x > 0) do { x = x - 1 }
while_node = make_while_macro(
    ('gt', ('var', 'x'), ('num', 0)),
    ('assign', 'x', ('sub', ('var', 'x'), ('num', 1)))
)
print("while macro expansion:")
print(while_node)

# Build a swap macro: swap(a, b) → let tmp=a in (a:=b; b:=tmp)
def make_swap_macro(a_name, b_name):
    tmp = f'_tmp_{a_name}_{b_name}'  # avoid name clashes (manual hygiene)
    return quasiquote(
        ('seq',
            ('assign', '$tmp', ('var', '$a')),
            ('seq',
                ('assign', '$a', ('var', '$b')),
                ('assign', '$b', ('var', '$tmp')))),
        {'tmp': tmp, 'a': a_name, 'b': b_name}
    )

swap_ab = make_swap_macro('x', 'y')
print("\nswap macro expansion for (x, y):")
print(swap_ab)
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

**CTQs**

> **CTQ 3.1** The `make_swap_macro` generates a fresh name `_tmp_x_y` to avoid name clashes. What would go wrong if we just used `tmp` as the name? Write a code example where this would cause a bug.

> **CTQ 3.2** Compare `quasiquote` here with Python's f-strings. What's similar? What's different? (Hint: f-strings work on text, quasiquote works on AST.)

> **CTQ 3.3** In Scheme, `define-syntax` / `syntax-rules` is the standard macro system. It's "pattern-based" — you write the input pattern and the output template. What are the benefits over our `quasiquote` approach?

---

#### Model 4 — The Hygiene Problem and Hygienic Macros

**Intuition.** Imagine your macro generates code that uses a helper variable called `tmp`. Now suppose the programmer using your macro also has a variable called `tmp`. After expansion, the two `tmp` references get tangled — the programmer's `tmp` is now in scope where your macro's `tmp` was supposed to be, or vice versa. This variable capture is the *hygiene problem*. The fix — `gensym`, generating a globally unique name like `_or_tmp7` — guarantees no accidental clash, because no human would ever choose that name.

> **Watch out!** The hygiene problem is subtle because it only shows up when *both* the macro author and the macro user happen to choose the same name. A macro might work correctly in 999 cases and silently break in the 1000th, when a user happens to name a variable `_tmp`. This is why modern macro systems (Scheme `syntax-rules`, Rust's macro hygiene) solve hygiene *automatically* — so library authors cannot accidentally ship a broken macro.

**Unhygienic macros** can accidentally *capture* variables from the context they're expanded in:

```python  liascript
# The classic hygiene problem
# Suppose we define a macro "or2(a, b)" that avoids double-evaluation:
# It expands to: let _tmp = a in (if _tmp then _tmp else b)

def expand_or2(a_ast, b_ast):
    """Unhygienic 'or' macro — uses a temporary variable."""
    return ('let', '_tmp', a_ast,
            ('if', ('var', '_tmp'), ('var', '_tmp'), b_ast))

# Safe usage:
print("or2(x > 0, y > 0) expands to:")
print(expand_or2(('gt', ('var', 'x'), ('num', 0)),
                 ('gt', ('var', 'y'), ('num', 0))))

# HYGIENE BUG: What if the user's code HAS a variable called _tmp?
# or2(_tmp, x > 0) — but _tmp is the user's variable!
# expands to: let _tmp = _tmp in (if _tmp then _tmp else (x > 0))
# The user's _tmp is shadowed by our macro's _tmp!
broken = expand_or2(('var', '_tmp'), ('gt', ('var', 'x'), ('num', 0)))
print("\nor2(_tmp, x>0) — BROKEN expansion:")
print(broken)
# The 'let _tmp = _tmp' binds a NEW _tmp to itself — looks up user's _tmp,
# but then inside the body, ('var', '_tmp') refers to the MACRO's _tmp.
# For simple literals this is OK, but in general the user's _tmp is captured.

# Hygienic solution: use a fresh, globally unique name
_gensym_counter = 0
def gensym(prefix='_g'):
    global _gensym_counter
    _gensym_counter += 1
    return f'{prefix}{_gensym_counter}'

def expand_or2_hygienic(a_ast, b_ast):
    """Hygienic 'or' macro — uses a fresh unique name."""
    tmp = gensym('_or_tmp')   # guaranteed fresh
    return ('let', tmp, a_ast,
            ('if', ('var', tmp), ('var', tmp), b_ast))

print("\nHygienic or2(_tmp, x>0):")
print(expand_or2_hygienic(('var', '_tmp'), ('gt', ('var', 'x'), ('num', 0))))
# Now the fresh name won't clash with _tmp
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

**CTQs**

> **CTQ 4.1** In `expand_or2(('var', '_tmp'), ...)`, what is the expansion? Trace through it carefully: what does `('let', '_tmp', ('var', '_tmp'), ...)` mean — which `_tmp` is the binding, and which is the reference?

> **CTQ 4.2** The `gensym` function generates names like `_or_tmp1`. Why is this guaranteed to be hygienic? What assumption does it rely on?

> **CTQ 4.3** Scheme's `syntax-rules` macros are *automatically* hygienic — the macro system tracks which names were introduced by the macro vs. which came from the call site. What information would our simple system need to track to do this automatically?

---

#### Model 5 — Implementing a Macro Expander for Mini

**Intuition.** The macro expander is a tree-walking pass that runs *before* the interpreter. It visits every node in the AST; when it finds a call whose function name is a registered macro, it invokes that macro's Python function with the raw (unevaluated) AST arguments, gets a new AST back, and then *expands the result again* (because a macro can expand into another macro call). When no macro calls remain, the fully expanded AST is handed to the interpreter. The interpreter never sees any macro names — by the time it runs, all macros have been dissolved into ordinary code.

A complete macro system for Mini needs:
1. A way to *define* macros (as functions from AST → AST)
2. An *expander* that walks the AST and expands macro calls before evaluation
3. A `gensym` for hygiene

```python  liascript
from dataclasses import dataclass, field
from typing import Any, Callable

# Macro registry
_macros: dict[str, Callable] = {}
_gensym_counter = 0

def gensym(prefix='g'):
    global _gensym_counter
    _gensym_counter += 1
    return f'__{prefix}{_gensym_counter}__'

def defmacro(name: str):
    """Decorator to register a macro."""
    def decorator(fn):
        _macros[name] = fn
        return fn
    return decorator

def macroexpand(ast):
    """Expand all macros in ast (post-order: expand leaves first)."""
    match ast:
        case ('call', ('var', name), args) if name in _macros:
            # Expand macro: pass raw AST args, get new AST back
            expanded = _macros[name](*args)
            return macroexpand(expanded)   # expand the result too!
        case tuple():
            return tuple(macroexpand(child) for child in ast)
        case list():
            return [macroexpand(child) for child in ast]
        case _:
            return ast

# Define a 'when' macro: when(cond, body) → if cond then body else nil
@defmacro('when')
def when_macro(cond_ast, body_ast):
    return ('if', cond_ast, body_ast, ('nil',))

# Define 'swap!' macro: swap!(a, b) → hygienic temp-var swap
@defmacro('swap!')
def swap_macro(a_ast, b_ast):
    # Only works for variable names
    assert a_ast[0] == 'var' and b_ast[0] == 'var', "swap! requires variable names"
    a_name = a_ast[1]
    b_name = b_ast[1]
    tmp = gensym('swap')
    return ('seq',
        ('let', tmp, ('var', a_name)),
        ('seq',
            ('assign', a_name, ('var', b_name)),
            ('assign', b_name, ('var', tmp))))

# Define 'unless' macro: unless(cond, body) → if not cond then body else nil
@defmacro('unless')
def unless_macro(cond_ast, body_ast):
    return ('if', ('not', cond_ast), body_ast, ('nil',))

# Test macroexpansion
print("when(x > 0, print(x)) expands to:")
ast1 = ('call', ('var', 'when'), [('gt', ('var', 'x'), ('num', 0)), ('print', ('var', 'x'))])
print(macroexpand(ast1))

print("\nswap!(x, y) expands to:")
ast2 = ('call', ('var', 'swap!'), [('var', 'x'), ('var', 'y')])
print(macroexpand(ast2))
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

**CTQs**

> **CTQ 5.1** `macroexpand` is called *recursively* on the result of a macro expansion (`return macroexpand(expanded)`). Why? What kind of macros require this?

> **CTQ 5.2** The expander here uses a **call-site pattern**: `('call', ('var', name), args)`. What are the limitations of this approach? Could a macro `(if ...)` be handled the same way?

> **CTQ 5.3** Macros are expanded *before* evaluation. What does this mean for error messages? If a macro produces malformed AST, when does the error occur? How does this make debugging harder?

---

#### Multiple Choice

What is the key difference between a macro and a function?

    [( )] Macros are faster than functions at runtime
    [(x)] Macros receive unevaluated syntax and return new syntax; functions receive evaluated values
    [( )] Macros are only available in Lisp-family languages
    [( )] Macros cannot take arguments

---

What is the "hygiene problem" in macro systems?

    [( )] Macros that contain too many nested levels
    [(x)] A macro-introduced variable accidentally captures or is captured by a user variable of the same name
    [( )] Macros that are too slow to expand
    [( )] Using macros to define recursive functions

---

`gensym` generates unique names to achieve hygiene. Which of the following is also needed for full hygiene?

    [( )] A faster garbage collector
    [(x)] Tracking which names were introduced by the macro vs. by the call-site context, to prevent *both* directions of capture
    [( )] Converting all macros to functions
    [( )] Using static scoping instead of dynamic scoping

---

When does macro expansion happen in a typical language implementation?

    [( )] At runtime, when the macro call is first encountered
    [(x)] At compile time / before evaluation, during a pass over the AST
    [( )] During lexing, by transforming token streams
    [( )] Only in interpreted languages, not compiled ones

---

#### Exercises

##### Exercise 1 — `and2` and `or2` Macros (15 min)

Implement *hygienic* `and2(a, b)` and `or2(a, b)` macros that short-circuit:
- `and2(a, b)` → evaluate `a`; if falsy, return it; otherwise return `b`
- `or2(a, b)` → evaluate `a`; if truthy, return it; otherwise return `b`

Test that `and2(false, side_effect())` does NOT evaluate `side_effect()` (demonstrate with a print in the side effect).

##### Exercise 2 — `let*` Macro (20 min)

In Scheme, `let*` allows sequential bindings where later bindings can use earlier ones:

```scheme
(let* ((x 1) (y (+ x 1)) (z (* y 2))) z)   ; → 4
```

Implement `let_star([('x', e1), ('y', e2), ...], body_ast)` as a macro that expands to nested `let`:

```
let x = e1 in (let y = e2 in (... body))
```

##### Exercise 3 — `define-syntax` Style Pattern Matching (25 min)

Implement a `syntax_rules` function that lets you define macros via patterns:

```python  liascript
cond_macro = syntax_rules('cond', [
    ('(cond)', lambda: ('nil',)),
    ('(cond (else e))', lambda e: e),
    ('(cond (test expr) . rest)', 
     lambda test, expr, rest: ('if', test, expr, ('call', ('var', 'cond'), rest)))
])
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

Test it on: `(cond ((x > 0) (print "pos")) (else (print "non-pos")))`.

##### Exercise 4 — Macro Expansion in Mini (30 min, harder)

Integrate the macro expander into your Mini interpreter pipeline:

1. Add a `MacroDef` AST node: `MacroDef(name: str, params: list[str], body: Expr)`
2. In the macro expander, handle `MacroDef` by registering the macro (evaluate the body as AST → AST function)
3. Write a Mini program that defines `unless` and `swap!` using the macro system
4. Demonstrate that the expanded code evaluates correctly

---

#### Reflection

*(Write your answers individually, then discuss with your group.)*

1. Languages like C, C++, and Rust have macro systems. Haskell and OCaml do NOT have true macros (they have Template Haskell / PPX, which are cumbersome). Is this a good tradeoff? What do you lose by not having macros?

2. Lisp programmers often say "Lisp macros let you extend the language." Give a concrete example of a language feature that would be impossible to add as a library function, but easy to add as a macro.

3. The final project has a "macros and hygienic quoting" extension option. How would you design the syntax for macro definitions in Mini? Write a sample Mini program that uses a macro.

---

#### Further Reading

- **"On Lisp"** — Paul Graham (free at https://paulgraham.com/onlisp.html): the classic book on Lisp macros
- **Scheme `syntax-rules`** — R7RS Section 4.3: https://r7rs.org/
- **Rust procedural macros** — The Rust Reference: https://doc.rust-lang.org/reference/procedural-macros.html
- **"Macros that Work Together"** — Flatt et al. (2012): how Racket achieves full hygienic macros
- **"Hygienic Macro Expansion"** — Kohlbecker et al. (1986): original hygiene paper
- **Julia macros** — https://docs.julialang.org/en/v1/manual/metaprogramming/: modern example of AST macros in a scientific language

## Going Deeper: The Expression Problem

Every large software system eventually hits a wall where adding a new feature requires editing dozens of existing files. The Expression Problem names this wall precisely and asks whether any language can tear it down. Think of it like a spreadsheet: OOP lets you add rows easily but adding columns is painful, while functional programming flips that — and the goal is a design where both are free. Understanding this tension explains why Haskell typeclasses, Rust traits, and Go interfaces exist and why they are shaped the way they are.

#### Learning Goals

By the end of this activity, you will be able to:

- State the Expression Problem precisely and explain why neither OOP nor functional pattern matching solves both dimensions simultaneously
- Demonstrate the OOP extensibility axis (easy new types, hard new operations) and the functional extensibility axis (easy new operations, hard new types) with concrete code examples
- Implement a dispatch-table solution to the Expression Problem in Python and explain how it achieves independent extensibility in both dimensions
- Connect the dispatch-based solution to Haskell typeclasses, Rust traits, and Go interfaces as language-level mechanisms for the same pattern
- Evaluate a given language feature or design choice by identifying which dimension of the Expression Problem it prioritizes

> **Before You Begin:** This activity assumes you can:
> - Write Python classes with inheritance and override methods on subclasses
> - Read and write basic Python `match`/`case` pattern matching (Python 3.10+)
> - Explain what a decorator (`@something`) does in Python at a high level
>
> If any of these feel shaky, review them first.

The **Expression Problem** is one of the most important design tensions in programming language theory. Coined by Philip Wadler in a 1998 mailing list post, it asks a deceptively simple question:

> *Can you add new data types AND new operations to a program without modifying any existing code?*

Every language and paradigm takes a position on this question. Object-oriented languages make it easy to add new types (just write a new class) but hard to add new operations (you must edit every existing class). Functional languages with pattern matching make it easy to add new operations (just write a new function) but hard to add new types (you must update every existing match expression). Understanding why this tension exists — and how different languages navigate it — reveals deep truths about the tradeoffs baked into language design itself.

In this activity you will move from the concrete problem through several attempted solutions, arriving at a principled approach using dispatch mechanisms that directly mirror Haskell typeclasses, Rust traits, and Go interfaces.

---

#### Directions and Group Roles

**This is a POGIL activity.** Work in groups of three or four. Assign the following roles before you begin, and rotate roles at each new Model.

| Role | Responsibility |
|------|---------------|
| **Manager** | Keeps the group on task and on time; escalates to the instructor when the group is stuck for more than two minutes |
| **Recorder** | Writes down the group's agreed answers; ensures responses are complete and legible |
| **Presenter** | Speaks for the group during class discussion; explains the group's reasoning, not just the answer |
| **Reflector** | Monitors group process; notes what strategies are working; leads the end-of-model reflection check-in |

> **Ground rule:** No one moves on until every member can explain the answer independently. If one person is confused, the group is not done.

---

#### Model 1 — The Problem: Two Dimensions of Extension

Picture a menu at a restaurant: OOP is like a menu where adding a new dish (new type) only requires writing one new recipe, but if the owner wants to add a nutritional-info column for every dish (new operation), they must revisit every recipe ever written. This model makes that asymmetry concrete in code you can run and modify.

We start with a shape hierarchy — the classic OOP teaching example. Read the code carefully. There are two kinds of things you might want to add to this system: (1) new shapes (data types) and (2) new operations over shapes. Pay attention to which is easy and which is hard.

```python  liascript
class Shape:
    pass

class Circle(Shape):
    def __init__(self, r): self.r = r
    def area(self): return 3.14159 * self.r * self.r
    def perimeter(self): return 2 * 3.14159 * self.r

class Rectangle(Shape):
    def __init__(self, w, h): self.w = w; self.h = h
    def area(self): return self.w * self.h
    def perimeter(self): return 2 * (self.w + self.h)

# EASY: add a new shape — just add a new class
class Triangle(Shape):
    def __init__(self, a, b, c): self.a=a; self.b=b; self.c=c
    def area(self):
        s = (self.a+self.b+self.c)/2
        return (s*(s-self.a)*(s-self.b)*(s-self.c))**0.5
    def perimeter(self): return self.a + self.b + self.c

# HARD: add a new operation (to_svg) — must touch EVERY class!
# We'd have to go back and add to_svg to Circle, Rectangle, AND Triangle.
# In a library with 20 shapes, this is impossible without modifying the library.

shapes = [Circle(5), Rectangle(3, 4), Triangle(3, 4, 5)]
for s in shapes:
    print(f"area={s.area():.2f}, perimeter={s.perimeter():.2f}")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

> **Watch out!** The constraint "without modifying existing code" is the whole point. It is easy to dismiss the problem by saying "just edit the class" — but that is exactly what the Expression Problem forbids. Imagine the class lives in a library you installed via `pip` and cannot change.

Notice that `Triangle` required zero changes to `Circle` or `Rectangle`. We simply wrote a new class. But imagine you now need to generate SVG output for every shape. You would have to open up `Circle`, `Rectangle`, and `Triangle` — and every other shape that existed before you arrived — and add a `to_svg` method to each. If this code lives in a library you do not own, that is simply impossible without forking.

This is the **OOP extensibility asymmetry**: new types are cheap; new operations are expensive.

**Critical Thinking Questions**

> **CTQ 1.1** Without running the code, predict what `Circle(5).area()` returns. Now predict what happens if you instantiate `Shape()` directly and call `.area()` on it. What does Python do? What would Java or Haskell do in the equivalent situation?

> **CTQ 1.2** Suppose the `Shape` library is published on PyPI and you are a user, not the author. You need to add a `to_bounding_box()` operation. What are your options? List at least three approaches and describe the tradeoffs of each.

> **CTQ 1.3** The problem statement says "without modifying existing code." Why does this constraint matter in practice? Name a real-world situation where you cannot freely modify existing code (hint: think about libraries, APIs, or large team codebases).

> **CTQ 1.4** Fill in the table below with "Easy" or "Hard" based on what you observed in this model:

| | Add new Shape type | Add new operation |
|---|---|---|
| OOP (methods on classes) | ? | ? |

---

#### Model 2 — Functional Style: Easy to Add Operations, Hard to Add Types

Flip the restaurant analogy: functional programming is like a spreadsheet where each column (operation) is a formula that covers all rows — adding a new formula is trivial, but adding a new row (type) forces you to update every formula. The `match` expression in this model is that spreadsheet formula, and you will feel the pain of extending it when a new shape arrives.

The functional approach represents each shape as a plain data value and writes operations as standalone functions using pattern matching. This flips the asymmetry exactly: adding a new operation is trivial, but adding a new type requires touching every function.

Python 3.10 introduced structural pattern matching (`match`/`case`), which enables an approximation of the algebraic data type style found in Haskell, Rust, and OCaml.

```python  liascript
from dataclasses import dataclass

@dataclass
class Circle:
    r: float

@dataclass
class Rectangle:
    w: float
    h: float

# EASY: add a new operation — just write a new function
def area(shape):
    match shape:
        case Circle(r=r): return 3.14159 * r * r
        case Rectangle(w=w, h=h): return w * h

def perimeter(shape):
    match shape:
        case Circle(r=r): return 2 * 3.14159 * r
        case Rectangle(w=w, h=h): return 2 * (w + h)

def to_svg(shape):
    match shape:
        case Circle(r=r): return f'<circle r="{r}"/>'
        case Rectangle(w=w, h=h): return f'<rect width="{w}" height="{h}"/>'

# HARD: add a new type (Triangle) — must touch area(), perimeter(), to_svg()!
# Every match expression needs a new case.

shapes = [Circle(5), Rectangle(3, 4)]
for s in shapes:
    print(f"area={area(s):.2f}, svg={to_svg(s)}")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

Adding `to_svg` required writing exactly one new function. Compare that to Model 1, where adding `to_svg` would have required modifying three existing classes. But now try adding a `Triangle` type. You must update `area`, `perimeter`, and `to_svg` — and every other operation that has ever been written over shapes. In a library with 20 operations, all three cases must be added everywhere.

> **Watch out!** Python's `match`/`case` does not exhaustiveness-check at compile time. If you forget a case for a new type, Python silently returns `None` rather than raising an error at the point where the match was incomplete. Haskell and Rust would catch this at compile time — a significant safety difference.

This is the **functional extensibility asymmetry**: new operations are cheap; new types are expensive.

**Critical Thinking Questions**

> **CTQ 2.1** Add a `Triangle` dataclass with fields `a`, `b`, `c` (side lengths) and add matching cases for `area`, `perimeter`, and `to_svg`. How many lines did you have to add? How many existing lines did you have to modify? Compare this to adding a new class in Model 1.

> **CTQ 2.2** What happens in Python if you call `area(Triangle(3, 4, 5))` before adding the `case Triangle(...)` arm? What would Haskell or Rust do with an incomplete match at compile time?

> **CTQ 2.3** Update the table from CTQ 1.4 with the functional row:

| | Add new Shape type | Add new operation |
|---|---|---|
| OOP (methods on classes) | Easy | Hard |
| Functional (match functions) | ? | ? |

> **CTQ 2.4** In one sentence, state the Expression Problem using the vocabulary of the two rows in your table. What would a "perfect" solution look like?

---

#### Model 3 — The Visitor Pattern: OOP's Attempt to Add Operations

Think of the Visitor as a hotel concierge: instead of each guest (shape) knowing how to fulfill every request, guests simply tell the concierge "I am a Circle" and the concierge looks up the right handler. Adding a new service (operation) means training a new concierge — no guest needs to change. But adding a new type of guest still requires updating the concierge's training manual (the abstract `ShapeVisitor` interface).

The Gang of Four **Visitor pattern** is OOP's classical workaround for the hard-to-add-operations problem. The idea: separate the operation from the data by encoding each operation as a "Visitor" object. Each shape accepts a visitor and dispatches to the appropriate method. New operations become new Visitor classes — no modification of existing shape classes required.

Read the structure carefully before running the code. The `accept` method on each shape class is the key: it calls back into the visitor, completing a two-step dispatch known as **double dispatch**.

```python  liascript
from abc import ABC, abstractmethod

class ShapeVisitor(ABC):
    @abstractmethod
    def visit_circle(self, c): pass
    @abstractmethod
    def visit_rectangle(self, r): pass

class Shape(ABC):
    @abstractmethod
    def accept(self, visitor): pass

class Circle(Shape):
    def __init__(self, r): self.r = r
    def accept(self, v): return v.visit_circle(self)

class Rectangle(Shape):
    def __init__(self, w, h): self.w = w; self.h = h
    def accept(self, v): return v.visit_rectangle(self)

class AreaVisitor(ShapeVisitor):
    def visit_circle(self, c): return 3.14159 * c.r * c.r
    def visit_rectangle(self, r): return r.w * r.h

class SVGVisitor(ShapeVisitor):
    def visit_circle(self, c): return f'<circle r="{c.r}"/>'
    def visit_rectangle(self, r): return f'<rect width="{r.w}" height="{r.h}"/>'

# Adding a new operation = new Visitor class (no modification!)
# Adding a new type = must add to ShapeVisitor interface AND all existing visitors

shapes = [Circle(5), Rectangle(3, 4)]
area = AreaVisitor()
svg = SVGVisitor()
for s in shapes:
    print(f"area={s.accept(area):.2f}, svg={s.accept(svg)}")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

> **Watch out!** The Visitor pattern requires every shape class to have an `accept` method baked in from the start. This is a design-time commitment — you cannot retrofit the Visitor pattern onto a library of shapes that were written without `accept`. That up-front coupling is the hidden cost of the pattern.

Adding `SVGVisitor` required no changes to `Circle`, `Rectangle`, `Shape`, or `AreaVisitor`. That is progress — we have solved the "hard to add operations" problem from Model 1. But the cost is visible: `ShapeVisitor` acts as a registry of all known types. Adding a new type (`Triangle`) requires: (1) adding `visit_triangle` to `ShapeVisitor`, (2) implementing it in every existing visitor, and (3) adding `accept` to `Triangle`. The Visitor pattern solves one dimension at the cost of making the other dimension even more entangled.

**Critical Thinking Questions**

> **CTQ 3.1** Trace the execution of `s.accept(area)` where `s` is a `Circle`. Write out each method call in order, naming the object and method. The term "double dispatch" refers to the two dynamic dispatch steps involved — identify them.

> **CTQ 3.2** What is the role of `ShapeVisitor` as an abstract base class? What happens if you add a `Triangle` class that extends `Shape` with an `accept` method, but do NOT add `visit_triangle` to `ShapeVisitor`? Does Python give you an error immediately, or only later?

> **CTQ 3.3** Update the table from CTQ 2.3 with the Visitor row:

| | Add new Shape type | Add new operation |
|---|---|---|
| OOP (methods on classes) | Easy | Hard |
| Functional (match functions) | Hard | Easy |
| Visitor pattern | ? | ? |

> **CTQ 3.4** Many compiler and IDE frameworks (ANTLR, Eclipse JDT, Roslyn) use the Visitor pattern on their AST classes. Given what you now know, what does this tell you about the design tradeoffs those frameworks made? What extension point did they decide to keep open?

---

#### Model 4 — The Open/Closed Solution: Extension Objects and Typeclasses

`singledispatch` works like a lookup table indexed by type: when you call `area(some_shape)`, Python looks up the runtime type in the dispatch table and calls the registered function. You can add new rows to this table from anywhere — a different file, a different package — without touching the table's original definition. This is the same mechanism Haskell uses with `instance` declarations and Rust uses with `impl Trait for Type`.

The holy grail is a mechanism where you can add both new types and new operations without modifying existing code. Python's `functools.singledispatch` provides this. It lets you register implementations of a function for specific types — after the fact, from anywhere. This is structurally equivalent to **Haskell typeclasses** and **Rust trait implementations**.

The key insight: the function and the implementations are decoupled. The function is a generic entry point; the implementations are registered associations between a type and a behavior. New types just register new implementations. New operations are new `singledispatch` functions, also with registered implementations.

```python  liascript
from functools import singledispatch

@singledispatch
def area(shape):
    raise NotImplementedError(f"No area for {type(shape)}")

@singledispatch
def to_svg(shape):
    raise NotImplementedError(f"No SVG for {type(shape)}")

# Define types
class Circle:
    def __init__(self, r): self.r = r

class Rectangle:
    def __init__(self, w, h): self.w = w; self.h = h

# Register implementations
@area.register(Circle)
def _(c): return 3.14159 * c.r * c.r

@area.register(Rectangle)
def _(r): return r.w * r.h

@to_svg.register(Circle)
def _(c): return f'<circle r="{c.r}"/>'

@to_svg.register(Rectangle)
def _(r): return f'<rect width="{r.w}" height="{r.h}"/>'

# Add a new type AFTER the fact — no modification!
class Triangle:
    def __init__(self, a, b, c): self.a=a; self.b=b; self.c=c

@area.register(Triangle)
def _(t):
    s = (t.a+t.b+t.c)/2
    return (s*(s-t.a)*(s-t.b)*(s-t.c))**0.5

@to_svg.register(Triangle)
def _(t): return f'<!-- triangle {t.a},{t.b},{t.c} -->'

shapes = [Circle(5), Rectangle(3,4), Triangle(3,4,5)]
for s in shapes:
    print(f"area={area(s):.2f}, svg={to_svg(s)}")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

> **Watch out!** `singledispatch` dispatches on the type of the **first argument only**. If you have a function that needs to branch on the types of two arguments simultaneously, `singledispatch` will not help directly — you need a different mechanism (such as multimethods or manual dispatch tables). This is why the Visitor pattern uses double dispatch explicitly.

Notice what did NOT happen: adding `Triangle` did not require opening any existing file. Adding `to_svg` did not require touching any shape class. Each registration is a new, independent declaration. This is the same mechanism Haskell uses with `instance` declarations and Rust uses with `impl Trait for Type` — both allow any module to provide an implementation of any trait for any type.

**Critical Thinking Questions**

> **CTQ 4.1** In Haskell, you define a typeclass with `class Area a where area :: a -> Double` and provide instances with `instance Area Circle where area c = ...`. Map each element of this Haskell syntax onto the corresponding Python construct in Model 4 (`@singledispatch`, `@area.register(Circle)`, etc.).

> **CTQ 4.2** The `singledispatch` approach still has one limitation called the **coherence problem**: what happens if two different modules each register a different `area` implementation for `Circle`? Which one wins? How do Haskell and Rust address this?

> **CTQ 4.3** Add a `perimeter` operation to the system above for all three shapes without modifying any of the existing code. How many new lines did you need? Did you modify any existing line? How does this compare to adding `to_svg` in Model 1?

> **CTQ 4.4** Fill in the final row of the table:

| | Add new Shape type | Add new operation |
|---|---|---|
| OOP (methods on classes) | Easy | Hard |
| Functional (match functions) | Hard | Easy |
| Visitor pattern | Hard | Easy |
| singledispatch / typeclasses | ? | ? |

---

#### Model 5 — Implications for Language Design: The Mini Interpreter

Compiler writers face the Expression Problem in its most acute form: every new language feature is a new AST node type, and every analysis pass is a new operation. Without a principled solution, adding a feature forces you to touch every analysis pass and adding a pass forces you to touch every node type. This model shows how `singledispatch` scales to a realistic interpreter setting where both dimensions grow simultaneously.

The Expression Problem is not just about shapes — it appears in its most important form in **language interpreters and compilers**. An interpreter has two dimensions that grow simultaneously:

- **AST node types**: `Num`, `Add`, `If`, `Lambda`, `App`, `Let`, `Var`, `Seq`, ...
- **Operations on AST**: `eval`, `typecheck`, `pretty_print`, `compile`, `optimize`, ...

Every time you add a language feature, you add a new AST node type. Every time you add an analysis pass, you add a new operation. Without a solution to the Expression Problem, you are constantly modifying existing code.

The code below implements a mini expression interpreter using `singledispatch`, demonstrating how this technique scales to a realistic language-design setting. Observe how adding `Sub` required only new `@register` declarations.

```python  liascript
from functools import singledispatch
from dataclasses import dataclass

@dataclass
class Num:
    value: int

@dataclass
class Add:
    left: object
    right: object

@dataclass
class Mul:
    left: object
    right: object

@singledispatch
def eval_expr(expr, env=None):
    raise ValueError(f"Unknown expr: {expr}")

@singledispatch
def pretty(expr):
    raise ValueError(f"Unknown expr: {expr}")

@eval_expr.register(Num)
def _(e, env=None): return e.value

@eval_expr.register(Add)
def _(e, env=None): return eval_expr(e.left) + eval_expr(e.right)

@eval_expr.register(Mul)
def _(e, env=None): return eval_expr(e.left) * eval_expr(e.right)

@pretty.register(Num)
def _(e): return str(e.value)

@pretty.register(Add)
def _(e): return f"({pretty(e.left)} + {pretty(e.right)})"

@pretty.register(Mul)
def _(e): return f"({pretty(e.left)} * {pretty(e.right)})"

# Test the base system
expr = Add(Mul(Num(2), Num(3)), Num(4))
print(f"Expression: {pretty(expr)}")
print(f"Value: {eval_expr(expr)}")

# Adding a new AST node type (Sub) needs only new @register decorators
@dataclass
class Sub:
    left: object
    right: object

@eval_expr.register(Sub)
def _(e, env=None): return eval_expr(e.left) - eval_expr(e.right)

@pretty.register(Sub)
def _(e): return f"({pretty(e.left)} - {pretty(e.right)})"

expr2 = Sub(Mul(Num(5), Num(3)), Num(7))
print(f"Expression: {pretty(expr2)}")
print(f"Value: {eval_expr(expr2)}")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

The pattern shown here mirrors how real compiler infrastructure is organized. LLVM's IR, GCC's GIMPLE, and JVM bytecode all separate the definition of instruction types from the definition of analysis passes. The `singledispatch` mechanism in Python, Haskell's typeclasses, Rust's traits, and Go's implicit interfaces are all language-level answers to the same design tension.

Each language makes a slightly different tradeoff:

- **Haskell typeclasses** require "orphan instance" rules to preserve coherence — you cannot define an instance for a type you don't own unless you own the typeclass.
- **Rust traits** use the **orphan rule** strictly: either the trait or the type must be defined in your crate.
- **Go interfaces** are implicit — any type satisfying the interface's method set satisfies it, which avoids the registration boilerplate but loses the ability to add operations without methods on the type.
- **Python `singledispatch`** is fully open, trading coherence guarantees for flexibility.

**Critical Thinking Questions**

> **CTQ 5.1** The base interpreter handles `Num`, `Add`, and `Mul`. When `Sub` is added, does `eval_expr(Add(Num(1), Num(2)))` still work? Why does adding a new registration not break existing registrations?

> **CTQ 5.2** Suppose a student adds a `Div` node and registers `eval_expr` for it, but forgets to register `pretty` for it. What happens when `pretty(Div(Num(6), Num(2)))` is called? At what point does the failure occur — at registration time or at call time? How would Rust's type system catch this at compile time?

> **CTQ 5.3** Go interfaces differ from Haskell typeclasses in a crucial way: in Go, a type satisfies an interface implicitly by having the right methods, with no explicit `instance` or `impl` declaration. Does this solve the Expression Problem, or does it fall into one of the original two traps (easy to add types / easy to add operations, but not both)? Justify your answer.

> **CTQ 5.4** Haskell's solution to the Expression Problem uses a technique called **"tagless final"** (Kiselyov, 2009), where the expression type is abstracted over the interpreter itself using a typeclass. Without diving into the full construction, describe in one or two sentences what problem tagless final solves that `singledispatch` does not.

---

#### Multiple Choice

[[MC]] Which statement best describes the Expression Problem?

[(X)] Simultaneously supporting extension in both new types and new operations without modifying existing code
[( )] Ensuring that recursive functions always terminate
[( )] Avoiding runtime type errors when evaluating arithmetic expressions
[( )] The difficulty of adding error handling to expression parsers

---

[[MC]] In the Visitor pattern, adding a new shape type requires:

[( )] Only writing one new Visitor class
[(X)] Adding a method to the Visitor interface AND implementing it in every existing concrete Visitor
[( )] Nothing — the `accept` method dispatches to new types automatically
[( )] Modifying only the abstract Shape base class

---

[[MC]] Python's `functools.singledispatch` most closely resembles which language feature?

[( )] Python's class inheritance and method resolution order
[(X)] Haskell typeclasses or Rust trait implementations
[( )] Python's `try/except` exception handling blocks
[( )] C++'s virtual functions and vtables

---

[[MC]] Which approach makes adding new operations the easiest?

[( )] The OOP approach with methods defined on each class
[(X)] The functional or dispatch approach (singledispatch, typeclasses, or match functions)
[( )] Simple single inheritance without abstract base classes
[( )] All approaches have the same difficulty for new operations

---

#### Exercises

##### Exercise 1 — Extending the singledispatch System (20 min)

Add a `perimeter` operation to Model 4's `singledispatch` system for all three shapes (`Circle`, `Rectangle`, `Triangle`) without modifying any of the code in Model 4. Then add a fourth shape, `Square`, and register `area`, `to_svg`, and `perimeter` for it. Verify that all four shapes work with all three operations.

Requirement: your additions must be written as if they were in a completely separate module — no edits to the original declarations.

##### Exercise 2 — Let Expressions and Variables in the Mini Interpreter (25 min)

Extend Model 5's mini interpreter to support variable bindings. Add two new AST node types:

- `Let(name: str, value_expr, body_expr)` — evaluates `value_expr`, binds the result to `name` in a new environment, and evaluates `body_expr` in that environment
- `Var(name: str)` — looks up `name` in the current environment

Register both `eval_expr` and `pretty` for each new node. The environment should be passed through recursive calls (update the existing `eval_expr` registrations to thread `env` through). Test with:

```
# let x = 3 + 4 in x * x  =>  should print 49
expr = Let("x", Add(Num(3), Num(4)), Mul(Var("x"), Var("x")))
```

##### Exercise 3 — Constant Folding Visitor (30 min, harder)

The **constant folding** optimization replaces expressions whose values are known at compile time with their computed values. For example, `Add(Num(2), Num(3))` simplifies to `Num(5)`, and `Mul(Num(0), anything)` simplifies to `Num(0)`.

Using the `singledispatch` approach from Model 5, add a new `fold(expr)` operation that performs constant folding. Rules:

- `Num(n)` folds to `Num(n)` (already a constant)
- `Add(Num(a), Num(b))` folds to `Num(a + b)`
- `Add(e1, e2)` where either side is not a `Num` folds recursively: `Add(fold(e1), fold(e2))`
- `Mul(Num(0), _)` and `Mul(_, Num(0))` fold to `Num(0)`
- Similarly for `Mul(Num(1), e)` and `Mul(e, Num(1))`
- All other `Mul` cases fold recursively

Test: `Add(Mul(Num(1), Num(3)), Add(Num(2), Num(2)))` should fold to `Num(7)`. Verify with `pretty` before and after folding.

---

#### Reflection

*(Write answers individually first, then discuss with your group.)*

1. In your final project interpreter, which approach did you use or will you use for AST operations: OOP with methods on AST node classes, functional with `match` expressions, the Visitor pattern, or `singledispatch`/registration? What tradeoffs does your choice make — specifically, which dimension of extension (new node types vs. new passes) is easier or harder?

2. TypeScript uses **structural typing** — a type satisfies an interface if it has the right shape (fields and methods), without any explicit declaration. Does this help or hurt with the Expression Problem compared to Java's **nominal typing** (where you must explicitly declare `implements Interface`)? Consider both adding new types and adding new operations.

3. The Expression Problem arises whenever you have a **two-dimensional extension space**. Identify one other domain (not shapes, not interpreters) where the same tension appears. Describe the two dimensions and which approach (OOP, functional, Visitor, or dispatch) would be most natural.

---

#### Further Reading

- Philip Wadler, "The Expression Problem" (1998 mailing list post) — the original formulation; search for "Wadler Expression Problem 1998"
- Oleg Kiselyov, "Typed Tagless Final Interpreters" (2009) — an advanced solution using type classes that fully solves both dimensions: https://okmij.org/ftp/tagless-final/
- Zenger and Odersky, "Independently Extensible Solutions to the Expression Problem" (FOOL 2005) — a survey of solutions in OOP languages
- William Cook, "On Understanding Data Abstraction, Revisited" (OOPSLA 2009) — clarifies the distinction between objects and abstract data types, which underlies the Expression Problem
- Rust Reference: Traits — https://doc.rust-lang.org/reference/items/traits.html — particularly the orphan rule discussion
- Haskell Wiki: Typeclasses — https://wiki.haskell.org/Typeclasses
