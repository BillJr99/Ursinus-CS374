# Control Flow Semantics
<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://github.com/BillJr99/Ursinus-CS374-Fall2026/blob/gh-pages/_pages/Activities/liascript-controlflowsemantics.md or locally via https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374-Fall2026/gh-pages/_pages/Activities/liascript-controlflowsemantics.md

import: https://raw.githubusercontent.com/liascript/CodeRunner/master/README.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

# Control Flow Semantics

## Learning Goals

By the end of this activity, you will be able to:

- Define non-strict evaluation and explain why `if` must not evaluate both branches
- Compare truthiness policies (booleans-only, universal truthiness, C-style numeric truth) and identify which values each policy accepts or rejects
- Explain short-circuit evaluation for `and` and `or`, and trace whether the right operand is evaluated in a given expression
- Implement a `truthy` predicate and a short-circuiting `and`/`or` evaluator consistent with a chosen policy
- Analyze how the design choices of truthiness and short-circuit semantics interact with a language's type system

`if` and `while` look trivial until you must implement them, at which point a swarm of decisions appears: what counts as true? are both branches evaluated? does `and` evaluate its right side when the left already decides? Today we pin down **control flow semantics** for your interpreter assignment, with special attention to **truthiness** and **short-circuit evaluation**, two places where languages quietly disagree. The arc: **selection semantics $\rightarrow$ truthiness $\rightarrow$ short-circuiting $\rightarrow$ iteration and its design questions**.

---

## Directions and Group Roles

Work in your POGIL team with rotated roles (**Manager**, **Recorder**, **Presenter**, **Reflector**). Consider each model and question individually first, then discuss with your group. The Recorder posts answers to the Class Activity Questions discussion board; the Presenter reports out areas of disagreement or alternative approaches. After class, respond to the reflective prompt individually in your notebook.

---

# Part I: Selection and Truth

## 1. The Semantics of If

**Selection evaluates the condition, then exactly one branch.** The "exactly one" is load-bearing: in `if (x != 0) { print 10 / x; } else { print 0; }`, evaluating the untaken branch would divide by zero. Your executor already respects this (the Python `if` inside `execute` chooses *which subtree to walk*), and naming the property matters: `if` is our first **non-strict** construct, one that deliberately does not evaluate all of its parts.

**Truthiness: what may stand as a condition?** Three coherent policies: (a) **booleans only** (Java): `if (count)` is a type error; (b) **everything has a truth value** (Python: zero, empty string, and empty collections are falsy; the rest truthy); (c) **a designated set** (C: zero is false, any nonzero number true). The policy interacts with your type system: a booleans-only language catches `if (x = 5)`-style accidents that permissive languages execute happily.

---

## Model 1: The Truthiness Tribunal

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

## 2. And/Or That Stop Early

**Short-circuit operators evaluate left to right and stop as soon as the answer is known**: `false and X` never evaluates `X`; `true or X` never evaluates `X`. This is not an optimization but a *semantic guarantee* programs rely on: `if (i < len(a) and a[i] > 0)` is only safe because the bounds check guards the access. Implementing it means `and`/`or` cannot be ordinary `BinOp`s (your `BinOp` case evaluates both children first, post-order); they need their own node and their own evaluation rule.

$$
\mathcal{E}[\![l \text{ and } r]\!] = \begin{cases} \mathcal{E}[\![l]\!] & \text{if } \mathcal{E}[\![l]\!] \text{ is falsy} \\ \mathcal{E}[\![r]\!] & \text{otherwise} \end{cases}
$$

(Note the Python-style refinement: returning the deciding *operand* rather than a normalized boolean is itself a design choice; Java normalizes, Python does not.)

---

## Model 3: Short-Circuit in Action

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

[[MC]]
The guarantee that `i < n and items[i] > 0` never indexes out of bounds depends on:
- ( ) The parser checking array lengths
- ( ) Operator precedence placing and below comparison
- (x) The semantic rule that and does not evaluate its right operand when the left is falsy
- ( ) The type checker proving i is a number

[[MC]]
In Python, `x or "default"` returns `"default"` when `x` is falsy. This behavior — returning the *operand* rather than normalizing to `True`/`False` — is called:
- ( ) Type coercion
- ( ) Lazy evaluation
- (x) Short-circuit evaluation with value-preserving semantics
- ( ) Boolean normalization

### Critical Thinking Questions

6. Trace why `LogicOp` cannot be folded into your `BinOp` case: quote the one line of the BinOp evaluator that makes it impossible.
7. Your parser must give `and`/`or` a precedence tier. Should `a == b and c == d` parse as `(a == b) and (c == d)`? Place the new tier in your precedence ladder (looser or tighter than comparison?) and justify with that example.
8. Python's `and`/`or` return one of their *operands*, not necessarily a boolean. So `"hello" and "world"` returns `"world"`, and `"" or "default"` returns `"default"`. Is this surprising? Name one production use of this behavior.

---

## Model 4: Language Comparison

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

## 3. While, and the Questions It Raises

Your `While` executor re-evaluates the condition before each pass: definite semantics, easy to implement, and the source of three design questions your team must answer in `SEMANTICS.md`:

1. Does the body create a fresh scope per iteration?
2. Do you provide `break`/`continue`, and if so, how?
3. Will you offer a counting `for`, and is it core syntax or sugar?

**The break/continue trick — use exception classes:**
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
