# The Lambda Calculus, Part 1: Syntax and Reduction
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

Beneath Scheme, beneath Python's `lambda`, beneath every functional language, sits a formal system from 1936 with **three forms of expression and one rule of computation**: Alonzo Church's **lambda calculus**, in which functions are the only thing that exists, and computing means substituting arguments into bodies. Today we learn to read it and to reduce expressions **by hand**, the way Church did, because by-hand reduction is the only way the system becomes real. The arc: **the three forms $\rightarrow$ free and bound variables $\rightarrow$ beta reduction by hand $\rightarrow$ alpha renaming when names collide**.

---

## Directions and Group Roles

Work in your POGIL team with rotated roles (**Manager**, **Recorder**, **Presenter**, **Reflector**). Today is a whiteboard day: every reduction is written out stepwise, and teammates check each other's substitutions character by character. The Recorder photographs the board for the discussion post. After class, respond to the reflective prompt individually in your notebook.

---

# Part I: The Whole Language

## 1. Three Forms

A lambda expression is exactly one of:

$$
e ::= x \;\mid\; (\lambda x.\, e) \;\mid\; (e_1\; e_2)
$$

a **variable**; an **abstraction** (a function of one parameter $x$ with body $e$, written `λx.e`); or an **application** ($e_1$ applied to $e_2$). That is the entire grammar; there are no numbers, no booleans, no operators (Part 2 builds them all *from functions*). Conventions: application associates left ($f\,a\,b$ means $((f\,a)\,b)$), the body of a λ extends as far right as possible, and multi-parameter functions are nested single-parameter ones: $\lambda x y. e$ abbreviates $\lambda x. (\lambda y. e)$, the trick called **currying**, after Haskell Curry.

**Bound and free.** In $\lambda x.\, x\, y$: the $x$ in the body is **bound** by the λ; $y$ is **free** (it refers to something outside). Binding here is your scope module's lexical scoping, in its original mathematical form: a λ is a binder, its body is the scope.

---

## Model 1: Parse by Eye

### Critical Thinking Questions

1. Fully parenthesize each, then circle binders and underline free variables: (a) $\lambda x. x$; (b) $\lambda x. \lambda y. x$; (c) $(\lambda x. x\, x)(\lambda x. x\, x)$; (d) $\lambda x. x\, (\lambda y. y\, x)$.
2. Expression (b) takes two arguments (curried) and returns the first. What familiar Python one-liner is it? Write the Python.
3. In (d), the inner $x$ at the far right: bound by which λ? Apply the innermost-enclosing-binder rule and connect it, by name, to the environment chain's lookup walk.
4. Why does the grammar need no precedence ladder? (You answered this once for Scheme; the lambda calculus is where Scheme got it.)

---

# Part II: Computation Is Substitution

## 2. Beta Reduction

**The one rule.** An application of an abstraction to an argument reduces by substituting:

$$
(\lambda x.\, e)\; a \;\;\rightarrow_\beta\;\; e[x := a]
$$

read "$e$ with every *free* occurrence of $x$ replaced by $a$." A **redex** is any subexpression of that shape; an expression with no redexes is in **normal form**: the answer. Reduce stepwise, one redex at a time, drawing an arrow per step.

Worked example, fully spelled out:

$$
(\lambda x. \lambda y.\, x)\; A\; B
\;\rightarrow_\beta\; (\lambda y.\, A)\; B
\;\rightarrow_\beta\; A
$$

Step 1 substituted $A$ for $x$ in $\lambda y. x$; the $y$-abstraction remained, now constant; step 2 applied it to $B$, which was discarded because $y$ never occurs in the body. The function selected its first argument: behavior, from substitution alone.

---

## Model 2: Reduce by Hand

### Critical Thinking Questions

5. Reduce, one arrow per step, all the way to normal form: (a) $(\lambda x.\, x)\, z$; (b) $(\lambda x.\, x\, x)(\lambda y.\, y)$; (c) $(\lambda x. \lambda y.\, y)\; A\; B$ (compare with the worked example: what does *this* function select?); (d) $(\lambda f. \lambda x.\, f\, (f\, x))\; g\; a$.
6. Expression (d)'s result applies $g$ twice. You wrote `twice(f)` in Python last week; write the lambda calculus term and the Python side by side. Which is which?
7. Now reduce $(\lambda x.\, x\, x)(\lambda x.\, x\, x)$, the famous **Omega**. Perform two steps. What do you notice, and what does Omega prove about whether every expression has a normal form?
8. In (d) you had a choice of which redex to reduce first at one point. Try the other order; does the normal form change? (The Church-Rosser theorem says it cannot; you have just collected one data point.)

---

## 3. Alpha Renaming: When Names Collide

Substitution has one trap: **capture**. Reduce $(\lambda x. \lambda y.\, x)\; y$ naively and the free $y$ we substitute lands inside $\lambda y$, where it is suddenly, wrongly, bound: the meaning changed. The repair is **alpha renaming**: bound names are arbitrary ($\lambda y. e$ and $\lambda z. e[y := z]$ are the same function), so rename the binder first:

$$
(\lambda x. \lambda y.\, x)\; y \;=_\alpha\; (\lambda x. \lambda z.\, x)\; y \;\rightarrow_\beta\; \lambda z.\, y
$$

The result correctly returns the *free* $y$, whatever it refers to outside. Capture is the shadowing bug from your scope module, in formal dress, and alpha renaming is the formal version of "pick a fresh local name."

[[MC]]
The reduction $(\lambda x. \lambda y.\, x\, y)\; y \rightarrow \lambda y.\, y\, y$ is wrong because:
- ( ) Application associates left
- ( ) The expression was already in normal form
- (x) The substituted free y was captured by the inner binder; alpha-renaming the inner λy is required first
- ( ) Beta reduction may only be applied once per expression

---

# Part III: Runnable Models

## Model 3: Beta Reduction Step Tracer

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

## Model 4: Alpha Equivalence Checker

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
- **Lambda Py** — run the calculus interactively in your browser: https://finsberg.github.io/pycombinator/docs/lambda-talk.html — experiment with the reductions from today's module without installing anything.
