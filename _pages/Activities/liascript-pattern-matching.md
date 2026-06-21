<!--
author:   CS374 Course Staff
email:    
version:  0.0.1
language: en
narrator: US English Female
comment:  Algebraic data types and pattern matching — modeling the world with types.
import:   https://raw.githubusercontent.com/liaScript/mermaid_template/master/README.md
link:     https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.3.0/css/all.min.css
-->

# Algebraic Data Types and Pattern Matching

Pattern matching is like a smart `switch` statement that simultaneously tests the *shape* of a value AND extracts pieces from it in one step — think of a postal sorter that reads the address off the envelope while physically routing the package, never handling the contents without first knowing what kind of parcel it is. This matters because most bugs in large programs come from handling the wrong kind of data at the wrong time; pattern matching plus algebraic data types forces you to confront every possible case at the point where you write the code, not six months later in a production crash. By the end of this activity you will write code that simply cannot reach an unhandled state.

## Learning Goals

By the end of this activity, you will be able to:

- Define algebraic data types (product types and sum types) using Python dataclasses and sealed class hierarchies
- Write pattern-matching code using Python's `match`/`case` syntax to safely deconstruct ADT values exhaustively
- Explain how sum types make illegal states unrepresentable and eliminate a class of runtime `None`/tag-check errors
- Apply ADTs and pattern matching to model a Mini-language AST, writing a recursive evaluator that dispatches on node type

> **"Pattern matching is the most powerful idea you haven't seen yet."**
>
> Today you will discover how types can model *everything* — shapes, trees, expressions, errors, results — and how pattern matching eliminates a whole class of runtime errors by making the impossible unrepresentable.

## Directions and Roles

> **Before You Begin:** This activity assumes you can:
> - Write basic Python classes and use `isinstance()` to branch on type
> - Understand what a `None` return value means and why forgetting to check it causes `AttributeError`/`TypeError` crashes
> - Read simple recursive functions (a function that calls itself on a smaller input)
> If any of these feel shaky, review them first.

Work in groups of 3–4. Rotate roles every 20 minutes.

- **Facilitator**: Keeps discussion on track; ensures everyone contributes.
- **Recorder**: Writes down answers and code that the group agrees on.
- **Reporter**: Presents findings to the class; explains the group's reasoning.
- **Reflector**: Monitors group process; writes the reflection at the end.

---

Before diving into the solution, Model 1 shows the *exact pain point* that algebraic data types cure: a function that sometimes returns a real value and sometimes returns `None`, with no way for the type system to remind callers to handle both possibilities. Run the code and watch it crash — that crash is the motivating problem for everything that follows.

## Model 1 — The Problem with Booleans and Null

In most languages, functions that can fail return either a special sentinel value (`-1`, `None`, `null`, `""`) or raise an exception. Both approaches have problems.

```python  liascript
# A "safe" dictionary lookup — the Python way
def find_user(user_id, db):
    if user_id in db:
        return db[user_id]   # returns a dict
    return None              # caller might forget to check!

users = {"alice": {"age": 30}, "bob": {"age": 25}}

u = find_user("charlie", users)
print(u["age"])   # 💥 TypeError: 'NoneType' object is not subscriptable
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

The problem: `None` *looks like* a real value. The type system doesn't force you to handle the failure case.

> **Watch out!** Python's `None` is assignable to *any* variable, so a dict value, a returned object, and a missing result all share the same type at runtime. This is by design in Python, but it means `u["age"]` compiles (or runs until that line) with no warning — the crash only happens when execution reaches the bad line, often deep in a call stack far from where `None` was returned.

**Critical Thinking Questions (CTQs)**

> **CTQ 1.1** What happens if you call `find_user("alice", users)["age"]`? What if you call `find_user("charlie", users)["age"]`?

> **CTQ 1.2** Can you tell from the function signature `find_user(user_id, db)` that it might return `None`? What documentation or convention would help?

> **CTQ 1.3** List two other common uses of `None` / `null` in Python or Java as a sentinel value. For each one, describe a bug that this pattern has caused in real software.

---

Model 2 introduces the core tool: a **sum type** (tagged union). Instead of returning `None`, we return a value whose *type tag* tells the caller whether an answer exists. The `match` statement then forces explicit handling of each tag, turning a potential runtime crash into a visible structural check at the call site.

## Model 2 — Sum Types: Tagging Variants

A **sum type** (also called a **tagged union**, **variant**, or **discriminated union**) is a type whose values are exactly one of several *tagged* possibilities:

```
Option[A]  =  Some(value: A)  |  Nothing
Result[A]  =  Ok(value: A)    |  Err(message: str)
Shape      =  Circle(radius: float)
           |  Rectangle(width: float, height: float)
           |  Triangle(base: float, height: float)
```

The `|` means "OR" — a Shape is *either* a Circle *or* a Rectangle *or* a Triangle. Each variant carries different data. This is why they're called "sum" types: the set of all Shapes is the *sum* (union) of the sets of Circles, Rectangles, and Triangles.

```python  liascript
from dataclasses import dataclass
from typing import Optional, Union
from math import pi

@dataclass
class Circle:
    radius: float

@dataclass
class Rectangle:
    width: float
    height: float

@dataclass
class Triangle:
    base: float
    height: float

Shape = Circle | Rectangle | Triangle

def area(shape: Shape) -> float:
    match shape:
        case Circle(radius=r):
            return pi * r * r
        case Rectangle(width=w, height=h):
            return w * h
        case Triangle(base=b, height=h):
            return 0.5 * b * h

shapes = [Circle(5), Rectangle(3, 4), Triangle(6, 8)]
for s in shapes:
    print(f"{s} → area = {area(s):.2f}")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

> **Watch out!** Python's `match` statement does **not** warn you when your cases are non-exhaustive. If you add a new variant (say `Square`) but forget a matching `case Square(...)` arm, Python silently falls through all arms and `area()` returns `None` — no error, no warning. Haskell and Rust treat a non-exhaustive match as a compile-time error. In Python, you must add `case _ : raise NotImplementedError(f"Unknown shape: {shape}")` as the final arm to catch this yourself.

**CTQs**

> **CTQ 2.1** What happens if you add a new variant `Square(side: float)` to `Shape` but forget to update `area()`? Try it! What does Python do? What would a language like Haskell or Rust do?

> **CTQ 2.2** Explain in one sentence why "pattern matching is exhaustive checking." How does this relate to the `None` problem from Model 1?

> **CTQ 2.3** Rewrite `area()` using `if/elif/isinstance()` instead of `match`. Which version is clearer? Which is safer?

---

Model 3 shows how to apply sum types to the exact failure-handling problem from Model 1. An `Option` type has exactly two variants — `Some(value)` when something is there, and `Nothing` when it isn't — so a caller who holds an `Option` is *structurally reminded* to handle both cases before accessing any value inside.

## Model 3 — The Option Type: Making Failure Explicit

```python  liascript
from dataclasses import dataclass
from typing import TypeVar, Generic, Callable

A = TypeVar('A')
B = TypeVar('B')

@dataclass
class Some(Generic[A]):
    value: A

@dataclass  
class Nothing:
    pass

Option = Some | Nothing

def find_user(user_id: str, db: dict) -> Option:
    if user_id in db:
        return Some(db[user_id])
    return Nothing()

def map_option(opt: Option, f: Callable) -> Option:
    """Apply f to the value inside Some, leave Nothing alone."""
    match opt:
        case Some(value=v):
            return Some(f(v))
        case Nothing():
            return Nothing()

def flat_map(opt: Option, f: Callable) -> Option:
    """f returns an Option; flatten the double-wrapping."""
    match opt:
        case Some(value=v):
            return f(v)
        case Nothing():
            return Nothing()

def get_or_default(opt: Option, default):
    match opt:
        case Some(value=v): return v
        case Nothing():     return default

# Usage
users = {"alice": {"age": 30, "city": "Philadelphia"}}
result = find_user("alice", users)
age    = map_option(result, lambda u: u["age"])
print(f"Alice's age: {get_or_default(age, 'unknown')}")

result2 = find_user("charlie", users)
age2    = map_option(result2, lambda u: u["age"])
print(f"Charlie's age: {get_or_default(age2, 'unknown')}")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

**CTQs**

> **CTQ 3.1** Why does `map_option` return `Option` rather than `Some`? What would go wrong if it returned `Some` directly?

> **CTQ 3.2** Compare `map_option` (value→value) with `flat_map` (value→Option). When would you use each?

> **CTQ 3.3** Chain: look up a user, then look up their city in a `cities` dict, then look up the zip code of that city. Write this chain using `flat_map` without any `if` statements or `None` checks.

---

Model 4 flips to the other half of algebraic data types: **product types**, which bundle *all* their fields together (like a struct). What makes this interesting is that pattern matching can reach *inside* nested product types in one `case` arm — you can simultaneously check the outer shape and destructure inner fields, including guarding on computed conditions.

## Model 4 — Product Types: Bundling Data

A **product type** bundles *all* of several fields — it's the familiar "struct" or "record". The set of values is the *product* of the component sets (i.e., every combination exists).

```python  liascript
from dataclasses import dataclass

@dataclass(frozen=True)
class Point:
    x: float
    y: float

@dataclass(frozen=True)
class Line:
    start: Point
    end: Point

def length(line: Line) -> float:
    dx = line.end.x - line.start.x
    dy = line.end.y - line.start.y
    return (dx**2 + dy**2) ** 0.5

# Pattern matching on nested structures!
def describe(line: Line) -> str:
    match line:
        case Line(start=Point(x=0, y=0), end=Point(x=x2, y=y2)):
            return f"Line from origin to ({x2}, {y2})"
        case Line(start=Point(x=x1, y=y1), end=Point(x=x2, y=y2)) if x1 == x2:
            return f"Vertical line at x={x1}"
        case Line(start=Point(x=x1, y=y1), end=Point(x=x2, y=y2)) if y1 == y2:
            return f"Horizontal line at y={y1}"
        # Note: guard clauses (the `if` after a case) are evaluated left-to-right,
        # and only after the structural pattern succeeds.
        case _:
            return f"Diagonal line, length={length(line):.2f}"

lines = [
    Line(Point(0, 0), Point(3, 4)),
    Line(Point(2, 1), Point(2, 7)),
    Line(Point(1, 3), Point(9, 3)),
    Line(Point(1, 1), Point(4, 5)),
]
for l in lines:
    print(describe(l))
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

 > **Watch out!** Guard clauses (`if x1 == x2` after the pattern) are evaluated **in order, top to bottom** — Python tries the first arm whose pattern structurally matches, then checks its guard. If the guard fails, Python moves on to the *next arm*, it does **not** re-try the same arm. This means arm order matters: a `case _:` wildcard placed before a guarded arm will swallow all remaining cases.

**CTQs**

> **CTQ 4.1** What does "nested pattern matching" mean? Give a one-sentence description of what `case Line(start=Point(x=0, y=0), ...)` does.

> **CTQ 4.2** The `case _:` at the end is the "wildcard" or "default" case. What happens if you remove it? What does Python do? Why is this different from Haskell or Rust?

> **CTQ 4.3** Why are product types called "product" types? If `Point` has `x ∈ ℝ` and `y ∈ ℝ`, how many distinct `Point` values are there?

---

Model 5 combines everything: sum types can refer to *themselves*, producing recursive structures like trees. An expression tree is the canonical example — `Add(Mul(Num(2), Num(3)), Num(1))` represents `(2*3)+1`. The evaluator is a single `match` over the four node variants, each of which recursively evaluates its children, and the whole thing terminates because every recursive call is on a *strictly smaller* subtree.

## Model 5 — Recursive Types: Trees and Expressions

The real power of sum types is **recursive definitions** — types that contain themselves:

```python  liascript
from __future__ import annotations
from dataclasses import dataclass

# An expression tree (Mini AST fragment)
@dataclass
class Num:
    value: int

@dataclass
class Add:
    left: Expr
    right: Expr

@dataclass
class Mul:
    left: Expr
    right: Expr

@dataclass
class Neg:
    operand: Expr

Expr = Num | Add | Mul | Neg

def eval_expr(e: Expr) -> int:
    match e:
        case Num(value=n):       return n
        case Add(left=l, right=r): return eval_expr(l) + eval_expr(r)
        case Mul(left=l, right=r): return eval_expr(l) * eval_expr(r)
        case Neg(operand=o):     return -eval_expr(o)

def pretty(e: Expr) -> str:
    match e:
        case Num(value=n):         return str(n)
        case Add(left=l, right=r): return f"({pretty(l)} + {pretty(r)})"
        case Mul(left=l, right=r): return f"({pretty(l)} * {pretty(r)})"
        case Neg(operand=o):       return f"(-{pretty(o)})"

# Build: 2 * (3 + (-4))
expr = Mul(Num(2), Add(Num(3), Neg(Num(4))))
print(f"{pretty(expr)} = {eval_expr(expr)}")

# Symbolic differentiation: d/dx (x * x)
@dataclass
class Var:
    name: str

Expr2 = Num | Var | Add | Mul | Neg  # augmented

def diff(e, var: str) -> Expr:
    """Symbolic differentiation: return d(e)/d(var)."""
    match e:
        case Num(_):               return Num(0)
        case Var(name=n) if n == var: return Num(1)
        case Var(_):               return Num(0)
        case Add(left=l, right=r): return Add(diff(l, var), diff(r, var))
        case Mul(left=l, right=r):
            # Product rule: (f*g)' = f'*g + f*g'
            return Add(Mul(diff(l, var), r), Mul(l, diff(r, var)))
        case Neg(operand=o):       return Neg(diff(o, var))

x_sq = Mul(Var("x"), Var("x"))   # x²
d_x_sq = diff(x_sq, "x")         # should be 2x (before simplification)
print(f"d/dx({pretty(x_sq)}) = {pretty(d_x_sq)}")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

**Step-by-Step Trace: `eval_expr(Mul(Num(2), Add(Num(3), Neg(Num(4)))))`**

This traces evaluation of the expression `2 * (3 + (-4))` built as `Mul(Num(2), Add(Num(3), Neg(Num(4))))`.

```
Call: eval_expr( Mul(Num(2), Add(Num(3), Neg(Num(4)))) )
  ├─ Pattern tried: Num(value=n)          → FAILS  (node is Mul, not Num)
  ├─ Pattern tried: Add(left=l, right=r)  → FAILS  (node is Mul, not Add)
  ├─ Pattern tried: Mul(left=l, right=r)  → MATCHES
  │     Bindings created: l = Num(2),  r = Add(Num(3), Neg(Num(4)))
  │
  │   Recurse left:  eval_expr( Num(2) )
  │     ├─ Pattern: Num(value=n)   → MATCHES
  │     │     Binding: n = 2
  │     └─ Returns: 2
  │
  │   Recurse right: eval_expr( Add(Num(3), Neg(Num(4))) )
  │     ├─ Pattern: Num(value=n)          → FAILS
  │     ├─ Pattern: Add(left=l, right=r)  → MATCHES
  │     │     Bindings: l = Num(3),  r = Neg(Num(4))
  │     │
  │     │   Recurse left:  eval_expr( Num(3) )
  │     │     ├─ Pattern: Num(value=n)  → MATCHES, n = 3
  │     │     └─ Returns: 3
  │     │
  │     │   Recurse right: eval_expr( Neg(Num(4)) )
  │     │     ├─ Pattern: Num(value=n)          → FAILS
  │     │     ├─ Pattern: Add(left=l, right=r)  → FAILS
  │     │     ├─ Pattern: Mul(left=l, right=r)  → FAILS
  │     │     ├─ Pattern: Neg(operand=o)        → MATCHES
  │     │     │     Binding: o = Num(4)
  │     │     │   Recurse: eval_expr( Num(4) )  → n = 4, returns 4
  │     │     └─ Returns: -4
  │     │
  │     └─ Returns: 3 + (-4) = -1
  │
  └─ Returns: 2 * (-1) = -2
```

Key observations from this trace:
- Each `match` arm is tried **in order**; only the *first* matching arm fires.
- Each arm **creates bindings** (`l`, `r`, `n`, `o`) for the sub-expressions it destructures.
- Recursion terminates because every recursive call is on a strictly *smaller* subtree — `Num` is the base case with no children.
- The total work is proportional to the *number of nodes* in the tree.

**CTQs**

> **CTQ 5.1** The derivative of `x²` by the product rule is `x*1 + 1*x` (before simplification). Is `pretty(d_x_sq)` what you expected? What simplification step is missing?

> **CTQ 5.2** Why does `Expr` have to be declared with `from __future__ import annotations`? What happens without it?

> **CTQ 5.3** The `diff` function is an example of a "structural recursion." What invariant guarantees that it terminates?

---

Model 6 builds on `Option` to add *error messages*: a `Result` type is either `Ok(value)` (success) or `Err(message)` (failure with an explanation). The key insight is that you can chain multiple fallible operations into a pipeline — `bind_result` acts as the connector — and errors automatically short-circuit the rest of the chain without any `if` checks or `try/except` blocks.

## Model 6 — Result Types: Railway-Oriented Programming

```python  liascript
from dataclasses import dataclass
from typing import TypeVar, Generic, Callable

A = TypeVar('A')

@dataclass
class Ok(Generic[A]):
    value: A

@dataclass
class Err:
    message: str

Result = Ok | Err

def safe_div(a: float, b: float) -> Result:
    if b == 0:
        return Err("Division by zero")
    return Ok(a / b)

def safe_sqrt(x: float) -> Result:
    if x < 0:
        return Err(f"Square root of negative: {x}")
    return Ok(x ** 0.5)

def bind_result(result: Result, f: Callable) -> Result:
    """Chain operations: if Ok, apply f; if Err, propagate the error."""
    match result:
        case Ok(value=v): return f(v)
        case Err(_):      return result

# Pipeline: compute sqrt(100 / x)
def pipeline(x):
    return bind_result(
        safe_div(100, x),
        lambda q: safe_sqrt(q)
    )

for x in [4, -1, 0, 25]:
    result = pipeline(x)
    match result:
        case Ok(value=v): print(f"√(100/{x}) = {v:.4f}")
        case Err(message=msg): print(f"Error for x={x}: {msg}")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

**CTQs**

> **CTQ 6.1** This pattern — chaining operations that might fail, propagating errors automatically — is called "railway-oriented programming" or the "Error monad." How is `bind_result` here similar to `flat_map` from Model 3?

> **CTQ 6.2** Compare this style to Python's `try/except` approach. What are the tradeoffs? When would you prefer each?

> **CTQ 6.3** Rust uses `Result<T, E>` and the `?` operator for this pattern. The `?` operator desugars to something like `bind_result`. Look up how it works and explain the desugaring in one paragraph.

---

## Multiple Choice

Which of the following correctly describes a sum type?

    [( )] A type formed by combining all fields of two types (like a struct with merged fields)
    [(x)] A type whose values are one of several tagged alternatives — like `Some(value)` or `Nothing`
    [( )] A type that stores a running total
    [( )] A type that inherits from multiple parent classes

---

In Python 3.10+'s `match` statement, what does `case _:` mean?

    [( )] Match only `None` values
    [( )] Match only the literal string `"_"`
    [(x)] Match any value; acts as a default / catch-all case
    [( )] Raise a `ValueError` if reached

---

Consider: `@dataclass class Pair: fst: int; snd: bool`. How many distinct `Pair` values are there (mathematically)?

    [( )] Infinite (ints are infinite)
    [(x)] `|int| × |bool|` = infinitely many int values × 2 bool values (still infinite, but the structure is a product)
    [( )] 2 (one per field)
    [( )] Undefined — Python dicts have no size

---

## Exercises

### Exercise 1 — JSON Value Type (20 min)

JSON values can be: `null`, a boolean, a number, a string, an array (list of JSON values), or an object (dict mapping strings to JSON values). Model this as a recursive sum type in Python and write:

- `JsonVal` type alias with 6 variants
- `json_to_python(val: JsonVal)` that converts to native Python types
- `json_size(val: JsonVal) -> int` that returns the total number of scalar leaves

Test it on: `{"name": "Alice", "scores": [95, 87, 92], "active": true}`

### Exercise 2 — Mini AST Extensions (20 min)

Extend the `Expr` type from Model 5 to add:
- `Let(name: str, value: Expr, body: Expr)` — let binding
- `Var(name: str)` — variable reference (already there)
- `IfExpr(cond: Expr, then_: Expr, else_: Expr)` — if-expression

Update `eval_expr` to handle these (pass an environment dict for variables).

Test: evaluate `let x = 5 in if x > 3 then x * 2 else 0`.

### Exercise 3 — Type Checker with ADTs (25 min)

Write a `type_check(e: Expr, env: dict) -> str` function that returns `"Int"`, `"Bool"`, or raises `TypeError`:

- `Num` → `"Int"`
- `Add`, `Mul`, `Neg` → require both sides `"Int"`, return `"Int"`
- `IfExpr` → require condition `"Bool"`, require branches same type, return that type
- `Var` → look up in env

Test both valid and invalid expressions (e.g., `1 + true` should raise `TypeError`).

### Exercise 4 — Pattern Matching in Mini (30 min, harder)

Design a syntax extension for Mini that supports pattern matching. Write:

1. New AST nodes: `MatchExpr(scrutinee: Expr, arms: list[MatchArm])` and `MatchArm(pattern: Pattern, body: Expr)` with `Pattern = WildPat | LitPat(value) | VarPat(name) | ConstructorPat(name, sub_patterns)`
2. An evaluator case for `MatchExpr` that tries each arm in order, binding variables
3. Two test cases: matching on integers, matching on a `Shape` constructor

---

## Reflection

*(Write your answers individually, then discuss with your group.)*

1. Before today, how did you handle "a function that might fail" in Python? How does `Option`/`Result` change your approach?

2. Pattern matching checks all cases — in what sense is this "exhaustive"? Python's `match` is not exhaustive by default; Haskell and Rust give warnings/errors. What are the implications for large codebases?

3. How does this connect to the final project? Which extension option (from `asmt-final-project.md`) does ADT pattern matching map to? What would you need to add to Mini to support it?

---

## Further Reading

- **Python 3.10 structural pattern matching** — PEP 634: https://peps.python.org/pep-0634/
- **"Why Functional Programming Matters"** — John Hughes: https://www.cs.kent.ac.uk/people/staff/dat/miranda/whyfp90.pdf
- **Rust enums and pattern matching** — The Rust Book Ch. 6: https://doc.rust-lang.org/book/ch06-00-enums.html
- **Haskell algebraic data types** — Learn You a Haskell Ch. 8
- **"Making Illegal States Unrepresentable"** — Scott Wlaschin: https://fsharpforfunandprofit.com/posts/designing-with-types-making-illegal-states-unrepresentable/
- **TAPL Ch. 11** — Simple Extensions (pairs, sums, variants) — Pierce
