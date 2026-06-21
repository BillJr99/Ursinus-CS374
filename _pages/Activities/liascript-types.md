# Type Systems
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

## Learning Goals

By the end of this activity, you will be able to:

- Define the two independent axes of type system design (static/dynamic and strong/weak) and place common languages on each axis
- Identify type errors in Python code and predict whether they are caught at parse time, compile time, or runtime
- Compare the trade-offs between static and dynamic typing with respect to early error detection and programming flexibility
- Explain type coercion and distinguish implicit coercion (weak typing) from explicit conversion (strong typing)
- Apply type-system concepts to specify the typing rules for a language being implemented in an interpreter project

Your interpreter happily computes `5 / 0`'s error, but what should it do with `"hello" * true`? A **type system** is a language's machinery for classifying values and rejecting senseless combinations, and the design axes (static or dynamic, strong or weak, declared or inferred) are among the most consequential your team will choose. The arc: **what types are for $\rightarrow$ the two axes $\rightarrow$ inference $\rightarrow$ adding type errors to your interpreter**.

---

## Directions and Group Roles

Work in your POGIL team with rotated roles (**Manager**, **Recorder**, **Presenter**, **Reflector**). Consider each model and question individually first, then discuss with your group. The Recorder posts answers to the Class Activity Questions discussion board; the Presenter reports out areas of disagreement or alternative approaches. After class, respond to the reflective prompt individually in your notebook.

---

# Part I: The Axes

## 1. Two Independent Questions

**A type classifies values and licenses operations**: numbers may be divided, strings concatenated, booleans tested. A **type error** is an operation applied outside its license. Languages differ on two independent axes:

**When is checking done?** **Static** typing checks before execution (Java rejects `int x = "hi";` at compile time); **dynamic** typing checks during execution, at the moment the operation runs (Python raises `TypeError` when `"hi" * {}` is attempted). Static catches errors earlier and on all paths, including paths your tests never run; dynamic permits more flexible code and faster iteration. This is the binding-time framework again: the type's binding time.

**How strictly is checking enforced?** **Strong** typing refuses undefined mixtures or requires explicit conversion; **weak** typing silently **coerces** (converts) operands to make the operation proceed. JavaScript famously computes `"5" - 1` as `4` and `"5" + 1` as `"51"`; Python, dynamically but *strongly* typed, raises on `"5" - 1`. The axes are independent: Python is dynamic and strong; C is static and (in places) weak.

**Inference splits the difference on ceremony.** Statically typed languages with **type inference** (Rust, Haskell, modern Java's `var`, TypeScript) deduce types you do not write: `let n = 5` is statically known to be an integer because 5 is. Inference buys static safety without annotation cost, at the price of error messages that can point far from the cause.

---

## Model 1: Place the Languages

| Language behavior | Static/Dynamic? | Strong/Weak? |
|-------------------|-----------------|--------------|
| Rejects `x = "hi"` at compile time when x was declared int | ? | ? |
| Raises TypeError at runtime on `"5" - 1` | ? | ? |
| Computes `"5" - 1 == 4` without complaint | ? | ? |
| Compiles `let n = 5; n = "hi"` to an error without any annotations | ? | ? |

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

---

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

### Critical Thinking Questions

8. The inference trace shows `let a: int`, `let b: int`, `let c: bool`. These are determined entirely from the *values* (literals), with no type annotations written. Is this static or dynamic typing? Explain.
9. When inference encounters `a + "hello"`, it reports the error at the `add` expression. But the *root cause* is that `a` was given an int value. How far is the reported error from the root cause, and what does this say about inference error message quality?
10. What would need to change to support `let a = 2; let b = a + 3.0;`? (Hint: numeric type widening — `int + float → float`.) Modify the `infer` function to allow this.

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
