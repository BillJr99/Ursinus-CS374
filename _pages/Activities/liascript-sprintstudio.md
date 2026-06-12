# Sprint Studio and Gallery Walk
<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://github.com/BillJr99/Ursinus-CS374-Fall2026/blob/gh-pages/_pages/Activities/liascript-sprintstudio.md or locally via https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374/gh-pages/_pages/Activities/liascript-sprintstudio.md

import: https://raw.githubusercontent.com/liascript/CodeRunner/master/README.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

# Sprint Studio and Gallery Walk

Studio days are structured work time for the team language project: a stand-up, focused build time, and, on designated days, the formal **gallery walk** peer review that feeds your final sprint. This page is the protocol for every studio day; the gallery walk sections apply on the scheduled walk day. The arc: **stand-up $\rightarrow$ build $\rightarrow$ gallery walk $\rightarrow$ triage $\rightarrow$ release checklist**.

---

## Directions and Group Roles

Project roles (rotated by sprint) are in effect: **Coordinator**, **Builder(s)**, **Evaluator**, **Scribe**. The Scribe maintains today's living document: stand-up notes, all feedback received verbatim, and the triaged backlog the team leaves with.

---

## 1. Stand-Up (10 minutes)

Each team answers, in two minutes at the board, exactly four questions: What runs end-to-end today (which sample programs pass)? What is the riskiest unfinished piece of the sprint? What does the test suite report this week (a number of passing tests, not an adjective)? What do you need from the instructor or another team? The discipline is *saying the number*; "mostly working" is not a status.

---

## 2. Build Time

Builders build the sprint increment; the Evaluator extends the test suite *ahead of* the features (a failing test is a specification); the Scribe keeps `SEMANTICS.md` and the decision log current as choices happen, not after; the Coordinator defends scope against good ideas that belong in the future-work list. Mid-studio checkpoint: the Coordinator confirms the sprint goal is still achievable or re-scopes it *now*, aloud.

---

## 3. Gallery Walk Protocol (40 minutes, designated days)

Stations: each team's language runs live (REPL up, sample programs ready) beside two artifacts: the grammar one-pager and the current test results table. Half of each team hosts; half walks; swap at the midpoint.

Walkers leave one structured card per station, with exactly three fields:

- **Strength**: one specific thing that works, precisely named ("the error message for an unclosed brace points at the opening brace's line").
- **Question**: one genuine question the demo raised, ideally about a seam or a semantics decision ("what does your `for` desugar to, and does the loop variable survive?").
- **Risk**: the one thing most likely to fail on Demo Day, stated kindly and concretely.

Hosts demonstrate honestly: at least one **known failure case** must be shown at every station (a program that breaks the parser, a semantics corner still undecided). A demo that hides its failures is rehearsing a deception; your `SEMANTICS.md` deserves better.

### Critical Thinking Questions

1. As a walker: across stations, which *design decision* (scoping, truthiness, the distinctive feature) varied most between languages, and which team's resolution would you steal?
2. As a host: which visitor question exposed a semantics corner your team had not decided? The Scribe records it verbatim; it likely belongs in `SEMANTICS.md` by Friday.
3. Which team's error messages would you most want at 2 AM, and what specifically makes them good? (Recall the parser module's standard.)

---

## 4. Triage (20 minutes, after the walk)

Cluster the cards and sort every item into exactly one bucket: **Fix before Demo Day** (breaks the core story), **Disclose at Demo Day** (real, acknowledged, out of scope), or **Future work** (report material). The discipline is the middle bucket: mature engineering names its known defects. The Scribe converts bucket one into assigned, dated backlog items before anyone leaves.

---

## 5. Demo Day Release Checklist

Before Demo Day, the Evaluator verifies and signs each line:

1. The REPL and the file-runner both work from a fresh clone following the readme, in under three minutes.
2. All sample programs (five minimum, including one that shows off the niche) run with committed expected outputs.
3. The test suite passes and its results table is current in the repository.
4. `SEMANTICS.md` and the grammar document match what the implementation actually does today.
5. One failure case is rehearsed and its disclosure worded.
6. Every teammate can run the demo and explain the distinctive feature solo.
7. Reproducibility: Python version listed, any dependencies pinned, setup tested by the teammate who did not write it.

---

## Reflection Prompt

In your notebook: compare the feedback your team received today with the error messages your language gives its users. Both are diagnostics offered to someone mid-effort. What makes each actionable or useless, and what will you change in one of them this week?

---

## 6. Further Reading

- The project specification's Demo Day rubric, reread tonight.
- Robert Nystrom. *Crafting Interpreters*, the "Challenges" sections of your weakest chapter, as triage inspiration.
