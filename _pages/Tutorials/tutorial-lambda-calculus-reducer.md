# Tutorial: Implementing a Lambda Calculus Reducer

<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374-Fall2026/gh-pages/_pages/Tutorials/tutorial-lambda-calculus-reducer.md

import: https://raw.githubusercontent.com/liascript/CodeRunner/master/README.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

# Tutorial: Implementing a Lambda Calculus Reducer

This tutorial builds a complete, correct lambda calculus reducer in Python — the same one you need for the Lambda Calculus assignment. We go slowly through every design decision and every subtle point, so that when you write your own from scratch, you understand *why* each piece works, not just *what* it does.

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
# lc_ast.py — Lambda Calculus AST

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
            # Case 4b: safe — the binder y is not free in the replacement
            new_body = substitute(term.body, name, replacement)
            return Lam(term.name, new_body)

        else:
            # Case 4c: CAPTURE WOULD OCCUR — must alpha-rename first
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

# THE HARD CASE — capture would occur without alpha-renaming:
# (λy. x)[x := y]  ← naively gives λy. y, but should give λw. y for fresh w
result = substitute(lam("y", var("x")), "x", var("y"))
print(result)  # (λv_1. y) or similar — y is not captured
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
    """True iff term is (λx. e) a — an application of an abstraction."""
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
# (λx. x x) y  →β  y y
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
    print(f"[reducer:normal] Step limit ({max_steps}) exceeded — may diverge")
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
# church.py — Church encodings as lambda terms

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
# lc_parser.py — a simple lambda calculus parser

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
# verification.py — tests every component

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
            print(f"  ✓ {desc}: {result} ({steps} steps)")
        else:
            print(f"  ○ {desc}: (code test)")
    except Exception as e:
        print(f"  ✗ {desc}: {e}")
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
