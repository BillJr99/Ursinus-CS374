# Functional Programming
<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://github.com/BillJr99/Ursinus-CS374-Fall2026/blob/gh-pages/_pages/Activities/liascript-functional.md or locally via https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374/gh-pages/_pages/Activities/liascript-functional.md

import: https://raw.githubusercontent.com/liascript/CodeRunner/master/README.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

# Functional Programming

Unit 3 turns from building languages to inhabiting one paradigm deeply. Over two days we practice **functional programming** in the language you know best: Python's `lambda`, `map`, `filter`, and `reduce`, with the discipline of **purity** and **immutability**, because the functional toolkit is both a daily professional skill (it is the shape of data pipelines and of modern Java, JavaScript, and Rust idioms) and the bridge to Scheme and the lambda calculus ahead. The arc: **purity and why it pays $\rightarrow$ the big three combinators $\rightarrow$ higher-order thinking $\rightarrow$ writing without assignment**.

---

## Directions and Group Roles

Work in your POGIL team with rotated roles (**Manager**, **Recorder**, **Presenter**, **Reflector**). Consider each model and question individually first, then discuss with your group. The Recorder posts answers to the Class Activity Questions discussion board; the Presenter reports out areas of disagreement or alternative approaches. After class, respond to the reflective prompt individually in your notebook.

---

# Part I: Purity (Day 1)

## 1. Functions Like Mathematics Meant

**A pure function's output depends only on its inputs, and it changes nothing outside itself.** No mutation of arguments, no global reads or writes, no printing, no randomness. Purity buys three concrete powers: **substitution** (a call can be replaced by its result anywhere, the referential transparency of week 1), **testability** (no setup, no teardown, just input and expected output), and **parallel safety** (no shared state means no interference, the observation from the paradigms module about summing two halves of a list).

**Immutability is purity's partner.** Functional style does not modify a list; it produces a new one. Python's tuples are immutable; its lists are not, and functional discipline in Python means *choosing* not to mutate, a self-imposed rule that today's exercises enforce.

---

## Model 1: The Purity Audit

```python
def f1(xs):           return sorted(xs)
def f2(xs):           xs.sort(); return xs
total = 0
def f3(x):            global total; total += x; return total
def f4(x):            return x + len(LOG_LINES)     # LOG_LINES is a module global
def f5(x, factor=2):  return x * factor
```

### Critical Thinking Questions

1. Rule each function pure or impure, citing the disqualifying feature for each impure one. (Careful: `f1` and `f2` differ in exactly the way that matters.)
2. `f2` returns the right answer; why is it still dangerous? Construct the two-line calling code where `f2` silently damages its caller and `f1` would not.
3. `f4` reads but never writes a global. What power from Section 1 does it still forfeit, and what test-time symptom reveals it?
4. State the team's one-sentence test for purity, suitable for auditing the code you write Thursday.

---

## 2. The Big Three

**`map` transforms, `filter` selects, `reduce` combines.** Each replaces a loop pattern you have written a hundred times:

$$
\text{map}(f, [x_1, \dots, x_n]) = [f(x_1), \dots, f(x_n)]
$$
$$
\text{reduce}(\oplus, [x_1, \dots, x_n], z) = ((z \oplus x_1) \oplus x_2) \oplus \cdots \oplus x_n
$$

Note `reduce`'s left fold: the same left-leaning shape as your parser's `addsub` loop, no coincidence, and the reason a `reduce` with subtraction associates left.

---

## Code Cell

```python
from functools import reduce

scores = [88, 92, 54, 71, 67, 95, 49, 83]

try:
    # map: transform every element (curve by 5, cap at 100)
    curved = list(map(lambda s: min(s + 5, 100), scores))

    # filter: keep the passing scores
    passing = list(filter(lambda s: s >= 70, curved))

    # reduce: combine into one value (sum, then by hand a mean)
    total = reduce(lambda acc, s: acc + s, passing, 0)
    print("curved :", curved)
    print("passing:", passing)
    print("mean of passing:", total / len(passing))

    # The pipeline composed in one expression: data flows left to right
    result = reduce(lambda acc, s: acc + s,
                    filter(lambda s: s >= 70,
                           map(lambda s: min(s + 5, 100), scores)), 0)
    print("composed:", result)

    # reduce builds ANY aggregate: maximum, with the first element as seed
    print("max:", reduce(lambda a, b: a if a > b else b, scores))
except Exception as e:
    print(f"[functional:bigthree] {e}")
    import traceback; traceback.print_exc()
```

---

## Model 2: Loops in Disguise

### Critical Thinking Questions

5. Rewrite each call above as the explicit `for` loop it replaces (on paper). What bookkeeping (accumulators, index variables, append calls) did the combinators absorb?
6. In the composed pipeline, no intermediate list has a name. Argue one benefit and one honest cost for the reader, and connect to the readability criteria from week 2.
7. `reduce` with `lambda a, b: a - b` over `[10, 3, 2]` and seed 0: compute it by hand using the left-fold formula, then verify. Where exactly does associativity show up?

---

# Part II: Higher-Order Thinking (Day 2)

## 3. Functions That Make Functions

**A higher-order function takes or returns functions.** `map` takes one; today we also *return* them: `def make_adder(n): return lambda x: x + n` produces a different adder for each `n`, and the returned lambda *remembers* `n`, a phenomenon (the closure) whose mechanism we expose properly in the closures module. For now, use the power: parameterized behavior without classes.

[[MC]]
`compose = lambda f, g: lambda x: f(g(x))` is a higher-order function because it:
- ( ) Uses lambda syntax twice
- ( ) Avoids mutation
- (x) Both consumes functions as arguments and produces a function as its result
- ( ) Runs in logarithmic time

---

## 4. Exercises

1. *Loop exorcism.* Rewrite each with the big three, no loops, no assignments inside the logic: (a) lengths of all words longer than 3 in a sentence; (b) the product of the odd numbers in a list; (c) one-line word count of a string (split, map to 1, reduce with +).
2. *Higher-order toolkit.* Implement `compose(f, g)`, `twice(f)` (applies f two times), and `pipeline(*fns)` (composes any number, left to right). Demonstrate `pipeline(str.strip, str.lower, len)` on messy input.
3. *Your own map and reduce.* Implement `my_map` and `my_reduce` recursively (no loops!), with the class exception pattern. Property-test them against the built-ins on five inputs each. The recursive `my_reduce` is the warm-up for Scheme on Thursday.
4. *Purity refactor.* Take one impure function from your own past coursework (or `f2`/`f3` above), refactor it pure, and write the two-line test that the impure version would have failed or complicated.
5. *No-assignment challenge.* Compute the average word length of a paragraph using exactly one expression: no statements, no names bound except the parameter. Longest readable solution wins; unreadable solutions spark Friday's discussion of when functional style stops paying.

---

## Reflection Prompt

In your notebook: purity forbids a function from leaving traces on the world, which makes it trustworthy and also means it cannot *do* anything (no printing, no saving) without breaking the rules. Real programs must do things. Where do you think the impurity should live in a well-organized program, and can you name a system (kitchen, lab, organization) organized the same way?

---

## 5. Further Reading

- Douglas Thain. *Introduction to Compilers and Language Design*, functional notes; Python's `functools` documentation.
- Abelson and Sussman. *Structure and Interpretation of Computer Programs*, sections 1.1 through 1.3.
- John Hughes. "Why Functional Programming Matters" (1990): the classic argument that composition is the point.
