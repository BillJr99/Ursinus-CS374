---
layout: assignment
permalink: /Assignments/Scheme
title: "CS374: Principles of Programming Languages - Functional Programming with Scheme"

info:
  coursenum: CS374
  purpose: "To get a Scheme environment running on your own machine and then write, from scratch, the list recursion, functional composition, and closures that the functional paradigm is actually made of, ending with one small program of your own."
  tilt:
    task: "Install Scheme (or open a browser REPL), work the four guided examples, then write the exercises and one small toy program of your own, submitting real transcripts of each running."
    criteria: "I grade this on a working environment with evidence, correct recursive list functions with their empty-list cases handled, correct use of functions as values including a closure, and a small program of your own that runs and is explained, weighted 20/35/20/25 across the four parts.  The rubric below breaks it down in full."
  points: 100
  goals:
    - To install and run a Scheme implementation, or run one in a browser, and to read its error messages
    - To write recursive functions over lists using car, cdr, cons, and a base case, since Scheme has no loop
    - To compose functions and pass them as values, including building a fold that takes its operator as a parameter
    - To write a closure and explain what it captured
    - To design, write, and explain one small program of your own in a language you met three days ago
  rubric:
    - weight: 20
      description: "Setup and the Guided Examples (Goal 1)"
      preemerging: No environment is running and no transcript is submitted
      beginning: A REPL is running but the transcripts are retyped by hand rather than captured, or several examples were not run
      progressing: All four guided examples run and are captured, but the write-up does not say which route was used or what went wrong along the way
      proficient: Every guided example is captured as a real transcript, the write-up names the route taken (local install or browser) with its version, and it reports at least one error you hit and how you read the message
    - weight: 35
      description: "List Recursion (Goal 2)"
      preemerging: The recursive functions are missing, or none returns a correct answer on a nonempty list
      beginning: Some functions work on typical lists but every one of them errors or loops forever on the empty list
      progressing: All functions are correct on nonempty lists and most handle the empty list, but at least one empty-list decision is undocumented or inconsistent with the others
      proficient: czr, reverse, count, and the improved largest are all correct; every one has a documented, defended answer for the empty list using pair? or null?; and the improvement to largest is explained in terms of how many recursive calls it makes rather than asserted
    - weight: 20
      description: "Functions as Values (Goals 3, 4)"
      preemerging: No function takes or returns another function
      beginning: The operator fold works for addition only, or the counter is written with a global rather than a captured binding
      progressing: The fold works for several operators and the counter increments, but two counters share state or the write-up does not say what was captured
      proficient: The fold takes its operator as a parameter and is demonstrated on at least three operators including one you define yourself; two independently created counters count independently; and the write-up names exactly what each closure captured and where it lives
    - weight: 25
      description: "Your Toy Program (Goal 5)"
      preemerging: No program of your own is submitted
      beginning: A program is submitted but does not run, or is a restatement of one of the exercises
      progressing: The program runs on the given cases but is not tested beyond them, or the write-up describes what it does without explaining the design
      proficient: The program runs on its own test cases including at least one edge case you chose; it uses recursion and at least one function passed as a value; and the write-up explains one design decision you made and one thing you would do differently with more time
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

Work it in order.  Part 1 gets Scheme running and walks four examples with you.  Parts 2 and 3 are exercises built directly on those examples.  Part 4 is one small program of your own, and it is the part I most want to read.

**This is individual work.**  Talk to each other about ideas and error messages as much as you like; the code and the write-up are yours.

---

## Part 1: Getting Scheme Running (20 points)

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

## Part 2: List Recursion (35 points)

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

## Part 3: Functions as Values (20 points)

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

## Part 4: A Small Program of Your Own (25 points)

Write one small program, in `toy.scm`, that does something you find worth doing.  Small means roughly fifteen to forty lines.  It must use recursion, and it must pass at least one function as a value somewhere.

**The one I would pick: a tiny expression evaluator.**  Represent an arithmetic expression as a nested list, exactly the way Scheme writes its own code, and evaluate it:

```scheme
(evaluate '(+ 1 2))              ; 3
(evaluate '(* (+ 2 3) 4))        ; 20
(evaluate '(- (* 6 7) (/ 10 2))) ; 37
```

A number evaluates to itself.  A list is an operator and its arguments, so evaluate the arguments first (`map` is your friend here) and then apply the operator.  That is the whole program, and it is about fifteen lines.

It is also, quietly, the point of this course.  You are writing an evaluator over a syntax tree in the first week of the term.  In October you will write the *parser* whose entire job is to build that same tree out of the flat text `(2 + 3) * 4`, and comparing the two line counts is a conversation I want us to have.

Extensions if you want them: handle unary minus; look variables up in an association list so `(evaluate '(+ x 1))` works; or use `apply` so an operator can take any number of arguments.

**If you would rather work with data than syntax**, here is an equally good alternative: a small list-statistics program that reports the count, sum, mean, largest, and reversed form of a list of numbers, built entirely from functions you wrote in Parts 2 and 3, using no built-ins beyond `car`, `cdr`, `cons`, and `null?`.  Make the report itself a list you build, not a pile of `display` calls.

**Anything else of similar size is fine too.**  Run it on your own test cases, including at least one edge case you chose deliberately.

---

## Deliverables

Submit a ZIP containing `setup.md` (route, version, four transcripts, one error), `recursion.scm`, `higher_order.scm`, `toy.scm`, and a `writeup.md` answering the questions raised in Parts 2, 3, and 4.  Include the output of each `.scm` file, either captured in a comment at the bottom of the file or pasted into the write-up.

## Grading Breakdown

| Component | Points |
|-----------|--------|
| Part 1: Getting Scheme Running | 20 |
| Part 2: List Recursion | 35 |
| Part 3: Functions as Values | 20 |
| Part 4: A Small Program of Your Own | 25 |
| **Total** | **100** |

## Reflection Prompts

- Which was harder: getting Scheme installed, or getting your first recursion to terminate?  What does your answer suggest about where the real cost of a new language sits?
- Name one thing that was genuinely easier here than it would have been in Python, and one thing that was genuinely harder.
- AI disclosure: list any generative-AI tools you used, for what, and how you verified the results (or state 'none').
- Approximately how many hours it took you to finish this (I will not judge you for this at all; I am simply using it to gauge if the assignments are too easy or hard)?
