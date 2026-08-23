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

Every program you write is a web of names (`x`, `count`, `add`, `config`) and the language decides, sometimes before you even run the code, what each name means and where that meaning is visible. Scope is like the visibility rules at a party: you can only introduce yourself to people in the same room or outer rooms, not rooms you haven't entered yet. Understanding these rules is what separates a programmer who debugs by intuition from one who reasons about their code with confidence.

## Learning Goals

By the end of this activity, you will be able to:

- Classify a name's binding time (language-design time, compile time, load time, or run time) and justify the classification for examples in Python and Java
- Distinguish static (lexical) scope from dynamic scope by tracing name resolution under each rule for a program with nested function calls
- Define the concepts of binding, declaration, use, shadowing, and lifetime, and apply each term correctly to code examples
- Analyze the trade-offs of static versus dynamic typing as a binding-time decision, articulating what each buys and what each costs
- Specify the scoping and binding rules for a new language design, defending the chosen rules in terms of predictability, flexibility, and implementation complexity

Your interpreter from *Tree-Walking Interpretation* currently stores every variable in one flat dictionary, and that simplicity is about to fail you: what happens when two parts of a program use the same name? Today we develop the vocabulary of **binding** (attaching a name to a meaning) and **scope** (where that attachment is visible), the semantics decisions at the heart of your interpreter assignment. The arc: **binding times $\rightarrow$ static versus dynamic scope $\rightarrow$ lifetime $\rightarrow$ design decisions for your language**.

> **Before You Begin:** This activity assumes you can:
> - Write and call Python functions, including nested (inner) functions
> - Explain what a variable assignment does in Python (creates or updates a name-value association)
> - Describe in general terms what a compiler or interpreter does when it encounters a name in source code
>
> If any of these feel shaky, review them first.

---

## Directions and Group Roles

Work in your POGIL team with rotated roles (**Manager**, **Recorder**, **Presenter**, **Reflector**). Consider each model and question individually first, then discuss with your group. The Recorder posts answers to the Class Activity Questions discussion board; the Presenter reports out areas of disagreement or alternative approaches. After class, respond to the reflective prompt individually in your notebook.

---

# Part I: Binding

## 1. When Does a Name Get Its Meaning?

**A binding is an association between a name and an attribute** (a value, a type, a memory location), and the central question is *when* it happens. The classical **binding times**, from earliest to latest: language design time (`+` means addition), compile time (a static type), load or startup time (a global's address), and run time (a variable's current value). Earlier binding buys efficiency and checkability; later binding buys flexibility. A language is, in large part, a schedule of binding times.

**Declarations create bindings; scope rules govern their reach.** In `let x = 5;`, the declaration binds `x`; every later mention of `x` is a *use* that must be **resolved** to some binding. When the same name is declared in nested regions, the inner declaration **shadows** the outer: both bindings exist, but the inner one wins within its region.

---

This model establishes the central vocabulary: a **binding** is the attachment of a name to some attribute (a value, a type, a memory address), and the moment that attachment is made is the **binding time**. The earlier a binding is made, the more the language can check and optimize ahead of time; the later it is made, the more flexibility the programmer has at runtime. As you work through the table, ask yourself: could the language have determined this earlier, and what would it gain or lose by doing so?

## Model 1: Binding Time Sort

| Fact | Bound when? |
|------|-------------|
| The meaning of the `*` symbol in your language | ? |
| The type of `count` in Java's `int count;` | ? |
| The type of `count` in Python after `count = 3` | ? |
| The value of `count` during a loop | ? |

**Explore Python's binding times interactively:**

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
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

> **Watch out!** A common mistake is to say "Python is dynamically typed, so Python has no binding times." Every language has binding times; Python just moves the *type* binding from compile time to run time. The object's type is fixed once created; what changes is which object the name points to. When you run `x = 42` and then `x = "hello"`, Python is not changing the number `42` into a string; it is re-binding the name `x` to a completely different object.

### Critical Thinking Questions

1. Complete the binding time table above, justifying each answer in a clause.
2. Java binds `count`'s type earlier than Python does. Restate the static-versus-dynamic-typing debate from the language evaluation module as a *binding time* decision: what is bought and what is paid at each time?
3. Your project language must decide: may a variable be assigned a number and later a string? State your team's provisional answer and the binding-time language for it.
4. When Python executes `a = 200`, does it change the object `100` refers to, or does it change what name `a` refers to? What does this imply about Python's mutation model?

---

# Part II: Scope

## 2. Where Does a Binding Reach?

**Static (lexical) scope: resolve names by the program's text.** A use of `x` refers to the declaration in the innermost *textually enclosing* region. The resolution can be done by reading the code, without running it, which is why it is called static, and it is the choice of essentially every modern language.

**Dynamic scope: resolve names by the call history.** A use of `x` refers to the most recent declaration *in the chain of active calls*, whatever code that was. Early Lisps worked this way; the behavior is occasionally convenient and chronically surprising, because a function's meaning depends on who called it.

Consider this program in a language with functions:

```
let x = 10;

function show() { print x; }

function demo() {
    let x = 99;
    show();
}

demo();
```

**Static scope prints 10** (`show`'s `x` resolves to the global, its textual surroundings); **dynamic scope prints 99** (`show`'s `x` resolves to `demo`'s, the most recent on the call chain).

---

This model makes the static-versus-dynamic distinction concrete by showing the same program behaving differently under each rule. The key question is: when `show()` looks up `x`, does it consult the text of the program (static) or the history of calls that led here (dynamic)? Running both resolvers side by side will make the difference unmistakable.

## Model 2: Be Both Resolvers

**Python is statically scoped. Verify it:**

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
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

> **Watch out!** Students often confuse **shadowing** with **assignment**. When `demo()` writes `x = 99`, it does *not* change the global `x`; it creates a brand-new local binding that happens to share the same name. The global `x` still equals `10` after `demo()` returns. Shadowing is about creating a second binding in an inner region; assignment is about updating an existing binding. These are completely different operations with completely different effects on the enclosing scope.

**Step-by-step trace of name lookup under static scope** (for the `demo()` -> `show()` call above):

1. `demo()` is called. Python creates a new local frame for `demo`. It executes `x = 99`, binding `x` to `99` **in `demo`'s local frame only**.
2. `show()` is called from inside `demo`. Python creates a new local frame for `show`. It has no local `x`.
3. `show` uses `x` in `print(...)`. Python walks **textual** enclosing regions: first `show`'s own locals (no `x`), then the **global module scope** (where `x = 10` lives). It finds `x = 10` there and uses it.
4. Python never looks at `demo`'s frame when resolving `show`'s names; `demo` is not a textual enclosing region of `show`. Both `show` and `demo` are defined at the top level; they are siblings, not parent and child in the text.
5. After both calls return, the global `x` is still `10`, untouched.

**Simulate dynamic scope in Python:**

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
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

Under static scoping, the binding that a variable use refers to can be determined:

[( )] Only by running the program and inspecting the call stack
[(X)] By reading the program text and finding the innermost enclosing declaration
[( )] By checking which function was called most recently
[( )] By the order of declarations in the global region only

A function `f` uses a variable `config` that it does not declare. Under **dynamic** scope, `config` resolves to:

[( )] The global `config` from when `f` was defined
[(X)] The most recent `config` on the call stack when `f` executes
[( )] An error, undefined variables are always errors
[( )] The `config` in `f`'s textual enclosing scope

### Critical Thinking Questions

4. Trace the program under each rule, writing the chain each resolver follows (textual nesting versus call stack). Confirm the 10 versus 99 split.
5. Argue each side in one sentence: what is genuinely convenient about dynamic scope (think: configuration that functions silently inherit), and what makes it hard to read?
6. Which rule lets a compiler resolve every name before the program runs? Connect to the binding-time framework.
7. Python is statically scoped. Why can Python not implement dynamic scope *without* changing the language?

---

Python does not merely distinguish "local" from "global"; it has four distinct scope layers that are searched in a fixed order. This model traces that order and surfaces the single most common Python scope bug: assigning to a name inside a function makes Python treat that name as local *throughout the entire function*, even lines before the assignment. This behavior is surprising, but completely consistent once you understand the rule.

## Model 3: Python's LEGB Rule

Python resolves names in order: **L**ocal -> **E**nclosing -> **G**lobal -> **B**uilt-in.

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
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

> **Watch out!** Python scopes are **function-level**, not block-level. In Java or C, a variable declared inside an `if` block or `for` loop is local to that block. In Python, `if` blocks and `for` loops do **not** create a new scope: a variable introduced inside them belongs to the enclosing function (or module). So a variable first assigned inside an `if` body is accessible throughout the rest of the function. This surprises programmers coming from Java or C, and it means Python's `global` keyword is nothing like C's `global` storage class: Python's `global` is a declaration inside a function saying "when I write this name, go find it in the module scope, not here."

**The `nonlocal` keyword, fixing the counter bug:**

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
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

### Critical Thinking Questions

8. In `make_counter_broken`, why does Python raise `UnboundLocalError`? What rule does Python apply when it sees an assignment inside a function?
9. The `nonlocal` keyword explicitly names the enclosing scope. Why might language designers prefer `nonlocal` (explicit) over always allowing silent enclosing-scope mutation?
10. Scheme uses `set!` to mutate a binding and `define` to create one. How would you design your interpreter to distinguish "create new binding" from "update existing binding"?

---

# Part III: Lifetime, and Your Language

Scope tells you *where in the code* a name is visible; lifetime tells you *how long in time* the storage for a value persists. These two concepts usually travel together (a local variable exists only while its function runs), but closures are a dramatic exception. When an inner function escapes its enclosing scope (by being returned or stored), it carries its enclosing bindings with it, keeping them alive indefinitely. This section shows both the power and the classic pitfall of that mechanism.

## 3. Scope Is Space; Lifetime Is Time

**Scope is the region of *text* where a binding is visible; lifetime is the span of *execution* during which its storage exists.** The two usually align (a local lives while its block runs) but can diverge: a C `static` local has tiny scope and program-long lifetime, and, the divergence that matters most for your project, a **closure** keeps a binding *alive* after its scope has ended.

**Lifetime divergence, closures keep bindings alive:**

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
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

> **Watch out!** The loop variable trap catches nearly every Python programmer eventually. When a `lambda` (or any closure) captures a name from an enclosing scope, it captures the **name**, not the value the name held at the moment the closure was created. By the time the loop finishes, `i` equals `4`, and every closure refers to that same `i`. This is not a bug in Python (it is the correct behavior of late binding) but it is different from what most people intend. The fix is to force **value capture** at creation time, either via a default argument (`i=i`) or a factory function that creates a fresh scope.

**The loop variable trap, scope vs lifetime:**

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
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

### Critical Thinking Questions

11. In the loop variable trap, all five closures capture the same `i`. Why? What is the difference between capturing a *name* and capturing a *value*?
12. The `i=i` default-argument trick works because default arguments are evaluated *once* at function definition. This is a Python-specific workaround; describe how your project interpreter should handle the analogous case with proper closure semantics.
13. A C `static` local variable has function scope but program lifetime. Name one use case where this combination is deliberately useful (not a bug).

---

## 4. Exercises

1. *Scope archaeology.* Run a three-level nested function experiment in Python (global, enclosing, local all binding `v`) and report which binding each level's `print` resolves to. Then state Python's resolution order (LEGB) in your own words.
2. *Design memo.* Write your project language's scoping rules in five sentences or fewer: static or dynamic; do blocks create scopes; is shadowing legal; what happens on use of an undeclared name; do loop bodies create a scope. Add it to `SEMANTICS.md`.
3. *Bug forensics.* Construct a program where shadowing causes a quiet wrong answer rather than an error. Propose one language rule that would catch it, and what that rule costs.
4. *Nonlocal simulator.* Implement a `ScopeChain` class with `define(name, val)`, `lookup(name)`, and `assign(name, val)` methods where `assign` walks the chain to find the existing binding (like `nonlocal`) rather than creating a new one in the current scope. Show it corrects the counter bug.
5. *Closure inspector.* Write a Python function that takes any closure (a function with `__closure__` not None) and prints a table of each captured name and its current value. Test it on `make_adder(7)` and on a counter closure.

---

## Reflection Prompt

In your notebook: shadowing lets inner code reuse a name without consulting outer code, which is both modularity and a trap. When you reuse a word with a private meaning in your own notes or conversation, what keeps you from confusing yourself, and is there a language-design lesson in your answer? Now that you understand the loop-variable trap, how does it change how you'll write closures in production Python code?

---

## 5. Further Reading

- Douglas Thain. *Introduction to Compilers and Language Design*, Chapter 7.
- Robert Nystrom. *Crafting Interpreters*, "Statements and State" and "Closures" (online).
- Robert Sebesta. *Concepts of Programming Languages*, the names/binding/scope chapter (any edition).
- Python docs: [Execution model: naming and binding](https://docs.python.org/3/reference/executionmodel.html)

Name-resolution mechanics continue hands-on in the *Environments and Variable Storage* activity. Together they are the scaffolding of the Interpreter assignment.
