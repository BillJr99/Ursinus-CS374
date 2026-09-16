---
layout: assignment
permalink: /Assignments/Parser
title: "CS374: Principles of Programming Languages - The Parser and AST"

info:
  coursenum: CS374
  purpose: "To build the second permanent component of your pipeline (a recursive descent parser that turns your Lexer's tokens into an AST) while learning formal grammars, precedence, and associativity."
  tilt:
    task: "Write a formal EBNF grammar; implement a working parser in your chosen direction (recursive descent atop your Lexer as the core direction, a Bison/PLY generator grammar with actions, or a Mini-Notation music parser); and build an AST with tooling, verification, and positioned error reporting."
    criteria: "I grade this on a grammar that matches the parser exactly, correct precedence and structure at every tier, and programmatic verification of the AST tooling with positioned errors.  The rubric applies equivalently to whichever direction you choose.  Please read the rubric below for the details."
  points: 100
  goals:
    - To write a formal EBNF grammar for the project language covering expressions, statements, and programs
    - To implement a recursive descent parser for expressions and statements atop the Lexer component
    - To build the full precedence ladder with correct associativity, parentheses, and unary minus
    - To produce an abstract syntax tree of node dataclasses with a pretty-printer and an unparser
    - To verify the round-trip law with property-based testing (Hypothesis), using a recursive AST generator and an automatically shrunk counterexample
    - To report syntax errors with positions, expected tokens, and found tokens
  rubric:
    - weight: 10
      description: "Part 0: Before You Start - Abstract Syntax Trees"
      preemerging: No AST is drawn and no node types are designed
      beginning: A tree is drawn but it is a parse tree rather than an AST, or no node types are designed
      progressing: The AST for 3 + 4 * 5 is correct and node types are sketched, but the write-up does not say what the AST discarded, or the node types omit one of the two required constructs
      proficient: The AST (not the parse tree) for 3 + 4 * 5 is drawn with precedence correct, and one sentence names what it threw away that the parse tree kept; node types for if/else and for function calls are designed concretely; and the one field you added out of uncertainty is marked as such
    - weight: 27
      description: "EBNF Grammar and Parsing Theory (Goal 1: write a formal EBNF grammar covering expressions, statements, and programs, and reason about how a bottom-up parser would treat it)"
      preemerging: No grammar is provided, or the grammar is so incomplete that fewer than half the language constructs are covered
      beginning: A grammar is provided but contains ambiguities, missing precedence levels, or structural errors that would make the parser behave incorrectly; the theory questions are unanswered or answered without reference to parser actions
      progressing: The grammar covers all constructs and is mostly unambiguous, but the precedence ladder is incomplete (e.g., comparison operators at the wrong level) or associativity is not explicit; most theory questions are answered but one trace or conflict explanation has a mechanical error
      proficient: The grammar is complete, unambiguous, and matches the implemented parser exactly; every precedence level is a separate non-terminal, associativity is enforced by structure, and the dangling-else resolution is stated explicitly; the parsing theory questions are answered correctly, with the shift-reduce and reduce-reduce conflicts explained in terms of stack actions, a correct hand-executed shift-reduce trace, and the left-recursion contrast stated, showing command of formal language specification in both the top-down and bottom-up views
    - weight: 36
      description: "Recursive Descent Parser (Goals 2-3: implement a recursive descent parser with the full precedence ladder and correct associativity)"
      preemerging: The parser fails to run or fails most provided programs because of major structural errors
      beginning: The parser runs but fails on several test programs, e.g., it cannot parse nested constructs, or associativity is wrong at one or more tiers
      progressing: The parser passes the provided test programs but fails on edge cases, e.g., it right-associates `and`/`or` instead of left-associating as the grammar specifies, or it crashes on certain valid inputs
      proficient: A correct parser passes all provided and hidden test programs with correct precedence and associativity at every tier; parenthesized subexpressions, nested blocks, and if-else chains parse correctly; and the parser is built by importing the Lexer unchanged, showing that Goals 2 and 3 are met end-to-end
    - weight: 27
      description: "AST Design, Tooling, and Error Reporting (Goals 4-5: produce a dataclass AST with pretty-printer/unparser, and report errors with positions)"
      preemerging: No AST node classes exist, or the tree structure does not reflect the program's meaning
      beginning: Node classes exist but the pretty-printer or unparser is missing, or error messages lack positions
      progressing: Node classes, pretty-printer, and unparser work for most constructs; errors include positions; but the round-trip property is verified only on fixed examples, not with a property-based generator
      proficient: Node dataclasses (or tagged-union nodes) cover every construct with documented fields; the pretty-printer renders nested structure clearly; the unparser inserts parentheses only where the tree shape requires them; the round-trip property parse(unparse(parse(s))) is verified across the full test suite **and** with a Hypothesis recursive-AST generator, with one shrunk counterexample reported (or a reasoned all-clear with the generator shown); every error states what was expected, what was found, and the line and column, showing that the AST is a complete, self-documenting artifact. (In the Mini-Notation direction, the timed-event evaluator and the Strudel validation table stand in for the unparser and fixed-example round-trip, with the generator applied to the pattern AST, and are assessed equivalently.)
  readings:
    - rtitle: "Recursive Descent Activity"
      rlink: "Activities/liascript-recursivedescent.md"
      liapage: true
    - rtitle: "Parsing Expressions Activity"
      rlink: "Activities/liascript-parsingexpressions.md"
      liapage: true
    - rtitle: "Abstract Syntax Trees Activity"
      rlink: "Activities/liascript-ast.md"
      liapage: true
    - rtitle: "Property-Based Testing Your Language with Hypothesis (Tutorial)"
      rlink: "../Tutorials/PropertyBasedTesting"
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

In this assignment you build the parser, the second permanent component of your language pipeline.  The parser reads the tokens your Lexer produces and builds an abstract syntax tree (AST): a tree that records the structure of the program and drops everything else.  You write the grammar first, because the grammar is the specification and the parser is its implementation, and the two must agree exactly in every direction below.  You leave with a `parser.py` that the Interpreter assignment imports unchanged, a pretty-printer and an unparser over your AST, a property-based test that finds bugs in programs you did not think to write, and error messages that name the line and column of every mistake.

---

## Part 0: Before You Start - Abstract Syntax Trees

Do this part before you write any parser code; you need pencil and paper and about twenty minutes.  A parse tree records every grammar rule the parser applied, including the parentheses and every intermediate non-terminal.  An AST keeps only the structure the rest of the language needs, and choosing what to keep is a design decision: you are choosing what the rest of your implementation never has to think about again.

> **Do this.**
> 1. Draw the AST, not the parse tree, for `3 + 4 * 5`.  Get the precedence right: the multiplication sits below the addition.
> 2. Write one sentence saying what the AST *threw away* that the parse tree kept.
> 3. Design the node types you would use to represent `if`/`else` and function calls in your team's language, as Python dataclasses or as a `match`/`case` shape.
> 4. Mark the one field you added because you were not sure you could do without it.

> **Bring to class.** Your drawing, your one sentence, and your node types with the uncertain field marked.  Part 3 builds tooling over these nodes, so a field you cannot justify now is one you will still be maintaining at the end of the term.

---

## Choose Your Direction

This is one assignment with one deliverable shape: a formal EBNF grammar (Extended Backus-Naur Form, the notation defined in Part 1), a working parser, and AST tooling with positioned errors.  You build it in your choice of direction.

| Direction | What you build | What you need | Pick this if |
|-----------|----------------|---------------|--------------|
| **Core: hand-rolled recursive descent** | One parsing function per grammar tier, written by hand on top of your Lexer, as Parts 1-3 scaffold it | Python 3.10+ and your `lexer.py` (or the reference lexer) | You want the path the step-by-step instructions assume, and the parser the Interpreter assignment imports unchanged |
| **Direction A: generator toolchain (Bison or PLY)** | The same grammar as a Bison `.y` file or a PLY `yacc` module, with semantic actions that build the AST; the LALR machinery replaces the hand-written ladder | Bison and a C compiler, or PLY in Python | You want to declare precedence instead of encoding it in structure, and to read the automaton the generator produces |
| **Direction B: Mini-Notation music parser** | A parser for the mini-notation shared by TidalCycles and Strudel, an evaluator that turns patterns into timed events, and a validation table against the production reference at strudel.cc | flex, bison, and gcc (or PLY), plus the in-class starter in `files/examples/mininote/` | You plan the music direction of the team project and can budget 25-35 hours |

Direction A is described in [its own section](#direction-a-generator-toolchain-bison-or-ply) below, and so is [Direction B](#direction-b-the-mini-notation-music-parser), which is the Parser stop on the [music and live-coding path]({{ site.baseurl }}/Projects/TeamLanguage#the-music-and-live-coding-path).  Part 1 (the formal grammar) and the Part 3 requirements (AST design, tooling, positioned errors) apply in every direction; the directions replace only Part 2's parsing *vehicle*.  Direction B also replaces the unparser and round-trip portion of Part 3 with a timed-event evaluator and reference validation of equal weight.  The rubric applies the same way to all three.  If you take Direction A or B, keep your recursive-descent skills warm: the Interpreter assignment consumes your core pipeline's AST.

---

## Before You Start

You need Python 3.10 or newer (run `python3 --version` to confirm), your completed Lexer (`lexer.py` and `token_spec.json`) or the reference lexer described below, a project folder named `cs374-parser/` where all of this assignment's work lives, and an editor such as VS Code.  If the terminal is new to you, read the [dev environment page]({{ site.baseurl }}/Tutorials/DevEnvironment) and the [shell primer]({{ site.baseurl }}/Tutorials/ShellForLanguageDev) first.  Create the deliverable files up front so each part has a home:

```text
cs374-parser/
  lexer.py         # from the Lexer assignment, unchanged
  token_spec.json  # from the Lexer assignment
  parser.py        # the recursive descent parser
  ast_nodes.py     # node dataclasses, pretty-printer, unparser
  test_parser.py   # the test suite
  readme.md        # grammar, theory answers, and write-up
```

Copy `lexer.py` and `token_spec.json` from your Lexer project and import the Lexer unchanged.  If you find a lexer bug while parsing, fix it and note the fix in your readme.  Confirm the import works before you write any parser code.  From inside `cs374-parser/`, run:

```bash
python3 -c "from lexer import Lexer; print(Lexer('let x = 1;').peek())"
```

```text
Token(type='LET', value='let', line=1, col=1, decoded=None)
```

**Reference lexer.**  That line is the reference lexer's output; your own `Token` may print with different field names, but its type must be `LET`.  (If Python reports `ModuleNotFoundError: No module named 'lexer'`, you are not running from the folder that holds `lexer.py`.)  The [reference lexer]({{ site.baseurl }}/files/reference/reference-lexer.zip) is released the day this assignment goes out, and you may unzip it into `cs374-parser/` in place of your own `lexer.py`.  If you do, declare it in one line in your readme ("This submission uses the reference lexer"); it carries no penalty, and your Lexer assignment grade stands on its own.

> **Time budget.** Part 0 takes about twenty minutes with pencil and paper.  The rest is the most substantial assignment of the semester and has one of the longest windows, and two pair labs inside that window complete pieces of it for you.  Direction B budgets roughly 25-35 hours end to end; the core direction is smaller but still fills the window, so start Part 1 the week the assignment goes out.

### Your First 30 Minutes

1. Draft the expression tiers of your grammar on paper (Part 1 gives you the ladder).
2. Copy the `Num` and `Var` dataclasses from Step 2a into `ast_nodes.py`.
3. Copy the `ParseError` class and the `parse_primary()` skeleton from Step 2a into `parser.py`, and fill in the `INT` and `IDENT` cases.
4. Create a scratch file `try_primary.py` in `cs374-parser/` containing `from lexer import Lexer`, `from parser import parse_primary`, and `print(parse_primary(Lexer("42")))`, then run `python3 try_primary.py`.  You should see `Num(value=42, line=1)`.
5. Change `"42"` to `"x"` and you should see a `Var`; change it to `";"` and you should see a `ParseError` traceback.  That is the pattern every other tier repeats: look at `lexer.peek()`, decide, consume with `lexer.advance()` or `lexer.expect()`, and return a node.

### Suggested Pacing

See the course schedule for the assigned and due dates.  If a break falls inside the window, front-load Part 1 so the grammar is drafted while the parsing sessions are fresh.  Two pair labs land inside this window and complete pieces of it for you: the **Grammar and Derivations Workshop lab** completes Part 1's grammar work, and the Parser Skeleton lab builds the first two ladder tiers (`parse_primary`, `parse_unary`).  Bring both in directly, then build tier by tier and keep the tests green as you go:

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

## Part 1: EBNF Grammar

Write the complete EBNF grammar for your language before you write a line of parser code.  A grammar is a set of rules that says which token sequences form a valid program; a non-terminal is a named rule in the grammar, and a terminal is a token from your Lexer, written in `ALL_CAPS` or as a quoted string.  Notation: `*` = zero or more, `+` = one or more, `?` = zero or one, `|` = alternation, `( )` = grouping.  You will include the grammar verbatim in your readme, where it is the contract between the grammar document and the implementation.  It must define at least the following non-terminals, in precedence order from loosest to tightest:

```ebnf
program     ::= stmt* EOF
stmt        ::= let_stmt | assign_stmt | print_stmt
              | if_stmt | while_stmt | block

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

> **Why this matters.** The `( COLON type )?` on `let_stmt`, the `fun_stmt` production, and the `call` production exist because the Interpreter assignment's type checker (Part 4) needs syntax for annotations, function definitions, and call sites.  You will not evaluate function calls until then, but a parser that produces `FunDef` and `Call` AST nodes today is a parser you do not have to reopen later.  If you are short on time, implement these productions last, and say so in your readme first.

### Step 1a: Document the Grammar

> **Do this.**
> 1. Open `readme.md` and write the complete grammar under a heading of its own.
> 2. Under each non-terminal, add one sentence that says what it represents and why it sits where it does in the precedence ladder.  For example: `addsub` handles `+` and `-`, which bind less tightly than multiplication and division, and its `( ... )*` loop enforces left-associativity, so `8 - 3 - 2` builds `(8-3)-2 = 3`, not `8-(3-2) = 7`.

### Step 1b: Resolve the Dangling Else

A dangling `else` is an `else` that could attach to more than one `if`.  Given `if a if b print 1; else print 2;`, does the `else` belong to the inner `if` or the outer?  Most languages attach it to the nearest `if`.

> **Do this.**
> 1. State explicitly in your readme which `if` the `else` attaches to.
> 2. Explain how your grammar (and the parser) enforce that rule.

### Step 1c: Answer the Parsing Theory Questions

These questions exercise the Table-Driven and LR Parsing session's material on the grammar you just wrote, and they are graded within Part 1's rubric row.  Your recursive descent parser is top-down: it starts from `program` and works down to tokens.  An LR parser is bottom-up: it keeps a stack, *shifts* the next token onto the stack, and *reduces* the top of the stack to a non-terminal when a right-hand side is complete.

> **Do this.** Answer all four questions in your readme, under a heading of their own.

1.  The dangling else, bottom-up.  An LR parser generator reports a shift-reduce conflict at the token `ELSE` for a grammar like yours.  Explain, in terms of the parser's stack and the two available actions, what the conflict *is*: what does shifting choose, and what does reducing choose?  Then give the two standard resolutions (a precedence/`%prec`-style declaration favoring shift, or grammar surgery into `matched`/`unmatched` productions) and state which one your grammar's Step 1b convention corresponds to.
2.  Manufacture a reduce-reduce conflict.  Consider adding this pair of productions to your grammar: `const_stmt ::= LET IDENT EQ INT SEMICOLON` alongside the existing `let_stmt ::= LET IDENT EQ expr SEMICOLON`.  Explain why an LR parser hits a reduce-reduce conflict on input like `let x = 42;` (which completed right-hand side matches the stack?), and restructure the productions to eliminate the conflict while keeping both language features.
3.  One shift-reduce trace.  Using the toy grammar `E ::= E + T | T` and `T ::= INT`, execute the shift-reduce parse of `1 + 2 + 3` as a stack-input-action table (the format from the Table-Driven and LR Parsing session; expect about ten rows).  Note the step where the parser reduces `E + T` to `E` *before* shifting the second `+`, and state which associativity that choice enforces.
4.  Left recursion, both worlds.  The toy grammar above is left-recursive.  State in one sentence each: why that grammar would send your recursive descent parser into an infinite loop, and why the LR parser handles it without complaint.

---

## Part 2: Recursive Descent Parser

### Step 2a: Define the AST Nodes and Start the Parser

Define the node classes before you write any parsing functions.  Python `dataclasses.dataclass` writes `__init__` and `__repr__` for you.

> **Do this.**
> 1. Open `ast_nodes.py` and paste in the dataclasses below, then add `Assign` and `Print` on the `Let` pattern.
> 2. Add `Str`, `BoolLit`, and `LogicOp` if your design uses them separately from `BinOp` and `UnaryOp`, and add `FunDef` and `Call` nodes for the `fun_stmt` and `call` productions, with fields you can justify.
> 3. Open `parser.py` and paste in the skeleton that follows the dataclasses.  Every parsing function takes the lexer and returns one node, and `ParseError` carries the position of the token that went wrong (Step 3d makes that a requirement).

```python
from dataclasses import dataclass, field
from typing import List, Any

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

# TODO: Assign(name, value) and Print(value)

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

> **Watch out.** A dataclass compares every field in `==`, including `line`.  The tree-shape tests below write `Num(8)` with the default `line=0`, while a parsed node carries `line=1`.  To make those comparisons pass (you will want this again for the Hypothesis test in Step 3e), declare the position field as `line: int = field(default=0, compare=False)` so equality ignores it.

```python
# parser.py
from lexer import Lexer
from ast_nodes import (Num, Var, BinOp, UnaryOp, Let, Assign, Print,
                       Block, If, While, Program)

class ParseError(Exception):
    def __init__(self, message: str, line: int = 0, col: int = 0):
        super().__init__(f"ParseError at line {line}, col {col}: {message}")
        self.line = line
        self.col = col

def parse_primary(lexer: Lexer):
    tok = lexer.peek()
    if tok.type == "INT":
        lexer.advance()
        return Num(value=int(tok.value), line=tok.line)
    # TODO: FLOAT, STRING, TRUE, FALSE, IDENT, and LPAREN (consume it, call parse_expr, expect RPAREN)
    raise ParseError(f"expected an expression, found {tok.type}", tok.line, tok.col)

def parse_unary(lexer: Lexer):
    # TODO: if the next token is MINUS (or BANG), consume it, recurse, and wrap the result in UnaryOp
    return parse_primary(lexer)

def parse_muldiv(lexer: Lexer):
    left = parse_unary(lexer)
    while lexer.peek().type in ("STAR", "SLASH"):
        op = lexer.advance()
        right = parse_unary(lexer)
        left = BinOp(op.value, left, right)   # the left-fold: left grows, right is one operand
    return left

# TODO: parse_addsub ... parse_expr (Step 2b), then the statement functions and parse_program (Step 2c)

def parse(source: str) -> Program:
    """Entry point used by the tests and by Part 3."""
    return parse_program(Lexer(source))
```

### Step 2b: Build the Expression Ladder (test after every tier)

Implement each function below in order.  Each tier parses the tier below it and then handles its own operators, and most tiers use the *left-fold* pattern of `parse_muldiv`: parse one operand, then loop while the next token is one of this tier's operators, consuming the operator, parsing one more operand, and replacing the left side with `BinOp(op, left, right)`.  The loop is what makes the operator left-associative.

- `parse_primary()`: returns a `Num`, `Var`, `Str`, `BoolLit`, or the result of a parenthesized `parse_expr()`.  Raise `ParseError` on any other token.
- `parse_unary()`: if the next token is `MINUS`, consume it and recursively call `parse_unary()`, wrapping the result in `UnaryOp("-", ...)`.  Verify that `--x` builds `UnaryOp("-", UnaryOp("-", Var("x")))`.
- `parse_muldiv()`: left-fold `unary` expressions over `STAR` and `SLASH`.  Verify `8 / 4 / 2` builds `BinOp("/", BinOp("/", Num(8), Num(4)), Num(2))`.
- `parse_addsub()`: the same left-fold over `PLUS` and `MINUS`, above `muldiv`.  Verify `2 + 3 * 4` builds `BinOp("+", Num(2), BinOp("*", Num(3), Num(4)))`.
- `parse_comparison()`: parse one `addsub`; if the next token is a comparison operator, consume it and one more `addsub` to form a `BinOp`.  Comparisons are non-associative (no chaining), so `a < b < c` is a syntax error.
- `parse_not()`: handle unary `NOT`, then call `parse_comparison()`.
- `parse_and()`: left-fold `not` expressions over `AND`.
- `parse_or()`: left-fold `and` expressions over `OR`.  Verify `a or b and c` builds `BinOp("or", Var("a"), BinOp("and", Var("b"), Var("c")))`.
- `parse_expr()`: delegates to `parse_or()`.

> **Do this.**
> 1. Open `test_parser.py` and paste in the harness below.
> 2. For each tier, add at least three tests named `test_...` that assert the tree shapes listed above, and run the suite from `cs374-parser/` after every tier:
>
> ```bash
> python3 test_parser.py
> ```

```python
# test_parser.py
from lexer import Lexer
from parser import parse, parse_expr, ParseError
from ast_nodes import Num, Var, BinOp, UnaryOp

def expr(source: str):
    return parse_expr(Lexer(source))

def test_muldiv_left_associates():
    assert expr("8 / 4 / 2") == BinOp("/", BinOp("/", Num(8), Num(4)), Num(2))

# TODO: at least three tests per tier: addsub, unary, comparison (including
#       that "a < b < c" raises ParseError), not, and, or

if __name__ == "__main__":
    tests = [f for name, f in dict(globals()).items() if name.startswith("test_")]
    for t in tests:
        t()
        print("PASS", t.__name__)
    print(f"{len(tests)} passed")
```

> **You should see.** One `PASS` line per test and a final count, for example `PASS test_muldiv_left_associates` and `1 passed`.  A failing assertion stops the run with an `AssertionError` traceback that names the test.  The same file also runs under `python3 -m pytest test_parser.py` once you install pytest in Step 3e.

> **If it fails.**
> - `8 / 4 / 2` right-associates: your loop parses the *right* side with the same tier instead of the tier below it, which recurses instead of folding.
> - `2 + 3 * 4` puts the addition under the multiplication: `parse_addsub` is calling `parse_unary` rather than `parse_muldiv`, so the ladder skips a rung.
> - The parser hangs: a tier calls itself on the left without consuming a token.  That is the left recursion of theory question 4, and the loop is the cure.

### Step 2c: Parse Statements and Blocks

Each statement begins with a token that tells you which rule to use.  `parse_stmt()` looks at that first token and dispatches to one of these:

- `parse_let_stmt()`: consumes `LET`, then expects `IDENT`, `EQ`, an expression, and `SEMICOLON` using `lexer.expect()`.  Returns a `Let` node.
- `parse_assign_stmt()`: consumes `IDENT` and `EQ`, then an expression and `SEMICOLON`.  Returns an `Assign` node.  (How will you distinguish assignment from an expression statement that starts with an identifier?  Document your lookahead strategy.)
- `parse_print_stmt()`: `PRINT`, expression, `SEMICOLON`.  Returns `Print`.
- `parse_block()`: `LBRACE`, then zero or more statements dispatched through `parse_stmt()`, then `RBRACE`.  Returns `Block`.
- `parse_if_stmt()`: `IF`, expression (the condition), block.  Then, if the next token is `ELSE`, consume it; if the token after `ELSE` is `IF`, recursively call `parse_if_stmt()` for the `else-if` branch, otherwise call `parse_block()`.  Returns `If`.
- `parse_while_stmt()`: `WHILE`, expression, block.  Returns `While`.
- `parse_program()`: parse statements until `EOF`.  Returns `Program`.

> **Do this.**
> 1. Add the statement functions and `parse_stmt()` to `parser.py`, in the order above.
> 2. Add tests to `test_parser.py` that call `parse(...)` on one-statement programs and assert the node returned, and run `python3 test_parser.py` after each function.
> 3. Write down, in your readme, how `parse_stmt()` tells an assignment from any other statement that starts with `IDENT`.

> **You should see.** `parse("let x = 1;")` returns `Program(stmts=[Let(name='x', value=Num(value=1, line=1))])`, and `parse("let x = 1")` raises `ParseError` naming `SEMICOLON` as the expected token.

### Step 2d: Trace the Worked Parse Example

The program below should produce the abbreviated tree that follows it:

```text
let x = 10;
while x > 0 {
    print x;
    x = x - 1;
}
```

```text
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

> **Do this.**
> 1. Save the program as `while_example.txt` in `cs374-parser/` and add a test that parses it and asserts the shape above (with `line` fields wherever your nodes carry them).
> 2. Trace the parser's calls on this program in your writeup: list each `parse_...` function in the order it is entered, and what it returns.  Your trace should begin `parse_program`, `parse_stmt`, `parse_let_stmt`, `parse_expr`, and descend the ladder to `parse_primary` for `10` before returning.

---

## Part 3: AST Tooling and Error Reporting

### Step 3a: Write the Pretty-Printer

Write `pretty(node, indent=0) -> str` in `ast_nodes.py`.  It returns an indented string representation of the tree, and each level of nesting adds two spaces.  For the worked example of Step 2d:

```text
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

> **Do this.**
> 1. Write `pretty()` with one case per node class.  A `match`/`case` over the node type or a chain of `isinstance` checks both work.
> 2. Add a test that asserts `pretty(parse(source))` for the worked example equals the text above.

### Step 3b: Write the Unparser

Write `unparse(node) -> str` in `ast_nodes.py`.  It regenerates valid source code from the AST, inserting parentheses around a `BinOp` subexpression only when they are needed to preserve the tree's meaning under standard precedence.  The rule: a child `BinOp` needs parentheses when its operator's precedence is *lower* than its parent's, or when it is the right child of a left-associative operator at the same precedence level.

- `unparse(BinOp("+", Num(2), BinOp("*", Num(3), Num(4))))` -> `"2 + 3 * 4"` (no parentheses needed).
- `unparse(BinOp("*", Num(2), BinOp("+", Num(3), Num(4))))` -> `"2 * (3 + 4)"` (parentheses required).

> **Do this.**
> 1. Write a precedence table (a dictionary from operator string to an integer) that mirrors the ladder in Part 1.
> 2. Write `unparse()` so that the two examples above produce exactly the strings shown, and add both as tests.

### Step 3c: Verify the Round Trip

For every test program in your test suite, verify the round-trip property:

```python
tree1 = parse(source)
source2 = unparse(tree1)
tree2 = parse(source2)
assert pretty(tree1) == pretty(tree2), f"Round-trip failed on: {source}"
```

This checks that `unparse` produces valid code and that the code means the same thing as the original.  Put the check in your test runner so that every program you add to the suite, including the worked `while` example, is verified automatically by `python3 test_parser.py`.

### Step 3d: Report Errors with Positions

Every `ParseError` must state what token type was expected, what token type was found, and the line and column of the offending token, for example `ParseError at line 3, col 12: expected SEMICOLON, found RBRACE`.

> **Watch out.** If your Lexer's `expect()` raises the lexer's own error type, catch it in a small helper in `parser.py` and re-raise it as a `ParseError` with the same line and column, so that every error the parser reports has one shape.

> **Do this.**
> 1. Run the five provided broken programs and five programs you write yourself through the parser:
>    - Missing semicolon: `let x = 5`
>    - Unclosed block: `while true { print x;`
>    - Bad operator: `let x = 5 + * 3;`
>    - Mismatched parenthesis: `print (1 + 2;`
>    - Assignment without `let`: `= 5;` (bare equals)
> 2. Record the error message for each in your readme.
> 3. In your writeup, show the before and after of the one error message you improved most during development.

### Step 3e: Property-Based Testing with Hypothesis

Your fixed test suite in Step 3c checks the round-trip law only on the programs *you thought to write*.  The interesting bugs live in the programs you did not think of: a unary minus applied to a parenthesized subtraction, an operator at exactly the precedence boundary, a deeply right-nested chain.  [Property-based testing](https://hypothesis.readthedocs.io/) finds those for you: instead of writing examples, you write a *generator* of random ASTs and assert that the law holds for all of them, and when it fails, Hypothesis **shrinks** the counterexample to the smallest tree that still breaks it.  This step is required, and the full walkthrough is in the [Property-Based Testing tutorial]({{ site.baseurl }}/Tutorials/PropertyBasedTesting).

> **Do this.**
> 1. Install Hypothesis with `uv add hypothesis` (or `pip install hypothesis`), and install pytest with `pip install pytest` if `pytest --version` reports that the command is not found.
> 2. Write an AST generator using `hypothesis.strategies.recursive`, so that trees can nest to arbitrary depth.  Add the sketch below to `test_parser.py`.
> 3. Run it with `pytest test_parser.py` (pytest discovers `@given` tests automatically).  When it fails, and on a first parser it usually will, Hypothesis prints the minimal failing tree.  Fix the bug (commonly a missing parenthesization rule in `unparse`, or a precedence/associativity error in `parse`), and re-run until it passes.
> 4. Report one shrunk counterexample you fixed in your `readme.md`: the minimal tree Hypothesis found, the one-sentence root cause, and the fix.  This is the deliverable: evidence that the property found a real bug your fixed tests missed (or a reasoned statement of why your parser was already correct, with the generator shown).

```python
from hypothesis import given, strategies as st

leaves = st.one_of(
    st.integers(min_value=0, max_value=999).map(Num),
    st.sampled_from(["x", "y", "z"]).map(Var),
)
exprs = st.recursive(
    leaves,
    lambda kids: st.builds(BinOp, st.sampled_from(["+", "-", "*", "/"]), kids, kids),
    max_leaves=25,
)

@given(exprs)
def test_round_trip(tree):
    assert parse(unparse(tree)) == tree   # structural equality on your AST
```

> **You should see.** On a passing run, pytest reports `test_round_trip PASSED` among your other tests.  On a failing run, Hypothesis prints `Falsifying example:` followed by the smallest tree that breaks the law; copy that tree into your readme before you fix it.

> **What this direction requires.** Direction B (Mini-Notation): apply the same idea to your pattern AST.  Generate random nestings of sequences, alternations, and Euclidean rhythms, and assert that your tree printer round-trips (or that re-parsing your printed form yields the same event list).  The reference-validation table stands in for the fixed-example half; the Hypothesis generator stands in for this half.

---

## Direction A: Generator Toolchain (Bison or PLY)

### What You Build

In this direction the LALR machinery of Bison (C) or PLY (Python) replaces the hand-written recursive descent ladder.  (LALR is the table-driven, bottom-up parsing method these tools generate.)  You still write the EBNF grammar of Part 1 first, and it remains the contract; you still deliver the AST tooling and positioned errors of Part 3.  What changes is Part 2's vehicle: instead of one function per tier, you write grammar productions with semantic actions, and instead of encoding precedence in the ladder's structure, you declare it.  This direction pairs naturally with the Lexer assignment's generator-toolchain direction, but the choices are independent: a PLY grammar can sit on top of your hand-rolled Lexer through a small token adapter.

### Requirements

> **What this direction requires.**
> - Part 1 in full, including the theory questions of Step 1c.
> - A grammar file with declared associativity and precedence, and zero unresolved conflicts in the generated automaton.
> - Semantic actions that build exactly one AST node each and evaluate nothing.
> - Part 3 in full: pretty-printer, unparser, round-trip verification, the Hypothesis test, and positioned `ParseError`s.
> - The same tree-shape tests as the core direction, including the worked `while` example of Step 2d.

### Step A.1: Write the Grammar File and Declarations

Write `parser.y` (Bison) or the PLY grammar module for the full language of Part 1.  Declare a `%union` (Bison) with fields for numeric values, strings, and your AST node pointer, and type your tokens accordingly (`%token <dval> NUMBER`, `%token <sval> IDENT STRING`, and so on).  Declare operator associativity and precedence with `%left`, `%right`, and `%nonassoc`; comparisons are `%nonassoc`, which enforces the same no-chaining rule the core direction's grammar encodes structurally.

### Step A.2: Write Conflict-Free Productions

Write the productions bottom-up, tightest binding first: `primary` -> `unary` -> `muldiv` -> `addsub` -> `comparison` -> `and` -> `or`, plus the statement, block, and program rules.  Your precedence declarations must resolve every shift-reduce conflict: run `bison -v` (or inspect PLY's `parser.out`) and confirm zero unresolved conflicts.  The dangling-else resolution of Step 1b still applies.  Document how the generator resolves it (the default shift is exactly "else binds to the nearest if") and cite the relevant state in the `.output`/`parser.out` automaton in your readme.

### Step A.3: Write the AST-Building Actions and Verify the Trees

Each production's semantic action builds exactly one AST node and nothing more; do not evaluate anything inside the parser.  In Python/PLY, build the same dataclass nodes from Step 2a; in C, use a tagged-union node struct with one constructor function per node type.  The syntax/semantics boundary is part of the grade.  The same tree-shape tests apply: `2 + 3 * 4` must build the multiplication under the addition, `8 / 4 / 2` must left-associate, and the worked `while` example of Step 2d must produce the same abbreviated tree.  Part 3 (pretty-printer, unparser, round-trip verification, and positioned `ParseError`s using the token's line/column from your lexer) applies unchanged.

---

## Direction B: The Mini-Notation Music Parser

### What You Build

In this direction you parse a production language: the **mini-notation** shared by TidalCycles and Strudel.  In it, `bd sn` is a two-step drum pattern, `bd*2` doubles, `<sn cp>` alternates per cycle, and `bd(3,8)` distributes three onsets among eight steps.  You grow the in-class flex/yacc subset (in the course repository under `files/examples/mininote/`) toward the real language, which means extending the lexer, the grammar, the AST, and the evaluator together: a new construct is never just a parser change.  The default toolchain is C with flex and bison, as in class; PLY is welcome, and its `parser.out` stands in for bison's `.output` automaton wherever cited below.  This direction never requires audio.  The semantics maps patterns to printable timed events `(value, begin, end)` over the cycle $$[0,1)$$, which you read, diff, and test as plain text.  Do not transcribe Strudel's own parser: derive the grammar and semantics yourself, then use Strudel strictly as an *oracle* (a trusted reference answer) to test against.

### Requirements

> **What this direction requires.** Direction B is the most ambitious direction of the three (budget roughly 25-35 hours end to end), and I recommend it mainly for students planning the music direction of the team project.  A reduced-scope variant earns full credit: B.2 (SLOW and DEGRADE) and B.3 (alternation `<a b c>`, with its displayed equation) are required; B.4 (Euclidean rhythms) and B.5 (polymeter) become optional extensions beyond full credit.  If you take the reduced scope, say so in your readme and build your B.6 validation table from the features you implemented.  In every scope, the grammar must remain conflict-free LALR(1), every transcript must be regenerable via `make test`, and random seeds must be fixed so that grading is reproducible.

### Step B.1: Write the Grammar First (Part 1 equivalent)

Write the complete EBNF grammar for your extended mini-notation (sequences, rests, groups, `*`, `/`, `?`, plus the constructs below), with one sentence per non-terminal explaining its placement.  Your readme cites specific states from the `.output` automaton to show where each new construct lives.

### Step B.2: Complete the Scaffolded Cases

The in-class evaluator leaves `SLOW` and `DEGRADE` unimplemented.  `slow n` stretches its child across $$n$$ cycles, which forces a design change: the evaluator signature carries no cycle number, so extend it (or derive the cycle from the span) and document your choice.  Gate `DEGRADE` on `rand() < RAND_MAX / 2` with `srand(42)` called exactly once, so grading is reproducible.

> **Paste into your submission.** A transcript of `bd/2 sn` on cycles 0 and 1, with a sentence explaining why they differ, and three identical consecutive runs of `hh*8?`.

### Step B.3: Add Alternation

`<a b c>` plays element $$\lfloor c \rfloor \bmod k$$ on cycle $$c$$, occupying the whole span:

$$
\mathcal{E}[\![\, \texttt{ALT}(c_1, \ldots, c_k) \,]\!](t_0, t_1, c) \;=\; \mathcal{E}[\![\, c_{(c \bmod k) + 1} \,]\!](t_0, t_1, c)
$$

Add `LANGLE`/`RANGLE` tokens, an `atom` production, an `N_ALT` node, and the evaluator case.  If you introduce a conflict along the way, keep the broken `.output` excerpt and describe in your readme how you diagnosed it.

> **Paste into your submission.** A transcript of `bd <sn cp hh>` across cycles 0-3, demonstrating rotation and wraparound.

### Step B.4: Add Euclidean Rhythms

`bd(3,8)` distributes $$k = 3$$ onsets as evenly as possible among $$n = 8$$ steps.  Toussaint showed these onset sets reproduce rhythm timelines from musical traditions worldwide ($$E(3,8)$$ is the Cuban tresillo).  An onset occurs at step $$i$$ exactly when

$$
(i \cdot k) \bmod n \;<\; k
$$

Verify the rule by hand for $$E(3,8)$$ (steps 0, 3, 6 -> `x..x..x.`) and one other $$(k, n)$$ pair before implementing, and include the hand-verification in your readme with a two-or-three-sentence argument for why the rule yields exactly $$k$$ onsets.  Syntactically, Euclid is a postfix modifier among the `term` productions: `term LPAREN NUMBER COMMA NUMBER RPAREN`.

> **Paste into your submission.** Transcripts of `bd(3,8)` and `bd(5,8)`, each matching its hand-computed onset set.

### Step B.5: Add Polymeter

`{a b, c d e}` runs its subsequences simultaneously at a common step rate, so different lengths drift and realign; `{a b, c d e}%4` fixes four steps per cycle.  Specify the semantics yourself, precisely, in displayed-equation style before writing code.  The specification is a graded artifact, and discovering that your first draft was ambiguous is an intended outcome.  Use strudel.cc to interrogate the corner cases (what happens on cycle 1? which subsequence sets the default step count?).  Add the brace/comma/percent tokens, the productions, an `N_POLY` node, and your specification's evaluator case.

> **Paste into your submission.** A transcript of `{bd sn, hh hh hh}` across cycles 0-2, annotated to show drift and realignment.

### Step B.6: Validate Against the Reference (Part 3 equivalent)

In place of the unparser and round-trip verification, deliver a tree printer (the pretty-printer requirement, unchanged), location-prefixed parse errors, and a validation table of at least eight patterns that together exercise every feature, including at least two that nest new constructs inside one another (`<bd(3,8) sn>`, `{bd <sn cp>, hh*2}`).  For each pattern, record your evaluator's event list against the spans Strudel highlights at strudel.cc, and investigate every discrepancy to a conclusion: grammar difference, semantic difference, or bug (yours or, occasionally and delightfully, theirs).  The Hypothesis generator of Step 3e, applied to your pattern AST, completes this part.

Deliverables for this direction use the same ZIP-and-readme shape as the core direction: complete source (`.l`, `.y`, `.c`, `.h`, `Makefile`, or the PLY equivalents), the generated `.output`/`parser.out` automaton, a test transcript regenerable via `make test`, and a readme containing the EBNF grammar, the hand-derivations, the polymeter specification, and the validation table.  Fix random seeds and list toolchain versions (`flex --version`, `bison --version`, `gcc --version`) for reproducibility.  Two useful resources: Levine's *flex & bison* (O'Reilly, 2009), particularly the conflict-diagnosis chapters, and Toussaint's "The Euclidean Algorithm Generates Traditional Musical Rhythms" (*BRIDGES* 2005).

---

## Deliverables

Submit a ZIP containing the files below, and list your Python version in the readme so that I can reproduce your test run.  **Direction A** swaps the vehicle inside the same structure: the `.y` grammar (plus `Makefile`) or PLY module in place of the hand-written `parser.py`, the automaton file demonstrating zero conflicts, and a readme that also documents the precedence declarations and the dangling-else state.  **Direction B**'s deliverable list appears at the end of its section above.  In every direction the readme leads with the complete EBNF grammar.

| File or artifact | What it shows | Rubric row |
|------------------|---------------|------------|
| Part 0 drawing and node types (in `readme.md` or a scanned page) | The AST for `3 + 4 * 5`, what it discarded, and the `if`/`else` and call nodes with the uncertain field marked | Part 0: Abstract Syntax Trees |
| `readme.md` (about one page) | The complete EBNF grammar with one sentence per non-terminal, the dangling-else policy, the four theory answers, the round-trip verification strategy, the error-message before-and-after, and the one shrunk Hypothesis counterexample you fixed (or a reasoned all-clear with the generator shown) | EBNF Grammar and Parsing Theory; AST Design, Tooling, and Error Reporting |
| `parser.py` | The parser module, importing `lexer.py` unchanged (note any lexer bug fixes in the readme) | Recursive Descent Parser |
| `ast_nodes.py` | All node dataclasses, the pretty-printer, and the unparser | AST Design, Tooling, and Error Reporting |
| `test_parser.py` | The test suite: tree-shape tests, fixed-example round-trip verification, the Hypothesis property-based round-trip test with its AST generator, and error tests | Recursive Descent Parser; AST Design, Tooling, and Error Reporting |
| `test_output.txt` | The test run output, with all tests passing, including the Hypothesis test | Recursive Descent Parser; AST Design, Tooling, and Error Reporting |

---

## Self-Check Before You Submit

- [ ] Part 0 shows the AST (not the parse tree) for `3 + 4 * 5`, names what it threw away, and marks the uncertain field.
- [ ] The grammar in the readme matches the parser exactly: every precedence level is its own non-terminal, and the dangling-else resolution is stated.
- [ ] All four theory questions are answered, with the shift-reduce trace as a stack-input-action table.
- [ ] `2 + 3 * 4`, `8 / 4 / 2`, `--x`, and `a or b and c` build the trees listed in Step 2b, and `a < b < c` raises `ParseError`.
- [ ] The worked `while` program parses to the tree in Step 2d, and the trace is in the writeup.
- [ ] `unparse` inserts parentheses only where the tree shape requires them, and the round-trip check runs over every program in the suite.
- [ ] The Hypothesis test runs, and the readme reports one shrunk counterexample (or a reasoned all-clear with the generator shown).
- [ ] Every `ParseError` names the expected token, the found token, and the line and column; the ten broken programs are recorded.
- [ ] `lexer.py` is imported unchanged, or the readme declares the reference lexer, and the Python version is listed.

---

## Reflection Prompts

- Which tier's left-recursion-to-loop rewrite did you have to think hardest about, and what finally made it click?  (Direction A: which precedence declaration did the same job, and how did you confirm it in the automaton?  Direction B: which construct's grammar placement did you have to think hardest about?)
- Your unparser had to decide where parentheses are necessary.  State the rule you implemented in one sentence.  (Direction B: your evaluator had to decide how cycle information reaches constructs that need it; state your design in one sentence.)
- When you traced the parser calls on the `while` example in step 2d, which recursive call surprised you, and why?  (Directions A and B: which reduction in the automaton surprised you, and why?)
- If you took a direction beyond the core: what did the grammar-first discipline reveal that jumping straight to code would have hidden?
- Direction B only: Toussaint's Euclidean rhythms emerged from a scheduling algorithm and turned out to describe music made by humans across centuries and continents.  What does this suggest about the relationship between formal structure and cultural practice, and about who is credited when an algorithm formalizes existing human knowledge?
