---
layout: assignment
permalink: /Assignments/ParticipationExercises/DerivationsAndAmbiguity
title: "CS374: Participation Exercises - Derivations, Parse Trees, Ambiguity, and Precedence"

info:
  coursenum: CS374
  purpose: "To see ambiguity as two drawings of the same string, and to fix it by changing the grammar rather than by adding a rule outside it."
  submission: "Nothing to upload. Bring your attempt, and the one step that stopped you, to the Derivations, Parse Trees, Ambiguity, and Precedence session. These are low-stakes preparation, assessed as part of the 15% Class Activities and Participation component, not graded for correctness."

tags:
  - resource
  - exercises

---

Ambiguity is not a subtle property once you have drawn it twice. Draw both trees, then rewrite the grammar until only one drawing survives; that rewrite is the whole technique, and doing it by hand once is worth more than reading three descriptions of it.

## The Exercises

- Show that a given expression grammar is ambiguous by drawing two distinct parse trees for one string. Then rewrite the grammar to encode precedence and associativity so the ambiguity is gone.
- Take `2 - 3 - 4` and draw the parse tree that makes subtraction left-associative; then the one that makes it right-associative. Which does your favorite language use? Confirm in the REPL.

## What to Bring

Mark the one step that resisted you and bring it: the rewritten grammar, and the place where encoding precedence made a rule harder to read. A genuine attempt that ran aground is worth more to the discussion than a blank page or a perfect one, and the stuck points set the agenda for the session.

## See also

- [Participation Exercises]({{ site.baseurl }}/Assignments/ParticipationExercises): the full bank, and the other units.
- [Preparing for Each Class]({{ site.baseurl }}/Participation/PreparingForClass): the routine these exercises fit into, and the participation rubric.
- [Derivations, Parse Trees, Ambiguity, and Precedence]({{ site.lia_viewer_url }}{{ site.raw_pages_url }}Activities/liascript-derivationsambiguity.md): the activity deck for the session these exercises prepare you for.
