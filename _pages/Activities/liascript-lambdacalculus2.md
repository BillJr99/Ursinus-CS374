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

## Going Deeper (Optional Appendices)

The core lesson above stands on its own. The optional deep dives below expand on it — read whichever interest you:

- The Y Combinator: Self-Reference Without Names
- Call with Current Continuation: Capturing the Future
- The Curry-Howard Correspondence: Programs Are Proofs

## Going Deeper: The Y Combinator: Self-Reference Without Names

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

## Going Deeper: Call with Current Continuation: Capturing the Future

#### Learning Goals

By the end of this activity, you will be able to:

- Describe what the "current continuation" is at any point in a CPS program and explain what it means to "capture" it
- Simulate `call/cc` in Python by building an escape continuation using CPS and a mutable cell, and use it to implement early exit from nested computation
- Identify `return`, `break`, and `raise` as restricted forms of escape continuations, and explain what makes `call/cc` more powerful than each of them
- Implement at least two control-flow patterns using captured continuations: early exit and coroutine-style cooperative multitasking
- Explain the connection between `call/cc`, CPS, and closures: continuations are closures over the rest of the program

---

#### Before You Begin

> **Prerequisites — make sure you are comfortable with these before proceeding:**
>
> - **Continuations and CPS** — You should be able to take a direct-style function and manually convert it to continuation-passing style. If that is fuzzy, revisit the [CPS Activity](_pages/Activities/liascript-functional.md) before continuing here.
> - **Closures** — You should understand that a Python function defined inside another function "closes over" the outer variables and carries them with it.
> - **Exceptions** — You should understand how `try / raise / except` work in Python and why raising an exception causes a non-local jump out of nested call frames.
>
> **Why those three?** `call/cc` is best understood as a generalization of all three at once: it is CPS made explicit, it uses closures to freeze the program state, and it performs the same kind of non-local jump that exceptions do — but under your direct control.

---

#### Opening Hook: You Already Know call/cc

Here is something surprising:

> **Python's `return`, `break`, and `raise` are all forms of call/cc in disguise. They all say "throw away the rest of the current computation and jump somewhere else." The `call/cc` operator makes this explicit and first-class — you can store a 'jump target' in a variable and invoke it later.**

Every time you write `return x` inside a loop, Python throws away the rest of the loop, throws away the rest of the function, and jumps to whatever called the function. `break` throws away the rest of the loop body. `raise` throws away the rest of everything until a matching `except` is found. These jumps are powerful, but they are *wired in* — you cannot pass a `return` around as a value, store it in a list, or call it five seconds later.

`call/cc` unfreezes this. It lets you name the jump target, store it, and fire it whenever you want — once, never, or many times.

This module follows three steps: **(1)** understand continuations as "the rest of the computation," **(2)** simulate `call/cc` in Python using CPS and mutable state, **(3)** observe how every major control-flow mechanism is secretly a restricted continuation.

---

#### Directions and Group Roles

| Role | Responsibility |
|------|---------------|
| **Facilitator** | Keeps the group moving; makes sure everyone has spoken before the group decides |
| **Recorder** | Writes down the group's answers and observations |
| **Reporter** | Shares the group's findings with the class |
| **Reflector** | Monitors process; raises a flag if the group is confused but plowing ahead |

Rotate roles every class meeting. Each model has a Python code block — run it, observe the output, then answer the Critical Thinking Questions *before* moving on.

---

#### 0. Motivation: try/except Is Already call/cc

Before we touch anything exotic, look at code you have been writing since CS1. The `try/except` construct is an escape continuation — a way of saying "abandon everything and jump here immediately."

```python  liascript
# Ordinary try/except: raise is an escape continuation
class EarlyExit(Exception):
    def __init__(self, value):
        self.value = value

def find_first_even_exceptions(lst):
    """Return the first even number in lst, or None."""
    try:
        for x in lst:
            print(f"  checking {x} ...")
            if x % 2 == 0:
                raise EarlyExit(x)   # JUMP out of the loop immediately
            print(f"  {x} is odd, continuing")
        return None
    except EarlyExit as e:
        print(f"  --> escaped with {e.value}")
        return e.value

print("find_first_even_exceptions([1, 3, 4, 7, 8]):")
print(find_first_even_exceptions([1, 3, 4, 7, 8]))
print()

# Now the same idea expressed with call/cc explicitly:
class Continuation:
    def __init__(self):
        self.value = None
    def __call__(self, value):
        self.value = value
        raise _EscapeException(value)

class _EscapeException(BaseException):
    def __init__(self, value): self.value = value

def callcc(f):
    k = Continuation()
    try:
        result = f(k)
        return result
    except _EscapeException as e:
        return e.value

def find_first_even_callcc(lst):
    """Same logic, but using callcc explicitly."""
    def body(k):          # k is the escape continuation
        for x in lst:
            print(f"  checking {x} ...")
            if x % 2 == 0:
                k(x)      # escape immediately with x
            print(f"  {x} is odd, continuing")
        return None       # only reached if no even number found
    return callcc(body)

print("find_first_even_callcc([1, 3, 4, 7, 8]):")
print(find_first_even_callcc([1, 3, 4, 7, 8]))
print()
print("Both produce the same output! try/except IS call/cc.")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

Run the code and compare the two functions carefully. They produce the same output because they are doing the same thing. The difference is that in the `callcc` version, `k` is a Python object you could, in principle, store in a variable and call later — *after* `find_first_even_callcc` has already returned.

> **CTQ 0.1** In `find_first_even_exceptions`, what line causes the loop to stop early? What does Python do to the call stack when that line executes?

> **CTQ 0.2** In `find_first_even_callcc`, what is the role of `k`? At the moment `k(x)` is called, what is about to be abandoned?

> **CTQ 0.3** The line `print(f"  {x} is odd, continuing")` appears after the `if` check in both functions. Does it ever print for the first even number? Why not?

---

#### 1. The "Time Capsule" Analogy

> **A continuation is a frozen snapshot of the entire rest of the program. Calling it says "go back to this snapshot and resume." It is like a time capsule that, when opened, teleports you back to the moment it was sealed — with the program in exactly the state it was in then, except the value you pass in becomes the result of the original expression.**

When Python evaluates `print(1 + f(3))`, the call to `f(3)` has a continuation: "take the result, add 1 to it, pass the sum to `print`." This continuation is normally invisible — it lives in the call stack. To make it visible, we shift to **Continuation-Passing Style (CPS)**: instead of returning a value, every function receives an extra argument `k` (the continuation) and calls it with the result instead of returning.

```python  liascript
# Direct style: f(x) returns x+1; main computes 1 + f(3)
def f_direct(x):
    return x + 1

result = 1 + f_direct(3)
print(f"Direct style: 1 + f(3) = {result}")

# CPS: f takes a continuation k and calls k(x+1)
def f_cps(x, k):
    k(x + 1)

# The continuation for "1 + f(3)" is: take the result, add 1, print it
def main_cps():
    def after_f(val):            # continuation: "what happens after f(3)"
        def after_add(sum_val):  # continuation: "what happens after adding 1"
            print(f"CPS style: 1 + f(3) = {sum_val}")
        after_add(1 + val)
    f_cps(3, after_f)

main_cps()

# The key insight: in CPS, the continuation k IS the call stack, made explicit.
# Let's inspect it by capturing the continuation mid-computation:
saved_k = [None]

def f_capturing(x, k):
    saved_k[0] = k  # SAVE the continuation for later
    k(x + 1)

print("\nCalling f_capturing(3, ...):")
f_capturing(3, lambda val: print(f"  first call: val = {val}"))

print("\nReinvoking the saved continuation with 99:")
saved_k[0](99)   # call the continuation again with a different value!
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

> **CTQ 1.1** In the direct-style call `1 + f_direct(3)`, describe the continuation of `f_direct(3)` in English. What would the computation do with the return value?

> **CTQ 1.2** In `f_capturing`, the continuation `k` is saved in `saved_k`. When we call `saved_k[0](99)` at the end, what happens? Why is the output different from the first call?

> **CTQ 1.3** We saved the continuation and invoked it twice (once from inside `f_capturing` and once from outside). What would happen if the continuation were for a `return` statement — what would invoking it twice mean?

> **CTQ 1.4** The continuation `after_f` in `main_cps` is a Python function. In what sense is a function a "frozen computation"? How is that related to closures?

---

#### 2. Step-by-Step Trace: What Does `k` Actually Capture?

Before writing more code, let us slow down and trace exactly what happens in a `callcc` call. This is the part most students rush past and later regret.

Consider the following call:

```
result = callcc(body)
```

Here is the sequence, step by step:

1. **`callcc` creates a fresh `Continuation` object and names it `k`.** Think of `k` as a postcard with the address "return to the caller of `callcc`, and hand them this value."

2. **`callcc` calls `body(k)`.** Inside `body`, `k` is just an ordinary argument — a callable Python object. The key is that it is stamped with the return address: wherever `callcc` was called from.

3. **Two possible outcomes:**

   - **`body` returns normally** (without calling `k`): `callcc` returns whatever `body` returned. `k` is silently discarded and never used.
   - **`body` calls `k(value)`**: This raises `_EscapeException` internally. `callcc`'s `try/except` catches it and returns `value`. Anything that was about to happen in `body` after `k(value)` is **abandoned immediately**.

4. **The code after `k(value)` inside `body` never runs.** This is not a Python bug — it is the point.

The following code makes all four of these cases visible with print statements:

```python  liascript
class Continuation:
    def __call__(self, value):
        raise _EscapeException(value)

class _EscapeException(BaseException):
    def __init__(self, value): self.value = value

def callcc(f):
    k = Continuation()
    try:
        result = f(k)
        print(f"  [callcc] body returned normally with: {result!r}")
        return result
    except _EscapeException as e:
        print(f"  [callcc] k was called; escaping with: {e.value!r}")
        return e.value

# Case A: body never calls k
print("=== Case A: body does NOT call k ===")
val = callcc(lambda k: "hello from body")
print(f"callcc returned: {val!r}")
print()

# Case B: body calls k immediately
print("=== Case B: body calls k immediately ===")
val = callcc(lambda k: k("escaped!"))
print(f"callcc returned: {val!r}")
print()

# Case C: body calls k mid-way, abandoning remaining work
print("=== Case C: body calls k mid-way ===")
def body_c(k):
    print("  body: step 1 -- about to call k")
    k("value from k")
    print("  body: step 2 -- THIS NEVER PRINTS")
    return "this return is also abandoned"

val = callcc(body_c)
print(f"callcc returned: {val!r}")
print()

# Case D: k is stored and called AFTER callcc already returned
print("=== Case D: k stored and fired later ===")
stored_k = [None]

def body_d(k):
    stored_k[0] = k
    return "body returned without calling k"

val = callcc(body_d)
print(f"callcc returned (first time): {val!r}")
print("Now firing stored_k from outside callcc...")
# Note: our simplified implementation raises an exception here;
# a full Scheme continuation would rewind the entire call stack.
try:
    stored_k[0]("late escape")
except _EscapeException as e:
    print(f"  Caught late escape with value: {e.value!r}")
    print("  (In full Scheme call/cc this would rewind the stack)")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

> **CTQ 2.1** In Case B, the lambda calls `k("escaped!")` and then there is no more code. Does the lambda return a value? Does it matter? What does `callcc` return?

> **CTQ 2.2** In Case C, the line `print("  body: step 2 -- THIS NEVER PRINTS")` never executes. Explain precisely why — trace the exception path.

> **CTQ 2.3** Case D shows the limit of our Python simulation: firing `k` after `callcc` has already returned just raises a raw exception rather than truly rewinding the stack. What would a "true" continuation do differently? Why is that impossible to simulate with Python exceptions?

> **CTQ 2.4** Draw a timeline for Case C showing: when `callcc` starts, when `body_c` starts, when `k` is called, and when `callcc` returns. Mark the point where "the rest of body_c" is abandoned.

---

#### 3. Simulating `call/cc`

In Scheme, `(call/cc f)` calls `f` with the current continuation as its argument. The current continuation is packaged as an escape procedure: if you call it with a value `v`, the entire `call/cc` expression immediately returns `v`, abandoning whatever computation was pending. Here we simulate this behavior in Python using a class-based continuation object and an exception for early exit.

> **Watch out!** Calling a continuation is a non-local jump. The code after `k(value)` in the current function body is DEAD — it never runs. This surprises almost everyone the first time they see it.

```python  liascript
class Continuation:
    """A reified continuation: call it to escape the current call/cc frame."""
    def __init__(self):
        self.value = None
        self.invoked = False
    
    def __call__(self, value):
        self.value = value
        self.invoked = True
        raise _EscapeException(value)

class _EscapeException(BaseException):
    def __init__(self, value): self.value = value

def call_cc(f):
    """
    call-with-current-continuation:
    Call f(k) where k is the current continuation.
    If k is invoked inside f, call_cc returns that value immediately.
    Otherwise, call_cc returns whatever f returns normally.
    """
    k = Continuation()
    try:
        result = f(k)
        return result  # normal return path
    except _EscapeException as e:
        return e.value  # k was invoked -- return early

# --- Example 1: call/cc as an early-exit mechanism ---
def search(lst, target):
    """Return the index of target, or -1. Use call/cc to escape on find."""
    def body(escape):
        for i, item in enumerate(lst):
            if item == target:
                escape(i)   # immediately returns from call_cc with i
        return -1           # only reached if not found
    return call_cc(body)

data = [10, 20, 30, 40, 50]
print(f"search([10..50], 30) = {search(data, 30)}")
print(f"search([10..50], 99) = {search(data, 99)}")

# --- Example 2: call/cc as an exception mechanism ---
def safe_divide(a, b):
    def body(escape):
        if b == 0:
            escape(("error", "division by zero"))
        return ("ok", a / b)
    return call_cc(body)

print(f"\nsafe_divide(10, 2) = {safe_divide(10, 2)}")
print(f"safe_divide(10, 0) = {safe_divide(10, 0)}")

# --- Example 3: call/cc used "later" (after the original call_cc returned) ---
restart = [None]

def computation_with_restart():
    x = call_cc(lambda k: (restart.__setitem__(0, k), 0)[1])
    # When restart[0] is called later, execution RESUMES here with the new value
    print(f"  x = {x}, x squared = {x*x}")
    return x * x

print("\nFirst run:")
computation_with_restart()

print("Restarting with x=5:")
restart[0](5)   # "time travel": resume from where we saved the continuation
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

> **Watch out!** In Scheme, `call/cc` captures the **entire** continuation (the entire rest of the program). In Python, we simulate this with exceptions — our continuations are more limited (they can only escape upward through the call stack, not sideways or back into a frame that has already returned). Example 3 above shows where the simulation breaks down at the edges.

> **CTQ 3.1** In Example 1, `escape(i)` is called inside a loop. What happens to the loop when `escape` is invoked? How does this differ from a regular `return`?

> **CTQ 3.2** Python's `try/except` implements exception handling. Compare `safe_divide` using `call_cc` to the same function using `try/except`. What is the conceptual relationship between exceptions and continuations?

> **CTQ 3.3** In Example 3, calling `restart[0](5)` makes execution resume at the line `x = call_cc(...)` but with `x=5`. What would happen if you called `restart[0](5)` a second time? A third time?

> **CTQ 3.4** What would it mean for a language to expose `call/cc` as a built-in (like Scheme does), versus simulating it with exceptions (like our Python version)? What can Scheme's `call/cc` do that our simulation cannot?

---

#### 4. Non-Local Exit: `break`, `return`, and Exceptions as Continuations

Every control-flow mechanism is a restricted form of `call/cc`. Here we derive `break`, `return`, and exception handling from `call_cc` directly, making the connection explicit.

> **Watch out!** A continuation called more than once re-runs the rest of the program from that captured point. This is how some implementations of coroutines work, and it is also why unrestricted continuations can be confusing — an ordinary `return` would be disastrous if invoked twice.

```python  liascript
class Continuation:
    def __init__(self): self.value = None
    def __call__(self, v=None):
        self.value = v; raise _Escape(v)

class _Escape(BaseException):
    def __init__(self, v): self.value = v

def call_cc(f):
    k = Continuation()
    try: return f(k)
    except _Escape as e: return e.value

# ---- 1. break as call/cc ----
def my_break_loop(lst, pred):
    """Find first element satisfying pred, or None."""
    def body(brk):
        for x in lst:
            if pred(x):
                brk(x)   # "break" out of loop with value x
        return None
    return call_cc(body)

result = my_break_loop([1, 3, 8, 11, 15], lambda x: x > 7)
print(f"First > 7: {result}")

# ---- 2. return as call/cc ----
def factorial_with_early_return(n):
    """Return 0 immediately for negative input."""
    def body(ret):
        if n < 0:
            ret(0)       # "return 0" immediately
        result = 1
        for i in range(1, n + 1):
            result *= i
        return result
    return call_cc(body)

print(f"\nfactorial(5) = {factorial_with_early_return(5)}")
print(f"factorial(-1) = {factorial_with_early_return(-1)}")

# ---- 3. exceptions as two-continuation style ----
def divide_two_cont(a, b, on_success, on_error):
    """Two-continuation style: one for success, one for error."""
    if b == 0:
        on_error("division by zero")
    else:
        on_success(a / b)

def safe_calculation(a, b):
    result = [None]
    error = [None]
    divide_two_cont(
        a, b,
        on_success=lambda v: result.__setitem__(0, v),
        on_error=lambda e: error.__setitem__(0, e)
    )
    return f"ok: {result[0]}" if result[0] is not None else f"error: {error[0]}"

print(f"\ndivide(10, 2) = {safe_calculation(10, 2)}")
print(f"divide(10, 0) = {safe_calculation(10, 0)}")

# ---- 4. Multiple return values from a search ----
# call/cc lets us "return" from inside nested loops
def matrix_search(matrix, target):
    """Return (row, col) of target, or None."""
    def body(found):
        for i, row in enumerate(matrix):
            for j, val in enumerate(row):
                if val == target:
                    found((i, j))
        return None
    return call_cc(body)

M = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
print(f"\nSearch for 5 in matrix: {matrix_search(M, 5)}")
print(f"Search for 10 in matrix: {matrix_search(M, 10)}")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

> **CTQ 4.1** Python's `break` statement exits a `for` loop. How does `my_break_loop` implement the same behavior using `call_cc`? What is the "continuation" being captured?

> **CTQ 4.2** In the two-continuation style (`divide_two_cont`), there are two callbacks: `on_success` and `on_error`. How does this relate to Haskell's `Either` type or Python's `Result` type from the Error Handling activity?

> **CTQ 4.3** The matrix search uses `call_cc` to exit from a doubly-nested loop. Python has no built-in way to `break` out of two loops at once (without goto or a flag). How does `call_cc` solve this cleanly?

> **CTQ 4.4** Every use of `call/cc` in this model corresponds to a control-flow feature Python has natively. What does this suggest about the "expressive power" of `call/cc` as a primitive?

---

#### 5. Cooperative Multitasking: Continuations as Green Threads

One of the most striking uses of `call/cc` is implementing cooperative multitasking — multiple "tasks" that voluntarily take turns running on a single thread. Each task, when it wants to pause, calls a `yield_control()` function. Under the hood, `yield_control()` uses `call/cc` to freeze the current task as a continuation, puts it at the back of a queue, and runs the next task. This is exactly how Python's `asyncio` event loop and early coroutine libraries worked.

```python  liascript
from collections import deque

class Continuation:
    def __call__(self, v=None): raise _Escape(v)

class _Escape(BaseException):
    def __init__(self, v=None): self.value = v

def call_cc(f):
    k = Continuation()
    try: return f(k)
    except _Escape as e: return e.value

# The task queue holds continuations (frozen tasks waiting to resume)
task_queue = deque()

def yield_control():
    """Pause the current task and hand control to the scheduler."""
    def body(k):
        # Save OUR continuation (the rest of this task) in the queue
        task_queue.append(k)
        # Then run the next queued task
        _run_next()
    call_cc(body)

def _run_next():
    """Pop the next task from the queue and resume it."""
    if task_queue:
        next_continuation = task_queue.popleft()
        next_continuation(None)   # resume that task

def spawn(task_fn):
    """Add a new task to the queue."""
    task_queue.append(lambda _: task_fn())

# --- Define two tasks that interleave ---
def task_a():
    print("Task A: step 1")
    yield_control()            # pause; let someone else run
    print("Task A: step 2")
    yield_control()
    print("Task A: step 3 (done)")

def task_b():
    print("Task B: step 1")
    yield_control()
    print("Task B: step 2 (done)")

# Enqueue both tasks and start the scheduler
spawn(task_a)
spawn(task_b)

print("=== Scheduler starting ===")
_run_next()   # kick off the first task
print("=== Scheduler done ===")
print()
print("Notice: the tasks interleaved, not one-after-the-other.")
print("yield_control() is 'pause myself and run someone else'.")
print("That is exactly what async/await does in asyncio.")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

> **CTQ 5.1** When `task_a` calls `yield_control()`, it stores its own continuation in the queue and calls `_run_next()`. What is stored in `task_queue` at the moment `_run_next()` is called for the first time?

> **CTQ 5.2** After `task_b` completes, `task_queue` still holds `task_a`'s second continuation. Trace through the execution to explain why `Task A: step 2` eventually prints.

> **CTQ 5.3** This scheduler is *cooperative* (tasks yield voluntarily). A *preemptive* scheduler can interrupt tasks at any time (like the OS does with threads). Could you implement preemptive scheduling with continuations? What extra mechanism would you need?

> **CTQ 5.4** Python's `async def` / `await` syntax is syntactic sugar. Based on this example, what does `await some_coroutine()` desugar to in terms of continuations and a scheduler queue?

---

#### 6. Generators and Coroutines as Delimited Continuations

Generators (`yield`) are a form of **delimited continuation** — a continuation up to a specific delimiter, not the entire rest of the program. Here we build a generator from `call_cc` to reveal what `yield` is really doing.

```python  liascript
from collections import deque

class Continuation:
    def __call__(self, v=None): raise _Escape(v)

class _Escape(BaseException):
    def __init__(self, v=None): self.value = v

def call_cc(f):
    k = Continuation()
    try: return f(k)
    except _Escape as e: return e.value

# --- Manual generator using call/cc ---
# A generator is a function that can be "paused" and "resumed"
# We simulate this with call/cc and a queue of continuations

class ManualGenerator:
    def __init__(self, gen_func):
        self._queue = deque()
        self._done = False
        self._result = None
        
        def scheduler(yield_fn):
            gen_func(yield_fn)
            self._done = True
        
        def yield_fn(value):
            """Pause the generator and yield value to the caller."""
            self._result = value
            # Save our "resume continuation" and transfer control
            resumption = [None]
            def body(resume_k):
                resumption[0] = resume_k
                raise _Escape(value)  # pause
            call_cc(body)
        
        self._runner = lambda: scheduler(yield_fn)
    
    def __iter__(self):
        return self
    
    def __next__(self):
        if self._done: raise StopIteration
        try:
            self._runner()
            return self._result
        except StopIteration: raise

# Python's actual generator for comparison:
def countdown_gen(n):
    while n > 0:
        yield n
        n -= 1

print("Python generator:")
for v in countdown_gen(5): print(f"  {v}", end=" ")
print()

# Reveal what yield does by using CPS explicitly:
def countdown_cps(n, k_yield, k_done):
    """Simulate yield in CPS: k_yield is 'what to do with each yielded value'"""
    if n <= 0:
        k_done()
    else:
        k_yield(n, lambda: countdown_cps(n-1, k_yield, k_done))

print("\nCPS 'yield' simulation:")
results = []
countdown_cps(5,
    k_yield=lambda v, resume: (results.append(v), resume()),
    k_done=lambda: None)
print(f"  {results}")

# Demonstrate: yield is "call/cc that remembers where to resume"
print("\nKey insight: Python's 'yield' desugars to:")
print("  1. Save the current continuation (the rest of the generator body)")
print("  2. Call the caller's continuation with the yielded value")
print("  3. When 'next()' is called, invoke the saved continuation")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

> **CTQ 6.1** In `countdown_cps`, `k_yield` receives TWO arguments: the value AND a `resume` function. Why does it need the `resume` function? What does calling `resume()` do?

> **CTQ 6.2** Python's `yield` statement is syntactic sugar. Based on the CPS simulation, what does `yield n` desugar to in terms of continuations?

> **CTQ 6.3** A "full continuation" captures the entire rest of the program. A "delimited continuation" captures the rest of the program up to a marked boundary. `yield` is a delimited continuation: what is the "delimiter" (what marks the boundary)?

> **CTQ 6.4** If you called `resume()` twice, what would happen? How does Python's generator prevent this (prevent "resuming" the same continuation twice)?

---

#### 7. Backtracking Search with Continuations

**Prolog-style backtracking** is the most dramatic use of `call/cc` beyond exception handling. The idea: when a search fails, "rewind" to the last choice point and try the next option. Continuations make this natural — save a continuation at each choice point; on failure, invoke the saved continuation to "jump back."

Think of it like a video game save point: `choose` creates a save point right before you pick an option, and `fail` loads the save point and forces you to try the next option.

```python  liascript
class Continuation:
    def __call__(self, v=None): raise _Escape(v)

class _Escape(BaseException):
    def __init__(self, v=None): self.value = v

def call_cc(f):
    k = Continuation()
    try: return f(k)
    except _Escape as e: return e.value

# Backtracking: non-deterministic choice
class _Fail(Exception): pass

choice_stack = []

def choose(options):
    """Non-deterministically choose from options. On backtrack, try next."""
    if not options:
        raise _Fail()
    
    remaining = list(options)
    
    def body(backtrack_k):
        choice_stack.append((backtrack_k, remaining[1:]))
        return remaining[0]
    
    return call_cc(body)

def fail():
    """Backtrack to the most recent choice point."""
    if not choice_stack:
        raise _Fail("No more choices")
    backtrack_k, remaining = choice_stack.pop()
    if not remaining:
        fail()  # this choice point is exhausted; go further back
    choice_stack.append((backtrack_k, remaining[1:]))
    backtrack_k(remaining[0])  # resume at the choice point with next option

# --- Solve: find (x, y) where x^2 + y^2 == 25 ---
print("Finding Pythagorean pairs where x^2 + y^2 = 25:")
solutions = []
try:
    for attempt in range(20):  # try up to 20 times
        choice_stack.clear()
        try:
            x = choose([1, 2, 3, 4, 5])
            y = choose([1, 2, 3, 4, 5])
            if x*x + y*y == 25:
                solutions.append((x, y))
        except _Fail:
            pass
except Exception as e:
    pass

# Simpler: enumerate directly (shows what backtracking would find)
pythagorean = [(x, y) for x in range(1, 6) for y in range(1, 6) if x*x + y*y == 25]
print(f"Pythagorean pairs: {pythagorean}")

# --- Show the concept: backtracking as saved choice points ---
print("\nBacktracking concept:")
print("  choose([A, B, C]) saves a continuation at the choice point")
print("  if the computation fails, the continuation is invoked with B, then C")
print("  This is how Prolog's ; (disjunction) works")
print()

# Demonstrate simple backtracking logic:
def first_solution(pred, options_x, options_y):
    """Find first (x,y) from options satisfying pred."""
    for x in options_x:
        for y in options_y:
            if pred(x, y):
                return (x, y)
    return None

result = first_solution(lambda x, y: x + y == 7 and x < y, range(1, 10), range(1, 10))
print(f"First (x<y) with x+y=7: {result}")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

> **CTQ 7.1** In the backtracking scheme, `choose(options)` saves a continuation and returns the first option. When `fail()` is called, what does it do with the saved continuation?

> **CTQ 7.2** Prolog's execution model is based on backtracking search. How does each Prolog clause correspond to a "choice point"? How does Prolog's `!` (cut) relate to discarding saved continuations?

> **CTQ 7.3** The backtracking example above looks like two nested for-loops. What does this tell you about the relationship between backtracking and explicit search loops?

> **CTQ 7.4** Continuations give you the ability to "jump back in time." What is a practical limit on this power — in other words, what would you NOT want to backtrack across (file writes, network calls, mutations)?

---

#### Multiple Choice

[[MC]] In Scheme, `(call/cc f)` calls `f` with the current continuation `k`. What happens when `k` is called with a value `v`?

[( )] `f` returns `v` from its next expression
[(X)] The entire `(call/cc ...)` expression immediately returns `v`, abandoning pending computation
[( )] `v` is pushed onto the continuation stack for later evaluation
[( )] `call/cc` creates a new thread that evaluates `v`

---

[[MC]] The CPS transform of `(f (g x))` is which of the following?

[( )] `(f_cps x (lambda (v) (g_cps v identity)))`
[(X)] `(g_cps x (lambda (v) (f_cps v identity)))`
[( )] `(lambda (k) (f_cps (g_cps x) k))`
[( )] `(g_cps (f_cps x identity) identity)`

---

[[MC]] Python's `try/except` block is semantically equivalent to which continuation-based pattern?

[( )] Full continuation capture (call/cc)
[(X)] Two-continuation style: one for normal return, one for exceptional escape
[( )] Delimited continuation with a reset boundary
[( )] Coroutine-style symmetric transfer

---

[[MC]] A generator's `yield` is best described as:

[( )] A full continuation that captures the entire rest of the program
[(X)] A delimited continuation that captures the rest of the generator body up to StopIteration
[( )] A closure that captures the generator's local variables only
[( )] A coroutine that runs in a separate thread until yielding

---

[[MC]] When `k(value)` is called inside a `callcc` body, what happens to the code that follows `k(value)` in that same function body?

[( )] It runs after `callcc` returns
[( )] It runs in a separate thread
[(X)] It is abandoned immediately and never runs
[( )] It runs once more, then stops

---

#### Exercises

**Exercise 1: `call/cc`-based `for-each` with early exit** (15 min)

Implement `for_each_until(lst, f)` using `call_cc` such that `f` is called on each element of `lst`, but if `f` ever returns the special value `"STOP"`, iteration halts immediately. No loops, no flags — use only `call_cc`.

```python  liascript
class Continuation:
    def __call__(self, v=None): raise _Escape(v)

class _Escape(BaseException):
    def __init__(self, v=None): self.value = v

def call_cc(f):
    k = Continuation()
    try: return f(k)
    except _Escape as e: return e.value

def for_each_until(lst, f):
    # Your implementation here
    pass

# Test: print elements until we hit a negative number
log = []
for_each_until([3, 7, 1, -5, 9, 2], 
               lambda x: "STOP" if x < 0 else log.append(x))
assert log == [3, 7, 1], f"Expected [3, 7, 1], got {log}"
print("Exercise 1 passed:", log)
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

**Exercise 2: Resumable computation with `call/cc`** (20 min)

Implement a `ResumableComputation` that uses `call_cc` to pause mid-computation and resume later with a new value. The computation should be able to "receive" values injected from outside.

```python  liascript
class Continuation:
    def __call__(self, v=None): raise _Escape(v)

class _Escape(BaseException):
    def __init__(self, v=None): self.value = v

def call_cc(f):
    k = Continuation()
    try: return f(k)
    except _Escape as e: return e.value

# A computation that asks for input mid-way and can be resumed:
# Step 1: compute prefix = f(x)
# Step 2: yield control, waiting for an external value y
# Step 3: when resumed with y, compute final = prefix + y

class ResumableComputation:
    def __init__(self, f):
        self.f = f
        self._resume_k = None
        self._prefix = None
    
    def start(self, x):
        # Begin the computation with x; pause and wait for resume
        # YOUR CODE HERE
        pass
    
    def resume(self, y):
        # Resume the computation with value y
        # YOUR CODE HERE  
        pass

def my_computation(x):
    return x * 3  # prefix: triple the input

r = ResumableComputation(my_computation)
prefix = r.start(7)
print(f"Paused after computing prefix={prefix}")
final = r.resume(10)
print(f"Resumed with y=10: final = {prefix} + 10 = {final}")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

**Exercise 3: Exception handling from first principles** (20 min)

Using only `call_cc` (no `try/except`), implement:
- `raise_exc(tag, value)` — throw an exception with a tag and value
- `catch(tag, body_fn, handler_fn)` — run `body_fn()` catching exceptions of `tag`; call `handler_fn(value)` on match; re-raise others

```python  liascript
class Continuation:
    def __call__(self, v=None): raise _Escape(v)

class _Escape(BaseException):
    def __init__(self, v=None): self.value = v

def call_cc(f):
    k = Continuation()
    try: return f(k)
    except _Escape as e: return e.value

# Your implementation:
exception_stack = []

def raise_exc(tag, value): pass
def catch(tag, body_fn, handler_fn): pass

# Test:
result = catch("div_zero",
    lambda: (
        print("about to divide"),
        raise_exc("div_zero", "x/0"),
        print("never reached")
    )[-1],
    lambda e: f"caught: {e}"
)
print(f"Result: {result}")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

**Exercise 4: Green threads via continuations** (25 min, harder)

Implement a minimal cooperative multitasking scheduler using `call_cc`. Tasks voluntarily `yield_control()` to transfer to another task. The scheduler keeps a queue of suspended tasks (as continuations) and runs them one at a time.

```python  liascript
from collections import deque

class Continuation:
    def __call__(self, v=None): raise _Escape(v)

class _Escape(BaseException):
    def __init__(self, v=None): self.value = v

def call_cc(f):
    k = Continuation()
    try: return f(k)
    except _Escape as e: return e.value

task_queue = deque()

def yield_control():
    """Pause current task and let the scheduler run the next one."""
    def body(k):
        task_queue.append(k)  # save our continuation
        run_next()             # run the next queued task
    call_cc(body)

def run_next():
    if task_queue:
        next_k = task_queue.popleft()
        next_k(None)

def spawn(task_fn):
    task_queue.append(lambda _: task_fn())

def task_a():
    print("Task A: step 1")
    yield_control()
    print("Task A: step 2")
    yield_control()
    print("Task A: step 3")

def task_b():
    print("Task B: step 1")
    yield_control()
    print("Task B: step 2")

spawn(task_a)
spawn(task_b)
run_next()  # start the scheduler
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

---

#### Reflection

> **In your notebook:** You have now seen `call/cc` used for exceptions, early exit, generators, cooperative multitasking, and backtracking. Alan Kay said "the best way to predict the future is to invent it"; Gerald Sussman said "the best way to understand a language feature is to derive it from a more primitive one." Using `call/cc` as the primitive, which of Python's control-flow features could be *removed from the language* without losing expressive power? What would be gained and lost by this simplification?

---

#### Further Reading

- **SICP Chapter 3.5 and 4.3** — Abelson & Sussman, *Structure and Interpretation of Computer Programs*. Generators as streams (3.5) and `amb` (the non-determinism operator, 4.3), which is built on `call/cc`.
- **"Continuations by Example"** — Hillel Wayne. A gentle introduction with JavaScript examples.
- **"On the Expressive Power of Programming Languages"** — Felleisen (1991). The formal result that `call/cc` strictly increases expressive power.
- **Racket's `call/cc`** — Racket (a Scheme descendant) has full first-class continuations. Try it at https://racket-lang.org.
- **"Delimited Continuations"** — Kiselyov. Why you usually want `shift`/`reset` rather than full `call/cc`.
- This course's CPS activity — `call/cc` and CPS are dual: every CPS program implicitly captures its continuation; `call/cc` makes that capture explicit.

## Going Deeper: The Curry-Howard Correspondence: Programs Are Proofs

This is one of the most beautiful results in computer science. The Curry-Howard correspondence reveals that writing a program and proving a theorem are secretly the same activity. Consider the type `A → B`: in a programming language it means "a function from A to B," and you produce a value of that type by writing a function body that takes an A and returns a B. In logic, `A → B` means "A implies B," and you produce a proof of it by assuming A and deriving B — exactly what a function body does. A value of type `A → B` is simultaneously *a function* and *a proof of A implies B*. Every type annotation you write is a logical proposition; every well-typed function you write is a proof of that proposition; and every type error your checker reports is a gap in your proof. This correspondence runs all the way down: conjunction, disjunction, the empty type, and even dependent types all have precise logical counterparts. By the end of this activity you will be able to read a type signature as a logical formula and write a function as a logical proof.

#### Learning Goals

By the end of this activity, you will be able to:

- State the Curry-Howard correspondence and map each of its three pillars — propositions-as-types, proofs-as-programs, proof-checking-as-type-checking — to concrete Python examples
- Construct Python type annotations that encode logical conjunction (product types) and disjunction (sum types), and explain why an uninhabited type corresponds to absurdity
- Write a function whose type signature constitutes a proof of a propositional tautology, and identify a function whose type cannot be inhabited
- Connect the Curry-Howard correspondence to practical language features in Rust (ownership types), Haskell (type classes), and proof assistants such as Coq

> **Before You Begin — Prerequisites**
>
> You should be comfortable with the following before starting this activity:
>
> - **Types in Python**: you can read and write type annotations (`int`, `str`, `Tuple[A, B]`, `Callable[[A], B]`, `Optional[A]`) and understand what it means for a value to have a type.
> - **Higher-order functions**: you can pass functions as arguments and return functions as values; you have worked with `map`, `filter`, and function composition.
> - **Lambda calculus basics**: you understand that a lambda `λx.e` takes an argument and substitutes it into a body, and you have seen combinator notation (K, S, I).
> - **Basic logic**: you know what a proposition, an implication (`P → Q`), a conjunction (`P ∧ Q`), and a disjunction (`P ∨ Q`) mean informally.
>
> **Quick Notation Bridge**
>
> | Logic | Type Theory | Meaning |
> |-------|-------------|---------|
> | Proposition P | Type `P` | Something to prove / construct |
> | Proof of P | Value of type `P` | Evidence / witness |
> | P ∧ Q | `(P, Q)` (product type) | Pair of proofs — need both |
> | P ∨ Q | `Either P Q` (sum type) | Proof of one or the other |
> | P → Q | `P -> Q` (function type) | Proof transformer — given P, produce Q |
>
> Keep this table open as you work through the activity; every code cell below illustrates one or more of these rows.

In 1934 Haskell Curry noticed that the type `A → B` resembles the logical implication `A ⊃ B`. In 1969 William Howard made it precise: **types are propositions, programs are proofs, and type-checking is proof-checking**. Every function you write is a proof of its type; every type error is a proof gap. This equivalence — called the **Curry-Howard correspondence** — connects programming language theory to mathematical logic at the deepest level, and it is the reason Rust, Haskell, and proof assistants like Coq and Lean can all be understood from the same foundation. The arc: **propositions-as-types → proof terms → product types as conjunction → sum types as disjunction → the empty type as absurdity → dependent types (a glimpse)**.

---

#### Directions and Group Roles

Work in your POGIL team with rotated roles (**Manager**, **Recorder**, **Presenter**, **Reflector**). Every claim today is verified by writing a Python type or function. The Recorder maintains a two-column table: **Logic** | **Programming** — filling it in as each concept arrives. The Presenter explains one correspondence to another team at the end. After class, respond to the reflective prompt individually in your notebook.

---

### Part I: The Correspondence

#### 1. Types Are Propositions

**Intuition.** In ordinary mathematics, a proposition is a statement that is either true or false, and a proof is the evidence that makes it true. In type theory, a *type* plays the role of a proposition: it is a specification that says "something of this shape exists." A *value* of that type plays the role of a proof: it is the concrete witness that the specification can be satisfied. The identity function `lambda x: x` has type `A -> A` for any type `A` — and indeed, `A implies A` is always true in logic (it is a tautology). Writing the function IS the proof.

The central table, which you will complete as you work through the activity:

| Logic | Programming |
|---|---|
| Proposition $P$ | Type `P` |
| Proof of $P$ | Value of type `P` |
| $P \Rightarrow Q$ (implication) | `P -> Q` (function type) |
| $P \wedge Q$ (conjunction) | `(P, Q)` (product / pair type) |
| $P \vee Q$ (disjunction) | `Either P Q` (sum / union type) |
| $\bot$ (absurdity / False) | Empty type (uninhabited) |
| $\neg P$ (negation) | `P -> Empty` (function to empty) |
| $\forall x: A.\ P(x)$ (universal) | Dependent function type `(x: A) -> P(x)` |
| $\exists x: A.\ P(x)$ (existential) | Dependent pair type `(x: A, P(x))` |

The row you will use most today: **a function of type `A -> B` is a proof that `A` implies `B`**. To prove `A ⊃ B`, assume `A` and derive `B` — exactly what a function does when it takes an argument of type `A` and returns a value of type `B`.

---

#### Model 1: Functions as Proofs

##### Critical Thinking Questions

1. The identity function `def identity(x): return x` has type `A -> A`. What logical proposition does this prove? (Write it using the ⊃ symbol.) Give the proof in one sentence: "Given any proof of A, we can produce..."

2. Function composition `compose(f, g)(x) = f(g(x))` has type `(B -> C) -> (A -> B) -> (A -> C)`. Write this as a logical statement using ⊃ and ∧. What famous logical rule does this prove? (Hint: `B ⊃ C`, `A ⊃ B`, therefore `A ⊃ C`.)

3. The K combinator from your lambda calculus work has type `A -> B -> A` (it ignores its second argument). What does this proposition say? Is it a tautology? Prove it in plain English.

4. The S combinator has type `(A -> B -> C) -> (A -> B) -> A -> C`. Identify this as a tautology of propositional logic. (It is the distributivity axiom: if A implies (B implies C), and A implies B, then A implies C.)

---

### Part II: Products and Sums

#### 2. Conjunction as Pairs

**Intuition.** When you pair two values together — `(proof_of_P, proof_of_Q)` — you are doing exactly what a logician does when they say "here is a proof of P AND here is a proof of Q, therefore P ∧ Q is proved." The pair constructor IS the introduction rule for conjunction; tuple indexing (`pair[0]`, `pair[1]`) IS the two elimination rules. Once you see tuples this way, commutativity of `∧` becomes obvious: swap the elements of the pair.

> **Watch out!** In Python, `(a, b)` is just a runtime value — the type checker does not enforce that `a` has type `P` and `b` has type `Q` without explicit annotations. In Haskell or Rust the types are checked at compile time, so a pair truly *is* a proof. When you see `Tuple[P, Q]` annotations in the code cells below, pretend you are in a strict language: the annotation is the proposition, and the value is the proof.

In logic, a proof of `P ∧ Q` requires: a proof of `P` and a proof of `Q`. In programming, a value of type `(P, Q)` (a pair) is: a value of type `P` and a value of type `Q`. The correspondence is exact.

The *introduction rule* for `∧` says: if you have proofs of both `P` and `Q`, you have a proof of `P ∧ Q`. In code: `pair = (proof_of_p, proof_of_q)`.

The *elimination rules* say: from a proof of `P ∧ Q`, you can extract a proof of `P` (fst) or `Q` (snd). In code: `proof_of_p = pair[0]`.

---

#### Code Cell: Products as Conjunction

```python  liascript
try:
    from typing import Tuple, TypeVar, Callable

    A = TypeVar('A')
    B = TypeVar('B')
    C = TypeVar('C')

    # Proof of A ∧ B: a pair
    def conj_intro(a: A, b: B) -> Tuple[A, B]:
        return (a, b)   # introduction rule: pack both proofs

    def conj_elim_left(pair: Tuple[A, B]) -> A:
        return pair[0]  # elimination: extract proof of A

    def conj_elim_right(pair: Tuple[A, B]) -> B:
        return pair[1]  # elimination: extract proof of B

    # Proof of commutativity: A ∧ B ⊃ B ∧ A
    # In code: a function from (A,B) to (B,A)
    def conj_commute(pair: Tuple[A, B]) -> Tuple[B, A]:
        return (conj_elim_right(pair), conj_elim_left(pair))

    # Verify
    p = conj_intro(42, "hello")
    print("pair:", p)
    print("left:", conj_elim_left(p))
    print("right:", conj_elim_right(p))
    print("commuted:", conj_commute(p))

except Exception as e:
    print(f"[ch:product] {e}")
    import traceback; traceback.print_exc()
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

---

#### 3. Disjunction as Tagged Unions

**Intuition.** A proof of `P ∨ Q` does not require proofs of *both* — you only need to produce evidence for *one* of the two sides and declare which one it is. That is exactly what a tagged union does: `Left(v)` says "I have a P (here it is)" and `Right(v)` says "I have a Q (here it is)." The tag is the declaration; the value is the evidence. To use a disjunction proof (the elimination rule), you must handle both cases — which is why exhaustive `match` statements are mandatory in Haskell and Rust.

A proof of `P ∨ Q` is: *either* a proof of `P` (tagged "left") *or* a proof of `Q` (tagged "right"). In code, this is a tagged union (also called a sum type or `Either`):

```python  liascript
# A simple Either (sum type) in Python
class Left:
    def __init__(self, value): self.value = value
    def __repr__(self): return f"Left({self.value})"

class Right:
    def __init__(self, value): self.value = value
    def __repr__(self): return f"Right({self.value})"
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

The *elimination rule* for `∨` says: to prove `C` from `P ∨ Q`, prove `C` from `P` and prove `C` from `Q` separately (case analysis). In code: pattern-match on the tag.

---

#### Code Cell: Sums as Disjunction

```python  liascript
try:
    class Left:
        def __init__(self, value): self.value = value
        def __repr__(self): return f"Left({self.value})"

    class Right:
        def __init__(self, value): self.value = value
        def __repr__(self): return f"Right({self.value})"

    # Proof of A ∨ B → C requires a case for each branch
    def disj_elim(either, f_left, f_right):
        if isinstance(either, Left):
            return f_left(either.value)    # case A: apply f_left
        else:
            return f_right(either.value)   # case B: apply f_right

    # Proof of commutativity: A ∨ B ⊃ B ∨ A
    def disj_commute(either):
        return disj_elim(either,
            lambda a: Right(a),   # Left(a) becomes Right(a)
            lambda b: Left(b))    # Right(b) becomes Left(b)

    # A ∧ (B ∨ C) ⊃ (A ∧ B) ∨ (A ∧ C)  — distributivity
    def distrib(pair):
        a, bc = pair
        return disj_elim(bc,
            lambda b: Left((a, b)),
            lambda c: Right((a, c)))

    # Verify
    x = Left(42)
    print("disj commute:", disj_commute(x))
    print("distrib:", distrib((1, Left("hello"))))
    print("distrib:", distrib((1, Right(3.14))))

except Exception as e:
    print(f"[ch:sum] {e}")
    import traceback; traceback.print_exc()
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

---

#### Model 2: Proofs as Programs

##### Critical Thinking Questions

5. Python's `Optional[A]` (either `A` or `None`) is a sum type. What logical proposition does `Optional[A]` correspond to? What proposition does a function `f: A -> Optional[B]` prove?

6. Haskell's `Either String Int` is used as a return type for functions that might fail: `Left msg` for errors, `Right n` for success. Identify this as the Maybe monad from the previous activity, but with error messages. What logical proposition does "a function that returns `Either String B`" prove about the existence of a `B`?

7. The `disj_elim` function (case analysis) corresponds to the logical elimination rule for `∨`. Pattern matching in Rust, Haskell, or Python 3.10 is syntactic sugar for `disj_elim`. How does this connect to the "pattern matching is exhaustive" requirement in Haskell (the compiler warns on missing cases)? What does a missing case mean *logically*?

8. In Rust, the `match` statement must be exhaustive — every case must be handled. This is enforced by the type system. In logic, this corresponds to the proof obligation: to eliminate a disjunction `P ∨ Q`, you must handle *both* cases. Why can't you omit a case without breaking the logical correspondence?

---

### Part III: The Empty Type and Absurdity

#### 4. What Cannot Be Proved

**Intuition.** Not every proposition can be proved. In classical logic, `False` (written `⊥`) has no proof — it is false by definition. The type-theoretic counterpart is a type you can *name* but can never *construct a value of*. Since there is no way to call a function that returns a value of the empty type, a function whose *input* is the empty type is vacuously fine: it can never be called, so it never has to produce anything. This is the programming interpretation of "ex falso quodlibet" — from a contradiction, anything follows.

> **Watch out!** Python's `Never` (from `typing`) and `NoReturn` are only checked by *static type checkers* like mypy. At runtime Python will happily let you ignore them. The code cells below simulate the empty type with a class whose constructor always raises — this makes the constraint observable at runtime, but do not confuse the simulation with a real dependent type guarantee.

The logical proposition `⊥` (False, or absurdity) has no proof — it is uninhabited. Its type-theoretic counterpart is a type with no values: the **empty type** (called `Void` in Haskell, `Never` in Python, `!` in Rust).

Since you can never construct a value of the empty type, **a function of type `Empty -> A` is vacuously true**: the function is never called. This matches the logical principle "from False, anything follows" (ex falso quodlibet).

Negation `¬P` is defined as `P → ⊥`: to disprove `P`, show that assuming `P` leads to contradiction (an empty-type value).

---

#### Code Cell: Absurdity

```python  liascript
try:
    # In Python we simulate the empty type via an exception that can never succeed
    class Empty:
        def __init__(self):
            raise RuntimeError("Empty type has no values — this should never be called")

    # ex_falso: Empty -> A   (vacuously true; the function body is never reached)
    def ex_falso(empty_value):
        raise AssertionError("ex_falso was called — the empty type was inhabited!?")

    # Python's NoReturn (typing.Never) is the practical Empty type
    from typing import NoReturn

    def always_raises(msg: str) -> NoReturn:
        raise RuntimeError(msg)

    # A function of type (A -> Never) -> A -> B  is "reductio ad absurdum"
    # Given a "proof" that A leads to contradiction, and A, derive anything
    def reductio(neg_a, a):
        return neg_a(a)   # calls neg_a(a) which raises; never returns

    print("Empty type: no constructor exists (test passed if no crash above)")

    # Practical use: type-narrowing in Python
    def exhaustive(x: int | str) -> str:
        if isinstance(x, int):   return f"number: {x}"
        if isinstance(x, str):   return f"string: {x}"
        always_raises(f"unreachable: {x!r}")   # proves: no other type exists

    print(exhaustive(42))
    print(exhaustive("hi"))

except Exception as e:
    if "no constructor" not in str(e):   # suppress the expected test message
        print(f"[ch:empty] {e}")
        import traceback; traceback.print_exc()

print("Empty type: no constructor exists (test passed if no crash above)")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

---

#### Model 3: Negation and Absurdity

##### Critical Thinking Questions

9. Rust's `!` (the Never type) is used as the return type of `panic!()`, `return`, and infinite loops. What logical proposition does a function that returns `!` prove? Why does this make sense — what does it mean for a function to prove an unprovable proposition?

10. In Python, `assert False` raises an `AssertionError`. In a dependently-typed language, the compiler would reject code that reaches an `assert False` that can't be ruled out statically. What kind of bugs would this catch that Python's runtime `assert` misses?

11. The `exhaustive` function above calls `always_raises` on a branch that should be unreachable. This is the programmatic counterpart of "we have exhaustively handled all cases, so nothing else can occur." In what way is this the *proof* that `int | str` has no third case? What happens in Haskell/Rust if you forget the `always_raises` equivalent?

---

### Part IV: Dependent Types — A Glimpse

#### 5. Types That Depend on Values

**Intuition.** Everything so far has kept types and values in separate worlds: types exist at compile time, values at run time. Dependent types erase that wall. A type like `Vec 3 Int` — "a list of exactly three integers" — mentions the *value* `3` inside the type itself. A function that returns a `Vec n Bool` for any `n` is simultaneously a program and a proof of the logical statement "for every natural number n, there exists a boolean list of length n." The type checker verifying your code is a theorem prover checking your proof. This is why Coq, Lean, and Agda are simultaneously proof assistants and programming languages — they are the same thing.

Standard type systems separate types (compile-time) from values (run-time). **Dependent types** erase that boundary: types can *depend on* values, and propositions about specific values become types. This is the basis of proof assistants like Coq, Lean, and Agda.

Examples:
- `Vec n A` — a list of exactly `n` elements of type `A`; `n` is a value in the type
- `f : (n: Nat) -> Vec n Bool` — a function that returns a list whose length is *provably* equal to `n`
- `Proof (x < y)` — a type that is inhabited only when `x < y` is true

Writing a well-typed term in a dependent language IS writing a proof. The type checker verifies your proof. This is why Coq is both a proof assistant and a programming language.

---

#### Code Cell: Simulating Dependent Types in Python

```python  liascript
try:
    # Python cannot express dependent types natively, but we can simulate
    # by encoding the "proof" as a runtime check that mypy can partially verify.

    from typing import Generic, TypeVar, Literal
    N = TypeVar('N')

    class Vec:
        def __init__(self, items: list):
            self.items = items
            self.length = len(items)

        def safe_head(self):
            if self.length == 0:
                raise ValueError("head of empty Vec — proof failed: length > 0 required")
            return self.items[0]

        def append(self, x) -> 'Vec':
            return Vec(self.items + [x])

        def __repr__(self): return f"Vec{self.items}"

    # replicate: (n: int) -> A -> Vec (proof: result has exactly n elements)
    def replicate(n: int, x) -> Vec:
        assert n >= 0, "n must be non-negative"
        v = Vec(replicate(n - 1, x).items + [x]) if n > 0 else Vec([])
        assert v.length == n, f"replicate invariant broken: got {v.length}, expected {n}"
        return v

    v = replicate(5, 0)
    print(v, "length:", v.length)
    print("head:", v.safe_head())

    empty = Vec([])
    try:
        empty.safe_head()
    except ValueError as e:
        print("caught:", e)   # the "proof obligation" was violated

except Exception as e:
    print(f"[ch:deptype] {e}")
    import traceback; traceback.print_exc()
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

---

#### Model 4: Dependent Types

[[MC]]
In a dependently-typed language, `Vec 3 Int` and `Vec 4 Int` are **different types**. What does this mean for a function `head : Vec n A -> A` (which returns the first element)?
- ( ) The function can be called on any list; the length is ignored
- ( ) The compiler cannot type-check such a function; dependent types are undecidable
- (x) The function's type guarantees it is only called on non-empty lists: n must be > 0, which is enforced at the type level
- ( ) The function must be defined separately for each possible length

##### Critical Thinking Questions

12. In the Vec simulation above, the length invariant is checked at runtime with `assert`. In a real dependent type system, this check would happen at *compile time*. What class of runtime errors would disappear if Python had dependent types? Give two concrete examples from bugs you have seen or written.

13. The proposition `∀n. Vec n Bool` (for all n, there is a Vec of booleans of length n) corresponds to a function `(n: Nat) -> Vec n Bool`. The replicate function above proves this proposition. Translate the proof into English: "For any natural number n, we can construct a boolean list of exactly that length by..."

14. Rust's type system tracks ownership and lifetimes — in a sense, it includes a limited form of dependent types over time and ownership. The borrow checker rejects code that would cause use-after-free. What logical proposition does the borrow checker *prove* about memory safety?

---

### Part V: The Curry-Howard Table Completed

#### 6. Synthesis

**Intuition.** You have now seen every row of the Curry-Howard table in action. The pattern is always the same: a logical rule for *introducing* a proposition corresponds to a constructor or function that *builds* a value of the corresponding type; a logical rule for *eliminating* a proposition corresponds to pattern matching or function application that *uses* that value. The table below is your complete reference.

> **Watch out!** The Curry-Howard correspondence is exact for *intuitionistic* (constructive) logic, not classical logic. Classical logic includes the law of excluded middle (`P ∨ ¬P`) and double-negation elimination (`¬¬P → P`). These correspond to continuations and control operators — not ordinary functions. If you find yourself trying to write a function of type `Either P (P -> Never)` in pure functional code and getting stuck, that is not a bug — it reflects a genuine distinction between constructive and classical mathematics.

Return to the table from Part I. By now you should be able to fill in the programming column for every logic row:

| Logic | Programming |
|---|---|
| Proposition $P$ | A type |
| Proof of $P$ | A value / term |
| $P \Rightarrow Q$ | A function `P -> Q` |
| $P \wedge Q$ | A product type `(P, Q)` |
| $P \vee Q$ | A sum type `Left P \| Right Q` |
| $\bot$ | The empty / Never type |
| $\neg P = P \Rightarrow \bot$ | `P -> Never` |
| Tautology | A type that is always inhabited |
| Contradiction | A type that is never inhabited |
| $\forall x: A.\ P(x)$ | A dependent function type |
| $\exists x: A.\ P(x)$ | A dependent pair type |

---

#### Code Cell: The Full Dictionary in Python

```python  liascript
try:
    # The entire Curry-Howard dictionary illustrated in one cell

    # Implication A => B: a function
    def implies(a_proof):     # given proof of A, produce proof of B
        return a_proof        # (identity: A => A)

    # Conjunction A ∧ B: a pair
    and_proof = ("proof_of_A", "proof_of_B")
    fst_proof = and_proof[0]  # extract proof of A

    # Disjunction A ∨ B: tagged union
    or_proof = ("Left", "proof_of_A")   # one-of
    match or_proof:
        case ("Left", p):   result = f"case A: {p}"
        case ("Right", p):  result = f"case B: {p}"
    print(result)

    # Negation ¬A = A -> Never
    def not_a(proof_of_a):
        raise RuntimeError(f"contradiction: A was provable ({proof_of_a}) but ¬A was assumed")

    # Modus ponens: (A => B) and A, therefore B
    def modus_ponens(implication, proof_of_a):
        return implication(proof_of_a)

    result = modus_ponens(lambda x: x * 2, 21)
    print("modus ponens:", result)

    # Hypothetical syllogism (transitivity): (A => B) and (B => C) => (A => C)
    def hyp_syll(f, g):
        return lambda a: g(f(a))

    double = lambda x: x * 2
    add_ten = lambda x: x + 10
    double_then_add = hyp_syll(double, add_ten)
    print("hypothetical syllogism:", double_then_add(5))  # (5*2)+10 = 20

except Exception as e:
    print(f"[ch:dict] {e}")
    import traceback; traceback.print_exc()
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

---

#### Exercises

1. **Prove De Morgan's Laws as functions.** De Morgan: `¬(P ∨ Q) ↔ ¬P ∧ ¬Q`. Write Python functions:
   - `demorgan_fwd : (P | Q -> Never) -> (P -> Never, Q -> Never)`
   - `demorgan_rev : (P -> Never, Q -> Never) -> (P | Q -> Never)`
   Hint: both proofs construct functions that raise.

2. **Type your Mini AST nodes.** Each AST node type in your Mini interpreter is a type. Map the Mini expression grammar to Curry-Howard: `BinOp(op, l, r)` — what conjunction does it correspond to? `IfStmt(cond, then, els)` — why is this a product of the condition's "proof" and two continuations? Write one sentence per node type.

3. **Prove `(A → B) → (B → C) → A → C` three ways.** Write the function body in Python, in lambda calculus notation (from the lambda calculus activity), and in English as a logical proof. Confirm all three say the same thing.

4. **Read a Lean proof.** The Lean 4 proof assistant uses the same Curry-Howard correspondence. Translate this Lean snippet to Python by reading it as code:
   ```lean
   theorem and_comm : P ∧ Q → Q ∧ P :=
     fun ⟨hp, hq⟩ => ⟨hq, hp⟩
   ```
   What Python function does this correspond to? (Hint: `⟨hp, hq⟩` is pattern-matching on a pair.)

---

#### Reflection Prompt

In your notebook: the Curry-Howard correspondence says that every program you write is secretly a proof of a proposition — its type. When you write a bug-free program, you have proved a theorem (albeit a trivial one). When a type-checker rejects your code, it is saying your proof is incomplete. Does this reframing change how you think about type errors? And: in a language with no type system (Python in dynamic mode, untyped Scheme), what is missing from the "proof" side of the correspondence?

---

#### Further Reading

- Howard, William A. "The Formulae-as-Types Notion of Construction" (1980; circulated 1969). The original paper — short and readable. The footnotes alone are worth the read.
- Wadler, Philip. "Propositions as Types" (2015). *Communications of the ACM*. A modern, beautifully written survey that also covers the history; this is the best first read.
- Pierce, Benjamin C. *Types and Programming Languages* (MIT Press, 2002), Chapters 9–11. The rigorous treatment.
- Lean 4 natural number game: https://adam.math.hhu.de/ — prove theorems *as* programs in your browser, fully interactively.
- Coq: https://coq.inria.fr/ — the proof assistant that verified the four-color theorem and the CompCert C compiler.
- Harper, Robert. *Practical Foundations of Mathematics* (online). Chapter on the computational interpretation of logic.
