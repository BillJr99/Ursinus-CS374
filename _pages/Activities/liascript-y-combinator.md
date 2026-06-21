# The Y Combinator: Self-Reference Without Names

<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://github.com/BillJr99/Ursinus-CS374-Fall2026/blob/main/_pages/Activities/liascript-y-combinator.md

import: https://raw.githubusercontent.com/liascript/CodeRunner/master/README.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

# The Y Combinator: Self-Reference Without Names

## Learning Goals

By the end of this activity, you will be able to:

- Explain why named self-reference is unavailable in the pure lambda calculus and why an anonymous recursive function requires a fixed-point operator
- Derive the Y combinator step by step from the self-application trick, tracing how each intermediate form eliminates a deficiency of the previous one
- Implement a working Y combinator in Python (using the Z combinator variant for strict evaluation) and use it to express factorial without `def` or assignment
- Define what it means for Y to be a fixed-point operator (`Y f = f (Y f)`) and verify this property by hand reduction
- Recognize the Y combinator pattern in real code (trampolined recursion, anonymous recursion idioms in JavaScript and Haskell)

*"The Y combinator is probably the most ingenious and least intuitive result in the lambda calculus."* — Pierce, *TAPL*

Every recursive function you have ever written calls itself by name: `factorial` calls `factorial`, `fib` calls `fib`. This seems obvious and necessary. But names are a feature of programming environments, not a feature of computation itself. The lambda calculus has no names — every definition is anonymous. So how do you write a recursive function when you cannot name it? How do you call a function you cannot refer to?

The answer is the **Y combinator**: a fixed-point operator that provides every function the gift of self-reference, without requiring a name. This module builds to Y from scratch — through a carefully designed sequence of wrong answers that teach the right intuition — and then shows Y at work in modern Python, JavaScript, and Haskell.

---

## 0. Prerequisites

You should know: lambda syntax, beta-reduction, function application (from the lambda calculus module), and Python lambdas.

```python
# Warm-up: confirm the recursive baseline
def factorial_named(n):
    return 1 if n == 0 else n * factorial_named(n - 1)   # named self-call

print([factorial_named(n) for n in range(8)])
# [1, 1, 2, 6, 24, 120, 720, 5040]
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

**Goal:** Rewrite `factorial` with no `def`, no name, no assignment — using only `lambda`.

---

# Part I: The Idea — Passing Yourself

## 1. The First Attempt: Pass a Copy of Yourself

If a function cannot refer to itself by name, the next best thing is to **receive itself as an argument**:

```python
# Step 1: a factorial that receives "itself" as its first argument
# If we call it "self", the recursive call becomes self(self)(n-1)
step1 = lambda self: lambda n: 1 if n == 0 else n * self(self)(n - 1)

# To call it, we must pass it to itself:
factorial_v1 = step1(step1)

print(factorial_v1(5))   # 120
print(factorial_v1(7))   # 5040
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

This works! But `step1(step1)` is repetitive, and the body has `self(self)(n-1)` instead of the clean `self(n-1)` we would prefer. The next steps clean this up.

---

### Critical Thinking Questions — *Solo*

1. In `step1 = lambda self: lambda n: ...`, what type does `self` have? (Hint: what does `self(self)` produce?)
2. Why does the recursive call have `self(self)(n-1)` rather than `self(n-1)`?
3. If we wrote `self(n-1)` instead, what would happen when we try to call `step1(step1)(3)`? Trace the first two calls.

---

## 2. Step 2: Cleaning Up the Body

The `self(self)(n-1)` pattern is ugly. Let us hide it inside a helper `rec`:

```python
# Step 2: wrap the self-application so the body is clean
step2 = lambda self: (
    lambda rec: lambda n: 1 if n == 0 else n * rec(n - 1)
)(lambda n: self(self)(n))

factorial_v2 = step2(step2)
print(factorial_v2(6))   # 720

# The key insight: rec = lambda n: self(self)(n)
# So rec(n-1) = self(self)(n-1)
# Which is the same as step1's self(self)(n-1), but hidden in rec.
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

Now the body `lambda n: 1 if n == 0 else n * rec(n - 1)` looks like a normal recursive function that calls `rec`. The self-application machinery is hidden in `rec`'s definition.

---

## 3. Step 3: Separating the Logic from the Fixed-Point Machinery

Notice that `lambda rec: lambda n: 1 if n == 0 else n * rec(n - 1)` is just the factorial *logic* — a function that takes its recursive call-stub and returns the actual implementation. Let us name this "the step" or "the generator":

```python
# Separate the factorial logic from the fixed-point machinery
factorial_generator = lambda rec: lambda n: 1 if n == 0 else n * rec(n - 1)

# The machinery that turns any generator into a recursive function:
Y_machinery = lambda gen: (lambda self: gen(lambda n: self(self)(n)))(
                           lambda self: gen(lambda n: self(self)(n)))

factorial_v3 = Y_machinery(factorial_generator)
print(factorial_v3(7))   # 5040

# The Y_machinery works for ANY generator, not just factorial:
fib_generator  = lambda rec: lambda n: n if n <= 1 else rec(n-1) + rec(n-2)
fib_v3         = Y_machinery(fib_generator)
print([fib_v3(n) for n in range(10)])   # [0,1,1,2,3,5,8,13,21,34]
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

**This is the Z combinator** (the applicative-order version of Y): `Y_machinery` takes any recursive-function-generator and returns the recursive function.

---

# Part II: The Y Combinator

## 4. The Formal Definition

The **Y combinator** in the pure lambda calculus is:

$$
Y = \lambda f.\ (\lambda x.\ f\ (x\ x))\ (\lambda x.\ f\ (x\ x))
$$

It satisfies the **fixed-point equation**: $Y\ g = g\ (Y\ g)$ for any $g$. Let us verify this by reducing:

$$
Y\ g = (\lambda f.\ (\lambda x.\ f\ (x\ x))\ (\lambda x.\ f\ (x\ x)))\ g
$$
$$
\rightarrow_{\beta} (\lambda x.\ g\ (x\ x))\ (\lambda x.\ g\ (x\ x))
$$
$$
\rightarrow_{\beta} g\ ((\lambda x.\ g\ (x\ x))\ (\lambda x.\ g\ (x\ x)))
$$
$$
= g\ (Y\ g)
$$

This is the **unfolding equation**: $Y\ g$ reduces to $g$ applied to $Y\ g$ applied to itself. Exactly what a recursive call does.

**Why we need the Z variant for strict languages:** Pure Y in Python loops:

```python
# Y = lambda f: (lambda x: f(x(x)))(lambda x: f(x(x)))
# In Python (applicative order), evaluating x(x) in the argument position
# causes immediate infinite recursion before f even runs.
# Python evaluates BOTH branches of the lambda body eagerly.

# FIX: wrap with an extra lambda to delay evaluation (eta-expansion)
Z = lambda f: (lambda x: f(lambda v: x(x)(v)))(lambda x: f(lambda v: x(x)(v)))

factorial_via_Z = Z(lambda rec: lambda n: 1 if n == 0 else n * rec(n - 1))
print([factorial_via_Z(n) for n in range(8)])
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

The Z combinator differs from Y only in the `lambda v:` wrapper: instead of `x(x)` (evaluated immediately), it is `lambda v: x(x)(v)` (a function, evaluated only when called). This one-token change converts Y from a normal-order term to an applicative-order term.

---

[[MC]]
What is the key difference between the Y combinator and the Z combinator?

- (x) Z wraps the self-application in an extra lambda (eta-expansion), delaying evaluation to make it safe for applicative-order (strict) languages like Python.
- ( ) Z works for non-recursive functions while Y only works for recursive ones.
- ( ) Z is for multi-argument functions while Y is for single-argument functions.
- ( ) They are the same combinator; Z is just an alternative name for Y used in some textbooks.

---

## 5. Y in JavaScript and Haskell

JavaScript (strict, but with arrow functions):

```javascript
// JavaScript Z combinator
const Z = f => (x => f(v => x(x)(v)))(x => f(v => x(x)(v)));

const factorial = Z(rec => n => n === 0 ? 1 : n * rec(n - 1));
console.log(factorial(6));   // 720

const fib = Z(rec => n => n <= 1 ? n : rec(n-1) + rec(n-2));
console.log(Array.from({length: 10}, (_, i) => fib(i)));
// [0,1,1,2,3,5,8,13,21,34]
```

Haskell (lazy — the original Y works directly):

```haskell
-- Haskell is lazy, so Y works without eta-expansion
y :: (a -> a) -> a
y f = let x = f x in x
-- equivalently: y f = f (y f)

-- But Haskell's type system rejects the standard λ-calculus Y because
-- it would require an infinite type (α = α → α).
-- Instead, use fix from Data.Function:
import Data.Function (fix)

factorial :: Int -> Int
factorial = fix (\rec n -> if n == 0 then 1 else n * rec (n - 1))

-- fix f = f (fix f) -- this is the definition; Haskell's laziness makes it work
```

---

# Part III: Fixed Points and the Meaning of Y

## 6. Y as a Fixed-Point Operator

A **fixed point** of a function $g$ is a value $x$ such that $g(x) = x$. The Y combinator computes a fixed point of $g$ in the following sense:

$$
Y\ g = g\ (Y\ g)
$$

The value $Y\ g$ is a program that *unfolds itself one step whenever called*, which is exactly what a recursive function does. Recursion is **the fixed point of an unrolled computation**.

```python
# Fixed point illustration (not Y, but the idea):
import math

# Find fixed point of cos(x) iteratively: x = cos(x)
def fixed_point(f, guess=1.0, tol=1e-10, max_iter=1000):
    x = guess
    for _ in range(max_iter):
        next_x = f(x)
        if abs(next_x - x) < tol:
            return next_x
        x = next_x
    return x

fp_cos = fixed_point(math.cos)
print(f"Fixed point of cos: {fp_cos:.10f}")   # ≈ 0.7390851332
print(f"Verify cos(x)=x:    {math.cos(fp_cos):.10f}")   # same

# For functions on programs (not real numbers),
# Y computes the fixed point: Y(f) = f(Y(f))
Z = lambda f: (lambda x: f(lambda v: x(x)(v)))(lambda x: f(lambda v: x(x)(v)))
fact_gen = lambda rec: lambda n: 1 if n == 0 else n * rec(n - 1)
factorial = Z(fact_gen)

# Verify: fact_gen(factorial) = factorial (they produce the same function)
for n in range(8):
    via_Y    = factorial(n)
    via_gen  = fact_gen(factorial)(n)
    assert via_Y == via_gen, f"Fixed point violated at n={n}"
print("Fixed point verified: Z(fact_gen)(n) == fact_gen(Z(fact_gen))(n) for all tested n")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

---

## 7. Y Without Y: Other Fixed-Point Tricks

Several practical patterns implement the same idea without writing Y explicitly:

```python
# Pattern 1: default argument hack (exploits Python's eager default binding)
factorial_default = lambda n, rec=None: (
    (lambda n2, rec2: 1 if n2 == 0 else n2 * rec2(n2-1, rec2))(n, rec)
    if rec else (lambda n2: factorial_default(n2))(n)
)
# This is a hack; don't do it. It works but is obscure.

# Pattern 2: the "self" trick with a wrapper class
class Recursive:
    def __init__(self, f):
        self.f = f
    def __call__(self, *args):
        return self.f(self, *args)

factorial_class = Recursive(lambda self, n: 1 if n == 0 else n * self(n-1))
print(factorial_class(6))   # 720

# Pattern 3: mutual recursion via a shared namespace
namespace = {}
namespace['even'] = lambda n: True  if n == 0 else namespace['odd'](n - 1)
namespace['odd']  = lambda n: False if n == 0 else namespace['even'](n - 1)
print(namespace['even'](10), namespace['odd'](11))   # True True
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

---

# Part IV: Exercises

## 8. Exercises

1. **Derive Z by hand.** Starting from Y = $\lambda f.\ (\lambda x.\ f\ (x\ x))\ (\lambda x.\ f\ (x\ x))$, derive Z by adding the eta-expansion `lambda v:` in the right place. Show why the unadapted Y diverges in Python by tracing the first three beta-reduction steps in applicative order.

2. **Non-numeric recursion.** Use Z to implement `reverse_list` (takes a list, returns it reversed) without any `def` or named function. Hint: `reverse_list_gen = lambda rec: lambda lst: [] if not lst else rec(lst[1:]) + [lst[0]]`.

3. **Mutual recursion.** Use Z to implement mutually recursive `is_even` and `is_odd` (without using `%`). Hint: pack both into a pair, pass the pair as the self-argument, and select the correct one.

4. **Fixed-point poetry.** The Y combinator satisfies $Y\ g = g\ (Y\ g)$. In Python, `print` is a function. Can you write an expression (one Python line, no semicolons) that prints itself? This is the Quine problem — a program that outputs its own source code. It is the programming equivalent of the fixed-point equation. Research the connection and write a two-paragraph explanation.

5. **Y in the wild.** Find one real-world use of the Y combinator (or the Z combinator, or `fix`) in production code or a popular library. (Hint: search GitHub for `fix` in Haskell libraries, or `Y` in functional JavaScript utilities.) Report: what is the function, what does it compute, and why was the author motivated to write it with an explicit fixed-point combinator rather than a named recursive function?

---

## 9. Reflection Prompt

The Y combinator makes a striking philosophical point: self-reference — the ability of a process to call itself — is not a primitive. It is derivable from two things: functions and application. In your notebook, write a paragraph responding to this: what does it mean for computation that all recursion, everywhere, is ultimately "just" this fixed-point trick? Does it change how you think about what a programming language "really" needs to provide, versus what it provides for convenience?

---

## 10. Further Reading

- Michaelson, Greg. *An Introduction to Functional Programming Through Lambda Calculus* (Dover, 2011). Chapter 7 builds Y from scratch, more slowly than we do here.
- Gabriel Lebec. "Lambda as JS, or, A Flock of Functions." Speakerdeck, 2016. The JavaScript Y combinator section directly connects to this module.
- Krishnamurthi, Shriram. *PLAI*, Chapter 9: "Recursion and Cycles." The semantics of letrec — what the evaluator does to implement Y — is the companion to the combinator view.
- Abelson and Sussman. *SICP*, Section 4.1.6. The metacircular evaluator's treatment of `define` and recursive definitions.
- Gabriel, Richard. "Lisp: Good News, Bad News, How to Win Big." 1991. Mentions the Y combinator in the context of Lisp's identity as "the programmable programming language."
