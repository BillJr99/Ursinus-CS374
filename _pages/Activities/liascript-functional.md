<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374-Fall2026/gh-pages/_pages/Activities/liascript-functional.md or locally via https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374-Fall2026/gh-pages/_pages/Activities/liascript-functional.md

import: https://raw.githubusercontent.com/liascript/CodeRunner/master/README.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

# Functional Programming

Functional programming describes *what* you want the data to become and leaves the step-by-step work to the language.  Compare it to driving directions.  Imperative programming says "turn left on Main, go two blocks, turn right": a recipe for *how* to get somewhere.  Functional programming names the destination instead.  The comparison stops there, because the language does not pick its own route; it follows the rules for `map`, `filter`, and `reduce` that you learn today.  Every modern language (Python, JavaScript, Java, Rust) now carries these ideas, and learning them gives you a shorter and clearer way to say what a program does.

## Learning Goals

By the end of this activity, you will be able to:

- Tell a pure function from an impure one, and explain why purity gives you referential transparency, easy testing, and safe parallelism
- Apply `map`, `filter`, and `reduce` to transform and combine data without writing a loop
- Write higher-order functions that take other functions as arguments and return functions, including anonymous `lambda` expressions
- Use currying and partial application to build a specialized function from a general one
- Solve iterative problems recursively, with no mutable state and no assignment
- Read Scheme's single syntactic form and explain why a language whose programs are already trees needs almost no parser
- Write a macro: a function that takes a program as data, returns a different program, and hands it back to the evaluator

This is the third and last of the sessions that open the term inside one paradigm.  On Day 2 you met the paradigms and typed your first s-expressions.  On Day 3 you wrote real Scheme.  Today you bring the same ideas to Python (`lambda`, `map`, `filter`, `reduce`) and add the discipline of purity and immutability.  This toolkit matters twice.  It is a daily professional skill (data pipelines, modern Java, JavaScript, and Rust), and it is the bridge to the lambda calculus in November.  The deck ends where Scheme is strangest and most instructive: a program that is literally a list you can take apart and rewrite.

Arc: purity and why it pays -> the big three combinators -> higher-order thinking -> currying and partial application -> recursion without loops -> code as data

Everything in this deck is Python except Part V, which returns to the Scheme you have been writing since Day 2.  Nothing here assumes the parser, the interpreter, or the type checker you build later in the term.  Where those come up, they are previews.

> **Before You Begin:** This activity assumes you can:
> - Write and call Python functions, including functions that take other functions as arguments
> - Use Python lists and explain that lists are mutable (they can be changed in place)
> - Read a `for` loop and describe what it does step by step
>
> If any of these feel shaky, review them first.

---

## Directions and Group Roles

Work in your POGIL team with your rotated roles (Manager, Recorder, Presenter, Reflector).  Think each model and question through on your own first, then talk it over with your group.  The Recorder posts your answers to the Class Activity Questions discussion board.  The Presenter reports out wherever you disagreed or found another approach.

> **How today runs.**  Parts I through IV are the core.  Part V (code as data) is the goal we want to reach together, so watch the clock.  If the period runs short, read Part IV's recursive rewrites of `map`, `filter`, and `reduce` at home; Exercise 3 has you write them anyway.  Everything after *Check Your Understanding* is homework.  The Scheme extension at the end is for whoever takes the Scheme direction on the Functional assignment.

---

## Key Concepts

This table defines the terms the activity uses, in plain English.  Come back to it whenever a term starts to feel slippery.

| Term | Plain-English meaning | Why it matters |
|------|-----------------------|----------------|
| **Pure function** | The output depends only on the inputs, and nothing outside the function changes | You can test, cache, substitute, and parallelize a pure function without fear |
| **Side effect** | Anything a function does besides return a value: changing data in place, printing, reading a global | Side effects are exactly what purity forbids; spotting them is a skill |
| **Immutability** | Never change existing data; build new data instead | Removes a whole class of "who changed my list?" bugs |
| **Referential transparency** | You can replace a call with its result anywhere without changing behavior | The formal reward for purity, and the license for safe refactoring |
| **`map`** | Transform every element of a list with a function | Replaces the "loop that builds a new list" pattern |
| **`filter`** | Keep only the elements that pass a test | Replaces the "loop with an `if` inside" pattern |
| **`reduce` (fold)** | Collapse a whole list into one value with a two-argument function | Replaces the "loop with an accumulator variable" pattern |
| **Higher-order function** | A function that takes a function as an argument or returns one | The mechanism behind combinators, decorators, and callbacks |
| **Lambda** | A small anonymous function written inline | Lets you hand behavior to `map`, `filter`, and `reduce` without naming it |
| **Currying / partial application** | Supply a function's arguments one at a time to build a specialized function from a general one | Turns general tools into custom ones; central to Haskell and to the lambda calculus ahead |

---

# Part I: Purity

## 1.  Functions Like Mathematics Meant

A pure function's output depends only on its inputs, and it changes nothing outside itself.  It does not change its arguments, read or write globals, print, or use randomness.  Purity buys three concrete powers:

1.  Substitution: you can replace a call with its result anywhere (this is referential transparency)
2.  Testability: no setup and no teardown, only input -> expected output
3.  Parallel safety: no shared state means no interference

Immutability is purity's partner.  Functional style does not modify a list; it produces a new one.  Run the cell below and watch what happens to `original`.

```python
# Spot the impure function, run this and observe the difference
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
print(f"data after two calls to impure_double: {data}")   # [4, 8, 12], not [4, 4, 4]!
```
@LIA.eval(`["main.py"]`, `none`, `python3 main.py`)

**Critical Thinking Questions (CTQs)**

> **CTQ 1.1** `pure_double` and `impure_double` return the same value for `[1, 2, 3]`, yet they differ in a basic way.  What is the difference, and why does it matter when a function is called more than once?

> **CTQ 1.2** The rule "calling a pure function twice with the same input always gives the same output" is called referential transparency.  Which functions in the code above have this property?  Which do not?

> **CTQ 1.3** Could `pure_double` safely run on two halves of the list in parallel and merge the results?  Could `impure_double`?  Explain.

---

A pure function behaves like a calculator: press `2 + 3` and you get `5` every time, no matter how many times you press it or what else is on your desk.  The comparison stops at memory, because a real calculator has a memory key and a pure function has none.  Model 1 gives you six functions.  Decide which ones behave like that calculator and which ones secretly remember, or change, the world around them.  Use the opening example above to guide your classification.

## Model 1: The Purity Audit

```python
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
@LIA.eval(`["main.py"]`, `none`, `python3 main.py`)

### Reading the Code

- The audit asks one question per function: given the same arguments, does it always return the same value, and does it change anything outside itself?  Both halves must hold for purity.
- `f4` reads a global without writing one.  It is still impure, because "same input, same output" fails the moment somebody else changes that global.  Purity is a property of the function *and* everything it can observe.
- The mutation surprise at the top is the practical stake.  `impure_double` looked like a transformation and was in fact an edit.  Calling it twice gives different answers from the same argument, which is exactly what referential transparency forbids.

### Try It Yourself

Write the test that catches the impurity, then make the function pure.

```python
LOG_LINES = []

def f_impure(xs):
    LOG_LINES.append(f"called with {len(xs)} items")
    return [x * 2 for x in xs]

def f_reads_global(x):
    return x + len(LOG_LINES)

print("=== The bug purity prevents ===")
data = [1, 2, 3]
print(f"  f_reads_global(10) = {f_reads_global(10)}")
f_impure(data)                        # someone else's call, elsewhere
print(f"  f_reads_global(10) = {f_reads_global(10)}   <- same input, new answer")

# TODO 1: write an assertion that PASSES right now and FAILS after another
#         call to f_impure. That assertion is the test CTQ 1.5 asks for,
#         and the fact that you can write it is the definition of the bug.

# TODO 2: make f_reads_global pure by turning the hidden dependency into a
#         parameter. What is its new signature, and who now has to supply
#         the extra argument?

# TODO 3: f_impure both logs AND transforms. Split it into a pure transform
#         and a separate logging step. Which half can you now test without
#         any setup at all?

print("\n=== After your refactor, this should hold no matter what ===")
print("  same input -> same output, every time, forever")
```
@LIA.eval(`["main.py"]`, `none`, `python3 main.py`)

Expected output: `f_reads_global(10)` returns 10 and then 11, from identical arguments.  That one changed digit is the whole case for purity, made in one line.

> **CTQ 1.4** Classify each function as pure or impure.  For each impure one, name the exact disqualifying feature.

> **CTQ 1.5** `f4` reads but never writes a global.  What referential transparency property does it still forfeit?  Construct a test that would *pass* today but *fail* after appending to `LOG_LINES`.

---

# Part II: The Big Three Combinators

The next two models cover the three combinators that replace nearly every explicit loop you have written.  A combinator is a function that takes a function and a list and builds a result from them.  Each of the three answers a question you already ask about data: "what does each element look like after a change?", "which elements do I want to keep?", and "what single summary value do these elements produce?"  You have been answering those questions with `for` loops.  Now you will answer them with one function call each.

> **Watch out!**  Python's `map` and `filter` do not stop you from passing in an impure function, one that prints, changes a global, or reads a file.  The combinators themselves are pure, but they run whatever function you hand them.  Make sure the lambda or function you pass in has no side effects.  Otherwise you lose the guarantees that make functional style worth using.

## 2.  Map, Filter, Reduce

$$\text{map}(f, [x_1, \dots, x_n]) = [f(x_1), \dots, f(x_n)]$$

$$\text{filter}(p, [x_1, \dots, x_n]) = [x_i \mid p(x_i) = \text{True}]$$

$$\text{reduce}(\oplus, [x_1, \dots, x_n], z) = ((z \oplus x_1) \oplus x_2) \oplus \cdots \oplus x_n$$

Each formula replaces a loop pattern you have written a hundred times.  `map` *transforms* every element, `filter` *selects* elements, and `reduce` *collapses* a list to one value.  In the `reduce` formula, $z$ is the starting value (the seed) and $\oplus$ is the two-argument function that combines the running result with the next element.

```python
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
@LIA.eval(`["main.py"]`, `none`, `python3 main.py`)

> **CTQ 2.1** Rewrite the `map` call as an explicit `for` loop.  What bookkeeping did `map` absorb?  Do the same for `filter`.

> **CTQ 2.2** `reduce` with `lambda a, b: a - b` over `[10, 3, 2]` and seed 0: compute it by hand using the left-fold formula `((0 - 10) - 3) - 2`.  What is the result?  Now try seed 10 with `[3, 2]`.  What does "left fold" mean?

> **CTQ 2.3** The pipeline composes `map`, `filter`, and `reduce` in a *single expression* with no intermediate names.  Name one benefit and one cost for a reader.

---

Python gives you two roads to the same result: the `map`/`filter` combinators you just saw, and *list comprehensions*, a syntax borrowed from mathematical set-builder notation.  Model 2 puts them side by side so you can see that they produce identical results while looking quite different.  You will meet both in real Python code, and comparing them sharpens your sense of what "transforming a collection" means.

> **Watch out!**  Immutability does not mean "constant."  In Python, `x = 5` creates a variable that you could reassign at any time.  Immutability in functional programming means that once you build a data structure you never modify it; you build a new one instead.  Python's `tuple` is immutable; a `list` is not.  When you call `pure_double` above, `original` stays unchanged because the function was *written* to build a new list, not because Python enforces it.  Nothing stops you from writing an impure version.  Discipline and code review do.

## Model 2: Comprehensions vs. Combinators

Python offers *list comprehensions* as a second syntax for map plus filter:

```python
scores = [88, 92, 54, 71, 67, 95, 49, 83]

# Using map + filter
via_combinators = list(filter(lambda s: s >= 70, map(lambda s: min(s + 5, 100), scores)))

# Using list comprehension
via_comprehension = [min(s + 5, 100) for s in scores if min(s + 5, 100) >= 70]

# Are they the same?
print(f"combinators:   {via_combinators}")
print(f"comprehension: {via_comprehension}")
print(f"equal: {via_combinators == via_comprehension}")

# Generator expression (lazy, no list built until needed):
gen = (min(s + 5, 100) for s in scores if min(s + 5, 100) >= 70)
print(f"generator sum: {sum(gen)}")
```
@LIA.eval(`["main.py"]`, `none`, `python3 main.py`)

> **CTQ 2.4** The comprehension evaluates `min(s + 5, 100)` *twice* for each element.  How would you fix this using a nested comprehension or a helper function?

> **CTQ 2.5** Generators are *lazy*: they produce elements one at a time on demand.  What advantage does this have for processing a file with 10 million lines?

Here is the word for what a comprehension does.  A loop is *imperative*: it tells the machine *how* to build the answer, one `append` at a time, and the answer exists only after the last step runs.  A comprehension is *declarative*: it describes *what* collection you want and leaves the construction to the language.  That is not a metaphor.  It is borrowed notation, and mathematicians have written the same thing for a century:

- set-builder: $\{\, f(x) \mid x \in S,\ p(x) \,\}$
- Python: `[f(x) for x in S if p(x)]`
- SQL: `SELECT f(x) FROM S WHERE p(x)`

Three notations, one idea: name the source, name the filter, name the transformation, and say nothing about the order of operations.  You met this in week 0 as the fourth paradigm.  Here it is with a syntax attached.

And here is the word for choosing it.  Python programmers call the comprehension the *Pythonic* version.  The term needs a careful definition because people so often use it to mean "shorter."  It does not mean that.  *Pythonic* means idiomatic for this language: the construction a fluent reader expects, the one the language was shaped to make easy.  A comprehension is Pythonic because Python grew comprehensions on purpose.  The same code translated word for word into C would be neither idiomatic nor readable.  Every language has its own version of this, and part of learning a language is learning which constructions its community reaches for first.

> **CTQ 2.6** "Pythonic" and "short" clearly are not the same thing, since a deeply nested comprehension is short and nobody calls it Pythonic.  Propose a test a reader could apply to decide whether a given comprehension has crossed the line, and try it on the generator expression above.

---

Before you move on to higher-order functions, run one pipeline entirely by hand.  Once you can produce every intermediate list on paper, `map`, `filter`, and `reduce` stop being incantations and become bookkeeping you happen not to write yourself.

## Model 3: Tracing a Map-Filter-Reduce Pipeline by Hand

**Worked example.**  Trace the scores pipeline from Section 2, one stage at a time:

```
scores    [88, 92, 54, 71, 67, 95, 49, 83]
   |  map: s -> min(s + 5, 100)          (curve, capped at 100)
curved    [93, 97, 59, 76, 72, 100, 54, 88]
   |  filter: s >= 70                    (keep passing scores)
passing   [93, 97, 76, 72, 100, 88]
   |  reduce: (acc, s) -> acc + s, seed 0
total     526                            mean = 526 / 6 = 87.7
```

Here is the same computation element by element.  Notice that `map` *transforms* the two failing scores but `filter` *discards* them, so they never reach `reduce`:

| Element | After `map` (`min(s+5, 100)`) | Passes `>= 70`? | Running total in `reduce` |
|---------|-------------------------------|-----------------|---------------------------|
| 88 | 93 | yes | 0 + 93 = 93 |
| 92 | 97 | yes | 93 + 97 = 190 |
| 54 | 59 | no | 190 (unchanged) |
| 71 | 76 | yes | 190 + 76 = 266 |
| 67 | 72 | yes | 266 + 72 = 338 |
| 95 | 100 | yes | 338 + 100 = 438 |
| 49 | 54 | no | 438 (unchanged) |
| 83 | 88 | yes | 438 + 88 = 526 |

Run the cell to see the machine agree with your paper trace, one fold step at a time:

```python
from functools import reduce

scores = [88, 92, 54, 71, 67, 95, 49, 83]

curved = list(map(lambda s: min(s + 5, 100), scores))
print(f"after map:    {curved}")

passing = list(filter(lambda s: s >= 70, curved))
print(f"after filter: {passing}")

def traced_add(acc, s):
    print(f"    fold step: acc={acc:3} + {s:3} -> {acc + s}")
    return acc + s

print("reduce, step by step:")
total = reduce(traced_add, passing, 0)
print(f"total = {total}, mean = {total / len(passing):.1f}")
```
@LIA.eval(`["main.py"]`, `none`, `python3 main.py`)

In the pipeline trace, the score 54 becomes 59 after the map stage and then vanishes.  Which statement is accurate?

[( )] `map` removed it because it was below 70
[(X)] `map` transformed it (54 -> 59) and `filter` discarded it because 59 < 70
[( )] `reduce` skipped it while folding
[( )] It was removed before the map stage ran

### Reading the Code

- Each stage is a separate line that produces a separate list, purely so the trace can print the intermediate results.  The one-expression version composes them without ever naming the intermediates.
- `reduce` is the only stage that collapses.  `map` preserves length, `filter` can only shorten, and `reduce` returns one value regardless.  Knowing which stage can change the length is most of debugging a pipeline.
- Nothing is mutated anywhere.  The "running total" column is the accumulator argument travelling from one call to the next.  That argument replaces the mutable variable an imperative loop would have needed.

### Try It Yourself

Rebuild the big three from scratch, so you can see there is nothing hidden in them.

```python
from functools import reduce

def my_map(f, xs):
    return [f(x) for x in xs]

def my_filter(p, xs):
    return [x for x in xs if p(x)]

def my_reduce(f, xs, init):
    acc = init
    for x in xs:
        acc = f(acc, x)
    return acc

scores = [54, 71, 88, 63, 95, 70]

print("=== yours against the library's ===")
print(f"  my_map    {my_map(lambda s: s + 5, scores)}")
print(f"  map       {list(map(lambda s: s + 5, scores))}")
print(f"  my_filter {my_filter(lambda s: s >= 70, scores)}")
print(f"  filter    {list(filter(lambda s: s >= 70, scores))}")
print(f"  my_reduce {my_reduce(lambda a, b: a + b, scores, 0)}")
print(f"  reduce    {reduce(lambda a, b: a + b, scores, 0)}")

# TODO 1: my_reduce uses a mutable accumulator and a for loop. Rewrite it
#         RECURSIVELY with no assignment at all. Both versions are pure
#         from the outside, so does the mutation inside matter? Argue it.

# TODO 2: define my_map using only my_reduce. Then define my_filter using
#         only my_reduce. What does that tell you about which of the three
#         is the fundamental one?

# TODO 3: my_reduce takes an explicit init. What goes wrong if you drop it
#         and start from xs[0]? Try it on an empty list and say what a
#         well-designed library should do.
```
@LIA.eval(`["main.py"]`, `none`, `python3 main.py`)

Expected output: each pair of lines identical.  TODO 2 is the interesting one: `reduce` is the general fold, and the other two are special cases of it.

**Critical Thinking Questions (CTQs)**

> **CTQ 3.1** Recompute the running-total column yourself to confirm 526.  Which two original scores never reach `reduce`, and which stage eliminated each one?

> **CTQ 3.2** The stage diagram builds two whole intermediate lists (`curved`, `passing`) because the code calls `list(...)`.  In the one-expression pipeline from Section 2 (no `list` calls), do those intermediate lists ever exist in memory?  Connect your answer to the laziness you observed in CTQ 2.5.

> **CTQ 3.3** The running-total column is exactly the accumulator variable from an imperative loop, yet nothing here is mutated.  Where does the "updated" accumulator live on each fold step instead?  And is `reduce` with `traced_add` still pure?  (Careful: `traced_add` prints.)

---

# Part III: Higher-Order Functions

You have already passed functions as arguments: every call to `map(lambda x: x*2, data)` hands a function to another function.  Part III adds the other direction: a function can also *return* a new function.  Think of a factory that builds machines instead of widgets.  `make_adder(5)` is that factory: call it once and you get back a custom addition function, ready to use anywhere.  The comparison stops there, because the returned function is not a physical thing.  It is a closure: a function bundled with the values it could see when it was created.

## 3.  Functions That Make Functions

A higher-order function takes functions as arguments *or* returns functions.  Today you also *return* them, which creates parameterized behavior without classes.

```python
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
@LIA.eval(`["main.py"]`, `none`, `python3 main.py`)

`compose = lambda f, g: lambda x: f(g(x))` is a higher-order function because it:

[( )] Uses lambda syntax twice
[( )] Avoids mutation
[(X)] Both consumes functions as arguments and produces a function as its result
[( )] Runs in logarithmic time

---

A composed pipeline like `clean` reads as one gesture, but the machine runs it one function at a time.  Tracing a composition call by call, writing down each intermediate value, is the fastest way to see that data flows left to right through `pipeline` and right to left through `compose`.

## Model 4: Composition, Traced One Call at a Time

**Worked example.**  Trace `clean("  Hello World  ")` where `clean = pipeline(str.strip, str.lower, lambda s: s.replace(' ', '_'))`.  Because `pipeline` folds with `lambda v, f: f(v)`, the string threads through the functions in order:

| Step | Function applied | Input value | Output value |
|------|------------------|-------------|--------------|
| start | - | `"  Hello World  "` | - |
| 1 | `str.strip` | `"  Hello World  "` | `"Hello World"` |
| 2 | `str.lower` | `"Hello World"` | `"hello world"` |
| 3 | `s.replace(' ', '_')` | `"hello world"` | `"hello_world"` |

Here is the same trace as a flow diagram, next to `compose`, which runs right to left:

```bash
pipeline:  x --> [strip] --> [lower] --> [replace ' '->'_'] --> "hello_world"
compose:   compose(f, g)(x) = f(g(x))    (g runs FIRST, then f)
```

The cell below wraps each stage so it narrates itself.  It then swaps the first and last stages to show that composition order is part of the meaning:

```python
from functools import reduce

def pipeline(*fns):
    return lambda x: reduce(lambda v, f: f(v), fns, x)

def traced(name, f):
    """Wrap f so each application narrates itself."""
    def wrapper(x):
        result = f(x)
        print(f"  {name:22} {x!r:22} -> {result!r}")
        return result
    return wrapper

clean = pipeline(
    traced("str.strip", str.strip),
    traced("str.lower", str.lower),
    traced("replace ' ' -> '_'", lambda s: s.replace(' ', '_')),
)

print("clean('  Hello World  '):")
print(f"result: {clean('  Hello World  ')!r}")

# Order matters: replace first, and the edge spaces get underscored
messy = pipeline(
    traced("replace ' ' -> '_'", lambda s: s.replace(' ', '_')),
    traced("str.strip", str.strip),
    traced("str.lower", str.lower),
)
print("\nsame three functions, different order:")
print(f"result: {messy('  Hello World  ')!r}")
```
@LIA.eval(`["main.py"]`, `none`, `python3 main.py`)

Notice that `traced` is itself a higher-order function.  It consumes a function and returns a new one with the same behavior plus narration, the same shape as `twice` and `compose`.

`compose(f, g)` returns `lambda x: f(g(x))`.  Evaluating `compose(str.lower, str.strip)("  ABC  ")` therefore:

[( )] Applies `lower` first, then `strip`
[(X)] Applies `strip` first (it is innermost), then `lower`
[( )] Applies both simultaneously
[( )] Raises an error because strings are immutable

**Critical Thinking Questions (CTQs)**

> **CTQ 4.1** Each stage's output becomes the next stage's input.  What requirement connects the *return type* of one stage to the *parameter type* of the next?  The swapped `messy` pipeline still ran without error; did it satisfy your requirement, and is "runs without error" the same as "correct"?

> **CTQ 4.2** Unroll `pipeline(f, g, h)(x)` by hand using the left-fold formula from CTQ 2.2 to show it computes `h(g(f(x)))`.  Then unroll `compose(f, g)(x)`.  Which order do you find easier to read, and why might data-pipeline libraries prefer left-to-right?

> **CTQ 4.3** `pipeline` is implemented with `reduce`, but it folds over a list of *functions* rather than numbers.  In the trace table, what plays the role of the accumulator, and what is its value after step 2?

---

If higher-order functions are factories, then currying and partial application are ways to customize the factory.  Take a general `power(base, exp)` function.  Partial application lets you say "I always want `exp=2`; give me a `square` function."  Currying goes further.  It restructures any multi-argument function so you supply arguments one at a time, producing a chain of single-argument functions.  Functional languages like Haskell use this style everywhere, and knowing it will make the lambda calculus later in the term feel natural.

## 4.  Partial Application and Currying

Partial application fixes some arguments of a function to produce a simpler one.

Currying transforms a function `f(a, b)` into `f(a)(b)`: a chain of single-argument functions.

```python
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
@LIA.eval(`["main.py"]`, `none`, `python3 main.py`)

> **CTQ 4.4** `map_with(lambda x: x * 2)` returns a function.  How is this different from `map(lambda x: x * 2, data)`?  When is the list transformer version more useful?

> **CTQ 4.5** Haskell functions are automatically curried: `f x y` is always `(f x) y`.  What advantage does automatic currying give you for composing functions?

---

# Part IV: Recursion Without Loops

In Python you have used `for` loops to walk through lists.  A `for` loop needs mutable state: a loop variable that changes on every pass.  Pure functional programming avoids mutable state entirely, so loops are off the table.  The replacement is recursion: a function solves a big problem by calling itself on a smaller piece of that problem.  Section 5 shows that `map`, `filter`, and `reduce` can themselves be written as recursive functions, which makes their structure visible and precise.

> **Watch out!**  When students first hear "no loops allowed," a common instinct is to reach for a `while True` loop with a counter.  That is still a loop.  Pure functional recursion means the function calls itself with a *smaller* argument: no loop variable, no `i += 1`, and no change to any list.  If you find yourself writing an assignment statement inside a recursive function, pause and reconsider.

## 5.  Thinking Recursively

In pure functional style there are no loops, only recursion.  Every loop corresponds to a recursive function:

```python
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

# Recursive sum, no loop, no accumulator variable
def rsum(lst):
    if not lst: return 0
    return lst[0] + rsum(lst[1:])

print(f"rsum({nums}) = {rsum(nums)}")
```
@LIA.eval(`["main.py"]`, `none`, `python3 main.py`)

> **CTQ 5.1** Each recursive function has a base case and a recursive case.  Identify them for `my_map`.  What guarantees the recursion terminates?

> **CTQ 5.2** `my_reduce(f, lst, init)` uses `init` as an accumulator.  Trace `my_reduce(lambda a, b: a - b, [3, 2, 1], 10)` step by step.  What is the result?

> **CTQ 5.3** Python has a default recursion limit of 1000.  Haskell compiles tail-recursive functions to loops.  What is a "tail call," and why can't Python's `rsum` be optimized this way?

---

Section 6 pushes recursion in two new directions: *mutual* recursion (two functions that call each other) and *structural* recursion (recursing along the shape of nested data instead of a numeric counter).  It also includes a fully functional merge sort with no mutation anywhere.  First, study the worked example below.  It shows how to turn an imperative loop into a functional composition, one step at a time.

**Worked Example: Imperative -> Functional**

Suppose you have this imperative code, which sums the squares of all even numbers in a list:

```python
# Imperative version. 5 statements, 2 mutation points
result = 0
for x in nums:
    if x % 2 == 0:
        result += x ** 2
```

Here is how to turn it into a functional composition, step by step.

Step 1.  Name the three loop concerns separately:
- *Filter*: keep only even numbers -> `x % 2 == 0`
- *Transform*: square each kept number -> `x ** 2`
- *Aggregate*: sum the results -> `+`

Step 2.  Write each concern as a lambda:

```python
is_even  = lambda x: x % 2 == 0
square   = lambda x: x ** 2
add      = lambda a, b: a + b
```

Step 3.  Assemble with `filter`, `map`, and `reduce`:

```python
from functools import reduce
result = reduce(add, map(square, filter(is_even, nums)), 0)
```

Step 4.  Inline the lambdas for a one-liner (optional):

```python
result = reduce(lambda a, b: a + b,
                map(lambda x: x**2,
                    filter(lambda x: x % 2 == 0, nums)), 0)
```

The result is identical to the loop.  The difference: the functional version has no mutation (`result` is never reassigned) and no loop variable, and each concern is a named, testable piece.

## 6.  Mutual Recursion and Structural Recursion

```python
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
@LIA.eval(`["main.py"]`, `none`, `python3 main.py`)

> **CTQ 6.1** `tree_sum` recurses on the *structure* of the data, not a loop counter.  What property of the tree guarantees this terminates?

> **CTQ 6.2** `mergesort` produces new lists at each step: it never mutates the input.  What is the memory cost compared to in-place quicksort?  Is purity free?

---

## Model 5: Recursion in a Single Expression

Everything above was Python written in a functional *style*.  Here is the same recursion with nowhere left to hide: no `def`, no statement, and no name except the one the lambda needs to call itself.

```python
# Define sumlist using a lambda and recursion.  This is the Scheme
# definition from the last session, transliterated one symbol at a time:
#
#   (define sumlist (lambda (L) (if (null? (cdr L)) (car L) (+ (car L) (sumlist (cdr L))))))
#
# L[0] is (car L); L[1:] is (cdr L); len(L) == 1 is (null? (cdr L)).

sumlist = lambda L: L[0] if len(L) == 1 else L[0] + sumlist(L[1:])

print(f"  sumlist([1, 2, 3])        = {sumlist([1, 2, 3])}")
print(f"  sumlist([4])              = {sumlist([4])}")
print(f"  sumlist(list(range(101))) = {sumlist(list(range(101)))}")

# The same shape, with the operator lifted out into a parameter.  This is
# oplist from the Scheme session, and it is also reduce with the argument
# order rearranged.
oplist = lambda op, L: L[0] if len(L) == 1 else op(L[0], oplist(op, L[1:]))

import operator
print()
print(f"  oplist(add, [2, 4, 6])    = {oplist(operator.add, [2, 4, 6])}")
print(f"  oplist(mul, [2, 4, 6])    = {oplist(operator.mul, [2, 4, 6])}")
print(f"  oplist(max, [2, 9, 6])    = {oplist(max, [2, 9, 6])}")
```
@LIA.eval(`["main.py"]`, `none`, `python3 main.py`)

### Reading the Code

- The conditional expression `a if test else b` is Python's `if` *as an expression*, which is the only kind Scheme has.  That is why the transliteration works symbol for symbol.
- `sumlist` refers to itself by name inside its own body.  This works because the name is bound before the lambda is ever called.  It is also the reason the lambda calculus needs the Y combinator: strip the name away and recursion becomes hard.
- `oplist` is `sumlist` with the operator promoted to a parameter.  Once you see that, `reduce` stops being a library function you memorize and becomes a shape you recognize.

### Critical Thinking Questions

1.  What does this code do?  How does it do it?
2.  What are the advantages of programming this way?

---

## Model 6: Purity Buys Parallelism

Part I claimed that pure functions parallelize safely because there is no shared state to protect.  Here is that claim as code you can time.  Nothing below takes a lock, and nothing needs one.

```python
from concurrent.futures import ThreadPoolExecutor, as_completed
from functools import reduce
import operator, time

# A pure function: it does not depend on or modify any shared state.
def factorial(n):
    return reduce(operator.mul, range(1, n + 1), 1)

# Another pure function, built from the first.
def sum_of_factorials(numbers):
    return sum(map(factorial, numbers))

def run(numbers, workers):
    start = time.perf_counter()
    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = {executor.submit(factorial, n): n for n in numbers}
        results = {}
        for future in as_completed(futures):
            n = futures[future]
            try:
                results[n] = future.result()
            except Exception as exc:
                print(f"  factorial of {n} raised {exc}")
    return time.perf_counter() - start, results

numbers = [5, 7, 10, 12, 15]
for workers in (1, 2, 4, 8):
    elapsed, results = run(numbers, workers)
    print(f"  {workers} worker(s): {elapsed * 1000:7.2f} ms")

_, results = run(numbers, 4)
print()
print(f"  factorials:        { {n: results[n] for n in sorted(results)} }")
print(f"  sum of factorials: {sum_of_factorials(numbers)}")
print()
print("  No locks, no ordering constraints, no shared mutable state.  The only")
print("  reason this is safe is that factorial is pure.  Make it write to a")
print("  global and every one of those guarantees evaporates.")
```
@LIA.eval(`["main.py"]`, `none`, `python3 main.py`)

### Reading the Code

- `as_completed` hands back results in whatever order they finish.  That is fine here, because each call is independent, so order carries no meaning.  That is a property of purity, not of the executor.
- The results come back into a dict keyed by input, so the answer is reproducible even though the schedule is not.  A pure function plus a deterministic key gives a deterministic output.
- Look at the timings carefully before you conclude anything about speed.  These factorials are small, and Python threads share one interpreter lock.  The *safety* is real; the *speedup* here mostly is not.  Question 3 is about that gap.

### Critical Thinking Questions

3.  Time the following program for various numbers of threads and values for `numbers`.  What do you notice?  Then say which part of your answer is about purity and which part is about Python.

---

# Part V: Code as Data

## 7.  Everything Is (operator operands...)

Scheme has one syntactic form: the parenthesized prefix application `(f a b c)`.  Arithmetic is not special: `(+ 2 3)` is 5, and `(* (+ 2 3) 4)` is 20.  Definitions, conditionals, and functions are *special forms* wearing the same parentheses:

```scheme
(define pi 3.14159)
(define (square x) (* x x))
(if (> x 0) "positive" "not positive")
(lambda (x) (* x x))
```

Notice what vanished.  There is no precedence (prefix notation needs none, because the nesting makes the tree explicit), no associativity rules, and no statement-versus-expression divide (everything is an expression with a value).  The parentheses *are* the tree, written by hand.

Bank that.  Starting next week this course spends most of a month on the machinery that recovers exactly that tree from flat infix text: grammars, then derivations and ambiguity, then a precedence ladder, then a recursive descent parser, then the abstract syntax tree (AST) that the parser finally hands to an interpreter.  Every piece of it exists because `2 + 3 * 4` does not say what it means.  When you meet the ladder grammar in September, come back to this page.

---

In Python, a parser has to work hard to turn the flat text `2 + 3 * 4` into a tree that captures precedence.  In Scheme, the programmer *writes* the tree.  Model 7 asks you to feel the difference by doing the translation yourself, before you write a line of the parser it makes unnecessary.

## Model 7: Trees Without a Parser

### Critical Thinking Questions

4.  Translate `2 + 3 * 4` and `(2 + 3) * 4` into Scheme.  Which required parentheses beyond the operators' own, and why does the question almost not make sense?
5.  Draw, by hand, the tree that `2 + 3 * 4` *means*: the multiplication has to happen first, so it hangs below the addition.  Now write the Scheme expression beside your drawing and state the relationship in one sentence.  Keep the page; in October you will build a parser whose entire output is that drawing.
6.  A Scheme "lexer" needs roughly four token types.  Name them.  Then predict what a Scheme "parser" would have to do, given that the nesting is already explicit in the text.
7.  What did Scheme's designers *pay* for this uniformity, in the four criteria from *Programming Paradigms, Evaluating Languages, and an Introduction to Functional Programming*?  (Ask anyone who has counted parentheses.)

---

## 8.  The Big Idea: Homoiconicity

`'(+ 1 2)` is a list whose first element is the symbol `+`.  The program is a data structure that the language itself can manipulate, and `(eval '(+ 1 2))` runs it.  This property is called **homoiconicity**.  It is why Lisp dialects have macros: functions that receive *code as lists*, transform it, and hand the result back to the evaluator.  The abstract syntax tree that most languages make you build out of classes is, in Scheme, the list you typed.

## Model 8: Homoiconicity, Executed

The claim above is easy to nod at and hard to feel.  Here it is as code you can run.  A Scheme program is a list, so we represent it as a Python list and evaluate it.  Then we write a macro: an ordinary function that takes a program as data, returns a different program as data, and hands it back to the evaluator.

```python
# A Scheme program IS a list. In Python, we write it as a Python list.
#   (+ 1 2)            ->  ["+", 1, 2]
#   (if (> x 0) 1 -1)  ->  ["if", [">", "x", 0], 1, -1]

import operator

BUILTINS = {
    "+": operator.add, "-": operator.sub, "*": operator.mul,
    ">": operator.gt,  "<": operator.lt,  "=": operator.eq,
}

def sch_eval(expr, env):
    if isinstance(expr, str):                 # a symbol: look it up
        return env[expr]
    if not isinstance(expr, list):            # a number: itself
        return expr

    head, *rest = expr
    if head == "quote":                       # (quote X) -> X, unevaluated
        return rest[0]
    if head == "if":
        test, conseq, alt = rest
        return sch_eval(conseq if sch_eval(test, env) else alt, env)
    if head == "let":
        (name, value), body = rest[0], rest[1]
        return sch_eval(body, {**env, name: sch_eval(value, env)})

    fn = sch_eval(head, env)
    return fn(*[sch_eval(a, env) for a in rest])

def show(expr):
    if isinstance(expr, list):
        return "(" + " ".join(show(e) for e in expr) + ")"
    return str(expr)

env = {**BUILTINS, "x": 7}

print("=== 1. A program is a list, and it runs ===")
program = ["+", 1, ["*", 2, 3]]
print(f"  as data:  {program}")
print(f"  as text:  {show(program)}")
print(f"  evaluated: {sch_eval(program, env)}")

print("\n=== 2. Quote turns a program back into data ===")
quoted = ["quote", ["+", 1, ["*", 2, 3]]]
print(f"  {show(quoted):24} -> {sch_eval(quoted, env)}")
print("  The SAME list. Evaluated it is 7; quoted it is a three-element list.")

print("\n=== 3. Programs are inspectable, because they are just lists ===")
def count_nodes(e):
    return 1 if not isinstance(e, list) else 1 + sum(count_nodes(c) for c in e)
print(f"  {show(program)} has {count_nodes(program)} nodes")
print(f"  its operator is {program[0]!r}, its second argument is {program[2]}")

print("\n=== 4. A MACRO: a function from program to program ===")
def unless_macro(form):
    """(unless test body)  ->  (if test 0 body)"""
    _, test, body = form
    return ["if", test, 0, body]

source   = ["unless", [">", "x", 100], ["*", "x", 2]]
expanded = unless_macro(source)
print(f"  you wrote:   {show(source)}")
print(f"  macro made:  {show(expanded)}")
print(f"  which runs to: {sch_eval(expanded, env)}")
print("  'unless' is not in the evaluator. A user added it, in six lines,")
print("  without touching the language implementation.")

print("\n=== 5. Why Python cannot do this as easily ===")
print("  In Python, 'if x > 100: ...' is syntax, parsed into an AST object")
print("  by the interpreter before your code ever sees it. In Scheme the")
print("  program was ALREADY the data structure, so no parsing step stands")
print("  between you and it. That is homoiconicity, and macros are the payoff.")
```
@LIA.eval(`["main.py"]`, `none`, `python3 main.py`)

### Reading the Code

- `sch_eval` is about twenty lines and needs no parser.  The *Recursive Descent Parsing* session in October exists because most languages do not hand you the tree.  Scheme does, and that is what the One Syntax Rule buys.
- `quote` is the only form that returns its argument untouched.  Everything else recurses.  That one special case is the door between program and data, in both directions.
- `unless_macro` is an *ordinary function*.  It takes a list, returns a list, and the evaluator never knows a macro was involved.  Compare that with what adding `unless` will cost you in the interpreter you build this term: a new AST node, a parser change, and an evaluator branch.
- `count_nodes` works on programs for the same reason it would work on any nested list: there is no difference between the two.

> **Watch out!**  Homoiconicity is not "Lisp has `eval`."  Python has `eval` too, and it takes a *string* that must be parsed.  The Scheme property is that the program is already the data structure the evaluator consumes, so transforming code needs no parsing and no printing back to text.  That is why Lisp macros compose and string-based code generation does not.

### Try It Yourself

Add a form to the language without touching the evaluator.

```python
import operator

BUILTINS = {"+": operator.add, "-": operator.sub, "*": operator.mul,
            ">": operator.gt,  "<": operator.lt,  "=": operator.eq}

def sch_eval(expr, env):
    if isinstance(expr, str):   return env[expr]
    if not isinstance(expr, list): return expr
    head, *rest = expr
    if head == "quote": return rest[0]
    if head == "if":
        test, conseq, alt = rest
        return sch_eval(conseq if sch_eval(test, env) else alt, env)
    if head == "let":
        (name, value), body = rest[0], rest[1]
        return sch_eval(body, {**env, name: sch_eval(value, env)})
    fn = sch_eval(head, env)
    return fn(*[sch_eval(a, env) for a in rest])

def show(expr):
    if isinstance(expr, list):
        return "(" + " ".join(show(e) for e in expr) + ")"
    return str(expr)

env = {**BUILTINS, "x": 7, "y": 3}

# TODO 1: write a macro for `when`:  (when test body) -> (if test body 0)
def when_macro(form):
    return form            # replace me

# TODO 2: write a macro for `double`: (double e) -> (* e 2)
#         Then apply it to (double (+ x y)) and check you get 20.
#         Careful: does your macro evaluate `e` once, or twice? Look at
#         (* e 2) versus (+ e e) and say which you wrote and why it matters.
def double_macro(form):
    return form            # replace me

# TODO 3: write a macro `swap-args` that takes (op a b) and returns (op b a).
#         Apply it to (- 10 3). What comes out, and what does that tell you
#         about how much power a macro has over code you wrote?

for name, macro, src in [("when",   when_macro,   ["when", [">", "x", 0], ["*", "x", 10]]),
                         ("double", double_macro, ["double", ["+", "x", "y"]])]:
    expanded = macro(src)
    print(f"  {name:8} {show(src):28} -> {show(expanded):28}", end="  ")
    try:
        print(f"= {sch_eval(expanded, env)}")
    except (KeyError, TypeError) as e:
        print(f"(not expanded yet: {type(e).__name__})")
```
@LIA.eval(`["main.py"]`, `none`, `python3 main.py`)

Expected output as written: both lines report that the macro has not been written yet.  The unexpanded form still has `when` or `double` at its head, and the evaluator has never heard of either.  Once your macros return real forms, you should see `70` and `20`.

---


# Check Your Understanding

Which of the following is a *pure* function?

[( )] `def f(lst): lst.append(1); return lst`
[(X)] `def f(lst): return lst + [1]`
[( )] `def f(x): print(x); return x`
[( )] `def f(): return time.time()`

---

Scheme's One Syntax Rule is that every compound form is `(operator operand ...)`. The practical consequence is:

[(X)] The program is already a tree when you type it, so the parser has almost nothing to do
[( )] Scheme programs are shorter than equivalent Python
[( )] Precedence is decided by a table at run time
[( )] Every Scheme program is a single expression

---

`(+ 1 2)` evaluates to 3; `'(+ 1 2)` is a three-element list. The quote:

[(X)] Suppresses evaluation, handing you the program itself as data
[( )] Converts the list to a string
[( )] Marks the expression as a comment
[( )] Makes evaluation lazy rather than eager

---

A Lisp macro differs from a function in that:

[(X)] It receives its argument as unevaluated code and returns code, which the evaluator then runs
[( )] It runs faster because it is compiled
[( )] It can access global variables that functions cannot
[( )] It may only be defined at the top level

---

Python has `eval` too. Homoiconicity is still different because:

[(X)] Python's `eval` takes a string that must be parsed; in Scheme the program is already the data structure the evaluator consumes
[( )] Python's `eval` is slower
[( )] Python cannot represent nested lists
[( )] Python's `eval` cannot see local variables

---

**In-class work stops here.**  Everything below is homework and going-deeper material.  Attempt the exercises before the related assignment.

## Exercises (Homework: ~95 minutes total)

### Exercise 1: Replace Loops With map, filter, and reduce (15 min)

Rewrite each of the following using `map`, `filter`, and `reduce`, with no loops or assignments:
- (a) lengths of all words longer than 3 in a sentence
- (b) product of all odd numbers in a list (use `reduce`)
- (c) word count of a string: split, map each word to 1, reduce with +

### Exercise 2: Higher-Order Toolkit (15 min)

Implement and test:
- `compose(f, g)`: apply g then f
- `twice(f)`: apply f two times
- `n_times(f, n)`: apply f exactly n times
- `pipeline(*fns)`: compose any number left-to-right

Demo: `pipeline(str.strip, str.lower, lambda s: s.split())` on `"  Hello World  "`.

### Exercise 3: My Map and Reduce (20 min)

Implement `my_map` and `my_reduce` recursively (no `for` or `while`).  Test each against the built-in on 5 inputs.  Then implement `my_zip(lst1, lst2)` and `my_flatten(nested)` recursively.

### Exercise 4: Purity Refactor (20 min)

Take the impure `f2` and `f3` from Model 1 and refactor them to be pure.  Then write tests that pass for the pure version but fail (or behave unexpectedly) for the impure version.

### Exercise 5: No-Assignment Challenge (25 min)

Compute the average word length of a paragraph using **exactly one expression**: no statements and no intermediate variable names (except the function parameter).  Then discuss: when does point-free style help, and when does it hurt readability?

---

# Extension: Pythonic and Declarative

> Past the 75 minutes.  Nothing in class assumes it.  Model 2 showed that a comprehension and a `map`/`filter` pair compute the same thing.  This extension picks up the other question: what the comprehension *is*, why Python grew four of them, and what the declarative style costs when you pay for it.

## Four Comprehensions, One Idea

The bracket you use decides the container; everything inside is unchanged.  Predict all four outputs, then run.

```python
import sys

scores = [58, 72, 91, 64, 88, 45, 70]

# --- 1. The comprehension is not just for lists ------------------------------
as_list = [min(s + 5, 100) for s in scores if s >= 60]
as_set  = {min(s + 5, 100) for s in scores if s >= 60}
as_dict = {s: min(s + 5, 100) for s in scores if s >= 60}

print("list :", as_list)
print("set  :", sorted(as_set), "  (duplicates collapsed, order gone)")
print("dict :", as_dict)
print()

# --- 2. The double-evaluation problem, and the := fix -------------------------
calls = []


def curve(s):
    calls.append(s)
    return min(s + 5, 100)


calls.clear()
twice = [curve(s) for s in scores if curve(s) >= 70]
print("naive comprehension called curve()", len(calls), "times for", len(scores), "scores")

calls.clear()
once = [c for s in scores if (c := curve(s)) >= 70]
print("walrus comprehension called curve()", len(calls), "times")
print("same answer:", twice == once)
print()

# --- 3. Nesting: the clauses read left to right, like nested for-loops --------
pairs = [(a, b) for a in "ab" for b in [1, 2]]
print("[(a, b) for a in 'ab' for b in [1, 2]] ->", pairs)
print("   the FIRST for is the OUTER loop, exactly as if you had indented them")
print()

# --- 4. Same syntax, different brackets: laziness ------------------------------
listcomp = [n * n for n in range(100000)]
genexpr  = (n * n for n in range(100000))
print("list comprehension holds", sys.getsizeof(listcomp), "bytes")
print("generator expression holds", sys.getsizeof(genexpr), "bytes")
print()

# A generator can be asked about a collection too large to build.
print("any(n * n > 1000 for n in range(10**9)):",
      any(n * n > 1000 for n in range(10**9)))
print("   that answered without building a billion squares: it stopped at the first True")
```
@LIA.eval(`["main.py"]`, `none`, `python3 main.py`)

### Reading the Code

- The four brackets.  `[...]` builds a list, `{...}` a set, `{k: v ...}` a dict, and `(...)` a generator.  The clause grammar, `for` then optional `if`, never changes.  Learn it once and you have four constructions.
- The double evaluation answers CTQ 2.4 with a measurement.  The naive comprehension calls `curve` 11 times for 7 scores, because every element pays for the filter and the survivors pay again for the transformation.  The walrus operator `:=` binds the result inside the `if` so the body can reuse it, and the count drops to 7.  This is the cost of a notation with no place to put a temporary variable, and Python added `:=` largely to give it one.
- Nesting order trips nearly everyone.  `for a ... for b ...` runs `a` as the *outer* loop, the same order you would write the nested `for` statements.  That is the opposite of what the reversed reading "for b, for a" suggests.
- The generator costs 208 bytes against roughly 800 KB for the list, because it stores a recipe rather than a result.  That is CTQ 2.5's answer, and the `any(...)` line is the sharper version: a generator can answer a question about a billion elements because it stops at the first one that settles the matter.  A list comprehension would have to build all billion first.

## What Declarative Buys, and What It Charges

Put the three notations from Model 2 side by side one more time, because the equivalence is the entire argument for the style:

| Notation | The same query |
|---|---|
| Set-builder | $\{\, f(x) \mid x \in S,\ p(x) \,\}$ |
| Python | `[f(x) for x in S if p(x)]` |
| SQL | `SELECT f(x) FROM S WHERE p(x)` |

Each names a source, a filter, and a transformation, and none of them says in what order to do the work.  That silence is the point.  It is what lets SQL's optimizer apply your `WHERE` before your `SELECT`, or use an index, or run the scan on eight cores, without asking you.  You gave up control of the *how* and got machinery in return.

Python's comprehension is the small, tame version.  The language reserves the right to build the list however it likes, and in practice it does roughly what your loop would have done, slightly faster.  Prolog and SQL are the ambitious versions, where "let the machinery find it" means a query planner or a resolution engine.  Same bargain, very different scale.

And it is a bargain, not a gift.  Here is what you pay:

- You cannot step into it.  There is no line to set a breakpoint on, no place to add a `print`, and no `break` when you have seen enough.  Refactoring a comprehension back into a loop is a routine debugging move, and having to do it is the cost showing up.
- You cannot easily short-circuit it.  A list comprehension always runs to the end of the source.  A generator can stop early, which is why `any` and `next` pair with generators and not with list comprehensions.
- It stops scaling with depth.  One `for` and one `if` reads well.  Three `for`s, two `if`s, and a conditional expression in the body is a write-only line, and the loop it replaced was better.  A comprehension is a *sentence*; when it needs a paragraph, write the paragraph.
- Fluency is not universal.  Week 0's language-evaluation criteria called readability relative to the reader, and comprehensions are the sharpest example in the language.  The same line is clearer to a fluent Python reader and murkier to a newcomer, and both readings are correct reports about the reader.

> **Watch out!**  "Pythonic" is a claim about idiom, not about brevity, and the two come apart in both directions.  A comprehension that has grown three clauses is short and thoroughly un-Pythonic.  An explicit loop with a good name is longer and, at that point, the idiomatic choice.  When you catch yourself defending a line because it is clever, you have stopped arguing about idiom.

### Critical Thinking Questions

20.  The dict comprehension printed its pairs in the order the scores appeared, while the set printed in an order you did not choose.  Which of those two is a *guarantee* of the language and which is an accident of the implementation?  Look it up before answering, and say how you checked.
21.  `[c for s in scores if (c := curve(s)) >= 70]` fixes the double evaluation, but a reader now has to notice that the `if` clause has a side effect on the body.  Is that a fair trade?  Give the version you would actually ship, and defend it.
22.  SQL's optimizer is free to reorder your query because you did not specify an order.  Python's comprehension has essentially no optimizer.  What would Python have to give up to earn one?  (Consider: what could `f` do that a SQL expression cannot?)
23.  A comprehension cannot `break`.  A generator plus `next` can stop whenever the consumer likes.  Explain that difference in terms of *who controls the loop*, and connect it to why `reduce` was the awkward one of the big three in Part II.
24.  Your project language will need some way to build a collection.  Decide now whether it gets a comprehension, and write two sentences for `SEMANTICS.md`: what the syntax is, and whether it is lazy.  If you say no, say what the programmer writes instead.

### Try It Yourself

```python
# TODO 1: rewrite each of these as a single comprehension, then decide, for
#         each one, whether the comprehension is actually the better code.
#         Say so explicitly. One of the three should be left as a loop.
#
#   (a) result = []
#       for w in words:
#           if len(w) > 3:
#               result.append(w.upper())
#
#   (b) counts = {}
#       for w in words:
#           counts[w] = counts.get(w, 0) + 1
#
#   (c) best = None
#       for w in words:
#           if best is None or len(w) > len(best):
#               best = w

words = ["to", "be", "or", "not", "to", "be", "that", "is", "the", "question"]

# TODO 2: write the SQL statement that corresponds to your answer for (a),
#         treating `words` as a one-column table. Then say which part of your
#         Python is the SELECT, which is the FROM, and which is the WHERE.

# TODO 3: (b) counts words. Write it as a comprehension and then explain why
#         the result is wrong, in terms of what a comprehension cannot do that
#         the loop's accumulator could. This is the one to leave as a loop.
```
@LIA.eval(`["main.py"]`, `none`, `python3 main.py`)

---

# Extension: Going Further with Scheme

> Past the 75 minutes.  Nothing in class assumes any of it.  Read it if the Scheme assignment left you wanting more, or later in the term if you take the Scheme direction on the Functional assignment.  The Scheme cells want a real REPL; the Python cells run in the page as usual.

## 9.  Where This Picks Up

You already wrote recursion over `car` and `cdr` in *Functional Programming in Scheme, Part 2*.  The base-case-plus-recursive-case shape you used there is the same one `my_reduce` used above, and the same one `evaluate` will use when it walks an AST in October.  This extension starts where that session stopped: what recursion *costs*, how Scheme's scoping forms differ, and how to build code out of lists on purpose.

Model 9 covers one of the most practical differences between Scheme and Python: what happens when recursion goes very deep.  Scheme guarantees that a tail-recursive function uses no more stack space than a simple loop.  So an algorithm that is naturally recursive (like traversing a million-element list) is both clear and efficient in Scheme.  Python offers no such guarantee, which is why Python programmers reach for `for` loops even when recursion would be cleaner.

> **Watch out!** `define` in Scheme is not assignment in the imperative sense.  Writing `(define x 5)` does not create a mutable variable you update later; it introduces a name binding in the current environment.  In functional Scheme style, you do not reassign `x`.  Instead, you pass updated values forward as function arguments (hence the accumulator pattern in tail recursion).  If you find yourself wanting to write `(set! x (+ x 1))` inside a loop, stop and think about how to express the same idea with a recursive accumulator parameter.

## Model 9: Tail Recursion, Scheme vs Python

A **tail call** is a recursive call that is the *last* operation in a function: no pending work remains after the call returns.  Scheme (and Racket) *guarantee* tail-call optimization (TCO), so a tail-recursive function uses O(1) stack space.  Python does not perform TCO; deep tail calls still overflow the call stack.

The cell below shows both a naive (non-tail) factorial and a tail-recursive accumulator version in Python.  It counts stack frames to make the difference concrete.

```python
import sys

def fact_naive(n):
    """Non-tail-recursive: the multiplication happens AFTER the recursive call returns."""
    if n == 0:
        return 1
    return n * fact_naive(n - 1)   # pending multiply on the stack

def fact_tail(n, acc=1):
    """Tail-recursive: accumulator carries the work; nothing left to do on return."""
    if n == 0:
        return acc
    return fact_tail(n - 1, acc * n)  # last action IS the call

# Show call-depth difference using a frame counter
def count_frames_naive(n, depth=0):
    if n == 0:
        return depth
    return count_frames_naive(n - 1, depth + 1)

def count_frames_tail(n, depth=0):
    if n == 0:
        return depth
    return count_frames_tail(n - 1, depth + 1)

print("fact_naive(10)  =", fact_naive(10))
print("fact_tail(10)   =", fact_tail(10))
print()
print("Python default recursion limit:", sys.getrecursionlimit())
print()

# Show that both reach the same depth - Python cannot collapse either
print("Frames used by naive  fact(20):", count_frames_naive(20))
print("Frames used by tail   fact(20):", count_frames_tail(20))
print()

# In Scheme, the tail version would keep a FIXED stack depth.
# In Python we can simulate TCO with a trampoline:
def trampoline(f, *args):
    """Run a 'thunk-returning' function without growing the stack."""
    result = f(*args)
    while callable(result):
        result = result()
    return result

def fact_trampoline(n, acc=1):
    if n == 0:
        return acc
    return lambda: fact_trampoline(n - 1, acc * n)

print("Trampoline fact(10):", trampoline(fact_trampoline, 10))
print("Trampoline fact(100):", trampoline(fact_trampoline, 100))
print()
print("Key insight: Scheme tail calls are as cheap as loops.")
print("Python tail calls still grow the stack unless you add a trampoline manually.")
```
@LIA.eval(`["main.py"]`, `none`, `python3 main.py`)

### Critical Thinking Questions

8.  In `fact_naive`, where is the pending multiplication "stored" between the recursive call and its return?  What data structure holds it, and what happens to that structure in a Scheme tail call?
9.  The trampoline converts recursive calls into *returned values* (thunks).  Explain in one sentence why that prevents stack growth, and identify the analogous mechanism Scheme's runtime uses.
10.  If you rewrote `sum` from *Recursion Is the Loop* above as a tail-recursive `sum-tail` with an accumulator, in what order would the additions be performed compared with the naive version?  Does the final answer change?
11.  Python's recursion limit defaults to 1000.  Name one algorithm from your CS coursework where hitting this limit would be a real practical concern, and describe how you would restructure it.

---

Model 10 asks a small but important question: when you write several name bindings together, can each one see the others?  The three forms `let`, `let*`, and `letrec` give three different answers.  The difference matters for reading Scheme code correctly, and it explains why Python's `def` and assignment behave the way they do.

## Model 10: let, let*, and letrec

Scheme's local binding forms give names to intermediate values.  They differ in *when* bindings become visible:

- `let`: all right-hand sides are evaluated in the outer environment; the bindings are parallel and independent.
- `let*`: the bindings are sequential; each right-hand side sees all previous bindings in the same `let*`.
- `letrec`: all names are in scope for all right-hand sides (required for mutually recursive local functions).

The Python simulation below models each form's scoping rule explicitly so you can observe the difference.

```python
# Simulate Scheme's let / let* / letrec scoping rules in Python

def demo_let():
    """
    Scheme:
      (let ((x 1)
            (y 2))
        (+ x y))
    All bindings use the OUTER scope.  Neither x nor y sees the other.
    """
    outer_x = 10
    # In a real 'let', both RHS are evaluated with outer_x = 10
    x = outer_x + 1   # x = 11
    y = outer_x + 2   # y = 12  (not x + 2, because let is parallel)
    result = x + y
    print(f"let:   x={x}, y={y}, x+y={result}")
    print("       Note: y used outer_x (10), NOT the new x (11)")

def demo_let_star():
    """
    Scheme:
      (let* ((x 1)
             (y (+ x 1)))   ; y CAN see x
        (+ x y))
    Sequential: each binding sees the previous ones.
    """
    x = 1
    y = x + 1   # y = 2; uses the JUST-BOUND x
    result = x + y
    print(f"let*:  x={x}, y={y}, x+y={result}")
    print("       Note: y used the new x (1), giving y=2")

def demo_letrec():
    """
    Scheme:
      (letrec ((even? (lambda (n) (if (= n 0) #t (odd?  (- n 1)))))
               (odd?  (lambda (n) (if (= n 0) #f (even? (- n 1))))))
        (even? 4))
    Both names are in scope for BOTH RHS, needed for mutual recursion.
    """
    # Python nested functions already implement letrec-like mutual visibility
    def even_q(n):
        if n == 0:
            return True
        return odd_q(n - 1)

    def odd_q(n):
        if n == 0:
            return False
        return even_q(n - 1)

    print(f"letrec: even?(4) = {even_q(4)}")
    print(f"letrec: odd?(7)  = {odd_q(7)}")
    print("        Note: even? and odd? reference each other - impossible with let or let*")

demo_let()
print()
demo_let_star()
print()
demo_letrec()
print()

# Bonus: show that let evaluates its bindings in parallel
print("--- Parallel swap (let) vs sequential (let*) ---")
a, b = 3, 7
# let swap: new_a = old_b, new_b = old_a  (evaluated simultaneously from outer scope)
new_a_let = b    # uses original b
new_b_let = a    # uses original a
print(f"let  swap: a={new_a_let}, b={new_b_let}  (correct parallel swap)")

# let* swap: sequential, so new_a is visible when new_b is evaluated
new_a_star = b           # new_a = 7
new_b_star = new_a_star  # new_b sees new_a (7), not original a (3)
print(f"let* swap: a={new_a_star}, b={new_b_star}  (WRONG - new_a leaked into new_b)")
```
@LIA.eval(`["main.py"]`, `none`, `python3 main.py`)

### Critical Thinking Questions

12.  In the "parallel swap" demonstration, `let` gives the correct result but `let*` does not.  Explain this in terms of evaluation order and what each binding's right-hand side is permitted to see.
13.  Why does `letrec` require all names to be in scope *before* any right-hand side is evaluated?  Construct a two-function mutual-recursion example where omitting `letrec` (using `let*` instead) would fail.
14.  Python's `def` inside a function body corresponds most closely to which Scheme binding form?  Justify your answer by pointing to the scoping rule each uses.
15.  A Scheme `let` can always be rewritten as a `lambda` application: `(let ((x 5)) body)` becomes `((lambda (x) body) 5)`.  Write out this transformation for the parallel-swap example.  What does this equivalence reveal about `let` as syntactic sugar?

---

Model 11 brings the pieces together.  You now know how Scheme evaluates expressions and how lists are constructed, so you can use Scheme's quasiquoting mechanism to build lists that are *programs* and then hand them to `eval`.  This is homoiconicity made concrete and operational.  The Python simulation in the runnable cell re-implements the same ideas so you can experiment without a Racket installation.

## Model 11: Quasiquoting and List Operations

Quasiquoting (the backtick, `\``) is a templating mechanism.  The entire form is treated as data (like `'`), *except* that subexpressions preceded by `,` (unquote) or `,@` (unquote-splicing) are evaluated.  It is the foundation of Scheme macros and a useful tool for building lists.

```python
# We cannot run Racket here, so we simulate quasiquoting semantics in Python
# to make the evaluation rules concrete.

def quasiquote(template, env):
    """
    Recursively process a nested list 'template'.
    - Strings that start with ',' are unquoted: look up the rest in env.
    - Lists that start with ',@' are spliced in.
    - Everything else is kept as-is (quoted).
    """
    if isinstance(template, list):
        result = []
        for item in template:
            if isinstance(item, list) and len(item) == 2 and item[0] == ',@':
                # Unquote-splicing: evaluate and extend
                val = env.get(item[1], [])
                if isinstance(val, list):
                    result.extend(val)
                else:
                    result.append(val)
            elif isinstance(item, str) and item.startswith(','):
                # Unquote: evaluate the name
                name = item[1:]
                result.append(env.get(name, item))
            elif isinstance(item, list):
                result.append(quasiquote(item, env))
            else:
                result.append(item)
        return result
    elif isinstance(template, str) and template.startswith(','):
        return env.get(template[1:], template)
    else:
        return template

# Example 1: basic unquote
env1 = {'x': 42, 'name': 'Alice'}
tmpl1 = ['define', ',name', ',x']
print("Template:", tmpl1)
print("Result:  ", quasiquote(tmpl1, env1))
# Equivalent Scheme: `(define ,name ,x)  with name='Alice' x=42
# => (define Alice 42)
print()

# Example 2: unquote-splicing to build a function call
env2 = {'fname': 'my-func', 'args': [1, 2, 3]}
tmpl2 = [',fname', [',@', 'args']]
print("Template:", tmpl2)
print("Result:  ", quasiquote(tmpl2, env2))
# Equivalent Scheme: `(,fname ,@args)  => (my-func 1 2 3)
print()

# Example 3: building a list of squares using quasiquote + list operations
nums = [1, 2, 3, 4, 5]

# car / cdr / cons equivalents
def car(lst): return lst[0]
def cdr(lst): return lst[1:]
def cons(x, lst): return [x] + lst
def null_p(lst): return lst == []

def my_map(f, lst):
    if null_p(lst):
        return []
    return cons(f(car(lst)), my_map(f, cdr(lst)))

def my_filter(pred, lst):
    if null_p(lst):
        return []
    if pred(car(lst)):
        return cons(car(lst), my_filter(pred, cdr(lst)))
    return my_filter(pred, cdr(lst))

def my_reduce(f, init, lst):
    if null_p(lst):
        return init
    return my_reduce(f, f(init, car(lst)), cdr(lst))

squares = my_map(lambda x: x * x, nums)
evens   = my_filter(lambda x: x % 2 == 0, nums)
total   = my_reduce(lambda a, b: a + b, 0, nums)

print("Original list:", nums)
print("Squares      :", squares)
print("Evens        :", evens)
print("Sum          :", total)
print()

# Demonstrate that (map f (filter pred lst)) composes cleanly
sum_of_even_squares = my_reduce(
    lambda a, b: a + b, 0,
    my_map(lambda x: x * x, my_filter(lambda x: x % 2 == 0, nums))
)
print("Sum of squares of even numbers:", sum_of_even_squares)
print("Expected: 4 + 16 = 20")
```
@LIA.eval(`["main.py"]`, `none`, `python3 main.py`)

### Critical Thinking Questions

16.  In Scheme, `` `(define ,name ,x) `` is syntactic sugar for a call to the `quasiquote` special form. Explain the difference between `,name` (unquote) and `,@name` (unquote-splicing) in terms of what the resulting list structure looks like.
17.  Macros in Scheme use quasiquoting to construct code.  If you wanted to write a `my-when` macro that desugars `(my-when test body)` into `(if test body (void))`, write out the quasiquoted template the macro body would return.
18.  The `my_map / my_filter / my_reduce` pipeline in the cell composes without intermediate variable names.  Compare this style with a Python `for`-loop equivalent and describe one advantage and one disadvantage of each.
19.  Unquote-splicing (`,@`) inserts a list's *elements* rather than the list itself.  Write a Scheme expression (or Python simulation) that uses `,@` to combine two argument lists into a single function call, and explain what would go wrong if you used `,` (plain unquote) instead.

---

## 10.  Taking It Back to the REPL

Everything above simulated Scheme semantics in Python so the cells could run in the page.  The real thing belongs in a real REPL, and you already have one open from *Functional Programming in Scheme, Part 2*: [try.scheme.org](https://try.scheme.org), or a local install.

The **Functional Programming with Scheme** assignment is where this gets written rather than read.  If you want more than it asks for, the natural next steps are the three below.

1.  *Trees, of course.*  Represent an arithmetic expression in Scheme as nested lists, like `'(* (+ 2 3) 4)`, and write `(evaluate tree)` for `+ - * /` in about fifteen lines.  Keep it.  In October you will write the parser whose whole job is to *build* that list from the flat text `(2 + 3) * 4`, and comparing the two line counts is the punchline of the front half of this course.
2.  *Quote experiments.*  Using `car`, `cdr`, and `cons`, take apart the list `'(+ 1 2)` and rebuild it as `'(* 1 2)`.  You have just written a program transformer, which is all a macro is.
3.  *Tail calls for real.*  Write a tail-recursive `sum` with an accumulator and run it on a list of one million elements.  It will finish in Scheme.  Try the same depth in Python and read the traceback.

### Check Yourself on Tail Calls

Scheme guarantees that a tail-recursive call uses no additional stack. That means:

[(X)] Recursion can express iteration with constant space, so a loop is not needed for a million-element traversal
[( )] Recursive functions run faster than loops
[( )] Every recursive function is automatically tail recursive
[( )] Deep recursion is impossible

---

---

### If you explore the evaluator: reflection prompts

Answer these in your course notebook if you work through the metacircular evaluator tutorial.

**Reflection 1.**  The word "metacircular" implies the evaluator is defined in terms of itself.  Our evaluator is written in Python, not Scheme, so in what sense is it still "metacircular"?  What would it take to port our evaluator from Python into the Scheme subset our evaluator understands, and what would that accomplish?

**Reflection 2.**  The course final project asks you to extend a language interpreter.  Identify three specific features from this evaluator (the `Env` chain, `Procedure` as a closure, or TCO via trampoline) that map directly to something you will need in your final project.  For each, write one sentence explaining the connection.

**Reflection 3.**  Our evaluator has no type system: `(+ 1 "hello")` raises a Python `TypeError` that leaks through the abstraction boundary.  Describe at least two changes you would make to add a static type system to this evaluator.  Consider: where would type annotations appear in the s-expression representation?  Where in `scheme_eval` would you insert a type-checking pass?  What new data structure would represent a type error vs. a value?

---

### Further reading on metacircular evaluation

- **Runnable example archive**: [SchemeInterpreter.zip](https://www.billmongan.com/Ursinus-CS374-Fall2026/files/replit/SchemeInterpreter.zip): a complete reference implementation of this activity's evaluator.  Explore it after you have attempted the activity yourself.

- **SICP Chapter 4**: Abelson & Sussman, *Structure and Interpretation of Computer Programs*, 2nd ed.  The original metacircular evaluator.  MIT Press open access: [https://mitp-content-server.mit.edu/books/content/sectbyfn/books_pubs/6515/sicp.pdf](https://mitp-content-server.mit.edu/books/content/sectbyfn/books_pubs/6515/sicp.pdf)

- **"The Art of the Interpreter"**: Guy Steele & Gerald Sussman (1978).  The founding paper on meta-circular evaluation, environments, and the relationship between interpreters and compilers.  [MIT AI Memo 452.](https://dspace.mit.edu/handle/1721.1/6094)

- **Norvig's `lis.py`**: Peter Norvig's "How to Write a (Lisp) Interpreter in Python."  Norvig's version is short and clear; ours extends it with TCO and a fuller set of special forms.  Search for "Norvig lis.py" to find his blog post.

- **R7RS Scheme specification**: The current small Scheme standard.  Section 4 (Expressions) maps directly to our `scheme_eval` dispatch table.  Available at [https://small.r7rs.org/](https://small.r7rs.org/).

- **"Proper Tail Recursion and Space Efficiency"**: Will Clinger (PLDI 1998).  A careful treatment of what tail-call optimization guarantees and how to implement it correctly.

---

## Reflection Prompt

Purity forbids a function from leaving traces on the world.  That makes it trustworthy, but it also means the function *cannot do anything* (no printing, no saving) without breaking the rules.  Real programs must do things.  Where should the impurity live in a well-organized program?  Name a non-programming system (kitchen, lab, organization) organized the same way.

---

## Further Reading

- **"Why Functional Programming Matters"**: John Hughes (1990): the classic argument that *composition* is the point: https://www.cs.kent.ac.uk/people/staff/dat/miranda/whyfp90.pdf
- **SICP Sections 1.1-1.3**: Abelson & Sussman: the functional core
- **Python `functools` documentation**: `reduce`, `partial`, `lru_cache`
- **Haskell Tour**: for seeing what pure FP looks like at full scale: https://www.haskell.org/tutorial/
- **"Structure and Interpretation of Computer Programs"**: online at https://mitp-content-server.mit.edu/books/content/sectbyfn/books_pubs/6515/sicp.pdf
- [Haskell Essentials](https://www.billmongan.com/Ursinus-CS374-Fall2026/Tutorials/HaskellEssentials): the Haskell behind this unit, covering functions, pattern matching, algebraic data types, and higher-order style.
- [Parser Combinators: Parsers as First-Class Values](https://www.billmongan.com/Ursinus-CS374-Fall2026/Tutorials/ParserCombinators): parsers themselves as composable higher-order functions.
- Monads (Maybe, List, IO), the monad laws, do-notation, thunks, and infinite streams: not covered in the course materials.  Direction A of the Functional assignment covers lazy sequences and generators in Python.
- Abelson and Sussman.  *Structure and Interpretation of Computer Programs*, Chapter 1 (free online).
- The Racket Guide, chapters 1 through 4: https://docs.racket-lang.org/guide/
- Paul Graham.  "The Roots of Lisp" (online essay): eval in a page.
- [Build a Complete Interpreter in Python](https://www.billmongan.com/Ursinus-CS374-Fall2026/Tutorials/BuildAnInterpreter): its metacircular Scheme evaluator section covers s-expression parsing, environment chains, the evaluator core, the global environment, and tail-call optimization via trampoline.  The Interpreter assignment has you build the same architecture for the Mini language.

---
- Continuation-passing style and MapReduce live where they are assessed: Directions B and E of the [Functional assignment](https://www.billmongan.com/Ursinus-CS374-Fall2026/Assignments/Functional).  Read those directions before choosing them.

---

Up next: *Syntax and BNF/EBNF*, where we stop writing programs and start writing down, precisely, what a program is allowed to look like.  That is the machinery Scheme almost does without, and the machinery your own language will need.

Everything in these three sessions, purity through code as data, comes back twice: in the **Functional Programming with Scheme** assignment handed out today, and in the Functional Programming assignment in November.
