# Scheme: Code as Data
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
