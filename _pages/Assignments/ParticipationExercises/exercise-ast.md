---
layout: assignment
permalink: /Assignments/ParticipationExercises/AbstractSyntaxTrees
title: "CS374: Participation Exercises - Abstract Syntax Trees"

info:
  coursenum: CS374
  purpose: "To be deliberate about what an AST throws away, because that choice becomes your interpreter's data model."
  submission: "Nothing to upload.  Please bring your attempt, and the one step that stopped you, to the Abstract Syntax Trees session.  I assess these as part of the 15% Class Activities and Participation component, and I do not grade them for correctness."

tags:
  - resource
  - exercises

---

The difference between a parse tree and an AST is a design decision.  You are choosing what the rest of your language implementation never has to think about again.  Draw one, then design the node types you would actually build on.

## The Exercises

- Draw the AST (not the parse tree) for `3 + 4 * 5`, and say in one sentence what the AST threw away that the parse tree kept.
- Design the node types (as Python dataclasses or a `match`/`case` shape) you would use to represent `if`/`else` and function calls in your team's language.

## What to Bring

Bring your node types, and the one field you added because you were not sure you could do without it.  Mark whatever gave you the most trouble, because that is where we will start.

## See also

- [Participation Exercises]({{ site.baseurl }}/Assignments/ParticipationExercises): the full bank, and the other units.
- [Preparing for Each Class]({{ site.baseurl }}/Participation/PreparingForClass): the routine these exercises fit into, and the participation rubric.
- [Abstract Syntax Trees]({{ site.lia_viewer_url }}{{ site.raw_pages_url }}Activities/liascript-ast.md): the activity deck for the session these exercises prepare you for.
