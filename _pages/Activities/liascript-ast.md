# Abstract Syntax Trees
<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://github.com/BillJr99/Ursinus-CS374-Fall2026/blob/gh-pages/_pages/Activities/liascript-ast.md or locally via https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374/gh-pages/_pages/Activities/liascript-ast.md

import: https://raw.githubusercontent.com/liascript/CodeRunner/master/README.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

# Abstract Syntax Trees

Your parser has been quietly building nested tuples; this two-day module makes the tree a first-class citizen: the **abstract syntax tree (AST)**, the central data structure of every language implementation and the hinge of your whole project, where the parser's output becomes the interpreter's input. The arc: **parse trees versus ASTs $\rightarrow$ node classes $\rightarrow$ building trees in the parser $\rightarrow$ walking trees (printing today, evaluating soon)**.

---

## Directions and Group Roles

Work in your POGIL team with rotated roles (**Manager**, **Recorder**, **Presenter**, **Reflector**). Consider each model and question individually first, then discuss with your group. The Recorder posts answers to the Class Activity Questions discussion board; the Presenter reports out areas of disagreement or alternative approaches. After class, respond to the reflective prompt individually in your notebook.

---

# Part I: The Tree Itself (Day 1)

## 1. Abstract Means On Purpose

**A parse tree records every grammar step; an AST records only meaning.** The parse tree for `(2 + 3)` contains nodes for `expr`, `addsub`, `muldiv`, `primary`, and the parentheses themselves: the full derivation, including all the ladder scaffolding that exists only to enforce precedence. The AST keeps the addition and its two operands, and nothing else: parentheses vanish (their *effect*, the tree shape, remains), and the single-child chains `expr -> addsub -> muldiv -> ...` collapse.

**Each node type captures one construct.** A practical design gives every construct a small class with named fields:

```
Num(value)            Var(name)            BinOp(op, left, right)
UnaryOp(op, operand)  Assign(name, expr)   Print(expr)
While(cond, body)     If(cond, then, otherwise)   Block(statements)
```

The set of node classes *is* your language's semantic inventory: if a construct has no node, your language cannot mean it.

---

## Model 1: Two Trees for One Expression

For the source `(2 + 3) * 4`, sketch side by side: the full parse tree under the ladder grammar, and the AST.

### Critical Thinking Questions

1. Count nodes in each. What fraction of the parse tree was scaffolding?
2. The parentheses appear nowhere in the AST, yet `(2 + 3) * 4` and `2 + 3 * 4` get different ASTs. Resolve the apparent paradox in two sentences.
3. The unary `-` and binary `-` use the same character but deserve different node types. Argue why, from the perspective of the evaluator that will consume the tree.
4. Propose the node class (name and fields) for your project language's `let` statement, and for a function call. Field naming is design; choose names your December teammates will thank you for.

---

## Code Cell

```python
# AST node classes: tiny, explicit, and printable. These replace the tuples.

class Node:
    """Base class so isinstance(x, Node) distinguishes trees from leaves."""

class Num(Node):
    def __init__(self, value): self.value = value
    def __repr__(self): return f"Num({self.value})"

class Var(Node):
    def __init__(self, name): self.name = name
    def __repr__(self): return f"Var({self.name!r})"

class BinOp(Node):
    def __init__(self, op, left, right):
        self.op, self.left, self.right = op, left, right
    def __repr__(self): return f"BinOp({self.op!r}, {self.left!r}, {self.right!r})"

class UnaryOp(Node):
    def __init__(self, op, operand):
        self.op, self.operand = op, operand
    def __repr__(self): return f"UnaryOp({self.op!r}, {self.operand!r})"

def pretty(node, indent=0):
    """An indented tree printer: your first tree WALK."""
    try:
        pad = "  " * indent
        if isinstance(node, Num):
            print(f"{pad}Num {node.value}")
        elif isinstance(node, Var):
            print(f"{pad}Var {node.name}")
        elif isinstance(node, UnaryOp):
            print(f"{pad}UnaryOp {node.op}")
            pretty(node.operand, indent + 1)
        elif isinstance(node, BinOp):
            print(f"{pad}BinOp {node.op}")
            pretty(node.left, indent + 1)
            pretty(node.right, indent + 1)
        else:
            print(f"{pad}?? {node!r}")
    except Exception as e:
        print(f"[ast:pretty] {e}")
        import traceback; traceback.print_exc()

# The AST for (2 + 3) * 4, built by hand today, by your parser tomorrow:
tree = BinOp("*", BinOp("+", Num(2), Num(3)), Num(4))
pretty(tree)
```

---

## Model 2: The Printer Is a Prototype

### Critical Thinking Questions

5. `pretty` dispatches on node type and recurses on children. Name the two or three lines you would change to make it *evaluate* instead of print. You have just designed next week's interpreter.
6. The recursion visits children before finishing the parent's subtree (children print indented beneath). For evaluation, must children be processed before or after the parent's operation? Which classic traversal order is that?
7. Add a `Paren` node to the classes, then argue the team out of it: what goes wrong (or merely gets noisy) downstream if syntax-only artifacts survive into the AST?

---

# Part II: Building Trees in the Parser (Day 2)

## 2. The One-Line Upgrade

Your expression parser changes almost nothing: every place it built a tuple now constructs a node. `node = (op, node, right)` becomes `node = BinOp(op, node, right)`; `("num", 4.0)` becomes `Num(4.0)`. The fold-left associativity logic, the tier structure, the lookahead: untouched. This is the payoff of having kept structure and meaning separate all along.

[[MC]]
After upgrading the parser to emit AST nodes, the team's old torture tests still pass with identical tree *shapes*. The best explanation is:
- (x) The grammar and the parsing logic determine the shape; the node classes only changed the representation of each node
- ( ) Python tuples and classes are interchangeable types
- ( ) The lexer normalizes the input
- ( ) Associativity moved into the node classes

---

## 3. Exercises

1. *Parser upgrade.* Convert your expression parser from tuples to the node classes, and extend the classes to cover your statement forms (`Assign`/`Let`, `Print`, `While`, `Block`, `If`). Demonstrate `pretty` on a three-statement program.
2. *To source and back.* Write `unparse(node)` producing valid source text from an AST, parenthesizing only where the tree shape requires it (`BinOp('*', BinOp('+', ...), ...)` needs them; `BinOp('+', BinOp('*', ...), ...)` does not). Verify `parse(unparse(parse(s)))` yields an identical tree for five inputs: a round-trip test your project will keep forever.
3. *Tree statistics.* Write `count_nodes(node)` and `depth(node)` as tree walks. Report both for your torture tests, and identify which source-level feature drives depth fastest.
4. *Node design review.* Trade your project node-class inventory with another team. Each reviews the other's for missing constructs, redundant nodes, and field names that will confuse an evaluator. Document one change you accepted.

---

## Reflection Prompt

In your notebook: the AST is the third representation of the same program this course has given you (characters, tokens, tree), each one closer to meaning and farther from what the programmer typed. What is gained and what is honestly lost at each translation? Whose intentions survive?

---

## 4. Further Reading

- Douglas Thain. *Introduction to Compilers and Language Design*, Chapter 5.
- Robert Nystrom. *Crafting Interpreters*, "Representing Code" (online).
- The Python `ast` module documentation: run `ast.dump(ast.parse("2+3*4"))` and meet a production AST.
