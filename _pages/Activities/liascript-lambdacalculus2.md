<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://github.com/BillJr99/Ursinus-CS374-Fall2026/blob/gh-pages/_pages/Activities/liascript-lambdacalculus2.md or locally via https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374/gh-pages/_pages/Activities/liascript-lambdacalculus2.md

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

Everything you need to compute can be expressed with just functions. Lambda calculus has no numbers, no booleans, no if-statements; yet Church showed how to encode ALL of these as pure lambda terms. This activity builds that encoding from scratch in Python.

The calculus of *The Lambda Calculus, Part 1* had no numbers, no booleans, no data, and today we discover it needs none: **everything can be built from functions alone**. Following the same path as Gabriel Lebec's "A Flock of Functions" (our companion reading, in JavaScript), we build booleans, then numbers, then arithmetic, verifying each construction by hand and in Python. The arc: **named combinators $\rightarrow$ Church booleans $\rightarrow$ Church numerals $\rightarrow$ arithmetic as function surgery**.

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

You reduced **K** $A\, B \rightarrow A$ and **KI** $A\, B \rightarrow B$ in *The Lambda Calculus, Part 1* without their names. Hold that thought; it is about to become the whole theory of truth.

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

> **Watch out!** Church booleans are functions, not values. `TRUE(a)(b)` returns `a`: that is the entire definition. The if-then-else `IF b t f = b(t)(f)` works because TRUE selects its first argument and FALSE selects its second. There is no special conditional syntax; the boolean *is* the branch selector.

> **Watch out!** Python's `lambda` returns single expressions. For multi-argument Church terms, use curried lambdas: `lambda x: lambda y: x` not `lambda x,y: x`. The curried form is what makes `TRUE(a)(b)` work, the first call returns another function that accepts `b`.

**Step-by-step reduction: NOT TRUE**

```
NOT TRUE
= (λb. b FALSE TRUE) (λx.λy. x)
->β (λx.λy. x) FALSE TRUE
->β (λy. FALSE) TRUE
->β FALSE  ✓
```

**Step-by-step reduction: AND TRUE FALSE**

```
AND TRUE FALSE
= (λp.λq. p q p) TRUE FALSE
->β (λq. TRUE q TRUE) FALSE
->β TRUE FALSE TRUE
= (λx.λy. x) FALSE TRUE
->β (λy. FALSE) TRUE
->β FALSE  ✓
```

**Decode helper, "peek inside" a Church boolean:**

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

### Church Booleans; Runnable

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

> **Intuition before numerals:** Zero is "apply f zero times": `lambda f: lambda x: x`. One is "apply f once": `lambda f: lambda x: f(x)`. The number N is "apply f N times to x." Addition is "apply f m+n times." Multiplication is "apply (n copies of f) m times." The number *is* the iteration count, there are no digits stored anywhere.

## 3. Church Numerals

A number $n$ is encoded as *the act of doing something n times*:

$$
\textbf{0} = \lambda f. \lambda x.\, x \qquad
\textbf{1} = \lambda f. \lambda x.\, f\, x \qquad
\textbf{2} = \lambda f. \lambda x.\, f\, (f\, x) \qquad
\textbf{3} = \lambda f. \lambda x.\, f\, (f\, (f\, x))
$$

You met $\textbf{2}$ in *The Lambda Calculus, Part 1* as `twice`. Arithmetic becomes composition of repetitions:

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
->β λf.λx. f ((λf.λx. x) f x)
->β λf.λx. f ((λx. x) x)
->β λf.λx. f x
= ONE  ✓
```


**Step-by-step reduction: PLUS TWO THREE reduces to FIVE**

`SUCC` shows the shape; addition shows why the encoding is more than a trick. Recall `PLUS = λm.λn.λf.λx. m f (n f x)`: "apply `f` `m` times on top of applying it `n` times."

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
=   FIVE  ✓                                    five applications of f
```

Count the `f`s at each stage: `THREE f x` contributes three, and `TWO f` wraps two more around them. Addition of Church numerals is literally **function composition counted**, `m + n` applications of `f` because you applied `f` `n` times and then `m` more times to the result. Nothing was added; things were nested.

Try `MULT TWO THREE = λf.λx. m (n f) x` on your own with the same method and watch why it gives six: `n f` is "apply `f` three times" treated as a *single* function, and `m` applies **that** twice.

**Decode helper, "peek inside" a Church numeral:**

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

## Church Encodings - Runnable

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
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

---

## Model 3: Interrogate the Encodings

### Critical Thinking Questions

> **CTQ 3.1** `church_to_int` decodes a numeral by handing it the successor function on machine integers and the seed 0. Explain why this works in one sentence that begins "A Church numeral n is...".

> **CTQ 3.2** Reduce $\textbf{SUCC}\; \textbf{1}$ by hand to confirm it is $\textbf{2}$ (expect two or three careful steps). The trace for `SUCC ZERO` above is a model; repeat the pattern one numeral up.

> **CTQ 3.3** Verify in code that $\textbf{MULT}\, \textbf{2}\, \textbf{3}$ and $\textbf{PLUS}\, \textbf{3}\, \textbf{3}$ decode equally, then explain MULT's eerie brevity: what is `n(f)`, and what does `m` do *to that*?

> **CTQ 3.4** Where is the data? A Church numeral stores no digits anywhere. Connect this to homoiconicity week's lesson, and to the claim "data is frozen behavior."

Under Church encoding, the expression `b(t)(e)` where b is a Church boolean implements if-then-else because:

[( )] Python evaluates booleans specially
[(X)] TRUE and FALSE are themselves selector functions returning their first and second arguments respectively
[( )] The lambda calculus has a built-in conditional form
[( )] t and e must be numerals

---

# Part IV: Pairs and the Predecessor

> **Intuition before pairs:** A pair stores two values. The pair itself is a function that takes a "selector": `lambda sel: sel(a)(b)`. FST passes `lambda x: lambda y: x` (which is TRUE/K) to extract the first element; SND passes `lambda x: lambda y: y` (which is FALSE/KI) to extract the second. You already built the selectors when you built booleans, pairs come for free.

## Model 4: Pairs and the Predecessor

**Church pairs: building linked data from functions:**

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

> **CTQ 4.1** The pair-based predecessor works by shifting: `(0,0) -> (1,0) -> (2,1) -> (3,2)`. After applying shift $n$ times to $(0,0)$, what is the SND? Why does `PRED(ZERO)` return ZERO rather than negative one?

> **CTQ 4.2** Subtraction `m - n` is defined as "apply PRED n times to m." What is `3 - 5` under this definition? This is called *monus* (truncated subtraction). Is this a bug or a deliberate design choice?

> **CTQ 4.3** You now have: booleans, conditionals, numerals, arithmetic, pairs. What other data structures (lists, trees) could be built from Church pairs? Sketch the encoding for a two-element list [a, b].

---

---
**In-class work stops here.** Everything below is homework and going-deeper material; attempt the exercises before the related assignment.

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

- Gabriel Lebec. "Lambda as JS, or A Flock of Functions": https://speakerdeck.com/glebec/lambda-as-js-or-a-flock-of-functions-combinators-lambda-calculus-and-church-encodings-in-javascript (talk recording also online). This is the companion reading for today's module: every Python cell here mirrors a section of that talk.
- **Lambda-Py / pycombinator** (combinators and Church encodings in Python; run every Church encoding from today interactively in your browser: https://finsberg.github.io/pycombinator/docs/lambda-talk.html
- Raymond Smullyan. *To Mock a Mockingbird* (1985): the combinator birds.
- Raul Rojas. "A Tutorial Introduction to the Lambda Calculus" (online), sections on encodings.

---

## Going Deeper (Optional Pointers)

> **Going further:** the full Y-combinator derivation that used to live here) self-reference without names, the fixed-point equation $Y\ g = g\ (Y\ g)$, and the Z combinator for strict languages; now lives as the advanced section "Advanced: Deriving the Y Combinator" at the end of the dedicated tutorial: [Build a Lambda Calculus Reducer](https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374/gh-pages/_pages/Tutorials/tutorial-lambda-calculus-reducer.md). **Direction C of the [Functional assignment](https://www.billmongan.com/Ursinus-CS374-Fall2026/Assignments/Functional) builds on the Church encodings from this activity**: read that direction's section before choosing it.

> **Going further:** the call-with-current-continuation appendix that used to live here: capturing "the rest of the computation" as a value, deriving break, return, exceptions, cooperative schedulers, generators, and backtracking from `call/cc`, now lives where it is assessed: **Direction B of the [Functional assignment](https://www.billmongan.com/Ursinus-CS374-Fall2026/Assignments/Functional) builds on this material**; read that direction's section before choosing it.

> **Going further:** the Curry-Howard correspondence appendix (programs as proofs: propositions as types, products and sums, the empty type and absurdity, a glimpse of dependent types) is a self-study topic; search "Curry-Howard correspondence" and see *Propositions as Types* by Philip Wadler when curiosity calls for it.

---

Up next: the *Language Design Workshop* kickoff (your team's language begins) while the Church encodings you built here power the Functional assignment.
