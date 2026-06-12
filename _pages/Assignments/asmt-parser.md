---
layout: assignment
permalink: /Assignments/Parser
title: "CS374: Principles of Programming Languages - The Parser and AST"

info:
  coursenum: CS374
  points: 100
  goals:
    - To implement a recursive descent parser for expressions and statements atop your Lexer component
    - To build the full precedence ladder with correct associativity, parentheses, and unary minus
    - To produce an abstract syntax tree of node classes with a pretty printer and an unparser
    - To report syntax errors with positions and expectations
  rubric:
    - weight: 60
      description: Algorithm and Implementation
      preemerging: The parser fails to run or fails most provided programs due to major issues
      beginning: The parser runs but fails on several provided test programs due to one or more minor issues
      progressing: The parser passes the provided test programs but would fail in a general case due to a minor issue such as an associativity error or a mishandled nested construct
      proficient: A correct parser passes the provided and hidden test programs with correct precedence and associativity at every tier, correct nesting of statements and blocks, and would be reasonably expected to handle the general case
    - weight: 20
      description: AST Design and Tooling
      preemerging: No node classes exist, or the tree structure is incorrect
      beginning: Node classes exist but the pretty printer or unparser is missing or incorrect
      progressing: Node classes, pretty printer, and unparser work, with the round-trip property tested on a few inputs
      proficient: Node classes cover every construct with documented fields, the pretty printer renders nested structure clearly, the unparser parenthesizes only where the tree shape requires, and the round-trip property parse(unparse(parse(s))) is verified programmatically across the test suite
    - weight: 10
      description: Error Reporting
      preemerging: Syntax errors crash without information
      beginning: Errors are reported without positions or expectations
      progressing: Errors report the expected and found tokens with positions for most failure modes
      proficient: Every error reports what was expected, what was found, and where, evaluated against the assignment's five provided broken programs plus five of your own design
    - weight: 10
      description: Writeup and Submission
      preemerging: An incomplete submission is provided
      beginning: The program is submitted, but not according to the directions in one or more ways
      progressing: The program is submitted according to the directions with a minor omission, with at least superficial responses to the reflection prompts
      proficient: The program is submitted according to the directions, including a readme writeup and thoughtful answers to the reflection prompts
  readings:
    - rtitle: "Recursive Descent Activity"
      rlink: "https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374/gh-pages/_pages/Activities/liascript-recursivedescent.md"
    - rtitle: "Parsing Expressions Activity"
      rlink: "https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374/gh-pages/_pages/Activities/liascript-parsingexpressions.md"
    - rtitle: "Abstract Syntax Trees Activity"
      rlink: "https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374/gh-pages/_pages/Activities/liascript-ast.md"

tags:
  - parser
  - ast
  - languages
  - pipeline

---

This assignment builds the second permanent component of your pipeline: a recursive descent parser that consumes your Lexer's tokens and produces an AST of node classes. Build tier by tier, testing each before adding the next; the scaffolding below is the order that works.

## Part 1: The Expression Ladder (scaffolded; test after every step)

Implement `parse_expr` through the full ladder, in this order, with at least three passing tests committed after each tier:

1a. `primary`: numbers, identifiers, and parenthesized expressions.

1b. `unary`: unary minus (and verify `--x` nests).

1c. `muldiv`: `*` and `/` with the left-fold loop; verify `8 / 4 / 2` builds the left-leaning tree.

1d. `addsub`: `+` and `-` above it; verify `2 + 3 * 4` nests the multiplication inside.

1e. `comparison`: `< <= > >= == !=` at a looser tier; verify `a + 1 < b * 2`.

1f. Logical `and`/`or` at the loosest tiers with `or` looser than `and`; verify `a or b and c` nests as `a or (b and c)`.

## Part 2: Statements and Blocks

2a. `letstmt`, assignment statements, and `printstmt`, each ending in a semicolon.

2b. `block` as brace-delimited statement lists, and `ifstmt` with optional `else` (document which `if` owns a dangling `else` in your grammar and verify with a test).

2c. `whilestmt`, and verify statements nest (a `while` containing an `if` containing a block).

2d. `parse_program`: a sequence of statements to EOF, returning a `Program` node.

## Part 3: AST Classes and Tooling

3a. Define node classes for every construct (`Num`, `Var`, `Str` if your lexer has strings, `BinOp`, `UnaryOp`, `LogicOp`, `Let`, `Assign`, `Print`, `Block`, `If`, `While`, `Program`), each with documented fields and a useful `__repr__`.

3b. `pretty(node)`: an indented tree printer.

3c. `unparse(node)`: produce valid source from a tree, inserting parentheses only where the tree's shape requires them, and verify the round-trip property `parse(unparse(parse(s)))` yields an equal tree (implement node equality or compare `pretty` outputs) across your whole test suite.

## Part 4: Errors

Run the five provided broken programs and five of your own through the parser; every message must state what was expected, what was found, and the line. Include the before-and-after of the one message you improved most.

## Deliverables

Submit a ZIP containing your parser and AST modules (importing your Lexer unchanged; note any Lexer bug fixes in the readme), the test suite with output, and a readme writeup of approximately one page including your final EBNF grammar exactly as implemented. Ensure reproducibility by listing software version information.

## Reflection Prompts

- Which tier's left-recursion-to-loop rewrite did you have to think hardest about, and what finally made it click?
- Your unparser had to decide where parentheses are necessary. State the rule you implemented in one sentence.
- If collaboration with a buddy was permitted, did you work with a buddy on this assignment? If so, who? If not, do you certify that this submission represents your own original work? Please identify any and all portions of your submission that were not originally written by you.
- Approximately how many hours it took you to finish this assignment (I will not judge you for this at all...I am simply using it to gauge if the assignments are too easy or hard)?
