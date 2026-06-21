<!--
author:   CS374 Course Staff
email:    
version:  0.0.1
language: en
narrator: US English Female
comment:  Compiler optimizations — making programs faster without changing what they mean.
import:   https://raw.githubusercontent.com/liaScript/mermaid_template/master/README.md
link:     https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.3.0/css/all.min.css
-->

# Compiler Optimizations: Making Programs Faster

## Learning Goals

By the end of this activity, you will be able to:

- Implement constant folding and dead-code elimination as AST-to-AST rewrite passes, and state the correctness condition that distinguishes valid from invalid optimizations
- Implement common subexpression elimination (CSE) by identifying redundant computations in an expression and rewriting the AST to share them
- Implement function inlining as an AST substitution pass, and explain when inlining improves and when it hurts performance
- Recognize tail calls in recursive functions, apply the tail-call optimization transformation, and explain why it enables constant-stack recursion

> **"The first 90% of the code accounts for the first 90% of the development time. The remaining 10% of the code accounts for the other 90% of the development time."** — Tom Cargill
>
> Optimizations speed up programs *without changing their meaning*. Today you will implement five core optimizations: constant folding, dead code elimination, common subexpression elimination, inlining, and tail call optimization. Each operates on the AST or IR — the same data structures you've been building all semester.

## Directions and Roles

Work in groups of 3–4. Rotate roles every 20 minutes.

- **Facilitator**: Keeps discussion on track; ensures everyone contributes.
- **Recorder**: Writes down answers and code that the group agrees on.
- **Reporter**: Presents findings to the class; explains the group's reasoning.
- **Reflector**: Monitors group process; writes the reflection at the end.

---

## Model 1 — What Makes an Optimization Valid?

An optimization is **valid** if it *preserves program semantics* — the optimized program produces the same observable results as the original for all valid inputs.

```python  liascript
# Some "optimizations" are INVALID — they change observable behavior

def f():
    print("side effect!")
    return 0

# INVALID: cannot fold f() + 0 → 0 (removes the print side effect)
x = f() + 0    # prints "side effect!" and gives x=0
# "optimized": x = 0   # WRONG — side effect gone!

# VALID: can fold pure expressions
y = 2 + 3 * 4   # evaluates to 14 at compile time
# optimized: y = 14

# INVALID: cannot reorder memory operations (in a language with mutation)
a = [1, 2, 3]
def g(lst):
    lst.append(4)
    return len(lst)

# a[0] = g(a)  -- cannot reorder the call and the subscript

# VALID: can eliminate dead code
if False:
    print("never runs")
# optimized: (remove the entire if block)

print("x =", x, "  y =", y)
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

**Critical Thinking Questions (CTQs)**

> **CTQ 1.1** What property of an expression makes it safe to evaluate at compile time? (Hint: think about the "pure function" discussion from the functional programming module.)

> **CTQ 1.2** The optimizer must prove that `f()` has no observable side effects before it can eliminate `f() + 0`. What information would the optimizer need to know about `f`? Where would it get that information?

> **CTQ 1.3** Name three operations that are NEVER safe to optimize away, even if their result is unused. (Think: division, function calls, I/O.)

---

## Model 2 — Constant Folding and Propagation

**Constant folding**: evaluate constant sub-expressions at compile time.
**Constant propagation**: substitute known constant values for variables.

```python  liascript
from dataclasses import dataclass
from typing import Any, Optional

@dataclass
class Num:
    value: float

@dataclass
class Var:
    name: str

@dataclass
class BinOp:
    op: str; left: Any; right: Any

@dataclass
class UnaryOp:
    op: str; operand: Any

@dataclass
class Let:
    name: str; value: Any; body: Any

@dataclass
class If:
    cond: Any; then_: Any; else_: Any

def fold_and_propagate(node, const_env: dict):
    """Constant folding + constant propagation in one pass."""
    match node:
        case Num():
            return node

        case Var(name=n):
            if n in const_env:
                return Num(const_env[n])   # constant propagation
            return node

        case Let(name=n, value=v, body=b):
            folded_v = fold_and_propagate(v, const_env)
            new_env = dict(const_env)
            if isinstance(folded_v, Num):
                new_env[n] = folded_v.value   # propagate this constant!
            return Let(n, folded_v, fold_and_propagate(b, new_env))

        case If(cond=c, then_=t, else_=e):
            fc = fold_and_propagate(c, const_env)
            if isinstance(fc, Num):
                # Dead branch elimination!
                if fc.value != 0:
                    return fold_and_propagate(t, const_env)
                else:
                    return fold_and_propagate(e, const_env)
            return If(fc,
                      fold_and_propagate(t, const_env),
                      fold_and_propagate(e, const_env))

        case UnaryOp(op='-', operand=o):
            fo = fold_and_propagate(o, const_env)
            if isinstance(fo, Num):
                return Num(-fo.value)
            return UnaryOp('-', fo)

        case BinOp(op=op, left=l, right=r):
            fl = fold_and_propagate(l, const_env)
            fr = fold_and_propagate(r, const_env)
            if isinstance(fl, Num) and isinstance(fr, Num):
                match op:
                    case '+': return Num(fl.value + fr.value)
                    case '-': return Num(fl.value - fr.value)
                    case '*': return Num(fl.value * fr.value)
                    case '/' if fr.value != 0: return Num(fl.value / fr.value)
            # Algebraic identities
            if isinstance(fl, Num) and fl.value == 0 and op == '+': return fr
            if isinstance(fr, Num) and fr.value == 0 and op == '+': return fl
            if isinstance(fl, Num) and fl.value == 1 and op == '*': return fr
            if isinstance(fr, Num) and fr.value == 1 and op == '*': return fl
            if isinstance(fl, Num) and fl.value == 0 and op == '*': return Num(0)
            if isinstance(fr, Num) and fr.value == 0 and op == '*': return Num(0)
            return BinOp(op, fl, fr)

def pretty(node) -> str:
    match node:
        case Num(value=v):          return str(int(v) if v == int(v) else v)
        case Var(name=n):           return n
        case Let(name=n, value=v, body=b): return f"let {n}={pretty(v)} in {pretty(b)}"
        case BinOp(op=o, left=l, right=r): return f"({pretty(l)}{o}{pretty(r)})"
        case UnaryOp(op=o, operand=x):     return f"({o}{pretty(x)})"
        case If(cond=c, then_=t, else_=e): return f"if {pretty(c)} then {pretty(t)} else {pretty(e)}"
        case _: return repr(node)

# Test cases
tests = [
    # let x = 3 in let y = x + 2 in x * y  → let x=3 in let y=5 in 15
    Let('x', Num(3), Let('y', BinOp('+', Var('x'), Num(2)),
                        BinOp('*', Var('x'), Var('y')))),
    # if (2 > 0) then 42 else 0  → 42  (dead code eliminated)
    If(BinOp('>', Num(2), Num(0)), Num(42), Num(0)),
    # (x + 0) * 1  → x
    BinOp('*', BinOp('+', Var('x'), Num(0)), Num(1)),
]

for t in tests:
    result = fold_and_propagate(t, {})
    print(f"{pretty(t):50} → {pretty(result)}")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

> **CTQ 2.1** The first test case propagates `x=3` into the body, evaluates `y=5`, then folds `3*5=15`. What is the final result? Is there any variable left in the output?

> **CTQ 2.2** Dead code elimination fires when the `If` condition folds to a known constant. The `2 > 0` case reduces to `Num(1)` (true). But our code doesn't fold `BinOp('>', Num(2), Num(0))` — fix the `fold_and_propagate` function to handle comparison operators.

> **CTQ 2.3** Constant propagation extends the `const_env` when a `let`-bound name gets a constant value. Why do we use `new_env = dict(const_env)` (a copy) rather than mutating `const_env` directly?

---

## Model 3 — Common Subexpression Elimination (CSE)

If the same expression appears twice and has no side effects in between, compute it once and reuse the result.

```python  liascript
from dataclasses import dataclass, field
from typing import Any

@dataclass
class Num:
    value: float

@dataclass
class Var:
    name: str

@dataclass
class BinOp:
    op: str; left: Any; right: Any

@dataclass
class Let:
    name: str; value: Any; body: Any

# Simple CSE: replace duplicate sub-expressions with shared variables
_cse_counter = 0
def fresh_name():
    global _cse_counter
    _cse_counter += 1
    return f"_cse{_cse_counter}"

def cse(node, seen: dict):
    """
    seen: maps (expr_key) → variable_name
    Returns (optimized_node, bindings_to_wrap)
    """
    key = expr_key(node)

    # Pure expression seen before? Reuse it!
    if key in seen and is_pure(node):
        return Var(seen[key]), []

    match node:
        case Num() | Var():
            return node, []

        case BinOp(op=op, left=l, right=r):
            new_l, binds_l = cse(l, seen)
            new_r, binds_r = cse(r, seen)
            new_node = BinOp(op, new_l, new_r)
            new_key = expr_key(new_node)
            name = fresh_name()
            seen[new_key] = name
            return Var(name), binds_l + binds_r + [(name, new_node)]

        case _:
            return node, []

def expr_key(node) -> str:
    """Canonical string representation for hashing."""
    match node:
        case Num(value=v): return f"N{v}"
        case Var(name=n):  return f"V{n}"
        case BinOp(op=o, left=l, right=r): return f"({expr_key(l)}{o}{expr_key(r)})"
        case _: return repr(node)

def is_pure(node) -> bool:
    """True if the expression has no side effects."""
    match node:
        case Num() | Var():          return True
        case BinOp(left=l, right=r): return is_pure(l) and is_pure(r)
        case _:                      return False

def wrap_bindings(node, bindings):
    """Wrap the result in let-bindings for CSE temporaries."""
    for name, val in reversed(bindings):
        node = Let(name, val, node)
    return node

def pretty(node) -> str:
    match node:
        case Num(value=v):  return str(int(v) if v == int(v) else v)
        case Var(name=n):   return n
        case BinOp(op=o, left=l, right=r): return f"({pretty(l)}{o}{pretty(r)})"
        case Let(name=n, value=v, body=b):  return f"let {n}={pretty(v)} in\n  {pretty(b)}"

# Expression: (x+1)*(x+1) — x+1 computed TWICE
from dataclasses import dataclass
_cse_counter = 0

x_plus_1 = BinOp('+', Var('x'), Num(1))
expr = BinOp('*', x_plus_1, x_plus_1)

optimized_core, bindings = cse(expr, {})
optimized = wrap_bindings(optimized_core, bindings)

print("Before CSE:")
print(f"  {pretty(expr)}")
print("\nAfter CSE:")
print(f"  {pretty(optimized)}")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

> **CTQ 3.1** After CSE, `(x+1)*(x+1)` should become `let _cse1 = (x+1) in _cse1 * _cse1`. Only ONE addition is computed instead of two. How many operations were eliminated?

> **CTQ 3.2** Why does CSE only apply to *pure* expressions? Give an example where applying CSE to an impure expression would change the program's behavior.

> **CTQ 3.3** CSE requires checking if two expressions are "the same." The `expr_key` function produces a canonical string. What's wrong with this approach if expressions contain variable names that were renamed by earlier passes?

---

## Model 4 — Function Inlining

**Inlining** replaces a function call with the function body, substituting arguments for parameters. This eliminates call overhead and enables further optimizations.

```python  liascript
from dataclasses import dataclass
from typing import Any

@dataclass
class Num:
    value: float

@dataclass
class Var:
    name: str

@dataclass
class BinOp:
    op: str; left: Any; right: Any

@dataclass
class Let:
    name: str; value: Any; body: Any

@dataclass
class Lambda:
    param: str; body: Any

@dataclass
class App:   # function application
    func: Any; arg: Any

def substitute(node, var: str, replacement):
    """Replace all free occurrences of var with replacement."""
    match node:
        case Num():                  return node
        case Var(name=n):            return replacement if n == var else node
        case BinOp(op=o, left=l, right=r):
            return BinOp(o, substitute(l, var, replacement),
                            substitute(r, var, replacement))
        case Let(name=n, value=v, body=b):
            new_v = substitute(v, var, replacement)
            if n == var:
                return Let(n, new_v, b)   # var is shadowed in body
            return Let(n, new_v, substitute(b, var, replacement))
        case Lambda(param=p, body=b):
            if p == var: return node   # var is shadowed
            return Lambda(p, substitute(b, var, replacement))
        case App(func=f, arg=a):
            return App(substitute(f, var, replacement),
                       substitute(a, var, replacement))
        case _: return node

def inline(node, fn_env: dict, inline_limit=5):
    """Inline small functions. fn_env maps name → Lambda."""
    match node:
        case App(func=Var(name=n), arg=a) if n in fn_env:
            lam = fn_env[n]
            if size(lam.body) <= inline_limit:  # only inline small functions
                inlined = substitute(lam.body, lam.param, inline(a, fn_env))
                return inline(inlined, fn_env)   # inline recursively!
        case App(func=f, arg=a):
            return App(inline(f, fn_env), inline(a, fn_env))
        case BinOp(op=o, left=l, right=r):
            return BinOp(o, inline(l, fn_env), inline(r, fn_env))
        case _:
            return node

def size(node) -> int:
    """Estimate node count (cost of inlining)."""
    match node:
        case Num() | Var():          return 1
        case BinOp(left=l, right=r): return 1 + size(l) + size(r)
        case Lambda(body=b):         return 1 + size(b)
        case App(func=f, arg=a):     return 1 + size(f) + size(a)
        case _:                      return 1

def pretty(node) -> str:
    match node:
        case Num(value=v):           return str(int(v) if v == int(v) else v)
        case Var(name=n):            return n
        case BinOp(op=o, left=l, right=r): return f"({pretty(l)}{o}{pretty(r)})"
        case Lambda(param=p, body=b):       return f"λ{p}.{pretty(b)}"
        case App(func=f, arg=a):            return f"{pretty(f)}({pretty(a)})"
        case Let(name=n, value=v, body=b):  return f"let {n}={pretty(v)} in {pretty(b)}"

# double = λx. x + x  — inline double(5) → 5 + 5
double = Lambda('x', BinOp('+', Var('x'), Var('x')))
fn_env = {'double': double}

expr = App(Var('double'), Num(5))
inlined = inline(expr, fn_env)
print(f"Before: {pretty(expr)}")
print(f"After:  {pretty(inlined)}")

# Compose with constant folding: double(3+2) → (3+2)+(3+2) → 10
from functools import reduce
expr2 = App(Var('double'), BinOp('+', Num(3), Num(2)))
inlined2 = inline(expr2, fn_env)
print(f"\nBefore: {pretty(expr2)}")
print(f"Inlined: {pretty(inlined2)}")
# (After constant folding, this would become 10)
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

> **CTQ 4.1** Inlining `double(5)` produces `5 + 5`. Can we further fold this? What optimization would you chain after inlining?

> **CTQ 4.2** The inline limit `inline_limit=5` prevents inlining large functions. Why? What happens to code size if you inline aggressively without a limit?

> **CTQ 4.3** Inlining a recursive function directly would loop forever. How does the limit protect against this? What more sophisticated check would be needed for a production compiler?

---

## Model 5 — Tail Call Optimization (TCO)

A **tail call** is a function call that is the *last* action of a function. Instead of creating a new stack frame, we can *reuse* the current frame.

```python  liascript
import sys

# Without TCO: factorial(10000) causes stack overflow in Python
def factorial_no_tco(n):
    if n <= 1: return 1
    return n * factorial_no_tco(n - 1)   # NOT a tail call: n * (...)

# With an accumulator, the recursive call IS a tail call:
def factorial_tco_helper(n, acc):
    if n <= 1: return acc
    return factorial_tco_helper(n - 1, n * acc)   # TAIL CALL: last action

def factorial_tco(n):
    return factorial_tco_helper(n, 1)

# Trampolining: simulate TCO in Python using thunks
class Thunk:
    def __init__(self, fn, *args):
        self.fn = fn; self.args = args
    def __call__(self):
        return self.fn(*self.args)

def trampoline(fn, *args):
    result = fn(*args)
    while isinstance(result, Thunk):
        result = result()
    return result

def fact_tramp(n, acc=1):
    if n <= 1: return acc
    return Thunk(fact_tramp, n - 1, n * acc)   # return thunk, not recursive call

print(f"factorial_tco(100)   = {factorial_tco(100)}")
print(f"fact_tramp(100)      = {trampoline(fact_tramp, 100)}")

# Without trampoline: would hit recursion limit at ~1000
# With trampoline: works for any n (constant stack depth!)
print(f"fact_tramp(5000)     = ...{str(trampoline(fact_tramp, 5000))[-5:]}")  # last 5 digits

# Detecting tail calls in an AST:
from dataclasses import dataclass
from typing import Any

@dataclass
class Call:
    fn_name: str; args: list

@dataclass
class If:
    cond: Any; then_: Any; else_: Any

@dataclass
class Return:
    value: Any

def is_tail_call(node, fn_name: str) -> bool:
    """Does node end with a tail call to fn_name?"""
    match node:
        case Return(value=Call(fn_name=n)) if n == fn_name:
            return True
        case If(then_=t, else_=e):
            return is_tail_call(t, fn_name) or is_tail_call(e, fn_name)
        case _:
            return False

# fact(n, acc) = if n<=1 then return acc else return fact(n-1, n*acc)
fact_body = If(None,
    Return(None),   # return acc — not a tail call to fact
    Return(Call('fact', []))   # return fact(...) — IS a tail call!
)
print(f"\nfact body has tail call to 'fact': {is_tail_call(fact_body, 'fact')}")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

> **CTQ 5.1** `factorial_no_tco` has `return n * factorial_no_tco(n-1)`. Why is this NOT a tail call? What computation happens after the recursive call returns?

> **CTQ 5.2** `factorial_tco_helper` has `return factorial_tco_helper(n-1, n*acc)`. Why IS this a tail call? What does "last action" mean precisely?

> **CTQ 5.3** Trampolining achieves tail call optimization without changing the language runtime — it works in Python, Java, or any language. What is the tradeoff compared to a language that natively supports TCO (like Scheme or Haskell)?

---

## Multiple Choice

Which optimization is UNSAFE to apply to `result = print("hello") or True`?

    [(x)] Replacing `print("hello")` with its constant value (it returns `None`)
    [( )] Evaluating `True` at compile time
    [( )] Keeping the original expression unchanged
    [( )] All of the above

---

Constant propagation extends the environment with `{x: 3}` when `let x = 3`. Why is it safe to propagate this constant throughout the body?

    [( )] Because x is an integer
    [(x)] Because `let` creates an immutable binding — x's value cannot change in the body
    [( )] Because 3 is small enough to inline
    [( )] Because the compiler checked for side effects

---

A tail call optimization converts a tail-recursive call into a loop at compile time. What benefit does this provide?

    [( )] Faster garbage collection
    [(x)] Constant stack space instead of O(n) stack frames — enables deep or infinite recursion without stack overflow
    [( )] Smaller bytecode
    [( )] Type safety

---

## Exercises

### Exercise 1 — Fix Comparison Folding (15 min)
Extend `fold_and_propagate` from Model 2 to handle comparison operators (`>`, `<`, `>=`, `<=`, `==`, `!=`) and boolean operators (`and`, `or`, `not`). Test: `if (2 > 1) then 42 else 0` should fold to `42`.

### Exercise 2 — Strength Reduction (20 min)
**Strength reduction** replaces expensive operations with cheaper ones:
- `x * 2` → `x + x` (addition is faster than multiplication on some CPUs)
- `x * 4` → `x << 2` (shift is faster than multiplication by a power of 2)
- `x / 2` → `x >> 1` (for integer division)

Implement `strength_reduce(node)` as a tree transformation. Test on `y * 8` and `z / 4`.

### Exercise 3 — Dead Code Elimination (20 min)
Write `eliminate_dead_code(node, live_vars: set)` that removes let-bindings whose names are never used in the body:

```
let x = expensive_computation() in 42
→ 42  (if x is never used)
```

But be careful: only eliminate if the binding expression is pure!

### Exercise 4 — Optimization Pipeline (25 min)
Combine multiple passes into a pipeline:
```python
def optimize(node):
    node = fold_and_propagate(node, {})
    node = eliminate_dead_code(node, collect_live_vars(node))
    node = inline(node, fn_env)
    node = fold_and_propagate(node, {})  # run again after inlining!
    return node
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)
Test the pipeline on a program that contains all four optimization opportunities. Show before and after.

### Exercise 5 — Mini TCO (30 min, harder)
Add tail call optimization to your Mini interpreter:
1. Write `is_tail_position(node, current_fn_name)` that returns True if a node is a tail call
2. Modify your evaluator: when a tail call is detected, instead of recursing, update the parameters and loop (use a `while True` loop in the evaluator)
3. Demonstrate: `fact(10000)` works without stack overflow after TCO, but fails without it

---

## Reflection

*(Write your answers individually, then discuss with your group.)*

1. **Safety vs. speed**: Every optimization in this module requires a safety proof ("this is valid because..."). What does this tell you about the relationship between semantics and optimization? Could you optimize a language you don't have a formal semantics for?

2. **Optimization order matters**: We ran constant folding *after* inlining. Why? Could you run them in the opposite order and get the same result? What does this say about the design of an optimization pipeline?

3. **Your final project**: Which of today's optimizations would you add to your Mini language? Which would require the most implementation effort? Pick one and sketch the implementation.

---

## Further Reading

- **"Engineering a Compiler"** — Cooper & Torczon, Chapters 8-10: the canonical compiler optimization textbook
- **"Compilers: Principles, Techniques, and Tools"** — Aho, Lam, Sethi, Ullman (Dragon Book): Chapters 9-10
- **"Compiling with Continuations"** — Appel: how CPS enables many optimizations uniformly
- **GCC optimization flags** — `gcc -O2` enables ~50 optimizations; the manual lists them all
- **LLVM passes** — each LLVM optimization is a separate pass; the source code is readable: https://llvm.org/docs/Passes.html
- **"Hacker's Delight"** — Henry Warren: arithmetic tricks behind strength reduction
