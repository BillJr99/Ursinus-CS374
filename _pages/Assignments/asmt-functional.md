---
layout: assignment
permalink: /Assignments/Functional
title: "CS374: Principles of Programming Languages - Functional Programming"

info:
  coursenum: CS374
  purpose: "To build fluency in the functional paradigm — pure and higher-order functions, recursive data structures with generic fold, closures, and lazy generators — as a design option your team will weigh for its own language."
  tilt:
    task: "Work through four parts: pure functions and combinators, recursive trees and linked lists with generic map/fold, closures and function factories, and lazy generator pipelines."
    criteria: "Assessed on honoring the no-loop and no-assignment constraints, genuinely generic tree and list operations, and infinite generators demonstrated without hanging, each part worth 25 points; see the rubric below for the full breakdown."
  points: 100
  goals:
    - To write pure functions and higher-order functions in Python using map, filter, reduce, and recursion without loops or assignment
    - To implement recursive data structures including trees and linked lists with map and fold operations
    - To build closures and function factories that capture and return behavior
    - To implement lazy sequences using Python generators and compare with strict evaluation
  rubric:
    - weight: 25
      description: "Pure Functions and Higher-Order Functions (Goal 1: write pure functions and higher-order functions using map, filter, reduce, and recursion without loops or assignment)"
      preemerging: The solutions rely pervasively on loops and assignment, or fail to run due to major errors
      beginning: Most solutions run but several use loops or assignment where the directions forbid them, or combinator usage is incorrect (e.g., map returns a map object that is never consumed)
      progressing: All solutions are correct and respect the no-loop and no-assignment constraints, but combinators are used awkwardly (e.g., reduce used where map would suffice, or lambda where a named function would be clearer)
      proficient: Correct solutions use map, filter, reduce, and recursion idiomatically throughout with no loops or assignment in solution bodies — demonstrating Goal 1; the compose function works for any arity; my_map and my_reduce are property-tested against the built-ins; and each function is documented with its type signature and one-sentence description
    - weight: 25
      description: "Recursive Data Structures (Goal 2: implement recursive data structures including trees and linked lists with map and fold operations)"
      preemerging: The tree or linked-list structures are missing, or the recursive cases do not terminate
      beginning: The structures are defined but tree_map or tree_fold is missing, or the linked-list fold does not handle the empty-list base case
      progressing: All structures and operations are implemented correctly for the provided test cases, but the functions are not generic — e.g., tree_fold is hardcoded to addition rather than taking a combining function
      proficient: Both the binary tree and the linked-list structures are defined as dataclasses; tree_map, tree_fold, list_map, and list_fold all take a function argument and work for any operation — demonstrating Goal 2; flatten and depth are implemented in terms of fold; and all operations are tested with at least four inputs including edge cases (empty list, single-node tree)
    - weight: 25
      description: "Closures and Function Factories (Goal 3: build closures and function factories that capture and return behavior)"
      preemerging: The closure-based functions are not implemented, or closures are not used — instead the factories use global state
      beginning: Closures are used but one or more factories are incorrect — e.g., the adder factory returns the wrong sum, or the memoizer does not cache correctly
      progressing: All factories work correctly for the provided test cases, but the memoizer does not handle multiple arguments, or the decorator version of memoize is not provided
      proficient: All five closure-based functions (adder, multiplier, counter, memoize, once) are implemented correctly using closures — demonstrating Goal 3; memoize works for any hashable arguments; the decorator pattern is demonstrated; and the writeup includes a diagram showing what each closure captures and why the captured variable does not leak between independent factory calls
    - weight: 25
      description: "Lazy Sequences with Generators (Goal 4: implement lazy sequences using Python generators and compare with strict evaluation)"
      preemerging: No generators are implemented, or all functions use lists and eager evaluation throughout
      beginning: Some generator functions are implemented but they do not use yield, or they materialize the entire sequence in memory before yielding
      progressing: All generator functions are implemented correctly with yield, but take() or the pipeline composition is missing, or infinite sequences are not demonstrated
      proficient: All five generator functions (naturals, fibonacci, take, gen_map, gen_filter) are implemented with yield and infinite sequences are demonstrated without hanging — demonstrating Goal 4; lazy pipelines are built using gen_map and gen_filter; the strict vs. lazy comparison demonstrates a concrete performance difference; and the writeup explains what would happen if naturals() used a list instead of yield
  readings:
    - rtitle: "Functional Programming Activity"
      rlink: "https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374-Fall2026/gh-pages/_pages/Activities/liascript-functional.md"
    - rtitle: "Scheme Activity"
      rlink: "https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374-Fall2026/gh-pages/_pages/Activities/liascript-scheme.md"
    - rtitle: "Lambda Calculus Part 2 Activity"
      rlink: "https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374-Fall2026/gh-pages/_pages/Activities/liascript-lambdacalculus2.md"

tags:
  - functional
  - closures
  - generators
  - higher-order-functions

---

This assignment exercises the functional paradigm in Python: pure functions, higher-order combinators, recursive data structures, closures, and lazy generators. The constraints are the content — where the directions say no loops and no assignment statements within the solution logic, the constraint is teaching you the paradigm shift from imperative to functional thinking.

---

## Getting Started

### Environment and Setup

You need Python 3.10+ and the standard library only — `functools` (for `reduce`), `dataclasses`, and `typing`. Create the deliverable files up front so each part has a home:

```
higher_order.py           # Part 1
recursive_structures.py   # Part 2
closures.py               # Part 3
generators.py             # Part 4
test_functional.py        # assertions for all four parts
```

### Your First 30 Minutes

Write `total_length` from Step 1a — it exercises the whole Part 1 toolkit in one line of thinking: `filter` to keep words longer than three letters, `map` to turn words into lengths, `reduce` (or `sum`) to combine them.

```python
from functools import reduce

# total_length: list[str] -> int
def total_length(words):
    return reduce(lambda acc, n: acc + n,
                  map(len, filter(lambda w: len(w) > 3, words)),
                  0)

assert total_length(["hi", "hello", "world", "it"]) == 10
```

Notice what is *absent*: no loop, no accumulator variable, no assignment. If you catch yourself reaching for `total = 0` and a `for` loop, that instinct is exactly what this assignment retrains — restate the problem as a chain of transformations instead.

### Suggested Pacing

This assignment is handed out on Thursday of week 11 and due on Thursday of week 12 — a one-week turnaround, so treat each part as a single sitting:

| Checkpoint | You should have |
|------------|----------------|
| Week 11 (Thu) — assigned | Part 1 complete: combinators, `compose`, and property-tested `my_map`/`my_reduce` |
| Weekend | Part 2 complete: tree and linked-list operations with edge-case tests |
| Week 12 (Tue) | Part 3 complete: all five closure factories including the `memoize` decorator |
| Week 12 (Thu) — due | Part 4 complete: lazy pipeline and timing comparison; writeup and ZIP submitted |

---

## Part 1: Pure Functions and Higher-Order Functions (25 points)

**The constraints for this entire part:** no `for` loops, no `while` loops, no assignment statements (no `=`) inside solution function bodies. You may use `map`, `filter`, `functools.reduce`, `lambda`, and recursion. You may use `return`.

### Step 1a: Basic Combinators

Implement and test each function. Each must be accompanied by its type signature (as a comment) and at least three test assertions.

**`total_length(words: list[str]) -> int`**  
Return the total number of characters across all words longer than three letters.  
Example: `total_length(["hi", "hello", "world", "it"])` → `10` (hello=5, world=5).

**`product_of_odds(nums: list[int]) -> int`**  
Return the product of all odd numbers. Define and document the empty-product case (return `1` for the empty list — this is mathematically the multiplicative identity).  
Example: `product_of_odds([1, 2, 3, 4, 5])` → `15`.

**`longest(words: list[str]) -> str`**  
Return the longest word via a single `reduce`. On a tie, return the first one encountered (left-to-right). Raise `ValueError` if the list is empty.  
Example: `longest(["cat", "elephant", "dog"])` → `"elephant"`.

**`flatten_once(lists: list[list]) -> list`**  
Flatten one level of nesting using `reduce`. Do not use `itertools`.  
Example: `flatten_once([[1,2], [3], [4,5]])` → `[1, 2, 3, 4, 5]`.

### Step 1b: Function Composition

**`compose(*fns)`**  
Return a new function that applies the given functions left-to-right (first function is applied first).

```python
strip_lower_len = compose(str.strip, str.lower, len)
assert strip_lower_len("  Hello  ") == 5
```

Use `functools.reduce` internally. Do not use a loop.

**Worked example:** `compose(f, g, h)(x)` = `h(g(f(x)))`.

### Step 1c: Recursive my_map and my_reduce

Implement `my_map(f, xs)` and `my_reduce(f, xs, seed)` recursively — **no loops, no list comprehensions inside the body**.

```python
def my_map(f, xs):
    """Base case: empty list → []. Recursive: f(head) consed onto my_map(f, tail)."""
    if not xs:
        return []
    return [f(xs[0])] + my_map(f, xs[1:])

def my_reduce(f, xs, seed):
    """Base case: empty list → seed. Recursive: apply f to seed and head, recurse on tail."""
    if not xs:
        return seed
    return my_reduce(f, xs[1:], f(seed, xs[0]))
```

**Property-test against the built-ins** on at least five inputs each:

```python
from functools import reduce
test_lists = [[1,2,3], [], [5], [1,2,3,4,5], [-1,0,1]]
for lst in test_lists:
    assert my_map(lambda x: x*2, lst) == list(map(lambda x: x*2, lst))
    assert my_reduce(lambda a,b: a+b, lst, 0) == reduce(lambda a,b: a+b, lst, 0)
print("All my_map and my_reduce properties hold.")
```

---

## Part 2: Recursive Data Structures (25 points)

### Binary Tree

Define a `BTree` dataclass with `Optional` left and right children:

```python
from dataclasses import dataclass
from typing import Optional, Any

@dataclass
class BTree:
    value: Any
    left: Optional['BTree'] = None
    right: Optional['BTree'] = None
```

**`tree_map(f, tree: Optional[BTree]) -> Optional[BTree]`**  
Apply `f` to every node's value, returning a new tree with the same structure. The original tree must not be modified (pure function).  
Example: `tree_map(lambda x: x*2, BTree(1, BTree(2), BTree(3)))` → `BTree(2, BTree(4), BTree(6))`.

**`tree_fold(f, tree: Optional[BTree], seed)`**  
Reduce the tree to a single value by applying `f(left_result, value, right_result)`. For a `None` node, return `seed`.  
Example with `f = lambda l, v, r: l + v + r` and seed `0`: computes the sum of all node values.

**`tree_depth(tree: Optional[BTree]) -> int`**  
Implement in terms of `tree_fold`. The depth of `None` is `0`; the depth of a leaf is `1`.

**`tree_flatten(tree: Optional[BTree]) -> list`**  
Return all node values in in-order traversal (left, root, right), implemented using `tree_fold`.

**Test trees to use:**
- Empty: `None` → all functions return seed/identity value
- Single node: `BTree(42)` → map doubles it, fold sums it, depth is 1
- Full tree: `BTree(1, BTree(2, BTree(4), BTree(5)), BTree(3))`
- Right-skewed: `BTree(1, None, BTree(2, None, BTree(3)))`

### Linked List

Define a linked-list type:

```python
@dataclass
class LLNode:
    head: Any
    tail: Optional['LLNode'] = None  # None represents the empty list
```

**`list_map(f, node: Optional[LLNode]) -> Optional[LLNode]`**  
Apply `f` to every element, returning a new linked list.

**`list_fold(f, node: Optional[LLNode], seed)`**  
Left fold: accumulate from left to right.  
Example: `list_fold(lambda acc, x: acc + x, LLNode(1, LLNode(2, LLNode(3))), 0)` → `6`.

**`list_to_python(node: Optional[LLNode]) -> list`**  
Convert to a Python list, implemented via `list_fold`.

**`list_from_python(lst: list) -> Optional[LLNode]`**  
Convert from a Python list to a linked list, implemented via `my_reduce` from Part 1 (no loops).

---

## Part 3: Closures and Function Factories (25 points)

### What is a Closure?

A closure is a function that *captures* variables from its enclosing scope. In Python, when a factory function creates and returns an inner function, the inner function retains access to the factory's local variables even after the factory has returned. This is the mechanism behind many design patterns.

### Step 3a: Simple Factories

**`make_adder(n: int) -> Callable`**  
Return a function that adds `n` to its argument. Each call to `make_adder` must produce an independent function.

```python
add5 = make_adder(5)
add10 = make_adder(10)
assert add5(3) == 8
assert add10(3) == 13
assert add5(add10(0)) == 15
```

**`make_multiplier(n: int) -> Callable`**  
Return a function that multiplies its argument by `n`.

**`make_between(lo: int, hi: int) -> Callable`**  
Return a predicate that tests whether its argument is in the closed interval `[lo, hi]`.

```python
is_teen = make_between(13, 19)
assert is_teen(15) == True
assert is_teen(20) == False
```

### Step 3b: Stateful Closures

**`make_counter(start: int = 0) -> Callable`**  
Return a function that, on each call, returns the next integer starting from `start`. Each counter is independent.

```python
c1 = make_counter()
c2 = make_counter(10)
assert c1() == 0
assert c1() == 1
assert c2() == 10
assert c1() == 2   # c1 and c2 do not share state
```

Hint: use a mutable default argument or a list to store state (since Python's `nonlocal` works but a list also demonstrates the technique).

**`make_once(f: Callable) -> Callable`**  
Return a wrapper that calls `f` at most once. On the first call, compute and cache the result. On subsequent calls, return the cached result without calling `f` again.

```python
side_effects = []
def expensive():
    side_effects.append("called")
    return 42

once_expensive = make_once(expensive)
assert once_expensive() == 42
assert once_expensive() == 42
assert len(side_effects) == 1  # f was only called once
```

### Step 3c: Memoization

**`memoize(f: Callable) -> Callable`**  
Return a wrapped version of `f` that caches return values by argument. Use a dictionary as the cache. Works for any hashable arguments.

```python
def slow_square(n):
    import time; time.sleep(0.001)  # simulate work
    return n * n

fast_square = memoize(slow_square)
assert fast_square(5) == 25
assert fast_square(5) == 25   # from cache; no sleep
```

**Decorator form:** Show that `memoize` can be used as a decorator:

```python
@memoize
def fib(n):
    if n <= 1: return n
    return fib(n-1) + fib(n-2)

assert fib(30) == 832040
```

**In your writeup:** Draw an ASCII diagram (or describe in prose) showing what each closure returned by `make_adder(5)` and `make_adder(10)` captures internally, and why the two closures do not share state.

---

## Part 4: Lazy Sequences with Generators (25 points)

### Why Lazy Evaluation?

A strict (eager) evaluation strategy computes every element of a sequence immediately. A lazy strategy computes elements only when demanded. This matters for infinite sequences (which cannot be stored in memory) and for pipelines where early termination saves work.

### Step 4a: Infinite Generators

**`naturals(start: int = 0) -> Iterator[int]`**  
Yield the natural numbers `start, start+1, start+2, ...` forever.

```python
def naturals(start=0):
    n = start
    while True:
        yield n
        n += 1
```

**`fibonacci() -> Iterator[int]`**  
Yield the Fibonacci sequence `0, 1, 1, 2, 3, 5, 8, ...` forever.

Both generators must run indefinitely without consuming more than O(1) extra memory. Do not call `list()` on them.

### Step 4b: Sequence Utilities

**`take(n: int, it: Iterator) -> list`**  
Consume and return the first `n` elements of any iterator as a list.

```python
assert take(5, naturals()) == [0, 1, 2, 3, 4]
assert take(8, fibonacci()) == [0, 1, 1, 2, 3, 5, 8, 13]
```

**`gen_map(f: Callable, it: Iterator) -> Iterator`**  
Lazily apply `f` to each element of `it`, yielding results one at a time.

```python
squares = gen_map(lambda x: x**2, naturals(1))
assert take(5, squares) == [1, 4, 9, 16, 25]
```

**`gen_filter(pred: Callable, it: Iterator) -> Iterator`**  
Lazily yield only elements of `it` for which `pred` is truthy.

```python
evens = gen_filter(lambda x: x % 2 == 0, naturals())
assert take(5, evens) == [0, 2, 4, 6, 8]
```

### Step 4c: Lazy Pipeline

Build a pipeline that computes the first 10 perfect squares that are also even, using only `gen_map`, `gen_filter`, `naturals`, and `take` — no list comprehensions, no intermediate lists:

```python
result = take(
    10,
    gen_filter(
        lambda x: x % 2 == 0,
        gen_map(lambda x: x**2, naturals(1))
    )
)
assert result == [4, 16, 36, 64, 100, 144, 196, 256, 324, 400]
```

### Step 4d: Strict vs. Lazy Performance Comparison

Write a brief comparison demonstrating that lazy evaluation avoids unnecessary work. Compute the first element greater than 1000 in the Fibonacci sequence two ways:

```python
import time

# Strict: generate a large list first
start = time.perf_counter()
fibs_list = [f for f in ... ]  # up to some large N
first_over_1000_strict = next(f for f in fibs_list if f > 1000)
strict_time = time.perf_counter() - start

# Lazy: generate and test one at a time
start = time.perf_counter()
first_over_1000_lazy = next(f for f in fibonacci() if f > 1000)
lazy_time = time.perf_counter() - start

print(f"Both found: {first_over_1000_strict} == {first_over_1000_lazy}")
print(f"Strict time: {strict_time:.6f}s, Lazy time: {lazy_time:.6f}s")
```

In your writeup, explain what would happen if `naturals()` used a list instead of `yield`, and why that would make the pipeline in Step 4c impossible to run.

---

## Deliverables

Submit a ZIP containing:
- `higher_order.py` — Part 1 (pure functions and combinators)
- `recursive_structures.py` — Part 2 (tree and linked-list operations)
- `closures.py` — Part 3 (function factories and memoization)
- `generators.py` — Part 4 (lazy sequences)
- `test_functional.py` — all tests for all four parts with assertions
- `test_output.txt` — output of running the test file (all tests passing)
- `readme.md` — approximately one page including the closure diagram, the strict vs. lazy analysis, and the comparative reflection

Ensure reproducibility by listing your Python version.

---

## Grading Breakdown

| Component | Points |
|-----------|--------|
| Part 1: Pure Functions and Higher-Order Functions | 25 |
| Part 2: Recursive Data Structures | 25 |
| Part 3: Closures and Function Factories | 25 |
| Part 4: Lazy Sequences with Generators | 25 |
| **Total** | **100** |

---

## Reflection Prompts

- Which constraint (no loops, or no assignment) changed your thinking more, and what did it force you to see?
- In Part 2, both `tree_depth` and `tree_flatten` were implemented in terms of `tree_fold`. What does this tell you about the relationship between fold and other recursive operations?
- In Part 3, two independent closures from `make_adder(5)` and `make_adder(10)` capture different values of `n`. Now consider: what would happen to the closure if `n` were a mutable object and the factory mutated it after creating the inner function? Write a short code example demonstrating the hazard and the fix.
- After completing Part 4, compare generators in Python to the concept of lazy evaluation in Haskell (if you have encountered it). What is the key semantic difference?
- If collaboration with a buddy was permitted, did you work with a buddy on this assignment? If so, who? If not, do you certify that this submission represents your own original work? Please identify any and all portions of your submission that were not originally written by you.
- Approximately how many hours it took you to finish this assignment (I will not judge you for this at all — I am simply using it to gauge if the assignments are too easy or hard)?
