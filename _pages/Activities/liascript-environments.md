<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://github.com/BillJr99/Ursinus-CS374-Fall2026/blob/gh-pages/_pages/Activities/liascript-environments.md or locally via https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374-Fall2026/gh-pages/_pages/Activities/liascript-environments.md

import: https://raw.githubusercontent.com/liascript/CodeRunner/master/README.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

# Environments: Implementing Scope

Every running program needs a way to answer the question: "what value does the name `x` refer to right now?" An **environment** is that answer — a data structure that maps names to values, much like a phone book maps names to numbers. But a single phone book is not enough: when you enter a new block or function, you need a fresh page that can shadow entries from the outer book, and when you leave, that page is torn out and discarded. Nested environments form a **chain of phone books**, each one consulted first, then deferring to the one above when a name is not found locally. Understanding how to build and manipulate this chain is the foundation of every scope rule your interpreter will enforce.

## Learning Goals

By the end of this activity, you will be able to:

- Implement an `Environment` class as a chain of dictionaries linked by parent pointers and explain why a single flat dictionary cannot correctly model nested scope
- Trace the four environment operations — `define`, `lookup`, `assign`, and scope entry/exit — on a program with nested blocks
- Predict the value printed at each point in a program with shadowed variable names, explaining each step of the chain-walk lookup
- Construct the environment chain diagram for a given program snapshot and identify the lifetime and scope of each binding
- Integrate the `Environment` class into a tree-walking interpreter so that block statements correctly push and pop scopes

> **Before You Begin:** This activity assumes you can:
> - Explain the difference between *scope* (where a name is visible in source text) and *lifetime* (how long its storage exists at runtime)
> - Read and write basic Python dictionaries and classes (including `__init__`, instance variables, and simple `while` loops)
> - Describe what static (lexical) scoping means: a name resolves to the declaration in the innermost enclosing block at the point where the name appears in the source
>
> If any of these feel shaky, review them first.

Yesterday's scope rules become today's data structure: the **environment**, a chain of dictionaries linked by parent pointers, in which lookup walks outward exactly as static scoping's "innermost enclosing declaration" demands. This two-day module builds the `Environment` class your interpreter assignment requires, and rehearses every operation on it until the picture is second nature. The arc: **why one dict fails $\rightarrow$ the chain $\rightarrow$ the four operations $\rightarrow$ blocks creating and discarding scopes**.

---

## Directions and Group Roles

Work in your POGIL team with rotated roles (**Manager**, **Recorder**, **Presenter**, **Reflector**). Consider each model and question individually first, then discuss with your group. The Recorder posts answers to the Class Activity Questions discussion board; the Presenter reports out areas of disagreement or alternative approaches. After class, respond to the reflective prompt individually in your notebook.

---

# Part I: The Chain (Day 1)

## 1. One Dictionary Cannot Shadow

Your interpreter's flat `env = {}` makes every variable global: a block that declares `x` overwrites any outer `x` forever, and nothing is discarded when the block ends. The cure mirrors the textual nesting itself: **one dictionary per scope, each holding a pointer to its parent (the enclosing scope)**. Entering a block pushes a fresh child environment; leaving it simply returns to the parent, and the child's bindings vanish with it.

**Lookup walks the chain.** To resolve `x`: check the current environment; if absent, ask the parent; continue to the global; fail (a name error) only past the root:

$$
\text{lookup}(x, E) = \begin{cases} E.\text{vars}[x] & x \in E.\text{vars} \\ \text{lookup}(x, E.\text{parent}) & \text{otherwise, if a parent exists} \\ \text{NameError} & \text{at the root} \end{cases}
$$

This walk *is* static scope: innermost first, outward through textual enclosure.

---

**Intuition for Model 1:** Imagine you are filling out a crossword puzzle on a notepad. You write global clues at the top of the page, then tear off a sticky note for each inner section and place it on top. When you look up a clue, you check the sticky note first; if it is not there, you look at the page beneath. When you finish the section, you peel off the sticky note and discard it — the clues written on it are gone, and any clues from the page that it was covering are visible again. This model lets you trace exactly that process with a two-scope program.

## Model 1: Paper Machine

The program (block braces create scopes):

```
let a = 1;
let b = 2;
{
    let b = 20;
    let c = 30;
    print a + b + c;     # line P1
}
print b;                 # line P2
```

### Critical Thinking Questions

1. Draw the environment picture at line P1: two boxes (global and block), their contents, and the parent arrow. The Recorder keeps the drawing.
2. Resolve each of `a`, `b`, `c` at P1 by walking the chain; report each walk's length and the printed value.
3. At P2, the block environment is gone. What does `print b` produce, and what happened to the binding `c`? Name the concept (scope, lifetime, or both?) that just ended for `c`.
4. Predict what `print c` at P2 would do, and which line of the lookup definition fires.

---

## Model 1 Code Cell: The Paper Machine, Executed

Run this cell to confirm your paper-machine answers from questions 1–4.

```python  liascript
try:
    class Environment:
        """A chain of scopes: each environment holds bindings and a parent link."""
        def __init__(self, parent=None):
            self.vars = {}
            self.parent = parent

        def define(self, name, value):
            """Create a NEW binding in THIS scope (a declaration: let)."""
            self.vars[name] = value

        def lookup(self, name):
            """Resolve a name by walking outward: static scope, executable."""
            env = self
            while env is not None:
                if name in env.vars:
                    return env.vars[name]
                env = env.parent
            raise NameError(f"undefined variable {name!r}")

        def assign(self, name, value):
            """Update an EXISTING binding wherever it lives (an assignment: x = ...)."""
            env = self
            while env is not None:
                if name in env.vars:
                    env.vars[name] = value
                    return
                env = env.parent
            raise NameError(f"cannot assign to undefined variable {name!r}")

    # The paper machine, executed:
    glob = Environment()
    glob.define("a", 1)
    glob.define("b", 2)

    block = Environment(parent=glob)      # entering the block: push a child
    block.define("b", 20)                 # shadows global b
    block.define("c", 30)
    print("P1:", block.lookup("a") + block.lookup("b") + block.lookup("c"))   # 51

    # leaving the block: we simply stop using `block`
    print("P2:", glob.lookup("b"))        # 2
    try:
        glob.lookup("c")
    except NameError as e:
        print("P2 c:", e)
except Exception as e:
    print(f"error: {e}")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

---

**Intuition for Model 2:** Now that you have seen the chain in action, it is time to read the class itself carefully. Think of `define`, `lookup`, and `assign` as three distinct post-office operations: `define` drops a letter into the current mailbox only; `lookup` asks each mailbox in the chain until the letter is found; and `assign` hunts through the chain to update the *existing* copy of the letter rather than creating a duplicate. Confusing `define` with `assign` is the single most common environment bug — this model is where you learn to tell them apart.

## Model 2: Read the Class

### Critical Thinking Questions

5. `define` writes only to `self.vars`; `assign` walks the chain. Construct a two-line program where confusing the two produces a wrong answer rather than an error, and state the rule: `let` means which method, bare `=` means which?
6. Verify your question 2 walk lengths by adding a counter to `lookup`. Does the executable machine agree with your paper machine?
7. "Leaving the block" is just ceasing to use the child environment. What reclaims its memory in Python, and why does the parent never need to know the child existed?

---

# Part II: The Four Operations in Practice (Day 1, continued)

**Intuition for Model 3:** Think of declaring a variable (`let x = 1`) versus updating one (`x = 99`) as two different actions at a hotel front desk. `define` is like checking *in* and being assigned a new room key — it always creates a fresh entry, even if another guest with the same name is already checked in on a higher floor. `assign` is like the manager walking every floor until they find the *existing* guest named `x` and handing them a new key — it never creates a new entry, it updates wherever `x` already lives. This model runs both operations side-by-side so you can see the difference concretely.

> **Watch out!** `define` and `assign` look almost identical when you call them, but they have opposite behavior when a parent scope already holds the name. Using `define` when you meant `assign` silently creates a *shadow copy* in the inner scope and leaves the outer binding unchanged — no error, just a subtly wrong answer. Always ask: am I *declaring* a new variable, or *updating* an existing one?

## Model 3: The Four Operations in Practice

The `Environment` class exposes exactly four operations. Understanding what each one does — and which scope it targets — is the entire implementation story for variable handling.

| Operation | Method | Scope targeted | Used for |
|-----------|--------|----------------|----------|
| **Define** | `define(name, val)` | current (innermost) only | `let x = ...` declarations |
| **Lookup** | `lookup(name)` | walks outward to root | reading any variable `x` |
| **Assign** | `assign(name, val)` | walks outward, updates first match | bare `x = ...` assignments |
| **Push** | `Environment(parent=e)` | creates a new innermost | entering a block `{ ... }` |

The **critical distinction**: `define` always writes to `self.vars` without checking ancestors, so calling it in a child silently creates a *new* shadowing binding rather than updating the outer one. `assign` walks before writing, so it updates the binding wherever it was first declared.

Run the cell below to see all four operations interact. **Before running**, predict: what will each `print` output?

```python  liascript
{% raw %}
try:
    class Environment:
        def __init__(self, parent=None):
            self.vars = {}
            self.parent = parent
        def define(self, name, value):
            self.vars[name] = value
        def lookup(self, name):
            env = self
            while env:
                if name in env.vars: return env.vars[name]
                env = env.parent
            raise NameError(f"undefined: {name!r}")
        def assign(self, name, value):
            env = self
            while env:
                if name in env.vars: env.vars[name] = value; return
                env = env.parent
            raise NameError(f"cannot assign undefined: {name!r}")
        def __repr__(self):
            items = ', '.join(f"{k}={v!r}" for k,v in self.vars.items())
            if self.parent: return f"{{{items}}} -> {self.parent}"
            return f"{{{items}}}"

    # Demo: define vs assign difference
    outer = Environment()
    outer.define('x', 10)
    inner = Environment(parent=outer)
    inner.define('y', 20)

    # define creates a NEW binding in inner
    inner.define('x', 99)    # shadows outer x
    print(f"inner.lookup('x') = {inner.lookup('x')}")   # 99
    print(f"outer.lookup('x') = {outer.lookup('x')}")   # 10 -- unaffected!

    # assign modifies the EXISTING binding (walks to outer)
    outer2 = Environment()
    outer2.define('x', 10)
    inner2 = Environment(parent=outer2)
    inner2.assign('x', 99)   # modifies outer2's x
    print(f"inner2.lookup('x') = {inner2.lookup('x')}")   # 99
    print(f"outer2.lookup('x') = {outer2.lookup('x')}")   # 99 -- changed!

    print(f"\nEnvironment chain: {inner}")
except Exception as e:
    print(f"[error] {e}")
{% endraw %}
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

### Critical Thinking Questions (Model 3)

8. After `inner.define('x', 99)`, the chain contains *two* bindings for `x`. How many environments does `inner.lookup('x')` visit before returning? How many does `outer.lookup('x')` visit?
9. `inner2.assign('x', 99)` mutated `outer2`'s binding, while `inner.define('x', 99)` left `outer`'s binding unchanged. In one sentence, state the rule: what is the correct behavior for a bare `=` assignment in a statically scoped language, and why does `assign` — not `define` — implement it?
10. The `__repr__` method uses `->` to render the chain. If you add a third level — `deep = Environment(parent=inner)` — and define a new variable `z = 5` in it, predict what `print(deep)` will show before running. Then add those two lines to the cell and verify.

---

**Intuition for Model 3 Extended:** Imagine a delivery driver whose job is to update the package status for a customer. If the driver writes the new status on a *fresh sticky note* and puts it on top of the original record, the original record never changes — and when that sticky note is thrown away at the end of the route, the customer's status looks exactly as it did before the delivery happened. That is exactly what `define` does to a loop counter. This model shows the bug in slow motion so you can recognize it instantly in your own interpreter.

> **Watch out!** When your interpreter evaluates a loop, it must thread the *same* environment through the loop condition check as through the loop body — and the loop body must use `assign` (not `define`) to update any counter declared outside the loop. If you forget this, your loop's exit condition will never become true, and you will have an infinite loop with no error message to explain why.

## Model 3 Extended: Define-when-you-meant-Assign

The most common environment bug is subtle: a student forgets that loop-counter assignments need `assign`, not `define`. The code runs, but the outer counter never changes, producing an infinite loop (or silent wrong answers).

```python  liascript
try:
    class Environment:
        def __init__(self, parent=None):
            self.vars = {}
            self.parent = parent
        def define(self, name, value):
            self.vars[name] = value
        def lookup(self, name):
            env = self
            while env:
                if name in env.vars: return env.vars[name]
                env = env.parent
            raise NameError(f"undefined: {name!r}")
        def assign(self, name, value):
            env = self
            while env:
                if name in env.vars: env.vars[name] = value; return
                env = env.parent
            raise NameError(f"cannot assign undefined: {name!r}")

    # Correct version: assign walks up and modifies outer counter
    print("=== Correct: assign ===")
    glob = Environment()
    glob.define('counter', 3)
    for _ in range(3):
        body_env = Environment(parent=glob)
        body_env.assign('counter', glob.lookup('counter') - 1)
    print(f"  counter after loop = {glob.lookup('counter')}")   # 0

    # Buggy version: define creates a fresh inner binding each iteration
    print("\n=== Buggy: define instead of assign ===")
    glob2 = Environment()
    glob2.define('counter', 3)
    safety = 0
    # Simulate 3 iterations but outer counter never changes
    for _ in range(3):
        body_env2 = Environment(parent=glob2)
        body_env2.define('counter', glob2.lookup('counter') - 1)
        inner_val = body_env2.lookup('counter')
        outer_val = glob2.lookup('counter')
        safety += 1
        print(f"  iter {safety}: inner counter={inner_val}, outer counter={outer_val}")
    print(f"  outer counter at end = {glob2.lookup('counter')}")  # still 3!
except Exception as e:
    print(f"[error] {e}")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

### Critical Thinking Questions (Model 3 Extended)

11. In the buggy version, the outer `counter` never decreases. Explain step by step why `body_env2.define('counter', ...)` fails to update `glob2`'s binding, even though `glob2` is the parent environment.
12. In your mini-language, `let x = ...` should map to `define` and bare `x = ...` should map to `assign`. Suppose a student writes `let x = 1` inside a `while` loop (intending to update `x` each iteration). What actually happens, and what error would you report?
13. What would happen if `assign` could not find the variable anywhere in the chain — for example, the programmer wrote `x = 5` without ever declaring `let x = ...`? Should this be a `NameError` (strict) or should your interpreter auto-declare it in the global scope (permissive)? List one language that takes each approach.

---

# Part III: Blocks, Loops, and Per-Iteration Scope (Day 2)

## 2. Blocks Push, Statements Thread

The interpreter changes are small and precise: `execute(Block(stmts), env)` creates `child = Environment(parent=env)` and executes the statements against `child`; `Let` calls `define` on the *current* environment; `Assign` calls `assign`; `Var` evaluation calls `lookup`. Conditionals and loops then inherit a design decision: does an `if` body or `while` body get its own scope? (C says yes with braces; Python says no; your language must say something, in `SEMANTICS.md`.)

> **Watch out!** When you wire `Environment` into a recursive tree-walking interpreter, every recursive call to `execute` or `evaluate` must receive the *correct* environment as an argument — it cannot use a global variable. It is easy to accidentally pass the *outer* environment into a block body instead of the freshly created child, or to forget to pass the current environment into an expression evaluator at all. If variables suddenly resolve to wrong values inside blocks, the first thing to check is whether the right environment is being threaded through every recursive call.

**Intuition for Model 4:** Consider a assembly line where each worker station has its own clipboard. At the start of each item, the station gets a fresh clipboard for that item's local notes — but to update the shared count on the factory-floor whiteboard, the worker must walk over to the whiteboard and change it there (not on the local clipboard). When the item moves on, the clipboard is recycled and all local notes are gone. This is exactly how per-iteration scope works: each iteration owns a child environment for its local variables, while shared state like loop counters lives in the parent and must be updated with `assign`.

## Model 4: Blocks, Loops, and Per-Iteration Scope

When a language gives every loop body its own fresh scope, a variable declared inside one iteration is invisible to the next and is gone after the loop. The cell below simulates a `while` loop where each iteration pushes a child environment:

```python  liascript
try:
    class Environment:
        def __init__(self, parent=None):
            self.vars = {}
            self.parent = parent

        def define(self, name, value):
            self.vars[name] = value

        def lookup(self, name):
            env = self
            while env is not None:
                if name in env.vars:
                    return env.vars[name]
                env = env.parent
            raise NameError(f"undefined variable {name!r}")

        def assign(self, name, value):
            env = self
            while env is not None:
                if name in env.vars:
                    env.vars[name] = value
                    return
                env = env.parent
            raise NameError(f"cannot assign to undefined variable {name!r}")

    # --- simulate: while (n > 0) { let t = n * 2; print t; n = n - 1; }
    glob = Environment()
    glob.define("n", 4)

    iteration = 0
    while glob.lookup("n") > 0:
        iteration += 1
        # Each iteration gets its own scope:
        loop_env = Environment(parent=glob)
        loop_env.define("t", glob.lookup("n") * 2)   # let t = n * 2
        print(f"  iteration {iteration}: t = {loop_env.lookup('t')}, "
              f"n visible = {loop_env.lookup('n')}")
        # n is in glob, so assign walks up and mutates glob:
        loop_env.assign("n", glob.lookup("n") - 1)
        # loop_env goes out of scope here; t disappears

    print("After loop: n =", glob.lookup("n"))

    # Confirm t is gone at the global level:
    try:
        glob.lookup("t")
    except NameError as e:
        print("After loop: t is gone --", e)

    # What if the loop body uses define for n instead of assign?
    print("\n--- Using define for n (wrong: creates a new inner n each time) ---")
    glob2 = Environment()
    glob2.define("n", 3)
    max_iters = 10   # safety guard
    iters = 0
    while glob2.lookup("n") > 0 and iters < max_iters:
        iters += 1
        loop_env2 = Environment(parent=glob2)
        # BUG: define shadows instead of updating outer n
        loop_env2.define("n", glob2.lookup("n") - 1)
        print(f"  iter {iters}: inner n = {loop_env2.lookup('n')}, "
              f"outer n = {glob2.lookup('n')}")
    if iters == max_iters:
        print("  (stopped after safety limit: outer n never decreased!)")
except Exception as e:
    print(f"[error] {e}")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

### Critical Thinking Questions (Model 4)

14. In the first loop, `t` is defined anew each iteration and disappears at the end of each iteration. Is `t`'s *scope* per-iteration, or is its *lifetime* per-iteration, or both? Define your terms before answering.
15. The second loop (with the "BUG") hits the safety limit. Explain precisely why: what does `loop_env2.define("n", ...)` do that prevents `glob2`'s `n` from ever decreasing?
16. In C, a `for` loop's init clause (`int i = 0`) creates a variable that is in scope for the entire loop but gone after. Where in the environment chain would you model that binding in your interpreter? Would it live in the same environment as the loop body, or a separate one?
17. Python does **not** give loop bodies their own scope: a variable declared inside a `for` loop is visible after the loop ends. Design an experiment (two small programs in your own language) that would tell a user whether your language follows Python's rule or C's rule. State which rule your team chose and document it in `SEMANTICS.md`.

---

**Intuition for Model 5:** When you call a function in a statically scoped language, the function's environment chain is determined by *where it was defined in the source code*, not by *who called it*. This is the chain-of-phone-books idea at full depth: a three-level nest creates three phone books stacked in order of textual enclosure, and lookup always searches from the innermost book outward. This model puts a tracer into `lookup` so you can watch every hop and verify that the counts match your mental model.

> **Watch out!** A very common conceptual error is to confuse **lexical (static) scoping** with **dynamic scoping**. In lexical scoping, the environment chain follows the *source code structure* — the nesting of blocks and functions in the file. In dynamic scoping, the chain follows the *call stack* at runtime — what called what. The `Environment` class you are building implements lexical scoping: the parent pointer is set when the child environment is *created* (at block entry), not when a function is *called*. If you accidentally set parent pointers based on the call stack rather than the textual structure, your language will exhibit dynamic scoping behavior, which is almost certainly not what you want.

**Step-by-step worked example for Model 5:** Before running the cell, trace through what happens at line INNER manually. Here is the environment state at the moment the four lookups execute:

| Environment | Variables stored | Parent |
|---|---|---|
| `global` | `x = 1`, `y = 2` | none (root) |
| `mid-block` | `y = 20`, `z = 30` | `global` |
| `inner-block` | `z = 300`, `w = 400` | `mid-block` |

Now trace each lookup step from `inner-block` outward:

- **`lookup("x")`**: check `inner-block` — not there; check `mid-block` — not there; check `global` — found `x = 1`. **3 hops.**
- **`lookup("y")`**: check `inner-block` — not there; check `mid-block` — found `y = 20`. **2 hops.** (Note: `global` has `y = 2`, but we stop at the first match.)
- **`lookup("z")`**: check `inner-block` — found `z = 300`. **1 hop.** (Note: `mid-block` has `z = 30`, but it is shadowed.)
- **`lookup("w")`**: check `inner-block` — found `w = 400`. **1 hop.**

Total hops at INNER: **3 + 2 + 1 + 1 = 7**. The result is `1 + 20 + 300 + 400 = 721`. Verify this against the trace output when you run the cell.

## Model 5: A Three-Level Environment Chain Trace

This cell demonstrates a three-level program and prints a full trace of every lookup, showing which environment satisfied each one.

```python  liascript
try:
    class Environment:
        def __init__(self, name="?", parent=None):
            self.vars = {}
            self.parent = parent
            self.name = name   # label for tracing

        def define(self, name, value):
            self.vars[name] = value

        def lookup(self, name, trace=False):
            env = self
            depth = 0
            while env is not None:
                if name in env.vars:
                    if trace:
                        print(f"    lookup({name!r}): found in [{env.name}] "
                              f"after {depth+1} hop(s) -> {env.vars[name]}")
                    return env.vars[name]
                if trace:
                    print(f"    lookup({name!r}): not in [{env.name}], "
                          f"trying parent...")
                env = env.parent
                depth += 1
            raise NameError(f"undefined variable {name!r}")

        def assign(self, name, value):
            env = self
            while env is not None:
                if name in env.vars:
                    env.vars[name] = value
                    return
                env = env.parent
            raise NameError(f"cannot assign to undefined variable {name!r}")

    # Three-level program:
    #   let x = 1; let y = 2;
    #   {
    #       let y = 20; let z = 30;
    #       {
    #           let z = 300; let w = 400;
    #           print x + y + z + w;   <-- line INNER
    #       }
    #       print x + y + z;           <-- line MID
    #   }
    #   print x + y;                   <-- line OUTER

    glob = Environment(name="global")
    glob.define("x", 1)
    glob.define("y", 2)

    mid = Environment(name="mid-block", parent=glob)
    mid.define("y", 20)
    mid.define("z", 30)

    inner = Environment(name="inner-block", parent=mid)
    inner.define("z", 300)
    inner.define("w", 400)

    print("=== Trace at INNER ===")
    result_inner = (inner.lookup("x", trace=True) +
                    inner.lookup("y", trace=True) +
                    inner.lookup("z", trace=True) +
                    inner.lookup("w", trace=True))
    print(f"  INNER result: {result_inner}")   # 1+20+300+400 = 721

    print("\n=== Trace at MID ===")
    result_mid = (mid.lookup("x", trace=True) +
                  mid.lookup("y", trace=True) +
                  mid.lookup("z", trace=True))
    print(f"  MID result: {result_mid}")       # 1+20+30 = 51

    print("\n=== Trace at OUTER ===")
    result_outer = (glob.lookup("x", trace=True) +
                    glob.lookup("y", trace=True))
    print(f"  OUTER result: {result_outer}")   # 1+2 = 3

    # Confirm w is not visible at MID or OUTER:
    print("\n=== Checking visibility of w at MID ===")
    try:
        mid.lookup("w", trace=True)
    except NameError as e:
        print("  As expected:", e)
except Exception as e:
    print(f"[error] {e}")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

### Critical Thinking Questions (Model 5)

18. At line INNER, how many total environment hops do all four lookups together require? Count from the trace output. Could you reduce this count without changing semantics? (Hint: think about which variable is looked up most often in a real program.)
19. The trace shows that `y` resolves to 20 at INNER (found in `mid-block`) rather than 2 (in `global`). This is shadowing. Now suppose your language also has a keyword `outer` that explicitly requests the *enclosing* scope's binding (skipping the innermost match). How would you modify `lookup` to support `outer.y` vs. `y`?
20. At line OUTER, `w` and `z` are gone. Is this a scope end, a lifetime end, or both? Can you construct a scenario in a language with closures where the *lifetime* of a binding outlives its lexical *scope*? (You do not need to implement this — describe it.)

---

## Multiple Choice Questions

[[MC]]
A `while` loop's body declares `let t = ...` each iteration, and the team gives each iteration a fresh child environment. After the loop, `t` is undefined. This behavior is the direct consequence of:
- ( ) The lexer discarding the variable
- ( ) Dynamic scoping
- (x) The binding's lifetime ending with the environment that held it, when the block scope is discarded
- ( ) Python's garbage collector running mid-loop

[[MC]]
A student writes `inner.define("x", 99)` when they meant to update the outer scope's `x`. The symptom they observe is:
- ( ) A `NameError` because `x` was not yet defined anywhere
- ( ) The outer `x` is updated to 99, as expected
- (x) A new inner `x` shadows the outer one, so the outer `x` is unchanged and the bug is silent
- ( ) The program crashes with a `KeyError`

---

# Part III.5: Variable Storage — A Step-by-Step Trace

## Model 6: Dictionary-Based Environment — Walking Through Every Operation

Before wiring the `Environment` class into your interpreter, it helps to trace every environment operation on a concrete program. This model runs a small program step by step, printing the state of every dictionary at each moment. The goal: after this trace, you should be able to predict the environment chain's exact contents at any point in any program — without running it.

**The program we will trace:**

```
let total = 0;
let n = 5;
{
    let i = 1;
    total = total + i;       # prints: total=1 after first iteration
}
print total;
```

The environment at each key moment:

```
After "let total = 0":    global: {total: 0}
After "let n = 5":        global: {total: 0, n: 5}
Enter inner block:         global: {total: 0, n: 5}  ← inner: {}
After "let i = 1":        global: {total: 0, n: 5}  ← inner: {i: 1}
After "total = total + i": global: {total: 1, n: 5}  ← inner: {i: 1}
Exit inner block:          global: {total: 1, n: 5}  (inner discarded)
```

```python
class Environment:
    """A chain of dictionaries implementing lexical scope."""

    def __init__(self, parent=None, name="?"):
        self.vars   = {}
        self.parent = parent
        self.name   = name    # for display only

    def define(self, name, value):
        """Create a new binding in the CURRENT scope."""
        self.vars[name] = value

    def lookup(self, name):
        """Walk the chain outward to find a binding."""
        if name in self.vars:
            return self.vars[name]
        if self.parent is not None:
            return self.parent.lookup(name)
        raise NameError(f"undefined variable '{name}'")

    def assign(self, name, value):
        """Update an EXISTING binding, wherever in the chain it lives."""
        if name in self.vars:
            self.vars[name] = value
            return
        if self.parent is not None:
            self.parent.assign(name, value)
            return
        raise NameError(f"cannot assign to undefined variable '{name}'")

    def __repr__(self):
        parts = [f"{self.name}:{self.vars}"]
        if self.parent:
            parts.append(repr(self.parent))
        return " ← ".join(parts)

def trace_program():
    print("=== Step-by-step environment trace ===\n")

    # Step 1: create global environment
    glob = Environment(name="global")
    print(f"Start:                  {glob}\n")

    # Step 2: let total = 0
    glob.define("total", 0)
    print(f"After 'let total = 0':  {glob}\n")

    # Step 3: let n = 5
    glob.define("n", 5)
    print(f"After 'let n = 5':      {glob}\n")

    # Step 4: enter inner block
    inner = Environment(parent=glob, name="inner")
    print(f"Enter block:            {inner}\n")

    # Step 5: let i = 1
    inner.define("i", 1)
    print(f"After 'let i = 1':      {inner}\n")

    # Step 6: total = total + i  (lookup total and i, assign to total)
    new_total = glob.lookup("total") + inner.lookup("i")
    glob.assign("total", new_total)
    print(f"After 'total = total+i': {inner}\n")

    # Step 7: exit inner block (discard inner)
    print(f"Exit block:             {glob}\n")

    # Step 8: print total
    result = glob.lookup("total")
    print(f"print total → {result}\n")

    # Step 9: demonstrate NameError after block exits
    try:
        glob.lookup("i")
    except NameError as e:
        print(f"lookup 'i' after block: {e}  (correct: 'i' is gone)\n")

trace_program()

# Demonstrate shadowing
print("=== Shadowing demonstration ===\n")
outer = Environment(name="outer")
outer.define("x", 10)
inner2 = Environment(parent=outer, name="inner")
inner2.define("x", 99)   # shadows outer x
print(f"Inner lookup 'x': {inner2.lookup('x')}  (should be 99)")
print(f"Outer lookup 'x': {outer.lookup('x')}   (should be 10)")
inner2.assign("x", 42)   # assigns to inner x (not outer)
print(f"After inner assign x=42:")
print(f"  inner x: {inner2.vars['x']}  (should be 42)")
print(f"  outer x: {outer.vars['x']}   (should be 10 — unchanged)")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

### Critical Thinking Questions

**CTQ 6.1** In Step 6 of the trace (`total = total + i`), the lookup for `total` walks to the global environment, but the assign also updates the global. Walk through the `assign` method call by call to show exactly why `inner.assign("total", 1)` updates `glob.vars["total"]` rather than creating a new `inner.vars["total"]`.

**CTQ 6.2** The `__repr__` method prints the chain as `inner:{...} ← global:{...}`. After Step 6, what does the full chain print? Write it out before running the code and confirm.

**CTQ 6.3** Change `inner2.assign("x", 42)` to `inner2.define("x", 42)`. What would `inner2.lookup("x")` and `outer.lookup("x")` return? Explain the difference between `define` and `assign` in one sentence.

---

# Part IV: Wiring It into the Interpreter (Day 2)

## 3. Exercises

1. *Interpreter surgery.* Replace your interpreter's flat dict with `Environment`, wiring `Let`, `Assign`, `Var`, and `Block` as above. Re-run last module's summation program (it must still work), then run the paper-machine program and confirm 51 and 2.

2. *Nested shadowing torture.* Write a three-level program (global, block, inner block) where the same name is bound at all three levels, and a fourth name is read from each level. Hand-draw the environment chain at the innermost print, then confirm by execution.

3. *Error message upgrade.* The current `NameError` messages say only "undefined variable 'x'". Upgrade them to also list the names currently visible in the entire chain: for example, "undefined variable 'pritnValue'; did you mean one of: printValue, x, n, total?". Implement the upgrade in the `lookup` method (add a `suggestions()` helper that collects all visible names by walking the chain). Show a before-and-after transcript on a program with a plausible typo.

4. *Design decision: if/while scope.* Your team must answer: do `if` and `while` bodies create fresh child environments, or do they execute in the enclosing environment? Implement **both** behaviors as a flag (`body_creates_scope: bool`) in a small interpreter, and write one program whose output differs between the two choices. Document your team's decision in `SEMANTICS.md` with the evidence program as justification.

5. *Instrumented environment.* Add a `lookup_count` counter to `Environment` that accumulates across the whole chain and resets to zero at the start of each top-level `execute` call. Print it after running the three-level trace program from Model 5. Then redesign `lookup` to cache the result of the most recent successful lookup per name. Show a benchmark (use `time.perf_counter`) demonstrating the speedup on a tight loop that reads the same variable 10,000 times.

---

## Reflection Prompt

In your notebook: the environment chain makes "context" into an explicit, inspectable object: you can print the whole chain at any moment. Where in your own debugging (or your own thinking) would you benefit from being able to print the chain of contexts you are currently inside?

---

## 4. Further Reading

- Douglas Thain. *Introduction to Compilers and Language Design*, Chapter 7.
- Robert Nystrom. *Crafting Interpreters*, "Statements and State" and "Functions" (online): environments, then closures over them.
- Abelson and Sussman. *Structure and Interpretation of Computer Programs*, section 3.2, the environment model, beautifully drawn.
