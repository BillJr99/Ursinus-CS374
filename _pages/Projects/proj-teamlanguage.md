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
      rlink: "/Projects/TeamLanguage#the-music-and-live-coding-path"
    - rtitle: "Make-a-Lisp (mal): incremental scaffold with a built-in test harness (Direction A option)"
      rlink: "https://github.com/kanaka/mal"
    - rtitle: "A Syntax Highlighter for Your Language with tree-sitter (Extensions Menu)"
      rlink: "https://www.billmongan.com/Ursinus-CS374-Fall2026/Tutorials/SyntaxHighlighter"
    - rtitle: "ShipIt Guide: Repo Hygiene, README, Packaging, and Your Portfolio (required self-check before Demo Day)"
      rlink: "/Projects/TeamLanguage#shipping-your-language-the-shipit-checklist"
    - rtitle: "Demo Day Guide: External Guests and Technical Interview Practice"
      rlink: "/Projects/TeamLanguage#demo-day-external-guests-and-technical-interview-practice"

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

**Your team over the project's seven weeks.** Teams reliably pass through recognizable stages (Tuckman, 1965), and this project's milestones are placed on that map deliberately. Your **team charter** (drafted at the design-phase milestone, signed with the proposal) is the *forming* work — you do it before the stakes are high. The **design phase** is where *storming* is expected: the argument over which niche to serve and what the design scorecard says is the productive conflict, so have it out loud in your own team meeting rather than quietly in a group chat. The **Sprint 0 proposal** is *norming* made concrete — a signed, presented agreement about what you are building and who owns what. The **sprints** are *performing*: role rotation and stand-ups carry the load, and the team self-corrects without drama. **Demo Day's retrospective** is *adjourning*: close deliberately, with contribution statements and the portfolio story each member takes with them. If the design phase feels contentious, that is the map working — run the charter's conflict-repair process and keep moving.

**Reference implementation policy.** Teams may build on the released reference lexer, parser, and interpreter instead of (or merged with) their own semester components, declared in the project README. The project is graded on the language you design and build on top, not on whose components you started from — spend your sprint time on the design, the distinctive feature, and the integration, wherever your starting components came from.

---

## Timeline and Milestones

The project is worth **100 points** total, earned at two graded milestones (proposal and Demo Day). The two small 3-point checkpoints along the way are assessed within Class Activities and Participation — they keep the team honest without raising the stakes of a studio day:

| Milestone (see the course schedule for dates) | What happens | Points |
|---|---|---|
| Project hand-out | Design phase begins: form teams of 3, pick a niche, draft the design scorecard | - |
| Design-phase studio check | Design-phase milestone: team, niche, design scorecard, and the **draft team charter** (submitted as the design-phase milestone; 3 points, assessed within Class Activities and Participation) | 3 |
| **Sprint 0 kickoff** | **Proposal due, presented in class — includes the signed team charter** | **25** |
| Sprint 1 increment checkpoint (see schedule) | Integrate components, with an in-class working-time session; checkpoint includes the charter re-read and confidential peer pulse (3 points, assessed within Class Activities and Participation) | 3 |
| Sprint 2 studio | Gallery walk and peer review | - |
| Sprint 3 studio | Release hardening | - |
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

The required scope maps naturally: patterns and tracks are your non-numeric type, cycle arithmetic and transformation operators are your arithmetic and precedence story, conditional and repeated structures are your selection and iteration, and the cycle semantics itself is a distinctive feature by construction. The **Music and Live-Coding guide** at [Projects/TeamLanguage#the-music-and-live-coding-path]({{ site.baseurl }}/Projects/TeamLanguage#the-music-and-live-coding-path) provides the full equivalence table mapping each deliverable to its classic counterpart, plus the text-events-only route through the whole track.

---

## Extensions Menu

The distinctive feature is required; the Extensions Menu is where teams go deeper. Adopting one or more extensions is a way to raise the ceiling of your language — depth here is credited through the project rubric (chiefly *Implementation Correctness and Integration*, *Evaluation and Testing*, and *Language Design and Documentation*), not through separate point values. An extension counts only when it is documented in your language reference, covered by at least two dedicated test programs, and demonstrated. A fully working extension with tests scores far better than two half-working ones without: scope what you adopt in your proposal's sprint plan.

### Static Type Inference (Hindley-Milner)

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

Give your language real editor support so an audience *sees* it is a language: a [tree-sitter](https://tree-sitter.github.io/tree-sitter/) grammar for your syntax (its precedence annotations mirror the ladder you already wrote) plus a `highlights.scm` query, or — the lower-friction route — a TextMate grammar wrapped in a minimal VS Code extension. Scope this small: keyword/number/operator/string coloring is a complete extension. The "wow" upgrade is one live **diagnostic** — pipe your interpreter's positioned error output (`line L, col C: message`, which your pipeline already emits) into VS Code's diagnostics API so a bad program shows a red squiggle at the right spot. Demonstrate on a sample program at Demo Day, and include a README line showing how a grader installs the extension. The [Syntax Highlighter tutorial]({{ site.baseurl }}/Tutorials/SyntaxHighlighter) is the step-by-step companion.

### Contribute Upstream: An Open-Source Contribution

Instead of (or alongside) extending your own language, contribute to an existing open-source ecosystem your project touches: a pattern or transformation function in [Strudel](https://github.com/tidalcycles/strudel)/TidalCycles (a natural fit for Direction B teams), a [tree-sitter](https://tree-sitter.github.io/tree-sitter/) grammar improvement (pairs with the Editor Support extension), a step port or test-suite improvement in [Make-a-Lisp (mal)](https://github.com/kanaka/mal), or documentation and worked examples for [SWI-Prolog](https://www.swi-prolog.org/). This counts like any other extension — credited through the existing rubric dimensions — when the issue you are addressing is scoped in your proposal, the pull request is submitted with tests and documentation following the upstream project's contributing guidelines, and the maintainer exchange is documented in your report. A merged PR is ideal but **not required** — a substantive review exchange is what is credited, because maintainer response times are outside your control. A real contribution reviewed by a real maintainer is a portfolio line few graduates have.

---

## Stage 1: Design Phase and Proposal (proposal due at the Sprint 0 kickoff — 25 points)

The project hand-out opens a **design phase**: form your team of three, pick a niche, draft the design scorecard, and draft your team charter. This phase runs outside class - there is no studio session for it - so budget a team meeting of your own between the hand-out and the milestone. The design-phase milestone — team, niche, scorecard, and draft charter — is submitted through Canvas (3 points, assessed within Class Activities and Participation); it exists so the graded proposal that follows is a refinement, not a scramble.

### The Team Charter

Your team writes a one-page charter it will actually use. Draft it for the design-phase milestone; the **signed** version is part of the proposal. All four topics are required.

**Role rotation plan.** The project phase uses four roles: **Coordinator** (sprint planning, scope), **Builder** (implementation), **Evaluator** (testing and sample programs), **Scribe** (documentation and decision log). State how your team will rotate them: e.g., "we will rotate by sprint, in alphabetical order by last name." Every member must hold every role at least once.

**External communication channel and norms.** State where the team will communicate outside class (Discord, text, email — pick one channel and use it consistently). State your response-time norm: e.g., "we will respond within 24 hours on weekdays, 48 on weekends." State how you will signal availability changes (illness, travel, exam crunch).

**Preparation norms.** State what "prepared for class" means for your team: e.g., "readings and previous activity reviewed before class; laptop charged; roles assigned by the start of class." State what you will do if a member is unprepared.

**Disagreement resolution.** State a concrete mechanism for resolving technical disagreements (e.g., "we will vote; ties go to the Coordinator") and interpersonal disagreements (e.g., "we will raise the issue with the Scribe, who records it in the decision log; unresolved issues go to the instructor"). Having this written before a disagreement occurs is the point.

All members sign the charter (typed names suffice) for the proposal. One charter per team; the Sprint 1 increment checkpoint is where you re-read it and file a revision if it no longer describes your team.

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
- The **signed team charter** (all four topics, every member's typed signature), revised from the design-phase draft.

---

## Stage 2: Sprints and Studios (Sprint 0 kickoff through the release-hardening studio)

Build in sprints aligned with the in-class studio days (see the course schedule for dates), following the sprint studio protocol: stand-ups with numbers, failing tests as specifications, current documents, role rotation at boundaries. **Sprint 1 (see schedule)** integrates members' components into one pipeline running the class language (Direction B: the front end printing ASTs), with an in-class working-time session; if a break falls inside the sprint window, front-load the integration so a working pipeline travels with you. The Sprint 1 increment checkpoint also carries the project's one structured team-health pause: **re-read your charter** ("does it still describe this team?" — file one revision if not) and each member sends the instructor a **confidential peer pulse** — rate yourself and each teammate 1-5 on contributing to the work, interacting with teammates, keeping the team on track, expecting quality, and having relevant knowledge and skills (the CATME dimensions), with a sentence of evidence for any 2 or below. The pulse is read only by the instructor, never mechanically averaged into a grade, and used to calibrate individual contribution and to start a coaching conversation where self- and peer-views diverge. **Sprint 2 (gallery-walk studio)** implements grammar differences and the distinctive feature's skeleton (Direction B: the evaluator emitting timed events); **Sprint 3 (release-hardening studio)** completes the feature, hardens errors, and finishes the sample suite — budget ~4 hours for the ShipIt checks (cold clone-to-run, packaging, README) — they are scored in the Documentation and Reproducibility dimension. The **gallery walk** (Sprint 2 studio day) is mandatory: host with one known failure shown, walk with Strength, Question, and Risk cards, and triage all feedback into fix, disclose, or future work. The **release hardening** studio is your last in-class working session before Demo Day.

---

## Stage 3: Demo Day (the last class meeting)

With all teams presenting in a single class session, each team has a hard cap of **9 minutes**, plus a 1-minute transition to the next team. Within your 9 minutes:

1. The pitch: niche, scorecard, and one design decision defended (60 seconds each).
2. The live demonstration: the REPL, a sample program showcasing the niche, and the distinctive feature **explained and demonstrated by a teammate who did not implement it**. Direction B teams close with the short performance described above — a live edit-and-rerun over the event output.
3. The candid minute: one known limitation, disclosed with its triage rationale.
4. The numbers: the test results table and one bug story with its regression test.

Every teammate speaks. The audience (your classmates) will write one Strength and one Question card per language; responding to your cards is part of the report.

Demo Day is **external-facing**: alumni, industry guests, and faculty from other departments may join the audience and Q&A, as available — your grade never depends on who attends. Prepare with the [Demo Day Guide]({{ site.baseurl }}/Projects/TeamLanguage#demo-day-external-guests-and-technical-interview-practice); the final sprint studios include a cross-team mock-interview rehearsal, credited as class participation.

There is no final exam. Demo Day and the final submission fall on the last class meeting, and **no work is accepted after the last class**.

---

## Stage 4: Final Submission (Demo Day — 75 points, together with the presentation)

**Deliverables:**
1. **The repository**: the integrated implementation, REPL and file-runner, test suite, sample programs with expected outputs, all configuration in JSON, located exception handling throughout, and a readme tested by the teammate who did not write it. Ensure reproducibility by fixing random seeds where applicable and listing software version information. The repository is public and recruiter-legible: run the [ShipIt self-check]({{ site.baseurl }}/Projects/TeamLanguage#shipping-your-language-the-shipit-checklist) before Demo Day — it is scored within the Documentation and Reproducibility dimension. (Direction B: the timed-event test fixtures and, if you used bison, the automaton report ride along here.)
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

---

## The Music and Live-Coding Path

*To show you the music and live-coding path through the course's required assignments — the built-in directions that let you meet the same outcomes on live-coding languages — so that each choice is made with full information.*

### Goals

- Understand that the music and live-coding path runs through the same required assignments as every other path — as directions chosen within them, one assignment at a time
- Know which assignments offer a music direction (Parser, Functional, and the Team Language Project) and what each direction entails
- Know that every music direction supports a text-events-only route, so no audio production or playback is ever required

### Background Reading and References

- [Music Languages and Live Coding Activity](https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374/gh-pages/_pages/Activities/liascript-languagedesign.md)
- [Flex and Yacc Activity](https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374/gh-pages/_pages/Activities/liascript-parsertable.md)

This page is a guide, not a graded assignment. It describes the **music and live-coding path** through the course: the same required assignments everyone completes, taken through the music **directions** built into them. There is no separate set of deliverables and nothing to sign up for — each direction is a choice you make *inside* its assignment, when that assignment is handed out, one at a time.

---

#### How the Music Path Works

Every assignment in this course exercises the same core outcomes: specifying a language formally, building a lexer/parser/evaluator pipeline, reasoning about semantics, and defending design decisions. Several assignments offer more than one **direction** — equivalent ways of meeting those outcomes, with a single deliverable and a single rubric that applies to every direction equally. Languages for live-coded music — TidalCycles, Strudel, and the mini-notation they share — are real, production languages with formal grammars, denotational semantics, and active communities, and they support every outcome the assignments assess. The music directions put those languages under your hands.

In the spirit of Universal Design for Learning, the music path is a deliberate choice of **engagement** (a problem domain that may hold your attention differently than a general-purpose toy language does) and of **expression** (your capstone demonstration can be a short live-coded performance rather than a REPL walkthrough — or a walkthrough of timed event output, if you prefer). It is not the easy path and it is not remedial: it is the same mountain, climbed on the same rubrics, by a route that happens to make rhythm.

**Accessibility note, stated up front:** the music materials are built around a semantics that maps programs to *timed event structures* — lists of `(value, begin, end)` events you can read, print, diff, and test as plain text. Every music direction supports a **text-events-only route**: sound rendering is always optional, and no deliverable requires you to produce, hear, or evaluate audio. If audio is not accessible or not appealing to you, the path is fully available through its textual semantics.

---

#### The Path, Assignment by Assignment

The music path follows the course's own arc — the same required assignments, in the same order, with the music direction chosen where one is offered:

1. **[Music Languages and Live Coding](https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374/gh-pages/_pages/Activities/liascript-languagedesign.md)** (activity) — meet TidalCycles and Strudel as *language designs*: embedded versus external DSLs, a formal model of patterns, and the timed-event semantics the rest of the path builds on.
2. **[Flex and Yacc](https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374/gh-pages/_pages/Activities/liascript-parsertable.md)** (activity) — build a working flex/yacc pipeline for a subset of the mini-notation in class. (Relatedly, the [Lexer assignment]({{ site.baseurl }}/Assignments/Lexer)'s generator-toolchain direction is a natural on-ramp: choosing Flex or PLY there puts the tools of the mini-notation pipeline in your hands early. It pairs well with what follows, but it is not required for it.)
3. **[The Parser and AST]({{ site.baseurl }}/Assignments/Parser) -> the Mini-Notation direction** — grow the in-class mini-notation subset toward the real language: alternation, Euclidean rhythms, and polymeter, parsed into an AST, evaluated to timed events, and validated against the Strudel reference implementation (or against printed event lists alone).
4. **[Functional Programming]({{ site.baseurl }}/Assignments/Functional) -> the Parallel Functional direction** — purity buys parallelism: the same core parts as everyone (pure functions, higher-order combinators, recursive structures with fold), then a complete MapReduce pipeline measured and analyzed against Amdahl's Law — the same pure-map/associative-reduce discipline pattern engines like Strudel run on.
5. **[Team Language Project]({{ site.baseurl }}/Projects/TeamLanguage) -> the Music and Live-Coding direction** (capstone) — design, specify, build, and demonstrate a small live-coding language with your team. The closing demonstration may be a live edit-and-rerun session over printed event output — rendered sound is optional here as everywhere on the path.

Assignments without a music direction listed here (Warmup, Regex, the Automata lab, Lexer, Interpreter, and the rest) are simply taken as they stand — they build the skills every direction draws on. And the choices are independent: you can take the Mini-Notation direction in the Parser assignment and any direction you like in Functional, or vice versa. The path above is the coherent musical route, not a package deal.

---

#### The Mapping at a Glance

| Required assignment | Its music direction |
| --- | --- |
| [The Parser and AST]({{ site.baseurl }}/Assignments/Parser) | Direction B: The Mini-Notation Music Parser |
| [Functional Programming]({{ site.baseurl }}/Assignments/Functional) | Direction E: Parallel Functional Programming |
| [Team Language Project]({{ site.baseurl }}/Projects/TeamLanguage) | The Music and Live-Coding direction (text-events-only route available) |

The two activities (Music Languages and Live Coding; Flex and Yacc) are preparation, not deliverables — they play the same role the optional readings do elsewhere in the schedule.

---

#### When to Decide

There is no track to join and no deadline to declare by: **each direction is chosen when its assignment is handed out**, inside that assignment, and each choice stands alone. If the music path appeals to you, the useful early moves are simply to work through the two activities above before the Parser assignment arrives, and to raise the Music and Live-Coding direction with your team when the Team Language Project kicks off — that one is a team decision, and it benefits from being made at the project's first sprint rather than mid-stream. Questions about any direction are always welcome in office hours; the choosing, though, needs no permission — the directions are built in.


---

## Shipping Your Language: The ShipIt Checklist

*To turn your team's language repository into a public, professional artifact — one a stranger can run, a recruiter can read, and each teammate can point to from a portfolio — so the semester's work exists in the world under your names.*

### Goals

- To publish the team language repository in a state a stranger can clone, install, and run from the README alone
- To write a README that answers what the language is, how to install it, and how to run a first program in thirty seconds, with each member's contribution credited
- To package the language for installation with pip, npm, or Docker, verified by a teammate who did not do the packaging
- To create a personal portfolio entry — the repository pinned or linked from each member's GitHub profile or portfolio page with a short project story suitable for a resume

### Background Reading and References

- [Publishing Your Language — pip, npm, and Docker](https://www.billmongan.com/Ursinus-CS374-Fall2026/Tutorials/PublishingYourLanguage)
- [CI and TDD for Interpreters](https://www.billmongan.com/Ursinus-CS374-Fall2026/Tutorials/CITDDForInterpreters)
- [Team Language Project](https://www.billmongan.com/Ursinus-CS374-Fall2026/Projects/TeamLanguage)

This guide is not separately graded; its checklist is assessed within the Team Language Project's **Documentation and Reproducibility** dimension.

By Demo Day your team will have built something few undergraduates can claim: a working programming language, designed and implemented end to end. This guide — required preparation for the final submission — makes sure that work *exists in the world* in a form that does it justice: a public repository a stranger can run, a README a recruiter can read in thirty seconds, an installation path that works cold, and a portfolio entry under each of your names. The self-check rewards finish, not scope: a small language with a spotless repository, a legible README, and a verified install demonstrates more than an ambitious one nobody else can run. Run the checklist as a team during the release-hardening studio, before Demo Day.

---

#### What Strong Work Looks Like

Strong work has these qualities:

- **A stranger succeeds without you in the room.** The decisive test for every stage of this guide is the cold test: someone who was not on your team — or the teammate who did *not* do the work — follows the public record alone and it works. "Setup was tested by the teammate who did not write it" is already in the project rubric; this guide extends the same discipline to installation and the README.
- **The README opens like an elevator pitch, not a lab report.** The first screen answers three questions: what is this language and what is its niche, how do I install it, and what does a first program look like — with its output shown. Details (the full grammar, the semantics, the extension guides) are linked, not inlined.
- **The repository tells the team's story by itself.** Issues and pull requests show the sprints, the decision log shows the contested calls, and the README's credits section names who built what. A visitor — a grader, a recruiter, a future you — can reconstruct the process without asking anyone.
- **The portfolio entry is specific.** A weak story says "We built a programming language for class." A strong story says: "Our team of three designed and shipped a query language over in-memory lists with a Hindley-Milner type checker. I built the parser and the AST layer, property-tested with Hypothesis, and wrote the differential test harness that caught three semantics bugs before Demo Day."

Weak work has a private repository, a README that assumes the reader attended the class, an install path nobody has tried cold, and no trace of the project anywhere under your own name.

---

#### Stage 1: Repository Hygiene

Make the repository presentable before making it prominent:

- **Make it public**, with a `LICENSE` file (MIT or BSD-3-Clause are fine defaults; agree as a team). Everything in the project rubric assumes a repository a stranger can reach.
- **Audit the history for secrets and personal data.** Search the full history — not just the current tree — for tokens, passwords, and anything personal that does not belong in public. If you find any, rotate the credential and consult the instructor before rewriting history.
- **Pin your dependencies** and state your toolchain versions (Python version, `uv` lock file or `requirements.txt` with versions), exactly as the project's reproducibility requirement demands.
- **Clean the top level.** A visitor should see the README, the license, the source package, the tests, the sample programs, the language reference, and `SEMANTICS.md` — not scratch files, stale experiments, or `old_parser_v2_final.py`.
- **Leave the process visible.** Do not squash away your issues, pull requests, or decision log — they are evidence of the professional practice the rubric credits, and they are what makes the repository more than a code dump.

---

#### Stage 2: The Recruiter-Legible README

Rewrite the README so its first screen passes the thirty-second test:

1. **What it is** — the language name, its niche, and a one-paragraph pitch (your proposal already contains this; compress it).
2. **Install** — the one command that installs it (see Stage 3).
3. **First program** — a small sample program *and its output*, so a reader sees the language run without installing anything.

Then, below the fold:

- A **CI badge** showing the test suite passing on the submission commit (the [CI and TDD for Interpreters]({{ site.baseurl }}/Tutorials/CITDDForInterpreters) tutorial covers wiring this up).
- Links to the **language reference**, **`SEMANTICS.md`**, and the sample program suite.
- A **credits section** naming each teammate and what they built — contribution attribution is part of the self-check, and it is what lets each of you point at this repository individually.

The teammate who did not write the README performs the cold test: fresh clone, follow it top to bottom, note every place they stall.

---

#### Stage 3: Package Your Language

Give your language a real installation path — one of:

- **pip:** package the implementation (a `pyproject.toml` with an entry point so `your-language` runs the REPL and `your-language file.lang` runs a program). Installing directly from the repository (`pip install git+https://...`) is sufficient; publishing to PyPI is stretch work under the Extensions Menu's *Libraries and Packaging* entry.
- **npm:** for JavaScript implementations, a scoped package with a working `bin`.
- **Docker:** a small image whose default command opens the REPL and which can run a mounted program file.

The step-by-step mechanics live in the [Publishing Your Language — pip, npm, and Docker]({{ site.baseurl }}/Tutorials/PublishingYourLanguage) tutorial; this guide only insists on the discipline around it:

- **Tag the release** with a semantic version (`v1.0.0` for the Demo Day submission) so the installed artifact and the graded commit are the same thing.
- **Verify cold.** The teammate who did *not* do the packaging installs it on a machine (or in a fresh container) that has never seen the project, following the README alone, and records a one-line confirmation with their name in the report.
- **Audit before you publish.** Review what the package or image actually contains (a `pip` sdist listing, `npm pack --dry-run`, or the image layer listing) — no test fixtures, no secrets, no personal files.

---

#### Stage 4: The Portfolio Entry

The last stage is individual. Each teammate:

- **Pins or links the repository** from their GitHub profile (or personal portfolio page). If you do not have a profile README, this is the moment to create one — it is a ten-minute job with an outsized payoff.
- **Writes a project story of roughly 200 words**: the problem (what niche, why a new language), what the team built (the pipeline, the distinctive feature, any extensions), and the evidence (the repo link, the CI badge, the verified install, a test-suite number). Name your individual contribution explicitly — "I built X" — because that is the sentence a resume bullet and an interview answer are made from.
- **Reuses the story.** The same story is your opening move with guests at Demo Day (see the [Demo Day Guide]({{ site.baseurl }}/Projects/TeamLanguage#demo-day-external-guests-and-technical-interview-practice)) and the seed of the resume bullet you will write when you next update your materials.
- **Drafts the post.** Each member turns the story into a **drafted LinkedIn-style post** (150-250 words: the niche, what you built, one concrete number — tests passing, sample programs, the install command — and what you learned) and includes the draft in the final submission. Submitting the draft is required; **publishing it is always optional and never graded — your professional profiles are yours.** The draft exists so that if you choose to post, the post is already written while the language still runs on your machine.

---

#### Frequently Asked Questions

**Q: Do we have to publish to PyPI or npm?**
A: No. An installation path that works cold from the public repository (`pip install git+...`, a Dockerfile, or an npm install from the repo) satisfies this guide. A public registry release is stretch work credited through the Extensions Menu's *Libraries and Packaging* entry.

**Q: Our repository has been private all semester. When should we flip it public?**
A: During the release-hardening studio at the latest — after the Stage 1 hygiene audit, before Demo Day. Do the secrets audit *first*: public means the full history is public.

**Q: One teammate doesn't want the repository on their profile. Is that a problem?**
A: The repository-side items (public repo, README credits) are team obligations; the profile pin is personal and the self-check is satisfied by a link from a portfolio page instead. If someone prefers not to be named publicly at all, talk to the instructor — there is always an accommodation, and the credit lives in the graded report regardless.

**Q: Does the ShipIt self-check add points?**
A: No — it is how you earn the points that already exist. The Documentation and Reproducibility dimension of the Team Language Project rubric names this checklist; running it honestly during release hardening is how you arrive at Demo Day already knowing that score.

---

#### Reflection Prompts

Answer these as a team during release hardening, and individually as part of your contribution statement:

- What did the cold test catch that the authors could not see, and why couldn't they see it?
- Read your own 200-word project story as a stranger: what claim in it is best supported by evidence in the repository, and what claim still needs shoring up?
- Do you certify that the repository and your portfolio story accurately represent your team's and your own work? Please identify any and all portions that were not originally created by your team.
- AI disclosure: list any generative-AI tools you used, for what, and how you verified the results (or state 'none').
- Approximately how many hours did this guide's checklist take your team (I will not judge you for this at all...I am simply using it to gauge if the assignments are too easy or hard)?

### Self-Check

| Criterion | Pre-Emerging | Beginning | Progressing | Proficient |
|---|---|---|---|---|
| Self-Check: Repository Hygiene | Our repository is private or cannot be found, has no license, or has credentials or secrets somewhere in its history | Our repository is public with a license, but dependencies are unpinned, the top level is cluttered with scratch files, or our team process (issues, pull requests, decision log) is invisible in the repository | Our repository is public, licensed, and clean at the top level, with pinned dependencies and visible team process, though a minor gap remains such as a stale branch or an untracked configuration step | Our repository is public with a license and a clean, self-explanatory top-level layout; dependencies and versions are pinned; no secrets or personal data appear anywhere in the history; and our issues, pull requests, and decision log make the team's process legible to an outsider |
| Self-Check: README and Language Reference Quality | Our README is missing, or only an author could follow it | Our README describes the language but a stranger could not install and run a first program from it alone, or no teammate is credited | Our README answers what, install, and first program in thirty seconds and links the language reference, with a minor gap such as a missing sample output or an out-of-date badge | Our README answers what the language is, how to install it, and how to run a first program in thirty seconds; shows a sample program with its output; carries a passing CI badge; links the language reference and SEMANTICS.md; and credits each member's contribution by name |
| Self-Check: Packaging and Distribution | The only way to run our language is to reproduce our development environment by hand | A packaging path (pip, npm, or Docker) exists but has not been verified by anyone who did not build it | Our language installs via pip, npm, or Docker following the README, verified cold by the teammate who did not do the packaging, though a minor gap remains such as a missing version tag | Our language installs via pip, npm, or Docker following the README alone; the installation was verified cold by the teammate who did not do the packaging, and their confirmation is recorded; and the release carries a semantic version tag matching the submission |
| Self-Check: Personal Portfolio and GitHub Profile | Nothing links me to this project outside the course | The repository is linked from my profile or portfolio, but with no story — a visitor cannot tell what I did or why it matters | The repository is pinned or linked from my GitHub profile or portfolio page with a short description, though my individual contribution is not yet legible | The repository is pinned or linked from my GitHub profile or portfolio page with a project story of roughly 200 words — the problem, what we built, and the evidence — that names my individual contribution and is ready to reuse on a resume and at Demo Day |


---

## Demo Day: External Guests and Technical Interview Practice

*To prepare you to present your language to people outside the course — invited guests at Demo Day, and eventually interviewers and colleagues — by practicing the plain-language pitch, the known limitation, and the interview-style deep dive on work you actually did.*

### Goals

- To open your project for a non-specialist in ninety seconds — what the language is, why it exists, and what working means — without jargon
- To practice the interview form on your own work - explaining your pipeline, defending a design decision, and telling a real bug story with its fix
- To handle questions honestly, including redirecting a question you cannot answer and disclosing a known limitation without being asked
- To connect the project to what comes next - a portfolio story, a resume conversation, and venues for presenting student work beyond the course

### Background Reading and References

- [Sprint Studio Protocol](https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374/gh-pages/_pages/Activities/liascript-sprintstudio.md)
- [Team Language Project](https://www.billmongan.com/Ursinus-CS374-Fall2026/Projects/TeamLanguage)
- [ShipIt Guide: Repo Hygiene, README, Packaging, and Your Portfolio]({{ site.baseurl }}/Projects/TeamLanguage#shipping-your-language-the-shipit-checklist)

This guide is not separately graded; the presentation is assessed within the Team Language Project's **Demo Day Presentation** dimension, and the mock-interview rehearsal is credited as **class participation**.

Demo Day is not a private class ritual. Alumni, industry guests, and faculty from other departments may be in the room as audience members and Q&A panelists — invited **as available**; your grade never depends on who attends — and the skills the day demands are exactly the ones a technical interview demands: explain a system you built, in plain language first and full depth on request, defend your decisions, and be honest about what does not work. This guide prepares you for both audiences at once. Nothing here is extra work — it is rehearsal for work you already owe.

---

#### Demo Day Format and Schedule

All teams present within a single class session: each team has a hard cap of **9 minutes**, followed by a **1-minute transition** while the next team plugs in. Nine minutes rewards a rehearsed demo — time your run-through, and cut material rather than rushing it. The order of presentation is set by lot: teams draw lots in the release-hardening studio, so you know your slot before the day.

---

#### What Strong Work Looks Like

- **The opener lands with someone who has never heard of a parser.** "We built a small programming language for describing drum patterns. You type a pattern, our system checks it, understands it, and plays it back as timed events. I built the part that turns your text into a structure the computer can walk." Ninety seconds, no jargon, ends with what *working* looks like.
- **Depth is available on demand, not imposed up front.** When a guest asks "how does it actually work?", the answer walks one line of code through the whole pipeline — characters to tokens to tree to value — at whatever level the asker's follow-ups invite.
- **The limitation is volunteered, not extracted.** Strong presenters disclose a known limitation with its triage rationale before anyone asks. It reads as command of the work, because it is.
- **Questions come back.** The best conversations at Demo Day are two-way: ask the guest what they build, what languages their team uses, what they wish new graduates knew.

---

#### The One-Page Brief: Talking to Guests

Have these five moves rehearsed before Demo Day:

1. **The ninety-second opener.** What the language is, the niche it serves, who would use it, and one sentence on what you personally built. Write it, say it aloud, cut every term a non-CS friend would stumble on.
2. **The three-sentence architecture.** The pipeline in plain words: *text comes in; the lexer breaks it into words; the parser builds the sentence structure; the evaluator walks that structure and produces the answer.* Then one sentence on where your distinctive feature lives in that pipeline.
3. **The known limitation.** One known limitation, stated plainly, with why you triaged it as disclose-rather-than-fix. Practice saying it without apologizing.
4. **The redirect.** For questions you cannot answer: "I don't know — my teammate built that part, let me hand you to them," or "I don't know, but here's how I'd find out." Both are strong answers. Bluffing is the only weak one.
5. **The question back.** Prepare two genuine questions to ask a guest — about their work, their team's languages and tools, or their path. Demo Day is a networking event wearing a final-exam costume; treat the conversation as two-way.

---

#### The Mock Technical Interview (Final Sprint Studios)

During the final sprint studio sessions, you will pair **across teams** for interview rounds, credited as class participation:

**Format.** Ten minutes per round, then swap roles. The interviewer asks from the question bank below (or invents better ones); the interviewee answers **without slides** — a whiteboard or paper is allowed, your repository is not. Close each round with a feedback card in the gallery-walk vocabulary: one **Strength**, one **Question** the interviewee should be ready for at Demo Day.

**Question bank** (interviewers: pick three or four, follow the answers, dig where they wobble):

- Walk me through what happens when this one line of your language runs — from characters to final value, naming each stage and what it hands to the next.
- Why an environment chain instead of one big dictionary? What breaks in your language if you flatten it?
- How would you add feature X (the interviewer picks something plausible — a `while` loop, string interpolation, a new operator)? Which pipeline stages does it touch, and which one is the risky edit?
- Tell me about a bug that lived *between* two stages — where the fix wasn't in either component but in the contract between them.
- What design decision would you reverse with one more sprint, and what would reversing it cost now?
- Your parser accepts a program your evaluator crashes on. Whose bug is that, and how do you decide?

**Why cross-team pairs:** explaining your language to someone who has never seen it is the whole game — your own teammates know too much to be useful practice, and interviewing *them* about their language teaches you what good interviewer questions feel like from the inside.

---

#### Taking It Further

The project does not have to end at Demo Day:

- **[CCSC-Eastern](https://ccscne.org/)** and similar regional conferences run **student poster sessions** — a team language with a live REPL demo is exactly the kind of work they exist to showcase. Talk to the instructor about submitting; the proposal you already wrote is most of the abstract.
- **Campus research and creative-work showcases** welcome course projects of this scope; presenting there is a low-stakes rehearsal for any external venue.
- **Your profile.** The [ShipIt guide]({{ site.baseurl }}/Projects/TeamLanguage#shipping-your-language-the-shipit-checklist)'s Stage 4 — the pinned repository and 200-word project story — is the durable version of everything you rehearsed here. Update your resume and LinkedIn while the numbers (test counts, sample programs, the verified install) are fresh.

---

#### Frequently Asked Questions

**Q: Will there definitely be external guests at Demo Day?**
A: Guests are invited as available — some years the room is full, some years it is classmates and faculty. Prepare the same either way: the rubric's multi-audience expectations do not change, and the mock-interview rehearsal happens regardless.

**Q: Does talking to guests affect my grade?**
A: The Demo Day presentation is graded by its existing rubric dimension; guest attendance and guest reactions are never grading conditions. The mock-interview rehearsal is credited as ordinary class participation for the studio session it happens in.

**Q: I get nervous in interview settings. Can I opt out of the mock interview?**
A: Talk to the instructor beforehand — the format can be adjusted (a smaller room, a written walk-through, extra prep time). The rehearsal exists precisely because the tenth time explaining your pipeline is calmer than the first; we want you to spend nervous repetitions here, where they are cheap.

**Q: What should I wear / bring on Demo Day?**
A: Whatever you present comfortably in. Bring a machine with the demo rehearsed and a fallback (a recording or transcript of the REPL session) in case of technical trouble — rehearsed fallbacks are professional practice, not admissions of doubt.

---

#### Reflection Prompts

Answer individually after the mock-interview rehearsal:

- Which question made you realize you understood something less well than you thought, and what did you do about it before Demo Day?
- What did you learn from being the *interviewer* that you could not have learned as the interviewee?
- AI disclosure: list any generative-AI tools you used, for what, and how you verified the results (or state 'none').
- Approximately how many hours did you spend preparing with this guide (I will not judge you for this at all...I am simply using it to gauge if the assignments are too easy or hard)?

### Self-Check

| Criterion | Pre-Emerging | Beginning | Progressing | Proficient |
|---|---|---|---|---|
| Self-Check: Guest-Facing Communication | I cannot explain the project without assuming the listener took this course | I can describe the language, but my opening runs long, leans on jargon, or hides what does not work | I can open the project in about ninety seconds in plain language and disclose a limitation when asked, though my answers to unexpected questions still wobble | I can open the project in ninety seconds in plain language, volunteer one rehearsed limitation with its triage rationale, redirect a question I cannot answer honestly ("I don't know, but here is how I would find out"), and ask a guest a genuine question back |
| Self-Check: Mock Technical Interview | I skipped the rehearsal or could not explain my own component | I explained my component but not how it connects to the rest of the pipeline, or I could not tell a single concrete bug story | I walked my partner through the pipeline token-to-value, defended one design decision, and told one bug story, though I leaned on notes or slides | Without slides, I explained the pipeline end to end, defended a design decision by naming the alternative we rejected and why, told a bug story with its regression test, and asked my partner at least one probing question about their language when roles reversed |
| Self-Check: Portfolio Story | I have no way to show this project to anyone outside the course | I can point at the repository but cannot yet tell its story in a way a recruiter would follow | My 200-word project story exists and names my contribution, though it is not yet linked from anywhere or rehearsed aloud | My project story is written, linked from my profile or portfolio per the ShipIt guide, rehearsed aloud as a two-minute narrative, a drafted (publication-optional) LinkedIn-style post exists, and I can produce the evidence behind every claim in it on request |

