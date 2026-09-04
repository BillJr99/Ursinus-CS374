---
layout: assignment
permalink: /Assignments/BNFWorkshop
title: "CS374: Principles of Programming Languages - Lab: BNF Workshop"

info:
  coursenum: CS374
  purpose: "To get early practice writing grammars while the stakes are still low: EBNF grammars for two small languages, a Chomsky-level classification, and a design-criteria argument.  Grammar writing is the skill the Parser stretch of the course leans on hardest."
  tilt:
    task: "With a partner, write EBNF grammars for two toy languages, classify a set of sample languages by Chomsky level, and argue one syntax design choice against the readability, writability, and reliability criteria."
    criteria: "I grade your work on correct and complete EBNF grammars, correct Chomsky classifications with reasons, and a design argument grounded in the course criteria, weighted 50/30/20 across the three parts.  See the rubric below for the full breakdown."
  points: 100
  goals:
    - To write EBNF grammars for small formal languages
    - To classify languages by Chomsky hierarchy level and justify each classification
    - To evaluate a syntax design choice against the readability, writability, and reliability criteria
  rubric:
    - weight: 10
      description: "Part 0: Before You Start - Syntax, BNF/EBNF, and Grammars"
      preemerging: No grammar of your own is drafted and no derivation is attempted
      beginning: A BNF grammar is drafted but it is not extended to EBNF, or no derivation is produced
      progressing: A BNF grammar is drafted and extended to EBNF and a derivation is given, but the write-up does not say what EBNF made shorter, or does not justify the non-generated string
      proficient: A BNF grammar of your own is drafted and extended to EBNF with a note on exactly what the EBNF notation bought you; a leftmost derivation of a generated string is shown; and a string the grammar cannot generate is given with an argument for how you know
    - weight: 45
      description: "EBNF Grammars (Goal 1)"
      preemerging: Grammars are missing or do not use BNF/EBNF notation
      beginning: One grammar is attempted but accepts clearly invalid strings or rejects clearly valid ones
      progressing: Both grammars are written and mostly correct, but one has an undefined nonterminal or accepts an edge case it should reject (or vice versa)
      proficient: Both grammars are complete and correct EBNF; every nonterminal is defined, repetition and optionality use EBNF operators rather than prose, and each grammar comes with three strings it accepts and two it rejects, verified by hand against the productions
    - weight: 27
      description: "Chomsky Classification (Goal 2)"
      preemerging: No classifications, or levels are assigned without reasons
      beginning: Some classifications are correct but reasons restate the level name rather than the structural property
      progressing: All classifications are correct but one or two reasons miss the structural property that forces the level (e.g., nesting requiring a stack)
      proficient: Every sample language is classified correctly with a one-sentence reason naming the structural property that forces its level (finite memory suffices; matching/nesting needs a stack; cross-serial constraints need more), and the write-up names which level the class language's tokens and its full syntax will each need
    - weight: 18
      description: "Design-Criteria Argument (Goal 3)"
      preemerging: No argument, or the argument does not reference the course criteria
      beginning: The argument names a criterion but does not connect the syntax choice to a concrete consequence for programmers
      progressing: The argument connects the choice to two criteria with concrete consequences but does not acknowledge the tradeoff
      proficient: The argument evaluates the choice against at least two of readability, writability, and reliability with concrete programmer-facing consequences, states the tradeoff plainly, and takes a defensible position
  readings:
    - rtitle: "Syntax and BNF/EBNF Activity"
      rlink: "Activities/liascript-syntaxbnf.md"
      liapage: true
    - rtitle: "Grammars and the Chomsky Hierarchy Activity"
      rlink: "Activities/liascript-grammars.md"
      liapage: true
    - rtitle: "Evaluating Languages Activity"
      rlink: "Activities/liascript-languageevaluation.md"
      liapage: true

tags:
  - grammars
  - syntax
  - theory
  - languages
  - lab

---

This **lab** is your first practice at writing grammars, done while the stakes are low.  You write two small EBNF grammars, classify five sample languages by Chomsky level, and make one design argument.  Grammar writing is the skill the Parser assignment leans on hardest, and the Grammar and Derivations Workshop later asks you to write a grammar for the real class language.  This lab is the warm-up on toy examples.  You do it on paper, or in a markdown file if you prefer, and you do it with a partner.

A grammar is a set of rules that says which strings belong to a language.  BNF (Backus-Naur Form) is a notation for writing those rules.  EBNF (Extended BNF) adds operators for repetition, optional parts, and grouping, so the same rules take fewer lines.

**Pair policy.**  You may do this lab in pairs.  One partner proposes a production (a single grammar rule), and the other tries to break it with a string the rule handles wrongly.  Submit one document between you, with each of you naming the other, and you both earn the same grade.  Working alone is fine too.

See the course schedule for the assigned and due dates.  Derivation trees and ambiguity get their own treatment later, in class and in the Grammar and Derivations Workshop.  Here the job is to write grammars that draw the right boundary between strings that belong to the language and strings that do not.

---

## Part 0: Before You Start - Syntax, BNF/EBNF, and Grammars (10 points)

Do this part before the Syntax and BNF/EBNF session, not after.  Fifteen minutes and a pencil will do it.  You may do this part alone even though the rest of this lab is pair work.

You can follow a grammar on a page without being able to write one.  Writing even a tiny grammar forces the decisions the reading makes look obvious: what counts as a terminal (a symbol that appears in the string itself), where the recursion goes, and what the notation is buying you.

1.  Write a BNF grammar for a small language of your choice.  Signed decimal numbers works; so does a boolean expression with `and`, `or`, and `not`.
2.  Extend that grammar to EBNF.  Note in one sentence what the EBNF made shorter.
3.  Take a short grammar from the reading and produce a leftmost derivation of one string it generates.  A leftmost derivation starts from the start symbol and, at each step, replaces the leftmost nonterminal (a symbol that still has a rule to apply) using one production.
4.  Give a string that grammar cannot generate, and explain how you know.

Bring the grammar you drafted, and mark the rule you are least sure about.  Rough edges are expected.  That uncertain rule is usually the best discussion of the day.

---

## Part 1: Two EBNF Grammars (45 points)

Write a complete EBNF grammar for each language below in `grammars.md`.  Then verify each grammar by hand with three strings it accepts and two it rejects.

1.  Phone directory entries: lines of the form `NAME: (610) 555-0123` or `NAME: 555-0123`, where a name is one or more capitalized words.  The area code is optional; the punctuation is not.
2.  A tiny configuration language: zero or more lines of `key = value;`, where a key is an identifier, and a value is an integer, a quoted string, or a bracketed comma-separated list of values (lists nest: `themes = ["dark", ["contrast", "high"]];`).

Use EBNF's operators for repetition (`{ }`), optionality (`[ ]`), and grouping.  The point of the exercise is to express shape in the notation rather than in prose.

## Part 2: Chomsky Classification (27 points)

The Chomsky hierarchy ranks languages by how much memory a machine needs to recognize them.  Regular languages need only finite memory.  Context-free languages need a stack, because they match or nest symbols.  Languages with cross-serial constraints, such as equal counts in three separate places, need more than a stack.

For each language below, name the lowest Chomsky level that can describe it.  Give a one-sentence reason that names the structural property forcing that level.

1.  Binary strings with an even number of 1s.
2.  Balanced parentheses.
3.  Your Part 1 configuration language (careful: the values nest).
4.  Identifiers matching `[A-Za-z_][A-Za-z0-9_]*`.
5.  Strings of the form `a^n b^n c^n` (equal counts of all three).

Close with one sentence for each of these three questions.  Which level do the class language's tokens need?  Which level does its full syntax need?  What does that split tell you about why compilers have both a lexer and a parser?

## Part 3: Design-Criteria Argument (18 points)

The configuration language's designer proposes making the trailing `;` optional.  Write one paragraph that evaluates the proposal against at least two of the readability, writability, and reliability criteria from the Evaluating Languages session.  For each criterion, give a concrete consequence: what a programmer gains or loses.  State the tradeoff, and take a position.

---

## Deliverables

Submit `grammars.md` containing all three parts, with both partners named at the top.

## Grading Breakdown

| Component | Points |
|-----------|--------|
| Part 0: Syntax, BNF/EBNF, and Grammars | 10 |
| Part 1: EBNF Grammars | 45 |
| Part 2: Chomsky Classification | 27 |
| Part 3: Design-Criteria Argument | 18 |
| **Total** | **100** |

## Reflection Prompts

- Which string broke your first draft of a grammar, and what production fixed it?
- If you worked in a pair, who did what, and name one thing your partner caught that you would have missed.  If you worked alone, note that instead.
- AI disclosure: list any generative-AI tools you used, for what, and how you verified the results (or state 'none').
- Approximately how many hours it took you to finish this lab (I will not judge you for this at all; I am simply using it to gauge if the labs are too easy or hard)?
