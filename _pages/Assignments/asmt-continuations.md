---
layout: assignment
permalink: /Assignments/Continuations
title: "CS374: Principles of Programming Languages - Continuations and call/cc"

info:
  coursenum: CS374
  purpose: "To transform your tree-walking interpreter into continuation-passing style and add first-class call/cc, then re-derive break, exceptions, and generators from continuations alone — seeing why call/cc is called the mother of all control structures."
  tilt:
    task: "Convert the interpreter to CPS with a trampoline, implement call/cc as a first-class feature, and use continuations to build non-local exit, exceptions, and generators, backed by a test suite and writeup."
    criteria: "Assessed on a correct CPS transform, a working call/cc with escaping continuations, three continuation-based control-flow applications, and a thorough test suite, each part worth 25 points; see the rubric below for the full breakdown."
  points: 100
  goals:
    - To transform a tree-walking interpreter to continuation-passing style (CPS)
    - To implement call/cc as a first-class language feature
    - To use continuations to implement non-local exit, generators, and coroutines
    - To understand how control flow abstractions unify as first-class continuations

  rubric:
    - weight: 25
      description: "CPS Transform (Goal 1)"
      preemerging: The student does not add a continuation parameter to interp, or the transformation compiles but produces wrong results for more than half the test cases due to incorrect continuation threading
      beginning: The continuation parameter is added and simple expressions (Num, Bool, Var) pass their value to k, but compound expressions such as BinOp, Let, and App do not chain continuations correctly — inner calls return values directly instead of calling k
      progressing: All expression types thread continuations correctly and interp_k(expr, env, lambda v v) agrees with interp(expr, env) for the provided test suite, but the trampoline is absent or incomplete so deeply nested programs still hit Python's recursion limit
      proficient: Every expression type passes its result through k with no direct returns; interp_k agrees with interp on all provided and hidden test cases; a working trampoline wraps all tail calls in thunks and a while loop drives them to completion; the student explains in comments why each recursive call is now a tail call
    - weight: 25
      description: "call/cc Implementation (Goals 2, 4)"
      preemerging: The Callcc AST node is defined but interp_k does not handle it, or the captured continuation is implemented as a plain closure that ignores the ContinuationEscape mechanism so invoking it does not actually escape
      beginning: ContinuationEscape and the Continuation class are present and the top-level driver catches the exception, but the captured continuation is applied at the wrong point — either it wraps the wrong k or it is invoked before the function argument is evaluated
      progressing: call/cc correctly escapes from within a single level of nesting (e.g., a flat list search) but fails when the escape must cross multiple continuation frames, such as escaping from a nested App or Let
      proficient: call/cc captures the exact current continuation k, wraps it as a Continuation that raises ContinuationEscape when called, the top-level driver unwraps the escaped value, and all three demonstration programs (non-local exit, abort, and try/raise) produce the specified output
    - weight: 25
      description: "Control Flow Applications (Goals 3, 4)"
      preemerging: Fewer than two of the three applications (non-local exit, exceptions, generators) are attempted, or those that are attempted do not use continuations — they use Python break/return/StopIteration directly instead
      beginning: Two of the three applications are implemented but one is structurally incorrect — for example, the exception mechanism uses only one continuation instead of two, or the generator saves state in a mutable list rather than in a captured continuation
      progressing: All three applications are implemented and produce correct output for the provided examples, but edge cases fail — the generator does not handle exhaustion gracefully, or the raise/handle mechanism does not propagate through nested handle calls correctly
      proficient: All three applications are implemented correctly using only continuations as the control mechanism; the non-local exit demo breaks at the right element; the raise/handle mechanism correctly propagates through nested frames; the range_gen generator yields every integer in range and raises StopIteration (or equivalent) on exhaustion; each application includes an explanatory comment connecting it to the continuation model
    - weight: 25
      description: "Testing and Documentation (Goals 1, 2, 3, 4)"
      preemerging: Fewer than five unit tests are present, or the test file does not import the student's module and instead tests stub functions, so the tests do not actually verify the implementation
      beginning: At least five tests are present and run against the real implementation, but they duplicate the same scenario with different literals — CPS equivalence, call/cc escape, the exception mechanism, and the generator protocol are not all covered
      progressing: Ten or more distinct tests cover all four required areas and all pass, but the README section is missing one or more of the three required explanations (what a continuation is, why call/cc is the mother of all control structures, which Python built-ins are special cases)
      proficient: Ten or more distinct tests cover CPS equivalence across at least four expression types, call/cc escape at multiple nesting depths, the two-continuation exception mechanism, and the generator protocol including exhaustion; all tests pass; the README section defines a continuation in one clear sentence, explains the "mother of all control structures" claim with at least one concrete example, and maps try/except, generators, and async/await to the continuation model

  readings:
    - rtitle: "Continuations and call/cc Activity"
      rlink: "https://liascript.github.io/course/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374-Fall2026/gh-pages/_pages/Activities/liascript-lambdacalculus2.md"
    - rtitle: "Structure and Interpretation of Computer Programs — Chapter 3"
      rlink: "https://mitp-content-server.mit.edu/books/content/sectbyfn/books_pres_0/6515/sicp.zip/index.html"
    - rtitle: "Continuation-Passing Style (Wikipedia)"
      rlink: "https://en.wikipedia.org/wiki/Continuation-passing_style"

tags:
  - continuations
  - cps
  - call-cc
  - interpreter
  - control-flow

---

This assignment extends the tree-walking interpreter you built in the previous assignment. You will transform it to continuation-passing style (CPS), implement `call/cc` as a first-class language feature, and then use those tools to re-derive Python's own control-flow abstractions — break, try/except, generators, and async/await — from scratch, using nothing but functions and continuations. By the end you will understand why `call/cc` is called "the mother of all control structures."

Build in the scaffolded order below. Each part depends on the previous one.

---

## Part 1: CPS Transform (25 points)

### Background

In a **direct-style** interpreter every recursive call to `interp` returns a value to its caller. That returned value sits on the Python call stack until the caller finishes with it. For a deeply nested expression (or a long-running recursive program), this means the Python stack grows proportionally to the expression depth.

In **continuation-passing style**, no call ever returns. Instead, every call is given an extra argument — the *continuation* `k` — which is a function representing "what to do next with the result." When the call computes its value, it passes that value to `k` instead of returning it. Because `k` is the very last thing called, every call is a *tail call*, and a sufficiently smart runtime (or a trampoline) can execute it in constant stack space.

The key mechanical rule is:

> Wherever direct style writes `return f(x)`, CPS writes `f_k(x, env, k)`.  
> Wherever direct style writes `v = f(x); use(v)`, CPS writes `f_k(x, env, lambda v: use_k(v, env, k))`.

### The Starter Interpreter

Below is the complete direct-style interpreter you will transform. Copy it into `continuations.py` and verify it works before touching anything.

```python
from dataclasses import dataclass
from typing import Any, Callable, Dict, Optional

# ---------- AST node types ----------

@dataclass
class Num:
    value: float

@dataclass
class Bool:
    value: bool

@dataclass
class Var:
    name: str

@dataclass
class BinOp:
    op: str
    left: Any
    right: Any

@dataclass
class If:
    cond: Any
    then: Any
    else_: Any

@dataclass
class Let:
    name: str
    val: Any
    body: Any

@dataclass
class Lam:
    param: str
    body: Any

@dataclass
class App:
    fun: Any
    arg: Any

# ---------- Environment ----------

class Env:
    def __init__(self, bindings=None, parent=None):
        self.bindings = bindings or {}
        self.parent = parent

    def lookup(self, name):
        if name in self.bindings:
            return self.bindings[name]
        if self.parent:
            return self.parent.lookup(name)
        raise NameError(name)

    def extend(self, name, val):
        return Env({name: val}, self)

@dataclass
class Closure:
    param: str
    body: Any
    env: Any

# ---------- Direct-style interpreter ----------

def interp(expr, env):
    if isinstance(expr, Num):
        return expr.value
    if isinstance(expr, Bool):
        return expr.value
    if isinstance(expr, Var):
        return env.lookup(expr.name)
    if isinstance(expr, BinOp):
        l = interp(expr.left, env)
        r = interp(expr.right, env)
        if expr.op == '+': return l + r
        if expr.op == '-': return l - r
        if expr.op == '*': return l * r
        if expr.op == '/': return l / r
        raise ValueError(f"Unknown op: {expr.op}")
    if isinstance(expr, If):
        branch = expr.then if interp(expr.cond, env) else expr.else_
        return interp(branch, env)
    if isinstance(expr, Let):
        v = interp(expr.val, env)
        return interp(expr.body, env.extend(expr.name, v))
    if isinstance(expr, Lam):
        return Closure(expr.param, expr.body, env)
    if isinstance(expr, App):
        fn  = interp(expr.fun, env)
        arg = interp(expr.arg, env)
        return interp(fn.body, Env({fn.param: arg}, fn.env))
    raise ValueError(f"Unknown expr: {expr}")
```

Smoke-test before proceeding:

```python
empty = Env()

# (lambda x: x + 1)(41)  =>  42.0
expr = App(Lam("x", BinOp("+", Var("x"), Num(1))), Num(41))
assert interp(expr, empty) == 42.0

# let y = 10 in (y * y)  =>  100.0
expr2 = Let("y", Num(10), BinOp("*", Var("y"), Var("y")))
assert interp(expr2, empty) == 100.0

print("direct-style tests passed")
```

### Step 1a: Add the Continuation Parameter

Transform `interp` into `interp_k(expr, env, k)` where `k: (Any) -> Any` is the current continuation. The identity continuation is `lambda v: v`, so `interp_k(expr, env, lambda v: v)` should give the same result as `interp(expr, env)`.

The mechanical rule for each case:

- **Num / Bool** — the value is already known. Pass it directly to `k`.
- **Var** — look up the value. Pass it to `k`.
- **BinOp** — evaluate the left sub-expression, then (inside its continuation) evaluate the right sub-expression, then (inside *that* continuation) apply the operator and pass the result to the outer `k`.
- **If** — evaluate the condition; inside its continuation, choose the branch and call `interp_k` on it with the same outer `k`.
- **Let** — evaluate the value; inside its continuation, evaluate the body in the extended environment with the same outer `k`.
- **Lam** — build the closure and pass it to `k` immediately (no sub-expressions to evaluate).
- **App** — evaluate the function, then the argument, then call `interp_k` on the closure body with the outer `k`.

Complete implementation:

```python
def interp_k(expr, env, k):
    """CPS interpreter. Every path ends with a call to k (or a tail call
    that will eventually call k). No path returns a value directly."""

    if isinstance(expr, Num):
        return k(expr.value)

    if isinstance(expr, Bool):
        return k(expr.value)

    if isinstance(expr, Var):
        return k(env.lookup(expr.name))

    if isinstance(expr, BinOp):
        # Evaluate left, then right, then apply op, then call k.
        def after_left(lv):
            def after_right(rv):
                if expr.op == '+': return k(lv + rv)
                if expr.op == '-': return k(lv - rv)
                if expr.op == '*': return k(lv * rv)
                if expr.op == '/': return k(lv / rv)
                raise ValueError(f"Unknown op: {expr.op}")
            return interp_k(expr.right, env, after_right)
        return interp_k(expr.left, env, after_left)

    if isinstance(expr, If):
        def after_cond(cv):
            branch = expr.then if cv else expr.else_
            return interp_k(branch, env, k)
        return interp_k(expr.cond, env, after_cond)

    if isinstance(expr, Let):
        def after_val(v):
            return interp_k(expr.body, env.extend(expr.name, v), k)
        return interp_k(expr.val, env, after_val)

    if isinstance(expr, Lam):
        return k(Closure(expr.param, expr.body, env))

    if isinstance(expr, App):
        def after_fun(fn):
            def after_arg(arg):
                new_env = Env({fn.param: arg}, fn.env)
                return interp_k(fn.body, new_env, k)
            return interp_k(expr.arg, env, after_arg)
        return interp_k(expr.fun, env, after_fun)

    raise ValueError(f"Unknown expr: {expr}")
```

### Step 1b: Verify CPS Equivalence

For every expression `e`, `interp_k(e, env, lambda v: v)` must equal `interp(e, env)`. Add the following tests to your test file and confirm they all pass:

```python
def test_cps_equivalence():
    empty = Env()
    identity = lambda v: v

    cases = [
        Num(3.14),
        Bool(True),
        BinOp("+", Num(2), Num(3)),
        BinOp("*", Num(4), BinOp("-", Num(10), Num(3))),
        If(Bool(True),  Num(1), Num(2)),
        If(Bool(False), Num(1), Num(2)),
        Let("x", Num(7), BinOp("*", Var("x"), Var("x"))),
        App(Lam("x", BinOp("+", Var("x"), Num(1))), Num(41)),
        Let("f", Lam("n", BinOp("*", Var("n"), Num(2))),
            App(Var("f"), Num(21))),
    ]

    for expr in cases:
        direct = interp(expr, empty)
        cps    = interp_k(expr, empty, identity)
        assert direct == cps, f"Mismatch on {expr}: direct={direct}, cps={cps}"

    print("CPS equivalence: all cases pass")

test_cps_equivalence()
```

### Step 1c: Trampolining

Even though every call in `interp_k` is a tail call *logically*, Python does not optimize tail calls. A deeply recursive program therefore still overflows the Python stack. The fix is a **trampoline**: instead of calling the next continuation directly, return a zero-argument *thunk* (a `lambda: ...`) and let a top-level loop drive execution.

Introduce a sentinel wrapper:

```python
class Thunk:
    """Wraps a zero-argument callable to distinguish a deferred call
    from an ordinary return value."""
    def __init__(self, f):
        self.f = f

def trampoline(thunk_or_value):
    """Drive a trampolined computation to completion."""
    result = thunk_or_value
    while isinstance(result, Thunk):
        result = result.f()
    return result
```

Then rewrite every tail call in `interp_k` to return a `Thunk` instead of calling directly:

```python
def interp_t(expr, env, k):
    """Trampolined CPS interpreter. Every recursive call is wrapped in
    a Thunk so Python never grows the call stack past a fixed depth."""

    if isinstance(expr, Num):
        return k(expr.value)

    if isinstance(expr, Bool):
        return k(expr.value)

    if isinstance(expr, Var):
        return k(env.lookup(expr.name))

    if isinstance(expr, BinOp):
        def after_left(lv):
            def after_right(rv):
                if expr.op == '+': return k(lv + rv)
                if expr.op == '-': return k(lv - rv)
                if expr.op == '*': return k(lv * rv)
                if expr.op == '/': return k(lv / rv)
                raise ValueError(f"Unknown op: {expr.op}")
            return Thunk(lambda: interp_t(expr.right, env, after_right))
        return Thunk(lambda: interp_t(expr.left, env, after_left))

    if isinstance(expr, If):
        def after_cond(cv):
            branch = expr.then if cv else expr.else_
            return Thunk(lambda: interp_t(branch, env, k))
        return Thunk(lambda: interp_t(expr.cond, env, after_cond))

    if isinstance(expr, Let):
        def after_val(v):
            return Thunk(lambda: interp_t(expr.body, env.extend(expr.name, v), k))
        return Thunk(lambda: interp_t(expr.val, env, after_val))

    if isinstance(expr, Lam):
        return k(Closure(expr.param, expr.body, env))

    if isinstance(expr, App):
        def after_fun(fn):
            def after_arg(arg):
                new_env = Env({fn.param: arg}, fn.env)
                return Thunk(lambda: interp_t(fn.body, new_env, k))
            return Thunk(lambda: interp_t(expr.arg, env, after_arg))
        return Thunk(lambda: interp_t(expr.fun, env, after_fun))

    raise ValueError(f"Unknown expr: {expr}")

def run(expr, env=None):
    """Top-level driver: trampolines interp_t with the identity continuation."""
    if env is None:
        env = Env()
    return trampoline(interp_t(expr, env, lambda v: v))
```

Verify the trampoline does not stack-overflow on a deeply nested chain of `Let` bindings:

```python
def deep_let(depth, base_val):
    """Build:  let x0 = base_val in let x1 = x0 in ... let xN = x(N-1) in xN"""
    expr = Num(base_val)
    for i in range(depth):
        expr = Let(f"x{i}", expr, Var(f"x{i}"))
    return expr

# Python default recursion limit is 1000; 2000 should overflow direct-style
deep = deep_let(2000, 99.0)
result = run(deep)
assert result == 99.0, f"Expected 99.0, got {result}"
print("Trampoline depth test passed")
```

---

## Part 2: Implementing call/cc (25 points)

### Background

`call/cc` stands for *call with current continuation*. It takes a function `f` and calls it with a special argument: the *current continuation* — the function that represents everything that would have happened after this `call/cc` expression returned. Calling that continuation with a value `v` is equivalent to "returning `v` from the call/cc expression, jumping over everything that came after it."

In a CPS interpreter this is almost trivial: the current continuation is exactly the `k` that was passed to the `call/cc` case of `interp_k`. The challenge is making the captured `k` usable as an *escape* — once invoked, it should bypass all the other pending continuations and deliver the value directly to wherever `k` was bound.

### Step 2a: New AST Node and Exception Classes

Add these definitions to `continuations.py`:

```python
@dataclass
class Callcc:
    """call/cc expression.  fun is a Lam (or any expression that
    evaluates to a Closure) that accepts the current continuation."""
    fun: Any


class ContinuationEscape(Exception):
    """Raised when a captured continuation is invoked.  Carries the
    value that was passed to the continuation so the top-level driver
    can recover it."""
    def __init__(self, cont_id: int, value: Any):
        self.cont_id = cont_id
        self.value   = value


class Continuation:
    """A first-class continuation.  Calling an instance raises
    ContinuationEscape, which unwinds all intermediate frames until
    the matching try/except in the top-level driver."""
    _counter = 0

    def __init__(self, k: Callable):
        Continuation._counter += 1
        self._id = Continuation._counter
        self._k  = k          # the continuation to resume

    def __call__(self, v: Any) -> Any:
        raise ContinuationEscape(self._id, v)

    def resume(self, v: Any) -> Any:
        """Called by the top-level driver after catching the escape."""
        return self._k(v)
```

Each `Continuation` gets a unique integer ID so the top-level driver can match the escape to the right continuation when multiple `call/cc`s are nested.

### Step 2b: Handle Callcc in interp_k

Add a `Callcc` branch to `interp_k` (and to `interp_t` for the trampolined version):

```python
    if isinstance(expr, Callcc):
        # Capture the current k as an escaping Continuation.
        cont = Continuation(k)
        # Evaluate the function argument.
        def after_fun(fn):
            # Apply fn to the captured continuation.
            # If fn calls cont(v), ContinuationEscape is raised immediately.
            new_env = Env({fn.param: cont}, fn.env)
            return interp_k(fn.body, new_env, k)
        return interp_k(expr.fun, env, after_fun)
```

### Step 2c: Top-Level Driver with Escape Handling

Update `run` to catch `ContinuationEscape` and resume the captured continuation:

```python
def run(expr, env=None):
    """Top-level driver with call/cc support.  Catches ContinuationEscape
    and hands the escaped value back to the captured continuation."""
    if env is None:
        env = Env()
    try:
        return trampoline(interp_t(expr, env, lambda v: v))
    except ContinuationEscape as esc:
        # Resume the captured continuation with the escaped value.
        return trampoline(esc.value if callable(esc.value) else
                          Thunk(lambda: esc.value))
```

A cleaner approach routes the resume through the stored `_k`:

```python
def run(expr, env=None):
    if env is None:
        env = Env()
    # We use a registry so nested call/cc can find the right continuation.
    _continuations: Dict[int, Continuation] = {}

    def drive(thunk_or_val):
        result = thunk_or_val
        while True:
            try:
                while isinstance(result, Thunk):
                    result = result.f()
                return result
            except ContinuationEscape as esc:
                # Look up the continuation and resume it.
                cont = _continuations.get(esc.cont_id)
                if cont is None:
                    raise   # unhandled escape
                result = Thunk(lambda: cont.resume(esc.value))

    # Patch Continuation.__init__ to register with our local dict.
    original_init = Continuation.__init__
    def patched_init(self, k):
        original_init(self, k)
        _continuations[self._id] = self
    Continuation.__init__ = patched_init

    try:
        return drive(interp_t(expr, env, lambda v: v))
    finally:
        Continuation.__init__ = original_init
```

### Step 2d: Demonstration Programs

Write and run each of the following. Include the output as a comment.

**Demo 1 — Non-local exit (escape from a "loop").**  
Build a list-search that returns the first even number without evaluating the rest of the list:

```python
def first_even_demo():
    """Uses call/cc to escape as soon as an even number is found.
    In a real interpreter this would be written in the object language;
    here we build ASTs by hand to demonstrate the mechanism."""

    # Simulated list as nested lets: let hd = 3 in let tl_hd = 8 in ...
    # We'll call a Python-level helper that searches and escapes.
    result_box = [None]

    class EscapeSignal(Exception):
        def __init__(self, v): self.v = v

    def search(lst, pred):
        cont_called = False
        escape = None

        def k_escape(v):
            nonlocal cont_called
            cont_called = True
            raise EscapeSignal(v)

        for item in lst:
            if pred(item):
                k_escape(item)

        return None   # not found

    data = [3, 7, 1, 8, 2, 5]
    try:
        search(data, lambda x: x % 2 == 0)
    except EscapeSignal as e:
        result_box[0] = e.v

    assert result_box[0] == 8, f"Expected 8, got {result_box[0]}"
    print(f"first_even_demo: found {result_box[0]}")   # => 8

first_even_demo()
```

**Demo 2 — Abort computation early (call/cc as throw).**  
Evaluate an expression tree that contains a "division by zero" node and abort before reaching it:

```python
def abort_demo():
    """Demonstrates that invoking the captured continuation aborts
    all pending computation.  The multiply-by-zero node is never reached."""

    abort_box = [None]

    # Simulate: let k = call/cc(lambda k: k) in (abort_early * expensive)
    # where abort_early calls k("aborted") before expensive is evaluated.
    class Abort(Exception):
        def __init__(self, v): self.v = v

    def run_with_abort(thunk):
        def k_abort(v):
            raise Abort(v)
        try:
            # The computation calls k_abort before reaching expensive_work.
            k_abort("aborted!")
            # This line should never execute.
            result = thunk() * 1000000
            return result
        except Abort as a:
            return a.v

    result = run_with_abort(lambda: 1 / 0)   # 1/0 is never reached
    assert result == "aborted!", f"Expected 'aborted!', got {result}"
    print(f"abort_demo: result = {result!r}")   # => 'aborted!'

abort_demo()
```

**Demo 3 — call/cc as try/raise.**  
Show that `call/cc` gives you a general try/raise mechanism:

```python
def try_raise_demo():
    """Implements a simple try/raise using two continuations:
    k_ret for normal return and k_exc for exception escape."""

    class Raised(Exception):
        def __init__(self, v): self.v = v

    def my_try(body_fn, handler_fn):
        """Run body_fn(raise_fn).  If body_fn calls raise_fn(v),
        run handler_fn(v) instead of returning body_fn's result."""
        def raise_fn(v):
            raise Raised(v)
        try:
            return body_fn(raise_fn)
        except Raised as r:
            return handler_fn(r.v)

    # Normal path — no raise.
    result1 = my_try(
        lambda raise_: 42,
        lambda exc:    -1
    )
    assert result1 == 42, f"Expected 42, got {result1}"

    # Exception path — raise is called.
    result2 = my_try(
        lambda raise_: raise_("oops") or 99,   # raise_ never returns
        lambda exc:    f"caught: {exc}"
    )
    assert result2 == "caught: oops", f"Expected 'caught: oops', got {result2}"

    print(f"try_raise_demo: normal={result1}, exceptional={result2!r}")

try_raise_demo()
```

---

## Part 3: Control Flow Applications (25 points)

With the CPS interpreter and `call/cc` in hand, you will re-derive three standard Python control-flow abstractions from first principles.

### Part 3a: Non-Local Exit (break / return)

A `break` statement is really "call the continuation that was captured at the top of the loop." In CPS, the loop body receives a `k_break` continuation in addition to the normal `k`; when the body calls `k_break(value)`, execution jumps directly to after the loop.

Implement `for_until` in Python (mimicking what your interpreter would do):

```python
def for_until(lst, body_fn, default):
    """Iterate over lst, calling body_fn(item, break_fn) for each item.
    If body_fn calls break_fn(v), iteration stops and v is returned.
    If the list is exhausted without a break, default is returned.

    break_fn is the continuation captured at the 'exit loop' point."""

    class BreakEscape(Exception):
        def __init__(self, v): self.v = v

    def break_fn(v):
        raise BreakEscape(v)

    try:
        for item in lst:
            body_fn(item, break_fn)
        return default
    except BreakEscape as b:
        return b.v


# Find the first string longer than 4 characters, return it, stop immediately.
words = ["cat", "dog", "elephant", "ant", "hippopotamus"]

result = for_until(
    words,
    lambda word, brk: brk(word) if len(word) > 4 else None,
    "not found"
)
assert result == "elephant", f"Expected 'elephant', got {result}"
print(f"for_until: first long word = {result!r}")   # => 'elephant'


# Demonstrate 'return' from a function via continuation.
def find_first(lst, pred):
    """Uses for_until so the body can 'return' early without
    examining the rest of the list."""
    return for_until(lst, lambda x, ret: ret(x) if pred(x) else None, None)

primes = [4, 6, 7, 8, 10, 12]
first_prime = find_first(primes, lambda n: n > 1 and all(n % i != 0 for i in range(2, n)))
assert first_prime == 7, f"Expected 7, got {first_prime}"
print(f"find_first prime: {first_prime}")   # => 7
```

Write a Mini-language program (as hand-built ASTs) that uses `Callcc` to break out of the first even number in a list, and verify the result with `run`.

### Part 3b: Exceptions from Scratch

Python's `try/except` is a two-continuation pattern: every computation runs with two `k`s — one for normal return (`k_ret`) and one for exception escape (`k_exc`). The `raise` keyword is just "call `k_exc`"; `try/except` is just "install a new `k_exc`."

Implement a `two_k_interp` wrapper that makes both continuations explicit:

```python
def with_handler(body_fn, handler_fn):
    """Run body_fn with an explicit exception continuation k_exc.
    If body_fn calls k_exc(err), handler_fn(err) is the result.
    Otherwise body_fn's normal return value is the result.

    This is structurally identical to Python's try/except, but the
    mechanism is visible: k_exc is just a function passed as an argument."""

    class ExcEscape(Exception):
        def __init__(self, err): self.err = err

    def k_exc(err):
        raise ExcEscape(err)

    try:
        return body_fn(k_exc)
    except ExcEscape as e:
        return handler_fn(e.err)


# Simple raise and catch.
result = with_handler(
    lambda raise_: raise_("division by zero"),
    lambda err:    f"handled: {err}"
)
assert result == "handled: division by zero"
print(f"with_handler basic: {result!r}")

# Nested handlers: inner handler catches TypeError, outer catches ValueError.
result2 = with_handler(
    lambda outer_raise: with_handler(
        lambda inner_raise: inner_raise("type mismatch"),
        lambda err: f"inner caught: {err}"
    ),
    lambda err: f"outer caught: {err}"
)
assert result2 == "inner caught: type mismatch"
print(f"with_handler nested: {result2!r}")

# Propagation: inner handler re-raises to outer.
result3 = with_handler(
    lambda outer_raise: with_handler(
        lambda inner_raise: outer_raise("propagated!"),
        lambda err: f"inner caught: {err}"   # inner never fires
    ),
    lambda err: f"outer caught: {err}"
)
assert result3 == "outer caught: propagated!"
print(f"with_handler propagated: {result3!r}")
```

In your write-up, explain in two or three sentences why Python's `try/except` is exactly this pattern and what the "third continuation" would buy you (see the reflection prompt).

### Part 3c: Generators as Coroutines

A generator `yield`s a value and *suspends* itself — it saves "the rest of the generator" as a continuation and hands control back to the caller. Resuming the generator is just calling that saved continuation.

Implement `range_gen` using explicit continuation capture:

```python
def make_generator(produce_fn):
    """Creates a generator object from produce_fn.
    produce_fn receives a yield_fn(value) callback.
    Calling next() on the returned object resumes the generator.

    Internally, produce_fn runs in a separate thread so that
    yield_fn can actually suspend it — this is how Python's own
    generator machinery works under the hood."""
    import threading

    ready     = threading.Event()   # generator has a value ready
    consumed  = threading.Event()   # caller has consumed the value
    box       = [None, False]       # [current_value, exhausted]
    exc_box   = [None]

    def yield_fn(value):
        box[0] = value
        ready.set()       # signal caller: value is ready
        consumed.wait()   # wait until caller calls next() again
        consumed.clear()

    def runner():
        try:
            produce_fn(yield_fn)
        except Exception as e:
            exc_box[0] = e
        finally:
            box[1] = True   # mark exhausted
            ready.set()     # wake the caller one last time

    thread = threading.Thread(target=runner, daemon=True)
    thread.start()

    class Generator:
        def __iter__(self):
            return self

        def __next__(self):
            ready.wait()    # wait for the next yield (or exhaustion)
            ready.clear()
            if exc_box[0] is not None:
                raise exc_box[0]
            if box[1]:
                raise StopIteration
            value = box[0]
            consumed.set()  # tell the generator to continue
            return value

    return Generator()


def range_gen(start, stop):
    """A generator that yields integers from start (inclusive) to
    stop (exclusive), one at a time.  Demonstrates that a generator
    is just a computation that suspends itself by saving its
    continuation and transferring control to the caller."""
    def produce(yld):
        i = start
        while i < stop:
            yld(i)
            i += 1
    return make_generator(produce)


# Consume the generator with a for loop (uses __next__ internally).
collected = list(range_gen(3, 8))
assert collected == [3, 4, 5, 6, 7], f"Expected [3..7], got {collected}"
print(f"range_gen(3, 8) = {collected}")

# Exhaust and verify StopIteration.
gen = range_gen(0, 2)
assert next(gen) == 0
assert next(gen) == 1
try:
    next(gen)
    assert False, "Should have raised StopIteration"
except StopIteration:
    print("range_gen: StopIteration raised correctly")
```

In your write-up, trace through one `next()` call and explain which line corresponds to the "save continuation" step and which corresponds to the "resume continuation" step.

---

## Part 4: Testing and Documentation (25 points)

### Step 4a: Test Suite

Create `test_continuations.py` with at least 10 unit tests. The tests must cover all four required areas. Use the standard `unittest` module or `pytest` (document your choice). Below is a skeleton to expand:

```python
import unittest
from continuations import (
    Num, Bool, Var, BinOp, If, Let, Lam, App, Callcc,
    Env, Closure, interp, interp_k, run, for_until, with_handler, range_gen
)

class TestCPSEquivalence(unittest.TestCase):

    def setUp(self):
        self.env = Env()
        self.idk = lambda v: v

    def test_num(self):
        expr = Num(3.0)
        self.assertEqual(interp(expr, self.env),
                         interp_k(expr, self.env, self.idk))

    def test_binop_add(self):
        expr = BinOp("+", Num(10), Num(32))
        self.assertEqual(interp(expr, self.env),
                         interp_k(expr, self.env, self.idk))

    def test_nested_let(self):
        expr = Let("x", Num(5), BinOp("*", Var("x"), Var("x")))
        self.assertEqual(interp(expr, self.env),
                         interp_k(expr, self.env, self.idk))

    def test_lambda_application(self):
        expr = App(Lam("n", BinOp("+", Var("n"), Num(1))), Num(99))
        self.assertEqual(interp(expr, self.env),
                         interp_k(expr, self.env, self.idk))

    def test_if_true_branch(self):
        expr = If(Bool(True), Num(1), Num(2))
        self.assertEqual(interp(expr, self.env), 1)
        self.assertEqual(interp_k(expr, self.env, self.idk), 1)

    def test_if_false_branch(self):
        expr = If(Bool(False), Num(1), Num(2))
        self.assertEqual(interp(expr, self.env), 2)
        self.assertEqual(interp_k(expr, self.env, self.idk), 2)


class TestCallcc(unittest.TestCase):

    def test_callcc_identity(self):
        """call/cc with a function that ignores its continuation
        should behave like a normal function call."""
        expr = Callcc(Lam("k", Num(42)))
        self.assertEqual(run(expr), 42)

    def test_callcc_escape(self):
        """Invoking the captured continuation should escape immediately."""
        # (call/cc (lambda k: (k 7))) => 7
        expr = Callcc(Lam("k", App(Var("k"), Num(7))))
        self.assertEqual(run(expr), 7)

    def test_callcc_escape_ignores_rest(self):
        """After escaping, the rest of the computation is discarded."""
        # let result = call/cc(lambda k: k(5)) in (result * 1000)
        # k(5) escapes before the multiply can run => result is 5, not 5000
        expr = Let(
            "result",
            Callcc(Lam("k", App(Var("k"), Num(5)))),
            BinOp("*", Var("result"), Num(1000))
        )
        # The escape fires before the Let body runs.
        result = run(expr)
        # Depending on your implementation the result is either 5 (escape before
        # Let body) or 5000 (escape resumes inside Let body).
        # Document your choice and assert the expected value.
        self.assertIn(result, [5, 5000])


class TestExceptionMechanism(unittest.TestCase):

    def test_no_raise(self):
        result = with_handler(lambda raise_: 99, lambda e: -1)
        self.assertEqual(result, 99)

    def test_raise_caught(self):
        result = with_handler(lambda raise_: raise_("err"), lambda e: f"got {e}")
        self.assertEqual(result, "got err")

    def test_propagation(self):
        result = with_handler(
            lambda outer: with_handler(
                lambda inner: outer("propagated"),
                lambda e: "inner"
            ),
            lambda e: f"outer: {e}"
        )
        self.assertEqual(result, "outer: propagated")


class TestGenerator(unittest.TestCase):

    def test_range_gen_values(self):
        self.assertEqual(list(range_gen(0, 5)), [0, 1, 2, 3, 4])

    def test_range_gen_exhaustion(self):
        gen = range_gen(0, 1)
        self.assertEqual(next(gen), 0)
        with self.assertRaises(StopIteration):
            next(gen)

    def test_range_gen_empty(self):
        self.assertEqual(list(range_gen(5, 5)), [])


if __name__ == "__main__":
    unittest.main()
```

Add at least three more tests of your own that cover edge cases not already tested above.

### Step 4b: README Documentation Section

Add a section called `## Continuations` to your submission's `README.md` that answers the following three questions. Each answer must be written in your own words.

**What is a continuation?**  
Write exactly one sentence. A continuation is the function representing "everything that remains to be done with a value once the current expression finishes evaluating."

**Why is call/cc called "the mother of all control structures"?**  
Write a short paragraph (three to five sentences). Explain that `call/cc` can encode any control transfer — early return, exceptions, loops with break, generators, coroutines, and async/await — because each of those is just a way of naming and invoking a specific point in the remaining computation. Give at least one concrete example: pick one Python construct and explain how it is `call/cc` with a restriction (e.g., generators restrict call/cc to a single level of nesting — the generator frame — and do not allow the saved continuation to be called more than once per `yield`).

**Which Python built-ins are special cases of continuations?**  
Write a table with three rows: `try/except`, `yield` (generators), and `async/await`. For each, name the restriction that makes it a "special case" rather than full `call/cc`.

---

## Deliverables

Submit a ZIP containing:
- `continuations.py` — all interpreter code from Parts 1–3 (import your prior `lexer.py` and `parser.py` if you wire the AST nodes to the parser; otherwise stand-alone AST definitions are fine)
- `test_continuations.py` — test suite from Part 4, all tests passing
- `README.md` — the Continuations documentation section from Part 4b

Ensure reproducibility: state your Python version and whether you used `pytest` or `unittest`.

---

## Grading Breakdown

| Component | Points |
|-----------|--------|
| Part 1: CPS Transform | 25 |
| Part 2: call/cc Implementation | 25 |
| Part 3: Control Flow Applications | 25 |
| Part 4: Testing and Documentation | 25 |
| **Total** | **100** |

---

## Reflection Prompts

1. The CPS transform makes every function call a tail call. Why does this matter for a language implementation? In particular, what property of tail calls is exploited by the trampoline, and what would happen to a language that ran CPS code without a trampoline on a stack-based machine?

2. `call/cc` captures "the rest of the computation." Where exactly does the boundary between "captured" and "not captured" fall? In the expression `(+ 1 (call/cc (lambda k: (k 7))))`, draw the call stack at the moment `k` is captured and identify which frames are inside the captured continuation and which are not.

3. Python has `try/except`, generators (`yield`), and `async/await`. Explain how each is a restricted form of `call/cc`. For each, name the specific restriction — for example, which direction(s) the continuation can travel, whether it can be called more than once, and whether it can outlive the frame that created it.

4. Your exception mechanism from Part 3b uses two continuations (`k_ret` and `k_exc`). What would a three-continuation interpreter look like, and what would the third continuation handle? (Hint: think about what happens in Python when a `finally` block runs — is it captured by `k_ret`, `k_exc`, or something else entirely?)

5. If collaboration with a buddy was permitted, did you work with a buddy on this assignment? If so, who? If not, do you certify that this submission represents your own original work? Please identify any and all portions of your submission that were not originally written by you. Approximately how many hours did it take you to finish this assignment?
