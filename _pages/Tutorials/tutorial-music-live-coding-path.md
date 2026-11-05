---
layout: textbook
permalink: /Tutorials/MusicLiveCodingPath
title: "CS374: The Music and Live-Coding Path"

info:
  coursenum: CS374
  eyebrow: "Tutorial"
  numbering: false
  objectives:
    - "Say what the music direction asks of a team"
    - "Choose the text-events-only route if it fits"

tags:
  - final-project
  - music

---
# The Music and Live-Coding Path

*To show you the music and live-coding path through the course's required assignments (the built-in directions that let you meet the same outcomes on live-coding languages) so that each choice is made with full information.*

### Goals

- Understand that the music and live-coding path is a direction of the Team Language Project, and that every other assignment is taken as it stands
- Know what the direction entails
- Know that every music direction supports a text-events-only route, so no audio production or playback is ever required

### Background Reading and References

- [Parsing, Part 2: LR Tables, Conflicts, and Flex and Bison]({{ site.lia_viewer_url }}{{ site.raw_pages_url }}Activities/liascript-parsing2.md)
- [Flex and Bison from Zero to a Working Language]({{ site.baseurl }}/Tutorials/FlexAndBison)

This section is a guide, not a graded assignment.  It describes the music and live-coding path through the course: the same required assignments everyone completes, taken through the music directions built into them.  There is no separate set of deliverables and nothing to sign up for.  Each direction is a choice you make *inside* its assignment, when that assignment is handed out, one at a time.

### How the Music Path Works

Every assignment in this course exercises the same core outcomes: specifying a language formally, building a lexer/parser/evaluator pipeline, reasoning about semantics, and defending design decisions.  The Team Language Project offers a music direction.  It is an equivalent way of meeting those outcomes, with a single deliverable and a single rubric that applies to both directions equally.  Languages for live-coded music (TidalCycles, Strudel, and the mini-notation they share) are real, production languages with formal grammars, denotational semantics, and active communities, and they support every outcome the assignments assess.  The music direction puts those languages under your hands.

In the spirit of Universal Design for Learning, the music path is a deliberate choice of engagement (a problem domain that may hold your attention differently than a general-purpose toy language does) and of expression (your capstone demonstration can be a short live-coded performance instead of a REPL walkthrough, or a walkthrough of timed event output, if you prefer).  It is not the easy path and it is not remedial.  It is the same mountain, climbed on the same rubrics, by a route that happens to make rhythm.

**Accessibility note, stated up front:** the music materials are built around a semantics that maps programs to timed event structures: lists of `(value, begin, end)` events you can read, print, diff, and test as plain text.  Every music direction supports a text-events-only route.  Sound rendering is always optional, and no deliverable requires you to produce, hear, or evaluate audio.  If audio is not accessible or not appealing to you, the path is fully available through its textual semantics.

### The Path, Assignment by Assignment

The music path follows the course's own arc, with the music direction chosen in the team project:

1. **[Parsing, Part 2]({{ site.lia_viewer_url }}{{ site.raw_pages_url }}Activities/liascript-parsing2.md)** (activity): meet the bottom-up, table-driven side of parsing, which is what a generator emits and what the mini-notation starter is built on.  The flex/yacc pipeline itself lives in two places you can work through on your own.  The [Flex and Bison tutorial]({{ site.baseurl }}/Tutorials/FlexAndBison) builds one end to end, and the mini-notation starter under `files/examples/mininote/` in this repository is a subset Direction B can grow.  Relatedly, the [Lexer assignment]({{ site.baseurl }}/Assignments/Lexer)'s generator-toolchain direction and the [Interpreter]({{ site.baseurl }}/Assignments/Interpreter)'s Flex and Bison option put those tools in your hands early.  They pair well with what follows, but neither is required for it.
2. **[Team Language Project]({{ site.baseurl }}/Projects/TeamLanguage) -> the Music and Live-Coding direction** (capstone): design, specify, build, and demonstrate a small live-coding language with your team.  The closing demonstration may be a live edit-and-rerun session over printed event output; rendered sound is optional here as everywhere on the path.  The project's optional [Contribute Upstream extension](#contribute-upstream-an-open-source-contribution) adds an open-source stop: a pattern or transformation function contributed to Strudel/TidalCycles.

The other assignments are taken as they stand; they build the skills every direction draws on.

### The Mapping at a Glance

| Required assignment | Its music direction |
|---|---|
| [Team Language Project]({{ site.baseurl }}/Projects/TeamLanguage) | The Music and Live-Coding direction (text-events-only route available) |

The Parsing, Part 2 activity and the Flex and Bison tutorial are preparation rather than deliverables.  They play the same role the optional readings do elsewhere in the schedule.

### When to Decide

There is no track to join.  If the music path appeals to you, the useful early moves are to work through the two activities above, and to raise the Music and Live-Coding direction with your team when the Team Language Project kicks off.  That one is a team decision, and it benefits from being made at the project's first sprint rather than mid-stream.  Questions about any direction are always welcome in office hours.  The choosing itself needs no permission: the directions are built in.
