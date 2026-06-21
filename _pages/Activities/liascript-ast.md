<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://github.com/BillJr99/Ursinus-CS374-Fall2026/blob/gh-pages/_pages/Activities/liascript-ast.md

import: https://raw.githubusercontent.com/liascript/CodeRunner/master/README.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

# Abstract Syntax Trees

Your parser has been quietly building nested tuples; this two-day module makes the tree a first-class citizen: the **abstract syntax tree (AST)**, the central data structure of every language implementation and the hinge of your whole project. The arc: **parse trees vs. ASTs → node classes → building trees in the parser → walking trees (printing today, evaluating soon) → transforming trees (optimizing)**

---

## Directions and Group Roles

Work in your POGIL team with rotated roles (**Manager**, **Recorder**, **Presenter**, **Reflector**). Consider each model individually first, then discuss with your group.

---

# Part I: The Tree Itself

## 1. Abstract Means On Purpose

**A parse tree records every grammar step; an AST records only meaning.** The parse tree for `(2 + 3)` contains nodes for `expr`, `addsub`, `muldiv`, `primary`, and the parentheses: the full derivation. The AST keeps only the addition and its two operands. Parentheses vanish (their *effect* — the tree shape — remains), and single-child chains collapse.

**Each node type captures one construct.** A practical design gives every construct a class with named fields:

```
Num(value)            Var(name)            BinOp(op, left, right)
UnaryOp(op, operand)  Assign(name, expr)   Print(expr)
While(cond, body)     If(cond, then_, otherwise)   Block(statements)
FunDef(name, params, body)   Call(callee, args)
```

The set of node classes *is* your language's semantic inventory: if a construct has no node, your language cannot mean it.

**Critical Thinking Questions (CTQs)**

> **CTQ 1.1** For the source `(2 + 3) * 4`, sketch both the full parse tree under the ladder grammar and the AST. Count nodes in each. What fraction of the parse-tree nodes was scaffolding (existed only to enforce precedence)?

> **CTQ 1.2** Parentheses appear nowhere in the AST, yet `(2 + 3) * 4` and `2 + 3 * 4` get different ASTs. Resolve the apparent paradox in two sentences.

> **CTQ 1.3** Unary `-` and binary `-` use the same character but deserve different node types. Argue why, from the perspective of the evaluator that will consume the tree.

---

## Model 1: Node Classes and the `pretty` Printer

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

> **CTQ 1.5** `pretty` dispatches on node type and recurses on children. Name the two or three lines you would change to make it *evaluate* instead of print. You have just designed next week's interpreter.

> **CTQ 1.6** The recursion visits children before finishing the parent's subtree. For evaluation, must children be processed before or after the parent's operation? Which traversal order is that (pre-order, in-order, or post-order)?

---

## Model 2: Tree Statistics and Analysis

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

> **CTQ 2.1** Which feature — deeply nested arithmetic, while loops, or if/else chains — drives `depth` highest? What does this suggest about the recursion depth needed by your evaluator?

> **CTQ 2.2** `collect_vars` returns the set of all variable *references*, not all variable *definitions*. How would you modify it to distinguish defined names from referenced-but-not-defined names? What programming analysis would that enable?

---

# Part II: Building Trees in the Parser

## 2. The One-Line Upgrade

Your expression parser changes almost nothing: every place it built a tuple now constructs a node. `('+', left, right)` becomes `BinOp('+', left, right)`. The fold-left associativity logic, the tier structure, the lookahead: untouched.

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

## Model 3: Tree Transformations — Your First Optimizer

Trees can be *transformed* as well as traversed. The simplest transformation is **constant folding**: evaluating constant sub-expressions at compile time.

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

def constant_fold(node):
    """Simplify constant sub-expressions: 2+3 → 5, 1*x → x, etc."""
    match node:
        case Num() | Var():
            return node

        case UnaryOp(op='-', operand=Num(value=v)):
            return Num(-v)   # -5 → Num(-5)

        case UnaryOp(op=op, operand=o):
            return UnaryOp(op, constant_fold(o))

        case BinOp(op=op, left=left, right=right):
            l = constant_fold(left)
            r = constant_fold(right)
            # Both constant: compute now
            if isinstance(l, Num) and isinstance(r, Num):
                match op:
                    case '+': return Num(l.value + r.value)
                    case '-': return Num(l.value - r.value)
                    case '*': return Num(l.value * r.value)
                    case '/' if r.value != 0: return Num(l.value / r.value)
            # Algebraic identities: x * 1 → x, x + 0 → x, etc.
            if isinstance(r, Num):
                if r.value == 0 and op == '+': return l
                if r.value == 0 and op == '-': return l
                if r.value == 1 and op == '*': return l
                if r.value == 1 and op == '/': return l
            if isinstance(l, Num):
                if l.value == 0 and op == '+': return r
                if l.value == 1 and op == '*': return r
                if l.value == 0 and op == '*': return Num(0)
            return BinOp(op, l, r)

def pretty(node):
    match node:
        case Num(value=v):           return str(v)
        case Var(name=n):            return n
        case BinOp(op=o, left=l, right=r): return f"({pretty(l)} {o} {pretty(r)})"
        case UnaryOp(op=o, operand=x):     return f"(-{pretty(x)})"

# Test constant folding
tests = [
    BinOp('+', Num(2), Num(3)),                          # 2+3 → 5
    BinOp('*', Num(1), Var('x')),                         # 1*x → x
    BinOp('+', Var('x'), Num(0)),                         # x+0 → x
    BinOp('*', Num(2), BinOp('+', Num(3), Num(4))),       # 2*(3+4) → 2*7 → 14
    BinOp('+', BinOp('*', Num(2), Num(3)), Var('y')),     # (2*3)+y → 6+y
    UnaryOp('-', Num(5)),                                  # -5 → Num(-5)
]

for t in tests:
    folded = constant_fold(t)
    print(f"{pretty(t):30} → {pretty(folded)}")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

> **CTQ 4.1** Constant folding is safe for pure expressions. Why is it *unsafe* to fold `f() + 0` to `f()` if `f` has side effects?

> **CTQ 4.2** The folding rule `x * 0 → 0` is an algebraic simplification. Why does this rule require checking `l.value == 0` rather than checking `isinstance(l, Num) and l.value == 0`? (They're the same — but why does the type check matter for correctness?)

> **CTQ 4.3** Dead code elimination is another tree transformation: `if true { body1 } else { body2 }` → `body1`. How would you extend `constant_fold` to handle this case?

---

[[MC]]
After upgrading the parser to emit AST nodes, the team's old torture tests still pass with identical tree shapes. The best explanation is:

    [(x)] The grammar and parsing logic determine the shape; the node classes only changed the representation
    [( )] Python tuples and dataclasses are interchangeable types
    [( )] The lexer normalizes the input before parsing
    [( )] Associativity moved into the node classes

---

[[MC]]
`constant_fold` is a tree *transformation* that returns a new tree. What does this say about ASTs?

    [( )] ASTs can only be read, not modified
    [(x)] The same tree-walking pattern used for evaluation and printing also supports transformation and optimization
    [( )] Constant folding requires the evaluator to run first
    [( )] Only leaf nodes can be transformed

---

# Part III: The `unparse` Round-Trip

## 3. Back to Source

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

## Exercises

### Exercise 1 — Parser Upgrade (20 min)
Convert your expression parser from tuples to the node classes, and extend to cover your statement forms (`Assign`/`Let`, `Print`, `While`, `Block`, `If`). Demonstrate `pretty` on a three-statement program.

### Exercise 2 — Round-Trip (20 min)
Write `unparse(node)` producing valid source text from an AST. Verify `parse(unparse(parse(s)))` yields an identical tree for five inputs. This round-trip test will live in your project test suite forever.

### Exercise 3 — Tree Statistics (15 min)
Write `count_nodes` and `depth` as tree walks. Report both for three programs: a simple expression, a while loop, and a recursive function. Which feature drives depth highest?

### Exercise 4 — Constant Folding (20 min)
Extend `constant_fold` from Model 3 to handle:
- Boolean constant folding: `true and false → false`, `true or x → true`
- Dead code elimination: `if true { body1 } else { body2 }` → `body1`
Test on at least 5 cases, including one where folding is NOT safe (function call with side effects).

### Exercise 5 — Python's ast Module (15 min)
Run `import ast; print(ast.dump(ast.parse("2 + 3 * 4")))` in Python. Compare Python's AST structure to what you built. What nodes does Python use? How does it handle operator precedence?

---

## Reflection Prompt

The AST is the third representation of the same program (characters → tokens → tree), each one closer to meaning and farther from what the programmer typed. What is gained and what is honestly lost at each translation? The tree is now the interface between the front end (lexer, parser) and the back end (evaluator, optimizer, compiler): what does this separation buy you as a language implementer?

---

## Further Reading

- **"Crafting Interpreters"** — Robert Nystrom, "Representing Code": our exact path, visualized
- **Python `ast` module** — `ast.dump(ast.parse("2+3*4"))` — meet a production AST
- **Douglas Thain. "Introduction to Compilers and Language Design"** — Chapter 5
- **"Engineering a Compiler"** — Cooper & Torczon, Chapter 5: AST construction in a real compiler
