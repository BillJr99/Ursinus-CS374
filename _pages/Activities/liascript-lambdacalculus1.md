<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://github.com/BillJr99/Ursinus-CS374-Fall2026/blob/gh-pages/_pages/Activities/liascript-lambdacalculus1.md or locally via https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374/gh-pages/_pages/Activities/liascript-lambdacalculus1.md

import: https://raw.githubusercontent.com/liascript/CodeRunner/master/README.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

# The Lambda Calculus, Part 1: Syntax and Reduction

The lambda calculus is a minimal formal system invented by Alonzo Church in the 1930s: it has only functions, application, and variables, yet it can compute anything a Turing machine can. Understanding lambda calculus is like learning to count using just a single mark on a page: it strips away all complexity to reveal the pure essence of computation. In this first part, you will learn to read, write, and reduce lambda expressions by hand, the foundational skill for everything that follows.

## Learning Goals

By the end of this activity, you will be able to:

- Write and read lambda calculus expressions in formal notation, applying left-associative application and maximal-body abstraction conventions
- Classify every variable occurrence in a lambda expression as either bound (and identify its binding λ) or free
- Perform beta reduction step by step on paper, substituting arguments into function bodies following the one reduction rule
- Recognize when variable capture would occur during substitution and apply alpha-renaming to avoid it
- Translate between lambda calculus notation and equivalent Python `lambda` expressions

> **Before You Begin: Prerequisites**
>
> This activity works best if you are comfortable with the following. If any feel shaky, review them before the session.
>
> - **Functions as values**: In Python you can write `f = lambda x: x + 1` and pass `f` to another function as an argument. Lambda calculus is built entirely on this idea.
> - **Substitution**: Evaluating `(lambda x: x * x)(5)` means replacing every `x` in the body with `5`. Lambda calculus makes this the *only* rule of computation; you will apply it by hand today.
> - **Recursive reduction**: Complex expressions simplify by applying the substitution rule repeatedly. Each application is one step; you will write out every step on the whiteboard.

Lambda calculus was invented by Alonzo Church in the 1930s to answer a fundamental question: what does it mean to *compute*? Church showed that two symbols, λ (for "function") and · (for "apply"), are sufficient to compute anything that is computable. Every programming language you have ever used, including Python, is secretly a lambda calculus with extra syntax. By the end of this activity, you will have seen Python's entire evaluation model in eight lines of math.

Beneath the Scheme of *Scheme: Code as Data*, beneath Python's `lambda`, beneath every functional language, sits a formal system from 1936 with **three forms of expression and one rule of computation**: Alonzo Church's **lambda calculus**, in which functions are the only thing that exists, and computing means substituting arguments into bodies. Today we learn to read it and to reduce expressions **by hand**, the way Church did, because by-hand reduction is the only way the system becomes real. The arc: **the three forms $\rightarrow$ free and bound variables $\rightarrow$ beta reduction by hand $\rightarrow$ alpha renaming when names collide**.

---

## Directions and Group Roles

Work in your POGIL team with rotated roles (**Manager**, **Recorder**, **Presenter**, **Reflector**). Today is a whiteboard day: every reduction is written out stepwise, and teammates check each other's substitutions character by character. The Recorder photographs the board for the discussion post. After class, respond to the reflective prompt individually in your notebook.

---

# Part I: The Whole Language

## Notation Bridge: Lambda Calculus vs. Python

Before we dive into the formal rules, here is a translation table. Every lambda calculus expression you will encounter today has a direct Python equivalent. Keep this table handy: whenever a lambda expression looks unfamiliar, find its Python mirror here.

| Lambda Calculus | Python | Meaning |
|---|---|---|
| `λx.x` | `lambda x: x` | identity function |
| `λx.λy.x` | `lambda x: lambda y: x` | constant function (returns first arg) |
| `(λx.x+1) 5` | `(lambda x: x+1)(5)` | function application |
| `λf.λx.f (f x)` | `lambda f: lambda x: f(f(x))` | apply-twice |

> **Note for beginners**: In Python, `lambda x: x` is a function with no name that takes one argument `x` and returns `x`. Lambda calculus is the same idea, just written with a λ symbol and a dot instead of a colon. The table above maps every symbol one-to-one.

**Core notation reference**: the three fundamental constructs of lambda calculus:

| Lambda Notation | Python Equivalent | Meaning |
|-----------------|-------------------|---------|
| `λx.e` | `lambda x: e` | A function taking x, returning e |
| `(f a)` | `f(a)` | Apply function f to argument a |
| `[x -> a]e` | (substitution) | Replace x with a in e |

---

## 1. Three Forms

> **Intuition**: Every lambda calculus expression is built from exactly three kinds of thing: a name (`x`), a function definition (`λx.body`), or a function call (`f arg`). That is the whole language. Before reading further, convince yourself that Python's `lambda x: f(f(x))` uses all three: `x` and `f` are variables, `lambda x: ...` is an abstraction, and `f(f(x))` is two nested applications.

A lambda expression is exactly one of:

$$
e ::= x \;\mid\; (\lambda x.\, e) \;\mid\; (e_1\; e_2)
$$

a **variable**; an **abstraction** (a function of one parameter $x$ with body $e$, written `λx.e`); or an **application** ($e_1$ applied to $e_2$). That is the entire grammar; there are no numbers, no booleans, no operators (Part 2 builds them all *from functions*). Conventions: application associates left ($f\,a\,b$ means $((f\,a)\,b)$), the body of a λ extends as far right as possible, and multi-parameter functions are nested single-parameter ones: $\lambda x y. e$ abbreviates $\lambda x. (\lambda y. e)$, the trick called **currying**, after Haskell Curry.

> **Watch out**: `λx.λy.x` is a function that takes `x`, then returns *a function* that takes `y`, then returns `x`. You have to apply it TWICE to get a value out. This is called "currying", named after Haskell Curry. In Python: `(lambda x: lambda y: x)(3)(99)` returns `3`. Calling `(lambda x: lambda y: x)(3)` alone gives you back a function, not a value.

**Bound and free.** In $\lambda x.\, x\, y$: the $x$ in the body is **bound** by the λ; $y$ is **free** (it refers to something outside). Binding here is your scope module's lexical scoping, in its original mathematical form: a λ is a binder, its body is the scope.

> **Watch out! Application is left-associative.** `f a b` means `(f a) b`, NOT `f (a b)`. Concretely: `f` is applied to `a` first, producing a new function, and *that* function is applied to `b`. This matters most for curried functions: `(λx.λy.x) A B` is `((λx.λy.x) A) B`, and the first application peels off one λ, giving `(λy.A) B`, which then reduces to `A`. If you mistakenly group it as `(λx.λy.x) (A B)`, you get a completely different computation.

---

## Model 1: Parse by Eye

> **Intuition**: Parsing lambda expressions is a mechanical skill: apply the two conventions (left-associative application, body extends right) until every sub-expression is explicitly parenthesized. A reliable strategy is to work outside-in: find the outermost application first, then recurse into each sub-expression. When you encounter a `λ`, its body runs all the way to the right end of the current parenthesization level.

### Critical Thinking Questions

1. Fully parenthesize each, then circle binders and underline free variables: (a) $\lambda x. x$; (b) $\lambda x. \lambda y. x$; (c) $(\lambda x. x\, x)(\lambda x. x\, x)$; (d) $\lambda x. x\, (\lambda y. y\, x)$.
2. Expression (b) takes two arguments (curried) and returns the first. What familiar Python one-liner is it? Write the Python.
3. In (d), the inner $x$ at the far right: bound by which λ? Apply the innermost-enclosing-binder rule and connect it, by name, to the environment chain's lookup walk.
4. Why does the grammar need no precedence ladder? (You answered this once for Scheme; the lambda calculus is where Scheme got it.)

---

# Part II: Computation Is Substitution

## 2. Beta Reduction

> **Intuition**: Beta reduction is function application: find a function `(λx.body)` applied to an argument `a`, and replace every free occurrence of `x` in `body` with `a`. That is literally it. The word "beta" just names this one rule so we can refer to it precisely. Each step erases one `λ` from the expression and performs one substitution. When no more lambdas are applied to arguments, you have reached normal form: the answer.

**The one rule.** An application of an abstraction to an argument reduces by substituting:

$$
(\lambda x.\, e)\; a \;\;\rightarrow_\beta\;\; e[x := a]
$$

read "$e$ with every *free* occurrence of $x$ replaced by $a$." A **redex** is any subexpression of that shape; an expression with no redexes is in **normal form**: the answer. Reduce stepwise, one redex at a time, drawing an arrow per step.

> **Watch out**: β-reduction is purely syntactic substitution. `(λx.x*x) (2+3)` does NOT compute `2+3` first; it substitutes the unevaluated expression `(2+3)` for `x`, giving `(2+3)*(2+3)`. Whether arguments are evaluated before substitution (eager) or after (lazy) is the call-by-value vs call-by-name distinction. Python uses call-by-value (eager), so Python would compute `5` first and then substitute. Pure lambda calculus by default uses call-by-name (lazy).

### Worked Example 1: Identity Function

$$
(\lambda x.\, x)\; z
$$

Step by step:

```
(λx.x) z
->β  [x := z] x      # substitute z for every free x in the body
->β  z               # the body was just x, now replaced by z
```

Result: `z`. The identity function returns its argument unchanged.

### Worked Example 2: Constant Function (K Combinator)

$$
(\lambda x. \lambda y.\, x)\; A\; B
$$

Step by step (remember: application is left-associative, so this is $(((\lambda x. \lambda y. x)\; A)\; B)$):

```
(λx.λy.x) A B
->β  [x := A] (λy.x)   B    # substitute A for x in body (λy.x)
->β  (λy.A) B               # after substitution, body is (λy.A)
->β  [y := B] A             # substitute B for y in body A
->β  A                      # y never appeared in body, so B is discarded
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
->β  [f := g] (λx. f(f x))   a   # substitute g for f in body
->β  (λx. g(g x)) a              # body now has g in place of f
->β  [x := a] g(g x)             # substitute a for x in body
->β  g(g a)                      # x replaced by a in both places
```

Result: `g(g a)`. This applies `g` twice to `a`, exactly what `twice(g)(a)` does in Python.

> **Watch out! The order of reduction matters for termination, but not for the final result.** If you reduce the same expression two different ways (choosing different redexes at each step), you may take a different number of steps, or one path may loop while the other terminates. However, the Church-Rosser theorem guarantees that if both paths reach a normal form, the normal forms are identical. A key corollary: always prefer normal-order (outermost-first) reduction when working by hand, because it is the strategy most likely to find a normal form if one exists.

---

## Model 2: Reduce by Hand

> **Intuition**: Work through each reduction at the pace of one substitution per arrow. Before you write an arrow, identify: (1) which subexpression is the redex (a `(λx.body) arg` shape) and (2) what substitution you will perform. Write the result of the substitution, draw the arrow, and look for the next redex. The Omega term in Question 7 is the key insight: some expressions have no normal form, which means not every computation terminates.

### Critical Thinking Questions

5. Reduce, one arrow per step, all the way to normal form: (a) $(\lambda x.\, x)\, z$; (b) $(\lambda x.\, x\, x)(\lambda y.\, y)$; (c) $(\lambda x. \lambda y.\, y)\; A\; B$ (compare with the worked example: what does *this* function select?); (d) $(\lambda f. \lambda x.\, f\, (f\, x))\; g\; a$.
6. Expression (d)'s result applies $g$ twice. You wrote `twice(f)` in Python in the *Functional Programming* activity; write the lambda calculus term and the Python side by side. Which is which?
7. Now reduce $(\lambda x.\, x\, x)(\lambda x.\, x\, x)$, the famous **Omega**. Perform two steps. What do you notice, and what does Omega prove about whether every expression has a normal form?
8. In (d) you had a choice of which redex to reduce first at one point. Try the other order; does the normal form change? (The Church-Rosser theorem says it cannot; you have just collected one data point.)

---

## 3. Alpha Renaming: When Names Collide

> **Intuition**: The variable capture problem is subtle but important. Imagine you are substituting a free variable `y` into an expression that happens to bind `y` internally. The substituted `y` would fall under the inner binder and suddenly mean something different. The fix is simple: rename the inner binder to a fresh name before substituting. Think of it as "pick a local variable name that does not clash with anything in scope", exactly what good programmers do to avoid shadowing bugs.

Substitution has one trap: **capture**. Reduce $(\lambda x. \lambda y.\, x)\; y$ naively and the free $y$ we substitute lands inside $\lambda y$, where it is suddenly, wrongly, bound: the meaning changed. The repair is **alpha renaming**: bound names are arbitrary ($\lambda y. e$ and $\lambda z. e[y := z]$ are the same function), so rename the binder first:

$$
(\lambda x. \lambda y.\, x)\; y \;=_\alpha\; (\lambda x. \lambda z.\, x)\; y \;\rightarrow_\beta\; \lambda z.\, y
$$

The result correctly returns the *free* $y$, whatever it refers to outside. Capture is the shadowing bug from your scope module, in formal dress, and alpha renaming is the formal version of "pick a fresh local name."

> **Watch out**: Variable capture is a subtle bug. When you substitute a value that contains a free variable `y` into a body that binds `y`, the `y` in your value would accidentally become bound by the inner lambda. The fix (alpha renaming) is just like how Python avoids variable shadowing bugs: pick a fresh name for the inner binder that does not collide with anything free in the argument.

### Step-by-step capture example (WRONG, then RIGHT):

**Wrong (capture):**

```
(λx.λy.x) y
->β  [x := y] (λy.x)    # naively substitute y for x
->β  λy.y               # WRONG: the free y is now captured by λy!
```
This says "a function that ignores its argument and returns ... its argument." That is the identity function, not the constant function. We changed the meaning!

**Right (alpha-rename first):**

```
(λx.λy.x) y
=α  (λx.λz.x) y        # rename bound y to fresh z (safe because z is not free in argument)
->β  [x := y] (λz.x)    # now substitute y for x
->β  λz.y               # correct: a function that ignores z and returns the free y
```

The reduction $(\lambda x. \lambda y.\, x\, y)\; y \rightarrow \lambda y.\, y\, y$ is wrong because:

[( )] Application associates left
[( )] The expression was already in normal form
[(X)] The substituted free y was captured by the inner binder; alpha-renaming the inner λy is required first
[( )] Beta reduction may only be applied once per expression

---

# Part III: Runnable Models

## Model 3: Beta Reduction Step Tracer

> **Intuition**: This tracer represents lambda expressions as nested Python tuples and implements the substitution rule explicitly. Before running it, predict what the output will be for the first two examples by applying the substitution rule by hand. Then run the code and compare. Pay special attention to the alpha-rename message in the capture example: this is the mechanism you applied manually in Section 3, now automated.

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
            # Bound by this lambda - no substitution inside
            return expr
        elif expr[1] in free_vars(replacement):
            # Capture risk! Alpha-rename the bound variable first
            new_param = fresh(expr[1])
            renamed_body = subst(expr[2], expr[1], var(new_param))
            print(f"  [α-rename] {expr[1]} -> {new_param} to avoid capture")
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
            # This is a redex: (λx.body) arg -> body[x := arg]
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

> **Intuition**: This simulator uses Python dataclasses (`Var`, `Lam`, `App`) to represent the three syntactic forms as Python objects, making the structure of each expression explicit and inspectable. Use it to check your hand reductions from Model 2: build the same expression you reduced on the whiteboard, run `normalize`, and verify the steps match. Notice that the `subst` function here does not implement full capture-avoiding renaming; compare this to Model 3 to see what is missing.

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
            # Beta reduction: (λx.body) arg -> [x:=arg] body
            result = subst(expr.fun.body, expr.fun.param, expr.arg)
            print(f"  ->β {result}")
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

> **Intuition**: De Bruijn indices solve the alpha-equivalence problem elegantly: instead of naming bound variables, replace each one with a number saying "I am bound by the lambda that is this many steps outward." Under this scheme, `λx.x` and `λy.y` both become `λ_.#0` (the bound variable is index 0, the immediately enclosing lambda). Two expressions are alpha-equivalent if and only if their de Bruijn representations are identical. Free variables keep their names because they refer to the *same* external binding regardless of renaming.

Two lambda expressions are **alpha-equivalent** ($=_\alpha$) if one can be obtained from the other by consistently renaming bound variables. They are *semantically identical*; only the choice of parameter names differs.

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

    ("λx.λy.x  vs  λx.λy.y  (K vs K', pick first vs second)",
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
print("They match -> alpha-equivalent.")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

### Critical Thinking Questions

13. De Bruijn indices replace variable names with *distances to the binder*. For `λx.λy.x`, the `x` in the body has index 1 (one lambda up). Confirm this by reading the printed de Bruijn structure and explain why index 0 would mean "bound by the innermost lambda."
14. The checker says `λx.x y` is alpha-equivalent to `λz.z y`. Why must the free variable `y` remain as a name (not an index) for the comparison to be correct? What would go wrong if free variables were also replaced by indices?
15. Two expressions with different de Bruijn representations are *never* alpha-equivalent. Prove this claim in two sentences by referring to what de Bruijn indices encode.
16. In your CS374 interpreter, when do two AST nodes represent "the same" computation? Is that relation alpha-equivalence, beta-normal-form equality, or something else? Give a concrete example where the distinction matters.

---

## Model 5: Free vs Bound Variables and WHNF

> **Intuition**: WHNF is the "good enough" answer for lazy evaluation. An expression is in WHNF when the outermost position is not a redex: it is either a variable, a lambda, or an application whose function is not a lambda. Haskell stops here rather than reducing everything inside, which is why it can represent infinite lists: the spine of the list is in WHNF (a cons cell whose tail is an unevaluated thunk), and you only reduce the tail when you actually ask for the next element.

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
        # Otherwise, the head is not a lambda - WHNF (even if args have redexes)
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

# λx.x  - identity: no free vars, x is bound; is a lambda so WHNF
classify(lam('x', var('x')), "λx.x")

# λx. x y  - y is free
classify(lam('x', app(var('x'), var('y'))), "λx.(x y)")

# (λx.x) z  - outermost is a redex: NOT WHNF, NOT normal form
classify(app(lam('x', var('x')), var('z')), "(λx.x) z")

# f ((λx.x) z)  - outermost head is free var f: IS WHNF, but NOT normal form
classify(app(var('f'), app(lam('x', var('x')), var('z'))), "f ((λx.x) z)")

# λy. (λx.x) z  - lambda at top: IS WHNF; body has redex, so NOT full NF
classify(lam('y', app(lam('x', var('x')), var('z'))), "λy.((λx.x) z)")

print("Key distinction:")
print("  Normal Form  - no redexes ANYWHERE in the expression.")
print("  WHNF         - outermost position is not a redex (body may still have them).")
print("  Lazy evaluation (Haskell) only reduces to WHNF: avoids evaluating")
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

---
**In-class work stops here.** Everything below is homework and going-deeper material: attempt the exercises before the related assignment.

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
- **Lambda-Py / pycombinator**; combinators and Church encodings in Python; run the calculus interactively in your browser: https://finsberg.github.io/pycombinator/docs/lambda-talk.html, experiment with the reductions from today's module without installing anything.

---

## Going Deeper (Optional Pointers)

The core lesson above stands on its own. The deep-dive appendices that used to follow it now live elsewhere:

> **Going further:** the material that used to live here, combinatory logic and the SKI calculus: the "flock of birds" (S, K, I, B, C, W and friends), deriving B and C from S and K, bracket abstraction, and point-free programming (is covered in depth as the advanced "Combinatory Logic and the SKI Calculus" section of the dedicated tutorial: [Implementing a Lambda Calculus Reducer](https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374/gh-pages/_pages/Tutorials/tutorial-lambda-calculus-reducer.md). **Direction D of the Functional assignment builds on this material.** Explore it when your project or curiosity calls for it.

> **Going further:** the material that used to live here) algebraic data types and pattern matching: is covered in the Modern Language Features activity (pattern matching, including matching on nested structures, in class) and the dedicated guide: [Typing Disciplines (Strong vs. Weak, Static vs. Dynamic, and Gradual Typing](https://www.billmongan.com/Ursinus-CS374-Fall2026/Tutorials/TypingDisciplines) (product and sum types). The specific worked ADT examples from the old appendix) safe lookups, Maybe-style values, and symbolic differentiation over an expression tree, make a good self-study exercise. Explore them when your project or curiosity calls for it.

---

Up next: *The Lambda Calculus, Part 2* builds booleans, numbers, and arithmetic from nothing but these functions; the Church encodings at the heart of the Functional assignment's Direction C.
