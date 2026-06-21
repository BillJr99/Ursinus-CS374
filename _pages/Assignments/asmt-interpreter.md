---
layout: assignment
permalink: /Assignments/Interpreter
title: "CS374: Principles of Programming Languages - The Interpreter"

info:
  coursenum: CS374
  points: 100
  goals:
    - To define a complete set of AST node dataclasses covering every language construct
    - To implement a tree-walking evaluator over the AST with strong dynamic typing
    - To implement nested scopes with an Environment class distinguishing definition from assignment
    - To build a REPL and file-runner with stage-identified error messages
    - To document the language semantics exhaustively with a SEMANTICS.md file
  rubric:
    - weight: 25
      description: AST Node Dataclasses
      preemerging: Fewer than half the required node types are defined, or the dataclass structure does not match the parser's output
      beginning: All required node types exist but several are missing fields, have incorrect types, or lack documented field meanings
      progressing: All required node types are defined with correct fields and a useful __repr__, but source-position information is missing from most nodes
      proficient: All required node types are defined as dataclasses with every field documented, source-position (line/col) stored for nodes where it aids error reporting, a complete visitor dispatch table or isinstance chain is present, and the node hierarchy is consistent with the parser's output
    - weight: 35
      description: Tree-Walking Evaluator
      preemerging: The evaluator fails to run or fails most provided programs due to major structural errors such as missing cases or infinite loops
      beginning: The evaluator runs but fails on several programs — e.g., nested scopes leak, type errors are not raised, or short-circuit logic evaluates both branches always
      progressing: The evaluator passes the provided programs but fails on hidden edge cases — e.g., a scope is not discarded after a block, or division by zero crashes Python instead of raising a language error
      proficient: A correct evaluator passes all provided and hidden programs; nested scopes behave per documented semantics; type errors name both operand types; short-circuit logic is verified by a non-evaluation test; division by zero, undefined variables, and undefined operations are all raised as language-level errors with stage and position
    - weight: 20
      description: REPL and File Runner
      preemerging: Neither the REPL nor the file runner exists, or both crash on the first error
      beginning: One of the two exists but dies on any error, or the REPL does not maintain state between inputs
      progressing: Both exist and survive most errors, but one error class (e.g., type errors) still crashes the REPL, or the file runner does not identify the stage in its error messages
      proficient: Both the REPL and file runner work; the REPL maintains a persistent environment across inputs and survives all error classes (lexical, syntax, name, type, zero-division) with a clear recover-and-continue behavior; the file runner identifies the stage and position in every error message; a transcript demonstrates each error class and recovery
    - weight: 20
      description: Error Messages with Stage Identification
      preemerging: Errors are unhandled Python exceptions with no stage identification
      beginning: Errors are caught but the stage (lexical vs. syntax vs. runtime) is not identified, or the position is absent
      progressing: Most error classes are caught with stage and position, but one class (e.g., type errors) is missing position or stage identification
      proficient: Every error class — LexError, ParseError, NameError, TypeError, ZeroDivisionError — is caught at the appropriate stage, reported with a message of the form "Stage error at line L, col C: <description>", and SEMANTICS.md includes one example program that triggers each error class with the expected message shown
  readings:
    - rtitle: "Tree-Walking Interpretation Activity"
      rlink: "https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374/gh-pages/_pages/Activities/liascript-interpretation.md"
    - rtitle: "Environments Activity"
      rlink: "https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374/gh-pages/_pages/Activities/liascript-environments.md"
    - rtitle: "Control Flow Semantics Activity"
      rlink: "https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374/gh-pages/_pages/Activities/liascript-controlflowsemantics.md"

tags:
  - interpreter
  - languages
  - pipeline

---

This assignment completes your pipeline: a tree-walking evaluator that runs programs in your language, with real scopes, real types, a REPL, and semantic documentation. This is the component your team project extends — the semantics documentation is as important a deliverable as the code. Build in the scaffolded order below; each part depends on the previous.

---

## Part 1: AST Node Dataclasses (25 points)

### Why Dataclasses?

Python `dataclass` gives you `__init__`, `__repr__`, and optional `__eq__` for free. Clean node types make the evaluator's isinstance dispatch readable, and `__repr__` makes test failures self-documenting.

### Step 1a: Define All Node Types

Define the following node types as `@dataclass` classes. Every field must have a type annotation and a one-line comment explaining its meaning. Store source positions (line, col) on nodes where they aid error reporting — at minimum on `Var`, `BinOp`, `UnaryOp`, `Let`, and `Assign`.

```python
from dataclasses import dataclass, field
from typing import Any, List, Optional

@dataclass
class Num:
    value: float          # the numeric value (already parsed)
    line: int = 0

@dataclass
class Str:
    value: str            # decoded string value (escapes resolved)
    line: int = 0

@dataclass
class BoolLit:
    value: bool           # True or False
    line: int = 0

@dataclass
class Var:
    name: str             # variable name as it appears in source
    line: int = 0

@dataclass
class BinOp:
    op: str               # one of: + - * / < <= > >= == !=
    left: Any
    right: Any
    line: int = 0

@dataclass
class UnaryOp:
    op: str               # one of: - not
    operand: Any
    line: int = 0

@dataclass
class LogicOp:
    op: str               # "and" or "or" — separate from BinOp for short-circuit
    left: Any
    right: Any
    line: int = 0

@dataclass
class Let:
    name: str             # variable name being defined
    value: Any            # initializer expression
    line: int = 0

@dataclass
class Assign:
    name: str             # variable name being updated (must already exist)
    value: Any
    line: int = 0

@dataclass
class Print:
    value: Any            # expression to evaluate and print

@dataclass
class Block:
    stmts: List[Any] = field(default_factory=list)

@dataclass
class If:
    condition: Any
    then_branch: Any      # always a Block
    else_branch: Any      # Block, If, or None

@dataclass
class While:
    condition: Any
    body: Any             # always a Block

@dataclass
class Break:
    line: int = 0

@dataclass
class Continue:
    line: int = 0

@dataclass
class Program:
    stmts: List[Any] = field(default_factory=list)
```

### Step 1b: Visitor Dispatch

Write an `Interpreter` class with one `eval_node(node)` method that dispatches on node type using `isinstance`. Every node type listed above must have a corresponding branch. An `else` branch raises `InterpreterError("Unknown node type: ...")`.

**Worked example:** Before implementing any evaluation logic, verify that `eval_node(Num(42))` raises `NotImplementedError` (or returns a placeholder), and that every node type reaches a branch rather than the else.

---

## Part 2: Tree-Walking Evaluator (35 points)

### Step 2a: Expression Evaluation

Implement evaluation for expression nodes. Return Python values: numbers as `float` or `int`, strings as `str`, booleans as `bool`.

**`Num`** — return `node.value`.

**`Str`** — return `node.value` (already decoded).

**`BoolLit`** — return `node.value`.

**`Var`** — call `env.lookup(node.name)`, raising a `LangNameError` if not found. Include the variable name and source line in the error.

**`UnaryOp("-")`** — evaluate the operand; if it is not a number, raise `LangTypeError("unary minus requires a number, got <type>")`.

**`BinOp`** — evaluate both operands, then apply the operator. **Type rules:**
- `+`, `-`, `*`, `/` require both operands to be numbers (raise `LangTypeError` naming both types otherwise).
- `+` on two strings concatenates (if you support this — document your decision).
- `/` by zero raises `LangZeroDivisionError` with the position.
- `<`, `<=`, `>`, `>=` require numbers; `==`, `!=` compare any same-type pair (cross-type raises or returns False — document which and why).

**Worked example — type error:**
```
let x = "hello";
let y = x + 1;      # LangTypeError at line 2, col 11: + requires numbers, got str and int
```

### Step 2b: Short-Circuit Logic

**`LogicOp("and")`** — evaluate left; if falsy, return it **without evaluating right**. Otherwise return right.

**`LogicOp("or")`** — evaluate left; if truthy, return it **without evaluating right**. Otherwise return right.

**`UnaryOp("not")`** — evaluate operand, apply truthiness, return the boolean complement.

**Truthiness policy** (document in SEMANTICS.md): What is falsy in your language? At minimum: `false`, `0`, `0.0`, and `""`. Everything else is truthy.

**Bomb test** — include this program in your test suite and verify it does not raise an error:
```
let safe = true or (1 / 0);   # right side must NOT be evaluated
```

### Step 2c: Environment and Statement Evaluation

**The `Environment` class:**

```python
class Environment:
    def __init__(self, parent=None):
        self._bindings = {}
        self._parent = parent

    def define(self, name: str, value):
        """Create a new binding in THIS scope (used by Let)."""
        self._bindings[name] = value

    def lookup(self, name: str):
        """Search this scope then parent scopes; raise LangNameError if not found."""
        if name in self._bindings:
            return self._bindings[name]
        if self._parent:
            return self._parent.lookup(name)
        raise LangNameError(f"Undefined variable '{name}'")

    def assign(self, name: str, value):
        """Update an existing binding wherever it lives; raise LangNameError if not found."""
        if name in self._bindings:
            self._bindings[name] = value
        elif self._parent:
            self._parent.assign(name, value)
        else:
            raise LangNameError(f"Cannot assign to undefined variable '{name}'")
```

**Verify the shadowing program produces `51` then `2`:**
```
let x = 2;
{
    let x = 51;
    print x;       # prints 51
}
print x;           # prints 2
```

**Statements:**

**`Let`** — evaluate the initializer, call `env.define(node.name, value)`.

**`Assign`** — evaluate the value, call `env.assign(node.name, value)`. This updates the binding wherever it lives — it does *not* create a new one.

**`Print`** — evaluate the expression and print the result to stdout. Booleans print as `true`/`false`, not `True`/`False`.

**`Block`** — create a child environment `child_env = Environment(parent=env)`, then evaluate each statement in the block using `child_env`. When the block finishes, discard `child_env` (it goes out of scope naturally).

**`If`** — evaluate the condition; convert to boolean via your truthiness rule; execute `then_branch` if truthy, `else_branch` (if present) otherwise.

**`While`** — evaluate condition, execute body while truthy. Document whether loop body creates a per-iteration scope (both choices are valid — pick one and write it in SEMANTICS.md). Catch `BreakSignal` to exit early; catch `ContinueSignal` to restart the loop.

### Step 2d: Break and Continue

Implement `break` and `continue` via signal exception classes:

```python
class BreakSignal(Exception): pass
class ContinueSignal(Exception): pass
```

`Break` and `Continue` nodes raise these signals. The `While` evaluator catches them. Any `BreakSignal` or `ContinueSignal` that escapes a `While` body and reaches the top level is caught by the error handler (step below) and reported as a `LangRuntimeError("break outside loop")` or similar.

---

## Part 3: REPL and File Runner (20 points)

### Step 3a: File Runner

`python mylang.py program.ml` should:
1. Read the source file.
2. Lex it, catching `LexError` → print `"Lexical error at line L, col C: <message>"` and exit.
3. Parse it, catching `ParseError` → print `"Syntax error at line L, col C: expected X, found Y"` and exit.
4. Evaluate it, catching `LangNameError`, `LangTypeError`, `LangZeroDivisionError`, and `LangRuntimeError` → print `"Runtime error at line L: <message>"` and exit.

The stage label (`Lexical error`, `Syntax error`, `Runtime error`) must appear in every message.

### Step 3b: REPL

`python mylang.py` with no arguments launches the REPL. Requirements:
- Display a `>> ` prompt.
- Read one line (or detect a multi-line statement and keep prompting with `.. ` — document your choice).
- Maintain a single `Environment` across all REPL inputs.
- On a successfully evaluated expression-statement, print the value.
- On any error (lexical, syntax, or runtime), print the error and return to the prompt without crashing.
- `quit` or `exit` (or EOF/Ctrl-D) exits cleanly.

**REPL session transcript to include in your submission:**

```
>> let x = 10;
>> x = x + 5;
>> print x;
15
>> let y = x / 0;
Runtime error at line 1: division by zero
>> print undefined_var;
Runtime error at line 1: Undefined variable 'undefined_var'
>> @bad token
Lexical error at line 1, col 1: unexpected character '@'
>> print x;
15
>> quit
```

---

## Part 4: Error Messages with Stage Identification (20 points)

### Step 4a: Error Class Hierarchy

Define a hierarchy of language-specific exceptions:

```python
class LangError(Exception):
    def __init__(self, message, line=0, col=0):
        self.message = message
        self.line = line
        self.col = col
    def __str__(self):
        return f"line {self.line}, col {self.col}: {self.message}"

class LangNameError(LangError): pass
class LangTypeError(LangError): pass
class LangZeroDivisionError(LangError): pass
class LangRuntimeError(LangError): pass
```

Every `raise` in the evaluator must use one of these classes with a meaningful message that names the variables, types, or operators involved.

### Step 4b: SEMANTICS.md

Write `SEMANTICS.md` with one section per topic below. Each section must include: a statement of the rule, a code example in your language, and the expected output (or error message).

1. **Truthiness** — what values are falsy? What are truthy? Show a `while` loop that relies on numeric truthiness.
2. **Division by zero** — what error is raised? What stage identifies it? Show the exact error message format.
3. **Scoping and shadowing** — where does `let` define? Where does bare assignment update? Show the shadowing program and its output.
4. **Loop-variable persistence** — does the loop variable remain in scope after the loop body? Show a program whose output depends on this decision.
5. **Assignment vs. definition** — what error does assigning an undefined variable produce? Show it.
6. **Type strictness** — can you add an int to a float? A string to a number? Show both cases and their outcomes.
7. **String concatenation** — is `"a" + "b"` legal? What about `"a" + 1`? State the rule and show examples.

### Step 4c: Differential Programs

Five programs are provided whose outputs depend on your semantics decisions. Run each, record the output, and confirm it matches your SEMANTICS.md documentation. If it does not match, fix either the code or the documentation — they must agree.

---

## Deliverables

Submit a ZIP containing:
- `interpreter.py` — the evaluator, Environment class, and error hierarchy (importing `lexer.py` and `parser.py` unchanged; note any fixes)
- `SEMANTICS.md` — the language semantics document
- `test_interpreter.py` — test suite with the shadowing program, the bomb test, all error-class tests, and the differential programs
- `repl_transcript.txt` — the REPL session showing each error class and recovery
- `readme.md` — approximately one page connecting the interpreter to the pipeline and the team project

Ensure reproducibility by listing your Python version.

---

## Grading Breakdown

| Component | Points |
|-----------|--------|
| Part 1: AST Node Dataclasses | 25 |
| Part 2: Tree-Walking Evaluator | 35 |
| Part 3: REPL and File Runner | 20 |
| Part 4: Error Messages and SEMANTICS.md | 20 |
| **Total** | **100** |

---

## Reflection Prompts

- Which semantics decision did you change after testing revealed a consequence you had not foreseen?
- Point to the exact line in your `Environment` class that makes your language statically (lexically) scoped rather than dynamically scoped.
- The `BreakSignal`/`ContinueSignal` pattern uses exceptions for control flow — a technique the course calls "signal exceptions." What property of exceptions makes them well suited for this, and what would you use instead if exceptions were not available?
- If collaboration with a buddy was permitted, did you work with a buddy on this assignment? If so, who? If not, do you certify that this submission represents your own original work? Please identify any and all portions of your submission that were not originally written by you.
- Approximately how many hours it took you to finish this assignment (I will not judge you for this at all — I am simply using it to gauge if the assignments are too easy or hard)?
