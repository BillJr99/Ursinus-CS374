<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374-Fall2026/gh-pages/_pages/Activities/liascript-lambdacalculus2.md or locally via https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374-Fall2026/gh-pages/_pages/Activities/liascript-lambdacalculus2.md

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
- Derive a fixed-point combinator twice over, once by refactoring a self-applying factorial until the machinery separates from the logic, and once algebraically by solving $\textbf{Y}\, f = f\, (\textbf{Y}\, f)$ for a self-application
- Put any recursive function into generator form, taking the rest of the recursion as a parameter rather than calling itself by name
- Verify the fixed-point equation by hand reduction, and explain why $\textbf{Y}$ diverges under call-by-value while $\textbf{Z}$, one eta-expansion away, does not

> **Before You Begin**
>
> This activity builds directly on **Lambda Calculus, Part 1**.  Before starting, you should be comfortable with:
>
> - Writing and reading lambda expressions (e.g., `λx.λy. x`)
> - Performing beta reduction step by step
> - Distinguishing free variables from bound variables
> - Applying multi-argument (curried) functions
>
> If any of those feel shaky, review the [Lambda Calculus, Part 1 activity](liascript-lambdacalculus1.md) before continuing.

---

Everything you need to compute can be expressed with just functions.  Lambda calculus has no numbers, no booleans, no if-statements; yet Church showed how to encode ALL of these as pure lambda terms.  This activity builds that encoding from scratch in Python.

The calculus of *The Lambda Calculus, Part 1* had no numbers, no booleans, no data, and today we discover it needs none: **everything can be built from functions alone**.  Following the same path as Gabriel Lebec's "A Flock of Functions" (our companion reading, in JavaScript), we build booleans, then numbers, then arithmetic, verifying each construction by hand and in Python.  Today's path runs **named combinators $\rightarrow$ Church booleans $\rightarrow$ Church numerals $\rightarrow$ arithmetic as function surgery $\rightarrow$ recursion with no names at all**.

---

## Directions and Group Roles

Work in your POGIL team with your rotated roles (**Manager**, **Recorder**, **Presenter**, **Reflector**).  Whiteboard day again: every claimed equality gets a stepwise reduction or a Python verification, checked by a teammate.  After class, please respond to the reflective prompt on your own in your notebook.

---

# Part I: The Flock

## 1.  Combinators: Closed Terms with Names

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

You reduced **K** $A\, B \rightarrow A$ and **KI** $A\, B \rightarrow B$ in *The Lambda Calculus, Part 1* without their names.  Hold that thought; it is about to become the whole theory of truth.

---

## Model 1: Birdwatching

### Critical Thinking Questions

> **CTQ 1.1** Verify by reduction that $\textbf{C}\, \textbf{K}\, A\, B$ behaves exactly like $\textbf{KI}\, A\, B$. (The Cardinal of the Kestrel is the Kite: flipping "take the first" yields "take the second.")

> **CTQ 1.2** Write each combinator as a Python lambda (`K = lambda x: lambda y: x`, and so on) and verify question 1 by execution with strings for $A$ and $B$.

> **CTQ 1.3** Why must a combinator have no free variables to deserve a permanent name?  Connect to purity from the functional module.

---

# Part II: Truth, Built from Selection

> **Intuition before booleans:** An `if` does one job: select between two things.  So we will *define* the booleans as the selectors.  TRUE is a function that ignores its second argument: `lambda x: lambda y: x`.  FALSE is `lambda x: lambda y: y`.  If/then/else is just applying a boolean to two branches: write `b(then_branch)(else_branch)` and the boolean itself picks the right one.

## 2.  Church Booleans

An `if` does one job: select between two things.  So *define* the booleans as the selectors you already have:

$$
\textbf{TRUE} = \textbf{K} = \lambda x. \lambda y.\, x \qquad \textbf{FALSE} = \textbf{KI} = \lambda x. \lambda y.\, y
$$

Then `if b then t else e` is simply $b\, t\, e$: no special form needed, the boolean *is* the conditional.  Logic follows as function surgery:

$$
\textbf{NOT} = \lambda b.\, b\, \textbf{FALSE}\, \textbf{TRUE} \qquad
\textbf{AND} = \lambda p. \lambda q.\, p\, q\, p \qquad
\textbf{OR} = \lambda p. \lambda q.\, p\, p\, q
$$

> **Watch out!**  Church booleans are functions, not values. `TRUE(a)(b)` returns `a`: that is the entire definition.  The if-then-else `IF b t f = b(t)(f)` works because TRUE selects its first argument and FALSE selects its second.  There is no special conditional syntax; the boolean *is* the branch selector.

> **Watch out!**  Python's `lambda` returns single expressions.  For multi-argument Church terms, use curried lambdas: `lambda x: lambda y: x` not `lambda x,y: x`.  The curried form is what makes `TRUE(a)(b)` work, the first call returns another function that accepts `b`.

**Step-by-step reduction: NOT TRUE**

```
NOT TRUE
= (λb. b FALSE TRUE) (λx.λy. x)
->β (λx.λy. x) FALSE TRUE
->β (λy. FALSE) TRUE
->β FALSE  OK
```

**Step-by-step reduction: AND TRUE FALSE**

```
AND TRUE FALSE
= (λp.λq. p q p) TRUE FALSE
->β (λq. TRUE q TRUE) FALSE
->β TRUE FALSE TRUE
= (λx.λy. x) FALSE TRUE
->β (λy. FALSE) TRUE
->β FALSE  OK
```

**Decode helper, "peek inside" a Church boolean:**

```python
TRUE  = lambda x: lambda y: x
FALSE = lambda x: lambda y: y

def church_to_bool(b):
    return b(True)(False)

print("church_to_bool(TRUE)  =", church_to_bool(TRUE))
print("church_to_bool(FALSE) =", church_to_bool(FALSE))
```
@LIA.eval(`["main.py"]`, `none`, `python3 main.py`)

Hand a Church boolean `True` and `False` (Python's built-ins) as its two arguments.  Since TRUE selects its first argument it returns `True`; FALSE returns `False`.  This is your window into the encoding.

### Church Booleans; Runnable

```python
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
@LIA.eval(`["main.py"]`, `none`, `python3 main.py`)

---

## Model 2: Prove the Logic

### Critical Thinking Questions

> **CTQ 2.1** Reduce $\textbf{NOT}\, \textbf{TRUE}$ step by step to $\textbf{FALSE}$. (Substitute, then let TRUE select.)  The trace above is a guide; write your own with all substitutions made explicit.

> **CTQ 2.2** Reduce $\textbf{AND}\, \textbf{TRUE}\, \textbf{FALSE}$ and $\textbf{AND}\, \textbf{FALSE}\, \textbf{TRUE}$. Explain *why* `p q p` works in one sentence: when is the answer just "whatever q is," and when is it "p itself"?

> **CTQ 2.3** $\textbf{AND}$ never examines $q$ when $p$ is FALSE. Which semantics from the control-flow module did you just get *for free*, and why is it free here?

> **CTQ 2.4** Notice $\textbf{NOT} = \textbf{C}$ applied cleverly... actually, verify: does $\textbf{C}\, b$ flip a Church boolean's selections?  Reduce $\textbf{C}\, \textbf{TRUE}\, A\, B$ and compare with $\textbf{FALSE}\, A\, B$.

---

# Part III: Numbers as Repetition

> **Intuition before numerals:** Zero is "apply f zero times": `lambda f: lambda x: x`.  One is "apply f once": `lambda f: lambda x: f(x)`.  The number N is "apply f N times to x."  Addition is "apply f m+n times."  Multiplication is "apply (n copies of f) m times."  The number *is* the iteration count, there are no digits stored anywhere.

## 3.  Church Numerals

A number $n$ is encoded as *the act of doing something n times*:

$$
\textbf{0} = \lambda f. \lambda x.\, x \qquad
\textbf{1} = \lambda f. \lambda x.\, f\, x \qquad
\textbf{2} = \lambda f. \lambda x.\, f\, (f\, x) \qquad
\textbf{3} = \lambda f. \lambda x.\, f\, (f\, (f\, x))
$$

You met $\textbf{2}$ in *The Lambda Calculus, Part 1* as `twice`.  Arithmetic becomes composition of repetitions:

$$
\textbf{SUCC} = \lambda n. \lambda f. \lambda x.\, f\, (n\, f\, x) \qquad
\textbf{PLUS} = \lambda m. \lambda n. \lambda f. \lambda x.\, m\, f\, (n\, f\, x) \qquad
\textbf{MULT} = \lambda m. \lambda n. \lambda f.\, m\, (n\, f)
$$

Read PLUS aloud: "apply $f$ $n$ times to $x$, then $m$ more times."  Read MULT: "$n$ copies of $f$, repeated $m$ times."

> **Watch out!**  Church numerals look like iteration counts, not numbers. `TWO f x = f(f(x))` applies `f` twice to `x`.  The numeral does not "contain" the digit 2; it *is* the behavior of applying something twice.  This is why `church_to_int` works: you hand it the successor function on machine integers and the seed 0, and count how many times successor fires.

**Step-by-step reduction: SUCC ZERO reduces to ONE**

```
SUCC ZERO
= (λn.λf.λx. f (n f x)) (λf.λx. x)
->β λf.λx. f ((λf.λx. x) f x)
->β λf.λx. f ((λx. x) x)
->β λf.λx. f x
= ONE  OK
```


**Step-by-step reduction: PLUS TWO THREE reduces to FIVE**

`SUCC` shows the shape; addition shows why the encoding is more than a trick.  Recall `PLUS = λm.λn.λf.λx. m f (n f x)`: "apply `f` `m` times on top of applying it `n` times."

```
PLUS TWO THREE
= (λm.λn.λf.λx. m f (n f x)) (λf.λx. f (f x)) (λf.λx. f (f (f x)))

->β  (λn.λf.λx. TWO f (n f x)) THREE            substitute m := TWO
->β  λf.λx. TWO f (THREE f x)                   substitute n := THREE

    -- expand THREE f x first:
    THREE f x = (λf.λx. f (f (f x))) f x
    ->β (λx. f (f (f x))) x
    ->β f (f (f x))

->   λf.λx. TWO f (f (f (f x)))

    -- now expand TWO f applied to that:
    TWO f (f (f (f x))) = (λf.λx. f (f x)) f (f (f (f x)))
    ->β (λx. f (f x)) (f (f (f x)))
    ->β f (f (f (f (f x))))

->   λf.λx. f (f (f (f (f x))))
=   FIVE  OK                                    five applications of f
```

Count the `f`s at each stage: `THREE f x` contributes three, and `TWO f` wraps two more around them.  Addition of Church numerals is literally **function composition counted**, `m + n` applications of `f` because you applied `f` `n` times and then `m` more times to the result.  Nothing was added; things were nested.

Try `MULT TWO THREE = λf.λx. m (n f) x` on your own with the same method and watch why it gives six: `n f` is "apply `f` three times" treated as a *single* function, and `m` applies **that** twice.

**Decode helper, "peek inside" a Church numeral:**

```python
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
@LIA.eval(`["main.py"]`, `none`, `python3 main.py`)

Hand the numeral the successor function on Python ints and the seed 0.  If the numeral applies its function twice (as TWO does), you get `0 + 1 + 1 = 2`.  The number of applications is exactly the Church numeral's value.

---

## Church Encodings - Runnable

```python
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
EXP   = lambda m: lambda n: n(m)    # m^n; shockingly simple

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
@LIA.eval(`["main.py"]`, `none`, `python3 main.py`)

---

### Reading the Code

- Every "value" here is a function, and nothing else exists.  `TRUE` and `FALSE` are not booleans in disguise; they are *selectors*, and `IF` works by applying its condition to the two branches and letting the condition choose.
- `church_to_int` is a decoder, not part of the encoding.  A Church numeral `n` means "apply `f` to `x`, `n` times"; handing it Python's successor and `0` is only one way to read it back out.
- `SUCC` wraps one more application around whatever it was given, which is why numerals compose without any arithmetic anywhere in sight.
- `ISZERO` applies `lambda _: FALSE` exactly `n` times to `TRUE`.  Applied zero times the `TRUE` survives untouched; applied even once it is gone.  With no numbers available, that is the only way to ask "is this zero?".

### Try It Yourself

Build operators the deck has not given you, using nothing but functions.

```python
TRUE  = lambda x: lambda y: x
FALSE = lambda x: lambda y: y
IF    = lambda b: lambda t: lambda f: b(t)(f)

ZERO  = lambda f: lambda x: x
SUCC  = lambda n: lambda f: lambda x: f(n(f)(x))
ADD   = lambda m: lambda n: lambda f: lambda x: m(f)(n(f)(x))
MULT  = lambda m: lambda n: lambda f: m(n(f))

to_int  = lambda n: n(lambda k: k + 1)(0)
to_bool = lambda b: b(True)(False)

ONE, TWO = SUCC(ZERO), SUCC(SUCC(ZERO))
THREE    = SUCC(TWO)

print("=== What you already have ===")
print("  to_int(THREE)            = " + str(to_int(THREE)))
print("  to_int(ADD(TWO)(THREE))  = " + str(to_int(ADD(TWO)(THREE))))
print("  to_int(MULT(TWO)(THREE)) = " + str(to_int(MULT(TWO)(THREE))))

# TODO 1: AND, OR, NOT. A Church boolean IS a selector, so each of these
#         is written by choosing what p should select.
#         Hint for the first: AND = lambda p: lambda q: p(q)(p)
AND = lambda p: lambda q: p            # replace me
OR  = lambda p: lambda q: p            # replace me
NOT = lambda p: p                      # replace me

print("\n=== Your booleans (all True until you fix the stubs) ===")
for name, expr in [("AND(TRUE)(FALSE)", AND(TRUE)(FALSE)),
                   ("AND(TRUE)(TRUE)",  AND(TRUE)(TRUE)),
                   ("OR(FALSE)(TRUE)",  OR(FALSE)(TRUE)),
                   ("NOT(TRUE)",        NOT(TRUE))]:
    print("  " + name.ljust(20) + " = " + str(to_bool(expr)))
print("  want: False, True, True, False")

# TODO 2: POW(m)(n) is m to the power n, and it is SHORTER than MULT.
#         Think about what happens when you apply one numeral to another.
POW = lambda m: lambda n: m            # replace me
print("\n  to_int(POW(TWO)(THREE)) = " + str(to_int(POW(TWO)(THREE))) + "   (want 8)")

# TODO 3: to_int decodes by counting. Decode THREE a DIFFERENT way: hand it
#         a function that appends to a string, so THREE becomes "fff".
#         What does that tell you about what a numeral actually is?
```
@LIA.eval(`["main.py"]`, `none`, `python3 main.py`)

Expected output: the first three lines are 3, 5 and 6; your four booleans all print `True` because the stubs return `p`, and `POW` reports 2 instead of 8.  Fix the stubs and the wanted values appear.

## Model 3: Interrogate the Encodings

### Critical Thinking Questions

> **CTQ 3.1** `church_to_int` decodes a numeral by handing it the successor function on machine integers and the seed 0.  Explain why this works in one sentence that begins "A Church numeral n is...".

> **CTQ 3.2** Reduce $\textbf{SUCC}\; \textbf{1}$ by hand to confirm it is $\textbf{2}$ (expect two or three careful steps).  The trace for `SUCC ZERO` above is a model; repeat the pattern one numeral up.

> **CTQ 3.3** Verify in code that $\textbf{MULT}\, \textbf{2}\, \textbf{3}$ and $\textbf{PLUS}\, \textbf{3}\, \textbf{3}$ decode equally, then explain MULT's eerie brevity: what is `n(f)`, and what does `m` do *to that*?

> **CTQ 3.4** Where is the data?  A Church numeral stores no digits anywhere.  Connect this to homoiconicity week's lesson, and to the claim "data is frozen behavior."

Under Church encoding, the expression `b(t)(e)` where b is a Church boolean implements if-then-else because:

[( )] Python evaluates booleans specially
[(X)] TRUE and FALSE are themselves selector functions returning their first and second arguments respectively
[( )] The lambda calculus has a built-in conditional form
[( )] t and e must be numerals

---

# Part IV: Pairs and the Predecessor

> **Intuition before pairs:** A pair stores two values.  The pair itself is a function that takes a "selector": `lambda sel: sel(a)(b)`.  FST passes `lambda x: lambda y: x` (which is TRUE/K) to extract the first element; SND passes `lambda x: lambda y: y` (which is FALSE/KI) to extract the second.  You already built the selectors when you built booleans, pairs come for free.

## Model 4: Pairs and the Predecessor

**Church pairs: building linked data from functions:**

```python
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
@LIA.eval(`["main.py"]`, `none`, `python3 main.py`)

### Critical Thinking Questions

> **CTQ 4.1** The pair-based predecessor works by shifting: `(0,0) -> (1,0) -> (2,1) -> (3,2)`.  After applying shift $n$ times to $(0,0)$, what is the SND? Why does `PRED(ZERO)` return ZERO rather than negative one?

> **CTQ 4.2** Subtraction `m - n` is defined as "apply PRED n times to m."  What is `3 - 5` under this definition?  This is called *monus* (truncated subtraction).  Is this a bug or a deliberate design choice?

> **CTQ 4.3** You now have: booleans, conditionals, numerals, arithmetic, pairs.  What other data structures (lists, trees) could be built from Church pairs?  Sketch the encoding for a two-element list [a, b].

---

# Part V: Recursion Without Names

## 4.  The Problem: A Lambda Has No Name to Call

Every recursive function you have ever written works because a name was bound before the body ran.  `sumlist` calls `sumlist`; `fact` calls `fact`.  Take the names away and the trick stops working, and in the pure calculus there are no names to take away: there is no `define`, so at the instant you write a term down there is nothing yet to recurse *through*.

That is not a small gap.  Everything else on today's list survived the reduction to functions.  Booleans became selectors, numerals became repetition, pairs became a function holding two things.  Repetition itself is the one thing that looks like it needs something the calculus does not have.

State the goal precisely before pushing any symbols.  We want a term $\textbf{Y}$ such that, for every $f$,

$$
\textbf{Y}\, f \;=_\beta\; f\, (\textbf{Y}\, f)
$$

This is the **fixed-point equation**, and a term satisfying it is a **fixed-point combinator**.  Read it as a promise rather than a formula: if $f$ is a function that, handed "the rest of the recursion," produces one more layer of a recursive definition, then $\textbf{Y}\, f$ is that definition unrolled as far as anyone ever asks for it.

We are going to earn that term twice.  First we will build it from the ground up, starting from a factorial that cannot be written and fixing one problem at a time until a combinator falls out.  Then we will derive the same term backwards from the equation above in four lines, as a check that the construction was not a lucky accident.

> **Watch out!**  Nothing in this Part defines recursion in terms of recursion.  Every step is beta reduction, and the finished $\textbf{Y}$ is a closed term you could write on a whiteboard from memory.  If a step ever feels circular, find where the repeated subterm came from: it always came from *substituting*, never from calling something by name.

---

## 5.  Deriving the Combinator, One Honest Step at a Time

### Step 0: The Term You Cannot Write

Here is factorial, as you want to write it, using the encodings from Part III:

$$
\text{FACT} = \lambda n.\, \text{IF}\, (\text{ISZERO}\, n)\, \overline{1}\, (\text{MULT}\, n\, (\;???\;(\text{PRED}\, n)))
$$

The whole exercise is that box.  In Scheme, `define` puts `FACT` there before the body ever runs.  Here there is no `define`, the term has no name, and a term cannot refer to itself.  So stop trying to reach outward for a name, and ask instead what a lambda term *can* get at.

It can get at its arguments.  That is the only thing it can get at.

### Step 1: Hand the Function a Copy of Itself

If a function cannot reach itself, hand it itself.  Add a parameter for it and pass the whole term in as an ordinary argument:

$$
F = \lambda \textit{self}.\, \lambda n.\, \text{IF}\, (\text{ISZERO}\, n)\, \overline{1}\, (\text{MULT}\, n\, ((\textit{self}\ \textit{self})\, (\text{PRED}\, n)))
$$

Two things to notice.  The recursive call is $(\textit{self}\ \textit{self})$ rather than $\textit{self}$, because $\textit{self}$ arrives as a function still waiting to be handed a copy of itself.  And $F$ is not started by calling it on a number; it is started by applying it to itself, $F\, F$.

Watch the recursion appear out of pure substitution:

```
F F 3
= (λself. λn. IF (ISZERO n) 1 (MULT n ((self self) (PRED n)))) F 3
->β (λn. IF (ISZERO n) 1 (MULT n ((F F) (PRED n)))) 3      <- self := F
->β IF (ISZERO 3) 1 (MULT 3 ((F F) 2))
->β MULT 3 ((F F) 2)                                        <- (F F) again: back where we began
->β MULT 3 (MULT 2 ((F F) 1))
->β MULT 3 (MULT 2 (MULT 1 ((F F) 0)))
->β MULT 3 (MULT 2 (MULT 1 1))                              <- ISZERO 0 selects the base case
=  6                                                        OK
```

That is a working recursive factorial with no name anywhere in it.  The problem is solved.  What follows is entirely about making it *tolerable*, and it is worth being clear that everything after this point is refactoring rather than new power.

### Step 2: Hide the Self-Application Behind a Name

The body of $F$ is unpleasant because it says $(\textit{self}\ \textit{self})$ where a reader wants to see "factorial of."  The plumbing has leaked into the arithmetic.  So bind the plumbing to a local name.  There are no `let` forms here either, but a `let` is only an applied lambda, so write it as one:

$$
F = \lambda \textit{self}.\, \underbrace{(\lambda \textit{rec}.\, \lambda n.\, \text{IF}\, (\text{ISZERO}\, n)\, \overline{1}\, (\text{MULT}\, n\, (\textit{rec}\, (\text{PRED}\, n))))}_{\text{clean: this is just factorial}}\, \underbrace{(\lambda v.\, ((\textit{self}\ \textit{self})\, v))}_{\text{the plumbing}}
$$

The underbraced left half now reads exactly like factorial written with a helper called $\textit{rec}$.  The right half is the self-application, wrapped in $\lambda v$ so that it is handed along as a function rather than run on the spot.  Hold on to that wrapper; in Step 5 we throw it away, and in section 7 we discover it was load-bearing after all.

### Step 3: Lift the Logic Out

The clean half no longer mentions $\textit{self}$, so nothing keeps it inside $F$.  Pull it out and give it a name of its own:

$$
G = \lambda \textit{rec}.\, \lambda n.\, \text{IF}\, (\text{ISZERO}\, n)\, \overline{1}\, (\text{MULT}\, n\, (\textit{rec}\, (\text{PRED}\, n)))
$$

$$
F = \lambda \textit{self}.\, G\, (\lambda v.\, ((\textit{self}\ \textit{self})\, v))
\qquad\qquad
\text{FACT} = F\, F
$$

$G$ is the **generator**, and it is the payoff of the whole exercise.  It is not recursive.  It does not mention its own name, because it does not have one.  It is a perfectly ordinary function of one argument that happens to call whatever it is handed, and every recursive function you will ever write can be put in this shape.

### Step 4: Abstract Over the Generator

$F$ mentions $G$ only because we typed $G$ there.  Nothing about $F$ is specific to factorial, so make $G$ a parameter and inline $F$ into $F\, F$:

$$
\textbf{Z} = \lambda f.\, (\lambda x.\, f\, (\lambda v.\, ((x\, x)\, v)))\, (\lambda x.\, f\, (\lambda v.\, ((x\, x)\, v)))
$$

and now $\text{FACT} = \textbf{Z}\, G$.  This is a combinator: closed, generic, and finished.  Hand it any generator and it hands you back the recursive function that generator describes.  Nothing about factorials survives in it.

### Step 5: Strip the Delay

One piece is still unexplained.  What is $\lambda v.\, ((x\, x)\, v)$ doing?  It takes an argument and passes it straight to $(x\, x)$, unchanged.  It computes nothing.

In the pure calculus, $\lambda v.\, (M\, v)$ and $M$ are interchangeable whenever $v$ is not free in $M$; that is the **eta rule**.  So delete the wrapper:

$$
\textbf{Y} = \lambda f.\, (\lambda x.\, f\, (x\, x))\, (\lambda x.\, f\, (x\, x))
$$

That is the Y combinator, and notice how it arrived: not invented, but left behind when the last piece of scaffolding was removed.  $\textbf{Y}$ is $\textbf{Z}$ with an eta-expansion undone, which is worth remembering, because section 7 is about the one situation in which undoing it is a catastrophe.

---

## Model 5: The Five Steps, Running

Every step above is executable.  Run the cell and watch the machinery separate itself from the factorial one line at a time; each `print` corresponds to one numbered step.

```python
# The derivation, each step runnable, so you can watch the machinery
# separate itself from the factorial one line at a time.

# Step 0 does not appear here, because it cannot be written:
#     lambda n: 1 if n == 0 else n * ???(n - 1)
# There is no name to put where ??? is.

# Step 1: hand the function a copy of itself, as an ordinary argument.
step1 = lambda self, n: 1 if n == 0 else n * self(self, n - 1)
print("step1 :", step1(step1, 5), "  called as step1(step1, 5)")

# Step 1, curried, one argument at a time, as the calculus insists.
# 'self' is a function you must apply to itself before you can use it.
step1c = lambda self: lambda n: 1 if n == 0 else n * self(self)(n - 1)
print("step1c:", step1c(step1c)(5), "  called as step1c(step1c)(5)")

# Step 2: the body is ugly because self(self) is spelled out inside it.
# Bind that self-application to a name so the body reads like factorial.
step2 = lambda self: (
    lambda rec: lambda n: 1 if n == 0 else n * rec(n - 1)
)(lambda v: self(self)(v))
print("step2 :", step2(step2)(5), "  the inner body now says rec(n - 1)")

# Step 3: that inner body never mentions self, so lift it out.  fact_gen is
# pure factorial logic: not recursive, no name of its own, calls what it gets.
fact_gen = lambda rec: lambda n: 1 if n == 0 else n * rec(n - 1)
step3 = lambda self: fact_gen(lambda v: self(self)(v))
print("step3 :", step3(step3)(5), "  logic and machinery now separate")

# Step 4: step3 mentions fact_gen only because we typed it there.  Abstract
# over it and nothing about factorial is left.  What remains is a combinator.
Z = lambda f: (lambda x: f(lambda v: (x(x))(v)))(
               lambda x: f(lambda v: (x(x))(v)))
print("step4 :", Z(fact_gen)(5), "  Z(fact_gen), and Z knows nothing of factorials")

# Proof that nothing about factorial survived: hand Z other generators.
fib_gen = lambda rec: lambda n: n if n < 2 else rec(n - 1) + rec(n - 2)
sum_gen = lambda rec: lambda xs: 0 if not xs else xs[0] + rec(xs[1:])
print()
print("Z(fib_gen)(10)           =", Z(fib_gen)(10))
print("Z(sum_gen)([1, 2, 3, 4]) =", Z(sum_gen)([1, 2, 3, 4]))

# Expected output:
# step1 : 120   called as step1(step1, 5)
# step1c: 120   called as step1c(step1c)(5)
# step2 : 120   the inner body now says rec(n - 1)
# step3 : 120   logic and machinery now separate
# step4 : 120   Z(fact_gen), and Z knows nothing of factorials
#
# Z(fib_gen)(10)           = 55
# Z(sum_gen)([1, 2, 3, 4]) = 10
```
@LIA.eval(`["main.py"]`, `none`, `python3 main.py`)

### Reading the Code

- Every step prints `120`.  That is the point: no step adds power, and steps 2 through 4 are refactoring.  All the difficulty lives in step 1, and step 1 is three tokens long.
- `step1` and `step1c` differ only in currying.  Python lets you write `self(self, n - 1)` with a comma; the calculus does not have commas, so `(self self) (PRED n)` is the honest spelling and `step1c` is the one to compare against the math.
- `fact_gen` is the shape worth memorizing.  It takes `rec` and calls `rec(n - 1)` exactly where a recursive call belongs, and it is not recursive itself.  Any recursive function can be bent into this shape mechanically.
- `Z(fib_gen)` and `Z(sum_gen)` are the argument that step 4 actually finished the job.  If any trace of factorial had survived in `Z`, those two lines could not work.

### Critical Thinking Questions

> **CTQ 5.1** Take the reduction of `F F 3` in Step 1 and continue it for `F F 4`, writing every substitution.  At which arrow does the term `(F F)` reappear, and what would happen to the reduction if `ISZERO` never selected the base case?

> **CTQ 5.2** Step 2 claims the two halves are "clean" and "plumbing."  Circle every occurrence of $\textit{self}$ in Step 2's term.  How many are in the clean half?  Why does that number make Step 3 possible?

> **CTQ 5.3** Write `sum_gen` for Scheme lists rather than Python lists, in the same shape as `fact_gen`, using `null?`, `car`, and `cdr`.  Then say in one sentence what `rec` is standing in for.

---

## 6.  The Same Term, Derived Backwards from the Equation

The construction above is honest but long.  Now that we know what we are looking for, here is the four-line derivation, working from the fixed-point equation rather than from a factorial.

We want a $\textbf{Y}$ with $\textbf{Y}\, f = f\, (\textbf{Y}\, f)$.  The only device we have for making a term reproduce itself is self-application, which Part 1 showed us in $\Omega = (\lambda x.\, x\, x)\, (\lambda x.\, x\, x)$.  So guess that $\textbf{Y}\, f$ is a self-application, write $\textbf{Y} = \lambda f.\, W\, W$, and solve for $W$:

```
Want:   W W  =  f (W W)

Read it as a specification for W: applied to an argument x,
W must return f applied to (x x).  Write exactly that down:

        W  =  λx. f (x x)

Check it, by substituting W for x:

        W W = (λx. f (x x)) (λx. f (x x))
            ->β f ((λx. f (x x)) (λx. f (x x)))
             =  f (W W)                          OK

So      Y  =  λf. (λx. f (x x)) (λx. f (x x))
```

The same term the construction produced, arrived at from the other end.  $\Omega$ was the raw material both times: Step 1's $F\, F$ is a self-application, and so is $W\, W$.  The difference between $\Omega$ and $\textbf{Y}$ is only that $\textbf{Y}$ leaves a place for $f$ to do work on the way around the loop.

**The full reduction, with every substitution named**

```
Y = λf. W W          where W = λx. f (x x)

Y f
= (λf. (λx. f (x x)) (λx. f (x x))) f
->β (λx. f (x x)) (λx. f (x x))          <- substitute f for the bound f
                                            this is W W
->β f ((λx. f (x x)) (λx. f (x x)))      <- substitute W for x in f (x x)
=  f (W W)
=  f (Y f)                                OK
```

Keep going and the pattern is the whole story of recursion:

```
Y f  ->β* f (W W)
     ->β* f (f (W W))
     ->β* f (f (f (W W)))
     ->β* ...
```

Each arrow wraps one more $f$ around the same self-applying core.  Nothing decides to stop, and nothing ever will: the *term* has no normal form.  What stops is the *computation*, when some $f$ finally ignores the argument it was handed because `ISZERO n` selected the base case.  That is a real and useful distinction, and it is worth saying out loud: a divergent term can compute a terminating function, so long as evaluation never demands the divergent part.

> **Watch out!**  "$\textbf{Y}$ has no normal form" and "$\textbf{Y}\, f$ never terminates" are different claims, and only the first is true.  Under normal-order reduction, `Y fact-gen 3` gets to 6 in finitely many steps, because the base case discards the unexpanded remainder before it is ever needed.

---

## 7.  Strictness: Why Y Hangs and Z Does Not

Everything in section 6 chose to contract the outermost redex first, which is **normal order**.  Scheme, Python, JavaScript, and nearly every language you will be paid to write are **call-by-value**: an argument is reduced to a value before the function receiving it runs.

Under that rule, $\textbf{Y}$ is a disaster, and it fails before $f$ ever executes a single instruction:

```
Y f
->β W W                    where W = λx. f (x x)
->β f (W W)                to call f, first reduce its ARGUMENT (W W):
      W W ->β f (W W)      to call f, first reduce its argument (W W):
        W W ->β f (W W)    ...
                           f is never applied to anything.  No base case is
                           ever tested, because no test is ever reached.
```

The loop is not in the factorial.  It is in the machinery, and it spins before the factorial gets a turn.

Now put back the wrapper we deleted in Step 5, and follow the same rule:

```
Z f
->β V V                    where V = λx. f (λv. ((x x) v))
->β f (λv. ((V V) v))      the argument to f is now a LAMBDA.  A lambda is
                           already a value, so call-by-value stops right
                           here and hands it to f, which runs.          OK
```

That is the entire fix.  $\lambda v.\, ((x\, x)\, v)$ computes nothing, but it is a *value*, and under call-by-value the difference between a value and a computation is the difference between stopping and not stopping.  The self-application inside it happens later, when the recursive call is actually made on a real argument $v$.

So the two combinators sit exactly one eta step apart, and which one you want is decided entirely by your evaluation order:

| | $\textbf{Y} = \lambda f.\, (\lambda x.\, f\, (x\, x))\, (\lambda x.\, f\, (x\, x))$ | $\textbf{Z} = \lambda f.\, (\lambda x.\, f\, (\lambda v.\, ((x\, x)\, v)))\, (\lambda x.\, f\, (\lambda v.\, ((x\, x)\, v)))$ |
|---|---|---|
| Normal order / lazy (Haskell) | works | works |
| Call-by-value (Scheme, Python) | diverges immediately | works |
| Difference | one eta-expansion | |

> **Watch out!**  "Y does not work" is the wrong lesson to take away.  $\textbf{Y}$ works perfectly; our machines' evaluation order does not suit it.  That distinction matters because your December language will have to choose an evaluation order, and this is one of the first places where that choice becomes visible to an ordinary programmer.

---

## Model 6: Y, Z, and the Order of Evaluation

```python
# Y and Z in Python.  Python is call-by-value, exactly like Scheme, so this
# cell is a fair test of the claim section 7 makes about Y.
import sys

# The classical Y, transcribed straight off the lambda term.
Y = lambda f: (lambda x: f(x(x)))(lambda x: f(x(x)))

# Z: the same term with each self-application wrapped in one more lambda.
Z = lambda f: (lambda x: f(lambda v: (x(x))(v)))(lambda x: f(lambda v: (x(x))(v)))

# The generator from Step 3.  Notice what is NOT in it: fact_gen never
# mentions its own name.  It takes the rest of the recursion as a parameter.
fact_gen = lambda self: lambda n: 1 if n == 0 else n * self(n - 1)

factorial = Z(fact_gen)
print("Z: factorial(0) =", factorial(0))
print("Z: factorial(5) =", factorial(5))

# The same machinery with two recursive calls instead of one.
fib_gen = lambda self: lambda n: n if n < 2 else self(n - 1) + self(n - 2)
print("Z: fib(10)      =", Z(fib_gen)(10))

# Now watch Y fail, for exactly the reason section 7 gives.  Note where it
# fails: building Y(fact_gen) is already enough.  We never get to call it.
sys.setrecursionlimit(300)
try:
    Y(fact_gen)
    print("Y: built a function (this does not happen in a strict language)")
except RecursionError:
    print("Y: RecursionError before f ran even once")
sys.setrecursionlimit(1000)

# Expected output:
# Z: factorial(0) = 1
# Z: factorial(5) = 120
# Z: fib(10)      = 55
# Y: RecursionError before f ran even once
```
@LIA.eval(`["main.py"]`, `none`, `python3 main.py`)

The same three definitions in Scheme, where they sit closer to the lambda terms because Scheme's `lambda` *is* the calculus's abstraction:

```scheme
; The Z combinator, transcribed from the term in section 7.
(define Z
  (lambda (f)
    ((lambda (x) (f (lambda (v) ((x x) v))))
     (lambda (x) (f (lambda (v) ((x x) v)))))))

; fact-generator is not recursive.  It takes "self" as a parameter and calls
; (self n) wherever a recursive call belongs.  It never names itself.
(define fact-generator
  (lambda (self)
    (lambda (n)
      (if (= n 0)
          1
          (* n (self (- n 1)))))))

(define factorial (Z fact-generator))

(factorial 5)                ; 120
(factorial 0)                ; 1
```

**Step-by-step: (factorial 3)**

```
(Z fact-generator)
 = (fact-generator self)          where self = (lambda (v) ((x x) v))
 = (lambda (n) (if (= n 0) 1 (* n (self (- n 1)))))

(factorial 3)
->  (* 3 (self 2))               ; calling self unfolds Z one more level
->  (* 3 (* 2 (self 1)))
->  (* 3 (* 2 (* 1 (self 0))))
->  (* 3 (* 2 (* 1 1)))          ; n = 0, base case, self is never called again
=   6                                                                       OK
```

### Reading the Code

- `fact-generator` is a plain function of one argument with no state, no mutation, and no name pointing back at itself.  Every recursive function you have written before today needed that name.  This one does not, and that is the whole result.
- Each call to `self` is another application of `Z` to `fact-generator`, which is the fixed-point equation $(\textbf{Z}\, f) = (f\, (\textbf{Z}\, f))$ being cashed in one unfolding at a time.  The trace above is that equation, four times.
- The recursion stops because `n = 0` selects the `1` branch and `self` is simply not called.  Delay is not what makes it terminate; delay is what keeps the *machinery* from running away before the base case can be tested.
- `(lambda (v) ...)` is the only textual difference between `Y` and `Z`, and in a strict language it is the difference between a factorial and a hung REPL.

### Critical Thinking Questions

> **CTQ 6.1** Section 6 derived $\textbf{Y}$ in four lines and section 5 took five steps.  What does the long derivation tell you that the short one does not?  Answer in terms of what a student could reconstruct from memory a week later.

> **CTQ 6.2** Write `fib-generator` in Scheme, in the same shape as `fact-generator`, and hand it to `Z`.  It has two recursive calls rather than one.  Does anything about `Z` have to change?  Predict first, then check.

> **CTQ 6.3** $\lambda v.\, (M\, v)$ and $M$ are interchangeable in the calculus, yet swapping one for the other turns a working factorial into a hang.  How can two terms be equal and still behave differently?  Say exactly what "equal" is quantifying over, and what it says nothing about.

> **CTQ 6.4** In the simply typed lambda calculus, $x\, x$ cannot be assigned a type at all, so $\textbf{Y}$ is not typable and every well-typed program terminates.  Connect this to the *Type Systems* activity: what did the type system buy, what did it cost, and by what mechanism do Haskell and ML get recursion back?

> **CTQ 6.5** `fact-generator` receives the rest of the recursion as a parameter.  `make-counter`, from the Scheme activity, got its persistence from `set!` on a captured variable instead.  Both supply something the bare calculus lacks.  Which would you rather explain to a first-year student, and which would you rather implement in your interpreter?  They need not be the same answer.

> **CTQ 6.6** Your tree-walking interpreter has to make recursion work somehow.  Find the place in it where a function's own name becomes visible inside its body, and say whether your implementation is closer to $\textbf{Z}$ or closer to `set!`.  Put the answer in `SEMANTICS.md` in one sentence.

### Try It Yourself

```python
# Start from the Model 6 cell.

# TODO 1: write mult_gen so that Z(mult_gen) multiplies two numbers using
#         only addition and recursion.  The generator takes exactly one
#         parameter, so you must decide where the second argument goes.

# TODO 2: instrument Z so it prints one line every time self is called.
#         Run factorial(4) and count the lines.  Does the count match the
#         hand trace in Model 6?

# TODO 3: define Y_lazy, a version of Y that works in Python by delaying the
#         WHOLE call site rather than the self-application.  Compare it with
#         Z and say which one you would put in a language specification.
```
@LIA.eval(`["main.py"]`, `none`, `python3 main.py`)

---

**In-class work stops here.**  Everything below is homework and going-deeper material; attempt the exercises before the related assignment.

# Check Your Understanding

`TRUE = \x.\y.x` and `FALSE = \x.\y.y`. A Church boolean is best described as:

[(X)] A selector: a function that picks one of the two things handed to it
[( )] A number in disguise, 1 for true and 0 for false
[( )] A primitive the lambda calculus provides
[( )] A pair whose first element is a flag

---

`IF = \b.\t.\f. b t f` works because:

[(X)] The boolean itself does the choosing; `IF` only hands it the two branches
[( )] It compares `b` against `TRUE`
[( )] It evaluates both branches and discards one
[( )] It relies on short-circuit evaluation

---

The Church numeral `THREE` is:

[(X)] A function that applies its first argument to its second, three times
[( )] The literal 3, encoded in binary
[( )] A list of three elements
[( )] A pair of `TWO` and `SUCC`

---

`ISZERO n` applies `\_.FALSE` to `TRUE`, `n` times. That decides zero because:

[(X)] Applied zero times the `TRUE` is never replaced; applied any positive number of times it becomes `FALSE`
[( )] It compares `n` against `ZERO` directly
[( )] `FALSE` absorbs any further application
[( )] Church numerals carry a zero flag

---

`PRED` is far harder than `SUCC` because:

[(X)] A numeral can only build applications outward, so removing one means rebuilding the count, classically with a pair that lags one behind
[( )] Subtraction is undefined on natural numbers
[( )] It requires the Y combinator
[( )] `SUCC` is not invertible in principle

---

The lambda calculus needs a fixed-point combinator because:

[(X)] A term has no name at the moment it is written, so a function cannot call itself by name
[( )] Beta reduction cannot express repetition
[( )] Church numerals are too weak to count loop iterations
[( )] Substitution is not powerful enough to duplicate a term

---

$\textbf{Y}$ diverges in Scheme but $\textbf{Z}$ does not, because:

[(X)] Scheme evaluates arguments before calling, so Y's inner `(x x)` re-triggers before `f` can reach its base case; Z's extra lambda makes that self-application a value instead
[( )] Z has a base case built into it and Y does not
[( )] Y is not a closed term, so Scheme cannot bind its free variables
[( )] Scheme's `lambda` is not the same construct as the calculus's abstraction

---

## 8.  Exercises

1.  *Pairs.*  Define $\textbf{PAIR} = \lambda a. \lambda b. \lambda f.\, f\, a\, b$, with $\textbf{FST} = \lambda p.\, p\, \textbf{K}$ and $\textbf{SND} = \lambda p.\, p\, \textbf{KI}$. Verify in Python, then say what data structure you just built from nothing, and what your AST could, in principle, be encoded as.
2.  *IS-ZERO.* Define $\textbf{ISZERO} = \lambda n.\, n\, (\lambda x.\, \textbf{FALSE})\, \textbf{TRUE}$ and verify on 0, 1, 2.  Explain the trick: what happens to TRUE if $f$ is applied even once?
3.  *XOR.* Build XOR from the flock (any correct construction), verify all four input pairs in code, and present your reduction for one pair on the board.
4.  *Flock report.*  Watch or skim Lebec's "A Flock of Functions" (linked below) and write a half page: one construction he presents that we did not build today, reduced or verified yourself.
5.  *Church list.*  Build a Church-encoded linked list: `NIL`, `CONS(head)(tail)`, `HEAD`, `TAIL`, `ISNIL`.  Represent the list `[1, 2, 3]` as Church numerals in a Church list, and write a `to_python_list` function that decodes it.
6.  *Tie the knot.*  Write `sumlist-generator` so that $\textbf{Z}$ turns it into a function that sums a Scheme list.  Then write the same thing the ordinary way, with `define` and a self-reference, and say in two sentences what the name was doing that $\textbf{Z}$ now does instead.
7.  *Mechanical audit.*  Choose one Church-encoding reduction you performed by hand in this module (for example, $\textbf{ISZERO}\, \overline{1}$ or $\textbf{FST}\, (\textbf{PAIR}\, a\, b)$) and verify it mechanically using Lambda-Py / pycombinator (https://finsberg.github.io/pycombinator/docs/lambda-talk.html) or your own Python reducer.  Include the transcript, and reconcile in one sentence: did the machine agree with your hand derivation step for step, and if not, which artifact erred?

---

## Reflection Prompt

In your notebook: numbers, booleans, pairs, and conditionals all dissolved into functions this week.  Does anything in computing now seem *irreducibly* data to you, or is it functions all the way down?  Defend your answer with one example, knowing your December language will choose what to make primitive.

---

## 9.  Further Reading

- Gabriel Lebec.  "Lambda as JS, or A Flock of Functions": https://speakerdeck.com/glebec/lambda-as-js-or-a-flock-of-functions-combinators-lambda-calculus-and-church-encodings-in-javascript (talk recording also online).  This is the companion reading for today's module: every Python cell here mirrors a section of that talk.
- **Lambda-Py / pycombinator**: combinators and Church encodings in Python; run every Church encoding from today interactively in your browser: https://finsberg.github.io/pycombinator/docs/lambda-talk.html
- Raymond Smullyan.  *To Mock a Mockingbird* (1985): the combinator birds.
- Raul Rojas.  "A Tutorial Introduction to the Lambda Calculus" (online), sections on encodings.
- [Build a Lambda Calculus Reducer](https://www.billmongan.com/Ursinus-CS374-Fall2026/Tutorials/LambdaCalculusReducer): builds the derivation from Part V up one step at a time in Python, from a factorial that takes a copy of itself through to the machinery separated out, and then implements the reducer that checks your hand reductions mechanically.  Direction C of the [Functional assignment](https://www.billmongan.com/Ursinus-CS374-Fall2026/Assignments/Functional) builds on the Church encodings from this activity.
- `call/cc`: capturing the rest of the computation as a value, and deriving break, return, exceptions, cooperative schedulers, generators, and backtracking from it.  Direction B of the [Functional assignment](https://www.billmongan.com/Ursinus-CS374-Fall2026/Assignments/Functional) builds on this.
- The Curry-Howard correspondence: propositions as types, products and sums, the empty type and absurdity, and a glimpse of dependent types.  Philip Wadler, *Propositions as Types*.

---

Up next: the *Closures and First-Class Functions* activity shows what a capturing lambda costs at run time, and sets today's fixed-point combinator beside the other way of getting something the bare calculus lacks, a captured variable you are allowed to mutate.  The Church encodings you built here power the Functional assignment.
