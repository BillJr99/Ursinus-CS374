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

## Going Deeper: Continuation-Passing Style: Control Flow as First-Class Values

#### Learning Goals

By the end of this activity, you will be able to:

- Mechanically transform a direct-style function into continuation-passing style (CPS), making every return explicit as a call to a continuation `k`
- Explain why CPS converts every call into a tail call and why tail calls do not grow the stack
- Implement a trampoline that executes a CPS computation in O(1) stack space using an iterative loop
- Identify the continuation at each point in a computation and describe what "the rest of the program" means at that point
- Recognize CPS as the common underlying mechanism behind tail-call optimization, exceptions, generators, async/await, and `call/cc`

Continuation-Passing Style (CPS) transforms "what to do next" into an explicit first-class value called a **continuation** — a function representing the rest of the computation. Every function in CPS takes an extra argument `k` — the continuation — and instead of returning a value to its caller, it calls `k` with that result directly. This single idea unifies tail-call optimization, exceptions, async/await, generators, coroutines, and `call/cc` under one conceptual roof, revealing that these features, which appear very different on the surface, are all variations of the same underlying mechanism: the explicit manipulation of control flow as data.

---

> **Before You Begin — Prerequisites**
>
> This activity assumes you are comfortable with **closures** (functions that capture variables from their enclosing scope) and **higher-order functions** (functions that accept or return other functions). If either of those concepts feels shaky, review the [Closures activity](../closures/) before continuing. In CPS, nearly every step involves passing a function as an argument and calling it inside another function — closures are not optional background material here, they are the core mechanism.

---

#### Why This Matters: The Stack Overflow Problem

Python's call stack has a limit of roughly 1,000 frames by default. That limit exists because the interpreter stores each active function call on a fixed-size stack in memory. Try summing a list of 10,000 elements with naive recursion and Python will stop you:

```python  liascript
import sys, traceback

def sum_list(lst):
    if len(lst) == 0:
        return 0
    return lst[0] + sum_list(lst[1:])   # non-tail call: pending addition after return

# Try with a small list first (works fine)
print("sum_list([1,2,3,4,5]) =", sum_list([1, 2, 3, 4, 5]))

# Now try 2000 elements — likely hits the recursion limit
try:
    result = sum_list(list(range(2000)))
    print("sum_list(range(2000)) =", result, "(succeeded — your limit is higher than default)")
except RecursionError as e:
    print("RecursionError with 2000 elements:", e)
    print("(Python's default recursion limit is", sys.getrecursionlimit(), "frames)")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

The problem is not the recursion itself — it is the **pending work** that accumulates on the stack. Each call to `sum_list` cannot return until its recursive call returns, because the addition `lst[0] + (...)` is still waiting. Python keeps every one of those frames alive simultaneously.

CPS transforms this so that every call becomes a **tail call** — no pending work remains on the stack after the call. Once every call is a tail call, a technique called **trampolining** can run the computation inside a simple `while` loop, using O(1) stack space regardless of list size. You will build all of this from scratch in this activity.

---

#### Notation Bridge: Direct Style to CPS

Before diving in, here is a quick translation table. The left column shows familiar direct-style code; the right column shows its CPS equivalent. The key pattern is: wherever direct style *returns* a value, CPS *calls the continuation* `k` with that value instead.

| Direct Style | CPS Style | What changed |
|---|---|---|
| `return x` | `k(x)` | "return" becomes "call `k` with" |
| `f(x)` | `f_k(x, k)` | every function gains an extra `k` argument |
| `y = f(x); g(y)` | `f_k(x, lambda y: g_k(y, k))` | sequencing becomes nested lambdas |
| `if b: e1 else: e2` | `(lambda: k(e1))() if b else (lambda: k(e2))()` | both branches call `k` |
| `return f(g(x))` | `g_k(x, lambda v: f_k(v, k))` | inner call names its result, outer call uses it |

The notation `f_k` is a naming convention meaning "CPS version of `f`." Some authors write `f_cps` instead. Both mean the same thing: a version of `f` that takes an extra continuation argument and calls it with the result instead of returning.

---

#### Step-by-Step CPS Transformation of Factorial

Here is how to mechanically transform `factorial` from direct style to CPS. Read through each step before running any code — the goal is to understand the algorithm before you see it execute.

**Original direct style:**

```
def factorial(n):
    if n == 0:
        return 1           # base case: returns 1
    else:
        return n * factorial(n - 1)   # non-tail: pending multiplication
```

**Step 1 — Add the continuation parameter `k`.**
Every CPS function accepts `k` as its last argument.

```
def factorial_k(n, k):
    if n == 0:
        ...
    else:
        ...
```

**Step 2 — Replace `return value` with `k(value)` in the base case.**
There is no pending work after the base case, so we just hand the result to `k`.

```
def factorial_k(n, k):
    if n == 0:
        k(1)               # was: return 1
    else:
        ...
```

**Step 3 — Handle the recursive case.**
In direct style: `return n * factorial(n-1)`.
The pending work is the multiplication `n * (...)`. We must capture that as a closure.

- The recursive call becomes `factorial_k(n-1, ...)`.
- The "..." is a lambda that receives the result of `factorial(n-1)`, multiplies by `n`, and passes the product to the *outer* `k`.
- Written out: `factorial_k(n-1, lambda result: k(n * result))`

```
def factorial_k(n, k):
    if n == 0:
        k(1)                                         # base: call k with 1
    else:
        factorial_k(n - 1, lambda result: k(n * result))  # recursive tail call
```

**Why this is now tail-recursive:**
After the `else` branch executes `factorial_k(n-1, ...)`, there is nothing left for the current call to do. The multiplication `n * result` will happen *inside* the lambda, which is called later. The current stack frame can be discarded immediately. The pending work moved from the stack to the heap (the closure).

> **Watch out! — Closures and variable capture**
>
> In the lambda `lambda result: k(n * result)`, the variable `n` is captured from the enclosing scope. In Python, this works correctly here because `n` is a function parameter — each call to `factorial_k` creates a new `n` binding. Lambda parameters (like `result`) also create new bindings. The danger arises with **loop variables**: if you wrote `for n in range(5): lambdas.append(lambda: n)`, all lambdas would capture the same `n` and all would print `4`. When writing CPS by hand inside loops, use a default argument trick (`lambda result, _n=n: _n * result`) to freeze the value at creation time, as you will see in the trampoline code later.

> **Watch out! — What the continuation `k` represents**
>
> The continuation `k` is "the rest of the computation." When `factorial_k(5, k)` is called, `k` is a function that knows what to do with the answer `120` once it arrives — perhaps print it, perhaps multiply it by something else, perhaps store it. Every function in CPS takes `k` and calls it with its result instead of returning. This means the result never travels back up the call stack; it always travels *forward* through the continuation chain.

---

#### Directions and Group Roles

**This is a POGIL activity.** Work in groups of three or four. Assign the following roles before you begin, and rotate roles with each new Part.

| Role | Responsibility |
|------|---------------|
| **Manager** | Keeps the group on task and on time; ensures everyone contributes; escalates to the instructor when the group is stuck for more than two minutes |
| **Recorder** | Writes down the group's agreed answers; ensures the written responses are complete and legible |
| **Presenter** | Speaks for the group during class discussion; prepares to explain the group's reasoning, not just the answer |
| **Reflector** | Monitors group process; notes what strategies are working or not; leads the end-of-part reflection check-in |

> **Ground rule:** No one moves on until the Recorder has written down an answer that every member can explain independently. If one person is confused, the group is not done.

---

#### Part I: Direct Style vs. CPS

##### Model 1: Two Ways to Write Factorial

Consider the factorial function written two different ways. Read both carefully before answering the questions below.

**Direct Style** — the familiar recursive version:

```python  liascript
def fact_direct(n):
    if n == 0:
        return 1
    else:
        return n * fact_direct(n - 1)

# Call it:
# fact_direct(5) => 120
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

**CPS Style** — every function takes an extra argument `k` (the continuation):

```python  liascript
def fact_cps(n, k):
    if n == 0:
        k(1)
    else:
        fact_cps(n - 1, lambda result: k(n * result))

# Call it with the identity continuation:
# fact_cps(5, lambda x: x)  => 120 (returned from identity)
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

**Key insight:** In the direct style, the Python call stack implicitly records "we still need to multiply by `n` after the recursive call returns." In the CPS version, that pending work is made *explicit* as a closure: `lambda result: k(n * result)`. The continuation **is** the stack frame. When there are no more stack frames to push because all pending work lives in closures, every call is a tail call.

##### Runnable Model: Comparing Both Versions

Run the cell below to see both versions produce the same output.

```python  liascript
import sys
import traceback

try:
    # ── Direct Style ──────────────────────────────────────────────
    def fact_direct(n):
        if n == 0:
            return 1
        else:
            return n * fact_direct(n - 1)

    # ── CPS Style ────────────────────────────────────────────────
    def fact_cps(n, k):
        if n == 0:
            k(1)
        else:
            fact_cps(n - 1, lambda result: k(n * result))

    # Identity continuation: just return the value as-is
    identity = lambda x: x

    # We capture the result by storing it in a mutable container
    # because Python lambdas cannot assign to outer variables directly.
    result_box = [None]
    def capture(x):
        result_box[0] = x

    print("Direct style:  fact_direct(6) =", fact_direct(6))

    fact_cps(6, capture)
    print("CPS style:     fact_cps(6, capture) =>", result_box[0])

    # Trace the first few steps manually
    print()
    print("Tracing fact_cps(3, print):")
    print("  Each step shows what k is called with:")
    fact_cps(3, lambda x: print("  Final k receives:", x))

except Exception as e:
    print("[cps:factorial] Error:", e)
    traceback.print_exc()
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

##### Critical Thinking Questions — Part I

**CTQ 1.1** In `fact_cps`, look at the two branches:

- Branch `n == 0`: calls `k(1)`
- Branch `n > 0`: calls `fact_cps(n - 1, lambda result: k(n * result))`

Which expression in *each* branch is in **tail position** (i.e., is the very last thing the function does before it "returns")?

[[___]]
<script>true</script>

> In the `n == 0` branch, the tail call is `k(1)`. In the `n > 0` branch, the tail call is `fact_cps(n - 1, ...)`. Crucially, **every** branch ends with exactly one tail call — there is no pending work after either recursive call. The pending multiplication has been absorbed into the new continuation closure.

---

**CTQ 1.2** The **identity continuation** is `lambda x: x`. When you call `fact_cps(5, lambda x: x)`, what does this continuation *do* with the final result? What is its role in the computation?

[[___]]
<script>true</script>

> The identity continuation simply returns its argument unchanged. It plays the role of "the top-level program that receives the final answer." In a full CPS-transformed program, the outermost call is always supplied with the identity (or a print/store continuation) because there is nothing left to do after the last result is produced.

---

**CTQ 1.3** Trace `fact_cps(3, lambda x: x)` step by step. At each step, write down:
(a) the value of `n`,
(b) the current continuation `k` (describe it as a closure, e.g., `lambda result: outer_k(3 * result)`),
(c) what call is made next.

[[___]]
<script>true</script>

> **Step 1:** `n=3`, `k = identity`. Since `n != 0`, call `fact_cps(2, lambda r: identity(3 * r))`.
>
> **Step 2:** `n=2`, `k = lambda r: identity(3*r)`. Call `fact_cps(1, lambda r: k_prev(2 * r))`.
>
> **Step 3:** `n=1`, `k = lambda r: k_prev(2*r)`. Call `fact_cps(0, lambda r: k_prev2(1*r))`.
>
> **Step 4:** `n=0`. Call `k(1)`. The chain unwinds: `1*1=1`, then `2*1=2`, then `3*2=6`. The identity continuation receives `6`.
>
> Notice how the chain of closures perfectly mirrors the chain of stack frames in the direct version — but the closures live on the heap, not the stack.

---

**CTQ 1.4** Direct-style `fact_direct` is *not* tail-recursive: after the recursive call, there is still a multiplication to do. Yet `fact_cps` **is** tail-recursive. Explain precisely how the CPS transform converts the non-tail recursive direct version into a tail-recursive CPS version. What happened to the pending multiplication?

[[___]]
<script>true</script>

> In `fact_direct`, the pending work `n * (...)` is stored implicitly on the call stack. The CPS transform takes that pending work and packages it into a new closure — the new continuation — which is passed *down* into the recursive call. The recursive call now has nothing left to do after it completes (because it never returns — it calls its continuation instead), so it is trivially in tail position. The multiplication did not disappear; it moved from the stack to the heap, encoded inside a closure. This is why CPS enables tail-call optimization even for functions that were originally non-tail-recursive: the transform relocates all pending work into explicit data structures.

---

#### Part II: The CPS Transform Algorithm

##### Model 2: The Mechanical CPS Transform

CPS transformation is a *systematic* algorithm. The core rule is:

> **For every subexpression, give it a name, then pass that name to a fresh continuation.**

Consider transforming `f(g(x)) + h(y)` from direct style to CPS. We want a function `transform(k)` that, when called, eventually calls `k` with the result of the whole expression.

**Step-by-step CPS transform of `f(g(x)) + h(y)`:**

```
Direct:     f(g(x)) + h(y)

Step 1: g(x) is the innermost call. Name its result v1.
        g_cps(x, lambda v1: ...)

Step 2: Apply f to v1. Name its result v2.
        g_cps(x, lambda v1:
            f_cps(v1, lambda v2: ...))

Step 3: h(y) is independent. Name its result v3.
        g_cps(x, lambda v1:
            f_cps(v1, lambda v2:
                h_cps(y, lambda v3: ...)))

Step 4: Add v2 and v3. Pass to original continuation k.
        g_cps(x, lambda v1:
            f_cps(v1, lambda v2:
                h_cps(y, lambda v3:
                    k(v2 + v3))))
```

Notice the **inside-out** structure: the outermost operation (`+`) ends up deepest in the nesting. The nesting order in CPS is the *reverse* of the evaluation order in direct style. This is because continuations represent "the future," and the most distant future is the outermost continuation.

##### Model 3: CPS Fibonacci

Here is Fibonacci in direct style and in CPS. The CPS version uses a single continuation that accumulates the final sum.

```python  liascript
import sys
import traceback

try:
    # Direct style Fibonacci
    def fib_direct(n):
        if n <= 1:
            return n
        return fib_direct(n - 1) + fib_direct(n - 2)

    # CPS Fibonacci
    # fib_cps(n, k) eventually calls k(fib(n))
    def fib_cps(n, k):
        if n <= 1:
            k(n)
        else:
            # First compute fib(n-1), then inside that continuation
            # compute fib(n-2), then add them and pass to k
            fib_cps(n - 1, lambda v1:
                fib_cps(n - 2, lambda v2:
                    k(v1 + v2)))

    result_box = [None]
    def capture(x):
        result_box[0] = x

    print("Direct fib(8) =", fib_direct(8))

    sys.setrecursionlimit(5000)
    fib_cps(8, capture)
    print("CPS    fib(8) =", result_box[0])

    # Show the inside-out structure for fib(3)
    print()
    print("fib_cps(3, print) traces:")
    fib_cps(3, lambda x: print("  k receives:", x))

except RecursionError as e:
    print("[cps:fibonacci] RecursionError:", e)
    print("  (Try a smaller n, or see Part V on trampolining)")
except Exception as e:
    print("[cps:fibonacci] Error:", e)
    traceback.print_exc()
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

##### Multiple Choice: CPS Form for `add(mul(2, 3), 4)`

Which of the following is the **correct** CPS form for `add(mul(2, 3), 4)`?

Assume `mul_cps(a, b, k)` and `add_cps(a, b, k)` are the CPS versions of multiply and add.

[( )] `add_cps(mul_cps(2, 3, identity), 4, k)`
[(X)] `mul_cps(2, 3, lambda v: add_cps(v, 4, k))`
[( )] `k(add_cps(mul_cps(2, 3, k), 4, k))`
[( )] `mul_cps(2, 3, k); add_cps(result, 4, k)`

> **Correct: option B.** The multiplication happens first (innermost subexpression). Its result `v` is passed to a continuation that performs the addition, and the addition's result is passed to the original continuation `k`. Option A incorrectly calls `mul_cps` and expects it to *return* a value (direct style thinking). Options C and D mix direct and CPS style.

##### Critical Thinking Questions — Part II

**CTQ 2.1** The claim is: "Every CPS function ends with exactly one tail call." Verify this for both branches of `fib_cps`:

- In the `n <= 1` branch, what is the single tail call?
- In the `n > 0` branch, identify each tail call as you read through the nesting.

[[___]]
<script>true</script>

> In the `n <= 1` branch: `k(n)` is the single tail call — the function does nothing after calling `k`.
>
> In the `n > 0` branch: the function's own tail call is `fib_cps(n-1, ...)`. Inside the lambda passed as its continuation, the tail call is `fib_cps(n-2, ...)`. Inside *that* lambda, the tail call is `k(v1 + v2)`. Every lambda in the chain ends with exactly one tail call — this is the defining structural property of CPS.

---

**CTQ 2.2** Consider the conditional expression `if a then b else c`. Write its CPS transform. Both branches should call the continuation `k`.

[[___]]
<script>true</script>

> ```
> def cond_cps(a, b_cps, c_cps, k):
>     if a:
>         b_cps(k)   # b_cps takes a continuation and calls it with b's result
>     else:
>         c_cps(k)   # c_cps takes a continuation and calls it with c's result
> ```
>
> The key point: both branches call `k` with their result. There is no "join point" after the conditional in CPS — both paths pass control forward through the same continuation. This makes conditional expressions structurally identical to function calls in CPS.

---

**CTQ 2.3** The CPS transform claims to remove *all* non-tail calls from a program. Explain in your own words why this is true. (Hint: Where does the pending work go?)

[[___]]
<script>true</script>

> Every non-tail call has pending work that needs to happen after the call returns. The CPS transform captures that pending work as a closure (the new continuation) and passes it as an argument to the called function. The called function's only job at its leaf is to call that continuation. Because all pending work is now in closures (heap-allocated data), no pending work remains on the call stack. Every call in the resulting CPS code is therefore a tail call — there is nothing left to do after any call completes, because "what to do next" has already been handed off as a data value.

---

**CTQ 2.4** Suppose you implement a CPS interpreter in Python that uses Python's own call stack to evaluate the CPS chain (i.e., Python evaluates each closure call by pushing a new stack frame). What specific risk does this create, and what is the standard solution? (This problem is the subject of Part V.)

[[___]]
<script>true</script>

> Even though every call in the CPS code is a tail call *logically*, Python does not optimize tail calls — it pushes a new stack frame for every function call regardless. A deep chain of CPS continuations therefore creates a deep Python call stack and will eventually raise `RecursionError`. The standard solution is **trampolining**: instead of calling each continuation directly, wrap it in a `Thunk` (a zero-argument lambda or object). A top-level loop (the trampoline) then repeatedly calls the thunk, unwrapping one step at a time. This replaces the implicit call stack with an explicit loop, using O(1) stack space regardless of program depth.

---

#### Part III: Exceptions as Continuations

##### Model 4: Two-Continuation Style

Ordinary CPS uses one continuation `k` representing "what to do on success." We can model exceptions by adding a *second* continuation `h` (the **handler** or escape continuation) representing "what to do on error."

Every function takes both continuations and chooses which one to invoke:

```
def f_cps(args, k, h):
    if error_condition:
        h(error_value)   # escape: jump to the handler
    else:
        k(result)        # normal: pass result forward
```

The `try/except` construct in direct style corresponds to:

- Setting up a new handler `h` that wraps the except-block
- Passing that `h` through the entire continuation chain inside the try-block
- Any function anywhere in the chain can call `h` directly, bypassing all intermediate `k` continuations

##### Runnable Model: CPS Division with Error Handler

```python  liascript
import traceback

try:
    # safe_div_cps(a, b, k, h):
    #   - calls k(a/b) on success
    #   - calls h("division by zero") on error
    def safe_div_cps(a, b, k, h):
        if b == 0:
            h("division by zero: {} / {}".format(a, b))
        else:
            k(a / b)

    # A computation: compute (10 / x) + (6 / y)
    # In CPS with error handling, both divisions share the same handler h
    def compute_cps(x, y, k, h):
        safe_div_cps(10, x, lambda v1:
            safe_div_cps(6, y, lambda v2:
                k(v1 + v2),
            h),
        h)

    # Success handler: just print
    def on_success(result):
        print("  Result:", result)

    # Error handler: print a message
    def on_error(msg):
        print("  Error caught by handler:", msg)

    print("compute_cps(2, 3, ...):")
    compute_cps(2, 3, on_success, on_error)

    print("compute_cps(0, 3, ...):")
    compute_cps(0, 3, on_success, on_error)

    print("compute_cps(2, 0, ...):")
    compute_cps(2, 0, on_success, on_error)

    # Nested handlers: inner try/except in CPS
    print()
    print("Nested handler demo (inner catches, outer does not see the error):")
    def inner_on_error(msg):
        print("  Inner handler caught:", msg)
        # Recover by calling the outer success continuation with a default
        on_success(-999.0)

    compute_cps(5, 0, on_success, inner_on_error)

except Exception as e:
    print("[cps:exceptions] Error:", e)
    traceback.print_exc()
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

##### Critical Thinking Questions — Part III

**CTQ 3.1** When `safe_div_cps(10, 0, k, h)` calls `h("division by zero")`, what happens to the continuation `k`? Does `k` ever get called? Trace the control flow through `compute_cps(2, 0, on_success, on_error)` to explain where control goes.

[[___]]
<script>true</script>

> When `h` is called, `k` is completely bypassed — it is never called. In `compute_cps(2, 0, ...)`:
> 1. `safe_div_cps(10, 2, lambda v1: ..., h)` succeeds, so it calls `lambda v1: ...` with `v1 = 5.0`.
> 2. Inside that continuation, `safe_div_cps(6, 0, lambda v2: k(v1+v2), h)` is called. Since `y=0`, it calls `h("division by zero: 6 / 0")`.
> 3. `h` is `on_error`, which prints the message. The continuation `lambda v2: k(v1+v2)` is never called.
>
> The handler `h` acts as a "side exit" from the continuation chain. Normal flow threads through the `k` chain; exceptional flow jumps directly to `h`, discarding all intermediate continuations.

---

**CTQ 3.2** In direct-style Python, `raise` can "jump over" multiple stack frames at once — an exception thrown inside a deeply nested helper reaches a `try/except` many levels up without executing any of the intermediate code. Explain why this same behavior emerges naturally in the two-continuation CPS model. Where is the "distance to the handler" encoded?

[[___]]
<script>true</script>

> In the two-continuation model, the handler `h` is not stored in any stack frame — it is passed as a *data argument* through the entire continuation chain. Every function in the chain receives `h` and must explicitly pass it further down. When any function calls `h(error)`, it invokes that function directly, bypassing the entire chain of `k` continuations that are waiting. The "distance to the handler" is not encoded anywhere — from `h`'s perspective, there is no distance at all. It is just a function that gets called. The intermediate `k` closures are simply never invoked, and since no one holds a reference that forces their evaluation, they become garbage. This is exactly what "jumping over stack frames" means: in CPS, the stack frames are just closures, and you can skip them by holding a direct reference to a far-away continuation.

---

**CTQ 3.3** A `finally` clause must execute whether or not an exception occurs. Design a two-continuation scheme to implement `finally`. How many continuations do you need? What does each one do?

[[___]]
<script>true</script>

> You still need two continuations, but you wrap *both* of them to first execute the finally-block:
>
> ```python
> def try_finally_cps(body_cps, finally_cps, k, h):
>     # k_with_finally: on success, run finally, then k
>     def k_with_finally(result):
>         finally_cps(lambda _: k(result), h)
>
>     # h_with_finally: on error, run finally, then re-raise via h
>     def h_with_finally(err):
>         finally_cps(lambda _: h(err), h)
>
>     body_cps(k_with_finally, h_with_finally)
> ```
>
> Both `k` and `h` are wrapped so that the finally-block runs before control passes on. The finally-block itself is CPS-transformed and takes its own continuation — this is how even cleanup code participates in the CPS chain without breaking the model.

---

#### Part IV: Async/Await as CPS in Disguise

##### Model 5: Callbacks, Generators, and Async

Consider how Python (and Node.js) approaches asynchronous I/O. In callback style:

```python  liascript
def fetch_user(user_id, on_done):
    # ... eventually calls on_done(user_data)
    pass

def fetch_posts(user, on_done):
    # ... eventually calls on_done(posts)
    pass

# Callback-style usage:
fetch_user(42, lambda user:
    fetch_posts(user, lambda posts:
        print("Got posts:", posts)))
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

This **is** CPS. `on_done` is the continuation. Nesting callbacks is manually writing the CPS transform.

Now compare `async/await`:

```python  liascript
async def get_user_posts():
    user = await fetch_user(42)     # fetch_user_cps(42, lambda user: ...)
    posts = await fetch_posts(user)  # fetch_posts_cps(user, lambda posts: ...)
    print("Got posts:", posts)
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

The `await` keyword *is* the continuation application. The compiler desugars `x = await expr; body` into `expr_cps(lambda x: body_cps(...))`. Python generates a state machine (a `coroutine` object) that is exactly a heap-allocated continuation.

Similarly, Python **generators** are "stackless coroutines" — they capture the continuation at the `yield` point:

```python  liascript
def my_gen():
    yield 1        # "call my caller's continuation with 1, then wait"
    yield 2        # "call my caller's continuation with 2, then wait"
    yield 3        # "call my caller's continuation with 3, then wait"
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

Each `yield` is a `k(value)` call where `k` is "send the value to whoever is iterating over me, then resume when they call next()."

##### Runnable Model: Manual CPS Simulation of a Simple Event Loop

```python  liascript
import traceback
from collections import deque

try:
    # A minimal "event loop" driven by CPS callbacks.
    # Tasks are (function, args) pairs enqueued for later execution.
    event_queue = deque()

    def schedule(fn, *args):
        """Schedule fn(*args) to run on the next event loop tick."""
        event_queue.append((fn, args))

    def run_loop():
        """Run until there are no more scheduled tasks."""
        while event_queue:
            fn, args = event_queue.popleft()
            fn(*args)

    # Simulated async operations using CPS + scheduling
    def async_add(a, b, k):
        """Asynchronously add a+b, then call k with the result."""
        def _work():
            result = a + b
            k(result)
        schedule(_work)

    def async_mul(a, b, k):
        """Asynchronously multiply a*b, then call k with the result."""
        def _work():
            result = a * b
            k(result)
        schedule(_work)

    # Manual CPS async program:
    # Compute (2 + 3) * 4 using async operations
    print("Starting async computation: (2 + 3) * 4")

    def start():
        async_add(2, 3, lambda sum_result:
            async_mul(sum_result, 4, lambda product:
                print("  Async result: (2+3)*4 =", product)))

    schedule(start)
    run_loop()

    # Compare to: synchronous CPS chain
    print()
    print("Same computation in synchronous CPS:")
    result_box = [None]

    def add_cps(a, b, k):
        k(a + b)

    def mul_cps(a, b, k):
        k(a * b)

    add_cps(2, 3, lambda s: mul_cps(s, 4, lambda p: result_box.__setitem__(0, p)))
    print("  Sync CPS result:", result_box[0])

    # Python generator as a resumable continuation
    print()
    print("Generator as resumable continuation:")

    def counting_gen():
        print("  [gen] about to yield 1")
        yield 1
        print("  [gen] resumed after 1, about to yield 2")
        yield 2
        print("  [gen] resumed after 2, about to yield 3")
        yield 3
        print("  [gen] done")

    g = counting_gen()
    for val in g:
        print("  [caller] received:", val)

except Exception as e:
    print("[cps:async] Error:", e)
    traceback.print_exc()
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

##### Critical Thinking Questions — Part IV

**CTQ 4.1** When a Python generator executes `yield value`, what does it "capture" at that moment? Describe in terms of continuations: what is the continuation of a `yield` expression, and who holds it?

[[___]]
<script>true</script>

> When a generator yields, Python captures the **entire execution state** of the generator function: the program counter (where to resume), all local variables, and the value stack at that point. This captured state is exactly a **continuation** — it is "the rest of the generator's computation, waiting for the next `next()` call." The generator object itself holds this continuation. The caller's loop (or `for` statement) holds the reference to the generator object. When the caller calls `next(g)`, it is applying that stored continuation, resuming the generator from where it left off. `yield value` is therefore `k_caller(value)` where `k_caller` is the continuation of whoever is iterating.

---

**CTQ 4.2** Callback-based APIs in Node.js (and early Python async code) require deeply nested callbacks for sequential asynchronous operations — a phenomenon called "callback hell." Explain precisely why this nesting arises in terms of CPS. What does the nesting structure *encode*?

[[___]]
<script>true</script>

> Callback hell arises because sequential operations in CPS have **lexically nested continuations**. If operation B must happen after operation A, then B's code must appear inside A's callback. If C must happen after B, C's code must appear inside B's callback (which is inside A's callback). The nesting depth equals the length of the sequential chain. This nesting is not incidental — it is the direct encoding of **sequential ordering** in CPS: the inner closures capture the outer closures' variables (the results of previous operations), which is exactly what sequential data flow requires. `async/await` does not eliminate this structure; it just lets the programmer write it as flat sequential code while the compiler generates the nested closures automatically.

---

**CTQ 4.3** The equivalence `async def f(): x = await g(); return x + 1` and `g_cps(lambda x: k(x + 1))` is claimed. Walk through the desugaring step by step. What does `await` *do* to the continuation? Where does `k` come from in the async version?

[[___]]
<script>true</script>

> Step 1: `async def f()` declares `f` as a coroutine. When called, it returns a coroutine object without running any code yet. The coroutine object *is* a suspended continuation — the entire body of `f` is waiting.
>
> Step 2: `x = await g()` means: run `g()` to get an awaitable; when that awaitable completes with a result, bind the result to `x` and continue. The "continue" part is the rest of `f`'s body — i.e., `return x + 1`. This rest-of-body is exactly the continuation `lambda x: k(x + 1)`, where `k` is the continuation of whoever awaited `f()`.
>
> Step 3: `return x + 1` in an async function calls the implicit outer continuation `k` with `x + 1`. The Python runtime provides `k` as the mechanism that signals the outer `await` (if any) or the event loop's task scheduler that `f` has completed.
>
> So `await` performs: "pass the rest of this coroutine as a continuation to the awaitable, and suspend until that continuation is invoked."

---

#### Part V: Trampolining

##### Model 6: The Stack Overflow Problem and Its Solution

In Python and JavaScript, every function call pushes a stack frame. CPS programs can chain thousands of tail calls, each one pushing a new frame — even though logically each frame is immediately garbage (there is no pending work). This causes `RecursionError` in Python even for simple CPS computations on large inputs.

**The trampoline pattern works in three steps:**

1. Instead of calling the next continuation directly, **return a thunk** — a zero-argument function (or wrapper object) that represents "the next step to execute."
2. The caller (the trampoline loop) receives the thunk but does NOT call it immediately inside the current frame. It first returns from the current frame, then calls the thunk.
3. A top-level `while` loop (the trampoline) keeps calling thunks until a non-thunk value emerges. This loop uses exactly one stack frame per step.

```
Without trampoline (stack grows):
  fact_tramp(5, k)
    fact_tramp(4, k2)        <-- frame stacked on top of 5's frame
      fact_tramp(3, k3)      <-- frame stacked on top of 4's frame
        ...                  <-- keeps growing

With trampoline (constant stack):
  trampoline loop iteration 1: calls fact_tramp(5, k)  -> returns Thunk(fact_tramp, 4, k2)
  trampoline loop iteration 2: calls fact_tramp(4, k2) -> returns Thunk(fact_tramp, 3, k3)
  trampoline loop iteration 3: calls fact_tramp(3, k3) -> returns Thunk(...)
  ...
  At every iteration, the previous frame is GONE before the next one starts.
```

**The key rule:** A trampolined CPS function must **return** a `Thunk` for its recursive tail call instead of **calling** it directly. This one change — `return Thunk(f, args)` instead of `f(args)` — is what makes trampolining work.

##### Runnable Model: Thunk Class and Trampoline

```python  liascript
import traceback

try:
    # ── Thunk: represents a deferred computation ─────────────────
    class Thunk:
        """
        A Thunk wraps a callable and its arguments.
        It represents 'do this computation, but not yet.'
        The trampoline loop will call it when it's ready.
        """
        def __init__(self, fn, *args):
            self.fn = fn
            self.args = args

        def __call__(self):
            return self.fn(*self.args)

        def __repr__(self):
            return "Thunk({}, {})".format(self.fn.__name__, self.args)

    # ── Trampoline: the iterative unwrapper ──────────────────────
    def trampoline(thunk_or_value):
        """
        Run a trampolined computation to completion.
        Keeps calling thunks until a non-Thunk value is produced.
        Uses O(1) stack space regardless of program depth.
        """
        result = thunk_or_value
        steps = 0
        while isinstance(result, Thunk):
            result = result()
            steps += 1
        return result, steps

    # ── Trampolined CPS factorial ────────────────────────────────
    # Instead of calling fact_cps(n-1, new_k) directly (which pushes a frame),
    # we return a Thunk wrapping that call (which pops back to the trampoline).
    def fact_tramp(n, k):
        """
        Trampolined CPS factorial.
        Returns a Thunk instead of making a direct recursive call.
        """
        if n == 0:
            return k(1)
        else:
            return Thunk(fact_tramp, n - 1, lambda result, _n=n, _k=k: _k(_n * result))

    # The final continuation stores the result and returns a non-Thunk value
    result_box = [None]
    def final_k(x):
        result_box[0] = x
        return x

    print("Trampolined factorial:")
    for n in [5, 10, 20, 100]:
        result_box[0] = None
        val, steps = trampoline(Thunk(fact_tramp, n, final_k))
        print("  fact_tramp({}) = {} ({} trampoline steps)".format(
            n, result_box[0], steps))

    # ── Show the O(1) stack depth ────────────────────────────────
    print()
    print("Demonstrating O(1) stack depth:")
    import sys

    max_depth = [0]
    call_count = [0]

    def fact_tramp_traced(n, k):
        call_count[0] += 1
        # Measure current Python call stack depth
        current_depth = 0
        frame = sys._getframe(0)
        while frame is not None:
            current_depth += 1
            frame = frame.f_back
        if current_depth > max_depth[0]:
            max_depth[0] = current_depth

        if n == 0:
            return k(1)
        else:
            return Thunk(fact_tramp_traced, n - 1,
                         lambda result, _n=n, _k=k: _k(_n * result))

    result_box[0] = None
    trampoline(Thunk(fact_tramp_traced, 50, final_k))
    print("  fact(50): max observed stack depth =", max_depth[0],
          "(constant regardless of n)")
    print("  Total thunk invocations:", call_count[0])

    # ── Non-trampolined CPS for comparison ───────────────────────
    print()
    print("For comparison, naive CPS factorial at n=500 (may hit recursion limit):")
    def fact_naive_cps(n, k):
        if n == 0:
            k(1)
        else:
            fact_naive_cps(n - 1, lambda result, _n=n, _k=k: _k(_n * result))

    original_limit = sys.getrecursionlimit()
    sys.setrecursionlimit(600)
    try:
        result_box[0] = None
        fact_naive_cps(500, lambda x: result_box.__setitem__(0, x))
        print("  Naive CPS fact(500) =", result_box[0], "(succeeded)")
    except RecursionError:
        print("  Naive CPS fact(500): RecursionError! (as expected without trampolining)")
    finally:
        sys.setrecursionlimit(original_limit)

    print()
    print("Trampolined version at n=500:")
    result_box[0] = None
    trampoline(Thunk(fact_tramp, 500, final_k))
    print("  Trampolined fact(500) ends in ...{}".format(
        str(result_box[0])[-6:]))
    print("  (succeeded)")

except Exception as e:
    print("[cps:trampoline] Error:", e)
    traceback.print_exc()
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

##### Critical Thinking Questions — Part V

**CTQ 5.1** In `fact_tramp`, the recursive branch returns `Thunk(fact_tramp, n-1, new_k)` instead of calling `fact_tramp(n-1, new_k)` directly. Why does wrapping in a `Thunk` prevent the immediate recursion that would otherwise occur?

[[___]]
<script>true</script>

> Calling `fact_tramp(n-1, new_k)` immediately invokes the function, pushing a new stack frame before the current frame has popped. This is what causes recursive stack growth.
>
> Returning `Thunk(fact_tramp, n-1, new_k)` instead constructs a `Thunk` object (heap allocation, O(1) work) and **returns** it — immediately popping the current stack frame. No recursive call has been made yet. The trampoline loop receives the `Thunk`, calls it (one frame), gets back another `Thunk` or a value, and repeats. At any moment, there is at most one active stack frame beyond the trampoline loop itself. The work that would have been encoded as nested stack frames is now encoded as a chain of `Thunk` objects on the heap, traversed iteratively.

---

**CTQ 5.2** The trampoline loop uses O(1) stack space regardless of program depth. Explain why. Be specific about what is on the stack at each iteration of the loop, and contrast this with what would be on the stack during a naive recursive CPS execution of the same program.

[[___]]
<script>true</script>

> **Trampoline loop:** At each iteration, the stack contains: (1) the trampoline loop frame, (2) one `Thunk.__call__` frame, (3) one `fact_tramp` frame. After `fact_tramp` returns a new `Thunk`, frames (2) and (3) are popped. The loop assigns the returned `Thunk` to `result` and iterates. Stack depth is always exactly 3 frames (or a constant) — independent of `n`.
>
> **Naive CPS:** `fact_cps(n, k)` calls `fact_cps(n-1, new_k)` without returning first. Frame for `n` stays on the stack while frame for `n-1` is added. Frame for `n-1` stays while `n-2` is added. After `n` calls, the stack has `n` frames for `fact_cps` plus frames for the intermediate lambda continuations. Stack depth is O(n).
>
> The trampoline trades stack depth for heap allocation: each `Thunk` object lives on the heap but stack depth stays constant.

---

**CTQ 5.3** In the Scheme tail-call activity (which you may have completed earlier in this course), Scheme guarantees proper tail calls by having the interpreter reuse the current stack frame instead of pushing a new one. Compare this to trampolining: what is the *same* about both approaches, and what is *different*?

[[___]]
<script>true</script>

> **Same goal:** Both achieve O(1) stack space for tail-call chains. Both allow unbounded recursion through tail calls without stack overflow. Both make it practical to write programs in CPS or continuation-heavy recursive style.
>
> **Different mechanisms:**
>
> - Scheme TCO is implemented by the *runtime/compiler*: when a call is in tail position, the runtime overwrites the current activation record with the new call's arguments and jumps (does not push a new frame). The programmer writes normal recursive code; the optimization is invisible.
>
> - Trampolining is implemented by the *programmer* (or a library): the programmer explicitly wraps tail calls in `Thunk` objects and calls the trampoline. The optimization is visible in the code structure.
>
> **Practical difference:** Scheme TCO is transparent and works for mutually recursive functions automatically. Trampolining requires the programmer to identify and wrap every tail call, and the trampoline must be entered at the top level. In languages without TCO (Python, Java, JavaScript without explicit optimization), trampolining is the standard workaround for writing recursive programs that would otherwise overflow the stack.

---

#### Exercises

> **Watch out! — Before the exercises: closures and loop variables**
>
> The exercises below ask you to write CPS functions by hand. Watch for this common mistake: if you build a continuation inside a loop or a function that rebinds a variable, all closures you create in that loop will share the *same* variable reference. Example: `[lambda: i for i in range(3)]` produces three lambdas that all return `2` (the final value of `i`), not `0`, `1`, `2`. Fix it with a default argument: `[lambda _i=i: _i for i in range(3)]`. The trampolined factorial above uses this pattern: `lambda result, _n=n, _k=k: _k(_n * result)`.

> **Watch out! — Before the exercises: the continuation is always the last argument**
>
> By convention throughout these exercises, the continuation `k` is always the *last* argument to any CPS function. When composing CPS functions, the inner function receives the outer function's continuation as its `k`. The outermost call always receives a final "sink" continuation (e.g., `print` or a `capture` function) that consumes the answer without passing it further.

##### Exercise 1: CPS-Transform `map`

In direct style, `map(f, lst)` applies `f` to each element of `lst` and returns a new list. In CPS, every call to `f` must use `f_cps`, and the result should be passed to `k` only once — after all elements have been processed.

Write `map_cps(f_cps, lst, k)` such that `k` receives the complete mapped list. Your implementation should be fully CPS: no intermediate returns, only tail calls to continuations.

```python  liascript
import traceback

try:
    # map_cps(f_cps, lst, k):
    #   f_cps is a CPS function: f_cps(x, k) calls k(f(x))
    #   lst is the input list
    #   k is called with the fully mapped list as its argument

    def map_cps(f_cps, lst, k):
        if len(lst) == 0:
            k([])
        else:
            f_cps(lst[0], lambda head:
                map_cps(f_cps, lst[1:], lambda tail:
                    k([head] + tail)))

    # A CPS version of "double": double_cps(x, k) calls k(2*x)
    def double_cps(x, k):
        k(x * 2)

    # A CPS version of "square": square_cps(x, k) calls k(x*x)
    def square_cps(x, k):
        k(x * x)

    result_box = [None]
    def capture(x):
        result_box[0] = x

    lst = [1, 2, 3, 4, 5]
    print("Input list:", lst)

    map_cps(double_cps, lst, capture)
    print("map double:", result_box[0])

    map_cps(square_cps, lst, capture)
    print("map square:", result_box[0])

    # Compare to Python's built-in map
    print("Direct map double:", list(map(lambda x: x * 2, lst)))
    print("Direct map square:", list(map(lambda x: x * x, lst)))

except Exception as e:
    print("[cps:map] Error:", e)
    traceback.print_exc()
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

**Exercise 1 Questions:**

1. In `map_cps`, how many times is `k` called during the evaluation of `map_cps(double_cps, [1,2,3], k)`? Trace through the execution to verify.
2. Modify `map_cps` to also handle errors: if `f_cps` takes a handler argument `h`, propagate `h` through the entire chain.

---

##### Exercise 2: CPS Interpreter for a Tiny Expression Language

Consider the following tiny expression language:

- `Num(n)` — a numeric literal
- `Add(left, right)` — addition of two sub-expressions
- `Let(name, value_expr, body_expr)` — bind `name` to the result of `value_expr` in `body_expr`

Write `eval_cps(node, env, k)` that evaluates `node` in environment `env` and calls `k` with the result. Every recursive call should be a tail call (CPS style).

```python  liascript
import traceback

try:
    # AST node constructors (using simple dicts for clarity)
    def Num(n):
        return {"type": "Num", "value": n}

    def Add(left, right):
        return {"type": "Add", "left": left, "right": right}

    def Let(name, value_expr, body_expr):
        return {"type": "Let", "name": name, "value": value_expr, "body": body_expr}

    def Var(name):
        return {"type": "Var", "name": name}

    # CPS interpreter
    def eval_cps(node, env, k):
        """
        Evaluate node in environment env (a dict), then call k with the result.
        All recursive calls are tail calls.
        """
        t = node["type"]

        if t == "Num":
            k(node["value"])

        elif t == "Var":
            if node["name"] not in env:
                raise NameError("Unbound variable: " + node["name"])
            k(env[node["name"]])

        elif t == "Add":
            # Evaluate left, then right, then add and call k
            eval_cps(node["left"], env, lambda left_val:
                eval_cps(node["right"], env, lambda right_val:
                    k(left_val + right_val)))

        elif t == "Let":
            # Evaluate value_expr, bind result to name, evaluate body in extended env
            eval_cps(node["value"], env, lambda val:
                eval_cps(node["body"], dict(list(env.items()) + [(node["name"], val)]), k))

        else:
            raise ValueError("Unknown node type: " + t)

    # Test programs
    env0 = {}

    result_box = [None]
    def capture(x):
        result_box[0] = x

    eval_cps(Num(42), env0, capture)
    print("Num(42) =>", result_box[0])

    eval_cps(Add(Num(3), Num(4)), env0, capture)
    print("Add(3, 4) =>", result_box[0])

    # let x = 5 in x + 10
    prog3 = Let("x", Num(5), Add(Var("x"), Num(10)))
    eval_cps(prog3, env0, capture)
    print("let x=5 in x+10 =>", result_box[0])

    # let x = 3 in let y = x+2 in x+y
    prog4 = Let("x", Num(3),
                Let("y", Add(Var("x"), Num(2)),
                    Add(Var("x"), Var("y"))))
    eval_cps(prog4, env0, capture)
    print("let x=3; y=x+2; x+y =>", result_box[0])   # Expected: 3 + 5 = 8

except NameError as e:
    print("[cps:interpreter] NameError:", e)
except Exception as e:
    print("[cps:interpreter] Error:", e)
    traceback.print_exc()
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

**Exercise 2 Questions:**

1. In `eval_cps` for `Add`, the left sub-expression is evaluated before the right. How would you modify the interpreter to evaluate them in *right-to-left* order? Does the final result change for well-typed programs?
2. Add a `Mul(left, right)` case to the interpreter. How many lines of new code are needed compared to the `Add` case?

---

##### Exercise 3: Implementing `call/cc`

`call-with-current-continuation` (call/cc) is a control operator that captures the **current continuation** — everything the program was about to do — and passes it as a first-class function to the user's function `f`. If `f` calls that captured continuation with a value, control jumps back to where `call/cc` was called, as if it had returned that value.

In CPS, `call/cc` is straightforward: since `k` already *is* the current continuation, we just pass `k` to `f`.

```python  liascript
import traceback

try:
    # callcc(f, k):
    #   Captures the current continuation k.
    #   Calls f with (k, k) — passing k both as the "escape" continuation
    #   and as the normal continuation.
    #   If f calls k(val), control returns to the call/cc site with val.

    def callcc(f, k):
        """
        call-with-current-continuation in CPS.
        f is a CPS function: f(escape, k) where escape IS k.
        """
        f(k, k)

    # ── Example 1: Normal use (no escape) ───────────────────────
    print("Example 1: callcc with normal return")
    def example1(k_outer):
        callcc(lambda escape, k: k(100),
               lambda result: k_outer("result from callcc: " + str(result)))

    example1(print)

    # ── Example 2: Early escape using callcc ────────────────────
    print()
    print("Example 2: early escape from search using callcc")

    def early_exit_search(lst, k):
        """
        Find the first negative in lst.
        Use callcc so that finding a match immediately calls k (the escape).
        """
        def search_body(escape, k_inner):
            found = None
            for item in lst:
                if item < 0:
                    found = item
                    break
            if found is not None:
                escape(found)
            else:
                k_inner(None)

        callcc(search_body, k)

    result_box = [None]
    def store(x):
        result_box[0] = x

    early_exit_search([3, 7, 2, -4, 8, -1], store)
    print("  First negative in [3,7,2,-4,8,-1]:", result_box[0])

    early_exit_search([1, 2, 3, 4, 5], store)
    print("  First negative in [1,2,3,4,5]:", result_box[0])

    # ── Example 3: Capture and re-invoke a continuation ──────────
    print()
    print("Example 3: demonstrating that callcc captures k as a first-class value")

    log = []

    def demo_capture(k_outer):
        # callcc passes k_outer to the body as 'escape'
        # The body records it and calls k_outer normally
        callcc(
            lambda escape, k_inner: (
                log.append("escape continuation captured"),
                log.append("escape is k_outer: {}".format(escape is k_outer)),
                k_inner("hello from inside callcc")
            )[-1],
            lambda msg: k_outer("wrapper saw: " + msg)
        )

    demo_capture(lambda s: log.append("outer received: " + str(s)))
    for entry in log:
        print(" ", entry)

except Exception as e:
    print("[cps:callcc] Error:", e)
    traceback.print_exc()
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

**Exercise 3 Questions:**

1. In the CPS model, `callcc(f, k)` is implemented as simply `f(k, k)`. Why is the continuation `k` passed *twice*? What role does each copy play?
2. A continuation captured by `call/cc` can be called *multiple times* (a "multi-shot continuation"). What would happen to the program state each time you called the same continuation? Why does this make multi-shot continuations dangerous to use carelessly?
3. Python's `return` statement is a restricted form of `call/cc` that can only be used once (single-shot, upward-only). What restriction does `return` impose that `call/cc` lifts?

---

##### Exercise 4: Manual Generator via CPS Closures

Python generators hide their continuation machinery. In this exercise you will build a simple "generator" manually using closures and CPS-style state, revealing exactly what `yield` is doing under the hood.

```python  liascript
import traceback

try:
    # We want to build a generator equivalent to:
    #
    #   def count_up(start, stop):
    #       n = start
    #       while n < stop:
    #           yield n
    #           n += 1
    #
    # A manual generator is an object with a send_next() method.
    # Internally it stores its continuation: "what to do when send_next() is called."

    class ManualGenerator:
        """
        A generator implemented using explicit CPS-style state.
        The '_resume' field holds the continuation for the next send_next() call.
        """

        def __init__(self, start, stop):
            self.stop = stop
            self._done = False
            self._value = None
            self._resume = None
            self._build(start)

        def _build(self, n):
            """
            Set up the continuation for the range [n, stop).
            Each step: yield n, then build for n+1.
            """
            if n >= self.stop:
                def done_step():
                    self._done = True
                    self._value = None
                self._resume = done_step
            else:
                def make_step(current_n):
                    def step():
                        self._value = current_n
                        # After yielding current_n, prepare the next step
                        self._build(current_n + 1)
                    return step
                self._resume = make_step(n)

        def send_next(self):
            """
            Advance the generator one step (like Python's next()).
            Returns (value, has_value): has_value is False when exhausted.
            """
            if self._done:
                return None, False
            self._resume()
            if self._done:
                return None, False
            return self._value, True

        def __iter__(self):
            while True:
                val, ok = self.send_next()
                if not ok:
                    break
                yield val

    # Test the manual generator
    print("Manual generator for range(2, 7):")
    gen = ManualGenerator(2, 7)
    values = []
    while True:
        val, ok = gen.send_next()
        if not ok:
            break
        values.append(val)
    print("  Values:", values)

    # Compare to Python generator
    print()
    print("Python generator for range(2, 7):")
    def py_gen(start, stop):
        n = start
        while n < stop:
            yield n
            n += 1

    print("  Values:", list(py_gen(2, 7)))

    # Show that the manual generator is iterable
    print()
    print("Manual generator using __iter__:")
    gen2 = ManualGenerator(10, 15)
    print("  Values:", list(gen2))

    # Demonstrate the continuation structure explicitly
    print()
    print("Peeking at the continuation chain:")
    gen3 = ManualGenerator(0, 4)
    print("  _resume is callable:", callable(gen3._resume))
    v1, _ = gen3.send_next()
    print("  After first send_next(): value =", v1, ", _resume points to next step")
    v2, _ = gen3.send_next()
    print("  After second send_next(): value =", v2)
    print("  The _resume field IS the saved continuation of the generator")

except Exception as e:
    print("[cps:generator] Error:", e)
    traceback.print_exc()
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

**Exercise 4 Questions:**

1. In `ManualGenerator`, where is the "continuation" stored? What does it contain at each point during the generator's lifetime?
2. In the Python generator `py_gen`, when `yield n` executes, what happens to the local variable `n` and the loop state? How does the `ManualGenerator` preserve equivalent information?
3. Python's `send(value)` method on generators can *pass a value back into* a paused generator (unlike `next()`, which always sends `None`). What would you need to add to `ManualGenerator` to support `send(value)`? How does this connect to the two-way nature of continuations?

---

#### Reflection Prompt

Take five minutes individually, then discuss with your group before the Recorder writes a shared response.

> **Every control flow structure you use daily — function calls, exceptions, async/await, generators, loops via recursion — has a CPS explanation. Does this make you feel that these are fundamentally the *same* thing, or fundamentally *different* things sharing a costume? What does your answer reveal about what a programming language *is*?**

Consider these sub-questions to guide your discussion:

- If they are the *same* thing (all just continuations), does that mean the differences between `return`, `raise`, `yield`, and `await` are merely *syntactic sugar* — or do the different affordances matter beyond aesthetics?
- If they are *different* things that CPS merely *encodes*, then what makes one control structure distinct from another? Is it the *type* of continuation (upward-only, reusable, shared), the *number* of continuations (k, h, both), or something else?
- Felleisen (1991) proved that `call/cc` cannot be encoded in lambda calculus without CPS transformation — it requires a change in the *evaluation strategy* of the language. What does this say about the relationship between syntax, semantics, and expressiveness?
- When you write `async/await` in Python or JavaScript, you are using a feature the language designers added explicitly. If CPS is "already there" underneath, why did those keywords need to be added at all?

[[___]]
<script>true</script>

---

#### Further Reading

- **Appel, Andrew W.** *Compiling with Continuations.* Cambridge University Press, 1992. — The definitive reference for CPS as an intermediate representation in optimizing compilers. Shows how every compiler optimization (inlining, closure conversion, register allocation) has a natural CPS formulation.

- **Scheme R7RS specification, Section 6.10:** `call-with-current-continuation`. The canonical definition of `call/cc` in a language that has supported it since 1975. Available at [r7rs.org](https://r7rs.org).

- **Felleisen, Matthias.** "On the Expressive Power of Programming Languages." *Science of Computer Programming* 17(1-3), 1991. — Proves formally that `call/cc` (and therefore CPS) adds strictly more expressive power than the untyped lambda calculus. Foundational for understanding what "expressive power" means rigorously.

- **Python PEP 342** (Coroutines via Enhanced Generators) and **PEP 3156** (Asynchronous I/O Support). Available at [peps.python.org](https://peps.python.org). — The design documents explaining how CPython implements generators and asyncio as CPS state machines.

- **Piponi, Dan.** "The Mother of All Monads." *A Neighborhood of Infinity* (blog), 2008. Available at [blog.sigfpe.com](http://blog.sigfpe.com/2008/12/mother-of-all-monads.html). — Shows that the continuation monad (the Haskell formalization of CPS) is the "universal" monad from which all other monads can be derived. Connects CPS to the broader theory of computational effects.

- **Reynolds, John C.** "Definitional Interpreters for Higher-Order Programming Languages." *Higher-Order and Symbolic Computation* 11(4), 1998 (reprint of 1972 original). — The paper that introduced CPS transformation as a program analysis and compilation technique, predating even Scheme's adoption of `call/cc`.

## Going Deeper: Parallelism for Free: Functional Programming at Scale

> **Imagine a restaurant kitchen preparing a five-course dinner.** If every chef shares one cutting board, each course must wait for the previous chef to finish — a single-file bottleneck. But if no chef ever touches another chef's equipment, all five courses can be prepared at the same time. Pure functional programming gives you the second kitchen automatically: because each function reads only its own argument and writes nothing shared, every call is its own isolated chef. Two cores can run `f(3)` and `f(7)` simultaneously without a mutex, a lock, or even a conversation. This module shows you exactly how that guarantee works — and how to cash it in.

#### Learning Goals

By the end of this activity, you will be able to:

- Explain why pure functions are trivially parallelizable and formally define the independence theorem for `map`
- Identify race conditions in shared-state concurrent code and contrast them with race-free functional equivalents
- Implement parallel data processing pipelines in Python using `multiprocessing` and `concurrent.futures`
- Construct a MapReduce computation by decomposing a problem into independent map phases and a reduction phase
- Compare the parallelism models of functional languages (Erlang, Haskell) with Python's multiprocessing approach and evaluate their tradeoffs

---

#### Before You Begin

Make sure you are comfortable with these concepts before starting. If any feel unfamiliar, spend five minutes reviewing them now.

- **Pure functions:** a function whose output depends only on its arguments and that produces no observable side effects (no global writes, no I/O, no mutation of arguments). You should be able to classify a given Python function as pure or impure.
- **`map`, `filter`, `reduce`:** the three higher-order functions from week 1. You should be able to read and write simple pipelines using them.
- **Python threads vs. processes:** `threading` uses OS threads that share memory and are subject to the GIL; `multiprocessing` spawns separate OS processes with no shared memory. Know which module you are looking at.
- **Lambda expressions:** `lambda x: expr` creates an anonymous function. You should be comfortable with one-liner lambdas passed as arguments.
- **Big-O notation:** you should be able to say whether an algorithm is O(n), O(n log n), or O(n²), and reason about why.

If you have not seen `functools.reduce` yet, run `help(reduce)` in a Python REPL before the first code block.

---

*"Pure functions are like electricity from nuclear power — you get massive energy with no visible moving parts, and purity is your containment vessel."*

Every processor you will touch for the rest of your career has multiple cores. The modern GPU has thousands of them. **The central promise of functional programming is that pure functions parallelize automatically**: if a function has no side effects and reads no shared state, two calls to it can run concurrently with zero synchronization. No mutexes. No race conditions. No deadlocks. This is not a minor convenience; it is a fundamental shift in how software scales.

In this module we trace that promise from the theory (why purity enables parallelism, mathematically) through the practice (Python's `multiprocessing`, `concurrent.futures`, and a worked MapReduce implementation) to the industrial scale at which functional languages like Erlang and Haskell operate. The authentic parallel assignment that follows this module asks you to parallelize a data processing pipeline over millions of records using only the tools you build here.

---

#### Directions and Group Roles

Work in your POGIL team (**Manager, Recorder, Presenter, Reflector**). Individual sections are marked *Solo*; partner sections are marked *Pairs*; group sections are unmarked and require all four roles. Post the Recorder's shared answers to the Class Activity discussion.

---

### Part I: The Theory — Why Purity Enables Parallelism

> **Intuition before the math.** Before you read the formal definitions, build the picture in your head: a race condition is what happens when two chefs both reach for the same salt shaker at the same moment — one of them gets an unexpected result. The formal treatment below shows exactly why a pure function is equivalent to giving each chef their own private salt shaker. The math is short; the intuition carries most of the weight.

#### 1. The Race Condition, Formally

A **race condition** occurs when two threads read and write a shared variable, and the final value depends on the order of execution — an order the scheduler, not the programmer, controls. Race conditions are the central hazard of concurrent imperative programming, and they are notoriously hard to test for: the test passes because the scheduler happened to run threads in the right order that morning.

**A pure function cannot participate in a race condition.** The mathematical reason: a pure function $f$ satisfies $f(x) = f(x)$ for all $x$ at all times — its result is a function of its argument alone. No thread can change what $f(5)$ returns by writing to shared state, because $f$ reads no shared state. Two calls $f(5)$ and $f(7)$ are **independent** by construction; they can execute on two different cores with no coordination at all.

**The independence theorem for `map`:** If $f$ is pure, then

$$
\mathrm{map}(f, [x_1, x_2, \ldots, x_n])
$$

is *trivially parallelizable*: the $n$ applications $f(x_1), f(x_2), \ldots, f(x_n)$ have no dependencies between them and can execute in any order, or simultaneously, yielding the same result.

---

##### Model 1: Pure vs. Impure Parallelism

```python
import threading

# ---- IMPURE: race condition ----
total_bad = 0
def add_to_total(x):
    global total_bad
    total_bad += x   # read-modify-write: NOT atomic!

threads = [threading.Thread(target=add_to_total, args=(i,)) for i in range(100)]
for t in threads: t.start()
for t in threads: t.join()
print("Impure sum (may be wrong):", total_bad)   # probably not 4950

# ---- PURE: no shared state ----
from functools import reduce
numbers = list(range(100))
pure_sum = reduce(lambda a, b: a + b, numbers, 0)
print("Pure sum (always correct):", pure_sum)   # always 4950
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

> **Watch out! — The GIL does not save you.** Students often assume Python's Global Interpreter Lock prevents all race conditions. It prevents two Python bytecode instructions from running at the *exact* same CPU cycle, but `total_bad += x` compiles to three bytecodes (LOAD, ADD, STORE), and the GIL can release between any two of them. You can still get the wrong answer. The pure `reduce` sidesteps the entire question.

##### Critical Thinking Questions — *Solo then Group*

1. Run the impure version several times. Does `total_bad` always equal 4950? Why or why not? What specific hardware interleaving causes the discrepancy?
2. The pure `reduce` is sequential. How is it *safer* than the threaded impure version even before parallelism enters the picture?
3. Identify the exact line in `add_to_total` that contains the race condition and explain why Python's GIL does NOT fully protect against it for all operations.

---

#### 2. The MapReduce Pattern

> **Intuition.** Think of MapReduce as a two-round election count. In round one, every precinct (a `map` worker) independently tallies its own ballots — no precinct needs to talk to another. In round two, a central office (the `reduce` step) sums the precinct totals. The independence of round one is the purity guarantee; the associativity requirement in round two is the mathematical condition that makes the tree-structured summing of partial totals give the same answer regardless of grouping.

**MapReduce** is the computational pattern that Google used to index the web, and that Hadoop, Spark, and modern cloud pipelines all implement. It has two phases:

1. **Map**: Apply a pure function to each element of a large dataset (parallelizable over all elements)
2. **Reduce**: Combine results using an associative operation (parallelizable as a tree)

The word count problem is the "Hello, World" of MapReduce. Given a corpus of documents:

- **Map**: each document → list of (word, 1) pairs
- **Shuffle** (sort by key — often handled by the framework)
- **Reduce**: for each unique word, sum the counts

```python
from functools import reduce
from collections import defaultdict

# A tiny corpus
corpus = [
    "the quick brown fox jumps over the lazy dog",
    "the dog barked at the fox",
    "quick brown foxes are quick",
]

# MAP: pure function, document -> (word, count) pairs
def word_map(document):
    return [(word, 1) for word in document.lower().split()]

# SHUFFLE: group by key (in real MapReduce, this is a distributed sort)
def shuffle(pairs):
    groups = defaultdict(list)
    for key, val in pairs:
        groups[key].append(val)
    return dict(groups)

# REDUCE: pure function, (key, [values]) -> (key, total)
def word_reduce(key_values):
    key, values = key_values
    return (key, reduce(lambda a, b: a + b, values, 0))

# Pipeline
all_pairs  = reduce(lambda a, b: a + b, map(word_map, corpus), [])
grouped    = shuffle(all_pairs)
word_count = dict(map(word_reduce, grouped.items()))

for word, count in sorted(word_count.items(), key=lambda x: -x[1])[:10]:
    print(f"  {word:15s}: {count}")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

---

##### Critical Thinking Questions — *Pairs*

4. In the MapReduce pipeline above, which phases could run on different cores simultaneously? Draw a diagram showing which operations could overlap on a 4-core machine.
5. The reduce phase requires an **associative** operation. What would go wrong if we used subtraction instead of addition in the word-count reducer? Construct a concrete counterexample.
6. The shuffle/sort step is the bottleneck in distributed MapReduce. Why can't shuffle be parallelized as freely as map? What property of the sorted output makes it necessary to coordinate?

---

### Part II: The Practice — Python Multiprocessing

> **Intuition.** Part I proved that pure functions *can* safely run in parallel. Part II shows how Python actually *does* it. The key mental model: `multiprocessing.Pool.map(f, items)` is the same as `list(map(f, items))` — identical interface, identical results — except the work is distributed across OS processes that share no memory. If `f` is pure, you get the speedup for free. If `f` has side effects, you get silent corruption instead.

#### 3. `multiprocessing.Pool.map`: The Parallel Map

Python's `multiprocessing` module spawns true OS processes, bypassing the GIL. `Pool.map(f, iterable)` is a parallel implementation of `map(f, iterable)`: it distributes the work across a pool of worker processes and collects results. Because each worker runs `f` on its slice of the data with no shared memory, the only requirement is that `f` is a **pure function** (or close enough — side effects to *separate* files are fine).

```python
import multiprocessing
import time
import math

def is_prime(n):
    """Pure function: no side effects, result depends only on n."""
    if n < 2: return False
    if n == 2: return True
    if n % 2 == 0: return False
    for i in range(3, int(math.sqrt(n)) + 1, 2):
        if n % i == 0:
            return False
    return True

numbers = list(range(100_000, 101_000))

# Sequential (always correct, always reproducible)
t0 = time.perf_counter()
seq_primes = [n for n in numbers if is_prime(n)]
t1 = time.perf_counter()
print(f"Sequential: {len(seq_primes)} primes in {t1-t0:.4f}s")

# Demonstrate: same pure function, same result regardless of execution order
# On a real machine: pool = multiprocessing.Pool(); results = pool.map(is_prime, numbers)
par_results = list(map(is_prime, numbers))   # identical logic, sequential for sandbox
par_primes  = [n for n, p in zip(numbers, par_results) if p]
assert seq_primes == par_primes
print(f"Pure function guarantee: {len(par_primes)} primes — result identical whether sequential or parallel ✓")
print("Key: is_prime reads only its argument → Pool.map(is_prime, numbers) is safe to parallelize")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

---

#### 4. `concurrent.futures`: The High-Level Interface

`concurrent.futures.ProcessPoolExecutor` is the modern, higher-level parallel map. It uses the same process-pool model but with a cleaner interface that works well with `map`, `submit`, and `as_completed`.

```python
import math
import time

def compute_heavy(n):
    """CPU-bound: sum of square roots of all divisors of n."""
    return sum(math.sqrt(i) for i in range(1, n+1) if n % i == 0)

data = list(range(1, 200))

t0 = time.perf_counter()
results = list(map(compute_heavy, data))
t1 = time.perf_counter()
print(f"Sequential: {len(results)} values in {t1-t0:.4f}s")

# On a real machine with ProcessPoolExecutor:
#   with ProcessPoolExecutor() as ex:
#       results = list(ex.map(compute_heavy, data))
# Interface is identical — only execution location changes.

top5 = sorted(zip(data, results), key=lambda x: -x[1])[:5]
print("Top 5 by divisor-sqrt-sum:")
for n, v in top5:
    print(f"  n={n:3d}: {v:.4f}")
print()
print("compute_heavy is pure: no closures, no shared state → picklable, safe for ProcessPoolExecutor")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

> **Watch out! — Functions must be picklable.** `ProcessPoolExecutor` serializes (pickles) your function and ships it to worker processes. Lambda functions and closures that capture local variables are NOT picklable in Python. If you try to pass a lambda to `ex.map(...)`, you will get a `PicklingError`. Define your worker function at module (top) level, not inside another function, and keep it free of captured mutable state.

---

##### Try It: *Group Activity* — Parallel Word Count

Extend the MapReduce pipeline from Section 2 to use `Pool.map` for the map phase. The corpus should be a list of 1000 sentences (you can generate them). Measure the speedup. Report:
- Sequential time for map phase
- Parallel time for map phase
- Speedup ratio
- Whether results are identical (they must be)

---

### Part III: Haskell — Parallelism as a Library

> **Intuition.** In Python you have to *ask* for parallelism by explicitly calling `Pool.map`. In Haskell, purity is enforced by the type system, so the runtime can hand out parallelism as hints (`par`) rather than commands — and because no function can secretly share state, those hints are always safe to act on (or ignore). Think of it as the difference between a kitchen where every chef must loudly announce "I need the cutting board" (Python's explicit locking) versus a kitchen where cutting boards are personal property by law, so no announcement is ever needed (Haskell's type-enforced purity).

#### 5. Sparks and Strategies in Haskell

Haskell's purity guarantee enables the runtime to parallelize evaluation **automatically and safely**. The `Control.Parallel` module provides two primitives:

- `par :: a -> b -> b` — evaluate `a` in a separate spark (lightweight thread), return `b`
- `pseq :: a -> b -> b` — evaluate `a` to weak head normal form, then return `b`

These combine into **evaluation strategies** in `Control.Parallel.Strategies`:

```haskell
-- Standard parallel map in Haskell
import Control.Parallel.Strategies

parMap :: Strategy b -> (a -> b) -> [a] -> [b]
parMap strat f xs = map f xs `using` parList strat

-- Usage: parallel prime check
primes :: [Int] -> [Bool]
primes xs = parMap rdeepseq isPrime xs
  where
    isPrime n = n > 1 && all (\d -> n `mod` d /= 0) [2..floor (sqrt (fromIntegral n))]

-- Parallel Fibonacci (contrived but illustrative)
fib :: Int -> Int
fib 0 = 0
fib 1 = 1
fib n = let a = fib (n-1)
            b = fib (n-2)
        in  a `par` b `pseq` (a + b)
```

**Why this works:** Haskell's type system enforces purity at compile time. A function in the `IO` monad (which can have side effects) cannot be passed to `parMap rdeepseq`. The compiler's type checker is a proof that parallelism is safe.

**The key concept:** `par x y` evaluates `x` as a *spark* (a hint to the runtime that `x` can be evaluated on another core) while returning `y` immediately. It is not a command ("evaluate this now on a thread") but a *hint* that is safe because `x` being pure means its evaluation cannot affect `y`. The runtime optimizes spark scheduling.

---

> **Watch out! — Sparks are hints, not guarantees.** Haskell's `par x y` does not force `x` to execute on another core right now. It registers `x` as a *spark* — a work item the runtime *may* steal onto another core when one is idle. If no core is free, the spark is simply ignored and `x` is computed lazily when needed. This means adding `par` everywhere will not necessarily speed things up; you need to spark work items that are large enough to justify the overhead of the spark bookkeeping (~microseconds). Profile before adding sparks.

#### 6. Erlang and the Actor Model

Haskell uses shared-nothing processes with message passing; so does **Erlang**, the language built for massive concurrency in telephone switches (now WhatsApp, Discord, RabbitMQ). Erlang's model is:

- Processes are **ultra-lightweight** (millions can run concurrently)
- **No shared memory** between processes (functional data only)
- Communication via **message passing** with immutable messages
- **Let it crash**: processes are supervised; failures restart cleanly

```erlang
% Erlang: parallel map via spawning
-module(pmap).
-export([pmap/2]).

pmap(F, List) ->
    Parent = self(),
    Pids = [spawn(fun() -> Parent ! {self(), F(X)} end) || X <- List],
    [receive {Pid, Result} -> Result end || Pid <- Pids].

% Usage:
% pmap:pmap(fun(X) -> X * X end, [1, 2, 3, 4, 5]).
% returns [1, 4, 9, 16, 25]
```

The pattern — spawn one lightweight process per element, collect results via message passing — works with millions of elements because Erlang processes use ~300 bytes of memory each (versus ~8KB for a kernel thread).

---

##### Critical Thinking Questions — *Group*

7. In Erlang's `pmap`, what guarantees that the `receive` loop collects results in the *same order* as the input list, even though processes might finish in different orders? (Hint: look at what is sent back.)
8. Compare Python's `multiprocessing.Pool.map` and Erlang's process-based `pmap`. Both achieve parallelism. What are three concrete differences in their cost model, and when would you prefer each?
9. Haskell's `par` is described as a "hint." What does it mean for a parallelism primitive to be a hint rather than a command, and what property of Haskell's semantics allows the hint to be safely ignored by the runtime?

---

### Part IV: Exercises — Building the Parallel Pipeline

> **Intuition before you code.** Before writing any parallel code, always ask: "Is my worker function pure?" If yes, parallelism is safe and the only question is whether the overhead of spawning processes is worth it for your input size. If no, you need to redesign — either make the function pure (return results rather than mutating state) or accept that you need explicit synchronization. The exercises below are designed so each worker function is pure; identify that property explicitly for each one before you start coding.

#### 7. Exercises

1. **Parallel image statistics.** Write a `parallel_map` that, given a list of 200 integers representing "pixel brightness" values, computes for each: whether it is above-average, its squared deviation from the mean, and its percentile rank (0-100). Implement this as a pure function on each pixel and run it in parallel. The mean must be computed sequentially first (why?), and the per-pixel computations are then independent. Report speedup.

2. **Word frequency pipeline.** Extend the MapReduce from Section 2 to handle a real text file (find a Project Gutenberg plain-text book). Use `Pool.map` for the map phase. Report: total unique words, top-20 most frequent, time comparison sequential vs. parallel.

3. **Parallel matrix multiply (conceptual).** Matrix multiplication $C = A \times B$ has $C_{ij} = \sum_k A_{ik} B_{kj}$. Show that computing each element $C_{ij}$ is a pure function of rows of $A$ and columns of $B$. Implement `par_matmul(A, B)` using `Pool.map` where the pure function computes one row of $C$. Verify on 50×50 random matrices that the result matches `np.dot(A, B)`.

4. **The cost of purity: profiling.** Pure functional style often creates extra copies of data rather than mutating in place. Write a benchmark that processes a list of one million integers in two ways: (a) functional style using `map` and `filter` chains; (b) imperative style using a single `for` loop with mutation. Measure wall-clock time and memory usage (`tracemalloc`). Discuss the tradeoff: when does the parallelizability of (a) outweigh its overhead, and at what input size does (b) win on a single core?

5. **Functional parallel design document.** You are designing a language feature for a new functional language that makes parallelism *explicit but safe*. Write a one-page design document: (a) the syntax for your parallel-map construct; (b) the type-system rule that ensures only pure functions can be parallelized; (c) how the compiler would detect purity statically; (d) one real-world pipeline (e.g., log analysis, image processing, ML feature extraction) that your construct would handle well. Use examples.

---

#### 8. Reflection Prompt

The MapReduce pattern was invented at Google because sorting, grouping, and aggregating billions of records required spreading computation across thousands of machines without any of those machines sharing memory or state. Your sequential `reduce` from week 1 already had the right shape; only the "map" being pure was needed to scale it to a datacenter. In your notebook, write a paragraph about one domain you care about (biology, music, economics, sports analytics, social science) where a dataset is large enough that sequential processing is a bottleneck, and sketch the map function and reduce function that would parallelize it.

---

#### 9. Further Reading

- Dean, Jeffrey and Sanjay Ghemawat. "MapReduce: Simplified Data Processing on Large Clusters." *OSDI '04*, USENIX, 2004. The original Google paper; beautifully written and accessible.
- Marlow, Simon. *Parallel and Concurrent Programming in Haskell* (O'Reilly, 2013). Free online. The definitive guide to `par`, `pseq`, and strategies.
- Armstrong, Joe. *Programming Erlang: Software for a Concurrent World* (Pragmatic Bookshelf, 2013). The creator of Erlang explains the actor model.
- Sutter, Herb. "The Free Lunch Is Over." *Dr. Dobb's Journal*, 2005. The foundational essay on why multicore requires a programming model change.
- Wadler, Philip. "Comprehending Monads." *Mathematical Structures in Computer Science* 2(4), 1992. Why the monad structure of `IO` in Haskell is what permits the type system to enforce purity and thus safe parallelism.

## Going Deeper: Monads: Programmable Semicolons

#### Learning Goals

By the end of this activity, you will be able to:

- Implement a `Maybe` monad in Python with `bind` (`>>=`) and `return`/`unit`, and use it to eliminate pyramid-of-doom null-checking from a multi-step pipeline
- State and verify the three monad laws (left identity, right identity, associativity) for a concrete monad implementation
- Implement a `List` monad and use it to model nondeterministic computation, explaining how `bind` distributes over the list of possibilities
- Read basic Haskell `do`-notation and translate it into the equivalent chain of `>>=` calls
- Recognize monadic patterns in Python code you already use (`with` blocks as IO monad, `async`/`await` as continuation monad, `None`-propagation as Maybe monad)

A **monad** is a design pattern for sequencing computations when something extra needs to happen between each step — propagating failure, threading state, collecting effects, or managing nondeterminism. Philip Wadler called `>>=` (pronounced "bind") a *programmable semicolon*: instead of `;` running statements silently in sequence, `>>=` runs a customizable "glue" operation between each step. Today we build the intuition bottom-up — from functions to functors to monads — and verify every construction in Python before touching Haskell. The arc: **the problem → Maybe → the three monad laws → List → do-notation → IO**.

---

#### Before You Begin

> **Prerequisites for this activity**
>
> **Required:**
>
> - **Higher-order functions** — you are comfortable passing functions as arguments and returning them. You know what `map`, `filter`, and `reduce` do.
> - **Closures** — you understand that a function can "capture" variables from its enclosing scope. `lambda x: x + n` captures `n`.
> - **Type systems basics** — you have seen type annotations in Python or another language. You understand what "a function that takes an `int` and returns a `str`" means as a type.
>
> **Helpful but not required:**
>
> - **Haskell syntax** — the activity introduces every piece of Haskell syntax it uses. You do not need prior Haskell experience, but familiarity helps.
>
> **If you are rusty on any Required topic**, spend 5 minutes reviewing before continuing — monads layer heavily on all three foundations.

---

#### You Already Use Monads

> **Stop. Read this before anything else.**
>
> Monads are not exotic mathematics invented to confuse you. You have already been using them for years — you just did not know the word.
>
> Here are three examples from Python you have certainly seen:
>
> **Python's `with open(...) as f:` block** is the **IO monad**. It sequences an operation (open file), ensures cleanup (close file), and threads the file handle through your code — all without you managing the lifecycle by hand.
>
> **None-safe chaining via `and`** is the **Maybe monad**. `x = d.get("key") and d["key"].upper()` short-circuits on `None` without an `if` statement. The "glue" between each step is: "if the previous step returned None, stop; otherwise keep going."
>
> **Python's `asyncio` / `async`/`await`** is the **async monad** (also called the Continuation monad). `result = await fetch(url)` looks like a normal assignment, but under the hood it suspends the coroutine, hands control back to the event loop, and resumes exactly where it left off. The "glue" between each `await` is the event loop's scheduler.
>
> **The one-sentence definition:** A monad is a design pattern for chaining computations while tracking a "side effect" — error state, IO, non-determinism, mutable state, async scheduling, etc. — in a way that is invisible to the pipeline author but customizable by the monad designer.
>
> Every monad you build today has already appeared in your programming life. The goal of this activity is to *name* what you already know.

---

#### Directions and Group Roles

Work in your POGIL team with rotated roles (**Manager**, **Recorder**, **Presenter**, **Reflector**). This is a derivation day: every abstraction is *derived* from a concrete problem. Do not accept a definition until you have seen the problem it solves. The Recorder writes Python implementations on the whiteboard; the Presenter explains the monad laws. After class, respond to the reflective prompt individually in your notebook.

---

### Part I: The Problem

#### 1. The Pipeline Problem — Why Monads Exist

Before we define anything, here is the problem that monads solve.

Suppose you have three operations, each of which might fail and return `None`:

- `divide(x, y)` — fails if `y == 0`
- `sqrt(x)` — fails if `x < 0`
- `log(x)` — fails if `x <= 0`

Without any monad, you get the **pyramid of doom**:

```python  liascript
def divide(x, y):
    return x / y if y != 0 else None

def safe_sqrt(x):
    return x ** 0.5 if x >= 0 else None

def safe_log(x):
    import math
    return math.log(x) if x > 0 else None

# Without monad: pyramid of doom
def pipeline_manual(x, y):
    result1 = divide(x, y)
    if result1 is not None:
        result2 = safe_sqrt(result1)
        if result2 is not None:
            result3 = safe_log(result2)
            # ... and it keeps nesting deeper with every new step
            return result3
    return None

print(pipeline_manual(4, 1))   # some float
print(pipeline_manual(-4, 1))  # None (sqrt of negative)
print(pipeline_manual(4, 0))   # None (division by zero)
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

Notice the pattern: every single step is wrapped in `if result is not None`. If you add a fourth step, you add another `if`. The logic you care about (divide, sqrt, log) is buried under boilerplate you do not care about.

Now here is the same pipeline **with the Maybe monad** (we will build this below):

```python  liascript
# With Maybe monad: flat chain
# (This is a preview — we build Maybe in the next section)

class Maybe:
    def __init__(self, value):
        self.value = value
    @classmethod
    def just(cls, x): return cls(x)
    @classmethod
    def nothing(cls): return cls(None)
    def bind(self, f):
        if self.value is None:
            return Maybe.nothing()
        return f(self.value)
    def __repr__(self):
        return f"Just({self.value})" if self.value is not None else "Nothing"

import math

def divide(x, y):
    return Maybe.nothing() if y == 0 else Maybe.just(x / y)

def safe_sqrt(x):
    return Maybe.nothing() if x < 0 else Maybe.just(x ** 0.5)

def safe_log(x):
    return Maybe.nothing() if x <= 0 else Maybe.just(math.log(x))

# With Maybe monad: flat chain — no pyramid, no repeated if-checks
result = Maybe.just(4).bind(lambda x: divide(x, 1)).bind(safe_sqrt).bind(safe_log)
print(result)

result2 = Maybe.just(4).bind(lambda x: divide(x, 0)).bind(safe_sqrt).bind(safe_log)
print(result2)  # Nothing propagates automatically
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

The `if result is not None` check still exists — but it is now inside `bind`, written once, rather than repeated by every caller. This is the core idea.

> **CTQ 0.1** In the pyramid-of-doom version, how many times is the pattern `if result is not None` written? In the monad version, how many times? Where did the other occurrences go?

> **CTQ 0.2** If you added a fourth step `safe_reciprocal(x)` (fails if `x == 0`) to the pipeline, how many lines would you add in the pyramid-of-doom version versus the monad version?

---

#### 2. Chaining Operations That Can Fail

Suppose several operations each return either a value or `None` (failure). Naive chaining drowns in `if` checks:

```python  liascript
def safe_div(x, y):
    return x / y if y != 0 else None

def safe_sqrt(x):
    return x ** 0.5 if x >= 0 else None

# Without a monad: tedious, fragile
def pipeline_manual(x, y):
    t1 = safe_div(x, y)
    if t1 is None: return None
    t2 = safe_sqrt(t1)
    if t2 is None: return None
    return t2

print(pipeline_manual(4, 1))    # 2.0
print(pipeline_manual(-4, 1))   # None (sqrt of negative)
print(pipeline_manual(4, 0))    # None (division by zero)
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

The pattern `result = f(x); if result is None: return None; ...` repeats every time. A monad *abstracts* that repetition into one operator.

---

#### The Maybe Monad — Full Implementation

```python  liascript
try:
    class Maybe:
        def __init__(self, value):
            self.value = value    # None means failure

        @classmethod
        def just(cls, x):
            return cls(x)         # wrap a success value

        @classmethod
        def nothing(cls):
            return cls(None)      # wrap failure

        def bind(self, f):
            # ">>= f": if we have a value, pass it to f; else propagate failure
            if self.value is None:
                return Maybe.nothing()
            return f(self.value)

        def __repr__(self):
            return f"Just({self.value})" if self.value is not None else "Nothing"

    # Wrap safe_div and safe_sqrt to return Maybe values
    def safe_div(x, y):
        return Maybe.nothing() if y == 0 else Maybe.just(x / y)

    def safe_sqrt(x):
        return Maybe.nothing() if x < 0 else Maybe.just(x ** 0.5)

    # The monadic pipeline: bind threads Maybe through the chain
    def pipeline(x, y):
        return safe_div(x, y).bind(safe_sqrt)

    print(pipeline(4, 1))    # Just(2.0)
    print(pipeline(-4, 1))   # Nothing
    print(pipeline(4, 0))    # Nothing

    # Multiple steps: x / y, then sqrt, then negate
    def multi(x, y):
        return (safe_div(x, y)
                .bind(safe_sqrt)
                .bind(lambda v: Maybe.just(-v)))

    print(multi(4, 1))   # Just(-2.0)

except Exception as e:
    print(f"[monads:maybe] {e}")
    import traceback; traceback.print_exc()
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

---

#### Model 1: Interrogating Maybe

> **Watch out!** A monad is NOT a container. It is a pattern for *sequencing computations*. The container metaphor ("Maybe is a box that either has a value or is empty") is a useful first intuition, but it breaks down for the State and Continuation monads, which you will see later. Think of a monad as a *pipeline builder*, not a *box*.

##### What Each Piece Does

Before the CTQs, make sure you can answer these warmup questions to yourself:

- `Maybe.just(5)` — what does this produce? What is `self.value`?
- `Maybe.nothing()` — what does this produce? What is `self.value`?
- `Maybe.just(5).bind(lambda x: Maybe.just(x * 2))` — trace through `bind` step by step. What is returned?
- `Maybe.nothing().bind(lambda x: Maybe.just(x * 2))` — trace through `bind`. Is the lambda called?

##### Critical Thinking Questions

> **CTQ 1.1** In `bind`, the check `if self.value is None: return Maybe.nothing()` is the "glue" that runs between every step. What would happen to the remaining `.bind` calls in `multi(4, 0)` — are they called or skipped? Trace through.

> **CTQ 1.2** `Maybe.just(x)` is called `return` in Haskell (it *wraps* a value without doing anything else). Why is a `return` function necessary alongside `bind`? What would go wrong if you could only chain `bind` calls?

> **CTQ 1.3** The `if result is None: return None` pattern from the manual pipeline is now *inside* `bind` — the caller never writes it. Identify one other situation in your Mini interpreter where you repeated a similar check everywhere. How would a monad-like abstraction eliminate it?

> **CTQ 1.4** None-checks are a form of *implicit control flow* — the function short-circuits without the caller's knowledge. How does the Maybe monad make that control flow *explicit* while still hiding it from the pipeline author? Is this better or worse than Python's exceptions for this use case?

---

### Part I-B: Two More Concrete Monads in Python

The Maybe monad handles one specific "side effect": the possibility of failure. But monads can track any side effect. Here are two more.

#### The Result Monad (aka Either)

The Maybe monad's weakness: when something fails, you get `Nothing` — but you do not know *why*. The **Result monad** (called Either in Haskell) fixes this by carrying an error message in the failure case.

```python  liascript
try:
    class Ok:
        """Represents a successful computation."""
        def __init__(self, value):
            self.value = value

        def bind(self, f):
            # Success: pass the value to f
            return f(self.value)

        def __repr__(self):
            return f"Ok({self.value})"

    class Err:
        """Represents a failed computation with an error message."""
        def __init__(self, message):
            self.message = message

        def bind(self, f):
            # Failure: skip f entirely, propagate the error
            return self

        def __repr__(self):
            return f"Err({self.message!r})"

    # Now our functions return Ok or Err instead of None
    def safe_div(x, y):
        if y == 0:
            return Err(f"Cannot divide {x} by zero")
        return Ok(x / y)

    def safe_sqrt(x):
        if x < 0:
            return Err(f"Cannot take sqrt of negative number {x}")
        return Ok(x ** 0.5)

    def safe_log(x):
        import math
        if x <= 0:
            return Err(f"Cannot take log of non-positive number {x}")
        return Ok(math.log(x))

    # Chain without try/except — errors propagate automatically
    result1 = safe_div(16, 4).bind(safe_sqrt).bind(safe_log)
    print(result1)   # Ok(some float)

    result2 = safe_div(16, 0).bind(safe_sqrt).bind(safe_log)
    print(result2)   # Err('Cannot divide 16 by zero') — error from step 1

    result3 = safe_div(-16, 4).bind(safe_sqrt).bind(safe_log)
    print(result3)   # Err('Cannot take sqrt of negative number -4.0') — error from step 2

except Exception as e:
    print(f"[monads:result] {e}")
    import traceback; traceback.print_exc()
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

> **Watch out!** Python's `list` comprehensions are syntactic sugar for the **List monad**. The expression `[y for x in xs for y in f(x)]` is exactly `xs >>= f` in Haskell's list monad. Every nested `for` clause is a monadic `bind`. You have been writing the List monad since your first Python class.

##### Critical Thinking Questions

> **CTQ 1.5** In the Result monad, `Err.bind` ignores `f` and returns `self`. This means once an error occurs, *all subsequent computations are skipped*. What is the advantage of this behavior over using `try/except`? What is one disadvantage?

> **CTQ 1.6** Both `Ok` and `Err` implement `bind`, but with different behavior. This is the *same interface* with *different implementations*. What design pattern from object-oriented programming does this resemble?

> **CTQ 1.7** In `result2` above, the error message says "Cannot divide 16 by zero." The `.bind(safe_sqrt)` and `.bind(safe_log)` calls after it are still written in the code — they are just skipped at runtime. How does this compare to early-return (`if ... return None`) in terms of readability?

---

#### The State Monad (Simplified)

The State monad threads a piece of mutable state through a sequence of pure functions — without actually mutating anything. Each step receives the current state, returns a value *and* a new state, and passes the new state to the next step.

Think of it like a factory assembly line where each station receives the product, modifies it, and passes it to the next station.

```python  liascript
try:
    class State:
        """
        Wraps a function: state -> (value, new_state)
        The 'state' can be anything: an integer counter, a stack, a dict, etc.
        """
        def __init__(self, run_fn):
            self._run = run_fn   # a function: s -> (value, s)

        @classmethod
        def pure(cls, x):
            # "return x" in a stateful context: don't touch the state
            return cls(lambda s: (x, s))

        def bind(self, f):
            # Run self to get (value, new_state), then run f(value) with new_state
            def run(s):
                value, new_s = self._run(s)   # step 1: run current computation
                return f(value)._run(new_s)   # step 2: run f with new state
            return State(run)

        def execute(self, initial_state):
            return self._run(initial_state)

    # State primitives
    def get():
        """Returns the current state as the value (without changing it)."""
        return State(lambda s: (s, s))

    def put(new_state):
        """Sets the state to new_state; returns None as the value."""
        return State(lambda s: (None, new_state))

    def modify(f):
        """Applies f to the current state."""
        return State(lambda s: (None, f(s)))

    # Example: thread a counter through three steps
    # Each step increments the counter by a different amount
    program = (
        modify(lambda n: n + 1)          # counter: 0 -> 1
        .bind(lambda _: modify(lambda n: n + 10))   # counter: 1 -> 11
        .bind(lambda _: modify(lambda n: n * 2))    # counter: 11 -> 22
        .bind(lambda _: get())           # read final state as value
    )

    value, final_state = program.execute(0)   # start with counter = 0
    print(f"value={value}, final_state={final_state}")  # value=22, final_state=22

    # A more realistic example: a stack machine
    def push(x):
        return modify(lambda stack: stack + [x])

    def pop():
        return State(lambda stack: (stack[-1], stack[:-1]) if stack else (None, stack))

    stack_program = (
        push(10)
        .bind(lambda _: push(20))
        .bind(lambda _: push(30))
        .bind(lambda _: pop())
        .bind(lambda top: State.pure(f"popped: {top}"))
    )

    result, remaining_stack = stack_program.execute([])
    print(result)            # popped: 30
    print(remaining_stack)   # [10, 20]

except Exception as e:
    print(f"[monads:state] {e}")
    import traceback; traceback.print_exc()
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

##### Critical Thinking Questions

> **CTQ 1.8** In the State monad, `bind` calls `self._run(s)` to get a `(value, new_state)` pair, then passes `new_state` to the next step. What would happen if `bind` passed the *original* `s` to the next step instead of `new_s`? Give a concrete example of the bug this would cause.

> **CTQ 1.9** The State monad threads state without any mutable variables — `s` is never assigned to; each step receives it as a function argument and returns a new one. How does this relate to the concept of *pure functions* from the earlier activities?

> **CTQ 1.10** The container metaphor ("a monad is a box") breaks for the State monad. There is no "box" here — `State` wraps a *function*, not a value. What does this reveal about the true nature of a monad?

---

### Part II: The Three Laws

#### 3. What Makes Something a Monad?

Three laws — not rules imposed from outside, but the conditions that make `bind` and `return` compose predictably. Every monad obeys them; if they fail, the abstraction breaks.

##### The Laws in Plain English First

Before the formal versions, here is what each law means in English:

**Left identity** — "Wrapping then immediately unwrapping is a no-op."
If you take a value `x`, wrap it in `just(x)`, and immediately call `.bind(f)`, you should get the same result as just calling `f(x)` directly. The wrapping did not add anything.

**Right identity** — "Unwrapping then re-wrapping is a no-op."
If you have a monad `m` and you call `.bind(just)`, you should get back something equivalent to `m`. Passing the wrapped value through the identity function should not change it.

**Associativity** — "Grouping of `.bind` chains does not matter."
Just as `(1 + 2) + 3 == 1 + (2 + 3)` for addition, `(m.bind(f)).bind(g)` should equal `m.bind(lambda x: f(x).bind(g))`. You can refactor long `.bind` chains freely — extracting a sub-chain into a helper function will not change the result.

##### Formal Statements

**Left identity:** `return(a).bind(f) == f(a)`

**Right identity:** `m.bind(return) == m`

**Associativity:** `(m.bind(f)).bind(g) == m.bind(lambda x: f(x).bind(g))`

The associativity law is why `bind` *is* a programmable semicolon: just as `(a; b); c` and `a; (b; c)` mean the same thing in imperative code, monadic sequencing is associative.

---

#### Code Cell: Verifying the Laws

```python  liascript
try:
    # Reuse Maybe from above (re-define inline for self-containment)
    class Maybe:
        def __init__(self, value):
            self.value = value
        @classmethod
        def just(cls, x): return cls(x)
        @classmethod
        def nothing(cls): return cls(None)
        def bind(self, f):
            return Maybe.nothing() if self.value is None else f(self.value)
        def __eq__(self, other):
            return self.value == other.value
        def __repr__(self):
            return f"Just({self.value})" if self.value is not None else "Nothing"

    ret = Maybe.just    # "return" in Haskell
    f = lambda x: Maybe.just(x * 2)
    g = lambda x: Maybe.just(x + 10) if x > 0 else Maybe.nothing()

    a = 5
    m = Maybe.just(3)

    # Left identity: ret(a).bind(f) == f(a)
    lhs_li = ret(a).bind(f)
    rhs_li = f(a)
    print("left identity:", lhs_li == rhs_li, f"  ({lhs_li} == {rhs_li})")

    # Right identity: m.bind(ret) == m
    lhs_ri = m.bind(ret)
    print("right identity:", lhs_ri == m, f"  ({lhs_ri} == {m})")

    # Associativity: (m.bind(f)).bind(g) == m.bind(lambda x: f(x).bind(g))
    lhs_as = m.bind(f).bind(g)
    rhs_as = m.bind(lambda x: f(x).bind(g))
    print("associativity:", lhs_as == rhs_as, f"  ({lhs_as} == {rhs_as})")

    # Verify law holds with Nothing too
    n = Maybe.nothing()
    print("nothing + left id:", ret(None).bind(f) == f(None) if False else "N/A (f not defined for None)")
    print("nothing + right id:", n.bind(ret) == n)
    print("nothing + assoc:", n.bind(f).bind(g) == n.bind(lambda x: f(x).bind(g)))

except Exception as e:
    print(f"[monads:laws] {e}")
    import traceback; traceback.print_exc()
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

---

#### Model 2: Laws in Action

[[MC]]
A programmer writes a "monad" where `m.bind(return)` returns `Maybe.nothing()` regardless of `m`. Which monad law does this violate?
- ( ) Left identity — wrapping then binding gives wrong result
- (x) Right identity — binding with the identity function must return the original monad
- ( ) Associativity — grouping of bind chains gives different results
- ( ) None; this is still a valid monad

##### Critical Thinking Questions

> **CTQ 2.1** The left identity law says `return(a).bind(f) == f(a)`. In words: "wrapping `a` and immediately passing it to `f` is the same as just calling `f(a)`." Why is this important? Give an example where a `return` that *did* something extra (beyond wrapping) would break a pipeline.

> **CTQ 2.2** Associativity means you can refactor long `bind` chains freely. Give a concrete example where the non-associativity of `bind` would make refactoring dangerous — where `(m.bind(f)).bind(g) ≠ m.bind(lambda x: f(x).bind(g))`.

> **CTQ 2.3** Your Mini interpreter's evaluator has an implicit "sequential execution" order: statements run one after another. In what sense is this already a monad? What is the "glue" between each statement, and what would you have to change to make it explicit?

> **CTQ 2.4** We verified the laws hold for `Maybe.nothing()`. Does this make intuitive sense for the right identity law? If `m` is `Nothing`, then `m.bind(ret)` calls `bind` with `ret` — but `bind` on `Nothing` returns `Nothing` without calling `ret`. So `Nothing.bind(ret) == Nothing`. Why is this the *correct* behavior? What would it mean if `Nothing.bind(ret)` returned `Just(None)` instead?

---

### Part III: The List Monad — Nondeterminism

#### 4. Lists as Nondeterministic Computations

The List monad treats a `[x, y, z]` as "a computation that nondeterministically returns x, y, or z." `bind` applies a function to every element and concatenates the results: it *fans out* all possibilities simultaneously.

```haskell
-- Haskell list monad (for reference)
do x <- [1, 2, 3]
   y <- [10, 20]
   return (x + y)
-- Result: [11, 21, 12, 22, 13, 23]
```

This is list comprehension — the `do` notation and `[x + y | x <- [1,2,3], y <- [10,20]]` compile to the same thing.

---

#### Code Cell: The List Monad

```python  liascript
try:
    class ListM:
        def __init__(self, values):
            self.values = list(values)

        @classmethod
        def ret(cls, x):
            return cls([x])

        def bind(self, f):
            # Apply f to each element; f returns a ListM; concatenate all
            result = []
            for v in self.values:
                result.extend(f(v).values)
            return ListM(result)

        def __repr__(self):
            return f"ListM({self.values})"

    xs = ListM([1, 2, 3])
    ys = ListM([10, 20])

    # Cartesian product: all pairs (x, y)
    sums = xs.bind(lambda x: ys.bind(lambda y: ListM.ret(x + y)))
    print("sums:", sums)

    # Compare to list comprehension — same result
    lc_sums = [x + y for x in [1, 2, 3] for y in [10, 20]]
    print("list comprehension:", lc_sums)
    print("same result:", sums.values == lc_sums)

    # Pythagorean triples up to n
    def pythag(n):
        ns = ListM(range(1, n + 1))
        return (ns
            .bind(lambda a: ns
            .bind(lambda b: ns
            .bind(lambda c:
                ListM([f"({a},{b},{c})"] if a*a + b*b == c*c and a <= b <= c
                      else []
                )))))
    print("Pythagorean triples <= 10:", pythag(10))

    # Verify left identity
    f = lambda x: ListM([x, x * 2])
    print("list left id:", ListM.ret(3).bind(f).values == f(3).values)

except Exception as e:
    print(f"[monads:list] {e}")
    import traceback; traceback.print_exc()
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

---

#### Model 3: Nondeterminism

##### Critical Thinking Questions

> **CTQ 3.1** `bind` for `ListM` concatenates results. The "glue" here is not failure propagation (as in Maybe) but *branching*: every possibility is explored. What real-world algorithm does this resemble? (Hint: think about backtracking search and Prolog from the Language Design module.)

> **CTQ 3.2** `ListM([])` (the empty list) acts as "no solutions" — analogous to `Maybe.nothing()`. Verify that `ListM([]).bind(f)` returns `ListM([])` for any `f`. Why is this the correct "failure" behavior for nondeterminism?

> **CTQ 3.3** Python's list comprehension `[x + y for x in [1,2,3] for y in [10,20]]` produces the same result as the List monad's bind chain. In one sentence: what does the List monad's `bind` correspond to in list comprehension syntax?

> **CTQ 3.4** The "side effect" tracked by the Maybe monad is failure. The "side effect" tracked by the List monad is nondeterminism (multiple possible values). What is the "side effect" being tracked by each of the following: (a) the Result monad, (b) the State monad, (c) the IO monad?

---

### Part IV: The IO Monad — Effects in a Pure Language

#### 5. Sequencing Side Effects

Haskell is a *pure* language: functions have no side effects. But programs must print output, read files, and interact with the world. The **IO monad** threads the "state of the world" implicitly through every IO-performing function, ensuring effects happen in order and are tracked by the type system.

You do not implement IO from scratch in Python (Python is impure by design), but you can *simulate* the idea: an `IO` value is a function from "current world state" to "(value, new world state)." `bind` sequences these world-transformations.

```python  liascript
# A toy IO monad that threads a "world log" instead of the real world
class IO:
    def __init__(self, run):
        self._run = run         # run : world -> (value, world)

    @classmethod
    def pure(cls, x):
        return cls(lambda w: (x, w))   # return: does nothing to the world

    def bind(self, f):
        def run(w):
            v, w2 = self._run(w)   # run self, get value + new world
            return f(v)._run(w2)   # run f(v) in the new world
        return IO(run)

    def execute(self):
        return self._run([])       # start with empty world log

# Demonstrate: pure wraps a value without touching the world
val, log = IO.pure(42).execute()
print(f"value={val}, log={log}")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

---

#### Code Cell: Toy IO Monad

```python  liascript
try:
    class IO:
        def __init__(self, run):
            self._run = run

        @classmethod
        def pure(cls, x):
            return cls(lambda w: (x, w))

        def bind(self, f):
            def run(w):
                v, w2 = self._run(w)
                return f(v)._run(w2)
            return IO(run)

        def execute(self):
            val, log = self._run([])
            return val, log

    def io_print(msg):
        return IO(lambda w: (None, w + [f"PRINT: {msg}"]))

    def io_read(prompt):
        return IO(lambda w: (f"<user input for '{prompt}'>", w + [f"READ: {prompt}"]))

    # Sequence: print a greeting, read a name, print "hello name"
    program = (
        io_print("What is your name?")
        .bind(lambda _: io_read("name"))
        .bind(lambda name: io_print(f"Hello, {name}!"))
    )

    val, log = program.execute()
    print("Execution log:")
    for entry in log: print(" ", entry)

except Exception as e:
    print(f"[monads:io] {e}")
    import traceback; traceback.print_exc()
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

---

#### Model 4: IO and Purity

##### Critical Thinking Questions

> **CTQ 4.1** In Haskell, a function of type `Int -> IO String` is *pure* — it does not actually perform IO. It produces an `IO String` value that describes what to do. Only the runtime executes it. How does this relate to the "values are descriptions of actions" idea in the toy IO monad above?

> **CTQ 4.2** In the IO monad, `bind` sequences two world-transformations. If you swapped the order — passing `w` to `f(v)` before `self._run` — what would break? What real-world bug does this correspond to?

> **CTQ 4.3** The type of `bind` for IO is `IO a -> (a -> IO b) -> IO b`. In words: "given an IO action that produces an `a`, and a function that turns an `a` into an IO action producing a `b`, produce an IO action producing a `b`." How is this *exactly* like writing `x = await some_async_function(); return x + 1` in Python?

> **CTQ 4.4** Compare the IO monad to the State monad. In State, the "state" being threaded is explicit in your code (you pass `s` everywhere). In IO, the "state" (the real world) is hidden inside `_run`. What is the advantage of hiding it? What might be the disadvantage?

---

### Part V: Do-Notation as Syntactic Sugar

#### 6. Making Monads Readable

Haskell's `do` notation desugars to `bind` chains:

```haskell
do x <- action1
   y <- action2 x
   return (x + y)

-- desugars to:
action1 >>= \x -> action2 x >>= \y -> return (x + y)
```

Python's `for` desugars similarly for the List monad, and `async`/`await` desugars for the IO/async monad. The pattern is always the same: `x <- m` becomes `m >>= \x -> rest`.

---

#### Code Cell: Simulating Do-Notation

```python  liascript
try:
    # Simulate do-notation using a generator-based approach for Maybe
    class Maybe:
        def __init__(self, value): self.value = value
        @classmethod
        def just(cls, x): return cls(x)
        @classmethod
        def nothing(cls): return cls(None)
        def bind(self, f):
            return Maybe.nothing() if self.value is None else f(self.value)
        def __repr__(self):
            return f"Just({self.value})" if self.value is not None else "Nothing"

    # A helper that runs a generator as a monad's do-notation
    def do(gen_fn, monad_class=Maybe):
        def run(*args):
            gen = gen_fn(*args)
            def step(value):
                try:
                    m = gen.send(value)   # resume generator with the bound value
                    return m.bind(step)   # bind the next step
                except StopIteration as e:
                    return monad_class.just(e.value)  # wrap final return value
            try:
                m = next(gen)
                return m.bind(step)
            except StopIteration as e:
                return monad_class.just(e.value)
        return run

    def safe_div(a, b):
        return Maybe.nothing() if b == 0 else Maybe.just(a / b)

    def safe_sqrt(x):
        return Maybe.nothing() if x < 0 else Maybe.just(x ** 0.5)

    # "do-notation" using Python generators — each yield is a monadic bind
    @do
    def pipeline(x, y):
        t = yield safe_div(x, y)   # like: t <- safe_div x y
        s = yield safe_sqrt(t)     # like: s <- safe_sqrt t
        return s * 2

    print(pipeline(4, 1))    # Just(4.0)
    print(pipeline(-4, 1))   # Nothing
    print(pipeline(4, 0))    # Nothing

except Exception as e:
    print(f"[monads:do] {e}")
    import traceback; traceback.print_exc()
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

---

#### Model 5: Do-Notation

[[MC]]
In Haskell's `do` notation, `x <- m` desugars to `m >>= \x -> ...rest...`. What does `_ <- io_print("hello")` (where the bound value is discarded) desugar to?
- ( ) `io_print("hello") >>= \_ -> ()`
- (x) `io_print("hello") >>= \_ -> rest` (bind with a function that ignores its argument)
- ( ) `return (io_print("hello"))`
- ( ) `io_print "hello"` (no desugaring needed)

##### Critical Thinking Questions

> **CTQ 5.1** The generator-based `do` simulation uses Python's `yield` to suspend a function and resume it with a value. In the CPS activity, `yield` was described as "giving the current continuation to the caller." Reconcile: how is `yield safe_div(x, y)` in the do-notation example equivalent to `safe_div_cps(x, y, lambda t: ...)`?

> **CTQ 5.2** Haskell's do-notation works for *any* monad — Maybe, List, IO, State, Parser. What is the one thing that must be the same across all of them for the desugaring to work?

> **CTQ 5.3** Your Mini interpreter's evaluator sequences statements: `eval_block` loops over a list of statements. Is this a monad? If you wanted to add early-exit (like `return` in the middle of a block), what would the "glue" between statements need to do? (Hint: this is exactly the `ReturnSignal` exception your Mini interpreter uses — describe it as a monad.)

> **CTQ 5.4** Python's `async`/`await` syntax is do-notation for the async monad. Write out what `result = await fetch(url)` would look like if Python used Haskell-style explicit bind instead of `await`. What does the `await` keyword "hide" from the programmer?

---

### Part VI: Exercises

1. **State monad extended.** Using the `State` monad implemented above, simulate a simple stack-based calculator that evaluates Reverse Polish Notation (RPN). Push numbers onto the stack; `+` and `*` operations pop two values and push the result. Evaluate `"3 4 + 5 *"` and verify the result is 35. Implement each operation as a `State` computation and chain them with `bind`.

2. **Parser monad.** A `Parser(run)` wraps `string -> (value, rest)` or `None` on failure. Implement `pure` and `bind`; implement `char(c)` (matches a single character). Use Parser to parse the string `"abc"` character by character. This is how Parsec-style parser combinator libraries work under the hood.

3. **Fmap and Functor.** Before monad, there is **functor**: a container supporting `fmap(f)` that applies `f` inside the container without affecting the structure. Implement `fmap` for Maybe and List. Show that `m.fmap(f).fmap(g) == m.fmap(lambda x: g(f(x)))` (functor composition law).

4. **Writer monad.** A `Writer(value, log)` carries a value and an accumulated log (a list of strings). `bind` sequences computations and concatenates their logs. Implement Writer and use it to add logging to the safe arithmetic pipeline: each step logs what it computed. The final result carries the full computation trace.

5. **Law verification for Result.** Verify all three monad laws hold for your `Ok`/`Err` Result monad from Part I-B. Write a Python test function that checks each law with `Ok(5)`, `Err("fail")`, and appropriate `f` and `g` functions. What happens when you check right identity on `Err("original")` — does `Err("original").bind(Ok) == Err("original")`?

---

#### Reflection Prompt

In your notebook: Philip Wadler called `>>=` a "programmable semicolon" because it lets you customize what happens between every two steps in a sequence. Your Mini interpreter's evaluator already *has* an implicit semicolon (the statement loop), but it is hardwired. If you replaced it with a monad, what capabilities would you gain? What would you lose? And: the Maybe, List, IO, and State monads all look completely different, yet they obey the same three laws. Does this surprise you — or does it feel like all "chaining" is secretly the same operation?

---

#### Further Reading

- Wadler, Philip. "Monads for Functional Programming" (1995). The original tutorial; still the clearest explanation, using exactly the error-handling and state examples from today.
- Hutton, Graham and Erik Meijer. "Monadic Parser Combinators" (1996). Parsers as monads — a direct preview of Exercise 2.
- Haskell Report 2010, Chapter 3.14: `do` notation desugaring — the formal specification.
- Milewski, Bartosz. *Category Theory for Programmers* (online, free). Part III covers monads from the categorical perspective — what "monoid in the category of endofunctors" actually means.
- Dan Piponi. "You Could Have Invented Monads! (And Maybe You Already Have.)" (blog, A Neighborhood of Infinity). The single best motivating essay; shows that monads arise naturally from the problems in Part I.
- Real World Haskell, Chapter 14: Monads — practical examples in a language where monads are unavoidable.

## Going Deeper: Lazy Evaluation and Infinite Structures

> **Imagine a just-in-time (JIT) factory.** A traditional factory builds parts in bulk, warehousing thousands of units before a single order arrives — it must predict demand in advance and guess wrong at its peril. A JIT factory builds a part only when a confirmed order arrives: no speculation, no waste, no inventory of parts that are never used. Lazy evaluation is JIT manufacturing for computation: an expression is only evaluated when its value is actually needed, and the result is cached so the "manufacturing run" never repeats. This module shows you how to build that factory from scratch in Python — and why languages like Haskell run it automatically for every expression.

#### Learning Goals

By the end of this activity, you will be able to:

- Distinguish eager (strict/call-by-value) from lazy (non-strict/call-by-need) evaluation strategies and explain the practical consequences of each for infinite data structures
- Implement a **thunk** in Python as a zero-argument closure that defers computation, and use it to represent an unevaluated expression
- Build a **lazy stream** (cons-cell with a thunk for the tail) and use it to represent and traverse infinite sequences such as the natural numbers or all primes
- Implement the Sieve of Eratosthenes as a lazy stream and use it to generate the first N primes without pre-specifying an upper bound
- Identify Python generators and iterators as built-in lazy evaluation mechanisms, and relate them to the thunk/stream model developed in this activity

---

#### Before You Begin

Review these concepts before starting. Each one appears directly in the code models below.

- **Zero-argument functions and closures:** you should be able to write `lambda: expr` and explain that the expression inside is not evaluated until the lambda is called. You should also understand that a lambda "closes over" variables from the surrounding scope.
- **Python classes and properties:** Models 3 and 4 use a class with a `@property` decorator. You should know that `obj.tail` calls the getter method, not direct attribute access.
- **Recursion:** several models define recursive functions and data structures. Be comfortable tracing two or three levels of recursion by hand before you start.
- **Python generators:** you have seen `yield` before (or will see it in the Reflection). Understanding that `yield` pauses execution and resumes on the next call is helpful background, though not required.
- **The call stack vs. the heap:** thunks store deferred computation on the heap (inside a closure object); forcing a thunk places a new frame on the call stack. Keeping these separate helps you reason about memoization.

---

Most programs you have written evaluate every expression the moment they encounter it. Add two numbers? The addition happens immediately. Build a list? Every element is computed before the list is returned. This strategy — called **eager evaluation** or **strict evaluation** — is the default in Python, Java, C, and most mainstream languages. It is easy to reason about: expressions have values, values are computed in order, and nothing is deferred.

But eager evaluation has a structural weakness. It forces you to know, before you start computing, how much you will need. You cannot ask for "the first five primes" without either pre-specifying a search limit or building a general-purpose lazy abstraction yourself. The moment your data source is conceptually infinite — the sequence of all primes, all Fibonacci numbers, all natural numbers — strict evaluation runs into a wall.

**Lazy evaluation** (also called **non-strict evaluation** or **call-by-need**) turns this on its head: values are computed only when they are actually needed, and the results are cached so that the same computation is never repeated. Haskell is lazy by default. Python and most other languages provide lazy tools as explicit abstractions — generators, iterators, and the patterns in this activity. Understanding how laziness is implemented — as **thunks**, **streams**, and **memoized closures** — illuminates both functional language design and practical Python patterns.

Arc: **the eager/lazy distinction → thunks as the primitive mechanism → streams as the data structure → the Sieve of Eratosthenes → calling conventions across languages**

---

#### Directions and Group Roles

Work in your POGIL team with rotated roles (**Manager**, **Recorder**, **Presenter**, **Reflector**). Consider each model individually first — run the code, observe the output, read the prose — then discuss the Critical Thinking Questions with your group before moving on.

---

### Part I: The Problem Laziness Solves

#### Model 1 — The Problem: Computing Without Knowing the End

> **Intuition.** The JIT factory analogy lands here in its most concrete form. An eager approach to "give me the first five primes" is like ordering a full warehouse run before you know how many units will sell. You must pick a limit, the limit may be wrong, and if it is too small you get a silently incorrect answer. A lazy approach is the confirmed-order model: produce the next prime only when asked, stop when the consumer says stop. The code below shows the eager version breaking; the rest of this activity builds the lazy factory from scratch.

The simplest statement of the problem: eager computation forces you to materialize the full sequence before you can work with it. If you want the first five primes, you need to supply a limit before you know where to stop. If the limit is too small, you miss answers; if it is too large, you waste work.

```python  liascript
# Eager: must generate ALL primes up to a limit
def primes_up_to(limit):
    result = []
    for n in range(2, limit + 1):
        if all(n % p != 0 for p in result):
            result.append(n)
    return result

# Problem: what if we want "the first 5 primes" without knowing the limit?
# primes_up_to(???)  # We don't know where to stop!

# Eager version requires over-approximating the limit
first_5_via_limit = primes_up_to(15)[:5]
print("First 5 primes (limit=15):", first_5_via_limit)

# What if the limit is too small?
too_small = primes_up_to(3)[:5]
print("First 5 primes (limit=3, too small):", too_small)  # Only 2 primes!

# What if we want the 1000th prime? We'd need a much larger limit.
# The eager approach couples "how many" to "up to where" — unnecessarily.

# What we WANT: generate primes on demand, stop when we have enough.
print("\nWhat we want:")
print("  - An infinite sequence of primes")
print("  - Take only as many as we need")
print("  - Never compute beyond what we asked for")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

> **Watch out! — Silent truncation is a real bug.** Notice that `primes_up_to(3)[:5]` does not raise an error — it silently returns a two-element list when you asked for five. Python slices never complain about over-indexing. In production code this kind of silent under-delivery causes downstream bugs that are hard to trace. Lazy evaluation makes this class of bug impossible: the consumer drives production, so you always get exactly as many elements as you ask for, or an explicit exhaustion signal.

This tension appears everywhere in computing: network packets arrive in a stream you cannot bound ahead of time; log files grow without a fixed length; a game's state space is conceptually infinite. The eager model forces an artificial ceiling onto every such problem. A lazy model lets you describe an infinite process and consume only as much as you need.

**Critical Thinking Questions (CTQs)**

> **CTQ 1.1** Run the code with `too_small = primes_up_to(3)[:5]`. The limit 3 yields fewer than 5 primes, so the slice silently returns a shorter list. How would you detect this error if you were calling `primes_up_to` from another module and did not know the true limit?

> **CTQ 1.2** `primes_up_to(15)[:5]` computes 6 primes (2, 3, 5, 7, 11, 13) before slicing down to 5. Roughly how much extra work does this represent? For the first 100 primes, the 100th prime is 541 — how many primes up to 541 would you compute unnecessarily?

> **CTQ 1.3** The phrase "on demand" means: produce the next value only when the consumer asks for it. Name two Python built-in features you already know that work this way (hint: what does `range(10**9)` return? What does `open(file)` return?).

---

### Part II: Thunks — The Primitive Mechanism

#### Model 2 — Thunks: Wrapping Computation in a Function

> **Intuition.** A thunk is a purchase order, not a product. When the JIT factory receives `lambda: sum(range(10**6))`, it receives a description of work to be done — a slip of paper, not a finished part. The slip sits in a drawer until someone calls it (`force(thunk)`), at which point the factory floor runs the computation and hands back the result. Nothing is manufactured until the order is confirmed. The `lazy_if` example below shows the payoff: the "else" branch is a purchase order that gets shredded before anyone reads it, so the expensive (or error-raising) work inside never happens.

The simplest way to defer computation: wrap it in a zero-argument function. In Haskell, the runtime does this automatically for every expression. In Python, we do it explicitly. A **thunk** is a zero-argument callable that, when called (**forced**), evaluates to the deferred value. The name comes from ALGOL compiler folklore — it described the "thunk" sound of a value landing on the stack after being computed.

Thunks are not exotic: every Python `lambda: expr` is a thunk if it takes no arguments. The key operations are `thunk(f) = f` (no-op: the lambda *is* the thunk) and `force(t) = t()` (call it to get the value). The power lies in what you can build on top.

```python  liascript
# A "thunk" is a zero-argument function that wraps a deferred computation.
def force(t):
    return t()   # evaluate the thunk by calling it

# Examples
x = lambda: 2 + 3         # not computed yet — just a closure over the expression
print("Thunk created, nothing computed yet.")
print("Forced value:", force(x))              # NOW computed: 5

# Lazy "if": only evaluate the branch we actually take
def lazy_if(cond, then_thunk, else_thunk):
    if cond:
        return force(then_thunk)
    else:
        return force(else_thunk)

# The else branch is 1/0 — would crash if evaluated eagerly
result = lazy_if(
    True,
    lambda: 42,
    lambda: 1 / 0     # never forced — no ZeroDivisionError
)
print("lazy_if result:", result)

# Regular Python 'if' is also lazy in this sense:
# The branch not taken is never evaluated.
# But function arguments are NOT lazy by default:
def eager_if(cond, then_val, else_val):
    return then_val if cond else else_val

# This WILL crash — both arguments evaluated before the call
try:
    bad = eager_if(True, 42, 1 / 0)
except ZeroDivisionError as e:
    print("eager_if crashed:", e)

# Thunks prevent the crash:
good = lazy_if(True, lambda: 42, lambda: 1 / 0)
print("lazy_if with bad branch:", good)
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

> **Watch out! — Closures capture variables by reference, not by value.** When you write `lambda: x + 1` inside a loop where `x` changes, the lambda does NOT capture the current value of `x` — it captures the variable `x` itself. By the time you force the thunk, `x` may have a completely different value. This is a classic Python gotcha. To freeze a value, use a default argument: `lambda x=x: x + 1`. You will encounter this issue in stream construction if you are not careful.

The contrast between `eager_if` and `lazy_if` reveals something profound about function calls: in a language where arguments are evaluated before the call (**by-value** or **applicative-order** evaluation), you cannot define a true conditional as a library function. The built-in `if` statement in Python, Java, and C is wired into the language precisely because argument evaluation is eager. In a lazy language like Haskell, you *can* define `myIf` as an ordinary function, because arguments are only evaluated when forced.

> **CTQ 2.1** What is the output of `force(lambda: force(lambda: force(lambda: 99)))`? How many times is `force` called? What does this tell you about the relationship between thunks and nesting?

> **CTQ 2.2** The `eager_if` function crashes even though `cond` is `True` and the result would be `42`. Explain the order of operations that causes the crash. At what exact point in the Python execution does `1/0` execute?

> **CTQ 2.3** Python's `and` and `or` are lazy (short-circuit). Write a one-line expression using `and` that safely accesses `obj.method()` only when `obj` is not `None`. How is this analogous to `lazy_if`?

> **CTQ 2.4** Suppose you wanted a `lazy_and(a_thunk, b_thunk)` function. Write it. Now argue: could you implement `lazy_and` correctly using `eager_and(a, b)`? Why or why not?

---

### Part III: Streams — Lazy Infinite Sequences

#### Model 3 — Streams: Lazy Infinite Sequences

> **Intuition.** A single thunk is a one-item purchase order. A stream is a standing order with a renewal clause: "deliver the first item now; attach a new purchase order for the second item; when that order is filled, attach one for the third; and so on." The factory never sees the full order book at once — only one item and the next slip at a time. Memoization is the factory's record-keeping: once an item has been manufactured (a tail forced), the result is logged so the floor never re-runs the same production run. This model builds the `Stream` class from scratch so you can see every moving part.

A thunk defers a single value. A **stream** uses thunks recursively to defer an entire infinite sequence. The idea is simple: a stream is a pair of a **head** (the current value, already computed) and a **tail** (a thunk that, when forced, produces the next stream). The tail is not forced until you ask for it, so the infinite sequence is never materialized all at once.

The key refinement is **memoization**: once the tail thunk has been forced, store the result so it is never recomputed. Without memoization, accessing `stream.tail.tail.tail` would re-evaluate the tail thunk three times. With memoization, each step is computed exactly once. This combination — lazy evaluation plus memoization — is called **call-by-need**, and it is what Haskell's runtime implements automatically.

```python  liascript
class Stream:
    def __init__(self, head, tail_thunk):
        self.head = head
        self._tail_thunk = tail_thunk
        self._tail = None          # None means "not yet computed"
        self._forced = False       # distinguish "not forced" from "forced to None"

    @property
    def tail(self):
        if not self._forced:
            self._tail = self._tail_thunk()   # force the thunk exactly once
            self._forced = True
        return self._tail                     # return memoized result

def stream_take(s, n):
    """Return the first n elements of stream s as a list."""
    result = []
    while n > 0 and s is not None:
        result.append(s.head)
        s = s.tail
        n -= 1
    return result

# Infinite stream of natural numbers starting at n
def count_from(n):
    return Stream(n, lambda: count_from(n + 1))

# Infinite stream of ones — self-referential!
ones = Stream(1, lambda: ones)

naturals = count_from(0)
print("First 10 naturals:", stream_take(naturals, 10))
print("First 5 ones:     ", stream_take(ones, 5))

# Map and filter over streams — they return new (lazy) streams
def stream_map(f, s):
    if s is None: return None
    return Stream(f(s.head), lambda: stream_map(f, s.tail))

def stream_filter(pred, s):
    if s is None: return None
    if pred(s.head):
        return Stream(s.head, lambda: stream_filter(pred, s.tail))
    return stream_filter(pred, s.tail)

evens   = stream_filter(lambda x: x % 2 == 0, count_from(0))
squares = stream_map(lambda x: x * x, count_from(1))

print("First 5 evens:   ", stream_take(evens, 5))
print("First 5 squares: ", stream_take(squares, 5))
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

Notice that `stream_map` and `stream_filter` return new streams immediately, without computing any elements. The lambda `lambda: stream_map(f, s.tail)` captures `f` and `s` in a closure; the actual recursive call happens only when `.tail` is accessed. Every stream operation is therefore O(1) in the number of elements consumed — no upfront work, no allocation beyond what you use.

> **CTQ 3.1** In `Stream.__init__`, why is `self._forced` necessary? Could you just check `self._tail is None` instead? Construct a case where a stream's tail legitimately produces `None` to justify the separate flag.

> **CTQ 3.2** The `ones` stream is defined as `ones = Stream(1, lambda: ones)`. Draw the structure in memory after `stream_take(ones, 3)` has been called. How many `Stream` objects exist? Which ones have been memoized?

> **CTQ 3.3** The `stream_filter` function calls itself recursively (not via a thunk) when the current head fails the predicate. What does this mean for filtering a stream where many consecutive elements fail? How might you fix it?

> **CTQ 3.4** Write `stream_zip(s1, s2)` that pairs corresponding elements from two streams, producing a stream of tuples `(s1.head, s2.head)`, `(s1.tail.head, s2.tail.head)`, etc. What is the type of the result?

---

### Part IV: The Sieve of Eratosthenes as a Stream

#### Model 4 — The Sieve of Eratosthenes as a Stream

> **Intuition.** The sieve is the killer demo of lazy streams. The eager version requires an upper bound; you must decide in advance how far to sieve. The lazy version has no ceiling — it is a pipeline of filters, each one stamped with a prime, chained end-to-end. When you ask for the next prime, the pipeline processes one more integer through every existing filter and, if it survives, stamps a new filter on the end. The pipeline grows on demand and never processes more than it must. Read the `sieve` function and find the single `lambda` that is the suspension point — everything before it runs eagerly; everything after it waits.

The Sieve of Eratosthenes is one of the oldest algorithms in mathematics: to find all primes, start with the integers from 2 upward, take the first element (it must be prime), remove all its multiples, and repeat on the remainder. In an eager language, you run the sieve over a bounded array. In a lazy language, the sieve can operate over an *infinite* stream of integers — the sieve never "finishes," but you can consume as many primes as you want.

The elegance of the lazy sieve is structural: `sieve(s)` is defined as "the first element of `s` (which is prime), followed by `sieve(filter out multiples of that element from the rest of s)`. This recursive definition describes an infinite process, but the thunk in the tail of each returned stream ensures that each step is deferred until the consumer asks for the next prime.

```python  liascript
class Stream:
    def __init__(self, head, tail_thunk):
        self.head = head
        self._tail_thunk = tail_thunk
        self._tail = None
        self._forced = False
    @property
    def tail(self):
        if not self._forced:
            self._tail = self._tail_thunk()
            self._forced = True
        return self._tail

def count_from(n):
    return Stream(n, lambda: count_from(n + 1))

def stream_filter(pred, s):
    if pred(s.head):
        return Stream(s.head, lambda: stream_filter(pred, s.tail))
    return stream_filter(pred, s.tail)

def stream_take(s, n):
    result = []
    while n > 0:
        result.append(s.head)
        s = s.tail
        n -= 1
    return result

def stream_nth(s, n):
    """Return the (0-indexed) nth element of stream s."""
    while n > 0:
        s = s.tail
        n -= 1
    return s.head

def sieve(s):
    p = s.head   # p is definitely prime: nothing smaller divided it
    return Stream(p, lambda: sieve(stream_filter(lambda x: x % p != 0, s.tail)))

primes = sieve(count_from(2))

print("First 10 primes:", stream_take(primes, 10))
print("First 20 primes:", stream_take(primes, 20))
print("100th prime:    ", stream_nth(primes, 99))
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

> **Watch out! — Stack depth grows with the number of primes.** Each new prime adds one `stream_filter` call frame to the chain. In CPython, the default recursion limit is 1000. If you ask for a very large prime (say, the 500th prime), the recursive calls inside `stream_filter` may hit Python's recursion limit and raise `RecursionError`. You can raise it with `sys.setrecursionlimit(5000)`, but the deeper fix is to rewrite `stream_filter` iteratively or use Python generators, which manage their own stack independently.

The `lambda: sieve(...)` in the tail of each returned stream is essential: without it, `sieve` would call itself immediately, which would call `sieve` again immediately, and so on — infinite recursion before a single prime is produced. The thunk inserts a suspension point: `sieve(s.tail_after_filtering)` is only called when someone accesses `.tail`, which only happens when the next prime is needed.

Memoization in `.tail` also matters here: every time `stream_take(primes, 10)` accesses `primes.tail`, it gets back the same memoized stream object rather than re-running the filter and sieve. Without memoization, consuming the 100th prime would re-evaluate every filter and sieve step at every level — exponential work instead of linear.

> **CTQ 4.1** Trace the first three steps of `sieve(count_from(2))` by hand. After accessing `.head`, what is the exact thunk stored in `.tail`? After forcing `.tail` once, what is the head of the resulting stream, and what is stored in its `.tail`?

> **CTQ 4.2** The `lambda: sieve(...)` in `sieve`'s return statement captures `p` by closure. Why is it critical that `p = s.head` is bound as a local variable before the `lambda` is created? What would go wrong if you wrote `lambda: sieve(stream_filter(lambda x: x % s.head != 0, s.tail))` instead?

> **CTQ 4.3** Each new prime `p` adds one more `stream_filter` layer to the chain. When you ask for the 1000th prime, the stream for the 999th filter must be traversed to produce the 1000th. How does memoization prevent this from being O(n²) total work?

> **CTQ 4.4** This sieve is sometimes called the "unfaithful sieve" because it is not quite as efficient as the true Sieve of Eratosthenes. In the true sieve, multiples of 2 are crossed out starting from 4, not tested for every odd number. In this stream version, `x % 2 != 0` is tested for every element in the stream. Can you think of a way to make the filter for prime `p` start at `p*p` rather than `p+1`?

---

### Part V: By-Value vs. By-Name — Language Design

#### Model 5 — By-Value vs. By-Name: Call Strategies in Language Design

> **Intuition.** You have now built lazy evaluation by hand. This model zooms out to ask: why don't all languages work this way? The answer is a trade-off with three points. By-value (eager): pay upfront, pay once per argument, predictable cost. By-name (lazy without memoization): skip unused arguments for free, but pay again for each use of the same argument. By-need (lazy with memoization, i.e., Haskell): skip unused arguments AND pay at most once per argument, but carry overhead for the thunk bookkeeping on every expression. The timing experiment below makes the cost of by-name's double-evaluation tangible.

Every language makes a fundamental decision at each function call: when do you evaluate the arguments? The two classic answers are:

- **Call-by-value** (eager, applicative-order): evaluate all arguments before entering the function body. Python, Java, C, Ruby, and almost every mainstream language use this.
- **Call-by-name** (lazy, normal-order): pass the argument as an unevaluated expression; evaluate it (from scratch) each time it is referenced in the body.
- **Call-by-need** (lazy + memoized): like call-by-name, but cache the result the first time it is forced. This is Haskell's strategy.

R uses **call-by-promise**: arguments are wrapped in promise objects that record whether they have been evaluated yet, which enables `missing()` and lazy default arguments that refer to other parameters.

The performance trade-offs are not obvious. Call-by-name can skip work entirely for unused arguments. But if an argument is used *multiple times*, call-by-name re-evaluates it each time — potentially far more expensive than call-by-value. Call-by-need gets the best of both worlds: skip unused arguments, evaluate used arguments exactly once.

```python  liascript
import time

# --- Simulated call-by-value (eager): argument evaluated before the call ---
def unused_arg_eager(x, y):
    return x   # y is computed but never used

t0 = time.perf_counter()
result_eager = unused_arg_eager(42, sum(range(10**6)))   # sum IS computed
t1 = time.perf_counter()
print(f"By-value:  result={result_eager}, time={t1 - t0:.4f}s  (sum computed even though unused)")

# --- Simulated call-by-name (lazy): argument wrapped in a thunk ---
def unused_arg_lazy(x, y_thunk):
    return x   # y_thunk is NEVER forced

def slow_sum():
    return sum(range(10**6))

t0 = time.perf_counter()
result_lazy = unused_arg_lazy(42, slow_sum)   # slow_sum is never called
t1 = time.perf_counter()
print(f"By-name:   result={result_lazy}, time={t1 - t0:.6f}s  (sum skipped entirely)")

# --- Python's short-circuit operators ARE lazy ---
print("\nPython short-circuit laziness:")
print("False and (1/0):", False and (1 / 0))   # 1/0 never evaluated
print("True  or  (1/0):", True  or  (1 / 0))   # 1/0 never evaluated

# --- When is by-value faster? When argument is used multiple times ---
def sum_twice_eager(n, total):
    # total already computed; we use it twice for free
    return total + total

def sum_twice_lazy(n, total_thunk):
    # call-by-name: total_thunk() called TWICE — computes sum twice!
    return total_thunk() + total_thunk()

val = 1000
t0 = time.perf_counter()
_ = sum_twice_eager(val, sum(range(val)))
t1 = time.perf_counter()
print(f"\nsum_twice eager:  {t1 - t0:.6f}s")

t0 = time.perf_counter()
_ = sum_twice_lazy(val, lambda: sum(range(val)))
t1 = time.perf_counter()
print(f"sum_twice lazy:   {t1 - t0:.6f}s  (sum computed twice!)")
print("(call-by-need would memoize the first call and match eager speed)")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

The timing output makes the trade-off concrete. By-name wins when the argument is unused; by-value wins (over naive by-name) when the argument is used multiple times. Call-by-need — the combination of by-name with memoization — dominates both: it skips unused arguments and computes used arguments exactly once. The `Stream` class from Models 3 and 4 implements call-by-need manually in Python: the `.tail` property is a by-name access, and the `_forced` flag is the memoization.

> **CTQ 5.1** The by-value run shows a measurable time cost even though `y` is unused. Precisely when during the function call does Python evaluate `sum(range(10**6))`? At what point in the call stack does control return to `unused_arg_eager`?

> **CTQ 5.2** The `sum_twice_lazy` example calls `total_thunk()` twice. Under call-by-need, the second call would return the memoized result instantly. Sketch a `memoize_thunk(f)` wrapper that converts a zero-argument function into a call-by-need thunk: the first call evaluates and caches; subsequent calls return the cache.

> **CTQ 5.3** Python's `and`/`or` are lazy, but Python's function calls are eager. Is there any built-in Python function (not operator) that is lazy in its arguments? Think about `all()`, `any()`, `map()`, `filter()`. Which of these produce results lazily, and which evaluate all arguments eagerly?

> **CTQ 5.4** R passes function arguments as *promises* — unevaluated expressions that are forced on first access and then cached. A default argument in R can refer to another parameter: `function(x, y = x * 2)`. Why is this impossible in Python's by-value model, and how does R's call-by-promise make it work?

---

#### Multiple Choice

[[MC]]
A thunk is `lambda: expr`. When does `expr` get evaluated?

    [( )] When the thunk is created
    [(X)] When the thunk is called (forced)
    [( )] Never, unless explicitly unboxed
    [( )] When the program exits

---

[[MC]]
The `Stream` class stores `self._tail` after the tail thunk is first forced. What is the purpose of this?

    [(X)] Avoid recomputing the tail on every access (memoization)
    [( )] Force evaluation of the tail earlier
    [( )] Allow mutation of the stream after construction
    [( )] Prevent infinite recursion in the constructor

---

[[MC]]
In call-by-name evaluation, what happens to an argument expression each time the parameter is referenced in the function body?

    [( )] It is evaluated once before the call and cached
    [(X)] It is re-evaluated from scratch each time the parameter is used
    [( )] It is evaluated at program start and stored globally
    [( )] It is never evaluated unless the programmer calls `force()`

---

[[MC]]
Python's `and` operator is lazy (short-circuit). Which of the following patterns exploits this to write safe, idiomatic Python?

    [( )] `print(x and y)` always prints both `x` and `y`
    [(X)] `obj and obj.method()` avoids calling `.method()` on `None`
    [( )] `x and y` always returns `True` or `False`
    [( )] `not x and y` is always equivalent to `not (x and y)`

---

#### Exercises

##### Exercise 1 — Stream Zip and Interleave (20 min)

Write `stream_zip(s1, s2)` that pairs corresponding elements from two streams, producing a stream of 2-tuples: `(s1[0], s2[0])`, `(s1[1], s2[1])`, and so on. Verify with `stream_take(stream_zip(count_from(0), count_from(10)), 5)` — you should see `[(0,10),(1,11),(2,12),(3,13),(4,14)]`.

Then write `stream_interleave(s1, s2)` that alternates elements: `s1[0]`, `s2[0]`, `s1[1]`, `s2[1]`, .... Verify by interleaving even numbers and odd numbers to recover the naturals.

##### Exercise 2 — Fibonacci as a Stream (20 min)

Implement the Fibonacci sequence as a `Stream` without any loops or index variables. One elegant approach: define `fibs` in terms of `stream_zip` and `stream_map` over `fibs` itself. Another approach: define a helper `fib_from(a, b)` that returns `Stream(a, lambda: fib_from(b, a+b))`. Verify that the first 10 terms are `[0, 1, 1, 2, 3, 5, 8, 13, 21, 34]`.

##### Exercise 3 — Memoize Decorator (25 min)

Write a `memoize(f)` decorator that caches the results of `f` by its arguments. Demonstrate that naive recursive Fibonacci is O(2^n) and that `memoize(fib)` (where `fib` calls the memoized version recursively) is O(n). Measure timing for `fib(30)` with and without memoization. Then connect back to streams: explain how the `_forced` flag in `Stream.tail` is memoization of a zero-argument function, making it a special case of your `memoize` decorator.

##### Exercise 4 — Lazy Pipeline (30 min)

Build a lazy pipeline for processing a "stream" of integers. Implement:
- `stream_drop(s, n)`: skip the first `n` elements
- `stream_scan(f, init, s)`: running cumulative reduce (like `itertools.accumulate`)
- `stream_until(pred, s)`: take elements while the predicate holds, then stop

Using these, compute the running sum of primes until the running sum exceeds 1000, returning both the running sum and the prime that pushed it over the threshold.

---

#### Reflection

**On laziness and modularity:** John Hughes's 1989 paper "Why Functional Programming Matters" argues that laziness is not just an efficiency trick — it is a *modularity* tool. It lets you separate the producer of data from the consumer of data: the producer generates infinitely; the consumer takes finitely. The producer does not need to know the consumer's stopping condition; the consumer does not need to know the producer's generation strategy. Reflect: in what other parts of software design does separation of producer and consumer improve modularity? (Think about HTTP streaming, Unix pipes, event listeners.)

**On Python generators:** Python's `yield` keyword creates generators, which are a form of laziness built into the language. Compare the `Stream` class from Model 3 to a generator function that `yield`s the same sequence. What does the generator provide that the `Stream` class does not? What does the `Stream` class provide that a generator does not? (Hint: consider re-traversal — can you go back and re-read an element of a generator after you have advanced past it?)

**On Haskell's trade-offs:** Haskell is lazy by default, which enables all the patterns in this activity without explicit thunks. But laziness is not free: every expression must be wrapped in a "thunk box" in memory, and the garbage collector must track which thunks have been forced. Haskell programmers sometimes encounter *space leaks* where unevaluated thunks accumulate faster than they are forced, exhausting memory. With eager evaluation, the memory profile of a program is predictable from its data structures. With lazy evaluation, space usage depends on evaluation order, which can be surprising. Is the expressiveness of laziness worth this trade-off? What kinds of programs benefit most from laziness?

---

#### Further Reading

- **"Why Functional Programming Matters"** — John Hughes (1989): the foundational argument that laziness enables modularity; freely available online. The section on lazy lists is directly relevant to this activity.
- **SRFI-41: Streams** — Philip Bewig's Scheme implementation of lazy streams, with a thorough discussion of eager vs. lazy stream variants and the memoization requirement.
- **Haskell's Lazy I/O and its pitfalls** — search "Haskell lazy IO problems" for discussions of `hGetContents` and why mixing laziness with side effects requires care.
- **Python `itertools` documentation** — the standard library's lazy iterator tools: `itertools.count`, `itertools.takewhile`, `itertools.islice`. These are Python's production-quality equivalents of the stream operations in this activity.
- **"The Art of the Interpreter"** — Guy Steele and Gerald Sussman (1978, MIT AI Memo 452): the paper that distinguished call-by-value, call-by-name, and call-by-need formally, and showed how to implement each in a meta-circular interpreter.
- **R's promise mechanism** — search "R lazy evaluation promises" for documentation on how R implements call-by-promise and why default arguments can refer to other parameters.
