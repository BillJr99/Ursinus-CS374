---
layout: assignment
permalink: /Assignments/Interpreter
title: "CS374: Principles of Programming Languages - The Interpreter"

info:
  coursenum: CS374
  purpose: "To complete your language pipeline with a tree-walking evaluator that has nested scopes, strong dynamic typing, a small static type checker, a REPL, and a precise semantics document.  This is the capstone component your team project extends."
  tilt:
    task: "Define AST node dataclasses with visitor dispatch, build a tree-walking evaluator with environments and short-circuit logic, add a REPL and file runner, implement a small static type checker over annotated declarations, and complete Part 5 in your choice of direction: Error Messages and SEMANTICS.md, or full Hindley-Milner Type Inference, or the Intcode VM."
    criteria: "I grade this on a correct evaluator with well-behaved scopes and short-circuit logic, a recoverable REPL and file runner, a working small static type checker that runs as its own stage before evaluation, and a complete Part 5 in your chosen direction (Error Messages and SEMANTICS.md, or full Hindley-Milner Type Inference, or the Intcode VM).  The Part 5 rubric applies equivalently to every direction.  See the rubric below for the full breakdown."
  points: 100
  goals:
    - To define a complete set of AST node dataclasses covering every language construct
    - To implement a tree-walking evaluator over the AST with strong dynamic typing
    - To implement nested scopes with an Environment class distinguishing definition from assignment
    - To verify semantic invariants (determinism, scope restoration, short-circuit non-evaluation) with property-based testing using Hypothesis and a generated program space
    - To build a REPL and file-runner with stage-identified error messages
    - To implement a small static type checker over annotated declarations (literal, variable, operator, and call-site checks) that runs as its own pipeline stage between parsing and evaluation
    - To make the language's semantics precise, by documenting the dynamic rules exhaustively in SEMANTICS.md, by extending the required checker to full Hindley-Milner type inference, or by implementing and precisely specifying a contrasting opcode-based execution model (the Intcode VM), in your choice of direction
  rubric:
    - weight: 10
      description: "Part 0: Before You Start - Evaluation and Invariants"
      preemerging: No trace is attempted and no invariants are stated
      beginning: The program is traced but the environment is not shown at each step, or no invariant is stated
      progressing: The trace shows the environment at every step, but the truthiness decision is left open, or only one invariant is stated, or an invariant is stated so vaguely that no program could test it
      proficient: The five-line program is traced by hand with the environment's contents and the value produced shown at every step; the truthiness policy is decided and written down in one sentence with the case that forced the decision; and two invariants are stated precisely enough to be tested, each naming the property and the class of programs it should hold over
    - weight: 22
      description: "AST Node Dataclasses (Goal 1: define a complete set of AST node dataclasses covering every language construct)"
      preemerging: Fewer than half the required node types are defined, or the dataclass structure does not match the parser's output
      beginning: All required node types exist but several are missing fields, have incorrect types, or lack documented field meanings
      progressing: All required node types are defined with correct fields and a useful __repr__, but source-position information is missing from most nodes
      proficient: All required node types are defined as dataclasses with every field documented and source-position (line/col) stored where it aids error reporting, meeting Goal 1 with a complete, parser-consistent node hierarchy and a visitor dispatch table or isinstance chain ready for the evaluator
    - weight: 28
      description: "Tree-Walking Evaluator (Goals 2-3: implement a tree-walking evaluator with strong dynamic typing and an Environment class for nested scopes)"
      preemerging: The evaluator fails to run or fails most provided programs because of major structural errors such as missing cases or infinite loops
      beginning: The evaluator runs but fails on several programs, e.g., nested scopes leak, type errors are not raised, or short-circuit logic always evaluates both branches
      progressing: The evaluator passes the provided programs but fails on hidden edge cases, e.g., a scope is not discarded after a block, or division by zero crashes Python instead of raising a language error
      proficient: A correct evaluator passes all provided and hidden programs; nested scopes behave per documented semantics, type errors name both operand types, short-circuit logic is verified by a non-evaluation test, and all runtime errors are raised at the language level with stage and position; the required Hypothesis invariant tests (Step 2e; determinism, scope restoration, short-circuit non-evaluation, and at least one more) pass over the generated program space, with one shrunk counterexample reported or a reasoned all-clear; and the control-flow theory questions are answered in the readme with the bomb test used as evidence, showing that Goals 2 and 3 are met
    - weight: 13
      description: "REPL and File Runner (Goal 4: build a REPL and file-runner with stage-identified error messages)"
      preemerging: Neither the REPL nor the file runner exists, or both crash on the first error
      beginning: One of the two exists but dies on any error, or the REPL does not maintain state between inputs
      progressing: Both exist and survive most errors, but one error class (e.g., type errors) still crashes the REPL, or the file runner does not identify the stage in its error messages
      proficient: Both the REPL and file runner work; the REPL maintains a persistent environment across inputs and recovers from all error classes, the file runner identifies stage and position in every error message, and a transcript demonstrates each error class and recovery, meeting Goal 4 end-to-end
    - weight: 13
      description: "The Small Static Type Checker (Goal 5: implement a static type checker over annotated declarations that runs as its own pipeline stage between parsing and evaluation)"
      preemerging: "No checker exists, or it never rejects an ill-typed program"
      beginning: "The checker rejects some ill-typed programs but misses operator mismatches or call-site errors, or it runs interleaved with evaluation rather than as its own stage"
      progressing: "The checker catches literal, variable, operator, and call-site errors as a separate stage, but error messages lack positions or do not name both conflicting types, or one construct (e.g., function return types) is unchecked"
      proficient: "The checker runs as its own stage between parsing and evaluation and rejects every ill-typed test program before any code runs; every type error is reported as \"Type error at line L, col C\" naming both conflicting types; annotated declarations, operator uses, call-site arity and argument types, and return types are all checked; and the file runner's staged output shows the Type stage firing before the Run stage"
    - weight: 14
      description: "Part 5, in the chosen direction: Staged Errors with SEMANTICS.md, full Hindley-Milner Type Inference, or the Intcode VM with a precise operational semantics (Goal 6: make the language's semantics precise, by documenting the dynamic rules exhaustively, extending the required checker to whole-program inference, or specifying and implementing a contrasting opcode-based execution model)"
      preemerging: "Dynamic-errors direction: errors are unhandled Python exceptions with no stage identification. Typing direction: no checker exists, or unification fails on basic cases. Intcode direction: the VM fails the Day 2 sample, or opcodes are not documented as transition rules"
      beginning: "Dynamic-errors direction: errors are caught but the stage (lexical vs. syntax vs. runtime) is not identified, or the position is absent. Typing direction: unification handles trivial cases but the checker fails on function application or let, or type errors carry no position. Intcode direction: the VM runs the Day 2 sample but parameter modes are wrong or INTCODE.md is incomplete"
      progressing: "Dynamic-errors direction: most error classes are caught with stage and position, but one class (e.g., type errors) is missing position or stage identification. Typing direction: the checker infers correct types for most programs with a defect in one case (e.g., a missing occurs check, or an incorrect constraint for one operator), and most type errors are positioned. Intcode direction: the VM passes the Day 2 and Day 5 checkpoints and most opcodes have transition rules, but position/immediate mode has a defect or the differential test against the tree-walker is missing"
      proficient: "Dynamic-errors direction: every error class (LexError, ParseError, NameError, TypeError, ZeroDivisionError) is caught at the appropriate stage and reported with a message of the form \"Stage error at line L, col C: description\"; SEMANTICS.md includes one example program that triggers each error class with the expected message shown. Typing direction: unification (with the occurs check) and Algorithm-W-style inference are correct for every construct the checker covers; the checker runs as its own stage before evaluation; every type error names both conflicting types with line and context; and TYPES.md states the typing rule per construct with one accepted and one rejected program each. Intcode direction: the VM passes every cited AoC checkpoint, illegal opcodes raise staged positioned errors, INTCODE.md gives a precise transition rule for every opcode and parameter mode, and the required differential test shows the VM and tree-walker agree on shared arithmetic. Any direction meets Goal 6 by providing a complete semantics reference"
  readings:
    - rtitle: "Tree-Walking Interpretation Activity"
      rlink: "Activities/liascript-interpretation.md"
      liapage: true
    - rtitle: "Environments Activity"
      rlink: "Activities/liascript-environments.md"
      liapage: true
    - rtitle: "Control Flow Semantics Activity"
      rlink: "Activities/liascript-controlflowsemantics.md"
      liapage: true
    - rtitle: "Property-Based Testing Your Language with Hypothesis (Tutorial)"
      rlink: "../Tutorials/PropertyBasedTesting"
    - rtitle: "Advent of Code 2019, Day 2: Intcode (Part 5 Intcode direction)"
      rlink: "https://adventofcode.com/2019/day/2"

tags:
  - interpreter
  - languages
  - pipeline
  - property-based-testing
  - virtual-machine

---

This assignment completes your pipeline with a tree-walking evaluator: a program that walks the abstract syntax tree (AST) your parser built and runs each node.  Your language gets nested scopes, type rules, a REPL (a read-eval-print loop, the interactive prompt), a static type checker, and a semantics document.  This is the component your team project extends, and the semantics document matters as much as the code does.  Build in the order below, since each part depends on the one before it.

---

## Before You Start

You need:

- Python 3.10 or newer.
- Your completed Lexer and Parser: `lexer.py`, `parser.py`, `ast_nodes.py`, and `token_spec.json`.  Import them unchanged, and note any bug fixes in your readme.
- The [Hypothesis]({{ site.baseurl }}/Tutorials/PropertyBasedTesting) library for Step 2e.
- A terminal and an editor.  If either is new to you, read the [dev environment page]({{ site.baseurl }}/Tutorials/DevEnvironment) and the [shell primer]({{ site.baseurl }}/Tutorials/ShellForLanguageDev) first.

**Reference parser and AST.**  The [reference parser and AST]({{ site.baseurl }}/files/reference/reference-parser.zip) are released with this assignment, and the zip also contains the reference lexer, so unzipping it gives you a complete pipeline up to parsing.  You may build on the reference parser or lexer instead of your own by declaring it in one line in your readme ("This submission uses the reference parser"); there is no penalty, and your Parser assignment grade stands unchanged.  The point of this assignment is the evaluator, and everyone deserves a solid tree to walk.  If you use the reference `ast_nodes.py`, its nodes already carry `line` and `col`; reconcile Step 1a against it and keep one set of node classes, because the evaluator dispatches on the exact classes the parser produces.  One thing the reference does *not* hand you is type annotations: Part 4a has you add them yourself, to the reference parser or your own, whichever you are building on.

> **Do this.**
> 1. Create a project folder named `cs374-interpreter` and copy `lexer.py`, `parser.py`, `ast_nodes.py`, and `token_spec.json` into it (or unzip the reference parser there).
> 2. Create the deliverable files up front so each part has a home: `interpreter.py` (evaluator, Environment, error hierarchy), `mylang.py` (file runner and REPL, Part 3), `typechecker.py` (Part 4), `SEMANTICS.md` (Part 5), and `test_interpreter.py`.  Rather than transcribing them, copy the [starter kit]({{ site.baseurl }}/files/starters/interpreter/) from `files/starters/interpreter/`: it holds those four Python files with every skeleton from this page already in place, and every `TODO` still yours to fill.  The seeded tests fail until you implement the branches they exercise, which is how you know they are running.
Your file runner is `mylang.py` and your programs end in `.ml`; the reference pipeline ships a `mylang.py` and `samples/*.ml` so the commands in this assignment work unchanged against it.

The starter kit matches this page: every skeleton below, including the error hierarchy, the signal classes, the `Environment`, and `mylang.py`'s `run_source`, is already in it, with every `TODO` still yours.

> 3. From inside the folder, confirm your Python version, install Hypothesis, and confirm the pipeline is connected:
>
> ```bash
> python3 --version
> pip install hypothesis
> python3 -c "from parser import parse; print(parse('print 1 + 2;'))"
> ```

> **You should see.** One line that is a `Program` tree: with the reference parser, `Program(stmts=[Print(value=BinOp(op='+', left=Num(value=1, line=1, col=7), right=Num(value=2, line=1, col=11), line=1, col=9), line=1)])`.  Your own parser's field names may differ slightly.

> **If it fails.**
> - `ModuleNotFoundError: No module named 'parser'`: you are not running from inside the project folder, or `parser.py` is not there.
> - `ImportError: cannot import name 'parse'`: your parser's entry point has a different name.  Use that name here and in `mylang.py`.
> - A `LexError` or `ParseError` on this one-line program: fix that stage first, or swap in the reference component.

> **Time budget.** Part 0 takes about thirty minutes with pencil and paper.  The rest has five parts that each depend on the one before, so it rewards steady work and punishes a final-week push harder than anything else this term.  Its window is the tightest of any programming assignment this term (see the schedule in the [syllabus]({{ site.baseurl }}/) for its dates).  Two labs of about two to three hours each, which you may do with a partner, carry pieces of it for you.  The Environments and Scope lab closes before this assignment opens, so Step 2c is largely written already.  The Type Checker Starter lab falls inside this window and finishes the core of Part 4.  Start Part 1 the day the assignment goes out, and read What You Already Have below before you write anything.

---

## Part 0: Before You Start - Evaluation and Invariants

Do this part before you write any evaluator code; you need pencil and paper and about thirty minutes.  An evaluator is a function from a tree and an environment to a value, and almost every bug in Part 2 is a disagreement between what you thought the environment held at some moment and what it actually held.  Tracing one program by hand now is how you find out which of those two you trust.

```text
let x = 2;
let y = x + 3;
{
    let x = 10;
    print x * y;
}
print x;
```

> **Do this.**
> 1. Trace this program one statement at a time.  At every step, write what the environment contains (including which scope each name lives in) and what value the step produced.  The last two `print` statements are the interesting ones; if you get `50` and then `2`, your model of block scope is already right.
> 2. Decide your truthiness policy and write it in one sentence: which values, other than `true` and `false`, may appear as the condition of an `if` or `while`, and what happens to the ones that may not.  Name the case that forced your decision.  Step 2b makes you implement whatever you decide here, so decide it deliberately rather than by accident.
> 3. State two **invariants**: properties that should hold for every program in your language, not just this one.  "Evaluating the same program twice in a fresh environment produces the same output" is one, and it is the one Step 2e has you test first.  Write each precisely enough that you could check it mechanically, and name the class of programs it ranges over.

> **Bring to class.** Your trace with the environment shown at every step, your one-sentence truthiness policy with its forcing case, and your two invariants.  Step 2e turns those invariants into Hypothesis properties over generated programs, so an invariant you state sharply now is a test you barely have to write later.

---

## Getting Started

### Where Each Step's Code Goes

Every step below names the file it changes, but it helps to see the whole map once before you start.  Files marked *scratch* are for checking your understanding; you run them and do not submit them.

| Step | File you work in | What you do there |
|---|---|---|
| 0 | paper | trace the program, decide truthiness, and state two invariants |
| 1a | `ast_nodes.py` | define or reconcile the node dataclasses |
| 1b | `interpreter.py` | write `Interpreter.eval_node` with one branch per node class |
| 1b | `evaluator_tour.py`, `check_dispatch.py` (scratch) | try dispatch, environments, and signals in miniature; confirm every class reaches its own branch |
| 2a | `interpreter.py` | add the error classes and two helpers, then fill the expression branches |
| 2b | `interpreter.py`, `test_interpreter.py` | fill `truthy`, `LogicOp`, and `not`; add the bomb test |
| 2c | `interpreter.py`, `shadow.ml`, `test_interpreter.py` | paste `Environment`, fill the statement branches, and test the shadowing program |
| 2d | your lexer and `parser.py` (only if they lack `break`), `interpreter.py`, `break.ml`, `continue.ml`, `test_interpreter.py` | add the signal classes and the `Break`, `Continue`, and `While` handling |
| 2e | `test_interpreter.py` | write the generator and at least four Hypothesis invariants |
| 3a | `mylang.py` | write `run_source` and `run_file` with staged errors |
| 3b | `mylang.py`, `repl_transcript.txt` | write `repl()` and save the session |
| 4a | your lexer, `parser.py`, `ast_nodes.py` | add the `COLON` token, read the annotation in `parse_let_stmt`, and add `type_ann` to `Let` |
| 4b | `typechecker.py`, `test_interpreter.py` | fill `TypeEnv` and `check`, and add the checker test programs |
| 4c | `typechecker.py`, `mylang.py`, `badtype.ml` | give every type error a position, and add the Type stage to `run_source` |
| 5a | `interpreter.py`, `test_interpreter.py` | audit every `raise`, and add one test per error class |
| 5b | `SEMANTICS.md` | write seven sections, each with a rule, an example, and its real output |
| 5c | `differential/`, `test_interpreter.py` | run the five provided programs and pin their outputs in tests |
| T.1 to T.4 (typing direction) | `hm_types.py`, `typecheck.py`, `mylang.py`, `TYPES.md` | in place of 5b and 5c |
| I.1 to I.4 (Intcode direction) | `INTCODE.md`, `intcode.py`, `test_interpreter.py` | in place of 5b and 5c |

### What You Already Have

Three pieces of this assignment exist before you start, and the schedule put them there deliberately.  Find them first, because the window is too short to rebuild any of them.

- **`Environment`, for Step 2c.**  The Environments and Scope lab closes before this assignment opens.  Copy that `Environment` class into your project on day one and wire it into the statement branches.  If the lab is still open when you reach Step 2c, finish the lab first.
- **The checker core, for Part 4.**  The Type Checker Starter lab is due inside this window (the syllabus has the date).  Read Part 4 before that lab so you know what you are extending, then grow the lab's checker to cover call sites and return types.
- **The parser and its generator, for Parts 1 and 2e.**  Your Parser assignment supplies `parse` and your existing `ast_nodes.py`, so Step 1a reconciles nodes rather than inventing them.  That assignment's recursive expression generator is what Step 2e feeds to Hypothesis here.

That leaves Parts 1, 2, 3, and 5 as the work in front of you.  Budget your time in the window against those four.

### Your First 30 Minutes

Get one statement through the whole pipeline on day one; the rest of Part 2 is filling in branches.

1. Copy the node dataclasses from Step 1a into `ast_nodes.py`, reconciling them with your parser's existing nodes.
2. In `interpreter.py`, write the `Interpreter` class with an `eval_node` method that has one branch per node type (Step 1b), each raising `NotImplementedError` for now.
3. Fill in only the `Num` branch (`return node.value`), the `Print` branch, and the `Program` branch (walk its statements).
4. Run `print 42;` end to end:

```bash
python3 -c "from parser import parse; from interpreter import Interpreter; Interpreter().eval_node(parse('print 42;'))"
```

> **You should see.** `42`.  A `NotImplementedError` naming a class tells you which branch the tree reached that you have not filled in yet; an `Unknown node type` error means a node class is missing from the dispatch.

### Suggested Pacing

See the course schedule for the assigned and due dates.  Two labs (which you may do with a partner) do real work for you here, and it helps to know where each one sits.  The **Environments and Scope lab** builds the `Environment` machinery of Step 2c.  That lab closes before this assignment opens, so you arrive already holding the file.  The **Type Checker Starter lab** builds the core of Part 4's checker, and it falls partway through this window.  Neither is a detour; each one hands you a file this assignment then imports.  Part 2 is the steepest section, so climb it in the small steps below rather than in one sitting.

| Checkpoint | You should have |
|------------|----------------|
| On assignment | Part 0 done on paper, and Part 1 complete: all node dataclasses and the dispatch skeleton (Steps 1a-1b) |
| Checkpoint 1 | Expression evaluation and short-circuit logic with the bomb test passing (Steps 2a-2b) |
| Type Checker lab due | `Environment` and statement evaluation, imported from your earlier lab and wired in; the shadowing program prints `51` then `2` (Step 2c) |
| Midpoint | Break/continue signals, the file runner with staged errors, and the Step 2e invariants running (Step 2d, Step 3a, Step 2e) |
| Checkpoint 2 | REPL with persistent environment and recovery; the checker core in place from the lab (Step 3b, Part 4) |
| Due date | Checker complete across all constructs, including call sites and return types; error hierarchy in place; Part 5 deliverable, differential programs, REPL transcript; ZIP submitted (Part 4, Steps 5a-5c) |

This window is shorter than the Parser's, so two rows are worth planning around.  You submit the Environments and Scope lab before this assignment opens.  Step 2c therefore becomes a matter of importing what you built there and wiring it in, rather than writing it from scratch.  The Type Checker lab falls in the middle of the window, and Part 4 extends its checker to call sites and return types.  Read Part 4 before that lab is due and you will know what you are building toward.

### If the Window Gets Tight

Protect the dependency chain first.  Parts 1 and 2 carry everything above them: Part 3 runs the evaluator, Part 4 checks the same AST, and Part 5 documents what Part 2 actually does.  No later part can be written around a missing Part 2.

When time runs short, work in this order:

1. **Part 1, and Steps 2a through 2c.**  A tree walker that evaluates expressions and statements against an environment is this assignment's spine.  Get that working before you polish anything else.
2. **Step 3a, the file runner.**  It is short, and it is how anyone runs your interpreter at all.
3. **Steps 2d and 2e.**  Break and continue first, then the Hypothesis invariants.
4. **Part 4, the type checker.**  The lab already handed you its core, so this is extension rather than construction.
5. **Part 5.**  `SEMANTICS.md` and the error hierarchy repay an hour of honest writing more than a rushed feature does.

Please tell me early rather than late if this window is not working for you.  The course's three-day extension policy asks only for a reasonable first draft by the deadline, and it exists for exactly this.

---

## Part 1: AST Node Dataclasses

### Step 1a: Define the Node Types

A Python `dataclass` writes `__init__`, `__repr__`, and `__eq__` for you, so a failing test prints the exact tree it was handed.  Define the node types below as `@dataclass` classes in `ast_nodes.py`.  Every field must have a type annotation and a one-line comment explaining its meaning.  Store source positions (line, col) on nodes where they aid error reporting, at minimum on `Var`, `BinOp`, `UnaryOp`, `Let`, and `Assign`.  Three design decisions are built into the list: `Var` carries a line because an undefined name is the first runtime error you report with a position; `LogicOp` is separate from `BinOp` because `and` and `or` must short-circuit (Step 2b); and `Let` and `Assign` are separate because defining a name and updating one are different operations on the environment (Step 2c).  If your parser already defines these nodes, compare each one against the definitions below and reconcile field names, since the evaluator dispatches on exactly these classes.

**You write:** `ast_nodes.py` - the sixteen node dataclasses below
**You run:** `python3 -c "from ast_nodes import Num, BinOp; print(BinOp('+', Num(1), Num(2)))"`

The skeleton gives every leaf and expression node a `line` and a `col`, and does the same for `Let` and `Assign`.  `Print`, `Block`, `If`, `While`, `Break`, and `Continue` carry a `line` only.  Later steps need the column: Step 2a's type errors and Step 4c's `Type error at line L, col C` both print one.  These are the same fields, in the same order, as the reference `ast_nodes.py`, so the reference parser can build these classes without changes.  If your Parser assignment declared positions as `field(default=0, compare=False)`, keep that form.  It changes how `==` treats positions, not what the node prints.

```python
from dataclasses import dataclass, field
from typing import Any, List, Optional
# --- Literals and variables: the leaves of the tree ---
@dataclass
class Num:
    value: float          # the numeric value (already parsed)
    line: int = 0         # 1-indexed source line (0 if built by hand)
    col: int = 0          # 1-indexed source column (0 if built by hand)
@dataclass
class Str:
    value: str            # decoded string value (escapes resolved)
    line: int = 0
    col: int = 0
@dataclass
class BoolLit:
    value: bool           # True or False
    line: int = 0
    col: int = 0
@dataclass
class Var:
    name: str             # variable name as it appears in source
    line: int = 0
    col: int = 0
# --- Expressions: nodes that combine values ---
@dataclass
class BinOp:
    op: str               # one of: + - * / < <= > >= == !=
    left: Any             # left operand expression
    right: Any            # right operand expression
    line: int = 0         # position of the operator token
    col: int = 0
@dataclass
class UnaryOp:
    op: str               # one of: - not
    operand: Any          # the operand expression
    line: int = 0
    col: int = 0
@dataclass
class LogicOp:
    op: str               # "and" or "or"; separate from BinOp for short-circuit
    left: Any             # left operand expression
    right: Any            # right operand (may never be evaluated)
    line: int = 0
    col: int = 0
# --- Statements: run for their effect, return no value ---
@dataclass
class Let:
    name: str             # variable name being defined
    value: Any            # initializer expression
    line: int = 0
    col: int = 0
@dataclass
class Assign:
    name: str             # variable name being updated (must already exist)
    value: Any            # new value expression
    line: int = 0
    col: int = 0
@dataclass
class Print:
    value: Any            # expression to evaluate and print
    line: int = 0
@dataclass
class Block:
    stmts: List[Any] = field(default_factory=list)  # statements, in order
    line: int = 0
@dataclass
class If:
    condition: Any        # test expression
    then_branch: Any      # always a Block
    else_branch: Any      # Block, If, or None
    line: int = 0
@dataclass
class While:
    condition: Any        # test expression, re-evaluated each iteration
    body: Any             # always a Block
    line: int = 0
@dataclass
class Break:
    line: int = 0         # source line, for "break outside loop" errors
@dataclass
class Continue:
    line: int = 0
@dataclass
class Program:            # the root your file runner hands to the evaluator
    stmts: List[Any] = field(default_factory=list)  # top-level statements
```

Check that the file loads and that `__repr__` is doing its job:

```bash
python3 -c "from ast_nodes import Num, BinOp; print(BinOp('+', Num(1), Num(2)))"
```

> **You should see.**
>
> ```text
> BinOp(op='+', left=Num(value=1, line=0, col=0), right=Num(value=2, line=0, col=0), line=0, col=0)
> ```

> **If it fails.**
> - `TypeError: BinOp.__init__() missing 1 required positional argument`: a field without a default is missing, or the fields are out of order.  `op`, `left`, and `right` come first; the defaulted positions come last.
> - `TypeError: non-default argument 'value' follows default argument`: a field with a default sits above one without.  Move `line` and `col` to the end of the class.
> - The output has no `col=0`: you kept your Parser's nodes without adding the column.  Add it now, because Steps 2a and 4c print it.

### Step 1b: Build the Visitor Dispatch

#### Before You Code: How the Evaluator Lives in Python

An evaluator is built from three Python patterns that you may not have combined before.  Here is each one in miniature, so the full evaluator becomes a bigger version of code you have already run.

| Idea | Python form | Where you use it |
|---|---|---|
| Dispatch on node type | an `isinstance` chain (`if isinstance(node, Num): ... elif isinstance(node, BinOp): ...`), or a dict from class to handler (`HANDLERS[type(node)](node)`) | `eval_node` in this step; `check` in Part 4 |
| An environment chain | an object holding a dict of bindings plus a `_parent` link; a lookup checks its own dict, then follows the link outward until it finds the name or the link is `None` | `Environment` in Step 2c; `TypeEnv` in Part 4 |
| A signal | an exception class raised deep inside the walk and caught by one `try`/`except` higher up; every call in between unwinds on its own | `BreakSignal` and `ContinueSignal` in Step 2d |

This page uses the `isinstance` chain, because it reads top to bottom and a missing branch falls through to a clear `else`.  A dict of handlers is just as acceptable, and the rubric accepts either.  Whichever you pick, every node class has exactly one place where its meaning is written down.

Save this as `evaluator_tour.py`.  It is scratch, so you do not submit it.  Before you run it, predict how many of the calls to `deep` return normally.

```python
from dataclasses import dataclass

# 1. Dispatch: pick the code to run from the node's class.
@dataclass
class Num:
    value: int
@dataclass
class Add:
    left: object
    right: object

def eval_chain(node):                     # style 1: an isinstance chain
    if isinstance(node, Num):
        return node.value
    elif isinstance(node, Add):
        return eval_chain(node.left) + eval_chain(node.right)
    else:
        raise TypeError(f"Unknown node type: {type(node).__name__}")

HANDLERS = {                              # style 2: a dict from class to function
    Num: lambda node: node.value,
    Add: lambda node: eval_dict(node.left) + eval_dict(node.right),
}
def eval_dict(node):
    return HANDLERS[type(node)](node)

tree = Add(Num(1), Add(Num(2), Num(3)))
print("chain:", eval_chain(tree))
print("dict: ", eval_dict(tree))

# 2. Environments: each scope is a dict plus a link to its parent.
outer = {"x": 2}
inner = {"x": 51, "__parent__": outer}
def find(scope, name):
    while scope is not None:
        if name in scope:
            return scope[name]
        scope = scope.get("__parent__")
    raise KeyError(name)
print("inner x:", find(inner, "x"), " outer x:", find(outer, "x"))

# 3. Signals: an exception unwinds through every call between raise and except.
class StopSignal(Exception):
    pass
def deep(n):
    if n == 0:
        raise StopSignal()
    return deep(n - 1)
try:
    deep(3)
except StopSignal:
    print("caught StopSignal from 3 calls down")
```

Run it with `python3 evaluator_tour.py`.

> **You should see.**
>
> ```text
> chain: 6
> dict:  6
> inner x: 51  outer x: 2
> caught StopSignal from 3 calls down
> ```

The second section is a toy: a real `Environment` is a class, not a dict with a `"__parent__"` key.  The shape is the same, though.  Look in this scope first, then walk outward.  Step 2c gives you the real class.

#### Write the Dispatch

Create `interpreter.py` with an `Interpreter` class and one `eval_node(node)` method that dispatches on node type using `isinstance`.  Paste the skeleton below and add one `elif` branch per remaining node type from Step 1a, each raising `NotImplementedError` naming the class; the `else` branch raises `InterpreterError("Unknown node type: ...")`.  The `env` parameter arrives in Step 2c; leave the default in place until then.  Before you write any evaluation logic, construct one instance of each class and confirm the `NotImplementedError` message names that class rather than reaching the `else`.

**You write:** `interpreter.py` - `InterpreterError` and `Interpreter.eval_node`, with one branch per node class
**You run:** `python3 check_dispatch.py`

```python
from ast_nodes import *
class InterpreterError(Exception):
    pass
class Interpreter:
    def eval_node(self, node, env=None):
        if isinstance(node, Num):
            raise NotImplementedError("Num")
        elif isinstance(node, Str):
            raise NotImplementedError("Str")
        elif isinstance(node, Program):
            raise NotImplementedError("Program")
        # TODO: one elif branch per remaining node type from Step 1a
        else:
            raise InterpreterError(f"Unknown node type: {type(node).__name__}")
```

| `# TODO` | How to write it |
|---|---|
| one `elif` branch per remaining node type | Copy the `Str` branch once per class, as in `elif isinstance(node, BoolLit): raise NotImplementedError("BoolLit")`.  The string is the class name, so the message tells you which branch you reached.  Thirteen classes are missing: `BoolLit`, `Var`, `BinOp`, `UnaryOp`, `LogicOp`, `Let`, `Assign`, `Print`, `Block`, `If`, `While`, `Break`, and `Continue`.  Keep the `else` last. |

Now check the dispatch.  Save this as `check_dispatch.py` (scratch, not submitted).  It builds one node of every class, plus one thing that is not a node at all, and reports which branch each one reached.

```python
from ast_nodes import *
from interpreter import Interpreter

samples = [Num(1), Str("s"), BoolLit(True), Var("x"),
           BinOp("+", Num(1), Num(2)), UnaryOp("-", Num(1)),
           LogicOp("and", BoolLit(True), BoolLit(False)),
           Let("x", Num(1)), Assign("x", Num(2)), Print(Num(1)), Block(),
           If(BoolLit(True), Block(), None), While(BoolLit(False), Block()),
           Break(), Continue(), Program(), "not a node"]
for node in samples:
    try:
        Interpreter().eval_node(node)
    except NotImplementedError as err:
        print("reached", err)
    except Exception as err:
        print(type(err).__name__ + ":", err)
```

> **You should see.**
>
> ```text
> reached Num
> reached Str
> reached BoolLit
> reached Var
> reached BinOp
> reached UnaryOp
> reached LogicOp
> reached Let
> reached Assign
> reached Print
> reached Block
> reached If
> reached While
> reached Break
> reached Continue
> reached Program
> InterpreterError: Unknown node type: str
> ```

> **If it fails.**
> - `InterpreterError: Unknown node type: Let` (or another class): that class has no `elif` yet.
> - Two lines name the same class, such as `reached Str` twice: you copied a branch and did not change the class in its `isinstance` test.
> - `NameError: name 'BoolLit' is not defined`: `ast_nodes.py` does not define that class, or `interpreter.py` lacks `from ast_nodes import *`.

---

## Part 2: Tree-Walking Evaluator

### Step 2a: Evaluate Expressions

Replace the `NotImplementedError` in each expression branch with the rule below.  Return Python values: numbers as `float` or `int`, strings as `str`, booleans as `bool`.

- `Num`, `Str`, `BoolLit`: return `node.value`.
- `Var`: call `env.lookup(node.name)`, raising a `LangNameError` if the name is not found.  Include the variable name and source line in the error.
- `UnaryOp("-")`: evaluate the operand.  If it is not a number, raise `LangTypeError("unary minus requires a number, got <type>")`.
- `BinOp`: evaluate both operands, then apply the operator.  The **type rules** are:
  - `+`, `-`, `*`, `/` require both operands to be numbers (otherwise raise `LangTypeError` naming both types).
  - `+` on two strings concatenates (if you support this, document your decision).
  - `/` by zero raises `LangZeroDivisionError` with the position.
  - `<`, `<=`, `>`, `>=` require numbers; `==`, `!=` compare any same-type pair (cross-type raises or returns False; document which and why).

The error classes (`LangNameError`, `LangTypeError`, `LangZeroDivisionError`) belong to the hierarchy that Step 5a audits, which is required in every Part 5 direction.  Define the whole hierarchy now, exactly as the skeleton below shows it, at the top of `interpreter.py`.  Step 5a does not replace these classes.  It checks that every `raise` in the file uses one of them with a good message and a position.  If you copied the starter kit, its `interpreter.py` already holds them; compare it with the skeleton, because the skeleton adds the `super().__init__` line.

Two pieces of Step 2c are needed already.  `Var` reads from an environment, and the test program below uses `let`.  Paste the `Environment` class from Step 2c now (What You Already Have asks you to bring it on day one).  Then give `Interpreter` an `__init__` that sets `self.globals = Environment()`, start `eval_node` with `if env is None: env = self.globals`, and fill the `Let` branch as Step 2c's first bullet describes.  The rest of Step 2c can wait.

**You write:** `interpreter.py` - the error classes, `is_number`, `type_name`, and the `Num`, `Str`, `BoolLit`, `Var`, `UnaryOp("-")`, and `BinOp` branches
**You run:** the two `python3 -c` commands below

```python
# --- Language-level errors: define them now; Step 5a audits every raise ---
class LangError(Exception):
    def __init__(self, message, line=0, col=0):
        self.message = message
        self.line = line
        self.col = col
        super().__init__(str(self))
    def __str__(self):
        return f"line {self.line}, col {self.col}: {self.message}"
class LangNameError(LangError): pass
class LangTypeError(LangError): pass
class LangZeroDivisionError(LangError): pass
class LangRuntimeError(LangError): pass

def is_number(value):
    """True for int and float.  bool is a subclass of int in Python, so exclude it."""
    # TODO: an isinstance test for int or float that also rules out bool
    raise NotImplementedError("is_number")

def type_name(value):
    """The type name your error messages print: bool, int, float, or str."""
    return type(value).__name__

# Inside Interpreter.eval_node, replacing the expression branches from Step 1b:
        if isinstance(node, Num):
            return node.value
        # TODO: Str and BoolLit, the same way
        elif isinstance(node, Var):
            # TODO: return env.lookup(node.name); re-raise its LangNameError with this node's position
            raise NotImplementedError("Var")
        elif isinstance(node, UnaryOp):
            value = self.eval_node(node.operand, env)
            if node.op == "-":
                # TODO: raise LangTypeError unless is_number(value); otherwise return -value
                raise NotImplementedError("unary minus")
            raise NotImplementedError("not")          # Step 2b fills this in
        elif isinstance(node, BinOp):
            left = self.eval_node(node.left, env)
            right = self.eval_node(node.right, env)
            # TODO: "+" on two strings concatenates (if you allow it)
            # TODO: + - * / < <= > >= need numbers on both sides, else LangTypeError naming both types
            # TODO: "/" with a zero right operand raises LangZeroDivisionError
            # TODO: == and != compare any pair; decide what a cross-type pair gives
            raise NotImplementedError("BinOp")
```

| `# TODO` | How to write it |
|---|---|
| `is_number` | `isinstance` accepts a tuple of classes: `isinstance(value, (int, float))`.  Add a second test, `and not isinstance(value, bool)`.  Without it `true + 1` quietly returns `2`, because Python treats `True` as the integer `1`. |
| `Str` and `BoolLit` | Two more branches that `return node.value`.  Or fold all three literals into one test, `isinstance(node, (Num, Str, BoolLit))`. |
| `Var` | `env.lookup(node.name)` raises a `LangNameError` that has no position.  Put the lookup in `try:`, catch it with `except LangNameError as err:`, and `raise LangNameError(err.message, node.line, node.col) from None`.  The `from None` hides the first, position-less traceback. |
| unary minus | Test `if not is_number(value):` and raise `LangTypeError` with the message from the bullet above, built with `type_name(value)`.  The last two arguments are always `node.line, node.col`. |
| `+` on two strings | `isinstance(left, str) and isinstance(right, str)`, tested before the number rule, returning `left + right`. |
| numbers on both sides | Test membership first, `if node.op in ("+", "-", "*", "/", "<", "<=", ">", ">="):`, then raise when `not (is_number(left) and is_number(right))`.  Build the message as `f"'{node.op}' requires numbers, got {type_name(left)} and {type_name(right)}"`.  To pick the operation, a dict from operator string to `lambda a, b: a + b` (and so on) is one lookup instead of eight `if`s. |
| `/` by zero | Test `node.op == "/" and right == 0` before you divide, and raise `LangZeroDivisionError("division by zero", node.line, node.col)`.  Python's own `ZeroDivisionError` must never escape. |
| `==` and `!=` | Python's `left == right` already compares any pair, but it says `true == 1` is `True`.  If you want that to be false, compare `type_name(left)` with `type_name(right)` first, and treat any two numbers as one kind with `is_number`.  `!=` is the negation of whatever `==` decides. |

Now run `print 1 + 2;` through the pipeline the same way as in Your First 30 Minutes, followed by the two-statement program `let x = "hello"; let y = x + 1;`:

```bash
python3 -c "from parser import parse; from interpreter import Interpreter; Interpreter().eval_node(parse('print 1 + 2;'))"
python3 -c "from parser import parse; from interpreter import Interpreter; Interpreter().eval_node(parse('let x = \"hello\"; let y = x + 1;'))"
```

> **You should see.** `3` (or `3.0` if your parser stores numbers as floats) for the first program.  The second ends in a traceback whose last line names both types:
>
> ```text
> interpreter.LangTypeError: line 1, col 28: '+' requires numbers, got str and int
> ```
>
> The whole program sits on one line inside the `-c` string, so the `+` is at line 1, col 28.  Saved as a two-line file, the same error would say line 2, col 11.  Your wording after the colon may differ, as long as both types appear.

> **If it fails.**
> - `NotImplementedError: Let`, or `AttributeError: 'Interpreter' object has no attribute 'globals'`: you skipped the two Step 2c pieces described above.
> - `TypeError: can only concatenate str (not "int") to str`, a Python error rather than a `LangTypeError`: your `BinOp` branch applied `+` before it checked the operand types.
> - The message says `line 0, col 0`: a `raise` is missing `node.line, node.col`, or your parser does not fill in positions.

### Step 2b: Implement Short-Circuit Logic

Short-circuit logic means the evaluator stops as soon as the left operand decides the answer.

- `LogicOp("and")`: evaluate left; if falsy, return it without evaluating right.  Otherwise return right.
- `LogicOp("or")`: evaluate left; if truthy, return it without evaluating right.  Otherwise return right.
- `UnaryOp("not")`: evaluate the operand, apply truthiness, and return the boolean complement.

Truthiness policy (document it in SEMANTICS.md): which values count as false in your language?  At minimum: `false`, `0`, `0.0`, and `""`.  Everything else is truthy.

**You write:** `interpreter.py` - `Interpreter.truthy`, the `LogicOp` branch, and the `not` case of `UnaryOp`; `test_interpreter.py` - `test_bomb`
**You run:** `python3 -m pytest test_interpreter.py`

Put the policy in one method, `truthy`, and call it from every place that needs a yes-or-no answer.  `LogicOp`, `not`, `If`, and `While` all use it, so a change to your policy is a change to one method.

```python
    def truthy(self, value):
        """Your truthiness policy from Part 0, in one place so it stays consistent."""
        # TODO: a bool is itself; a number is true unless zero; a string is true unless empty
        # TODO: anything else is true
        raise NotImplementedError("truthy")

# Inside eval_node:
        elif isinstance(node, LogicOp):
            left = self.eval_node(node.left, env)
            # TODO: "and": if left is falsy, return left; otherwise evaluate and return the right
            # TODO: "or": if left is truthy, return left; otherwise evaluate and return the right
            raise NotImplementedError("LogicOp")
# ...and in the UnaryOp branch, replacing raise NotImplementedError("not"):
            if node.op == "not":
                # TODO: the boolean complement of truthy(value)
                raise NotImplementedError("not")
```

| `# TODO` | How to write it |
|---|---|
| bool, number, string | Test `isinstance(value, bool)` first, because `True` is also an `int`.  Then `is_number(value)` leads to `value != 0`, and `isinstance(value, str)` leads to `value != ""`. |
| anything else | `return True`.  If your Part 0 policy differs from the minimum above, this method is the one place to change it. |
| `"and"` | Test `self.truthy(left)` and return `left` itself, not `True` or `False`.  Call `self.eval_node(node.right, env)` only on the path where the left did not decide the answer. |
| `"or"` | The mirror image of `"and"`: return `left` when it is truthy. |
| `not` | Python's own `not` applied to `self.truthy(value)`.  `not` always gives a real boolean, even though `and` and `or` give back an operand. |

**Bomb test**: include the program `let safe = true or (1 / 0);` in your test suite and verify that it does not raise an error, since the right side must never be evaluated.  Create `test_interpreter.py` with the bomb test as its first test, then run `python3 -m pytest test_interpreter.py`:

```python
from parser import parse
from interpreter import Interpreter
def test_bomb():
    # must not raise: the right side of `or` is never evaluated
    Interpreter().eval_node(parse('let safe = true or (1 / 0);'))
```

> **You should see.** A last line such as `============================== 1 passed in 0.16s ===============================` (the time varies).  If you started from the starter kit's `test_interpreter.py`, it also holds the shadowing test, which fails with `NotImplementedError: Block` until Step 2c.  In that case the last line reads `1 failed, 1 passed`, and the failure is the shadowing test, not the bomb test.

> **If it fails.**
> - A `LangZeroDivisionError` in the traceback: your `or` branch evaluates the right operand before checking the left.
> - `NotImplementedError: Let`: fill the `Let` branch (see Step 2a), since the bomb test is a `let`.
> - `No module named pytest`: run `pip install pytest`, then try again.

Control-flow theory questions (in your readme, required in every Part 5 direction), from the Control Flow and Statement Semantics session:

1.  Explain why short-circuiting is a *semantic commitment* rather than an optimization, using the bomb test as evidence.  What observable behavior changes if both sides evaluate?
2.  Your `and`/`or` return an *operand*, not a boolean.  Name one language that does this and one that coerces to boolean, and state one concrete program whose result differs between the two designs.
3.  Pick one truthiness rule you adopted and one you rejected, and defend the pair against a reliability argument from the Evaluating Languages criteria.

### Step 2c: Build the Environment and Evaluate Statements

An environment is the table that maps variable names to their current values.  Each block gets its own environment with a link to its parent, which is how nested scopes work.  The Environments and Scope lab builds this machinery (alone or with a partner); bring your lab code here and add the class to `interpreter.py`, above `Interpreter`.

**You write:** `interpreter.py` - `Environment` (from your lab), `format_value`, and the `Assign`, `Print`, `Block`, `If`, and `While` branches
**You run:** `python3 -c "from parser import parse; from interpreter import Interpreter; Interpreter().eval_node(parse(open('shadow.ml').read()))"`

Paste the class, not the lab's `LangError` and `LangNameError`.  Step 2a already defined those in this file, and the lab's warning applies here: with two copies of `LangNameError`, an `except LangNameError` can miss the one your `Environment` raises.  The parent tests below read `is not None`, as the lab recommends.  The starter kit's copy already does.

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
        if self._parent is not None:
            return self._parent.lookup(name)
        raise LangNameError(f"Undefined variable '{name}'")
    def assign(self, name: str, value):
        """Update an existing binding wherever it lives; raise LangNameError if not found."""
        if name in self._bindings:
            self._bindings[name] = value
        elif self._parent is not None:
            self._parent.assign(name, value)
        else:
            raise LangNameError(f"Cannot assign to undefined variable '{name}'")
```

Give `Interpreter` a global environment (`self.globals = Environment()` in `__init__`), have `eval_node` use it when `env` is `None`, and pass `env` through every recursive call so blocks can hand their child environment down.  You did the first two in Step 2a.  Then implement the statements:

- `Let`: evaluate the initializer, then call `env.define(node.name, value)`.
- `Assign`: evaluate the value, then call `env.assign(node.name, value)`.  This updates the binding wherever it lives; it does *not* create a new one.
- `Print`: evaluate the expression and print the result to stdout.  Booleans print as `true`/`false`, not `True`/`False`.
- `Block`: create a child environment `child_env = Environment(parent=env)`, then evaluate each statement in the block using `child_env`.  When the block finishes, discard `child_env` (it goes out of scope naturally).
- `If`: evaluate the condition and convert it to a boolean with your truthiness rule.  Execute `then_branch` if truthy, and `else_branch` (if present) otherwise.
- `While`: evaluate the condition and execute the body while it is truthy.  Document whether the loop body creates a per-iteration scope (both choices are valid; pick one and write it in SEMANTICS.md).  Catch `BreakSignal` to exit early; catch `ContinueSignal` to restart the loop.

Here are those branches as a skeleton, with the `Let` branch you wrote in Step 2a for comparison.  The signals in the last bullet wait for Step 2d.

```python
def format_value(value):
    """How print shows a value: true/false for booleans, str() for everything else."""
    # TODO: a bool becomes "true" or "false"; every other value becomes str(value)
    raise NotImplementedError("format_value")

# Inside eval_node:
        elif isinstance(node, Let):
            env.define(node.name, self.eval_node(node.value, env))   # from Step 2a
        elif isinstance(node, Assign):
            # TODO: evaluate node.value, then env.assign; re-raise LangNameError with this node's position
            raise NotImplementedError("Assign")
        elif isinstance(node, Print):
            # TODO: print the evaluated value through format_value
            raise NotImplementedError("Print")
        elif isinstance(node, Block):
            child_env = Environment(parent=env)
            # TODO: evaluate each statement in node.stmts with child_env
            raise NotImplementedError("Block")
        elif isinstance(node, If):
            # TODO: truthy condition -> then_branch; otherwise else_branch, if it is not None
            raise NotImplementedError("If")
        elif isinstance(node, While):
            # TODO: loop while the condition is truthy, evaluating the body (see the scope choice below)
            raise NotImplementedError("While")
```

| `# TODO` | How to write it |
|---|---|
| `format_value` | Test `isinstance(value, bool)` first.  The conditional expression `"true" if value else "false"` picks the word. |
| `Assign` | The same shape as `Var` in Step 2a.  Call `env.assign(node.name, value)` inside `try:`, and re-raise the `LangNameError` with `node.line, node.col`. |
| `Print` | Wrap the evaluated value in `format_value(...)` before you hand it to Python's `print`.  The version from Your First 30 Minutes called `print` directly, so booleans came out as `True`. |
| `Block` | A `for stmt in node.stmts:` loop that calls `self.eval_node(stmt, child_env)`.  Pass `child_env`, never `env`, and never store it in `self.globals`. |
| `If` | `if self.truthy(self.eval_node(node.condition, env)):` evaluates the then branch.  Then use `elif node.else_branch is not None:`.  An `else_branch` that is itself an `If` needs no special case, because `eval_node` already handles `If`. |
| `While` | `while self.truthy(self.eval_node(node.condition, env)):` evaluates the condition again on every pass.  The body line depends on your scope choice, shown next. |

The scope choice comes down to where the child environment is made.  Your `While` body is a `Block`, and Step 2c's `Block` branch makes a fresh child environment every time it runs.  So the plain recursive call gives you a per-iteration scope for free.  The alternative makes one child environment before the loop and runs the body's statements in it directly:

```python
# Choice A: a per-iteration scope.  Each pass through the Block branch
# makes a new child Environment, so a `let` in the body starts fresh.
            while self.truthy(self.eval_node(node.condition, env)):
                self.eval_node(node.body, env)

# Choice B: one scope for the whole loop.  Make the child once, then run
# the body's statements in it, skipping the Block branch.
            loop_env = Environment(parent=env)
            while self.truthy(self.eval_node(node.condition, env)):
                for stmt in node.body.stmts:
                    self.eval_node(stmt, loop_env)
```

In both choices, a `let` inside the body does not survive the loop.  Differential program 4 in Step 5c probes this.  **Can you write a program whose output differs between Choice A and Choice B?**

> **Do this.** Save the **shadowing program** as `shadow.ml`, run it through the pipeline with the Your First 30 Minutes command (passing `open('shadow.ml').read()` to `parse`), and add it to `test_interpreter.py`:
>
> ```text
> let x = 2;
> {
>     let x = 51;
>     print x;       # prints 51
> }
> print x;           # prints 2
> ```

> **You should see.** `51` on one line and `2` on the next.

> **If it fails.**
> - Both lines print `51`: your `Block` branch evaluated its statements in the parent environment instead of a child, or `Let` called `assign` instead of `define`.
> - `Undefined variable 'x'` after the block: your `Block` branch replaced `self.globals` with the child environment instead of passing the child down.
> - `NotImplementedError: format_value` or `NotImplementedError: Block`: a skeleton line is still in place.  The message names the one to fill.

### Step 2d: Implement Break and Continue

Implement `break` and `continue` with signal exception classes: the `Break` and `Continue` branches raise them, and the `While` branch wraps its body evaluation in `try`/`except` for both.  If a signal escapes a `While` body and reaches the top level, the error handler (Step 3a) reports it as a `LangRuntimeError("break outside loop")` or similar.  Add a test with a `while` loop that counts to 10 and breaks at 5, and confirm it prints `1` through `5` only.  A `BreakSignal` traceback means the `While` branch is not catching it; an infinite loop means `continue` skipped the counter update, which is a semantics decision, so give it a line in SEMANTICS.md.

**You write:** `interpreter.py` - `BreakSignal`, `ContinueSignal`, the `Break` and `Continue` branches, and the `try` in `While`; `break.ml`, `continue.ml`, and `test_break_at_five` in `test_interpreter.py`
**You run:** `python3 -c "from parser import parse; from interpreter import Interpreter; Interpreter().eval_node(parse(open('break.ml').read()))"`

**First, check that your parser can produce these nodes.**  The reference lexer and parser already read `break;` and `continue;`.  The Parser assignment did not ask for them, so if you built your own, add them now:

1. Two keyword tokens, `BREAK` with the pattern `break\b` and `CONTINUE` with `continue\b`.  Put them before `IDENT`, like every other keyword, or `break` lexes as an identifier.
2. Two cases in `parse_stmt`.  Each one consumes its keyword with `expect`, then a `SEMICOLON`, and returns `Break(tok.line)` or `Continue(tok.line)`, where `tok` is the keyword token.

Confirm the parse before you touch the evaluator:

```bash
python3 -c "from parser import parse; print(parse('while true { break; }'))"
```

> **You should see.**
>
> ```text
> Program(stmts=[While(condition=BoolLit(value=True, line=1, col=7), body=Block(stmts=[Break(line=1)], line=1), line=1)])
> ```
>
> A `ParseError` on `break;` (often `expected EQ, found SEMICOLON`) means the lexer read `break` as an `IDENT`, so `parse_stmt` treated it as the start of an assignment.

Now the evaluator.  Each signal carries a `line`, so Step 3a can say where a stray `break` was.  The starter kit already declares both classes this way:

```python
class BreakSignal(Exception):
    """Raised by a Break node; caught by the nearest enclosing While."""
    def __init__(self, line=0):
        super().__init__("break")
        self.line = line          # where the break was, for "break outside loop"
class ContinueSignal(Exception):
    """Raised by a Continue node; caught by the nearest enclosing While."""
    def __init__(self, line=0):
        super().__init__("continue")
        self.line = line

# Inside eval_node:
        elif isinstance(node, Break):
            # TODO: raise the break signal, carrying this node's line
            raise NotImplementedError("Break")
        elif isinstance(node, Continue):
            # TODO: raise the continue signal, carrying this node's line
            raise NotImplementedError("Continue")
        elif isinstance(node, While):
            while self.truthy(self.eval_node(node.condition, env)):
                # TODO: wrap the body in try; a BreakSignal leaves the loop, a ContinueSignal starts the next pass
                self.eval_node(node.body, env)
```

| `# TODO` | How to write it |
|---|---|
| raise the break or continue signal | `raise` the matching class, passing `node.line` as its argument.  The branch never returns. |
| wrap the body in `try` | Put `try:` around the one body line, followed by `except BreakSignal:` with Python's `break` and `except ContinueSignal:` with Python's `continue`.  These work because the `except` clauses sit inside the Python `while`. |

A signal that escapes every `While` needs nothing here.  It travels up to `run_source` in Step 3a, which turns it into a staged `Runtime error`.

Save these two programs.  The first is the required test program; the second shows `continue`:

```text
# break.ml
let i = 0;
while i < 10 {
    i = i + 1;
    print i;
    if i == 5 { break; }
}
```

```text
# continue.ml
let i = 0;
while i < 5 {
    i = i + 1;
    if i == 3 { continue; }
    print i;
}
```

Then add the test to `test_interpreter.py`:

```python
import io
from contextlib import redirect_stdout

def test_break_at_five():
    buf = io.StringIO()
    with redirect_stdout(buf):
        Interpreter().eval_node(parse(open("break.ml").read()))
    assert buf.getvalue().split() == ["1", "2", "3", "4", "5"]
```

> **You should see.** `break.ml` prints `1`, `2`, `3`, `4`, and `5`, one per line, and stops.  `continue.ml` (run the same command with its name) prints `1`, `2`, `4`, and `5`.  The `3` is skipped because `continue` jumps past the `print`.  The counter update comes before the `continue`, so the loop still ends.

> **If it fails.**
> - A `BreakSignal` traceback: the `While` branch has no `try`, or its `try` catches only `ContinueSignal`.
> - `continue.ml` prints `1` and `2` and then stops: the `try` surrounds the whole Python `while` instead of the body line, so a `ContinueSignal` ends the loop rather than starting the next pass.
> - `continue.ml` never stops: you moved `i = i + 1;` below the `continue`, so the counter stops changing at 3.  That is the semantics decision named above; give it a line in SEMANTICS.md.

### Step 2e: Verify Invariants with Hypothesis

In the Parser assignment you used [Hypothesis](https://hypothesis.readthedocs.io/) to check a *syntactic* law (round-trip).  Here you check *semantic* laws: properties that must hold for every program, not only the ones in your test file.  The programs you did not think to write are where scoping and short-circuit bugs hide.  This step is required.  Reuse the recursive AST generator you built for the parser (copy it into `test_interpreter.py` or import it), restricted to the expression and small-statement nodes your evaluator supports, and encode **at least four** invariants as `@given` tests.  The first three below are required; add at least one more, either the fourth below or one of your own:

1.  Determinism.  Evaluating the same AST twice in fresh environments produces identical output and result.  `eval(tree)` has no hidden state that leaks between runs.
2.  Scope restoration.  For any generated expression `e` and a fresh variable name `v` not free in `e`, evaluating a block that binds `v` with `let` and then evaluates `e` leaves the outer environment without `v` afterward: the inner `let` does not leak.  (Generate `e`; wrap it; assert the outer env is unchanged.)
3.  Short-circuit non-evaluation.  Give `and`/`or` a right operand with an observable side effect (for example, a call to a test-only built-in function that appends to a Python list each time it runs, or a subexpression that divides by zero).  Assert that when the left operand determines the result (`false and X`, `true or X`), the right operand's side effect never fires.  Hypothesis will hunt for the operand shape that sneaks past your short-circuit.
4.  Arithmetic agreement (metamorphic).  For generated integer-only expressions using `+ - *`, your evaluator's result equals Python's evaluation of the same expression.  This is a cheap oracle that catches precedence and associativity bugs that slipped through the parser into evaluation.

The first invariant is written out in full below, because the shape of one of these is most of the difficulty; the others are yours.  Note the two things it does that a hand-written test does not: it builds a *fresh* `Interpreter` for each run, so state cannot leak between them, and it captures stdout so that printed output counts as part of the result.

**You write:** `test_interpreter.py` - the `exprs` generator, `run`, `test_determinism`, `test_scope_restoration`, `Probe` and `ProbeInterpreter`, `test_short_circuit_non_evaluation`, and at least one more invariant
**You run:** `python3 -m pytest -v test_interpreter.py`

Your Parser generator needs two changes before the evaluator can use it.  First, it built `Var` leaves named `x`, `y`, and `z`.  A fresh interpreter has no bindings, so nearly every generated tree would stop at a `LangNameError`.  The generator below uses literal leaves only.  Second, it built only `BinOp` nodes, and the evaluator also has `LogicOp` and `UnaryOp`, so the generator builds those too.  Note that `exprs` is a strategy object, not a function, so you write `@given(tree=exprs)` with no parentheses.

A generated tree can still fail on its own, such as `1 / 0` or `true + 1`.  That is a legitimate outcome, not a broken test, so `run` records the error as part of the result instead of letting it escape.

```python
import io
from contextlib import redirect_stdout
from dataclasses import dataclass
from typing import Any

import pytest
from hypothesis import given, assume
from hypothesis import strategies as st

from ast_nodes import *
from parser import parse
from interpreter import Interpreter, LangError, LangNameError

leaves = st.one_of(
    st.integers(min_value=0, max_value=999).map(Num),
    st.booleans().map(BoolLit),
)
exprs = st.recursive(
    leaves,
    lambda kids: st.one_of(
        st.builds(BinOp, st.sampled_from(["+", "-", "*", "/", "<", "=="]), kids, kids),
        st.builds(LogicOp, st.sampled_from(["and", "or"]), kids, kids),
        st.builds(UnaryOp, st.sampled_from(["-", "not"]), kids),
    ),
    max_leaves=25,
)

def run(tree):
    """Evaluate a tree in a fresh interpreter, returning (value, printed output).
    A language error is a legal outcome, so it becomes part of the result."""
    buf = io.StringIO()
    with redirect_stdout(buf):
        try:
            value = Interpreter().eval_node(tree)
        except LangError as err:
            value = f"{type(err).__name__}: {err.message}"
    return value, buf.getvalue()

@given(tree=exprs)
def test_determinism(tree):
    first = run(tree)
    second = run(tree)
    assert first == second, f"same tree gave {first!r} then {second!r}"

@given(e=exprs)
def test_scope_restoration(e):
    interp = Interpreter()
    tree = Program([Block([Let("v", Num(0)), Print(e)])])
    # TODO: evaluate tree with interp, hiding the printed output and ignoring a LangError
    # TODO: assert that interp.globals.lookup("v") now raises LangNameError

@dataclass
class Probe:
    """Test-only node: the side-effecting built-in.  Records that it ran, then returns its value."""
    value: Any

class ProbeInterpreter(Interpreter):
    """An Interpreter that also understands Probe."""
    def __init__(self):
        super().__init__()
        self.fired = []          # one entry per Probe evaluation
    def eval_node(self, node, env=None):
        if isinstance(node, Probe):
            # TODO: record node.value in self.fired, then return it
            raise NotImplementedError("Probe")
        return super().eval_node(node, env)

@given(left=exprs, op=st.sampled_from(["and", "or"]))
def test_short_circuit_non_evaluation(left, op):
    interp = ProbeInterpreter()
    # TODO: evaluate left alone; discard this example if that raises a LangError
    # TODO: discard it unless left decides op (falsy for "and", truthy for "or")
    # TODO: evaluate LogicOp(op, left, Probe(1)) and assert interp.fired == []

# TODO: at least one more invariant, e.g. test_arithmetic_agreement over + - * trees
```

| `# TODO` | How to write it |
|---|---|
| evaluate, hiding output and ignoring a `LangError` | `with redirect_stdout(io.StringIO()):` around `try: interp.eval_node(tree)` and `except LangError: pass`.  A generated `e` may divide by zero, and that is not a scope bug. |
| assert the lookup raises | `with pytest.raises(LangNameError):` around `interp.globals.lookup("v")`.  The test fails if the lookup succeeds, which is exactly a leaked `let`. |
| record and return the `Probe` | `self.fired.append(node.value)`, then `return node.value`.  Your `Interpreter` makes every recursive call through `self.eval_node`, so a `Probe` anywhere in a tree reaches this method. |
| evaluate `left` alone | `try: left_value = interp.eval_node(left)` and `except LangError: assume(False)`.  `assume(False)` tells Hypothesis to throw this example away and draw another. |
| `left` decides `op` | For `"or"` the left decides when `interp.truthy(left_value)` holds; for `"and"`, when it does not.  Store that in a variable and call `assume(...)` on it. |
| evaluate and assert | `interp.eval_node(LogicOp(op, left, Probe(1)))`, then the `assert`.  Positions default to 0, so you can build nodes by hand. |
| one more invariant | For arithmetic agreement, write a second strategy, `int_exprs`, with only `Num` leaves and `BinOp` over `["+", "-", "*"]`.  Then write a small recursive `python_value(tree)` that uses a dict from operator to `lambda a, b: ...`.  Assert `Interpreter().eval_node(tree) == python_value(tree)`. |

> **You should see.** After `python3 -m pytest -v test_interpreter.py`, each property test listed as passed, or a `Falsifying example` block showing the smallest program that breaks the invariant (Hypothesis shrinks a failure to the minimal offending program).  Recent Hypothesis versions label that block `Failing test case:` instead.  A passing run includes these four lines among your other tests, each followed by a percentage:
>
> ```text
> test_interpreter.py::test_determinism PASSED
> test_interpreter.py::test_scope_restoration PASSED
> test_interpreter.py::test_short_circuit_non_evaluation PASSED
> test_interpreter.py::test_arithmetic_agreement PASSED
> ```
>
> In your `readme.md`, report one invariant that caught a real bug, or a reasoned all-clear with your properties and the generator shown.

To see a property bite once, break your `or` branch on purpose: move `self.eval_node(node.right, env)` above the truthiness test, run the suite, and put the line back.  The bomb test fails, and so does `test_short_circuit_non_evaluation`, with a shrunk example such as `left=Num(1), op='or'`.

> **If it fails.**
> - `TypeError: 'RecursiveStrategy' object is not callable`: you wrote `exprs()`.  A strategy is used as `exprs`, without parentheses.
> - `NotImplementedError: Probe`: the `Probe` branch of `ProbeInterpreter` is still the skeleton line.
> - `test_scope_restoration` fails with `Failed: DID NOT RAISE LangNameError`: your `Block` branch runs its statements in `env` instead of `child_env`, so `v` lands in the global scope.  This is the leak the invariant exists to catch.

> **Why this matters.** The same invariants, generalized to your team's language, become the core of the Team Language Project's property-based test suite, so write them to be reusable.

---

## Part 3: REPL and File Runner

### Step 3a: Build the File Runner

`python3 mylang.py program.ml` should:

1.  Read the source file.
2.  Lex it, catching `LexError` -> print `"Lexical error at line L, col C: <message>"` and exit.
3.  Parse it, catching `ParseError` -> print `"Syntax error at line L, col C: expected X, found Y"` and exit.
4.  Evaluate it, catching `LangNameError`, `LangTypeError`, `LangZeroDivisionError`, and `LangRuntimeError` -> print `"Runtime error at line L: <message>"` and exit.

The stage label (`Lexical error`, `Syntax error`, `Runtime error`) must appear in every message.  Create `mylang.py` in the project folder from this skeleton, then run the shadowing program through it (`python3 mylang.py shadow.ml`) and a program with one error of each stage.

**You write:** `mylang.py` - `run_source` and `run_file`
**You run:** `python3 mylang.py shadow.ml`, then the same command on each error program below

The skeleton puts the stages in a helper, `run_source`, that *returns* the staged message instead of printing it and exiting.  `run_file` prints the message and exits.  The REPL in Step 3b prints it and keeps going.  The Type stage in Step 4c goes into the same helper, so each stage's `try` is written exactly once.

```python
import sys
from lexer import LexError          # TODO: match your lexer's error class name
from parser import parse, ParseError
from interpreter import Interpreter, LangError, BreakSignal, ContinueSignal
def run_source(source, interp):
    """Run one program through every stage.  Return None, or one staged error line."""
    # TODO: tree = parse(source), catching LexError -> "Lexical error at line L, col C: ..."
    #       and ParseError -> "Syntax error at line L, col C: ..."
    # TODO: interp.eval_node(tree), catching LangError subclasses -> "Runtime error at line L: ..."
    # TODO: a BreakSignal or ContinueSignal that escapes -> "Runtime error at line L: 'break' outside loop"
    return None
def run_file(path):
    source = open(path).read()
    message = run_source(source, Interpreter())
    if message is not None:
        print(message)
        sys.exit(1)                  # exit after printing any error
if __name__ == "__main__":
    run_file(sys.argv[1]) if len(sys.argv) > 1 else repl()   # repl() arrives in Step 3b
```

| `# TODO` | How to write it |
|---|---|
| parse, catching `LexError` and `ParseError` | One `try: tree = parse(source)` with two `except` clauses, `except LexError as err:` and `except ParseError as err:`.  Each one `return`s an f-string built from `err.line`, `err.col`, and `err.message`.  The reference lexer is lazy: it lexes while `parse` asks for tokens, so its `LexError` comes out of `parse`.  If your lexer runs first as its own call, give that call its own `try` above this one.  If your `ParseError` keeps `expected` and `found` instead of `message`, build the text as `f"expected {err.expected}, found {err.found}"`. |
| evaluate, catching `LangError` | A second `try` around `interp.eval_node(tree)`, with `except LangError as err:` returning `f"Runtime error at line {err.line}: {err.message}"`.  One clause catches all four subclasses. |
| a stray signal | Two more `except` clauses on the same `try`, `except BreakSignal as sig:` and `except ContinueSignal as sig:`, using the `sig.line` you stored in Step 2d. |

Save one program per stage, so each stage's message has been seen at least once.  Each error sits on line 2, after a `print 1;` that shows whether the program started running:

| File | Contents |
|---|---|
| `badlex.ml` | `print 1;` then `let z = 3 @ 4;` |
| `badsyntax.ml` | `print 1;` then `let = 4;` |
| `divzero.ml` | `let y = 1 / 0;` (one line) |
| `strays.ml` | `print 1;` then `break;` |

> **You should see.** `51` then `2`, with no traceback.  For a file containing `let y = 1 / 0;`, exactly one line: `Runtime error at line 1: division by zero` (your wording may differ; the stage label and line may not).  With the reference lexer and parser, the four files print:
>
> ```text
> $ python3 mylang.py badlex.ml
> Lexical error at line 2, col 11: unexpected character '@'
> $ python3 mylang.py badsyntax.ml
> Syntax error at line 2, col 5: expected IDENT, found EQ
> $ python3 mylang.py divzero.ml
> Runtime error at line 1: division by zero
> $ python3 mylang.py strays.ml
> 1
> Runtime error at line 2: 'break' outside loop
> ```
>
> Look at which files print `1`.  **Why does `strays.ml` print it while `badlex.ml` and `badsyntax.ml` do not?**

> **If it fails.**
> - A Python traceback instead of a staged message: the exception escaped the `try` for its stage.  Check that each stage's `except` names the right class.
> - `Runtime error` for a misspelled keyword: that is a lexical or syntax error and must be caught at its own stage, before evaluation begins.
> - `AttributeError: 'ParseError' object has no attribute 'message'`: your Parser's error class stores `expected` and `found`.  Build the text from those, as the hint table shows.
> - `NameError: name 'repl' is not defined` when you run `python3 mylang.py` with no file: expected until Step 3b.

### Step 3b: Build the REPL

`python3 mylang.py` with no arguments launches the REPL.  Requirements:

- Display a `>> ` prompt.
- Read one line (or detect a multi-line statement and keep prompting with `.. `; document your choice).
- Maintain a single `Environment` across all REPL inputs.
- On a successfully evaluated expression-statement, print the value.
- On any error (lexical, syntax, or runtime), print the error and return to the prompt without crashing.
- `quit` or `exit` (or EOF/Ctrl-D) exits cleanly.

**You write:** `mylang.py` - `repl()`; `repl_transcript.txt` - the saved session
**You run:** `python3 mylang.py`

```python
def repl():
    """Step 3b: one persistent Environment, recovery after every error class."""
    interp = Interpreter()           # ONE interpreter for the session, so ONE global Environment
    while True:
        # TODO: read a line with input(">> "); leave the loop on EOFError
        # TODO: leave the loop on "quit" or "exit"
        # TODO: run the line through run_source(line, interp); print any message and keep looping
        raise NotImplementedError("repl")
```

| `# TODO` | How to write it |
|---|---|
| read a line, leaving on `EOFError` | `try: line = input(">> ")` and `except EOFError:` with a bare `print()` and `break`.  The `print()` moves the shell's prompt onto a fresh line after Ctrl-D. |
| `quit` or `exit` | `line.strip() in ("quit", "exit")`, then `break`. |
| run the line | `message = run_source(line, interp)`, and `print(message)` when it is not `None`.  Because `run_source` returns instead of exiting, the loop simply goes around again. |
| printing an expression's value (optional) | The grammar has no expression statements, so `x + 1` alone is a `ParseError`.  The reference parser also offers `parse_expression(source)`.  On a `ParseError`, try that and print `format_value(interp.eval_node(expr))`.  The transcript below does not need it. |

> **Do this.**
> 1. Fill in `repl()` in `mylang.py`: create one `Interpreter` before the loop, and inside the loop read a line with `input(">> ")`, run it through the same three stages as `run_file`, and print any error instead of exiting.
> 2. Handle `EOFError` (Ctrl-D) and the words `quit` and `exit` by leaving the loop, then launch it with `python3 mylang.py` and reproduce the transcript below.

> **You should see.** This session, which you also save as `repl_transcript.txt` for your submission.  It demonstrates each error class and that the environment survives an error (`x` is still `15` at the end).

```text
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

> **If it fails.**
> - `x` is gone after the division error: you created a new `Interpreter` (or a new `Environment`) inside the loop.
> - The REPL exits on the first error: an `except` is calling `sys.exit` the way `run_file` does.  In the REPL, print and continue.

---

## Part 4: The Small Static Type Checker

Your evaluator enforces types *dynamically*: a type error surfaces only when the offending expression is actually evaluated.  Part 4 adds a small **static type checker** that catches a useful class of those errors before evaluation begins, as its own pipeline stage: lex -> parse -> check -> evaluate.  This is deliberately not full type inference.  Annotations are required at declarations, so there is no unification; the checker verifies only what is *declared*.

> **The checker is stricter than the evaluator, on purpose.**  Your evaluator has a truthiness rule, so `while 1 { ... }` and `"" or "fallback"` both mean something at run time.  A checker that requires `Bool` conditions and `Bool` operands rejects those programs before they run, even though they would have worked.  That gap is not a bug in either stage: a static checker that never accepts a program that would fail must also reject some programs that would have succeeded, and where to draw that line is a language design decision rather than a correctness question.  Decide where you draw it, implement it consistently, and say so in `SEMANTICS.md`; the Type Checker Starter lab's last reflection prompt asks you to defend exactly this choice.  Where a type is unknown (an unannotated construct you choose not to cover), document the gap in your readme rather than guessing.  The Type Checker Starter lab builds the core (alone or with a partner) before this part is due, and the Hindley-Milner direction in Part 5 grows this checker into whole-program inference, so Part 4 is a foundation, not a throwaway.

### Step 4a: Carry Type Annotations on Declarations

Your language's `let` declarations and function definitions carry (or are extended to carry) type annotations: `let x: Num = 42;`, `fun f(a: Num, b: Str) -> Bool { ... }`.  The checker can only verify what the parser hands it, so the annotation has to survive lexing and parsing and land on the AST node.  Extend your lexer and parser so `let` accepts an optional `: Type` after the name (and so function definitions carry parameter and return annotations, if your language has functions), then add the annotation to the node.

> **This step is yours even if you are using the reference parser.**  The reference lexer has no `COLON` token and the reference `Let` node has no annotation field, so `let x: Num = 1;` does not lex, let alone parse, against it out of the box.  That is deliberate: reading a new token, threading it through one production, and landing it on a node is the smallest end-to-end change you can make to a language pipeline, and Part 4 is the right moment to make it.  The Type Checker Starter lab walks the same extension and budgets about ten minutes for it.  Do it in whichever lexer and parser you are building on, and note in your readme which one that was.  One way is an optional field on `Let`, `type_ann: Optional[str] = None`, holding `"Num"`, `"Str"`, `"Bool"`, or `None`.  If your Type Checker Starter lab already added this field under the name `annotation`, keep that name, and read `annotation` wherever this page says `type_ann`.

**You write:** your lexer - a `COLON` token; `ast_nodes.py` - the `type_ann` field on `Let`; `parser.py` - the annotation in `parse_let_stmt`
**You run:** `python3 -c "from parser import parse; print(parse('let x: Num = 42;'))"`

The change touches three files, one line or a few lines in each.  The skeleton shows the reference versions; yours may differ in names.

```python
# Lexer: one new token.  The reference lexer reads its default table from
# TOKEN_SPEC in lexer.py (token_spec.json is read only when you pass
# config_path), so add the pair to that list.  ":" is no other token's
# prefix, so its position in the list does not matter.
    ("COLON",      r":"),

# ast_nodes.py: one new field, last and with a default, so every
# existing Let(...) call keeps working.
@dataclass
class Let:
    name: str             # variable name being defined
    value: Any            # initializer expression
    line: int = 0
    col: int = 0
    type_ann: Optional[str] = None   # "Num", "Str", "Bool", or None if unannotated

# parser.py
    def parse_let_stmt(self):
        let_tok = self.expect("LET")
        name = self.expect("IDENT")
        type_ann = None
        # TODO: if the next token is a COLON, consume it, then expect an IDENT and keep its value
        self.expect("EQ")
        value = self.parse_expr()
        self.expect("SEMICOLON")
        return Let(name.value, value, let_tok.line, let_tok.col, type_ann)
```

| `# TODO` | How to write it |
|---|---|
| an optional `COLON` and type name | `if self.peek().type == "COLON":`, then `self.advance()`, then `type_ann = self.expect("IDENT").value`.  Type names such as `Num` lex as ordinary identifiers, so no new keyword is needed. |

Confirm the annotation lands on the node:

```bash
python3 -c "from parser import parse; print(parse('let x: Num = 42;'))"
```

> **You should see.** A `Program` whose `Let` node shows `type_ann='Num'`.  A `ParseError` means the parser is not consuming the colon and type name yet.  With the reference parser and the skeleton above, the line is:
>
> ```text
> Program(stmts=[Let(name='x', value=Num(value=42, line=1, col=14), line=1, col=1, type_ann='Num')])
> ```

> **If it fails.**
> - `LexError at line 1, col 6: unexpected character ':'`: the lexer has no `COLON` yet, or you edited a token table the lexer does not read.
> - `ParseError ... expected EQ, found COLON`: the lexer works, but `parse_let_stmt` is not consuming the colon.
> - `TypeError: Let.__init__() takes from 3 to 5 positional arguments but 6 were given`: the `type_ann` field is missing from `Let`.

### Step 4b: Walk the AST with a Type Environment

The checker walks the AST once, maintaining a type environment that mirrors your `Environment` class (a table from names to declared types, with a parent link for nested blocks), and verifies three things:

- Literals and variables.  Every literal has its constant type; every variable use looks up the declared type; a `let` whose initializer's type disagrees with its annotation is an error.
- Operators.  Arithmetic operators require `Num` operands; comparison operators yield `Bool`; mixed-type operands are rejected naming *both* types.
- Operators whose static rule is yours to set.  `and`/`or` and the conditions of `if` and `while` are where the strictness decision above becomes concrete.  Requiring `Bool` is the simpler rule and the one the lab's skeleton assumes.  Allowing any type, and letting truthiness decide at run time, keeps every program your evaluator can run.  Either is defensible; pick one, apply it to all four places, and record it.
- Call sites.  Every function call checks arity and each argument's type against the parameter annotations, and the call expression takes the declared return type; a function whose body cannot produce its declared return type is an error.

Create `typechecker.py`, starting from your Type Checker Starter lab code, and shape it around this skeleton.  Then write one ill-typed program per bullet above (three files) and one well-typed program, and add each to `test_interpreter.py`.

**You write:** `typechecker.py` - `TypeEnv.define`, `TypeEnv.lookup`, and one `check` branch per node class; three ill-typed programs, one well-typed program, and their tests in `test_interpreter.py`
**You run:** the two `python3 -c` commands below the hint table

Your lab's names may differ from the skeleton's: `TypeEnvironment` for `TypeEnv`, or separate `check_stmt` and `check_expr` functions.  Keep whichever you have, provided `mylang.py` can call one function on the whole tree.

```python
from ast_nodes import *
from interpreter import LangTypeError
class TypeEnv:
    """Mirrors Environment, but maps names to declared type names."""
    def __init__(self, parent=None):
        self._types = {}
        self._parent = parent
    # TODO: define(name, typ) and lookup(name), same shape as Environment
def check(node, tenv=None):
    """Return the type of an expression node; check a statement node and return None."""
    if tenv is None:
        tenv = TypeEnv()
    if isinstance(node, Num):
        return "Num"
    # TODO: Str -> "Str", BoolLit -> "Bool", Var -> tenv.lookup(...)
    # TODO: BinOp: arithmetic needs Num operands; comparisons yield Bool
    # TODO: LogicOp and UnaryOp("not") need Bool
    # TODO: Let: check the initializer against type_ann, then tenv.define
    # TODO: Block: check statements in TypeEnv(parent=tenv)
    # TODO: call sites: arity, argument types, declared return type
```

| `# TODO` | How to write it |
|---|---|
| `define` and `lookup` | Copy `Environment.define` and `Environment.lookup`, with `_types` in place of `_bindings`.  For a name that no scope declares, `lookup` returns `None`, an unknown type; the note below the table explains why. |
| `Str`, `BoolLit`, `Var` | `return "Str"` and `return "Bool"`.  `Var` returns `tenv.lookup(node.name)`. |
| `BinOp` | Check both sides first: `lt, rt = check(node.left, tenv), check(node.right, tenv)`.  For `+ - * /` and `< <= > >=`, raise when `(lt, rt) != ("Num", "Num")`, with a message naming both, such as `f"'{node.op}' requires Num operands, got {lt} and {rt}"`.  Arithmetic returns `"Num"` and comparisons return `"Bool"`.  `==` and `!=` need `lt == rt` and return `"Bool"`.  If your evaluator concatenates strings, let `+` accept two `"Str"` and return `"Str"`. |
| `LogicOp` and `not` | Check each operand, and require `"Bool"` if you chose the strict rule above.  Return `"Bool"`.  While you are here, unary `-` needs `"Num"` and returns `"Num"`. |
| `Let` | `actual = check(node.value, tenv)`.  If `node.type_ann` is set and differs from `actual`, raise naming both.  Then `tenv.define(node.name, node.type_ann or actual)`, so an unannotated `let` takes its initializer's type. |
| `Block` | `inner = TypeEnv(parent=tenv)`, then a `for` loop calling `check(stmt, inner)`.  `Program` is the same loop, run in `tenv` itself.  The statements without a TODO line need branches too: `Assign` (the new value's type must equal the declared one), `Print` (check the expression), `If` and `While` (check the condition, then each branch or body), and `Break` and `Continue` (nothing to check).  Statements `return None`. |
| call sites | Only if your language has functions.  The core grammar on this page has none, so say that in your readme and leave this TODO as a comment. |

**A name with no declared type.**  An undeclared variable is a Run-stage error.  The checker treats a name that no scope declares as an *unknown* type: `lookup` returns `None`, and every rule skips its check when a side is `None`.  The evaluator then reports the name with `LangNameError`, as it does now, so Step 5a's `LangNameError` stays visible through `mylang.py`.  If you did the Type Checker lab, your checker already works this way.

```bash
python3 -c "from parser import parse; from typechecker import check; check(parse('let x: Num = 42;')); print('ok')"
python3 -c "from parser import parse; from typechecker import check; check(parse('let x: Num = \"hi\";'))"
```

> **You should see.** `check(parse('let x: Num = 42;'))` returns without error, and `check(parse('let x: Num = "hi";'))` raises `LangTypeError`.  The first command prints `ok`.  The second ends in a traceback whose last line names both types, such as:
>
> ```text
> interpreter.LangTypeError: line 1, col 1: 'x' is declared Num but its initializer is Str
> ```

> **If it fails.**
> - `NotImplementedError: no typing rule yet for Program`: `check` is handed the whole tree, so it needs a `Program` branch.
> - A rule compares against `None`, such as `'+' requires Num operands, got Num and None`: a branch fell off the end without a `return`, or `lookup` returned `None` and the rule did not skip it.
> - `let x: Num = 1; { let x: Str = "a"; } x = 2;` is rejected at the `x = 2`: your `Block` branch defines into `tenv` instead of `inner`, so the inner `Str` replaced the outer `Num`.

### Step 4c: Report Positioned Errors and Add the Stage

Report every rejection as `Type error at line L, col C: ...`, naming both conflicting types (declared vs. actual, or left vs. right operand), so make every `raise` in `typechecker.py` carry the node's line and col and both types.  Your file runner gains a fourth stage label, and a program that fails the check never runs: in `mylang.py`, call `check(tree)` between parsing and evaluation in both `run_file` and `repl`, catching `LangTypeError` and printing `Type error at line L, col C: <message>`.  Then run an ill-typed program with `python3 mylang.py badtype.ml`.

**You write:** `typechecker.py` - `node.line, node.col` on every `raise`; `mylang.py` - the Type stage in `run_source`; `badtype.ml`
**You run:** `python3 mylang.py badtype.ml`

Both `run_file` and `repl` go through `run_source`, so the Type stage is one new `try` there, between the other two:

```python
from interpreter import Interpreter, LangError, LangTypeError, BreakSignal, ContinueSignal
from typechecker import check

def run_source(source, interp):
    """Run one program through every stage.  Return None, or one staged error line."""
    # ... the parse stage from Step 3a ...
    # TODO: check(tree), catching LangTypeError -> "Type error at line L, col C: ..."
    # ... the evaluate stage from Step 3a ...
```

| `# TODO` | How to write it |
|---|---|
| the Type stage | Its own `try: check(tree)` with `except LangTypeError as err:` returning `f"Type error at line {err.line}, col {err.col}: {err.message}"`.  Place it after the parse `try` and before the evaluate `try`.  Because it returns, `eval_node` never runs on a rejected tree. |
| positions on every `raise` | Expression nodes carry `line` and `col`, so pass `node.line, node.col`.  `If` and `While` carry only a `line`, so report a bad condition at the condition's own position, `node.condition.line, node.condition.col`. |

Save this as `badtype.ml`.  Its error is on the last line, after a `print` that would run if the check were interleaved with evaluation:

```text
let total: Num = 10;
print total;
let label: Str = "items";
print total + label;
```

> **You should see.** One `Type error at line L, col C: ...` line naming both types, and no program output at all, since the Type stage fires before the Run stage.  Keep this staged output; the rubric asks for it.  If the program prints output and then a type error, the check is running interleaved with evaluation; it must finish over the whole tree before `eval_node` is called.  With the hints above, the one line is:
>
> ```text
> Type error at line 4, col 13: '+' requires Num operands, got Num and Str
> ```
>
> Run `python3 mylang.py shadow.ml` again, too.  A well-typed program passes through the new stage unchanged, so it still prints `51` and then `2`.

> **If it fails.**
> - `10` prints before the Type error: `check` runs inside or after evaluation.  It must finish before `eval_node` starts.
> - `Type error at line 0, col 0`: a `raise` in `typechecker.py` is missing the node's position.
> - The REPL transcript from Step 3b changes, and an undefined name now stops at the Type stage: your `TypeEnv.lookup` still raises for a missing name.  Return `None` instead, as the Step 4b note says, and the transcript stays exactly as Step 3b shows it.

---

## Part 5: Making the Semantics Precise, Choose Your Direction

Parts 1-4 give your language a working evaluator and a static checking stage.  Part 5 makes its semantics *precise*, in your choice of **direction**.  You complete one Part 5 and submit one deliverable, and the same rubric row applies equivalently to each.

| Direction | What you build | Pick this if |
|-----------|----------------|--------------|
| **Staged errors and SEMANTICS.md** (the core direction) | The language-level error hierarchy and a document stating every dynamic rule with an example, as Steps 5a-5c below scaffold it | You want the most direct path to a complete semantics reference for your team project |
| **Full type inference (Hindley-Milner)** | Part 4's annotation checker grown into whole-program *inference* that deduces types with no annotations at all, the way Haskell, OCaml, and Rust do.  See the [typing direction](#part-5-direction-full-type-inference-hindley-milner) | You enjoyed Part 4 and want the unification machinery behind modern type systems |
| **The Intcode VM** | A *virtual machine* that executes a flat list of numeric opcodes, the model behind CPython's bytecode, the JVM, and WebAssembly, implemented as the [Advent of Code 2019 Intcode](https://adventofcode.com/2019/day/2) machine and specified opcode by opcode.  See the [Intcode direction](#part-5-direction-a-contrasting-execution-model-the-intcode-vm) | You want to have built both dominant execution models and to say precisely how they differ |

> **On choosing.**  The three directions are graded equivalently, but they are not equal in size.  The core direction is the smallest of the three and the most directly reusable, because `SEMANTICS.md` is the document your team project will be reading all term.  The typing and Intcode directions are each roughly half again as much work, and both are worth it if the subject is what you want to spend that time on.  If this window is tight for you, take the core direction without hesitation; it is a first-class choice, not a fallback.

In every direction, Step 5a's error hierarchy is required (lexical, syntax, and name errors still need staged reporting; in the Intcode direction, malformed programs and illegal opcodes are staged errors), and the control-flow theory questions from Step 2b go in your readme.  The two alternative directions replace Steps 5b and 5c (SEMANTICS.md and the differential programs) with their own sections below: the typing direction with the inference engine, and the Intcode direction with the VM, where the self-checking AoC inputs are your oracle and a required differential test pins your VM's arithmetic against your tree-walker's.  Whichever direction you choose, the goal is the same: for every construct in your language (or VM), there is exactly one written answer to "what does this mean, and what happens when it is misused?", and your implementation agrees with it.

### Step 5a: Define the Error Class Hierarchy

Define a hierarchy of language-specific exceptions at the top of `interpreter.py`.  Step 2a already put it there, so this step is an audit rather than a rewrite: confirm your classes match the ones below.  Then search `interpreter.py` for every `raise` and confirm each one uses one of these classes with a message that names the variables, types, or operators involved, and passes the node's line (and col where you store it).  Add one test per error class to `test_interpreter.py`, each asserting the class raised and that the message names the offending variable, type, or operator, and confirm `python3 mylang.py` reports each one with its stage label and position in the format Step 3a requires.

**You write:** `interpreter.py` - the audited hierarchy and every `raise`; `test_interpreter.py` - one test per error class
**You run:** `python3 -m pytest test_interpreter.py`, then `python3 mylang.py` on each error program

```python
class LangError(Exception):
    def __init__(self, message, line=0, col=0):
        self.message = message
        self.line = line
        self.col = col
        super().__init__(str(self))
    def __str__(self):
        return f"line {self.line}, col {self.col}: {self.message}"
class LangNameError(LangError): pass
class LangTypeError(LangError): pass
class LangZeroDivisionError(LangError): pass
class LangRuntimeError(LangError): pass
```

The `super().__init__(str(self))` line makes this the same class the Environments lab wrote, so you have one definition, not two.  It also stores the message as the exception's `args`, the way Python's own exceptions do.

Here is the first test as a model; the other three are yours:

```python
from interpreter import LangNameError, LangTypeError, LangZeroDivisionError
from mylang import run_source

def test_undefined_variable_names_the_variable():
    with pytest.raises(LangNameError) as info:
        Interpreter().eval_node(parse("print missing;"))
    assert "missing" in info.value.message
    assert info.value.line == 1

# TODO: one test each for LangTypeError, LangZeroDivisionError, and LangRuntimeError
```

| `# TODO` | How to write it |
|---|---|
| `LangTypeError` | Evaluate `parse('print "a" - 1;')` inside `pytest.raises(LangTypeError)`, and assert that both `"str"` and `"int"` appear in `info.value.message`. |
| `LangZeroDivisionError` | `print 1 / 0;`, with the same shape.  Assert on `info.value.line` as well. |
| `LangRuntimeError` | Your evaluator never raises this one itself; a stray `break` becomes it in `run_source`.  So test the message instead: `assert run_source("break;", Interpreter()) == "Runtime error at line 1: 'break' outside loop"`. |

Then check the staged reporting end to end.  Step 3a's four error files, Step 4c's `badtype.ml`, and one new file cover every class.  Save `badname.ml` as the one line `print missing;`.

> **You should see.** One line per file, each with its stage label.  With the hints on this page, the two new runs print:
>
> ```text
> $ python3 mylang.py badtype.ml
> Type error at line 4, col 13: '+' requires Num operands, got Num and Str
> $ python3 mylang.py badname.ml
> Runtime error at line 1: Undefined variable 'missing'
> ```
>
> The other four files print exactly what Step 3a showed.  If `badname.ml` stops at the Type stage instead, your `TypeEnv.lookup` still raises for a missing name; return `None`, as the Step 4b note says.

> **If it fails.**
> - An `except LangNameError` does not catch the error your `Environment` raises: there are two copies of the class, one from the lab's `environment.py` and one in `interpreter.py`.  Delete one and import the other.
> - `Runtime error at line 0`: some `raise` passes no position.  The usual culprit is the `Environment`, whose errors must be re-raised with the node's position, as in Steps 2a and 2c.
> - `ImportError: cannot import name 'run_source' from 'mylang'`: your file runner keeps the stages inside `run_file`.  Test the stray `break` through `run_file` instead, or move the stages into a helper as Step 3a does.

### Step 5b: Write SEMANTICS.md

Write `SEMANTICS.md` with one `##` section per topic below, in this order.  Each section must include a statement of the rule in one or two sentences, a code example in your language, and the expected output (or error message).

1.  **Truthiness**: what values are falsy?  What are truthy?  Show a `while` loop that relies on numeric truthiness, and state what your Part 4 checker does with that same program.  If your checker requires `Bool` conditions, the program is rejected before it runs, and the honest answer is that your language's static and dynamic halves disagree by design: say so, show the staged `Type error`, and name the programs that disagreement costs you.  If your checker allows any type there, show the loop running and say what you gave up to allow it.
2.  **Division by zero**: what error is raised?  What stage identifies it?  Show the exact error message format.
3.  **Scoping and shadowing**: where does `let` define?  Where does bare assignment update?  Show the shadowing program and its output.
4.  **Loop-variable persistence**: does the loop variable remain in scope after the loop body?  Show a program whose output depends on this decision.
5.  **Assignment vs. definition**: what error does assigning an undefined variable produce?  Show it.
6.  **Type strictness**: can you add an int to a float?  A string to a number?  Show both cases and their outcomes.
7.  **String concatenation**: is `"a" + "b"` legal?  What about `"a" + 1`?  State the rule and show examples.

Run every example with `python3 mylang.py` and paste the real output; do not type it from memory.  If the program and the prose disagree, one of them is wrong, and Step 5c is where you settle it.

**You write (in `SEMANTICS.md`, one `##` heading per topic above):** a rule, an example program, and its real output, seven times
**You run:** `python3 mylang.py <example>.ml` for each example program

Every section has the same three parts.  Here is section 3 filled in, as a model of the shape and the length.  The other six sections follow it.

```text
## 3. Scoping and shadowing

Rule: `let` creates a new binding in the current block's scope, even when
an outer scope already has that name.  A bare assignment updates the
nearest existing binding, wherever it lives, and never creates one.

Example (shadow.ml):

    let x = 2;
    {
        let x = 51;
        print x;       # prints 51
    }
    print x;           # prints 2

Output of `python3 mylang.py shadow.ml`:

    51
    2
```

> **If it fails.**
> - An example's real output differs from your rule: decide which one is wrong before you change either.  Step 5c's differential programs exist to settle exactly this.
> - An example stops at the Type stage before it can show the behavior: either show the Type error as the answer (section 1 asks for this), or add annotations so the program passes the checker and reaches the Run stage.

### Step 5c: Run the Differential Programs

[Five programs are provided]({{ site.baseurl }}/files/starters/interpreter/differential/), in `files/starters/interpreter/differential/`, whose outputs depend on your semantics decisions.  Each one names the `SEMANTICS.md` section it probes in a header comment, and between them they touch all seven.  Run each with `python3 mylang.py <program>` and record its output.  Confirm that each output matches your SEMANTICS.md documentation; if it does not, fix either the code or the documentation, since they must agree.  Add the five programs and their recorded outputs to `test_interpreter.py`, each traceable to a specific rule in SEMANTICS.md.

**You write:** `differential/` - copy the five programs into your project; `test_interpreter.py` - one test per program
**You run:** `for f in differential/*.ml; do echo "== $f"; python3 mylang.py "$f"; done`

These programs probe *decisions*, so there is no single right output.  For comparison, here is what they print when every decision follows the hints on this page.  Those choices are: the minimum truthiness rule, Python's true division, `==` false across types, `+` on two strings, a per-iteration loop scope, a checker that requires `Bool` conditions, and unknown names left to the Run stage.

```text
== differential/01-truthiness.ml
Type error at line 15, col 7: condition of 'while' must be Bool, got Num
== differential/02-division-and-numbers.ml
3.0
2.0
3.5
true
Runtime error at line 13: division by zero
== differential/03-scope-and-shadowing.ml
51
2
outer=shadowed
Runtime error at line 20: Cannot assign to undefined variable 'never_defined'
== differential/04-loop-scope.ml
3
Runtime error at line 14: Undefined variable 'inner'
== differential/05-strings.ml
Type error at line 13, col 16: '+' requires Num operands, got Str and Num
```

Wherever your output differs, find the decision that caused it, and check that `SEMANTICS.md` states that decision.  To pin an output in a test, run the program the way a user would and compare what it prints.  Here is one, as a model:

```python
import subprocess, sys

def mylang_output(path):
    """Run a program through mylang.py as a user would; return what it prints."""
    result = subprocess.run([sys.executable, "mylang.py", path],
                            capture_output=True, text=True)
    return result.stdout

def test_differential_02_division_and_numbers():
    # SEMANTICS.md sections 2 (Division by zero) and 6 (Type strictness)
    assert mylang_output("differential/02-division-and-numbers.ml").splitlines() == [
        "3.0", "2.0", "3.5", "true", "Runtime error at line 13: division by zero"]

# TODO: the other four programs, each naming the SEMANTICS.md section it probes
```

| `# TODO` | How to write it |
|---|---|
| the other four programs | Copy `test_differential_02_...` four times.  Change the file name, the section comment, and the expected list, pasting each list from your real run, never from this page. |

> **If it fails.**
> - The expected list is missing only the error line: your `mylang.py` prints its errors to `sys.stderr`.  Read `result.stderr` as well, or print errors to standard output.
> - The test sees an empty list, but the program works by hand: pytest is running from another folder, so Python cannot find `mylang.py` (the complaint is in `result.stderr`).  Run pytest from the project folder.

---

## Part 5 Direction: Full Type Inference (Hindley-Milner)

{: #part-5-direction-full-type-inference-hindley-milner}

This direction replaces Steps 5b-5c.  You grow Part 4's annotation checker into whole-program *inference*: still its own pipeline stage after parsing and before evaluation, but now deducing types where no annotations exist at all, with the same unification and Algorithm-W-style machinery that lets Haskell, OCaml, and Rust do it.  Part 4's type environment, staged error reporting, and operator rules all carry forward.  What changes is that unknown types become type *variables* to be solved rather than gaps to be documented.  A **type** is one of three things: a type variable `α, β, ...` (unknown, to be solved), a type constant (`Num`, `Bool`, `Str`), or, if your checker covers functions, a function type `τ₁ -> τ₂`.  A substitution maps type variables to types.  Unification of two types finds the most general substitution that makes them equal, or fails, and that failure *is* the type error.  The inference algorithm walks the AST, generates fresh type variables constrained by each node's structure, and unifies to solve them.

> **What this direction requires.** `hm_types.py` (T.1), `typecheck.py` (T.2), positioned type errors (T.3), and `TYPES.md` with its accepted and rejected test programs (T.4), in place of `SEMANTICS.md` and the differential programs.  Step 5a is still required.

### Step T.1: Type Terms, Substitution, and Unification (`hm_types.py`)

Create `hm_types.py` in the project folder from the skeleton below.  Define frozen dataclasses `TVar(name)` and `TCon(name)` (and `TFun(param, ret)` if you cover functions), with `apply(subst, typ)` and `free_vars(typ)` helpers.  Implement `unify(t1, t2, subst) -> subst`:

1.  Apply the current substitution to both types.  If they are now identical, return the substitution unchanged.
2.  If one is a type variable `α` that does not occur in the other, extend the substitution with `{α: other}`.  The **occurs check** (refusing to bind `α` to a type containing `α`) is what prevents infinite types.  Raise a `LangTypeError` naming both types if it fires.
3.  Recurse componentwise on matching constructors.  Otherwise raise a `LangTypeError` naming both conflicting types.

**You write:** `hm_types.py` - `TVar`, `TCon`, `apply`, `free_vars`, and `unify`, plus three tests in `test_interpreter.py`
**You run:** `python3 -m pytest test_interpreter.py`

> **Watch out.** Python's standard library already has a module named `types`, and `dataclasses` imports it.  That is why this file is named `hm_types.py`.  A file named `types.py` in your project folder would hide the real one, so `from dataclasses import dataclass` would fail with `ImportError: cannot import name 'MappingProxyType' from 'types'`, and pytest would fail to start.

```python
from dataclasses import dataclass
from interpreter import LangTypeError
@dataclass(frozen=True)
class TVar:
    name: str             # a type variable, e.g. "a"
@dataclass(frozen=True)
class TCon:
    name: str             # a type constant: "Num", "Bool", or "Str"
TNum, TBool, TStr = TCon("Num"), TCon("Bool"), TCon("Str")
def apply(subst, typ):
    # TODO: replace every TVar bound in subst, recursively
    ...
def free_vars(typ):
    # TODO: the set of TVar names appearing in typ
    ...
def unify(t1, t2, subst):
    # TODO: the three rules above; return the extended substitution
    ...
```

Add these tests to `test_interpreter.py`, at minimum: `unify(TVar("a"), TNum, {})` binds `a`; unifying `TNum` with `TBool` raises; and an occurs-check case raises.  If the occurs-check test hangs, you have found the infinite type it exists to prevent; add the check before the bind.

### Step T.2: Inference over Your AST (`typecheck.py`)

Create `typecheck.py` (it may grow out of Part 4's `typechecker.py`; keep whichever file name you document) and implement `infer(node, type_env, subst) -> (subst, type)` structured like `eval_node`: one `isinstance` branch per node type your evaluator handles, each returning the new substitution and the node's type, with the substitution threaded through every case.

- Literals return their constant type.
- `Var` looks up the type environment (undefined names remain `LangNameError`s).
- Arithmetic operators unify both operands with `Num` and return `Num`.
- Comparisons return `Bool`.
- `LogicOp` and `not` unify with `Bool`.
- `If` and `While` conditions must be `Bool`.  Note that this is *stricter* than your dynamic truthiness rule; see the reflection prompt.
- `Let` extends the type environment.
- `Assign` unifies the new value's type with the variable's existing type.
- `Block` checks its statements in a child type environment that mirrors your `Environment` scoping.

**You write:** `typecheck.py` - `fresh` and `infer`; `mylang.py` - the `--typed` flag
**You run:** `python3 mylang.py --typed shadow.ml`

```python
from ast_nodes import *
from interpreter import LangNameError, LangTypeError
from hm_types import TVar, TCon, TNum, TBool, TStr, apply, unify
from typechecker import TypeEnv          # reuse Part 4's scope chain

_count = 0
def fresh():
    """Return a type variable that no other part of the program uses."""
    global _count
    _count += 1
    return TVar(f"t{_count}")

def infer(node, type_env, subst):
    """Return (subst, type) for an expression, or (subst, None) for a statement."""
    if isinstance(node, Num):
        return subst, TNum
    # TODO: one isinstance branch per node type eval_node handles, threading subst
    #       through every recursive call:  subst, t = infer(child, type_env, subst)
    raise NotImplementedError(f"no inference rule yet for {type(node).__name__}")
```

Wire it into `mylang.py` as a stage: `python3 mylang.py --typed program.ml` (or make it the default; document your choice) lexes, parses, **type-checks**, and only then evaluates.  The stage label `Type error` keeps the staged-error format of Step 4c: `Type error at line L, col C: <message>`.  Run `python3 mylang.py --typed shadow.ml` and confirm it still prints `51` then `2`: a well-typed program must pass through the new stage unchanged.

One way to read the flag, replacing the last two lines of `mylang.py`:

```python
if __name__ == "__main__":
    args = sys.argv[1:]
    typed = "--typed" in args                  # Step T.2: run infer before evaluation
    paths = [a for a in args if a != "--typed"]
    # TODO: pass typed into run_file and run_source, and call infer there when it is set
    run_file(paths[0]) if paths else repl()
```

### Step T.3: Positioned Type Errors

Every type error must name both conflicting types, cite the source line, and give a short context, in the spirit of:

```text
Type error at line 7: condition of 'if' must be Bool, got Num
Type error at line 12: '+' requires Num operands, got Str and Num
Type error at line 5: cannot unify Num with Bool (from assignment to 'result')
```

Give every `LangTypeError` raised from `unify` and `infer` the line of the node being checked and a context phrase naming the construct.  Write three programs, one per message above, and confirm each produces one positioned line naming both types and no program output.

**You write:** `typecheck.py` - a line and a context phrase on every `LangTypeError`; three ill-typed programs
**You run:** `python3 mylang.py --typed <program>.ml` on each of the three

### Step T.4: TYPES.md and Test Programs

**You write (in `TYPES.md`, one `##` heading per construct):** a typing rule, one accepted program, and one rejected program, with the checker's real output for each; five test programs and their tests in `test_interpreter.py`
**You run:** `python3 mylang.py --typed <program>.ml` for each program, then `python3 -m pytest test_interpreter.py`

In place of SEMANTICS.md, write `TYPES.md`: one `##` section per construct your `infer` covers, stating its typing rule in prose (or inference-rule notation), with one program the checker accepts and one it rejects, showing the checker's real output for each.  Include at least five test programs total: three that the checker rejects with distinct positioned errors, and two that pass the checker and then run correctly, showing that well-typed programs still evaluate as before.  Add the five to `test_interpreter.py`, asserting the three rejections by message and the two acceptances by evaluated output.

**Depth (part of "proficient"):** if your language grows function values in the team project (or if you simply want the full Milner experience), implement let-polymorphism.  Generalize a let-bound name's type over the type variables not free in the environment, and instantiate fresh copies at each use, so a polymorphic identity function can be applied to both a `Num` and a `Bool` in the same scope.  Self-application (`f(f)`) must still be rejected: no finite type satisfies it, and your occurs check is what says so.

---

## Part 5 Direction: A Contrasting Execution Model, the Intcode VM

{: #part-5-direction-a-contrasting-execution-model-the-intcode-vm}

A tree-walker is one way to run a program; a **virtual machine** is another.  Instead of recursing over an AST, a VM holds the program as a flat array of integers and steps a program counter through them, decoding one instruction at a time.  This is the model underneath CPython's bytecode, the JVM, and WebAssembly, and Advent of Code 2019's Intcode is the smallest complete instance of it worth studying.  Its operational semantics is small enough to write down completely, which is what makes it a legitimate "make the semantics precise" direction: every opcode is one state-transition rule over the machine state `(memory, pc, input, output, relative_base)`.

> **What this direction requires.** `INTCODE.md` with a transition rule per opcode (I.1), `intcode.py` (I.2), the AoC checkpoint outputs in your readme (I.3), and the tree-walker-vs-VM differential test in `test_interpreter.py` (I.4), in place of `SEMANTICS.md` and the differential programs.  Step 5a is still required.

### Step I.1: Write the Operational Semantics (`INTCODE.md`)

Before you write code, write `INTCODE.md`: a section on the machine state, a section per opcode with its rule as a transition on that state, a section on parameter modes, and a section on illegal opcodes and out-of-range addresses.

**You write (in `INTCODE.md`, one `##` heading per opcode, plus machine state, parameter modes, and illegal opcodes):** the transition rules.  No code yet.

For example, opcode 1 (add):

```text
add: with parameters a, b, c, set mem[c] <- value(a) + value(b), then pc <- pc + 4.
```

Cover opcodes `1` (add), `2` (multiply), `3` (input), `4` (output), `5` (jump-if-true), `6` (jump-if-false), `7` (less-than), `8` (equals), and `99` (halt), plus the **parameter modes** (0 = position, 1 = immediate, and, for the full machine, 2 = relative, with opcode `9` adjusting the relative base).  State what an unknown opcode does: it is a staged error (`LangRuntimeError`), not a crash.  Write the rules before `intcode.py` exists; the document is the specification your VM must agree with, not a description written afterward.  You end with nine opcode rules (ten with opcode `9`), each stating what is read, what is written, and how `pc` changes.

### Step I.2: Build the VM (`intcode.py`)

Create `intcode.py` in the project folder from the skeleton below and implement `run(program, inputs) -> outputs` as an opcode dispatch loop.  Decode each instruction as `opcode = instr % 100` and the per-parameter modes from the higher digits.  Structure the dispatch so that adding an opcode is a localized change (a dict from opcode to a small handler, or a match statement), the same "one construct, one place" discipline as your tree-walker's visitor.  Illegal opcodes and out-of-range addresses raise your Step 5a error classes with a position (the `pc` at fault).

**You write:** `intcode.py` - `run(program, inputs)`
**You run:** `python3 -c "from intcode import run; p=[1,9,10,3,2,3,11,0,99,30,40,50]; run(p, []); print(p[0])"`

```python
from interpreter import LangRuntimeError
def run(program, inputs):
    """Execute an Intcode program; return the list of outputs."""
    mem = program                # the program is its own memory; run in place
    pc = 0                       # (copy it first if you prefer, and say so in INTCODE.md)
    outputs = []
    inputs = list(inputs)
    while True:
        instr = mem[pc]
        opcode = instr % 100
        # TODO: decode parameter modes from instr // 100
        # TODO: dispatch on opcode (dict of handlers or match statement)
        # TODO: opcode 99 -> return outputs
        # TODO: unknown opcode -> raise LangRuntimeError(f"illegal opcode {opcode}", line=pc)
        ...
```

Run the Day 2 sample:

```bash
python3 -c "from intcode import run; p=[1,9,10,3,2,3,11,0,99,30,40,50]; run(p, []); print(p[0])"
```

> **You should see.** `3500`: the sample program halts with that value in position 0.  If you see `1`, the program was never modified, so either the add handler is writing somewhere else or `run` is working on a copy without returning it.

### Step I.3: Check the VM against the AoC Oracle

Intcode is self-validating: the puzzle inputs come with known answers.  Include at least these checkpoints, each as a test in `test_interpreter.py` asserting the exact expected output, and each recorded with its output in your `readme.md`.

**You write:** `test_interpreter.py` - one test per checkpoint, plus the illegal-opcode test; `readme.md` - each checkpoint's output
**You run:** `python3 -m pytest test_interpreter.py`

The checkpoints:

- The Day 2 sample programs (e.g., `1,9,10,3,2,3,11,0,99,30,40,50` halts with `3500` in position 0).
- A Day 5 program exercising input, output, immediate mode, and a jump/comparison (e.g., "is the input equal to 8?").
- If you implement relative mode + opcode 9, the Day 9 quine (`104,1125899906842624,99`) which must output its own large constant.

Add a test that an illegal opcode raises `LangRuntimeError` with the `pc` at fault, as a staged, positioned error rather than an `IndexError` or `KeyError`.

### Step I.4: Differential Test against Your Tree-Walker (Required)

The two execution models must agree where they overlap.  Write a differential test: for a handful of integer arithmetic expressions, evaluate each **both** with your Part 2 tree-walker and with an equivalent hand-assembled Intcode program, and assert that the results match.  Show each Intcode program's assembly in the test so a reader can check the correspondence.  In your readme, name one thing the VM makes easy that the tree-walker makes hard (or vice versa), e.g., self-modifying code, or explicit control over evaluation order.

**You write:** `test_interpreter.py` - the differential test, with each program's assembly in comments
**You run:** `python3 -m pytest test_interpreter.py`

Here is one case as a model.  It computes `(2 + 3) * 4` both ways.  The Intcode program keeps its data after the `99`, where the machine never executes it:

```python
from intcode import run as run_intcode

def test_vm_agrees_with_tree_walker_on_add_then_multiply():
    interp = Interpreter()
    interp.eval_node(parse("let r = (2 + 3) * 4;"))
    program = [
        1, 13, 14, 15,      # 0: add  mem[15] <- mem[13] + mem[14]    (2 + 3)
        2, 15, 16, 15,      # 4: mul  mem[15] <- mem[15] * mem[16]    (... * 4)
        4, 15,              # 8: out  mem[15]
        99,                 # 10: halt
        0, 0,               # 11-12: unused
        2, 3, 0, 4,         # 13-16: data: 2, 3, the result slot, 4
    ]
    assert run_intcode(program, []) == [interp.globals.lookup("r")]

# TODO: a handful more, e.g. one with subtraction (add a negative immediate) and one with nesting
```

> **Scope note.** This direction is warm-up-scale by design.  The VM is a couple hundred lines and its correctness is externally checkable, so your effort goes into the *precise semantics* and the *model comparison*, which is what the 14-point Part 5 rubric rewards.

---

## Deliverables

Submit a ZIP containing:

| File or artifact | What it shows | Rubric row |
|------------------|---------------|------------|
| `interpreter.py` | The evaluator, Environment class, and error hierarchy (importing `lexer.py` and `parser.py` unchanged; note any fixes) | Parts 1, 2, 5 |
| `mylang.py` | The entry point: file runner and REPL (Part 3), with the Type stage from Part 4 | Parts 3, 4 |
| `typechecker.py` | The small static type checker | Part 4 |
| `SEMANTICS.md` | The language semantics document | Part 5 |
| `test_interpreter.py` | Test suite with the shadowing program, the bomb test, all error-class tests, the differential programs, and the required Step 2e Hypothesis invariant tests | Parts 2, 4, 5 |
| `repl_transcript.txt` | The REPL session showing each error class and recovery | Part 3 |
| `readme.md` | Approximately one page connecting the interpreter to the pipeline and the team project; the control-flow theory questions; the Step 2e report; any reference-component declaration; your Python version | Parts 2, 5 |

**Typing direction:** substitute `hm_types.py`, `typecheck.py`, and `TYPES.md` (with its accepted/rejected test programs) for `SEMANTICS.md` and the differential programs.  Everything else on the list is unchanged, and the REPL transcript also demonstrates one positioned type error.

**Intcode direction:** substitute `intcode.py` and `INTCODE.md` (with the per-opcode transition rules) for `SEMANTICS.md` and the differential programs.  Add the AoC checkpoint outputs and the tree-walker-vs-VM differential test to `test_interpreter.py`.  Everything else on the list is unchanged.

Every direction includes the required Step 2e Hypothesis invariant tests in `test_interpreter.py`.  Ensure reproducibility by listing your Python version.

---

## Self-Check Before You Submit

- [ ] Every node type from Step 1a is a dataclass with annotated, commented fields, and `Var`, `BinOp`, `UnaryOp`, `Let`, and `Assign` carry positions.
- [ ] The shadowing program prints `51` then `2`, and the bomb test passes without evaluating its right side.
- [ ] Every runtime error is a Step 5a class raised at the language level with stage and position, and type errors name both operand types.
- [ ] At least four Hypothesis invariants (determinism, scope restoration, short-circuit non-evaluation, and at least one more) are in `test_interpreter.py`, and the readme reports a shrunk counterexample or a reasoned all-clear.
- [ ] The REPL keeps its environment across an error, and `repl_transcript.txt` shows every error class and recovery.
- [ ] The file runner prints a stage label (`Lexical`, `Syntax`, `Type`, `Runtime`) in every error message, and the Type stage fires before any code runs.
- [ ] The Part 5 deliverable for your direction is complete (`SEMANTICS.md` and the differential programs, or `hm_types.py` + `typecheck.py` + `TYPES.md`, or `intcode.py` + `INTCODE.md` with the AoC checkpoints and the differential test), and the control-flow theory questions are answered in the readme.
- [ ] The readme lists your Python version and any reference component you used.

---

## Reflection Prompts

- Which semantics decision did you change after testing revealed a consequence you had not foreseen?
- Point to the exact line in your `Environment` class that makes your language statically (lexically) scoped rather than dynamically scoped.
- Typing direction only: your dynamic truthiness rule accepts `while 1 { ... }`, but your type checker demands a `Bool` condition.  Where else did the static discipline reject a program your evaluator would have happily run, and which behavior do you consider correct for your language?
- The `BreakSignal`/`ContinueSignal` pattern uses exceptions for control flow, a technique the course calls "signal exceptions."  What property of exceptions makes them well suited for this, and what would you use instead if exceptions were not available?
