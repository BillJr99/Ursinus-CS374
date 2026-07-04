---
layout: assignment
permalink: /Assignments/FlockOfBirds
title: "Assignment: A Flock of Functions — Combinatory Logic in Code"

info:
  points: 100
  goals:
    - "Reduce combinatory logic expressions by hand using the I, K, S, B, C, W, and M rules."
    - "Derive standard higher-order functions (compose, flip, const, id) as bird combinators."
    - "Implement a combinator term reducer in Python using an AST representation."
    - "Apply bracket abstraction to convert lambda terms to SKI expressions mechanically."
    - "Connect combinatory logic to point-free programming style in Python and Haskell."
    - "Appreciate the philosophical significance of Turing-complete computation with zero variables."
  purpose: "The combinatory calculus strips the lambda calculus down to its barest bones: no variables, no binding, no substitution, only application and a small fixed set of primitive combinators. This assignment asks you to work within that constraint — deriving familiar functions from first principles, reducing terms by hand, and building a machine that reduces them for you. The constraint is the point: when you can only use application and the birds, you are forced to see function composition, argument passing, and currying as the only tools available, and that discipline reshapes how you think about higher-order programming."
  tasks:
    - "Perform hand reductions of combinator expressions, one rule per step."
    - "Derive B, C, and W from S and K using bracket abstraction."
    - "Implement an AST and combinator reducer for SKI (plus B, C, W, M)."
    - "Implement point-free versions of five standard functions using only the birds."
    - "Write a bracket abstraction translator from lambda terms to SKI."
    - "Demonstrate your reducer on the Y combinator in SK."
    - "Answer analysis questions connecting combinators to modern programming."
  rubric:
    - weight: 25
      description: Hand Reductions
      preemerging: Reductions are absent or show no awareness of the individual combinator rules.
      beginning: Most reductions reach correct results but steps are skipped or combinator rules are misapplied.
      progressing: All reductions are correct with one rule applied per line, redexes identified, and intermediate terms shown completely.
      proficient: Reductions are correct and annotated with rule names; the report states which combinator fired at each step; reduction paths that branch (multiple redexes available) note the choice made and confirm confluence holds for the examples.
    - weight: 25
      description: Combinator Reducer Implementation
      preemerging: The reducer does not run or cannot reduce I applied to an argument.
      beginning: I, K, S rules are implemented and reduce simple expressions, but the interpreter loops on terms with more than one redex and no strategy is defined.
      progressing: All seven birds (I, K, S, B, C, W, M) are implemented; outermost-first reduction (normal order analog) is used; a step limit prevents divergence; exceptions are caught and reported with location prefix.
      proficient: Strategy is selectable (outermost-first vs. innermost-first) via a JSON config; the reducer detects and reports a normal form; the diverging terms M(M) and omega are handled gracefully (step limit exceeded, not a crash); a trace mode shows each reduction step.
    - weight: 20
      description: Point-Free Implementations
      preemerging: Less than two point-free implementations are correct.
      beginning: At least three of five point-free implementations are correct and tested.
      progressing: All five are correct, tested on at least three inputs each, and the combinator expression for each is stated alongside the Python code.
      proficient: All five are correct and tested; each includes both the combinator-calculus expression (e.g., B (B succ) zero) and the Python code; a sixth point-free function of the student's own design is included with a motivation.
    - weight: 15
      description: Bracket Abstraction Translator
      preemerging: The translator is absent or applies only one of the three abstraction rules.
      beginning: The translator handles simple cases but fails on nested applications where the variable appears in both subterms.
      progressing: All three rules are implemented correctly; the translator correctly handles variables that do and do not appear free in a term; the output is verified by reducing translated terms to the same result as the original lambda term.
      proficient: The translator is implemented and tested; the output is reduced by the combinator reducer and compared to the interpreter's result on the same lambda term; known expansion blowup (SKI expressions are exponentially larger) is measured and discussed.
    - weight: 15
      description: Analysis and Connections
      preemerging: Analysis questions are not answered.
      beginning: Answers restate module content without engaging the student's own implementations.
      progressing: Answers are specific and cite the student's own code and reduction transcripts as evidence.
      proficient: Answers are precise, cite specific terms and transcripts, connect the birds to Haskell point-free style and to the lambda calculus fixed-point theorem, and include an original observation about a design tradeoff the student encountered.

tags:
  - combinators
  - lambda-calculus
  - functional-programming
  - theory
  - point-free
---

## Assignment: A Flock of Functions — Combinatory Logic in Code

Raymond Smullyan named every combinator after a bird; Gabriel Lebec showed every bird is a function you already use. In this assignment you will meet the whole flock, reduce their expressions by hand, implement a machine that reduces them automatically, and discover that an entire programming language can be built from S and K alone — no variables, no binding, just two birds and application.

---

### Part 1: Hand Reductions (25 points)

Reduce each expression to normal form, one combinator rule per line. At each step, underline or box the redex you are contracting and write the rule name beside the step (e.g., "K rule", "S rule").

*Recall the rules:*

$$
\mathbf{I}\ a \Rightarrow a \qquad
\mathbf{K}\ a\ b \Rightarrow a \qquad
\mathbf{S}\ f\ g\ x \Rightarrow f\ x\ (g\ x)
$$
$$
\mathbf{B}\ f\ g\ x \Rightarrow f\ (g\ x) \qquad
\mathbf{C}\ f\ a\ b \Rightarrow f\ b\ a \qquad
\mathbf{W}\ f\ x \Rightarrow f\ x\ x
$$

**(a)** $\mathbf{K}\ \mathbf{I}\ a\ b$ — identify which standard function this is.

**(b)** $\mathbf{S}\ \mathbf{K}\ \mathbf{K}\ 42$ — what is the result, and what well-known combinator is $\mathbf{S}\ \mathbf{K}\ \mathbf{K}$?

**(c)** $\mathbf{B}\ f\ (\mathbf{B}\ g\ h)\ x$ and $\mathbf{B}\ (\mathbf{B}\ f\ g)\ h\ x$ — reduce both and confirm they produce $f\ (g\ (h\ x))$. This is **associativity of composition**.

**(d)** $\mathbf{C}\ (\mathbf{B}\ f\ g)\ a\ b$ — reduce to normal form. What two-argument function does $\mathbf{C}\ (\mathbf{B}\ f\ g)$ represent?

**(e)** $\mathbf{W}\ (\mathbf{K}\ a)$ — reduce; describe the result in English (what does this function do to any argument?).

**(f)** $\mathbf{S}\ (\mathbf{K}\ \mathbf{S})\ \mathbf{K}\ f\ g\ x$ — reduce fully and identify the result as one of the named birds.

---

### Part 2: Combinator Reducer (25 points)

Implement, in Python, a combinator term reducer supporting the birds I, K, S, B, C, W, and M.

**AST.** Represent terms as: `Prim(name)` for a primitive combinator, `App(rator, rand)` for application. Application is left-associative, so `S K K` is `App(App(Prim("S"), Prim("K")), Prim("K"))`.

**Reduction strategy.** Implement outermost-first (normal-order analog) as the default: always reduce the leftmost, outermost redex. A redex for `K` is any `App(App(Prim("K"), a), b)`; for `S` it is `App(App(App(Prim("S"), f), g), x)`, etc. Implement innermost-first as an option (selectable via JSON config).

**Configuration.** Read from `config.json`: `strategy` (`"outermost"` or `"innermost"`), `max_steps` (integer, default 1000), `trace` (boolean, default false). If trace is true, print each intermediate term.

**Step limit.** If no normal form is reached within `max_steps` steps, print a diagnostic (include `[reducer:run]` prefix) and stop; do not crash.

**Verification.** Demonstrate your reducer on:
- $\mathbf{I}\ 42$ → $42$
- $\mathbf{K}\ \mathbf{I}\ a\ b$ → $b$ (where $a$ and $b$ are `Prim("a")` and `Prim("b")`)
- $\mathbf{S}\ \mathbf{K}\ \mathbf{K}\ x$ → $x$
- $\mathbf{B}\ f\ g\ x$ → $f\ (g\ x)$ (with $f$, $g$, $x$ as primitives representing opaque functions)
- The term $\mathbf{M}\ \mathbf{M}$ — confirm step limit fires and reports gracefully

---

### Part 3: Point-Free Implementations (20 points)

Using the birds as Python callables (as in the module code), implement the following five functions in **point-free style** — that is, using only the bird combinators and composition, with no `lambda`, no `def`, no named parameter variables in the definition of the function itself.

For each: (1) write the combinator expression (e.g., $\mathbf{B}\ f\ g$); (2) translate it to Python using the birds; (3) demonstrate it on at least three inputs.

1. `double_then_negate`: given a number, double it and negate it.
2. `apply_twice(f)`: a function that returns a new function applying `f` twice. (Hint: which bird duplicates?)
3. `swap_args(f)`: given a two-argument curried function `f`, return a new function with arguments swapped. (One bird does exactly this.)
4. `on(f, g)`: apply `g` to both arguments, then apply `f` to the results. i.e., `on(f, g)(a)(b) = f(g(a))(g(b))`. (This is the **Psi** bird: $\Psi$.)
5. `const_function(x)`: return a function that ignores its argument and always returns `x`. (The pure Kestrel.)

---

### Part 4: Bracket Abstraction Translator (15 points)

Implement the bracket abstraction algorithm that translates a lambda term (represented as a simple Python AST with `LamVar`, `LamAbs`, `LamApp` nodes) to an equivalent SKI combinator expression.

The three rules (Section 9 of the module):

$$
[x]\, x = \mathbf{I}
$$
$$
[x]\, e = \mathbf{K}\, e \quad (x \notin \mathrm{FV}(e))
$$
$$
[x]\, (e_1\ e_2) = \mathbf{S}\, ([x]\, e_1)\, ([x]\, e_2) \quad (x \in \mathrm{FV}(e_1 e_2))
$$

Apply $[x]$ for every lambda, outermost first, until no lambdas remain.

**Verification:** Translate $\lambda x.\ x$ to SKI and verify your reducer produces $y$ when applied to any $y$. Translate $\lambda f.\ \lambda x.\ f\ x$ and verify it behaves as identity on functions. Translate $\lambda x.\ \lambda y.\ x$ (the Kestrel) and verify it returns its first argument.

**Size analysis.** Measure the size (number of nodes) of the SKI expression for $\lambda x.\ \lambda y.\ x\ y$ versus the lambda term itself. Comment on the expansion ratio and explain why this matters for real combinator compilers (the Turner algorithm paper in Further Reading optimizes this).

---

### Part 5: Analysis Questions (15 points)

Answer each in a paragraph of 5–10 sentences, citing your own code and reduction transcripts as evidence.

1. **SKI Turing completeness.** The Church-Turing thesis says that any computable function is computable in the lambda calculus. The lambda calculus can be translated to SKI combinators by bracket abstraction. Therefore, any computable function can be computed with only S, K, and application — no variables whatsoever. What does this imply about the *minimum syntactic complexity* required for universal computation? Why is this philosophically surprising?

2. **Point-free style: when it helps, when it hurts.** Your point-free implementations from Part 3 have no parameter names. Compare the readability of your point-free `double_then_negate` to its point-full equivalent `lambda x: -(x * 2)`. In what circumstances does point-free style improve code quality, and in what circumstances does it harm it? Use examples from both your Part 3 implementations and from real Haskell code you have encountered.

3. **Combinators and closures.** Your tree-walking interpreter from the interpreter assignment uses environments (dictionaries) to implement closures. Combinatory logic has no environments and no closures — yet it computes the same functions. Explain precisely how the combinator S *replaces* the role of an environment in the lambda calculus, using the S rule $\mathbf{S}\ f\ g\ x = f\ x\ (g\ x)$ as your example.

---

### Deliverables

- **A written document** (PDF) containing all hand reductions (Part 1), verification output (Part 2), combinator expressions and demonstrations (Part 3), size analysis (Part 4), and analysis answers (Part 5).
- **Python source** for the combinator reducer (Part 2), the point-free implementations (Part 3), and the bracket abstraction translator (Part 4), each in its own file with a `README` showing how to reproduce every transcript.
- **A `config.json`** for the reducer with your preferred default settings.
- A transcript file showing the reducer operating on all required inputs, including the diverging `M M` case.

Ensure reproducibility: list Python version; every transcript must be regenerable with a single documented command.

---

### Submission Instructions

Submit a single ZIP to the course LMS. Did you work with a buddy on this assignment? If so, who? If not, do you certify that this submission represents your own original work? Identify any portions not originally written by you.

Approximately how many hours did this assignment take?

---

### Reflection Prompts

- You implemented the same computation three ways: as a tree-walking interpreter (previous assignment), as Python lambdas using the bird combinators, and as a term reducer on a combinator AST. What changed, what stayed the same, and which representation made you think differently about the underlying computation?
- The birds are named after birds because Raymond Smullyan wrote a puzzle book where a wise bird teaches a logician about forests full of combinators. Does the metaphor help or hinder your intuition? What alternative metaphor would you use to teach a newcomer the K combinator?
- Gabriel Lebec's 2016 talk ends with: "This is not just a historical curiosity — it is the abstract pattern underlying every higher-order function you will ever write." Based on your work in this assignment, do you agree? Write one sentence that either defends or challenges this claim.

---

### Resources

- The in-class module "Flock of Birds: Combinatory Logic and the SKI Calculus."
- Smullyan, Raymond. *To Mock a Mockingbird* (Knopf, 1985). The source of the bird names; the puzzles are delightful and directly relevant.
- Lebec, Gabriel. "A Flock of Functions." London Functional Programmers Meetup, 2016. Watch before Part 3; the JavaScript implementations map directly to your Python birds.
- Hindley, J. Roger and Jonathan P. Seldin. *Lambda-Calculus and Combinators: An Introduction* (Cambridge UP, 2008). Chapters 2–3 for bracket abstraction theory.
- Turner, David. "Another Algorithm for Bracket Abstraction." *Journal of Symbolic Logic* 44(2), 1979. The optimized algorithm referenced in Part 4.
