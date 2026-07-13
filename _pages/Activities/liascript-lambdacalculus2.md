<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://github.com/BillJr99/Ursinus-CS374-Fall2026/blob/gh-pages/_pages/Activities/liascript-lambdacalculus2.md or locally via https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374-Fall2026/gh-pages/_pages/Activities/liascript-lambdacalculus2.md

import: https://raw.githubusercontent.com/liascript/CodeRunner/master/README.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

# The Lambda Calculus, Part 2: Church Encodings and Combinators

## Learning Goals

By the end of this activity, you will be able to:

- Define and reduce the named combinators I, K, KI, and C as pure lambda terms, and verify their behavior by hand reduction and Python execution
- Encode booleans as lambda terms (Church booleans) and implement `AND`, `OR`, `NOT`, and `IF-THEN-ELSE` using only function application
- Encode natural numbers as Church numerals and implement successor, addition, and multiplication as lambda functions
- Demonstrate that every combinator with no free variables can be given a permanent name, and connect this to the concept of referential transparency
- Trace the full reduction of an arithmetic expression written in Church numeral notation to its normal form

> **Before You Begin**
>
> This activity builds directly on **Lambda Calculus, Part 1**. Before starting, you should be comfortable with:
>
> - Writing and reading lambda expressions (e.g., `λx.λy. x`)
> - Performing beta reduction step by step
> - Distinguishing free variables from bound variables
> - Applying multi-argument (curried) functions
>
> If any of those feel shaky, review the [Lambda Calculus, Part 1 activity](liascript-lambdacalculus1.md) before continuing.

---

Everything you need to compute can be expressed with just functions. Lambda calculus has no numbers, no booleans, no if-statements — yet Church showed how to encode ALL of these as pure lambda terms. This activity builds that encoding from scratch in Python.

Yesterday's calculus had no numbers, no booleans, no data, and today we discover it needs none: **everything can be built from functions alone**. Following the same path as Gabriel Lebec's "A Flock of Functions" (our companion reading, in JavaScript), we build booleans, then numbers, then arithmetic, verifying each construction by hand and in Python. The arc: **named combinators $\rightarrow$ Church booleans $\rightarrow$ Church numerals $\rightarrow$ arithmetic as function surgery**.

---

## Directions and Group Roles

Work in your POGIL team with rotated roles (**Manager**, **Recorder**, **Presenter**, **Reflector**). Whiteboard day again: every claimed equality gets a stepwise reduction or a Python verification, checked by a teammate. After class, respond to the reflective prompt individually in your notebook.

---

# Part I: The Flock

## 1. Combinators: Closed Terms with Names

A **combinator** is a lambda expression with no free variables; the famous ones have bird names (from Raymond Smullyan's puzzle book, the tradition Lebec's talk follows):

$$
\textbf{I} = \lambda x.\, x \quad \text{(Identity, the Idiot bird)}
$$
$$
\textbf{K} = \lambda x. \lambda y.\, x \quad \text{(the Kestrel: constant-maker)}
$$
$$
\textbf{KI} = \lambda x. \lambda y.\, y \quad \text{(Kite: discards the first)}
$$
$$
\textbf{C} = \lambda f. \lambda a. \lambda b.\, f\, b\, a \quad \text{(Cardinal: flips arguments)}
$$

You reduced **K** $A\, B \rightarrow A$ and **KI** $A\, B \rightarrow B$ yesterday without their names. Hold that thought; it is about to become the whole theory of truth.

---

## Model 1: Birdwatching

### Critical Thinking Questions

> **CTQ 1.1** Verify by reduction that $\textbf{C}\, \textbf{K}\, A\, B$ behaves exactly like $\textbf{KI}\, A\, B$. (The Cardinal of the Kestrel is the Kite: flipping "take the first" yields "take the second.")

> **CTQ 1.2** Write each combinator as a Python lambda (`K = lambda x: lambda y: x`, and so on) and verify question 1 by execution with strings for $A$ and $B$.

> **CTQ 1.3** Why must a combinator have no free variables to deserve a permanent name? Connect to purity from the functional module.

---

# Part II: Truth, Built from Selection

> **Intuition before booleans:** An `if` does one job: select between two things. So we will *define* the booleans as the selectors. TRUE is a function that ignores its second argument: `lambda x: lambda y: x`. FALSE is `lambda x: lambda y: y`. If/then/else is just applying a boolean to two branches: write `b(then_branch)(else_branch)` and the boolean itself picks the right one.

## 2. Church Booleans

An `if` does one job: select between two things. So *define* the booleans as the selectors you already have:

$$
\textbf{TRUE} = \textbf{K} = \lambda x. \lambda y.\, x \qquad \textbf{FALSE} = \textbf{KI} = \lambda x. \lambda y.\, y
$$

Then `if b then t else e` is simply $b\, t\, e$: no special form needed, the boolean *is* the conditional. Logic follows as function surgery:

$$
\textbf{NOT} = \lambda b.\, b\, \textbf{FALSE}\, \textbf{TRUE} \qquad
\textbf{AND} = \lambda p. \lambda q.\, p\, q\, p \qquad
\textbf{OR} = \lambda p. \lambda q.\, p\, p\, q
$$

> **Watch out!** Church booleans are functions, not values. `TRUE(a)(b)` returns `a` — that is the entire definition. The if-then-else `IF b t f = b(t)(f)` works because TRUE selects its first argument and FALSE selects its second. There is no special conditional syntax; the boolean *is* the branch selector.

> **Watch out!** Python's `lambda` returns single expressions. For multi-argument Church terms, use curried lambdas: `lambda x: lambda y: x` not `lambda x,y: x`. The curried form is what makes `TRUE(a)(b)` work — the first call returns another function that accepts `b`.

**Step-by-step reduction: NOT TRUE**

```
NOT TRUE
= (λb. b FALSE TRUE) (λx.λy. x)
→β (λx.λy. x) FALSE TRUE
→β (λy. FALSE) TRUE
→β FALSE  ✓
```

**Step-by-step reduction: AND TRUE FALSE**

```
AND TRUE FALSE
= (λp.λq. p q p) TRUE FALSE
→β (λq. TRUE q TRUE) FALSE
→β TRUE FALSE TRUE
= (λx.λy. x) FALSE TRUE
→β (λy. FALSE) TRUE
→β FALSE  ✓
```

**Decode helper — "peek inside" a Church boolean:**

```python  liascript
TRUE  = lambda x: lambda y: x
FALSE = lambda x: lambda y: y

def church_to_bool(b):
    return b(True)(False)

print("church_to_bool(TRUE)  =", church_to_bool(TRUE))
print("church_to_bool(FALSE) =", church_to_bool(FALSE))
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

Hand a Church boolean `True` and `False` (Python's built-ins) as its two arguments. Since TRUE selects its first argument it returns `True`; FALSE returns `False`. This is your window into the encoding.

### Church Booleans — Runnable

```python  liascript
# Church booleans: TRUE selects first, FALSE selects second.
TRUE  = lambda x: lambda y: x          # K  (Kestrel)
FALSE = lambda x: lambda y: y          # KI (Kite)
NOT   = lambda b: b(FALSE)(TRUE)
AND   = lambda p: lambda q: p(q)(p)
OR    = lambda p: lambda q: p(p)(q)
XOR   = lambda p: lambda q: p(NOT(q))(q)

# Decode helper: peek inside any Church boolean
def church_to_bool(b):
    return b(True)(False)

show_bool = lambda b: b("TRUE")("FALSE")   # a boolean selects its own name

print("=== Church Booleans ===")
print("church_to_bool(TRUE)  =", church_to_bool(TRUE))
print("church_to_bool(FALSE) =", church_to_bool(FALSE))
print("NOT TRUE        =", show_bool(NOT(TRUE)))
print("NOT FALSE       =", show_bool(NOT(FALSE)))
print("AND TRUE FALSE  =", show_bool(AND(TRUE)(FALSE)))
print("OR  FALSE TRUE  =", show_bool(OR(FALSE)(TRUE)))
print("XOR TRUE  TRUE  =", show_bool(XOR(TRUE)(TRUE)))
print("XOR TRUE  FALSE =", show_bool(XOR(TRUE)(FALSE)))

# if-then-else is just application: b(then)(else)
print("\n=== Church if-then-else ===")
print("if TRUE  then 'yes' else 'no' =", TRUE("yes")("no"))
print("if FALSE then 'yes' else 'no' =", FALSE("yes")("no"))
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

---

## Model 2: Prove the Logic

### Critical Thinking Questions

> **CTQ 2.1** Reduce $\textbf{NOT}\, \textbf{TRUE}$ step by step to $\textbf{FALSE}$. (Substitute, then let TRUE select.) The trace above is a guide; write your own with all substitutions made explicit.

> **CTQ 2.2** Reduce $\textbf{AND}\, \textbf{TRUE}\, \textbf{FALSE}$ and $\textbf{AND}\, \textbf{FALSE}\, \textbf{TRUE}$. Explain *why* `p q p` works in one sentence: when is the answer just "whatever q is," and when is it "p itself"?

> **CTQ 2.3** $\textbf{AND}$ never examines $q$ when $p$ is FALSE. Which semantics from the control-flow module did you just get *for free*, and why is it free here?

> **CTQ 2.4** Notice $\textbf{NOT} = \textbf{C}$ applied cleverly... actually, verify: does $\textbf{C}\, b$ flip a Church boolean's selections? Reduce $\textbf{C}\, \textbf{TRUE}\, A\, B$ and compare with $\textbf{FALSE}\, A\, B$.

---

# Part III: Numbers as Repetition

> **Intuition before numerals:** Zero is "apply f zero times": `lambda f: lambda x: x`. One is "apply f once": `lambda f: lambda x: f(x)`. The number N is "apply f N times to x." Addition is "apply f m+n times." Multiplication is "apply (n copies of f) m times." The number *is* the iteration count — there are no digits stored anywhere.

## 3. Church Numerals

A number $n$ is encoded as *the act of doing something n times*:

$$
\textbf{0} = \lambda f. \lambda x.\, x \qquad
\textbf{1} = \lambda f. \lambda x.\, f\, x \qquad
\textbf{2} = \lambda f. \lambda x.\, f\, (f\, x) \qquad
\textbf{3} = \lambda f. \lambda x.\, f\, (f\, (f\, x))
$$

You met $\textbf{2}$ yesterday as `twice`. Arithmetic becomes composition of repetitions:

$$
\textbf{SUCC} = \lambda n. \lambda f. \lambda x.\, f\, (n\, f\, x) \qquad
\textbf{PLUS} = \lambda m. \lambda n. \lambda f. \lambda x.\, m\, f\, (n\, f\, x) \qquad
\textbf{MULT} = \lambda m. \lambda n. \lambda f.\, m\, (n\, f)
$$

Read PLUS aloud: "apply $f$ $n$ times to $x$, then $m$ more times." Read MULT: "$n$ copies of $f$, repeated $m$ times."

> **Watch out!** Church numerals look like iteration counts, not numbers. `TWO f x = f(f(x))` applies `f` twice to `x`. The numeral does not "contain" the digit 2; it *is* the behavior of applying something twice. This is why `church_to_int` works: you hand it the successor function on machine integers and the seed 0, and count how many times successor fires.

**Step-by-step reduction: SUCC ZERO reduces to ONE**

```
SUCC ZERO
= (λn.λf.λx. f (n f x)) (λf.λx. x)
→β λf.λx. f ((λf.λx. x) f x)
→β λf.λx. f ((λx. x) x)
→β λf.λx. f x
= ONE  ✓
```

**Decode helper — "peek inside" a Church numeral:**

```python  liascript
ZERO = lambda f: lambda x: x
SUCC = lambda n: lambda f: lambda x: f(n(f)(x))

def church_to_int(n):
    return n(lambda x: x + 1)(0)

ONE = SUCC(ZERO)
TWO = SUCC(ONE)
print("church_to_int(ZERO) =", church_to_int(ZERO))
print("church_to_int(ONE)  =", church_to_int(ONE))
print("church_to_int(TWO)  =", church_to_int(TWO))
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

Hand the numeral the successor function on Python ints and the seed 0. If the numeral applies its function twice (as TWO does), you get `0 + 1 + 1 = 2`. The number of applications is exactly the Church numeral's value.

---

## Church Encodings — Runnable

```python  liascript
# Church encodings, executable. Python lambdas ARE lambda calculus terms.

TRUE  = lambda x: lambda y: x          # K  (Kestrel)
FALSE = lambda x: lambda y: y          # KI (Kite)
NOT   = lambda b: b(FALSE)(TRUE)
AND   = lambda p: lambda q: p(q)(p)
OR    = lambda p: lambda q: p(p)(q)
XOR   = lambda p: lambda q: p(NOT(q))(q)

show_bool = lambda b: b("TRUE")("FALSE")    # a boolean selects its own name

# Decode helpers
def church_to_bool(b):
    return b(True)(False)

def church_to_int(n):
    return n(lambda x: x + 1)(0)

print("=== Church Numerals ===")
ZERO  = lambda f: lambda x: x
SUCC  = lambda n: lambda f: lambda x: f(n(f)(x))
PLUS  = lambda m: lambda n: lambda f: lambda x: m(f)(n(f)(x))
MULT  = lambda m: lambda n: lambda f: m(n(f))
EXP   = lambda m: lambda n: n(m)    # m^n — shockingly simple

ONE, TWO = SUCC(ZERO), SUCC(SUCC(ZERO))
THREE    = PLUS(ONE)(TWO)
SIX      = MULT(TWO)(THREE)
EIGHT    = EXP(TWO)(THREE)   # 2^3

print("church_to_int(ZERO)  =", church_to_int(ZERO))
print("church_to_int(ONE)   =", church_to_int(ONE))
print("church_to_int(TWO)   =", church_to_int(TWO))
print("ONE, TWO, 1+2, 2*3  =", church_to_int(ONE), church_to_int(TWO), church_to_int(THREE), church_to_int(SIX))
print("2^3 =", church_to_int(EIGHT))

# if-then-else is just application: b(then)(else)
print("\n=== Church if-then-else ===")
print("if TRUE: 'yes'  =", TRUE("yes")("no"))
print("if FALSE: 'yes' =", FALSE("yes")("no"))

# ISZERO: apply (lambda x: FALSE) n times to TRUE. If n=0, never applied.
ISZERO = lambda n: n(lambda _: FALSE)(TRUE)
print("\n=== ISZERO ===")
for n, val in [(ZERO, "ZERO"), (ONE, "ONE"), (TWO, "TWO")]:
    print(f"ISZERO({val}) = {show_bool(ISZERO(n))}")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

---

## Model 3: Interrogate the Encodings

### Critical Thinking Questions

> **CTQ 3.1** `church_to_int` decodes a numeral by handing it the successor function on machine integers and the seed 0. Explain why this works in one sentence that begins "A Church numeral n is...".

> **CTQ 3.2** Reduce $\textbf{SUCC}\; \textbf{1}$ by hand to confirm it is $\textbf{2}$ (expect two or three careful steps). The trace for `SUCC ZERO` above is a model; repeat the pattern one numeral up.

> **CTQ 3.3** Verify in code that $\textbf{MULT}\, \textbf{2}\, \textbf{3}$ and $\textbf{PLUS}\, \textbf{3}\, \textbf{3}$ decode equally, then explain MULT's eerie brevity: what is `n(f)`, and what does `m` do *to that*?

> **CTQ 3.4** Where is the data? A Church numeral stores no digits anywhere. Connect this to homoiconicity week's lesson, and to the claim "data is frozen behavior."

[[MC]]
Under Church encoding, the expression `b(t)(e)` where b is a Church boolean implements if-then-else because:
- ( ) Python evaluates booleans specially
- (x) TRUE and FALSE are themselves selector functions returning their first and second arguments respectively
- ( ) The lambda calculus has a built-in conditional form
- ( ) t and e must be numerals

---

# Part IV: Pairs and the Predecessor

> **Intuition before pairs:** A pair stores two values. The pair itself is a function that takes a "selector": `lambda sel: sel(a)(b)`. FST passes `lambda x: lambda y: x` (which is TRUE/K) to extract the first element; SND passes `lambda x: lambda y: y` (which is FALSE/KI) to extract the second. You already built the selectors when you built booleans — pairs come for free.

## Model 4: Pairs and the Predecessor

**Church pairs — building linked data from functions:**

```python  liascript
# Church pairs: PAIR a b f = f a b
# FST p = p K  (select first)
# SND p = p KI (select second)

TRUE  = lambda x: lambda y: x   # K
FALSE = lambda x: lambda y: y   # KI

# Decode helpers
def church_to_int(n):
    return n(lambda k: k + 1)(0)

ZERO  = lambda f: lambda x: x
SUCC  = lambda n: lambda f: lambda x: f(n(f)(x))

PAIR = lambda a: lambda b: lambda f: f(a)(b)
FST  = lambda p: p(TRUE)
SND  = lambda p: p(FALSE)

print("=== Church Pairs ===")
p = PAIR("hello")("world")
print(f"FST (PAIR 'hello' 'world') = {FST(p)!r}")
print(f"SND (PAIR 'hello' 'world') = {SND(p)!r}")

# Numeric pairs for predecessor: PAIR n (n-1)
# Increment a pair: (n,m) -> (SUCC n, n)  i.e., shift right
shift = lambda p: PAIR(SUCC(FST(p)))(FST(p))

# PRED n: start from (0,0), apply shift n times, take SND
ZERO_PAIR = PAIR(ZERO)(ZERO)
PRED = lambda n: SND(n(shift)(ZERO_PAIR))

# Build some numerals
ONE = SUCC(ZERO); TWO = SUCC(ONE); THREE = SUCC(TWO); FOUR = SUCC(THREE)

print("\n=== Predecessor ===")
print(f"PRED(0) = {church_to_int(PRED(ZERO))}")   # 0 (special case)
print(f"PRED(1) = {church_to_int(PRED(ONE))}")    # 0
print(f"PRED(2) = {church_to_int(PRED(TWO))}")    # 1
print(f"PRED(4) = {church_to_int(PRED(FOUR))}")   # 3

# Subtraction from predecessor:
MINUS = lambda m: lambda n: n(PRED)(m)
print(f"\n4 - 2 = {church_to_int(MINUS(FOUR)(TWO))}")   # 2
print(f"3 - 4 = {church_to_int(MINUS(THREE)(FOUR))}")   # 0 (floored)
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

### Critical Thinking Questions

> **CTQ 4.1** The pair-based predecessor works by shifting: `(0,0) → (1,0) → (2,1) → (3,2)`. After applying shift $n$ times to $(0,0)$, what is the SND? Why does `PRED(ZERO)` return ZERO rather than negative one?

> **CTQ 4.2** Subtraction `m - n` is defined as "apply PRED n times to m." What is `3 - 5` under this definition? This is called *monus* (truncated subtraction). Is this a bug or a deliberate design choice?

> **CTQ 4.3** You now have: booleans, conditionals, numerals, arithmetic, pairs. What other data structures (lists, trees) could be built from Church pairs? Sketch the encoding for a two-element list [a, b].

---

---
**🛑 In-class work stops here.** Everything below is homework and going-deeper material — attempt the exercises before the related assignment.

## 4. Exercises

1. *Pairs.* Define $\textbf{PAIR} = \lambda a. \lambda b. \lambda f.\, f\, a\, b$, with $\textbf{FST} = \lambda p.\, p\, \textbf{K}$ and $\textbf{SND} = \lambda p.\, p\, \textbf{KI}$. Verify in Python, then say what data structure you just built from nothing, and what your AST could, in principle, be encoded as.
2. *IS-ZERO.* Define $\textbf{ISZERO} = \lambda n.\, n\, (\lambda x.\, \textbf{FALSE})\, \textbf{TRUE}$ and verify on 0, 1, 2. Explain the trick: what happens to TRUE if $f$ is applied even once?
3. *XOR.* Build XOR from the flock (any correct construction), verify all four input pairs in code, and present your reduction for one pair on the board.
4. *Flock report.* Watch or skim Lebec's "A Flock of Functions" (linked below) and write a half page: one construction he presents that we did not build today, reduced or verified yourself.
5. *Church list.* Build a Church-encoded linked list: `NIL`, `CONS(head)(tail)`, `HEAD`, `TAIL`, `ISNIL`. Represent the list `[1, 2, 3]` as Church numerals in a Church list, and write a `to_python_list` function that decodes it.
6. *Mechanical audit.* Choose one Church-encoding reduction you performed by hand in this module (for example, $\textbf{ISZERO}\, \overline{1}$ or $\textbf{FST}\, (\textbf{PAIR}\, a\, b)$) and verify it mechanically using Lambda-Py / pycombinator (https://finsberg.github.io/pycombinator/docs/lambda-talk.html) or your own Python reducer. Include the transcript, and reconcile in one sentence: did the machine agree with your hand derivation step for step, and if not, which artifact erred?

---

## Reflection Prompt

In your notebook: numbers, booleans, pairs, and conditionals all dissolved into functions this week. Does anything in computing now seem *irreducibly* data to you, or is it functions all the way down? Defend your answer with one example, knowing your December language will choose what to make primitive.

---

## 5. Further Reading

- Gabriel Lebec. "Lambda as JS, or A Flock of Functions": https://speakerdeck.com/glebec/lambda-as-js-or-a-flock-of-functions-combinators-lambda-calculus-and-church-encodings-in-javascript (talk recording also online). This is the companion reading for today's module — every Python cell here mirrors a section of that talk.
- **Lambda-Py / pycombinator** — combinators and Church encodings in Python; run every Church encoding from today interactively in your browser: https://finsberg.github.io/pycombinator/docs/lambda-talk.html
- Raymond Smullyan. *To Mock a Mockingbird* (1985): the combinator birds.
- Raul Rojas. "A Tutorial Introduction to the Lambda Calculus" (online), sections on encodings.

---

## Going Deeper (at home): The Y Combinator — Self-Reference Without Names

Imagine a self-playing record: the groove that plays the current note also contains the instruction to move to the next note. The record does not need to consult an external playlist — the mechanism for advancing is baked into every moment of the playback. The Y combinator works the same way: the code that produces the next recursive call is folded directly into each call site, with no external name, no registry, no environment entry needed.

#### Learning Goals

By the end of this activity, you will be able to:

- Explain why named self-reference is unavailable in the pure lambda calculus and why an anonymous recursive function requires a fixed-point operator
- Derive the Y combinator step by step from the self-application trick, tracing how each intermediate form eliminates a deficiency of the previous one
- Implement a working Y combinator in Python (using the Z combinator variant for strict evaluation) and use it to express factorial without `def` or assignment
- Define what it means for Y to be a fixed-point operator (`Y f = f (Y f)`) and verify this property by hand reduction
- Recognize the Y combinator pattern in real code (trampolined recursion, anonymous recursion idioms in JavaScript and Haskell)

> **Before You Begin — Prerequisites**
>
> This activity assumes you are comfortable with:
>
> - **Lambda calculus syntax and beta-reduction** — you can apply a lambda term to an argument step by step
> - **Higher-order functions** — a function that takes another function as an argument and returns a function
> - **Python lambdas** — `lambda n: n * 2` is a valid Python callable; you can nest lambdas and call them immediately
> - **The combinators module (recommended but not required)** — familiarity with I, K, and S helps with Section 10 of that module, which shows Y in pure SK form
>
> The key mental model you need: a function in the lambda calculus is *anonymous*. It has no name. The question this module answers is: how can something anonymous call itself?

*"The Y combinator is probably the most ingenious and least intuitive result in the lambda calculus."* — Pierce, *TAPL*

Every recursive function you have ever written calls itself by name: `factorial` calls `factorial`, `fib` calls `fib`. This seems obvious and necessary. But names are a feature of programming environments, not a feature of computation itself. The lambda calculus has no names — every definition is anonymous. So how do you write a recursive function when you cannot name it? How do you call a function you cannot refer to?

The answer is the **Y combinator**: a fixed-point operator that provides every function the gift of self-reference, without requiring a name. This module builds to Y from scratch — through a carefully designed sequence of wrong answers that teach the right intuition — and then shows Y at work in modern Python, JavaScript, and Haskell.

---

#### 0. Prerequisites

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

### Part I: The Idea — Passing Yourself

#### 1. The First Attempt: Pass a Copy of Yourself

The big idea in this part is embarrassingly simple once you see it: if you cannot *name* yourself, you can *be given* yourself as an argument. Instead of `factorial` calling `factorial`, you write a function that says "whoever you are, call yourself on the next input." Then the caller is responsible for handing the function a copy of itself. This feels circular — and it is! — but the circularity is explicit and controlled rather than hidden in a name lookup.

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

> **Watch out! — `self` is a function, not an integer**
>
> In `step1`, the argument called `self` is not a number — it is a *function* (specifically, it will be `step1` itself). The call `self(self)` returns a *function* (one that takes `n`), and then `(n - 1)` calls that function. Students often confuse `self(self)(n-1)` with `self(n-1)`: the first passes `self` as argument to produce a callable, then calls that callable on `n-1`; the second would pass `n-1` directly to `self`, which expects a function. Always trace the types.

---

##### Critical Thinking Questions — *Solo*

1. In `step1 = lambda self: lambda n: ...`, what type does `self` have? (Hint: what does `self(self)` produce?)
2. Why does the recursive call have `self(self)(n-1)` rather than `self(n-1)`?
3. If we wrote `self(n-1)` instead, what would happen when we try to call `step1(step1)(3)`? Trace the first two calls.

---

#### 2. Step 2: Cleaning Up the Body

The self-application ugliness (`self(self)(n-1)`) is a leaky abstraction: the *caller's* machinery is bleeding into the function's *logic*. The fix is a wrapper that absorbs the machinery, so the recursive call site looks like an ordinary call `rec(n-1)`. Think of `rec` as a pre-packaged "call-me-again" token that the function receives and uses freely, without knowing or caring that underneath it is `self(self)`.

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

#### 3. Step 3: Separating the Logic from the Fixed-Point Machinery

This is the key abstraction step. Once the self-application plumbing is hidden in `rec`, the factorial logic becomes a perfectly ordinary function generator: "give me a `rec` that handles the recursive call, and I will give you a working factorial." This generator works for *any* recursive function — not just factorial. The machinery that turns a generator into a recursive function is independent of what the function computes. That machinery — currently called `Y_machinery` — is the Y combinator. You have now rebuilt it from scratch.

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

### Part II: The Y Combinator

#### 4. The Formal Definition

The formal definition of Y in the lambda calculus is exactly the `Y_machinery` you built in Part I, written in lambda notation and compressed. The self-playing record analogy pays off here: $\lambda x.\ f\ (x\ x)$ is the "groove" — a function that, when applied to itself, hands $f$ a way to replay itself. Applied to itself, it produces $f\ (\text{the whole thing again})$. The outer $\lambda f$ makes the machinery generic: it works for *any* generator $f$, not just factorial. The one practical obstacle is evaluation order, which forces us to use the Z variant in Python.

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

> **Watch out! — Python evaluates arguments before calling functions**
>
> In the pure Y combinator, the body contains `x(x)` as a sub-expression. Python (like most languages) evaluates *both* arguments before making a function call. So when it processes `(lambda x: f(x(x)))(lambda x: f(x(x)))`, it tries to evaluate the argument `lambda x: f(x(x))` applied to itself *immediately* — before any base case can fire — resulting in infinite recursion. The fix is eta-expansion: wrap `x(x)` in `lambda v: x(x)(v)`, which delays evaluation until `v` is actually provided. This single change converts the call-by-name Y into the call-by-value Z.

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

#### 5. Y in JavaScript and Haskell

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

### Part III: Fixed Points and the Meaning of Y

#### 6. Y as a Fixed-Point Operator

A fixed point is a value that a function maps to itself: $g(x) = x$. For numeric functions, this is a concrete number (the fixed point of cosine is about 0.739). For function-valued functions — generators that take a recursive call-stub and return a function — the "fixed point" is the fully recursive function itself. This is the self-playing record in precise mathematical language: the record that, when played, produces itself as output. The Y combinator finds that fixed point for any generator.

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

#### 7. Y Without Y: Other Fixed-Point Tricks

Real-world code rarely spells out `Z = lambda f: (lambda x: ...)`. Instead, programmers reach for idioms that produce the same effect — passing `self` as an argument, wrapping in a class, using a shared namespace. These are all approximations of the fixed-point idea, using features (assignment, objects, closures) that the lambda calculus deliberately excludes. Recognizing them as instances of the same underlying pattern is the payoff of having studied Y from scratch.

Several practical patterns implement the same idea without writing Y explicitly:

```python
# Pattern 1: default argument hack (exploits Python's eager default binding)
factorial_default = lambda n, rec=None: (
    (lambda n2, rec2: 1 if n2 == 0 else n2 * rec2(n2-1, rec2))(n, rec)
    if rec else (lambda n2: factorial_default(n2))(n)
)
# This is a hack; don't do it. It works but is obscure.
# Watch out: this function still relies on the name `factorial_default` in its
# body — it is not truly anonymous. It smuggles a name in through the closure.

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

### Part IV: Exercises

#### 8. Exercises

1. **Derive Z by hand.** Starting from Y = $\lambda f.\ (\lambda x.\ f\ (x\ x))\ (\lambda x.\ f\ (x\ x))$, derive Z by adding the eta-expansion `lambda v:` in the right place. Show why the unadapted Y diverges in Python by tracing the first three beta-reduction steps in applicative order.

2. **Non-numeric recursion.** Use Z to implement `reverse_list` (takes a list, returns it reversed) without any `def` or named function. Hint: `reverse_list_gen = lambda rec: lambda lst: [] if not lst else rec(lst[1:]) + [lst[0]]`.

3. **Mutual recursion.** Use Z to implement mutually recursive `is_even` and `is_odd` (without using `%`). Hint: pack both into a pair, pass the pair as the self-argument, and select the correct one.

4. **Fixed-point poetry.** The Y combinator satisfies $Y\ g = g\ (Y\ g)$. In Python, `print` is a function. Can you write an expression (one Python line, no semicolons) that prints itself? This is the Quine problem — a program that outputs its own source code. It is the programming equivalent of the fixed-point equation. Research the connection and write a two-paragraph explanation.

5. **Y in the wild.** Find one real-world use of the Y combinator (or the Z combinator, or `fix`) in production code or a popular library. (Hint: search GitHub for `fix` in Haskell libraries, or `Y` in functional JavaScript utilities.) Report: what is the function, what does it compute, and why was the author motivated to write it with an explicit fixed-point combinator rather than a named recursive function?

---

#### 9. Reflection Prompt

The Y combinator makes a striking philosophical point: self-reference — the ability of a process to call itself — is not a primitive. It is derivable from two things: functions and application. In your notebook, write a paragraph responding to this: what does it mean for computation that all recursion, everywhere, is ultimately "just" this fixed-point trick? Does it change how you think about what a programming language "really" needs to provide, versus what it provides for convenience?

---

#### 10. Further Reading

- Michaelson, Greg. *An Introduction to Functional Programming Through Lambda Calculus* (Dover, 2011). Chapter 7 builds Y from scratch, more slowly than we do here.
- Gabriel Lebec. "Lambda as JS, or, A Flock of Functions." Speakerdeck, 2016. The JavaScript Y combinator section directly connects to this module.
- Krishnamurthi, Shriram. *PLAI*, Chapter 9: "Recursion and Cycles." The semantics of letrec — what the evaluator does to implement Y — is the companion to the combinator view.
- Abelson and Sussman. *SICP*, Section 4.1.6. The metacircular evaluator's treatment of `define` and recursive definitions.
- Gabriel, Richard. "Lisp: Good News, Bad News, How to Win Big." 1991. Mentions the Y combinator in the context of Lisp's identity as "the programmable programming language."

---

## Going Deeper (Optional Pointers)

> **Going further:** the call-with-current-continuation appendix that used to live here — capturing "the rest of the computation" as a value, deriving break, return, exceptions, cooperative schedulers, generators, and backtracking from `call/cc` — now lives where it is assessed: **Direction B of the [Functional assignment](https://www.billmongan.com/Ursinus-CS374-Fall2026/Assignments/Functional) builds on this material** — read that direction's section before choosing it.

> **Going further:** the Curry-Howard correspondence appendix (programs as proofs: propositions as types, products and sums, the empty type and absurdity, a glimpse of dependent types) is a self-study topic — search "Curry-Howard correspondence" and see *Propositions as Types* by Philip Wadler when curiosity calls for it.
