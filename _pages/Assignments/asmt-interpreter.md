---
layout: assignment
permalink: /Assignments/Interpreter
title: "CS374: Principles of Programming Languages - The Interpreter"

info:
  coursenum: CS374
  purpose: "To read a small working interpreter written in Flex and Bison, and to change its evaluator, scanner, and grammar, so that you can see how the pieces of a language fit together."
  tilt:
    task: "Build and run a given Scheme interpreter, answer three questions about how it works, and make three targeted changes to it: a new primitive, a new shorthand in the scanner and grammar, and a new special form."
    criteria: "I grade this on accurate answers about how the interpreter works, and on three changes that work without breaking the provided programs.  The rubric below breaks this down in full."
  points: 100
  goals:
    - To explain how a scanner, a grammar, and an evaluator work together in a small interpreter
    - To add a primitive function to an interpreter
    - To add syntax through the scanner and the grammar
    - To add a special form, and to explain why it cannot be a function
  rubric:
    - weight: 25
      description: "Reading the Interpreter (Goal 1)"
      preemerging: The interpreter was not built, or the questions are not answered
      beginning: One question is answered accurately
      progressing: Two questions are answered accurately, or all three with a mistake in the trace
      proficient: The trace of an evaluation is accurate, the answer says why `if` is a special form, and the answer follows the scope chain for `adder` through the parent link
    - weight: 25
      description: "A New Primitive (Goal 2)"
      preemerging: No primitive is added
      beginning: The function is written, but it is not in the table or does not run
      progressing: The primitive runs but returns a wrong value in some case
      proficient: "`max` returns the larger of its two evaluated arguments, and it is added with one function and one table row"
    - weight: 25
      description: "A New Shorthand (Goal 3)"
      preemerging: The shorthand is not added
      beginning: The scanner or the grammar is changed, but not both
      progressing: The shorthand works on a symbol or a list but not both, or the build reports warnings
      proficient: "`'x` reads as the list `(quote x)` for any datum, and the build has no conflict or scanner warnings"
    - weight: 25
      description: "A New Special Form (Goal 4)"
      preemerging: The form is not added
      beginning: The form is added but evaluates every clause, or it crashes
      progressing: The form chooses correctly, but a case with no matching clause is not reported
      proficient: "`cond` evaluates tests in order and only the chosen expression, reports an error when no clause matches, and the provided programs give the same output as before"
  readings:
    - rtitle: "Flex and Bison"
      rlink: "../Tutorials/FlexAndBison"
    - rtitle: "Scope Chains and Closures Activity (the scope chain this interpreter uses)"
      rlink: "Activities/liascript-scope-chains.md"
      liapage: true
    - rtitle: "Functional Programming in Scheme Activity"
      rlink: "Activities/liascript-functional.md"
      liapage: true

tags:
  - interpreter
  - scheme
  - languages

---

In this assignment you read a small working interpreter and change it.  You get a Scheme written in Flex, Bison, and C, about 300 lines in all, and you add to it in three small steps.  Everything is in the [starter kit]({{ site.baseurl }}/files/starters/interpreter/), and nothing depends on any earlier assignment.

---

## Before You Start

You need `flex`, `bison`, `gcc`, and `make`.  On Ubuntu, `sudo apt install flex bison gcc make` installs them.  Make a folder named `cs374-interpreter`, and copy the starter kit into it.

---

## Part 1: Build It, Run It, and Read It

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

Read these three files in this order, because each change below touches a different one:

- **`scanner.l`** turns characters into tokens: numbers, symbols, `#t`, `#f`, and parentheses.
- **`parser.y`** turns tokens into Scheme data.  A list in the source becomes a linked list of `Value`s, built with `cons` in the `items` rule.  Scheme code and Scheme data are the same thing, so the parser needs no other structure.  The `program` rule evaluates each item as soon as it is read.
- **`scheme.c`** holds the evaluator.  In `eval`, a number evaluates to itself and a symbol is looked up.  A list is either a special form, which decides for itself what to evaluate, or a call, which evaluates everything and then applies the function.  `lookup` walks a linked list of scopes, and a call makes a new scope whose parent is the scope where the function was created.  That parent link is why `adder` in `functions.scm` works.

**Do this.**  Answer these in `notes.md`.  The answers are short, and each one points you at a part of the code.

1. Trace `(+ 1 (* 2 3))` through `eval`.  Which case handles the outer list, in what order are its parts evaluated, and what does `apply` receive?
2. Why is `if` a special form in `eval`, when `+` is a primitive?  What would go wrong with `(if (= n 0) 1 (fact (- n 1)))` if `if` were a primitive?
3. In `functions.scm`, `add3` is called after `adder` has already returned.  How does `lookup` still find `a`?  Name the two scopes on the chain.

---

## Part 2: Add a Primitive, `max`

A primitive is a function written in C.  It receives its evaluated arguments as a list, and `first(a)` and `second(a)` read them.  So adding one takes two lines in `scheme.c`: a function next to `prim_add`, and a row in the `PRIMITIVES` table.  Write `prim_max`, which returns the larger argument, and add its row under the name `max`.

```bash
make && printf '(max 3 7)\n(max (+ 5 5) 7)\n' | ./scheme
```

> **You should see.** `7`, then `10`.  The arguments are evaluated before your function runs, which is why `(+ 5 5)` arrives as `10`.

## Part 3: Add a Shorthand, `'`

Scheme programmers write `'x` for `(quote x)`.  The evaluator already handles `quote`, so this change lives only in the scanner and the grammar.

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

## Part 4: Add a Special Form, `cond`

`cond` has to be a special form, because a call would evaluate every clause, and `cond` must evaluate only the one it chooses.  It looks like this:

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

## Deliverables

Submit a ZIP of your `cs374-interpreter` folder, with the build products removed (`make clean`), containing `notes.md` and the interpreter with your three changes.

## Self-Check Before You Submit

- [ ] `make clean && make` shows no warnings.
- [ ] `max`, `'`, and `cond` work.
- [ ] Both provided programs give the same output as before your changes.

## Reflection Prompts

- Each change touched a different file.  How did you decide where each one belonged?
- `'` needed no change to `eval`.  What does that tell you about the difference between syntax and meaning?
