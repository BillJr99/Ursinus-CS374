---
layout: assignment
permalink: /Projects/TeamLanguage
title: "CS374: Principles of Programming Languages - Final Project: A Language of Your Own"

info:
  coursenum: CS374
  purpose: "To design, build, document, and perform a programming language of your own — assembled from the semester's lexer, parser, AST, environment, and evaluator components — proving they were reusable components that snap together and grow."
  tilt:
    task: "In rotating-role team sprints, choose your language's direction, integrate your components into one pipeline, add a distinctive feature (going deeper via the Extensions Menu if you choose), and ship a REPL, file-runner, samples, tests, and SEMANTICS.md, then present the language at Demo Day."
    criteria: "Assessed on the Sprint 0 proposal, language design and documentation, implementation correctness and integration, testing, reproducibility, and the Demo Day presentation, weighted 25/20/20/15/10/10. The proposal (25 points) is due at the Sprint 0 kickoff; the remaining 75 points are earned at Demo Day with the final submission — see the course schedule for the dates, and the rubric below for the full breakdown."
  points: 100
  goals:
    - To design a programming language with a niche, a documented grammar, and exhaustive semantics
    - To choose and commit to a direction — a general-purpose or domain language of the team's design, or a music/live-coding language — and defend that choice against the design scorecard
    - To implement the language end to end by integrating the lexer, parser, AST, environments, and evaluator built across the semester
    - To implement at least one distinctive feature requiring real design and implementation work
    - To deliver a tested, reproducible implementation with a REPL, file-runner, and sample program suite
    - To present the language at a public Demo Day with a candid account of its limitations
    - To work in sustained team sprints with rotating roles and structured peer review
  rubric:
    - weight: 25
      description: Proposal (due at the Sprint 0 kickoff)
      preemerging: The proposal is missing, or names a language with no niche, grammar, or plan
      beginning: The proposal states a niche but the grammar v0, node inventory, or SEMANTICS.md v0 is missing or generic, or the merge plan and sprint plan are absent
      progressing: All checklist items are present and specific, with minor gaps such as a vague risk pre-mortem or an incomplete node inventory
      proficient: Every checklist item is complete and specific, the chosen direction is declared and defended against the design scorecard, the distinctive feature (and any Extensions Menu adoptions) is scoped to fit the sprint plan, and the proposal is delivered on time at the Sprint 0 kickoff
    - weight: 20
      description: Language Design and Documentation
      preemerging: The language has no documented grammar or semantics, or the design is the class language unchanged
      beginning: A grammar exists but diverges from the implementation, and semantics documentation is generic or incomplete
      progressing: The grammar and SEMANTICS.md are complete and largely match the implementation, with a stated niche and scorecard, and minor gaps
      proficient: The niche, scorecard, EBNF grammar, node inventory, and exhaustive SEMANTICS.md are complete, current, and verified against the implementation, with a decision log recording contested choices and their rationales
    - weight: 20
      description: Implementation Correctness and Integration
      preemerging: The implementation fails to run the sample programs
      beginning: The implementation runs but fails on several sample or test programs due to one or more minor issues
      progressing: The implementation passes its test suite and sample programs, with a fragile area such as error recovery or a semantics corner that diverges from the documentation
      proficient: The integrated pipeline passes a substantive test suite and all sample programs, the distinctive feature works end to end, error messages identify their stage and position, and behavior matches SEMANTICS.md throughout
    - weight: 15
      description: Evaluation and Testing
      preemerging: No systematic testing exists
      beginning: A minimal test suite exists without coverage of the distinctive feature or error cases
      progressing: The test suite covers the core language, the distinctive feature, and error cases, with results tracked across sprints
      proficient: The test suite covers the core language, the distinctive feature, error cases, and the differential semantics programs, results are tracked across sprints with the failing-test-as-specification discipline visible in the history, and at least three fixed bugs are documented with their regression tests
    - weight: 10
      description: Documentation and Reproducibility
      preemerging: The repository cannot be run by a stranger
      beginning: Setup works but documentation is thin or stale
      progressing: A stranger can run the REPL and samples from the readme, with minor gaps, and the ShipIt self-check was attempted with gaps remaining (e.g., a private repo, a missing license, or no portfolio link)
      proficient: A fresh clone runs the REPL, file-runner, and all samples in under three minutes following the readme, the language reference document teaches the language to a newcomer with examples, dependencies and versions are pinned, and setup was tested by the teammate who did not write it; and the repository passes the ShipIt self-check — public, with a license, a recruiter-legible readme (what, install, first program in thirty seconds) crediting each member's contribution, and either packaged for installation (pip, npm, or Docker) or linked with a project story from each member's portfolio or GitHub profile
    - weight: 10
      description: Demo Day Presentation
      preemerging: The presentation is missing or no demonstration occurs
      beginning: The presentation shows the happy path only, with uneven team participation
      progressing: The presentation includes a live demonstration and acknowledges limitations, with most teammates participating
      proficient: The presentation includes a live REPL demonstration, a sample program showcasing the niche, the distinctive feature explained by its non-author, a rehearsed disclosure of one known limitation, and every teammate presenting
  readings:
    - rtitle: "Language Design Studio Activity"
      rlink: "https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374/gh-pages/_pages/Activities/liascript-languagedesign.md"
    - rtitle: "Sprint Studio Protocol"
      rlink: "https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374/gh-pages/_pages/Activities/liascript-sprintstudio.md"
    - rtitle: "Music and Live-Coding Track Guide (for Direction B: deliverable equivalence table and the text-events-only route)"
      rlink: "https://www.billmongan.com/Ursinus-CS374-Fall2026/Assignments/MusicTrack"
    - rtitle: "Make-a-Lisp (mal) — incremental scaffold with a built-in test harness (Direction A option)"
      rlink: "https://github.com/kanaka/mal"
    - rtitle: "A Syntax Highlighter for Your Language with tree-sitter (Extensions Menu)"
      rlink: "https://www.billmongan.com/Ursinus-CS374-Fall2026/Tutorials/SyntaxHighlighter"
    - rtitle: "ShipIt Guide: Repo Hygiene, README, Packaging, and Your Portfolio (required self-check before Demo Day)"
      rlink: "https://www.billmongan.com/Ursinus-CS374-Fall2026/Assignments/ShipIt"
    - rtitle: "Demo Day Guide: External Guests and Technical Interview Practice"
      rlink: "https://www.billmongan.com/Ursinus-CS374-Fall2026/Assignments/DemoDayGuide"

tags:
  - final-project
  - languages
  - team
  - dsl
  - music

---

# Overview

Your team will design, implement, document, and present **a programming language of your own**: a real language with a niche, a grammar, documented semantics, and a working implementation assembled from the lexer, parser, AST, environment, and evaluator components your members built individually. The project is the proof that the semester's components were components: they snap together, and then they grow.

**Required scope.** Your language must include variables with documented scoping; arithmetic with full precedence and associativity; booleans, comparisons, and short-circuit logic; selection and iteration; strings or another non-numeric type; and at least one **distinctive feature** requiring real design and implementation (functions with closures, a desugared construct, pattern slices, or a domain-specific statement serving your niche). It ships with a REPL, a file-runner, at least five sample programs (one showcasing the niche), a test suite, a language reference document, and `SEMANTICS.md`. (Direction B teams satisfy this scope through the equivalences described below.)

Teams are three members each, formed in the design phase from your standing POGIL groups. Project roles (**Coordinator**, **Builder**, **Evaluator**, **Scribe**) rotate at every sprint boundary so every member holds every role; your report's contribution statements must show the rotation.

**Reference implementation policy.** Teams may build on the released reference lexer, parser, and interpreter instead of (or merged with) their own semester components, declared in the project README. The project is graded on the language you design and build on top, not on whose components you started from — spend your sprint time on the design, the distinctive feature, and the integration, wherever your starting components came from.

---

## Timeline and Milestones

The project is worth **100 points** total, earned at two graded milestones:

| Milestone (see the course schedule for dates) | What happens | Points |
|---|---|---|
| Project hand-out | Design phase begins: form teams of 3, pick a niche, draft the design scorecard | — |
| Design-phase studio check | Design-phase milestone: team, niche, and design scorecard (checked in studio, ungraded) | — |
| **Sprint 0 kickoff** | **Proposal due, presented in class** | **25** |
| Sprint 1 (see schedule) | Integrate components, with an in-class working-time session | — |
| Sprint 2 studio | Gallery walk and peer review | — |
| Sprint 3 studio | Release hardening | — |
| **Demo Day (last class meeting)** | **Demo Day and final submission** | **75** |

Demo Day is the **last class meeting**. There is no final exam, and no work is accepted after the last class.

---

## Choose Your Direction

Every team declares one of two directions in its proposal. Both are the same project — the same milestones, the same rubric, the same deliverables discipline — pointed at different niches.

### Direction A: A General-Purpose or Domain Language of Your Design

The default framing above: design a language with a niche of your choosing (a recipe DSL, a query language over in-memory lists, a turtle-graphics language, a logic language, a constraint language, or a compelling original idea), implement the required scope end to end from your semester components, and add a distinctive feature that serves the niche. Everything in the stage descriptions below applies as written.

> **Scaffold option — Make-a-Lisp (mal).** If your team's niche is a Lisp-shaped or expression-oriented language, you may build on the **[Make-a-Lisp (mal)](https://github.com/kanaka/mal)** process as your scaffold instead of starting the front end from scratch. mal is an eleven-step incremental path to a working Lisp, and — the reason it is worth knowing about — it ships a **shared test harness** (`runtest.py` against per-step `.mal` test files) that becomes a free, rigorous regression suite for your language as you build. You still own the design: you must give the language a real niche and distinctive feature of your own (mal out of the box is a generic Lisp, which is not by itself a distinctive feature), document your semantics, and integrate your team's components — but mal's staged tests and reference structure can carry the routine reader/eval/print plumbing so your sprint time goes to the parts that make your language *yours*. Cite mal in your proposal if you adopt it, and note which steps you used.

### Direction B: A Music / Live-Coding Language

Design a small live-coding language of your own — a language whose programs denote **timed event structures over cycle time**, in the tradition of the mini-notation you studied. Past directions that have worked well include a drum-machine language of named, layered tracks with mutation operators; a melodic language with scales, degrees, and transposition as first-class constructs; a language of rhythmic transformations (rotate, invert, thin) applied to seed patterns; and a language for spatial or lighting cues synchronized to cycles, which shows that cycle semantics generalizes beyond audio.

Direction B maps onto the same timeline and stages:

- **Proposal (Sprint 0):** your design document additionally includes a denotational semantics — one displayed equation per construct, mapping programs to event sets over cycle spans — at least one **algebraic law** your language satisfies, stated as an equation, and a design rationale argued against the embedded-versus-external tradeoff axes, with at least two rejected alternatives. These stand in for (or fold into) `SEMANTICS.md` v0.
- **Sprint 1:** the lexical and syntactic front end — built either from your semester's Python components or with flex/bison (if you use bison, keep the grammar conflict-free and include the `-v` automaton report in your repository) — parsing every specification example and printing ASTs with location-prefixed errors.
- **Sprint 2:** the evaluator, by structural recursion over the AST, one case per semantic equation, each case commented with the equation it implements, emitting a **timed event list**.
- **Sprint 3:** hardening, the specification-driven test suite (every semantic equation has at least one test against a hand-computed event list; the algebraic law is verified empirically on at least three instances; stochastic constructs are reproducible under a fixed seed), and performance rehearsal.
- **Demo Day:** your live demonstration closes with a short **performance** — live-editing and re-running a program while the class follows the event output as it changes. **Emitting events as text is sufficient; audio hardware is never required.** Ambitious teams may additionally render sound by translating event lists into Strudel or MIDI, and that translation layer — mapping your semantics onto someone else's — is itself worth a section of your report.

The required scope maps naturally: patterns and tracks are your non-numeric type, cycle arithmetic and transformation operators are your arithmetic and precedence story, conditional and repeated structures are your selection and iteration, and the cycle semantics itself is a distinctive feature by construction. The **Music and Live-Coding guide** at [Assignments/MusicTrack](/Assignments/MusicTrack) provides the full equivalence table mapping each deliverable to its classic counterpart, plus the text-events-only route through the whole track.

---

## Extensions Menu

The distinctive feature is required; the Extensions Menu is where teams go deeper. Adopting one or more extensions is a way to raise the ceiling of your language — depth here is credited through the project rubric (chiefly *Implementation Correctness and Integration*, *Evaluation and Testing*, and *Language Design and Documentation*), not through separate point values. An extension counts only when it is documented in your language reference, covered by at least two dedicated test programs, and demonstrated. A fully working extension with tests scores far better than two half-working ones without: scope what you adopt in your proposal's sprint plan.

### Static Type Inference (Hindley–Milner)

Add a type-checking pass that runs before evaluation and infers types for every expression without user-written annotations, reporting type errors with positions and the conflicting types. Implement let-polymorphism so a polymorphic utility (such as an identity function) works at multiple types in one program. Include a test program that is correctly rejected.

### Transpilation to Another Language

Add a visitor-based code generator that walks your AST and emits valid Python 3 or ES2020 source as a standalone file runnable with `python3` or `node`, producing output identical to your interpreter for every test program. Parenthesize operator precedence correctly in the target, document any constructs that do not transpile and the substitution your generator makes, and make the back end a runtime flag alongside your interpreter so a test harness can diff the two execution paths across your whole suite.

### Bytecode Compiler and Stack VM

Add a two-phase back end: a compiler lowering your AST to a linear stack-machine instruction sequence (PUSH, LOAD, STORE, ADD, JMP_IF_FALSE, CALL, RETURN, and kin) and a virtual machine executing it, producing the same output as the tree-walking evaluator on all test programs. Include an annotated execution trace for one non-trivial program showing each instruction, the operand stack before and after, and the program counter.

### Pattern Matching over Algebraic Data Types

Add user-definable algebraic data types and a `match` construct supporting at minimum constructor patterns and wildcard. Exhaustiveness checking is recognized in grading. Demonstrate with at least one recursive ADT (a list or tree) and a recursive function over it.

### Garbage Collector

Implement a mark-and-sweep or Cheney copying collector over your runtime environment and heap-allocated values. Demonstrate that cyclic structures are identified and collected, include a program that would leak without a GC, and report live and dead object counts before and after a collection cycle.

### Concurrency Primitives

Add `spawn` (lightweight concurrent execution) and channel send/receive, implemented with threads, asyncio, or similar. Demonstrate a producer/consumer program communicating through a channel, and document your memory model: are variables shared, isolated, or communicated exclusively through channels?

### Macros or Hygienic Quoting

Add a macro system that expands at parse time, with hygienic renaming so bindings introduced inside a macro body do not capture user bindings of the same name. Demonstrate at least two macros — one structural (such as `unless`) and one that introduces a binding — plus a test case that would fail under unhygienic expansion and passes under yours.

### Foreign Function Interface

Allow calling host-language functions from your language via a `foreign` declaration, with marshalling that converts your values to host objects before the call and back after. Demonstrate at least two foreign functions whose results feed further computation in your language.

### Libraries and Packaging

Give your language a **module system**: an `import` form that creates a module environment and runs its top-level code, qualified access (`mod.name`), a from-import that copies bindings into the caller's environment, and circular-import detection that raises a clean error rather than recursing forever. Module namespaces must be isolated — private names are not reachable from outside without qualification. Test with at least three modules, including one that imports another.

On the packaging side, structure your *implementation* as a proper package with a clean public API (`__init__.py` re-exports, `__all__`, underscore-private helpers), and consider a plugin architecture — discovering extension modules by name pattern via `importlib` and validating each against a required interface, skipping malformed plugins with a warning — as a way to make your language's built-in library user-extensible.

### Scripting and Automation Targets

Make your language a good citizen of the shell: a file-runner that composes in pipelines (reads stdin, writes stdout, sends errors to stderr), meaningful exit codes on success and each error class, and a scripts-as-tests harness — a driver that runs your whole sample suite, checks exit codes, prints a pass/fail line per program, and exits non-zero if anything failed. Ship the driver and any helper scripts shellcheck-clean and portable (no GNU-only flags without a fallback), with a README explaining how to run the suite. If your language's niche *is* automation — a build language, a text-processing language, a task-runner DSL — this extension deepens into the niche itself: demonstrate your language orchestrating real programs through pipes and redirection.

### Editor Support: Syntax Highlighting (and an Optional Diagnostic)

Give your language real editor support so an audience *sees* it is a language: a [tree-sitter](https://tree-sitter.github.io/tree-sitter/) grammar for your syntax (its precedence annotations mirror the ladder you already wrote) plus a `highlights.scm` query, or — the lower-friction route — a TextMate grammar wrapped in a minimal VS Code extension. Scope this small: keyword/number/operator/string coloring is a complete extension. The "wow" upgrade is one live **diagnostic** — pipe your interpreter's positioned error output (`line L, col C: message`, which your pipeline already emits) into VS Code's diagnostics API so a bad program shows a red squiggle at the right spot. Demonstrate on a sample program at Demo Day, and include a README line showing how a grader installs the extension. The [Syntax Highlighter tutorial](/Tutorials/SyntaxHighlighter) is the step-by-step companion.

### Contribute Upstream: An Open-Source Contribution

Instead of (or alongside) extending your own language, contribute to an existing open-source ecosystem your project touches: a pattern or transformation function in [Strudel](https://github.com/tidalcycles/strudel)/TidalCycles (a natural fit for Direction B teams), a [tree-sitter](https://tree-sitter.github.io/tree-sitter/) grammar improvement (pairs with the Editor Support extension), a step port or test-suite improvement in [Make-a-Lisp (mal)](https://github.com/kanaka/mal), or documentation and worked examples for [SWI-Prolog](https://www.swi-prolog.org/). This counts like any other extension — credited through the existing rubric dimensions — when the issue you are addressing is scoped in your proposal, the pull request is submitted with tests and documentation following the upstream project's contributing guidelines, and the maintainer exchange is documented in your report. A merged PR is ideal but **not required** — a substantive review exchange is what is credited, because maintainer response times are outside your control. A real contribution reviewed by a real maintainer is a portfolio line few graduates have.

---

## Stage 1: Design Phase and Proposal (proposal due at the Sprint 0 kickoff — 25 points)

The project hand-out opens a **design phase**: form your team of three, pick a niche, and draft the design scorecard. The design-phase milestone — team, niche, and scorecard — is checked at the design-phase studio check (ungraded); it exists so the graded proposal that follows is a refinement, not a scramble.

The proposal itself is due at the Sprint 0 kickoff, and is **presented in class**. A two-to-three page proposal containing:

**Checklist:**
- The language name, niche, and three-sentence pitch, with your **direction (A or B)** declared.
- The design scorecard: readability, writability, reliability, and implementation cost, with priorities and sacrifices stated.
- Grammar v0 in EBNF, with differences from the class language marked.
- The node inventory table: every AST node, fields, producing rule, consuming rule.
- `SEMANTICS.md` v0 importing your assignment-era decisions and adding the niche feature's semantics (Direction B: the denotational equations, algebraic law, and embedded/external rationale described above).
- The distinctive feature specification: syntax, semantics, and the pipeline stages it touches — plus any **Extensions Menu** adoptions, scoped to the sprint plan.
- The merge plan: whose lexer, parser, and evaluator seed the integration, and the order of merging.
- The risk pre-mortem: the most likely derailment and the smallest experiment that retires it.
- The sprint plan with role rotation schedule.

---

## Stage 2: Sprints and Studios (Sprint 0 kickoff through the release-hardening studio)

Build in sprints aligned with the in-class studio days (see the course schedule for dates), following the sprint studio protocol: stand-ups with numbers, failing tests as specifications, current documents, role rotation at boundaries. **Sprint 1 (see schedule)** integrates members' components into one pipeline running the class language (Direction B: the front end printing ASTs), with an in-class working-time session; if a break falls inside the sprint window, front-load the integration so a working pipeline travels with you. **Sprint 2 (gallery-walk studio)** implements grammar differences and the distinctive feature's skeleton (Direction B: the evaluator emitting timed events); **Sprint 3 (release-hardening studio)** completes the feature, hardens errors, and finishes the sample suite — budget ~4 hours for the ShipIt checks (cold clone-to-run, packaging, README) — they are scored in the Documentation and Reproducibility dimension. The **gallery walk** (Sprint 2 studio day) is mandatory: host with one known failure shown, walk with Strength, Question, and Risk cards, and triage all feedback into fix, disclose, or future work. The **release hardening** studio is your last in-class working session before Demo Day.

---

## Stage 3: Demo Day (the last class meeting)

With all teams presenting in a single class session, each team has a hard cap of **9 minutes**, plus a 1-minute transition to the next team. Within your 9 minutes:

1. The pitch: niche, scorecard, and one design decision defended (60 seconds each).
2. The live demonstration: the REPL, a sample program showcasing the niche, and the distinctive feature **explained and demonstrated by a teammate who did not implement it**. Direction B teams close with the short performance described above — a live edit-and-rerun over the event output.
3. The candid minute: one known limitation, disclosed with its triage rationale.
4. The numbers: the test results table and one bug story with its regression test.

Every teammate speaks. The audience (your classmates) will write one Strength and one Question card per language; responding to your cards is part of the report.

Demo Day is **external-facing**: alumni, industry guests, and faculty from other departments may join the audience and Q&A, as available — your grade never depends on who attends. Prepare with the [Demo Day Guide](/Assignments/DemoDayGuide); the final sprint studios include a cross-team mock-interview rehearsal, credited as class participation.

There is no final exam. Demo Day and the final submission fall on the last class meeting, and **no work is accepted after the last class**.

---

## Stage 4: Final Submission (Demo Day — 75 points, together with the presentation)

**Deliverables:**
1. **The repository**: the integrated implementation, REPL and file-runner, test suite, sample programs with expected outputs, all configuration in JSON, located exception handling throughout, and a readme tested by the teammate who did not write it. Ensure reproducibility by fixing random seeds where applicable and listing software version information. The repository is public and recruiter-legible: run the [ShipIt self-check](/Assignments/ShipIt) before Demo Day — it is scored within the Documentation and Reproducibility dimension. (Direction B: the timed-event test fixtures and, if you used bison, the automaton report ride along here.)
2. **The language reference** (approximately four pages): teach your language to a newcomer with examples for every construct, the full grammar, the distinctive feature's guide, and a section per adopted extension.
3. **`SEMANTICS.md`**, final and verified against the implementation by the differential programs (Direction B: the semantic equations, revised to match the implemented language, with a change log from the proposal).
4. **The report** (approximately four pages): the design story with the decision log's three most contested calls, the integration experience (what snapped together, what did not, and why), the evaluation summary, limitations (your disclose bucket, verbatim), responses to your Demo Day cards, and individual contribution statements covering the rotation. (Direction B: include the performance postmortem — what performing revealed that the test suite could not — and, if you rendered audio, the translation-layer section.)

---

### Submission Rubric

The rubric rewards a finished minimal language over an ambitious unfinished one: the required feature list at proficient IS the target; extensions distinguish work beyond proficient.

See the **rubric** section in this assignment for the detailed evaluation breakdown. The Proposal dimension (25 points) is assessed at the Sprint 0 kickoff; the remaining dimensions (75 points) are assessed at Demo Day.

## Reflection Prompts

Answer individually in your contribution statement:

- Which component (yours or a teammate's) survived integration best, and what property made it survive?
- Which design decision would you reverse if you had one more sprint, and what would it cost now versus what it would have cost in Sprint 0?
- Do you certify that your contribution statement accurately represents your own work? Please identify any and all portions of the project that were not originally created by your team.
- AI disclosure: list any generative-AI tools you used, for what, and how you verified the results (or state 'none').
- Approximately how many hours did the project take you personally (I will not judge you for this at all...I am simply using it to gauge if the assignments are too easy or hard)?
