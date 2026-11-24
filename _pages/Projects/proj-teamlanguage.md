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
    - To choose and commit to a direction (a general-purpose or domain language of the team's design, a music/live-coding language, or an extension of the provided Interpreter) and defend that choice against the design scorecard
    - To implement the language end to end by extending a provided lexer, parser, AST, and evaluator
    - To implement at least one distinctive feature requiring real design and implementation work
    - To deliver a tested, reproducible implementation with a REPL, file-runner, and sample program suite
    - To present the language at a public Demo Day with a candid account of its limitations
    - To work in sustained team sprints with rotating roles and structured peer review
  rubric:
    - weight: 28
      description: Proposal
      preemerging: The proposal is missing or gives neither a team roster nor a plan
      beginning: The proposal names the team and an idea, but leaves out the direction, the distinctive feature, or the team's plan for sharing and checking the work
      progressing: The proposal names the team, states the niche and direction, and gives a workable plan, but leaves a responsibility or a check for success unclear
      proficient: The proposal names all three teammates, explains the niche and why the chosen direction fits, and gives a realistic plan for building and testing one distinctive feature, including who will start each major task and how the team will tell whether the feature works
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

Your team will design, build, document, and present a programming language of your own.  It must be a real language: it has a niche (the kind of problem it exists to solve), a grammar, documented semantics, and a working implementation.  You can start from a [small working language]({{ site.baseurl }}/files/starters/teamlanguage/README.md) that already has a lexer, a parser, an AST, and an evaluator, so the project needs nothing from any other assignment.  The Where you start section below lists other routes.  Your job is to grow it into a language of your own.  You work in a team of three, in sprints with rotating roles, and you finish by presenting the language at a public Demo Day.  You leave with a public repository under your own name, a language reference you wrote, and a project story you can tell in an interview.

---

## Milestone Timeline

The project is worth **100 points**, earned at two graded milestones: the proposal (28 points) and the Demo Day Presentations deliverable (72 points), which you submit on the last class day and present at Demo Day.  Your peer review and release work goes in with the final submission.  See the course schedule for the assigned and due dates; it is the source of truth for every date below.

| Milestone (see the course schedule for dates) | What is due | Points |
|---|---|---|
| Project hand-out | Nothing is submitted. Form a team of three and discuss possible niches. | - |
| **Proposal** | **One plan per team: name your partners, describe what you will build, and say how you will divide and check the work. No prototype.** | **28** |
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

- *Forming* is finding your partners and agreeing on how to meet.
- *Storming* is discussing which niche to serve and what your team can realistically build.
- *Norming* is settling on a plan in the proposal, then writing your team charter at the start of Sprint 1.
- *Performing* is the sprints, where role rotation and stand-ups carry the load and the team self-corrects without drama.
- *Adjourning* is Demo Day's retrospective.  Close deliberately, with contribution statements and the portfolio story each member takes away.

If the design phase feels contentious, the map is working.  Run the charter's conflict-repair process and keep going.

**Where you start.**  Most teams should start from the [small working language]({{ site.baseurl }}/files/starters/teamlanguage/README.md).  You may instead choose Direction C, [Extend the Interpreter]({{ site.baseurl }}/Projects/TeamLanguage#direction-c-extend-the-interpreter), as your final project, or use the Make-a-Lisp option under Direction A.  You may use your own code or a teammate's instead, as long as the project README says which.  I grade the language you design and build on top, and I do not care where you started.  Spend your sprint time on the design and the distinctive feature.

---

## Before You Start

For Sprint 1, you need:

- A starting codebase: the [small working language]({{ site.baseurl }}/files/starters/teamlanguage/README.md), or the Make-a-Lisp scaffold for Direction A or the Interpreter for Direction C.
- Python 3.10 or newer for the small working language.  That pipeline can use the standard library only, so there need be nothing to install for it.  If you choose another route, follow its setup instructions.
- A shared git repository for the team.  It may stay private until release hardening; it must be public by Demo Day.
- A working terminal.  If the shell is still new to you, read the [dev environment page]({{ site.baseurl }}/Tutorials/DevEnvironment) and the [shell primer for language development]({{ site.baseurl }}/Tutorials/ShellForLanguageDev) once before Sprint 1.
- The [Project Language Guide]({{ site.baseurl }}/Tutorials/ProjectLanguageGuide), a complete worked path through this project, which the schedule lists as reading.

When you start building in Sprint 1, confirm your Python version if you are using the small working language:

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

Every team declares one of three directions in its proposal.  All three are choices for the same final project, with the same milestones, proposal, Demo Day, rubric, and deliverables discipline.

| Direction | What you build | Pick this if |
|---|---|---|
| **A: General-purpose or domain language** | A language with a niche of your choosing, the required scope end to end, and a distinctive feature that serves the niche | Your team has an idea for a problem a small language would make easier to state |
| **B: Music / live-coding language** | A small live-coding language whose programs denote timed event structures over cycle time, in the tradition of the mini-notation you studied | Your team wants the capstone to make rhythm, or at least timed events; audio is never required |
| **C: Extend the Interpreter** | A language your team develops by extending the provided small Scheme in Flex, Bison, and C | Your team wants to make the Interpreter its final project and extend its syntax and evaluator for a chosen niche |

The rubric is the same on both directions.

### Direction A: A General-Purpose or Domain Language of Your Design

This is the default framing above.  Design a language with a niche of your choosing (a recipe domain-specific language (DSL), a query language over in-memory lists, a turtle-graphics language, a logic language, a constraint language, or a compelling original idea), grow the starter into the required scope end to end, and add a distinctive feature that serves the niche.  Everything in the milestone sections below applies as written.

> **Code path.**  Scaffold option: Make-a-Lisp (mal).  If your team's niche is a Lisp-shaped or expression-oriented language, you may build on the [Make-a-Lisp (mal)](https://github.com/kanaka/mal) process as your scaffold instead of starting the front end from scratch.  mal is an eleven-step incremental path to a working Lisp.  What makes it useful here is its shared test harness (`runtest.py` against per-step `.mal` test files), which becomes a free, rigorous regression suite for your language as you build.  You still own the design.  You must give the language a niche of its own and a distinctive feature of your own (mal out of the box is a generic Lisp, which is not by itself a distinctive feature), document your semantics, and integrate your team's components.  mal's staged tests and reference structure can carry the routine reader/eval/print plumbing, so your sprint time goes to the parts that make your language *yours*.  If you adopt mal, cite it and list the steps you used in your final README.

### Direction B: A Music / Live-Coding Language

Design a small live-coding language of your own: a language whose programs denote timed event structures over cycle time, in the tradition of the mini-notation you studied.  Past directions that have worked well include a drum-machine language of named, layered tracks with mutation operators; a melodic language with scales, degrees, and transposition as first-class constructs; a language of rhythmic transformations (rotate, invert, thin) applied to seed patterns; and a language for spatial or lighting cues synchronized to cycles, which shows that cycle semantics generalizes beyond audio.

Direction B maps onto the same milestones:

- **Proposal:** name the music or live-coding niche and describe the timed-event feature you plan to build. The formal equations, algebraic law, and design rationale belong to the build and final submission.
- **Sprint 1:** the lexical and syntactic front end, built either from the starter language or with flex/bison (the [mini-notation starter]({{ site.baseurl }}/files/examples/mininote/README.md) is a good seed).  If you use bison, keep the grammar conflict-free and include the `-v` automaton report in your repository.  The front end parses every specification example and prints ASTs with location-prefixed errors.
- **Sprint 2:** the evaluator, by structural recursion over the AST, one case per semantic equation, each case commented with the equation it implements, emitting a timed event list.
- **Sprint 3:** hardening, the specification-driven test suite, and performance rehearsal.  In the test suite, every semantic equation has at least one test against a hand-computed event list, the algebraic law is verified empirically on at least three instances, and stochastic constructs are reproducible under a fixed seed.
- **Demo Day:** your live demonstration closes with a short performance: live-editing and re-running a program while the class follows the event output as it changes.  **Emitting events as text is sufficient; audio hardware is never required.**  Ambitious teams may also render sound by translating event lists into Strudel or MIDI.  That translation layer (mapping your semantics onto someone else's) is itself worth a section of your report.

The required scope maps naturally.  Patterns and tracks are your non-numeric type, cycle arithmetic and transformation operators are your arithmetic and precedence story, conditional and repeated structures are your selection and iteration, and the cycle semantics itself is a distinctive feature by construction.  The Music and Live-Coding guide at [Tutorials/MusicLiveCodingPath]({{ site.baseurl }}/Tutorials/MusicLiveCodingPath) provides the full equivalence table mapping each deliverable to its classic counterpart, plus the text-events-only route through the whole track.

---

### Direction C: Extend the Interpreter

Your team may choose to extend the [small Scheme in Flex, Bison, and C]({{ site.baseurl }}/files/starters/interpreter/) as its Team Language Project.  Follow the [Interpreter guide]({{ site.baseurl }}/Projects/TeamLanguage#direction-c-extend-the-interpreter) to build and read it, add a primitive, extend the scanner and grammar, and add a special form.  You submit the language your team extends as the final project.  It is graded through the same proposal, project milestones, Demo Day, and rubric as Directions A and B, with no separate Interpreter assignment or submission.

Defend your design choices with the design scorecard: readability, writability, reliability, and implementation cost, including the priorities and sacrifices for each.  Write grammar v0 and the node inventory for the language you extend, and document its rules and your changes in `SEMANTICS.md`.  Add a distinctive feature that meets the required project scope.  Include the same REPL, file-runner, sample programs, tests, language reference, report, and team contribution statements required below.  The guide's exercises help you extend the interpreter; the final submission must meet the project requirements.

Name this direction and the provided Interpreter in your proposal and project README.  Use the guide's build instructions, and document your C implementation's build, run, and test commands in place of the Python examples below.

#### Purpose and Readings

Read the small working interpreter and change its evaluator, scanner, and grammar to see how the pieces of a language fit together.  The steps below ask you to explain the scanner, grammar, and evaluator; add a primitive; add syntax through the scanner and grammar; and add a special form and explain why it cannot be a function.  Use the answers and checks to verify your changes; this work is submitted and graded through the final project.

- [From Calculator to Scheme Activity]({{ site.lia_viewer_url }}{{ site.raw_pages_url }}Activities/liascript-calculator-to-scheme.md)
- [Flex and Bison]({{ site.baseurl }}/Tutorials/FlexAndBison)
- [C for Flex and Bison]({{ site.baseurl }}/Tutorials/CForFlexAndBison)
- [Scope Chains and Closures Activity]({{ site.lia_viewer_url }}{{ site.raw_pages_url }}Activities/liascript-scope-chains.md), the scope chain this interpreter uses
- [Functional Programming in Scheme Activity]({{ site.lia_viewer_url }}{{ site.raw_pages_url }}Activities/liascript-functional.md)

In this direction, you extend the Interpreter as your final project.  You read a small working interpreter and change it.  You get a Scheme written in Flex, Bison, and C, about 300 lines in all, and you add to it in three small steps.  Everything is in the [starter kit]({{ site.baseurl }}/files/starters/interpreter/), and nothing depends on any earlier assignment.  This guide has no separate grade, deadline, or submission.  Submit your extended language as the Team Language Project, following its required scope, graded milestones, Demo Day, and rubric.

---

#### Before You Start

You need `flex`, `bison`, `gcc`, and `make`.  On Ubuntu, `sudo apt install flex bison gcc make` installs them.  Make a folder named `cs374-interpreter`, and copy the starter kit into it.

---

#### Part 1: Build It, Run It, and Read It

**You write:** `notes.md`.
**You run:** `make`, from inside your folder.

Build it and run the two provided programs.  `make` runs `bison -d parser.y`, `flex scanner.l`, and `gcc`, so you only have to run it again after a change.  The interpreter reads a program from standard input, and it prints the value of each expression at the top level:

```bash
make
./scheme < programs/basics.scm
./scheme < programs/functions.scm
```

> **You should see.**
>
> ```text
> 7
> 9
> (a b c)
> 2
> 120
> 7
> (4 5 6)
> ```

[From Calculator to Scheme](https://liascript.github.io/course/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374-Fall2026/gh-pages/_pages/Activities/liascript-calculator-to-scheme.md#7) builds this same evaluator in Python, and [C for Flex and Bison]({{ site.baseurl }}/Tutorials/CForFlexAndBison) covers the C it is written in: structs, `->`, `switch`, and the table of functions.

Read these three files in this order, because each change below touches a different one:

- **`scanner.l`** turns characters into tokens: numbers, symbols, `#t`, `#f`, and parentheses.
- **`parser.y`** turns tokens into Scheme data.  A list in the source becomes a linked list of `Value`s, built with `cons` in the `items` rule.  Scheme code and Scheme data are the same thing, so the parser needs no other structure.  The `program` rule evaluates each item as soon as it is read.
- **`scheme.c`** holds the evaluator.  In `eval`, a number evaluates to itself and a symbol is looked up.  A list is either a special form, which decides for itself what to evaluate, or a call, which evaluates everything and then applies the function.  `lookup` walks a linked list of scopes, and a call makes a new scope whose parent is the scope where the function was created.  That parent link is why `adder` in `functions.scm` works.

**Do this.**  Answer these in `notes.md`.  The answers are short, and each one points you at a part of the code.

1. Trace `(+ 1 (* 2 3))` through `eval`.  Which case handles the outer list, in what order are its parts evaluated, and what does `apply` receive?
2. Why is `if` a special form in `eval`, when `+` is a primitive?  What would go wrong with `(if (= n 0) 1 (fact (- n 1)))` if `if` were a primitive?
3. In `functions.scm`, `add3` is called after `adder` has already returned.  How does `lookup` still find `a`?  Name the two scopes on the chain.

---

#### Part 2: Add a Primitive, `max`

A primitive is a function written in C, and [the table of functions]({{ site.baseurl }}/Tutorials/CForFlexAndBison#enums-switch-and-a-table-of-functions) shows the pattern on another example.  It receives its evaluated arguments as a list, and `first(a)` and `second(a)` read them.  So adding one takes two lines in `scheme.c`: a function next to `prim_add`, and a row in the `PRIMITIVES` table.  Write `prim_max`, which returns the larger argument, and add its row under the name `max`.

```bash
make && printf '(max 3 7)\n(max (+ 5 5) 7)\n' | ./scheme
```

> **You should see.** `7`, then `10`.  The arguments are evaluated before your function runs, which is why `(+ 5 5)` arrives as `10`.

#### Part 3: Add a Shorthand, `'`

Scheme programmers write `'x` for `(quote x)`, and [Step 5: Quote](https://liascript.github.io/course/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374-Fall2026/gh-pages/_pages/Activities/liascript-calculator-to-scheme.md#10) explains what `quote` does.  The evaluator already handles `quote`, so this change lives only in the scanner and the grammar.

1. In `scanner.l`, the last rule catches a stray `'` as an error, and it is the only character that rule can still reach.  Replace that rule with one that returns the character:

   ```text
   "'"     { return '\''; }
   ```

2. In `parser.y`, add a rule to `datum` that builds the same list the long form would build:

   ```text
   | '\'' datum   { /* TODO: $$ is the list (quote <datum>), built with cons, make_symbol, and nil */ }
   ```

```bash
make && printf "'(a b c)\n(car '(1 2))\n" | ./scheme
```

> **You should see.** `(a b c)`, then `1`.

#### Part 4: Add a Special Form, `cond`

[Step 4: If](https://liascript.github.io/course/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374-Fall2026/gh-pages/_pages/Activities/liascript-calculator-to-scheme.md#9) shows why `if` is a special form, and `cond` has to be one for the same reason: a call would evaluate every clause, and `cond` must evaluate only the one it chooses.  It looks like this:

```text
(cond (test1 expr1) (test2 expr2) ...)
```

Add it to `eval` in `scheme.c`, next to `if`.  Here is the algorithm, and `x->cdr` is the list of clauses:

```text
for each clause c in x->cdr:
    if is_true(eval(first(c), env)):
        return eval(second(c), env)
report an error, with die, that no clause matched
```

```bash
make && printf '(define sign (lambda (n) (cond ((< n 0) -1) ((= n 0) 0) (#t 1))))\n(sign -5)\n(sign 0)\n(sign 9)\n' | ./scheme
```

> **You should see.** `-1`, `0`, and `1`.  Then run the two provided programs again, and confirm their output has not changed.

---

#### Carry This Into Your Project

Keep `notes.md` and the interpreter with your three changes in your team's project repository.  Use `make clean` to remove build products before packaging your `cs374-interpreter` folder.  Continue from these changes toward your team's language design and the Team Language Project requirements; completing this guide alone does not complete the project.

#### Self-Check Before You Continue

- [ ] `make clean && make` shows no warnings.
- [ ] `max`, `'`, and `cond` work.
- [ ] Both provided programs give the same output as before your changes.

#### Reflection Prompts

- Each change touched a different file.  How did you decide where each one belonged?
- `'` needed no change to `eval`.  What does that tell you about the difference between syntax and meaning?

---

## Extensions Menu

The distinctive feature is required, and the [Extensions Menu]({{ site.baseurl }}/Tutorials/LanguageExtensions) is where teams go deeper.  It describes each extension your team can adopt: static type inference, transpilation, a bytecode compiler and stack VM, pattern matching, garbage collection, concurrency, macros, a foreign function interface, libraries and packaging, scripting targets, editor support, continuations, a lambda-calculus core, logic programming, and an upstream open-source contribution.

---

## Milestone 1: Project Hand-Out (the design phase opens)

The hand-out opens a design phase that runs outside class.  There is no class session for it, so the work happens in a team meeting you schedule yourselves.  Nothing is submitted at the hand-out; the point of this milestone is to leave it with a team, a meeting, and a shortlist.

> **Do this.**
> 1. Form a team of three from your standing POGIL groups.
> 2. Put a team meeting on the calendar, early in the design phase.  Pick one external communication channel (Discord, text, or email) and use it from now on.
> 3. At the meeting, discuss who would use your language and what they would use it for. Read Choose Your Direction above and decide which direction best fits your idea.

> **Why this matters.**  This is Tuckman's *storming*.  The argument over which niche to serve is productive conflict.  Have it now, in person, while nothing is graded yet.

### The Niche and the Design Scorecard

Your language needs a reason to exist beyond the assignment.  The strongest student languages pick a *niche* and let it drive every decision.  A niche is the specific group of users and the specific kind of program your language exists to serve: dice-game scripting, turtle-style drawing, survey logic, recipe scaling, music patterns, or grading rules.  The niche supplies your example programs, your Demo Day story, and the tiebreaker for every design argument ("which choice serves dice players?").

The **design scorecard** rates your language on four criteria.  For each one, write what you prioritize and what you give up to get it:

- **Readability:** can a reader who did not write the code follow it quickly?
- **Writability:** can an author produce correct code quickly?
- **Reliability:** how well does the language keep a program from doing the wrong thing without anyone noticing?
- **Implementation cost:** how much will it take to build?  This is your scarcest resource.

Save the full scorecard and the [Project Language Guide's]({{ site.baseurl }}/Tutorials/ProjectLanguageGuide) Grammar v0 builder for Sprint 1.

---

## Milestone 2: The Proposal (28 points)

Submit one short written plan per team in Canvas. Name your partners and tell me what you intend to build. **You do not need a prototype, code, a repository, a formal grammar, an AST inventory, a semantics document, or test results for the proposal.**

1. **Partners:** List all three teammates.
2. **Idea:** Name the people or problem your language will serve. Choose Direction A, B, or C, say why it fits, and describe one distinctive feature in plain language. Name your intended starter if you know it.
3. **Plan:** Say what you will build first, who will start each major task, and how you will check that the distinctive feature works. Describe the check; you do not need to run it yet.

For example, a team building a recipe language might plan a `scale` feature that doubles the quantities in a recipe without changing their units. The proposal says who will start the parser, evaluator, and tests, and names an example the team will run later: scaling `2 cups` by two should give `4 cups`.

See [Demo Day and Final Submission](#milestone-5-demo-day-and-final-submission-72-points) for what you build and turn in after the proposal.

---

## Milestone 3: Sprint 1: Get It Running and Grow the Core

Development starts here, after the proposal. Set up the shared repository and draft your design scorecard, EBNF grammar (mark changes from the starter), AST node inventory (fields and producing and consuming rules), and `SEMANTICS.md` (one section per rule, with a small example and its expected output). Scope the distinctive feature's syntax, behavior, and affected pipeline stages. For Direction B, draft the timed-event equations before you build the evaluator. Name the biggest risk and the smallest experiment that would help you check it. Use these drafts to build and revise the artifacts you will submit at the end.

### The Team Charter

At the start of Sprint 1, write a short team charter you will actually use. Cover these four topics:

**Role rotation plan.**  The project uses four roles: Coordinator (sprint planning, scope), Builder (implementation), Evaluator (testing and sample programs), and Scribe (documentation and decision log).  State how your team will rotate them, for example: "we will rotate by sprint, in alphabetical order by last name."  Every member must hold every role at least once.

**External communication channel and norms.**  State where the team will communicate outside class (Discord, text, email; pick one channel and use it consistently).  State your response-time norm, for example: "we will respond within 24 hours on weekdays, 48 on weekends."  State how you will signal availability changes (illness, travel, exam crunch).

**Preparation norms.**  State what "prepared for class" means for your team, for example: "readings and previous activity reviewed before class; laptop charged; roles assigned by the start of class."  State what you will do if a member is unprepared.

**Disagreement resolution.**  State a concrete mechanism for resolving technical disagreements (for example, "we will vote; ties go to the Coordinator") and interpersonal disagreements (for example, "we will raise the issue with the Scribe, who records it in the decision log; unresolved issues go to the instructor").  Having this written before a disagreement occurs is the point.

Keep one charter in your team repository, with each teammate's typed name. Revisit it during the sprint and revise it if it no longer describes how you work.

### Build and Test the Core

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
2. **The language reference** (approximately four pages): teach your language to a newcomer with examples for every construct, the full EBNF grammar with changes from the starter identified, the AST node inventory, the distinctive feature's guide, and a section per adopted extension.
3. **`SEMANTICS.md`,** final and verified against the implementation by your semantics programs. Direction B: include one denotational equation per construct, at least one algebraic law, and the embedded-versus-external design rationale with at least two alternatives you rejected.
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
