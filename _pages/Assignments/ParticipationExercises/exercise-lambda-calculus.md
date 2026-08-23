---
layout: assignment
permalink: /Assignments/ParticipationExercises/LambdaCalculus
title: "CS374: Participation Exercises - Lambda Calculus"

info:
  coursenum: CS374
  purpose: "To reduce terms until they stop, and to meet one that does not."
  submission: "Nothing to upload.  Please bring your attempt, and the one step that stopped you, to the Lambda Calculus I: Syntax and Beta Reduction session.  These belong to the 15% Class Activities and Participation component, and I am not grading them for correctness."

tags:
  - resource
  - exercises

---

Beta reduction is a rewriting rule, and you learn it by applying it slowly with every step written down.  Two reductions will do here, one that reaches a normal form and one that never will.  The second one is why the lambda calculus is worth a unit of this course.

## The Exercises

- Beta-reduce `(λx. λy. x) a b` to normal form, showing each step.  Then try `(λx. x x)(λx. x x)` and explain what happens.
- Using the Church encodings from the reading, verify by reduction that `SUCC ZERO` behaves like `ONE`.

## What to Bring

Bring the reduction step you were least confident was legal.  Those are the ones we work through together at the board.

## See also

- [Participation Exercises]({{ site.baseurl }}/Assignments/ParticipationExercises): the full bank, and the other units.
- [Preparing for Each Class]({{ site.baseurl }}/Participation/PreparingForClass): the routine these exercises fit into, and the participation rubric.
- [Lambda Calculus I: Syntax and Beta Reduction]({{ site.lia_viewer_url }}{{ site.raw_pages_url }}Activities/liascript-lambdacalculus1.md): the activity deck for the session these exercises prepare you for.
