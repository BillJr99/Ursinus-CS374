---
layout: assignment
permalink: /Projects/TeamLanguage
title: "CS374: Principles of Programming Languages - Final Project: A Language of Your Own"

info:
  coursenum: CS374
  purpose: "To design, build, document, and present a programming language of your own, starting from a small working language I give you, and to show that a language can grow one stage at a time."
  tilt:
    task: "In rotating-role team sprints, choose your language's direction, grow the starter language into your own, add a distinctive feature (going deeper via the Extensions Menu if you choose), and ship a REPL, file-runner, samples, tests, and SEMANTICS.md, then present the language at Demo Day."
    criteria: "I assess your work on the proposal, language design and documentation, implementation correctness and integration, testing, reproducibility, and the Demo Day presentation.  You submit the proposal; the rest is earned with the final submission, due on the last class day, and the presentation at Demo Day.  See the course schedule for the dates, and the rubric below for the full breakdown."
  points: 100
  goals:
    - To design a programming language with a niche, a documented grammar, and exhaustive semantics
    - To choose and commit to a direction (a general-purpose or domain language of the team's design, or a music/live-coding language) and defend that choice against the design scorecard
    - To implement the language end to end by extending a provided lexer, parser, AST, and evaluator
    - To implement at least one distinctive feature requiring real design and implementation work
    - To deliver a tested, reproducible implementation with a REPL, file-runner, and sample program suite
    - To present the language at a public Demo Day with a candid account of its limitations
    - To work in sustained team sprints with rotating roles and structured peer review
  rubric:
    - weight: 28
      description: Proposal
      preemerging: The proposal is missing, or names a language with no team roster, niche, grammar, or plan
      beginning: The proposal names the team and a niche, but the design scorecard or the team charter is missing, or the grammar v0, node inventory, or SEMANTICS.md v0 is missing or generic, or the build plan and sprint plan are absent
      progressing: All checklist items are present and specific, with minor gaps such as a scorecard that states priorities without their sacrifices, a charter topic left vague, a vague risk pre-mortem, or an incomplete node inventory
      proficient: Every checklist item is complete and specific; the proposal opens with the three-member team roster, the niche in one sentence, the design scorecard with a priority and a sacrifice for each of readability, writability, reliability, and implementation cost, and the team charter covering all four topics and signed by every member; the chosen direction is declared and defended against the design scorecard; the distinctive feature (and any Extensions Menu adoptions) is scoped to fit the sprint plan; and the proposal is submitted on time
    - weight: 19
      description: Language Design and Documentation
      preemerging: The language has no documented grammar or semantics, or the design is the starter language unchanged
      beginning: A grammar exists but diverges from the implementation, and semantics documentation is generic or incomplete
      progressing: The grammar and SEMANTICS.md are complete and largely match the implementation, with a stated niche and scorecard, and minor gaps
      proficient: The niche, scorecard, EBNF grammar, node inventory, and exhaustive SEMANTICS.md are complete, current, and verified against the implementation, with a decision log recording contested choices and their rationales
    - weight: 19
      description: Implementation Correctness and Integration
      preemerging: The implementation fails to run the sample programs
      beginning: The implementation runs but fails on several sample or test programs due to one or more minor issues
      progressing: The implementation passes its test suite and sample programs, with a fragile area such as error recovery or a semantics corner that diverges from the documentation
      proficient: The pipeline passes a substantive test suite and all sample programs, the distinctive feature works end to end, error messages identify their stage and position, and behavior matches SEMANTICS.md throughout
    - weight: 14
      description: Evaluation and Testing
      preemerging: No systematic testing exists
      beginning: A minimal test suite exists without coverage of the distinctive feature or error cases
      progressing: The test suite covers the core language, the distinctive feature, and error cases, with results tracked across sprints
      proficient: The test suite covers the core language, the distinctive feature, error cases, and programs that check the implementation against SEMANTICS.md, results are tracked across sprints with the failing-test-as-specification discipline visible in the history, and at least three fixed bugs are documented with their regression tests
    - weight: 10
      description: Documentation and Reproducibility
      preemerging: The repository cannot be run by a stranger
      beginning: Setup works but documentation is thin or stale
      progressing: A stranger can run the REPL and samples from the readme, with minor gaps, and the ShipIt self-check was attempted with gaps remaining (e.g., a private repo, a missing license, or no portfolio link)
      proficient: A fresh clone runs the REPL, file-runner, and all samples in under three minutes following the readme, the language reference document teaches the language to a newcomer with examples, dependencies and versions are pinned, and setup was tested by the teammate who did not write it; and the repository passes the ShipIt self-check; public, with a license, a recruiter-legible readme (what, install, first program in thirty seconds) crediting each member's contribution, and either packaged for installation (pip, npm, or Docker) or linked with a project story from each member's portfolio or GitHub profile
    - weight: 10
      description: Demo Day Presentation
      preemerging: The presentation is missing or no demonstration occurs
      beginning: The presentation shows the happy path only, with uneven team participation
      progressing: The presentation includes a live demonstration and acknowledges limitations, with most teammates participating
      proficient: The presentation includes a live REPL demonstration, a sample program that shows off the niche, the distinctive feature explained by its non-author, a rehearsed disclosure of one known limitation, and every teammate presenting
  readings:
    - rtitle: "The Project Language Guide, including the Grammar v0 starter and the feature menu"
      rlink: "Tutorials/ProjectLanguageGuide"
    - rtitle: "Music and Live-Coding Track Guide (for Direction B: deliverable equivalence table and the text-events-only route)"
      rlink: "../Tutorials/MusicLiveCodingPath"
    - rtitle: "Make-a-Lisp (mal): incremental scaffold with a built-in test harness (Direction A option)"
      rlink: "https://github.com/kanaka/mal"
    - rtitle: "A Syntax Highlighter for Your Language with tree-sitter (Extensions Menu)"
      rlink: "../Tutorials/SyntaxHighlighter"
    - rtitle: "ShipIt Guide: Repo Hygiene, README, Packaging, and Your Portfolio (required self-check before Demo Day)"
      rlink: "../Tutorials/ShipIt"
    - rtitle: "Demo Day Guide: External Guests"
      rlink: "../Tutorials/DemoDayGuide"

tags:
  - final-project
  - languages
  - team
  - dsl
  - music

---

# What Your Team Builds

Your team will design, build, document, and present a programming language of your own.  It must be a real language: it has a niche (the kind of problem it exists to solve), a grammar, documented semantics, and a working implementation.  You start from a [small working language]({{ site.baseurl }}/files/starters/teamlanguage/README.md) that already has a lexer, a parser, an AST, and an evaluator, so the project needs nothing from any other assignment.  Your job is to grow it into a language of your own.  You work in a team of three, in sprints with rotating roles, and you finish by presenting the language at a public Demo Day.  You leave with a public repository under your own name, a language reference you wrote, and a project story you can tell in an interview.

---

## Milestone Timeline

The project is worth **100 points**, earned at two graded milestones: the proposal (28 points) and the Demo Day Presentations deliverable (72 points), which you submit on the last class day and present at Demo Day.  Your peer review and release work goes in with the final submission.  See the course schedule for the assigned and due dates; it is the source of truth for every date below.

| Milestone (see the course schedule for dates) | What is due | Points |
|---|---|---|
| Project hand-out | Nothing is submitted.  The design phase opens: form a team of three, pick a niche, start the design scorecard and the team charter | - |
| **Proposal** | **The proposal, opening with the team roster, the niche, the design scorecard, and the signed team charter** | **28** |
| **Demo Day Presentations: submitted on the last class day, then presented at Demo Day (final exam period)** | **The final submission, due on the last class day, including your peer review cards and triage and the ShipIt Release Checklist, and the presentation at Demo Day** | **72** |

Demo Day takes place in the course's final exam period, which the course schedule lists.  The final submission is due earlier, on the last class day.  There is no written final exam; Demo Day is the course's terminal event, and I accept no work after it.

---

## Required Scope

Your language must include all of the following:

- Variables with documented scoping.
- Arithmetic with full precedence and associativity.
- Booleans, comparisons, and short-circuit logic.
- Selection and iteration.
- Strings or another non-numeric type.
- At least one **distinctive feature** that requires substantial design and implementation work: functions with closures, a desugared construct, pattern slices, or a domain-specific statement that serves your niche.

It ships with a REPL, a file-runner, at least five sample programs (one that shows off the niche), a test suite, a language reference document, and `SEMANTICS.md`.  Direction B teams satisfy this scope through the equivalences in Choose Your Direction below.

---

## How Your Team Works

Teams are three members each, formed in the design phase from your standing POGIL groups.  The project uses four roles: Coordinator (sprint planning and scope), Builder (implementation), Evaluator (testing and sample programs), and Scribe (documentation and the decision log).  Roles rotate at every sprint boundary so that every member holds every role.  Your report's contribution statements must show the rotation.

**Your team over the project's six weeks.**  Teams reliably pass through recognizable stages (Tuckman, 1965; the fifth stage, *adjourning*, was added by Tuckman and Jensen, 1977), and I placed this project's milestones on that map on purpose:

- *Forming* is the team charter, drafted in the design phase and signed in the proposal.  You do it before the stakes get high.
- *Storming* is the design phase.  The argument over which niche to serve and what the design scorecard says is productive conflict, so have it out loud in your own team meeting instead of quietly in a group chat.
- *Norming* is the proposal: a signed agreement about what you are building and who owns what.
- *Performing* is the sprints, where role rotation and stand-ups carry the load and the team self-corrects without drama.
- *Adjourning* is Demo Day's retrospective.  Close deliberately, with contribution statements and the portfolio story each member takes away.

If the design phase feels contentious, the map is working.  Run the charter's conflict-repair process and keep going.

**Where you start.**  Most teams should start from the [small working language]({{ site.baseurl }}/files/starters/teamlanguage/README.md).  You may use your own code or a teammate's instead, as long as the project README says which.  I grade the language you design and build on top, and I do not care where you started.  Spend your sprint time on the design and the distinctive feature.

---

## Before You Start

You need:

- The [small working language]({{ site.baseurl }}/files/starters/teamlanguage/README.md): a lexer, parser, AST, evaluator, REPL, and test that run as they are.
- Python 3.10 or newer.  The pipeline can use the standard library only, so there need be nothing to install for it.
- A shared git repository for the team.  It may stay private until release hardening; it must be public by Demo Day.
- A working terminal.  If the shell is still new to you, read the [dev environment page]({{ site.baseurl }}/Tutorials/DevEnvironment) and the [shell primer for language development]({{ site.baseurl }}/Tutorials/ShellForLanguageDev) once before Sprint 1.
- The [Project Language Guide]({{ site.baseurl }}/Tutorials/ProjectLanguageGuide), a complete worked path through this project, which the schedule lists as reading.

Confirm your Python version before the first team meeting:

```bash
python3 --version
```

```text
Python 3.11.2
```

Any version 3.10 or newer is fine.  If the command is not found, follow the dev environment page before continuing.

> **Time budget.**  The project runs about six weeks from the hand-out to Demo Day.  The project has no in-class studio sessions, so budget one team meeting of your own early in the design phase, well before the proposal is due.  Budget about 4 hours in Sprint 3 for the ShipIt checks (cold clone-to-run, packaging, README).

---

## Choose Your Direction

Every team declares one of two directions in its proposal.  Both are the same project (the same milestones, the same rubric, the same deliverables discipline), pointed at different niches.

| Direction | What you build | Pick this if |
|---|---|---|
| **A: General-purpose or domain language** | A language with a niche of your choosing, the required scope end to end, and a distinctive feature that serves the niche | Your team has an idea for a problem a small language would make easier to state |
| **B: Music / live-coding language** | A small live-coding language whose programs denote timed event structures over cycle time, in the tradition of the mini-notation you studied | Your team wants the capstone to make rhythm, or at least timed events; audio is never required |

The rubric is the same on both directions.

### Direction A: A General-Purpose or Domain Language of Your Design

This is the default framing above.  Design a language with a niche of your choosing (a recipe domain-specific language (DSL), a query language over in-memory lists, a turtle-graphics language, a logic language, a constraint language, or a compelling original idea), grow the starter into the required scope end to end, and add a distinctive feature that serves the niche.  Everything in the milestone sections below applies as written.

> **Code path.**  Scaffold option: Make-a-Lisp (mal).  If your team's niche is a Lisp-shaped or expression-oriented language, you may build on the [Make-a-Lisp (mal)](https://github.com/kanaka/mal) process as your scaffold instead of starting the front end from scratch.  mal is an eleven-step incremental path to a working Lisp.  What makes it useful here is its shared test harness (`runtest.py` against per-step `.mal` test files), which becomes a free, rigorous regression suite for your language as you build.  You still own the design.  You must give the language a niche of its own and a distinctive feature of your own (mal out of the box is a generic Lisp, which is not by itself a distinctive feature), document your semantics, and integrate your team's components.  mal's staged tests and reference structure can carry the routine reader/eval/print plumbing, so your sprint time goes to the parts that make your language *yours*.  Cite mal in your proposal if you adopt it, and note which steps you used.

### Direction B: A Music / Live-Coding Language

Design a small live-coding language of your own: a language whose programs denote timed event structures over cycle time, in the tradition of the mini-notation you studied.  Past directions that have worked well include a drum-machine language of named, layered tracks with mutation operators; a melodic language with scales, degrees, and transposition as first-class constructs; a language of rhythmic transformations (rotate, invert, thin) applied to seed patterns; and a language for spatial or lighting cues synchronized to cycles, which shows that cycle semantics generalizes beyond audio.

Direction B maps onto the same milestones:

- **Proposal:** your design document also includes a denotational semantics (one displayed equation per construct, mapping programs to event sets over cycle spans), at least one algebraic law your language satisfies, stated as an equation, and a design rationale argued against the embedded-versus-external tradeoff axes, with at least two rejected alternatives.  These stand in for (or fold into) `SEMANTICS.md` v0.
- **Sprint 1:** the lexical and syntactic front end, built either from the starter language or with flex/bison (the [mini-notation starter]({{ site.baseurl }}/files/examples/mininote/README.md) is a good seed).  If you use bison, keep the grammar conflict-free and include the `-v` automaton report in your repository.  The front end parses every specification example and prints ASTs with location-prefixed errors.
- **Sprint 2:** the evaluator, by structural recursion over the AST, one case per semantic equation, each case commented with the equation it implements, emitting a timed event list.
- **Sprint 3:** hardening, the specification-driven test suite, and performance rehearsal.  In the test suite, every semantic equation has at least one test against a hand-computed event list, the algebraic law is verified empirically on at least three instances, and stochastic constructs are reproducible under a fixed seed.
- **Demo Day:** your live demonstration closes with a short performance: live-editing and re-running a program while the class follows the event output as it changes.  **Emitting events as text is sufficient; audio hardware is never required.**  Ambitious teams may also render sound by translating event lists into Strudel or MIDI.  That translation layer (mapping your semantics onto someone else's) is itself worth a section of your report.

The required scope maps naturally.  Patterns and tracks are your non-numeric type, cycle arithmetic and transformation operators are your arithmetic and precedence story, conditional and repeated structures are your selection and iteration, and the cycle semantics itself is a distinctive feature by construction.  The Music and Live-Coding guide at [Tutorials/MusicLiveCodingPath]({{ site.baseurl }}/Tutorials/MusicLiveCodingPath) provides the full equivalence table mapping each deliverable to its classic counterpart, plus the text-events-only route through the whole track.

---

## Extensions Menu

The distinctive feature is required, and the [Extensions Menu]({{ site.baseurl }}/Tutorials/LanguageExtensions) is where teams go deeper.  It describes each extension your team can adopt: static type inference, transpilation, a bytecode compiler and stack VM, pattern matching, garbage collection, concurrency, macros, a foreign function interface, libraries and packaging, scripting targets, editor support, continuations, a lambda-calculus core, logic programming, and an upstream open-source contribution.

---

## Milestone 1: Project Hand-Out (the design phase opens)

The hand-out opens a design phase that runs outside class.  There is no class session for it, so the work happens in a team meeting you schedule yourselves.  Nothing is submitted at the hand-out; the point of this milestone is to leave it with a team, a meeting, and a shortlist.

> **Do this.**
> 1. Form a team of three from your standing POGIL groups.
> 2. Put a team meeting on the calendar, early in the design phase.  Pick one external communication channel (Discord, text, or email) and use it from now on.
> 3. Read the Niche and the Design Scorecard below before the meeting.
> 4. At the meeting, argue the niche out loud.  Read Choose Your Direction above and lean toward A or B; a team direction is easier to settle now than mid-sprint.
> 5. Start the design scorecard: readability, writability, reliability, and implementation cost, with what you prioritize and what you sacrifice.
> 6. Create the team's shared repository.  It can stay private for now.

> **Why this matters.**  This is Tuckman's *storming*.  The argument over which niche to serve is productive conflict.  Have it now, in person, while nothing is graded yet.

### The Niche and the Design Scorecard

Your language needs a reason to exist beyond the assignment.  The strongest student languages pick a *niche* and let it drive every decision.  A niche is the specific group of users and the specific kind of program your language exists to serve: dice-game scripting, turtle-style drawing, survey logic, recipe scaling, music patterns, or grading rules.  The niche supplies your example programs, your Demo Day story, and the tiebreaker for every design argument ("which choice serves dice players?").

The **design scorecard** rates your language on four criteria.  For each one, write what you prioritize and what you give up to get it:

- **Readability:** can a reader who did not write the code follow it quickly?
- **Writability:** can an author produce correct code quickly?
- **Reliability:** how well does the language keep a program from doing the wrong thing without anyone noticing?
- **Implementation cost:** how much will it take to build?  This is your scarcest resource.

The [Project Language Guide]({{ site.baseurl }}/Tutorials/ProjectLanguageGuide) has a Grammar v0 builder and a menu of features, with models you can run, for when you get to the proposal.

**Deliverables checklist (nothing is uploaded at this milestone; carry these into the proposal, Milestone 2):**

- [ ] A team of three, with one communication channel chosen.
- [ ] A team meeting scheduled early in the design phase.
- [ ] A niche shortlist and a working lean toward Direction A or B.
- [ ] A first pass at the design scorecard.
- [ ] A shared repository with all three members as collaborators.

---

## Milestone 2: The Proposal (28 points)

Submit the proposal through Canvas by its due date.  It is two to three pages, and it is the only graded deliverable before Demo Day, so treat it as the contract your team builds against.  It opens with the team: your roster, your niche, the design scorecard, and the signed team charter.  The rest is the plan.  The rubric's proficient level asks for every checklist item complete and specific, the chosen direction declared and defended against the design scorecard, the distinctive feature (and any Extensions Menu adoptions) scoped to fit the sprint plan, and the proposal submitted on time.

> **Do this.**
> 1. Open with the team: list the three members.
> 2. Settle the niche and write it in one sentence: the kind of problem the language exists to solve.
> 3. Finish the design scorecard.  For each of readability, writability, reliability, and implementation cost, state its priority and what you give up to get it.
> 4. Write the team charter (all four topics below), and have every member sign it.
> 5. Write the pitch: the language name, three sentences, and your direction (A or B).
> 6. Write grammar v0 in EBNF, starting from the starter language's grammar at the top of its `parser.py` and marking every difference.
> 7. Build the node inventory table: every node your language will have, its fields, the rule that produces it, the rule that consumes it.
> 8. Start `SEMANTICS.md` v0: one short section per rule of your language (truthiness, scope, types, division by zero), each with a small program and what it prints.  Then add the niche feature's semantics.  Direction B: the denotational equations, the algebraic law, and the embedded/external rationale go here.
> 9. Specify the distinctive feature: its syntax, its semantics, and which pipeline stages it touches (lexer, parser, AST, environment, evaluator).  Scope any Extensions Menu adoptions against the sprint plan; one that ships beats two that do not.
> 10. Write the build plan: which feature each sprint adds, and which stages each one touches.
> 11. Run the risk pre-mortem: name the most likely derailment and the smallest experiment that retires it.
> 12. Write the sprint plan with the role rotation schedule, and check that it matches the charter's rotation plan.
> 13. Submit the proposal through Canvas by its due date.

### The Team Charter

Your team writes a one-page charter it will actually use.  The signed charter is one of the proposal's first sections.  All four topics are required.

**Role rotation plan.**  The project uses four roles: Coordinator (sprint planning, scope), Builder (implementation), Evaluator (testing and sample programs), and Scribe (documentation and decision log).  State how your team will rotate them, for example: "we will rotate by sprint, in alphabetical order by last name."  Every member must hold every role at least once.

**External communication channel and norms.**  State where the team will communicate outside class (Discord, text, email; pick one channel and use it consistently).  State your response-time norm, for example: "we will respond within 24 hours on weekdays, 48 on weekends."  State how you will signal availability changes (illness, travel, exam crunch).

**Preparation norms.**  State what "prepared for class" means for your team, for example: "readings and previous activity reviewed before class; laptop charged; roles assigned by the start of class."  State what you will do if a member is unprepared.

**Disagreement resolution.**  State a concrete mechanism for resolving technical disagreements (for example, "we will vote; ties go to the Coordinator") and interpersonal disagreements (for example, "we will raise the issue with the Scribe, who records it in the decision log; unresolved issues go to the instructor").  Having this written before a disagreement occurs is the point.

All members sign the charter (typed names suffice) in the proposal.  One charter per team.  During Sprint 1, re-read it as a team and file a revision if it no longer describes your team.

**Deliverables checklist (two to three pages, one Canvas submission per team):**

- [ ] Team roster (three members).
- [ ] The niche, in one sentence.
- [ ] The language name and three-sentence pitch, with your **direction (A or B)** declared.
- [ ] The design scorecard: readability, writability, reliability, and implementation cost, with priorities and sacrifices stated.
- [ ] Grammar v0 in EBNF, with differences from the starter language marked.
- [ ] The node inventory table: every AST node, fields, producing rule, consuming rule.
- [ ] `SEMANTICS.md` v0 with one section per rule and the niche feature's semantics (Direction B: the denotational equations, algebraic law, and embedded/external rationale described above).
- [ ] The distinctive feature specification: syntax, semantics, and the pipeline stages it touches, plus any **Extensions Menu** adoptions, scoped to the sprint plan.
- [ ] The build plan: which feature each sprint adds, and which stages it touches.
- [ ] The risk pre-mortem: the most likely derailment and the smallest experiment that retires it.
- [ ] The sprint plan with role rotation schedule.
- [ ] The **signed team charter**: role rotation, communication channel and norms, preparation norms, and disagreement resolution, with every member's typed signature.
- [ ] If you adopt mal as a scaffold: a citation and the list of steps you used.

---

## Milestone 3: Sprint 1: Get It Running and Grow the Core

Sprint 1 is the build phase.  You get the starter running in your repository and start growing it toward the required scope (Direction B: the front end printing ASTs).  Build in sprints, with stand-ups that report numbers, failing tests as specifications, current documents, and role rotation at boundaries.

> **Do this.**
> 1. Copy the starter into your team's repository, and run its test before you change anything.  One layout that works is shown below.
> 2. Add the required scope one feature at a time, in the order your build plan states.  For each feature, write a failing test, and then touch the lexer, the parser, the AST, and the evaluator in that order.
> 3. Keep the REPL and the file-runner working from the top of the repository, with the commands below.
> 4. Write the first failing test for the distinctive feature.  A failing test is your specification; it tells the next sprint what to build.
> 5. Re-read the charter as a team and ask "does it still describe this team?"  File one revision if not.

One repository layout that works:

```text
yourlang/
  README.md
  LICENSE
  SEMANTICS.md
  docs/reference.md      # the language reference
  src/                   # lexer, parser, ast, environment, evaluator
  repl.py                # REPL and file-runner
  samples/               # at least five programs with expected outputs
  tests/
  config/                # every configuration file, in JSON
```

Running your own pipeline from the top of the repository:

```bash
python3 repl.py                        # opens the REPL
python3 repl.py samples/hello.lang     # runs one program
python3 -m pytest tests/               # runs the test suite
```

> **You should see.**  The REPL prompt, then a value echoed back for an expression you type; the file-runner printing the sample program's output; and the test suite reporting how many tests passed, with the distinctive-feature test failing on purpose.

> **If it fails.**
> - An import error after moving files usually means the starter's flat imports (`from lexer import ...`) no longer match the layout.  Fix the imports, or keep the starter's files together in one folder.
> - A program that lexes and parses but crashes in the evaluator is a stage-boundary bug.  Write it down; it is a bug story for Demo Day.

**Checklist (nothing is uploaded):**

- [ ] The pipeline running in your repository, with at least one feature added beyond the starter (Direction B: the front end parsing every specification example and printing ASTs with location-prefixed errors).
- [ ] The README line naming what you started from.
- [ ] A failing test for the distinctive feature, committed.
- [ ] The charter re-read, with a revision filed if it no longer describes the team.
- [ ] Roles rotated for Sprint 2, recorded in the decision log.

---

## Milestone 4: Release and Review

Sprints 2 and 3 happen outside class, in your team's own meetings.  Their work goes in with your final submission, due on the last class day: your peer review cards and their triage, and the ShipIt Release Checklist.

### Sprint 2: Peer Review

Sprint 2 implements the grammar differences and the distinctive feature's skeleton (Direction B: the evaluator emitting timed events, by structural recursion, one case per semantic equation, each commented with the equation it implements).  Trading a review with another team is required, because it is how you find out what your README and your demo actually do for someone who did not build them.

> **Do this.**
> 1. Implement every grammar difference you marked in grammar v0, and update `SEMANTICS.md` as you go so the documents stay current.
> 2. Build the distinctive feature's skeleton so the failing test from Sprint 1 either passes or fails for a more interesting reason.
> 3. Pair with another team, and trade repositories.  Show one known failure in your README, because a demo that hides its failures gets no useful cards.
> 4. Run the other team's language from its README, and leave one card with three fields.  **Strength:** one specific thing that works, precisely named.  **Question:** one real question it raised, ideally about a seam or a semantics decision.  **Risk:** the one thing most likely to fail on Demo Day, stated kindly and concretely.
> 5. Triage every card you received into one of three buckets: fix before Demo Day, disclose at Demo Day, or future work.  The Scribe records the triage in the decision log.
> 6. Rotate roles for Sprint 3.

> **Checkpoint.**  Your disclose bucket becomes, verbatim, the limitations section of your report and the candid minute of your presentation.  Do not clean it up later.

### Sprint 3: Release Hardening and the ShipIt Checklist

Sprint 3 completes the feature, hardens errors, and finishes the sample suite.  Release hardening starts right after you triage your peer review.  Budget about 4 hours for the ShipIt checks (cold clone-to-run, packaging, README); they are scored in the Documentation and Reproducibility dimension.

> **Do this.**
> 1. Finish the distinctive feature so it works end to end, and make every error message identify its stage and position.
> 2. Finish the sample suite: at least five programs, one that shows off the niche, each with its expected output.
> 3. Finish the test suite: the core language, the distinctive feature, error cases, and programs that check the implementation against `SEMANTICS.md`.  Direction B: every semantic equation has at least one test against a hand-computed event list, the algebraic law is verified on at least three instances, and stochastic constructs reproduce under a fixed seed.
> 4. Document at least three fixed bugs with their regression tests.
> 5. Run the [ShipIt self-check]({{ site.baseurl }}/Tutorials/ShipIt) as a team: the secrets audit, the public flip with a license, pinned dependencies, the recruiter-legible README, the packaging path verified cold by the teammate who did not build it, and each member's portfolio entry.
> 6. Draw lots for the Demo Day presentation order.
> 7. Rehearse the 9-minute demo with a timer, and prepare a fallback (a recording or transcript of the REPL session).

> **Watch out.**  Flip the repository public only after the secrets audit.  Public means the full history is public.

**Deliverables checklist (part of the final submission, due on the last class day):**

- [ ] Grammar differences implemented and reflected in `SEMANTICS.md`.
- [ ] The distinctive feature's skeleton running end to end on at least one program (Direction B: the evaluator emitting a timed event list).
- [ ] A peer review traded with another team, with one known failure shown.
- [ ] A Strength, Question, and Risk card left for the other team.
- [ ] Every card you received triaged into fix, disclose, or future work, recorded in the decision log.
- [ ] Roles rotated for Sprint 3.
- [ ] The distinctive feature complete, with stage-and-position error messages throughout.
- [ ] At least five sample programs with expected outputs, one showing off the niche.
- [ ] The test suite covering the core language, the distinctive feature, error cases, and programs that check `SEMANTICS.md`, with results tracked across sprints.
- [ ] At least three fixed bugs documented with regression tests.
- [ ] The ShipIt self-check run: public repository, license, secrets audit, pinned dependencies, README, packaging verified cold, portfolio entries.
- [ ] Presentation order drawn, and the demo rehearsed with a fallback ready.

---

## Milestone 5: Demo Day and Final Submission (72 points)

All teams present during the final exam period.  The final submission is due before that, on the last class day.  There is no written final exam, and I accept no work after Demo Day.  Demo Day is external-facing: alumni, industry guests, and faculty from other departments may join the audience and Q&A, as available.  Your grade never depends on who attends.  Prepare with the [Demo Day Guide]({{ site.baseurl }}/Tutorials/DemoDayGuide).

### The Presentation (9 minutes)

Each team has a hard cap of **9 minutes**, plus a 1-minute transition to the next team.  Within your 9 minutes:

1. **The pitch:** niche, scorecard, and one design decision defended (60 seconds each).
2. **The live demonstration:** the REPL, a sample program that shows off the niche, and the distinctive feature explained and demonstrated by a teammate who did not implement it.  Direction B teams close with the short performance described above: a live edit-and-rerun over the event output.
3. **The candid minute:** one known limitation, disclosed with its triage rationale.
4. **The numbers:** the test results table and one bug story with its regression test.

Every teammate speaks.  You answer the audience's questions, from classmates and guests alike, live at the end of your demo.

> **Do this.**
> 1. Assign each of the four segments to a speaker so that every teammate speaks, and make sure the distinctive feature's presenter is not its author.
> 2. Time a full run-through.  Cut material rather than rushing it.
> 3. Bring a machine with the demo rehearsed and the fallback ready.
> 4. Prepare to answer the audience's questions live at the end of your demo.

### The Final Submission

Submit these four deliverables on the last class day, before you present:

1. **The repository:** the implementation, REPL and file-runner, test suite, sample programs with expected outputs, all configuration in JSON, located exception handling throughout, and a readme tested by the teammate who did not write it.  Ensure reproducibility by fixing random seeds where applicable and listing software version information.  The repository is public and recruiter-legible: run the [ShipIt self-check]({{ site.baseurl }}/Tutorials/ShipIt) before Demo Day; it is scored within the Documentation and Reproducibility dimension.  (Direction B: the timed-event test fixtures and, if you used bison, the automaton report ride along here.)
2. **The language reference** (approximately four pages): teach your language to a newcomer with examples for every construct, the full grammar, the distinctive feature's guide, and a section per adopted extension.
3. **`SEMANTICS.md`,** final and verified against the implementation by your semantics programs (Direction B: the semantic equations, revised to match the implemented language, with a change log from the proposal).
4. **The report** (approximately four pages): the design story with the decision log's three most contested calls, the build experience (which features came easily, which did not, and why), the evaluation summary, limitations (your disclose bucket, verbatim), responses to the Strength, Question, and Risk cards from your peer review, and individual contribution statements covering the rotation.  (Direction B: include the performance postmortem, what performing revealed that the test suite could not, and, if you rendered audio, the translation-layer section.)

**Deliverables checklist:**

- [ ] The presentation delivered within 9 minutes, with every teammate speaking and the distinctive feature explained by its non-author.
- [ ] The public repository: implementation, REPL, file-runner, tests, samples with expected outputs, JSON configuration, located exception handling, pinned versions and fixed seeds, and a readme tested by the teammate who did not write it (Direction B: timed-event fixtures and any bison automaton report).
- [ ] The language reference (about four pages).
- [ ] `SEMANTICS.md`, final and verified by your semantics programs (Direction B: revised equations with a change log).
- [ ] The report (about four pages), including responses to your peer review cards and each member's contribution statement.
- [ ] Each member's answers to the Reflection Prompts, inside their contribution statement.
- [ ] Each member's drafted LinkedIn-style post from the ShipIt guide (submitting the draft is required; publishing it is optional).

A note on what the rubric is looking for.  It rewards a finished minimal language over an ambitious unfinished one.  The required feature list at proficient IS the target; extensions distinguish work beyond proficient.

---

## Reflection Prompts

Answer individually in your contribution statement:

- Which stage of the pipeline was easiest to extend, and what property made it easy?
- Which design decision would you reverse if you had one more sprint, and what would it cost now versus what it would have cost at the proposal?

---

## Companion Guides

- [The Music and Live-Coding Path]({{ site.baseurl }}/Tutorials/MusicLiveCodingPath): how Direction B fits the course.
- [The ShipIt Checklist]({{ site.baseurl }}/Tutorials/ShipIt): repository hygiene, the README, packaging, and your portfolio entry.  Run its self-check before Demo Day.
- [Demo Day: External Guests]({{ site.baseurl }}/Tutorials/DemoDayGuide): the format, the one-page brief, and how to talk to guests.
