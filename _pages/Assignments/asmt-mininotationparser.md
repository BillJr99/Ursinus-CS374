---
layout: assignment
permalink: /Assignments/MiniNotationParser
title: "Programming Assignment: A Mini-Notation Parser with Flex and Yacc"

info:
  points: 100
  goals:
    - "Construct a lexical analyzer with flex from a regular-expression token specification."
    - "Extend a context-free grammar and its LALR(1) yacc specification with new productions, keeping the grammar conflict-free."
    - "Build and traverse an abstract syntax tree using semantic actions, maintaining a clean separation between syntax and semantics."
    - "Implement a denotational evaluator that maps an AST to timed events, implementing the displayed semantic equations by structural recursion."
    - "Derive and implement the Euclidean rhythm onset condition <span>\\((i \\cdot k) \\bmod n < k\\)</span> and connect it to the generated event spans."
    - "Diagnose grammar conflicts using bison's verbose automaton output."
    - "Validate an independent implementation against a production reference implementation (Strudel)."
    - "Reflect on language design tradeoffs revealed by extending a real DSL."
  purpose: "In class we built a working flex/yacc pipeline for a subset of the TidalCycles/Strudel mini-notation. In this assignment you will grow that subset toward the real language, extending the lexer, the grammar, the AST, and the evaluator in concert, and validating your semantics against the reference implementation at strudel.cc."
  tilt:
    task: "Extend a flex/bison mini-notation pipeline — lexer, LALR(1) grammar, AST, and evaluator — with alternation, Euclidean rhythms, and polymeter, then validate the timed-event output against the Strudel reference."
    criteria: "Assessed on a conflict-free grammar and lexer, clean AST design, evaluator semantics matching the equations, and documented validation against strudel.cc; see the rubric below for the full breakdown."
  tasks:
    - "Complete the scaffolded SLOW and DEGRADE evaluator cases from the in-class module."
    - "Extend the lexer and grammar with alternation <a b c>, verifying zero conflicts."
    - "Extend the lexer and grammar with Euclidean rhythms name(k,n), deriving and implementing the onset rule."
    - "Extend the lexer and grammar with polymeter {a b, c d e} with an optional %NUMBER step count."
    - "Validate all features against strudel.cc and document agreements and discrepancies."
    - "Submit code, a test transcript, the bison .output automaton, and a short report."
  rubric:
    - weight: 25
      description: Grammar and Lexer Extensions
      preemerging: New tokens or productions are absent, or the specification no longer builds.
      beginning: Some constructs parse, but the grammar has unresolved conflicts or rejects valid patterns from the specification table.
      progressing: All required constructs lex and parse correctly with a conflict-free grammar, with minor edge-case omissions.
      proficient: All constructs parse with a conflict-free LALR(1) grammar; the report cites specific states from the bison .output file to demonstrate where each new construct lives in the automaton, and edge cases (nesting new constructs inside one another) are tested deliberately.
    - weight: 15
      description: AST Construction and Design
      preemerging: Semantic actions are missing or the tree does not reflect the input structure.
      beginning: Trees are built but conflate distinct constructs or embed evaluation work inside parser actions.
      progressing: Each production builds exactly one well-typed node; the syntax/semantics boundary is respected throughout.
      proficient: Node design is documented with a written rationale, includes a tree printer whose output appears in the test transcript for every feature, and the report explains how the tagged-union design parallels an algebraic data type.
    - weight: 25
      description: Evaluator Semantics
      preemerging: The evaluator is incomplete for the in-class scaffolded cases (SLOW, DEGRADE).
      beginning: New constructs produce events, but spans are incorrect for nested or combined cases.
      progressing: All constructs produce correct event spans matching the displayed semantic equations, including the derived Euclidean onset rule.
      proficient: Each evaluator case is annotated with a comment naming the semantic equation it implements; cycle-dependent constructs (SLOW, alternation) take an explicit cycle parameter; DEGRADE is reproducible via a fixed seed (srand(42)); and the report includes a worked hand-derivation of at least one nested example that the program output matches exactly.
    - weight: 10
      description: Validation Against the Reference Implementation
      preemerging: No comparison to Strudel is attempted.
      beginning: A comparison is mentioned but undocumented or limited to a single trivial pattern.
      progressing: At least five patterns spanning all new features are compared against strudel.cc with documented outcomes.
      proficient: The comparison table covers all features including nested combinations across multiple cycles, every discrepancy is investigated and explained (parser difference, semantic difference, or bug), and at least one discrepancy investigation includes a hypothesis test.
    - weight: 10
      description: Reflection
      preemerging: Reflection prompts are unanswered.
      beginning: Responses are superficial or restate the assignment.
      progressing: Responses engage the prompts with specific evidence from the student's own implementation experience.
      proficient: Responses connect the implementation experience to course concepts (language classes, LALR(1) limits, syntax versus semantics, DSL design tradeoffs) with concrete examples from the student's own code and conflict reports.
    - weight: 10
      description: Code Quality and Documentation
      preemerging: Code does not compile or is unreadable.
      beginning: Code compiles with warnings, sparse comments, or memory errors on valid input.
      progressing: Clean compilation, consistent style, meaningful comments connecting code to theory.
      proficient: Compiles cleanly with -Wall; every error path prints a location-prefixed message; the Makefile reproduces the full build; comments cite the relevant equations and grammar productions by name.
    - weight: 5
      description: Submission Completeness
      preemerging: Required artifacts are missing.
      beginning: Code is present but the transcript, .output file, or report is absent.
      progressing: All artifacts present and organized as specified.
      proficient: All artifacts present, the test transcript is regenerable by a single make test target, and the report includes the toolchain version information for reproducibility.

tags:
  - parsing
  - flex
  - yacc
  - grammars
  - dsl
  - semantics
  - music
---

## Overview

In the in-class module, we built a complete language pipeline for a subset of the mini-notation shared by TidalCycles and Strudel: a flex scanner, a conflict-free LALR(1) yacc grammar, a tagged-union AST, and an evaluator implementing a small denotational semantics over the cycle $[0,1)$. That subset handled sequences, rests, groups, `*`, `/`, and `?`. In this assignment you will extend every stage of that pipeline in concert, which is the authentic experience of DSL maintenance: a new construct is never just a parser change, because the lexer must tokenize it, the grammar must place it, the AST must represent it, and the evaluator must mean it.

Start from the in-class code (provided in the course repository under `examples/mininote/`). The default toolchain is C with flex and bison, as in class; if you prefer to work in Python with PLY or SLY, speak with me first, and note that the grammar-analysis deliverables (the `.output` automaton citations) have direct PLY equivalents (`parser.out`) that you will be expected to produce.

Do **not** simply transcribe Strudel's own parser; the point is to derive the grammar and semantics yourself and then use Strudel as an *oracle* to test against. Be creative with your test patterns, and do not limit yourself to the examples we used during class.

---

## Part 1: Complete the Scaffolded Cases

**Theoretical foundation.** The in-class evaluator deliberately left `N_SLOW` and `N_DEGRADE` unimplemented. `slow n` stretches its child across $n$ cycles, so within cycle $c$ the evaluator must render the window of the child corresponding to cycle position $\lfloor c \rfloor \bmod n$; this forces a design change, because the evaluator signature `eval_pattern(Node*, double, double)` carries no cycle number. Extend the signature to carry the current cycle (or derive it from the span), and document your choice.

**Implementation.** Provide the complete revised `eval_pattern` function (never a fragment). For `N_DEGRADE`, gate each event on `rand() < RAND_MAX / 2` with `srand(42)` called exactly once in `main`, so that grading is reproducible.

Your submission should include:
- The complete revised `eval.c` and any header changes.
- A transcript of `bd/2 sn` evaluated on cycles 0 and 1, with a sentence explaining why the two cycles differ.
- A transcript of three consecutive runs of `hh*8?` demonstrating identical output.

---

## Part 2: Alternation

**Theoretical foundation.** The construct `<a b c>` plays exactly one of its elements per cycle, rotating: element $\lfloor c \rfloor \bmod k$ on cycle $c$, occupying the construct's entire span. Formally, for children $c_1, \ldots, c_k$,

$$
\mathcal{E}[\![\, \texttt{ALT}(c_1, \ldots, c_k) \,]\!](t_0, t_1, c) \;=\; \mathcal{E}[\![\, c_{(c \bmod k) + 1} \,]\!](t_0, t_1, c)
$$

**Implementation.** Add `LANGLE`/`RANGLE` tokens to the lexer, an `atom` production deriving `LANGLE sequence RANGLE`, an `N_ALT` node, and the evaluator case above. Run `bison -v` and confirm the grammar remains conflict-free; if you introduce a conflict along the way, keep the broken `.output` excerpt, because diagnosing it is worth describing in your report.

Your submission should include:
- The complete revised `.l` and `.y` files.
- A transcript of `bd <sn cp hh>` across cycles 0, 1, 2, and 3, demonstrating the rotation and its wraparound.

---

## Part 3: Euclidean Rhythms

**Theoretical foundation.** The construct `bd(3,8)` distributes $k = 3$ onsets as evenly as possible among $n = 8$ steps, a problem with a beautiful pedigree: Toussaint observed that the resulting onset sets reproduce rhythm timelines found across world musical traditions, with $E(3,8)$ giving the Cuban tresillo. An onset occurs at step $i \in \{0, \ldots, n-1\}$ exactly when

$$
(i \cdot k) \bmod n \;<\; k
$$

Before implementing, verify this rule by hand for $E(3,8)$: steps 0, 3, and 6 satisfy the inequality, yielding the pattern `x..x..x.`. Include this hand-verification, for $E(3,8)$ and one other $(k, n)$ pair of your choosing, in your report, and prove or argue in two or three sentences that the rule always yields exactly $k$ onsets when $\gcd$ considerations are set aside, or exhibit the algebraic fact that makes it so.

**Implementation.** Lexically, `(`, `)`, and `,` become tokens; syntactically, Euclid is a postfix modifier, so it belongs among the `term` productions: `term LPAREN NUMBER COMMA NUMBER RPAREN`. The evaluator divides the construct's span into $n$ equal steps and renders the child into each step satisfying the onset rule, with rests elsewhere.

Your submission should include:
- The complete revised specifications and evaluator case.
- Transcripts of `bd(3,8)` and `bd(5,8)`, each accompanied by the hand-computed onset set it must match.

---

## Part 4: Polymeter

**Theoretical foundation.** The construct `{a b, c d e}` runs its comma-separated subsequences simultaneously, each stepping at a common rate so that subsequences of different lengths drift against one another and realign; `{a b, c d e}%4` fixes the number of steps per cycle to 4. Specify the semantics yourself, precisely, in the displayed-equation style of the in-class module, before writing any code; the specification is a graded artifact, and discovering that your first specification was ambiguous is an intended outcome. Use strudel.cc to interrogate the corner cases your specification must decide (what happens on cycle 1? which subsequence determines the default step count?).

**Implementation.** Add `LBRACE`, `RBRACE`, `COMMA` (shared with Part 3), and `PERCENT` tokens; add productions for a brace-delimited list of sequences with an optional `%NUMBER` suffix; add an `N_POLY` node carrying the subsequences and step count; implement your specification.

Your submission should include:
- Your written semantic specification, including the corner cases and how Strudel resolved them.
- The complete revised specifications and evaluator case.
- Transcripts of `{bd sn, hh hh hh}` across cycles 0, 1, and 2, annotated to show the drift and realignment.

---

## Part 5: Validation Against the Reference Implementation

Construct a validation table of at least eight patterns that collectively exercise every feature, including at least two patterns that nest new constructs inside one another (for example, `<bd(3,8) sn>` or `{bd <sn cp>, hh*2}`). For each pattern, record your evaluator's event list and the spans Strudel highlights at strudel.cc, and mark agreement or discrepancy. Investigate every discrepancy to a conclusion: a difference in the grammar (does Strudel even accept the string?), a difference in semantics (same tree, different meaning?), or a bug (yours or, occasionally and delightfully, theirs).

---

## Deliverables

Submit a ZIP containing your complete source (`.l`, `.y`, `.c`, `.h`, `Makefile`), the generated `mininotation.output` automaton file, a test transcript regenerable via `make test`, and a report of approximately two to three pages containing the hand-derivations, the polymeter specification, the validation table, and your reflection responses. Each code file should be cleanly commented with references to the equations and productions it implements.

Ensure reproducibility by fixing random seeds and listing software version information (`flex --version`, `bison --version`, `gcc --version`) in your report.

---

## Reflection Prompts

- The lexer, grammar, AST, and evaluator changed together for every feature. Which stage surprised you by being the hardest to extend, and what does that suggest about where DSL maintenance costs concentrate?
- Alternation and `slow` forced cycle information into an evaluator that previously needed none. What does this reveal about how semantic requirements propagate backward into interface design, and where have you seen the same phenomenon in software outside this course?
- Strudel's grammar accepts some strings yours rejects, or vice versa. Choose one such string from your validation table and argue whether the difference is a defect, a design choice, or a dialect, and what a language specification document would need to say to settle the question.
- Toussaint's Euclidean rhythms emerged from a scheduling algorithm and turned out to describe music made by humans across centuries and continents. What does this case suggest about the relationship between formal structure and cultural practice, and about who is credited when an algorithm formalizes existing human knowledge?

---

## Submission Instructions

Submit your ZIP to the course LMS under this assignment. If collaboration with a buddy was permitted, did you work with a buddy on this assignment? If so, who? If not, do you certify that this submission represents your own original work? Please identify any and all portions of your submission that were not originally written by you.

Approximately how many hours it took you to finish this assignment (I will not judge you for this at all...I am simply using it to gauge if the assignments are too easy or hard)?

---

## Resources

- The in-class module on flex/yacc and the mini-notation, including the starter pipeline in `examples/mininote/`.
- Levine, John. *flex & bison* (O'Reilly, 2009), particularly the chapters on conflict diagnosis.
- Toussaint, Godfried. "The Euclidean Algorithm Generates Traditional Musical Rhythms." *BRIDGES: Mathematical Connections in Art, Music, and Science* (2005).
- The Strudel reference at [strudel.cc](https://strudel.cc) and its mini-notation documentation, used here strictly as a validation oracle.
