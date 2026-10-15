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
| [G: Contribute to an Open-Source Language Ecosystem](#direction-g-contribute-to-an-open-source-language-ecosystem) | A scoped, functional-paradigm-relevant pull request with tests and documentation to [mal (Make-a-Lisp)](https://github.com/kanaka/mal), [Strudel](https://github.com/tidalcycles/strudel)/TidalCycles, a [tree-sitter](https://tree-sitter.github.io/tree-sitter/) grammar, or [SWI-Prolog](https://www.swi-prolog.org/) | The upstream project's language and tools, git, and GitHub | You want a public portfolio line, and you can get **instructor scope approval within 3 days of hand-out** |

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

Solution code and test code live in separate files.  Your functions go in `higher_order.py` and `recursive_structures.py`, and every assertion goes in `test_functional.py`, which imports the functions it checks.  You always run the test file, never the solution files.  This table shows which file each step works in, so you always know where new code goes:

| Step | File you work in | What you do there |
|---|---|---|
| First 30 Minutes | `higher_order.py`, `test_functional.py` | paste `total_length` and its first assertion, then run the test file |
| Before You Code (Part 1) | `explore_functional.py` | a scratch file you run once and do not submit |
| 1.1 | `higher_order.py` | add `product_of_odds`, `longest`, and `flatten_once` |
| 1.1 to 1.3 | `test_functional.py` | add the Part 1 assertions and the property test |
| 1.2 | `higher_order.py` | add `compose` |
| 1.3 | `higher_order.py` | add `my_map` and `my_reduce` |
| 1.4 | `readme.md` | answer the three theory questions |
| Before You Code (Part 2) | `explore_tree.py` | a scratch file you run once and do not submit |
| 2.1 | `recursive_structures.py` | add `BTree`, `tree_map`, `tree_fold`, `tree_depth`, and `tree_flatten` |
| 2.2 | `recursive_structures.py` | add `LLNode`, `list_map`, `list_fold`, `list_to_python`, and `list_from_python` |
| 2.1, 2.2 | `test_functional.py` | add the tree and linked-list assertions |
| Part 3 | your direction's files, as its section names them | the direction work and its tests |
| Deliverables | `test_output.txt` | capture the output of the finished test file |

### Your First 30 Minutes

1. Open `higher_order.py` and type in `total_length` below, together with the `from functools import reduce` line above it.  This is the one worked example in the core, and it exercises the whole Part 1 toolkit, so read it line by line before you run it.

   ```python
   # higher_order.py
   from functools import reduce

   # total_length: list[str] -> int
   # Total characters across the words longer than three letters.
   def total_length(words):
       return reduce(lambda acc, n: acc + n,
                     map(len, filter(lambda w: len(w) > 3, words)),
                     0)
   ```

   - `from functools import reduce`: `map` and `filter` are built in, but `reduce` lives in the `functools` module, so you import it.
   - The two comments: the type signature (a list of strings in, an integer out) and a one-sentence description.  Every Part 1 function needs both, because the rubric checks for them.
   - `filter(lambda w: len(w) > 3, words)`: keeps only the words longer than three letters.  It is lazy, so nothing runs yet.
   - `map(len, ...)`: turns each surviving word into its length, also lazily.
   - `reduce(lambda acc, n: acc + n, ..., 0)`: pulls the lengths through one at a time and adds each one to the running total `acc`, which starts at the seed `0`.
   - `return`: the whole body is one expression.  Read it from the inside out: filter, then map, then reduce.  There is no loop and no variable to update.

2. Open `test_functional.py` and give it two lines: the import `from higher_order import total_length`, and the first assertion from the test file in Step 1.1.
3. Run `python3 test_functional.py` from your project folder.  A silent exit means the assertion held.
4. Break it on purpose: in `higher_order.py`, change `> 3` to `> 5`, run the test file again, and read the traceback.  It ends with the assertion line and then a bare `AssertionError`, because no word is now long enough to count and the total is `0`.  Change it back.  That loop (edit, run, read the failure) is the whole workflow for the core.
5. Notice what is absent: no loop, no accumulator variable, no assignment.  If you catch yourself reaching for `total = 0` and a `for` loop, restate the problem as a chain of transformations instead.

> **If it fails.**
> - `ModuleNotFoundError: No module named 'higher_order'`: you ran from a different folder.  `cd` into `cs374-functional` and try again.
> - `NameError: name 'reduce' is not defined`: the `from functools import reduce` line is missing from the top of `higher_order.py`.
> - `ImportError: cannot import name 'total_length'`: the function name in `higher_order.py` is misspelled, or the file was not saved.

### Suggested Pacing

See the course schedule for the assigned and due dates.  Choose your direction on day one, and start the property-tested core early, because it works well in short sittings.  Direction G's scope approval falls due within three days of hand-out, so send it early.  Your team project's sprints run in parallel:

| Checkpoint | You should have |
|------------|----------------|
| On assignment | Part 1 underway: combinators, `compose`, and property-tested `my_map`/`my_reduce`; direction chosen, and Direction G scope approval sent |
| Checkpoint 1 | Part 1 complete, and Part 2 underway: tree and linked-list operations with edge-case tests |
| Checkpoint 2 | Part 2 complete; direction components working for the provided cases |
| Due date | Direction depth checklist complete; writeup and ZIP submitted |

---

## Part 1 (Core): Pure Functions and Higher-Order Functions

The constraints for this entire part: no `for` loops, no `while` loops, and no assignment statements (no `=`) inside solution function bodies.  You may use `map`, `filter`, `functools.reduce`, `lambda`, recursion, and `return`.  The constraints apply to solution bodies only; your test code in `test_functional.py` may loop freely.  All Part 1 code lives in `higher_order.py`.  Give every function its type signature as a comment and a one-sentence description, because the rubric checks for both; the comment above each `def` line below is its contract, so copy it into your file.

From here on, the page gives you each function's contract and its algorithm in plain steps, and you write the Python.

### Step 1.1: Write the Basic Combinators

These four functions are the vocabulary of the paradigm.  Each one is a short chain of `filter`, `map`, and `reduce`, and each has an edge case (an empty list, a tie) that you must decide and document.  `total_length`, from your first 30 minutes, is the worked example; the other three are yours.

**You write:** `higher_order.py` - `product_of_odds`, `longest`, and `flatten_once`; `test_functional.py` - their assertions.
**You run:** `python3 test_functional.py`

#### Before You Code: How Functions Live in Python

This part is ungraded, and it takes about ten minutes.  Every Part 1 function treats other functions as ordinary values, so let's see what that means before you rely on it.

| Idea | What it looks like | What it means |
|---|---|---|
| a function is a value | `yell = shout` | no parentheses, so nothing is called; `yell` is now a second name for the same function |
| `lambda` | `lambda x: x * x` | a function with no name whose body is one expression; it returns that expression's value |
| `map(f, xs)` | `map(len, ["hi", "hello"])` | a lazy iterator that will produce `f(x)` for each `x`; nothing runs until something asks |
| `filter(p, xs)` | `filter(lambda w: len(w) > 3, words)` | a lazy iterator over only the `x` for which `p(x)` is true |
| `list(...)` | `list(map(len, ["hi"]))` | pulls every value out of an iterator; an iterator runs only once, so a second `list(...)` is empty |
| `functools.reduce(f, xs, seed)` | `reduce(lambda acc, x: acc + x, xs, 0)` | starts with `acc = seed`, then replaces it with `f(acc, x)` for each `x` in turn, and returns the last `acc` |
| a closure | `lambda name: greeting + ", " + name` inside `make_greeter` | a function that remembers a variable from the scope where it was created |

`reduce` is the one that takes getting used to, so here it is by hand.  In `total_length(["hi", "hello", "world", "it"])`, the `filter` keeps `hello` and `world`, the `map` turns them into `5` and `5`, and the `reduce` does this:

| Step | `acc` before | `x` | `acc + x` |
|---|---|---|---|
| start | `0` (the seed) | | |
| 1 | `0` | `5` | `5` |
| 2 | `5` | `5` | `10` |
| end | | | returns `10` |

If the list is empty, `reduce` never calls the function and returns the seed.  That is why a `reduce` should pass a seed unless an earlier check has already ruled out the empty list: without one, `reduce` on an empty list raises `TypeError: reduce() of empty iterable with no initial value`.

To see all of this in action, save the lines below as `explore_functional.py`, a scratch file you do not submit, and run `python3 explore_functional.py` from your project folder.  The scratch file uses `=` freely; the no-assignment rule applies only to solution bodies.

```python
from functools import reduce

def shout(s):
    return s.upper() + "!"

yell = shout                  # no parentheses: yell is the function itself
print(yell("hi"))             # call it through its new name
print(type(shout).__name__)

square = lambda x: x * x      # a lambda is a one-expression function with no name
print(square(7))

squares = map(square, [1, 2, 3])
print(type(squares).__name__) # a lazy map object, not a list
print(list(squares))          # list(...) pulls every value out
print(list(squares))          # used up: an iterator runs only once

print(list(filter(lambda x: x % 2 == 0, [1, 2, 3, 4])))
print(reduce(lambda acc, x: acc + x, [1, 2, 3, 4], 0))
print(reduce(lambda acc, x: acc + x, [], 0))   # empty list: the seed comes back

def make_greeter(greeting):
    return lambda name: greeting + ", " + name  # the lambda captures greeting

hello = make_greeter("Hello")
howdy = make_greeter("Howdy")
print(hello("Ada"), "/", howdy("Ada"))
```

> **You should see.**
>
> ```text
> HI!
> function
> 49
> map
> [1, 4, 9]
> []
> [2, 4]
> 10
> 0
> Hello, Ada / Howdy, Ada
> ```
>
> **Predict** before you move on: `make_greeter` has already returned by the time `hello("Ada")` runs.  Where does `hello` find the word `Hello`?

> **Do this.**
> 1. In `higher_order.py`, below `total_length`, write the three functions from the contracts and algorithms below.
> 2. In `test_functional.py`, import them and write at least three assertions per function, starting from the test file below.
> 3. Run the tests from your project folder:
>
> ```bash
> python3 test_functional.py
> ```

```python
# higher_order.py, below total_length

# product_of_odds: list[int] -> int
# Product of the odd numbers; 1 for the empty list (the multiplicative identity).
def product_of_odds(nums):
    ...

# longest: list[str] -> str
# The longest word, found with a single reduce; the first one (left to right) on a tie;
# ValueError on an empty list.
def longest(words):
    ...

# flatten_once: list[list] -> list
# One level of flattening, using reduce; no itertools.
def flatten_once(lists):
    ...
```

Each body is one `return` of a `reduce`, plus a guard for `longest`.  `total_length` shows the shape: a `filter` or `map` goes inside, and `reduce` goes outermost.

**`product_of_odds`, step by step:**

1. Keep only the odd numbers.  A number is odd when its remainder after dividing by 2 is 1, and in Python that test also holds for negative odd numbers.
2. Combine the numbers that survive by multiplying them, two at a time.
3. Seed the combination with `1`.  A list with no odd numbers never multiplies anything, so the seed comes back, and that is the contract's answer for the empty list.

**`longest`, step by step:**

1. If the list is empty, raise a `ValueError` whose message names the function.  An `if` and a `raise` are not assignments, so they are allowed.
2. Otherwise, combine the words with a single `reduce`.  The accumulator is "the best word so far," and each step compares it with the next word.
3. At each step, keep the next word only if it is strictly longer than the best so far; otherwise keep the best.  Strictly longer, not "longer or equal," is what keeps the first word on a tie.
4. Step 1 already ruled out the empty list, so you may leave out the seed here.  The first word then starts as the best.

**`flatten_once`, step by step:**

1. Combine the inner lists with `reduce`.  The accumulator is the flat list built so far.
2. At each step, join the next inner list onto the end of the accumulator with list concatenation.  That joins one level only; a list inside an inner list stays a list.
3. Seed with the empty list, so that `flatten_once` of an empty list is an empty list.

**The test file.**  Write each new `assert` above the `print` line.  To test the empty-list error, test code may use a `try` block: call `longest` on an empty list, follow the call with an assertion that always fails (it runs only if no error was raised), and catch the `ValueError` so the file keeps going.

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

Replace the one-name import from your first 30 minutes with the four-name import above.

> **You should see.**
>
> ```text
> Part 1 tests pass.
> ```

> **If it fails.**  An `AssertionError` names a line; start there.  The most common causes:
> - `map` or `filter` returned a lazy object that you compared to a list.  `map(...) == [...]` is always `False`, so consume the iterator with `reduce` or `list()` first.
> - The failing line calls a function you have not finished.  A body of `...` returns `None`, and `None` equals nothing you are testing for.  Replace the `...` with a `return` line.
> - `longest` lost the tie rule.  The left word must win, so the comparison must ask "strictly longer," not "longer or equal."
> - A `for` loop or an `=` crept into a solution body.  Remove it, even if the test passes; the rubric checks for it.

### Step 1.2: Compose Functions

`compose(*fns)` returns a new function that applies the given functions left to right, so `compose(f, g, h)(x)` equals `h(g(f(x)))`.  It must work for any arity, which the rubric checks: `compose(f)` behaves like `f`, and `compose(f, g, h, i)` chains all four.  Decide what `compose()` with no arguments returns (the identity function is the natural choice) and say so in its description.  Add `compose` to `higher_order.py` using `functools.reduce` internally, not a loop; then add the assertion below, plus at least two of your own (a single-function and a three-function pipeline), to `test_functional.py` and run it again.

**You write:** `higher_order.py` - `compose`; `test_functional.py` - its assertions, above the `print("Part 1 tests pass.")` line.
**You run:** `python3 test_functional.py`

```python
# higher_order.py
# compose: (*Callable) -> Callable
# Left-to-right composition: compose(f, g, h)(x) == h(g(f(x))).
def compose(*fns):
    ...
```

```python
# in test_functional.py, below the first import line:
from higher_order import compose

# and with the other assertions, above the print line:
strip_lower_len = compose(str.strip, str.lower, len)
assert strip_lower_len("  Hello  ") == 5
```

`compose` is a closure factory.  It returns a function, and that function remembers the functions it was built from, just like `make_greeter` in the Before You Code section.  The `reduce` builds the pipeline one function at a time, and its accumulator is itself a function: "everything composed so far."

**`compose`, step by step:**

1. Start from the identity function, a one-argument function that hands back its argument unchanged.  It is the pipeline before any function is added, so it is the seed.  It is also what `compose()` returns, so say so in the description comment.
2. Reduce over `fns`.  The combining step receives two functions: the pipeline so far, and the next function in `fns`.
3. The combining step returns a NEW one-argument function.  Given `x`, that new function runs the pipeline so far on `x` first, then runs the next function on that result.  Left to right means the pipeline so far goes first.
4. Return what the `reduce` produces, without calling it.  `compose` returns a function, not a value.

Trace `compose(str.strip, str.lower, len)` on paper before you run it.  After the first step, `acc` is "identity, then `strip`."  After the second, it is "that, then `lower`."  After the third, it is "that, then `len`."

> **You should see.**
>
> ```text
> Part 1 tests pass.
> ```
>
> The line is the same as before, and that is the point: the new assertions passed silently above it.

> **If it fails.**
> - `TypeError: descriptor 'lower' for 'str' objects doesn't apply to a 'int' object`: the functions run right to left.  `len` ran first and handed `9` to `str.lower`.  In the new function your combining step builds, the pipeline so far must run first and the next function second.
> - `TypeError: reduce() of empty iterable with no initial value`, from `compose()`: the seed is missing.  `reduce` needs the identity function as its starting value.
> - `TypeError: descriptor 'strip' for 'str' objects doesn't apply to a 'function' object`: the combining step calls the next function right away, on the pipeline itself, instead of returning a new one-argument function.  It handed a function to `str.strip`.

### Step 1.3: Write my_map and my_reduce Recursively

Implement `my_map(f, xs)` and `my_reduce(f, xs, seed)` recursively, with no loops and no list comprehensions inside the body.  Each has a base case (the empty list) and a recursive case (do something with the first element, then recurse on the rest).  Add both to `higher_order.py`:

**You write:** `higher_order.py` - `my_map` and `my_reduce`; `test_functional.py` - the property test, below the `print("Part 1 tests pass.")` line.
**You run:** `python3 test_functional.py`

```python
# higher_order.py
# my_map: (Callable, list) -> list
# A recursive map: f applied to each x in xs, in order, built without a loop.
def my_map(f, xs):
    ...

# my_reduce: (Callable, list, Any) -> Any
# A recursive left fold: combine seed with each element of xs, left to right.
def my_reduce(f, xs, seed):
    ...
```

In Python, the head of a list is `xs[0]` and the tail is `xs[1:]`, a new list holding everything after the head.  The tail of a one-element list is `[]`, so every recursive call is on a shorter list and the recursion reaches the base case.  An empty list is falsy, which gives you a short test for "is this list empty?"

**`my_map`, step by step:**

1. Base case: if `xs` is empty, return an empty list.  Mapping over nothing gives nothing.
2. Recursive case: apply `f` to the head, and put that one result in a one-element list.
3. Call `my_map` with the same `f` on the tail.  Trust it to map the rest of the list.
4. Join the two lists with list concatenation, the mapped head first, and return the result.  This joining is the "cons" of the functional world: one item on the front of a smaller list.

**`my_reduce`, step by step:**

1. Base case: if `xs` is empty, return `seed`.  When the list runs out, the seed holds the whole answer.
2. Recursive case: combine the seed with the head by calling `f`.  Pass the accumulator first and the element second, to match `functools.reduce`.
3. Return the result of calling `my_reduce` on the tail, with that combined value as the new seed.  Nothing happens after the recursive call returns; the seed carries all the work forward.

**Predict** before you run it: in `my_reduce`, how many times is `f` called on a list of five items, and what is `seed` on the last call?

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

> **You should see.**
>
> ```text
> Part 1 tests pass.
> All my_map and my_reduce properties hold.
> ```

> **If it fails.**
> - `IndexError: list index out of range`: the base case does not `return`.  The function checks for the empty list, then falls through and reads the head of that empty list.
> - `RecursionError: maximum recursion depth exceeded`: a recursive call passes the whole list instead of its tail, so the list never gets shorter.
> - The addition test passes even if `f`'s arguments are swapped, because `a + b == b + a`.  To catch that bug, also compare the two with a subtraction function, or with a function that appends each item to an accumulator list seeded with `[]`.

### Step 1.4: Answer the Functional Theory Questions (in your writeup)

Answer three written questions in your writeup, `readme.md`.  They draw on the Programming Paradigms and Functional Programming sessions, and I grade them within Part 1's rubric row.

**You write (in `readme.md` under a `## Part 1: Theory Questions` heading):** the three answers below, including your own small impure function for question 1.
**You run:** your impure function, once with the call and once with its result substituted, so you can paste both outputs into the answer.

1.  **Referential transparency, demonstrated.**  Define referential transparency in one sentence.  Then take `total_length` above and show that replacing any call with its result preserves the program.  Next, exhibit one small *impure* Python function of your own (one that uses mutation or I/O) where that replacement changes behavior, and name exactly which property broke.
2.  **Paradigm placement.**  Classify each of these as imperative, functional, or declarative, and state which *question* each paradigm makes the programmer answer ("how, step by step?", "what combination of transformations?", "what result?"):
    - `total = 0` / `for n in nums: total += n`
    - `reduce(lambda a, b: a + b, nums, 0)`
    - `SELECT SUM(n) FROM nums;`
3.  **Purity's price.**  Name one thing your Part 1 constraints (no loops, no assignment) made harder, and one thing they made automatic (testing, reasoning, or parallelism).  Tie each to a property of pure functions rather than to taste.

---

## Part 2 (Core): Recursive Data Structures

Both structures in this part are recursive: a tree contains smaller trees, and a list contains a smaller list.  A fold is the one operation that visits the whole structure and combines what it finds, and you will define the other operations in terms of it.  All Part 2 code lives in `recursive_structures.py`, and its tests go in `test_functional.py` alongside Part 1's.  Each step gives you a specification: what every function takes, what it returns, and its edge cases.  The algorithm is yours to design, using the Part 1 recursion pattern.  Copy each function's contract into a type-signature comment and a one-sentence description above it, as in Part 1.  The rubric's proficient row asks that every operation take a function argument and work for any operation (not hardcoded to addition).

### Step 2.1: Build the Binary Tree and Its Fold

A binary tree is either empty, written `None`, or a node holding a value and two smaller trees.  Every function in this step follows that definition: one case for `None`, and one case for a node that recurses on both children.

**You write:** `recursive_structures.py` - `BTree`, `tree_map`, `tree_fold`, `tree_depth`, and `tree_flatten`; `test_functional.py` - the tree assertions, at the bottom of the file.
**You run:** `python3 test_functional.py`

#### Before You Code: How a Recursive Dataclass Lives in Python

This part is ungraded.  A `@dataclass` is a class whose fields you list once, with their types; Python writes the constructor, the printed form, and `==` for you.  `BTree` is recursive because two of its fields hold more `BTree`s, or `None`.

| You write | What Python gives you |
|---|---|
| `BTree(1, BTree(2), BTree(3))` | a node with value `1`; `left` and `right` default to `None` when you leave them out |
| `t.value`, `t.left`, `t.right` | the three fields, read by name |
| `print(t)` | `BTree(value=1, left=..., right=...)`, every field spelled out, all the way down |
| `t == BTree(1, BTree(2), BTree(3))` | `True`: `==` compares the fields, recursively, so two separately built trees with the same shape and values are equal |
| `@dataclass(frozen=True)` | the same class, except that assigning to a field raises `FrozenInstanceError`.  Directions C and D use it.  `BTree` stays a plain `@dataclass` here, and your functions keep it unchanged by never assigning to a field. |

That `==` is what makes the tests readable: `assert tree_map(...) == BTree(2, BTree(4), BTree(6))` compares whole trees in one line.

Save the lines below as `explore_tree.py`, a scratch file you do not submit, and run `python3 explore_tree.py`.  `count_nodes` is a fold with `+` built in.  `tree_fold` will be the same function with the combining step passed in as an argument.

```python
from dataclasses import dataclass
from typing import Optional, Any

@dataclass
class BTree:
    value: Any
    left: Optional['BTree'] = None
    right: Optional['BTree'] = None

t = BTree(1, BTree(2), BTree(3))
print(t)
print(t.left.value, t.right.right)
print(t == BTree(1, BTree(2), BTree(3)))   # == compares the fields, all the way down

def count_nodes(tree):
    if tree is None:
        return 0
    return count_nodes(tree.left) + 1 + count_nodes(tree.right)

print(count_nodes(t), count_nodes(None))

@dataclass(frozen=True)
class Point:
    x: int
    y: int

p = Point(1, 2)
try:
    p.x = 5
except Exception as e:
    print(type(e).__name__)
print(p)
```

> **You should see.**
>
> ```text
> BTree(value=1, left=BTree(value=2, left=None, right=None), right=BTree(value=3, left=None, right=None))
> 2 None
> True
> 3 0
> FrozenInstanceError
> Point(x=1, y=2)
> ```
>
> **Predict** before you move on: what is the smallest change that makes `count_nodes` compute the sum of the values instead of the number of nodes?

> **Do this.**
> 1. In `recursive_structures.py`, define the `BTree` dataclass and implement the four operations in the specification below.  `tree_map` must not modify the original tree (it is a pure function), and `tree_depth` and `tree_flatten` must be written in terms of `tree_fold`.
> 2. In `test_functional.py`, import them and test every operation on all four test trees listed after the specification.
> 3. Run `python3 test_functional.py`.

**`BTree`** is a `@dataclass` with three fields, in this order: `value` (any type), then `left` and `right` (each an optional `BTree`, defaulting to `None`).  The Before You Code scratch file defines exactly this class, with the imports it needs.

| Function | Takes | Returns | Required behavior and edge cases |
|---|---|---|---|
| `tree_map(f, tree)` | a function and an optional `BTree` | a NEW optional `BTree` | The same shape, with every value replaced by `f` of that value; the original tree is unchanged.  `None` maps to `None`.  Doubling `BTree(1, BTree(2), BTree(3))` gives `BTree(2, BTree(4), BTree(6))`. |
| `tree_fold(f, tree, seed)` | a three-argument function, an optional `BTree`, and a seed | one value | At each node, the result is `f` called with the left child's fold, the node's value, and the right child's fold, in that order.  A `None` tree folds to `seed`.  With a function that adds its three arguments and the seed `0`, the fold is the sum of all values. |
| `tree_depth(tree)` | an optional `BTree` | an `int` | The number of nodes on the longest path from the root down to a leaf.  `None` has depth 0, and a leaf has depth 1.  Written as one call to `tree_fold`. |
| `tree_flatten(tree)` | an optional `BTree` | a list | All values in in-order traversal: the left subtree, then the root, then the right subtree.  `None` flattens to `[]`.  Written as one call to `tree_fold`. |

Every function has the same two cases as `count_nodes`: one for `None`, and one for a node that recurses on both children.

**Test trees to use:** the empty tree `None` (every function returns its seed or identity value); the single node `BTree(42)` (map doubles it, fold sums it, depth is 1); the full tree `BTree(1, BTree(2, BTree(4), BTree(5)), BTree(3))`; and the right-skewed tree `BTree(1, None, BTree(2, None, BTree(3)))`.

Start the tree tests at the bottom of `test_functional.py`, below the `my_map` property test, like this:

```python
from recursive_structures import BTree, tree_map, tree_fold, tree_depth, tree_flatten

full = BTree(1, BTree(2, BTree(4), BTree(5)), BTree(3))
skew = BTree(1, None, BTree(2, None, BTree(3)))
assert tree_map(lambda x: x*2, BTree(1, BTree(2), BTree(3))) == BTree(2, BTree(4), BTree(6))
assert tree_fold(lambda l, v, r: l + v + r, full, 0) == 15
assert tree_flatten(full) == [4, 2, 5, 1, 3]
assert tree_depth(full) == 3 and tree_depth(skew) == 3
# TODO: every operation on all four test trees, including None and BTree(42)
print("Part 2 tree tests pass.")
```

> **You should see.**
>
> ```text
> Part 1 tests pass.
> All my_map and my_reduce properties hold.
> Part 2 tree tests pass.
> ```

> **If it fails.**
> - `RecursionError: maximum recursion depth exceeded`: a recursive case never reaches `None`.  Check that every recursive call is on `tree.left` or `tree.right`, not on `tree` itself.
> - `AttributeError: 'NoneType' object has no attribute 'value'`: the `None` check is missing or comes after a line that reads `tree.value`.  The `None` case must be checked before any field is read.
> - `TypeError: <lambda>() takes 2 positional arguments but 3 were given`: `tree_fold` calls `f` with three values, so every combining function needs three parameters (left result, value, right result), even if it ignores the value.
> - `tree_flatten` returns the values in the wrong order: the combining function put the node's value first instead of between the two child lists.

### Step 2.2: Build the Linked List and Its Fold

A linked list is either empty, written `None`, or a node holding one value (`head`) and a smaller list (`tail`).  So `LLNode(1, LLNode(2, LLNode(3)))` is the list 1, 2, 3, and it prints as `LLNode(head=1, tail=LLNode(head=2, tail=LLNode(head=3, tail=None)))`.

**You write:** `recursive_structures.py` - `LLNode`, `list_map`, `list_fold`, `list_to_python`, and `list_from_python`, below the tree code; `test_functional.py` - the list assertions, at the bottom of the file.
**You run:** `python3 test_functional.py`

> **Do this.**
> 1. Add the `LLNode` dataclass and the four operations below to `recursive_structures.py`.  The linked list is the same pattern with one child instead of two, and it closes the loop with Part 1: import `my_reduce` from `higher_order.py` at the top of `recursive_structures.py`, and build `list_from_python` from it (no loops).
> 2. Test each operation in `test_functional.py` on at least four inputs, including the empty list (`None`) and a single node.
> 3. Run `python3 test_functional.py`.

**`LLNode`** is a `@dataclass` with two fields, in this order: `head` (any type), then `tail` (an optional `LLNode`, defaulting to `None`).  `None` represents the empty list.

| Function | Takes | Returns | Required behavior and edge cases |
|---|---|---|---|
| `list_map(f, node)` | a function and an optional `LLNode` | a NEW optional `LLNode` | Every element replaced by `f` of that element, in the same order; the original list is unchanged.  `None` maps to `None`. |
| `list_fold(f, node, seed)` | a two-argument function, an optional `LLNode`, and a seed | one value | A left fold: `f` combines the accumulator (first argument) with each element (second argument), from left to right, starting at `seed`.  `None` folds to `seed`.  Folding addition over the list 1, 2, 3 with the seed `0` gives `6`. |
| `list_to_python(node)` | an optional `LLNode` | a Python list | The same elements in the same order.  `None` gives `[]`.  Written as one call to `list_fold`. |
| `list_from_python(lst)` | a Python list | an optional `LLNode` | The same elements in the same order.  `[]` gives `None`.  Written as one call to `my_reduce` from Part 1, with no loops. |

For `list_from_python`, notice that a new node always goes on the front of the list built so far.  Which element of `lst` must be placed first?

Start the list tests at the bottom of `test_functional.py`:

```python
from recursive_structures import LLNode, list_map, list_fold, list_to_python, list_from_python

assert list_to_python(list_from_python([1, 2, 3])) == [1, 2, 3]
assert list_from_python([]) is None
assert list_fold(lambda acc, x: acc + x, LLNode(1, LLNode(2, LLNode(3))), 0) == 6
# TODO: each operation on at least four inputs, including None and a single node
print("Part 2 list tests pass.")
```

> **You should see.** The finished core prints four lines.  This is the output your `test_output.txt` must contain, plus a line for each direction section you add:
>
> ```text
> Part 1 tests pass.
> All my_map and my_reduce properties hold.
> Part 2 tree tests pass.
> Part 2 list tests pass.
> ```

> **If it fails.**
> - `list_to_python(list_from_python([1, 2, 3]))` gives `[3, 2, 1]`: the nodes were placed in the order the elements appear in `lst`, and each new node went on the front, so the first element ended up at the back.
> - `ImportError: cannot import name 'my_reduce' from 'higher_order'`: either `my_reduce` is misspelled in `higher_order.py`, or `higher_order.py` imports from `recursive_structures.py` (a circular import).  The import goes one way only, from Part 2 to Part 1.
> - `AttributeError: 'NoneType' object has no attribute 'head'`: the `None` check is missing or comes too late, exactly as in Step 2.1.

---

## Part 3: Your Direction (choose exactly one)

Read only the direction you chose.  Every direction below has the same shape: what you build and need, numbered steps, and a depth checklist.  The checklist is the line between "the components work" (progressing) and "the direction reached its stated depth" (proficient), so treat it as the specification.

## Direction A: Closures and Lazy Generators

Two files, `closures.py` and `generators.py`.  In the first you write function factories (functions that return functions) and see exactly what a returned function carries with it.  In the second you write sequences that never end and pipelines that compute only what is asked for.  You need `closures.py` and `generators.py` in your `cs374-functional` folder, tests in `test_functional.py`, and the standard library only (`typing.Callable` for signatures and `time.perf_counter()` for the strict-vs-lazy comparison in A.2).  The Closures class material falls early in this assignment's window (see the course schedule); read ahead in that activity if you want to start sooner.

### A.1: Closures and Function Factories

A closure is a function that captures variables from the scope where it was created.  When a factory function creates and returns an inner function, the inner function keeps access to the factory's local variables even after the factory has returned.  Every call to a factory must produce an independent function.

**You write:** `closures.py` - `make_adder`, `make_multiplier`, `make_between`, `make_counter`, `make_once`, and `memoize`; `test_functional.py` - the closure tests, at the bottom of the file.
**You run:** `python3 test_functional.py`

> **Do this.**
> 1. Create `closures.py` with the five factories and `memoize` from the specification below.  `make_greeter`, in Part 1's Before You Code section, shows the capture.
> 2. For `make_counter`, keep the state in a list or a mutable default argument; Python's `nonlocal` also works, but a list demonstrates the capture directly.
> 3. Test each one in `test_functional.py`, including the independence checks and the decorator form shown below.
> 4. In your writeup, draw an ASCII diagram (or describe in prose) showing what each closure returned by `make_adder(5)` and `make_adder(10)` captures internally, and why the two closures do not share state.

Every factory returns a function; none of them returns a value directly.  Give each one its type signature in a comment, as in Part 1, and import `Callable` from `typing` for the annotations.

| Function | Takes | Returns | Required behavior and edge cases |
|---|---|---|---|
| `make_adder(n)` | an `int` | a one-argument function | The returned function adds `n` to its argument. |
| `make_multiplier(n)` | an `int` | a one-argument function | The returned function multiplies its argument by `n`. |
| `make_between(lo, hi)` | two `int`s | a one-argument predicate | The predicate is `True` when its argument lies in the closed interval from `lo` to `hi`, both ends included. |
| `make_counter(start=0)` | an optional `int` | a zero-argument function | Each call returns the next integer, beginning with `start`.  Two counters never share a count. |
| `make_once(f)` | a function | a function | The first call runs `f` and returns its result; every later call returns that same first result without running `f` again.  This holds even when `f` returns `None`. |
| `memoize(f)` | a function | a function | Returns what `f` returns, but computes `f` only once per distinct set of arguments, for any hashable arguments.  It must work as a decorator. |

Add the tests below to the bottom of `test_functional.py`:

```python
from closures import make_adder, make_multiplier, make_between, make_counter, make_once, memoize

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
# TODO: tests for make_multiplier and make_once, and an independence check for each factory
print("Direction A closure tests pass.")
```

> **You should see.** The four core lines, then `Direction A closure tests pass.`, and `fib(30)` returns in well under a second.  If it takes several seconds, `memoize` is not caching.  A common cause is building the cache inside the returned function, so every call starts with an empty dictionary.

### A.2: Lazy Sequences with Generators

Strict (eager) evaluation computes every element of a sequence immediately.  Lazy evaluation computes an element only when someone asks for it.  Laziness matters for infinite sequences, which cannot fit in memory, and for pipelines that stop early and so skip the remaining work.

**You write:** `generators.py` - `naturals`, `fibonacci`, `take`, `gen_map`, `gen_filter`, and the strict-vs-lazy timing under `if __name__ == "__main__":`; `test_functional.py` - the generator tests.
**You run:** `python3 test_functional.py`, then `python3 generators.py` for the timing.

> **Do this.**
> 1. Create `generators.py` from the specification below.  Every function that produces a sequence must use `yield`, and the two infinite generators must run indefinitely in O(1) extra memory.
> 2. Test with `take`, never with `list()`, on the infinite generators.  If a test hangs, a generator is being consumed to the end: the usual culprits are `list(naturals())`, a `for` loop over an infinite generator with no `break`, or a `take` that loops on the iterator instead of stopping after `n` items.
> 3. Build the lazy pipeline below: the first 10 perfect squares that are also even, using only `gen_map`, `gen_filter`, `naturals`, and `take`, with no list comprehensions and no intermediate lists.
> 4. Strict vs. lazy: find the first Fibonacci number greater than 1000 two ways, first by materializing a large list, then lazily one element at a time.  Time both with `time.perf_counter()`.

| Function | Takes | Produces | Required behavior and edge cases |
|---|---|---|---|
| `naturals(start=0)` | an optional `int` | a generator | Yields `start`, `start + 1`, `start + 2`, and so on forever, in O(1) extra memory. |
| `fibonacci()` | nothing | a generator | Yields `0, 1, 1, 2, 3, 5, 8, ...` forever, in O(1) extra memory. |
| `take(n, it)` | an `int` and any iterable | a list | The first `n` elements of `it`, in order.  If `it` runs out before `n` elements, return the ones it had, without an error. |
| `gen_map(f, it)` | a function and any iterable | a generator | Lazily yields `f(x)` for each `x` in `it`, computing each one only when asked. |
| `gen_filter(pred, it)` | a predicate and any iterable | a generator | Lazily yields only the `x` in `it` for which `pred(x)` is true. |

Loops are allowed in this direction.  A loop inside a generator runs one step each time someone asks for the next value, which is what makes it lazy.

The timing harness below is provided.  Fill in the two marked lines, using only your own functions plus a way to pull the first matching value out of an iterator.

```python
# generators.py, at the bottom
if __name__ == "__main__":
    import time
    start = time.perf_counter()
    # TODO strict: build a list of the first 20,000 Fibonacci numbers, then set
    #              strict_answer to the first one in that list over 1000
    strict_time = time.perf_counter() - start
    start = time.perf_counter()
    # TODO lazy: set lazy_answer to the first Fibonacci number over 1000, computing
    #            only as many Fibonacci numbers as it takes to find it
    lazy_time = time.perf_counter() - start
    print(f"strict: {strict_answer} in {strict_time:.6f} s")
    print(f"lazy:   {lazy_answer} in {lazy_time:.6f} s")
```

The `if __name__ == "__main__":` guard keeps the timing code from running when `test_functional.py` imports `generators.py`.  Add the tests below to the bottom of `test_functional.py`:

```python
from generators import naturals, fibonacci, take, gen_map, gen_filter

assert take(5, naturals()) == [0, 1, 2, 3, 4]
assert take(5, gen_map(lambda x: x**2, naturals(1))) == [1, 4, 9, 16, 25]
assert take(5, gen_filter(lambda x: x % 2 == 0, naturals())) == [0, 2, 4, 6, 8]
result = take(10, gen_filter(lambda x: x % 2 == 0, gen_map(lambda x: x**2, naturals(1))))
assert result == [4, 16, 36, 64, 100, 144, 196, 256, 324, 400]
# TODO: a test for fibonacci, and take on a finite iterator shorter than n
print("Direction A generator tests pass.")
```

> **You should see.** From `python3 test_functional.py`, the earlier lines and then `Direction A generator tests pass.`  From `python3 generators.py`, both methods report `1597`.  Your times will differ from these, but the lazy one should be smaller by orders of magnitude:
>
> ```text
> strict: 1597 in 0.018543 s
> lazy:   1597 in 0.000009 s
> ```

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

**You write:** `continuations.py` - the AST dataclasses, `Env`, `Closure`, `interp`, then `interp_k`; `test_functional.py` - the equivalence tests.
**You run:** `python3 continuations.py` for the smoke tests, then `python3 test_functional.py`.

> **Do this.**
> 1. Write the direct-style `interp(expr, env)` first: a miniature of your Interpreter assignment with dataclass AST nodes `Num`, `Bool`, `Var`, `BinOp`, `If`, `Let`, `Lam`, `App`, an `Env` chain, and a `Closure` value.  It is under sixty lines.
> 2. Smoke-test it on `(λx. x + 1)(41)` -> `42.0` and `let y = 10 in y * y` -> `100.0` before you change anything.
> 3. Copy it to `interp_k(expr, env, k)` and transform one case at a time, re-running the equivalence tests after each case.

Start the direct-style half from these provided AST nodes.  The field order of each node matters, because `match` patterns such as `BinOp(op, left, right)` and the hand-built ASTs in B.3 (`Lam("k", ...)`, `App(Var("k"), ...)`) read the fields in that order.  `Env` is your Interpreter's `Environment` under a shorter name.

```python
# continuations.py
from dataclasses import dataclass
import operator

@dataclass
class Num:
    n: float

@dataclass
class Bool:
    b: bool

@dataclass
class Var:
    name: str

@dataclass
class BinOp:
    op: str            # "+", "-", "*", "/", "<", "=="
    left: object
    right: object

@dataclass
class If:
    cond: object
    then: object
    orelse: object

@dataclass
class Let:
    name: str
    value: object
    body: object

@dataclass
class Lam:
    param: str
    body: object

@dataclass
class App:
    fn: object
    arg: object

OPS = {"+": operator.add, "-": operator.sub, "*": operator.mul,
       "/": operator.truediv, "<": operator.lt, "==": operator.eq}

class Env:
    def __init__(self, parent=None):
        self._bindings = {}
        self._parent = parent

    def define(self, name, value):
        ...  # binds name in THIS scope only

    def lookup(self, name):
        ...  # the value bound to name here or in an enclosing scope; NameError if none

@dataclass
class Closure:
    param: str
    body: object
    env: Env           # the environment where the Lam was evaluated

def interp(expr, env):
    ...  # the value of expr in env, one case per AST node

if __name__ == "__main__":
    print(interp(App(Lam("x", BinOp("+", Var("x"), Num(1))), Num(41)), Env()))
    print(interp(Let("y", Num(10), BinOp("*", Var("y"), Var("y"))), Env()))
```

What each node means is the same as in your Interpreter assignment:

- `Num` evaluates to a Python `float`, and `Bool` to a Python `bool`.
- `Var` looks its name up in the environment.
- `BinOp` evaluates both operands and applies the matching function from `OPS`.
- `If` evaluates its condition, then only the branch it picks.
- `Let` evaluates its value, binds it to its name in a new child scope, and evaluates its body there.
- `Lam` evaluates to a `Closure` that remembers the current environment.
- `App` evaluates the function to a closure and the argument to a value, then evaluates the closure's body in a child of the closure's environment, with the parameter bound to that value.

> **You should see.** `42.0` and then `100.0`, from `python3 continuations.py`.

Next, write `interp_k(expr, env, k)` in the same file, below `interp`.  It has one case per AST node, exactly like `interp`, and it computes the same value.  The difference is the invariant: no case may return a value to its caller.  Every case ends by passing its value to `k`, or by calling `interp_k` on a smaller expression with a continuation that will.  The mechanical rule for getting there: wherever direct style evaluates a subexpression and then uses its value, CPS evaluates the subexpression with a continuation that receives the value and does the rest.

**Verify equivalence:** for every test expression, `interp_k(e, env, lambda v: v)` must equal `interp(e, env)`.  Cover at least `Num`, `BinOp` (nested), `If` (both branches), `Let`, and `App`.  Reading any `interp_k` case top to bottom, the last thing it does must be a call to `k` (or to another `_k` function that will).

### B.2: Trampolining

Python does not optimize tail calls, so deep recursion still overflows the stack.  Wrap every tail call in a zero-argument `Thunk` and drive execution with a loop.

**You write:** `continuations.py` - `Thunk`, `trampoline`, and the `Thunk`-returning version of `interp_k`; `test_functional.py` - the 2,000-deep `Let` test.
**You run:** `python3 test_functional.py`

- `Thunk(f)` is a small class that holds one zero-argument function, `f`, for later.  Creating a `Thunk` runs nothing.
- `trampoline(result)` takes either a `Thunk` or a final value.  As long as it holds a `Thunk`, it runs that thunk's function and keeps whatever comes back.  It returns the first result that is not a `Thunk`.  Because each thunk runs from inside this one loop, the Python stack never grows.

> **Do this.**
> 1. Change each tail call in `interp_k` so that it returns a `Thunk` holding that call instead of making the call, and run the top-level entry through `trampoline`.
> 2. Build a chain of 2,000 nested `Let` bindings (comfortably past Python's default recursion limit) and verify that it evaluates to the right answer.
> 3. Run the same AST through the un-trampolined `interp_k` once to watch the `RecursionError` you just eliminated, and keep that comparison for your writeup.

### B.3: call/cc

Add a `Callcc(fun)` AST node.  In the CPS interpreter, the current continuation is *exactly* the `k` in hand.  Wrap it in a `Continuation` object that, when called, raises a `ContinuationEscape` carrying the value; the top-level `run` driver catches the escape and resumes.

**You write:** `continuations.py` - `Callcc`, `ContinuationEscape`, `Continuation`, the `Callcc` case of `interp_k`, an `App` case that also accepts a `Continuation`, and `run`; `test_functional.py` - the three demonstrations.
**You run:** `python3 test_functional.py`

```python
@dataclass
class Callcc:
    fun: object                    # an expression that evaluates to a one-parameter Closure
```

The rest of B.3, as a specification:

- `ContinuationEscape` is an `Exception` subclass that carries two attributes, `k` and `value`.
- `Continuation(k)` stores the `k` that was in hand when `Callcc` was evaluated.  Calling a `Continuation` with a value raises a `ContinuationEscape` carrying that stored `k` and the value.
- The `Callcc(fun)` case of `interp_k` evaluates `fun` to a closure and runs that closure's body with its parameter bound to `Continuation(k)`.  The body's continuation is the same `k`, so a body that never uses its parameter behaves as a normal call.
- The `App` case must also accept a `Continuation` as the function value, and call it with the argument.
- `run(expr, env=None)` evaluates `expr` with the identity continuation, in `env` or a fresh `Env`.  When a `ContinuationEscape` reaches it, `run` resumes the computation by handing the escape's value to the escape's `k`, and returns what that produces.

Demonstrate each of the following as a hand-built AST run through `run`:

1. `call/cc` whose function ignores the continuation behaves as a normal call: `Callcc(Lam("k", Num(42)))` -> `42.0`.
2. Invoking the continuation escapes immediately: `Callcc(Lam("k", App(Var("k"), Num(7))))` -> `7.0`.
3. After an escape, pending computation is discarded: bind `call/cc(λk. k(5))` in a `Let` whose body multiplies by 1000, and document which value your implementation produces and why.

### B.4: One control structure from scratch

Using the two-continuation pattern (a normal-return `k` and an escape `k`), implement **either** `for_until` **or** `with_handler`.  `for_until` is break as a continuation: iterate a body that may call `break_fn(v)` to exit with `v`.  `with_handler` is exceptions as continuations: `raise_fn` is simply "call the handler's continuation," and it must propagate correctly through nested handlers.  Test the one you build, including the nested case.

**You write:** `continuations.py` - `for_until` or `with_handler`; `test_functional.py` - its tests, including the nested case.
**You run:** `python3 test_functional.py`

These two signatures are one workable shape, written as plain CPS Python functions rather than AST nodes.  You may choose another shape if you document it in your readme.

```python
# for_until: (list, Callable, Callable) -> Any
# body(x, break_fn, continue_k) handles one item.  It calls continue_k(None) to go on to
# the next item, or break_fn(v) to leave the loop with v.  When the items run out, the
# loop passes None to k.  break_fn is the loop's own k: escaping means skipping the rest.
def for_until(items, body, k):
    ...

# with_handler: (Callable, Callable, Callable) -> Any
# body(raise_fn, k) runs normally and passes its value to k.  raise_fn(err) abandons the
# body and runs handler(err, k) instead.  A handler may call an outer raise_fn to re-raise.
def with_handler(body, handler, k):
    ...
```

With these shapes, `for_until([1, 2, 5, 7], lambda x, brk, cont: brk(x) if x > 3 else cont(None), lambda v: v)` returns `5`, and the same loop over `[1, 2]` returns `None`.

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

**You write:** `lambda_calc.py` - `LVar`, `LLam`, `LApp`, `free_vars`, `subst`, `step_normal`, and `normalize`; `test_functional.py` - the three adversarial substitution tests.
**You run:** `python3 test_functional.py`

> **Do this.**
> 1. Create `lambda_calc.py` with the three provided AST dataclasses below, then write `free_vars` from its specification.
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

# free_vars: term -> set[str]; the names that occur free in term
def free_vars(term) -> set[str]:
    ...

# subst: (term, str, term) -> term; every free occurrence of var replaced, capture-avoiding
def subst(term, var: str, replacement):
    ...

# step_normal: term -> term | None; one normal-order step, or None in normal form
def step_normal(term):
    ...

# normalize: term -> term; step until normal form or until max_steps steps have run
def normalize(term, max_steps=1000, trace=False):
    ...
```

The specification for each function:

- `free_vars` returns a new set and never changes `term`.  A variable is free unless an enclosing `LLam` binds its name.
- `subst` follows the standard definition, one case per constructor.  A binder with the same name as `var` shadows it, so substitution stops there.  When a binder's name is free in `replacement`, rename the binder (and its uses in the body) to a fresh name that is free in neither term, then continue.
- `step_normal` contracts exactly one redex, the leftmost-outermost one, and returns the new term.  It returns `None` when `term` has no redex.
- `normalize` returns the normal form.  With `trace=True`, it prints each intermediate term.  If `max_steps` steps run without reaching normal form, it prints a message naming the limit and the last term, then returns that term without crashing.

**Adversarial substitution tests**: your substitution must pass these capture traps, and your writeup must display them:

- $$(\lambda y.\, x)[x := y]$$: naive substitution captures $$y$$; correct substitution renames the binder first.
- $$(\lambda y.\, x\ y)[x := y\ z]$$: the same trap, one level deeper.
- One trap of your own design that defeats a substitution function lacking the fresh-variable case.  Show the wrong answer naive substitution produces.

> **You should see.** For the first trap, a result of the shape $$\lambda y'.\, y$$ (a renamed binder with the free $$y$$ intact), never $$\lambda y.\, y$$.  If you get the identity function, the binder was not renamed and the free variable was captured.

### C.2: The encodings

Encode each of the following as terms in your AST, and verify them mechanically through your reducer:

**You write:** `lambda_calc.py` - the encodings as module-level constants, and `alpha_equiv`; `test_functional.py` - one test per law.
**You run:** `python3 test_functional.py`

Each encoding is a value built from the three constructors.  Application is left-associative, so `TRUE a b` is `LApp(LApp(TRUE, a), b)`.  A small helper built on Part 1's `reduce` saves the nesting:

```python
from functools import reduce

TRUE  = LLam("t", LLam("f", LVar("t")))     # λt.λf.t, written in the AST
FALSE = ...  # λt.λf.f
# Also: AND, OR, NOT, IF; ZERO through FOUR, SUCC, ADD, MUL; PAIR, FST, SND

# app: (term, term, ...) -> term; left-associative application, app(f, a, b) == LApp(LApp(f, a), b)
def app(*terms):
    return reduce(LApp, terms)

# alpha_equiv: (term, term) -> bool
# True when the two terms differ only in the names of bound variables.
def alpha_equiv(t1, t2, env1=None, env2=None) -> bool:
    ...
```

For `alpha_equiv`, `env1` and `env2` are yours to define; one workable strategy records, for each bound name, how deep its binder sits.

For example, `normalize(app(TRUE, LVar("a"), LVar("b")))` must return `LVar(name='a')`.

- **Booleans:** `TRUE = λt.λf.t`, `FALSE = λt.λf.f`, with `AND`, `OR`, `NOT`, and `IF`.  Verify that the full truth tables reduce correctly.
- **Numerals:** $$\overline{0}$$ through $$\overline{4}$$, with `SUCC`, `ADD`, and `MUL`.  Verify that `ADD 2 2` and `MUL 2 2` both reduce to terms alpha-equivalent to $$\overline{4}$$.  Two terms are alpha-equivalent when they differ only in the names of bound variables; you will need a small alpha-equivalence checker, so write one.
- **Pairs:** `PAIR`, `FST`, `SND`.  Verify that `FST (PAIR a b)` reduces to `a` and `SND (PAIR a b)` to `b`.

Present the verification as a test table that maps each law to a passing reduction.

### C.3: Strategy and divergence

Implement applicative-order reduction (arguments first) behind the same interface, and demonstrate the term where the two strategies behave differently: $$(\lambda x.\, \lambda y.\, y)\ \Omega$$, where $$\Omega = (\lambda x.\, x\ x)(\lambda x.\, x\ x)$$.  Normal order discards $$\Omega$$ unevaluated and terminates.  Applicative order runs forever, and your step limit fires.  Write one sentence on what each strategy does and why, and one more connecting this to why a lazy language can pass an infinite structure to a function that ignores it.

**You write:** `lambda_calc.py` - `step_applicative`, and a `step` parameter on `normalize`; `test_functional.py` - the Ω test under both strategies.
**You run:** `python3 test_functional.py`

"The same interface" means the two step functions are interchangeable: each takes a term and returns the next term, or `None` in normal form.  `normalize` then takes the strategy as an argument, with normal order as the default, so every earlier call still works.

```python
# step_applicative: term -> term | None; one applicative-order step, or None in normal form
def step_applicative(term):
    ...

# normalize: as in C.1, but it advances with the step function it is given
def normalize(term, max_steps=1000, trace=False, step=step_normal):
    ...
```

Applicative order contracts a redex only after its argument can no longer step.  Otherwise its contract matches `step_normal`'s.

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

**You write (in `readme.md` under a `## D.1: Hand Reductions` heading):** the five reductions (a) through (e), one rule per line.  No code.

**(a)** $$\mathbf{K}\ \mathbf{I}\ a\ b$$: identify which standard function this is.  **(b)** $$\mathbf{S}\ \mathbf{K}\ \mathbf{K}\ 42$$: what well-known combinator is $$\mathbf{S}\ \mathbf{K}\ \mathbf{K}$$? **(c)** $$\mathbf{B}\ f\ (\mathbf{B}\ g\ h)\ x$$ and $$\mathbf{B}\ (\mathbf{B}\ f\ g)\ h\ x$$: confirm both produce $$f\ (g\ (h\ x))$$, which is associativity of composition.  **(d)** $$\mathbf{C}\ (\mathbf{B}\ f\ g)\ a\ b$$: what two-argument function is $$\mathbf{C}\ (\mathbf{B}\ f\ g)$$? **(e)** $$\mathbf{S}\ (\mathbf{K}\ \mathbf{S})\ \mathbf{K}\ f\ g\ x$$: reduce fully and identify the result as one of the named birds.

### D.2: The combinator reducer

**You write:** `birds.py` - `Prim`, `App`, `step_outermost`, `step_innermost`, and `reduce_term`; `config.json` - the strategy, step limit, and trace switch; `test_functional.py` - the five verification terms.
**You run:** `python3 test_functional.py`

> **Do this.**
> 1. Create `birds.py` with the two provided dataclasses below, then write the reducer from its specification.  Application is left-associative, so `S K K` is `App(App(Prim("S"), Prim("K")), Prim("K"))`.
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

# step_outermost: term -> term | None; contract the leftmost-outermost redex, or None
def step_outermost(term):
    ...

# step_innermost: term -> term | None; contract a redex only after its arguments
# can no longer step (the analog of applicative order), or None
def step_innermost(term):
    ...

# reduce_term: (term, dict) -> term; reduce under the strategy, limit, and trace in config
def reduce_term(term, config):
    ...
```

The specification for the reducer:

- A redex is a bird applied to at least as many arguments as its rule needs: 1 for `I` and `M`, 2 for `K` and `W`, 3 for `S`, `B`, and `C`.  Contracting it replaces those arguments with the rule's right-hand side; any extra arguments stay applied, in order.  An atom such as `Prim("a")` never fires.
- Each step function contracts exactly one redex and returns the new term, or returns `None` when no rule fires anywhere.
- With the example key names above, `config["strategy"]` is `"outermost"` or `"innermost"`, and `reduce_term` picks the matching step function.  Read `config.json` once with the `json` module and pass the resulting dictionary in.
- `reduce_term` returns the normal form.  With `trace` on, it prints each step.  If `max_steps` steps run without reaching normal form, it prints a diagnostic that starts with a location such as `birds.py: reduce_term:`, names the limit and the term, and returns the term.

> **You should see.** $$\mathbf{I}\ 42$$ reduces to `42` in one step and $$\mathbf{S}\ \mathbf{K}\ \mathbf{K}\ x$$ to `x` in two; $$\mathbf{M}\ \mathbf{M}$$ prints 1000 identical steps under `trace` and then a diagnostic such as a step-limit message naming the term, and the program keeps running.

### D.3: Point-free programming

Point-free style defines a function without naming its arguments: no `lambda`, no `def`, and no named parameters in the definition itself.  Using the birds as Python callables, implement each of the following in point-free style, state its combinator expression beside the Python, and demonstrate it on at least three inputs:

**You write:** `birds.py` - the seven birds as curried callables and the five point-free functions, plus a sixth of your own; `test_functional.py` - three inputs each.
**You run:** `python3 test_functional.py`

As callables, the birds take one argument at a time, so `K(1)(2)` is $$\mathbf{K}\ 1\ 2$$.  The birds themselves may use `lambda`; only the five definitions below must not.

```python
# birds.py, below the reducer: the birds as curried Python callables
import operator
from functools import partial

I = ...  # all seven birds: I, K, S, B, C, W, M, each following its rule above

double = partial(operator.mul, 2)      # helpers built without lambda or def
negate = operator.neg

double_then_negate = ...  # point-free, from the birds, negate, and double
```

Each bird is a curried callable: it takes one argument and returns a function waiting for the next, until it has as many as its rule needs.  To check one bird before you use it: `K(1)(2)` returns `1`.

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

**You write:** `bracket.py` - `LamVar`, `LamAbs`, `LamApp`, `translate`, and a node-count helper; `test_functional.py` - the three verifications through the reducer.
**You run:** `python3 test_functional.py`

`translate` returns a term built from `birds.py`'s own `Prim` and `App`, so the reducer can run it directly.  A free variable such as the `x` in $$\mathbf{K}\ x$$ becomes an atom, `Prim("x")`.

```python
# bracket.py
from dataclasses import dataclass
from birds import Prim, App, reduce_term

@dataclass(frozen=True)
class LamVar:
    name: str

@dataclass(frozen=True)
class LamAbs:
    param: str
    body: object

@dataclass(frozen=True)
class LamApp:
    rator: object
    rand: object

# translate: lambda term -> Prim | App
# The SKI equivalent of term: no LamAbs remains, and every LamVar becomes a Prim atom.
def translate(term):
    ...

# size: any term -> int; the number of nodes, counting every leaf and every
# application node, for the expansion-ratio comparison
def size(term):
    ...
```

To test identity, apply the translation to an atom and reduce: `reduce_term(App(translate(LamAbs("x", LamVar("x"))), Prim("a")), config)` should return `Prim(name='a')`.

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
- **Dataset:** the Project Gutenberg plain-text *Moby Dick* (approximately 21,000 lines), split into lines; each line is one "document."  Save it in the project folder and read it from there.  It is Project Gutenberg eBook #2701, at [gutenberg.org/ebooks/2701](https://www.gutenberg.org/ebooks/2701); download the "Plain Text UTF-8" file and save it as `moby_dick.txt`.  Gutenberg's license header and footer are part of that file, and including them is fine, as long as you say so in your readme.
- A machine with more than one core, and its CPU model and core count written down before you start; every number you report depends on them.

### E.1: The sequential baseline

`word_frequencies(line) -> dict[str, int]` is your map function; argue in writing that it is pure (no global reads, no shared mutation, and the same output for the same input every time).  `merge_counts(a, b) -> dict` is your reduce function; argue that it is pure *and associative*, and say why associativity matters for parallelism.  `top_n(counts, n)` returns the most frequent words.  Implement the three from the specification below, test each on two or three short hand-made lines in `test_functional.py`, then run `python3 pipeline.py` on the full corpus and record total words, unique words, the top 20, and the runtime.  Put the code that starts a `Pool` under `if __name__ == "__main__":`; on macOS and Windows, worker processes re-import your module, and without that guard each worker starts its own pool and the program never finishes.  The map function must be defined at module level so that Python can pickle it (serialize it to send to another process).

**You write:** `pipeline.py` - `word_frequencies`, `merge_counts`, `top_n`, and the sequential run under `if __name__ == "__main__":`; `test_functional.py` - two or three hand-made lines per function.
**You run:** `python3 test_functional.py`, then `python3 pipeline.py`.

```python
# pipeline.py
from functools import reduce
from multiprocessing import Pool

# word_frequencies: str -> dict[str, int]
def word_frequencies(line):
    ...

# merge_counts: (dict, dict) -> dict
def merge_counts(a, b):
    ...

# top_n: (dict, int) -> list
def top_n(counts, n):
    ...

if __name__ == "__main__":
    ...  # read the corpus into lines; run the sequential pipeline; then the Pool
         # version; assert the two results are equal before you time anything
```

| Function | Required behavior and edge cases |
|---|---|
| `word_frequencies(line)` | A dictionary mapping each word in `line` to how many times it appears.  Case does not matter, so `The` and `the` are the same word.  The word rule (what counts as a word, and what happens to punctuation) is yours; document it in the readme.  An empty line gives an empty dictionary.  It reads no globals and changes nothing outside itself. |
| `merge_counts(a, b)` | A NEW dictionary holding every word from either input, with the two counts added for a word in both.  `a` and `b` are unchanged afterward.  Merging with an empty dictionary gives back the same counts. |
| `top_n(counts, n)` | A list of the `n` most frequent `(word, count)` pairs, most frequent first.  Ties are broken alphabetically by word, so the output is the same on every run.  If there are fewer than `n` words, return them all. |
| the main block | Reads `moby_dick.txt` from the project folder as UTF-8 and splits it into lines.  The sequential result is the reduce of `merge_counts` over the `word_frequencies` of every line, seeded with an empty dictionary. |

### E.2: The parallel map

Replace `map(word_frequencies, lines)` with `multiprocessing.Pool.map` and assert that the parallel result equals the sequential result.  Then measure wall-clock time (`timeit`, five runs per configuration, report the mean) across worker counts 1, 2, 4, and the maximum available, and across chunk sizes (default, 10, 100, 1000) at maximum workers.  Tabulate time, speedup, and efficiency ($$= \text{speedup} / \text{workers}$$) for every configuration.  At what worker count does efficiency drop below 0.8, and why?  What effect does chunk size have, and why?

**You write:** `pipeline.py` - `parallel_counts` and `time_config`, and the timing table in the main block.
**You run:** `python3 pipeline.py`

A timing harness keeps every configuration measured the same way.  These two signatures are one way to shape it:

```python
import os
import timeit

# parallel_counts: (list[str], int, int | None) -> dict
# The same counts as the sequential pipeline, with the map step run on a Pool of
# `workers` processes, handing them `chunksize` lines at a time.
def parallel_counts(lines, workers, chunksize=None):
    ...

# time_config: (list[str], int, int | None, int) -> float
# Mean wall-clock seconds over `runs` separate runs of parallel_counts.
def time_config(lines, workers, chunksize=None, runs=5):
    ...

# In the main block, os.cpu_count() gives "the maximum available" worker count.
```

The pool must be closed when each run ends, so that one run's processes do not linger into the next.  The `timeit` module can repeat a zero-argument call and hand back each run's time.

> **You should see.** The equality assertion passes on the first try if `word_frequencies` is pure; if it fails, look for a global or a mutable default argument.  With one worker the parallel version is usually slower than the sequential baseline (process start-up and pickling are pure overhead there), and speedup grows, then flattens, as workers increase.

### E.3: Tree-reduce

The sequential `reduce(merge_counts, results, {})` performs $$O(n)$$ merges one after another.  Implement `tree_reduce(merge_fn, results)`: pair up adjacent elements, merge the pairs in parallel via `Pool.map`, and repeat until one element remains (carry an odd element forward).  Verify that it matches the sequential reduce, then measure and compare both on the full corpus.  In your writeup, draw the dependency graph of a tree-reduce over 8 elements: how many rounds are there, what is the maximum speedup regardless of core count, and how does the synchronization between rounds relate to the serial fraction below?

**You write:** `pipeline.py` - `tree_reduce`; `test_functional.py` - the empty, single-document, and odd-length cases.
**You run:** `python3 test_functional.py`, then `python3 pipeline.py`.

With `merge_counts`, `tree_reduce` should match the sequential reduce on the edge cases too: an empty list of results gives an empty dictionary, and a one-element list gives that element.  `Pool.map` passes exactly one argument to its function, and that function must be defined at module level, so plan a helper that merges one pair.

### E.4: Amdahl's Law analysis

If a fraction $$f$$ of the computation is serial, the maximum speedup with $$n$$ processors is

$$
S(n) = \frac{1}{f + \frac{1-f}{n}} \;\xrightarrow{\,n \to \infty\,}\; \frac{1}{f}
$$

**You write (in `readme.md` under a `## E.4: Amdahl's Law` heading):** the estimate of $$f$$, the theoretical bound, the comparison, and the 100-worker projection.  No new code.

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

**You write:** `logic.pl` - the `parent/2` facts and the `grandparent/2`, `sibling/2`, and `ancestor/2` rules; `logic_session.md` - each query and its answers.
**You run:** each query in the SWISH query pane, pressing `;` until it reports `false`.

> **Do this.**
> 1. Open SWISH, paste the starter facts below into the program pane, and add your rules from the specification after them.  Then run `?- grandparent(tom, Who).`, `?- parent(bob, Child).`, and `?- ancestor(tom, X).` in the query pane one at a time.
> 2. After each query, press `;` (or the Next button) until SWISH reports `false`, so you see every answer backtracking finds.
> 3. Copy each query and its answers into `logic_session.md` as you go.

```prolog
% logic.pl
parent(tom, bob).
parent(bob, ann).
% Add more parent/2 facts: enough for a grandparent, a sibling pair,
% and a three-generation chain.
```

The rules, as a specification:

- `grandparent(X, Z)` holds when `X` is a parent of someone who is a parent of `Z`.
- `sibling(X, Y)` holds when `X` and `Y` share a parent and are not the same person.
- `ancestor(X, Z)` holds when `X` is a parent of `Z`, or a parent of an ancestor of `Z`.  It is recursive, so give it a base clause and a recursive clause.

> **You should see.** `Who = ann` for the first query.  For a query with several answers, SWISH shows one binding at a time and waits for `;`.  If a query answers `false` when you expected a binding, the usual cause is a spelling mismatch between a fact and a rule, or a variable that starts with a lowercase letter (Prolog reads that as an atom, not a variable).

### F.2: A curated set of the Ninety-Nine Prolog Problems

Solve the following six problems from the classic [Ninety-Nine Prolog Problems](https://www.metalevel.at/prolog/99) list.  I chose them to span list recursion, structural recursion, arithmetic, logic, and constraint search:

**You write:** `logic.pl` - the clauses for all six problems; `logic_session.md` - one query per problem with its answers, and the P90 solution count.
**You run:** each query in SWISH; for P90, `?- aggregate_all(count, queens(Qs), N).` counts the solutions for you, once you have seen a few of them one at a time with `;`.

1.  **P01 `my_last(X, List)`**: the last element of a list (basic list recursion).
2.  **P05 `rev(List, Reversed)`**: reverse a list (accumulator recursion).
3.  **P07 `my_flatten(List, Flat)`**: flatten a nested list structure (recursion over term structure).
4.  **P31 `is_prime(N)`**: primality (arithmetic and the `\+`/negation-as-failure you should explain).
5.  **P46 `table(A, B, Expr)`**: print the truth table of a logical expression in `A` and `B` (logic connectives as relations).
6.  **P90 `queens(Qs)`**: place eight non-attacking queens (backtracking search, the payoff problem, where the declarative style shines).

For each problem, include the clause(s) in `logic.pl` and, in `logic_session.md`, the query you ran with its answer(s).  Where a problem admits multiple solutions (P90), show that Prolog enumerates them on backtracking and count how many exist.

### F.3: Run it backwards (the bidirectional relation)

Pick one relation you wrote (or `append/3`) and demonstrate it in at least two modes: for example, `append([1,2],[3],Xs)` (concatenate) *and* `append(Xs, Ys, [1,2,3])` (enumerate every split).  Explain in your writeup why a Python function *cannot* be run backwards like this, and what property of Prolog (unification over logic variables, not evaluation of expressions) makes it possible.  This is the single most important idea in the direction.

**You write:** `logic_session.md` - both modes with their answers; `readme.md` - the explanation, under a `## F.3: Running Backwards` heading.
**You run:** the relation in SWISH in at least two modes, such as `?- append([1,2],[3],Xs).` and `?- append(Xs, Ys, [1,2,3]).`

### F.4: Unification and backtracking vs. your interpreter's environments

Close with a short written comparison; it is required, and it ties the direction back to the pipeline.  Your interpreter's `Environment` maps names to *values* by assignment, in one direction only, and evaluation never "undoes" a binding.  Prolog's unification binds logic variables to *terms* in both directions, and backtracking un-binds them when a branch fails.  In one paragraph, contrast (a) binding-by-assignment vs. binding-by-unification, and (b) your evaluator's single forward pass vs. Prolog's search-with-backtracking.  If you took the type-checking direction of the Interpreter, connect this explicitly to the unification in your type inferencer; it is the *same* algorithm doing a different job.

**You write (in `readme.md` under a `## F.4: Unification vs. Environments` heading):** the one-paragraph comparison.  No code.

### Direction F depth checklist

- The warm-up knowledge base demonstrates a single-answer query, a multi-answer (backtracking) query, and a recursive rule, with the proof-search-vs-evaluation distinction stated.
- All six curated problems (P01, P05, P07, P31, P46, P90) are solved with correct clauses and shown queries/answers; P90's multiple solutions are enumerated and counted; negation-as-failure in P31 is explained.
- One relation is demonstrated running in at least two modes, with a written explanation of why unification (not evaluation) makes bidirectionality possible.
- The F.4 comparison contrasts assignment-binding vs. unification-binding and forward evaluation vs. backtracking search, connecting to the interpreter (and, if applicable, to Hindley-Milner (HM) type-inference unification).
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
- **[SWI-Prolog](https://www.swi-prolog.org/)**: documentation with worked examples, or test cases for library predicates.  It pairs naturally with Direction F's material, and documentation contributions are a common first way into an open-source project.

Something else you care about is negotiable; bring it to the scope-approval conversation.  Two things are not negotiable: the work must have functional-paradigm substance (a typo fix or formatting change does not qualify), and it must be small enough to finish.  One well-scoped, well-tested contribution beats an ambitious abandoned one.

### G.1: Issue selection and scope approval (first 3 days)

Find your target: a triaged open issue, a gap in the documentation, a missing test, or a small feature request with maintainer interest.  In `contribution.md`, record the issue or gap (with links), why it is *functional-paradigm* work (which core ideas from Parts 1 and 2 it exercises), and your one-sentence minimum viable scope (the smallest version of the change that would still be worth submitting).  Bring this to me for approval within 3 days of hand-out; the approval exists to protect you from scope that cannot land in the assignment window, and it is a five-minute conversation if those three things are written down.

**You write:** `contribution.md` - the issue or gap with links, its functional-paradigm substance, and the one-sentence minimum viable scope.
**You run:** nothing yet; bring `contribution.md` to the scope-approval conversation.

### G.2: Specification first

Before you write the fix, write the specification the way this course always does: a failing test that demonstrates the issue.  For documentation work, the specification is the worked example that does not yet exist and the checklist it must satisfy.  Commit it, or record it in its original form in `contribution.md`.  If the project's own test suite has conventions, follow them; reading a mature project's test conventions is part of the learning here.

**You write:** the failing test (or the documentation checklist), in the upstream project's own test layout, and a dated copy in `contribution.md`.
**You run:** the upstream project's test command, as its `CONTRIBUTING` file or README names it, and confirm that your new test fails.

### G.3: The contribution

Do the work on a fork, and follow the upstream project's `CONTRIBUTING` guidelines to the letter (branch naming, commit style, changelog entries, whatever they ask).  Your pull request must include tests and documentation for what it changes.  Keep the diff as small as the fix allows; maintainers review diffs, and a disciplined diff is a professional courtesy they notice.

**You write:** the fix, its tests, and its documentation, on a branch of your fork.
**You run:** the upstream test command again, and confirm that your test now passes and nothing else broke.

### G.4: The exchange

Submit the pull request and engage with what comes back: respond to review comments, make requested changes, and record the exchange in `contribution.md`.  A merge is ideal but not required.  Maintainer response times are outside your control, and the graded work is yours, not theirs.  If no maintainer responds within a week of submission, document the attempt and perform a written self-review against the project's own contributing standards: what would a maintainer flag, and why?

**You write:** `contribution.md` - the pull request link and a dated log of the exchange (or the self-review).
**You run:** whatever the reviewers' requested changes need, and the upstream test command after each change.

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
