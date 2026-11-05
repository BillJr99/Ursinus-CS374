---
layout: assignment
permalink: /Assignments/LambdaCalculusLab
title: "CS374: Principles of Programming Languages - Lab: Lambda Calculus"

info:
  coursenum: CS374
  purpose: "To see that functions alone can compute, individually or with a partner, by working out how Church booleans make decisions and how Church numerals count, which is the theory floor beneath functional programming."
  tilt:
    task: "Individually or with a partner, fill in tables for AND and OR, build XOR from its truth table, answer questions on the SUCC ONE and ADD walkthroughs, and write the formula for multiplication in steps."
    criteria: "I assess your work on correct tables, a correct XOR, answers that point to the reductions, and a multiplication formula you can explain.  Please read the rubric below for the details."
  points: 15
  goals:
    - To show how Church booleans implement AND, OR, and XOR by selecting between their arguments
    - To follow reductions of SUCC and ADD on Church numerals and explain why they count correctly
    - To derive multiplication on Church numerals from the idea of repeated application
  rubric:
    - weight: 25
      description: "AND and OR (Goal 1)"
      preemerging: The tables are missing
      beginning: One table is filled in, or several rows name the wrong result
      progressing: Both tables are filled in with at most one wrong row, or the picks column is left out
      proficient: Every row of both tables shows the term, which argument it picks, and the correct result
    - weight: 25
      description: "XOR (Goal 1)"
      preemerging: No formula is written
      beginning: A formula is written, but it fails more than one row of the truth table
      progressing: The formula is correct, but the table is not filled in, or one row is wrong
      proficient: The formula is correct, and all four rows are checked against the given truth table
    - weight: 25
      description: "SUCC and ADD (Goal 2)"
      preemerging: The questions are unanswered
      beginning: The questions are answered without reference to the reductions
      progressing: Most answers are correct and point to a line of the walkthrough, with one error
      proficient: Every answer is correct and points to a line of the walkthrough, and SUCC ZERO and ADD TWO ONE are worked out to their numerals
    - weight: 25
      description: "Multiplication (Goal 3)"
      preemerging: The steps are blank
      beginning: Some steps are filled in, but the formula does not multiply
      progressing: The formula is correct, but the check on MULT TWO TWO is missing or wrong
      proficient: Each step is filled in, the formula is correct, and the check on MULT TWO TWO counts four applications of f
  readings:
    - rtitle: "Lambda Calculus I Activity"
      rlink: "Activities/liascript-lambdacalculus1.md"
      liapage: true
    - rtitle: "Lambda Calculus II Activity"
      rlink: "Activities/liascript-lambdacalculus2.md"
      liapage: true

tags:
  - lambda-calculus
  - functional
  - theory
  - lab

---

The lambda calculus has no booleans and no numbers, only functions.  In this short lab you see how functions alone can make a decision and count.  It is paper work: you fill in one file and hand it in.

Download [reductions.md]({{ site.baseurl }}/files/starters/lambda/reductions.md) and fill it in, or copy its blanks onto paper and hand in a photo.  You may work alone or with a partner.  A pair hands in one file with both names and earns the same grade.

## Part 1: AND and OR

[Church Booleans](https://liascript.github.io/course/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374-Fall2026/gh-pages/_pages/Activities/liascript-lambdacalculus2.md#10) covers this in the activity.  A Church boolean is a function that picks one of two arguments:

```text
TRUE  = λa.λb. a      picks the first argument
FALSE = λa.λb. b      picks the second argument
```

So a boolean does not store a decision.  It *is* the decision.  That means `AND` and `OR` only have to hand a boolean the right two things to choose between:

```text
AND = λp.λq. p q p
OR  = λp.λq. p p q
```

Read `AND` this way: if `p` is true, the answer depends on `q`, so `p` picks `q`.  If `p` is false, the answer is false, and `p` itself is false, so `p` picks `p`.  Here is one row, worked:

```text
AND TRUE FALSE  =  TRUE FALSE TRUE     substitute p = TRUE, q = FALSE
                =  FALSE               TRUE picks its first argument
```

**Do this.**  Fill in the AND and OR tables in `reductions.md`.  Each row shows the term after substitution, which argument the first boolean picks, and the result.

## Part 2: XOR

XOR is true when exactly one of its inputs is true:

| p | q | XOR p q |
|---|---|---|
| TRUE | TRUE | FALSE |
| TRUE | FALSE | TRUE |
| FALSE | TRUE | TRUE |
| FALSE | FALSE | FALSE |

Look at the table one `p` at a time.  When `p` is `TRUE`, the answer is the opposite of `q`.  When `p` is `FALSE`, the answer is `q`.  So `p` has to pick between those two, and you have one more tool for the opposite:

```text
NOT = λb. b FALSE TRUE
```

**Do this.**  Fill in `XOR = λp.λq. p ___ ___` in `reductions.md`, and check all four rows of the truth table with your formula.

## Part 3: SUCC and ADD

[Church Numerals](https://liascript.github.io/course/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374-Fall2026/gh-pages/_pages/Activities/liascript-lambdacalculus2.md#16) covers this in the activity.  A Church numeral is a function that applies `f` that many times.  The number *is* the repetition:

```text
ZERO = λf.λx. x
ONE  = λf.λx. f x
TWO  = λf.λx. f (f x)
```

To use a numeral, you give it an `f` and a starting `x`, so `n f x` means "apply `f` to `x`, `n` times."

**SUCC adds one more `f`.**

```text
SUCC = λn.λf.λx. f (n f x)

SUCC ONE
  =  λf.λx. f (ONE f x)          line 1: substitute ONE for n
  =  λf.λx. f ((λx. f x) x)      line 2: ONE takes f
  =  λf.λx. f (f x)              line 3: that function takes x
  =  TWO
```

**ADD does `n`'s applications, and then `m`'s on top of them.**  The activity calls this `PLUS`.

```text
ADD = λm.λn.λf.λx. m f (n f x)

ADD ONE ONE
  =  λf.λx. ONE f (ONE f x)      line 1: substitute both numerals
  =  λf.λx. ONE f (f x)          line 2: the inner ONE f x becomes f x
  =  λf.λx. (λx. f x) (f x)      line 3: the outer ONE takes f
  =  λf.λx. f (f x)              line 4: that function takes (f x) as its x
  =  TWO
```

**Do this.**  Answer the questions in `reductions.md`, pointing to a line of the walkthrough in each answer.

## Part 4: Multiplication

Multiplying is repeated repeating.  `m` times `n` means: do "apply `f`, `n` times" a total of `m` times.  You already have both pieces.  `n f` is a function that applies `f` a total of `n` times, and a numeral `m` repeats any function you hand it `m` times.

**Do this.**  Fill in the steps in `reductions.md`, which build the formula from the inside out, and then check it on `MULT TWO TWO`.

## Deliverables

Submit `reductions.md`, or a PDF of your paper copy, with your name (and your partner's, if you worked in a pair) at the top.

## Reflection Prompt

In one or two sentences: which of these surprised you most, that a boolean can be a function or that a number can be?  What AI tools, if any, did you use, and how?
