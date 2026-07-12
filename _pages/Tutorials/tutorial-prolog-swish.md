---
layout: tutorial
permalink: /Tutorials/Prolog
title: "CS374: Prolog in the Browser with SWISH"

info:
  coursenum: CS374
  goals:
    - To write facts, rules, and queries in Prolog and run them with zero installation in SWISH
    - To explain unification and backtracking as the engine behind a Prolog query
    - To solve a curated set of the Ninety-Nine Prolog Problems spanning list recursion, arithmetic, logic, and search
    - To demonstrate a relation running in more than one mode (running it backwards)
    - To contrast unification-binding and backtracking with your interpreter's environment and forward evaluation

readings:
  - rtitle: "The Power of Prolog (Markus Triska)"
    rlink: "https://www.metalevel.at/prolog"
  - rtitle: "SWISH — SWI-Prolog in the Browser"
    rlink: "https://swish.swi-prolog.org/"
  - rtitle: "The Ninety-Nine Prolog Problems"
    rlink: "https://www.metalevel.at/prolog/99"

tags:
  - logic-programming
  - prolog
  - functional
  - paradigms
---

# Prolog in the Browser with SWISH

This tutorial is the companion to **Direction F (Declarative Logic Programming in Prolog)** of the Functional Programming assignment. Everything here runs in the browser at [SWISH](https://swish.swi-prolog.org/) — nothing to install. For depth beyond this tutorial, read the opening chapters of [The Power of Prolog](https://www.metalevel.at/prolog).

Logic programming is the widest paradigm contrast in the course. Every other assignment is about **evaluation** — you write an expression and a machine reduces it to a value. Prolog is about **relations** — you state what is true, pose a query, and a search engine finds every way to make it true.

---

## Section 1: Facts, rules, and queries

A Prolog program is a set of **facts** and **rules**. A query asks whether something can be proven.

Paste this into a SWISH program pane (left side):

```prolog
parent(tom, bob).
parent(bob, ann).
parent(bob, pat).

grandparent(X, Z) :- parent(X, Y), parent(Y, Z).
sibling(X, Y)     :- parent(P, X), parent(P, Y), X \= Y.
ancestor(X, Y)    :- parent(X, Y).
ancestor(X, Y)    :- parent(X, Z), ancestor(Z, Y).
```

Then, in the query pane (bottom right), ask:

```prolog
?- grandparent(tom, Who).
```

SWISH answers `Who = ann`. Press `;` (or "Next") and it backtracks to `Who = pat`. Press `;` again and it reports no more solutions.

Read `:-` as "if", the comma as "and". `grandparent(X, Z)` holds *if* there is some `Y` such that `X` is a parent of `Y` and `Y` is a parent of `Z`. You never told Prolog *how* to find `Y` — the engine searched.

> **The core idea:** a query is a request for a *proof*. The engine tries clauses top to bottom, **unifies** the query with each clause head (a two-way pattern match that binds variables), and **backtracks** — undoing bindings — whenever a branch fails. Contrast this with your interpreter, which computes a value in one forward pass and never un-binds.

---

## Section 2: Lists and recursion

Lists are written `[1,2,3]`, with head/tail pattern `[H|T]`. Recursion is the norm:

```prolog
my_last(X, [X]).
my_last(X, [_|T]) :- my_last(X, T).

rev(List, Rev) :- rev_acc(List, [], Rev).
rev_acc([], Acc, Acc).
rev_acc([H|T], Acc, Rev) :- rev_acc(T, [H|Acc], Rev).
```

Query `?- rev([1,2,3], R).` gives `R = [3,2,1]`. Note there is no "return" — `rev/2` *relates* a list to its reversal.

---

## Section 3: The curated Ninety-Nine problems

Direction F asks for a deliberately small, representative slice of the classic [Ninety-Nine Prolog Problems](https://www.metalevel.at/prolog/99), chosen to span the paradigm:

| Problem | Relation | What it exercises |
|---------|----------|-------------------|
| P01 | `my_last(X, List)` | basic list recursion |
| P05 | `rev(List, Rev)` | accumulator recursion |
| P07 | `my_flatten(List, Flat)` | recursion over nested term structure |
| P31 | `is_prime(N)` | arithmetic + negation-as-failure (`\+`) |
| P46 | `table(A, B, Expr)` | logic connectives as relations |
| P90 | `queens(Qs)` | backtracking search — eight non-attacking queens |

Work each in SWISH, and record the query and its answer(s) in your `logic_session.md`. For P90, press `;` repeatedly (or use `findall/3`) to enumerate and **count** the solutions — the declarative style shines when the same clauses that *describe* a valid board also *search* for one.

A note on P31 and negation: `\+ Goal` succeeds when `Goal` cannot be proven ("negation as failure"). Explain in your writeup why this is subtly different from logical "not".

---

## Section 4: Running a relation backwards

This is the single most important idea in the direction. `append/3` is built in, but consider what it *is*: a relation between two lists and their concatenation. That means it runs in every direction:

```prolog
?- append([1,2], [3], Xs).       % concatenate:  Xs = [1,2,3]
?- append(Xs, Ys, [1,2,3]).      % split every way:
                                 %   Xs = [],      Ys = [1,2,3] ;
                                 %   Xs = [1],     Ys = [2,3]   ;
                                 %   Xs = [1,2],   Ys = [3]     ;
                                 %   Xs = [1,2,3], Ys = []
```

A Python function `append(a, b)` can only run one way — you cannot ask it "what two lists concatenate to `[1,2,3]`?" Prolog can, because `append/3` binds **logic variables** by unification rather than evaluating expressions. Demonstrate one of your own relations used in at least two modes and explain this in your writeup.

---

## Section 5: Unification and backtracking vs. your interpreter (the required comparison)

Close Direction F by connecting it back to the pipeline:

- **Binding.** Your interpreter's `Environment` maps a name to a *value* by assignment, one direction, permanently (until reassigned). Prolog **unifies** a logic variable with a *term*, two-directionally, and **un-binds** it on backtracking.
- **Control.** Your evaluator makes a single forward pass. Prolog searches a proof tree, trying alternatives and backtracking on failure.

If you took the **type-checking direction** of the Interpreter assignment, make the link explicit: the unification in your Hindley-Milner inferencer is the *same algorithm* Prolog uses to match goals — it just serves type inference there and proof search here.

---

## Reference

- [The Power of Prolog](https://www.metalevel.at/prolog) — the modern, free, complete text (with videos).
- [SWISH](https://swish.swi-prolog.org/) — run and share Prolog in the browser.
- [The Ninety-Nine Prolog Problems](https://www.metalevel.at/prolog/99) — the full problem ladder if you want more than the curated six.
