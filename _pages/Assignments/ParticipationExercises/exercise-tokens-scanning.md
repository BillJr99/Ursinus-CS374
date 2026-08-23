---
layout: assignment
permalink: /Assignments/ParticipationExercises/TokensAndScanning
title: "CS374: Participation Exercises - Tokens and Scanning"

info:
  coursenum: CS374
  purpose: "To decide, by hand, what your scanner should do at the inputs that do not read cleanly."
  submission: "Nothing to upload. Bring your attempt, and the one step that stopped you, to the Tokens and Scanning: Building a Lexer session. These are low-stakes preparation, assessed as part of the 15% Class Activities and Participation component, not graded for correctness."

tags:
  - resource
  - exercises

---

A scanner is easy to write for input that behaves and interesting to write for input that does not. The awkward cases below are the ones your Lexer assignment will actually turn on, so it is worth having an opinion about them before we compare answers in class.

## The Exercises

- Hand-tokenize the line `x = 12 + foo(3)` into a token stream, giving each token a type and a value. Then predict what your scanner should do with `12foo` and with `= =` versus `==`.
- Write the regular expressions your lexer would use for three token classes, and identify one pair whose patterns overlap: which rule wins, and why does order matter?

## What to Bring

Mark the one step that resisted you and bring it: your answer for `12foo`, and whether you would call it one token, two, or an error. A genuine attempt that ran aground is worth more to the discussion than a blank page or a perfect one, and the stuck points set the agenda for the session.

## See also

- [Participation Exercises]({{ site.baseurl }}/Assignments/ParticipationExercises): the full bank, and the other units.
- [Preparing for Each Class]({{ site.baseurl }}/Participation/PreparingForClass): the routine these exercises fit into, and the participation rubric.
- [Tokens and Scanning: Building a Lexer]({{ site.lia_viewer_url }}{{ site.raw_pages_url }}Activities/liascript-tokensscanning.md): the activity deck for the session these exercises prepare you for.
