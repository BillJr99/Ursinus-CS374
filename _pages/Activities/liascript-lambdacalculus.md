# The Lambda Calculus: From Church to Strudel

<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://github.com/BillJr99/Ursinus-CS374-Fall2026/blob/gh-pages/_pages/Activities/liascript-lambdacalculus.md or locally if deployed via https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374-Fall2026/gh-pages/_pages/Activities/liascript-lambdacalculus.md

import: https://raw.githubusercontent.com/liascript/CodeRunner/master/README.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

# The Lambda Calculus: From Church to Strudel

The lambda calculus is a minimal formal system invented by Alonzo Church in the 1930s — it has only functions, application, and variables, yet it can compute anything a Turing machine can. Understanding lambda calculus is like learning to count using just a single mark on a page: it strips away all complexity to reveal the pure essence of computation. Every feature of every programming language you have used — loops, booleans, numbers, recursion — can be built from this tiny foundation.

## Learning Goals

By the end of this activity, you will be able to:

- Parse and fully parenthesize lambda calculus expressions using the three syntactic forms (variable, abstraction, application), correctly applying left-associativity and maximal-body conventions
- Perform beta reduction step by step, applying capture-avoiding substitution and alpha-renaming when variable capture would otherwise occur
- Construct Church encodings for booleans and natural numbers from pure lambda terms, and verify them by hand reduction
- Derive the Y combinator from first principles and explain how it achieves recursion without named self-reference
- Identify where lambda calculus constructs appear in real languages (Python `lambda`, Haskell functions, TidalCycles/Strudel patterns)

> **Before You Begin — Prerequisites**
>
> This module assumes you are comfortable with the following ideas. If any feel shaky, spend ten minutes reviewing before proceeding.
>
> - **Functions as values**: In Python you can write `f = lambda x: x + 1` and pass `f` to another function. Lambda calculus is built entirely on this idea — every value is a function.
> - **Substitution**: When you call `f(3)` and `f = lambda x: x * x`, Python replaces every `x` in the body with `3`. Lambda calculus makes this substitution step the *only* rule of computation.
> - **Recursive reduction**: Evaluating a complex expression means applying substitution repeatedly until no more substitutions are possible. You will perform these steps by hand before relying on any code.

This module develops the **lambda calculus**, the three-rule language from 1936 that is simultaneously the smallest programming language ever designed and the theoretical core of every functional language you use. We move from **syntax $\rightarrow$ substitution and $\beta$-reduction $\rightarrow$ evaluation strategies $\rightarrow$ Church encodings $\rightarrow$ recursion via the Y combinator $\rightarrow$ the calculus alive in modern code**, and we keep one practical thread taut throughout: the live coding languages we have been studying, TidalCycles in Haskell and Strudel in JavaScript, are lambda calculus with costumes on, and by the end of this module you will be able to point to exactly where the costume ends.

---

## Notation at a Glance

If you have never seen lambda calculus notation before, this table maps every symbol you will encounter to a Python equivalent you already know. Return here whenever a symbol looks unfamiliar.

| Lambda Notation | Python Equivalent | Meaning |
|-----------------|-------------------|---------|
| `λx.e` | `lambda x: e` | A function taking x, returning e |
| `(f a)` | `f(a)` | Apply function f to argument a |
| `[x → a]e` | (substitution) | Replace x with a in e |
| `λx.λy.e` | `lambda x: lambda y: e` | Curried two-argument function |
| `f a b` (no parens) | `f(a)(b)` | Left-associative application: `(f a) b` |

---

## 0. Environment & Utilities

This module uses Python as a workbench for executing lambda terms, because Python's `lambda` is a direct (if syntactically heavier) transliteration of the calculus. No internet access is required; every cell is self-contained.

---

## Code Cell

```python
# The three syntactic forms of the lambda calculus, transliterated.
# Variable:     x
# Abstraction:  lambda x: body
# Application:  f(a)

identity = lambda x: x
self_apply_arg = lambda f: f(f)

print("identity(42) =", identity(42))
print("Environment ready.")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

---

# Part I: The Calculus Itself

## 1. Syntax: Three Forms and Nothing Else

> **Intuition**: Before reading the formal grammar, hold this picture: every lambda calculus expression is a tree with exactly three kinds of node — a leaf (variable), a box labeled with a parameter name (abstraction), or a connector joining two sub-expressions (application). There is nothing else. Every program ever written in a functional language is, at its core, just such a tree.

**The entire grammar of the lambda calculus fits on one line.** With $x$ ranging over an infinite supply of variable names, the set of terms $e$ is defined inductively by

$$
e \;::=\; x \;\mid\; \lambda x.\, e \;\mid\; e\ e
$$

read as: a term is a **variable**, an **abstraction** (a function of one parameter $x$ with body $e$), or an **application** of one term to another. There are no numbers, no booleans, no `if`, no recursion, and no assignment, and Part II of this module is the demonstration that none of them are missing, because all of them can be built. After our parsing module, you should also notice that this grammar is context-free, recursive through itself in exactly the way our mini-notation grammar was, and one of the exercises asks you to treat it accordingly.

**Two notational conventions keep terms readable.** Application associates to the **left**, so $f\ a\ b$ means $(f\ a)\ b$, and abstraction bodies extend as far **right** as possible, so $\lambda x.\, x\ y$ means $\lambda x.\,(x\ y)$, not $(\lambda x.\, x)\ y$. Misreading these two conventions causes more student errors than every other topic in this module combined, so we pause on them.

> **Watch out! — Lambda functions always take exactly one argument.** `λx.λy.e` is not a two-argument function — it is a one-argument function that *returns* another one-argument function. You must apply it twice to get a result: `(λx.λy.e) a b` first produces `(λy.e[x:=a])`, then produces `e[x:=a][y:=b]`. In Python: `(lambda x: lambda y: x + y)(3)` returns a function, not a number. Applying it again, `(lambda x: lambda y: x + y)(3)(4)`, returns `7`. This one-at-a-time pattern is called **currying** and it is the only way lambda calculus handles multiple arguments.

**Multi-argument functions are nested single-argument functions, and this is currying.** The two-argument function "apply $f$ to $a$" is written

$$
\lambda f.\, \lambda a.\, f\ a
$$

and supplying only $f$ yields a perfectly good value, namely the one-argument function $\lambda a.\, f\ a$ awaiting the rest. You have already used this in performance: Tidal's `fast 2`, a function given one of its two arguments and handed to `every` as a transformation, is currying deployed on stage. The calculus is where that move is defined.

---

### Try It: Individually

Fully parenthesize each term below according to the two conventions, then label every variable occurrence as bound or free. Work on paper before checking with a neighbor.

1. $\lambda x.\, \lambda y.\, x\ y\ x$
2. $(\lambda x.\, x)\ \lambda y.\, y\ z$
3. $\lambda f.\, f\ (\lambda x.\, f\ x)$

For term 2, state in one sentence why $z$'s status matters to anyone who wants to evaluate the term.

---

## 2. Substitution and Beta-Reduction

> **Intuition**: Think of beta-reduction as the act of calling a function. When you write `(lambda x: x * x)(5)` in Python, the interpreter replaces every `x` in the body with `5` and returns `5 * 5`. Lambda calculus formalizes exactly this: the entire model of computation is "find a function applied to an argument, substitute, repeat." The subtlety — and the main source of bugs — is that naive substitution can accidentally capture a variable that should have remained free, changing the meaning of the expression. The formal substitution rules exist solely to prevent that accident.

**Computation in the lambda calculus is one rule: $\beta$-reduction.** Applying an abstraction to an argument substitutes the argument for the parameter throughout the body:

$$
(\lambda x.\, e)\ a \;\longrightarrow_{\beta}\; e[x := a]
$$

A term of the shape $(\lambda x.\, e)\ a$ is called a **redex**, and a term containing no redex is in **normal form**. Everything your laptop does, within the scope of the computable, can be expressed as chains of this single rewriting step, which is the content of the Church-Turing thesis as it touches this course.

**Substitution must avoid variable capture, and this is the one subtle point.** Naively substituting $y$ into $\lambda y.\, x$ for $x$ would produce $\lambda y.\, y$, silently turning a free variable into a bound one and changing the term's meaning. The repair is **$\alpha$-conversion**: bound variable names are arbitrary, so we rename the binder first, $\lambda y.\, x \;=_{\alpha}\; \lambda w.\, x$, and only then substitute, obtaining $\lambda w.\, y$. The capture-avoiding substitution $e[x := a]$ is defined by structural recursion on $e$:

$$
x[x := a] = a \qquad
y[x := a] = y \ (y \neq x) \qquad
(e_1\ e_2)[x := a] = e_1[x := a]\ \ e_2[x := a]
$$

$$
(\lambda y.\, e)[x := a] =
\begin{cases}
\lambda y.\, e & \text{if } y = x \\
\lambda y.\, e[x := a] & \text{if } y \neq x \text{ and } y \notin \mathrm{FV}(a) \\
\lambda w.\, e[y := w][x := a] & \text{otherwise, with } w \text{ fresh}
\end{cases}
$$

When you implement substitution in this unit's written assignment, the third case is where every bug will live, and the test suite we provide targets it deliberately.

> **Watch out! — Alpha-renaming preserves meaning; capture destroys it.** `λy.x` and `λw.x` are the *same* function — the parameter name is just a placeholder. But `λy.y` and `λy.x` are *different* functions (identity vs. constant). When you substitute and risk capture, you must rename the binder to a *fresh* name before substituting. Skipping this step is the single most common source of incorrect reductions. A reliable check: after substitution, confirm that no variable that was free in the argument has become bound inside the result.

**A reduction, worked in full.** Consider $(\lambda f.\, \lambda x.\, f\ (f\ x))\ (\lambda y.\, y)$:

$$
\begin{aligned}
(\lambda f.\, \lambda x.\, f\ (f\ x))\ (\lambda y.\, y)
&\longrightarrow_{\beta} \lambda x.\, (\lambda y.\, y)\ ((\lambda y.\, y)\ x) \\
&\longrightarrow_{\beta} \lambda x.\, (\lambda y.\, y)\ x \\
&\longrightarrow_{\beta} \lambda x.\, x
\end{aligned}
$$

Applying "twice" to the identity yields the identity, which is reassuring, and the calculation previews Church numerals: the first term is the numeral $\overline{2}$.

[[MC]]
Reducing $(\lambda x.\, \lambda y.\, x)\ y$ requires care. Which result is correct?
- (x) $\lambda w.\, y$, because the bound $y$ must first be renamed to avoid capturing the free argument $y$.
- ( ) $\lambda y.\, y$, by substituting $y$ for $x$ directly in the body.
- ( ) $\lambda x.\, y$, because the outer parameter is the one renamed.
- ( ) The term is already in normal form, since abstractions are values.

---

## 3. Evaluation Strategies and Confluence

**When a term contains several redexes, a strategy chooses which to reduce first, and the choice has consequences.** **Normal-order** reduction always reduces the leftmost, outermost redex, deferring argument evaluation; **applicative-order** reduces arguments first, as C, Java, Python, and JavaScript do. The strategies can differ in termination. Let $\Omega = (\lambda x.\, x\ x)(\lambda x.\, x\ x)$, the canonical infinite loop, which reduces only to itself, and consider

$$
(\lambda x.\, \lambda y.\, y)\ \Omega
$$

Normal order discards $\Omega$ unevaluated and reaches $\lambda y.\, y$ in one step; applicative order attempts $\Omega$ first and loops forever. The **Church-Rosser theorem** guarantees that this divergence in termination is the worst that can happen: reduction is **confluent**, so if two strategies both reach a normal form, it is the same normal form, and no term has two distinct normal forms. Moreover, normal-order reduction is **normalizing**: if a normal form exists at all, normal order finds it. Haskell's lazy evaluation is an efficient implementation of the normal-order idea, and it is why Tidal can hand around infinite patterns, functions queriable at any future cycle, without computing any of them until queried; the pattern model from our first module is Church-Rosser's gift to musicians.

---

### Try It: With a Partner

One partner is the **normal-order machine** and the other the **applicative-order machine**. Each reduces the same term on paper, one numbered step per line, choosing redexes strictly according to their assigned strategy:

$$
(\lambda x.\, x\ x)\ ((\lambda y.\, y)\ (\lambda z.\, z))
$$

Compare transcripts: confirm that you reached the same normal form, and record which machine took fewer steps and why. Then swap strategies and repeat with $(\lambda x.\, \lambda y.\, x)\ (\lambda z.\, z)\ \Omega$, where the outcome is starker; the applicative-order machine should explain at what step, and why, it concedes.

---

# Part II: Building a Language from Nothing

## 4. Church Encodings: Booleans and Numerals

**Data can be encoded as the functions that consume it.** A boolean's only job is to choose between two alternatives, so let the boolean **be** the chooser:

$$
\mathbf{true} = \lambda t.\, \lambda f.\, t \qquad
\mathbf{false} = \lambda t.\, \lambda f.\, f \qquad
\mathbf{if} = \lambda b.\, \lambda t.\, \lambda f.\, b\ t\ f
$$

A natural number's essence is iteration, so let the numeral $\overline{n}$ **be** the function that applies its first argument $n$ times to its second:

$$
\overline{n} = \lambda f.\, \lambda x.\, f^{\,n}(x)
\qquad\quad
\mathbf{succ} = \lambda n.\, \lambda f.\, \lambda x.\, f\ (n\ f\ x)
$$

$$
\mathbf{add} = \lambda m.\, \lambda n.\, \lambda f.\, \lambda x.\, m\ f\ (n\ f\ x)
\qquad
\mathbf{mul} = \lambda m.\, \lambda n.\, \lambda f.\, m\ (n\ f)
$$

Read $\mathbf{add}$ aloud: apply $f$ a total of $n$ times, then $m$ more times. The encoding is not a trick; it is the observation that a datum and the fold over that datum carry the same information, an idea that returns when we study algebraic data types in the Haskell unit.

---

## Code Cell

```python
# Church encodings executed verbatim in Python. The only liberty taken
# is to_int, a measuring device that applies a numeral to (+1) and 0
# so we can see results. Compare each definition to the math above.

true  = lambda t: lambda f: t
false = lambda t: lambda f: f
iff   = lambda b: lambda t: lambda f: b(t)(f)

zero  = lambda f: lambda x: x
succ  = lambda n: lambda f: lambda x: f(n(f)(x))
add   = lambda m: lambda n: lambda f: lambda x: m(f)(n(f)(x))
mul   = lambda m: lambda n: lambda f: m(n(f))

to_int = lambda n: n(lambda k: k + 1)(0)

one   = succ(zero)
two   = succ(one)
three = add(one)(two)

print("three        ->", to_int(three))            # expect 3
print("mul 3 2      ->", to_int(mul(three)(two)))  # expect 6
print("if true a b  ->", iff(true)("a")("b"))      # expect a
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

---

## 5. Recursion Without Names: The Y Combinator

**The calculus has no recursion because definitions have no names to call.** A factorial cannot refer to "factorial." The escape is to write a function that receives **itself** as an argument, then to find a term that performs that self-feeding automatically. The **Y combinator**,

$$
Y = \lambda f.\, (\lambda x.\, f\ (x\ x))\ (\lambda x.\, f\ (x\ x))
$$

satisfies the fixed-point equation $Y\ g \;=\; g\ (Y\ g)$ for every $g$, which a two-line $\beta$-reduction confirms and which is precisely the unfolding a recursive call performs. In an applicative-order language the unfolding runs away, so strict languages use the eta-delayed variant $Z = \lambda f. (\lambda x. f (\lambda v. x\, x\, v))(\lambda x. f (\lambda v. x\, x\, v))$; the code cell below uses $Z$ so that Python can execute it.

---

## Code Cell

```python
# The Z combinator (applicative-order Y) computing factorial with no
# def, no name, and no recursion in the host language's sense.

Z = lambda f: (lambda x: f(lambda v: x(x)(v)))(lambda x: f(lambda v: x(x)(v)))

fact_step = lambda self: lambda n: 1 if n == 0 else n * self(n - 1)

factorial = Z(fact_step)
print("factorial(6) =", factorial(6))   # expect 720
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

---

[[MC]]
The term $\Omega = (\lambda x.\, x\ x)(\lambda x.\, x\ x)$ and the combinator $Y$ both contain self-application $x\ x$. What distinguishes their behavior?
- (x) $\Omega$ reduces only to itself forever, while $Y\ g$ unfolds to $g\ (Y\ g)$, so $g$ can stop the unfolding by not using its argument, which is what a base case does.
- ( ) $Y$ is typable in the simply typed lambda calculus while $\Omega$ is not, and typability is what permits termination.
- ( ) $\Omega$ uses applicative order while $Y$ uses normal order, and the strategy is part of each term.
- ( ) There is no difference; both diverge, and practical languages use neither.

---

# Part III: The Calculus in the Wild, Synthesis & Practice

## 6. Where You Have Been Using This All Along

**Haskell is the lambda calculus with types, names, and syntax sugar, and Tidal inherits all of it.** The performance expression `every 4 (fast 2) $ sound "bd sn"` desugars, name by name, into nested abstractions and applications; `fast 2` is a partial application, legal because `fast` denotes $\lambda n.\, \lambda p.\, \ldots$ and one argument peels one binder. **JavaScript's arrow functions are abstractions with different clothing**, so Strudel's `x => x.fast(2)` is $\lambda x.\, \texttt{fast}\ 2\ x$, and the equivalence between the Haskell idiom and the JavaScript idiom that we noted in the first module is, formally, an $\eta$-conversion away from being syntactic identity. Closures, callbacks, `map` and `filter`, Python decorators, and the event-span query functions we wrote for the pattern model are all terms of this calculus; within the scope of language features built on first-class functions, the lambda calculus is not an ancestor of your tools but their present-tense specification.

---

## 7. Exercises

Exercises 1 through 3 are individual; exercises 4 and 5 are partner exercises, and the pair work here directly rehearses the written assignment that follows this module.

1. *Reduction transcript.* Reduce $\mathbf{add}\ \overline{1}\ \overline{1}$ to normal form using normal order, one numbered step per line, marking the redex you contract at each step. Report the transcript and confirm the result is $\alpha$-equivalent to $\overline{2}$.
2. *Capture hunting.* Construct a term whose naive (capture-permitting) substitution and capture-avoiding substitution yield different normal forms, show both computations, and state in one sentence the meaning change that capture caused.
3. *Encodings extended.* Define Church pairs $\mathbf{pair}$, $\mathbf{fst}$, $\mathbf{snd}$ in the calculus, transliterate them into Python in the style of the Section 4 code cell, and demonstrate `fst(pair(a)(b)) == a` on two test values. Report definitions and output.
4. *Partner: grammar and parse.* The lambda calculus grammar in Section 1 is context-free. With a partner, write an unambiguous yacc-style grammar for it that enforces the two conventions of Section 1 (left-associative application, right-extending bodies); one partner drafts productions while the other attempts to break them with the terms from the first Try It, then swap. Report the final grammar and one term that forced a revision.
5. *Partner: strategy referee.* Each partner independently reduces $(\lambda x.\, \overline{2})\ \Omega\ $ under an assigned strategy as in the Section 3 activity, then jointly write a three-sentence explanation of how this example predicts the behavior difference between Haskell and Python when passing an infinite structure to a function that ignores its argument. Connect explicitly to Tidal's infinite patterns.

---

# Part IV: Runnable Models

## Model 6: Beta Reduction Stepper

Instead of reducing on paper, this model implements a step-by-step beta reducer that shows each intermediate term. Terms are represented as Python objects (a small data structure), and the stepper prints one reduction at a time until a normal form is reached or a step limit is hit.

```python
# Beta-reduction stepper using an explicit term representation.
# Terms: Var(name), Lam(param, body), App(func, arg)

from dataclasses import dataclass, field
from typing import Union
import itertools

_counter = itertools.count()

@dataclass
class Var:
    name: str
    def __repr__(self): return self.name

@dataclass
class Lam:
    param: str
    body: "Term"
    def __repr__(self): return f"(λ{self.param}.{self.body})"

@dataclass
class App:
    func: "Term"
    arg: "Term"
    def __repr__(self): return f"({self.func} {self.arg})"

Term = Union[Var, Lam, App]

def free_vars(t: Term) -> set:
    if isinstance(t, Var): return {t.name}
    if isinstance(t, Lam): return free_vars(t.body) - {t.param}
    return free_vars(t.func) | free_vars(t.arg)

def fresh(avoid: set) -> str:
    for letter in "abcdefghijklmnopqrstuvwxyz":
        if letter not in avoid: return letter
    # fallback: numbered variables
    n = next(_counter); return f"v{n}"

def subst(t: Term, var: str, val: Term) -> Term:
    """Capture-avoiding substitution: t[var := val]."""
    if isinstance(t, Var):
        return val if t.name == var else t
    if isinstance(t, Lam):
        if t.param == var:          # bound variable shadows; stop here
            return t
        fv = free_vars(val)
        if t.param in fv:           # would capture; rename first
            w = fresh(fv | free_vars(t.body) | {var})
            renamed_body = subst(t.body, t.param, Var(w))
            return Lam(w, subst(renamed_body, var, val))
        return Lam(t.param, subst(t.body, var, val))
    # App
    return App(subst(t.func, var, val), subst(t.arg, var, val))

def step(t: Term):
    """Return (reduced_term, True) if a beta step was taken, else (t, False)."""
    if isinstance(t, App):
        if isinstance(t.func, Lam):     # beta redex at top level
            return subst(t.func.body, t.func.param, t.arg), True
        # Try to reduce func first (normal order: leftmost-outermost)
        reduced, fired = step(t.func)
        if fired: return App(reduced, t.arg), True
        reduced, fired = step(t.arg)
        if fired: return App(t.func, reduced), True
    if isinstance(t, Lam):
        reduced, fired = step(t.body)
        if fired: return Lam(t.param, reduced), True
    return t, False

def reduce(t: Term, limit: int = 20):
    print(f"  start : {t}")
    for i in range(limit):
        t2, fired = step(t)
        if not fired:
            print(f"  → normal form reached after {i} step(s)")
            return t2
        print(f"  step {i+1}: {t2}")
        t = t2
    print(f"  (stopped after {limit} steps — may diverge)")
    return t

# ── Demo terms ────────────────────────────────────────────────────────────────

identity = Lam("x", Var("x"))
const    = Lam("x", Lam("y", Var("x")))

print("=== (λx.x) 42-analogue: identity applied to const ===")
reduce(App(identity, const))

print()
# (λf.λx. f (f x)) (λy. y)  — "twice" applied to identity
twice  = Lam("f", Lam("x", App(Var("f"), App(Var("f"), Var("x")))))
print("=== twice identity ===")
reduce(App(twice, identity))
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

### Critical Thinking Questions

21. The `step` function first tries to fire a redex at the **top level** of an `App`, then recurses left, then right. This implements leftmost-outermost (normal-order) reduction. Modify the call order to get **applicative-order**: reduce the argument *before* applying the function. What changes in the `step` code, and what would happen if you fed `Omega` under applicative order?
22. Trace `step` manually for `(λf.λx. f (f x)) (λy.y)`. After the first call to `step`, what is the returned term? After the second call? Confirm the final result matches the pen-and-paper reduction from Section 2.
23. The `fresh` helper searches lowercase letters to avoid capture. Why is generating a truly *fresh* name more than a naming preference — what semantic property of the term breaks if the same name is reused?

---

## Model 7: Church Numerals

Church numerals exist in the lambda calculus as pure functions, but Python's `lambda` executes them directly, letting us verify arithmetic identities like `add(two)(three) == five` by checking `church_to_int` on both sides.

```python
# Church numerals: zero, succ, add, mult — all as Python lambdas.
# church_to_int is only a display device; it is not part of the encoding.

zero  = lambda f: lambda x: x
succ  = lambda n: lambda f: lambda x: f(n(f)(x))
add   = lambda m: lambda n: lambda f: lambda x: m(f)(n(f)(x))
mult  = lambda m: lambda n: lambda f: m(n(f))
exp   = lambda m: lambda n: n(m)   # Church exponentiation: m^n

church_to_int = lambda n: n(lambda k: k + 1)(0)

# Build the first several numerals via succ
one   = succ(zero)
two   = succ(one)
three = succ(two)
four  = succ(three)
five  = succ(four)

print("=== Basic numerals ===")
for name, num in [("zero",zero),("one",one),("two",two),("three",three)]:
    print(f"  {name} -> {church_to_int(num)}")

print()
print("=== Arithmetic ===")
print(f"  add(two)(three)  = {church_to_int(add(two)(three))}")    # 5
print(f"  mult(two)(three) = {church_to_int(mult(two)(three))}")   # 6
print(f"  exp(two)(three)  = {church_to_int(exp(two)(three))}")    # 8  (2^3)

# Verify add(two)(three) == five
assert church_to_int(add(two)(three)) == 5, "arithmetic failed!"
assert church_to_int(mult(two)(three)) == 6, "multiplication failed!"
assert church_to_int(exp(two)(three)) == 8, "exponentiation failed!"
print()
print("All assertions passed.")

# ── Bonus: Church booleans and iszero ────────────────────────────────────────
iszero = lambda n: n(lambda _: False)(True)
print()
print("=== iszero ===")
for num, name in [(zero,"zero"),(one,"one"),(two,"two")]:
    print(f"  iszero({name}) = {iszero(num)}")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

### Critical Thinking Questions

24. `church_to_int` is defined as `lambda n: n(lambda k: k+1)(0)`. Unpack this: what does `n` receive as its first argument `f`, and what as its second argument `x`? Why does this produce the integer value of the Church numeral? Trace `church_to_int(two)` step by step.
25. `mult(two)(three)` is implemented as `lambda f: two(three(f))`. Explain this in English: `three(f)` is "apply `f` three times"; `two(three(f))` does what? How does this mirror the mathematical definition $m \times n$ as "apply $f$ a total of $m \times n$ times"?
26. The `exp` encoding `lambda m: lambda n: n(m)` looks surprisingly simple. Verify by hand that `exp(two)(three)` produces `eight`. (Hint: `three(two)` means "apply `two` three times, starting from `f`".)
27. Define `pred` (predecessor) in Python using the Church numeral representation. This is famously tricky — look up the "pair trick" (Kleene's predecessor). Implement it and verify `church_to_int(pred(three)) == 2`.

---

## Model 8: Alpha Equivalence

Two lambda terms are **alpha-equivalent** if they differ only in the names of their bound variables. `λx.x` and `λy.y` are the same function; only the label changed. This model implements a canonical renaming (de Bruijn–style index assignment) so that alpha-equivalent terms produce identical canonical forms, then uses that to check equivalence.

```python
# Alpha equivalence via canonical renaming.
# Strategy: replace each bound variable with a positional index
# (depth from binding lambda), eliminating names for bound vars entirely.
# Free variables keep their names.

from dataclasses import dataclass
from typing import Union

# Reuse the term dataclasses from Model 6
@dataclass
class Var:
    name: str
    def __repr__(self): return self.name

@dataclass
class Lam:
    param: str
    body: "Term"
    def __repr__(self): return f"(λ{self.param}.{self.body})"

@dataclass
class App:
    func: "Term"
    arg: "Term"
    def __repr__(self): return f"({self.func} {self.arg})"

Term = Union[Var, Lam, App]

def canonicalize(t: Term, env: dict = None) -> str:
    """Return a canonical string where bound variables are replaced by
    their de Bruijn depth index.  Free variables keep their original names."""
    if env is None:
        env = {}
    if isinstance(t, Var):
        if t.name in env:
            return f"#{env[t.name]}"     # bound: use depth index
        return t.name                    # free: keep name
    if isinstance(t, Lam):
        depth = len(env)
        new_env = {**env, t.param: depth}
        return f"(λ#{depth}.{canonicalize(t.body, new_env)})"
    # App
    return f"({canonicalize(t.func, env)} {canonicalize(t.arg, env)})"

def alpha_equiv(t1: Term, t2: Term) -> bool:
    return canonicalize(t1) == canonicalize(t2)

# ── Build terms ───────────────────────────────────────────────────────────────

lam_x_x = Lam("x", Var("x"))          # λx.x
lam_y_y = Lam("y", Var("y"))          # λy.y
lam_z_z = Lam("z", Var("z"))          # λz.z
lam_x_y = Lam("x", Var("y"))          # λx.y  (y is FREE here)
lam_y_x = Lam("y", Var("x"))          # λy.x  (x is FREE here)

# λx.λy.x  vs  λa.λb.a  (both are Church TRUE / K combinator)
true1 = Lam("x", Lam("y", Var("x")))
true2 = Lam("a", Lam("b", Var("a")))

# λx.λy.y  vs  λa.λb.b  (both are Church FALSE)
false1 = Lam("x", Lam("y", Var("y")))
false2 = Lam("a", Lam("b", Var("b")))

print("=== Canonical forms ===")
for name, t in [("λx.x", lam_x_x), ("λy.y", lam_y_y), ("λz.z", lam_z_z),
                ("λx.y", lam_x_y), ("λy.x", lam_y_x)]:
    print(f"  {name:8} -> {canonicalize(t)}")

print()
print("=== Alpha equivalence checks ===")
tests = [
    ("λx.x",    lam_x_x, "λy.y",    lam_y_y, True),
    ("λx.x",    lam_x_x, "λz.z",    lam_z_z, True),
    ("λx.y",    lam_x_y, "λz.y",    Lam("z", Var("y")), True),
    ("λx.y",    lam_x_y, "λy.x",    lam_y_x, False),  # different free vars
    ("true1",   true1,   "true2",   true2,   True),
    ("false1",  false1,  "false2",  false2,  True),
    ("true1",   true1,   "false1",  false1,  False),
]
for n1, t1, n2, t2, expected in tests:
    result = alpha_equiv(t1, t2)
    status = "PASS" if result == expected else "FAIL"
    print(f"  [{status}] alpha_equiv({n1}, {n2}) = {result}  (expected {expected})")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

### Critical Thinking Questions

28. `λx.y` and `λz.y` are alpha-equivalent because `y` is **free** in both and the bound variable name is irrelevant. But `λx.y` and `λy.x` are **not** alpha-equivalent. Explain why: what is `y`'s status in the first term and `x`'s status in the second?
29. The canonical form uses depth indices for bound variables. What is the canonical form of `λx.λy.x`? What about `λa.λb.b`? Verify your answers match the test cases above and explain why the depth index correctly distinguishes the two terms.
30. Alpha equivalence is the "cheapest" notion of equivalence for lambda terms. Two stronger notions are **beta equivalence** (reduce both to normal form and compare) and **eta equivalence** (`λx.f x` ≡ `f` when `x` not free in `f`). Give an example where two terms are beta-equivalent but the canonical form check would say they are different. Why is this not a bug in the alpha-checker?

---

## 8. Further Reading

- Pierce, Benjamin C. *Types and Programming Languages* (MIT Press, 2002). Chapter 5 is the standard modern treatment of the untyped calculus, including the substitution definition used here.
- **Lambda Py interactive notebook** — run the calculus directly in your browser: https://finsberg.github.io/pycombinator/docs/lambda-talk.html — an excellent companion to the code cells in this module.
- Church, Alonzo. "An Unsolvable Problem of Elementary Number Theory." *American Journal of Mathematics* 58 (1936). The original; read the first pages for the historical voice.
- Barendregt, Henk. *The Lambda Calculus: Its Syntax and Semantics* (North-Holland, 1984). The encyclopedic reference, for depth beyond this course.
- Hudak, Paul, John Hughes, Simon Peyton Jones, and Philip Wadler. "A History of Haskell: Being Lazy with Class." *HOPL III* (2007). How the calculus, lazy evaluation, and Church-Rosser shaped the language that hosts TidalCycles.
- McLean, Alex. "Making Programming Languages to Dance to: Live Coding with Tidal." *FARM Workshop, ICFP* (2014). Re-read Section 3 of this paper after today; the combinator design reads differently once you can see the abstractions underneath.

---
