---
layout: assignment
permalink: /Assignments/Interpreter
title: "CS374: Principles of Programming Languages - The Interpreter"

info:
  coursenum: CS374
  points: 100
  goals:
    - To implement a tree-walking evaluator over your AST with strong dynamic typing
    - To implement nested scopes with an Environment class distinguishing definition from assignment
    - To implement control flow including short-circuit logic, with documented truthiness
    - To deliver a REPL and file-runner, and to document your language's semantics
  rubric:
    - weight: 60
      description: Algorithm and Implementation
      preemerging: The interpreter fails to run or fails most provided programs due to major issues
      beginning: The interpreter runs but fails on several provided test programs due to one or more minor issues
      progressing: The interpreter passes the provided test programs but would fail in a general case due to a minor issue such as a scope leak or an unchecked operand type
      proficient: A correct interpreter passes the provided and hidden test programs, with nested scopes behaving per the documented semantics, type errors raised on undefined mixtures, short-circuit logic verified by a non-evaluation test, and would be reasonably expected to handle the general case
    - weight: 15
      description: Environment and Scope Implementation
      preemerging: A flat global dictionary is used for all variables
      beginning: An Environment class exists but lookup, define, or assign is incorrect
      progressing: The Environment chain works with blocks creating scopes, with a minor defect such as assignment creating rather than updating bindings
      proficient: The Environment chain correctly implements define, lookup, and assign with shadowing, block scopes are created and discarded properly, and name errors report the missing variable
    - weight: 15
      description: REPL, Errors, and Semantics Documentation
      preemerging: No REPL exists and semantics are undocumented
      beginning: A REPL exists but dies on errors, or SEMANTICS.md is missing or generic
      progressing: The REPL survives all error classes and SEMANTICS.md documents most decisions
      proficient: The REPL and file-runner both work, every error class is caught with a stage-identifying message, and SEMANTICS.md exhaustively documents truthiness, division by zero, scoping rules, loop variable persistence, and type strictness with examples
    - weight: 10
      description: Writeup and Submission
      preemerging: An incomplete submission is provided
      beginning: The program is submitted, but not according to the directions in one or more ways
      progressing: The program is submitted according to the directions with a minor omission, with at least superficial responses to the reflection prompts
      proficient: The program is submitted according to the directions, including a readme writeup and thoughtful answers to the reflection prompts
  readings:
    - rtitle: "Tree-Walking Interpretation Activity"
      rlink: "https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374/gh-pages/_pages/Activities/liascript-interpretation.md"
    - rtitle: "Environments Activity"
      rlink: "https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374/gh-pages/_pages/Activities/liascript-environments.md"
    - rtitle: "Control Flow Semantics Activity"
      rlink: "https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374/gh-pages/_pages/Activities/liascript-controlflowsemantics.md"

tags:
  - interpreter
  - languages
  - pipeline

---

This assignment completes your pipeline: a tree-walking evaluator that runs programs in your language, with real scopes, real types, and a REPL. This is the component your team project extends, so the semantics documentation is as much a deliverable as the code. Build in the scaffolded order below.

## Part 1: Expressions (test after each step)

1a. Evaluate `Num`, `Str` (if present), `Var` (via the Environment), `UnaryOp`, and `BinOp` for arithmetic with strong dynamic typing per the types module: undefined mixtures raise a `TypeError` naming both operand types; division by zero raises with a clear message.

1b. Comparisons returning booleans, with cross-type comparison raising.

1c. Short-circuit `and`/`or` as their own evaluation rule, plus unary `not`. Include the Bomb test from class, expressed in your language: a right operand that would divide by zero but is never evaluated.

## Part 2: Environments and Statements

2a. Implement the `Environment` class (`define`, `lookup`, `assign`, parent chains) with the semantics from class: `let` defines in the current scope; bare assignment updates the existing binding wherever it lives, and errors if none exists.

2b. Execute `Let`, `Assign`, `Print`, and `Block` (each block a fresh child environment), and verify the class shadowing program produces 51 then 2.

2c. Execute `If` (with truthiness per your documented policy) and `While`. Document and implement your decision on whether loop bodies create per-iteration scopes.

2d. Implement `break` and `continue` via signal exception classes raised by the statements and caught by the loop, with the class exception-logging pattern applied to any unexpected exception.

## Part 3: The Shell

3a. The file-runner: `python mylang.py program.ml` tokenizes, parses, and executes, with every error class (lexical, syntax, name, type, zero-division) caught and reported with a message identifying the stage and position.

3b. The REPL: a prompt that reads a line (or a statement spanning lines, your choice, documented), executes against a persistent environment, prints expression values, and survives every error class. Submit a transcript demonstrating each error class and recovery.

## Part 4: Semantics Documentation

Write `SEMANTICS.md` covering, exhaustively and with a code example each: truthiness; division by zero; scoping rules and shadowing; loop-variable persistence; assignment-versus-definition; type strictness including your string `+` policy. Run the provided differential programs (whose outputs depend on these decisions) and confirm your implementation matches your document.

## Deliverables

Submit a ZIP containing your interpreter (importing your Lexer and Parser; note any fixes in the readme), `SEMANTICS.md`, the test suite and REPL transcript, and a readme writeup of approximately one page. Ensure reproducibility by listing software version information.

## Reflection Prompts

- Which semantics decision did you change after testing revealed a consequence you had not foreseen?
- Point to the exact line that makes your language statically scoped.
- If collaboration with a buddy was permitted, did you work with a buddy on this assignment? If so, who? If not, do you certify that this submission represents your own original work? Please identify any and all portions of your submission that were not originally written by you.
- Approximately how many hours it took you to finish this assignment (I will not judge you for this at all...I am simply using it to gauge if the assignments are too easy or hard)?
