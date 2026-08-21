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

---

## Advanced (optional): Build a Mini-Prolog Interpreter in Python

> **Where this came from:** this section is the advanced capstone moved here from the Language Evaluation activity. It assumes you have seen unification and backtracking conceptually (Sections 1-5 above). Here you assemble a complete, self-contained Prolog engine in ordinary Python — terms, a unifier, variable renaming, and a depth-first solver — behind a clean `query(db, goal, *vars)` API.

### Putting it all together

We now have all the pieces: terms, unification, clause representation, variable renaming, and the backtracking solver. A complete mini-Prolog interpreter adds:

1. A **database class** with methods to assert facts and rules
2. A **query interface** that returns human-readable results
3. A **reification** step that walks the answer substitution to produce ground terms

The `reify` function applies the final substitution to a query variable to get its answer. If a variable is still unbound, it prints as itself — meaning the query is satisfied for *any* value of that variable.

---

**Intuition.** You now have all the ingredients: a term language (Var/Atom/Compound), a unifier, variable renaming, and the solver loop. Assembling them into a `DB` class with `fact`/`rule` methods and a `query` helper gives you a complete, self-contained Prolog engine. As you read Model 5, focus on the *interface*, not the internals — the internals are exactly what you built piecemeal in Models 2 and 3. The new thing is the clean `query(db, goal, *vars)` API that hides the generator machinery.

### The full mini-Prolog interpreter

```python
# Model 5: Complete mini-Prolog interpreter
from dataclasses import dataclass
from typing import Iterator, Any

# ============================================================
# Term representation
# ============================================================
@dataclass(frozen=True)
class Var:
    name: str
    def __repr__(self): return self.name

@dataclass(frozen=True)
class Atom:
    name: str
    def __repr__(self): return str(self.name)

@dataclass(frozen=True)
class Compound:
    functor: str
    args: tuple
    def __repr__(self):
        if self.functor == "." and len(self.args) == 2:
            items, cur = [], self
            while isinstance(cur, Compound) and cur.functor == ".":
                items.append(repr(cur.args[0])); cur = cur.args[1]
            tail = "" if cur == Atom("[]") else f"|{repr(cur)}"
            return "[" + ", ".join(items) + tail + "]"
        return f"{self.functor}({', '.join(repr(a) for a in self.args)})"

Subst = dict

# ============================================================
# Core unification operations
# ============================================================
def walk(t, s):
    while isinstance(t, Var) and t in s: t = s[t]
    return t

def occurs(v, t, s):
    t = walk(t, s)
    if isinstance(t, Var): return t == v
    if isinstance(t, Atom): return False
    return any(occurs(v, a, s) for a in t.args)

def unify(t1, t2, s):
    t1, t2 = walk(t1, s), walk(t2, s)
    if t1 == t2: return s
    if isinstance(t1, Var):
        return None if occurs(t1, t2, s) else {**s, t1: t2}
    if isinstance(t2, Var):
        return None if occurs(t2, t1, s) else {**s, t2: t1}
    if (isinstance(t1, Compound) and isinstance(t2, Compound)
            and t1.functor == t2.functor and len(t1.args) == len(t2.args)):
        for a, b in zip(t1.args, t2.args):
            s = unify(a, b, s)
            if s is None: return None
        return s
    return None

def reify(t, s):
    t = walk(t, s)
    if isinstance(t, (Var, Atom)): return t
    return Compound(t.functor, tuple(reify(a, s) for a in t.args))

# ============================================================
# Clause and database
# ============================================================
@dataclass
class Clause:
    head: Any
    body: list

_ctr = [0]
def fresh(clause):
    _ctr[0] += 1; n = _ctr[0]; memo = {}
    def r(t):
        if isinstance(t, Var):
            if t not in memo: memo[t] = Var(f"{t.name}_{n}")
            return memo[t]
        if isinstance(t, Atom): return t
        return Compound(t.functor, tuple(r(a) for a in t.args))
    return Clause(r(clause.head), [r(g) for g in clause.body])

class DB:
    def __init__(self): self.clauses = []
    def fact(self, functor, *args):
        self.clauses.append(Clause(Compound(functor, tuple(args)), []))
    def rule(self, head_f, head_args, *body_goals):
        head = Compound(head_f, tuple(head_args))
        self.clauses.append(Clause(head, list(body_goals)))

NIL = Atom("[]")
def cons(h, t): return Compound(".", (h, t))
def lst(*items):
    r = NIL
    for item in reversed(items): r = cons(item, r)
    return r

def a(s): return Atom(s)
def v(s): return Var(s)

# ============================================================
# Solver with depth-first backtracking
# ============================================================
def solve(goals, subst, db, depth=0):
    if depth > 80: return
    if not goals: yield subst; return
    goal, *rest = goals
    goal = reify(goal, subst)
    for clause in db.clauses:
        f = fresh(clause)
        s = unify(goal, f.head, subst)
        if s is not None:
            yield from solve(f.body + rest, s, db, depth + 1)

def query(db, goal_compound, *query_vars, limit=10):
    """Run a query; return results for the named query variables."""
    results = []
    for s in solve([goal_compound], {}, db):
        binding = {vr.name: reify(vr, s) for vr in query_vars}
        results.append(binding)
        if len(results) >= limit: break
    return results

# ============================================================
# Demo knowledge base
# ============================================================
db = DB()

# Family tree
for parent, child in [("tom","bob"),("tom","liz"),("bob","ann"),
                       ("bob","pat"),("pat","jim")]:
    db.fact("parent", a(parent), a(child))

# Genders
for m in ["tom","bob","pat","jim"]: db.fact("male",   a(m))
for f in ["liz","ann"]:             db.fact("female", a(f))

# ancestor(X,Y) :- parent(X,Y).
X, Y, Z, H, T, R = v("X"), v("Y"), v("Z"), v("H"), v("T"), v("R")
db.rule("ancestor", (X, Y), Compound("parent", (X, Y)))
# ancestor(X,Y) :- parent(X,Z), ancestor(Z,Y).
db.rule("ancestor", (X, Y), Compound("parent",  (X, Z)),
                             Compound("ancestor", (Z, Y)))

# member(X, [X|_]).
db.rule("member", (X, cons(X, v("_m"))),)
# member(X, [_|T]) :- member(X, T).
db.rule("member", (X, cons(v("_n"), T)), Compound("member", (X, T)))

# append([], Y, Y).
db.fact("append", NIL, Y, Y)
# append([H|T], Y, [H|R]) :- append(T, Y, R).
db.rule("append", (cons(H, T), Y, cons(H, R)), Compound("append", (T, Y, R)))

# ============================================================
# Run queries
# ============================================================
W = v("W")
print("=== ancestors of jim ===")
for r in query(db, Compound("ancestor", (W, a("jim"))), W):
    print("  Who =", r["W"])

print()
print("=== descendants of tom ===")
for r in query(db, Compound("ancestor", (a("tom"), W)), W):
    print("  Who =", r["W"])

print()
print("=== append([a,b], [c,d], Z) ===")
Zv = v("Z2")
for r in query(db, Compound("append", (lst(a("a"),a("b")), lst(a("c"),a("d")), Zv)), Zv):
    print("  Z =", r["Z2"])

print()
print("=== splits of [1,2,3]: append(X, Y, [1,2,3]) ===")
Xa, Ya = v("Xa"), v("Ya")
for r in query(db, Compound("append", (Xa, Ya, lst(a("1"),a("2"),a("3")))), Xa, Ya):
    print("  X =", r["Xa"], " Y =", r["Ya"])

print()
print("=== member(X, [p,q,r]) ===")
Mx = v("Mx")
for r in query(db, Compound("member", (Mx, lst(a("p"),a("q"),a("r")))), Mx):
    print("  X =", r["Mx"])
```

**Critical Thinking Questions (CTQs)**

> **CTQ 5.1** The `DB` class stores all clauses in a single list. What is the consequence of this for predicate lookup — specifically, when the solver tries to match a goal `parent(tom, X)`, it must scan *all* clauses. How would a real Prolog implementation index the database to make this faster?

> **CTQ 5.2** The `query` function has a `limit=10` parameter to prevent infinite output. What class of queries would produce infinitely many results without this limit? Give an example using the family database.

> **CTQ 5.3** The `fresh` function renames variables by appending `_N` where N is a global counter. Why must this counter be global (or at least shared across all calls to `fresh`) rather than local to each call? What would go wrong if it reset to 0 for each query?

> **CTQ 5.4** Examine the `db.fact("append", NIL, Y, Y)` line. The variable `Y` is a Python variable referencing a `Var("Y")` object. Every call to `db.fact("append", ...)` with `Y` stores the *same* `Var("Y")` object in two argument positions. Why is this safe — what operation do we rely on to make it not interfere across queries?

> **CTQ 5.5** How would you add a `not_member(X, L)` predicate? What is the challenge of implementing "negation" in a pure SLD resolution engine?

### Reflection prompt (for the advanced section)

Take 5-10 minutes individually to respond to the following prompt in your notebook:

> Logic programming inverts the usual programming model: instead of describing *how* to compute, you describe *what is true* and let the engine search. Choose one concept from today — unification, backtracking, bidirectionality, or the connection to type inference — and explain in your own words: (1) what makes it surprising or powerful, (2) a situation in your prior programming experience where this concept would have simplified your code, and (3) a limitation of logic programming that makes it unsuitable as a *general-purpose* language.

---

---

### Further reading on logic programming

**Classic Texts**

- W.F. Clocksin and C.S. Mellish, *Programming in Prolog* (5th ed., Springer, 2003) — the definitive introductory text.
- Leon Sterling and Ehud Shapiro, *The Art of Prolog* (2nd ed., MIT Press, 1994) — advanced techniques and program transformation.
- J.A. Robinson, "A Machine-Oriented Logic Based on the Resolution Principle," *JACM* 12(1), 1965 — the original unification paper.

**miniKanren and Relational Programming**

- William Byrd, Eric Holk, and Daniel Friedman, "miniKanren, Live and Untagged," *Scheme Workshop 2012* — the original miniKanren paper.
- Daniel Friedman, William Byrd, Oleg Kiselyov, and Jason Hemann, *The Reasoned Schemer* (2nd ed., MIT Press, 2018) — logic programming embedded in Scheme.
- miniKanren home: http://minikanren.org/
- Python `kanren` library: https://github.com/pythological/kanren

**Type Inference Connection**

- Luis Damas and Robin Milner, "Principal type-schemes for functional programs," *POPL 1982* — Algorithm W.
- Benjamin Pierce, *Types and Programming Languages*, Chapter 22 (type reconstruction) — connects unification to type inference formally.
- Oleg Kiselyov, "How OCaml type checker works," https://okmij.org/ftp/ML/generalization.html

**Constraint Logic Programming**

- Jaffar and Lassez, "Constraint Logic Programming," *POPL 1987* — extends Prolog with general constraints (CLP(R), CLP(FD)).
- SWI-Prolog CLP(FD) library: https://www.swi-prolog.org/man/clpfd.html — finite domain constraints for puzzles, scheduling, etc.

**Implementations to Explore**

- SWI-Prolog (https://www.swi-prolog.org/) — the standard modern Prolog, with excellent documentation.
- Tau Prolog (https://tau-prolog.org/) — Prolog in the browser, good for experimentation.
- Python `pyswip` — calls SWI-Prolog from Python.

---

## Reference

- [The Power of Prolog](https://www.metalevel.at/prolog) — the modern, free, complete text (with videos).
- [SWISH](https://swish.swi-prolog.org/) — run and share Prolog in the browser.
- [The Ninety-Nine Prolog Problems](https://www.metalevel.at/prolog/99) — the full problem ladder if you want more than the curated six.
