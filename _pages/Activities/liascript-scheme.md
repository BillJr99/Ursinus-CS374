# Scheme: Code as Data
<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://github.com/BillJr99/Ursinus-CS374-Fall2026/blob/gh-pages/_pages/Activities/liascript-scheme.md or locally via https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374/gh-pages/_pages/Activities/liascript-scheme.md

import: https://raw.githubusercontent.com/liascript/CodeRunner/master/README.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

# Scheme: Code as Data

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

## Model 2: Run and Vary

### Critical Thinking Questions

5. Trace `(sum '(1 2 3))` by hand, writing every call and return. Where does the addition for `1` actually happen: on the way down or the way back up?
6. Write `(my-filter pred lst)` following the `my-map` template; predict its output on `(my-filter odd? '(1 2 3 4 5))` and verify. Which line differs structurally from `my-map`?
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
