---
layout: assignment
permalink: /Assignments/ParserSkeleton
title: "CS374: Principles of Programming Languages - Lab: Parser Skeleton"

info:
  coursenum: CS374
  purpose: "To stand up the first two tiers of the recursive descent ladder with a partner (the peek/decide/consume pattern that every remaining parsing function repeats) so the Parser assignment's midpoint finds you already climbing."
  tilt:
    task: "With a partner, implement parse_primary and parse_unary over the Lexer interface, with tree-shape tests and one positioned parse error."
    criteria: "I assess your work on correct primary and unary parsing with passing tree-shape tests, and a positioned error on invalid input, weighted 70/30 across the two parts.  The rubric below spells out each row."
  points: 100
  goals:
    - To implement the primary and unary tiers of a recursive descent parser over the Lexer's peek/advance/expect interface
    - To verify parser output with tree-shape tests rather than string comparison
    - To raise a positioned ParseError stating what was expected and what was found
  rubric:
    - weight: 70
      description: "The First Two Tiers (Goal 1)"
      preemerging: Neither tier runs, or the parser reads tokens without using the Lexer interface
      beginning: parse_primary handles literals but not identifiers or parenthesized expressions, or parse_unary cannot nest
      progressing: Both tiers work for the provided cases but one edge fails, e.g., double negation, or a parenthesized expression as a unary operand
      proficient: parse_primary handles number, string, boolean, identifier, and parenthesized expressions; parse_unary handles negation and logical not, nesting correctly (e.g., --x and not not x); both consume tokens only through peek/advance/expect; and the pattern is documented in one sentence per function
    - weight: 30
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

This **lab** builds the bottom of the recursive descent ladder, `parse_primary` and `parse_unary`.  Those two functions establish the pattern every other tier of the Parser assignment repeats: look at `peek()`, decide, consume with `advance()` or `expect()`, and return a node.  Landing this mid-assignment means the Parser's hardest stretch starts from working code instead of a blank file.  You do this one with a partner.

Use your own Lexer, or the released Reference Lexer.  Either one satisfies the interface contract, and this lab makes a good first test of whichever you plan to build the Parser assignment on.

**Pair policy.**  You may do this lab **in pairs**: driver/navigator works well, swapping between the two tiers.  Submit the same files, name your partner, and you both receive the same grade.  Alone is fine as well.  The Parser assignment remains individual work: you may both grow this shared skeleton there, but the remaining tiers are your own.

See the course schedule for the assigned and due dates.

---

## Part 1: The First Two Tiers (70 points)

In `parser_skeleton.py`, define the AST node dataclasses you need (`Num`, `Str`, `Bool`, `Var`, `Unary`, plus a `Grouping` or pass-through for parentheses; match the node names your grammar work uses), then implement:

- **`parse_primary`**: number, string, and boolean literals; identifiers; and `( expression )` (for this lab, a parenthesized expression may recurse into `parse_unary`; the full expression ladder arrives in the Parser assignment).
- **`parse_unary`**: `-` and `not`, right-associative and nesting (`--x`, `not not ok`), delegating to `parse_primary` at the bottom.

Both functions consume tokens **only** through the Lexer's `peek`/`advance`/`expect`, the discipline the whole ladder depends on.

## Part 2: Tests and Errors (30 points)

In `test_skeleton.py`, write **tree-shape tests**: assert on node types and fields (`isinstance(node, Unary)`, `node.op == "-"`, `node.operand.value == 42`), never on printed strings, covering every primary form and at least two nested unary cases.  Then make failure informative: parsing an input that cannot start an expression (e.g., `;`) must raise a `ParseError` stating what was expected, what was found, and the line and column from the offending token.

---

## Deliverables

Submit a ZIP containing `parser_skeleton.py`, `test_skeleton.py` with its passing output captured, and a readme line naming both partners and stating whether you built on your own Lexer or the reference.

## Grading Breakdown

| Component | Points |
|-----------|--------|
| Part 1: The First Two Tiers | 70 |
| Part 2: Tests and Errors | 30 |
| **Total** | **100** |

## Reflection Prompts

- State the peek/decide/consume pattern in your own words, and name which remaining tier of the Parser assignment you expect to repeat it most times.
- If you worked in a pair, who did what, and name one thing your partner caught that you would have missed.  If you worked alone, note that instead.
- AI disclosure: list any generative-AI tools you used, for what, and how you verified the results (or state 'none').
- Approximately how many hours it took you to finish this lab (I will not judge you for this at all; I am simply using it to gauge if the labs are too easy or hard)?
