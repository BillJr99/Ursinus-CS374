---
layout: assignment
permalink: /Assignments/MusicTrack
title: "CS374: Principles of Programming Languages - The Music and Live-Coding Path"

info:
  coursenum: CS374
  purpose: "To show you the music and live-coding path through the course's required assignments — the built-in directions that let you meet the same outcomes on live-coding languages — so that each choice is made with full information."
  tilt:
    task: "Read this guide, skim the linked assignments and their music directions, and keep the mapping in mind — each direction is chosen inside its own assignment when that assignment is handed out, so nothing is committed now."
    criteria: "Nothing is submitted; you have met the page's goals when you can name each assignment that offers a music direction, say what that direction asks for, and know that every one of them supports a text-events-only route."
  points: 0
  goals:
    - "Understand that the music and live-coding path runs through the same required assignments as every other path — as directions chosen within them, one assignment at a time"
    - "Know which assignments offer a music direction (Parser, Functional, and the Team Language Project) and what each direction entails"
    - "Know that every music direction supports a text-events-only route, so no audio production or playback is ever required"
  readings:
    - rtitle: "Music Languages and Live Coding Activity"
      rlink: "https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374/gh-pages/_pages/Activities/liascript-languagedesign.md"
    - rtitle: "Flex and Yacc Activity"
      rlink: "https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374/gh-pages/_pages/Activities/liascript-parsertable.md"

tags:
  - music
  - livecoding
  - dsl
  - languages
  - directions

---

This page is a guide, not a graded assignment. It describes the **music and live-coding path** through the course: the same required assignments everyone completes, taken through the music **directions** built into them. There is no separate set of deliverables and nothing to sign up for — each direction is a choice you make *inside* its assignment, when that assignment is handed out, one at a time.

---

## How the Music Path Works

Every assignment in this course exercises the same core outcomes: specifying a language formally, building a lexer/parser/evaluator pipeline, reasoning about semantics, and defending design decisions. Several assignments offer more than one **direction** — equivalent ways of meeting those outcomes, with a single deliverable and a single rubric that applies to every direction equally. Languages for live-coded music — TidalCycles, Strudel, and the mini-notation they share — are real, production languages with formal grammars, denotational semantics, and active communities, and they support every outcome the assignments assess. The music directions put those languages under your hands.

In the spirit of Universal Design for Learning, the music path is a deliberate choice of **engagement** (a problem domain that may hold your attention differently than a general-purpose toy language does) and of **expression** (your capstone demonstration can be a short live-coded performance rather than a REPL walkthrough — or a walkthrough of timed event output, if you prefer). It is not the easy path and it is not remedial: it is the same mountain, climbed on the same rubrics, by a route that happens to make rhythm.

**Accessibility note, stated up front:** the music materials are built around a semantics that maps programs to *timed event structures* — lists of `(value, begin, end)` events you can read, print, diff, and test as plain text. Every music direction supports a **text-events-only route**: sound rendering is always optional, and no deliverable requires you to produce, hear, or evaluate audio. If audio is not accessible or not appealing to you, the path is fully available through its textual semantics.

---

## The Path, Assignment by Assignment

The music path follows the course's own arc — the same required assignments, in the same order, with the music direction chosen where one is offered:

1. **[Music Languages and Live Coding](https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374/gh-pages/_pages/Activities/liascript-languagedesign.md)** (activity) — meet TidalCycles and Strudel as *language designs*: embedded versus external DSLs, a formal model of patterns, and the timed-event semantics the rest of the path builds on.
2. **[Flex and Yacc](https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374/gh-pages/_pages/Activities/liascript-parsertable.md)** (activity) — build a working flex/yacc pipeline for a subset of the mini-notation in class. (Relatedly, the [Lexer assignment](/Assignments/Lexer)'s generator-toolchain direction is a natural on-ramp: choosing Flex or PLY there puts the tools of the mini-notation pipeline in your hands early. It pairs well with what follows, but it is not required for it.)
3. **[The Parser and AST](/Assignments/Parser) → the Mini-Notation direction** — grow the in-class mini-notation subset toward the real language: alternation, Euclidean rhythms, and polymeter, parsed into an AST, evaluated to timed events, and validated against the Strudel reference implementation (or against printed event lists alone).
4. **[Functional Programming](/Assignments/Functional) → the Parallel Functional direction** — purity buys parallelism: the same core parts as everyone (pure functions, higher-order combinators, recursive structures with fold), then a complete MapReduce pipeline measured and analyzed against Amdahl's Law — the same pure-map/associative-reduce discipline pattern engines like Strudel run on.
5. **[Team Language Project](/Projects/TeamLanguage) → the Music and Live-Coding direction** (capstone) — design, specify, build, and demonstrate a small live-coding language with your team. The closing demonstration may be a live edit-and-rerun session over printed event output — rendered sound is optional here as everywhere on the path.

Assignments without a music direction listed here (Warmup, Regex, the Automata lab, Lexer, Interpreter, and the rest) are simply taken as they stand — they build the skills every direction draws on. And the choices are independent: you can take the Mini-Notation direction in the Parser assignment and any direction you like in Functional, or vice versa. The path above is the coherent musical route, not a package deal.

---

## The Mapping at a Glance

| Required assignment | Its music direction |
| --- | --- |
| [The Parser and AST](/Assignments/Parser) | Direction B: The Mini-Notation Music Parser |
| [Functional Programming](/Assignments/Functional) | Direction E: Parallel Functional Programming |
| [Team Language Project](/Projects/TeamLanguage) | The Music and Live-Coding direction (text-events-only route available) |

The two activities (Music Languages and Live Coding; Flex and Yacc) are preparation, not deliverables — they play the same role the optional readings do elsewhere in the schedule.

---

## When to Decide

There is no track to join and no deadline to declare by: **each direction is chosen when its assignment is handed out**, inside that assignment, and each choice stands alone. If the music path appeals to you, the useful early moves are simply to work through the two activities above before the Parser assignment arrives, and to raise the Music and Live-Coding direction with your team when the Team Language Project kicks off — that one is a team decision, and it benefits from being made at the project's first sprint rather than mid-stream. Questions about any direction are always welcome in office hours; the choosing, though, needs no permission — the directions are built in.
