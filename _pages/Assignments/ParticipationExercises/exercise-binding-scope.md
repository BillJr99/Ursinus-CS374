---
layout: assignment
permalink: /Assignments/ParticipationExercises/BindingAndScope
title: "CS374: Participation Exercises - Tree-Walking Interpretation, Binding, and Scope"

info:
  coursenum: CS374
  purpose: "To draw the environment at every step, so that scope becomes something you can point at rather than something you recall."
  submission: "Nothing to upload. Bring your attempt, and the one step that stopped you, to the Tree-Walking Interpretation and Binding and Scope sessions. These are low-stakes preparation, assessed as part of the 15% Class Activities and Participation component, not graded for correctness."

tags:
  - resource
  - exercises

---

Scope arguments are unwinnable in the abstract and settle themselves the moment someone draws the environment. Evaluate the shadowing example below on paper, once under lexical scope and once under dynamic, and the two disciplines separate at a specific step you can name. This page also backs the in-class Mystery Scoping Language exercise on the Binding and Scope day.

## The Exercises

- Evaluate `let x = 2 in let x = x + 1 in x * x` by hand, drawing the environment at each step. Then predict the answer under *dynamic* rather than lexical scope and say where they diverge.
- Trace what your evaluator does with an unbound variable, and decide what error it should raise and when.

## What to Bring

Mark the one step that resisted you and bring it: the step where the lexical and dynamic traces first disagree. A genuine attempt that ran aground is worth more to the discussion than a blank page or a perfect one, and the stuck points set the agenda for the session.

## See also

- [Participation Exercises]({{ site.baseurl }}/Assignments/ParticipationExercises): the full bank, and the other units.
- [Preparing for Each Class]({{ site.baseurl }}/Participation/PreparingForClass): the routine these exercises fit into, and the participation rubric.
- [Tree-Walking Interpretation: Evaluating the AST]({{ site.lia_viewer_url }}{{ site.raw_pages_url }}Activities/liascript-interpretation.md): the activity deck for the session these exercises prepare you for.
- [Binding and Scope]({{ site.lia_viewer_url }}{{ site.raw_pages_url }}Activities/liascript-bindingscope.md): the second of the two sessions these exercises prepare you for, and the home of the Mystery Scoping Language exercise.
