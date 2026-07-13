---
layout: assignment
permalink: /Assignments/TypeCheckerLab
title: "CS374: Principles of Programming Languages - Lab: Type Checker Starter"

info:
  coursenum: CS374
  purpose: "To build the core of the Interpreter assignment's required static type checker with a partner — literal, variable, and operator checks over the class AST, running before any code is evaluated."
  tilt:
    task: "With a partner, implement a checker that walks the class AST with a type environment, verifying annotated declarations, variable uses, and operator applications, and reporting positioned type errors."
    criteria: "Assessed on a checker that accepts the well-typed programs and rejects each ill-typed program with a positioned two-type error message, plus a set of typing-rule statements written on paper, weighted 70/30 across the two parts; see the rubric below for the full breakdown."
  points: 100
  goals:
    - To implement a static checking pass over the class AST using a type environment that mirrors the Environment class
    - To check annotated declarations, variable uses, and operator applications, reporting errors with positions and both conflicting types
    - To state typing rules precisely on paper before encoding them
  rubric:
    - weight: 70
      description: "The Checker Core (Goals 1, 2)"
      preemerging: The checker is missing, or it never rejects an ill-typed program
      beginning: The checker rejects some ill-typed programs but misses operator mismatches, or it crashes on programs it should reject cleanly
      progressing: All provided ill-typed programs are rejected, but error messages lack positions or name only one of the two conflicting types
      proficient: Every provided well-typed program is accepted and every ill-typed program rejected with a message of the form "Type error at line L, col C" naming both conflicting types; the type environment correctly scopes annotations through nested blocks
    - weight: 30
      description: "Typing Rules on Paper (Goal 3)"
      preemerging: No rules are written, or they contradict the implemented checker
      beginning: Rules are written for literals only
      progressing: Rules cover literals, variables, and operators but at least one rule is imprecise about its premises
      proficient: Each covered construct has a precise rule (premises above, conclusion below, or a disciplined if/then sentence), and each rule cites the checker function that implements it
  readings:
    - rtitle: "Type Systems Activity"
      rlink: "https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374/gh-pages/_pages/Activities/liascript-types.md"
    - rtitle: "Core Tutorial: Typing Disciplines — Strong vs. Weak, Static vs. Dynamic, and Gradual Typing"
      rlink: "https://www.billmongan.com/Ursinus-CS374-Fall2026/Tutorials/TypingDisciplines"

tags:
  - interpreter
  - types
  - languages
  - lab

---

This **lab** builds the core of the Interpreter assignment's Part 4 — the small static type checker that runs between parsing and evaluation. Here you get the machinery working on the checker's three foundational cases (literals, variables, operators) with a partner; the assignment then extends it to call sites and return types on your own. Budget **two to three hours**.

**Pair policy:** this lab may be completed **in pairs**. Both partners submit the same files, each naming the other, and both earn the same grade. (You may also work alone.) The Interpreter assignment remains individual work: you may both carry this shared checker core into it, but the extension to calls and returns must be your own.

---

## Part 1: The Checker Core (70 points)

Implement `check(program) -> None` in `typechecker.py`, walking the class AST (use your Parser assignment's AST nodes, or the reference AST) with a **type environment** — the same parent-chaining discipline as your Environments lab, but binding names to *types* rather than values:

- **Literals:** numbers are `Num`, strings are `Str`, booleans are `Bool`.
- **Declarations:** `let x: Num = expr;` checks that `expr`'s type equals the annotation, then binds `x : Num` in the current scope. A mismatch is an error naming both types.
- **Variables:** a use of `x` looks up its declared type; an undeclared use is a positioned error.
- **Operators:** `+ - * /` require `Num` operands and yield `Num`; `< <= > >=` require `Num` and yield `Bool`; `== !=` require both sides to have the same type and yield `Bool`; `and`/`or`/`not` require `Bool`. Every violation is reported as `Type error at line L, col C: ...` naming **both** conflicting types.

Verify against the provided programs (course starter repo): six well-typed programs that must pass silently, and six ill-typed programs that must each produce a positioned error — including the classic `let x: Num = 1 + true;` (error *before* anything runs) and a shadowing case where an inner `let x: Str` legitimately changes the type of `x` for the inner scope only.

## Part 2: Typing Rules on Paper (30 points)

In `RULES.md`, state the typing rule for each construct your checker covers — one rule per construct, premises and conclusion, in either inference-rule layout or a disciplined "if... then..." sentence (e.g., *if `e1 : Num` and `e2 : Num`, then `e1 + e2 : Num`*). Cite, for each rule, the function or branch in `typechecker.py` that implements it. This document becomes the seed of the Interpreter assignment's semantics writeup — and if you later choose the full Hindley-Milner direction, these rules are exactly what inference generalizes.

Close `RULES.md` with two theory questions from the Type Systems session: (1) place four languages — Python, C, Haskell, and JavaScript — on the **static/dynamic × strong/weak** quadrant, with one sentence of justification each; (2) your checker makes the class language *gradually* typed in spirit (annotated declarations are checked, unannotated territory is documented as unchecked) — state one benefit and one risk of that middle ground, using the mypy/TypeScript comparison from class.

---

## Deliverables

Submit a ZIP containing `typechecker.py`, the run log over the twelve provided programs, and `RULES.md` with both partners named.

## Grading Breakdown

| Component | Points |
|-----------|--------|
| Part 1: The Checker Core | 70 |
| Part 2: Typing Rules on Paper | 30 |
| **Total** | **100** |

## Reflection Prompts

- Your checker rejects `while 1 { ... }` if you require a `Bool` condition, though the evaluator's truthiness rule would happily run it. Which behavior do you consider correct for the class language, and why?
- If you worked in a pair, who did what, and name one thing your partner caught that you would have missed. If you worked alone, note that instead.
- AI disclosure: list any generative-AI tools you used, for what, and how you verified the results (or state 'none').
- Approximately how many hours it took you to finish this lab (I will not judge you for this at all — I am simply using it to gauge if the labs are too easy or hard)?
