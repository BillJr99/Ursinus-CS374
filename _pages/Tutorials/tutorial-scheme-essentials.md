---
layout: notes
permalink: /Tutorials/SchemeEssentials
title: "CS374: Scheme Essentials for the Programming Languages Course"

info:
  coursenum: CS374
  goals:
    - "Installed a Scheme, or opened one in a browser, and run a file rather than only typing at a prompt"
    - "Read and wrote s-expressions fluently, including the quote that separates data from a function call"
    - "Defined functions with `define` and `lambda`, and explained why `define` binds a name rather than assigning to a variable"
    - "Wrote recursive functions over lists with `car`, `cdr`, `cons`, and a `null?` base case, since Scheme has no loop"
    - "Passed functions as values and wrote a fold that takes its operator as a parameter"
    - "Wrote a closure with `make-counter` and said exactly what it captured"

tags:
  - scheme
  - functional

---
# Tutorial: Scheme Essentials for the Programming Languages Course

## Learning Goals

By the end of this tutorial, you will have:

- Installed a Scheme, or opened one in a browser, and run a file rather than only typing at a prompt
- Read and written s-expressions fluently, including the quote that separates data from a function call
- Defined functions with `define` and `lambda`, and explained why `define` binds a name rather than assigning to a variable
- Written recursive functions over lists with `car`, `cdr`, `cons`, and a `null?` base case, since Scheme has no loop
- Passed functions as values, and written a fold that takes its operator as a parameter
- Written a closure with `make-counter` and said exactly what it captured

Scheme is to programming languages what Latin is to the Romance languages: it exposes the undiluted core the others are built from, stripped of the ornamental syntax that usually hides the machinery.  It has essentially **one syntactic rule**, which means there is very little to memorize and nowhere for the semantics to hide.

This tutorial is the reference companion to the *Functional Programming in Scheme* session and the **Functional Programming with Scheme** assignment.  Everything the assignment asks you to write is worked here at least once.  Read it with a REPL open; nothing below is worth reading without running.

**What you need:**

- **The course dev container**: already has one; `guile` gives you a REPL, `guile file.scm` runs a file (see the [Development Environment tutorial]({{ site.baseurl }}/Tutorials/DevEnvironment))
- **[try.scheme.org](https://try.scheme.org)**: a full Scheme REPL in a browser tab, nothing to install
- The course's own [Scheme warmup exercise]({{ site.baseurl }}/Modules/Scheme/Warmup/Exercise), which runs Scheme in the page and checks your answer
- Or a local install, which is what you eventually want:
  - **A Python Scheme, no package manager needed:** `git clone https://github.com/BillJr99/scheme-interpreter.git`, then `python scheme.py <your scheme file>`
  - **Cygwin (Windows):** install `guile` from the Cygwin installer
  - **Ubuntu (Linux):** `sudo apt install mit-scheme`
  - **Mac:** `brew install mit-scheme`, if you have [homebrew](https://brew.sh/)

---

# Part 1: The One Syntax Rule

## 1.1 Everything Is (operator operands ...)

Every compound form in Scheme is a parenthesized list with the operator first.  Arithmetic is not special, and neither is anything else:

```scheme
(+ 2 3)                      ; 5
(* (+ 2 3) 4)                ; 20
(define pi 3.14159)
(if (> 5 0) "positive" "not positive")
```

Notice what is missing.  There is no precedence table, because prefix notation does not need one: the nesting *is* the structure.  There is no associativity rule.  There is no statement-versus-expression divide, because everything is an expression with a value.

Here is why that matters in this course.  Most of October is spent building the machinery that recovers, from flat infix text like `2 + 3 * 4`, the tree a Scheme programmer simply writes: grammars, then derivations and ambiguity, then a precedence ladder, then a recursive descent parser, then an abstract syntax tree.  All of it exists because `2 + 3 * 4` does not say what it means.  Scheme's parentheses say what they mean.

| Python | Scheme |
|---|---|
| `f(a, b)` | `(f a b)` |
| `2 + 3` | `(+ 2 3)` |
| `(2 + 3) * 4` | `(* (+ 2 3) 4)` |
| `[1, 2, 3]` | `'(1 2 3)` |
| `lst[0]` / `lst[1:]` | `(car lst)` / `(cdr lst)` |
| `def f(x): return x + 1` | `(define (f x) (+ x 1))` |
| `lambda x: x + 1` | `(lambda (x) (+ x 1))` |

## 1.2 Quote: the Difference Between Data and a Call

```scheme
(+ 1 2)                      ; 3        -- a call, evaluated
'(+ 1 2)                     ; (+ 1 2)  -- a three-element list, as data
(1 2 3)                      ; ERROR: application: not a procedure
'(1 2 3)                     ; (1 2 3)
```

> **Watch out!**  Forgetting the quote is the single most common beginner error in this language.  `(1 2 3)` tells Scheme to call the function named `1` with arguments `2` and `3`, and `1` is not a function.  Trigger this error on purpose once, right now, and read the message; it is the One Syntax Rule explaining itself.

That `'(+ 1 2)` is an ordinary list is not a curiosity.  It is the property called **homoiconicity**: a Scheme program is a data structure the language itself can take apart and rebuild, which is why Lisp macros are just functions over lists.

## 1.3 Lists, and the Three Operations That Build Them

```scheme
(define L (list 'a 'b 'c))
(car L)                      ; a          -- the first element
(cdr L)                      ; (b c)      -- everything after the first
(cons 'z L)                  ; (z a b c)  -- a new list with z on the front
(null? '())                  ; #t         -- true for the empty list
(pair? L)                    ; #t         -- true for a nonempty list
```

`car` and `cdr` are Scheme's names for what most languages call `head` and `tail`.  They are historical accidents from 1950s IBM register names and they are not going to start making sense, so read them as "the first one" and "the rest."  Calling either on the empty list is a runtime error, which is why every list recursion checks its base case first.

---

# Part 2: Functions

## 2.1 define and lambda

```scheme
(define square
  (lambda (n)
    (* n n)))

(define (square n) (* n n))  ; shorthand for exactly the same thing

(square 7)                   ; 49
```

Reading the long form first makes `lambda` feel ordinary rather than exotic: `define` binds a name to a value, and a `lambda` expression is just one kind of value.

> **Watch out!**  `define` is not assignment.  `(define x 5)` introduces a name binding in the current environment; it does not create a mutable box you update in a loop.  If you catch yourself reaching for `(set! x (+ x 1))`, stop and ask how to pass the updated value forward as a function argument instead.  That question is what produces the accumulator pattern.

## 2.2 Conditionals

```scheme
(define (sign n)
  (if (< n 0) 'negative 'non-negative))

(define (classify n)
  (cond ((< n 0) 'negative)
        ((= n 0) 'zero)
        (else    'positive)))

(map classify '(-3 0 7))     ; (negative zero positive)
```

`if` takes exactly two branches; `cond` takes as many as you like and is the one you will reach for.

## 2.3 Functions Are Values

```scheme
(define add +)               ; not a typo
(add 3 2)                    ; 5
```

`+` is a value, the addition function, and `define` binds names to values of any kind.  Nothing in Scheme distinguishes a name holding a number from a name holding a function, and the rest of this tutorial is built on that one fact.

---

# Part 3: Recursion Is the Loop

Scheme has no `while`.  Iteration is recursion over a list: peel one element off the front with `car`, do something with it, and recur on `cdr`.

## 3.1 sumlist

```scheme
(define sumlist
  (lambda (L)
    (if (null? (cdr L))
        (car L)
        (+ (car L) (sumlist (cdr L))))))

(sumlist (list 1 2 3))       ; 6
```

Note where this one stops: at the *last element*, not at the empty list.  That means `(sumlist '())` is an error rather than 0.  Whether that is a bug or a deliberate statement about what summing nothing means is a real design question, and the assignment asks you to take a side.

## 3.2 largest, and Why the Obvious Version Is Expensive

```scheme
(define largest
  (lambda (L)
    (if (null? (cdr L))
        (car L)
        (if (>= (car L) (largest (cdr L)))
            (car L)
            (largest (cdr L))))))
```

This is correct and wasteful: `(largest (cdr L))` is evaluated in the test *and* again in the else branch, so the work doubles at every level.  Name the subresult once with `let`:

```scheme
(define largest2
  (lambda (L)
    (if (null? (cdr L))
        (car L)
        (let ((largestval (largest2 (cdr L))))
          (if (>= (car L) largestval)
              (car L)
              largestval)))))
```

On a list of sixteen elements whose largest is last, the first version makes 65,535 calls and the second makes 16.  Same answer, same shape, and the only difference in the source is a `let`.

## 3.3 czr, and Tail Position

```scheme
(define czr
  (lambda (l)
    (if (null? (cdr l))
        (car l)
        (czr (cdr l)))))

(czr '(1 2 3 4))             ; 4
```

`czr` is not a standard Scheme procedure; it is ours.  It walks to the end of a list and hands back the last element.  Notice what makes it different from `sumlist`: nothing happens after the recursive call returns.  A call in that position is a **tail call**, and a Scheme implementation is required to run it in constant stack space, which is why recursion here costs no more than a loop.  Python makes no such guarantee, which is why Python programmers reach for `for` even when recursion reads better.

`czr` as written breaks on the empty list.  Guard it, and decide deliberately what the empty list should return:

```scheme
(define czr
  (lambda (l)
    (if (not (pair? l))
        l
        (if (null? (cdr l))
            l
            (czr (cdr l))))))
```

---

# Part 4: Higher-Order Functions

## 4.1 map and apply

```scheme
(define L1 '(1 2 3))
(define L2 '(4 5 6))
(map - L1 L2)                ; (-3 -3 -3)   -- element by element, two lists at once
(apply + '(1 2 3))           ; 6            -- spreads the list into the arguments
(map (lambda (x) (* x x)) '(1 2 3 4 5))     ; (1 4 9 16 25)
((lambda (x) (* x x)) 5)     ; 25           -- a lambda applied on the spot
```

`map` takes a *function* as its first argument.  `apply` does the opposite: it takes one function and one list, and spreads the list out as that function's arguments, so `(apply + '(1 2 3))` is `(+ 1 2 3)`.

## 4.2 An Anonymous Function, Applied Immediately

```scheme
(define plusminus
  (lambda (a b)
    ((lambda (x y) (list (+ x y) (- x y)))
     a b)))

(plusminus 6 2)              ; (8 4)
```

There are two functions here.  The outer one is named; the inner one is created, applied to `a` and `b`, and thrown away.  Written out, the call is `((lambda (x y) ...) a b)`, which is the One Syntax Rule again with a function *expression* in the operator position instead of a function *name*.

## 4.3 Lifting the Operator Out

```scheme
(define oplist
  (lambda (op L)
    (if (null? (cdr L))
        (car L)
        (op (car L) (oplist op (cdr L))))))

(oplist * (list 2 4 6))      ; 48
(oplist + (list 2 4 6))      ; 12
(apply * (list 2 4 6))       ; 48
```

`oplist` is `sumlist` with the operator promoted to a parameter.  That one change turns a function that sums into a function that does whatever you hand it, and once you see it, `reduce` and `fold` stop being library functions to memorize and become a shape you recognize.

---

# Part 5: Closures

```scheme
(define (make-counter)
  (let ((count 0))           ; the environment the closure captures
    (lambda ()               ; the lambda forms the closure
      (set! count (+ count 1))
      count)))

(define counter1 (make-counter))
(define counter2 (make-counter))

(counter1)                   ; 1
(counter1)                   ; 2
(counter2)                   ; 1
(counter1)                   ; 3
```

`make-counter` returns a function that still has access to `count`, long after `make-counter` has returned and even though `count` is visible nowhere else in the program.  The returned function plus the environment it captured is a **closure**.

`counter1` and `counter2` each captured their *own* `count`, which is why they count independently.  This is also the one place in this tutorial where `set!` earns its keep: the whole point is state that persists between calls.

A closure is a small object with exactly one method.  An object is a closure with a dispatch table.  Which of those framings you find more natural says a good deal about which paradigm you grew up in, and the question comes back in November when the course builds environments and first-class functions for real.

---

# Part 6: Exercises

These are the same exercises as the **Functional Programming with Scheme** assignment; if you are working the assignment, work them there.

1. Write `count`, which returns how many items are in a list.  Use `czr` as a guide to traversing the list; note that its base case cannot look at `(car L)` at all.
2. Write `reverse-list` using only `car`, `cdr`, and `cons`.  Then count how many `cons` calls it makes for a list of length *n*, and say whether you are happy with that.
3. Fix `sumlist` so that `(sumlist '())` returns 0, and argue in two sentences whether the original was a bug or a decision.
4. Write the linear equation `y = mx + b` as a function of three parameters.  Then write projectile distance, `v0*t + 0.5*a*t^2`, twice: once with `(* t t)` spelled out and once with your `square` substituted in.  Say what the substitution bought you, given that it did not change the answer.
5. Add a `reset` capability to `make-counter`.  You will have to decide what the returned value even *is* once there is more than one operation, and that decision is exactly the one object-oriented languages made.
6. Write a tiny expression evaluator: represent an arithmetic expression as a nested list, the way Scheme writes its own code, and evaluate it.  `(evaluate '(* (+ 2 3) 4))` should give 20.  A number evaluates to itself; a list is an operator and its arguments, so evaluate the arguments first and then apply the operator.  Fifteen lines will do it.

---

## Further Reading

- [The Scheme Programming Language](https://www.scheme.com/tspl3/) (R. Kent Dybvig): the standard reference, and readable front to back
- [Structure and Interpretation of Computer Programs](https://mitp-content-server.mit.edu/books/content/sectbyfn/books_pubs/6515/sicp.pdf) (Abelson and Sussman), Chapter 1: the functional core, in Scheme
- [Closures in Scheme](https://www.artificialworlds.net/presentations/scheme-03-closures/scheme-03-closures.html) (Andy Balaam): where `make-counter` comes from
- [QuickSort in Scheme](https://riptutorial.com/scheme/example/10903/quicksort): eight lines, worth reading beside your own sorting code
- [Implementing Python as Syntax Rules for Racket](https://github.com/pedropramos/PyonR/): what "one syntax rule" buys you, taken to its logical end
- [Build a Complete Interpreter in Python]({{ site.baseurl }}/Tutorials/BuildAnInterpreter): the metacircular evaluator, if you want to write the language you have been using
- Runnable course archives: [SchemeSumList.zip]({{ site.baseurl }}/files/replit/SchemeSumList.zip), [SchemeLargestElement.zip]({{ site.baseurl }}/files/replit/SchemeLargestElement.zip), [czrEmptyListScheme.zip]({{ site.baseurl }}/files/replit/czrEmptyListScheme.zip), [ApplyScheme.zip]({{ site.baseurl }}/files/replit/ApplyScheme.zip), [ClosureStateScheme.zip]({{ site.baseurl }}/files/replit/ClosureStateScheme.zip), [QuickSortScheme.zip]({{ site.baseurl }}/files/replit/QuickSortScheme.zip)
