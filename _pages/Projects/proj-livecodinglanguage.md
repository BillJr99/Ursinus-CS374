---
layout: assignment
permalink: /Projects/LiveCodingLanguage
title: "Project: Design and Implement Your Own Live Coding Language"

info:
  points: 100
  goals:
    - "Design a small domain-specific language, producing a written specification with a formal grammar and a denotational account of its semantics."
    - "Justify embedded-versus-external design decisions against the tradeoff axes studied in this unit."
    - "Implement a complete language pipeline (lexer, parser, AST, evaluator) with flex and yacc, maintaining a conflict-free LALR(1) grammar."
    - "Define and implement a semantics mapping programs to timed event structures."
    - "Validate the implementation against the specification with a documented test suite."
    - "Present and perform with the language, demonstrating it live and reflecting on its design under use."
  purpose: "Throughout this unit you have studied a language (the mini-notation), parsed it, given it a semantics, and met the calculus beneath its host languages. The project closes the loop: you will design a small live coding language of your own, specify it precisely, build it with the flex/yacc pipeline, and perform with it. The deliverable is not only a working artifact but a defensible set of design decisions."
  tasks:
    - "Stage 1: Language design document with grammar and semantic sketch."
    - "Stage 2: Working lexer and parser producing printed ASTs, with the bison automaton report."
    - "Stage 3: Evaluator producing a timed event list, with a specification-driven test suite."
    - "Stage 4: Final report, in-class demonstration, and a short live performance or rendered output."
  rubric:
    - weight: 25
      description: Language Design and Specification
      preemerging: The design document is missing, or the grammar is informal sketches without productions.
      beginning: A grammar is given but is ambiguous, incomplete relative to the described features, or the semantics is described only by example.
      progressing: The grammar is complete and unambiguous, the semantics is specified with displayed equations in the style of the unit, and design decisions are stated.
      proficient: The specification is precise enough that a classmate could reimplement the language from it alone; design decisions are argued against the embedded/external tradeoff axes with explicit rejected alternatives; at least one semantic corner case is identified and resolved in the document before implementation.
    - weight: 30
      description: Implementation Quality
      preemerging: The pipeline does not build, or the parser rejects programs the specification accepts.
      beginning: The pipeline builds and handles simple programs, but the grammar has unresolved conflicts or the AST conflates constructs.
      progressing: The full pipeline works on all specified constructs with a conflict-free grammar and a clean syntax/semantics separation.
      proficient: The grammar is conflict-free with the .output automaton submitted and discussed; errors produce location-prefixed messages rather than crashes; the build is reproduced by a single make; memory handling is clean on valid and invalid inputs; code comments cite the specification's productions and equations by name.
    - weight: 20
      description: Semantics and Evaluation
      preemerging: The evaluator is absent or produces untimed output.
      beginning: Events are produced but disagree with the specification on nested or combined constructs.
      progressing: The evaluator implements the specified semantics correctly, verified by a test suite mapping specification clauses to passing tests.
      proficient: Every semantic equation in the specification has at least one corresponding test; cycle-dependent behavior is handled and demonstrated across multiple cycles; one nontrivial algebraic law of the language (stated in the specification) is verified empirically and argued from the definitions.
    - weight: 15
      description: Presentation and Demonstration
      preemerging: No demonstration is given.
      beginning: The demonstration shows the tool but does not connect design decisions to outcomes.
      progressing: A clear demonstration including a live or rendered performance, with design rationale presented to the class.
      proficient: The demonstration teaches the audience something transferable about language design, includes a live modification of a running or re-run program, and handles audience questions about specification corner cases with reference to the document.
    - weight: 10
      description: Final Report and Reflection
      preemerging: The report is missing or perfunctory.
      beginning: The report describes what was built without evaluating the design.
      progressing: The report evaluates the design honestly against its specification, documenting what changed between Stage 1 and the final artifact and why.
      proficient: "The report includes a substantive postmortem: which specification decisions survived contact with implementation and performance, which did not, a candid account of the hardest defect with its diagnosis trail, and a concrete redesign the author would make in a version 2."

tags:
  - final-project
  - dsl
  - parsing
  - flex
  - yacc
  - semantics
  - music
---

# Overview

You have spent this unit inside other people's languages: parsing the mini-notation that Alex McLean designed, validating against the Strudel implementation that Felix Roos built, and tracing both back to the calculus Alonzo Church wrote down in 1936. This project hands you the designer's chair. Working individually or in pairs (pairs take on the larger scope noted in each stage), you will design a small live coding language of your own, give it a specification precise enough to be implemented by a stranger, implement it with the flex/yacc pipeline from this unit, and close by performing with it, because a live coding language that has never been performed has never really been tested.

Your language must be meaningfully your own rather than a re-skin of the mini-notation, and the design space is wide. Past directions that have worked well include: a drum-machine language organized around named, layered tracks with mutation operators; a melodic language with scales, degrees, and transposition as first-class constructs; a language whose primitives are rhythmic transformations (rotate, invert, thin) applied to seed patterns; and a language for spatial or lighting cues synchronized to cycles, which demonstrates that the cycle semantics generalizes beyond audio. Whatever the direction, the non-negotiables are a formal grammar, a denotational semantics over cycle time in the style of this unit, and a working evaluator that emits a timed event list. Emitting events as text is sufficient; ambitious teams may additionally render audio by translating their event lists into Strudel or into MIDI, and that translation layer, mapping your semantics onto someone else's, is itself worth a section of your report.

The project proceeds in four stages with checkpoints; later stages may revise earlier decisions, and documenting those revisions honestly is a graded virtue, not a confession.

---

## Stage 1: Language Design Document

Produce a specification document containing: the language's purpose and intended performance idiom in a paragraph; a complete context-free grammar in yacc-style productions; a token-level lexical specification; a denotational semantics, one displayed equation per construct, mapping programs to event sets over cycle spans; at least one algebraic law your language satisfies, stated as an equation; and a design rationale arguing your major decisions against the embedded/external tradeoff axes from the unit, including at least two alternatives you considered and rejected. Pairs additionally specify at least one construct whose semantics requires cycle-dependent state (in the spirit of alternation or `slow`).

**Checklist:**
- Purpose statement and a short example program with its intended meaning worked by hand.
- Complete grammar and lexical specification.
- Semantic equations covering every construct, plus one stated algebraic law.
- Design rationale with rejected alternatives.
- One identified semantic corner case, with its resolution.

---

## Stage 2: Lexer and Parser

Implement the lexical and syntactic front end with flex and bison. The deliverable parses every program in your specification's example set, prints the AST in an indented tree format, rejects invalid programs with location-prefixed error messages, and builds via a single `make`. Run `bison -v` and submit the `.output` automaton; your checkpoint memo must cite at least one state from it and explain, in a sentence or two, what that state is waiting to see. If your grammar produced conflicts along the way, the memo should narrate one diagnosis using the conflict report, which is among the most professionally transferable skills this project exercises.

**Checklist:**
- `make` builds the front end from a clean checkout.
- All specification examples parse to correct printed trees.
- Invalid-input tests demonstrate graceful, located errors.
- `.output` file submitted with the state-citation memo.

---

## Stage 3: Evaluator and Test Suite

Implement the evaluator by structural recursion over the AST, one case per semantic equation, each case commented with the equation it implements. Build a specification-driven test suite: every semantic equation has at least one test mapping a program to its hand-computed event list, runnable via `make test`, and your stated algebraic law is verified empirically on at least three instances. Any stochastic construct must be reproducible under a fixed seed. Pairs additionally demonstrate their cycle-dependent construct across at least three cycles.

**Checklist:**
- Evaluator covering every construct, with equation-citing comments.
- `make test` runs the full suite and reports results.
- Hand-computed expected outputs included alongside each test.
- Algebraic law verified empirically, with the instances documented.

---

## Stage 4: Submission, Presentation, and Performance

**Deliverables:**
1. The complete source tree (`.l`, `.y`, C sources, `Makefile`, tests), building and testing cleanly from a fresh checkout, with toolchain version information recorded for reproducibility.
2. The final specification document, revised to match the implemented language, with a change log from Stage 1.
3. A final report of approximately four pages: design narrative, the postmortem described in the rubric, the hardest-defect diagnosis trail, and your version 2 redesign.
4. An in-class presentation of ten minutes (fifteen for pairs): teach one transferable design lesson, demonstrate the pipeline end to end, and close with a short performance, live editing and re-running a program of your language while the class follows the event output (or rendered sound) as it changes.

---

### Submission Rubric

See the **rubric** section in this assignment for the detailed evaluation breakdown.

---

## Reflection Prompts

These prompts seed the report's postmortem; address them directly within it.

- Which decision in your Stage 1 specification did implementation prove wrong, and what early signal, had you noticed it, would have predicted the problem?
- Performance is a usability test conducted under pressure. What did performing with your language reveal that your test suite could not?
- Your language formalizes some musical (or temporal) intuition. Whose intuition is it, what does your notation make easy and what does it make invisible, and who would find your language foreign?
- Having now occupied designer, implementer, specifier, and performer roles for one language, which role most changed how you read other languages, and how?
