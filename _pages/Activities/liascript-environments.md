# Environments: Implementing Scope
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

## Learning Goals

By the end of this activity, you will be able to:

- Implement an `Environment` class as a chain of dictionaries linked by parent pointers and explain why a single flat dictionary cannot correctly model nested scope
- Trace the four environment operations — `define`, `lookup`, `assign`, and scope entry/exit — on a program with nested blocks
- Predict the value printed at each point in a program with shadowed variable names, explaining each step of the chain-walk lookup
- Construct the environment chain diagram for a given program snapshot and identify the lifetime and scope of each binding
- Integrate the `Environment` class into a tree-walking interpreter so that block statements correctly push and pop scopes

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

## Model 2: Read the Class

### Critical Thinking Questions

5. `define` writes only to `self.vars`; `assign` walks the chain. Construct a two-line program where confusing the two produces a wrong answer rather than an error, and state the rule: `let` means which method, bare `=` means which?
6. Verify your question 2 walk lengths by adding a counter to `lookup`. Does the executable machine agree with your paper machine?
7. "Leaving the block" is just ceasing to use the child environment. What reclaims its memory in Python, and why does the parent never need to know the child existed?

---

# Part II: The Four Operations in Practice (Day 1, continued)

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
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

### Critical Thinking Questions (Model 3)

8. After `inner.define('x', 99)`, the chain contains *two* bindings for `x`. How many environments does `inner.lookup('x')` visit before returning? How many does `outer.lookup('x')` visit?
9. `inner2.assign('x', 99)` mutated `outer2`'s binding, while `inner.define('x', 99)` left `outer`'s binding unchanged. In one sentence, state the rule: what is the correct behavior for a bare `=` assignment in a statically scoped language, and why does `assign` — not `define` — implement it?
10. The `__repr__` method uses `->` to render the chain. If you add a third level — `deep = Environment(parent=inner)` — and define a new variable `z = 5` in it, predict what `print(deep)` will show before running. Then add those two lines to the cell and verify.

---

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
