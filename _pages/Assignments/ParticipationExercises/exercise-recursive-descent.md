---
layout: assignment
permalink: /Assignments/ParticipationExercises/RecursiveDescent
title: "CS374: Participation Exercises - Recursive Descent Parsing"

info:
  coursenum: CS374
  purpose: "To trace a parser by hand so that the grammar-to-code translation stops being mechanical and starts being obvious."
  submission: "Nothing to upload.  Please bring your attempt, and the one step that stopped you, to the Recursive Descent Parsing: From Grammar to Code session.  I count these within the 15% Class Activities and Participation component, and a wrong answer you worked for is worth full credit."

tags:
  - resource
  - exercises

---

Recursive descent is where a grammar turns into a program you could have written yourself.  Trace one function on three tokens and you will see exactly where lookahead lives.  Then look at left recursion, which is the one grammar shape this technique cannot survive.

## The Exercises

- For a small expression grammar, write the pseudocode of the recursive-descent function for one non-terminal, and trace it by hand on a three-token input, marking where it looks ahead.
- Identify a grammar rule that would make naive recursive descent loop forever (left recursion) and rewrite it so it does not.

## What to Bring

Bring the trace, with the point marked where you needed to look ahead more than one token.  A trace that broke down partway is worth bringing; we start class from wherever people got stuck.

## See also

- [Participation Exercises]({{ site.baseurl }}/Assignments/ParticipationExercises): the full bank, and the other units.
- [Preparing for Each Class]({{ site.baseurl }}/Participation/PreparingForClass): the routine these exercises fit into, and the participation rubric.
- [Recursive Descent Parsing: From Grammar to Code]({{ site.lia_viewer_url }}{{ site.raw_pages_url }}Activities/liascript-recursivedescent.md): the activity deck for the session these exercises prepare you for.
