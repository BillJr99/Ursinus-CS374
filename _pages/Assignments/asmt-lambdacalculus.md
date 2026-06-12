---
layout: assignment
permalink: Assignments/LambdaCalculus
title: "Written Assignment: The Lambda Calculus By Hand and In Code"

info:
  points: 100
  goals:
    - "Perform alpha-conversion, capture-avoiding substitution, and beta-reduction by hand with complete, auditable derivations."
    - "Compare normal-order and applicative-order evaluation strategies on terms where they diverge in behavior."
    - "Construct Church encodings of booleans, numerals, and pairs, and verify their algebraic behavior."
    - "Implement a substitution-based interpreter for the untyped lambda calculus with correct capture avoidance."
    - "Verify by-hand derivations mechanically against the interpreter."
    - "Connect the calculus to its working incarnations in Haskell, JavaScript, and the live coding languages studied in this unit."
  purpose: "The lambda calculus rewards being computed by hand and being computed by machine, and the two activities check one another. In this assignment you will do both: produce careful paper derivations, build an interpreter whose substitution function is provably careful about capture, and use each artifact to audit the other."
  tasks:
    - "Complete the by-hand derivation problems, one numbered reduction step per line."
    - "Implement an AST, capture-avoiding substitution, and normal-order reduction in Python."
    - "Implement an applicative-order strategy and demonstrate a term where the strategies diverge."
    - "Encode and test Church booleans, numerals, and pairs in your interpreter."
    - "Verify each by-hand derivation against the interpreter and reconcile any disagreement."
    - "Answer the reflection prompts connecting the calculus to Tidal, Strudel, and your other languages."
  rubric:
    - weight: 30
      description: By-Hand Derivations
      preemerging: Derivations are absent, or steps are skipped so that the work cannot be audited.
      beginning: Most reductions reach correct results, but redexes are not identified per step or capture situations are mishandled.
      progressing: All derivations are correct, one reduction per line, with the contracted redex marked and alpha-conversions shown explicitly where required.
      proficient: Derivations are correct and annotated: each capture-avoidance renaming is justified by naming the free variable that would have been captured, strategy choices are stated, and the writeup notes where Church-Rosser guarantees the result is strategy-independent.
    - weight: 30
      description: Interpreter Implementation
      preemerging: The interpreter does not run or cannot reduce simple terms.
      beginning: Beta-reduction works on capture-free terms but the substitution function captures variables on the provided adversarial tests.
      progressing: Capture-avoiding substitution passes all provided tests; normal-order reduction reaches normal forms correctly.
      proficient: Both strategies are implemented behind a common interface; substitution handles all three cases of the formal definition with the fresh-variable case tested explicitly; configuration (step limits, trace verbosity) is externalized to a JSON config; exceptions print location-prefixed messages with tracebacks rather than failing silently.
    - weight: 15
      description: Church Encodings and Verification
      preemerging: Encodings are absent or untested.
      beginning: Booleans and numerals are encoded but verification is limited to one or two cases.
      progressing: Booleans, numerals, and pairs are encoded and verified, including arithmetic on numerals through the interpreter.
      proficient: Verification is systematic (a test table mapping each law to a passing reduction), includes at least one law verified both by hand and by machine with the transcripts cross-referenced, and discusses one encoding design alternative.
    - weight: 15
      description: Connections and Analysis
      preemerging: The analysis questions are unanswered.
      beginning: Answers restate module content without engaging the student's own artifacts.
      progressing: Answers are correct and draw on the student's own derivations and interpreter behavior as evidence.
      proficient: Answers are precise, cite specific terms and transcripts from the submission, and articulate the currying and evaluation-strategy connections to Tidal and Strudel with concrete code-level correspondences.
    - weight: 10
      description: Organization and Writing Quality
      preemerging: The submission is disorganized or substantially incomplete.
      beginning: Components are present but hard to navigate or inconsistently formatted.
      progressing: Clear sectioning matching the assignment parts; readable mathematical notation; clean prose.
      proficient: The document reads as a coherent technical report, with derivations typeset or impeccably scanned, transcripts labeled and referenced from the prose, and version information listed for reproducibility.

tags:
  - lambda-calculus
  - theory
  - interpreters
  - functional-programming
  - written
---

## Assignment: The Lambda Calculus By Hand and In Code

The lambda calculus is small enough that you can hold all of it in your head, and that smallness is an invitation: every claim in this assignment is one you can check completely, by hand, with no appeal to authority. The hand and the machine play complementary roles here. Paper derivations build the reflexes (spotting redexes, fearing capture) that no amount of running code instills, while the interpreter is the tireless auditor that catches the step 7 slip your eyes glide past. You will build both and make them agree.

### Instructions

1. **By hand.** For each term below, reduce to normal form (or demonstrate divergence) under the indicated strategy. One reduction per line; underline or box the redex you contract; show every alpha-conversion as its own line with a one-clause justification.

   - (a) $(\lambda x.\, \lambda y.\, x\ y)\ (\lambda z.\, z)\ w$, normal order.
   - (b) $(\lambda x.\, \lambda y.\, x)\ y$, any strategy; capture awaits the unwary.
   - (c) $\mathbf{mul}\ \overline{2}\ \overline{2}$ using the Church definitions from the module, normal order, reduced fully to $\alpha$-equivalence with $\overline{4}$.
   - (d) $(\lambda x.\, \lambda y.\, y)\ \Omega$ under both normal order and applicative order, with a sentence stating what each strategy does and why.

2. **In code.** Implement, in Python, an interpreter for the untyped calculus comprising: an AST (`Var`, `Lam`, `App`), a free-variable function, capture-avoiding substitution implementing the three-case definition from the module exactly, a single-step reducer for each of normal order and applicative order, and a driver that reduces to normal form under a configurable step limit. Externalize the step limit and trace verbosity into a JSON configuration file. Every exception handler must print the exception with a location-specific prefix (for example, `[interp:substitute]`) and a traceback; do not silently swallow exceptions. Provide complete function definitions throughout your writeup, never fragments.

3. **Adversarial substitution tests.** Your interpreter must pass, and your report must display, the results of substituting on these capture traps: $(\lambda y.\, x)[x := y]$, $(\lambda y.\, x\ y)[x := y\ z]$, and one trap of your own design that defeats a substitution function lacking the fresh-variable case. For your own trap, show the wrong answer naive substitution produces.

4. **Encodings.** Encode Church booleans, numerals through $\overline{4}$, $\mathbf{succ}$, $\mathbf{add}$, $\mathbf{mul}$, and pairs ($\mathbf{pair}$, $\mathbf{fst}$, $\mathbf{snd}$) as terms in your interpreter's AST. Verify mechanically: $\mathbf{add}\ \overline{2}\ \overline{2}$ and $\mathbf{mul}\ \overline{2}\ \overline{2}$ both reduce to terms $\alpha$-equivalent to $\overline{4}$, and $\mathbf{fst}\ (\mathbf{pair}\ a\ b)$ reduces to $a$.

5. **Cross-verification.** Run each by-hand problem from step 1 through your interpreter with tracing enabled, and reconcile: either the transcripts agree step for step under the same strategy, or you identify which artifact erred and correct it, documenting the reconciliation. The reconciliation narrative, including any errors found, is a graded component; finding your own mistake is worth more than not reporting one.

6. **Analysis.** In a page or less, answer: (a) precisely where, in the expression `every 4 (fast 2) $ sound "bd sn"`, does currying occur, and what is the lambda term that `fast 2` denotes? (b) The Strudel idiom `x => x.fast(2)` and the Haskell partial application `fast 2`: exhibit the eta-conversion relating them and state what eta-equivalence asserts in general. (c) Using your divergence result from 1(d), explain why Haskell can pass an infinite Tidal pattern to a function that ignores it while an applicative-order language evaluating the pattern eagerly could not.

---

## Deliverables

- **A written document** (PDF; typeset or cleanly scanned) containing the derivations, adversarial test results, reconciliation narrative, and analysis.
- **Your interpreter** (Python source plus the JSON configuration file), with a `README` stating how to reproduce every transcript in the document.
- **A transcript file** showing the encodings verification of step 4 and the traced runs of step 5.

Ensure reproducibility by listing software version information, and by making every transcript regenerable from a single documented command.

---

## Submission Instructions

Submit a single ZIP to the course LMS under this assignment. If collaboration with a buddy was permitted, did you work with a buddy on this assignment? If so, who? If not, do you certify that this submission represents your own original work? Please identify any and all portions of your submission that were not originally written by you.

Approximately how many hours it took you to finish this assignment (I will not judge you for this at all...I am simply using it to gauge if the assignments are too easy or hard)?

---

## Reflection Prompts

- Your substitution function and the parser you built for the mini-notation both enforce invariants that the surface syntax hides. Compare the two: which invariant was harder to get right, and what made it so?
- Church encodings show that data can be represented as behavior. Where in a modern language or system have you seen this idea earn its keep, and where would it be a poor engineering choice?
- The Church-Rosser theorem promises that strategies can differ in termination but never in the normal form reached. How did that guarantee, or its absence, shape your debugging experience when your two strategies disagreed?
- Alonzo Church built this calculus in 1936 to answer a question in logic, decades before anyone could run it. What does this unit's arc, from a 1936 logic paper to a browser tab making music, suggest to you about the relationship between theoretical and applied computer science?

---

## Resources

- The in-class module on the lambda calculus, including the substitution definition your implementation must match.
- Pierce, Benjamin C. *Types and Programming Languages* (MIT Press, 2002), Chapters 5 through 7, including the discussion of representing terms and avoiding capture in an implementation.
- Sestoft, Peter. "Demonstrating Lambda Calculus Reduction." *The Essence of Computation* (Springer, 2002). A careful tour of reduction strategies with an accompanying reducer; excellent to consult after your own implementation works.
