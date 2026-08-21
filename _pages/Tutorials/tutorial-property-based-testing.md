---
layout: tutorial
permalink: /Tutorials/PropertyBasedTesting
title: "CS374: Property-Based Testing Your Language with Hypothesis"

info:
  coursenum: CS374
  goals:
    - To explain how property-based testing differs from example-based testing
    - To write a recursive generator of ASTs with hypothesis.strategies.recursive
    - To state and check the round-trip law parse(unparse(ast)) == ast over generated inputs
    - To state and check semantic invariants (determinism, scope restoration, short-circuit non-evaluation) over generated programs
    - To read a shrunk counterexample and use it to locate a real bug

readings:
  - rtitle: "Hypothesis Documentation"
    rlink: "https://hypothesis.readthedocs.io/"
  - rtitle: "Hypothesis: recursive() strategy"
    rlink: "https://hypothesis.readthedocs.io/en/latest/data.html#recursive-data"

tags:
  - testing
  - property-based-testing
  - parser
  - interpreter
  - pipeline
---

# Property-Based Testing Your Language with Hypothesis

This tutorial is the companion to the property-based-testing steps in the **Parser** assignment (Step 3e) and the **Interpreter** assignment (Step 2e). It shows you how to let a library generate thousands of test programs for you and automatically shrink any failure to the smallest program that still breaks, which is exactly the kind of bug your hand-written examples miss.

You already know Python and `pytest`. This tutorial bridges the gap between "my ten test cases pass" and "I have evidence the law holds for *every* program my generator can produce."

---

## Section 1: Why example-based tests are not enough

When you write a test like:

```python
def test_round_trip_simple():
    assert parse(unparse(parse("2 + 3 * 4"))) == parse("2 + 3 * 4")
```

you are checking one program (the one you thought of. But the bugs in a parser or evaluator live in the programs you *didn't* think of: a unary minus applied to a parenthesized subtraction, an operator sitting exactly at a precedence boundary, a right-associative chain nested twelve deep. You cannot enumerate those by hand.

**Property-based testing** flips the process around. Instead of writing examples, you:

1. Describe a *space of inputs* (a generator).
2. State a *property* (a law) that must hold for **every** input in that space.
3. Let the library sample hundreds of inputs, and) when one fails: automatically **shrink** it to a minimal counterexample.

The library we use is [Hypothesis](https://hypothesis.readthedocs.io/), the standard property-based testing tool for Python.

Install it into your project environment:

```bash
uv add hypothesis      # or: pip install hypothesis
```

---

## Section 2: Generating ASTs with `recursive`

The key to testing a language is generating *trees*, not strings, a random string is almost never a valid program, but a random AST always is (and you can `unparse` it to a valid string). Hypothesis builds recursive data with `st.recursive(base, extend)`: `base` is the strategy for leaves, and `extend` takes a strategy for children and returns a strategy for one-level-deeper trees.

Assume your AST node classes are `Num(value)`, `Var(name)`, and `BinOp(op, left, right)`:

```python
from hypothesis import given, strategies as st
from ast_nodes import Num, Var, BinOp   # your own node classes

# Leaves: small numbers and a few variable names
leaves = st.one_of(
    st.integers(min_value=0, max_value=999).map(Num),
    st.sampled_from(["x", "y", "z"]).map(Var),
)

# Recursive step: a binary operator over two sub-expressions
exprs = st.recursive(
    leaves,
    lambda kids: st.builds(
        BinOp,
        st.sampled_from(["+", "-", "*", "/"]),
        kids,
        kids,
    ),
    max_leaves=25,     # cap tree size so tests stay fast
)
```

`max_leaves` bounds how big trees get. Start small (10-25) while developing; raise it once your code passes.

> **Tip:** if your node classes are frozen dataclasses with structural equality (the default for `@dataclass`), `ast1 == ast2` compares whole trees for you; which is exactly what the round-trip law needs.

---

## Section 3: The round-trip law (Parser assignment)

Now state the law: unparsing a tree and re-parsing it must return the same tree.

```python
from parser import parse
from ast_nodes import unparse

@given(exprs)
def test_round_trip(tree):
    assert parse(unparse(tree)) == tree
```

Run it with `pytest`: Hypothesis discovers `@given` tests automatically. On a first parser this usually fails, and Hypothesis prints something like:

```
Falsifying example: test_round_trip(
    tree=BinOp('*', Num(0), BinOp('+', Num(0), Num(0))),
)
```

That is the **minimal** tree that breaks the law. `2 * (3 + 4)` shrank all the way down to `0 * (0 + 0)`, the numbers do not matter, the *shape* does. The bug is almost always in `unparse`: it failed to parenthesize a lower-precedence subtraction/addition under a higher-precedence multiplication. Fix the parenthesization rule and re-run.

**What to report (Parser Step 3e):** the one shrunk counterexample you fixed, its root cause in one sentence, and the fix.

---

## Section 4: Semantic invariants (Interpreter assignment)

The same generator, pointed at your evaluator, checks *meaning*. Restrict the generator to the nodes your evaluator supports, then state invariants:

**Determinism**, same tree, same result, twice:

```python
from interpreter import eval_program, fresh_env

@given(exprs)
def test_deterministic(tree):
    assert eval_program(tree, fresh_env()) == eval_program(tree, fresh_env())
```

**Scope restoration**, an inner `let` does not leak to the outer environment:

```python
@given(exprs, st.sampled_from(["a", "b", "c"]))
def test_scope_restoration(expr, name):
    env = fresh_env()
    # Evaluate a block that binds `name`, then `expr`; the outer env must not gain `name`.
    run_block(env, binds={name: expr})
    assert name not in env.names()
```

**Short-circuit non-evaluation**: the right operand of `false and X` never runs. Give the right side an observable effect (dividing by zero is a convenient one; it raises if evaluated):

```python
@given(exprs)
def test_short_circuit(rhs):
    # `false and (1/0 ...)` must NOT raise, because the RHS is never evaluated
    tree = LogicOp("and", Bool(False), div_by_zero_wrapping(rhs))
    assert eval_program(tree, fresh_env()) is False   # no exception
```

Hypothesis will search for the operand shape that sneaks past a buggy short-circuit implementation.

**What to report (Interpreter Step 2e):** at least three invariants (the first two required), and one that caught a real bug, or a reasoned all-clear with the properties and generator shown.

---

## Section 5: Shrinking, `@example`, and reproducibility

- **Shrinking** is automatic: Hypothesis always reports the *smallest* failing input, which is what makes the counterexample readable.
- **Pin a known-hard case** with `@example(...)` above `@given(...)` so a specific tree is always tested.
- **Reproduce a failure**: Hypothesis prints a `@reproduce_failure` decorator you can paste in to replay the exact input.
- **Keep runs fast** with `max_leaves` and, if needed, `@settings(max_examples=200)`.

---

## Section 6: Reusing this in the Team Language Project

Write your generators and invariant tests so they are parameterized by your node classes and evaluator entry point. When your team integrates the pipeline, the same three invariants (generalized to your team's language) become the backbone of its property-based test suite, and the round-trip generator becomes your parser's regression net. Property-based tests are one of the highest-value, lowest-effort ways to make your language demonstrably correct at Demo Day.
