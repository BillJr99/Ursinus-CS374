---
layout: assignment
permalink: /Assignments/Parser
title: "CS374: Principles of Programming Languages - The Parser and AST"

info:
  coursenum: CS374
  purpose: "To build the second permanent component of your pipeline (a recursive descent parser that turns your Lexer's tokens into an AST) while mastering formal grammars, precedence, and associativity."
  tilt:
    task: "Write a formal EBNF grammar, implement a working parser: recursive descent atop your Lexer (core), a Bison/PLY generator grammar with actions, or a Mini-Notation music parser, by direction, and build an AST with tooling, verification, and positioned error reporting."
    criteria: "Assessed on a grammar that matches the parser exactly, correct precedence and structure at every tier, and programmatic verification of the AST tooling with positioned errors, weighted 30/40/30 across the three parts; the rubric applies equivalently to whichever direction you choose. See the rubric below for the full breakdown."
  points: 100
  goals:
    - To write a formal EBNF grammar for the project language covering expressions, statements, and programs
    - To implement a recursive descent parser for expressions and statements atop the Lexer component
    - To build the full precedence ladder with correct associativity, parentheses, and unary minus
    - To produce an abstract syntax tree of node dataclasses with a pretty-printer and an unparser
    - To verify the round-trip law with property-based testing (Hypothesis), using a recursive AST generator and an automatically shrunk counterexample
    - To report syntax errors with positions, expected tokens, and found tokens
  rubric:
    - weight: 30
      description: "EBNF Grammar and Parsing Theory (Goal 1: write a formal EBNF grammar covering expressions, statements, and programs, and reason about how a bottom-up parser would treat it)"
      preemerging: No grammar is provided, or the grammar is so incomplete that fewer than half the language constructs are covered
      beginning: A grammar is provided but contains ambiguities, missing precedence levels, or structural errors that would cause the parser to behave incorrectly; the theory questions are unanswered or answered without reference to parser actions
      progressing: The grammar covers all constructs and is mostly unambiguous, but the precedence ladder is incomplete (e.g., comparison operators at the wrong level) or associativity is not explicit; most theory questions are answered but one trace or conflict explanation has a mechanical error
      proficient: The grammar is complete, unambiguous, and matches the implemented parser exactly; every precedence level is a separate non-terminal, associativity is enforced by structure, and the dangling-else resolution is stated explicitly, and the parsing theory questions are answered correctly, with the shift-reduce and reduce-reduce conflicts explained in terms of stack actions, a correct hand-executed shift-reduce trace, and the left-recursion contrast stated, demonstrating mastery of formal language specification in both the top-down and bottom-up views
    - weight: 40
      description: "Recursive Descent Parser (Goals 2-3: implement a recursive descent parser with the full precedence ladder and correct associativity)"
      preemerging: The parser fails to run or fails most provided programs due to major structural errors
      beginning: The parser runs but fails on several test programs, e.g., it cannot parse nested constructs, or associativity is wrong at one or more tiers
      progressing: The parser passes the provided test programs but fails on edge cases, e.g., it right-associates `and`/`or` instead of left-associating as the grammar specifies, or it crashes on certain valid inputs
      proficient: A correct parser passes all provided and hidden test programs with correct precedence and associativity at every tier; parenthesized subexpressions, nested blocks, and if-else chains parse correctly; and the parser is built by importing the Lexer unchanged, demonstrating that Goals 2 and 3 are met end-to-end
    - weight: 30
      description: "AST Design, Tooling, and Error Reporting (Goals 4-5: produce a dataclass AST with pretty-printer/unparser, and report errors with positions)"
      preemerging: No AST node classes exist, or the tree structure does not reflect the program's meaning
      beginning: Node classes exist but the pretty-printer or unparser is missing, or error messages lack positions
      progressing: Node classes, pretty-printer, and unparser work for most constructs; errors include positions; but the round-trip property is verified only on fixed examples, not with a property-based generator
      proficient: Node dataclasses (or tagged-union nodes) cover every construct with documented fields; the pretty-printer renders nested structure clearly; the unparser inserts parentheses only where the tree shape requires them; the round-trip property parse(unparse(parse(s))) is verified across the full test suite **and** with a Hypothesis recursive-AST generator, with one shrunk counterexample reported (or a reasoned all-clear with the generator shown); every error states what was expected, what was found, and the line and column, demonstrating that the AST is a complete, self-documenting artifact. (In the Mini-Notation direction, the timed-event evaluator and the Strudel validation table stand in for the unparser and fixed-example round-trip, with the generator applied to the pattern AST, and are assessed equivalently.)
  readings:
    - rtitle: "Recursive Descent Activity"
      rlink: "https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374/gh-pages/_pages/Activities/liascript-recursivedescent.md"
    - rtitle: "Parsing Expressions Activity"
      rlink: "https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374/gh-pages/_pages/Activities/liascript-parsingexpressions.md"
    - rtitle: "Abstract Syntax Trees Activity"
      rlink: "https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374/gh-pages/_pages/Activities/liascript-ast.md"
    - rtitle: "Property-Based Testing Your Language with Hypothesis (Tutorial)"
      rlink: "https://www.billmongan.com/Ursinus-CS374/Tutorials/PropertyBasedTesting"
    - rtitle: "Hypothesis Documentation"
      rlink: "https://hypothesis.readthedocs.io/"

tags:
  - parser
  - ast
  - languages
  - pipeline
  - testing
  - property-based-testing

---

This assignment builds the second permanent component of your pipeline: a parser that consumes tokens and produces an AST. The grammar you write first is the specification; the parser is the implementation of that specification; they must agree exactly. That principle holds in every direction below.

---

## Choose Your Direction

This is one assignment with one deliverable shape (a formal EBNF grammar, a working parser, and AST tooling with positioned errors) built in your choice of **direction**:

- **Recursive descent (the core direction).** Hand-write the parser tier by tier atop your Lexer, exactly as scaffolded in Parts 1-3 below. This is the direction the step-by-step scaffolding assumes, and the component it produces is imported unchanged by the Interpreter assignment.
- **Generator toolchain (Bison or PLY).** Write the same grammar as a Bison `.y` file (or PLY `yacc` module) with semantic actions that build the AST, letting the LALR machinery replace the hand-written ladder. See **[Direction A](#direction-a-generator-toolchain-bison-or-ply)**.
- **Mini-Notation music parser.** Parse a real live-coding pattern notation (the mini-notation shared by TidalCycles and Strudel) into an AST, and give it meaning as timed events validated against the production reference at strudel.cc. See **[Direction B](#direction-b-the-mini-notation-music-parser)**. This is the Parser stop on the [music and live-coding path]({{ site.baseurl }}/Projects/TeamLanguage#the-music-and-live-coding-path).

In every direction, Part 1 (the formal grammar) and the Part 3 requirements (AST design, tooling, positioned errors) apply; the directions substitute Part 2's parsing *vehicle*, and Direction B additionally substitutes the unparser/round-trip portion of Part 3 with a timed-event evaluator and reference validation of equivalent weight. The rubric applies equivalently to all three. If you take Direction A or B, plan with the Interpreter assignment in mind: the interpreter consumes your core pipeline's AST, so keep your recursive-descent skills warm; the worked grammar in Part 1 is your specification either way.

---

## Getting Started

### Environment and Setup

You need Python 3.10+ and your completed Lexer. Copy your `lexer.py` and `token_spec.json` into the project directory and import the Lexer unchanged; if you discover a lexer bug while parsing, fix it and note the fix in your readme. Create the deliverable files up front:

```
lexer.py         # from the Lexer assignment, unchanged
parser.py        # the recursive descent parser
ast_nodes.py     # node dataclasses, pretty-printer, unparser
test_parser.py   # the test suite
```

Confirm the import works before writing any parser code: `python -c "from lexer import Lexer; print(Lexer('let x = 1;').peek())"` should print a `LET` token.

**Reference implementation policy.** A Reference Lexer is released the day this assignment goes out. You may import it in place of your own `lexer.py` by declaring one line in your readme ("This project uses the reference lexer"). Your Lexer assignment grade stands on its own, and using the reference carries no penalty here; the point of this assignment is the parser, and everyone deserves a solid token stream to build on.

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

See the course schedule for the assigned and due dates; this is the most substantial assignment of the semester and has one of the longest windows. If a break falls inside the window, front-load Part 1 so the grammar is drafted while the parsing sessions are fresh. Two pair labs land inside this window and complete pieces of it for you: the **Grammar and Derivations Workshop lab** completes Part 1's grammar work, and the **Parser Skeleton lab** builds the first two ladder tiers (`parse_primary`, `parse_unary`); bring both in directly. Build tier by tier and keep the tests green as you go:

| Checkpoint | You should have |
|------------|----------------|
| On assignment | Grammar drafting begun (Part 1, with the Grammar and Derivations Workshop lab) |
| Grammar lab due | Part 1's grammar complete via the lab; theory questions (Step 1c) drafted |
| Skeleton lab due | `parse_primary` and `parse_unary` working via the lab; expression ladder underway |
| Checkpoint | Expression ladder complete through `parse_expr` with passing tree-shape tests (Step 2b) |
| Checkpoint | Statements, blocks, and the worked `while` example parsing (Steps 2c-2d) |
| Checkpoint | Pretty-printer and unparser working (Steps 3a-3b) |
| Due date | Round-trip verification and error reports complete; readme and ZIP submitted |

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

let_stmt    ::= LET IDENT ( COLON type )? EQ expr SEMICOLON
assign_stmt ::= IDENT EQ expr SEMICOLON
print_stmt  ::= PRINT expr SEMICOLON
if_stmt     ::= IF expr block ( ELSE ( if_stmt | block ) )?
while_stmt  ::= WHILE expr block
fun_stmt    ::= FUN IDENT LPAREN params? RPAREN ( ARROW type )? block
params      ::= param ( COMMA param )*
param       ::= IDENT COLON type
type        ::= IDENT                       // Num, Str, Bool
block       ::= LBRACE stmt* RBRACE

expr        ::= or_expr
or_expr     ::= and_expr ( OR and_expr )*
and_expr    ::= not_expr ( AND not_expr )*
not_expr    ::= NOT not_expr | comparison
comparison  ::= addsub ( ( LT | LE | GT | GE | EQEQ | NEQ ) addsub )?
addsub      ::= muldiv ( ( PLUS | MINUS ) muldiv )*
muldiv      ::= unary ( ( STAR | SLASH ) unary )*
unary       ::= ( MINUS | BANG ) unary | call
call        ::= primary ( LPAREN args? RPAREN )*
args        ::= expr ( COMMA expr )*
primary     ::= INT | FLOAT | STRING | TRUE | FALSE | IDENT
              | LPAREN expr RPAREN
```

**On the optional parts.** The `( COLON type )?` on `let_stmt`, the `fun_stmt` production, and the `call` production exist because the Interpreter assignment's type checker (Part 4) needs syntax for annotations, function definitions, and call sites. Parse them now, even though you will not evaluate function calls until the Interpreter assignment - a parser that produces `FunDef` and `Call` AST nodes today is a parser you do not have to reopen later. If you are short on time, the annotation and function productions are the last thing to implement and the first thing to say so about in your readme.

### Step 1a: Grammar Documentation

In your readme, write the complete grammar. For each non-terminal, add one sentence explaining what it represents and why it is placed at its position in the precedence ladder. For example:

> `addsub` handles `+` and `-`, which bind less tightly than multiplication and division. The `( ... )*` loop enforces left-associativity: `8 - 3 - 2` builds `(8-3)-2 = 3`, not `8-(3-2) = 7`.

### Step 1b: Dangling-Else Resolution

State explicitly in your writeup which `if` a dangling `else` is attached to, and how your grammar enforces that rule. Example: given `if a if b print 1; else print 2;`, does the `else` belong to the inner `if` or the outer? Most languages attach `else` to the nearest `if`; if you follow that convention, explain why the grammar (and parser) do so.

### Step 1c: Parsing Theory Questions

Answer these in your readme; they exercise the Table-Driven and LR Parsing session's material on the same grammar you just wrote, and they are graded within Part 1's rubric row. Your recursive descent parser is top-down; these questions make you reason about what the bottom-up alternative would do with your language:

1. **The dangling else, bottom-up.** An LR parser generator reports a **shift-reduce conflict** at the token `ELSE` for a grammar like yours. Explain, in terms of the parser's stack and the two available actions, what the conflict *is*: what does shifting choose, and what does reducing choose? Then give the two standard resolutions (a precedence/`%prec`-style declaration favoring shift, or grammar surgery into `matched`/`unmatched` productions) and state which one your grammar's Step 1b convention corresponds to.
2. **Manufacture a reduce-reduce conflict.** Consider adding this pair of productions to your grammar: `const_stmt ::= LET IDENT EQ INT SEMICOLON` alongside the existing `let_stmt ::= LET IDENT EQ expr SEMICOLON`. Explain why an LR parser hits a **reduce-reduce conflict** on input like `let x = 42;` (which completed right-hand side matches the stack?), and restructure the productions to eliminate the conflict while keeping both language features.
3. **One shift-reduce trace.** Using the toy grammar `E ::= E + T | T` and `T ::= INT`, execute the shift-reduce parse of `1 + 2 + 3` as a stack-input-action table (the format from the Table-Driven and LR Parsing session; expect about ten rows). Note the step where the parser reduces `E + T` to `E` *before* shifting the second `+`, and state which associativity that choice enforces.
4. **Left recursion, both worlds.** The toy grammar above is left-recursive. State in one sentence each: why that grammar would send your recursive descent parser into an infinite loop, and why the LR parser handles it without complaint.

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

**`parse_primary()`**: returns a `Num`, `Var`, `Str`, `BoolLit`, or the result of a parenthesized `parse_expr()`. Raise `ParseError` on any other token.

**`parse_unary()`**: if the next token is `MINUS`, consume it and recursively call `parse_unary()`, wrapping in `UnaryOp("-", ...)`. Verify that `--x` builds `UnaryOp("-", UnaryOp("-", Var("x")))`.

**`parse_muldiv()`**: parse one `unary`, then loop while the next token is `STAR` or `SLASH`, consuming the operator and another `unary`, and replacing the left side with `BinOp(op, left, right)`. Verify `8 / 4 / 2` builds `BinOp("/", BinOp("/", Num(8), Num(4)), Num(2))`.

**`parse_addsub()`**: same left-fold pattern over `PLUS` and `MINUS` above `muldiv`. Verify `2 + 3 * 4` builds `BinOp("+", Num(2), BinOp("*", Num(3), Num(4)))`.

**`parse_comparison()`**: parse one `addsub`; if the next token is a comparison operator, consume it and one more `addsub` to form a `BinOp`. Comparisons are non-associative (no chaining); attempting `a < b < c` is a syntax error.

**`parse_not()`**: handle unary `NOT`, then call `parse_comparison()`.

**`parse_and()`**: left-fold `not` expressions over `AND`.

**`parse_or()`**: left-fold `and` expressions over `OR`. Verify `a or b and c` builds `BinOp("or", Var("a"), BinOp("and", Var("b"), Var("c")))`.

**`parse_expr()`**: delegates to `parse_or()`.

### Step 2c: Statements and Blocks

**`parse_let_stmt()`**: consumes `LET`, then expects `IDENT`, `EQ`, an expression, and `SEMICOLON` using `lexer.expect()`. Returns a `Let` node.

**`parse_assign_stmt()`**: consumes `IDENT` and `EQ`, then an expression and `SEMICOLON`. Returns an `Assign` node. (How will you distinguish assignment from an expression statement that starts with an identifier? Document your lookahead strategy.)

**`parse_print_stmt()`**: `PRINT`, expression, `SEMICOLON`. Returns `Print`.

**`parse_block()`**: `LBRACE`, then zero or more statements, then `RBRACE`. Returns `Block`. Each statement is dispatched via `parse_stmt()`.

**`parse_if_stmt()`**: `IF`, expression (the condition), block. Then, if the next token is `ELSE`, consume it. If the token after `ELSE` is `IF`, recursively call `parse_if_stmt()` for the `else-if` branch; otherwise call `parse_block()`. Returns `If`.

**`parse_while_stmt()`**: `WHILE`, expression, block. Returns `While`.

**`parse_program()`**: parse statements until `EOF`. Returns `Program`.

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

Example: `unparse(BinOp("+", Num(2), BinOp("*", Num(3), Num(4))))` -> `"2 + 3 * 4"` (no parentheses needed).  
Example: `unparse(BinOp("*", Num(2), BinOp("+", Num(3), Num(4))))` -> `"2 * (3 + 4)"` (parentheses required).

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

### Step 3e: Property-Based Testing with Hypothesis

Your fixed test suite in Step 3c checks the round-trip law on the handful of programs *you thought to write*. The interesting bugs live in the programs you did not think of: a unary minus applied to a parenthesized subtraction, an operator at exactly the precedence boundary, a deeply right-nested chain. **[Property-based testing](https://hypothesis.readthedocs.io/)** finds those for you: instead of writing examples, you write a *generator* of random ASTs and assert that the law holds for **all** of them; when it fails, Hypothesis automatically **shrinks** the counterexample to the smallest tree that still breaks it.

This is a required step. It replaces the busywork of hand-enumerating more round-trip cases with a generator that enumerates them for you: the same verification effort, far more coverage. The full walkthrough is in the [Property-Based Testing tutorial]({{ site.baseurl }}/Tutorials/PropertyBasedTesting).

1. **Install Hypothesis:** `uv add hypothesis` (or `pip install hypothesis`).
2. **Write an AST generator** using `hypothesis.strategies.recursive`, so that trees can nest to arbitrary depth. Sketch:

   ```python
   from hypothesis import given, strategies as st

   # leaves: numbers and simple identifiers
   leaves = st.one_of(
       st.integers(min_value=0, max_value=999).map(Num),
       st.sampled_from(["x", "y", "z"]).map(Var),
   )
   # recursive: binary operators over sub-expressions
   exprs = st.recursive(
       leaves,
       lambda kids: st.builds(BinOp,
           st.sampled_from(["+", "-", "*", "/"]), kids, kids),
       max_leaves=25,
   )

   @given(exprs)
   def test_round_trip(tree):
       assert parse(unparse(tree)) == tree   # structural equality on your AST
   ```
3. **Run it** (`pytest` discovers `@given` tests automatically). When it fails (and on a first parser it usually will) Hypothesis prints the minimal failing tree. Fix the bug (commonly a missing parenthesization rule in `unparse`, or a precedence/associativity error in `parse`), and re-run until it passes.
4. **Report one shrunk counterexample you fixed** in your `readme.md`: the minimal tree Hypothesis found, the one-sentence root cause, and the fix. This is the deliverable: evidence that the property found a real bug your fixed tests missed (or a reasoned statement of why your parser was already correct, with the generator shown).

> **Note for Direction B (Mini-Notation):** apply the same idea to your pattern AST: generate random nestings of sequences, alternations, and Euclidean rhythms, and assert your tree printer round-trips (or that re-parsing your printed form yields the same event list). The reference-validation table stands in for the fixed-example half; the Hypothesis generator stands in for this half.

---

## Direction A: Generator Toolchain (Bison or PLY)

In this direction the LALR machinery of Bison (C) or PLY (Python) replaces the hand-written recursive descent ladder. You still write the EBNF grammar of Part 1 first (it remains the contract) and you still deliver the AST tooling and positioned errors of Part 3. What changes is Part 2's vehicle: instead of one function per tier, you write grammar productions with semantic actions, and instead of encoding precedence in the ladder's structure, you declare it.

**A.1; Grammar file and declarations.** Write `parser.y` (Bison) or the PLY grammar module for the full language of Part 1. Declare a `%union` (Bison) with fields for numeric values, strings, and your AST node pointer, and type your tokens accordingly (`%token <dval> NUMBER`, `%token <sval> IDENT STRING`, and so on). Declare operator associativity and precedence with `%left`, `%right`, and `%nonassoc`: comparisons are `%nonassoc` to enforce the same no-chaining rule the core direction's grammar encodes structurally.

**A.2 (Conflict-free productions.** Write the productions bottom-up, tightest binding first), `primary` -> `unary` -> `muldiv` -> `addsub` -> `comparison` -> `and` -> `or`; plus the statement, block, and program rules. Your precedence declarations must resolve every shift-reduce conflict: run `bison -v` (or inspect PLY's `parser.out`) and confirm **zero unresolved conflicts**. The dangling-else resolution of Step 1b still applies: document how the generator resolves it (the default shift is exactly "else binds to the nearest if") and cite the relevant state in the `.output`/`parser.out` automaton in your readme.

**A.3, AST-building actions.** Each production's semantic action builds exactly one AST node and nothing more: no evaluation inside the parser. In Python/PLY, build the same dataclass nodes from Step 2a; in C, use a tagged-union node struct with one constructor function per node type. The syntax/semantics boundary is part of the grade.

**A.4, Verification.** The same tree-shape tests apply: `2 + 3 * 4` must build the multiplication under the addition, `8 / 4 / 2` must left-associate, and the worked `while` example of Step 2d must produce the same abbreviated tree. Part 3, pretty-printer, unparser, round-trip verification, and positioned `ParseError`s (use the token's line/column from your lexer), applies unchanged.

This direction pairs naturally with the Lexer assignment's generator-toolchain direction (a Flex/PLY scanner feeding this grammar), but the choices are independent: a PLY grammar can sit atop your hand-rolled Lexer through a small token adapter.

---

## Direction B: The Mini-Notation Music Parser

In this direction you parse a production language: the **mini-notation** shared by TidalCycles and Strudel, in which `bd sn` is a two-step drum pattern, `bd*2` doubles, `<sn cp>` alternates per cycle, and `bd(3,8)` distributes three onsets among eight steps. You will grow the in-class flex/yacc subset (provided in the course repository under `files/examples/mininote/`) toward the real language (extending the lexer, the grammar, the AST, and the evaluator in concert, which is the authentic experience of DSL maintenance: a new construct is never just a parser change. The default toolchain is C with flex and bison, as in class; PLY is welcome, and its `parser.out` stands in for bison's `.output` automaton wherever cited below. This direction never requires audio: the semantics maps patterns to printable timed events `(value, begin, end)` over the cycle $[0,1)$, which you read, diff, and test as plain text.

Do **not** transcribe Strudel's own parser; derive the grammar and semantics yourself, then use Strudel strictly as an *oracle* to test against.

> **Scope note.** Direction B is the most ambitious direction of the three (budget roughly 25-35 hours end to end) and it is recommended mainly for students planning the music direction of the team project. A **reduced-scope variant earns full credit**: B.2 (SLOW and DEGRADE) and B.3 (alternation `<a b c>`, with its displayed equation) are required; B.4 (Euclidean rhythms) and B.5 (polymeter) become optional extensions beyond full credit. If you take the reduced scope, say so in your readme and build your B.6 validation table from the features you implemented.

**B.1 (Grammar first (Part 1 equivalent).** Write the complete EBNF grammar for your extended mini-notation) sequences, rests, groups, `*`, `/`, `?`, plus the three constructs below: with one sentence per non-terminal explaining its placement. The grammar must remain conflict-free LALR(1); your readme cites specific states from the `.output` automaton to show where each new construct lives.

**B.2: Complete the scaffolded cases.** The in-class evaluator leaves `SLOW` and `DEGRADE` unimplemented. `slow n` stretches its child across $$n$$ cycles, which forces a design change: the evaluator signature carries no cycle number, so extend it (or derive the cycle from the span) and document your choice. Gate `DEGRADE` on `rand() < RAND_MAX / 2` with `srand(42)` called exactly once, so grading is reproducible. Transcript: `bd/2 sn` on cycles 0 and 1, with a sentence explaining why they differ, and three identical consecutive runs of `hh*8?`.

**B.3; Alternation.** `<a b c>` plays element $$\lfloor c \rfloor \bmod k$$ on cycle $$c$$, occupying the whole span:

$$
\mathcal{E}[\![\, \texttt{ALT}(c_1, \ldots, c_k) \,]\!](t_0, t_1, c) \;=\; \mathcal{E}[\![\, c_{(c \bmod k) + 1} \,]\!](t_0, t_1, c)
$$

Add `LANGLE`/`RANGLE` tokens, an `atom` production, an `N_ALT` node, and the evaluator case. Transcript: `bd <sn cp hh>` across cycles 0-3, demonstrating rotation and wraparound. If you introduce a conflict along the way, keep the broken `.output` excerpt: diagnosing it is worth describing in your readme.

**B.4; Euclidean rhythms.** `bd(3,8)` distributes $$k = 3$$ onsets as evenly as possible among $$n = 8$$ steps: Toussaint showed these onset sets reproduce rhythm timelines from musical traditions worldwide ($$E(3,8)$$ is the Cuban tresillo). An onset occurs at step $$i$$ exactly when

$$
(i \cdot k) \bmod n \;<\; k
$$

Verify the rule by hand for $$E(3,8)$$ (steps 0, 3, 6 -> `x..x..x.`) and one other $$(k, n)$$ pair before implementing, and include the hand-verification in your readme with a two-or-three-sentence argument for why the rule yields exactly $$k$$ onsets. Syntactically, Euclid is a postfix modifier among the `term` productions: `term LPAREN NUMBER COMMA NUMBER RPAREN`. Transcripts: `bd(3,8)` and `bd(5,8)`, each matching its hand-computed onset set.

**B.5: Polymeter.** `{a b, c d e}` runs its subsequences simultaneously at a common step rate, so different lengths drift and realign; `{a b, c d e}%4` fixes four steps per cycle. **Specify the semantics yourself, precisely, in displayed-equation style before writing code**: the specification is a graded artifact, and discovering your first draft was ambiguous is an intended outcome. Use strudel.cc to interrogate the corner cases (what happens on cycle 1? which subsequence sets the default step count?). Add the brace/comma/percent tokens, the productions, an `N_POLY` node, and your specification's evaluator case. Transcript: `{bd sn, hh hh hh}` across cycles 0-2, annotated to show drift and realignment.

**B.6, Validation against the reference (Part 3 equivalent).** In place of the unparser and round-trip verification, deliver a tree printer (the pretty-printer requirement, unchanged), location-prefixed parse errors, and a **validation table** of at least eight patterns collectively exercising every feature, including at least two that nest new constructs inside one another (`<bd(3,8) sn>`, `{bd <sn cp>, hh*2}`). For each pattern, record your evaluator's event list against the spans Strudel highlights at strudel.cc, and investigate every discrepancy to a conclusion: grammar difference, semantic difference, or bug (yours or, occasionally and delightfully, theirs).

**Direction B deliverables** (same ZIP-and-readme shape): complete source (`.l`, `.y`, `.c`, `.h`, `Makefile`, or the PLY equivalents), the generated `.output`/`parser.out` automaton, a test transcript regenerable via `make test`, and a readme containing the EBNF grammar, the hand-derivations, the polymeter specification, and the validation table. Fix random seeds and list toolchain versions (`flex --version`, `bison --version`, `gcc --version`) for reproducibility.

Two useful resources for this direction: Levine's *flex & bison* (O'Reilly, 2009), particularly the conflict-diagnosis chapters, and Toussaint's "The Euclidean Algorithm Generates Traditional Musical Rhythms" (*BRIDGES* 2005).

---

## Deliverables

Submit a ZIP containing:
- `parser.py`: the parser module (importing `lexer.py` unchanged; note any lexer bug fixes)
- `ast_nodes.py`: all node dataclasses, the pretty-printer, and the unparser
- `test_parser.py`: the test suite including fixed-example round-trip verification, the Hypothesis property-based round-trip test with its AST generator, and error tests
- `test_output.txt`: test run output (all tests passing, including the Hypothesis test)
- `readme.md`; approximately one page including: the complete EBNF grammar, the dangling-else policy, the round-trip verification strategy, and the one shrunk Hypothesis counterexample you fixed (or a reasoned all-clear with the generator shown)

Ensure reproducibility by listing your Python version.

**Direction A** swaps the vehicle inside the same structure: the `.y` grammar (plus `Makefile`) or PLY module in place of the hand-written `parser.py`, the automaton file demonstrating zero conflicts, and a readme that additionally documents the precedence declarations and the dangling-else state. **Direction B**'s deliverable list appears at the end of its section above. In every direction the readme leads with the complete EBNF grammar.

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

- Which tier's left-recursion-to-loop rewrite did you have to think hardest about, and what finally made it click? (Direction A: which precedence declaration did the same job, and how did you confirm it in the automaton? Direction B: which construct's grammar placement did you have to think hardest about?)
- Your unparser had to decide where parentheses are necessary. State the rule you implemented in one sentence. (Direction B: your evaluator had to decide how cycle information reaches constructs that need it; state your design in one sentence.)
- When you traced the parser calls on the `while` example in step 2d, which recursive call surprised you, and why? (Directions A and B: which reduction in the automaton surprised you, and why?)
- If you took a direction beyond the core: what did the grammar-first discipline reveal that jumping straight to code would have hidden?
- Direction B only: Toussaint's Euclidean rhythms emerged from a scheduling algorithm and turned out to describe music made by humans across centuries and continents. What does this suggest about the relationship between formal structure and cultural practice, and about who is credited when an algorithm formalizes existing human knowledge?
- If collaboration with a buddy was permitted, did you work with a buddy on this assignment? If so, who? If not, do you certify that this submission represents your own original work? Please identify any and all portions of your submission that were not originally written by you.
- AI disclosure: list any generative-AI tools you used, for what, and how you verified the results (or state 'none').
- Approximately how many hours it took you to finish this assignment (I will not judge you for this at all; I am simply using it to gauge if the assignments are too easy or hard)?
