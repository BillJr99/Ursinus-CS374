---
layout: assignment
permalink: /Assignments/ParticipationExercises/BindingAndScope
title: "CS374: Participation Exercises - Binding and Scope"

info:
  coursenum: CS374
  purpose: "To draw the environment at every step, so that scope becomes something you can point at rather than something you recall."
  submission: "Nothing to upload.  Please bring your attempt, and the one step that stopped you, to the Tree-Walking Interpretation and Binding and Scope sessions.  These count toward the 15% Class Activities and Participation component.  I am looking for the attempt, not for correct answers."

tags:
  - resource
  - exercises

---

You cannot win a scope argument in the abstract, and you can settle one in about thirty seconds by drawing the environment.  Please evaluate the shadowing example below on paper twice, once under lexical scope and once under dynamic, and you will find the exact step where the two disciplines part company.  This one exercise comes in two parts, handed out on the two days it prepares you for.

## The Exercises

### Part 1, handed out on the Tree-Walking Interpretation day

- Evaluate `let x = 2 in let x = x + 1 in x * x` by hand, drawing the environment at each step.  Then predict the answer under *dynamic* rather than lexical scope and say where they diverge.
- Trace what your evaluator does with an unbound variable, and decide what error it should raise and when.

### Part 2, handed out on the Binding and Scope day

- **Mystery Scoping Language.**  Write down, before class, two short programs whose output would *differ* depending on whether a language is lexically or dynamically scoped.  One of them should be as short as you can make it.  In class you will run these against an interpreter whose scoping rule is hidden and deduce the rule from the answers, so the value of a probe is entirely in whether it can tell the two apart.  Bring both, and bring your prediction of what each would print under each rule.

## What to Bring

Bring the trace, and mark the step where the lexical and dynamic versions first disagree.  A half-finished trace is worth more to me than a blank page; I build the session around the places people got stuck.

## See also

- [Participation Exercises]({{ site.baseurl }}/Assignments/ParticipationExercises): the full bank, and the other units.
- [Preparing for Each Class]({{ site.baseurl }}/Participation/PreparingForClass): the routine these exercises fit into, and the participation rubric.
- [Tree-Walking Interpretation: Evaluating the AST]({{ site.lia_viewer_url }}{{ site.raw_pages_url }}Activities/liascript-interpretation.md): the activity deck for the session these exercises prepare you for.
- [Binding and Scope]({{ site.lia_viewer_url }}{{ site.raw_pages_url }}Activities/liascript-bindingscope.md): the second of the two sessions these exercises prepare you for, and the home of the Mystery Scoping Language exercise.
