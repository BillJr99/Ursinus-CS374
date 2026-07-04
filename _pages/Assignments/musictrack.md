---
layout: assignment
permalink: /Assignments/MusicTrack
title: "CS374: Principles of Programming Languages - Choose Your Track: Music & Live-Coding Language Track"

info:
  coursenum: CS374
  points: 0
  goals:
    - "Understand what the music and live-coding track is, which deliverables it comprises, and how they parallel the classic track"
    - "Weigh the two tracks against your own interests and choose deliberately, with your instructor, by the week 11 team project handout"
    - "Know that every music-track deliverable supports a text-events-only path, so no audio production or playback is ever required"
  readings:
    - rtitle: "Music Languages and Live Coding Activity"
      rlink: "https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374-Fall2026/gh-pages/_pages/Activities/liascript-musiclanguages.md"
    - rtitle: "Flex and Yacc Activity"
      rlink: "https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374-Fall2026/gh-pages/_pages/Activities/liascript-flexyacc.md"

tags:
  - music
  - livecoding
  - dsl
  - languages
  - tracks

---

This page is a guide, not a graded assignment. It describes an alternative path through the second half of the course — the music and live-coding language track — so that you can choose your route with full information rather than discovering it piecemeal.

---

## Why an Alternative Track Exists

Every deliverable in this course exercises the same core outcomes: specifying a language formally, building a lexer/parser/evaluator pipeline, reasoning about semantics, and defending design decisions. But those outcomes do not require every student to exercise them on the same artifact. Languages for live-coded music — TidalCycles, Strudel, and the mini-notation they share — are real, production languages with formal grammars, denotational semantics, and active communities, and they support every outcome the classic track does.

In the spirit of Universal Design for Learning, this track is a deliberate choice of **engagement** (a problem domain that may hold your attention differently than a general-purpose toy language does) and of **expression** (your capstone demonstration can be a short live-coded performance rather than a REPL walkthrough — or a REPL walkthrough of timed event output, if you prefer). Neither track is the "easy" one, and neither is remedial: they are two routes over the same mountain, graded against the same kinds of rubrics.

**Accessibility note, stated up front:** the music materials are built around a semantics that maps programs to *timed event structures* — lists of `(value, begin, end)` events you can read, print, diff, and test as plain text. Every activity, assignment, and the capstone project on this track supports a **text-events-only path**: sound rendering is always optional, and no deliverable requires you to produce, hear, or evaluate audio. If audio is not accessible or not appealing to you, the track is fully available through its textual semantics.

---

## The TILT View

**Purpose.** To let you meet the course outcomes of the second half — parsing with generator tools, semantics, the lambda calculus, functional programming, and language design — through a coherent sequence built around music and live-coding languages, and to make the substitution rules explicit so the choice is transparent.

**Task.** Read the track arc below, skim the linked deliverables, and decide — with your instructor — whether to take the classic track, the music track, or a mix. Declare your choice no later than the week 11 team project handout.

**Criteria.** There is nothing to submit for this page. You have met its goals when you can (1) name the music-track deliverables and their classic counterparts, (2) state which substitutions you intend to propose, and (3) confirm that plan with your instructor before the decision point. Use this as a self-checklist rather than a rubric.

---

## The Track Arc

The music track follows the same shape as the classic track: two preparatory activities, a parser assignment with generator tools, a theory unit on the calculus beneath it all, a functional programming assignment that cashes theory into performance, and a capstone language project.

1. **[Music Languages and Live Coding](https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374-Fall2026/gh-pages/_pages/Activities/liascript-musiclanguages.md)** (activity) — meet TidalCycles and Strudel as *language designs*: embedded versus external DSLs, a formal model of patterns, and the timed-event semantics the rest of the track builds on.
2. **[Flex and Yacc](https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374-Fall2026/gh-pages/_pages/Activities/liascript-flexyacc.md)** (activity) — build a working flex/yacc pipeline for a subset of the mini-notation in class.
3. **[Programming Assignment: A Mini-Notation Parser with Flex and Yacc](/Assignments/MiniNotationParser)** — grow the in-class subset toward the real language: alternation, Euclidean rhythms, and polymeter, validated against the Strudel reference implementation (or against printed event lists alone).
4. **[Written Assignment: The Lambda Calculus By Hand and In Code](/Assignments/LambdaCalculus)** — paper derivations and a capture-avoiding interpreter, each auditing the other; connects the calculus to the host languages of Tidal and Strudel.
5. **[Assignment: A Flock of Functions — Combinatory Logic in Code](/Assignments/FlockOfBirds)** — the calculus stripped to combinators: hand reductions, a term reducer, and bracket abstraction.
6. **[Assignment: Massively Parallel Data Processing with Pure Functions](/Assignments/ParallelFunctional)** — purity buys parallelism: a complete MapReduce pipeline, measured and analyzed against Amdahl's Law.
7. **[Project: Design and Implement Your Own Live Coding Language](/Projects/LiveCodingLanguage)** (capstone) — design, specify, build, and perform with a small live-coding language of your own; the alternative to the [Team Language Project](/Projects/TeamLanguage). The closing "performance" may be a live edit-and-rerun session over printed event output — rendered sound is optional here as everywhere on the track.

---

## Proposed Equivalence Table

The table below maps each music-track deliverable to the classic-track deliverable it is designed to parallel. It is **Proposed — confirm with your instructor before substituting.** Substitutions are individually negotiated because the classic Lexer → Parser → Interpreter sequence builds one permanent pipeline, and swapping a component mid-stream has downstream consequences your instructor will help you plan for.

| Music-track deliverable | Classic-track deliverable it can substitute for |
| --- | --- |
| [A Mini-Notation Parser with Flex and Yacc](/Assignments/MiniNotationParser) | [The Parser and AST](/Assignments/Parser) |
| [The Lambda Calculus By Hand and In Code](/Assignments/LambdaCalculus) | [Continuations and call/cc](/Assignments/Continuations) — choose this row *or* the next, not both |
| [A Flock of Functions](/Assignments/FlockOfBirds) | [Continuations and call/cc](/Assignments/Continuations) — the row not chosen above counts as enrichment |
| [Massively Parallel Data Processing with Pure Functions](/Assignments/ParallelFunctional) | [Functional Programming](/Assignments/Functional) |
| [Design and Implement Your Own Live Coding Language](/Projects/LiveCodingLanguage) | [Team Language Project](/Projects/TeamLanguage) |

The two activities (Music Languages and Live Coding; Flex and Yacc) are preparation, not substitutions — they play the same role the optional readings do on the classic schedule.

---

## Decision Point

Choose your track **by the week 11 team project handout**. That is the moment the classic track commits to the Team Language Project, and it is the latest point at which the live-coding capstone can be scoped in its place without compressing the sprint schedule. You are welcome to decide earlier — the mini-notation parser substitution, for example, is best negotiated before the classic Parser assignment is handed out — and you are welcome to mix tracks, taking individual music-track deliverables as enrichment without switching your capstone. Whatever you choose, confirm it with your instructor: the equivalences above are proposals, and the conversation is part of the point.
