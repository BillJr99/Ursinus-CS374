<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://github.com/BillJr99/Ursinus-CS374-Fall2026/blob/gh-pages/_pages/Activities/liascript-bindingscope.md or locally via https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374/gh-pages/_pages/Activities/liascript-bindingscope.md

import: https://raw.githubusercontent.com/liascript/CodeRunner/master/README.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

# Names, Binding, and Scope

Every program you write is a web of names — `x`, `count`, `add`, `config` — and the language decides, sometimes before you even run the code, what each name means and where that meaning is visible. Scope is like the visibility rules at a party: you can only introduce yourself to people in the same room or outer rooms, not rooms you haven't entered yet. Understanding these rules is what separates a programmer who debugs by intuition from one who reasons about their code with confidence.

## Learning Goals

By the end of this activity, you will be able to:

- Classify a name's binding time (language-design time, compile time, load time, or run time) and justify the classification for examples in Python and Java
- Distinguish static (lexical) scope from dynamic scope by tracing name resolution under each rule for a program with nested function calls
- Define the concepts of binding, declaration, use, shadowing, and lifetime, and apply each term correctly to code examples
- Analyze the trade-offs of static versus dynamic typing as a binding-time decision, articulating what each buys and what each costs
- Specify the scoping and binding rules for a new language design, defending the chosen rules in terms of predictability, flexibility, and implementation complexity

Your interpreter currently stores every variable in one flat dictionary, and that simplicity is about to fail you: what happens when two parts of a program use the same name? Today we develop the vocabulary of **binding** (attaching a name to a meaning) and **scope** (where that attachment is visible), the semantics decisions at the heart of your interpreter assignment. The arc: **binding times $\rightarrow$ static versus dynamic scope $\rightarrow$ lifetime $\rightarrow$ design decisions for your language**.

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

This model establishes the central vocabulary: a **binding** is the attachment of a name to some attribute (a value, a type, a memory address), and the moment that attachment is made is the **binding time**. The earlier a binding is made, the more the language can check and optimize ahead of time; the later it is made, the more flexibility the programmer has at runtime. As you work through the table, ask yourself: could the language have determined this earlier — and what would it gain or lose by doing so?

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

> **Watch out!** A common mistake is to say "Python is dynamically typed, so Python has no binding times." Every language has binding times — Python just moves the *type* binding from compile time to run time. The object's type is fixed once created; what changes is which object the name points to. When you run `x = 42` and then `x = "hello"`, Python is not changing the number `42` into a string — it is re-binding the name `x` to a completely different object.

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

**Python is statically scoped — verify it:**
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

> **Watch out!** Students often confuse **shadowing** with **assignment**. When `demo()` writes `x = 99`, it does *not* change the global `x` — it creates a brand-new local binding that happens to share the same name. The global `x` still equals `10` after `demo()` returns. Shadowing is about creating a second binding in an inner region; assignment is about updating an existing binding. These are completely different operations with completely different effects on the enclosing scope.

**Step-by-step trace of name lookup under static scope** (for the `demo()` → `show()` call above):

1. `demo()` is called. Python creates a new local frame for `demo`. It executes `x = 99`, binding `x` to `99` **in `demo`'s local frame only**.
2. `show()` is called from inside `demo`. Python creates a new local frame for `show`. It has no local `x`.
3. `show` uses `x` in `print(...)`. Python walks **textual** enclosing regions: first `show`'s own locals (no `x`), then the **global module scope** (where `x = 10` lives). It finds `x = 10` there and uses it.
4. Python never looks at `demo`'s frame when resolving `show`'s names — `demo` is not a textual enclosing region of `show`. Both `show` and `demo` are defined at the top level; they are siblings, not parent and child in the text.
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

[[MC]]
Under static scoping, the binding that a variable use refers to can be determined:
- ( ) Only by running the program and inspecting the call stack
- (x) By reading the program text and finding the innermost enclosing declaration
- ( ) By checking which function was called most recently
- ( ) By the order of declarations in the global region only

[[MC]]
A function `f` uses a variable `config` that it does not declare. Under **dynamic** scope, `config` resolves to:
- ( ) The global `config` from when `f` was defined
- (x) The most recent `config` on the call stack when `f` executes
- ( ) An error — undefined variables are always errors
- ( ) The `config` in `f`'s textual enclosing scope

### Critical Thinking Questions

4. Trace the program under each rule, writing the chain each resolver follows (textual nesting versus call stack). Confirm the 10 versus 99 split.
5. Argue each side in one sentence: what is genuinely convenient about dynamic scope (think: configuration that functions silently inherit), and what makes it hard to read?
6. Which rule lets a compiler resolve every name before the program runs? Connect to the binding-time framework.
7. Python is statically scoped. Why can Python not implement dynamic scope *without* changing the language?

---

Python does not merely distinguish "local" from "global" — it has four distinct scope layers that are searched in a fixed order. This model traces that order and surfaces the single most common Python scope bug: assigning to a name inside a function makes Python treat that name as local *throughout the entire function*, even lines before the assignment. This behavior is surprising, but completely consistent once you understand the rule.

## Model 3: Python's LEGB Rule

Python resolves names in order: **L**ocal → **E**nclosing → **G**lobal → **B**uilt-in.

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

> **Watch out!** Python scopes are **function-level**, not block-level. In Java or C, a variable declared inside an `if` block or `for` loop is local to that block. In Python, `if` blocks and `for` loops do **not** create a new scope — a variable introduced inside them belongs to the enclosing function (or module). So a variable first assigned inside an `if` body is accessible throughout the rest of the function. This surprises programmers coming from Java or C, and it means Python's `global` keyword is nothing like C's `global` storage class: Python's `global` is a declaration inside a function saying "when I write this name, go find it in the module scope, not here."

**The `nonlocal` keyword — fixing the counter bug:**
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

Scope tells you *where in the code* a name is visible; lifetime tells you *how long in time* the storage for a value persists. These two concepts usually travel together — a local variable exists only while its function runs — but closures are a dramatic exception. When an inner function escapes its enclosing scope (by being returned or stored), it carries its enclosing bindings with it, keeping them alive indefinitely. This section shows both the power and the classic pitfall of that mechanism.

## 3. Scope Is Space; Lifetime Is Time

**Scope is the region of *text* where a binding is visible; lifetime is the span of *execution* during which its storage exists.** The two usually align (a local lives while its block runs) but can diverge: a C `static` local has tiny scope and program-long lifetime, and, the divergence that matters most for your project, a **closure** keeps a binding *alive* after its scope has ended.

**Lifetime divergence — closures keep bindings alive:**
```python
def make_adder(n):
    # n's SCOPE: the body of make_adder
    # n's LIFETIME: as long as the returned closure exists!
    def adder(x):
        return x + n   # n is still alive — captured by closure
    return adder

add5 = make_adder(5)
add10 = make_adder(10)

# make_adder has returned; its scope is gone, but n lives on
print(add5(3))    # 8  — n=5 is still alive
print(add10(3))   # 13 — n=10 is still alive

# Python's closure mechanism: check what's captured
print(add5.__closure__[0].cell_contents)   # 5
print(add10.__closure__[0].cell_contents)  # 10
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

> **Watch out!** The loop variable trap catches nearly every Python programmer eventually. When a `lambda` (or any closure) captures a name from an enclosing scope, it captures the **name**, not the value the name held at the moment the closure was created. By the time the loop finishes, `i` equals `4`, and every closure refers to that same `i`. This is not a bug in Python — it is the correct behavior of late binding — but it is different from what most people intend. The fix is to force **value capture** at creation time, either via a default argument (`i=i`) or a factory function that creates a fresh scope.

**The loop variable trap — scope vs lifetime:**
```python
# Classic bug: all closures share the SAME variable
adders_broken = []
for i in range(5):
    adders_broken.append(lambda x: x + i)   # i is captured by reference

print("Broken:", [f(0) for f in adders_broken])  # [4,4,4,4,4] — all see final i=4

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
- Python docs: [Execution model — naming and binding](https://docs.python.org/3/reference/executionmodel.html)

## Going Deeper (Optional Appendices)

The core lesson above stands on its own. The optional deep dives below expand on it — read whichever interest you:

- Variable Resolution: From Name to Value

## Going Deeper: Variable Resolution: From Name to Value

Variable resolution is like looking up a word in a dictionary — you start with the innermost, most-specific dictionary and work outward until you find an entry or run out of dictionaries. In programming languages, each nested function or block is its own dictionary (called a *frame* or *environment*), and the language's scoping rules determine exactly which dictionaries to search and in what order. Mastering these rules lets you read any program with confidence and avoid the subtle bugs that trip up even experienced developers.

#### Learning Goals

By the end of this activity, you will be able to:

- Trace variable lookup through a chain of nested scopes (local, enclosing, global, built-in) for Python, JavaScript, and C programs
- Compare static (lexical) scoping and dynamic scoping and predict the value each produces for a given call sequence
- Implement an environment as a stack of frames and define the lookup algorithm that walks the chain
- Identify the LEGB rule in Python and explain what happens when `global` or `nonlocal` declarations modify the default resolution path
- Analyze how scope-chain design decisions (closure semantics, hoisting, block scope) affect correctness and readability of programs

> **Prerequisites:** Basic programming, functions, variables
> **Goal:** Understand exactly how a language looks up a variable name — the scope chain, LIFO stack of environments, and why Python/JavaScript/C make different choices.

> **Before You Begin — Prerequisite Checklist**
>
> Make sure you are comfortable with the following before diving in:
>
> - **Python scope rules (LEGB):** You should know that Python looks for a name in Local, then Enclosing, then Global, then Built-in scope. If this is unfamiliar, review a Python scoping tutorial first.
> - **Closures:** You should understand that an inner function can "remember" variables from its enclosing function even after that enclosing function has returned. If closures feel mysterious, spend a few minutes with a closure example before continuing.
> - **Symbol tables:** You should know that a compiler or interpreter keeps a data structure mapping names to their bindings (type, value, memory location). If you have not seen the term before, think of it as the "dictionary" metaphor above — each scope has one.

**POGIL Roles:** Driver · Recorder · Reporter · Manager

---

#### Model 1: The Name Resolution Problem

**Intuition:** Before studying the formal rules, consider what "resolving a name" means in practice. Imagine you're reading a mystery novel and you encounter the character "Smith." You first check whether "Smith" was just introduced in this chapter (local), then whether a character named "Smith" appeared in an enclosing flashback (enclosing), and finally whether there's a "Smith" from the very beginning of the book (global). Programming languages perform exactly this layered search — the only difference is that different languages define the layers differently. Model 1 shows you three languages doing this search in the same nested structure, so you can see what they agree on and where they diverge.

When the interpreter or compiler sees a name like `x`, it must answer: *which `x`?* Every language has a rule — but the rules differ.

Consider this pattern in three languages:

**Python**

```python
x = "global"

def outer():
    x = "outer"
    def inner():
        x = "inner"
        print(x)      # (A)
    inner()
    print(x)          # (B)

outer()
print(x)              # (C)
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

**JavaScript (var)**

```javascript
var x = "global";
function outer() {
    var x = "outer";
    function inner() {
        var x = "inner";
        console.log(x);   // (A)
    }
    inner();
    console.log(x);       // (B)
}
outer();
console.log(x);           // (C)
```

**C (block scope)**

```c
#include <stdio.h>
int x = 0;   /* global */
void f() {
    int x = 1;   /* local */
    {
        int x = 2;   /* block */
        printf("%d\n", x);   /* (A) */
    }
    printf("%d\n", x);       /* (B) */
}
int main() { f(); printf("%d\n", x); return 0; }  /* (C) */
```

> **Critical Thinking Questions 1–3**

**CTQ 1.** Without running the code, predict what lines (A), (B), and (C) print in the Python version. Explain your reasoning.

[[inner / outer / global]]
<script>true</script>

**CTQ 2.** The three languages above all use *lexical (static) scope*. What property of the source code text determines which `x` each print statement refers to?

[[___ your answer here ___]]

**CTQ 3.** A classmate claims "Python, JavaScript, and C all print the same thing for this example." Is that claim true? What would need to be *different* to make them disagree?

[[___ your answer here ___]]

---

#### Model 2: The Scope Chain — A LIFO Stack of Frames

**Intuition:** Think of the call stack as a stack of sticky notes on your desk. Each time a function is called, you place a new sticky note on top with that function's local variable names written on it. When you need to look up a name, you read the top note first; if the name is not there, you peek at the note below it, and so on down to the desk surface (the global frame). When the function returns, you throw away the top note. This Last-In-First-Out (LIFO) discipline is why nested functions can see their enclosing function's variables: those variables are on the note just below. Python's LEGB rule is just a precise name for this search order.

> **Watch out!** Free variables in a closure are resolved in the **defining** scope, not the **calling** scope. When `inner` is defined inside `outer`, `inner` captures `outer`'s frame — no matter where `inner` is later called from. If you call the returned closure from an entirely different function, it still uses the scope it was born in.

When a function is called, a new **frame** (environment) is pushed onto the call stack. Name lookup walks the stack from top (innermost) to bottom (global).

```
CALL STACK (top = most recent)
┌─────────────────────────────┐
│  inner()  frame             │  ← lookup starts here
│    x = "inner"              │
├─────────────────────────────┤
│  outer()  frame             │
│    x = "outer"              │
├─────────────────────────────┤
│  global   frame             │  ← lookup ends here
│    x = "global"             │
└─────────────────────────────┘
```

Python formalizes this as the **LEGB rule**:

| Letter | Scope | Example |
|--------|-------|---------|
| **L** | Local | variable assigned inside current function |
| **E** | Enclosing | variable in any enclosing `def` or `lambda` |
| **G** | Global | variable at module top level |
| **B** | Built-in | `len`, `print`, `range`, … |

You can inspect both levels at runtime:

```python
x = "module-level"

def demo():
    y = "local"
    print("locals :", locals())
    print("globals keys:", list(globals().keys())[:6], "...")

demo()
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

##### The `nonlocal` Keyword — Fixing the Classic Counter Bug

Without `nonlocal`, assignment inside a nested function creates a *new* local variable rather than modifying the enclosing one:

```python
def make_counter():
    count = 0
    def increment():
        nonlocal count   # without this line, count += 1 raises UnboundLocalError
        count += 1
        return count
    return increment

c = make_counter()
print(c())   # 1
print(c())   # 2
print(c())   # 3
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

> **Critical Thinking Questions 4–7**

**CTQ 4.** What does LEGB stand for? List one concrete Python object that lives at each level.

[[___ L: ___ E: ___ G: ___ B: ___]]

**CTQ 5.** Remove the `nonlocal count` line from the counter above. What error do you expect, and *why* does Python raise it? (Hint: think about what assignment inside a function implies.)

[[___ your answer here ___]]

**CTQ 6.** What is the difference between a variable's **scope** (where it is *visible*) and its **lifetime** (how long its storage persists)? Give an example where these differ.

[[___ your answer here ___]]

**CTQ 7.** Consider: `x = 10` then inside a function `x = x + 1` without `global x`. Python raises `UnboundLocalError`. Why does the presence of the assignment on the left side of `=` affect the lookup on the *right* side?

[[___ your answer here ___]]

##### Simulating a Scope Chain in Python

```python
# A scope chain is just a list of dicts; lookup walks from end to front (LIFO)
def lookup(name, scope_chain):
    for frame in reversed(scope_chain):
        if name in frame:
            return frame[name]
    raise NameError(f"name '{name}' is not defined")

global_frame  = {"x": "global", "y": 99}
outer_frame   = {"x": "outer",  "z": True}
inner_frame   = {"w": 42}

chain = [global_frame, outer_frame, inner_frame]

print(lookup("w", chain))   # 42   — found in inner
print(lookup("x", chain))   # outer — shadows global x
print(lookup("y", chain))   # 99   — found in global
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

---

#### Model 3: Static (Lexical) vs Dynamic Scope

**Intuition:** Lexical scope and dynamic scope answer the same question — "which frame do I look in next?" — but they use different evidence. Lexical scope uses the *source code* as its map: you look at where the function was written down in the file, and the enclosing text tells you the parent scope. Dynamic scope uses the *call stack* as its map: you look at who called you, and their frame is the parent scope. Most modern languages (Python, JavaScript, Java, C) use lexical scope because it lets you understand a function just by reading it; with dynamic scope, you would need to know the entire call history at runtime to reason about what a variable contains.

> **Watch out!** Python's late binding in closures surprises many students. In a lexically-scoped language, you might expect a closure to capture the *value* of a variable at the moment the closure is created. Python closures instead capture the *variable itself* (a reference to the cell). This means that if the variable changes after the closure is created — for example, in a loop — the closure will see the final value of the variable when it is called, not the value at creation time. CTQ 10 below demonstrates this precisely.

The two historical approaches to scope differ in *when* name resolution happens:

| | Resolved at … | Rule |
|---|---|---|
| **Lexical (static)** | Definition site | Look outward through the *source text* |
| **Dynamic** | Call site | Look outward through the *call stack at runtime* |

```python
x = "global"

def f():
    print(x)   # which x?

def g():
    x = "local to g"
    f()          # Python (lexical): prints "global"
                 # dynamic scope would print "local to g"

g()
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

**Why does Python print `"global"`?**
Because `f` was *defined* in the module scope, so its enclosing environment is the module frame, not `g`'s frame. The call from inside `g` is irrelevant to name resolution.

##### Languages That Use Dynamic Scope

- **Emacs Lisp** (classic): variable lookup walks the *call stack*
- **Bash**: all variables are dynamic by default
- **Common Lisp special variables** (declared with `defvar`/`defparameter`)

Dynamic scope makes it easy to pass implicit parameters through deep call chains, but it makes programs much harder to reason about locally.

> **Critical Thinking Questions 8–10**

**CTQ 8.** In a dynamically-scoped language, what would `f()` print when called from `g()` above? What would it print when called directly from the module level?

[[___ your answer here ___]]

**CTQ 9.** Name one advantage and one disadvantage of dynamic scope compared to lexical scope.

[[___ your answer here ___]]

**CTQ 10.** In Python, closures capture the *enclosing scope*, not a snapshot of values. What does the following print, and why?

```python
fns = [lambda: i for i in range(3)]
print([f() for f in fns])
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

[[___ your answer here ___]]

---

#### Model 4: How C Resolves Variables

**Intuition:** C was designed before closures or garbage collectors, so its scoping model reflects the hardware directly. There is no hidden dictionary-chaining at runtime the way Python does it — C's block scopes live inside a single stack frame, and file-scope variables live in a fixed memory segment decided at compile time. Understanding C's model helps you see what Python and JavaScript are *abstracting over*. The `static` keyword in C is particularly illuminating: it lets a local variable persist across calls (extended lifetime, unchanged scope) or restricts a global to one file (unchanged lifetime, narrowed visibility) — demonstrating that scope and lifetime are genuinely independent concepts.

> **Watch out!** Hoisting in JavaScript is a resolution-time phenomenon, not a runtime one. When the JavaScript engine processes a `var` declaration, it moves (hoists) the *declaration* to the top of the enclosing function scope before any code runs — but the *assignment* stays in place. This means a variable declared with `var` anywhere in a function is technically in scope for the entire function, yet holds `undefined` until the assignment line executes. `let` and `const` fix this with block scope and a Temporal Dead Zone, which is why modern JavaScript style prefers them.

C has four scope levels and two additional concepts (linkage and storage class):

```
Scope levels in C
─────────────────────────────────────────────────────────
Block scope     │ { int x = 0; ... }     visible inside braces
Function scope  │ goto labels only
File scope      │ declared outside any function
Function-proto  │ parameter names in a declaration
─────────────────────────────────────────────────────────

Linkage (across translation units)
───────────────────────────────────
External linkage  │ int x;          — visible to linker, other .c files
Internal linkage  │ static int x;   — file-private
No linkage        │ local variables
```

##### Block Scope and Stack Frames

```
Stack frame for f():
┌────────────────────┐  ← top of stack (high address)
│  return address    │
│  saved %rbp        │
│  int x = 1         │  ← f's local x
│  int y = 2         │
├────────────────────┤
│  nested block:     │
│  int x = 99        │  ← inner x (shadows f's x, same frame region)
└────────────────────┘
```

##### `extern` Across Translation Units

```c
/* math_utils.c */
int helper_count = 0;   /* external linkage by default */

/* main.c */
extern int helper_count;   /* declaration only — no new storage */
```

> **Critical Thinking Questions 11–13**

**CTQ 11.** What does `static` mean when applied to a **local variable** in C? How does its lifetime differ from an ordinary local variable?

[[___ your answer here ___]]

**CTQ 12.** What does `static` mean when applied to a **file-scope variable or function** in C? How does this relate to the concept of information hiding?

[[___ your answer here ___]]

**CTQ 13.** A C function has a local `int x = 5`. Another translation unit uses `extern int x`. Are these the same variable? Why or why not?

[[___ your answer here ___]]

---

#### Multiple Choice Review

**Intuition:** These questions test whether you can apply the rules quickly and precisely. For each question, try to answer before reading the options — then check whether your answer matches one of the choices. If it does not, that mismatch reveals a gap worth revisiting in the models above.

**Question 1.** In Python's LEGB rule, if a name is found in the *Enclosing* scope, the search:

- [( )] continues to check the Global scope as well
- [(X)] stops immediately and uses the enclosing binding
- [( )] raises a `SyntaxError`
- [( )] falls through to the Built-in scope

**Question 2.** Which of the following correctly describes *lexical scope*?

- [( )] Variable bindings are resolved by walking the call stack at runtime
- [(X)] Variable bindings are resolved by walking the enclosing text of the source code
- [( )] All variables are global unless declared `local`
- [( )] Variables are resolved dynamically but cached after the first lookup

---

#### Exercises

**Intuition:** The exercises below ask you to both *use* closures and *simulate* the environment model in code. When you implement `lookup` and `assign` yourself, you are essentially writing the core of an interpreter — which makes the abstract rules feel concrete. Always predict the output before running; the prediction step is where real learning happens.

**Exercise 1.** Write a Python function `make_adder(n)` that returns a closure adding `n` to its argument. Verify it works for `add5 = make_adder(5); print(add5(3))` → `8`.

```python
# Your solution here

```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

**Exercise 2.** The code below has a bug. Fix it using `nonlocal` and explain what the bug was.

```python
def make_accumulator():
    total = 0
    def add(n):
        total += n   # bug: UnboundLocalError
        return total
    return add

acc = make_accumulator()
print(acc(5))
print(acc(3))
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

**Exercise 3.** Implement the `lookup` function from Model 2 but also implement `assign(name, value, scope_chain)` that modifies the *innermost* frame containing `name`, or raises `NameError` if not found. Test it.

```python
# Your solution here

```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

**Exercise 4.** Predict what each print statement outputs, then verify by running:

```python
x = 1
def f():
    x = 2
    def g():
        print(x)   # (a)
    g()
    print(x)       # (b)
f()
print(x)           # (c)
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

**Exercise 5.** Write a function `scope_depth(name, scope_chain)` that returns the *depth* at which `name` is found (0 = innermost, increasing toward global), or -1 if not found.

```python
# Your solution here

```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

---

#### Reflection

In 2–3 sentences each, answer:

1. Why does Python require the programmer to explicitly write `global` or `nonlocal` to modify outer variables, instead of just modifying them automatically?

2. A student argues: "dynamic scope is better because you can always override a variable from anywhere in the call chain." Give a concrete scenario where this leads to a hard-to-find bug.

3. How does the concept of a *scope chain* connect to the LIFO structure of the call stack? What happens to a frame's variables when the function returns?

---

*End of Activity — Variable Resolution, Scope Chains, and Stacked Scope*
