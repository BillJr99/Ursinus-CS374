<!--
author:   CS374 Course Team
email:    
version:  0.0.1
language: en
narrator: US English Female
comment:  Variable Resolution - Scope Chains, Global/Local/Stacked Scope, Static vs Dynamic Scope
import:   https://raw.githubusercontent.com/liaScript/coderunner/master/README.md
link:     https://cdn.jsdelivr.net/chartist.min.css
-->

# Variable Resolution: From Name to Value

## Learning Goals

By the end of this activity, you will be able to:

- Trace variable lookup through a chain of nested scopes (local, enclosing, global, built-in) for Python, JavaScript, and C programs
- Compare static (lexical) scoping and dynamic scoping and predict the value each produces for a given call sequence
- Implement an environment as a stack of frames and define the lookup algorithm that walks the chain
- Identify the LEGB rule in Python and explain what happens when `global` or `nonlocal` declarations modify the default resolution path
- Analyze how scope-chain design decisions (closure semantics, hoisting, block scope) affect correctness and readability of programs

> **Prerequisites:** Basic programming, functions, variables
> **Goal:** Understand exactly how a language looks up a variable name — the scope chain, LIFO stack of environments, and why Python/JavaScript/C make different choices.

**POGIL Roles:** Driver · Recorder · Reporter · Manager

---

## Model 1: The Name Resolution Problem

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

## Model 2: The Scope Chain — A LIFO Stack of Frames

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

### The `nonlocal` Keyword — Fixing the Classic Counter Bug

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

### Simulating a Scope Chain in Python

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

## Model 3: Static (Lexical) vs Dynamic Scope

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

### Languages That Use Dynamic Scope

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

## Model 4: How C Resolves Variables

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

### Block Scope and Stack Frames

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

### `extern` Across Translation Units

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

## Multiple Choice Review

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

## Exercises

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

## Reflection

In 2–3 sentences each, answer:

1. Why does Python require the programmer to explicitly write `global` or `nonlocal` to modify outer variables, instead of just modifying them automatically?

2. A student argues: "dynamic scope is better because you can always override a variable from anywhere in the call chain." Give a concrete scenario where this leads to a hard-to-find bug.

3. How does the concept of a *scope chain* connect to the LIFO structure of the call stack? What happens to a frame's variables when the function returns?

---

*End of Activity — Variable Resolution, Scope Chains, and Stacked Scope*
