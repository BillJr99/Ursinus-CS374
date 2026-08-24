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

When you give someone driving directions, you say "turn left on Main, go two blocks, turn right."  That is imperative programming: a step-by-step recipe for *how* to get somewhere.  Functional programming is like giving the destination instead: you describe *what* you want the data to look like, and let the language figure out how to get there.  This shift in thinking is why functional ideas now show up in every modern language (Python, JavaScript, Java, Rust) and why mastering them makes you a dramatically more expressive programmer.

## Learning Goals

By the end of this activity, you will be able to:

- Distinguish pure functions from impure ones and explain why purity enables referential transparency, testability, and safe parallelism
- Apply `map`, `filter`, and `reduce` to transform and aggregate data without explicit loops
- Write higher-order functions that accept and return other functions, including anonymous `lambda` expressions
- Use currying and partial application to build specialized functions from general ones
- Implement recursive solutions to iterative problems without using mutable state or assignment
- Read Scheme's one syntactic form and explain why a language whose programs are already trees needs almost no parser
- Write a macro: a function that takes a program as data, returns a different program, and hands it back to the evaluator

With the interpreter core complete through *Control Flow Semantics*, the course turns from building languages to inhabiting one paradigm deeply.  We practice **functional programming** in Python (`lambda`, `map`, `filter`, `reduce`) with the discipline of **purity** and **immutability**, because the functional toolkit is both a daily professional skill (data pipelines, modern Java/JavaScript/Rust) and the bridge to the lambda calculus ahead.  We finish in Scheme, where the paradigm is native and where a program is literally a list you can take apart.

Arc: **purity and why it pays -> the big three combinators -> higher-order thinking -> currying and partial application -> recursion without loops -> code as data**

> **Before You Begin:** This activity assumes you can:
> - Write and call Python functions, including functions that take other functions as arguments
> - Use Python lists and understand that lists are mutable (they can be changed in place)
> - Recognize a `for` loop and describe what it does step by step
>
> If any of these feel shaky, review them first.

---

## Directions and Group Roles

Work in your POGIL team with your rotated roles (**Manager**, **Recorder**, **Presenter**, **Reflector**).  Please think each model and question through on your own first, then talk it over with your group.  The Recorder posts your answers to the Class Activity Questions discussion board, and the Presenter reports out wherever you disagreed or found another approach.

> **How today runs.**  Parts I through IV are the core, and Part V (code as data) is the payoff we want to reach together, so keep an eye on the clock: if the period is running short, Part IV's recursive rewrites of `map`, `filter`, and `reduce` are the ones to read at home, since Exercise 3 has you write them anyway.  Everything after *Check Your Understanding* is homework, and the Scheme extension at the end is there for whoever takes the Scheme direction on the Functional assignment.

---

## Key Concepts

Here is a plain-English glossary of the terms this activity uses.  Please come back to this table whenever one of them starts to feel slippery.

| Term | Plain-English meaning | Why it matters |
|------|-----------------------|----------------|
| **Pure function** | Output depends only on inputs; nothing outside the function changes | Pure functions can be tested, cached, substituted, and parallelized fearlessly |
| **Side effect** | Anything a function does besides return a value: mutating, printing, reading globals | Side effects are exactly what purity forbids; spotting them is a skill |
| **Immutability** | Never modify existing data; build new data instead | Removes an entire class of "who changed my list?" bugs |
| **Referential transparency** | A call can be replaced by its result anywhere without changing behavior | The formal payoff of purity; the license for safe refactoring |
| **`map`** | Transform every element of a list with a function | Replaces the "loop that builds a new list" pattern |
| **`filter`** | Keep only the elements that satisfy a test | Replaces the "loop with an `if` inside" pattern |
| **`reduce` (fold)** | Collapse a whole list into one value with a two-argument function | Replaces the "loop with an accumulator variable" pattern |
| **Higher-order function** | A function that takes functions as arguments or returns one | The mechanism behind combinators, decorators, and callbacks |
| **Lambda** | A small anonymous function written inline | Lets you hand behavior to `map`/`filter`/`reduce` without naming it |
| **Currying / partial application** | Supplying a function's arguments one at a time to build specialized functions from general ones | Turns general tools into custom ones; central to Haskell and the lambda calculus ahead |

---

# Part I: Purity

## 1.  Functions Like Mathematics Meant

A pure function's output depends only on its inputs, and it changes nothing outside itself.  No mutation of arguments, no global reads or writes, no printing, no randomness.  Purity buys three concrete powers:

1.  **Substitution**: a call can be replaced by its result anywhere (referential transparency)
2.  **Testability**: no setup, no teardown: just input -> expected output
3.  **Parallel safety**: no shared state means no interference

Immutability is purity's partner.  Functional style does not modify a list; it produces a new one.

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

> **CTQ 1.1** `pure_double` and `impure_double` return the same value for `[1, 2, 3]`, yet they differ fundamentally.  What is the difference, and why does it matter when a function is called more than once?

> **CTQ 1.2** The rule "calling a pure function twice with the same input always gives the same output" is called **referential transparency**.  Which functions in the code above have this property?  Which do not?

> **CTQ 1.3** Could `pure_double` safely run on two halves of the list in parallel and merge the results?  Could `impure_double`?  Explain.

---

Think of purity the way you think about a calculator: press `2 + 3` and you always get `5`, no matter how many times you press it and no matter what else is on your desk.  Model 1 gives you six functions and asks you to decide which ones behave like that trustworthy calculator and which ones secretly remember (or change) the world around them.  Use what you learned from the opening example above to guide your classification.

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

- The audit turns on one question per function: given the same arguments, does it always return the same value, and does it change anything outside itself?  Both halves must hold for purity.
- `f4` reads a global without writing one.  It is still impure, because "same input, same output" fails the moment somebody else changes that global.  Purity is a property of the function *and* everything it can observe.
- The mutation surprise at the top is the practical stake: `impure_double` looked like a transformation and was in fact an edit.  Calling it twice gives different answers from the same argument, which is exactly what referential transparency forbids.

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

Expected output: `f_reads_global(10)` returns 10 and then 11, from identical arguments.  That single changed digit is the case for purity, made in one line.

> **CTQ 1.4** Classify each function as pure or impure.  For each impure one, name the exact disqualifying feature.

> **CTQ 1.5** `f4` reads but never writes a global.  What referential transparency property does it still forfeit?  Construct a test that would *pass* today but *fail* after appending to `LOG_LINES`.

---

# Part II: The Big Three Combinators

The next two models focus on the three combinators that replace nearly every explicit loop you have ever written.  Before we look at any code, notice that each combinator corresponds to a question you already ask about data: "what does each element look like after a change?", "which elements do I want to keep?", "what single summary value do these elements produce?"  You have been answering these questions with `for` loops; now you will answer them with a single function call.

> **Watch out!**  Python's `map` and `filter` do not prevent you from passing in an impure function, one that prints, mutates globals, or reads from a file.  The combinators themselves are pure, but they will faithfully execute whatever function you hand them.  Always make sure the lambda or function you pass in has no side effects, or you lose the guarantees that make functional style valuable.

## 2.  Map, Filter, Reduce

$$\text{map}(f, [x_1, \dots, x_n]) = [f(x_1), \dots, f(x_n)]$$

$$\text{filter}(p, [x_1, \dots, x_n]) = [x_i \mid p(x_i) = \text{True}]$$

$$\text{reduce}(\oplus, [x_1, \dots, x_n], z) = ((z \oplus x_1) \oplus x_2) \oplus \cdots \oplus x_n$$

Each replaces a loop pattern you have written a hundred times.  The key: `map` *transforms* every element, `filter` *selects* elements, `reduce` *collapses* a list to one value.

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

Python gives you two roads to the same destination: the `map`/`filter` combinators you just saw, and *list comprehensions*, which borrow syntax from mathematical set-builder notation.  Model 2 puts them side by side so you can see that they produce identical results while looking quite different.  Understanding both is practical (you will encounter both in real Python codebases) and comparing them deepens your intuition for what "transforming a collection" really means.

> **Watch out!**  Immutability does not mean "constant."  In Python, writing `x = 5` creates a variable that you could reassign at any time.  True immutability in functional programming means that once a data structure is built you never modify it; instead you build a new one.  Python's `tuple` is immutable; a `list` is not.  When you call `pure_double` above, `original` stays unchanged not because Python enforces it, but because the function was *written* to build a new list.  Nothing stops you from writing an impure version; discipline and code review do.

## Model 2: Comprehensions vs. Combinators

Python offers *list comprehensions* as an alternative syntax for map+filter:

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

---

Before moving on to higher-order functions, pause and run one pipeline entirely *by hand*.  If you can produce every intermediate list on paper, `map`/`filter`/`reduce` stop being magic incantations and become bookkeeping you happen not to write yourself.

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

The same computation element by element: note how the two failing scores are *transformed* by `map` but *discarded* by `filter`, so they never reach `reduce`:

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

Run the cell to see the machine agree with your paper trace, fold step by fold step:

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

- Each stage is a separate line producing a separate list, purely so the trace can print the intermediate results.  The one-expression version composes them without ever naming the intermediates.
- `reduce` is the only stage that collapses.  `map` preserves length, `filter` can only shorten, and `reduce` returns one value regardless.  Knowing which stage can change the length is most of debugging a pipeline.
- Nothing is mutated anywhere.  The "running total" column is the accumulator argument travelling from one call to the next, which is what replaces the mutable variable an imperative loop would have needed.

### Try It Yourself

Rebuild the big three from scratch, so you know there is nothing in them.

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
#         from the outside -- so does the mutation inside matter? Argue it.

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

> **CTQ 3.2** The stage diagram materializes two whole intermediate lists (`curved`, `passing`) because the code calls `list(...)`.  In the one-expression pipeline from Section 2 (no `list` calls), do those intermediate lists ever exist in memory?  Connect your answer to the laziness you observed in CTQ 2.5.

> **CTQ 3.3** The running-total column is exactly the accumulator variable from an imperative loop, yet nothing here is mutated.  Where does the "updated" accumulator live on each fold step instead?  And is `reduce` with `traced_add` still pure?  (Careful: `traced_add` prints.)

---

# Part III: Higher-Order Functions

You have already passed functions as arguments: every time you called `map(lambda x: x*2, data)` you handed a function to another function.  Part III asks: what if a function could also *return* a new function?  Think of it like a factory: instead of building one widget, the factory builds a machine that builds widgets. `make_adder(5)` is that factory: call it once and you get back a custom addition function, ready to use anywhere.

## 3.  Functions That Make Functions

A **higher-order function** takes functions as arguments *or* returns functions.  Today we also *return* them, creating parameterized behavior without classes.

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

A composed pipeline like `clean` reads as a single gesture, but the machine executes it one function at a time.  Tracing a composition call by call (writing down each intermediate value) is the fastest way to convince yourself that data really does flow left to right through `pipeline`, and right to left through `compose`.

## Model 4: Composition, Traced One Call at a Time

**Worked example.**  Trace `clean("  Hello World  ")` where `clean = pipeline(str.strip, str.lower, lambda s: s.replace(' ', '_'))`.  Since `pipeline` folds with `lambda v, f: f(v)`, the string threads through the functions in order:

| Step | Function applied | Input value | Output value |
|------|------------------|-------------|--------------|
| start | - | `"  Hello World  "` | - |
| 1 | `str.strip` | `"  Hello World  "` | `"Hello World"` |
| 2 | `str.lower` | `"Hello World"` | `"hello world"` |
| 3 | `s.replace(' ', '_')` | `"hello world"` | `"hello_world"` |

As a flow diagram, and contrast with `compose`, which runs right to left:

```bash
pipeline:  x --> [strip] --> [lower] --> [replace ' '->'_'] --> "hello_world"
compose:   compose(f, g)(x) = f(g(x))    -- g runs FIRST, then f
```

The cell below wraps each stage so it narrates itself, then swaps the first and last stages to show that composition order is part of the meaning:

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

Notice that `traced` is itself a higher-order function: it consumes a function and returns a new one with the same behavior plus narration, the same shape as `twice` and `compose`.

`compose(f, g)` returns `lambda x: f(g(x))`.  Evaluating `compose(str.lower, str.strip)("  ABC  ")` therefore:

[( )] Applies `lower` first, then `strip`
[(X)] Applies `strip` first (it is innermost), then `lower`
[( )] Applies both simultaneously
[( )] Raises an error because strings are immutable

**Critical Thinking Questions (CTQs)**

> **CTQ 4.1** Each stage's output becomes the next stage's input.  What requirement connects the *return type* of one stage to the *parameter type* of the next?  The swapped `messy` pipeline still ran without error; did it satisfy your requirement, and is "runs without error" the same as "correct"?

> **CTQ 4.2** Unroll `pipeline(f, g, h)(x)` by hand using the left-fold formula from CTQ 2.2 to show it computes `h(g(f(x)))`.  Then unroll `compose(f, g)(x)`.  Which order do you find easier to read, and why might data-pipeline libraries prefer left-to-right?

> **CTQ 4.3** `pipeline` is implemented with `reduce`, but folding over a list of *functions* rather than numbers.  In the trace table, what plays the role of the accumulator, and what is its value after step 2?

---

If higher-order functions are factories, then currying and partial application are factory *customizations*.  Imagine a general `power(base, exp)` function.  Partial application lets you say "I always want `exp=2`; give me a `square` function."  Currying takes this further: it restructures any multi-argument function so you can supply arguments one at a time, producing a chain of single-argument functions.  This style shows up everywhere in functional languages like Haskell, and understanding it will make the lambda calculus we study later feel natural.

## 4.  Partial Application and Currying

**Partial application**: fix some arguments of a function to produce a simpler one.

**Currying**: transform a function `f(a, b)` into `f(a)(b)`: a chain of single-argument functions.

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

In Python you have used `for` loops to walk through lists.  But a `for` loop requires mutable state: a counter variable that changes on every iteration.  Pure functional programming avoids mutable state entirely, so loops are off the table.  The replacement is recursion: a function that solves a big problem by calling itself on a smaller piece of that problem.  Model 5 shows you that `map`, `filter`, and `reduce` (which you already know) can themselves be written as recursive functions, making their structure visible and precise.

> **Watch out!**  When students first encounter "no loops allowed," a common instinct is to reach for a `while True` loop with a counter.  That is still a loop!  Pure functional recursion means the function calls itself with a *smaller* argument: there is no loop variable, no `i += 1`, and no mutation of any list.  If you find yourself writing an assignment statement inside a recursive function, pause and reconsider.

## 5.  Thinking Recursively

In pure functional style, **there are no loops**, only recursion.  Every loop corresponds to a recursive function:

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

Model 6 pushes recursion in two new directions: *mutual* recursion (two functions that call each other) and *structural* recursion (recursing along the shape of nested data, not a numeric counter).  You will also see a fully functional merge sort, no mutation anywhere.  Before diving in, study the worked example below that shows how to translate an imperative loop into a functional composition step by step.

**Worked Example: Imperative -> Functional**

Suppose you have this imperative code that sums the squares of all even numbers in a list:

```python
# Imperative version. 5 statements, 2 mutation points
result = 0
for x in nums:
    if x % 2 == 0:
        result += x ** 2
```

Here is how to transform it step by step into a functional composition:

**Step 1.  Identify the three loop concerns separately:**
- *Filter*: keep only even numbers -> `x % 2 == 0`
- *Transform*: square each kept number -> `x ** 2`
- *Aggregate*: sum the results -> `+`

**Step 2.  Write each concern as a lambda:**

```python
is_even  = lambda x: x % 2 == 0
square   = lambda x: x ** 2
add      = lambda a, b: a + b
```

**Step 3.  Assemble with `filter`, `map`, `reduce`:**

```python
from functools import reduce
result = reduce(add, map(square, filter(is_even, nums)), 0)
```

**Step 4; Inline the lambdas for a one-liner (optional):**

```python
result = reduce(lambda a, b: a + b,
                map(lambda x: x**2,
                    filter(lambda x: x % 2 == 0, nums)), 0)
```

The result is identical to the loop.  The difference: the functional version has **no mutation** (`result` is never reassigned), **no loop variable**, and each concern is a named, testable piece.

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

# Part V: Code as Data

## 7.  Everything Is (operator operands...)

**Scheme has essentially one syntactic form**: the parenthesized prefix application `(f a b c)`.  Arithmetic is not special: `(+ 2 3)` is 5; `(* (+ 2 3) 4)` is 20.  Definitions, conditionals, and functions are *special forms* wearing the same parentheses:

```scheme
(define pi 3.14159)
(define (square x) (* x x))
(if (> x 0) "positive" "not positive")
(lambda (x) (* x x))
```

**Notice what vanished.**  No precedence (prefix notation needs none: the tree is explicit in the nesting), no associativity rules, no statement-versus-expression divide (everything is an expression with a value).  Your ambiguity module's entire ladder grammar exists to recover, for infix notation, the tree that Scheme's syntax simply *is*.  The parentheses are the AST, written by hand.

---

This model makes the connection between Scheme's syntax and the Abstract Syntax Trees you have been building in Python explicit.  In Python, a parser works hard to transform the flat text `2 + 3 * 4` into a tree that captures precedence; in Scheme, the programmer simply *writes* the tree directly as nested parentheses.  Model 5 asks you to feel the difference by doing the translation yourself.

## Model 5: Trees Without a Parser

### Critical Thinking Questions

1.  Translate `2 + 3 * 4` and `(2 + 3) * 4` into Scheme.  Which required parentheses beyond the operators' own, and why does the question almost not make sense?
2.  Draw the AST your CS374 parser builds for `2 + 3 * 4`, then write the Scheme expression beside it.  State the relationship in one sentence; it is the punchline of the day.
3.  A Scheme "lexer" needs roughly four token types.  Name them, and explain what a Scheme "parser" does that your recursive descent parser did not have to sweat (hint: almost nothing; nesting is explicit).
4.  What did Scheme's designers *pay* for this uniformity, in the *Evaluating Languages* criteria?  (Ask anyone who has counted parentheses.)

---

## 8.  The Big Idea: Homoiconicity

`'(+ 1 2)` is a list whose first element is the symbol `+`: **the program is a data structure the language itself manipulates**, and `(eval '(+ 1 2))` runs it.  This property, **homoiconicity**, is why Lisp dialects have **macros**: functions that receive *code as lists*, transform it, and hand the result back to the evaluator, which is your `for`-loop desugaring exercise, except performed by user programs rather than by the language implementer.  The AST you carefully constructed in Python with classes is, in Scheme, just... the list you typed.

## Model 6: Homoiconicity, Executed

The claim above is easy to nod at and hard to feel.  Here it is as code you can run.  A Scheme program is a list; we represent it as a Python list, evaluate it, and then write a **macro**: an ordinary function that takes a program as data, returns a different program as data, and hands it back to the evaluator.

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

- `sch_eval` is about twenty lines and needs no parser.  The whole *Recursive Descent Parsing* session exists because most languages do not hand you the tree; Scheme does, which is what the One Syntax Rule buys.
- `quote` is the only form that returns its argument untouched.  Everything else recurses.  That one special case is the door between program and data, in both directions.
- `unless_macro` is an *ordinary function*.  It takes a list, returns a list, and the evaluator never knows a macro was involved.  Compare with adding `unless` to your own interpreter, which would mean a new AST node, a parser change, and an evaluator branch.
- `count_nodes` works on programs for the same reason it would work on any nested list: there is no difference between the two.

> **Watch out!**  Homoiconicity is not "Lisp has `eval`."  Python has `eval` too, and it takes a *string* that must be parsed.  The Scheme property is that the program is already the data structure the evaluator consumes, so transforming code needs no parsing and no printing back to text. That is why Lisp macros compose and string-based code generation does not.

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

Expected output as written: both lines report that the macro has not been written yet, because the unexpanded form has `when` or `double` at the head and the evaluator has never heard of either.  Once your macros return real forms, you should see `70` and `20`.

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

**In-class work stops here.**  Everything below is homework and going-deeper material, attempt the exercises before the related assignment.

## Exercises (Homework: ~95 minutes total)

### Exercise 1: Loop Exorcism (15 min)

Rewrite each using `map`/`filter`/`reduce` with no loops or assignments:
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

Implement `my_map` and `my_reduce` recursively (no `for`/`while`).  Test against the built-ins on 5 inputs each.  Then implement `my_zip(lst1, lst2)` and `my_flatten(nested)` recursively.

### Exercise 4: Purity Refactor (20 min)

Take the impure `f2` and `f3` from Model 1, refactor them to be pure, and write tests that pass for the pure version but fail (or behave unexpectedly) for the impure version.

### Exercise 5: No-Assignment Challenge (25 min)

Compute the average word length of a paragraph using **exactly one expression**, no statements, no intermediate variable names (except the function parameter).  Then discuss: when does point-free style help, and when does it hurt readability?

---

# Extension: Going Further with Scheme

> Past the 75 minutes.  Nothing in class assumes any of it, and none of it is on an assignment unless you take the Scheme direction on the Functional assignment, in which case start here.  The Scheme cells want a Racket REPL; the Python cells run in the page as usual.

## 9.  Recursion Is the Loop

Scheme has no `while`; iteration is recursion, usually on lists, which are built from `cons` cells and dissected with `car` (first element) and `cdr` (the rest):

> **Watch out!** `car` and `cdr` are Scheme's names for what most languages call `head` and `tail` (or `first` and `rest`).  The names are historical accidents from 1950s IBM hardware register names.  When you see `(car lst)` think "give me the first element"; when you see `(cdr lst)` think "give me everything except the first element."  Calling `car` or `cdr` on an empty list `'()` is a runtime error; always check `(null? lst)` first in your base case.

```scheme
(define (sum lst)
  (if (null? lst)
      0
      (+ (car lst) (sum (cdr lst)))))

(sum '(1 2 3 4 5))    ; 15

(define (my-map f lst)
  (if (null? lst)
      '()
      (cons (f (car lst)) (my-map f (cdr lst)))))

(my-map (lambda (x) (* x x)) '(1 2 3))   ; (1 4 9)
```

The base-case-plus-recursive-case shape is the same one your `my_reduce` exercise used, and the same shape as `evaluate` walking an AST: *the* functional pattern.

---

Model 7 is where recursion becomes your only loop.  Every pattern you know from Python `for`-loops (mapping a function over a list, filtering elements, accumulating a sum) can be expressed as a short recursive function that peels one element off the front of a list, does something with it, and recurs on the rest.  Watch how `car` grabs the head and `cdr` returns the tail; those two operations are the entire engine.

## Model 7: Run and Vary

### Critical Thinking Questions

5.  Trace `(sum '(1 2 3))` by hand, writing every call and return.  Where does the addition for `1` actually happen: on the way down or the way back up?
6.  Write `(my-filter pred lst)` following the `my-map` template; predict its output on `(my-filter odd? '(1 2 3 4 5))` and verify.  Which line differs structurally from `my-map`?

> **Watch out!**  Forgetting the quote `'` before a list literal is the single most common Scheme beginner error.  Writing `(1 2 3)` tells Scheme: "call the function named `1` with arguments `2` and `3`."  Since `1` is not a function, you get an error like `application: not a procedure`.  Always write `'(1 2 3)` when you mean a list of data, not a function call.

7.  The quote in `'(1 2 3)` says "data, do not evaluate."  Predict the difference between `(1 2 3)` and `'(1 2 3)` at the prompt; verify; explain the error message in terms of the One Syntax Rule.

In Scheme, the expression `(+ 1 2)` and the quoted form `'(+ 1 2)` differ in that:

[( )] The first is a list and the second is a number
[(X)] The first evaluates to 3, while the second is a three-element list (the unevaluated program itself, as data)
[( )] The second contains a syntax error
[( )] They are identical in every context

---

Model 8 explores one of the most practically important differences between Scheme and Python: what happens when recursion goes very deep.  Scheme guarantees that a tail-recursive function uses no more stack space than a simple loop, so algorithms that are naturally recursive (like traversing a million-element list) are not just elegant but efficient.  Python offers no such guarantee, which is why Python programmers reach for `for`-loops even when recursion would be cleaner.

> **Watch out!** `define` in Scheme is not assignment in the imperative sense.  Writing `(define x 5)` does not create a mutable variable you update later; it introduces a name binding in the current environment.  In functional Scheme style, you do not reassign `x`; instead, you pass updated values forward as function arguments (hence the accumulator pattern in tail recursion).  If you find yourself wanting to write `(set! x (+ x 1))` inside a loop, stop and think about how to express the same idea with a recursive accumulator parameter.

## Model 8: Tail Recursion, Scheme vs Python

**Tail recursion** occurs when a recursive call is the *last* operation in a function: no pending work remains after the call returns.  Scheme (and Racket) *guarantee* tail-call optimization (TCO): a tail-recursive function consumes O(1) stack space.  Python does **not** perform TCO; deep tail calls still overflow the call stack.

The cell below demonstrates both a naive (non-tail) factorial and a tail-recursive accumulator version in Python, counting stack frames to make the difference concrete.

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

Model 9 zooms in on a subtle but important question: when you write several name bindings together, can each one see the others?  The three forms `let`, `let*`, and `letrec` give three different answers to that question.  Understanding the difference matters both for reading Scheme code correctly and for appreciating why Python's `def` and assignment behave the way they do.

## Model 9: let, let*, and letrec

Scheme's **local binding forms** give names to intermediate values.  They differ in *when* bindings become visible:

- `let`: all right-hand sides are evaluated in the **outer** environment; bindings are parallel and independent.
- `let*`: bindings are sequential; each RHS sees **all previous** bindings in the same `let*`.
- `letrec`: all names are in scope for **all** right-hand sides (required for mutually recursive local functions).

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

# Bonus: show that let's parallel evaluation matters
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

Model 10 brings together everything: now that you know how Scheme evaluates expressions and how lists are constructed, you can use Scheme's quasiquoting mechanism to build lists that are *programs*, then hand them to `eval`.  This is homoiconicity made concrete and operational.  The Python simulation in the runnable cell re-implements the same ideas so you can experiment without a Racket installation.

## Model 10: Quasiquoting and List Operations

**Quasiquoting** (`\`` backtick) is a templating mechanism: the entire form is treated as data (like `'`), *except* that subexpressions preceded by `,` (unquote) or `,@` (unquote-splicing) are evaluated.  This is the foundation of Scheme macros and a powerful list-construction tool.

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

## 10.  Writing Real Scheme in a REPL

Everything above simulated Scheme semantics in Python so the cells could run here.  Now write the real thing.  **This section is the in-class hands-on:** open [try.scheme.org](https://try.scheme.org) in a browser tab; it gives you a full Scheme REPL with nothing to install.  (Alternatives: download and run the course archives [SchemeSumList.zip](https://www.billmongan.com/Ursinus-CS374-Fall2026/files/replit/SchemeSumList.zip) and [QuickSortScheme.zip](https://www.billmongan.com/Ursinus-CS374-Fall2026/files/replit/QuickSortScheme.zip).)

Complete the three tasks below in actual Scheme.  Type each definition into the REPL, then run the test calls and check your output against the expected transcript.

**Task 1. `sum-list` by recursion.**  Sum a list of numbers with no loop: the empty list sums to 0; otherwise add the `car` to the sum of the `cdr`.

```scheme
(define (sum-list lst)
  (if (null? lst)
      0
      (+ (car lst) (sum-list (cdr lst)))))
```

Expected transcript:

```text
> (sum-list '(1 2 3 4 5))
15
> (sum-list '())
0
> (sum-list '(10 -10 7))
7
```

**Task 2. `my-map` from `cons`/`car`/`cdr`.**  Rebuild `map` yourself: apply `f` to the `car`, `cons` the result onto the mapped `cdr`.

```scheme
(define (my-map f lst)
  (if (null? lst)
      '()
      (cons (f (car lst)) (my-map f (cdr lst)))))
```

Expected transcript:

```text
> (my-map (lambda (x) (* x x)) '(1 2 3 4))
(1 4 9 16)
> (my-map car '((a 1) (b 2) (c 3)))
(a b c)
> (my-map (lambda (x) (+ x 1)) '())
()
```

**Task 3. a two-branch `cond`.**  Write `classify`, which returns the symbol `negative` for numbers below zero and `non-negative` otherwise, using `cond` with exactly two branches (a test branch and an `else` branch).

```scheme
(define (classify n)
  (cond ((< n 0) 'negative)
        (else    'non-negative)))
```

Expected transcript:

```text
> (classify -3)
negative
> (classify 7)
non-negative
> (classify 0)
non-negative
> (my-map classify '(-2 0 5))
(negative non-negative non-negative)
```

If any output differs from the transcript, read the REPL's error message aloud to your group and fix the definition before moving on; debugging in the REPL *is* the exercise.

---

### Scheme Exercises

1.  *Warmups.*  Define and test: `(double x)`, `(average a b)`, `(my-length lst)` recursively, and `(count-if pred lst)`.
2.  *The translation suite.*  Port your exercises from the *Functional Programming* activity to Scheme: the product of odds (use your `my-filter` plus a recursive `product`), and word-count's shape `(my-reduce + 0 (my-map (lambda (w) 1) ws))`.  Note which felt more natural in which language, honestly.
3.  *Trees, of course.*  Represent your CS374 AST in Scheme as nested lists, like `'(* (+ 2 3) 4)`, and write `(evaluate tree)` for `+ - * /` in fifteen lines.  You have now written your interpreter twice; compare line counts and explain the difference in one sentence.
4.  *Quote experiments.*  Using `car`, `cdr`, and `cons` on `'(define (square x) (* x x))`, extract the function name, the parameter list, and the body.  You are manipulating a program with a program; say so out loud.

---

---

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

**Reflection 1.**  The word "metacircular" implies the evaluator is defined in terms of itself.  Our evaluator is written in Python, not Scheme; so in what sense is it still "metacircular"?  What would it take to port our evaluator from Python into the Scheme subset our evaluator understands, and what would that accomplish?

**Reflection 2.**  The course final project asks you to extend a language interpreter.  Identify **three specific features** from this evaluator (the `Env` chain, `Procedure` as a closure, or TCO via trampoline) that map directly to something you will need in your final project.  For each, write one sentence explaining the connection.

**Reflection 3.**  Our evaluator has no type system: `(+ 1 "hello")` raises a Python `TypeError` that leaks through the abstraction boundary.  Describe at minimum **two changes** you would make to add a static type system to this evaluator.  Consider: where would type annotations appear in the s-expression representation?  Where in `scheme_eval` would you insert a type-checking pass?  What new data structure would represent a type error vs. a value?

---

### Further reading on metacircular evaluation

- **Runnable example archive**: [SchemeInterpreter.zip](https://www.billmongan.com/Ursinus-CS374-Fall2026/files/replit/SchemeInterpreter.zip): a complete reference implementation of this activity's evaluator, worth exploring after you have attempted the activity yourself.

- **SICP Chapter 4**: Abelson & Sussman, *Structure and Interpretation of Computer Programs*, 2nd ed.  The original metacircular evaluator.  MIT Press open access: [https://mitp-content-server.mit.edu/books/content/sectbyfn/books_pubs/6515/sicp.pdf](https://mitp-content-server.mit.edu/books/content/sectbyfn/books_pubs/6515/sicp.pdf)

- **"The Art of the Interpreter"**: Guy Steele & Gerald Sussman (1978).  The foundational paper on meta-circular evaluation, environments, and the relationship between interpreters and compilers.  [MIT AI Memo 452.](https://dspace.mit.edu/handle/1721.1/6094)

- **Norvig's `lis.py`**: Peter Norvig's "How to Write a (Lisp) Interpreter in Python."  Norvig's version is compact and elegant; ours extends it with TCO and a fuller special-form set.  Search for "Norvig lis.py" to find his blog post.

- **R7RS Scheme specification**: The current small Scheme standard.  Section 4 (Expressions) maps directly to our `scheme_eval` dispatch table.  Available at [https://small.r7rs.org/](https://small.r7rs.org/).

- **"Proper Tail Recursion and Space Efficiency"**: Will Clinger (PLDI 1998).  A careful treatment of what tail-call optimization guarantees and how to implement it correctly.

---

## Reflection Prompt

Purity forbids a function from leaving traces on the world: which makes it trustworthy, but also means it *cannot do anything* (no printing, no saving) without breaking the rules.  Real programs must do things.  Where should the impurity live in a well-organized program?  Name a non-programming system (kitchen, lab, organization) organized the same way.

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

Up next: *Language Design Workshop* turns all of this on a language of your own.  Everything here, purity through code as data, is the core of the Functional assignment.
