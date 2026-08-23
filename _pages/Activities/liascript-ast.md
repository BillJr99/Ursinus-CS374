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

Think of source code as a recipe written in dense prose, readable by a human, but awkward for a program to act on. The AST is the structured outline a chef actually follows: every step is a labeled node, ingredients are children, and the nesting encodes what happens before what. Every compiler, interpreter, linter, and code formatter you have ever used is really just a program that walks this tree. Understanding the AST is understanding the beating heart of language implementation.

## Learning Goals

By the end of this activity, you will be able to:

- Distinguish between a parse tree and an abstract syntax tree (AST) and explain what information each retains or discards
- Construct AST node classes using Python dataclasses and identify the fields required for each language construct
- Trace the post-order recursive walk over an AST to predict the output of a pretty-printer or evaluator
- Build an AST by hand for a given arithmetic or assignment expression, annotating each node with its type and children
- Apply tree transformations (constant folding, dead-code elimination) and explain how each transformation preserves program semantics

In *Tokens and Scanning: Building a Lexer* you turned characters into tokens; this session builds the structure those tokens are destined for: the **abstract syntax tree (AST)**, the central data structure of every language implementation and the hinge of your whole project. The recursive-descent parser you build in the *Recursive Descent Parsing* activity constructs exactly these nodes; here you learn to build, walk, and transform them by hand first. The arc: **parse trees vs. ASTs -> node classes -> building trees in the parser -> walking trees (printing today, evaluating soon) -> transforming trees (optimizing)**

> **Before You Begin:** This activity assumes you can:
> - Use Python dataclasses (`@dataclass`, typed fields, `field(...)`)
> - Reason about recursive tree structures (a tree node holds references to other tree nodes as children)
> - Recognize a token stream (the output of your lexer from the *Tokens and Scanning* activity) as the raw material a parser consumes
> - Understand basic operator precedence (why `2 + 3 * 4` equals `14`, not `20`)
>
> If any of these feel shaky, review them first.

---

## Directions and Group Roles

Work in your POGIL team with rotated roles (**Manager**, **Recorder**, **Presenter**, **Reflector**). Consider each model individually first, then discuss with your group. The Recorder posts answers to the Class Activity Questions discussion board; the Presenter reports out areas of disagreement or alternative approaches. After class, respond to the reflective prompt individually in your notebook.

---

# Part I: The Tree Itself

## 1. Abstract Means On Purpose

*What problem does this solve?* When a parser recognizes `(2 + 3)`, it must record every grammar rule it fired (`expr`, `additive`, `primary`, the parentheses) just to prove the string is valid. But the *evaluator* downstream does not care about parentheses or which nonterminal fired; it only cares that there is an addition of two numbers. The AST strips away that grammatical scaffolding so every later phase gets a clean, uniform data structure to walk. The fewer irrelevant details each phase has to handle, the simpler and less error-prone each phase becomes.

**A parse tree records every grammar step; an AST records only meaning.** The parse tree for `(2 + 3)` contains nodes for `expr`, `addsub`, `muldiv`, `primary`, and the parentheses: the full derivation. The AST keeps only the addition and its two operands. Parentheses vanish (their *effect*, the tree shape, remains), and single-child chains collapse.

**Each node type captures one construct.** A practical design gives every construct a class with named fields:

```
Num(value)            Var(name)            BinOp(op, left, right)
UnaryOp(op, operand)  Assign(name, expr)   Print(expr)
While(cond, body)     If(cond, then_, otherwise)   Block(statements)
FunDef(name, params, body)   Call(callee, args)
```

The set of node classes *is* your language's semantic inventory: if a construct has no node, your language cannot mean it.

> **Watch out!** Students often confuse the **parse tree** with the **AST**. The parse tree is a record of the grammar derivation: it includes every intermediate nonterminal and every piece of punctuation. The AST keeps *only meaning-bearing* nodes. Parentheses disappear entirely (their effect lives in the tree shape), and long single-child chains like `expr -> additive -> multiplicative -> primary -> Num` collapse to a single `Num` node. If your AST looks like your grammar, it is probably not abstract enough.

**Worked example, tracing `1 + 2 * 3` from tokens to AST:**

**Step 1. Tokens:**

```
NUM(1)  OP(+)  NUM(2)  OP(*)  NUM(3)
```

**Step 2. Parse tree** (using a ladder grammar with separate `additive` and `multiplicative` levels):

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

**Step 3. AST** (scaffolding collapsed, precedence now encoded in tree shape):

```
BinOp('+')
|- Num(1)
`- BinOp('*')
   |- Num(2)
   `- Num(3)
```
Only 5 nodes remain. The `*` is a child of `+`, which correctly encodes that multiplication binds tighter: `2 * 3` is evaluated first. No nonterminals, no parentheses, no grammar-level noise.

**Critical Thinking Questions (CTQs)**

> **CTQ 1.1** For the source `(2 + 3) * 4`, sketch both the full parse tree under the ladder grammar and the AST. Count nodes in each. What fraction of the parse-tree nodes was scaffolding (existed only to enforce precedence)?

> **CTQ 1.2** Parentheses appear nowhere in the AST, yet `(2 + 3) * 4` and `2 + 3 * 4` get different ASTs. Resolve the apparent paradox in two sentences.

> **CTQ 1.3** Unary `-` and binary `-` use the same character but deserve different node types. Argue why, from the perspective of the evaluator that will consume the tree.

---

## Model 1: Node Classes and the `pretty` Printer

*What problem does this solve?* Now that we know what an AST *is*, we need a concrete way to represent one in Python. This model shows how to define each node type as a dataclass (so fields have names, not just positions), and then how to *walk* the tree recursively with `pretty`. Walking a tree (visiting every node in order) is the one pattern you will use for everything: printing, evaluating, type-checking, compiling. Understand `pretty` here and the evaluator of the *Tree-Walking Interpretation* activity is trivial.

```python  liascript
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
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

> **CTQ 1.4** The two trees have the same nodes but different shapes. Which one evaluates to 20 and which to 14? Verify by hand.

> **CTQ 1.5** `pretty` dispatches on node type and recurses on children. Name the two or three lines you would change to make it *evaluate* instead of print. You have just designed the interpreter of the *Tree-Walking Interpretation* activity.

> **CTQ 1.6** The recursion visits children before finishing the parent's subtree. For evaluation, must children be processed before or after the parent's operation? Which traversal order is that (pre-order, in-order, or post-order)?

> **Watch out!** The `case _:` arm in `pretty` is a safety net, but in a real interpreter it is a bug waiting to happen. If you add a new node type (say, `FunDef`) but forget to add a corresponding `case FunDef(...):` arm, Python will silently fall through to `Unknown: ...` instead of raising an error. Every time you add a new AST node, immediately add a handler for it in *every* tree-walking function: `pretty`, `count_nodes`, `collect_vars`, `constant_fold`, and especially the evaluator.

---

## Model 2: Tree Statistics and Analysis

*What problem does this solve?* A tree walk does not have to produce output: it can also *compute* information about a program. This model shows three read-only analyses: counting nodes (useful for complexity budgets), measuring depth (tells you how deep the evaluator's call stack can get), and collecting all variable names (a primitive form of scope analysis). These same patterns (accumulate a count, accumulate a maximum, accumulate a set) recur constantly in real compilers.

```python  liascript
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
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

> **CTQ 2.1** Which feature (deeply nested arithmetic, while loops, or if/else chains) drives `depth` highest? What does this suggest about the recursion depth needed by your evaluator?

> **CTQ 2.2** `collect_vars` returns the set of all variable *references*, not all variable *definitions*. How would you modify it to distinguish defined names from referenced-but-not-defined names? What programming analysis would that enable?

---

# Part II: Building Trees in the Parser

## 2. The One-Line Upgrade

*What problem does this solve?* A first parser often returns nested tuples like `('+', left, right)`. Tuples work, but they are fragile: you have to remember that index 0 is the operator, index 1 is the left child, and so on. A dataclass gives every field a *name*, making the tree self-documenting and letting Python's structural pattern matching work cleanly.

**Preview of the connection:** the recursive-descent parser you build in the *Recursive Descent Parsing* activity constructs exactly these nodes. The upgrade from tuples is literally one line per production, every place a parser would build a tuple, it constructs a node instead: `('+', left, right)` becomes `BinOp('+', left, right)`, while the fold-left associativity logic, the tier structure, and the lookahead stay untouched.

```python  liascript
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
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

> **CTQ 3.1** The test `('NUM', 3)` vs `Num(3)`: why does the change from tuple to dataclass make debugging easier? Hint: try `repr(('*', Num(2), Num(3)))` vs `repr(BinOp('*', Num(2), Num(3)))`.

> **CTQ 3.2** The parser's structure is unchanged after the upgrade. What does this tell you about the relationship between syntax (parsing) and representation (AST)?

---


> **Your first optimizer, constant folding as a tree transformation, moved to the tutorial shelf:** [From AST Back to Code](https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374-Fall2026/gh-pages/_pages/Tutorials/tutorial-ast-to-code.md). It is the natural warm-up for that tutorial's `unparse` work.

# Part III: The `unparse` Round-Trip

## 3. Back to Source

*What problem does this solve?* Going from source text to an AST is the job of the parser. But can you go the other way, from an AST back to valid source text? This is called *unparsing* (or pretty-printing), and it is crucial for testing: if you parse a string, unparse the tree, and re-parse the result, you should get an identical tree. This round-trip property is one of the most powerful automated checks you can write for a language implementation. It also raises a subtle challenge: the AST discards parentheses, so the unparsing pass must *re-insert* them only where operator precedence requires it, no more, no less.

```python  liascript
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
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

> **CTQ 5.1** The `unparse` function adds parentheses "only when needed." How does `parent_prec` enforce this? Trace through `unparse(t1)` step by step.

> **CTQ 5.2** The round-trip test `parse(unparse(parse(s))) == parse(s)` is a **property test**. What property is it testing? Why is this important for a language implementation?

---

---
**In-class work stops here.** Everything below is homework and going-deeper material: attempt the exercises before the related assignment.

## Exercises (Homework, ~90 minutes total)

### Exercise 1: Parser Upgrade (20 min)

Convert your expression parser from tuples to the node classes, and extend to cover your statement forms (`Assign`/`Let`, `Print`, `While`, `Block`, `If`). Demonstrate `pretty` on a three-statement program.

### Exercise 2: Round-Trip (20 min)

Write `unparse(node)` producing valid source text from an AST. Verify `parse(unparse(parse(s)))` yields an identical tree for five inputs. This round-trip test will live in your project test suite forever.

### Exercise 3: Tree Statistics (15 min)

Write `count_nodes` and `depth` as tree walks. Report both for three programs: a simple expression, a while loop, and a recursive function. Which feature drives depth highest?

### Exercise 4: Constant Folding (20 min)

Extend `constant_fold` from Model 3 to handle:
- Boolean constant folding: `true and false -> false`, `true or x -> true`
- Dead code elimination: `if true { body1 } else { body2 }` -> `body1`
Test on at least 5 cases, including one where folding is NOT safe (function call with side effects).

### Exercise 5: Python's ast Module (15 min)

Run `import ast; print(ast.dump(ast.parse("2 + 3 * 4")))` in Python. Compare Python's AST structure to what you built. What nodes does Python use? How does it handle operator precedence?

---

# Part IV: Expression Trees in Practice, Adapted Examples

These models adapt code from *Foundations of Computing* by Chuck Allison (Fresh Sources, Inc.), used under the [MIT License](https://github.com/chuckallison/foundations-of-computing/blob/main/LICENSE). The adapted example rewrites Allison's binary-tree traversal as a typed `ExprNode` dataclass, connecting preorder/inorder/postorder traversal directly to prefix/infix/postfix notation, the same connection your parser and evaluator rely on.

---

## Model 6: Prefix, Infix, and Postfix, Three Views of One Tree

An expression tree encodes *both* the values *and* the operator order, but different traversal orders produce different notation styles:
- **Preorder** (root -> left -> right): prefix / Polish notation, operator comes first
- **Inorder** (left -> root -> right): infix, operator is between operands (needs parentheses for unambiguity)
- **Postorder** (left -> right -> root): postfix / reverse Polish, operator comes last, used by stack machines

Understanding this connection makes the AST concrete: it is not just a compiler data structure; it is a *notation* for expressions, and different tree walks serialize it differently.

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
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

**CTQ M6.1** The two trees above represent the same tokens in a different order: `(1+2)*3` vs `1+2*3`. What physical property of the tree (depth, root label, or shape) encodes operator precedence? Trace `eval_tree(tree2)` step by step to confirm that multiplication is evaluated before addition.

**CTQ M6.2** Postfix notation is used by stack machines (RPN calculators, the JVM bytecode verifier). Write a `eval_postfix(tokens: list[str]) -> float` function that evaluates a postfix expression using only a stack. Verify it gives the same result as `eval_tree` for both trees above.

**CTQ M6.3** The `to_infix` function adds parentheses around every subexpression. This is safe but verbose; `((1 + 2) * 3)` has more parentheses than needed. Modify `to_infix` to include parentheses only where necessary (i.e., only when a child's operator has lower precedence than the parent's). Test on `1 + 2 * 3` to confirm it produces `1 + 2 * 3` not `(1 + (2 * 3))`.

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

1. *Tree construction.* Build `ExprNode` trees for: (a) `2 + 3 * 4`, (b) `(2 + 3) * 4`, (c) `a - b + c` (left-associative). For each, print all three notations and the numeric value (using `a=2, b=3, c=4`).

2. *Postfix evaluator.* Implement `eval_postfix(tokens)` using a stack: push numbers, and on each operator pop two operands, apply the operation, and push the result. Verify it matches `eval_tree` for both trees in Model 6.

3. *Parse prefix.* Write `from_prefix(tokens: list[str]) -> ExprNode` that reconstructs a tree from a prefix token list (recursively: if the next token is an operator, read two subtrees; otherwise it's a leaf). Test it by doing the round-trip `from_prefix(to_prefix(tree).split()) == tree` for both trees in Model 6.

4. *Depth and balance.* Write `tree_depth(node)` and `count_leaves(node)`. For a perfectly balanced binary tree of depth $d$, what is the relationship between `count_leaves` and $d$? Verify with a tree of depth 3.

5. *AST for your language.* Using the `ExprNode` structure as a template, design node classes for all constructs in your team's language (not just arithmetic). Draw the tree for a `while` loop with a compound body. What fields does each node type need?

---

## Reflection Prompt

The AST is the third representation of the same program (characters -> tokens -> tree), each one closer to meaning and farther from what the programmer typed. What is gained and what is honestly lost at each translation? The tree is now the interface between the front end (lexer, parser) and the back end (evaluator, optimizer, compiler): what does this separation buy you as a language implementer?

---

## Further Reading

- **"Crafting Interpreters"**, Robert Nystrom, "Representing Code": our exact path, visualized
- **Python `ast` module**, `ast.dump(ast.parse("2+3*4"))`: meet a production AST
- **Douglas Thain. "Introduction to Compilers and Language Design"**, Chapter 5
- **"Engineering a Compiler"**, Cooper & Torczon, Chapter 5: AST construction in a real compiler

---

## Going Deeper (Optional Pointers)

The core lesson above stands on its own. The deep-dive appendices that used to follow it now live on the Tutorials shelf:

> **Going further:** the material that used to live here, expression-oriented language design (conditionals as values, `let`-expressions, sequencing, short-circuit and lazy evaluation) and the interpreter-to-compiler path (the visitor pattern, transpiling your AST to Python, JavaScript, and Haskell, and source maps), is covered in depth in the dedicated tutorial [From AST to Code: Visitors and Transpilers](https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374-Fall2026/gh-pages/_pages/Tutorials/tutorial-ast-to-code.md). Explore it when your project or curiosity calls for it; transpilation is one of the Team Language Project's extension directions.

> **Going further:** the stack-machine and bytecode-compiler material that used to live here (compiling your AST to instructions and executing them on a virtual machine) is covered in depth in the dedicated tutorial: [Building a Bytecode VM for Mini](https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374-Fall2026/gh-pages/_pages/Tutorials/tutorial-bytecode-vm.md). Explore it when your project or curiosity calls for it.

---

Up next: the *Recursive Descent Parsing* activity builds the machine that constructs these trees from tokens; together they are the core of the Parser assignment.
