# Evaluating Languages: Readability, Writability, Reliability
<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://github.com/BillJr99/Ursinus-CS374-Fall2026/blob/gh-pages/_pages/Activities/liascript-languageevaluation.md or locally via https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374/gh-pages/_pages/Activities/liascript-languageevaluation.md

import: https://raw.githubusercontent.com/liascript/CodeRunner/master/README.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

# Evaluating Languages: Readability, Writability, Reliability

"Which language is best?" is a bad question; "best *for what*, judged *by what criteria*" is an engineering question. Today we adopt the classical evaluation framework (readability, writability, reliability, and cost) and the design tradeoffs that connect them, because every choice your team makes in December will trade one criterion against another. The arc: **the criteria $\rightarrow$ the design features that drive them $\rightarrow$ tradeoffs in real languages $\rightarrow$ a scorecard for your own design**.

---

## Directions and Group Roles

Work in your POGIL team with rotated roles (**Manager**, **Recorder**, **Presenter**, **Reflector**). Consider each model and question individually first, then discuss with your group. The Recorder posts answers to the Class Activity Questions discussion board; the Presenter reports out areas of disagreement or alternative approaches. After class, respond to the reflective prompt individually in your notebook.

---

# Part I: The Criteria

## 1. Four Lenses

**Readability** is the ease with which programs can be read and understood, and it dominates total cost because code is read far more often than written. It is driven by *simplicity* (few constructs, few ways to do one thing), *orthogonality* (a small set of features combinable without special cases), and *syntax design* (meaningful keywords, consistent forms).

**Writability** is the ease of creating programs: *expressivity* (powerful, concise operations like list comprehensions), *abstraction support* (functions, classes, modules), and fit between the language and the problem domain.

**Reliability** is the likelihood that programs behave as intended: *type checking* (catching misuse early), *exception handling*, *aliasing restrictions* (fewer ways for two names to surprise you by referring to one cell), and, foundationally, readability and writability themselves, since code that is hard to read hides its bugs.

**Cost** totals the lifecycle: training, writing, compiling, executing, maintaining, and the price of unreliability. A language fast to write but cryptic to read shifts cost from author to maintainer; a language with heavyweight checking shifts cost from runtime failures to compile-time friction.

---

## Model 1: Orthogonality — Combining Features Without Surprises

**Orthogonality** means that a small set of primitives can be combined uniformly: adding a new feature does not require dozens of special cases for where it *cannot* be used. C is famously non-orthogonal: you can have a pointer to a struct, a pointer to a function, an array of structs — but you cannot pass an array by value, return an array from a function, or use `==` to compare two structs. Python is more orthogonal (everything is an object, `+` works on many types) but still has asymmetries.

The cell below catalogs several "does it combine?" experiments so your team can observe orthogonality failures directly.

```python
print("=== Python Orthogonality Probe ===")
print()

# '+' on different types
for a, b in [(1, 2), (1.0, 2.0), ("a", "b"), ([1], [2])]:
    try:
        result = a + b
        print(f"  {type(a).__name__} + {type(b).__name__} = {result!r}   ✓")
    except TypeError as e:
        print(f"  {type(a).__name__} + {type(b).__name__} → TypeError: {e}  ✗")

print()

# '*' on different types (non-orthogonal: str*int works, list*list doesn't)
for a, b in [(3, 4), (3.0, 4.0), ("ha", 3), ([1, 2], 3), ([1, 2], [3, 4])]:
    try:
        result = a * b
        print(f"  {type(a).__name__} * {type(b).__name__} = {result!r}   ✓")
    except TypeError as e:
        print(f"  {type(a).__name__} * {type(b).__name__} → TypeError: {e}  ✗")

print()
print("=== '==' Comparison Orthogonality ===")
# Python lets you compare almost anything with ==, even different types
# (never raises, but result may surprise)
comparisons = [
    (1, 1), (1, 1.0), (1, "1"), ([], []), ({}, {}), (None, False), (0, False)
]
for a, b in comparisons:
    result = (a == b)
    print(f"  {a!r} == {b!r}  →  {result}")

print()
print("=== Container + Operator Asymmetry ===")
# sets use | for union, not +
s1, s2 = {1, 2}, {2, 3}
print(f"  set | set = {s1 | s2}   (union)  ✓")
try:
    _ = s1 + s2
except TypeError as e:
    print(f"  set + set → TypeError: {e}  ✗")

# dicts: | works in Python 3.9+, + does not
d1, d2 = {"a": 1}, {"b": 2}
try:
    merged = d1 | d2
    print(f"  dict | dict = {merged}  ✓")
except TypeError as e:
    print(f"  dict | dict → TypeError: {e}  ✗")
try:
    _ = d1 + d2
except TypeError as e:
    print(f"  dict + dict → TypeError: {e}  ✗")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

### Critical Thinking Questions

1. From the output, identify two cases where Python *is* orthogonal (the same operator works uniformly across types) and two where it is *not*. For each non-orthogonal case, state what the programmer must remember as a special case.
2. Define orthogonality in your own words using these examples: which special cases break the "features combine uniformly" promise in each language? Should `set + set` work? Make an argument both ways using readability and reliability as criteria.
3. A maximally orthogonal language sounds ideal. Propose one danger of *too much* orthogonality (hint: if everything combines with everything, what can the reader assume about any expression?).
4. Score C and Python (low/medium/high) on each of the four criteria for the task "a 200-line data cleaning script maintained by rotating student workers." Defend your most contested cell.

---

# Part II: Tradeoffs

## 2. There Is No Free Criterion

**Reliability versus cost of execution.** Java checks every array index at runtime; C does not. One buys memory safety with cycles; the other buys speed with vulnerability (buffer overflows remain a top security flaw class decades later).

**Writability versus readability.** APL and Perl achieve astonishing concision; their critics call them write-only. Python's design explicitly privileges the reader ("readability counts"), accepting more keystrokes.

**Flexibility versus reliability.** Dynamic typing (Python) lets any variable hold anything, which speeds exploration and defers type errors to runtime, possibly in production. Static typing (Java, Rust) front-loads the friction. Modern designs hedge: type *inference* (the compiler deduces types you did not write) and *gradual typing* (Python's optional annotations) try to buy reliability without the ceremony.

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
    print("  JavaScript would give '34' (string concat) — silent wrong type")

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
        print(f"  safe_divide({a!r}, {b!r}) → {type(e).__name__}: {e}")
    try:
        print(f"  unsafe_divide({a!r}, {b!r}) = {unsafe_divide(a, b)}")
    except Exception as e:
        print(f"  unsafe_divide({a!r}, {b!r}) → {type(e).__name__}: {e}")

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
        print(f"  {type(obj).__name__}.sound() → AttributeError: {e}")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

### Critical Thinking Questions

5. For each of the four "feature choices" in the cell, identify which criterion it improves and which it weakens, using the vocabulary (readability/writability/reliability/cost).
6. The list comprehension and `for`-loop produce identical results. A new programmer finds the loop more readable; an experienced Python programmer finds the comprehension more readable. What does this asymmetry reveal about readability as a criterion — is it absolute or relative to the reader?
7. Duck typing (`make_sound`) defers the `Rock` error until `make_sound(Rock())` is actually called. In a large program, how far might that call be from the assignment `thing = Rock()`? Connect this to the "hidden path" problem from the types module.

[[MC]]
A team adds implicit type coercion to their language so that `"3" + 4` yields `7`, reasoning that it improves writability. The most likely cost, in this framework, is to:
- ( ) Execution speed only
- (x) Reliability, because errors that types would have caught now produce silently wrong values
- ( ) Training cost only
- ( ) Nothing; coercion is free

---

## Model 2: The Billion-Dollar Hindsight

Tony Hoare called the null reference his "billion-dollar mistake" in a 2009 keynote. His argument: the null reference can be assigned to any pointer-typed variable and dereferenced into a crash, yet no type system of the era flagged the dereference as potentially unsafe. The result: null dereferences became one of the most common runtime errors in Java, C, and C++. Languages have responded differently.

```python
# Simulating three language designs for the "absence" problem in Python.
# The point is to observe what each design forces the programmer to do.

print("=== Design 1: Implicit null (Java / C pre-Optional) ===")
print("  Null is a valid value of every reference type.")
print("  Dereference crashes at runtime, possibly far from the assignment.")

def find_user_java_style(db, user_id):
    """Returns a dict or None — caller MUST check but nothing forces them to."""
    return db.get(user_id)   # returns None if not found

db = {"alice": {"age": 30}}

user = find_user_java_style(db, "alice")
print(f"  alice found: {user['age']} years old")

user = find_user_java_style(db, "bob")
# The following would crash silently — representing Java-style null deref:
try:
    print(f"  bob's age: {user['age']}")  # NullPointerException equivalent
except TypeError as e:
    print(f"  bob lookup → crash: {e}  (the null dereference)")

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
            raise ValueError("Called unwrap() on Nothing — explicit error, not a crash")
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
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

### Critical Thinking Questions

8. Express each of the three designs as a position in the reliability-versus-writability tradeoff. Which shifts the cost of absence-handling earliest — to the programmer at write time, to the compiler at compile time, or to the user at run time?
9. Your project language will have to decide what happens when a variable is used before assignment. Enumerate three possible designs (error at parse time, error at run time, default value) and score each on reliability and writability. Which does Python use? Which does Java use?
10. Hoare's mistake survived fifty years because it was *convenient*. Name one convenience in a language you use that you now suspect is somebody's future billion-dollar regret. Use the four criteria to defend your suspicion.

---

## Model 3: Simplicity vs Expressiveness — Counting the Ways

One dimension of readability is the number of ways a language provides to do the same thing. More ways can improve writability (each programmer uses their preferred style) but harm readability (the reader must recognize all styles). The cell below counts several ways to sum a list in Python to make this concrete.

```python
nums = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
target = sum(nums)  # 55

print("=== Six ways to sum a list ===")
print(f"  Target: {target}")
print()

# Way 1: built-in
r1 = sum(nums)
print(f"  1. sum(nums)                           = {r1}")

# Way 2: for loop
r2 = 0
for x in nums:
    r2 += x
print(f"  2. for loop with accumulator           = {r2}")

# Way 3: while loop
r3, i = 0, 0
while i < len(nums):
    r3 += nums[i]; i += 1
print(f"  3. while loop with index               = {r3}")

# Way 4: reduce
from functools import reduce
r4 = reduce(lambda a, b: a + b, nums)
print(f"  4. functools.reduce                    = {r4}")

# Way 5: generator expression
r5 = sum(x for x in nums)
print(f"  5. sum(generator)                      = {r5}")

# Way 6: recursion
def recursive_sum(lst):
    if not lst: return 0
    return lst[0] + recursive_sum(lst[1:])
r6 = recursive_sum(nums)
print(f"  6. recursion                           = {r6}")

print()
assert r1 == r2 == r3 == r4 == r5 == r6 == target
print("  All six agree. ✓")
print()

# Now: which is most readable? Force the team to vote.
print("=== APL — extreme concision, extreme opacity ===")
print("  APL would write: +/1 2 3 4 5  (read: reduce-add over the array)")
print("  Python's 'sum([1..10])' is longer but more readable to most humans.")
print()
print("  Question: who is 'most humans'? The answer depends on the reader's background.")
print()

# Perl golf (unrunnable, shown as string)
print("=== Perl one-liner (write-only) ===")
print("  perl -e 'print eval join(\"+\",1..10),\"\\n\"'")
print("  Produces 55, but requires knowing Perl's list and eval idioms.")
print()
print("=== Key insight ===")
print("  The 'number of ways' is a language design axis.")
print("  Perl/Ruby maximize it (TIMTOWTDI: There Is More Than One Way To Do It)")
print("  Python minimizes it (PEP 20: 'There should be one obvious way to do it')")
print("  Your language will land somewhere; mark your position deliberately.")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

### Critical Thinking Questions

11. Python's PEP 20 says "There should be one — and preferably only one — obvious way to do it." Yet Python provides *six* ways to sum a list (the cell above). Is this a contradiction or a pragmatic balance? What would Perl's TIMTOWTDI philosophy say?
12. For a *beginner* writing their first sum loop, which of the six methods is most readable, and which is most writable? Do your answers change for an experienced Python developer?
13. Rank the six methods on reliability: which is hardest to introduce an off-by-one error into, and why?

[[MC]]
Python's design philosophy ("There should be one obvious way to do it") prioritizes which criterion above all others?
- (x) Readability — fewer ways to express the same thing means readers encounter fewer patterns to learn
- ( ) Writability — one way is faster to type
- ( ) Reliability — one way reduces bugs
- ( ) Cost of compilation — fewer forms to parse

---

# Part III: Synthesis and Practice

## 4. Exercises

1. *Criteria audit.* Choose one feature of a language you know (Python indentation blocks, Java checked exceptions, C pointers, JavaScript `==` coercion). Write a half-page evaluation through all four lenses, ending with a verdict: keep, modify, or remove, and why.
2. *Scorecard draft.* Create your team's language-design scorecard: the four criteria as rows, with a sentence per row stating what your language will prioritize and what it will knowingly sacrifice. This scorecard reappears in your project proposal.
3. *Holy war defusal.* Find one online "language X versus Y" argument and translate its two loudest claims into this framework. Does the disagreement survive translation, or does it dissolve into different weightings of the same criteria?
4. *Null policy.* Write a 150-word statement for your project's SEMANTICS.md documenting your language's policy on absent values: what type/value represents absence, what happens when the programmer dereferences it, and which of the three designs from Model 2 you are choosing and why.
5. *Coercion matrix.* Build a 4×4 matrix (types: int, float, string, bool) showing which of the 16 pairwise `+` operations your language will allow, which will coerce, and which will error. For each allowed coercion, state the reliability risk.

---

## Reflection Prompt

In your notebook: recall the language feature that most confused you as a beginning programmer. Through today's lenses, was the confusion a readability failure, a reliability failure, or a teaching failure? What would you change? Now that you are about to design your own language in December, which of the four criteria do you find yourself valuing *more* than you expected before this course began?

---

## 5. Further Reading

- Douglas Thain. *Introduction to Compilers and Language Design*, Chapter 1.
- Robert Sebesta. *Concepts of Programming Languages*, Chapter 1 (the canonical source of this framework; any edition, library reserve).
- Tony Hoare. "Null References: The Billion Dollar Mistake" (talk, 2009, online).
- Python PEP 20 — "The Zen of Python": `import this` in any Python interpreter.
- Gary Bernhardt. "Wat" (talk, 2012, online): four minutes of coercion comedy with a serious lesson.
