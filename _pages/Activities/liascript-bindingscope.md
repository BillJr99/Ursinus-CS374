<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374-Fall2026/gh-pages/_pages/Activities/liascript-bindingscope.md or locally via https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374-Fall2026/gh-pages/_pages/Activities/liascript-bindingscope.md

import: https://raw.githubusercontent.com/liascript/CodeRunner/master/README.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

# Binding, Scope, and Environments

A program is full of names: `x`, `count`, `add`, `config`.  The language decides what each name means and where that meaning can be seen.  A binding attaches a name to a meaning.  A scope is the region of the program where that binding is visible.  Scope works like the rooms at a party: you can talk to people in your own room or in any outer room you walked through, but not to people in a room you never entered.  The analogy stops there, because a program's rooms are fixed by its text, not by where you happen to wander.  Once you know these rules, you can predict what a name means by reading the code instead of guessing.

A running program must then enforce those rules, answering one question over and over: what value does the name `x` hold right now?  An **environment** is the data structure that answers it.  An environment is a table that pairs each variable name with its current value.  One table is not enough.  A block or a function can declare its own `x` that hides the outer `x`, and that inner `x` must disappear when the block ends.  So each block gets its own environment, and each environment keeps a pointer to the environment that encloses it, called its parent.  Following those pointers outward is the parent chain.  Building and walking that chain is how your interpreter enforces every scope rule.

## Learning Goals

By the end of this activity, you will be able to:

- Classify a name's binding time (language design time, compile time, load time, or run time) and justify the classification for examples in Python and Java
- Distinguish static (lexical) scope from dynamic scope by tracing name resolution under each rule for a program with nested function calls
- Define binding, declaration, use, shadowing, and lifetime, and apply each term correctly to code examples
- Implement an `Environment` class as a chain of dictionaries linked by parent pointers, and explain why a flat dictionary cannot model nested scope
- Trace the four environment operations (`define`, `lookup`, `assign`, and scope entry/exit) on a program with nested blocks, and predict the value printed at each point in a program with shadowed names
- Wire the `Environment` class into a tree-walking interpreter so that block statements push and pop scopes correctly
- Specify the scoping and binding rules for a new language design, and defend the chosen rules in terms of predictability, flexibility, and implementation complexity

Your interpreter from *Tree-Walking Interpretation* stores every variable in one flat dictionary.  That design breaks as soon as two parts of a program use the same name for different things.  Today you build the vocabulary to fix it, **binding** (attaching a name to a meaning) and scope (where that attachment is visible), and then the data structure that enforces it.  The `Environment` class you build here is the one the Environments and Scope lab, handed out today, asks you to finish and test, and the one the Interpreter assignment imports unchanged.  The path for today runs from binding times, to static versus dynamic scope, to the environment chain, to the operations and blocks that use it, to lifetime and the design decisions for your own language.

> **Before You Begin:** This activity assumes you can:
> - Write and call Python functions, including nested (inner) functions
> - Explain what a variable assignment does in Python (it creates or updates a name-value association)
> - Read and write basic Python dictionaries and classes (including `__init__`, instance variables, and simple `while` loops)
> - Describe in general terms what a compiler or interpreter does when it meets a name in source code
>
> If any of these feel shaky, review them first.

---

## Directions and Group Roles

Work in your POGIL (Process Oriented Guided Inquiry Learning) team with your rotated roles (**Manager**, **Recorder**, **Presenter**, **Reflector**).  Please think each model and question through on your own first, then talk it over with your group.  The Recorder posts your answers to the Class Activity Questions discussion board, and the Presenter reports out wherever you disagreed or found another approach.  After class, please respond to the reflective prompt on your own in your notebook.

---

## Today's 75 Minutes

Rules first, then the machine that enforces them.  Parts I and II are the vocabulary; Parts III and IV are the `Environment` class your lab and your interpreter depend on; Part V is the one place where scope and lifetime come apart.

| Minutes | Segment | What your team does |
|---------|---------|---------------------|
| 0-5 | Roles and the flat-dictionary problem | Rotate roles; the Manager states, in one sentence, what goes wrong when a block reuses an outer variable's name in your current interpreter |
| 5-15 | Part I: Binding | Fill the Model 1 table, run its first cell, and answer CTQs 1-4 |
| 15-30 | Part II: Scope | Run both resolvers in Model 2, answer CTQs 5-8, and commit to a prediction for Probe 1 of the Mystery Scoping Language before running it |
| 30-45 | Part III: The Environment Chain | Run the paper machine by hand (CTQs 9-12), check it against the Model 3 code cell, and read the class (CTQs 13-15) |
| 45-62 | Part IV: Define, Assign, and Blocks | Run Model 5 and answer CTQs 16-18, then simulate per-iteration scope in Model 6 and answer CTQs 19-20 |
| 62-72 | Part V: Lifetime, and Your Language | Run `make_adder` and the loop-variable trap, and answer CTQs 23-25 |
| 72-75 | Wrap-up | The Recorder posts the team's answers; everyone opens the Environments and Scope lab and reads its Part 0 |

If the period runs short, the Try It Yourself blocks (other than Probe 1) and CTQs 21-22 move to homework.  Everything after **In-class work stops here** is self-paced: the exercises and four extensions covering Python's LEGB rule, the define-when-you-meant-assign bug, a three-level chain trace, and a step-by-step storage trace.  The last two are the closest rehearsal for the lab's paper trace.

---

# Part I: Binding

## 1.  When Does a Name Get Its Meaning?

A **binding** is an association between a name and an attribute, such as a value, a type, or a memory location.  The central question about a binding is when it happens.  That moment is its binding time.  The classical binding times, from earliest to latest, are: language design time (`+` means addition), compile time (a static type), load or startup time (a global's address), and run time (a variable's current value).  Earlier binding buys efficiency and checkability.  Later binding buys flexibility.  A language is, in large part, a schedule of binding times.

A declaration creates a binding.  In `let x = 5;`, the declaration binds `x`.  Every later mention of `x` is a use, and the language must resolve each use to some binding.  Scope rules decide which binding a use reaches.  When the same name is declared in nested regions, the inner declaration shadows the outer one: both bindings exist, but the inner one wins inside its own region.

---

This model puts the vocabulary above to work.  As you fill in the table, ask two questions about each fact: could the language have decided this earlier, and what would it gain or lose by doing so?  The earlier a binding happens, the more the language can check and optimize ahead of time.  The later it happens, the more the programmer can change at run time.

## Model 1: Binding Time Sort

| Fact | Bound when? |
|------|-------------|
| The meaning of the `*` symbol in your language | ? |
| The type of `count` in Java's `int count;` | ? |
| The type of `count` in Python after `count = 3` | ? |
| The value of `count` during a loop | ? |

Run this cell to watch Python bind types at run time:

```python
# Python binds types at runtime, not compile time
x = 42
print(f"x = {x!r}, type = {type(x).__name__}")

x = "now a string"   # rebind: Python allows type change
print(f"x = {x!r}, type = {type(x).__name__}")

x = [1, 2, 3]        # rebind again
print(f"x = {x!r}, type = {type(x).__name__}")

# Compare: in Java, `int x = 42; x = "hello";` is a COMPILE ERROR
# In Python, the name 'x' is bound to a NEW object each time
# The object's type is fixed; the binding is flexible

# id() shows the object's identity (address in CPython)
a = 100
b = a
print(f"\na is b? {a is b}  (same object: {id(a) == id(b)})")
a = 200   # rebind a to a new object; b still points to 100
print(f"After a = 200: a={a}, b={b}  (b unchanged)")
```
@LIA.eval(`["main.py"]`, `none`, `python3 main.py`)

### Reading the Code

- The three assignments to `x` never change an object.  Each one points the name `x` at a new object.  That is why `type(x)` changes while no integer ever turned into a string.
- The `a is b` probe tests identity, not equality.  Two names can hold equal values without naming the same object.  Here they name the same object until `a = 200` rebinds one of them.
- Nothing in this cell is about scope yet.  It is only about when the link between a name and an attribute is fixed.  Part II asks the same question in space (where) instead of in time (when).

### Try It Yourself

Find the binding time of each fact below by experiment, not by assertion.

```python
# For each probe: predict FIRST, in writing, then run.

print("=== 1. When is the meaning of '*' decided? ===")
print(f"  3 * 4       = {3 * 4}")
print(f"  'ab' * 3    = {'ab' * 3!r}")
print(f"  [1, 2] * 2  = {[1, 2] * 2}")
# TODO: '*' clearly does different things. Was that decided when Python was
#       designed, when this file was compiled, or when the line ran?
#       Add a probe that distinguishes your answer from the alternatives.

print("\n=== 2. When is a function's default argument bound? ===")
def append_to(item, target=[]):        # the classic
    target.append(item)
    return target

print(f"  append_to(1) -> {append_to(1)}")
print(f"  append_to(2) -> {append_to(2)}")
# TODO: explain the second line. At what moment was the empty list created,
#       and how many times? Name the binding time.

print("\n=== 3. When is a global's value bound? ===")
LIMIT = 10
def show_limit():
    print(f"  inside show_limit, LIMIT = {LIMIT}")
show_limit()
LIMIT = 99
show_limit()
# TODO: the function body never changed. Which binding time does this
#       demonstrate, and how would a compiled language differ?
```
@LIA.eval(`["main.py"]`, `none`, `python3 main.py`)

Expected output: probe 2 prints `[1]` and then `[1, 2]`, not `[1]` twice.  That surprise is a binding-time fact.  Naming it correctly is the exercise.

> **Watch out!**  A common mistake is to say "Python is dynamically typed, so Python has no binding times."  Every language has binding times.  Python moves the type binding from compile time to run time, and that is the only difference.  An object's type is fixed once the object exists.  What changes is which object the name points to.  When you run `x = 42` and then `x = "hello"`, Python does not turn the number `42` into a string.  It rebinds the name `x` to a different object.

### Critical Thinking Questions

1.  Complete the binding time table above.  Justify each answer in a clause.
2.  Java binds the type of `count` earlier than Python does.  Restate the static-versus-dynamic-typing debate from the language evaluation module as a binding-time decision: what does each choice buy, and what does each choice cost?
3.  Your project language must decide: may a variable hold a number and later a string?  State your team's provisional answer, and state it in binding-time terms.
4.  When Python executes `a = 200`, does it change the object that `100` refers to, or does it change what the name `a` refers to?  What does this imply about Python's mutation model?

---

# Part II: Scope

## 2.  Where Does a Binding Reach?

A scope rule says which binding a use of a name reaches.  Two rules matter.

Static (lexical) scope resolves names by the program's text.  A use of `x` refers to the declaration in the innermost region that textually encloses the use.  You can do this resolution by reading the code, without running it.  That is why it is called static, and it is the choice of almost every modern language.

Dynamic scope resolves names by the call history.  A use of `x` refers to the most recent declaration of `x` in the chain of active calls, whatever code made that declaration.  Early Lisps worked this way.  The behavior is sometimes convenient and often surprising, because a function's meaning depends on who called it.

The two rules disagree only about free variables.  A free variable is a name that a function uses but does not declare itself.  In the program below, `x` is free in `show`:

```
let x = 10;

function show() { print x; }

function demo() {
    let x = 99;
    show();
}

demo();
```

Static scope prints 10, because the `x` in `show` resolves to the global `x`, its textual surroundings.  Dynamic scope prints 99, because the `x` in `show` resolves to the `x` in `demo`, the most recent binding on the call chain.

Almost every language you will use is statically scoped.  So the interesting differences are no longer static versus dynamic.  They are about **what counts as a scope**.  Languages disagree about that more than you would expect, and each disagreement comes with its own signature bug.

| Language | What creates a scope | The signature surprise |
|---|---|---|
| **Python** | Functions, classes, modules, comprehensions.  **Not** `if`, `for`, or `while` | A name assigned *anywhere* in a function is local *everywhere* in it, including lines above the assignment |
| **C** | Every `{ ... }` block, plus a file-wide scope outside all functions | A `for` loop's index can shadow an outer variable of the same name, silently, for the length of the loop |
| **Java** | Every block, like C, but shadowing a local with a local is a **compile error** | A field and a local *may* share a name, and `this.x` versus `x` then decides which one you meant |
| **JavaScript** | `let` and `const` are block-scoped; `var` is **function**-scoped and hoisted | A `var` is readable before its declaration line, as `undefined`; a `let` throws instead, from its "temporal dead zone" |
| **Scheme** | `let`, `let*`, `letrec`, and lambda bodies | `let` binds all its names *simultaneously*, so a right-hand side cannot see its siblings; `let*` and `letrec` change exactly that |
| **Your language** | You decide, this term | Whatever you choose, write it down before you implement it |

Read the table as a menu, not as trivia.  The rightmost column lists the bugs that each design choice hands to its programmers.  By the end of the term you will have chosen one of these rows for your own language.


---

This model runs the same program under both rules so you can watch them disagree.  When `show()` looks up `x`, does it consult the text of the program (static) or the history of calls that led here (dynamic)?  Running both resolvers side by side makes the difference plain.

## Model 2: Be Both Resolvers

Python is statically scoped.  Verify it:

```python
# Static scope in action: Python resolves print(x) inside show() textually.

x = 10

def show():
    print("show sees x =", x)       # resolves to the GLOBAL x: textual nesting

def demo():
    x = 99                          # a NEW binding, shadowing locally
    show()                          # does NOT affect what show sees

demo()
print("after demo, global x =", x)

# Shadowing in nested regions:
def outer():
    y = "outer"
    def inner():
        y = "inner"                 # shadows outer's y inside inner only
        return y
    return inner(), y

print(outer())                      # ('inner', 'outer')
```
@LIA.eval(`["main.py"]`, `none`, `python3 main.py`)

> **Watch out!**  Students often confuse shadowing with assignment.  When `demo()` writes `x = 99`, it does not change the global `x`.  It creates a new local binding that happens to share the same name.  The global `x` still equals `10` after `demo()` returns.  Shadowing creates a second binding in an inner region.  Assignment updates a binding that already exists.  These are different operations with different effects on the enclosing scope.

Here is the step-by-step trace of name lookup under static scope for the `demo()` -> `show()` call above:

1. `demo()` is called.  Python creates a new local frame (a table of that call's local names) for `demo`.  It executes `x = 99`, which binds `x` to `99` in `demo`'s local frame only.
2. `show()` is called from inside `demo`.  Python creates a new local frame for `show`.  That frame has no `x`.
3. `show` uses `x` in `print(...)`.  Python walks the textual enclosing regions: first `show`'s own locals (no `x`), then the global module scope, where `x = 10` lives.  It finds `x = 10` there and uses it.
4.  Python never looks at `demo`'s frame when resolving `show`'s names, because `demo` does not textually enclose `show`.  Both functions are defined at the top level.  They are siblings in the text, not parent and child.
5.  After both calls return, the global `x` is still `10`.

Now simulate dynamic scope in Python:

```python
# Dynamic scope simulation using a stack
scope_stack = [{"x": 10}]   # global frame

def lookup_dynamic(name):
    # Walk the stack from top (most recent) to bottom (oldest)
    for frame in reversed(scope_stack):
        if name in frame:
            return frame[name]
    raise NameError(f"undefined: {name!r}")

def show_dynamic():
    print("show (dynamic) sees x =", lookup_dynamic("x"))

def demo_dynamic():
    scope_stack.append({"x": 99})   # push new frame
    show_dynamic()
    scope_stack.pop()               # pop frame

demo_dynamic()          # dynamic: show sees 99 (most recent x on stack)
show_dynamic()          # static simulation: show sees 10 (global)
```
@LIA.eval(`["main.py"]`, `none`, `python3 main.py`)

### Reading the Code

- `scope_stack` is a list used as a stack of frames.  `lookup_dynamic` walks it with `reversed(...)`, newest frame first.  That single line is dynamic scope.
- Compare it with how Python resolved the same program above.  Python walked the textual regions.  This code walks the call history.  Same program, same names, different answer, and the only difference is which chain you follow.
- `demo_dynamic` pushes a frame before the call and pops it after.  Forgetting the `pop()` is the classic dynamic-scope bug: the binding leaks into every function called afterwards.
- The second `show_dynamic()` prints 10.  Once the frame is popped, the 99 is gone.  That is the "time" half of the scope-versus-lifetime distinction that Part V makes.

### Try It Yourself: The Mystery Scoping Language

Below is an interpreter for a tiny language.  Its scoping rule is hidden inside `RULE`, which is set from a value you cannot read off the code.  Do not try to reason it out from the source.  Deduce it by experiment, the way you would probe a language whose implementation you did not have.

Write a program in the mini-language whose output differs depending on the rule.  Run it, and use the answer to identify `RULE`.  Then predict what your own interpreter's `Environment` will do with the same program.

```python
from dataclasses import dataclass
from typing import Any
import hashlib

# --- The mystery: one of "lexical" or "dynamic". No peeking. ----------------
RULE = hashlib.sha256(b"cs374").hexdigest()[0]
RULE = "lexical" if int(RULE, 16) % 2 == 0 else "dynamic"

@dataclass
class Num:  value: float
@dataclass
class Var:  name: str
@dataclass
class Add:  left: Any; right: Any
@dataclass
class Fun:  param: str; body: Any        # a one-argument function
@dataclass
class Call: fn: Any; arg: Any
@dataclass
class Let:  name: str; val: Any; body: Any

class Closure:
    def __init__(self, param, body, env):
        self.param, self.body, self.env = param, body, env

def interp(e, env, stack):
    if isinstance(e, Num):  return e.value
    if isinstance(e, Var):
        if RULE == "lexical":
            scope = env
        else:
            scope = {}                       # newest frame wins
            for frame in stack:
                scope.update(frame)
        if e.name not in scope:
            raise NameError(f"undefined: {e.name}")
        return scope[e.name]
    if isinstance(e, Add):
        return interp(e.left, env, stack) + interp(e.right, env, stack)
    if isinstance(e, Fun):
        return Closure(e.param, e.body, dict(env))
    if isinstance(e, Let):
        v = interp(e.val, env, stack)
        return interp(e.body, {**env, e.name: v}, stack + [{e.name: v}])
    if isinstance(e, Call):
        f = interp(e.fn, env, stack)
        a = interp(e.arg, env, stack)
        return interp(f.body, {**f.env, f.param: a}, stack + [{f.param: a}])
    raise ValueError(e)

def run(program, label):
    try:
        print(f"  {label:44} -> {interp(program, {}, [{}])}")
    except NameError as err:
        print(f"  {label:44} -> NameError: {err}")

# --- Probe 1: the classic. Does f see the x where it was DEFINED, or the
# --- x that happens to be in scope where it was CALLED?
#   let x = 10 in
#   let f = fun _ -> x in
#   let x = 99 in f(0)
probe1 = Let("x", Num(10),
         Let("f", Fun("_", Var("x")),
         Let("x", Num(99),
         Call(Var("f"), Num(0)))))
run(probe1, "let x=10; f=fun _ -> x; let x=99; f(0)")

# TODO 1: before running, predict BOTH answers. Which number means lexical?
#         Which means dynamic? Write it down, then run.

# TODO 2: write a SECOND probe that distinguishes the two rules a different
#         way, so you are not trusting a single experiment. A good one:
#         make the caller's binding the only one that exists, and see
#         whether the callee can reach it.

# TODO 3: state the rule you deduced, and say what your own interpreter's
#         Environment (with its parent chain) would print for probe1.

print(f"\n  ...and the answer, once you have committed: RULE = {RULE!r}")
```
@LIA.eval(`["main.py"]`, `none`, `python3 main.py`)

Expected output: one number for probe 1, and then the rule revealed on the last line.  The exercise is worthless if you read the last line first.  Cover it, predict, and only then run.

---

Under static scoping, the binding that a variable use refers to can be determined:

[( )] Only by running the program and inspecting the call stack
[(X)] By reading the program text and finding the innermost enclosing declaration
[( )] By checking which function was called most recently
[( )] By the order of declarations in the global region only

A function `f` uses a variable `config` that it does not declare.  Under **dynamic** scope, `config` resolves to:

[( )] The global `config` from when `f` was defined
[(X)] The most recent `config` on the call stack when `f` executes
[( )] An error, undefined variables are always errors
[( )] The `config` in `f`'s textual enclosing scope

### Critical Thinking Questions

5.  Trace the program under each rule.  Write out the chain each resolver follows (textual nesting versus call stack), and confirm the 10 versus 99 split.
6.  Argue each side in one sentence: what is convenient about dynamic scope (think of configuration that functions silently inherit), and what makes it hard to read?
7.  Which rule lets a compiler resolve every name before the program runs?  Connect your answer to the binding-time framework.
8.  Python is statically scoped.  Why can Python not implement dynamic scope without changing the language?

---

# Part III: The Environment Chain

Parts I and II gave you the rules.  Part III builds the data structure that enforces them: a chain of dictionaries linked by parent pointers.  Lookup walks outward through the chain, which is exactly what static scoping requires.

## 3.  One Dictionary Cannot Shadow

Right now your interpreter keeps every variable in one flat dictionary, `env = {}`.  That makes every variable global.  A block that declares `x` overwrites any outer `x` for good, and nothing goes away when the block ends.  The fix mirrors the nesting in the source text: one dictionary per scope, and each dictionary holds a pointer to its parent.  Entering a block creates a fresh child environment.  Leaving the block returns to the parent, and the child's bindings vanish with it.  When an inner binding hides an outer binding with the same name, we say the inner one shadows the outer one.

Lookup is the operation that finds the value of a name, and it walks the chain.  To resolve `x`, check the current environment first.  If `x` is not there, ask the parent.  Keep going until you reach the global environment.  Only past the root do you fail with a name error:

$$
\text{lookup}(x, E) = \begin{cases} E.\text{vars}[x] & x \in E.\text{vars} \\ \text{lookup}(x, E.\text{parent}) & \text{otherwise, if a parent exists} \\ \text{NameError} & \text{at the root} \end{cases}
$$

That walk is static scope in code: innermost first, then outward.

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

# Part IV: Define, Assign, and Blocks

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

# Part V: Lifetime, and Your Language

Scope tells you where in the code a name is visible.  Lifetime tells you how long in time the storage for a value persists.  The two usually travel together: a local variable exists only while its function runs.  Closures are the big exception.  When an inner function escapes its enclosing scope (by being returned or stored), it carries its enclosing bindings with it and keeps them alive indefinitely.  This section shows both the power of that mechanism and its classic pitfall.

## 5.  Scope Is Space; Lifetime Is Time

**Scope is the region of text where a binding is visible; lifetime is the span of execution during which its storage exists.**  The two usually line up: a local lives while its block runs.  But they can diverge.  A C `static` local has a tiny scope and a program-long lifetime.  And, in the divergence that matters most for your project, a closure keeps a binding alive after its scope has ended.

> **Watch out!**  C spends the single keyword `static` on two unrelated jobs, and which job you get depends only on where you write it.  Written inside a function, it changes lifetime: the variable survives from call to call, while its scope stays the same small block it always was.  Written at file scope, outside every function, it changes linkage: the lifetime was already the whole program, and what changes is whether other files can see the name at all.  One keyword, two axes.  If you read the linker extension of *Parsing Expressions and Table-Driven Parsing*, the file-scope version is the one that gives a name *internal linkage*: it still appears in the object file's symbol table, but with a local binding, so the linker never matches it against another file's uses.  That is C's main tool for making a name private to one file.


Closures keep bindings alive after their scope ends:

```python
def make_adder(n):
    # n's SCOPE: the body of make_adder
    # n's LIFETIME: as long as the returned closure exists!
    def adder(x):
        return x + n   # n is still alive, captured by closure
    return adder

add5 = make_adder(5)
add10 = make_adder(10)

# make_adder has returned; its scope is gone, but n lives on
print(add5(3))    # 8, n=5 is still alive
print(add10(3))   # 13, n=10 is still alive

# Python's closure mechanism: check what's captured
print(add5.__closure__[0].cell_contents)   # 5
print(add10.__closure__[0].cell_contents)  # 10
```
@LIA.eval(`["main.py"]`, `none`, `python3 main.py`)

> **Watch out!**  The loop variable trap catches nearly every Python programmer eventually.  When a `lambda` (or any closure) captures a name from an enclosing scope, it captures the name, not the value the name held when the closure was created.  By the time the loop finishes, `i` equals `4`, and every closure refers to that same `i`.  This is not a bug in Python.  It is the correct behavior of late binding.  It is also different from what most people intend.  The fix is to force value capture at creation time, either with a default argument (`i=i`) or with a factory function that creates a fresh scope.

The loop variable trap, scope versus lifetime:

```python
# Classic bug: all closures share the SAME variable
adders_broken = []
for i in range(5):
    adders_broken.append(lambda x: x + i)   # i is captured by reference

print("Broken:", [f(0) for f in adders_broken])  # [4,4,4,4,4], all see final i=4

# Fix 1: default argument captures VALUE at creation time
adders_fixed1 = []
for i in range(5):
    adders_fixed1.append(lambda x, i=i: x + i)

print("Fixed1:", [f(0) for f in adders_fixed1])   # [0,1,2,3,4]

# Fix 2: factory function creates a new scope each iteration
def make_adder(n):
    return lambda x: x + n

adders_fixed2 = [make_adder(i) for i in range(5)]
print("Fixed2:", [f(0) for f in adders_fixed2])   # [0,1,2,3,4]
```
@LIA.eval(`["main.py"]`, `none`, `python3 main.py`)

### Reading the Code

- `make_adder` returns and its frame disappears, yet `n` is still readable through the returned function.  Scope (where a name is visible) ended.  Lifetime (how long the value survives) did not.  Those are the two axes this Part is about.
- `__closure__` shows you the captured cells directly.  Everything the returned function can still reach is in there, and nothing else is.
- The late-binding loop bug is not a scoping bug.  Every lambda correctly refers to the same `i`.  The surprise is that the lifetime of `i` outlasts each iteration, so every lambda reads its final value.
- The two fixes attack the two different halves.  The default argument copies the value at creation time.  The factory function creates a fresh scope per iteration.  Knowing which one you reached for, and why, is the check that you have the distinction.

### Try It Yourself

Settle the scope-versus-lifetime question for the language you are building.

```python
def make_counter():
    count = 0
    def bump():
        nonlocal count
        count += 1
        return count
    return bump

c1, c2 = make_counter(), make_counter()
print("=== Two counters from the same factory ===")
print(f"  c1: {c1()}, {c1()}, {c1()}")
print(f"  c2: {c2()}")
# TODO 1: c2 restarted at 1. How many `count` variables exist right now,
#         and where does each one live? Neither is reachable by name from
#         out here, so what is keeping them alive?

print("\n=== The loop again, three ways ===")
late  = [lambda: i for i in range(3)]
early = [lambda i=i: i for i in range(3)]
# TODO 2: add a third list using a factory function, then print all three.
print(f"  late-bound : {[f() for f in late]}")
print(f"  default-arg: {[f() for f in early]}")

print("\n=== The decision for YOUR language ===")
# TODO 3: does a loop body in your language get a FRESH scope per iteration
#         (so closures capture different variables) or ONE scope for the
#         whole loop (so they share)? Write the one-sentence rule for
#         SEMANTICS.md, and name a language that made each choice.
```
@LIA.eval(`["main.py"]`, `none`, `python3 main.py`)

Expected output: `1, 2, 3` then `1`, and `[2, 2, 2]` against `[0, 1, 2]`.  The two counters do not interfere with each other.  That is the same mechanism as the two fixes to the loop bug, seen from the other side.

### Critical Thinking Questions

23.  In the loop variable trap, all five closures capture the same `i`.  Why?  What is the difference between capturing a name and capturing a value?
24.  The `i=i` default-argument trick works because Python evaluates default arguments once, at function definition.  This is a Python-specific workaround.  Describe how your project interpreter should handle the analogous case with proper closure semantics.
25.  A C `static` local variable has function scope but program lifetime.  Name one use case where this combination is deliberately useful (not a bug).

---

**In-class work stops here.**  Everything below is homework and going-deeper material.  Attempt the exercises before the Environments and Scope lab is due.

---

# Check Your Understanding

A name is bound to a type at compile time in Java and at run time in Python.  This difference is best described as:

[(X)] A binding-time decision, trading early checkability for later flexibility
[( )] Java having types and Python not having them
[( )] A scoping difference between the two languages
[( )] A difference in how long each language's values stay alive

---

In the Mystery Scoping Language probe, `f` is defined where `x` is 10 and called where `x` is 99.  Printing 99 tells you the language is:

[(X)] Dynamically scoped: names resolve against the call history
[( )] Lexically scoped: names resolve against the program text
[( )] Weakly typed
[( )] Using late binding of the function's body

---

Inside a Python function, writing `x = 1` anywhere makes `x` local for the whole function, including lines above the assignment.  That rule exists because:

[(X)] Python decides each name's scope once for the entire function body, before executing any of it
[( )] Python executes function bodies out of order
[( )] Assignment always creates a global unless declared otherwise
[( )] The interpreter cannot see the assignment until it runs

---

`static int n;` appears twice in a C program: once inside a function, once at file scope outside every function.  What do the two occurrences have in common?

[(X)] Only the spelling: inside a function it changes lifetime, at file scope it changes visibility to other files
[( )] Both make the variable read-only after initialization
[( )] Both give the variable program-long lifetime, which it would not otherwise have
[( )] Both restrict the variable to the block it is written in

---

`make_adder(5)` returns, and its frame is gone, but the returned function still reads `n`.  This shows that:

[(X)] Lifetime and scope are different: `n` is no longer *visible* by name, but its value is still *alive*
[( )] Python leaks memory when functions return
[( )] `n` was actually a global all along
[( )] The returned function re-runs `make_adder` on each call

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

# Exercises

1.  *Scope archaeology.*  Run a three-level nested function experiment in Python (global, enclosing, and local each binding `v`).  Report which binding each level's `print` resolves to.  Then state Python's resolution order (LEGB) in your own words.
2.  *Design memo.*  Write your project language's scoping rules in five sentences or fewer: static or dynamic; whether blocks create scopes; whether shadowing is legal; what happens on use of an undeclared name; whether loop bodies create a scope.  Add it to `SEMANTICS.md`.
3.  *Bug forensics.*  Construct a program where shadowing causes a quiet wrong answer rather than an error.  Propose one language rule that would catch it, and say what that rule costs.
4.  *Closure inspector.*  Write a Python function that takes any closure (a function whose `__closure__` is not None) and prints a table of each captured name and its current value.  Test it on `make_adder(7)` and on a counter closure.
5.  *Interpreter surgery.*  Replace your interpreter's flat dict with `Environment`, wiring `Let`, `Assign`, `Var`, and `Block` as Section 4 describes.  Re-run last module's summation program (it must still work).  Then run the paper-machine program and confirm 51 and 2.
6.  *Nested shadowing torture.*  Write a three-level program (global, block, inner block) where the same name is bound at all three levels and a fourth name is read from each level.  Hand-draw the environment chain at the innermost print, then confirm by execution.
7.  *Error message upgrade.*  Upgrade the `NameError` messages to also list the names visible in the entire chain ("undefined variable 'pritnValue'; did you mean one of: printValue, x, n, total?").  Do this with a `suggestions()` helper in `lookup` that collects visible names by walking the chain.  Show a before-and-after transcript on a plausible typo.
8.  *Design decision: if/while scope.*  Do `if` and `while` bodies create fresh child environments, or do they execute in the enclosing environment?  Implement both behaviors behind a flag (`body_creates_scope: bool`).  Write one program whose output differs between the two choices.  Document your team's decision in `SEMANTICS.md`, with that program as the evidence.
9.  *Instrumented environment.*  Add a `lookup_count` counter to `Environment` that accumulates across the chain and resets at each top-level `execute` call; print it after the Model 9 trace program.  Then make `lookup` cache the most recent successful lookup per name, and benchmark (`time.perf_counter`) the speedup on a tight loop that reads the same variable 10,000 times.

---

## Reflection Prompt

In your notebook, answer two prompts.  First: shadowing lets inner code reuse a name without consulting outer code.  That is both modularity and a trap.  When you reuse a word with a private meaning in your own notes or conversation, what keeps you from confusing yourself, and is there a language-design lesson in your answer?  Now that you understand the loop-variable trap, how will it change the way you write closures in production Python code?  Second: the environment chain makes "context" an explicit object you can inspect.  You can print the whole chain at any moment.  Where in your own debugging or thinking would it help to print the chain of contexts you are currently inside?

---

## 6.  Further Reading

- Douglas Thain.  *Introduction to Compilers and Language Design*, Chapter 7.
- Robert Nystrom.  *Crafting Interpreters*, "Statements and State," "Functions," and "Closures" (online): environments, then closures over them.
- Robert Sebesta.  *Concepts of Programming Languages*, the names/binding/scope chapter (any edition).
- Abelson and Sussman.  *Structure and Interpretation of Computer Programs*, section 3.2, the environment model, beautifully drawn.
- Python docs: [Execution model: naming and binding](https://docs.python.org/3/reference/executionmodel.html)

---

# Extension: Python's LEGB Rule (self-paced)

> Past the 75 minutes.  Nothing in class assumes it.  Read it before you write Python closures that assign to an enclosing variable, and before Exercise 1.

Python does more than distinguish "local" from "global."  It has four scope layers, and it searches them in a fixed order.  This model traces that order and shows the single most common Python scope bug: assigning to a name anywhere inside a function makes Python treat that name as local throughout the entire function, even on lines before the assignment.  This behavior is surprising at first, and completely consistent once you know the rule.

## Model 7: Python's LEGB Rule

Python resolves names in this order: **L**ocal -> **E**nclosing -> **G**lobal -> **B**uilt-in.

```python
# LEGB Rule in action
x = "global"              # G: global scope

def outer():
    x = "enclosing"       # E: enclosing scope

    def inner():
        x = "local"       # L: local scope
        print("inner sees:", x)     # L wins

    def inner_no_local():
        print("inner_no_local:", x) # E wins (no local x)

    def inner_global():
        global x
        print("inner_global:", x)   # G (via global keyword)

    inner()
    inner_no_local()
    inner_global()

outer()
print("global x:", x)

# Built-in scope: len, print, range live there
print(f"Built-in 'len' found: {type(len)}")
import builtins
print(f"All built-ins: {len(dir(builtins))} names")
```
@LIA.eval(`["main.py"]`, `none`, `python3 main.py`)

> **Watch out!**  Python scopes are function-level, not block-level.  In Java or C, a variable declared inside an `if` block or `for` loop is local to that block.  In Python, `if` blocks and `for` loops do not create a new scope.  A variable introduced inside them belongs to the enclosing function (or module).  So a variable first assigned inside an `if` body is accessible throughout the rest of the function.  This surprises programmers coming from Java or C.  It also means Python's `global` keyword is nothing like C's storage classes.  Python's `global` is a declaration inside a function that says "when I write this name, find it in the module scope, not here."

The `nonlocal` keyword fixes the counter bug:

```python
# Classic bug: cannot assign to enclosing scope without 'nonlocal'
def make_counter_broken():
    count = 0
    def inc():
        count = count + 1   # UnboundLocalError! Python sees count as local
        return count
    return inc

def make_counter_fixed():
    count = 0
    def inc():
        nonlocal count      # tells Python: count is in the ENCLOSING scope
        count = count + 1
        return count
    return inc

try:
    c = make_counter_broken()
    print(c())
except UnboundLocalError as e:
    print(f"Broken counter: {e}")

c = make_counter_fixed()
print(c(), c(), c())        # 1 2 3
```
@LIA.eval(`["main.py"]`, `none`, `python3 main.py`)

### Critical Thinking Questions

26.  In `make_counter_broken`, why does Python raise `UnboundLocalError`?  What rule does Python apply when it sees an assignment inside a function?
27.  The `nonlocal` keyword names the enclosing scope explicitly.  Why might language designers prefer `nonlocal` (explicit) over always allowing silent mutation of the enclosing scope?
28.  Scheme uses `set!` to mutate a binding and `define` to create one.  How would you design your interpreter to distinguish "create a new binding" from "update an existing binding"?

---

# Extension: Define When You Meant Assign (self-paced)

> Past the 75 minutes.  Nothing in class assumes it.  Read it the first time a loop in your interpreter never terminates.

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

> Past the 75 minutes.  Nothing in class assumes it.  It is the closest rehearsal for the lab's paper trace.

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

> Past the 75 minutes.  Nothing in class assumes it.  Work it before you wire the `Environment` class into your interpreter.

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

Up next: the *Type Systems* activity asks what your interpreter should do with senseless values.  The `Environment` you built here goes into the Environments and Scope lab, due at that session, and from there straight into the Interpreter assignment.
