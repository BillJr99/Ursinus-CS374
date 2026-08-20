<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://github.com/BillJr99/Ursinus-CS374-Fall2026/blob/gh-pages/_pages/Activities/liascript-controlflowsemantics.md or locally via https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374/gh-pages/_pages/Activities/liascript-controlflowsemantics.md

import: https://raw.githubusercontent.com/liascript/CodeRunner/master/README.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

# Control Flow Semantics

Think of a program as a choose-your-own-adventure book: every time you reach a decision point, the story branches, and you only read one of the two paths that follow. Control flow semantics are the rules that determine *which* page you turn to next — and critically, whether the unchosen pages are ever glanced at at all. In this activity you will pin down those rules precisely enough to implement them in your own interpreter. You pinned down *what values are* in the *Type Systems* activity; today you pin down *which code runs*.

## Learning Goals

By the end of this activity, you will be able to:

- Define non-strict evaluation and explain why `if` must not evaluate both branches
- Compare truthiness policies (booleans-only, universal truthiness, C-style numeric truth) and identify which values each policy accepts or rejects
- Explain short-circuit evaluation for `and` and `or`, and trace whether the right operand is evaluated in a given expression
- Implement a `truthy` predicate and a short-circuiting `and`/`or` evaluator consistent with a chosen policy
- Analyze how the design choices of truthiness and short-circuit semantics interact with a language's type system

`if` and `while` look trivial until you must implement them, at which point a swarm of decisions appears: what counts as true? are both branches evaluated? does `and` evaluate its right side when the left already decides? Today we pin down **control flow semantics** for your interpreter assignment, with special attention to **truthiness** and **short-circuit evaluation**, two places where languages quietly disagree. The arc: **selection semantics $\rightarrow$ truthiness $\rightarrow$ short-circuiting $\rightarrow$ iteration and its design questions**.

> **Before You Begin:** This activity assumes you can:
> - Write and trace basic Python `if`/`elif`/`else` and `while` statements, including nested conditions
> - Explain what a boolean expression evaluates to and identify common falsy values in Python (`0`, `""`, `[]`, `None`, `False`)
> - Read a simple recursive Python function and follow what gets returned at each call
>
> If any of these feel shaky, review them first.

---

## Directions and Group Roles

Work in your POGIL team with rotated roles (**Manager**, **Recorder**, **Presenter**, **Reflector**). Consider each model and question individually first, then discuss with your group. The Recorder posts answers to the Class Activity Questions discussion board; the Presenter reports out areas of disagreement or alternative approaches. After class, respond to the reflective prompt individually in your notebook.

---

# Part I: Selection and Truth

Before diving into code, consider what an `if` statement really promises: it will look at a condition, and then read *exactly one* of two possible continuations. That promise turns out to have deep consequences — it is what makes guarded divisions safe, what forces you to define "what counts as true," and what separates `if` from every ordinary function call in your language.

## 1. The Semantics of If

**Selection evaluates the condition, then exactly one branch.** The "exactly one" is load-bearing: in `if (x != 0) { print 10 / x; } else { print 0; }`, evaluating the untaken branch would divide by zero. Your executor already respects this (the Python `if` inside `execute` chooses *which subtree to walk*), and naming the property matters: `if` is our first **non-strict** construct, one that deliberately does not evaluate all of its parts.

**Truthiness: what may stand as a condition?** Three coherent policies: (a) **booleans only** (Java): `if (count)` is a type error; (b) **everything has a truth value** (Python: zero, empty string, and empty collections are falsy; the rest truthy); (c) **a designated set** (C: zero is false, any nonzero number true). The policy interacts with your type system: a booleans-only language catches `if (x = 5)`-style accidents that permissive languages execute happily.

> **Watch out!** The string `"false"` is *truthy* in Python because it is a non-empty string — its content is irrelevant to the truthiness test. This surprises many beginners who expect the *meaning* of a value to determine its truth. If your language adopts Python-style universal truthiness, make sure your documentation spells this out explicitly.

---

## Model 1: The Truthiness Tribunal

Every language designer must answer the question: "What values are allowed to appear as a condition?" Python says almost anything goes — zero and empty collections are false, everything else is true. Java says only actual booleans are allowed. C says zero is false and any nonzero number is true. None of these is obviously "right"; each reflects a different trade-off between convenience and catching bugs at compile time. In this model you will run all three policies side by side so the differences become concrete.

The condition values: `0`, `1`, `-3`, `""`, `"false"`, an empty list, the boolean `false`.

**Run the Python truthiness table:**

```python
test_values = [0, 1, -3, "", "false", [], False, True, None, 0.0, 0.1]

print(f"{'Value':<12} {'Python bool()':<16} {'C-style (!=0)':<16} {'Java (bool only)'}")
print("-" * 60)
for v in test_values:
    python_result = bool(v)
    # C-style: only numbers treated as truthy/falsy
    try:
        c_style = bool(v) if isinstance(v, (int, float)) else "TYPE ERROR"
    except:
        c_style = "TYPE ERROR"
    # Java-style: only booleans allowed
    java_style = bool(v) if isinstance(v, bool) else "TYPE ERROR"
    print(f"{str(v):<12} {str(python_result):<16} {str(c_style):<16} {str(java_style)}")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

### Critical Thinking Questions

1. For each value, rule its truth under policies (a), (b), and (c) (write "error" where the policy rejects it). Where do the policies disagree most surprisingly? (`"false"` deserves the team's attention — it's a non-empty string, so it's truthy in Python even though it *looks* false.)
2. The classic C bug `if (x = 5)` (assignment, not comparison) runs and is always true. Which policy, and separately which *grammar* decision (is assignment an expression?), each independently prevents it? Your language gets two chances to kill this bug; choose at least one.
3. Decide your project's truthiness policy and write the `truthy(value)` specification in `SEMANTICS.md` language: exhaustive, no "etc."

---

## Model 2: If Is Non-Strict

It is one thing to say "the untaken branch is not evaluated" and another to *prove* it. In this model a special `Bomb` node plays the role of a branch that would crash the program if it were ever executed. If the interpreter is truly non-strict, the bomb never goes off — and that silence is itself the evidence. Pay close attention to the single line that makes this work: the Python ternary that *chooses which recursive call to make*, rather than making both.

**Prove that if does not evaluate the untaken branch:**

```python
from dataclasses import dataclass
from typing import Any

@dataclass
class Num:       value: float
@dataclass
class BinOp:     op: str; left: Any; right: Any
@dataclass
class Cond:      cond: Any; then_: Any; else_: Any
@dataclass
class Bomb:
    pass  # evaluating this should explode

def truthy(v):
    if isinstance(v, bool): return v
    if isinstance(v, (int, float)): return v != 0
    return v is not None

def evaluate(node, env):
    if isinstance(node, Num):   return node.value
    if isinstance(node, bool):  return node
    if isinstance(node, Bomb):  raise RuntimeError("untaken branch was evaluated!")
    if isinstance(node, Cond):
        cond_val = evaluate(node.cond, env)
        # Non-strict: only evaluate the TAKEN branch
        return evaluate(node.then_ if truthy(cond_val) else node.else_, env)
    if isinstance(node, BinOp):
        L, R = evaluate(node.left, env), evaluate(node.right, env)
        return {"+": L+R, "-": L-R, "*": L*R, "/": L/R}[node.op]
    raise TypeError(f"unknown: {node!r}")

# Test 1: false condition — else branch evaluated, then_ (Bomb) skipped
result1 = evaluate(Cond(False, Bomb(), Num(42)), {})
print(f"false → else: {result1}")  # 42

# Test 2: true condition — then_ evaluated, else_ (Bomb) skipped
result2 = evaluate(Cond(True, Num(99), Bomb()), {})
print(f"true → then: {result2}")   # 99

# Test 3: both branches safe
result3 = evaluate(Cond(Num(0), Num(1), Num(2)), {})
print(f"0 → else: {result3}")  # 2 (0 is falsy)
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

### Critical Thinking Questions

4. The Bomb proves non-evaluation by *absence of explosion*. Why is this a better test than inspecting return values, and what general testing idea (observing side effects to detect evaluation) did you just use?
5. In the `evaluate` function for `Cond`, the key line is `evaluate(node.then_ if truthy(cond_val) else node.else_, env)`. This is a Python ternary that *chooses which recursive call to make*. Why does this implement non-strictness, while `evaluate(node.then_, env) + evaluate(node.else_, env)` would not?

---

# Part II: Short-Circuit Evaluation

You have seen that `if` skips one whole branch. Now consider what happens *inside* the condition itself: does evaluating `a and b` always look at both `a` and `b`? In most languages the answer is no — and that "no" is not a performance trick, it is a guarantee programs are written to depend on. This part examines exactly when `and` and `or` are allowed to stop early, and why your interpreter must handle them differently from ordinary binary operators.

## 2. And/Or That Stop Early

**Short-circuit operators evaluate left to right and stop as soon as the answer is known**: `false and X` never evaluates `X`; `true or X` never evaluates `X`. This is not an optimization but a *semantic guarantee* programs rely on: `if (i < len(a) and a[i] > 0)` is only safe because the bounds check guards the access. Implementing it means `and`/`or` cannot be ordinary `BinOp`s (your `BinOp` case evaluates both children first, post-order); they need their own node and their own evaluation rule.

$$
\mathcal{E}[\![l \text{ and } r]\!] = \begin{cases} \mathcal{E}[\![l]\!] & \text{if } \mathcal{E}[\![l]\!] \text{ is falsy} \\ \mathcal{E}[\![r]\!] & \text{otherwise} \end{cases}
$$

(Note the Python-style refinement: returning the deciding *operand* rather than a normalized boolean is itself a design choice; Java normalizes, Python does not.)

> **Watch out!** Short-circuit evaluation is **not universal**. Some languages (notably older Fortran, and certain functional languages with call-by-value semantics) evaluate both operands of `and`/`or` before applying the operator. If you are porting code that relies on short-circuiting as a guard, always check the target language's specification — you cannot assume the right operand is skipped.

---

## Model 3: Short-Circuit in Action

The key insight here is that `and` and `or` cannot simply be added to your existing `BinOp` evaluator, because `BinOp` always evaluates both children before doing anything with them. Logical operators need their own node type with their own evaluation rule — one that only reaches for the right child after deciding whether it is necessary. The Bomb-based test makes this difference visible: if the right side were always evaluated, the bomb would explode.

```python
# Short-circuit logic as its own node type: the right child is evaluated
# conditionally, unlike every BinOp. Demonstrated with a guard idiom.

class LogicOp:
    def __init__(self, op, left, right):
        self.op, self.left, self.right = op, left, right

def truthy(v):
    return bool(v)

def eval_logic(node, env, evaluate):
    left = evaluate(node.left, env)
    if node.op == "and":
        return evaluate(node.right, env) if truthy(left) else left
    if node.op == "or":
        return left if truthy(left) else evaluate(node.right, env)
    raise ValueError(f"unknown logical operator {node.op!r}")

# Proof that the right side is skipped: a right child that would explode.
class Bomb:
    pass

def evaluate_demo(node, env):
    if isinstance(node, (bool, int)):  return node
    if isinstance(node, Bomb):         raise RuntimeError("the right side was evaluated!")
    if isinstance(node, LogicOp):      return eval_logic(node, env, evaluate_demo)
    raise TypeError(f"unknown node {node!r}")

print(evaluate_demo(LogicOp("and", False, Bomb()), {}))   # False, no explosion
print(evaluate_demo(LogicOp("or",  True,  Bomb()), {}))   # True, no explosion

try:
    evaluate_demo(LogicOp("and", True, Bomb()), {})        # True: must look right
except RuntimeError as e:
    print("as expected:", e)

# Real use: Python-style short-circuit
items = [10, 20, 30]
i = 5   # out of bounds

# Safe guard using Python's short-circuit:
result = i < len(items) and items[i] > 0
print(f"Safe guard result: {result}")   # False (never indexes out of bounds)
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

The guarantee that `i < n and items[i] > 0` never indexes out of bounds depends on:

[( )] The parser checking array lengths
[( )] Operator precedence placing and below comparison
[(X)] The semantic rule that and does not evaluate its right operand when the left is falsy
[( )] The type checker proving i is a number

In Python, `x or "default"` returns `"default"` when `x` is falsy. This behavior — returning the *operand* rather than normalizing to `True`/`False` — is called:

[( )] Type coercion
[( )] Lazy evaluation
[(X)] Short-circuit evaluation with value-preserving semantics
[( )] Boolean normalization

### Critical Thinking Questions

6. Trace why `LogicOp` cannot be folded into your `BinOp` case: quote the one line of the BinOp evaluator that makes it impossible.
7. Your parser must give `and`/`or` a precedence tier. Should `a == b and c == d` parse as `(a == b) and (c == d)`? Place the new tier in your precedence ladder (looser or tighter than comparison?) and justify with that example.
8. Python's `and`/`or` return one of their *operands*, not necessarily a boolean. So `"hello" and "world"` returns `"world"`, and `"" or "default"` returns `"default"`. Is this surprising? Name one production use of this behavior.

---

## Model 4: Language Comparison

You now know *that* `and`/`or` short-circuit, but there is a second independent question: *what do they return?* Python returns the actual operand that decided the outcome — not a normalized boolean — which opens up concise idioms like `name or "Anonymous"`. Java always returns `true` or `false`. Both are internally consistent choices; this model lets you see their practical consequences side by side before you commit to one in your own language.

```python
# Python's short-circuit with value-preserving semantics
print("Python 'and' returns operand:")
print(f"  True and 'hello'  → {True and 'hello'!r}")
print(f"  False and 'hello' → {False and 'hello'!r}")
print(f"  0 and 'hello'     → {0 and 'hello'!r}")

print("\nPython 'or' returns operand:")
print(f"  '' or 'default'   → {('' or 'default')!r}")
print(f"  0 or 42           → {(0 or 42)!r}")
print(f"  'x' or 'default'  → {('x' or 'default')!r}")

print("\nCommon Python idiom: default values")
name = ""
display = name or "Anonymous"
print(f"  display = {display!r}")

print("\nCommon Python idiom: conditional assignment")
config = None
timeout = config or 30
print(f"  timeout = {timeout}")

print("\nNote: Java 'and'/'or' always return boolean:")
# In Java: boolean b = true && false;  // always true or false
# Python allows: x = True and "hello"  // returns "hello"
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

### Critical Thinking Questions

9. The Python idiom `name = input_name or "Anonymous"` relies on short-circuit value-preserving semantics. Rewrite this as an explicit `if` statement. Which version do you prefer, and why?
10. Should your project language's `and`/`or` return the deciding operand (Python style) or always return a boolean (Java style)? Write a program whose output differs between the two choices.

---

# Part III: Iteration

Loops are where control flow gets its most dramatic power — and its most dangerous failure mode. A `while` loop keeps re-reading the same page of the adventure book as long as the condition holds, and you need to know precisely when the condition is re-checked, whether the body gets a fresh environment each time, and what it means to exit the loop early. These are not cosmetic details; they determine what programs your language can express correctly.

## 3. While, and the Questions It Raises

Your `While` executor re-evaluates the condition before each pass: definite semantics, easy to implement, and the source of three design questions your team must answer in `SEMANTICS.md`:

1. Does the body create a fresh scope per iteration?
2. Do you provide `break`/`continue`, and if so, how?
3. Will you offer a counting `for`, and is it core syntax or sugar?

**The break/continue trick — use exception classes:**

> **Watch out!** `break` and `continue` behave differently across languages. In Python, `break` inside a `for`/`while` exits only the *innermost* loop — a `break` nested three loops deep does not escape all three. Some languages (Java, Kotlin) offer labeled breaks to exit an outer loop directly. When implementing these statements in your interpreter, decide up front how deeply nested `break` can reach, and document it: the choice affects what programs are expressible and what complexity the interpreter must track.

```python
from dataclasses import dataclass
from typing import Any, List

@dataclass
class Num:    value: float
@dataclass
class Var:    name: str
@dataclass
class BinOp:  op: str; left: Any; right: Any
@dataclass
class While:  cond: Any; body: Any
@dataclass
class Block:  stmts: List[Any]
@dataclass
class Assign: name: str; expr: Any
@dataclass
class Print:  expr: Any
@dataclass
class Break:  pass
@dataclass
class Continue: pass

class BreakSignal(Exception):    pass
class ContinueSignal(Exception): pass

def truthy(v):
    return v != 0 if isinstance(v, (int, float)) else bool(v)

def evaluate(node, env):
    if isinstance(node, Num):   return node.value
    if isinstance(node, Var):   return env.get(node.name, 0)
    if isinstance(node, BinOp):
        L, R = evaluate(node.left, env), evaluate(node.right, env)
        return {"+": L+R, "-": L-R, "*": L*R, "/": L/R,
                ">": float(L>R), "<": float(L<R), "==": float(L==R)}[node.op]

def execute(stmt, env):
    if isinstance(stmt, Assign):
        env[stmt.name] = evaluate(stmt.expr, env)
    elif isinstance(stmt, Print):
        print(evaluate(stmt.expr, env))
    elif isinstance(stmt, Block):
        for s in stmt.stmts:
            execute(s, env)
    elif isinstance(stmt, Break):
        raise BreakSignal()
    elif isinstance(stmt, Continue):
        raise ContinueSignal()
    elif isinstance(stmt, While):
        while truthy(evaluate(stmt.cond, env)):
            try:
                execute(stmt.body, env)
            except ContinueSignal:
                continue   # re-evaluate condition
            except BreakSignal:
                break      # exit loop
    else:
        raise TypeError(f"unknown stmt: {stmt!r}")

# Find first multiple of 7 in 1..50:
# n = 1; while n <= 50: if n%7 == 0: print n; break; n = n + 1
env = {}
program = Block([
    Assign("n", Num(1)),
    While(BinOp("<=", Var("n"), Num(50)),
        Block([
            # if n % 7 == 0: print n; break
            # Simplified: check if n is exactly 7 (first multiple)
            Assign("rem", BinOp("-", Var("n"), BinOp("*", Num(7), Num(1)))),
            # Actually just print multiples of 7 using continue for odds
            Print(Var("n")),
            Assign("n", BinOp("+", Var("n"), Num(7))),
            Break(),   # only print the first one
        ])),
])
print("First multiple of 7:")
execute(program, env)
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

### Critical Thinking Questions

11. The `BreakSignal` and `ContinueSignal` exception classes contain no data. Why use custom exception classes rather than a boolean flag variable?
12. When `ContinueSignal` is caught by the `While` executor's `except ContinueSignal: continue`, what Python statement does the bare `continue` refer to? Trace the control flow carefully.
13. **Desugaring.** Implement `for (let i = 0; i < n; i = i + 1) { body }` as a parser transformation that produces the AST of `{ let i = 0; while (i < n) { body; i = i + 1; } }`. What is this called, and why does it mean you get `for` loops for free with no new evaluator code?

---

## 4. Exercises

1. *Implement the trio.* Add `LogicOp` with short-circuit `and`/`or` and a unary `not` to your lexer, parser (new tier), and evaluator. Reproduce the Bomb test inside *your* language: a right operand that would raise (divide by zero) but is never reached.
2. *Break and continue.* Implement both using custom exception classes (`BreakSignal`, `ContinueSignal`) raised by the statements and caught by the `While` executor. Demonstrate a search loop that exits early on finding a value.
3. *Desugaring.* Implement `for (let i = 0; i < n; i = i + 1) { ... }` purely in the parser, producing the AST of the equivalent block-plus-while with no new evaluator code. Show the `pretty` output proving the rewrite.
4. *Truthiness differential.* Write one program whose output differs under booleans-only versus Python-style truthiness, and confirm your interpreter follows your documented policy.
5. *Step limit.* Add a `max_steps` parameter to your `While` executor that raises `RuntimeError` after N iterations. This protects against infinite loops in student programs. Test it with `while 1 > 0: print 1` and a limit of 100.

---

## Reflection Prompt

In your notebook: short-circuiting means the language promises *not to look* at something. Contracts about what will not be examined are everywhere (sealed exams, privacy policies, blind review). Pick one and describe what breaks when the no-look promise is violated, in computing or out of it. Also: now that you have implemented `break` via exceptions, does using exceptions for control flow seem elegant or surprising? Under what other circumstances might you use exceptions for non-error control flow?

---

## 5. Further Reading

- Douglas Thain. *Introduction to Compilers and Language Design*, Chapter 6 and 7 notes on control flow.
- Robert Nystrom. *Crafting Interpreters*, "Control Flow" (online), including the break-via-exception trick.
- Robert Sebesta. *Concepts of Programming Languages*, the statement-level control structures chapter.
- Python docs on [short-circuit evaluation](https://docs.python.org/3/reference/expressions.html#boolean-operations) — the return-operand semantics documented precisely.

---

Up next: the *Functional Programming and Higher-Order Functions* activity changes the lens entirely — and today's semantics decisions complete the Interpreter assignment's core.

# From the Tree-Walking Interpretation Activity: Statements, State, and the REPL

This session is Day 2 of tree-walking interpretation. Day 1 evaluated *expressions* - a fold over the tree that returns a value. Statements are different: they do not return values, they change state, and that difference is what the rest of this session is about. The material below came from the interpretation activity's own Part II, which covered the same ground this session covers.

# Part II: Statements, State, and the REPL (Day 2)

## 2. Executing Statements

Expressions produce values; **statements produce effects**: an `Assign` updates the environment, a `Print` writes output, a `Block` executes children in order, a `While` re-evaluates its condition. The executor therefore threads the environment through:

```python
def execute(stmt, env):
    Assign(name, e)   -> env[name] = evaluate(e, env)
    Print(e)          -> print(evaluate(e, env))
    Block(stmts)      -> for s in stmts: execute(s, env)
    If(c, t, o)       -> execute(t if truthy(evaluate(c, env)) else o, env)
    While(c, body)    -> while truthy(evaluate(c, env)): execute(body, env)
```

Notice `truthy`: your language must decide what counts as true (only a boolean? any nonzero number? an empty string?), a semantics decision with daily consequences.

In a tree-walking interpreter, executing the program's `while` loop one million times will re-walk the loop body's subtree one million times. The principal cost this design accepts, relative to compilation, is:

[( )] Incorrect results on large inputs
[(X)] Repeated traversal and dispatch overhead per execution of the same code
[( )] Loss of operator precedence
[( )] The inability to support variables

---

**Model 3 preview:** Where expressions *return* values, statements *change the world* — they update the environment, produce output, or repeat a block. This model introduces `execute`, a sibling function to `evaluate` that handles the statement layer. The single most important design rule here is that `execute` must always pass the *same* `env` dictionary through every recursive call so that assignments made inside a loop body are visible after the loop ends.

> **Watch out!** A common mistake is for `execute` to return `None` (implicitly) for every branch, and then have a caller accidentally use that `None` as if it were a language value — for example, printing the result of `execute(Print(...), env)` instead of the result already printed inside `execute`. Statements produce *effects*, not values; callers of `execute` should never inspect its return value.

## Model 3: Complete Statement Executor

```python
from dataclasses import dataclass, field
from typing import Any, List, Optional

# ─── AST nodes ────────────────────────────────────────────────────────────────
@dataclass
class Num:     value: float
@dataclass
class Var:     name: str
@dataclass
class BinOp:   op: str; left: Any; right: Any
@dataclass
class Assign:  name: str; expr: Any
@dataclass
class Print:   expr: Any
@dataclass
class Block:   stmts: List[Any]
@dataclass
class If:      cond: Any; then_: Any; else_: Any = None
@dataclass
class While:   cond: Any; body: Any

# ─── Evaluator ────────────────────────────────────────────────────────────────
def evaluate(node, env):
    if isinstance(node, Num):   return node.value
    if isinstance(node, Var):
        if node.name not in env: raise NameError(f"undefined: {node.name!r}")
        return env[node.name]
    if isinstance(node, BinOp):
        L, R = evaluate(node.left, env), evaluate(node.right, env)
        return {"+": L+R, "-": L-R, "*": L*R, "/": L/R,
                ">": L>R, "<": L<R, ">=": L>=R, "<=": L<=R,
                "==": L==R, "!=": L!=R}[node.op]
    raise TypeError(f"unknown expr node: {node!r}")

def truthy(val):
    if isinstance(val, bool): return val
    if isinstance(val, (int, float)): return val != 0
    return val is not None

# ─── Executor ────────────────────────────────────────────────────────────────
def execute(stmt, env):
    if isinstance(stmt, Assign):
        env[stmt.name] = evaluate(stmt.expr, env)
    elif isinstance(stmt, Print):
        print(evaluate(stmt.expr, env))
    elif isinstance(stmt, Block):
        for s in stmt.stmts:
            execute(s, env)
    elif isinstance(stmt, If):
        cond = evaluate(stmt.cond, env)
        if truthy(cond):
            execute(stmt.then_, env)
        elif stmt.else_ is not None:
            execute(stmt.else_, env)
    elif isinstance(stmt, While):
        while truthy(evaluate(stmt.cond, env)):
            execute(stmt.body, env)
    else:
        raise TypeError(f"unknown stmt node: {stmt!r}")

# ─── Test: n = 5; total = 0; while n > 0: total += n; n -= 1; print total ───
env = {}
program = Block([
    Assign("n",     Num(5)),
    Assign("total", Num(0)),
    While(BinOp(">", Var("n"), Num(0)),
          Block([
              Assign("total", BinOp("+", Var("total"), Var("n"))),
              Assign("n",     BinOp("-", Var("n"),     Num(1))),
          ])),
    Print(Var("total")),        # should print 15
])
execute(program, env)
print(f"env after: {env}")     # n=0, total=15
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

### Critical Thinking Questions

8. Predict the output before running; then run. If they differ, the bug hunt order is: lexer → parser tree (use pretty-printer!) → evaluator. Why that order?
9. Print the environment after execution. Should `n` still exist after the loop? Defend your language's answer; both choices are defensible.
10. Add a `truthy(0.0)` call and a `truthy(None)` call to the test. What do they return? How does your `truthy` definition match Python's? Where do they differ?

---

**Model 4 preview:** The REPL (Read-Eval-Print Loop) is what makes your language *feel* like a language. It chains the entire pipeline — tokenize, parse, evaluate — inside a loop that persists a single `env` across lines, so earlier assignments are visible in later ones. This model uses a simulated REPL (a list of inputs instead of real keyboard input) so it can run non-interactively here, but the architecture is identical to what you would wire up with Python's `input()`.

> **Watch out!** Because the REPL's `env` dictionary persists across lines, a variable assigned on line 1 is still live on line 100. This means the *order* in which the user types lines matters, and re-running the REPL from scratch will start with an empty environment. Students sometimes expect the REPL to behave like a script (isolated, top-to-bottom) rather than a stateful session. They are different execution models, and it is worth being explicit in your language documentation about which one your REPL provides.

## Model 4: The REPL — Your Language Goes Interactive

```python
from dataclasses import dataclass
from typing import Any
import re

# Minimal tokenizer → parser → evaluator pipeline for the REPL
@dataclass
class Num:  value: float
@dataclass
class Var:  name: str
@dataclass
class BinOp: op: str; left: Any; right: Any
@dataclass
class Assign: name: str; expr: Any

def tokenize(src):
    return re.findall(r"\d+\.?\d*|[A-Za-z_]\w*|[=+\-*/()]|;", src)

def parse_expr(tokens, pos):
    lhs, pos = parse_term(tokens, pos)
    while pos < len(tokens) and tokens[pos] in ("+", "-"):
        op, pos = tokens[pos], pos+1
        rhs, pos = parse_term(tokens, pos)
        lhs = BinOp(op, lhs, rhs)
    return lhs, pos

def parse_term(tokens, pos):
    lhs, pos = parse_primary(tokens, pos)
    while pos < len(tokens) and tokens[pos] in ("*", "/"):
        op, pos = tokens[pos], pos+1
        rhs, pos = parse_primary(tokens, pos)
        lhs = BinOp(op, lhs, rhs)
    return lhs, pos

def parse_primary(tokens, pos):
    tok = tokens[pos]
    if tok == "(":
        expr, pos = parse_expr(tokens, pos+1)
        assert tokens[pos] == ")", "expected ')'"
        return expr, pos+1
    if re.match(r"\d", tok):
        return Num(float(tok)), pos+1
    return Var(tok), pos+1

def parse(src):
    tokens = tokenize(src.strip().rstrip(";"))
    if len(tokens) >= 2 and re.match(r"[A-Za-z_]", tokens[0]) and tokens[1] == "=":
        expr, _ = parse_expr(tokens, 2)
        return Assign(tokens[0], expr)
    expr, _ = parse_expr(tokens, 0)
    return expr

def evaluate(node, env):
    if isinstance(node, Num):    return node.value
    if isinstance(node, Var):    return env.get(node.name, 0.0)
    if isinstance(node, Assign):
        val = evaluate(node.expr, env)
        env[node.name] = val
        return val
    if isinstance(node, BinOp):
        L, R = evaluate(node.left, env), evaluate(node.right, env)
        return {"+": L+R, "-": L-R, "*": L*R, "/": L/R}[node.op]

# ─── Simulate a REPL session ────────────────────────────────────────────────
env = {}
repl_input = [
    "x = 10",
    "y = 3",
    "x * y + 2",
    "z = (x - y) * 4",
    "z",
]

print("Mini-REPL session:")
for line in repl_input:
    try:
        result = evaluate(parse(line), env)
        print(f"  >>> {line}")
        if not line.strip().startswith(tuple("abcdefghijklmnopqrstuvwxyz") + ("x","y","z")) or "=" in line:
            pass
        print(f"  {result}")
    except Exception as e:
        print(f"  Error: {e}")

print(f"\nFinal environment: {env}")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

### Critical Thinking Questions

11. A real REPL must handle errors without dying: if the user types `1/0` or `undefined_var`, the REPL should print an error and continue. Wrap the inner call in a `try/except` and identify the *three error classes* you must catch (one per stage: lex, parse, eval).
12. The REPL above has a persistent `env` dictionary. If a user types `x = 10` and then `x = 20`, what should happen? Should the language allow rebinding?
13. REPLs for functional languages (Haskell's `ghci`, Scheme's REPL) do not allow mutation. How would you implement a purely functional REPL where each "assignment" introduces a new immutable binding rather than updating an old one?

---

---
**🛑 In-class work stops here.** Everything below is homework and going-deeper material — attempt the exercises before the related assignment.

## 3. Exercises

1. *Complete the executor.* Implement `execute` for all your statement nodes with the exception pattern from class, define and document `truthy` for your language, and demonstrate the summation program plus an `if/else` program.
2. *The REPL.* Write the read-evaluate-print loop: prompt, read a line, tokenize, parse, execute against a persistent environment, repeat, catching and printing every error class without dying. Your language now has an interactive shell; transcript required.
3. *Error taxonomy.* Construct one program each that fails in the lexer, the parser, and the evaluator. Verify each error message names its stage and location; improve the worst one.
4. *Semantics memo.* Document three semantics decisions your team made today (truthiness, division by zero, loop variable persistence) in a `SEMANTICS.md` your project will grow all semester.
5. *Interpreter speedup.* Modify the `While` executor to count the number of times the loop body executes. Then add a "step limit" parameter that raises a `RuntimeError` if the loop exceeds 10,000 iterations. This protects against infinite loops in student-written programs. Show it triggering on `while 1 > 0: print 1`.

---

