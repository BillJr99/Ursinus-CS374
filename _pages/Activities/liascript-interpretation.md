<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://github.com/BillJr99/Ursinus-CS374-Fall2026/blob/gh-pages/_pages/Activities/liascript-interpretation.md or locally via https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374-Fall2026/gh-pages/_pages/Activities/liascript-interpretation.md

import: https://raw.githubusercontent.com/liascript/CodeRunner/master/README.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

# Tree-Walking Interpretation

You have a lexer that turns characters into tokens and a parser that turns tokens into trees. Now comes the payoff: the **evaluator** turns those trees into *values* — it is the part that actually *runs* your program. Think of it as a universal translator: given any sentence in the source language (an AST node), it produces the meaning (a Python value) directly, by asking the same question recursively of every sub-sentence. After today, no magic remains between source code and output.

## Learning Goals

By the end of this activity, you will be able to:

- Implement a recursive tree-walking evaluator and trace its post-order execution on a given AST
- Evaluate arithmetic, boolean, and comparison expressions by dispatching on AST node type and combining child values
- Explain the semantics of assignment, print, while, and if statements as implemented in the evaluator, including how control flow is handled
- Identify and resolve the semantic design decisions embedded in an evaluator (short-circuit evaluation, type coercion, division semantics)
- Integrate a lexer, parser, and evaluator into a functioning REPL and trace the complete pipeline from source string to printed output

The pipeline completes its first full circuit: this two-day module builds the **evaluator**, the recursive tree walk that turns ASTs into values, upgrading your pretty-printer's skeleton into an interpreter. With lexer, parser, and evaluator joined, you will run a program in a language that exists because you built it. The arc: **evaluation as recursion $\rightarrow$ the evaluator in code $\rightarrow$ semantics decisions hiding in plain sight $\rightarrow$ the REPL**.

---

> **Before You Begin:** This activity assumes you can:
> - Write recursive Python functions that call themselves on sub-parts of a data structure (tree recursion)
> - Define and instantiate Python `dataclass` types (`@dataclass`, field access with `node.field`)
> - Read and modify a Python dictionary (`env["x"] = 5`, `env.get("x")`, `"x" in env`)
> - Understand what a post-order tree traversal means (children processed before their parent)
>
> If any of these feel shaky, review them first.

---

## Directions and Group Roles

Work in your POGIL team with rotated roles (**Manager**, **Recorder**, **Presenter**, **Reflector**). Consider each model and question individually first, then discuss with your group. The Recorder posts answers to the Class Activity Questions discussion board; the Presenter reports out areas of disagreement or alternative approaches. After class, respond to the reflective prompt individually in your notebook.

---

# Part I: Evaluation Is a Fold over the Tree (Day 1)

The central idea of Part I is deceptively simple: **the value of any expression is computed entirely from the values of its sub-expressions.** A number node is its own value; an addition node evaluates both children and adds the results. This recursive definition is both the formal semantics of the language and the literal shape of the code you will write.

## 1. The Recursive Definition of Meaning

**The value of a node is defined in terms of the values of its children.** This is denotational thinking made executable:

$$
\mathcal{E}[\![\text{Num}(n)]\!] = n \qquad
\mathcal{E}[\![\text{BinOp}(+, l, r)]\!] = \mathcal{E}[\![l]\!] + \mathcal{E}[\![r]\!]
$$

and so on for every node class: evaluate children first (post-order, exactly as Model 2 of the AST module predicted), then combine with the node's operation. Where the pretty-printer printed, the evaluator returns; the recursion structure is identical, which is why a tree walk is the most honest possible name.

---

**Model 1 preview:** This model shows the minimal but complete core of a tree-walking evaluator. It handles numbers, variables, unary negation, and the four arithmetic operators. The key insight is that every case follows the same pattern — inspect the node type, recursively evaluate any children, then combine. Notice that the environment (`env`) is passed into every call so that variable lookups always reflect current state.

## Model 1: The Evaluator — Build it from Scratch

This is the complete evaluator. Every line is consequential. Read it, trace it, then run it:

```python
from dataclasses import dataclass, field
from typing import Any, Optional

# ─── AST Node Definitions ───────────────────────────────────────────────────
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

# ─── The Evaluator ──────────────────────────────────────────────────────────
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

# ─── Test ────────────────────────────────────────────────────────────────────
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
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

**Step-by-step worked example — tracing `(+ 1 (* 2 3))`**

Suppose the AST is `BinOp("+", Num(1), BinOp("*", Num(2), Num(3)))` and `env = {}`.

```
evaluate( BinOp("+", Num(1), BinOp("*", Num(2), Num(3))), env )
  │ It's a BinOp("+"), so evaluate children first (post-order):
  ├─ evaluate( Num(1), env )
  │    It's a Num → return 1                              ← left = 1
  └─ evaluate( BinOp("*", Num(2), Num(3)), env )
       │ It's a BinOp("*"), evaluate children:
       ├─ evaluate( Num(2), env ) → return 2             ← left = 2
       └─ evaluate( Num(3), env ) → return 3             ← right = 3
       2 * 3 = 6 → return 6                              ← right = 6
  1 + 6 = 7 → return 7
```

**Key observations:** (1) Multiplication finishes entirely before addition sees any result. (2) The environment is threaded through every call but never consulted for `Num` nodes. (3) Operator precedence was *already encoded* in the tree structure by the parser — the evaluator never re-derives it.

> **Watch out!** Students often try to evaluate the operator before the children (pre-order) by writing `result = node.op` and then recursing. That will fail: you need the children's *values* before you can apply the operator. Evaluation is always post-order for expressions.

### Critical Thinking Questions

1. Trace `evaluate` on `3 + price * 2`, writing every call with its arguments and return value in order. Where in your trace does the multiplication happen relative to the addition, and which week's design decision (which module) put it there?
2. The evaluator never consults precedence, parentheses, or the grammar. State precisely where precedence "went," and why this separation of concerns is the architecture lesson of the whole pipeline.
3. We chose to make division by zero raise an error with a custom message. List two other behaviors your team could have chosen (return infinity, return zero) and one language that makes each choice. Record your project's decision.
4. Compare `evaluate` and a tree pretty-printer line by line. Write the general recipe: to add a new *consumer* of the AST (a type checker, an optimizer, a compiler), what do you write and what do you never touch?

---

**Model 2 preview:** Model 1 was correct but silent. This model adds instrumented tracing so you can *see* the call tree printed as `evaluate` runs. It is the same recursion wearing a lab coat — each call announces itself before recursing and reports its result when it returns. Studying this output is the fastest way to build the mental model you need before writing evaluators for richer node types.

## Model 2: Tracing Evaluation Step by Step

Instrumented evaluator that shows the call tree:

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
        print(f"{indent}Num({node.value}) → {node.value}")
        return node.value
    if isinstance(node, Var):
        val = env[node.name]
        print(f"{indent}Var({node.name!r}) → {val}  [lookup in env]")
        return val
    if isinstance(node, BinOp):
        print(f"{indent}BinOp({node.op!r}) — evaluating children...")
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
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

### Critical Thinking Questions

5. The trace shows post-order evaluation: both children are evaluated *before* the parent combines them. Name one language feature that would break this order (hint: short-circuit evaluation of `and`/`or`).
6. How would you modify the tracer to also print the *depth* of recursion? What would that depth correspond to in terms of the tree's structure?
7. If a `BinOp` node is at depth 3 in the trace, how deep is the tree at that point? Does depth in the call stack correspond exactly to depth in the AST?

> **Watch out!** The global `_depth` counter works here because Python is single-threaded and evaluation is deterministic, but it is fragile: if `evaluate_traced` ever raises an exception mid-recursion, `_depth` is left in a wrong state and all future indentation will be off. In production tracing code, use a `try/finally` block to ensure `_depth -= 1` always runs.

---

# Part II: Statements, State, and the REPL (Day 2)

## 2. Executing Statements

Expressions produce values; **statements produce effects**: an `Assign` updates the environment, a `Print` writes output, a `Block` executes children in order, a `While` re-evaluates its condition. The executor therefore threads the environment through:

```
def execute(stmt, env):
    Assign(name, e)   -> env[name] = evaluate(e, env)
    Print(e)          -> print(evaluate(e, env))
    Block(stmts)      -> for s in stmts: execute(s, env)
    If(c, t, o)       -> execute(t if truthy(evaluate(c, env)) else o, env)
    While(c, body)    -> while truthy(evaluate(c, env)): execute(body, env)
```

Notice `truthy`: your language must decide what counts as true (only a boolean? any nonzero number? an empty string?), a semantics decision with daily consequences.

[[MC]]
In a tree-walking interpreter, executing the program's `while` loop one million times will re-walk the loop body's subtree one million times. The principal cost this design accepts, relative to compilation, is:
- ( ) Incorrect results on large inputs
- (x) Repeated traversal and dispatch overhead per execution of the same code
- ( ) Loss of operator precedence
- ( ) The inability to support variables

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

## 3. Exercises

1. *Complete the executor.* Implement `execute` for all your statement nodes with the exception pattern from class, define and document `truthy` for your language, and demonstrate the summation program plus an `if/else` program.
2. *The REPL.* Write the read-evaluate-print loop: prompt, read a line, tokenize, parse, execute against a persistent environment, repeat, catching and printing every error class without dying. Your language now has an interactive shell; transcript required.
3. *Error taxonomy.* Construct one program each that fails in the lexer, the parser, and the evaluator. Verify each error message names its stage and location; improve the worst one.
4. *Semantics memo.* Document three semantics decisions your team made today (truthiness, division by zero, loop variable persistence) in a `SEMANTICS.md` your project will grow all semester.
5. *Interpreter speedup.* Modify the `While` executor to count the number of times the loop body executes. Then add a "step limit" parameter that raises a `RuntimeError` if the loop exceeds 10,000 iterations. This protects against infinite loops in student-written programs. Show it triggering on `while 1 > 0: print 1`.

---

# Part III: Tree Traversal — Why Post-Order, Not Breadth-First

## Model 4: BFS vs DFS — Why Evaluators Use Post-Order

When you evaluate an AST, you always use *depth-first, post-order* traversal: left child first, right child next, then the current node. But why not breadth-first search? After all, BFS is the "level-by-level" traversal, and it seems simpler. This model shows both traversals on the same tree and makes the answer concrete: evaluating a node requires its children's *values*, which are only available after the children have been fully evaluated. BFS visits children of a node before it visits their children's children — it cannot satisfy the "children before parent" requirement of evaluation.

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
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

**CTQ M4.1** The BFS order for `(1 + 2) * 3` is `* + 3 1 2`. Explain precisely why you *cannot* evaluate the tree by processing nodes in this order. Which node in the BFS order is visited before its children's values are available?

**CTQ M4.2** Post-order guarantees that every node is processed *after all its descendants*. Is this property true of DFS pre-order as well? Give a concrete example of a case where pre-order evaluation fails for the same reason BFS fails.

**CTQ M4.3** The `eval_postorder` function uses recursion — but the call stack is implicit. Rewrite it iteratively using an explicit stack, producing the same result. What is the relationship between the recursive call stack and the explicit stack you used?

---

## Practice — Allison Reading 6.3

[[MC]]
An evaluator that processes an AST uses which traversal order?
- ( ) Breadth-first (level by level)
- ( ) Pre-order (root before children)
- (x) Post-order (children before root)
- ( ) In-order (left child, root, right child)

[[MC]]
A pretty-printer that prints operators *between* their operands uses which traversal?
- ( ) Post-order
- ( ) Pre-order
- (x) In-order (with parentheses)
- ( ) Breadth-first

[[MC]]
The BFS traversal of the tree for `(1 + 2) * 3` visits nodes in order:
- ( ) `1 2 + 3 *`
- ( ) `* + 3 1 2`
- (x) `* + 3 1 2` — root first, then level 1, then leaves
- ( ) `1 + 2 * 3`

1. *Three traversals.* Build the expression tree for `a * b + c * d` (where `+` is the root). Write out all three traversal orders by hand, then verify with code.

2. *BFS on a program AST.* Consider the AST for:
   ```
   while (x > 0) {
       x = x - 1;
       print x;
   }
   ```
   Draw the tree. Then list the nodes in BFS order and in post-order. Explain why the evaluator *must* use post-order for the body and cannot use BFS.

3. *Iterative post-order.* Rewrite `eval_postorder` using an explicit stack (no recursion). Test it on both trees from Model 4 and Model 6 (of the AST activity).

4. *Tree statistics.* Write `max_depth(root)` and `node_count(root)` as tree walks. For the BFS traversal of a complete binary tree of depth 4, how many nodes are at level 3? Verify with code.

5. *Interpreter extension.* In your interpreter's `evaluate` function, add a `depth` counter that increments on each recursive call and prints the current depth at each node. Run it on a deeply nested expression like `((((1 + 2) + 3) + 4) + 5)`. What is the maximum depth, and how does it relate to the number of operators?

---

## Reflection Prompt

In your notebook: you have now run a program in a language whose every component you understand, with no magic remaining between the characters and the answer. How does that change how you regard the languages you use daily? Which stage of the pipeline surprised you most, and what magic do you now most want to dispel next (type checking? closures? garbage collection?)?

---

## 4. Further Reading

- Douglas Thain. *Introduction to Compilers and Language Design*, Chapter 5 and interpretation notes.
- Robert Nystrom. *Crafting Interpreters*, "Evaluating Expressions" and "Statements and State" (online): our exact path, expanded.
- Shriram Krishnamurthi. *PLAI*, the interpreter chapters, for the denotational view.
- Python's `ast.NodeVisitor` — the standard library's version of the visitor pattern you just wrote by hand.

## Going Deeper (Optional Appendices)

The core lesson above stands on its own. The optional deep dives below expand on it — read whichever interest you:

- Parsing and Interpreting: Putting It All Together
- Operational Semantics: Specifying Languages with Inference Rules

## Going Deeper: Parsing and Interpreting: Putting It All Together

Think of the **parser** as the reader and the **interpreter** as the thinker. Parsing converts raw source text into a structured tree — the Abstract Syntax Tree — by recognizing the grammar of the language, much like a reader turning printed words into sentences. Interpretation then walks that tree and gives it meaning: it decides what each node *does*, computing values, updating variables, and producing output. Keeping these two phases separate is one of the great design principles of language implementation — it lets you swap out the interpreter (for a compiler, a type checker, or an optimizer) without touching the parser.

#### Learning Goals

By the end of this activity, you will be able to:

- Trace a source string through the complete tokenizer → parser → evaluator pipeline and explain the data structure produced at each stage
- Implement a recursive descent parser that constructs an abstract syntax tree from a token stream for arithmetic and boolean expressions
- Construct an environment-passing interpreter that evaluates an AST, correctly handling variable lookup, function application, and nested scopes
- Identify and fix common interpreter bugs: incorrect precedence, wrong scoping rules, missing base cases in recursive evaluation
- Extend the pipeline with a new language feature — new syntax, new AST node, and new evaluation rule — end-to-end

**CS374 Principles of Programming Languages — Weeks 11–14**

**References:** Compilers (Dragon Book) Ch. 4–5 | PLAI Ch. 15–17

Over the past weeks you have studied grammars, tokens, scanning, recursive descent parsing, and LL/LR table construction. This activity brings those pieces together into a complete pipeline: **source text → tokens → abstract syntax tree → evaluated result**. By the end you will have a working mini-interpreter built from first principles.

> **Before You Begin — Prerequisites**
>
> This activity assumes you are comfortable with the following skills. Review the linked material if any feels shaky before proceeding:
>
> - **Writing a recursive-descent parser** — translating a BNF/EBNF grammar into a set of mutually recursive functions, one per non-terminal, that consume tokens and return AST nodes.
> - **Building Python dataclass AST nodes** — defining `@dataclass` classes to represent each syntactic construct (literals, operators, variables, control flow), including nested node references typed with `Any`.
> - **Writing a tree-walking evaluator function** — a single `evaluate(node, env)` function that dispatches on `isinstance` checks, recursively evaluates children, and returns a Python value.

---

#### Directions and Group Roles

This is a **POGIL** (Process-Oriented Guided Inquiry Learning) activity. Work in groups of 3–4 and assign the following roles before you begin. Rotate roles between models.

| Role | Responsibilities |
|------|-----------------|
| **Manager** | Keeps the group on task; tracks time; ensures everyone participates. |
| **Recorder** | Writes down group answers to Critical Thinking Questions (CTQs). |
| **Presenter** | Shares the group's answers with the class during discussion. |
| **Reflector** | Monitors group process; notes what is working and what is not. |

**How to use this activity:**

1. Read each Model's prose introduction carefully.
2. Run the code and observe the output.
3. Answer the CTQs in your group — discuss before writing.
4. Do not move to the next Model until the group agrees on answers.
5. Complete the Multiple Choice, Exercises, and Reflection at the end.

---

#### Model 1: The Complete Pipeline — From Source to Result

Before any parsing or evaluation can happen, the interpreter needs to break raw text into discrete, typed pieces. Imagine reading a math problem aloud: you naturally group characters into numbers, operator symbols, and parentheses before you start reasoning about what they mean. The tokenizer (also called a lexer or scanner) does exactly this — it scans left-to-right and emits a flat list of tokens that later stages can work with cleanly.

A programming language implementation transforms source text through several **stages**. Each stage produces a data structure that the next stage consumes:

```
Source string  →  [Tokenizer]  →  Token list
Token list     →  [Parser]     →  Abstract Syntax Tree (AST)
AST            →  [Evaluator]  →  Result value
```

The code below implements the first stage — the **tokenizer** (also called a *lexer* or *scanner*). It uses Python's `re` module to match patterns left-to-right across the source string, producing a list of typed tokens.

```python
import re
from dataclasses import dataclass
from typing import Any, Optional

# === TOKENIZER ===
@dataclass
class Token:
    type: str
    value: str
    line: int

def tokenize(source: str) -> list:
    patterns = [
        ('NUMBER',  r'\d+(\.\d+)?'),
        ('STRING',  r'"[^"]*"'),
        ('PLUS',    r'\+'),
        ('MINUS',   r'-'),
        ('STAR',    r'\*'),
        ('SLASH',   r'/'),
        ('LPAREN',  r'\('),
        ('RPAREN',  r'\)'),
        ('EQ',      r'=='),
        ('ASSIGN',  r'='),
        ('NAME',    r'[a-zA-Z_]\w*'),
        ('SKIP',    r'[ \t]+'),
        ('NEWLINE', r'\n'),
    ]
    master = '|'.join(f'(?P<{name}>{pat})' for name, pat in patterns)
    tokens = []
    line = 1
    for m in re.finditer(master, source):
        kind = m.lastgroup
        if kind == 'NEWLINE':
            line += 1
        elif kind != 'SKIP':
            tokens.append(Token(kind, m.group(), line))
    tokens.append(Token('EOF', '', line))
    return tokens

# Test tokenizer
source = "x = 3 + 4 * 2"
tokens = tokenize(source)
print("Tokens:")
for t in tokens:
    print(f"  {t.type:10} {t.value!r}")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

**Critical Thinking Questions — Model 1**

1. What does the tokenizer's `SKIP` pattern do, and why is it necessary? What would happen if whitespace were not explicitly handled?

   [[___ your answer here ___]]

2. The `EQ` pattern (`==`) is listed **before** `ASSIGN` (`=`) in the patterns list. Why does this order matter? What would go wrong if they were reversed?

   [[___ your answer here ___]]

3. What does the `EOF` sentinel token signal to downstream stages, and why is it useful to represent end-of-input explicitly as a token rather than relying on an empty list?

   [[___ your answer here ___]]

4. How does the `line` counter assist with error messages? Trace through what happens when the tokenizer encounters a `\n` character.

   [[___ your answer here ___]]

---

#### Model 2: Recursive Descent Parser

A flat list of tokens is like a list of words without punctuation or grammar — you know the vocabulary but not the sentence structure. The parser's job is to impose that structure by grouping tokens according to the grammar rules, producing a tree that encodes both *what* operators appear and *in what order* they should be applied. Each grammar rule becomes a function, and the nesting of those function calls is what gives operator precedence its meaning.

> **Watch out!** The parser and interpreter are **separate phases** — the parser only builds the tree; it never computes values. Mixing evaluation logic into parsing creates "spaghetti" code that is difficult to extend (adding a new feature requires changes scattered across both phases) and impossible to reuse the parser for other purposes like type checking or compilation.

The tokenizer gives us a flat list of tokens. The **parser** imposes grammatical structure by grouping tokens into an **Abstract Syntax Tree (AST)**. A recursive descent parser encodes the grammar directly as a set of mutually recursive functions.

The grammar for our expression language is:

```
expr    → add
add     → mul ( ('+' | '-') mul )*
mul     → primary ( ('*' | '/') primary )*
primary → NUMBER | NAME | '(' expr ')'
```

Notice that `add` calls `mul`, and `mul` calls `primary`. This nesting is how the grammar enforces **operator precedence**: multiplication binds more tightly than addition because `mul` sits deeper in the call stack.

```python
from dataclasses import dataclass
from typing import Any, Optional

# AST nodes
@dataclass
class Num:
    value: float

@dataclass
class Str:
    value: str

@dataclass
class Var:
    name: str
    line: int

@dataclass
class BinOp:
    op: str
    left: Any
    right: Any

@dataclass
class Assign:
    name: str
    value: Any

# Re-use Token from above for demonstration
class Token:
    def __init__(self, type_, value, line=0):
        self.type = type_; self.value = value; self.line = line
    def __repr__(self): return f"Token({self.type!r}, {self.value!r})"

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def peek(self): return self.tokens[self.pos]
    def advance(self):
        t = self.tokens[self.pos]
        self.pos += 1
        return t
    def expect(self, type_):
        t = self.advance()
        if t.type != type_:
            raise SyntaxError(f"Expected {type_}, got {t.type} ({t.value!r}) at line {t.line}")
        return t

    def parse_expr(self):
        return self.parse_add()

    def parse_add(self):
        left = self.parse_mul()
        while self.peek().type in ('PLUS', 'MINUS'):
            op = self.advance().value
            right = self.parse_mul()
            left = BinOp(op, left, right)
        return left

    def parse_mul(self):
        left = self.parse_primary()
        while self.peek().type in ('STAR', 'SLASH'):
            op = self.advance().value
            right = self.parse_primary()
            left = BinOp(op, left, right)
        return left

    def parse_primary(self):
        t = self.peek()
        if t.type == 'NUMBER':
            self.advance()
            return Num(float(t.value))
        if t.type == 'NAME':
            self.advance()
            return Var(t.value, t.line)
        if t.type == 'LPAREN':
            self.advance()
            expr = self.parse_expr()
            self.expect('RPAREN')
            return expr
        raise SyntaxError(f"Unexpected token: {t.type} ({t.value!r}) at line {t.line}")

# Test the parser
import re
def tokenize_simple(source):
    patterns = [('NUMBER',r'\d+'),('PLUS',r'\+'),('MINUS',r'-'),('STAR',r'\*'),
                ('SLASH',r'/'),('LPAREN',r'\('),('RPAREN',r'\)'),
                ('NAME',r'[a-zA-Z_]\w*'),('SKIP',r'\s+')]
    master = '|'.join(f'(?P<{n}>{p})' for n,p in patterns)
    toks = [Token(m.lastgroup, m.group()) for m in re.finditer(master, source) if m.lastgroup != 'SKIP']
    toks.append(Token('EOF', ''))
    return toks

tokens = tokenize_simple("3 + 4 * (2 - 1)")
parser = Parser(tokens)
tree = parser.parse_expr()

def pprint(node, indent=0):
    prefix = "  " * indent
    if isinstance(node, Num): print(f"{prefix}Num({node.value})")
    elif isinstance(node, Var): print(f"{prefix}Var({node.name})")
    elif isinstance(node, BinOp):
        print(f"{prefix}BinOp({node.op!r})")
        pprint(node.left, indent+1)
        pprint(node.right, indent+1)

print("AST for '3 + 4 * (2 - 1)':")
pprint(tree)
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

> **Watch out!** Never evaluate expressions *during* parsing. It is tempting to compute `3 + 4` the moment `parse_add` recognizes the `+` token, but doing so prevents you from transforming, optimizing, or type-checking the tree before execution. Always return an AST node from the parser and let the evaluator decide when and how to compute values.

**Critical Thinking Questions — Model 2**

1. Why does `parse_add` call `parse_mul` rather than `parse_primary`? Draw the call chain for parsing `3 + 4 * 2` and explain how the tree structure encodes precedence.

   [[___ your answer here ___]]

2. How does the grammar structure in the parser enforce that `*` binds more tightly than `+`? Would the precedence change if you swapped the bodies of `parse_add` and `parse_mul`?

   [[___ your answer here ___]]

3. What happens step-by-step when the parser sees `(` in `parse_primary`? Why does the parser call `parse_expr` recursively rather than `parse_primary`?

   [[___ your answer here ___]]

4. What specific error does `expect('RPAREN')` catch? Write an example input that would trigger this error and predict the error message.

   [[___ your answer here ___]]

---

#### Model 3: Tree-Walking Evaluator

With a well-formed AST in hand, evaluation becomes a simple recursive traversal: visit each node, evaluate its children first, then combine the results according to the node's operator or meaning. The other ingredient is the **environment** — a dictionary that maps variable names to their current values and grows as the program executes. Understanding how environments chain together is the key to understanding scope.

The parser produces an AST. The **evaluator** (also called an *interpreter*) walks that tree recursively, computing a result. This is the simplest evaluation strategy: **tree-walking interpretation**.

The evaluator needs an **environment** — a mapping from variable names to their current values. Environments can be chained: a child environment delegates to its parent when a name is not found locally. This chain implements **lexical scoping**.

```python
from dataclasses import dataclass, field
from typing import Any, Optional

@dataclass
class Num: value: float
@dataclass
class Var: name: str
@dataclass
class BinOp: op: str; left: Any; right: Any
@dataclass
class Assign: name: str; value_expr: Any
@dataclass
class If: cond: Any; then_branch: Any; else_branch: Any
@dataclass
class Print: expr: Any

@dataclass
class Env:
    bindings: dict = field(default_factory=dict)
    parent: Optional['Env'] = None

    def define(self, name, value): self.bindings[name] = value
    def lookup(self, name):
        if name in self.bindings: return self.bindings[name]
        if self.parent: return self.parent.lookup(name)
        raise NameError(f"Undefined variable: '{name}'")

def evaluate(node, env: Env) -> Any:
    if isinstance(node, Num):
        return node.value
    if isinstance(node, Var):
        return env.lookup(node.name)
    if isinstance(node, Assign):
        val = evaluate(node.value_expr, env)
        env.define(node.name, val)
        return val
    if isinstance(node, BinOp):
        l, r = evaluate(node.left, env), evaluate(node.right, env)
        match node.op:
            case '+': return l + r
            case '-': return l - r
            case '*': return l * r
            case '/':
                if r == 0: raise ZeroDivisionError("division by zero")
                return l / r
            case '==': return l == r
            case '<': return l < r
            case '>': return l > r
        raise ValueError(f"Unknown operator: {node.op}")
    if isinstance(node, If):
        return evaluate(node.then_branch, env) if evaluate(node.cond, env) \
               else evaluate(node.else_branch, env)
    if isinstance(node, Print):
        val = evaluate(node.expr, env)
        print(val)
        return val
    raise ValueError(f"Unknown node: {type(node).__name__}")

# Test: if 3 > 2 then x = 10 else x = 0; print(x)
env = Env()
program = [
    If(BinOp('>', Num(3), Num(2)),
       Assign("x", Num(10)),
       Assign("x", Num(0))),
    Print(Var("x")),
]
for stmt in program:
    evaluate(stmt, env)
print(f"x = {env.lookup('x')}")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

**Critical Thinking Questions — Model 3**

1. What does `evaluate` return for an `Assign` node? Why is it useful for assignment to return a value rather than `None`?

   [[___ your answer here ___]]

2. The `If` node only evaluates **one** branch — either `then_branch` or `else_branch`, but never both. Why is this the correct behavior? Give an example where evaluating both branches would produce incorrect or harmful results.

   [[___ your answer here ___]]

3. How would you add a `While` loop node to this interpreter? Sketch the dataclass definition and the case in `evaluate`. What could go wrong if the loop condition never becomes `False`?

   [[___ your answer here ___]]

4. What would happen if the `Env` class were removed entirely and the interpreter used a single global Python dictionary? Describe a program that would behave differently.

   [[___ your answer here ___]]

---

#### Model 4: A Complete REPL

The three pipeline stages — tokenize, parse, evaluate — can be chained together and wrapped in a loop to produce an interactive shell. A REPL lets you test your interpreter one expression at a time, immediately seeing how small changes to the language or environment affect results. It is one of the fastest ways to discover bugs in precedence, scoping, or error handling.

A **REPL** (Read-Eval-Print Loop) is an interactive shell that processes one expression or statement at a time. REPLs are invaluable for exploring a language interactively — Python's `>>>` prompt is one example.

The REPL maintains a persistent **environment** across inputs: a variable assigned in one line is still accessible in subsequent lines. Each iteration of the loop:

1. **Reads** a line of input,
2. **Evaluates** it (tokenize → parse → evaluate),
3. **Prints** the result,
4. **Loops** back to read the next line.

```python
import re
from dataclasses import dataclass, field
from typing import Any, Optional

# Abbreviated versions (assume tokenizer + parser + evaluator from above)
@dataclass
class Num: value: float
@dataclass
class Var: name: str
@dataclass
class BinOp: op: str; left: Any; right: Any
@dataclass
class Assign: name: str; value: Any
@dataclass
class Env:
    bindings: dict = field(default_factory=dict)
    def define(self, n, v): self.bindings[n] = v
    def lookup(self, n):
        if n in self.bindings: return self.bindings[n]
        raise NameError(f"Undefined: {n}")

def mini_eval(node, env):
    if isinstance(node, Num): return node.value
    if isinstance(node, Var): return env.lookup(node.name)
    if isinstance(node, Assign):
        v = mini_eval(node.value, env); env.define(node.name, v); return v
    if isinstance(node, BinOp):
        l, r = mini_eval(node.left, env), mini_eval(node.right, env)
        return {'+': l+r, '-': l-r, '*': l*r, '/': l/r}[node.op]
    raise ValueError(f"Unknown: {type(node)}")

def quick_parse(expr_str):
    """Parse: NAME=NUM, NAME, NUM, or NUM OP NUM."""
    expr_str = expr_str.strip()
    m = re.match(r'([a-z]+)\s*=\s*(.+)', expr_str)
    if m:
        return Assign(m.group(1), quick_parse(m.group(2)))
    m = re.match(r'(\d+(?:\.\d+)?)\s*([+\-*/])\s*(\d+(?:\.\d+)?)', expr_str)
    if m:
        ops = {'+': '+', '-': '-', '*': '*', '/': '/'}
        return BinOp(ops[m.group(2)], Num(float(m.group(1))), Num(float(m.group(3))))
    m = re.match(r'\d+(?:\.\d+)?$', expr_str)
    if m: return Num(float(m.group()))
    m = re.match(r'[a-z]+$', expr_str)
    if m: return Var(m.group())
    raise SyntaxError(f"Cannot parse: {expr_str!r}")

# Simulate a REPL session
env = Env()
session = [
    "x = 10",
    "y = 3",
    "x + y",
    "z = x * y",
    "z",
    "w = z + 1",
    "w",
]

print("Mini REPL session:")
for line in session:
    try:
        result = mini_eval(quick_parse(line), env)
        print(f">>> {line}")
        print(f"    {result}")
    except Exception as e:
        print(f">>> {line}")
        print(f"    Error: {e}")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

**Critical Thinking Questions — Model 4**

1. What does **REPL** stand for? Identify exactly which line(s) of the simulation above correspond to each of the four letters.

   [[___ your answer here ___]]

2. Why is a REPL especially useful when developing an interpreter? What kinds of bugs or design decisions become immediately visible in a REPL that are harder to see through batch testing?

   [[___ your answer here ___]]

3. What **state** persists between REPL lines in this simulation? Trace through the session and list the contents of `env.bindings` after each line executes.

   [[___ your answer here ___]]

4. How would you implement a special REPL command — say `env` — that prints all current variable bindings? Sketch the change to the REPL loop needed to support it.

   [[___ your answer here ___]]

---

#### Model 5: Error Recovery and Diagnostics

A correct interpreter that produces cryptic error messages is nearly as frustrating as one that crashes silently. Good diagnostics require planning from the very beginning: the tokenizer records line and column numbers, the parser attaches them to AST nodes, and the evaluator propagates them through its exceptions. This model shows how to build that infrastructure so that errors always point the user to exactly the right place in their source.

> **Watch out!** When a parse or evaluation error occurs, **raise a structured exception** — never just print a message to stdout and return `None`. A silent `None` propagates invisibly through the rest of the pipeline, causing a confusing error far from the actual mistake. Structured exceptions carry location information, can be caught and re-raised with additional context, and let the caller (such as a REPL's error handler) decide how to display them.

A correct interpreter is not enough — users need **useful error messages**. The gold standard is to report the line number, the relevant source text, and a pointer to the exact location of the problem, just as modern compilers like Rust or Clang do.

To achieve this, AST nodes carry **source location** metadata (line number, column, original source text). When the evaluator detects an error, it constructs an exception that includes this location and formats it into a human-readable message.

```python
from dataclasses import dataclass
from typing import Any, Optional

@dataclass
class SourceLocation:
    line: int
    col: int = 0
    source_line: str = ""

    def format(self) -> str:
        pointer = " " * self.col + "^"
        return f"  Line {self.line}: {self.source_line}\n  {pointer}"

@dataclass
class InterpreterError(Exception):
    message: str
    location: Optional[SourceLocation] = None

    def __str__(self):
        if self.location:
            return f"Error at line {self.location.line}: {self.message}\n{self.location.format()}"
        return f"Error: {self.message}"

class UndefinedVariable(InterpreterError): pass
class TypeError_(InterpreterError): pass
class DivisionByZero(InterpreterError): pass

@dataclass
class Num:
    value: float
    loc: SourceLocation = None

@dataclass
class Var:
    name: str
    loc: SourceLocation = None

@dataclass
class BinOp:
    op: str
    left: Any
    right: Any
    loc: SourceLocation = None

def safe_eval(node, env: dict) -> Any:
    if isinstance(node, Num): return node.value
    if isinstance(node, Var):
        if node.name not in env:
            raise UndefinedVariable(f"'{node.name}' is not defined", node.loc)
        return env[node.name]
    if isinstance(node, BinOp):
        l = safe_eval(node.left, env)
        r = safe_eval(node.right, env)
        if node.op == '/' and r == 0:
            raise DivisionByZero("division by zero", node.loc)
        if node.op in ('+', '-', '*', '/') and not (isinstance(l, (int,float)) and isinstance(r, (int,float))):
            raise TypeError_(f"Cannot apply '{node.op}' to {type(l).__name__} and {type(r).__name__}", node.loc)
        return {'+': l+r, '-': l-r, '*': l*r, '/': l/r}[node.op]
    raise InterpreterError(f"Unknown node: {type(node).__name__}")

# Test error messages
source_lines = ["x = 10", "y = x / 0", "z = undefined_var"]
loc1 = SourceLocation(2, 4, source_lines[1])
loc2 = SourceLocation(3, 4, source_lines[2])

env = {"x": 10.0}

tests = [
    (BinOp('/', Var('x'), Num(0), loc1), "x / 0"),
    (Var('undefined_var', loc2), "undefined_var"),
    (BinOp('+', Num(1.0), Num(2.0)), "1 + 2"),
]

for node, desc in tests:
    try:
        result = safe_eval(node, env)
        print(f"OK  {desc} = {result}")
    except InterpreterError as e:
        print(f"ERR {desc}:\n{e}")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

**Critical Thinking Questions — Model 5**

1. Why should error messages include line numbers and the original source text? Describe a real-world debugging scenario where the difference between a vague error and a located error saves significant time.

   [[___ your answer here ___]]

2. What information does `SourceLocation` track? Where in a real tokenizer or parser would you construct `SourceLocation` objects and attach them to AST nodes?

   [[___ your answer here ___]]

3. How does attaching `loc` fields to AST nodes help error reporting in the evaluator, even though the evaluator runs long after tokenizing and parsing are complete?

   [[___ your answer here ___]]

4. What is the difference in user experience between `NameError: 'x'` (Python's default) and a detailed location message with a source pointer? When might the simpler message actually be preferable?

   [[___ your answer here ___]]

---

#### Model 6: Adding Functions and Closures

Functions are where interpreters become genuinely interesting. The critical insight is that a function definition and a callable function value are two different things: one lives in the AST (a `Lambda` node), the other lives in the runtime (a `Closure` that pairs the function's code with the environment where it was defined). Getting this distinction right is what makes lexical scoping work correctly, including the powerful case of functions that return other functions.

Functions are the most powerful abstraction in programming languages. To implement them correctly, we must distinguish two things:

- A **Lambda** is a *syntactic* AST node: `lambda params: body`. It is part of the program text.
- A **Closure** is a *runtime value*: the function together with the **environment at the point of definition**. The captured environment is what makes closures powerful.

When a closure is called, we create a **new environment** that (a) extends the closure's captured environment and (b) binds the parameters to the call's arguments. This is **static (lexical) scoping**: the function sees the variables that were in scope where it was defined, not where it is called.

```python
from dataclasses import dataclass, field
from typing import Any, Optional

@dataclass
class Env:
    bindings: dict = field(default_factory=dict)
    parent: Optional['Env'] = None
    def define(self, n, v): self.bindings[n] = v
    def lookup(self, n):
        if n in self.bindings: return self.bindings[n]
        if self.parent: return self.parent.lookup(n)
        raise NameError(f"Undefined: '{n}'")

@dataclass
class Num: value: float
@dataclass
class Var: name: str
@dataclass
class BinOp: op: str; left: Any; right: Any
@dataclass
class Lambda: params: list; body: Any  # anonymous function
@dataclass
class Call: func: Any; args: list      # function call
@dataclass
class Closure:                          # runtime value: function + its env
    params: list
    body: Any
    env: Env

def interp(node, env: Env) -> Any:
    if isinstance(node, Num): return node.value
    if isinstance(node, Var): return env.lookup(node.name)
    if isinstance(node, BinOp):
        l, r = interp(node.left, env), interp(node.right, env)
        return {'+': l+r, '-': l-r, '*': l*r, '/': l/r}[node.op]
    if isinstance(node, Lambda):
        return Closure(node.params, node.body, env)  # captures current env
    if isinstance(node, Call):
        fn = interp(node.func, env)
        args = [interp(a, env) for a in node.args]
        if not isinstance(fn, Closure):
            raise TypeError(f"Not a function: {fn}")
        # Create new env extending the closure's captured env
        call_env = Env(parent=fn.env)
        for param, arg in zip(fn.params, args):
            call_env.define(param, arg)
        return interp(fn.body, call_env)
    raise ValueError(f"Unknown: {type(node).__name__}")

# Test: (lambda x, y: x + y)(3, 4)
add_fn = Lambda(["x", "y"], BinOp('+', Var("x"), Var("y")))
call = Call(add_fn, [Num(3), Num(4)])
env = Env()
print(f"(lambda x,y: x+y)(3,4) = {interp(call, env)}")

# Test closure: make_adder
# let make_adder = lambda n: lambda x: n + x
make_adder = Lambda(["n"], Lambda(["x"], BinOp('+', Var("n"), Var("x"))))
add5_expr = Call(make_adder, [Num(5)])
env.define("make_adder", interp(make_adder, env))
add5 = interp(add5_expr, env)
print(f"make_adder(5) is a Closure, params={add5.params}")
result = interp(Call(Lambda(["x"], BinOp('+', Var("n"), Var("x"))), [Num(3)]),
                Env(bindings={"n": 5}))
print(f"add5(3) = {result}")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

**Critical Thinking Questions — Model 6**

1. What is the difference between a `Lambda` (an AST node) and a `Closure` (a runtime value)? At what point in execution does a `Lambda` become a `Closure`?

   [[___ your answer here ___]]

2. Why does a `Closure` capture `env` at **definition time** rather than at **call time**? Give an example where using the call-time environment would produce a different — and wrong — result.

   [[___ your answer here ___]]

3. How does `Call` create a new environment that extends the closure's captured environment? Trace through the `make_adder(5)` call step-by-step, showing the chain of environments.

   [[___ your answer here ___]]

4. What is **static (lexical) scoping** and how does the `Closure`'s `env` field implement it? Contrast with **dynamic scoping** — what would change in the interpreter to implement dynamic scoping instead?

   [[___ your answer here ___]]

---

#### Multiple Choice

**Question 1**

In a recursive descent parser, how is operator precedence encoded?

[[MC]]
- [( )] By checking operator precedence tables at each parse step
- [(X)] By the nesting of parse functions — higher-precedence operators are parsed deeper in the call stack
- [( )] By sorting tokens by precedence before parsing begins
- [( )] By the order of tokens in the token stream

**Question 2**

What does a REPL do after it evaluates an expression?

[[MC]]
- [( )] It discards all variable bindings and starts fresh
- [( )] It saves the expression to a file for batch processing
- [(X)] It prints the result and loops back to read the next input, keeping the environment
- [( )] It compiles the expression to machine code before printing

**Question 3**

When a `Closure` is created by evaluating a `Lambda` node, what environment does it capture?

[[MC]]
- [( )] The global environment at program startup
- [(X)] The environment that is current at the moment the `Lambda` is evaluated
- [( )] The environment that will be current when the closure is eventually called
- [( )] A fresh empty environment with no bindings

**Question 4**

In the tree-walking evaluator for `If`, why is it correct to evaluate only one branch?

[[MC]]
- [( )] The other branch is evaluated later when the condition changes
- [( )] Both branches are evaluated but only one result is returned
- [(X)] The unevaluated branch may have side effects that should not occur when its condition is false
- [( )] The parser already removed the false branch from the AST

---

#### Exercises

**Exercise 1 — Let Expressions**

Add a `Let` expression to the interpreter. A `Let` node has three fields: `name` (a string), `value_expr` (an AST node), and `body_expr` (an AST node). Evaluating `Let(name, value_expr, body_expr)` should:

1. Evaluate `value_expr` in the current environment.
2. Create a **new** child environment that extends the current one.
3. Bind `name` to the result in the new environment.
4. Evaluate and return `body_expr` in the new environment.

The key difference from `Assign` is that `Let` creates a new scope — the binding is not visible outside `body_expr`.

```
Let("x", Num(5), BinOp('+', Var("x"), Num(3)))   # should return 8
```

Implement the `Let` dataclass and add a case to `evaluate` or `interp`. Test it with at least two examples: one where the `Let`-bound variable shadows an outer binding.

**Exercise 2 — Cond (if-elif-else Chain)**

Add a `Cond` node that represents a multi-way conditional:

```
Cond(clauses=[(cond1, result1), (cond2, result2), ...], else_result=...)
```

Evaluating `Cond` should scan through `clauses` in order. The first clause whose condition evaluates to a truthy value determines the result. If no clause matches, `else_result` is evaluated and returned.

Implement `Cond` and demonstrate it on an example that classifies a number as `"negative"`, `"zero"`, or `"positive"`.

**Exercise 3 — Recursive Functions with LetRec**

Ordinary `Lambda`/`Closure` cannot refer to themselves because the binding is not in scope when the function body is defined. Add a `LetRec(name, func_expr, body)` node that enables recursion:

1. Create a new child environment.
2. Evaluate `func_expr` to get a `Closure`.
3. Bind `name` to the closure **in the closure's own captured environment** (mutating it after creation).
4. Evaluate `body` in the new environment.

**Hint:** You may need to update `closure.env` after creating it. Test with a recursive factorial or Fibonacci function expressed as a `LetRec`.

**Exercise 4 — Pretty-Printer**

Implement a function `pretty(node) -> str` that converts an AST back into a human-readable infix expression string. Examples:

```
pretty(Num(3))                        # "3"
pretty(Var("x"))                      # "x"
pretty(BinOp('+', Num(3), Num(4)))    # "(3 + 4)"
pretty(BinOp('*', Num(2),
             BinOp('+', Num(1), Num(5))))  # "(2 * (1 + 5))"
pretty(Lambda(["x"], Var("x")))       # "(lambda x: x)"
pretty(Call(Var("f"), [Num(1), Num(2)]))   # "f(1, 2)"
```

The pretty-printer is useful for debugging (round-trip: parse then pretty-print) and for generating readable output from transformed ASTs.

---

#### Reflection

You have now built a complete interpreter pipeline from scratch: a tokenizer that turns source text into tokens, a recursive descent parser that builds an AST, and a tree-walking evaluator that computes results. You also saw how to report errors with source locations and how to implement closures.

Respond to the following prompt in 3–4 sentences:

*Which stage of the pipeline was the most surprising to you, and why? What would you add — beyond lexical scoping, arithmetic, and conditionals — to turn this toy interpreter into a practical programming language?*

[[___ your reflection here ___]]

---

#### Further Reading

- **Compilers: Principles, Techniques, and Tools** (Aho, Lam, Sethi, Ullman) — Chapter 4: Syntax Analysis; Chapter 5: Syntax-Directed Translation
- **Programming Languages: Application and Interpretation** (Krishnamurthi) — Chapter 15: Interpreting Variables; Chapter 16: Functions; Chapter 17: Closures and Higher-Order Functions
- **Crafting Interpreters** (Nystrom) — Free online at https://craftinginterpreters.com — a complete, annotated implementation of a full language in Java and C
- **Let's Build A Simple Interpreter** (Ruslan Spivak) — Blog series building a Pascal interpreter in Python, excellent complement to this activity
- **Structure and Interpretation of Computer Programs** (Abelson & Sussman) — Chapter 4: Metalinguistic Abstraction — the classic treatment of building evaluators in Scheme

## Going Deeper: Operational Semantics: Specifying Languages with Inference Rules

When you write an interpreter, you are making decisions about what programs *mean* — but those decisions live buried in Python code, not in a form anyone else can easily check or reason about. Operational semantics is like a referee's rulebook for a programming language: it specifies exactly what each syntactic construct *does*, step by step, so there is no ambiguity about the language's behavior independent of any particular implementation. By the end of this activity you will be able to read and write these rules and see exactly how they map onto the evaluator you have already built.

#### Learning Goals

By the end of this activity, you will be able to:

- Define the components of an inference rule (premises, conclusion, axiom) and interpret inference rule notation correctly
- Construct big-step derivation trees for arithmetic and conditional expressions using big-step (natural) semantics rules
- Trace small-step reduction sequences for expressions, identifying each intermediate configuration
- Compare big-step and small-step operational semantics and explain which style aligns more closely with a tree-walking interpreter
- Analyze the connection between operational semantics rules and the corresponding cases in an interpreter's `eval` function

Your interpreter is an implementation of a language — but implementations can have bugs. A **formal semantics** is a mathematical specification of the language that is separate from any implementation: you check your interpreter against the semantics, not the other way around. Today we study **operational semantics**, the dominant style in programming language theory, which defines meaning by specifying computation as a set of formal **inference rules** over program configurations. The arc: **configurations → big-step semantics → small-step semantics → connecting to your evaluator → where semantics and type systems meet**.

> **Before You Begin:** This activity assumes you can:
> - Read and trace through a recursive tree-walking interpreter (your Mini evaluator from earlier assignments)
> - Understand environments as mappings from variable names to values, and explain what variable lookup and extension mean
> - Recognize the structure of a lambda expression and explain how closures capture their defining environment
> - Write simple mathematical proofs by cases (e.g., case analysis on which constructor an expression uses)
> If any of these feel shaky, review them first.

---

#### Directions and Group Roles

Work in your POGIL team with rotated roles (**Manager**, **Recorder**, **Presenter**, **Reflector**). Today is a pencil-and-paper day: every derivation is written as an inference tree, checked by another teammate. The Recorder photographs derivation trees for the discussion board. After class, respond to the reflective prompt individually in your notebook.

---

### Part I: Inference Rules

#### 1. The Notation

An **inference rule** has the form:

$$
\frac{\text{premise}_1 \quad \text{premise}_2 \quad \cdots}{\text{conclusion}} \quad [\text{Rule Name}]
$$

Read it: "if all premises hold, then the conclusion holds." An **axiom** is a rule with no premises (an always-true conclusion, written with nothing above the line). A **derivation** (or proof tree) builds up a conclusion from axioms using the rules, like a mathematical proof.

**Notation for expression evaluation:** $\langle e, \sigma \rangle \Downarrow v$ means "expression $e$ in environment $\sigma$ evaluates to value $v$." (Some texts write $\sigma \vdash e \Rightarrow v$.) The environment $\sigma$ is a partial function from variable names to values.

**Notation quick-reference — formal symbol to plain English:**

| Notation | Meaning |
|----------|---------|
| `Γ ⊢ e : τ` | "In type environment Γ, expression e has type τ" |
| `⟨e, σ⟩ ⇓ v` | "Expression e, evaluated in environment σ, produces final value v" (big-step) |
| `⟨e, σ⟩ → ⟨e', σ'⟩` | "Expression e reduces to e' in one step, updating the environment" (small-step) |
| `→*` | Zero or more small-step reduction steps |
| `[x ↦ v]e` | "Substitute v for every free occurrence of x in expression e" |
| `σ[x ↦ v]` | "The environment σ extended so that x now maps to v" |
| `λx. e` | "A function with parameter x and body e" |
| Horizontal bar | "If everything above the bar holds, then the thing below the bar holds" |

> **Watch out!** The notation $\Gamma \vdash e : \tau$ (type judgment, Part IV) looks very similar to $\langle e, \sigma \rangle \Downarrow v$ (value judgment, Parts II–III), but they are different kinds of relations. $\Gamma$ maps names to *types*; $\sigma$ maps names to *values*. One is used by the type checker; the other by the evaluator. Do not mix them up when building derivation trees.

---

### Part II: Big-Step (Natural) Semantics

**Intuition:** In this section we write down the exact rules your tree-walking interpreter already follows — just in mathematical notation instead of Python. Each rule corresponds to one `if`-branch in your `eval` function: the premises are the recursive calls, and the conclusion is what the whole expression evaluates to. As you read each rule, mentally map it onto the matching Python code you wrote.

#### 2. Big-Step Rules for Mini

"Big-step" semantics (also called **natural semantics** or **evaluation semantics**) defines evaluation in one jump from expression to final value — matching the recursive structure of your tree-walking interpreter.

**Literals (axioms — no premises):**

$$
\frac{}{\langle n, \sigma \rangle \Downarrow n} \quad [\text{Num}]
\qquad
\frac{}{\langle \textbf{true}, \sigma \rangle \Downarrow \textbf{true}} \quad [\text{Bool-T}]
\qquad
\frac{}{\langle \textbf{false}, \sigma \rangle \Downarrow \textbf{false}} \quad [\text{Bool-F}]
$$

**Variable lookup:**

$$
\frac{\sigma(x) = v}{\langle x, \sigma \rangle \Downarrow v} \quad [\text{Var}]
$$

**Arithmetic:**

$$
\frac{\langle e_1, \sigma \rangle \Downarrow n_1 \quad \langle e_2, \sigma \rangle \Downarrow n_2 \quad n = n_1 + n_2}{\langle e_1 + e_2, \sigma \rangle \Downarrow n} \quad [\text{Add}]
$$

(Rules for $-, *, /$ are analogous.)

**Conditionals:**

$$
\frac{\langle e_1, \sigma \rangle \Downarrow \textbf{true} \quad \langle e_2, \sigma \rangle \Downarrow v}{\langle \textbf{if}\; e_1\; \textbf{then}\; e_2\; \textbf{else}\; e_3, \sigma \rangle \Downarrow v} \quad [\text{If-T}]
$$

$$
\frac{\langle e_1, \sigma \rangle \Downarrow \textbf{false} \quad \langle e_3, \sigma \rangle \Downarrow v}{\langle \textbf{if}\; e_1\; \textbf{then}\; e_2\; \textbf{else}\; e_3, \sigma \rangle \Downarrow v} \quad [\text{If-F}]
$$

**Let binding:**

$$
\frac{\langle e_1, \sigma \rangle \Downarrow v_1 \quad \langle e_2, \sigma[x \mapsto v_1] \rangle \Downarrow v_2}{\langle \textbf{let}\; x = e_1\; \textbf{in}\; e_2, \sigma \rangle \Downarrow v_2} \quad [\text{Let}]
$$

The notation $\sigma[x \mapsto v_1]$ means "the environment $\sigma$ extended with $x$ mapping to $v_1$."

**Function abstraction and application:**

$$
\frac{}{\langle \lambda x.\, e, \sigma \rangle \Downarrow \langle \lambda x.\, e, \sigma \rangle} \quad [\text{Lam}]
\qquad
\frac{\langle e_1, \sigma \rangle \Downarrow \langle \lambda x.\, e, \sigma' \rangle \quad \langle e_2, \sigma \rangle \Downarrow v_2 \quad \langle e, \sigma'[x \mapsto v_2] \rangle \Downarrow v}{\langle e_1\; e_2, \sigma \rangle \Downarrow v} \quad [\text{App}]
$$

Notice: $[\text{Lam}]$ says a lambda evaluates to a **closure** — the function expression paired with its defining environment $\sigma'$. $[\text{App}]$ uses $\sigma'$ (not $\sigma$) to extend — this is lexical scoping in the rule.

---

#### Code Cell: Deriving a Rule Machine in Python

```python
try:
    # A "rule engine" that mirrors big-step semantics as Python recursive eval.
    # Each function corresponds exactly to one or more semantic rules.

    def eval_bs(expr, env):
        """Big-step evaluation: returns a value."""

        tag = expr[0]

        # [Num] — literal
        if tag == 'num':
            return expr[1]

        # [Bool-T], [Bool-F]
        if tag == 'bool':
            return expr[1]

        # [Var]
        if tag == 'var':
            name = expr[1]
            if name not in env:
                raise NameError(f"unbound variable '{name}'")
            return env[name]

        # [Add] (and analogous rules for -, *, /)
        if tag == 'binop':
            _, op, e1, e2 = expr
            v1 = eval_bs(e1, env)
            v2 = eval_bs(e2, env)
            return {'+': v1 + v2, '-': v1 - v2,
                    '*': v1 * v2, '/': v1 / v2}[op]

        # [If-T], [If-F]
        if tag == 'if':
            _, cond, then_e, else_e = expr
            cv = eval_bs(cond, env)
            return eval_bs(then_e, env) if cv else eval_bs(else_e, env)

        # [Let]
        if tag == 'let':
            _, name, e1, e2 = expr
            v1 = eval_bs(e1, env)
            return eval_bs(e2, {**env, name: v1})

        # [Lam]: evaluates to a closure (tuple of lambda node + captured env)
        if tag == 'lam':
            return ('closure', expr, env)

        # [App]: apply a closure
        if tag == 'app':
            _, e1, e2 = expr
            fn = eval_bs(e1, env)
            arg = eval_bs(e2, env)
            if fn[0] != 'closure':
                raise TypeError(f"not a function: {fn}")
            _, lam, closure_env = fn
            _, param, body = lam    # lam = ('lam', param, body)
            return eval_bs(body, {**closure_env, param: arg})

        raise ValueError(f"unknown expression: {expr!r}")

    # Test: (lambda x. x + 1)(5) = 6
    prog = ('app',
        ('lam', 'x', ('binop', '+', ('var', 'x'), ('num', 1))),
        ('num', 5))
    print("(λx. x+1)(5) =", eval_bs(prog, {}))

    # Test: let x = 3 in let y = 4 in x * y = 12
    prog2 = ('let', 'x', ('num', 3),
             ('let', 'y', ('num', 4),
              ('binop', '*', ('var', 'x'), ('var', 'y'))))
    print("let x=3 in let y=4 in x*y =", eval_bs(prog2, {}))

    # Test: if true then 1 else 2 = 1
    prog3 = ('if', ('bool', True), ('num', 1), ('num', 2))
    print("if true then 1 else 2 =", eval_bs(prog3, {}))

except Exception as e:
    print(f"[opsem:bigstep] {e}")
    import traceback; traceback.print_exc()
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

---

**Intuition:** A derivation tree is not something you *invent* — it is something you *discover* by asking, for each sub-expression, which rule applies and what its premises require. Start at the root (the whole expression), work downward through sub-expressions, and bottom out at axioms (leaves with no premises). The tree proves that the expression evaluates to the stated value.

> **Watch out!** Inference rules are not proofs you construct freely — they are rules you *apply*. A rule fires only when its premises are all derivable. You cannot choose to skip a premise or apply a rule "partially." If you cannot derive every premise of a rule, that rule does not apply for that expression. This is different from writing a proof by assumption — here, every step must be grounded in an axiom or a previously derived judgment.

#### Model 1: Building Derivation Trees

##### Worked Example: Derivation Tree for `(λx. x) 5`

This traces the complete big-step derivation for applying the identity function to 5, in an empty environment `{}`.

**Goal:** show `⟨(λx. x) 5, {}⟩ ⇓ 5`

We need to apply rule `[App]`, whose three premises are:
1. Evaluate the function expression `λx. x` in `{}`
2. Evaluate the argument `5` in `{}`
3. Evaluate the body in the extended closure environment

**Premise 1 — evaluate the function:** By `[Lam]` (an axiom):

```
─────────────────────────────────────── [Lam]
⟨λx. x, {}⟩ ⇓ ⟨λx. x, {}⟩   (a closure)
```

**Premise 2 — evaluate the argument:** By `[Num]` (an axiom):

```
─────────────────── [Num]
⟨5, {}⟩ ⇓ 5
```

**Premise 3 — evaluate the body in the extended environment:** The closure environment is `{}`, extended with `x ↦ 5`, giving `{x ↦ 5}`. The body is `x`. By `[Var]`:

```
{x ↦ 5}(x) = 5
─────────────────────────── [Var]
⟨x, {x ↦ 5}⟩ ⇓ 5
```

**Putting it all together with `[App]`:**

```
──────────────────────────── [Lam]    ─────────────── [Num]    ─────────────────────────── [Var]
⟨λx. x, {}⟩ ⇓ ⟨λx. x, {}⟩          ⟨5, {}⟩ ⇓ 5             ⟨x, {x ↦ 5}⟩ ⇓ 5
─────────────────────────────────────────────────────────────────────────────────────────── [App]
⟨(λx. x) 5, {}⟩ ⇓ 5
```

The three leaves (axioms) are at the top; the root conclusion is at the bottom. Every step cites its rule name in brackets.

> **Watch out!** Notice that `[App]` uses the closure's captured environment `{}` (called `σ'` in the rule) to extend for the function body — **not** the call-site environment. For this simple example they happen to be the same (`{}`), but if the function had been defined inside a `let` binding that added variables, `σ'` would include those variables and the call-site environment would not. This asymmetry is exactly what enforces lexical (static) scoping.

##### Critical Thinking Questions

1. Write the complete big-step derivation tree (using the rules above) for `(2 + 3) * 4` in an empty environment. Label every inference rule used. (The tree should have 3 leaves: two $[\text{Num}]$ axioms for 2 and 3 feeding into one $[\text{Add}]$, which feeds into the $[\text{Mul}]$ with the $[\text{Num}]$ axiom for 4.)

2. Derive `let x = 5 in x + 1` step by step. Show: (a) how `5` is evaluated by $[\text{Num}]$; (b) how `x + 1` is evaluated in the extended environment $\{x \mapsto 5\}$; (c) the final $[\text{Let}]$ rule that combines them.

3. The $[\text{App}]$ rule evaluates the argument before substituting into the function body. What evaluation strategy does this implement — call-by-value, call-by-name, or call-by-need? How would you change the rule to implement call-by-name?

4. The $[\text{Lam}]$ rule says `λx. e` evaluates to a *closure* `(λx. e, σ)` in the *current* environment. The $[\text{App}]$ rule then uses `σ'` (the closure's environment) for the function body, not the call site's environment `σ`. Write a 2-sentence explanation of why this implements **lexical scoping** rather than **dynamic scoping**.

---

### Part III: Small-Step (Structural) Semantics

**Intuition:** Rather than jumping straight from expression to final value, small-step semantics describes one tiny reduction at a time — like watching a computation frame-by-frame in a debugger. Each step rewrites the expression slightly closer to a value. The rules specify not just *what* to reduce, but also *which* sub-expression to reduce first, which is what gives the language a well-defined evaluation order.

#### 3. One Step at a Time

**Small-step semantics** (also called **structural operational semantics**, SOS, or reduction semantics) describes computation as a sequence of single-step reductions. Instead of $\langle e, \sigma \rangle \Downarrow v$, we write $\langle e, \sigma \rangle \to \langle e', \sigma' \rangle$ (one reduction step) and $\to^*$ for zero or more steps. A term is in **normal form** when no rule applies.

Small-step semantics is more suitable for describing:
- Concurrent programs (interleaving of steps)
- Infinite loops (distinguished from "no value" — a loop takes infinitely many steps)
- Side effects (each step can modify the environment)

**Small-step rules for arithmetic:**

$$
\frac{}{\langle n_1 + n_2, \sigma \rangle \to \langle n_1 + n_2, \sigma \rangle \to \langle n, \sigma \rangle} \quad [\text{Add-Reduce}]
$$

where both $n_1$ and $n_2$ are already numeric values, and $n = n_1 + n_2$.

For non-values (when we must first reduce a sub-expression):

$$
\frac{\langle e_1, \sigma \rangle \to \langle e_1', \sigma' \rangle}{\langle e_1 + e_2, \sigma \rangle \to \langle e_1' + e_2, \sigma' \rangle} \quad [\text{Add-L}]
$$

$$
\frac{\langle e_2, \sigma \rangle \to \langle e_2', \sigma' \rangle}{\langle n_1 + e_2, \sigma \rangle \to \langle n_1 + e_2', \sigma' \rangle} \quad [\text{Add-R}]
$$

(where $n_1$ is already a value — $[\text{Add-R}]$ applies only once the left is a value.)

**Sequencing:** in small-step, `let x = e₁ in e₂` first reduces `e₁`:

$$
\frac{\langle e_1, \sigma \rangle \to \langle e_1', \sigma' \rangle}{\langle \textbf{let}\; x = e_1\; \textbf{in}\; e_2, \sigma \rangle \to \langle \textbf{let}\; x = e_1'\; \textbf{in}\; e_2, \sigma' \rangle} \quad [\text{Let-Step}]
$$

$$
\frac{}{\langle \textbf{let}\; x = v\; \textbf{in}\; e_2, \sigma \rangle \to \langle e_2, \sigma[x \mapsto v] \rangle} \quad [\text{Let-Val}]
$$

---

#### Code Cell: Small-Step Reducer

```python
try:
    def is_value(expr):
        return expr[0] in ('num', 'bool', 'closure')

    def step(expr, env):
        """One small-step reduction. Returns (new_expr, new_env) or None if normal form."""
        tag = expr[0]

        if is_value(expr):
            return None   # already a value; no step possible

        # Variable: look up (one-step)
        if tag == 'var':
            name = expr[1]
            if name not in env:
                raise NameError(f"unbound: {name!r}")
            return (env[name], env)   # Var-Lookup

        # Add-Reduce: both sides are values
        if tag == 'binop':
            _, op, e1, e2 = expr
            if is_value(e1) and is_value(e2):
                n1, n2 = e1[1], e2[1]
                result = {'+': n1+n2, '-': n1-n2,
                          '*': n1*n2, '/': n1/n2}[op]
                return (('num', result), env)   # BinOp-Reduce
            # Add-L: reduce left first
            if not is_value(e1):
                e1p, envp = step(e1, env)
                return (('binop', op, e1p, e2), envp)
            # Add-R: reduce right once left is a value
            e2p, envp = step(e2, env)
            return (('binop', op, e1, e2p), envp)

        # If-T / If-F: reduce condition first, then select branch
        if tag == 'if':
            _, cond, then_e, else_e = expr
            if not is_value(cond):
                cp, envp = step(cond, env)
                return (('if', cp, then_e, else_e), envp)
            return ((then_e if cond[1] else else_e), env)

        # Let-Step / Let-Val
        if tag == 'let':
            _, name, e1, body = expr
            if not is_value(e1):
                e1p, envp = step(e1, env)
                return (('let', name, e1p, body), envp)
            return (body, {**env, name: e1[1]})

        # Lam: a value (no step needed)
        if tag == 'lam':
            return (('closure', expr, env), env)

        # App-Step
        if tag == 'app':
            _, e1, e2 = expr
            if not is_value(e1):
                e1p, envp = step(e1, env)
                return (('app', e1p, e2), envp)
            if not is_value(e2):
                e2p, envp = step(e2, env)
                return (('app', e1, e2p), envp)
            # App-Beta: both sides are values
            fn = e1
            if fn[0] != 'closure':
                raise TypeError(f"not a function: {fn}")
            _, lam, closure_env = fn
            _, param, body = lam
            return (body, {**closure_env, param: e2[1]})

        raise ValueError(f"unknown: {expr!r}")

    def run_steps(expr, env, max_steps=30):
        """Run small-step until normal form; print each step."""
        print(f"  Initial: {expr}")
        for i in range(max_steps):
            result = step(expr, env)
            if result is None:
                print(f"  → (normal form)")
                return expr
            expr, env = result
            print(f"  → {expr}")
        print("  (max steps reached)")
        return expr

    # (1 + 2) * 3  →  3 * 3  →  9
    prog = ('binop', '*',
            ('binop', '+', ('num', 1), ('num', 2)),
            ('num', 3))
    print("Small-step trace for (1+2)*3:")
    run_steps(prog, {})
    print()

    # let x = 4 in x + 1
    prog2 = ('let', 'x', ('num', 4),
             ('binop', '+', ('var', 'x'), ('num', 1)))
    print("Small-step trace for let x=4 in x+1:")
    run_steps(prog2, {})

except Exception as e:
    print(f"[opsem:smallstep] {e}")
    import traceback; traceback.print_exc()
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

---

**Intuition:** In small-step derivations you are writing a *sequence* of configurations, not a tree. Each line shows one application of one rule, turning the current configuration into the next. The sequence ends when the expression is a value (normal form) or gets stuck. Compare this to the derivation tree from Model 1 — the tree captures the entire computation at once, while the sequence shows one reduction at a time.

> **Watch out!** Big-step and small-step semantics for the *same* language should agree on the *final value* for any terminating program, but they are not the same relation. Big-step says nothing about intermediate states. Small-step says nothing about the final value in one step — you must follow the whole sequence. Students often confuse "the two styles agree" with "they are interchangeable" — they are not: they serve different purposes and are used to prove different properties.

#### Model 2: Small-Step Derivations

##### Critical Thinking Questions

5. Write the full small-step reduction sequence for `(if true then 1 else 2) + 3`:
   - Step 1: reduce `if true then 1 else 2` to `1` (which rule?)
   - Step 2: reduce `1 + 3` to `4` (which rule?)
   Connect this to the evaluation order in your Python evaluator: does it match?

6. Big-step semantics and small-step semantics should *agree* on the final value for any terminating program. Why are there *two* semantics styles if they agree? Name one thing small-step can express that big-step cannot.

7. The $[\text{Add-L}]$ rule says: reduce the **left** sub-expression first. This is a **deterministic** choice — for each expression, at most one rule applies. What would happen if you had two rules, $[\text{Add-L}]$ and $[\text{Add-R}]$, that could both apply simultaneously? Would the program still be deterministic? How does the ordering in $[\text{Add-R}]$ (which requires $e_1$ to already be a value) prevent this?

8. An **infinite loop** in big-step has no derivation at all — there is simply no proof tree. In small-step, an infinite loop produces an infinite reduction sequence: `e → e' → e'' → ...` that never reaches a normal form. Which style distinguishes "no value" (infinite loop) from "error" (stuck state, like dividing by zero) more clearly?

---

### Part IV: Type Rules and Type Safety

**Intuition:** Type rules look exactly like evaluation rules — same inference-rule notation, same tree-building process — but instead of asking "what value does this expression produce?" they ask "what *type* does this expression have?" The payoff is the type safety theorem: if you can build a type derivation for a program, the program is guaranteed never to get stuck at runtime with a type mismatch.

#### 4. Types as Proof Obligations

A **type system** is a set of inference rules over types instead of values. The judgment $\Gamma \vdash e : \tau$ means "in type environment $\Gamma$, expression $e$ has type $\tau$."

$$
\frac{}{\Gamma \vdash n : \text{Int}} \quad [\text{T-Num}]
\qquad
\frac{\Gamma(x) = \tau}{\Gamma \vdash x : \tau} \quad [\text{T-Var}]
$$

$$
\frac{\Gamma \vdash e_1 : \text{Int} \quad \Gamma \vdash e_2 : \text{Int}}{\Gamma \vdash e_1 + e_2 : \text{Int}} \quad [\text{T-Add}]
$$

$$
\frac{\Gamma \vdash e_1 : \text{Bool} \quad \Gamma \vdash e_2 : \tau \quad \Gamma \vdash e_3 : \tau}{\Gamma \vdash \textbf{if}\; e_1\; \textbf{then}\; e_2\; \textbf{else}\; e_3 : \tau} \quad [\text{T-If}]
$$

$$
\frac{\Gamma, x : \tau_1 \vdash e : \tau_2}{\Gamma \vdash \lambda x.\, e : \tau_1 \to \tau_2} \quad [\text{T-Lam}]
\qquad
\frac{\Gamma \vdash e_1 : \tau_1 \to \tau_2 \quad \Gamma \vdash e_2 : \tau_1}{\Gamma \vdash e_1\; e_2 : \tau_2} \quad [\text{T-App}]
$$

**Type safety** (the Milner-Wright theorem): if $\Gamma \vdash e : \tau$ (the expression is well-typed), then either $e$ evaluates to a value of type $\tau$, or it diverges. A well-typed program never *gets stuck* (reaches a state where no rule applies but the expression is not a value).

---

#### Code Cell: Type-Checking as Inference Rules

```python
try:
    # A simple type checker implementing the inference rules above

    def typecheck(expr, type_env):
        """Return the type of expr, or raise TypeError."""
        tag = expr[0]

        # [T-Num]
        if tag == 'num':   return 'Int'
        if tag == 'bool':  return 'Bool'
        if tag == 'str':   return 'Str'

        # [T-Var]
        if tag == 'var':
            name = expr[1]
            if name not in type_env:
                raise TypeError(f"unbound variable '{name}'")
            return type_env[name]

        # [T-Add] and siblings
        if tag == 'binop':
            _, op, e1, e2 = expr
            t1 = typecheck(e1, type_env)
            t2 = typecheck(e2, type_env)
            if op in ('+', '-', '*', '/'):
                if t1 != 'Int':
                    raise TypeError(f"'{op}' requires Int, got {t1}")
                if t2 != 'Int':
                    raise TypeError(f"'{op}' requires Int, got {t2}")
                return 'Int'
            if op in ('<', '>', '==', '!=', '<=', '>='):
                if t1 != t2:
                    raise TypeError(f"comparison: {t1} vs {t2}")
                return 'Bool'

        # [T-If]
        if tag == 'if':
            _, cond, then_e, else_e = expr
            tc = typecheck(cond, type_env)
            if tc != 'Bool':
                raise TypeError(f"condition must be Bool, got {tc}")
            tt = typecheck(then_e, type_env)
            te = typecheck(else_e, type_env)
            if tt != te:
                raise TypeError(f"branches must match: {tt} vs {te}")
            return tt

        # [T-Let]
        if tag == 'let':
            _, name, e1, body = expr
            t1 = typecheck(e1, type_env)
            return typecheck(body, {**type_env, name: t1})

        # [T-Lam]: require a type annotation on the parameter
        if tag == 'lam':
            _, param, param_type, body = expr   # annotated lambda
            t2 = typecheck(body, {**type_env, param: param_type})
            return (param_type, '->', t2)   # function type as tuple

        # [T-App]
        if tag == 'app':
            _, e1, e2 = expr
            t1 = typecheck(e1, type_env)
            t2 = typecheck(e2, type_env)
            if not (isinstance(t1, tuple) and t1[1] == '->'):
                raise TypeError(f"not a function type: {t1}")
            param_t, _, ret_t = t1
            if param_t != t2:
                raise TypeError(f"argument: expected {param_t}, got {t2}")
            return ret_t

        raise ValueError(f"unknown: {expr!r}")

    # Well-typed: (λx:Int. x + 1)(5) : Int
    prog = ('app',
            ('lam', 'x', 'Int', ('binop', '+', ('var', 'x'), ('num', 1))),
            ('num', 5))
    print("type of (λx:Int. x+1)(5):", typecheck(prog, {}))

    # Well-typed: if true then 1 else 2 : Int
    prog2 = ('if', ('bool', True), ('num', 1), ('num', 2))
    print("type of if true then 1 else 2:", typecheck(prog2, {}))

    # Ill-typed: if 1 then 2 else 3 (Int as condition)
    try:
        typecheck(('if', ('num', 1), ('num', 2), ('num', 3)), {})
    except TypeError as e:
        print("type error (expected):", e)

    # Ill-typed: 1 + true
    try:
        typecheck(('binop', '+', ('num', 1), ('bool', True)), {})
    except TypeError as e:
        print("type error (expected):", e)

except Exception as e:
    print(f"[opsem:types] {e}")
    import traceback; traceback.print_exc()
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

---

**Intuition:** Type safety is often stated as two lemmas — *progress* (a well-typed expression is either a value or can take a step) and *preservation* (if a well-typed expression takes a step, the result is still well-typed at the same type). Together they guarantee that well-typed programs never get stuck. As you work through the questions below, try to state each argument as one of these two lemmas.

#### Model 3: Types and Safety

[[MC]]
The type safety theorem says a well-typed program either evaluates to a value of the right type or diverges. It does NOT guarantee that the program:
- ( ) Produces a value of the declared type
- ( ) Terminates
- (x) Both: terminates AND produces the right type (it may still loop)
- ( ) Does not throw exceptions

##### Critical Thinking Questions

9. The $[\text{T-If}]$ rule requires both branches to have the *same* type $\tau$. Why? Give an example of a program that would be accepted if this restriction were dropped, and show what would go wrong at runtime.

10. The $[\text{T-App}]$ rule unifies the function's parameter type with the argument's type. This is essentially one step of Hindley-Milner unification. Connect this to the type inference assignment: Algorithm W automates the process of figuring out what $\tau_1$ and $\tau_2$ must be from the code, rather than requiring annotations.

11. In the small-step semantics, a **stuck state** is a configuration where no rule applies and the expression is not a value (e.g., `true + 1`). Type safety says well-typed programs cannot get stuck. Prove this informally for the $[\text{T-Add}]$ case: if `e₁ + e₂` has type Int and both `e₁` and `e₂` are values, what type must each value have, and why can the Add-Reduce rule always apply?

---

### Part V: Exercises

1. **Derive the [App] rule.** Write the complete big-step derivation tree for the application `(λx. x * x)(3)` in an empty environment. The tree should have leaves for: the lambda (closure), the argument 3, the multiplication, and the sub-expressions.

2. **Add while-loops to big-step semantics.** The rule for `while cond do body` in big-step can be written by "unrolling" one iteration:
   $$
   \frac{\langle cond, \sigma \rangle \Downarrow \textbf{false}}{\langle \textbf{while}\; cond\; \textbf{do}\; body, \sigma \rangle \Downarrow \sigma} \quad [\text{While-F}]
   $$
   Write the $[\text{While-T}]$ rule for when the condition is true (hint: evaluate body, update environment, recurse on the while loop). What is the return value of a while loop in your Mini language?

3. **Short-circuit in small-step.** Your language's `&&` short-circuits: if the left is false, the right is not evaluated. Write the small-step rules for `&&`:
   - One rule when the left is `false` (immediately reduce to `false`)
   - One rule when the left is `true` (reduce to the right sub-expression)
   - One rule for reducing the left when it is not yet a value
   Verify: do these rules capture short-circuit semantics correctly?

4. **Big-step vs. small-step for recursion.** Consider a recursive function `let f = λn. if n==0 then 1 else n * f(n-1) in f(3)`. In big-step semantics, how does the rule for function application handle the recursive reference to `f` in its own body? (What must the closure capture?) Write the $[\text{Let}]$ rule for a *letrec* (recursive let) that solves this.

---

#### Reflection Prompt

In your notebook: your Python interpreter implements big-step semantics by being a big-step evaluator — each Python function call corresponds to one semantic rule. Your type checker implements the type rules. Does writing the formal rules *before* the code make implementation easier? What bugs would you have avoided in your Mini assignments if you had formal rules to check against first? And: the Curry-Howard correspondence says type rules and proof rules are the same thing — does the $[\text{T-If}]$ rule above look like a logical inference rule to you now?

---

#### Further Reading

- Winskel, Glynn. *The Formal Semantics of Programming Languages* (MIT Press, 1993). Chapters 2–4 are the standard treatment of big-step and small-step semantics; this course's notation follows Winskel.
- Wright, Andrew K. and Matthias Felleisen. "A Syntactic Approach to Type Soundness" (1994). The paper that introduced the "progress + preservation" proof method for type safety.
- Pierce, Benjamin C. *Types and Programming Languages* (MIT Press, 2002), Chapters 3–9. Covers both styles with full proofs.
- Plotkin, Gordon D. "A Structural Approach to Operational Semantics" (1981, Aarhus Tech Report). The foundational paper for small-step semantics.
- Online tool: PLT Redex — run your semantics as executable specifications in DrRacket: https://redex.racket-lang.org/
