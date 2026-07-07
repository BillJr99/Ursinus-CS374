<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://github.com/BillJr99/Ursinus-CS374-Fall2026/blob/gh-pages/_pages/Activities/liascript-scheme.md or locally via https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374-Fall2026/gh-pages/_pages/Activities/liascript-scheme.md

import: https://raw.githubusercontent.com/liascript/CodeRunner/master/README.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

# Scheme: Code as Data

Scheme is to programming languages what Latin is to the Romance languages — it exposes the pure, undiluted core that every other language is built from, stripped of the ornamental syntax that usually hides the machinery beneath. Studying Scheme in a PL course is not about learning yet another language; it is about seeing, perhaps for the first time, that a programming language can be so minimal that its programs and its data are literally the same thing. Once you have felt that, you will read every other language differently.

## Learning Goals

By the end of this activity, you will be able to:

- Explain the uniform s-expression syntax of Scheme and why programs and data share the same structure
- Trace the evaluation of recursive Scheme functions, including higher-order functions like `map` and `fold`
- Describe how Scheme's `quote` and `eval` mechanisms enable code to be treated as data and vice versa
- Contrast Scheme's functional style with imperative Python, identifying where recursion replaces loops and closures replace mutable state

> **Before You Begin:** This activity assumes you can:
> - Write and call Python functions, including functions that call themselves recursively (e.g., factorial, Fibonacci)
> - Explain what a call stack is and what happens to it during nested function calls
> - Describe what a higher-order function is (a function that takes or returns another function, like Python's `map` and `filter`)
>
> If any of these feel shaky, review them first.

| Python | Scheme | Notes |
|--------|--------|-------|
| `def f(x): return x + 1` | `(define (f x) (+ x 1))` | Parentheses wrap everything — operator comes first |
| `if x > 0: ...` | `(if (> x 0) ...)` | Condition is just another expression in parens |
| `[1, 2, 3]` | `'(1 2 3)` | The quote `'` tells Scheme: "data, do not evaluate" |
| `f(a, b)` | `(f a b)` | Every call looks the same; no special infix operators |
| `lambda x: x * 2` | `(lambda (x) (* x 2))` | Anonymous functions use the same `(operator operands)` shape |

Today we study a language as an *artifact*: **Scheme** (we use its Racket dialect), a tiny functional language whose syntax is so uniform that programs and data share one shape, the parenthesized list. Scheme matters to this course twice over: it is functional programming distilled to essentials, and its **s-expression** syntax makes the lexer-parser machinery you built almost disappear, a designed contrast your team should feel. The arc: **s-expressions $\rightarrow$ evaluation rules $\rightarrow$ recursion as the only loop $\rightarrow$ code as data**.

---

## Directions and Group Roles

Work in your POGIL team with rotated roles (**Manager**, **Recorder**, **Presenter**, **Reflector**). Today is hands-on: install Racket (racket-lang.org) or use an online evaluator; the Manager drives, all predict before running. The Recorder posts answers to the Class Activity Questions discussion board; the Presenter reports out areas of disagreement or alternative approaches. After class, respond to the reflective prompt individually in your notebook.

---

# Part I: One Syntax Rule

## 1. Everything Is (operator operands...)

**Scheme has essentially one syntactic form**: the parenthesized prefix application `(f a b c)`. Arithmetic is not special: `(+ 2 3)` is 5; `(* (+ 2 3) 4)` is 20. Definitions, conditionals, and functions are *special forms* wearing the same parentheses:

```scheme
(define pi 3.14159)
(define (square x) (* x x))
(if (> x 0) "positive" "not positive")
(lambda (x) (* x x))
```

**Notice what vanished.** No precedence (prefix notation needs none: the tree is explicit in the nesting), no associativity rules, no statement-versus-expression divide (everything is an expression with a value). Your ambiguity module's entire ladder grammar exists to recover, for infix notation, the tree that Scheme's syntax simply *is*. The parentheses are the AST, written by hand.

---

This model makes the connection between Scheme's syntax and the Abstract Syntax Trees you have been building in Python explicit. In Python, a parser works hard to transform the flat text `2 + 3 * 4` into a tree that captures precedence; in Scheme, the programmer simply *writes* the tree directly as nested parentheses. Model 1 asks you to feel the difference by doing the translation yourself.

## Model 1: Trees Without a Parser

### Critical Thinking Questions

1. Translate `2 + 3 * 4` and `(2 + 3) * 4` into Scheme. Which required parentheses beyond the operators' own, and why does the question almost not make sense?
2. Draw the AST your CS374 parser builds for `2 + 3 * 4`, then write the Scheme expression beside it. State the relationship in one sentence; it is the punchline of the day.
3. A Scheme "lexer" needs roughly four token types. Name them, and explain what a Scheme "parser" does that your recursive descent parser did not have to sweat (hint: almost nothing; nesting is explicit).
4. What did Scheme's designers *pay* for this uniformity, in the week 2 evaluation criteria? (Ask anyone who has counted parentheses.)

---

# Part II: The Functional Core

## 2. Recursion Is the Loop

Scheme has no `while`; iteration is recursion, usually on lists, which are built from `cons` cells and dissected with `car` (first element) and `cdr` (the rest):

> **Watch out!** `car` and `cdr` are Scheme's names for what most languages call `head` and `tail` (or `first` and `rest`). The names are historical accidents from 1950s IBM hardware register names. When you see `(car lst)` think "give me the first element"; when you see `(cdr lst)` think "give me everything except the first element." Calling `car` or `cdr` on an empty list `'()` is a runtime error — always check `(null? lst)` first in your base case.

```scheme
(define (sum lst)
  (if (null? lst)
      0
      (+ (car lst) (sum (cdr lst)))))

(sum '(1 2 3 4 5))    ; 15

(define (my-map f lst)
  (if (null? lst)
      '()
      (cons (f (car lst)) (my-map f (cdr lst)))))

(my-map (lambda (x) (* x x)) '(1 2 3))   ; (1 4 9)
```

The base-case-plus-recursive-case shape is the same one your `my_reduce` exercise used, and the same shape as `evaluate` walking an AST: *the* functional pattern.

---

Model 2 is where recursion becomes your only loop. Every pattern you know from Python `for`-loops — mapping a function over a list, filtering elements, accumulating a sum — can be expressed as a short recursive function that peels one element off the front of a list, does something with it, and recurs on the rest. Watch how `car` grabs the head and `cdr` returns the tail; those two operations are the entire engine.

## Model 2: Run and Vary

### Critical Thinking Questions

5. Trace `(sum '(1 2 3))` by hand, writing every call and return. Where does the addition for `1` actually happen: on the way down or the way back up?
6. Write `(my-filter pred lst)` following the `my-map` template; predict its output on `(my-filter odd? '(1 2 3 4 5))` and verify. Which line differs structurally from `my-map`?

> **Watch out!** Forgetting the quote `'` before a list literal is the single most common Scheme beginner error. Writing `(1 2 3)` tells Scheme: "call the function named `1` with arguments `2` and `3`." Since `1` is not a function, you get an error like `application: not a procedure`. Always write `'(1 2 3)` when you mean a list of data, not a function call.

7. The quote in `'(1 2 3)` says "data, do not evaluate." Predict the difference between `(1 2 3)` and `'(1 2 3)` at the prompt; verify; explain the error message in terms of the One Syntax Rule.

[[MC]]
In Scheme, the expression `(+ 1 2)` and the quoted form `'(+ 1 2)` differ in that:
- ( ) The first is a list and the second is a number
- (x) The first evaluates to 3, while the second is a three-element list (the unevaluated program itself, as data)
- ( ) The second contains a syntax error
- ( ) They are identical in every context

---

## 3. The Big Idea: Homoiconicity

`'(+ 1 2)` is a list whose first element is the symbol `+`: **the program is a data structure the language itself manipulates**, and `(eval '(+ 1 2))` runs it. This property, **homoiconicity**, is why Lisp dialects have **macros**: functions that receive *code as lists*, transform it, and hand the result back to the evaluator, which is your `for`-loop desugaring exercise, except performed by user programs rather than by the language implementer. The AST you carefully constructed in Python with classes is, in Scheme, just... the list you typed.

---

# Part III: Runnable Models

Model 3 explores one of the most practically important differences between Scheme and Python: what happens when recursion goes very deep. Scheme guarantees that a tail-recursive function uses no more stack space than a simple loop, so algorithms that are naturally recursive — like traversing a million-element list — are not just elegant but efficient. Python offers no such guarantee, which is why Python programmers reach for `for`-loops even when recursion would be cleaner.

> **Watch out!** `define` in Scheme is not assignment in the imperative sense. Writing `(define x 5)` does not create a mutable variable you update later — it introduces a name binding in the current environment. In functional Scheme style, you do not reassign `x`; instead, you pass updated values forward as function arguments (hence the accumulator pattern in tail recursion). If you find yourself wanting to write `(set! x (+ x 1))` inside a loop, stop and think about how to express the same idea with a recursive accumulator parameter.

## Model 3: Tail Recursion — Scheme vs Python

**Tail recursion** occurs when a recursive call is the *last* operation in a function — no pending work remains after the call returns. Scheme (and Racket) *guarantee* tail-call optimization (TCO): a tail-recursive function consumes O(1) stack space. Python does **not** perform TCO; deep tail calls still overflow the call stack.

The cell below demonstrates both a naive (non-tail) factorial and a tail-recursive accumulator version in Python, counting stack frames to make the difference concrete.

```python  liascript
import sys

def fact_naive(n):
    """Non-tail-recursive: the multiplication happens AFTER the recursive call returns."""
    if n == 0:
        return 1
    return n * fact_naive(n - 1)   # pending multiply on the stack

def fact_tail(n, acc=1):
    """Tail-recursive: accumulator carries the work; nothing left to do on return."""
    if n == 0:
        return acc
    return fact_tail(n - 1, acc * n)  # last action IS the call

# Show call-depth difference using a frame counter
def count_frames_naive(n, depth=0):
    if n == 0:
        return depth
    return count_frames_naive(n - 1, depth + 1)

def count_frames_tail(n, depth=0):
    if n == 0:
        return depth
    return count_frames_tail(n - 1, depth + 1)

print("fact_naive(10)  =", fact_naive(10))
print("fact_tail(10)   =", fact_tail(10))
print()
print("Python default recursion limit:", sys.getrecursionlimit())
print()

# Show that both reach the same depth — Python cannot collapse either
print("Frames used by naive  fact(20):", count_frames_naive(20))
print("Frames used by tail   fact(20):", count_frames_tail(20))
print()

# In Scheme, the tail version would keep a FIXED stack depth.
# In Python we can simulate TCO with a trampoline:
def trampoline(f, *args):
    """Run a 'thunk-returning' function without growing the stack."""
    result = f(*args)
    while callable(result):
        result = result()
    return result

def fact_trampoline(n, acc=1):
    if n == 0:
        return acc
    return lambda: fact_trampoline(n - 1, acc * n)

print("Trampoline fact(10):", trampoline(fact_trampoline, 10))
print("Trampoline fact(100):", trampoline(fact_trampoline, 100))
print()
print("Key insight: Scheme tail calls are as cheap as loops.")
print("Python tail calls still grow the stack unless you add a trampoline manually.")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

### Critical Thinking Questions

8. In `fact_naive`, where is the pending multiplication "stored" between the recursive call and its return? What data structure holds it, and what happens to that structure in a Scheme tail call?
9. The trampoline converts recursive calls into *returned values* (thunks). Explain in one sentence why that prevents stack growth, and identify the analogous mechanism Scheme's runtime uses.
10. If you rewrote `sum` from Part II as a tail-recursive `sum-tail` with an accumulator, in what order would the additions be performed compared with the naive version? Does the final answer change?
11. Python's recursion limit defaults to 1000. Name one algorithm from your CS coursework where hitting this limit would be a real practical concern, and describe how you would restructure it.

---

Model 4 zooms in on a subtle but important question: when you write several name bindings together, can each one see the others? The three forms `let`, `let*`, and `letrec` give three different answers to that question. Understanding the difference matters both for reading Scheme code correctly and for appreciating why Python's `def` and assignment behave the way they do.

## Model 4: let, let*, and letrec

Scheme's **local binding forms** give names to intermediate values. They differ in *when* bindings become visible:

- `let` — all right-hand sides are evaluated in the **outer** environment; bindings are parallel and independent.
- `let*` — bindings are sequential; each RHS sees **all previous** bindings in the same `let*`.
- `letrec` — all names are in scope for **all** right-hand sides (required for mutually recursive local functions).

The Python simulation below models each form's scoping rule explicitly so you can observe the difference.

```python  liascript
# Simulate Scheme's let / let* / letrec scoping rules in Python

def demo_let():
    """
    Scheme:
      (let ((x 1)
            (y 2))
        (+ x y))
    All bindings use the OUTER scope.  Neither x nor y sees the other.
    """
    outer_x = 10
    # In a real 'let', both RHS are evaluated with outer_x = 10
    x = outer_x + 1   # x = 11
    y = outer_x + 2   # y = 12  (not x + 2, because let is parallel)
    result = x + y
    print(f"let:   x={x}, y={y}, x+y={result}")
    print("       Note: y used outer_x (10), NOT the new x (11)")

def demo_let_star():
    """
    Scheme:
      (let* ((x 1)
             (y (+ x 1)))   ; y CAN see x
        (+ x y))
    Sequential: each binding sees the previous ones.
    """
    x = 1
    y = x + 1   # y = 2; uses the JUST-BOUND x
    result = x + y
    print(f"let*:  x={x}, y={y}, x+y={result}")
    print("       Note: y used the new x (1), giving y=2")

def demo_letrec():
    """
    Scheme:
      (letrec ((even? (lambda (n) (if (= n 0) #t (odd?  (- n 1)))))
               (odd?  (lambda (n) (if (= n 0) #f (even? (- n 1))))))
        (even? 4))
    Both names are in scope for BOTH RHS — needed for mutual recursion.
    """
    # Python nested functions already implement letrec-like mutual visibility
    def even_q(n):
        if n == 0:
            return True
        return odd_q(n - 1)

    def odd_q(n):
        if n == 0:
            return False
        return even_q(n - 1)

    print(f"letrec: even?(4) = {even_q(4)}")
    print(f"letrec: odd?(7)  = {odd_q(7)}")
    print("        Note: even? and odd? reference each other — impossible with let or let*")

demo_let()
print()
demo_let_star()
print()
demo_letrec()
print()

# Bonus: show that let's parallel evaluation matters
print("--- Parallel swap (let) vs sequential (let*) ---")
a, b = 3, 7
# let swap: new_a = old_b, new_b = old_a  (evaluated simultaneously from outer scope)
new_a_let = b    # uses original b
new_b_let = a    # uses original a
print(f"let  swap: a={new_a_let}, b={new_b_let}  (correct parallel swap)")

# let* swap: sequential, so new_a is visible when new_b is evaluated
new_a_star = b           # new_a = 7
new_b_star = new_a_star  # new_b sees new_a (7), not original a (3)
print(f"let* swap: a={new_a_star}, b={new_b_star}  (WRONG — new_a leaked into new_b)")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

### Critical Thinking Questions

12. In the "parallel swap" demonstration, `let` gives the correct result but `let*` does not. Explain this in terms of evaluation order and what each binding's right-hand side is permitted to see.
13. Why does `letrec` require all names to be in scope *before* any right-hand side is evaluated? Construct a two-function mutual-recursion example where omitting `letrec` (using `let*` instead) would fail.
14. Python's `def` inside a function body corresponds most closely to which Scheme binding form? Justify your answer by pointing to the scoping rule each uses.
15. A Scheme `let` can always be rewritten as a `lambda` application: `(let ((x 5)) body)` becomes `((lambda (x) body) 5)`. Write out this transformation for the parallel-swap example. What does this equivalence reveal about `let` as syntactic sugar?

---

Model 5 brings together everything: now that you know how Scheme evaluates expressions and how lists are constructed, you can use Scheme's quasiquoting mechanism to build lists that are *programs*, then hand them to `eval`. This is homoiconicity made concrete and operational. The Python simulation in the runnable cell re-implements the same ideas so you can experiment without a Racket installation.

## Model 5: Quasiquoting and List Operations

**Quasiquoting** (`\`` backtick) is a templating mechanism: the entire form is treated as data (like `'`), *except* that subexpressions preceded by `,` (unquote) or `,@` (unquote-splicing) are evaluated. This is the foundation of Scheme macros and a powerful list-construction tool.

```python  liascript
# We cannot run Racket here, so we simulate quasiquoting semantics in Python
# to make the evaluation rules concrete.

def quasiquote(template, env):
    """
    Recursively process a nested list 'template'.
    - Strings that start with ',' are unquoted: look up the rest in env.
    - Lists that start with ',@' are spliced in.
    - Everything else is kept as-is (quoted).
    """
    if isinstance(template, list):
        result = []
        for item in template:
            if isinstance(item, list) and len(item) == 2 and item[0] == ',@':
                # Unquote-splicing: evaluate and extend
                val = env.get(item[1], [])
                if isinstance(val, list):
                    result.extend(val)
                else:
                    result.append(val)
            elif isinstance(item, str) and item.startswith(','):
                # Unquote: evaluate the name
                name = item[1:]
                result.append(env.get(name, item))
            elif isinstance(item, list):
                result.append(quasiquote(item, env))
            else:
                result.append(item)
        return result
    elif isinstance(template, str) and template.startswith(','):
        return env.get(template[1:], template)
    else:
        return template

# Example 1: basic unquote
env1 = {'x': 42, 'name': 'Alice'}
tmpl1 = ['define', ',name', ',x']
print("Template:", tmpl1)
print("Result:  ", quasiquote(tmpl1, env1))
# Equivalent Scheme: `(define ,name ,x)  with name='Alice' x=42
# => (define Alice 42)
print()

# Example 2: unquote-splicing to build a function call
env2 = {'fname': 'my-func', 'args': [1, 2, 3]}
tmpl2 = [',fname', [',@', 'args']]
print("Template:", tmpl2)
print("Result:  ", quasiquote(tmpl2, env2))
# Equivalent Scheme: `(,fname ,@args)  => (my-func 1 2 3)
print()

# Example 3: building a list of squares using quasiquote + list operations
nums = [1, 2, 3, 4, 5]

# car / cdr / cons equivalents
def car(lst): return lst[0]
def cdr(lst): return lst[1:]
def cons(x, lst): return [x] + lst
def null_p(lst): return lst == []

def my_map(f, lst):
    if null_p(lst):
        return []
    return cons(f(car(lst)), my_map(f, cdr(lst)))

def my_filter(pred, lst):
    if null_p(lst):
        return []
    if pred(car(lst)):
        return cons(car(lst), my_filter(pred, cdr(lst)))
    return my_filter(pred, cdr(lst))

def my_reduce(f, init, lst):
    if null_p(lst):
        return init
    return my_reduce(f, f(init, car(lst)), cdr(lst))

squares = my_map(lambda x: x * x, nums)
evens   = my_filter(lambda x: x % 2 == 0, nums)
total   = my_reduce(lambda a, b: a + b, 0, nums)

print("Original list:", nums)
print("Squares      :", squares)
print("Evens        :", evens)
print("Sum          :", total)
print()

# Demonstrate that (map f (filter pred lst)) composes cleanly
sum_of_even_squares = my_reduce(
    lambda a, b: a + b, 0,
    my_map(lambda x: x * x, my_filter(lambda x: x % 2 == 0, nums))
)
print("Sum of squares of even numbers:", sum_of_even_squares)
print("Expected: 4 + 16 = 20")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

### Critical Thinking Questions

16. In Scheme, `` `(define ,name ,x) `` is syntactic sugar for a call to the `quasiquote` special form. Explain the difference between `,name` (unquote) and `,@name` (unquote-splicing) in terms of what the resulting list structure looks like.
17. Macros in Scheme use quasiquoting to construct code. If you wanted to write a `my-when` macro that desugars `(my-when test body)` into `(if test body (void))`, write out the quasiquoted template the macro body would return.
18. The `my_map / my_filter / my_reduce` pipeline in the cell composes without intermediate variable names. Compare this style with a Python `for`-loop equivalent and describe one advantage and one disadvantage of each.
19. Unquote-splicing (`,@`) inserts a list's *elements* rather than the list itself. Write a Scheme expression (or Python simulation) that uses `,@` to combine two argument lists into a single function call, and explain what would go wrong if you used `,` (plain unquote) instead.

---

## 4. Exercises

1. *Warmups.* Define and test: `(double x)`, `(average a b)`, `(my-length lst)` recursively, and `(count-if pred lst)`.
2. *The translation suite.* Port your Day 1 functional exercises to Scheme: the product of odds (use your `my-filter` plus a recursive `product`), and word-count's shape `(my-reduce + 0 (my-map (lambda (w) 1) ws))`. Note which felt more natural in which language, honestly.
3. *Trees, of course.* Represent your CS374 AST in Scheme as nested lists, like `'(* (+ 2 3) 4)`, and write `(evaluate tree)` for `+ - * /` in fifteen lines. You have now written your interpreter twice; compare line counts and explain the difference in one sentence.
4. *Quote experiments.* Using `car`, `cdr`, and `cons` on `'(define (square x) (* x x))`, extract the function name, the parameter list, and the body. You are manipulating a program with a program; say so out loud.

---

## Reflection Prompt

In your notebook: Scheme deletes nearly all syntax and gains the ability to treat code as data; your language adds syntax and gains familiarity. After today, has your team's appetite for syntactic richness in your December language changed? What is one construct you now might simplify?

---

## 5. Further Reading

- Abelson and Sussman. *Structure and Interpretation of Computer Programs*, Chapter 1 (free online).
- The Racket Guide, chapters 1 through 4: https://docs.racket-lang.org/guide/
- Paul Graham. "The Roots of Lisp" (online essay): eval in a page.

## Going Deeper: The Metacircular Evaluator: Scheme in Python

An interpreter written in the very language it interprets sounds like a paradox, but it is actually one of the most clarifying ideas in computer science — it proves that the language's evaluation rules are self-consistent and complete. Think of it like a dictionary that defines every word using other words in the same dictionary: the circularity is a feature, not a bug, because it shows the system is closed. Building this evaluator in Python forces every semantic choice to become explicit code, revealing the machinery that your own course interpreter already contains.

#### Learning Goals

By the end of this activity, you will be able to:

- Parse Scheme s-expressions into Python data structures and traverse them to implement `eval` and `apply`
- Implement lexical scoping using a linked chain of environment frames that correctly handles closures
- Build a trampoline-based tail-call optimizer that runs deeply recursive Scheme programs without stack overflow
- Explain the relationship between the metacircular evaluator and the course's Mini-language interpreter, identifying where the two designs converge and diverge

> **Before You Begin:** This activity assumes you can:
> - Write and trace through a recursive Python function that processes nested lists
> - Explain what a Python dictionary is and how you would use one to map variable names to values
> - Describe what a closure is: a function paired with the environment in which it was created
>
> If any of these feel shaky, review them first.

> **"To understand the evaluator is to understand computation."** — SICP

A **metacircular evaluator** is an interpreter for a language written in (or very close to) that language itself. In SICP Chapter 4, Abelson and Sussman build a Scheme interpreter *in Scheme*, revealing that the evaluation rules almost write themselves — because the host language and the implemented language share the same underlying ideas. Here, we build a Scheme interpreter in Python. Python is close enough that the translation is direct; different enough that we must make every semantic choice explicit.

You have already built a Mini-language interpreter in this course. That experience carries over completely. The arc of this activity: **Scheme code as data (s-expressions)** → **the environment model** → **the evaluator dispatch loop** → **the global environment** → **tail-call optimization via trampoline**.

By the end you will have a working REPL that can evaluate recursive Scheme programs of arbitrary depth.

---

#### Directions and Group Roles

Work in your POGIL team of four with the following roles. Rotate roles each class meeting.

| Role | Responsibility |
|------|----------------|
| **Facilitator** | Keeps the group on track; ensures every member speaks before moving on |
| **Recorder** | Writes down agreed answers; posts Critical Thinking Question (CTQ) responses to the discussion board |
| **Reporter** | Presents the group's findings to the class; flags unresolved disagreements |
| **Reflector** | Monitors process; leads the end-of-activity reflection; notes what confused the group |

**Working norms:** Predict every code cell's output *before* running it. Write your prediction in the space above the cell. If the result surprises you, explain why *before* moving to the next question.

---

### Part I: S-Expressions — Code as Data

#### Model 1: S-Expressions

In most languages, source code is text and data is something else entirely. Scheme collapses this distinction: a program is a list, and lists are data. This means a Scheme program can construct and run another Scheme program using the same `car`, `cdr`, and `cons` operations it uses on ordinary lists. Before you can build the evaluator, you need to be comfortable reading nested Python lists as Scheme programs — the translation table in this model is your Rosetta Stone.

> **Watch out!** In our representation, Scheme symbols (like variable names `x`, `y`, operator names `+`) and Scheme strings (like `"hello"`) are both Python `str` values. The evaluator distinguishes them by context: a string that starts with `"` is a literal; anything else is a symbol to look up. This is a shortcut that would not work in a production system, but it simplifies the parser significantly.

Scheme's defining design choice: **program text and data share the same representation.** Every Scheme expression is an *s-expression* (symbolic expression): either an **atom** (number, boolean, string, or symbol) or a **pair** `(head . tail)`, where tail is usually another pair, recursively, giving a list. The surface syntax `(op arg1 arg2 ...)` is just a printed list.

This is not a curiosity — it is what makes Scheme's macros, `eval`, and `quote` work: a program can construct and execute another program using the same list operations it uses on ordinary data.

##### Mapping Scheme to Python

For our interpreter we represent s-expressions as nested Python lists of atoms. The correspondence:

| Scheme source | Python representation |
|---------------|-----------------------|
| `(+ 1 2)` | `['+', 1, 2]` |
| `(define x 42)` | `['define', 'x', 42]` |
| `(lambda (x) (* x x))` | `['lambda', ['x'], ['*', 'x', 'x']]` |
| `(if #t 1 0)` | `['if', True, 1, 0]` |
| `(let ((x 5)) (+ x 1))` | `['let', [['x', 5]], ['+', 'x', 1]]` |
| `'foo` | `['quote', 'foo']` |

Atoms map to: Python `int`/`float`, `bool`, `str` (for Scheme strings), or Python `str` (for Scheme symbols — we distinguish symbol from string by context).

##### The Parser

The parser has two stages: a **tokenizer** that splits the input string into a flat list of token strings, then a **recursive descent** step that folds those tokens into nested Python lists.

```python
import re

def tokenize(s):
    """
    Split a Scheme source string into a list of token strings.
    Handles: parentheses, strings, #t/#f, numbers, symbols.
    """
    # Insert spaces around parens, then split; handle quoted strings carefully
    token_pattern = r'\"[^\"]*\"|\(|\)|[^\s()\"]+' 
    return re.findall(token_pattern, s)

def parse_atom(token):
    """Convert a single token string to its Python atom value."""
    if token == '#t':
        return True
    if token == '#f':
        return False
    if token.startswith('"') and token.endswith('"'):
        return token[1:-1]            # strip quotes; store as Python str
    try:
        return int(token)
    except ValueError:
        pass
    try:
        return float(token)
    except ValueError:
        pass
    return token                      # symbol: just keep the string

def parse_tokens(tokens):
    """
    Consume tokens (a list used as a mutable queue via pop(0)) and return
    the next complete s-expression as a nested Python list/atom.
    """
    if not tokens:
        raise SyntaxError("Unexpected EOF")
    token = tokens.pop(0)
    if token == '(':
        result = []
        while tokens[0] != ')':
            result.append(parse_tokens(tokens))
        tokens.pop(0)                 # consume ')'
        return result
    elif token == ')':
        raise SyntaxError("Unexpected ')'")
    elif token == "'":                # shorthand quote
        return ['quote', parse_tokens(tokens)]
    else:
        return parse_atom(token)

def parse_sexp(s):
    """Parse a Scheme source string and return its Python representation."""
    tokens = tokenize(s)
    return parse_tokens(tokens)

# --- Demo ---
examples = [
    "(+ 1 2)",
    "(define x 42)",
    "(lambda (x) (* x x))",
    "(if #t 1 0)",
    "(let ((x 5)) (+ x 1))",
]
for src in examples:
    print(f"{src!s:40s} => {parse_sexp(src)}")
```
@LIA.eval(`["main.py"]`, `none`, `python3 main.py`)

---

##### Critical Thinking Questions — Model 1

**CTQ 1.** What Python type represents a Scheme pair/list in our encoding? What Python type represents a Scheme symbol? How does the evaluator distinguish a symbol `"x"` (which should be looked up) from a Scheme string `"hello"` (which is a literal value)?

> *Write your group's answer here.*

**CTQ 2.** What does `parse_sexp("(+ (* 2 3) 4)")` return? Trace through `parse_tokens` step by step, listing the state of `tokens` at each recursive call.

> *Write your group's answer here.*

**CTQ 3.** Numbers and booleans are stored as Python `int`, `float`, and `bool` rather than as strings. What advantage does this give the evaluator? What would break if `(+ 1 2)` were stored as `['+', '1', '2']`?

> *Write your group's answer here.*

---

### Part II: Environments

#### Model 2: The Environment as a Linked Chain of Frames

Scoping rules determine which variable binding wins when the same name exists in multiple contexts. Lexical scoping — the rule Scheme and Python both use — answers "which binding?" by looking at where the code was written, not where it was called. The linked chain of frames implements this: each frame holds the bindings introduced at one scope level, and the `outer` pointer to the enclosing scope forms the lookup chain. This structure is the heart of closures.

An **environment** in our interpreter is a dictionary that may have a pointer to an **outer** (enclosing) environment. Variable lookup walks the chain until the name is found or the outermost frame is exhausted.

```python
class SchemeError(Exception):
    pass

class Env(dict):
    """
    A single environment frame.
    Inherits from dict so frame[var] = val works directly.
    outer: the enclosing environment, or None for the global frame.
    """
    def __init__(self, params=(), args=(), outer=None):
        super().__init__()
        self.outer = outer
        if len(params) != len(args):
            raise SchemeError(
                f"Arity mismatch: expected {len(params)} args, got {len(args)}"
            )
        self.update(zip(params, args))   # bind each param to its arg

    def find(self, var):
        """
        Return the innermost frame that contains var.
        Raises SchemeError if var is unbound anywhere in the chain.
        """
        if var in self:
            return self
        if self.outer is None:
            raise SchemeError(f"Unbound variable: {var!r}")
        return self.outer.find(var)

# --- Demo: manual environment construction ---
global_env = Env()
global_env['y'] = 10

# Simulate (lambda (x) (+ x y)) called with x=3
call_env = Env(params=['x'], args=[3], outer=global_env)

print("x in call_env:", call_env.find('x')['x'])   # 3
print("y via outer:  ", call_env.find('y')['y'])   # 10
```
@LIA.eval(`["main.py"]`, `none`, `python3 main.py`)

The chain for `(define f (lambda (x) (+ x y)))` where `y = 10` in the global environment looks like this:

```
Global frame:  { y: 10, f: <Procedure> }
                        ^
                        | outer
Call frame:    { x: 3  }
```

When the body `(+ x y)` is evaluated in the call frame, `x` resolves immediately; `y` requires walking up one link to the global frame.

---

##### Critical Thinking Questions — Model 2

**CTQ 4.** What happens when `find` reaches the outermost environment (where `outer is None`) and the variable still has not been found? Write the exact exception that would be raised for `(+ x undefined-var)`.

> *Write your group's answer here.*

**CTQ 5.** Lexical (static) scope vs. dynamic scope differs entirely in *which frame becomes the `outer`* of a new call frame. In lexical scope, which environment is passed as `outer` when a closure is called? In dynamic scope, which environment would be passed instead?

> *Write your group's answer here.*

**CTQ 6.** Trace the full environment chain for the following interaction:

```scheme
(define y 10)
(define f (lambda (x) (+ x y)))
(f 5)
```

Draw the frames that exist when `(+ x y)` is being evaluated. Label every `outer` pointer. Then answer: if `y` were rebound to `20` *after* `f` was defined, would `(f 5)` return 15 or 25? Why?

> *Write your group's answer here.*

---

### Part III: The Evaluator Core

#### Model 3: `scheme_eval` — Dispatch on Form

The entire evaluator fits in one function because every Scheme expression falls into one of three categories: a self-evaluating atom (numbers, booleans), a symbol to look up, or a list. Lists are further divided into special forms (keywords like `if`, `define`, `lambda` that have their own evaluation rules) and procedure calls. This dispatch-on-shape pattern is the same pattern you used in your course interpreter — seeing it made explicit here should feel familiar.

> **Watch out!** In Scheme, only `#f` (the boolean false) is falsy. Everything else — including `0`, the empty list, and the empty string — is truthy. The line `branch = x[2] if test is not False else ...` implements this rule. Students frequently miss this and write `if not test`, which would treat `0` as false and produce wrong results for numeric conditions.

The evaluator is a single function that **dispatches** on the type and shape of the expression. Atoms evaluate to themselves or to their binding. Lists beginning with a keyword are **special forms** handled directly. Any other list is a **procedure call**.

```python
# We assume Env and SchemeError from Model 2 are already defined.

class Procedure:
    """
    A first-class Scheme procedure (closure).
    params: list of parameter name strings
    body:   s-expression (the body, a single expression or begin-list)
    env:    the defining environment (captured at lambda creation)
    """
    def __init__(self, params, body, env):
        self.params = params
        self.body   = body
        self.env    = env           # lexical environment — the closure

    def __call__(self, args):
        """Create a new frame on the *defining* environment, then evaluate body."""
        call_env = Env(self.params, args, self.env)
        return scheme_eval(self.body, call_env)

    def __repr__(self):
        return f"#<procedure ({' '.join(self.params)})>"


def scheme_eval(x, env):
    """
    Evaluate s-expression x in environment env.
    Returns a Python value representing the Scheme result.
    """

    # --- Self-evaluating atoms ---
    if isinstance(x, (int, float, bool)):
        return x
    if isinstance(x, str) and x.startswith('"'):
        return x                          # Scheme string literal

    # --- Symbol lookup ---
    if isinstance(x, str):
        return env.find(x)[x]

    # --- Special forms and procedure calls (x is a list) ---
    if not isinstance(x, list) or len(x) == 0:
        raise SchemeError(f"Cannot evaluate: {x!r}")

    head = x[0]

    # (quote datum)
    if head == 'quote':
        return x[1]

    # (if test consequent [alternate])
    if head == 'if':
        test = scheme_eval(x[1], env)
        # In Scheme only #f is false; everything else (including 0) is truthy
        branch = x[2] if test is not False else (x[3] if len(x) > 3 else False)
        return scheme_eval(branch, env)

    # (define symbol value)  or  (define (name params...) body)
    if head == 'define':
        if isinstance(x[1], list):
            # Syntactic sugar: (define (f x y) body) => (define f (lambda (x y) body))
            name   = x[1][0]
            params = x[1][1:]
            body   = x[2]
            env[name] = Procedure(params, body, env)
        else:
            env[x[1]] = scheme_eval(x[2], env)
        return None

    # (set! symbol value)
    if head == 'set!':
        env.find(x[1])[x[1]] = scheme_eval(x[2], env)
        return None

    # (lambda (params...) body)
    if head == 'lambda':
        params = x[1]
        body   = x[2] if len(x) == 3 else ['begin'] + x[2:]
        return Procedure(params, body, env)

    # (begin expr1 expr2 ...)
    if head == 'begin':
        result = None
        for expr in x[1:]:
            result = scheme_eval(expr, env)
        return result

    # (let ((var val) ...) body)
    if head == 'let':
        bindings = x[1]          # list of [var, val] pairs
        body     = x[2]
        params   = [b[0] for b in bindings]
        args     = [scheme_eval(b[1], env) for b in bindings]
        # Desugar: ((lambda (params...) body) args...)
        proc = Procedure(params, body, env)
        return proc(args)

    # (and expr ...)
    if head == 'and':
        result = True
        for expr in x[1:]:
            result = scheme_eval(expr, env)
            if result is False:
                return False
        return result

    # (or expr ...)
    if head == 'or':
        for expr in x[1:]:
            result = scheme_eval(expr, env)
            if result is not False:
                return result
        return False

    # --- Procedure call: (proc arg1 arg2 ...) ---
    proc = scheme_eval(head, env)
    args = [scheme_eval(a, env) for a in x[1:]]
    if callable(proc):
        return proc(args)
    raise SchemeError(f"Not a procedure: {proc!r}")


# --- Minimal global environment for the demo ---
import operator, math

def make_global_env():
    env = Env()
    env.update({
        '+':  lambda args: args[0] + args[1],
        '-':  lambda args: args[0] - args[1],
        '*':  lambda args: args[0] * args[1],
        '/':  lambda args: args[0] / args[1],
        '<':  lambda args: args[0] < args[1],
        '>':  lambda args: args[0] > args[1],
        '<=': lambda args: args[0] <= args[1],
        '>=': lambda args: args[0] >= args[1],
        '=':  lambda args: args[0] == args[1],
        'not':       lambda args: args[0] is False,
        'display':   lambda args: print(args[0], end=''),
        'newline':   lambda args: print(),
    })
    return env

# --- Tokenizer / parser (abbreviated; same as Model 1) ---
import re

def tokenize(s):
    return re.findall(r'\"[^\"]*\"|\(|\)|[^\s()\"]+', s)

def parse_atom(t):
    if t == '#t': return True
    if t == '#f': return False
    if t.startswith('"'): return t
    try: return int(t)
    except ValueError: pass
    try: return float(t)
    except ValueError: pass
    return t

def parse_tokens(tokens):
    if not tokens: raise SyntaxError("EOF")
    t = tokens.pop(0)
    if t == '(':
        lst = []
        while tokens[0] != ')':
            lst.append(parse_tokens(tokens))
        tokens.pop(0)
        return lst
    elif t == "'":
        return ['quote', parse_tokens(tokens)]
    else:
        return parse_atom(t)

def parse_sexp(s):
    return parse_tokens(tokenize(s))

# --- Run some expressions ---
genv = make_global_env()

tests = [
    "(+ 2 3)",
    "(if #t 42 0)",
    "(if #f 42 99)",
    "(define x 10)",
    "(+ x 5)",
    "(define square (lambda (n) (* n n)))",
    "(square 7)",
    "(let ((a 3) (b 4)) (+ (* a a) (* b b)))",
    "(and #t #t #f)",
    "(or  #f #f 7)",
    "(begin (define y 100) (+ y 1))",
]

for src in tests:
    ast    = parse_sexp(src)
    result = scheme_eval(ast, genv)
    if result is not None:
        print(f"{src!s:50s} => {result}")
```
@LIA.eval(`["main.py"]`, `none`, `python3 main.py`)

---

##### Critical Thinking Questions — Model 3

**CTQ 7.** Why does `define` store into `env` directly with `env[x[1]] = ...` while `set!` uses `env.find(x[1])[x[1]] = ...`? What would happen if `set!` used `env[x[1]] = ...` instead? Give a concrete example where the behavior would differ.

> *Write your group's answer here.*

**CTQ 8.** Show the complete desugaring of `(let ((x 5) (y 3)) (+ x y))` into a lambda application. Write out both the s-expression that `scheme_eval` actually evaluates and the equivalent Python call tree that results.

> *Write your group's answer here.*

**CTQ 9.** Consider:

```scheme
(define fact
  (lambda (n)
    (if (<= n 1)
        1
        (* n (fact (- n 1))))))
(fact 5)
```

Does this work in our evaluator? Trace through why `fact` is visible inside its own body even though it is being defined *right now*. (Hint: look at how `define` stores the procedure into `env` *before* the body is ever called.)

> *Write your group's answer here.*

---

### Part IV: The Global Environment

#### Model 4: `make_global_env` — The Built-In World

Every language has a layer of operations that the interpreter cannot define in terms of itself — the bedrock primitives. In Scheme these are things like `+`, `cons`, `car`, and `display`. In our interpreter they are Python lambdas sitting in the global environment frame. Everything else the user writes builds on top of this layer, which is why getting the primitive set right matters: it is the entire foundation.

The global environment pre-loads all the primitive operations. In real Scheme these are implemented in a low-level language for speed; in our interpreter they are just Python lambdas.

```python
import operator, math

# (Re-use Env, SchemeError, Procedure, scheme_eval from Models 2–3)

def make_global_env():
    """Return an Env pre-loaded with standard Scheme primitives."""
    env = Env()
    env.update({
        # --- Arithmetic ---
        '+':  lambda a: sum(a),
        '-':  lambda a: a[0] - a[1] if len(a) == 2 else -a[0],
        '*':  lambda a: a[0] * a[1],
        '/':  lambda a: a[0] / a[1],
        '%':  lambda a: a[0] % a[1],

        # --- Comparison ---
        '<':  lambda a: a[0] <  a[1],
        '>':  lambda a: a[0] >  a[1],
        '<=': lambda a: a[0] <= a[1],
        '>=': lambda a: a[0] >= a[1],
        '=':  lambda a: a[0] == a[1],

        # --- List operations ---
        # We represent Scheme pairs as Python 2-tuples (head, tail).
        # The empty list is None (representing Scheme's '()).
        'cons':   lambda a: (a[0], a[1]),
        'car':    lambda a: a[0][0],
        'cdr':    lambda a: a[0][1],
        'list':   lambda a: _make_list(a),
        'null?':  lambda a: a[0] is None,
        'pair?':  lambda a: isinstance(a[0], tuple),
        'length': lambda a: _length(a[0]),
        'append': lambda a: _append(a[0], a[1]),
        'map':    lambda a: _map(a[0], a[1]),

        # --- Boolean ---
        'not':      lambda a: a[0] is False,
        'boolean?': lambda a: isinstance(a[0], bool),

        # --- Type predicates ---
        'number?':    lambda a: isinstance(a[0], (int, float)) and not isinstance(a[0], bool),
        'symbol?':    lambda a: isinstance(a[0], str) and not a[0].startswith('"'),
        'string?':    lambda a: isinstance(a[0], str) and a[0].startswith('"'),
        'procedure?': lambda a: callable(a[0]),

        # --- I/O ---
        'display':  lambda a: (print(a[0], end=''), None)[1],
        'newline':  lambda a: (print(), None)[1],
    })
    return env

# --- Helpers for list operations ---
def _make_list(items):
    result = None
    for item in reversed(items):
        result = (item, result)
    return result

def _length(pair):
    count = 0
    while pair is not None:
        count += 1
        pair = pair[1]
    return count

def _append(p1, p2):
    if p1 is None:
        return p2
    return (p1[0], _append(p1[1], p2))

def _map(proc, lst):
    if lst is None:
        return None
    return (proc([lst[0]]), _map(proc, lst[1]))

def scheme_list_to_python(pair):
    """Convert our pair-based list to a Python list for display."""
    result = []
    while pair is not None:
        result.append(pair[0])
        pair = pair[1]
    return result

# --- Test the global environment ---
# (Re-define tokenizer, parser, Env, Procedure, scheme_eval here — abbreviated)
import re

class SchemeError(Exception): pass

class Env(dict):
    def __init__(self, params=(), args=(), outer=None):
        super().__init__()
        self.outer = outer
        self.update(zip(params, args))
    def find(self, var):
        if var in self: return self
        if self.outer is None: raise SchemeError(f"Unbound: {var!r}")
        return self.outer.find(var)

class Procedure:
    def __init__(self, params, body, env):
        self.params, self.body, self.env = params, body, env
    def __call__(self, args):
        return scheme_eval(self.body, Env(self.params, args, self.env))
    def __repr__(self): return f"#<procedure>"

def scheme_eval(x, env):
    if isinstance(x, (int, float, bool)): return x
    if isinstance(x, str) and x.startswith('"'): return x
    if isinstance(x, str): return env.find(x)[x]
    if not isinstance(x, list) or not x: raise SchemeError(f"Bad expr: {x!r}")
    head = x[0]
    if head == 'quote': return x[1]
    if head == 'if':
        test = scheme_eval(x[1], env)
        branch = x[2] if test is not False else (x[3] if len(x) > 3 else False)
        return scheme_eval(branch, env)
    if head == 'define':
        if isinstance(x[1], list):
            env[x[1][0]] = Procedure(x[1][1:], x[2], env)
        else:
            env[x[1]] = scheme_eval(x[2], env)
        return None
    if head == 'set!':
        env.find(x[1])[x[1]] = scheme_eval(x[2], env); return None
    if head == 'lambda':
        body = x[2] if len(x)==3 else ['begin']+x[2:]
        return Procedure(x[1], body, env)
    if head == 'begin':
        result = None
        for e in x[1:]: result = scheme_eval(e, env)
        return result
    if head == 'let':
        params = [b[0] for b in x[1]]; args = [scheme_eval(b[1],env) for b in x[1]]
        return Procedure(params, x[2], env)(args)
    if head == 'and':
        r = True
        for e in x[1:]:
            r = scheme_eval(e, env)
            if r is False: return False
        return r
    if head == 'or':
        for e in x[1:]:
            r = scheme_eval(e, env)
            if r is not False: return r
        return False
    proc = scheme_eval(head, env); args = [scheme_eval(a,env) for a in x[1:]]
    if callable(proc): return proc(args)
    raise SchemeError(f"Not a procedure: {proc!r}")

def tokenize(s): return re.findall(r'\"[^\"]*\"|\(|\)|[^\s()\"]+', s)
def parse_atom(t):
    if t=='#t': return True
    if t=='#f': return False
    if t.startswith('"'): return t
    try: return int(t)
    except: pass
    try: return float(t)
    except: pass
    return t
def parse_tokens(tokens):
    if not tokens: raise SyntaxError("EOF")
    t = tokens.pop(0)
    if t=='(':
        lst=[]
        while tokens[0]!=')': lst.append(parse_tokens(tokens))
        tokens.pop(0); return lst
    elif t=="'": return ['quote',parse_tokens(tokens)]
    else: return parse_atom(t)
def parse_sexp(s): return parse_tokens(tokenize(s))

genv = make_global_env()

tests = [
    ("(cons 1 2)",           None),
    ("(car (cons 1 2))",     None),
    ("(cdr (cons 1 2))",     None),
    ("(null? (list))",       None),
    ("(pair? (cons 1 2))",   None),
    ("(number? 42)",         None),
    ("(boolean? #t)",        None),
    ("(procedure? car)",     None),
]

for src, _ in tests:
    result = scheme_eval(parse_sexp(src), genv)
    print(f"{src!s:40s} => {result}")

# List demo
lst = scheme_eval(parse_sexp("(list 1 2 3 4)"), genv)
print("(list 1 2 3 4) as Python:", scheme_list_to_python(lst))
```
@LIA.eval(`["main.py"]`, `none`, `python3 main.py`)

---

##### Critical Thinking Questions — Model 4

**CTQ 10.** Our `cons` returns a Python 2-tuple `(head, tail)`, not a Python list. This means `(list 1 2 3)` produces `(1, (2, (3, None)))`. Name two operations from Model 3 that would break if we used Python lists instead of tuples for pairs. Why would the `null?` check fail?

> *Write your group's answer here.*

---

### Part V: Tail Call Optimization

#### Model 5: The Stack Overflow Problem and the Trampoline

A properly tail-recursive Scheme program should run in constant stack space — that is the Scheme specification's guarantee. But our Python evaluator grows a Python stack frame for every recursive `scheme_eval` call, even when the Scheme call is in tail position. The trampoline fixes this without changing Python's runtime: instead of recursing, tail calls return a "do this next" object (a `Thunk`), and a top-level loop bounces on those thunks until a real value appears. It converts recursion into iteration by making "what to do next" explicit.

> **Watch out!** The TCO evaluator uses a `while True` loop with `continue` for self-tail-calls. This is only an optimization for calls where the current function calls itself. Calls to a *different* procedure still need to update `x` and `env` and `continue` the loop, which is what the `Procedure call` branch does. Missing the `continue` after updating `env` and `x` would send execution to the bottom of the loop body instead of restarting from the top.

Python has a default recursion limit of about 1000 frames. A naive Scheme-in-Python evaluator will hit this limit when evaluating deeply recursive Scheme programs — even if the Scheme program is *tail recursive* and should need no stack at all.

Consider:

```scheme
(define count-down
  (lambda (n)
    (if (= n 0)
        'done
        (count-down (- n 1)))))
(count-down 10000)   ; Should work in Scheme; crashes in naive Python evaluator
```

The fix is a **trampoline**: instead of calling the recursive eval directly, return a *thunk* (a zero-argument lambda that will do the work) from tail positions. The trampoline loop bounces on thunks until a real value emerges.

```python
# Trampoline-based TCO evaluator

class Thunk:
    """A deferred computation: a zero-argument callable."""
    def __init__(self, thunk_fn):
        self.thunk_fn = thunk_fn
    def __call__(self):
        return self.thunk_fn()

def trampoline(val):
    """Repeatedly call val() while val is a Thunk; return the final value."""
    while isinstance(val, Thunk):
        val = val()
    return val

# In scheme_eval_tco we return Thunk objects at tail positions.
# Here is the key part of the TCO evaluator — only the changed branches shown:

def scheme_eval_tco(x, env):
    """
    TCO variant: tail calls return Thunk instead of recursing.
    Call via trampoline(scheme_eval_tco(expr, env)).
    """
    while True:   # Use a loop for self-tail-calls to avoid Python stack growth
        if isinstance(x, (int, float, bool)):
            return x
        if isinstance(x, str) and x.startswith('"'):
            return x
        if isinstance(x, str):
            return env.find(x)[x]
        if not isinstance(x, list) or not x:
            raise SchemeError(f"Bad expr: {x!r}")

        head = x[0]

        if head == 'quote':
            return x[1]

        # (if ...) — only the taken branch is a tail position
        if head == 'if':
            test = trampoline(scheme_eval_tco(x[1], env))
            branch = x[2] if test is not False else (x[3] if len(x) > 3 else False)
            x = branch          # tail position: loop instead of recurse
            continue

        if head == 'define':
            if isinstance(x[1], list):
                env[x[1][0]] = ProcedureTCO(x[1][1:], x[2], env)
            else:
                env[x[1]] = trampoline(scheme_eval_tco(x[2], env))
            return None

        if head == 'set!':
            env.find(x[1])[x[1]] = trampoline(scheme_eval_tco(x[2], env))
            return None

        if head == 'lambda':
            body = x[2] if len(x)==3 else ['begin']+x[2:]
            return ProcedureTCO(x[1], body, env)

        # (begin ...) — last expression is in tail position
        if head == 'begin':
            for expr in x[1:-1]:
                trampoline(scheme_eval_tco(expr, env))
            x = x[-1]          # tail position: loop
            continue

        if head == 'let':
            params = [b[0] for b in x[1]]
            args   = [trampoline(scheme_eval_tco(b[1], env)) for b in x[1]]
            env = Env(params, args, env)
            x   = x[2]         # tail position: loop
            continue

        # Procedure call
        proc = trampoline(scheme_eval_tco(head, env))
        args = [trampoline(scheme_eval_tco(a, env)) for a in x[1:]]
        if isinstance(proc, ProcedureTCO):
            env = Env(proc.params, args, proc.env)
            x   = proc.body    # tail call: loop
            continue
        elif callable(proc):
            return proc(args)
        raise SchemeError(f"Not a procedure: {proc!r}")


class ProcedureTCO:
    def __init__(self, params, body, env):
        self.params, self.body, self.env = params, body, env
    def __repr__(self): return "#<procedure-tco>"


# --- We need supporting code from previous models here ---
import re

class SchemeError(Exception): pass

class Env(dict):
    def __init__(self, params=(), args=(), outer=None):
        super().__init__(); self.outer = outer; self.update(zip(params, args))
    def find(self, var):
        if var in self: return self
        if self.outer is None: raise SchemeError(f"Unbound: {var!r}")
        return self.outer.find(var)

def tokenize(s): return re.findall(r'\"[^\"]*\"|\(|\)|[^\s()\"]+', s)
def parse_atom(t):
    if t=='#t': return True
    if t=='#f': return False
    if t.startswith('"'): return t
    try: return int(t)
    except: pass
    try: return float(t)
    except: pass
    return t
def parse_tokens(tokens):
    if not tokens: raise SyntaxError("EOF")
    t = tokens.pop(0)
    if t=='(':
        lst=[]
        while tokens[0]!=')': lst.append(parse_tokens(tokens))
        tokens.pop(0); return lst
    elif t=="'": return ['quote', parse_tokens(tokens)]
    else: return parse_atom(t)
def parse_sexp(s): return parse_tokens(tokenize(s))

def make_global_env_tco():
    env = Env()
    env.update({
        '+':  lambda a: a[0]+a[1], '-': lambda a: a[0]-a[1],
        '*':  lambda a: a[0]*a[1], '/': lambda a: a[0]/a[1],
        '<=': lambda a: a[0]<=a[1], '>=': lambda a: a[0]>=a[1],
        '<':  lambda a: a[0]<a[1],  '>':  lambda a: a[0]>a[1],
        '=':  lambda a: a[0]==a[1],
        'display': lambda a: (print(a[0], end=''), None)[1],
        'newline': lambda a: (print(), None)[1],
    })
    return env

def run(src):
    genv = make_global_env_tco()
    exprs = []
    tokens = tokenize(src)
    while tokens:
        exprs.append(parse_tokens(tokens))
    result = None
    for expr in exprs:
        result = trampoline(scheme_eval_tco(expr, genv))
    return result

# --- Demo: deep recursion without stack overflow ---
prog = """
(define count-down
  (lambda (n)
    (if (= n 0)
        0
        (count-down (- n 1)))))
"""
print("count-down 100000 =>", run(prog + "(count-down 100000)"))

# Tail-recursive sum
prog2 = """
(define sum-iter
  (lambda (n acc)
    (if (= n 0)
        acc
        (sum-iter (- n 1) (+ acc n)))))
"""
print("sum 0..1000 =>", run(prog2 + "(sum-iter 1000 0)"))
```
@LIA.eval(`["main.py"]`, `none`, `python3 main.py`)

---

##### Critical Thinking Questions — Model 5

**CTQ 11.** In the expression `(if test then-branch else-branch)`, which sub-expressions are in **tail position** and which are not? Justify your answer by explaining what computation (if any) must happen *after* that sub-expression returns.

> *Write your group's answer here.*

**CTQ 12.** Python does not automatically optimize tail calls, even when the programmer writes a tail-recursive function. Name two language design decisions in Python that make automatic tail-call optimization difficult or undesirable (consider stack traces, debugging, and Python's object model).

> *Write your group's answer here.*

---

### Part VI: Multiple Choice Comprehension Check

Answer individually, then compare with your group.

**Question 1.** What does evaluating `(lambda (x) x)` return in our interpreter?

    [( )] The number `0`
    [(x)] A `Procedure` object (a closure)
    [( )] The symbol `x`
    [( )] A `SchemeError` because `x` is unbound

**Question 2.** The expression `(let ((x 5)) (+ x 1))` desugars to which of the following?

    [( )] `(define x 5) (+ x 1)`
    [(x)] `((lambda (x) (+ x 1)) 5)`
    [( )] `(set! x 5) (+ x 1)`
    [( )] `(begin (define x 5) (+ x 1))`

**Question 3.** In `(define (square n) (* n n))`, the list `(square n)` as the first argument to `define` is:

    [( )] A syntax error in standard Scheme
    [( )] A pair of a function name and its return type
    [(x)] Syntactic sugar that expands to `(define square (lambda (n) (* n n)))`
    [( )] A call to the `square` function before it is defined

**Question 4.** Which component of the evaluator is directly responsible for implementing **lexical scope**?

    [( )] The tokenizer, which preserves symbol names
    [( )] The `scheme_eval` dispatch loop
    [(x)] The `Env` chain: each `Procedure` captures and stores its *defining* environment, which becomes the `outer` of each call frame
    [( )] The `trampoline` function

---

### Part VII: Exercises

Work through these exercises in your group. Each builds directly on the evaluator code from Parts I–V.

---

#### Exercise 1: Add `cond`

Scheme's `cond` is a multi-way conditional:

```scheme
(cond
  ((< x 0) 'negative)
  ((= x 0) 'zero)
  (else    'positive))
```

It evaluates each test in order; the first truthy test causes its associated expression to be evaluated and returned. The `else` clause (if present) is always truthy.

**Task:** Add a `cond` branch to `scheme_eval` (or `scheme_eval_tco`). The clause list is `x[1:]`; each clause is a two-element list `[test, expr]`. The special symbol `'else'` should be treated as always true.

```python
# Starter: fill in the cond branch inside scheme_eval

# if head == 'cond':
#     for clause in x[1:]:
#         test_expr, result_expr = clause[0], clause[1]
#         if test_expr == 'else' or scheme_eval(test_expr, env) is not False:
#             return scheme_eval(result_expr, env)
#     return None   # no matching clause

# Test with:
# (cond ((< 3 0) 'neg) ((= 3 0) 'zero) (else 'pos))
# Expected: 'pos'
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

Write the complete working implementation and verify it handles the test case above, plus a case where the first clause matches and the others are never evaluated.

---

#### Exercise 2: Add Scheme `do` Loops

Scheme's `do` loop is a structured iteration form:

```scheme
(do ((i 0 (+ i 1))     ; var init step
     (sum 0 (+ sum i)))
    ((= i 5) sum)       ; termination test, result
  (display i))          ; body (side effect only; run each iteration)
```

Each binding is `(var init step)`. On each iteration: evaluate all `step` expressions (using the *current* bindings, not the updated ones), then rebind. When `test` is true, evaluate `result` and return it.

**Task:** Implement `do` as a special form in `scheme_eval`. You will need to:
1. Extract bindings, the termination clause, and the body.
2. Create an initial environment with `var = init` for each binding.
3. Loop: check the test; if true, evaluate and return the result expression. Otherwise evaluate the body, compute all new step values simultaneously, rebind, repeat.

---

#### Exercise 3: Tail-Recursive `map` in Pure Scheme

The built-in `map` uses Python recursion. Write a **pure Scheme** `map` that is tail-recursive using an accumulator, then reverses the result.

```scheme
(define my-reverse
  (lambda (lst acc)
    (if (null? lst)
        acc
        (my-reverse (cdr lst) (cons (car lst) acc)))))

(define my-map
  (lambda (f lst)
    ; YOUR CODE HERE
    ; Use my-reverse and an accumulator
    ))

(my-map (lambda (x) (* x x)) (list 1 2 3 4 5))
; Expected: (1 4 9 16 25) as a Scheme list
```

Verify that your implementation produces the correct result by running it in the TCO evaluator. Then explain: is your `my-map` call to `my-map` in the recursive case actually in tail position? Draw the call to convince yourself.

---

#### Exercise 4: The Y Combinator

Without `define`, a lambda cannot refer to itself by name. The **Y combinator** makes anonymous recursion possible. In our evaluator (which uses applicative-order evaluation), the Z combinator (the strict variant) works:

```scheme
(define Z
  (lambda (f)
    ((lambda (x) (f (lambda (v) ((x x) v))))
     (lambda (x) (f (lambda (v) ((x x) v)))))))

(define fact
  (Z (lambda (self)
       (lambda (n)
         (if (<= n 1)
             1
             (* n (self (- n 1))))))))

(fact 6)
; Expected: 720
```

**Task:**
1. Run the Z combinator in your evaluator. Verify `(fact 6) = 720`.
2. Explain in one paragraph why the *eager Y combinator* `(lambda (f) ((lambda (x) (f (x x))) (lambda (x) (f (x x)))))` diverges under applicative-order evaluation but the Z combinator above does not.
3. *Challenge:* Define `fib` using `Z` without `define`. Test `(fib 10)`.

---

### Part VIII: Reflection

Answer these questions individually in your course notebook after completing the activity.

**Reflection 1.** The word "metacircular" implies the evaluator is defined in terms of itself. Our evaluator is written in Python, not Scheme — so in what sense is it still "metacircular"? What would it take to port our evaluator from Python into the Scheme subset our evaluator understands, and what would that accomplish?

**Reflection 2.** The course final project asks you to extend a language interpreter. Identify **three specific features** from this evaluator — the `Env` chain, `Procedure` as a closure, or TCO via trampoline — that map directly to something you will need in your final project. For each, write one sentence explaining the connection.

**Reflection 3.** Our evaluator has no type system: `(+ 1 "hello")` raises a Python `TypeError` that leaks through the abstraction boundary. Describe at minimum **two changes** you would make to add a static type system to this evaluator. Consider: where would type annotations appear in the s-expression representation? Where in `scheme_eval` would you insert a type-checking pass? What new data structure would represent a type error vs. a value?

---

### Further Reading

- **Runnable example archive** — [SchemeInterpreter.zip](/files/replit/SchemeInterpreter.zip): a complete reference implementation of this activity's evaluator, worth exploring after you have attempted the activity yourself.

- **SICP Chapter 4** — Abelson & Sussman, *Structure and Interpretation of Computer Programs*, 2nd ed. The original metacircular evaluator. MIT Press open access: [https://mitp-content-server.mit.edu/books/content/sectbyfn/books_pubs/6515/sicp.pdf](https://mitp-content-server.mit.edu/books/content/sectbyfn/books_pubs/6515/sicp.pdf)

- **"The Art of the Interpreter"** — Guy Steele & Gerald Sussman (1978). The foundational paper on meta-circular evaluation, environments, and the relationship between interpreters and compilers. [MIT AI Memo 452.](https://dspace.mit.edu/handle/1721.1/6094)

- **Norvig's `lis.py`** — Peter Norvig's "How to Write a (Lisp) Interpreter in Python." Norvig's version is compact and elegant; ours extends it with TCO and a fuller special-form set. Search for "Norvig lis.py" to find his blog post.

- **R7RS Scheme specification** — The current small Scheme standard. Section 4 (Expressions) maps directly to our `scheme_eval` dispatch table. Available at [https://small.r7rs.org/](https://small.r7rs.org/).

- **"Proper Tail Recursion and Space Efficiency"** — Will Clinger (PLDI 1998). A careful treatment of what tail-call optimization guarantees and how to implement it correctly.
