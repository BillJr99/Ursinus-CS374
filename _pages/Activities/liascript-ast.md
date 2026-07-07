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

Think of source code as a recipe written in dense prose — readable by a human, but awkward for a program to act on. The AST is the structured outline a chef actually follows: every step is a labeled node, ingredients are children, and the nesting encodes what happens before what. Every compiler, interpreter, linter, and code formatter you have ever used is really just a program that walks this tree. Understanding the AST is understanding the beating heart of language implementation.

## Learning Goals

By the end of this activity, you will be able to:

- Distinguish between a parse tree and an abstract syntax tree (AST) and explain what information each retains or discards
- Construct AST node classes using Python dataclasses and identify the fields required for each language construct
- Trace the post-order recursive walk over an AST to predict the output of a pretty-printer or evaluator
- Build an AST by hand for a given arithmetic or assignment expression, annotating each node with its type and children
- Apply tree transformations (constant folding, dead-code elimination) and explain how each transformation preserves program semantics

Your parser has been quietly building nested tuples; this two-day module makes the tree a first-class citizen: the **abstract syntax tree (AST)**, the central data structure of every language implementation and the hinge of your whole project. The arc: **parse trees vs. ASTs → node classes → building trees in the parser → walking trees (printing today, evaluating soon) → transforming trees (optimizing)**

> **Before You Begin:** This activity assumes you can:
> - Use Python dataclasses (`@dataclass`, typed fields, `field(...)`)
> - Reason about recursive tree structures (a tree node holds references to other tree nodes as children)
> - Read a simple recursive-descent parser and trace how it builds up a result from tokens
> - Understand basic operator precedence (why `2 + 3 * 4` equals `14`, not `20`)
>
> If any of these feel shaky, review them first.

---

## Directions and Group Roles

Work in your POGIL team with rotated roles (**Manager**, **Recorder**, **Presenter**, **Reflector**). Consider each model individually first, then discuss with your group.

---

# Part I: The Tree Itself

## 1. Abstract Means On Purpose

*What problem does this solve?* When a parser recognizes `(2 + 3)`, it must record every grammar rule it fired — `expr`, `additive`, `primary`, the parentheses — just to prove the string is valid. But the *evaluator* downstream does not care about parentheses or which nonterminal fired; it only cares that there is an addition of two numbers. The AST strips away that grammatical scaffolding so every later phase gets a clean, uniform data structure to walk. The fewer irrelevant details each phase has to handle, the simpler and less error-prone each phase becomes.

**A parse tree records every grammar step; an AST records only meaning.** The parse tree for `(2 + 3)` contains nodes for `expr`, `addsub`, `muldiv`, `primary`, and the parentheses: the full derivation. The AST keeps only the addition and its two operands. Parentheses vanish (their *effect* — the tree shape — remains), and single-child chains collapse.

**Each node type captures one construct.** A practical design gives every construct a class with named fields:

```
Num(value)            Var(name)            BinOp(op, left, right)
UnaryOp(op, operand)  Assign(name, expr)   Print(expr)
While(cond, body)     If(cond, then_, otherwise)   Block(statements)
FunDef(name, params, body)   Call(callee, args)
```

The set of node classes *is* your language's semantic inventory: if a construct has no node, your language cannot mean it.

> **Watch out!** Students often confuse the **parse tree** with the **AST**. The parse tree is a record of the grammar derivation — it includes every intermediate nonterminal and every piece of punctuation. The AST keeps *only meaning-bearing* nodes. Parentheses disappear entirely (their effect lives in the tree shape), and long single-child chains like `expr → additive → multiplicative → primary → Num` collapse to a single `Num` node. If your AST looks like your grammar, it is probably not abstract enough.

**Worked example — tracing `1 + 2 * 3` from tokens to AST:**

**Step 1 — Tokens:**
```
NUM(1)  OP(+)  NUM(2)  OP(*)  NUM(3)
```

**Step 2 — Parse tree** (using a ladder grammar with separate `additive` and `multiplicative` levels):
```
expr
└─ additive
   ├─ multiplicative
   │  └─ primary → NUM(1)
   ├─ OP(+)
   └─ additive
      └─ multiplicative
         ├─ primary → NUM(2)
         ├─ OP(*)
         └─ multiplicative
            └─ primary → NUM(3)
```
The parse tree has 10+ nodes, most of them grammar scaffolding.

**Step 3 — AST** (scaffolding collapsed, precedence now encoded in tree shape):
```
BinOp('+')
├─ Num(1)
└─ BinOp('*')
   ├─ Num(2)
   └─ Num(3)
```
Only 5 nodes remain. The `*` is a child of `+`, which correctly encodes that multiplication binds tighter — `2 * 3` is evaluated first. No nonterminals, no parentheses, no grammar-level noise.

**Critical Thinking Questions (CTQs)**

> **CTQ 1.1** For the source `(2 + 3) * 4`, sketch both the full parse tree under the ladder grammar and the AST. Count nodes in each. What fraction of the parse-tree nodes was scaffolding (existed only to enforce precedence)?

> **CTQ 1.2** Parentheses appear nowhere in the AST, yet `(2 + 3) * 4` and `2 + 3 * 4` get different ASTs. Resolve the apparent paradox in two sentences.

> **CTQ 1.3** Unary `-` and binary `-` use the same character but deserve different node types. Argue why, from the perspective of the evaluator that will consume the tree.

---

## Model 1: Node Classes and the `pretty` Printer

*What problem does this solve?* Now that we know what an AST *is*, we need a concrete way to represent one in Python. This model shows how to define each node type as a dataclass (so fields have names, not just positions), and then how to *walk* the tree recursively with `pretty`. Walking a tree — visiting every node in order — is the one pattern you will use for everything: printing, evaluating, type-checking, compiling. Understand `pretty` here and the evaluator next week is trivial.

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

> **Watch out!** The `case _:` arm in `pretty` is a safety net, but in a real interpreter it is a bug waiting to happen. If you add a new node type (say, `FunDef`) but forget to add a corresponding `case FunDef(...):` arm, Python will silently fall through to `Unknown: ...` instead of raising an error. Every time you add a new AST node, immediately add a handler for it in *every* tree-walking function — `pretty`, `count_nodes`, `collect_vars`, `constant_fold`, and especially the evaluator.

---

## Model 2: Tree Statistics and Analysis

*What problem does this solve?* A tree walk does not have to produce output — it can also *compute* information about a program. This model shows three read-only analyses: counting nodes (useful for complexity budgets), measuring depth (tells you how deep the evaluator's call stack can get), and collecting all variable names (a primitive form of scope analysis). These same patterns — accumulate a count, accumulate a maximum, accumulate a set — recur constantly in real compilers.

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

*What problem does this solve?* Your earlier parser returned nested tuples like `('+', left, right)`. Tuples work, but they are fragile: you have to remember that index 0 is the operator, index 1 is the left child, and so on. A dataclass gives every field a *name*, making the tree self-documenting and letting Python's structural pattern matching work cleanly. The upgrade is literally one line per production: replace a tuple literal with a node constructor. Nothing else in the parser changes.

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

*What problem does this solve?* A language implementer does not just read the AST — they sometimes want to *rewrite* it into a simpler or faster equivalent before evaluation. Constant folding is the canonical first optimization: if both children of a `BinOp` are `Num` nodes, there is no reason to wait until runtime to compute the result. This model introduces the pattern of a tree *transformation*: a function that takes a node and returns a (possibly different) node, recursing on children. The same pattern underlies dead-code elimination, inlining, and virtually every compiler optimization you will study.

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

> **Watch out!** Constant folding is only safe for *pure* sub-expressions — ones with no side effects. It is tempting to fold `f() + 0` to `f()` because "adding zero does nothing," but that reasoning only applies when `f()` has no side effects. If `f()` prints to the screen or modifies a global, folding away the `+ 0` is correct *for the arithmetic* but changes the program's observable behavior in other ways. When in doubt, only fold sub-trees made entirely of `Num`, `Bool`, and `Str` nodes with no `Call` or `Var` nodes anywhere inside.

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

*What problem does this solve?* Going from source text to an AST is the job of the parser. But can you go the other way — from an AST back to valid source text? This is called *unparsing* (or pretty-printing), and it is crucial for testing: if you parse a string, unparse the tree, and re-parse the result, you should get an identical tree. This round-trip property is one of the most powerful automated checks you can write for a language implementation. It also raises a subtle challenge: the AST discards parentheses, so the unparsing pass must *re-insert* them only where operator precedence requires it — no more, no less.

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

# Part V: Expression Trees in Practice — Adapted Examples

These models adapt code from *Foundations of Computing* by Chuck Allison (Fresh Sources, Inc.), used under the [MIT License](https://github.com/chuckallison/foundations-of-computing/blob/main/LICENSE). The adapted example rewrites Allison's binary-tree traversal as a typed `ExprNode` dataclass, connecting preorder/inorder/postorder traversal directly to prefix/infix/postfix notation — the same connection your parser and evaluator rely on.

---

## Model 6: Prefix, Infix, and Postfix — Three Views of One Tree

An expression tree encodes *both* the values *and* the operator order, but different traversal orders produce different notation styles:
- **Preorder** (root → left → right): prefix / Polish notation — operator comes first
- **Inorder** (left → root → right): infix — operator is between operands (needs parentheses for unambiguity)
- **Postorder** (left → right → root): postfix / reverse Polish — operator comes last, used by stack machines

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
    """Preorder traversal → prefix (Polish) notation."""
    if node.is_leaf():
        return node.value
    return f"{node.value} {to_prefix(node.left)} {to_prefix(node.right)}"

def to_infix(node: ExprNode) -> str:
    """Inorder traversal → infix notation (with parentheses for clarity)."""
    if node.is_leaf():
        return node.value
    return f"({to_infix(node.left)} {node.value} {to_infix(node.right)})"

def to_postfix(node: ExprNode) -> str:
    """Postorder traversal → postfix (Reverse Polish) notation."""
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

# Build the tree for  1 + 2 * 3   (multiplication binds tighter → * is deeper)
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

**CTQ M6.1** The two trees above represent the same tokens in a different order — `(1+2)*3` vs `1+2*3`. What physical property of the tree (depth, root label, or shape) encodes operator precedence? Trace `eval_tree(tree2)` step by step to confirm that multiplication is evaluated before addition.

**CTQ M6.2** Postfix notation is used by stack machines (RPN calculators, the JVM bytecode verifier). Write a `eval_postfix(tokens: list[str]) -> float` function that evaluates a postfix expression using only a stack. Verify it gives the same result as `eval_tree` for both trees above.

**CTQ M6.3** The `to_infix` function adds parentheses around every subexpression. This is safe but verbose — `((1 + 2) * 3)` has more parentheses than needed. Modify `to_infix` to include parentheses only where necessary (i.e., only when a child's operator has lower precedence than the parent's). Test on `1 + 2 * 3` to confirm it produces `1 + 2 * 3` not `(1 + (2 * 3))`.

---

## Practice — Allison Readings 6.1 and 6.2

[[MC]]
A postorder traversal of an expression tree visits nodes in which order?
- ( ) Root, then left subtree, then right subtree
- ( ) Left subtree, then root, then right subtree
- (x) Left subtree, then right subtree, then root
- ( ) Right subtree, then left subtree, then root

[[MC]]
The postfix expression `3 4 + 5 *` evaluates to:
- ( ) 23
- (x) 35
- ( ) 17
- ( ) 32

[[MC]]
In an expression tree for `a + b * c`, the root node contains:
- ( ) `a`
- ( ) `*`
- (x) `+`
- ( ) `b`

1. *Tree construction.* Build `ExprNode` trees for: (a) `2 + 3 * 4`, (b) `(2 + 3) * 4`, (c) `a - b + c` (left-associative). For each, print all three notations and the numeric value (using `a=2, b=3, c=4`).

2. *Postfix evaluator.* Implement `eval_postfix(tokens)` using a stack: push numbers, and on each operator pop two operands, apply the operation, and push the result. Verify it matches `eval_tree` for both trees in Model 6.

3. *Parse prefix.* Write `from_prefix(tokens: list[str]) -> ExprNode` that reconstructs a tree from a prefix token list (recursively: if the next token is an operator, read two subtrees; otherwise it's a leaf). Test it by doing the round-trip `from_prefix(to_prefix(tree).split()) == tree` for both trees in Model 6.

4. *Depth and balance.* Write `tree_depth(node)` and `count_leaves(node)`. For a perfectly balanced binary tree of depth $d$, what is the relationship between `count_leaves` and $d$? Verify with a tree of depth 3.

5. *AST for your language.* Using the `ExprNode` structure as a template, design node classes for all constructs in your team's language (not just arithmetic). Draw the tree for a `while` loop with a compound body. What fields does each node type need?

---

## Reflection Prompt

The AST is the third representation of the same program (characters → tokens → tree), each one closer to meaning and farther from what the programmer typed. What is gained and what is honestly lost at each translation? The tree is now the interface between the front end (lexer, parser) and the back end (evaluator, optimizer, compiler): what does this separation buy you as a language implementer?

---

## Further Reading

- **"Crafting Interpreters"** — Robert Nystrom, "Representing Code": our exact path, visualized
- **Python `ast` module** — `ast.dump(ast.parse("2+3*4"))` — meet a production AST
- **Douglas Thain. "Introduction to Compilers and Language Design"** — Chapter 5
- **"Engineering a Compiler"** — Cooper & Torczon, Chapter 5: AST construction in a real compiler

## Going Deeper: Code Structure: Expressions and Conditionals

> **Think about city zoning for a moment.** A well-planned city separates residential neighborhoods from industrial districts from commercial zones — not because mixing them is physically impossible, but because keeping related things together prevents conflicts and makes the city easier to navigate. Programming languages do the same thing with *modules*, *namespaces*, and *packages*. The way a language carves up code into named, bounded units reflects its philosophy about separation of concerns: who owns what, what is visible to whom, and how names from different places coexist without colliding. In this activity, you will explore how expression structure — the building blocks *inside* those units — is designed in functional languages.

#### Learning Goals

By the end of this activity, you will be able to:

- Distinguish expressions from statements and explain the significance of treating `if` and `let` as expressions rather than statements
- Implement `let`-binding as an expression form and trace how it extends the environment for the scope of its body
- Construct a small expression evaluator that handles arithmetic, conditionals, and local variable binding
- Compare strict (eager) and short-circuit (lazy) evaluation of boolean expressions and identify where each is semantically necessary
- Analyze how sequencing is encoded as a language construct and explain its relationship to side effects

CS374 — Principles of Programming Languages | Week 7

Reference: PLAI (Programming Languages: Application and Interpretation) Ch. 7

> **Before You Begin**
>
> This activity assumes you are comfortable with:
>
> - Writing and calling Python functions, including lambda expressions
> - Basic Python data structures (lists, dicts) and comprehensions
> - The concept of *scope* — that a variable defined inside a function is not visible outside it
> - Python's `dataclass` decorator (used in Models 4–5); a quick review: `@dataclass` auto-generates `__init__` from field annotations
>
> You do **not** need prior exposure to Scheme or Haskell, though the activity will introduce small snippets of each. If you have never seen Scheme syntax before, note that `(f a b)` means "call function `f` with arguments `a` and `b`" — the function name comes first, inside the parentheses.

---

#### Directions and Group Roles

This is a POGIL (Process Oriented Guided Inquiry Learning) activity. Work in groups of 3–4. Each person takes a role:

- **Facilitator**: Keeps the group on task, ensures everyone participates, and watches the clock.
- **Recorder**: Writes down the group's answers and keeps notes for the group.
- **Reporter**: Prepares to share the group's findings with the class when called upon.
- **Reflector**: Monitors group dynamics, notes what is working well, and identifies any confusion.

Roles may rotate between activities. Everyone should contribute to the critical thinking questions, even if only one person records the answers.

**Learning Goals for This Activity:**

- Distinguish between *expressions* (which produce a value) and *statements* (which produce side effects)
- Understand `let` as an expression and how it models local variable binding
- Explore sequencing as a language construct
- Build a small expression evaluator with conditionals and let bindings
- Understand short-circuit (lazy) evaluation vs. strict evaluation

---

#### Model 1: Expressions vs Statements

*Intuition:* Imagine a vending machine. You put in money (input), press a button (operation), and get a snack (value) — the whole interaction *produces something*. That is an expression. Now imagine a light switch: you flip it (action) and a side effect occurs (light changes), but the switch itself does not hand you a value. That is a statement. Most languages mix both, but functional languages lean heavily toward the vending-machine model — nearly everything hands back a value.

> **Watch out!** Python's `if` is a *statement* by default, so you cannot write `x = if cond: 5 else 10` directly. Python provides the *ternary expression* `5 if cond else 10` as a separate syntax for cases where you need an expression. These are two distinct constructs in Python, but they are unified into one `if`-expression in Haskell and Scheme. Do not mix them up when answering the critical thinking questions.

In programming language theory, a key distinction is between **expressions** and **statements**.

- An **expression** is a syntactic form that *evaluates to a value*. For example, `3 + 4` evaluates to `7`.
- A **statement** is a syntactic form that *performs an action* (a side effect) and does not necessarily produce a value. For example, a `print` call or an assignment statement.

In many functional languages (Haskell, Scheme, ML), `if` is an **expression** — it always produces a value. In Python, `if` is a **statement** by default, although Python provides a *conditional expression* (the ternary operator) as well. Python 3.8+ also introduced the walrus operator (`:=`) as a limited form of assignment expression.

The code below demonstrates these distinctions in Python and shows how we can simulate a strict if-expression.

```python
# Python: if-expression (ternary)
x = 10
label = "positive" if x > 0 else "non-positive"
print(f"x={x}, label={label}")

# Demonstrate: assignment is a statement (not an expression)
# In Python 3.8+, the walrus operator := creates assignment expressions
import re
text = "Hello, world! My number is 42."
if m := re.search(r'\d+', text):
    print(f"Found number: {m.group()}")
else:
    print("No number found")

# In a pure expression language, everything has a value
# Simulate: evaluate a conditional as an expression
def iif(cond, then_val, else_val):
    """Strict if-expression (both branches always evaluated)."""
    return then_val if cond else else_val

result = iif(5 > 3, "yes", "no")
print(f"iif result: {result}")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

##### Critical Thinking Questions

1. What is the difference between an expression and a statement? Give one example of each from the code above.

2. Could every statement be rewritten as an expression? Consider an assignment statement like `x = 5`. What would it mean to treat that as an expression (what value would it produce)? What language does exactly this?

3. What are the tradeoffs of treating `if` as an expression (as in Haskell) versus treating it as a statement (as in Java)? Think about code clarity, composability, and how `if` can be nested inside other expressions.

4. The `iif` function above is called a *strict* if-expression. What does "evaluation order" mean in this context, and how does `iif` differ from Python's built-in ternary `x if cond else y` in terms of when each branch is evaluated?

---

#### Model 2: Let Expressions and Local Binding

*Intuition:* Think of a math proof that says "Let x = 5. Then x + 3 = 8." The word "let" introduces a local name that is only meaningful for the lines that follow — once the proof moves on, `x` is gone. Functional `let` works exactly the same way: it binds a name to a value for the duration of one sub-expression (the *body*), and nowhere else. This is fundamentally different from Python assignment, which drops the name into the surrounding function's scope and leaves it there.

> **Watch out!** The Python simulation uses a `lambda` as the `body` argument. This works, but it hides an important subtlety: the lambda's *parameters* act as the bound variables, not as normal function arguments. When you see `let({"x": 5}, lambda x: x + 1)`, read it as "in the scope where x = 5, evaluate x + 1" — not as "call a function with argument 5."

In functional languages like Scheme and Haskell, `let` is an **expression** that introduces local variable bindings. For example, in Scheme:

```
(let ((x 5) (y 3)) (+ x y))
```

This evaluates to `8`: `x` is bound to `5`, `y` is bound to `3`, and the body `(+ x y)` is evaluated in that local scope.

In Python, local binding is accomplished through assignment statements, which are not expressions. However, we can *simulate* the semantics of `let` using a higher-order function to better understand what `let` means as a language construct.

An important distinction: `let` (non-recursive) evaluates all binding values in the *outer* environment, while `letrec` (recursive let) allows the bindings to refer to each other, which is necessary for mutually recursive definitions.

```python
# In Scheme: (let ((x 5) (y 3)) (+ x y))
# Python doesn't have let as an expression, but we can simulate it:

def let(bindings, body):
    """Simulate a let expression: evaluate body with given bindings."""
    return body(**bindings)

result = let(
    {"x": 5, "y": 3},
    lambda x, y: x + y
)
print(f"let x=5, y=3 in x+y = {result}")

# Nested let:
result2 = let(
    {"a": 10},
    lambda a: let(
        {"b": a * 2},
        lambda b: b + 1
    )
)
print(f"let a=10 in let b=a*2 in b+1 = {result2}")

# Python's walrus operator as a limited let-expression:
# (Python 3.8+)
data = [1, 5, 3, 8, 2, 9, 4]
result3 = [y for x in data if (y := x * 2) > 8]
print(f"doubled values > 8: {result3}")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

##### Critical Thinking Questions

1. Why is `let` useful as an expression rather than a statement? How does treating `let` as an expression affect composability — can you nest `let` inside another expression?

2. How does the `let` simulation above capture the semantics of `let` in functional languages? What role does the `body` lambda play? What is the environment in which `body` is evaluated?

3. What is the difference between `let` (non-recursive) and `letrec` (recursive)? Give an example of a definition that requires `letrec` but cannot be expressed with plain `let`. Hint: think about a recursive function.

4. How does Python's variable scoping (function-local scope, closures) differ from Scheme's `let` scoping? In Python, does a variable defined inside a function leak out? How does this compare to a `let` binding in Scheme?

---

#### Model 3: Sequencing and Begin

*Intuition:* A recipe says "first preheat the oven, then mix the batter, then bake." The *order* matters, even if each step has no meaningful return value on its own. In a pure expression language, "doing things in order" requires an explicit construct because expressions do not inherently sequence — they just produce values. Scheme's `begin` is that explicit sequencing construct: it evaluates expressions one after another and hands back whatever the last one produces.

In purely functional languages, there are no statements and no side effects — every construct is an expression. But even functional languages need to do things in *order*, particularly when dealing with I/O or mutable state.

The `begin` form in Scheme sequences expressions and returns the value of the *last* one:

```
(begin
  (display "step 1")
  (display "step 2")
  42)   ; returns 42
```

Python's sequence of statements is the natural analog, but it is not an expression — you can't embed a sequence of statements inside a larger expression. The Python `begin` simulation below models Scheme's behavior explicitly.

```python
# Simulate Scheme's (begin e1 e2 ... en) — returns last value
def begin(*exprs):
    """Evaluate expressions in order, return the last value."""
    result = None
    for expr in exprs:
        result = expr() if callable(expr) else expr
    return result

counter = [0]

def increment():
    counter[0] += 1
    return counter[0]

value = begin(
    lambda: print("step 1: incrementing"),
    increment,
    lambda: print(f"step 2: counter is now {counter[0]}"),
    increment,
    lambda: print(f"step 3: counter is now {counter[0]}"),
    increment,
)
print(f"Final value: {value}")

# Python's sequence of statements IS sequencing, but not as an expression
# Show that list comprehensions are essentially sequenced expressions:
squares = [x**2 for x in range(1, 6)]
print(f"Squares: {squares}")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

##### Critical Thinking Questions

1. What does "sequencing" mean in a programming language? Why do we need it even in a language that is primarily expression-based?

2. Why does `begin` return the *last* value rather than the first? In what situations might it be useful to have a form that sequences expressions but discards all values except the last?

3. In Python, how is sequencing expressed differently from a functional language like Scheme? Is Python's sequencing (a block of statements) usable inside an expression? Give an example of where this limitation is noticeable.

4. What would happen if a language had no sequencing at all — only pure expressions with no side effects? What kinds of programs would be impossible or very difficult to write? What kinds of programs might actually be *easier* to reason about?

---

#### Model 4: Building an Expression Evaluator

*Intuition:* An evaluator is a program that reads a tree of expression nodes and collapses it into a single value — the way a calculator reduces `(3 + 4) * 2` to `14` step by step. The key ingredient is the *environment*: a dictionary mapping variable names to their current values. When you encounter a `Var` node, you look its name up in the environment. When you encounter a `LetExpr`, you extend the environment with a new binding for the duration of the body. The environment grows as you go *in* to nested expressions and shrinks (is discarded) as you come *out*.

> **Watch out!** In `eval_expr`, the `If` node evaluates its condition and then evaluates **only one branch** — the chosen one. This is different from how `BinOp` works: `BinOp` evaluates *both* sub-expressions before applying the operator. Keep this asymmetry in mind for the critical thinking questions about strict vs. lazy evaluation.

PLAI Ch. 7 focuses on building an interpreter for a language with conditionals and let bindings. In this model, we implement a small evaluator for an expression language that includes arithmetic, booleans, conditionals (`If`), and local bindings (`LetExpr`).

This interpreter models the *substitution model*: when we encounter a `LetExpr`, we extend the environment with the new binding rather than substituting directly. This is a key concept in interpreter design.

Notice that `If` only evaluates **one** branch — the correct branch based on the condition. This is called *lazy* or *call-by-need* conditional evaluation.

```python
from dataclasses import dataclass
from typing import Any

@dataclass
class Num:
    value: float

@dataclass
class Bool:
    value: bool

@dataclass
class BinOp:
    op: str    # '+', '-', '*', '/', '<', '>', '==', 'and', 'or'
    left: Any
    right: Any

@dataclass
class If:
    cond: Any
    then_expr: Any
    else_expr: Any

@dataclass
class LetExpr:
    name: str
    value_expr: Any
    body_expr: Any

@dataclass
class Var:
    name: str

def eval_expr(expr, env: dict) -> Any:
    if isinstance(expr, Num):
        return expr.value
    if isinstance(expr, Bool):
        return expr.value
    if isinstance(expr, Var):
        if expr.name not in env:
            raise NameError(f"Undefined variable: {expr.name}")
        return env[expr.name]
    if isinstance(expr, BinOp):
        l = eval_expr(expr.left, env)
        r = eval_expr(expr.right, env)
        ops = {
            '+': l + r, '-': l - r, '*': l * r,
            '/': l / r if r != 0 else (_ for _ in ()).throw(ZeroDivisionError()),
            '<': l < r, '>': l > r, '==': l == r,
            'and': l and r, 'or': l or r,
        }
        return ops[expr.op]
    if isinstance(expr, If):
        cond_val = eval_expr(expr.cond, env)
        if cond_val:
            return eval_expr(expr.then_expr, env)
        else:
            return eval_expr(expr.else_expr, env)
    if isinstance(expr, LetExpr):
        val = eval_expr(expr.value_expr, env)
        new_env = {**env, expr.name: val}  # extend env
        return eval_expr(expr.body_expr, new_env)
    raise ValueError(f"Unknown expression type: {type(expr)}")

# Test: if x > 5 then x * 2 else x + 1
# with x = 7
program = If(
    BinOp('>', Var('x'), Num(5)),
    BinOp('*', Var('x'), Num(2)),
    BinOp('+', Var('x'), Num(1))
)
env = {"x": 7}
result = eval_expr(program, env)
print(f"if x>5 then x*2 else x+1 where x=7 = {result}")

# Test: let y = x * 2 in if y > 10 then y else 0
program2 = LetExpr(
    "y",
    BinOp('*', Var('x'), Num(2)),
    If(BinOp('>', Var('y'), Num(10)), Var('y'), Num(0))
)
print(f"let y=x*2 in if y>10 then y else 0 where x=7: {eval_expr(program2, env)}")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

##### Critical Thinking Questions

1. Why does the `If` node in `eval_expr` only evaluate *one* of `then_expr` or `else_expr`? What would go wrong if both branches were always evaluated? Give a concrete example involving a side effect or an error.

2. What is "short-circuit evaluation"? How does it relate to the behavior of `If` in this evaluator? Is the `BinOp` for `'and'` in this evaluator short-circuit or strict? How can you tell?

3. In `LetExpr`, we create a new env dict with `{**env, expr.name: val}` rather than modifying the existing one. Why is this important? What problem would arise if we wrote `env[expr.name] = val` instead, especially in the presence of nested let expressions?

4. What would happen if both branches of `If` were always evaluated (strict semantics)? This is called *strict conditional evaluation*. Name one advantage and one disadvantage of strict evaluation compared to lazy conditional evaluation.

---

#### Model 5: Short-Circuit Evaluation and Lazy Conditionals

*Intuition:* Imagine a security guard who checks two ID requirements: "Must be over 18 AND must have a valid badge." If the visitor is clearly 10 years old, the guard does not bother asking for the badge — the first condition already determines the outcome. Python's `and`/`or` operators work the same way: they stop evaluating as soon as the result is certain. This is called *short-circuit* (or *lazy*) evaluation, and it is not just a performance trick — it is what makes patterns like `x is not None and x.value > 0` safe, because the right side is only reached when `x` is guaranteed non-None.

We saw in Model 4 that the `If` node only evaluates one branch. Python's `and` and `or` operators exhibit similar behavior: they use **short-circuit evaluation** (also called *lazy* or *non-strict* evaluation).

- `A and B`: if `A` is `False`, Python does **not** evaluate `B`.
- `A or B`: if `A` is `True`, Python does **not** evaluate `B`.

This is crucial for correctness (avoiding errors) and performance (avoiding expensive computations). The code below demonstrates short-circuit evaluation and contrasts it with strict evaluation, then shows how to build a lazy conditional using thunks (zero-argument functions that delay evaluation).

```python
# Short-circuit evaluation
def safe_divide(a, b):
    return a / b if b != 0 else None

# Without short-circuit, this would call safe_divide(10, 0) even when False
x = 0
# Python's 'and' is short-circuit: doesn't evaluate right side if left is False
result1 = x != 0 and (10 / x > 1)
print(f"x!=0 and 10/x>1 = {result1}")  # False, no ZeroDivisionError

# Python's 'or' is short-circuit too
def expensive_computation():
    print("  (expensive computation called)")
    return 42

cached = None
value = cached or expensive_computation()
print(f"cached or expensive: {value}")

# Simulate strict vs lazy evaluation in our evaluator
import time

def make_lazy(thunk):
    """Wrap a computation to be lazy (only evaluate when called)."""
    computed = [False]
    result = [None]
    def force():
        if not computed[0]:
            result[0] = thunk()
            computed[0] = True
        return result[0]
    return force

def lazy_if(cond, then_thunk, else_thunk):
    """Lazy conditional: only evaluates the chosen branch."""
    return then_thunk() if cond else else_thunk()

# Demonstrate: lazy if avoids computing both branches
print("\nLazy if demonstration:")
answer = lazy_if(
    True,
    lambda: (print("  evaluating THEN"), 42)[1],
    lambda: (print("  evaluating ELSE"), 0)[1]
)
print(f"Result: {answer}")  # Only prints "evaluating THEN"
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

##### Critical Thinking Questions

1. What is short-circuit evaluation and why is it important? Give an example from the code above where short-circuit evaluation prevents a runtime error that strict evaluation would cause.

2. Give an original example (not from the code above) where short-circuit evaluation of `or` is useful for avoiding an expensive computation. Describe what the "expensive" part would be and why it is safe to skip.

3. What is the difference between "lazy" and "strict" conditional evaluation? In `lazy_if`, how do lambda expressions (thunks) delay evaluation until the branch is chosen? What is the overhead cost of using thunks?

4. How does Python's `and`/`or` short-circuiting relate to the `If` node in the evaluator from Model 4? Are they handling laziness in the same way? What is the key difference in how Python implements short-circuiting versus how `lazy_if` implements it above?

---

#### Multiple Choice

**Question 1:** In a functional language where `if` is an expression, what must be true?

[[MC]]
- [( )] Only the condition is evaluated; neither branch is evaluated until explicitly called
- [(X)] Both branches exist syntactically, but only one is evaluated based on the condition
- [( )] Both branches are always evaluated eagerly, and the result is selected after
- [( )] The condition and both branches are always evaluated to check for errors

---

**Question 2:** In Scheme, `let` binds all variables simultaneously using the *outer* environment. `letrec` allows bindings to refer to each other. Which of the following **requires** `letrec` and cannot be expressed with plain `let`?

[[MC]]
- [( )] `(let ((x 1) (y 2)) (+ x y))`
- [( )] `(let ((x 5)) (let ((y x)) y))`
- [(X)] `(letrec ((even? (lambda (n) (if (= n 0) #t (odd? (- n 1))))) (odd? (lambda (n) (if (= n 0) #f (even? (- n 1)))))) (even? 4))`
- [( )] `(let ((f (lambda (x) (* x 2)))) (f 5))`

---

**Question 3:** Consider the `BinOp` case in the expression evaluator from Model 4. Both `eval_expr(expr.left, env)` and `eval_expr(expr.right, env)` are called before performing the operation. What does this mean about the evaluator's strategy for `BinOp`?

[[MC]]
- [( )] It uses lazy evaluation — operands are evaluated only when needed
- [(X)] It uses strict (eager) evaluation — both operands are always evaluated before the operation
- [( )] It uses short-circuit evaluation — the right operand may not be evaluated
- [( )] It uses call-by-name — operands are substituted unevaluated into the operation

---

**Question 4:** Python's `or` operator short-circuits. Given `result = f() or g()`, when is `g()` **not** called?

[[MC]]
- [( )] When `g()` would raise an exception
- [( )] When both `f()` and `g()` return `True`
- [(X)] When `f()` returns a truthy value
- [( )] When `f()` returns `False` or `None`

---

#### Exercises

**Exercise 1: While Loop as an Expression**

Add a `While` loop to the expression evaluator from Model 4. Define a new dataclass `WhileExpr(cond, body)`. The evaluator should execute `body` repeatedly as long as `cond` evaluates to `True`, and return the **number of iterations** performed as its value. Add it to `eval_expr` and test it with a small example (e.g., count from 1 to 5 using a mutable variable in the environment).

*Hint:* You will need to allow the environment to be updated during the loop body, which means reconsidering the immutability of `env`. Discuss with your group how to handle this while keeping the evaluator as clean as possible.

**Exercise 2: Not and Cond**

Extend the expression evaluator with two new constructs:

- `NotExpr(expr)` — a unary operator that negates a boolean expression.
- `CondExpr(clauses, else_expr)` — a multi-branch conditional, where `clauses` is a list of `(condition, result)` pairs. It evaluates each condition in order and returns the result of the first truthy one; if none match, it evaluates `else_expr`.

Add both to `eval_expr` and write a test that uses `CondExpr` to classify a number as "negative", "zero", or "positive".

**Exercise 3: Sequential Let (let*)**

In Scheme, `let*` allows each binding to see the bindings that came before it (sequential binding). For example:

```
(let* ((x 2) (y (* x 3))) y)  ; y = 6, because y sees x
```

Write a Python function `let_star(bindings_list, body)` where `bindings_list` is a list of `(name, value)` pairs evaluated sequentially (each sees the previous ones) and `body` is a lambda taking keyword arguments for all bindings. Test it with at least two bindings where the second depends on the first.

**Exercise 4: Short-Circuit BinOp in the Evaluator**

The `BinOp` case in the evaluator from Model 4 always evaluates both operands before performing the operation. This means `'and'` and `'or'` are strict, not short-circuit.

Modify `eval_expr` so that `BinOp` with `op='and'` and `op='or'` use short-circuit evaluation: for `'and'`, if the left side is `False`, do not evaluate the right side; for `'or'`, if the left side is `True`, do not evaluate the right side.

Write a test that demonstrates the difference — construct an expression where strict evaluation would raise a `ZeroDivisionError` but lazy/short-circuit evaluation succeeds.

---

#### Reflection Prompt

In Python, `if` is a statement; in Haskell, `if` is an expression. What practical difference does this make when writing code? Write 3–4 sentences considering: where you can place an `if`, how it affects composability (e.g., can you use `if` inside a list comprehension, as a function argument, or inside another expression directly?), and whether you think expression-based `if` or statement-based `if` leads to clearer code in typical programming tasks.

---

#### Further Reading

- **PLAI Ch. 7** — Conditionals and Bindings: the primary reference for this activity. Covers how interpreters handle `if` and `let` at the semantic level.
- **"Structure and Interpretation of Computer Programs" (SICP) Ch. 1.1** — Expressions: introduces the expression-based model of computation in Scheme and motivates why everything being an expression simplifies reasoning.
- **Python PEP 572** — Assignment Expressions (the walrus operator `:=`): the design rationale behind adding a limited expression-form assignment to Python, including discussion of the tradeoffs and rejected alternatives.
- **Wadler, "Theorems for Free" (1989)** — A research paper explaining why purely expression-based (purely functional) languages have desirable mathematical properties, including the ability to reason about programs using equational reasoning.

## Going Deeper: From Interpreter to Compiler: Code Generation and Transpilation

Your tree-walking interpreter already does the hard work — it understands the meaning of every AST node. A compiler does the same traversal but instead of computing a value, it writes down instructions for someone else to execute later. The difference is not intelligence but timing: an interpreter acts now, a compiler acts once so that execution can happen many times fast. This activity builds three backends on top of the same AST your interpreter already handles, making that timing difference concrete.

#### Learning Goals

By the end of this activity, you will be able to:

- Explain the architectural difference between a tree-walking interpreter, a transpiler, and a bytecode compiler, and identify which pipeline stages each shares and where they diverge
- Implement a Visitor-pattern AST traversal that emits syntactically correct Python and JavaScript from a Mini-language AST, including correct operator precedence in the output
- Design and implement a stack-machine instruction set for a simple expression language, write a compiler that emits those instructions from an AST, and trace instruction-by-instruction execution through a virtual machine
- Run an end-to-end equivalence test confirming that the interpreter, both transpilers, and the stack machine produce identical output for the same Mini-language program

> **Before You Begin:** This activity assumes you can:
> - Explain what an abstract syntax tree (AST) is and describe the node types your course interpreter already handles
> - Write a Python class with methods that dispatch based on the type of an argument
> - Describe what a call stack is and what it means for a value to be "on top of the stack"
>
> If any of these feel shaky, review them first.

*"The difference between an interpreter and a compiler is not how smart they are about the language — it is when they do their work."*

Your tree-walking interpreter evaluates an AST **at runtime**: it visits each node and immediately computes a value. A **compiler** walks the same AST but, instead of computing values, **emits instructions** — for a virtual machine, a real CPU, or another programming language. A **transpiler** (source-to-source compiler) emits valid code in a different high-level language. All three share the same frontend (lexer, parser, AST builder); they diverge only in what the AST traversal produces.

In this module we build the complete bridge: starting from the interpreter you have already built, we add a **code generator** that emits Python bytecode (via a virtual stack machine), then a **transpiler** that emits valid JavaScript and valid Haskell. You will be able to run programs in your language by transpiling them — without writing a new frontend.

---

#### 0. Setup

```python
# We assume the mini-language interpreter from the course pipeline.
# This module builds on top of the AST defined there.
# Define a minimal AST for illustration:

class Num:
    def __init__(self, value): self.value = value
class BinOp:
    def __init__(self, op, left, right): self.op = op; self.left = left; self.right = right
class Var:
    def __init__(self, name): self.name = name
class Let:
    def __init__(self, name, value, body): self.name = name; self.value = value; self.body = body
class IfExpr:
    def __init__(self, cond, then_, else_): self.cond = cond; self.then_ = then_; self.else_ = else_
class FuncDef:
    def __init__(self, param, body): self.param = param; self.body = body
class Call:
    def __init__(self, func, arg): self.func = func; self.arg = arg

print("AST nodes loaded.")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

---

### Part I: The Visitor Pattern

#### 1. Why We Need the Visitor

Imagine you need to add a type-checker, an optimizer, and a pretty-printer to your interpreter — all traversing the same AST. Without the Visitor pattern, you end up with three copies of the same `if isinstance(...)` dispatch logic, and every new AST node type means updating all three copies. The Visitor pattern solves this by making the traversal a single place and making each "what to do at each node" a separate, swappable object.

Your tree-walking interpreter is a set of `if isinstance(node, ...)` branches inside a single `evaluate` function. This works, but as soon as you want to **also** compile, and **also** type-check, and **also** transpile the same AST, you face a choice:

- Add a second `emit_python` function with the same `if isinstance` structure (code duplication)
- Bundle evaluate/emit/typecheck methods inside the AST node classes (breaks separation of concerns)
- Use the **Visitor pattern**: define a `Visitor` interface where each node class calls back into the visitor

The Visitor pattern separates the **what to do** (the visitor) from the **what to visit** (the AST). Adding a new operation (e.g., a type checker, an optimizer, a pretty-printer) requires adding a new visitor class — not modifying the AST.

```python
class Num:
    def __init__(self, value): self.value = value
class BinOp:
    def __init__(self, op, left, right): self.op = op; self.left = left; self.right = right
class Var:
    def __init__(self, name): self.name = name
class Let:
    def __init__(self, name, value, body): self.name = name; self.value = value; self.body = body
class IfExpr:
    def __init__(self, cond, then_, else_): self.cond = cond; self.then_ = then_; self.else_ = else_
class FuncDef:
    def __init__(self, param, body): self.param = param; self.body = body
class Call:
    def __init__(self, func, arg): self.func = func; self.arg = arg

# Visitor base class
class Visitor:
    def visit(self, node):
        method_name = f"visit_{type(node).__name__}"
        method = getattr(self, method_name, self.generic_visit)
        return method(node)

    def generic_visit(self, node):
        raise NotImplementedError(f"No visitor for {type(node).__name__}")

# Interpreter as a Visitor
class Interpreter(Visitor):
    def __init__(self):
        self.env = {}

    def visit_Num(self, node):
        return node.value

    def visit_BinOp(self, node):
        left  = self.visit(node.left)
        right = self.visit(node.right)
        ops   = {'+': lambda a, b: a + b,
                 '-': lambda a, b: a - b,
                 '*': lambda a, b: a * b,
                 '/': lambda a, b: a / b if b != 0 else (_ for _ in ()).throw(ZeroDivisionError("div by zero"))}
        return ops[node.op](left, right)

    def visit_Var(self, node):
        if node.name not in self.env:
            raise NameError(f"[interp] Undefined variable: {node.name}")
        return self.env[node.name]

    def visit_Let(self, node):
        val = self.visit(node.value)
        old_env = dict(self.env)
        self.env[node.name] = val
        result = self.visit(node.body)
        self.env = old_env
        return result

    def visit_IfExpr(self, node):
        cond = self.visit(node.cond)
        return self.visit(node.then_) if cond else self.visit(node.else_)

# Test
interp = Interpreter()
# let x = 3 in x * 2 + 1
ast = Let("x", Num(3), BinOp("+", BinOp("*", Var("x"), Num(2)), Num(1)))
print("Interpreter result:", interp.visit(ast))   # 7
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

> **Watch out!** `getattr(self, method_name, self.generic_visit)` dispatches to a method named `visit_ClassName`. This means the method name is determined by the Python class name of the AST node, not by any tag you set. If you rename `BinOp` to `BinaryOperation`, the dispatch will break silently — `generic_visit` will be called instead, likely raising a confusing error. Always keep AST class names stable once you build visitors over them.

---

### Part II: Transpiler to Python

#### 2. The Python Transpiler

A transpiler is just a visitor that accumulates strings instead of values. Every `visit_*` method returns a fragment of source code, and the fragments compose exactly the way the original AST composes. This is why well-structured ASTs produce clean, readable transpiled output — the structure of the AST maps directly to the structure of the emitted code.

A transpiler is a visitor that **returns strings** instead of values.

A transpiler is a visitor that **returns strings** instead of values. Each `visit_*` method returns a Python expression string. The result of visiting the root is a complete Python expression (or program).

```python
class Num:
    def __init__(self, value): self.value = value
class BinOp:
    def __init__(self, op, left, right): self.op = op; self.left = left; self.right = right
class Var:
    def __init__(self, name): self.name = name
class Let:
    def __init__(self, name, value, body): self.name = name; self.value = value; self.body = body
class IfExpr:
    def __init__(self, cond, then_, else_): self.cond = cond; self.then_ = then_; self.else_ = else_
class FuncDef:
    def __init__(self, param, body): self.param = param; self.body = body
class Call:
    def __init__(self, func, arg): self.func = func; self.arg = arg

class Visitor:
    def visit(self, node):
        method_name = f"visit_{type(node).__name__}"
        method = getattr(self, method_name, self.generic_visit)
        return method(node)
    def generic_visit(self, node):
        raise NotImplementedError(f"No visitor for {type(node).__name__}")

ast = Let("x", Num(3), BinOp("+", BinOp("*", Var("x"), Num(2)), Num(1)))

class PythonTranspiler(Visitor):
    """Transpiles our mini-language AST to Python source code."""

    def __init__(self):
        self._indent = 0

    def visit_Num(self, node):
        return str(node.value)

    def visit_BinOp(self, node):
        left  = self.visit(node.left)
        right = self.visit(node.right)
        return f"({left} {node.op} {right})"

    def visit_Var(self, node):
        return node.name

    def visit_Let(self, node):
        # let x = e in body  ->  (lambda x: body)(e)
        val  = self.visit(node.value)
        body = self.visit(node.body)
        return f"(lambda {node.name}: {body})({val})"

    def visit_IfExpr(self, node):
        cond  = self.visit(node.cond)
        then_ = self.visit(node.then_)
        else_ = self.visit(node.else_)
        return f"({then_} if {cond} else {else_})"

    def visit_FuncDef(self, node):
        body = self.visit(node.body)
        return f"(lambda {node.param}: {body})"

    def visit_Call(self, node):
        func = self.visit(node.func)
        arg  = self.visit(node.arg)
        return f"{func}({arg})"

# Transpile and execute
py_trans = PythonTranspiler()
py_code  = py_trans.visit(ast)
print("Python code:", py_code)
result   = eval(py_code)
print("Evaluated: ", result)   # should be 7
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

---

#### 3. The JavaScript Transpiler

The JavaScript transpiler demonstrates the key insight: the AST structure is language-neutral, but target-language quirks (like JavaScript's ternary operator `?:` for `if` expressions, or the need for `Math.trunc` for integer division) must be encoded per-target. Each new target language is a new visitor — no changes to the AST or the frontend.

> **Watch out!** JavaScript's `/` operator always returns a floating-point result, unlike Python's `//` (integer division). Our `Let` node uses `(lambda x: body)(value)` in Python but `((x) => body)(value)` in JavaScript. These look similar but behave differently for closures in edge cases — always test transpiler output with the target language's actual runtime.

The same AST, same visitor structure, different target language:

```python
class Num:
    def __init__(self, value): self.value = value
class BinOp:
    def __init__(self, op, left, right): self.op = op; self.left = left; self.right = right
class Var:
    def __init__(self, name): self.name = name
class Let:
    def __init__(self, name, value, body): self.name = name; self.value = value; self.body = body
class IfExpr:
    def __init__(self, cond, then_, else_): self.cond = cond; self.then_ = then_; self.else_ = else_
class FuncDef:
    def __init__(self, param, body): self.param = param; self.body = body
class Call:
    def __init__(self, func, arg): self.func = func; self.arg = arg

class Visitor:
    def visit(self, node):
        method_name = f"visit_{type(node).__name__}"
        method = getattr(self, method_name, self.generic_visit)
        return method(node)
    def generic_visit(self, node):
        raise NotImplementedError(f"No visitor for {type(node).__name__}")

ast = Let("x", Num(3), BinOp("+", BinOp("*", Var("x"), Num(2)), Num(1)))

class JavaScriptTranspiler(Visitor):
    """Transpiles our mini-language AST to JavaScript source code."""

    def visit_Num(self, node):
        return str(node.value)

    def visit_BinOp(self, node):
        left  = self.visit(node.left)
        right = self.visit(node.right)
        # JS division is floating point; add Math.trunc for integer div if needed
        if node.op == '/':
            return f"Math.trunc({left} / {right})"
        return f"({left} {node.op} {right})"

    def visit_Var(self, node):
        return node.name

    def visit_Let(self, node):
        # let x = e in body  ->  ((x) => body)(e)
        val  = self.visit(node.value)
        body = self.visit(node.body)
        return f"(({node.name}) => {body})({val})"

    def visit_IfExpr(self, node):
        cond  = self.visit(node.cond)
        then_ = self.visit(node.then_)
        else_ = self.visit(node.else_)
        return f"({cond} ? {then_} : {else_})"

    def visit_FuncDef(self, node):
        body = self.visit(node.body)
        return f"(({node.param}) => {body})"

    def visit_Call(self, node):
        func = self.visit(node.func)
        arg  = self.visit(node.arg)
        return f"{func}({arg})"

js_trans = JavaScriptTranspiler()
js_code  = js_trans.visit(ast)
print("JavaScript code:", js_code)
# Output: ((x) => ((x * 2) + 1))(3)
# Paste into browser console to verify: returns 7
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

---

#### 4. The Haskell Transpiler

Haskell uses `let ... in ...` naturally for our `Let` node, and lambda syntax for `FuncDef`. The transpiler produces valid Haskell expressions:

```python
class Num:
    def __init__(self, value): self.value = value
class BinOp:
    def __init__(self, op, left, right): self.op = op; self.left = left; self.right = right
class Var:
    def __init__(self, name): self.name = name
class Let:
    def __init__(self, name, value, body): self.name = name; self.value = value; self.body = body
class IfExpr:
    def __init__(self, cond, then_, else_): self.cond = cond; self.then_ = then_; self.else_ = else_
class FuncDef:
    def __init__(self, param, body): self.param = param; self.body = body
class Call:
    def __init__(self, func, arg): self.func = func; self.arg = arg

class Visitor:
    def visit(self, node):
        method_name = f"visit_{type(node).__name__}"
        method = getattr(self, method_name, self.generic_visit)
        return method(node)
    def generic_visit(self, node):
        raise NotImplementedError(f"No visitor for {type(node).__name__}")

ast = Let("x", Num(3), BinOp("+", BinOp("*", Var("x"), Num(2)), Num(1)))

class HaskellTranspiler(Visitor):
    """Transpiles our mini-language AST to Haskell expressions."""

    def visit_Num(self, node):
        return str(node.value)

    def visit_BinOp(self, node):
        left  = self.visit(node.left)
        right = self.visit(node.right)
        if node.op == '/':
            return f"(div {left} {right})"    # integer division in Haskell
        return f"({left} {node.op} {right})"

    def visit_Var(self, node):
        return node.name

    def visit_Let(self, node):
        val  = self.visit(node.value)
        body = self.visit(node.body)
        return f"(let {node.name} = {val} in {body})"

    def visit_IfExpr(self, node):
        cond  = self.visit(node.cond)
        then_ = self.visit(node.then_)
        else_ = self.visit(node.else_)
        return f"(if {cond} then {then_} else {else_})"

    def visit_FuncDef(self, node):
        body = self.visit(node.body)
        return f"(\\{node.param} -> {body})"

    def visit_Call(self, node):
        func = self.visit(node.func)
        arg  = self.visit(node.arg)
        return f"({func} {arg})"

hs_trans = HaskellTranspiler()
hs_code  = hs_trans.visit(ast)
print("Haskell expression:", hs_code)
# Output: (let x = 3 in ((x * 2) + 1))
# Load in GHCi to verify: returns 7
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

---

[[MC]]
A transpiler differs from an interpreter in which fundamental way?

- (x) A transpiler emits code in a target language rather than executing the program; both traverse the same AST but produce different output from each node.
- ( ) A transpiler performs type-checking at compile time while an interpreter does not.
- ( ) A transpiler uses a bottom-up (LR) parser while an interpreter uses a top-down (LL) parser.
- ( ) A transpiler is always faster to execute than an interpreter because it generates native code.

---

### Part III: Stack Machine / Bytecode Compiler

#### 5. Compiling to a Virtual Stack Machine

A stack machine is like a desk calculator with an explicit memory stack: you push operands, apply an operation that consumes the top values and pushes a result, and at the end the answer sits alone on the top of the stack. Compiling to this model is much simpler than compiling to a real CPU because you never need to manage registers — the stack is both source and destination for every operation.

Real compilers (Python, Java, Lua) compile to a **bytecode** for a virtual stack machine. The stack machine has a simple instruction set:

| Instruction | Effect |
|---|---|
| `PUSH n` | Push constant `n` onto stack |
| `LOAD x` | Push value of variable `x` |
| `STORE x` | Pop and store in variable `x` |
| `ADD` / `SUB` / `MUL` / `DIV` | Pop two values, push result |
| `JMP_IF_FALSE label` | Pop; if 0/False, jump to label |
| `JMP label` | Unconditional jump |
| `LABEL label` | Mark this position |
| `CALL n` | Call top-of-stack function with n args |
| `RETURN` | Return top of stack |

Compilation is a visitor that emits a list of these instructions:

```python
class Num:
    def __init__(self, value): self.value = value
class BinOp:
    def __init__(self, op, left, right): self.op = op; self.left = left; self.right = right
class Var:
    def __init__(self, name): self.name = name
class Let:
    def __init__(self, name, value, body): self.name = name; self.value = value; self.body = body
class IfExpr:
    def __init__(self, cond, then_, else_): self.cond = cond; self.then_ = then_; self.else_ = else_

class Visitor:
    def visit(self, node):
        method_name = f"visit_{type(node).__name__}"
        method = getattr(self, method_name, self.generic_visit)
        return method(node)
    def generic_visit(self, node):
        raise NotImplementedError(f"No visitor for {type(node).__name__}")

ast = Let("x", Num(3), BinOp("+", BinOp("*", Var("x"), Num(2)), Num(1)))

class Bytecode:
    def __init__(self, op, *args):
        self.op   = op
        self.args = args

    def __repr__(self):
        return f"{self.op} {' '.join(str(a) for a in self.args)}".strip()

class BytecodeCompiler(Visitor):
    def __init__(self):
        self.instructions = []
        self._label_count = 0

    def fresh_label(self, prefix="L"):
        self._label_count += 1
        return f"{prefix}{self._label_count}"

    def emit(self, op, *args):
        self.instructions.append(Bytecode(op, *args))

    def visit_Num(self, node):
        self.emit("PUSH", node.value)

    def visit_Var(self, node):
        self.emit("LOAD", node.name)

    def visit_BinOp(self, node):
        self.visit(node.left)    # push left
        self.visit(node.right)   # push right
        ops = {'+': 'ADD', '-': 'SUB', '*': 'MUL', '/': 'DIV'}
        self.emit(ops[node.op])  # pop two, push result

    def visit_Let(self, node):
        self.visit(node.value)         # push value
        self.emit("STORE", node.name)  # store in variable
        self.visit(node.body)          # compile body (value is now on stack)

    def visit_IfExpr(self, node):
        else_lbl = self.fresh_label("ELSE")
        end_lbl  = self.fresh_label("END")
        self.visit(node.cond)
        self.emit("JMP_IF_FALSE", else_lbl)
        self.visit(node.then_)
        self.emit("JMP", end_lbl)
        self.emit("LABEL", else_lbl)
        self.visit(node.else_)
        self.emit("LABEL", end_lbl)

# Compile the example AST
compiler = BytecodeCompiler()
compiler.visit(ast)

print("Bytecode for: let x = 3 in x * 2 + 1")
for i, instr in enumerate(compiler.instructions):
    print(f"  {i:3d}  {instr}")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

---

#### 6. Executing the Bytecode (Virtual Machine)

The bytecode interpreter is now much simpler than the tree-walking interpreter: it is a loop over a flat instruction list with a stack:

```python
class Num:
    def __init__(self, value): self.value = value
class BinOp:
    def __init__(self, op, left, right): self.op = op; self.left = left; self.right = right
class Var:
    def __init__(self, name): self.name = name
class Let:
    def __init__(self, name, value, body): self.name = name; self.value = value; self.body = body
class IfExpr:
    def __init__(self, cond, then_, else_): self.cond = cond; self.then_ = then_; self.else_ = else_

class Visitor:
    def visit(self, node):
        method_name = f"visit_{type(node).__name__}"
        method = getattr(self, method_name, self.generic_visit)
        return method(node)
    def generic_visit(self, node):
        raise NotImplementedError(f"No visitor for {type(node).__name__}")

class Bytecode:
    def __init__(self, op, *args):
        self.op   = op
        self.args = args
    def __repr__(self):
        return f"{self.op} {' '.join(str(a) for a in self.args)}".strip()

class BytecodeCompiler(Visitor):
    def __init__(self):
        self.instructions = []
        self._label_count = 0
    def fresh_label(self, prefix="L"):
        self._label_count += 1
        return f"{prefix}{self._label_count}"
    def emit(self, op, *args):
        self.instructions.append(Bytecode(op, *args))
    def visit_Num(self, node):
        self.emit("PUSH", node.value)
    def visit_Var(self, node):
        self.emit("LOAD", node.name)
    def visit_BinOp(self, node):
        self.visit(node.left)
        self.visit(node.right)
        ops = {'+': 'ADD', '-': 'SUB', '*': 'MUL', '/': 'DIV'}
        self.emit(ops[node.op])
    def visit_Let(self, node):
        self.visit(node.value)
        self.emit("STORE", node.name)
        self.visit(node.body)
    def visit_IfExpr(self, node):
        else_lbl = self.fresh_label("ELSE")
        end_lbl  = self.fresh_label("END")
        self.visit(node.cond)
        self.emit("JMP_IF_FALSE", else_lbl)
        self.visit(node.then_)
        self.emit("JMP", end_lbl)
        self.emit("LABEL", else_lbl)
        self.visit(node.else_)
        self.emit("LABEL", end_lbl)

ast = Let("x", Num(3), BinOp("+", BinOp("*", Var("x"), Num(2)), Num(1)))
compiler = BytecodeCompiler()
compiler.visit(ast)

class StackMachine:
    def __init__(self, instructions):
        self.instructions = instructions
        self.stack        = []
        self.env          = {}
        # Build label map
        self.labels = {
            instr.args[0]: i
            for i, instr in enumerate(instructions)
            if instr.op == "LABEL"
        }

    def run(self):
        pc = 0
        while pc < len(self.instructions):
            instr = self.instructions[pc]
            op    = instr.op

            if op == "PUSH":
                self.stack.append(instr.args[0])
            elif op == "LOAD":
                self.stack.append(self.env[instr.args[0]])
            elif op == "STORE":
                self.env[instr.args[0]] = self.stack.pop()
            elif op in ("ADD", "SUB", "MUL", "DIV"):
                b, a = self.stack.pop(), self.stack.pop()
                result = {'ADD': a+b, 'SUB': a-b, 'MUL': a*b, 'DIV': a//b}[op]
                self.stack.append(result)
            elif op == "JMP_IF_FALSE":
                if not self.stack.pop():
                    pc = self.labels[instr.args[0]]
                    continue
            elif op == "JMP":
                pc = self.labels[instr.args[0]]
                continue
            elif op == "LABEL":
                pass   # no-op at runtime
            pc += 1

        return self.stack[-1] if self.stack else None

vm = StackMachine(compiler.instructions)
result = vm.run()
print("VM result:", result)   # 7
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

---

### Part IV: Source Maps and Debugging

#### 7. Source Maps: Connecting Output Back to Input

A **source map** connects positions in the generated code back to positions in the source. This is why browser developer tools can show you a TypeScript error on the TypeScript line, even though the browser runs JavaScript. For our bytecode, a source map is a list of `(instruction_index, source_line)` pairs.

```python
class Num:
    def __init__(self, value): self.value = value
class BinOp:
    def __init__(self, op, left, right): self.op = op; self.left = left; self.right = right
class Var:
    def __init__(self, name): self.name = name
class Let:
    def __init__(self, name, value, body): self.name = name; self.value = value; self.body = body
class IfExpr:
    def __init__(self, cond, then_, else_): self.cond = cond; self.then_ = then_; self.else_ = else_

class Visitor:
    def visit(self, node):
        method_name = f"visit_{type(node).__name__}"
        method = getattr(self, method_name, self.generic_visit)
        return method(node)
    def generic_visit(self, node):
        raise NotImplementedError(f"No visitor for {type(node).__name__}")

class Bytecode:
    def __init__(self, op, *args):
        self.op   = op
        self.args = args
    def __repr__(self):
        return f"{self.op} {' '.join(str(a) for a in self.args)}".strip()

class BytecodeCompiler(Visitor):
    def __init__(self):
        self.instructions = []
        self._label_count = 0
    def fresh_label(self, prefix="L"):
        self._label_count += 1
        return f"{prefix}{self._label_count}"
    def emit(self, op, *args):
        self.instructions.append(Bytecode(op, *args))
    def visit_Num(self, node):
        self.emit("PUSH", node.value)
    def visit_Var(self, node):
        self.emit("LOAD", node.name)
    def visit_BinOp(self, node):
        self.visit(node.left)
        self.visit(node.right)
        ops = {'+': 'ADD', '-': 'SUB', '*': 'MUL', '/': 'DIV'}
        self.emit(ops[node.op])
    def visit_Let(self, node):
        self.visit(node.value)
        self.emit("STORE", node.name)
        self.visit(node.body)
    def visit_IfExpr(self, node):
        else_lbl = self.fresh_label("ELSE")
        end_lbl  = self.fresh_label("END")
        self.visit(node.cond)
        self.emit("JMP_IF_FALSE", else_lbl)
        self.visit(node.then_)
        self.emit("JMP", end_lbl)
        self.emit("LABEL", else_lbl)
        self.visit(node.else_)
        self.emit("LABEL", end_lbl)

ast = Let("x", Num(3), BinOp("+", BinOp("*", Var("x"), Num(2)), Num(1)))

class TracingCompiler(BytecodeCompiler):
    """Extends BytecodeCompiler to emit source map entries."""

    def __init__(self):
        super().__init__()
        self.source_map = []   # (instruction_index, node_type)

    def emit(self, op, *args):
        self.source_map.append((len(self.instructions), op))
        super().emit(op, *args)

    def visit_BinOp(self, node):
        start_pc = len(self.instructions)
        super().visit_BinOp(node)
        end_pc = len(self.instructions)
        print(f"  BinOp '{node.op}' -> instructions {start_pc}..{end_pc-1}")

tc = TracingCompiler()
tc.visit(ast)
print("\nSource map excerpt (instruction index -> operation):")
for idx, op in tc.source_map[:8]:
    print(f"  {idx}: {op}")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

---

### Part V: Exercises

#### 8. Exercises

1. **Extend the transpilers.** Add support for `FuncDef` and `Call` nodes to all three transpilers (Python, JavaScript, Haskell). Test with the AST for `(lambda x: x * x)(5)` — i.e., `Call(FuncDef("x", BinOp("*", Var("x"), Var("x"))), Num(5))`. All three transpilers should produce expressions that evaluate to 25 in their respective languages.

2. **Boolean support.** Add `Bool(value)` and `And(left, right)` / `Or(left, right)` nodes to the AST. Extend all three transpilers and the bytecode compiler. Python uses `and`/`or`; JavaScript uses `&&`/`||`; Haskell uses `&&`/`||`. Test with `And(Bool(True), Bool(False))`.

3. **Bytecode optimizer: constant folding.** Write a `ConstantFolder` visitor that transforms `BinOp("+", Num(2), Num(3))` into `Num(5)` before compilation. This is the simplest compiler optimization: evaluating constant expressions at compile time. Apply it to the AST before compiling to bytecode and verify that the bytecode is shorter.

4. **Transpile your own mini-language.** Take the parser you built for the mini-language assignment and add a `PythonTranspiler` backend. The transpiler should translate your language's programs into valid Python. Test by parsing a factorial program in your language and transpiling + executing it in Python. Include one program that demonstrates your language's most distinctive feature.

5. **Reflection: when to interpret, when to compile, when to transpile.** Write a one-page analysis of three real language implementation decisions: (a) why CPython compiles to `.pyc` bytecode rather than interpreting the source AST directly; (b) why TypeScript transpiles to JavaScript rather than compiling to machine code; (c) why HHVM (Facebook's PHP runtime) JIT-compiles rather than interpreting. In each case, state the tradeoff and who benefits.

---

#### 9. Further Reading

- Nystrom, Robert. *Crafting Interpreters* (available free online). Part III covers bytecode compilation with a full stack machine (Clox); the code in this module is a simplified version of that approach.
- Thain, Douglas. *Introduction to Compilers and Language Design*. Chapters 8–10 cover intermediate representations, code generation, and optimization in depth.
- Gamma, Erich et al. *Design Patterns* (Addison-Wesley, 1995). Chapter on the Visitor pattern — the pattern that makes the transpiler architecture here work cleanly.
- Cooper, Keith and Linda Torczon. *Engineering a Compiler* (2nd ed., Morgan Kaufmann, 2011). The most complete modern treatment of code generation, register allocation, and optimization.
- Pereira, Fernando and Jens Palsberg. "Register Allocation After Classical SSA Elimination is NP-Complete." *FoSSaCS*, 2005. A glimpse at why real compilers are hard, even after you have a correct code generator.
