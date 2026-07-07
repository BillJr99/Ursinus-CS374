<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://github.com/BillJr99/Ursinus-CS374-Fall2026/blob/gh-pages/_pages/Activities/liascript-lambdacalculus1.md or locally via https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374-Fall2026/gh-pages/_pages/Activities/liascript-lambdacalculus1.md

import: https://raw.githubusercontent.com/liascript/CodeRunner/master/README.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

# The Lambda Calculus, Part 1: Syntax and Reduction

The lambda calculus is a minimal formal system invented by Alonzo Church in the 1930s — it has only functions, application, and variables, yet it can compute anything a Turing machine can. Understanding lambda calculus is like learning to count using just a single mark on a page: it strips away all complexity to reveal the pure essence of computation. In this first part, you will learn to read, write, and reduce lambda expressions by hand — the foundational skill for everything that follows.

## Learning Goals

By the end of this activity, you will be able to:

- Write and read lambda calculus expressions in formal notation, applying left-associative application and maximal-body abstraction conventions
- Classify every variable occurrence in a lambda expression as either bound (and identify its binding λ) or free
- Perform beta reduction step by step on paper, substituting arguments into function bodies following the one reduction rule
- Recognize when variable capture would occur during substitution and apply alpha-renaming to avoid it
- Translate between lambda calculus notation and equivalent Python `lambda` expressions

> **Before You Begin — Prerequisites**
>
> This activity works best if you are comfortable with the following. If any feel shaky, review them before the session.
>
> - **Functions as values**: In Python you can write `f = lambda x: x + 1` and pass `f` to another function as an argument. Lambda calculus is built entirely on this idea.
> - **Substitution**: Evaluating `(lambda x: x * x)(5)` means replacing every `x` in the body with `5`. Lambda calculus makes this the *only* rule of computation — you will apply it by hand today.
> - **Recursive reduction**: Complex expressions simplify by applying the substitution rule repeatedly. Each application is one step; you will write out every step on the whiteboard.

Lambda calculus was invented by Alonzo Church in the 1930s to answer a fundamental question: what does it mean to *compute*? Church showed that two symbols — λ (for "function") and · (for "apply") — are sufficient to compute anything that is computable. Every programming language you have ever used, including Python, is secretly a lambda calculus with extra syntax. By the end of this activity, you will have seen Python's entire evaluation model in eight lines of math.

Beneath Scheme, beneath Python's `lambda`, beneath every functional language, sits a formal system from 1936 with **three forms of expression and one rule of computation**: Alonzo Church's **lambda calculus**, in which functions are the only thing that exists, and computing means substituting arguments into bodies. Today we learn to read it and to reduce expressions **by hand**, the way Church did, because by-hand reduction is the only way the system becomes real. The arc: **the three forms $\rightarrow$ free and bound variables $\rightarrow$ beta reduction by hand $\rightarrow$ alpha renaming when names collide**.

---

## Directions and Group Roles

Work in your POGIL team with rotated roles (**Manager**, **Recorder**, **Presenter**, **Reflector**). Today is a whiteboard day: every reduction is written out stepwise, and teammates check each other's substitutions character by character. The Recorder photographs the board for the discussion post. After class, respond to the reflective prompt individually in your notebook.

---

# Part I: The Whole Language

## Notation Bridge: Lambda Calculus vs. Python

Before we dive into the formal rules, here is a translation table. Every lambda calculus expression you will encounter today has a direct Python equivalent. Keep this table handy — whenever a lambda expression looks unfamiliar, find its Python mirror here.

| Lambda Calculus | Python | Meaning |
|---|---|---|
| `λx.x` | `lambda x: x` | identity function |
| `λx.λy.x` | `lambda x: lambda y: x` | constant function (returns first arg) |
| `(λx.x+1) 5` | `(lambda x: x+1)(5)` | function application |
| `λf.λx.f (f x)` | `lambda f: lambda x: f(f(x))` | apply-twice |

> **Note for beginners**: In Python, `lambda x: x` is a function with no name that takes one argument `x` and returns `x`. Lambda calculus is the same idea, just written with a λ symbol and a dot instead of a colon. The table above maps every symbol one-to-one.

**Core notation reference** — the three fundamental constructs of lambda calculus:

| Lambda Notation | Python Equivalent | Meaning |
|-----------------|-------------------|---------|
| `λx.e` | `lambda x: e` | A function taking x, returning e |
| `(f a)` | `f(a)` | Apply function f to argument a |
| `[x → a]e` | (substitution) | Replace x with a in e |

---

## 1. Three Forms

> **Intuition**: Every lambda calculus expression is built from exactly three kinds of thing: a name (`x`), a function definition (`λx.body`), or a function call (`f arg`). That is the whole language. Before reading further, convince yourself that Python's `lambda x: f(f(x))` uses all three: `x` and `f` are variables, `lambda x: ...` is an abstraction, and `f(f(x))` is two nested applications.

A lambda expression is exactly one of:

$$
e ::= x \;\mid\; (\lambda x.\, e) \;\mid\; (e_1\; e_2)
$$

a **variable**; an **abstraction** (a function of one parameter $x$ with body $e$, written `λx.e`); or an **application** ($e_1$ applied to $e_2$). That is the entire grammar; there are no numbers, no booleans, no operators (Part 2 builds them all *from functions*). Conventions: application associates left ($f\,a\,b$ means $((f\,a)\,b)$), the body of a λ extends as far right as possible, and multi-parameter functions are nested single-parameter ones: $\lambda x y. e$ abbreviates $\lambda x. (\lambda y. e)$, the trick called **currying**, after Haskell Curry.

> **Watch out**: `λx.λy.x` is a function that takes `x`, then returns *a function* that takes `y`, then returns `x`. You have to apply it TWICE to get a value out. This is called "currying" — named after Haskell Curry. In Python: `(lambda x: lambda y: x)(3)(99)` returns `3`. Calling `(lambda x: lambda y: x)(3)` alone gives you back a function, not a value.

**Bound and free.** In $\lambda x.\, x\, y$: the $x$ in the body is **bound** by the λ; $y$ is **free** (it refers to something outside). Binding here is your scope module's lexical scoping, in its original mathematical form: a λ is a binder, its body is the scope.

> **Watch out! — Application is left-associative.** `f a b` means `(f a) b`, NOT `f (a b)`. Concretely: `f` is applied to `a` first, producing a new function, and *that* function is applied to `b`. This matters most for curried functions: `(λx.λy.x) A B` is `((λx.λy.x) A) B`, and the first application peels off one λ, giving `(λy.A) B`, which then reduces to `A`. If you mistakenly group it as `(λx.λy.x) (A B)`, you get a completely different computation.

---

## Model 1: Parse by Eye

> **Intuition**: Parsing lambda expressions is a mechanical skill: apply the two conventions (left-associative application, body extends right) until every sub-expression is explicitly parenthesized. A reliable strategy is to work outside-in — find the outermost application first, then recurse into each sub-expression. When you encounter a `λ`, its body runs all the way to the right end of the current parenthesization level.

### Critical Thinking Questions

1. Fully parenthesize each, then circle binders and underline free variables: (a) $\lambda x. x$; (b) $\lambda x. \lambda y. x$; (c) $(\lambda x. x\, x)(\lambda x. x\, x)$; (d) $\lambda x. x\, (\lambda y. y\, x)$.
2. Expression (b) takes two arguments (curried) and returns the first. What familiar Python one-liner is it? Write the Python.
3. In (d), the inner $x$ at the far right: bound by which λ? Apply the innermost-enclosing-binder rule and connect it, by name, to the environment chain's lookup walk.
4. Why does the grammar need no precedence ladder? (You answered this once for Scheme; the lambda calculus is where Scheme got it.)

---

# Part II: Computation Is Substitution

## 2. Beta Reduction

> **Intuition**: Beta reduction is function application: find a function `(λx.body)` applied to an argument `a`, and replace every free occurrence of `x` in `body` with `a`. That is literally it. The word "beta" just names this one rule so we can refer to it precisely. Each step erases one `λ` from the expression and performs one substitution. When no more lambdas are applied to arguments, you have reached normal form — the answer.

**The one rule.** An application of an abstraction to an argument reduces by substituting:

$$
(\lambda x.\, e)\; a \;\;\rightarrow_\beta\;\; e[x := a]
$$

read "$e$ with every *free* occurrence of $x$ replaced by $a$." A **redex** is any subexpression of that shape; an expression with no redexes is in **normal form**: the answer. Reduce stepwise, one redex at a time, drawing an arrow per step.

> **Watch out**: β-reduction is purely syntactic substitution. `(λx.x*x) (2+3)` does NOT compute `2+3` first — it substitutes the unevaluated expression `(2+3)` for `x`, giving `(2+3)*(2+3)`. Whether arguments are evaluated before substitution (eager) or after (lazy) is the call-by-value vs call-by-name distinction. Python uses call-by-value (eager), so Python would compute `5` first and then substitute. Pure lambda calculus by default uses call-by-name (lazy).

### Worked Example 1: Identity Function

$$
(\lambda x.\, x)\; z
$$

Step by step:

```
(λx.x) z
→β  [x := z] x      # substitute z for every free x in the body
→β  z               # the body was just x, now replaced by z
```

Result: `z`. The identity function returns its argument unchanged.

### Worked Example 2: Constant Function (K Combinator)

$$
(\lambda x. \lambda y.\, x)\; A\; B
$$

Step by step (remember: application is left-associative, so this is $(((\lambda x. \lambda y. x)\; A)\; B)$):

```
(λx.λy.x) A B
→β  [x := A] (λy.x)   B    # substitute A for x in body (λy.x)
→β  (λy.A) B               # after substitution, body is (λy.A)
→β  [y := B] A             # substitute B for y in body A
→β  A                      # y never appeared in body, so B is discarded
```

Result: `A`. This function selects its first argument and ignores its second.

Fully spelled out in math notation:

$$
(\lambda x. \lambda y.\, x)\; A\; B
\;\rightarrow_\beta\; (\lambda y.\, A)\; B
\;\rightarrow_\beta\; A
$$

Step 1 substituted $A$ for $x$ in $\lambda y. x$; the $y$-abstraction remained, now constant; step 2 applied it to $B$, which was discarded because $y$ never occurs in the body. The function selected its first argument: behavior, from substitution alone.

### Worked Example 3: Apply-Twice

$$
(\lambda f. \lambda x.\, f\,(f\, x))\; g\; a
$$

Step by step:

```
(λf.λx. f(f x)) g a
→β  [f := g] (λx. f(f x))   a   # substitute g for f in body
→β  (λx. g(g x)) a              # body now has g in place of f
→β  [x := a] g(g x)             # substitute a for x in body
→β  g(g a)                      # x replaced by a in both places
```

Result: `g(g a)`. This applies `g` twice to `a` — exactly what `twice(g)(a)` does in Python.

> **Watch out! — The order of reduction matters for termination, but not for the final result.** If you reduce the same expression two different ways (choosing different redexes at each step), you may take a different number of steps, or one path may loop while the other terminates. However, the Church-Rosser theorem guarantees that if both paths reach a normal form, the normal forms are identical. A key corollary: always prefer normal-order (outermost-first) reduction when working by hand, because it is the strategy most likely to find a normal form if one exists.

---

## Model 2: Reduce by Hand

> **Intuition**: Work through each reduction at the pace of one substitution per arrow. Before you write an arrow, identify: (1) which subexpression is the redex — a `(λx.body) arg` shape — and (2) what substitution you will perform. Write the result of the substitution, draw the arrow, and look for the next redex. The Omega term in Question 7 is the key insight: some expressions have no normal form, which means not every computation terminates.

### Critical Thinking Questions

5. Reduce, one arrow per step, all the way to normal form: (a) $(\lambda x.\, x)\, z$; (b) $(\lambda x.\, x\, x)(\lambda y.\, y)$; (c) $(\lambda x. \lambda y.\, y)\; A\; B$ (compare with the worked example: what does *this* function select?); (d) $(\lambda f. \lambda x.\, f\, (f\, x))\; g\; a$.
6. Expression (d)'s result applies $g$ twice. You wrote `twice(f)` in Python last week; write the lambda calculus term and the Python side by side. Which is which?
7. Now reduce $(\lambda x.\, x\, x)(\lambda x.\, x\, x)$, the famous **Omega**. Perform two steps. What do you notice, and what does Omega prove about whether every expression has a normal form?
8. In (d) you had a choice of which redex to reduce first at one point. Try the other order; does the normal form change? (The Church-Rosser theorem says it cannot; you have just collected one data point.)

---

## 3. Alpha Renaming: When Names Collide

> **Intuition**: The variable capture problem is subtle but important. Imagine you are substituting a free variable `y` into an expression that happens to bind `y` internally. The substituted `y` would fall under the inner binder and suddenly mean something different. The fix is simple: rename the inner binder to a fresh name before substituting. Think of it as "pick a local variable name that does not clash with anything in scope" — exactly what good programmers do to avoid shadowing bugs.

Substitution has one trap: **capture**. Reduce $(\lambda x. \lambda y.\, x)\; y$ naively and the free $y$ we substitute lands inside $\lambda y$, where it is suddenly, wrongly, bound: the meaning changed. The repair is **alpha renaming**: bound names are arbitrary ($\lambda y. e$ and $\lambda z. e[y := z]$ are the same function), so rename the binder first:

$$
(\lambda x. \lambda y.\, x)\; y \;=_\alpha\; (\lambda x. \lambda z.\, x)\; y \;\rightarrow_\beta\; \lambda z.\, y
$$

The result correctly returns the *free* $y$, whatever it refers to outside. Capture is the shadowing bug from your scope module, in formal dress, and alpha renaming is the formal version of "pick a fresh local name."

> **Watch out**: Variable capture is a subtle bug. When you substitute a value that contains a free variable `y` into a body that binds `y`, the `y` in your value would accidentally become bound by the inner lambda. The fix — alpha renaming — is just like how Python avoids variable shadowing bugs: pick a fresh name for the inner binder that does not collide with anything free in the argument.

### Step-by-step capture example (WRONG, then RIGHT):

**Wrong (capture):**
```
(λx.λy.x) y
→β  [x := y] (λy.x)    # naively substitute y for x
→β  λy.y               # WRONG: the free y is now captured by λy!
```
This says "a function that ignores its argument and returns ... its argument." That is the identity function, not the constant function. We changed the meaning!

**Right (alpha-rename first):**
```
(λx.λy.x) y
=α  (λx.λz.x) y        # rename bound y to fresh z (safe because z is not free in argument)
→β  [x := y] (λz.x)    # now substitute y for x
→β  λz.y               # correct: a function that ignores z and returns the free y
```

[[MC]]
The reduction $(\lambda x. \lambda y.\, x\, y)\; y \rightarrow \lambda y.\, y\, y$ is wrong because:
- ( ) Application associates left
- ( ) The expression was already in normal form
- (x) The substituted free y was captured by the inner binder; alpha-renaming the inner λy is required first
- ( ) Beta reduction may only be applied once per expression

---

# Part III: Runnable Models

## Model 3: Beta Reduction Step Tracer

> **Intuition**: This tracer represents lambda expressions as nested Python tuples and implements the substitution rule explicitly. Before running it, predict what the output will be for the first two examples by applying the substitution rule by hand. Then run the code and compare. Pay special attention to the alpha-rename message in the capture example — this is the mechanism you applied manually in Section 3, now automated.

The tracer below parses a simple subset of the lambda calculus (no real substitution engine is needed for small examples) and prints each beta-reduction step. Study the output to see exactly what the substitution rule does.

```python
# A Python-based beta-reduction step tracer for the lambda calculus.
# Expressions are represented as Python tuples:
#   ('var', name)
#   ('lam', param, body)
#   ('app', func, arg)

def var(name):      return ('var', name)
def lam(p, body):   return ('lam', p, body)
def app(f, a):      return ('app', f, a)

def pretty(expr, parens=False):
    """Pretty-print a lambda expression."""
    tag = expr[0]
    if tag == 'var':
        return expr[1]
    elif tag == 'lam':
        s = f"λ{expr[1]}.{pretty(expr[2])}"
        return f"({s})" if parens else s
    elif tag == 'app':
        f_str = pretty(expr[1], parens=True)
        a_str = pretty(expr[2], parens=True)
        return f"{f_str} {a_str}"

def free_vars(expr):
    """Return the set of free variable names in expr."""
    tag = expr[0]
    if tag == 'var':
        return {expr[1]}
    elif tag == 'lam':
        return free_vars(expr[2]) - {expr[1]}
    elif tag == 'app':
        return free_vars(expr[1]) | free_vars(expr[2])

_fresh_counter = [0]
def fresh(hint='z'):
    _fresh_counter[0] += 1
    return f"{hint}{_fresh_counter[0]}"

def subst(expr, var_name, replacement):
    """Substitute replacement for free occurrences of var_name in expr."""
    tag = expr[0]
    if tag == 'var':
        return replacement if expr[1] == var_name else expr
    elif tag == 'lam':
        if expr[1] == var_name:
            # Bound by this lambda — no substitution inside
            return expr
        elif expr[1] in free_vars(replacement):
            # Capture risk! Alpha-rename the bound variable first
            new_param = fresh(expr[1])
            renamed_body = subst(expr[2], expr[1], var(new_param))
            print(f"  [α-rename] {expr[1]} → {new_param} to avoid capture")
            return lam(new_param, subst(renamed_body, var_name, replacement))
        else:
            return lam(expr[1], subst(expr[2], var_name, replacement))
    elif tag == 'app':
        return app(subst(expr[1], var_name, replacement),
                   subst(expr[2], var_name, replacement))

def step(expr):
    """Perform one outermost beta-reduction step. Returns (new_expr, did_reduce)."""
    tag = expr[0]
    if tag == 'app':
        f, a = expr[1], expr[2]
        if f[0] == 'lam':
            # This is a redex: (λx.body) arg → body[x := arg]
            result = subst(f[2], f[1], a)
            return result, True
        # Try to reduce the function part, then the argument
        f2, reduced = step(f)
        if reduced:
            return app(f2, a), True
        a2, reduced = step(a)
        if reduced:
            return app(f, a2), True
    elif tag == 'lam':
        body2, reduced = step(expr[2])
        if reduced:
            return lam(expr[1], body2), True
    return expr, False

def normalize(expr, max_steps=20):
    """Reduce expr to normal form, printing each step."""
    print(f"  Start: {pretty(expr)}")
    for i in range(max_steps):
        new_expr, reduced = step(expr)
        if not reduced:
            print(f"  Normal form reached in {i} step(s).")
            return expr
        print(f"  Step {i+1}: {pretty(new_expr)}")
        expr = new_expr
    print("  (max steps reached)")
    return expr

# --- Demo reductions ---

print("=== (λx.x) z  [identity applied to z] ===")
e1 = app(lam('x', var('x')), var('z'))
normalize(e1)
print()

print("=== (λx.λy.x) A B  [K combinator: select first] ===")
e2 = app(app(lam('x', lam('y', var('x'))), var('A')), var('B'))
normalize(e2)
print()

print("=== (λf.λx. f(f x)) g a  [apply g twice] ===")
e3 = app(
    app(lam('f', lam('x', app(var('f'), app(var('f'), var('x'))))),
        var('g')),
    var('a'))
normalize(e3)
print()

print("=== Capture example: (λx.λy.x) y  [needs alpha-rename] ===")
e4 = app(lam('x', lam('y', var('x'))), var('y'))
normalize(e4)
print()

print("Free vars in (λx. x y):", free_vars(lam('x', app(var('x'), var('y')))))
print("Free vars in (λx.λy. x):", free_vars(lam('x', lam('y', var('x')))))
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

### Critical Thinking Questions

9. The tracer prints each beta-reduction step. For the K-combinator example `(λx.λy.x) A B`, write out both steps in the mathematical notation $\rightarrow_\beta$ and match each printed line to one step.
10. When does the tracer print an alpha-rename message? Trace the capture example by hand first, then run to verify. Identify the exact variable that was at risk of capture and explain why the renamed variable avoids it.
11. The `free_vars` function returns a set. Why is it a *set* rather than a list, and how does `free_vars` influence the substitution decision inside `subst`?
12. The `step` function applies the **outermost** redex first (normal order). How would the output change for the "apply g twice" example if you instead always reduced the **innermost** redex (applicative order)? Which order does Python use when evaluating function calls?

---

## Model 3b: Interactive Reduction Simulator

> **Intuition**: This simulator uses Python dataclasses (`Var`, `Lam`, `App`) to represent the three syntactic forms as Python objects, making the structure of each expression explicit and inspectable. Use it to check your hand reductions from Model 2 — build the same expression you reduced on the whiteboard, run `normalize`, and verify the steps match. Notice that the `subst` function here does not implement full capture-avoiding renaming; compare this to Model 3 to see what is missing.

The simulator below lets you construct any lambda expression using the `Var`, `Lam`, and `App` building blocks, then watch each substitution step. Use it to check your hand reductions from Model 2. Build the expression you want, call `normalize(...)`, and compare to your whiteboard work.

```python
# A simple substitution-based reducer for lambda calculus
# Represents: Var(name), Lam(param, body), App(fun, arg)

from dataclasses import dataclass
from typing import Any

@dataclass
class Var:
    name: str
    def __str__(self): return self.name

@dataclass
class Lam:
    param: str
    body: Any
    def __str__(self): return f"(λ{self.param}.{self.body})"

@dataclass
class App:
    fun: Any
    arg: Any
    def __str__(self): return f"({self.fun} {self.arg})"

def subst(expr, var, value):
    """Substitute value for var in expr (capture-avoiding for Var only)."""
    if isinstance(expr, Var):
        return value if expr.name == var else expr
    if isinstance(expr, Lam):
        if expr.param == var:  # bound variable shadows
            return expr
        return Lam(expr.param, subst(expr.body, var, value))
    if isinstance(expr, App):
        return App(subst(expr.fun, var, value), subst(expr.arg, var, value))

def reduce_one(expr, depth=0):
    """Try one beta-reduction step. Return (new_expr, True) if reduced."""
    if isinstance(expr, App):
        if isinstance(expr.fun, Lam):
            # Beta reduction: (λx.body) arg → [x:=arg] body
            result = subst(expr.fun.body, expr.fun.param, expr.arg)
            print(f"  →β {result}")
            return result, True
        # Try reducing inside
        new_fun, r1 = reduce_one(expr.fun)
        if r1: return App(new_fun, expr.arg), True
        new_arg, r2 = reduce_one(expr.arg)
        if r2: return App(expr.fun, new_arg), True
    return expr, False

def normalize(expr, limit=20):
    """Reduce to normal form, printing each step."""
    print(f"  {expr}")
    for _ in range(limit):
        expr, reduced = reduce_one(expr)
        if not reduced:
            print(f"  = {expr} (normal form)")
            return expr
    print("  ... (did not terminate)")
    return expr

# Identity: (λx.x) 5
print("Identity: (λx.x) 5")
normalize(App(Lam("x", Var("x")), Var("5")))

# Constant: (λx.λy.x) a b
print("\nConstant: ((λx.λy.x) a) b")
normalize(App(App(Lam("x", Lam("y", Var("x"))), Var("a")), Var("b")))

# Self-application: (λx.x x) (λx.x)
print("\nSelf-apply identity to identity: (λx.x x)(λy.y)")
normalize(App(Lam("x", App(Var("x"), Var("x"))), Lam("y", Var("y"))))

# Apply-twice: (λf.λx.f(f x)) g a
print("\nApply-twice: (λf.λx.f(f x)) g a")
normalize(App(App(Lam("f", Lam("x", App(Var("f"), App(Var("f"), Var("x"))))), Var("g")), Var("a")))
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

---

## Model 4: Alpha Equivalence Checker

> **Intuition**: De Bruijn indices solve the alpha-equivalence problem elegantly: instead of naming bound variables, replace each one with a number saying "I am bound by the lambda that is this many steps outward." Under this scheme, `λx.x` and `λy.y` both become `λ_.#0` (the bound variable is index 0 — the immediately enclosing lambda). Two expressions are alpha-equivalent if and only if their de Bruijn representations are identical. Free variables keep their names because they refer to the *same* external binding regardless of renaming.

Two lambda expressions are **alpha-equivalent** ($=_\alpha$) if one can be obtained from the other by consistently renaming bound variables. They are *semantically identical* — only the choice of parameter names differs.

```python
# Alpha-equivalence checker using de Bruijn indices.
# Replace each bound variable with the numeric "distance" to its binder.
# Free variables keep their names.  Then structural equality = alpha-equiv.

def to_debruijn(expr, env=None):
    """
    Convert to de Bruijn index representation.
    env: list of bound variable names, innermost first.
    Returns a new structure using integers for bound vars, strings for free vars.
    """
    if env is None:
        env = []
    tag = expr[0]
    if tag == 'var':
        name = expr[1]
        if name in env:
            return ('idx', env.index(name))   # bound: replace with depth
        else:
            return ('free', name)              # free: keep name
    elif tag == 'lam':
        param = expr[1]
        new_env = [param] + env
        return ('lam_db', to_debruijn(expr[2], new_env))
    elif tag == 'app':
        return ('app', to_debruijn(expr[1], env), to_debruijn(expr[2], env))

def alpha_equiv(e1, e2):
    """Return True iff e1 and e2 are alpha-equivalent."""
    return to_debruijn(e1) == to_debruijn(e2)

def pretty(expr, parens=False):
    tag = expr[0]
    if tag == 'var':   return expr[1]
    if tag == 'lam':   
        s = f"λ{expr[1]}.{pretty(expr[2])}"
        return f"({s})" if parens else s
    if tag == 'app':   
        return f"{pretty(expr[1], True)} {pretty(expr[2], True)}"

var  = lambda n:    ('var', n)
lam  = lambda p, b: ('lam', p, b)
app  = lambda f, a: ('app', f, a)

# --- Test pairs ---
pairs = [
    # (description, expr1, expr2, expected)
    ("λx.x  vs  λy.y  (identity, different names)",
     lam('x', var('x')),
     lam('y', var('y')),
     True),

    ("λx.λy.x  vs  λa.λb.a  (K combinator, renamed)",
     lam('x', lam('y', var('x'))),
     lam('a', lam('b', var('a'))),
     True),

    ("λx.λy.x  vs  λx.λy.y  (K vs K' — pick first vs second)",
     lam('x', lam('y', var('x'))),
     lam('x', lam('y', var('y'))),
     False),

    ("λx.x y  vs  λz.z y  (free y preserved)",
     lam('x', app(var('x'), var('y'))),
     lam('z', app(var('z'), var('y'))),
     True),

    ("λx.x y  vs  λx.x w  (different free variables)",
     lam('x', app(var('x'), var('y'))),
     lam('x', app(var('x'), var('w'))),
     False),
]

print(f"{'Expression 1':<30} {'Expression 2':<30} {'α-equiv?':<10} {'Correct?'}")
print("-" * 85)
for desc, e1, e2, expected in pairs:
    result = alpha_equiv(e1, e2)
    correct = "YES" if result == expected else "NO (BUG)"
    print(f"{pretty(e1):<30} {pretty(e2):<30} {str(result):<10} {correct}")
    print(f"  ({desc})")

print()
print("De Bruijn indices for λx.λy.x:")
print(" ", to_debruijn(lam('x', lam('y', var('x')))))
print("De Bruijn indices for λa.λb.a:")
print(" ", to_debruijn(lam('a', lam('b', var('a')))))
print("They match → alpha-equivalent.")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

### Critical Thinking Questions

13. De Bruijn indices replace variable names with *distances to the binder*. For `λx.λy.x`, the `x` in the body has index 1 (one lambda up). Confirm this by reading the printed de Bruijn structure and explain why index 0 would mean "bound by the innermost lambda."
14. The checker says `λx.x y` is alpha-equivalent to `λz.z y`. Why must the free variable `y` remain as a name (not an index) for the comparison to be correct? What would go wrong if free variables were also replaced by indices?
15. Two expressions with different de Bruijn representations are *never* alpha-equivalent. Prove this claim in two sentences by referring to what de Bruijn indices encode.
16. In your CS374 interpreter, when do two AST nodes represent "the same" computation? Is that relation alpha-equivalence, beta-normal-form equality, or something else? Give a concrete example where the distinction matters.

---

## Model 5: Free vs Bound Variables and WHNF

> **Intuition**: WHNF is the "good enough" answer for lazy evaluation. An expression is in WHNF when the outermost position is not a redex — it is either a variable, a lambda, or an application whose function is not a lambda. Haskell stops here rather than reducing everything inside, which is why it can represent infinite lists: the spine of the list is in WHNF (a cons cell whose tail is an unevaluated thunk), and you only reduce the tail when you actually ask for the next element.

**Weak Head Normal Form (WHNF)** is a partial-normal form used by lazy languages (Haskell): an expression is in WHNF when its *outermost* constructor is not a redex, even if subexpressions remain unreduced. This is in contrast to full normal form where *no* redexes remain anywhere.

```python
# Demonstrate free/bound variable analysis and WHNF detection.

var  = lambda n:    ('var', n)
lam  = lambda p, b: ('lam', p, b)
app  = lambda f, a: ('app', f, a)

def free_vars(expr):
    tag = expr[0]
    if tag == 'var':  return {expr[1]}
    if tag == 'lam':  return free_vars(expr[2]) - {expr[1]}
    if tag == 'app':  return free_vars(expr[1]) | free_vars(expr[2])

def bound_vars(expr):
    """Return the set of all bound variable names in expr."""
    tag = expr[0]
    if tag == 'var':  return set()
    if tag == 'lam':  return {expr[1]} | bound_vars(expr[2])
    if tag == 'app':  return bound_vars(expr[1]) | bound_vars(expr[2])

def is_whnf(expr):
    """
    An expression is in Weak Head Normal Form if:
    - It is a variable, OR
    - It is a lambda abstraction (regardless of body), OR
    - It is an application whose head (leftmost function position) is NOT a lambda
      (i.e., the outermost application is not a redex).
    """
    tag = expr[0]
    if tag == 'var':  return True   # variable: trivially WHNF
    if tag == 'lam':  return True   # abstraction: WHNF (body may have redexes)
    if tag == 'app':
        # A redex (λx.body) arg is NOT in WHNF
        if expr[1][0] == 'lam':
            return False
        # Otherwise, the head is not a lambda — WHNF (even if args have redexes)
        return True

def has_redex(expr):
    """True if expr contains any beta redex anywhere."""
    tag = expr[0]
    if tag == 'var':  return False
    if tag == 'lam':  return has_redex(expr[2])
    if tag == 'app':
        if expr[1][0] == 'lam':  return True   # outermost is a redex
        return has_redex(expr[1]) or has_redex(expr[2])

def classify(expr, name):
    fv = free_vars(expr)
    bv = bound_vars(expr)
    whnf = is_whnf(expr)
    nf   = not has_redex(expr)
    print(f"{name}:")
    print(f"  Free vars : {fv if fv else '∅'}")
    print(f"  Bound vars: {bv if bv else '∅'}")
    print(f"  WHNF?     : {whnf}")
    print(f"  Normal form? : {nf}")
    print()

# λx.x  — identity: no free vars, x is bound; is a lambda so WHNF
classify(lam('x', var('x')), "λx.x")

# λx. x y  — y is free
classify(lam('x', app(var('x'), var('y'))), "λx.(x y)")

# (λx.x) z  — outermost is a redex: NOT WHNF, NOT normal form
classify(app(lam('x', var('x')), var('z')), "(λx.x) z")

# f ((λx.x) z)  — outermost head is free var f: IS WHNF, but NOT normal form
classify(app(var('f'), app(lam('x', var('x')), var('z'))), "f ((λx.x) z)")

# λy. (λx.x) z  — lambda at top: IS WHNF; body has redex, so NOT full NF
classify(lam('y', app(lam('x', var('x')), var('z'))), "λy.((λx.x) z)")

print("Key distinction:")
print("  Normal Form  — no redexes ANYWHERE in the expression.")
print("  WHNF         — outermost position is not a redex (body may still have them).")
print("  Lazy evaluation (Haskell) only reduces to WHNF — avoids evaluating")
print("  unreachable subexpressions, enabling infinite data structures.")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

### Critical Thinking Questions

17. The expression `f ((λx.x) z)` is in WHNF but *not* in normal form. Explain precisely why: what makes it WHNF, and where is the remaining redex?
18. Haskell evaluates to WHNF rather than full normal form. Write a Python example where evaluating an argument before it is needed causes an error or infinite loop that lazy (WHNF) evaluation would avoid.
19. The `bound_vars` function returns *all* bound variable names, not just the one bound at the outermost lambda. In the expression `λx. λy. x`, both `x` and `y` are bound. Explain why knowing the full set of bound variable names matters when performing a substitution.
20. Connect WHNF to your CS374 interpreter: when your `evaluate` function encounters `("call", func, arg)`, does it evaluate `arg` before or after looking up `func`? What evaluation strategy does that correspond to, and what is its name?

---

# Part IV: Synthesis and Practice

## 4. Exercises

1. *Reduction portfolio.* Reduce to normal form, showing every step: $(\lambda x.\, x)(\lambda y.\, y)(z)$; $(\lambda f.\, f\, a)(\lambda x.\, x)$; $(\lambda x. \lambda y.\, y\, x)\; p\; (\lambda q.\, q)$; and one capture trap of your own design, solved with explicit alpha renaming.
2. *Python mirror.* Express exercises 1's first three in Python lambdas and verify by execution that each normal form matches Python's answer (use strings or small functions as the free-variable stand-ins).
3. *Currying made real.* Write Python's `add = lambda x: lambda y: x + y` and call `add(3)(4)`. Then write the lambda calculus term it transliterates. One sentence: what does partial application (`add(3)` alone) *mean*, in both notations?
4. *The scope bridge.* Write a paragraph mapping vocabulary across your three systems: λ-binder, `let`-declaration, and environment `define`; free variable and name resolved in an outer scope; alpha renaming and shadow-avoidance. This paragraph is your study sheet for the closures module.

---

## Reflection Prompt

In your notebook: Church built this system in 1936 to study what "computable" means, with no machine in mind, and it turned out equivalent to Turing's machines. Does it change your view of programming to learn that its functional core predates computers? What, then, is a programming language *about*?

---

## 5. Further Reading

- Raul Rojas. "A Tutorial Introduction to the Lambda Calculus" (online): short and gentle.
- Henk Barendregt and Erik Barendsen. "Introduction to Lambda Calculus" (online notes), for the formal substitution definition.
- Gabriel Lebec. "Lambda as JS, or A Flock of Functions" (talk and slides), which Part 2 follows: https://speakerdeck.com/glebec/lambda-as-js-or-a-flock-of-functions-combinators-lambda-calculus-and-church-encodings-in-javascript
- **Lambda-Py / pycombinator** — combinators and Church encodings in Python; run the calculus interactively in your browser: https://finsberg.github.io/pycombinator/docs/lambda-talk.html — experiment with the reductions from today's module without installing anything.

## Going Deeper: Flock of Birds: Combinatory Logic and the SKI Calculus

Think of combinators as **LEGO bricks for computation**. Each brick does exactly one simple, self-contained thing — snap the identity brick onto the constant brick, snap that onto the compose brick — and from a handful of primitive pieces you can build any computation that any computer can perform. No names, no variables, no environment. Just bricks clicking together.

#### Learning Goals

By the end of this activity, you will be able to:

- Reduce combinatory logic expressions (I, K, S, B, C, W, M) to normal form using the combinator reduction rules, circling the active redex at each step
- Translate lambda expressions into combinator form using bracket abstraction, eliminating all variable bindings
- Implement the standard combinator birds in Python and verify their reduction behavior by execution
- Explain why S and K together are computationally complete (Schönfinkel's theorem) and connect this to the Church-Turing thesis
- Derive familiar higher-order functions (function composition, `flip`, `const`, identity) directly from combinator definitions

> **Before You Begin — Prerequisites**
>
> This activity assumes you are comfortable with:
>
> - **Lambda calculus syntax** — you can read $\lambda x.\ e$ and know that it means "a function that takes $x$ and returns $e$"
> - **Beta-reduction** — you can apply a lambda term to an argument by substituting the argument for the bound variable
> - **Currying** — you understand that `lambda a: lambda b: a` is a two-argument function written as two nested one-argument functions
> - **Python lambdas** — `lambda x: x + 1` is valid Python and returns a callable
>
> If any of these feel shaky, review the Lambda Calculus module before continuing. Combinators are built directly on top of that material; every reduction rule here is just beta-reduction with no bound variables.

*"To every combination there corresponds a unique bird."* — Raymond Smullyan, *To Mock a Mockingbird* (1985)

In the lambda calculus module we built computation from three syntactic forms: variables, abstraction, and application. Today we take the abstraction away. **Combinatory logic** is the lambda calculus with no bound variables — no $\lambda x$, no substitution, no alpha-conversion, no capture to fear. Only application and a small fixed collection of **combinators**: functions with no free variables whose behavior is defined entirely by how they transform their arguments. In 1924, Moses Schönfinkel proved that just two combinators, **S** and **K**, suffice to express any computable function. The birds are named in Raymond Smullyan's puzzle book, and Gabriel Lebec's 2016 London talk "*A Flock of Functions*" demonstrates the entire menagerie live in JavaScript. By the end of this module you will reduce terms in the combinator calculus by hand, implement all the birds in Python, derive familiar operations (function composition, `flip`, `const`, `id`) directly from the birds, and understand why SKI completeness is the combinatory-logic version of the Church-Turing thesis.

---

#### 0. Environment

```python
# Every bird is a Python callable. We verify by running the cells below.
# No libraries required.
print("Ready to meet the flock.")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

---

### Part I: The Birds Themselves

#### 1. Notation and Reduction Rules

Before diving into the rules, orient yourself: in the lambda calculus you had *variables*, *abstractions* ($\lambda x.\ e$), and *application*. Combinatory logic throws out variables and abstractions entirely. What remains? Application only — and a small fixed menu of named functions (the "birds") whose behavior is completely captured by simple rewrite rules. Each rule says: "when this bird receives enough arguments, rewrite the whole expression." There is no substitution, no renaming, no environment to thread around. Reduction is pure term rewriting, like rearranging LEGO bricks according to a picture.

**Combinatory terms** are built from:

- **Constants**: the combinators themselves (I, K, S, B, C, W, M, …)
- **Application**: writing two terms next to each other, left-associative

That is the entire syntax. There are no variables and no abstractions. A **reduction rule** for each combinator states how it consumes arguments from the right:

$$
\mathbf{I}\ a \;\Rightarrow\; a
$$
$$
\mathbf{K}\ a\ b \;\Rightarrow\; a
$$
$$
\mathbf{S}\ a\ b\ c \;\Rightarrow\; a\ c\ (b\ c)
$$

Application associates left, so $\mathbf{S}\ a\ b\ c$ means $(((\mathbf{S}\ a)\ b)\ c)$. A **redex** in combinatory logic is any subterm of the form $\mathbf{I}\ a$, $\mathbf{K}\ a\ b$, or $\mathbf{S}\ a\ b\ c$ (and analogously for other combinators). Reduction is confluent, exactly as in the lambda calculus, because the combinators are derived from it.

> **Watch out! — Argument counting**
>
> A combinator only fires when it has received *all* of its required arguments. $\mathbf{K}\ a$ is a partially applied function — it is waiting for its second argument and does *not* yet reduce. $\mathbf{S}\ a\ b$ is similarly stuck. Writing $\mathbf{S}\ a\ b\ c$ is what triggers the rule. If you try to reduce a term and nothing fires, check whether every combinator in the term is fully saturated.

**The translation from lambda calculus to combinators** (bracket abstraction) works by structural recursion:

$$
[x]\ x = \mathbf{I}
$$
$$
[x]\ e = \mathbf{K}\ e \quad (x \notin \mathrm{FV}(e))
$$
$$
[x]\ (e_1\ e_2) = \mathbf{S}\ ([x]\ e_1)\ ([x]\ e_2) \quad (x \in \mathrm{FV}(e_1 e_2))
$$

Every lambda term becomes a combinator expression — free of variables, yet computationally identical. The gain is conceptual: reduction is pure term rewriting, no environment, no substitution machinery.

---

##### Try It: Individually — Reduce by Hand

Reduce each expression to normal form, one rule application per line, circling the redex at each step.

1. $\mathbf{I}\ (\mathbf{K}\ a\ b)$
2. $\mathbf{K}\ (\mathbf{I}\ a)\ b$
3. $\mathbf{S}\ \mathbf{K}\ \mathbf{K}\ a$ — what well-known combinator does this behave like?

Hint for (3): what does $\mathbf{K}\ a\ (\_)$ do to any second argument?

---

#### 2. The Identity Bird — **I** (Idiot)

This is the simplest possible LEGO brick: snap it onto anything and that thing comes straight out the other side unchanged. It seems useless in isolation, but it becomes essential as a "do nothing" placeholder when you need a function in a slot that does not actually transform its argument. It also shows up in the derivation of every other combinator from S and K.

$$
\mathbf{I}\ a = a
$$

The Idiot bird passes its argument through unchanged. In lambda calculus it is $\lambda a.\ a$. In Haskell it is `id`. In mathematics it is the identity function on every set. Note that $\mathbf{I}$ is not primitive given S and K: $\mathbf{S}\ \mathbf{K}\ \mathbf{K}\ a \Rightarrow \mathbf{K}\ a\ (\mathbf{K}\ a) \Rightarrow a$, so $\mathbf{I} = \mathbf{S}\ \mathbf{K}\ \mathbf{K}$.

```python
I = lambda a: a

print(I(42))          # 42
print(I("hello"))     # hello
print(I(I)(42))       # 42  -- identity of identity is still identity
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

---

#### 3. The Kestrel — **K** (Constant)

The Kestrel is the "ignore and keep" brick. You hand it a value, and no matter what else you stack on top, it will always return that original value. This turns out to encode the Boolean *true* in Church encodings — because `if true then x else y` means "take two branches, return the first." Connect to the LEGO analogy: K is a brick with a trap door; everything that enters the second slot falls straight through and disappears.

$$
\mathbf{K}\ a\ b = a
$$

The Kestrel takes two arguments and returns the first, discarding the second. In lambda calculus it is $\lambda a.\ \lambda b.\ a$ — the encoding of **true** in Church booleans! In Haskell it is `const`. In Python:

```python
I = lambda a: a
K = lambda a: lambda b: a

print(K("first")("second"))   # first
print(K(42)("anything"))      # 42

# K is Church true
true  = K
false = lambda a: lambda b: b   # we'll derive this from KI below
KI    = K(I)                    # KI a b = K I a b = I b = b -- this IS Church false!
print(KI("ignored")("returned"))  # returned -- K(I) behaves as false / second-selector
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

---

#### 4. The Bluebird — **B** (Compose)

The Bluebird is the pipeline brick. Snap two bricks together end-to-end: the output of the second feeds into the input of the first. This is Haskell's `.` operator, and it is how real functional programs are built — not by writing big monolithic functions, but by composing small single-purpose ones. Notice that the argument order matters: $\mathbf{B}\ f\ g$ means "do $g$ first, then $f$," which is the standard mathematical right-to-left composition.

$$
\mathbf{B}\ f\ g\ x = f\ (g\ x)
$$

The Bluebird composes two functions: apply $g$ first, then $f$. In lambda calculus it is $\lambda f.\ \lambda g.\ \lambda x.\ f\ (g\ x)$. In Haskell it is `(.)`. It is one of the most-used birds in practice because function composition is the primary method of building programs in functional style.

```python
K = lambda a: lambda b: a
B = lambda f: lambda g: lambda x: f(g(x))

double  = lambda x: x * 2
add_one = lambda x: x + 1

double_then_add = B(add_one)(double)   # add 1 after doubling
add_then_double = B(double)(add_one)   # double after adding 1

print(double_then_add(5))  # (5*2)+1 = 11
print(add_then_double(5))  # (5+1)*2 = 12

# B is derivable: B = S (K S) K
S = lambda a: lambda b: lambda c: a(c)(b(c))
B_from_SK = S(K(S))(K)
print(B_from_SK(add_one)(double)(5))  # 11 -- same as B(add_one)(double)(5)
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

---

#### 5. The Cardinal — **C** (Flip)

The Cardinal is the "swap the inputs" brick. When you have a two-argument function and the arguments are arriving in the wrong order — perhaps you want to partially apply the *second* argument first — the Cardinal flips them for you. Haskell calls this `flip`, and it appears constantly when adapting library functions for use in pipelines and point-free style.

$$
\mathbf{C}\ f\ a\ b = f\ b\ a
$$

The Cardinal flips the argument order of a two-argument function. In lambda calculus it is $\lambda f.\ \lambda a.\ \lambda b.\ f\ b\ a$. In Haskell it is `flip`.

```python
K = lambda a: lambda b: a
S = lambda f: lambda g: lambda x: f(x)(g(x))
B = lambda f: lambda g: lambda x: f(g(x))
C = lambda f: lambda a: lambda b: f(b)(a)

subtract = lambda x: lambda y: x - y   # curried subtraction
subtract_from_10 = C(subtract)(10)      # flip: now b goes first
print(subtract_from_10(3))              # 10 - 3 = 7 (without flip: 3 - 10 = -7)

# C is derivable: C = S (B B S) (K K)
C_from_SK = S(B(B)(S))(K(K))
print(C_from_SK(subtract)(10)(3))   # 7
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

---

#### 6. The Starling — **S** (the Power Bird)

The Starling is the "fork and merge" brick — the one that makes the calculus powerful enough to compute anything. Given $x$, it routes $x$ down two separate paths simultaneously: one path feeds $x$ into $f$, producing a function; the other path feeds $x$ into $g$, producing an argument; then the results are merged by application. This is the combinator encoding of *sharing*: the same input reaches two different parts of a computation. Without this sharing capability, the calculus could only compute linear functions.

$$
\mathbf{S}\ f\ g\ x = f\ x\ (g\ x)
$$

The Starling is the heart of the calculus. It passes $x$ to both $f$ and $g$, then applies the result of $f(x)$ to the result of $g(x)$. This is the combinator version of *sharing an argument*: both branches see $x$, so duplication is built in. **S and K together are Turing complete**: any computable function can be expressed using only these two birds.

```python
K = lambda a: lambda b: a
S = lambda f: lambda g: lambda x: f(x)(g(x))

# S K K = I
SKK = S(K)(K)
print(SKK(42))   # 42

# The power of S: apply a function to a value AND its "environment"
# This is what makes S the basis for closures and environments
add  = lambda x: lambda y: x + y
succ = S(add)(K(1))   # succ x = add x (K 1 x) = add x 1 = x + 1
print(succ(5))   # 6
print(succ(10))  # 11
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

---

#### 7. The Mockingbird — **M** (Self-Application)

The Mockingbird is the "danger" brick — handle with care. It takes whatever you hand it and makes it eat itself. Applied to a safe function, this produces interesting behavior (self-duplication, mirroring). Applied to itself, it produces $\Omega$: the combinator equivalent of an infinite loop. The Mockingbird is the combinatory seed from which fixed-point combinators and recursion grow; it demonstrates that non-termination is an intrinsic feature of any sufficiently expressive system.

$$
\mathbf{M}\ a = a\ a
$$

The Mockingbird applies its argument to itself. In lambda calculus it is $\lambda a.\ a\ a$. It is the self-application operator, and $\mathbf{M}\ \mathbf{M}$ is the combinatory equivalent of $\Omega$ — it reduces forever. But applied carefully, the Mockingbird is the basis for fixed-point combinators and recursion in the combinator calculus.

```python
# We can't actually call M(M) -- infinite loop! 
# But M applied to other combinators is safe:
I = lambda a: a
K = lambda a: lambda b: a
M = lambda a: a(a)

print(M(I)(42))      # I(I)(42) = I(42) = 42
print(M(K)("a"))     # K(K)("a") = K  -- a function, not a value we can print easily

# M applied to a saturated-enough combinator:
double = lambda x: x * 2
# M doesn't make sense on double alone since double takes one arg; 
# but M(double) = double(double) and double is not a valid argument to double
# This shows M is "dangerous" -- it only makes sense with combinators that expect functions
print("M is the self-application bird")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

> **Watch out! — Do not evaluate M(M)**
>
> `M(M)` in Python will immediately raise a `RecursionError` (or spin forever). The Mockingbird is safe only when its argument is a function that can meaningfully accept a function as input. Before running any expression involving M, ask: "does this argument expect a callable?" If not, do not apply M.

---

#### 8. The Warbler — **W** (Duplicate)

The Warbler is the "copy and double-feed" brick. It takes a two-argument function and collapses its two inputs into one: whatever you hand it, it hands to $f$ twice. This is subtly different from the Mockingbird: M makes $x$ eat *itself*, while W feeds $x$ to an *external* two-argument function $f$. The Warbler is how you derive "diagonal" operations — squaring, equality-with-self, duplication — without ever naming the argument twice.

$$
\mathbf{W}\ f\ x = f\ x\ x
$$

The Warbler duplicates its second argument, passing it twice to $f$. This is different from $\mathbf{M}$: $\mathbf{W}$ feeds $x$ to a two-argument function $f$, not to $x$ itself.

```python
W = lambda f: lambda x: f(x)(x)

# W with add: add x x = 2x (doubling!)
add = lambda x: lambda y: x + y
double_via_W = W(add)
print(double_via_W(5))   # add 5 5 = 10
print(double_via_W(7))   # add 7 7 = 14

# W as a way to express "apply diagonal"
eq = lambda x: lambda y: x == y
is_zero = W(lambda x: lambda y: x == 0 and y == 0)
print(W(eq)(5))    # eq 5 5 = True
print(W(eq)(5))    # True -- a number always equals itself
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

---

### Part II: Derivation and the Completeness of SKI

#### 9. Everything from S, K, I

You have now met seven birds. Here is the remarkable fact: you do not need seven. You need *two*. S and K alone — two LEGO bricks — can simulate every other bird, every lambda term, every computable function. This is Schönfinkel's 1924 theorem, the combinatory-logic counterpart of the Church-Turing thesis. The bracket abstraction algorithm in Section 1 is the constructive proof: it tells you mechanically how to turn any lambda term into an SKI expression. The derivations below make this concrete.

The true power of combinatory logic is that S and K suffice for *any* lambda term. The bracket abstraction algorithm (Section 1) converts any lambda term to an equivalent SKI expression. Let us derive B, C, and W from SKI to see this concretely.

**Deriving B (Compose) from SKI:**

We want $\mathbf{B}\ f\ g\ x = f\ (g\ x)$. Use $[x]\ (f\ (g\ x))$:

$$
[x]\ (f\ (g\ x)) = \mathbf{S}\ ([x]\ f)\ ([x]\ (g\ x)) = \mathbf{S}\ (\mathbf{K}\ f)\ (\mathbf{S}\ (\mathbf{K}\ g)\ \mathbf{I})
$$

So $\mathbf{B} = \mathbf{S}\ (\mathbf{K}\ \mathbf{S})\ \mathbf{K}$ (with one more step of abstraction). Verify:

$$
\mathbf{S}\ (\mathbf{K}\ \mathbf{S})\ \mathbf{K}\ f\ g\ x \Rightarrow \mathbf{K}\ \mathbf{S}\ f\ (\mathbf{K}\ f)\ g\ x \Rightarrow \mathbf{S}\ (\mathbf{K}\ f)\ g\ x \Rightarrow \mathbf{K}\ f\ x\ (g\ x) \Rightarrow f\ (g\ x)
$$

```python
# Verify B = S(KS)K
S = lambda f: lambda g: lambda x: f(x)(g(x))
K = lambda a: lambda b: a
I_bird = S(K)(K)

B_from_SK = S(K(S))(K)

add_one = lambda x: x + 1
double  = lambda x: x * 2

print(B_from_SK(add_one)(double)(5))   # 11: same as add_one(double(5))
print(B_from_SK(str)(double)(5))       # "10": str(double(5))
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

> **Watch out! — SKI expressions grow quickly**
>
> The naive bracket abstraction algorithm can produce expressions that are exponentially larger than the original lambda term — a two-variable lambda can become dozens of S, K, and I tokens. This is why real compilers (e.g., Turner 1979) use optimized combinators like B and C to keep the output manageable. When you do bracket abstraction by hand in the exercises, count your tokens; if the result seems enormous, double-check your steps.

---

[[MC]]
Which reduction sequence correctly shows that $\mathbf{K}\ \mathbf{I}\ a\ b \Rightarrow b$ (i.e., that $\mathbf{K}\ \mathbf{I}$ is **false** / the second-argument selector)?
- (x) $\mathbf{K}\ \mathbf{I}\ a \Rightarrow \mathbf{I}$, then $\mathbf{I}\ b \Rightarrow b$. Each step fires one combinator rule.
- ( ) $\mathbf{K}\ \mathbf{I}\ a\ b \Rightarrow \mathbf{K}\ b$, then $\mathbf{K}\ b \Rightarrow b$.
- ( ) $\mathbf{K}\ \mathbf{I}\ a\ b \Rightarrow \mathbf{I}\ \mathbf{I}\ b \Rightarrow b$. K fires on I and b simultaneously.
- ( ) The reduction diverges because $\mathbf{K}\ \mathbf{I}$ contains no redex.

---

#### 10. The Y Combinator in SK

This section pulls together everything: if S and K are computationally complete, and if recursion is a computable operation, then S and K can express recursion — without any `def`, without any name, without any environment. The Y combinator written in pure SK is startling precisely because it looks like nothing else you have seen: a wall of S, K, and I with no variables anywhere. Yet it satisfies $Y\ g = g\ (Y\ g)$ for any $g$. The derivation in the Y combinator module explains *why* this works; here the goal is to see that it is expressible at all.

Recall from the lambda calculus module that the Y combinator satisfies $Y\ g = g\ (Y\ g)$. In strict (applicative-order) languages we use the Z combinator instead. In pure SK combinatory logic:

$$
\mathbf{Y} = \mathbf{S}\ (\mathbf{K}\ (\mathbf{S}\ \mathbf{I}\ \mathbf{I}))\ (\mathbf{S}\ (\mathbf{S}\ (\mathbf{K}\ \mathbf{S})\ \mathbf{K})\ (\mathbf{K}\ (\mathbf{S}\ \mathbf{I}\ \mathbf{I})))
$$

This derivation of Y from S and K — without any variables, without any lambda, without any notion of binding — is the combinatory logic proof that recursion is not a primitive: it is computable from application alone.

```python
# Z combinator (applicative-order Y) in combinatory style
# We build it from our birds to show the connection
Z = lambda f: (lambda x: f(lambda v: x(x)(v)))(lambda x: f(lambda v: x(x)(v)))

# factorial without def, without recursion primitives, only Z and lambdas
step = lambda self: lambda n: 1 if n == 0 else n * self(n - 1)
factorial = Z(step)
print([factorial(n) for n in range(8)])   # [1, 1, 2, 6, 24, 120, 720, 5040]

# Fibonacci the same way
fib_step = lambda self: lambda n: n if n <= 1 else self(n-1) + self(n-2)
fib = Z(fib_step)
print([fib(n) for n in range(10)])   # [0,1,1,2,3,5,8,13,21,34]
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

---

### Part III: The Flock in Practice

#### 11. Gabriel Lebec's Birds in JavaScript — and in Python

The birds stop being an abstract curiosity the moment you recognize them in code you already write. Every time you call `map(lambda x: x + 1, lst)` you are using I. Every time you write `key=lambda _: 0` you are using K. Every time you write `sorted(lst, key=lambda x: -x)` you are using a partial application of C. Gabriel Lebec's talk makes this explicit for JavaScript; this section makes it explicit for Python. The punchline: **combinators are not exotic theory — they are the names for the patterns you reach for every day without knowing it**.

Gabriel Lebec's 2016 talk "*A Flock of Functions*" demonstrates that every standard higher-order function in JavaScript is a bird in disguise. The key insight is that **you already use combinators every day** — you just call them `const`, `id`, `flip`, `compose`, and `curry`. Here is the full correspondence, in Python:

```python
# === The Flock — Python Edition ===
# Inspired by Gabriel Lebec's "A Flock of Functions" (2016)

# Primitive birds
I = lambda a: a                                      # Idiot / id
K = lambda a: lambda b: a                            # Kestrel / const
S = lambda f: lambda g: lambda x: f(x)(g(x))        # Starling

# Derived birds (all from SKI)
B = lambda f: lambda g: lambda x: f(g(x))           # Bluebird / compose
C = lambda f: lambda a: lambda b: f(b)(a)           # Cardinal / flip
W = lambda f: lambda x: f(x)(x)                     # Warbler / duplicate
M = lambda a: a(a)                                   # Mockingbird / self-apply
T = lambda a: lambda f: f(a)                         # Thrush / apply / pipe-right
V = lambda a: lambda b: lambda f: f(a)(b)            # Vireo / pair constructor

KI = K(I)   # False / second-selector

# Pair operations via Vireo
pair = V
fst  = lambda p: p(K)
snd  = lambda p: p(KI)

p = pair(1)(2)
print(fst(p), snd(p))   # 1 2

# Church numerals from K and I
zero  = K(I)                             # λf.λx.x -- apply f zero times
once  = lambda f: lambda x: f(x)         # λf.λx.fx -- apply f once
twice = lambda f: lambda x: f(f(x))      # λf.λx.f(fx)

to_int = lambda n: n(lambda k: k + 1)(0)
succ = lambda n: lambda f: lambda x: f(n(f)(x))

print(to_int(zero))   # 0
print(to_int(once))   # 1
print(to_int(twice))  # 2
print(to_int(succ(twice)))  # 3
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

---

#### 12. Point-Free Style: Programming Without Variables

Point-free programming is what happens when you take the combinator philosophy all the way to the surface of your code. Instead of writing `lambda x: f(g(x))` — which names $x$ even though $x$ appears in only one place — you write `B(f)(g)`, which says "compose f and g" without ever mentioning what they are applied to. This is not just an aesthetic preference: in Haskell it is the dominant style, because it emphasizes what transformations are being composed rather than what data they act on. The LEGO metaphor completes here: point-free code is a blueprint describing how bricks connect, not a sequence of operations on a specific piece.

**Point-free** (or "tacit") programming uses only combinators and function composition — no named variables, no lambdas. It is the ultimate expression of the combinatory-logic philosophy, and it is the standard style in Haskell. Here is the connection:

```python
from functools import reduce
B = lambda f: lambda g: lambda x: f(g(x))
W = lambda f: lambda x: f(x)(x)

# Point-full (with explicit variable x):
def square_then_add_one_v1(x):
    return x * x + 1

# Point-free (x never appears):
square   = W(lambda x: lambda y: x * y)  # W(mul) x = mul x x = x*x
add_one  = lambda x: x + 1
square_then_add_one = B(add_one)(square)  # compose: add_one . square

print(square_then_add_one(5))   # 26
print(square_then_add_one(3))   # 10

# A pipeline of birds: reduce with curried B using explicit application
pipeline = lambda *fns: reduce(lambda a, b: B(a)(b), fns) if len(fns) > 1 else fns[0]

process = pipeline(lambda s: s.replace(" ", "_"), str.lower, str.strip)
print(process("  Hello World  "))   # hello_world
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

---

##### Try It: With a Partner — Bird Identification

For each Python expression below, identify which bird (I, K, S, B, C, W, M, KI) it instantiates. One partner argues; the other challenges. Write the combinator reduction rule that proves the claim.

1. `lambda x: x`
2. `lambda x: lambda y: x`
3. `lambda f: lambda g: lambda x: f(g(x))`
4. `lambda f: lambda x: f(x)(x)`
5. `lambda x: lambda y: lambda z: x(z)(y(z))`
6. `lambda f: lambda a: lambda b: f(b)(a)`
7. `lambda a: lambda b: lambda f: f(a)(b)` — which bird pairs data?

---

#### 13. Exercises

1. **Reduction transcripts.** Reduce to normal form, one combinator rule per line, circling the redex:
   - (a) $\mathbf{B}\ f\ (\mathbf{B}\ g\ h)\ x$ — show this equals $\mathbf{B}\ (\mathbf{B}\ f\ g)\ h\ x$ (associativity of composition)
   - (b) $\mathbf{C}\ \mathbf{K}\ a\ b$ — what does this return, and what lambda term is it equivalent to?
   - (c) $\mathbf{W}\ \mathbf{K}\ a$ — one step is enough; what does it return?

2. **Bracket abstraction.** Use the three-rule bracket abstraction algorithm to convert $\lambda x.\ \lambda y.\ y\ x$ to an SKI expression. Verify by reducing your expression on two concrete arguments.

3. **Flock identification.** A colleague writes `f = lambda x: lambda _: x`. Which bird is this? Write the bird's one-line reduction rule, its lambda term, its Haskell name, and the two-word English description that explains what it does to its arguments.

4. **Pairs from birds.** Using only I, K, KI, V (Vireo), implement `swap` (exchange the components of a pair) as a bird expression, with no lambda. Verify on `pair(1)(2)`.

5. **SKI Turing completeness (research).** The combinator $\mathbf{S}\ \mathbf{K}$ applied to itself loops: $\mathbf{S}\ \mathbf{K}\ (\mathbf{S}\ \mathbf{K}) \Rightarrow \mathbf{K}\ (\mathbf{S}\ \mathbf{K})\ (\mathbf{K}\ (\mathbf{S}\ \mathbf{K})) \Rightarrow \mathbf{S}\ \mathbf{K}$. Write a one-paragraph explanation of why the existence of a non-terminating term (like $\Omega$ in the lambda calculus) is *necessary* for a system to be Turing complete, connecting to the Halting Problem.

---

#### 14. Further Reading

- Smullyan, Raymond. *To Mock a Mockingbird* (Knopf, 1985). The source of the bird names; a puzzle book that teaches combinatory logic through delightful ornithological fiction.
- Lebec, Gabriel. "Lambda as JS, or A Flock of Functions: Combinators, Lambda Calculus, and Church Encodings in JavaScript." London Functional Programmers Meetup, 2016. **This is the direct inspiration for this module.** Slides: https://speakerdeck.com/glebec/lambda-as-js-or-a-flock-of-functions-combinators-lambda-calculus-and-church-encodings-in-javascript — Source: https://github.com/glebec/lambda-talk — Watch the recording; every combinator in this activity appears there in JavaScript.
- **Lambda-Py / pycombinator** — combinators and Church encodings in Python: https://finsberg.github.io/pycombinator/docs/lambda-talk.html — the flock in Python rather than JavaScript; use it to check your hand reductions from this module against a mechanical reducer.
- Curry, H. B. and R. Feys. *Combinatory Logic, Volume I* (North-Holland, 1958). The foundational text.
- Hindley, J. Roger and Jonathan P. Seldin. *Lambda-Calculus and Combinators: An Introduction* (Cambridge UP, 2008). Modern, rigorous, and accessible.
- Turner, David. "Another Algorithm for Bracket Abstraction." *Journal of Symbolic Logic* 44(2), 1979. The optimized bracket abstraction that compilers actually use, avoiding the SKI expansion explosion.
- Tromp, John. "Binary Lambda Calculus and Combinatory Logic." *Randomness and Complexity* (World Scientific, 2007). SK programs as bit strings; the smallest known universal computer.

## Going Deeper: Algebraic Data Types and Pattern Matching

Pattern matching is like a smart `switch` statement that simultaneously tests the *shape* of a value AND extracts pieces from it in one step — think of a postal sorter that reads the address off the envelope while physically routing the package, never handling the contents without first knowing what kind of parcel it is. This matters because most bugs in large programs come from handling the wrong kind of data at the wrong time; pattern matching plus algebraic data types forces you to confront every possible case at the point where you write the code, not six months later in a production crash. By the end of this activity you will write code that simply cannot reach an unhandled state.

#### Learning Goals

By the end of this activity, you will be able to:

- Define algebraic data types (product types and sum types) using Python dataclasses and sealed class hierarchies
- Write pattern-matching code using Python's `match`/`case` syntax to safely deconstruct ADT values exhaustively
- Explain how sum types make illegal states unrepresentable and eliminate a class of runtime `None`/tag-check errors
- Apply ADTs and pattern matching to model a Mini-language AST, writing a recursive evaluator that dispatches on node type

> **"Pattern matching is the most powerful idea you haven't seen yet."**
>
> Today you will discover how types can model *everything* — shapes, trees, expressions, errors, results — and how pattern matching eliminates a whole class of runtime errors by making the impossible unrepresentable.

#### Directions and Roles

> **Before You Begin:** This activity assumes you can:
> - Write basic Python classes and use `isinstance()` to branch on type
> - Understand what a `None` return value means and why forgetting to check it causes `AttributeError`/`TypeError` crashes
> - Read simple recursive functions (a function that calls itself on a smaller input)
> If any of these feel shaky, review them first.

Work in groups of 3–4. Rotate roles every 20 minutes.

- **Facilitator**: Keeps discussion on track; ensures everyone contributes.
- **Recorder**: Writes down answers and code that the group agrees on.
- **Reporter**: Presents findings to the class; explains the group's reasoning.
- **Reflector**: Monitors group process; writes the reflection at the end.

---

Before diving into the solution, Model 1 shows the *exact pain point* that algebraic data types cure: a function that sometimes returns a real value and sometimes returns `None`, with no way for the type system to remind callers to handle both possibilities. Run the code and watch it crash — that crash is the motivating problem for everything that follows.

#### Model 1 — The Problem with Booleans and Null

In most languages, functions that can fail return either a special sentinel value (`-1`, `None`, `null`, `""`) or raise an exception. Both approaches have problems.

```python  liascript
# A "safe" dictionary lookup — the Python way
def find_user(user_id, db):
    if user_id in db:
        return db[user_id]   # returns a dict
    return None              # caller might forget to check!

users = {"alice": {"age": 30}, "bob": {"age": 25}}

u = find_user("charlie", users)
print(u["age"])   # 💥 TypeError: 'NoneType' object is not subscriptable
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

The problem: `None` *looks like* a real value. The type system doesn't force you to handle the failure case.

> **Watch out!** Python's `None` is assignable to *any* variable, so a dict value, a returned object, and a missing result all share the same type at runtime. This is by design in Python, but it means `u["age"]` compiles (or runs until that line) with no warning — the crash only happens when execution reaches the bad line, often deep in a call stack far from where `None` was returned.

**Critical Thinking Questions (CTQs)**

> **CTQ 1.1** What happens if you call `find_user("alice", users)["age"]`? What if you call `find_user("charlie", users)["age"]`?

> **CTQ 1.2** Can you tell from the function signature `find_user(user_id, db)` that it might return `None`? What documentation or convention would help?

> **CTQ 1.3** List two other common uses of `None` / `null` in Python or Java as a sentinel value. For each one, describe a bug that this pattern has caused in real software.

---

Model 2 introduces the core tool: a **sum type** (tagged union). Instead of returning `None`, we return a value whose *type tag* tells the caller whether an answer exists. The `match` statement then forces explicit handling of each tag, turning a potential runtime crash into a visible structural check at the call site.

#### Model 2 — Sum Types: Tagging Variants

A **sum type** (also called a **tagged union**, **variant**, or **discriminated union**) is a type whose values are exactly one of several *tagged* possibilities:

```
Option[A]  =  Some(value: A)  |  Nothing
Result[A]  =  Ok(value: A)    |  Err(message: str)
Shape      =  Circle(radius: float)
           |  Rectangle(width: float, height: float)
           |  Triangle(base: float, height: float)
```

The `|` means "OR" — a Shape is *either* a Circle *or* a Rectangle *or* a Triangle. Each variant carries different data. This is why they're called "sum" types: the set of all Shapes is the *sum* (union) of the sets of Circles, Rectangles, and Triangles.

```python  liascript
from dataclasses import dataclass
from typing import Optional, Union
from math import pi

@dataclass
class Circle:
    radius: float

@dataclass
class Rectangle:
    width: float
    height: float

@dataclass
class Triangle:
    base: float
    height: float

Shape = Circle | Rectangle | Triangle

def area(shape: Shape) -> float:
    match shape:
        case Circle(radius=r):
            return pi * r * r
        case Rectangle(width=w, height=h):
            return w * h
        case Triangle(base=b, height=h):
            return 0.5 * b * h

shapes = [Circle(5), Rectangle(3, 4), Triangle(6, 8)]
for s in shapes:
    print(f"{s} → area = {area(s):.2f}")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

> **Watch out!** Python's `match` statement does **not** warn you when your cases are non-exhaustive. If you add a new variant (say `Square`) but forget a matching `case Square(...)` arm, Python silently falls through all arms and `area()` returns `None` — no error, no warning. Haskell and Rust treat a non-exhaustive match as a compile-time error. In Python, you must add `case _ : raise NotImplementedError(f"Unknown shape: {shape}")` as the final arm to catch this yourself.

**CTQs**

> **CTQ 2.1** What happens if you add a new variant `Square(side: float)` to `Shape` but forget to update `area()`? Try it! What does Python do? What would a language like Haskell or Rust do?

> **CTQ 2.2** Explain in one sentence why "pattern matching is exhaustive checking." How does this relate to the `None` problem from Model 1?

> **CTQ 2.3** Rewrite `area()` using `if/elif/isinstance()` instead of `match`. Which version is clearer? Which is safer?

---

Model 3 shows how to apply sum types to the exact failure-handling problem from Model 1. An `Option` type has exactly two variants — `Some(value)` when something is there, and `Nothing` when it isn't — so a caller who holds an `Option` is *structurally reminded* to handle both cases before accessing any value inside.

#### Model 3 — The Option Type: Making Failure Explicit

```python  liascript
from dataclasses import dataclass
from typing import TypeVar, Generic, Callable

A = TypeVar('A')
B = TypeVar('B')

@dataclass
class Some(Generic[A]):
    value: A

@dataclass  
class Nothing:
    pass

Option = Some | Nothing

def find_user(user_id: str, db: dict) -> Option:
    if user_id in db:
        return Some(db[user_id])
    return Nothing()

def map_option(opt: Option, f: Callable) -> Option:
    """Apply f to the value inside Some, leave Nothing alone."""
    match opt:
        case Some(value=v):
            return Some(f(v))
        case Nothing():
            return Nothing()

def flat_map(opt: Option, f: Callable) -> Option:
    """f returns an Option; flatten the double-wrapping."""
    match opt:
        case Some(value=v):
            return f(v)
        case Nothing():
            return Nothing()

def get_or_default(opt: Option, default):
    match opt:
        case Some(value=v): return v
        case Nothing():     return default

# Usage
users = {"alice": {"age": 30, "city": "Philadelphia"}}
result = find_user("alice", users)
age    = map_option(result, lambda u: u["age"])
print(f"Alice's age: {get_or_default(age, 'unknown')}")

result2 = find_user("charlie", users)
age2    = map_option(result2, lambda u: u["age"])
print(f"Charlie's age: {get_or_default(age2, 'unknown')}")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

**CTQs**

> **CTQ 3.1** Why does `map_option` return `Option` rather than `Some`? What would go wrong if it returned `Some` directly?

> **CTQ 3.2** Compare `map_option` (value→value) with `flat_map` (value→Option). When would you use each?

> **CTQ 3.3** Chain: look up a user, then look up their city in a `cities` dict, then look up the zip code of that city. Write this chain using `flat_map` without any `if` statements or `None` checks.

---

Model 4 flips to the other half of algebraic data types: **product types**, which bundle *all* their fields together (like a struct). What makes this interesting is that pattern matching can reach *inside* nested product types in one `case` arm — you can simultaneously check the outer shape and destructure inner fields, including guarding on computed conditions.

#### Model 4 — Product Types: Bundling Data

A **product type** bundles *all* of several fields — it's the familiar "struct" or "record". The set of values is the *product* of the component sets (i.e., every combination exists).

```python  liascript
from dataclasses import dataclass

@dataclass(frozen=True)
class Point:
    x: float
    y: float

@dataclass(frozen=True)
class Line:
    start: Point
    end: Point

def length(line: Line) -> float:
    dx = line.end.x - line.start.x
    dy = line.end.y - line.start.y
    return (dx**2 + dy**2) ** 0.5

# Pattern matching on nested structures!
def describe(line: Line) -> str:
    match line:
        case Line(start=Point(x=0, y=0), end=Point(x=x2, y=y2)):
            return f"Line from origin to ({x2}, {y2})"
        case Line(start=Point(x=x1, y=y1), end=Point(x=x2, y=y2)) if x1 == x2:
            return f"Vertical line at x={x1}"
        case Line(start=Point(x=x1, y=y1), end=Point(x=x2, y=y2)) if y1 == y2:
            return f"Horizontal line at y={y1}"
        # Note: guard clauses (the `if` after a case) are evaluated left-to-right,
        # and only after the structural pattern succeeds.
        case _:
            return f"Diagonal line, length={length(line):.2f}"

lines = [
    Line(Point(0, 0), Point(3, 4)),
    Line(Point(2, 1), Point(2, 7)),
    Line(Point(1, 3), Point(9, 3)),
    Line(Point(1, 1), Point(4, 5)),
]
for l in lines:
    print(describe(l))
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

 > **Watch out!** Guard clauses (`if x1 == x2` after the pattern) are evaluated **in order, top to bottom** — Python tries the first arm whose pattern structurally matches, then checks its guard. If the guard fails, Python moves on to the *next arm*, it does **not** re-try the same arm. This means arm order matters: a `case _:` wildcard placed before a guarded arm will swallow all remaining cases.

**CTQs**

> **CTQ 4.1** What does "nested pattern matching" mean? Give a one-sentence description of what `case Line(start=Point(x=0, y=0), ...)` does.

> **CTQ 4.2** The `case _:` at the end is the "wildcard" or "default" case. What happens if you remove it? What does Python do? Why is this different from Haskell or Rust?

> **CTQ 4.3** Why are product types called "product" types? If `Point` has `x ∈ ℝ` and `y ∈ ℝ`, how many distinct `Point` values are there?

---

Model 5 combines everything: sum types can refer to *themselves*, producing recursive structures like trees. An expression tree is the canonical example — `Add(Mul(Num(2), Num(3)), Num(1))` represents `(2*3)+1`. The evaluator is a single `match` over the four node variants, each of which recursively evaluates its children, and the whole thing terminates because every recursive call is on a *strictly smaller* subtree.

#### Model 5 — Recursive Types: Trees and Expressions

The real power of sum types is **recursive definitions** — types that contain themselves:

```python  liascript
from __future__ import annotations
from dataclasses import dataclass

# An expression tree (Mini AST fragment)
@dataclass
class Num:
    value: int

@dataclass
class Add:
    left: Expr
    right: Expr

@dataclass
class Mul:
    left: Expr
    right: Expr

@dataclass
class Neg:
    operand: Expr

Expr = Num | Add | Mul | Neg

def eval_expr(e: Expr) -> int:
    match e:
        case Num(value=n):       return n
        case Add(left=l, right=r): return eval_expr(l) + eval_expr(r)
        case Mul(left=l, right=r): return eval_expr(l) * eval_expr(r)
        case Neg(operand=o):     return -eval_expr(o)

def pretty(e: Expr) -> str:
    match e:
        case Num(value=n):         return str(n)
        case Add(left=l, right=r): return f"({pretty(l)} + {pretty(r)})"
        case Mul(left=l, right=r): return f"({pretty(l)} * {pretty(r)})"
        case Neg(operand=o):       return f"(-{pretty(o)})"

# Build: 2 * (3 + (-4))
expr = Mul(Num(2), Add(Num(3), Neg(Num(4))))
print(f"{pretty(expr)} = {eval_expr(expr)}")

# Symbolic differentiation: d/dx (x * x)
@dataclass
class Var:
    name: str

Expr2 = Num | Var | Add | Mul | Neg  # augmented

def diff(e, var: str) -> Expr:
    """Symbolic differentiation: return d(e)/d(var)."""
    match e:
        case Num(_):               return Num(0)
        case Var(name=n) if n == var: return Num(1)
        case Var(_):               return Num(0)
        case Add(left=l, right=r): return Add(diff(l, var), diff(r, var))
        case Mul(left=l, right=r):
            # Product rule: (f*g)' = f'*g + f*g'
            return Add(Mul(diff(l, var), r), Mul(l, diff(r, var)))
        case Neg(operand=o):       return Neg(diff(o, var))

x_sq = Mul(Var("x"), Var("x"))   # x²
d_x_sq = diff(x_sq, "x")         # should be 2x (before simplification)
print(f"d/dx({pretty(x_sq)}) = {pretty(d_x_sq)}")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

**Step-by-Step Trace: `eval_expr(Mul(Num(2), Add(Num(3), Neg(Num(4)))))`**

This traces evaluation of the expression `2 * (3 + (-4))` built as `Mul(Num(2), Add(Num(3), Neg(Num(4))))`.

```
Call: eval_expr( Mul(Num(2), Add(Num(3), Neg(Num(4)))) )
  ├─ Pattern tried: Num(value=n)          → FAILS  (node is Mul, not Num)
  ├─ Pattern tried: Add(left=l, right=r)  → FAILS  (node is Mul, not Add)
  ├─ Pattern tried: Mul(left=l, right=r)  → MATCHES
  │     Bindings created: l = Num(2),  r = Add(Num(3), Neg(Num(4)))
  │
  │   Recurse left:  eval_expr( Num(2) )
  │     ├─ Pattern: Num(value=n)   → MATCHES
  │     │     Binding: n = 2
  │     └─ Returns: 2
  │
  │   Recurse right: eval_expr( Add(Num(3), Neg(Num(4))) )
  │     ├─ Pattern: Num(value=n)          → FAILS
  │     ├─ Pattern: Add(left=l, right=r)  → MATCHES
  │     │     Bindings: l = Num(3),  r = Neg(Num(4))
  │     │
  │     │   Recurse left:  eval_expr( Num(3) )
  │     │     ├─ Pattern: Num(value=n)  → MATCHES, n = 3
  │     │     └─ Returns: 3
  │     │
  │     │   Recurse right: eval_expr( Neg(Num(4)) )
  │     │     ├─ Pattern: Num(value=n)          → FAILS
  │     │     ├─ Pattern: Add(left=l, right=r)  → FAILS
  │     │     ├─ Pattern: Mul(left=l, right=r)  → FAILS
  │     │     ├─ Pattern: Neg(operand=o)        → MATCHES
  │     │     │     Binding: o = Num(4)
  │     │     │   Recurse: eval_expr( Num(4) )  → n = 4, returns 4
  │     │     └─ Returns: -4
  │     │
  │     └─ Returns: 3 + (-4) = -1
  │
  └─ Returns: 2 * (-1) = -2
```

Key observations from this trace:
- Each `match` arm is tried **in order**; only the *first* matching arm fires.
- Each arm **creates bindings** (`l`, `r`, `n`, `o`) for the sub-expressions it destructures.
- Recursion terminates because every recursive call is on a strictly *smaller* subtree — `Num` is the base case with no children.
- The total work is proportional to the *number of nodes* in the tree.

**CTQs**

> **CTQ 5.1** The derivative of `x²` by the product rule is `x*1 + 1*x` (before simplification). Is `pretty(d_x_sq)` what you expected? What simplification step is missing?

> **CTQ 5.2** Why does `Expr` have to be declared with `from __future__ import annotations`? What happens without it?

> **CTQ 5.3** The `diff` function is an example of a "structural recursion." What invariant guarantees that it terminates?

---

Model 6 builds on `Option` to add *error messages*: a `Result` type is either `Ok(value)` (success) or `Err(message)` (failure with an explanation). The key insight is that you can chain multiple fallible operations into a pipeline — `bind_result` acts as the connector — and errors automatically short-circuit the rest of the chain without any `if` checks or `try/except` blocks.

#### Model 6 — Result Types: Railway-Oriented Programming

```python  liascript
from dataclasses import dataclass
from typing import TypeVar, Generic, Callable

A = TypeVar('A')

@dataclass
class Ok(Generic[A]):
    value: A

@dataclass
class Err:
    message: str

Result = Ok | Err

def safe_div(a: float, b: float) -> Result:
    if b == 0:
        return Err("Division by zero")
    return Ok(a / b)

def safe_sqrt(x: float) -> Result:
    if x < 0:
        return Err(f"Square root of negative: {x}")
    return Ok(x ** 0.5)

def bind_result(result: Result, f: Callable) -> Result:
    """Chain operations: if Ok, apply f; if Err, propagate the error."""
    match result:
        case Ok(value=v): return f(v)
        case Err(_):      return result

# Pipeline: compute sqrt(100 / x)
def pipeline(x):
    return bind_result(
        safe_div(100, x),
        lambda q: safe_sqrt(q)
    )

for x in [4, -1, 0, 25]:
    result = pipeline(x)
    match result:
        case Ok(value=v): print(f"√(100/{x}) = {v:.4f}")
        case Err(message=msg): print(f"Error for x={x}: {msg}")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

**CTQs**

> **CTQ 6.1** This pattern — chaining operations that might fail, propagating errors automatically — is called "railway-oriented programming" or the "Error monad." How is `bind_result` here similar to `flat_map` from Model 3?

> **CTQ 6.2** Compare this style to Python's `try/except` approach. What are the tradeoffs? When would you prefer each?

> **CTQ 6.3** Rust uses `Result<T, E>` and the `?` operator for this pattern. The `?` operator desugars to something like `bind_result`. Look up how it works and explain the desugaring in one paragraph.

---

#### Multiple Choice

Which of the following correctly describes a sum type?

    [( )] A type formed by combining all fields of two types (like a struct with merged fields)
    [(x)] A type whose values are one of several tagged alternatives — like `Some(value)` or `Nothing`
    [( )] A type that stores a running total
    [( )] A type that inherits from multiple parent classes

---

In Python 3.10+'s `match` statement, what does `case _:` mean?

    [( )] Match only `None` values
    [( )] Match only the literal string `"_"`
    [(x)] Match any value; acts as a default / catch-all case
    [( )] Raise a `ValueError` if reached

---

Consider: `@dataclass class Pair: fst: int; snd: bool`. How many distinct `Pair` values are there (mathematically)?

    [( )] Infinite (ints are infinite)
    [(x)] `|int| × |bool|` = infinitely many int values × 2 bool values (still infinite, but the structure is a product)
    [( )] 2 (one per field)
    [( )] Undefined — Python dicts have no size

---

#### Exercises

##### Exercise 1 — JSON Value Type (20 min)

JSON values can be: `null`, a boolean, a number, a string, an array (list of JSON values), or an object (dict mapping strings to JSON values). Model this as a recursive sum type in Python and write:

- `JsonVal` type alias with 6 variants
- `json_to_python(val: JsonVal)` that converts to native Python types
- `json_size(val: JsonVal) -> int` that returns the total number of scalar leaves

Test it on: `{"name": "Alice", "scores": [95, 87, 92], "active": true}`

##### Exercise 2 — Mini AST Extensions (20 min)

Extend the `Expr` type from Model 5 to add:
- `Let(name: str, value: Expr, body: Expr)` — let binding
- `Var(name: str)` — variable reference (already there)
- `IfExpr(cond: Expr, then_: Expr, else_: Expr)` — if-expression

Update `eval_expr` to handle these (pass an environment dict for variables).

Test: evaluate `let x = 5 in if x > 3 then x * 2 else 0`.

##### Exercise 3 — Type Checker with ADTs (25 min)

Write a `type_check(e: Expr, env: dict) -> str` function that returns `"Int"`, `"Bool"`, or raises `TypeError`:

- `Num` → `"Int"`
- `Add`, `Mul`, `Neg` → require both sides `"Int"`, return `"Int"`
- `IfExpr` → require condition `"Bool"`, require branches same type, return that type
- `Var` → look up in env

Test both valid and invalid expressions (e.g., `1 + true` should raise `TypeError`).

##### Exercise 4 — Pattern Matching in Mini (30 min, harder)

Design a syntax extension for Mini that supports pattern matching. Write:

1. New AST nodes: `MatchExpr(scrutinee: Expr, arms: list[MatchArm])` and `MatchArm(pattern: Pattern, body: Expr)` with `Pattern = WildPat | LitPat(value) | VarPat(name) | ConstructorPat(name, sub_patterns)`
2. An evaluator case for `MatchExpr` that tries each arm in order, binding variables
3. Two test cases: matching on integers, matching on a `Shape` constructor

---

#### Reflection

*(Write your answers individually, then discuss with your group.)*

1. Before today, how did you handle "a function that might fail" in Python? How does `Option`/`Result` change your approach?

2. Pattern matching checks all cases — in what sense is this "exhaustive"? Python's `match` is not exhaustive by default; Haskell and Rust give warnings/errors. What are the implications for large codebases?

3. How does this connect to the final project? Which extension option (from `asmt-final-project.md`) does ADT pattern matching map to? What would you need to add to Mini to support it?

---

#### Further Reading

- **Python 3.10 structural pattern matching** — PEP 634: https://peps.python.org/pep-0634/
- **"Why Functional Programming Matters"** — John Hughes: https://www.cs.kent.ac.uk/people/staff/dat/miranda/whyfp90.pdf
- **Rust enums and pattern matching** — The Rust Book Ch. 6: https://doc.rust-lang.org/book/ch06-00-enums.html
- **Haskell algebraic data types** — Learn You a Haskell Ch. 8
- **"Making Illegal States Unrepresentable"** — Scott Wlaschin: https://fsharpforfunandprofit.com/posts/designing-with-types-making-illegal-states-unrepresentable/
- **TAPL Ch. 11** — Simple Extensions (pairs, sums, variants) — Pierce
