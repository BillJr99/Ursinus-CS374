# A Gallery of Programming Languages: Same Problem, Different Minds
<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://github.com/BillJr99/Ursinus-CS374-Fall2026/blob/gh-pages/_pages/Activities/liascript-language-gallery.md

import: https://raw.githubusercontent.com/liascript/CodeRunner/master/README.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

# A Gallery of Programming Languages: Same Problem, Different Minds

A programming language is not just a tool — it is a crystallized theory of what computation is. Every `for` loop, list comprehension, or logic clause embeds a belief about how problems should be decomposed and what the programmer should have to say explicitly. Exploring many languages through the same problem is like tasting the same dish cooked by five different chefs: the ingredients are the same, but the philosophy behind the recipe changes everything.

## Learning Goals

By the end of this activity, you will be able to:

- Identify the five major programming paradigms (imperative, object-oriented, functional, logic, declarative) and characterize the computational worldview each embodies
- Implement the same problem in multiple paradigms in Python and explain how the choice of paradigm shapes the structure and readability of the solution
- Compare how different paradigms handle state, control flow, and abstraction, and evaluate the tradeoffs in expressiveness and correctness
- Apply the concept of paradigm as a design choice — not a fact — when selecting an approach for a given problem
- Analyze an unfamiliar language feature and classify it within the paradigm taxonomy based on its behavior

> **Before You Begin:** This activity assumes you can:
> - Write Python functions using loops, list comprehensions, and lambda expressions
> - Describe in plain English what a recursive function does on a concrete example
> - Explain what an environment (dictionary of variable-to-value mappings) is in the context of an interpreter
>
> If any of these feel shaky, review them first.

## Introduction

Here is a fact that most programming courses hide from you: **programming languages are not tools — they are philosophical positions.**

Every language embeds a theory of computation. Every syntax reflects a model of mind. Every design choice encodes a belief about what programs should look like, what programmers should be allowed to do, and what the relationship between human thought and machine execution should be. When you write a `for` loop, you are not just iterating — you are adopting an entire worldview about how computation unfolds through time, step by step, mutation by mutation. When you write `sum(x*x for x in range(1,101) if x%2==0)`, you are making a different philosophical commitment: that computation is best described as a transformation of values, not a sequence of state changes.

This activity takes a small number of concrete problems and solves each one through five different philosophical lenses. You will not be learning five new languages today — you will be learning five ways of *thinking* about what it means to compute something. By the end, you should feel the difference viscerally: not as an abstract taxonomy from a textbook, but as a lived experience of writing (or reading) code that surprises you, delights you, or unsettles your assumptions. The "right" way to write a program is a choice, not a fact. Today you will practice making that choice consciously.

---

## Model 1: Five Ways to Sum a List

All five snippets below compute the same number (171700), yet they read like different languages from different planets. As you read each one, ask yourself: what does the programmer have to say explicitly? What does the language figure out on its own? The answers reveal the core trade-off each paradigm is making between programmer control and language assistance.

> **The Problem:** Compute the sum of the squares of all even numbers from 1 to 100.
>
> **The Claim:** There are at least five meaningfully different ways to express this — and they reveal five different theories of what computation is.

Before we visit other languages, we stay in Python. Python is a polyglot language: it can wear multiple paradigm hats. This lets us isolate the *paradigm* from the *syntax*, and see clearly that the choice of style is a choice of mindset.

```python
# Problem: compute sum of squares of even numbers from 1 to 100
# Five paradigms, one problem

# --- Imperative (C-style thinking in Python) ---
result_imp = 0
for i in range(1, 101):
    if i % 2 == 0:
        result_imp += i * i
print(f"Imperative: {result_imp}")

# --- Object-Oriented ---
class NumberPipeline:
    def __init__(self, data): self._data = list(data)
    def filter(self, pred): return NumberPipeline(x for x in self._data if pred(x))
    def map(self, fn): return NumberPipeline(fn(x) for x in self._data)
    def reduce(self, fn, init):
        acc = init
        for x in self._data: acc = fn(acc, x)
        return acc

result_oop = (NumberPipeline(range(1, 101))
              .filter(lambda x: x % 2 == 0)
              .map(lambda x: x * x)
              .reduce(lambda a, b: a + b, 0))
print(f"OOP:        {result_oop}")

# --- Functional (higher-order functions) ---
from functools import reduce
result_fn = reduce(lambda a, b: a + b,
                   map(lambda x: x * x,
                       filter(lambda x: x % 2 == 0, range(1, 101))))
print(f"Functional: {result_fn}")

# --- Declarative (comprehension) ---
result_decl = sum(x * x for x in range(1, 101) if x % 2 == 0)
print(f"Declarative:{result_decl}")

# --- APL-inspired (array-oriented) ---
import numpy as np
nums = np.arange(1, 101)
result_apl = np.sum((nums[nums % 2 == 0]) ** 2)
print(f"Array:      {result_apl}")

# All should be 171700
assert result_imp == result_oop == result_fn == result_decl == result_apl == 171700
print("\nAll paradigms agree: 171700")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

> **Watch out!** The NumPy array-oriented version returns a NumPy scalar (`numpy.int64`), not a plain Python `int`. The `==` comparison still works, but `type(result_apl) == int` is `False`. This is a common source of subtle bugs when mixing NumPy and pure Python code.

---

**Critical Thinking Questions**

1. The imperative version uses a loop and mutation: `result_imp` changes on each iteration. The declarative version is one line and introduces no variable that changes. What does the declarative version *hide* that the imperative version *exposes*? Which is more readable — and more importantly, *readable to whom*? Does the answer change depending on whether the reader has a C background or a math background?

2. The OOP version creates a `NumberPipeline` class with `.filter()`, `.map()`, and `.reduce()` methods. What design pattern does this implement? (Hint: look up "fluent interface" and "builder pattern.") What concrete advantage does method chaining give over the nested function calls in the functional version?

3. The functional version nests `map`, `filter`, and `reduce`. The `reduce` is the *outermost* call — it appears first in the source. But it executes *last*. Why does evaluation happen inside-out? Draw the call tree if it helps.

4. NumPy's array operations can parallelize implicitly — the hardware can compute all element-wise squares at the same time. Why is this safe for the array-oriented version but potentially *unsafe* for a parallelized version of the imperative loop with a shared `result_imp` variable?

---

## Model 2: Fibonacci — Recursion, Memoization, and Generators

The naive recursive Fibonacci is famous for being simultaneously the clearest expression of the mathematical definition and a comically slow program. The five variants here each fix the performance problem in a different way — and each fix reveals a different language design concept. Pay attention to what changes between versions and what stays the same.

> **Watch out!** `@lru_cache` caches based on argument equality. If you call `fib_memo(20)` in two different places, the second call returns the cached result instantly. But the cache is tied to the function object — a new function defined with the same body gets its own empty cache. This catches students who define their own cached function and wonder why it is still slow.

> **The Problem:** Compute Fibonacci numbers.
>
> **The Claim:** This deceptively simple problem reveals how the *same mathematical definition* can be expressed with radically different computational consequences — from exponential time to logarithmic time, and from finite lists to infinite streams.

Fibonacci is the "Hello, World" of recursion, but most courses stop at the naive version and leave students with the impression that recursion is slow. That is backwards. The naive version is slow not because it is recursive, but because it *recomputes the same subproblems*. What follows shows four ways to fix that, plus one approach that sidesteps the recursion entirely.

```python
import sys
sys.setrecursionlimit(500)

# 1. Naive recursion (beautiful but exponential)
def fib_naive(n):
    if n <= 1: return n
    return fib_naive(n-1) + fib_naive(n-2)

# 2. Memoized recursion (adds caching transparently)
from functools import lru_cache

@lru_cache(maxsize=None)
def fib_memo(n):
    if n <= 1: return n
    return fib_memo(n-1) + fib_memo(n-2)

# 3. Iterative (tail-recursive style, but imperative)
def fib_iter(n):
    a, b = 0, 1
    for _ in range(n): a, b = b, a + b
    return a

# 4. Generator (lazy, infinite sequence)
def fib_stream():
    a, b = 0, 1
    while True:
        yield a
        a, b = b, a + b

# 5. Matrix exponentiation (O(log n)) — different algorithm entirely
def mat_mul(A, B):
    return [
        [A[0][0]*B[0][0] + A[0][1]*B[1][0], A[0][0]*B[0][1] + A[0][1]*B[1][1]],
        [A[1][0]*B[0][0] + A[1][1]*B[1][0], A[1][0]*B[0][1] + A[1][1]*B[1][1]]
    ]

def mat_pow(M, n):
    if n == 1: return M
    if n % 2 == 0:
        half = mat_pow(M, n // 2)
        return mat_mul(half, half)
    return mat_mul(M, mat_pow(M, n - 1))

def fib_matrix(n):
    if n == 0: return 0
    M = [[1,1],[1,0]]
    return mat_pow(M, n)[0][1]

# Compare all at n=20
n = 20
results = {
    "Naive":    fib_naive(n),
    "Memoized": fib_memo(n),
    "Iterative":fib_iter(n),
    "Generator":next(x for i,x in enumerate(fib_stream()) if i == n),
    "Matrix":   fib_matrix(n),
}
for name, val in results.items():
    print(f"  {name:12}: fib({n}) = {val}")

# Show laziness: first 10 from the infinite stream
stream = fib_stream()
print(f"\nFirst 10: {[next(stream) for _ in range(10)]}")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

---

**Critical Thinking Questions**

1. The naive recursive solution is the most direct translation of the mathematical definition: *fib(n) = fib(n-1) + fib(n-2)*. What is its time complexity, and why? Draw a partial call tree for `fib_naive(5)` and count the number of calls to `fib_naive(2)` to build your intuition.

2. `@lru_cache` transforms the exponential-time function to linear-time without changing a single line of the recursive logic. The "what" (the recurrence relation) stays the same; only the "how" (caching) is added. What is the general term in PL design for separating the *specification* of a computation from its *implementation* strategy? (Hint: think about what a compiler does with tail-call optimization, or what a SQL optimizer does with a query.)

3. The generator `fib_stream()` represents an *infinite* sequence. What does it mean for a sequence to be "lazy"? Why would `list(fib_stream())` run forever (or until you run out of memory) while `next(stream)` is safe? What other languages build laziness into their evaluation model by default?

4. The matrix exponentiation version computes fib(n) in O(log n) time — it is a fundamentally different algorithm from any of the recursive or iterative approaches. What does this tell you about the relationship between *algorithm choice* and *paradigm choice*? Are they independent?

---

## Model 3: Sorting — Algorithms as Philosophies

Sorting algorithms are taught as performance exercises, but viewed through a PL lens they are paradigm exercises: quicksort embodies divide-and-conquer recursion, mergesort embodies pure functional immutability, and the "specification" approach embodies the logic programming idea that you should describe what you want and let the runtime figure out how. Watch for what each style makes easy and what it hides.

> **The Problem:** Sort a list of integers.
>
> **The Claim:** Different sorting algorithms encode different philosophical commitments about how to break a problem apart, and different language paradigms make some commitments more natural to express than others.

Quicksort and mergesort are both "divide and conquer," but they divide differently and conquer differently. The third approach — describing *what it means* to be sorted rather than *how* to sort — represents the logic programming worldview. Python's production `sorted()` is a reminder that real systems optimize for different things than textbooks do.

```python
# Three sorting philosophies

# 1. Quicksort — divide and conquer with a pivot
# In Haskell this is ONE LINE: qsort [] = []; qsort (x:xs) = qsort smaller ++ [x] ++ qsort larger
# Python functional version:
def qsort(lst):
    if len(lst) <= 1: return lst
    pivot = lst[len(lst) // 2]
    left  = [x for x in lst if x < pivot]
    mid   = [x for x in lst if x == pivot]
    right = [x for x in lst if x > pivot]
    return qsort(left) + mid + qsort(right)

# 2. Mergesort — pure divide and conquer (no in-place mutation)
def mergesort(lst):
    if len(lst) <= 1: return lst
    mid = len(lst) // 2
    left  = mergesort(lst[:mid])
    right = mergesort(lst[mid:])
    return merge(left, right)

def merge(a, b):
    if not a: return b
    if not b: return a
    if a[0] <= b[0]:
        return [a[0]] + merge(a[1:], b)
    return [b[0]] + merge(a, b[1:])

# 3. "Bogo-describe" — express the property, let the runtime find a solution
# (Prolog-style thinking: describe what you want, not how to compute it)
def is_sorted(lst):
    return all(lst[i] <= lst[i+1] for i in range(len(lst)-1))

def check_sort(lst):
    """Verify a sort by SPECIFICATION: the result should be sorted and a permutation."""
    result = sorted(lst)
    assert is_sorted(result), "Not sorted!"
    assert sorted(result) == sorted(lst), "Not a permutation!"
    return result

# 4. Python's built-in Timsort — a hybrid, hyper-optimized, REAL sort
import random
data = [random.randint(1, 100) for _ in range(20)]
print(f"Input: {data}")
print(f"qsort:     {qsort(data)}")
print(f"mergesort: {mergesort(data)}")
print(f"Timsort:   {sorted(data)}")
print(f"All equal: {qsort(data) == mergesort(data) == sorted(data)}")

# The "specification" approach:
result = check_sort(data)
print(f"\nSpecification-verified sort: {result[:5]}...{result[-5:]}")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

> **Watch out!** The `merge` function above creates new lists with `[a[0]] + merge(...)` on every recursive call, giving O(n²) total allocation. This is pedagogically clean but performance-terrible for large inputs. Real mergesort implementations use in-place merging or pre-allocated buffers — a good example of the gap between a paradigm-pure implementation and a production one.

---

**Critical Thinking Questions**

1. The comment in the code shows that Haskell's quicksort fits in two lines using pattern matching on lists: `qsort [] = []` and `qsort (x:xs) = qsort smaller ++ [x] ++ qsort larger`. The Python version needs five lines to express the same idea. What does this tell you about the *expressiveness* of list pattern matching compared to Python's index-based approach? What syntactic feature of Haskell makes this possible?

2. The `merge` function in mergesort is recursive and builds entirely new lists at each step — it never modifies an existing list. What is the memory cost of this approach relative to an in-place merge? Under what circumstances would you prefer immutable mergesort over a mutation-based sort?

3. The `check_sort` function verifies that `sorted(lst)` is correct by checking two properties: (a) the output is ordered, and (b) the output is a permutation of the input. This is the *specification* of a sort. In Prolog or a constraint solver, you could write these constraints and let the runtime *generate* a sorted list rather than verify one. What ingredient is missing from `check_sort` that would make it a generator rather than a verifier?

4. Python's `sorted()` uses Timsort, a hybrid algorithm that combines merge sort and insertion sort and is specifically tuned for real-world data patterns (partially sorted runs). Why would the designers of a practical language *not* use the most theoretically elegant algorithm? What tradeoffs does Timsort make?

---

## Model 4: Tree Operations — Pattern Matching vs. Visitor Pattern

Expression trees are the central data structure of every interpreter you will write this semester. This model shows three philosophically distinct ways to traverse the same tree: functional pattern matching (enumerate cases in a function), OOP visitor (dispatch through method overriding), and fold (replace constructors with functions). Notice that the fold produces `eval`, `count`, and `depth` from a single recursive structure — you provide the algebra, not the recursion.

> **The Problem:** Evaluate, pretty-print, count, and measure the depth of an expression tree.
>
> **The Claim:** ML/Haskell-style pattern matching and OOP's Visitor pattern solve the same extensibility problem in opposite ways. Understanding *why* they are opposites unlocks one of the deepest questions in PL design.

A binary expression tree is the central data structure of every interpreter and compiler. How you traverse it says a great deal about your programming model. In ML, you write a function and enumerate the cases. In Java, you write a class hierarchy and add methods. In category theory, you write a fold (catamorphism) that replaces each constructor with a function. All three produce the same output. None of them is "correct."

```python
from dataclasses import dataclass
from typing import Any, Optional, Callable

# A binary expression tree
@dataclass
class Leaf: value: float

@dataclass
class Add: left: Any; right: Any

@dataclass
class Mul: left: Any; right: Any

@dataclass
class Neg: child: Any

# === STYLE 1: Pattern Matching (ML/Haskell style) ===
# Haskell: eval (Leaf v) = v
#          eval (Add l r) = eval l + eval r
#          eval (Mul l r) = eval l * eval r
#          eval (Neg c) = -(eval c)
def eval_match(tree) -> float:
    match tree:
        case Leaf(value=v):      return v
        case Add(left=l, right=r): return eval_match(l) + eval_match(r)
        case Mul(left=l, right=r): return eval_match(l) * eval_match(r)
        case Neg(child=c):       return -eval_match(c)
    raise ValueError(f"Unknown: {type(tree)}")

# === STYLE 2: OOP Visitor Pattern (Java/C++ style) ===
class EvalVisitor:
    def visit(self, tree):
        method = getattr(self, f'visit_{type(tree).__name__}')
        return method(tree)
    def visit_Leaf(self, node): return node.value
    def visit_Add(self, node): return self.visit(node.left) + self.visit(node.right)
    def visit_Mul(self, node): return self.visit(node.left) * self.visit(node.right)
    def visit_Neg(self, node): return -self.visit(node.child)

class PrettyPrintVisitor:
    def visit(self, tree):
        method = getattr(self, f'visit_{type(tree).__name__}')
        return method(tree)
    def visit_Leaf(self, n): return str(n.value)
    def visit_Add(self, n): return f"({self.visit(n.left)} + {self.visit(n.right)})"
    def visit_Mul(self, n): return f"({self.visit(n.left)} * {self.visit(n.right)})"
    def visit_Neg(self, n): return f"(-{self.visit(n.child)})"

# === STYLE 3: Functional fold (catamorphism) ===
def fold(tree, leaf_fn: Callable, add_fn: Callable, mul_fn: Callable, neg_fn: Callable):
    match tree:
        case Leaf(value=v): return leaf_fn(v)
        case Add(l, r): return add_fn(fold(l,leaf_fn,add_fn,mul_fn,neg_fn),
                                     fold(r,leaf_fn,add_fn,mul_fn,neg_fn))
        case Mul(l, r): return mul_fn(fold(l,leaf_fn,add_fn,mul_fn,neg_fn),
                                     fold(r,leaf_fn,add_fn,mul_fn,neg_fn))
        case Neg(c): return neg_fn(fold(c,leaf_fn,add_fn,mul_fn,neg_fn))

# Build: -(3 + 4) * 2
tree = Mul(Neg(Add(Leaf(3), Leaf(4))), Leaf(2))

# Evaluate
print(f"Pattern match eval: {eval_match(tree)}")
print(f"Visitor eval:       {EvalVisitor().visit(tree)}")
print(f"Visitor pretty:     {PrettyPrintVisitor().visit(tree)}")
print(f"Fold eval:          {fold(tree, lambda v: v, lambda a,b: a+b, lambda a,b: a*b, lambda x: -x)}")

# Fold for count of nodes:
count = fold(tree, lambda _: 1, lambda a,b: a+b, lambda a,b: a+b, lambda x: x)
print(f"Fold node count:    {count}")

# Fold for maximum depth:
depth = fold(tree, lambda _: 1, lambda a,b: 1+max(a,b), lambda a,b: 1+max(a,b), lambda x: 1+x)
print(f"Fold depth:         {depth}")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

---

**Critical Thinking Questions**

1. Consider the following fold call:
   ```
   fold(tree, str, lambda a,b: f"(+ {a} {b})", lambda a,b: f"(* {a} {b})", lambda x: f"(- {x})")
   ```
   What would this produce for the tree `-(3 + 4) * 2`? What language's syntax does the output resemble, and what is significant about that language's use of that notation?

2. The visitor pattern makes it easy to *add new operations* (a new `Visitor` subclass) without modifying the `Leaf`, `Add`, `Mul`, or `Neg` classes. The pattern matching style makes it easy to *add new node types* (a new `case`) without modifying existing functions — but requires updating *every* match-based function when a new type appears. This tension has a name in PL design. What is it called? (Hint: it involves a "two-dimensional" design space and was named by Philip Wadler.)

3. Looking at the code for `eval_match` (12 lines with comments) versus `EvalVisitor` (6 lines), pattern matching is less verbose for *this specific case*. Under what circumstances would the visitor pattern start to look *less* verbose than pattern matching?

4. The `fold` function encodes the entire recursion structure once. `eval`, `count`, and `depth` are then just three different choices of functions to pass in — no recursion written by the caller at all. What does this tell you about the relationship between `fold` and the general concept of structural recursion over a datatype?

---

**Multiple Choice: Check Your Understanding**

What is a catamorphism?

- [( )] A pattern that matches on algebraic data types
- [(X)] A structural recursion that replaces each constructor of a datatype with a function, generalizing fold to arbitrary recursive types
- [( )] A recursive descent parser rule for a context-free grammar
- [( )] A method for detecting ambiguity in parsing

---

## Model 5: The Same Interpreter in Three Styles

A tree-walking interpreter, a CPS interpreter, and a bytecode-plus-VM compiler all compute the same thing — they implement the same semantics, just at different altitudes. Understanding why they are equivalent (and what differs) is the conceptual foundation for the rest of the course. Trace through the CPS version slowly: the continuation `k` is "what to do with this result when it is ready," and every recursive call hands off that baton rather than waiting for it.

> **Watch out!** The tree-walker in Style 1 uses `env={}` as a default mutable argument — a classic Python footgun. Default mutable arguments are shared across all calls that use the default, so if you ever mutate `env` in place (rather than constructing a new dict with `{**env, k: v}`), you will corrupt the shared default. The code here is safe because it never mutates `env` in place, but be careful when you adapt it.

> **The Problem:** Implement a tiny interpreter for a language with numbers, addition, and let-bindings.
>
> **The Claim:** "The interpreter" is an idea, not an implementation. Tree-walkers, CPS transformations, and bytecode compilers with stack VMs all implement the same semantics — and understanding *why* they are equivalent is the beginning of understanding what programs *mean*.

This is the model that most directly connects to what you will build in this course. A let-binding like `let x = 3 in let y = 4 in x + y` is a tiny programming language. It has variables, scoping, and arithmetic. Interpreting it correctly requires thinking carefully about environments. Three radically different strategies for doing so follow.

```python
from dataclasses import dataclass
from typing import Any

@dataclass
class Num: v: float
@dataclass
class Add: l: Any; r: Any
@dataclass
class Let: name: str; val: Any; body: Any
@dataclass
class Var: name: str

# === STYLE 1: Recursive tree-walker (most common in this course) ===
def interp1(node, env={}):
    if isinstance(node, Num): return node.v
    if isinstance(node, Var): return env[node.name]
    if isinstance(node, Add): return interp1(node.l, env) + interp1(node.r, env)
    if isinstance(node, Let):
        v = interp1(node.val, env)
        return interp1(node.body, {**env, node.name: v})

# === STYLE 2: Continuation-Passing Style (CPS) ===
# Each eval call takes a "k" (continuation) — what to do NEXT with the result
def interp2(node, env, k):
    if isinstance(node, Num): return k(node.v)
    if isinstance(node, Var): return k(env[node.name])
    if isinstance(node, Add):
        return interp2(node.l, env, lambda lv:
               interp2(node.r, env, lambda rv:
               k(lv + rv)))
    if isinstance(node, Let):
        return interp2(node.val, env, lambda v:
               interp2(node.body, {**env, node.name: v}, k))

# === STYLE 3: Compilation to bytecode then VM execution ===
def compile_to_bytecode(node, env_vars=None):
    """Compile to a list of (opcode, arg) instructions."""
    if env_vars is None: env_vars = {}
    instrs = []
    if isinstance(node, Num):
        instrs.append(('PUSH', node.v))
    elif isinstance(node, Var):
        instrs.append(('LOAD', node.name))
    elif isinstance(node, Add):
        instrs.extend(compile_to_bytecode(node.l))
        instrs.extend(compile_to_bytecode(node.r))
        instrs.append(('ADD', None))
    elif isinstance(node, Let):
        instrs.extend(compile_to_bytecode(node.val))
        instrs.append(('STORE', node.name))
        instrs.extend(compile_to_bytecode(node.body))
    return instrs

def run_bytecode(instrs, env=None):
    """Stack-based VM."""
    if env is None: env = {}
    stack = []
    for op, arg in instrs:
        if op == 'PUSH': stack.append(arg)
        elif op == 'LOAD': stack.append(env[arg])
        elif op == 'ADD': b, a = stack.pop(), stack.pop(); stack.append(a + b)
        elif op == 'STORE': env[arg] = stack.pop()
    return stack[-1] if stack else None

# Test program: let x = 3 in let y = 4 in x + y
program = Let("x", Num(3), Let("y", Num(4), Add(Var("x"), Var("y"))))

r1 = interp1(program)
r2 = interp2(program, {}, lambda x: x)
bytecode = compile_to_bytecode(program)
r3 = run_bytecode(bytecode)

print(f"Tree-walk:  {r1}")
print(f"CPS:        {r2}")
print(f"Bytecode:   {r3}")
print(f"Bytecode instructions: {bytecode}")
print(f"\nAll agree: {r1 == r2 == r3}")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

---

**Critical Thinking Questions**

1. In `interp2`, every recursive call immediately passes its result to `k` — there is no "waiting for a result" and then doing more work with it. In `interp1`, the call `interp1(node.l, env)` must complete and *return* before the addition `+ interp1(node.r, env)` can proceed. Why does the CPS transformation matter for *tail-call optimization*? Which version is more amenable to being compiled to a loop?

2. The bytecode version separates compilation (`compile_to_bytecode`) from execution (`run_bytecode`). For a program that will be run *once*, this is extra work. For a program run *many times* (like a hot loop in a JVM or a frequently-called function in V8), what concrete advantage does pre-compilation to bytecode give?

3. All three interpreters produce the same result for the same input program. This is not a coincidence: they implement the same *semantics*. The study of what programs mean, independently of how they are executed, is a formal field. What is it called? (Hint: there are several sub-disciplines including denotational, operational, and axiomatic approaches.)

4. Consider which interpreter style you would use in each scenario: (a) an interactive REPL where you type one expression at a time; (b) a production compiler for a language that needs to run on a JVM; (c) a concurrent language where multiple threads execute different parts of the program simultaneously. Justify each choice in one sentence.

---

**Multiple Choice: Check Your Understanding**

Which property of pure functions makes the array-oriented approach in Model 1 safe to parallelize?

- [(X)] No shared mutable state — each element can be processed independently without coordinating with other elements
- [( )] Lazy evaluation defers computation until needed, eliminating race conditions
- [( )] Type safety prevents data races at compile time
- [( )] Immutable types are allocated on the stack rather than the heap

---

The expression `reduce(lambda a,b: a+b, map(lambda x: x*x, filter(...)))` evaluates inside-out. Why?

- [( )] Python's optimizer reverses evaluation order for performance
- [( )] `filter` always runs before `map` regardless of nesting depth
- [(X)] `filter` must produce its entire output before `map` can process any of it, because Python's `map` and `filter` are eager in this context — each stage consumes the previous stage's complete output
- [( )] The lambda calculus dictates outermost-first reduction in all cases

---

What does the visitor pattern solve that pattern matching does not?

- [(X)] Adding new operations to a fixed, closed set of types without modifying the type definitions themselves
- [( )] Handling infinite data structures efficiently without running out of memory
- [( )] Avoiding ambiguity in context-free grammars
- [( )] Enabling tail-call optimization for deeply recursive traversals

---

## Exercises

**Exercise 1: Extend the Expression Tree**

Add a `Max` node to the tree from Model 4 (it takes the maximum of its two children's values). Implement this new node in all three traversal styles:

- **Pattern matching style**: add a new `case Max(left=l, right=r)` branch to `eval_match`.
- **Visitor style**: add `visit_Max` methods to both `EvalVisitor` and `PrettyPrintVisitor`.
- **Fold style**: add a `max_fn` parameter to `fold` and update all three call sites (eval, count, depth).

Which style required the most edits? Which required the fewest? Does your answer match your expectation from CTQ 2 in Model 4?

---

**Exercise 2: A Lazy Pipeline with itertools**

Implement the "sum of squares of even numbers from 1 to 100" problem from Model 1 using Python's `itertools` module. Specifically, use `itertools.count()` to generate an infinite stream of integers, `itertools.islice()` to take the first 100, `filter()` to keep even numbers, `map()` to square them, and `itertools.accumulate()` to compute a running sum. Take the last element of the accumulated result.

This is a *lazy pipeline* — no intermediate list is ever fully materialized. Contrast this with the NumPy array version: both avoid intermediate lists, but for different reasons. Explain the difference.

---

**Exercise 3: Add Loops to the Interpreter**

Add a `While` node to the interpreter in Model 5. A `While` node has two fields: `cond` (an expression that should evaluate to a number; nonzero means "keep looping") and `body` (an expression to evaluate repeatedly). You will also need a way to assign to variables — add an `Assign` node with `name` and `val` fields.

Implement `While` and `Assign` in all three styles:

- **Tree-walker**: straightforward — evaluate `cond`, loop while nonzero, evaluate `body` each iteration.
- **CPS**: this is the hard part. The continuation must be re-invoked on each iteration. Think carefully about what `k` means inside a loop.
- **Bytecode VM**: add `JUMP_IF_ZERO` and `JUMP` instructions. The compiler needs to emit a conditional branch, the loop body, and an unconditional back-jump.

---

**Exercise 4: Ten Languages, One Problem**

Look up and copy (with full attribution — author, language, source URL) implementations of the "sum of squares of even numbers from 1 to 100" problem in at least three languages you have never used before. Suggested languages to explore:

- **Haskell**: `sum [x^2 | x <- [1..100], even x]`
- **Erlang**: use list comprehensions
- **Clojure**: use `reduce`, `filter`, `map`, or `->>` threading macro
- **APL or J**: a one-liner using array primitives at `tryapl.org`
- **Forth**: a stack-based loop
- **Prolog**: use `aggregate_all` or `findall`

For each language you choose: (a) copy the implementation with attribution, (b) run it in an online REPL, and (c) write 2-3 sentences describing what makes the paradigm feel different from Python.

---

## Reflection

You have now seen the same computations expressed in more than five different ways. Write a 4-5 sentence reflection addressing the following: Which paradigm felt most "natural" to you, and what does your preference reveal about how you currently think about computation? Did any paradigm *surprise* you — did a solution appear more or less complex than you expected? Thinking ahead: as you encounter more languages this semester (Racket, Haskell, Prolog, possibly others), do you expect your sense of what is "natural" to shift? Will your answer to these questions change by December, and what would it mean if it did?

---

## Further Reading

The ideas in this activity connect to a rich literature. These are starting points, not assignments:

- **"Concepts, Techniques, and Models of Computer Programming"** — Peter Van Roy and Seif Haridi. The most comprehensive paradigm taxonomy in print. Chapter 4 covers declarative concurrency; Chapter 6 covers objects. If you want to understand why there are so many paradigms, this book explains.

- **"Why Functional Programming Matters"** — John Hughes, 1990. A short, readable paper that argues functional programming's real advantage is *composability*, not purity. Available free online. Read it before the end of the semester.

- **"Programming Language Pragmatics"** — Michael Scott. Chapter 6 covers control flow in depth; Chapter 11 covers functional languages. A solid reference for the technical material in this course.

- **APL in the browser**: `https://tryapl.org` — type `+/(2|⍳100)` and see what happens. APL's entire philosophy is that arrays are the right primitive, and operations on arrays should be single characters. It is either beautiful or horrifying, depending on your background.

- **Rosetta Code**: `https://rosettacode.org` — the same problem implemented in hundreds of languages. Look up "Fibonacci sequence" or "sorting algorithms" and browse. You will find things that don't look like programming at all.

- **"Structure and Interpretation of Computer Programs"** — Abelson, Sussman, Sussman. The classic MIT textbook. The interpreter in Model 5 is a minimal version of what you build in Chapters 3 and 4. Available free at `https://mitpress.mit.edu/sites/default/files/sicp/index.html`.
