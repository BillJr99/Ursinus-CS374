<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://github.com/BillJr99/Ursinus-CS374-Fall2026/blob/gh-pages/_pages/Activities/liascript-types.md or locally via https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374/gh-pages/_pages/Activities/liascript-types.md

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

Your interpreter — now equipped with the environments of *Environments and Variable Storage* — happily computes `5 / 0`'s error, but what should it do with `"hello" * true`? A **type system** is a language's machinery for classifying values and rejecting senseless combinations, and the design axes (static or dynamic, strong or weak, declared or inferred) are among the most consequential your team will choose. The arc: **what types are for $\rightarrow$ the two axes $\rightarrow$ inference $\rightarrow$ adding type errors to your interpreter**.

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
2. Row 3's behavior (coercion) maximizes which criterion from the *Evaluating Languages* activity, and damages which? Cite the `"5" + 1` versus `"5" - 1` asymmetry in JavaScript as evidence.
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

---
**🛑 In-class work stops here.** Everything below is homework and going-deeper material — attempt the exercises before the related assignment.

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

## Going Deeper (Optional Pointers)

The core lesson above stands on its own. The deep-dive appendices that used to follow it now live on the Tutorials shelf:

> **Going further:** the material that used to live here — Robinson unification, substitutions and the occurs check, Algorithm W, Hindley-Milner type inference, and let-polymorphism — is covered in depth in the dedicated tutorial: [Implementing Hindley-Milner Type Inference](https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374/gh-pages/_pages/Tutorials/tutorial-type-inference.md). Explore it when your project or curiosity calls for it.

> **Going further:** the material that used to live here — the static/dynamic and strong/weak axes in depth, Python annotations and `mypy`, type erasure, product and sum types, structural vs. nominal typing, and gradual typing with the consistency relation and blame — is covered in depth in the dedicated guide: [Typing Disciplines — Strong vs. Weak, Static vs. Dynamic, and Gradual Typing](https://www.billmongan.com/Ursinus-CS374-Fall2026/Tutorials/TypingDisciplines). Explore it when your project or curiosity calls for it.

---

Up next: the *Control Flow and Statement Semantics* activity pins down which code runs — and the Interpreter assignment's type-checking direction builds on today's axes.
