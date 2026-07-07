<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://github.com/BillJr99/Ursinus-CS374-Fall2026/blob/gh-pages/_pages/Activities/liascript-types.md or locally via https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374-Fall2026/gh-pages/_pages/Activities/liascript-types.md

import: https://raw.githubusercontent.com/liascript/CodeRunner/master/README.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

# Type Systems

Every time you write `def add(x, y)` in Python, you are making an implicit promise: callers will pass values that support `+`. A **type system** is the mechanism that turns informal promises like this into enforceable contracts — checked either before your program ever runs or the instant a broken promise is exercised at runtime. Catching a broken promise in the compiler is like catching a typo before you mail a letter; catching it at runtime is like discovering the mistake only after the recipient tries to read it. This activity will show you exactly how those two approaches differ, why the difference matters, and how to build the checking machinery into your own interpreter.

## Learning Goals

By the end of this activity, you will be able to:

- Define the two independent axes of type system design (static/dynamic and strong/weak) and place common languages on each axis
- Identify type errors in Python code and predict whether they are caught at parse time, compile time, or runtime
- Compare the trade-offs between static and dynamic typing with respect to early error detection and programming flexibility
- Explain type coercion and distinguish implicit coercion (weak typing) from explicit conversion (strong typing)
- Apply type-system concepts to specify the typing rules for a language being implemented in an interpreter project

> **Before You Begin:** This activity assumes you can:
> - Explain what a runtime error is and describe the difference between a crash that happens at parse time versus one that happens during execution
> - Read and write basic Python functions, including `try`/`except` blocks and `isinstance()` checks
> - Describe at a high level what your interpreter's evaluation (`eval`) function does with a binary operation node
>
> If any of these feel shaky, review them first.

Your interpreter happily computes `5 / 0`'s error, but what should it do with `"hello" * true`? A **type system** is a language's machinery for classifying values and rejecting senseless combinations, and the design axes (static or dynamic, strong or weak, declared or inferred) are among the most consequential your team will choose. The arc: **what types are for $\rightarrow$ the two axes $\rightarrow$ inference $\rightarrow$ adding type errors to your interpreter**.

---

## Directions and Group Roles

Work in your POGIL team with rotated roles (**Manager**, **Recorder**, **Presenter**, **Reflector**). Consider each model and question individually first, then discuss with your group. The Recorder posts answers to the Class Activity Questions discussion board; the Presenter reports out areas of disagreement or alternative approaches. After class, respond to the reflective prompt individually in your notebook.

---

## Key Concepts

Before diving in, here is a plain-English glossary of the terms this activity uses. Return to this table whenever a term feels slippery.

| Term | Plain-English meaning | Why it matters |
|------|-----------------------|----------------|
| **Type** | A label on a value that says which operations are licensed for it | The whole activity is about who checks these licenses, and when |
| **Type error** | An operation applied to a value outside its license, like `"hi" * {}` | The failure every type system exists to catch — early or late |
| **Static typing** | Checking happens *before* the program runs | Catches errors on every path, including paths your tests never exercise |
| **Dynamic typing** | Checking happens at the instant each operation executes | Maximum flexibility; errors surface only when the bad line actually runs |
| **Strong typing** | The language refuses to silently mix incompatible types | Broken promises stop the program instead of flowing onward as wrong values |
| **Weak typing** | The language silently converts operands so the operation can proceed | The source of `"5" - 1 == 4` surprises; convenience purchased with silence |
| **Coercion** | An implicit, automatic type conversion the programmer never asked for | The defining behavior of weak typing; contrast with explicit conversion |
| **Type inference** | The checker deduces types from values and context, with no annotations written | Static safety without annotation ceremony — Rust, Haskell, TypeScript |
| **Type environment** | A mapping from variable names to their (inferred or declared) types | The checker's version of your interpreter's environment: names to types, not values |

---

# Part I: The Axes

## 1. Two Independent Questions

**A type classifies values and licenses operations**: numbers may be divided, strings concatenated, booleans tested. A **type error** is an operation applied outside its license. Languages differ on two independent axes:

**When is checking done?** **Static** typing checks before execution (Java rejects `int x = "hi";` at compile time); **dynamic** typing checks during execution, at the moment the operation runs (Python raises `TypeError` when `"hi" * {}` is attempted). Static catches errors earlier and on all paths, including paths your tests never run; dynamic permits more flexible code and faster iteration. This is the binding-time framework again: the type's binding time.

**How strictly is checking enforced?** **Strong** typing refuses undefined mixtures or requires explicit conversion; **weak** typing silently **coerces** (converts) operands to make the operation proceed. JavaScript famously computes `"5" - 1` as `4` and `"5" + 1` as `"51"`; Python, dynamically but *strongly* typed, raises on `"5" - 1`. The axes are independent: Python is dynamic and strong; C is static and (in places) weak.

**Inference splits the difference on ceremony.** Statically typed languages with **type inference** (Rust, Haskell, modern Java's `var`, TypeScript) deduce types you do not write: `let n = 5` is statically known to be an integer because 5 is. Inference buys static safety without annotation cost, at the price of error messages that can point far from the cause.

---

**Intuition for Model 1:** The two axes — static/dynamic and strong/weak — are completely independent, so a language can land in any of the four quadrants. Think of Python refusing `"5" - 1` (strong, because no silent conversion) yet only discovering that refusal when the line actually executes (dynamic). In contrast, a language like Haskell refuses that expression at compile time without you ever running the program (static and strong). This model asks you to place real behaviors on those axes before you look at any code.

## Model 1: Place the Languages

| Language behavior | Static/Dynamic? | Strong/Weak? |
|-------------------|-----------------|--------------|
| Rejects `x = "hi"` at compile time when x was declared int | ? | ? |
| Raises TypeError at runtime on `"5" - 1` | ? | ? |
| Computes `"5" - 1 == 4` without complaint | ? | ? |
| Compiles `let n = 5; n = "hi"` to an error without any annotations | ? | ? |

> **Watch out!** Static/dynamic and strong/weak are two *separate* axes — do not conflate them. "Static" refers to *when* checking happens (before vs. during execution). "Strong" refers to *whether* the language permits silent coercion between incompatible types. Python is **dynamic** (checks at runtime) AND **strong** (refuses coercion). C is **static** (compile-time) but can be **weak** in places (e.g., implicitly converting pointer types). Any combination of the four quadrants is possible.

> **Watch out!** Python is *not* "untyped." Every Python value has a definite type — `type(42)` is `<class 'int'>`, `type("hi")` is `<class 'str'>`. The language simply chooses to check type compatibility at runtime rather than before execution. Calling Python "untyped" is a common and consequential misconception: it conflates the absence of *declared* types with the absence of types altogether.

**Verify Python's dynamic strong typing:**
```python
# Python: dynamic (checks at runtime) + strong (refuses coercion)
print("=== Python Type Behavior ===")

# Strong: refuses silent coercion
try:
    result = "5" - 1   # JavaScript would give 4; Python refuses
except TypeError as e:
    print(f"'5' - 1 → TypeError: {e}")

# String + number: also refused
try:
    result = "hello" + 42
except TypeError as e:
    print(f"'hello' + 42 → TypeError: {e}")

# Dynamic: no compile-time check; type errors only happen at runtime
def risky(x):
    return x * 2   # works for int, float, str — but might fail

print(f"risky(5) = {risky(5)}")
print(f"risky('ab') = {risky('ab')}")  # string * 2 = "abab" — licensed!

try:
    print(risky([1, 2]) + 1)   # list * 2 works, but list + 1 fails at runtime
except TypeError as e:
    print(f"risky([1,2]) + 1 → TypeError: {e}")

# The "hidden path" problem:
def categorize(x):
    if x > 100:
        return x / 2     # if x is a string, crash — but test might not reach here
    return x + 1

# Tests passing doesn't mean type-safe:
print(categorize(50))     # fine
print(categorize(200))    # fine
# categorize("hello")     # would crash — static typing would catch this
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

### Critical Thinking Questions

1. Fill the grid and name a plausible language for each row.
2. Row 3's behavior (coercion) maximizes which evaluation criterion from week 2, and damages which? Cite the `"5" + 1` versus `"5" - 1` asymmetry in JavaScript as evidence.
3. Row 4 shows inference: the checker deduced `n`'s type from `5`. Sketch how it would propagate types through `let m = n + 1; let s = m + "!"` and where it would report the error. Whose line gets blamed?
4. Testing exercises only the paths you run; static checking covers all paths. Construct a two-branch program where dynamic typing hides a type error from a test suite that achieves 100% line coverage on the happy branch — then explain why coverage did not save you.

---

# Part II: Types in Your Interpreter

**Intuition for Model 2:** Your interpreter already evaluates binary expressions like `3.0 + 4.0`. This model shows you how to add a gatekeeper at the top of that evaluation: before you touch the operands, check whether the combination makes sense and raise a clear error if it does not. Think of it like a bouncer who checks IDs before letting values into an operation — `float + float` gets in, `float + string` does not.

## 2. A Dynamically, Strongly Typed Core

Your language (like Python) will check at runtime and refuse silent coercion: a respectable, implementable choice. The implementation pattern: each evaluated value carries its Python type along naturally; binary operations *check before computing*.

```python
# Adding strong dynamic typing to the BinOp evaluator: check, then compute.

def type_name(v):
    return {bool: "bool", float: "number", str: "string"}.get(type(v), type(v).__name__)

def eval_binop(op, left, right):
    """Strong typing: refuse undefined mixtures with a located, specific error."""
    if op in ("+", "-", "*", "/"):
        if op == "+" and isinstance(left, str) and isinstance(right, str):
            return left + right                   # string concatenation: licensed
        if isinstance(left, bool) or isinstance(right, bool):
            raise TypeError(f"arithmetic on bool is not defined: "
                            f"{type_name(left)} {op} {type_name(right)}")
        if isinstance(left, float) and isinstance(right, float):
            if op == "+": return left + right
            if op == "-": return left - right
            if op == "*": return left * right
            if op == "/":
                if right == 0: raise ZeroDivisionError("division by zero")
                return left / right
        raise TypeError(f"operator {op!r} not defined for "
                        f"{type_name(left)} and {type_name(right)}")
    if op in ("<", "<=", ">", ">=", "==", "!="):
        if type(left) is not type(right):
            raise TypeError(f"cannot compare {type_name(left)} with {type_name(right)}")
        return {"<": left < right, "<=": left <= right, ">": left > right,
                ">=": left >= right, "==": left == right, "!=": left != right}[op]
    raise ValueError(f"unknown operator {op!r}")

print("=== Type Checking Results ===")
for l, op, r in [(3.0, "+", 4.0), ("ab", "+", "cd"), (3.0, "+", "cd"),
                 (True, "*", 2.0), (3.0, "<", "cd"), (3.0, "/", 0.0)]:
    try:
        result = eval_binop(op, l, r)
        print(f"  {l!r} {op} {r!r} = {result!r}")
    except (TypeError, ZeroDivisionError) as e:
        print(f"  {l!r} {op} {r!r} → {type(e).__name__}: {e}")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

### Critical Thinking Questions

5. Identify the lines that make this typing *strong* (refusals) versus the line that would make it *weak* if you replaced a refusal with `float(...)` coercion. Make the weak version mentally: what does `3.0 + "cd"` return, and what bug class did you just legalize?
6. We licensed `+` for two strings but not `*` for string and number. Python licenses `"ab" * 3`. Debate and record your project's policy on string repetition, and add it to `SEMANTICS.md`.
7. Where would a *static* checker for your language live in the pipeline (between which two existing stages), and what would it walk? You already own every data structure it needs; name them.

[[MC]]
Python raises a TypeError on `"5" - 1` at the moment the subtraction executes, never silently converting. On the two axes, Python is therefore:
- ( ) Statically and weakly typed
- ( ) Statically and strongly typed
- (x) Dynamically and strongly typed
- ( ) Dynamically and weakly typed

[[MC]]
A language that deduces `n: int` from `let n = 5` without requiring the programmer to write the type annotation is using:
- ( ) Dynamic typing
- ( ) Weak typing
- (x) Type inference
- ( ) Duck typing

> **Watch out!** Duck typing (Python's "if it walks like a duck and quacks like a duck, treat it as a duck") is *still* a form of typing — it is a dynamic, structural approach where compatibility is checked by whether an object supports the required operations, not by its declared class. Saying a language "has no types" because it uses duck typing is incorrect. Duck typing is a deliberate design choice that trades the early-error benefits of nominal or structural static checks for maximum flexibility.

---

**Intuition for Model 2:** A dynamically typed interpreter never checks anything in advance — every check rides along with evaluation itself. Picture evaluation as water flowing up from the leaves of the AST: values form at the literals, meet at each operator, and *at each meeting point* the bouncer from Section 2 checks the pair before combining them. This model slows that flow down to one step at a time so you can see exactly when each check fires — and, just as important, what has already irrevocably happened by the time a check fails.

## Model 2: Tracing the Runtime Checker on a Compound Expression

**Worked example.** Trace the interpreter evaluating `(3.0 + 4.0) < (2.0 * 6.0)`. Evaluation is bottom-up (innermost first), so the checks fire in this order:

| Step | Node evaluated | Left value : type | Right value : type | Check performed | Result |
|------|----------------|-------------------|--------------------|-----------------|--------|
| 1 | `3.0 + 4.0` | `3.0` : number | `4.0` : number | `+` licensed for number, number | `7.0` |
| 2 | `2.0 * 6.0` | `2.0` : number | `6.0` : number | `*` licensed for number, number | `12.0` |
| 3 | `7.0 < 12.0` | `7.0` : number | `12.0` : number | `<` requires same type — OK | `True` |

Three checks, three passes, one final value. Now the same trace for `(3.0 + 4.0) < ("total: " + 12.0)`:

| Step | Node evaluated | Left value : type | Right value : type | Check performed | Result |
|------|----------------|-------------------|--------------------|-----------------|--------|
| 1 | `3.0 + 4.0` | `3.0` : number | `4.0` : number | `+` licensed | `7.0` |
| 2 | `"total: " + 12.0` | `"total: "` : string | `12.0` : number | `+` **not** licensed for string, number | **TypeError** |
| 3 | `... < ...` | — | — | never reached | — |

Step 1 completed *before* the error: its work is done and cannot be undone. The `<` at step 3 never runs at all. That is dynamic checking in one picture: checks are interleaved with execution, so an error stops the program mid-flight rather than before takeoff.

```python
def type_name(v):
    return {bool: "bool", float: "number", str: "string"}.get(type(v), type(v).__name__)

STEP = 0

def evaluate(node):
    """Evaluate a tuple-AST bottom-up, narrating every type check."""
    global STEP
    kind = node[0]
    if kind == "lit":
        return node[1]
    op, left_node, right_node = node
    left  = evaluate(left_node)     # innermost first:
    right = evaluate(right_node)    # children are fully evaluated before we check
    STEP += 1
    print(f"  step {STEP}: {left!r} {op} {right!r}  "
          f"[{type_name(left)} {op} {type_name(right)}]", end="  ")
    if op in "+-*/":
        if isinstance(left, float) and isinstance(right, float):
            result = {"+": left + right, "-": left - right,
                      "*": left * right, "/": left / right}[op]
            print(f"check OK -> {result!r}")
            return result
        if op == "+" and isinstance(left, str) and isinstance(right, str):
            print(f"check OK -> {(left + right)!r}")
            return left + right
        print("check FAILS")
        raise TypeError(f"operator {op!r} not defined for "
                        f"{type_name(left)} and {type_name(right)}")
    if op == "<":
        if type(left) is not type(right):
            print("check FAILS")
            raise TypeError(f"cannot compare {type_name(left)} with {type_name(right)}")
        print(f"check OK -> {left < right}")
        return left < right
    raise ValueError(f"unknown operator {op!r}")

good = ("<", ("+", ("lit", 3.0), ("lit", 4.0)),
             ("*", ("lit", 2.0), ("lit", 6.0)))
bad  = ("<", ("+", ("lit", 3.0), ("lit", 4.0)),
             ("+", ("lit", "total: "), ("lit", 12.0)))

print("=== (3.0 + 4.0) < (2.0 * 6.0) ===")
print("final value:", evaluate(good))

print("\n=== (3.0 + 4.0) < ('total: ' + 12.0) ===")
STEP = 0
try:
    evaluate(bad)
except TypeError as e:
    print(f"stopped by TypeError: {e}")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

[[MC]]
An interpreter with dynamic (runtime) checking evaluates `(3.0 + 4.0) < ("a" + 1.0)`. When is the type error for `"a" + 1.0` detected?
- ( ) Before execution begins
- ( ) When the `<` comparison runs
- (x) At the moment the `+` on `"a"` and `1.0` is evaluated — after `3.0 + 4.0` has already computed
- ( ) Never; dynamic languages coerce automatically

### Critical Thinking Questions

8. The trace shows the checks firing in steps 1, 2, 3 — the same order as evaluation. State the general rule: in a dynamically typed interpreter, when does the check for an operator fire, relative to the evaluation of that operator's operands?
9. In the failing trace, step 1 finished before the TypeError at step 2. Suppose step 1 had been `print("charging card...")` instead of an addition. What does this tell you about *where in a program's lifetime* you would prefer type errors to fire, and which typing discipline delivers that?
10. Redo the failing trace as a *static* checker would perform it, before execution: rewrite the table with types only, no values. Which columns disappear, and which check still fails?

---

**Intuition for Model 3:** Type inference is the party trick where the compiler figures out every variable's type from context alone — you write `let a = 2` and the checker deduces `a: int` without you saying so. Mechanically, it is just a tree walk: visit each node, compute what type it must produce, and propagate that information upward. When two branches disagree on type (e.g., adding an `int` to a `str`), the checker reports an error *at that node* — which may feel far from the actual mistake if the mistake was made pages earlier.

## Model 3: Type Inference by Hand

**Implementing Hindley-Milner style inference in miniature:**

```python
# Mini type inference: propagate types through a simple expression AST

from dataclasses import dataclass
from typing import Any, Optional

@dataclass
class TInt:   pass
@dataclass
class TFloat: pass
@dataclass
class TStr:   pass
@dataclass
class TBool:  pass
@dataclass
class TUnknown: pass  # not yet inferred

def type_str(t):
    return {TInt: "int", TFloat: "float", TStr: "str",
            TBool: "bool", TUnknown: "?"}[type(t)]

# "Type environment": name → type
type_env = {}

def infer(expr, env):
    """Infer the type of an expression given a type environment."""
    kind, *args = expr
    if kind == "int":     return TInt()
    if kind == "float":   return TFloat()
    if kind == "str":     return TStr()
    if kind == "bool":    return TBool()
    if kind == "var":
        name = args[0]
        if name in env:   return env[name]
        raise TypeError(f"undefined variable {name!r}")
    if kind == "let":
        name, val_expr, body_expr = args
        val_type = infer(val_expr, env)
        new_env = dict(env, **{name: val_type})
        print(f"  let {name}: {type_str(val_type)}")
        return infer(body_expr, new_env)
    if kind == "add":
        lt = infer(args[0], env)
        rt = infer(args[1], env)
        if type(lt) == type(rt) and isinstance(lt, (TInt, TFloat)):
            return lt
        if isinstance(lt, TStr) and isinstance(rt, TStr):
            return TStr()
        raise TypeError(f"cannot add {type_str(lt)} and {type_str(rt)}")
    if kind == "lt":
        lt = infer(args[0], env)
        rt = infer(args[1], env)
        if type(lt) != type(rt):
            raise TypeError(f"cannot compare {type_str(lt)} with {type_str(rt)}")
        return TBool()
    raise ValueError(f"unknown expression kind {kind!r}")

# Program: let a = 2; let b = a + 3; let c = b < 10; in c
print("=== Type Inference Trace ===")
program = ("let", "a", ("int",), ("let", "b", ("add", ("var", "a"), ("int",)),
           ("let", "c", ("lt", ("var", "b"), ("int",)), ("var", "c"))))
try:
    result_type = infer(program, {})
    print(f"Result type: {type_str(result_type)}")
except TypeError as e:
    print(f"Type error: {e}")

# Program with error: let a = 2; let d = a + "hello"  — type error
print("\n=== Type Error Program ===")
bad_program = ("let", "a", ("int",), ("add", ("var", "a"), ("str",)))
try:
    result_type = infer(bad_program, {})
    print(f"Result type: {type_str(result_type)}")
except TypeError as e:
    print(f"Type error: {e}")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

### Worked Example: Tracing Type Inference Step by Step

Consider the small program: `let a = 2; let b = a + 3; let c = b < 10; in c`

The `infer` function walks this AST top-down, building a **type environment** (a mapping from variable names to their inferred types) as it goes:

| Step | Node visited | Type environment before | Result type deduced |
|------|-------------|------------------------|---------------------|
| 1 | `let a = ("int",)` | `{}` (empty) | literal `("int",)` → `TInt` |
| 2 | Extend env with `a: TInt`; recurse into body | `{a: TInt}` | — |
| 3 | `let b = ("add", ("var","a"), ("int",))` | `{a: TInt}` | look up `a` → `TInt`; literal → `TInt`; `TInt + TInt` → `TInt` |
| 4 | Extend env with `b: TInt`; recurse into body | `{a: TInt, b: TInt}` | — |
| 5 | `let c = ("lt", ("var","b"), ("int",))` | `{a: TInt, b: TInt}` | look up `b` → `TInt`; literal → `TInt`; same type → `TBool` |
| 6 | Extend env with `c: TBool`; body is `("var","c")` | `{a: TInt, b: TInt, c: TBool}` | look up `c` → `TBool` |
| **Final** | whole program | — | **`TBool`** |

Now trace the *error* program: `let a = 2; a + "hello"`

| Step | Node visited | Type environment | Result |
|------|-------------|-----------------|--------|
| 1 | `let a = ("int",)` | `{}` | `TInt` |
| 2 | Extend env; recurse into body `("add", ("var","a"), ("str",))` | `{a: TInt}` | — |
| 3 | left: look up `a` → `TInt`; right: `("str",)` → `TStr` | `{a: TInt}` | `TInt + TStr` → **TypeError**: `cannot add int and str` |

Notice that the error is reported at the `add` node (step 3), but the root cause is the choice made at step 1. This distance between the error location and the root cause is a recurring challenge in type inference systems — and why good inference error messages are hard to write.

### Critical Thinking Questions

11. The inference trace shows `let a: int`, `let b: int`, `let c: bool`. These are determined entirely from the *values* (literals), with no type annotations written. Is this static or dynamic typing? Explain.
12. When inference encounters `a + "hello"`, it reports the error at the `add` expression. But the *root cause* is that `a` was given an int value. How far is the reported error from the root cause, and what does this say about inference error message quality?
13. What would need to change to support `let a = 2; let b = a + 3.0;`? (Hint: numeric type widening — `int + float → float`.) Modify the `infer` function to allow this.

---

**Intuition for Model 4:** Weak typing's danger is not crashes — it is the *absence* of crashes. When a language coerces instead of refusing, a type mistake does not stop the program; it flows onward disguised as a plausible-looking value, and the first symptom appears far from the cause, often outside the program entirely. This model performs a postmortem on one such incident, step by step, with the strong-typing alternative traced alongside for contrast.

## Model 4: A Type-Error Postmortem

**The incident.** A checkout system written in a weakly typed language reads a price from a web form. Form fields always arrive as *strings* — and nobody converted. Here is the program:

```
subtotal = "19.99"                       # from the form: a STRING, not a number
shipping = 5.00
total    = (subtotal + shipping) * 1.06  # add shipping, then 6% tax
```

The intended arithmetic: `(19.99 + 5.00) * 1.06 = 24.99 * 1.06 = 26.49`. What the weak language actually computes, step by step:

| Step | Expression | What a weak language does | Value after | What a strong language does |
|------|-----------|----------------------------|-------------|------------------------------|
| 1 | `subtotal = "19.99"` | stores the string | `"19.99"` (string) | the same — the mistake is still latent |
| 2 | `subtotal + 5.00` | coerces `5.00` → `"5"`, then *concatenates* | `"19.995"` (string) | **TypeError: cannot add string and number** — stops here |
| 3 | `"19.995" * 1.06` | coerces `"19.995"` → `19.995`, then multiplies | `21.1947` (number) | never reached |
| 4 | charge the customer | charges `$21.19` with no error anywhere | wrong by `$5.30` | bug reported at step 2, with a line number |

Note the direction flip: at step 2 the `+` coerced the *number toward the string*, but at step 3 the `*` coerced the *string toward the number*. The same pair of types flowed in opposite directions depending on the operator — that inconsistency, not any single conversion, is what makes weak typing treacherous. And notice what is missing from the weak column: any error, at any step. The only symptom is money.

```python
# Simulate both typing disciplines on the same buggy program.

def to_js_str(v):
    if isinstance(v, float) and v == int(v):
        return str(int(v))          # 5.0 renders as "5", as in JavaScript
    return str(v)

def weak_add(a, b):
    """JavaScript-style +: if either side is a string, concatenate."""
    if isinstance(a, str) or isinstance(b, str):
        return to_js_str(a) + to_js_str(b)
    return a + b

def weak_mul(a, b):
    """JavaScript-style *: coerce both sides toward number."""
    return float(a) * float(b)

def strong_add(a, b):
    if type(a) is not type(b):
        raise TypeError(f"cannot add {type(a).__name__} and {type(b).__name__}")
    return a + b

subtotal = "19.99"       # the latent mistake: a string from the form
shipping = 5.00

print("=== Weak mode: no errors, wrong money ===")
step2 = weak_add(subtotal, shipping)
print(f"  step 2: {subtotal!r} + {shipping!r} -> {step2!r}")
step3 = weak_mul(step2, 1.06)
print(f"  step 3: {step2!r} * 1.06 -> {step3!r}")
print(f"  charged: ${step3:.2f}   (intended: ${(19.99 + 5.00) * 1.06:.2f})")

print("\n=== Strong mode: stops at the mistake ===")
try:
    strong_add(subtotal, shipping)
except TypeError as e:
    print(f"  step 2: TypeError: {e}")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

[[MC]]
In a weakly typed language, `"19.99" + 5.0` yields `"19.995"` and `"19.995" * 1.06` yields `21.1947`. The deepest design problem this postmortem illustrates is:
- ( ) Floating-point rounding error
- ( ) The slowness of string operations
- (x) Silent coercion lets a type mistake flow through the program as plausible-looking wrong values instead of stopping with an error
- ( ) Strings cannot represent decimal numbers

### Critical Thinking Questions

14. Walk the postmortem table: at which step did the *type* first go wrong, and at which step did the *money* first go wrong? Why is it significant that these are different steps?
15. Step 2 coerced number → string, but step 3 coerced string → number. Write the coercion rule a language designer would have to publish to justify both choices at once. Does the result sound principled or accidental?
16. The weak-mode run produces no error at any point; the bug would surface only as customer complaints. Name two other places in the software pipeline (besides the language's type system) where this bug could have been caught, and what each catch would cost compared to a step-2 TypeError.
17. For your project language: which, if any, of these coercions will you allow? Record the decision in `SEMANTICS.md`, citing this postmortem as evidence for or against.

---

# Part III: Synthesis and Practice

## 3. Exercises

1. *Interpreter integration.* Wire `eval_binop` into your interpreter's `BinOp` case, add booleans and strings as value types (with literals in your lexer and parser if absent), and demonstrate three programs: one that runs, one that raises your TypeError with a helpful message, and one comparison program.
2. *Coercion lab.* Implement a `--weak` configuration flag that turns two refusals into coercions. Write one program whose output silently changes between modes, and one paragraph on which mode your team ships and why, citing the evaluation criteria.
3. *Inference on paper.* For the program `let a = 2; let b = a + 3; let c = b < a; let d = c + 1;`, infer every variable's type top to bottom and identify the first line a static checker would reject. Note how far the *error* is from the *mistake*, and what that implies about inference error messages.
4. *Type archaeology.* Find one real bug report or postmortem caused by implicit coercion (JavaScript and PHP folklore abounds). Summarize the failure in two sentences and the language rule that would have prevented it.
5. *Runtime type tag.* Modify your interpreter's value representation so that every value is a `(type_tag, raw_value)` pair: `("num", 3.0)`, `("str", "hi")`, `("bool", True)`. Update `eval_binop` to check the tag before operating. Show that error messages now include the tag.

---

## Reflection Prompt

In your notebook: strong typing refuses to guess what you meant; weak typing guesses. Describe one tool or person in your life whose refusals to guess you have come to value, and what it cost to appreciate them. Then: the type inference mini-implementation shows that a checker can deduce `c: bool` from context alone — no annotation needed. Does this feel like magic to you now? After this activity, what makes it feel mechanical rather than magical?

---

## 4. Further Reading

- Douglas Thain. *Introduction to Compilers and Language Design*, Chapter 7.
- Robert Nystrom. *Crafting Interpreters*, "Evaluating Expressions" (runtime type checks).
- Gary Bernhardt. "Wat" (talk, 2012, online): four minutes of coercion comedy with a serious lesson.
- Benjamin Pierce. *Types and Programming Languages* (TAPL), the gold standard reference.

---

## Going Deeper: Type Systems: From Annotations to Inference

> **Opening Hook:** A type checker is like a proofreader who catches grammatical errors before the article is published. The proofreader does not verify that your argument is logically sound or that your facts are accurate — but it *does* systematically catch every subject-verb disagreement, every dangling modifier, every mismatched quote. A type system does the same thing for code: it does not prove your program is *correct*, but it proves, automatically and exhaustively, that it is free of an entire class of structural errors — before the program runs once.

#### Learning Goals

By the end of this activity, you will be able to:

- Compare static and dynamic typing by predicting when a type error is caught for a given program and test suite
- Explain how type inference allows a statically typed language to eliminate annotation overhead while preserving compile-time guarantees
- Trace the Hindley-Milner type inference process by assigning type variables, generating constraints, and applying unification
- Evaluate the trade-offs between type annotation burden and error-message clarity in languages with type inference
- Implement basic type-checking logic in Python that rejects ill-typed expressions before evaluation

---

> **Before You Begin**
>
> This module assumes you are comfortable with:
> - Writing and calling Python functions, including higher-order functions (functions that take functions as arguments)
> - The concept of a variable's *type* (e.g., `int`, `str`, `bool`) and what a `TypeError` means
> - Basic lambda calculus notation: `λx. body` means "a function that takes `x` and returns `body`"
> - What an AST (Abstract Syntax Tree) is — the tree structure your parser builds to represent a program
>
> You do **not** need prior experience with Haskell or formal type theory. All formal notation is introduced step by step.

---

*"A type system is a tractable syntactic method for proving the absence of certain program behaviors by classifying phrases according to the kinds of values they compute."* — Benjamin Pierce, *Types and Programming Languages*

A type is a **proof** carried in the program, checked by the compiler, that a value will be used consistently. When the checker passes, you have a machine-verified claim that the program is free of entire classes of errors — not just the errors you thought to test for, but all errors of that shape. This module traces the design space: from **dynamic typing** (types checked at runtime), through **static typing** (types checked at compile time), to **type inference** (types deduced by the compiler without annotations), to the beautiful algorithm at the heart of Haskell's type system — **Hindley-Milner**, the method that lets you write:

```haskell
map f xs = foldr (\x acc -> f x : acc) [] xs
```

without a single type annotation and have the compiler prove that `map :: (a -> b) -> [a] -> [b]` for *every* type `a` and `b`.

---

#### Directions

Work in your POGIL team. Solo sections are for individual reflection first; group sections require all four roles.

---

### Part I: Static vs. Dynamic Typing

> **Intuition:** Imagine two worlds. In one world, before your program runs, a compiler reads every line and asks: "Can I *prove* this expression produces a value of the right type?" If not, it refuses to compile. In the other world, the program starts running and only complains when it actually hits the bad operation — possibly after minutes of correct execution. That is the essential difference between static and dynamic typing. Neither is strictly "better" — they make different tradeoffs that suit different programming contexts.

#### 1. The Core Tradeoff

**Dynamic typing** (Python, JavaScript, Ruby, Lisp): types are attached to *values* at runtime. A variable has no type; its current value does. Type errors are caught when the offending operation actually runs.

**Static typing** (Java, Haskell, Rust, TypeScript): types are attached to *expressions* at compile time. A variable has a declared (or inferred) type; the compiler verifies consistency before the program runs. Type errors are caught before any execution.

```python
# Dynamic typing: this runs without error until the bad line
def add(a, b):
    return a + b

print(add(1, 2))        # 3 — fine
print(add("a", "b"))    # "ab" — also fine! + is overloaded
print(add(1, "hello"))  # TypeError at runtime: unsupported operand types
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

```
-- Static typing (Haskell): this fails at COMPILE time, before any execution
-- add :: Int -> Int -> Int
-- add a b = a + b
-- main = putStrLn (add 1 "hello")
-- Error: Couldn't match type '[Char]' with 'Int'
-- Expected type: Int, Actual type: String
```

---

> **Watch out!** A common misconception: "Python doesn't have types." Python has types on every *value* — `type(42)` returns `<class 'int'>`. What Python *lacks* is compile-time checking of those types. The values know their types; the compiler just doesn't verify consistency before running.

##### Model 1: Type Error Timing

```python
# When does Python catch this error? Trace the execution.

def always_fails(x):
    return x + 1   # will fail if x is not a number

def sometimes_called(flag, x):
    if flag:
        return always_fails(x)
    return 42

# This line is fine:
print(sometimes_called(False, "hello"))   # 42

# This line fails at runtime:
try:
    print(sometimes_called(True, "hello"))
except TypeError as e:
    print(f"[TypeError] {e}")

# The bug was already in the code when we ran line 1.
# A static type checker would have flagged it before line 1 ran.
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

##### Critical Thinking Questions — *Solo*

1. In the `sometimes_called` function, the bug is present whether or not `flag` is `True`. Under dynamic typing, when is the bug discovered? Under static typing, when would it be discovered?
2. Name three program behaviors that a type system cannot detect (i.e., programs that type-check but are still wrong).
3. Python has `typing.py` with annotations: `def always_fails(x: int) -> int`. These are not enforced by Python at runtime, but tools like `mypy` check them statically. Is this static typing, dynamic typing, or something in between? What does the existence of these tools suggest about the tradeoff?

---

#### 2. Type Inference: Types Without Annotations

> **Intuition:** Type inference is how a compiler does the annotation work *for you*. When you write `x = 3 + 4` in Haskell, the compiler reasons: `3` has type `Int`, `4` has type `Int`, `+` takes two `Int`s and returns an `Int`, therefore `x` must have type `Int`. No annotation needed — the compiler solved the equation. Full Hindley-Milner inference extends this to functions, polymorphism, and entire programs.

**Type inference** is the ability to deduce a type from context without the programmer writing it. Every language has some: even Java infers the type of a local variable with `var x = 3` (Java 10+). Full inference — where the programmer writes almost no type annotations — is the achievement of Hindley-Milner.

```python
# Python's runtime cannot infer types, but we can reason about them.
# What is the type of each expression?

x = 3            # int
y = 3.14         # float
z = x + y        # float (implicit promotion)
f = lambda a: a  # for every type T, T -> T (polymorphic)
g = lambda a: a + 1  # int -> int (because + 1 constrains a to int)
h = lambda a: len(a) # for sequences: list/str/... -> int
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

```haskell
-- Haskell's compiler deduces ALL of these without a single annotation:
x = 3          -- x :: Num a => a
y = 3.14       -- y :: Fractional a => a
f = \a -> a    -- f :: a -> a          (id)
g = \a -> a+1  -- g :: Num a => a -> a
h = length     -- h :: [a] -> Int
compose f g x = f (g x)  -- compose :: (b -> c) -> (a -> b) -> a -> c
```

---

### Part II: The Hindley-Milner Algorithm

> **Intuition:** Hindley-Milner is an algorithm for solving a system of type equations — the same way you solve simultaneous linear equations in algebra. Each expression in the program generates a constraint ("the argument of this function must have the same type as its parameter"), and the algorithm finds the most general assignment of types to variables that satisfies all the constraints simultaneously. The remarkable result (proved by Milner, 1978) is that if a solution exists, the algorithm always finds the *most general* one.

#### 3. Types as Terms

In Hindley-Milner, **types** are first-class objects, just like lambda terms:

$$
\tau ::= \alpha \mid T \mid \tau_1 \to \tau_2 \mid T[\tau_1, \ldots, \tau_n]
$$

- $\alpha, \beta, \gamma, \ldots$ are **type variables** (unknown types)
- $\mathbf{Int}, \mathbf{Bool}, \mathbf{String}$ are **type constants**
- $\tau_1 \to \tau_2$ is a **function type** (input $\tau_1$, output $\tau_2$)
- $\mathbf{List}[\tau]$, $\mathbf{Maybe}[\tau]$ are **parameterized types**

A **type scheme** (or polytype) $\forall \alpha.\ \tau$ means "for all types $\alpha$, this has type $\tau$." The identity function `id :: forall a. a -> a` says: whatever type you hand me, I return the same type.

> **Watch out!** The notation $\forall \alpha.\ \tau$ (read "for all alpha, tau") does *not* mean the function works on infinitely many types by magic. It means the *same code*, without modification, is safe to use with any type that fits the shape. The type variable $\alpha$ is a placeholder, not a runtime parameter.

#### 4. Unification: Solving Type Equations

**Unification** is the algorithm that, given two type terms, finds a substitution (a mapping from type variables to types) that makes them equal.

$$
\text{unify}(\alpha \to \mathbf{Int}, \ \mathbf{Bool} \to \beta) \Rightarrow \{\alpha \mapsto \mathbf{Bool},\ \beta \mapsto \mathbf{Int}\}
$$

**Unification fails** if the terms have incompatible structure:

$$
\text{unify}(\mathbf{Int}, \ \mathbf{Bool}) \Rightarrow \text{fail}
$$

$$
\text{unify}(\alpha, \ \alpha \to \alpha) \Rightarrow \text{fail (occurs check)}
$$

The **occurs check** prevents the infinite type $\alpha = \alpha \to \alpha$, which would require an infinitely deep type.

```python
# Unification in Python

class TypeVar:
    def __init__(self, name): self.name = name
    def __repr__(self): return self.name

class TypeConst:
    def __init__(self, name): self.name = name
    def __repr__(self): return self.name

class FuncType:
    def __init__(self, inp, out): self.inp = inp; self.out = out
    def __repr__(self): return f"({self.inp} -> {self.out})"

Int  = TypeConst("Int")
Bool = TypeConst("Bool")

def occurs(var, typ):
    """Does type variable `var` appear in `typ`? (Occurs check)"""
    if isinstance(typ, TypeVar):   return typ.name == var.name
    if isinstance(typ, TypeConst): return False
    if isinstance(typ, FuncType):  return occurs(var, typ.inp) or occurs(var, typ.out)
    return False

def apply_subst(subst, typ):
    """Apply a substitution dict to a type."""
    if isinstance(typ, TypeVar):
        return apply_subst(subst, subst[typ.name]) if typ.name in subst else typ
    if isinstance(typ, TypeConst):
        return typ
    if isinstance(typ, FuncType):
        return FuncType(apply_subst(subst, typ.inp), apply_subst(subst, typ.out))
    return typ

def unify(t1, t2, subst=None):
    """Return a substitution that unifies t1 and t2, or raise TypeError."""
    if subst is None: subst = {}
    t1 = apply_subst(subst, t1)
    t2 = apply_subst(subst, t2)

    if isinstance(t1, TypeConst) and isinstance(t2, TypeConst):
        if t1.name == t2.name: return subst
        raise TypeError(f"Cannot unify {t1} with {t2}")

    if isinstance(t1, TypeVar):
        if isinstance(t2, TypeVar) and t1.name == t2.name: return subst
        if occurs(t1, t2): raise TypeError(f"Occurs check: {t1} in {t2}")
        subst[t1.name] = t2; return subst

    if isinstance(t2, TypeVar):
        return unify(t2, t1, subst)

    if isinstance(t1, FuncType) and isinstance(t2, FuncType):
        subst = unify(t1.inp, t2.inp, subst)
        return unify(apply_subst(subst, t1.out), apply_subst(subst, t2.out), subst)

    raise TypeError(f"Cannot unify {t1} with {t2}")

# Examples
a, b = TypeVar("α"), TypeVar("β")

# unify(α -> Int, Bool -> β)  =>  {α: Bool, β: Int}
result = unify(FuncType(a, Int), FuncType(Bool, b))
print("Subst:", result)   # {'α': Bool, 'β': Int}

# unify(Int, Bool) => fail
try:
    unify(Int, Bool)
except TypeError as e:
    print("Expected failure:", e)

# occurs check: unify(α, α -> α) => fail
try:
    unify(a, FuncType(a, a))
except TypeError as e:
    print("Occurs check failure:", e)
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

---

> **Watch out!** Unification can fail in two ways: a *structural mismatch* (trying to unify `Int` with `Bool`) and an *occurs check failure* (trying to make a type variable equal to a type that contains it, like `α = α → α`). The occurs check is not just a technicality — without it, the type system would accept programs that loop forever at the type level, producing infinite types the compiler could never print or reason about.

#### 5. Algorithm W: Inferring Types for Lambda Expressions

> **Intuition:** Algorithm W walks the AST of a program top-down, assigning fresh type variables to unknowns and generating unification constraints as it goes. Think of it as two passes in one: a forward pass that names every unknown ("this parameter gets type `t1`; this function result gets type `t2`"), then a constraint-solving pass that determines what each name must be. The Python implementation below makes this concrete — follow the `infer` function case by case and you will see exactly where each constraint comes from.

**Algorithm W** (Damas and Milner, 1982) takes an expression and an environment mapping variables to type schemes, and returns the most general type for the expression along with the substitution needed.

```python
# Simplified Algorithm W for our Mini language AST
# AST node classes defined inline (no external imports needed)

class Num:
    def __init__(self, val): self.val = val
class BoolLit:
    def __init__(self, val): self.val = val
class Var:
    def __init__(self, name): self.name = name
class Fun:
    def __init__(self, param, body): self.param = param; self.body = body
class App:
    def __init__(self, func, arg): self.func = func; self.arg = arg
class Let:
    def __init__(self, name, value, body): self.name = name; self.value = value; self.body = body

# Type classes (re-stated here for self-contained execution)
class TypeVar:
    def __init__(self, name): self.name = name
    def __repr__(self): return self.name
class TypeConst:
    def __init__(self, name): self.name = name
    def __repr__(self): return self.name
class FuncType:
    def __init__(self, inp, out): self.inp = inp; self.out = out
    def __repr__(self): return f"({self.inp} -> {self.out})"

Int  = TypeConst("Int")
BoolT = TypeConst("Bool")

def occurs(var, typ):
    if isinstance(typ, TypeVar):   return typ.name == var.name
    if isinstance(typ, TypeConst): return False
    if isinstance(typ, FuncType):  return occurs(var, typ.inp) or occurs(var, typ.out)
    return False

def apply_subst(subst, typ):
    if isinstance(typ, TypeVar):
        return apply_subst(subst, subst[typ.name]) if typ.name in subst else typ
    if isinstance(typ, TypeConst): return typ
    if isinstance(typ, FuncType):
        return FuncType(apply_subst(subst, typ.inp), apply_subst(subst, typ.out))
    return typ

def unify(t1, t2, subst=None):
    if subst is None: subst = {}
    t1 = apply_subst(subst, t1); t2 = apply_subst(subst, t2)
    if isinstance(t1, TypeConst) and isinstance(t2, TypeConst):
        if t1.name == t2.name: return subst
        raise TypeError(f"Cannot unify {t1} with {t2}")
    if isinstance(t1, TypeVar):
        if isinstance(t2, TypeVar) and t1.name == t2.name: return subst
        if occurs(t1, t2): raise TypeError(f"Occurs check: {t1} in {t2}")
        subst[t1.name] = t2; return subst
    if isinstance(t2, TypeVar): return unify(t2, t1, subst)
    if isinstance(t1, FuncType) and isinstance(t2, FuncType):
        subst = unify(t1.inp, t2.inp, subst)
        return unify(apply_subst(subst, t1.out), apply_subst(subst, t2.out), subst)
    raise TypeError(f"Cannot unify {t1} with {t2}")

class TypeScheme:
    def __init__(self, bound_vars, typ):
        self.bound_vars = bound_vars
        self.typ = typ
    def instantiate(self, fresh_var):
        subst = {v: fresh_var(v) for v in self.bound_vars}
        return apply_subst(subst, self.typ)
    def __repr__(self):
        if self.bound_vars:
            return f"∀{','.join(self.bound_vars)}.{self.typ}"
        return str(self.typ)

counter = [0]
def fresh():
    counter[0] += 1
    return TypeVar(f"t{counter[0]}")

def free_type_vars(typ):
    if isinstance(typ, TypeVar):   return {typ.name}
    if isinstance(typ, TypeConst): return set()
    if isinstance(typ, FuncType):  return free_type_vars(typ.inp) | free_type_vars(typ.out)
    return set()

def generalize(env_vars, typ):
    free_in_type = free_type_vars(typ)
    free_in_env  = set().union(*(free_type_vars(t) for t in env_vars))
    quantified   = free_in_type - free_in_env
    return TypeScheme(list(quantified), typ)

def infer(node, env):
    """Returns (substitution, type) for node given type environment env."""
    if isinstance(node, Num):
        return {}, Int
    if isinstance(node, BoolLit):
        return {}, BoolT
    if isinstance(node, Var):
        if node.name not in env:
            raise TypeError(f"[typecheck] Unbound variable: {node.name}")
        return {}, env[node.name].instantiate(lambda v: fresh())
    if isinstance(node, Fun):
        param_type = fresh()
        new_env    = {**env, node.param: TypeScheme([], param_type)}
        s, body_type = infer(node.body, new_env)
        return s, FuncType(apply_subst(s, param_type), body_type)
    if isinstance(node, App):
        s1, func_type = infer(node.func, env)
        s2, arg_type  = infer(node.arg, {k: TypeScheme(v.bound_vars, apply_subst(s1, v.typ))
                                          for k, v in env.items()})
        result_type = fresh()
        s3 = unify(apply_subst(s2, func_type), FuncType(arg_type, result_type))
        combined = {**s1, **s2, **s3}
        return combined, apply_subst(combined, result_type)
    if isinstance(node, Let):
        s1, val_type = infer(node.value, env)
        scheme       = generalize({apply_subst(s1, v.typ) for v in env.values()}, val_type)
        new_env      = {**{k: TypeScheme(v.bound_vars, apply_subst(s1, v.typ)) for k, v in env.items()},
                        node.name: scheme}
        s2, body_type = infer(node.body, new_env)
        return {**s1, **s2}, body_type
    raise TypeError(f"[typecheck] Unknown node: {type(node).__name__}")

# Demo: infer the type of (fun x -> x + 1) applied to a number literal
# fun x -> x + 1  encoded as: Fun("x", App(App(Var("+"), Var("x")), Num(1)))
# We simplify: just infer Fun("x", Num(1)) to show the machinery works
env = {}
s, t = infer(Fun("x", Num(1)), env)
print(f"fun x -> 1  :  {t}")   # (t1 -> Int)

s2, t2 = infer(Let("id", Fun("x", Var("x")), App(Var("id"), Num(42))), env)
print(f"let id = fun x -> x in id 42  :  {t2}")  # Int
print("Algorithm W defined and demonstrated.")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

---

[[MC]]
The type of `map` in Haskell is `(a -> b) -> [a] -> [b]`. The type variable `a` can be instantiated to `Int`, making the type `(Int -> b) -> [Int] -> [b]`. This is called:

- (x) Parametric polymorphism (generics): the same code works for all types; the type variables are placeholders for any type.
- ( ) Ad-hoc polymorphism (overloading): the function has different implementations for different types.
- ( ) Subtype polymorphism (inheritance): the type variables range over subtypes of a base class.
- ( ) Type coercion: integers are automatically converted to match the type variable.

---

#### 6. Type Errors as Proof Failures

> **Intuition:** A type error is not "the compiler being picky." It is the compiler saying: "I tried to find a consistent assignment of types to all expressions in your program, and the constraints you generated are *contradictory* — no assignment can satisfy them all." The error message is a proof that the program cannot be correct as written under the type discipline. This is why type errors can feel confusing: the reported location is where the *contradiction surfaced*, not necessarily where the *mistake was made*.

When the type checker rejects a program, it is not arbitrarily strict — it has found a proof that the program **cannot be correct** under the type discipline. The error message is a witness to the inconsistency.

```python
# Simulating what a type checker would say about a common bug

# "Bug": applying a non-function
# Python: crashes at runtime
try:
    x = 5
    result = x(3)   # TypeError: 'int' object is not callable
except TypeError as e:
    print(f"Runtime: {e}")

# Haskell equivalent (conceptual):
# x :: Int
# x 3  =>  type error: "Int" is not a function
# The type checker knows Int cannot be applied to anything,
# because Int has no instance of the function arrow (->) type.

# What the occurs check prevents:
# If we allowed α = α -> α, then:
#   (λx. x x) :: α -> α  (applying x to x requires α = α -> α)
# This type has no finite representation.
# Languages that allow this (System U) are not normalizing:
# they allow non-terminating programs to type-check.
print("Type error examples shown.")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

---

#### 7. Exercises

1. **Unification by hand.** Solve each unification problem, showing the substitution or explaining the failure:
   - $\text{unify}(\alpha \to \beta, \ \mathbf{Int} \to \mathbf{Bool})$
   - $\text{unify}(\alpha \to \alpha, \ \mathbf{Int} \to \beta)$
   - $\text{unify}((\alpha \to \beta) \to \gamma, \ (\mathbf{Int} \to \beta) \to (\mathbf{Bool} \to \mathbf{String}))$
   - $\text{unify}(\alpha, \ \mathbf{List}[\alpha])$ — why does this fail?

2. **Type derivation.** Derive the type of `fun f -> fun x -> f (f x)` using Algorithm W (on paper, not code). What is the most general type? This is the Church numeral 2.

3. **Add type checking to your interpreter.** Implement a `TypeChecker` class (using the `Visitor` pattern from the transpiler module) that annotates each AST node with its inferred type, using the unification algorithm from Section 4. Your type checker should report type errors with location information before evaluation begins. Test it on: `(fun x -> x + 1) true` (type error) and `let f = fun x -> x in f 1 + f 2` (polymorphic let, should type-check).

4. **Compare error messages.** Write a program in both Python and Java that applies a non-function to an argument. Run both. Compare the error messages: which is more informative? Which catches the error earlier? Which gives the programmer more information about *why* the error occurred?

5. **Hindley-Milner in Haskell.** Load GHCi (`ghci`). Type `:t map`, `:t fst`, `:t flip`, `:t ($)`. For each, explain in English what the universally-quantified type variables mean, and give two concrete instantiations (e.g., `map` can be `(Int -> String) -> [Int] -> [String]` or `(Bool -> Char) -> [Bool] -> [Char]`).

---

#### 8. Further Reading

- Pierce, Benjamin C. *Types and Programming Languages* (MIT Press, 2002). The standard reference. Chapters 9–22 cover simply-typed lambda calculus, subtyping, and System F.
- Damas, Luis and Robin Milner. "Principal Type-Schemes for Functional Programs." *POPL '82*. The original Algorithm W paper; 7 pages.
- Cardelli, Luca and Peter Wegner. "On Understanding Types, Data Abstraction, and Polymorphism." *ACM Computing Surveys* 17(4), 1985. The definitive taxonomy of type-system concepts.
- Heeren, Bastiaan, Jurriaan Hage, and Doaitse Swierstra. "Helium, for Learning Haskell." *Haskell Workshop*, 2003. How to give type errors that help beginners rather than intimidating them.

---

## Going Deeper: Type Systems: From Weak to Strong, Static to Dynamic

> **Opening Hook:** Type system features like generics are like templates in manufacturing: you write the blueprint once for `List<T>` and the factory instantiates it for steel, aluminum, or titanium without rewriting the assembly line. The `T` is not a runtime value — it is a compile-time *slot* that the type checker fills in at each use site, verifying safety separately for each instantiation. This module explores the full design space: how strictly types are checked (strong vs. weak), when they are checked (static vs. dynamic), whether compatibility is determined by name or shape (nominal vs. structural), and what survives to runtime (type erasure).

#### Learning Goals

By the end of this activity, you will be able to:

- Identify where a language falls on the 2×2 matrix of static/dynamic and strong/weak type disciplines
- Analyze JavaScript-style implicit coercions and predict the result of mixed-type expressions
- Compare structural typing and nominal typing and determine which relationship holds for two given types
- Explain type erasure and describe how generic types are represented at runtime in a JVM-style language
- Evaluate the correctness risks introduced by weak typing and implicit coercions in real-world code

---

> **Before You Begin**
>
> This module assumes you are comfortable with:
> - Writing Python classes and calling methods on objects
> - The idea that a variable has a *type* (e.g., `int`, `str`) and that operations can fail with `TypeError`
> - Basic familiarity with at least one statically typed language (Java, C, TypeScript, or similar) — enough to know what a type annotation looks like
> - The concept of a *generic* container such as Java's `ArrayList<String>` or Python's `List[int]`
>
> You do **not** need to know what "covariance" or "structural subtyping" mean yet — those are introduced here.

---

> **Prerequisites:** Basic programming in Python and one statically-typed language
> **Goal:** Understand the 2×2 matrix of type discipline, how type coercion works, what structural vs nominal typing means, and how type erasure lets generics coexist with runtime efficiency.

**POGIL Roles:** Driver · Recorder · Reporter · Manager

---

#### Model 1: The 2×2 Matrix of Type Systems

> **Intuition:** Think of the two axes as answering two separate questions. *When* does the language check types? (Before running = static; while running = dynamic.) *How strictly* does the language handle a mismatch? (Refuse to proceed = strong; silently convert = weak.) These questions are independent: a language can be any combination of the four quadrants. Most programmers have only experienced one or two quadrants; this model forces you to see the full space.

Type systems vary along two orthogonal axes:

**Axis 1 — When are types checked?**

- **Static:** At compile time, before any code runs. Errors are caught early.
- **Dynamic:** At runtime, when an operation is actually attempted. More flexible but errors appear later.

**Axis 2 — How strictly are type mismatches handled?**

- **Strong:** The language refuses to implicitly coerce a value from one type to another. A type mismatch is an error.
- **Weak:** The language will silently convert values between types to make an operation work.

```
               STATIC              DYNAMIC
           ┌───────────────┬───────────────────┐
  STRONG   │  Java, C#,    │  Python, Ruby,    │
           │  Haskell, Rust│  Erlang           │
           ├───────────────┼───────────────────┤
  WEAK     │  C, C++       │  JavaScript, PHP, │
           │               │  Perl             │
           └───────────────┴───────────────────┘
```

> **Note:** "Strong" and "weak" are informal terms without a single agreed definition. We use them to mean: does the language allow implicit type coercions that change the *kind* of data?

```python
# Python: dynamic AND strong
# Type errors surface at runtime, but Python won't silently coerce types
x = "5"
y = 3
print(x + y)   # TypeError: can only concatenate str (not "int") to str
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

> **Critical Thinking Questions 1–3**

**CTQ 1.** In the 2×2 grid above, where would you place TypeScript? Where would you place Perl? Justify each placement.

[[___ your answer here ___]]

**CTQ 2.** A language is *statically typed* but *weakly typed*. Give a concrete example from C where the compiler accepts code that silently performs a type coercion.

[[___ your answer here ___]]

**CTQ 3.** Python's `TypeError` above fires at *runtime*, not compile time. What does this tell you about whether Python checks types at all?

[[___ your answer here ___]]

---

> **Watch out!** The terms "strong" and "weak" typing are *informal* and used inconsistently in the wild. Some textbooks define "strong" to mean statically checked; others use it to mean no implicit coercions. In this course we use "strong" strictly to mean: the language does not silently convert between *kinds* of data (e.g., number to string). When you read these terms in other sources, always check what the author means.

#### Model 2: Type Coercion — The JavaScript Nightmare

> **Intuition:** JavaScript's coercion rules were designed to make the language beginner-friendly by "doing what you probably meant." The problem is that "what you probably meant" is defined by a complex set of precedence rules that no one can memorize — and that interact badly at scale. Python made the opposite design choice: fail loudly on any ambiguous coercion, forcing the programmer to be explicit. The code is slightly more verbose but the behavior is predictable.

JavaScript is infamous for implicit coercions. These are all valid JavaScript expressions:

| Expression | Result | Why |
|---|---|---|
| `"5" + 3` | `"53"` | `+` prefers string concatenation |
| `"5" - 3` | `2` | `-` has no string meaning; coerces to number |
| `[] + {}` | `"[object Object]"` | both coerced to strings |
| `{} + []` | `0` | `{}` parsed as empty block; `+[]` = 0 |
| `false == "0"` | `true` | both coerced to 0 |
| `null == undefined` | `true` | special case in spec |
| `null === undefined` | `false` | strict equality, no coercion |

The root cause: JavaScript has a small set of runtime types (`number`, `string`, `boolean`, `object`, `undefined`, `null`, `symbol`, `bigint`) and the operators try hard to make any operands work.

**Python's intentional design contrast:**

```python
# Python refuses implicit numeric/string coercions
print("5" + 3)         # TypeError — no implicit coercion
print(int("5") + 3)    # 8 — explicit conversion is fine
print(str(3) + "5")    # "35" — explicit conversion is fine
print(True + 1)        # 2 — bool IS a subclass of int in Python (one coercion Python does allow)
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

##### Implicit vs Explicit Coercion

- **Implicit coercion** (type *coercion*): language does it automatically — `"5" - 3` in JS
- **Explicit coercion** (type *conversion* or *casting*): programmer does it — `int("5")` in Python

> **Critical Thinking Questions 4–6**

**CTQ 4.** In JavaScript, `"5" + 3` gives `"53"` but `"5" - 3` gives `2`. What rule would explain why `+` and `-` behave differently?

[[___ your answer here ___]]

**CTQ 5.** Python allows `True + 1 == 2`. Is this a violation of Python's "strong typing"? Argue both sides, then give your conclusion.

[[___ your answer here ___]]

**CTQ 6.** A teammate says: "Weak typing is just a bug — all languages should be strongly typed." Give one legitimate use case where implicit coercion reduces boilerplate without causing confusion.

[[___ your answer here ___]]

---

#### Model 3: Structural vs Nominal Typing

> **Intuition:** Imagine hiring for a job. A nominal hiring process checks your official job title on your resume — if it doesn't say "Senior Engineer," you don't qualify, even if you can do everything the role requires. A structural hiring process checks your skills — if you can write code, debug systems, and design architecture, you qualify, regardless of what your title says. Nominal typing is the first process; structural typing is the second. Python's duck typing takes this to the extreme: it doesn't even check at hire time, it just tries the work and fails if you can't do it.

Two philosophies for deciding whether two types are *compatible*:

**Nominal typing** — compatibility is determined by *name* (and explicit declaration).

```java
// Java: nominal
interface Drawable { void draw(); }
class Circle implements Drawable { public void draw() { ... } }
class Square { public void draw() { ... } }  // does NOT implement Drawable
// Square cannot be used where Drawable is expected, even though it has draw()
```

**Structural typing** — compatibility is determined by *shape* (do you have the right methods/fields?).

```typescript
// TypeScript: structural
interface Drawable { draw(): void; }
class Circle { draw() { console.log("circle"); } }
class Square { draw() { console.log("square"); } }
// Both Circle and Square satisfy Drawable — no explicit declaration needed
```

**Python's duck typing** is informal structural typing: "if it walks like a duck and quacks like a duck, it's a duck."

```python
class Circle:
    def draw(self):
        print("Drawing circle")

class Square:
    def draw(self):
        print("Drawing square")

def render(shape):
    shape.draw()   # works for anything with a draw() method

render(Circle())   # works
render(Square())   # works
render(42)         # AttributeError at runtime — "int has no attribute 'draw'"
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

##### Python Protocols (Structural Typing Made Explicit)

Python 3.8 added `Protocol` for *static* structural checking:

```python
from typing import Protocol, runtime_checkable

@runtime_checkable
class Drawable(Protocol):
    def draw(self) -> None: ...

class Triangle:
    def draw(self) -> None:
        print("Drawing triangle")

t = Triangle()
print(isinstance(t, Drawable))   # True — structural, not nominal!
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

> **Critical Thinking Questions 7–9**

**CTQ 7.** In nominal typing, what must a class do to be considered a subtype of an interface? In structural typing, what determines subtyping?

[[___ your answer here ___]]

**CTQ 8.** Duck typing defers type checking to runtime. What is the trade-off compared to structural typing checked at compile time?

[[___ your answer here ___]]

**CTQ 9.** Go uses structural typing for interfaces: a type satisfies an interface by having the right methods, no `implements` needed. What advantage does this give to library designers? What risk does it introduce?

[[___ your answer here ___]]

---

> **Watch out!** Python's `Protocol` and duck typing look similar but operate at different times. Duck typing is a *runtime* check — Python tries to call the method and raises `AttributeError` if it's missing. A `Protocol` with `@runtime_checkable` allows `isinstance` checks at runtime, but the real power is enabling *static* tools like `mypy` to verify structural compatibility before you run the program at all.

#### Model 4: Gradual Typing and Type Annotations

> **Intuition:** Gradual typing is a spectrum dial, not a binary switch. At one end, every value is untyped and any operation is attempted at runtime. At the other end, every expression has a verified static type and the compiler rejects anything inconsistent. Gradual typing lets you place individual functions or modules at any point on this dial, which is why Python went from zero type annotation support (Python 2) to a rich annotation system (Python 3.5+) without breaking existing code. The unannotated parts behave as before; the annotated parts gain static checking.

Some languages allow mixing typed and untyped code in the same program. This is **gradual typing**.

```
Spectrum of type discipline:
Untyped ──────────────────────────────────── Fully Static
  │                  │                              │
Python (no hints) Python + hints (mypy)   Java/Haskell/Rust
```

**Python type hints** (PEP 484, Python 3.5+):

```python
def greet(name: str) -> str:
    return "Hello, " + name

def add(x: int, y: int) -> int:
    return x + y

# Annotations are stored but NOT enforced at runtime
print(greet(42))         # works at runtime despite type hint saying str
print(add.__annotations__)
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

**Key insight:** Python type hints are *documentation* and *tool hints*, not enforcement. The runtime ignores them. Tools like `mypy`, `pyright`, and IDEs use them for static analysis.

##### What mypy Would Catch

```python
# mypy would flag this before you run it:
def double(x: int) -> int:
    return x * 2

result: str = double(5)   # error: Incompatible types in assignment
                          # (expression has type "int", variable has type "str")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

> **Critical Thinking Questions 10–11**

**CTQ 10.** What does it mean for a type system to be *gradual*? What is the key property that separates gradual typing from simply "optional type hints"?

[[___ your answer here ___]]

**CTQ 11.** A function `def f(x)` with no annotation is treated by mypy as `def f(x: Any) -> Any`. Why does `Any` play a special role in gradual type systems rather than acting like `object`?

[[___ your answer here ___]]

---

> **Watch out!** Python's type annotations do *not* raise errors at runtime. `def greet(name: str)` followed by `greet(42)` will run without complaint. The annotation is stored as metadata (accessible via `__annotations__`) but ignored by the Python interpreter. The enforcement only happens if you run a separate static checker like `mypy`. This surprises many students who expect Java-like behavior.

#### Model 5: Type Erasure

> **Intuition:** Type erasure is the compiler's answer to a performance problem: if `List<String>` and `List<Integer>` had to be separate classes in memory, you would need an explosion of class definitions. Instead, the Java compiler checks all the generic types at compile time for correctness, then *throws away* the type parameters and produces a single `List` class at the bytecode level. The safety was verified already — no need to repeat it at runtime. C++ takes the opposite approach (monomorphization): it keeps the type information and generates a separate specialized function for each instantiation, trading binary size for the ability to optimize each version independently.

When generic types are compiled, the type parameter often disappears. This is **type erasure**.

##### Java: Erasure at Compile Time

```java
// Source code — parameterized
List<String> names = new ArrayList<>();
names.add("Alice");
String s = names.get(0);   // compiler inserts cast

// After erasure — what the JVM actually runs
List names = new ArrayList();
names.add("Alice");
String s = (String) names.get(0);   // explicit cast inserted by compiler
```

At runtime, `List<String>` and `List<Integer>` are the **same** class. You cannot write `names instanceof List<String>`.

##### C++: Monomorphization (No Erasure)

```cpp
template<typename T>
T max_val(T a, T b) { return a > b ? a : b; }

// Compiler generates TWO separate functions:
int    max_val(int a,    int b);     // for int
double max_val(double a, double b);  // for double
```

C++ templates are erased in a different sense: the source template disappears, but each instantiation becomes a fully typed, specialized function.

##### Python: No Runtime Generics at All

```python
from typing import get_type_hints, List

def first(items: List[int]) -> int:
    return items[0]

# What survives to runtime?
print(get_type_hints(first))
# {'items': list[int], 'return': <class 'int'>}
# The annotation IS accessible via get_type_hints, but...

xs: List[int] = [1, 2, 3]
xs.append("oops")   # no runtime error — list doesn't check element types
print(xs)
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

##### C++ `std::function` as Type Erasure

`std::function<void(int)>` stores *any callable* with the right signature — a regular function, a lambda, a functor. The concrete type is erased; only the interface survives. This is the **type erasure design pattern** (distinct from Java's compiler mechanism).

> **Critical Thinking Questions 12–15**

**CTQ 12.** In Java, why can't you write `new T()` or `T[] arr = new T[10]` inside a generic method? (Hint: what has been erased?)

[[___ your answer here ___]]

**CTQ 13.** C++ monomorphization means a template instantiated with 10 different types generates 10 copies of the function. What is the trade-off vs Java's erasure approach?

[[___ your answer here ___]]

**CTQ 14.** Python's `list` at runtime has no knowledge of its type annotation. What practical problem does this cause if you rely on type hints for correctness?

[[___ your answer here ___]]

**CTQ 15.** The `std::function` type erasure pattern in C++ has a runtime cost (heap allocation, indirect call). Under what circumstances is that cost worth paying?

[[___ your answer here ___]]

---

#### Multiple Choice Review

**Question 1.** A language checks types only when an operation is actually executed, and it does *not* implicitly convert between numeric and string types. This language is:

- [( )] Static and weak
- [( )] Static and strong
- [(X)] Dynamic and strong
- [( )] Dynamic and weak

**Question 2.** In Java's generic type system, `List<String>` and `List<Integer>` at runtime are:

- [(X)] The same raw `List` class (type parameter erased)
- [( )] Different classes generated by monomorphization
- [( )] Incompatible interfaces requiring explicit adapters
- [( )] Identical because Java has no generics at runtime

**Question 3.** Which of the following best describes Python's `Protocol` class?

- [( )] Enforces nominal subtyping at runtime
- [(X)] Enables structural subtyping checked statically by tools like mypy
- [( )] Replaces `abstract` base classes entirely
- [( )] Adds compile-time generics to Python

---

#### Exercises

**Exercise 1.** In Python, write a function that deliberately breaks the type hint contract and confirm that Python does NOT raise a runtime error:

```python
def multiply(x: int, y: int) -> int:
    return x * y

# Call it with strings and observe
result = multiply("ha", 3)
print(result)
print(type(result))
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

**Exercise 2.** Demonstrate Python's strong typing by showing three operations that *do* raise `TypeError`, and three that succeed after explicit conversion:

```python
# Three TypeError examples
# Three explicit conversion examples

```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

**Exercise 3.** Implement a `Sizeable` Protocol and two classes that satisfy it structurally (without inheriting from it). Verify with `isinstance`:

```python
from typing import Protocol, runtime_checkable

# Your solution here

```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

**Exercise 4.** Use `get_type_hints` to inspect the annotations of a function with several parameters, then add a value of the wrong type to a typed list and confirm no runtime error:

```python
from typing import get_type_hints, List

def process(items: List[str], count: int) -> bool:
    return len(items) == count

print(get_type_hints(process))
items: List[str] = ["a", "b"]
items.append(99)   # wrong type — does Python complain?
print(items)
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

**Exercise 5.** Write a `TypedStack` class that enforces element type at runtime (unlike Python's built-in `list`). Use `__init__(self, element_type)` and raise `TypeError` on a bad `push`:

```python
# Your solution here

```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

---

*End of Activity — Type Systems: Strong/Weak, Static/Dynamic, Structural/Nominal, Type Coercion, Type Erasure*

---

## Going Deeper: Type Inference: How Does the Compiler Know the Types?

#### Learning Goals

By the end of this activity, you will be able to:

- Explain how type inference frames type-checking as constraint generation followed by unification
- Trace the type variable assignment and constraint generation steps of Algorithm W for simple expressions and function definitions
- Implement the unification algorithm that solves a system of type equations by substitution
- Apply let-polymorphism (generalization and instantiation) to explain how the same function can be used at multiple types
- Analyze type inference failure cases and identify which constraint produces a unification error

> **Before You Begin**
>
> This activity assumes you are comfortable with:
>
> - **Type systems basics** — what types are, why they matter, and the difference between static and dynamic typing. Review: [Type Systems](liascript-types.md)
> - **Python OOP** — dataclasses, inheritance, and `isinstance` checks. Review: [Types in Python](liascript-types.md)
>
> If either of those feels shaky, spend 10–15 minutes reviewing before continuing. The models here build directly on those foundations.

---

Type inference is the magic behind languages like Haskell, Rust, and OCaml where you don't write types — the compiler figures them out. At its core, it works like solving a system of equations: each expression generates type constraints (`x + 1` means `x` must be an `Int`), then unification solves the system. The result is that "if you can write it, it has a type; if it doesn't have a type, it won't compile." This is genuinely surprising — and you'll implement it from scratch today.

---

#### Directions and Group Roles

Work in your POGIL team with rotated roles (**Manager**, **Recorder**, **Presenter**, **Reflector**). You will build Algorithm W piece by piece across five models, each model depending on the last. The Recorder maintains a running glossary of terms introduced. The Presenter will be asked to explain one model to another group. After class, respond to the reflective prompt individually in your notebook.

---

#### Model 1: Types as Terms — A Type Algebra

##### The Big Picture First

Before diving into code, here is the core intuition. Consider this simple function:

```
f(x) = x + 1

Step 1 — Assign type variables:  f : α,   x : β,   1 : Int

Step 2 — Generate constraints:   β = Int        (because x appears in x + 1, and 1 is Int,
                                                  so the + operator requires both sides to be Int)
                                  α = Int → Int  (because f takes a value of type β and returns
                                                  a value of type β + 1, which is Int)

Step 3 — Solve (unify):          substitute β = Int everywhere

Result:  f : Int → Int,   x : Int
```

This "assign unknowns, collect equations, solve" process is exactly what Algorithm W automates. Every model below implements one piece of it.

---

##### Type Terms

Types in Hindley-Milner are **terms** — a small algebra with three forms: base types (`Int`, `Bool`, `Str`), function types (`t1 → t2`), and type variables (`'a`, `'b`, `'c`). Type variables are the key insight: they represent *unknown* types that the algorithm will later fill in.

```python  liascript
from dataclasses import dataclass, field
from typing import Any, Optional

# Type terms
@dataclass(frozen=True)
class TVar:    # type variable: 'a, 'b, 'c
    name: str
    def __str__(self): return f"'{self.name}"

@dataclass(frozen=True)
class TCon:    # type constructor: Int, Bool, List
    name: str
    args: tuple = ()
    def __str__(self):
        if not self.args: return self.name
        return f"({self.name} {' '.join(str(a) for a in self.args)})"

@dataclass(frozen=True)
class TFun:    # function type: t1 -> t2
    t1: Any
    t2: Any
    def __str__(self): return f"({self.t1} -> {self.t2})"

# Some type constants
Int  = TCon("Int")
Bool = TCon("Bool")
Str  = TCon("Str")
def List(t): return TCon("List", (t,))

# Type variables
a, b, c = TVar("a"), TVar("b"), TVar("c")

# Example types:
print("Some types:")
print(f"  Int:              {Int}")
print(f"  Bool:             {Bool}")
print(f"  Int -> Bool:      {TFun(Int, Bool)}")
print(f"  'a -> 'a:         {TFun(a, a)}")           # identity function
print(f"  'a -> 'b -> 'a:   {TFun(a, TFun(b, a))}")  # const function
print(f"  ('a -> 'b) -> List 'a -> List 'b: {TFun(TFun(a, b), TFun(List(a), List(b)))}")  # map

# Free type variables
def free_vars(t) -> set:
    if isinstance(t, TVar): return {t.name}
    if isinstance(t, TCon): return set().union(*[free_vars(a) for a in t.args]) if t.args else set()
    if isinstance(t, TFun): return free_vars(t.t1) | free_vars(t.t2)
    return set()

print(f"\nFree vars of ('a -> 'b -> 'a): {free_vars(TFun(a, TFun(b, a)))}")
print(f"Free vars of (Int -> Bool):     {free_vars(TFun(Int, Bool))}")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

##### Critical Thinking Questions

> **CTQ 1.1** `TFun(a, TFun(b, a))` represents `'a -> 'b -> 'a`. What function has this type? (Hint: it takes two arguments and returns the first one, ignoring the second.) Write a Python lambda that has this type.

[[___ your answer here ___]]

> **CTQ 1.2** A type variable `'a` means "any type." The function `id : 'a -> 'a` says "given any type `'a`, it takes a value of that type and returns a value of that type." Why is this more useful than having `id_int : Int -> Int` and `id_bool : Bool -> Bool` as separate functions?

[[___ your answer here ___]]

> **CTQ 1.3** `free_vars` finds unbound type variables in a type. For `TFun(Int, Bool)`, there are no free variables. For `TFun(a, TFun(b, a))`, there are two. Why would a type *with* free variables be considered "polymorphic," while a type *without* free variables is "monomorphic"?

[[___ your answer here ___]]

> **CTQ 1.4** The `map` function's type `('a -> 'b) -> List 'a -> List 'b` contains two different type variables. What does the presence of *two* type variables say about `map`'s flexibility compared to a function like `reverse : List 'a -> List 'a` which has only one?

[[___ your answer here ___]]

---

#### Model 2: Substitution — Replacing Type Variables with Types

##### The Find-and-Replace Analogy

A substitution is like a "find and replace" for types. `{α: Int, β: Bool}` means "wherever you see α, replace it with Int; wherever you see β, replace it with Bool." So applying that substitution to `α → β` produces `Int → Bool`.

The algorithm builds up a substitution incrementally as it gathers constraints. At the end, the substitution tells us the type of every expression in the program.

> **Watch out!** `compose_subst` order matters: `compose(s1, s2)` applies s2 first, then s1. This is the function-composition convention — just like `(f ∘ g)(x) = f(g(x))` means g runs first. When composing `s1` on top of `s2`, we must apply `s1` to all of `s2`'s values so that earlier bindings are refined by later discoveries.

```python  liascript
{% raw %}
# Substitution: dict mapping type variable names to types
# e.g., {"a": Int, "b": Bool} means 'a := Int, 'b := Bool

from dataclasses import dataclass
from typing import Any

@dataclass(frozen=True)
class TVar:
    name: str
    def __str__(self): return f"'{self.name}"

@dataclass(frozen=True)
class TCon:
    name: str
    args: tuple = ()
    def __str__(self):
        if not self.args: return self.name
        return f"({self.name} {' '.join(str(a) for a in self.args)})"

@dataclass(frozen=True)
class TFun:
    t1: Any
    t2: Any
    def __str__(self): return f"({self.t1} -> {self.t2})"

Int  = TCon("Int")
Bool = TCon("Bool")

def free_vars(t) -> set:
    if isinstance(t, TVar): return {t.name}
    if isinstance(t, TCon): return set().union(*[free_vars(a) for a in t.args]) if t.args else set()
    if isinstance(t, TFun): return free_vars(t.t1) | free_vars(t.t2)
    return set()

def apply_subst(subst: dict, t) -> Any:
    """Apply substitution to type t, recursively."""
    if isinstance(t, TVar):
        return apply_subst(subst, subst[t.name]) if t.name in subst else t
    if isinstance(t, TCon):
        return TCon(t.name, tuple(apply_subst(subst, a) for a in t.args))
    if isinstance(t, TFun):
        return TFun(apply_subst(subst, t.t1), apply_subst(subst, t.t2))
    return t

def compose_subst(s1: dict, s2: dict) -> dict:
    """Compose two substitutions: apply s1 to s2's values, then merge."""
    result = {k: apply_subst(s1, v) for k, v in s2.items()}
    result.update(s1)
    return result

# Test substitutions
subst1 = {"a": Int, "b": Bool}
t1 = TFun(TVar("a"), TVar("b"))  # 'a -> 'b
print(f"Before: {t1}")
print(f"After applying {{a:=Int, b:=Bool}}: {apply_subst(subst1, t1)}")

# Composition: first apply s2, then s1
s2 = {"c": TFun(TVar("a"), Int)}  # c := 'a -> Int
s1 = {"a": Bool}                   # a := Bool
composed = compose_subst(s1, s2)
print(f"\nComposed substitution: {composed}")
print(f"Apply composed to 'c: {apply_subst(composed, TVar('c'))}")  # should be Bool -> Int

# What about a substitution that maps a variable to itself?
identity_subst = {"a": TVar("a")}
t2 = TFun(TVar("a"), Int)
print(f"\nApply identity subst to 'a -> Int: {apply_subst(identity_subst, t2)}")
{% endraw %}
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

##### Critical Thinking Questions

> **CTQ 2.1** After applying `{a:=Int, b:=Bool}` to `'a -> 'b`, what is the result? Is there anything "polymorphic" left in the resulting type? What happened to the type variables?

[[___ your answer here ___]]

> **CTQ 2.2** `compose_subst(s1, s2)` means "first do s2, then do s1." Why must we apply `s1` to `s2`'s *values* when composing? Give a concrete example where forgetting to do this would produce a wrong result.

[[___ your answer here ___]]

> **CTQ 2.3** The code tests applying `{"a": TVar("a")}` (a variable mapped to itself) to `'a -> Int`. What is the result? Why is this substitution effectively a no-op, and when might the algorithm generate such a substitution?

[[___ your answer here ___]]

> **CTQ 2.4** After applying a "complete" substitution (one that maps every free variable), can the result still contain type variables? What would it mean if it does — is the expression still polymorphic, or is something wrong?

[[___ your answer here ___]]

---

#### Model 3: Unification — The Heart of Type Inference

##### What Unification Does

Unification asks: "Can these two types be made identical by substituting type variables?"

- `Int = Int` → yes (trivially — no substitution needed)
- `α = Int` → yes (substitute α := Int)
- `List(α) = List(Bool)` → yes (unify α with Bool, giving `{α: Bool}`)
- `Int = Bool` → **NO** (failure — this is a type error!)
- `α → β = Int → Bool` → yes (substitute α := Int, β := Bool)

The result of a successful unification is the *most general substitution* (MGU) that makes the two types equal. "Most general" means: we make only the commitments we are forced to make, leaving everything else as a free variable.

> **Watch out!** The occurs check prevents infinite types like `α = List(α)`. Without it, unification would try to build `List(List(List(...)))` forever — an infinitely nested type — and loop forever. The check catches this: if α appears inside the right-hand side, the equation has no finite solution, so we reject it as a type error.

**Unification** is the engine of type inference. When the algorithm says "this argument must be `Int` but you passed a `Bool`", that is a unification failure — a type error. When it succeeds, the result tells us exactly how to reconcile two type expressions.

```python  liascript
from dataclasses import dataclass
from typing import Any

@dataclass(frozen=True)
class TVar:
    name: str
    def __str__(self): return f"'{self.name}"

@dataclass(frozen=True)
class TCon:
    name: str
    args: tuple = ()
    def __str__(self):
        if not self.args: return self.name
        return f"({self.name} {' '.join(str(a) for a in self.args)})"

@dataclass(frozen=True)
class TFun:
    t1: Any
    t2: Any
    def __str__(self): return f"({self.t1} -> {self.t2})"

Int  = TCon("Int")
Bool = TCon("Bool")

def free_vars(t) -> set:
    if isinstance(t, TVar): return {t.name}
    if isinstance(t, TCon): return set().union(*[free_vars(a) for a in t.args]) if t.args else set()
    if isinstance(t, TFun): return free_vars(t.t1) | free_vars(t.t2)
    return set()

def apply_subst(subst: dict, t) -> Any:
    if isinstance(t, TVar):
        return apply_subst(subst, subst[t.name]) if t.name in subst else t
    if isinstance(t, TCon):
        return TCon(t.name, tuple(apply_subst(subst, a) for a in t.args))
    if isinstance(t, TFun):
        return TFun(apply_subst(subst, t.t1), apply_subst(subst, t.t2))
    return t

def compose_subst(s1: dict, s2: dict) -> dict:
    result = {k: apply_subst(s1, v) for k, v in s2.items()}
    result.update(s1)
    return result

class UnificationError(Exception): pass

def occurs_check(var_name: str, t) -> bool:
    """Return True if var_name appears in t (prevents infinite types)."""
    return var_name in free_vars(t)

def unify(t1, t2) -> dict:
    """
    Most General Unifier (MGU): find substitution S such that
    apply_subst(S, t1) == apply_subst(S, t2).
    """
    if t1 == t2:
        return {}  # no substitution needed — already equal

    if isinstance(t1, TVar):
        if occurs_check(t1.name, t2) and t2 != t1:
            raise UnificationError(f"Infinite type: {t1.name} occurs in {t2}")
        return {t1.name: t2}

    if isinstance(t2, TVar):
        return unify(t2, t1)  # symmetric: flip and try again

    if isinstance(t1, TFun) and isinstance(t2, TFun):
        s1 = unify(t1.t1, t2.t1)                           # unify parameter types
        s2 = unify(apply_subst(s1, t1.t2),                 # unify return types
                   apply_subst(s1, t2.t2))                  # (under s1)
        return compose_subst(s2, s1)

    if isinstance(t1, TCon) and isinstance(t2, TCon):
        if t1.name != t2.name or len(t1.args) != len(t2.args):
            raise UnificationError(f"Cannot unify {t1} with {t2}")
        s = {}
        for a1, a2 in zip(t1.args, t2.args):
            s = compose_subst(unify(apply_subst(s, a1), apply_subst(s, a2)), s)
        return s

    raise UnificationError(f"Cannot unify {t1} with {t2}")

# Tests
print("Unification tests:")
# 'a ~ Int => {'a: Int}
s = unify(TVar("a"), Int)
print(f"unify('a, Int) = {s}")

# 'a -> 'b ~ Int -> Bool => {'a: Int, 'b: Bool}
s = unify(TFun(TVar("a"), TVar("b")), TFun(Int, Bool))
print(f"unify('a->'b, Int->Bool) = {s}")

# ('a -> 'a) ~ (Int -> 'b) => {'a: Int, 'b: Int}
s = unify(TFun(TVar("a"), TVar("a")), TFun(Int, TVar("b")))
print(f"unify('a->'a, Int->'b) = {s}")

# Error: Int ~ Bool
try:
    unify(Int, Bool)
except UnificationError as e:
    print(f"unify(Int, Bool) => Error: {e}")

# Error: occurs check ('a ~ 'a -> Int would be infinite)
try:
    unify(TVar("a"), TFun(TVar("a"), Int))
except UnificationError as e:
    print(f"occurs check: {e}")

# Symmetry check
s_forward  = unify(TVar("a"), Int)
s_backward = unify(Int, TVar("a"))
print(f"\nunify('a, Int)  = {s_forward}")
print(f"unify(Int, 'a)  = {s_backward}")
print(f"Both yield same binding: {apply_subst(s_forward, TVar('a')) == apply_subst(s_backward, TVar('a'))}")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

##### Critical Thinking Questions

> **CTQ 3.1** When unifying `'a -> 'a` with `Int -> 'b`, the result is `{'a: Int, 'b: Int}`. Trace through the `unify` code step by step to verify this. Which recursive call is responsible for establishing `'b: Int`?

[[___ your answer here ___]]

> **CTQ 3.2** What is the "occurs check" and why is it necessary? What would `'a ~ ('a -> Int)` mean if we allowed it — sketch what the resulting "type" would look like if you tried to write it out fully.

[[___ your answer here ___]]

> **CTQ 3.3** "Most general unifier" means there is no substitution that is MORE general. Why is `{'a: Int}` a valid MGU for `unify('a, Int)` but `{}` (the empty substitution) is not a valid unifier for the same pair?

[[___ your answer here ___]]

> **CTQ 3.4** The code verifies that unification is symmetric. Run it and confirm both directions give equal results. Now think about `unify('a -> 'b, 'b -> 'a)`. Without running code, predict what the MGU should be. Then verify by adding it to the code block.

[[___ your answer here ___]]

---

#### Model 4: Algorithm W — Inferring Types for Expressions

##### A Hand Trace Before the Code

Before reading the implementation, here is a complete hand trace of Algorithm W on `let id = λx.x in id 42`. Follow it carefully — then check that the code produces the same result.

```
W(λx.x):
  fresh α₁                          -- create a new unknown type for parameter x
  extend env with {x : α₁}
  W(x) = (∅, α₁)                   -- x has type α₁ in env {x : α₁}
  return (∅, α₁ → α₁)              -- id takes α₁ and returns α₁

W(id 42):
  W(id) = (∅, α₁ → α₁)            -- look up id in the env (instantiated fresh)
  W(42) = (∅, Int)                  -- numeric literals are Int
  fresh α₂                          -- unknown result type of the application
  unify (α₁ → α₁) with (Int → α₂) -- function type must match argument + result
    → α₁ = Int,  α₂ = Int
  result type = apply subst to α₂ = Int

Final: let id = λx.x in id 42  :  Int
```

The `let` case adds one step: after inferring the type of the bound expression, `generalize` wraps any free type variables in a `forall`. That is what lets `id` be used at multiple types in a single program.

> **Watch out!** Let-polymorphism is what makes `let id = λx.x in (id 1, id True)` work. The `id` function gets a "forall" type `∀α.α→α`, so each use can instantiate α differently — one use at `Int`, another at `Bool`. Without `let`-polymorphism, `id` would be forced to a single concrete type the first time it is used, and the second use at a different type would be a type error.

Algorithm W assigns types to every expression. It takes a **type environment** Γ (mapping variable names to type schemes) and an expression, and returns a substitution + type. The environment grows as we encounter `let` bindings and lambda parameters. The substitution grows as we unify constraints. At the end, composing all the substitutions gives us the complete type assignment for the program.

```python  liascript
from dataclasses import dataclass
from typing import Any

# --- Type terms (same as before) ---
@dataclass(frozen=True)
class TVar:
    name: str
    def __str__(self): return f"'{self.name}"

@dataclass(frozen=True)
class TCon:
    name: str
    args: tuple = ()
    def __str__(self):
        if not self.args: return self.name
        return f"({self.name} {' '.join(str(a) for a in self.args)})"

@dataclass(frozen=True)
class TFun:
    t1: Any
    t2: Any
    def __str__(self): return f"({self.t1} -> {self.t2})"

Int  = TCon("Int")
Bool = TCon("Bool")

def free_vars(t) -> set:
    if isinstance(t, TVar): return {t.name}
    if isinstance(t, TCon): return set().union(*[free_vars(a) for a in t.args]) if t.args else set()
    if isinstance(t, TFun): return free_vars(t.t1) | free_vars(t.t2)
    return set()

def apply_subst(subst: dict, t) -> Any:
    if isinstance(t, TVar):
        return apply_subst(subst, subst[t.name]) if t.name in subst else t
    if isinstance(t, TCon):
        return TCon(t.name, tuple(apply_subst(subst, a) for a in t.args))
    if isinstance(t, TFun):
        return TFun(apply_subst(subst, t.t1), apply_subst(subst, t.t2))
    return t

def compose_subst(s1: dict, s2: dict) -> dict:
    result = {k: apply_subst(s1, v) for k, v in s2.items()}
    result.update(s1)
    return result

class UnificationError(Exception): pass

def occurs_check(var_name: str, t) -> bool:
    return var_name in free_vars(t)

def unify(t1, t2) -> dict:
    if t1 == t2: return {}
    if isinstance(t1, TVar):
        if occurs_check(t1.name, t2) and t2 != t1:
            raise UnificationError(f"Infinite type: {t1.name} occurs in {t2}")
        return {t1.name: t2}
    if isinstance(t2, TVar): return unify(t2, t1)
    if isinstance(t1, TFun) and isinstance(t2, TFun):
        s1 = unify(t1.t1, t2.t1)
        s2 = unify(apply_subst(s1, t1.t2), apply_subst(s1, t2.t2))
        return compose_subst(s2, s1)
    if isinstance(t1, TCon) and isinstance(t2, TCon):
        if t1.name != t2.name or len(t1.args) != len(t2.args):
            raise UnificationError(f"Cannot unify {t1} with {t2}")
        s = {}
        for a1, a2 in zip(t1.args, t2.args):
            s = compose_subst(unify(apply_subst(s, a1), apply_subst(s, a2)), s)
        return s
    raise UnificationError(f"Cannot unify {t1} with {t2}")

# --- Type Schemes ---
class TypeScheme:
    """A polymorphic type: forall vars. type"""
    def __init__(self, vars: list, t):
        self.vars = vars  # universally quantified type variables
        self.t = t
    def __str__(self):
        if not self.vars: return str(self.t)
        return f"forall {','.join(self.vars)}. {self.t}"

# --- AST nodes ---
@dataclass
class Num: value: float
@dataclass
class Bool_: value: bool
@dataclass
class Var: name: str
@dataclass
class Lam: param: str; body: Any   # lambda x. body
@dataclass
class App: func: Any; arg: Any     # func arg
@dataclass
class Let: name: str; val: Any; body: Any

# --- Fresh type variable generator ---
_counter = [0]
def fresh() -> TVar:
    _counter[0] += 1
    return TVar(f"t{_counter[0]}")

def instantiate(scheme: TypeScheme) -> Any:
    """Replace quantified variables with fresh type variables."""
    subst = {v: fresh() for v in scheme.vars}
    return apply_subst(subst, scheme.t)

def generalize(env: dict, t) -> TypeScheme:
    """Quantify over type variables that don't appear free in env."""
    env_free = set().union(*(free_vars(s.t) for s in env.values())) if env else set()
    quantified = free_vars(t) - env_free
    return TypeScheme(list(quantified), t)

def w(env: dict, expr) -> tuple:
    """Algorithm W: returns (substitution, type)"""
    if isinstance(expr, Num):
        return {}, Int
    if isinstance(expr, Bool_):
        return {}, Bool
    if isinstance(expr, Var):
        if expr.name not in env:
            raise TypeError(f"Unbound variable: {expr.name}")
        return {}, instantiate(env[expr.name])
    if isinstance(expr, Lam):
        tv = fresh()
        new_env = {**env, expr.param: TypeScheme([], tv)}
        s1, t1 = w(new_env, expr.body)
        return s1, TFun(apply_subst(s1, tv), t1)
    if isinstance(expr, App):
        tv = fresh()
        s1, t1 = w(env, expr.func)
        s2, t2 = w({k: TypeScheme(v.vars, apply_subst(s1, v.t)) for k, v in env.items()}, expr.arg)
        s3 = unify(apply_subst(s2, t1), TFun(t2, tv))
        return compose_subst(s3, compose_subst(s2, s1)), apply_subst(s3, tv)
    if isinstance(expr, Let):
        s1, t1 = w(env, expr.val)
        env1 = {k: TypeScheme(v.vars, apply_subst(s1, v.t)) for k, v in env.items()}
        scheme = generalize(env1, t1)
        new_env = {**env1, expr.name: scheme}
        s2, t2 = w(new_env, expr.body)
        return compose_subst(s2, s1), t2
    raise TypeError(f"Unknown expression type: {type(expr)}")

# --- Tests ---
base_env = {}

# Test 1: infer type of (lambda x. x)  =>  'a -> 'a
_counter[0] = 0
s, t = w(base_env, Lam("x", Var("x")))
print(f"lambda x. x : {t}")

# Test 2: (lambda x. x) 42  =>  Int
_counter[0] = 0
s, t = w(base_env, App(Lam("x", Var("x")), Num(42)))
print(f"(lambda x. x) 42 : {t}")

# Test 3: let id = lambda x. x in id 42  =>  Int
_counter[0] = 0
s, t = w(base_env, Let("id", Lam("x", Var("x")), App(Var("id"), Num(42))))
print(f"let id = lambda x. x in id 42 : {t}")

# Test 4: let id = lambda x. x in id True  =>  Bool
_counter[0] = 0
s, t = w(base_env, Let("id", Lam("x", Var("x")), App(Var("id"), Bool_(True))))
print(f"let id = lambda x. x in id True : {t}")

# Test 5: lambda f. lambda x. f x  =>  ('a -> 'b) -> 'a -> 'b
_counter[0] = 0
s, t = w(base_env, Lam("f", Lam("x", App(Var("f"), Var("x")))))
print(f"lambda f. lambda x. f x : {t}")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

##### Critical Thinking Questions

> **CTQ 4.1** When `w` processes `Lam("x", body)`, it creates a *fresh* type variable `tv` for the parameter `x`. Why does it need a fresh variable rather than reusing an existing type variable that might already be in scope?

[[___ your answer here ___]]

> **CTQ 4.2** For `App(func, arg)`, Algorithm W infers types for `func` and `arg` separately, then unifies `func`'s type with `TFun(t_arg, t_result)`. Why must `func`'s type be a function type for the application to type-check? What happens at the `unify` step if `func` is not a function?

[[___ your answer here ___]]

> **CTQ 4.3** `generalize` quantifies over free type variables in `t` that do NOT appear free in `env`. Why must we exclude variables that appear in `env`? Give a concrete example where including them would cause a type-safety violation.

[[___ your answer here ___]]

> **CTQ 4.4** The tests show `let id = λx.x in id 42` types to `Int` and `let id = λx.x in id True` types to `Bool`. In both cases, `id` has the polymorphic type `forall a. 'a -> 'a`. How does `instantiate` allow `id` to be used at different types in different calls?

[[___ your answer here ___]]

---

#### Model 5: Type Errors as Unification Failures

Type errors are not a separate mechanism — they are simply unification failures. When two types cannot be made equal, Algorithm W raises an error. Understanding *where* the failure occurs tells you exactly *what* the programmer did wrong.

```python  liascript
from dataclasses import dataclass
from typing import Any

# --- Infrastructure (same as Model 4) ---
@dataclass(frozen=True)
class TVar:
    name: str
    def __str__(self): return f"'{self.name}"

@dataclass(frozen=True)
class TCon:
    name: str
    args: tuple = ()
    def __str__(self):
        if not self.args: return self.name
        return f"({self.name} {' '.join(str(a) for a in self.args)})"

@dataclass(frozen=True)
class TFun:
    t1: Any
    t2: Any
    def __str__(self): return f"({self.t1} -> {self.t2})"

Int  = TCon("Int")
Bool = TCon("Bool")

def free_vars(t) -> set:
    if isinstance(t, TVar): return {t.name}
    if isinstance(t, TCon): return set().union(*[free_vars(a) for a in t.args]) if t.args else set()
    if isinstance(t, TFun): return free_vars(t.t1) | free_vars(t.t2)
    return set()

def apply_subst(subst: dict, t) -> Any:
    if isinstance(t, TVar):
        return apply_subst(subst, subst[t.name]) if t.name in subst else t
    if isinstance(t, TCon):
        return TCon(t.name, tuple(apply_subst(subst, a) for a in t.args))
    if isinstance(t, TFun):
        return TFun(apply_subst(subst, t.t1), apply_subst(subst, t.t2))
    return t

def compose_subst(s1: dict, s2: dict) -> dict:
    result = {k: apply_subst(s1, v) for k, v in s2.items()}
    result.update(s1)
    return result

class UnificationError(Exception): pass

def occurs_check(var_name: str, t) -> bool:
    return var_name in free_vars(t)

def unify(t1, t2) -> dict:
    if t1 == t2: return {}
    if isinstance(t1, TVar):
        if occurs_check(t1.name, t2) and t2 != t1:
            raise UnificationError(f"Infinite type: {t1.name} occurs in {t2}")
        return {t1.name: t2}
    if isinstance(t2, TVar): return unify(t2, t1)
    if isinstance(t1, TFun) and isinstance(t2, TFun):
        s1 = unify(t1.t1, t2.t1)
        s2 = unify(apply_subst(s1, t1.t2), apply_subst(s1, t2.t2))
        return compose_subst(s2, s1)
    if isinstance(t1, TCon) and isinstance(t2, TCon):
        if t1.name != t2.name or len(t1.args) != len(t2.args):
            raise UnificationError(f"Cannot unify {t1} with {t2}")
        s = {}
        for a1, a2 in zip(t1.args, t2.args):
            s = compose_subst(unify(apply_subst(s, a1), apply_subst(s, a2)), s)
        return s
    raise UnificationError(f"Cannot unify {t1} with {t2}")

class TypeScheme:
    def __init__(self, vars: list, t):
        self.vars = vars
        self.t = t
    def __str__(self):
        if not self.vars: return str(self.t)
        return f"forall {','.join(self.vars)}. {self.t}"

@dataclass
class Num: value: float
@dataclass
class Bool_: value: bool
@dataclass
class Var: name: str
@dataclass
class Lam: param: str; body: Any
@dataclass
class App: func: Any; arg: Any
@dataclass
class Let: name: str; val: Any; body: Any

_counter = [0]
def fresh() -> TVar:
    _counter[0] += 1
    return TVar(f"t{_counter[0]}")

def instantiate(scheme: TypeScheme) -> Any:
    subst = {v: fresh() for v in scheme.vars}
    return apply_subst(subst, scheme.t)

def generalize(env: dict, t) -> TypeScheme:
    env_free = set().union(*(free_vars(s.t) for s in env.values())) if env else set()
    quantified = free_vars(t) - env_free
    return TypeScheme(list(quantified), t)

def w(env: dict, expr) -> tuple:
    if isinstance(expr, Num):   return {}, Int
    if isinstance(expr, Bool_): return {}, Bool
    if isinstance(expr, Var):
        if expr.name not in env:
            raise TypeError(f"Unbound variable: {expr.name}")
        return {}, instantiate(env[expr.name])
    if isinstance(expr, Lam):
        tv = fresh()
        new_env = {**env, expr.param: TypeScheme([], tv)}
        s1, t1 = w(new_env, expr.body)
        return s1, TFun(apply_subst(s1, tv), t1)
    if isinstance(expr, App):
        tv = fresh()
        s1, t1 = w(env, expr.func)
        s2, t2 = w({k: TypeScheme(v.vars, apply_subst(s1, v.t)) for k, v in env.items()}, expr.arg)
        s3 = unify(apply_subst(s2, t1), TFun(t2, tv))
        return compose_subst(s3, compose_subst(s2, s1)), apply_subst(s3, tv)
    if isinstance(expr, Let):
        s1, t1 = w(env, expr.val)
        env1 = {k: TypeScheme(v.vars, apply_subst(s1, v.t)) for k, v in env.items()}
        scheme = generalize(env1, t1)
        new_env = {**env1, expr.name: scheme}
        s2, t2 = w(new_env, expr.body)
        return compose_subst(s2, s1), t2
    raise TypeError(f"Unknown expression: {type(expr)}")

# --- Build a richer test environment ---
test_env = {
    "add":    TypeScheme([], TFun(Int, TFun(Int, Int))),
    "not_":   TypeScheme([], TFun(Bool, Bool)),
    "iszero": TypeScheme([], TFun(Int, Bool)),
}

# Test 1: Well-typed: add 1 2  =>  Int
_counter[0] = 0
s, t = w(test_env, App(App(Var("add"), Num(1)), Num(2)))
print(f"add 1 2 : {t}")

# Test 2: Well-typed: not_ (iszero 0)  =>  Bool
_counter[0] = 0
s, t = w(test_env, App(Var("not_"), App(Var("iszero"), Num(0))))
print(f"not_ (iszero 0) : {t}")

# Test 3: Ill-typed: add True 1  =>  type error
_counter[0] = 0
try:
    s, t = w(test_env, App(App(Var("add"), Bool_(True)), Num(1)))
    print(f"add True 1 : {t}")
except (UnificationError, TypeError) as e:
    print(f"Type error in 'add True 1': {e}")

# Test 4: Partial application is FINE — add 5 has type Int -> Int
_counter[0] = 0
s, t = w(test_env, App(Var("add"), Num(5)))
print(f"\nadd 5 (partial application) : {t}")

# Test 5: Let polymorphism — id used twice at same type
_counter[0] = 0
program = Let("id", Lam("x", Var("x")),
              App(App(Var("add"),
                      App(Var("id"), Num(1))),
                  App(Var("id"), Num(2))))
s, t = w(test_env, program)
print(f"\nlet id = lambda x. x in add (id 1) (id 2) : {t}")

# Test 6: Applying a non-function  =>  type error
_counter[0] = 0
try:
    s, t = w(test_env, App(Num(42), Num(1)))
    print(f"42 1 : {t}")
except (UnificationError, TypeError) as e:
    print(f"\nType error in '42 1' (applying a non-function): {e}")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

##### Critical Thinking Questions

> **CTQ 5.1** `add True 1` fails because `True` has type `Bool` but `add` expects `Int`. Trace through the `App` case in Algorithm W to find the exact `unify` call that raises the error. Which two types are being unified when the error occurs?

[[___ your answer here ___]]

> **CTQ 5.2** `add 5` (partial application) succeeds with type `Int -> Int`. Why does applying a function to *too few* arguments not cause a type error? What would you have to do to trigger an arity-related error?

[[___ your answer here ___]]

> **CTQ 5.3** Test 5 uses `id` twice with `Int`. Modify the program so that `id` is used once with `Int` and once with `Bool` in the same `let` expression (for example, feed one result to `not_` and the other to `add`). Does it type-check? Why or why not?

[[___ your answer here ___]]

> **CTQ 5.4** What is the fundamental difference between a **type error** (caught by Algorithm W at compile time) and a **runtime error** (like division by zero)? Can type inference eliminate all possible program errors? If not, what can it and cannot it guarantee?

[[___ your answer here ___]]

---

#### Multiple Choice

Which answer best completes each statement?

What does the "occurs check" in unification prevent?

[[ (X) Infinite types like `'a = 'a -> Int`, which would cause non-termination during type inference ]]
[[ Circular variable references at runtime ]]
[[ Using the same type variable twice in the same expression ]]
[[ Polymorphism in recursive functions ]]

---

What does `generalize(env, t)` do that `TypeScheme([], t)` does not?

[[ (X) It universally quantifies free type variables in `t` that are not constrained by `env`, enabling let-polymorphism ]]
[[ It applies a substitution to make all type variables concrete ]]
[[ It checks whether `t` contains any type errors ]]
[[ It removes duplicate type variables from `t` ]]

---

"Most General Unifier" (MGU) means:

[[ The substitution with the fewest mappings ]]
[[ (X) The substitution that makes `t1 = t2` while leaving maximum generality — any other unifier can be obtained by composing the MGU with another substitution ]]
[[ The substitution that works for the most possible programs ]]
[[ The first substitution found by the algorithm, before any optimization ]]

---

In Haskell, `length :: [a] -> Int`. What does this tell you about Algorithm W?

[[ `length` was annotated manually by the programmer ]]
[[ `length` has no type, so Haskell uses dynamic typing here ]]
[[ (X) Algorithm W inferred a polymorphic type: `length` works for any list regardless of element type ]]
[[ `length` is a special built-in that bypasses the type system ]]

---

#### Exercises

**Exercise 1: Add `Plus` to the AST**

Add a `Plus` AST node that requires both arguments to be `Int` and returns `Int`. Extend `w` to handle it. Test both `Plus(Num(1), Num(2))` (should succeed with type `Int`) and `Plus(Num(1), Bool_(True))` (should fail with a type error naming `Bool` where `Int` was expected).

**Exercise 2: Add `If` to the AST**

Add `If(cond, then_e, else_e)` to the AST where `cond` must be `Bool` and both branches must have the same type. The resulting type is the type of either branch. Extend `w` to handle it. Test `If(Bool_(True), Num(1), Num(2))` (should succeed, type `Int`), `If(Num(1), Num(1), Num(2))` (should fail — condition is not `Bool`), and `If(Bool_(True), Num(1), Bool_(False))` (should fail — branches have different types).

**Exercise 3: Infer list literal types**

Implement `w_list(env, exprs)` that infers the type of a list literal: all elements must have the same type, and the result is `List[t]` for that common type. Use `TCon("List", (t,))` as the list type. Test `[Num(1), Num(2), Num(3)]` (should give `(List Int)`) and `[Num(1), Bool_(True), Num(3)]` (should fail — elements have different types).

**Exercise 4: Pretty-print inferred types**

Write a `typeof_expr(expr, env=None) -> str` function that calls Algorithm W on an expression and returns a clean, human-readable string for the inferred type. Normalize type variable names to alphabetical order (`'a`, `'b`, `'c`, ...) rather than `'t1`, `'t2`, etc. Test it on at least three examples from Models 4 and 5.

---

#### Reflection

> In your notebook: Hindley-Milner type inference was published in 1978. Before it, type systems required programmers to annotate every variable and function parameter. After it, Haskell, ML, OCaml, Rust, and many others could infer types automatically throughout entire programs. What did this change about the *experience* of programming in those languages? And what are the limits — when can HM inference fail, produce confusing error messages, or require annotations after all?

---

#### Further Reading

- Damas & Milner (1982) "Principal type-schemes for functional programs" — the original Algorithm W paper
- This course's Type Inference Tutorial — goes deeper on each phase of the algorithm
- This course's Type Inference Assignment — build the full system yourself
- Pierce, "Types and Programming Languages," Chapter 22 — Reconstruction
- Diehl, "Write You a Haskell" — implements HM in Haskell, for Haskell

---

---

## Going Deeper: Data Structures and Generics in Programming Languages

This activity examines data structures from a language-design perspective — not just how to use them, but how different languages provide, constrain, and reason about them. We will ask: what does a type system *guarantee* about a container, and at what cost? By tracing the same ideas (a stack, a linked list, a union of shapes) through increasingly precise type machinery, you will see how language designers make deliberate trade-offs between flexibility and safety.

#### Learning Goals

By the end of this activity, you will be able to:

- Distinguish polymorphic, generic, and monomorphic container types and explain when each is appropriate in a statically typed language
- Implement parametric generic classes in Python using type variables and explain how the type checker verifies them without requiring separate implementations per type
- Construct algebraic data types (product and sum types) and use pattern matching to exhaustively handle all cases
- Define recursive data structures (linked lists, binary trees) and implement recursive algorithms over them
- Compare structural and nominal type compatibility and evaluate how each approach affects code reuse and type safety

Every nontrivial program keeps collections of values — but *which* values, and enforced *how*? This activity walks from Python's fully polymorphic built-in containers through typed generic classes, algebraic data types, recursive structures, and finally the structural-versus-nominal typing divide. The arc: **polymorphic containers → parametric generics → product and sum types → recursive types → structural typing via Protocols**.

> **Before You Begin — Prerequisites**
>
> This activity assumes you are comfortable with:
>
> - **Python lists, dicts, and classes** — you can write a class with `__init__`, instance variables, and methods without consulting documentation.
> - **Immutability** — you understand the difference between a mutable object (one you can change in-place) and an immutable one (one that cannot be changed after creation), and why the distinction matters for reasoning about program state.
> - **Basic recursion with trees** — you can trace a recursive function that walks a binary tree and identify the base case and the recursive case.
>
> If any of these feel shaky, spend 10–15 minutes reviewing them before the activity — each Model builds on the previous one.

---

#### Directions and Group Roles

Work in your POGIL team with rotated roles (**Manager**, **Recorder**, **Presenter**, **Reflector**). Consider each model and question individually first, then discuss with your group. The Recorder posts answers to the Class Activity Questions discussion board; the Presenter reports out areas of disagreement or alternative approaches. After class, respond to the reflective prompt individually in your notebook.

---

### Part I: Collections and Polymorphism

#### Model 1: Built-in Collections and Polymorphism

Before we impose any type constraints, it helps to see what Python gives us by default: containers that will hold *anything*. A Python `list` does not care whether you put integers, strings, or other lists inside it. This maximum flexibility is convenient, but it shifts every responsibility for correctness to runtime — the language will not warn you if you accidentally mix types in a list that was supposed to be all numbers. As you read this model, ask yourself: what does the programmer gain from Python's permissiveness, and what would a stricter language's type checker catch?

Python's four built-in collection types — `list`, `dict`, `set`, `tuple` — are **polymorphic**: each can hold values of any type, including a mix of types in a single container. A **homogeneous** collection stores one type throughout; a **heterogeneous** collection mixes types. Both are possible in Python, but only homogeneous collections are typical in statically typed languages without generics.

```python
# Python built-in collections: fully polymorphic

# Heterogeneous list — holds any type
mixed = [42, "hello", 3.14, True, None, [1, 2]]
print("=== Heterogeneous list ===")
for item in mixed:
    print(f"  {item!r:20}  type: {type(item).__name__}")

# isinstance for type testing
print("\n=== isinstance checks ===")
print(f"mixed[0] is int:  {isinstance(mixed[0], int)}")
print(f"mixed[1] is str:  {isinstance(mixed[1], str)}")
print(f"mixed[3] is bool: {isinstance(mixed[3], bool)}")
# Note: bool is a subclass of int in Python
print(f"mixed[3] is int:  {isinstance(mixed[3], int)}  (bool is a subclass of int!)")

# Homogeneous list — conventional, tools can reason about it
ints:   list[int]   = [1, 2, 3, 4, 5]
words:  list[str]   = ["alpha", "beta", "gamma"]
print(f"\nints sum:  {sum(ints)}")
print(f"words joined: {', '.join(words)}")

# dict as key-value store
inventory: dict[str, int] = {"apples": 5, "bananas": 3, "cherries": 12}
print("\n=== dict (key-value store) ===")
for key, val in inventory.items():
    print(f"  {key}: {val}")
inventory["dates"] = 7
print(f"After insertion: {inventory}")

# set operations
evens = {2, 4, 6, 8, 10}
primes = {2, 3, 5, 7, 11}
print("\n=== set operations ===")
print(f"union:        {evens | primes}")
print(f"intersection: {evens & primes}")
print(f"difference:   {evens - primes}")
print(f"symmetric diff: {evens ^ primes}")

# tuple — immutable, fixed structure
point: tuple[float, float] = (3.0, 4.0)
x, y = point
print(f"\npoint = {point},  distance from origin = {(x**2 + y**2)**0.5:.4f}")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

##### Critical Thinking Questions

1. What does it mean to call a container **polymorphic**? In your own words, contrast Python's `list` with Java's `int[]`.
2. What is the difference between a **homogeneous** and a **heterogeneous** collection? Give a real-world scenario in which you would deliberately want each.
3. The code shows that `isinstance(True, int)` returns `True`. Why is this the case in Python's type hierarchy? Does this surprise you? What problems could it cause in a type checker?
4. `dict`, `set`, and `tuple` each enforce a different structural constraint (ordered key-value pairs, unique elements, immutable sequence). Which of these constraints is enforced statically (at definition) versus dynamically (at runtime), and why?
5. A `set` requires elements to be **hashable**. What does that mean, and which of the types in `mixed` above are not hashable? Verify your prediction by trying to construct a set containing a list.

---

### Part II: Parametric Polymorphism

#### Model 2: Generics and Parametric Polymorphism

Now we add *one* constraint: a container should hold a single consistent type, and the type checker should enforce that. The key insight is that we want to write the algorithm once — not once for `int` and again for `str` — but still get the safety guarantee. **Parametric polymorphism** is the language-design mechanism that achieves both goals simultaneously. Think of `T` as a blank that gets filled in when someone creates a `Stack[int]` or `Stack[str]`; the algorithm is identical, but the type checker now knows which blank was filled.

**Parametric polymorphism** means a class or function can be *parameterized by a type*: `Stack[int]` and `Stack[str]` are the same algorithm but specialized to different element types. Python's `typing` module provides `TypeVar` and `Generic[T]` to express this. At runtime Python erases the type parameter (**type erasure**), but static checkers like mypy and pyright use it to catch mismatches before execution.

> **Watch out! — Type erasure is not a bug, it is a design choice.** When Python runs your `Stack[int]`, it does not keep a record that the type parameter was `int`; there is simply a `Stack`. This means you cannot write `if T is int:` inside a generic method and expect it to work at runtime. The type annotation exists *only* for the static checker. Languages like C++ take the opposite approach (reification / monomorphization): every instantiation `stack<int>` becomes a distinct compiled type, which enables runtime introspection but increases compile time and binary size. Neither approach is universally better — the choice reflects the language's overall philosophy about when and where to pay costs.

```python
from typing import TypeVar, Generic, Optional

T = TypeVar('T')

class Stack(Generic[T]):
    def __init__(self) -> None:
        self._items: list[T] = []

    def push(self, item: T) -> None:
        self._items.append(item)

    def pop(self) -> Optional[T]:
        if self._items:
            return self._items.pop()
        return None

    def peek(self) -> Optional[T]:
        return self._items[-1] if self._items else None

    def is_empty(self) -> bool:
        return len(self._items) == 0

    def __len__(self) -> int:
        return len(self._items)

    def __repr__(self) -> str:
        return f"Stack({self._items})"

# Type-annotated usage: Stack[int]
int_stack: Stack[int] = Stack()
int_stack.push(1)
int_stack.push(2)
int_stack.push(3)
print("=== Stack[int] ===")
print(f"Stack: {int_stack}")
print(f"Size:  {len(int_stack)}")
print(f"Peek:  {int_stack.peek()}")
print(f"Pop:   {int_stack.pop()}")
print(f"After pop: {int_stack}")

# Stack[str] — same implementation, different element type
str_stack: Stack[str] = Stack()
str_stack.push("hello")
str_stack.push("world")
str_stack.push("!")
print("\n=== Stack[str] ===")
print(f"Stack: {str_stack}")
print(f"Top:   {str_stack.peek()}")
while not str_stack.is_empty():
    print(f"  popped: {str_stack.pop()!r}")

# At runtime, both are the same class — type erasure in action
print(f"\ntype(int_stack) is type(str_stack): {type(int_stack) is type(str_stack)}")
print(f"Both are Stack: {isinstance(int_stack, Stack) and isinstance(str_stack, Stack)}")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

##### Critical Thinking Questions

6. What is `T` called, and what role does it play in the definition of `Stack`? How is it different from a concrete type like `int`?
7. The annotation `Stack[int]` signals intent to a static checker, but the final `print` shows that at runtime `type(int_stack) is type(str_stack)`. What does this tell you about **type erasure**? What safety does the annotation still provide?
8. In a language like Java, `Stack<Integer>` and `Stack<String>` are also the same class at runtime (Java also erases). In C++, `std::stack<int>` and `std::stack<std::string>` generate *separate compiled code*. What are the trade-offs of each approach (code size, performance, error messages)?
9. The `Optional[T]` return type on `pop` encodes the possibility of an empty stack. What is the alternative design (raising an exception)? Which is more *composable* in a functional style?
10. Suppose a static checker flags `int_stack.push("oops")`. Where in the pipeline does this error fire relative to type erasure? What does this imply about when generic type annotations are useful?

---

### Part III: Algebraic Data Types

#### Model 3: Algebraic Data Types — Product and Sum Types

So far our containers have been homogeneous: all elements are the same type. But many real-world values naturally come in distinct shapes — a payment is either a credit card charge *or* a bank transfer *or* a cash payment, never all three at once. **Algebraic data types** let us encode that "one of these shapes" constraint directly in the type, so the type checker can tell us when we have forgotten to handle a case. The word "algebraic" comes from the analogy: combining types with "and" (product) or "or" (sum) mirrors how algebraic expressions combine numbers with multiplication and addition.

> **Watch out! — Sum types encode exclusivity in the type system.** A `Union[Circle, Rectangle, Triangle]` does not mean a value can be all three simultaneously — it means it is *exactly one* of them at any given moment. This exclusivity is what makes exhaustive pattern matching possible: if you handle all three cases and the type system guarantees no fourth case exists, the checker can confirm your function is complete. Languages like Rust (`enum`), Haskell (algebraic data types), and Kotlin (`sealed class`) can enforce this at compile time; Python's `Union` relies on the programmer (and a static checker) to maintain the discipline.

**Algebraic data types** (ADTs) come in two flavors:

- A **product type** requires *all* its fields simultaneously — it is the Cartesian product of its component types. `Circle(radius=5.0)` must have a `radius`; there is no partial `Circle`.
- A **sum type** (also called a **variant** or **union**) holds *exactly one* of several alternatives. `Shape` is a `Circle` **or** a `Rectangle` **or** a `Triangle` — never two at once.

Python's `dataclass` gives product types; `Union` gives sum types. The combination is powerful enough to model most domain entities precisely.

```python
from dataclasses import dataclass
from typing import Union
import math

# Product types: every field is required simultaneously
@dataclass
class Circle:
    radius: float

@dataclass
class Rectangle:
    width: float
    height: float

@dataclass
class Triangle:
    base: float
    height: float

# Sum type: a Shape is exactly ONE of the three alternatives
Shape = Union[Circle, Rectangle, Triangle]

def area(shape: Shape) -> float:
    """Pattern-match on the shape's runtime type."""
    if isinstance(shape, Circle):
        return math.pi * shape.radius ** 2
    elif isinstance(shape, Rectangle):
        return shape.width * shape.height
    elif isinstance(shape, Triangle):
        return 0.5 * shape.base * shape.height
    else:
        raise ValueError(f"Unknown shape type: {type(shape).__name__}")

def perimeter(shape: Shape) -> float:
    if isinstance(shape, Circle):
        return 2 * math.pi * shape.radius
    elif isinstance(shape, Rectangle):
        return 2 * (shape.width + shape.height)
    elif isinstance(shape, Triangle):
        # For a right triangle with given base and height
        hyp = math.sqrt(shape.base ** 2 + shape.height ** 2)
        return shape.base + shape.height + hyp
    else:
        raise ValueError(f"Unknown shape type: {type(shape).__name__}")

shapes: list[Shape] = [
    Circle(5.0),
    Rectangle(3.0, 4.0),
    Triangle(6.0, 8.0),
]

print(f"{'Shape':<25} {'Area':>10} {'Perimeter':>12}")
print("-" * 50)
for s in shapes:
    name = type(s).__name__
    print(f"{name:<25} {area(s):>10.4f} {perimeter(s):>12.4f}")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

##### Critical Thinking Questions

11. Explain why `Circle` is a **product type**: what does "product" mean here, and what constraint does it place on construction?
12. Explain why `Shape` is a **sum type**: what does "sum" mean here? How many values can a single `Shape` variable contain simultaneously?
13. What happens if you add a new variant — say `@dataclass class Pentagon: sides: float` — to `Shape` but forget to add a branch to `area()`? Trace what Python does. How would a **sealed sum type** in a language like Rust, Haskell, or Kotlin prevent this mistake at compile time?
14. The `else: raise ValueError` branch in `area` is defensive programming against a case the type system claims cannot happen. Should it be there? What does its presence say about the gap between Python's runtime and its static type annotations?
15. Dataclasses generate `__eq__` and `__repr__` automatically. What other "free" operations could a language derive from a product type's structure? (Hint: think serialization, copying, hashing.)

---

### Part IV: Recursive Data Structures

#### Model 4: Recursive Data Structures — A Generic Linked List

Generics and ADTs gave us better ways to describe *what* a container holds. Now we turn to *how the container is structured*. A linked list is perhaps the simplest example of a data structure that is defined in terms of itself: a list is either empty, or it is a value followed by another list. This self-referential definition is not a quirk — it is the natural match between recursive structure and recursive algorithms. As you read the code, notice that the shape of the recursive type mirrors the shape of every recursive function that operates on it.

> **Watch out! — The linked list is the canonical functional data structure because prepending is O(1) without mutation.** To prepend a value, you create one new node pointing to the existing list — the existing list is unchanged. This means two different variables can safely share the same tail without either one affecting the other. In a purely functional language like Haskell or Clojure, this property (called **structural sharing**) is the foundation of efficient **persistent data structures**: instead of copying an entire collection when you "modify" it, you create a new version that shares as much structure as possible with the old one. Python's `list` does not share structure this way — `.insert(0, x)` copies all existing elements — so functional patterns map most naturally onto linked structures, not Python arrays.

A **recursive data type** is one that refers to itself in its own definition: `Node[T]` has a `value: T` and a `next` which is either another `Node[T]` or `None`. This is the canonical example of a **sum type inside a product type**: each node simultaneously holds a value (product) *and* is one of "has a next node" or "is the last node" (sum / `Optional`).

```python
from __future__ import annotations
from typing import TypeVar, Generic, Optional

T = TypeVar('T')

class Node(Generic[T]):
    def __init__(self, value: T, next: Optional[Node[T]] = None) -> None:
        self.value: T = value
        self.next: Optional[Node[T]] = next

    def __repr__(self) -> str:
        return f"Node({self.value!r})"

class LinkedList(Generic[T]):
    def __init__(self) -> None:
        self.head: Optional[Node[T]] = None
        self._size: int = 0

    def prepend(self, value: T) -> None:
        """Add to front in O(1)."""
        self.head = Node(value, self.head)
        self._size += 1

    def append(self, value: T) -> None:
        """Add to back in O(n)."""
        new_node: Node[T] = Node(value)
        if self.head is None:
            self.head = new_node
        else:
            current = self.head
            while current.next is not None:
                current = current.next
            current.next = new_node
        self._size += 1

    def to_list(self) -> list[T]:
        result: list[T] = []
        current = self.head
        while current is not None:
            result.append(current.value)
            current = current.next
        return result

    def contains(self, value: T) -> bool:
        current = self.head
        while current is not None:
            if current.value == value:
                return True
            current = current.next
        return False

    def __len__(self) -> int:
        return self._size

    def __repr__(self) -> str:
        return " -> ".join(str(v) for v in self.to_list()) + " -> None"

# Build a LinkedList[int]
lst: LinkedList[int] = LinkedList()
for i in [5, 4, 3, 2, 1]:
    lst.prepend(i)

print("=== LinkedList[int] (prepend order) ===")
print(f"List:     {lst}")
print(f"Size:     {len(lst)}")
print(f"Contains 3: {lst.contains(3)}")
print(f"Contains 9: {lst.contains(9)}")

# Build a LinkedList[str]
words: LinkedList[str] = LinkedList()
for w in ["the", "quick", "brown", "fox"]:
    words.append(w)

print("\n=== LinkedList[str] (append order) ===")
print(f"List:     {words}")
print(f"Size:     {len(words)}")
print(f"as list:  {words.to_list()}")

# Node structure visible
print("\n=== Node internals ===")
current = lst.head
depth = 0
while current is not None:
    print(f"  depth {depth}: Node(value={current.value}, next={current.next})")
    current = current.next
    depth += 1
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

##### Critical Thinking Questions

16. Why does `Node` use `Optional[Node[T]]` for `next` rather than just `Node[T]`? What would happen if you tried to construct the last node without `Optional`?
17. What is the **base case** of this recursive type? In other words, what terminates the chain, and how is it represented in the type?
18. Trace how the type parameter `T` flows: if you write `LinkedList[int]`, what type does `self.head` have? What type does `current.value` have inside `to_list`? Does Python actually enforce this at runtime?
19. `prepend` is O(1) and `append` is O(n). Why? Sketch a modification (a `tail` pointer) that would make `append` O(1), and describe what invariant you must maintain.
20. The `from __future__ import annotations` at the top is required for `Optional[Node[T]]` to work inside `Node`'s own definition. Why? What problem does it solve? (Hint: think about when Python evaluates type annotations.)

---

### Part V: Structural vs Nominal Typing

#### Model 5: Structural vs Nominal Typing and Protocols

The previous models all concerned what a container *holds*. This final model concerns a different question: how does the type system decide whether one type is *compatible* with another? Two classes that have the same methods but no shared parent — should a function that accepts one also accept the other? The answer depends on whether the language uses **nominal** or **structural** typing, and it has large practical consequences for how libraries are composed and how independently written code can interoperate.

Two philosophies govern whether a type "fits" where another is expected:

- **Nominal typing**: a type fits because you *declared* it belongs (via inheritance or `implements`). Java's `class Circle implements Drawable` is required; the compiler checks the declaration chain.
- **Structural typing** (duck typing): a type fits because it *has the right shape* — the necessary attributes and methods exist. Python's `Protocol` formalizes this: any class that provides the required methods satisfies the protocol, with no explicit declaration.

`@runtime_checkable` lets you use `isinstance` to test protocol conformance at runtime.

```python
from typing import Protocol, runtime_checkable
import math

@runtime_checkable
class Drawable(Protocol):
    def draw(self) -> str: ...
    def area(self) -> float: ...

# Neither class inherits from Drawable or from any shared base class.
# They satisfy the protocol purely by having the right methods.

class Circle:
    def __init__(self, r: float) -> None:
        self.r = r

    def draw(self) -> str:
        return f"Circle(r={self.r})"

    def area(self) -> float:
        return math.pi * self.r ** 2

class Square:
    def __init__(self, s: float) -> None:
        self.s = s

    def draw(self) -> str:
        return f"Square(s={self.s})"

    def area(self) -> float:
        return self.s ** 2

class Triangle:
    def __init__(self, base: float, height: float) -> None:
        self.base = base
        self.height = height

    def draw(self) -> str:
        return f"Triangle(base={self.base}, height={self.height})"

    def area(self) -> float:
        return 0.5 * self.base * self.height

# A class that is missing one required method — does NOT satisfy Drawable
class NotDrawable:
    def draw(self) -> str:
        return "I exist"
    # No area() method

def render_all(shapes: list[Drawable]) -> None:
    for shape in shapes:
        print(f"  {shape.draw():<35}  area={shape.area():.4f}")

shapes: list[Drawable] = [Circle(3.0), Square(4.0), Triangle(5.0, 6.0)]

print("=== Structural typing via Protocol ===")
render_all(shapes)

print("\n=== isinstance checks against Protocol ===")
for obj in [Circle(1.0), Square(2.0), NotDrawable(), "a string", 42]:
    result = isinstance(obj, Drawable)
    print(f"  {type(obj).__name__:<15} is Drawable: {result}")

# Nominal equivalent would require:
#   class Circle(Drawable): ...
# Instead, Python checks structure at the isinstance call.
print("\n=== MRO: no Drawable in the chain ===")
print(f"Circle MRO: {[c.__name__ for c in Circle.__mro__]}")
print(f"Square MRO: {[c.__name__ for c in Square.__mro__]}")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

##### Critical Thinking Questions

21. Do `Circle` and `Square` inherit from `Drawable`? Check the MRO output. Yet `isinstance(circle, Drawable)` returns `True`. Explain why.
22. In Java, to achieve the same effect you would write `class Circle implements Drawable`. What does that declaration cost you (coupling, compile-time checking, file organization)? What does Python's structural approach cost you in return?
23. `NotDrawable` has `draw` but not `area`. How does `isinstance(NotDrawable(), Drawable)` respond, and why? What does this tell you about the granularity of Protocol checking?
24. Structural typing is sometimes called **duck typing** ("if it walks like a duck and quacks like a duck, it is a duck"). Name one situation where duck typing is a significant advantage over nominal typing, and one where it is a significant disadvantage.
25. The `...` (Ellipsis) in `def draw(self) -> str: ...` is a body placeholder. How is this different from `pass`? When would you use each?

---

### Part VI: Multiple Choice

[[MC]]
What is parametric polymorphism?
- (x) A type or function can be parameterized by another type (e.g., `Stack[T]`)
- ( ) A function has multiple implementations selected by argument types at runtime
- ( ) A subtype can be used wherever a supertype is expected
- ( ) Types are checked only at runtime

[[MC]]
In Python's `typing` module, `Union[Circle, Rectangle, Triangle]` represents:
- ( ) A class that inherits from all three types simultaneously
- (x) A sum type — a value that is exactly one of the listed alternatives
- ( ) A product type combining all three types' fields
- ( ) A generic type parameterized by three TypeVars

[[MC]]
Type erasure means:
- ( ) Type annotations are removed from source code before compilation
- ( ) A type can be cast to a different type at runtime
- (x) Generic type parameters exist only at the static-checking level and are unavailable at runtime
- ( ) The garbage collector removes unused type objects from memory

[[MC]]
In structural typing via `Protocol`, `isinstance(obj, MyProtocol)` returns `True` when:
- ( ) `obj`'s class explicitly inherits from `MyProtocol`
- ( ) `obj`'s class is registered with `MyProtocol.register()`
- (x) `obj`'s class provides all the methods and attributes required by `MyProtocol`
- ( ) `obj` is of exactly the same type as `MyProtocol`

---

### Part VII: Exercises

#### 3. Exercises

1. *Generic `Queue[T]`.* Implement a `Queue` class using `Generic[T]` with `enqueue(item: T) -> None`, `dequeue() -> Optional[T]`, `front() -> Optional[T]`, and `__len__`. Instantiate both a `Queue[int]` and a `Queue[str]`, verify that they work correctly, and confirm that at runtime both are instances of the same `Queue` class (type erasure).

2. *Binary tree `BTree[T]`.* Implement a `BTree` generic class with `insert(value: T) -> None` (BST insertion using `<` ordering) and `inorder() -> list[T]` (in-order traversal). Demonstrate with `BTree[int]` and `BTree[str]`. What constraint must `T` satisfy for `<` to be defined? How would you express that constraint using a `Protocol`?

3. *`Result[T, E]` ADT.* Implement a `Result` type that is either `Ok(value: T)` or `Err(error: E)` — a sum type representing success or failure. Add a `map(f) -> Result` method that applies `f` to the value if `Ok`, or passes `Err` through unchanged. Show that `Result` chains let you compose several operations that might fail without any explicit `try`/`except` at each step.

4. *`Comparable` Protocol and generic sort.* Define a `Comparable` Protocol requiring `__lt__(self, other: Any) -> bool`. Write a generic function `insertion_sort(items: list[C]) -> list[C]` (where `C` is a `TypeVar` bound to `Comparable`) that sorts any list of `Comparable` items. Verify with lists of `int`, `str`, and a custom `Card` dataclass that implements `__lt__` by rank.

---

#### Reflection Prompt

In your notebook: both generics and dynamic typing allow a single function or class to work with many types — but they do so in very different ways. Generics express the constraint *statically*, before any value exists; dynamic typing defers the question until a value is actually used. Describe a scenario where catching a type mismatch before the program runs would have saved significant debugging time, and a scenario where dynamic flexibility genuinely made the code simpler. Which approach does your project's language take, and what does that choice imply for the users of your language?

---

#### 4. Further Reading

- Python Software Foundation. "typing — Support for type hints." *Python 3 Documentation*, docs.python.org/3/library/typing.html.
- Jukka Lehtosalo et al. *Mypy: Optional Static Typing for Python*, mypy.readthedocs.io.
- Benjamin C. Pierce. *Types and Programming Languages*, Chapter 22: Type Reconstruction, and Chapter 23: Universal Types. MIT Press, 2002.
- Simon Peyton Jones. "Haskell's Type Classes vs Python's Protocols." (Compare structural Protocol typing with Haskell's nominally-declared type classes for a sharp contrast.)
- Alexis King. "Parse, don't validate." *Lexi Lambda Blog*, 2019. (A practical argument for ADTs and sum types as the right tool for data modelling.)

---

## Going Deeper: Gradual Typing: Between Static and Dynamic

Static typing catches errors at compile time but demands up-front annotations for every value; dynamic typing runs without annotations but lets bugs hide until runtime. Gradual typing is the pragmatic middle ground — like a building code that mandates inspections only in the load-bearing walls while leaving interior decoration to the owner's discretion. Languages such as TypeScript, mypy-annotated Python, and Typed Racket all make this bet, and the theory behind it is surprisingly deep.

#### Learning Goals

By the end of this activity, you will be able to:

- Define gradual typing and explain how the unknown type `?` bridges statically-typed and dynamically-typed code
- Identify the consistency relation between types and distinguish it from type equality and subtyping
- Implement a bidirectional type checker that accepts gradually-typed programs and inserts runtime casts at typed/untyped boundaries
- Analyze blame assignment at static/dynamic boundaries and determine which component (caller or callee) is responsible for a cast failure
- Evaluate the correctness guarantees a gradually-typed language can and cannot provide compared to fully static or fully dynamic typing

> **Before You Begin:** This activity assumes you can:
> - Explain the difference between static and dynamic typing with a concrete example in at least one language
> - Read and write basic Python type annotations (`int`, `str`, `List[int]`, `Optional[str]`)
> - Trace through a simple recursive Python function and predict its output
>
> If any of these feel shaky, review them first.

Real-world languages rarely commit fully to either end of the static/dynamic spectrum. TypeScript adds optional types to JavaScript. mypy adds optional types to Python. Dart, Hack (PHP), and Typed Racket all make the same bet: let programmers annotate where they care about correctness, leave the rest unchecked, and insert runtime guards at the boundaries. The theory behind this approach — **gradual typing** — was formalized by Siek and Taha in 2006. It is not simply "some types, sometimes." It is a precise design with a formal consistency relation, a blame calculus for tracking contract violations, and deep consequences for what your language can and cannot guarantee.

Today you will move from pure dynamic typing (Model 1) through optional annotations (Model 2), implement a mini bi-directional type checker with a gradual consistency relation (Model 3), track blame at typed/untyped boundaries (Model 4), and wire a runtime type-checking interpreter that enforces annotated boundaries while leaving unannotated code free (Model 5).

---

#### Directions and Group Roles

Work in your POGIL team with rotated roles (**Manager**, **Recorder**, **Presenter**, **Reflector**). The Recorder maintains a running glossary: every bolded term introduced is a potential exam definition. The Presenter should be prepared to walk another group through the `consistent` relation in Model 3 and explain why it is not transitive. After class, complete the reflection prompt individually in your course journal.

Each model builds on the last. Do not skip ahead.

---

#### Model 1: Python's Dynamic Types in Action

Before you can appreciate the value of types, you need to feel the pain of their absence. This model shows Python at its most flexible — a single function serving wildly different argument types — and at its most hazardous, where the error only surfaces deep at runtime. Keep track of when you first know something has gone wrong versus when the program tells you.

Python is dynamically typed: there are no type annotations required, and the interpreter never checks types until it actually tries an operation. The same function can receive an `int`, a `str`, or a `list` — and it will cheerfully proceed with whichever it gets. This flexibility is genuinely useful. It is also the source of some of the hardest-to-find bugs in large codebases.

The model below shows how a single function can be called correctly and incorrectly, with the error appearing only at the moment the operation is attempted — which may be thousands of calls deep in production.

```python  liascript
def double(x):
    return x + x

print(double(5))        # 10  -- works
print(double("ha"))     # "haha" -- also works!
print(double([1,2]))    # [1,2,1,2] -- unexpected but valid

# The hazard: runtime surprises
def add_one(x):
    return x + 1

try:
    print(add_one("hello"))   # TypeError at runtime
except TypeError as e:
    print(f"Runtime error: {e}")

print("Program continues after the try/except")
# In a large codebase, this error might happen deep in production
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

> **Watch out!** `double("ha")` succeeds because `+` on strings means concatenation, not addition. Python does not check intent — it checks capability. The function works for strings, lists, and integers for completely different reasons. This is duck typing in action, and it can make unit tests deceptively quiet.

##### Critical Thinking Questions

**CTQ 1.** Which call to `double` do you think the programmer intended when they wrote the function? What clue in the function body suggests one interpretation over another?

[[___ your answer here ___]]

**CTQ 2.** The error in `add_one("hello")` only appears at runtime. Imagine this call is buried inside a library function invoked after reading a configuration file at startup. At what point does the programmer learn about the error? In a 100,000-line codebase, what makes this harder to debug than a compile-time error?

[[___ your answer here ___]]

**CTQ 3.** Python chose to allow `double("ha")` even though the programmer almost certainly wrote `double` for numbers. Name one **language design advantage** of this choice (think: code reuse, expressiveness) and one **language design disadvantage** (think: documentation, correctness guarantees).

[[___ your answer here ___]]

**CTQ 4.** The `try/except` block catches the `TypeError` and lets the program continue. Is this always the right thing to do? Describe a situation where catching and continuing is appropriate and a situation where it would silently corrupt a computation.

[[___ your answer here ___]]

---

#### Model 2: Type Annotations — Python's Optional Types (mypy-style)

Type annotations in Python are like sticky notes on a whiteboard: they communicate intent clearly to anyone reading the code, but the whiteboard does not enforce them — a different tool (mypy, pyright) must play that enforcement role. This model introduces the annotation vocabulary and forces you to notice the key surprise: Python runs annotated code with zero enforcement at runtime.

Python 3.5 introduced **type hints** via PEP 484. They are syntactically legal in the language, stored in `__annotations__`, and available to external tools — but Python itself **ignores them completely at runtime**. The enforcement is delegated to an optional static checker such as `mypy`. This is the essential design choice of gradual typing: annotation is voluntary, checking is opt-in, and the runtime is unchanged.

The model below covers the core of Python's annotation vocabulary: base types, `Optional`, `Union`, `List`, and `Callable`. A type checker running over this code would flag exactly one line. The interpreter will not.

```python  liascript
from typing import List, Optional, Union, Callable

# Type annotations are hints -- Python ignores them at runtime
def add_one(x: int) -> int:
    return x + 1

def greet(name: str) -> str:
    return f"Hello, {name}!"

def first(lst: List[int]) -> Optional[int]:
    return lst[0] if lst else None

# Union type: accepts int or float
def square(x: Union[int, float]) -> float:
    return float(x * x)

# Higher-order: function that takes a function
def apply_twice(f: Callable[[int], int], x: int) -> int:
    return f(f(x))

# These are all CORRECT by the type signatures
print(add_one(5))
print(greet("Alice"))
print(first([1, 2, 3]))
print(square(3))
print(apply_twice(add_one, 10))

# Python does not enforce at runtime -- this still runs:
result = add_one("hello")  # a type checker would flag this
print(f"Sneaked through: {type(result)}")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

> **Watch out!** Python type annotations are **not** enforced at runtime. `add_one("hello")` runs without any error — Python simply ignores the `: int` annotation. Only an external tool like `mypy` would flag it. Students often expect annotations to act like Java's compile-time checks; they do not.

##### Critical Thinking Questions

**CTQ 5.** `Optional[int]` is shorthand for `Union[int, None]` — the value might be `None`. What does `first([])` return, and is that consistent with its declared return type `Optional[int]`? What does `first([1, 2, 3])` return?

[[___ your answer here ___]]

**CTQ 6.** A type checker would flag `add_one("hello")` as an error, but Python still runs it and prints a result. What does this tell you about the **difference between static checking and runtime behavior** in a gradual type system?

[[___ your answer here ___]]

**CTQ 7.** Write the type signature for a function `map_list` that takes a list of `int` values and a function from `int` to `str`, and returns a list of `str` values. Express it using `List` and `Callable` from the `typing` module.

[[___ your answer here ___]]

**CTQ 8.** `Union[int, float]` in `square` says the function accepts either type. Without `Union`, you would need two separate functions or an `isinstance` check. What is the cost of using `Union` types liberally throughout a large codebase? (Hint: consider what the type checker can still guarantee when a function accepts many different types.)

[[___ your answer here ___]]

---

#### Model 3: Building a Mini Type Checker with the Consistency Relation

Ordinary type equality is strict: `Int` equals `Int` and nothing else. The consistency relation relaxes this by introducing a wildcard type `Any` that is compatible with everything — like a universal adapter that fits any socket. The catch is that this wildcard breaks transitivity, and that gap between what the static checker accepts and what can succeed at runtime is exactly where runtime failures live.

At the heart of gradual typing is a relation called **consistency** (written `~`). It differs from ordinary type equality. Two types are consistent if they could be the same type at runtime: `Int ~ Int` (trivially), `Any ~ Int` (a dynamic value might be an `Int`), `Int ~ Any` (an `Int` is compatible with an unknown type). But `Int ~ Str` is **false** — no runtime value is both an integer and a string.

Formally:

```
t ~ t             (reflexivity)
Any ~ t           (Any is consistent with everything)
t ~ Any           (symmetric)
```

This relation is **not transitive**: `Int ~ Any` and `Any ~ Str` are both true, but `Int ~ Str` is false. That gap is precisely where runtime failures live — and where the blame calculus (Model 4) must assign responsibility.

The code below implements a bi-directional type checker for a small expression language using `consistent` as its compatibility predicate.

```python  liascript
from dataclasses import dataclass
from typing import Any, Dict

# Types in our mini language
INT  = "Int"
BOOL = "Bool"
STR  = "Str"
DYN  = "Any"  # the gradual type -- compatible with everything

def consistent(t1, t2):
    """Two types are consistent if one is Any or they are equal."""
    return t1 == DYN or t2 == DYN or t1 == t2

# AST nodes
@dataclass
class Lit:    value: Any; ty: str
@dataclass
class Var:    name: str
@dataclass
class Add:    left: Any; right: Any
@dataclass
class Eq:     left: Any; right: Any
@dataclass
class If:     cond: Any; then_: Any; else_: Any
@dataclass
class Ann:    expr: Any; ty: str   # explicit annotation: (expr : ty)

Env = Dict[str, str]  # variable -> type

def infer(expr, env: Env) -> str:
    if isinstance(expr, Lit):
        return expr.ty
    if isinstance(expr, Var):
        return env.get(expr.name, DYN)   # unannotated vars have type Any
    if isinstance(expr, Ann):
        t = infer(expr.expr, env)
        if not consistent(t, expr.ty):
            raise TypeError(f"Annotation mismatch: got {t}, expected {expr.ty}")
        return expr.ty
    if isinstance(expr, Add):
        t1, t2 = infer(expr.left, env), infer(expr.right, env)
        if not consistent(t1, INT) or not consistent(t2, INT):
            raise TypeError(f"Add requires Int, got {t1} + {t2}")
        return INT
    if isinstance(expr, Eq):
        t1, t2 = infer(expr.left, env), infer(expr.right, env)
        if not consistent(t1, t2):
            raise TypeError(f"Eq: {t1} vs {t2}")
        return BOOL
    if isinstance(expr, If):
        tc = infer(expr.cond, env)
        if not consistent(tc, BOOL):
            raise TypeError(f"If cond must be Bool, got {tc}")
        t1 = infer(expr.then_, env)
        t2 = infer(expr.else_, env)
        if consistent(t1, t2): return t1 if t1 != DYN else t2
        raise TypeError(f"If branches: {t1} vs {t2}")
    raise ValueError(f"Unknown: {expr}")

env = {"x": INT, "name": STR}

# Well-typed programs
print(infer(Add(Var("x"), Lit(1, INT)), env))   # Int
print(infer(Eq(Var("x"), Lit(0, INT)), env))    # Bool

# Gradual: untyped var y has type Any -- consistent with everything
print(infer(Add(Var("y"), Lit(1, INT)), env))   # Int (Any + Int is OK)

# Explicit annotation accepted
print(infer(Ann(Var("x"), INT), env))           # Int

# Type error caught statically
try:
    print(infer(Add(Var("name"), Lit(1, INT)), env))
except TypeError as e:
    print(f"Type error: {e}")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

> **Watch out!** Consistency is **not** the same as subtyping. `Any` is consistent with `Int`, but `Any` is not a subtype of `Int`. Subtyping is a containment relationship; consistency is a compatibility relationship. Conflating them leads to incorrect reasoning about what the type checker actually accepts.

##### Critical Thinking Questions

**CTQ 9.** `DYN = "Any"` represents an unannotated binding. What does `consistent(DYN, INT)` return, and why? Trace through the `consistent` function body to verify your answer.

[[___ your answer here ___]]

**CTQ 10.** In gradual typing, `(Any + Int) -> Int`. This means the checker accepts adding an unannotated value to an `Int` and returns `Int`. Is this **sound**? (Hint: what if the `Any` value turns out to be a `Str` at runtime? Will the addition succeed?)

[[___ your answer here ___]]

**CTQ 11.** The consistency relation is **not transitive**: `consistent(INT, DYN)` is true and `consistent(DYN, STR)` is true, but `consistent(INT, STR)` is false. Draw a small diagram showing these three types and the consistency arrows between them. Why does allowing `DYN` to be consistent with everything create this non-transitivity?

[[___ your answer here ___]]

**CTQ 12.** What does the type checker **guarantee** when a program type-checks with **no** `DYN` types at all (i.e., every variable in `env` has a concrete type and no `Var` lookup returns `DYN`)? How does this guarantee weaken when some variables are unannotated?

[[___ your answer here ___]]

---

#### Model 4: The Blame Calculus — Who Gets the Error?

When two parties sign a contract, a violation needs to be traced back to whoever broke it — not to some innocent bystander in the middle. The blame calculus does exactly this for type boundaries: it tags each boundary with a label so that when a runtime cast fails, the error message names the site that made the broken promise rather than the function body that happened to discover the problem.

When a gradually-typed program fails at runtime — because a `DYN` value turned out to be the wrong type at a typed boundary — the system needs to say **which boundary** was violated. This is the **blame calculus** (Wadler and Findler, 2009). Without blame, a runtime failure deep inside a library could be misleadingly attributed to the library itself, when the real problem is that the caller passed an untyped value that violated the library's contract.

The key insight: when typed code calls untyped code, or untyped code calls typed code, a **cast** is inserted at the boundary. If the cast fails, blame is assigned to the boundary label — the name of the site that promised a value of the wrong type.

Note that TypeScript and mypy **erase** types at runtime: TypeScript compiles to plain JavaScript, and mypy-annotated Python runs without any runtime checks. This means that in practice those systems do not enforce blame semantics at runtime. The blame calculus is more of a theoretical model for understanding responsibility than a feature you get for free in everyday toolchains.

```python  liascript
class Proxy:
    """A proxy wraps a dynamic value and tracks where it came from."""
    def __init__(self, value, expected_type, blame_label):
        self.value = value
        self.expected_type = expected_type
        self.blame_label = blame_label

    def force(self):
        """Check the type when the value is actually used."""
        type_map = {int: "Int", str: "Str", bool: "Bool"}
        actual = type_map.get(type(self.value), "Unknown")
        if actual != self.expected_type:
            raise RuntimeError(
                f"Blame: {self.blame_label} -- "
                f"expected {self.expected_type}, got {actual}"
            )
        return self.value

# Simulating: typed function f: Int -> Int called with dynamic argument
def f_typed(x_proxy):
    x = x_proxy.force()   # blame fires HERE if x is not Int
    return x + 1

# Good: calling f with an actual int wrapped as a proxy
good_arg = Proxy(42, "Int", "call-site:line-10")
print(f_typed(good_arg))  # 43

# Bad: calling f with a string (common when dynamic code calls typed code)
bad_arg = Proxy("hello", "Int", "call-site:line-15")
try:
    print(f_typed(bad_arg))
except RuntimeError as e:
    print(e)

# Demonstrate: blame label identifies the boundary, not the function body
def g_typed(x_proxy):
    # g does more work before using x
    intermediate = 100
    x = x_proxy.force()
    return x + intermediate

bad_for_g = Proxy(3.14, "Int", "untyped-module:line-42")
try:
    print(g_typed(bad_for_g))
except RuntimeError as e:
    print(e)
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

##### Critical Thinking Questions

**CTQ 13.** Without blame tracking, what would the error message look like if `f_typed` simply called `int(x)` and raised `ValueError` on a string? Why is knowing the **call site** more useful than knowing the **function body line** where the failure occurred?

[[___ your answer here ___]]

**CTQ 14.** TypeScript compiles to JavaScript and erases all types. mypy-annotated Python runs without any runtime checks. Given this, what happens when a TypeScript function typed `(n: number) => number` is called from JavaScript with a string? Does blame semantics apply?

[[___ your answer here ___]]

**CTQ 15.** If `f` is a typed function called from **untyped** code, should blame go to the **caller** or the **callee** when a type mismatch occurs? Justify your answer using the principle that blame should be assigned to the party that made a promise it did not keep.

[[___ your answer here ___]]

**CTQ 16.** The `Proxy` above only tracks a single `blame_label`. In a real system, typed values can pass through many boundaries (typed → untyped → typed → untyped). How might you extend `Proxy` to track a **chain** of blame labels rather than just one?

[[___ your answer here ___]]

---

#### Model 5: Adding Gradual Typing to Your Language

This model is a direct bridge to your course interpreter project. The key new idea is `runtime_check`: a small function called at every typed boundary that either lets a value pass or raises an error with useful blame information. Annotated bindings are checked; unannotated ones are not. Everything else in the interpreter stays the same.

> **Watch out!** The `runtime_check` for a typed function parameter fires at **application time**, not at lambda definition time. The lambda itself is just a closure; the check happens when the function is called with a specific argument. Students sometimes expect the check at the point the `Lam` is evaluated — it is not.

The final model wires everything together: a small interpreter that supports **both typed and untyped bindings**. Annotated `let` bindings and annotated lambda parameters have their types **checked at runtime** when the value crosses the annotated boundary. Unannotated bindings pass through freely. This is the core mechanism of a gradually-typed interpreter — the static checker (Model 3) accepts programs that mix typed and untyped code; this interpreter enforces the typed parts at runtime.

The structure mirrors what you have been building in your course interpreter project. The new ingredient is `runtime_check`, which is called exactly when a value is bound to a typed name, and when a typed function is applied to an argument.

```python  liascript
from dataclasses import dataclass
from typing import Any, Optional

@dataclass
class Let:
    name: str
    ty: Optional[str]   # None = dynamic
    val: Any
    body: Any

@dataclass
class Var:    name: str
@dataclass
class Num:    value: float
@dataclass
class BinOp:  op: str; left: Any; right: Any
@dataclass
class Lam:    param: str; param_ty: Optional[str]; body: Any
@dataclass
class App:    fun: Any; arg: Any

class Env:
    def __init__(self, d=None, parent=None):
        self.d = d or {}; self.parent = parent
    def lookup(self, n):
        return self.d[n] if n in self.d else self.parent.lookup(n)
    def extend(self, n, v): return Env({n: v}, self)

@dataclass
class Closure:
    param: str; param_ty: Optional[str]; body: Any; env: Any

def runtime_check(value, expected_ty, where):
    if expected_ty is None: return value   # dynamic: no check
    actual = type(value).__name__
    ty_map = {"float": "Num", "int": "Num", "str": "Str",
              "bool": "Bool", "Closure": "Fun"}
    actual_ty = ty_map.get(actual, actual)
    if actual_ty != expected_ty:
        raise TypeError(f"[{where}] Expected {expected_ty}, got {actual_ty}")
    return value

def interp(expr, env):
    if isinstance(expr, Num): return float(expr.value)
    if isinstance(expr, Var): return env.lookup(expr.name)
    if isinstance(expr, BinOp):
        l, r = interp(expr.left, env), interp(expr.right, env)
        ops = {'+': l+r, '-': l-r, '*': l*r, '/': l/r}
        return ops[expr.op]
    if isinstance(expr, Let):
        v = interp(expr.val, env)
        v = runtime_check(v, expr.ty, f"let {expr.name}")
        return interp(expr.body, env.extend(expr.name, v))
    if isinstance(expr, Lam):
        return Closure(expr.param, expr.param_ty, expr.body, env)
    if isinstance(expr, App):
        fn = interp(expr.fun, env)
        arg = interp(expr.arg, env)
        arg = runtime_check(arg, fn.param_ty, f"call to {expr.fun}")
        return interp(fn.body, Env({fn.param: arg}, fn.env))

base_env = Env({"pi": 3.14159})

# Typed let: let x: Num = 5 in x * 2
prog1 = Let("x", "Num", Num(5), BinOp("*", Var("x"), Num(2)))
print("Typed let:", interp(prog1, base_env))

# Untyped let: let y = 5 in y * 2 (no check)
prog2 = Let("y", None, Num(5), BinOp("*", Var("y"), Num(2)))
print("Untyped let:", interp(prog2, base_env))

# Typed function: fun (x: Num) -> x + 1
typed_fn = Lam("x", "Num", BinOp("+", Var("x"), Num(1)))
prog3 = App(Let("f", None, typed_fn, Var("f")), Num(3))
print("Typed fn call:", interp(prog3, base_env))

# Typed let with wrong type: let x: Num = "hello" in x
prog4 = Let("x", "Num", Num(0), BinOp("+", Var("x"), Num(1)))
print("Well-typed annotated let:", interp(prog4, base_env))

# Demonstrate runtime_check catching a mismatch
try:
    bad = runtime_check("oops", "Num", "manual-test")
except TypeError as e:
    print(f"Caught: {e}")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

##### Critical Thinking Questions

**CTQ 17.** The check `runtime_check(v, expr.ty, ...)` only runs when `expr.ty` is not `None`. What does the interpreter do with unannotated values? Can an unannotated binding ever cause a runtime type error in this interpreter?

[[___ your answer here ___]]

**CTQ 18.** If you annotate a `let` binding as `Num` but the right-hand side computes a `Closure` (e.g., `Let("f", "Num", Lam(...), ...)`), at what precise moment does the error fire? Trace through `interp` to identify the call chain.

[[___ your answer here ___]]

**CTQ 19.** Currently `runtime_check` handles `Num`, `Str`, `Bool`, and `Fun`. How would you add a `List[Num]` type to this system? Specifically, what would `runtime_check` need to do for lists — can it check the type in O(1), or must it inspect every element?

[[___ your answer here ___]]

**CTQ 20.** Compare this interpreter's behavior to the static checker from Model 3. If a program passes the static checker (Model 3), is it guaranteed to pass all runtime checks in this interpreter (Model 5)? If a program fails the static checker, does it necessarily fail at runtime? Explain both directions.

[[___ your answer here ___]]

---

#### Multiple Choice

Which answer best completes each statement?

Gradual typing is "gradual" because...

[[ Type errors are only found gradually, one at a time ]]
[[ (X) Programs can mix typed and untyped code, with boundaries checked at runtime ]]
[[ Types are inferred gradually during execution ]]
[[ The type checker slows down gradually as programs grow ]]

---

`consistent(DYN, INT)` returns `True`. This means...

[[ DYN and INT are the same type ]]
[[ (X) A dynamically-typed value may be used where an Int is expected, with a runtime check inserted at the boundary ]]
[[ The program will not have any type errors ]]
[[ INT is a subtype of DYN ]]

---

In the blame calculus, blame is assigned to...

[[ (X) The code boundary that violated a type contract ]]
[[ The programmer who wrote the bug ]]
[[ The type checker ]]
[[ The line where the error was detected at runtime ]]

---

TypeScript compiles to JavaScript and erases all types. What does this mean for type safety?

[[ TypeScript programs are slower than JavaScript ]]
[[ (X) TypeScript type errors are caught at compile time but there are no runtime type checks in the generated JavaScript output ]]
[[ TypeScript and JavaScript have incompatible runtime semantics ]]
[[ TypeScript type annotations are treated as comments by the browser ]]

---

#### Exercises

**Exercise 1: Extend Model 3 with `Let`**

Add a `Let` node to the `infer` function in Model 3. `Let(name, ty, val, body)` optionally annotates `name` with type `ty` (which may be `None`, meaning `DYN`). The checker should: (a) infer the type of `val`; (b) check that the inferred type is consistent with `ty` if `ty` is not `None`; (c) add `name` to the environment with the annotated type (or `DYN` if unannotated); (d) infer and return the type of `body`. Write two test cases: one that passes (annotated correctly) and one that fails (annotation mismatch).

**Exercise 2: Add `Str` type and string concatenation**

Extend Model 5's interpreter to support a `Str` type and string concatenation. Add a `StrLit` AST node whose value is a Python string and whose `runtime_check` type name is `"Str"`. Extend `BinOp` to support `"+"` on strings (concatenation). Write a test that concatenates two typed string values and one that mixes a typed `Str` with an untyped binding.

**Exercise 3: Non-transitivity and blame chains**

The consistency relation is not transitive: `consistent(INT, DYN)` and `consistent(DYN, STR)` are both true, but `consistent(INT, STR)` is false. Construct a three-module scenario (a typed module A, an untyped module B, and a typed module C) where a value flows from A through B to C. Describe precisely: (a) what check is inserted at the A→B boundary; (b) what check is inserted at the B→C boundary; (c) why non-transitivity means the B→C check can fail even when the A→B check succeeded.

---

#### Reflection

> In your course journal: TypeScript, mypy, and Hack (PHP) all chose gradual typing over requiring a full switch to a statically typed language. Why might a language designer make this choice? What does it cost in terms of formal guarantees? If your final project language is dynamically typed, where would you add optional type annotations — which parts of the language would benefit most — and what would the annotation syntax look like?

---

#### Further Reading

- Siek and Taha, "Gradual Typing for Functional Languages" (2006) — the paper that named and formalized the approach
- Wadler and Findler, "Well-Typed Programs Can't Be Blamed" (2009) — the blame calculus
- mypy documentation: `type: ignore` and `cast()` — how to escape the checker intentionally
- TypeScript's `unknown` vs `any` — a real-world version of this activity's `DYN` type, with `unknown` requiring an explicit narrowing check before use
- Typed Racket — a production gradually-typed language that does insert runtime checks, giving you actual blame semantics

---
