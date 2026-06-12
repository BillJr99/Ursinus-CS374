# Environments: Implementing Scope
<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://github.com/BillJr99/Ursinus-CS374-Fall2026/blob/gh-pages/_pages/Activities/liascript-environments.md or locally via https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374/gh-pages/_pages/Activities/liascript-environments.md

import: https://raw.githubusercontent.com/liascript/CodeRunner/master/README.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

# Environments: Implementing Scope

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

## Code Cell

```python
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
        try:
            env = self
            while env is not None:
                if name in env.vars:
                    return env.vars[name]
                env = env.parent
            raise NameError(f"undefined variable {name!r}")
        except NameError:
            raise
        except Exception as e:
            print(f"[environments:lookup] {e}")
            import traceback; traceback.print_exc()
            raise

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
```

---

## Model 2: Read the Class

### Critical Thinking Questions

5. `define` writes only to `self.vars`; `assign` walks the chain. Construct a two-line program where confusing the two produces a wrong answer rather than an error, and state the rule: `let` means which method, bare `=` means which?
6. Verify your question 2 walk lengths by adding a counter to `lookup`. Does the executable machine agree with your paper machine?
7. "Leaving the block" is just ceasing to use the child environment. What reclaims its memory in Python, and why does the parent never need to know the child existed?

---

# Part II: Wiring It into the Interpreter (Day 2)

## 2. Blocks Push, Statements Thread

The interpreter changes are small and precise: `execute(Block(stmts), env)` creates `child = Environment(parent=env)` and executes the statements against `child`; `Let` calls `define` on the *current* environment; `Assign` calls `assign`; `Var` evaluation calls `lookup`. Conditionals and loops then inherit a design decision: does an `if` body or `while` body get its own scope? (C says yes with braces; Python says no; your language must say something, in `SEMANTICS.md`.)

[[MC]]
A `while` loop's body declares `let t = ...` each iteration, and the team gives each iteration a fresh child environment. After the loop, `t` is undefined. This behavior is the direct consequence of:
- ( ) The lexer discarding the variable
- ( ) Dynamic scoping
- (x) The binding's lifetime ending with the environment that held it, when the block scope is discarded
- ( ) Python's garbage collector running mid-loop

---

## 3. Exercises

1. *Interpreter surgery.* Replace your interpreter's flat dict with `Environment`, wiring `Let`, `Assign`, `Var`, and `Block` as above. Re-run last module's summation program (it must still work), then run the paper-machine program and confirm 51 and 2.
2. *Nested shadowing torture.* Write a three-level program (global, block, inner block) where the same name is bound at all three levels, and a fourth name is read from each level. Hand-draw the environment chain at the innermost print, then confirm by execution.
3. *Error message upgrade.* Make `NameError` messages include the variable name and the names visible in the current chain ("did you mean...?" optional). Show before and after on a typo program.
4. *Design decision.* Implement and document your team's answer to "do if and while bodies create scopes?", with one program whose output differs between the two choices as evidence that you tested it.

---

## Reflection Prompt

In your notebook: the environment chain makes "context" into an explicit, inspectable object: you can print the whole chain at any moment. Where in your own debugging (or your own thinking) would you benefit from being able to print the chain of contexts you are currently inside?

---

## 4. Further Reading

- Douglas Thain. *Introduction to Compilers and Language Design*, Chapter 7.
- Robert Nystrom. *Crafting Interpreters*, "Statements and State" and "Functions" (online): environments, then closures over them.
- Abelson and Sussman. *Structure and Interpretation of Computer Programs*, section 3.2, the environment model, beautifully drawn.
