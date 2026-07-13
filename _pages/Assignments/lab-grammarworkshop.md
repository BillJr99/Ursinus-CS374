---
layout: assignment
permalink: /Assignments/GrammarWorkshop
title: "CS374: Principles of Programming Languages - Lab: Grammar and Derivations Workshop"

info:
  coursenum: CS374
  purpose: "To complete the Parser assignment's grammar work with a partner — a full EBNF grammar for the class language, derivations that prove it produces the programs you expect, and precedence decisions you can defend."
  tilt:
    task: "With a partner, write the EBNF grammar the Parser assignment's Part 1 requires, produce leftmost derivations and parse trees for two worked programs, and demonstrate how the grammar's shape enforces precedence and associativity."
    criteria: "Assessed on a complete and correct EBNF grammar, correct derivations with matching parse trees, and a demonstrated precedence/ambiguity analysis, weighted 50/25/25 across the three parts; see the rubric below for the full breakdown."
  points: 100
  goals:
    - To write a complete EBNF grammar for the class language's expressions and statements
    - To construct leftmost derivations and parse trees that verify the grammar against concrete programs
    - To explain how grammar structure (the expression ladder) enforces precedence and associativity and eliminates ambiguity
  rubric:
    - weight: 50
      description: "EBNF Grammar (Goal 1)"
      preemerging: The grammar is missing most constructs or does not use EBNF notation
      beginning: The grammar covers expressions or statements but not both, or several productions reference undefined nonterminals
      progressing: The grammar is complete but flat — precedence levels are missing, so it is ambiguous for arithmetic
      proficient: The grammar covers every expression and statement form of the class language in correct EBNF, with a tiered expression ladder (one production per precedence level) and no undefined nonterminals
    - weight: 25
      description: "Derivations and Parse Trees (Goal 2)"
      preemerging: No derivation is attempted, or the derivations do not follow the submitted grammar
      beginning: One program is derived but with skipped steps, or the parse tree does not match the derivation
      progressing: Both programs are derived with matching trees, but one derivation has a misapplied production
      proficient: Both worked programs have complete leftmost derivations, every step citing the production applied, with parse trees that match the derivations exactly
    - weight: 25
      description: "Precedence and Ambiguity Analysis (Goal 3)"
      preemerging: No analysis, or the analysis restates notes without using the submitted grammar
      beginning: The analysis asserts precedence works but shows no derivation-level evidence
      progressing: The analysis shows the correct tree for the precedence example but does not explain which grammar feature forces it
      proficient: The analysis derives the precedence example, names the exact productions that force multiplication to bind tighter than addition and subtraction to associate left, and shows what a flat one-level grammar would have permitted instead
  readings:
    - rtitle: "Recursive Descent Parsing Activity"
      rlink: "https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374/gh-pages/_pages/Activities/liascript-recursivedescent.md"
    - rtitle: "Parsing Expressions Activity"
      rlink: "https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374/gh-pages/_pages/Activities/liascript-parsingexpressions.md"

tags:
  - grammars
  - parsing
  - languages
  - lab

---

This **lab** is the Parser assignment's Part 1, done early and with a partner: the EBNF grammar that your recursive-descent parser will transcribe function-by-function. Getting the grammar right on paper first is the highest-leverage two hours of the whole Parser assignment — every parsing function you write next week is one production from this document. Budget **two to three hours**; it is due mid-assignment, before the parsing code gets serious.

**Pair policy:** this lab may be completed **in pairs**. Grammar design benefits from argument — one partner proposes a production, the other tries to break it with a program it mis-derives. Both partners submit the same document, each naming the other, and both earn the same grade. (You may also work alone.) The Parser assignment remains individual work: you may both build on this shared grammar, but your parsers are your own.

---

## Part 1: The EBNF Grammar (50 points)

Write the complete EBNF grammar for the class language used across the Lexer, Parser, and Interpreter assignments: `let`/assignment/`print` statements, `if`/`else`, `while` with blocks, and expressions over numbers, strings, booleans, identifiers, calls, and the arithmetic/comparison/logical operators. Structure the expression productions as a **ladder** — one production per precedence level, from `or` at the top down through `and`, comparison, additive, multiplicative, unary, and primary — exactly the shape the Parser assignment's Part 2 transcribes into functions.

## Part 2: Derivations and Parse Trees (25 points)

Produce a **leftmost derivation** (every step citing the production applied) and the matching **parse tree** for both:

1. `let x = 1 + 2 * 3;`
2. `while x < 10 { x = x + 1; }`

## Part 3: Precedence and Ambiguity (25 points)

Using your derivation of program 1, explain which productions force `*` to bind tighter than `+`, and show the (wrong) second tree a flat single-level expression grammar would also permit. Then state how your grammar makes `1 - 2 - 3` associate left, and verify with a three-line derivation sketch.

---

## Deliverables

Submit `grammar.md` containing all three parts, with both partners named at the top. Bring it to the Parser assignment: its Part 1 asks you to include (and refine, if the coding surfaces issues) exactly this grammar.

## Grading Breakdown

| Component | Points |
|-----------|--------|
| Part 1: EBNF Grammar | 50 |
| Part 2: Derivations and Parse Trees | 25 |
| Part 3: Precedence and Ambiguity Analysis | 25 |
| **Total** | **100** |

## Reflection Prompts

- Which production went through the most revisions before your partner could no longer break it, and what broke it last?
- If you worked in a pair, who did what, and name one thing your partner caught that you would have missed. If you worked alone, note that instead.
- AI disclosure: list any generative-AI tools you used, for what, and how you verified the results (or state 'none').
- Approximately how many hours it took you to finish this lab (I will not judge you for this at all — I am simply using it to gauge if the labs are too easy or hard)?
