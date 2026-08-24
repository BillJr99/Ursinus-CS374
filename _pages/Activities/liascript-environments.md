<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374-Fall2026/gh-pages/_pages/Activities/liascript-environments.md or locally via https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374-Fall2026/gh-pages/_pages/Activities/liascript-environments.md

import: https://raw.githubusercontent.com/liascript/CodeRunner/master/README.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

# Environments: Implementing Scope

Every running program needs a way to answer the question: "what value does the name `x` refer to right now?"  An **environment** is that answer: a data structure mapping names to values, much like a phone book.  But one phone book is not enough: entering a block or function needs a fresh page that can shadow outer entries, torn out and discarded on exit.  Nested environments form a **chain of phone books**, each consulted first, then deferring outward when a name is not found locally.  Building and manipulating this chain is the foundation of every scope rule your interpreter will enforce.

## Learning Goals

By the end of this activity, you will be able to:

- Implement an `Environment` class as a chain of dictionaries linked by parent pointers, and explain why a flat dictionary cannot model nested scope
- Trace the four environment operations (`define`, `lookup`, `assign`, and scope entry/exit) on a program with nested blocks
- Predict the value printed at each point in a program with shadowed variable names, explaining each step of the chain-walk lookup
- Construct the environment chain diagram for a given program snapshot and identify the lifetime and scope of each binding
- Integrate the `Environment` class into a tree-walking interpreter so that block statements correctly push and pop scopes

> **Before You Begin:** This activity assumes you can:
> - Explain the difference between *scope* (where a name is visible in source text) and *lifetime* (how long its storage exists at runtime)
> - Read and write basic Python dictionaries and classes (including `__init__`, instance variables, and simple `while` loops)
> - Describe static (lexical) scoping: a name resolves to the innermost enclosing declaration at the point where it appears in the source
>
> If any of these feel shaky, review them first.

The scope rules of *Binding and Scope* become today's data structure: the **environment**, a chain of dictionaries linked by parent pointers, in which lookup walks outward exactly as static scoping demands.  This session builds the `Environment` class your interpreter assignment requires.  The path today: **why one dict fails $\rightarrow$ the chain $\rightarrow$ the four operations $\rightarrow$ blocks creating and discarding scopes**.

---

## Directions and Group Roles

Work in your POGIL team with your rotated roles (**Manager**, **Recorder**, **Presenter**, **Reflector**).  Please think each model and question through on your own first, then talk it over with your group.  The Recorder posts your answers to the Class Activity Questions discussion board, and the Presenter reports out wherever you disagreed or found another approach.  After class, please respond to the reflective prompt on your own in your notebook.

---

# Part I: The Chain

## 1.  One Dictionary Cannot Shadow

Your interpreter's flat `env = {}` makes every variable global: a block that declares `x` overwrites any outer `x` forever, and nothing is discarded when the block ends.  The cure mirrors the textual nesting itself: **one dictionary per scope, each holding a pointer to its parent**.  Entering a block pushes a fresh child environment; leaving it returns to the parent, and the child's bindings vanish with it.

**Lookup walks the chain.**  To resolve `x`: check the current environment; if absent, ask the parent; continue to the global; fail (a name error) only past the root:

$$
\text{lookup}(x, E) = \begin{cases} E.\text{vars}[x] & x \in E.\text{vars} \\ \text{lookup}(x, E.\text{parent}) & \text{otherwise, if a parent exists} \\ \text{NameError} & \text{at the root} \end{cases}
$$

This walk *is* static scope: innermost first, then outward.

---

**Intuition for Model 1:** Think of a notepad with sticky notes: global clues live on the page, and each inner section gets a sticky note placed on top.  You check the sticky note first, then the page beneath; when the section ends, the note is peeled off and discarded, and anything it covered is visible again.  This model lets you trace exactly that process with a two-scope program.

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

1.  Draw the environment picture at line P1: two boxes (global and block), their contents, and the parent arrow.  The Recorder keeps the drawing.
2.  Resolve each of `a`, `b`, `c` at P1 by walking the chain; report each walk's length and the printed value.
3.  At P2, the block environment is gone.  What does `print b` produce, and what happened to the binding `c`?  Name the concept (scope, lifetime, or both?) that just ended for `c`.
4.  Predict what `print c` at P2 would do, and which line of the lookup definition fires.

---

## Model 1 Code Cell: The Paper Machine, Executed

Run this cell to confirm your paper-machine answers from questions 1-4.

This cell contains the canonical `Environment` class, the one complete build in this activity.  Every later cell repeats it silently at the top so that each cell runs on its own; read it here once, and from then on look only at the code below the class.

```python
class Environment:
    """A chain of scopes: each environment holds bindings and a parent link."""
    def __init__(self, parent=None, name="?"):
        self.vars = {}
        self.parent = parent
        self.name = name   # label used in drawings and traces

    def define(self, name, value):
        """Create a NEW binding in THIS scope (a declaration: let)."""
        self.vars[name] = value

    def lookup(self, name, trace=False):
        """Resolve a name by walking outward: static scope, executable."""
        env = self
        depth = 0
        while env is not None:
            if name in env.vars:
                if trace:
                    print(f"    lookup({name!r}): found in [{env.name}] "
                          f"after {depth+1} hop(s) -> {env.vars[name]}")
                return env.vars[name]
            if trace:
                print(f"    lookup({name!r}): not in [{env.name}], trying parent...")
            env = env.parent
            depth += 1
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

    def __repr__(self):
        parts = [f"{self.name}:{self.vars}"]
        if self.parent:
            parts.append(repr(self.parent))
        return " -> ".join(parts)

# The paper machine, executed:
glob = Environment(name="global")
glob.define("a", 1)
glob.define("b", 2)

block = Environment(parent=glob, name="block")   # entering the block: push a child
block.define("b", 20)                 # shadows global b
block.define("c", 30)
print("P1:", block.lookup("a") + block.lookup("b") + block.lookup("c"))   # 51

# leaving the block: we simply stop using `block`
print("P2:", glob.lookup("b"))        # 2
try:
    glob.lookup("c")
except NameError as e:
    print("P2 c:", e)
```
@LIA.eval(`["main.py"]`, `none`, `python3 main.py`)

### Reading the Code

- `vars` and `parent` are the entire data structure.  Everything else on the class is a *walk* over that chain; there is no other state anywhere.
- `define` writes to `self.vars` and never looks at `parent`.  `assign` never writes to `self.vars` unless the name is already there.  That one asymmetry is the entire difference between declaring and updating, and it is where most interpreter bugs live.
- `lookup` walks outward and stops at the *first* frame that has the name.  Shadowing is not a special case in the code; it falls out of stopping early.
- Leaving a block is not an operation.  There is no `pop`: the code simply stops using `block`, and Python's garbage collector does the rest.  Scope ending is the absence of a reference, not an instruction.
- `__repr__` renders the chain outward with `->`, which is why the printed trace reads exactly like the boxes you drew on paper.

### Try It Yourself

Break the chain on purpose, and watch which operation notices.

```python
class Environment:
    def __init__(self, parent=None, name="?"):
        self.vars = {}
        self.parent = parent
        self.name = name
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
    def __repr__(self):
        parts = [f"{self.name}:{self.vars}"]
        if self.parent:
            parts.append(repr(self.parent))
        return " -> ".join(parts)

glob  = Environment(name="global")
glob.define("total", 0)
inner = Environment(parent=glob, name="inner")

print("=== Start ===")
print(f"  {inner}")

# TODO 1: call inner.assign("total", 5) and print the chain. WHICH frame
#         changed? Predict before you run.

# TODO 2: now call inner.define("total", 99) and print the chain again.
#         There are now two bindings named "total". Which one does
#         inner.lookup("total") find, and which does glob.lookup("total")
#         find? Print both.

# TODO 3: break it. Set inner.parent = None, then try inner.lookup("total")
#         and glob.lookup("total"). Which one still works, and why does
#         that tell you where the chain actually lives?

print("\n=== After your edits ===")
print(f"  inner: {inner}")
print(f"  glob : {glob}")
```
@LIA.eval(`["main.py"]`, `none`, `python3 main.py`)

Expected output before you edit anything: one line showing `inner:{} -> global:{'total': 0}`, twice.  Each TODO changes exactly one thing, so run after each one rather than all at the end.

---

**Intuition for Model 2:** Read the class as three post-office operations: `define` drops a letter into the current mailbox only; `lookup` asks each mailbox up the chain; `assign` updates the *existing* copy wherever it lives rather than creating a duplicate.  Confusing `define` with `assign` is the single most common environment bug.

## Model 2: Read the Class

### Critical Thinking Questions

5. `define` writes only to `self.vars`; `assign` walks the chain.  Construct a two-line program where confusing the two produces a wrong answer rather than an error, and state the rule: `let` means which method, bare `=` means which?
6.  Verify your question 2 walk lengths using the built-in tracer: call `lookup(..., trace=True)`.  Does the executable machine agree with your paper machine?
7.  "Leaving the block" is just ceasing to use the child environment.  What reclaims its memory in Python, and why does the parent never need to know the child existed?

---

# Part II: The Four Operations in Practice

**Intuition for Model 3:** At a hotel front desk, `define` is checking *in*: always a fresh entry, even if a same-named guest is registered on a higher floor. `assign` is the manager walking every floor to hand the *existing* guest a new key, never a new entry.  This model runs both operations side-by-side so you can see the difference concretely.

> **Watch out!**  Using `define` when you meant `assign` silently creates a *shadow copy* in the inner scope and leaves the outer binding unchanged, no error, just a subtly wrong answer.  Always ask: am I *declaring* a new variable, or *updating* an existing one?

## Model 3: The Four Operations in Practice

The `Environment` class exposes exactly four operations; which scope each one targets is the entire implementation story for variable handling.

| Operation | Method | Scope targeted | Used for |
|-----------|--------|----------------|----------|
| **Define** | `define(name, val)` | current (innermost) only | `let x = ...` declarations |
| **Lookup** | `lookup(name)` | walks outward to root | reading any variable `x` |
| **Assign** | `assign(name, val)` | walks outward, updates first match | bare `x = ...` assignments |
| **Push** | `Environment(parent=e)` | creates a new innermost | entering a block `{ ... }` |

The **critical distinction**: `define` writes to `self.vars` without checking ancestors (a child silently creates a *new* shadowing binding); `assign` walks before writing, updating the binding where it was first declared.

Run the cell below to see all four operations interact, no new methods needed.  **Before running**, predict: what will each `print` output?

```python
# --- The canonical Environment class from Model 1 (repeated so this cell
# --- runs on its own; each cell in this deck is self-contained).
class Environment:
    """A chain of scopes: each environment holds bindings and a parent link."""
    def __init__(self, parent=None, name="?"):
        self.vars = {}
        self.parent = parent
        self.name = name   # label used in drawings and traces

    def define(self, name, value):
        """Create a NEW binding in THIS scope (a declaration: let)."""
        self.vars[name] = value

    def lookup(self, name, trace=False):
        """Resolve a name by walking outward: static scope, executable."""
        env = self
        depth = 0
        while env is not None:
            if name in env.vars:
                if trace:
                    print(f"    lookup({name!r}): found in [{env.name}] "
                          f"after {depth+1} hop(s) -> {env.vars[name]}")
                return env.vars[name]
            if trace:
                print(f"    lookup({name!r}): not in [{env.name}], trying parent...")
            env = env.parent
            depth += 1
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

    def __repr__(self):
        parts = [f"{self.name}:{self.vars}"]
        if self.parent:
            parts.append(repr(self.parent))
        return " -> ".join(parts)

# Demo: define vs assign difference
outer = Environment(name="outer")
outer.define('x', 10)
inner = Environment(parent=outer, name="inner")
inner.define('y', 20)

# define creates a NEW binding in inner
inner.define('x', 99)    # shadows outer x
print(f"inner.lookup('x') = {inner.lookup('x')}")   # 99
print(f"outer.lookup('x') = {outer.lookup('x')}")   # 10 -- unaffected!

# assign modifies the EXISTING binding (walks to outer)
outer2 = Environment(name="outer2")
outer2.define('x', 10)
inner2 = Environment(parent=outer2, name="inner2")
inner2.assign('x', 99)   # modifies outer2's x
print(f"inner2.lookup('x') = {inner2.lookup('x')}")   # 99
print(f"outer2.lookup('x') = {outer2.lookup('x')}")   # 99 -- changed!

print(f"\nEnvironment chain: {inner}")
```
@LIA.eval(`["main.py"]`, `none`, `python3 main.py`)

### Reading the Code

- The demo runs the same two-line program twice, once with `define` and once with `assign`, and the only difference in the output is *which frame* holds the changed value.  Part II comes down to that one contrast.
- Watch `inner` after the `define` run: it has its own `x`.  After the `assign` run it is empty, and `outer`'s `x` moved instead.  Two bindings versus one.
- Neither operation ever copies a frame.  `assign` reaches through the chain and mutates in place, which is why a change made deep inside a block is still visible after the block ends.

### Critical Thinking Questions (Model 3)

8.  After `inner.define('x', 99)`, the chain contains *two* bindings for `x`.  How many environments does `inner.lookup('x')` visit before returning?  How many does `outer.lookup('x')` visit?
9. `inner2.assign('x', 99)` mutated `outer2`'s binding, while `inner.define('x', 99)` left `outer`'s binding unchanged.  In one sentence, state the rule: what is the correct behavior for a bare `=` assignment in a statically scoped language, and why does `assign` (not `define`) implement it?
10.  The canonical class's `__repr__` method (Model 1) uses `->` to render the chain.  If you add a third level (`deep = Environment(parent=inner, name="deep")`) and define a new variable `z = 5` in it, predict what `print(deep)` will show before running.  Then add those two lines to the cell and verify.

---

**Intuition for Model 3 Extended:** Writing a package's new status on a *fresh sticky note* placed over the original record never changes the record, and when the note is discarded, the status looks untouched.  That is what `define` does to a loop counter.  This model shows the bug in slow motion.

## Model 3 Extended: Define-when-you-meant-Assign

The most common environment bug is subtle: a student forgets that loop-counter assignments need `assign`, not `define`.  The code runs, but the outer counter never changes, producing an infinite loop (or silent wrong answers).  No new methods here either; paste your canonical class and watch the bug unfold.  (With `assign` instead, the outer counter would correctly reach 0 after three iterations; Model 4 shows that working version inside a real loop.)

```python
# --- The canonical Environment class from Model 1 (repeated so this cell
# --- runs on its own; each cell in this deck is self-contained).
class Environment:
    """A chain of scopes: each environment holds bindings and a parent link."""
    def __init__(self, parent=None, name="?"):
        self.vars = {}
        self.parent = parent
        self.name = name   # label used in drawings and traces

    def define(self, name, value):
        """Create a NEW binding in THIS scope (a declaration: let)."""
        self.vars[name] = value

    def lookup(self, name, trace=False):
        """Resolve a name by walking outward: static scope, executable."""
        env = self
        depth = 0
        while env is not None:
            if name in env.vars:
                if trace:
                    print(f"    lookup({name!r}): found in [{env.name}] "
                          f"after {depth+1} hop(s) -> {env.vars[name]}")
                return env.vars[name]
            if trace:
                print(f"    lookup({name!r}): not in [{env.name}], trying parent...")
            env = env.parent
            depth += 1
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

    def __repr__(self):
        parts = [f"{self.name}:{self.vars}"]
        if self.parent:
            parts.append(repr(self.parent))
        return " -> ".join(parts)

# Buggy version: define creates a fresh inner binding each iteration
print("=== Buggy: define instead of assign ===")
glob2 = Environment()
glob2.define('counter', 3)
# Simulate 3 iterations but outer counter never changes
for i in range(1, 4):
    body_env2 = Environment(parent=glob2)
    body_env2.define('counter', glob2.lookup('counter') - 1)
    print(f"  iter {i}: inner counter={body_env2.lookup('counter')}, "
          f"outer counter={glob2.lookup('counter')}")
print(f"  outer counter at end = {glob2.lookup('counter')}")  # still 3!
```
@LIA.eval(`["main.py"]`, `none`, `python3 main.py`)

### Critical Thinking Questions (Model 3 Extended)

11.  In the buggy version, the outer `counter` never decreases.  Explain step by step why `body_env2.define('counter', ...)` fails to update `glob2`'s binding, even though `glob2` is the parent environment.
12.  In your mini-language, `let x = ...` should map to `define` and bare `x = ...` should map to `assign`.  Suppose a student writes `let x = 1` inside a `while` loop (intending to update `x` each iteration).  What actually happens, and what error would you report?
13.  What would happen if `assign` could not find the variable anywhere in the chain, for example, the programmer wrote `x = 5` without ever declaring `let x = ...`?  Should this be a `NameError` (strict) or should your interpreter auto-declare it in the global scope (permissive)?  List one language that takes each approach.

---

# Part III: Blocks, Loops, and Per-Iteration Scope

## 2.  Blocks Push, Statements Thread

The interpreter changes are small: `execute(Block(stmts), env)` creates `child = Environment(parent=env)` and executes the statements against `child`; `Let` calls `define` on the *current* environment; `Assign` calls `assign`; `Var` evaluation calls `lookup`.  Conditionals and loops then inherit a design decision: does an `if` or `while` body get its own scope?  (C says yes with braces; Python says no; your language must say something, in `SEMANTICS.md`.)

> **Watch out!**  Every recursive call to `execute` or `evaluate` must receive the *correct* environment as an argument, never a global variable.  It is easy to pass the *outer* environment into a block body instead of the freshly created child.  If variables suddenly resolve to wrong values inside blocks, first check that the right environment is threaded through every recursive call.

**Intuition for Model 4:** Each assembly-line item gets a fresh clipboard for local notes, but the shared count lives on the factory whiteboard and must be updated there.  That is per-iteration scope: locals live in the iteration's child environment; shared loop counters live in the parent, updated with `assign`.

## Model 4: Blocks, Loops, and Per-Iteration Scope

When a language gives every loop body its own fresh scope, a variable declared inside one iteration is invisible to the next and is gone after the loop.  The cell below simulates a `while` loop where each iteration pushes a child environment (again, nothing new to add to the class):

```python
# --- The canonical Environment class from Model 1 (repeated so this cell
# --- runs on its own; each cell in this deck is self-contained).
class Environment:
    """A chain of scopes: each environment holds bindings and a parent link."""
    def __init__(self, parent=None, name="?"):
        self.vars = {}
        self.parent = parent
        self.name = name   # label used in drawings and traces

    def define(self, name, value):
        """Create a NEW binding in THIS scope (a declaration: let)."""
        self.vars[name] = value

    def lookup(self, name, trace=False):
        """Resolve a name by walking outward: static scope, executable."""
        env = self
        depth = 0
        while env is not None:
            if name in env.vars:
                if trace:
                    print(f"    lookup({name!r}): found in [{env.name}] "
                          f"after {depth+1} hop(s) -> {env.vars[name]}")
                return env.vars[name]
            if trace:
                print(f"    lookup({name!r}): not in [{env.name}], trying parent...")
            env = env.parent
            depth += 1
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

    def __repr__(self):
        parts = [f"{self.name}:{self.vars}"]
        if self.parent:
            parts.append(repr(self.parent))
        return " -> ".join(parts)

# --- simulate: while (n > 0) { let t = n * 2; print t; n = n - 1; }
glob = Environment(name="global")
glob.define("n", 4)

iteration = 0
while glob.lookup("n") > 0:
    iteration += 1
    # Each iteration gets its own scope:
    loop_env = Environment(parent=glob, name="loop")
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
```
@LIA.eval(`["main.py"]`, `none`, `python3 main.py`)

Had the body used `define` for `n` instead of `assign`, you would recreate the Model 3 Extended bug: the outer `n` would never decrease and the loop would never terminate.

### Reading the Code

- `loop_env` is rebuilt inside the `while`, once per iteration.  Move that line above the loop and every iteration would share one frame, which is exactly the closure-capture decision from *Names, Binding, and Scope*, now visible in the interpreter rather than in Python.
- `n` is updated with `assign`, so it reaches out to `glob` and the loop can terminate.  `t` is created with `define`, so it stays in `loop_env` and vanishes each iteration.  Swap those two calls and you get an infinite loop, which is the single most common bug in this assignment.
- The final lookup of `t` raising `NameError` is the *proof* that per-iteration scope worked.  A test that only checks the printed values would pass even if `t` leaked.

### Try It Yourself

Decide the per-iteration question for your own language, and prove your answer with the environment rather than by asserting it.

```python
class Environment:
    def __init__(self, parent=None, name="?"):
        self.vars, self.parent, self.name = {}, parent, name
    def define(self, name, value):
        self.vars[name] = value
    def lookup(self, name):
        env = self
        while env is not None:
            if name in env.vars: return env.vars[name]
            env = env.parent
        raise NameError(f"undefined variable {name!r}")
    def assign(self, name, value):
        env = self
        while env is not None:
            if name in env.vars:
                env.vars[name] = value; return
            env = env.parent
        raise NameError(f"cannot assign to undefined variable {name!r}")
    def __repr__(self):
        parts = [f"{self.name}:{self.vars}"]
        if self.parent: parts.append(repr(self.parent))
        return " -> ".join(parts)

# Simulate:  for i in 0..2 { let captured = i; remember(captured); }
# The question: does each iteration get a FRESH frame, or share one?

def run(fresh_frame_per_iteration):
    glob = Environment(name="global")
    remembered = []
    shared = Environment(parent=glob, name="loop")     # used when NOT fresh
    for i in range(3):
        if fresh_frame_per_iteration:
            body = Environment(parent=glob, name=f"iter{i}")   # a new frame
        else:
            body = shared                                      # the same frame
        body.define("captured", i)
        remembered.append(body)                        # keep the frame alive
    return [f.lookup("captured") for f in remembered]

print("=== Fresh frame per iteration ===")
print(f"  remembered values: {run(True)}")
print("=== One shared frame ===")
print(f"  remembered values: {run(False)}")

# TODO 1: explain the second line. All three frames are the SAME object,
#         so all three report the last value written. Which Python bug
#         from the Binding and Scope session is this?

# TODO 2: your language has to pick. Write the one-sentence rule for
#         SEMANTICS.md, and name a language that made each choice.

# TODO 3: harder. Make the shared version behave like the fresh one WITHOUT
#         creating a new Environment per iteration. What do you have to
#         copy instead, and what does that tell you about what a closure
#         really captures?
```
@LIA.eval(`["main.py"]`, `none`, `python3 main.py`)

Expected output: `[0, 1, 2]` and then `[2, 2, 2]`.  If you have seen `[2, 2, 2]` before, that is the point: it is the same bug, one level down.

### Critical Thinking Questions (Model 4)

14.  In the first loop, `t` is defined anew each iteration and disappears at the end of each iteration.  Is `t`'s *scope* per-iteration, or is its *lifetime* per-iteration, or both?  Define your terms before answering.
15.  Suppose the loop body called `loop_env.define("n", ...)` instead of `assign`, the bug from Model 3 Extended.  Explain precisely why the loop would never terminate: what does `define` do that prevents `glob`'s `n` from ever decreasing?
16.  In C, a `for` loop's init clause (`int i = 0`) creates a variable that is in scope for the entire loop but gone after.  Where in the environment chain would you model that binding in your interpreter?  Would it live in the same environment as the loop body, or a separate one?
17.  Python does **not** give loop bodies their own scope: a variable declared inside a `for` loop is visible after the loop ends.  Design an experiment (two small programs in your own language) that would tell a user whether your language follows Python's rule or C's rule.  State which rule your team chose and document it in `SEMANTICS.md`.

---

**Intuition for Model 5:** In a statically scoped language the chain is determined by *where code was defined*, not *who called it*: a three-level nest stacks three phone books in textual-enclosure order, searched innermost-out.  The tracer in `lookup` lets you watch every hop and check the counts against your mental model.

> **Watch out!**  In **lexical (static) scoping** the environment chain follows the *source code structure*; in **dynamic scoping** it follows the runtime *call stack*.  Your class is lexical because the parent pointer is set when the child environment is *created* (at block entry), not when a function is *called*.  Set parents from the call stack instead, and your language silently becomes dynamically scoped, almost certainly not what you want.

**Before running the cell**, trace line INNER by hand: `lookup("x")` misses twice and finds `x = 1` in `global` (**3 hops**); `lookup("y")` finds the shadowing `y = 20` in `mid-block` (**2 hops**; the first match beats `global`'s `y = 2`); `lookup("z")` and `lookup("w")` hit immediately in `inner-block` (**1 hop** each).  Total hops: **3 + 2 + 1 + 1 = 7**; the result is `1 + 20 + 300 + 400 = 721`.  Verify against the trace output.

## Model 5: A Three-Level Environment Chain Trace

No new code is needed: your canonical `lookup` already carries the tracer (`trace=True`), and this model is where it earns its keep.  The cell below builds a three-level program and prints a full trace of every lookup at line INNER, showing which environment satisfied each one.  Extend it to trace lines MID and OUTER.

```python
# --- The canonical Environment class from Model 1 (repeated so this cell
# --- runs on its own; each cell in this deck is self-contained).
class Environment:
    """A chain of scopes: each environment holds bindings and a parent link."""
    def __init__(self, parent=None, name="?"):
        self.vars = {}
        self.parent = parent
        self.name = name   # label used in drawings and traces

    def define(self, name, value):
        """Create a NEW binding in THIS scope (a declaration: let)."""
        self.vars[name] = value

    def lookup(self, name, trace=False):
        """Resolve a name by walking outward: static scope, executable."""
        env = self
        depth = 0
        while env is not None:
            if name in env.vars:
                if trace:
                    print(f"    lookup({name!r}): found in [{env.name}] "
                          f"after {depth+1} hop(s) -> {env.vars[name]}")
                return env.vars[name]
            if trace:
                print(f"    lookup({name!r}): not in [{env.name}], trying parent...")
            env = env.parent
            depth += 1
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

    def __repr__(self):
        parts = [f"{self.name}:{self.vars}"]
        if self.parent:
            parts.append(repr(self.parent))
        return " -> ".join(parts)

# Three-level program:
#   let x = 1; let y = 2;
#   { let y = 20; let z = 30;
#     { let z = 300; let w = 400;
#       print x + y + z + w; }    <-- line INNER
#     print x + y + z; }          <-- line MID
#   print x + y;                  <-- line OUTER

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

# Confirm w is not visible at MID (or OUTER):
print("\n=== Checking visibility of w at MID ===")
try:
    mid.lookup("w", trace=True)
except NameError as e:
    print("  As expected:", e)
```
@LIA.eval(`["main.py"]`, `none`, `python3 main.py`)

### Reading the Code

- Three frames, three `define` calls at different depths, and every printed lookup reports the *hop count* that found it.  Read the hop counts as the cost of a name: a variable two blocks out costs two pointer follows on every use.
- `x` is found at the global frame from all three depths, and `z` resolves to a different value depending on where you stand.  Same name, same program, three answers, all correct.
- The `w` lookup from MID raising `NameError` is the containment check: inner names are invisible from outside, which is the property that makes blocks safe to nest.

### Critical Thinking Questions (Model 5)

18.  At line INNER, how many total environment hops do all four lookups together require?  Count from the trace output.  Could you reduce this count without changing semantics?  (Hint: think about which variable is looked up most often in a real program.)
19.  The trace shows that `y` resolves to 20 at INNER (found in `mid-block`) rather than 2 (in `global`).  This is shadowing.  Now suppose your language also has a keyword `outer` that explicitly requests the *enclosing* scope's binding (skipping the innermost match).  How would you modify `lookup` to support `outer.y` vs. `y`?
20.  At line OUTER, `w` and `z` are gone.  Is this a scope end, a lifetime end, or both?  Can you construct a scenario in a language with closures where the *lifetime* of a binding outlives its lexical *scope*?  (You do not need to implement this; describe it.)

---

## Multiple Choice Questions

A `while` loop's body declares `let t = ...` each iteration, and the team gives each iteration a fresh child environment.  After the loop, `t` is undefined.  This behavior is the direct consequence of:

[( )] The lexer discarding the variable
[( )] Dynamic scoping
[(X)] The binding's lifetime ending with the environment that held it, when the block scope is discarded
[( )] Python's garbage collector running mid-loop

A student writes `inner.define("x", 99)` when they meant to update the outer scope's `x`.  The symptom they observe is:

[( )] A `NameError` because `x` was not yet defined anywhere
[( )] The outer `x` is updated to 99, as expected
[(X)] A new inner `x` shadows the outer one, so the outer `x` is unchanged and the bug is silent
[( )] The program crashes with a `KeyError`

---

# Part IV: Variable Storage, A Step-by-Step Trace

## Model 6 (At Home): Dictionary-Based Environment, Walking Through Every Operation

Before wiring the `Environment` class into your interpreter, trace every environment operation on a concrete program: this model runs one step by step, printing the state of every dictionary at each moment.  The goal: to predict the chain's exact contents at any point in any program, without running it.

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

Before running the trace, predict the environment chain's contents after each of these moments: both `let` statements, block entry, `let i = 1`, the assignment `total = total + i`, and block exit.

The class itself contains nothing new; this model is pure rehearsal.  Run the trace and check each printed state against your prediction.

```python
# --- The canonical Environment class from Model 1 (repeated so this cell
# --- runs on its own; each cell in this deck is self-contained).
class Environment:
    """A chain of scopes: each environment holds bindings and a parent link."""
    def __init__(self, parent=None, name="?"):
        self.vars = {}
        self.parent = parent
        self.name = name   # label used in drawings and traces

    def define(self, name, value):
        """Create a NEW binding in THIS scope (a declaration: let)."""
        self.vars[name] = value

    def lookup(self, name, trace=False):
        """Resolve a name by walking outward: static scope, executable."""
        env = self
        depth = 0
        while env is not None:
            if name in env.vars:
                if trace:
                    print(f"    lookup({name!r}): found in [{env.name}] "
                          f"after {depth+1} hop(s) -> {env.vars[name]}")
                return env.vars[name]
            if trace:
                print(f"    lookup({name!r}): not in [{env.name}], trying parent...")
            env = env.parent
            depth += 1
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

    def __repr__(self):
        parts = [f"{self.name}:{self.vars}"]
        if self.parent:
            parts.append(repr(self.parent))
        return " -> ".join(parts)

def trace_program():
    print("=== Step-by-step environment trace ===\n")

    glob = Environment(name="global")     # Step 1: create global environment
    print(f"Start:                  {glob}\n")

    glob.define("total", 0)               # Step 2: let total = 0
    print(f"After 'let total = 0':  {glob}\n")

    glob.define("n", 5)                   # Step 3: let n = 5
    print(f"After 'let n = 5':      {glob}\n")

    inner = Environment(parent=glob, name="inner")   # Step 4: enter inner block
    print(f"Enter block:            {inner}\n")

    inner.define("i", 1)                  # Step 5: let i = 1
    print(f"After 'let i = 1':      {inner}\n")

    # Step 6: total = total + i  (lookup total and i, assign to total)
    inner.assign("total", inner.lookup("total") + inner.lookup("i"))
    print(f"After 'total = total+i': {inner}\n")

    # Step 7: exit inner block (discard inner)
    print(f"Exit block:             {glob}\n")

    # Step 8: print total
    print(f"print total -> {glob.lookup('total')}\n")

    # Step 9: demonstrate NameError after block exits
    try:
        glob.lookup("i")
    except NameError as e:
        print(f"lookup 'i' after block: {e}  (correct: 'i' is gone)\n")

trace_program()
```
@LIA.eval(`["main.py"]`, `none`, `python3 main.py`)

### Critical Thinking Questions

**CTQ 6.1** In Step 6 of the trace (`total = total + i`), the lookup for `total` walks to the global environment, but the assign also updates the global.  Walk through the `assign` method step by step to show exactly why `inner.assign("total", 1)` updates `glob.vars["total"]` rather than creating a new `inner.vars["total"]`.

**CTQ 6.2** The `__repr__` method prints the chain as `inner:{...} -> global:{...}`.  After Step 6, what does the full chain print?  Write it out before running the code and confirm.

**CTQ 6.3** Extend the cell with a shadowing experiment: `outer` holds `x = 10`, child `inner2` holds its own `x = 99`. `inner2.assign("x", 42)` updates the *inner* binding (the first match on the walk).  With `inner2.define("x", 42)` instead, what would `inner2.lookup("x")` and `outer.lookup("x")` return?  State the `define`/`assign` difference in one sentence.

---

# Part V: Wiring It into the Interpreter

## 3.  Exercises

1.  *Interpreter surgery.*  Replace your interpreter's flat dict with `Environment`, wiring `Let`, `Assign`, `Var`, and `Block` as above.  Re-run last module's summation program (it must still work), then run the paper-machine program and confirm 51 and 2.

2.  *Nested shadowing torture.*  Write a three-level program (global, block, inner block) where the same name is bound at all three levels, and a fourth name is read from each level.  Hand-draw the environment chain at the innermost print, then confirm by execution.

3.  *Error message upgrade.*  Upgrade the `NameError` messages to also list the names visible in the entire chain ("undefined variable 'pritnValue'; did you mean one of: printValue, x, n, total?") via a `suggestions()` helper in `lookup` that collects visible names by walking the chain.  Show a before-and-after transcript on a plausible typo.

4.  *Design decision: if/while scope.*  Do `if` and `while` bodies create fresh child environments, or execute in the enclosing environment?  Implement **both** behaviors behind a flag (`body_creates_scope: bool`), write one program whose output differs between the choices, and document your team's decision in `SEMANTICS.md` with the evidence program as justification.

5.  *Instrumented environment.*  Add a `lookup_count` counter to `Environment` that accumulates across the chain and resets at each top-level `execute` call; print it after the Model 5 trace program.  Then make `lookup` cache the most recent successful lookup per name, and benchmark (`time.perf_counter`) the speedup on a tight loop reading the same variable 10,000 times.

---

## Reflection Prompt

In your notebook: the environment chain makes "context" an explicit, inspectable object: you can print the whole chain at any moment.  Where in your own debugging or thinking would you benefit from printing the chain of contexts you are currently inside?

---

## 4.  Further Reading

- Douglas Thain.  *Introduction to Compilers and Language Design*, Chapter 7.
- Robert Nystrom.  *Crafting Interpreters*, "Statements and State" and "Functions" (online): environments, then closures over them.
- Abelson and Sussman.  *Structure and Interpretation of Computer Programs*, section 3.2, the environment model, beautifully drawn.

---

Up next: the *Type Systems* activity asks what your interpreter should do with senseless values, while the `Environment` you built here goes straight into the Interpreter assignment.

