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

In this lab you (alone or with a partner) evaluate lambda calculus expressions by hand, the way the Lambda Calculus class sessions do at the board.  It is entirely on paper.  You leave with a page of reductions carried out one step at a time, a capture case you handled by renaming a bound variable, and Church-encoded booleans and numerals you verified by reduction rather than by trust.  This also prepares you for the closures material, where "a function that captures a variable" stops being mysterious once you have alpha-renamed by hand.

**Pair policy.**  You may do this lab in pairs.  Reduce independently, then reconcile line by line, because the disagreements are where the learning is.  Hand in one document between you, each naming the other, and you both receive the same grade.  You may also do this alone; if you do, redo each reduction independently after a break and reconcile it against your first attempt.

Five terms come up throughout:

- A *redex* is a subterm ready to reduce: a lambda applied to an argument, such as $$(\lambda x.\, x)\ y$$.
- *Beta reduction* contracts a redex by substituting the argument for the bound variable in the body.  One contraction is one beta-step.
- A term is in *normal form* when it contains no redexes.
- *Capture* happens when a free variable in the argument becomes bound by accident after substitution.
- *Alpha-renaming* changes a bound variable's name (with all its uses) to avoid capture.  It does not change the term's meaning.

---

## Before You Start

There is nothing to install.  Work through the Lambda Calculus I and II activities listed under Readings, because every encoding here comes from them.  Then choose how you will hand this in:

- **Typed:** download [reductions.md]({{ site.baseurl }}/files/starters/lambda/reductions.md), which already has every heading, the line template, and a cheat sheet for typing lambda terms.  Put your names on the first line, and fill in each item under its heading.
- **Handwritten:** write both names at the top, label every part and item the same way, and hand in one `reductions.pdf` with readable photos of the pages in order.

---

## Notation and a Worked Reduction

Two conventions do most of the work.  Application associates to the left, so $$f\ a\ b$$ means $$(f\ a)\ b$$.  The body of a lambda extends as far right as it can, so $$\lambda x.\, x\ y$$ means $$\lambda x.\, (x\ y)$$.  Here is a term that reduces to normal form in three steps, with the contracted redex underlined and a reason after each line.  This is the format I want to see in your work, because the reason is what shows the step is legal.

$$\underline{(\lambda x.\, \lambda y.\, y\ x)\ a}\ (\lambda z.\, z)$$

Start: application is left-associative, so the only redex is the underlined one.  The rightmost $$(\lambda z.\, z)$$ has nothing applied to it, so it is not a redex.

$$\to_\beta \quad \underline{(\lambda y.\, y\ a)\ (\lambda z.\, z)}$$

Step 1: substitute $$a$$ for $$x$$ in the body $$\lambda y.\, y\ x$$.  No capture, because $$a$$ contains no free $$y$$.

$$\to_\beta \quad \underline{(\lambda z.\, z)\ a}$$

Step 2: substitute $$(\lambda z.\, z)$$ for $$y$$ in the body $$y\ a$$.  No capture, because the body binds nothing.

$$\to_\beta \quad a$$

Step 3: substitute $$a$$ for $$z$$ in the body $$z$$.  The result has no redexes, so it is in normal form.

When a capture would occur, add an alpha step first, on a line of its own:

$$\lambda y.\, y\ w \quad \to_\alpha \quad \lambda v.\, v\ w$$

The bound $$y$$ and every use of it become a fresh name $$v$$, and the free $$w$$ is left alone.  [Slide 11 of the Lambda Calculus I activity](https://liascript.github.io/course/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374-Fall2026/gh-pages/_pages/Activities/liascript-lambdacalculus1.md#11) explains beta reduction, and [slide 17](https://liascript.github.io/course/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374-Fall2026/gh-pages/_pages/Activities/liascript-lambdacalculus1.md#17) explains capture.

> **Try it first.**  Cover the worked reduction and reduce the same term on scratch paper, then compare line by line.  If you end somewhere other than $$a$$, the usual cause is reading $$f\ a\ b$$ as $$f\ (a\ b)$$.  You do not submit this.

## Church Booleans and Numerals

A Church encoding represents a value as a lambda term, so the calculus needs no built-in data.  A boolean is a function that chooses one of its two arguments, so $$\text{AND}\ p\ q$$ is $$p\ q\ p$$: if $$p$$ is true, the answer is $$q$$, and otherwise the answer is $$p$$, which is false.  A numeral $$n$$ applies its first argument $$n$$ times to its second:

```text
TWO f x:    x --f--> f x --f--> f (f x)
```

$$\text{SUCC}$$ runs $$n$$ and then applies $$f$$ once more.

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

## Part 0: Beta Reduction and Church Encodings

Do this part first.  Beta reduction is a rewriting rule, and you learn it by applying it slowly and recording each step.  One reduction reaches a normal form, one never will, and one shows that a numeral behaves as its definition claims.

### Step 0.1: A Term That Stops and a Term That Does Not

Under `## Part 0`, `### Item 1`:

1. Beta-reduce $$(\lambda x.\, \lambda y.\, x)\ a\ b$$ to normal form.  It has the same shape as the worked reduction.
2. Reduce $$(\lambda x.\, x\ x)\ (\lambda x.\, x\ x)$$ far enough to show why it never terminates, and explain what happens.

> **If you get stuck.**
> - Your first step contracted $$a\ b$$, or applied the lambda to $$b$$.  Application is left-associative, so write in the parentheses that implies before you pick a redex.
> - You replaced only one $$x$$ in $$x\ x$$.  A beta-step replaces every occurrence of the bound variable in the body, all at once.
> - You worried that the two binders named $$x$$ clash.  Capture needs a free variable in the argument, and this argument has none.

### Step 0.2: Verify SUCC ZERO by Reduction

Under `### Item 2`, write out the definitions of $$\text{SUCC}$$ and $$\text{ZERO}$$ in full, then reduce $$\text{SUCC}\ \text{ZERO}$$ until the result matches $$\text{ONE}$$ up to the names of bound variables.

> **If you get stuck.**
> - You substituted the name $$\text{ZERO}$$ as if it were a variable.  A name is an abbreviation: write its definition, in parentheses, wherever the name appears.
> - You stopped while a redex was still inside the body of a lambda.  In this lab you keep reducing inside lambda bodies until no redex remains anywhere.
> - The $$f$$ and $$x$$ of $$\text{SUCC}$$ and of $$\text{ZERO}$$ blur together.  They are different variables.  If it helps, rename $$\text{ZERO}$$'s binders on an $$\to_\alpha$$ line before you substitute.

### Step 0.3: Mark Your Least-Confident Step

Under `### Least-confident step`, say where your shakiest step is by part, item, and step number, copy its line, and add one sentence saying what made you unsure.  Bring it to class, because those are the steps we work through at the board.

---

## Part 1: Beta Reduction

Reduce each term to normal form, one beta-step per line, with the redex underlined or bracketed on every line.

### Step 1.1: A Reduction With Constants

Under `## Part 1`, `### Item 1`, reduce $$(\lambda f.\, \lambda x.\, f\ (f\ x))\ (\lambda z.\, z + 1)\ 0$$.  Treat $$+$$ and the numerals as constants, which are not redexes.  If you simplify the arithmetic at the end, put it on its own line with $$=$$, because it is not a beta-step.

> **If you get stuck.**
> - Your term lost its shape after you substituted a lambda into a body.  Keep any substituted lambda in parentheses, or its body swallows everything to its right.
> - You see two redexes and are unsure which to pick.  Either choice reaches the same normal form here.  Contract the leftmost outermost one, which is a good habit.

### Step 1.2: The Capture Case

Here the obvious substitution is wrong.  A free variable in the argument refers to something outside the term, so it must still be free after the substitution.  Before each substitution, run this check:

```text
1. List the free variables of the argument.
2. List the binders inside the body that the substitution passes under.
3. If a name is on both lists, rename that binder and its uses to a fresh name.
```

Under `### Item 2`, reduce $$(\lambda x.\, \lambda y.\, x\ y)\ y$$.  Show the renaming on its own $$\to_\alpha$$ line, then the beta-step, and add one sentence saying what would have gone wrong without the renaming.  Check your final term: the $$y$$ that came in as the argument must still be free.

> **If you get stuck.**
> - You renamed the free $$y$$.  Only a bound variable may be renamed.
> - You renamed and substituted on one line.  The renaming is its own line.

### Step 1.3: Evaluation Order

Some terms have a normal form that only some evaluation orders find.  *Normal order* reduces the leftmost outermost redex first.  *Applicative order* reduces arguments before applying the function.  Under `### Item 3`, reduce $$(\lambda x.\, z)\ ((\lambda x.\, x\ x)\ (\lambda x.\, x\ x))$$ twice, using the template each time:

1. **Normal order:** continue until you reach a normal form.
2. **Applicative order:** show two steps, enough to see what is happening.

Then say in a few sentences which order terminates, why, and what that implies about lazy evaluation.

> **If you get stuck.**  You only see one redex in the starting term.  Check every parenthesized subterm, including the argument, and ask whether it is a lambda applied to something.

---

## Part 2: Church Encodings

Write each name's definition in full on your first line, each in its own parentheses, and then reduce.  A verification succeeds when your complete sequence ends at the expected term, up to the names of bound variables.  Keep going until no redex remains anywhere, including inside lambda bodies.

> **If you get stuck.**
> - A binder named $$f$$ in the argument seems to clash with a binder in the body.  Capture is only about the argument's *free* variables, and these encodings have none.
> - A definition appears twice in your term.  Contract one redex per line, and leave the other copy alone until a redex reaches it.

### Step 2.1: AND FALSE TRUE

Under `## Part 2`, `### Item 1`, verify that $$\text{AND}\ \text{FALSE}\ \text{TRUE}$$ reduces to $$\text{FALSE}$$.

### Step 2.2: AND TRUE TRUE

Under `### Item 2`, verify that $$\text{AND}\ \text{TRUE}\ \text{TRUE}$$ reduces to $$\text{TRUE}$$.

### Step 2.3: SUCC ONE

Under `### Item 3`, verify that $$\text{SUCC}\ \text{ONE}$$ reduces to a term alpha-equivalent to $$\text{TWO}$$.  If your binder names differ, add one $$\to_\alpha$$ line that ends exactly at $$\text{TWO}$$.

### Step 2.4: The Closing Answer

A Church numeral *is* a higher-order function: "apply $$f$$, $$n$$ times."  Under `### Item 4`, name the Python or Scheme idiom from the Functional Programming sessions that does exactly this, and one place your team language or interpreter could use the same trick.  A few sentences are enough.

---

## Deliverables

| File or artifact | What it shows | Rubric row |
|------------------|---------------|------------|
| `## Part 0` section of `reductions.md` (or `reductions.pdf`) | Both Part 0 reductions step by step, the non-terminating case explained, $$\text{SUCC}\ \text{ZERO}$$ verified, and the least-confident step marked | Part 0: Before You Start |
| `## Part 1` section | Three items, one beta-step per line with the redex marked, the capture case alpha-renamed with a sentence, and the evaluation-order answer with the divergence example | Beta Reduction (Goal 1) |
| `## Part 2` section | Three complete verifications ending at the expected term, and the closing answer connecting Church numerals to a higher-order-function idiom | Church Encodings (Goals 2, 3) |
| Your name (and your partner's, if you worked in a pair) on the first line | Who did the work; partners receive the same grade | All rows |

---

## Self-Check Before You Submit

- [ ] Both partners are named at the top (or "worked alone" is written there).
- [ ] Every heading from `reductions.md` is present, in order, with its item under it.
- [ ] Every reduction is one beta-step per line, with no two steps folded into one.
- [ ] The redex is underlined or bracketed on every line, not only the first.
- [ ] Part 1 item 2 has a $$\to_\alpha$$ line before the substitution, plus one sentence saying what capture would have done.
- [ ] Part 1 item 3 says which evaluation order terminates on the divergence example and what that implies about lazy evaluation.
- [ ] Every Part 2 verification starts from the expanded definitions and ends at the expected term, with a renaming line under item 3 if the binder names differ from $$\text{TWO}$$.
- [ ] Part 2 item 4 names a specific idiom from the Functional Programming sessions and a specific place in your team language or interpreter.
- [ ] The least-confident step from Part 0 is marked, and, if handwritten, every photo is readable.

---

## Reflection Prompts

- Which reduction did you and your partner disagree on, and what settled it?  Or, if you worked alone, which reduction did you have to redo, and what settled it?
- If you worked in a pair, note who did what.  If you worked alone, note that instead.
