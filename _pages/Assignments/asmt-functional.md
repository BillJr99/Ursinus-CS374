---
layout: assignment
permalink: /Assignments/Functional
title: "CS374: Principles of Programming Languages - Functional Programming"

info:
  coursenum: CS374
  purpose: "To build fluency in the functional paradigm.  Everyone completes a shared core (pure functions, higher-order functions, and recursive structures with fold), and then takes one self-chosen direction deeper.  Your team will weigh this paradigm as a design option for its own language."
  tilt:
    task: "Complete the two core parts (pure functions with higher-order combinators, and recursive structures with a generic fold), then choose ONE direction and carry it to depth: closures and lazy generators, CPS and call/cc, Church encodings, combinatory logic, parallel functional programming, declarative logic programming in Prolog, or a scoped open-source contribution to a functional-language ecosystem."
    criteria: "I grade the core on honoring the no-loop and no-assignment constraints and on fully generic tree and list operations, and I grade your chosen direction on reaching its stated depth.  The direction-depth rubric row applies equally to every direction.  The rubric below breaks it down in full."
  points: 100
  goals:
    - To write pure functions and higher-order functions in Python using map, filter, reduce, and recursion without loops or assignment
    - To implement recursive data structures including trees and linked lists with map and fold operations
    - "To take the paradigm shift to depth along one self-chosen direction: closures and lazy generators, continuation-passing style and call/cc, Church encodings, combinatory logic, parallel functional programming, declarative logic programming in Prolog, or a scoped open-source contribution to a functional-language ecosystem"
  rubric:
    - weight: 25
      description: "Core: Pure Functions and Higher-Order Functions (Goal 1: write pure functions and higher-order functions using map, filter, reduce, and recursion without loops or assignment)"
      preemerging: The solutions rely pervasively on loops and assignment, or fail to run due to major errors
      beginning: Most solutions run but several use loops or assignment where the directions forbid them, or combinator usage is incorrect (e.g., map returns a map object that is never consumed)
      progressing: All solutions are correct and respect the no-loop and no-assignment constraints, but combinators are used awkwardly (e.g., reduce used where map would suffice, or lambda where a named function would be clearer)
      proficient: Correct solutions use map, filter, reduce, and recursion idiomatically throughout with no loops or assignment in solution bodies, demonstrating Goal 1; the compose function works for any arity; my_map and my_reduce are property-tested against the built-ins; each function is documented with its type signature and one-sentence description; and the functional theory questions are answered with a correct referential-transparency demonstration and paradigm placements
    - weight: 25
      description: "Core: Recursive Data Structures (Goal 2: implement recursive data structures including trees and linked lists with map and fold operations)"
      preemerging: The tree or linked-list structures are missing, or the recursive cases do not terminate
      beginning: The structures are defined but tree_map or tree_fold is missing, or the linked-list fold does not handle the empty-list base case
      progressing: All structures and operations are implemented correctly for the provided test cases, but the functions are not generic, e.g., tree_fold is hardcoded to addition rather than taking a combining function
      proficient: Both the binary tree and the linked-list structures are defined as dataclasses; tree_map, tree_fold, list_map, and list_fold all take a function argument and work for any operation, demonstrating Goal 2; flatten and depth are implemented in terms of fold; and all operations are tested with at least four inputs including edge cases (empty list, single-node tree)
    - weight: 50
      description: "Direction Depth (Goal 3: carry your chosen direction, closures and lazy generators, CPS and call/cc, Church encodings, combinatory logic, parallel functional programming, declarative logic programming in Prolog, or a scoped open-source contribution to a language ecosystem, to its stated depth)"
      preemerging: "The direction work is absent, or does not use the direction's defining mechanism, e.g., factories that use global state instead of closures, a CPS interpreter whose cases return values directly instead of calling k, encodings that are never reduced, a reducer that cannot contract a single redex, a \"parallel\" map that is sequential, Prolog clauses that never rely on unification/backtracking (e.g., only ground facts, no rules), or an open-source \"contribution\" with no functional-paradigm substance (a typo fix or formatting-only change)"
      beginning: "The direction's defining mechanism is present but one or more of its required components is incorrect or missing, e.g., generators that materialize the whole sequence before yielding, continuations threaded incorrectly through compound expressions, substitution that captures variables on the adversarial tests, combinator rules misapplied, parallel results never verified against the sequential baseline, Prolog solutions that solve some curated problems but omit the bidirectional-relation demonstration or the backtracking enumeration, or an open-source contribution submitted without tests or documentation, or with no maintainer exchange (or documented attempt) recorded"
      progressing: All of the direction's required components work correctly for the provided cases, but items on the direction's depth checklist are incomplete; the demonstrations, measurements, or analyses that turn a working artifact into an argued one
      proficient: Every item on the chosen direction's depth checklist is met, all required components work on provided and edge cases, and the writeup connects the direction back to the core, stating precisely what Parts 1 and 2's pure-function and fold disciplines contributed to the direction work, demonstrating Goal 3 at full depth
  readings:
    - rtitle: "Functional Programming Activity, including the Scheme extension for Direction C"
      rlink: "Activities/liascript-functional.md"
      liapage: true
    - rtitle: "Lambda Calculus Part 2 Activity"
      rlink: "Activities/liascript-lambdacalculus2.md"
      liapage: true
    - rtitle: "The Power of Prolog (Markus Triska): Direction F"
      rlink: "https://www.metalevel.at/prolog"
    - rtitle: "SWISH: SWI-Prolog in the Browser (Direction F)"
      rlink: "https://swish.swi-prolog.org/"
    - rtitle: "Prolog in the Browser with SWISH (Tutorial)"
      rlink: "../Tutorials/Prolog"
    - rtitle: "Make-a-Lisp (mal): Direction G target"
      rlink: "https://github.com/kanaka/mal"
    - rtitle: "Strudel (TidalCycles): Direction G target"
      rlink: "https://github.com/tidalcycles/strudel"
    - rtitle: "tree-sitter: Direction G target"
      rlink: "https://tree-sitter.github.io/tree-sitter/"

tags:
  - functional
  - closures
  - generators
  - higher-order-functions
  - continuations
  - lambda-calculus
  - combinators
  - parallelism
  - logic-programming
  - prolog
  - open-source

---

This assignment trains you to write Python in the functional style.  Everyone completes the same two-part core: Part 1 is pure functions with higher-order combinators, and Part 2 is recursive data structures with a generic fold.  Then you choose **one direction** and carry it to depth.  You leave with a working toolkit (`map`, `filter`, `reduce`, a generic fold, and whatever your direction adds), a test file that proves it, and a one-page writeup your team can use when it weighs this paradigm as a design option for its own language.

The constraints are the content.  Where a part says no loops and no assignment statements inside the solution logic, that rule is what retrains you from imperative thinking (change a variable, step by step) to functional thinking (describe the result as a chain of transformations).  Two terms recur throughout.  A pure function is one whose output depends only on its inputs and which changes nothing outside itself.  A higher-order function is one that takes a function as an argument or returns one.

---

## Choose Your Direction

This is one assignment with one deliverable and one rubric.  Parts 1 and 2 are the core.  Part 3 is your direction.  Choose exactly one:

| Direction | What you build | Language or tool | Pick this if |
|-----------|----------------|------------------|--------------|
| [A: Closures and Lazy Generators](#direction-a-closures-and-lazy-generators) | Function factories that capture behavior, memoization, and infinite sequences computed on demand | Python | You want the most direct continuation of the core; its techniques (memoization, generator pipelines) are the ones you are most likely to reuse in the team project |
| [B: Continuation-Passing Style and call/cc](#direction-b-continuation-passing-style-and-callcc) | A small interpreter transformed so that no call ever returns, then "the rest of the computation" captured as a value and break, exceptions, and generators rebuilt from it | Python | You enjoyed the Interpreter assignment and want to see control flow become a value |
| [C: Church Encodings](#direction-c-church-encodings) | The untyped lambda calculus in code: capture-avoiding substitution, normal-order reduction, and booleans, numerals, and pairs represented as pure behavior | Python | You completed the Lambda Calculus lab and want its by-hand reductions reproduced by your own reducer |
| [D: Combinatory Logic, A Flock of Birds](#direction-d-combinatory-logic-a-flock-of-birds) | Computation with no variables at all: a reducer for S, K, I (and friends), point-free programming, and bracket abstraction from lambda terms | Python, plus a `config.json` | You want to see how far composition alone can go |
| [E: Parallel Functional Programming](#direction-e-parallel-functional-programming) | A MapReduce pipeline over a real corpus, measured and analyzed against Amdahl's Law | Python `multiprocessing` | You want speedup numbers you measured on your own machine, or you are on the [music and live-coding path]({{ site.baseurl }}/Projects/TeamLanguage#the-music-and-live-coding-path) (this is its Functional stop) |
| [F: Declarative Logic Programming in Prolog](#direction-f-declarative-logic-programming-in-prolog) | Relations that hold, solved by unification plus backtracking, including one relation run "backwards" | Prolog in the browser via SWISH; nothing to install | You want the widest possible contrast with the interpreter you just built |
| [G: Contribute to an Open-Source Language Ecosystem](#direction-g-contribute-to-an-open-source-language-ecosystem) | A scoped, functional-paradigm-relevant pull request with tests and documentation to [mal (Make-a-Lisp)](https://github.com/kanaka/mal), [Strudel](https://github.com/tidalcycles/strudel)/TidalCycles, a [tree-sitter](https://tree-sitter.github.io/tree-sitter/) grammar, or [SWI-Prolog](https://www.swi-prolog.org/) | The upstream project's language and tools, git, and GitHub | You want a public portfolio line, and you can get **instructor scope approval within the first week** of the assignment |

Read the core (Parts 1 and 2, plus Getting Started) and the one direction you chose; nothing in the other six sections counts toward your grade.  Every direction is graded on the same direction-depth rubric row and ends in the same deliverable shape: working code, tests, and a writeup section that connects the direction back to the core.  Choose by interest; none of them is the easy one.  Direction E is the Functional stop on the music and live-coding path, and students on that path may use a corpus of timed-event listings as their dataset.  Direction G's targets are a mal step port increment or test-harness improvement, a Strudel pattern or transformation function (the open-source stop on the music path), a tree-sitter grammar, or SWI-Prolog documentation and worked examples (which pairs naturally with Direction F's material).

> **Time budget.** This assignment runs alongside your team project's build sprints.  Budget the direction at roughly **6-8 hours**, finish the core before you start it, and pick a bounded slice you can finish well; each direction's depth checklist marks the line between "complete" and "extension."  The core is the smaller half in hours, but it is where the no-loop and no-assignment habits form, so do not rush it.  If you completed the Lambda Calculus lab, Direction C is a natural continuation: the lab's by-hand reductions and Church encodings are exactly the behavior your reducer must reproduce in code.

---

## Getting Started

- Python 3.10 or newer, and only the standard library: `functools` (for `reduce`), `dataclasses`, `typing`, and, for Direction E only, `multiprocessing`.  Direction F needs only a browser; Direction G needs git, a GitHub account, and whatever the upstream project uses.
- Any text editor (VS Code is fine) and a terminal.  If the terminal is new to you, read the [dev environment page]({{ site.baseurl }}/Tutorials/DevEnvironment) and the [shell primer]({{ site.baseurl }}/Tutorials/ShellForLanguageDev) first; every step below runs a file from the terminal, not from an editor button.

> **Do this.**
> 1. Make a project folder named `cs374-functional` and open a terminal in it.
> 2. Create the core files up front, empty for now: `higher_order.py` (Part 1), `recursive_structures.py` (Part 2), `test_functional.py` (assertions for the core and your direction), and `readme.md` (your writeup), plus the file(s) your direction's section names.
> 3. Run `python3 --version` from the same folder and confirm it prints a version of 3.10 or newer, such as `Python 3.11.4`.  If the shell says `python3: command not found`, try `python --version`; on some Windows installs only `python` is on the path, and you can use it everywhere this page says `python3`.  If neither works, follow the install steps on the dev environment page before continuing.

### Your First 30 Minutes

1. Open `higher_order.py` and paste in `total_length` from Step 1.1 together with its first assertion from the test file.  It exercises the whole Part 1 toolkit: `filter` keeps the words longer than three letters, `map` turns each word into its length, and `reduce` combines the lengths.
2. Run `python3 higher_order.py` from your project folder.  A silent exit means the assertion held.
3. Break it on purpose: change `> 3` to `> 5`, run again, and read the `AssertionError` traceback that points at the failing line.  Change it back.  That loop (edit, run, read the failure) is the whole workflow for the core.
4. Notice what is absent: no loop, no accumulator variable, no assignment.  If you catch yourself reaching for `total = 0` and a `for` loop, restate the problem as a chain of transformations instead.

### Suggested Pacing

See the course schedule for the assigned and due dates.  If a break falls inside the window, finish Parts 1 and 2 before it so that only the direction work travels with you.  Your team project's sprints run in parallel:

| Checkpoint | You should have |
|------------|----------------|
| On assignment | Part 1 underway: combinators, `compose`, and property-tested `my_map`/`my_reduce`; direction chosen |
| Checkpoint 1 | Part 1 complete (Direction G: scope approval within 3 days of hand-out) |
| Checkpoint 2 | Part 2 complete: tree and linked-list operations with edge-case tests; direction started |
| Midpoint | Direction components working for the provided cases, on your own schedule |
| Checkpoint 3 | Direction depth work underway |
| Due date | Direction depth checklist complete; writeup and ZIP submitted |

---

## Part 1 (Core): Pure Functions and Higher-Order Functions

The constraints for this entire part: no `for` loops, no `while` loops, and no assignment statements (no `=`) inside solution function bodies.  You may use `map`, `filter`, `functools.reduce`, `lambda`, recursion, and `return`.  The constraints apply to solution bodies only; your test code in `test_functional.py` may loop freely.  All Part 1 code lives in `higher_order.py`.  Give every function its type signature as a comment and a one-sentence description, because the rubric checks for both; the comment above each function in the skeletons below is its contract.

### Step 1.1: Write the Basic Combinators

These four functions are the vocabulary of the paradigm.  Each one is a short chain of `filter`, `map`, and `reduce`, and each has an edge case (an empty list, a tie) that you must decide and document.  `total_length` is done for you.

> **Do this.**
> 1. In `higher_order.py`, implement the four functions from the skeleton below, replacing each `TODO`.
> 2. In `test_functional.py`, import them and write at least three assertions per function, starting from the test file below.
> 3. Run the tests from your project folder:
>
> ```bash
> python3 test_functional.py
> ```

```python
# higher_order.py
from functools import reduce

# total_length: list[str] -> int
# Total characters across the words longer than three letters.
def total_length(words):
    return reduce(lambda acc, n: acc + n,
                  map(len, filter(lambda w: len(w) > 3, words)),
                  0)

# product_of_odds: list[int] -> int
# Product of the odd numbers; 1 for the empty list (the multiplicative identity).
def product_of_odds(nums):
    ...  # TODO: filter the odds, then reduce with multiplication, seeded with 1

# longest: list[str] -> str
# The longest word, found with a single reduce; the first one (left to right) on a tie;
# ValueError on an empty list.
def longest(words):
    ...  # TODO: guard the empty list, then one reduce that keeps the longer word

# flatten_once: list[list] -> list
# One level of flattening, using reduce; no itertools.
def flatten_once(lists):
    ...  # TODO: reduce with list concatenation
```

```python
# test_functional.py (starts like this and grows with every step)
from higher_order import total_length, product_of_odds, longest, flatten_once

assert total_length(["hi", "hello", "world", "it"]) == 10   # hello=5, world=5
assert product_of_odds([1, 2, 3, 4, 5]) == 15
assert product_of_odds([]) == 1
assert longest(["cat", "elephant", "dog"]) == "elephant"
assert flatten_once([[1, 2], [3], [4, 5]]) == [1, 2, 3, 4, 5]
# TODO: at least three assertions per function, including the tie and empty cases
print("Part 1 tests pass.")
```

> **You should see.** `Part 1 tests pass.` on one line.  If instead an `AssertionError` names a line, start there; the three most common causes: `map` or `filter` returned a lazy object that you compared to a list (consume it with `reduce` or `list()`); a `for` loop or an `=` crept into a solution body (remove it, even if the test passes); or `longest` lost the tie rule (the left word must win).

### Step 1.2: Compose Functions

`compose(*fns)` returns a new function that applies the given functions left to right, so `compose(f, g, h)(x)` equals `h(g(f(x)))`.  It must work for any arity, which the rubric checks: `compose(f)` behaves like `f`, and `compose(f, g, h, i)` chains all four.  Decide what `compose()` with no arguments returns (the identity function is the natural choice) and say so in its description.  Add `compose` to `higher_order.py` using `functools.reduce` internally, not a loop; then add the assertion below, plus at least two of your own (a single-function and a three-function pipeline), to `test_functional.py` and run it again.

```python
# compose: (*Callable) -> Callable
# Left-to-right composition: compose(f, g, h)(x) == h(g(f(x))).
def compose(*fns):
    ...  # TODO: reduce over fns, wrapping each function around the one before it

# in test_functional.py:
strip_lower_len = compose(str.strip, str.lower, len)
assert strip_lower_len("  Hello  ") == 5
```

### Step 1.3: Write my_map and my_reduce Recursively

Implement `my_map(f, xs)` and `my_reduce(f, xs, seed)` recursively, with no loops and no list comprehensions inside the body.  Each has a base case (the empty list) and a recursive case (do something with the first element, then recurse on the rest).  Add both to `higher_order.py`:

```python
def my_map(f, xs):
    """Base case: empty list -> []. Recursive: f(head) consed onto my_map(f, tail)."""
    if not xs:
        return []
    return [f(xs[0])] + my_map(f, xs[1:])

def my_reduce(f, xs, seed):
    """Base case: empty list -> seed. Recursive: apply f to seed and head, recurse on tail."""
    if not xs:
        return seed
    return my_reduce(f, xs[1:], f(seed, xs[0]))
```

Then add the property test below to `test_functional.py` and run `python3 test_functional.py` again.  A property test checks that two implementations agree on many inputs instead of checking one hand-computed answer; the `for` loop is fine here because it is test code, not a solution body.

```python
from functools import reduce
from higher_order import my_map, my_reduce

test_lists = [[1,2,3], [], [5], [1,2,3,4,5], [-1,0,1]]
for lst in test_lists:
    assert my_map(lambda x: x*2, lst) == list(map(lambda x: x*2, lst))
    assert my_reduce(lambda a,b: a+b, lst, 0) == reduce(lambda a,b: a+b, lst, 0)
print("All my_map and my_reduce properties hold.")
```

> **You should see.** Two lines, `Part 1 tests pass.` and `All my_map and my_reduce properties hold.`

### Step 1.4: Answer the Functional Theory Questions (in your writeup)

Answer three written questions in your writeup, `readme.md`.  They draw on the Programming Paradigms and Functional Programming sessions, and I grade them within Part 1's rubric row.

1.  **Referential transparency, demonstrated.**  Define referential transparency in one sentence.  Then take `total_length` above and show that replacing any call with its result preserves the program.  Next, exhibit one small *impure* Python function of your own (one that uses mutation or I/O) where that replacement changes behavior, and name exactly which property broke.
2.  **Paradigm placement.**  Classify each of these as imperative, functional, or declarative, and state which *question* each paradigm makes the programmer answer ("how, step by step?", "what combination of transformations?", "what result?"):
    - `total = 0` / `for n in nums: total += n`
    - `reduce(lambda a, b: a + b, nums, 0)`
    - `SELECT SUM(n) FROM nums;`
3.  **Purity's price.**  Name one thing your Part 1 constraints (no loops, no assignment) made harder, and one thing they made automatic (testing, reasoning, or parallelism).  Tie each to a property of pure functions rather than to taste.

---

## Part 2 (Core): Recursive Data Structures

Both structures in this part are recursive: a tree contains smaller trees, and a list contains a smaller list.  A fold is the one operation that visits the whole structure and combines what it finds, and you will define the other operations in terms of it.  All Part 2 code lives in `recursive_structures.py`, and its tests go in `test_functional.py` alongside Part 1's.  The comment above each function in the skeletons is its contract, and the rubric's proficient row asks that every operation take a function argument and work for any operation (not hardcoded to addition).

### Step 2.1: Build the Binary Tree and Its Fold

> **Do this.**
> 1. In `recursive_structures.py`, define the `BTree` dataclass and implement the four operations from the skeleton below.  `tree_map` must not modify the original tree (it is a pure function), and `tree_depth` and `tree_flatten` must be written in terms of `tree_fold`.
> 2. In `test_functional.py`, import them and test every operation on all four test trees listed after the skeleton.
> 3. Run `python3 test_functional.py`.

```python
# recursive_structures.py
from dataclasses import dataclass
from typing import Optional, Any

@dataclass
class BTree:
    value: Any
    left: Optional['BTree'] = None
    right: Optional['BTree'] = None

# tree_map: (Callable, Optional[BTree]) -> Optional[BTree]
# Apply f to every node's value and return a NEW tree with the same structure, e.g.
# tree_map(lambda x: x*2, BTree(1, BTree(2), BTree(3))) -> BTree(2, BTree(4), BTree(6)).
def tree_map(f, tree):
    ...  # TODO: None -> None; otherwise a new BTree with f(value) and mapped children

# tree_fold: (Callable, Optional[BTree], Any) -> Any
# Reduce the tree to one value by applying f(left_result, value, right_result) at each
# node; a None node yields seed.  With f = lambda l, v, r: l + v + r and seed 0, the
# fold computes the sum of all node values.
def tree_fold(f, tree, seed):
    ...  # TODO: None -> seed; otherwise f(fold(left), value, fold(right))

# tree_depth: Optional[BTree] -> int
# Depth of None is 0; depth of a leaf is 1.  Implemented via tree_fold.
def tree_depth(tree):
    ...  # TODO: one tree_fold call; the combining function takes max of the children plus 1

# tree_flatten: Optional[BTree] -> list
# All node values in in-order traversal (left, root, right).  Implemented via tree_fold.
def tree_flatten(tree):
    ...  # TODO: one tree_fold call; the combining function concatenates left, [value], right
```

**Test trees to use:** the empty tree `None` (every function returns its seed or identity value); the single node `BTree(42)` (map doubles it, fold sums it, depth is 1); the full tree `BTree(1, BTree(2, BTree(4), BTree(5)), BTree(3))`; and the right-skewed tree `BTree(1, None, BTree(2, None, BTree(3)))`.

> **You should see.** Your `Part 1` lines followed by a new `Part 2 tree tests pass.` line (add that `print` after your tree assertions).  For the full tree, `tree_flatten` returns `[4, 2, 5, 1, 3]` and `tree_depth` returns `3`; for the right-skewed tree, depth is also `3`.  A `RecursionError` means a recursive case never reaches `None`; check that every recursive call is on a child, not on the tree itself.  A wrong `tree_flatten` order usually means the combining function put `[value]` first instead of between the two child results.

### Step 2.2: Build the Linked List and Its Fold

> **Do this.**
> 1. Add the `LLNode` dataclass and the four operations below to `recursive_structures.py`.  The linked list is the same pattern with one child instead of two, and it closes the loop with Part 1: import `my_reduce` from `higher_order.py` and build `list_from_python` from it (no loops).
> 2. Test each operation in `test_functional.py` on at least four inputs, including the empty list (`None`) and a single node.
> 3. Run `python3 test_functional.py`.

```python
from higher_order import my_reduce

@dataclass
class LLNode:
    head: Any
    tail: Optional['LLNode'] = None  # None represents the empty list

# list_map: (Callable, Optional[LLNode]) -> Optional[LLNode]
# Apply f to every element and return a new linked list.
def list_map(f, node):
    ...  # TODO: None -> None; otherwise LLNode(f(head), list_map(f, tail))

# list_fold: (Callable, Optional[LLNode], Any) -> Any
# Left fold, accumulating from left to right, e.g.
# list_fold(lambda acc, x: acc + x, LLNode(1, LLNode(2, LLNode(3))), 0) -> 6.
def list_fold(f, node, seed):
    ...  # TODO: None -> seed; otherwise fold the tail with f(seed, head) as the new seed

# list_to_python: Optional[LLNode] -> list
# Convert to a Python list, via list_fold.
def list_to_python(node):
    ...  # TODO: one list_fold call

# list_from_python: list -> Optional[LLNode]
# Convert a Python list to a linked list, via my_reduce from Part 1.
def list_from_python(lst):
    ...  # TODO: my_reduce over lst; think about which end the nodes must be built from
```

> **You should see.** `list_to_python(list_from_python([1, 2, 3]))` returns `[1, 2, 3]`, `list_from_python([])` returns `None`, and the fold example in the skeleton returns `6`.  Add a `Part 2 list tests pass.` line so the test output shows the section ran.

---

## Part 3: Your Direction (choose exactly one)

Read only the direction you chose.  Every direction below has the same shape: what you build and need, numbered steps, and a depth checklist.  The checklist is the line between "the components work" (progressing) and "the direction reached its stated depth" (proficient), so treat it as the specification.

## Direction A: Closures and Lazy Generators

Two files, `closures.py` and `generators.py`.  In the first you write function factories (functions that return functions) and see exactly what a returned function carries with it.  In the second you write sequences that never end and pipelines that compute only what is asked for.  You need `closures.py` and `generators.py` in your `cs374-functional` folder, tests in `test_functional.py`, and the standard library only (`typing.Callable` for signatures and `time.perf_counter()` for the strict-vs-lazy comparison in A.2).  The Closures class material falls early in this assignment's window (see the course schedule); read ahead in that activity if you want to start sooner.

### A.1: Closures and Function Factories

A closure is a function that captures variables from the scope where it was created.  When a factory function creates and returns an inner function, the inner function keeps access to the factory's local variables even after the factory has returned.  Every call to a factory must produce an independent function.

> **Do this.**
> 1. Create `closures.py` from the skeleton below.  `make_adder` is done for you; it shows the capture.
> 2. Implement the other four factories, then `memoize`.  For `make_counter`, keep the state in a list or a mutable default argument; Python's `nonlocal` also works, but a list demonstrates the capture directly.
> 3. Test each one in `test_functional.py`, including the independence checks and the decorator form shown below.
> 4. In your writeup, draw an ASCII diagram (or describe in prose) showing what each closure returned by `make_adder(5)` and `make_adder(10)` captures internally, and why the two closures do not share state.

```python
# closures.py
from typing import Callable

# make_adder: int -> Callable; a function that adds n to its argument
def make_adder(n: int) -> Callable:
    def add(x):
        return x + n      # n is captured from make_adder's scope
    return add

# make_multiplier: int -> Callable; a function that multiplies its argument by n
def make_multiplier(n: int) -> Callable:
    ...  # TODO

# make_between: (int, int) -> Callable; a predicate for the closed interval [lo, hi]
def make_between(lo: int, hi: int) -> Callable:
    ...  # TODO

# make_counter: int -> Callable; returns the next integer on each call, starting from start
def make_counter(start: int = 0) -> Callable:
    ...  # TODO: keep the count in a list (or nonlocal) that the returned function captures

# make_once: Callable -> Callable; calls f at most once, then returns the cached first result
def make_once(f: Callable) -> Callable:
    ...  # TODO

# memoize: Callable -> Callable; caches f's results by argument, for any hashable arguments
def memoize(f: Callable) -> Callable:
    ...  # TODO: the cache dict is created once, outside the inner function
```

```python
add5, add10 = make_adder(5), make_adder(10)
assert add5(3) == 8 and add10(3) == 13 and add5(add10(0)) == 15
is_teen = make_between(13, 19)
assert is_teen(15) == True and is_teen(20) == False
c1, c2 = make_counter(), make_counter(10)
assert (c1(), c1(), c2(), c1()) == (0, 1, 10, 2)   # c1 and c2 do not share state
@memoize
def fib(n):
    if n <= 1: return n
    return fib(n-1) + fib(n-2)
assert fib(30) == 832040
```

> **You should see.** All assertions pass, and `fib(30)` returns in well under a second.  If it takes several seconds, `memoize` is not caching (a common cause is building the cache inside the wrapper, so every call starts with an empty dictionary).

### A.2: Lazy Sequences with Generators

Strict (eager) evaluation computes every element of a sequence immediately.  Lazy evaluation computes an element only when someone asks for it.  Laziness matters for infinite sequences, which cannot fit in memory, and for pipelines that stop early and so skip the remaining work.

> **Do this.**
> 1. Create `generators.py` from the skeleton below.  Every function that produces a sequence must use `yield`, and the two infinite generators must run indefinitely in O(1) extra memory.
> 2. Test with `take`, never with `list()`, on the infinite generators.  If a test hangs, a generator is being consumed to the end: the usual culprits are `list(naturals())`, a `for` loop over an infinite generator with no `break`, or a `take` that loops on the iterator instead of stopping after `n` items.
> 3. Build the lazy pipeline below: the first 10 perfect squares that are also even, using only `gen_map`, `gen_filter`, `naturals`, and `take`, with no list comprehensions and no intermediate lists.
> 4. Strict vs. lazy: find the first Fibonacci number greater than 1000 two ways, first by materializing a large list, then lazily one element at a time.  Time both with `time.perf_counter()`.

```python
# generators.py
def naturals(start=0):
    ...  # TODO: yield start, start+1, ... forever, in O(1) extra memory

def fibonacci():
    ...  # TODO: yield 0, 1, 1, 2, 3, 5, 8, ... forever

def take(n, it):
    ...  # TODO: consume the first n elements of any iterator and return them as a list

def gen_map(f, it):
    ...  # TODO: lazily yield f(x) for each x in it

def gen_filter(pred, it):
    ...  # TODO: lazily yield only the x for which pred(x) is true
```

```python
assert take(5, naturals()) == [0, 1, 2, 3, 4]
assert take(5, gen_map(lambda x: x**2, naturals(1))) == [1, 4, 9, 16, 25]
assert take(5, gen_filter(lambda x: x % 2 == 0, naturals())) == [0, 2, 4, 6, 8]
result = take(10, gen_filter(lambda x: x % 2 == 0, gen_map(lambda x: x**2, naturals(1))))
assert result == [4, 16, 36, 64, 100, 144, 196, 256, 324, 400]
```

### Direction A depth checklist

- All five factories (`make_adder`, `make_multiplier`, `make_between`, `make_counter`, `make_once`) plus `memoize` are correct, with independence between factory instances tested; `memoize` handles any hashable arguments and is demonstrated as a decorator.
- All five generator functions are implemented with `yield`; infinite sequences are demonstrated without hanging; the lazy pipeline runs without intermediate lists.
- The strict-vs-lazy comparison demonstrates a concrete performance difference, and the writeup explains what would happen if `naturals()` used a list instead of `yield`, and why that makes the pipeline impossible to run.
- The closure-capture diagram appears in the writeup.

---

## Direction B: Continuation-Passing Style and call/cc

One file, `continuations.py`, holding a small direct-style interpreter, its continuation-passing twin, a trampoline that runs the twin in constant stack space, `call/cc`, and one control structure (break or exceptions) rebuilt from continuations.

In a direct-style interpreter, every recursive call returns a value that waits on the Python call stack.  In continuation-passing style (CPS), no call ever returns: every call receives one extra argument, the continuation `k`, a function that represents "what to do next with the result," and passes its value to `k` instead of returning it.  Because calling `k` is the last thing each call does, every call is a tail call, and a trampoline (a loop that runs one step at a time) can execute it in constant stack space.  Once continuations are values, capturing the current one gives you `call/cc` ("call with current continuation"), from which you can rebuild break, exceptions, and generators.  That is why `call/cc` is called *the mother of all control structures*.  You need `continuations.py` in your `cs374-functional` folder, tests in `test_functional.py`, the standard library only (B.2 runs into Python's recursion limit on purpose, and the trampoline, not a larger `sys.setrecursionlimit`, is the point of that step), and your Interpreter assignment open beside you: the direct-style miniature reuses its structure (dataclass AST nodes, an `Env` chain, a `Closure` value).

### B.1: The CPS transform

> **Do this.**
> 1. Write the direct-style `interp(expr, env)` first: a miniature of your Interpreter assignment with dataclass AST nodes `Num`, `Bool`, `Var`, `BinOp`, `If`, `Let`, `Lam`, `App`, an `Env` chain, and a `Closure` value.  It is under sixty lines.
> 2. Smoke-test it on `(λx. x + 1)(41)` -> `42.0` and `let y = 10 in y * y` -> `100.0` before you change anything.
> 3. Copy it to `interp_k(expr, env, k)` and transform one case at a time, re-running the equivalence tests after each case.

The mechanical rule: wherever direct style writes `return f(x)`, CPS writes `f_k(x, env, k)`; wherever direct style writes `v = f(x); use(v)`, CPS writes `f_k(x, env, lambda v: use_k(v, env, k))`.  Case by case: `Num`, `Bool`, and `Lam` pass their value (or closure) straight to `k`.  `BinOp` evaluates the left operand, then *inside its continuation* evaluates the right operand, then applies the operator and calls the outer `k`.  `If` chooses the branch inside the condition's continuation.  `Let` and `App` chain the same way.  No case may return a value directly.

```python
# continuations.py (the CPS side; the direct-style interp and AST nodes come first)
def interp_k(expr, env, k):
    match expr:
        case Num(n):
            return k(float(n))            # the value goes to k, not to the caller
        case BinOp(op, left, right):
            ...  # TODO: evaluate left; inside its continuation evaluate right;
                 # inside that continuation apply op and call k
        # TODO: Bool, Var, Lam, If, Let, App; every case ends in a call to k
```

**Verify equivalence:** for every test expression, `interp_k(e, env, lambda v: v)` must equal `interp(e, env)`.  Cover at least `Num`, `BinOp` (nested), `If` (both branches), `Let`, and `App`.  Reading any `interp_k` case top to bottom, the last thing it does must be a call to `k` (or to another `_k` function that will).

### B.2: Trampolining

Python does not optimize tail calls, so deep recursion still overflows the stack.  Wrap every tail call in a zero-argument `Thunk` and drive execution with a loop:

```python
class Thunk:
    def __init__(self, f): self.f = f

def trampoline(result):
    while isinstance(result, Thunk):
        result = result.f()
    return result
```

> **Do this.**
> 1. Change each tail call in `interp_k` to return `Thunk(lambda: <the call>)` instead of making the call, and wrap the top-level entry in `trampoline(...)`.
> 2. Build a chain of 2,000 nested `Let` bindings (comfortably past Python's default recursion limit) and verify that it evaluates to the right answer.
> 3. Run the same AST through the un-trampolined `interp_k` once to watch the `RecursionError` you just eliminated, and keep that comparison for your writeup.

### B.3: call/cc

Add a `Callcc(fun)` AST node.  In the CPS interpreter, the current continuation is *exactly* the `k` in hand.  Wrap it in a `Continuation` object that, when called, raises a `ContinuationEscape` carrying the value; the top-level `run` driver catches the escape and resumes.  Demonstrate each of the following as a hand-built AST run through `run`:

1. `call/cc` whose function ignores the continuation behaves as a normal call: `Callcc(Lam("k", Num(42)))` -> `42`.
2. Invoking the continuation escapes immediately: `Callcc(Lam("k", App(Var("k"), Num(7))))` -> `7`.
3. After an escape, pending computation is discarded: bind `call/cc(λk. k(5))` in a `Let` whose body multiplies by 1000, and document which value your implementation produces and why.

### B.4: One control structure from scratch

Using the two-continuation pattern (a normal-return `k` and an escape `k`), implement **either** `for_until` **or** `with_handler`.  `for_until` is break as a continuation: iterate a body that may call `break_fn(v)` to exit with `v`.  `with_handler` is exceptions as continuations: `raise_fn` is simply "call the handler's continuation," and it must propagate correctly through nested handlers.  Test the one you build, including the nested case.

### Direction B depth checklist

- CPS equivalence tests pass across at least four expression types, and every `interp_k` case ends in a call to `k` (state this invariant in a comment and explain why each recursive call is now a tail call).
- The trampolined interpreter survives the 2,000-deep `Let` chain.
- All three `call/cc` demonstrations produce their specified results, with escape verified across more than one nesting depth.
- The derived control structure (`for_until` or `with_handler`) works including its nested/propagation case.
- The writeup defines a continuation in one sentence, explains the "mother of all control structures" claim with one concrete example, and maps Python's `try/except`, generators, and `async/await` to the continuation model in a three-row table (naming the restriction that makes each a special case).

---

## Direction C: Church Encodings

One file, `lambda_calc.py`: an AST for the untyped lambda calculus, capture-avoiding substitution, two reduction strategies behind one interface, an alpha-equivalence checker, and Church booleans, numerals, and pairs verified mechanically through your own reducer.

The untyped lambda calculus has three constructs (variables, abstraction, application), and it can compute anything computable.  Its most striking consequence is that data can be represented as pure behavior: a Church boolean *is* the act of choosing between two things, and a Church numeral *is* the act of repeating a function some number of times.  Your Part 1 combinators and Part 2 folds were this same idea in Python dress.  You need `lambda_calc.py` in your `cs374-functional` folder, tests in `test_functional.py`, the standard library only, and the Lambda Calculus Part 2 activity (in the readings) plus, if you did it, your Lambda Calculus lab: its by-hand reductions are the behavior your reducer must reproduce.

### C.1: The calculus in code

Substitution replaces a free variable with a term, and it is capture-avoiding when it never lets a free variable of the replacement become accidentally bound under a binder.  Follow the standard three-case definition exactly, including the fresh-variable renaming case when substituting under a binder whose variable appears free in the replacement.

> **Do this.**
> 1. Create `lambda_calc.py` from the skeleton below: the three AST dataclasses and `free_vars`.
> 2. Implement capture-avoiding substitution and run the three adversarial tests before you write the reducer.
> 3. Implement the single-step normal-order reducer (leftmost-outermost redex first) and the `normalize` driver, which reduces to normal form under a configurable step limit with an optional step-by-step trace.

```python
# lambda_calc.py
from dataclasses import dataclass

@dataclass(frozen=True)
class LVar:
    name: str

@dataclass(frozen=True)
class LLam:
    param: str
    body: "LVar | LLam | LApp"

@dataclass(frozen=True)
class LApp:
    rator: "LVar | LLam | LApp"
    rand: "LVar | LLam | LApp"

def free_vars(term) -> set[str]:
    ...  # TODO: one case per constructor

def subst(term, var: str, replacement):
    ...  # TODO: the three standard cases; when term is LLam and its param is free
         # in replacement, rename the binder to a fresh name first

def step_normal(term):
    ...  # TODO: contract the leftmost-outermost redex; return None if term is in normal form

def normalize(term, max_steps=1000, trace=False):
    ...  # TODO: repeat step_normal until None or until max_steps fires; print each step if trace
```

**Adversarial substitution tests**: your substitution must pass these capture traps, and your writeup must display them:

- $$(\lambda y.\, x)[x := y]$$: naive substitution captures $$y$$; correct substitution renames the binder first.
- $$(\lambda y.\, x\ y)[x := y\ z]$$: the same trap, one level deeper.
- One trap of your own design that defeats a substitution function lacking the fresh-variable case.  Show the wrong answer naive substitution produces.

> **You should see.** For the first trap, a result of the shape $$\lambda y'.\, y$$ (a renamed binder with the free $$y$$ intact), never $$\lambda y.\, y$$.  If you get the identity function, the binder was not renamed and the free variable was captured.

### C.2: The encodings

Encode each of the following as terms in your AST, and verify them mechanically through your reducer:

- **Booleans:** `TRUE = λt.λf.t`, `FALSE = λt.λf.f`, with `AND`, `OR`, `NOT`, and `IF`.  Verify that the full truth tables reduce correctly.
- **Numerals:** $$\overline{0}$$ through $$\overline{4}$$, with `SUCC`, `ADD`, and `MUL`.  Verify that `ADD 2 2` and `MUL 2 2` both reduce to terms alpha-equivalent to $$\overline{4}$$.  Two terms are alpha-equivalent when they differ only in the names of bound variables; you will need a small alpha-equivalence checker, so write one.
- **Pairs:** `PAIR`, `FST`, `SND`.  Verify that `FST (PAIR a b)` reduces to `a` and `SND (PAIR a b)` to `b`.

Present the verification as a test table that maps each law to a passing reduction.

### C.3: Strategy and divergence

Implement applicative-order reduction (arguments first) behind the same interface, and demonstrate the term where the two strategies behave differently: $$(\lambda x.\, \lambda y.\, y)\ \Omega$$, where $$\Omega = (\lambda x.\, x\ x)(\lambda x.\, x\ x)$$.  Normal order discards $$\Omega$$ unevaluated and terminates.  Applicative order runs forever, and your step limit fires.  Write one sentence on what each strategy does and why, and one more connecting this to why a lazy language can pass an infinite structure to a function that ignores it.

> **You should see.** Under normal order, $$\lambda y.\, y$$ in one step.  Under applicative order, a step-limit report (for example, a message naming the limit and the last term) and a clean return, not a `RecursionError` or a hang.

### Direction C depth checklist

- Substitution passes all three adversarial capture traps, with the naive wrong answer exhibited for your own trap.
- Both reduction strategies work behind a common interface, with the step limit and trace verbosity configurable, and the $$\Omega$$ divergence demonstrated (graceful step-limit report, not a crash).
- All encoding laws are verified mechanically, including `MUL 2 2` up to alpha-equivalence via your checker, presented as a law-to-reduction test table.
- One derivation (your choice) is worked by hand in the writeup, one reduction per line with the contracted redex marked, and cross-checked step-for-step against the interpreter's trace, reconciling any disagreement (finding your own mistake is worth more than not reporting one).
- The writeup answers: where in `map`/`filter`/`reduce` from Part 1 have you already been treating behavior as data, and where in a modern language have Church-style encodings earned their keep?

---

## Direction D: Combinatory Logic, A Flock of Birds

Three files: `birds.py` (a reducer for seven combinators and the point-free functions), `bracket.py` (the translation from lambda terms to SKI), and `config.json` (the reducer's strategy, step limit, and trace switch).

Combinatory logic strips the lambda calculus down further: no variables, no binding, no substitution.  Only application remains, plus a small fixed set of primitive combinators, each named (after Raymond Smullyan's puzzle book) for a bird.  With only application and the birds, composition, argument passing, and currying are your only tools.  The rules:

$$
\mathbf{I}\ a \Rightarrow a \qquad
\mathbf{K}\ a\ b \Rightarrow a \qquad
\mathbf{S}\ f\ g\ x \Rightarrow f\ x\ (g\ x)
$$
$$
\mathbf{B}\ f\ g\ x \Rightarrow f\ (g\ x) \qquad
\mathbf{C}\ f\ a\ b \Rightarrow f\ b\ a \qquad
\mathbf{W}\ f\ x \Rightarrow f\ x\ x \qquad
\mathbf{M}\ x \Rightarrow x\ x
$$

You need `birds.py`, `bracket.py`, and `config.json` in your `cs374-functional` folder, tests in `test_functional.py`, the standard library only (`json` reads the configuration), and paper for D.1.

### D.1: Hand reductions

The hand reductions come first, and they are the answers your reducer must reproduce.  Reduce each term to normal form, one rule per line, naming the rule that fires at each step:

**(a)** $$\mathbf{K}\ \mathbf{I}\ a\ b$$: identify which standard function this is.  **(b)** $$\mathbf{S}\ \mathbf{K}\ \mathbf{K}\ 42$$: what well-known combinator is $$\mathbf{S}\ \mathbf{K}\ \mathbf{K}$$? **(c)** $$\mathbf{B}\ f\ (\mathbf{B}\ g\ h)\ x$$ and $$\mathbf{B}\ (\mathbf{B}\ f\ g)\ h\ x$$: confirm both produce $$f\ (g\ (h\ x))$$, which is associativity of composition.  **(d)** $$\mathbf{C}\ (\mathbf{B}\ f\ g)\ a\ b$$: what two-argument function is $$\mathbf{C}\ (\mathbf{B}\ f\ g)$$? **(e)** $$\mathbf{S}\ (\mathbf{K}\ \mathbf{S})\ \mathbf{K}\ f\ g\ x$$: reduce fully and identify the result as one of the named birds.

### D.2: The combinator reducer

> **Do this.**
> 1. Create `birds.py` from the skeleton below.  Application is left-associative, so `S K K` is `App(App(Prim("S"), Prim("K")), Prim("K"))`.
> 2. Implement outermost-first reduction (the analog of normal order) as the default, with innermost-first selectable via `config.json` alongside `max_steps` (default 1000) and `trace`, for example `{"strategy": "outermost", "max_steps": 1000, "trace": false}` (the key names are yours to choose; document them in your readme).  If no normal form is reached within the step limit, print a location-prefixed diagnostic and stop; do not crash.
> 3. Verify on $$\mathbf{I}\ 42$$, $$\mathbf{K}\ \mathbf{I}\ a\ b$$, $$\mathbf{S}\ \mathbf{K}\ \mathbf{K}\ x$$, $$\mathbf{B}\ f\ g\ x$$, and the diverging $$\mathbf{M}\ \mathbf{M}$$.

```python
# birds.py
from dataclasses import dataclass

@dataclass(frozen=True)
class Prim:
    name: str          # one of "S", "K", "I", "B", "C", "W", "M", or an atom like "a"

@dataclass(frozen=True)
class App:
    rator: object
    rand: object

def step_outermost(term):
    ...  # TODO: find the leftmost-outermost redex (a Prim applied to enough arguments)
         # and contract it by its rule; return None when no rule fires

def reduce_term(term, config):
    ...  # TODO: strategy from config; loop up to config["max_steps"], printing each step
         # when config["trace"]; on the limit, print a location-prefixed diagnostic and stop
```

> **You should see.** $$\mathbf{I}\ 42$$ reduces to `42` in one step and $$\mathbf{S}\ \mathbf{K}\ \mathbf{K}\ x$$ to `x` in two; $$\mathbf{M}\ \mathbf{M}$$ prints 1000 identical steps under `trace` and then a diagnostic such as a step-limit message naming the term, and the program keeps running.

### D.3: Point-free programming

Point-free style defines a function without naming its arguments: no `lambda`, no `def`, and no named parameters in the definition itself.  Using the birds as Python callables, implement each of the following in point-free style, state its combinator expression beside the Python, and demonstrate it on at least three inputs:

1. `double_then_negate`: double, then negate.
2. `apply_twice(f)`: apply `f` twice.  (Which bird duplicates?)
3. `swap_args(f)`: swap a curried two-argument function's arguments.  (One bird does exactly this.)
4. `on(f, g)`: `on(f, g)(a)(b) = f(g(a))(g(b))`.  (The Psi bird.)
5. `const_function(x)`: ignore the argument, always return `x`.  (The pure Kestrel.)

### D.4: Bracket abstraction

Bracket abstraction translates a lambda term into an SKI expression via three rules:

$$
[x]\, x = \mathbf{I} \qquad
[x]\, e = \mathbf{K}\, e \;\; (x \notin \mathrm{FV}(e)) \qquad
[x]\, (e_1\ e_2) = \mathbf{S}\, ([x]\, e_1)\, ([x]\, e_2)
$$

> **Do this.**
> 1. Create `bracket.py` with the three lambda-term dataclasses (`LamVar`, `LamAbs`, `LamApp`) and a `translate(term)` function that applies the rules for every lambda, outermost first, until no lambdas remain.
> 2. Reduce the translations of $$\lambda x.\ x$$, $$\lambda f.\ \lambda x.\ f\ x$$, and $$\lambda x.\ \lambda y.\ x$$ through the reducer from `birds.py` (import it; do not copy it) and confirm they behave as identity, function-identity, and Kestrel.
> 3. Measure the size (node count) of the SKI translation of $$\lambda x.\ \lambda y.\ x\ y$$ against the original term and comment on the expansion ratio in your writeup.  This blowup is why real combinator compilers (Turner's algorithm) optimize the translation.

### Direction D depth checklist

- All hand reductions are correct, one rule per line with rule names, and where multiple redexes were available the choice is noted with a remark that confluence held.
- The reducer supports all seven birds with a selectable strategy, a firing step limit on $$\mathbf{M}\ \mathbf{M}$$ (graceful, location-prefixed), and a trace mode showing each step.
- All five point-free functions are correct and tested, each with its combinator expression stated; a sixth of your own design is included with a motivation.
- The bracket-abstraction translator passes all three verifications *through the reducer*, and the size analysis appears in the writeup.
- The writeup answers: how does $$\mathbf{S}\ f\ g\ x = f\ x\ (g\ x)$$ do the job your interpreter's environment does (distributing a value to everywhere it is needed) without any environment at all?

---

## Direction E: Parallel Functional Programming

One file, `pipeline.py`, plus your corpus: a word-count MapReduce over a real book, first sequential, then parallel with `multiprocessing`, then with a parallel tree-reduce, each version measured and the measurements explained with Amdahl's Law.

The Google MapReduce paper (Dean and Ghemawat, 2004) opens with one observation: when you write a computation as a pure map over independent inputs followed by an associative reduce over the results, the framework can parallelize it for you, with no threads to coordinate and no locks to write.  (A reduce is associative when grouping does not matter: merging `a` with `b` and then with `c` gives the same result as merging `a` with the merge of `b` and `c`.)  This direction tests the paradigm's central promise, *purity buys parallelism*, on a 21,000-line corpus with timings you take yourself, and confronts the practical limit (Amdahl's Law) that constrains distributed systems.  It is also the Functional stop on the [music and live-coding path]({{ site.baseurl }}/Projects/TeamLanguage#the-music-and-live-coding-path): the same pure-map, associative-reduce discipline is how pattern engines like Strudel evaluate independent events, so students on that path may analyze a corpus of timed-event listings as their dataset instead.  The pipeline requirements are identical.  You need:

- `pipeline.py` in your `cs374-functional` folder, and tests in `test_functional.py`.  The standard library: `multiprocessing`, `functools.reduce`, and `timeit`.
- **Dataset:** the Project Gutenberg plain-text *Moby Dick* (approximately 21,000 lines), split into lines; each line is one "document."  Save it in the project folder and read it from there.
- A machine with more than one core, and its CPU model and core count written down before you start; every number you report depends on them.

### E.1: The sequential baseline

`word_frequencies(line) -> dict[str, int]` is your map function; argue in writing that it is pure (no global reads, no shared mutation, and the same output for the same input every time).  `merge_counts(a, b) -> dict` is your reduce function; argue that it is pure *and associative*, and say why associativity matters for parallelism.  `top_n(counts, n)` returns the most frequent words.  Implement the three from the skeleton, test each on two or three short hand-made lines in `test_functional.py`, then run `python3 pipeline.py` on the full corpus and record total words, unique words, the top 20, and the runtime.  Put the code that starts a `Pool` under `if __name__ == "__main__":`; on macOS and Windows, worker processes re-import your module, and without that guard each worker starts its own pool and the program never finishes.  The map function must be defined at module level so that Python can pickle it (serialize it to send to another process).

```python
# pipeline.py
from functools import reduce
from multiprocessing import Pool

# word_frequencies: str -> dict[str, int]
def word_frequencies(line):
    ...  # TODO: pure map function; no global reads, no shared mutation

# merge_counts: (dict, dict) -> dict
def merge_counts(a, b):
    ...  # TODO: pure and associative; return a new dict, never mutate a or b

# top_n: (dict, int) -> list
def top_n(counts, n):
    ...  # TODO

if __name__ == "__main__":
    ...  # TODO: read the corpus into lines; run the sequential pipeline; then the Pool
         # version; assert the two results are equal before you time anything
```

### E.2: The parallel map

Replace `map(word_frequencies, lines)` with `multiprocessing.Pool.map` and assert that the parallel result equals the sequential result.  Then measure wall-clock time (`timeit`, five runs per configuration, report the mean) across worker counts 1, 2, 4, and the maximum available, and across chunk sizes (default, 10, 100, 1000) at maximum workers.  Tabulate time, speedup, and efficiency ($$= \text{speedup} / \text{workers}$$) for every configuration.  At what worker count does efficiency drop below 0.8, and why?  What effect does chunk size have, and why?

> **You should see.** The equality assertion passes on the first try if `word_frequencies` is pure; if it fails, look for a global or a mutable default argument.  With one worker the parallel version is usually slower than the sequential baseline (process start-up and pickling are pure overhead there), and speedup grows, then flattens, as workers increase.

### E.3: Tree-reduce

The sequential `reduce(merge_counts, results, {})` performs $$O(n)$$ merges one after another.  Implement `tree_reduce(merge_fn, results)`: pair up adjacent elements, merge the pairs in parallel via `Pool.map`, and repeat until one element remains (carry an odd element forward).  Verify that it matches the sequential reduce, then measure and compare both on the full corpus.  In your writeup, draw the dependency graph of a tree-reduce over 8 elements: how many rounds are there, what is the maximum speedup regardless of core count, and how does the synchronization between rounds relate to the serial fraction below?

### E.4: Amdahl's Law analysis

If a fraction $$f$$ of the computation is serial, the maximum speedup with $$n$$ processors is

$$
S(n) = \frac{1}{f + \frac{1-f}{n}} \;\xrightarrow{\,n \to \infty\,}\; \frac{1}{f}
$$

From your measured data, estimate $$f$$ (using $$f \approx \frac{1/S_{\text{max}} - 1/n_{\text{max}}}{1 - 1/n_{\text{max}}}$$), compute the theoretical maximum speedup, and compare it to what you measured.  Explain the discrepancies (process spawn cost, pickling for inter-process communication, the final sort, OS scheduling).  What speedup would 100 workers give, and what does that imply about this pipeline at datacenter scale?

### Direction E depth checklist

- The map function's purity and the reduce function's purity *and associativity* are argued in writing, and the parallel results are asserted equal to the sequential baseline.
- Timing uses at least five runs per configuration; the full time/speedup/efficiency table covers all worker counts and chunk sizes, with the chunk-size effect explained.
- The tree-reduce works (including the odd-element and empty/single-document edge cases), is measured against the sequential reduce, and its dependency-graph analysis appears in the writeup.
- The Amdahl analysis estimates $$f$$ from measured data, computes the theoretical bound, reconciles it with measurement, and projects to 100 workers.  Your machine's CPU model and core count are stated prominently; speedup numbers are meaningless without them.
- The writeup constructs one hypothetical *non*-associative reduce function and shows how tree-reduce would produce wrong results with it, connecting associativity back to Part 2's folds.

---

## Direction F: Declarative Logic Programming in Prolog

Two files, and no Python for this direction: `logic.pl` (your Prolog source) and `logic_session.md` (every query you ran and what it answered).  You build a small knowledge base, solve six of the Ninety-Nine Prolog Problems, and run one relation in more than one direction.

Every other direction is a story about *evaluation*: you write an expression, and a machine reduces it to a value.  In Prolog you state relations that hold (facts and rules) and then pose a query.  The engine searches for every way to make the query true, using unification (two-way pattern matching, the same idea your parser's AST equality hinted at) and backtracking (undoing a choice that failed and trying the next one).  There is no "call and return."  A relation like `append/3` can concatenate two lists, split a list every possible way, or check membership: the same clause, run in any direction.  This is the widest paradigm contrast the course offers, and it directly motivates the microKanren-style relational ideas and the unification you met in the type-checking direction of the Interpreter.  You need:

- A browser.  You will work entirely in [SWISH](https://swish.swi-prolog.org/) (SWI-Prolog online); there is nothing to install.  The [Prolog in the Browser tutorial]({{ site.baseurl }}/Tutorials/Prolog) walks through the SWISH editor and query pane.
- Before you start, read the opening chapters of [The Power of Prolog](https://www.metalevel.at/prolog) (Markus Triska's free, modern text) for facts, rules, queries, lists, and how backtracking works.
- `logic.pl` and `logic_session.md` in your `cs374-functional` folder.  Write clauses in the SWISH editor, and copy them into `logic.pl` as you go so the file always matches what you ran.

### F.1: Relational thinking, facts, rules, and queries

Warm up with a family knowledge base: `parent/2` facts, then `grandparent/2`, `sibling/2`, and `ancestor/2` rules.  In `logic_session.md`, show at least one query with a single answer, one query that yields *multiple* answers on backtracking, and one recursive rule (`ancestor/2`) with a query that requires several backtracking steps.  Explain in one or two sentences what "the engine searches for a proof" means here versus "the evaluator computes a value" in your interpreter.

> **Do this.**
> 1. Open SWISH, paste the starter below into the program pane, and run `?- grandparent(tom, Who).`, `?- parent(bob, Child).`, and `?- ancestor(tom, X).` in the query pane one at a time.
> 2. After each query, press `;` (or the Next button) until SWISH reports `false`, so you see every answer backtracking finds.
> 3. Copy each query and its answers into `logic_session.md` as you go.

```prolog
% logic.pl
parent(tom, bob).
parent(bob, ann).
% TODO: more parent/2 facts, enough for a grandparent, a sibling pair, and a three-generation chain

grandparent(X, Z) :- parent(X, Y), parent(Y, Z).
% TODO: sibling/2 and the recursive ancestor/2
```

> **You should see.** `Who = ann` for the first query.  For a query with several answers, SWISH shows one binding at a time and waits for `;`.  If a query answers `false` when you expected a binding, the usual cause is a spelling mismatch between a fact and a rule, or a variable that starts with a lowercase letter (Prolog reads that as an atom, not a variable).

### F.2: A curated set of the Ninety-Nine Prolog Problems

Solve the following six problems from the classic [Ninety-Nine Prolog Problems](https://www.metalevel.at/prolog/99) list.  I chose them to span list recursion, structural recursion, arithmetic, logic, and constraint search:

1.  **P01 `my_last(X, List)`**: the last element of a list (basic list recursion).
2.  **P05 `rev(List, Reversed)`**: reverse a list (accumulator recursion).
3.  **P07 `my_flatten(List, Flat)`**: flatten a nested list structure (recursion over term structure).
4.  **P31 `is_prime(N)`**: primality (arithmetic and the `\+`/negation-as-failure you should explain).
5.  **P46 `table(A, B, Expr)`**: print the truth table of a logical expression in `A` and `B` (logic connectives as relations).
6.  **P90 `queens(Qs)`**: place eight non-attacking queens (backtracking search, the payoff problem, where the declarative style shines).

For each problem, include the clause(s) in `logic.pl` and, in `logic_session.md`, the query you ran with its answer(s).  Where a problem admits multiple solutions (P90), show that Prolog enumerates them on backtracking and count how many exist.

### F.3: Run it backwards (the bidirectional relation)

Pick one relation you wrote (or `append/3`) and demonstrate it in at least two modes: for example, `append([1,2],[3],Xs)` (concatenate) *and* `append(Xs, Ys, [1,2,3])` (enumerate every split).  Explain in your writeup why a Python function *cannot* be run backwards like this, and what property of Prolog (unification over logic variables, not evaluation of expressions) makes it possible.  This is the single most important idea in the direction.

### F.4: Unification and backtracking vs. your interpreter's environments

Close with a short written comparison; it is required, and it ties the direction back to the pipeline.  Your interpreter's `Environment` maps names to *values* by assignment, in one direction only, and evaluation never "undoes" a binding.  Prolog's unification binds logic variables to *terms* in both directions, and backtracking un-binds them when a branch fails.  In one paragraph, contrast (a) binding-by-assignment vs. binding-by-unification, and (b) your evaluator's single forward pass vs. Prolog's search-with-backtracking.  If you took the type-checking direction of the Interpreter, connect this explicitly to the unification in your type inferencer; it is the *same* algorithm doing a different job.

### Direction F depth checklist

- The warm-up knowledge base demonstrates a single-answer query, a multi-answer (backtracking) query, and a recursive rule, with the proof-search-vs-evaluation distinction stated.
- All six curated problems (P01, P05, P07, P31, P46, P90) are solved with correct clauses and shown queries/answers; P90's multiple solutions are enumerated and counted; negation-as-failure in P31 is explained.
- One relation is demonstrated running in at least two modes, with a written explanation of why unification (not evaluation) makes bidirectionality possible.
- The F.4 comparison contrasts assignment-binding vs. unification-binding and forward evaluation vs. backtracking search, connecting to the interpreter (and, if applicable, to HM type-inference unification).
- `logic.pl` loads cleanly in SWISH and `logic_session.md` records every query and its output.

---

## Direction G: Contribute to an Open-Source Language Ecosystem

A public pull request, with tests and documentation, to a real open-source language project, plus `contribution.md`: the contribution log described below, with a link to the pull request.  **Scope approval from the instructor is required within 3 days of hand-out.**

This direction takes the paradigm into a codebase that predates you and will outlive the semester.  You find a scoped, functional-paradigm-relevant piece of work, specify it with a failing test before you write the fix (the same failing-test-as-specification discipline the whole course runs on), and carry it through a public pull request and a maintainer exchange.  The paradigm content is the same as in the other directions (pure transformations, recursion over structure, functions as values); the added content is the professional practice around it, and the result is a portfolio line few undergraduates have: *my code was reviewed by the maintainers of a real project.*  You need:

- A GitHub account, git on your machine, and a fork of the target project.  The upstream project's own setup instructions tell you what else to install; follow them exactly.
- `contribution.md` in your `cs374-functional` folder, started on day one and updated as the work proceeds.
- A target from the approved list below, and my approval of your scope within 3 days of hand-out.

**Choosing a target.**  Approved ecosystems, with the kind of contribution that fits each:

- **[mal: Make-a-Lisp](https://github.com/kanaka/mal)**: an increment to a step implementation in a language of your choice, or an improvement to the shared test harness.  mal's whole structure is fold-and-recursion over expression trees.
- **[Strudel](https://github.com/tidalcycles/strudel) / TidalCycles**: a pattern or transformation function.  Pattern combinators *are* higher-order functions over timed event structures.  This is the open-source stop on the [music and live-coding path]({{ site.baseurl }}/Projects/TeamLanguage#the-music-and-live-coding-path).
- **[tree-sitter](https://tree-sitter.github.io/tree-sitter/) grammars**: a grammar fix or improvement with its test cases.  This is structural recursion over syntax, adjacent to everything you built this semester.
- **[SWI-Prolog](https://www.swi-prolog.org/)**: documentation with worked examples, or test cases for library predicates.  It pairs naturally with Direction F's material, and documentation contributions are how most successful open-source careers start.

Something else you care about is negotiable; bring it to the scope-approval conversation.  Two things are not negotiable: the work must have functional-paradigm substance (a typo fix or formatting change does not qualify), and it must be small enough to finish.  One well-scoped, well-tested contribution beats an ambitious abandoned one.

### G.1: Issue selection and scope approval (first 3 days)

Find your target: a triaged open issue, a gap in the documentation, a missing test, or a small feature request with maintainer interest.  In `contribution.md`, record the issue or gap (with links), why it is *functional-paradigm* work (which core ideas from Parts 1 and 2 it exercises), and your one-sentence minimum viable scope.  Bring this to me for approval within 3 days of hand-out; the approval exists to protect you from scope that cannot land in the assignment window, and it is a five-minute conversation if those three things are written down.

### G.2: Specification first

Before you write the fix, write the specification the way this course always does: a failing test that demonstrates the issue.  For documentation work, the specification is the worked example that does not yet exist and the checklist it must satisfy.  Commit it, or record it in its original form in `contribution.md`.  If the project's own test suite has conventions, follow them; reading a mature project's test conventions is part of the learning here.

### G.3: The contribution

Do the work on a fork, and follow the upstream project's `CONTRIBUTING` guidelines to the letter (branch naming, commit style, changelog entries, whatever they ask).  Your pull request must include tests and documentation for what it changes.  Keep the diff as small as the fix allows; maintainers review diffs, and a disciplined diff is a professional courtesy they notice.

### G.4: The exchange

Submit the pull request and engage with what comes back: respond to review comments, make requested changes, and record the exchange in `contribution.md`.  A merge is ideal but not required.  Maintainer response times are outside your control, and the graded work is yours, not theirs.  If no maintainer responds within a week of submission, document the attempt and perform a written self-review against the project's own contributing standards: what would a maintainer flag, and why?

### Direction G depth checklist

- The scope was approved by the instructor within 3 days of hand-out, and `contribution.md` records the issue, its functional-paradigm substance, and the minimum viable scope.
- Specification-first evidence exists: the failing test (or documentation checklist) is preserved in its original form, dated before the fix.
- The pull request is public, linked, and includes tests and documentation, following the upstream project's contributing guidelines.
- The maintainer exchange is documented, or, if none occurred within a week, the attempt is documented and a written self-review against the project's standards stands in its place.
- The writeup connects the contribution back to the core: which of Parts 1-2's pure-function and fold disciplines the upstream code exercises, with specific examples from the code you touched.

---

## Deliverables

Submit a ZIP containing the files below.

| File or artifact | What it shows | Rubric row |
|------------------|---------------|------------|
| `higher_order.py` | Part 1: pure functions and combinators, `compose`, and the recursive `my_map` and `my_reduce`, each with its type signature and one-sentence description | Core: Pure Functions and Higher-Order Functions |
| `recursive_structures.py` | Part 2: the `BTree` and `LLNode` dataclasses with their map and fold operations | Core: Recursive Data Structures |
| Your direction's file(s), as named in its section | The direction work.  Direction F submits `logic.pl` and `logic_session.md` instead of Python direction files; Direction G submits `contribution.md` with the public pull request link | Direction Depth |
| `test_functional.py` | All tests for the core and your direction, with assertions.  Direction F's queries and expected answers live in `logic_session.md`; Direction G's tests live in the upstream pull request, linked from `contribution.md`; the core Part 1/Part 2 tests are still required in every direction | All three rows |
| `test_output.txt` | Output of running the test file, all tests passing | All three rows |
| `readme.md` | Approximately one page naming your chosen direction, answering the Part 1 theory questions, containing every writeup item on your direction's depth checklist, and closing with two or three sentences connecting the direction back to the core | Core: Pure Functions (theory questions) and Direction Depth |

Produce `test_output.txt` from your project folder with `python3 test_functional.py > test_output.txt`, and ensure reproducibility by listing your Python version (and, for Direction E, your CPU model and core count) in `readme.md`.

---

## Self-Check Before You Submit

- [ ] No `for`, no `while`, and no `=` appears inside any Part 1 solution body, and every `map` or `filter` result is consumed (no stray `<map object>`).
- [ ] `compose` works for any number of functions, and `my_map` and `my_reduce` are property-tested against the built-ins on at least five inputs each.
- [ ] Every Part 1 function carries a type-signature comment and a one-sentence description, and the three theory answers (with the referential-transparency demonstration) are in `readme.md`.
- [ ] `BTree` and `LLNode` are dataclasses; `tree_map`, `tree_fold`, `list_map`, and `list_fold` take a function argument and work for any operation; `tree_depth` and `tree_flatten` are written in terms of `tree_fold`.
- [ ] Every Part 2 operation is tested on at least four inputs, including the empty list and a single-node tree.
- [ ] Every item on your direction's depth checklist is met, and `readme.md` states what Parts 1 and 2's pure-function and fold disciplines contributed to the direction work.
- [ ] `test_output.txt` shows every test passing, and `readme.md` lists your Python version (and, for Direction E, CPU model and core count).

---

## Reflection Prompts

- Which constraint (no loops, or no assignment) changed your thinking more, and what did it force you to see?
- In Part 2, both `tree_depth` and `tree_flatten` were implemented in terms of `tree_fold`.  What does this tell you about the relationship between fold and other recursive operations?
- Why did you choose the direction you chose, and now that you have finished it, which *other* direction do you most wish you had time for, and what do you suspect it would have taught you?
- Every direction is the same paradigm at a different altitude: closures capture environments, continuations capture control, Church encodings capture data, combinators capture composition, parallelism captures the payoff of purity, logic programming captures relations instead of functions, and an upstream contribution captures the paradigm living in real code.  State, in your own words, the single idea they all share.
