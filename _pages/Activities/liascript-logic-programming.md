<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://github.com/BillJr99/Ursinus-CS374-Fall2026/blob/gh-pages/_pages/Activities/liascript-logic-programming.md or locally via https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374-Fall2026/gh-pages/_pages/Activities/liascript-logic-programming.md

import: https://raw.githubusercontent.com/liascript/CodeRunner/master/README.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

# Logic Programming and Prolog

## Learning Goals

By the end of this activity, you will be able to:

- Explain the logic programming paradigm and contrast declarative knowledge bases with imperative and functional programs
- Construct Prolog-style facts, rules, and queries and trace how the resolution engine searches for proofs
- Implement unification over terms with variables and explain how it underpins both Prolog resolution and Hindley-Milner type inference
- Simulate backtracking search in Python, identifying choice points and the order in which solutions are generated
- Build a mini-Prolog interpreter that supports facts, rules, conjunctive goals, and variable bindings

The fourth paradigm from the paradigms module has a surprising claim: to compute, simply *declare what is true* and ask questions. The runtime searches for proofs. Prolog, the archetype of logic programming, powers natural language processing, constraint solving, and type inference engines — Hindley-Milner uses the same unification algorithm at its heart. Today we build that engine from scratch. The arc: **facts and queries → unification → resolution → backtracking → a complete mini-Prolog interpreter**.

---

## Directions and Group Roles

Work in your POGIL team with rotated roles (**Manager**, **Recorder**, **Presenter**, **Reflector**). Consider each model and question individually first, then discuss with your group. The Recorder posts answers to the Class Activity Questions discussion board; the Presenter reports out areas of disagreement or alternative approaches. After class, respond to the reflective prompt individually in your notebook.

---

# Part I: Facts, Rules, and Queries

## The Logic Programming Paradigm

In **imperative** programming you describe *how* to compute. In **functional** programming you describe *what* to compute using expressions. In **logic** programming you describe *what is true* using **facts** and **rules**, then ask the runtime to prove goals for you. The runtime is not a step-by-step executor — it is a **proof search engine**.

Prolog (Programming in Logic, 1972) is the canonical logic language. A Prolog program is a **knowledge base**:

- A **fact** asserts something unconditionally: `parent(tom, bob).` means "tom is a parent of bob."
- A **rule** asserts something conditionally: `grandparent(X, Z) :- parent(X, Y), parent(Y, Z).` means "X is a grandparent of Z *if* X is a parent of Y and Y is a parent of Z."
- A **query** asks the engine to find solutions: `?- grandparent(tom, Who).` asks "for what values of `Who` is tom a grandparent?"

The engine answers by **searching** for a sequence of rule applications (a **proof**) that derives the goal from the knowledge base. If it finds one, it reports the variable bindings; if not, it reports failure.

This paradigm has a striking dual use: the **same unification algorithm** that powers Prolog queries also powers **Hindley-Milner type inference** — the type system of Haskell, OCaml, and ML. By the end of this activity you will have built both.

---

## Model 1: Facts as a Database — Simulating Prolog Queries in Python

Prolog's knowledge base is like a relational database whose tables are predicates. We can simulate it in Python using lists of tuples and list comprehensions. The correspondences are:

| Prolog                        | Python                                                                   |
|-------------------------------|--------------------------------------------------------------------------|
| `parent(tom, bob).`           | `("parent", "tom", "bob")` in a facts list                              |
| `?- parent(tom, X).`          | `[y for (r,x,y) in facts if r=="parent" and x=="tom"]`                  |
| `,` (conjunction)             | nested comprehension or `and` in condition                               |
| `;` (disjunction)             | `|` of two sets                                                          |
| `\+` (negation-as-failure)    | `not any(...)`                                                           |

The Python simulation below encodes a family tree and shows how queries become set expressions. Notice that Prolog's uppercase variables (`X`, `Y`) become Python iteration variables. The key difference: Prolog searches *automatically* — we write the query as a logical sentence and the engine generates the iteration. In Python we must write the comprehension by hand.

```python  liascript
# Model 1: Family tree facts and queries
# Facts are stored as (predicate_name, arg1, arg2, ...) tuples

facts = [
    ("parent", "tom",   "bob"),
    ("parent", "tom",   "liz"),
    ("parent", "bob",   "ann"),
    ("parent", "bob",   "pat"),
    ("parent", "pat",   "jim"),
    ("male",   "tom",   ""),
    ("male",   "bob",   ""),
    ("male",   "pat",   ""),
    ("male",   "jim",   ""),
    ("female", "liz",   ""),
    ("female", "ann",   ""),
]

# Helper: collect all (arg1, arg2) pairs for a binary predicate
def rel(pred):
    return [(a, b) for (p, a, b) in facts if p == pred]

def unary(pred):
    return [a for (p, a, b) in facts if p == pred]

# ----- Direct fact queries -----
# Prolog: ?- parent(tom, X).
children_of_tom = [y for (x, y) in rel("parent") if x == "tom"]
print("Children of tom:", children_of_tom)

# Prolog: ?- parent(X, ann).
parents_of_ann = [x for (x, y) in rel("parent") if y == "ann"]
print("Parents of ann:", parents_of_ann)

# ----- Derived rule: grandparent(X, Z) :- parent(X, Y), parent(Y, Z). -----
grandparent_pairs = [
    (x, z)
    for (x, y1) in rel("parent")
    for (y2, z) in rel("parent")
    if y1 == y2
]
print("Grandparent pairs:", grandparent_pairs)

# Prolog: ?- grandparent(tom, X).
grandchildren_of_tom = [z for (x, z) in grandparent_pairs if x == "tom"]
print("Grandchildren of tom:", grandchildren_of_tom)

# ----- Derived rule: sibling(X, Y) :- parent(Z, X), parent(Z, Y), X \= Y. -----
sibling_pairs = [
    (x, y)
    for (z, x) in rel("parent")
    for (z2, y) in rel("parent")
    if z == z2 and x != y
]
print("Sibling pairs:", sibling_pairs)

# ----- Combining with unary predicates -----
# Prolog: ?- parent(X, Y), male(X), female(Y).
father_daughter = [
    (x, y)
    for (x, y) in rel("parent")
    if x in unary("male") and y in unary("female")
]
print("Father-daughter pairs:", father_daughter)

# ----- Recursive rule: ancestor(X, Y) -----
# ancestor(X, Y) :- parent(X, Y).
# ancestor(X, Y) :- parent(X, Z), ancestor(Z, Y).
def ancestor(x, y, depth=0):
    if depth > 10:
        return False   # guard against cycles
    for (px, py) in rel("parent"):
        if px == x and py == y:
            return True
        if px == x and ancestor(py, y, depth + 1):
            return True
    return False

def all_ancestors(y):
    people = {a for (p, a, b) in facts}
    return [x for x in people if ancestor(x, y)]

print("All ancestors of jim:", all_ancestors("jim"))
print("All ancestors of ann:", all_ancestors("ann"))
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

**Critical Thinking Questions (CTQs)**

> **CTQ 1.1** In Prolog, `parent(tom, X)` is a single declarative statement. In Python, we wrote a list comprehension. What information did *we* have to supply in Python that Prolog infers automatically?

> **CTQ 1.2** The `grandparent` rule uses two `parent` facts joined on a shared variable `Y`. In relational database terms, what operation does this correspond to?

> **CTQ 1.3** The `ancestor` relation is **recursive** — an ancestor is either a direct parent, or a parent of an ancestor. Why can't we compute all ancestor pairs with a single list comprehension in Python the way we computed grandparents? What would we need instead?

> **CTQ 1.4** In Prolog, `sibling(X, Y) :- parent(Z, X), parent(Z, Y), X \= Y.` The `\=` means "does not unify." Why is this constraint necessary? What happens if you remove it from the Python simulation?

---

# Part II: Terms and Unification

## The Algebra of Prolog Terms

Prolog's central operation is not function application — it is **unification**. Before we can understand how Prolog searches for proofs, we must understand how it computes.

Everything in Prolog is a **term**. Terms come in three flavors:

1. **Atoms** — lowercase names or quoted strings: `tom`, `bob`, `foo`, `'Hello World'`
2. **Variables** — uppercase names or starting with `_`: `X`, `Who`, `_Temp`
3. **Compound terms** — a functor applied to argument terms: `parent(tom, X)`, `f(g(a), b)`, `[1,2,3]` (which is `'.'(1,'.'(2,'.'(3,'[]')))`)

**Unification** is the operation $\text{unify}(t_1, t_2, \sigma)$: find a substitution $\sigma'$ extending $\sigma$ that makes $t_1$ and $t_2$ identical after applying $\sigma'$. In formal notation:

$$ \text{unify}(X, \text{tom}, \emptyset) = \{X \mapsto \text{tom}\} $$

$$ \text{unify}(f(X, b), f(a, Y), \emptyset) = \{X \mapsto a,\; Y \mapsto b\} $$

$$ \text{unify}(f(X, X), f(a, b), \emptyset) = \text{fail} \quad \text{(X can't be both a and b)} $$

The **occurs check** prevents circular substitutions. Naively, $\text{unify}(X, f(X))$ might produce $\{X \mapsto f(X)\}$, which is an infinite term. The occurs check says: before binding $X \mapsto t$, verify $X$ does not appear in $t$. Standard Prolog omits the occurs check for performance, but correct unification includes it.

The **Robinson unification algorithm** (1965) is the foundation:

1. **Walk** both terms: if either is a variable, follow its binding in the substitution.
2. If both are atoms: succeed iff they are equal.
3. If one is an unbound variable: bind it to the other (after occurs check).
4. If both are compounds: unify functor/arity, then unify arguments pairwise left-to-right.
5. Otherwise: fail.

---

## Model 2: Robinson Unification in Python

```python  liascript
# Model 2: Robinson Unification Algorithm with Occurs Check
from dataclasses import dataclass
from typing import Optional

# --- Term data types ---
@dataclass(frozen=True)
class Var:
    name: str
    def __repr__(self): return self.name

@dataclass(frozen=True)
class Atom:
    name: str
    def __repr__(self): return self.name

@dataclass(frozen=True)
class Compound:
    functor: str
    args: tuple
    def __repr__(self):
        return f"{self.functor}({', '.join(repr(a) for a in self.args)})"

# Substitution type: dict mapping Var -> term
Subst = dict

def walk(term, subst):
    """Follow variable bindings until we reach a non-variable or unbound var."""
    while isinstance(term, Var) and term in subst:
        term = subst[term]
    return term

def occurs(var, term, subst):
    """Return True if var occurs in term (after walking subst). Prevents infinite terms."""
    term = walk(term, subst)
    if isinstance(term, Var):
        return term == var
    elif isinstance(term, Atom):
        return False
    elif isinstance(term, Compound):
        return any(occurs(var, arg, subst) for arg in term.args)
    return False

def unify(t1, t2, subst):
    """
    Robinson unification with occurs check.
    Returns extended substitution on success, None on failure.
    """
    t1 = walk(t1, subst)
    t2 = walk(t2, subst)

    # Case 1: identical terms (atoms equal, same var, same compound)
    if t1 == t2:
        return subst

    # Case 2: t1 is an unbound variable -- bind it
    if isinstance(t1, Var):
        if occurs(t1, t2, subst):
            return None   # occurs check fails
        return {**subst, t1: t2}

    # Case 3: t2 is an unbound variable -- bind it
    if isinstance(t2, Var):
        if occurs(t2, t1, subst):
            return None   # occurs check fails
        return {**subst, t2: t1}

    # Case 4: both atoms -- must be equal (already handled in case 1)
    if isinstance(t1, Atom) and isinstance(t2, Atom):
        return None   # different atoms

    # Case 5: both compounds -- unify functor, arity, then args pairwise
    if (isinstance(t1, Compound) and isinstance(t2, Compound)
            and t1.functor == t2.functor and len(t1.args) == len(t2.args)):
        s = subst
        for a1, a2 in zip(t1.args, t2.args):
            s = unify(a1, a2, s)
            if s is None:
                return None
        return s

    return None   # incompatible structures

def reify(term, subst):
    """Fully substitute all variables in term."""
    term = walk(term, subst)
    if isinstance(term, Var):
        return term
    elif isinstance(term, Atom):
        return term
    elif isinstance(term, Compound):
        return Compound(term.functor, tuple(reify(a, subst) for a in term.args))
    return term

# --- Test cases ---
X = Var("X"); Y = Var("Y"); Z = Var("Z")
a = Atom("a"); b = Atom("b"); c = Atom("c")

def test(label, t1, t2, subst=None):
    if subst is None:
        subst = {}
    result = unify(t1, t2, subst)
    if result is None:
        print(f"{label}: FAIL")
    else:
        full = {k: reify(v, result) for k, v in result.items()}
        print(f"{label}: {full}")

# Basic atom unification
test("unify(a, a)", a, a)
test("unify(a, b)", a, b)

# Variable unification
test("unify(X, a)",   X, a)
test("unify(a, X)",   a, X)
test("unify(X, Y)",   X, Y)

# Compound unification
test("unify(f(X,Y), f(a,b))",
     Compound("f", (X, Y)),
     Compound("f", (a, b)))

test("unify(f(X,X), f(a,b))",
     Compound("f", (X, X)),
     Compound("f", (a, b)))

test("unify(f(g(X),Y), f(g(a),b))",
     Compound("f", (Compound("g", (X,)), Y)),
     Compound("f", (Compound("g", (a,)),  b)))

# Occurs check
test("unify(X, f(X))  [occurs check]",
     X, Compound("f", (X,)))

# Chained variable bindings
s = unify(X, Y, {})
s = unify(Y, a, s)
print(f"unify chain X=Y, Y=a -> X walks to: {reify(X, s)}, Y walks to: {reify(Y, s)}")

# Nested compound
test("unify(p(X,f(Y)), p(a,f(b)))",
     Compound("p", (X, Compound("f", (Y,)))),
     Compound("p", (a, Compound("f", (b,)))))
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

**Critical Thinking Questions (CTQs)**

> **CTQ 2.1** What substitution does `unify(f(X, Y), f(a, b), {})` produce? Show the bindings for `X` and `Y`.

> **CTQ 2.2** Why does `unify(X, f(X), {})` fail? What infinite term would result if we skipped the occurs check?

> **CTQ 2.3** When we unify `f(X, X)` with `f(a, b)`, we first bind `X → a`. Then we try to unify `X` with `b`. After walking `X` in the substitution, what term do we get, and why does unification then fail?

> **CTQ 2.4** The `walk` function follows a chain of variable bindings. Given the substitution `{X → Y, Y → a}`, show what `walk(X, subst)` returns step by step.

> **CTQ 2.5** Unification is at the core of **Hindley-Milner type inference**. In that system, type variables like `α` and `β` play the role of Prolog variables, and type constructors like `Int → Bool` play the role of compound terms. When the compiler infers the type of `f x = x + 1`, it generates a constraint `α = Int` and solves it by unification. Name one other place outside Prolog where unification is used.

---

$$ \text{unify}(f(X, g(Y)),\ f(a, g(b)),\ \emptyset) = \{X \mapsto a,\ Y \mapsto b\} $$

---

# Part III: Resolution and Backtracking

## SLD Resolution: How Prolog Proves Goals

Now that we have unification, we can describe Prolog's proof search. The core mechanism is **SLD resolution** (Selective Linear Definite clause resolution):

**To prove goal $G$:**

1. Find a clause $H \mathrel{:-} B_1, \ldots, B_n$ in the knowledge base such that $G$ unifies with $H$ via substitution $\sigma$.
2. Apply $\sigma$ to get the new goals $B_1\sigma, \ldots, B_n\sigma$.
3. Recursively prove each $B_i\sigma$ in left-to-right order.
4. If any step fails, **backtrack**: undo the choice and try the next matching clause.

For a fact $H \mathrel{:-}.$ (no body), proving $G$ succeeds immediately when $G$ unifies with $H$.

The search strategy is **depth-first, left-to-right**: Prolog tries clauses in the order they are written, and tries the leftmost subgoal first. This makes Prolog's behavior predictable but means the order of clauses and goals matters for termination.

**Variable renaming** is essential. Each time we *use* a clause, we rename its variables with fresh names so that earlier bindings do not interfere. This is called **standardizing apart**. Without it, `ancestor(X, Y)` could clash with `X` already bound in the caller.

$$ \text{To prove } \mathtt{ancestor(tom, Z)}: $$

$$ \text{Try clause 1: } \mathtt{ancestor(X', Y') :- parent(X', Y')} $$

$$ \text{Unify: } X' \mapsto \text{tom},\ Y' \mapsto Z $$

$$ \text{New goal: } \mathtt{parent(tom, Z)} $$

$$ \Rightarrow \text{succeeds with } Z \mapsto \text{bob},\ Z \mapsto \text{liz},\ \ldots $$

---

## Model 3: A Backtracking Proof Engine

```python  liascript
# Model 3: Backtracking proof engine with SLD resolution
from dataclasses import dataclass
from typing import Iterator

# --- Term types (self-contained) ---
@dataclass(frozen=True)
class Var:
    name: str
    def __repr__(self): return self.name

@dataclass(frozen=True)
class Atom:
    name: str
    def __repr__(self): return self.name

@dataclass(frozen=True)
class Compound:
    functor: str
    args: tuple
    def __repr__(self):
        return f"{self.functor}({', '.join(repr(a) for a in self.args)})"

Subst = dict

def walk(term, subst):
    while isinstance(term, Var) and term in subst:
        term = subst[term]
    return term

def occurs(var, term, subst):
    term = walk(term, subst)
    if isinstance(term, Var):   return term == var
    if isinstance(term, Atom):  return False
    if isinstance(term, Compound):
        return any(occurs(var, a, subst) for a in term.args)
    return False

def unify(t1, t2, subst):
    t1 = walk(t1, subst); t2 = walk(t2, subst)
    if t1 == t2: return subst
    if isinstance(t1, Var):
        if occurs(t1, t2, subst): return None
        return {**subst, t1: t2}
    if isinstance(t2, Var):
        if occurs(t2, t1, subst): return None
        return {**subst, t2: t1}
    if (isinstance(t1, Compound) and isinstance(t2, Compound)
            and t1.functor == t2.functor and len(t1.args) == len(t2.args)):
        s = subst
        for a1, a2 in zip(t1.args, t2.args):
            s = unify(a1, a2, s)
            if s is None: return None
        return s
    return None

def reify(term, subst):
    term = walk(term, subst)
    if isinstance(term, (Var, Atom)): return term
    if isinstance(term, Compound):
        return Compound(term.functor, tuple(reify(a, subst) for a in term.args))
    return term

# --- Clause: head :- body ---
@dataclass
class Clause:
    head: object
    body: list

# --- Variable renaming: standardize apart ---
_counter = [0]
def fresh_vars(clause):
    """Rename all variables in clause with a unique suffix."""
    _counter[0] += 1
    n = _counter[0]
    memo = {}
    def rename(term):
        if isinstance(term, Var):
            if term not in memo:
                memo[term] = Var(f"{term.name}_{n}")
            return memo[term]
        if isinstance(term, Atom): return term
        if isinstance(term, Compound):
            return Compound(term.functor, tuple(rename(a) for a in term.args))
        return term
    new_head = rename(clause.head)
    new_body = [rename(g) for g in clause.body]
    return Clause(new_head, new_body)

# --- Solver: generator yielding substitutions ---
def solve(goals, subst, db, depth=0):
    if depth > 50: return          # depth limit
    if not goals:
        yield subst                # all goals proved -- success!
        return
    goal, *rest = goals
    goal = reify(goal, subst)     # apply current subst before trying
    for clause in db:
        fresh = fresh_vars(clause)
        s = unify(goal, fresh.head, subst)
        if s is not None:
            new_goals = fresh.body + rest
            yield from solve(new_goals, s, db, depth + 1)

# --- Build family knowledge base ---
def atom(s): return Atom(s)
def compound(f, *args): return Compound(f, args)

# Variables
X = Var("X"); Y = Var("Y"); Z = Var("Z")

# Facts: parent(tom, bob). parent(tom, liz). etc.
db = [
    Clause(compound("parent", atom("tom"), atom("bob")), []),
    Clause(compound("parent", atom("tom"), atom("liz")), []),
    Clause(compound("parent", atom("bob"), atom("ann")), []),
    Clause(compound("parent", atom("bob"), atom("pat")), []),
    Clause(compound("parent", atom("pat"), atom("jim")), []),
    # ancestor(X, Y) :- parent(X, Y).
    Clause(compound("ancestor", X, Y),
           [compound("parent", X, Y)]),
    # ancestor(X, Y) :- parent(X, Z), ancestor(Z, Y).
    Clause(compound("ancestor", X, Y),
           [compound("parent", X, Z), compound("ancestor", Z, Y)]),
]

# --- Run queries ---
print("=== Query: ancestor(tom, Who)? ===")
Who = Var("Who")
query = [compound("ancestor", atom("tom"), Who)]
results = list(solve(query, {}, db))
for s in results:
    print("  Who =", reify(Who, s))

print()
print("=== Query: ancestor(Who, ann)? ===")
Who2 = Var("Who2")
query2 = [compound("ancestor", Who2, atom("ann"))]
results2 = list(solve(query2, {}, db))
for s in results2:
    print("  Who =", reify(Who2, s))

print()
print("=== Query: ancestor(tom, ann)? (yes/no) ===")
q3 = [compound("ancestor", atom("tom"), atom("ann"))]
print("  ", "yes" if list(solve(q3, {}, db)) else "no")

print()
print("=== Query: ancestor(ann, tom)? (yes/no) ===")
q4 = [compound("ancestor", atom("ann"), atom("tom"))]
print("  ", "yes" if list(solve(q4, {}, db)) else "no")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

**Critical Thinking Questions (CTQs)**

> **CTQ 3.1** The `fresh_vars` function renames variables before each clause is used. Trace through what would go wrong if we did *not* rename: suppose the query is `ancestor(tom, Who)` and the second ancestor clause is used twice (once for the outer call, once for the recursive call). What would happen to the variable `Z`?

> **CTQ 3.2** SLD resolution searches depth-first. Given the two ancestor clauses in the order shown, trace the first few steps when proving `ancestor(tom, jim)`. Which clause is tried first? What subgoal does it generate?

> **CTQ 3.3** What would happen if the recursive ancestor clause came *before* the base case? Would the query `ancestor(tom, X)` still terminate? Why or why not?

> **CTQ 3.4** The `solve` generator uses Python's `yield from` to propagate solutions through backtracking. What is the Python equivalent of Prolog's backtracking — i.e., when does the engine "try the next clause"?

> **CTQ 3.5** The depth limit `if depth > 50: return` prevents infinite loops. What class of Prolog programs causes infinite loops even when a solution exists? Give an example from the family database.

---

# Part IV: Lists in Prolog and the miniKanren Connection

## Lists as Recursive Data Structures

In Prolog, a list is a compound term built from the list constructor `'.'` (also written `[H|T]`):

- `[]` is the empty list (an atom)
- `[1,2,3]` is `'.'(1, '.'(2, '.'(3, '[]')))`

The power of logic programming with lists comes from **bidirectionality**: a predicate like `append(X, Y, Z)` can run in *any* mode:

- Given `X` and `Y`, find `Z` (append them)
- Given `Z`, find all `X` and `Y` pairs that split `Z` (reverse append)
- Given `X` and `Z`, find `Y` (difference list)

This works because append is defined by **logical equations**, not by a directional algorithm. The Prolog definition is:

```
append([], Y, Y).
append([H|T], Y, [H|R]) :- append(T, Y, R).
```

The first clause says: appending the empty list to Y gives Y. The second says: appending `[H|T]` to Y gives `[H|R]` where R is the result of appending T to Y.

When run backwards, the engine searches for unifications that satisfy these equations — and finds all valid splits.

The **miniKanren** library (Byrd et al.) embeds the same idea into Scheme (and its descendants into Python). Rather than a standalone interpreter, you get logic programming as a *library*: `run`, `fresh`, `==`, `conde` are functions. The core is the same: unification + search.

---

## Model 4: Bidirectional List Predicates

```python  liascript
# Model 4: Bidirectional list operations in logic style
from dataclasses import dataclass
from typing import Iterator

# --- Term types ---
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
            items = []
            cur = self
            while isinstance(cur, Compound) and cur.functor == ".":
                items.append(repr(cur.args[0]))
                cur = cur.args[1]
            if cur == Atom("[]"):
                return "[" + ", ".join(items) + "]"
            else:
                return "[" + ", ".join(items) + " | " + repr(cur) + "]"
        return f"{self.functor}({', '.join(repr(a) for a in self.args)})"

Subst = dict

def walk(term, subst):
    while isinstance(term, Var) and term in subst:
        term = subst[term]
    return term

def occurs(var, term, subst):
    term = walk(term, subst)
    if isinstance(term, Var):   return term == var
    if isinstance(term, Atom):  return False
    if isinstance(term, Compound):
        return any(occurs(var, a, subst) for a in term.args)
    return False

def unify(t1, t2, subst):
    t1 = walk(t1, subst); t2 = walk(t2, subst)
    if t1 == t2: return subst
    if isinstance(t1, Var):
        if occurs(t1, t2, subst): return None
        return {**subst, t1: t2}
    if isinstance(t2, Var):
        if occurs(t2, t1, subst): return None
        return {**subst, t2: t1}
    if (isinstance(t1, Compound) and isinstance(t2, Compound)
            and t1.functor == t2.functor and len(t1.args) == len(t2.args)):
        s = subst
        for a1, a2 in zip(t1.args, t2.args):
            s = unify(a1, a2, s)
            if s is None: return None
        return s
    return None

def reify(term, subst):
    term = walk(term, subst)
    if isinstance(term, (Var, Atom)): return term
    if isinstance(term, Compound):
        return Compound(term.functor, tuple(reify(a, subst) for a in term.args))
    return term

@dataclass
class Clause:
    head: object
    body: list

_counter = [0]
def fresh_vars(clause):
    _counter[0] += 1
    n = _counter[0]
    memo = {}
    def rename(term):
        if isinstance(term, Var):
            if term not in memo: memo[term] = Var(f"{term.name}_{n}")
            return memo[term]
        if isinstance(term, Atom): return term
        if isinstance(term, Compound):
            return Compound(term.functor, tuple(rename(a) for a in term.args))
        return term
    return Clause(rename(clause.head), [rename(g) for g in clause.body])

def solve(goals, subst, db, depth=0):
    if depth > 100: return
    if not goals:
        yield subst
        return
    goal, *rest = goals
    goal = reify(goal, subst)
    for clause in db:
        fresh = fresh_vars(clause)
        s = unify(goal, fresh.head, subst)
        if s is not None:
            yield from solve(fresh.body + rest, s, db, depth + 1)

# --- Helpers to build list terms ---
NIL = Atom("[]")
def cons(h, t): return Compound(".", (h, t))
def from_pylist(lst):
    result = NIL
    for item in reversed(lst):
        result = cons(Atom(str(item)), result)
    return result

# --- Variables ---
H = Var("H"); T = Var("T")
X = Var("X"); Y = Var("Y"); Z = Var("Z"); R = Var("R")

# --- Database with list predicates ---
# member(X, [X|_]).
# member(X, [_|T]) :- member(X, T).
# append([], Y, Y).
# append([H|T], Y, [H|R]) :- append(T, Y, R).

db = [
    # member/2
    Clause(Compound("member", (X, cons(X, Var("_1")))), []),
    Clause(Compound("member", (X, cons(Var("_2"), T))),
           [Compound("member", (X, T))]),
    # append/3
    Clause(Compound("append", (NIL, Y, Y)), []),
    Clause(Compound("append", (cons(H, T), Y, cons(H, R))),
           [Compound("append", (T, Y, R))]),
]

# --- Query 1: member(X, [1,2,3]) ---
print("=== member(X, [1,2,3]) ===")
lst123 = from_pylist([1, 2, 3])
Xq = Var("Xq")
for s in solve([Compound("member", (Xq, lst123))], {}, db):
    print("  X =", reify(Xq, s))

# --- Query 2: append([1,2], [3,4], Z) ---
print()
print("=== append([1,2], [3,4], Z) ===")
Zq = Var("Zq")
for s in solve([Compound("append", (from_pylist([1,2]), from_pylist([3,4]), Zq))], {}, db):
    print("  Z =", reify(Zq, s))

# --- Query 3 (BACKWARD): append(X, Y, [1,2,3]) -- find all splits ---
print()
print("=== append(X, Y, [1,2,3]) -- backward mode ===")
Xb = Var("Xb"); Yb = Var("Yb")
lst = from_pylist([1, 2, 3])
for s in solve([Compound("append", (Xb, Yb, lst))], {}, db):
    print("  X =", reify(Xb, s), " Y =", reify(Yb, s))

# --- Query 4: append([1,2], Y, [1,2,3,4]) -- find suffix ---
print()
print("=== append([1,2], Y, [1,2,3,4]) ===")
Ys = Var("Ys")
for s in solve([Compound("append", (from_pylist([1,2]), Ys, from_pylist([1,2,3,4])))], {}, db):
    print("  Y =", reify(Ys, s))
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

**Critical Thinking Questions (CTQs)**

[[MC]]
Which Prolog query finds all `X` such that `member(X, [1, 2, 3])` is true?
- ( ) `?- member([1,2,3], X).`
- (x) `?- member(X, [1,2,3]).`
- ( ) `?- X member [1,2,3].`
- ( ) `?- find(member, [1,2,3], X).`

[[MC]]
What makes `append/3` bidirectional in Prolog but not in a typical Python list concatenation function?
- ( ) Prolog uses a special list data structure unavailable in Python.
- ( ) Prolog evaluates arguments right-to-left, Python left-to-right.
- (x) Prolog's append is defined as logical equations over terms; unification can solve for any argument, while Python's `+` is a directed function that requires both operands to be known.
- ( ) Python lists are mutable, so concatenation cannot be reversed.

> **CTQ 4.1** The `append` predicate with query `append(X, Y, [1,2,3])` returns four solutions. List them. What does each solution represent geometrically (think about splitting the list)?

> **CTQ 4.2** miniKanren (and its Python port `kanren`) implements logic programming as a *library* rather than a standalone language. What are the practical tradeoffs of embedding logic programming in a host language versus using a standalone language like Prolog?

> **CTQ 4.3** Could you define `reverse/2` (reverses a list) using `append/3` in Prolog? Sketch the definition. (*Hint: what is the relationship between `reverse([H|T], R)` and `reverse(T, RT)` and `append(RT, [H], R)`?*)

---

# Part V: Complete Mini-Prolog Interpreter

## Putting It All Together

We now have all the pieces: terms, unification, clause representation, variable renaming, and the backtracking solver. A complete mini-Prolog interpreter adds:

1. A **database class** with methods to assert facts and rules
2. A **query interface** that returns human-readable results
3. A **reification** step that walks the answer substitution to produce ground terms

The `reify` function applies the final substitution to a query variable to get its answer. If a variable is still unbound, it prints as itself — meaning the query is satisfied for *any* value of that variable.

---

## Model 5: Full Mini-Prolog Interpreter

```python  liascript
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
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

**Critical Thinking Questions (CTQs)**

> **CTQ 5.1** The `DB` class stores all clauses in a single list. What is the consequence of this for predicate lookup — specifically, when the solver tries to match a goal `parent(tom, X)`, it must scan *all* clauses. How would a real Prolog implementation index the database to make this faster?

> **CTQ 5.2** The `query` function has a `limit=10` parameter to prevent infinite output. What class of queries would produce infinitely many results without this limit? Give an example using the family database.

> **CTQ 5.3** The `fresh` function renames variables by appending `_N` where N is a global counter. Why must this counter be global (or at least shared across all calls to `fresh`) rather than local to each call? What would go wrong if it reset to 0 for each query?

> **CTQ 5.4** Examine the `db.fact("append", NIL, Y, Y)` line. The variable `Y` is a Python variable referencing a `Var("Y")` object. Every call to `db.fact("append", ...)` with `Y` stores the *same* `Var("Y")` object in two argument positions. Why is this safe — what operation do we rely on to make it not interfere across queries?

> **CTQ 5.5** How would you add a `not_member(X, L)` predicate? What is the challenge of implementing "negation" in a pure SLD resolution engine?

---

# Part VI: Cut, Negation, and Arithmetic

## Arithmetic as a Built-in Predicate

Pure logic programming is Turing-complete but impractical without arithmetic. Prolog adds **built-in predicates** handled specially by the engine:

- `N is Expr` — evaluate `Expr` as an arithmetic expression, unify result with `N`
- `X > Y`, `X < Y`, `X =:= Y` — arithmetic comparison (both sides must be ground)
- `X =\= Y` — arithmetic inequality

The **cut** (`!`) is a control predicate that commits to the current choice: once `!` is reached, all choice points since the parent goal are discarded. It is used to implement if-then-else and negation-as-failure efficiently.

**Negation-as-failure** (`\+Goal`) succeeds iff `Goal` has no proof. This is *not* classical logical negation — it is a closed-world assumption: if we cannot prove P, we assume ¬P. This is powerful but non-monotonic (adding facts can make previously true goals fail).

A classic use of cut + arithmetic is Fibonacci:

```
fib(0, 0) :- !.
fib(1, 1) :- !.
fib(N, F) :- N > 1, N1 is N - 1, N2 is N - 2,
             fib(N1, F1), fib(N2, F2), F is F1 + F2.
```

The cuts ensure that once `fib(0,0)` matches, we do not try the third clause.

---

## Model 6: Arithmetic and Fibonacci in the Mini-Prolog Engine

```python  liascript
# Model 6: Arithmetic built-ins, cut, and Fibonacci
from dataclasses import dataclass
from typing import Iterator, Any

# --- Term types ---
@dataclass(frozen=True)
class Var:
    name: str
    def __repr__(self): return self.name

@dataclass(frozen=True)
class Atom:
    name: str
    def __repr__(self): return str(self.name)

@dataclass(frozen=True)
class Num:
    value: int
    def __repr__(self): return str(self.value)

@dataclass(frozen=True)
class Compound:
    functor: str
    args: tuple
    def __repr__(self):
        return f"{self.functor}({', '.join(repr(a) for a in self.args)})"

Subst = dict

def walk(t, s):
    while isinstance(t, Var) and t in s: t = s[t]
    return t

def occurs(v, t, s):
    t = walk(t, s)
    if isinstance(t, Var): return t == v
    if isinstance(t, (Atom, Num)): return False
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
    if isinstance(t, (Var, Atom, Num)): return t
    return Compound(t.functor, tuple(reify(a, s) for a in t.args))

def to_num(t, s):
    """Evaluate an arithmetic term to a Python int."""
    t = walk(t, s)
    if isinstance(t, Num): return t.value
    if isinstance(t, Atom):
        try: return int(t.name)
        except: raise ValueError(f"Not a number: {t}")
    if isinstance(t, Compound):
        if t.functor == "+" and len(t.args)==2: return to_num(t.args[0],s)+to_num(t.args[1],s)
        if t.functor == "-" and len(t.args)==2: return to_num(t.args[0],s)-to_num(t.args[1],s)
        if t.functor == "*" and len(t.args)==2: return to_num(t.args[0],s)*to_num(t.args[1],s)
        if t.functor == "/" and len(t.args)==2: return to_num(t.args[0],s)//to_num(t.args[1],s)
    raise ValueError(f"Cannot evaluate: {t}")

class CutException(Exception): pass

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
        if isinstance(t, (Atom, Num)): return t
        return Compound(t.functor, tuple(r(a) for a in t.args))
    return Clause(r(clause.head), [r(g) for g in clause.body])

class DB:
    def __init__(self): self.clauses = []
    def fact(self, f, *args):
        self.clauses.append(Clause(Compound(f, tuple(args)), []))
    def rule(self, hf, hargs, *body):
        self.clauses.append(Clause(Compound(hf, tuple(hargs)), list(body)))

def n(x): return Num(x)
def a(s): return Atom(s)
def v(s): return Var(s)
def arith(op, x, y): return Compound(op, (x, y))

def solve(goals, subst, db, depth=0):
    if depth > 200: return
    if not goals: yield subst; return
    goal, *rest = goals
    goal = reify(goal, subst)

    # Built-in: is/2  (N is Expr)
    if isinstance(goal, Compound) and goal.functor == "is" and len(goal.args) == 2:
        lhs, rhs = goal.args
        try:
            val = to_num(rhs, subst)
            s = unify(lhs, Num(val), subst)
            if s is not None: yield from solve(rest, s, db, depth+1)
        except: pass
        return

    # Built-in: comparison predicates
    if isinstance(goal, Compound) and goal.functor in (">","<",">=","=<","=:=","=\\=") and len(goal.args)==2:
        try:
            lv = to_num(goal.args[0], subst)
            rv = to_num(goal.args[1], subst)
            ops = {">": lv>rv, "<": lv<rv, ">=": lv>=rv,
                   "=<": lv<=rv, "=:=": lv==rv, "=\\=": lv!=rv}
            if ops.get(goal.functor, False):
                yield from solve(rest, subst, db, depth+1)
        except: pass
        return

    # Built-in: cut
    if isinstance(goal, Atom) and goal.name == "!":
        yield from solve(rest, subst, db, depth+1)
        raise CutException()

    # User-defined clauses
    for clause in db.clauses:
        f = fresh(clause)
        s = unify(goal, f.head, subst)
        if s is not None:
            try:
                yield from solve(f.body + rest, s, db, depth+1)
            except CutException:
                return  # cut: stop trying further clauses

def query(db, goal, *qvars, limit=15):
    results = []
    try:
        for s in solve([goal], {}, db):
            results.append({v.name: reify(v, s) for v in qvars})
            if len(results) >= limit: break
    except CutException:
        pass
    return results

# ============================================================
# Fibonacci knowledge base
# ============================================================
db = DB()
N  = v("N"); F  = v("F")
N1 = v("N1"); N2 = v("N2")
F1 = v("F1"); F2 = v("F2")

# fib(0, 0) :- !.
db.rule("fib", (n(0), n(0)), a("!"))
# fib(1, 1) :- !.
db.rule("fib", (n(1), n(1)), a("!"))
# fib(N, F) :- N > 1, N1 is N-1, N2 is N-2, fib(N1,F1), fib(N2,F2), F is F1+F2.
db.rule("fib", (N, F),
    Compound(">",   (N, n(1))),
    Compound("is",  (N1, arith("-", N, n(1)))),
    Compound("is",  (N2, arith("-", N, n(2)))),
    Compound("fib", (N1, F1)),
    Compound("fib", (N2, F2)),
    Compound("is",  (F, arith("+", F1, F2))))

print("Fibonacci sequence (fib/2):")
for i in range(10):
    res = query(db, Compound("fib", (n(i), v("Fq"))), v("Fq"), limit=1)
    fval = res[0]["Fq"] if res else "?"
    print(f"  fib({i}) = {fval}")

# Factorial knowledge base
db2 = DB()
Nf = v("N"); Ff = v("F"); N1f = v("N1"); F1f = v("F1")
# fact(0, 1) :- !.
db2.rule("fact", (n(0), n(1)), a("!"))
# fact(N, F) :- N > 0, N1 is N-1, fact(N1, F1), F is N * F1.
db2.rule("fact", (Nf, Ff),
    Compound(">",    (Nf, n(0))),
    Compound("is",   (N1f, arith("-", Nf, n(1)))),
    Compound("fact", (N1f, F1f)),
    Compound("is",   (Ff, arith("*", Nf, F1f))))

print()
print("Factorial sequence (fact/2):")
for i in range(8):
    res = query(db2, Compound("fact", (n(i), v("Fq2"))), v("Fq2"), limit=1)
    fval = res[0]["Fq2"] if res else "?"
    print(f"  {i}! = {fval}")

# Arithmetic built-ins demonstration
print()
print("Arithmetic built-ins:")
Xv = v("Xv")
for s in solve([Compound("is", (Xv, arith("+", arith("*", n(3), n(4)), n(5))))], {}, db):
    print("  X is 3*4+5 =>", reify(Xv, s))
for s in solve([Compound(">", (n(7), n(3)))], {}, db):
    print("  7 > 3: true")
for s in solve([Compound(">", (n(2), n(5)))], {}, db):
    print("  2 > 5: true")
print("  2 > 5:", "true" if list(solve([Compound(">", (n(2), n(5)))], {}, db)) else "false")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

**Critical Thinking Questions (CTQs)**

> **CTQ 6.1** The cut (`!`) in `fib(0, 0) :- !.` prevents backtracking into subsequent clauses once this one matches. What would happen without the cut — i.e., if we tried `fib(0, F)` and there was no cut? Which clauses would the engine also try?

> **CTQ 6.2** The `is/2` predicate requires the right-hand side to be fully **ground** (no variables). Why? What error would occur if you wrote `X is Y + 1` with `Y` unbound?

> **CTQ 6.3** Prolog's arithmetic is not "bidirectional" the way `append` is. You cannot write `3 is X + 1` and expect Prolog to infer `X = 2`. Why not? What alternative (constraint logic programming over reals, or CLP(R)) would support this?

> **CTQ 6.4** The Fibonacci implementation above has exponential time complexity. In standard Prolog, you can use **assert/retract** to memoize results dynamically. How would you add memoization to the Python solver? What data structure would you use?

---

# Part VII: Exercises

## Exercise 1 — Sibling and Extended Family Predicates

The mini-Prolog interpreter from Model 5 has `parent`, `ancestor`, and `member`. Extend it with:

- `sibling(X, Y)` — X and Y share a parent and are distinct
- `uncle(X, Y)` — X is a brother of one of Y's parents
- `cousin(X, Y)` — X's parent and Y's parent are siblings

Use the `DB.rule` API from Model 5. Test your predicates by querying the family database built there.

[[___]]
<script>true</script>

> Sketch answer: add after the existing DB setup in Model 5.
> ```python
> # sibling(X, Y) :- parent(Z, X), parent(Z, Y).
> # (Filter X != Y in post-processing or add a not_equal built-in)
> P = v("P"); P2 = v("P2")
> db.rule("sibling", (X, Y),
>     Compound("parent", (Z, X)),
>     Compound("parent", (Z, Y)))
>
> # uncle(X, Y) :- sibling(X, P), parent(P, Y), male(X).
> db.rule("uncle", (X, Y),
>     Compound("sibling", (X, P)),
>     Compound("parent",  (P, Y)),
>     Compound("male",    (X,)))
>
> # cousin(X, Y) :- parent(P, X), parent(P2, Y), sibling(P, P2).
> db.rule("cousin", (X, Y),
>     Compound("parent",  (P, X)),
>     Compound("parent",  (P2, Y)),
>     Compound("sibling", (P, P2)))
> ```
> Query cousins: `query(db, Compound("cousin", (v("A"), v("B"))), v("A"), v("B"))`

## Exercise 2 — Implement `reverse/2`

Define `reverse/2` in the mini-Prolog interpreter. The standard Prolog definition uses an accumulator:

```
reverse([], Acc, Acc).
reverse([H|T], Acc, R) :- reverse(T, [H|Acc], R).
reverse(L, R) :- reverse(L, [], R).
```

Add these clauses to a DB instance and test `reverse([1,2,3,4,5], X)`.

[[___]]
<script>true</script>

> In the `Compound/cons/lst` framework of Model 5:
> ```python
> H2, T2, Acc, Rv = v("H2"), v("T2"), v("Acc"), v("Rv")
> NIL = Atom("[]")
> def cons(h, t): return Compound(".", (h, t))
>
> # reverse([], Acc, Acc).
> db.fact("rev3", NIL, Acc, Acc)
>
> # reverse([H|T], Acc, R) :- reverse(T, [H|Acc], R).
> db.rule("rev3", (cons(H2, T2), Acc, Rv),
>     Compound("rev3", (T2, cons(H2, Acc), Rv)))
>
> # reverse(L, R) :- reverse(L, [], R).
> Lv = v("Lv")
> db.rule("reverse", (Lv, Rv), Compound("rev3", (Lv, NIL, Rv)))
> ```
> Query: `query(db, Compound("reverse", (lst(a("1"),a("2"),a("3")), v("R"))), v("R"))`
> Expected output: `R = [3, 2, 1]`

## Exercise 3 — Flatten a Nested List

In Prolog:

```
flatten([], []).
flatten([H|T], F) :- is_list(H), !, flatten(H, FH), flatten(T, FT), append(FH, FT, F).
flatten([H|T], [H|FT]) :- flatten(T, FT).
```

The `is_list/1` predicate checks whether a term is a proper list. Implement this in the mini-Prolog interpreter, adding `is_list` as a Python built-in predicate in the `solve` function. Test with `flatten([1,[2,[3,4]],5], X)`.

[[___]]
<script>true</script>

> Add a built-in check in `solve` before the user-defined clause loop:
> ```python
> def is_list_term(t, s):
>     t = walk(t, s)
>     while isinstance(t, Compound) and t.functor == "." and len(t.args) == 2:
>         t = walk(t.args[1], s)
>     return t == Atom("[]")
>
> # In solve, before "for clause in db.clauses":
> if isinstance(goal, Compound) and goal.functor == "is_list" and len(goal.args) == 1:
>     if is_list_term(goal.args[0], subst):
>         yield from solve(rest, subst, db, depth+1)
>     return
> ```
> Then add the three flatten clauses using cons/NIL.
> Note: the cut in the middle clause stops the third clause from also firing when H is a list.

## Exercise 4 — Connection to Hindley-Milner Type Inference

The unification algorithm from Model 2 is the exact same algorithm used in **Algorithm W** (Hindley-Milner type inference). In that context:

- Type variables (`α`, `β`, `γ`) correspond to Prolog `Var`s
- Type constructors (`Int`, `Bool`, `→`, `[]`) correspond to `Atom`s and `Compound`s
- Unification solves type equations generated by the typing rules

The typing rule for function application is:

$$ \frac{\Gamma \vdash e_1 : \tau_1 \quad \Gamma \vdash e_2 : \tau_2 \quad \text{unify}(\tau_1,\ \tau_2 \to \alpha)}{\Gamma \vdash e_1\ e_2 : \alpha} $$

where $\alpha$ is a fresh type variable. Study the snippet below, which type-checks a small expression using exactly the Robinson unification from Model 2:

```python  liascript
# Exercise 4: Robinson unification powering type inference
from dataclasses import dataclass
from typing import Optional

@dataclass(frozen=True)
class TVar:
    name: str
    def __repr__(self): return self.name

@dataclass(frozen=True)
class TCon:
    name: str
    def __repr__(self): return self.name

@dataclass(frozen=True)
class TApp:
    functor: str
    args: tuple
    def __repr__(self):
        if self.functor == "->" and len(self.args) == 2:
            return f"({self.args[0]} -> {self.args[1]})"
        return f"{self.functor}[{', '.join(repr(a) for a in self.args)}]"

Subst = dict

def walk_t(t, s):
    while isinstance(t, TVar) and t in s: t = s[t]
    return t

def occurs_t(v, t, s):
    t = walk_t(t, s)
    if isinstance(t, TVar):  return t == v
    if isinstance(t, TCon):  return False
    return any(occurs_t(v, a, s) for a in t.args)

def unify_t(t1, t2, s):
    t1, t2 = walk_t(t1, s), walk_t(t2, s)
    if t1 == t2: return s
    if isinstance(t1, TVar):
        if occurs_t(t1, t2, s): return None
        return {**s, t1: t2}
    if isinstance(t2, TVar):
        if occurs_t(t2, t1, s): return None
        return {**s, t2: t1}
    if (isinstance(t1, TApp) and isinstance(t2, TApp)
            and t1.functor == t2.functor and len(t1.args) == len(t2.args)):
        for a, b in zip(t1.args, t2.args):
            s = unify_t(a, b, s)
            if s is None: return None
        return s
    return None

def reify_t(t, s):
    t = walk_t(t, s)
    if isinstance(t, (TVar, TCon)): return t
    return TApp(t.functor, tuple(reify_t(a, s) for a in t.args))

def arrow(a, b): return TApp("->", (a, b))
def list_t(a):   return TApp("[]", (a,))

Int  = TCon("Int"); Bool = TCon("Bool")
_fresh = [0]
def fresh_tvar():
    _fresh[0] += 1; return TVar(f"a{_fresh[0]}")

# -------------------------------------------------------
# Type-check:  map :: (a -> b) -> [a] -> [b]
#              applied to (+1) :: Int -> Int
#              applied to [1,2,3] :: [Int]
# -------------------------------------------------------
alpha, beta = fresh_tvar(), fresh_tvar()
map_type = arrow(arrow(alpha, beta), arrow(list_t(alpha), list_t(beta)))

plus1_type = arrow(Int, Int)

# Applying map to (+1): map_type unifies with (plus1_type -> result)
result1 = fresh_tvar()
s = unify_t(map_type, arrow(plus1_type, result1), {})
if s:
    print("map (+1) ::", reify_t(result1, s))
else:
    print("Type error at first application!")

# Applying result to [1,2,3] :: [Int]
list_int_type = list_t(Int)
result2 = fresh_tvar()
partial = reify_t(result1, s)
s2 = unify_t(partial, arrow(list_int_type, result2), s)
if s2:
    print("map (+1) [1,2,3] ::", reify_t(result2, s2))
else:
    print("Type error at second application!")

# Type error example: applying (+1) to Bool
print()
print("--- Type error: applying (+1) to True ---")
s3 = unify_t(plus1_type, arrow(Bool, fresh_tvar()), {})
if s3 is None:
    print("Type error: cannot unify Int with Bool")
else:
    print("Unexpectedly succeeded:", s3)

# Polymorphic identity: id :: a -> a
alpha2 = fresh_tvar()
id_type = arrow(alpha2, alpha2)
print()
print("id ::", id_type)
a3 = fresh_tvar()
s4 = unify_t(id_type, arrow(Int, a3), {})
print("id Int ::", reify_t(a3, s4))
a4 = fresh_tvar()
s5 = unify_t(id_type, arrow(Bool, a4), {})
print("id Bool ::", reify_t(a4, s5))

# The occurs check in type inference
print()
print("--- Infinite type: unify(a, a -> b) ---")
av = fresh_tvar(); bv = fresh_tvar()
s6 = unify_t(av, arrow(av, bv), {})
print("Result:", s6, "(None = occurs check blocked infinite type)")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

> **CTQ E4.1** In the type inference code, `map_type` is defined using fresh type variables `alpha` and `beta`. When we unify `map_type` with `(Int→Int) → result`, what substitution is produced? What are `alpha` and `beta` bound to?

> **CTQ E4.2** Why do we need *fresh* type variables for each use of a polymorphic function? If we reused the same `alpha` for two calls to `id`, what would go wrong?

> **CTQ E4.3** The occurs check prevents `α = α → α`. In the context of type inference, what kind of type would this represent, and why is it problematic?

## Exercise 5 — miniKanren and Relational Programming

**miniKanren** (Byrd, Friedman, Kiselyov, 2009) embeds logic programming into a host language. The Python library `kanren` (a port of miniKanren) provides the same primitives:

- `run(n, x, goal)` — run `goal`, return up to `n` values of `x`
- `eq(u, v)` — unification goal
- `conde([g1, g2], [g3, g4])` — disjunction (like Prolog's `;`)
- `lall(g1, g2, ...)` — conjunction (like Prolog's `,`)
- `fresh(lambda x, y: ...)` — introduce fresh logic variables

The key insight of miniKanren: **goals are values** — they are first-class functions that take a substitution and return a *stream* of substitutions. This makes logic programming composable in the host language.

```python  liascript
# Exercise 5: miniKanren-style logic programming in pure Python
# We implement the miniKanren core directly -- no external library needed

from dataclasses import dataclass
from typing import Iterator

# --- Terms ---
@dataclass(frozen=True)
class LVar:
    name: str
    def __repr__(self): return f"?{self.name}"

Subst = dict

_vc = [0]
def lvar(name=None):
    _vc[0] += 1
    return LVar(name or f"v{_vc[0]}")

def walk_mk(t, s):
    while isinstance(t, LVar) and t in s: t = s[t]
    return t

def occurs_mk(v, t, s):
    t = walk_mk(t, s)
    if isinstance(t, LVar): return t == v
    if isinstance(t, (list, tuple)):
        return any(occurs_mk(v, a, s) for a in t)
    return False

def unify_mk(t1, t2, s):
    t1, t2 = walk_mk(t1, s), walk_mk(t2, s)
    if t1 == t2: return s
    if isinstance(t1, LVar):
        if occurs_mk(t1, t2, s): return None
        return {**s, t1: t2}
    if isinstance(t2, LVar):
        if occurs_mk(t2, t1, s): return None
        return {**s, t2: t1}
    if isinstance(t1, (list, tuple)) and isinstance(t2, (list, tuple)) and len(t1)==len(t2):
        for a, b in zip(t1, t2):
            s = unify_mk(a, b, s)
            if s is None: return None
        return s
    return None

def reify_mk(t, s):
    t = walk_mk(t, s)
    if isinstance(t, LVar): return t
    if isinstance(t, (list, tuple)):
        return type(t)(reify_mk(a, s) for a in t)
    return t

# --- Goal combinators (miniKanren style) ---
def eq(u, v):
    """Unification goal: succeeds if u and v unify."""
    def goal(s):
        s2 = unify_mk(u, v, s)
        if s2 is not None: yield s2
    return goal

def conde(*clauses):
    """Disjunction: try each clause (list of goals) and interleave results."""
    def goal(s):
        for clause in clauses:
            yield from run_goals(clause, s)
    return goal

def run_goals(goals, s):
    """Run a list of goals conjunctively."""
    if not goals: yield s; return
    g, *rest = goals
    for s2 in g(s):
        yield from run_goals(rest, s2)

def run(n, var, *goals):
    """Run goals, return up to n values of var."""
    results = []
    for s in run_goals(list(goals), {}):
        results.append(reify_mk(var, s))
        if n and len(results) >= n: break
    return results

# --- Library predicates ---
def membero(x, lst):
    """x is a member of lst."""
    h, t = lvar("h"), lvar("t")
    return conde(
        [eq(lst, [x])],
        [eq(lst, [h, *[t]]), membero(x, t)]
    )

# Simpler membero with proper list structure
def membero2(x, lst):
    if not isinstance(lst, list): return eq(False, True)
    if not lst: return eq(False, True)
    return conde(
        [eq(x, lst[0])],
        [membero2(x, lst[1:])] if lst[1:] else [eq(False, True)]
    )

def appendo(x, y, z):
    """Relational append: append(x, y) = z."""
    h, t, r = lvar("h"), lvar("t"), lvar("r")
    return conde(
        [eq(x, []), eq(y, z)],
        [eq(x, [h] + [t]), eq(z, [h] + [r]), appendo(t, y, r)]
    )

# --- Demonstrations ---
x = lvar("x")
print("=== run(0, x, membero2(x, [1,2,3])) ===")
print(run(0, x, membero2(x, [1, 2, 3])))

print()
y = lvar("y")
print("=== run(1, z, appendo([1,2],[3,4], z)) ===")
z = lvar("z")
print(run(1, z, appendo([1, 2], [3, 4], z)))

print()
a2, b2 = lvar("a"), lvar("b")
print("=== splits of [1,2,3]: run(4, (a,b), appendo(a, b, [1,2,3])) ===")
for sol in run(4, (a2, b2), appendo(a2, b2, [1, 2, 3])):
    print(" ", sol)

print()
print("=== run(3, x, membero2(x, ['red','green','blue'])) ===")
xc = lvar("xc")
print(run(3, xc, membero2(xc, ["red", "green", "blue"])))
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

> **CTQ E5.1** Compare the miniKanren `conde` to Prolog's `;`. One key difference is that `conde` interleaves solutions from each branch rather than trying them sequentially. Why does interleaving help with completeness (finding all solutions even when one branch is infinite)?

> **CTQ E5.2** In our mini-Prolog (Model 5), goals are not first-class values — they are terms in the knowledge base. In miniKanren, goals *are* host-language functions. What new capabilities does this give the programmer? Give an example of something easy to express in miniKanren that would require meta-programming tricks in Prolog.

> **CTQ E5.3** The `run` function in miniKanren returns a list of answers. In Prolog, you ask for answers one at a time with `;` at the prompt. What is the trade-off between these two interfaces for a programmer who needs only the *first* answer versus *all* answers?

---

# Reflection Prompt

Take 5–10 minutes individually to respond to the following prompt in your notebook:

> Logic programming inverts the usual programming model: instead of describing *how* to compute, you describe *what is true* and let the engine search. Choose one concept from today — unification, backtracking, bidirectionality, or the connection to type inference — and explain in your own words: (1) what makes it surprising or powerful, (2) a situation in your prior programming experience where this concept would have simplified your code, and (3) a limitation of logic programming that makes it unsuitable as a *general-purpose* language.

---

# Further Reading

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
