<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374-Fall2026/gh-pages/_pages/Activities/liascript-ast.md or locally via https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374-Fall2026/gh-pages/_pages/Activities/liascript-ast.md

import: https://raw.githubusercontent.com/liascript/CodeRunner/master/README.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

# Abstract Syntax Trees

An abstract syntax tree (AST) is a tree that records what a program means and leaves out everything else.  Each node in the tree stands for one construct: a number, a variable, an addition, a loop.  A node's children are the smaller pieces that construct is built from, so an addition node has two children, its left and right operands.  Source code is a recipe written in prose for a person to read; the AST is the same recipe as a labeled outline that a program can follow step by step.  The analogy stops there, because an AST also fixes the order of evaluation through its nesting, which a written outline does not.  Every compiler, interpreter, linter, and code formatter you have used is a program that walks this tree, so learning the AST is learning the center of language implementation.

## Learning Goals

By the end of this activity, you will be able to:

- Distinguish between a parse tree and an abstract syntax tree (AST) and explain what information each retains or discards
- Construct AST node classes using Python dataclasses and identify the fields required for each language construct
- Trace the post-order recursive walk over an AST to predict the output of a pretty-printer or evaluator
- Build an AST by hand for a given arithmetic or assignment expression, annotating each node with its type and children
- Apply tree transformations (constant folding, dead-code elimination) and explain how each transformation preserves program semantics

In *Tokens and Scanning: Building a Lexer* you turned characters into tokens.  This session builds the structure those tokens feed: the AST, the central data structure of every language implementation and of your whole project.  The recursive-descent parser you build in the *Recursive Descent Parsing* activity constructs exactly these nodes.  Here you build, walk, and transform them by hand first.  Today's path runs from parse trees and ASTs, to node classes, to building trees in the parser, to walking trees (printing today, evaluating soon), to transforming trees (optimizing).

> **Before You Begin:** This activity assumes you can:
> - Use Python dataclasses (`@dataclass`, typed fields, `field(...)`)
> - Reason about recursive tree structures (a tree node holds references to other tree nodes as children)
> - Recognize a token stream (the output of your lexer from the *Tokens and Scanning* activity) as the raw material a parser consumes
> - Understand basic operator precedence (why `2 + 3 * 4` equals `14`, not `20`)
>
> If any of these feel shaky, review them first.

---

## Directions and Group Roles

Work in your POGIL team with your rotated roles (**Manager**, **Recorder**, **Presenter**, **Reflector**).  Please think each model through on your own first, then talk it over with your group.  The Recorder posts your answers to the Class Activity Questions discussion board, and the Presenter reports out wherever you disagreed or found another approach.  After class, please respond to the reflective prompt on your own in your notebook.

---

# Part I: The Tree Itself

## 1.  Abstract Means On Purpose

An AST keeps only the nodes that carry meaning.  A parse tree keeps everything: it records every grammar rule the parser fired.  When a parser recognizes `(2 + 3)`, it fires `expr`, `additive`, `primary`, and the parenthesis rules only to prove the string is valid.  The evaluator that runs later does not care about parentheses or about which nonterminal fired.  It only needs to know that this is an addition of two numbers.  The AST strips away that grammar scaffolding, so every later phase gets one clean, uniform structure to walk.  Each phase then handles fewer irrelevant details, which makes it simpler and less error prone.

Compare the two trees for `(2 + 3)`.  The parse tree contains nodes for `expr`, `addsub`, `muldiv`, `primary`, and the parentheses: the full derivation.  The AST keeps only the addition and its two operands.  The parentheses vanish, although their effect (the tree shape) remains, and chains of single-child nodes collapse into one node.

Each node type captures one construct.  A practical design gives every construct a class with named fields:

```
Num(value)            Var(name)            BinOp(op, left, right)
UnaryOp(op, operand)  Assign(name, expr)   Print(expr)
While(cond, body)     If(cond, then_, otherwise)   Block(statements)
FunDef(name, params, body)   Call(callee, args)
```

The set of node classes is your language's inventory of meanings.  If a construct has no node, your language cannot mean it.

> **Watch out!**  Students often confuse the parse tree with the AST.  The parse tree is a record of the grammar derivation: it includes every intermediate nonterminal and every piece of punctuation.  The AST keeps only the nodes that carry meaning.  Parentheses disappear entirely (their effect lives in the tree shape), and long single-child chains like `expr -> additive -> multiplicative -> primary -> Num` collapse to a single `Num` node.  If your AST looks like your grammar, it is probably not abstract enough.

Here is a worked example that traces `1 + 2 * 3` from tokens to AST.

Step 1, the tokens:

```
NUM(1)  OP(+)  NUM(2)  OP(*)  NUM(3)
```

Step 2, the parse tree (using a ladder grammar with separate `additive` and `multiplicative` levels):

```
expr
`- additive
   |- multiplicative
   |  `- primary -> NUM(1)
   |- OP(+)
   `- additive
      `- multiplicative
         |- primary -> NUM(2)
         |- OP(*)
         `- multiplicative
            `- primary -> NUM(3)
```

The parse tree has 10+ nodes, most of them grammar scaffolding.

Step 3, the AST (scaffolding collapsed, precedence now encoded in the tree shape):

```
BinOp('+')
|- Num(1)
`- BinOp('*')
   |- Num(2)
   `- Num(3)
```

Only 5 nodes remain.  The `*` is a child of `+`, which correctly encodes that multiplication binds tighter: `2 * 3` is evaluated first.  No nonterminals, no parentheses, no grammar-level noise.

To remember: the parse tree records how the grammar matched the input, and the AST records only what the input means.  Grouping and precedence survive as tree shape, not as nodes.

**Critical Thinking Questions (CTQs)**

> **CTQ 1.1** For the source `(2 + 3) * 4`, sketch both the full parse tree under the ladder grammar and the AST.  Count the nodes in each.  What fraction of the parse-tree nodes was scaffolding (existed only to enforce precedence)?

> **CTQ 1.2** Parentheses appear nowhere in the AST, yet `(2 + 3) * 4` and `2 + 3 * 4` get different ASTs.  Resolve the apparent paradox in two sentences.

> **CTQ 1.3** Unary `-` and binary `-` use the same character but deserve different node types.  Argue why, from the perspective of the evaluator that will consume the tree.

---

## Model 1: Node Classes and the `pretty` Printer

This model represents an AST in Python.  Each node type is a dataclass, so its fields have names instead of positions.  Then `pretty`, a pretty printer, walks the tree and prints each node on its own indented line, so you can read the tree's shape at a glance.  A tree walk visits every node in order, and it is the one pattern you will use for everything: printing, evaluating, type checking, compiling.  Once you understand `pretty`, the evaluator in the *Tree-Walking Interpretation* activity is a small step.

```python
from dataclasses import dataclass, field
from typing import Any, List, Optional

# AST node classes using dataclasses for cleaner field access
@dataclass
class Num:
    value: float

@dataclass
class Str:
    value: str

@dataclass
class Bool:
    value: bool

@dataclass
class Var:
    name: str

@dataclass
class BinOp:
    op: str
    left: Any    # left child
    right: Any   # right child

@dataclass
class UnaryOp:
    op: str
    operand: Any

@dataclass
class Assign:
    name: str
    expr: Any

@dataclass
class Print:
    expr: Any

@dataclass
class Block:
    statements: List[Any]

@dataclass
class If:
    cond: Any
    then_: Any
    otherwise: Optional[Any] = None

@dataclass
class While:
    cond: Any
    body: Any

def pretty(node, indent=0):
    """Indented tree printer: your first tree walk."""
    pad = "  " * indent
    match node:
        case Num(value=v):         print(f"{pad}Num({v})")
        case Str(value=v):         print(f"{pad}Str({v!r})")
        case Bool(value=v):        print(f"{pad}Bool({v})")
        case Var(name=n):          print(f"{pad}Var({n!r})")
        case BinOp(op=o, left=l, right=r):
            print(f"{pad}BinOp({o!r})")
            pretty(l, indent + 1)
            pretty(r, indent + 1)
        case UnaryOp(op=o, operand=x):
            print(f"{pad}UnaryOp({o!r})")
            pretty(x, indent + 1)
        case Assign(name=n, expr=e):
            print(f"{pad}Assign({n!r})")
            pretty(e, indent + 1)
        case Print(expr=e):
            print(f"{pad}Print")
            pretty(e, indent + 1)
        case Block(statements=ss):
            print(f"{pad}Block")
            for s in ss: pretty(s, indent + 1)
        case If(cond=c, then_=t, otherwise=o):
            print(f"{pad}If")
            pretty(c, indent + 1)
            pretty(t, indent + 1)
            if o: pretty(o, indent + 1)
        case While(cond=c, body=b):
            print(f"{pad}While")
            pretty(c, indent + 1)
            pretty(b, indent + 1)
        case _:
            print(f"{pad}Unknown: {node!r}")

# Build the AST for: (2 + 3) * 4
tree1 = BinOp("*", BinOp("+", Num(2), Num(3)), Num(4))
print("AST for (2+3)*4:")
pretty(tree1)

print()

# Build the AST for: 2 + 3 * 4  (different tree, different precedence)
tree2 = BinOp("+", Num(2), BinOp("*", Num(3), Num(4)))
print("AST for 2+3*4:")
pretty(tree2)
```
@LIA.eval(`["main.py"]`, `none`, `python3 main.py`)

> **CTQ 1.4** The two trees have the same nodes but different shapes.  Which one evaluates to 20 and which to 14?  Verify by hand.

### Reading the Code

- Each node type is a `@dataclass`, so `BinOp('+', l, r)` gives you `.op`, `.left`, and `.right` by name rather than by index.  That is the only difference from a tuple, and it is why `repr` on a dataclass reads like the tree it represents.
- `pretty` is the **tree walk**, and it has the shape every later pass will have: one `case` per node type, a recursive call per child, and a base case at the leaves.  A function of this shape, one that visits every node and does one thing per node type, is called a visitor.  Printing, evaluating, type checking, and compiling are all this function with the body changed.
- The indentation argument passes down through the recursion instead of living in a global.  That keeps the walk reentrant, and later it is what makes an evaluator's environment behave correctly under nesting.
- `pretty` never sees parentheses or grammar nonterminals.  The parser consumed them and left no node behind.  Their whole effect survives as the shape of the tree that `pretty` prints.

### Critical Thinking Questions

> **CTQ 1.5** `pretty` dispatches on node type and recurses on children.  Name the two or three lines you would change to make it *evaluate* instead of print.  You have just designed the interpreter of the *Tree-Walking Interpretation* activity.

> **CTQ 1.6** The recursion visits children before finishing the parent's subtree.  For evaluation, must children be processed before or after the parent's operation?  Which traversal order is that (pre-order, in-order, or post-order)?

> **Watch out!**  The `case _:` arm in `pretty` is a safety net, but in a real interpreter it is a bug waiting to happen.  If you add a new node type (say, `FunDef`) but forget to add a matching `case FunDef(...):` arm, Python silently falls through to `Unknown: ...` instead of raising an error.  Every time you add a new AST node, immediately add a handler for it in every tree-walking function: `pretty`, `count_nodes`, `collect_vars`, `constant_fold`, and especially the evaluator.

### Try It Yourself

Add a node type and watch the silent-fallthrough bug happen to you, on purpose.

```python
from dataclasses import dataclass
from typing import Any, List

@dataclass
class Num:     value: float
@dataclass
class Var:     name: str
@dataclass
class BinOp:   op: str; left: Any; right: Any
@dataclass
class Call:    fn: str; args: List[Any]      # <-- the NEW node type

def pretty(node, indent=0):
    pad = "  " * indent
    match node:
        case Num(value=v):
            print(f"{pad}Num({v})")
        case Var(name=n):
            print(f"{pad}Var({n})")
        case BinOp(op=o, left=l, right=r):
            print(f"{pad}BinOp({o})")
            pretty(l, indent + 1)
            pretty(r, indent + 1)
        # TODO: add a `case Call(fn=f, args=a):` arm that prints the function
        #       name and then recurses on every argument.
        case _:
            print(f"{pad}Unknown: {node}")

tree = BinOp("+", Num(1), Call("max", [Num(2), BinOp("*", Num(3), Var("x"))]))

print("Before you add the Call arm:")
pretty(tree)
print()
print("Notice what went wrong: the whole Call SUBTREE vanished into one")
print("'Unknown' line. The multiplication and the variable inside it were")
print("never visited. A missing case does not raise; it silently truncates.")
print()
print("Now add the arm and rerun. Every node should appear.")
```
@LIA.eval(`["main.py"]`, `none`, `python3 main.py`)

Expected output before your edit: one `Unknown:` line swallowing three nodes.  After your edit: the full tree, six nodes deep.  Remember this the next time an evaluator "works" but quietly ignores a construct.

To remember: a dataclass per node type gives every field a name, and a tree walk is one `case` per node type plus a recursive call per child.  Every new node type needs a new `case` in every walk, or the walk will skip it without complaint.

---

## Model 2: Tree Statistics and Analysis

A tree walk does not have to print anything.  It can also compute facts about a program.  This model shows three read-only analyses: counting nodes (useful for complexity budgets), measuring depth (which tells you how deep the evaluator's call stack can get), and collecting all variable names (a first form of scope analysis).  Each one accumulates something different on the way back up the recursion: a count, a maximum, or a set.  These same three patterns recur constantly in real compilers.

```python
from dataclasses import dataclass, field
from typing import Any, List, Optional

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

@dataclass
class UnaryOp:
    op: str
    operand: Any

@dataclass
class While:
    cond: Any
    body: Any

@dataclass
class If:
    cond: Any
    then_: Any
    otherwise: Any = None

@dataclass
class Block:
    statements: List[Any]

# Tree analysis functions
def count_nodes(node) -> int:
    """Count total nodes in the tree."""
    match node:
        case Num() | Var():           return 1
        case BinOp(left=l, right=r): return 1 + count_nodes(l) + count_nodes(r)
        case UnaryOp(operand=o):     return 1 + count_nodes(o)
        case While(cond=c, body=b):  return 1 + count_nodes(c) + count_nodes(b)
        case If(cond=c, then_=t, otherwise=o):
            return 1 + count_nodes(c) + count_nodes(t) + (count_nodes(o) if o else 0)
        case Block(statements=ss):   return 1 + sum(count_nodes(s) for s in ss)
        case _:                      return 1

def depth(node) -> int:
    """Maximum depth of the tree."""
    match node:
        case Num() | Var():           return 1
        case BinOp(left=l, right=r): return 1 + max(depth(l), depth(r))
        case UnaryOp(operand=o):     return 1 + depth(o)
        case While(cond=c, body=b):  return 1 + max(depth(c), depth(b))
        case If(cond=c, then_=t, otherwise=o):
            d_else = depth(o) if o else 0
            return 1 + max(depth(c), depth(t), d_else)
        case Block(statements=ss):   return 1 + max((depth(s) for s in ss), default=0)
        case _:                      return 1

def collect_vars(node) -> set:
    """Collect all variable names referenced in the tree."""
    match node:
        case Num():                  return set()
        case Var(name=n):            return {n}
        case BinOp(left=l, right=r): return collect_vars(l) | collect_vars(r)
        case UnaryOp(operand=o):     return collect_vars(o)
        case While(cond=c, body=b):  return collect_vars(c) | collect_vars(b)
        case If(cond=c, then_=t, otherwise=o):
            return collect_vars(c) | collect_vars(t) | (collect_vars(o) if o else set())
        case Block(statements=ss):   return set().union(*(collect_vars(s) for s in ss))
        case _:                      return set()

# Test: while (n > 0) { total = total + n; n = n - 1; }
# Represented as:
loop = While(
    cond=BinOp(">", Var("n"), Num(0)),
    body=Block([
        BinOp("+", Var("total"), Var("n")),  # simplified (no Assign for demo)
        BinOp("-", Var("n"), Num(1)),
    ])
)

print(f"Node count: {count_nodes(loop)}")
print(f"Tree depth: {depth(loop)}")
print(f"Variables:  {collect_vars(loop)}")

# Deeply nested arithmetic
deep = BinOp("+", BinOp("*", BinOp("-", Num(1), Num(2)), BinOp("+", Num(3), Num(4))),
             BinOp("/", Num(10), BinOp("-", Num(5), Num(3))))
print(f"\nDeep expr node count: {count_nodes(deep)}")
print(f"Deep expr depth:      {depth(deep)}")
```
@LIA.eval(`["main.py"]`, `none`, `python3 main.py`)

> **CTQ 2.1** Which feature (deeply nested arithmetic, while loops, or if/else chains) drives `depth` highest?  What does this suggest about the recursion depth needed by your evaluator?

> **CTQ 2.2** `collect_vars` returns the set of all variable *references*, not all variable *definitions*.  How would you modify it to distinguish defined names from referenced-but-not-defined names?  What programming analysis would that enable?

To remember: an analysis is a tree walk that returns a value instead of printing.  Each leaf returns a base value, and each parent combines what its children returned.

---

# Part II: Building Trees in the Parser

## 2.  The One-Line Upgrade

Switching a parser from tuples to node classes takes one line per grammar rule.  A first parser often returns nested tuples like `('+', left, right)`.  Tuples work, but they are fragile: you have to remember that index 0 is the operator, index 1 is the left child, and so on.  A dataclass gives every field a name, which makes the tree self-documenting and lets Python's structural pattern matching work cleanly.

The recursive-descent parser you build in the *Recursive Descent Parsing* activity constructs exactly these nodes.  Every place the parser would build a tuple, it builds a node instead: `('+', left, right)` becomes `BinOp('+', left, right)`.  The fold-left associativity logic, the tier structure, and the lookahead stay untouched.

```python
from dataclasses import dataclass, field
from typing import Any

@dataclass
class Num:
    value: float

@dataclass
class BinOp:
    op: str; left: Any; right: Any

@dataclass
class UnaryOp:
    op: str; operand: Any

# Minimal parser to show the upgrade
class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def peek(self):
        return self.tokens[self.pos] if self.pos < len(self.tokens) else ('EOF', None)

    def advance(self):
        tok = self.tokens[self.pos]; self.pos += 1; return tok

    def eat(self, expected_type):
        tok = self.advance()
        assert tok[0] == expected_type, f"Expected {expected_type}, got {tok[0]}"
        return tok

    def parse_expr(self):
        return self.parse_additive()

    def parse_additive(self):
        node = self.parse_multiplicative()
        while self.peek()[0] in ('+', '-'):
            op = self.advance()[0]
            right = self.parse_multiplicative()
            node = BinOp(op, node, right)   # <-- was: (op, node, right)
        return node

    def parse_multiplicative(self):
        node = self.parse_unary()
        while self.peek()[0] in ('*', '/'):
            op = self.advance()[0]
            right = self.parse_unary()
            node = BinOp(op, node, right)
        return node

    def parse_unary(self):
        if self.peek()[0] == '-':
            op = self.advance()[0]
            return UnaryOp(op, self.parse_unary())  # <-- was: (op, ...)
        return self.parse_primary()

    def parse_primary(self):
        tok = self.peek()
        if tok[0] == 'NUM':
            return Num(self.advance()[1])   # <-- was: ('num', self.advance()[1])
        elif tok[0] == '(':
            self.advance()
            node = self.parse_expr()
            self.eat(')')
            return node
        raise SyntaxError(f"Unexpected: {tok}")

def pretty(node, indent=0):
    pad = "  " * indent
    match node:
        case Num(value=v):           print(f"{pad}Num({v})")
        case BinOp(op=o, left=l, right=r):
            print(f"{pad}BinOp({o!r})")
            pretty(l, indent+1); pretty(r, indent+1)
        case UnaryOp(op=o, operand=x):
            print(f"{pad}UnaryOp({o!r})"); pretty(x, indent+1)

# Tokenize "3 + -(2 * 4)" manually for demo
tokens = [('NUM', 3), ('+', '+'), ('-', '-'), ('(', '('),
          ('NUM', 2), ('*', '*'), ('NUM', 4), (')', ')')]
p = Parser(tokens)
tree = p.parse_expr()
print("AST for 3 + -(2 * 4):")
pretty(tree)
```
@LIA.eval(`["main.py"]`, `none`, `python3 main.py`)

> **CTQ 3.1** The test `('NUM', 3)` vs `Num(3)`: why does the change from tuple to dataclass make debugging easier?  Hint: try `repr(('*', Num(2), Num(3)))` vs `repr(BinOp('*', Num(2), Num(3)))`.

> **CTQ 3.2** The parser's structure is unchanged after the upgrade.  What does this tell you about the relationship between syntax (parsing) and representation (AST)?

To remember: the parser decides the tree's shape, and the node classes decide only how each node is stored.  Changing the storage from tuples to dataclasses leaves the parsing logic alone.

---


## Model 4: Your First Optimizer, Constant Folding

Every walk so far has read the tree.  A walk can also rewrite it, returning a new tree instead of a value.  That is what a compiler optimization is.  The simplest one is **constant folding**: wherever both children of an operator are already known numbers, do the arithmetic now and replace the whole subtree with its answer.

### Examples: Fold It by Hand First

Take `2 * 3 + x * (4 + 1)` and fold it on paper, innermost first.  Fill in the node counts before you run anything:

| Pass | Tree | Nodes |
|------|------|-------|
| original | `BinOp(+, BinOp(*, 2, 3), BinOp(*, x, BinOp(+, 4, 1)))` | 9 |
| fold `2*3` | `BinOp(+, 6, BinOp(*, x, BinOp(+, 4, 1)))` | ? |
| fold `4+1` | `BinOp(+, 6, BinOp(*, x, 5))` | ? |
| anything left? | `x` is not a constant, so `x * 5` stays | ? |

Settle two questions before you look at the code.  Does folding ever need a second pass over the tree?  And is `x * 0` foldable to `0`?  Argue both, then check.

```python
from dataclasses import dataclass
from typing import Any

@dataclass
class Num:   value: float
@dataclass
class Var:   name: str
@dataclass
class BinOp: op: str; left: Any; right: Any

def show(node):
    match node:
        case Num(value=v):                return str(int(v) if v == int(v) else v)
        case Var(name=n):                 return n
        case BinOp(op=o, left=l, right=r): return f"({show(l)} {o} {show(r)})"

def size(node):
    match node:
        case BinOp(left=l, right=r): return 1 + size(l) + size(r)
        case _:                      return 1

OPS = {"+": lambda a, b: a + b, "-": lambda a, b: a - b,
       "*": lambda a, b: a * b, "/": lambda a, b: a / b}

def fold(node):
    """Rewrite the tree, returning a NEW tree with constant subtrees collapsed."""
    match node:
        case BinOp(op=o, left=l, right=r):
            l, r = fold(l), fold(r)              # children first: bottom-up
            if isinstance(l, Num) and isinstance(r, Num):
                if o == "/" and r.value == 0:
                    return BinOp(o, l, r)        # refuse: leave the error for runtime
                return Num(OPS[o](l.value, r.value))
            return BinOp(o, l, r)
        case _:
            return node

examples = [
    BinOp("+", BinOp("*", Num(2), Num(3)),
               BinOp("*", Var("x"), BinOp("+", Num(4), Num(1)))),
    BinOp("*", BinOp("+", Num(1), Num(2)), BinOp("-", Num(10), Num(4))),
    BinOp("+", Var("y"), Var("z")),
    BinOp("/", Num(1), Num(0)),
]

print(f"  {'before':34} {'after':22} {'nodes':>12}")
for tree in examples:
    folded = fold(tree)
    before, after = size(tree), size(folded)
    pct = 100 * (before - after) / before
    print(f"  {show(tree):34} {show(folded):22} {before:2} -> {after:2}  ({pct:4.0f}% gone)")

print("\n=== Does folding need a second pass? ===")
deep = BinOp("+", Num(1), BinOp("+", Num(2), BinOp("+", Num(3), Num(4))))
print(f"  {show(deep)}")
once = fold(deep)
print(f"  after one pass:  {show(once)}  (nodes {size(deep)} -> {size(once)})")
twice = fold(once)
print(f"  after two passes: {show(twice)}")
print("  Because fold() recurses into the children BEFORE testing the parent,")
print("  one bottom-up pass already reaches a fixed point here.")
```
@LIA.eval(`["main.py"]`, `none`, `python3 main.py`)

### Reading the Code

- `fold` returns a tree, not a number.  That single difference turns a read-only analysis into a transformation, and a transformation is what a compiler pass does for a living.
- The line `l, r = fold(l), fold(r)` comes before the constant test.  Folding the children first is what makes one bottom-up pass enough: by the time `fold` examines the parent, its children are already as folded as they will get.
- The division guard refuses to fold `1 / 0`.  An optimizer must never turn a program that would have raised at runtime into one that fails at compile time, or the reverse.  Every optimization obeys this rule: preserve observable behavior.
- `Var` falls to `case _:` and comes back unchanged.  Anything the optimizer does not understand, it must leave alone.

> **Watch out!**  It is tempting to add algebraic rules like `x * 0 -> 0` or `x + 0 -> x`.  Be careful: `x * 0` is only `0` if evaluating `x` has no side effects and cannot raise.  In a language where `x` might be a function call, that rewrite changes what the program does.  Real optimizers gate these rules behind an effects analysis, which is why the safe fold above only touches subtrees that are already literal numbers.

### Critical Thinking Questions

> **CTQ 3.3** In the first example, folding removed a third of the nodes and the variable `x` prevented more.  What property of a subtree makes it foldable, stated in one sentence?

> **CTQ 3.4** `fold` recurses into children before testing the parent.  Rewrite that order in your head, testing the parent first, and give a tree where the naive order misses a fold that the bottom-up order catches.

> **CTQ 3.5** The division guard leaves `1 / 0` in the tree.  Argue the other side: what would be *good* about reporting the division by zero at compile time, and what language design decision does that choice belong to?

### Try It Yourself

Extend the optimizer with one more rewrite and check that you have not broken anything.

```python
from dataclasses import dataclass
from typing import Any

@dataclass
class Num:   value: float
@dataclass
class Var:   name: str
@dataclass
class BinOp: op: str; left: Any; right: Any

def show(node):
    match node:
        case Num(value=v):                 return str(int(v) if v == int(v) else v)
        case Var(name=n):                  return n
        case BinOp(op=o, left=l, right=r): return f"({show(l)} {o} {show(r)})"

OPS = {"+": lambda a, b: a + b, "-": lambda a, b: a - b,
       "*": lambda a, b: a * b, "/": lambda a, b: a / b}

def fold(node):
    match node:
        case BinOp(op=o, left=l, right=r):
            l, r = fold(l), fold(r)
            if isinstance(l, Num) and isinstance(r, Num):
                if o == "/" and r.value == 0:
                    return BinOp(o, l, r)
                return Num(OPS[o](l.value, r.value))
            # TODO 1: add the identity rules  x + 0 -> x  and  0 + x -> x
            # TODO 2: add  x * 1 -> x  and  1 * x -> x
            # TODO 3: decide about x * 0 -> 0. Read the Watch out! above first,
            #         then either implement it or write down why you refused.
            return BinOp(o, l, r)
        case _:
            return node

cases = [
    BinOp("+", Var("x"), Num(0)),
    BinOp("*", Num(1), Var("y")),
    BinOp("*", Var("z"), Num(0)),
    BinOp("+", BinOp("*", Var("a"), Num(1)), Num(0)),
]
for tree in cases:
    print(f"  {show(tree):22} -> {show(fold(tree))}")
```
@LIA.eval(`["main.py"]`, `none`, `python3 main.py`)

Expected output once TODOs 1 and 2 are done: the first two collapse to `x` and `y`, and the fourth collapses all the way to `a`.  What you do with the third is a design decision you should be able to defend.

To remember: an optimizer is a tree walk that returns a new tree, and it folds children before parents so one pass is enough.  It may only rewrite what it can prove leaves the program's behavior unchanged.

---

# Part IV: The `unparse` Round-Trip

## 3.  Back to Source

Unparsing turns an AST back into valid source text.  The parser goes from text to tree; `unparse` (also called pretty-printing) goes the other way.  This matters for testing: if you parse a string, unparse the tree, and parse the result again, you should get an identical tree.  This round-trip property is one of the strongest automated checks you can write for a language implementation.  It also raises a challenge: the AST discards parentheses, so `unparse` must put them back only where operator precedence requires them, no more and no less.

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
    op: str; left: Any; right: Any

@dataclass
class UnaryOp:
    op: str; operand: Any

# Precedence for each operator (higher = tighter binding)
PRECEDENCE = {'+': 1, '-': 1, '*': 2, '/': 2, '^': 3}

def unparse(node, parent_prec=0):
    """Generate source text from AST; add parens only when needed."""
    match node:
        case Num(value=v):  return str(int(v) if v == int(v) else v)
        case Var(name=n):   return n
        case UnaryOp(op='-', operand=o):
            return f"-{unparse(o, 100)}"
        case BinOp(op=op, left=l, right=r):
            prec = PRECEDENCE.get(op, 0)
            left_str  = unparse(l, prec)
            right_str = unparse(r, prec + 1)  # +1 forces left-assoc parens on right
            result = f"{left_str} {op} {right_str}"
            if prec < parent_prec:
                result = f"({result})"
            return result

# Round-trip test: different trees should unparse distinctly
t1 = BinOp('*', BinOp('+', Num(2), Num(3)), Num(4))   # (2+3)*4
t2 = BinOp('+', Num(2), BinOp('*', Num(3), Num(4)))   # 2+3*4

print(f"t1 unparse: {unparse(t1)}")
print(f"t2 unparse: {unparse(t2)}")
print(f"Different? {unparse(t1) != unparse(t2)}")

# Associativity test
t3 = BinOp('-', BinOp('-', Num(5), Num(3)), Num(1))   # (5-3)-1 = 1 (left assoc)
t4 = BinOp('-', Num(5), BinOp('-', Num(3), Num(1)))   # 5-(3-1) = 3 (right assoc)
print(f"(5-3)-1 unparse: {unparse(t3)}")
print(f"5-(3-1) unparse: {unparse(t4)}")
```
@LIA.eval(`["main.py"]`, `none`, `python3 main.py`)

> **CTQ 5.1** The `unparse` function adds parentheses "only when needed."  How does `parent_prec` enforce this?  Trace through `unparse(t1)` step by step.

> **CTQ 5.2** The round-trip test `parse(unparse(parse(s))) == parse(s)` is a **property test**.  What property is it testing?  Why is this important for a language implementation?

To remember: `unparse` walks the tree and passes each node the precedence of its parent, adding parentheses only when the child binds more loosely.  Parse, unparse, and parse again should give the same tree every time.

---

**In-class work stops here.**  Everything below is homework and going-deeper material: attempt the exercises before the related assignment.

# Check Your Understanding

A parse tree and an abstract syntax tree differ in that the AST:

[(X)] Discards the punctuation and single-child chains that only existed to encode grammar structure
[( )] Contains more nodes, because it records every grammar rule applied
[( )] Is built by the lexer rather than the parser
[( )] Cannot represent nested expressions

---

The AST for `2 + 3 * 4` has `+` at the root.  That means `+` is:

[(X)] Evaluated last: its children must be computed before it can add anything
[( )] Evaluated first, because the root is visited first
[( )] Of higher precedence than `*`
[( )] Left-associative

---

Parentheses appear in the source but not in the AST.  That is because:

[(X)] Their only job was to force a grouping, and the tree's shape already records that grouping
[( )] The lexer deletes them
[( )] They are stored as node attributes rather than nodes
[( )] The AST is lossy in a way that is a known limitation

---

Adding a new consumer of the AST (a type checker, a pretty printer, an optimizer) requires:

[(X)] A new traversal over the existing node types; the nodes themselves do not change
[( )] New node classes for each consumer
[( )] Changes to the parser
[( )] A new grammar

---

## Exercises (Homework, ~90 minutes total)

### Exercise 1: Parser Upgrade (20 min)

Convert your expression parser from tuples to the node classes, and extend it to cover your statement forms (`Assign`/`Let`, `Print`, `While`, `Block`, `If`).  Demonstrate `pretty` on a three-statement program.

### Exercise 2: Round-Trip (20 min)

Write `unparse(node)`, which produces valid source text from an AST.  Verify that `parse(unparse(parse(s)))` yields an identical tree for five inputs.  This round-trip test will live in your project test suite forever.

### Exercise 3: Tree Statistics (15 min)

Write `count_nodes` and `depth` as tree walks.  Report both for three programs: a simple expression, a while loop, and a recursive function.  Which feature drives depth highest?

### Exercise 4: Constant Folding (20 min)

Extend the `fold` function from Model 4 to handle:
- Boolean constant folding: `true and false -> false`, `true or x -> true`
- Dead code elimination: `if true { body1 } else { body2 }` -> `body1`
Test on at least 5 cases, including one where folding is NOT safe (a function call with side effects).

### Exercise 5: Python's ast Module (15 min)

Run `import ast; print(ast.dump(ast.parse("2 + 3 * 4")))` in Python.  Compare Python's AST structure to what you built.  What nodes does Python use?  How does it handle operator precedence?

---

# Part V: Expression Trees in Practice, Adapted Examples

These models adapt code from *Foundations of Computing* by Chuck Allison (Fresh Sources, Inc.), used under the [MIT License](https://github.com/chuckallison/foundations-of-computing/blob/main/LICENSE).  The adapted example rewrites Allison's binary-tree traversal as a typed `ExprNode` dataclass.  It connects preorder, inorder, and postorder traversal directly to prefix, infix, and postfix notation, the same connection your parser and evaluator rely on.

---

## Model 6: Prefix, Infix, and Postfix, Three Views of One Tree

An expression tree encodes both the values and the operator order.  Different traversal orders (the order in which a walk visits the root and its children) produce different notations for the same tree:

- Preorder (root, then left, then right) gives prefix or Polish notation, with the operator first
- Inorder (left, then root, then right) gives infix notation, with the operator between its operands (this one needs parentheses to stay unambiguous)
- Postorder (left, then right, then root) gives postfix or reverse Polish notation, with the operator last, which is what stack machines use

This connection makes the AST concrete.  The tree is a compiler data structure, and it is also a *notation* for expressions: each tree walk writes it out in a different order.

> *Adapted from [`polish.py`](https://github.com/chuckallison/foundations-of-computing/blob/main/code/polish.py) in *Foundations of Computing* by Chuck Allison (Fresh Sources, Inc.), used under the [MIT License](https://github.com/chuckallison/foundations-of-computing/blob/main/LICENSE).*

```python
from dataclasses import dataclass
from typing import Optional

@dataclass
class ExprNode:
    """A node in an expression tree.
    Leaf nodes (numbers/variables) have op=None and no children.
    Internal nodes (operators) have op set and left/right children."""
    value: str                        # number, variable name, or operator
    left:  Optional['ExprNode'] = None
    right: Optional['ExprNode'] = None

    def is_leaf(self):
        return self.left is None and self.right is None

def to_prefix(node: ExprNode) -> str:
    """Preorder traversal -> prefix (Polish) notation."""
    if node.is_leaf():
        return node.value
    return f"{node.value} {to_prefix(node.left)} {to_prefix(node.right)}"

def to_infix(node: ExprNode) -> str:
    """Inorder traversal -> infix notation (with parentheses for clarity)."""
    if node.is_leaf():
        return node.value
    return f"({to_infix(node.left)} {node.value} {to_infix(node.right)})"

def to_postfix(node: ExprNode) -> str:
    """Postorder traversal -> postfix (Reverse Polish) notation."""
    if node.is_leaf():
        return node.value
    return f"{to_postfix(node.left)} {to_postfix(node.right)} {node.value}"

def eval_tree(node: ExprNode) -> float:
    """Evaluate an expression tree bottom-up (postorder)."""
    if node.is_leaf():
        return float(node.value)
    left_val  = eval_tree(node.left)
    right_val = eval_tree(node.right)
    ops = {'+': left_val + right_val, '-': left_val - right_val,
           '*': left_val * right_val, '/': left_val / right_val}
    return ops[node.value]

# Build the tree for  (1 + 2) * 3
#        *
#       / \
#      +   3
#     / \
#    1   2
tree1 = ExprNode('*',
            ExprNode('+', ExprNode('1'), ExprNode('2')),
            ExprNode('3'))

# Build the tree for  1 + 2 * 3   (multiplication binds tighter -> * is deeper)
#      +
#     / \
#    1   *
#       / \
#      2   3
tree2 = ExprNode('+',
            ExprNode('1'),
            ExprNode('*', ExprNode('2'), ExprNode('3')))

for label, tree, expected_val in [
    ("(1 + 2) * 3", tree1, 9.0),
    ("1 + 2 * 3",   tree2, 7.0),
]:
    print(f"=== {label} ===")
    print(f"  prefix:  {to_prefix(tree)}")
    print(f"  infix:   {to_infix(tree)}")
    print(f"  postfix: {to_postfix(tree)}")
    val = eval_tree(tree)
    print(f"  value:   {val}  ({'OK' if val == expected_val else 'WRONG'})")
    print()
```
@LIA.eval(`["main.py"]`, `none`, `python3 main.py`)

**CTQ M6.1** The two trees above represent the same tokens in a different order: `(1+2)*3` vs `1+2*3`.  What physical property of the tree (depth, root label, or shape) encodes operator precedence?  Trace `eval_tree(tree2)` step by step to confirm that multiplication is evaluated before addition.

**CTQ M6.2** Stack machines (RPN calculators, the JVM bytecode verifier) use postfix notation.  Write an `eval_postfix(tokens: list[str]) -> float` function that evaluates a postfix expression using only a stack.  Verify that it gives the same result as `eval_tree` for both trees above.

**CTQ M6.3** The `to_infix` function adds parentheses around every subexpression.  This is safe but verbose; `((1 + 2) * 3)` has more parentheses than needed.  Modify `to_infix` to include parentheses only where necessary (that is, only when a child's operator has lower precedence than the parent's).  Test on `1 + 2 * 3` to confirm that it produces `1 + 2 * 3`, not `(1 + (2 * 3))`.

To remember: one tree, three traversal orders, three notations.  Postorder matches how an evaluator works, because it finishes both children before it applies the operator at the root.

---

## Practice: Allison Readings 6.1 and 6.2

A postorder traversal of an expression tree visits nodes in which order?

[( )] Root, then left subtree, then right subtree
[( )] Left subtree, then root, then right subtree
[(X)] Left subtree, then right subtree, then root
[( )] Right subtree, then left subtree, then root

The postfix expression `3 4 + 5 *` evaluates to:

[( )] 23
[(X)] 35
[( )] 17
[( )] 32

In an expression tree for `a + b * c`, the root node contains:

[( )] `a`
[( )] `*`
[(X)] `+`
[( )] `b`

1.  *Tree construction.*  Build `ExprNode` trees for: (a) `2 + 3 * 4`, (b) `(2 + 3) * 4`, (c) `a - b + c` (left-associative).  For each, print all three notations and the numeric value (using `a=2, b=3, c=4`).

2.  *Postfix evaluator.*  Implement `eval_postfix(tokens)` using a stack: push numbers, and on each operator pop two operands, apply the operation, and push the result.  Verify that it matches `eval_tree` for both trees in Model 6.

3.  *Parse prefix.*  Write `from_prefix(tokens: list[str]) -> ExprNode`, which rebuilds a tree from a prefix token list (recursively: if the next token is an operator, read two subtrees; otherwise it is a leaf).  Test it with the round-trip `from_prefix(to_prefix(tree).split()) == tree` for both trees in Model 6.

4.  *Depth and balance.*  Write `tree_depth(node)` and `count_leaves(node)`.  For a perfectly balanced binary tree of depth $d$, what is the relationship between `count_leaves` and $d$?  Verify with a tree of depth 3.

5.  *AST for your language.*  Using the `ExprNode` structure as a template, design node classes for all constructs in your team's language (not only arithmetic).  Draw the tree for a `while` loop with a compound body.  What fields does each node type need?

---

## Reflection Prompt

The AST is the third representation of the same program (characters -> tokens -> tree).  Each one is closer to meaning and farther from what the programmer typed.  What is gained and what is honestly lost at each translation?  The tree is now the interface between the front end (lexer, parser) and the back end (evaluator, optimizer, compiler): what does this separation buy you as a language implementer?

---

## Further Reading

- **"Crafting Interpreters"**, Robert Nystrom, "Representing Code": our exact path, visualized
- **Python `ast` module**, `ast.dump(ast.parse("2+3*4"))`: meet a production AST
- **Douglas Thain.  "Introduction to Compilers and Language Design"**, Chapter 5
- **"Engineering a Compiler"**, Cooper & Torczon, Chapter 5: AST construction in a real compiler
- [From AST to Code: Visitors and Transpilers](https://www.billmongan.com/Ursinus-CS374-Fall2026/Tutorials/ASTToCode): expression-oriented design (conditionals as values, `let`-expressions, sequencing, short-circuit evaluation), the visitor pattern, and transpiling your AST to Python, JavaScript, and Haskell with source maps.  Transpilation is one of the Team Language Project's extension directions.
- [Building a Bytecode VM for Mini](https://www.billmongan.com/Ursinus-CS374-Fall2026/Tutorials/BytecodeVM): compiling your AST to instructions and running them on a virtual machine.

---

Up next: the *Recursive Descent Parsing* activity builds the machine that constructs these trees from tokens; together they are the core of the Parser assignment.
