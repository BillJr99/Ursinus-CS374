<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374-Fall2026/gh-pages/_pages/Activities/liascript-scope-chains.md or locally via https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374-Fall2026/gh-pages/_pages/Activities/liascript-scope-chains.md

import: https://raw.githubusercontent.com/liascript/CodeRunner/master/README.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

# Scope Chains and Closures

*Binding and Scope* said what a name should mean.  Today you build the machine that makes it happen, and it is a small one: a linked list of dictionaries.  Then you add it to the Scheme you built, and functions finally work.

## Learning Goals

By the end of this activity, you will be able to:

- Implement an `Environment` class as a chain of dictionaries linked by parent pointers, and explain why a flat dictionary cannot model nested scope
- Trace the four environment operations (`define`, `lookup`, `assign`, and scope entry/exit) on a program with nested blocks, and predict the value printed at each point in a program with shadowed names
- Define a closure as a pair of code and its defining environment, and explain why a language with first-class functions and static scope needs it
- Trace environment diagrams for closure creation and invocation, identifying captured variable bindings and parent environment pointers
- Add `lambda` to a small Scheme, using a scope chain for its parameters

> **Before You Begin:** You need *Binding and Scope*, *From Calculator to Scheme*, *Lambda Calculus II*, and Python classes with instance variables.

---

## Directions and Group Roles

Work in your POGIL team with your rotated roles (**Manager**, **Recorder**, **Presenter**, **Reflector**).  Think each model and question through on your own first, then talk it over with your group.

---

## How Today Runs

| Segment | What your team does |
|---------|---------------------|
| Part I: The Environment Chain | Run the paper machine by hand (CTQs 9-12), check it against the Model 3 code cell, and read the class (CTQs 13-15) |
| Part II: Define, Assign, and Blocks | Run Model 5 and answer CTQs 16-18, then the linked-list calculator in Model 12 |
| Part III: Closures | Run `make_adder`, and answer CTQs 5.1 and 5.2, then run Model 5 of closures and answer CTQs 5.4-5.5 |
| Part IV: Functions in Our Scheme | Run the cell, trace `(add3 4)`, and answer the questions |
| Part V: Two Ways to Get What the Calculus Lacks | Read the section aloud, and answer CTQs 7.1 and 7.2 |

If the period runs short, Part V and the Try It Yourself blocks move to homework.

---

# Part I: The Environment Chain

*Binding and Scope* gave you the rules.  This part builds the data structure that enforces them: a chain of dictionaries linked by parent pointers.  Lookup walks outward through the chain, which is exactly what static scoping requires.

## 3.  One Dictionary Cannot Shadow

Right now your interpreter keeps every variable in one flat dictionary, `env = {}`.  That makes every variable global.  A block that declares `x` overwrites any outer `x` for good, and nothing goes away when the block ends.  The fix mirrors the nesting in the source text: one dictionary per scope, and each dictionary holds a pointer to its parent.  Entering a block creates a fresh child environment.  Leaving the block returns to the parent, and the child's bindings vanish with it.  When an inner binding hides an outer binding with the same name, we say the inner one shadows the outer one.

Lookup is the operation that finds the value of a name, and it walks the chain.  To resolve `x`, check the current environment first.  If `x` is not there, ask the parent.  Keep going until you reach the global environment.  Only past the root do you fail with a name error:

$$
\text{lookup}(x, E) = \begin{cases} E.\text{vars}[x] & x \in E.\text{vars} \\ \text{lookup}(x, E.\text{parent}) & \text{otherwise, if a parent exists} \\ \text{NameError} & \text{at the root} \end{cases}
$$

That walk is static scope in code: innermost first, then outward.  The self-paced extension *A Calculator with Variables and Scope* builds this into a working calculator.

---

**Intuition for Model 3:** A page of notes with sticky notes on top is a good model of the chain.  Global bindings live on the page.  Each inner block adds a sticky note on top.  You read the top note first, then the page under it.  When the block ends, you peel the note off and throw it away, and anything it covered is visible again.  The analogy stops at one point: a real note covers everything under it, but an environment hides only the names it defines.  Model 3 traces this process with a two-scope program.

## Model 3: Paper Machine

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

9.  Draw the environment picture at line P1: two boxes (global and block), their contents, and the parent arrow.  The Recorder keeps the drawing.
10.  Resolve each of `a`, `b`, and `c` at P1 by walking the chain.  Report the length of each walk and the printed value.
11.  At P2, the block environment is gone.  What does `print b` produce, and what happened to the binding `c`?  Which concept ended for `c` at that moment: its scope, its lifetime, or both?
12.  Predict what `print c` at P2 would do, and say which line of the lookup definition fires.

---

## Model 3 Code Cell: The Paper Machine, Executed

Run this cell to check your answers to questions 9 through 12.

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
- Leaving a block is not an operation.  There is no `pop`.  The code stops using `block`, so nothing points to it anymore.  Memory that nothing points to is garbage, and Python's garbage collector reclaims it.  Keep two ideas apart here.  The block's *scope*, the stretch of program text where its names are visible, ends at the closing brace.  The environment *object* lives until its last reference disappears, not when an instruction says so, and a closure created inside the block can keep it alive long after the block's scope has ended.
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

**Intuition for Model 4:** Read the class as three operations that differ in where they write.  `define` writes to the current frame only.  `lookup` reads, asking each frame up the chain in turn.  `assign` updates the existing binding wherever it lives and never creates a duplicate.  Mixing up `define` and `assign` is the most common environment bug.

## Model 4: Read the Class

### Critical Thinking Questions

13.  `define` writes only to `self.vars`; `assign` walks the chain.  Construct a two-line program where confusing the two produces a wrong answer rather than an error.  Then state the rule: `let` means which method, and bare `=` means which?
14.  Verify your question 10 walk lengths with the built-in tracer: call `lookup(..., trace=True)`.  Does the executable machine agree with your paper machine?
15.  Leaving the block means the interpreter stops using the child environment, and nothing else happens.  What reclaims the child's memory in Python, and why does the parent never need to know the child existed?

---

# Part II: Define, Assign, and Blocks

**Intuition for Model 5:** `define` is a hotel check-in.  It always creates a fresh entry on the current floor, even if a guest with the same name is registered on a higher floor.  `assign` is the manager walking the floors to hand the existing guest a new key; it never adds an entry.  The analogy stops at the search order: a manager might start anywhere, but `assign` always starts at the innermost frame and moves outward.  Model 5 runs both operations side by side so you can see the difference.

> Watch out: `define` in place of `assign` silently creates a shadow copy in the inner scope and leaves the outer binding unchanged.  There is no error, only a wrong answer.  Before each write, ask: am I declaring a new variable, or updating an existing one?

## Model 5: The Four Operations in Practice

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
# --- The canonical Environment class from Model 3 (repeated so this cell
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

- The demo runs the same two-line program twice, once with `define` and once with `assign`.  The only difference in the output is which frame holds the changed value.  Part IV comes down to that one contrast.
- Look at `inner` after the `define` run: it holds its own `x`.  Look at `inner2` after the `assign` run: it is empty, and `outer2`'s `x` changed instead.  Two bindings versus one.
- Neither operation ever copies a frame.  `assign` reaches through the chain and changes the binding in place.  That is why a change made deep inside a block is still visible after the block ends.

### Critical Thinking Questions

16.  After `inner.define('x', 99)`, the chain contains two bindings for `x`.  How many environments does `inner.lookup('x')` visit before returning?  How many does `outer.lookup('x')` visit?
17.  `inner2.assign('x', 99)` changed `outer2`'s binding, while `inner.define('x', 99)` left `outer`'s binding unchanged.  In one sentence, state the rule: what is the correct behavior for a bare `=` assignment in a statically scoped language, and why does `assign` (not `define`) implement it?
18.  The canonical class's `__repr__` method (Model 3) uses `->` to print the chain.  Add a third level (`deep = Environment(parent=inner, name="deep")`) and define a new variable `z = 5` in it.  Predict what `print(deep)` will show before running.  Then add those two lines to the cell and verify.

---

## 4.  Blocks Push, Statements Thread

The interpreter changes are small.  `execute(Block(stmts), env)` creates `child = Environment(parent=env)` and executes the statements against `child`.  `Let` calls `define` on the current environment.  `Assign` calls `assign`.  Evaluating a `Var` calls `lookup`.  Conditionals and loops then inherit a design decision: does an `if` or `while` body get its own scope?  C says yes with braces.  Python says no.  Your language must say something, in `SEMANTICS.md`.

> Watch out: every recursive call to `execute` or `evaluate` must receive the correct environment as an argument, never through a global variable.  It is easy to pass the outer environment into a block body instead of the freshly created child.  If variables resolve to wrong values inside blocks, first check that the right environment is threaded through every recursive call.

**Intuition for Model 6:** On an assembly line, each item gets a fresh clipboard for local notes, but the shared count lives on the factory whiteboard and must be updated there.  That is per-iteration scope: locals live in the iteration's child environment, and shared loop counters live in the parent, updated with `assign`.  The analogy stops at cleanup: a clipboard has to be handed back, but a child environment disappears on its own once nothing refers to it.

## Model 6: Blocks, Loops, and Per-Iteration Scope

When a language gives every loop body its own fresh scope, a variable declared in one iteration is invisible to the next and gone after the loop.  The cell below simulates a `while` loop where each iteration pushes a child environment.  Again, nothing new goes into the class.

```python
# --- The canonical Environment class from Model 3 (repeated so this cell
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

If the body used `define` for `n` instead of `assign`, you would recreate the bug in Model 8 (an extension at the end of this page): the outer `n` would never decrease, and the loop would never end.

### Reading the Code

- `loop_env` is rebuilt inside the `while`, once per iteration.  Move that line above the loop and every iteration shares one frame.  That is the closure-capture decision that Part V meets in Python, here visible in the interpreter itself.
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
#         from Part V of this activity is this?

# TODO 2: your language has to pick. Write the one-sentence rule for
#         SEMANTICS.md, and name a language that made each choice.

# TODO 3: harder. Make the shared version behave like the fresh one WITHOUT
#         creating a new Environment per iteration. What do you have to
#         copy instead, and what does that tell you about what a closure
#         really captures?
```
@LIA.eval(`["main.py"]`, `none`, `python3 main.py`)

Expected output: `[0, 1, 2]` and then `[2, 2, 2]`.  If you have seen `[2, 2, 2]` before, that is the point.  It is the same bug, one level down.

### Critical Thinking Questions

19.  In the first loop, `t` is defined anew each iteration and disappears at the end of each iteration.  Is `t`'s scope per-iteration, is its lifetime per-iteration, or both?  Define your terms before answering.
20.  Suppose the loop body called `loop_env.define("n", ...)` instead of `assign`, the bug from Model 8.  Explain precisely why the loop would never end: what does `define` do that prevents `glob`'s `n` from ever decreasing?
21.  In C, a `for` loop's init clause (`int i = 0`) creates a variable that is in scope for the entire loop but gone after it.  Where in the environment chain would you model that binding in your interpreter?  Would it live in the same environment as the loop body, or in a separate one?
22.  Python does not give loop bodies their own scope: a variable declared inside a `for` loop is visible after the loop ends.  Design an experiment (two small programs in your own language) that would tell a user whether your language follows Python's rule or C's rule.  State which rule your team chose and document it in `SEMANTICS.md`.

---

## Model 12: A Linked List of Dictionaries

The fix is one dictionary per scope, with a link to the scope around it, which makes a linked list:

```text
self.scope --> [ x: 10 ]          the block's scope
                  |  parent
                  v
               [ x: 1, y: 20 ]    the global scope
```

Lookup checks the first dictionary, then follows the links outward, and stops at the first match.  We also need to tell a new variable from an update: `let x = 1;` defines `x` in the current scope, and `x = 1;` walks outward and updates the `x` it finds.  Entering a block pushes a new `Scope` onto the front of the list.  Leaving the block moves back to its parent.

```python
import re

class Scope:
    """One dictionary, plus a link to the scope around it."""
    def __init__(self, parent=None):
        self.vars = {}
        self.parent = parent

    def lookup(self, name):
        scope = self
        while scope is not None:            # walk outward along the links
            if name in scope.vars:
                return scope.vars[name]
            scope = scope.parent
        raise NameError(f"undefined variable {name!r}")

    def define(self, name, value):
        self.vars[name] = value             # this scope only

    def assign(self, name, value):
        scope = self
        while scope is not None:            # update the x we find
            if name in scope.vars:
                scope.vars[name] = value
                return
            scope = scope.parent
        raise NameError(f"undefined variable {name!r}")


class Parser:
    def __init__(self, text):
        # Names have several characters, so split the text into tokens first.
        self.tokens = re.findall(r"\d+|[A-Za-z_]\w*|\S", text)
        self.pos = 0
        self.scope = Scope()                # the global scope

    def peek(self):
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return None

    def match(self, token):
        if self.peek() == token:
            self.pos += 1
            return True
        return False

    def E(self):
        value = self.T()
        while self.peek() in ("+", "-"):
            op = self.peek()
            self.match(op)
            right = self.T()
            value = value + right if op == "+" else value - right
        return value

    def T(self):
        value = self.F()
        while self.peek() in ("*", "/"):
            op = self.peek()
            self.match(op)
            right = self.F()
            value = value * right if op == "*" else value / right
        return value

    def F(self):
        token = self.peek()
        if self.match("("):
            value = self.E()
            self.match(")")
            return value
        self.match(token)
        if token.isdigit():
            return int(token)
        return self.scope.lookup(token)     # lookup: walk the chain

    def statement(self):
        token = self.peek()
        self.match(token)
        if token == "{":
            self.scope = Scope(self.scope)  # enter: push a new scope
            while not self.match("}"):
                self.statement()
            self.scope = self.scope.parent  # leave: back to the parent
            return
        if token == "print":
            print(self.E())
        elif token == "let":
            name = self.peek()
            self.match(name)
            self.match("=")
            self.scope.define(name, self.E())
        else:
            self.match("=")
            self.scope.assign(token, self.E())
        self.match(";")

    def parse(self):
        while self.peek() is not None:
            self.statement()


Parser("""
let x = 1;
let y = 2;
{
    let x = 10;
    y = 20;
    print x + y;
}
print x + y;
""").parse()                                          # 30, then 21
```
@LIA.eval(`["main.py"]`, `none`, `python3 main.py`)

Here is what happens on that program:

```text
let x = 1;        global: x=1
let y = 2;        global: x=1, y=2
{                 push:   block: (empty) -> global: x=1, y=2
let x = 10;       block: x=10 -> global: x=1, y=2       define in the block
y = 20;           block: x=10 -> global: x=1, y=20      y is not in the block, so walk out
print x + y;      x found in block, y found in global:  30
}                 pop:    global: x=1, y=20
print x + y;      the inner x is gone:                  21
```

### Reading the Code

- `Scope` is the same idea as the `Environment` class from Part I: a dictionary and a parent link.
- `statement` handles `{` with a recursive call per statement inside it, so nested blocks work without any extra code.
- Nothing deletes the inner dictionary.  The parser stops pointing at it.

### Critical Thinking Questions

38.  What does this program print if `let x = 10;` in the block becomes `x = 10;`?  Predict, and then run it.  Why does the second `print` change?

39.  What happens if you `let z = 5;` inside the block and then `print z;` after it?  Which line of `Scope` reports the error?

40.  The [Flex and Bison tutorial](https://www.billmongan.com/Ursinus-CS374-Fall2026/Tutorials/FlexAndBison) builds this same list of symbol tables in C.  Where does its `push_scope` run, compared with `Scope(self.scope)` here?

---

# Part III: Closures, the Problem and the Mechanism

A language has **first-class functions** when a function is an ordinary value: you can store it in a variable, pass it as an argument, and return it from another function.  A language has static scope when a name refers to the variable declared where the function was written.  Put those two rules together and a function can escape the scope where it was born.  To keep working, it must carry that scope with it.  What it carries is the environment chain you built in *Binding, Scope, and Environments*.  The bundle of code plus captured environment is a closure.  It is the mechanism behind `make_adder`, behind every Church encoding you ran in Python today, and behind the function values your interpreter supports.

### Key Concepts

This glossary defines the terms the activity uses.  Come back to it whenever a term starts to feel slippery.

| Term | Plain-English meaning | Why it matters |
|------|-----------------------|----------------|
| **Closure** | A function bundled with the environment where it was defined | The mechanism that lets a function read variables after their scope ends |
| **First-class function** | A function treated as an ordinary value: stored, passed, returned | Without this, closures never arise; with it, they are unavoidable |
| **Defining environment** | The scope chain in effect at the moment a function is created | This is what the closure captures, never the caller's environment |
| **Captured variable** | A variable from an enclosing scope that an inner function reads or writes | The closure keeps that variable alive after its scope returns |
| **Capture by reference** | The closure holds a pointer to the *binding*, not a snapshot of the value | Explains why closures see later changes, and the loop-variable trap |
| **Lexical (static) scope** | Names resolve where the function was *written* in the source | The rule Python, JavaScript, and Scheme use; implemented by one parent-pointer choice |
| **Dynamic scope** | Names resolve in whoever *called* the function | The historical alternative; a contrast that shows what lexical scope buys |
| **Environment diagram** | Boxes for scopes, arrows for parent and capture pointers | The picture that makes every closure question answerable |
| **Loop-variable trap** | All closures made in a loop share one binding, so all see its final value | The most common closure bug in Python and JavaScript alike |
| **Factory function** | A function whose every call creates a fresh scope and returns a closure over it | The standard fix for the trap, and the pattern behind `make_adder` |
| **Mutable cell / `nonlocal`** | The way an inner function assigns into a captured binding | How closures hold changing *state* as well as constants |

---

A function defined inside another function keeps reading the variables of its birth environment after the enclosing function has returned.  One analogy: a contractor trained in your workshop still knows the workshop's tools and rules after the workshop closes.  The analogy stops there, because the contractor carries a memory of the workshop while a closure carries a live link to it.  This section uses the classic `make_adder` example to show why this behavior is necessary and useful.

## 6.  A Function Outlives Its Scope

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

By the lifetime rules of the environments module, `make_adder`'s local scope should die at `return` and take `n` with it.  Yet `add5` still finds `n = 5`.  The resolution is that **a function value is not just code; it is a closure**, a pair of `(code, defining_environment)`.  When Python created `adder`, it captured a reference to the environment where `n` was bound.  That environment survives because the closure still points to it.  Lifetime follows reachability: an environment stays alive as long as something, such as a closure, can still reach it.

$$\text{closure} = \langle \text{params}, \text{body}, E_{\text{def}} \rangle$$

Calling a closure brings its birthplace back into use.  The call `add5(10)` creates a fresh environment for the parameter (`x = 10`).  The parent of that environment is the closure's captured environment (where `n = 5`), not the caller's environment.  That parent choice is static scoping enforced at runtime.  The entire difference between lexical and dynamic scope is one decision about which parent pointer to use.

Remember two things from this section.  A closure is code plus its defining environment.  A call runs the body in a child of that captured environment.

**Critical Thinking Questions (CTQs)**

> **CTQ 5.1** Draw the environment diagram at `print(add5(3))`: the global frame, the still-alive `make_adder` frame holding `n = 5`, the call frame holding `x = 3`, and every parent arrow.  Which arrow embodies "static scope"?

> **CTQ 5.2** After `add5 = make_adder(5)` and `add10 = make_adder(10)`, how many `make_adder` environments exist at the same time?  What does each closure's captured pointer tell you about whether closures *copy* or *reference* their environment?

> **CTQ 5.3** In the lambda calculus, `(λn. λx. x + n) 5` reduces to `λx. x + 5` by *substitution*: the 5 is pasted into the body.  State the relationship: closures are an *implementation strategy* for what substitution *specifies*.  Why might an interpreter prefer environments over literal substitution for large function bodies?

---

A closure holds a live reference to a variable binding.  Any change to that variable after the closure is created is visible through the closure.  One analogy: a closure is a security camera pointed at a shelf, not a photograph of the shelf.  When you look at the feed later, you see whatever is on the shelf now.  The analogy stops at the camera's one-way view, because a closure can also write to the shelf through `nonlocal` or a mutable cell.

> **Watch out!**  A common mistake is to think a closure *copies* the value of a variable at the moment the closure is created.  It does not.  It captures a *reference* to the binding.  If the variable changes after the closure is defined, the closure sees the new value.  The `get_x` example below demonstrates this directly.

## Model 5: Closures Capture, Not Copy

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

> **CTQ 5.4** `get_x()` returns 99 after `x = 99`.  What does this prove about whether closures copy or reference the captured binding?

> **CTQ 5.5** The `make_counter` example has TWO closures (`increment` and `reset`) that share ONE captured environment containing `count`.  Draw the environment diagram.  Which arrow makes them share state?

### Reading the Code

These notes cover the Model 5 code.

- The first block reassigns the captured variable *after* the closure is built, and the closure reports the new value.  That proves capture by reference.  If the closure had copied, it would still report the old value.
- The default-argument contrast is the control case.  `get_x_snapshot(val=x)` evaluates `x` once, at definition, and stores the result in `val`.  It is not a closure over `x` at all.
- The shared-mutable-cell block is the same mechanism used on purpose.  Two functions closing over one binding is how you get an object with two methods, which is where the Extension on closures and objects goes.

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

---

---

# Part IV: Functions in Our Scheme

Here is the Scheme from *From Calculator to Scheme* again.  Only three things changed.  `symbols` became a chain, `Env`.  `evaluate` takes the environment it is working in.  And `lambda` makes a `Closure`, which a call turns into a new scope.

```python
def tokenize(text):
    return text.replace("(", " ( ").replace(")", " ) ").split()

def read(tokens):
    token = tokens.pop(0)
    if token == "(":
        items = []
        while tokens[0] != ")":
            items.append(read(tokens))
        tokens.pop(0)                      # the closing )
        return items
    try:
        return int(token)
    except ValueError:
        return token                       # a symbol, kept as a string


# The Scheme from last time, with its one dictionary replaced by a chain.
PRIMITIVES = {
    "+": lambda a, b: a + b,
    "-": lambda a, b: a - b,
    "*": lambda a, b: a * b,
    "=": lambda a, b: a == b,
    "<": lambda a, b: a < b,
    "car": lambda p: p[0],
    "cdr": lambda p: p[1:],
    "cons": lambda a, p: [a] + p,
    "null?": lambda p: p == [],
}
class Env:
    def __init__(self, names=(), values=(), parent=None):
        self.table = dict(zip(names, values))    # this scope's dictionary
        self.parent = parent                     # the link to the scope around it

    def lookup(self, name):
        env = self
        while env is not None:                   # walk the linked list outward
            if name in env.table:
                return env.table[name]
            env = env.parent
        raise NameError(f"undefined name {name}")

    def define(self, name, value):
        self.table[name] = value                 # always in the current scope


class Closure:
    def __init__(self, params, body, env):
        self.params, self.body, self.env = params, body, env


global_env = Env(PRIMITIVES.keys(), PRIMITIVES.values())

def evaluate(x, env):
    if isinstance(x, int):
        return x
    if isinstance(x, str):
        return env.lookup(x)
    if x[0] == "define":
        env.define(x[1], evaluate(x[2], env))
        return None
    if x[0] == "quote":
        return x[1]
    if x[0] == "if":
        test, yes, no = x[1:]
        return evaluate(yes if evaluate(test, env) else no, env)
    if x[0] == "lambda":
        return Closure(x[1], x[2], env)          # remember the scope it was made in
    function, *args = [evaluate(part, env) for part in x]
    if isinstance(function, Closure):
        # A new scope for this call, linked to where the function was DEFINED.
        call_env = Env(function.params, args, function.env)
        return evaluate(function.body, call_env)
    return function(*args)


def run(text):
    tokens = tokenize(text)
    while tokens:
        result = evaluate(read(tokens), global_env)
        if result is not None:
            print(result)


run("""
(define x 1)
(define shadow (lambda (x) (+ x 10)))
(shadow 5)
x
(define adder (lambda (a) (lambda (b) (+ a b))))
(define add3 (adder 3))
(add3 4)
(define fact (lambda (n) (if (= n 0) 1 (* n (fact (- n 1))))))
(fact 5)
""")
```
@LIA.eval(`["main.py"]`, `none`, `python3 main.py`)

Trace `(add3 4)`:

```text
evaluate(add3)     finds a Closure in the global scope: params (b), and env = the scope from (adder 3)
call_env           [ b: 4 ] -> [ a: 3 ] -> [ global ]
evaluate (+ a b)   + walks all the way out to global; a is one link out; b is right here    -> 7
```

The Interpreter assignment's `scheme.c` does the same thing in C.

> **CTQ** In `call_env`, the parent is `function.env`.  Change it to `env`, the scope of the caller.  Which kind of scoping did you just build?  Find a program in this cell that prints something different, and explain why.

> **CTQ** Why can `fact` call itself, even though `fact` has not been defined at the moment the `lambda` is evaluated?

---

# Part V: Two Ways to Get What the Calculus Lacks

## 8.  A Combinator and a Captured Binding

In *Lambda Calculus II* you derived $\textbf{Z}$ and then $\textbf{Y}$, and used $\textbf{Z}$ to make a function call itself with no name anywhere in the term.  The generator `fact_gen` took "the rest of the recursion" as an ordinary parameter, and the combinator supplied it.  Nothing was captured and nothing was mutated.  There was only application and substitution.

The closure of Parts III and IV is nothing like that.  A closure gets its power from holding on to a *binding*, and `set!` gets its power from writing to that binding.  The counter remembers because the frame outlived the call that made it, and because somebody was allowed to change what the frame holds.

The two mechanisms are unrelated.  One is pure and needs no notion of memory at all; the other is nothing but memory.  Neither is derivable from the other in any obvious way.  And yet both exist to buy the same missing thing.  The bare calculus gives you no way to refer back to something, whether that something is a function you are in the middle of defining or a value you set on the last call.  The combinator buys self-reference without names.  The closure buys names that persist without a global.

This is also why CTQ 6.3 was harder than it looked.  When `Fun` runs, the function's own name is not in `env` yet, so a closure cannot capture it.  The fix in the Try It Yourself is to reach into the captured environment afterward and point the name at the closure.  That is called *tying the knot*, and it is the mutation-based answer to exactly the problem $\textbf{Y}$ solves without mutation.  Your interpreter is free to pick either one.  Most real languages pick the knot, because it is cheaper and because programmers want to write the name.

## Model 7: Choose Your Mechanism

> **CTQ 7.1** Scheme ships both mechanisms.  Write `factorial` twice, once with `define` and a self-reference, once with $\textbf{Z}$ and a generator.  Which one would you hand a first-year student, and which one would you rather implement in your evaluator?  Notice those may not be the same answer.

> **CTQ 7.2** Tying the knot creates a cycle: an environment holds a closure whose captured environment is that same environment.  $\textbf{Z}$ creates no cycle at all.  What does that difference cost a garbage collector, and does it change your answer to CTQ 7.1?

> **CTQ 7.3** A memoized function keeps a cache in a captured binding, so it mutates on every miss.  Could you memoize a $\textbf{Z}$-built function without introducing any mutation?  If not, say precisely what would have to change about the language.

---

**In-class work stops here.**  Everything below is homework and going-deeper material.

---

# Check Your Understanding

`[lambda: i for i in range(3)]` returns three functions that all print `2`. This is because:

[(X)] All three closed over the same binding of `i`, and by call time it holds the loop's final value
[( )] Python evaluates lambdas lazily and only the last one survives
[( )] List comprehensions reuse one function object
[( )] `range(3)` is exhausted before the lambdas run

---

A `while` loop's body declares `let t = ...` each iteration, and the team gives each iteration a fresh child environment.  After the loop, `t` is undefined.  This behavior is the direct consequence of:

[( )] The lexer discarding the variable
[( )] Dynamic scoping
[(X)] The binding's lifetime ending with the environment that held it, when the block scope is discarded
[( )] Python's garbage collector running mid-loop

---

A student writes `inner.define("x", 99)` when they meant to update the outer scope's `x`.  The symptom they observe is:

[( )] A `NameError` because `x` was not yet defined anywhere
[( )] The outer `x` is updated to 99, as expected
[(X)] A new inner `x` shadows the outer one, so the outer `x` is unchanged and the bug is silent
[( )] The program crashes with a `KeyError`

---

A closure is created when the evaluator meets a function expression. What does it store?

[(X)] The parameter, the unevaluated body, and the environment in force at that moment
[( )] The parameter, the body, and the values of every free variable, copied out
[( )] The fully evaluated body, ready to return on the next call
[( )] Only the body; the environment is looked up again at call time

---

In Model 6, changing `base = fn.env` to `base = env` in the `Call` branch turns the language from lexically scoped to dynamically scoped. Why is that one line enough?

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

# Exercises

1.  *Bug forensics.*  Construct a program where shadowing causes a quiet wrong answer rather than an error.  Propose one language rule that would catch it, and say what that rule costs.
2.  *Interpreter surgery.*  Replace your interpreter's flat dict with `Environment`, wiring `Let`, `Assign`, `Var`, and `Block` as Part II describes.  Re-run last module's summation program (it must still work).  Then run the paper-machine program and confirm 51 and 2.
3.  *Nested shadowing torture.*  Write a three-level program (global, block, inner block) where the same name is bound at all three levels and a fourth name is read from each level.  Hand-draw the environment chain at the innermost print, then confirm by execution.
4.  *Error message upgrade.*  Upgrade the `NameError` messages to also list the names visible in the entire chain ("undefined variable 'pritnValue'; did you mean one of: printValue, x, n, total?").  Do this with a `suggestions()` helper in `lookup` that collects visible names by walking the chain.  Show a before-and-after transcript on a plausible typo.
5.  *Design decision: if/while scope.*  Do `if` and `while` bodies create fresh child environments, or do they execute in the enclosing environment?  Implement both behaviors behind a flag (`body_creates_scope: bool`).  Write one program whose output differs between the two choices.  Document your team's decision in `SEMANTICS.md`, with that program as the evidence.
6.  *Instrumented environment.*  Add a `lookup_count` counter to `Environment` that accumulates across the chain and resets at each top-level `execute` call; print it after the Model 9 trace program.  Then make `lookup` cache the most recent successful lookup per name, and benchmark (`time.perf_counter`) the speedup on a tight loop that reads the same variable 10,000 times.

7.  *Integrate closures into Mini (30 min).*  Add closures to your Mini interpreter:
    1.  Add `FunDef(name, params, body)` and `Call(callee, args)` AST nodes
    2.  In the parser, add `fun name(params) { body }` syntax and `name(args)` call syntax
    3.  In the evaluator, implement `execute_fundef` (create closure, bind name) and `eval_call` (create child env, run body, catch ReturnSignal)
    4.  Demonstrate: a plain function, `factorial(5)`, and `make_adder` working in your language
8.  *Counter objects (15 min).*  Build `make_counter()` using closures (not a class) that returns an increment function.  Then build `make_account(balance)` with `deposit(amount)` and `withdraw(amount)` methods.  Demonstrate shared state between the two returned functions.
9.  *Trap tour (15 min).*  Reproduce the loop-variable trap in your language (or Python), apply both fixes, and explain each fix's mechanism with environment diagrams.
10.  *Scope flip experiment (20 min).*  Apply the one-line change from Model 6 (`base = fn.env` becomes `base = env`) to make your interpreter dynamically scoped.  Rerun the `show`/`demo` program from Model 2 of the *Binding, Scope, and Environments* activity in your language.  Report the output difference and explain with a diagram which environment chain the dynamically scoped version follows.

---

## Further Reading

- Robert Nystrom.  *Crafting Interpreters*, "Statements and State," "Functions," and "Closures" (online).
- Abelson and Sussman.  *Structure and Interpretation of Computer Programs*, section 3.2, the environment model, beautifully drawn.
- Steele and Sussman.  "The Art of the Interpreter" (1978): closures invented and explained.
- [Flex and Bison tutorial](https://www.billmongan.com/Ursinus-CS374-Fall2026/Tutorials/FlexAndBison): the same list of symbol tables, in C.

---

# Extension: Define When You Meant Assign (self-paced)

> Nothing in class assumes it.  Read it the first time a loop in your interpreter never terminates.

**Intuition for Model 8:** A `define` inside a loop body writes a fresh binding into the body's frame each time around.  The outer counter is never touched, so it never changes.  This model shows that bug in slow motion.

## Model 8: Define When You Meant Assign

The most common environment bug is quiet.  A student forgets that updating a loop counter needs `assign`, not `define`.  The code runs, but the outer counter never changes, so the loop runs forever (or returns wrong answers without complaint).  Nothing new goes into the class here.  Run the cell and watch the bug unfold.  With `assign` instead, the outer counter would reach 0 after three iterations; Model 6 shows that working version inside a real loop.

```python
# --- The canonical Environment class from Model 3 (repeated so this cell
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

### Critical Thinking Questions

29.  In the buggy version, the outer `counter` never decreases.  Explain step by step why `body_env2.define('counter', ...)` fails to update `glob2`'s binding, even though `glob2` is the parent environment.
30.  In your mini-language, `let x = ...` should map to `define` and bare `x = ...` should map to `assign`.  Suppose a student writes `let x = 1` inside a `while` loop, intending to update `x` each iteration.  What actually happens, and what error would you report?
31.  Suppose `assign` cannot find the variable anywhere in the chain, because the programmer wrote `x = 5` without ever declaring `let x = ...`.  Should this be a `NameError` (strict), or should your interpreter auto-declare the variable in the global scope (permissive)?  List one language that takes each approach.

---

# Extension: A Three-Level Environment Chain Trace (self-paced)

> Nothing in class assumes it.  It is the closest rehearsal for the lab's paper trace.

**Intuition for Model 9:** In a statically scoped language, the chain is fixed by where code appears in the source, not by who called it.  A three-level nest stacks three frames in the order the blocks enclose one another, and lookup searches innermost first.  The tracer built into `lookup` prints every hop, so you can check the counts against your own trace.

> Watch out: in lexical (static) scoping, the environment chain follows the source code structure.  In dynamic scoping, it follows the runtime call stack.  Your class is lexical because the parent pointer is set when the child environment is created (at block entry), not when a function is called.  Set parents from the call stack instead and your language silently becomes dynamically scoped, which is almost certainly not what you want.

Before you run the cell, trace line INNER by hand.  `lookup("x")` misses in `inner-block` and `mid-block` and finds `x = 1` in `global`: 3 hops.  `lookup("y")` finds the shadowing `y = 20` in `mid-block`: 2 hops, because the first match beats `global`'s `y = 2`.  `lookup("z")` and `lookup("w")` hit at once in `inner-block`: 1 hop each.  Total hops: 3 + 2 + 1 + 1 = 7.  The result is 1 + 20 + 300 + 400 = 721.  Check both numbers against the trace output.

## Model 9: A Three-Level Environment Chain Trace

No new code is needed.  Your canonical `lookup` already carries the tracer (`trace=True`), and this model is where it earns its keep.  The cell below builds a three-level program and prints a full trace of every lookup at line INNER, showing which environment satisfied each one.  Extend it to trace lines MID and OUTER.

```python
# --- The canonical Environment class from Model 3 (repeated so this cell
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

### Critical Thinking Questions

32.  At line INNER, how many environment hops do all four lookups together require?  Count from the trace output.  Could you reduce this count without changing semantics?  (Hint: think about which variable is looked up most often in a real program.)
33.  The trace shows that `y` resolves to 20 at INNER (found in `mid-block`) rather than 2 (in `global`).  This is shadowing.  Now suppose your language also has a keyword `outer` that explicitly requests the enclosing scope's binding, skipping the innermost match.  How would you modify `lookup` to support `outer.y` vs. `y`?
34.  At line OUTER, `w` and `z` are gone.  Is this a scope end, a lifetime end, or both?  Can you construct a scenario in a language with closures where the lifetime of a binding outlives its lexical scope?  (You do not need to implement this; describe it.)

---

# Extension: Variable Storage, A Step-by-Step Trace (self-paced)

> Nothing in class assumes it.  Work it before you wire the `Environment` class into your interpreter.

## Model 10: Dictionary-Based Environment, Walking Through Every Operation

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
# --- The canonical Environment class from Model 3 (repeated so this cell
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

35.  In Step 6 of the trace (`total = total + i`), the lookup for `total` walks to the global environment, and the assign also updates the global.  Walk through the `assign` method step by step to show exactly why `inner.assign("total", 1)` updates `glob.vars["total"]` rather than creating a new `inner.vars["total"]`.

36.  The `__repr__` method prints the chain as `inner:{...} -> global:{...}`.  After Step 6, what does the full chain print?  Write it out before running the code, then confirm.

37.  Extend the cell with a shadowing experiment: `outer` holds `x = 10`, and its child `inner2` holds its own `x = 99`.  `inner2.assign("x", 42)` updates the inner binding, because that is the first match on the walk.  With `inner2.define("x", 42)` instead, what would `inner2.lookup("x")` and `outer.lookup("x")` return?  State the `define`/`assign` difference in one sentence.

---

# Extension: Closures in an AST Interpreter (self-paced)

## 7.  Theory: One Field, One Line

Part III used Python to show you *its* closures.  Now you build your own.  It takes very little: a closure is a three-field record, and the entire static-versus-dynamic decision is one word in one line.

When the evaluator meets a function expression, it does **not** evaluate the body.  It packages three things and returns them:

```
Closure(param, body, env)
```

The `param` and `body` come straight off the abstract syntax tree (AST).  The third field, `env`, is the environment at the moment the function was created.  This is the function's lexical environment: the scope chain in force where the function appears in the source.  Capturing it is the one thing this record exists to do.

When the evaluator later meets a call, it evaluates the function, evaluates the argument, and then evaluates the body in

```
closure.env.extend(closure.param, argument)
```

Read that line carefully, because the session turns on it.  The body runs in a child of the closure's captured environment, not a child of the environment where the call sits.  Change `closure.env` to the caller's `env` on that one line and you have written a dynamically scoped language.  Nothing else has to change.

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

## Model 6: Build the Closure, Then Flip the Switch

This is a complete evaluator for a language with first-class functions.  The `LEXICAL` flag at the top selects which environment a call body runs in, and the *same* program runs under both settings.

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

- The `Fun` branch is three words long and never touches the body.  A function value is *not* a running thing.  It is a suspended thing plus the environment it was suspended in.
- `Closure.env` is the single field that implements static scope.  The evaluator fills it in at `Fun`, reads it at `Call`, and never modifies it.
- `base = fn.env if lexical else env` is the entire scoping discipline of the language, on one line.  Every hard question about scope reduces to which of those two names you write there.
- `extend` returns a *new* `Env` rather than mutating.  That is what lets two calls to the same closure run without seeing each other's arguments, and it is why recursion works at all.
- `Call` evaluates `fn` and `arg` in the *current* `env` under both settings.  Only the body's environment changes.  Getting that wrong gives a language where even the argument expression resolves strangely.

> **Watch out!**  It is tempting to store the *values* of the free variables in the closure instead of the environment: capture `x = 10` rather than a pointer to the frame holding `x`.  That works until something reassigns `x`.  Then your closure reads a stale copy while Python's would see the update.  Model 5 already showed the difference; this is where you either preserve it or lose it.

Remember two things from this part.  `Fun` captures the defining environment and evaluates nothing.  `Call` extends that captured environment, and swapping it for the caller's environment is the whole difference between lexical and dynamic scope.

### Critical Thinking Questions

> **CTQ 6.1** Run the model and record all four numbers.  For the first program, which result is 11 and which is 100?  Explain each in one sentence using the words "defining" and "calling."

> **CTQ 6.2** `Closure` holds `env`, but `Env.extend` never copies bindings.  If some later statement reassigns `x` in the captured frame, does the closure see the new value or the old one?  Which of the two capture strategies from Model 5 does that make this?

> **CTQ 6.3** Recursion is not implemented anywhere in this evaluator, yet `bump(bump(0))` works.  What would you have to add for a function to call *itself* by name, and why is that harder than it looks?  (Hint: at the moment `Fun` runs, is the function's own name in `env` yet?)

> **CTQ 6.4** Write down what your team's language does, and put it in `SEMANTICS.md` as one sentence naming the environment a call body runs in.

### Try It Yourself

Add recursion, which is the one thing the model above cannot do.

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

Expected output as written: a `NameError` naming `fact`, with the explanation.  Once TODO 1 is in, `fact(5) = 120`.  Those two lines are why `letrec` exists at all.

---

---

# Extension: The Loop-Variable Trap (self-paced)

> Nothing in class assumes it.  You met the trap in Part III of *Binding and Scope*; this extension draws it as boxes.

The loop-variable trap is one of the most common beginner bugs in Python and JavaScript alike.  It happens when every closure created in a loop captures the same variable binding instead of its own private copy.  One analogy: every worker on a factory floor shares one whiteboard for the current job number.  By the time any worker reads the board, the number has moved on to the last job.  The analogy stops at the sharing, because the fix in code is to give each closure its own board, which a factory cannot do by rewriting one line.

> **Watch out!**  When you write `[lambda: i for i in range(3)]`, all three lambdas capture *one* variable `i`, the same loop variable.  By the time any of them is called, the loop has finished and `i` is `2`.  This is not a bug in Python.  It is the correct behavior of reference capture.  The two fixes shown (default argument and factory function) both work by creating a separate binding per iteration.

## 13.  The Famous Python Bug

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

> **CTQ 10.1** All three lambdas captured the same `i` binding.  After the loop, what is `i`?  Why do all three lambdas return 2?

> **CTQ 10.2** Fix 1 uses `lambda i=i: i`.  Python evaluates the outer `i` (the default argument value) at *definition time*, which captures the current value.  Why does this work, while the capture in the original version does not?

> **CTQ 10.3** Fix 2 uses a factory function `make_fn(i)` that creates a new scope.  Draw the environment diagram showing why each returned lambda has a *different* captured environment.

> **CTQ 10.4** JavaScript's historic `var` scoping caused the same bug; `let` was introduced to fix it.  How does `let` create "per-iteration" scope?  Why can't `var` do this?

---

The code above showed the trap and two fixes.  The notes below explain the code, the Try It Yourself asks you to predict five variants, and Model 10 then draws the trap as boxes.  The broken and fixed versions differ by exactly one thing (how many environment boxes exist), and the box diagram makes the bug visible at a glance.

### Reading the Code

- `[lambda: i for i in range(3)]` builds three functions that all close over the *same* `i`.  Nothing about that is a bug.  It is capture-by-reference doing exactly what Model 5 demonstrated on purpose.
- The two fixes attack different halves.  The default argument stops closing over `i` at all, so there is nothing to share.  The factory function makes a new binding per iteration, so there are three `i`s to close over instead of one.
- JavaScript's `var` had this exact shape, and `let` changed it by giving loop bodies per-iteration bindings.  You made the same decision in the Model 6 Try It Yourself of *Binding, Scope, and Environments*; JavaScript made it at ecosystem scale.

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

Expected output: `a` and `d` give `[2, 2, 2]`; `b`, `c`, and `e` give `[0, 1, 2]`.  If you predicted the comprehension and the for-loop would differ, note that they do not.  The comprehension's scope is not what saves you.

## Model 10: The Loop Trap, Drawn as Boxes

**Broken:** `fns = [lambda: i for i in range(3)]`.  The comprehension runs in a single scope, so there is exactly one box holding `i`, and every lambda's capture arrow points at it:

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

Here is the broken version's history as a timeline.  The trap is a *timing* bug: capture is by reference, and the calls happen after the last write.

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

Remember two things from this part.  Closures made in one scope share one binding, so they all see its final value.  A factory call makes a fresh scope, so each closure gets its own binding.

**Critical Thinking Questions (CTQs)**

> **CTQ 10.5** Which single line of the cell's output is direct evidence for the "three arrows, one box" picture?  Which line is evidence for "three boxes"?

> **CTQ 10.6** In the fixed diagram, what act creates each new box: the `lambda` *definition*, or the *call* to `make_fn`?  Justify your answer with the environment-creation rule from Part VI (a call builds a new environment).

> **CTQ 10.7** Fix 1's lambdas report `__closure__ = None`; they are not closures at all.  Where does each one's `i` live instead, and why does that location make capture unnecessary?

---

Two closures created by separate calls to `make_adder(5)` and `make_adder(3)` return different results for the same input because:

[( )] The function body's code differs between them
[(X)] Each closure captured a different defining environment in which `n` is bound to a different value
[( )] Python caches the most recent return value
[( )] Closures copy the global environment at call time

---

# Extension: Closures vs. Objects (self-paced)

> Nothing in class assumes it.  Read it before your team decides whether its language gets objects, closures, or both.

Objects and closures do the same job.  Both bundle state with behavior, and both control which code can reach that state.  They look different at first: an object is a class instance with named fields, and a closure is a function bundled with hidden environment variables.  This model builds a counter both ways, side by side, so you can see the parallel directly.

> **Watch out!**  Closures are not limited to functional languages.  Python, JavaScript, Ruby, and Java (through lambdas) all have closures.  A common misconception is that "closures = Haskell/Scheme only."  In modern JavaScript, you use a closure every time you write a callback, an event handler, or a `useEffect` hook in React.

## 14.  Closures and Objects Are Two Views of One Idea

A well-known saying in the field puts it this way: "Closures are a poor man's objects; objects are a poor man's closures."  Each can stand in for the other.  They are dual.

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

> **CTQ 11.1** In the closure-based counter, `count` is a shared mutable cell.  In the object-based counter, `self._count` is a field.  What is the structural difference?  What is the conceptual difference?

> **CTQ 11.2** The closure counter uses a list `[start]` to work around Python's scoping rules for `nonlocal`.  Rewrite it using `nonlocal count` (Python 3) instead of a list.  Why is `nonlocal` cleaner?

> **CTQ 11.3** Languages like OCaml and Haskell have closures but no classes.  Java before version 8 had classes but no lambdas; its nearest thing to a closure was an anonymous inner class, an object that could capture only `final` local variables.  From what you now know about the implementation of each, argue: which is more fundamental?

---

**Up next:** *Type Systems* asks what your interpreter should do with senseless values.
