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

---
**🛑 In-class work stops here.** Everything below is homework and going-deeper material — attempt the exercises before the related assignment.

# Going Deeper (at home): Closures vs. Objects

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

## Going Deeper (at home, Optional Appendices)

The core lesson above stands on its own. The deep dives below stay in this file because they feed directly into the Interpreter assignment and the team project — but they are at-home material, not part of the class session:

- Coroutines and Generators: Pausable Computation
- Error Handling: From Return Codes to Algebraic Effects

## Going Deeper (at home): Coroutines and Generators — Pausable Computation

> **Opening hook:** Imagine a vending machine. A regular function is like a vending machine that dumps every item it will ever produce onto the floor the moment you press the button — all at once, whether you want them yet or not. A **generator** is a vending machine that produces exactly one item each time you press the button, remembers where it left off, and waits patiently until you press again. The machine's internal state — which slot it was at, how many remain — is frozen between presses. That frozen state is the essence of a coroutine.

#### Learning Goals

By the end of this activity, you will be able to:

- Define coroutines and generators and explain how `yield` captures a continuation to pause and resume computation
- Trace the execution of a generator function step-by-step, predicting what value each `next()` call produces
- Implement lazy infinite sequences using generator functions and compare their memory use to eager list-based equivalents
- Explain how `async`/`await` desugars to a state machine and identify where suspension points occur
- Extend a simple interpreter to support generator objects with `yield` and `send` semantics

> **Prerequisites:** Python functions and closures; basic familiarity with the idea of a continuation (see Direction B of the Functional assignment)
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
> If the term "continuation" feels fuzzy, skim Direction B of the Functional assignment. If Python closures feel shaky, review how `def` inside `def` works and what a stack frame contains.

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

> **Going further:** the material that used to live here — generator basics, eager vs. lazy sequences, and generator pipelines — is covered in class in the *Modern Language Features* activity, and lazy evaluation is covered in depth in the dedicated tutorial: [Haskell Essentials for the Programming Languages Course](https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374/gh-pages/_pages/Tutorials/tutorial-haskell-essentials.md). Explore it when your project or curiosity calls for it.

---

#### Model 2: `yield` as a Two-Way Channel (`send` and `throw`)

> **Going further:** `yield` is not only an output channel — `gen.send(value)` resumes a paused generator *and delivers a value into it*, and `gen.throw(exc)` raises an exception at the paused `yield`. This two-way protocol is what made generator-based coroutines possible before `async`/`await`. The details are a self-study topic: see the Python reference on generator-iterator methods (`send`, `throw`, `close`).

---

#### Model 3: How `yield` Captures a Continuation

> **Going further:** the material that used to live here — `yield` seen as a captured continuation, manual CPS transformation, and simulated `call/cc` — now lives where it is assessed: **Direction B of the [Functional assignment](https://www.billmongan.com/Ursinus-CS374-Fall2026/Assignments/Functional) builds on this material** — read that direction's section before choosing it.

---

#### Model 4: `async`/`await` — Generators Over I/O

> **Going further:** `async`/`await`, event loops, and the "function color" problem are a self-study topic — Python's `asyncio` documentation and the essay "What Color Is Your Function?" (Bob Nystrom) are the places to start. The mechanism underneath is exactly the paused-and-resumed generator you build in Model 5 below.

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

**Question 2.** A generator captures its execution state by:

- [( )] Allocating a new heap object for each yielded value
- [( )] Using OS threads with mutex locks
- [(X)] Freezing the stack frame (locals, instruction pointer) as a heap-allocated object
- [( )] Copying all local variables into a global dictionary

---

#### Exercises

> *(The generator-pipeline, scheduler, and memoization exercises that used to live here duplicated the lazy-streams material now covered by the Haskell Essentials tutorial and the Functional assignment.)*

**Exercise 1.** Extend the mini interpreter from Model 5 to support a `while` loop inside generator bodies. Add a `While` AST node and a `Assign` node so you can write:

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

#### Reflection

1. Generators, coroutines, and async/await are all variations on the same idea: pausable computation. Map each to the continuation-passing-style ideas from Direction B of the Functional assignment: where is the continuation stored in each case?

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

## Going Deeper (at home): Error Handling — From Return Codes to Algebraic Effects

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

> **Going further:** the material that used to live here — the `Option`/`Maybe` type that makes absence explicit instead of using `null` — is covered in depth in the dedicated tutorial: [Haskell Essentials for the Programming Languages Course](https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374/gh-pages/_pages/Tutorials/tutorial-haskell-essentials.md) (the Maybe monad). The `Result`/`Either` pattern in Model 4 below generalizes it by carrying the *reason* for failure.

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

> **Going further:** the side-by-side survey that used to live here — sentinel `None` vs. exception vs. `(value, ok)` tuple vs. `Result` for the same "find element or fail" task, with a comparison table across C, Go, Java, Python, Rust, and Haskell — is a worthwhile self-study exercise: implement all four idioms yourself and decide which row your team's language will choose (record it in `SEMANTICS.md`).

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

**Exercise 3.** Add structured error reporting to a mini expression evaluator. Extend the evaluator to collect ALL errors in an expression (not just the first one) before reporting them:

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

**Exercise 4.** Design an error hierarchy for a complete interpreter. Create a class hierarchy of `InterpreterError` subclasses covering: lexer errors (invalid character, unterminated string), parser errors (unexpected token, missing closing paren), and runtime errors (undefined variable, type mismatch, division by zero, stack overflow). Write a function that pretty-prints any error with its category, location, and a helpful suggestion:

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
