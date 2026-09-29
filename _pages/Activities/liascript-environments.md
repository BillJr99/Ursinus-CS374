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

A running program must answer one question over and over: what value does the name `x` hold right now?  An **environment** is the data structure that answers it.  An environment is a table that pairs each variable name with its current value; one such pair is a binding.  One table is not enough.  A block or a function can declare its own `x` that hides the outer `x`, and that inner `x` must disappear when the block ends.  So each block gets its own environment, and each environment keeps a pointer to the environment that encloses it, called its parent.  Following those pointers outward is the parent chain.  Building and walking that chain is how your interpreter enforces every scope rule.

## Learning Goals

By the end of this activity, you will be able to:

- Implement an `Environment` class as a chain of dictionaries linked by parent pointers, and explain why a flat dictionary cannot model nested scope
- Trace the four environment operations (`define`, `lookup`, `assign`, and scope entry/exit) on a program with nested blocks
- Predict the value printed at each point in a program with shadowed variable names, and explain each step of the chain walk
- Draw the environment chain for a given program snapshot and identify the lifetime and scope of each binding
- Wire the `Environment` class into a tree-walking interpreter so that block statements push and pop scopes correctly

> **Before You Begin:** This activity assumes you can:
> - Explain the difference between *scope* (where a name is visible in the source text) and *lifetime* (how long its storage exists at runtime)
> - Read and write basic Python dictionaries and classes (including `__init__`, instance variables, and simple `while` loops)
> - Describe static (lexical) scoping: a name resolves to the innermost enclosing declaration at the point where it appears in the source
>
> If any of these feel shaky, review them first.

In *Binding and Scope* you learned the rules.  Today you build the data structure that enforces them: a chain of dictionaries linked by parent pointers.  Lookup walks outward through the chain, which is exactly what static scoping requires.  The `Environment` class you build here is the one your interpreter assignment needs.  The path today: why one dict fails $\rightarrow$ the chain $\rightarrow$ the four operations $\rightarrow$ blocks that create and discard scopes.

---

## Directions and Group Roles

Work in your POGIL team with your rotated roles (**Manager**, **Recorder**, **Presenter**, **Reflector**).  Think each model and question through on your own first, then talk it over with your group.  The Recorder posts your answers to the Class Activity Questions discussion board.  The Presenter reports out wherever you disagreed or found another approach.  After class, respond to the reflection prompt on your own in your notebook.

---

# Part I: The Chain

## 1.  One Dictionary Cannot Shadow

Right now your interpreter keeps every variable in one flat dictionary, `env = {}`.  That makes every variable global.  A block that declares `x` overwrites any outer `x` for good, and nothing goes away when the block ends.  The fix mirrors the nesting in the source text: one dictionary per scope, and each dictionary holds a pointer to its parent.  Entering a block creates a fresh child environment.  Leaving the block returns to the parent, and the child's bindings vanish with it.  When an inner binding hides an outer binding with the same name, we say the inner one shadows the outer one.

Lookup is the operation that finds the value of a name, and it walks the chain.  To resolve `x`, check the current environment first.  If `x` is not there, ask the parent.  Keep going until you reach the global environment.  Only past the root do you fail with a name error:

$$
\text{lookup}(x, E) = \begin{cases} E.\text{vars}[x] & x \in E.\text{vars} \\ \text{lookup}(x, E.\text{parent}) & \text{otherwise, if a parent exists} \\ \text{NameError} & \text{at the root} \end{cases}
$$

That walk is static scope in code: innermost first, then outward.

---

**Intuition for Model 1:** A page of notes with sticky notes on top is a good model of the chain.  Global bindings live on the page.  Each inner block adds a sticky note on top.  You read the top note first, then the page under it.  When the block ends, you peel the note off and throw it away, and anything it covered is visible again.  The analogy stops at one point: a real note covers everything under it, but an environment hides only the names it defines.  Model 1 traces this process with a two-scope program.

## Model 1: Paper Machine

A paper machine is a trace you run by hand: you play the interpreter and draw each environment as a box.  The program (block braces create scopes):

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
2.  Resolve each of `a`, `b`, and `c` at P1 by walking the chain.  Report the length of each walk and the printed value.
3.  At P2, the block environment is gone.  What does `print b` produce, and what happened to the binding `c`?  Which concept ended for `c` at that moment: its scope, its lifetime, or both?
4.  Predict what `print c` at P2 would do, and say which line of the lookup definition fires.

---

## Model 1 Code Cell: The Paper Machine, Executed

Run this cell to check your answers to questions 1 through 4.

This cell holds the canonical `Environment` class, the one complete build in this activity.  Every later cell repeats the class at the top so that each cell runs on its own.  Read it here once.  In later cells, look only at the code below the class.

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

- `vars` and `parent` are the whole data structure.  Each `Environment` object is one frame: one box in your drawing.  Every method on the class is a walk over the chain of frames.  There is no other state anywhere.
- `define` writes to `self.vars` and never looks at `parent`.  `assign` never writes to `self.vars` unless the name is already there.  That one asymmetry is the whole difference between declaring and updating, and it is where most interpreter bugs live.
- `lookup` walks outward and stops at the first frame that has the name.  Shadowing is not a special case in the code.  It falls out of stopping early.
- Leaving a block is not an operation.  There is no `pop`.  The code stops using `block`, so nothing points to it anymore.  Memory that nothing points to is garbage, and Python's garbage collector reclaims it.  A scope ends when its last reference disappears, not when an instruction says so.
- `__repr__` prints the chain outward with `->`, which is why the printed trace reads like the boxes you drew on paper.

### Try It Yourself

Break the chain on purpose and watch which operation notices.

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

Before you edit anything, the chain prints as `inner:{} -> global:{'total': 0}` at the start and again at the end.  Each TODO changes exactly one thing, so run the cell after each one rather than after all three.

---

**Intuition for Model 2:** Read the class as three operations that differ in where they write.  `define` writes to the current frame only.  `lookup` reads, asking each frame up the chain in turn.  `assign` updates the existing binding wherever it lives and never creates a duplicate.  Mixing up `define` and `assign` is the most common environment bug.

## Model 2: Read the Class

### Critical Thinking Questions

5.  `define` writes only to `self.vars`; `assign` walks the chain.  Construct a two-line program where confusing the two produces a wrong answer rather than an error.  Then state the rule: `let` means which method, and bare `=` means which?
6.  Verify your question 2 walk lengths with the built-in tracer: call `lookup(..., trace=True)`.  Does the executable machine agree with your paper machine?
7.  Leaving the block means the interpreter stops using the child environment, and nothing else happens.  What reclaims the child's memory in Python, and why does the parent never need to know the child existed?

---

# Part II: The Four Operations in Practice

**Intuition for Model 3:** `define` is a hotel check-in.  It always creates a fresh entry on the current floor, even if a guest with the same name is registered on a higher floor.  `assign` is the manager walking the floors to hand the existing guest a new key; it never adds an entry.  The analogy stops at the search order: a manager might start anywhere, but `assign` always starts at the innermost frame and moves outward.  Model 3 runs both operations side by side so you can see the difference.

> Watch out: `define` in place of `assign` silently creates a shadow copy in the inner scope and leaves the outer binding unchanged.  There is no error, only a wrong answer.  Before each write, ask: am I declaring a new variable, or updating an existing one?

## Model 3: The Four Operations in Practice

The `Environment` class has exactly four operations.  Which scope each one targets is the whole story of variable handling in your interpreter.

| Operation | Method | Scope targeted | Used for |
|-----------|--------|----------------|----------|
| **Define** | `define(name, val)` | current (innermost) only | `let x = ...` declarations |
| **Lookup** | `lookup(name)` | walks outward to root | reading any variable `x` |
| **Assign** | `assign(name, val)` | walks outward, updates first match | bare `x = ...` assignments |
| **Push** | `Environment(parent=e)` | creates a new innermost | entering a block `{ ... }` |

The critical distinction: `define` writes to `self.vars` without checking ancestors, so a child silently creates a new shadowing binding.  `assign` walks first and then writes, updating the binding where it was first declared.

Run the cell below to see all four operations interact; no new methods are needed.  Before you run it, predict what each `print` will output.

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
print(f"outer.lookup('x') = {outer.lookup('x')}")   # 10, unaffected

# assign modifies the EXISTING binding (walks to outer)
outer2 = Environment(name="outer2")
outer2.define('x', 10)
inner2 = Environment(parent=outer2, name="inner2")
inner2.assign('x', 99)   # modifies outer2's x
print(f"inner2.lookup('x') = {inner2.lookup('x')}")   # 99
print(f"outer2.lookup('x') = {outer2.lookup('x')}")   # 99, changed

print(f"\nEnvironment chain: {inner}")
```
@LIA.eval(`["main.py"]`, `none`, `python3 main.py`)

### Reading the Code

- The demo runs the same two-line program twice, once with `define` and once with `assign`.  The only difference in the output is which frame holds the changed value.  Part II comes down to that one contrast.
- Look at `inner` after the `define` run: it holds its own `x`.  Look at `inner2` after the `assign` run: it is empty, and `outer2`'s `x` changed instead.  Two bindings versus one.
- Neither operation ever copies a frame.  `assign` reaches through the chain and changes the binding in place.  That is why a change made deep inside a block is still visible after the block ends.

### Critical Thinking Questions (Model 3)

8.  After `inner.define('x', 99)`, the chain contains two bindings for `x`.  How many environments does `inner.lookup('x')` visit before returning?  How many does `outer.lookup('x')` visit?
9.  `inner2.assign('x', 99)` changed `outer2`'s binding, while `inner.define('x', 99)` left `outer`'s binding unchanged.  In one sentence, state the rule: what is the correct behavior for a bare `=` assignment in a statically scoped language, and why does `assign` (not `define`) implement it?
10.  The canonical class's `__repr__` method (Model 1) uses `->` to print the chain.  Add a third level (`deep = Environment(parent=inner, name="deep")`) and define a new variable `z = 5` in it.  Predict what `print(deep)` will show before running.  Then add those two lines to the cell and verify.

---

**Intuition for Model 3 Extended:** A `define` inside a loop body writes a fresh binding into the body's frame each time around.  The outer counter is never touched, so it never changes.  This model shows that bug in slow motion.

## Model 3 Extended: Define-when-you-meant-Assign

The most common environment bug is quiet.  A student forgets that updating a loop counter needs `assign`, not `define`.  The code runs, but the outer counter never changes, so the loop runs forever (or returns wrong answers without complaint).  Nothing new goes into the class here.  Run the cell and watch the bug unfold.  With `assign` instead, the outer counter would reach 0 after three iterations; Model 4 shows that working version inside a real loop.

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
12.  In your mini-language, `let x = ...` should map to `define` and bare `x = ...` should map to `assign`.  Suppose a student writes `let x = 1` inside a `while` loop, intending to update `x` each iteration.  What actually happens, and what error would you report?
13.  Suppose `assign` cannot find the variable anywhere in the chain, because the programmer wrote `x = 5` without ever declaring `let x = ...`.  Should this be a `NameError` (strict), or should your interpreter auto-declare the variable in the global scope (permissive)?  List one language that takes each approach.

---

# Part III: Blocks, Loops, and Per-Iteration Scope

## 2.  Blocks Push, Statements Thread

The interpreter changes are small.  `execute(Block(stmts), env)` creates `child = Environment(parent=env)` and executes the statements against `child`.  `Let` calls `define` on the current environment.  `Assign` calls `assign`.  Evaluating a `Var` calls `lookup`.  Conditionals and loops then inherit a design decision: does an `if` or `while` body get its own scope?  C says yes with braces.  Python says no.  Your language must say something, in `SEMANTICS.md`.

> Watch out: every recursive call to `execute` or `evaluate` must receive the correct environment as an argument, never through a global variable.  It is easy to pass the outer environment into a block body instead of the freshly created child.  If variables resolve to wrong values inside blocks, first check that the right environment is threaded through every recursive call.

**Intuition for Model 4:** On an assembly line, each item gets a fresh clipboard for local notes, but the shared count lives on the factory whiteboard and must be updated there.  That is per-iteration scope: locals live in the iteration's child environment, and shared loop counters live in the parent, updated with `assign`.  The analogy stops at cleanup: a clipboard has to be handed back, but a child environment disappears on its own once nothing refers to it.

## Model 4: Blocks, Loops, and Per-Iteration Scope

When a language gives every loop body its own fresh scope, a variable declared in one iteration is invisible to the next and gone after the loop.  The cell below simulates a `while` loop where each iteration pushes a child environment.  Again, nothing new goes into the class.

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

If the body used `define` for `n` instead of `assign`, you would recreate the Model 3 Extended bug: the outer `n` would never decrease, and the loop would never end.

### Reading the Code

- `loop_env` is rebuilt inside the `while`, once per iteration.  Move that line above the loop and every iteration shares one frame.  That is the closure-capture decision from *Names, Binding, and Scope*, now visible in the interpreter rather than in Python.
- `n` is updated with `assign`, so the write reaches out to `glob` and the loop can end.  `t` is created with `define`, so it stays in `loop_env` and vanishes each iteration.  Swap those two calls and you get an infinite loop, the most common bug in this assignment.
- The final lookup of `t` raising `NameError` is the proof that per-iteration scope worked.  A test that only checks the printed values would pass even if `t` leaked.

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

Expected output: `[0, 1, 2]` and then `[2, 2, 2]`.  If you have seen `[2, 2, 2]` before, that is the point.  It is the same bug, one level down.

### Critical Thinking Questions (Model 4)

14.  In the first loop, `t` is defined anew each iteration and disappears at the end of each iteration.  Is `t`'s scope per-iteration, is its lifetime per-iteration, or both?  Define your terms before answering.
15.  Suppose the loop body called `loop_env.define("n", ...)` instead of `assign`, the bug from Model 3 Extended.  Explain precisely why the loop would never end: what does `define` do that prevents `glob`'s `n` from ever decreasing?
16.  In C, a `for` loop's init clause (`int i = 0`) creates a variable that is in scope for the entire loop but gone after it.  Where in the environment chain would you model that binding in your interpreter?  Would it live in the same environment as the loop body, or in a separate one?
17.  Python does not give loop bodies their own scope: a variable declared inside a `for` loop is visible after the loop ends.  Design an experiment (two small programs in your own language) that would tell a user whether your language follows Python's rule or C's rule.  State which rule your team chose and document it in `SEMANTICS.md`.

---

**Intuition for Model 5:** In a statically scoped language, the chain is fixed by where code appears in the source, not by who called it.  A three-level nest stacks three frames in the order the blocks enclose one another, and lookup searches innermost first.  The tracer built into `lookup` prints every hop, so you can check the counts against your own trace.

> Watch out: in lexical (static) scoping, the environment chain follows the source code structure.  In dynamic scoping, it follows the runtime call stack.  Your class is lexical because the parent pointer is set when the child environment is created (at block entry), not when a function is called.  Set parents from the call stack instead and your language silently becomes dynamically scoped, which is almost certainly not what you want.

Before you run the cell, trace line INNER by hand.  `lookup("x")` misses in `inner-block` and `mid-block` and finds `x = 1` in `global`: 3 hops.  `lookup("y")` finds the shadowing `y = 20` in `mid-block`: 2 hops, because the first match beats `global`'s `y = 2`.  `lookup("z")` and `lookup("w")` hit at once in `inner-block`: 1 hop each.  Total hops: 3 + 2 + 1 + 1 = 7.  The result is 1 + 20 + 300 + 400 = 721.  Check both numbers against the trace output.

## Model 5: A Three-Level Environment Chain Trace

No new code is needed.  Your canonical `lookup` already carries the tracer (`trace=True`), and this model is where it earns its keep.  The cell below builds a three-level program and prints a full trace of every lookup at line INNER, showing which environment satisfied each one.  Extend it to trace lines MID and OUTER.

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

- Three frames, three groups of `define` calls at different depths, and every printed lookup reports the hop count that found it.  Read the hop count as the cost of a name: a variable two blocks out costs two pointer follows on every use.
- `x` is found in the global frame from all three depths.  `z` resolves to a different value depending on where you stand.  Same name, same program, three answers, all correct.
- The `w` lookup from MID raising `NameError` is the containment check.  Inner names are invisible from outside, and that property is what makes blocks safe to nest.

### Critical Thinking Questions (Model 5)

18.  At line INNER, how many environment hops do all four lookups together require?  Count from the trace output.  Could you reduce this count without changing semantics?  (Hint: think about which variable is looked up most often in a real program.)
19.  The trace shows that `y` resolves to 20 at INNER (found in `mid-block`) rather than 2 (in `global`).  This is shadowing.  Now suppose your language also has a keyword `outer` that explicitly requests the enclosing scope's binding, skipping the innermost match.  How would you modify `lookup` to support `outer.y` vs. `y`?
20.  At line OUTER, `w` and `z` are gone.  Is this a scope end, a lifetime end, or both?  Can you construct a scenario in a language with closures where the lifetime of a binding outlives its lexical scope?  (You do not need to implement this; describe it.)

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

Before you wire the `Environment` class into your interpreter, trace every environment operation on one concrete program.  This model runs that program step by step and prints the state of every dictionary at each moment.  The goal is to predict the chain's exact contents at any point in any program, without running it.

The program to trace:

```
let total = 0;
let n = 5;
{
    let i = 1;
    total = total + i;       # prints: total=1 after first iteration
}
print total;
```

Before you run the trace, predict the chain's contents after each of these moments: both `let` statements, block entry, `let i = 1`, the assignment `total = total + i`, and block exit.

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

**CTQ 6.1** In Step 6 of the trace (`total = total + i`), the lookup for `total` walks to the global environment, and the assign also updates the global.  Walk through the `assign` method step by step to show exactly why `inner.assign("total", 1)` updates `glob.vars["total"]` rather than creating a new `inner.vars["total"]`.

**CTQ 6.2** The `__repr__` method prints the chain as `inner:{...} -> global:{...}`.  After Step 6, what does the full chain print?  Write it out before running the code, then confirm.

**CTQ 6.3** Extend the cell with a shadowing experiment: `outer` holds `x = 10`, and its child `inner2` holds its own `x = 99`.  `inner2.assign("x", 42)` updates the inner binding, because that is the first match on the walk.  With `inner2.define("x", 42)` instead, what would `inner2.lookup("x")` and `outer.lookup("x")` return?  State the `define`/`assign` difference in one sentence.

---

# Part V: Wiring It into the Interpreter

## 3.  Exercises

1.  *Interpreter surgery.*  Replace your interpreter's flat dict with `Environment`, wiring `Let`, `Assign`, `Var`, and `Block` as Section 2 describes.  Re-run last module's summation program (it must still work).  Then run the paper-machine program and confirm 51 and 2.

2.  *Nested shadowing torture.*  Write a three-level program (global, block, inner block) where the same name is bound at all three levels and a fourth name is read from each level.  Hand-draw the environment chain at the innermost print, then confirm by execution.

3.  *Error message upgrade.*  Upgrade the `NameError` messages to also list the names visible in the entire chain ("undefined variable 'pritnValue'; did you mean one of: printValue, x, n, total?").  Do this with a `suggestions()` helper in `lookup` that collects visible names by walking the chain.  Show a before-and-after transcript on a plausible typo.

4.  *Design decision: if/while scope.*  Do `if` and `while` bodies create fresh child environments, or do they execute in the enclosing environment?  Implement both behaviors behind a flag (`body_creates_scope: bool`).  Write one program whose output differs between the two choices.  Document your team's decision in `SEMANTICS.md`, with that program as the evidence.

5.  *Instrumented environment.*  Add a `lookup_count` counter to `Environment` that accumulates across the chain and resets at each top-level `execute` call; print it after the Model 5 trace program.  Then make `lookup` cache the most recent successful lookup per name, and benchmark (`time.perf_counter`) the speedup on a tight loop that reads the same variable 10,000 times.

---

## Reflection Prompt

In your notebook: the environment chain makes "context" an explicit object you can inspect.  You can print the whole chain at any moment.  Where in your own debugging or thinking would it help to print the chain of contexts you are currently inside?

---

## 4.  Further Reading

- Douglas Thain.  *Introduction to Compilers and Language Design*, Chapter 7.
- Robert Nystrom.  *Crafting Interpreters*, "Statements and State" and "Functions" (online): environments, then closures over them.
- Abelson and Sussman.  *Structure and Interpretation of Computer Programs*, section 3.2, the environment model, beautifully drawn.

---

Up next: the *Type Systems* activity asks what your interpreter should do with senseless values.  The `Environment` you built here goes straight into the Interpreter assignment.
