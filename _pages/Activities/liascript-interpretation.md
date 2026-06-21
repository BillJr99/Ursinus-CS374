# Tree-Walking Interpretation
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

The pipeline completes its first full circuit: this two-day module builds the **evaluator**, the recursive tree walk that turns ASTs into values, upgrading your pretty-printer's skeleton into an interpreter. With lexer, parser, and evaluator joined, you will run a program in a language that exists because you built it. The arc: **evaluation as recursion $\rightarrow$ the evaluator in code $\rightarrow$ semantics decisions hiding in plain sight $\rightarrow$ the REPL**.

---

## Directions and Group Roles

Work in your POGIL team with rotated roles (**Manager**, **Recorder**, **Presenter**, **Reflector**). Consider each model and question individually first, then discuss with your group. The Recorder posts answers to the Class Activity Questions discussion board; the Presenter reports out areas of disagreement or alternative approaches. After class, respond to the reflective prompt individually in your notebook.

---

# Part I: Evaluation Is a Fold over the Tree (Day 1)

## 1. The Recursive Definition of Meaning

**The value of a node is defined in terms of the values of its children.** This is denotational thinking made executable:

$$
\mathcal{E}[\![\text{Num}(n)]\!] = n \qquad
\mathcal{E}[\![\text{BinOp}(+, l, r)]\!] = \mathcal{E}[\![l]\!] + \mathcal{E}[\![r]\!]
$$

and so on for every node class: evaluate children first (post-order, exactly as Model 2 of the AST module predicted), then combine with the node's operation. Where the pretty-printer printed, the evaluator returns; the recursion structure is identical, which is why a tree walk is the most honest possible name.

---

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

### Critical Thinking Questions

1. Trace `evaluate` on `3 + price * 2`, writing every call with its arguments and return value in order. Where in your trace does the multiplication happen relative to the addition, and which week's design decision (which module) put it there?
2. The evaluator never consults precedence, parentheses, or the grammar. State precisely where precedence "went," and why this separation of concerns is the architecture lesson of the whole pipeline.
3. We chose to make division by zero raise an error with a custom message. List two other behaviors your team could have chosen (return infinity, return zero) and one language that makes each choice. Record your project's decision.
4. Compare `evaluate` and a tree pretty-printer line by line. Write the general recipe: to add a new *consumer* of the AST (a type checker, an optimizer, a compiler), what do you write and what do you never touch?

---

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

## Reflection Prompt

In your notebook: you have now run a program in a language whose every component you understand, with no magic remaining between the characters and the answer. How does that change how you regard the languages you use daily? Which stage of the pipeline surprised you most, and what magic do you now most want to dispel next (type checking? closures? garbage collection?)?

---

## 4. Further Reading

- Douglas Thain. *Introduction to Compilers and Language Design*, Chapter 5 and interpretation notes.
- Robert Nystrom. *Crafting Interpreters*, "Evaluating Expressions" and "Statements and State" (online): our exact path, expanded.
- Shriram Krishnamurthi. *PLAI*, the interpreter chapters, for the denotational view.
- Python's `ast.NodeVisitor` — the standard library's version of the visitor pattern you just wrote by hand.
