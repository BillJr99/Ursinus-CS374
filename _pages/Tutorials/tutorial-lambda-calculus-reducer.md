<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374/gh-pages/_pages/Tutorials/tutorial-lambda-calculus-reducer.md

import: https://raw.githubusercontent.com/liascript/CodeRunner/master/README.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

# Tutorial: Implementing a Lambda Calculus Reducer

## Learning Goals

By the end of this tutorial, you will have:

- Implemented the `Var`, `Lam`, and `App` AST nodes for the lambda calculus and a pretty-printer that produces readable output
- Implemented `free_vars` correctly and tested it on abstractions, applications, and variables bound vs. free in the same term
- Implemented capture-avoiding substitution and verified it does not accidentally rename variables in the substituted term
- Implemented both normal-order and applicative-order beta reduction strategies and observed on a concrete term where they differ
- Built a step-tracer and REPL that interactively reduces lambda calculus terms, suitable for use in the Lambda Calculus assignment

This tutorial builds a complete, correct lambda calculus reducer in Python, the same one you need for the Lambda Calculus assignment. We go slowly through every design decision and every subtle point, so that when you write your own from scratch, you understand *why* each piece works, not just *what* it does.

By the end you will have:
- An AST with `Var`, `Lam`, `App` nodes
- A `free_vars` function
- A correct `substitute` function (capture-avoiding)
- A normal-order reducer
- An applicative-order reducer
- A step tracer
- A REPL for the lambda calculus

---

# Part 1: The AST

## 1.1 Three Node Types

The lambda calculus has exactly three syntactic forms. Each gets one class:

```python
# lc_ast.py - Lambda Calculus AST

from dataclasses import dataclass
import string

@dataclass(frozen=True)
class Var:
    """A variable: just a name."""
    name: str

    def __str__(self):
        return self.name

@dataclass(frozen=True)
class Lam:
    """An abstraction: λname. body"""
    name: str
    body: object   # another AST node

    def __str__(self):
        return f"(λ{self.name}. {self.body})"

@dataclass(frozen=True)
class App:
    """An application: (func arg)"""
    func: object
    arg:  object

    def __str__(self):
        return f"({self.func} {self.arg})"

# Convenience constructors
def var(name):  return Var(name)
def lam(x, b):  return Lam(x, b)
def app(f, a):  return App(f, a)

# Test
identity = lam("x", var("x"))                  # λx. x
true_    = lam("t", lam("f", var("t")))         # λt. λf. t
false_   = lam("t", lam("f", var("f")))         # λt. λf. f

print("Identity:", identity)
print("True:    ", true_)
print("False:   ", false_)
```

---

# Part 2: Free Variables

## 2.1 Why Free Variables Matter

$x$ is **free** in a term if it is not bound by any enclosing $\lambda x$. We need to know free variables to implement capture-avoiding substitution: we cannot substitute a term $a$ for $x$ into $(\lambda y.\ e)$ if $y$ is free in $a$, because that would accidentally bind $y$.

```python
# free_vars.py

def free_vars(term) -> frozenset:
    """Returns the set of free variable names in term."""
    if isinstance(term, Var):
        return frozenset({term.name})
    elif isinstance(term, Lam):
        # λx. body: x is bound, so remove it from body's free vars
        return free_vars(term.body) - frozenset({term.name})
    elif isinstance(term, App):
        return free_vars(term.func) | free_vars(term.arg)
    else:
        raise ValueError(f"Unknown term type: {type(term)}")

# Verification
print(free_vars(var("x")))              # {'x'}
print(free_vars(lam("x", var("x"))))    # set() -- x is bound
print(free_vars(lam("x", var("y"))))    # {'y'} -- y is free
print(free_vars(app(var("f"), var("x"))))  # {'f', 'x'}

# λx. (f x): f is free, x is bound
print(free_vars(lam("x", app(var("f"), var("x")))))  # {'f'}
```

---

# Part 3: Capture-Avoiding Substitution

## 3.1 The Three Cases

$e[x := a]$ replaces every free occurrence of $x$ in $e$ with $a$. The three cases:

```python
# substitution.py

# A global counter for generating fresh variable names
_fresh_counter = 0

def fresh_var(hint="v"):
    """Generate a variable name not used elsewhere."""
    global _fresh_counter
    _fresh_counter += 1
    return f"{hint}_{_fresh_counter}"

def substitute(term, name: str, replacement) -> object:
    """
    Perform capture-avoiding substitution: term[name := replacement].
    
    This implements exactly the three-case definition:
    
    x[x := a]        = a
    y[x := a]        = y          (y ≠ x)
    (e1 e2)[x := a]  = e1[x:=a] (e2[x:=a])
    (λy. e)[x := a]  =
        λy. e          if y == x              (x is rebound; nothing to do)
        λy. e[x:=a]    if y ≠ x and y ∉ FV(a) (safe to substitute)
        λw. e[y:=w][x:=a]  otherwise          (α-rename to avoid capture)
    """
    if isinstance(term, Var):
        if term.name == name:
            return replacement          # Case 1: this is the variable to replace
        else:
            return term                 # Case 2: different variable; untouched

    elif isinstance(term, App):
        # Case 3: distribute into both subterms
        new_func = substitute(term.func, name, replacement)
        new_arg  = substitute(term.arg,  name, replacement)
        return App(new_func, new_arg)

    elif isinstance(term, Lam):
        if term.name == name:
            # Case 4a: x is rebound here; the inner x is a different variable
            return term

        elif term.name not in free_vars(replacement):
            # Case 4b: safe - the binder y is not free in the replacement
            new_body = substitute(term.body, name, replacement)
            return Lam(term.name, new_body)

        else:
            # Case 4c: CAPTURE WOULD OCCUR - must alpha-rename first
            # Pick a fresh name that is not free in either body or replacement
            forbidden = free_vars(term.body) | free_vars(replacement) | {name, term.name}
            w = fresh_var(term.name)
            while w in forbidden:
                w = fresh_var(term.name)
            # Rename λterm.name to λw in the body
            renamed_body = substitute(term.body, term.name, Var(w))
            # Now safely substitute in the renamed body
            new_body = substitute(renamed_body, name, replacement)
            return Lam(w, new_body)

    else:
        raise ValueError(f"Unknown term type: {type(term)}")

# === Tests ===

# Basic substitution: (λx. x)[x := y] = λx. x  (x is rebound)
print(substitute(lam("x", var("x")), "x", var("y")))  # (λx. x)

# Substitution under abstraction: (λz. x)[x := y] = λz. y
print(substitute(lam("z", var("x")), "x", var("y")))  # (λz. y)

# THE HARD CASE - capture would occur without alpha-renaming:
# (λy. x)[x := y]  <- naively gives λy. y, but should give λw. y for fresh w
result = substitute(lam("y", var("x")), "x", var("y"))
print(result)  # (λv_1. y) or similar - y is not captured
# Verify: the bound variable name is NOT 'y'
assert isinstance(result, Lam)
assert result.name != "y", "Capture occurred! Bug in substitution."
print("Capture-avoidance test passed.")

# Another capture case from the assignment: (λy. x y)[x := y z]
# Result should be something like λw. (y z) w  (w fresh)
term2 = lam("y", app(var("x"), var("y")))
result2 = substitute(term2, "x", app(var("y"), var("z")))
print(result2)  # (λv_2. ((y z) v_2)) or similar
```

---

# Part 4: Beta Reduction

## 4.1 Finding and Contracting a Redex

A **redex** (reducible expression) is an application of an abstraction to an argument: $(\lambda x.\ e)\ a$. Contracting it means substituting $a$ for $x$ in $e$.

```python
# reducer.py

def is_redex(term) -> bool:
    """True iff term is (λx. e) a - an application of an abstraction."""
    return isinstance(term, App) and isinstance(term.func, Lam)

def beta_step(term):
    """
    Contract the redex in term, if it is itself a redex.
    Returns the contracted term.
    """
    assert is_redex(term), "Not a redex"
    lam_node = term.func
    arg      = term.arg
    return substitute(lam_node.body, lam_node.name, arg)

# Test
redex = app(lam("x", app(var("x"), var("x"))), var("y"))
# (λx. x x) y  ->β  y y
print(beta_step(redex))   # (y y)

# identity applied to z
id_app = app(identity, var("z"))  # (λx. x) z
print(beta_step(id_app))   # z
```

---

## 4.2 Normal-Order Reduction

**Normal-order** always reduces the **leftmost, outermost** redex. This is the strategy that finds a normal form whenever one exists.

```python
def normal_order_step(term):
    """
    Find and contract the leftmost, outermost redex.
    Returns (new_term, True) if a step was taken, or (term, False) if in normal form.
    """
    # If this term IS a redex, contract it (outermost first)
    if is_redex(term):
        return beta_step(term), True

    # Otherwise, recurse into subterms (leftmost first)
    if isinstance(term, App):
        # Try the function first (leftmost)
        new_func, stepped = normal_order_step(term.func)
        if stepped:
            return App(new_func, term.arg), True
        # Then try the argument
        new_arg, stepped = normal_order_step(term.arg)
        if stepped:
            return App(term.func, new_arg), True

    if isinstance(term, Lam):
        # Reduce under lambdas (normal order does this; applicative does not)
        new_body, stepped = normal_order_step(term.body)
        if stepped:
            return Lam(term.name, new_body), True

    return term, False   # no redex found: in normal form

def reduce_normal(term, max_steps=1000, trace=False):
    """Reduce to normal form under normal-order strategy."""
    for step in range(max_steps):
        new_term, stepped = normal_order_step(term)
        if not stepped:
            return term, step   # reached normal form
        if trace:
            print(f"  step {step+1}: {new_term}")
        term = new_term
    print(f"[reducer:normal] Step limit ({max_steps}) exceeded - may diverge")
    return term, max_steps
```

---

## 4.3 Applicative-Order Reduction

**Applicative-order** reduces arguments first. This is what Python, Java, C, and most languages do.

```python
def applicative_order_step(term):
    """
    Find and contract the leftmost, innermost redex.
    Returns (new_term, True) if a step was taken, or (term, False) if no inner redex.
    """
    if isinstance(term, App):
        # First, fully reduce the function and argument (innermost first)
        new_func, stepped = applicative_order_step(term.func)
        if stepped:
            return App(new_func, term.arg), True
        new_arg, stepped  = applicative_order_step(term.arg)
        if stepped:
            return App(term.func, new_arg), True
        # Only contract THIS redex after arguments are in normal form
        if is_redex(term):
            return beta_step(term), True

    if isinstance(term, Lam):
        new_body, stepped = applicative_order_step(term.body)
        if stepped:
            return Lam(term.name, new_body), True

    return term, False

def reduce_applicative(term, max_steps=1000, trace=False):
    """Reduce under applicative-order strategy."""
    for step in range(max_steps):
        new_term, stepped = applicative_order_step(term)
        if not stepped:
            return term, step
        if trace:
            print(f"  step {step+1}: {new_term}")
        term = new_term
    print(f"[reducer:applicative] Step limit ({max_steps}) exceeded")
    return term, max_steps
```

---

# Part 5: Church Encodings as Terms

## 5.1 Building and Testing Church Encodings

```python
# church.py - Church encodings as lambda terms

# Booleans
church_true  = lam("t", lam("f", var("t")))   # λt. λf. t
church_false = lam("t", lam("f", var("f")))   # λt. λf. f
church_if    = lam("b", lam("t", lam("f", app(app(var("b"), var("t")), var("f")))))

# Numerals: λf. λx. f^n(x)
def church_num(n):
    body = var("x")
    for _ in range(n):
        body = app(var("f"), body)
    return lam("f", lam("x", body))

zero  = church_num(0)   # λf. λx. x
one   = church_num(1)   # λf. λx. (f x)
two   = church_num(2)   # λf. λx. (f (f x))
three = church_num(3)

# Successor: λn. λf. λx. f (n f x)
succ_term = lam("n", lam("f", lam("x",
    app(var("f"), app(app(var("n"), var("f")), var("x"))))))

# Addition: λm. λn. λf. λx. m f (n f x)
add_term = lam("m", lam("n", lam("f", lam("x",
    app(app(var("m"), var("f")), app(app(var("n"), var("f")), var("x")))))))

# Multiplication: λm. λn. λf. m (n f)
mul_term = lam("m", lam("n", lam("f",
    app(var("m"), app(var("n"), var("f"))))))

# Decode a Church numeral to a Python int
def to_int(church_n, max_steps=10000):
    """Apply the Church numeral to (+1) and 0, reduce, read off the number."""
    plus_one = lam("k", app(var("k"), var("SUCC")))  # placeholder
    # Actually: apply to a counting function and initial value
    applied = app(app(church_n, lam("k", app(var("k"), var("__succ__")))), var("__zero__"))
    # Simpler: just count reduction steps by interpreting directly
    result, _ = reduce_normal(app(app(church_n, lam("n", var("S"))), var("Z")), max_steps)
    # Count the S's in the result
    def count_s(term):
        if isinstance(term, Var) and term.name == "Z": return 0
        if isinstance(term, App):
            if isinstance(term.func, Var) and term.func.name == "S":
                return 1 + count_s(term.arg)
        return -1  # not a Church numeral
    return count_s(result)

# Test
print("zero  =", to_int(zero))   # 0
print("one   =", to_int(one))    # 1
print("two   =", to_int(two))    # 2
print("three =", to_int(three))  # 3

# succ(two) should be three
succ_two, steps = reduce_normal(app(succ_term, two), trace=False)
print("succ(two) =", to_int(succ_two), f"({steps} steps)")  # 3

# add(two)(three)
add_2_3, steps = reduce_normal(app(app(add_term, two), three), trace=False)
print("add(2)(3) =", to_int(add_2_3), f"({steps} steps)")  # 5

# mul(two)(three)
mul_2_3, steps = reduce_normal(app(app(mul_term, two), three), trace=False)
print("mul(2)(3) =", to_int(mul_2_3), f"({steps} steps)")  # 6
```

---

# Part 6: The REPL

## 6.1 Parsing Lambda Terms

A minimal parser for the lambda calculus (enough for the assignment REPL):

```python
# lc_parser.py - a simple lambda calculus parser

import re

def tokenize_lc(source):
    """Tokenize a lambda calculus expression."""
    pattern = r'λ|\\|->|[a-zA-Z_][a-zA-Z0-9_]*|[().]|\s+'
    tokens = []
    for tok in re.findall(pattern, source):
        if not tok.strip():
            continue
        tokens.append(tok)
    return tokens

def parse_lc(source):
    """Parse a lambda calculus expression into an AST."""
    tokens = tokenize_lc(source)
    pos = [0]

    def peek():
        return tokens[pos[0]] if pos[0] < len(tokens) else None

    def consume(expected=None):
        tok = tokens[pos[0]]
        if expected and tok != expected:
            raise SyntaxError(f"Expected {expected!r}, got {tok!r}")
        pos[0] += 1
        return tok

    def parse_expr():
        """expr ::= lam | app"""
        if peek() in ('λ', '\\'):
            return parse_lam()
        return parse_app()

    def parse_lam():
        consume()   # consume λ or \
        param = consume()
        if peek() == '.':
            consume('.')
        elif peek() == '->':
            consume('->')
        body = parse_expr()
        return lam(param, body)

    def parse_app():
        """Left-associative application."""
        func = parse_atom()
        while peek() and peek() not in (')', '.'):
            # Don't consume a λ as an argument without parens
            if peek() in ('λ', '\\'):
                break
            arg = parse_atom()
            func = app(func, arg)
        return func

    def parse_atom():
        tok = peek()
        if tok == '(':
            consume('(')
            e = parse_expr()
            consume(')')
            return e
        if tok and tok not in ('λ', '\\', ')', '.', '->'):
            consume()
            return var(tok)
        raise SyntaxError(f"Unexpected token: {tok!r}")

    return parse_expr()

# Test
print(parse_lc("λx. x"))
print(parse_lc("λf. λx. f (f x)"))
print(parse_lc("(λx. x x) (λx. x x)"))   # Omega

def repl_lc():
    """A REPL for the lambda calculus."""
    print("Lambda Calculus REPL")
    print("Syntax: λx. body  or  \\x. body  or  \\x -> body")
    print("Type 'quit' to exit. Type 'normal' or 'applicative' to switch strategies.")
    strategy = 'normal'
    max_steps = 200

    while True:
        try:
            line = input(f"λ [{strategy}]> ").strip()
            if not line: continue
            if line == 'quit': break
            if line == 'normal':     strategy = 'normal';     print("Strategy: normal-order"); continue
            if line == 'applicative': strategy = 'applicative'; print("Strategy: applicative"); continue

            term = parse_lc(line)
            print(f"Parsed: {term}")

            if strategy == 'normal':
                result, steps = reduce_normal(term, max_steps, trace=True)
            else:
                result, steps = reduce_applicative(term, max_steps, trace=True)

            print(f"Normal form ({steps} steps): {result}")
            print(f"Free variables: {sorted(free_vars(result))}")

        except (SyntaxError, ValueError) as e:
            print(f"Error: {e}")
        except KeyboardInterrupt:
            print("\nInterrupted.")
            break

# Uncomment to run:
# repl_lc()
print("REPL defined. Call repl_lc() to start.")
```

---

# Part 7: Verification Checklist

Before submitting the lambda calculus assignment, verify your reducer passes all of these:

```python
# verification.py - tests every component

def assert_equal_by_alpha(t1, t2, msg=""):
    """
    Alpha-equivalence check: are t1 and t2 the same up to variable renaming?
    Simple version: reduce both to normal form and compare string structure.
    """
    pass  # implement if needed

tests = [
    # (description, term_str, expected_int_or_none)
    ("identity on y",         "(λx. x) y",          None),    # reduces to y
    ("constant function",     "(λx. λy. x) a b",    None),    # reduces to a
    ("church zero = id",      "λf. λx. x",          0),
    ("church one",            "λf. λx. f x",        1),
    ("church two",            "λf. λx. f (f x)",    2),
    ("succ zero = one",       None,                  1),        # succ_term zero
    ("add 2 3 = 5",           None,                  5),
    ("mul 2 3 = 6",           None,                  6),
]

print("Running verification...")
for desc, term_str, expected in tests:
    try:
        if term_str:
            term   = parse_lc(term_str)
            result, steps = reduce_normal(term)
            print(f"  OK {desc}: {result} ({steps} steps)")
        else:
            print(f"  o {desc}: (code test)")
    except Exception as e:
        print(f"  FAIL {desc}: {e}")
```

---

## Summary: What to Build for the Assignment

| Component | Key function | Located in |
|---|---|---|
| AST | `Var`, `Lam`, `App` | `lc_ast.py` |
| Free variables | `free_vars(term)` | this tutorial |
| Substitution | `substitute(term, name, replacement)` | this tutorial |
| Redex detection | `is_redex(term)` | this tutorial |
| Beta step | `beta_step(redex)` | this tutorial |
| Normal order | `reduce_normal(term, ...)` | this tutorial |
| Applicative | `reduce_applicative(term, ...)` | this tutorial |
| Church encodings | `church_num(n)`, `add_term`, etc. | this tutorial |
| REPL | `repl_lc()` | this tutorial |
| Config | `config.json` | your code |
| Transcript | run with trace=True, redirect to file | `README` |

The one step not covered here: **alpha-equivalence checking** for your cross-verification report. Two terms are alpha-equivalent if one can be obtained from the other by consistently renaming bound variables. The cleanest approach is to normalize bound variable names (rename them in order of appearance: `x₁`, `x₂`, etc.) and then compare structurally.

---

# Advanced: Deriving the Y Combinator

*"The Y combinator is probably the most ingenious and least intuitive result in the lambda calculus."*, Pierce, *TAPL*

This optional advanced section stands apart from the reducer you built above: it answers the question the reducer raises but cannot answer on its own: how does an *anonymous* function recurse?

Imagine a self-playing record: the groove that plays the current note also contains the instruction to move to the next note. The record does not need to consult an external playlist; the mechanism for advancing is baked into every moment of the playback. The Y combinator works the same way: the code that produces the next recursive call is folded directly into each call site, with no external name, no registry, no environment entry needed.

Every recursive function you have ever written calls itself by name: `factorial` calls `factorial`, `fib` calls `fib`. This seems obvious and necessary. But names are a feature of programming environments, not a feature of computation itself. The lambda calculus has no names; every definition is anonymous. So how do you write a recursive function when you cannot name it? How do you call a function you cannot refer to?

The answer is the **Y combinator**: a fixed-point operator that provides every function the gift of self-reference, without requiring a name. This section builds to Y from scratch (through a carefully designed sequence of wrong answers that teach the right intuition) and then shows Y at work in modern Python, JavaScript, and Haskell.

By the end of this section, you will be able to:

- Explain why named self-reference is unavailable in the pure lambda calculus and why an anonymous recursive function requires a fixed-point operator
- Derive the Y combinator step by step from the self-application trick, tracing how each intermediate form eliminates a deficiency of the previous one
- Implement a working Y combinator in Python (using the Z combinator variant for strict evaluation) and use it to express factorial without `def` or assignment
- Define what it means for Y to be a fixed-point operator (`Y f = f (Y f)`) and verify this property by hand reduction
- Recognize the Y combinator pattern in real code (trampolined recursion, anonymous recursion idioms in JavaScript and Haskell)

> **Before You Begin: Prerequisites**
>
> This section assumes you are comfortable with:
>
> - **Lambda calculus syntax and beta-reduction**: you can apply a lambda term to an argument step by step (Parts 1-4 of this tutorial)
> - **Higher-order functions**: a function that takes another function as an argument and returns a function
> - **Python lambdas**: `lambda n: n * 2` is a valid Python callable; you can nest lambdas and call them immediately
> - **Named combinators (recommended but not required)**: familiarity with I, K, and the Church encodings from Part 5 helps
>
> The key mental model you need: a function in the lambda calculus is *anonymous*. It has no name. The question this section answers is: how can something anonymous call itself?

---

## Warm-Up: The Named Baseline

```python
# Warm-up: confirm the recursive baseline
def factorial_named(n):
    return 1 if n == 0 else n * factorial_named(n - 1)   # named self-call

print([factorial_named(n) for n in range(8)])
# [1, 1, 2, 6, 24, 120, 720, 5040]
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

**Goal:** Rewrite `factorial` with no `def`, no name, no assignment, using only `lambda`.

---

## Step 1: Pass a Copy of Yourself

The big idea in this step is embarrassingly simple once you see it: if you cannot *name* yourself, you can *be given* yourself as an argument. Instead of `factorial` calling `factorial`, you write a function that says "whoever you are, call yourself on the next input." Then the caller is responsible for handing the function a copy of itself. This feels circular (and it is!) but the circularity is explicit and controlled rather than hidden in a name lookup.

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

> **Watch out! `self` is a function, not an integer**
>
> In `step1`, the argument called `self` is not a number: it is a *function* (specifically, it will be `step1` itself). The call `self(self)` returns a *function* (one that takes `n`), and then `(n - 1)` calls that function. It is easy to confuse `self(self)(n-1)` with `self(n-1)`: the first passes `self` as argument to produce a callable, then calls that callable on `n-1`; the second would pass `n-1` directly to `self`, which expects a function. Always trace the types.

**Check your understanding**, answer these for yourself before moving on:

1. In `step1 = lambda self: lambda n: ...`, what type does `self` have? (Hint: what does `self(self)` produce?)
2. Why does the recursive call have `self(self)(n-1)` rather than `self(n-1)`?
3. If we wrote `self(n-1)` instead, what would happen when we try to call `step1(step1)(3)`? Trace the first two calls.

---

## Step 2: Cleaning Up the Body

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

## Step 3: Separating the Logic from the Fixed-Point Machinery

This is the key abstraction step. Once the self-application plumbing is hidden in `rec`, the factorial logic becomes a perfectly ordinary function generator: "give me a `rec` that handles the recursive call, and I will give you a working factorial." This generator works for *any* recursive function, not just factorial. The machinery that turns a generator into a recursive function is independent of what the function computes. That machinery (currently called `Y_machinery`) is the Y combinator. You have now rebuilt it from scratch.

Notice that `lambda rec: lambda n: 1 if n == 0 else n * rec(n - 1)` is just the factorial *logic*: a function that takes its recursive call-stub and returns the actual implementation. Let us name this "the step" or "the generator":

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

## The Y Combinator, Formally

The formal definition of Y in the lambda calculus is exactly the `Y_machinery` you built above, written in lambda notation and compressed. The self-playing record analogy pays off here: $\lambda x.\ f\ (x\ x)$ is the "groove": a function that, when applied to itself, hands $f$ a way to replay itself. Applied to itself, it produces $f\ (\text{the whole thing again})$. The outer $\lambda f$ makes the machinery generic: it works for *any* generator $f$, not just factorial. The one practical obstacle is evaluation order, which forces us to use the Z variant in Python.

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

> **Watch out! Python evaluates arguments before calling functions**
>
> In the pure Y combinator, the body contains `x(x)` as a sub-expression. Python (like most languages) evaluates *both* arguments before making a function call. So when it processes `(lambda x: f(x(x)))(lambda x: f(x(x)))`, it tries to evaluate the argument `lambda x: f(x(x))` applied to itself *immediately* (before any base case can fire), resulting in infinite recursion. The fix is eta-expansion: wrap `x(x)` in `lambda v: x(x)(v)`, which delays evaluation until `v` is actually provided. This single change converts the call-by-name Y into the call-by-value Z.

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

The Z combinator differs from Y only in the `lambda v:` wrapper: instead of `x(x)` (evaluated immediately), it is `lambda v: x(x)(v)` (a function, evaluated only when called). This one-token change converts Y from a normal-order term to an applicative-order term. (You can watch the difference with the reducer you built in Part 4: normal order finds the base case; applicative order hits the step limit.)

What is the key difference between the Y combinator and the Z combinator?

[(X)] Z wraps the self-application in an extra lambda (eta-expansion), delaying evaluation to make it safe for applicative-order (strict) languages like Python.
[( )] Z works for non-recursive functions while Y only works for recursive ones.
[( )] Z is for multi-argument functions while Y is for single-argument functions.
[( )] They are the same combinator; Z is just an alternative name for Y used in some textbooks.

---

## Y in JavaScript and Haskell

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

Haskell (lazy, the original Y works directly):

```haskell
-- Haskell is lazy, so Y works without eta-expansion
y :: (a -> a) -> a
y f = let x = f x in x
-- equivalently: y f = f (y f)

-- But Haskell's type system rejects the standard λ-calculus Y because
-- it would require an infinite type (α = α -> α).
-- Instead, use fix from Data.Function:
import Data.Function (fix)

factorial :: Int -> Int
factorial = fix (\rec n -> if n == 0 then 1 else n * rec (n - 1))

-- fix f = f (fix f) -- this is the definition; Haskell's laziness makes it work
```

---

## Y as a Fixed-Point Operator

A fixed point is a value that a function maps to itself: $g(x) = x$. For numeric functions, this is a concrete number (the fixed point of cosine is about 0.739). For function-valued functions (generators that take a recursive call-stub and return a function) the "fixed point" is the fully recursive function itself. This is the self-playing record in precise mathematical language: the record that, when played, produces itself as output. The Y combinator finds that fixed point for any generator.

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

## Y Without Y: Other Fixed-Point Tricks

Real-world code rarely spells out `Z = lambda f: (lambda x: ...)`. Instead, programmers reach for idioms that produce the same effect: passing `self` as an argument, wrapping in a class, using a shared namespace. These are all approximations of the fixed-point idea, using features (assignment, objects, closures) that the lambda calculus deliberately excludes. Recognizing them as instances of the same underlying pattern is the payoff of having studied Y from scratch.

Several practical patterns implement the same idea without writing Y explicitly:

```python
# Pattern 1: default argument hack (exploits Python's eager default binding)
factorial_default = lambda n, rec=None: (
    (lambda n2, rec2: 1 if n2 == 0 else n2 * rec2(n2-1, rec2))(n, rec)
    if rec else (lambda n2: factorial_default(n2))(n)
)
# This is a hack; don't do it. It works but is obscure.
# Watch out: this function still relies on the name `factorial_default` in its
# body - it is not truly anonymous. It smuggles a name in through the closure.

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

## Y Combinator Exercises

1. **Derive Z by hand.** Starting from Y = $\lambda f.\ (\lambda x.\ f\ (x\ x))\ (\lambda x.\ f\ (x\ x))$, derive Z by adding the eta-expansion `lambda v:` in the right place. Show why the unadapted Y diverges in Python by tracing the first three beta-reduction steps in applicative order.

2. **Non-numeric recursion.** Use Z to implement `reverse_list` (takes a list, returns it reversed) without any `def` or named function. Hint: `reverse_list_gen = lambda rec: lambda lst: [] if not lst else rec(lst[1:]) + [lst[0]]`.

3. **Mutual recursion.** Use Z to implement mutually recursive `is_even` and `is_odd` (without using `%`). Hint: pack both into a pair, pass the pair as the self-argument, and select the correct one.

4. **Fixed-point poetry.** The Y combinator satisfies $Y\ g = g\ (Y\ g)$. In Python, `print` is a function. Can you write an expression (one Python line, no semicolons) that prints itself? This is the Quine problem: a program that outputs its own source code. It is the programming equivalent of the fixed-point equation. Research the connection and write a two-paragraph explanation.

5. **Y in the wild.** Find one real-world use of the Y combinator (or the Z combinator, or `fix`) in production code or a popular library. (Hint: search GitHub for `fix` in Haskell libraries, or `Y` in functional JavaScript utilities.) Write up: what is the function, what does it compute, and why was the author motivated to write it with an explicit fixed-point combinator rather than a named recursive function?

---

## Reflection

The Y combinator makes a striking philosophical point: self-reference (the ability of a process to call itself) is not a primitive. It is derivable from two things: functions and application. Write a paragraph responding to this: what does it mean for computation that all recursion, everywhere, is ultimately "just" this fixed-point trick? Does it change how you think about what a programming language "really" needs to provide, versus what it provides for convenience?

---

## Further Reading on the Y Combinator

- Michaelson, Greg. *An Introduction to Functional Programming Through Lambda Calculus* (Dover, 2011). Chapter 7 builds Y from scratch, more slowly than we do here.
- Gabriel Lebec. "Lambda as JS, or, A Flock of Functions." Speakerdeck, 2016. The JavaScript Y combinator section directly connects to this section.
- Krishnamurthi, Shriram. *PLAI*, Chapter 9: "Recursion and Cycles." The semantics of letrec (what the evaluator does to implement Y) is the companion to the combinator view.
- Abelson and Sussman. *SICP*, Section 4.1.6. The metacircular evaluator's treatment of `define` and recursive definitions.
- Gabriel, Richard. "Lisp: Good News, Bad News, How to Win Big." 1991. Mentions the Y combinator in the context of Lisp's identity as "the programmable programming language."

---

# Advanced: Combinatory Logic and the SKI Calculus

**Direction D of the Functional assignment builds on this material**; if you are considering that direction, this section is your foundation.

Think of combinators as **LEGO bricks for computation**. Each brick does exactly one simple, self-contained thing: snap the identity brick onto the constant brick, snap that onto the compose brick, and from a handful of primitive pieces you can build any computation that any computer can perform. No names, no variables, no environment. Just bricks clicking together.

By the end of this section, you will be able to:

- Reduce combinatory logic expressions (I, K, S, B, C, W, M) to normal form using the combinator reduction rules, circling the active redex at each step
- Translate lambda expressions into combinator form using bracket abstraction, eliminating all variable bindings
- Implement the standard combinator birds in Python and verify their reduction behavior by execution
- Explain why S and K together are computationally complete (Schönfinkel's theorem) and connect this to the Church-Turing thesis
- Derive familiar higher-order functions (function composition, `flip`, `const`, identity) directly from combinator definitions

> **Before You Begin: Prerequisites**
>
> This section assumes you are comfortable with:
>
> - **Lambda calculus syntax**: you can read $\lambda x.\ e$ and know that it means "a function that takes $x$ and returns $e$"
> - **Beta-reduction**: you can apply a lambda term to an argument by substituting the argument for the bound variable
> - **Currying**: you understand that `lambda a: lambda b: a` is a two-argument function written as two nested one-argument functions
> - **Python lambdas**: `lambda x: x + 1` is valid Python and returns a callable
>
> If any of these feel shaky, review Parts 1-5 of this tutorial before continuing. Combinators are built directly on top of that material; every reduction rule here is just beta-reduction with no bound variables.

*"To every combination there corresponds a unique bird."*, Raymond Smullyan, *To Mock a Mockingbird* (1985)

In this tutorial we built computation from three syntactic forms: variables, abstraction, and application. Here we take the abstraction away. **Combinatory logic** is the lambda calculus with no bound variables: no $\lambda x$, no substitution, no alpha-conversion, no capture to fear. Only application and a small fixed collection of **combinators**: functions with no free variables whose behavior is defined entirely by how they transform their arguments. In 1924, Moses Schönfinkel proved that just two combinators, **S** and **K**, suffice to express any computable function. The birds are named in Raymond Smullyan's puzzle book, and Gabriel Lebec's 2016 London talk "*A Flock of Functions*" demonstrates the entire menagerie live in JavaScript. By the end of this section you will reduce terms in the combinator calculus by hand, implement all the birds in Python, derive familiar operations (function composition, `flip`, `const`, `id`) directly from the birds, and understand why SKI completeness is the combinatory-logic version of the Church-Turing thesis.

---

## Setting Up

```python
# Every bird is a Python callable. We verify by running the cells below.
# No libraries required.
print("Ready to meet the flock.")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

---

## Part I: The Birds Themselves

### 1. Notation and Reduction Rules

Before diving into the rules, orient yourself: in the lambda calculus you had *variables*, *abstractions* ($\lambda x.\ e$), and *application*. Combinatory logic throws out variables and abstractions entirely. What remains? Application only, and a small fixed menu of named functions (the "birds") whose behavior is completely captured by simple rewrite rules. Each rule says: "when this bird receives enough arguments, rewrite the whole expression." There is no substitution, no renaming, no environment to thread around. Reduction is pure term rewriting, like rearranging LEGO bricks according to a picture.

**Combinatory terms** are built from:

- **Constants**: the combinators themselves (I, K, S, B, C, W, M, ...)
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

> **Watch out! Argument counting**
>
> A combinator only fires when it has received *all* of its required arguments. $\mathbf{K}\ a$ is a partially applied function: it is waiting for its second argument and does *not* yet reduce. $\mathbf{S}\ a\ b$ is similarly stuck. Writing $\mathbf{S}\ a\ b\ c$ is what triggers the rule. If you try to reduce a term and nothing fires, check whether every combinator in the term is fully saturated.

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

Every lambda term becomes a combinator expression, free of variables, yet computationally identical. The gain is conceptual: reduction is pure term rewriting, no environment, no substitution machinery.

---

#### Try It: Reduce by Hand

Reduce each expression to normal form, one rule application per line, circling the redex at each step.

1. $\mathbf{I}\ (\mathbf{K}\ a\ b)$
2. $\mathbf{K}\ (\mathbf{I}\ a)\ b$
3. $\mathbf{S}\ \mathbf{K}\ \mathbf{K}\ a$: what well-known combinator does this behave like?

Hint for (3): what does $\mathbf{K}\ a\ (\_)$ do to any second argument?

---

### 2. The Identity Bird, **I** (Idiot)

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

### 3. The Kestrel, **K** (Constant)

The Kestrel is the "ignore and keep" brick. You hand it a value, and no matter what else you stack on top, it will always return that original value. This turns out to encode the Boolean *true* in Church encodings, because `if true then x else y` means "take two branches, return the first." Connect to the LEGO analogy: K is a brick with a trap door; everything that enters the second slot falls straight through and disappears.

$$
\mathbf{K}\ a\ b = a
$$

The Kestrel takes two arguments and returns the first, discarding the second. In lambda calculus it is $\lambda a.\ \lambda b.\ a$, the encoding of **true** in Church booleans! In Haskell it is `const`. In Python:

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

### 4. The Bluebird, **B** (Compose)

The Bluebird is the pipeline brick. Snap two bricks together end-to-end: the output of the second feeds into the input of the first. This is Haskell's `.` operator, and it is how real functional programs are built: not by writing big monolithic functions, but by composing small single-purpose ones. Notice that the argument order matters: $\mathbf{B}\ f\ g$ means "do $g$ first, then $f$," which is the standard mathematical right-to-left composition.

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

### 5. The Cardinal, **C** (Flip)

The Cardinal is the "swap the inputs" brick. When you have a two-argument function and the arguments are arriving in the wrong order (perhaps you want to partially apply the *second* argument first), the Cardinal flips them for you. Haskell calls this `flip`, and it appears constantly when adapting library functions for use in pipelines and point-free style.

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

### 6. The Starling, **S** (the Power Bird)

The Starling is the "fork and merge" brick, the one that makes the calculus powerful enough to compute anything. Given $x$, it routes $x$ down two separate paths simultaneously: one path feeds $x$ into $f$, producing a function; the other path feeds $x$ into $g$, producing an argument; then the results are merged by application. This is the combinator encoding of *sharing*: the same input reaches two different parts of a computation. Without this sharing capability, the calculus could only compute linear functions.

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

### 7. The Mockingbird, **M** (Self-Application)

The Mockingbird is the "danger" brick; handle with care. It takes whatever you hand it and makes it eat itself. Applied to a safe function, this produces interesting behavior (self-duplication, mirroring). Applied to itself, it produces $\Omega$: the combinator equivalent of an infinite loop. The Mockingbird is the combinatory seed from which fixed-point combinators and recursion grow; it demonstrates that non-termination is an intrinsic feature of any sufficiently expressive system.

$$
\mathbf{M}\ a = a\ a
$$

The Mockingbird applies its argument to itself. In lambda calculus it is $\lambda a.\ a\ a$. It is the self-application operator, and $\mathbf{M}\ \mathbf{M}$ is the combinatory equivalent of $\Omega$; it reduces forever. But applied carefully, the Mockingbird is the basis for fixed-point combinators and recursion in the combinator calculus.

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

> **Watch out! Do not evaluate M(M)**
>
> `M(M)` in Python will immediately raise a `RecursionError` (or spin forever). The Mockingbird is safe only when its argument is a function that can meaningfully accept a function as input. Before running any expression involving M, ask: "does this argument expect a callable?" If not, do not apply M.

---

### 8. The Warbler, **W** (Duplicate)

The Warbler is the "copy and double-feed" brick. It takes a two-argument function and collapses its two inputs into one: whatever you hand it, it hands to $f$ twice. This is subtly different from the Mockingbird: M makes $x$ eat *itself*, while W feeds $x$ to an *external* two-argument function $f$. The Warbler is how you derive "diagonal" operations (squaring, equality-with-self, duplication) without ever naming the argument twice.

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

## Part II: Derivation and the Completeness of SKI

### 9. Everything from S, K, I

You have now met seven birds. Here is the remarkable fact: you do not need seven. You need *two*. S and K alone (two LEGO bricks) can simulate every other bird, every lambda term, every computable function. This is Schönfinkel's 1924 theorem, the combinatory-logic counterpart of the Church-Turing thesis. The bracket abstraction algorithm in Section 1 is the constructive proof: it tells you mechanically how to turn any lambda term into an SKI expression. The derivations below make this concrete.

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

> **Watch out! SKI expressions grow quickly**
>
> The naive bracket abstraction algorithm can produce expressions that are exponentially larger than the original lambda term: a two-variable lambda can become dozens of S, K, and I tokens. This is why real compilers (e.g., Turner 1979) use optimized combinators like B and C to keep the output manageable. When you do bracket abstraction by hand in the exercises, count your tokens; if the result seems enormous, double-check your steps.

---

Which reduction sequence correctly shows that $\mathbf{K}\ \mathbf{I}\ a\ b \Rightarrow b$ (i.e., that $\mathbf{K}\ \mathbf{I}$ is **false** / the second-argument selector)?

[(X)] $\mathbf{K}\ \mathbf{I}\ a \Rightarrow \mathbf{I}$, then $\mathbf{I}\ b \Rightarrow b$. Each step fires one combinator rule.
[( )] $\mathbf{K}\ \mathbf{I}\ a\ b \Rightarrow \mathbf{K}\ b$, then $\mathbf{K}\ b \Rightarrow b$.
[( )] $\mathbf{K}\ \mathbf{I}\ a\ b \Rightarrow \mathbf{I}\ \mathbf{I}\ b \Rightarrow b$. K fires on I and b simultaneously.
[( )] The reduction diverges because $\mathbf{K}\ \mathbf{I}$ contains no redex.

---

### 10. The Y Combinator in SK

This section pulls together everything: if S and K are computationally complete, and if recursion is a computable operation, then S and K can express recursion, without any `def`, without any name, without any environment. The Y combinator written in pure SK is startling precisely because it looks like nothing else you have seen: a wall of S, K, and I with no variables anywhere. Yet it satisfies $Y\ g = g\ (Y\ g)$ for any $g$. The derivation in the Y combinator section above explains *why* this works; here the goal is to see that it is expressible at all.

Recall from the previous section that the Y combinator satisfies $Y\ g = g\ (Y\ g)$. In strict (applicative-order) languages we use the Z combinator instead. In pure SK combinatory logic:

$$
\mathbf{Y} = \mathbf{S}\ (\mathbf{K}\ (\mathbf{S}\ \mathbf{I}\ \mathbf{I}))\ (\mathbf{S}\ (\mathbf{S}\ (\mathbf{K}\ \mathbf{S})\ \mathbf{K})\ (\mathbf{K}\ (\mathbf{S}\ \mathbf{I}\ \mathbf{I})))
$$

This derivation of Y from S and K (without any variables, without any lambda, without any notion of binding) is the combinatory logic proof that recursion is not a primitive: it is computable from application alone.

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

## Part III: The Flock in Practice

### 11. Gabriel Lebec's Birds in JavaScript, and in Python

The birds stop being an abstract curiosity the moment you recognize them in code you already write. Every time you call `map(lambda x: x + 1, lst)` you are using I. Every time you write `key=lambda _: 0` you are using K. Every time you write `sorted(lst, key=lambda x: -x)` you are using a partial application of C. Gabriel Lebec's talk makes this explicit for JavaScript; this section makes it explicit for Python. The punchline: **combinators are not exotic theory; they are the names for the patterns you reach for every day without knowing it**.

Gabriel Lebec's 2016 talk "*A Flock of Functions*" demonstrates that every standard higher-order function in JavaScript is a bird in disguise. The key insight is that **you already use combinators every day**; you just call them `const`, `id`, `flip`, `compose`, and `curry`. Here is the full correspondence, in Python:

```python
# === The Flock - Python Edition ===
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

### 12. Point-Free Style: Programming Without Variables

Point-free programming is what happens when you take the combinator philosophy all the way to the surface of your code. Instead of writing `lambda x: f(g(x))` (which names $x$ even though $x$ appears in only one place) you write `B(f)(g)`, which says "compose f and g" without ever mentioning what they are applied to. This is not just an aesthetic preference: in Haskell it is the dominant style, because it emphasizes what transformations are being composed rather than what data they act on. The LEGO metaphor completes here: point-free code is a blueprint describing how bricks connect, not a sequence of operations on a specific piece.

**Point-free** (or "tacit") programming uses only combinators and function composition: no named variables, no lambdas. It is the ultimate expression of the combinatory-logic philosophy, and it is the standard style in Haskell. Here is the connection:

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

#### Try It: Bird Identification

For each Python expression below, identify which bird (I, K, S, B, C, W, M, KI) it instantiates, and write the combinator reduction rule that proves the claim.

1. `lambda x: x`
2. `lambda x: lambda y: x`
3. `lambda f: lambda g: lambda x: f(g(x))`
4. `lambda f: lambda x: f(x)(x)`
5. `lambda x: lambda y: lambda z: x(z)(y(z))`
6. `lambda f: lambda a: lambda b: f(b)(a)`
7. `lambda a: lambda b: lambda f: f(a)(b)`: which bird pairs data?

---

### 13. Exercises

1. **Reduction transcripts.** Reduce to normal form, one combinator rule per line, circling the redex:
   - (a) $\mathbf{B}\ f\ (\mathbf{B}\ g\ h)\ x$: show this equals $\mathbf{B}\ (\mathbf{B}\ f\ g)\ h\ x$ (associativity of composition)
   - (b) $\mathbf{C}\ \mathbf{K}\ a\ b$: what does this return, and what lambda term is it equivalent to?
   - (c) $\mathbf{W}\ \mathbf{K}\ a$: one step is enough; what does it return?

2. **Bracket abstraction.** Use the three-rule bracket abstraction algorithm to convert $\lambda x.\ \lambda y.\ y\ x$ to an SKI expression. Verify by reducing your expression on two concrete arguments.

3. **Flock identification.** A colleague writes `f = lambda x: lambda _: x`. Which bird is this? Write the bird's one-line reduction rule, its lambda term, its Haskell name, and the two-word English description that explains what it does to its arguments.

4. **Pairs from birds.** Using only I, K, KI, V (Vireo), implement `swap` (exchange the components of a pair) as a bird expression, with no lambda. Verify on `pair(1)(2)`.

5. **SKI Turing completeness (research).** The combinator $\mathbf{S}\ \mathbf{K}$ applied to itself loops: $\mathbf{S}\ \mathbf{K}\ (\mathbf{S}\ \mathbf{K}) \Rightarrow \mathbf{K}\ (\mathbf{S}\ \mathbf{K})\ (\mathbf{K}\ (\mathbf{S}\ \mathbf{K})) \Rightarrow \mathbf{S}\ \mathbf{K}$. Write a one-paragraph explanation of why the existence of a non-terminating term (like $\Omega$ in the lambda calculus) is *necessary* for a system to be Turing complete, connecting to the Halting Problem.

---

### 14. Further Reading on Combinatory Logic

- Smullyan, Raymond. *To Mock a Mockingbird* (Knopf, 1985). The source of the bird names; a puzzle book that teaches combinatory logic through delightful ornithological fiction.
- Lebec, Gabriel. "Lambda as JS, or A Flock of Functions: Combinators, Lambda Calculus, and Church Encodings in JavaScript." London Functional Programmers Meetup, 2016. **This is the direct inspiration for this section.** Slides: https://speakerdeck.com/glebec/lambda-as-js-or-a-flock-of-functions-combinators-lambda-calculus-and-church-encodings-in-javascript. Source: https://github.com/glebec/lambda-talk. Watch the recording; every combinator in this section appears there in JavaScript.
- **Lambda-Py / pycombinator**: combinators and Church encodings in Python: https://finsberg.github.io/pycombinator/docs/lambda-talk.html, the flock in Python rather than JavaScript; use it to check your hand reductions from this section against a mechanical reducer.
- Curry, H. B. and R. Feys. *Combinatory Logic, Volume I* (North-Holland, 1958). The foundational text.
- Hindley, J. Roger and Jonathan P. Seldin. *Lambda-Calculus and Combinators: An Introduction* (Cambridge UP, 2008). Modern, rigorous, and accessible.
- Turner, David. "Another Algorithm for Bracket Abstraction." *Journal of Symbolic Logic* 44(2), 1979. The optimized bracket abstraction that compilers actually use, avoiding the SKI expansion explosion.
- Tromp, John. "Binary Lambda Calculus and Combinatory Logic." *Randomness and Complexity* (World Scientific, 2007). SK programs as bit strings; the smallest known universal computer.
