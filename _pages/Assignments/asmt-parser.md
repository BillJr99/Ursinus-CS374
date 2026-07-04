---
layout: assignment
permalink: /Assignments/Parser
title: "CS374: Principles of Programming Languages - The Parser and AST"

info:
  coursenum: CS374
  points: 100
  goals:
    - To write a formal EBNF grammar for the project language covering expressions, statements, and programs
    - To implement a recursive descent parser for expressions and statements atop the Lexer component
    - To build the full precedence ladder with correct associativity, parentheses, and unary minus
    - To produce an abstract syntax tree of node dataclasses with a pretty-printer and an unparser
    - To report syntax errors with positions, expected tokens, and found tokens
  rubric:
    - weight: 30
      description: "EBNF Grammar (Goal 1: write a formal EBNF grammar covering expressions, statements, and programs)"
      preemerging: No grammar is provided, or the grammar is so incomplete that fewer than half the language constructs are covered
      beginning: A grammar is provided but contains ambiguities, missing precedence levels, or structural errors that would cause the parser to behave incorrectly
      progressing: The grammar covers all constructs and is mostly unambiguous, but the precedence ladder is incomplete (e.g., comparison operators at the wrong level) or associativity is not explicit
      proficient: The grammar is complete, unambiguous, and matches the implemented parser exactly — every precedence level is a separate non-terminal, associativity is enforced by structure, and the dangling-else resolution is stated explicitly — demonstrating mastery of formal language specification
    - weight: 40
      description: "Recursive Descent Parser (Goals 2–3: implement a recursive descent parser with the full precedence ladder and correct associativity)"
      preemerging: The parser fails to run or fails most provided programs due to major structural errors
      beginning: The parser runs but fails on several test programs — e.g., it cannot parse nested constructs, or associativity is wrong at one or more tiers
      progressing: The parser passes the provided test programs but fails on edge cases — e.g., it right-associates `and`/`or` instead of left-associating as the grammar specifies, or it crashes on certain valid inputs
      proficient: A correct parser passes all provided and hidden test programs with correct precedence and associativity at every tier; parenthesized subexpressions, nested blocks, and if-else chains parse correctly; and the parser is built by importing the Lexer unchanged — demonstrating that Goals 2 and 3 are met end-to-end
    - weight: 30
      description: "AST Design, Tooling, and Error Reporting (Goals 4–5: produce a dataclass AST with pretty-printer/unparser, and report errors with positions)"
      preemerging: No AST node classes exist, or the tree structure does not reflect the program's meaning
      beginning: Node classes exist but the pretty-printer or unparser is missing, or error messages lack positions
      progressing: Node classes, pretty-printer, and unparser work for most constructs; errors include positions; but the round-trip property is not verified programmatically
      proficient: Node dataclasses cover every construct with documented fields; the pretty-printer renders nested structure clearly; the unparser inserts parentheses only where the tree shape requires them; the round-trip property parse(unparse(parse(s))) is verified across the full test suite; every error states what was expected, what was found, and the line and column — demonstrating that the AST is a complete, self-documenting artifact
  readings:
    - rtitle: "Recursive Descent Activity"
      rlink: "https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374-Fall2026/gh-pages/_pages/Activities/liascript-recursivedescent.md"
    - rtitle: "Parsing Expressions Activity"
      rlink: "https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374-Fall2026/gh-pages/_pages/Activities/liascript-parsingexpressions.md"
    - rtitle: "Abstract Syntax Trees Activity"
      rlink: "https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374-Fall2026/gh-pages/_pages/Activities/liascript-ast.md"

tags:
  - parser
  - ast
  - languages
  - pipeline

---

This assignment builds the second permanent component of your pipeline: a recursive descent parser that consumes your Lexer's tokens and produces an AST of node dataclasses. Build tier by tier, testing each before adding the next. The grammar you write first is the specification; the parser is the implementation of that specification — they must agree exactly.

---

## Purpose, Task, and Criteria

**Purpose:** This assignment builds the skills of writing a formal EBNF grammar, implementing a recursive descent parser with a full precedence ladder and correct associativity, and designing an AST of dataclasses with a pretty-printer, an unparser, and positioned error messages. Recursive descent is not a museum piece — it is how most production compilers (including those for several major languages) parse source code, and the same technique powers linters, formatters, configuration readers, and the language servers behind your IDE's autocomplete. This parser is the second permanent component of your pipeline: it imports your Lexer unchanged, and the Interpreter assignment and your team project import it unchanged in turn.

**Task:** Work through the three numbered Parts below in order: the EBNF grammar (Part 1), the recursive descent parser built tier by tier atop your Lexer (Part 2), and the AST tooling with round-trip verification and error reporting (Part 3). Write the grammar before any parser code — it is the contract everything else is checked against.

**Criteria:** Your work is graded against the rubric at the top of this page (30/40/30 points across the three Parts). What a strong submission looks like:

- The grammar and the parser agree exactly: every precedence tier is its own non-terminal, associativity is enforced by structure, and the dangling-else policy is stated in the readme rather than left implicit.
- The precedence tests from Step 2b pass with the exact tree shapes shown — `8 / 4 / 2` left-associates, `2 + 3 * 4` binds the multiplication tighter — and the Lexer is imported unchanged.
- The round-trip property `parse(unparse(parse(s)))` is verified programmatically across the whole test suite, and every `ParseError` names the expected token, the found token, and its line and column.

---

## Getting Started

### Environment and Setup

You need Python 3.10+ and your completed Lexer. Copy your `lexer.py` and `token_spec.json` into the project directory and import the Lexer unchanged — if you discover a lexer bug while parsing, fix it and note the fix in your readme. Create the deliverable files up front:

```
lexer.py         # from the Lexer assignment, unchanged
parser.py        # the recursive descent parser
ast_nodes.py     # node dataclasses, pretty-printer, unparser
test_parser.py   # the test suite
```

Confirm the import works before writing any parser code: `python -c "from lexer import Lexer; print(Lexer('let x = 1;').peek())"` should print a `LET` token.

### Your First 30 Minutes

Draft the expression tiers of your grammar on paper (Part 1 gives you the ladder), then implement just the bottom rung. Copy the `Num` and `Var` dataclasses from Step 2a into `ast_nodes.py`, and write `parse_primary()` in `parser.py`:

```python
from lexer import Lexer
from ast_nodes import Num

lexer = Lexer("42")
print(parse_primary(lexer))   # Num(value=42, line=1)
```

When `parse_primary` returns a `Num` for `42`, a `Var` for `x`, and raises `ParseError` for `;`, you have the pattern every other tier repeats: look at `lexer.peek()`, decide, consume with `lexer.advance()` or `lexer.expect()`, return a node. Each tier of the ladder is one more function built on this move.

### Suggested Pacing

This assignment is handed out on Thursday of week 7 and due on Tuesday of week 9. Build tier by tier and keep the tests green as you go:

| Checkpoint | You should have |
|------------|----------------|
| Week 7 (Thu) — assigned | Grammar drafted (Part 1); `parse_primary` and `parse_unary` working |
| Week 8 (Tue) | Expression ladder complete through `parse_expr` with passing tree-shape tests (Step 2b) |
| Week 8 (Thu) | Statements, blocks, and the worked `while` example parsing (Steps 2c–2d) |
| Weekend | Pretty-printer and unparser working (Steps 3a–3b) |
| Week 9 (Tue) — due | Round-trip verification and error reports complete; readme and ZIP submitted |

---

## Part 1: EBNF Grammar (30 points)

### Writing the Grammar

Write the complete EBNF grammar for your language before writing a line of parser code. The grammar will be included verbatim in your readme and will serve as the contract between the grammar document and the implementation.

Notation: `*` = zero or more, `+` = one or more, `?` = zero or one, `|` = alternation, `( )` = grouping. Terminal tokens appear in `ALL_CAPS` or as quoted strings.

### Required Non-Terminals

Your grammar must define at least the following non-terminals, in precedence order from loosest to tightest:

```
program     ::= stmt* EOF

stmt        ::= let_stmt
              | assign_stmt
              | print_stmt
              | if_stmt
              | while_stmt
              | block

let_stmt    ::= LET IDENT EQ expr SEMICOLON
assign_stmt ::= IDENT EQ expr SEMICOLON
print_stmt  ::= PRINT expr SEMICOLON
if_stmt     ::= IF expr block ( ELSE ( if_stmt | block ) )?
while_stmt  ::= WHILE expr block
block       ::= LBRACE stmt* RBRACE

expr        ::= or_expr
or_expr     ::= and_expr ( OR and_expr )*
and_expr    ::= not_expr ( AND not_expr )*
not_expr    ::= NOT not_expr | comparison
comparison  ::= addsub ( ( LT | LE | GT | GE | EQEQ | NEQ ) addsub )?
addsub      ::= muldiv ( ( PLUS | MINUS ) muldiv )*
muldiv      ::= unary ( ( STAR | SLASH ) unary )*
unary       ::= MINUS unary | primary
primary     ::= INT | FLOAT | STRING | TRUE | FALSE | IDENT
              | LPAREN expr RPAREN
```

### Step 1a: Grammar Documentation

In your readme, write the complete grammar. For each non-terminal, add one sentence explaining what it represents and why it is placed at its position in the precedence ladder. For example:

> `addsub` handles `+` and `-`, which bind less tightly than multiplication and division. The `( ... )*` loop enforces left-associativity: `8 - 3 - 2` builds `(8-3)-2 = 3`, not `8-(3-2) = 7`.

### Step 1b: Dangling-Else Resolution

State explicitly in your writeup which `if` a dangling `else` is attached to, and how your grammar enforces that rule. Example: given `if a if b print 1; else print 2;`, does the `else` belong to the inner `if` or the outer? Most languages attach `else` to the nearest `if`; if you follow that convention, explain why the grammar (and parser) do so.

---

## Part 2: Recursive Descent Parser (40 points)

### Step 2a: AST Node Dataclasses

Before writing any parsing functions, define the node classes. Use Python `dataclasses.dataclass` for clean `__init__` and `__repr__`:

```python
from dataclasses import dataclass, field
from typing import List, Optional, Any

@dataclass
class Num:
    value: float       # already parsed to a Python number
    line: int = 0

@dataclass
class Var:
    name: str
    line: int = 0

@dataclass
class BinOp:
    op: str            # "+", "-", "*", "/", "<", "<=", etc.
    left: Any
    right: Any

@dataclass
class UnaryOp:
    op: str            # "-" or "not"
    operand: Any

@dataclass
class Let:
    name: str
    value: Any

@dataclass
class Assign:
    name: str
    value: Any

@dataclass
class Print:
    value: Any

@dataclass
class Block:
    stmts: List[Any] = field(default_factory=list)

@dataclass
class If:
    condition: Any
    then_branch: Any   # always a Block
    else_branch: Any   # Block, If, or None

@dataclass
class While:
    condition: Any
    body: Any          # always a Block

@dataclass
class Program:
    stmts: List[Any] = field(default_factory=list)
```

Add `Str`, `BoolLit`, and `LogicOp` if your design uses them separately from `BinOp` and `UnaryOp`.

### Step 2b: Expression Ladder (test after every step)

Implement each parsing function below. After each step, commit at least three passing tests before moving to the next.

**`parse_primary()`** — returns a `Num`, `Var`, `Str`, `BoolLit`, or the result of a parenthesized `parse_expr()`. Raise `ParseError` on any other token.

**`parse_unary()`** — if the next token is `MINUS`, consume it and recursively call `parse_unary()`, wrapping in `UnaryOp("-", ...)`. Verify that `--x` builds `UnaryOp("-", UnaryOp("-", Var("x")))`.

**`parse_muldiv()`** — parse one `unary`, then loop while the next token is `STAR` or `SLASH`, consuming the operator and another `unary`, and replacing the left side with `BinOp(op, left, right)`. Verify `8 / 4 / 2` builds `BinOp("/", BinOp("/", Num(8), Num(4)), Num(2))`.

**`parse_addsub()`** — same left-fold pattern over `PLUS` and `MINUS` above `muldiv`. Verify `2 + 3 * 4` builds `BinOp("+", Num(2), BinOp("*", Num(3), Num(4)))`.

**`parse_comparison()`** — parse one `addsub`; if the next token is a comparison operator, consume it and one more `addsub` to form a `BinOp`. Comparisons are non-associative (no chaining); attempting `a < b < c` is a syntax error.

**`parse_not()`** — handle unary `NOT`, then call `parse_comparison()`.

**`parse_and()`** — left-fold `not` expressions over `AND`.

**`parse_or()`** — left-fold `and` expressions over `OR`. Verify `a or b and c` builds `BinOp("or", Var("a"), BinOp("and", Var("b"), Var("c")))`.

**`parse_expr()`** — delegates to `parse_or()`.

### Step 2c: Statements and Blocks

**`parse_let_stmt()`** — consumes `LET`, then expects `IDENT`, `EQ`, an expression, and `SEMICOLON` using `lexer.expect()`. Returns a `Let` node.

**`parse_assign_stmt()`** — consumes `IDENT` and `EQ`, then an expression and `SEMICOLON`. Returns an `Assign` node. (How will you distinguish assignment from an expression statement that starts with an identifier? Document your lookahead strategy.)

**`parse_print_stmt()`** — `PRINT`, expression, `SEMICOLON`. Returns `Print`.

**`parse_block()`** — `LBRACE`, then zero or more statements, then `RBRACE`. Returns `Block`. Each statement is dispatched via `parse_stmt()`.

**`parse_if_stmt()`** — `IF`, expression (the condition), block. Then, if the next token is `ELSE`, consume it. If the token after `ELSE` is `IF`, recursively call `parse_if_stmt()` for the `else-if` branch; otherwise call `parse_block()`. Returns `If`.

**`parse_while_stmt()`** — `WHILE`, expression, block. Returns `While`.

**`parse_program()`** — parse statements until `EOF`. Returns `Program`.

### Step 2d: Worked Parse Example

The program:

```
let x = 10;
while x > 0 {
    print x;
    x = x - 1;
}
```

should produce (abbreviated):

```
Program(stmts=[
  Let(name='x', value=Num(10)),
  While(
    condition=BinOp('>', Var('x'), Num(0)),
    body=Block(stmts=[
      Print(Var('x')),
      Assign('x', BinOp('-', Var('x'), Num(1)))
    ])
  )
])
```

Trace the parser's calls on this program in your writeup.

---

## Part 3: AST Tooling and Error Reporting (30 points)

### Step 3a: Pretty Printer

Write `pretty(node, indent=0) -> str` that returns an indented string representation of the tree. Each level of nesting adds two spaces. Example:

```
Program
  Let x
    Num(10)
  While
    BinOp(>)
      Var(x)
      Num(0)
    Block
      Print
        Var(x)
      Assign x
        BinOp(-)
          Var(x)
          Num(1)
```

### Step 3b: Unparser

Write `unparse(node) -> str` that regenerates valid source code from the AST. Rules:
- Insert parentheses around a `BinOp` subexpression only when necessary to preserve the tree's meaning given standard precedence.
- The rule: a child `BinOp` needs parentheses when its operator's precedence is *lower* than its parent's, or when it is the right child of a left-associative operator at the same precedence level.

Example: `unparse(BinOp("+", Num(2), BinOp("*", Num(3), Num(4))))` → `"2 + 3 * 4"` (no parentheses needed).  
Example: `unparse(BinOp("*", Num(2), BinOp("+", Num(3), Num(4))))` → `"2 * (3 + 4)"` (parentheses required).

### Step 3c: Round-Trip Verification

For every test program in your test suite, verify the round-trip property:

```python
tree1 = parse(source)
source2 = unparse(tree1)
tree2 = parse(source2)
assert pretty(tree1) == pretty(tree2), f"Round-trip failed on: {source}"
```

This checks that `unparse` produces valid code and that the code means the same thing as the original. Include this verification in your test runner.

### Step 3d: Error Reporting

Every `ParseError` must include:
- What token type was expected
- What token type was actually found
- The line and column of the offending token

Example: `ParseError at line 3, col 12: expected SEMICOLON, found RBRACE`

Run the five provided broken programs and five programs you write yourself through the parser. Record the error message for each. In your writeup, show the before and after of the one error message you improved most during development.

**The five provided broken programs:**
1. Missing semicolon: `let x = 5`
2. Unclosed block: `while true { print x;`
3. Bad operator: `let x = 5 + * 3;`
4. Mismatched parenthesis: `print (1 + 2;`
5. Assignment without `let`: `= 5;` (bare equals)

---

## Deliverables

Submit a ZIP containing:
- `parser.py` — the parser module (importing `lexer.py` unchanged; note any lexer bug fixes)
- `ast_nodes.py` — all node dataclasses, the pretty-printer, and the unparser
- `test_parser.py` — the test suite including round-trip verification and error tests
- `test_output.txt` — test run output (all tests passing)
- `readme.md` — approximately one page including: the complete EBNF grammar, the dangling-else policy, and the round-trip verification strategy

Ensure reproducibility by listing your Python version.

---

## Grading Breakdown

| Component | Points |
|-----------|--------|
| Part 1: EBNF Grammar | 30 |
| Part 2: Recursive Descent Parser | 40 |
| Part 3: AST Tooling and Error Reporting | 30 |
| **Total** | **100** |

---

## Reflection Prompts

- Which tier's left-recursion-to-loop rewrite did you have to think hardest about, and what finally made it click?
- Your unparser had to decide where parentheses are necessary. State the rule you implemented in one sentence.
- When you traced the parser calls on the `while` example in step 2d, which recursive call surprised you, and why?
- If collaboration with a buddy was permitted, did you work with a buddy on this assignment? If so, who? If not, do you certify that this submission represents your own original work? Please identify any and all portions of your submission that were not originally written by you.
- Approximately how many hours it took you to finish this assignment (I will not judge you for this at all — I am simply using it to gauge if the assignments are too easy or hard)?
