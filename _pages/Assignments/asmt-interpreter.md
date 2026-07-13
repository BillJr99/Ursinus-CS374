---
layout: assignment
permalink: /Assignments/Interpreter
title: "CS374: Principles of Programming Languages - The Interpreter"

info:
  coursenum: CS374
  purpose: "To complete your language pipeline with a tree-walking evaluator — nested scopes, strong dynamic typing, a REPL, and a precise semantics document — the capstone component your team project extends."
  tilt:
    task: "Define AST node dataclasses with visitor dispatch, build a tree-walking evaluator with environments and short-circuit logic, add a REPL and file runner, and complete Part 4 in your choice of direction — Error Messages and SEMANTICS.md, or Static Type Checking, or the Intcode VM."
    criteria: "Assessed on a correct evaluator with well-behaved scopes and short-circuit logic, a recoverable REPL and file runner, and a complete Part 4 in your chosen direction — Error Messages and SEMANTICS.md, or Static Type Checking, or the Intcode VM — weighted 25/35/20/20 across the four parts; the Part 4 rubric applies equivalently to every direction. See the rubric below for the full breakdown."
  points: 100
  goals:
    - To define a complete set of AST node dataclasses covering every language construct
    - To implement a tree-walking evaluator over the AST with strong dynamic typing
    - To implement nested scopes with an Environment class distinguishing definition from assignment
    - To verify semantic invariants (determinism, scope restoration, short-circuit non-evaluation) with property-based testing using Hypothesis and a generated program space
    - To build a REPL and file-runner with stage-identified error messages
    - To make the language's semantics precise — by documenting the dynamic rules exhaustively in SEMANTICS.md, by enforcing them statically with a Hindley-Milner-style type checker, or by implementing and precisely specifying a contrasting opcode-based execution model (the Intcode VM), in your choice of direction
  rubric:
    - weight: 25
      description: "AST Node Dataclasses (Goal 1: define a complete set of AST node dataclasses covering every language construct)"
      preemerging: Fewer than half the required node types are defined, or the dataclass structure does not match the parser's output
      beginning: All required node types exist but several are missing fields, have incorrect types, or lack documented field meanings
      progressing: All required node types are defined with correct fields and a useful __repr__, but source-position information is missing from most nodes
      proficient: All required node types are defined as dataclasses with every field documented and source-position (line/col) stored where it aids error reporting — demonstrating Goal 1 by providing a complete, parser-consistent node hierarchy with a visitor dispatch table or isinstance chain ready for the evaluator
    - weight: 35
      description: "Tree-Walking Evaluator (Goals 2–3: implement a tree-walking evaluator with strong dynamic typing and an Environment class for nested scopes)"
      preemerging: The evaluator fails to run or fails most provided programs due to major structural errors such as missing cases or infinite loops
      beginning: The evaluator runs but fails on several programs — e.g., nested scopes leak, type errors are not raised, or short-circuit logic evaluates both branches always
      progressing: The evaluator passes the provided programs but fails on hidden edge cases — e.g., a scope is not discarded after a block, or division by zero crashes Python instead of raising a language error
      proficient: A correct evaluator passes all provided and hidden programs — nested scopes behave per documented semantics, type errors name both operand types, short-circuit logic is verified by a non-evaluation test, and all runtime errors are raised at the language level with stage and position; the required Hypothesis invariant tests (Step 2e — determinism, scope restoration, short-circuit non-evaluation, and at least one more) pass over the generated program space, with one shrunk counterexample reported or a reasoned all-clear — demonstrating that Goals 2 and 3 are met
    - weight: 20
      description: "REPL and File Runner (Goal 4: build a REPL and file-runner with stage-identified error messages)"
      preemerging: Neither the REPL nor the file runner exists, or both crash on the first error
      beginning: One of the two exists but dies on any error, or the REPL does not maintain state between inputs
      progressing: Both exist and survive most errors, but one error class (e.g., type errors) still crashes the REPL, or the file runner does not identify the stage in its error messages
      proficient: Both the REPL and file runner work — the REPL maintains a persistent environment across inputs and recovers from all error classes, the file runner identifies stage and position in every error message, and a transcript demonstrates each error class and recovery — demonstrating Goal 4 end-to-end
    - weight: 20
      description: "Part 4, in the chosen direction — Staged Errors with SEMANTICS.md, Static Type Checking, or the Intcode VM with a precise operational semantics (Goal 5: make the language's semantics precise — by documenting the dynamic rules exhaustively, enforcing them statically before evaluation, or specifying and implementing a contrasting opcode-based execution model)"
      preemerging: "Dynamic-errors direction: errors are unhandled Python exceptions with no stage identification. Typing direction: no checker exists, or unification fails on basic cases. Intcode direction: the VM fails the Day 2 sample, or opcodes are not documented as transition rules"
      beginning: "Dynamic-errors direction: errors are caught but the stage (lexical vs. syntax vs. runtime) is not identified, or the position is absent. Typing direction: unification handles trivial cases but the checker fails on function application or let, or type errors carry no position. Intcode direction: the VM runs the Day 2 sample but parameter modes are wrong or INTCODE.md is incomplete"
      progressing: "Dynamic-errors direction: most error classes are caught with stage and position, but one class (e.g., type errors) is missing position or stage identification. Typing direction: the checker infers correct types for most programs with a defect in one case (e.g., a missing occurs check, or an incorrect constraint for one operator), and most type errors are positioned. Intcode direction: the VM passes the Day 2 and Day 5 checkpoints and most opcodes have transition rules, but position/immediate mode has a defect or the differential test against the tree-walker is missing"
      proficient: "Dynamic-errors direction: every error class — LexError, ParseError, NameError, TypeError, ZeroDivisionError — is caught at the appropriate stage and reported with a message of the form \"Stage error at line L, col C: description\"; SEMANTICS.md includes one example program that triggers each error class with the expected message shown. Typing direction: unification (with the occurs check) and Algorithm-W-style inference are correct for every construct the checker covers; the checker runs as its own stage before evaluation; every type error names both conflicting types with line and context; and TYPES.md states the typing rule per construct with one accepted and one rejected program each. Intcode direction: the VM passes every cited AoC checkpoint, illegal opcodes raise staged positioned errors, INTCODE.md gives a precise transition rule for every opcode and parameter mode, and the required differential test shows the VM and tree-walker agree on shared arithmetic — any direction demonstrating Goal 5 by providing a complete semantics reference"
  readings:
    - rtitle: "Tree-Walking Interpretation Activity"
      rlink: "https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374/gh-pages/_pages/Activities/liascript-interpretation.md"
    - rtitle: "Environments Activity"
      rlink: "https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374/gh-pages/_pages/Activities/liascript-environments.md"
    - rtitle: "Control Flow Semantics Activity"
      rlink: "https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374/gh-pages/_pages/Activities/liascript-controlflowsemantics.md"
    - rtitle: "Property-Based Testing Your Language with Hypothesis (Tutorial)"
      rlink: "https://www.billmongan.com/Ursinus-CS374-Fall2026/Tutorials/PropertyBasedTesting"
    - rtitle: "Advent of Code 2019, Day 2 — Intcode (Part 4 Intcode direction)"
      rlink: "https://adventofcode.com/2019/day/2"

tags:
  - interpreter
  - languages
  - pipeline
  - property-based-testing
  - virtual-machine

---

This assignment completes your pipeline: a tree-walking evaluator that runs programs in your language, with real scopes, real types, a REPL, and semantic documentation. This is the component your team project extends — the semantics documentation is as important a deliverable as the code. Build in the scaffolded order below; each part depends on the previous.

---

## Getting Started

### Environment and Setup

You need Python 3.10+ plus your completed Lexer and Parser. Copy `lexer.py`, `parser.py`, `ast_nodes.py`, and `token_spec.json` into the project directory and import them unchanged (note any bug fixes in your readme). Create the deliverable files up front:

```
interpreter.py        # evaluator, Environment, error hierarchy
mylang.py             # entry point: file runner and REPL (Part 3)
SEMANTICS.md          # the semantics document (Part 4)
test_interpreter.py   # the test suite
```

Confirm the pipeline is connected before evaluating anything: `python -c "from parser import parse; print(parse('print 1 + 2;'))"` should print a `Program` tree.

**Reference implementation policy.** A Reference Parser and AST are released the day this assignment goes out. You may import them in place of your own `parser.py` and `ast_nodes.py` by declaring one line in your readme ("This project uses the reference parser and AST"). Your Parser assignment grade stands on its own, and using the reference carries no penalty here — the point of this assignment is the evaluator, and everyone deserves a solid tree to walk.

### Your First 30 Minutes

Do exactly what Step 1b's worked example asks — build the dispatch skeleton before any evaluation logic. Copy the node dataclasses from Step 1a (reconciling them with your parser's existing nodes), then write the `Interpreter` class with an `eval_node` that has one branch per node type, each raising `NotImplementedError`:

```python
interp = Interpreter()
try:
    interp.eval_node(Num(42))
except NotImplementedError:
    print("dispatch reached the Num branch")   # good — the wiring works
```

Then fill in just the `Num` branch (`return node.value`) and the `Print` branch, and run `print 42;` end to end through your lexer, parser, and evaluator. Seeing one statement flow through the entire pipeline on day one turns the rest of Part 2 into filling in branches one at a time.

### Suggested Pacing

This assignment is handed out on Tuesday of week 9 (Oct 27) and due on Tuesday of week 11 (Nov 10). It is the longest assignment in the pipeline, and Part 2 is its steepest section — the schedule below climbs it in small steps rather than one leap:

| Checkpoint | You should have |
|------------|----------------|
| Week 9 (Tue Oct 27) — assigned | Part 1 complete: all node dataclasses and the dispatch skeleton (Steps 1a–1b) |
| Week 9 (Thu Oct 29) | Expression evaluation and short-circuit logic with the bomb test passing (Steps 2a–2b) |
| Week 10 (Tue Nov 3) | `Environment` and statement evaluation; shadowing program prints `51` then `2` (Step 2c) |
| Week 10 (Thu Nov 5) | Break/continue signals and the file runner with staged errors (Step 2d, Step 3a) |
| Weekend | REPL with persistent environment and recovery; error hierarchy in place (Step 3b, Step 4a) |
| Week 11 (Tue Nov 10) — due | `SEMANTICS.md`, differential programs, REPL transcript; ZIP submitted (Steps 4b–4c) |

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

### Step 2e: Property-Based Invariants with Hypothesis

In the Parser assignment you used **[Hypothesis](https://hypothesis.readthedocs.io/)** to check a *syntactic* law (round-trip). Here you check *semantic* laws — properties that must hold for **every** program, not just the ones in your test file. These invariants are where scoping and short-circuit bugs hide, because they only surface on inputs you did not think to write. This is a required step; reuse the recursive AST generator you built for the parser (restrict it to the expression and small-statement nodes your evaluator supports).

Encode **at least three** of the following invariants as `@given` tests (the first two are required; pick at least one more):

1. **Determinism.** Evaluating the same AST twice in fresh environments produces identical output and result. `eval(tree)` has no hidden state that leaks between runs.
2. **Scope restoration.** For any generated expression `e` and a fresh variable name `v` not free in `e`, evaluating a block that binds `v` with `let`, then evaluates `e`, leaves the outer environment without `v` afterward — the inner `let` does not leak. (Generate `e`; wrap it; assert the outer env is unchanged.)
3. **Short-circuit non-evaluation.** Give `and`/`or` a right operand with an observable side effect (e.g., a call to a tool that appends to a list, or a subexpression that divides by zero). Assert that when the left operand determines the result (`false and X`, `true or X`), the right operand's side effect **never** fires — Hypothesis will hunt for the operand shape that sneaks past your short-circuit.
4. **Arithmetic agreement (metamorphic).** For generated integer-only expressions using `+ - *`, your evaluator's result equals Python's evaluation of the same expression — a cheap oracle that catches precedence/associativity bugs that slipped through the parser into evaluation.

When a property fails, Hypothesis shrinks to the minimal offending program. In your `readme.md`, report one invariant that caught a real bug (or a reasoned all-clear, with the three properties and the generator shown).

> This step also feeds the Team Language Project: the same three invariants, generalized to your team's language, become the core of its property-based test suite — so write them to be reusable.

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

## Part 4: Making the Semantics Precise (20 points) — Choose Your Direction

Parts 1–3 give your language a working evaluator. Part 4 makes its semantics *precise*, in your choice of **direction** — one Part 4, one deliverable, the same 20-point rubric row applied equivalently:

- **Staged dynamic errors and SEMANTICS.md (the core direction).** Build the language-level error hierarchy and document every semantic rule, as scaffolded in Steps 4a–4c below.
- **Static type checking (Hindley-Milner-style inference).** Instead of documenting what happens when a type error reaches the evaluator, catch it *before evaluation ever begins*, the way Haskell, OCaml, and Rust do. This direction substitutes Steps 4b and 4c (SEMANTICS.md and the differential programs) with the type checker described in the **[typing direction](#part-4-direction-static-type-checking-hindley-milner-style-inference)** section; Step 4a's error hierarchy is still required, since lexical, syntax, and name errors still need staged reporting, and your file runner gains a fourth stage label (`Type error`). The total remains 100 points.
- **A contrasting execution model — the Intcode VM.** Your tree-walker interprets an AST directly. A *virtual machine* instead executes a flat list of numeric opcodes — the model behind CPython's bytecode, the JVM, and WebAssembly. In this direction you implement the **[Advent of Code 2019 Intcode](https://adventofcode.com/2019/day/2)** machine, whose operational semantics is small enough to specify completely yet rich enough to be Turing-capable, and you make that semantics *precise* by writing each opcode as a state-transition rule. This direction substitutes Steps 4b and 4c with the **[Intcode direction](#part-4-direction-a-contrasting-execution-model-the-intcode-vm)** section; Step 4a's error hierarchy is still required (malformed programs and illegal opcodes are staged errors). The self-checking AoC inputs are your oracle, and a required differential test pins your VM's arithmetic against your tree-walker's on shared operations.

Whichever direction you choose, the underlying goal is the same: for every construct in your language (or VM), there is exactly one written answer to "what does this mean, and what happens when it is misused?" — and your implementation agrees with it.

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

## Part 4 Direction: Static Type Checking (Hindley-Milner-Style Inference)

This direction replaces Steps 4b–4c with a static type checker that runs as its own pipeline stage — after parsing, before evaluation — and rejects ill-typed programs without running them. It is the same machinery (unification and Algorithm-W-style inference) that lets Haskell, OCaml, and Rust deduce types without annotations, scoped here to your language's constructs.

### Background

A **type** is a type variable `α, β, ...` (unknown, to be solved), a type constant (`Num`, `Bool`, `Str`), or — if your checker covers functions — a function type `τ₁ → τ₂`. A **substitution** maps type variables to types. **Unification** of two types finds the most general substitution that makes them equal, or fails — and that failure *is* the type error. The inference algorithm walks the AST, generating fresh type variables constrained by each node's structure and unifying to solve.

### T.1 — Type terms, substitution, and unification (`types.py`)

Define frozen dataclasses `TVar(name)`, `TCon(name)` (and `TFun(param, ret)` if covering functions), with `apply(subst, typ)` and `free_vars(typ)` helpers. Implement `unify(t1, t2, subst) -> subst`:

1. Apply the current substitution to both types; if they are now identical, return the substitution unchanged.
2. If one is a type variable `α` not occurring in the other, extend the substitution with `{α: other}`. The **occurs check** — refusing to bind `α` to a type containing `α` — is what prevents infinite types; raise a `LangTypeError` naming both types if it fires.
3. Recurse componentwise on matching constructors; otherwise raise a `LangTypeError` naming both conflicting types.

Test at minimum: `unify(TVar("a"), TNum)` binds `a`; unifying `TNum` with `TBool` raises; and an occurs-check case raises.

### T.2 — Inference over your AST (`typecheck.py`)

Implement `infer(node, type_env, subst) -> (subst, type)` with one case per node type your evaluator handles: literals return their constant type; `Var` looks up the type environment (undefined names remain `LangNameError`s); arithmetic operators unify both operands with `Num` and return `Num`; comparisons return `Bool`; `LogicOp` and `not` unify with `Bool`; `If` and `While` conditions must be `Bool` (note that this is *stricter* than your dynamic truthiness rule — see the reflection prompt); `Let` extends the type environment; `Assign` unifies the new value's type with the variable's existing type; `Block` checks its statements in a child type environment mirroring your `Environment` scoping. Thread the substitution through every case.

Wire it into `mylang.py` as a stage: `python mylang.py --typed program.ml` (or make it the default — document your choice) lexes, parses, **type-checks**, and only then evaluates. The stage label `Type error` joins the staged-error format of Part 3: `Type error at line L: <message>`.

### T.3 — Positioned type errors

Every type error must name both conflicting types, cite the source line, and give a short context, in the spirit of:

```
Type error at line 7: condition of 'if' must be Bool, got Num
Type error at line 12: '+' requires Num operands, got Str and Num
Type error at line 5: cannot unify Num with Bool (from assignment to 'result')
```

### T.4 — TYPES.md and test programs

In place of SEMANTICS.md, write `TYPES.md`: one section per construct stating its typing rule in prose (or inference-rule notation), with one program the checker accepts and one it rejects, showing the exact error message. Include at least five test programs total: three that the checker rejects with distinct positioned errors, and two that pass the checker and then run correctly — demonstrating that well-typed programs still evaluate as before.

**Depth (part of "proficient"):** if your language grows function values in the team project — or if you simply want the full Milner experience — implement **let-polymorphism**: generalize a let-bound name's type over the type variables not free in the environment, and instantiate fresh copies at each use, so a polymorphic identity function can be applied to both a `Num` and a `Bool` in the same scope. Self-application (`f(f)`) must still be rejected — no finite type satisfies it, and your occurs check is what says so.

---

## Part 4 Direction: A Contrasting Execution Model — the Intcode VM
{: #part-4-direction-a-contrasting-execution-model-the-intcode-vm}

### Background

A tree-walker is one way to run a program; a **virtual machine** is another. Instead of recursing over an AST, a VM holds the program as a flat array of integers and steps a program counter through them, decoding one instruction at a time. This is the model underneath CPython's bytecode, the JVM, and WebAssembly — and Advent of Code 2019's **Intcode** is the smallest complete instance of it worth studying. Choosing this direction means you have now built the two dominant execution models in the same course and can say precisely how they differ.

Intcode's operational semantics is small enough to write down completely, which is exactly what makes it a legitimate "make the semantics precise" direction: every opcode is one state-transition rule over the machine state `(memory, pc, input, output, relative_base)`.

### I.1 — Precise operational semantics (`INTCODE.md`)

Before writing code, write `INTCODE.md`: for **each** opcode, state its rule as a transition on the machine state. For example, opcode 1 (add):

> `add`: with parameters `a, b, c`, set `mem[c] ← value(a) + value(b)`, then `pc ← pc + 4`.

Cover opcodes `1` (add), `2` (multiply), `3` (input), `4` (output), `5` (jump-if-true), `6` (jump-if-false), `7` (less-than), `8` (equals), and `99` (halt), plus the **parameter modes** (0 = position, 1 = immediate, and — for the full machine — 2 = relative, with opcode `9` adjusting the relative base). State what an unknown opcode does: it is a staged error (`LangRuntimeError`), not a crash.

### I.2 — The VM (`intcode.py`)

Implement `run(program, inputs) -> outputs` as an opcode dispatch loop. Decode each instruction as `opcode = instr % 100` and the per-parameter modes from the higher digits. Structure the dispatch so that adding an opcode is a localized change (a dict from opcode to a small handler, or a match statement) — the same "one construct, one place" discipline as your tree-walker's visitor. Illegal opcodes and out-of-range addresses raise your Part 4a error classes with a position (the `pc` at fault).

### I.3 — Self-checking against the AoC oracle

Intcode is self-validating: the puzzle inputs come with known answers. Include at least these checkpoints, each with the exact expected output in your `readme.md`:
- The Day 2 sample programs (e.g., `1,9,10,3,2,3,11,0,99,30,40,50` halts with `3500` in position 0).
- A Day 5 program exercising input, output, immediate mode, and a jump/comparison (e.g., "is the input equal to 8?").
- If you implement relative mode + opcode 9, the Day 9 quine (`104,1125899906842624,99`) which must output its own large constant.

### I.4 — Differential test against your tree-walker (required)

The two execution models must agree where they overlap. Write a differential test: for a handful of integer arithmetic expressions, evaluate each **both** with your Part 2 tree-walker and with an equivalent hand-assembled Intcode program, and assert the results match. In your readme, name one thing the VM makes easy that the tree-walker makes hard (or vice versa) — e.g., self-modifying code, or explicit control over evaluation order.

> **Scope note:** this direction is warm-up-scale by design — the VM is a couple hundred lines and its correctness is externally checkable, so your effort goes into the *precise semantics* and the *model comparison*, which is what the 20-point Part 4 rubric rewards.

---

## Deliverables

Submit a ZIP containing:
- `interpreter.py` — the evaluator, Environment class, and error hierarchy (importing `lexer.py` and `parser.py` unchanged; note any fixes)
- `mylang.py` — the entry point: file runner and REPL (Part 3)
- `SEMANTICS.md` — the language semantics document
- `test_interpreter.py` — test suite with the shadowing program, the bomb test, all error-class tests, and the differential programs
- `repl_transcript.txt` — the REPL session showing each error class and recovery
- `readme.md` — approximately one page connecting the interpreter to the pipeline and the team project

**Typing direction:** substitute `types.py`, `typecheck.py`, and `TYPES.md` (with its accepted/rejected test programs) for `SEMANTICS.md` and the differential programs; everything else on the list is unchanged, and the REPL transcript additionally demonstrates one positioned type error.

**Intcode direction:** substitute `intcode.py` and `INTCODE.md` (with the per-opcode transition rules) for `SEMANTICS.md` and the differential programs; add the AoC checkpoint outputs and the tree-walker-vs-VM differential test to `test_interpreter.py`; everything else on the list is unchanged.

Every direction includes the required Step 2e Hypothesis invariant tests in `test_interpreter.py`.

Ensure reproducibility by listing your Python version.

---

## Grading Breakdown

| Component | Points |
|-----------|--------|
| Part 1: AST Node Dataclasses | 25 |
| Part 2: Tree-Walking Evaluator | 35 |
| Part 3: REPL and File Runner | 20 |
| Part 4 (chosen direction): Error Messages and SEMANTICS.md, or Static Type Checking, or the Intcode VM | 20 |
| **Total** | **100** |

---

## Reflection Prompts

- Which semantics decision did you change after testing revealed a consequence you had not foreseen?
- Point to the exact line in your `Environment` class that makes your language statically (lexically) scoped rather than dynamically scoped.
- Typing direction only: your dynamic truthiness rule accepts `while 1 { ... }`, but your type checker demands a `Bool` condition. Where else did the static discipline reject a program your evaluator would have happily run, and which behavior do you consider correct for your language?
- The `BreakSignal`/`ContinueSignal` pattern uses exceptions for control flow — a technique the course calls "signal exceptions." What property of exceptions makes them well suited for this, and what would you use instead if exceptions were not available?
- If collaboration with a buddy was permitted, did you work with a buddy on this assignment? If so, who? If not, do you certify that this submission represents your own original work? Please identify any and all portions of your submission that were not originally written by you.
- AI disclosure: list any generative-AI tools you used, for what, and how you verified the results (or state 'none').
- Approximately how many hours it took you to finish this assignment (I will not judge you for this at all — I am simply using it to gauge if the assignments are too easy or hard)?
