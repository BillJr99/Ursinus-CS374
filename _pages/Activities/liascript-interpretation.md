<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374/gh-pages/_pages/Activities/liascript-interpretation.md or locally via https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374/gh-pages/_pages/Activities/liascript-interpretation.md

import: https://raw.githubusercontent.com/liascript/CodeRunner/master/README.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

# Tree-Walking Interpretation

You have a lexer (*Tokens and Scanning*) that turns characters into tokens and a parser (*Recursive Descent Parsing*) that turns tokens into trees. Now comes the payoff: the **evaluator** turns those trees into *values*; it is the part that actually *runs* your program. Think of it as a universal translator: given any sentence in the source language (an AST node), it produces the meaning (a Python value) directly, by asking the same question recursively of every sub-sentence. After today, no magic remains between source code and output.

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

## 0. Interpreters and Compilers: When Does Translation Happen?

Before writing the evaluator, place it on the map. There are two fundamentally different ways to make source text run, and the difference is *when* the translation work happens:

| | **Interpreter** (what you build in this course) | **Compiler** |
|---|---|---|
| What it does with the AST | Walks it and computes values *now* | Translates it into another language (machine code, bytecode) to run *later* |
| When errors like `1 + "hello"` surface | While the program runs, at that expression | Potentially before the program ever runs |
| Cost model | Pays a small translation tax on every execution of every node | Pays translation once, then runs at full speed |
| Change the source? | Just run again | Recompile first |

The pipeline you have built so far (lexer -> parser -> AST) is **identical for both**. They diverge only at this step: a compiler of your class language would consume the very same AST your parser produces and emit instructions instead of values. (That path is walked in the *Table-Driven and LR Parsing* session's compile-link-load model and the *Build a Bytecode VM* tutorial.) Everything you learn today about evaluation order and environments applies to both worlds.

Quick check: a tree-walking interpreter and a compiler for the same language both receive the AST for `x * (y + 1)`. What does each produce from it?

- [( )] Both produce the numeric answer
- [(X)] The interpreter produces the numeric answer; the compiler produces code that will compute it when run
- [( )] The interpreter produces machine code; the compiler produces the answer
- [( )] Both produce new source text in a different language

The central idea of Part I is deceptively simple: **the value of any expression is computed entirely from the values of its sub-expressions.** A number node is its own value; an addition node evaluates both children and adds the results. This recursive definition is both the formal semantics of the language and the literal shape of the code you will write.

## 1. The Recursive Definition of Meaning

**The value of a node is defined in terms of the values of its children.** This is denotational thinking made executable:

$$
\mathcal{E}[\![\text{Num}(n)]\!] = n \qquad
\mathcal{E}[\![\text{BinOp}(+, l, r)]\!] = \mathcal{E}[\![l]\!] + \mathcal{E}[\![r]\!]
$$

and so on for every node class: evaluate children first (post-order, exactly as Model 2 of the AST module predicted), then combine with the node's operation. Where the pretty-printer printed, the evaluator returns; the recursion structure is identical, which is why a tree walk is the most accurate possible name.

---

**Model 1 preview:** This model shows the minimal but complete core of a tree-walking evaluator. It handles numbers, variables, unary negation, and the four arithmetic operators. The key insight is that every case follows the same pattern: inspect the node type, recursively evaluate any children, then combine. Notice that the environment (`env`) is passed into every call so that variable lookups always reflect current state.

## Model 1: The Evaluator, Build it from Scratch

This is the complete evaluator. Every line is consequential. Read it, trace it, then run it:

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
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

**Step-by-step worked example, tracing `(+ 1 (* 2 3))`**

Suppose the AST is `BinOp("+", Num(1), BinOp("*", Num(2), Num(3)))` and `env = {}`.

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

**Key observations:** (1) Multiplication finishes entirely before addition sees any result. (2) The environment is threaded through every call but never consulted for `Num` nodes. (3) Operator precedence was *already encoded* in the tree structure by the parser; the evaluator never re-derives it.

> **Watch out!** Students often try to evaluate the operator before the children (pre-order) by writing `result = node.op` and then recursing. That will fail: you need the children's *values* before you can apply the operator. Evaluation is always post-order for expressions.

### Critical Thinking Questions

1. Trace `evaluate` on `3 + price * 2`, writing every call with its arguments and return value in order. Where in your trace does the multiplication happen relative to the addition, and which week's design decision (which module) put it there?
2. The evaluator never consults precedence, parentheses, or the grammar. State precisely where precedence "went," and why this separation of concerns is the architecture lesson of the whole pipeline.
3. We chose to make division by zero raise an error with a custom message. List two other behaviors your team could have chosen (return infinity, return zero) and one language that makes each choice. Record your project's decision.
4. Compare `evaluate` and a tree pretty-printer line by line. Write the general recipe: to add a new *consumer* of the AST (a type checker, an optimizer, a compiler), what do you write and what do you never touch?

---

**Model 2 preview:** Model 1 was correct but silent. This model adds instrumented tracing so you can *see* the call tree printed as `evaluate` runs. It is the same recursion wearing a lab coat: each call announces itself before recursing and reports its result when it returns. Studying this output is the fastest way to build the mental model you need before writing evaluators for richer node types.

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
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

### Critical Thinking Questions

5. The trace shows post-order evaluation: both children are evaluated *before* the parent combines them. Name one language feature that would break this order (hint: short-circuit evaluation of `and`/`or`).
6. How would you modify the tracer to also print the *depth* of recursion? What would that depth correspond to in terms of the tree's structure?
7. If a `BinOp` node is at depth 3 in the trace, how deep is the tree at that point? Does depth in the call stack correspond exactly to depth in the AST?

> **Watch out!** The global `_depth` counter works here because Python is single-threaded and evaluation is deterministic, but it is fragile: if `evaluate_traced` ever raises an exception mid-recursion, `_depth` is left in a wrong state and all future indentation will be off. In production tracing code, use a `try/finally` block to ensure `_depth -= 1` always runs.

---


> **Continued next session.** Statements, state, and the REPL are Day 2 of this topic: [Control Flow and Statement Semantics](https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374/gh-pages/_pages/Activities/liascript-controlflowsemantics.md).

# Part III: Tree Traversal, Why Post-Order, Not Breadth-First

## Model 5: BFS vs DFS, Why Evaluators Use Post-Order

When you evaluate an AST, you always use *depth-first, post-order* traversal: left child first, right child next, then the current node. But why not breadth-first search? After all, BFS is the "level-by-level" traversal, and it seems simpler. This model shows both traversals on the same tree and makes the answer concrete: evaluating a node requires its children's *values*, which are only available after the children have been fully evaluated. BFS visits children of a node before it visits their children's children; it cannot satisfy the "children before parent" requirement of evaluation.

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

**CTQ M5.1** The BFS order for `(1 + 2) * 3` is `* + 3 1 2`. Explain precisely why you *cannot* evaluate the tree by processing nodes in this order. Which node in the BFS order is visited before its children's values are available?

**CTQ M5.2** Post-order guarantees that every node is processed *after all its descendants*. Is this property true of DFS pre-order as well? Give a concrete example of a case where pre-order evaluation fails for the same reason BFS fails.

**CTQ M5.3** The `eval_postorder` function uses recursion, but the call stack is implicit. Rewrite it iteratively using an explicit stack, producing the same result. What is the relationship between the recursive call stack and the explicit stack you used?

---

## Practice: Allison Reading 6.3

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

[( )] `1 2 + 3 *`
[( )] `* + 3 1 2`
[(X)] `* + 3 1 2`: root first, then level 1, then leaves
[( )] `1 + 2 * 3`

1. *Three traversals.* Build the expression tree for `a * b + c * d` (where `+` is the root). Write out all three traversal orders by hand, then verify with code.

2. *BFS on a program AST.* Consider the AST for:
   ```
   while (x > 0) {
       x = x - 1;
       print x;
   }
   ```
   Draw the tree. Then list the nodes in BFS order and in post-order. Explain why the evaluator *must* use post-order for the body and cannot use BFS.

3. *Iterative post-order.* Rewrite `eval_postorder` using an explicit stack (no recursion). Test it on both trees from Model 5 (above) and Model 6 (of the AST activity).

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
- Python's `ast.NodeVisitor`: the standard library's version of the visitor pattern you just wrote by hand.

---

## Going Deeper (Optional Pointers)

The core lesson above stands on its own. The deep-dive appendices that used to follow it now live elsewhere:

> **Going further:** the material that used to live here, the standalone start-to-finish pipeline (tokenizer, parser, evaluator, statement executor, error reporting, closures, and a complete REPL, assembled as one program), is covered in depth in the dedicated tutorial: [Build a Complete Interpreter in Python: Step by Step](https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374/gh-pages/_pages/Tutorials/tutorial-build-an-interpreter.md), the complete start-to-finish companion for the Interpreter assignment. Explore it when your project or curiosity calls for it.

> **Going further:** the operational-semantics appendix (specifying languages with inference rules: judgments, big-step and small-step rules, and derivation trees) is now a self-study topic; search "big-step operational semantics" or start with Chapter 3 of Benjamin Pierce's *Types and Programming Languages* when curiosity calls for it.

---

Up next: the *Binding and Scope* activity confronts the first crack in this evaluator (one flat dictionary of variables) and together they anchor the Interpreter assignment.
