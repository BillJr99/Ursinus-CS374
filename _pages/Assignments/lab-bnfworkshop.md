---
layout: assignment
permalink: /Assignments/BNFWorkshop
title: "CS374: Principles of Programming Languages - Lab: BNF Workshop"

info:
  coursenum: CS374
  purpose: "To get early, low-stakes practice writing grammars: EBNF for two small languages, Chomsky-level classification, and a design-criteria argument, the skill the Parser stretch of the course leans on hardest."
  tilt:
    task: "With a partner, write EBNF grammars for two toy languages, classify a set of sample languages by Chomsky level, and argue one syntax design choice against the readability/writability/reliability criteria."
    criteria: "Assessed on correct and complete EBNF grammars, correct Chomsky classifications with reasons, and a criteria-grounded design argument, weighted 50/30/20 across the three parts; see the rubric below for the full breakdown."
  points: 100
  goals:
    - To write EBNF grammars for small formal languages
    - To classify languages by Chomsky hierarchy level and justify each classification
    - To evaluate a syntax design choice against the readability, writability, and reliability criteria
  rubric:
    - weight: 50
      description: "EBNF Grammars (Goal 1)"
      preemerging: Grammars are missing or do not use BNF/EBNF notation
      beginning: One grammar is attempted but accepts clearly invalid strings or rejects clearly valid ones
      progressing: Both grammars are written and mostly correct, but one has an undefined nonterminal or accepts an edge case it should reject (or vice versa)
      proficient: Both grammars are complete and correct EBNF; every nonterminal defined, repetition and optionality expressed with EBNF operators rather than ad-hoc prose, and each is accompanied by three strings it accepts and two it rejects, verified by hand against the productions
    - weight: 30
      description: "Chomsky Classification (Goal 2)"
      preemerging: No classifications, or levels are assigned without reasons
      beginning: Some classifications are correct but reasons restate the level name rather than the structural property
      progressing: All classifications are correct but one or two reasons miss the structural property that forces the level (e.g., nesting requiring a stack)
      proficient: Every sample language is classified correctly with a one-sentence reason naming the structural property that forces its level (finite memory suffices; matching/nesting needs a stack; cross-serial constraints need more), and the writeup names which level the class language's tokens versus its full syntax will each need
    - weight: 20
      description: "Design-Criteria Argument (Goal 3)"
      preemerging: No argument, or the argument does not reference the course criteria
      beginning: The argument names a criterion but does not connect the syntax choice to a concrete consequence for programmers
      progressing: The argument connects the choice to two criteria with concrete consequences but does not acknowledge the tradeoff
      proficient: The argument evaluates the choice against at least two of readability, writability, and reliability with concrete programmer-facing consequences, states the tradeoff plainly, and takes a defensible position
  readings:
    - rtitle: "Syntax and BNF/EBNF Activity"
      rlink: "https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374/gh-pages/_pages/Activities/liascript-syntaxbnf.md"
    - rtitle: "Grammars and the Chomsky Hierarchy Activity"
      rlink: "https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374/gh-pages/_pages/Activities/liascript-grammars.md"
    - rtitle: "Evaluating Languages Activity"
      rlink: "https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374/gh-pages/_pages/Activities/liascript-languageevaluation.md"

tags:
  - grammars
  - syntax
  - theory
  - languages
  - lab

---

This **lab** is your first grammar-writing rep, taken while the stakes are low: two small EBNF grammars, a Chomsky-classification exercise, and one design argument. Grammar-writing is the skill the Parser assignment leans on hardest, and the Grammar and Derivations Workshop later asks you to do this for the real class language; this lab is the warm-up on toy examples. It is entirely on paper (or in a markdown file); budget **two to three hours** with a partner.

**Pair policy:** this lab may be completed **in pairs**: one partner proposes a production, the other tries to break it with a string it mis-handles. Both partners submit the same document, each naming the other, and both earn the same grade. (You may also work alone.)

See the course schedule for the assigned and due dates. Derivation trees and ambiguity get their own treatment later, in class and in the Grammar and Derivations Workshop; here the job is just to write grammars that draw the right boundary.

---

## Part 1: Two EBNF Grammars (50 points)

Write a complete EBNF grammar for each, in `grammars.md`, and verify each by hand with **three accepted and two rejected strings**:

1. **Phone directory entries**: lines of the form `NAME: (610) 555-0123` or `NAME: 555-0123`, where a name is one or more capitalized words. The area code is optional; the punctuation is not.
2. **A tiny configuration language**: zero or more lines of `key = value;`, where a key is an identifier, and a value is an integer, a quoted string, or a bracketed comma-separated list of values (lists nest: `themes = ["dark", ["contrast", "high"]];`).

Use EBNF's operators for repetition (`{ }`), optionality (`[ ]`), and grouping; the point of the exercise is expressing shape declaratively rather than in prose.

## Part 2: Chomsky Classification (30 points)

For each language below, name the lowest Chomsky level that can describe it and give a one-sentence reason naming the structural property that forces it:

1. Binary strings with an even number of 1s.
2. Balanced parentheses.
3. Your Part 1 configuration language (careful: the values nest).
4. Identifiers matching `[A-Za-z_][A-Za-z0-9_]*`.
5. Strings of the form `a^n b^n c^n` (equal counts of all three).

Close with one sentence each: which level do the class language's *tokens* need, and which does its *full syntax* need, and what does that split tell you about why compilers have both a lexer and a parser?

## Part 3: Design-Criteria Argument (20 points)

The configuration language's designer proposes making the trailing `;` optional. In one paragraph, evaluate the proposal against at least two of the **readability, writability, and reliability** criteria from the Evaluating Languages session, with a concrete consequence for each (what a programmer gains or loses), state the tradeoff, and take a position.

---

## Deliverables

Submit `grammars.md` containing all three parts, with both partners named at the top.

## Grading Breakdown

| Component | Points |
|-----------|--------|
| Part 1: EBNF Grammars | 50 |
| Part 2: Chomsky Classification | 30 |
| Part 3: Design-Criteria Argument | 20 |
| **Total** | **100** |

## Reflection Prompts

- Which string broke your first draft of a grammar, and what production fixed it?
- If you worked in a pair, who did what, and name one thing your partner caught that you would have missed. If you worked alone, note that instead.
- AI disclosure: list any generative-AI tools you used, for what, and how you verified the results (or state 'none').
- Approximately how many hours it took you to finish this lab (I will not judge you for this at all; I am simply using it to gauge if the labs are too easy or hard)?
