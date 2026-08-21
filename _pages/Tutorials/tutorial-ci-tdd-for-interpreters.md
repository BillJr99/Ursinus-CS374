---
layout: tutorial
permalink: /Tutorials/CITDDForInterpreters
title: "CS374: CI/CD and TDD for Language Projects"

info:
  coursenum: CS374
  goals:
    - To write a pytest test suite that tests your language interpreter end-to-end
    - To apply test-driven development: write a failing test, then implement the feature to pass it
    - To set up a GitHub Actions workflow that runs your test suite on every push
    - To use coverage reporting to identify untested interpreter paths
    - To structure your interpreter for testability (separating lexer, parser, evaluator)

readings:
  - rtitle: "pytest Documentation"
    rlink: "https://docs.pytest.org/"
  - rtitle: "GitHub Actions Documentation"
    rlink: "https://docs.github.com/en/actions"
  - rtitle: "coverage.py Documentation"
    rlink: "https://coverage.readthedocs.io/"

tags:
  - testing
  - ci-cd
  - tdd
  - final-project
---

# Tutorial: CI/CD and Test-Driven Development for Language Projects

<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374/gh-pages/_pages/Tutorials/tutorial-ci-tdd-for-interpreters.md

import: https://raw.githubusercontent.com/liascript/CodeRunner/master/README.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

# Tutorial: CI/CD and Test-Driven Development for Language Projects

## Learning Goals

By the end of this tutorial, you will have:

- Written a `pytest` test suite that tests your interpreter end-to-end: arithmetic, variables, functions, closures, recursion, and error cases
- Applied test-driven development (TDD): written a failing test for a new language feature, then implemented that feature until the test passes
- Set up a GitHub Actions workflow that runs your full test suite automatically on every push
- Used `coverage.py` to generate an HTML coverage report and identified untested paths in your evaluator
- Structured your interpreter as independent, testable functions so that each stage (lexer, parser, evaluator) can be tested in isolation

Interpreters are unusually hard to debug manually. When you run a program and get the wrong answer, the bug could live in the lexer, the parser, the AST representation, the environment lookup, the evaluator dispatch, or the closure construction. A good test suite isolates each stage and catches regressions the moment you introduce them. Continuous integration then ensures those tests run on every push, not just when you remember to.

**What you need:**

- Python 3.10+
- A terminal with `pip` available
- A GitHub repository containing your interpreter (or the Mini interpreter from the Build-an-Interpreter tutorial)
- `pip install pytest pytest-cov`

---

# Part 1: Why Test Your Interpreter?

## 1.1 The Manual Testing Problem

Consider the typical debugging loop without automated tests:

```
Edit interpreter -> run one example program -> see wrong output -> guess what changed -> repeat
```

This breaks down as soon as you have more than a handful of language features. Adding closures should not break arithmetic. Adding a `while` loop should not break `let` bindings. Without a test suite you will not discover these regressions until a demo.

**Key insight:** An interpreter is a collection of pure-ish functions. `tokenize` maps a string to a list of tokens. `parse` maps tokens to an AST. `evaluate` maps an AST and an environment to a value. Functions with clear inputs and outputs are the easiest things in the world to test.

---

## 1.2 The TDD Mindset for Language Features

Test-driven development inverts the usual order of work:

1. **Red**: write a test that exercises a feature that does not exist yet. Run it. Watch it fail.
2. **Green**: write the minimum code to make the test pass.
3. **Refactor**: clean up, then confirm the test still passes.

For language work, the "feature" is almost always a new construct: a loop, a list literal, a pattern match, a type annotation. Writing the test first forces you to decide exactly what the feature should do before you write a single line of evaluator code. This is the same discipline as writing an operational semantics rule before implementing it.

---

## 1.3 What Continuous Integration Buys You

GitHub Actions runs your test suite every time you push a commit. The benefits for a language project:

- You never merge a branch that breaks the existing test cases.
- Your collaborators (or your future self) can see at a glance whether the interpreter is healthy.
- You can require a green CI badge before merging pull requests for new features.
- Coverage enforcement (via `--cov-fail-under`) prevents you from shipping features with no tests at all.

---

# Part 2: Structuring Your Interpreter for Testability

## 2.1 The Three-Stage Pipeline

The most important architectural decision for testability is keeping the three stages of interpretation as separate, stateless functions:

```python
# lexer.py  - source text -> token list
def tokenize(source: str) -> list[Token]: ...

# parser.py - token list -> AST
def parse(tokens: list[Token]) -> ASTNode: ...

# evaluator.py - AST + environment -> value
def evaluate(ast: ASTNode, env: Environment) -> Value: ...

# mylang.py - convenience entry point
def run(source: str) -> Value:
    return evaluate(parse(tokenize(source)))
```

If each function is pure (no global state, no mutation of shared objects) then every test is three lines: call the function, check the result.

---

## 2.2 The Global-State Trap

The single most common reason test suites fail intermittently is shared mutable state. Consider this evaluator that keeps a global symbol table:

```python
# BAD - global state leaks between tests
_global_env = {}

def evaluate(ast):
    # uses _global_env directly
    ...
```

If test A binds `x = 5` and test B asks for `x`, test B may pass even though it should raise a `NameError`. Worse, the failure depends on test execution order.

The fix is always the same: create a fresh `Environment()` for each test.

```python
# GOOD - each test starts clean
class Environment:
    def __init__(self, parent=None):
        self.bindings = {}
        self.parent   = parent

    def extend(self, name, value):
        child = Environment(parent=self)
        child.bindings[name] = value
        return child

    def lookup(self, name):
        if name in self.bindings:
            return self.bindings[name]
        if self.parent:
            return self.parent.lookup(name)
        raise LangNameError(f"Undefined variable: {name}")
```

When `run(source)` creates a fresh `Environment()` on every call, every test is isolated automatically.

---

## 2.3 Return Values vs. Printed Output

A second common problem: if your interpreter prints results via `print()` instead of returning them, testing requires capturing `sys.stdout`. This is doable, but it adds boilerplate to every test.

The better design is to make `evaluate` return a Python value. Add a thin `run_and_print` wrapper only for the REPL and file-runner:

```python
# evaluator.py
def evaluate(ast: ASTNode, env: Environment) -> Value:
    ...  # pure computation, no print

# repl.py
from evaluator import evaluate
from parser   import parse
from lexer    import tokenize

def repl():
    while True:
        src    = input(">>> ")
        result = evaluate(parse(tokenize(src)), Environment())
        print(result)
```

Now every test is `assert run("1 + 1") == 2`. No output capture needed.

---

# Part 3: Writing pytest Tests for Your Interpreter

## 3.1 Installing pytest

```bash
pip install pytest pytest-cov
```

Verify the installation:

```bash
pytest --version
# pytest 8.x.x
```

Create a `tests/` directory at the top level of your project:

```
my-interpreter/
    lexer.py
    parser.py
    evaluator.py
    mylang.py
    tests/
        __init__.py          # empty file; makes tests/ a package
        test_mylang.py
```

---

## 3.2 A Complete Test File

The following `test_mylang.py` covers the core features of the Mini interpreter from class. Adapt the imports and the language syntax to match your own project.

```python
# tests/test_mylang.py
import pytest
from mylang import run, tokenize, parse
from lexer   import LexError
from parser  import ParseError
from evaluator import LangNameError, LangTypeError

# ---------------------------------------------------------------------------
# Arithmetic
# ---------------------------------------------------------------------------

class TestArithmetic:
    def test_integer_literal(self):
        assert run("42") == 42

    def test_negative_literal(self):
        assert run("-7") == -7

    def test_addition(self):
        assert run("1 + 2") == 3

    def test_subtraction(self):
        assert run("10 - 3") == 7

    def test_multiplication(self):
        assert run("4 * 5") == 20

    def test_division(self):
        assert run("10 / 2") == 5

    def test_operator_precedence(self):
        # Multiplication binds tighter than addition: 2 + (3 * 4) = 14
        assert run("2 + 3 * 4") == 14

    def test_left_associativity(self):
        # Subtraction is left-associative: (10 - 3) - 2 = 5
        assert run("10 - 3 - 2") == 5

    def test_parentheses_override_precedence(self):
        assert run("(2 + 3) * 4") == 20

    def test_nested_parens(self):
        assert run("((1 + 2) * (3 + 4))") == 21

# ---------------------------------------------------------------------------
# Booleans and comparisons
# ---------------------------------------------------------------------------

class TestBooleans:
    def test_true_literal(self):
        assert run("true") is True

    def test_false_literal(self):
        assert run("false") is False

    def test_equality_true(self):
        assert run("3 == 3") is True

    def test_equality_false(self):
        assert run("3 == 4") is False

    def test_less_than(self):
        assert run("2 < 5") is True

    def test_greater_than(self):
        assert run("5 > 2") is True

    def test_if_true_branch(self):
        assert run("if true then 1 else 2") == 1

    def test_if_false_branch(self):
        assert run("if false then 1 else 2") == 2

    def test_if_condition_is_expression(self):
        assert run("if 3 < 5 then 10 else 20") == 10

# ---------------------------------------------------------------------------
# Variables and let-bindings
# ---------------------------------------------------------------------------

class TestVariables:
    def test_let_binding_used_in_body(self):
        assert run("let x = 5 in x + 1") == 6

    def test_nested_let(self):
        assert run("let x = 3 in let y = 4 in x + y") == 7

    def test_let_shadows_outer(self):
        assert run("let x = 1 in let x = 2 in x") == 2

    def test_outer_binding_restored_after_shadow(self):
        # The outer x should still be 1 in the outer scope
        assert run("let x = 1 in (let x = 2 in 0) + x") == 1

    def test_undefined_variable_raises(self):
        with pytest.raises(LangNameError):
            run("x + 1")

    def test_undefined_variable_message(self):
        with pytest.raises(LangNameError, match="x"):
            run("x + 1")

# ---------------------------------------------------------------------------
# Functions and closures
# ---------------------------------------------------------------------------

class TestFunctions:
    def test_identity_function(self):
        assert run("(fun x -> x) 42") == 42

    def test_constant_function(self):
        assert run("(fun x -> 7) 99") == 7

    def test_function_uses_argument(self):
        assert run("(fun x -> x + 1) 5") == 6

    def test_curried_addition(self):
        assert run("""
            let add = fun x -> fun y -> x + y in
            add 3 4
        """) == 7

    def test_closure_captures_outer_variable(self):
        assert run("""
            let add5 = let n = 5 in fun x -> x + n in
            add5 3
        """) == 8

    def test_closure_in_let(self):
        assert run("""
            let add = fun x -> fun y -> x + y in
            let add5 = add 5 in
            add5 3
        """) == 8

    def test_higher_order_function(self):
        assert run("""
            let apply = fun f -> fun x -> f x in
            apply (fun x -> x * 2) 6
        """) == 12

    def test_function_returned_from_function(self):
        assert run("""
            let make_adder = fun n -> fun x -> x + n in
            let add10 = make_adder 10 in
            add10 32
        """) == 42

# ---------------------------------------------------------------------------
# Recursion via letrec
# ---------------------------------------------------------------------------

class TestRecursion:
    def test_factorial_base_case(self):
        assert run("""
            letrec fact = fun n ->
                if n == 0 then 1 else n * fact (n - 1) in
            fact 0
        """) == 1

    def test_factorial_five(self):
        assert run("""
            letrec fact = fun n ->
                if n == 0 then 1 else n * fact (n - 1) in
            fact 5
        """) == 120

    def test_fibonacci(self):
        assert run("""
            letrec fib = fun n ->
                if n == 0 then 0
                else if n == 1 then 1
                else fib (n - 1) + fib (n - 2) in
            fib 7
        """) == 13

    def test_mutual_even_odd(self):
        # Requires your interpreter to support mutual recursion via letrec-and or similar
        # Skip this test if your language does not support mutual recursion yet
        pytest.skip("mutual recursion not yet implemented")

# ---------------------------------------------------------------------------
# Error handling
# ---------------------------------------------------------------------------

class TestErrors:
    def test_lex_error_on_unknown_character(self):
        with pytest.raises(LexError):
            run("1 @ 2")

    def test_parse_error_on_missing_in(self):
        with pytest.raises(ParseError):
            run("let x = 5 x")

    def test_parse_error_on_incomplete_if(self):
        with pytest.raises(ParseError):
            run("if true then 1")

    def test_type_error_on_adding_bool(self):
        with pytest.raises(LangTypeError):
            run("1 + true")

    def test_type_error_on_calling_non_function(self):
        with pytest.raises(LangTypeError):
            run("42 7")

    def test_name_error_in_function_body(self):
        with pytest.raises(LangNameError):
            run("(fun x -> y) 1")

# ---------------------------------------------------------------------------
# Lexer-level tests (stage isolation)
# ---------------------------------------------------------------------------

class TestLexer:
    def test_single_number(self):
        tokens = tokenize("42")
        assert tokens[0].type == "NUMBER"
        assert tokens[0].value == 42

    def test_keywords_recognized(self):
        tokens = tokenize("let x = 5 in x")
        types = [t.type for t in tokens]
        assert "LET" in types
        assert "IN"  in types

    def test_eof_token_present(self):
        tokens = tokenize("1")
        assert tokens[-1].type == "EOF"

    def test_empty_source(self):
        tokens = tokenize("")
        assert tokens[0].type == "EOF"
```

---

## 3.3 Parametrized Tests

When you have a table of input-output pairs that all exercise the same code path, use `@pytest.mark.parametrize` instead of copying the same test body:

```python
import pytest
from mylang import run

@pytest.mark.parametrize("src,expected", [
    ("1 + 1",   2),
    ("10 - 3",  7),
    ("2 * 6",  12),
    ("10 / 2",  5),
    ("3 + 4 * 2", 11),
    ("(3 + 4) * 2", 14),
])
def test_arithmetic_ops(src, expected):
    assert run(src) == expected

@pytest.mark.parametrize("src,expected", [
    ("if true  then 1 else 2", 1),
    ("if false then 1 else 2", 2),
    ("if 1 < 2 then 10 else 20", 10),
    ("if 2 < 1 then 10 else 20", 20),
])
def test_conditionals(src, expected):
    assert run(src) == expected
```

pytest will report each combination as a separate test case, so you see exactly which input failed:

```
FAILED tests/test_mylang.py::test_arithmetic_ops[3 + 4 * 2-11]
```

---

## 3.4 Running Your Tests

```bash
# Run all tests, verbose output
pytest tests/ -v

# Run only one class
pytest tests/test_mylang.py::TestFunctions -v

# Run tests whose name contains "closure"
pytest tests/ -k "closure" -v

# Stop at the first failure
pytest tests/ -x
```

A passing run looks like this:

```
tests/test_mylang.py::TestArithmetic::test_integer_literal     PASSED
tests/test_mylang.py::TestArithmetic::test_addition            PASSED
tests/test_mylang.py::TestFunctions::test_closure_in_let       PASSED
...
===================== 42 passed in 0.31s =====================
```

---

# Part 4: Test-Driven Development, Adding a Feature

## 4.1 The Red-Green-Refactor Cycle in Practice

We will walk through adding a `while` loop to the Mini interpreter using strict TDD. The syntax will be:

```
while <condition> do <body> done
```

The loop evaluates `body` repeatedly as long as `condition` is `true`. Because Mini is expression-oriented and a `while` loop's value is not meaningful, we will say it returns `0` when the condition becomes false.

---

## 4.2 Step 1: Write the Failing Test (Red)

Add this test to `tests/test_mylang.py` before touching any interpreter code:

```python
class TestWhileLoop:
    def test_while_counts_to_three(self):
        # Uses mutable state; assumes your interpreter supports assignment
        assert run("""
            let x = 0 in
            while x < 3 do
                x = x + 1
            done;
            x
        """) == 3

    def test_while_body_never_runs(self):
        assert run("""
            let x = 0 in
            while false do
                x = x + 1
            done;
            x
        """) == 0

    def test_while_returns_zero(self):
        assert run("while false do 1 done") == 0
```

Run pytest:

```bash
pytest tests/test_mylang.py::TestWhileLoop -v
```

Expected output:

```
FAILED tests/test_mylang.py::TestWhileLoop::test_while_counts_to_three
  ParseError: unexpected token 'while'
```

The test is **Red**: it fails with a `ParseError` because the parser does not yet know about `while`.

---

## 4.3 Step 2: Add the AST Node and Token

In `lexer.py`, register `while`, `do`, and `done` as keywords:

```python
KEYWORDS = {
    # ... existing keywords ...
    "while": "WHILE",
    "do":    "DO",
    "done":  "DONE",
}
```

In `ast_nodes.py` (or wherever your AST nodes live), add:

```python
@dataclass
class WhileExpr:
    cond: ASTNode
    body: ASTNode
    line: int
```

Run pytest again: the `ParseError` about `while` being an unexpected token is gone, but now you get a different error because the parser still does not produce a `WhileExpr`.

---

## 4.4 Step 3: Parse the `while` Expression

In `parser.py`, add a branch in your top-level expression parser:

```python
def parse_expr(self) -> ASTNode:
    if self.current().type == "WHILE":
        return self.parse_while()
    # ... existing branches ...

def parse_while(self) -> WhileExpr:
    line = self.current().line
    self.expect("WHILE")
    cond = self.parse_expr()
    self.expect("DO")
    body = self.parse_expr()
    self.expect("DONE")
    return WhileExpr(cond=cond, body=body, line=line)
```

Run pytest:

```bash
pytest tests/test_mylang.py::TestWhileLoop -v
```

Now you get a different error:

```
FAILED tests/test_mylang.py::TestWhileLoop::test_while_counts_to_three
  AttributeError: Evaluator has no method eval_WhileExpr
```

Progress: parsing works, evaluation is missing.

---

## 4.5 Step 4: Evaluate the `while` Expression (Green)

In `evaluator.py`, add:

```python
def eval_WhileExpr(self, node: WhileExpr, env: Environment) -> Value:
    while True:
        cond = self.evaluate(node.cond, env)
        if not isinstance(cond, bool):
            raise LangTypeError(
                f"while condition must be boolean, got {type(cond).__name__}",
                node.line,
            )
        if not cond:
            return 0
        self.evaluate(node.body, env)
```

Run pytest:

```bash
pytest tests/test_mylang.py::TestWhileLoop -v
```

```
PASSED tests/test_mylang.py::TestWhileLoop::test_while_counts_to_three
PASSED tests/test_mylang.py::TestWhileLoop::test_while_body_never_runs
PASSED tests/test_mylang.py::TestWhileLoop::test_while_returns_zero
```

All three tests are **Green**. Now run the full suite to confirm no regressions:

```bash
pytest tests/ -v
```

Every pre-existing test still passes. The `while` feature is shipped.

---

## 4.6 Step 5: Refactor

Now that the tests are green, you can safely clean up. For example, if `eval_WhileExpr` duplicates a type-checking pattern used in `eval_IfExpr`, extract a helper:

```python
def _assert_bool(self, value, construct_name: str, line: int) -> None:
    if not isinstance(value, bool):
        raise LangTypeError(
            f"{construct_name} condition must be boolean, got {type(value).__name__}",
            line,
        )
```

Run pytest after the refactor to confirm nothing broke. This is the refactor step: change structure, not behavior, and let the tests catch you if you slip.

---

# Part 5: GitHub Actions CI

## 5.1 Creating the Workflow File

Create the directory `.github/workflows/` at the root of your repository, then create the file `test.yml` inside it:

```bash
mkdir -p .github/workflows
```

```yaml
# .github/workflows/test.yml
name: Test Interpreter

on:
  push:
    branches:
      - main
      - "claude/**"
  pull_request:
    branches:
      - main

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
      - name: Check out source
        uses: actions/checkout@v4

      - name: Set up Python 3.12
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'

      - name: Install dependencies
        run: pip install pytest pytest-cov

      - name: Run test suite
        run: pytest tests/ -v --tb=short

      - name: Enforce coverage threshold
        run: pytest tests/ --cov=. --cov-report=term-missing --cov-fail-under=70
```

---

## 5.2 What Each Section Does

**`on`**: triggers for this workflow:

- `push` to `main` or any branch starting with `claude/` runs the suite immediately.
- `pull_request` targeting `main` runs the suite on every PR update.

**`jobs`**: a workflow has one or more jobs. Each job runs on a fresh virtual machine. Our single `test` job runs on the latest Ubuntu image (`ubuntu-latest`).

**`steps`**: sequential commands inside the job:

| Step | What it does |
|---|---|
| `actions/checkout@v4` | Clones your repository into the VM |
| `actions/setup-python@v5` | Installs Python 3.12 and adds it to `PATH` |
| `pip install pytest pytest-cov` | Installs your test toolchain |
| `pytest tests/ -v --tb=short` | Runs all tests; `--tb=short` prints concise tracebacks |
| `pytest ... --cov-fail-under=70` | Fails the job if coverage drops below 70% |

**`--cov-fail-under=70`** - if your test suite covers fewer than 70% of your interpreter's lines, the CI job fails and GitHub marks the commit with a red X. This prevents you from shipping a feature with zero test coverage. You can raise the threshold over time as your suite grows.

---

## 5.3 Adding a Status Badge

After your first CI run completes, add a badge to your repository's `README.md`:

```markdown
![Tests](https://github.com/YOUR_USERNAME/YOUR_REPO/actions/workflows/test.yml/badge.svg)
```

Replace `YOUR_USERNAME` and `YOUR_REPO` with your actual GitHub username and repository name. The badge turns green when the suite passes and red when it fails.

---

## 5.4 Dependencies File (Optional but Recommended)

If your interpreter has additional dependencies beyond the standard library (e.g., `ply` for lexing), add a `requirements.txt`:

```
pytest>=8.0
pytest-cov>=5.0
ply>=3.11
```

Then change the install step in `test.yml`:

```yaml
      - name: Install dependencies
        run: pip install -r requirements.txt
```

This ensures CI and your local environment stay in sync.

---

# Part 6: Coverage Reporting

## 6.1 Running Coverage Locally

```bash
# Collect coverage data and print a per-file summary
pytest tests/ --cov=. --cov-report=term-missing
```

Sample output:

```
---------- coverage: platform linux, python 3.12 ----------
Name             Stmts   Miss  Cover   Missing
------------------------------------------------
evaluator.py        94     18    81%   47, 112-118, 203-210
lexer.py            61      4    93%   88-91
parser.py           80      7    91%   144-150
mylang.py           12      0   100%
------------------------------------------------
TOTAL              247     29    88%
```

The `Missing` column shows the exact line numbers not covered by any test.

---

## 6.2 HTML Report

```bash
pytest tests/ --cov=. --cov-report=html
open htmlcov/index.html   # macOS
xdg-open htmlcov/index.html   # Linux
```

The HTML report color-codes every line: green means covered, red means not covered. This makes it easy to spot entire branches of the evaluator that no test exercises.

---

## 6.3 Common Blind Spots

After running coverage on a typical Mini interpreter, these areas tend to show up red:

**Error recovery paths**

```python
def eval_BinOp(self, node, env):
    left  = self.evaluate(node.left,  env)
    right = self.evaluate(node.right, env)
    if node.op == "+":
        if not (isinstance(left, int) and isinstance(right, int)):
            raise LangTypeError(...)   # <-- often untested
        return left + right
```

Fix: add a test like `test_type_error_on_adding_bool` in `TestErrors`.

**The `else` branch of every conditional in the evaluator**

If you only test happy-path programs, every `else raise RuntimeError` stays red. Add one test per error type.

**The EOF / empty-input case in the lexer**

```python
def tokenize(source: str) -> list[Token]:
    if not source.strip():      # <-- easy to miss
        return [Token("EOF", None, 1, 1)]
    ...
```

Fix: `test_empty_source` in `TestLexer` above.

**Recursion base cases**

It is easy to write a factorial test for `n=5` and forget `n=0`. Add both.

---

## 6.4 Excluding Generated or Boilerplate Code

If you have files that should not count toward coverage (e.g., the REPL, a file-runner, or generated parser tables), add a `.coveragerc` file:

```ini
# .coveragerc
[run]
omit =
    repl.py
    tests/*
    setup.py
```

Then coverage reports will only grade the core interpreter modules.

---

# Part 7: Common Pitfalls

## 7.1 Global State Breaks Test Isolation

Already discussed in Part 2, but worth repeating because it is the most common cause of mysterious, order-dependent test failures:

```python
# BAD
_env = {}

def run(source):
    # modifies _env in place
    ...

# GOOD
def run(source):
    env = Environment()   # fresh for every call
    return evaluate(parse(tokenize(source)), env)
```

If you find tests passing in isolation but failing when the full suite runs, global state is almost always the cause. Run `pytest -p no:randomly` to fix test order and isolate the problem.

---

## 7.2 Testing Output Instead of Return Values

If your evaluator calls `print()` and returns `None`, you must capture stdout in every test:

```python
# Painful
import sys
from io import StringIO

def test_print_statement(capsys):
    run('print 42')
    captured = capsys.readouterr()
    assert captured.out.strip() == "42"
```

This is manageable for a few tests but becomes tedious at scale. The better fix is to have `evaluate` return the value and let the REPL handle printing. Tests then look like `assert run("42") == 42`.

If you have already committed to a print-based design, pytest's built-in `capsys` fixture (shown above) is the cleanest approach.

---

## 7.3 Floating-Point Comparison

If your language supports floating-point:

```python
# BAD; may fail due to floating-point rounding
assert run("0.1 + 0.2") == 0.3

# GOOD
import math
assert math.isclose(run("0.1 + 0.2"), 0.3, rel_tol=1e-9)

# or with pytest
assert run("0.1 + 0.2") == pytest.approx(0.3)
```

---

## 7.4 Dict Ordering in Environment Display

If your interpreter has a `debug` or `print-env` feature that displays the current environment, do not compare the raw string - dictionaries preserve insertion order in Python 3.7+ but tests should not rely on that if the order is semantically arbitrary:

```python
# BAD
assert run("debug-env") == "{'x': 1, 'y': 2}"

# GOOD, parse the output and compare as a set of pairs
result = run("debug-env")
pairs  = set(result.strip("{}").split(", "))
assert pairs == {"'x': 1", "'y': 2"}
```

---

## 7.5 Skipping Unimplemented Features Cleanly

When you write tests for a feature before implementing it, use `pytest.skip` or `pytest.mark.xfail` rather than commenting out the test:

```python
@pytest.mark.xfail(reason="list literals not yet implemented", strict=True)
def test_list_literal():
    assert run("[1, 2, 3]") == [1, 2, 3]
```

`strict=True` means the test suite fails if the test unexpectedly passes: a reminder that you should remove the `xfail` marker once the feature ships.

---

## Exercises

### Exercise 1: Bootstrap Your Test Suite (30 min)

Take your current interpreter (or the Mini interpreter from the Build-an-Interpreter tutorial). Create `tests/__init__.py` and `tests/test_mylang.py`. Copy the `TestArithmetic` and `TestVariables` classes from Section 3.2, adjusting imports and language syntax to match your project. Run `pytest tests/ -v`. Aim for all tests green before proceeding.

### Exercise 2: TDD: Add String Literals (45 min)

Using strict TDD:

1. Write a failing test: `assert run('"hello"') == "hello"` and `assert run('"a" + "b"') == "ab"`.
2. Run pytest: confirm Red.
3. Add string tokens to the lexer, a `StringLit` AST node to the parser, and `eval_StringLit` to the evaluator.
4. Run pytest: confirm Green.
5. Run the full suite to confirm no regressions.

### Exercise 3: Set Up GitHub Actions (20 min)

Create `.github/workflows/test.yml` using the template from Section 5.1. Push it to your repository. Open the GitHub Actions tab and watch the first run. If the run fails, read the log and fix the issue.

### Exercise 4: Coverage Hunt (30 min)

Run `pytest tests/ --cov=. --cov-report=html`. Open `htmlcov/index.html`. Find the three largest blocks of red (uncovered) lines in your evaluator. Write a test for each one. Re-run coverage and confirm the lines turn green.

### Exercise 5: Parametrize a Test Class (15 min)

Pick the `TestArithmetic` class or the `TestBooleans` class. Replace the individual test methods with a single `@pytest.mark.parametrize` test. Confirm the parametrized version reports the same results as the original.

---

## Further Reading

- Krekel, Holger, et al. *pytest: helps you write better programs*. pytest.org, 2024. https://docs.pytest.org/
- GitHub. *GitHub Actions Documentation*. docs.github.com, 2024. https://docs.github.com/en/actions
- Batchelder, Ned. *coverage.py: Code Coverage for Python*. coverage.readthedocs.io, 2024. https://coverage.readthedocs.io/
- Beck, Kent. *Test Driven Development: By Example*. Addison-Wesley, 2002., The original TDD book; the Red-Green-Refactor cycle comes from Chapter 1.
- Fowler, Martin. *Refactoring: Improving the Design of Existing Code*, 2nd ed. Addison-Wesley, 2018., Chapter 4 covers test strategy for larger systems.

# From the Sprint Studio: Velocity and Red-Green Discipline

Two studio tools from the Sprint Studio sessions: measuring what "done" means across sprints, and writing the test before the code.

## Model 1: Sprint Velocity; Measuring What "Done" Looks Like

Velocity is the sprint's heartbeat reading: a falling trend is your early warning system, and a flat trend three sprints before the deadline is a crisis that has not been named yet. This model simulates three sprints with concrete numbers so you can see what a healthy trajectory looks like versus a warning trajectory, and practice interpreting the dashboard before your own numbers are in it.

A sprint velocity is a *count*, not a feeling. The Evaluator tracks two numbers: **stories completed** (AST nodes with passing tests) and **tests passing**. The cell below simulates a three-sprint project and visualizes the velocity trend, because a slowing velocity three sprints before Demo Day is early warning, not bad luck.

```python
# Sprint health dashboard: velocity, test coverage, and projection.
# Edit the DATA dict to reflect your team's actual numbers each sprint.

DATA = {
    "Sprint 1": {
        "nodes_planned": 8,
        "nodes_done":    6,
        "tests_passing": 14,
        "tests_total":   18,
        "sample_programs_running": 1,
        "known_failures": ["string concatenation crashes", "nested if not parsed"],
    },
    "Sprint 2": {
        "nodes_planned": 6,
        "nodes_done":    5,
        "tests_passing": 22,
        "tests_total":   26,
        "sample_programs_running": 3,
        "known_failures": ["function return value sometimes None"],
    },
    "Sprint 3": {
        "nodes_planned": 4,
        "nodes_done":    4,
        "tests_passing": 30,
        "tests_total":   30,
        "sample_programs_running": 5,
        "known_failures": [],
    },
}

TOTAL_NODES = 18  # total nodes in the node inventory

print("=" * 60)
print("SPRINT HEALTH DASHBOARD")
print("=" * 60)
print()

completed_so_far = 0
for sprint, d in DATA.items():
    velocity = d["nodes_done"] / d["nodes_planned"] if d["nodes_planned"] else 0
    test_pct  = d["tests_passing"] / d["tests_total"] * 100 if d["tests_total"] else 0
    bar_v     = "#" * d["nodes_done"] + "." * (d["nodes_planned"] - d["nodes_done"])
    bar_t     = "#" * (d["tests_passing"] // 2) + "." * ((d["tests_total"] - d["tests_passing"]) // 2)

    print(f"-- {sprint} ----------------------------------")
    print(f"  Nodes:   [{bar_v}]  {d['nodes_done']}/{d['nodes_planned']} ({velocity*100:.0f}%)")
    print(f"  Tests:   [{bar_t}]  {d['tests_passing']}/{d['tests_total']} ({test_pct:.0f}%)")
    print(f"  Samples: {d['sample_programs_running']} running")
    if d["known_failures"]:
        print(f"  Known failures ({len(d['known_failures'])}):")
        for f in d["known_failures"]:
            print(f"    * {f}")
    else:
        print(f"  Known failures: none OK")
    completed_so_far += d["nodes_done"]
    print()

remaining = TOTAL_NODES - completed_so_far
last_velocity = DATA["Sprint 3"]["nodes_done"] / DATA["Sprint 3"]["nodes_planned"]
sprints_needed = remaining / (last_velocity * DATA["Sprint 3"]["nodes_planned"]) if last_velocity > 0 else float("inf")

print("-- Projection -------------------------------------")
print(f"  Total nodes:        {TOTAL_NODES}")
print(f"  Completed so far:   {completed_so_far}")
print(f"  Remaining:          {remaining}")
print(f"  Last sprint rate:   {last_velocity*100:.0f}% ({DATA['Sprint 3']['nodes_done']}/{DATA['Sprint 3']['nodes_planned']})")
if remaining == 0:
    print(f"  -> All nodes complete! Ready for Demo Day polish. OK")
elif sprints_needed <= 1:
    print(f"  -> On track: ~{sprints_needed:.1f} sprints to clear remaining nodes.")
else:
    print(f"  -> WARNING: at current rate, ~{sprints_needed:.1f} more sprints needed. Re-scope now.")

print()
print("  Rule: a sprint with more than 2 known failures is not done.")
print("  Rule: test_pct < 80% triggers a test-debt sprint before new features.")
```

> **Watch out!** The projection formula assumes your last sprint's velocity holds constant. Real project velocity rarely stays constant; it often drops in the final sprint due to integration work and debugging. If you are already at 80% velocity, the projection is optimistic. Use the projection as a floor, not a ceiling.

### Critical Thinking Questions

1. The dashboard reports "known failures." Why is it *better* to list them than to omit them? Connect to the gallery walk protocol's requirement that every host show at least one failure.
2. If the projection says "2.3 more sprints" and only 1 sprint remains, what are the two legitimate responses? (Hint: one improves execution; the other improves scope.) Which is harder, and why?
3. "Mostly working" is not a status. Rewrite each of these non-statuses as a measurable status using the dashboard's vocabulary: "the parser is almost done," "tests are passing," "the niche feature is nearly complete."

---

## Model 2: The Red-Green Discipline - Writing Tests Before Code

A failing test is not a sign of failure: it is a specification. Before a feature exists, the only accurate representation of "we plan to build this" is a test that currently fails. This model makes that discipline concrete by treating the set of failing tests as the literal sprint backlog, so the sprint goal is visible and measurable at every moment.

The Evaluator's job is to write **failing tests** before the Builder writes the code they test. A failing test is a specification: it states precisely what the code must do before the code exists. The cell below demonstrates the discipline by running a test suite against a deliberately incomplete interpreter, showing which tests fail (red), which pass (green), and what the gap is.

```python
# Demonstrate red-green testing: tests written first, implementation following.
# Edit the 'implemented' set to simulate different sprint states.

# -- Sprint State --------------------------------------------------------------
# Set each feature to True when it is implemented in your interpreter.
IMPLEMENTED = {
    "NumLit":     True,
    "StrLit":     True,
    "BoolLit":    True,
    "BinOp_arith": True,
    "BinOp_compare": True,
    "LetStmt":    True,
    "VarRef":     True,
    "IfStmt":     True,
    "WhileStmt":  False,   # <- not yet implemented
    "FunDecl":    False,   # <- not yet implemented
    "Call":       False,   # <- not yet implemented
    "ReturnStmt": False,
    "PrintStmt":  True,
    "LogicOp":    False,   # short-circuit
    "StringConcat": False, # "a" + "b"
}

# -- Test Registry -------------------------------------------------------------
# Each test: (description, required_feature, expected_output)
TESTS = [
    ("Integer literal",          "NumLit",       "42"),
    ("String literal",           "StrLit",       "hello"),
    ("Boolean literal",          "BoolLit",      "true"),
    ("Addition 2+3",             "BinOp_arith",  "5"),
    ("Subtraction 10-4",         "BinOp_arith",  "6"),
    ("Multiplication 3*4",       "BinOp_arith",  "12"),
    ("Division 10/4",            "BinOp_arith",  "2.5"),
    ("Comparison 3 < 5",         "BinOp_compare","true"),
    ("Equality 5 == 5",          "BinOp_compare","true"),
    ("Let x = 5; print x",       "LetStmt",      "5"),
    ("Variable reference",       "VarRef",       "10"),
    ("If true print yes",        "IfStmt",       "yes"),
    ("If false print no",        "IfStmt",       "no"),
    ("While count down",         "WhileStmt",    "0"),
    ("Function declaration",     "FunDecl",      None),
    ("Function call",            "Call",         "42"),
    ("Return statement",         "ReturnStmt",   "7"),
    ("Print statement",          "PrintStmt",    "hello world"),
    ("Short-circuit: and",       "LogicOp",      "false"),
    ("Short-circuit: or",        "LogicOp",      "true"),
    ("String concat 'a'+'b'",    "StringConcat", "ab"),
]

# -- Run and Report -------------------------------------------------------------
passing = [t for t in TESTS if IMPLEMENTED.get(t[1], False)]
failing = [t for t in TESTS if not IMPLEMENTED.get(t[1], False)]

print("=" * 55)
print(f"  TEST RESULTS, Sprint {sum(IMPLEMENTED.values())}/{len(IMPLEMENTED)} features")
print("=" * 55)
print()
print("  OK PASSING")
for desc, feat, expected in passing:
    print(f"    OK  {desc}")

print()
print("  FAIL FAILING (specification written, not yet implemented)")
for desc, feat, expected in failing:
    label = f"[{feat}]"
    print(f"    FAIL  {desc:<35} {label}")

print()
print(f"  Summary: {len(passing)}/{len(TESTS)} tests passing ({len(passing)/len(TESTS)*100:.0f}%)")
print()
if len(failing) == 0:
    print("  All tests green. Sprint goal met. OK")
elif len(failing) <= 3:
    print(f"  {len(failing)} test(s) remaining. Sprint finish is this session.")
else:
    print(f"  {len(failing)} tests still failing. Evaluate sprint scope with Coordinator.")
print()
print("  Key: failing tests ARE the sprint backlog. Each FAIL is the next task.")
```

### Critical Thinking Questions

4. The test for `FunDecl` has `expected_output = None` (no known output yet, just a known requirement. What does this represent in the red-green discipline, and why is it still worth writing the test?
5. If the Evaluator writes 5 new failing tests at the start of the sprint, and the Builder closes 3 of them, what is the sprint's velocity? Is a sprint with 2 remaining failing tests "done"?
6. The test suite acts as executable documentation of the language's semantics. Which is more authoritative: a test that passes, or the corresponding entry in `SEMANTICS.md`? What should you do when they disagree?

---

