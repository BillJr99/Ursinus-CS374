<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://github.com/BillJr99/Ursinus-CS374-Fall2026/blob/gh-pages/_pages/Activities/liascript-functional.md

import: https://raw.githubusercontent.com/liascript/CodeRunner/master/README.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

# Functional Programming

## Learning Goals

By the end of this activity, you will be able to:

- Distinguish pure functions from impure ones and explain why purity enables referential transparency, testability, and safe parallelism
- Apply `map`, `filter`, and `reduce` to transform and aggregate data without explicit loops
- Write higher-order functions that accept and return other functions, including anonymous `lambda` expressions
- Use currying and partial application to build specialized functions from general ones
- Implement recursive solutions to iterative problems without using mutable state or assignment

Unit 3 turns from building languages to inhabiting one paradigm deeply. We practice **functional programming** in Python — `lambda`, `map`, `filter`, `reduce` — with the discipline of **purity** and **immutability**, because the functional toolkit is both a daily professional skill (data pipelines, modern Java/JavaScript/Rust) and the bridge to Scheme and the lambda calculus ahead.

Arc: **purity and why it pays → the big three combinators → higher-order thinking → currying and partial application → recursion without loops**

---

## Directions and Group Roles

Work in your POGIL team with rotated roles (**Manager**, **Recorder**, **Presenter**, **Reflector**). Consider each model and question individually first, then discuss with your group.

---

# Part I: Purity

## 1. Functions Like Mathematics Meant

**A pure function's output depends only on its inputs, and it changes nothing outside itself.** No mutation of arguments, no global reads or writes, no printing, no randomness. Purity buys three concrete powers:

1. **Substitution** — a call can be replaced by its result anywhere (referential transparency)
2. **Testability** — no setup, no teardown: just input → expected output
3. **Parallel safety** — no shared state means no interference

**Immutability is purity's partner.** Functional style does not modify a list; it produces a new one.

```python  liascript
# Spot the impure function — run this and observe the difference
def pure_double(xs):
    return [x * 2 for x in xs]    # produces a NEW list

def impure_double(xs):
    for i in range(len(xs)):
        xs[i] *= 2                # mutates the ARGUMENT
    return xs

original = [1, 2, 3, 4, 5]

result1 = pure_double(original)
print(f"After pure_double: original={original}, result={result1}")

result2 = impure_double(original)
print(f"After impure_double: original={original}, result={result2}")

# Surprise: original has changed! Try calling impure_double twice:
data = [1, 2, 3]
impure_double(data)
impure_double(data)
print(f"data after two calls to impure_double: {data}")   # [4, 8, 12] — not [4, 4, 4]!
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

**Critical Thinking Questions (CTQs)**

> **CTQ 1.1** `pure_double` and `impure_double` return the same value for `[1, 2, 3]`, yet they differ fundamentally. What is the difference, and why does it matter when a function is called more than once?

> **CTQ 1.2** The rule "calling a pure function twice with the same input always gives the same output" is called **referential transparency**. Which functions in the code above have this property? Which do not?

> **CTQ 1.3** Could `pure_double` safely run on two halves of the list in parallel and merge the results? Could `impure_double`? Explain.

---

## Model 1: The Purity Audit

```python  liascript
import random

LOG_LINES = ["startup", "config loaded"]  # module global

def f1(xs):           return sorted(xs)
def f2(xs):           xs.sort(); return xs
total = 0
def f3(x):            global total; total += x; return total
def f4(x):            return x + len(LOG_LINES)   # reads a global
def f5(x, factor=2):  return x * factor
def f6():             return random.random()

# Test each
data = [3, 1, 4, 1, 5]
print(f"f1([3,1,4,1,5]) = {f1(data)}, data after = {data}")
print(f"f2([3,1,4,1,5]) = {f2(data)}, data after = {data}")  # data mutated!
print(f"f3(10) twice: {f3(10)}, {f3(10)}")     # different each time!
print(f"f4(0) = {f4(0)}")
print(f"f5(7) = {f5(7)}")
print(f"f6() twice: {f6():.4f}, {f6():.4f}")   # random
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

> **CTQ 1.4** Classify each function as pure or impure. For each impure one, name the exact disqualifying feature.

> **CTQ 1.5** `f4` reads but never writes a global. What referential transparency property does it still forfeit? Construct a test that would *pass* today but *fail* after appending to `LOG_LINES`.

---

# Part II: The Big Three Combinators

## 2. Map, Filter, Reduce

$$\text{map}(f, [x_1, \dots, x_n]) = [f(x_1), \dots, f(x_n)]$$

$$\text{filter}(p, [x_1, \dots, x_n]) = [x_i \mid p(x_i) = \text{True}]$$

$$\text{reduce}(\oplus, [x_1, \dots, x_n], z) = ((z \oplus x_1) \oplus x_2) \oplus \cdots \oplus x_n$$

Each replaces a loop pattern you have written a hundred times. The key: `map` *transforms* every element, `filter` *selects* elements, `reduce` *collapses* a list to one value.

```python  liascript
from functools import reduce

scores = [88, 92, 54, 71, 67, 95, 49, 83]

# map: transform every element
curved = list(map(lambda s: min(s + 5, 100), scores))
print("curved:  ", curved)

# filter: select elements satisfying a predicate
passing = list(filter(lambda s: s >= 70, curved))
print("passing: ", passing)

# reduce: fold to one value
total = reduce(lambda acc, s: acc + s, passing, 0)
mean  = total / len(passing)
print(f"mean of passing: {mean:.1f}")

# The same pipeline composed in one expression:
pipeline_result = reduce(
    lambda acc, s: acc + s,
    filter(lambda s: s >= 70,
           map(lambda s: min(s + 5, 100), scores)),
    0)
print(f"pipeline result: {pipeline_result}")

# reduce builds ANY aggregate: maximum score
max_score = reduce(lambda a, b: a if a > b else b, scores)
print(f"max score: {max_score}")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

> **CTQ 2.1** Rewrite the `map` call as an explicit `for` loop. What bookkeeping did `map` absorb? Do the same for `filter`.

> **CTQ 2.2** `reduce` with `lambda a, b: a - b` over `[10, 3, 2]` and seed 0: compute it by hand using the left-fold formula `((0 - 10) - 3) - 2`. What is the result? Now try seed 10 with `[3, 2]`. What does "left fold" mean?

> **CTQ 2.3** The pipeline composes `map`, `filter`, and `reduce` in a *single expression* with no intermediate names. Name one benefit and one honest cost for a reader.

---

## Model 2: Comprehensions vs. Combinators

Python offers *list comprehensions* as an alternative syntax for map+filter:

```python  liascript
scores = [88, 92, 54, 71, 67, 95, 49, 83]

# Using map + filter
via_combinators = list(filter(lambda s: s >= 70, map(lambda s: min(s + 5, 100), scores)))

# Using list comprehension
via_comprehension = [min(s + 5, 100) for s in scores if min(s + 5, 100) >= 70]

# Are they the same?
print(f"combinators:   {via_combinators}")
print(f"comprehension: {via_comprehension}")
print(f"equal: {via_combinators == via_comprehension}")

# Generator expression (lazy — no list built until needed):
gen = (min(s + 5, 100) for s in scores if min(s + 5, 100) >= 70)
print(f"generator sum: {sum(gen)}")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

> **CTQ 2.4** The comprehension evaluates `min(s + 5, 100)` *twice* for each element. How would you fix this using a nested comprehension or a helper function?

> **CTQ 2.5** Generators are *lazy* — they produce elements one at a time on demand. What advantage does this have for processing a file with 10 million lines?

---

# Part III: Higher-Order Functions

## 3. Functions That Make Functions

A **higher-order function** takes functions as arguments *or* returns functions. Today we also *return* them — creating parameterized behavior without classes.

```python  liascript
# make_adder returns a function; each call creates a new closure
def make_adder(n):
    return lambda x: x + n

add5 = make_adder(5)
add10 = make_adder(10)
print(f"add5(3) = {add5(3)}")       # 8
print(f"add10(3) = {add10(3)}")     # 13
print(f"add5(add10(1)) = {add5(add10(1))}")  # 16

# Function composition
def compose(f, g):
    return lambda x: f(g(x))

# Pipeline of transformations
def pipeline(*fns):
    return lambda x: reduce(lambda v, f: f(v), fns, x)

from functools import reduce

clean = pipeline(str.strip, str.lower, lambda s: s.replace(' ', '_'))
print(clean("  Hello World  "))   # "hello_world"

# twice: apply a function twice
twice = lambda f: lambda x: f(f(x))
add5_twice = twice(add5)
print(f"add5 twice applied to 0: {add5_twice(0)}")   # 10
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

[[MC]]
`compose = lambda f, g: lambda x: f(g(x))` is a higher-order function because it:

    [( )] Uses lambda syntax twice
    [( )] Avoids mutation
    [(x)] Both consumes functions as arguments and produces a function as its result
    [( )] Runs in logarithmic time

---

## 4. Partial Application and Currying

**Partial application**: fix some arguments of a function to produce a simpler one.

**Currying**: transform a function `f(a, b)` into `f(a)(b)` — a chain of single-argument functions.

```python  liascript
from functools import partial

# Partial application with functools.partial
def power(base, exp):
    return base ** exp

square = partial(power, exp=2)
cube   = partial(power, exp=3)

print(f"square(5) = {square(5)}")
print(f"cube(3)   = {cube(3)}")

# Manual currying
def curried_add(a):
    return lambda b: a + b

add = curried_add
print(f"add(3)(4) = {add(3)(4)}")

# Curried map: fix the function, get a list transformer
def map_with(f):
    return lambda lst: list(map(f, lst))

double_all = map_with(lambda x: x * 2)
negate_all = map_with(lambda x: -x)

data = [1, 2, 3, 4, 5]
print(f"double_all({data}) = {double_all(data)}")
print(f"negate_all({data}) = {negate_all(data)}")

# Point-free style: compose transformers without naming the data
from functools import reduce
process = lambda lst: reduce(lambda a, b: a + b,
                             filter(lambda x: x > 0,
                                    map(lambda x: x - 2, lst)), 0)
print(f"process({data}) = {process(data)}")   # sum of elements > 0 after subtracting 2
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

> **CTQ 3.1** `map_with(lambda x: x * 2)` returns a function. How is this different from `map(lambda x: x * 2, data)`? When is the list transformer version more useful?

> **CTQ 3.2** Haskell functions are automatically curried — `f x y` is always `(f x) y`. What advantage does automatic currying give you for composing functions?

---

# Part IV: Recursion Without Loops

## 5. Thinking Recursively

In pure functional style, **there are no loops** — only recursion. Every loop corresponds to a recursive function:

```python  liascript
import sys
sys.setrecursionlimit(10000)

# Implement map recursively (no loops!)
def my_map(f, lst):
    if not lst:
        return []
    return [f(lst[0])] + my_map(f, lst[1:])

# Implement filter recursively
def my_filter(pred, lst):
    if not lst:
        return []
    head, *tail = lst
    if pred(head):
        return [head] + my_filter(pred, tail)
    return my_filter(pred, tail)

# Implement reduce recursively
def my_reduce(f, lst, init):
    if not lst:
        return init
    head, *tail = lst
    return my_reduce(f, tail, f(init, head))

# Test all three
nums = [1, 2, 3, 4, 5]
print(f"my_map(x²):     {my_map(lambda x: x**2, nums)}")
print(f"my_filter(odd): {my_filter(lambda x: x % 2 != 0, nums)}")
print(f"my_reduce(+):   {my_reduce(lambda a, b: a + b, nums, 0)}")

# Recursive sum — no loop, no accumulator variable
def rsum(lst):
    if not lst: return 0
    return lst[0] + rsum(lst[1:])

print(f"rsum({nums}) = {rsum(nums)}")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

> **CTQ 5.1** Each recursive function has a base case and a recursive case. Identify them for `my_map`. What guarantees the recursion terminates?

> **CTQ 5.2** `my_reduce(f, lst, init)` uses `init` as an accumulator. Trace `my_reduce(lambda a, b: a - b, [3, 2, 1], 10)` step by step. What is the result?

> **CTQ 5.3** Python has a default recursion limit of 1000. Haskell compiles tail-recursive functions to loops. What is a "tail call," and why can't Python's `rsum` be optimized this way?

---

## 6. Mutual Recursion and Structural Recursion

```python  liascript
import sys
sys.setrecursionlimit(10000)

# Mutual recursion: is_even and is_odd define each other
def is_even(n):
    if n == 0: return True
    return is_odd(n - 1)

def is_odd(n):
    if n == 0: return False
    return is_even(n - 1)

print(f"is_even(10) = {is_even(10)}")
print(f"is_odd(7)   = {is_odd(7)}")

# Structural recursion over a tree (nested lists)
def tree_sum(tree):
    """Sum all numbers in a nested list tree."""
    if isinstance(tree, (int, float)):
        return tree
    return sum(tree_sum(child) for child in tree)

nested = [1, [2, [3, 4], 5], [6, 7]]
print(f"tree_sum({nested}) = {tree_sum(nested)}")

# Flatten a nested list
def flatten(lst):
    if not lst: return []
    head, *tail = lst
    if isinstance(head, list):
        return flatten(head) + flatten(tail)
    return [head] + flatten(tail)

print(f"flatten({nested}) = {flatten(nested)}")

# Merge sort: purely functional, no mutation
def merge(xs, ys):
    if not xs: return ys
    if not ys: return xs
    if xs[0] <= ys[0]:
        return [xs[0]] + merge(xs[1:], ys)
    return [ys[0]] + merge(xs, ys[1:])

def mergesort(lst):
    if len(lst) <= 1: return lst
    mid = len(lst) // 2
    return merge(mergesort(lst[:mid]), mergesort(lst[mid:]))

print(f"mergesort([5,2,8,1,9,3]) = {mergesort([5,2,8,1,9,3])}")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

> **CTQ 6.1** `tree_sum` recurses on the *structure* of the data, not a loop counter. What property of the tree guarantees this terminates?

> **CTQ 6.2** `mergesort` produces new lists at each step — it never mutates the input. What is the memory cost compared to in-place quicksort? Is purity free?

---

## Multiple Choice

Which of the following is a *pure* function?

    [( )] `def f(lst): lst.append(1); return lst`
    [(x)] `def f(lst): return lst + [1]`
    [( )] `def f(x): print(x); return x`
    [( )] `def f(): return time.time()`

---

## Exercises

### Exercise 1 — Loop Exorcism (15 min)
Rewrite each using `map`/`filter`/`reduce` with no loops or assignments:
- (a) lengths of all words longer than 3 in a sentence
- (b) product of all odd numbers in a list (use `reduce`)
- (c) word count of a string: split, map each word to 1, reduce with +

### Exercise 2 — Higher-Order Toolkit (15 min)
Implement and test:
- `compose(f, g)` — apply g then f
- `twice(f)` — apply f two times
- `n_times(f, n)` — apply f exactly n times
- `pipeline(*fns)` — compose any number left-to-right

Demo: `pipeline(str.strip, str.lower, lambda s: s.split())` on `"  Hello World  "`.

### Exercise 3 — My Map and Reduce (20 min)
Implement `my_map` and `my_reduce` recursively (no `for`/`while`). Test against the built-ins on 5 inputs each. Then implement `my_zip(lst1, lst2)` and `my_flatten(nested)` recursively.

### Exercise 4 — Purity Refactor (20 min)
Take the impure `f2` and `f3` from Model 1, refactor them to be pure, and write tests that pass for the pure version but fail (or behave unexpectedly) for the impure version.

### Exercise 5 — No-Assignment Challenge (25 min)
Compute the average word length of a paragraph using **exactly one expression** — no statements, no intermediate variable names (except the function parameter). Then discuss: when does point-free style help, and when does it hurt readability?

---

## Reflection Prompt

Purity forbids a function from leaving traces on the world — which makes it trustworthy, but also means it *cannot do anything* (no printing, no saving) without breaking the rules. Real programs must do things. Where should the impurity live in a well-organized program? Name a non-programming system (kitchen, lab, organization) organized the same way.

---

## Further Reading

- **"Why Functional Programming Matters"** — John Hughes (1990): the classic argument that *composition* is the point: https://www.cs.kent.ac.uk/people/staff/dat/miranda/whyfp90.pdf
- **SICP Sections 1.1–1.3** — Abelson & Sussman: the functional core
- **Python `functools` documentation**: `reduce`, `partial`, `lru_cache`
- **Haskell Tour** — for seeing what pure FP looks like at full scale: https://www.haskell.org/tutorial/
- **"Structure and Interpretation of Computer Programs"** — online at https://mitp-content-server.mit.edu/books/content/sectbyfn/books_pubs/6515/sicp.pdf
