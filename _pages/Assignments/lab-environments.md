---
layout: assignment
permalink: /Assignments/EnvironmentsLab
title: "CS374: Principles of Programming Languages - Lab: Environments and Scope"

info:
  coursenum: CS374
  purpose: "To build the Interpreter assignment's Environment class with a partner: nested scopes, define versus assign, and shadowing, verified against the exact behaviors the Interpreter's evaluator depends on."
  tilt:
    task: "With a partner, implement an Environment class with parent chaining, distinguish define from assign, and verify shadowing, scope restoration, and name-error behavior against a provided test script."
    criteria: "Assessed on a correct Environment class passing all provided behavior tests and a short trace exercise predicting scope behavior on paper, weighted 70/30 across the two parts; see the rubric below for the full breakdown."
  points: 100
  goals:
    - To implement an Environment class with parent chaining supporting nested scopes
    - To distinguish definition (creating a name in the current scope) from assignment (updating the nearest enclosing binding)
    - To verify shadowing, scope restoration, and name-error behavior with tests and paper traces
  rubric:
    - weight: 70
      description: "The Environment Class (Goals 1, 2)"
      preemerging: The class is missing, or lookup does not consult parent scopes
      beginning: Lookup chains to parents but define and assign are conflated, so inner assignment creates shadows instead of updating
      progressing: Define/assign are distinguished and shadowing works, but assignment to an undefined name does not raise a language-level error, or exiting a scope fails to restore the outer binding
      proficient: define creates in the current scope, assign updates the nearest enclosing binding and raises a positioned language-level name error when no binding exists, lookup chains correctly to any depth, shadowing and scope restoration pass every provided test, and the shadowing program prints 51 then 2
    - weight: 30
      description: "Scope Trace Exercise (Goal 3)"
      preemerging: The trace is missing or contradicts the submitted implementation
      beginning: The trace predicts final output only, with no per-step environment states
      progressing: The trace shows environment states per step with one prediction error against the actual run
      proficient: The trace shows the environment chain at every step, every prediction matches the actual run, and the lexical-vs-dynamic question is answered by pointing to the exact line of the class that decides it
  readings:
    - rtitle: "Binding and Scope Activity"
      rlink: "https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374/gh-pages/_pages/Activities/liascript-bindingscope.md"
    - rtitle: "Environments Activity"
      rlink: "https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374/gh-pages/_pages/Activities/liascript-environments.md"

tags:
  - interpreter
  - scope
  - languages
  - lab

---

This **lab** builds the single most consequential class in your interpreter: `Environment`, the data structure that makes scope *real*. The Interpreter assignment's Step 2c imports what you build here unchanged; by the time you wire it into the evaluator, its behavior should already be settled and tested. Budget **two to three hours** with a partner.

**Pair policy:** this lab may be completed **in pairs**. Both partners submit the same files, each naming the other, and both earn the same grade. (You may also work alone.) The Interpreter assignment remains individual work: you may both carry this shared `Environment` into it, but the evaluator around it must be your own.

---

## Part 1: The Environment Class (70 points)

Implement `Environment` in `environment.py`, standing alone (no AST or evaluator needed; its interface is plain Python):

- `Environment(parent=None)`: a scope with an optional enclosing scope.
- `define(name, value)`: create `name` in *this* scope, shadowing any outer binding of the same name.
- `assign(name, value)`: update the *nearest enclosing* binding of `name`; if no scope in the chain defines it, raise a language-level `LangNameError` (not a bare Python `KeyError`) carrying the name.
- `lookup(name)`: return the nearest enclosing binding's value, or raise `LangNameError`.

Verify against the provided behavior script `test_environment.py` (in the course starter repo), which exercises: lookup through three levels of nesting; define-shadows-outer; assign-updates-outer-through-inner; assign-to-undefined raises; and **scope restoration**: after a child scope is discarded, the outer binding is unchanged. The signature behavior to get right is the Interpreter assignment's shadowing program: an inner `let x` shadows (prints `51`), and after the block exits the outer `x` is intact (prints `2`).

## Part 2: Scope Trace Exercise (30 points)

On paper (in `trace.md`), predict (*before running*) the environment chain at each numbered step of the short program provided with the test script (three nested blocks mixing `define` and `assign`). Show each scope as a box with its bindings and a parent arrow. Then run it and reconcile: for any step where the prediction missed, explain which rule you misapplied. Close with two theory questions from the Binding and Scope session: (1) which line of your class makes this language **lexically** scoped rather than dynamically scoped? (2) re-predict the trace program's final output under **dynamic** scoping (where the lookup chain follows the *callers* rather than the *enclosing text*) and name the step where the two disciplines first diverge.

---

## Deliverables

Submit a ZIP containing `environment.py`, the passing `test_environment.py` output (log or screenshot), and `trace.md` with both partners named.

## Grading Breakdown

| Component | Points |
|-----------|--------|
| Part 1: The Environment Class | 70 |
| Part 2: Scope Trace Exercise | 30 |
| **Total** | **100** |

## Reflection Prompts

- What is the observable difference, in one example program, between a language where assignment creates bindings and one where it only updates them?
- If you worked in a pair, who did what, and name one thing your partner caught that you would have missed. If you worked alone, note that instead.
- AI disclosure: list any generative-AI tools you used, for what, and how you verified the results (or state 'none').
- Approximately how many hours it took you to finish this lab (I will not judge you for this at all; I am simply using it to gauge if the labs are too easy or hard)?
