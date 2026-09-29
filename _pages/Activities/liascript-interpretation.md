<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374-Fall2026/gh-pages/_pages/Activities/liascript-interpretation.md or locally via https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374-Fall2026/gh-pages/_pages/Activities/liascript-interpretation.md

import: https://raw.githubusercontent.com/liascript/CodeRunner/master/README.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

# Tree-Walking Interpretation

You have a lexer (*Tokens and Scanning*) that turns characters into tokens, and a parser (*Recursive Descent Parsing*) that turns tokens into trees.  Today you build the third piece, the evaluator, which turns those trees into values.  The evaluator is the part that runs your program.  Two words matter here.  An *expression* is a piece of source code that describes a computation, such as `3 + price * 2`.  A *value* is the finished result of that computation, such as `13.0`.  The parser stores each expression as an abstract syntax tree (AST).  The evaluator computes the value of each AST node from the values of that node's children, and it uses the same rule at every node.  Because it walks the tree one node at a time, this kind of interpreter is called a tree-walking interpreter.  After today, no magic remains between source code and output.

## Learning Goals

By the end of this activity, you will be able to:

- Implement a recursive tree-walking evaluator and trace its post-order execution on a given AST
- Evaluate arithmetic, boolean, and comparison expressions by dispatching on AST node type and combining child values
- Explain the semantics of assignment, print, while, and if statements as implemented in the evaluator, including how control flow is handled
- Identify and resolve the semantic design decisions embedded in an evaluator (short-circuit evaluation, type coercion, division semantics)
- Integrate a lexer, parser, and evaluator into a working read-eval-print loop (REPL) and trace the complete pipeline from source string to printed output

This two-day module builds the evaluator: a recursive tree walk that turns ASTs into values.  Your pretty-printer from the AST module already has the right skeleton; the evaluator upgrades it to return values instead of printing text.  With lexer, parser, and evaluator joined, you will run a program in a language that exists because you built it.  Today's route runs **evaluation as recursion $\rightarrow$ the evaluator in code $\rightarrow$ semantics decisions hiding in plain sight $\rightarrow$ the REPL**.

---

> **Before You Begin:** This activity assumes you can:
> - Write recursive Python functions that call themselves on sub-parts of a data structure (tree recursion)
> - Define and instantiate Python `dataclass` types (`@dataclass`, field access with `node.field`)
> - Read and modify a Python dictionary (`env["x"] = 5`, `env.get("x")`, `"x" in env`)
> - Explain what a post-order tree traversal means (children processed before their parent)
>
> If any of these feel shaky, review them first.

---

## Directions and Group Roles

Work in your POGIL team with your rotated roles (**Manager**, **Recorder**, **Presenter**, **Reflector**).  Please think each model and question through on your own first, then talk it over with your group.  The Recorder posts your answers to the Class Activity Questions discussion board, and the Presenter reports out wherever you disagreed or found another approach.  After class, please respond to the reflective prompt on your own in your notebook.

---

# Part I: Evaluation Is a Fold over the Tree (Day 1)

## 0.  Interpreters and Compilers: When Does Translation Happen?

Before you write the evaluator, place it on the map.  There are two ways to make source text run, and the difference is *when* the translation work happens.  An interpreter reads the AST and computes values now.  A compiler translates the AST into another language, such as machine code or bytecode, that runs later.

| | **Interpreter** (what you build in this course) | **Compiler** |
|---|---|---|
| What it does with the AST | Walks it and computes values *now* | Translates it into another language (machine code, bytecode) to run *later* |
| When errors like `1 + "hello"` surface | While the program runs, at that expression | Possibly before the program runs at all |
| Cost model | Pays a small translation tax on every execution of every node | Pays translation once, then runs at full speed |
| Change the source? | Run it again | Recompile first |

The pipeline you have built so far (lexer -> parser -> AST) is the same for both.  They part ways only at this step.  A compiler for your class language would take the very same AST your parser produces and emit instructions instead of values.  (The *Table-Driven and LR Parsing* session's compile-link-load model and the *Build a Bytecode VM* tutorial walk that path.)  Everything you learn today about evaluation order and environments (the store of variable values) applies to both.

Quick check: a tree-walking interpreter and a compiler for the same language both receive the AST for `x * (y + 1)`.  What does each produce from it?

- [( )] Both produce the numeric answer
- [(X)] The interpreter produces the numeric answer; the compiler produces code that will compute it when run
- [( )] The interpreter produces machine code; the compiler produces the answer
- [( )] Both produce new source text in a different language

The central idea of Part I is simple to state: **the value of any expression is computed entirely from the values of its sub-expressions.**  A number node is its own value.  An addition node evaluates both children and adds the results.  This recursive definition is both the formal meaning of the language and the literal shape of the code you will write.

## 1.  The Recursive Definition of Meaning

The value of a node is defined in terms of the values of its children.  Written as rules, the definition looks like this:

$$
\mathcal{E}[\![\text{Num}(n)]\!] = n \qquad
\mathcal{E}[\![\text{BinOp}(+, l, r)]\!] = \mathcal{E}[\![l]\!] + \mathcal{E}[\![r]\!]
$$

Read $\mathcal{E}$ as "the value of."  The first rule says the value of a number node is the number itself.  The second says the value of an addition node is the value of its left child plus the value of its right child.  There is one such rule for every node class.  To apply them, evaluate the children first (post-order, exactly as Model 2 of the AST module predicted), then combine the results with the node's operation.  Functional programmers call this pattern a fold: one function walks the whole structure and combines each node's children into a single result.  Where the pretty-printer printed, the evaluator returns.  The recursion structure is identical, which is why "tree walk" is the most accurate possible name.

---

**Model 1 preview:** This model is the smallest complete core of a tree-walking evaluator.  It handles numbers, variables, unary negation, and the four arithmetic operators.  Every case follows the same pattern: inspect the node type, evaluate any children recursively, then combine.  The environment, `env`, is a Python dictionary that maps each variable name to its current value.  It is passed into every call so that a variable lookup always sees the current state.

## Model 1: The Evaluator, Build it from Scratch

This is the complete evaluator.  Every line matters.  Read it, trace it, then run it:

```python
from dataclasses import dataclass, field
from typing import Any, Optional

# --- AST Node Definitions ---------------------------------------------------
@dataclass
class Num:
    value: float

@dataclass
class Var:
    name: str

@dataclass
class UnaryOp:
    op: str
    operand: Any

@dataclass
class BinOp:
    op: str
    left: Any
    right: Any

# --- The Evaluator ----------------------------------------------------------
def evaluate(node, env):
    if isinstance(node, Num):
        return node.value
    if isinstance(node, Var):
        if node.name not in env:
            raise NameError(f"undefined variable {node.name!r}")
        return env[node.name]
    if isinstance(node, UnaryOp):
        val = evaluate(node.operand, env)
        return -val if node.op == "-" else val
    if isinstance(node, BinOp):
        left  = evaluate(node.left, env)   # children first: post-order
        right = evaluate(node.right, env)
        if node.op == "+": return left + right
        if node.op == "-": return left - right
        if node.op == "*": return left * right
        if node.op == "/":
            if right == 0:
                raise ZeroDivisionError("division by zero in your language")
            return left / right
        if node.op == "**": return left ** right
        raise ValueError(f"unknown operator {node.op!r}")
    raise TypeError(f"cannot evaluate {node!r}")

# --- Test --------------------------------------------------------------------
env = {"price": 5.0, "qty": 3}

# 3 + price * 2   (tree encodes precedence: * is deeper)
tree = BinOp("+", Num(3), BinOp("*", Var("price"), Num(2)))
print(f"3 + price*2 = {evaluate(tree, env)}")   # 13.0

# price * qty - 1
tree2 = BinOp("-", BinOp("*", Var("price"), Var("qty")), Num(1))
print(f"price*qty-1 = {evaluate(tree2, env)}")  # 14.0

# -(price + 1)
tree3 = UnaryOp("-", BinOp("+", Var("price"), Num(1)))
print(f"-(price+1) = {evaluate(tree3, env)}")   # -6.0
```
@LIA.eval(`["main.py"]`, `none`, `python3 main.py`)

**Step-by-step worked example, tracing `(+ 1 (* 2 3))`**

Suppose the AST is `BinOp("+", Num(1), BinOp("*", Num(2), Num(3)))` and `env = {}` (no variables yet).

```
evaluate( BinOp("+", Num(1), BinOp("*", Num(2), Num(3))), env )
  | It's a BinOp("+"), so evaluate children first (post-order):
  |- evaluate( Num(1), env )
  |    It's a Num -> return 1                              <- left = 1
  `- evaluate( BinOp("*", Num(2), Num(3)), env )
       | It's a BinOp("*"), evaluate children:
       |- evaluate( Num(2), env ) -> return 2             <- left = 2
       `- evaluate( Num(3), env ) -> return 3             <- right = 3
       2 * 3 = 6 -> return 6                              <- right = 6
  1 + 6 = 7 -> return 7
```

Three things to notice.  First, multiplication finishes entirely before addition sees any result.  Second, the environment is passed through every call but never consulted for `Num` nodes.  Third, the parser *already encoded* operator precedence in the tree's shape; the evaluator never re-derives it.

### Reading the Code

- The whole evaluator is one `if isinstance(...)` chain.  Each branch matches exactly one line of the recursive definition of meaning in section 1.  That match is the point: the definition *is* the program.
- The `Num` and `Var` branches are the base cases; they return without recursing.  Every other branch recurses first and combines afterward.  A recursive function over a tree always has this shape.
- `env` is passed to every call, including calls that cannot use it.  That uniformity lets you later swap the flat dictionary for a chained environment without touching any other branch.
- Nothing in the file mentions precedence, parentheses, or the grammar.  The parser did that work, and the tree that arrives here already records the answer in its shape.

> **Watch out!**  Students often try to evaluate the operator before the children (pre-order) by writing `result = node.op` and then recursing.  That fails: you need the children's *values* before you can apply the operator.  Evaluation of an expression is always post-order.

### Try It Yourself

Add a node type to the evaluator without touching any branch that already works.  This is the "new consumer of the AST" recipe from Critical Thinking Question (CTQ) 4, run in the other direction: a new *producer*.

```python
from dataclasses import dataclass
from typing import Any

@dataclass
class Num:   value: float
@dataclass
class BinOp: op: str; left: Any; right: Any
@dataclass
class Min:   left: Any; right: Any     # NEW: min(a, b)

def evaluate(node, env):
    if isinstance(node, Num):
        return node.value
    if isinstance(node, BinOp):
        l, r = evaluate(node.left, env), evaluate(node.right, env)
        return {"+": lambda: l + r, "-": lambda: l - r,
                "*": lambda: l * r, "/": lambda: l / r}[node.op]()

    # TODO 1: add the Min branch. Evaluate BOTH children, then return the
    #         smaller. Notice you cannot decide which child to return until
    #         both have been evaluated: that is post-order again.

    raise ValueError(f"unknown node: {type(node).__name__}")

tests = [
    ("min(3, 5)",          Min(Num(3), Num(5))),
    ("min(2 + 4, 3 * 2)",  Min(BinOp("+", Num(2), Num(4)), BinOp("*", Num(3), Num(2)))),
    ("min(1, 2) + 10",     BinOp("+", Min(Num(1), Num(2)), Num(10))),
]
for label, tree in tests:
    try:
        print(f"  {label:20} = {evaluate(tree, {})}")
    except ValueError as e:
        print(f"  {label:20} -> {e}")

# TODO 2: now add Max the same way, and note how many existing lines you had
#         to change to do it. That number is the architecture lesson.
```
@LIA.eval(`["main.py"]`, `none`, `python3 main.py`)

Expected output once `Min` is in place: `3`, `6`, and `11`.  Before you write it, predict how many *existing* lines you will have to modify.

### Critical Thinking Questions

1.  Trace `evaluate` on `3 + price * 2`.  Write every call with its arguments and return value, in order.  Where in your trace does the multiplication happen relative to the addition, and which week's design decision (which module) put it there?
2.  The evaluator never consults precedence, parentheses, or the grammar.  State exactly where precedence "went," and explain why this separation of concerns is the architecture lesson of the whole pipeline.
3.  We chose to make division by zero raise an error with a custom message.  List two other behaviors your team could have chosen (return infinity, return zero) and one language that makes each choice.  Record your project's decision.
4.  Compare `evaluate` and a tree pretty-printer line by line.  Write the general recipe: to add a new *consumer* of the AST (a type checker, an optimizer, a compiler), what do you write, and what do you never touch?

---

**Model 2 preview:** Model 1 was correct but silent.  This model adds tracing so you can *see* the call tree printed as `evaluate` runs.  It is the same recursion wearing a lab coat: each call announces itself before recursing and reports its result when it returns.  Study this output to build the mental picture you need before you write evaluators for richer node types.

## Model 2: Tracing Evaluation Step by Step

This instrumented evaluator prints the call tree as it runs:

```python
from dataclasses import dataclass
from typing import Any

@dataclass
class Num:
    value: float
@dataclass
class Var:
    name: str
@dataclass
class BinOp:
    op: str
    left: Any
    right: Any

_depth = 0

def evaluate_traced(node, env):
    global _depth
    indent = "  " * _depth
    _depth += 1
    result = _eval_inner(node, env, indent)
    _depth -= 1
    return result

def _eval_inner(node, env, indent):
    if isinstance(node, Num):
        print(f"{indent}Num({node.value}) -> {node.value}")
        return node.value
    if isinstance(node, Var):
        val = env[node.name]
        print(f"{indent}Var({node.name!r}) -> {val}  [lookup in env]")
        return val
    if isinstance(node, BinOp):
        print(f"{indent}BinOp({node.op!r}) - evaluating children...")
        left  = evaluate_traced(node.left, env)
        right = evaluate_traced(node.right, env)
        ops = {"+": lambda a,b: a+b, "-": lambda a,b: a-b,
               "*": lambda a,b: a*b, "/": lambda a,b: a/b}
        result = ops[node.op](left, right)
        print(f"{indent}BinOp({node.op!r}): {left} {node.op} {right} = {result}")
        return result

env = {"x": 4.0}
# 2 * x + 1
tree = BinOp("+", BinOp("*", Num(2), Var("x")), Num(1))
print("Evaluating: 2 * x + 1  where x=4")
print()
result = evaluate_traced(tree, env)
print(f"\nFinal result: {result}")
```
@LIA.eval(`["main.py"]`, `none`, `python3 main.py`)

### Reading the Code

- `evaluate_traced` is a thin wrapper that only manages indentation.  `_eval_inner` is Model 1's evaluator with `print` statements added.  The recursion is unchanged, so the trace is trustworthy: you are watching the real thing, not a simulation of it.
- Each `BinOp` prints twice: once *before* recursing ("evaluating children...") and once *after* ("`2 * 4 = 8`").  The lines between those two are exactly the subtree's evaluation.
- Indentation depth equals call-stack depth.  Read the output as a picture of the stack: every indent is a frame that has not returned yet.
- `ops` is a dictionary of lambdas, so only the selected operator runs.  If it were a dictionary of computed values, every entry would run, and a division by zero anywhere in the tree would surface at the wrong node.

### Try It Yourself

Make the tracer answer CTQ 6 for you: print the depth alongside the indentation.  Then guard it against the failure the "Watch out!" note below describes.

```python
from dataclasses import dataclass
from typing import Any

@dataclass
class Num:   value: float
@dataclass
class Var:   name: str
@dataclass
class BinOp: op: str; left: Any; right: Any

_depth = 0

def evaluate_traced(node, env):
    global _depth
    indent = "  " * _depth
    _depth += 1
    # TODO 1: wrap this in try/finally so _depth is restored even when a
    #         child raises. Then run the division-by-zero tree below TWICE
    #         and confirm the second trace is still indented correctly.
    result = _eval_inner(node, env, indent)
    _depth -= 1
    return result

def _eval_inner(node, env, indent):
    # TODO 2: print the numeric depth as well as the indentation, e.g.
    #         "[d=2]   Num(3.0) -> 3.0"
    if isinstance(node, Num):
        print(f"{indent}Num({node.value}) -> {node.value}")
        return node.value
    if isinstance(node, Var):
        val = env[node.name]
        print(f"{indent}Var({node.name!r}) -> {val}")
        return val
    if isinstance(node, BinOp):
        print(f"{indent}BinOp({node.op!r}) - evaluating children...")
        left  = evaluate_traced(node.left, env)
        right = evaluate_traced(node.right, env)
        ops = {"+": lambda: left+right, "-": lambda: left-right,
               "*": lambda: left*right, "/": lambda: left/right}
        result = ops[node.op]()
        print(f"{indent}BinOp({node.op!r}): {left} {node.op} {right} = {result}")
        return result

boom = BinOp("+", Num(1), BinOp("/", Num(3), Num(0)))
for attempt in (1, 2):
    print(f"--- attempt {attempt} ---")
    try:
        evaluate_traced(boom, {})
    except ZeroDivisionError as e:
        print(f"  ZeroDivisionError: {e}")
```
@LIA.eval(`["main.py"]`, `none`, `python3 main.py`)

Expected output as written: the second trace is indented *wrongly*, because `_depth` was never decremented when the exception unwound the stack.  Fix TODO 1 and the two traces become identical.

### Critical Thinking Questions

5.  The trace shows post-order evaluation: both children are evaluated *before* the parent combines them.  Name one language feature that would break this order (hint: short-circuit evaluation of `and`/`or`).
6.  How would you modify the tracer to also print the *depth* of recursion?  What would that depth correspond to in terms of the tree's structure?
7.  If a `BinOp` node is at depth 3 in the trace, how deep is the tree at that point?  Does depth in the call stack correspond exactly to depth in the AST?

> **Watch out!**  The global `_depth` counter works here because Python is single-threaded and evaluation is deterministic.  But it is fragile: if `evaluate_traced` ever raises an exception mid-recursion, `_depth` is left wrong and all later indentation is off.  In production tracing code, use a `try/finally` block so that `_depth -= 1` always runs.

---


# Part II: When Evaluation Fails

## 2.  Theory: An Error Is a Result Too

Model 1 quietly assumed every tree it received made sense.  Real input does not.  A `Var` node can name something the environment has never heard of.  A `/` node can be handed a zero.  An operator can arrive that the evaluator does not implement.  Each of those is a decision your language has to make *on purpose*, and the decision belongs in `SEMANTICS.md`.

There are three separate questions, and they are easy to run together:

- What counts as an error?  Is `1 / 0` an error, or is it infinity?  Is an unbound variable an error, or does it default to zero?  Different languages answer differently, and both answers are defensible.
- When is it detected?  Your evaluator finds these *while running*, which is the dynamic checking of the *Type Systems* session.  A static checker would find the unbound variable before the program started.
- What does the user see?  An error that says `KeyError: 'prise'` is a bug report about your interpreter.  An error that says `undefined variable 'prise' at line 3, column 12` is a bug report about the user's program.  Only the second is useful, and the difference is entirely in what you chose to carry through the recursion.

The practical consequence: error handling is not an afterthought bolted onto a finished evaluator.  It changes what every branch returns.  Deciding it now is much cheaper than retrofitting it in week 12.

## Examples: Three Failures, by Hand

For each tree below, say what your evaluator *should* do, before looking at what Model 3 does.  Write down the message you would want a student in CS174 to see.

| Tree | What is wrong | Your language's answer |
|------|---------------|------------------------|
| `BinOp("/", Num(1), Num(0))` | division by zero | ? |
| `Var("prise")` with `env = {"price": 3}` | a typo: no such name | ? |
| `BinOp("%", Num(7), Num(2))` | operator not implemented | ? |

The middle row is the interesting one.  A helpful interpreter can notice that `prise` is one character away from `price` and say so.  That costs about four lines, and it is the difference between a language people tolerate and one they enjoy.

## Model 3: Errors That Name the Program, Not the Interpreter

This evaluator carries a line and column number on every node, and it raises its own error type when the user's program is at fault:

```python
from dataclasses import dataclass
from typing import Any
import difflib

@dataclass
class Num:   value: float; line: int = 0; col: int = 0
@dataclass
class Var:   name: str;    line: int = 0; col: int = 0
@dataclass
class BinOp: op: str; left: Any; right: Any; line: int = 0; col: int = 0

class LangError(Exception):
    """An error in the USER'S program, not in our interpreter."""
    def __init__(self, msg, node):
        super().__init__(f"{msg} (line {node.line}, column {node.col})")

def evaluate(node, env):
    if isinstance(node, Num):
        return node.value

    if isinstance(node, Var):
        if node.name in env:
            return env[node.name]
        near = difflib.get_close_matches(node.name, list(env), n=1, cutoff=0.6)
        hint = f"; did you mean {near[0]!r}?" if near else ""
        raise LangError(f"undefined variable {node.name!r}{hint}", node)

    if isinstance(node, BinOp):
        left  = evaluate(node.left, env)
        right = evaluate(node.right, env)
        if node.op == "/" and right == 0:
            raise LangError("division by zero", node)
        ops = {"+": lambda: left + right, "-": lambda: left - right,
               "*": lambda: left * right, "/": lambda: left / right}
        if node.op not in ops:
            raise LangError(f"operator {node.op!r} is not supported", node)
        return ops[node.op]()

    raise LangError(f"cannot evaluate a {type(node).__name__} node", node)

env = {"price": 3.0, "qty": 4.0}

print("=== Programs that work ===")
for label, tree in [
    ("price * qty", BinOp("*", Var("price", 1, 1), Var("qty", 1, 9), 1, 7)),
    ("price + 1",   BinOp("+", Var("price", 2, 1), Num(1, 2, 9), 2, 7)),
]:
    print(f"  {label:16} = {evaluate(tree, env)}")

print("\n=== Programs that fail, each blaming the right line ===")
failures = [
    ("1 / 0",       BinOp("/", Num(1, 3, 1), Num(0, 3, 5), 3, 3)),
    ("prise + 1",   BinOp("+", Var("prise", 4, 1), Num(1, 4, 9), 4, 7)),
    ("qtyy * 2",    BinOp("*", Var("qtyy", 5, 1), Num(2, 5, 8), 5, 6)),
    ("7 % 2",       BinOp("%", Num(7, 6, 1), Num(2, 6, 5), 6, 3)),
]
for label, tree in failures:
    try:
        evaluate(tree, env)
    except LangError as e:
        print(f"  {label:16} -> {e}")

print("\nCompare with what an unguarded evaluator would have printed:")
print("  KeyError: 'prise'")
print("That is a bug report about the interpreter. The messages above are")
print("bug reports about the user's program, which is the whole difference.")
```
@LIA.eval(`["main.py"]`, `none`, `python3 main.py`)

### Reading the Code

- Every node now carries `line` and `col`.  The parser fills these in; the evaluator only has to *pass them along* to the error.  That is why deciding on errors early matters: adding these fields later means touching every node class and every place a node is built.
- `LangError` is a separate class from Python's built-in exceptions on purpose.  When you catch `LangError` in your REPL, you know it is the user's mistake.  When a bare `KeyError` escapes, that is *your* bug, and it should crash loudly.
- The `difflib.get_close_matches` call is the entire "did you mean" feature.  Four lines, and it is what students will remember about your language.
- The `/` check happens *before* the `ops` dictionary is consulted, because `1 / 0` must produce your message rather than Python's `ZeroDivisionError`.
- The final `raise` is a real safety net.  An evaluator that silently returns `None` for an unknown node type produces a wrong answer somewhere far away instead of an error here.

> **Watch out!**  It is tempting to make the evaluator return a sentinel (a placeholder value such as `None` or `-1`) on error instead of raising.  Do not.  A sentinel propagates: `None + 1` fails somewhere else entirely, and the reported line number belongs to innocent code.  Raise at the point of discovery, where you still know which node was to blame.

### Critical Thinking Questions

8.  Model 3 raises on an unbound variable.  Name a real language that instead gives unbound names a default value, and describe one bug that choice makes easy to write and hard to find.
9.  The `line`/`col` fields are threaded through the AST, but the evaluator never *reads* them except when raising.  What would it cost, in lines changed, to add them to a language that did not have them from the start?
10. `LangError` is caught by the caller, not by `evaluate`.  Where should your REPL catch it, and what should it do afterward: exit, or print and continue reading?  What does Python's REPL do?

### Try It Yourself

Give your language a policy for one more failure, and make the message earn its keep.

```python
from dataclasses import dataclass
from typing import Any
import difflib

@dataclass
class Num:   value: float; line: int = 0; col: int = 0
@dataclass
class Var:   name: str;    line: int = 0; col: int = 0
@dataclass
class BinOp: op: str; left: Any; right: Any; line: int = 0; col: int = 0

class LangError(Exception):
    def __init__(self, msg, node):
        super().__init__(f"{msg} (line {node.line}, column {node.col})")

def evaluate(node, env):
    if isinstance(node, Num):  return node.value
    if isinstance(node, Var):
        if node.name in env: return env[node.name]
        near = difflib.get_close_matches(node.name, list(env), n=1, cutoff=0.6)
        hint = f"; did you mean {near[0]!r}?" if near else ""
        raise LangError(f"undefined variable {node.name!r}{hint}", node)
    if isinstance(node, BinOp):
        left, right = evaluate(node.left, env), evaluate(node.right, env)

        # TODO 1: decide what "/" by zero does in YOUR language. Pick one and
        #         implement it: raise, return float('inf'), or return 0.
        # TODO 2: add "%" (remainder). What does it do when right is 0?
        #         Your answer should be consistent with your TODO 1 choice.

        ops = {"+": lambda: left + right, "-": lambda: left - right,
               "*": lambda: left * right, "/": lambda: left / right}
        if node.op not in ops:
            raise LangError(f"operator {node.op!r} is not supported", node)
        return ops[node.op]()
    raise LangError(f"cannot evaluate a {type(node).__name__} node", node)

for label, tree in [("7 % 2", BinOp("%", Num(7,1,1), Num(2,1,5), 1, 3)),
                    ("7 % 0", BinOp("%", Num(7,2,1), Num(0,2,5), 2, 3)),
                    ("1 / 0", BinOp("/", Num(1,3,1), Num(0,3,5), 3, 3))]:
    try:
        print(f"  {label:8} = {evaluate(tree, {})}")
    except LangError as e:
        print(f"  {label:8} -> {e}")
    except ZeroDivisionError as e:
        # Catching this separately is itself the lesson: until you decide,
        # Python decides for you, and its message names no line of the
        # user's program.
        print(f"  {label:8} -> raw Python {type(e).__name__}: {e}")
```
@LIA.eval(`["main.py"]`, `none`, `python3 main.py`)

Expected output as written: the first two report that `%` is unsupported, and the third divides by zero.  Once your TODOs are in, write the three resulting behaviors into `SEMANTICS.md` as one sentence each.  That paragraph is a deliverable of the Interpreter assignment.

---

> **Continued next session.**  Statements, state, and the REPL are Day 2 of this topic: [Control Flow and Statement Semantics](https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374-Fall2026/gh-pages/_pages/Activities/liascript-controlflowsemantics.md).

# Part III: Tree Traversal, Why Post-Order, Not Breadth-First

## Model 4: BFS vs DFS, Why Evaluators Use Post-Order

When you evaluate an AST, you always use *depth-first, post-order* traversal: left child first, right child next, then the current node.  Depth-first search (DFS) follows one branch all the way down before it moves to the next branch.  Breadth-first search (BFS) visits the tree level by level instead: the root, then all of its children, then all of their children.  BFS looks simpler, so why not use it?  This model runs both traversals on the same tree and makes the answer concrete.  Evaluating a node requires its children's *values*, and those exist only after the children have been fully evaluated.  BFS visits a node before any of its children, so it can never satisfy the "children before parent" requirement of evaluation.

> *Adapted from [`bfs.py`](https://github.com/chuckallison/foundations-of-computing/blob/main/code/bfs.py) in *Foundations of Computing* by Chuck Allison (Fresh Sources, Inc.), used under the [MIT License](https://github.com/chuckallison/foundations-of-computing/blob/main/LICENSE).*

```python
from dataclasses import dataclass, field
from typing import Optional, Any
from collections import deque

@dataclass
class TreeNode:
    label: str
    children: list = field(default_factory=list)

def bfs_traversal(root: TreeNode) -> list[str]:
    """Breadth-first (level-by-level) traversal."""
    if root is None:
        return []
    result = []
    queue = deque([root])
    while queue:
        node = queue.popleft()
        result.append(node.label)
        for child in node.children:
            queue.append(child)
    return result

def dfs_postorder(root: TreeNode) -> list[str]:
    """Depth-first, post-order traversal: children before parent."""
    if root is None:
        return []
    result = []
    for child in root.children:
        result.extend(dfs_postorder(child))
    result.append(root.label)   # parent LAST
    return result

def dfs_preorder(root: TreeNode) -> list[str]:
    """Depth-first, pre-order traversal: parent before children."""
    if root is None:
        return []
    result = [root.label]       # parent FIRST
    for child in root.children:
        result.extend(dfs_preorder(child))
    return result

# Expression tree for  (1 + 2) * 3
#       *
#      / \
#     +   3
#    / \
#   1   2
# Represented as a general tree (each internal node has a list of children):
expr_tree = TreeNode('*', [
    TreeNode('+', [
        TreeNode('1'),
        TreeNode('2'),
    ]),
    TreeNode('3'),
])

bfs_order   = bfs_traversal(expr_tree)
post_order  = dfs_postorder(expr_tree)
pre_order   = dfs_preorder(expr_tree)

print("=== (1 + 2) * 3 ===")
print(f"  BFS order:       {' '.join(bfs_order)}")
print(f"  DFS pre-order:   {' '.join(pre_order)}")
print(f"  DFS post-order:  {' '.join(post_order)}")

print()
print("Why post-order works for evaluation:")
print("  Post-order visits '1' then '2' then '+', so when we")
print("  process '+' both operand values are already known.")
print()
print("Why BFS does NOT work for evaluation:")
print("  BFS visits '*' before '+' (at level 0 before level 1),")
print("  but to evaluate '*' we need the VALUE of '+' first.")

# Simulate evaluation with post-order
def eval_postorder(root: TreeNode) -> float:
    """Evaluate an expression tree using post-order recursion."""
    if not root.children:            # leaf node
        return float(root.label)
    child_vals = [eval_postorder(c) for c in root.children]
    ops = {'+': sum(child_vals), '-': child_vals[0] - child_vals[1],
           '*': child_vals[0] * child_vals[1], '/': child_vals[0] / child_vals[1]}
    return ops[root.label]

print(f"\nEvaluated result: {eval_postorder(expr_tree)}  (expected 9.0)")
```
@LIA.eval(`["main.py"]`, `none`, `python3 main.py`)

**CTQ M4.1** The BFS order for `(1 + 2) * 3` is `* + 3 1 2`.  Explain exactly why you *cannot* evaluate the tree by processing nodes in this order.  Which node in the BFS order is visited before its children's values are available?

**CTQ M4.2** Post-order guarantees that every node is processed *after all its descendants*.  Is this property true of DFS pre-order as well?  Give a concrete example of a case where pre-order evaluation fails for the same reason BFS fails.

**CTQ M4.3** The `eval_postorder` function uses recursion, so the call stack is implicit.  Rewrite it iteratively using an explicit stack, producing the same result.  What is the relationship between the recursive call stack and the explicit stack you used?

---

# Check Your Understanding

An evaluator that processes an AST uses which traversal order?

[( )] Breadth-first (level by level)
[( )] Pre-order (root before children)
[(X)] Post-order (children before root)
[( )] In-order (left child, root, right child)

A pretty-printer that prints operators *between* their operands uses which traversal?

[( )] Post-order
[( )] Pre-order
[(X)] In-order (with parentheses)
[( )] Breadth-first

The BFS traversal of the tree for `(1 + 2) * 3` visits nodes in order:

[( )] `1 2 + 3 *`: that is post-order, the evaluation order
[(X)] `* + 3 1 2`: the root first, then level 1, then the leaves
[( )] `* + 1 2 3`: BFS does not skip the `3` at level 1
[( )] `1 + 2 * 3`: that is in-order, what a pretty-printer uses

---

In Model 3, why does `evaluate` raise at the node where the problem is found rather than returning a sentinel value?

[(X)] A sentinel propagates, so the failure surfaces far from its cause and blames the wrong line
[( )] Python does not allow a function to return `None`
[( )] Raising is faster than returning
[( )] The parser cannot attach line numbers unless an exception is raised

---

# Exercises

1.  *Three traversals.*  Build the expression tree for `a * b + c * d` (where `+` is the root).  Write out all three traversal orders by hand, then verify with code.

2.  *BFS on a program AST.* Consider the AST for:
   ```
   while (x > 0) {
       x = x - 1;
       print x;
   }
   ```
   Draw the tree.  Then list the nodes in BFS order and in post-order.  Explain why the evaluator *must* use post-order for the body and cannot use BFS.

3.  *Iterative post-order.*  Rewrite `eval_postorder` using an explicit stack (no recursion).  Test it on both trees from Model 4 (above) and on an AST from the *Abstract Syntax Trees* activity.

4.  *Tree statistics.*  Write `max_depth(root)` and `node_count(root)` as tree walks.  For the BFS traversal of a complete binary tree of depth 4, how many nodes are at level 3?  Verify with code.

5.  *Interpreter extension.*  In your interpreter's `evaluate` function, add a `depth` counter that increments on each recursive call and prints the current depth at each node.  Run it on a deeply nested expression like `((((1 + 2) + 3) + 4) + 5)`.  What is the maximum depth, and how does it relate to the number of operators?

---

## Reflection Prompt

In your notebook: you have now run a program in a language whose every component you understand, with no magic remaining between the characters and the answer.  How does that change how you regard the languages you use daily?  Which stage of the pipeline surprised you most, and what magic do you now most want to dispel next (type checking? closures? garbage collection?)?

---

## 4.  Further Reading

- Douglas Thain.  *Introduction to Compilers and Language Design*, Chapter 5 and interpretation notes.
- Robert Nystrom.  *Crafting Interpreters*, "Evaluating Expressions" and "Statements and State" (online): our exact path, expanded.
- Shriram Krishnamurthi.  *PLAI*, the interpreter chapters, for the denotational view.
- Python's `ast.NodeVisitor`: the standard library's version of the visitor pattern you just wrote by hand.
- [Build a Complete Interpreter in Python](https://www.billmongan.com/Ursinus-CS374-Fall2026/Tutorials/BuildAnInterpreter): the whole pipeline assembled as one program, covering tokenizer, parser, evaluator, statement executor, error reporting, closures, and a REPL.  The start-to-finish companion for the Interpreter assignment.
- Operational semantics: specifying a language with inference rules, big-step and small-step judgments, and derivation trees.  Chapter 3 of Benjamin Pierce's *Types and Programming Languages*.

---

Up next: the *Control Flow and Statement Semantics* activity finishes the evaluator by pinning down which code runs and in what order.  *Binding and Scope* follows it and confronts the first crack in this design, the single flat dictionary of variables.  Together the three anchor the Interpreter assignment.
