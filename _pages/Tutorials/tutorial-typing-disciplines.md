---
layout: tutorial
permalink: /Tutorials/TypingDisciplines
title: "CS374: Typing Disciplines: Strong vs. Weak, Static vs. Dynamic, and Gradual Typing"

info:
  coursenum: CS374
  goals:
    - To distinguish the static/dynamic axis (when types are checked) from the strong/weak axis (how strictly types are enforced)
    - To place real languages in the strong/weak by static/dynamic quadrant with concrete examples
    - To explain gradual typing and why mypy and TypeScript are unsound by design
    - To connect these disciplines to your interpreter's dynamic typing and the Hindley-Milner type-checking direction

readings:
  - rtitle: "mypy Documentation"
    rlink: "https://mypy.readthedocs.io/"
  - rtitle: "TypeScript Playground (try the examples live)"
    rlink: "https://www.typescriptlang.org/play"
  - rtitle: "Siek and Taha, Gradual Typing for Functional Languages (the founding paper)"
    rlink: "https://scholar.google.com/scholar?q=Gradual+Typing+for+Functional+Languages+Siek+Taha"

tags:
  - types
  - static-typing
  - dynamic-typing
  - gradual-typing
  - languages
---

# Typing Disciplines: Strong vs. Weak, Static vs. Dynamic, and Gradual Typing

This is the core companion for the **Type Systems** unit. It pins down two axes that are constantly confused, places real languages on them, and then looks at **gradual typing**: the discipline behind mypy and TypeScript that lets a single program be part-checked and part-unchecked. It connects directly to the two type stories in your own pipeline: the **dynamic** typing your Interpreter enforces at runtime, and the **static** Hindley-Milner checker offered as a direction of that assignment.

---

## Section 1: Two independent axes

People say "strongly typed" to mean many things. Untangle it into two *independent* questions:

- **Static vs. dynamic: *when* are types checked?**
  - **Static:** before the program runs, by a type checker (C, Java, Haskell, Rust, TypeScript).
  - **Dynamic:** as the program runs, when an operation is attempted (Python, Ruby, JavaScript, your CS374 interpreter).
- **Strong vs. weak: *how strictly* are type rules enforced (how much implicit coercion / reinterpretation of bits is allowed)?**
  - **Strong:** the language refuses nonsensical operations rather than silently coercing (Python raises on `"a" + 1`; Haskell won't compile it).
  - **Weak:** the language silently coerces or reinterprets values (C lets you cast a pointer to an int; JavaScript makes `"a" + 1` the string `"a1"` and `[] + {}` a string).

These axes are independent; a language picks a point on *each*.

---

## Section 2: The quadrant

|                | **Static** (checked before running) | **Dynamic** (checked while running) |
|----------------|--------------------------------------|--------------------------------------|
| **Strong** (little/no silent coercion) | Haskell, Rust, Java (mostly), OCaml | **Python**, Ruby, Scheme, **your CS374 interpreter** |
| **Weak** (silent coercion / bit reinterpretation) | C, C++ (implicit conversions, casts) | JavaScript, PHP, Perl |

Worked contrasts to try:

- `"a" + 1`
  - **Python** (strong/dynamic): `TypeError` at runtime.
  - **Haskell** (strong/static): compile error.
  - **JavaScript** (weak/dynamic): `"a1"`, silent coercion.
  - **C** (weak/static): `'a' + 1` is `98`, a `char` is just a small int.
- Your **CS374 interpreter** deliberately sits in the *strong/dynamic* box: `SEMANTICS.md` says adding a string to a number raises a `LangTypeError` at evaluation time. That is a design choice, and stating it precisely is part of the Interpreter assignment.

> **Common misconception:** "static" does not imply "strong," and "dynamic" does not imply "weak." C is static but weak; Python is dynamic but strong. Keep the axes separate.

---

## Section 3: Where your pipeline lives

You have built (or will build) *both* type stories:

- The **tree-walking interpreter** enforces types **dynamically and strongly**: `"a" + 1` gets as far as evaluation and then raises a positioned `LangTypeError`. The rule lives in `SEMANTICS.md`.
- The **Hindley-Milner type-checking direction** moves the *same* language to **static** checking: it rejects `"a" + 1` *before evaluation ever begins*, the way Haskell and OCaml do, and documents each rule in `TYPES.md`. Notice this direction is also *stricter* than the dynamic version in places (it requires `if`/`while` conditions to be `Bool`, not merely truthy).

Choosing the type-checking direction is literally moving your language one column left in the quadrant.

---

## Section 4: Gradual typing, mypy and TypeScript

What if you want *both*: dynamic flexibility during prototyping and static guarantees where it matters? **Gradual typing** (Siek and Taha, 2006) lets you annotate *some* parts of a program with static types and leave others dynamic, inserting runtime checks at the boundary between the two.

- **mypy** adds gradual static typing to Python. Unannotated code is treated as the dynamic type `Any` and passes silently; annotated code is checked.
- **TypeScript** does the same for JavaScript.

Try the same buggy snippet under both (this is the in-class compare):

```python
# Python + mypy
def add(x: int, y: int) -> int:
    return x + y

add("a", 3)     # mypy: error: Argument 1 to "add" has incompatible type "str"
untyped = []    # inferred Any
untyped.foo()   # mypy: no error - Any silences the check
```

```typescript
// TypeScript
function add(x: number, y: number): number { return x + y; }
add("a", 3);              // tsc: error, string not assignable to number
const x: any = [];        // 'any' opts out
x.foo();                  // tsc: no error - 'any' silences the check
```

**The key insight: gradual type systems are *unsound* by design.** `Any` (mypy) and `any` (TypeScript) are escape hatches that turn checking *off*, so a type-checked program can still fail at runtime. That is a deliberate trade: adoptability and flexibility in exchange for the airtight guarantee a fully static language like Haskell gives you. Contrast this with your HM checker, which has no `Any` escape hatch and so is sound for the fragment it covers.

---

## Section 5: Discussion prompts (POGIL)

1. Place Go, Elixir, and Rust in the quadrant. Where is each, and what evidence (a one-line program) puts it there?
2. TypeScript compiles to JavaScript and then *erases* all types: the runtime has no type information. What class of bug can therefore still occur at runtime despite a clean `tsc`? How does that relate to `Any`?
3. Your interpreter is strong/dynamic. Name one program that runs to completion under it but is *rejected* by the HM type-checking direction. Why is the checker stricter, and is that a bug or a feature?
4. Weakly-typed C lets you reinterpret an `int`'s bits as a `float`. Name one situation where that is genuinely useful and one where it is a catastrophe.

---

## Section 6: Structural vs. Nominal Typing

> **Intuition:** Imagine hiring for a job. A nominal hiring process checks your official job title on your resume: if it doesn't say "Senior Engineer," you don't qualify, even if you can do everything the role requires. A structural hiring process checks your skills: if you can write code, debug systems, and design architecture, you qualify, regardless of what your title says. Nominal typing is the first process; structural typing is the second. Python's duck typing takes this to the extreme: it doesn't even check at hire time, it just tries the work and fails if you can't do it.

The axes in Sections 1-2 concern *when* and *how strictly* types are checked. A separate design question is how the type system decides whether one type is *compatible* with another: two classes that have the same methods but no shared parent: should a function that accepts one also accept the other? Two philosophies govern the answer:

**Nominal typing**: compatibility is determined by *name* (and explicit declaration).

```java
// Java: nominal
interface Drawable { void draw(); }
class Circle implements Drawable { public void draw() { ... } }
class Square { public void draw() { ... } }  // does NOT implement Drawable
// Square cannot be used where Drawable is expected, even though it has draw()
```

**Structural typing**: compatibility is determined by *shape* (do you have the right methods/fields?).

```typescript
// TypeScript: structural
interface Drawable { draw(): void; }
class Circle { draw() { console.log("circle"); } }
class Square { draw() { console.log("square"); } }
// Both Circle and Square satisfy Drawable - no explicit declaration needed
```

**Python's duck typing** is informal structural typing: "if it walks like a duck and quacks like a duck, it's a duck."

```python
class Circle:
    def draw(self):
        print("Drawing circle")

class Square:
    def draw(self):
        print("Drawing square")

def render(shape):
    shape.draw()   # works for anything with a draw() method

render(Circle())   # works
render(Square())   # works
render(42)         # AttributeError at runtime - "int has no attribute 'draw'"
```

### Protocols: structural typing made explicit

Python 3.8 added `Protocol` (PEP 544) so that structural compatibility can be checked *statically* by tools like mypy, and, with `@runtime_checkable`, tested with `isinstance` at runtime. In the example below, none of the shape classes inherits from `Drawable` or from any shared base class; they satisfy the protocol purely by having the right methods.

```python
from typing import Protocol, runtime_checkable
import math

@runtime_checkable
class Drawable(Protocol):
    def draw(self) -> str: ...
    def area(self) -> float: ...

# Neither class inherits from Drawable or from any shared base class.
# They satisfy the protocol purely by having the right methods.

class Circle:
    def __init__(self, r: float) -> None:
        self.r = r

    def draw(self) -> str:
        return f"Circle(r={self.r})"

    def area(self) -> float:
        return math.pi * self.r ** 2

class Square:
    def __init__(self, s: float) -> None:
        self.s = s

    def draw(self) -> str:
        return f"Square(s={self.s})"

    def area(self) -> float:
        return self.s ** 2

class Triangle:
    def __init__(self, base: float, height: float) -> None:
        self.base = base
        self.height = height

    def draw(self) -> str:
        return f"Triangle(base={self.base}, height={self.height})"

    def area(self) -> float:
        return 0.5 * self.base * self.height

# A class that is missing one required method - does NOT satisfy Drawable
class NotDrawable:
    def draw(self) -> str:
        return "I exist"
    # No area() method

def render_all(shapes: list[Drawable]) -> None:
    for shape in shapes:
        print(f"  {shape.draw():<35}  area={shape.area():.4f}")

shapes: list[Drawable] = [Circle(3.0), Square(4.0), Triangle(5.0, 6.0)]

print("=== Structural typing via Protocol ===")
render_all(shapes)

print("\n=== isinstance checks against Protocol ===")
for obj in [Circle(1.0), Square(2.0), NotDrawable(), "a string", 42]:
    result = isinstance(obj, Drawable)
    print(f"  {type(obj).__name__:<15} is Drawable: {result}")

# Nominal equivalent would require:
#   class Circle(Drawable): ...
# Instead, Python checks structure at the isinstance call.
print("\n=== MRO: no Drawable in the chain ===")
print(f"Circle MRO: {[c.__name__ for c in Circle.__mro__]}")
print(f"Square MRO: {[c.__name__ for c in Square.__mro__]}")
```

> **Watch out!** Python's `Protocol` and duck typing look similar but operate at different times. Duck typing is a *runtime* check: Python tries to call the method and raises `AttributeError` if it's missing. A `Protocol` with `@runtime_checkable` allows `isinstance` checks at runtime, but the real power is enabling *static* tools like `mypy` to verify structural compatibility before you run the program at all.

Questions to consider:

1. In nominal typing, what must a class do to be considered a subtype of an interface? In structural typing, what determines subtyping?
2. Duck typing defers type checking to runtime. What is the trade-off compared to structural typing checked at compile time?
3. Go uses structural typing for interfaces: a type satisfies an interface by having the right methods, no `implements` needed. What advantage does this give to library designers? What risk does it introduce?
4. Do `Circle` and `Square` inherit from `Drawable`? Check the MRO output. Yet `isinstance(circle, Drawable)` returns `True`. Explain why.
5. In Java, to achieve the same effect you would write `class Circle implements Drawable`. What does that declaration cost you (coupling, compile-time checking, file organization)? What does Python's structural approach cost you in return?
6. `NotDrawable` has `draw` but not `area`. How does `isinstance(NotDrawable(), Drawable)` respond, and why? What does this tell you about the granularity of Protocol checking?
7. The `...` (Ellipsis) in `def draw(self) -> str: ...` is a body placeholder. How is this different from `pass`? When would you use each?

---

## Section 7: Type Erasure

> **Intuition:** Type erasure is the compiler's answer to a performance problem: if `List<String>` and `List<Integer>` had to be separate classes in memory, you would need an explosion of class definitions. Instead, the Java compiler checks all the generic types at compile time for correctness, then *throws away* the type parameters and produces a single `List` class at the bytecode level. The safety was verified already; no need to repeat it at runtime. C++ takes the opposite approach (monomorphization): it keeps the type information and generates a separate specialized function for each instantiation, trading binary size for the ability to optimize each version independently.

When generic types are compiled, the type parameter often disappears. This is **type erasure**.

### Java: erasure at compile time

```java
// Source code - parameterized
List<String> names = new ArrayList<>();
names.add("Alice");
String s = names.get(0);   // compiler inserts cast

// After erasure - what the JVM actually runs
List names = new ArrayList();
names.add("Alice");
String s = (String) names.get(0);   // explicit cast inserted by compiler
```

At runtime, `List<String>` and `List<Integer>` are the **same** class. You cannot write `names instanceof List<String>`.

### C++: monomorphization (no erasure)

```cpp
template<typename T>
T max_val(T a, T b) { return a > b ? a : b; }

// Compiler generates TWO separate functions:
int    max_val(int a,    int b);     // for int
double max_val(double a, double b);  // for double
```

C++ templates are erased in a different sense: the source template disappears, but each instantiation becomes a fully typed, specialized function.

### Python: no runtime generics at all

```python
from typing import get_type_hints, List

def first(items: List[int]) -> int:
    return items[0]

# What survives to runtime?
print(get_type_hints(first))
# {'items': list[int], 'return': <class 'int'>}
# The annotation IS accessible via get_type_hints, but...

xs: List[int] = [1, 2, 3]
xs.append("oops")   # no runtime error - list doesn't check element types
print(xs)
```

### C++ `std::function` as type erasure

`std::function<void(int)>` stores *any callable* with the right signature: a regular function, a lambda, a functor. The concrete type is erased; only the interface survives. This is the **type erasure design pattern** (distinct from Java's compiler mechanism).

Questions to consider:

1. In Java, why can't you write `new T()` or `T[] arr = new T[10]` inside a generic method? (Hint: what has been erased?)
2. C++ monomorphization means a template instantiated with 10 different types generates 10 copies of the function. What is the trade-off vs Java's erasure approach?
3. Python's `list` at runtime has no knowledge of its type annotation. What practical problem does this cause if you rely on type hints for correctness?
4. The `std::function` type erasure pattern in C++ has a runtime cost (heap allocation, indirect call). Under what circumstances is that cost worth paying?

### Try it: exercises

These exercises span this section and Section 6; run them in any Python 3.10+ environment.

**Exercise 1.** In Python, write a function that deliberately breaks the type hint contract and confirm that Python does NOT raise a runtime error:

```python
def multiply(x: int, y: int) -> int:
    return x * y

# Call it with strings and observe
result = multiply("ha", 3)
print(result)
print(type(result))
```

**Exercise 2.** Demonstrate Python's strong typing by showing three operations that *do* raise `TypeError`, and three that succeed after explicit conversion:

```python
# Three TypeError examples
# Three explicit conversion examples

```

**Exercise 3.** Implement a `Sizeable` Protocol and two classes that satisfy it structurally (without inheriting from it). Verify with `isinstance`:

```python
from typing import Protocol, runtime_checkable

# Your solution here

```

**Exercise 4.** Use `get_type_hints` to inspect the annotations of a function with several parameters, then add a value of the wrong type to a typed list and confirm no runtime error:

```python
from typing import get_type_hints, List

def process(items: List[str], count: int) -> bool:
    return len(items) == count

print(get_type_hints(process))
items: List[str] = ["a", "b"]
items.append(99)   # wrong type - does Python complain?
print(items)
```

**Exercise 5.** Write a `TypedStack` class that enforces element type at runtime (unlike Python's built-in `list`). Use `__init__(self, element_type)` and raise `TypeError` on a bad `push`:

```python
# Your solution here

```

---

## Section 8: Algebraic Data Types: Product and Sum Types

This section is the background for the Team Language Project's **"Pattern Matching over Algebraic Data Types"** extension; the sum-and-product vocabulary below is exactly what that extension asks you to design pattern matching over.

Many real-world values naturally come in distinct shapes: a payment is either a credit card charge *or* a bank transfer *or* a cash payment, never all three at once. **Algebraic data types** let us encode that "one of these shapes" constraint directly in the type, so the type checker can tell us when we have forgotten to handle a case. The word "algebraic" comes from the analogy: combining types with "and" (product) or "or" (sum) mirrors how algebraic expressions combine numbers with multiplication and addition.

> **Watch out! Sum types encode exclusivity in the type system.** A `Union[Circle, Rectangle, Triangle]` does not mean a value can be all three simultaneously; it means it is *exactly one* of them at any given moment. This exclusivity is what makes exhaustive pattern matching possible: if you handle all three cases and the type system guarantees no fourth case exists, the checker can confirm your function is complete. Languages like Rust (`enum`), Haskell (algebraic data types), and Kotlin (`sealed class`) can enforce this at compile time; Python's `Union` relies on the programmer (and a static checker) to maintain the discipline.

**Algebraic data types** (ADTs) come in two flavors:

- A **product type** requires *all* its fields simultaneously; it is the Cartesian product of its component types. `Circle(radius=5.0)` must have a `radius`; there is no partial `Circle`.
- A **sum type** (also called a **variant** or **union**) holds *exactly one* of several alternatives. `Shape` is a `Circle` **or** a `Rectangle` **or** a `Triangle`, never two at once.

Python's `dataclass` gives product types; `Union` gives sum types. The combination is powerful enough to model most domain entities precisely.

```python
from dataclasses import dataclass
from typing import Union
import math

# Product types: every field is required simultaneously
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

# Sum type: a Shape is exactly ONE of the three alternatives
Shape = Union[Circle, Rectangle, Triangle]

def area(shape: Shape) -> float:
    """Pattern-match on the shape's runtime type."""
    if isinstance(shape, Circle):
        return math.pi * shape.radius ** 2
    elif isinstance(shape, Rectangle):
        return shape.width * shape.height
    elif isinstance(shape, Triangle):
        return 0.5 * shape.base * shape.height
    else:
        raise ValueError(f"Unknown shape type: {type(shape).__name__}")

def perimeter(shape: Shape) -> float:
    if isinstance(shape, Circle):
        return 2 * math.pi * shape.radius
    elif isinstance(shape, Rectangle):
        return 2 * (shape.width + shape.height)
    elif isinstance(shape, Triangle):
        # For a right triangle with given base and height
        hyp = math.sqrt(shape.base ** 2 + shape.height ** 2)
        return shape.base + shape.height + hyp
    else:
        raise ValueError(f"Unknown shape type: {type(shape).__name__}")

shapes: list[Shape] = [
    Circle(5.0),
    Rectangle(3.0, 4.0),
    Triangle(6.0, 8.0),
]

print(f"{'Shape':<25} {'Area':>10} {'Perimeter':>12}")
print("-" * 50)
for s in shapes:
    name = type(s).__name__
    print(f"{name:<25} {area(s):>10.4f} {perimeter(s):>12.4f}")
```

Questions to consider:

1. Explain why `Circle` is a **product type**: what does "product" mean here, and what constraint does it place on construction?
2. Explain why `Shape` is a **sum type**: what does "sum" mean here? How many values can a single `Shape` variable contain simultaneously?
3. What happens if you add a new variant (say `@dataclass class Pentagon: sides: float`) to `Shape` but forget to add a branch to `area()`? Trace what Python does. How would a **sealed sum type** in a language like Rust, Haskell, or Kotlin prevent this mistake at compile time?
4. The `else: raise ValueError` branch in `area` is defensive programming against a case the type system claims cannot happen. Should it be there? What does its presence say about the gap between Python's runtime and its static type annotations?
5. Dataclasses generate `__eq__` and `__repr__` automatically. What other "free" operations could a language derive from a product type's structure? (Hint: think serialization, copying, hashing.)

---

## Section 9: Gradual Typing in Depth: Consistency and Blame

Section 4 introduced gradual typing as it appears in mypy and TypeScript. This section goes one level deeper into the theory those tools are built on: the **consistency relation** that replaces type equality, and the **blame calculus** that decides which boundary gets the error when a mixed program fails at runtime.

### A mini type checker built on the consistency relation

Ordinary type equality is strict: `Int` equals `Int` and nothing else. The consistency relation relaxes this by introducing a wildcard type `Any` that is compatible with everything, like a universal adapter that fits any socket. The catch is that this wildcard breaks transitivity, and that gap between what the static checker accepts and what can succeed at runtime is exactly where runtime failures live.

At the heart of gradual typing is a relation called **consistency** (written `~`). It differs from ordinary type equality. Two types are consistent if they could be the same type at runtime: `Int ~ Int` (trivially), `Any ~ Int` (a dynamic value might be an `Int`), `Int ~ Any` (an `Int` is compatible with an unknown type). But `Int ~ Str` is **false**: no runtime value is both an integer and a string.

Formally:

```
t ~ t             (reflexivity)
Any ~ t           (Any is consistent with everything)
t ~ Any           (symmetric)
```

This relation is **not transitive**: `Int ~ Any` and `Any ~ Str` are both true, but `Int ~ Str` is false. That gap is precisely where runtime failures live, and where the blame calculus (below) must assign responsibility.

The code below implements a bi-directional type checker for a small expression language using `consistent` as its compatibility predicate.

```python
from dataclasses import dataclass
from typing import Any, Dict

# Types in our mini language
INT  = "Int"
BOOL = "Bool"
STR  = "Str"
DYN  = "Any"  # the gradual type -- compatible with everything

def consistent(t1, t2):
    """Two types are consistent if one is Any or they are equal."""
    return t1 == DYN or t2 == DYN or t1 == t2

# AST nodes
@dataclass
class Lit:    value: Any; ty: str
@dataclass
class Var:    name: str
@dataclass
class Add:    left: Any; right: Any
@dataclass
class Eq:     left: Any; right: Any
@dataclass
class If:     cond: Any; then_: Any; else_: Any
@dataclass
class Ann:    expr: Any; ty: str   # explicit annotation: (expr : ty)

Env = Dict[str, str]  # variable -> type

def infer(expr, env: Env) -> str:
    if isinstance(expr, Lit):
        return expr.ty
    if isinstance(expr, Var):
        return env.get(expr.name, DYN)   # unannotated vars have type Any
    if isinstance(expr, Ann):
        t = infer(expr.expr, env)
        if not consistent(t, expr.ty):
            raise TypeError(f"Annotation mismatch: got {t}, expected {expr.ty}")
        return expr.ty
    if isinstance(expr, Add):
        t1, t2 = infer(expr.left, env), infer(expr.right, env)
        if not consistent(t1, INT) or not consistent(t2, INT):
            raise TypeError(f"Add requires Int, got {t1} + {t2}")
        return INT
    if isinstance(expr, Eq):
        t1, t2 = infer(expr.left, env), infer(expr.right, env)
        if not consistent(t1, t2):
            raise TypeError(f"Eq: {t1} vs {t2}")
        return BOOL
    if isinstance(expr, If):
        tc = infer(expr.cond, env)
        if not consistent(tc, BOOL):
            raise TypeError(f"If cond must be Bool, got {tc}")
        t1 = infer(expr.then_, env)
        t2 = infer(expr.else_, env)
        if consistent(t1, t2): return t1 if t1 != DYN else t2
        raise TypeError(f"If branches: {t1} vs {t2}")
    raise ValueError(f"Unknown: {expr}")

env = {"x": INT, "name": STR}

# Well-typed programs
print(infer(Add(Var("x"), Lit(1, INT)), env))   # Int
print(infer(Eq(Var("x"), Lit(0, INT)), env))    # Bool

# Gradual: untyped var y has type Any -- consistent with everything
print(infer(Add(Var("y"), Lit(1, INT)), env))   # Int (Any + Int is OK)

# Explicit annotation accepted
print(infer(Ann(Var("x"), INT), env))           # Int

# Type error caught statically
try:
    print(infer(Add(Var("name"), Lit(1, INT)), env))
except TypeError as e:
    print(f"Type error: {e}")
```

> **Watch out!** Consistency is **not** the same as subtyping. `Any` is consistent with `Int`, but `Any` is not a subtype of `Int`. Subtyping is a containment relationship; consistency is a compatibility relationship. Conflating them leads to incorrect reasoning about what the type checker actually accepts.

Questions to consider:

1. `DYN = "Any"` represents an unannotated binding. What does `consistent(DYN, INT)` return, and why? Trace through the `consistent` function body to verify your answer.
2. In gradual typing, `(Any + Int) -> Int`. This means the checker accepts adding an unannotated value to an `Int` and returns `Int`. Is this **sound**? (Hint: what if the `Any` value turns out to be a `Str` at runtime? Will the addition succeed?)
3. The consistency relation is **not transitive**: `consistent(INT, DYN)` is true and `consistent(DYN, STR)` is true, but `consistent(INT, STR)` is false. Draw a small diagram showing these three types and the consistency arrows between them. Why does allowing `DYN` to be consistent with everything create this non-transitivity?
4. What does the type checker **guarantee** when a program type-checks with **no** `DYN` types at all (i.e., every variable in `env` has a concrete type and no `Var` lookup returns `DYN`)? How does this guarantee weaken when some variables are unannotated?

### The blame calculus: who gets the error?

When two parties sign a contract, a violation needs to be traced back to whoever broke it, not to some innocent bystander in the middle. The blame calculus does exactly this for type boundaries: it tags each boundary with a label so that when a runtime cast fails, the error message names the site that made the broken promise rather than the function body that happened to discover the problem.

When a gradually-typed program fails at runtime (because a `DYN` value turned out to be the wrong type at a typed boundary) the system needs to say **which boundary** was violated. This is the **blame calculus** (Wadler and Findler, 2009). Without blame, a runtime failure deep inside a library could be misleadingly attributed to the library itself, when the real problem is that the caller passed an untyped value that violated the library's contract.

The key insight: when typed code calls untyped code, or untyped code calls typed code, a **cast** is inserted at the boundary. If the cast fails, blame is assigned to the boundary label, the name of the site that promised a value of the wrong type.

Note that TypeScript and mypy **erase** types at runtime (Section 7): TypeScript compiles to plain JavaScript, and mypy-annotated Python runs without any runtime checks. This means that in practice those systems do not enforce blame semantics at runtime. The blame calculus is more of a theoretical model for understanding responsibility than a feature you get for free in everyday toolchains.

```python
class Proxy:
    """A proxy wraps a dynamic value and tracks where it came from."""
    def __init__(self, value, expected_type, blame_label):
        self.value = value
        self.expected_type = expected_type
        self.blame_label = blame_label

    def force(self):
        """Check the type when the value is actually used."""
        type_map = {int: "Int", str: "Str", bool: "Bool"}
        actual = type_map.get(type(self.value), "Unknown")
        if actual != self.expected_type:
            raise RuntimeError(
                f"Blame: {self.blame_label} -- "
                f"expected {self.expected_type}, got {actual}"
            )
        return self.value

# Simulating: typed function f: Int -> Int called with dynamic argument
def f_typed(x_proxy):
    x = x_proxy.force()   # blame fires HERE if x is not Int
    return x + 1

# Good: calling f with an actual int wrapped as a proxy
good_arg = Proxy(42, "Int", "call-site:line-10")
print(f_typed(good_arg))  # 43

# Bad: calling f with a string (common when dynamic code calls typed code)
bad_arg = Proxy("hello", "Int", "call-site:line-15")
try:
    print(f_typed(bad_arg))
except RuntimeError as e:
    print(e)

# Demonstrate: blame label identifies the boundary, not the function body
def g_typed(x_proxy):
    # g does more work before using x
    intermediate = 100
    x = x_proxy.force()
    return x + intermediate

bad_for_g = Proxy(3.14, "Int", "untyped-module:line-42")
try:
    print(g_typed(bad_for_g))
except RuntimeError as e:
    print(e)
```

Questions to consider:

1. Without blame tracking, what would the error message look like if `f_typed` simply called `int(x)` and raised `ValueError` on a string? Why is knowing the **call site** more useful than knowing the **function body line** where the failure occurred?
2. TypeScript compiles to JavaScript and erases all types. mypy-annotated Python runs without any runtime checks. Given this, what happens when a TypeScript function typed `(n: number) => number` is called from JavaScript with a string? Does blame semantics apply?
3. If `f` is a typed function called from **untyped** code, should blame go to the **caller** or the **callee** when a type mismatch occurs? Justify your answer using the principle that blame should be assigned to the party that made a promise it did not keep.
4. The `Proxy` above only tracks a single `blame_label`. In a real system, typed values can pass through many boundaries (typed -> untyped -> typed -> untyped). How might you extend `Proxy` to track a **chain** of blame labels rather than just one?

### Try it: exercises

**Exercise 1: Extend the mini checker with `Let`.** Add a `Let` node to the `infer` function above. `Let(name, ty, val, body)` optionally annotates `name` with type `ty` (which may be `None`, meaning `DYN`). The checker should: (a) infer the type of `val`; (b) check that the inferred type is consistent with `ty` if `ty` is not `None`; (c) add `name` to the environment with the annotated type (or `DYN` if unannotated); (d) infer and return the type of `body`. Write two test cases: one that passes (annotated correctly) and one that fails (annotation mismatch).

**Exercise 2: Non-transitivity and blame chains.** The consistency relation is not transitive: `consistent(INT, DYN)` and `consistent(DYN, STR)` are both true, but `consistent(INT, STR)` is false. Construct a three-module scenario (a typed module A, an untyped module B, and a typed module C) where a value flows from A through B to C. Describe precisely: (a) what check is inserted at the A->B boundary; (b) what check is inserted at the B->C boundary; (c) why non-transitivity means the B->C check can fail even when the A->B check succeeded.

---

## Reference

- [mypy documentation](https://mypy.readthedocs.io/) and [TypeScript Playground](https://www.typescriptlang.org/play)
- Siek & Taha, "Gradual Typing for Functional Languages" (2006): the founding paper
- Wadler & Findler, "Well-Typed Programs Can't Be Blamed" (2009): the blame calculus behind Section 9
- Typed Racket: a production gradually-typed language that does insert runtime checks at boundaries, giving you actual blame semantics
- TypeScript's `unknown` vs `any`: a real-world version of Section 9's `DYN` type, with `unknown` requiring an explicit narrowing check before use
- Your own `SEMANTICS.md` (dynamic rules) and `TYPES.md` (static rules) from the Interpreter assignment
