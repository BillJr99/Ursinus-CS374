---
layout: assignment
permalink: /Assignments/LambdaCalculusLab
title: "CS374: Principles of Programming Languages - Lab: Lambda Calculus"

info:
  coursenum: CS374
  purpose: "To evaluate lambda calculus expressions by hand with a partner, working beta reduction with capture-avoiding substitution and Church encodings of booleans and numerals, which are the theory floor beneath functional programming."
  tilt:
    task: "With a partner, carry out step-by-step beta reductions including a capture-avoidance case, and verify Church-encoded booleans and numerals by reduction."
    criteria: "I assess your work on correct, fully-shown reduction sequences and correct Church-encoding verifications.  Please read the rubric below for the details."
  points: 15
  goals:
    - To perform beta reduction step by step, identifying redexes and applying capture-avoiding substitution
    - To verify Church encodings of booleans and numerals by reduction
    - To connect lambda calculus to the closures and higher-order functions of the surrounding course
  rubric:
    - weight: 10
      description: "Part 0: Before You Start - Beta Reduction and Church Encodings"
      preemerging: No reductions are attempted
      beginning: A reduction is attempted but the steps are not shown individually
      progressing: Both reductions are carried out step by step, but the non-terminating case is not explained, or the SUCC ZERO verification is incomplete
      proficient: (lambda x. lambda y. x) a b is beta-reduced to normal form with every step written out; the self-application case is reduced far enough to show why it never terminates, and that is explained; SUCC ZERO is verified by reduction to behave like ONE; and the step you were least confident was legal is marked
    - weight: 50
      description: "Beta Reduction (Goal 1)"
      preemerging: Reductions are missing or skip directly to claimed answers with no steps
      beginning: Simple reductions are correct but the capture-avoidance case substitutes blindly, capturing the free variable
      progressing: All reductions are correct including the alpha-renaming, but redexes are not marked or one sequence skips steps
      proficient: Every reduction is shown one beta-step at a time with the redex underlined or bracketed at each step, the capture case is handled by explicit alpha-renaming with a sentence explaining why, and the normal-order vs. applicative-order question is answered with the divergence example
    - weight: 40
      description: "Church Encodings (Goals 2, 3)"
      preemerging: Encodings are stated but never verified by reduction
      beginning: The boolean verifications are shown but the numeral ones are missing or incorrect
      progressing: All verifications are shown with one reduction error, or the connection question is unanswered
      proficient: TRUE/FALSE/AND and successor-of-one are all verified by complete reduction sequences, and the closing question connects Church encoding to a concrete higher-order-function idiom from the Functional Programming sessions
  readings:
    - rtitle: "Lambda Calculus I Activity"
      rlink: "Activities/liascript-lambdacalculus1.md"
      liapage: true
    - rtitle: "Lambda Calculus II Activity"
      rlink: "Activities/liascript-lambdacalculus2.md"
      liapage: true
    - rtitle: "Supplemental Tutorial: Build a Lambda Calculus Reducer"
      rlink: "../Tutorials/LambdaCalculusReducer"

tags:
  - lambda-calculus
  - functional
  - theory
  - lab

---

In this lab you and a partner evaluate lambda calculus expressions by hand, the way the Lambda Calculus class sessions do at the board.  It is entirely on paper.  You leave with a page of reductions carried out one step at a time, a capture case you handled by renaming a bound variable, and Church-encoded booleans and numerals you verified by reduction rather than by trust.  No later assignment imports this lab, but it prepares you for the Functional Programming assignment's Direction C (Church encodings in code, where these reductions become the test cases your reducer has to reproduce) and for the closures material, where "a function that captures a variable" stops being mysterious once you have alpha-renamed by hand.  Work the reductions slowly; rushing them defeats the purpose.

**Pair policy.**  You may do this lab in pairs.  Reduce independently, then reconcile line by line; the disagreements are where the learning is.  Hand in one document between you, each naming the other, and you both receive the same grade.  You may also do this alone.

Five terms come up throughout:

- A *redex* is a subterm ready to reduce: a lambda applied to an argument, such as $$(\lambda x.\, x)\ y$$.
- *Beta reduction* contracts a redex by substituting the argument for the bound variable in the body.  One contraction is one beta-step.
- A term is in *normal form* when it contains no redexes.
- *Capture* happens when a free variable in the argument becomes bound by accident after substitution.
- *Alpha-renaming* changes a bound variable's name (with all its uses) to avoid capture.  It does not change the term's meaning.

---

## Before You Start

There is nothing to install.  You may hand in a typed Markdown file or a legible scan or photo of handwritten work; decide now, because the typed route needs a file and the handwritten route needs a camera.

- Work through the Lambda Calculus I and Lambda Calculus II activities listed under Readings above.  Every encoding this lab uses comes from them.
- Have pencil, paper, an eraser, and a second pen color for underlining redexes.
- If you type your submission, use VS Code or any plain-text editor; the [dev environment page]({{ site.baseurl }}/Tutorials/DevEnvironment) walks through installing one.  You do not need the terminal for this lab, but the [shell primer]({{ site.baseurl }}/Tutorials/ShellForLanguageDev) covers the two commands below if you want to make your folder that way.
- The [Build a Lambda Calculus Reducer tutorial]({{ site.baseurl }}/Tutorials/LambdaCalculusReducer) is optional.  This lab does not need it.

### Step 0.1: Set Up the Deliverable

> **Do this.**
> 1. Create a folder named `cs374-lambda` (File, Open Folder in VS Code, or the two commands below).
> 2. **Typed route:** create `reductions.md` inside it.  Put both partners' names on the first line, then the headings `## Part 0`, `## Part 1`, and `## Part 2`, each with `### Item 1`, `### Item 2`, and so on for its items, plus `### Least-confident step` under Part 0.
> 3. **Handwritten route:** write both names at the top of the first sheet and label every part and item number the same way, so I can find item 4 of Part 1 without hunting.  When done, photograph each page in good light with the page filling the frame, confirm every symbol is readable, and hand in one `reductions.pdf` with the pages in order (or `reductions-1.jpg`, `reductions-2.jpg`, and so on).

```bash
mkdir cs374-lambda
cd cs374-lambda
```

### Step 0.2: How to Type a Term

If you type, write every lambda term in display math: open with `$$`, type the term, close with `$$`, and put each beta-step on its own line.  A single `$` does not render on this site, and a term that does not render is a term I cannot grade.

| What you want | Type this inside `$$...$$` |
|---------------|----------------------------|
| The symbol $$\lambda$$ | `\lambda` |
| A binder and its body, $$\lambda x.\, x$$ | `\lambda x.\, x` (the `\,` adds a small space after the dot) |
| Application, $$f\ x$$ | `f\ x` (a backslash-space keeps the gap) |
| An underlined redex | `\underline{...}` around the redex |
| A beta-step arrow, $$\to_\beta$$ | `\to_\beta` |
| An alpha-renaming arrow, $$\to_\alpha$$ | `\to_\alpha` |
| A name like $$\text{TRUE}$$ | `\text{TRUE}` |

For example, `$$\underline{(\lambda x.\, x)\ y} \to_\beta y$$` renders as $$\underline{(\lambda x.\, x)\ y} \to_\beta y$$.

> **Time budget.**  Two to three hours, most of it in one sitting with your partner: about half an hour for Part 0 and an hour each for Parts 1 and 2, with the reconciliation inside those.

---

## Notation and a Worked Reduction

Two conventions from the readings do most of the work.  Application associates to the left, so $$f\ a\ b$$ means $$(f\ a)\ b$$.  The body of a lambda extends as far right as it can, so $$\lambda x.\, x\ y$$ means $$\lambda x.\, (x\ y)$$.  Here is a term that reduces to normal form in three steps, with the contracted redex underlined and a justification after each line.  This is the format I want to see in your work.

$$\underline{(\lambda x.\, \lambda y.\, y\ x)\ a}\ (\lambda z.\, z)$$

Start: application is left-associative, so the only redex is the underlined one.  The rightmost $$(\lambda z.\, z)$$ has nothing applied to it, so it is not a redex.

$$\to_\beta \quad \underline{(\lambda y.\, y\ a)\ (\lambda z.\, z)}$$

Step 1: substitute $$a$$ for $$x$$ in the body $$\lambda y.\, y\ x$$.  No capture, because $$a$$ contains no free $$y$$.

$$\to_\beta \quad \underline{(\lambda z.\, z)\ a}$$

Step 2: substitute $$(\lambda z.\, z)$$ for $$y$$ in the body $$y\ a$$.  No capture, because the body binds nothing.

$$\to_\beta \quad a$$

Step 3: substitute $$a$$ for $$z$$ in the body $$z$$.  The result has no redexes, so it is in normal form.

That is the whole format: one term per line, the redex underlined, the arrow labeled, and one phrase saying what was substituted for what and why no capture occurred.  When a capture would occur, add an alpha step first on a line of its own (this example is not from the lab):

$$\lambda y.\, y\ w \quad \to_\alpha \quad \lambda v.\, v\ w$$

The bound $$y$$ and every use of it become a fresh name $$v$$; the free $$w$$ is left alone, and the term means the same thing before and after.

### Church Booleans and Numerals

A Church encoding represents a value such as a boolean or a number as a lambda term, so the calculus needs no built-in data.  A boolean is a function that chooses one of its two arguments; a numeral $$n$$ is a function that applies its first argument $$n$$ times to its second.

| Name | Definition |
|------|------------|
| $$\text{TRUE}$$ | $$\lambda t.\, \lambda f.\, t$$ |
| $$\text{FALSE}$$ | $$\lambda t.\, \lambda f.\, f$$ |
| $$\text{AND}$$ | $$\lambda p.\, \lambda q.\, p\ q\ p$$ |
| $$\text{ZERO}$$ | $$\lambda f.\, \lambda x.\, x$$ |
| $$\text{ONE}$$ | $$\lambda f.\, \lambda x.\, f\ x$$ |
| $$\text{TWO}$$ | $$\lambda f.\, \lambda x.\, f\ (f\ x)$$ |
| $$\text{SUCC}$$ | $$\lambda n.\, \lambda f.\, \lambda x.\, f\ (n\ f\ x)$$ |

---

## Your First 15 Minutes

1. Read the worked reduction above once, start to finish, without writing anything.
2. Cover it and reduce $$(\lambda x.\, \lambda y.\, y\ x)\ a\ (\lambda z.\, z)$$ yourself on paper: one beta-step per line, the redex underlined on every line, and a phrase after each line saying what you substituted for what.
3. Uncover the worked version and compare line by line.  You should match it step for step: three beta-steps, ending at $$a$$.  If you ended somewhere else, the usual cause is reading $$f\ a\ b$$ as $$f\ (a\ b)$$; reread the left-associativity convention and try again before you move on.
4. Open `reductions.md` (or your first sheet) at `## Part 0` and start item 1.  It has the same shape as the term you just reduced.

---

## Part 0: Before You Start - Beta Reduction and Church Encodings

Do this part first.  Beta reduction is a rewriting rule, and you learn it by applying it slowly and recording each step.  Two reductions will do: one that reaches a normal form, and one that never will.

> **Do this.**  Under `## Part 0`, one item per heading:
> 1. Beta-reduce $$(\lambda x.\, \lambda y.\, x)\ a\ b$$ to normal form, showing each step.  Then try $$(\lambda x.\, x\ x)\ (\lambda x.\, x\ x)$$: reduce it far enough to show why it never terminates, and explain what happens.
> 2. Using the Church encodings from the reading, verify by reduction that $$\text{SUCC}\ \text{ZERO}$$ behaves like $$\text{ONE}$$.  Write out both definitions in full first, then reduce until the result matches $$\text{ONE}$$ up to the names of bound variables.
> 3. Under `### Least-confident step`, mark the step you were least confident was legal: circle it on paper, or write `<-- least confident` after it in the file, and add one sentence saying what made you unsure.

> **Bring to class.**  Your least-confident step.  Those are the steps we work through at the board, and capture-avoiding substitution (Part 1) is usually the reason one felt wrong.

---

## Part 1: Beta Reduction

Reduce each expression below to normal form, one beta-step per line, with the redex you contract underlined or bracketed on every line.  Before each step, compare the argument's free variables with the binder you are about to substitute under; if a name appears in both places, alpha-rename the binder first.  Item 4 is the one place in this lab where the obvious move is wrong, and the rubric row for this part turns on whether you renamed or captured.

> **Do this.**  Under `## Part 1`, one item per heading:
> 1. Reduce $$(\lambda x.\, x)\ y$$.
> 2. Reduce $$(\lambda x.\, \lambda y.\, x)\ a\ b$$.
> 3. Reduce $$(\lambda f.\, \lambda x.\, f\ (f\ x))\ (\lambda z.\, z + 1)\ 0$$.  Treat $$+$$ and the numerals as constants: they are not redexes, and $$0 + 1$$ stays written as $$0 + 1$$ (you may simplify the arithmetic after the last beta-step).
> 4. **The capture case:** reduce $$(\lambda x.\, \lambda y.\, x)\ y$$.  Blind substitution captures the free $$y$$.  Alpha-rename first, show the renaming as its own $$\to_\alpha$$ line, and add one sentence explaining what would have gone wrong without it.
> 5. Reduce $$(\lambda x.\, x\ x)\ (\lambda x.\, x\ x)$$ three steps, then state what this term tells you about termination.  Then answer: given $$(\lambda x.\, z)\ ((\lambda x.\, x\ x)\ (\lambda x.\, x\ x))$$, which evaluation order (normal or applicative) terminates, and what does that imply about lazy evaluation?  Normal order reduces the leftmost outermost redex first; applicative order reduces arguments before applying the function.  Work the term both ways on paper, a few steps each, before you write the answer.

---

## Part 2: Church Encodings

When an item names an encoding from the table above, write its definition in full as your first line, then reduce; a name is an abbreviation, not a redex.  Two terms are alpha-equivalent when they differ only in the names of bound variables, so a verification succeeds when your complete sequence ends at a term matching the expected one after renaming, not when you claim it would.

> **Do this.**  Under `## Part 2`, one item per heading:
> 1. Verify that $$\text{AND}\ \text{TRUE}\ \text{FALSE}$$ reduces to $$\text{FALSE}$$, showing every step.  Your first line expands all three names to their definitions.
> 2. Verify that $$\text{AND}\ \text{TRUE}\ \text{TRUE}$$ reduces to $$\text{TRUE}$$.
> 3. Verify that $$\text{SUCC}\ \text{ONE}$$ reduces to a term alpha-equivalent to $$\text{TWO} = \lambda f.\, \lambda x.\, f\ (f\ x)$$.  If your final term has different binder names from $$\text{TWO}$$, add one $$\to_\alpha$$ line that renames them and ends exactly at $$\text{TWO}$$.
> 4. Close with a short answer: a Church numeral *is* a higher-order function, "apply $$f$$, $$n$$ times."  Name the Python or Scheme idiom from the Functional Programming sessions that does exactly this, and one place your team language or interpreter could use the same trick.

---

## Deliverables

| File or artifact | What it shows | Rubric row |
|------------------|---------------|------------|
| `## Part 0` section of `reductions.md` (or `reductions.pdf`) | Both Part 0 reductions step by step, the non-terminating case explained, $$\text{SUCC}\ \text{ZERO}$$ verified, and the least-confident step marked | Part 0: Before You Start |
| `## Part 1` section | Five reductions, one beta-step per line with the redex marked, the capture case alpha-renamed with a sentence, and the evaluation-order answer with the divergence example | Beta Reduction (Goal 1) |
| `## Part 2` section | Three complete verifications ending at the expected term, and the closing answer connecting Church numerals to a higher-order-function idiom | Church Encodings (Goals 2, 3) |
| Partner names on the first line | Who did the work; both partners receive the same grade | All rows |

---

## Self-Check Before You Submit

- [ ] Both partners are named at the top (or "worked alone" is written there).
- [ ] Every reduction is one beta-step per line, with no two steps folded into one.
- [ ] The redex is underlined or bracketed on every line, not only the first.
- [ ] Part 1 item 4 has a $$\to_\alpha$$ line before the substitution, plus one sentence saying what capture would have done.
- [ ] Part 1 item 5 says which evaluation order terminates on the divergence example and what that implies about lazy evaluation.
- [ ] Every Part 2 verification starts from the expanded definitions and ends at the expected term, with a renaming line under item 3 if the binder names differ from $$\text{TWO}$$.
- [ ] Part 2 item 4 names a specific idiom from the Functional Programming sessions and a specific place in your team language or interpreter.
- [ ] The least-confident step from Part 0 is marked, and, if handwritten, every photo is readable.

---

## Reflection Prompts

- Which reduction did you and your partner disagree on, and what settled it?
- If you worked in a pair, who did what.  If you worked alone, note that instead.
