<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374-Fall2026/gh-pages/_pages/Activities/liascript-languageevaluation.md or locally via https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374-Fall2026/gh-pages/_pages/Activities/liascript-languageevaluation.md

import: https://raw.githubusercontent.com/liascript/CodeRunner/master/README.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

# Programming Paradigms, Evaluating Languages, and an Introduction to Functional Programming

Evaluating a programming language is a lot like evaluating a tool in a workshop: a hammer and a screwdriver are both "correct" tools, but which one you reach for depends entirely on what you are building.  No language is universally best; every language embodies a set of deliberate tradeoffs that make it excellent for some tasks and awkward for others.

Today has three parts, and they build on each other.  First we name the **paradigms**, the handful of fundamentally different stories languages tell about what a program *is*.  Then we develop a systematic, criteria-driven way to judge the tradeoffs those stories make, so you can choose languages wisely and design your own with open eyes.  Finally we open the door to the paradigm we are going to spend the next two sessions inside: **functional programming**, in the language where it is most nearly the only option.

## Learning Goals

By the end of this activity, you will be able to:

- Distinguish the major programming paradigms and say what each one treats as the fundamental unit of a program
- Define the four classical language evaluation criteria (readability, writability, reliability, cost) and explain how each is measured
- Identify specific language features (orthogonality, type checking, abstraction support, etc.) and predict their effect on each evaluation criterion
- Analyze code examples to detect orthogonality failures and explain the programmer confusion they produce
- Compare two languages on at least two evaluation criteria using concrete feature-level evidence rather than personal preference
- Apply the evaluation framework as a scorecard to justify design decisions for your own language project
- Read and write a first Scheme expression, and explain why a function can be bound to a name the same way a number can

> **Before You Begin:** This activity assumes you can:
> - Describe at least one high-level difference between a statically typed language (e.g., Java) and a dynamically typed language (e.g., Python)
> - Read and run basic Python code (loops, functions, exceptions, list comprehensions)
> - Explain in plain English what a runtime error is and how it differs from a compile-time error
>
> If any of these feel shaky, review them first.

"Which language is best?" is a bad question; "best *for what*, judged *by what criteria*" is an engineering question.  Today we adopt the classical evaluation framework (readability, writability, reliability, and cost) and the design tradeoffs that connect them, because every choice your team makes in December will trade one criterion against another.  We move today from **the paradigms $\rightarrow$ the criteria $\rightarrow$ the design features that drive them $\rightarrow$ tradeoffs in real languages $\rightarrow$ a first look at the functional paradigm in Scheme**.

---

## Directions and Group Roles

Work in your POGIL team with your rotated roles (**Manager**, **Recorder**, **Presenter**, **Reflector**).  Please think each model and question through on your own first, then talk it over with your group.  The Recorder posts your answers to the Class Activity Questions discussion board, and the Presenter reports out wherever you disagreed or found another approach.  After class, please respond to the reflective prompt on your own in your notebook.

> **How today runs.**  Three parts in seventy-five minutes means the clock is real.  Part I (paradigms) takes about fifteen minutes, Part II and Part III (the criteria and the tradeoffs) take about thirty together, and Part V (your first Scheme) takes the last twenty and is the one I will not cut, because the next two sessions depend on you having typed something.  If we run short, **Model 1's Try It Yourself block and all of Model 2 are read-at-home**: they are worth your time, but the criteria in Part II carry the point without them, and the *Evaluating Languages and Paradigms* participation exercise walks the same ground.

---

# Part I: Four Paradigms

## 0.  What a Program *Is*

A **paradigm** is not a syntax family; it is a claim about what the fundamental unit of a program is.  Change that claim and everything downstream changes: what you name, what you can reuse, what kinds of bugs you get, and what the language has to work hardest to support.

| Paradigm | A program is... | The unit you build with | Where you have met it |
|---|---|---|---|
| **Imperative / procedural** | a sequence of commands that change state | the statement, the variable, the procedure | C, and most of the Python you have written |
| **Object-oriented** | a society of objects exchanging messages | the class, the object, the method | Java, C++, and Python's other half |
| **Functional** | an expression to be evaluated | the function, applied to values | Scheme, Haskell, and the `map`/`filter`/`lambda` corner of every modern language |
| **Logic / declarative** | a set of facts and rules, plus a question | the relation and the query | Prolog, SQL, and the type checker you will write in November |

Most languages you will use are mixtures.  That is the interesting part: Python has objects *and* closures *and* comprehensions, and every one of those was borrowed from a paradigm that took it seriously first.  Knowing which paradigm a feature came from tells you what it is for.

## Model 1: The Same Problem, Four Ways

One task, stated four ways: given a list of numbers, add up the squares of the even ones.

```python
data = [1, 2, 3, 4, 5, 6, 7, 8]

# 1. IMPERATIVE: a sequence of commands that mutate state.
#    The accumulator is the point; the answer accumulates in it.
total = 0
for n in data:
    if n % 2 == 0:
        total = total + n * n
print(f"  imperative:      {total}")

# 2. OBJECT-ORIENTED: state and behavior packaged together.
#    The object owns the running total and knows how to update it.
class EvenSquareSummer:
    def __init__(self):
        self.total = 0
    def offer(self, n):
        if n % 2 == 0:
            self.total += n * n
        return self

summer = EvenSquareSummer()
for n in data:
    summer.offer(n)
print(f"  object-oriented: {summer.total}")

# 3. FUNCTIONAL: an expression, evaluated. No variable is ever updated.
from functools import reduce
print(f"  functional:      "
      f"{reduce(lambda a, b: a + b, map(lambda n: n * n, filter(lambda n: n % 2 == 0, data)), 0)}")

# 4. DECLARATIVE: say WHAT you want and let the machinery find it.
#    Python's comprehension is a small, tame version of the same idea;
#    in SQL or Prolog the machinery does considerably more work for you.
print(f"  declarative:     {sum(n * n for n in data if n % 2 == 0)}")

print()
print("  Four answers, one number.  What differs is not the result but what")
print("  each version asks YOU to keep track of: an accumulator, an object,")
print("  a pipeline of functions, or nothing at all.")
```
@LIA.eval(`["main.py"]`, `none`, `python3 main.py`)

### Reading the Code

- Versions 1 and 2 both maintain a running total that changes over time.  If two threads ran either one, you would have to think about it.  Versions 3 and 4 never update anything, which is the property we will chase for the next two sessions.
- Version 3 is deliberately written the ugly way, with explicit `lambda`s, so you can see the three separate jobs: select, transform, combine.  Those three jobs have names (`filter`, `map`, `reduce`), and by the end of the functional sessions you will reach for them without thinking.
- Version 4 is the shortest and hides the most.  Hiding machinery is what "declarative" means, and it is a tradeoff, not a free win: ask anyone who has tried to make a slow SQL query fast.

### Critical Thinking Questions

1.  What are some potential advantages of Functional Programming as a paradigm?
2.  Which of the four versions would be easiest to test in isolation, and why?  Which would be hardest to debug when it produced the wrong number?
3.  Rewrite version 1 so that it computes the sum of the *odd* squares.  Now do the same for version 3.  Which edit was more localized, and what does that tell you about where each paradigm puts the "select" decision?
4.  Name a task where the imperative version is clearly the right one to write.  Paradigm choice is engineering, not fashion.

---

# Part II: The Criteria

## 1.  Four Lenses

Before diving into definitions, consider why we need multiple lenses at all.  When you argue that "Python is better than Java," you are almost certainly weighting one criterion heavily and ignoring others.  The four lenses below give you a shared vocabulary so that design debates become precise: instead of "I like Python better," you can say "Python trades static-typing reliability for writability speed, which is the right call for this domain."

**Readability** is the ease with which programs can be read and understood, and it dominates total cost because code is read far more often than written.  It is driven by *simplicity* (few constructs, few ways to do one thing), *orthogonality* (a small set of features combinable without special cases), and *syntax design* (meaningful keywords, consistent forms).

**Writability** is the ease of creating programs: *expressivity* (powerful, concise operations like list comprehensions), *abstraction support* (functions, classes, modules), and fit between the language and the problem domain.

**Reliability** is the likelihood that programs behave as intended: *type checking* (catching misuse early), *exception handling*, *aliasing restrictions* (fewer ways for two names to surprise you by referring to one cell), and, foundationally, readability and writability themselves, since code that is hard to read hides its bugs.

**Cost** totals the lifecycle: training, writing, compiling, executing, maintaining, and the price of unreliability.  A language fast to write but cryptic to read shifts cost from author to maintainer; a language with heavyweight checking shifts cost from runtime failures to compile-time friction.

---

## Model 2: Orthogonality, Combining Features Without Surprises

Imagine a language where every operator works on every type in a consistent, predictable way: no surprise exceptions, no "well, `+` works on strings but `*` only works on strings with integers, not with other strings."  That ideal is called orthogonality.  In practice, every real language falls short of it somewhere, and the gaps are exactly where programmers make mental-model mistakes.  This model makes those gaps visible by running operator experiments directly.

> **Watch out!**  Students often conflate orthogonality with "the feature exists."  The question is not whether Python supports string repetition (`"ha" * 3`) but whether the same rule applies uniformly everywhere.  When you find a case where it does not, that is a special case the programmer must memorize, a direct hit on readability.

**Orthogonality** means that a small set of primitives can be combined uniformly: adding a new feature does not require dozens of special cases for where it *cannot* be used.  C is famously non-orthogonal: you can have a pointer to a struct, a pointer to a function, an array of structs, but you cannot pass an array by value, return an array from a function, or use `==` to compare two structs.  Python is more orthogonal (everything is an object, `+` works on many types) but still has asymmetries.

The cell below catalogs several "does it combine?" experiments so your team can observe orthogonality failures directly.

```python
print("=== Python Orthogonality Probe ===")
print()

# '+' on different types
for a, b in [(1, 2), (1.0, 2.0), ("a", "b"), ([1], [2])]:
    try:
        result = a + b
        print(f"  {type(a).__name__} + {type(b).__name__} = {result!r}   OK")
    except TypeError as e:
        print(f"  {type(a).__name__} + {type(b).__name__} -> TypeError: {e}  FAIL")

print()

# '*' on different types (non-orthogonal: str*int works, list*list doesn't)
for a, b in [(3, 4), (3.0, 4.0), ("ha", 3), ([1, 2], 3), ([1, 2], [3, 4])]:
    try:
        result = a * b
        print(f"  {type(a).__name__} * {type(b).__name__} = {result!r}   OK")
    except TypeError as e:
        print(f"  {type(a).__name__} * {type(b).__name__} -> TypeError: {e}  FAIL")

print()
print("=== '==' Comparison Orthogonality ===")
# Python lets you compare almost anything with ==, even different types
# (never raises, but result may surprise)
comparisons = [
    (1, 1), (1, 1.0), (1, "1"), ([], []), ({}, {}), (None, False), (0, False)
]
for a, b in comparisons:
    result = (a == b)
    print(f"  {a!r} == {b!r}  ->  {result}")

print()
print("=== Container + Operator Asymmetry ===")
# sets use | for union, not +
s1, s2 = {1, 2}, {2, 3}
print(f"  set | set = {s1 | s2}   (union)  OK")
try:
    _ = s1 + s2
except TypeError as e:
    print(f"  set + set -> TypeError: {e}  FAIL")

# dicts: | works in Python 3.9+, + does not
d1, d2 = {"a": 1}, {"b": 2}
try:
    merged = d1 | d2
    print(f"  dict | dict = {merged}  OK")
except TypeError as e:
    print(f"  dict | dict -> TypeError: {e}  FAIL")
try:
    _ = d1 + d2
except TypeError as e:
    print(f"  dict + dict -> TypeError: {e}  FAIL")
```
@LIA.eval(`["main.py"]`, `none`, `python3 main.py`)

### Reading the Code

- Orthogonality is the property that features combine without special cases.  Each probe pairs one operator with several operand types and asks whether the rule generalizes; where it does not, you have found a wart.
- `+` on strings and on lists both mean "concatenate", which is orthogonal.  `*` means "repeat" for a string and an integer and has no meaning for two lists, which is not.  That inconsistency is the finding.
- `==` never raises, whatever you compare.  Convenient, and also why a typo comparing two different types fails silently rather than loudly: a reliability cost paid for a writability gain.
- Sets use `|` for union while lists use `+` for concatenation, so two collection types spell the same idea differently.  Every such difference is one more thing a reader has to hold in their head.

### Try It Yourself

Audit a corner of Python for orthogonality and score what you find against the four criteria.

```python
def probe(label, thunk):
    try:
        print("  " + label.ljust(26) + " -> " + repr(thunk()))
    except Exception as e:
        print("  " + label.ljust(26) + " -> " + type(e).__name__ + ": " + str(e))

print("=== Does 'in' mean the same thing everywhere? ===")
probe("3 in [1,2,3]",    lambda: 3 in [1, 2, 3])
probe("'a' in 'cat'",    lambda: "a" in "cat")
probe("'at' in 'cat'",   lambda: "at" in "cat")
probe("'a' in {'a': 1}", lambda: "a" in {"a": 1})
probe("1 in {'a': 1}",   lambda: 1 in {"a": 1})

# TODO 1: 'in' means "is an element" for a list, "is a SUBSTRING" for a
#         string, and "is a KEY" for a dict. Is that orthogonal? Which
#         criterion does the inconsistency serve, and which does it cost?

print("\n=== Does len() mean the same thing everywhere? ===")
for label, value in [("len('abc')", "abc"), ("len([1,2])", [1, 2]),
                     ("len({'a':1})", {"a": 1}), ("len((1,))", (1,))]:
    probe(label, lambda v=value: len(v))

# TODO 2: pick ONE more operator or built-in and probe it the same way.
#         Candidates: the * operator, slicing, or + on tuples versus sets.
#         Write four probes and report what you find.

# TODO 3: score your finding on all four criteria from Part I. A feature
#         that costs reliability and buys writability is a TRADE, not a
#         mistake. Say which trade Python made, and whether you would make
#         the same one in your language.
```
@LIA.eval(`["main.py"]`, `none`, `python3 main.py`)

Expected output: `'at' in 'cat'` is `True` while nothing analogous works for a list, and `1 in {'a': 1}` is `False` because `in` checks keys, not values.  Both are defensible; neither is orthogonal.

### Critical Thinking Questions

5.  From the output, identify two cases where Python *is* orthogonal (the same operator works uniformly across types) and two where it is *not*.  For each non-orthogonal case, state what the programmer must remember as a special case.
6.  Define orthogonality in your own words using these examples: which special cases break the "features combine uniformly" promise in each language?  Should `set + set` work?  Make an argument both ways using readability and reliability as criteria.
7.  A maximally orthogonal language sounds ideal.  Propose one danger of *too much* orthogonality (hint: if everything combines with everything, what can the reader assume about any expression?).
8.  Score C and Python (low/medium/high) on each of the four criteria for the task "a 200-line data cleaning script maintained by rotating student workers."  Defend your most contested cell.

---

# Check Your Understanding

Orthogonality means:

[(X)] Features combine without special cases, so a rule learned once applies everywhere
[( )] Every feature is independent of every other feature's implementation
[( )] The language has few features
[( )] Operators may not be overloaded

---

`"ab" * 3` works but `[1,2] * [3]` does not. That is:

[(X)] A failure of orthogonality: the operator generalizes over one pairing of types and not the analogous one
[( )] A type error, and nothing more
[( )] Evidence that Python is weakly typed
[( )] Correct, because repetition is undefined for lists

---

Writability and reliability frequently pull against each other because:

[(X)] Conveniences that let you say less also let you say something wrong without being told
[( )] Reliable languages are always slower
[( )] Writability requires dynamic typing
[( )] Reliability requires more keywords

---

Tony Hoare called null his "billion-dollar mistake" because:

[(X)] Making absence a value of every type means every dereference is a possible failure the type system never flags
[( )] Nulls are slow to check at run time
[( )] It forced garbage collection into the language
[( )] It made the parser ambiguous

---

# Part III: Tradeoffs

## 2.  There Is No Free Criterion

Part I gave you four lenses; Part II shows why you cannot maximize all four at once.  Every language design decision moves at least one criterion up and at least one criterion down; there is no free lunch.  As you read through the examples below, resist the instinct to call one choice "wrong."  Instead, ask: "Which criterion did the designer prioritize, and does that match the language's target use case?"

> **Watch out!**  It is tempting to conclude "Python is better than C because it has higher reliability."  That claim ignores context.  For a hard-real-time embedded system where memory layout matters, C's lower abstraction is a feature, not a bug.  Criteria scores are always relative to the problem domain, not absolute.

Reliability versus cost of execution.  Java checks every array index at runtime; C does not.  One buys memory safety with cycles; the other buys speed with vulnerability (buffer overflows remain a top security flaw class decades later).

**Writability versus readability.**  APL and Perl achieve astonishing concision; their critics call them write-only.  Python's design explicitly privileges the reader ("readability counts"), accepting more keystrokes.

**Flexibility versus reliability.**  Dynamic typing (Python) lets any variable hold anything, which speeds exploration and defers type errors to runtime, possibly in production.  Static typing (Java, Rust) front-loads the friction.  Modern designs hedge: type *inference* (the compiler deduces types you did not write) and *gradual typing* (Python's optional annotations) try to buy reliability without the ceremony.

> **Runnable version (at home).**  *Part III* below demonstrates four of these tradeoffs in executable Python (coercion, comprehensions, checked division, and duck typing), with its own questions.

A team adds implicit type coercion to their language so that `"3" + 4` yields `7`, reasoning that it improves writability.  The most likely cost, in this framework, is to:

[( )] Execution speed only
[(X)] Reliability, because errors that types would have caught now produce silently wrong values
[( )] Training cost only
[( )] Nothing; coercion is free

---

## Model 3: The Billion-Dollar Hindsight

One of the most studied reliability failures in language design history is the null reference: the idea that a variable of any type can silently hold "nothing," and that nothing will only explode when you try to use it, potentially deep inside code far from where the bad value was introduced.  This model walks through three different language-design responses to that problem, letting you directly compare the reliability-versus-writability tradeoffs each one makes.

Tony Hoare called the null reference his "billion-dollar mistake" in a 2009 keynote.  His argument: the null reference can be assigned to any pointer-typed variable and dereferenced into a crash, yet no type system of the era flagged the dereference as potentially unsafe.  The result: null dereferences became one of the most common runtime errors in Java, C, and C++. Languages have responded differently.

```python
# Simulating three language designs for the "absence" problem in Python.
# The point is to observe what each design forces the programmer to do.

print("=== Design 1: Implicit null (Java / C pre-Optional) ===")
print("  Null is a valid value of every reference type.")
print("  Dereference crashes at runtime, possibly far from the assignment.")

def find_user_java_style(db, user_id):
    """Returns a dict or None - caller MUST check but nothing forces them to."""
    return db.get(user_id)   # returns None if not found

db = {"alice": {"age": 30}}

user = find_user_java_style(db, "alice")
print(f"  alice found: {user['age']} years old")

user = find_user_java_style(db, "bob")
# The following would crash silently - representing Java-style null deref:
try:
    print(f"  bob's age: {user['age']}")  # NullPointerException equivalent
except TypeError as e:
    print(f"  bob lookup -> crash: {e}  (the null dereference)")

print()
print("=== Design 2: Optional type (Kotlin / Swift / Rust Option) ===")
print("  Absence is a separate type; the compiler forces you to unwrap.")

# Simulated with Python's Optional pattern
from typing import Optional

def find_user_optional(db, user_id) -> Optional[dict]:
    return db.get(user_id)

def get_age_safe(db, user_id) -> Optional[int]:
    user = find_user_optional(db, user_id)
    if user is None:
        return None          # explicit, visible propagation
    return user.get("age")  # safe: only reached when user exists

for uid in ["alice", "bob"]:
    age = get_age_safe(db, uid)
    if age is None:
        print(f"  {uid}: not found or no age (handled explicitly)")
    else:
        print(f"  {uid}: {age} years old")

print()
print("=== Design 3: No null; absence requires a sum type ===")
# Simulate Rust's Result/Option with a tiny class
class Option:
    def __init__(self, value=None, present=True):
        self._value = value
        self._present = present

    @staticmethod
    def Some(v): return Option(v, True)

    @staticmethod
    def Nothing(): return Option(None, False)

    def unwrap(self):
        if not self._present:
            raise ValueError("Called unwrap() on Nothing - explicit error, not a crash")
        return self._value

    def unwrap_or(self, default):
        return self._value if self._present else default

    def __repr__(self):
        return f"Some({self._value!r})" if self._present else "Nothing"

def find_user_rust_style(db, user_id) -> Option:
    val = db.get(user_id)
    return Option.Some(val) if val is not None else Option.Nothing()

for uid in ["alice", "bob"]:
    result = find_user_rust_style(db, uid)
    print(f"  {uid}: {result}")
    # Must explicitly handle both cases:
    age = result.unwrap_or({}).get("age", "unknown")
    print(f"  {uid} age: {age}")

print()
print("=== Summary ===")
print("  Design 1 (implicit null): min ceremony, max crash risk")
print("  Design 2 (Optional type): moderate ceremony, compiler-assisted")
print("  Design 3 (no null):       max ceremony, compiler-guaranteed safety")
```
@LIA.eval(`["main.py"]`, `none`, `python3 main.py`)

### Critical Thinking Questions

9.  Express each of the three designs as a position in the reliability-versus-writability tradeoff.  Which shifts the cost of absence-handling earliest: to the programmer at write time, to the compiler at compile time, or to the user at run time?
10.  Your project language will have to decide what happens when a variable is used before assignment.  Enumerate three possible designs (error at parse time, error at run time, default value) and score each on reliability and writability.  Which does Python use?  Which does Java use?
11.  Hoare's mistake survived fifty years because it was *convenient*.  Name one convenience in a language you use that you now suspect is somebody's future billion-dollar regret.  Use the four criteria to defend your suspicion.

---


> **Cut for time.**  The simplicity-versus-expressiveness comparison (including the Perl-golf demonstration) added length without adding a criterion beyond the four lenses in Part I. The point it made (that terseness and clarity are different axes, and that a language can optimize for either) is covered in Model 1's orthogonality discussion.

# Part IV: A First Look at the Functional Paradigm

## 3.  Scheme, Where the Paradigm Is Not Optional

Version 3 of Model 1 was functional programming wearing a Python costume: you can write in that style, but nothing makes you, and the language will happily let you reach for a loop and an accumulator instead.  To feel a paradigm properly you have to spend time somewhere it is the *only* option.  For the next two sessions that place is **Scheme**.

Scheme is to programming languages what Latin is to the Romance languages: it exposes the undiluted core the others are built from, stripped of the ornamental syntax that usually hides the machinery.  It has essentially **one syntactic rule**: everything is a parenthesized list with the operator first.

| Python | Scheme |
|---|---|
| `f(a, b)` | `(f a b)` |
| `2 + 3` | `(+ 2 3)` |
| `(2 + 3) * 4` | `(* (+ 2 3) 4)` |
| `[1, 2, 3]` | `'(1 2 3)` |
| `def f(x): return x + 1` | `(define (f x) (+ x 1))` |

There is no precedence table, because prefix notation does not need one: the nesting *is* the structure.  Hold onto that.  In a few weeks this course spends three sessions building a parser whose entire job is to recover, from flat infix text like `2 + 3 * 4`, the tree a Scheme programmer simply writes.

## Model 4: Your First Scheme

Get a REPL in front of you before you read the code.  [try.scheme.org](https://try.scheme.org) needs no install and works in a browser tab; the course's own [Scheme warmup exercise](https://www.billmongan.com/Ursinus-CS374-Fall2026/Modules/Scheme/Warmup/Exercise) runs Scheme in the page and checks your answer.  If you would rather install it locally, the *Functional Programming in Scheme* activity opens with four routes, and the Scheme assignment walks all of them.

```scheme
(define L (list 'a 'b 'c))
(car L)                      ; a
(cdr L)                      ; (b c)

(define x (+ 3 2))
(+ x 5)                      ; 10

(define add +)
(add 3 2)                    ; 5
```

### Reading the Code

- `car` gives you the first element of a list and `cdr` gives you everything after it.  The names are historical accidents from 1950s IBM register names and they are not going to start making sense, so read them as "the first one" and "the rest."  Those two operations, plus recursion, are the entire engine of list processing in this language.
- `(define x (+ 3 2))` binds the name `x` to the value 5.  Note the word: **binds**, not assigns.  You do not come back later and update `x`.  That single discipline is what makes the functional paradigm's promises (testability, safe parallelism) possible.
- `(define add +)` is not a typo.  `+` is a *value*, the addition function, and `define` gives it a second name.  Nothing in Scheme distinguishes a name holding a number from a name holding a function.

> **Watch out!**  Forgetting the quote before a list literal is the most common beginner error in this language.  `(1 2 3)` tells Scheme to call the function named `1` with arguments `2` and `3`, and since `1` is not a function you get `application: not a procedure`.  Write `'(1 2 3)` when you mean data.  Trigger the error on purpose once, right now, and read the message: it is the One Syntax Rule explaining itself.

### Critical Thinking Questions

15.  Translate `2 + 3 * 4` and `(2 + 3) * 4` into Scheme.  Which one needed parentheses beyond the operators' own, and why does the question almost stop making sense?
16.  `(define add +)` works in Scheme.  What is the nearest Python equivalent, and is there anything Scheme lets you do here that Python does not?
17.  Score Scheme's one-syntax-rule uniformity against all four criteria from Part II.  Ask anyone who has counted parentheses before you decide readability is a clean win.

### Try It Yourself

Before the next session: get a REPL open, type the three blocks above, and then write `(define double (lambda (n) (* n 2)))` and call it.  Bring the one expression that would not evaluate.  Debugging in the REPL is the exercise, and next session assumes you have already met the parentheses.

---

# Part V: Synthesis and Practice

## Runnable: Four Feature Choices, Measured on Both Axes (At Home)

```python
# Concrete illustration of the writability-reliability tradeoff.
# Four "feature choices" measured on both axes.

print("=== Implicit Type Coercion (writability UP, reliability DOWN) ===")
# Python refuses; JavaScript would silently convert
try:
    result = "3" + 4     # TypeError in Python; would be "34" in JS
    print(f"  '3' + 4 = {result!r}")
except TypeError as e:
    print(f"  Python refuses '3' + 4: {e}")
    print("  JavaScript would give '34' (string concat) - silent wrong type")

print()
print("=== List Comprehensions (writability UP, readability tradeoff) ===")
# Three ways to build squares of evens 0..9
# Option 1: verbose loop (high readability to beginners)
result_loop = []
for x in range(10):
    if x % 2 == 0:
        result_loop.append(x ** 2)

# Option 2: comprehension (concise, rewards fluency)
result_comp = [x ** 2 for x in range(10) if x % 2 == 0]

# Option 3: functional pipeline (composable, unfamiliar to imperative readers)
result_func = list(map(lambda x: x**2, filter(lambda x: x % 2 == 0, range(10))))

print(f"  Loop:          {result_loop}")
print(f"  Comprehension: {result_comp}")
print(f"  Functional:    {result_func}")
print("  Same answer, different readability/writability profiles")

print()
print("=== Exception Handling (reliability UP, writability cost) ===")
def safe_divide(a, b):
    """Checked division: reliability over brevity."""
    if not isinstance(a, (int, float)):
        raise TypeError(f"Expected number, got {type(a).__name__}")
    if not isinstance(b, (int, float)):
        raise TypeError(f"Expected number, got {type(b).__name__}")
    if b == 0:
        raise ZeroDivisionError("Cannot divide by zero")
    return a / b

def unsafe_divide(a, b):
    """Unchecked: writability over reliability."""
    return a / b

for a, b in [(10, 2), (10, 0), ("10", 2)]:
    try:
        print(f"  safe_divide({a!r}, {b!r}) = {safe_divide(a, b)}")
    except (TypeError, ZeroDivisionError) as e:
        print(f"  safe_divide({a!r}, {b!r}) -> {type(e).__name__}: {e}")
    try:
        print(f"  unsafe_divide({a!r}, {b!r}) = {unsafe_divide(a, b)}")
    except Exception as e:
        print(f"  unsafe_divide({a!r}, {b!r}) -> {type(e).__name__}: {e}")

print()
print("=== Dynamic Dispatch (writability UP, reliability cost) ===")
# Duck typing: no interface required, but caller has no guarantee
class Duck:
    def sound(self): return "quack"

class Dog:
    def sound(self): return "woof"

class Rock:
    pass   # no 'sound' method

def make_sound(thing):
    """Works if thing has .sound(); crashes at runtime otherwise."""
    return thing.sound()

for obj in [Duck(), Dog(), Rock()]:
    try:
        print(f"  {type(obj).__name__}.sound() = {make_sound(obj)!r}")
    except AttributeError as e:
        print(f"  {type(obj).__name__}.sound() -> AttributeError: {e}")
```
@LIA.eval(`["main.py"]`, `none`, `python3 main.py`)

### Critical Thinking Questions

12.  For each of the four "feature choices" in the cell, identify which criterion it improves and which it weakens, using the vocabulary (readability/writability/reliability/cost).
13.  The list comprehension and `for`-loop produce identical results.  A new programmer finds the loop more readable; an experienced Python programmer finds the comprehension more readable.  What does this asymmetry reveal about readability as a criterion: is it absolute or relative to the reader?
14.  Duck typing (`make_sound`) defers the `Rock` error until `make_sound(Rock())` is actually called.  In a large program, how far might that call be from the assignment `thing = Rock()`?  Connect this to the "hidden path" problem from the types module.


## 4.  Exercises

1.  *Criteria audit.*  Choose one feature of a language you know (Python indentation blocks, Java checked exceptions, C pointers, JavaScript `==` coercion).  Write a half-page evaluation through all four lenses, ending with a verdict: keep, modify, or remove, and why.
2.  *Scorecard draft.*  Create your team's language-design scorecard: the four criteria as rows, with a sentence per row stating what your language will prioritize and what it will knowingly sacrifice.  This scorecard reappears in your project proposal.
3.  *Holy war defusal.*  Find one online "language X versus Y" argument and translate its two loudest claims into this framework.  Does the disagreement survive translation, or does it dissolve into different weightings of the same criteria?
4.  *Null policy.*  Write a 150-word statement for your project's SEMANTICS.md documenting your language's policy on absent values: what type/value represents absence, what happens when the programmer dereferences it, and which of the three designs from Model 3 you are choosing and why.
5.  *Coercion matrix.*  Build a 4×4 matrix (types: int, float, string, bool) showing which of the 16 pairwise `+` operations your language will allow, which will coerce, and which will error.  For each allowed coercion, state the reliability risk.

---

## Reflection Prompt

In your notebook: recall the language feature that most confused you as a beginning programmer.  Through today's lenses, was the confusion a readability failure, a reliability failure, or a teaching failure?  What would you change?  Now that you are about to design your own language in December, which of the four criteria do you find yourself valuing *more* than you expected before this course began?

---

## 5.  Further Reading

- Douglas Thain.  *Introduction to Compilers and Language Design*, Chapter 1.
- Robert Sebesta.  *Concepts of Programming Languages*, Chapter 1 (the canonical source of this framework; any edition, library reserve).
- Tony Hoare.  "Null References: The Billion Dollar Mistake" (talk, 2009, online).
- Python PEP 20, "The Zen of Python": `import this` in any Python interpreter.
- Gary Bernhardt.  "Wat" (talk, 2012, online): four minutes of coercion comedy with a serious lesson.
- [Prolog in the Browser with SWISH](https://www.billmongan.com/Ursinus-CS374-Fall2026/Tutorials/Prolog): logic programming, covering family-tree facts and rules, Robinson unification, SLD resolution and backtracking, bidirectional list predicates, a complete mini-Prolog interpreter in Python, and the miniKanren connection.  Backs Direction F of the Functional assignment.

---

Up next: *Functional Programming in Scheme, Part 2*, where we stay in the parentheses long enough for them to stop being strange, and write the recursion, composition, and closures that the paradigm is actually made of.
