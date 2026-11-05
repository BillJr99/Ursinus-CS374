<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374-Fall2026/gh-pages/_pages/Activities/liascript-calculator-to-scheme.md or locally via https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374-Fall2026/gh-pages/_pages/Activities/liascript-calculator-to-scheme.md

import: https://raw.githubusercontent.com/liascript/CodeRunner/master/README.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

# From Calculator to Scheme

Last session the calculator learned names, and we hit a wall: it computes as it reads, so it cannot skip a branch or run anything twice.  Today you take it the rest of the way.  In five small steps it becomes a language you have already written programs in: Scheme.  Every step adds one idea, and each one runs.

```text
calculator          computes while it reads
 + variables        a symbol table
 Step 1: read       text becomes nested lists, and nothing is computed yet
 Step 2: evaluate   a recursive walk over those lists
 Step 3: define     the symbol table comes back
 Step 4: if         the first thing that must not evaluate all of its parts
 Step 5: quote      lists as data, because code and data are the same lists
```

## Learning Goals

By the end of this activity, you will be able to:

- Explain why a language with conditionals must separate reading a program from evaluating it
- Read an S-expression into nested lists with a small recursive reader
- Write a recursive evaluator, and trace its children-first order on a small expression
- Add definitions and lookups with a symbol table
- Explain why `if` must be a special form rather than a primitive
- Use `quote` to treat a list as data, and explain what it means for code and data to be the same structure

> **Before You Begin:** You need *Calculator with Variables*, and the Scheme you learned at the start of the term.

---

## Directions and Group Roles

Work in your POGIL team with your rotated roles (**Manager**, **Recorder**, **Presenter**, **Reflector**).  Think each model and question through on your own first, then talk it over with your group.

---

## How Today Runs

| Segment | What your team does |
|---------|---------------------|
| Why the calculator stops working | Answer CTQ 0.1 from what you found last session |
| Steps 1 and 2: Read, Then Evaluate | Run both cells, trace `(+ 1 (* 2 3))`, and answer CTQs 1.1-2.2 |
| Step 3: Define | Run the cell, and answer CTQ 3.1 |
| Step 4: If | Predict first, run the cell, and answer CTQs 4.1 and 4.2 |
| Step 5: Quote | Run the cell, and answer CTQs 5.1 and 5.2 |
| Where this goes | Read the Interpreter connection, and name what is still missing |

---

# Why the Calculator Stops Working

The calculator's `F` computes a value the moment it reads a number.  That is fine for arithmetic.  Now suppose a program says this:

```text
if x = 0 then 1 / x else x
```

A parser that computes as it reads would divide by zero on a branch that was never meant to run.  A function body is worse, because it has to run again on every call, long after it was read.

The way out is to stop computing during the parse.  Reading produces a structure, and a separate step walks it.  Parsers usually build a tree of node objects for this, which is what the *Abstract Syntax Trees* activity showed.  Scheme gets to be simpler: its programs are already written as nested lists, so the structure is just a list.

> **CTQ 0.1** Name two things a compute-while-reading calculator can never do, and say why.

---

# Step 1: Read

The grammar has one choice to make, and one token decides it, so this is the smallest LL(1) parser you have seen:

```text
datum -> NUMBER | SYMBOL | ( datum* )
```

```python
# Step 1: read the text into nested Python lists, and compute nothing yet.
def tokenize(text):
    return text.replace("(", " ( ").replace(")", " ) ").split()

def read(tokens):
    token = tokens.pop(0)
    if token == "(":
        items = []
        while tokens[0] != ")":
            items.append(read(tokens))
        tokens.pop(0)                      # the closing )
        return items
    try:
        return int(token)
    except ValueError:
        return token                       # a symbol, kept as a string


print(tokenize("(+ 1 (* 2 3))"))
print(read(tokenize("(+ 1 (* 2 3))")))
print(read(tokenize("7")))
```
@LIA.eval(`["main.py"]`, `none`, `python3 main.py`)

> **CTQ 1.1** Where is the recursion, and which grammar rule does it match?

> **CTQ 1.2** What does the reader do with the meaning of `+`?  Why is that a good thing?

---

# Step 2: Evaluate

Evaluation is recursion over that list: evaluate the parts, and combine them.

```python
def tokenize(text):
    return text.replace("(", " ( ").replace(")", " ) ").split()

def read(tokens):
    token = tokens.pop(0)
    if token == "(":
        items = []
        while tokens[0] != ")":
            items.append(read(tokens))
        tokens.pop(0)                      # the closing )
        return items
    try:
        return int(token)
    except ValueError:
        return token                       # a symbol, kept as a string


# Step 2: evaluate.  A number is itself.  A list is an operator and its operands.
def evaluate(x):
    if isinstance(x, int):
        return x
    op, *args = x
    values = [evaluate(a) for a in args]   # post-order: children first
    if op == "+":
        return sum(values)
    if op == "*":
        result = 1
        for v in values:
            result *= v
        return result
    if op == "-":
        return values[0] - values[1]
    raise NameError(f"unknown operator {op}")


def run(text):
    return evaluate(read(tokenize(text)))


print(run("(+ 1 (* 2 3))"))
print(run("(- 10 (+ 1 2))"))
```
@LIA.eval(`["main.py"]`, `none`, `python3 main.py`)

```text
evaluate(['+', 1, ['*', 2, 3]])
  evaluate(1)                  -> 1
  evaluate(['*', 2, 3])
    evaluate(2)                -> 2
    evaluate(3)                -> 3
                               -> 6
                               -> 7
```

The children finish before the parent can combine them.  That order is called post-order, and the self-paced extension below explains why an evaluator cannot use any other.

> **CTQ 2.1** Compare this with the board calculator's `E`.  Where does each one do the addition, and when?

> **CTQ 2.2** Add `/` to `evaluate`.  What did it take?

---

# Step 3: Define

Here is the symbol table again.  A symbol evaluates by lookup, and `define` writes.  Notice that the operators moved into the same table, so `+` is now just a name whose value happens to be a function.

```python
def tokenize(text):
    return text.replace("(", " ( ").replace(")", " ) ").split()

def read(tokens):
    token = tokens.pop(0)
    if token == "(":
        items = []
        while tokens[0] != ")":
            items.append(read(tokens))
        tokens.pop(0)                      # the closing )
        return items
    try:
        return int(token)
    except ValueError:
        return token                       # a symbol, kept as a string


# Step 3: a symbol table, the same dictionary as the calculator with variables.
PRIMITIVES = {
    "+": lambda a, b: a + b,
    "-": lambda a, b: a - b,
    "*": lambda a, b: a * b,
    "=": lambda a, b: a == b,
    "<": lambda a, b: a < b,
}
symbols = dict(PRIMITIVES)

def evaluate(x):
    if isinstance(x, int):
        return x
    if isinstance(x, str):
        if x not in symbols:
            raise NameError(f"undefined name {x}")
        return symbols[x]                   # lookup
    if x[0] == "define":
        symbols[x[1]] = evaluate(x[2])      # assignment
        return None
    function, *args = [evaluate(part) for part in x]
    return function(*args)


def run(text):
    tokens = tokenize(text)
    while tokens:
        result = evaluate(read(tokens))
        if result is not None:
            print(result)


run("""
(define x 3)
(define y (+ (* x 2) 1))
y
(* x y)
""")
```
@LIA.eval(`["main.py"]`, `none`, `python3 main.py`)

> **CTQ 3.1** Why does `define` need its own check, ahead of the general call at the end of `evaluate`?  What would go wrong if `define` were treated as a call?

---

# Step 4: If

Predict before you run: what should `(if (= x 0) (/ 1 0) x)` do when `x` is 3?  This Scheme has no `/`, so evaluating that branch would be an error you can see.

```python
def tokenize(text):
    return text.replace("(", " ( ").replace(")", " ) ").split()

def read(tokens):
    token = tokens.pop(0)
    if token == "(":
        items = []
        while tokens[0] != ")":
            items.append(read(tokens))
        tokens.pop(0)                      # the closing )
        return items
    try:
        return int(token)
    except ValueError:
        return token                       # a symbol, kept as a string


# Step 4: if, which must not evaluate all of its parts.
PRIMITIVES = {
    "+": lambda a, b: a + b,
    "-": lambda a, b: a - b,
    "*": lambda a, b: a * b,
    "=": lambda a, b: a == b,
    "<": lambda a, b: a < b,
}
symbols = dict(PRIMITIVES)

def evaluate(x):
    if isinstance(x, int):
        return x
    if isinstance(x, str):
        if x not in symbols:
            raise NameError(f"undefined name {x}")
        return symbols[x]                   # lookup
    if x[0] == "define":
        symbols[x[1]] = evaluate(x[2])      # assignment
        return None
    if x[0] == "if":                        # a special form: evaluate only one branch
        test, yes, no = x[1:]
        return evaluate(yes if evaluate(test) else no)
    function, *args = [evaluate(part) for part in x]
    return function(*args)


def run(text):
    tokens = tokenize(text)
    while tokens:
        result = evaluate(read(tokens))
        if result is not None:
            print(result)


run("""
(define x 3)
(if (< x 5) 100 200)
(if (= x 0) (/ 1 0) x)
""")
```
@LIA.eval(`["main.py"]`, `none`, `python3 main.py`)

The general call at the end of `evaluate` evaluates every part first.  `if` cannot go through there, or both branches would run.  A form that decides for itself what to evaluate is called a **special form**, and `define` was one too.

> **CTQ 4.1** Move the `if` check below the line that evaluates all the parts.  What happens on the program above, and why?

> **CTQ 4.2** `and` should stop at the first false value.  Should it be a primitive or a special form?  Add it to the cell, and test `(and (= x 0) (/ 1 0))`.

---

# Step 5: Quote

`(1 2 3)` looks like a call to a function named `1`.  To talk about a list instead of running it, you need a form that hands back its operand unevaluated.

```python
def tokenize(text):
    return text.replace("(", " ( ").replace(")", " ) ").split()

def read(tokens):
    token = tokens.pop(0)
    if token == "(":
        items = []
        while tokens[0] != ")":
            items.append(read(tokens))
        tokens.pop(0)                      # the closing )
        return items
    try:
        return int(token)
    except ValueError:
        return token                       # a symbol, kept as a string


# Step 5: quote and lists.  Code and data are now the same nested lists.
PRIMITIVES = {
    "+": lambda a, b: a + b,
    "-": lambda a, b: a - b,
    "*": lambda a, b: a * b,
    "=": lambda a, b: a == b,
    "<": lambda a, b: a < b,
    "car": lambda p: p[0],
    "cdr": lambda p: p[1:],
    "cons": lambda a, p: [a] + p,
    "null?": lambda p: p == [],
}
symbols = dict(PRIMITIVES)

def evaluate(x):
    if isinstance(x, int):
        return x
    if isinstance(x, str):
        if x not in symbols:
            raise NameError(f"undefined name {x}")
        return symbols[x]                   # lookup
    if x[0] == "define":
        symbols[x[1]] = evaluate(x[2])      # assignment
        return None
    if x[0] == "quote":                     # data: hand back the list, unevaluated
        return x[1]
    if x[0] == "if":                        # a special form: evaluate only one branch
        test, yes, no = x[1:]
        return evaluate(yes if evaluate(test) else no)
    function, *args = [evaluate(part) for part in x]
    return function(*args)


def run(text):
    tokens = tokenize(text)
    while tokens:
        result = evaluate(read(tokens))
        if result is not None:
            print(result)


run("""
(define nums (quote (1 2 3)))
(car nums)
(cdr nums)
(cons 0 nums)
(null? (quote ()))
(quote (+ 1 2))
""")
```
@LIA.eval(`["main.py"]`, `none`, `python3 main.py`)

The last line of output is the point: `(+ 1 2)` is a program, and with `quote` it is also three pieces of data.

> **CTQ 5.1** Why must `quote` be a special form?

> **CTQ 5.2** Trace `(car (cdr (quote (1 2 3))))` through `evaluate`.  Which parts are evaluated, and which are not?

---

# Where This Goes

You now have numbers, names, conditionals, and lists in about fifty lines.  Three things are missing:

- **Functions.**  `lambda` needs somewhere for its parameters to live.  One dictionary will not do, for the same reason it could not hold two `x`s.  *Scope Chains and Closures* adds it, to this same code.
- **A real parser.**  The Interpreter assignment's Scheme has the same shape in C, with Flex and Bison doing the reading: its `items` rule builds these same lists.
- **Better errors.**  The extensions below cover errors that name the program instead of the interpreter.

---

**In-class work stops here.**  Everything below is self-paced.  It is the same evaluator built with explicit AST node classes in place of lists, with control flow, statements, and a REPL, for a language with ordinary syntax.

# Extension: Evaluation Is a Fold over an AST (self-paced)

## 0.  Interpreters and Compilers: When Does Translation Happen?

Before you write the evaluator, place it on the map.  There are two ways to make source text run, and the difference is *when* the translation work happens.  An interpreter reads the AST and computes values now.  A compiler translates the AST into another language, such as machine code or bytecode, that runs later.

| | **Interpreter** (what you build in this course) | **Compiler** |
|---|---|---|
| What it does with the AST | Walks it and computes values *now* | Translates it into another language (machine code, bytecode) to run *later* |
| When errors like `1 + "hello"` surface | While the program runs, at that expression | Possibly before the program runs at all |
| Cost model | Pays a small translation tax on every execution of every node | Pays translation once, then runs at full speed |
| Change the source? | Run it again | Recompile first |

The pipeline you have built so far (lexer -> parser -> AST) is the same for both.  They part ways only at this step.  A compiler for your class language would take the very same AST your parser produces and emit instructions instead of values.  (The compile-link-load extension of *Parsing Expressions and Table-Driven Parsing* and the *Build a Bytecode VM* tutorial walk that path.)  Everything you learn today about evaluation order and environments (the store of variable values) applies to both.

Quick check: a tree-walking interpreter and a compiler for the same language both receive the AST for `x * (y + 1)`.  What does each produce from it?

- [( )] Both produce the numeric answer
- [(X)] The interpreter produces the numeric answer; the compiler produces code that will compute it when run
- [( )] The interpreter produces machine code; the compiler produces the answer
- [( )] Both produce new source text in a different language

The central idea here is simple to state: **the value of any expression is computed entirely from the values of its sub-expressions.**  A number node is its own value.  An addition node evaluates both children and adds the results.  This recursive definition is both the formal meaning of the language and the literal shape of the code you will write.

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


# Extension: When Evaluation Fails (self-paced)

## 2.  Theory: An Error Is a Result Too

Model 1 quietly assumed every tree it received made sense.  Real input does not.  A `Var` node can name something the environment has never heard of.  A `/` node can be handed a zero.  An operator can arrive that the evaluator does not implement.  Each of those is a decision your language has to make *on purpose*, and the decision belongs in `SEMANTICS.md`.

There are three separate questions, and they are easy to run together:

- What counts as an error?  Is `1 / 0` an error, or is it infinity?  Is an unbound variable an error, or does it default to zero?  Different languages answer differently, and both answers are defensible.
- When is it detected?  Your evaluator finds these *while running*, which is the dynamic checking of the *Type Systems* session.  A static checker would find the unbound variable before the program started.
- What does the user see?  An error that says `KeyError: 'prise'` is a bug report about your interpreter.  An error that says `undefined variable 'prise' at line 3, column 12` is a bug report about the user's program.  Only the second is useful, and the difference is entirely in what you chose to carry through the recursion.

The practical consequence: error handling is not an afterthought bolted onto a finished evaluator.  It changes what every branch returns.  Deciding it now is much cheaper than retrofitting it during the project sprints.

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

Expected output as written: the first two report that `%` is unsupported, and the third divides by zero.  Once your TODOs are in, write the three resulting behaviors into `SEMANTICS.md` as one sentence each.  The Interpreter assignment's `SEMANTICS.md` asks for rules like these.

---


# Extension: Tree Traversal, Why Post-Order, Not Breadth-First (self-paced)

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
    a, b = child_vals                # lambdas, as in Model 2: only the selected operator runs
    ops = {'+': lambda: a + b, '-': lambda: a - b,
           '*': lambda: a * b, '/': lambda: a / b}
    return ops[root.label]()

print(f"\nEvaluated result: {eval_postorder(expr_tree)}  (expected 9.0)")
```
@LIA.eval(`["main.py"]`, `none`, `python3 main.py`)

**CTQ M4.1** The BFS order for `(1 + 2) * 3` is `* + 3 1 2`.  Explain exactly why you *cannot* evaluate the tree by processing nodes in this order.  Which node in the BFS order is visited before its children's values are available?

**CTQ M4.2** Post-order guarantees that every node is processed *after all its descendants*.  Is this property true of DFS pre-order as well?  Give a concrete example of a case where pre-order evaluation fails for the same reason BFS fails.

**CTQ M4.3** The `eval_postorder` function uses recursion, so the call stack is implicit.  Rewrite it iteratively using an explicit stack, producing the same result.  What is the relationship between the recursive call stack and the explicit stack you used?

---

## Check Your Understanding: The AST Evaluator

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

## Exercises: The AST Evaluator

1.  *Three traversals.*  Build the expression tree for `a * b + c * d` (where `+` is the root).  Write out all three traversal orders by hand, then verify with code.

2.  *BFS on a program AST.* Consider the AST for:
   ```
   while (x > 0) {
       x = x - 1;
       print x;
   }
   ```
   Draw the tree.  Then list the nodes in BFS order and in post-order.  Explain why the evaluator *must* use post-order for the body and cannot use BFS.

3.  *Iterative post-order.*  Rewrite `eval_postorder` using an explicit stack (no recursion).  Test it on the tree from Model 4 (above), on your tree from Exercise 1, and on an AST from the *Abstract Syntax Trees* activity.

4.  *Tree statistics.*  Write `max_depth(root)` and `node_count(root)` as tree walks.  For the BFS traversal of a complete binary tree of depth 4, how many nodes are at level 3?  Verify with code.

5.  *Interpreter extension.*  In your interpreter's `evaluate` function, add a `depth` counter that increments on each recursive call and prints the current depth at each node.  Run it on a deeply nested expression like `((((1 + 2) + 3) + 4) + 5)`.  What is the maximum depth, and how does it relate to the number of operators?

---

# Extension: Selection and Truth (self-paced)

An `if` statement makes one promise: it evaluates the condition, then runs exactly one of its two branches.  That promise has three consequences.  It makes guarded divisions safe.  It forces you to define what counts as true.  And it separates `if` from every ordinary function call in your language.

## 1.  The Semantics of If

Selection evaluates the condition, then exactly one branch.  The words "exactly one" matter.  In `if (x != 0) { print 10 / x; } else { print 0; }`, evaluating the untaken branch would divide by zero.  Your executor already respects this rule, because the Python `if` inside `execute` chooses which subtree to walk.  The rule deserves a name: `if` is your first **non-strict** construct.  A non-strict construct deliberately leaves some of its parts unevaluated.

Truthiness is the rule that says which values may stand as a condition.  Three policies are common.  (a) Booleans only (Java): `if (count)` is a type error.  (b) Everything has a truth value (Python): zero, the empty string, and empty collections are falsy, and everything else is truthy.  (c) A designated set (C): zero is false, and any nonzero number is true.  The policy interacts with your type system.  A booleans-only language catches accidents like `if (x = 5)` that permissive languages run without complaint.

> **Watch out!**  The string `"false"` is truthy in Python because it is a non-empty string.  Its content plays no part in the truthiness test.  This surprises many beginners who expect the meaning of a value to decide its truth.  If your language adopts Python-style universal truthiness, spell this out in your documentation.

---

## Model 1: Which Values Count as True?

Every language designer must answer one question: which values are allowed to appear as a condition?  Python accepts almost anything: zero and empty collections are false, and everything else is true.  Java accepts only actual booleans.  C treats zero as false and any nonzero number as true.  None of these is the one right answer.  Each trades convenience against catching bugs at compile time.  In this model you run all three policies side by side so the differences become concrete.

The condition values: `0`, `1`, `-3`, `""`, `"false"`, an empty list, the boolean `false`.

Run the Python truthiness table:

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
@LIA.eval(`["main.py"]`, `none`, `python3 main.py`)

### Critical Thinking Questions

1.  For each value, rule its truth under policies (a), (b), and (c) (write "error" where the policy rejects it).  Where do the policies disagree most surprisingly?  (`"false"` deserves the team's attention; it is a non-empty string, so it is truthy in Python even though it looks false.)
2.  The classic C bug `if (x = 5)` (assignment, not comparison) runs and is always true.  Which policy, and separately which grammar decision (is assignment an expression?), each independently prevents it?  Your language gets two chances to stop this bug; choose at least one.
3.  Decide your project's truthiness policy and write the `truthy(value)` specification in `SEMANTICS.md` language: exhaustive, no "etc."

---

## Model 2: If Is Non-Strict

Saying "the untaken branch is not evaluated" is one thing.  Proving it is another.  In this model a special `Bomb` node plays the role of a branch that would crash the program if it were ever executed.  If the interpreter is non-strict, the bomb never goes off, and that silence is the evidence.  Watch the single line that makes this work: a Python ternary that chooses which recursive call to make, rather than making both.

Prove that `if` does not evaluate the untaken branch:

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
        return {"+": lambda: L+R,
                "-": lambda: L-R,
                "*": lambda: L*R,
                "/": lambda: L/R}[node.op]()
    raise TypeError(f"unknown: {node!r}")

# Test 1: false condition, else branch evaluated, then_ (Bomb) skipped
result1 = evaluate(Cond(False, Bomb(), Num(42)), {})
print(f"false -> else: {result1}")  # 42

# Test 2: true condition, then_ evaluated, else_ (Bomb) skipped
result2 = evaluate(Cond(True, Num(99), Bomb()), {})
print(f"true -> then: {result2}")   # 99

# Test 3: both branches safe
result3 = evaluate(Cond(Num(0), Num(1), Num(2)), {})
print(f"0 -> else: {result3}")  # 2 (0 is falsy)
```
@LIA.eval(`["main.py"]`, `none`, `python3 main.py`)

### Critical Thinking Questions

4.  The Bomb proves non-evaluation by absence of explosion.  Why is this a better test than inspecting return values, and what general testing idea (observing side effects to detect evaluation) did you just use?
5.  In the `evaluate` function for `Cond`, the key line is `evaluate(node.then_ if truthy(cond_val) else node.else_, env)`.  This is a Python ternary that chooses which recursive call to make.  Why does this implement non-strictness, while `evaluate(node.then_, env) + evaluate(node.else_, env)` would not?

---

### Reading the Code

- `Bomb` is a node whose evaluation always raises.  Putting one in a branch is how you prove the branch was skipped.  If the program prints an answer instead of exploding, the evaluator never went there.
- The `Cond` case evaluates the condition, then evaluates exactly one of `then_` and `else_`.  Compare that with the `BinOp` case, which always evaluates both children.  That difference is the definition of non-strict.
- This is why `if` cannot be a function in a strict language.  A function call evaluates its arguments first, so `my_if(cond, a, b)` would evaluate both `a` and `b` before `my_if` ever ran, and the Bomb would go off.

### Try It Yourself

Write `if` as an ordinary function, watch it fail, then fix it the way real languages do.  The fix uses a thunk: a function that takes no arguments and wraps an expression so the expression is not evaluated until someone calls the function.

```python
from dataclasses import dataclass
from typing import Any

def boom():
    raise ZeroDivisionError("this branch should never have run")

print("=== 1. if as a FUNCTION: both arguments are evaluated first ===")
def my_if(cond, then_val, else_val):
    return then_val if cond else else_val

try:
    print(f"  my_if(True, 42, boom()) = {my_if(True, 42, boom())}")
except ZeroDivisionError as e:
    print(f"  my_if(True, 42, boom()) -> {type(e).__name__}: {e}")
    print("  The else branch ran even though the condition was True.")

print("\n=== 2. Python's own if: non-strict ===")
print(f"  42 if True else boom() = {42 if True else boom()}")

print("\n=== 3. The fix real languages use: pass THUNKS ===")
def my_if_lazy(cond, then_thunk, else_thunk):
    return then_thunk() if cond else else_thunk()

print(f"  my_if_lazy(True, lambda: 42, lambda: boom()) = "
      f"{my_if_lazy(True, lambda: 42, lambda: boom())}")

# TODO 1: explain in one sentence why wrapping in `lambda:` fixes it.
#         What did the lambda delay, and until when?

# TODO 2: Haskell needs no thunks here, because it is lazy by default.
#         What does that buy, and what does it cost? Name one thing that
#         becomes harder to reason about.

# TODO 3: your language's `if` is a NODE, not a function. Write the one
#         sentence for SEMANTICS.md stating that it evaluates its condition
#         and then exactly one branch.
```
@LIA.eval(`["main.py"]`, `none`, `python3 main.py`)

Expected output: the first call raises, the second prints `42`, the third prints `42`.  That progression is why `if` is built into the grammar rather than shipped as a library function.

Remember two things from the extensions above.  `if` evaluates its condition and then exactly one branch, which makes it non-strict.  Your truthiness policy decides which values may serve as that condition, and you must write the policy down.

# Extension: Short-Circuit Evaluation (self-paced)

You have seen that `if` skips one whole branch.  Now look inside the condition itself.  Does evaluating `a and b` always look at both `a` and `b`?  In most languages the answer is no.  That "no" is not a performance trick.  It is a guarantee, and programs are written to depend on it.  This part examines when `and` and `or` may stop early, and why your interpreter must treat them differently from ordinary binary operators.

## 2.  And/Or That Stop Early

Short-circuit operators evaluate left to right and stop as soon as the answer is known.  `false and X` never evaluates `X`.  `true or X` never evaluates `X`.  This is a semantic guarantee rather than an optimization.  The test `if (i < len(a) and a[i] > 0)` is only safe because the bounds check guards the access.  To implement this guarantee, `and` and `or` cannot be ordinary `BinOp`s, because your `BinOp` case evaluates both children first (post-order).  They need their own node and their own evaluation rule.

$$
\mathcal{E}[\![l \text{ and } r]\!] = \begin{cases} \mathcal{E}[\![l]\!] & \text{if } \mathcal{E}[\![l]\!] \text{ is falsy} \\ \mathcal{E}[\![r]\!] & \text{otherwise} \end{cases}
$$

(Note the Python-style refinement: returning the deciding operand rather than a normalized boolean is itself a design choice.  Java normalizes; Python does not.)

> **Watch out!**  Short-circuit evaluation is not universal.  Some languages do not promise it: standard Pascal (ISO 7185) leaves the order of evaluation of the operands of `and`/`or` to the implementation, and they may not both be evaluated; Fortran likewise lets the compiler skip an operand of `.and.`/`.or.` when the result is already known, without requiring it to.  Visual Basic's `And`/`Or` always evaluate both operands (VB.NET adds `AndAlso`/`OrElse` for short-circuiting).  If you port code that relies on short-circuiting as a guard, check the target language's specification.  You cannot assume the right operand is skipped.

---

## Model 3: Short-Circuit in Action

`and` and `or` cannot simply be added to your existing `BinOp` evaluator, because `BinOp` always evaluates both children before doing anything with them.  Logical operators need their own node type with their own evaluation rule, one that reaches for the right child only after deciding whether it is needed.  The Bomb test makes this difference visible.  If the right side were always evaluated, the bomb would explode.

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
@LIA.eval(`["main.py"]`, `none`, `python3 main.py`)

The guarantee that `i < n and items[i] > 0` never indexes out of bounds depends on:

[( )] The parser checking array lengths
[( )] Operator precedence placing and below comparison
[(X)] The semantic rule that and does not evaluate its right operand when the left is falsy
[( )] The type checker proving i is a number

In Python, `x or "default"` returns `"default"` when `x` is falsy.  This behavior (returning the operand rather than normalizing to `True`/`False`) is called:

[( )] Type coercion
[( )] Lazy evaluation
[(X)] Short-circuit evaluation with value-preserving semantics
[( )] Boolean normalization

### Critical Thinking Questions

6.  Trace why `LogicOp` cannot be folded into your `BinOp` case: quote the one line of the BinOp evaluator that makes it impossible.
7.  Your parser must give `and`/`or` a precedence tier.  Should `a == b and c == d` parse as `(a == b) and (c == d)`?  Place the new tier in your precedence ladder (looser or tighter than comparison?) and justify with that example.
8.  Python's `and`/`or` return one of their operands, not necessarily a boolean.  So `"hello" and "world"` returns `"world"`, and `"" or "default"` returns `"default"`.  Is this surprising?  Name one production use of this behavior.

---

## Model 4: Language Comparison

You now know that `and`/`or` short-circuit.  A second, independent question remains: what do they return?  Python returns the operand that decided the outcome, not a normalized boolean.  That choice allows short idioms like `name or "Anonymous"`.  Java always returns `true` or `false`.  Both choices are internally consistent.  This model shows their practical consequences side by side before you commit to one in your own language.

```python
# Python's short-circuit with value-preserving semantics
print("Python 'and' returns operand:")
print(f"  True and 'hello'  -> {True and 'hello'!r}")
print(f"  False and 'hello' -> {False and 'hello'!r}")
print(f"  0 and 'hello'     -> {0 and 'hello'!r}")

print("\nPython 'or' returns operand:")
print(f"  '' or 'default'   -> {('' or 'default')!r}")
print(f"  0 or 42           -> {(0 or 42)!r}")
print(f"  'x' or 'default'  -> {('x' or 'default')!r}")

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
@LIA.eval(`["main.py"]`, `none`, `python3 main.py`)

### Critical Thinking Questions

9.  The Python idiom `name = input_name or "Anonymous"` relies on short-circuit value-preserving semantics.  Rewrite this as an explicit `if` statement.  Which version do you prefer, and why?
10.  Should your project language's `and`/`or` return the deciding operand (Python style) or always return a boolean (Java style)?  Write a program whose output differs between the two choices.

---

### Reading the Code

- Python's `and`/`or` return an operand, not a boolean.  `True and "hello"` is `"hello"`.  Java's `&&` is defined to produce a `boolean`, so the same expression would not type-check there.
- Your language must make two independent decisions.  Does `and` stop early (short-circuit)?  Does it return a boolean or one of its operands (value-preserving)?  A language can pick either answer to each.
- The value-preserving choice is what makes the idiom `name = user_input or "anonymous"` work.  It is also what makes `0 or "default"` return `"default"`, which surprises people, because `0` is falsy.

### Try It Yourself

Decide both questions for your language, and find the case where the two choices disagree.

```python
print("=== Python: and/or return an OPERAND ===")
cases = [
    ('True and "hello"',  True and "hello"),
    ('False and "hello"', False and "hello"),
    ('"" or "fallback"',  "" or "fallback"),
    ('0 or "fallback"',   0 or "fallback"),
    ('"a" or "b"',        "a" or "b"),
]
for label, value in cases:
    print(f"  {label:22} -> {value!r:12} (type {type(value).__name__})")

print("\n=== A boolean-only language would give ===")
for label, value in cases:
    print(f"  {label:22} -> {bool(value)!r}")

# TODO 1: find the line where the two columns disagree in a way that
#         MATTERS, not just in type. Hint: look at the fallback idiom.

# TODO 2: your language has two independent decisions:
#           (a) does `and` evaluate its right operand when the left is false?
#           (b) does `and` return a boolean, or one of its operands?
#         Write both answers into SEMANTICS.md. Name a language for each
#         of the four combinations, or argue that one combination is silly.

# TODO 3: implement `default(value, fallback)` as a FUNCTION and show it
#         behaves differently from `value or fallback` for at least one
#         input. Which behaviour do you want in your language?
```
@LIA.eval(`["main.py"]`, `none`, `python3 main.py`)

Expected output: `0 or "fallback"` gives `"fallback"` in the first column and `True` in the second.  If your language ever means "use the default only when the value is missing", that row is the bug waiting to happen.

Remember two things from the extensions above.  `and` and `or` stop as soon as the left operand decides the answer, so they need their own node and rule instead of the `BinOp` case.  Whether they return a boolean or the deciding operand is a separate choice, and you must document both.

# Extension: Iteration (self-paced)

Loops give control flow its most useful power and its most dangerous failure mode.  A `while` loop runs its body again and again as long as the condition holds.  You need to know exactly when the condition is re-checked, whether the body gets a fresh environment each time, and what it means to exit the loop early.  These details decide which programs your language can express correctly.

## 3.  While, and the Questions It Raises

Your `While` executor re-evaluates the condition before each pass.  The semantics are definite and easy to implement, and they raise three design questions your team must answer in `SEMANTICS.md`:

1.  Does the body create a fresh scope per iteration?
2.  Do you provide `break`/`continue`, and if so, how?
3.  Will you offer a counting `for`, and is it core syntax or syntactic sugar?

The break/continue trick: use exception classes.  A `break` statement raises a `BreakSignal`, and the `While` executor catches it and leaves the loop.  `continue` works the same way with a `ContinueSignal`.

> **Watch out!** `break` and `continue` behave differently across languages.  In Python, `break` inside a `for`/`while` exits only the innermost loop; a `break` nested three loops deep does not escape all three.  Some languages (Java, Kotlin) offer labeled breaks to exit an outer loop directly.  When you implement these statements in your interpreter, decide up front how deeply nested `break` can reach, and document it.  The choice affects which programs are expressible and how much state the interpreter must track.

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
        return {"+":  lambda: L+R,
                "-":  lambda: L-R,
                "*":  lambda: L*R,
                "/":  lambda: L/R,
                ">":  lambda: float(L>R),
                "<":  lambda: float(L<R),
                ">=": lambda: float(L>=R),
                "<=": lambda: float(L<=R),
                "==": lambda: float(L==R),
                "!=": lambda: float(L!=R)}[node.op]()

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

# Print the first multiple of 7, then break out while n <= 50 is still true.
# There is no If node yet, so the break is unconditional:
# n = 7; while n <= 50: print n; n = n + 7; break
env = {}
program = Block([
    Assign("n", Num(7)),
    While(BinOp("<=", Var("n"), Num(50)),
        Block([
            Print(Var("n")),
            Assign("n", BinOp("+", Var("n"), Num(7))),
            Break(),   # only print the first one
        ])),
])
print("First multiple of 7:")
execute(program, env)
```
@LIA.eval(`["main.py"]`, `none`, `python3 main.py`)

### Critical Thinking Questions

11.  The `BreakSignal` and `ContinueSignal` exception classes contain no data.  Why use custom exception classes rather than a boolean flag variable?
12.  When `ContinueSignal` is caught by the `While` executor's `except ContinueSignal: continue`, what Python statement does the bare `continue` refer to?  Trace the control flow carefully.
13.  **Desugaring.**  Implement `for (let i = 0; i < n; i = i + 1) { body }` as a parser transformation that produces the abstract syntax tree (AST) of `{ let i = 0; while (i < n) { body; i = i + 1; } }`.  What is this called, and why does it mean you get `for` loops for free with no new evaluator code?

---

# Extension: Statements, State, and the REPL (self-paced)

## 4.  Theory: Executing Statements

An expression produces a value.  A statement produces an effect.  An `Assign` updates the environment, a `Print` writes output, a `Block` (a list of statements) executes its children in order, and a `While` re-evaluates its condition.  The executor therefore passes the environment through every call:

```python
def execute(stmt, env):
    Assign(name, e)   -> env[name] = evaluate(e, env)
    Print(e)          -> print(evaluate(e, env))
    Block(stmts)      -> for s in stmts: execute(s, env)
    If(c, t, o)       -> execute(t if truthy(evaluate(c, env)) else o, env)
    While(c, body)    -> while truthy(evaluate(c, env)): execute(body, env)
```

Notice `truthy`.  Your language must decide what counts as true (only a boolean? any nonzero number? an empty string?).  That semantics decision has daily consequences.

In a tree-walking interpreter, executing the program's `while` loop one million times will re-walk the loop body's subtree one million times.  The principal cost this design accepts, relative to compilation, is:

[( )] Incorrect results on large inputs
[(X)] Repeated traversal and dispatch overhead per execution of the same code
[( )] Loss of operator precedence
[( )] The inability to support variables

---

**Model 5 preview:** Where expressions return values, statements change the world.  They update the environment, produce output, or repeat a block.  This model introduces `execute`, a sibling function to `evaluate` that handles the statement layer.  The most important design rule is that `execute` must always pass the same `env` dictionary through every recursive call, so that assignments made inside a loop body are visible after the loop ends.

> **Watch out!**  A common mistake is for `execute` to return `None` (implicitly) for every branch, and for a caller to use that `None` as if it were a language value.  For example, a caller might print the result of `execute(Print(...), env)` instead of relying on the output already printed inside `execute`.  Statements produce effects, not values.  Callers of `execute` should never inspect its return value.

## Model 5: Complete Statement Executor

```python
from dataclasses import dataclass, field
from typing import Any, List, Optional

# --- AST nodes ----------------------------------------------------------------
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

# --- Evaluator ----------------------------------------------------------------
def evaluate(node, env):
    if isinstance(node, Num):   return node.value
    if isinstance(node, Var):
        if node.name not in env: raise NameError(f"undefined: {node.name!r}")
        return env[node.name]
    if isinstance(node, BinOp):
        L, R = evaluate(node.left, env), evaluate(node.right, env)
        return {"+":  lambda: L+R,
                "-":  lambda: L-R,
                "*":  lambda: L*R,
                "/":  lambda: L/R,
                ">":  lambda: L>R,
                "<":  lambda: L<R,
                ">=": lambda: L>=R,
                "<=": lambda: L<=R,
                "==": lambda: L==R,
                "!=": lambda: L!=R}[node.op]()
    raise TypeError(f"unknown expr node: {node!r}")

def truthy(val):
    if isinstance(val, bool): return val
    if isinstance(val, (int, float)): return val != 0
    return val is not None

# --- Executor ----------------------------------------------------------------
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

# --- Test: n = 5; total = 0; while n > 0: total += n; n -= 1; print total ---
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
@LIA.eval(`["main.py"]`, `none`, `python3 main.py`)

### Critical Thinking Questions

14.  Predict the output before running; then run.  If they differ, the bug hunt order is: lexer -> parser tree (use pretty-printer!) -> evaluator.  Why that order?
15.  Print the environment after execution.  Should `n` still exist after the loop?  Defend your language's answer; both choices are defensible.
16.  Add a `truthy(0.0)` call and a `truthy(None)` call to the test.  What do they return?  How does your `truthy` definition match Python's?  Where do they differ?

---

### Reading the Code

- `execute` returns nothing.  Every branch works by effect: writing to `env`, printing, or looping.  It differs structurally from `evaluate`, which returns a value and touches nothing.
- The same `env` dictionary is passed to every recursive call, never copied.  That is what makes an assignment inside a loop body visible after the loop ends, and it is the opposite of the fresh-frame-per-call discipline that closures need.
- `While` re-evaluates its condition expression on every pass.  It does not cache it.  If it did, `while n > 0` would run forever.
- `Block` executes its children in order and discards each result.  Order matters here in a way it never did for expressions.

### Try It Yourself

Add the two statements the executor is missing, using the trick real interpreters use.

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
class Assign: name: str; expr: Any
@dataclass
class Print:  expr: Any
@dataclass
class Block:  stmts: List[Any]
@dataclass
class While:  cond: Any; body: Any
@dataclass
class Break:  pass
@dataclass
class Continue: pass

class BreakSignal(Exception):    pass
class ContinueSignal(Exception): pass

def evaluate(node, env):
    if isinstance(node, Num): return node.value
    if isinstance(node, Var): return env.get(node.name, 0)
    if isinstance(node, BinOp):
        L, R = evaluate(node.left, env), evaluate(node.right, env)
        return {"+": lambda: L+R, "-": lambda: L-R, "*": lambda: L*R,
                "/": lambda: L/R, ">": lambda: L>R, "<": lambda: L<R,
                "==": lambda: L==R, "%": lambda: L%R}[node.op]()
    raise TypeError(node)

def execute(stmt, env):
    if isinstance(stmt, Assign): env[stmt.name] = evaluate(stmt.expr, env)
    elif isinstance(stmt, Print): print("   ", evaluate(stmt.expr, env))
    elif isinstance(stmt, Block):
        for s in stmt.stmts: execute(s, env)
    elif isinstance(stmt, While):
        while evaluate(stmt.cond, env):
            execute(stmt.body, env)
            # TODO 1: catch BreakSignal here and stop the loop.
            # TODO 2: catch ContinueSignal and go to the next iteration.
            #         Careful: where exactly does the try/except go for
            #         continue to skip the REST of the body but still
            #         re-check the condition?
    elif isinstance(stmt, Break):    raise BreakSignal()
    elif isinstance(stmt, Continue): raise ContinueSignal()
    else: raise TypeError(stmt)

#  n = 0; while n < 10 { n = n + 1; if n % 2 == 0 continue; if n > 7 break; print n }
# Written without If for now: just exercise break.
prog = Block([
    Assign("n", Num(0)),
    While(BinOp("<", Var("n"), Num(10)),
          Block([Assign("n", BinOp("+", Var("n"), Num(1))),
                 Print(Var("n"))])),
])
print("Counting to 10 with no break yet:")
try:
    execute(prog, {})
except (BreakSignal, ContinueSignal) as sig:
    print(f"  {type(sig).__name__} escaped the loop -- that is TODO 1/2.")

# TODO 3: once break works, put a Break in the body and show the loop
#         stopping early. Then answer: why is an EXCEPTION the natural
#         mechanism here, when break is not an error?
```
@LIA.eval(`["main.py"]`, `none`, `python3 main.py`)

Expected output as written: the numbers 1 through 10.  Add a `Break` and, until TODO 1 is done, the signal escapes the loop entirely and the outer handler catches it.  That is the bug the `except` inside `While` prevents.

## Model 6: The REPL

The REPL (Read-Eval-Print Loop) is what makes your language feel like a language.  It runs the whole pipeline (tokenize, parse, evaluate) inside a loop that keeps a single `env` across lines, so earlier assignments are visible in later ones.  This model uses a simulated REPL (a list of inputs instead of real keyboard input) so it can run here without interaction.  The structure is the same as what you would wire up with Python's `input()`.

> **Watch out!**  Because the REPL's `env` dictionary persists across lines, a variable assigned on line 1 is still live on line 100.  So the order in which the user types lines matters, and re-running the REPL from scratch starts with an empty environment.  Students sometimes expect the REPL to behave like a script (isolated, top-to-bottom) rather than a stateful session.  They are different execution models.  State in your language documentation which one your REPL provides.

```python
from dataclasses import dataclass
from typing import Any
import re

# Minimal tokenizer -> parser -> evaluator pipeline for the REPL
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
        return {"+": lambda: L+R,
                "-": lambda: L-R,
                "*": lambda: L*R,
                "/": lambda: L/R}[node.op]()

# --- Simulate a REPL session ------------------------------------------------
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
        print(f"  {result}")
    except Exception as e:
        print(f"  Error: {e}")

print(f"\nFinal environment: {env}")
```
@LIA.eval(`["main.py"]`, `none`, `python3 main.py`)

### Reading the Code

- The REPL is a loop around the same three stages the whole session has been building: tokenize, parse, evaluate (here `evaluate` also handles `Assign`, so one function covers both expressions and assignments).  Nothing new is required to make a language interactive.  You stop reading from a file and start reading from the user.
- `env` lives outside the loop, which is what makes the session stateful.  A variable defined on one line is visible on the next.  Move it inside the loop and every line would start from nothing.
- Errors are caught per line rather than ending the session.  This is the `LangError` discipline from the AST evaluator extension at work: a user's typo prints a message and the prompt comes back.

### Critical Thinking Questions

17.  A real REPL must handle errors without dying: if the user types `1/0` or `undefined_var`, the REPL should print an error and continue.  The session loop above already wraps each line in `try/except Exception`.  Add `"1/0"` and `"undefined_var"` to `repl_input` and run it.  Which line reaches the `except`, and why does the other one never raise (look at the `Var` case of `evaluate`)?  What would happen to the rest of the session without the `try/except`?  Catching every `Exception` lumps all failures together; identify the three error classes you would catch instead (one per stage: lex, parse, eval).
18.  The REPL above has a persistent `env` dictionary.  If a user types `x = 10` and then `x = 20`, what should happen?  Should the language allow rebinding?
19.  REPLs for functional languages (Haskell's `ghci`, Scheme's REPL) do not allow mutation.  How would you implement a purely functional REPL where each "assignment" introduces a new immutable binding rather than updating an old one?

---



---

Remember two things from the extensions above.  `while` re-checks its condition before every pass, and `break` and `continue` unwind to the loop by raising signal exceptions.  `execute` works by effect and threads one shared `env` through every call, and the REPL is that same pipeline wrapped in a loop that keeps `env` alive between lines.

---

## Check Your Understanding: Control Flow

`if` cannot be written as an ordinary function in a strict language because:

[(X)] A function call evaluates all its arguments first, so both branches would run before the function did
[( )] Functions cannot return different types from different branches
[( )] The condition would be evaluated twice
[( )] `if` needs access to the environment and functions do not

---

In Python, `0 or "fallback"` evaluates to `"fallback"`. This shows that Python's `or` is:

[(X)] Short-circuiting *and* value-preserving: it returns an operand, not a boolean
[( )] Short-circuiting only: it returns `True` or `False`
[( )] Neither: it evaluates both sides and returns the second
[( )] Coercing `0` to a string

---

`execute` returns nothing and `evaluate` returns a value. That difference exists because:

[(X)] Statements produce effects on the environment and output; expressions produce values
[( )] Python functions cannot return from inside a `while`
[( )] `execute` is called for its speed, not its result
[( )] Statements are evaluated lazily

---

`break` is implemented by raising an exception caught in the `While` executor. Why is that natural even though `break` is not an error?

[(X)] It needs to unwind out of arbitrarily nested statement execution to one known place, which is exactly what exceptions do
[( )] Python offers no other way to leave a loop
[( )] It makes `break` slower, which discourages its use
[( )] Exceptions are the only values `execute` can return

---

## Exercises: Control Flow
1.  *Implement the trio.*  Add `LogicOp` with short-circuit `and`/`or` and a unary `not` to your lexer, parser (new tier), and evaluator.  Reproduce the Bomb test inside your language: a right operand that would raise (divide by zero) but is never reached.
2.  *Break and continue.*  Implement both using custom exception classes (`BreakSignal`, `ContinueSignal`) raised by the statements and caught by the `While` executor.  Demonstrate a search loop that exits early on finding a value.
3.  *Desugaring.*  Implement `for (let i = 0; i < n; i = i + 1) { ... }` purely in the parser, producing the AST of the equivalent block-plus-while with no new evaluator code.  Show the `pretty` output proving the rewrite.
4.  *Truthiness differential.*  Write one program whose output differs under booleans-only versus Python-style truthiness, and confirm your interpreter follows your documented policy.
5.  *Step limit.*  Add a `max_steps` parameter to your `While` executor that raises `RuntimeError` after N iterations.  This protects against infinite loops in student programs.  Test it with `while 1 > 0: print 1` and a limit of 100.
6.  *Complete the executor.*  Implement `execute` for all your statement nodes with the exception pattern from class, define and document `truthy` for your language, and demonstrate the summation program plus an `if/else` program.
7.  *The REPL.* Write the read-evaluate-print loop: prompt, read a line, tokenize, parse, execute against a persistent environment, repeat, catching and printing every error class without dying.  Your language now has an interactive shell; transcript required.
8.  *Error taxonomy.*  Construct one program each that fails in the lexer, the parser, and the evaluator.  Verify each error message names its stage and location; improve the worst one.
9.  *Semantics memo.*  Document three semantics decisions your team made today (truthiness, division by zero, loop variable persistence) in a `SEMANTICS.md` your project will grow all semester.
10.  *Loop counter.*  Modify the `While` executor to count the number of times the loop body executes, and report the count after the loop ends (for example, add it to a statistics dictionary your interpreter prints at the end of a run).  Show the count for the summation program and for a loop whose condition is false the first time (count 0).  If you also did Exercise 5, let the step limit read this same counter rather than keeping a second one.

---

---

## Further Reading

- Douglas Thain.  *Introduction to Compilers and Language Design*, Chapter 5 and interpretation notes.
- Robert Nystrom.  *Crafting Interpreters*, "Evaluating Expressions" and "Statements and State" (online): our exact path, expanded.
- Shriram Krishnamurthi.  *PLAI*, the interpreter chapters, for the denotational view.
- Python's `ast.NodeVisitor`: the standard library's version of the visitor pattern you just wrote by hand.
- [Build a Complete Interpreter in Python](https://www.billmongan.com/Ursinus-CS374-Fall2026/Tutorials/BuildAnInterpreter): the whole pipeline assembled as one program, covering tokenizer, parser, evaluator, statement executor, error reporting, closures, and a REPL.  The start-to-finish companion for the Interpreter assignment.
- Operational semantics: specifying a language with inference rules, big-step and small-step judgments, and derivation trees.  Chapter 3 of Benjamin Pierce's *Types and Programming Languages*.
- Douglas Thain.  *Introduction to Compilers and Language Design*, Chapter 6 and 7 notes on control flow.
- Robert Nystrom.  *Crafting Interpreters*, "Control Flow" (online), including the break-via-exception trick.
- Robert Sebesta.  *Concepts of Programming Languages*, the statement-level control structures chapter.
- Python docs on [short-circuit evaluation](https://docs.python.org/3/reference/expressions.html#boolean-operations): the return-operand semantics documented precisely.

---

**Up next:** *Binding and Scope* gives us the vocabulary for what a name means and where that meaning reaches.
