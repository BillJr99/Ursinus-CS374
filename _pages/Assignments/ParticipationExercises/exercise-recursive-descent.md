---
layout: assignment
permalink: /Assignments/ParticipationExercises/RecursiveDescent
title: "CS374: Participation Exercises - Recursive Descent Parsing"

info:
  coursenum: CS374
  purpose: "To trace a parser by hand so that the grammar-to-code translation stops being mechanical and starts being obvious."
  submission: "Nothing to upload. Bring your attempt, and the one step that stopped you, to the Recursive Descent Parsing: From Grammar to Code session. These are low-stakes preparation, assessed as part of the 15% Class Activities and Participation component, not graded for correctness."

tags:
  - resource
  - exercises

---

Recursive descent is the point where a grammar becomes a program you could have written yourself. Tracing one function on three tokens shows you exactly where lookahead lives, and left recursion shows you the one grammar shape the technique cannot survive.

## The Exercises

- For a small expression grammar, write the pseudocode of the recursive-descent function for one non-terminal, and trace it by hand on a three-token input, marking where it looks ahead.
- Identify a grammar rule that would make naive recursive descent loop forever (left recursion) and rewrite it so it does not.

## What to Bring

Mark the one step that resisted you and bring it: the trace, with the point marked where you needed to look ahead more than one token. A genuine attempt that ran aground is worth more to the discussion than a blank page or a perfect one, and the stuck points set the agenda for the session.

## See also

- [Participation Exercises]({{ site.baseurl }}/Assignments/ParticipationExercises): the full bank, and the other units.
- [Preparing for Each Class]({{ site.baseurl }}/Participation/PreparingForClass): the routine these exercises fit into, and the participation rubric.
- [Recursive Descent Parsing: From Grammar to Code]({{ site.lia_viewer_url }}{{ site.raw_pages_url }}Activities/liascript-recursivedescent.md): the activity deck for the session these exercises prepare you for.
