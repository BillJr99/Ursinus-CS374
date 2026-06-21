<!--
author:   CS374 Course Team
email:    
version:  0.0.1
language: en
narrator: US English Female
comment:  Objects and OOP - Classes, Vtables, Polymorphism, Multiple Inheritance, Objects as Closures
import:   https://raw.githubusercontent.com/liaScript/coderunner/master/README.md
link:     https://cdn.jsdelivr.net/chartist.min.css
-->

# Objects and OOP: From Closures to Vtables

## Learning Goals

By the end of this activity, you will be able to:

- Implement an object with encapsulated mutable state using only closures, without any class machinery, and explain why the two approaches are semantically equivalent
- Describe how a vtable (virtual dispatch table) enables dynamic polymorphism, and trace method resolution for a given class hierarchy by hand
- Predict Python's method resolution order (MRO) for a multiple-inheritance diamond hierarchy and verify the prediction using `ClassName.__mro__`
- Compare the OOP models of Python, Java, and C++ across the dimensions of single vs. multiple inheritance, dynamic vs. static dispatch, and interface vs. abstract-class design

> **Prerequisites:** Basic Python classes, functional programming activity
> **Goal:** See objects as a special case of closures, understand how vtables implement dynamic dispatch, and explore the OOP design space across Python, Java, and C++.

**POGIL Roles:** Driver · Recorder · Reporter · Manager

---

## Model 1: Objects Are Closures

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

## Model 2: Python's Object Model

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

### Attribute Lookup Order

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

## Model 3: Inheritance and the MRO

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

### The Diamond Problem

Without C3 linearization, `D.hello()` could go to either `B.hello` or `C.hello`. Python's rule: left-to-right depth-first, but each class appears only *after* all its subclasses — this is the C3 constraint.

### `super()` Follows the MRO

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

## Model 4: Virtual Dispatch and Vtables

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

### Abstract Base Classes Enforce the Interface

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

## Model 5: Protocols, Duck Typing, and Interfaces

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

### Mixins — Reuse Without Inheritance Chains

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

### `__slots__` for Memory Optimization

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

## Multiple Choice Review

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

## Exercises

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

## Reflection

Answer each in 2–3 sentences:

1. This activity argued that objects are a special case of closures. Does the reverse hold — are closures a special case of objects? Defend your answer with a specific example.

2. Python's vtable equivalent (dict-based lookup) is more flexible than C++'s fixed vtable, but slower. Describe one programming pattern that is possible in Python because of this flexibility but impossible (or extremely awkward) in C++.

3. The MRO exists to solve the diamond problem. Describe in your own words what the C3 linearization rule guarantees, and explain why that guarantee matters for correctness.

---

*End of Activity — Objects and OOP: From Closures to Vtables*
