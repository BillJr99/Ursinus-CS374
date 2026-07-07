<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://github.com/BillJr99/Ursinus-CS374-Fall2026/blob/gh-pages/_pages/Activities/liascript-closures.md

import: https://raw.githubusercontent.com/liascript/CodeRunner/master/README.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

# Closures and First-Class Functions

Have you ever wondered how a function can "remember" a value from a context that no longer exists? Think of a closure like a letter that carries its own envelope: even after the post office (the enclosing scope) closes for the day, the letter still knows exactly where it came from. Closures are the mechanism that makes callbacks, iterators, and the entire functional-programming style of JavaScript, Python, and Scheme possible — understanding them means understanding how scope and state really work at runtime.

## Learning Goals

By the end of this activity, you will be able to:

- Define a closure as a pair of code and its defining environment, and explain why it is necessary in a language with first-class functions and static scope
- Trace environment diagrams for closure creation and invocation, identifying captured variable bindings and parent environment pointers
- Implement closure creation and application in an interpreter by storing and restoring the defining environment at call time
- Identify the loop-variable capture trap and explain why closures in loops capture a reference rather than a value
- Compare closures and objects as dual mechanisms for bundling state with behavior

Every thread of the semester knots together today: when a language with **first-class functions** and **static scope** lets a function escape the scope where it was born, the function must carry its birthplace with it. That bundle of code plus captured environment is a **closure** — the mechanism behind `make_adder`, behind every Church encoding, and behind the `FunDef` node your interpreter will support.

Arc: **the problem closures solve → the mechanism drawn precisely → closures in your interpreter → the loop-variable trap → objects vs closures**

> **Before You Begin:** This activity assumes you can:
> - Define what an environment (scope chain) is, and trace a simple variable lookup through nested scopes
> - Explain the difference between a value and a binding, and describe what it means for a variable to "go out of scope"
> - Read and write basic Python functions, including functions that define and return inner functions
>
> If any of these feel shaky, review the Environments and Scope module before continuing.

---

## Directions and Group Roles

Work in your POGIL team with rotated roles (**Manager**, **Recorder**, **Presenter**, **Reflector**). Consider each model individually first, then discuss with your group.

---

## Key Concepts

Before diving in, here is a plain-English glossary of the terms this activity uses. Return to this table whenever a term feels slippery.

| Term | Plain-English meaning | Why it matters |
|------|-----------------------|----------------|
| **Closure** | A function bundled with the environment where it was defined | The mechanism that lets a function remember variables after their scope ends |
| **First-class function** | A function treated as an ordinary value: stored, passed, returned | Without this, closures never arise; with it, they are unavoidable |
| **Defining environment** | The scope chain in effect at the moment a function is created | This is what the closure captures — never the caller's environment |
| **Capture by reference** | The closure holds a pointer to the *binding*, not a snapshot of the value | Explains why closures see later changes — and the loop-variable trap |
| **Lexical (static) scope** | Names resolve where the function was *written* in the source | The rule Python, JavaScript, and Scheme use; implemented by one parent-pointer choice |
| **Dynamic scope** | Names resolve in whoever *called* the function | The historical alternative; a contrast that shows what lexical scope buys |
| **Environment diagram** | Boxes for scopes, arrows for parent and capture pointers | The picture that makes every closure question answerable |
| **Loop-variable trap** | All closures made in a loop share one binding, so all see its final value | The most famous closure bug in Python and JavaScript alike |
| **Factory function** | A function whose every call creates a fresh scope and returns a closure over it | The standard fix for the trap, and the pattern behind `make_adder` |
| **Mutable cell / `nonlocal`** | The way an inner function assigns into a captured binding | How closures hold changing *state*, not just constants |

---

# Part I: The Problem and the Mechanism

Imagine hiring a contractor who was trained in your workshop. After the workshop closes, the contractor still knows all its tools and rules — they carry that knowledge with them wherever they go. In the same way, a function defined inside another function "remembers" the variables from its birth environment even after the enclosing function has returned. This section shows the classic `make_adder` example that demonstrates why this behavior is necessary and useful.

## 1. A Function Outlives Its Scope

```python  liascript
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
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

By the lifetime rules of the environments module, `make_adder`'s local scope should die at `return`, taking `n` with it — yet `add5` still finds `n = 5`. The resolution: **a function value is not just code; it is a closure**, a pair of `(code, defining_environment)`. When `adder` was created, it captured a reference to the environment where `n` was bound. That environment survives because the closure still points to it — lifetime follows reachability.

$$\text{closure} = \langle \text{params}, \text{body}, E_{\text{def}} \rangle$$

**Calling a closure resurrects its birthplace.** The call `add5(10)` creates a fresh environment for the parameter (`x = 10`) whose **parent is the closure's captured environment** (where `n = 5`), not the caller's. This is static scoping enforced at runtime — the entire difference between lexical and dynamic scope, implemented in one decision about which parent pointer to use.

**Critical Thinking Questions (CTQs)**

> **CTQ 1.1** Draw the environment diagram at `print(add5(3))`: the global frame, the still-alive `make_adder` frame holding `n = 5`, the call frame holding `x = 3`, and every parent arrow. Which arrow embodies "static scope"?

> **CTQ 1.2** After `add5 = make_adder(5)` and `add10 = make_adder(10)`, how many `make_adder` environments exist simultaneously? What does each closure's captured pointer tell you about whether closures *copy* or *reference* their environment?

> **CTQ 1.3** In the lambda calculus, `(λn. λx. x + n) 5` reduces to `λx. x + 5` by *substitution* — the 5 is pasted into the body. State the relationship: closures are an *implementation strategy* for what substitution *specifies*. Why might an interpreter prefer environments over literal substitution for large function bodies?

---

Think of a closure like a security camera that watches a shelf, not a photograph of what is on the shelf right now. When you look at the camera feed later, you see whatever is currently on the shelf — not what was there when the camera was installed. This model shows that closures hold a live reference to a variable binding, so changes to that variable after the closure is created are visible through the closure.

> **Watch out!** A common mistake is to think a closure *copies* the value of a variable at the moment the closure is created. It does not — it captures a *reference* to the binding. If the variable changes after the closure is defined, the closure will see the new value. The `get_x` example below demonstrates this directly.

## Model 1: Closures Capture, Not Copy

```python  liascript
# CRITICAL: closures capture the VARIABLE BINDING, not the value at capture time

x = 10

def get_x():
    return x    # captures the variable x, not the value 10

print(f"get_x() = {get_x()}")   # 10

x = 99
print(f"After x=99, get_x() = {get_x()}")   # 99 — the closure sees the new value!

# Contrast: a default argument captures the VALUE at definition time
def get_x_snapshot(val=x):
    return val

x = 42
print(f"get_x_snapshot() = {get_x_snapshot()}")   # 99, not 42 — captured at def time

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
print(inc())                 # 1 — both closures share the same count cell
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

> **CTQ 1.4** `get_x()` returns 99 after `x = 99`. What does this prove about whether closures copy or reference the captured binding?

> **CTQ 1.5** The `make_counter` example has TWO closures (`increment` and `reset`) that share ONE captured environment containing `count`. Draw the environment diagram. Which arrow makes them share state?

---

Imagine two employees: one always looks up rules in the company handbook where they were originally trained (lexical scope), and another asks whoever is currently standing next to them (dynamic scope). Python uses the first approach — a function's variable lookups are always resolved against the environment where the function was *defined*, not the environment where it is *called*. This model makes that contrast concrete.

> **Watch out!** Students sometimes expect that calling a function from inside another function will let the called function "see" the caller's local variables. This would be dynamic scope, and Python does *not* work that way. The `show()` / `demo()` example below will surprise you if you carry this assumption in.

## Model 2: Lexical vs. Dynamic Scope

```python  liascript
# Python uses LEXICAL (static) scope.
# Let's simulate what DYNAMIC scope would look like.

x = "global"

def show():
    print(f"show sees x = {x}")  # always sees x from DEFINING scope (global)

def demo():
    x = "demo"     # local x in demo's frame
    show()         # show() is NOT affected by demo's x

demo()  # prints "global" — static scope: show sees the global x

# What dynamic scope would look like (manually simulated):
def show_dynamic(env):
    print(f"show_dynamic sees x = {env.get('x', 'not found')}")

def demo_dynamic():
    local_env = {'x': 'demo'}
    show_dynamic(local_env)   # show uses CALLER's environment

demo_dynamic()  # prints "demo" — dynamic scope: show sees caller's x
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

> **CTQ 2.1** Python's `show()` prints `"global"` even when called from `demo()` where `x = "demo"` is in scope. Explain why, using the environment chain diagram.

> **CTQ 2.2** Early Lisp used dynamic scope by accident. Under dynamic scope, `show_dynamic(local_env)` prints `"demo"`. Write a scenario where dynamic scope causes a bug: a function `show_name()` that reads a variable `name` from the environment, and a caller that accidentally shadows `name` with a different value.

> **CTQ 2.3** The single decision that implements static scope in the evaluator is: when creating a closure, save the **defining environment**, not the calling environment. Locate this decision in the closure code in Part II.

---

# Part II: Closures in Your Interpreter

Building an interpreter that supports closures requires translating the abstract idea ("a function carries its birth environment") into concrete data structures. Think of it like building a passport system: when a function is created, you stamp its passport with the environment it was born in; when it is called later, you open a new room that is connected back to that stamped environment, not to wherever the function happens to be called from. This section shows exactly how `Environment`, `Closure`, and `eval_call` work together to implement that passport stamp.

## 2. Twenty Lines to First-Class Functions

Adding closures to Mini requires:
1. A `FunDef` node and a `Call` node from the parser
2. A `Closure` value created at **definition time**, capturing the *current* environment
3. A call rule that builds the new environment parented on the **closure's captured environment**

```python  liascript
# Closure-based interpreter for Mini (simplified)

class Environment:
    def __init__(self, parent=None):
        self._vars = {}
        self.parent = parent

    def define(self, name, value):
        self._vars[name] = value

    def lookup(self, name):
        if name in self._vars:
            return self._vars[name]
        if self.parent is not None:
            return self.parent.lookup(name)
        raise NameError(f"Undefined: {name}")

    def assign(self, name, value):
        if name in self._vars:
            self._vars[name] = value
        elif self.parent is not None:
            self.parent.assign(name, value)
        else:
            raise NameError(f"Undefined: {name}")

class Closure:
    def __init__(self, params, body, env):
        self.params = params
        self.body   = body
        self.env    = env   # THE CAPTURED ENVIRONMENT — static scope lives here

class ReturnSignal(Exception):
    def __init__(self, value): self.value = value

def execute_fundef(name, params, body, env):
    """Create a closure and bind it to name in env."""
    closure = Closure(params, body, env)   # capture env HERE
    env.define(name, closure)

def eval_call(callee_val, arg_vals, evaluate_body, env):
    """Call a closure with evaluated argument values."""
    fn = callee_val
    if not isinstance(fn, Closure):
        raise TypeError(f"Not callable: {fn!r}")
    if len(arg_vals) != len(fn.params):
        raise TypeError(f"Expected {len(fn.params)} args, got {len(arg_vals)}")
    # *** THE ONE LINE THAT CHOOSES LEXICAL SCOPE ***
    local = Environment(parent=fn.env)   # parent = DEFINING env, not calling env!
    for name, val in zip(fn.params, arg_vals):
        local.define(name, val)
    try:
        evaluate_body(fn.body, local)
    except ReturnSignal as r:
        return r.value
    return None

# -----------------------------------------------------------------------
# STEP-BY-STEP TRACE: what happens when we define and call make_adder(5)
#
# Step 1 (DEFINITION — execute_fundef called):
#   current env = global_env  { }
#   closure = Closure(params=["n"], body=..., env=global_env)
#   global_env.define("make_adder", closure)
#   Result: global_env = { make_adder -> <Closure env=global_env> }
#
# Step 2 (CALL make_adder(5) — eval_call called):
#   fn       = global_env.lookup("make_adder")  -> the Closure from Step 1
#   arg_vals = [5]
#   local    = Environment(parent=fn.env)        # parent = global_env (lexical!)
#   local.define("n", 5)
#   Result: local = { n -> 5, parent -> global_env }
#   evaluate_body runs and creates the inner 'adder' closure:
#     inner_closure = Closure(params=["x"], body=..., env=local)  # captures local!
#     local.define("adder", inner_closure)
#     ReturnSignal(inner_closure) raised and caught
#   eval_call returns inner_closure
#
# Step 3 (CALL add5(3), where add5 = inner_closure from Step 2):
#   fn       = add5  (inner_closure, env=local where n=5)
#   arg_vals = [3]
#   call_env = Environment(parent=fn.env)   # parent = local (n=5), NOT global!
#   call_env.define("x", 3)
#   body evaluates x + n:
#     call_env.lookup("x") -> 3 (found in call_env)
#     call_env.lookup("n") -> not in call_env -> tries parent (local) -> 5
#   return 3 + 5 = 8  ✓
#
# The key: Step 3 uses fn.env (local, where n=5) as parent, NOT the caller's env.
# That single parent= choice IS lexical scope.
# -----------------------------------------------------------------------

# Demo: make_adder in this closure system
global_env = Environment()

execute_fundef("make_adder", ["n"],
    # body: return lambda x: x + n  (simulated as a nested closure)
    [("fundef", "adder", ["x"], [("return", ("add", ("var", "x"), ("var", "n")))])],
    global_env)

# Verify the closure was created and captured the right env
ma = global_env.lookup("make_adder")
print(f"make_adder is a Closure: {isinstance(ma, Closure)}")
print(f"make_adder captured env has 'make_adder': {'make_adder' in ma.env._vars}")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

**CTQs**

> **CTQ 3.1** Find the single line `local = Environment(parent=fn.env)` that decides static-versus-dynamic scope. Write the one-token change that would make your language dynamically scoped. (Hint: what if you used `env` instead of `fn.env`?)

> **CTQ 3.2** Arguments are evaluated in `env` (the caller's environment) but bound in `local` (parented on the *definer's* environment). Construct a program where these two environments differ and where confusing them would change the output.

> **CTQ 3.3** `ReturnSignal` rides an exception out of nested blocks to the call boundary. What would happen if `eval_call` caught *all* exceptions rather than only `ReturnSignal`?

---

For a function to call itself recursively, it must be able to look up its own name at the moment it runs. This is not automatic — it requires the function's name to be bound in the environment *before* the function body executes. Think of it like a business that must be registered with the government before it can issue contracts referencing itself. This model shows the precise ordering: bind the name first, then use the closure, so that recursive lookup through the captured environment succeeds.

## Model 3: Closures Enable Recursion

```python  liascript
# Recursion requires the function to see itself in its own closure.
# execute_fundef binds the name BEFORE returning, so:

class Environment:
    def __init__(self, parent=None):
        self._vars = {}
        self.parent = parent
    def define(self, name, val):   self._vars[name] = val
    def lookup(self, name):
        if name in self._vars: return self._vars[name]
        if self.parent: return self.parent.lookup(name)
        raise NameError(name)

class Closure:
    def __init__(self, params, body_fn, env):
        self.params = params; self.body_fn = body_fn; self.env = env
    def __call__(self, *args):
        local = Environment(parent=self.env)
        for p, a in zip(self.params, args):
            local.define(p, a)
        return self.body_fn(local)

global_env = Environment()

# Define factorial using our closure mechanism
# fact(n) = if n <= 0 then 1 else n * fact(n-1)
def fact_body(env):
    n = env.lookup('n')
    if n <= 0: return 1
    return n * env.lookup('fact')(n - 1)   # looks up 'fact' via captured env!

fact_closure = Closure(['n'], fact_body, global_env)
global_env.define('fact', fact_closure)    # bind BEFORE any calls

print(f"fact(0) = {global_env.lookup('fact')(0)}")
print(f"fact(5) = {global_env.lookup('fact')(5)}")
print(f"fact(10) = {global_env.lookup('fact')(10)}")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

> **CTQ 4.1** `execute_fundef` defines the name in the *current* environment before any calls. When `fact_body` runs and looks up `'fact'`, it finds the closure in `global_env`. Trace the environment chain: call frame → captured `global_env` → finds `fact`. What would break if we didn't define the name until after creating the closure?

> **CTQ 4.2** `make_adder` creates a new closure for each call. `fact` is a single closure that calls itself. Draw the environment chain for `fact(3)` calling `fact(2)` calling `fact(1)` calling `fact(0)`. How deep does the chain grow?

---

Every closure question becomes answerable the moment you draw the boxes. Here we take the classic **counter factory** — the "hello world" of stateful closures — and draw every environment box and arrow it creates, then verify the picture by peeking at Python's actual closure cells.

## Model 4: The Counter Factory, Drawn as Environment Boxes

**Worked example.** Trace this program by hand before running anything:

```python
def make_counter():
    count = 0
    def increment():
        nonlocal count
        count += 1
        return count
    return increment

c1 = make_counter()   # call #1
c2 = make_counter()   # call #2
c1(); c1(); c2()
```

Step by step:

1. **Call #1 to `make_counter`** creates environment box **E1** (parent: global) holding `count = 0`.
2. The `def increment` inside that call creates **closure A** = ⟨code of `increment`, E1⟩, which is returned and bound to `c1`. `make_counter` has returned, but E1 survives — closure A still points to it (lifetime follows reachability).
3. **Call #2** repeats the story with a *fresh* box **E2** and **closure B**, bound to `c2`.
4. **`c1()`** creates a call frame whose parent is **E1** (the captured environment, not the caller's!). `nonlocal count` makes `count += 1` an *assignment into E1*: E1's count becomes 1. The second `c1()` makes it 2.
5. **`c2()`** assigns into **E2**: its count becomes 1. E1 is untouched.

The final picture:

```
                +---------------------------+
                | global                    |
                |   make_counter -> <fn>    |
                |   c1 -> closure A         |
                |   c2 -> closure B         |
                +---------------------------+
                     ^                ^
             parent  |                |  parent
        +-----------------+    +-----------------+
        | E1 (call #1)    |    | E2 (call #2)    |
        |   count = 2     |    |   count = 1     |
        +-----------------+    +-----------------+
                 ^                      ^
        captured |             captured |
        closure A = <increment, E1>   closure B = <increment, E2>
             (bound to c1)                 (bound to c2)
```

And the same history as a table:

| Action | E1's `count` | E2's `count` | Return value |
|--------|--------------|--------------|--------------|
| `c1 = make_counter()` | 0 | — | closure A |
| `c2 = make_counter()` | 0 | 0 | closure B |
| `c1()` | 1 | 0 | 1 |
| `c1()` | 2 | 0 | 2 |
| `c2()` | 2 | 1 | 1 |

```python  liascript
def make_counter():
    count = 0
    def increment():
        nonlocal count
        count += 1
        return count
    return increment

c1 = make_counter()
c2 = make_counter()

print(c1(), c1())     # 1 2  — both assignments land in E1
print(c2())           # 1    — E2 is a separate box

# Verify the boxes are real: Python exposes them as closure "cells"
print("c1's captured count:", c1.__closure__[0].cell_contents)   # 2
print("c2's captured count:", c2.__closure__[0].cell_contents)   # 1
print("same box?", c1.__closure__[0] is c2.__closure__[0])       # False — E1 is not E2
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

[[MC]]
After `c1 = make_counter()`, `c2 = make_counter()`, then `c1(); c1(); c2()`, the returned values are 1, 2, 1 because:
- ( ) Each call to `c1` creates a fresh environment with `count = 0`
- (x) Each *call to `make_counter`* created its own environment box, so `c1` and `c2` increment different `count` bindings
- ( ) Python copies the value of `count` into each closure at definition time
- ( ) `c2` reset the shared counter

**Critical Thinking Questions (CTQs)**

> **CTQ 5.1** The diagram shows two separate boxes, E1 and E2, each holding its own `count`. What single fact about *when* environment boxes are created explains why `c1` and `c2` never interfere?

> **CTQ 5.2** `make_counter` returned long ago, yet the table shows E1's `count` still changing. Using the phrase "lifetime follows reachability," name exactly what is keeping E1 alive, and predict what would have to happen for Python to reclaim it.

> **CTQ 5.3** `nonlocal count` makes `count += 1` an **assign** into E1 rather than a **define** of a new local. Connect this to the environments module: without `nonlocal`, which operation would `count += 1` attempt, and why does it fail here? (Delete the `nonlocal` line in the cell and read the error.)

> **CTQ 5.4** Redraw the boxes for the `make_counter` of Model 1, which returns *two* closures (`increment` and `reset`). How many E-boxes does one call create, and which arrows in your drawing explain why the pair shares state?

---

# Part III: The Loop-Variable Trap

The loop-variable trap is one of the most famous beginner bugs in Python and JavaScript alike. Imagine handing every worker in a factory floor the *same* whiteboard marker and telling them to write down the current job number. By the time they all pick up the marker to write, the job number has moved on to the last value — they all write the same thing. This is exactly what happens when closures in a loop all capture the same variable binding instead of their own private copy.

> **Watch out!** When you write `[lambda: i for i in range(3)]`, all three lambdas capture *one* variable `i` — the same loop variable. By the time any of them is called, the loop has finished and `i` is `2`. This is not a bug in Python; it is the correct behavior of reference capture. The two fixes shown (default argument and factory function) both work by creating a separate binding per iteration.

## 3. The Famous Python Bug

```python  liascript
# The loop-variable trap — every Python programmer falls into this once
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
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

> **CTQ 6.1** All three lambdas captured the same `i` binding. After the loop, what is `i`? Why do all three lambdas return 2?

> **CTQ 6.2** Fix 1 uses `lambda i=i: i`. The outer `i` (the default argument value) is evaluated at *definition time*, capturing the current value. Why does this work, while the capture in the original version doesn't?

> **CTQ 6.3** Fix 2 uses a factory function `make_fn(i)` that creates a new scope. Draw the environment diagram showing why each returned lambda has a *different* captured environment.

> **CTQ 6.4** JavaScript's historic `var` scoping caused the same bug; `let` was introduced to fix it. How does `let` create "per-iteration" scope? Why can't `var` do this?

---

The code above showed the trap and two fixes; now draw it. The broken and fixed versions differ by exactly one thing — how many environment boxes exist — and the box diagram makes the bug visible at a glance.

## Model 5: The Loop Trap, Drawn as Boxes

**Broken:** `fns = [lambda: i for i in range(3)]`. The comprehension runs in a single scope, so there is exactly **one** box holding `i`, and every lambda's capture arrow points at it:

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

**Fixed (factory):** `fns = [make_fn(i) for i in range(3)]`. Each *call* to `make_fn` creates a fresh box, and each lambda captures its own:

```
   +-----------+   +-----------+   +-----------+
   | E0: i = 0 |   | E1: i = 1 |   | E2: i = 2 |
   +-----------+   +-----------+   +-----------+
        ^               ^               ^
        |               |               |
      lam0            lam1            lam2
   three closures, three boxes: one binding per closure
```

The broken version's history as a timeline — the trap is a *timing* bug, because capture is by reference and the calls happen after the last write:

| Loop step | Shared box's `i` | Closures created so far | What each would return *if called now* |
|-----------|------------------|-------------------------|----------------------------------------|
| iteration 0 | 0 | lam0 | lam0 → 0 |
| iteration 1 | 1 | lam0, lam1 | both → 1 |
| iteration 2 | 2 | lam0, lam1, lam2 | all → 2 |
| after the loop (calls happen here) | 2 | all three | **all → 2** |

```python  liascript
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
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

[[MC]]
`fns = [lambda: i for i in range(3)]` yields functions that all return 2, and `fns[0].__closure__[0] is fns[1].__closure__[0]` prints `True`. Together these show:
- ( ) The lambdas were compiled to the same code object, which forces one result
- (x) All three closures captured the very same binding (cell) for `i`, whose final value is 2
- ( ) Python evaluates lambda bodies eagerly at definition time
- ( ) The list comprehension copied the last lambda three times

**Critical Thinking Questions (CTQs)**

> **CTQ 7.1** Which single line of the cell's output is direct evidence for the "three arrows, one box" picture? Which line is evidence for "three boxes"?

> **CTQ 7.2** In the fixed diagram, what act creates each new box: the `lambda` *definition*, or the *call* to `make_fn`? Justify your answer with the environment-creation rule from Part II (`eval_call` builds a new environment per call).

> **CTQ 7.3** Fix 1's lambdas report `__closure__ = None` — they are not closures at all. Where does each one's `i` live instead, and why does that location make capture unnecessary?

---

[[MC]]
Two closures created by separate calls to `make_adder(5)` and `make_adder(3)` return different results for the same input because:

    [( )] The function body's code differs between them
    [(x)] Each closure captured a different defining environment in which `n` is bound to a different value
    [( )] Python caches the most recent return value
    [( )] Closures copy the global environment at call time

---

# Part IV: Closures vs. Objects

At first glance, objects and closures look very different — one is a class instance with named fields; the other is a function bundled with hidden environment variables. But look closer and you will find they are two sides of the same coin. Both bundle state with behavior; both control which code can reach that state. This model encodes a counter two ways, side-by-side, so you can see the structural parallel directly.

> **Watch out!** Closures are not limited to functional languages. Python, JavaScript, Ruby, and even Java (via lambdas) all have closures. A common misconception is that "closures = Haskell/Scheme only." In modern JavaScript, closures are used every time you write a callback, event handler, or `useEffect` hook in React.

## 4. The Koan: Closures Are Poor Man's Objects

The famous koan: "Closures are a poor man's objects; objects are a poor man's closures." They are dual.

```python  liascript
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
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

> **CTQ 8.1** In the closure-based counter, `count` is a shared mutable cell. In the object-based counter, `self._count` is a field. What is the structural difference? What is the conceptual difference?

> **CTQ 8.2** The closure counter uses a list `[start]` to work around Python's scoping rules for `nonlocal`. Rewrite it using `nonlocal count` (Python 3) instead of a list. Why is `nonlocal` cleaner?

> **CTQ 8.3** Languages like OCaml and Haskell have closures but no classes. Languages like Java (pre-lambda) have classes but no closures (lambdas are objects). From what you now know about the implementation of each, argue: which is more fundamental?

---

## Exercises

### Exercise 1 — Integrate Closures into Mini (30 min)
Add closures to your Mini interpreter:
1. Add `FunDef(name, params, body)` and `Call(callee, args)` AST nodes
2. In the parser, add `fun name(params) { body }` syntax and `name(args)` call syntax
3. In the evaluator, implement `execute_fundef` (create closure, bind name) and `eval_call` (create child env, run body, catch ReturnSignal)
4. Demonstrate: a plain function, `factorial(5)`, and `make_adder` working in your language

### Exercise 2 — Counter Objects (15 min)
Build `make_counter()` using closures (not a class) that returns an increment function. Then build `make_account(balance)` with `deposit(amount)` and `withdraw(amount)` methods. Demonstrate shared state between the two returned functions.

### Exercise 3 — Trap Tour (15 min)
Reproduce the loop-variable trap in your language (or Python), apply both fixes, and explain each fix's mechanism with environment diagrams.

### Exercise 4 — Scope Flip Experiment (20 min)
Apply the one-token change from CTQ 3.1 to make your interpreter dynamically scoped. Rerun the `show`/`demo` program from the scope module. Report the output difference and explain with a diagram which environment chain the dynamically scoped version follows.

---

## Reflection Prompt

A closure carries its context everywhere, so it always means what it meant at home. Dynamically scoped code means whatever its surroundings currently impose. People can resemble both: some carry their context everywhere; others adapt to whoever is calling. When has carrying your own context served you, and when has adapting to the caller been the wiser semantics?

---

## Further Reading

- **"Crafting Interpreters"** — Robert Nystrom, "Functions" and "Closures" chapters (online, free): our exact implementation, then optimized
- **SICP Section 3.2** — Abelson & Sussman: the environment model of evaluation
- **"The Art of the Interpreter"** — Steele & Sussman (1978): closures invented and explained
- **Python `__closure__`** — CPython exposes closures via `fn.__closure__`: introspect live closures
- **JavaScript `let` vs `var`** — MDN: the real-world consequence of the loop-variable trap at ecosystem scale

## Going Deeper (Optional Appendices)

The core lesson above stands on its own. The optional deep dives below expand on it — read whichever interest you:

- Coroutines and Generators: Pausable Computation
- Error Handling: From Return Codes to Algebraic Effects

## Going Deeper: Coroutines and Generators: Pausable Computation

> **Opening hook:** Imagine a vending machine. A regular function is like a vending machine that dumps every item it will ever produce onto the floor the moment you press the button — all at once, whether you want them yet or not. A **generator** is a vending machine that produces exactly one item each time you press the button, remembers where it left off, and waits patiently until you press again. The machine's internal state — which slot it was at, how many remain — is frozen between presses. That frozen state is the essence of a coroutine.

#### Learning Goals

By the end of this activity, you will be able to:

- Define coroutines and generators and explain how `yield` captures a continuation to pause and resume computation
- Trace the execution of a generator function step-by-step, predicting what value each `next()` call produces
- Implement lazy infinite sequences using generator functions and compare their memory use to eager list-based equivalents
- Explain how `async`/`await` desugars to a state machine and identify where suspension points occur
- Extend a simple interpreter to support generator objects with `yield` and `send` semantics

> **Prerequisites:** Python functions and closures; basic continuations from the CPS activity
> **Goal:** Understand generators as semi-coroutines, how `yield` captures a continuation, how `async/await` desugars to state machines, and how to add generator support to a simple interpreter.

**POGIL Roles:** Driver · Recorder · Reporter · Manager

---

> **Before You Begin**
>
> This activity assumes you are comfortable with:
>
> - Writing and calling Python functions, including closures that capture variables from an enclosing scope
> - The idea of a **continuation** from the CPS (Continuation-Passing Style) activity — roughly, "the rest of the computation"
> - Basic Python iteration: `for` loops, `range()`, and what `StopIteration` means
>
> If the term "continuation" feels fuzzy, revisit the CPS activity before Model 3. If Python closures feel shaky, review how `def` inside `def` works and what a stack frame contains.

---

#### Preface: Why Functions Are Too Rigid

A function is called, runs to completion, and returns. This works for most computations — but not all:

- **Infinite sequences:** How do you iterate over all prime numbers? You can't return them all.
- **Cooperative multitasking:** How does one task yield the CPU to another without OS threads?
- **Asynchronous I/O:** How does a function pause while waiting for data without blocking everything?
- **Two-way communication:** How does a producer send values to a consumer one at a time?

All four problems share a structure: a computation needs to **pause at an arbitrary point** and later **resume from exactly where it left off**. This is the essence of a **coroutine**.

---

#### Model 1: Generators as Lazy Sequences

**Intuition:** Think of the difference between a photographer who prints every photo in the roll immediately versus one who prints each photo only when you ask for the next one. The first approach — printing everything up front — is **eager evaluation**: fast to start iterating but expensive in memory. The second — printing on demand — is **lazy evaluation**: the camera (generator) remembers exactly which frame it was on and produces the next one only when asked. `yield` is the instruction that says "print this one, then pause and wait."

A Python **generator function** uses `yield` instead of (or in addition to) `return`. Calling it returns a **generator object** — an object that remembers where the function paused.

```python
import sys

# A regular function computes a finite list eagerly
def first_n_squares_eager(n):
    result = []
    for i in range(n):
        result.append(i * i)
    return result

# A generator function produces values lazily, one at a time
def squares_lazy():
    i = 0
    while True:                  # infinite sequence!
        yield i * i              # pause here, return i*i to caller
        i += 1                   # resume here on next()

print("=== Eager list ===")
xs = first_n_squares_eager(5)
print(f"  type: {type(xs)}, values: {xs}")
print(f"  memory: ~{sys.getsizeof(xs)} bytes (all in RAM)")

print()
print("=== Lazy generator ===")
gen = squares_lazy()
print(f"  type: {type(gen)}")
print(f"  memory: ~{sys.getsizeof(gen)} bytes (no values stored)")
print()

print("  First 7 values (pulled on demand):")
for i, val in enumerate(gen):
    print(f"    next() #{i+1} → {val}")
    if i >= 6:
        break

print()
print("=== Generator protocol: __iter__ and __next__ ===")
gen2 = squares_lazy()
print(f"  next(gen2) = {next(gen2)}")
print(f"  next(gen2) = {next(gen2)}")
print(f"  next(gen2) = {next(gen2)}")

print()
print("=== yield expression inside a for loop ===")
def first_n(gen, n):
    return [next(gen) for _ in range(n)]

print(f"  First 10 squares: {first_n(squares_lazy(), 10)}")

print()
print("=== Finite generator: StopIteration ===")
def countdown(n):
    while n >= 0:
        yield n
        n -= 1

cd = countdown(3)
for v in cd:
    print(f"  {v}", end=" ")
print()

try:
    next(cd)   # already exhausted
except StopIteration:
    print("  StopIteration raised on exhausted generator")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

**Key insight:** A generator function's stack frame is **frozen** at every `yield`. The local variables, loop counter, and instruction pointer are all preserved. `next()` thaws the frame and continues from the yield point.

> **Watch out!** Calling a generator function does **not** execute any of its body. `gen = squares_lazy()` returns a generator object instantly — the line `i = 0` has not run yet. The body only starts executing on the *first* `next(gen)` call. This surprises many beginners who expect `gen = squares_lazy()` to behave like a normal function call.

> **Critical Thinking Questions 1–3**

**CTQ 1.** An infinite list `first_n_squares_eager(1_000_000)` allocates a list of 1 million integers in RAM before returning. A generator `squares_lazy()` uses ~200 bytes regardless of how many values you pull. What architectural difference explains this?

[[___ your answer here ___]]

**CTQ 2.** The generator object remembers "where it was." What four pieces of state must be preserved in the frozen frame to allow resumption at the `yield` point? (Hint: same things a stack frame normally stores.)

[[___ your answer here ___]]

**CTQ 3.** `for v in countdown(3)` implicitly calls `next()` and catches `StopIteration`. Write the desugared version using a `while True` loop with explicit `try/except StopIteration`. What does this reveal about how `for` loops work in Python?

[[___ your answer here ___]]

---

#### Model 2: `yield` as a Two-Way Channel (`send` and `throw`)

**Intuition:** So far a generator has been a one-way conveyor belt — values flow out to the caller via `yield`. Model 2 upgrades the belt to a **two-lane road**: the generator can also *receive* a value from the caller at the same `yield` point. Think of it as a walkie-talkie conversation where you press the button to transmit a value, hear a reply, and the other party is waiting for your next message before they continue. `.send(v)` is you pressing the button and speaking; `value = yield result` is the generator speaking *and* listening at the same time.

Generators are not just output pipelines — they can **receive** values via `.send()`. This makes them true **coroutines** (two-way communication channels).

```python
def running_average():
    """Coroutine: receives numbers via send(), yields running average."""
    total = 0.0
    count = 0
    avg = None
    while True:
        value = yield avg         # send avg out AND receive new value in
        if value is None:
            break
        total += value
        count += 1
        avg = total / count

print("=== Bidirectional coroutine with send() ===")
coro = running_average()
result = next(coro)       # must prime the coroutine (run to first yield)
print(f"  initial yield: {result}")   # None (no avg yet)
# Watch out! Calling coro.send(10) before next(coro) raises TypeError.
# The coroutine must reach its first yield before it can receive a sent value.

for v in [10, 20, 30, 40, 50]:
    result = coro.send(v)
    print(f"  sent {v:2d}, received avg = {result:.2f}")

coro.close()   # sends GeneratorExit; coroutine can clean up in try/finally

print()
print("=== throw(): injecting exceptions ===")
def safe_counter():
    n = 0
    while True:
        try:
            yield n
            n += 1
        except ValueError as e:
            print(f"  resetting because: {e}")
            n = 0

sc = safe_counter()
for _ in range(4):
    print(f"  next() → {next(sc)}")
sc.throw(ValueError, "manual reset!")
for _ in range(3):
    print(f"  next() → {next(sc)}")
sc.close()

print()
print("=== yield from: delegating to a sub-generator ===")
def gen_a():
    yield "a1"
    yield "a2"

def gen_b():
    yield "b1"
    yield from gen_a()   # delegate: transparently yields a1, a2
    yield "b2"

print("  yield from chain:")
for v in gen_b():
    print(f"  {v}")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

> **Critical Thinking Questions 4–6**

**CTQ 4.** `value = yield avg` is a single expression that both sends `avg` out AND receives the next `send()` value in. Draw the communication diagram between the driver code and the coroutine. What is the invariant about when `value` gets its value?

[[___ your answer here ___]]

**CTQ 5.** `next(coro)` is equivalent to `coro.send(None)`. Why must you "prime" a coroutine with `next()` (or `send(None)`) before calling `.send(value)`? What is the coroutine's execution state before and after priming?

[[___ your answer here ___]]

**CTQ 6.** `yield from gen_a()` in `gen_b()` is transparent: values pass through `gen_b` as if `gen_a` were inlined. `send()` and `throw()` values also pass through. What design problem does `yield from` solve that plain `for v in gen_a(): yield v` does not handle?

[[___ your answer here ___]]

---

#### Model 3: How `yield` Captures a Continuation

**Intuition:** Recall from the CPS activity that a continuation is "everything that happens next after this point." When a generator hits `yield`, it takes a snapshot of its entire execution state — local variables, loop counters, the instruction pointer — and stores it on the heap as a frozen frame. This is a *delimited* continuation: it captures only up to the next `yield` or the function's return, not the entire rest of the program. The state machine analogy makes this concrete: if you had to implement `yield` yourself without language support, you would number each yield point and use a big `if/elif` to jump back to the right place. Python's bytecode compiler does exactly that automatically.

`yield` is a **delimited continuation** — it captures the rest of the computation up to the nearest coroutine boundary. This connects generators to the CPS transformation you have already seen.

```python
# Manual CPS transformation of a generator
# Original generator:
#   def gen():
#       yield 1
#       yield 2
#       yield 3
#
# In CPS, "the rest of gen after yield 1" becomes a continuation k1.
# We model this as explicit states.

from dataclasses import dataclass
from typing import Callable, Any, Optional

@dataclass
class GeneratorState:
    """Manual state machine equivalent of a generator."""
    state: int = 0     # which 'yield' are we at?
    # local variables would go here

def gen_state_machine():
    """Models: def gen(): yield 1; yield 2; yield 3"""
    g = GeneratorState()
    while True:
        if g.state == 0:
            g.state = 1
            yield 1           # continuation: state 1
        elif g.state == 1:
            g.state = 2
            yield 2           # continuation: state 2
        elif g.state == 2:
            g.state = 3
            yield 3           # continuation: state 3
        else:
            return             # StopIteration

print("=== State machine equivalent of a 3-yield generator ===")
for v in gen_state_machine():
    print(f"  {v}")

print()
print("=== Python actually compiles generators to state machines ===")
def original_gen():
    yield 1
    yield 2
    yield 3

import dis
print("  Bytecode of original_gen (showing YIELD_VALUE / RESUME):")
for instr in dis.get_instructions(original_gen):
    if instr.opname in ('YIELD_VALUE', 'RETURN_VALUE', 'RESUME', 'LOAD_CONST',
                        'GEN_START', 'RETURN_CONST', 'LOAD_FAST'):
        print(f"    {instr.offset:3d}  {instr.opname:<20} {instr.argval!r}")

print()
print("=== Generators and first-class continuations ===")
# call/cc (call-with-current-continuation) generalizes yield:
# it captures the ENTIRE continuation, not just to the nearest coroutine boundary.
# Python doesn't have call/cc, but we can simulate limited versions.

def make_generator_cps():
    """Shows that 'yield' is equivalent to saving/restoring execution state."""
    continuations = []
    
    def step():
        results = []
        for state in [1, 2, 3]:
            results.append(state)    # 'yield state' captured here
        return results
    
    return step()

print("  Generator-as-CPS result:", make_generator_cps())
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

> **Critical Thinking Questions 7–9**

**CTQ 7.** The state machine version of `gen()` tracks which `yield` the function has reached using an integer state variable. Where does Python store this state in a real generator? (Hint: look at what a generator object contains.)

[[___ your answer here ___]]

**CTQ 8.** A generator's continuation is **delimited** — it runs until the next `yield` or the function returns. A true first-class continuation (Scheme's `call/cc`) captures the **entire remaining computation**. Give an example of something `call/cc` can express that generators cannot.

[[___ your answer here ___]]

**CTQ 9.** The bytecode output shows `YIELD_VALUE` and `RESUME` instructions. Explain what the Python VM does when it hits `YIELD_VALUE`: what changes in the VM's execution state, and what happens to the generator object's frame?

[[___ your answer here ___]]

---

#### Model 4: `async`/`await` — Generators Over I/O

**Intuition:** Imagine a chef managing multiple orders at a restaurant. A synchronous chef starts one dish, cooks it entirely, plates it, then starts the next — customers wait in sequence. An asynchronous chef starts a dish, puts it in the oven (the I/O), then immediately starts prepping the next dish while the oven does its work. When the oven timer fires (the I/O completes), the chef resumes that dish. `await` is the chef's oven-start moment: "I'm handing this off; resume me when it's done." The **event loop** is the kitchen manager who tracks which oven is done and tells the right chef to continue. Crucially, this is all on one thread — no parallelism, just clever scheduling.

Python's `async def` / `await` syntax is syntactic sugar built on generators. An `async` function is a **coroutine** that yields control when waiting for I/O, and an event loop resumes it when the awaited operation completes.

```python
import asyncio
import time

# Simulate async I/O with asyncio.sleep
async def fetch_data(source: str, delay: float) -> str:
    print(f"  [{time.monotonic():.2f}s] Starting fetch from {source}...")
    await asyncio.sleep(delay)    # yields to event loop; other tasks run here
    print(f"  [{time.monotonic():.2f}s] Finished fetch from {source}")
    return f"data from {source}"

async def main_sequential():
    """Sequential: fetch one at a time. Total time ≈ sum of delays."""
    start = time.monotonic()
    a = await fetch_data("server_A", 0.05)
    b = await fetch_data("server_B", 0.05)
    elapsed = time.monotonic() - start
    print(f"  Sequential: got {a!r}, {b!r} in {elapsed:.3f}s")

async def main_concurrent():
    """Concurrent: both fetches run in parallel via asyncio.gather."""
    start = time.monotonic()
    a, b = await asyncio.gather(
        fetch_data("server_A", 0.05),
        fetch_data("server_B", 0.05),
    )
    elapsed = time.monotonic() - start
    print(f"  Concurrent: got {a!r}, {b!r} in {elapsed:.3f}s")

print("=== Sequential async (awaits one at a time) ===")
asyncio.run(main_sequential())

print()
print("=== Concurrent async (gather runs both at once) ===")
asyncio.run(main_concurrent())

print()
print("=== Desugaring: async/await as generator syntax ===")
# Before async/await syntax existed (Python 2 era), coroutines were
# written using generators with yield from.
# Here is the mental model (not real Python 2, but illustrative):

def old_style_coroutine():
    """Equivalent to: async def coroutine(): await asyncio.sleep(0.01)"""
    print("  about to 'yield' (simulating await)")
    yield   # pause; event loop does work here
    print("  resumed after 'yield'")

def old_event_loop(coro):
    gen = coro()
    try:
        next(gen)    # run until first yield
        print("  [event loop] doing other work...")
        next(gen)    # resume after yield
    except StopIteration:
        pass

old_event_loop(old_style_coroutine)
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

> **Critical Thinking Questions 10–12**

> **Watch out!** `async`/`await` is **not** parallelism. Both tasks in `main_concurrent` run on a single OS thread. `asyncio.gather` interleaves them only because each `await asyncio.sleep(...)` voluntarily yields the thread back to the event loop. If one coroutine does CPU-heavy work without any `await`, it **blocks the entire event loop** and no other coroutine can run. For true CPU parallelism you need `multiprocessing` or a thread pool.

**CTQ 10.** In `main_concurrent`, both `fetch_data` calls appear to run simultaneously, yet Python has a Global Interpreter Lock (GIL). Explain how concurrency is achieved without true parallelism. What kind of waiting does `asyncio.sleep` simulate?

[[___ your answer here ___]]

**CTQ 11.** The "function color" problem: an `async` function can only be awaited from another `async` function. This means `async` "infects" callers all the way up the call chain. Why does this structural constraint exist? What would break if you could `await` from a regular function?

[[___ your answer here ___]]

**CTQ 12.** The desugaring demo shows that `await` desugars to `yield`. Describe how an event loop works in terms of generators: what does the event loop do when a coroutine yields? What does it do when the awaited I/O completes?

[[___ your answer here ___]]

---

#### Model 5: Implementing a Generator in a Mini Interpreter

**Intuition:** When you add generator support to your own interpreter, you face the same design choice Python's implementers faced: where do you store the frozen execution state between `yield` calls? The cleanest trick is to use the *host language's* own generator mechanism as the storage. Since our interpreter is written in Python, we write the core evaluation loop as a Python generator — every time we encounter a `yield` node in the mini language, we `yield` from Python. Python's own frame-freezing machinery then carries our interpreter's state for free. This technique — using the host language's feature to implement the same feature in the guest language — is called **reflective implementation** or **metacircular interpretation**.

Adding generator support to an interpreter requires preserving the function's execution state across multiple calls. The cleanest approach uses Python's own generators as the implementation mechanism.

```python
from dataclasses import dataclass, field
from typing import Any, Optional, Iterator

# --- AST nodes ---
@dataclass
class Num:
    value: float

@dataclass
class Var:
    name: str

@dataclass
class BinOp:
    op: str
    left: Any
    right: Any

@dataclass
class Yield_:          # our language's 'yield' statement
    value: Any

@dataclass
class GeneratorDef:
    param: str
    body: list         # list of statements (each is an AST node)

@dataclass
class Call:
    func: Any
    arg: Any

# --- Environment ---
class Env:
    def __init__(self, parent=None):
        self.bindings = {}
        self.parent = parent
    def lookup(self, name):
        if name in self.bindings: return self.bindings[name]
        if self.parent: return self.parent.lookup(name)
        raise NameError(f"undefined: {name!r}")
    def define(self, name, val):
        self.bindings[name] = val

# --- Generator object produced by calling a GeneratorDef ---
class GeneratorObj:
    def __init__(self, param, body, closure_env, arg):
        self._iter = self._run(param, body, closure_env, arg)
    
    def _run(self, param, body, closure_env, arg):
        env = Env(parent=closure_env)
        env.define(param, arg)
        for stmt in body:
            if isinstance(stmt, Yield_):
                yield eval_expr(stmt.value, env)
            else:
                eval_expr(stmt, env)   # side-effecting statement
    
    def __iter__(self):
        return self
    
    def __next__(self):
        return next(self._iter)

def eval_expr(node, env):
    if isinstance(node, Num):
        return node.value
    if isinstance(node, Var):
        return env.lookup(node.name)
    if isinstance(node, BinOp):
        l = eval_expr(node.left, env)
        r = eval_expr(node.right, env)
        return {"+": l+r, "-": l-r, "*": l*r, "/": l/r}[node.op]
    if isinstance(node, GeneratorDef):
        return node   # a generator definition evaluates to itself (like a closure)
    if isinstance(node, Call):
        fn = eval_expr(node.func, env)
        arg = eval_expr(node.arg, env)
        if isinstance(fn, GeneratorDef):
            return GeneratorObj(fn.param, fn.body, env, arg)
        raise TypeError(f"not callable: {fn!r}")
    raise ValueError(f"unknown node: {node!r}")

# Demo: generator that yields 0, 1, 4, 9, ... (squares up to n)
# Equivalent to:
#   gen squares(n):
#       i = 0
#       while i <= n:
#           yield i * i
#           i = i + 1
# We'll approximate with a fixed body producing first 5 squares:

global_env = Env()
global_env.define("squares_of_5", GeneratorDef(
    param="start",
    body=[
        Yield_(BinOp("*", Var("start"), Var("start"))),
        Yield_(BinOp("*", BinOp("+", Var("start"), Num(1)), BinOp("+", Var("start"), Num(1)))),
        Yield_(BinOp("*", BinOp("+", Var("start"), Num(2)), BinOp("+", Var("start"), Num(2)))),
    ]
))

print("=== Mini interpreter with generator support ===")
call_node = Call(Var("squares_of_5"), Num(0))
gen_obj = eval_expr(call_node, global_env)

print(f"Generator object: {type(gen_obj).__name__}")
for val in gen_obj:
    print(f"  yielded: {val}")

print()
print("=== Key insight: Python's generator IS our interpreter's continuation ===")
print("  Each 'yield eval_expr(...)' in _run captures the frame's state.")
print("  next() on the GeneratorObj resumes exactly where _run paused.")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

> **Critical Thinking Questions 13–15**

**CTQ 13.** The `GeneratorObj._run` method is itself a Python generator (it uses `yield`). This means we are using Python's generator mechanism to implement our interpreter's generator mechanism. What is the technical term for this implementation strategy? What is the risk?

[[___ your answer here ___]]

**CTQ 14.** In the mini interpreter, calling `squares_of_5(0)` creates a new `GeneratorObj` with its own private `Env`. If you called `squares_of_5(0)` twice, you would get two independent generators. How does this differ from calling a regular function twice?

[[___ your answer here ___]]

**CTQ 15.** The body of `GeneratorDef` is evaluated lazily — statements only run when `next()` is called. If the generator body has a side effect (like printing), when does that side effect occur? Give an example where this laziness causes surprising behavior.

[[___ your answer here ___]]

---

#### Multiple Choice Review

**Question 1.** A Python generator function `def g(): yield 1; yield 2` called as `g()` returns:

- [( )] The value `1` immediately
- [( )] A list `[1, 2]`
- [(X)] A generator object that yields `1` then `2` when iterated
- [( )] Nothing; the function body has not executed yet

**Question 2.** `coro.send(value)` on a generator/coroutine:

- [( )] Calls the function with `value` as an argument
- [(X)] Resumes the coroutine and makes `value` the result of the `yield` expression
- [( )] Appends `value` to the generator's output sequence
- [( )] Resets the generator to its initial state

**Question 3.** The "function color" problem with `async/await` means:

- [( )] Async functions run faster than regular functions
- [(X)] Async functions can only be awaited from other async functions, propagating up the call chain
- [( )] Async functions cannot call regular functions
- [( )] Async functions require multiple OS threads

**Question 4.** A generator captures its execution state by:

- [( )] Allocating a new heap object for each yielded value
- [( )] Using OS threads with mutex locks
- [(X)] Freezing the stack frame (locals, instruction pointer) as a heap-allocated object
- [( )] Copying all local variables into a global dictionary

---

#### Exercises

**Exercise 1.** Implement a `pipeline` that chains generators: `map_gen`, `filter_gen`, and `take_gen`. Use them to compute the first 5 even squares:

```python
def integers_from(n):
    while True:
        yield n
        n += 1

def map_gen(gen, f):
    for v in gen:
        yield f(v)

def filter_gen(gen, pred):
    for v in gen:
        if pred(v):
            yield v

def take_gen(gen, n):
    for i, v in enumerate(gen):
        if i >= n:
            break
        yield v

# Compute: first 5 even perfect squares
squares = map_gen(integers_from(0), lambda n: n * n)
even_squares = filter_gen(squares, lambda n: n % 2 == 0)
result = list(take_gen(even_squares, 5))
print(f"First 5 even squares: {result}")

# Compare memory: eager vs lazy
eager = [n*n for n in range(10000) if (n*n) % 2 == 0][:5]
print(f"Eager (computed 10000, kept 5): {eager}")
print(f"Lazy (computed exactly 5): {result}")
print("Both produce the same answer; lazy is O(1) memory.")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

**Exercise 2.** Implement a cooperative multitasking scheduler using generators. Each "task" is a generator that yields to give up control. The scheduler runs tasks in round-robin:

```python
def task_a():
    for i in range(3):
        print(f"  task_a: step {i}")
        yield   # give up control

def task_b():
    for i in range(4):
        print(f"  task_b: step {i}")
        yield   # give up control

def scheduler(*tasks):
    """Round-robin cooperative scheduler."""
    active = [t() for t in tasks]
    while active:
        next_round = []
        for gen in active:
            try:
                next(gen)   # run task until its next yield
                next_round.append(gen)
            except StopIteration:
                print(f"  [task finished]")
        active = next_round

print("=== Cooperative multitasking with generators ===")
scheduler(task_a, task_b)
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

**Exercise 3.** Implement a `memoize_gen` that caches yielded values so that the generator can be replayed from the beginning without recomputing:

```python
class ReplayableGen:
    def __init__(self, gen_fn, *args, **kwargs):
        self._gen_fn = gen_fn
        self._args = args
        self._kwargs = kwargs
        self._cache = []
        self._gen = gen_fn(*args, **kwargs)
        self._done = False
    
    def __iter__(self):
        idx = 0
        while True:
            if idx < len(self._cache):
                yield self._cache[idx]
            elif self._done:
                return
            else:
                try:
                    val = next(self._gen)
                    self._cache.append(val)
                    yield val
                except StopIteration:
                    self._done = True
                    return
            idx += 1

def expensive_gen(n):
    for i in range(n):
        print(f"  [computing {i}]")
        yield i * i

rg = ReplayableGen(expensive_gen, 4)

print("First pass (computes each value):")
for v in rg:
    print(f"  got {v}")

print()
print("Second pass (reads from cache, no recomputation):")
for v in rg:
    print(f"  got {v}")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

**Exercise 4.** Extend the mini interpreter from Model 5 to support a `while` loop inside generator bodies. Add a `While` AST node and a `Assign` node so you can write:

```
gen count_up(start):
    while start <= 5:
        yield start
        start = start + 1
```

```python
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
    op: str
    left: Any
    right: Any

@dataclass
class Compare:
    op: str
    left: Any
    right: Any

@dataclass
class Yield_:
    value: Any

@dataclass
class Assign:
    name: str
    value: Any

@dataclass
class While:
    condition: Any
    body: list

@dataclass
class GeneratorDef:
    param: str
    body: list

class Env:
    def __init__(self, parent=None):
        self.bindings = {}
        self.parent = parent
    def lookup(self, name):
        if name in self.bindings: return self.bindings[name]
        if self.parent: return self.parent.lookup(name)
        raise NameError(f"undefined: {name!r}")
    def define(self, name, val):
        self.bindings[name] = val
    def assign(self, name, val):
        if name in self.bindings:
            self.bindings[name] = val
            return
        if self.parent:
            self.parent.assign(name, val)
            return
        raise NameError(f"assign to undefined: {name!r}")

def eval_node(node, env):
    if isinstance(node, Num): return node.value
    if isinstance(node, Var): return env.lookup(node.name)
    if isinstance(node, BinOp):
        l, r = eval_node(node.left, env), eval_node(node.right, env)
        return {"+": l+r, "-": l-r, "*": l*r}[node.op]
    if isinstance(node, Compare):
        l, r = eval_node(node.left, env), eval_node(node.right, env)
        return {"<=": l<=r, "<": l<r, ">=": l>=r}[node.op]
    if isinstance(node, Assign):
        val = eval_node(node.value, env)
        env.assign(node.name, val)
        return val
    if isinstance(node, Yield_):
        return ("yield", eval_node(node.value, env))
    if isinstance(node, While):
        while eval_node(node.condition, env):
            for stmt in node.body:
                result = eval_node(stmt, env)
                if isinstance(result, tuple) and result[0] == "yield":
                    yield result[1]
        return
    raise ValueError(f"unknown: {node!r}")

def run_generator(gen_def: GeneratorDef, arg, parent_env):
    env = Env(parent=parent_env)
    env.define(gen_def.param, arg)
    for stmt in gen_def.body:
        yield from run_node_yielding(stmt, env)

def run_node_yielding(node, env):
    if isinstance(node, Yield_):
        yield eval_node(node.value, env)
    elif isinstance(node, While):
        while eval_node(node.condition, env):
            for stmt in node.body:
                yield from run_node_yielding(stmt, env)
    elif isinstance(node, Assign):
        eval_node(node, env)

# count_up(start): while start <= 5: yield start; start = start + 1
global_env = Env()
count_up = GeneratorDef(
    param="start",
    body=[
        While(
            condition=Compare("<=", Var("start"), Num(5)),
            body=[
                Yield_(Var("start")),
                Assign("start", BinOp("+", Var("start"), Num(1)))
            ]
        )
    ]
)

print("count_up(1):")
for val in run_generator(count_up, 1, global_env):
    print(f"  {val}")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

**Exercise 5.** Implement a simple async event loop using generators. Create a `Task` class, an `EventLoop` that runs tasks cooperatively, and simulate I/O with time-delayed wake-ups:

```python
import time
from dataclasses import dataclass, field
from typing import Any, List, Callable

@dataclass
class Future:
    result: Any = None
    done: bool = False
    callbacks: List[Callable] = field(default_factory=list)
    
    def set_result(self, value):
        self.result = value
        self.done = True
        for cb in self.callbacks:
            cb(value)

class SimpleEventLoop:
    def __init__(self):
        self._ready = []       # (gen, send_value) pairs
        self._sleeping = []    # (wake_time, gen) pairs
    
    def call_soon(self, gen, value=None):
        self._ready.append((gen, value))
    
    def call_later(self, delay, gen):
        self._sleeping.append((time.monotonic() + delay, gen))
    
    def run(self, coro):
        gen = coro()
        self.call_soon(gen)
        
        while self._ready or self._sleeping:
            # Wake up sleeping tasks
            now = time.monotonic()
            still_sleeping = []
            for wake_time, gen in self._sleeping:
                if now >= wake_time:
                    self.call_soon(gen)
                else:
                    still_sleeping.append((wake_time, gen))
            self._sleeping = still_sleeping
            
            # Run ready tasks
            if self._ready:
                gen, value = self._ready.pop(0)
                try:
                    signal = gen.send(value)
                    if isinstance(signal, tuple) and signal[0] == "sleep":
                        self.call_later(signal[1], gen)
                except StopIteration:
                    pass

def sleep(seconds):
    """Our language's equivalent of asyncio.sleep."""
    yield ("sleep", seconds)

def fake_io_task(name, delay):
    print(f"  [{time.monotonic():.3f}] {name} starting")
    yield from sleep(delay)
    print(f"  [{time.monotonic():.3f}] {name} done after {delay}s")
    return f"result from {name}"

def main_coro():
    yield from fake_io_task("task_A", 0.03)
    yield from fake_io_task("task_B", 0.02)
    print("  all tasks done")

print("=== Simple generator-based event loop ===")
loop = SimpleEventLoop()
loop.run(main_coro)
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

---

#### Reflection

1. Generators, coroutines, and async/await are all variations on the same idea: pausable computation. Map each to a concept from the CPS activity: where is the continuation stored in each case?

2. Python added `async def` / `await` as dedicated syntax rather than using bare generators. What usability problem did this solve? What did it give up?

3. Your interpreter currently evaluates expressions to completion. If you wanted to add generator support to your language, where in the evaluation pipeline would the most significant changes go? What data structure would you need to add?

---

#### Further Reading

- **Python docs:** Generator Expressions, `yield from`, `asyncio` event loop
- **PEP 255** — Simple Generators (the original Python generator proposal)
- **PEP 342** — Coroutines via Enhanced Generators (added `send`, `throw`, `close`)
- **PEP 3156** — Asynchronous I/O Support (asyncio)
- **Talk:** David Beazley, "Python Concurrency from the Ground Up" (PyCon 2015)
- **Talk:** David Beazley, "Generators: The Final Frontier" (PyCon 2014) — builds an event loop from scratch
- **Paper:** Moura & Ierusalimschy (2009), "Revisiting Coroutines" — theory of semi-coroutines vs full coroutines
- **Book:** *Crafting Interpreters* — Nystrom, Chapter 26 (closures → generators is a natural extension)

---

*End of Activity — Coroutines and Generators: yield, send, async/await, state machines, interpreter implementation*

## Going Deeper: Error Handling: From Return Codes to Algebraic Effects

Error handling is not just a library concern — it is a fundamental language design decision that shapes every program written in a language. Should errors interrupt control flow or flow as values? Should the type system enforce that errors are handled? The choice between exceptions, error values, and algebraic effect types reflects a philosophy about programmer responsibility, code clarity, and what the language should guarantee versus what it trusts the programmer to do correctly.

#### Learning Goals

By the end of this activity, you will be able to:

- Compare error-handling strategies (return codes, checked/unchecked exceptions, Option/Maybe, Result/Either) and identify the tradeoffs each makes in static safety, composability, and caller burden
- Implement the Option and Result types in Python and use them to propagate errors without exceptions
- Apply monadic chaining (`flatMap`/`bind`) to thread errors through a pipeline without nested conditionals
- Analyze how a language's error strategy shapes the user experience of writing and reading code in that language
- Design error handling for a mini interpreter, choosing an appropriate strategy and justifying the choice

> **Prerequisites:** Python programming, familiarity with exceptions, basic type system concepts
> **Goal:** Compare how different languages approach errors — return codes, checked/unchecked exceptions, Option/Maybe, Result/Either, monadic propagation — and understand how each choice shapes language design and user experience.

> **Before You Begin — check that you have these foundations:**
>
> - **Python try/except:** You have written `try`/`except` blocks to catch exceptions and `raise` to signal errors. If you have not, review the Python docs on exceptions first.
> - **The call stack:** You understand that when function A calls B which calls C, Python maintains a stack of active frames. When an exception propagates "up," it unwinds that stack looking for a matching `except`.
> - **Maybe / Result types:** You have at least seen the idea that a function can return a value that is *either* a success or a failure, rather than raising an exception. (Models 3 and 4 below build this up from scratch, but having a mental picture helps.)

**POGIL Roles:** Driver · Recorder · Reporter · Manager

---

#### Preface: Why Error Handling Is a Language Design Problem

Every program encounters errors: bad input, missing files, network failures, type mismatches, division by zero. A language's error handling strategy determines:

- **When** errors are detected (statically vs. dynamically)
- **How** errors are represented (return values, exceptions, types)
- **Who** is responsible for handling them (caller vs. callee)
- **What** happens when errors are ignored (silently continue, crash, type error)
- **How** errors compose (deeply nested error propagation)

There is no single best answer — each approach makes different tradeoffs, and understanding them will inform how you design error handling in your own interpreter.

---

#### Model 1: Return Codes — The C Approach

**Intuition:** Imagine asking a friend to look up a phone number. If they can't find it, they could simply hand you back a slip of paper that says "-1" instead of a real number. It is your job to notice the slip says "-1" before you try to dial. There is nothing stopping you from ignoring it and dialing anyway — that is exactly the problem with return codes. This is the oldest and lowest-level error-handling strategy, inherited from C, where functions signal failure through a conventional "magic" return value. The entire burden of checking falls on the caller, and the language provides no help enforcing that check.

The oldest strategy: functions return a special value (typically -1 or NULL) to signal failure. The caller is responsible for checking the return value.

```python
# Simulating the C-style return code pattern in Python
import os
import errno as errno_module

# Simulate a C-style library with return code conventions
ENOENT = 2    # No such file or directory
EACCES = 13   # Permission denied
EINVAL = 22   # Invalid argument

def c_style_open(filename, mode):
    """Returns (fd, errno_code). fd=-1 on error."""
    if not isinstance(filename, str):
        return -1, EINVAL
    if filename == "/etc/shadow":
        return -1, EACCES
    if not filename.startswith("/") and "." not in filename:
        return -1, ENOENT
    # Success: return a fake fd and errno=0
    return 42, 0

def c_style_read(fd, nbytes):
    """Returns (data, errno_code). data=None on error."""
    if fd < 0:
        return None, EINVAL
    if fd == 42:
        return "file contents", 0
    return None, ENOENT

# Caller must check EVERY return value
print("=== C-style return code usage ===")

fd, err = c_style_open("myfile.txt", "r")
if err != 0:
    print(f"open failed: errno={err}")
else:
    data, err = c_style_read(fd, 1024)
    if err != 0:
        print(f"read failed: errno={err}")
    else:
        print(f"read succeeded: {data!r}")

print()
print("=== What happens if caller forgets to check? ===")
fd2, _ = c_style_open("/etc/shadow", "r")   # error ignored
data2, _ = c_style_read(fd2, 1024)          # called with invalid fd
print(f"data2 = {data2!r}")   # None — silently wrong

print()
print("=== The errno global pattern (real C) ===")
# In real C, errno is a global modified as a side effect
# This breaks in multithreaded code unless errno is thread-local
try:
    with open("nonexistent_file_xyz.txt") as f:
        pass
except OSError as e:
    print(f"Python wraps errno: e.errno={e.errno}, e.strerror={e.strerror!r}")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

**The fundamental problem with return codes:** They can be silently ignored. The language provides no mechanism to force the caller to check. In large codebases, forgotten checks cause mysterious bugs far from the actual failure.

> **Critical Thinking Questions 1–3**

**CTQ 1.** In the example above, `c_style_read(fd2, 1024)` is called with an invalid fd and returns `None` silently. What real-world bugs does this pattern cause? Give a concrete example from systems programming.

[[___ your answer here ___]]

**CTQ 2.** The `errno` global variable breaks in multi-threaded C programs. Why? What does this tell you about global mutable state as an error mechanism?

[[___ your answer here ___]]

**CTQ 3.** Return codes have one significant advantage over exceptions: they are explicit in the type signature. `int read(int fd, void *buf, size_t count)` returns -1 on error. How does this relate to the caller-callee contract in a statically typed language?

[[___ your answer here ___]]

---

#### Model 2: Exceptions — Non-Local Control Flow

**Intuition:** Return codes require every caller to check — what if you could install an "emergency exit" somewhere up the call stack, so that any failure anywhere below it automatically jumps to that exit? That is exceptions in a nutshell. The function that detects the error does not need to know who called it or whether anyone will handle the error; it just raises. The nearest matching `except` block, potentially many frames away, catches it. This decoupling is powerful for separating error-detection from error-recovery, but it comes at a cost: the control flow becomes invisible — a function can silently exit through an exception channel that is not visible in its signature.

Exceptions decouple error signaling from error handling. A function can raise an exception at any depth; the nearest matching `catch`/`except` in the call stack handles it.

```python
import traceback

# Python: unchecked exceptions — no declaration required
def parse_int(s):
    return int(s)   # raises ValueError if s is not a valid integer

def read_config(filename):
    with open(filename) as f:   # raises FileNotFoundError or PermissionError
        return f.read()

def process(filename):
    text = read_config(filename)
    value = parse_int(text.strip())
    return value * 2

print("=== Unchecked exceptions (Python style) ===")
print("1. Happy path:")
try:
    # create a temp file
    with open("/tmp/test_config.txt", "w") as f:
        f.write("  42  ")
    print(f"   result = {process('/tmp/test_config.txt')}")
except Exception as e:
    print(f"   error: {e}")

print("2. File not found:")
try:
    print(f"   result = {process('/nonexistent/file.txt')}")
except FileNotFoundError as e:
    print(f"   caught FileNotFoundError: {e}")

print("3. Bad integer:")
try:
    with open("/tmp/test_config.txt", "w") as f:
        f.write("not a number")
    print(f"   result = {process('/tmp/test_config.txt')}")
except ValueError as e:
    print(f"   caught ValueError: {e}")

print("4. Catching too broadly (dangerous):")
try:
    print(f"   result = {process('/nonexistent.txt')}")
except Exception as e:
    print(f"   caught ANYTHING: {type(e).__name__}: {e}")
    # We swallowed a bug — maybe KeyboardInterrupt?

print()
print("=== Exception hierarchy ===")
# Python exceptions form a tree: BaseException > Exception > ...
examples = [ValueError("bad"), TypeError("type"), FileNotFoundError("no file"),
            KeyboardInterrupt(), MemoryError()]
for ex in examples:
    mro = [c.__name__ for c in type(ex).__mro__]
    print(f"  {type(ex).__name__}: {' > '.join(mro[:4])}")

print()
print("=== finally: the cleanup guarantee ===")
class Resource:
    def __init__(self, name):
        self.name = name
        print(f"  opened {name}")
    def close(self):
        print(f"  closed {self.name}")

def risky_operation(r, should_fail):
    try:
        if should_fail:
            raise RuntimeError("something went wrong")
        return "success"
    finally:
        r.close()   # ALWAYS runs, even on exception

r = Resource("db_connection")
try:
    result = risky_operation(r, should_fail=True)
except RuntimeError as e:
    print(f"  caught: {e}")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

> **Watch out! — The bare `except` antipattern**
> Writing `except Exception` (or worse, a bare `except:` with no class at all) catches *everything*, including errors you did not anticipate — misspelled variable names (`NameError`), out-of-memory conditions (`MemoryError`), even `SystemExit`. This silently swallows bugs and makes debugging extremely difficult because the error disappears rather than propagating. Always catch the *most specific* exception type you actually know how to handle (e.g. `except ValueError`, `except FileNotFoundError`). If you need a catch-all for logging, re-raise with `raise` afterward.

##### Checked vs. Unchecked Exceptions

**Java-style checked exceptions:** The compiler forces callers to either catch or declare every checked exception. `IOException`, `SQLException` are checked; `NullPointerException`, `ArrayIndexOutOfBoundsException` are unchecked.

**Python/C++/C#-style unchecked exceptions:** No compile-time enforcement. Callers may or may not catch. The risk: a function silently throws an exception that callers don't know about.

> **Critical Thinking Questions 4–6**

**CTQ 4.** In Python, `except Exception` catches almost every exception. Why is this considered dangerous? What would a disciplined exception-handling policy look like?

[[___ your answer here ___]]

**CTQ 5.** Java's checked exceptions were controversial and were rejected in C# and Kotlin. The argument against: they pollute call signatures with exception declarations that bubble all the way up. The argument for: callers can't ignore failure modes. Which position do you find more compelling? Why?

[[___ your answer here ___]]

**CTQ 6.** Exceptions are a form of non-local control flow — they break the normal call/return pattern. A function that throws "jumps" to a catch block potentially many frames up the call stack. What debugging challenges does this create compared to return codes?

[[___ your answer here ___]]

---

#### Model 3: Option / Maybe — Explicit Absence

**Intuition:** Both return codes and exceptions have a common flaw — the type of a function like `find_user(id)` does not tell you that it might fail. What if the return type itself forced you to reckon with the possibility of failure? The `Option` (or `Maybe`) type does exactly that: instead of returning a `User` (which might secretly be `None`) or raising an exception (which is invisible in the type), the function returns `Some(user)` or `Nothing`. The type is now `Option[User]`, and the language (or the type checker) will not let you use the inner user value without first checking which variant you got. This is the functional programming answer to null-pointer crashes.

Many errors boil down to "there is no value here." The **Option** type (Haskell's `Maybe`, Rust's `Option`, Scala's `Option`) makes absence explicit in the type system rather than using `null` or raising an exception.

```python
from __future__ import annotations
from dataclasses import dataclass
from typing import TypeVar, Generic, Callable

T = TypeVar("T")
U = TypeVar("U")

@dataclass(frozen=True)
class Some(Generic[T]):
    value: T
    def is_some(self): return True
    def is_none(self): return False
    def unwrap(self): return self.value
    def map(self, f: Callable[[T], U]) -> "Option[U]":
        return Some(f(self.value))
    def and_then(self, f: Callable[[T], "Option[U]"]) -> "Option[U]":
        return f(self.value)
    def unwrap_or(self, default: T) -> T:
        return self.value
    def __repr__(self): return f"Some({self.value!r})"

@dataclass(frozen=True)
class Nothing:
    def is_some(self): return False
    def is_none(self): return True
    def unwrap(self): raise ValueError("called unwrap() on Nothing")
    def map(self, f): return self
    def and_then(self, f): return self
    def unwrap_or(self, default): return default
    def __repr__(self): return "Nothing"

Option = Some | Nothing
NOTHING = Nothing()

# Functions that might fail return Option instead of raising
def safe_div(x: float, y: float) -> Option:
    if y == 0:
        return NOTHING
    return Some(x / y)

def safe_head(lst: list) -> Option:
    if not lst:
        return NOTHING
    return Some(lst[0])

def parse_positive_int(s: str) -> Option:
    try:
        n = int(s)
        return Some(n) if n > 0 else NOTHING
    except ValueError:
        return NOTHING

print("=== Option/Maybe usage ===")
print(safe_div(10, 2))        # Some(5.0)
print(safe_div(10, 0))        # Nothing
print(safe_head([1, 2, 3]))   # Some(1)
print(safe_head([]))          # Nothing

print()
print("=== Chaining with and_then (flatMap) ===")
# Process: parse → divide → take head
def pipeline(s: str, divisor: float) -> Option:
    return (parse_positive_int(s)
            .map(float)
            .and_then(lambda x: safe_div(x, divisor)))

print(f"pipeline('12', 4)   = {pipeline('12', 4)}")    # Some(3.0)
print(f"pipeline('12', 0)   = {pipeline('12', 0)}")    # Nothing (div by zero)
print(f"pipeline('-5', 4)   = {pipeline('-5', 4)}")    # Nothing (not positive)
print(f"pipeline('abc', 4)  = {pipeline('abc', 4)}")   # Nothing (parse fail)

print()
print("=== unwrap_or for defaults ===")
result = pipeline("bad", 4).unwrap_or(0.0)
print(f"pipeline('bad', 4).unwrap_or(0.0) = {result}")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

> **Critical Thinking Questions 7–9**

**CTQ 7.** The Option type forces callers to handle the absence case explicitly (they can't just use the value without checking). How does this differ from the behavior of `None` in Python, where calling a method on `None` raises `AttributeError` at runtime?

[[___ your answer here ___]]

**CTQ 8.** `and_then` (also called `flatMap` or `>>=` in Haskell) sequences Option computations so that if any step returns `Nothing`, the whole chain returns `Nothing`. What is the control flow equivalent of this? (Hint: think about what happens in an imperative `if ... return None` chain.)

[[___ your answer here ___]]

**CTQ 9.** Python's `Optional[T]` type hint (`from typing import Optional`) annotates a value that may be `None`. How does this differ from the `Option` type implemented above, in terms of static guarantees?

[[___ your answer here ___]]

> **Watch out! — Exceptions break referential transparency**
> In functional programming, a function is *referentially transparent* if you can replace a call with its return value without changing the program's meaning. A function that raises an exception is **not** referentially transparent — calling `parse_int("abc")` does not simply produce a value; it may instead unwind the call stack. This is why purely functional languages like Haskell avoid exceptions in pure code entirely, using `Maybe`/`Either` instead. When you write functional-style pipelines in Python (chaining `.map` and `.and_then`), mixing in `raise` inside those lambdas defeats the whole discipline.

---

#### Model 4: Result / Either — Typed Errors

**Intuition:** `Option`/`Maybe` answers the question "did it succeed or not?" but throws away the reason for failure — `Nothing` is the same whether the file was missing, the network timed out, or the input was malformed. `Result`/`Either` extends the idea: a computation returns `Ok(value)` on success or `Err(error)` on failure, where `error` is a *structured value* you define. This means callers know not just that something went wrong, but *what* went wrong, and they can pattern-match on the specific error type to recover differently for different failures. Rust has made this pattern central to its standard library, and the `?` operator makes the boilerplate nearly invisible.

Option discards error information ("it failed" but not "why it failed"). **Result** (Rust, Swift) or **Either** (Haskell) carries both the success value and a structured error value.

```python
from __future__ import annotations
from dataclasses import dataclass
from typing import TypeVar, Generic, Callable

T = TypeVar("T")
E = TypeVar("E")
U = TypeVar("U")

@dataclass(frozen=True)
class Ok(Generic[T]):
    value: T
    def is_ok(self): return True
    def is_err(self): return False
    def unwrap(self): return self.value
    def unwrap_err(self): raise ValueError("called unwrap_err() on Ok")
    def map(self, f): return Ok(f(self.value))
    def map_err(self, f): return self
    def and_then(self, f): return f(self.value)
    def __repr__(self): return f"Ok({self.value!r})"

@dataclass(frozen=True)
class Err(Generic[E]):
    error: E
    def is_ok(self): return False
    def is_err(self): return True
    def unwrap(self): raise ValueError(f"called unwrap() on Err({self.error!r})")
    def unwrap_err(self): return self.error
    def map(self, f): return self
    def map_err(self, f): return Err(f(self.error))
    def and_then(self, f): return self
    def __repr__(self): return f"Err({self.error!r})"

# Result = Ok[T] | Err[E]
# Richer errors: use a dataclass hierarchy
@dataclass(frozen=True)
class ParseError:
    input: str
    message: str

@dataclass(frozen=True)
class MathError:
    operation: str
    message: str

@dataclass(frozen=True)
class IOError_:
    filename: str
    message: str

def parse_number(s: str):
    try:
        return Ok(float(s))
    except ValueError:
        return Err(ParseError(s, f"cannot parse {s!r} as number"))

def safe_sqrt(x: float):
    if x < 0:
        return Err(MathError("sqrt", f"sqrt of negative: {x}"))
    import math
    return Ok(math.sqrt(x))

def load_number(filename: str):
    try:
        with open(filename) as f:
            return parse_number(f.read().strip())
    except FileNotFoundError:
        return Err(IOError_(filename, "file not found"))

print("=== Result type ===")
print(parse_number("3.14"))     # Ok(3.14)
print(parse_number("xyz"))      # Err(ParseError(...))
print(safe_sqrt(9.0))           # Ok(3.0)
print(safe_sqrt(-1.0))          # Err(MathError(...))

print()
print("=== Chaining Results ===")
def process(s: str):
    return parse_number(s).and_then(safe_sqrt)

print(f"process('9')   = {process('9')}")
print(f"process('-1')  = {process('-1')}")
print(f"process('abc') = {process('abc')}")

print()
print("=== Pattern matching on Result (Python 3.10+) ===")
for test in ["16", "-4", "not_a_number"]:
    result = process(test)
    match result:
        case Ok(value=v):
            print(f"  sqrt({test}) = {v:.4f}")
        case Err(error=ParseError(input=i, message=m)):
            print(f"  parse error for {i!r}: {m}")
        case Err(error=MathError(operation=op, message=m)):
            print(f"  math error in {op}: {m}")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

> **Critical Thinking Questions 10–12**

**CTQ 10.** `Err` carries a *typed* error value. What advantage does this have over Python's exception hierarchy where you catch by exception class? Give a scenario where typed errors are significantly cleaner.

[[___ your answer here ___]]

**CTQ 11.** In Rust, if you call `.unwrap()` on an `Err`, the program panics (crashes with a message). This is intentional: `unwrap()` is a way of saying "I know this can't fail, and if it does, crash loudly." How does this compare to the `except Exception` anti-pattern in Python?

[[___ your answer here ___]]

**CTQ 12.** Rust's `?` operator desugars to: "if this is `Err`, return the error from the current function; otherwise, unwrap the `Ok` value." Implement a Python decorator or helper that provides similar behavior for the `Result` type above:

```python
# Your implementation of a "question mark operator" helper
# (This one doesn't need @LIA.eval — think about it with your group)
```

How would you use it to write a multi-step `Result`-chaining function without deeply nested `and_then` calls?

[[___ your answer here ___]]

---

#### Model 5: Error Propagation in Your Interpreter

**Intuition:** The previous models were abstract; now apply them concretely. When your interpreter evaluates `x + y` and `x` is undefined, what should happen? The naive answer — let Python raise a `KeyError` — is wrong: the user of your language sees a Python traceback, not an error in *their* language. Good interpreter error handling requires two things: (1) catching every possible failure and converting it into an error type your interpreter owns, and (2) attaching source location information (line, column) so the user can find the problem. This model shows how to build a structured exception hierarchy for an interpreter and attach `SourceLocation` objects.

Your interpreter must handle runtime errors: undefined variables, type mismatches, division by zero, stack overflow. How you design this affects usability.

```python
from dataclasses import dataclass
from typing import Any, Optional

@dataclass
class SourceLocation:
    line: int
    column: int
    def __str__(self):
        return f"line {self.line}, col {self.column}"

@dataclass
class InterpreterError(Exception):
    message: str
    location: Optional[SourceLocation] = None
    def __str__(self):
        loc = f" at {self.location}" if self.location else ""
        return f"RuntimeError{loc}: {self.message}"

@dataclass
class UndefinedVariableError(InterpreterError):
    name: str = ""
    def __str__(self):
        loc = f" at {self.location}" if self.location else ""
        return f"UndefinedVariable{loc}: '{self.name}' is not defined"

@dataclass
class TypeMismatchError(InterpreterError):
    expected: str = ""
    got: str = ""
    def __str__(self):
        loc = f" at {self.location}" if self.location else ""
        return f"TypeError{loc}: expected {self.expected}, got {self.got}"

@dataclass
class DivisionByZeroError(InterpreterError):
    def __str__(self):
        loc = f" at {self.location}" if self.location else ""
        return f"DivisionByZero{loc}"

# A mini environment + evaluator that produces good errors
class Environment:
    def __init__(self, parent=None):
        self.bindings = {}
        self.parent = parent

    def lookup(self, name: str, loc: SourceLocation = None) -> Any:
        if name in self.bindings:
            return self.bindings[name]
        if self.parent:
            return self.parent.lookup(name, loc)
        raise UndefinedVariableError(
            message=f"'{name}' is not defined",
            location=loc,
            name=name
        )

    def define(self, name: str, value: Any):
        self.bindings[name] = value

def eval_binop(op: str, left: Any, right: Any, loc: SourceLocation) -> Any:
    if op == "+":
        if isinstance(left, (int, float)) and isinstance(right, (int, float)):
            return left + right
        if isinstance(left, str) and isinstance(right, str):
            return left + right
        raise TypeMismatchError(
            message=f"operator '+' requires matching numeric or string operands",
            location=loc,
            expected="int/float or str",
            got=f"{type(left).__name__} and {type(right).__name__}"
        )
    if op == "/":
        if not isinstance(left, (int, float)):
            raise TypeMismatchError(message="'/' requires numbers", location=loc,
                                    expected="number", got=type(left).__name__)
        if right == 0:
            raise DivisionByZeroError(message="division by zero", location=loc)
        return left / right
    raise InterpreterError(f"unknown operator '{op}'", loc)

print("=== Good interpreter error messages ===")
env = Environment()
env.define("x", 10)
env.define("name", "Alice")

loc1 = SourceLocation(3, 5)
loc2 = SourceLocation(7, 12)
loc3 = SourceLocation(9, 8)

test_cases = [
    ("x + 5",       lambda: eval_binop("+", env.lookup("x"), 5, loc1)),
    ("x / 0",       lambda: eval_binop("/", env.lookup("x"), 0, loc2)),
    ("x + name",    lambda: eval_binop("+", env.lookup("x"), env.lookup("name"), loc3)),
    ("undefined_var", lambda: env.lookup("undefined_var", SourceLocation(11, 3))),
]

for label, fn in test_cases:
    try:
        result = fn()
        print(f"  {label} => {result}")
    except InterpreterError as e:
        print(f"  {label} => {e}")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

> **Critical Thinking Questions 13–15**

**CTQ 13.** The `SourceLocation` dataclass carries line and column numbers. Where in your interpreter pipeline would you attach source locations to AST nodes? (Hint: the lexer knows the position of each token.)

[[___ your answer here ___]]

**CTQ 14.** The evaluator raises `InterpreterError` subclasses. This is a form of exception-based error propagation. What would the `Result`-based alternative look like? What are the tradeoffs between the two approaches for an interpreter?

[[___ your answer here ___]]

**CTQ 15.** When an error occurs during the evaluation of a deeply nested expression (e.g., inside a function call inside a `let` body inside another function), what information would you want in the error message? How does a **stack trace** differ from a single source location?

[[___ your answer here ___]]

---

#### Model 6: Comparative Survey

**Intuition:** You have now seen four strategies in detail. This model puts them side by side on a single, concrete task — "find an element in a list, or fail" — so you can feel the ergonomic difference directly. Each strategy makes a different trade: how much the caller is trusted, how much information a failure carries, and how well errors compose when you chain multiple operations. As you read, think about which row of the comparison table you would choose for a new language you were designing, and why.

```python
# Demonstrate three idioms for "find element or fail" in Python
from typing import Optional

data = [10, 20, 30, 40, 50]

# Strategy 1: Return None (sentinel value)
def find_sentinel(lst, target) -> Optional[int]:
    for i, v in enumerate(lst):
        if v == target:
            return i
    return None   # caller must check

# Strategy 2: Raise exception
def find_exception(lst, target) -> int:
    for i, v in enumerate(lst):
        if v == target:
            return i
    raise ValueError(f"{target} not found in list")

# Strategy 3: Return (value, ok) tuple (Go style)
def find_tuple(lst, target):
    for i, v in enumerate(lst):
        if v == target:
            return i, True
    return -1, False

# Strategy 4: Return Result type
from dataclasses import dataclass

@dataclass
class NotFoundError:
    target: object

def find_result(lst, target):
    for i, v in enumerate(lst):
        if v == target:
            return ("ok", i)
    return ("err", NotFoundError(target))

print("=== Comparing four error strategies ===")
for target in [30, 99]:
    print(f"\nSearching for {target}:")
    
    r = find_sentinel(data, target)
    print(f"  sentinel:  {r!r}  (caller must check for None)")
    
    try:
        r = find_exception(data, target)
        print(f"  exception: found at index {r}")
    except ValueError as e:
        print(f"  exception: raised {e!r}")
    
    idx, ok = find_tuple(data, target)
    print(f"  tuple:     ({idx}, {ok})  (caller must check ok)")
    
    tag, val = find_result(data, target)
    if tag == "ok":
        print(f"  result:    Ok({val})")
    else:
        print(f"  result:    Err({val})")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

> **Watch out! — Go-style (value, ok) tuples require constant discipline**
> The `find_tuple` pattern — returning `(result, ok)` and expecting callers to check the `ok` flag — has the same fundamental flaw as C return codes: nothing prevents a caller from writing `idx, _ = find_tuple(data, 99)` and then using `idx` as if it were valid. In a large Go codebase the `if err != nil { return ..., err }` check must appear at *every* call site, and a single omission silently propagates a bad value. The `Result` type wins precisely because the bad value is structurally impossible to use without first unwrapping it.

> **Critical Thinking Questions 16–18**

**CTQ 16.** Fill in this comparison table for your group:

| Strategy | Can be ignored? | Carries error info? | Composable? | Statically checked? |
|----------|----------------|--------------------|-----------|--------------------|
| Return None/sentinel | | | | |
| Exception | | | | |
| (value, ok) tuple | | | | |
| Result/Either type | | | | |

Which row has the best profile? Why might languages still use the others?

[[___ your answer here ___]]

**CTQ 17.** Go's (value, error) tuple idiom has been criticized for being verbose — every call site requires `if err != nil { return nil, err }`. The `Result` type with `?` in Rust addresses this. What is the fundamental insight that makes `?` (or monadic bind `>>=`) cleaner than manual propagation?

[[___ your answer here ___]]

**CTQ 18.** **Algebraic effects** (a research direction in PL) generalize both exceptions and coroutines: you define an "effect" (like `raise IOException`), and the effect handler is separate from both the raiser and the call chain. How does this differ from exception handling? What new flexibility does it provide?

[[___ your answer here ___]]

---

#### Multiple Choice Review

**Question 1.** In Python, `except Exception` catches:

- [( )] All exceptions including `SystemExit` and `KeyboardInterrupt`
- [(X)] Most exceptions, but not `BaseException` subclasses like `SystemExit`
- [( )] Only subclasses of `RuntimeError`
- [( )] Only exceptions explicitly raised with `raise`

**Question 2.** Rust's `Option<T>` type prevents:

- [( )] All runtime panics
- [( )] Division by zero
- [(X)] Using a potentially-absent value without first checking whether it is present
- [( )] Stack overflow from deep recursion

**Question 3.** Java's checked exceptions require the caller to:

- [(X)] Either catch the exception or declare it in the method signature
- [( )] Catch the exception in the same function that throws it
- [( )] Use a `Result` type instead of throwing
- [( )] Handle all exceptions with a single `catch (Exception e)`

**Question 4.** The `finally` block in Python runs:

- [( )] Only when no exception was raised
- [( )] Only when an exception was raised and caught
- [( )] Only when an exception was raised and not caught
- [(X)] Always, whether or not an exception was raised or caught

---

#### Exercises

**Exercise 1.** Implement a `safe_chain` decorator that converts any function returning a value (or raising an exception) into a function returning `Result`. Then use it to build a pipeline without explicit try/except at every step:

```python
from dataclasses import dataclass
from typing import Any, Callable

@dataclass(frozen=True)
class Ok:
    value: Any
    def and_then(self, f): return f(self.value)
    def map(self, f): return Ok(f(self.value))
    def __repr__(self): return f"Ok({self.value!r})"

@dataclass(frozen=True)
class Err:
    error: Any
    def and_then(self, f): return self
    def map(self, f): return self
    def __repr__(self): return f"Err({self.error!r})"

def safe(fn: Callable) -> Callable:
    def wrapper(*args, **kwargs):
        try:
            return Ok(fn(*args, **kwargs))
        except Exception as e:
            return Err(str(e))
    return wrapper

# Wrap risky operations
safe_int  = safe(int)
safe_sqrt = safe(__import__('math').sqrt)
safe_div  = safe(lambda a, b: a / b)

# Build a pipeline using and_then
for s in ["16", "-4", "abc"]:
    result = safe_int(s).map(float).and_then(safe_sqrt)
    print(f"sqrt(int({s!r})) = {result}")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

**Exercise 2.** Implement a "stack trace" for your interpreter. Maintain a call stack (list of strings) that records function names as they are entered/exited. When an error occurs, attach the current stack trace to the error:

```python
from dataclasses import dataclass, field
from typing import List, Any, Optional

call_stack: List[str] = []

@dataclass
class InterpreterError(Exception):
    message: str
    stack_trace: List[str] = field(default_factory=list)
    def __str__(self):
        trace = "\n  ".join(reversed(self.stack_trace))
        return f"Error: {self.message}\nCall stack:\n  {trace}"

def enter_function(name: str):
    call_stack.append(name)

def exit_function():
    call_stack.pop()

def raise_error(message: str):
    raise InterpreterError(message, list(call_stack))

# Simulate a call chain: main → foo → bar → baz → error
def baz():
    enter_function("baz")
    try:
        raise_error("undefined variable 'x'")
    finally:
        exit_function()

def bar():
    enter_function("bar")
    try:
        baz()
    finally:
        exit_function()

def foo():
    enter_function("foo")
    try:
        bar()
    finally:
        exit_function()

def main():
    enter_function("main")
    try:
        foo()
    finally:
        exit_function()

try:
    main()
except InterpreterError as e:
    print(e)
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

**Exercise 3.** Compare Python's `Optional[T]` type hint (from `typing`) with the `Option` dataclass from Model 3. Write a function that accepts `Optional[int]` and one that accepts your `Option` type. Show what happens at runtime when a caller passes `None` vs. `Nothing()` to each:

```python
from typing import Optional
from dataclasses import dataclass

@dataclass(frozen=True)
class Some:
    value: object
    def map(self, f): return Some(f(self.value))
    def unwrap_or(self, d): return self.value

@dataclass(frozen=True)
class Nothing:
    def map(self, f): return self
    def unwrap_or(self, d): return d

Option = Some | Nothing

def double_optional(x: Optional[int]) -> Optional[int]:
    if x is None:
        return None
    return x * 2

def double_option(x: Option) -> Option:
    return x.map(lambda v: v * 2)

print("Optional[int]:")
print(f"  double_optional(5)    = {double_optional(5)}")
print(f"  double_optional(None) = {double_optional(None)}")
# What happens if caller ignores the hint and passes a string?
print(f"  double_optional('hi') = {double_optional('hi')}")  # runtime error or wrong answer?

print()
print("Option type:")
print(f"  double_option(Some(5))   = {double_option(Some(5))}")
print(f"  double_option(Nothing()) = {double_option(Nothing())}")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

**Exercise 4.** Add structured error reporting to a mini expression evaluator. Extend the evaluator to collect ALL errors in an expression (not just the first one) before reporting them:

```python
from dataclasses import dataclass, field
from typing import List, Any

@dataclass
class EvalError:
    expr: str
    message: str
    def __str__(self): return f"  [{self.expr}]: {self.message}"

def eval_expr(expr: str, env: dict) -> tuple:
    """Returns (value_or_None, list_of_errors)."""
    errors: List[EvalError] = []
    
    # Very simplified: handle 'a + b', 'a / b', integer literals, variable names
    expr = expr.strip()
    
    for op in ["+", "-", "*", "/"]:
        if op in expr:
            parts = expr.split(op, 1)
            left_s, right_s = parts[0].strip(), parts[1].strip()
            left_v, left_errs = eval_expr(left_s, env)
            right_v, right_errs = eval_expr(right_s, env)
            errors.extend(left_errs)
            errors.extend(right_errs)
            if left_v is None or right_v is None:
                return None, errors
            if op == "/" and right_v == 0:
                errors.append(EvalError(expr, "division by zero"))
                return None, errors
            ops = {"+": lambda a,b: a+b, "-": lambda a,b: a-b,
                   "*": lambda a,b: a*b, "/": lambda a,b: a/b}
            return ops[op](left_v, right_v), errors
    
    try:
        return int(expr), errors
    except ValueError:
        pass
    
    if expr in env:
        return env[expr], errors
    
    errors.append(EvalError(expr, f"undefined variable '{expr}'"))
    return None, errors

env = {"x": 10, "y": 5}
tests = ["x + y", "x / 0", "x + z", "10 + 3"]

for t in tests:
    value, errors = eval_expr(t, env)
    if errors:
        print(f"eval({t!r}): ERRORS:")
        for e in errors:
            print(e)
    else:
        print(f"eval({t!r}) = {value}")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

**Exercise 5.** Design an error hierarchy for a complete interpreter. Create a class hierarchy of `InterpreterError` subclasses covering: lexer errors (invalid character, unterminated string), parser errors (unexpected token, missing closing paren), and runtime errors (undefined variable, type mismatch, division by zero, stack overflow). Write a function that pretty-prints any error with its category, location, and a helpful suggestion:

```python
from dataclasses import dataclass
from typing import Optional

@dataclass
class SourceLocation:
    line: int
    col: int
    source_line: str = ""
    def __str__(self):
        pointer = " " * self.col + "^"
        return f"  {self.source_line}\n  {pointer}"

@dataclass
class InterpreterError(Exception):
    message: str
    location: Optional[SourceLocation] = None
    suggestion: str = ""
    
    @property
    def category(self): return "Error"
    
    def pretty(self) -> str:
        parts = [f"{self.category}: {self.message}"]
        if self.location:
            parts.append(str(self.location))
        if self.suggestion:
            parts.append(f"  Hint: {self.suggestion}")
        return "\n".join(parts)

@dataclass
class LexError(InterpreterError):
    @property
    def category(self): return "LexError"

@dataclass
class ParseError(InterpreterError):
    @property
    def category(self): return "ParseError"

@dataclass
class UndefinedVar(InterpreterError):
    name: str = ""
    @property
    def category(self): return "RuntimeError"

@dataclass
class TypeError_(InterpreterError):
    expected: str = ""
    got: str = ""
    @property
    def category(self): return "TypeError"

# Demo
errors = [
    LexError("unexpected character '@'",
             SourceLocation(3, 7, "  let x = @value"),
             "Valid identifiers start with a letter or underscore"),
    ParseError("expected ')' but found 'end of input'",
               SourceLocation(5, 20, "  (let x (+ x 1)"),
               "Check for unmatched parentheses"),
    UndefinedVar("variable 'y' is not defined",
                 SourceLocation(8, 12, "  let z = x + y"),
                 "Did you mean 'x'? Or define 'y' before using it",
                 name="y"),
    TypeError_("operator '+' requires numeric operands",
               SourceLocation(11, 10, "  print(1 + \"hello\")"),
               "Use str() to convert numbers to strings, or int() for the reverse",
               expected="number", got="str"),
]

for err in errors:
    print(err.pretty())
    print()
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

---

#### Reflection

1. Your interpreter currently raises Python exceptions for runtime errors. A user of your language sees a Python traceback rather than a clean error message. Describe the two changes needed to give users clean, localized error messages.

2. A language designer is choosing between checked exceptions (Java-style) and `Result` types (Rust-style) for a new systems language. The language emphasizes correctness and will be used for network services. Which would you recommend, and what tradeoff are you accepting?

3. Go's philosophy is "errors are values" — errors are returned, not thrown. Haskell's philosophy is "errors are types" — absence and failure are encoded in the type system. Python's philosophy is "errors are exceptions" — errors interrupt control flow. Each philosophy has a consistent design vision. Which appeals most to you, and why?

---

#### Further Reading

- **Python docs:** `exceptions` — the full exception hierarchy
- **Rust book:** Chapter 9, "Error Handling" — `panic!`, `Result`, and the `?` operator
- **Haskell wiki:** `Maybe` and `Either` monads
- **Paper:** *Exceptional Syntax* — Benton & Kennedy (2001), on typed exceptions
- **Talk:** *Inventing on Principle* — Bret Victor (mentions error feedback loops)
- **Research:** Algebraic effects and handlers — Plotkin & Pretnar (2009); the Koka language
- **Book:** *Crafting Interpreters* — Robert Nystrom, Chapter 14 (runtime errors with source locations)

---

*End of Activity — Error Handling: Return Codes, Exceptions, Option/Maybe, Result/Either, Interpreter Error Design*
