# The Lambda Calculus, Part 2: Church Encodings and Combinators
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

1. Verify by reduction that $\textbf{C}\, \textbf{K}\, A\, B$ behaves exactly like $\textbf{KI}\, A\, B$. (The Cardinal of the Kestrel is the Kite: flipping "take the first" yields "take the second.")
2. Write each combinator as a Python lambda (`K = lambda x: lambda y: x`, and so on) and verify question 1 by execution with strings for $A$ and $B$.
3. Why must a combinator have no free variables to deserve a permanent name? Connect to purity from the functional module.

---

# Part II: Truth, Built from Selection

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

---

## Model 2: Prove the Logic

### Critical Thinking Questions

4. Reduce $\textbf{NOT}\, \textbf{TRUE}$ step by step to $\textbf{FALSE}$. (Substitute, then let TRUE select.)
5. Reduce $\textbf{AND}\, \textbf{TRUE}\, \textbf{FALSE}$ and $\textbf{AND}\, \textbf{FALSE}\, \textbf{TRUE}$. Explain *why* `p q p` works in one sentence: when is the answer just "whatever q is," and when is it "p itself"?
6. $\textbf{AND}$ never examines $q$ when $p$ is FALSE. Which semantics from the control-flow module did you just get *for free*, and why is it free here?
7. Notice $\textbf{NOT} = \textbf{C}$ applied cleverly... actually, verify: does $\textbf{C}\, b$ flip a Church boolean's selections? Reduce $\textbf{C}\, \textbf{TRUE}\, A\, B$ and compare with $\textbf{FALSE}\, A\, B$.

---

# Part III: Numbers as Repetition

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

---

## Church Encodings — Runnable

```python
# Church encodings, executable. Python lambdas ARE lambda calculus terms.

TRUE  = lambda x: lambda y: x          # K  (Kestrel)
FALSE = lambda x: lambda y: y          # KI (Kite)
NOT   = lambda b: b(FALSE)(TRUE)
AND   = lambda p: lambda q: p(q)(p)
OR    = lambda p: lambda q: p(p)(q)
XOR   = lambda p: lambda q: p(NOT(q))(q)

show_bool = lambda b: b("TRUE")("FALSE")    # a boolean selects its own name

print("=== Church Booleans ===")
print("NOT TRUE        =", show_bool(NOT(TRUE)))
print("NOT FALSE       =", show_bool(NOT(FALSE)))
print("AND TRUE FALSE  =", show_bool(AND(TRUE)(FALSE)))
print("OR  FALSE TRUE  =", show_bool(OR(FALSE)(TRUE)))
print("XOR TRUE  TRUE  =", show_bool(XOR(TRUE)(TRUE)))
print("XOR TRUE  FALSE =", show_bool(XOR(TRUE)(FALSE)))

print("\n=== Church Numerals ===")
ZERO  = lambda f: lambda x: x
SUCC  = lambda n: lambda f: lambda x: f(n(f)(x))
PLUS  = lambda m: lambda n: lambda f: lambda x: m(f)(n(f)(x))
MULT  = lambda m: lambda n: lambda f: m(n(f))
EXP   = lambda m: lambda n: n(m)    # m^n — shockingly simple

ONE, TWO = SUCC(ZERO), SUCC(SUCC(ZERO))
THREE    = PLUS(ONE)(TWO)
SIX      = MULT(TWO)(THREE)
EIGHT    = EXP(TWO)(THREE)   # 2^3

to_int = lambda n: n(lambda k: k + 1)(0)    # decode: count repetitions
print("ONE, TWO, 1+2, 2*3  =", to_int(ONE), to_int(TWO), to_int(THREE), to_int(SIX))
print("2^3 =", to_int(EIGHT))

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

8. `to_int` decodes a numeral by handing it the successor function on machine integers and the seed 0. Explain why this works in one sentence that begins "A Church numeral n is...".
9. Reduce $\textbf{SUCC}\; \textbf{1}$ by hand to confirm it is $\textbf{2}$ (expect two or three careful steps).
10. Verify in code that $\textbf{MULT}\, \textbf{2}\, \textbf{3}$ and $\textbf{PLUS}\, \textbf{3}\, \textbf{3}$ decode equally, then explain MULT's eerie brevity: what is `n(f)`, and what does `m` do *to that*?
11. Where is the data? A Church numeral stores no digits anywhere. Connect this to homoiconicity week's lesson, and to the claim "data is frozen behavior."

[[MC]]
Under Church encoding, the expression `b(t)(e)` where b is a Church boolean implements if-then-else because:
- ( ) Python evaluates booleans specially
- (x) TRUE and FALSE are themselves selector functions returning their first and second arguments respectively
- ( ) The lambda calculus has a built-in conditional form
- ( ) t and e must be numerals

---

## Model 4: Pairs and the Predecessor

**Church pairs — building linked data from functions:**
```python
# Church pairs: PAIR a b f = f a b
# FST p = p K  (select first)
# SND p = p KI (select second)

TRUE  = lambda x: lambda y: x   # K
FALSE = lambda x: lambda y: y   # KI
to_int = lambda n: n(lambda k: k+1)(0)
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
# Increment a pair: (n,m) → (SUCC n, n)  i.e., shift right
shift = lambda p: PAIR(SUCC(FST(p)))(FST(p))

# PRED n: start from (0,0), apply shift n times, take SND
ZERO_PAIR = PAIR(ZERO)(ZERO)
PRED = lambda n: SND(n(shift)(ZERO_PAIR))

# Build some numerals
ONE = SUCC(ZERO); TWO = SUCC(ONE); THREE = SUCC(TWO); FOUR = SUCC(THREE)

print("\n=== Predecessor ===")
print(f"PRED(0) = {to_int(PRED(ZERO))}")   # 0 (special case)
print(f"PRED(1) = {to_int(PRED(ONE))}")    # 0
print(f"PRED(2) = {to_int(PRED(TWO))}")    # 1
print(f"PRED(4) = {to_int(PRED(FOUR))}")   # 3

# Subtraction from predecessor:
MINUS = lambda m: lambda n: n(PRED)(m)
print(f"\n4 - 2 = {to_int(MINUS(FOUR)(TWO))}")   # 2
print(f"3 - 5 = {to_int(MINUS(THREE)(FOUR))}")   # 0 (floored)
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

### Critical Thinking Questions

12. The pair-based predecessor works by shifting: `(0,0) → (1,0) → (2,1) → (3,2)`. After applying shift $n$ times to $(0,0)$, what is the SND? Why does `PRED(ZERO)` return ZERO rather than negative one?
13. Subtraction `m - n` is defined as "apply PRED n times to m." What is `3 - 5` under this definition? This is called *monus* (truncated subtraction). Is this a bug or a deliberate design choice?
14. You now have: booleans, conditionals, numerals, arithmetic, pairs. What other data structures (lists, trees) could be built from Church pairs? Sketch the encoding for a two-element list [a, b].

---

## 4. Exercises

1. *Pairs.* Define $\textbf{PAIR} = \lambda a. \lambda b. \lambda f.\, f\, a\, b$, with $\textbf{FST} = \lambda p.\, p\, \textbf{K}$ and $\textbf{SND} = \lambda p.\, p\, \textbf{KI}$. Verify in Python, then say what data structure you just built from nothing, and what your AST could, in principle, be encoded as.
2. *IS-ZERO.* Define $\textbf{ISZERO} = \lambda n.\, n\, (\lambda x.\, \textbf{FALSE})\, \textbf{TRUE}$ and verify on 0, 1, 2. Explain the trick: what happens to TRUE if $f$ is applied even once?
3. *XOR.* Build XOR from the flock (any correct construction), verify all four input pairs in code, and present your reduction for one pair on the board.
4. *Flock report.* Watch or skim Lebec's "A Flock of Functions" (linked below) and write a half page: one construction he presents that we did not build today, reduced or verified yourself.
5. *Church list.* Build a Church-encoded linked list: `NIL`, `CONS(head)(tail)`, `HEAD`, `TAIL`, `ISNIL`. Represent the list `[1, 2, 3]` as Church numerals in a Church list, and write a `to_python_list` function that decodes it.

---

## Reflection Prompt

In your notebook: numbers, booleans, pairs, and conditionals all dissolved into functions this week. Does anything in computing now seem *irreducibly* data to you, or is it functions all the way down? Defend your answer with one example, knowing your December language will choose what to make primitive.

---

## 5. Further Reading

- Gabriel Lebec. "Lambda as JS, or A Flock of Functions": https://speakerdeck.com/glebec/lambda-as-js-or-a-flock-of-functions-combinators-lambda-calculus-and-church-encodings-in-javascript (talk recording also online). This is the companion reading for today's module — every Python cell here mirrors a section of that talk.
- **Lambda Py** — run every Church encoding from today interactively in your browser: https://finsberg.github.io/pycombinator/docs/lambda-talk.html
- Raymond Smullyan. *To Mock a Mockingbird* (1985): the combinator birds.
- Raul Rojas. "A Tutorial Introduction to the Lambda Calculus" (online), sections on encodings.
