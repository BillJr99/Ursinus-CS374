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

When you give someone driving directions, you say "turn left on Main, go two blocks, turn right." That is imperative programming — a step-by-step recipe for *how* to get somewhere. Functional programming is like giving the destination instead: you describe *what* you want the data to look like, and let the language figure out how to get there. This shift in thinking is why functional ideas now show up in every modern language — Python, JavaScript, Java, Rust — and why mastering them makes you a dramatically more expressive programmer.

## Learning Goals

By the end of this activity, you will be able to:

- Distinguish pure functions from impure ones and explain why purity enables referential transparency, testability, and safe parallelism
- Apply `map`, `filter`, and `reduce` to transform and aggregate data without explicit loops
- Write higher-order functions that accept and return other functions, including anonymous `lambda` expressions
- Use currying and partial application to build specialized functions from general ones
- Implement recursive solutions to iterative problems without using mutable state or assignment

Unit 3 turns from building languages to inhabiting one paradigm deeply. We practice **functional programming** in Python — `lambda`, `map`, `filter`, `reduce` — with the discipline of **purity** and **immutability**, because the functional toolkit is both a daily professional skill (data pipelines, modern Java/JavaScript/Rust) and the bridge to Scheme and the lambda calculus ahead.

Arc: **purity and why it pays → the big three combinators → higher-order thinking → currying and partial application → recursion without loops**

> **Before You Begin:** This activity assumes you can:
> - Write and call Python functions, including functions that take other functions as arguments
> - Use Python lists and understand that lists are mutable (they can be changed in place)
> - Recognize a `for` loop and describe what it does step by step
>
> If any of these feel shaky, review them first.

---

## Directions and Group Roles

Work in your POGIL team with rotated roles (**Manager**, **Recorder**, **Presenter**, **Reflector**). Consider each model and question individually first, then discuss with your group.

---

## Key Concepts

Before diving in, here is a plain-English glossary of the terms this activity uses. Return to this table whenever a term feels slippery.

| Term | Plain-English meaning | Why it matters |
|------|-----------------------|----------------|
| **Pure function** | Output depends only on inputs; nothing outside the function changes | Pure functions can be tested, cached, substituted, and parallelized fearlessly |
| **Side effect** | Anything a function does besides return a value — mutating, printing, reading globals | Side effects are exactly what purity forbids; spotting them is a skill |
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

Think of purity the way you think about a calculator: press `2 + 3` and you always get `5`, no matter how many times you press it and no matter what else is on your desk. Model 1 gives you six functions and asks you to decide which ones behave like that trustworthy calculator and which ones secretly remember — or change — the world around them. Use what you learned from the opening example above to guide your classification.

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

The next two models focus on the three combinators that replace nearly every explicit loop you have ever written. Before we look at any code, notice that each combinator corresponds to a question you already ask about data: "what does each element look like after a change?", "which elements do I want to keep?", "what single summary value do these elements produce?" You have been answering these questions with `for` loops; now you will answer them with a single function call.

> **Watch out!** Python's `map` and `filter` do not prevent you from passing in an impure function — one that prints, mutates globals, or reads from a file. The combinators themselves are pure, but they will faithfully execute whatever function you hand them. Always make sure the lambda or function you pass in has no side effects, or you lose the guarantees that make functional style valuable.

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

Python gives you two roads to the same destination: the `map`/`filter` combinators you just saw, and *list comprehensions*, which borrow syntax from mathematical set-builder notation. Model 2 puts them side by side so you can see that they produce identical results while looking quite different. Understanding both is practical — you will encounter both in real Python codebases — and comparing them deepens your intuition for what "transforming a collection" really means.

> **Watch out!** Immutability does not mean "constant." In Python, writing `x = 5` creates a variable that you could reassign tomorrow. True immutability in functional programming means that once a data structure is built you never modify it — instead you build a new one. Python's `tuple` is immutable; a `list` is not. When you call `pure_double` above, `original` stays unchanged not because Python enforces it, but because the function was *written* to build a new list. Nothing stops you from writing an impure version — discipline and code review do.

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

Before moving on to higher-order functions, pause and run one pipeline entirely *by hand*. If you can produce every intermediate list on paper, `map`/`filter`/`reduce` stop being magic incantations and become bookkeeping you happen not to write yourself.

## Model 3: Tracing a Map–Filter–Reduce Pipeline by Hand

**Worked example.** Trace the scores pipeline from Section 2, one stage at a time:

```
scores    [88, 92, 54, 71, 67, 95, 49, 83]
   |  map: s -> min(s + 5, 100)          (curve, capped at 100)
curved    [93, 97, 59, 76, 72, 100, 54, 88]
   |  filter: s >= 70                    (keep passing scores)
passing   [93, 97, 76, 72, 100, 88]
   |  reduce: (acc, s) -> acc + s, seed 0
total     526                            mean = 526 / 6 = 87.7
```

The same computation element by element — note how the two failing scores are *transformed* by `map` but *discarded* by `filter`, so they never reach `reduce`:

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

```python  liascript
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
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

[[MC]]
In the pipeline trace, the score 54 becomes 59 after the map stage and then vanishes. Which statement is accurate?
- ( ) `map` removed it because it was below 70
- (x) `map` transformed it (54 → 59) and `filter` discarded it because 59 < 70
- ( ) `reduce` skipped it while folding
- ( ) It was removed before the map stage ran

**Critical Thinking Questions (CTQs)**

> **CTQ 3.1** Recompute the running-total column yourself to confirm 526. Which two original scores never reach `reduce`, and which stage eliminated each one?

> **CTQ 3.2** The stage diagram materializes two whole intermediate lists (`curved`, `passing`) because the code calls `list(...)`. In the one-expression pipeline from Section 2 (no `list` calls), do those intermediate lists ever exist in memory? Connect your answer to the laziness you observed in CTQ 2.5.

> **CTQ 3.3** The running-total column is exactly the accumulator variable from an imperative loop — yet nothing here is mutated. Where does the "updated" accumulator live on each fold step instead? And is `reduce` with `traced_add` still pure? (Careful: `traced_add` prints.)

---

# Part III: Higher-Order Functions

You have already passed functions as arguments — every time you called `map(lambda x: x*2, data)` you handed a function to another function. Part III asks: what if a function could also *return* a new function? Think of it like a factory: instead of building one widget, the factory builds a machine that builds widgets. `make_adder(5)` is that factory — call it once and you get back a custom addition function, ready to use anywhere.

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

A composed pipeline like `clean` reads as a single gesture, but the machine executes it one function at a time. Tracing a composition call by call — writing down each intermediate value — is the fastest way to convince yourself that data really does flow left to right through `pipeline`, and right to left through `compose`.

## Model 4: Composition, Traced One Call at a Time

**Worked example.** Trace `clean("  Hello World  ")` where `clean = pipeline(str.strip, str.lower, lambda s: s.replace(' ', '_'))`. Since `pipeline` folds with `lambda v, f: f(v)`, the string threads through the functions in order:

| Step | Function applied | Input value | Output value |
|------|------------------|-------------|--------------|
| start | — | `"  Hello World  "` | — |
| 1 | `str.strip` | `"  Hello World  "` | `"Hello World"` |
| 2 | `str.lower` | `"Hello World"` | `"hello world"` |
| 3 | `s.replace(' ', '_')` | `"hello world"` | `"hello_world"` |

As a flow diagram — and contrast with `compose`, which runs right to left:

```
pipeline:  x --> [strip] --> [lower] --> [replace ' '->'_'] --> "hello_world"
compose:   compose(f, g)(x) = f(g(x))    -- g runs FIRST, then f
```

The cell below wraps each stage so it narrates itself, then swaps the first and last stages to show that composition order is part of the meaning:

```python  liascript
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
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

Notice that `traced` is itself a higher-order function: it consumes a function and returns a new one with the same behavior plus narration — the same shape as `twice` and `compose`.

[[MC]]
`compose(f, g)` returns `lambda x: f(g(x))`. Evaluating `compose(str.lower, str.strip)("  ABC  ")` therefore:
- ( ) Applies `lower` first, then `strip`
- (x) Applies `strip` first (it is innermost), then `lower`
- ( ) Applies both simultaneously
- ( ) Raises an error because strings are immutable

**Critical Thinking Questions (CTQs)**

> **CTQ 4.1** Each stage's output becomes the next stage's input. What requirement connects the *return type* of one stage to the *parameter type* of the next? The swapped `messy` pipeline still ran without error — did it satisfy your requirement, and is "runs without error" the same as "correct"?

> **CTQ 4.2** Unroll `pipeline(f, g, h)(x)` by hand using the left-fold formula from CTQ 2.2 to show it computes `h(g(f(x)))`. Then unroll `compose(f, g)(x)`. Which order do you find easier to read, and why might data-pipeline libraries prefer left-to-right?

> **CTQ 4.3** `pipeline` is implemented with `reduce` — but folding over a list of *functions* rather than numbers. In the trace table, what plays the role of the accumulator, and what is its value after step 2?

---

If higher-order functions are factories, then currying and partial application are factory *customizations*. Imagine a general `power(base, exp)` function. Partial application lets you say "I always want `exp=2` — give me a `square` function." Currying takes this further: it restructures any multi-argument function so you can supply arguments one at a time, producing a chain of single-argument functions. This style shows up everywhere in functional languages like Haskell, and understanding it will make the lambda calculus we study later feel natural.

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

> **CTQ 4.4** `map_with(lambda x: x * 2)` returns a function. How is this different from `map(lambda x: x * 2, data)`? When is the list transformer version more useful?

> **CTQ 4.5** Haskell functions are automatically curried — `f x y` is always `(f x) y`. What advantage does automatic currying give you for composing functions?

---

# Part IV: Recursion Without Loops

In Python you have used `for` loops to walk through lists. But a `for` loop requires mutable state: a counter variable that changes on every iteration. Pure functional programming avoids mutable state entirely, so loops are off the table. The replacement is recursion: a function that solves a big problem by calling itself on a smaller piece of that problem. Model 5 shows you that `map`, `filter`, and `reduce` — which you already know — can themselves be written as recursive functions, making their structure visible and precise.

> **Watch out!** When students first encounter "no loops allowed," a common instinct is to reach for a `while True` loop with a counter. That is still a loop! Pure functional recursion means the function calls itself with a *smaller* argument — there is no loop variable, no `i += 1`, and no mutation of any list. If you find yourself writing an assignment statement inside a recursive function, pause and reconsider.

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

Model 6 pushes recursion in two new directions: *mutual* recursion (two functions that call each other) and *structural* recursion (recursing along the shape of nested data, not a numeric counter). You will also see a fully functional merge sort — no mutation anywhere. Before diving in, study the worked example below that shows how to translate an imperative loop into a functional composition step by step.

**Worked Example: Imperative → Functional**

Suppose you have this imperative code that sums the squares of all even numbers in a list:

```python
# Imperative version — 5 statements, 2 mutation points
result = 0
for x in nums:
    if x % 2 == 0:
        result += x ** 2
```

Here is how to transform it step by step into a functional composition:

**Step 1 — Identify the three loop concerns separately:**
- *Filter*: keep only even numbers → `x % 2 == 0`
- *Transform*: square each kept number → `x ** 2`
- *Aggregate*: sum the results → `+`

**Step 2 — Write each concern as a lambda:**
```python
is_even  = lambda x: x % 2 == 0
square   = lambda x: x ** 2
add      = lambda a, b: a + b
```

**Step 3 — Assemble with `filter`, `map`, `reduce`:**
```python
from functools import reduce
result = reduce(add, map(square, filter(is_even, nums)), 0)
```

**Step 4 — Inline the lambdas for a one-liner (optional):**
```python
result = reduce(lambda a, b: a + b,
                map(lambda x: x**2,
                    filter(lambda x: x % 2 == 0, nums)), 0)
```

The result is identical to the loop. The difference: the functional version has **no mutation** (`result` is never reassigned), **no loop variable**, and each concern is a named, testable piece.

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
