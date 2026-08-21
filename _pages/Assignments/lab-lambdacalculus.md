---
layout: assignment
permalink: /Assignments/LambdaCalculusLab
title: "CS374: Principles of Programming Languages - Lab: Lambda Calculus"

info:
  coursenum: CS374
  purpose: "To evaluate lambda calculus expressions by hand with a partner: beta reduction with capture-avoiding substitution, and Church encodings of booleans and numerals, the theory floor beneath functional programming."
  tilt:
    task: "With a partner, carry out step-by-step beta reductions including a capture-avoidance case, and verify Church-encoded booleans and numerals by reduction."
    criteria: "Assessed on correct, fully-shown reduction sequences and correct Church-encoding verifications, weighted 55/45 across the two parts; see the rubric below for the full breakdown."
  points: 100
  goals:
    - To perform beta reduction step by step, identifying redexes and applying capture-avoiding substitution
    - To verify Church encodings of booleans and numerals by reduction
    - To connect lambda calculus to the closures and higher-order functions of the surrounding course
  rubric:
    - weight: 55
      description: "Beta Reduction (Goal 1)"
      preemerging: Reductions are missing or skip directly to claimed answers with no steps
      beginning: Simple reductions are correct but the capture-avoidance case substitutes blindly, capturing the free variable
      progressing: All reductions are correct including the alpha-renaming, but redexes are not marked or one sequence skips steps
      proficient: Every reduction is shown one beta-step at a time with the redex underlined or bracketed at each step, the capture case is handled by explicit alpha-renaming with a sentence explaining why, and the normal-order vs. applicative-order question is answered with the divergence example
    - weight: 45
      description: "Church Encodings (Goals 2, 3)"
      preemerging: Encodings are stated but never verified by reduction
      beginning: The boolean verifications are shown but the numeral ones are missing or incorrect
      progressing: All verifications are shown with one reduction error, or the connection question is unanswered
      proficient: TRUE/FALSE/AND and successor-of-one are all verified by complete reduction sequences, and the closing question connects Church encoding to a concrete higher-order-function idiom from the Functional Programming sessions
  readings:
    - rtitle: "Lambda Calculus I Activity"
      rlink: "https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374/gh-pages/_pages/Activities/liascript-lambdacalculus1.md"
    - rtitle: "Lambda Calculus II Activity"
      rlink: "https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374/gh-pages/_pages/Activities/liascript-lambdacalculus2.md"
    - rtitle: "Supplemental Tutorial: Build a Lambda Calculus Reducer"
      rlink: "https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374/gh-pages/_pages/Tutorials/tutorial-lambda-calculus-reducer.md"

tags:
  - lambda-calculus
  - functional
  - theory
  - lab

---

This **lab** is entirely on paper: you and a partner evaluate lambda calculus expressions by hand, the way the Lambda Calculus class sessions do on the board. It stands alone (nothing imports it) but it is deliberate preparation for two things: the Functional Programming assignment's **Direction C** (Church encodings in code; the reductions you write here are the test cases your reducer must reproduce) and the closures material, where "a function that captures a variable" stops being mysterious once you have alpha-renamed by hand. Budget **two to three hours**.

**Pair policy:** this lab may be completed **in pairs**: reduce independently, then reconcile line by line; disagreements are where the learning is. Both partners submit the same document, each naming the other, and both earn the same grade. (You may also work alone.)

---

## Part 1: Beta Reduction (55 points)

In `reductions.md`, reduce each expression to normal form, **one beta-step per line, marking the redex** you contract at each step:

1. `(λx. x) y`
2. `(λx. λy. x) a b`
3. `(λf. λx. f (f x)) (λz. z + 1) 0`: treat `+` and numerals as constants.
4. **The capture case:** `(λx. λy. x) y`: blind substitution captures the free `y`; alpha-rename first and add one sentence explaining what would have gone wrong without it.
5. `(λx. x x) (λx. x x)`: reduce three steps, then state what this term tells you about termination. Then answer: given `(λx. z) ((λx. x x) (λx. x x))`, which evaluation order (normal or applicative) terminates, and what does that imply about lazy evaluation?

## Part 2: Church Encodings (45 points)

Using `TRUE = λt. λf. t`, `FALSE = λt. λf. f`, `AND = λp. λq. p q p`, and numerals `ZERO = λf. λx. x`, `ONE = λf. λx. f x`, `SUCC = λn. λf. λx. f (n f x)`:

1. Verify `AND TRUE FALSE` reduces to `FALSE`, showing every step.
2. Verify `AND TRUE TRUE` reduces to `TRUE`.
3. Verify `SUCC ONE` reduces to a term alpha-equivalent to `TWO = λf. λx. f (f x)`.
4. Close with a short answer: a Church numeral *is* a higher-order function, "apply `f`, `n` times." Name the Python or Scheme idiom from the Functional Programming sessions that does exactly this, and one place your team language or interpreter could use the same trick.

---

## Deliverables

Submit `reductions.md` (or a scanned/photographed handwritten equivalent, legible) containing both parts, with both partners named at the top.

## Grading Breakdown

| Component | Points |
|-----------|--------|
| Part 1: Beta Reduction | 55 |
| Part 2: Church Encodings | 45 |
| **Total** | **100** |

## Reflection Prompts

- Which reduction did you and your partner disagree on, and what settled it?
- If you worked in a pair, who did what. If you worked alone, note that instead.
- AI disclosure: list any generative-AI tools you used, for what, and how you verified the results (or state 'none').
- Approximately how many hours it took you to finish this lab (I will not judge you for this at all; I am simply using it to gauge if the labs are too easy or hard)?
