<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374-Fall2026/gh-pages/_pages/Activities/liascript-expression-problem.md

import: https://raw.githubusercontent.com/liascript/CodeRunner/master/README.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-CS374-Fall2026@gh-pages/assets/css/main.css
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

# The Expression Problem

Every large software system eventually hits a wall where adding a new feature requires editing dozens of existing files. The Expression Problem names this wall precisely and asks whether any language can tear it down. Think of it like a spreadsheet: OOP lets you add rows easily but adding columns is painful, while functional programming flips that — and the goal is a design where both are free. Understanding this tension explains why Haskell typeclasses, Rust traits, and Go interfaces exist and why they are shaped the way they are.

## Learning Goals

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

## Directions and Group Roles

**This is a POGIL activity.** Work in groups of three or four. Assign the following roles before you begin, and rotate roles at each new Model.

| Role | Responsibility |
|------|---------------|
| **Manager** | Keeps the group on task and on time; escalates to the instructor when the group is stuck for more than two minutes |
| **Recorder** | Writes down the group's agreed answers; ensures responses are complete and legible |
| **Presenter** | Speaks for the group during class discussion; explains the group's reasoning, not just the answer |
| **Reflector** | Monitors group process; notes what strategies are working; leads the end-of-model reflection check-in |

> **Ground rule:** No one moves on until every member can explain the answer independently. If one person is confused, the group is not done.

---

## Model 1 — The Problem: Two Dimensions of Extension

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

## Model 2 — Functional Style: Easy to Add Operations, Hard to Add Types

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

## Model 3 — The Visitor Pattern: OOP's Attempt to Add Operations

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

## Model 4 — The Open/Closed Solution: Extension Objects and Typeclasses

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

## Model 5 — Implications for Language Design: The Mini Interpreter

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

## Multiple Choice

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

## Exercises

### Exercise 1 — Extending the singledispatch System (20 min)

Add a `perimeter` operation to Model 4's `singledispatch` system for all three shapes (`Circle`, `Rectangle`, `Triangle`) without modifying any of the code in Model 4. Then add a fourth shape, `Square`, and register `area`, `to_svg`, and `perimeter` for it. Verify that all four shapes work with all three operations.

Requirement: your additions must be written as if they were in a completely separate module — no edits to the original declarations.

### Exercise 2 — Let Expressions and Variables in the Mini Interpreter (25 min)

Extend Model 5's mini interpreter to support variable bindings. Add two new AST node types:

- `Let(name: str, value_expr, body_expr)` — evaluates `value_expr`, binds the result to `name` in a new environment, and evaluates `body_expr` in that environment
- `Var(name: str)` — looks up `name` in the current environment

Register both `eval_expr` and `pretty` for each new node. The environment should be passed through recursive calls (update the existing `eval_expr` registrations to thread `env` through). Test with:

```
# let x = 3 + 4 in x * x  =>  should print 49
expr = Let("x", Add(Num(3), Num(4)), Mul(Var("x"), Var("x")))
```

### Exercise 3 — Constant Folding Visitor (30 min, harder)

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

## Reflection

*(Write answers individually first, then discuss with your group.)*

1. In your final project interpreter, which approach did you use or will you use for AST operations: OOP with methods on AST node classes, functional with `match` expressions, the Visitor pattern, or `singledispatch`/registration? What tradeoffs does your choice make — specifically, which dimension of extension (new node types vs. new passes) is easier or harder?

2. TypeScript uses **structural typing** — a type satisfies an interface if it has the right shape (fields and methods), without any explicit declaration. Does this help or hurt with the Expression Problem compared to Java's **nominal typing** (where you must explicitly declare `implements Interface`)? Consider both adding new types and adding new operations.

3. The Expression Problem arises whenever you have a **two-dimensional extension space**. Identify one other domain (not shapes, not interpreters) where the same tension appears. Describe the two dimensions and which approach (OOP, functional, Visitor, or dispatch) would be most natural.

---

## Further Reading

- Philip Wadler, "The Expression Problem" (1998 mailing list post) — the original formulation; search for "Wadler Expression Problem 1998"
- Oleg Kiselyov, "Typed Tagless Final Interpreters" (2009) — an advanced solution using type classes that fully solves both dimensions: https://okmij.org/ftp/tagless-final/
- Zenger and Odersky, "Independently Extensible Solutions to the Expression Problem" (FOOL 2005) — a survey of solutions in OOP languages
- William Cook, "On Understanding Data Abstraction, Revisited" (OOPSLA 2009) — clarifies the distinction between objects and abstract data types, which underlies the Expression Problem
- Rust Reference: Traits — https://doc.rust-lang.org/reference/items/traits.html — particularly the orphan rule discussion
- Haskell Wiki: Typeclasses — https://wiki.haskell.org/Typeclasses
