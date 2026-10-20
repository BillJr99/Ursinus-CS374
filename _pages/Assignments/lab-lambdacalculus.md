---
layout: assignment
permalink: /Assignments/LambdaCalculusLab
title: "CS374: Principles of Programming Languages - Lab: Lambda Calculus"

info:
  coursenum: CS374
  purpose: "To evaluate lambda calculus expressions by hand, individually or with a partner, working beta reduction with capture-avoiding substitution and Church encodings of booleans and numerals, which are the theory floor beneath functional programming."
  tilt:
    task: "Individually or with a partner, carry out step-by-step beta reductions including a capture-avoidance case, and verify Church-encoded booleans and numerals by reduction."
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
    - rtitle: "Lambda Calculus II and Closures Activity"
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

In this lab you (alone or with a partner) evaluate lambda calculus expressions by hand, the way the Lambda Calculus class sessions do at the board.  It is entirely on paper.  You leave with a page of reductions carried out one step at a time, a capture case you handled by renaming a bound variable, and Church-encoded booleans and numerals you verified by reduction rather than by trust.  No later assignment imports this lab, but it prepares you for the Functional Programming assignment's Direction C (Church encodings in code, where these reductions become the test cases your reducer has to reproduce) and for the closures material, where "a function that captures a variable" stops being mysterious once you have alpha-renamed by hand.  Work the reductions slowly; rushing them defeats the purpose.

**Pair policy.**  You may do this lab in pairs.  Reduce independently, then reconcile line by line; the disagreements are where the learning is.  Hand in one document between you, each naming the other, and you both receive the same grade.  You may also do this alone; if you do, redo each reduction independently after a break and reconcile it against your first attempt.

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

Everything you hand in lives in one file, `reductions.md`, or in one set of photographed pages if you write by hand.  Every item gets its own heading, so I can find item 4 of Part 1 without hunting.

**You write:** `reductions.md` - your name (and your partner's) on the first line, then the empty headings shown below.

> **Do this.**
> 1. Create a folder named `cs374-lambda` (File, Open Folder in VS Code, or the two commands below).
> 2. **Typed route:** create `reductions.md` inside it.  Put your name (and your partner's, if you worked in a pair) on the first line, then the headings `## Part 0`, `## Part 1`, and `## Part 2`, each with `### Item 1`, `### Item 2`, and so on for its items, plus `### Least-confident step` under Part 0.  The skeleton below has every heading in order; copy it in.
> 3. **Handwritten route:** write both names at the top of the first sheet and label every part and item number the same way, so I can find item 4 of Part 1 without hunting.  When done, photograph each page in good light with the page filling the frame, confirm every symbol is readable, and hand in one `reductions.pdf` with the pages in order (or `reductions-1.jpg`, `reductions-2.jpg`, and so on).

```bash
mkdir cs374-lambda
cd cs374-lambda
```

Here is the skeleton of `reductions.md`.  Replace the angle-bracket text on the first line, and leave the headings exactly as they are.

```markdown
<Your name> and <your partner's name>   (or: <Your name>, worked alone)

## Part 0

### Item 1

### Item 2

### Least-confident step

## Part 1

### Item 1

### Item 2

### Item 3

### Item 4

### Item 5

## Part 2

### Item 1

### Item 2

### Item 3

### Item 4
```

This table shows which heading each step fills, so you always know where your next line goes.  On paper, the same labels go in the margin.

| Step | File you work in | What you do there |
|---|---|---|
| Worked reduction | scratch paper (not submitted) | practice the line format on a term that is already worked for you |
| 0.1 | `reductions.md`, first line | both names, or "worked alone" |
| 0.3 | `reductions.md`, `## Part 0` > `### Item 1` | reduce a term to normal form, then a term that never gets there |
| 0.4 | `reductions.md`, `## Part 0` > `### Item 2` | verify $$\text{SUCC}\ \text{ZERO}$$ by reduction |
| 0.5 | `reductions.md`, `## Part 0` > `### Least-confident step` | point to your shakiest step and say why |
| 1.1 to 1.5 | `reductions.md`, `## Part 1` > `### Item 1` to `### Item 5` | one reduction per item; item 4 is the capture case, item 5 adds the evaluation-order table |
| 2.1 to 2.3 | `reductions.md`, `## Part 2` > `### Item 1` to `### Item 3` | one Church-encoding verification per item |
| 2.4 | `reductions.md`, `## Part 2` > `### Item 4` | the short closing answer |

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
| A constant such as $$z + 1$$ or $$0$$ | `z + 1` and `0`, typed as they are (Part 1 item 3 treats $$+$$ and numerals as constants, not redexes) |
| A wider gap after an arrow, as in the worked reduction | `\quad` |

For example, `$$\underline{(\lambda x.\, x)\ y} \to_\beta y$$` renders as $$\underline{(\lambda x.\, x)\ y} \to_\beta y$$.

> **Time budget.**  Two to three hours, most of it in one sitting (with your partner, if you have one): about half an hour for Part 0 and an hour each for Parts 1 and 2, with the reconciliation inside those.

---

## Refresher on the Lambda Calculus

This section collects the notation, the line format, and the Church encodings that every part of the lab uses.  Read it before Part 0, and come back to it whenever a later step points here.

### Notation and a Worked Reduction

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

### A Template to Copy

Every item in Parts 0, 1, and 2 uses this layout.  Copy it under the item's heading, then replace each angle-bracket placeholder.  Each pair of lines answers three questions: what is the term now, which redex did I contract, and which rule did I use?

```markdown
$$\underline{<the first redex>}\ <the rest of the starting term>$$

Start: <which subterm is the redex, and why it is the one you contract>.

$$\to_\beta \quad <the new term, with the next redex underlined>$$

Step 1: substitute <the argument> for <the bound variable> in the body <the body>.  No capture, because <reason>.

$$\to_\alpha \quad <the same term, with one binder and its uses renamed>$$

Step 2 (alpha, only when needed): rename <old binder> to <fresh name>, because <the free variable> would otherwise be captured.

$$\to_\beta \quad <the term after the next substitution>$$

Step 3: substitute <the argument> for <the bound variable> in the body <the body>.  No redex remains, so this is the normal form.
```

Number the steps in order, counting alpha steps too, so you can point to "Step 3" later.  Repeat the beta pair as many times as the reduction needs, and leave out the alpha pair when no capture threatens.  On paper, use the same layout: one term per line, the redex underlined in your second color, and the step phrase underneath.

Work the reduction above yourself before you start Part 0, so the format is settled on a term you have already seen worked.

**You write (on scratch paper, which you do not submit):** the three-step reduction below, in the template's layout.

> **Do this.**
> 1. Read the worked reduction above once, start to finish, without writing anything.
> 2. Cover it and reduce $$(\lambda x.\, \lambda y.\, y\ x)\ a\ (\lambda z.\, z)$$ yourself on paper: one beta-step per line, the redex underlined on every line, and a phrase after each line saying what you substituted for what.
> 3. Uncover the worked version and compare line by line.  You should match it step for step: three beta-steps, ending at $$a$$.  If you ended somewhere else, the usual cause is reading $$f\ a\ b$$ as $$f\ (a\ b)$$; reread the left-associativity convention above and try again before you move on.

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

## Part 0: Before You Start - Beta Reduction and Church Encodings

Do this part first.  Beta reduction is a rewriting rule, and you learn it by applying it slowly and recording each step.  Two reductions will do: one that reaches a normal form, and one that never will.  Use the template from *A Template to Copy* for every sequence.

### Step 0.3: Reduce a Term That Stops and a Term That Does Not

The first term has the same shape as the term in the worked reduction, so lean on that example.  The second is the classic term with no normal form.

**You write (in `reductions.md` under a `### Item 1` heading in `## Part 0`):** two reduction sequences in the template's layout, then a few sentences about the second one.

> **Do this.**
> 1. Beta-reduce $$(\lambda x.\, \lambda y.\, x)\ a\ b$$ to normal form, showing each step; it has the same shape as the term in the worked reduction above.  Your last line should contain no redex.
> 2. Then try $$(\lambda x.\, x\ x)\ (\lambda x.\, x\ x)$$: reduce it far enough to show why it never terminates, and explain what happens.

> **If you get stuck.**
> - Your first step contracted $$a\ b$$, or applied the lambda to $$b$$.  Application is left-associative.  Write in the parentheses that convention implies before you pick a redex, as the worked reduction does in its Start line.
> - You replaced only one $$x$$ in $$x\ x$$.  A beta-step replaces every occurrence of the bound variable in the body, all at once.
> - You worried that the two binders named $$x$$ clash.  Two binders that share a name are still separate binders.  Capture needs a free variable in the argument, so list the argument's free variables before you decide whether an alpha step is needed.

### Step 0.4: Verify SUCC ZERO by Reduction

**You write (in `reductions.md` under a `### Item 2` heading in `## Part 0`):** the definitions of $$\text{SUCC}$$ and $$\text{ZERO}$$ written out, then one reduction sequence that ends at a term matching $$\text{ONE}$$.

> **Do this.**
> 1. Using the Church encodings from the reading, verify by reduction that $$\text{SUCC}\ \text{ZERO}$$ behaves like $$\text{ONE}$$.  Write out both definitions in full first, then reduce until the result matches $$\text{ONE}$$ up to the names of bound variables.

> **If you get stuck.**
> - You substituted the name $$\text{ZERO}$$ as if it were a variable.  A name is an abbreviation: write its definition, in parentheses, wherever the name appears, and reduce that.
> - You stopped while a redex was still inside the body of a lambda.  In this lab you keep reducing inside lambda bodies until no redex remains anywhere.  A redex under a binder still counts.
> - The $$f$$ and $$x$$ of $$\text{SUCC}$$ and the $$f$$ and $$x$$ of $$\text{ZERO}$$ blur together.  They are different variables that happen to share names.  If it helps, rename $$\text{ZERO}$$'s binders to fresh names on an $$\to_\alpha$$ line of their own before you substitute.  That is always legal here, because $$\text{ZERO}$$ has no free variables.

### Step 0.5: Mark Your Least-Confident Step

**You write (in `reductions.md` under the `### Least-confident step` heading in `## Part 0`):** where your shakiest step is, the line itself, and one sentence.

> **Do this.**
> 1. Under `### Least-confident step`, mark the step you were least confident was legal: circle it on paper, or write `<-- least confident` after it in the file, and add one sentence saying what made you unsure.

In the file, put `<-- least confident` at the end of that step's "Step k:" phrase, not inside the `$$...$$`, so the term still renders.  Then, under the heading, say where the step is by part, item, and step number, such as `Part 0, Item 2, Step 3`, and copy its term line below that.  On paper, circle the step and write the same part, item, and step number under the heading.

> **Bring to class.**  Your least-confident step.  Those are the steps we work through at the board, and capture-avoiding substitution (Part 1) is usually the reason one felt wrong.

---

## Part 1: Beta Reduction

Reduce each expression below to normal form, one beta-step per line, with the redex you contract underlined or bracketed on every line.  Before each step, compare the argument's free variables with the binder you are about to substitute under; if a name appears in both places, alpha-rename the binder first.  Item 4 is the one place in this lab where the obvious move is wrong, and the rubric row for this part turns on whether you renamed or captured.

> **Do this.**  Under `## Part 1`, one item per heading, as in Steps 1.1 to 1.5 below.

### Step 1.1: The Identity

**You write (in `reductions.md` under a `### Item 1` heading in `## Part 1`):** one reduction sequence.

> **Do this.**
> 1. Reduce $$(\lambda x.\, x)\ y$$.

### Step 1.2: Two Arguments

**You write (in `reductions.md` under a `### Item 2` heading in `## Part 1`):** one reduction sequence.

This is the first term from Part 0, Item 1.  Reduce it again here, in full, so that Part 1 stands on its own.

> **Do this.**
> 1. Reduce $$(\lambda x.\, \lambda y.\, x)\ a\ b$$.

### Step 1.3: A Reduction With Constants

**You write (in `reductions.md` under a `### Item 3` heading in `## Part 1`):** one reduction sequence, plus an optional arithmetic line at the end.

> **Do this.**
> 1. Reduce $$(\lambda f.\, \lambda x.\, f\ (f\ x))\ (\lambda z.\, z + 1)\ 0$$.  Treat $$+$$ and the numerals as constants: they are not redexes, and $$0 + 1$$ stays written as $$0 + 1$$ (you may simplify the arithmetic after the last beta-step).

If you simplify the arithmetic, put it on its own line after the last beta-step and write it with $$=$$, not $$\to_\beta$$, because it is not a beta-step.

> **If you get stuck.**
> - You underlined $$z + 1$$ or $$0 + 1$$ as a redex.  Only a lambda applied to an argument is a redex; $$+$$ is a constant.
> - Your term lost its shape after you substituted a lambda into a body.  Keep any substituted lambda in parentheses everywhere it lands.  Without them, the lambda's body swallows everything to its right.
> - You see two redexes and are unsure which to pick.  Either choice reaches the same normal form on this term.  Contracting the leftmost outermost one first is a good habit, and it is the order Item 5 asks about.

### Step 1.4: The Capture Case

Here the obvious substitution is wrong.  Before you write anything, run this check on the redex:

1. List the free variables of the argument.
2. List the binders inside the body that the substitution would pass under.
3. If a name is on both lists, rename that binder (and every use of it) to a fresh name that appears nowhere else in the term.

**You write (in `reductions.md` under a `### Item 4` heading in `## Part 1`):** an $$\to_\alpha$$ line, then the beta-step, then one sentence about what would have gone wrong.

> **Do this.**
> 1. **The capture case:** reduce $$(\lambda x.\, \lambda y.\, x)\ y$$.  Blind substitution captures the free $$y$$.  Alpha-rename first, show the renaming as its own $$\to_\alpha$$ line, and add one sentence explaining what would have gone wrong without it.

Check your final term: the $$y$$ that came in as the argument is free, so it must still be free at the end.

> **If you get stuck.**
> - Your final term binds the $$y$$ that came from the argument.  That is capture.  Go back, and do the alpha step before the beta-step.
> - You renamed the free $$y$$ instead of the bound one.  Only a bound variable may be renamed; a free variable refers to something outside the term.
> - You renamed and substituted on one line.  The renaming is its own $$\to_\alpha$$ line, and the substitution is the next $$\to_\beta$$ line.

### Step 1.5: Divergence and Evaluation Order

**You write (in `reductions.md` under a `### Item 5` heading in `## Part 1`):** three beta-steps with a sentence about termination, then the two-column table below for the second term, then your answer.

> **Do this.**
> 1. Reduce $$(\lambda x.\, x\ x)\ (\lambda x.\, x\ x)$$ three steps, then state what this term tells you about termination.
> 2. Then answer: given $$(\lambda x.\, z)\ ((\lambda x.\, x\ x)\ (\lambda x.\, x\ x))$$, which evaluation order (normal or applicative) terminates, and what does that imply about lazy evaluation?  Normal order reduces the leftmost outermost redex first; applicative order reduces arguments before applying the function.  Work the term both ways on paper, a few steps each, before you write the answer.

Work the two orders side by side in this table, one row per beta-step.  Underline, in each cell, the redex that column's rule picks.  Stop a column when it reaches a normal form, or after four rows if it has not.  Write your answer in a few sentences below the table.

```markdown
| Step | Normal order (leftmost outermost first) | Applicative order (arguments first) |
|------|-----------------------------------------|-------------------------------------|
| 0 | $$<the starting term, this rule's redex underlined>$$ | $$<the starting term, this rule's redex underlined>$$ |
| 1 | $$\to_\beta \quad <term>$$ | $$\to_\beta \quad <term>$$ |
| 2 | $$\to_\beta \quad <term>$$ | $$\to_\beta \quad <term>$$ |
| 3 | <a term, or "normal form reached"> | <a term, or "normal form reached"> |
```

On paper, draw two columns with the same labels.

> **If you get stuck.**
> - You switched rules partway down a column.  Each column follows its own rule on every row.  Decide which redex the rule picks before you write the row.
> - In the normal-order column you started inside the argument.  The leftmost outermost redex is the one that is not inside any other redex and whose $$\lambda$$ starts farthest to the left.
> - You only see one redex in the starting term.  Check every parenthesized subterm, the argument included, and ask whether it is a lambda applied to something.

---

## Part 2: Church Encodings

When an item names an encoding from the table above, write its definition in full as your first line, then reduce; a name is an abbreviation, not a redex.  Two terms are alpha-equivalent when they differ only in the names of bound variables, so a verification succeeds when your complete sequence ends at a term matching the expected one after renaming, not when you claim it would.

> **Do this.**  Under `## Part 2`, one item per heading, as in Steps 2.1 to 2.4 below.

> **If you get stuck (all of Part 2).**
> - Your first line runs the definitions together.  Wrap each expanded definition in its own parentheses, so a term like $$\text{AND}\ \text{TRUE}\ \text{FALSE}$$ becomes three parenthesized terms side by side.  Without the parentheses, the first lambda's body swallows the rest.
> - You worried that a binder named $$f$$ inside the argument clashes with a binder named $$f$$ in the body.  Capture is only about the argument's *free* variables, and the encodings in the table have none.  An alpha step is optional here, but it can make the names easier to follow.
> - A definition now appears twice in your term.  Each copy is its own term.  Contract one redex per line and leave the other copy alone until a redex reaches it.
> - You stopped with a redex still inside a lambda body.  As in Part 0, keep going until no redex remains anywhere.

### Step 2.1: AND TRUE FALSE

**You write (in `reductions.md` under a `### Item 1` heading in `## Part 2`):** one reduction sequence, starting from the expanded definitions.

> **Do this.**
> 1. Verify that $$\text{AND}\ \text{TRUE}\ \text{FALSE}$$ reduces to $$\text{FALSE}$$, showing every step.  Your first line expands all three names to their definitions.

### Step 2.2: AND TRUE TRUE

**You write (in `reductions.md` under a `### Item 2` heading in `## Part 2`):** one reduction sequence, starting from the expanded definitions.

> **Do this.**
> 1. Verify that $$\text{AND}\ \text{TRUE}\ \text{TRUE}$$ reduces to $$\text{TRUE}$$.

### Step 2.3: SUCC ONE

**You write (in `reductions.md` under a `### Item 3` heading in `## Part 2`):** one reduction sequence, plus a final $$\to_\alpha$$ line if your binder names differ from $$\text{TWO}$$.

> **Do this.**
> 1. Verify that $$\text{SUCC}\ \text{ONE}$$ reduces to a term alpha-equivalent to $$\text{TWO} = \lambda f.\, \lambda x.\, f\ (f\ x)$$.  If your final term has different binder names from $$\text{TWO}$$, add one $$\to_\alpha$$ line that renames them and ends exactly at $$\text{TWO}$$.

This is the same pattern as Part 0, Item 2, one numeral higher.  If that reduction went well, follow the same moves here.

### Step 2.4: The Closing Answer

**You write (in `reductions.md` under a `### Item 4` heading in `## Part 2`):** a short paragraph.  No reductions.

> **Do this.**
> 1. Close with a short answer: a Church numeral *is* a higher-order function, "apply $$f$$, $$n$$ times."  Name the Python or Scheme idiom from the Functional Programming sessions that does exactly this, and one place your team language or interpreter could use the same trick.

Two things are required: a specific idiom by name, and a specific place in your team language or interpreter.  A few sentences are sufficient.

---

## Deliverables

| File or artifact | What it shows | Rubric row |
|------------------|---------------|------------|
| `## Part 0` section of `reductions.md` (or `reductions.pdf`) | Both Part 0 reductions step by step, the non-terminating case explained, $$\text{SUCC}\ \text{ZERO}$$ verified, and the least-confident step marked | Part 0: Before You Start |
| `## Part 1` section | Five reductions, one beta-step per line with the redex marked, the capture case alpha-renamed with a sentence, and the evaluation-order answer with the divergence example | Beta Reduction (Goal 1) |
| `## Part 2` section | Three complete verifications ending at the expected term, and the closing answer connecting Church numerals to a higher-order-function idiom | Church Encodings (Goals 2, 3) |
| Your name (and your partner's, if you worked in a pair) on the first line | Who did the work; partners receive the same grade | All rows |

---

## Self-Check Before You Submit

- [ ] Both partners are named at the top (or "worked alone" is written there).
- [ ] Every heading from the Step 0.1 skeleton is present, in order, with its item under it.
- [ ] Every reduction is one beta-step per line, with no two steps folded into one.
- [ ] The redex is underlined or bracketed on every line, not only the first.
- [ ] Part 1 item 4 has a $$\to_\alpha$$ line before the substitution, plus one sentence saying what capture would have done.
- [ ] Part 1 item 5 says which evaluation order terminates on the divergence example and what that implies about lazy evaluation.
- [ ] Every Part 2 verification starts from the expanded definitions and ends at the expected term, with a renaming line under item 3 if the binder names differ from $$\text{TWO}$$.
- [ ] Part 2 item 4 names a specific idiom from the Functional Programming sessions and a specific place in your team language or interpreter.
- [ ] The least-confident step from Part 0 is marked, and, if handwritten, every photo is readable.

---

## Reflection Prompts

- Which reduction did you and your partner disagree on, and what settled it?  Or, if you worked alone, which reduction did you have to redo, and what settled it?
- If you worked in a pair, note who did what.  If you worked alone, note that instead.
