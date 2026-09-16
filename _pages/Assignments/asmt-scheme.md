---
layout: assignment
permalink: /Assignments/Scheme
title: "CS374: Principles of Programming Languages - Functional Programming with Scheme"
info:
  coursenum: CS374
  purpose: "To get a Scheme environment running on your own machine and then write, from scratch, the list recursion, functional composition, and closures that the functional paradigm is actually made of, ending with an evaluator for arithmetic expressions written as nested lists."
  tilt:
    task: "Rewrite one of your own loops in a functional style, install Scheme (or open a browser REPL), work the four guided examples, then write the exercises and an evaluator for nested-list arithmetic expressions, submitting real transcripts of each running."
    criteria: "I grade this on a defended functional rewrite of a loop you wrote, a working environment with evidence, correct recursive list functions with their empty-list cases handled, correct use of functions as values including a closure, and a working expression evaluator that handles an unknown operator and is explained, weighted according to the rubric below."
  points: 100
  goals:
    - To rewrite a loop you already know how to write into map, filter, and reduce, and to say honestly which version reads better and why
    - To install and run a Scheme implementation, or run one in a browser, and to read its error messages
    - To write recursive functions over lists using car, cdr, cons, and a base case, since Scheme has no loop
    - To compose functions and pass them as values, including building a fold that takes its operator as a parameter
    - To write a closure and explain what it captured
    - To read and write let, association lists, and assq before you need them in the evaluator
    - To write a recursive evaluator over a nested-list expression tree, the same structure the parser you write later in this course produces
  rubric:
    - weight: 10
      description: "Part 0: The Functional Rewrite (Goal 1)"
      preemerging: "No rewrite is submitted, or the original loop is not shown"
      beginning: "A rewrite is submitted but it does not run, or it still uses an explicit loop"
      progressing: "The rewrite runs and is equivalent to the original, but the write-up asserts a preference without arguing for it"
      proficient: "Both versions are shown and run; the rewrite uses map, filter, and reduce appropriately; and the write-up argues which is more readable and separates what is about the code from what is about your own habits"
    - weight: 18
      description: "Setup and the Guided Examples (Goal 2)"
      preemerging: "No environment is running and no transcript is submitted"
      beginning: "A REPL is running but the transcripts are retyped by hand rather than captured, or several examples were not run"
      progressing: "All four guided examples run and are captured, but the write-up does not say which route was used or what went wrong along the way"
      proficient: "Every guided example is captured as a real transcript, the write-up names the route taken (local install or browser) with its version, and it reports at least one error you hit and how you read the message"
    - weight: 32
      description: "List Recursion (Goal 3)"
      preemerging: "The recursive functions are missing, or none returns a correct answer on a nonempty list"
      beginning: "Some functions work on typical lists but every one of them errors or loops forever on the empty list"
      progressing: "All functions are correct on nonempty lists and most handle the empty list, but at least one empty-list decision is undocumented or inconsistent with the others"
      proficient: "czr, reverse, count, and the improved largest are all correct; every one has a documented, defended answer for the empty list using pair? or null?; and the improvement to largest is explained in terms of how many recursive calls it makes rather than asserted"
    - weight: 18
      description: "Functions as Values (Goals 4, 5)"
      preemerging: "No function takes or returns another function"
      beginning: "The operator fold works for addition only, or the counter is written with a global rather than a captured binding"
      progressing: "The fold works for several operators and the counter increments, but two counters share state or the write-up does not say what was captured"
      proficient: "The fold takes its operator as a parameter and is demonstrated on at least three operators including one you define yourself; two independently created counters count independently; and the write-up names exactly what each closure captured and where it lives"
    - weight: 22
      description: "The Expression Evaluator (Goal 6)"
      preemerging: "No evaluator is submitted, or it does not run"
      beginning: "The evaluator handles a flat expression such as (+ 1 2) but fails on a nested one, or the operator symbol is never resolved to a procedure"
      progressing: "The evaluator is correct on all the required test cases but does not detect an unknown operator, or the required extension is missing"
      proficient: "The evaluator is correct on every required test case including the three-deep nesting and the division case; an unknown operator is reported rather than crashing; one of the two extensions works; and the write-up answers all three questions, including where the recursion bottoms out and why it terminates"
  readings:
    - rtitle: "Programming Paradigms, Evaluating Languages, and an Introduction to Functional Programming Activity"
      rlink: Activities/liascript-languageevaluation.md
      liapage: true
    - rtitle: "Functional Programming in Scheme, Part 2 Activity"
      rlink: Activities/liascript-scheme.md
      liapage: true
    - rtitle: "Functional Programming and Higher-Order Functions Activity"
      rlink: Activities/liascript-functional.md
      liapage: true
    - rtitle: "Scheme Essentials for the Programming Languages Course"
      rlink: ../Tutorials/SchemeEssentials
    - rtitle: "The Scheme Programming Language (Dybvig)"
      rlink: https://www.scheme.com/tspl3/
tags:
  - functional
  - scheme
  - paradigms
---

This assignment is the written half of our work in the functional paradigm. Everything in it was worked at the board or in the activity decks, so nothing here should be a surprise; what is new is that you write it yourself, with a real interpreter telling you when you are wrong.

Work it in order. Part 0 is a short warmup in a language you already know, and you should do it before you start Part 1. Part 1 gets Scheme running and walks four examples with you. Parts 2 and 3 are exercises built directly on those examples. Before Part 4, there is a short primer on four forms the evaluator needs that we have not yet used as heavily in class: `let`, association lists, `assq`, and a second look at `map` and `apply`. Part 4 is the expression evaluator itself, and it is the part I most want to read.

**This is individual work.** Talk to each other about ideas and error messages as much as you like; the code and the write-up are yours.

---

## Part 0: Before You Start - The Functional Rewrite (10 points)

Do this one first, in **Python or whatever language you reach for by default**, not in Scheme. It takes about twenty minutes, and its whole purpose is to make you notice your own habits before a new language starts rearranging them.

Find a loop you have actually written: something from a previous course, a script, anything with a `for` in it that does real work. Rewrite it using `map`, `filter`, and `reduce` (in Python, `functools.reduce`, and comprehensions count as `map`/`filter` if you say so).

Then, in `part0.md`, put:

1. **Both versions**, the original loop and the rewrite, and the output of each showing they agree.
2. **Which one you find more readable**, in two or three sentences.
3. **The honest part**: how much of your answer to (2) is about the code, and how much is about which one you have seen more often? The first time most people do this, the functional version reads *worse* to them, and that reaction is the interesting data, not a wrong answer.

If your loop refuses to translate cleanly, that is the best possible outcome here. Say where it broke. A loop that carries two accumulators, mutates something outside itself, or breaks early is exactly the case where the paradigms genuinely diverge, and naming why is worth more than a smooth rewrite.

> **Note:** you will write a closure in Part 3 (`make-counter`, exercise 9) and trace what it captured there. Do not do that twice; this part is only the loop.

---

## Part 1: Getting Scheme Running (18 points)

### Pick a route

You need a Scheme prompt. Any of these gives you one, and the first three need no new install at all:

- **The course dev container**: if you built the [course container]({{ site.baseurl }}/Tutorials/DevEnvironment) in the Overview assignment, Scheme is already installed. Run `guile` for a REPL, or `guile your_file.scm` to run a file. `mit-scheme` is in there too, on the CPU architectures Debian builds it for. Report whichever one you use, and its version, in the write-up.
- **[try.scheme.org](https://try.scheme.org)**: a full Scheme REPL in a browser tab. Nothing to set up, and the fastest way to be typing in thirty seconds. There is no file to load here: the page evaluates whatever you paste into it, in the order you paste it. So paste a function's `define` and run it *first*, and only then paste the call that uses it. Pasting `(square 5)` before `(define square ...)` gives you an unbound-variable error that looks like a problem with Scheme and is really a problem with the order.
- **The course's own runner**: the [Scheme warmup exercise]({{ site.baseurl }}/Modules/Scheme/Warmup/Exercise) runs Scheme directly in the page and checks your answer. Do that one first; it takes two minutes and confirms your browser is not the problem.
- **A Python Scheme, no package manager needed**: `git clone https://github.com/BillJr99/scheme-interpreter.git` gives you a `scheme.py` you run as `python scheme.py <your scheme file>`.
- **A real local install**, which is what I would like you to end up with:
  * **Cygwin (Windows):** install `guile` from the Cygwin installer
  * **Ubuntu (Linux):** `sudo apt install mit-scheme`
  * **Mac:** `brew install mit-scheme`, or `brew install guile`, provided you have installed [homebrew](https://brew.sh/). Either one is a fine Scheme for this assignment; guile is the safer bet on Apple Silicon, where MIT/GNU Scheme is not always available

Whichever you pick, get to the point where you can run a file rather than only type at a prompt. Every exercise below wants a file you can hand in.

### Making your program print something

A REPL echoes the value of every expression you type, so at a prompt `(square 5)` shows you `25` on its own. Running a *file* is different: nothing is echoed, and a file full of correct definitions prints absolutely nothing. That silence is the single most common "my Scheme is broken" report I get, and the fix is one procedure. `display` prints a value, and `newline` ends the line.

Always follow a `display` with a `(newline)`. It separates your output, and it also matters for a reason that is easy to miss: some interpreters buffer what you print and only flush a line once it is terminated, so a `display` with no `newline` after it can leave your last result sitting in the buffer, unprinted, even though the program ran correctly. If output is missing and you are sure the code is right, a missing `(newline)` is the first thing to check.

```scheme
(define square
  (lambda (n)
    (* n n)))

(square 5)            ; at a REPL this shows 25; in a file it prints nothing at all
(display (square 5))  ; prints 25
(newline)             ; ends the line, so the next output does not run into this one
                      ; and so a buffering interpreter actually flushes it to the terminal
```

Every exercise below wants a file you can hand in, so wrap the results you want to see in `display` and follow each one with `newline`. If an interpreter you are using does echo top-level values, `display` is still correct and still worth writing, because it is what makes the same file behave the same way everywhere.

> **Watch out!** Forgetting the quote before a list literal is the most common beginner error in this language. `(1 2 3)` tells Scheme to call the function named `1` with arguments `2` and `3`, and since `1` is not a function you get `application: not a procedure` or similar. Write `'(1 2 3)` when you mean data. Trigger this error on purpose once and read the message; the write-up asks you about it.

### The four guided examples

Type each of these, run it, and **capture the transcript**. Then change one thing and run it again. The exercises build directly on these worked examples.

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

`car` is the first element, `cdr` is everything after it, and `cons` puts one element back on the front. Those three are the whole engine. `(define add +)` is not a typo: `+` is an ordinary value, and `define` binds names to values of any kind, functions included.

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

Note where this one stops: at the *last element*, not at the empty list. That means `(sumlist '())` is an error. Whether that is a bug is Part 2's first question.

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

`cond` is `if` with more than two branches. `map` takes a *function* as its first argument and applies it across a list. `apply` does the opposite: it takes one function and one list, and spreads the list out as that function's arguments, so `(apply + '(1 2 3))` is `(+ 1 2 3)`.

We will come back to both `map` and `apply` in the primer before Part 4, so do not worry yet about using them fluently; for now, just get the transcript above running and matching the comments.

### What to write up

In `setup.md`: which route you used and its version, the four captured transcripts, and one error you hit along the way with the message it printed and what it turned out to mean. If nothing went wrong, go trigger the unquoted-list error deliberately and write that one up.

---

## Part 2: List Recursion (32 points)

Put these in `recursion.scm`, with a test call after each one. Every function here must have a documented answer for the empty list; use `null?` or `pair?` (which returns `#t` for a nonempty list) to guard it, and say in a comment what you decided and why.

1. **`czr`**: return the last element of a list. Model it on `sumlist`, but notice that nothing has to happen on the way back up: the answer is just whatever the deepest call found.
2. **`count`**: return how many items are in a list. Use `czr` as a guide to traversing the list. Its base case cannot look at `(car L)` at all, which is the hint you need.
3. **`reverse-list`**: reverse a list using only `car`, `cdr`, and `append`. (Name it `reverse-list` so you do not collide with the built-in `reverse`; compare against the built-in when you are done.)
4. **`largest`**: return the largest element. Start from the version below, which is correct but wasteful, and improve it.

```scheme
(define largest
  (lambda (L)
    (if (null? (cdr L))
        (car L)
        (if (>= (car L) (largest (cdr L)))
            (car L)
            (largest (cdr L))))))
```

Look closely at that second branch: `(largest (cdr L))` appears **twice**, once in the `if` test and once again if the test fails. Scheme does not remember the answer from the first call; it walks all the way to the end of the list and back a second time, from scratch, just to get a value it already computed once. The improvement is not a style preference. Count the recursive calls each version makes on `'(1 2 3 4 5 6 7 8)`, where the largest element is last, and report both numbers. Your write-up should explain the difference in terms of what gets recomputed, not in terms of which one looks nicer.

Here is the hint. Add a `(let ((X y)) ...)` to the lambda, where `X` is a name and `y` is an expression. Which expression should you bind to `X` so that Scheme computes it only once? The primer before Part 4 introduces `let`. Skim it now if this hint does not land.

5. **The empty-list question**: `sumlist` from Part 1 errors on `'()`. Fix it so it returns 0, and then argue in two or three sentences whether that was a bug in `sumlist` or a deliberate choice about what summing nothing should mean. There is a defensible answer either way; I am grading the argument.

---

## Part 3: Functions as Values (18 points)

Put these in `higher_order.scm`.

6. **`y` and a projectile**: write the linear equation as a function of three parameters, then use it and `square` together.

```scheme
(define y
  (lambda (m x b)
    (+ (* x m) b)))

(y 5 6 7)                    ; 37
```

Now do the same for projectile motion. With `v0` the initial velocity, `t` the time, and `a` the acceleration, the distance is `v0*t + 0.5*a*t^2`. Write it twice: once with `(* t t)` written out, and once with your `square` from Part 1 substituted in. Confirm the two agree, then say in one sentence what substituting `square` bought you, given that it did not change the answer. Finally, use `map` to compute the distance at `t` values `'(1 2 3 4 5)`; you will need a one-argument lambda that closes over `v0` and `a`.

7. **`plusminus`**: given two numbers, return a two-element list of their sum and their difference, using an anonymous `lambda` applied immediately:

```scheme
(define plusminus
  (lambda (a b)
    ((lambda (x y) (list (+ x y) (- x y)))
     a b)))

(plusminus 6 2)              ; (8 4)
```

Run it, then draw (on paper, and describe in your write-up) how `a` and `b` bind to `x` and `y` in that inner lambda.

8. **`oplist`**: write a function that accepts a list *and an operator* as parameters. Apply that operator to the whole list recursively: if the operator is `+`, return the sum; if it is `*`, return the product. Demonstrate it on at least three operators, one of which is a function you define yourself. Then compare your result against `(apply * (list 2 4 6))` and say when the two would disagree.

9. **`make-counter`**: write a function that returns a counter function. Each call to the returned function gives the next number, and two counters made separately must count independently.

```scheme
(define (make-counter)
  (let ((count 0))
    (lambda ()
      (set! count (+ count 1))
      count)))
```

Run it with two counters interleaved. Then answer in your write-up: what exactly did each returned function capture, and where does that captured value live once `make-counter` has returned? Compare a closure with an object in two or three sentences.

That `(let ((count 0)) ...)` at the top of `make-counter` is the same `let` the primer below covers in more depth: it is what gives this counter a private variable that nothing outside the function can see or reset. If you have not written `let` before this exercise, read the primer first and come back.

---

## Tools You'll Need First: `let`, Association Lists, `assq`, and a Second Look at `map` and `apply`

Part 4 assembles an evaluator out of four ingredients: `let` to name a value once, an association list to store lookups, `assq` to search that list, and `map`/`apply` to spread work across a list. You have already used `map` and `apply` once, in Part 1's Example 4, and `let` once, in `make-counter`. This section slows each one down. Each gets a worked example and a one-line practice step to run at your REPL before you meet all four wired together in the evaluator. **These practice steps are ungraded**, like the Scheme warmup exercise in Part 1. Nothing here goes in a deliverable. Run them anyway: they are the fastest way to keep Part 4 from stalling on syntax you have not typed yet.

### `let`: naming a value once

Every expression you have written so far names things only two ways: as a function parameter, or with a top-level `define`. `let` gives you a third way: a name that exists only for the extent of one expression. Use it when a function body needs the same value more than once and you do not want to compute it twice.

The shape is `(let ((name expression)) body)`. It evaluates `expression` once, binds it to `name`, and then evaluates `body` with that binding visible.

```scheme
(let ((x (+ 2 3)))
  (* x x))                   ; 25
```

Read that as: compute `(+ 2 3)`, call the result `x`, then compute `(* x x)` using that `x`. The parentheses nest more deeply than you are used to, so build them from the inside out. `(x (+ 2 3))` is one binding pair. `((x (+ 2 3)))` is a list holding that one pair. The `let` then wraps that list around a body.

You can bind more than one name in the same `let` by adding more pairs:

```scheme
(let ((a 3)
      (b 4))
  (+ (* a a) (* b b)))       ; 25
```

Scheme computes both `a` and `b` from the *outside* environment, not from each other. A binding that depends on another binding needs `let*`, which this assignment does not use. Keep every binding in a single `let` independent of the others.

> **Watch out!** A common typo is writing `(let (x (+ 2 3)) ...)` with one pair of parentheses missing. `let` always wants a *list of bindings*, so even a single binding needs its own extra parentheses: `((x (+ 2 3)))`, not `(x (+ 2 3))`. If Scheme complains that `x` is not a procedure, this is almost always why.

**Practice (ungraded):** at your REPL, bind a single name to `(* 6 7)` with `let` and use it twice in the body, once to print it and once to compare it against `42` with `=`. If you have already written `make-counter` in Part 3, you have already used `let` for real; this is just isolating it so the syntax is automatic before Part 4.

### Association lists: a list of pairs

An **association list**, usually just called an *alist*, is Scheme's simplest lookup table: a list where each element is a pair, `(key . value)`, built with `cons`.

```scheme
(define ops (list (cons '+ +) (cons '- -)))
```

`(cons '+ +)` builds the pair `(+ . #<procedure:+>)`, a symbol on the left and the actual addition procedure on the right; `car` of that pair gets you the symbol back, `cdr` gets you the procedure back. `ops` is then a list of two such pairs. Nothing here is a new data type: it is exactly the `list`, `cons`, `car`, and `cdr` from Part 1's Example 1, just arranged so that each element is itself a two-part `key . value` record.

**Practice (ungraded):** build a two-entry alist pairing the symbols `'red` and `'blue` with the strings `"stop"` and `"go"`. Use `car` and `cdr` on the first entry by hand to confirm you get `red` and `"stop"` back.

### `assq`: searching an alist

Writing `car`/`cdr` chains to search an alist by hand works, but Scheme gives you `assq` to do it directly. `(assq key alist)` walks the list looking for a pair whose `car` is `eq?` to `key`, and returns that whole pair if found, or `#f` if not.

```scheme
(define ops (list (cons '+ +) (cons '- -)))
(assq '+ ops)                ; (+ . #<procedure:+>)
(assq '* ops)                ; #f
```

Notice that `assq` gives you back the **pair**, not just the value; you still need `cdr` to pull the value out once you have found it:

```scheme
(cdr (assq '+ ops))          ; #<procedure:+>
```

Way B below relies on exactly that trick, as does the evaluator's variable extension if you choose it. Look up a symbol with `assq`, then `cdr` the result to get the value that symbol was paired with. If the symbol is not in the list, `assq` returns `#f`, and your code needs to decide what to do about that. A common pattern is:

```scheme
(let ((found (assq '* ops)))
  (if found
      (cdr found)
      (error "not found:" '*)))
```

That `let` is doing exactly the job from the section above: `(assq '* ops)` only gets called once, its result is named `found`, and both the `if` test and the `error` branch reuse that name instead of calling `assq` a second time.

**`assq` versus `assoc`, and why this assignment uses `assq`.** Scheme gives you two searching functions, and they differ in one way. `assq` compares keys with `eq?`, an identity comparison. `assoc` compares keys with `equal?`, a structural comparison. For symbol keys such as `'+`, `'-`, or `'x`, the two never disagree. The reader interns every symbol it reads, so two occurrences of `'+` are already the same object in memory. Whenever your keys are symbols, `assq` is the correct and cheaper tool. `assoc` earns its keep once your keys are lists, strings, or other structured data, where two values can be `equal?` (same contents) without being `eq?` (same object):

```scheme
(define points (list (cons '(0 . 0) "origin")))

(assq  '(0 . 0) points)      ; #f  -- eq? sees two DIFFERENT list objects
(assoc '(0 . 0) points)      ; ((0 . 0) . "origin")  -- equal? compares structure
```

Every lookup table in this assignment uses symbol keys, both `ops` here and the variable bindings in Part 4's optional extension. `assq` is therefore sufficient throughout, and you should not need `assoc` anywhere. Learn the difference anyway. A future lookup table keyed by lists or strings will silently miss every match under `assq`.

**Practice (ungraded):** using the `'red`/`'blue` alist you built above, call `assq` for `'red` and confirm you get the pair back, then call it for a key that is not in the list and confirm you get `#f`.

### `map`, once more

You have already seen `map` twice, once in Part 1's Example 4 and once in the `plusminus`/projectile work in Part 3. The one habit worth locking in before Part 4: `map`'s first argument is always a *function*, never a function call. `(map square '(1 2 3))` passes the function `square` itself into `map`, which calls it once per element. `(map (square 1) '(1 2 3))` calls `square` first, gets back a number, and then tries to use that number as a function. That fails.

```scheme
(map square '(1 2 3))        ; (1 4 9)
```

`map` always returns a list the same length as its input, with each element replaced by the function's result on that element. When those elements are themselves expressions, `map` calls your function once per expression. A function that can handle a nested expression therefore handles the nesting automatically, one layer at a time. That is the role `map` plays in Part 4's Step 2.

**Practice (ungraded):** call `(map square '(2 (+ 1 2) 4))` and read the error carefully. `square` only multiplies a number by itself, so it cannot handle the middle element, which is a list. Keep that error in mind. Part 4's evaluator handles *both* numbers and nested lists, which is why Step 2 can map `evaluate` over sub-expressions without hitting the error that `square` just hit.

### `apply`, once more

`apply` takes a function and a list, and calls the function with the list's elements spread out as separate arguments, rather than as one list argument.

```scheme
(apply + '(1 2 3))           ; same as (+ 1 2 3), which is 6
(+ '(1 2 3))                 ; error: + does not want a list as an argument
```

That second line is worth trying on purpose: `+` wants numbers, not a list of numbers, so calling it directly on a list fails, and `apply` is exactly the tool that unpacks the list into individual arguments first. This matters for Part 4 because after `map` evaluates every operand down to a plain number, you are left holding a procedure and a list of numbers, precisely the two things `apply` wants.

**Practice (ungraded):** call `(apply * '(2 3 4))` and confirm you get `24`, then call `(* '(2 3 4))` directly and read the error it produces.

### Putting the four together

Here is a small, complete example that uses all four forms from this section at once, entirely separate from the evaluator, so you can see them cooperate before Part 4 asks you to write something similar:

```scheme
(define ops (list (cons '+ +) (cons '- -) (cons '* *) (cons '/ /)))

(define lookup
  (lambda (sym)
    (let ((found (assq sym ops)))
      (if found
          (cdr found)
          (error "not found:" sym)))))

(apply (lookup '*) (map square '(2 3 4)))   ; (* 4 9 16) = 576
```

Walk that last line from the inside out. `map` squares each element of `'(2 3 4)`, giving `(4 9 16)`. `lookup` searches `ops` with `assq` for the symbol `'*`, using a `let` so `assq` runs once, and returns the multiplication procedure. `apply` then calls that procedure with the three squared numbers spread out as arguments. That is, in miniature, the three-step shape Part 4 asks you to build, with a fixed operator and a fixed list in place of a nested expression tree.

**Practice (ungraded):** run the block above as written, then change `'*` to `'+` and confirm the result changes to `29`. If both run correctly, you have every piece Part 4 needs.

---

## Part 4: An Expression Evaluator (22 points)

Write this one in `evaluate.scm`. It runs to about fifteen lines, and it is the oldest program in this language's history. John McCarthy's 1960 paper defined Lisp by writing an evaluator for Lisp in Lisp, and every interpreter you have ever used descends from that idea. You write the arithmetic-sized version of it in your first week.

### The representation

An arithmetic expression is a **nested list**, written exactly the way Scheme writes its own code. The `car` is the operator symbol; the `cdr` is the list of operands. A number is a leaf and stands for itself.

So `(* (+ 2 3) 4)` is this list:

```
'(* (+ 2 3) 4)              *
 ├─ car:  *                / \
 └─ cdr: ((+ 2 3) 4)      +   4
                         / \
                        2   3
```

That picture on the right is a **syntax tree**, and it is worth knowing now that you will meet it again. Later in this course, the Parser assignment's entire job is to build that same tree out of the flat text `(2 + 3) * 4`. Scheme hands it to you for free, because Scheme's source code *is* the tree. That is the trade the language made, and it is why the evaluator fits in fifteen lines here and does not there.

### The shape of the solution

Every recursion in Part 2 had the same two-case shape, and so does this one:

```scheme
(define evaluate
  (lambda (expr)
    (if (number? expr)
        expr                     ; base case: a number evaluates to itself
        ...)))                   ; recursive case: expr is a list
```

The recursive case has three steps. Work them in order. Each step reaches for one of the tools from the primer above, and each has a checkpoint you can run before moving on.

**Step 1: get the operator.**

```scheme
(car '(+ 1 2))                   ; +
```

That looks like it gave you addition. It did not. It gave you the **symbol** `+`, which is a name rather than the procedure that adds. Run the next line and read the error. This is the single place most students lose twenty minutes, so lose it deliberately now:

```scheme
((car '(+ 1 2)) 1 2)             ; error: + is not a procedure
```

You must convert the symbol into the procedure yourself. Two ways work, and you should understand both. The primer previewed each one.

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

(define lookup-op
  (lambda (sym)
    (let ((found (assq sym ops)))
      (if found
          (cdr found)
          (error "unknown operator:" sym)))))
```

Way B is the `ops` and `lookup` pattern from the primer, with the error message reworded to name the operator. Look at what Way B is: a list whose values **are procedures**. That is Part 3's functions as values doing load-bearing work rather than sitting in an exercise. Either way is acceptable. Say in your write-up which you chose.

If you choose Way B, the `let` inside `lookup-op` serves the same purpose it served in Part 2's `largest`. The expression `(assq sym ops)` is used twice, once in the `if` test and once in the `cdr`, so you compute it once and name it.

**Checkpoint.** Test `lookup-op` on its own before wiring it into anything:

```scheme
(lookup-op '+)                   ; #<procedure:+>
((lookup-op '+) 1 2)             ; 3
(lookup-op '&)                   ; error: unknown operator: &
```

The second line is the payoff. You now hold the procedure itself, so you can call it. The third line is the unknown-operator requirement below, already satisfied.

**Step 2: evaluate the operands.** Each operand may itself be a whole expression, so each one needs the same treatment. That means `evaluate` calls itself:

```scheme
(map evaluate (cdr expr))        ; on (* (+ 2 3) 4), the cdr is ((+ 2 3) 4) => (5 4)
```

This is the same `map` from Part 1's Example 4 and from the primer, except that the function you pass it is `evaluate` itself, the procedure you are in the middle of writing.

Compare this against the primer's practice step, where `(map square '(2 (+ 1 2) 4))` failed. `square` did not know what to do with a list. `evaluate` does know, because handling a list is its recursive case. That is why mapping `evaluate` over a mix of numbers and sub-expressions works where mapping `square` did not.

**Step 3: apply.** You now hold two things: a procedure, from Step 1, and a list of numbers, from Step 2. Those are exactly what `apply` takes.

```scheme
(apply + '(5 4))                 ; 9
```

This is the same `apply` from the primer's `(apply * '(2 3 4))` practice step, with the procedure coming from `lookup-op` instead of being written literally.

### Assembling the three steps

The three steps compose into one procedure. Write it yourself rather than looking for a finished version to copy. Nothing below is new material; it is a method for putting together the three pieces you have already run.

**Build it against a real value first.** The hardest part of assembly is that `expr` is a parameter, so you cannot see what it holds while you are writing the body. Remove that problem. At your REPL, bind `expr` to a test expression and build each piece against it, watching each one produce the right answer before you commit to it:

```scheme
(define expr '(* (+ 2 3) 4))     ; a scratch binding, only while you build
```

Now every fragment you write is something you can run.

**Work out the two arguments separately.** The recursive branch is a single call to `apply`, and `apply` takes exactly two arguments here. Build each one alone, at the REPL, against that scratch binding:

- **The first argument is a procedure.** You wrote the expression that produces it in Step 1's checkpoint, where you called `lookup-op` on a quoted symbol. Write the same call, but pass the operator out of `expr` rather than a symbol you typed. Step 1 says which accessor gets the operator. Run it: the result must print as a procedure, not as a symbol. If you see `*` rather than something that says procedure, you passed the symbol through without converting it.
- **The second argument is a list of numbers.** You wrote this one in Step 2, complete. Run it against the scratch binding: it must return `(5 4)`. Two numbers, no remaining lists. If a sub-expression is still there unevaluated, the function you mapped is wrong.

**Substitute, then generalize.** Put the two working fragments into the `apply` call in that order. Then replace the `...` in the skeleton with that call. The `if` keeps both branches: the true branch still returns `expr` itself, and this new call becomes the false branch. Finally, delete the scratch `define` of `expr`, because the parameter now supplies it.

**Check the parentheses by counting closers.** Assembly errors in this procedure are almost always parenthesis errors rather than logic errors, and Scheme reports them far from where you made them. Work outward from the innermost form. The `apply` call closes before the `if` closes, the `if` closes before the `lambda` closes, and the `lambda` closes before the `define` closes. Four closing parentheses end the procedure, one for each of those forms. If Scheme complains about an unexpected end of input, you are short one. If it complains about an extra close paren, you have one too many.

Nothing else belongs in the procedure. A `cond` with more than two branches, or a helper you did not test in a step above, means you have added something the three steps did not ask for.

**Checkpoint.** Your assembled procedure must produce these:

```scheme
(evaluate 42)                    ; 42   <- the base case alone
(evaluate '(+ 1 2))              ; 3    <- flat, one operator
(evaluate '(* (+ 2 3) 4))        ; 20   <- one level of nesting
```

Work them in that order, because each one tests strictly more than the last. Read a failure this way:

| What fails | Where to look |
|---|---|
| The first one | Your base case. The `if` test or the true branch is wrong. |
| The first passes, the second fails with "not a procedure" | Step 1. You handed `apply` a symbol instead of a procedure. |
| The first two pass, the third fails | Step 2. You are handing `apply` a list that still contains an unevaluated expression. |
| All three pass | You are done. |

Count the lines when you are finished; the write-up asks for the number.

### Optional and ungraded: trace it by hand

This step is optional. You submit none of it, in the same way the primer's practice steps are not submitted. Do it if the recursion still feels like magic, because filling the table in is usually the moment it stops.

Trace `(evaluate '(* (+ 2 3) 4))` by hand. Each row is one call to `evaluate`. Fill in what that call receives, which branch of the `if` it takes, and what it returns. The first row is done for you.

| Call | `expr` received | Branch taken | Returns |
|---|---|---|---|
| 1 | `(* (+ 2 3) 4)` | list, so the recursive branch | |
| 2 | `(+ 2 3)` | | |
| 3 | `2` | | |
| 4 | `3` | | |
| 5 | `4` | | |

Answer two questions for yourself once the table is full. Which rows return without making any further call, and what do those rows have in common? Which row cannot return until other rows have returned, and why?

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

What should `(evaluate '(+ 1 (& 2 3)))` do? Your evaluator must **detect the unknown operator and report it**, naming the offending symbol, rather than crashing with whatever Scheme says by default. `error` is the procedure you want, and `lookup-op`'s `else` branch (Way A) or its `if found ... (error ...)` branch (Way B) is where that detection lives. This is your first error message as a language implementer. It must meet the standard you will be held to in the Lexer and Parser assignments: say what was wrong, and say which thing was wrong.

### Required: one extension, your choice of two

Pick **one** and make it work. Each description below gives you the reasoning you need. Neither gives you the code.

#### Option A: any number of arguments

**The goal.** `(evaluate '(+ 1 2 3 4))` returns `10`, and `(evaluate '(* 2 3 4 5))` returns `120`.

**Start by testing, not by editing.** Run those two calls against the evaluator you already have. If you built Step 3 with `apply`, they very likely work already, and the extension is then an explanation rather than a change.

**Why it already works, if it does.** Trace the two steps that touch the operand list. `map` returns a list the same length as its input, so a four-operand expression produces four numbers rather than two. `apply` then spreads however many elements that list holds into separate arguments. Neither step hardcodes a count, and neither one checks for two. Scheme's `+` and `*` accept any number of arguments, so the whole path is indifferent to arity. Say this in one sentence in your write-up, naming the two steps, rather than changing working code.

**When it does not already work.** Some students build Step 3 another way: pulling out `(car ...)` and `(cadr ...)` by hand, or folding the operands two at a time. Either approach writes arity two into the evaluator. Find that assumption and remove it. The cleanest repair is to reach the `apply` shape the three steps describe, because `apply` makes arity somebody else's problem.

**Two edge cases worth trying.** Check `(evaluate '(+ 5))`, a single operand, and `(evaluate '(+))`, none at all. Scheme's `+` returns `0` for no arguments and `5` for one, so both should work without special handling. Subtraction and division do not behave the same way with one argument, so try `(evaluate '(- 5))` and say what you get and why. Report whatever you find rather than making it match a guess.

#### Option B: variables

**The goal.** `(evaluate '(+ x 1) '((x . 5)))` returns `6`.

That second argument is an association list, the structure the primer covered. It maps a symbol to a value, exactly as `ops` maps a symbol to a procedure. It has a name: this is an **environment**, the same structure the Interpreter assignment builds later and the Environments and Scope lab makes you get right.

**Change 1: the signature.** `evaluate` takes two parameters now, the expression and the environment. Every existing call site changes to match, including the recursive ones.

**Change 2: a third case.** Your evaluator currently asks one question, "is this a number?", and has a branch for yes and a branch for no. It now needs three outcomes, so a `cond` replaces the `if`:

1. A **number** evaluates to itself, unchanged from before.
2. A **symbol** is a variable. Look it up in the environment and return the value it is bound to.
3. Anything else is a **list**, handled the same way as before.

Scheme gives you `symbol?` to test the second case, the way `number?` tests the first.

**Change 3: the lookup.** The variable case is the `assq` pattern from the primer, applied to the environment rather than to `ops`. Search for the symbol, and `cdr` the pair you get back to reach the value. `assq` returns `#f` when the symbol is absent, so decide now what an unbound variable should do and write that decision down. Reporting it with `error`, naming the offending symbol, matches what you already do for an unknown operator, and matches the standard the Lexer and Parser assignments hold you to.

**Change 4: threading the environment.** This is the part that catches people, so work it deliberately. Every recursive call needs the same environment, but `map` calls the function you give it with exactly one argument, the list element. Your `evaluate` now wants two. Those do not fit.

The fix is a closure, the same idea as `make-counter` in Part 3. Instead of handing `map` the name `evaluate`, hand it a one-argument `lambda` whose body calls `evaluate` with that one argument **and** with the environment. The environment is not a parameter of that lambda; it is captured from the surrounding scope, which is what makes this a closure. Write it out and then answer, for your write-up, what exactly got captured and where it lives.

**One subtle trap.** The operator in `(+ x 1)` is the symbol `+`, and symbols are now a case your evaluator handles. Test for the symbol case before separating the operator from the operands, and the evaluator will look up `+` in the environment, fail to find it, and report `+` as unbound. Keep the operator on the `lookup-op` path and the operands on the `evaluate` path. Only operands are evaluated as expressions; the operator is never one.

**Test these.** A bare variable, `(evaluate 'x '((x . 5)))`. A variable inside nesting, `(evaluate '(* x (+ y 1)) '((x . 2) (y . 3)))`. An unbound variable, to confirm your decision from Change 3 fires. And an expression with no variables at all, to confirm you did not break the cases that already worked.

### What to write up

In `writeup.md`:

- How many lines is your `evaluate`? Count them.
- What is `(map evaluate (cdr expr))` doing that a `for` loop over the operands would not? Answer in terms of the nesting, not in terms of style.
- Where does the recursion bottom out, and how do you know it terminates on every well-formed expression?
- If you used `let` or `assq` anywhere in `evaluate.scm` or `lookup-op`, say where and why; if you did not use them at all, say what you used instead.

---

## Deliverables

Submit a ZIP containing `part0.md` (both loop versions, their output, and your readability argument), `setup.md` (route, version, four transcripts, one error), `recursion.scm`, `higher_order.scm`, `evaluate.scm`, and a `writeup.md` answering the questions raised in Parts 2, 3, and 4. Include the output of each `.scm` file, either captured in a comment at the bottom of the file or pasted into the write-up. The primer's practice steps are ungraded and do not need to be submitted.

## Grading Breakdown

| Component                       | Points  |
| -------------------------------- | ------- |
| Part 0: The Functional Rewrite   | 10      |
| Part 1: Getting Scheme Running   | 18      |
| Part 2: List Recursion           | 32      |
| Part 3: Functions as Values      | 18      |
| Part 4: An Expression Evaluator  | 22      |
| **Total**                        | **100** |

## Reflection Prompts

- Which was harder: getting Scheme installed, or getting your first recursion to terminate? What does your answer suggest about where the real cost of a new language sits?
- Name one thing that was genuinely easier here than it would have been in Python, and one thing that was genuinely harder.
- Your `evaluate` walks a syntax tree in about fifteen lines. Later in this course you will write a parser whose only job is to *build* that tree from flat text. Before you write it: how much code do you think that will take, and what exactly is the parser doing that Scheme did for you here? I will ask you to look back at your answer.
- Of `let`, `assq`, `map`, and `apply`, which one took the longest to feel natural, and what finally made it click?
