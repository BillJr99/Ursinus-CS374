<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374-Fall2026/gh-pages/_pages/Activities/liascript-closures.md or locally via https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374-Fall2026/gh-pages/_pages/Activities/liascript-closures.md

import: https://raw.githubusercontent.com/liascript/CodeRunner/master/README.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

# Closures and First-Class Functions

Have you ever wondered how a function can "remember" a value from a context that no longer exists?  Think of a closure like a letter that carries its own envelope: even after the post office (the enclosing scope) closes for the day, the letter still knows exactly where it came from.  Closures are the mechanism that makes callbacks, iterators, and the entire functional-programming style of JavaScript, Python, and Scheme possible; understanding them means understanding how scope and state really work at runtime.

## Learning Goals

By the end of this activity, you will be able to:

- Define a closure as a pair of code and its defining environment, and explain why it is necessary in a language with first-class functions and static scope
- Trace environment diagrams for closure creation and invocation, identifying captured variable bindings and parent environment pointers
- Implement closure creation and application in an interpreter by storing and restoring the defining environment at call time
- Identify the loop-variable capture trap and explain why closures in loops capture a reference rather than a value
- Compare closures and objects as dual mechanisms for bundling state with behavior

With your team's language now underway from the *Language Design Workshop* kickoff, every thread of the semester knots together today: when a language with **first-class functions** and **static scope** lets a function escape the scope where it was born, the function must carry its birthplace with it, and what it carries is exactly the environment model you built in *Environments and Variable Storage*.  That bundle of code plus captured environment is a **closure**: the mechanism behind `make_adder`, behind every Church encoding, and behind the `FunDef` node your interpreter will support.

Arc: **the problem closures solve -> the mechanism drawn precisely -> closures in your interpreter -> the loop-variable trap -> objects vs closures**

> **Before You Begin:** This activity assumes you can:
> - Define what an environment (scope chain) is, and trace a simple variable lookup through nested scopes
> - Explain the difference between a value and a binding, and describe what it means for a variable to "go out of scope"
> - Read and write basic Python functions, including functions that define and return inner functions
>
> If any of these feel shaky, review the *Environments and Variable Storage* activity before continuing.

---

## Directions and Group Roles

Work in your POGIL team with your rotated roles (**Manager**, **Recorder**, **Presenter**, **Reflector**).  Please think each model through on your own first, then talk it over with your group.  The Recorder posts your answers to the Class Activity Questions discussion board, and the Presenter reports out wherever you disagreed or found another approach.  After class, please respond to the reflective prompt on your own in your notebook.

---

## Key Concepts

Here is a plain-English glossary of the terms this activity uses.  Please come back to this table whenever one of them starts to feel slippery.

| Term | Plain-English meaning | Why it matters |
|------|-----------------------|----------------|
| **Closure** | A function bundled with the environment where it was defined | The mechanism that lets a function remember variables after their scope ends |
| **First-class function** | A function treated as an ordinary value: stored, passed, returned | Without this, closures never arise; with it, they are unavoidable |
| **Defining environment** | The scope chain in effect at the moment a function is created | This is what the closure captures, never the caller's environment |
| **Capture by reference** | The closure holds a pointer to the *binding*, not a snapshot of the value | Explains why closures see later changes, and the loop-variable trap |
| **Lexical (static) scope** | Names resolve where the function was *written* in the source | The rule Python, JavaScript, and Scheme use; implemented by one parent-pointer choice |
| **Dynamic scope** | Names resolve in whoever *called* the function | The historical alternative; a contrast that shows what lexical scope buys |
| **Environment diagram** | Boxes for scopes, arrows for parent and capture pointers | The picture that makes every closure question answerable |
| **Loop-variable trap** | All closures made in a loop share one binding, so all see its final value | The most famous closure bug in Python and JavaScript alike |
| **Factory function** | A function whose every call creates a fresh scope and returns a closure over it | The standard fix for the trap, and the pattern behind `make_adder` |
| **Mutable cell / `nonlocal`** | The way an inner function assigns into a captured binding | How closures hold changing *state*, not just constants |

---

# Part I: The Problem and the Mechanism

Imagine hiring a contractor who was trained in your workshop.  After the workshop closes, the contractor still knows all its tools and rules; they carry that knowledge with them wherever they go.  In the same way, a function defined inside another function "remembers" the variables from its birth environment even after the enclosing function has returned.  This section shows the classic `make_adder` example that demonstrates why this behavior is necessary and useful.

## 1.  A Function Outlives Its Scope

```python
def make_adder(n):
    def adder(x):
        return x + n
    return adder

add5  = make_adder(5)
add10 = make_adder(10)

print(f"add5(3)  = {add5(3)}")    # 8
print(f"add10(3) = {add10(3)}")   # 13

# make_adder has RETURNED, yet n=5 and n=10 still live somewhere.
# Where?
print(f"add5's closure cells: {add5.__closure__[0].cell_contents}")
print(f"add10's closure cells: {add10.__closure__[0].cell_contents}")
```
@LIA.eval(`["main.py"]`, `none`, `python3 main.py`)

By the lifetime rules of the environments module, `make_adder`'s local scope should die at `return`, taking `n` with it; yet `add5` still finds `n = 5`.  The resolution: **a function value is not just code; it is a closure**, a pair of `(code, defining_environment)`.  When `adder` was created, it captured a reference to the environment where `n` was bound.  That environment survives because the closure still points to it: lifetime follows reachability.

$$\text{closure} = \langle \text{params}, \text{body}, E_{\text{def}} \rangle$$

Calling a closure resurrects its birthplace.  The call `add5(10)` creates a fresh environment for the parameter (`x = 10`) whose **parent is the closure's captured environment** (where `n = 5`), not the caller's.  This is static scoping enforced at runtime, the entire difference between lexical and dynamic scope, implemented in one decision about which parent pointer to use.

**Critical Thinking Questions (CTQs)**

> **CTQ 1.1** Draw the environment diagram at `print(add5(3))`: the global frame, the still-alive `make_adder` frame holding `n = 5`, the call frame holding `x = 3`, and every parent arrow.  Which arrow embodies "static scope"?

> **CTQ 1.2** After `add5 = make_adder(5)` and `add10 = make_adder(10)`, how many `make_adder` environments exist simultaneously?  What does each closure's captured pointer tell you about whether closures *copy* or *reference* their environment?

> **CTQ 1.3** In the lambda calculus, `(λn. λx. x + n) 5` reduces to `λx. x + 5` by *substitution*: the 5 is pasted into the body.  State the relationship: closures are an *implementation strategy* for what substitution *specifies*.  Why might an interpreter prefer environments over literal substitution for large function bodies?

---

Think of a closure like a security camera that watches a shelf, not a photograph of what is on the shelf right now.  When you look at the camera feed later, you see whatever is currently on the shelf, not what was there when the camera was installed.  This model shows that closures hold a live reference to a variable binding, so changes to that variable after the closure is created are visible through the closure.

> **Watch out!**  A common mistake is to think a closure *copies* the value of a variable at the moment the closure is created.  It does not: it captures a *reference* to the binding.  If the variable changes after the closure is defined, the closure will see the new value.  The `get_x` example below demonstrates this directly.

## Model 1: Closures Capture, Not Copy

```python
# CRITICAL: closures capture the VARIABLE BINDING, not the value at capture time

x = 10

def get_x():
    return x    # captures the variable x, not the value 10

print(f"get_x() = {get_x()}")   # 10

x = 99
print(f"After x=99, get_x() = {get_x()}")   # 99, the closure sees the new value!

# Contrast: a default argument captures the VALUE at definition time
def get_x_snapshot(val=x):
    return val

x = 42
print(f"get_x_snapshot() = {get_x_snapshot()}")   # 99, not 42, captured at def time

# Multiple closures sharing a mutable cell:
def make_counter():
    count = [0]   # list so we can mutate it (Python 2 workaround; Python 3 uses nonlocal)
    def increment():
        count[0] += 1
        return count[0]
    def reset():
        count[0] = 0
    return increment, reset

inc, rst = make_counter()
print(inc(), inc(), inc())   # 1 2 3
rst()
print(inc())                 # 1, both closures share the same count cell
```
@LIA.eval(`["main.py"]`, `none`, `python3 main.py`)

> **CTQ 1.4** `get_x()` returns 99 after `x = 99`.  What does this prove about whether closures copy or reference the captured binding?

> **CTQ 1.5** The `make_counter` example has TWO closures (`increment` and `reset`) that share ONE captured environment containing `count`.  Draw the environment diagram.  Which arrow makes them share state?

---

Imagine two employees: one always looks up rules in the company handbook where they were originally trained (lexical scope), and another asks whoever is currently standing next to them (dynamic scope).  Python uses the first approach: a function's variable lookups are always resolved against the environment where the function was *defined*, not the environment where it is *called*.  This model makes that contrast concrete.

> **Watch out!**  Students sometimes expect that calling a function from inside another function will let the called function "see" the caller's local variables.  This would be dynamic scope, and Python does *not* work that way.  The `show()` / `demo()` example below will surprise you if you carry this assumption in.

### Reading the Code

- The first block reassigns the captured variable *after* the closure is built, and the closure reports the new value.  That is the proof of capture-by-reference: if it had copied, it would still report the old one.
- The default-argument contrast is the control case.  `lambda v=n: v` evaluates `n` once, at definition, and stores the result.  It is not a closure over `n` at all.
- The shared-mutable-cell block is the same mechanism used deliberately: two functions closing over one binding is how you get an object with two methods, which is exactly where Part IV's koan goes.

### Try It Yourself

Find out, by experiment, exactly what Python keeps in a closure.

```python
def make():
    secret = "original"
    hidden  = "never used by the inner function"
    def peek():
        return secret            # only 'secret' is referenced
    def poke(v):
        nonlocal secret
        secret = v
    return peek, poke

peek, poke = make()
print("=== Capture is by reference, not by value ===")
print(f"  peek()          -> {peek()!r}")
poke("changed")
print(f"  after poke      -> {peek()!r}")

print("\n=== What is actually in the closure? ===")
names = peek.__code__.co_freevars
cells = [c.cell_contents for c in (peek.__closure__ or ())]
print(f"  peek captured: {dict(zip(names, cells))}")

# TODO 1: 'hidden' was in scope when peek was defined, but is it captured?
#         Look at the printed dict and say why or why not. What does that
#         tell you about what a closure costs in memory?

# TODO 2: peek and poke were made by the SAME call to make(). Print
#         poke.__closure__ too and compare the cell objects with
#         `peek.__closure__[0] is poke.__closure__[0]`. What does the
#         answer say about how they share state?

# TODO 3: call make() a second time and confirm the new peek is unaffected
#         by the old poke. How many 'secret' variables exist now?
```
@LIA.eval(`["main.py"]`, `none`, `python3 main.py`)

Expected output: `'original'`, then `'changed'`, then a dict with exactly one entry.  The absence of `hidden` from that dict is the answer to TODO 1.

## Model 2: Lexical vs. Dynamic Scope

```python
# Python uses LEXICAL (static) scope.
# Let's simulate what DYNAMIC scope would look like.

x = "global"

def show():
    print(f"show sees x = {x}")  # always sees x from DEFINING scope (global)

def demo():
    x = "demo"     # local x in demo's frame
    show()         # show() is NOT affected by demo's x

demo()  # prints "global", static scope: show sees the global x

# What dynamic scope would look like (manually simulated):
def show_dynamic(env):
    print(f"show_dynamic sees x = {env.get('x', 'not found')}")

def demo_dynamic():
    local_env = {'x': 'demo'}
    show_dynamic(local_env)   # show uses CALLER's environment

demo_dynamic()  # prints "demo", dynamic scope: show sees caller's x
```
@LIA.eval(`["main.py"]`, `none`, `python3 main.py`)

> **CTQ 2.1** Python's `show()` prints `"global"` even when called from `demo()` where `x = "demo"` is in scope.  Explain why, using the environment chain diagram.

> **CTQ 2.2** Early Lisp used dynamic scope by accident.  Under dynamic scope, `show_dynamic(local_env)` prints `"demo"`.  Write a scenario where dynamic scope causes a bug: a function `show_name()` that reads a variable `name` from the environment, and a caller that accidentally shadows `name` with a different value.

> **CTQ 2.3** The single decision that implements static scope in the evaluator is: when creating a closure, save the **defining environment**, not the calling environment.  Locate this decision in Model 3's `Call` branch in Part II; it is a single line, and the model runs the same program with it set both ways.

---


# Part II: Closures in Your Own Interpreter

## 2.  Theory: One Field, One Line

Everything above was Python showing you *its* closures.  Now build them.  The surprising part is how little it takes: a closure is a three-field record, and the entire static-versus-dynamic decision is one word in one line.

When the evaluator meets a function expression, it does **not** evaluate the body.  It packages three things and returns them:

```
Closure(param, body, env)
```

The `param` and `body` come straight off the AST.  The third field, `env`, is the environment **at the moment the function was created**.  That is the capture.

When the evaluator later meets a call, it evaluates the function, evaluates the argument, and then evaluates the body in

```
closure.env.extend(closure.param, argument)
```

Read that carefully, because it is the whole session.  The body runs in a child of the closure's **captured** environment, not a child of the environment the call happens to be sitting in.  Change `closure.env` to the caller's `env` on that one line and you have written a dynamically scoped language.  Nothing else has to change.

## Examples: Which Environment Wins, by Hand

Take this program and work out both answers before running anything:

```
let x = 10 in
let f = fun y -> x + y in
let x = 99 in
  f(1)
```

Fill in the table.  The only question that matters is which `x` the body of `f` sees.

| Rule | Which `x` does `f`'s body find | Result |
|------|-------------------------------|--------|
| Lexical: body runs in a child of `closure.env` | the `x` in scope where `fun` was written | ? |
| Dynamic: body runs in a child of the caller's `env` | the `x` in scope where `f(1)` was written | ? |

Now say which line of code you would change to move from one row to the other.  There is exactly one.

## Model 3: Build the Closure, Then Flip the Switch

This is a complete evaluator for a language with first-class functions.  The `LEXICAL` flag at the top selects which environment a call body runs in, and the *same* program is run under both settings.

```python
from dataclasses import dataclass
from typing import Any

@dataclass
class Num:  value: float
@dataclass
class Var:  name: str
@dataclass
class Add:  left: Any; right: Any
@dataclass
class Fun:  param: str; body: Any
@dataclass
class Call: fn: Any; arg: Any
@dataclass
class Let:  name: str; val: Any; body: Any

class Env:
    def __init__(self, bindings=None, parent=None):
        self.bindings = bindings or {}
        self.parent = parent
    def lookup(self, name):
        env = self
        while env is not None:
            if name in env.bindings:
                return env.bindings[name]
            env = env.parent
        raise NameError(f"undefined: {name!r}")
    def extend(self, name, value):
        return Env({name: value}, self)

@dataclass
class Closure:
    param: str
    body:  Any
    env:   Any          # <-- THE capture. Everything else is bookkeeping.

def interp(e, env, lexical):
    if isinstance(e, Num): return e.value
    if isinstance(e, Var): return env.lookup(e.name)
    if isinstance(e, Add): return interp(e.left, env, lexical) + interp(e.right, env, lexical)

    if isinstance(e, Fun):
        return Closure(e.param, e.body, env)        # capture the DEFINING env

    if isinstance(e, Let):
        v = interp(e.val, env, lexical)
        return interp(e.body, env.extend(e.name, v), lexical)

    if isinstance(e, Call):
        fn  = interp(e.fn,  env, lexical)
        arg = interp(e.arg, env, lexical)
        if not isinstance(fn, Closure):
            raise TypeError(f"not a function: {fn!r}")
        # ------------------------------------------------------------------
        # THE ONE LINE. fn.env is lexical scope; env is dynamic scope.
        base = fn.env if lexical else env
        # ------------------------------------------------------------------
        return interp(fn.body, base.extend(fn.param, arg), lexical)

    raise ValueError(f"unknown node: {type(e).__name__}")

#   let x = 10 in let f = fun y -> x + y in let x = 99 in f(1)
program = Let("x", Num(10),
          Let("f", Fun("y", Add(Var("x"), Var("y"))),
          Let("x", Num(99),
          Call(Var("f"), Num(1)))))

print("=== The same program, the same evaluator, one line different ===")
for lexical in (True, False):
    label = "lexical (fn.env)" if lexical else "dynamic (env)"
    print(f"  {label:20} -> {interp(program, Env(), lexical)}")

print("\n  11 means the body found the x that was in scope where 'fun' was")
print("     written. 100 means it found the x in scope at the call.")

# A second program, to show this is not a fluke of that one shape.
#   let n = 1 in
#   let bump = fun k -> n + k in
#   let n = 500 in bump(bump(0))
program2 = Let("n", Num(1),
           Let("bump", Fun("k", Add(Var("n"), Var("k"))),
           Let("n", Num(500),
           Call(Var("bump"), Call(Var("bump"), Num(0))))))

print("\n=== Nested calls, same switch ===")
for lexical in (True, False):
    label = "lexical" if lexical else "dynamic"
    print(f"  {label:20} -> {interp(program2, Env(), lexical)}")
```
@LIA.eval(`["main.py"]`, `none`, `python3 main.py`)

### Reading the Code

- The `Fun` branch is three words long and never touches the body.  A function value is *not* a running thing; it is a suspended thing plus the environment it was suspended in.
- `Closure.env` is the field CTQ 2.3 asks you to find.  It is filled in at `Fun`, read at `Call`, and never modified.
- `base = fn.env if lexical else env` is the entire scoping discipline of the language, on one line.  Everything students find hard about scope reduces to which of those two names you write there.
- `extend` returns a *new* `Env` rather than mutating.  That is what lets two calls to the same closure run without seeing each other's arguments, and it is why recursion works at all.
- Note that `Call` evaluates `fn` and `arg` in the *current* `env` under both settings.  Only the body's environment changes.  Getting that wrong gives a language where even the argument expression resolves strangely.

> **Watch out!**  It is tempting to store the *values* of the free variables in the closure instead of the environment: capture `x = 10` rather than a pointer to the frame holding `x`.  That works until something reassigns `x`, and then your closure is reading a stale copy while Python's would see the update.  Model 1 already showed the difference; this is where you either preserve it or lose it.

### Critical Thinking Questions

> **CTQ 3.1** Run the model and record all four numbers.  For the first program, which result is 11 and which is 100?  Explain each in one sentence using the words "defining" and "calling."

> **CTQ 3.2** `Closure` holds `env`, but `Env.extend` never copies bindings.  If some later statement reassigns `x` in the captured frame, does the closure see the new value or the old one?  Which of the two capture strategies from Model 1 does that make this?

> **CTQ 3.3** Recursion is not implemented anywhere in this evaluator, yet `bump(bump(0))` works.  What would you have to add for a function to call *itself* by name, and why is that harder than it looks?  (Hint: at the moment `Fun` runs, is the function's own name in `env` yet?)

> **CTQ 3.4** Write down what your team's language does, and put it in `SEMANTICS.md` as one sentence naming the environment a call body runs in.

### Try It Yourself

Add recursion, which is the thing the model above deliberately cannot do.

```python
from dataclasses import dataclass
from typing import Any

@dataclass
class Num:  value: float
@dataclass
class Var:  name: str
@dataclass
class Add:  left: Any; right: Any
@dataclass
class Mul:  left: Any; right: Any
@dataclass
class If0:  test: Any; then_e: Any; else_e: Any
@dataclass
class Fun:  param: str; body: Any
@dataclass
class Call: fn: Any; arg: Any
@dataclass
class Let:  name: str; val: Any; body: Any

class Env:
    def __init__(self, bindings=None, parent=None):
        self.bindings = bindings or {}
        self.parent = parent
    def lookup(self, name):
        env = self
        while env is not None:
            if name in env.bindings: return env.bindings[name]
            env = env.parent
        raise NameError(f"undefined: {name!r}")
    def extend(self, name, value):
        return Env({name: value}, self)

@dataclass
class Closure:
    param: str; body: Any; env: Any

def interp(e, env):
    if isinstance(e, Num): return e.value
    if isinstance(e, Var): return env.lookup(e.name)
    if isinstance(e, Add): return interp(e.left, env) + interp(e.right, env)
    if isinstance(e, Mul): return interp(e.left, env) * interp(e.right, env)
    if isinstance(e, If0):
        return interp(e.then_e, env) if interp(e.test, env) == 0 else interp(e.else_e, env)
    if isinstance(e, Fun):  return Closure(e.param, e.body, env)
    if isinstance(e, Let):
        v = interp(e.val, env)
        return interp(e.body, env.extend(e.name, v))
    if isinstance(e, Call):
        fn, arg = interp(e.fn, env), interp(e.arg, env)
        return interp(fn.body, fn.env.extend(fn.param, arg))
    raise ValueError(type(e).__name__)

#   let fact = fun n -> if0 n then 1 else n * fact(n - 1) in fact(5)
fact_body = If0(Var("n"),
                Num(1),
                Mul(Var("n"), Call(Var("fact"), Add(Var("n"), Num(-1)))))
program = Let("fact", Fun("n", fact_body), Call(Var("fact"), Num(5)))

try:
    print(f"  fact(5) = {interp(program, Env())}")
except NameError as err:
    print(f"  fact(5) -> NameError: {err}")
    print("  The closure captured env BEFORE 'fact' was bound into it,")
    print("  so the body cannot see its own name.")

# TODO 1: fix it. The trick has a name: tie the knot. After building the
#         Closure for fact, reach into the closure's captured environment
#         and define "fact" to point at the closure itself.
#         Two lines, and fact(5) prints 120.
#
# TODO 2: having done that, draw the environment. It now contains a
#         pointer to a closure whose env is that same environment. What
#         is that structure called, and what does it mean for the garbage
#         collector?
#
# TODO 3: most real languages give recursion its own form (letrec, or a
#         'def' statement) rather than making the programmer tie the knot.
#         Which does your language do, and why?
```
@LIA.eval(`["main.py"]`, `none`, `python3 main.py`)

Expected output as written: a `NameError` naming `fact`, with the explanation.  Once TODO 1 is in, `fact(5) = 120`.  That two-line fix is the whole reason `letrec` exists.

---

# Part III: The Loop-Variable Trap

The loop-variable trap is one of the most famous beginner bugs in Python and JavaScript alike.  Imagine handing every worker in a factory floor the *same* whiteboard marker and telling them to write down the current job number.  By the time they all pick up the marker to write, the job number has moved on to the last value; they all write the same thing.  This is exactly what happens when closures in a loop all capture the same variable binding instead of their own private copy.

> **Watch out!**  When you write `[lambda: i for i in range(3)]`, all three lambdas capture *one* variable `i`, the same loop variable.  By the time any of them is called, the loop has finished and `i` is `2`.  This is not a bug in Python; it is the correct behavior of reference capture.  The two fixes shown (default argument and factory function) both work by creating a separate binding per iteration.

## 3.  The Famous Python Bug

```python
# The loop-variable trap, every Python programmer falls into this once
fns = [lambda: i for i in range(3)]
print("Results:", [f() for f in fns])     # [2, 2, 2], not [0, 1, 2]!

# Why? All three lambdas captured the SAME binding of 'i'.
# By the time they're called, i == 2.
print("i after loop:", end=" ")
try:
    print(i)  # i still exists after the loop! (Python scoping quirk)
except NameError:
    print("not available")

# Fix 1: default argument captures VALUE at definition time
fns_fixed1 = [lambda i=i: i for i in range(3)]
print("Fix 1 (default arg):", [f() for f in fns_fixed1])   # [0, 1, 2]

# Fix 2: factory function creates a new scope per iteration
def make_fn(i):
    return lambda: i

fns_fixed2 = [make_fn(i) for i in range(3)]
print("Fix 2 (factory):", [f() for f in fns_fixed2])   # [0, 1, 2]

# The lesson: each iteration needs its OWN binding, not a shared one
# JavaScript's 'let' fixed this at the ecosystem scale (was 'var' before)
```
@LIA.eval(`["main.py"]`, `none`, `python3 main.py`)

> **CTQ 6.1** All three lambdas captured the same `i` binding.  After the loop, what is `i`?  Why do all three lambdas return 2?

> **CTQ 6.2** Fix 1 uses `lambda i=i: i`.  The outer `i` (the default argument value) is evaluated at *definition time*, capturing the current value.  Why does this work, while the capture in the original version doesn't?

> **CTQ 6.3** Fix 2 uses a factory function `make_fn(i)` that creates a new scope.  Draw the environment diagram showing why each returned lambda has a *different* captured environment.

> **CTQ 6.4** JavaScript's historic `var` scoping caused the same bug; `let` was introduced to fix it.  How does `let` create "per-iteration" scope?  Why can't `var` do this?

---

The code above showed the trap and two fixes; now draw it.  The broken and fixed versions differ by exactly one thing (how many environment boxes exist) and the box diagram makes the bug visible at a glance.

### Reading the Code

- `[lambda: i for i in range(3)]` builds three functions that all close over the *same* `i`.  Nothing about that is a bug; it is capture-by-reference doing exactly what Model 1 demonstrated on purpose.
- The two fixes attack different halves.  The default argument stops closing over `i` at all, so there is nothing to share.  The factory function makes a genuinely new binding per iteration, so there are three `i`s to close over instead of one.
- JavaScript's `var` had this exact shape and `let` changed it by giving loop bodies per-iteration bindings.  That is the same decision you made in the *Environments* Try It Yourself, at ecosystem scale.

### Try It Yourself

Predict, then check, which of these five loops has the trap.

```python
def factory(v):
    return lambda: v

print("=== Five loops. Which give [0, 1, 2]? ===")

a = [lambda: i for i in range(3)]
b = [lambda i=i: i for i in range(3)]
c = [factory(i) for i in range(3)]
d = []
for i in range(3):
    d.append(lambda: i)
e = []
for i in range(3):
    e.append(factory(i))

# TODO: predict all five BEFORE running. Write your predictions down.
for name, fns in [("a  comprehension, bare lambda", a),
                  ("b  comprehension, default arg", b),
                  ("c  comprehension, factory    ", c),
                  ("d  for-loop, bare lambda     ", d),
                  ("e  for-loop, factory         ", e)]:
    print(f"  {name} -> {[f() for f in fns]}")

print("\nTwo of these share one binding and three do not.")
print("For each, say WHERE the per-iteration binding comes from,")
print("or why there isn't one.")
```
@LIA.eval(`["main.py"]`, `none`, `python3 main.py`)

Expected output: `a` and `d` give `[2, 2, 2]`; `b`, `c`, and `e` give `[0, 1, 2]`.  If you predicted the comprehension and the for-loop would differ, note that they do not: the comprehension's scope is not what saves you.

## Model 5: The Loop Trap, Drawn as Boxes

**Broken:** `fns = [lambda: i for i in range(3)]`.  The comprehension runs in a single scope, so there is exactly **one** box holding `i`, and every lambda's capture arrow points at it:

```
        +----------------------------+
        | comprehension scope        |
        |   i = 2   (final value)    |
        +----------------------------+
             ^         ^         ^
             |         |         |
           lam0      lam1      lam2
   three closures, ONE shared box: all see i = 2 at call time
```

**Fixed (factory):** `fns = [make_fn(i) for i in range(3)]`.  Each *call* to `make_fn` creates a fresh box, and each lambda captures its own:

```
   +-----------+   +-----------+   +-----------+
   | E0: i = 0 |   | E1: i = 1 |   | E2: i = 2 |
   +-----------+   +-----------+   +-----------+
        ^               ^               ^
        |               |               |
      lam0            lam1            lam2
   three closures, three boxes: one binding per closure
```

The broken version's history as a timeline: the trap is a *timing* bug, because capture is by reference and the calls happen after the last write:

| Loop step | Shared box's `i` | Closures created so far | What each would return *if called now* |
|-----------|------------------|-------------------------|----------------------------------------|
| iteration 0 | 0 | lam0 | lam0 -> 0 |
| iteration 1 | 1 | lam0, lam1 | both -> 1 |
| iteration 2 | 2 | lam0, lam1, lam2 | all -> 2 |
| after the loop (calls happen here) | 2 | all three | **all -> 2** |

```python
# Evidence for the diagrams: inspect the closure cells directly
broken = [lambda: i for i in range(3)]
print("broken results:", [f() for f in broken])
print("one shared box?",
      broken[0].__closure__[0] is broken[1].__closure__[0] is broken[2].__closure__[0])

def make_fn(i):
    return lambda: i

fixed = [make_fn(i) for i in range(3)]
print("\nfixed results:", [f() for f in fixed])
print("distinct boxes?",
      fixed[0].__closure__[0] is not fixed[1].__closure__[0])
print("each box's contents:", [f.__closure__[0].cell_contents for f in fixed])

# Fix 1 (default argument) is different again: no closure at all
fix1 = [lambda i=i: i for i in range(3)]
print("\nfix1 results:", [f() for f in fix1])
print("fix1 closures:", [f.__closure__ for f in fix1])   # [None, None, None]
```
@LIA.eval(`["main.py"]`, `none`, `python3 main.py`)

`fns = [lambda: i for i in range(3)]` yields functions that all return 2, and `fns[0].__closure__[0] is fns[1].__closure__[0]` prints `True`.  Together these show:

[( )] The lambdas were compiled to the same code object, which forces one result
[(X)] All three closures captured the very same binding (cell) for `i`, whose final value is 2
[( )] Python evaluates lambda bodies eagerly at definition time
[( )] The list comprehension copied the last lambda three times

**Critical Thinking Questions (CTQs)**

> **CTQ 7.1** Which single line of the cell's output is direct evidence for the "three arrows, one box" picture?  Which line is evidence for "three boxes"?

> **CTQ 7.2** In the fixed diagram, what act creates each new box: the `lambda` *definition*, or the *call* to `make_fn`?  Justify your answer with the environment-creation rule from Part II (`eval_call` builds a new environment per call).

> **CTQ 7.3** Fix 1's lambdas report `__closure__ = None`; they are not closures at all.  Where does each one's `i` live instead, and why does that location make capture unnecessary?

---

Two closures created by separate calls to `make_adder(5)` and `make_adder(3)` return different results for the same input because:

[( )] The function body's code differs between them
[(X)] Each closure captured a different defining environment in which `n` is bound to a different value
[( )] Python caches the most recent return value
[( )] Closures copy the global environment at call time

---

**In-class work stops here.**  Everything below is homework and going-deeper material: attempt the exercises before the related assignment.

# Extension: Closures vs. Objects

At first glance, objects and closures look very different: one is a class instance with named fields; the other is a function bundled with hidden environment variables.  But look closer and you will find they are two sides of the same coin.  Both bundle state with behavior; both control which code can reach that state.  This model encodes a counter two ways, side-by-side, so you can see the structural parallel directly.

> **Watch out!**  Closures are not limited to functional languages.  Python, JavaScript, Ruby, and even Java (via lambdas) all have closures.  A common misconception is that "closures = Haskell/Scheme only."  In modern JavaScript, closures are used every time you write a callback, event handler, or `useEffect` hook in React.

## 4.  The Koan: Closures Are Poor Man's Objects

The famous koan: "Closures are a poor man's objects; objects are a poor man's closures."  They are dual.

```python
# Objects approach: counter using a class
class Counter:
    def __init__(self, start=0):
        self._count = start
    def increment(self):
        self._count += 1
        return self._count
    def reset(self):
        self._count = 0
    def value(self):
        return self._count

# Closures approach: counter using closures (no class!)
def make_counter(start=0):
    count = [start]   # mutable cell
    return {
        'increment': lambda: (count.__setitem__(0, count[0] + 1), count[0])[1],
        'reset':     lambda: count.__setitem__(0, 0),
        'value':     lambda: count[0],
    }

obj_counter = Counter(0)
clo_counter = make_counter(0)

obj_counter.increment(); obj_counter.increment()
print(f"Object counter: {obj_counter.value()}")

clo_counter['increment'](); clo_counter['increment']()
print(f"Closure counter: {clo_counter['value']()}")

# Both share mutable state via different mechanisms:
# Object: self._count (field in object's dictionary)
# Closure: count (binding in captured environment)
# They are structurally dual.
```
@LIA.eval(`["main.py"]`, `none`, `python3 main.py`)

> **CTQ 8.1** In the closure-based counter, `count` is a shared mutable cell.  In the object-based counter, `self._count` is a field.  What is the structural difference?  What is the conceptual difference?

> **CTQ 8.2** The closure counter uses a list `[start]` to work around Python's scoping rules for `nonlocal`.  Rewrite it using `nonlocal count` (Python 3) instead of a list.  Why is `nonlocal` cleaner?

> **CTQ 8.3** Languages like OCaml and Haskell have closures but no classes.  Languages like Java (pre-lambda) have classes but no closures (lambdas are objects).  From what you now know about the implementation of each, argue: which is more fundamental?

---

# Check Your Understanding

A closure is created when the evaluator meets a function expression. What does it store?

[(X)] The parameter, the unevaluated body, and the environment in force at that moment
[( )] The parameter, the body, and the values of every free variable, copied out
[( )] The fully evaluated body, ready to return on the next call
[( )] Only the body; the environment is looked up again at call time

---

In Model 3, changing `base = fn.env` to `base = env` in the `Call` branch turns the language from lexically scoped to dynamically scoped. Why is that one line enough?

[(X)] It is the only place the body's environment is chosen; everything else already threads environments unchanged
[( )] It also changes how `Fun` captures, because the two share a reference
[( )] It changes name lookup, which is what scope means
[( )] It is not enough; `Env.lookup` must change too

---

`fact(5)` raises `NameError` in the Try It Yourself because:

[(X)] The closure captured the environment *before* `fact` was bound into it, so the body cannot see its own name
[( )] Recursion requires a stack, which the evaluator does not have
[( )] `If0` evaluates both branches, so it never terminates
[( )] `Let` does not extend the environment

---

`[lambda: i for i in range(3)]` returns three functions that all print `2`. This is because:

[(X)] All three closed over the same binding of `i`, and by call time it holds the loop's final value
[( )] Python evaluates lambdas lazily and only the last one survives
[( )] List comprehensions reuse one function object
[( )] `range(3)` is exhausted before the lambdas run

---

## Exercises

### Exercise 1: Integrate Closures into Mini (30 min)

Add closures to your Mini interpreter:
1.  Add `FunDef(name, params, body)` and `Call(callee, args)` AST nodes
2.  In the parser, add `fun name(params) { body }` syntax and `name(args)` call syntax
3.  In the evaluator, implement `execute_fundef` (create closure, bind name) and `eval_call` (create child env, run body, catch ReturnSignal)
4.  Demonstrate: a plain function, `factorial(5)`, and `make_adder` working in your language

### Exercise 2: Counter Objects (15 min)

Build `make_counter()` using closures (not a class) that returns an increment function.  Then build `make_account(balance)` with `deposit(amount)` and `withdraw(amount)` methods.  Demonstrate shared state between the two returned functions.

### Exercise 3: Trap Tour (15 min)

Reproduce the loop-variable trap in your language (or Python), apply both fixes, and explain each fix's mechanism with environment diagrams.

### Exercise 4: Scope Flip Experiment (20 min)

Apply the one-token change from CTQ 3.1 to make your interpreter dynamically scoped.  Rerun the `show`/`demo` program from the *Binding and Scope* activity.  Report the output difference and explain with a diagram which environment chain the dynamically scoped version follows.

---

## Reflection Prompt

A closure carries its context everywhere, so it always means what it meant at home.  Dynamically scoped code means whatever its surroundings currently impose.  People can resemble both: some carry their context everywhere; others adapt to whoever is calling.  When has carrying your own context served you, and when has adapting to the caller been the wiser semantics?

---

## Further Reading

- **"Crafting Interpreters"**, Robert Nystrom, "Functions" and "Closures" chapters (online, free): our exact implementation, then optimized
- **SICP Section 3.2**, Abelson & Sussman: the environment model of evaluation
- **"The Art of the Interpreter"**, Steele & Sussman (1978): closures invented and explained
- **Python `__closure__`**, CPython exposes closures via `fn.__closure__`: introspect live closures
- **JavaScript `let` vs `var`**, MDN: the real-world consequence of the loop-variable trap at ecosystem scale


## Going Further (at home)

The core lesson above stands on its own.  Two full self-paced tutorials extend today's mechanism into runtime territory that feeds the Interpreter assignment's extensions and the team project:

- [Coroutines and Generators: Pausable Computation](https://www.billmongan.com/Ursinus-CS374-Fall2026/Tutorials/CoroutinesAndGenerators): how `yield` freezes a stack frame, how `async`/`await` desugars to a state machine, and how to add generator objects to your interpreter
- [Error Handling: From Return Codes to Algebraic Effects](https://www.billmongan.com/Ursinus-CS374-Fall2026/Tutorials/ErrorHandling): return codes, exceptions, Option/Maybe, Result/Either, and designing error propagation for your interpreter

---

Closures complete the environment story your Interpreter assignment depends on.  Next, the *Modern Language Features* activity surveys how today's languages package these mechanics, and your team carries both into the sprint studios.
