# Language Design Studio: Sprint 0
<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://github.com/BillJr99/Ursinus-CS374-Fall2026/blob/gh-pages/_pages/Activities/liascript-languagedesign.md or locally via https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374/gh-pages/_pages/Activities/liascript-languagedesign.md

import: https://raw.githubusercontent.com/liascript/CodeRunner/master/README.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

# Language Design Studio: Sprint 0

The team project begins today: your team will design and implement **a programming language of your own**, assembling the lexer, parser, AST, environments, and evaluator you each built into one system with an identity, a grammar, and a Demo Day. Today is Sprint 0: identity, scorecard, grammar v0, and a working plan. The arc: **what makes a language yours $\rightarrow$ the design scorecard $\rightarrow$ grammar and node inventory v0 $\rightarrow$ sprint roles and cadence**.

---

## Directions and Group Roles

From today through Demo Day, your team works in **project roles, rotated every sprint**:

- **Coordinator**: owns the sprint plan, runs stand-ups, watches scope.
- **Builder(s)**: own the code increment of the sprint.
- **Evaluator**: owns the test suite, the sample programs, and release readiness.
- **Scribe**: owns the design documents, `SEMANTICS.md`, meeting notes, and decision log.

Every member holds every role at least once before Demo Day; the Scribe records today's rotation schedule. After class, respond to the reflective prompt individually in your notebook.

---

# Part I: Identity

## 1. A Language Is a Point of View

**Your language needs a reason to exist beyond the assignment.** The strongest student languages pick a *niche* and let it drive decisions: a language for dice-game scripting, for turtle-style drawing, for survey logic, for recipe scaling, for music patterns, for grading rules. The niche supplies your example programs, your Demo Day story, and the tiebreaker for every design argument ("which choice serves dice players?"). General-purpose-but-tiny is also legitimate; what is not legitimate is having no answer to "who is this for?"

**Constraints (the non-negotiables).** Your language must include: variables with your documented scoping; arithmetic with full precedence; booleans, comparisons, and short-circuit logic; selection and iteration; strings or another non-numeric type; and at least one **distinctive feature** that required real design (functions with closures, pattern slices, a domain-specific statement, a desugared construct). It must be implemented on your own pipeline components, ship with a REPL and a file-runner, and include at least five sample programs.

---

## Model 1: The Design Scorecard

Recall the evaluation criteria module's scorecard. Today it becomes binding.

### Critical Thinking Questions

1. Draft your scorecard: for readability, writability, reliability, and cost (of implementation, your scarcest resource), one sentence on what your language prioritizes and one on what it knowingly sacrifices, *in service of the niche*.
2. Stress-test the niche: each teammate writes one program (five to ten lines, in imagined syntax) your users would actually want. Do the four sketches agree on syntax? Catalog every disagreement; each is a design decision with your team's name on it.
3. Apply the third lens: pick the two most contested decisions from question 2 and resolve each with an explicit appeal to the scorecard, recording the loser's strongest argument in the decision log. (Decisions with recorded dissent reverse gracefully; decisions by fatigue do not.)

---

# Part II: Grammar v0 and the Node Inventory

## 2. Write It Down or It Is Not Designed

**Grammar v0.** Produce the EBNF for your full statement set and your expression ladder, niche constructs included, in the dialect from the syntax module. Mark every place your grammar differs from the class language, because each difference is parser work, and Sprint 1 is sized by this list.

**Node inventory.** One table: every AST node, its fields, the parser rule that builds it, and the evaluator rule that consumes it. Empty cells are the sprint backlog, made visible.

**`SEMANTICS.md` v0.** Import every decision your assignments already made you document (truthiness, division by zero, scoping, loop scopes, type strictness), then add the niche feature's semantics in the same style: exhaustive, exampled, no "etc."

[[MC]]
A team's niche is dice-game scripting, and they are debating whether `3d6` should be core syntax (a lexer token and AST node) or a library function `roll(3, 6)`. The scorecard-driven way to decide is:
- ( ) Core syntax, because it is more impressive at Demo Day
- ( ) A function, because lexer changes are risky
- (x) Ask which choice best serves the niche's readability and writability, then weigh it against the implementation cost row of the scorecard
- ( ) Defer the decision until the final sprint

---

# Part III: The Plan

## 3. Sprints to Demo Day

The remaining weeks run in sprints aligned with in-class studio days (see the sprint studio activity for the protocols). Each sprint ends with: a runnable increment, passing tests (the Evaluator demonstrates), updated documents (the Scribe demonstrates), and the role rotation. The standard arc, adjusted to your design's risk: **Sprint 1** merges members' components into one pipeline running the class language; **Sprint 2** implements grammar v0's differences and the distinctive feature's skeleton; **Sprint 3** completes the feature, hardens errors, and builds the sample program suite; the **gallery walk** then triages polish from disclosure for **Demo Day**.

## 4. Exercises (Today's Deliverables)

1. *The one-pager.* Language name, niche, the four-row scorecard, and the team's three-sentence pitch. Post it; it is the cover page of your proposal.
2. *Grammar v0 and node inventory.* As specified above, committed to the team repository with the decision log.
3. *Sprint 1 plan.* The Coordinator drafts: whose lexer, whose parser, whose evaluator seed the merge (a real decision; discuss kindly), the merge order, and each member's first task with a date.
4. *Risk pre-mortem.* As a team, name the one technical risk most likely to derail you (the distinctive feature's parser change? the merge?) and the smallest experiment that retires it this week.

---

## Reflection Prompt

In your notebook: you have criticized languages all semester; today you became answerable for one. Which criticism you have made of other languages do you most fear earning yourself, and what will you do in the next two weeks to dodge it?

---

## 5. Further Reading

- Your own assignment codebases, reread as a library you are about to depend on.
- Robert Nystrom. *Crafting Interpreters*, "The Lox Language" chapter: a master class in specifying a small language readably.
- The project specification and rubric, reread tonight with the scorecard beside it.
