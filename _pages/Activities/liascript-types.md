# Type Systems
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
| Compiles `let n = 5; n = "hi"` to an error without any annotations in the source | ? | ? |

### Critical Thinking Questions

1. Fill the grid and name a plausible language for each row.
2. Row 3's behavior (coercion) maximizes which evaluation criterion from week 2, and damages which? Cite the `"5" + 1` versus `"5" - 1` asymmetry as evidence.
3. Row 4 shows inference: the checker deduced `n`'s type from `5`. Sketch how it would propagate types through `let m = n + 1; let s = m + "!"` and where it would report the error. Whose line gets blamed?
4. Testing exercises only the paths you run; static checking covers all paths. Construct a two-branch program where dynamic typing hides a type error from a test suite that achieves 100 percent line coverage on the happy branch... and then explain why coverage did not save you.

---

# Part II: Types in Your Interpreter

## 2. A Dynamically, Strongly Typed Core

Your language (like Python) will check at runtime and refuse silent coercion: a respectable, implementable choice. The implementation pattern: each evaluated value carries its Python type along naturally; binary operations *check before computing*.

---

## Code Cell

```python
# Adding strong dynamic typing to the BinOp evaluator: check, then compute.

def type_name(v):
    return {bool: "bool", float: "number", str: "string"}.get(type(v), type(v).__name__)

def eval_binop(op, left, right):
    """Strong typing: refuse undefined mixtures with a located, specific error."""
    try:
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
    except (TypeError, ZeroDivisionError, ValueError):
        raise
    except Exception as e:
        print(f"[types:eval_binop] {e}")
        import traceback; traceback.print_exc()
        raise

for expr in [(3.0, "+", 4.0), ("ab", "+", "cd"), (3.0, "+", "cd"),
             (True, "*", 2.0), (3.0, "<", "cd")]:
    l, op, r = expr
    try:
        print(f"{l!r} {op} {r!r} = {eval_binop(op, l, r)!r}")
    except (TypeError, ZeroDivisionError) as e:
        print(f"{l!r} {op} {r!r} -> {type(e).__name__}: {e}")
```

---

## Model 2: The Checker You Just Read

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

---

# Part III: Synthesis and Practice

## 3. Exercises

1. *Interpreter integration.* Wire `eval_binop` into your interpreter's `BinOp` case, add booleans and strings as value types (with literals in your lexer and parser if absent), and demonstrate three programs: one that runs, one that raises your TypeError with a helpful message, and one comparison program.
2. *Coercion lab.* Implement a `--weak` configuration flag that turns two refusals into coercions. Write one program whose output silently changes between modes, and one paragraph on which mode your team ships and why, citing the evaluation criteria.
3. *Inference on paper.* For the program `let a = 2; let b = a + 3; let c = b < a; let d = c + 1;`, infer every variable's type top to bottom and identify the first line a static checker would reject. Note how far the *error* is from the *mistake*, and what that implies about inference error messages.
4. *Type archaeology.* Find one real bug report or postmortem caused by implicit coercion (JavaScript and PHP folklore abounds). Summarize the failure in two sentences and the language rule that would have prevented it.

---

## Reflection Prompt

In your notebook: strong typing refuses to guess what you meant; weak typing guesses. Describe one tool or person in your life whose refusals to guess you have come to value, and what it cost to appreciate them.

---

## 4. Further Reading

- Douglas Thain. *Introduction to Compilers and Language Design*, Chapter 7.
- Robert Nystrom. *Crafting Interpreters*, "Evaluating Expressions" (runtime type checks).
- Gary Bernhardt. "Wat" (talk, 2012, online): four minutes of coercion comedy with a serious lesson.
