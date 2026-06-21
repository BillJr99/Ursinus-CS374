<!--
author:   CS374 Course Team
email:    
version:  0.0.1
language: en
narrator: US English Female
comment:  Type Systems - Strong/Weak, Static/Dynamic, Structural/Nominal, Type Coercion, Type Erasure
import:   https://raw.githubusercontent.com/liaScript/coderunner/master/README.md
link:     https://cdn.jsdelivr.net/chartist.min.css
-->

# Type Systems: From Weak to Strong, Static to Dynamic

> **Opening Hook:** Type system features like generics are like templates in manufacturing: you write the blueprint once for `List<T>` and the factory instantiates it for steel, aluminum, or titanium without rewriting the assembly line. The `T` is not a runtime value — it is a compile-time *slot* that the type checker fills in at each use site, verifying safety separately for each instantiation. This module explores the full design space: how strictly types are checked (strong vs. weak), when they are checked (static vs. dynamic), whether compatibility is determined by name or shape (nominal vs. structural), and what survives to runtime (type erasure).

## Learning Goals

By the end of this activity, you will be able to:

- Identify where a language falls on the 2×2 matrix of static/dynamic and strong/weak type disciplines
- Analyze JavaScript-style implicit coercions and predict the result of mixed-type expressions
- Compare structural typing and nominal typing and determine which relationship holds for two given types
- Explain type erasure and describe how generic types are represented at runtime in a JVM-style language
- Evaluate the correctness risks introduced by weak typing and implicit coercions in real-world code

---

> **Before You Begin**
>
> This module assumes you are comfortable with:
> - Writing Python classes and calling methods on objects
> - The idea that a variable has a *type* (e.g., `int`, `str`) and that operations can fail with `TypeError`
> - Basic familiarity with at least one statically typed language (Java, C, TypeScript, or similar) — enough to know what a type annotation looks like
> - The concept of a *generic* container such as Java's `ArrayList<String>` or Python's `List[int]`
>
> You do **not** need to know what "covariance" or "structural subtyping" mean yet — those are introduced here.

---

> **Prerequisites:** Basic programming in Python and one statically-typed language
> **Goal:** Understand the 2×2 matrix of type discipline, how type coercion works, what structural vs nominal typing means, and how type erasure lets generics coexist with runtime efficiency.

**POGIL Roles:** Driver · Recorder · Reporter · Manager

---

## Model 1: The 2×2 Matrix of Type Systems

> **Intuition:** Think of the two axes as answering two separate questions. *When* does the language check types? (Before running = static; while running = dynamic.) *How strictly* does the language handle a mismatch? (Refuse to proceed = strong; silently convert = weak.) These questions are independent: a language can be any combination of the four quadrants. Most programmers have only experienced one or two quadrants; this model forces you to see the full space.

Type systems vary along two orthogonal axes:

**Axis 1 — When are types checked?**

- **Static:** At compile time, before any code runs. Errors are caught early.
- **Dynamic:** At runtime, when an operation is actually attempted. More flexible but errors appear later.

**Axis 2 — How strictly are type mismatches handled?**

- **Strong:** The language refuses to implicitly coerce a value from one type to another. A type mismatch is an error.
- **Weak:** The language will silently convert values between types to make an operation work.

```
               STATIC              DYNAMIC
           ┌───────────────┬───────────────────┐
  STRONG   │  Java, C#,    │  Python, Ruby,    │
           │  Haskell, Rust│  Erlang           │
           ├───────────────┼───────────────────┤
  WEAK     │  C, C++       │  JavaScript, PHP, │
           │               │  Perl             │
           └───────────────┴───────────────────┘
```

> **Note:** "Strong" and "weak" are informal terms without a single agreed definition. We use them to mean: does the language allow implicit type coercions that change the *kind* of data?

```python
# Python: dynamic AND strong
# Type errors surface at runtime, but Python won't silently coerce types
x = "5"
y = 3
print(x + y)   # TypeError: can only concatenate str (not "int") to str
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

> **Critical Thinking Questions 1–3**

**CTQ 1.** In the 2×2 grid above, where would you place TypeScript? Where would you place Perl? Justify each placement.

[[___ your answer here ___]]

**CTQ 2.** A language is *statically typed* but *weakly typed*. Give a concrete example from C where the compiler accepts code that silently performs a type coercion.

[[___ your answer here ___]]

**CTQ 3.** Python's `TypeError` above fires at *runtime*, not compile time. What does this tell you about whether Python checks types at all?

[[___ your answer here ___]]

---

> **Watch out!** The terms "strong" and "weak" typing are *informal* and used inconsistently in the wild. Some textbooks define "strong" to mean statically checked; others use it to mean no implicit coercions. In this course we use "strong" strictly to mean: the language does not silently convert between *kinds* of data (e.g., number to string). When you read these terms in other sources, always check what the author means.

## Model 2: Type Coercion — The JavaScript Nightmare

> **Intuition:** JavaScript's coercion rules were designed to make the language beginner-friendly by "doing what you probably meant." The problem is that "what you probably meant" is defined by a complex set of precedence rules that no one can memorize — and that interact badly at scale. Python made the opposite design choice: fail loudly on any ambiguous coercion, forcing the programmer to be explicit. The code is slightly more verbose but the behavior is predictable.

JavaScript is infamous for implicit coercions. These are all valid JavaScript expressions:

| Expression | Result | Why |
|---|---|---|
| `"5" + 3` | `"53"` | `+` prefers string concatenation |
| `"5" - 3` | `2` | `-` has no string meaning; coerces to number |
| `[] + {}` | `"[object Object]"` | both coerced to strings |
| `{} + []` | `0` | `{}` parsed as empty block; `+[]` = 0 |
| `false == "0"` | `true` | both coerced to 0 |
| `null == undefined` | `true` | special case in spec |
| `null === undefined` | `false` | strict equality, no coercion |

The root cause: JavaScript has a small set of runtime types (`number`, `string`, `boolean`, `object`, `undefined`, `null`, `symbol`, `bigint`) and the operators try hard to make any operands work.

**Python's intentional design contrast:**

```python
# Python refuses implicit numeric/string coercions
print("5" + 3)         # TypeError — no implicit coercion
print(int("5") + 3)    # 8 — explicit conversion is fine
print(str(3) + "5")    # "35" — explicit conversion is fine
print(True + 1)        # 2 — bool IS a subclass of int in Python (one coercion Python does allow)
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

### Implicit vs Explicit Coercion

- **Implicit coercion** (type *coercion*): language does it automatically — `"5" - 3` in JS
- **Explicit coercion** (type *conversion* or *casting*): programmer does it — `int("5")` in Python

> **Critical Thinking Questions 4–6**

**CTQ 4.** In JavaScript, `"5" + 3` gives `"53"` but `"5" - 3` gives `2`. What rule would explain why `+` and `-` behave differently?

[[___ your answer here ___]]

**CTQ 5.** Python allows `True + 1 == 2`. Is this a violation of Python's "strong typing"? Argue both sides, then give your conclusion.

[[___ your answer here ___]]

**CTQ 6.** A teammate says: "Weak typing is just a bug — all languages should be strongly typed." Give one legitimate use case where implicit coercion reduces boilerplate without causing confusion.

[[___ your answer here ___]]

---

## Model 3: Structural vs Nominal Typing

Two philosophies for deciding whether two types are *compatible*:

**Nominal typing** — compatibility is determined by *name* (and explicit declaration).

```java
// Java: nominal
interface Drawable { void draw(); }
class Circle implements Drawable { public void draw() { ... } }
class Square { public void draw() { ... } }  // does NOT implement Drawable
// Square cannot be used where Drawable is expected, even though it has draw()
```

**Structural typing** — compatibility is determined by *shape* (do you have the right methods/fields?).

```typescript
// TypeScript: structural
interface Drawable { draw(): void; }
class Circle { draw() { console.log("circle"); } }
class Square { draw() { console.log("square"); } }
// Both Circle and Square satisfy Drawable — no explicit declaration needed
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
render(42)         # AttributeError at runtime — "int has no attribute 'draw'"
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

### Python Protocols (Structural Typing Made Explicit)

Python 3.8 added `Protocol` for *static* structural checking:

```python
from typing import Protocol, runtime_checkable

@runtime_checkable
class Drawable(Protocol):
    def draw(self) -> None: ...

class Triangle:
    def draw(self) -> None:
        print("Drawing triangle")

t = Triangle()
print(isinstance(t, Drawable))   # True — structural, not nominal!
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

> **Critical Thinking Questions 7–9**

**CTQ 7.** In nominal typing, what must a class do to be considered a subtype of an interface? In structural typing, what determines subtyping?

[[___ your answer here ___]]

**CTQ 8.** Duck typing defers type checking to runtime. What is the trade-off compared to structural typing checked at compile time?

[[___ your answer here ___]]

**CTQ 9.** Go uses structural typing for interfaces: a type satisfies an interface by having the right methods, no `implements` needed. What advantage does this give to library designers? What risk does it introduce?

[[___ your answer here ___]]

---

## Model 4: Gradual Typing and Type Annotations

Some languages allow mixing typed and untyped code in the same program. This is **gradual typing**.

```
Spectrum of type discipline:
Untyped ──────────────────────────────────── Fully Static
  │                  │                              │
Python (no hints) Python + hints (mypy)   Java/Haskell/Rust
```

**Python type hints** (PEP 484, Python 3.5+):

```python
def greet(name: str) -> str:
    return "Hello, " + name

def add(x: int, y: int) -> int:
    return x + y

# Annotations are stored but NOT enforced at runtime
print(greet(42))         # works at runtime despite type hint saying str
print(add.__annotations__)
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

**Key insight:** Python type hints are *documentation* and *tool hints*, not enforcement. The runtime ignores them. Tools like `mypy`, `pyright`, and IDEs use them for static analysis.

### What mypy Would Catch

```python
# mypy would flag this before you run it:
def double(x: int) -> int:
    return x * 2

result: str = double(5)   # error: Incompatible types in assignment
                          # (expression has type "int", variable has type "str")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

> **Critical Thinking Questions 10–11**

**CTQ 10.** What does it mean for a type system to be *gradual*? What is the key property that separates gradual typing from simply "optional type hints"?

[[___ your answer here ___]]

**CTQ 11.** A function `def f(x)` with no annotation is treated by mypy as `def f(x: Any) -> Any`. Why does `Any` play a special role in gradual type systems rather than acting like `object`?

[[___ your answer here ___]]

---

## Model 5: Type Erasure

When generic types are compiled, the type parameter often disappears. This is **type erasure**.

### Java: Erasure at Compile Time

```java
// Source code — parameterized
List<String> names = new ArrayList<>();
names.add("Alice");
String s = names.get(0);   // compiler inserts cast

// After erasure — what the JVM actually runs
List names = new ArrayList();
names.add("Alice");
String s = (String) names.get(0);   // explicit cast inserted by compiler
```

At runtime, `List<String>` and `List<Integer>` are the **same** class. You cannot write `names instanceof List<String>`.

### C++: Monomorphization (No Erasure)

```cpp
template<typename T>
T max_val(T a, T b) { return a > b ? a : b; }

// Compiler generates TWO separate functions:
int    max_val(int a,    int b);     // for int
double max_val(double a, double b);  // for double
```

C++ templates are erased in a different sense: the source template disappears, but each instantiation becomes a fully typed, specialized function.

### Python: No Runtime Generics at All

```python
from typing import get_type_hints, List

def first(items: List[int]) -> int:
    return items[0]

# What survives to runtime?
print(get_type_hints(first))
# {'items': list[int], 'return': <class 'int'>}
# The annotation IS accessible via get_type_hints, but...

xs: List[int] = [1, 2, 3]
xs.append("oops")   # no runtime error — list doesn't check element types
print(xs)
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

### C++ `std::function` as Type Erasure

`std::function<void(int)>` stores *any callable* with the right signature — a regular function, a lambda, a functor. The concrete type is erased; only the interface survives. This is the **type erasure design pattern** (distinct from Java's compiler mechanism).

> **Critical Thinking Questions 12–15**

**CTQ 12.** In Java, why can't you write `new T()` or `T[] arr = new T[10]` inside a generic method? (Hint: what has been erased?)

[[___ your answer here ___]]

**CTQ 13.** C++ monomorphization means a template instantiated with 10 different types generates 10 copies of the function. What is the trade-off vs Java's erasure approach?

[[___ your answer here ___]]

**CTQ 14.** Python's `list` at runtime has no knowledge of its type annotation. What practical problem does this cause if you rely on type hints for correctness?

[[___ your answer here ___]]

**CTQ 15.** The `std::function` type erasure pattern in C++ has a runtime cost (heap allocation, indirect call). Under what circumstances is that cost worth paying?

[[___ your answer here ___]]

---

## Multiple Choice Review

**Question 1.** A language checks types only when an operation is actually executed, and it does *not* implicitly convert between numeric and string types. This language is:

- [( )] Static and weak
- [( )] Static and strong
- [(X)] Dynamic and strong
- [( )] Dynamic and weak

**Question 2.** In Java's generic type system, `List<String>` and `List<Integer>` at runtime are:

- [(X)] The same raw `List` class (type parameter erased)
- [( )] Different classes generated by monomorphization
- [( )] Incompatible interfaces requiring explicit adapters
- [( )] Identical because Java has no generics at runtime

**Question 3.** Which of the following best describes Python's `Protocol` class?

- [( )] Enforces nominal subtyping at runtime
- [(X)] Enables structural subtyping checked statically by tools like mypy
- [( )] Replaces `abstract` base classes entirely
- [( )] Adds compile-time generics to Python

---

## Exercises

**Exercise 1.** In Python, write a function that deliberately breaks the type hint contract and confirm that Python does NOT raise a runtime error:

```python
def multiply(x: int, y: int) -> int:
    return x * y

# Call it with strings and observe
result = multiply("ha", 3)
print(result)
print(type(result))
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

**Exercise 2.** Demonstrate Python's strong typing by showing three operations that *do* raise `TypeError`, and three that succeed after explicit conversion:

```python
# Three TypeError examples
# Three explicit conversion examples

```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

**Exercise 3.** Implement a `Sizeable` Protocol and two classes that satisfy it structurally (without inheriting from it). Verify with `isinstance`:

```python
from typing import Protocol, runtime_checkable

# Your solution here

```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

**Exercise 4.** Use `get_type_hints` to inspect the annotations of a function with several parameters, then add a value of the wrong type to a typed list and confirm no runtime error:

```python
from typing import get_type_hints, List

def process(items: List[str], count: int) -> bool:
    return len(items) == count

print(get_type_hints(process))
items: List[str] = ["a", "b"]
items.append(99)   # wrong type — does Python complain?
print(items)
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

**Exercise 5.** Write a `TypedStack` class that enforces element type at runtime (unlike Python's built-in `list`). Use `__init__(self, element_type)` and raise `TypeError` on a bad `push`:

```python
# Your solution here

```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

---

*End of Activity — Type Systems: Strong/Weak, Static/Dynamic, Structural/Nominal, Type Coercion, Type Erasure*
