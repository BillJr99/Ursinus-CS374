<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374-Fall2026/gh-pages/_pages/Activities/liascript-scheme.md or locally via https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374-Fall2026/gh-pages/_pages/Activities/liascript-scheme.md

import: https://raw.githubusercontent.com/liascript/CodeRunner/master/README.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

# Functional Programming in Scheme, Part 2

Last session you met the functional paradigm and typed your first few Scheme expressions.  Today we stay in Scheme long enough for it to stop feeling strange.

Scheme is to programming languages what Latin is to the Romance languages: it exposes the pure, undiluted core that every other language is built from, stripped of the ornamental syntax that usually hides the machinery beneath.  Studying it in a PL course is not about collecting another language.  It is about seeing, perhaps for the first time, that a language can be so minimal that its programs and its data are literally the same thing.  Once you have felt that, you will read every other language differently, including the one your team is going to design.

## Learning Goals

By the end of this activity, you will be able to:

- Read and write Scheme's one syntactic form, the parenthesized prefix application, and explain why it needs no precedence rules
- Define functions with `define` and `lambda`, and explain why `define` binds a name rather than assigning to a variable
- Write recursive functions over lists using `car`, `cdr`, `cons`, and a `null?` base case, since Scheme has no loop
- Pass functions as values and receive them as parameters, using `map`, `apply`, and functions you write yourself
- Explain what a closure captures, and compare a closure with an object
- Build an object out of a closure by dispatching on a message, and capture a table rather than a number to memoize a function

> **Before You Begin:** This activity assumes you can:
>
> - Write and call a function in Python, including one that calls itself recursively
> - Explain what a call stack is and what happens to it during nested calls
> - Say what it means for a function to take another function as an argument
>
> If any of these feel shaky, review them first.  Everything else you need is here.

| Python | Scheme | Notes |
|--------|--------|-------|
| `def f(x): return x + 1` | `(define (f x) (+ x 1))` | Parentheses wrap everything, and the operator comes first |
| `f = lambda x: x + 1` | `(define f (lambda (x) (+ x 1)))` | The same thing, written the long way |
| `if x > 0: ...` | `(if (> x 0) ...)` | The condition is just another expression in parentheses |
| `[1, 2, 3]` | `'(1 2 3)` | The quote says "data, do not evaluate" |
| `f(a, b)` | `(f a b)` | Every call looks the same; there are no infix operators |
| `lst[0]` / `lst[1:]` | `(car lst)` / `(cdr lst)` | First element, and everything after it |

Today's path runs **get a REPL open $\rightarrow$ one syntax rule $\rightarrow$ recursion as the only loop $\rightarrow$ functions as values $\rightarrow$ closures**.

---

## Directions and Group Roles

Work in your POGIL team with your rotated roles (**Manager**, **Recorder**, **Presenter**, **Reflector**).  Today is hands-on, so the Manager drives the REPL and everyone predicts before running.  Please think each model through on your own first, then talk it over with your group.  The Recorder posts your answers to the Class Activity Questions discussion board, and the Presenter reports out wherever you disagreed or found another approach.

> **How today runs.**  Parts I through III are the core.  Part III's closure model is the one to protect if we run short, because "compare closures and objects" is the question that pays off again in November.  The Scheme assignment goes out Thursday and is due the Thursday after, and it asks you to write everything you read today, so treat these models as worked examples for homework you already have.

---

## Key Concepts

Here is a plain-English glossary of the terms this activity uses.  Please come back to this table whenever one of them starts to feel slippery.

| Term | Plain-English meaning |
|---|---|
| **s-expression** | A parenthesized list, like `(+ 1 2)`.  Scheme's only compound form, used for both code and data |
| **`define`** | Introduces a name binding.  It is not assignment; you do not update it later |
| **`lambda`** | Makes a function value.  `define` just gives that value a name |
| **`car`** | The first element of a list |
| **`cdr`** | The rest of the list, everything after the first element |
| **`cons`** | Builds a new list by putting one element on the front of an existing list |
| **`null?`** | True for the empty list `'()`.  This is how a recursion knows to stop |
| **`pair?`** | True for a nonempty list.  The guard that keeps `car` from being called on nothing |
| **quote (`'`)** | Suppresses evaluation.  `'(1 2 3)` is a list of three numbers, not a call to a function named `1` |
| **higher-order function** | A function that takes a function as an argument or returns one |
| **closure** | A function value that remembers the environment it was created in |
| **`set!`** | Assignment to a binding that already exists.  The one thing that turns a captured variable into memory |
| **message passing** | Handing a procedure a symbol so it decides which operation you meant.  A dispatcher plus a shared environment is an object |
| **memoization** | Caching a function's answers in state only that function can see, so repeated arguments cost a lookup instead of a recomputation |
| **tail call** | A recursive call whose result is returned directly, with no work left to do after it returns |

---

# Part I: Getting Scheme Running

## 1.  Four Ways to Get a REPL

You cannot learn this by reading it.  Get a prompt in front of you before the first model, using whichever of these is least painful on your machine.

**No install, right now.**  Open [try.scheme.org](https://try.scheme.org) in a browser tab.  It gives you a full Scheme REPL with nothing to set up, and it is the fastest way to be typing in the next thirty seconds.  The course's own [Scheme warmup exercise](https://www.billmongan.com/Ursinus-CS374-Fall2026/Modules/Scheme/Warmup/Exercise) also runs Scheme directly in the page and checks your answer.

**Install it locally**, which you will want eventually:

- **A Python Scheme, no package manager needed:** `git clone https://github.com/BillJr99/scheme-interpreter.git`, which gives you a `scheme.py` you can run as `python scheme.py <your scheme file>`
- **Cygwin (Windows):** install `guile` from the Cygwin installer
- **Ubuntu (Linux):** `sudo apt install mit-scheme`
- **Mac:** `brew install mit-scheme`, provided you have installed [homebrew](https://brew.sh/)

Every code block below is real Scheme.  Type it, run it, then change something and run it again.  The comments after `;` show what each expression evaluates to.

> **Watch out!**  Forgetting the quote before a list literal is the single most common beginner error in this language.  Writing `(1 2 3)` tells Scheme "call the function named `1` with arguments `2` and `3`."  Since `1` is not a function, you get an error like `application: not a procedure`.  Write `'(1 2 3)` when you mean a list of data.  Trigger this error on purpose once today, and read the message out loud; you will save yourself an hour later.

---

# Part II: One Syntax Rule and the Functional Core

## 2.  Everything Is (operator operands ...)

**Scheme has essentially one syntactic form**: the parenthesized prefix application `(f a b c)`.  Arithmetic is not special.  `(+ 2 3)` is 5, and `(* (+ 2 3) 4)` is 20.  Definitions, conditionals, and functions are *special forms* wearing exactly the same parentheses:

```scheme
(define pi 3.14159)
(define (square x) (* x x))
(if (> x 0) "positive" "not positive")
(lambda (x) (* x x))
```

**Notice what vanished.**  There is no precedence, because prefix notation needs none: the tree is explicit in the nesting.  There is no associativity rule.  There is no statement-versus-expression divide, because everything is an expression with a value.

Hold onto that.  In a few weeks this course will spend three sessions building a parser whose entire job is to recover, from flat infix text like `2 + 3 * 4`, the tree that a Scheme programmer simply *writes*.  The parentheses you are typing today are the tree.  When we get to grammars and precedence ladders, come back to this page and ask what all that machinery is buying us, and what it costs.

## Model 1: Definitions, `square`, and `pow`

Two ways to say the same thing, and then a function that calls itself:

```scheme
(define L (list 'a 'b 'c))
(car L)                      ; a
(cdr L)                      ; (b c)

(define x (+ 3 2))
(+ x 5)                      ; 10

(define add +)
(add 3 2)                    ; 5
```

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

### Reading the Code

- `(define add +)` is not a typo.  `+` is a *value*, the addition function, and `define` gives it a second name.  Nothing in Scheme distinguishes "a variable holding a number" from "a variable holding a function," and that single fact is what the rest of today is built on.
- `square` is written the long way on purpose: `(define (square n) (* n n))` is shorthand for exactly what you see.  Reading the long form first makes `lambda` feel ordinary rather than exotic.
- `pow` has the shape every recursion in this course will have: a base case that answers directly, and a recursive case that does a little work and asks a smaller version of itself.

> **Watch out!**  `define` in Scheme is not assignment in the imperative sense.  `(define x 5)` introduces a name binding in the current environment; it does not create a mutable box you update in a loop.  If you catch yourself wanting to write `(set! x (+ x 1))`, stop and ask how to pass the updated value forward as a function argument instead.

### Critical Thinking Questions

1.  What is a statement in Scheme?
2.  What shared variables exist in this program?
3.  How are function parameters handled in Scheme?  Are they passed by value or by reference?
4.  What is a function in Scheme?  How is it represented?
5.  Rewrite `pow` using the shorthand `(define (pow n k) ...)` form.  Does anything about its meaning change?

---

## 3.  Recursion Is the Loop

Scheme has no `while`.  Iteration is recursion, almost always over a list, and a list is built from `cons` cells that you take apart with `car` (the first element) and `cdr` (everything else).

> **Watch out!**  `car` and `cdr` are Scheme's names for what most languages call `head` and `tail`.  The names are historical accidents from 1950s IBM register names, and they are not going to start making sense, so just read `(car lst)` as "the first one" and `(cdr lst)` as "the rest."  Calling either on the empty list `'()` is a runtime error, which is why every list recursion checks its base case first.

## Model 2: `sumlist` and `largest`

```scheme
(define sumlist
  (lambda (L)
    (if (null? (cdr L))
        (car L)
        (+ (car L) (sumlist (cdr L))))))

(sumlist (list 1 2 3))       ; 6
```

```scheme
(define largest
  (lambda (L)
    (if (null? (cdr L))
        (car L)
        (if (>= (car L) (largest (cdr L)))
            (car L)
            (largest (cdr L))))))

(largest (list 1 2 4 3))     ; 4
```

```scheme
(define largest2
  (lambda (L)
    (if (null? (cdr L))
        (car L)
        (let ((largestval (largest2 (cdr L))))
          (if (>= (car L) largestval)
              (car L)
              largestval)))))

(largest2 (list 1 2 4 3))    ; 4
```

Both versions of `largest` return the same answer.  They do not cost the same.  The cell below counts the recursive calls each one makes, so you can see the difference rather than take my word for it.

```python
# The two versions of largest, transliterated into Python so we can count calls.
# car(L) is L[0]; cdr(L) is L[1:]; (null? (cdr L)) is len(L) == 1.

calls = {"largest": 0, "largest2": 0}

def largest(L):
    calls["largest"] += 1
    if len(L) == 1:
        return L[0]
    if L[0] >= largest(L[1:]):      # first recursive call
        return L[0]
    return largest(L[1:])           # second recursive call, same work again

def largest2(L):
    calls["largest2"] += 1
    if len(L) == 1:
        return L[0]
    largestval = largest2(L[1:])    # computed ONCE, then named
    return L[0] if L[0] >= largestval else largestval

for n in (4, 8, 12, 16):
    data = list(range(1, n + 1))    # worst case: the largest element is last
    calls["largest"] = calls["largest2"] = 0
    assert largest(data) == largest2(data) == n
    print(f"  n = {n:2d}   largest: {calls['largest']:6d} calls    "
          f"largest2: {calls['largest2']:3d} calls")

print()
print("  Same answer, same shape, wildly different cost: doubling every level")
print("  against one call per level.  The only difference in the source is that")
print("  largest2 names the subresult with let instead of recomputing it.")
```
@LIA.eval(`["main.py"]`, `none`, `python3 main.py`)

### Reading the Code

- `sumlist` stops at the *last element*, not at the empty list: its base case is `(null? (cdr L))`.  That choice means `(sumlist '())` is an error rather than 0.  Whether that is a bug or a design decision is question 9 below.
- `largest` evaluates `(largest (cdr L))` twice on every level.  Each of those calls does the same thing again, and the doubling compounds.  `largest2` calls it once and gives the answer a name with `let`.
- `let` introduces a binding for the duration of its body.  It is the tool for "I need this value more than once."

### Critical Thinking Questions

6.  How might you improve upon the implementation of the `largest` function?
7.  Trace `(sumlist '(1 2 3))` by hand, writing every call and every return.  Where does the addition for `1` actually happen: on the way down, or on the way back up?
8.  In your own words, define tail recursion.  Do you see instances of tail recursion in these examples?  Draw a call stack for one of these examples.
9.  Using the `pair?` directive, which returns `#t` if the parameter is a nonempty list, add a check to one of these list recursion examples to ensure that `null` is returned if an empty list is passed.

### Try It Yourself

Type `sumlist` into your REPL and get it running.  Then write `product`, which multiplies a list instead of summing it, by changing exactly one character.  Then write `count`, which returns how many items are in a list; note that its base case cannot look at `(car L)` at all.

---

# Part III: Functions Are Values

## 4.  Passing, Returning, and Capturing

You have already seen `(define add +)`.  Once functions are ordinary values, three things follow immediately: you can pass one to a function, you can build one on the spot without naming it, and a function you return can remember where it came from.  The next four models are those three ideas plus the one Scheme idiom that makes list traversal feel natural.

## Model 3: The Linear Equation, Projectile Motion, and `czr`

```scheme
(define y
  (lambda (m x b)
    (+ (* x m) b)))

(y 5 6 7)                    ; 37
```

```scheme
(define v0 3)
(define t 5)
(define a 9.80665)

(define square
  (lambda (n)
    (* n n)))

(+ (* v0 t) (* 0.5 (* a (* t t))))

(+ (* v0 t) (* 0.5 (* a (square t))))
```

```scheme
(define czr
  (lambda (l)
    (if (null? (cdr l))
        (car l)
        (czr (cdr l)))))

(czr '(1 2 3 4))             ; 4
```

### Reading the Code

- `y` is `y = mx + b` with the parentheses moved.  Read it aloud as "add, to the product of x and m, b" and prefix notation stops fighting you.
- The two projectile lines compute the same number.  The second one substitutes `(square t)` for `(* t t)`, which is the whole idea of composition: a function call is an expression, so it goes anywhere an expression goes.
- `czr` walks to the end of the list and hands back the last element.  It is not a standard Scheme procedure; it is ours.  Notice it has the same skeleton as `sumlist`, minus the work on the way back up: nothing happens after the recursive call returns.

### Critical Thinking Questions

10.  What does `czr` do in your own words?
11.  Write a function to count the number of items in a list using a recursive call and a base case, using `czr` as a guide to traversing a list.
12.  `czr` as written breaks on the empty list.  Bill's own version guards it with `(if (not (pair? l)) l ...)`.  Add that guard, decide what the empty list *should* return, and defend your choice.
13.  Which of `sumlist`, `largest`, and `czr` are tail-recursive as written, and which are not?  Use your answer to question 8.

---

## Model 4: `plusminus` and Anonymous Lambdas

```scheme
(define plusminus
  (lambda (a b)
    ((lambda (x y) (list (+ x y) (- x y)))
     a b)))

(plusminus 6 2)              ; (8 4)
```

### Reading the Code

There are two functions here.  The outer one is named `plusminus` and takes `a` and `b`.  The inner one has no name at all: it is created, applied to `a` and `b`, and thrown away.  Written out, the call is `((lambda (x y) ...) a b)`, which is the One Syntax Rule again, with a function *expression* in the operator position instead of a function *name*.

### Critical Thinking Questions

14.  Diagram the binding of the values in the call to `plusminus` to the anonymous lambda function.
15.  Rewrite `plusminus` without the inner lambda, so it just calls `list` directly.  What did the inner lambda buy, and what would it buy in a version where the inner function were returned instead of called?

---

## Model 5: `map`, `apply`, and Folding an Operator

```scheme
(define L1 '(1 2 3))
(define L2 '(4 5 6))
(define L3 (map - L1 L2))    ; (-3 -3 -3)
(apply + L3)                 ; -9

((lambda (x) (* x x)) 5)     ; 25
(map (lambda (x) (* x x)) '(1 2 3 4 5))   ; (1 4 9 16 25)
```

```scheme
(define oplist
  (lambda (op L)
    (if (null? (cdr L))
        (car L)
        (op (car L) (oplist op (cdr L))))))

(display (oplist * (list 2 4 6)))   ; 48
(newline)
(display (apply * (list 2 4 6)))    ; 48
```

### Reading the Code

- `map` takes a *function* as its first argument.  `(map - L1 L2)` subtracts the lists element by element, because `map` here is walking two lists at once.
- `apply` does the opposite of `map`: it takes one function and one list, and spreads the list out as the function's arguments.  `(apply + '(1 2 3))` is `(+ 1 2 3)`.
- `oplist` is `sumlist` with the `+` pulled out into a parameter.  That one change turns a function that sums into a function that does whatever you hand it.  Compare it against `(apply * ...)` on the last line: the built-in and your version agree.

### Critical Thinking Questions

16.  What is the result of the `map`/`apply` sequence?  What would happen if `map` were applied to only a single list?
17.  Write a function that accepts a list and an operator as parameters, such as addition.  Apply that operator to the whole list recursively; for example, if the operator is the addition operator, return the sum of the list.  If it is the multiplication operator, return the product of all items in the list.
18.  `oplist` and `apply` give the same answer here.  Name one case where they would not, and say which one you would rather have in your own language.

---

## Model 6: `make-counter` and Closures

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

### Reading the Code

`make-counter` returns a function.  That function still has access to `count`, even though `make-counter` has long since returned and `count` is not visible anywhere else in the program.  The returned function plus the environment it captured is a **closure**.

`counter1` and `counter2` each captured their *own* `count`, which is why they count independently.  Note also that this is the one place today where `set!` earns its keep: the whole point is state that persists between calls.

### Critical Thinking Questions

19.  Compare and contrast closures and objects.
20.  What shared variables exist in this program, and how does your answer differ from your answer to question 2?
21.  Add a `reset` capability to `make-counter`.  You will have to decide what the returned value even *is* once there is more than one operation, and that decision is exactly the one object-oriented languages made.

---

## Model 7: `make-account` and Message Passing

Question 21 asked what a closure's return value even *is* once there is more than one operation.  Here is one answer, and it is the answer Scheme programmers reached for long before anyone wrote the word `class` in a language specification.

```scheme
(define (make-account balance)
  (define (withdraw amount)
    (if (>= balance amount)
        (begin (set! balance (- balance amount)) balance)
        "insufficient funds"))
  (define (deposit amount)
    (set! balance (+ balance amount))
    balance)
  (lambda (message)
    (cond ((eq? message 'withdraw) withdraw)
          ((eq? message 'deposit) deposit)
          ((eq? message 'balance) balance)
          (else (error "unknown request" message)))))

(define acc (make-account 100))

((acc 'deposit) 50)          ; 150
((acc 'withdraw) 30)         ; 120
(acc 'balance)               ; 120
```

### Reading the Code

- `balance` is just the parameter of `make-account`, and `withdraw` and `deposit` were both created in the frame that holds it.  One variable, two procedures that can see it, and no way to reach it from outside.  That is the entire mechanism; there is nothing else in the box.
- The returned lambda is not an operation.  It is a *dispatcher*: hand it a symbol and it hands you back a procedure.  That is why the call reads `((acc 'deposit) 50)` with two sets of parentheses.  The inner call chooses the operation and the outer one runs it.
- `eq?` on symbols is a pointer comparison rather than a string comparison, because the reader interns every symbol it reads.  Dispatching on `'deposit` therefore costs about what a jump table costs, which is roughly what a method lookup costs in a language that has methods.
- `'balance` breaks the pattern: it hands back a *number* where the other two hand back *procedures*.  That is pleasant to type and unpleasant to use, and whether it is a convenience or a design error is question 23.

> **Watch out!**  The double parentheses are where everyone stubs a toe the first time.  `(acc 'deposit)` gives you a procedure and does nothing at all to the account.  `((acc 'deposit) 50)` calls that procedure.  Forget the outer pair and Scheme will cheerfully print the procedure itself, which MIT Scheme renders as `#[compound-procedure deposit]` and Guile as `#<procedure deposit (a)>`, while your balance sits exactly where it was.

### Critical Thinking Questions

22.  Draw the environment after `(define acc (make-account 100))`, and draw it again after `((acc 'deposit) 50)`.  How many frames are there, which one holds `balance`, and what changed between the two drawings?
23.  Make the interface uniform, so every message returns a procedure and reading the balance is `((acc 'balance))`.  Then argue the other side: what did the inconsistent version buy, and who paid for it?
24.  `(define acc2 (make-account 100))` gives you a second account.  What exactly is *not* shared between `acc` and `acc2`, and what *is*?  Compare your answer with your answer to question 20.
25.  This object has no inheritance, no `self`, and no type.  Pick one of the three and sketch how you would add it using nothing but closures.  Which of the three is hardest, and what does that tell you about why languages build them in?

---

## Model 8: `memoize`, When the Captured State Is Not a Number

`make-counter` captured an integer and `make-account` captured a number that two procedures share.  Nothing requires the captured state to be small.  A closure can capture a whole table, which is all that memoization is: a function wrapped in a cache that only it can see.

```scheme
(define (memoize f)
  (let ((cache '()))                 ; the captured state, an association list
    (lambda (x)
      (let ((hit (assoc x cache)))   ; look once, name the result
        (if hit
            (cdr hit)
            (let ((result (f x)))
              (set! cache (cons (cons x result) cache))
              result))))))

(define slow-square
  (lambda (n)
    (display "computing ") (display n) (newline)
    (* n n)))

(define fast-square (memoize slow-square))

(fast-square 4)              ; prints "computing 4", returns 16
(fast-square 4)              ; prints nothing at all, returns 16
```

### Reading the Code

- `assoc` walks the list looking for a pair whose `car` is `x`, and hands back that whole pair, or `#f` if there is no such pair.  `(cdr hit)` is therefore the cached answer.
- Naming the lookup with `let` means the cache is searched once instead of twice.  That is the same move `largest2` made in Model 2, and it is worth noticing that the fix looks identical in a completely different setting.
- The cache is captured, not global.  Two calls to `memoize` build two independent caches, exactly as two calls to `make-counter` built two independent counters, and nothing else in the program can reach either one.
- `set!` earns its keep here for the second time today.  A memo table you cannot update is an empty list forever.

> **Watch out!**  An association list searches in $O(n)$, so this is a teaching cache rather than a production one.  MIT Scheme spells the real thing `(make-equal-hash-table)`, `(hash-table/get cache x #f)`, and `(hash-table/put! cache x result)`; Racket spells it `make-hash`; R7RS does not standardize hash tables at all, which is why the portable version above uses `assoc`.  Write the association list when you want the code to run in any Scheme, and reach for your dialect's hash table when the cache gets big.  The hash-table version also acquires a bug that this one does not have, and that bug is question 27.

### Critical Thinking Questions

26.  `memoize` takes a one-argument function.  What breaks if you hand it a two-argument function, and what is the smallest change that fixes it?
27.  Suppose you rewrite the cache with a hash table and test for a hit using `(hash-table/get cache x #f)`.  Now memoize a predicate, a function that legitimately returns `#f` sometimes.  What goes wrong, how often does it go wrong, and how would you fix it without giving up the hash table?
28.  Memoizing `slow-square` saves nothing worth having.  Name a function you could write with what you know today whose running time memoization would drag from exponential down to linear, and say exactly which repeated work disappears.
29.  A memoized function mutates on every cache miss, so it is not referentially transparent on the inside.  Is it still referentially transparent on the *outside*?  Defend your answer, because your team's language will have to take a position on this in December.

---

## Model 9: Both Closures, Instrumented

Scheme fences in this deck are static, and the last two models both make claims about sharing and about cost.  Here are the same two closures in Python, counted, so the claims are numbers rather than assertions.

```python
# Model 7 and Model 8, transliterated so we can count.
# Scheme's inner (define ...) inside a closure is Python's def inside a def.

def make_account(balance):
    # 'balance' is the captured state.  'nonlocal' is Python's set! for a
    # captured binding: without it, the assignment would make a NEW local.
    def withdraw(amount):
        nonlocal balance
        if balance >= amount:
            balance = balance - amount
            return balance
        return "insufficient funds"

    def deposit(amount):
        nonlocal balance
        balance = balance + amount
        return balance

    def dispatch(message):
        if message == "withdraw":
            return withdraw
        if message == "deposit":
            return deposit
        if message == "balance":
            return balance
        raise ValueError("unknown request: " + str(message))

    return dispatch


acc = make_account(100)
acc2 = make_account(100)
print("deposit 50  :", acc("deposit")(50))
print("withdraw 30 :", acc("withdraw")(30))
print("acc balance :", acc("balance"))
print("acc2 balance:", acc2("balance"), "(untouched, its own frame)")

# ---- memoize, and the number that makes the point ----

calls = dict()

def counted(name, f):
    calls[name] = 0
    def wrapped(n):
        calls[name] = calls[name] + 1
        return f(n)
    return wrapped

def memoize(f):
    cache = dict()                  # the captured state: a table, not a number
    def wrapped(x):
        if x not in cache:
            cache[x] = f(x)
        return cache[x]
    return wrapped

def fib_slow(n):
    if n < 2:
        return n
    return slow(n - 1) + slow(n - 2)

slow = counted("slow", fib_slow)

def fib_fast(n):
    if n < 2:
        return n
    return fast(n - 1) + fast(n - 2)

fast = memoize(counted("fast", fib_fast))

print()
print("fib(25) naive    :", slow(25), "in", calls["slow"], "calls")
print("fib(25) memoized :", fast(25), "in", calls["fast"], "calls")

# Expected output:
# deposit 50  : 150
# withdraw 30 : 120
# acc balance : 120
# acc2 balance: 100 (untouched, its own frame)
#
# fib(25) naive    : 75025 in 242785 calls
# fib(25) memoized : 75025 in 26 calls
```
@LIA.eval(`["main.py"]`, `none`, `python3 main.py`)

### Reading the Code

- `acc2` is untouched by everything done to `acc`, and it is untouched for the same reason `counter2` was: each call to the constructor allocated a fresh frame, and the two closures captured different ones.
- `nonlocal` is the confession Python has to make out loud.  Scheme's `set!` already means "assign to the binding you can see," so Scheme needs no keyword; Python's plain `balance = ...` would create a new local instead, so it needs one.  Two languages, one mechanism, and only one of them makes you say it.
- `242785` against `26` is the whole argument for closure state in one line.  The memoized version is the same recursion with the same base case; the only difference is a table nobody else can reach.

### Try It Yourself

```python
# Start from the cell above and change three things.

# TODO 1: give make_account a 'history' message that returns the list of every
#         amount deposited or withdrawn.  Where does the list have to live for
#         acc and acc2 to keep separate histories?

# TODO 2: print len(cache) at the end by returning it from memoize somehow.
#         You will find you cannot reach it from outside without adding a
#         message, which is the point.  Add the message.

# TODO 3: predict the two call counts for fib(30) BEFORE you run it.  Write
#         your predictions down, then run it, then explain the naive one.
```
@LIA.eval(`["main.py"]`, `none`, `python3 main.py`)

---

# Part IV: Synthesis

# Check Your Understanding

Scheme's One Syntax Rule is that every compound form is `(operator operand ...)`.  The practical consequence is:

[(X)] The program is already a tree when you type it, so a parser has almost nothing to do
[( )] Scheme programs are shorter than the equivalent Python
[( )] Precedence is decided by a table at run time
[( )] Every Scheme program is a single expression

---

`(+ 1 2)` evaluates to 3.  `'(+ 1 2)` is a three-element list.  The quote:

[(X)] Suppresses evaluation, handing you the program itself as data
[( )] Converts the list to a string
[( )] Marks the expression as a comment
[( )] Makes evaluation lazy rather than eager

---

`(define add +)` works because:

[(X)] `+` is an ordinary value, and `define` binds a name to a value of any kind
[( )] Scheme special-cases the arithmetic operators
[( )] `add` becomes an alias resolved by the reader before evaluation
[( )] Scheme copies the definition of `+` into `add`

---

`largest2` beats `largest` because:

[( )] `let` is compiled more efficiently than `if`
[(X)] It computes the recursive result once and names it, instead of recomputing it in both branches
[( )] It is tail-recursive and `largest` is not
[( )] It avoids `car` on the empty list

---

A closure is:

[(X)] A function value together with the environment it was created in
[( )] Any function defined inside another function
[( )] A function that has been fully applied to all its arguments
[( )] A list whose first element is the symbol `lambda`

---

In `((acc 'deposit) 50)`, the inner call `(acc 'deposit)`:

[(X)] Returns the `deposit` procedure without touching the account
[( )] Deposits nothing and raises an error, since `'deposit` is not a number
[( )] Deposits the symbol `'deposit` into the account
[( )] Is the actual deposit, and the outer parentheses are redundant

---

`make-account` and `make-counter` both keep state that no other part of the program can reach.  What makes that state unreachable is:

[(X)] Lexical scope: `balance` and `count` are local to a frame that only the returned procedures captured
[( )] `set!`, which marks a variable as private
[( )] The `define` inside the procedure body, which acts as a visibility modifier
[( )] Scheme's garbage collector, which hides frames after their procedure returns

---

A cache that lives inside `memoize`'s `let` rather than at top level buys you:

[(X)] One independent cache per memoized function, with no chance of two functions colliding in a shared table
[( )] Faster lookups, because a captured variable is a register
[( )] Referential transparency, since the mutation is hidden
[( )] Thread safety, since each closure gets its own lock

---

**In-class work stops here.**  Everything below is the homework path.

## 5.  Exercises

Everything you read today is a worked example for the **Functional Programming with Scheme** assignment, handed out Thursday and due the Thursday after.  It asks you to write `czr` with its empty-list case, `reverse`, a recursive `count`, an improved `largest`, an operator-folding function like `oplist`, a `make-counter` closure, and one small program of your own.  Getting a REPL open today is the prerequisite for all of it, so do not leave here without one.

Before then, and independent of the assignment:

1.  Rewrite `sumlist` so that `(sumlist '())` returns 0 instead of erroring.  You will need `null?` rather than `(null? (cdr L))`.
2.  Write `reverse` using only `car`, `cdr`, and `cons`.  Then count how many `cons` calls it makes for a list of length `n`, and say whether you are happy with that.
3.  Take the projectile expression and factor it into a named function of `v0`, `t`, and `a`.  Then use `map` to compute the distance at `t` values `'(1 2 3 4 5)`.
4.  Give `make-account` a fourth message, `'history`, that returns every amount deposited or withdrawn so far, most recent first.  Then explain in one sentence why `acc` and `acc2` do not share a history, using the word *frame*.

## Reflection Prompt

Scheme paid for its uniformity.  Name one thing about today that was genuinely harder than the equivalent Python, and one thing that was genuinely easier.  Then say which of the two you would rather your team's language optimize for, and why.  Keep your answer; we will come back to it at the Language Design Workshop.

## 6.  Further Reading

- [The Scheme Programming Language](https://www.scheme.com/tspl3/) (Dybvig): the standard reference, and readable front to back
- [Closures in Scheme](https://www.artificialworlds.net/presentations/scheme-03-closures/scheme-03-closures.html) (Andy Balaam): where `make-counter` comes from
- [Structure and Interpretation of Computer Programs](https://mitp-content-server.mit.edu/books/content/sectbyfn/books_pres_0/6515/sicp.zip/full-text/book/book.html) (Abelson and Sussman), sections 3.1 and 3.2: where `make-account` comes from, and the source of the argument that a closure and an object are the same idea seen from two sides
- [QuickSort in Scheme](https://riptutorial.com/scheme/example/10903/quicksort): eight lines, and worth reading beside your own sorting code
- [Implementing Python as Syntax Rules for Racket](https://github.com/pedropramos/PyonR/): what "one syntax rule" buys you, taken to its logical end
- Runnable course archives: [SchemeSumList.zip](https://www.billmongan.com/Ursinus-CS374-Fall2026/files/replit/SchemeSumList.zip), [SchemeLargestElement.zip](https://www.billmongan.com/Ursinus-CS374-Fall2026/files/replit/SchemeLargestElement.zip), [czrEmptyListScheme.zip](https://www.billmongan.com/Ursinus-CS374-Fall2026/files/replit/czrEmptyListScheme.zip), [ApplyScheme.zip](https://www.billmongan.com/Ursinus-CS374-Fall2026/files/replit/ApplyScheme.zip), [ClosureStateScheme.zip](https://www.billmongan.com/Ursinus-CS374-Fall2026/files/replit/ClosureStateScheme.zip), [QuickSortScheme.zip](https://www.billmongan.com/Ursinus-CS374-Fall2026/files/replit/QuickSortScheme.zip)

Up next: *Functional Programming and Higher-Order Functions*, where the ideas you just met in Scheme show up in Python, and where a program turns out to be a list you can take apart and rewrite.
