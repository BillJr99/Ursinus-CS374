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

> **CTQ 5.1** All three lambdas captured the same `i` binding. After the loop, what is `i`? Why do all three lambdas return 2?

> **CTQ 5.2** Fix 1 uses `lambda i=i: i`. The outer `i` (the default argument value) is evaluated at *definition time*, capturing the current value. Why does this work, while the capture in the original version doesn't?

> **CTQ 5.3** Fix 2 uses a factory function `make_fn(i)` that creates a new scope. Draw the environment diagram showing why each returned lambda has a *different* captured environment.

> **CTQ 5.4** JavaScript's historic `var` scoping caused the same bug; `let` was introduced to fix it. How does `let` create "per-iteration" scope? Why can't `var` do this?

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

> **CTQ 6.1** In the closure-based counter, `count` is a shared mutable cell. In the object-based counter, `self._count` is a field. What is the structural difference? What is the conceptual difference?

> **CTQ 6.2** The closure counter uses a list `[start]` to work around Python's scoping rules for `nonlocal`. Rewrite it using `nonlocal count` (Python 3) instead of a list. Why is `nonlocal` cleaner?

> **CTQ 6.3** Languages like OCaml and Haskell have closures but no classes. Languages like Java (pre-lambda) have classes but no closures (lambdas are objects). From what you now know about the implementation of each, argue: which is more fundamental?

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
