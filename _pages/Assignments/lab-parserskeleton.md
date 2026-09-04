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

In this lab you build the bottom two tiers of a recursive descent parser: `parse_primary` and `parse_unary`.  A recursive descent parser is a parser written as one function per grammar rule, where each function calls the functions for the rules it uses.  These two functions set the pattern every other tier of the Parser assignment repeats: look at `peek()`, decide which rule applies, consume tokens with `advance()` or `expect()`, and return a node.  Finishing them now means the hardest stretch of the Parser assignment starts from working code instead of a blank file.  You do this lab with a partner.

Use your own Lexer or the released Reference Lexer.  Either one satisfies the interface contract.  This lab is a good first test of whichever one you plan to build the Parser assignment on.

**Pair policy.**  You may do this lab in pairs.  Driver/navigator works well; swap roles between the two tiers.  Submit the same files, name your partner, and you both receive the same grade.  Working alone is fine as well.  The Parser assignment remains individual work: you may both grow this shared skeleton there, but the remaining tiers are your own.

See the course schedule for the assigned and due dates.

---

## Part 0: Before You Start - Recursive Descent Parsing (10%)

Do this part on paper before you write `parse_primary`, and ideally before the Recursive Descent Parsing session.  You may do it alone even though the rest of this lab is pair work.

Tracing one function on three tokens shows you exactly where lookahead lives.  Lookahead is the token the parser inspects without consuming, so that it can decide which rule applies.

1.  Write the pseudocode for the recursive-descent function of one non-terminal in a small expression grammar.  (A non-terminal is a grammar symbol defined by rules, such as `expression` or `term`.)  Trace it by hand on a three-token input and mark every point where it looks ahead.
2.  Find a grammar rule that would make naive recursive descent loop forever.  This is left recursion: a rule whose right-hand side begins with the same non-terminal it defines, so the function calls itself before consuming anything.  Rewrite the rule so the function terminates.

Bring the trace, with the point marked where you needed more than one token of lookahead.  A trace that broke down partway is still worth bringing.  The peek/decide/consume pattern you build in Part 1 is the fix for wherever it broke.

---

## Part 1: The First Two Tiers (63%)

In `parser_skeleton.py`, first define the AST (abstract syntax tree) node dataclasses you need: `Num`, `Str`, `Bool`, `Var`, `Unary`, plus a `Grouping` node or a pass-through for parentheses.  Match the node names your grammar work uses.  Then implement two functions:

- `parse_primary` handles number, string, and boolean literals; identifiers; and `( expression )`.  For this lab, a parenthesized expression may recurse into `parse_unary`; the full expression ladder arrives in the Parser assignment.
- `parse_unary` handles `-` and `not`.  Both are right-associative and nest (`--x`, `not not ok`).  At the bottom it delegates to `parse_primary`.

Both functions consume tokens only through the Lexer's `peek`, `advance`, and `expect`.  The whole ladder depends on that discipline.  Document the pattern in one sentence per function.

## Part 2: Tests and Errors (27%)

In `test_skeleton.py`, write tree-shape tests.  A tree-shape test asserts on node types and fields, for example `isinstance(node, Unary)`, `node.op == "-"`, and `node.operand.value == 42`.  Never compare printed strings.  Cover every primary form and at least two nested unary cases.

Then make failure informative.  Parsing an input that cannot start an expression (for example, `;`) must raise a `ParseError` that states what was expected, what was found, and the line and column of the offending token.

---

## Deliverables

Submit a ZIP containing `parser_skeleton.py`, `test_skeleton.py` with its passing output captured, and a readme line naming both partners and stating whether you built on your own Lexer or the reference.

## Grading Breakdown

This lab is worth 15 points, as the course schedule states.  Each part's weight below is a percentage of those 15 points, and the rubric rows use the same percentages.

| Component | Weight |
|-----------|--------|
| Part 0: Recursive Descent Parsing | 10% |
| Part 1: The First Two Tiers | 63% |
| Part 2: Tests and Errors | 27% |
| **Total** | **100% (15 points)** |

## Reflection Prompts

- State the peek/decide/consume pattern in your own words, and name which remaining tier of the Parser assignment you expect to repeat it most times.
- If you worked in a pair, who did what, and name one thing your partner caught that you would have missed.  If you worked alone, note that instead.
- AI disclosure: list any generative-AI tools you used, for what, and how you verified the results (or state 'none').
- Approximately how many hours it took you to finish this lab (I will not judge you for this at all; I am simply using it to gauge if the labs are too easy or hard)?
