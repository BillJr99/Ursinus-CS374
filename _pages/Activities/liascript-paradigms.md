# Programming Paradigms
<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://github.com/BillJr99/Ursinus-CS374-Fall2026/blob/gh-pages/_pages/Activities/liascript-paradigms.md or locally via https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374-Fall2026/gh-pages/_pages/Activities/liascript-paradigms.md

import: https://raw.githubusercontent.com/liascript/CodeRunner/master/README.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

# Programming Paradigms

A **paradigm** is a worldview about what a program *is*: a sequence of commands, a society of objects, a composition of functions, or a set of facts and rules. Today we tour the four major paradigms with the same small problem expressed in each, because your team's language will have to pick a side (or blend several, as most modern languages do). The arc: **imperative $\rightarrow$ object-oriented $\rightarrow$ functional $\rightarrow$ logic $\rightarrow$ multi-paradigm reality**.

---

## Directions and Group Roles

Work in your POGIL team with rotated roles (**Manager**, **Recorder**, **Presenter**, **Reflector**). Consider each model and question individually first, then discuss with your group. The Recorder posts answers to the Class Activity Questions discussion board; the Presenter reports out areas of disagreement or alternative approaches. After class, respond to the reflective prompt individually in your notebook.

---

# Part I: The Four Worldviews

## 1. Imperative and Object-Oriented

**Imperative: a program is a sequence of state changes.** The core concepts are variables (named mutable cells), assignment, and control flow (sequencing, selection, iteration). The model matches the machine: memory cells change over time. C is the archetype; most languages contain an imperative heart.

**Object-oriented: a program is a society of objects exchanging messages.** State is *encapsulated* inside objects; behavior travels with the data it governs; **polymorphism** lets the same message mean different things to different receivers. OO answers the imperative paradigm's scaling problem: when everything can mutate everything, large programs become unpredictable, so OO draws fences.

## 2. Functional and Logic

**Functional: a program is the composition of functions.** The central commitments are **immutability** (values do not change; new values are produced), **first-class functions** (functions are values that can be passed and returned), and **referential transparency** (an expression can be replaced by its value without changing behavior). Where imperative code says *do this, then that*, functional code says *the answer is this transformation of that*. Scheme, Haskell, and increasingly the cores of Python and Java.

**Logic: a program is facts and rules; the runtime searches for proofs.** In Prolog one declares `parent(tom, mary).` and rules like `ancestor(X, Y) :- parent(X, Y).`, then asks queries; the *how* belongs entirely to the engine. Logic programming is the purest case of **declarative** programming, stating what is true rather than what to do.

---

## Model 1: Same Problem, Four Ways

Count the vowels in a string. Run each approach and compare:

**Imperative — explicit state mutation:**
```python
s = "programming languages are fascinating"

count = 0
for ch in s:
    if ch in "aeiou":
        count = count + 1

print(f"Imperative count: {count}")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

**Object-oriented — encapsulated state:**
```python
s = "programming languages are fascinating"

class VowelCounter:
    VOWELS = set("aeiou")

    def __init__(self, text):
        self.text = text
        self._count = None  # lazy computation

    def count(self):
        if self._count is None:
            self._count = sum(1 for ch in self.text if ch in self.VOWELS)
        return self._count

    def __repr__(self):
        return f"VowelCounter({self.text!r}, count={self.count()})"

vc = VowelCounter(s)
print(f"OO count: {vc.count()}")
print(repr(vc))
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

**Functional — composition of pure functions:**
```python
from functools import reduce

s = "programming languages are fascinating"

# No variables mutated; each step is a pure function
is_vowel  = lambda ch: ch in "aeiou"
to_one    = lambda _: 1
add       = lambda a, b: a + b

count = reduce(add, map(to_one, filter(is_vowel, s)), 0)
print(f"Functional count: {count}")

# Even more compact with sum + generator:
count2 = sum(1 for ch in s if ch in "aeiou")
print(f"Comprehension count: {count2}")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

**Logic-style — simulate Prolog with constraint search:**
```python
# Python simulation of logic-style declarative counting
s = "programming languages are fascinating"

# "Facts" — vowel membership
vowels = {"a", "e", "i", "o", "u"}

# "Rule" — count is cardinality of {ch | ch in s AND vowel(ch)}
count = len({i: ch for i, ch in enumerate(s) if ch in vowels})
print(f"Logic-style count: {count}")

# More Prolog-like: unification via list comprehension
answer = [ch for ch in s if ch in vowels]
print(f"Witness list: {answer[:10]}... (length {len(answer)})")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

### Critical Thinking Questions

1. Identify the mutable state in each version (there may be none). Which versions could safely run on two halves of the string in parallel and add the results, and why?
2. The OO version wraps the same logic in a class with lazy computation. Name one situation where that wrapping pays for itself, and one where it is ceremony without benefit.
3. In the logic-style version, where is the loop? What does its absence tell you about who owns control flow in a declarative style?
4. Your team's language project must choose: mutable variables or immutable bindings (or both). List one implementation consequence of each choice for the *interpreter* you will build.

---

# Part II: Paradigms in the Wild

## 3. Multi-Paradigm Reality

**Pure paradigm languages are rare; blends are the norm.** Python is imperative and OO with a functional toolkit (`map`, `filter`, comprehensions, `lambda`). Java added lambdas and streams in 2014; JavaScript mixes prototypal objects with pervasive higher-order functions; Rust is imperative with functional pattern matching and an ownership discipline. The paradigm question for a designer is not *which one* but *which defaults*: what does the language make easy, and what does it make possible?

[[MC]]
A language guarantees that no value can ever be modified after creation and that functions may be stored in variables and passed as arguments. These two guarantees are the signatures of:
- ( ) The imperative paradigm
- ( ) The object-oriented paradigm
- (x) The functional paradigm
- ( ) The logic paradigm

[[MC]]
A program in language X cannot run a function until every argument is known. Language Y can pass a function as a value and call it later. The property that distinguishes Y from X is:
- ( ) Dynamic typing
- ( ) Object orientation
- (x) First-class functions
- ( ) Static scoping

---

## Model 2: Classify the Snippets

| Snippet | Paradigm signal |
|---------|-----------------|
| `account.deposit(50)` | ? |
| `x := x + 1` | ? |
| `(reduce + 0 prices)` | ? |
| `sibling(X,Y) :- parent(P,X), parent(P,Y).` | ? |

**Paradigm Detective — run this and read the clues:**
```python
snippets = [
    ("account.deposit(50)",                      "sends a message to an object"),
    ("x := x + 1",                              "named cell changes over time"),
    ("(reduce + 0 prices)",                      "function applied to function applied to list"),
    ("sibling(X,Y) :- parent(P,X), parent(P,Y)", "rule: X and Y share a parent"),
]

paradigm_hints = {
    "sends a message to an object":         "Object-Oriented",
    "named cell changes over time":         "Imperative",
    "function applied to function applied": "Functional",
    "rule: X and Y share a parent":         "Logic/Declarative",
}

for snippet, hint in snippets:
    for key, paradigm in paradigm_hints.items():
        if key in hint:
            print(f"  [{paradigm:20}] {snippet}")
            break
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

### Critical Thinking Questions

5. Classify each snippet and name the *single feature* that gave it away.
6. `account.deposit(50)` mutates state *and* sends a message to an object. Is OO a kind of imperative programming with better manners, or something fundamentally different? Take a team position.
7. Modern Python lets you write all four rows' ideas (the fourth via libraries). Does multi-paradigm flexibility help or hurt the *reader* of a program? Connect to tomorrow's topic, language evaluation criteria.

---

## Model 3: Paradigm Costs and Benefits

The choice of paradigm shapes what is easy and what is hard. Run this performance comparison:

```python
import time

data = list(range(1, 100001))
target = lambda x: x % 2 == 0

# Imperative
t0 = time.perf_counter()
result_imp = []
for x in data:
    if target(x):
        result_imp.append(x * x)
total_imp = sum(result_imp)
t1 = time.perf_counter()

# Functional (generator — lazy, low memory)
t2 = time.perf_counter()
total_func = sum(x*x for x in data if target(x))
t3 = time.perf_counter()

print(f"Imperative:  {total_imp}  ({(t1-t0)*1000:.2f} ms)")
print(f"Functional:  {total_func}  ({(t3-t2)*1000:.2f} ms)")
print(f"Same result? {total_imp == total_func}")

# Key observation: functional version never builds an intermediate list
import sys
imp_list_size = sys.getsizeof(result_imp)
print(f"Imperative list size in memory: {imp_list_size} bytes")
print(f"Functional generator: no intermediate list (lazy evaluation)")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

### Critical Thinking Questions

8. The functional version uses a generator expression. What does "lazy evaluation" mean in this context, and why does it save memory?
9. For a list of 100,000 elements, which approach do you expect to be faster? Run it and report your findings.
10. If you wanted to parallelize this computation across 4 CPU cores, which style (imperative or functional) is easier to split safely? Why?

---

# Part III: Synthesis and Practice

## 4. Exercises

1. *Paradigm translation.* Take the imperative vowel counter and rewrite it functionally in Python using `filter` and `len` with no assignment statements. Verify both produce identical results on three inputs.
2. *Blend audit.* Pick one language a teammate knows well and list which paradigm supplies its defaults and which paradigms are available on request, with one feature as evidence each.
3. *Design straw poll.* As a team, record a provisional decision for your future language: primary paradigm, mutability default, and whether functions are first-class. You may change it later; the exercise is having reasons now.
4. *Referential transparency test.* Write a Python function that violates referential transparency (its output depends on something other than its arguments). Then write a pure version. Explain what changed and why the pure version is easier to test.
5. *Paradigm mashup.* Write a Python program that uses all four paradigm styles to solve the same problem (filter even numbers, square them, sum). Use: imperative loop, class with method, `filter`/`map`/`reduce`, and a set comprehension. Show all four produce the same answer.

---

## Reflection Prompt

In your notebook: which paradigm fits the way *you* naturally think about problems, and which feels most foreign? Describe one problem from another course (mathematics, biology, economics) and which paradigm would express it most directly. Then: now that you have seen the cost/benefit tradeoffs, does your answer change when the problem needs to scale to millions of items?

---

## 5. Further Reading

- Douglas Thain. *Introduction to Compilers and Language Design*, Chapter 1.
- Peter Van Roy. "Programming Paradigms for Dummies: What Every Programmer Should Know" (2009, online). A famous map of the paradigm space.
- Shriram Krishnamurthi. *PLAI*, early chapters on the functional core.
- Rich Hickey. "Simple Made Easy" (Strange Loop 2011, YouTube). A functional programming designer's case for immutability.
