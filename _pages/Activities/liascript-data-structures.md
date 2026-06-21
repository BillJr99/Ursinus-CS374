# Data Structures and Generics in Programming Languages
<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://github.com/BillJr99/Ursinus-CS374-Fall2026/blob/gh-pages/_pages/Activities/liascript-data-structures.md or locally via https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374/gh-pages/_pages/Activities/liascript-data-structures.md

import: https://raw.githubusercontent.com/liascript/CodeRunner/master/README.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

# Data Structures and Generics in Programming Languages

Every nontrivial program keeps collections of values — but *which* values, and enforced *how*? This activity walks from Python's fully polymorphic built-in containers through typed generic classes, algebraic data types, recursive structures, and finally the structural-versus-nominal typing divide. The arc: **polymorphic containers → parametric generics → product and sum types → recursive types → structural typing via Protocols**.

---

## Directions and Group Roles

Work in your POGIL team with rotated roles (**Manager**, **Recorder**, **Presenter**, **Reflector**). Consider each model and question individually first, then discuss with your group. The Recorder posts answers to the Class Activity Questions discussion board; the Presenter reports out areas of disagreement or alternative approaches. After class, respond to the reflective prompt individually in your notebook.

---

# Part I: Collections and Polymorphism

## Model 1: Built-in Collections and Polymorphism

Python's four built-in collection types — `list`, `dict`, `set`, `tuple` — are **polymorphic**: each can hold values of any type, including a mix of types in a single container. A **homogeneous** collection stores one type throughout; a **heterogeneous** collection mixes types. Both are possible in Python, but only homogeneous collections are typical in statically typed languages without generics.

```python
# Python built-in collections: fully polymorphic

# Heterogeneous list — holds any type
mixed = [42, "hello", 3.14, True, None, [1, 2]]
print("=== Heterogeneous list ===")
for item in mixed:
    print(f"  {item!r:20}  type: {type(item).__name__}")

# isinstance for type testing
print("\n=== isinstance checks ===")
print(f"mixed[0] is int:  {isinstance(mixed[0], int)}")
print(f"mixed[1] is str:  {isinstance(mixed[1], str)}")
print(f"mixed[3] is bool: {isinstance(mixed[3], bool)}")
# Note: bool is a subclass of int in Python
print(f"mixed[3] is int:  {isinstance(mixed[3], int)}  (bool is a subclass of int!)")

# Homogeneous list — conventional, tools can reason about it
ints:   list[int]   = [1, 2, 3, 4, 5]
words:  list[str]   = ["alpha", "beta", "gamma"]
print(f"\nints sum:  {sum(ints)}")
print(f"words joined: {', '.join(words)}")

# dict as key-value store
inventory: dict[str, int] = {"apples": 5, "bananas": 3, "cherries": 12}
print("\n=== dict (key-value store) ===")
for key, val in inventory.items():
    print(f"  {key}: {val}")
inventory["dates"] = 7
print(f"After insertion: {inventory}")

# set operations
evens = {2, 4, 6, 8, 10}
primes = {2, 3, 5, 7, 11}
print("\n=== set operations ===")
print(f"union:        {evens | primes}")
print(f"intersection: {evens & primes}")
print(f"difference:   {evens - primes}")
print(f"symmetric diff: {evens ^ primes}")

# tuple — immutable, fixed structure
point: tuple[float, float] = (3.0, 4.0)
x, y = point
print(f"\npoint = {point},  distance from origin = {(x**2 + y**2)**0.5:.4f}")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

### Critical Thinking Questions

1. What does it mean to call a container **polymorphic**? In your own words, contrast Python's `list` with Java's `int[]`.
2. What is the difference between a **homogeneous** and a **heterogeneous** collection? Give a real-world scenario in which you would deliberately want each.
3. The code shows that `isinstance(True, int)` returns `True`. Why is this the case in Python's type hierarchy? Does this surprise you? What problems could it cause in a type checker?
4. `dict`, `set`, and `tuple` each enforce a different structural constraint (ordered key-value pairs, unique elements, immutable sequence). Which of these constraints is enforced statically (at definition) versus dynamically (at runtime), and why?
5. A `set` requires elements to be **hashable**. What does that mean, and which of the types in `mixed` above are not hashable? Verify your prediction by trying to construct a set containing a list.

---

# Part II: Parametric Polymorphism

## Model 2: Generics and Parametric Polymorphism

**Parametric polymorphism** means a class or function can be *parameterized by a type*: `Stack[int]` and `Stack[str]` are the same algorithm but specialized to different element types. Python's `typing` module provides `TypeVar` and `Generic[T]` to express this. At runtime Python erases the type parameter (**type erasure**), but static checkers like mypy and pyright use it to catch mismatches before execution.

```python
from typing import TypeVar, Generic, Optional

T = TypeVar('T')

class Stack(Generic[T]):
    def __init__(self) -> None:
        self._items: list[T] = []

    def push(self, item: T) -> None:
        self._items.append(item)

    def pop(self) -> Optional[T]:
        if self._items:
            return self._items.pop()
        return None

    def peek(self) -> Optional[T]:
        return self._items[-1] if self._items else None

    def is_empty(self) -> bool:
        return len(self._items) == 0

    def __len__(self) -> int:
        return len(self._items)

    def __repr__(self) -> str:
        return f"Stack({self._items})"

# Type-annotated usage: Stack[int]
int_stack: Stack[int] = Stack()
int_stack.push(1)
int_stack.push(2)
int_stack.push(3)
print("=== Stack[int] ===")
print(f"Stack: {int_stack}")
print(f"Size:  {len(int_stack)}")
print(f"Peek:  {int_stack.peek()}")
print(f"Pop:   {int_stack.pop()}")
print(f"After pop: {int_stack}")

# Stack[str] — same implementation, different element type
str_stack: Stack[str] = Stack()
str_stack.push("hello")
str_stack.push("world")
str_stack.push("!")
print("\n=== Stack[str] ===")
print(f"Stack: {str_stack}")
print(f"Top:   {str_stack.peek()}")
while not str_stack.is_empty():
    print(f"  popped: {str_stack.pop()!r}")

# At runtime, both are the same class — type erasure in action
print(f"\ntype(int_stack) is type(str_stack): {type(int_stack) is type(str_stack)}")
print(f"Both are Stack: {isinstance(int_stack, Stack) and isinstance(str_stack, Stack)}")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

### Critical Thinking Questions

6. What is `T` called, and what role does it play in the definition of `Stack`? How is it different from a concrete type like `int`?
7. The annotation `Stack[int]` signals intent to a static checker, but the final `print` shows that at runtime `type(int_stack) is type(str_stack)`. What does this tell you about **type erasure**? What safety does the annotation still provide?
8. In a language like Java, `Stack<Integer>` and `Stack<String>` are also the same class at runtime (Java also erases). In C++, `std::stack<int>` and `std::stack<std::string>` generate *separate compiled code*. What are the trade-offs of each approach (code size, performance, error messages)?
9. The `Optional[T]` return type on `pop` encodes the possibility of an empty stack. What is the alternative design (raising an exception)? Which is more *composable* in a functional style?
10. Suppose a static checker flags `int_stack.push("oops")`. Where in the pipeline does this error fire relative to type erasure? What does this imply about when generic type annotations are useful?

---

# Part III: Algebraic Data Types

## Model 3: Algebraic Data Types — Product and Sum Types

**Algebraic data types** (ADTs) come in two flavors:

- A **product type** requires *all* its fields simultaneously — it is the Cartesian product of its component types. `Circle(radius=5.0)` must have a `radius`; there is no partial `Circle`.
- A **sum type** (also called a **variant** or **union**) holds *exactly one* of several alternatives. `Shape` is a `Circle` **or** a `Rectangle` **or** a `Triangle` — never two at once.

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
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

### Critical Thinking Questions

11. Explain why `Circle` is a **product type**: what does "product" mean here, and what constraint does it place on construction?
12. Explain why `Shape` is a **sum type**: what does "sum" mean here? How many values can a single `Shape` variable contain simultaneously?
13. What happens if you add a new variant — say `@dataclass class Pentagon: sides: float` — to `Shape` but forget to add a branch to `area()`? Trace what Python does. How would a **sealed sum type** in a language like Rust, Haskell, or Kotlin prevent this mistake at compile time?
14. The `else: raise ValueError` branch in `area` is defensive programming against a case the type system claims cannot happen. Should it be there? What does its presence say about the gap between Python's runtime and its static type annotations?
15. Dataclasses generate `__eq__` and `__repr__` automatically. What other "free" operations could a language derive from a product type's structure? (Hint: think serialization, copying, hashing.)

---

# Part IV: Recursive Data Structures

## Model 4: Recursive Data Structures — A Generic Linked List

A **recursive data type** is one that refers to itself in its own definition: `Node[T]` has a `value: T` and a `next` which is either another `Node[T]` or `None`. This is the canonical example of a **sum type inside a product type**: each node simultaneously holds a value (product) *and* is one of "has a next node" or "is the last node" (sum / `Optional`).

```python
from __future__ import annotations
from typing import TypeVar, Generic, Optional

T = TypeVar('T')

class Node(Generic[T]):
    def __init__(self, value: T, next: Optional[Node[T]] = None) -> None:
        self.value: T = value
        self.next: Optional[Node[T]] = next

    def __repr__(self) -> str:
        return f"Node({self.value!r})"

class LinkedList(Generic[T]):
    def __init__(self) -> None:
        self.head: Optional[Node[T]] = None
        self._size: int = 0

    def prepend(self, value: T) -> None:
        """Add to front in O(1)."""
        self.head = Node(value, self.head)
        self._size += 1

    def append(self, value: T) -> None:
        """Add to back in O(n)."""
        new_node: Node[T] = Node(value)
        if self.head is None:
            self.head = new_node
        else:
            current = self.head
            while current.next is not None:
                current = current.next
            current.next = new_node
        self._size += 1

    def to_list(self) -> list[T]:
        result: list[T] = []
        current = self.head
        while current is not None:
            result.append(current.value)
            current = current.next
        return result

    def contains(self, value: T) -> bool:
        current = self.head
        while current is not None:
            if current.value == value:
                return True
            current = current.next
        return False

    def __len__(self) -> int:
        return self._size

    def __repr__(self) -> str:
        return " -> ".join(str(v) for v in self.to_list()) + " -> None"

# Build a LinkedList[int]
lst: LinkedList[int] = LinkedList()
for i in [5, 4, 3, 2, 1]:
    lst.prepend(i)

print("=== LinkedList[int] (prepend order) ===")
print(f"List:     {lst}")
print(f"Size:     {len(lst)}")
print(f"Contains 3: {lst.contains(3)}")
print(f"Contains 9: {lst.contains(9)}")

# Build a LinkedList[str]
words: LinkedList[str] = LinkedList()
for w in ["the", "quick", "brown", "fox"]:
    words.append(w)

print("\n=== LinkedList[str] (append order) ===")
print(f"List:     {words}")
print(f"Size:     {len(words)}")
print(f"as list:  {words.to_list()}")

# Node structure visible
print("\n=== Node internals ===")
current = lst.head
depth = 0
while current is not None:
    print(f"  depth {depth}: Node(value={current.value}, next={current.next})")
    current = current.next
    depth += 1
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

### Critical Thinking Questions

16. Why does `Node` use `Optional[Node[T]]` for `next` rather than just `Node[T]`? What would happen if you tried to construct the last node without `Optional`?
17. What is the **base case** of this recursive type? In other words, what terminates the chain, and how is it represented in the type?
18. Trace how the type parameter `T` flows: if you write `LinkedList[int]`, what type does `self.head` have? What type does `current.value` have inside `to_list`? Does Python actually enforce this at runtime?
19. `prepend` is O(1) and `append` is O(n). Why? Sketch a modification (a `tail` pointer) that would make `append` O(1), and describe what invariant you must maintain.
20. The `from __future__ import annotations` at the top is required for `Optional[Node[T]]` to work inside `Node`'s own definition. Why? What problem does it solve? (Hint: think about when Python evaluates type annotations.)

---

# Part V: Structural vs Nominal Typing

## Model 5: Structural vs Nominal Typing and Protocols

Two philosophies govern whether a type "fits" where another is expected:

- **Nominal typing**: a type fits because you *declared* it belongs (via inheritance or `implements`). Java's `class Circle implements Drawable` is required; the compiler checks the declaration chain.
- **Structural typing** (duck typing): a type fits because it *has the right shape* — the necessary attributes and methods exist. Python's `Protocol` formalizes this: any class that provides the required methods satisfies the protocol, with no explicit declaration.

`@runtime_checkable` lets you use `isinstance` to test protocol conformance at runtime.

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

# A class that is missing one required method — does NOT satisfy Drawable
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
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

### Critical Thinking Questions

21. Do `Circle` and `Square` inherit from `Drawable`? Check the MRO output. Yet `isinstance(circle, Drawable)` returns `True`. Explain why.
22. In Java, to achieve the same effect you would write `class Circle implements Drawable`. What does that declaration cost you (coupling, compile-time checking, file organization)? What does Python's structural approach cost you in return?
23. `NotDrawable` has `draw` but not `area`. How does `isinstance(NotDrawable(), Drawable)` respond, and why? What does this tell you about the granularity of Protocol checking?
24. Structural typing is sometimes called **duck typing** ("if it walks like a duck and quacks like a duck, it is a duck"). Name one situation where duck typing is a significant advantage over nominal typing, and one where it is a significant disadvantage.
25. The `...` (Ellipsis) in `def draw(self) -> str: ...` is a body placeholder. How is this different from `pass`? When would you use each?

---

# Part VI: Multiple Choice

[[MC]]
What is parametric polymorphism?
- (x) A type or function can be parameterized by another type (e.g., `Stack[T]`)
- ( ) A function has multiple implementations selected by argument types at runtime
- ( ) A subtype can be used wherever a supertype is expected
- ( ) Types are checked only at runtime

[[MC]]
In Python's `typing` module, `Union[Circle, Rectangle, Triangle]` represents:
- ( ) A class that inherits from all three types simultaneously
- (x) A sum type — a value that is exactly one of the listed alternatives
- ( ) A product type combining all three types' fields
- ( ) A generic type parameterized by three TypeVars

[[MC]]
Type erasure means:
- ( ) Type annotations are removed from source code before compilation
- ( ) A type can be cast to a different type at runtime
- (x) Generic type parameters exist only at the static-checking level and are unavailable at runtime
- ( ) The garbage collector removes unused type objects from memory

[[MC]]
In structural typing via `Protocol`, `isinstance(obj, MyProtocol)` returns `True` when:
- ( ) `obj`'s class explicitly inherits from `MyProtocol`
- ( ) `obj`'s class is registered with `MyProtocol.register()`
- (x) `obj`'s class provides all the methods and attributes required by `MyProtocol`
- ( ) `obj` is of exactly the same type as `MyProtocol`

---

# Part VII: Exercises

## 3. Exercises

1. *Generic `Queue[T]`.* Implement a `Queue` class using `Generic[T]` with `enqueue(item: T) -> None`, `dequeue() -> Optional[T]`, `front() -> Optional[T]`, and `__len__`. Instantiate both a `Queue[int]` and a `Queue[str]`, verify that they work correctly, and confirm that at runtime both are instances of the same `Queue` class (type erasure).

2. *Binary tree `BTree[T]`.* Implement a `BTree` generic class with `insert(value: T) -> None` (BST insertion using `<` ordering) and `inorder() -> list[T]` (in-order traversal). Demonstrate with `BTree[int]` and `BTree[str]`. What constraint must `T` satisfy for `<` to be defined? How would you express that constraint using a `Protocol`?

3. *`Result[T, E]` ADT.* Implement a `Result` type that is either `Ok(value: T)` or `Err(error: E)` — a sum type representing success or failure. Add a `map(f) -> Result` method that applies `f` to the value if `Ok`, or passes `Err` through unchanged. Show that `Result` chains let you compose several operations that might fail without any explicit `try`/`except` at each step.

4. *`Comparable` Protocol and generic sort.* Define a `Comparable` Protocol requiring `__lt__(self, other: Any) -> bool`. Write a generic function `insertion_sort(items: list[C]) -> list[C]` (where `C` is a `TypeVar` bound to `Comparable`) that sorts any list of `Comparable` items. Verify with lists of `int`, `str`, and a custom `Card` dataclass that implements `__lt__` by rank.

---

## Reflection Prompt

In your notebook: both generics and dynamic typing allow a single function or class to work with many types — but they do so in very different ways. Generics express the constraint *statically*, before any value exists; dynamic typing defers the question until a value is actually used. Describe a scenario where catching a type mismatch before the program runs would have saved significant debugging time, and a scenario where dynamic flexibility genuinely made the code simpler. Which approach does your project's language take, and what does that choice imply for the users of your language?

---

## 4. Further Reading

- Python Software Foundation. "typing — Support for type hints." *Python 3 Documentation*, docs.python.org/3/library/typing.html.
- Jukka Lehtosalo et al. *Mypy: Optional Static Typing for Python*, mypy.readthedocs.io.
- Benjamin C. Pierce. *Types and Programming Languages*, Chapter 22: Type Reconstruction, and Chapter 23: Universal Types. MIT Press, 2002.
- Simon Peyton Jones. "Haskell's Type Classes vs Python's Protocols." (Compare structural Protocol typing with Haskell's nominally-declared type classes for a sharp contrast.)
- Alexis King. "Parse, don't validate." *Lexi Lambda Blog*, 2019. (A practical argument for ADTs and sum types as the right tool for data modelling.)
