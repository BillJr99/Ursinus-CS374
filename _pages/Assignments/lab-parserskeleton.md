---
layout: assignment
permalink: /Assignments/ParserSkeleton
title: "CS374: Principles of Programming Languages - Lab: Parser Skeleton"

info:
  coursenum: CS374
  purpose: "To build the first two tiers of a recursive descent parser with a partner, using the peek/decide/consume pattern that every remaining parsing function repeats, so the Parser assignment's midpoint finds you already climbing."
  tilt:
    task: "With a partner, implement parse_primary and parse_unary over the Lexer interface, with tree-shape tests and one positioned parse error."
    criteria: "I grade correct primary and unary parsing with passing tree-shape tests, and a positioned error on invalid input, weighted 70/30 across the two parts.  The rubric below spells out each row."
  points: 15
  goals:
    - To implement the primary and unary tiers of a recursive descent parser over the Lexer's peek/advance/expect interface
    - To verify parser output with tree-shape tests rather than string comparison
    - To raise a positioned ParseError stating what was expected and what was found
  rubric:
    - weight: 10
      description: "Part 0: Before You Start - Recursive Descent Parsing"
      preemerging: No pseudocode is written and no trace is attempted
      beginning: Pseudocode is written for a non-terminal but it is not traced on any input
      progressing: The function is traced on a three-token input but the lookahead points are not marked, or the left-recursive rule is identified without being rewritten
      proficient: Pseudocode for one non-terminal's recursive-descent function is traced by hand on a three-token input with every lookahead marked; a rule that would make naive recursive descent loop forever is identified as left recursion and rewritten so it terminates
    - weight: 63
      description: "The First Two Tiers (Goal 1)"
      preemerging: Neither tier runs, or the parser reads tokens without using the Lexer interface
      beginning: parse_primary handles literals but not identifiers or parenthesized expressions, or parse_unary cannot nest
      progressing: Both tiers work for the provided cases but one edge fails, e.g., double negation, or a parenthesized expression as a unary operand
      proficient: parse_primary handles number, string, boolean, identifier, and parenthesized expressions; parse_unary handles negation and logical not, nesting correctly (e.g., --x and not not x); both consume tokens only through peek/advance/expect; and the pattern is documented in one sentence per function
    - weight: 27
      description: "Tests and Errors (Goals 2-3)"
      preemerging: No tests, or tests compare printed strings instead of tree shapes
      beginning: Tree-shape tests exist for primaries only, and errors are bare Python exceptions
      progressing: Tree-shape tests cover both tiers but the parse error lacks position or the expected/found pair
      proficient: Tree-shape tests cover every primary form and nested unary cases, and an invalid input (e.g., a stray semicolon where an expression is required) raises a ParseError stating what was expected, what was found, and the line and column
  readings:
    - rtitle: "Recursive Descent Activity"
      rlink: "Activities/liascript-recursivedescent.md"
      liapage: true
    - rtitle: "Abstract Syntax Trees Activity"
      rlink: "Activities/liascript-ast.md"
      liapage: true

tags:
  - parser
  - languages
  - pipeline
  - lab

---

In this lab you build the bottom two tiers of a recursive descent parser: `parse_primary` and `parse_unary`.  A recursive descent parser is a parser written as one function per grammar rule, where each function calls the functions for the rules it uses.  These two functions set the pattern every other tier of the Parser assignment repeats: look at `peek()`, decide which rule applies, consume tokens with `advance()` or `expect()`, and return a node.  You leave with a `parser_skeleton.py` that parses literals, identifiers, parentheses, and nested negation, a test file that checks tree shapes, and a parse error that says where things went wrong.  Use your own Lexer or the released Reference Lexer; either satisfies the interface contract, and this lab is a good first test of whichever one you plan to build the Parser assignment on.

**Pair policy.**  You may do this lab in pairs.  Driver/navigator works well; swap roles between the two tiers.  Submit the same files, name your partner, and you both receive the same grade.  Working alone is fine as well.  The Parser assignment remains individual work: you may both grow this shared skeleton there, but the remaining tiers are your own.

See the course schedule for the assigned and due dates.

---

## Before You Start

You need:

- Python 3.10 or newer (run `python3 --version` to check).
- A terminal and an editor such as VS Code.  If either is new to you, work through the [dev environment page]({{ site.baseurl }}/Tutorials/DevEnvironment) and the [shell primer]({{ site.baseurl }}/Tutorials/ShellForLanguageDev) first.
- A Lexer that exposes `peek()`, `advance()`, and `expect(token_type)`.  Use your own `lexer.py` from the Lexer assignment, or the [reference lexer]({{ site.baseurl }}/files/reference/reference-lexer.zip), which was released with the Parser assignment.  Using the reference costs nothing and does not change your Lexer grade; you only need to declare it with one line in your readme.  If you use your own, check that `not` produces its own token type: the Lexer assignment's minimum token table has no `not` keyword, so add a `NOT` rule before `IDENT` if needed, or `not ok` lexes as two identifiers and `parse_unary` never sees the operator.  The reference lexer already has `NOT`.
- The two activities listed under Readings above.  Part 0 assumes you have seen a hand trace of recursive descent.

> **Do this.**
> 1. Create the project folder and move into it.  Every command in this lab runs from inside it.
> 2. Put a lexer in it: copy your own `lexer.py` (and any file it imports, such as `tokens.py`) into the folder, or move `reference-lexer.zip` into the folder and run the two marked lines to unpack it and copy its two files up.
> 3. Confirm Python can import the lexer and hand you one token.
>
> ```bash
> mkdir cs374-parser-skeleton
> cd cs374-parser-skeleton
> unzip reference-lexer.zip                # reference lexer only
> cp lexer/lexer.py lexer/tokens.py .      # reference lexer only
> python3 -c "from lexer import Lexer; print(Lexer('42').peek())"
> ```

> **You should see.** One token.  With the reference lexer it is exactly the line below; with your own lexer the field names may differ, but the type must be your number type and line and column must both be 1.

```text
Token(type='INT', value='42', line=1, col=1, decoded=None)
```

> **If it fails.**
> - `ModuleNotFoundError`: for `lexer`, you are not inside `cs374-parser-skeleton/` or the file is not named `lexer.py` (run `ls` and check); for `tokens`, the reference `lexer.py` imports `tokens.py`, so copy both.
> - `python3: command not found`: on Windows try `python` or `py`, and use that spelling for every command in this lab.

> **Time budget.** About three hours: 20 to 30 minutes for Part 0 on paper, about 90 minutes for Part 1, and about an hour for Part 2.

### Your First 15 Minutes

1. Do Part 0 on paper, at least the trace of one function.  Ten minutes is enough for a first pass.
2. Do Step 1.1: paste the skeleton, fill in only the number case of `parse_primary`, and run the file.
3. When you see `Num(value=42, line=1)`, swap driver and navigator and start Step 1.2.  Every remaining case is one more branch of the same `if`: edit, run, read the output.

---

## Part 0: Before You Start - Recursive Descent Parsing (10%)

Do this part on paper before you write `parse_primary`.  You may do it alone even though the rest of this lab is pair work.  Tracing one function on three tokens shows you exactly where lookahead lives: the token the parser inspects without consuming, so that it can decide which rule applies.

> **Do this.**
> 1. Write the pseudocode for the recursive-descent function of one non-terminal in a small expression grammar.  (A non-terminal is a grammar symbol defined by rules, such as `expression` or `term`.)  Trace it by hand on a three-token input and mark every point where it looks ahead.
> 2. Find a grammar rule that would make naive recursive descent loop forever.  This is left recursion: a rule whose right-hand side begins with the same non-terminal it defines, so the function calls itself before consuming anything.  Rewrite the rule so the function terminates.

> **Bring to class.** The trace, with the point marked where you needed more than one token of lookahead.  Bring one that broke down partway too; the peek/decide/consume pattern in Part 1 is the fix for wherever it broke.

---

## Part 1: The First Two Tiers (63%)

In `parser_skeleton.py` you define the AST (abstract syntax tree) node dataclasses `Num`, `Str`, `Bool`, `Var`, `Unary`, plus a `Grouping` node or a pass-through for parentheses, matching the node names your grammar work uses.  Then you implement two functions.  `parse_primary` handles number, string, and boolean literals; identifiers; and `( expression )`; for this lab a parenthesized expression may recurse into `parse_unary`, and the full expression ladder arrives in the Parser assignment.  `parse_unary` handles `-` and `not`; both are right-associative and nest (`--x`, `not not ok`), and at the bottom it delegates to `parse_primary`.

Both functions consume tokens only through the Lexer's `peek`, `advance`, and `expect`.  If a parsing function reaches into the token list directly, every tier above it breaks when the lexer changes.  Document the pattern in one sentence per function.

### Step 1.1: Create the skeleton and parse a number

A dataclass is a Python class where you list the fields and Python writes `__init__` and `__repr__` for you.  The token type names in the comments are the reference lexer's (`INT`, `FLOAT`, `STRING`, `TRUE`, `FALSE`, `IDENT`, `LPAREN`, `RPAREN`, `MINUS`, `NOT`); if your own lexer uses different names, substitute yours.

> **Do this.**
> 1. Create `parser_skeleton.py` in `cs374-parser-skeleton/` and paste in the skeleton below.  Read every `# TODO` before you change anything.
> 2. Decide the one open choice (a `Grouping` node or a pass-through for parentheses) and record it in the comment where the TODO asks.
> 3. In `parse_primary`, replace the `raise NotImplementedError` line with the `INT` (and `FLOAT`) case: check `tok.type`, call `self.lexer.advance()` to consume the token, and return `Num(int(tok.value), tok.line)` (or `float(...)` for a `FLOAT`).  Leave the other cases for Step 1.2.
> 4. Run the file from inside `cs374-parser-skeleton/` with `python3 parser_skeleton.py`.

```python
"""parser_skeleton.py: the bottom two tiers of a recursive descent parser."""
from dataclasses import dataclass
from typing import Any
from lexer import Lexer   # your own lexer.py, or the reference one

@dataclass
class Num:
    value: float
    line: int = 0         # where the literal appeared (useful in error messages)

# TODO: define Str (value: str, the contents without the quotes), Bool
#       (value: bool), and Var (name: str) the same way, each with line: int = 0.

@dataclass
class Unary:
    op: str               # "-" or "not"
    operand: Any          # another Unary, or a primary node

# TODO (your choice): define a Grouping dataclass (one field, expr) and return
#       Grouping(inner) from parse_primary, or return inner directly (a
#       pass-through).  Replace this comment with your choice and why.

class ParseError(Exception):
    """A syntax error at a known position; str(err) names it all."""
    def __init__(self, expected: str, found: str, line: int, col: int):
        self.expected, self.found, self.line, self.col = expected, found, line, col
        super().__init__(f"ParseError at line {line}, col {col}: "
                         f"expected {expected}, found {found}")

class Parser:
    """Reads tokens only through lexer.peek(), lexer.advance(), lexer.expect()."""

    def __init__(self, lexer: Lexer):
        self.lexer = lexer

    def parse_primary(self):
        """Pattern: TODO (one sentence)."""
        tok = self.lexer.peek()      # look at the next token; do not consume it yet
        # TODO: decide on tok.type, consume with advance() or expect(), return a node:
        #   INT or FLOAT   -> Num(...)   convert tok.value with int() or float()
        #   STRING         -> Str(...)   strip the quotes (reference lexer: tok.decoded)
        #   TRUE or FALSE  -> Bool(...);  IDENT -> Var(...)
        #   LPAREN         -> consume it, parse the inside with self.parse_unary(),
        #                     expect RPAREN, return the inside (or a Grouping)
        #   anything else  -> raise ParseError("an expression", tok.type, tok.line, tok.col)
        raise NotImplementedError("parse_primary")

    def parse_unary(self):
        """Pattern: TODO (one sentence)."""
        tok = self.lexer.peek()
        # TODO: if tok.type is MINUS or NOT, consume it, call self.parse_unary()
        #       for the operand, and return Unary(op, operand).
        #       Otherwise return self.parse_primary().
        raise NotImplementedError("parse_unary")

if __name__ == "__main__":
    print(Parser(Lexer("42")).parse_primary())
    # After Step 1.3, add:  print(Parser(Lexer("--42")).parse_unary())
```

> **You should see.** The dataclass repr of the node your parser returned for `42`.

```text
Num(value=42, line=1)
```

> **If it fails.**
> - `NotImplementedError: parse_primary`: your new `if` did not match.  Print `tok.type` right after `peek()` and compare it with the name you tested.
> - `ValueError: invalid literal for int()`: your lexer's `value` field holds something other than the raw digits.  Check what your `Token` stores.

### Step 1.2: Finish parse_primary

> **Do this.**
> 1. Add the `STRING`, `TRUE`, `FALSE`, and `IDENT` cases.  For a string, strip the two quote characters (the reference lexer's `tok.decoded` already has them removed and escapes resolved).
> 2. Add the `LPAREN` case: consume the `(`, call `self.parse_unary()` for the inside, then consume the `)` with `self.lexer.expect("RPAREN")`.  Return the inside node, or wrap it in `Grouping` if that was your choice.  (The reference lexer's `expect()` raises its own `LexError` on a mismatch.  That is fine for this lab: the required `ParseError` is for a token that cannot start an expression, which you detect yourself in the next item.)
> 3. Add the final `else`: any other token cannot start an expression, so raise `ParseError("an expression", tok.type, tok.line, tok.col)`.  Do not consume the token first; the error should point at it.
> 4. Change the input in the `__main__` block to `"(x)"` and run again.

> **You should see.** With the pass-through choice, `Var(name='x', line=1)`.  With a `Grouping` node, `Grouping(expr=Var(name='x', line=1))`.

### Step 1.3: Implement parse_unary and document the pattern

`parse_unary` is the first function that calls itself.  A prefix operator applies to whatever comes after it, and that might be another prefix operator, so the operand is parsed by another call to `parse_unary`.  That recursion is what makes `-` and `not` right-associative and lets them nest.

> **Do this.**
> 1. In `parse_unary`, check whether `tok.type` is `MINUS` or `NOT`.
> 2. If it is, consume it with `advance()`, call `self.parse_unary()` to parse the operand, and return `Unary("-", operand)` or `Unary("not", operand)`.
> 3. If it is not, return `self.parse_primary()`.
> 4. Add the second print line the `__main__` block suggests, and run `python3 parser_skeleton.py` again.
> 5. Replace the two `TODO` docstrings with one sentence each that states the peek/decide/consume pattern as that function uses it.
> 6. Search your file to confirm that neither function touches the lexer through anything other than `peek`, `advance`, and `expect`.

> **You should see.** Two lines: your Step 1.2 result, then a `Unary` nested inside a `Unary`, which shows that `--42` built two levels.

```text
Var(name='x', line=1)
Unary(op='-', operand=Unary(op='-', operand=Num(value=42, line=1)))
```

> **If it fails.**
> - `RecursionError`: you called `parse_unary()` without consuming the operator first, so every call sees the same `-`.  Consume, then recurse.
> - Only one `Unary` level appears: you called `parse_primary()` for the operand instead of `parse_unary()`.

> **Checkpoint.** `python3 parser_skeleton.py` prints both lines above; `(x)`, `"hi"`, `true`, and `not not ok` each produce the node you expect; and each function has a one-sentence pattern docstring.  Swap driver and navigator before Part 2.

---

## Part 2: Tests and Errors (27%)

In `test_skeleton.py`, you write tree-shape tests.  A tree-shape test asserts on node types and fields, for example `isinstance(node, Unary)`, `node.op == "-"`, and `node.operand.value == 42`.  Never compare printed strings: a `repr` changes whenever you add a field, but the shape of the tree is what the interpreter will walk.  Cover every primary form and at least two nested unary cases.  Then make failure informative: an input that cannot start an expression (for example, `;`) must raise a `ParseError` that states what was expected, what was found, and the line and column of the offending token.

### Step 2.1: Write tree-shape tests

> **Do this.**
> 1. Create `test_skeleton.py` next to `parser_skeleton.py` and paste in the skeleton below.
> 2. `test_number` is complete; use it as the model.  Write one test per primary form (string, boolean, identifier, parenthesized) with the suggested names.
> 3. Finish `test_double_negation`, then add `test_double_not` for `not not ok` and `test_paren_unary_operand` for `-(x)`, a parenthesized expression as a unary operand.
> 4. Run the tests with `python3 test_skeleton.py`.

```python
"""test_skeleton.py: tree-shape tests for parse_primary and parse_unary."""
from lexer import Lexer
from parser_skeleton import Parser, ParseError, Num, Str, Bool, Var, Unary

def parse(src: str):
    return Parser(Lexer(src)).parse_unary()

def test_number():
    node = parse("42")
    assert isinstance(node, Num), f"expected Num, got {type(node).__name__}"
    assert node.value == 42

# TODO: test_string ('"hi"' -> Str "hi"), test_boolean ("true" -> Bool True),
#       test_identifier ("x" -> Var "x"), test_parenthesized ("(x)" -> your
#       Step 1.2 choice).  Assert on node types and fields, never on str(node).

def test_double_negation():
    node = parse("--x")
    # TODO: assert node is a Unary with op "-", node.operand is a Unary with
    #       op "-", and node.operand.operand is a Var named "x".
    raise NotImplementedError("test_double_negation")

# TODO: test_double_not for "not not ok", and test_paren_unary_operand for
#       "-(x)" (a Unary whose operand came through the parenthesis case).

def test_bad_start_raises_parse_error():
    try:
        parse(";")
    except ParseError as err:
        # TODO: assert err.line == 1 and err.col == 1, and that str(err)
        #       names both what was expected and what was found (SEMICOLON).
        return
    assert False, "parse(';') did not raise ParseError"

if __name__ == "__main__":
    for name, fn in sorted(globals().items()):
        if name.startswith("test_"):
            try:
                fn()
                print(f"PASS {name}")
            except Exception as err:
                print(f"FAIL {name}: {err}")
```

> **You should see.** One line per test, in alphabetical order, every one beginning `PASS`.  With the suggested names the full run is nine lines.

```text
PASS test_bad_start_raises_parse_error
PASS test_boolean
PASS test_double_negation
PASS test_double_not
PASS test_identifier
PASS test_number
PASS test_paren_unary_operand
PASS test_parenthesized
PASS test_string
```

> **If it fails.**
> - A `FAIL` line ending in `NotImplementedError`: that test still has its TODO body.
> - `FAIL test_parenthesized: expected Var, got Grouping` (or the reverse): the test and Step 1.2 disagree about the parenthesis choice.  Pick one and make both match.
> - `ImportError` naming `Grouping`: you chose the pass-through, so do not import a node you did not define.

### Step 2.2: Make failure informative

> **Do this.**
> 1. Finish `test_bad_start_raises_parse_error`: assert the line and column are both 1 and that `str(err)` contains both the expected description and `SEMICOLON`.
> 2. Confirm the message reads in full, then capture the passing test output for your submission.  The `>` sends what the tests print into a file instead of the screen; open the file to check it.
>
> ```bash
> python3 -c "from lexer import Lexer; from parser_skeleton import Parser; Parser(Lexer(';')).parse_unary()"
> python3 test_skeleton.py > test_output.txt
> ```

> **You should see.** A traceback whose last line is your positioned error.

```text
parser_skeleton.ParseError: ParseError at line 1, col 1: expected an expression, found SEMICOLON
```

> **If it fails.**
> - The last line is a `LexError`: the `;` never reached your parser, so your lexer does not recognize it.  Add a `SEMICOLON` rule, or test with another token your lexer does know, such as `)`.
> - The column is wrong: you consumed the bad token before raising.  Raise on the peeked token.

---

## Deliverables

Submit a ZIP containing the items below.

| File or artifact | What it shows | Rubric row |
|------------------|---------------|------------|
| `parser_skeleton.py` | The five node dataclasses, the parenthesis choice, `parse_primary` and `parse_unary`, and a one-sentence pattern per function | The First Two Tiers |
| `test_skeleton.py` | Tree-shape tests for every primary form, at least two nested unary cases, and the positioned `ParseError` test | Tests and Errors |
| Captured test output (for example `test_output.txt`) | The tests pass on the lexer you chose | Tests and Errors |
| Readme line | Both partners' names, and whether you built on your own Lexer or the reference | Deliverable requirement |
| Part 0 trace, on paper | Pseudocode traced on three tokens with lookahead marked; the left-recursive rule rewritten | Part 0 |

---

## Self-Check Before You Submit

- [ ] `parse_primary` returns a node for a number, a string, a boolean, an identifier, and a parenthesized expression.
- [ ] `parse_unary` builds two nested `Unary` nodes for `--x` and for `not not ok`, and handles `-(x)`.
- [ ] Neither function touches the lexer except through `peek`, `advance`, and `expect`, and each has a one-sentence docstring stating the peek/decide/consume pattern.
- [ ] Every test asserts on node types and fields; no test compares `str(node)` or `repr(node)` to a string.
- [ ] Parsing `;` raises a `ParseError` whose message includes what was expected, what was found, and line 1, col 1.
- [ ] The captured test output shows every test passing, and the readme names both partners and says which lexer you built on.

---

## Grading Breakdown

This lab is worth 15 points, as the course schedule states.  Each part's weight below is a percentage of those 15 points, and the rubric rows use the same percentages.

| Component | Weight |
|-----------|--------|
| Part 0: Recursive Descent Parsing | 10% |
| Part 1: The First Two Tiers | 63% |
| Part 2: Tests and Errors | 27% |
| **Total** | **100% (15 points)** |

---

## Reflection Prompts

- State the peek/decide/consume pattern in your own words, and name which remaining tier of the Parser assignment you expect to repeat it most times.
- If you worked in a pair, who did what, and name one thing your partner caught that you would have missed.  If you worked alone, note that instead.
