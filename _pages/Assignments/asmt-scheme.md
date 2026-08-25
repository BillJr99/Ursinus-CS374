---
layout: assignment
permalink: /Assignments/Scheme
title: "CS374: Principles of Programming Languages - Functional Programming with Scheme"

info:
  coursenum: CS374
  purpose: "To get a Scheme environment running on your own machine and then write, from scratch, the list recursion, functional composition, and closures that the functional paradigm is actually made of, ending with an evaluator for arithmetic expressions written as nested lists."
  tilt:
    task: "Rewrite one of your own loops in a functional style, install Scheme (or open a browser REPL), work the four guided examples, then write the exercises and an evaluator for nested-list arithmetic expressions, submitting real transcripts of each running."
    criteria: "I grade this on a defended functional rewrite of a loop you wrote, a working environment with evidence, correct recursive list functions with their empty-list cases handled, correct use of functions as values including a closure, and a working expression evaluator that handles an unknown operator and is explained, weighted 10/18/32/18/22 across the five parts.  The rubric below breaks it down in full."
  points: 100
  goals:
    - To rewrite a loop you already know how to write into map, filter, and reduce, and to say honestly which version reads better and why
    - To install and run a Scheme implementation, or run one in a browser, and to read its error messages
    - To write recursive functions over lists using car, cdr, cons, and a base case, since Scheme has no loop
    - To compose functions and pass them as values, including building a fold that takes its operator as a parameter
    - To write a closure and explain what it captured
    - To write a recursive evaluator over a nested-list expression tree, the same structure the parser you write in October produces
  rubric:
    - weight: 10
      description: "Part 0: The Functional Rewrite (Goal 1)"
      preemerging: No rewrite is submitted, or the original loop is not shown
      beginning: A rewrite is submitted but it does not run, or it still uses an explicit loop
      progressing: The rewrite runs and is equivalent to the original, but the write-up asserts a preference without arguing for it
      proficient: Both versions are shown and run; the rewrite uses map, filter, and reduce appropriately; and the write-up argues which is more readable and separates what is about the code from what is about your own habits
    - weight: 18
      description: "Setup and the Guided Examples (Goal 2)"
      preemerging: No environment is running and no transcript is submitted
      beginning: A REPL is running but the transcripts are retyped by hand rather than captured, or several examples were not run
      progressing: All four guided examples run and are captured, but the write-up does not say which route was used or what went wrong along the way
      proficient: Every guided example is captured as a real transcript, the write-up names the route taken (local install or browser) with its version, and it reports at least one error you hit and how you read the message
    - weight: 32
      description: "List Recursion (Goal 3)"
      preemerging: The recursive functions are missing, or none returns a correct answer on a nonempty list
      beginning: Some functions work on typical lists but every one of them errors or loops forever on the empty list
      progressing: All functions are correct on nonempty lists and most handle the empty list, but at least one empty-list decision is undocumented or inconsistent with the others
      proficient: czr, reverse, count, and the improved largest are all correct; every one has a documented, defended answer for the empty list using pair? or null?; and the improvement to largest is explained in terms of how many recursive calls it makes rather than asserted
    - weight: 18
      description: "Functions as Values (Goals 4, 5)"
      preemerging: No function takes or returns another function
      beginning: The operator fold works for addition only, or the counter is written with a global rather than a captured binding
      progressing: The fold works for several operators and the counter increments, but two counters share state or the write-up does not say what was captured
      proficient: The fold takes its operator as a parameter and is demonstrated on at least three operators including one you define yourself; two independently created counters count independently; and the write-up names exactly what each closure captured and where it lives
    - weight: 22
      description: "The Expression Evaluator (Goal 6)"
      preemerging: No evaluator is submitted, or it does not run
      beginning: The evaluator handles a flat expression such as (+ 1 2) but fails on a nested one, or the operator symbol is never resolved to a procedure
      progressing: The evaluator is correct on all the required test cases but does not detect an unknown operator, or the required extension is missing
      proficient: The evaluator is correct on every required test case including the three-deep nesting and the division case; an unknown operator is reported rather than crashing; one of the two extensions works; and the write-up answers all three questions, including where the recursion bottoms out and why it terminates
  readings:
    - rtitle: "Programming Paradigms, Evaluating Languages, and an Introduction to Functional Programming Activity"
      rlink: "Activities/liascript-languageevaluation.md"
      liapage: true
    - rtitle: "Functional Programming in Scheme, Part 2 Activity"
      rlink: "Activities/liascript-scheme.md"
      liapage: true
    - rtitle: "Functional Programming and Higher-Order Functions Activity"
      rlink: "Activities/liascript-functional.md"
      liapage: true
    - rtitle: "Scheme Essentials for the Programming Languages Course"
      rlink: "../Tutorials/SchemeEssentials"
    - rtitle: "The Scheme Programming Language (Dybvig)"
      rlink: "https://www.scheme.com/tspl3/"

tags:
  - functional
  - scheme
  - paradigms

---

This assignment is the written half of the three sessions we just spent in the functional paradigm.  Everything in it was worked at the board or in the activity decks, so nothing here should be a surprise; what is new is that you write it yourself, with a real interpreter telling you when you are wrong.

Work it in order.  Part 0 is a short warmup in a language you already know, and you should do it before the Functional Programming and Higher-Order Functions session rather than after.  Part 1 gets Scheme running and walks four examples with you.  Parts 2 and 3 are exercises built directly on those examples.  Part 4 is an expression evaluator, and it is the part I most want to read.

**This is individual work.**  Talk to each other about ideas and error messages as much as you like; the code and the write-up are yours.

---

## Part 0: Before You Start — The Functional Rewrite (10 points)

Do this one first, in **Python or whatever language you reach for by default**, not in Scheme.  It takes about twenty minutes, and its whole purpose is to make you notice your own habits before a new language starts rearranging them.

Find a loop you have actually written: something from a previous course, a script, anything with a `for` in it that does real work.  Rewrite it using `map`, `filter`, and `reduce` (in Python, `functools.reduce`, and comprehensions count as `map`/`filter` if you say so).

Then, in `part0.md`, put:

1. **Both versions**, the original loop and the rewrite, and the output of each showing they agree.
2. **Which one you find more readable**, in two or three sentences.
3. **The honest part**: how much of your answer to (2) is about the code, and how much is about which one you have seen more often?  The first time most people do this, the functional version reads *worse* to them, and that reaction is the interesting data, not a wrong answer.

If your loop refuses to translate cleanly, that is the best possible outcome here.  Say where it broke.  A loop that carries two accumulators, mutates something outside itself, or breaks early is exactly the case where the paradigms genuinely diverge, and naming why is worth more than a smooth rewrite.

> **Note:** you will write a closure in Part 3 (`make-counter`, exercise 9) and trace what it captured there.  Do not do that twice; this part is only the loop.

---

## Part 1: Getting Scheme Running (18 points)

### Pick a route

You need a Scheme prompt.  Any of these gives you one, and the first two need no install at all:

- **[try.scheme.org](https://try.scheme.org)**: a full Scheme REPL in a browser tab.  Nothing to set up, and the fastest way to be typing in thirty seconds.
- **The course's own runner**: the [Scheme warmup exercise]({{ site.baseurl }}/Modules/Scheme/Warmup/Exercise) runs Scheme directly in the page and checks your answer.  Do that one first; it takes two minutes and confirms your browser is not the problem.
- **A Python Scheme, no package manager needed**: `git clone https://github.com/BillJr99/scheme-interpreter.git` gives you a `scheme.py` you run as `python scheme.py <your scheme file>`.
- **A real local install**, which is what I would like you to end up with:
  - **Cygwin (Windows):** install `guile` from the Cygwin installer
  - **Ubuntu (Linux):** `sudo apt install mit-scheme`
  - **Mac:** `brew install mit-scheme`, provided you have installed [homebrew](https://brew.sh/)

Whichever you pick, get to the point where you can run a file rather than only type at a prompt.  Every exercise below wants a file you can hand in.


> **Watch out!**  Forgetting the quote before a list literal is the most common beginner error in this language.  `(1 2 3)` tells Scheme to call the function named `1` with arguments `2` and `3`, and since `1` is not a function you get `application: not a procedure` or similar.  Write `'(1 2 3)` when you mean data.  Trigger this error on purpose once and read the message; the write-up asks you about it.

### The four guided examples

Type each of these, run it, and **capture the transcript**.  Then change one thing and run it again.  These are the worked examples the exercises build on, so do not skip ahead.

**Example 1: lists, and `define` as binding.**

```scheme
(define L (list 'a 'b 'c))
(car L)                      ; a
(cdr L)                      ; (b c)
(cons 'z L)                  ; (z a b c)

(define x (+ 3 2))
(+ x 5)                      ; 10

(define add +)
(add 3 2)                    ; 5
```

`car` is the first element, `cdr` is everything after it, and `cons` puts one element back on the front.  Those three are the whole engine.  `(define add +)` is not a typo: `+` is an ordinary value, and `define` binds names to values of any kind, functions included.

**Example 2: `lambda`, `if`, and recursion.**

```scheme
(define square
  (lambda (n)
    (* n n)))

(define pow
  (lambda (n k)
    (if (= k 0)
        1
        (* n (pow n (- k 1))))))

(square (pow 5 3))           ; 15625
```

Every recursion in this assignment has that shape: a base case that answers directly, and a recursive case that does a little work and asks a smaller version of itself.

**Example 3: recursion over a list.**

```scheme
(define sumlist
  (lambda (L)
    (if (null? (cdr L))
        (car L)
        (+ (car L) (sumlist (cdr L))))))

(sumlist (list 1 2 3))       ; 6
```

Note where this one stops: at the *last element*, not at the empty list.  That means `(sumlist '())` is an error.  Whether that is a bug is Part 2's first question.

**Example 4: `cond`, `map`, and `apply`.**

```scheme
(define classify
  (lambda (n)
    (cond ((< n 0) 'negative)
          ((= n 0) 'zero)
          (else    'positive))))

(map classify '(-3 0 7))     ; (negative zero positive)

(define L1 '(1 2 3))
(define L2 '(4 5 6))
(map - L1 L2)                ; (-3 -3 -3)
(apply + '(1 2 3))           ; 6
```

`cond` is `if` with more than two branches.  `map` takes a *function* as its first argument and applies it across a list.  `apply` does the opposite: it takes one function and one list, and spreads the list out as that function's arguments, so `(apply + '(1 2 3))` is `(+ 1 2 3)`.

### What to write up

In `setup.md`: which route you used and its version, the four captured transcripts, and one error you hit along the way with the message it printed and what it turned out to mean.  If nothing went wrong, go trigger the unquoted-list error deliberately and write that one up.

---

## Part 2: List Recursion (32 points)

Put these in `recursion.scm`, with a test call after each one.  Every function here must have a documented answer for the empty list; use `null?` or `pair?` (which returns `#t` for a nonempty list) to guard it, and say in a comment what you decided and why.

1.  **`czr`**: return the last element of a list.  Model it on `sumlist`, but notice that nothing has to happen on the way back up: the answer is just whatever the deepest call found.
2.  **`count`**: return how many items are in a list.  Use `czr` as a guide to traversing the list.  Its base case cannot look at `(car L)` at all, which is the hint you need.
3.  **`reverse-list`**: reverse a list using only `car`, `cdr`, and `cons`.  (Name it `reverse-list` so you do not collide with the built-in `reverse`; compare against the built-in when you are done.)  Then answer: how many `cons` calls does yours make for a list of length `n`?
4.  **`largest`**: return the largest element.  Start from the version below, which is correct but wasteful, and improve it.

```scheme
(define largest
  (lambda (L)
    (if (null? (cdr L))
        (car L)
        (if (>= (car L) (largest (cdr L)))
            (car L)
            (largest (cdr L))))))
```

The improvement is not a style preference.  Count the recursive calls each version makes on `'(1 2 3 4 5 6 7 8)`, where the largest element is last, and report both numbers.  Your write-up should explain the difference in terms of what gets recomputed, not in terms of which one looks nicer.

5.  **The empty-list question**: `sumlist` from Part 1 errors on `'()`.  Fix it so it returns 0, and then argue in two or three sentences whether that was a bug in `sumlist` or a deliberate choice about what summing nothing should mean.  There is a defensible answer either way; I am grading the argument.

---

## Part 3: Functions as Values (18 points)

Put these in `higher_order.scm`.

6.  **`y` and a projectile**: write the linear equation as a function of three parameters, then use it and `square` together.

```scheme
(define y
  (lambda (m x b)
    (+ (* x m) b)))

(y 5 6 7)                    ; 37
```

Now do the same for projectile motion.  With `v0` the initial velocity, `t` the time, and `a` the acceleration, the distance is `v0*t + 0.5*a*t^2`.  Write it twice: once with `(* t t)` written out, and once with your `square` from Part 1 substituted in.  Confirm the two agree, then say in one sentence what substituting `square` bought you, given that it did not change the answer.  Finally, use `map` to compute the distance at `t` values `'(1 2 3 4 5)`; you will need a one-argument lambda that closes over `v0` and `a`.

7.  **`plusminus`**: given two numbers, return a two-element list of their sum and their difference, using an anonymous `lambda` applied immediately:

```scheme
(define plusminus
  (lambda (a b)
    ((lambda (x y) (list (+ x y) (- x y)))
     a b)))

(plusminus 6 2)              ; (8 4)
```

Run it, then draw (on paper, and describe in your write-up) how `a` and `b` bind to `x` and `y` in that inner lambda.

8.  **`oplist`**: write a function that accepts a list *and an operator* as parameters.  Apply that operator to the whole list recursively: if the operator is `+`, return the sum; if it is `*`, return the product.  Demonstrate it on at least three operators, one of which is a function you define yourself.  Then compare your result against `(apply * (list 2 4 6))` and say when the two would disagree.

9.  **`make-counter`**: write a function that returns a counter function.  Each call to the returned function gives the next number, and two counters made separately must count independently.

```scheme
(define (make-counter)
  (let ((count 0))
    (lambda ()
      (set! count (+ count 1))
      count)))
```

Run it with two counters interleaved.  Then answer in your write-up: what exactly did each returned function capture, and where does that captured value live once `make-counter` has returned?  Compare a closure with an object in two or three sentences.

---

## Part 4: An Expression Evaluator (22 points)

Write this one in `evaluate.scm`.  It is about fifteen lines, and it is the oldest program in this language's history: John McCarthy's 1960 paper defined Lisp by writing an evaluator for Lisp in Lisp, and every interpreter you have ever used is a descendant of that idea.  You are going to write the arithmetic-sized version of it in your first week.

### The representation

An arithmetic expression is a **nested list**, written exactly the way Scheme writes its own code.  The `car` is the operator symbol; the `cdr` is the list of operands.  A number is a leaf and stands for itself.

So `(* (+ 2 3) 4)` is this list:

```
    '(* (+ 2 3) 4)              *
     ├─ car:  *                / \
     └─ cdr: ((+ 2 3) 4)      +   4
                             / \
                            2   3
```

That picture on the right is a **syntax tree**, and it is worth knowing now that you will meet it again.  In October the Parser assignment's entire job is to build that same tree out of the flat text `(2 + 3) * 4`.  Scheme hands it to you for free, because Scheme's source code *is* the tree.  That is the trade the language made, and it is why the evaluator fits in fifteen lines here and does not there.

### The shape of the solution

Every recursion in Part 2 had the same two-case shape, and so does this one:

```scheme
(define evaluate
  (lambda (expr)
    (if (number? expr)
        expr                     ; base case: a number evaluates to itself
        ...)))                   ; recursive case: expr is a list
```

The recursive case has three steps.  Work them in this order.

**Step 1: get the operator — and read this part twice.**

```scheme
(car '(+ 1 2))                   ; +
```

That looks like it gave you addition.  It did not.  It gave you the **symbol** `+`, which is a name, not the procedure that adds.  Try `((car '(+ 1 2)) 1 2)` in your REPL and read the error; this is the single place everyone loses twenty minutes on this assignment, and you may as well lose it on purpose now.

You need to turn the symbol into the procedure.  Two ways, and you should understand both:

```scheme
; Way A: dispatch with cond
(define lookup-op
  (lambda (sym)
    (cond ((eq? sym '+) +)
          ((eq? sym '-) -)
          ((eq? sym '*) *)
          ((eq? sym '/) /)
          (else (error "unknown operator:" sym)))))

; Way B: an association list, searched with assq
(define ops (list (cons '+ +) (cons '- -) (cons '* *) (cons '/ /)))
```

Look at what Way B is: a list whose values *are procedures*.  That is Part 3's "functions as values" doing load-bearing work rather than sitting in an exercise.  Either way is acceptable; say in your write-up which you chose.

**Step 2: evaluate the operands.**  Each operand may itself be a whole expression, so each one needs the same treatment — which is to say, `evaluate` calls itself:

```scheme
(map evaluate (cdr expr))        ; ((+ 2 3) 4)  =>  (5 4)
```

That is the same `map` from Part 1's Example 4, except the function you are passing it is the one you are in the middle of writing.

**Step 3: apply.**  You now hold a procedure and a list of numbers, which is exactly what `apply` takes:

```scheme
(apply + '(5 4))                 ; 9
```

Assemble those three steps and you are done.

### Required test cases

Run all of these and capture the output:

```scheme
(evaluate '(+ 1 2))                        ; 3
(evaluate '(* (+ 2 3) 4))                  ; 20
(evaluate '(- (* 6 7) (/ 10 2)))           ; 37
(evaluate '(+ 1 (* 2 (- 10 (/ 8 4)))))     ; 17   <- nested three deep
(evaluate 42)                              ; 42   <- the base case, on its own
```

Then add **one edge case you chose deliberately**, and say in your write-up why you picked it and what it told you.

### Required: the unknown operator

What should `(evaluate '(+ 1 (& 2 3)))` do?  Your evaluator must **detect the unknown operator and report it**, naming the offending symbol, rather than crashing with whatever Scheme says by default.  `error` is the procedure you want.  This is your first error message as a language implementer, and the standard it has to meet is the one you will be held to in the Lexer and Parser assignments: say what was wrong, and say which thing was wrong.

### Required: one extension, your choice of two

Pick **one** and make it work:

- **Any number of arguments.**  Make `(evaluate '(+ 1 2 3 4))` return `10`.  If you built Step 3 with `apply`, check whether this already works, and if it does, say why in one sentence rather than changing code.
- **Variables.**  Give `evaluate` a second parameter, an association list of bindings, so that `(evaluate '(+ x 1) '((x . 5)))` returns `6`.  Look symbols up with `assq`, and decide what happens when a variable is not bound.  Be warned that you are building an *environment* here — the same structure the Interpreter assignment builds in November, and the same one the Environments and Scope lab makes you get right.

### What to write up

In `writeup.md`:

- How many lines is your `evaluate`?  Count them.
- What is `(map evaluate (cdr expr))` doing that a `for` loop over the operands would not?  Answer in terms of the nesting, not in terms of style.
- Where does the recursion bottom out, and how do you know it terminates on every well-formed expression?

---

## Deliverables

Submit a ZIP containing `part0.md` (both loop versions, their output, and your readability argument), `setup.md` (route, version, four transcripts, one error), `recursion.scm`, `higher_order.scm`, `evaluate.scm`, and a `writeup.md` answering the questions raised in Parts 2, 3, and 4.  Include the output of each `.scm` file, either captured in a comment at the bottom of the file or pasted into the write-up.

## Grading Breakdown

| Component | Points |
|-----------|--------|
| Part 0: The Functional Rewrite | 10 |
| Part 1: Getting Scheme Running | 18 |
| Part 2: List Recursion | 32 |
| Part 3: Functions as Values | 18 |
| Part 4: An Expression Evaluator | 22 |
| **Total** | **100** |

## Reflection Prompts

- Which was harder: getting Scheme installed, or getting your first recursion to terminate?  What does your answer suggest about where the real cost of a new language sits?
- Name one thing that was genuinely easier here than it would have been in Python, and one thing that was genuinely harder.
- Your `evaluate` walks a syntax tree in about fifteen lines.  In October you will write a parser whose only job is to *build* that tree from flat text.  Before you write it: how much code do you think that will take, and what exactly is the parser doing that Scheme did for you here?  I will ask you to look back at your answer.
- AI disclosure: list any generative-AI tools you used, for what, and how you verified the results (or state 'none').
- Approximately how many hours it took you to finish this (I will not judge you for this at all; I am simply using it to gauge if the assignments are too easy or hard)?
