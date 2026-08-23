---
layout: assignment
permalink: /Assignments/ParticipationExercises/DerivationsAndAmbiguity
title: "CS374: Participation Exercises - Derivations, Parse Trees, Ambiguity, and Precedence"

info:
  coursenum: CS374
  purpose: "To see ambiguity as two drawings of the same string, and to fix it by changing the grammar rather than by adding a rule outside it."
  submission: "Nothing to upload.  Please bring your attempt, and the one step that stopped you, to the Derivations, Parse Trees, Ambiguity, and Precedence session.  These are preparation, so they count within the 15% Class Activities and Participation component and I do not grade them for correctness."

tags:
  - resource
  - exercises

---

Ambiguity stops being subtle the moment you have drawn it twice.  Draw both trees, then rewrite the grammar until only one drawing survives.  That rewrite is the whole technique, and you will learn more from doing it once by hand than from reading three descriptions of it.

## The Exercises

- Show that a given expression grammar is ambiguous by drawing two distinct parse trees for one string.  Then rewrite the grammar to encode precedence and associativity so the ambiguity is gone.
- Take `2 - 3 - 4` and draw the parse tree that makes subtraction left-associative; then the one that makes it right-associative.  Which does your favorite language use?  Confirm in the REPL.

## What to Bring

Bring the rewritten grammar, and mark the place where encoding precedence made a rule harder to read.  If the whole thing fell apart on you, bring it anyway.  Where it fell apart is what we should spend class time on.

## See also

- [Participation Exercises]({{ site.baseurl }}/Assignments/ParticipationExercises): the full bank, and the other units.
- [Preparing for Each Class]({{ site.baseurl }}/Participation/PreparingForClass): the routine these exercises fit into, and the participation rubric.
- [Derivations, Parse Trees, Ambiguity, and Precedence]({{ site.lia_viewer_url }}{{ site.raw_pages_url }}Activities/liascript-derivationsambiguity.md): the activity deck for the session these exercises prepare you for.
