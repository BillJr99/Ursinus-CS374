---
layout: assignment
permalink: /Assignments/ParticipationExercises/AbstractSyntaxTrees
title: "CS374: Participation Exercises - Abstract Syntax Trees"

info:
  coursenum: CS374
  purpose: "To be deliberate about what an AST throws away, because that choice becomes your interpreter's data model."
  submission: "Nothing to upload. Bring your attempt, and the one step that stopped you, to the Abstract Syntax Trees session. These are low-stakes preparation, assessed as part of the 15% Class Activities and Participation component, not graded for correctness."

tags:
  - resource
  - exercises

---

The difference between a parse tree and an AST is a design decision, not a technicality: you are choosing what the rest of your language implementation will never have to think about again. Draw one, then design the node types you would actually build on.

## The Exercises

- Draw the AST (not the parse tree) for `3 + 4 * 5`, and say in one sentence what the AST threw away that the parse tree kept.
- Design the node types (as Python dataclasses or a `match`/`case` shape) you would use to represent `if`/`else` and function calls in your team's language.

## What to Bring

Mark the one step that resisted you and bring it: your node types, and the one field you added because you were not sure you could do without it. A genuine attempt that ran aground is worth more to the discussion than a blank page or a perfect one, and the stuck points set the agenda for the session.

## See also

- [Participation Exercises]({{ site.baseurl }}/Assignments/ParticipationExercises): the full bank, and the other units.
- [Preparing for Each Class]({{ site.baseurl }}/Participation/PreparingForClass): the routine these exercises fit into, and the participation rubric.
- [Abstract Syntax Trees]({{ site.lia_viewer_url }}{{ site.raw_pages_url }}Activities/liascript-ast.md): the activity deck for the session these exercises prepare you for.
