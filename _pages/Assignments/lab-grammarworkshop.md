---
layout: assignment
permalink: /Assignments/GrammarWorkshop
title: "CS374: Principles of Programming Languages - Lab: Grammar and Derivations Workshop"

info:
  coursenum: CS374
  purpose: "To complete the Parser assignment's grammar work with a partner by writing a full EBNF grammar for the class language, deriving programs that prove it produces what you expect, and settling precedence decisions you can defend."
  tilt:
    task: "With a partner, write the EBNF grammar the Parser assignment's Part 1 requires, produce leftmost derivations and parse trees for two worked programs, and demonstrate how the grammar's shape enforces precedence and associativity."
    criteria: "I grade this on a complete and correct EBNF grammar, correct derivations with matching parse trees, and a demonstrated precedence/ambiguity analysis, weighted 50/25/25 across the three parts.  The rubric below has the details."
  points: 100
  goals:
    - To write a complete EBNF grammar for the class language's expressions and statements
    - To construct leftmost derivations and parse trees that verify the grammar against concrete programs
    - To explain how grammar structure (the expression ladder) enforces precedence and associativity and eliminates ambiguity
  rubric:
    - weight: 10
      description: "Part 0: Before You Start - Derivations, Ambiguity, and Precedence"
      preemerging: No parse trees are drawn
      beginning: One parse tree is drawn, so the ambiguity is asserted rather than shown
      progressing: Two distinct parse trees are drawn for one string, but the grammar is not rewritten to remove the ambiguity, or the associativity trees are missing
      proficient: Two distinct parse trees are drawn for one string of an ambiguous grammar; the grammar is rewritten so only one survives, with the place marked where encoding precedence made a rule harder to read; and both the left- and right-associative trees for 2 - 3 - 4 are drawn, with your language's actual choice confirmed in a REPL
    - weight: 45
      description: "EBNF Grammar (Goal 1)"
      preemerging: The grammar is missing most constructs or does not use EBNF notation
      beginning: The grammar covers expressions or statements but not both, or several productions reference undefined nonterminals
      progressing: The grammar is complete but flat, precedence levels are missing, so it is ambiguous for arithmetic
      proficient: The grammar covers every expression and statement form of the class language in correct EBNF, with a tiered expression ladder (one production per precedence level) and no undefined nonterminals
    - weight: 23
      description: "Derivations and Parse Trees (Goal 2)"
      preemerging: No derivation is attempted, or the derivations do not follow the submitted grammar
      beginning: One program is derived but with skipped steps, or the parse tree does not match the derivation
      progressing: Both programs are derived with matching trees, but one derivation has a misapplied production
      proficient: Both worked programs have complete leftmost derivations, every step citing the production applied, with parse trees that match the derivations exactly
    - weight: 22
      description: "Precedence and Ambiguity Analysis (Goal 3)"
      preemerging: No analysis, or the analysis restates notes without using the submitted grammar
      beginning: The analysis asserts precedence works but shows no derivation-level evidence
      progressing: The analysis shows the correct tree for the precedence example but does not explain which grammar feature forces it
      proficient: The analysis derives the precedence example, names the exact productions that force multiplication to bind tighter than addition and subtraction to associate left, and shows what a flat one-level grammar would have permitted instead
  readings:
    - rtitle: "Recursive Descent Parsing Activity"
      rlink: "Activities/liascript-recursivedescent.md"
      liapage: true
    - rtitle: "Parsing Expressions Activity"
      rlink: "Activities/liascript-parsingexpressions.md"
      liapage: true

tags:
  - grammars
  - parsing
  - languages
  - lab

---

This **lab** is the Parser assignment's Part 1, done early and with a partner.  You write the EBNF grammar that your recursive-descent parser will transcribe function by function.  Getting the grammar right on paper first pays off more than anything else you do in the Parser assignment, because every parsing function you write there is one production from this document.  It is due mid-assignment, before the parsing code gets serious.

**Pair policy.**  You may do this lab **in pairs**.  Grammar design benefits from argument: one partner proposes a production, the other tries to break it with a program it mis-derives.  Turn in the same document, each of you naming the other, and you will both get the same grade.  Working alone is allowed.  The Parser assignment remains individual work: you may both build on this shared grammar, but your parsers are your own.

---

## Part 0: Before You Start — Derivations, Ambiguity, and Precedence (10 points)

Do this one **first**, before the rest of the lab, and ideally before the Derivations, Parse Trees, Ambiguity, and Precedence session.  You may do it alone even though the rest of this lab is pair work.

Ambiguity stops being subtle the moment you have drawn it twice.  Draw both trees, then rewrite the grammar until only one drawing survives.  That rewrite is the whole technique, and doing it once by hand teaches more than reading three descriptions of it.

1.  **Show that a given expression grammar is ambiguous** by drawing two distinct parse trees for one string.  Then rewrite the grammar to encode precedence and associativity so the ambiguity is gone.  Mark the place where encoding precedence made a rule *harder to read* — that cost is real, and Part 3 will ask you to defend paying it.
2.  **Take `2 - 3 - 4`** and draw the parse tree that makes subtraction left-associative, then the one that makes it right-associative.  Which does your favorite language use?  Confirm it in a REPL rather than guessing.

If the rewrite fell apart on you, bring it anyway.  Where it fell apart is what the session is for.

---

## Part 1: The EBNF Grammar (45 points)

Write the complete EBNF grammar for the class language used across the Lexer, Parser, and Interpreter assignments: `let`/assignment/`print` statements, `if`/`else`, `while` with blocks, and expressions over numbers, strings, booleans, identifiers, calls, and the arithmetic/comparison/logical operators.  Structure the expression productions as a **ladder**: one production per precedence level, from `or` at the top down through `and`, comparison, additive, multiplicative, unary, and primary, exactly the shape the Parser assignment's Part 2 transcribes into functions.

## Part 2: Derivations and Parse Trees (23 points)

Produce a **leftmost derivation** (every step citing the production applied) and the matching **parse tree** for both:

1. `let x = 1 + 2 * 3;`
2. `while x < 10 { x = x + 1; }`

## Part 3: Precedence and Ambiguity (22 points)

Using your derivation of program 1, explain which productions force `*` to bind tighter than `+`, and show the (wrong) second tree a flat single-level expression grammar would also permit.  Then state how your grammar makes `1 - 2 - 3` associate left, and verify with a three-line derivation sketch.

---

## Deliverables

Submit `grammar.md` containing all three parts, with both partners named at the top.  Bring it to the Parser assignment: its Part 1 asks you to include (and refine, if the coding surfaces issues) exactly this grammar.

## Grading Breakdown

| Component | Points |
|-----------|--------|
| Part 0: Derivations, Ambiguity, and Precedence | 10 |
| Part 1: EBNF Grammar | 45 |
| Part 2: Derivations and Parse Trees | 23 |
| Part 3: Precedence and Ambiguity Analysis | 22 |
| **Total** | **100** |

## Reflection Prompts

- Which production went through the most revisions before your partner could no longer break it, and what broke it last?
- If you worked in a pair, who did what, and name one thing your partner caught that you would have missed.  If you worked alone, note that instead.
- AI disclosure: list any generative-AI tools you used, for what, and how you verified the results (or state 'none').
- Approximately how many hours it took you to finish this lab (I will not judge you for this at all; I am simply using it to gauge if the labs are too easy or hard)?
