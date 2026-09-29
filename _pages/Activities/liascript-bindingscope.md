<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374-Fall2026/gh-pages/_pages/Activities/liascript-bindingscope.md or locally via https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374-Fall2026/gh-pages/_pages/Activities/liascript-bindingscope.md

import: https://raw.githubusercontent.com/liascript/CodeRunner/master/README.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

# Names, Binding, and Scope

A program is full of names: `x`, `count`, `add`, `config`.  The language decides what each name means and where that meaning can be seen.  A binding attaches a name to a meaning.  A scope is the region of the program where that binding is visible.  Scope works like the rooms at a party: you can talk to people in your own room or in any outer room you walked through, but not to people in a room you never entered.  The analogy stops there, because a program's rooms are fixed by its text, not by where you happen to wander.  Once you know these rules, you can predict what a name means by reading the code instead of guessing.

## Learning Goals

By the end of this activity, you will be able to:

- Classify a name's binding time (language design time, compile time, load time, or run time) and justify the classification for examples in Python and Java
- Distinguish static (lexical) scope from dynamic scope by tracing name resolution under each rule for a program with nested function calls
- Define binding, declaration, use, shadowing, and lifetime, and apply each term correctly to code examples
- Analyze static versus dynamic typing as a binding-time decision, stating what each buys and what each costs
- Specify the scoping and binding rules for a new language design, and defend the chosen rules in terms of predictability, flexibility, and implementation complexity

Your interpreter from *Tree-Walking Interpretation* stores every variable in one flat dictionary.  That design breaks as soon as two parts of a program use the same name for different things.  Today you build the vocabulary to fix it: **binding** (attaching a name to a meaning) and scope (where that attachment is visible).  These are the semantics decisions at the center of your interpreter assignment.  The path for today runs from binding times, to static versus dynamic scope, to lifetime, to the design decisions for your own language.

> **Before You Begin:** This activity assumes you can:
> - Write and call Python functions, including nested (inner) functions
> - Explain what a variable assignment does in Python (it creates or updates a name-value association)
> - Describe in general terms what a compiler or interpreter does when it meets a name in source code
>
> If any of these feel shaky, review them first.

---

## Directions and Group Roles

Work in your POGIL team with your rotated roles (**Manager**, **Recorder**, **Presenter**, **Reflector**).  Please think each model and question through on your own first, then talk it over with your group.  The Recorder posts your answers to the Class Activity Questions discussion board, and the Presenter reports out wherever you disagreed or found another approach.  After class, please respond to the reflective prompt on your own in your notebook.

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

1. `demo()` is called.  Python creates a new local frame for `demo`.  It executes `x = 99`, which binds `x` to `99` in `demo`'s local frame only.
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
- The second `show_dynamic()` prints 10.  Once the frame is popped, the 99 is gone.  That is the "time" half of the scope-versus-lifetime distinction that Part III makes.

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

4.  Trace the program under each rule.  Write out the chain each resolver follows (textual nesting versus call stack), and confirm the 10 versus 99 split.
5.  Argue each side in one sentence: what is convenient about dynamic scope (think of configuration that functions silently inherit), and what makes it hard to read?
6.  Which rule lets a compiler resolve every name before the program runs?  Connect your answer to the binding-time framework.
7.  Python is statically scoped.  Why can Python not implement dynamic scope without changing the language?

---

Python does more than distinguish "local" from "global."  It has four scope layers, and it searches them in a fixed order.  This model traces that order and shows the single most common Python scope bug: assigning to a name anywhere inside a function makes Python treat that name as local throughout the entire function, even on lines before the assignment.  This behavior is surprising at first, and completely consistent once you know the rule.

## Model 3: Python's LEGB Rule

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

8.  In `make_counter_broken`, why does Python raise `UnboundLocalError`?  What rule does Python apply when it sees an assignment inside a function?
9.  The `nonlocal` keyword names the enclosing scope explicitly.  Why might language designers prefer `nonlocal` (explicit) over always allowing silent mutation of the enclosing scope?
10.  Scheme uses `set!` to mutate a binding and `define` to create one.  How would you design your interpreter to distinguish "create a new binding" from "update an existing binding"?

---

# Part III: Lifetime, and Your Language

Scope tells you where in the code a name is visible.  Lifetime tells you how long in time the storage for a value persists.  The two usually travel together: a local variable exists only while its function runs.  Closures are the big exception.  When an inner function escapes its enclosing scope (by being returned or stored), it carries its enclosing bindings with it and keeps them alive indefinitely.  This section shows both the power of that mechanism and its classic pitfall.

## 3.  Scope Is Space; Lifetime Is Time

**Scope is the region of text where a binding is visible; lifetime is the span of execution during which its storage exists.**  The two usually line up: a local lives while its block runs.  But they can diverge.  A C `static` local has a tiny scope and a program-long lifetime.  And, in the divergence that matters most for your project, a closure keeps a binding alive after its scope has ended.

> **Watch out!**  C spends the single keyword `static` on two unrelated jobs, and which job you get depends only on where you write it.  Written inside a function, it changes lifetime: the variable survives from call to call, while its scope stays the same small block it always was.  Written at file scope, outside every function, it changes linkage: the lifetime was already the whole program, and what changes is whether other files can see the name at all.  One keyword, two axes.  If you met the linker in *Table-Driven and LR Parsing*, the file-scope version is the one that keeps a name out of the symbol table entirely.  That is C's only way to make something private.


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

11.  In the loop variable trap, all five closures capture the same `i`.  Why?  What is the difference between capturing a name and capturing a value?
12.  The `i=i` default-argument trick works because Python evaluates default arguments once, at function definition.  This is a Python-specific workaround.  Describe how your project interpreter should handle the analogous case with proper closure semantics.
13.  A C `static` local variable has function scope but program lifetime.  Name one use case where this combination is deliberately useful (not a bug).

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

# Exercises

1.  *Scope archaeology.*  Run a three-level nested function experiment in Python (global, enclosing, and local each binding `v`).  Report which binding each level's `print` resolves to.  Then state Python's resolution order (LEGB) in your own words.
2.  *Design memo.*  Write your project language's scoping rules in five sentences or fewer: static or dynamic; whether blocks create scopes; whether shadowing is legal; what happens on use of an undeclared name; whether loop bodies create a scope.  Add it to `SEMANTICS.md`.
3.  *Bug forensics.*  Construct a program where shadowing causes a quiet wrong answer rather than an error.  Propose one language rule that would catch it, and say what that rule costs.
4.  *Nonlocal simulator.*  Implement a `ScopeChain` class with `define(name, val)`, `lookup(name)`, and `assign(name, val)` methods.  `assign` walks the chain to find the existing binding (like `nonlocal`) rather than creating a new one in the current scope.  Show that it corrects the counter bug.
5.  *Closure inspector.*  Write a Python function that takes any closure (a function whose `__closure__` is not None) and prints a table of each captured name and its current value.  Test it on `make_adder(7)` and on a counter closure.

---

## Reflection Prompt

In your notebook: shadowing lets inner code reuse a name without consulting outer code.  That is both modularity and a trap.  When you reuse a word with a private meaning in your own notes or conversation, what keeps you from confusing yourself, and is there a language-design lesson in your answer?  Now that you understand the loop-variable trap, how will it change the way you write closures in production Python code?

---

## 5.  Further Reading

- Douglas Thain.  *Introduction to Compilers and Language Design*, Chapter 7.
- Robert Nystrom.  *Crafting Interpreters*, "Statements and State" and "Closures" (online).
- Robert Sebesta.  *Concepts of Programming Languages*, the names/binding/scope chapter (any edition).
- Python docs: [Execution model: naming and binding](https://docs.python.org/3/reference/executionmodel.html)

Name-resolution mechanics continue hands-on in the *Environments and Variable Storage* activity.  Together they are the scaffolding of the Interpreter assignment.
