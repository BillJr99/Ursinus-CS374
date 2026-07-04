---
layout: assignment
permalink: /Projects/TeamLanguage
title: "CS374: Principles of Programming Languages - Final Project: A Language of Your Own"

info:
  coursenum: CS374
  points: 100
  goals:
    - To design a programming language with a niche, a documented grammar, and exhaustive semantics
    - To implement the language end to end by integrating the lexer, parser, AST, environments, and evaluator built across the semester
    - To implement at least one distinctive feature requiring real design and implementation work
    - To deliver a tested, reproducible implementation with a REPL, file-runner, and sample program suite
    - To present the language at a public Demo Day with an honest account of its limitations
    - To work in sustained team sprints with rotating roles and structured peer review
  rubric:
    - weight: 30
      description: Language Design and Documentation
      preemerging: The language has no documented grammar or semantics, or the design is the class language unchanged
      beginning: A grammar exists but diverges from the implementation, and semantics documentation is generic or incomplete
      progressing: The grammar and SEMANTICS.md are complete and largely match the implementation, with a stated niche and scorecard, and minor gaps
      proficient: The niche, scorecard, EBNF grammar, node inventory, and exhaustive SEMANTICS.md are complete, current, and verified against the implementation, with a decision log recording contested choices and their rationales
    - weight: 25
      description: Implementation Correctness and Integration
      preemerging: The implementation fails to run the sample programs
      beginning: The implementation runs but fails on several sample or test programs due to one or more minor issues
      progressing: The implementation passes its test suite and sample programs, with a fragile area such as error recovery or a semantics corner that diverges from the documentation
      proficient: The integrated pipeline passes a substantive test suite and all sample programs, the distinctive feature works end to end, error messages identify their stage and position, and behavior matches SEMANTICS.md throughout
    - weight: 20
      description: Evaluation and Testing
      preemerging: No systematic testing exists
      beginning: A minimal test suite exists without coverage of the distinctive feature or error cases
      progressing: The test suite covers the core language, the distinctive feature, and error cases, with results tracked across sprints
      proficient: The test suite covers the core language, the distinctive feature, error cases, and the differential semantics programs, results are tracked across sprints with the failing-test-as-specification discipline visible in the history, and at least three fixed bugs are documented with their regression tests
    - weight: 13
      description: Documentation and Reproducibility
      preemerging: The repository cannot be run by a stranger
      beginning: Setup works but documentation is thin or stale
      progressing: A stranger can run the REPL and samples from the readme, with minor gaps
      proficient: A fresh clone runs the REPL, file-runner, and all samples in under three minutes following the readme, the language reference document teaches the language to a newcomer with examples, dependencies and versions are pinned, and setup was tested by the teammate who did not write it
    - weight: 12
      description: Demo Day Presentation
      preemerging: The presentation is missing or no demonstration occurs
      beginning: The presentation shows the happy path only, with uneven team participation
      progressing: The presentation includes a live demonstration and acknowledges limitations, with most teammates participating
      proficient: The presentation includes a live REPL demonstration, a sample program showcasing the niche, the distinctive feature explained by its non-author, a rehearsed disclosure of one known limitation, and every teammate presenting
  readings:
    - rtitle: "Language Design Studio Activity"
      rlink: "https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374-Fall2026/gh-pages/_pages/Activities/liascript-languagedesign.md"
    - rtitle: "Sprint Studio Protocol"
      rlink: "https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374-Fall2026/gh-pages/_pages/Activities/liascript-sprintstudio.md"

tags:
  - final-project
  - languages
  - team

---

# Overview

Your team will design, implement, document, and present **a programming language of your own**: a real language with a niche, a grammar, documented semantics, and a working implementation assembled from the lexer, parser, AST, environment, and evaluator components your members built individually. The project is the proof that the semester's components were components: they snap together, and then they grow.

**Required scope.** Your language must include variables with documented scoping; arithmetic with full precedence and associativity; booleans, comparisons, and short-circuit logic; selection and iteration; strings or another non-numeric type; and at least one **distinctive feature** requiring real design and implementation (functions with closures, a desugared construct, pattern slices, or a domain-specific statement serving your niche). It ships with a REPL, a file-runner, at least five sample programs (one showcasing the niche), a test suite, a language reference document, and `SEMANTICS.md`.

Teams are your standing POGIL teams of three or four. Project roles (**Coordinator**, **Builder**, **Evaluator**, **Scribe**) rotate at every sprint boundary so every member holds every role; your report's contribution statements must show the rotation.

---

## Stage 1: Proposal (due at the end of Sprint 0 week)

A two-to-three page proposal containing:

**Checklist:**
- The language name, niche, and three-sentence pitch.
- The design scorecard: readability, writability, reliability, and implementation cost, with priorities and sacrifices stated.
- Grammar v0 in EBNF, with differences from the class language marked.
- The node inventory table: every AST node, fields, producing rule, consuming rule.
- `SEMANTICS.md` v0 importing your assignment-era decisions and adding the niche feature's semantics.
- The distinctive feature specification: syntax, semantics, and the pipeline stages it touches.
- The merge plan: whose lexer, parser, and evaluator seed the integration, and the order of merging.
- The risk pre-mortem: the most likely derailment and the smallest experiment that retires it.
- The sprint plan with role rotation schedule.

---

## Stage 2: Sprints and Studios (weeks 13 through 15)

Build in sprints aligned with the in-class studio days, following the sprint studio protocol: stand-ups with numbers, failing tests as specifications, current documents, role rotation at boundaries. **Sprint 1** integrates members' components into one pipeline running the class language; **Sprint 2** implements grammar differences and the distinctive feature's skeleton; **Sprint 3** completes the feature, hardens errors, and finishes the sample suite. The **gallery walk** (scheduled studio day) is mandatory: host with one known failure shown, walk with Strength, Question, and Risk cards, and triage all feedback into fix, disclose, or future work.

---

## Stage 3: Demo Day (final exam meeting)

A 12-minute presentation plus questions:

1. The pitch: niche, scorecard, and one design decision defended (60 seconds each).
2. The live demonstration: the REPL, a sample program showcasing the niche, and the distinctive feature **explained and demonstrated by a teammate who did not implement it**.
3. The honest minute: one known limitation, disclosed with its triage rationale.
4. The numbers: the test results table and one bug story with its regression test.

Every teammate speaks. The audience (your classmates) will write one Strength and one Question card per language; responding to your cards is part of the report.

---

## Stage 4: Final Submission (Demo Day)

**Deliverables:**
1. **The repository**: the integrated implementation, REPL and file-runner, test suite, sample programs with expected outputs, all configuration in JSON, located exception handling throughout, and a readme tested by the teammate who did not write it. Ensure reproducibility by fixing random seeds where applicable and listing software version information.
2. **The language reference** (approximately four pages): teach your language to a newcomer with examples for every construct, the full grammar, and the distinctive feature's guide.
3. **`SEMANTICS.md`**, final and verified against the implementation by the differential programs.
4. **The report** (approximately four pages): the design story with the decision log's three most contested calls, the integration experience (what snapped together, what did not, and why), the evaluation summary, limitations (your disclose bucket, verbatim), responses to your Demo Day cards, and individual contribution statements covering the rotation.

---

### Submission Rubric

See the **rubric** section in this assignment for the detailed evaluation breakdown.

## Reflection Prompts

Answer individually in your contribution statement:

- Which component (yours or a teammate's) survived integration best, and what property made it survive?
- Which design decision would you reverse if you had one more sprint, and what would it cost now versus what it would have cost in Sprint 0?
- Do you certify that your contribution statement accurately represents your own work? Please identify any and all portions of the project that were not originally created by your team.
- Approximately how many hours did the project take you personally (I will not judge you for this at all...I am simply using it to gauge if the assignments are too easy or hard)?
