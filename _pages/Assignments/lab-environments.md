---
layout: assignment
permalink: /Assignments/EnvironmentsLab
title: "CS374: Principles of Programming Languages - Lab: Environments and Type Checking"

info:
  coursenum: CS374
  purpose: "To build the scope table your interpreter uses for nested scopes, and then to reuse that same table to check a program's types before it runs, individually or with a partner."
  tilt:
    task: "Individually or with a partner, fill in the define, lookup, and assign methods of a provided Environment class, then fill in the type rules for literals, variables, binary operators, and if and while conditions in a provided checker that stores types in that same Environment."
    criteria: "I grade a scope table and a checker that pass the eleven provided tests, a short prediction of a scope trace made before you run it, and four typing rules written on paper.  The full breakdown is in the rubric below."
  points: 30
  goals:
    - To implement a scope table with parent chaining that supports nested scopes and shadowing
    - To distinguish definition (creating a name in the current scope) from assignment (updating the nearest enclosing binding)
    - To reuse the same scope table to check types before a program runs, with positioned errors that name both conflicting types
    - To state typing rules precisely and connect each rule to the code that enforces it
  rubric:
    - weight: 35
      description: "Part 1: The Scope Table (Goals 1, 2)"
      preemerging: define, lookup, and assign are missing, or lookup never consults an enclosing scope
      beginning: lookup walks the chain, but define and assign are conflated, so an inner assignment creates a new binding instead of updating the outer one
      progressing: define and assign are distinguished and shadowing works, but assigning to an undefined name does not raise LangNameError, or a test among 1 through 6 still fails
      proficient: define writes only into the current scope, lookup walks the chain to any depth, assign updates the nearest enclosing binding and raises LangNameError naming the variable when no binding exists, and tests 1 through 6 all pass
    - weight: 15
      description: "Part 1: Predicting the Scope Trace (Goal 2)"
      preemerging: No predictions are written, or they were written after the run
      beginning: Predictions are written, but more than two of the six are wrong and no miss is explained
      progressing: All six predictions are written before the run, and each miss is noted, but at least one explanation does not name the rule that was misapplied
      proficient: All six predictions are written before the run, and every miss is explained by naming the rule misapplied (define versus assign, or the scope where a lookup starts)
    - weight: 35
      description: "Part 2: The Type Rules (Goal 3)"
      preemerging: The type rules are missing, or the checker never rejects an ill-typed program
      beginning: Literals and variables are typed, but the operator rules are missing or crash on programs they should reject
      progressing: Every rule is present, but an error message lacks its position or names only one of the two types, or a test among 7 through 11 still fails
      proficient: Literals, variables, binary operators, and if and while conditions are checked through the Part 1 scope table, an undeclared name is treated as unknown, every error names its line, column, and both types, and tests 7 through 11 all pass
    - weight: 15
      description: "Part 2: Typing Rules on Paper (Goal 4)"
      preemerging: No rules are written, or they contradict the checker
      beginning: Rules are written for literals only
      progressing: Rules cover all four constructs, but at least one rule leaves out a premise the code checks
      proficient: Each of the four constructs has a precise rule (premises above a line and the conclusion below it, or a disciplined if-then sentence), and each rule names the function in scope_lab.py that enforces it
  readings:
    - rtitle: "Binding, Scope, and Environments Activity"
      rlink: "Activities/liascript-bindingscope.md"
      liapage: true
    - rtitle: "Type Systems Activity"
      rlink: "Activities/liascript-types.md"
      liapage: true
    - rtitle: "Core Tutorial: Typing Disciplines, Strong vs. Weak, Static vs. Dynamic, and Gradual Typing"
      rlink: "../Tutorials/TypingDisciplines"

tags:
  - interpreter
  - scope
  - types
  - languages
  - lab

---

In this lab you build one data structure and use it twice.  The data structure is a **scope table**: a class named `Environment` that maps names to what they mean, one table per block of code, with each table pointing to the block that encloses it.  In Part 1 the table maps names to *values*, which is exactly what your interpreter needs to run a program with nested blocks.  In Part 2 the same class maps names to *types*, and you use it to check a program before it runs.  The class does not change between the parts, because scope rules and type rules walk the same chain.

You start from a provided file, `scope_lab.py`.  Every class, error, and function in it is already written and documented, except for seven method bodies marked `TODO`.  A provided test file checks your work, and its eleven tests turn from `FAIL` to `ok` one at a time as you finish each method.  Your `Environment` goes into the Interpreter assignment's Step 2c, and your checker is the starting point for its Part 4.

> **Time budget.**  About three hours: about an hour and a half on Part 1 (fifteen minutes on the worked example, forty-five minutes on the three methods, and twenty minutes predicting the trace), and about an hour and a half on Part 2 (fifteen minutes on the worked example, an hour on the four rules, and fifteen minutes writing them on paper).  See the course schedule for the assigned and due dates.

**Pair policy.**  You may do this lab in pairs.  You each submit the same files, name each other in them, and earn the same grade.  You may also work alone.  The Interpreter assignment remains individual work: you may both carry this shared `scope_lab.py` into it, but the evaluator and the checker extensions you write there must be your own.

---

## Before You Start

You need:

- Python 3.10 or newer, and a terminal you can run `python3` from.  On Windows, if `python3` is not found, use `python` wherever this page says `python3`.  If the terminal is new to you, read the [Dev Environment tutorial]({{ site.baseurl }}/Tutorials/DevEnvironment) and the [Shell for Language Development primer]({{ site.baseurl }}/Tutorials/ShellForLanguageDev) first; both are short.
- The two provided files: the starter [scope_lab.py]({{ site.baseurl }}/files/starters/environments/scope_lab.py) and the tests [test_scope_lab.py]({{ site.baseurl }}/files/starters/environments/test_scope_lab.py).
- The two readings listed above.  Part 1 uses the vocabulary of the *Binding, Scope, and Environments* activity, and Part 2 uses the vocabulary of the *Type Systems* activity.

**You write:** nothing yet.
**You run:** `python3 test_scope_lab.py`

> **Do this.**
> 1. Make a folder named `cs374-scopes`, and download both provided files into it.
> 2. Create one more file by hand, `notes.md`, with your name (and your partner's) at the top.  It holds the two pieces of paper work: your trace predictions in Step 1.4 and your typing rules in Step 2.5.  A photo of a paper page is fine in either place.
> 3. From inside the folder, run the tests once on the untouched starter.

```bash
mkdir cs374-scopes
cd cs374-scopes
python3 --version
python3 test_scope_lab.py
```

> **You should see.**  Eleven tests, each marked `FAIL`, and no crash.  Each failure says which method is not written yet, such as `not written yet: define still raises NotImplementedError`.  The last line reads `FAILED (failures=11)`.  That list is your to-do list, in order.

This table shows where each step's work goes:

| Step | File you work in | What you do there | Tests that should pass afterward |
|---|---|---|---|
| 1.1 | (reading) | follow the worked lookup and predict one result | none yet |
| 1.2 | `scope_lab.py` | write `define` and `lookup` | 1, 2, 3 |
| 1.3 | `scope_lab.py` | write `assign` | 1 through 6 |
| 1.4 | `notes.md` | predict the trace program's six printed values, then run it | 1 through 6 |
| 2.1 | (reading) | follow the worked check of `1 + true` | 1 through 6 |
| 2.2 | `scope_lab.py` | type literals and variables in `check_expr` | 1 through 8 |
| 2.3 | `scope_lab.py` | type the binary operators in `check_expr` | 1 through 10 |
| 2.4 | `scope_lab.py` | write `check_condition` | all 11 |
| 2.5 | `notes.md` | write the four typing rules | all 11 |

You never edit `test_scope_lab.py`, and you never need to change any code in `scope_lab.py` outside the seven `TODO` bodies.

---

## Part 1: The Scope Table

An `Environment` is one scope: a table of bindings for one block, plus a link to the scope that encloses it.  In Python, one `Environment` object holds exactly two things:

| On paper | In Python | Example value |
|---|---|---|
| the box of bindings for one scope | `self._bindings`, a `dict` from name to value | `{'x': 2, 'y': 10}` |
| the arrow to the enclosing scope | `self._parent`, another `Environment` | the outer scope's object |
| the end of the chain (the top level has no arrow) | `self._parent is None` | `None` |
| "is `x` bound in this box?" | `name in self._bindings` | `True` or `False` |
| "follow the arrow and ask again" | the same method, called on `self._parent` | whatever the outer scope answers |

You write three methods, and two of them have the same shape: check this scope, else ask the parent, else raise.

- `define(name, value)` creates `name` in *this* scope.  It shadows (hides) any outer binding of the same name.
- `lookup(name)` returns the value of the nearest binding of `name`.  If no scope in the chain has it, it raises `LangNameError`.
- `assign(name, value)` updates the nearest binding of `name`.  It never creates a binding.  If no scope has the name, it raises `LangNameError`.

The difference between `define` and `assign` is the most important idea in this part.  `define` writes into this scope no matter what any parent holds.  `assign` never writes into this scope unless the name is already here.

### Step 1.1: Follow One Worked Lookup

Here is a program with one block, written as calls on the class.  A `let` is a `define`.  Entering a block makes a new `Environment` whose parent is the current one.

```python
outer = Environment()               # the top-level scope
outer.define("x", 2)                # let x = 2;
outer.define("y", 10)               # let y = 10;
inner = Environment(parent=outer)   # {   enter a block
inner.define("x", 51)               #     let x = 51;
inner.lookup("y")                   #     ... y ...
```

Let's trace the last call, `inner.lookup("y")`, one scope at a time:

| Call | Scope it checks | Is `y` there? | What happens |
|---|---|---|---|
| `inner.lookup("y")` | `inner`, holding `{'x': 51}` | no | `inner` has a parent, so it returns `outer.lookup("y")` |
| `outer.lookup("y")` | `outer`, holding `{'x': 2, 'y': 10}` | yes | it returns `10` |

The answer is `10`, and it travels back through `inner.lookup` unchanged.  Notice that the lookup stopped at the first scope that had the name.  That is all shadowing is: `inner.lookup("x")` stops at `inner` and never sees the outer `x`.

**You write (in `notes.md`, optional):** your answer to the prediction below.  It is not graded.

> **Predict.**  What does `inner.lookup("z")` do, and how many scopes does it check before it stops?

### Step 1.2: Write define and lookup

**You write:** `scope_lab.py` - the bodies of `define` and `lookup`.
**You run:** `python3 test_scope_lab.py`

> **Do this.**
> 1. Open `scope_lab.py` and find the `Environment` class.
> 2. Replace the `raise NotImplementedError("define")` line with the one line the comment describes.
> 3. Replace the `raise NotImplementedError("lookup")` line with the three steps its comment describes.  Give the `LangNameError` a message that contains the name, such as `Undefined variable 'y'`.
> 4. Run the tests.

| Method | How to think about it |
|---|---|
| `define` | One write into this scope's dictionary, indexed by the name.  No `if`, and no mention of the parent. |
| `lookup`, step 1 | Test membership with `name in self._bindings`, not `.get`.  The `.get` method returns `None` both for a missing name and for a name bound to `None`, and test 2 binds a name to `None` on purpose. |
| `lookup`, step 2 | Test the parent with `self._parent is not None`, then `return self._parent.lookup(name)`.  If you leave out `return`, the parent's answer is thrown away. |
| `lookup`, step 3 | You reach this only when the name is not here and there is no parent.  Pass only the message to `LangNameError`; `line` and `col` default to zero. |

> **You should see.**  Tests 1, 2, and 3 marked `ok`, and tests 4 through 11 still marked `FAIL`.  The last line reads `FAILED (failures=8)`.

> **If it fails.**
> - `RecursionError: maximum recursion depth exceeded`: `lookup` called `self.lookup` instead of `self._parent.lookup`, so it asks the same scope the same question forever.
> - `AttributeError: 'NoneType' object has no attribute 'lookup'`: `lookup` asked the parent without checking that there is one.
> - Test 2 fails on `a name bound to None still counts as bound`: you used `.get` instead of `in`.

### Step 1.3: Write assign

**You write:** `scope_lab.py` - the body of `assign`.
**You run:** `python3 test_scope_lab.py`

> **Do this.**
> 1. Replace the `raise NotImplementedError("assign")` line with the three steps its comment describes.
> 2. Give the `LangNameError` a message that contains the name, such as `Cannot assign to undefined variable 'nope'`.
> 3. Run the tests.

| Step | How to think about it |
|---|---|
| step 1 | The same membership test as `lookup`.  Overwrite the value in this scope's table, then stop, so you do not also hand the job to the parent. |
| step 2 | Hand the whole job, name and value, to `self._parent.assign`.  The parent runs the same three steps on its own table. |
| step 3 | Raise.  This path must never write into this scope's table. |

> **You should see.**  Tests 1 through 6 marked `ok`.  Test 6 runs the shadowing program from the Interpreter assignment and checks that it prints `51`, then `2`, then `11`.  The last line reads `FAILED (failures=5)`, because Part 2 has not started.

> **If it fails.**
> - Test 4 fails on `assign created a new y in the inner scope`: your `assign` wrote into `self._bindings` when the name was not there.  That is the define-versus-assign bug.
> - Test 5 fails with a `KeyError` in the message: `assign` indexed a dictionary instead of raising `LangNameError`.

> **Watch out.**  The Interpreter assignment's Step 5a defines the same `LangError` classes in `interpreter.py`.  When you carry your `Environment` into that assignment, keep one copy of the error classes, not two.  With two copies of `LangNameError`, an `except LangNameError` in the evaluator can miss the one your `Environment` raises.

### Step 1.4: Predict the Scope Trace, Then Run It

The provided test file includes a program of three nested blocks that mixes `define` and `assign`.  Predict what it prints before you run it.  This is the graded paper work for Part 1.

```text
let x = 1;               # step 1
let y = 10;              # step 2
{                        # step 3   enter block A
    let x = 2;           # step 4   define: shadows the outer x
    y = y + x;           # step 5   assign: no let, so it updates an existing y
    {                    # step 6   enter block B
        x = x * 10;      # step 7   assign
        let z = y;       # step 8   define
        {                # step 9   enter block C
            let y = 0;   # step 10  define: shadows an outer y
            z = z + x;   # step 11  assign
            print y;     # step 12
        }                # step 13  leave block C
        print x;         # step 14
        print z;         # step 15
    }                    # step 16  leave block B
    print x;             # step 17
}                        # step 18  leave block A
print x;                 # step 19
print y;                 # step 20
```

**You write (in `notes.md`, under a heading `Step 1.4`):** your six predicted values, then, after the run, one sentence for each value you missed.
**You run:** `python3 test_scope_lab.py --trace`, only after your predictions are written.

> **Do this.**
> 1. Work through the program by hand.  At each `let`, add the name to the innermost open block.  At each assignment, find the nearest block that already has the name and change it there.
> 2. Write the six values that `print` produces, in order (steps 12, 14, 15, 17, 19, and 20).
> 3. Run the trace.  It runs the tests first, then the program through your class, one line per step, ending with the six printed values.
> 4. For each value you missed, write one sentence naming the rule you misapplied: define versus assign, or which scope a lookup starts in.

> **You should see.**  The eleven test results, then twenty numbered steps.  Each step shows the line, the chain of scopes from the innermost outward (such as `A{x=2} -> top{x=1, y=10}`), and what the line did.  The last six lines are the printed values.  The trace starts like this:
>
> ```text
> Step 1.4 trace program:
> step  1  let x = 1;   top{x=1}                                       define x=1
> step  2  let y = 10;  top{x=1, y=10}                                 define y=10
> ```
>
> If a Part 1 test still fails, the script prints `Finish Part 1 (tests 1 to 6) before running the trace program.` instead.

---

## Part 2: Type Checking with the Same Table

A **static type checker** reads a program's abstract syntax tree (AST) and decides whether each operation makes sense, before any of the program runs.  It never computes a value.  It remembers *types* instead: `x` is a `Num`, `s` is a `Str`.

A type checker needs to know, at each point in the program, what type each name has.  That is a scope question, with the same answer as in Part 1: look in this block, then in the enclosing blocks.  So the checker stores types in your Part 1 `Environment`.  After `let x: Num = 1;`, the checker's table holds `{'x': 'Num'}`.  Inside a block that declares `let x: Str = "hi";`, the inner table holds `{'x': 'Str'}`, and the outer `x` is still a `Num`.  You get shadowing for free.

The starter already has most of the checker:

- `LangTypeError`, whose message reads `Type error at line L, col C: ...`.
- A small copy of the class AST, with the same node and field names as the `ast_nodes.py` the activities build.  `Let` has an extra field, `annotation`, that holds the declared type name.
- `check(program)`, which makes the top-level table and checks each statement.
- `check_stmt`, already complete.  It checks a `let` against its annotation and defines the name's type in the current table.  It opens a new child table for each block.  It sends each `if` and `while` condition to `check_condition`.

You write four rules, in the order the tests check them:

| Rule | Where | What it says |
|---|---|---|
| literals | `check_expr` | a `Num` is `Num` (written for you as the model), a `Str` is `Str`, a `BoolLit` is `Bool` |
| variables | `check_expr` | a `Var` has the type its nearest declaration gave it; a name no scope declares has the **unknown** type, `None` |
| binary operators | `check_expr` | `+ - * /` need two `Num`s and give `Num`; `< <= > >=` need two `Num`s and give `Bool`; `== !=` need two equal types and give `Bool` |
| conditions | `check_condition` | the condition of an `if` or a `while` must be `Bool` |

One rule covers all four: **if either type a rule compares is `None`, the rule skips its check** and still returns its usual result type.  An unknown type comes from a name nobody declared.  The checker cannot prove anything about it, so it leaves that name to the evaluator, which reports `Undefined variable` when the program runs.

### Step 2.1: Follow One Worked Check

Let's check `let x: Num = 1 + true;`.  The `+` sits at line 1, column 16.  In the AST, that line is a `Let` whose value is `BinOp("+", Num(1), BoolLit(True))`.

| Call | What it does | Result |
|---|---|---|
| `check_stmt(Let(...), tenv)` | types the initializer before it binds `x` | calls `check_expr` on the `BinOp` |
| `check_expr(BinOp("+", ...), tenv)` | types the left operand | `Num` |
| | types the right operand | `Bool` |
| | `+` is arithmetic, so both operands must be `Num`; the right one is not | raises `LangTypeError` at the `BinOp`'s line and column |

The error stops the check before `x` is ever defined, and long before anything runs.  The message names the operator and *both* operand types:

```text
Type error at line 1, col 16: '+' requires Num operands, got Num and Bool
```

> **Predict.**  What should the checker do with `let x: Num = 1 + y;` when no `let` declares `y`?  Find the rule above that answers it.

### Step 2.2: Type Literals and Variables

**You write:** `scope_lab.py` - two literal branches and the variable branch in `check_expr`.
**You run:** `python3 test_scope_lab.py`

> **Do this.**
> 1. In `check_expr`, under the literals `TODO`, add a branch for `Str` and a branch for `BoolLit`.  Copy the shape of the `Num` branch above them.
> 2. Under the variables `TODO`, add a branch for `Var`.  Look `node.name` up in `tenv`.  Catch `LangNameError` and return `None`.
> 3. Run the tests.

| Branch | How to think about it |
|---|---|
| literals | Test the class with `isinstance` and return a type constant.  A literal needs nothing from `tenv`.  Keep every branch above the final `raise`, or the `raise` runs first. |
| `Var` | `tenv` is your Part 1 `Environment`, so `tenv.lookup(node.name)` walks the chain for you and returns the declared type.  Your `lookup` raises `LangNameError` for a missing name.  Here a missing name is not an error; it is the unknown type, so catch the error and return `None`. |

> **You should see.**  Tests 1 through 8 marked `ok`, and `FAILED (failures=3)` on the last line.  Test 8 also checks that, after `let x: Num = 1;`, the table's `_bindings` is exactly `{'x': 'Num'}`.  That is your Part 1 class holding a type.

> **If it fails.**
> - `not written yet: no typing rule yet for Str`: the branch sits below the final `raise`, tests the wrong class, or has no `return`.
> - Test 8 fails on `an undeclared name has the unknown type None`: the `Var` branch let the `LangNameError` escape.  Catch it.

### Step 2.3: Type the Binary Operators

**You write:** `scope_lab.py` - the `BinOp` branch in `check_expr`.
**You run:** `python3 test_scope_lab.py`

> **Do this.**
> 1. Under the binary operators `TODO`, add a branch for `BinOp`.  Type the left operand and the right operand by calling `check_expr` on each.
> 2. If either type is `None`, skip the check and return the operator's result type.
> 3. Otherwise, pick the rule by the operator's family.  The starter names the three families: `ARITHMETIC`, `COMPARISON`, and `EQUALITY`.
> 4. When the check fails, raise `LangTypeError(message, node.line, node.col)`.  For arithmetic and comparison, use a message such as `'+' requires Num operands, got Num and Bool`.  For equality, use `'==' requires operands of the same type, got Num and Str`.
> 5. Run the tests.

| Family | Needs | Gives |
|---|---|---|
| `ARITHMETIC`: `+ - * /` | `Num` and `Num` | `Num` |
| `COMPARISON`: `< <= > >=` | `Num` and `Num` | `Bool` |
| `EQUALITY`: `== !=` | two equal types, whatever they are | `Bool` |

Put the two types you *found* in the message, not the type you expected.  Then the message names both types even when only one of them is wrong.

> **You should see.**  Tests 1 through 10 marked `ok`, and `FAILED (failures=1)` on the last line.

> **If it fails.**
> - Test 9 fails on `must sit at the operator's position`: you raised at an operand's position.  Use `node.line` and `node.col` of the `BinOp`.
> - Test 10 fails on `two Strs may be compared with ==`: the equality family is falling into the `Num` check.  Test for `EQUALITY` first.
> - A message names only one type: format both `left` and `right` into it.

### Step 2.4: Check if and while Conditions

**You write:** `scope_lab.py` - the body of `check_condition`.
**You run:** `python3 test_scope_lab.py`

> **Do this.**
> 1. Type the condition with `check_expr`.
> 2. If the type is known and is not `BOOL`, raise `LangTypeError` at the *condition's* `line` and `col`.  Name the keyword and the type, such as `while condition must be Bool, got Num`.
> 3. Run the tests.

The `If` and `While` nodes store only a `line`, with no `col`.  Every expression node has both, which is why the error goes at the condition.  `check_stmt` already checks the branches and the loop body after it calls `check_condition`.

> **You should see.**  All eleven tests marked `ok`, ending in:
>
> ```text
> Ran 11 tests in 0.004s
>
> OK
> ```
>
> The time may differ on your machine.

Your evaluator has a truthiness rule, so `while 1 { ... }` means something when it runs.  The checker is stricter on purpose and rejects it.  The first reflection prompt asks you whether that is the right call.

### Step 2.5: Write the Four Typing Rules on Paper

A **typing rule** has premises (what must already be true about the parts) and a conclusion (what then holds for the whole).  Writing the rule after the code is deliberate.  The code tells you what you enforced, and the rule tells you whether that is what you meant.

**You write (in `notes.md`, under a heading `Step 2.5`):** one rule each for literals, variables, binary operators, and conditions, each followed by the name of the function in `scope_lab.py` that enforces it.  No new code.

The rule for `+` can be written either way.  In inference-rule layout, premises go above the line and the conclusion below it:

```text
e1 : Num    e2 : Num
--------------------
   e1 + e2 : Num
```

As a sentence: *if `e1 : Num` and `e2 : Num`, then `e1 + e2 : Num`*.

> **Do this.**
> 1. Write one rule per construct.  For binary operators, one rule per family is enough.  For variables, say where the type comes from and what happens when no scope declares the name.
> 2. Under each rule, name the function that enforces it, such as "`check_expr`, the `BinOp` branch."
> 3. Check each rule against its code.  If the code checks a premise the rule leaves out, or the rule states one the code does not check, fix whichever is wrong.

---

## Deliverables

Submit a ZIP containing the files below, with your name (and your partner's, if you worked in a pair) at the top of `notes.md`.

| File | What it shows | Rubric row |
|---|---|---|
| `scope_lab.py` | `define`, `lookup`, and `assign`; the literal, variable, operator, and condition rules | Part 1: The Scope Table; Part 2: The Type Rules |
| `test_output.txt`, made with `python3 test_scope_lab.py > test_output.txt 2>&1` (or a screenshot) | all eleven tests passing | Part 1: The Scope Table; Part 2: The Type Rules |
| `notes.md`, Step 1.4 | six predictions written before the run, and one sentence per miss | Part 1: Predicting the Scope Trace |
| `notes.md`, Step 2.5 | four typing rules, each naming the function that enforces it | Part 2: Typing Rules on Paper |

If you did any of the optional extensions below, include that work too, and say which ones in `notes.md`.  They earn no points, and I am glad to talk about them with you.

---

## Self-Check Before You Submit

- [ ] `python3 test_scope_lab.py` ends in `OK`, and `test_output.txt` holds that run.
- [ ] `define` writes only into the current scope, and `assign` never creates a binding.
- [ ] `assign` and `lookup` raise `LangNameError` (not `KeyError`) for a name no scope has, with the name in the message.
- [ ] The checker looks variables up in the Part 1 `Environment`, and an undeclared name is unknown (`None`), not an error.
- [ ] Every type error names its line, its column, and both conflicting types.
- [ ] `notes.md` has six trace predictions written before the run, a sentence for each miss, and four typing rules that each name their function.
- [ ] Your name, and your partner's if you worked in a pair, is at the top of `notes.md`.

---

## Reflection Prompts

- What is the observable difference, in one example program, between a language where assignment creates bindings and one where it only updates them?
- Your checker rejects `while 1 { ... }`, though the evaluator's truthiness rule would happily run it.  Which behavior do you consider correct for the class language, and why?
- If you worked in a pair, who did what, and name one thing your partner caught that you would have missed.  If you worked alone, note that instead.

---

## Optional Extensions (no points)

Everything below is optional, earns no points, and is not part of the time budget.  These sections go deeper into both halves of the lab: paper traces of lexical and dynamic scope, worked models of type systems, the remaining type rules, and running the checker on real source files from your own parser.  Several of them prepare you for the Interpreter assignment's Part 4, so they are worth a look when you get there.  Where a section asks for written answers, put them in `notes.md` under the section's name.

### Extension A: Trace Binding and Scope on Paper

Do this on paper; you may do it alone even if you did the rest of the lab with a partner.  Put your answers in `notes.md` under this section's name (a photo of the paper is fine).  Two terms first.  Under lexical scope, a name refers to the binding in the enclosing text of the program.  Under dynamic scope, a name refers to the most recent binding made by any caller that is still running.

#### A.1: Trace the Shadowing Expression

Evaluate this expression by hand, drawing the environment at each step.  The inner binding of `x` shadows (hides) the outer one.

**You write (in `notes.md` under A.1):** the lexical trace table and the final value.  No code.

```text
let x = 2 in let x = x + 1 in x * x
```

> **Do this.**
> 1. Copy the table below into `notes.md` (or draw it on paper).  Step 1 is done for you as a model.
> 2. Fill in the chain and the result at every step.  Write chains innermost-first, each scope a box of bindings with an arrow to its parent, like `E1{x=2} -> E0{}` (`E0` is the empty top-level scope).  A drawn picture of boxes and arrows is just as good.
> 3. Write the final value of the whole expression under the table.

| Step | Expression being evaluated | Environment chain (lexical) | Result |
|------|----------------------------|-----------------------------|--------|
| 1 | `let x = 2 in ...` binds the outer `x` | `E1{x=2} -> E0{}` | scope `E1` entered |
| 2 | `x + 1`, evaluated inside `E1` | | |
| 3 | `let x = <step 2 result> in ...` binds the inner `x` | | |
| 4 | `x * x`, evaluated inside the inner scope | | |
| 5 | the inner `let` ends, then the outer `let` ends | | |

#### A.2: Predict It Under Dynamic Scope

**You write (in `notes.md` under A.2):** the dynamic trace table and the step where the two tables first differ.  No code.

> **Do this.**
> 1. Copy the same table again, headed "Environment chain (dynamic)", and fill it in under the dynamic rule.
> 2. Mark the exact step where the two tables first give different results.  If every row agrees for this expression, say so, and say what a program would have to contain before the two rules could disagree.

#### A.3: Decide the Unbound-Variable Behavior

**You write (in `notes.md` under A.3):** your two-line expression, its trace, and one sentence naming the error and the moment it fires.  No code.

> **Do this.**
> 1. Write a two-line expression of your own that uses an unbound variable, a name no environment in the chain defines (for example, an outer `let` that binds `x` and a body that mentions `y`).
> 2. Trace it the same way, and stop at the step where the chain runs out.
> 3. Decide what error the evaluator should raise (name the class) and at what moment.  The class you built in Part 1 raises `LangNameError` for a missing name, so name that class unless you can argue for another; the moment is the real decision.  The choices are: when the program is read, when the enclosing `let` is entered, or when the lookup of the name actually runs.  Write the error and the moment as one sentence in `notes.md`.  Decide this now rather than let Python decide for you.

#### A.4: Write Two Probe Programs for the Mystery Scoping Language

In class you will run programs against an interpreter whose scoping rule is hidden and deduce the rule from the answers.  A probe program is one whose output differs depending on whether the language is lexically or dynamically scoped, so a program that prints the same thing under both rules tells you nothing.  Here is the shape of a probe, in pseudocode: a function reads a name it did not bind, and it is called from a place that rebinds that name.  This one is mine, so it does not count toward your two.

```text
let x = 1;
fun show() { print x; }      # show reads x but does not bind it
fun caller() {
    let x = 2;               # rebinds x, then calls show
    show();
}
caller();
```

**You write (in `notes.md` under A.4):** two probe programs and four predictions, one per program per rule.  No code.

> **Do this.**
> 1. Write two short programs of your own whose output differs depending on the scoping rule.  Make one of them as short as you can.
> 2. For each program, write your prediction of what it prints under each rule: one line for lexical, one line for dynamic.
> 3. If both predictions for a probe match, it cannot tell the rules apart, so change it.

> **Have ready.** Both probe programs and all four predictions.  Run them against the Mystery Scoping Language interpreter in Part II of the *Binding, Scope, and Environments* activity.

### Extension B: The Full Trace Table

Step 1.4 asked only for the six printed values.  This extension traces the same program one row per step, and then runs it by hand through your class.

#### B.1: Fill In the Trace Table Before You Run Anything

**You write (in `notes.md` under B.1):** the 20-row trace table.  No code.

> **Do this.**
> 1. Copy the table below into `notes.md`, one row per numbered step, and fill in every row from the rules, not by running code.  Step 1 is done for you as a model.
> 2. Draw each chain innermost-first, as in the trace output, naming the scopes `top`, `A`, `B`, and `C`.  In the Result column write the value printed (for a `print` step), the binding created or changed and in which scope (for a `let` or assignment step), or "enter" and "leave" for the braces.
> 
| Step | Line | Environment chain | Result |
|------|------|-------------------|--------|
| 1 | `let x = 1;` | `top{x=1}` | `x=1` created in `top` |
| 2 | `let y = 10;` | | |
| ... | one row per step, through step 20 `print y;` | | |

#### B.2: Run the Program Through Your Class and Compare

You do not have an evaluator yet, so translate each step into a call on your class.  This is a preview of exactly what the Interpreter assignment's `Let`, `Assign`, `Block`, and `Var` cases will do.

**You write:** `trace_run.py` - one line of Python per step of the trace program, steps 1 through 20, except the three "leave block" steps.
**You run:** `python3 trace_run.py`, then compare with `python3 test_scope_lab.py --trace`.

Each scope gets its own variable, named after it: `top` for the top level, `a` for block A, `b` for block B, and `c` for block C.  Each line calls a method on the variable for the scope that step runs in, the innermost block you are in at that moment.  The worked example in Step 1.1 already uses most of the calls you need.

> **Do this.**
> 1. Create `trace_run.py` next to `scope_lab.py`.  Import `Environment` with `from scope_lab import Environment`, and make `top`, the program's top-level scope, with no parent.
> 2. Work down the listing one step at a time, starting at step 1.  For each step, decide which of the five kinds in the table below it is.
> 3. Decide which scope the step runs in: the innermost block still open at that moment.  That scope's variable is the one you call the method on.
> 4. Write the one line for that step.  End it with a comment holding the step number and the original line, so you can match your lines against the `--trace` output later.
> 5. For the three "leave block" steps (13, 16, and 18), write only a comment.  Leaving a block takes no call: from that step on, your lines use the parent's variable instead.
> 6. Run `python3 trace_run.py` and compare the six printed values with your predictions.  For any step where your prediction missed, write one sentence in `notes.md` naming the rule you misapplied (define versus assign, or which scope a lookup starts in).

Every step of the program is one of five kinds:

| Kind of step | How to think about it |
|---|---|
| `{` (enter a block) | Make a new `Environment` whose parent is the variable of the block you are in now, and give it the new block's name.  Step 3 makes `a` inside `top`; step 6 makes `b` inside `a`; step 9 goes one level deeper. |
| `let name = value;` (define) | A `let` is a `define` on the current scope, never on an outer one.  If the value is another variable, as in `let z = y;`, read that variable first with a `lookup` on the current scope. |
| `name = expression;` (assign) | No `let` means `assign`.  Build the new value from `lookup` calls on the current scope, then call `assign` on the current scope too.  Do not call it on the scope you think holds the name; walking the chain is the job of `assign`. |
| `print name;` | Print the result of a `lookup` on the innermost scope still open at that step. |
| `}` (leave a block) | No call at all.  Switch to the parent's variable for every line after it. |

> **You should see.** Six lines of output, one integer per line, one per `print`, in the order of steps 12, 14, 15, 17, 19, and 20.  They must match the last six lines of `python3 test_scope_lab.py --trace`, and each row of your table must match the chain column of that output.

> **If it fails.**
> - `NameError: name 'b' is not defined` (or `'c'`): a line uses a block's variable before the `(enter)` line that creates it.  Check that steps 6 and 9 come first and use the names `b` and `c`.
> - `LangNameError: line 0, col 0: Undefined variable 'z'`: a line after step 13 used a scope outside block B, where `z` lives.  Recheck which block is innermost at that step.
> - Your run and the `--trace` output disagree on a value: one of your lines used `define` where the program has no `let`, or called a method on the wrong block's variable.  Find the first step where your values differ from the `--trace` row.  Its chain column shows which scope holds each name, so check whether your line for that step should have created a binding or updated one.

### Extension C: Worked Models of Type Systems

This extension opens with a short paper exercise, then four worked models from the Type Systems class session: a runtime checker for the interpreter you are building, a trace of it on compound expressions, inference by hand, and a type-error postmortem.  Each model has a script you can run and questions to talk through (with your partner, if you have one).  They go further than Part 2 into what a type system buys and costs.

#### Type Systems on Paper

Plan on about fifteen minutes with pencil and paper.  Everyone has an opinion about static typing; an example is what makes the argument worth having.

**You write (at the top of `notes.md`, or on paper you photograph):** the annotated program, the rejected expression with your preference, and the guarantee and forbidden program.  No code.

> **Do this.**
> 1. Write a small program and annotate each subexpression with the type you expect it to have.
> 2. Find one expression in it that a static type checker would reject but a dynamic language would run.  Say which behavior you prefer there, and why.
> 3. State one guarantee a type system gives you, and one program it forbids that you wish it allowed.
> 4. Write your answers at the top of `notes.md`, or put a photo of your page in the ZIP.

> **Bring to class.**  The program you wish the checker had allowed, even if you could not settle the question.  The unsettled cases are the ones we argue about, and Part 2 made you take a side in code.

#### Model 1: A Dynamically, Strongly Typed Core

Your interpreter already evaluates binary expressions like `3.0 + 4.0`.  This model adds a gatekeeper at the top of that evaluation: before it touches the operands, it checks whether the combination makes sense and raises an error naming both types if it does not.  The language checks types at runtime and refuses silent coercion, the same choice Python makes.  Coercion is a conversion the language performs on its own, such as turning the number `5` into the string `"5"` so that it can be concatenated.  Refusing to coerce is what makes the typing *strong*; checking while the program runs, rather than before it starts, is what makes it *dynamic*.

**You write:** `model1_strong.py` - the script below, pasted as is.  It is not submitted.
**You run:** `python3 model1_strong.py`

> **Do this.**  Create `model1_strong.py` in your lab folder, paste the script below into it, and run `python3 model1_strong.py`.

```python
# Adding strong dynamic typing to the BinOp evaluator: check, then compute.

def type_name(v):
    return {bool: "bool", float: "number", str: "string"}.get(type(v), type(v).__name__)

def eval_binop(op, left, right):
    """Strong typing: refuse undefined mixtures with a located, specific error."""
    if op in ("+", "-", "*", "/"):
        if op == "+" and isinstance(left, str) and isinstance(right, str):
            return left + right                   # string concatenation: licensed
        if isinstance(left, bool) or isinstance(right, bool):
            raise TypeError(f"arithmetic on bool is not defined: "
                            f"{type_name(left)} {op} {type_name(right)}")
        if isinstance(left, float) and isinstance(right, float):
            if op == "+": return left + right
            if op == "-": return left - right
            if op == "*": return left * right
            if op == "/":
                if right == 0: raise ZeroDivisionError("division by zero")
                return left / right
        raise TypeError(f"operator {op!r} not defined for "
                        f"{type_name(left)} and {type_name(right)}")
    if op in ("<", "<=", ">", ">=", "==", "!="):
        if type(left) is not type(right):
            raise TypeError(f"cannot compare {type_name(left)} with {type_name(right)}")
        return {"<": left < right, "<=": left <= right, ">": left > right,
                ">=": left >= right, "==": left == right, "!=": left != right}[op]
    raise ValueError(f"unknown operator {op!r}")

print("=== Type Checking Results ===")
for l, op, r in [(3.0, "+", 4.0), ("ab", "+", "cd"), (3.0, "+", "cd"),
                 (True, "*", 2.0), (3.0, "<", "cd"), (3.0, "/", 0.0)]:
    try:
        result = eval_binop(op, l, r)
        print(f"  {l!r} {op} {r!r} = {result!r}")
    except (TypeError, ZeroDivisionError) as e:
        print(f"  {l!r} {op} {r!r} -> {type(e).__name__}: {e}")
```

> **You should see.**  Three passes and three refusals, each refusal naming both operand types.

```text
=== Type Checking Results ===
  3.0 + 4.0 = 7.0
  'ab' + 'cd' = 'abcd'
  3.0 + 'cd' -> TypeError: operator '+' not defined for number and string
  True * 2.0 -> TypeError: arithmetic on bool is not defined: bool * number
  3.0 < 'cd' -> TypeError: cannot compare number with string
  3.0 / 0.0 -> ZeroDivisionError: division by zero
```

Those refusals are the whole lab in miniature.  The checker you wrote in Part 2 produces the same kind of message, with two differences: it names a line and column, and it fires before the program runs rather than while it runs.

`type_name` turns a Python type into the name the error messages print.  The first `if` in `eval_binop` handles arithmetic: it allows string concatenation, refuses booleans, computes on two floats, and refuses everything else.  The second `if` handles comparisons, which require both sides to have the same type.

##### Critical Thinking Questions

1.  Identify the lines that make this typing *strong* (refusals) versus the line that would make it *weak* if you replaced a refusal with `float(...)` coercion.  Make the weak version mentally: what does `3.0 + "cd"` return, and what bug class did you just legalize?
2.  We licensed `+` for two strings but not `*` for string and number.  Python licenses `"ab" * 3`.  Debate and record your project's policy on string repetition, and add it to `SEMANTICS.md` (the Interpreter assignment's semantics document).
3.  Where would a *static* checker for your language live in the pipeline (between which two existing stages), and what would it walk?  You already own every data structure it needs; name them.

Python raises a TypeError on `"5" - 1` at the moment the subtraction executes, never silently converting.  On the two axes, is Python statically and weakly typed, statically and strongly typed, dynamically and strongly typed, or dynamically and weakly typed?

> **Answer.**  Dynamically and strongly typed.

A language that deduces `n: int` from `let n = 5` without requiring the programmer to write the type annotation is using dynamic typing, weak typing, type inference, or duck typing?

> **Answer.**  Type inference.

> **Watch out.**  Duck typing (Python's "if it walks like a duck and quacks like a duck, treat it as a duck") is still a form of typing: a dynamic, structural one, where compatibility is checked by whether an object supports the required operations rather than by its declared class.  Saying a language "has no types" because it uses duck typing is incorrect.

#### Model 2: Tracing the Runtime Checker on a Compound Expression

A dynamically typed interpreter never checks anything in advance; every check rides along with evaluation.  Values form at the literals and meet at each operator, and at each meeting point the gatekeeper from Model 1 checks the pair before combining them.  This model slows that to one step at a time, so you can see when each check fires and what has already happened by the time a check fails.

Evaluation is bottom-up (innermost first).  For `(3.0 + 4.0) < (2.0 * 6.0)` the checks fire at `+`, then `*`, then `<`: three checks, three passes, one final value.  The same trace for `(3.0 + 4.0) < ("total: " + 12.0)`:

| Step | Node evaluated | Left value : type | Right value : type | Check performed | Result |
|------|----------------|-------------------|--------------------|-----------------|--------|
| 1 | `3.0 + 4.0` | `3.0` : number | `4.0` : number | `+` licensed | `7.0` |
| 2 | `"total: " + 12.0` | `"total: "` : string | `12.0` : number | `+` **not** licensed for string, number | **TypeError** |
| 3 | `... < ...` | - | - | never reached | - |

Step 1 completed *before* the error, so its work cannot be undone, and the `<` at step 3 never runs.  That is dynamic checking in one picture: checks are interleaved with execution, so an error stops the program in flight rather than before takeoff.

**You write:** `model2_trace.py` - the script below, pasted as is.  It is not submitted.
**You run:** `python3 model2_trace.py`

> **Do this.**  Create `model2_trace.py` in your lab folder, paste the script below into it, and run `python3 model2_trace.py`.

```python
def type_name(v):
    return {bool: "bool", float: "number", str: "string"}.get(type(v), type(v).__name__)

STEP = 0

def evaluate(node):
    """Evaluate a tuple-AST bottom-up, narrating every type check."""
    global STEP
    kind = node[0]
    if kind == "lit":
        return node[1]
    op, left_node, right_node = node
    left  = evaluate(left_node)     # innermost first:
    right = evaluate(right_node)    # children are fully evaluated before we check
    STEP += 1
    print(f"  step {STEP}: {left!r} {op} {right!r}  "
          f"[{type_name(left)} {op} {type_name(right)}]", end="  ")
    if op in "+-*/":
        if isinstance(left, float) and isinstance(right, float):
            result = {"+": left + right, "-": left - right,
                      "*": left * right, "/": left / right}[op]
            print(f"check OK -> {result!r}")
            return result
        if op == "+" and isinstance(left, str) and isinstance(right, str):
            print(f"check OK -> {(left + right)!r}")
            return left + right
        print("check FAILS")
        raise TypeError(f"operator {op!r} not defined for "
                        f"{type_name(left)} and {type_name(right)}")
    if op == "<":
        if type(left) is not type(right):
            print("check FAILS")
            raise TypeError(f"cannot compare {type_name(left)} with {type_name(right)}")
        print(f"check OK -> {left < right}")
        return left < right
    raise ValueError(f"unknown operator {op!r}")

good = ("<", ("+", ("lit", 3.0), ("lit", 4.0)),
             ("*", ("lit", 2.0), ("lit", 6.0)))
bad  = ("<", ("+", ("lit", 3.0), ("lit", 4.0)),
             ("+", ("lit", "total: "), ("lit", 12.0)))

print("=== (3.0 + 4.0) < (2.0 * 6.0) ===")
print("final value:", evaluate(good))

print("\n=== (3.0 + 4.0) < ('total: ' + 12.0) ===")
STEP = 0
try:
    evaluate(bad)
except TypeError as e:
    print(f"stopped by TypeError: {e}")
```

> **You should see.**  Both traces, one step per line.  The first prints three `check OK` lines (`7.0`, `12.0`, `True`) and then `final value: True`.  The second prints `step 1: 3.0 + 4.0  [number + number]  check OK -> 7.0`, then `step 2: 'total: ' + 12.0  [string + number]  check FAILS`, then `stopped by TypeError: operator '+' not defined for string and number`.  Step 1 prints its result before step 2 fails.

```text
=== (3.0 + 4.0) < (2.0 * 6.0) ===
  step 1: 3.0 + 4.0  [number + number]  check OK -> 7.0
  step 2: 2.0 * 6.0  [number * number]  check OK -> 12.0
  step 3: 7.0 < 12.0  [number < number]  check OK -> True
final value: True

=== (3.0 + 4.0) < ('total: ' + 12.0) ===
  step 1: 3.0 + 4.0  [number + number]  check OK -> 7.0
  step 2: 'total: ' + 12.0  [string + number]  check FAILS
stopped by TypeError: operator '+' not defined for string and number
```

An interpreter with dynamic (runtime) checking evaluates `(3.0 + 4.0) < ("a" + 1.0)`.  When is the type error for `"a" + 1.0` detected: before execution begins, when the `<` comparison runs, at the moment the `+` on `"a"` and `1.0` is evaluated (after `3.0 + 4.0` has already computed), or never, because dynamic languages coerce automatically?

> **Answer.**  At the moment the `+` on `"a"` and `1.0` is evaluated, after `3.0 + 4.0` has already computed.

##### Critical Thinking Questions

4.  The trace shows the checks firing in steps 1, 2, 3, the same order as evaluation.  State the general rule: in a dynamically typed interpreter, when does the check for an operator fire, relative to the evaluation of that operator's operands?
5.  In the failing trace, step 1 finished before the TypeError at step 2.  Suppose step 1 had been `print("charging card...")` instead of an addition.  What does this tell you about *where in a program's lifetime* you would prefer type errors to fire, and which typing discipline delivers that?
6.  Redo the failing trace as a *static* checker would perform it, before execution: rewrite the table with types only, no values.  Which columns disappear, and which check still fails?
{: start="4"}

#### Model 3: Type Inference by Hand

Type inference is the trick where the checker works out every variable's type from context alone: you write `let a = 2` and it deduces `a: int` without you saying so.  Mechanically, it is a tree walk.  Visit each node, compute the type it must produce, and pass that type upward.  When two branches disagree (for example, adding an `int` to a `str`), the checker reports an error *at that node*, which can be far from the actual mistake.

The script below is a miniature of bottom-up type inference: it works out each `let` binding's type from its initializer, with no annotations.  It is not full Hindley-Milner inference, which adds type variables and unification so that it can also infer the types of function parameters; here every expression's type is fixed by its parts, so a single bottom-up walk is enough.  Each `if kind == ...` branch of `infer` is one typing rule, and the `let` branch is where the type environment grows.  This is the closest model to what you built in Part 2: your checker walks the same way and keeps the same kind of environment, but reads the type from the annotation on each `let` instead of deducing it from the initializer.

**You write:** `model3_infer.py` - the script below, pasted as is.  It is not submitted.
**You run:** `python3 model3_infer.py`

> **Do this.**  Create `model3_infer.py` in your lab folder, paste the script below into it, and run `python3 model3_infer.py`.

```python
# Mini type inference: propagate types through a simple expression AST

class TInt:   pass
class TFloat: pass
class TStr:   pass
class TBool:  pass

def type_str(t):
    return {TInt: "int", TFloat: "float", TStr: "str", TBool: "bool"}[type(t)]

def infer(expr, env):
    """Infer the type of an expression given a type environment (name -> type)."""
    kind, *args = expr
    if kind == "int":     return TInt()
    if kind == "float":   return TFloat()
    if kind == "str":     return TStr()
    if kind == "bool":    return TBool()
    if kind == "var":
        name = args[0]
        if name in env:   return env[name]
        raise TypeError(f"undefined variable {name!r}")
    if kind == "let":
        name, val_expr, body_expr = args
        val_type = infer(val_expr, env)
        new_env = dict(env, **{name: val_type})
        print(f"  let {name}: {type_str(val_type)}")
        return infer(body_expr, new_env)
    if kind == "add":
        lt = infer(args[0], env)
        rt = infer(args[1], env)
        if type(lt) == type(rt) and isinstance(lt, (TInt, TFloat)):
            return lt
        if isinstance(lt, TStr) and isinstance(rt, TStr):
            return TStr()
        raise TypeError(f"cannot add {type_str(lt)} and {type_str(rt)}")
    if kind == "lt":
        lt = infer(args[0], env)
        rt = infer(args[1], env)
        if type(lt) != type(rt):
            raise TypeError(f"cannot compare {type_str(lt)} with {type_str(rt)}")
        return TBool()
    raise ValueError(f"unknown expression kind {kind!r}")

# let a = 2; let b = a + 3; let c = b < 10; in c
program = ("let", "a", ("int",), ("let", "b", ("add", ("var", "a"), ("int",)),
           ("let", "c", ("lt", ("var", "b"), ("int",)), ("var", "c"))))
# let a = 2; a + "hello"        (a type error)
bad_program = ("let", "a", ("int",), ("add", ("var", "a"), ("str",)))

for title, prog in [("Type Inference Trace", program), ("Type Error Program", bad_program)]:
    print(f"=== {title} ===")
    try:
        print(f"Result type: {type_str(infer(prog, {}))}")
    except TypeError as e:
        print(f"Type error: {e}")
```

> **You should see.**  Under `=== Type Inference Trace ===`, the lines `let a: int`, `let b: int`, `let c: bool`, and `Result type: bool`.  Under `=== Type Error Program ===`, one line `let a: int` and then `Type error: cannot add int and str`.  No value is ever computed; only types move.

```text
=== Type Inference Trace ===
  let a: int
  let b: int
  let c: bool
Result type: bool
=== Type Error Program ===
  let a: int
Type error: cannot add int and str
```

Follow the environment through the good program.  It starts empty; `let a = 2` binds `a: TInt`; `let b = a + 3` looks up `a`, types the literal, applies `TInt + TInt -> TInt`, and binds `b: TInt`; `let c = b < 10` binds `c: TBool`; the body `("var", "c")` looks up `TBool`.  In the error program, the environment holds `{a: TInt}` when `add` finds `TInt + TStr` and raises.  The error is reported at the `add` node, but the root cause is the choice made at the first `let`.  That distance between the error location and the root cause is a recurring problem in type inference, and the reason good inference error messages are hard to write.

##### Critical Thinking Questions

7.  The inference trace shows `let a: int`, `let b: int`, `let c: bool`.  These are determined entirely from the *values* (literals), with no type annotations written.  Is this static or dynamic typing?  Explain.
8.  When inference encounters `a + "hello"`, it reports the error at the `add` expression.  But the *root cause* is that `a` was given an int value.  How far is the reported error from the root cause, and what does this say about inference error message quality?
9.  What would need to change to support `let a = 2; let b = a + 3.0;`?  (Hint: numeric type widening, `int + float -> float`.)  Modify the `infer` function to allow this.
{: start="7"}

#### Model 4: A Type-Error Postmortem

The danger of weak typing is not crashes; it is the absence of crashes.  When a language coerces instead of refusing, a type mistake does not stop the program.  It flows onward disguised as a plausible-looking value, and the first symptom appears far from the cause, often outside the program entirely.

**The incident.**  A checkout system written in a weakly typed language reads a price from a web form.  Form fields always arrive as *strings*, and nobody converted: `subtotal = "19.99"` is a string, `shipping = 5.00` is a number, and `total = (subtotal + shipping) * 1.06` adds shipping and then 6% tax.  The intended arithmetic is `(19.99 + 5.00) * 1.06 = 26.49`.  What the weak language actually computes, step by step:

| Step | Expression | What a weak language does | Value after | What a strong language does |
|------|-----------|----------------------------|-------------|------------------------------|
| 1 | `subtotal = "19.99"` | stores the string | `"19.99"` (string) | the same; the mistake is still latent |
| 2 | `subtotal + 5.00` | coerces `5.00` -> `"5"`, then *concatenates* | `"19.995"` (string) | **TypeError: cannot add string and number**, stops here |
| 3 | `"19.995" * 1.06` | coerces `"19.995"` -> `19.995`, then multiplies | `21.1947` (number) | never reached |
| 4 | charge the customer | charges `$21.19` with no error anywhere | wrong by `$5.30` | bug reported at step 2, with a line number |

Note the direction flip: at step 2 the `+` coerced the *number toward the string*, but at step 3 the `*` coerced the *string toward the number*.  That inconsistency, not any single conversion, is what makes weak typing treacherous.  And the weak column contains no error at any step; the only symptom is money.

**You write:** `model4_postmortem.py` - the script below, pasted as is.  It is not submitted.
**You run:** `python3 model4_postmortem.py`

> **Do this.**  Create `model4_postmortem.py` in your lab folder, paste the script below into it, and run `python3 model4_postmortem.py`.

```python
# Simulate both typing disciplines on the same buggy program.

def to_js_str(v):
    if isinstance(v, float) and v == int(v):
        return str(int(v))          # 5.0 renders as "5", as in JavaScript
    return str(v)

def weak_add(a, b):
    """JavaScript-style +: if either side is a string, concatenate."""
    if isinstance(a, str) or isinstance(b, str):
        return to_js_str(a) + to_js_str(b)
    return a + b

def weak_mul(a, b):
    """JavaScript-style *: coerce both sides toward number."""
    return float(a) * float(b)

def strong_add(a, b):
    if type(a) is not type(b):
        raise TypeError(f"cannot add {type(a).__name__} and {type(b).__name__}")
    return a + b

subtotal = "19.99"       # the latent mistake: a string from the form
shipping = 5.00

print("=== Weak mode: no errors, wrong money ===")
step2 = weak_add(subtotal, shipping)
print(f"  step 2: {subtotal!r} + {shipping!r} -> {step2!r}")
step3 = weak_mul(step2, 1.06)
print(f"  step 3: {step2!r} * 1.06 -> {step3!r}")
print(f"  charged: ${step3:.2f}   (intended: ${(19.99 + 5.00) * 1.06:.2f})")

print("\n=== Strong mode: stops at the mistake ===")
try:
    strong_add(subtotal, shipping)
except TypeError as e:
    print(f"  step 2: TypeError: {e}")
```

> **You should see.**  The weak run prints `step 2: '19.99' + 5.0 -> '19.995'`, `step 3: '19.995' * 1.06 -> 21.1947`, and `charged: $21.19   (intended: $26.49)`, with no error anywhere.  The strong run prints one line, `step 2: TypeError: cannot add str and float`, and stops.

```text
=== Weak mode: no errors, wrong money ===
  step 2: '19.99' + 5.0 -> '19.995'
  step 3: '19.995' * 1.06 -> 21.1947
  charged: $21.19   (intended: $26.49)

=== Strong mode: stops at the mistake ===
  step 2: TypeError: cannot add str and float
```

In a weakly typed language, `"19.99" + 5.0` yields `"19.995"` and `"19.995" * 1.06` yields `21.1947`.  Is the deepest design problem this postmortem illustrates floating-point rounding error, the slowness of string operations, silent coercion letting a type mistake flow through the program as plausible-looking wrong values instead of stopping with an error, or the inability of strings to represent decimal numbers?

> **Answer.**  Silent coercion lets a type mistake flow through the program as plausible-looking wrong values instead of stopping with an error.

##### Critical Thinking Questions

10.  Walk the postmortem table: at which step did the *type* first go wrong, and at which step did the *money* first go wrong?  Why is it significant that these are different steps?
11.  Step 2 coerced number -> string, but step 3 coerced string -> number.  Write the coercion rule a language designer would have to publish to justify both choices at once.  Does the result sound principled or accidental?
12.  The weak-mode run produces no error at any point; the bug would surface only as customer complaints.  Name two other places in the software pipeline (besides the language's type system) where this bug could have been caught, and what each catch would cost compared to a step-2 TypeError.
13.  For your project language: which, if any, of these coercions will you allow?  Record the decision in `SEMANTICS.md`, citing this postmortem as evidence for or against.
{: start="10"}

### Extension D: The Remaining Type Rules

The checker in Part 2 handles literals, variables, binary operators, and conditions.  The class language has three more constructs, and the starter's AST already includes their node classes: `Assign`, `LogicOp`, and `UnaryOp`.  Right now `check_stmt` and `check_expr` raise `NotImplementedError` for them.  Each rule below follows the same unknown-type rule as Part 2: when a type it compares is `None`, it skips the check.  The Interpreter assignment's Part 4 asks for all three, so this is a head start.

**You write:** `scope_lab.py` - an `Assign` branch in `check_stmt`, and `LogicOp` and `UnaryOp` branches in `check_expr`.

**`Assign` in `check_stmt`.**  Input: an `Assign` node with `name`, `value`, `line`, and `col`.  Output: nothing.

1. Look up the variable's declared type through the chain, catching `LangNameError` the way your `Var` rule does.
2. Type the new value, `node.value`.
3. If both types are known and they differ, raise at the `Assign` node's line and column.  The message has the form `'<name>' declared <declared>, but assigned a value of type <actual>`.
4. Do not define anything.  An assignment changes a value, never a type.

**`LogicOp` in `check_expr`.**  Input: a `LogicOp` node for `and` or `or`, with `op`, `left`, `right`, `line`, and `col`.  Output: `Bool`.

1. Type both operands.
2. If both are known and either one is not `Bool`, raise naming the operator and both operand types.
3. Return `Bool`.

**`UnaryOp` in `check_expr`.**  Input: a `UnaryOp` node with `op`, `operand`, `line`, and `col`.  Output: the type the operator wants.

1. Type the single operand.
2. Work out the wanted type: `not` wants `Bool`, and `-` wants `Num`.
3. If the operand's type is known and differs from the wanted type, raise naming the operator, the wanted type, and the operand's type.
4. Return the wanted type.

A unary operator has only one operand, so "both types" in its message means the wanted type and the actual one.  Test each rule with a small tree built by hand, the way `test_scope_lab.py` builds its trees.

### Extension E: Run the Checker on Real Source Files

Part 2 checked trees built by hand.  This extension connects the checker to your own lexer and parser, so it can read a program from a file.  Copy your AST, parser, and lexer files into `cs374-scopes`.  Then replace the AST section of `scope_lab.py` with `from ast_nodes import *`, so the checker sees your parser's node classes.  Finish Extension D first, because two of the twelve programs use `Assign` and unary minus.

Add this file driver to the bottom of `scope_lab.py`, adjusting the import names if your parser's differ:

```python
if __name__ == "__main__":
    import sys
    from parser import parse, ParseError
    from lexer import LexError
    source = open(sys.argv[1]).read()
    try:
        check(parse(source))
    except (LangTypeError, ParseError, LexError) as err:
        print(err)
        sys.exit(1)
```

#### Carry the annotation from the source to the `Let` node

Right now `let x: Num = 42;` may not get past the lexer yet, if yours has no token for `:`.  The annotation has to survive three stages to reach the checker: the lexer must produce a `COLON` token, the parser must read `COLON` and a type name inside `parse_let_stmt`, and the `Let` node must have a field to hold the name.  If your lexer and parser already do all three, skip to the twelve programs below, and read `node.annotation` as whatever your field is called.

**You write:** `lexer.py` - one new `COLON` entry in `TOKEN_SPEC`; `ast_nodes.py` - one new field on `Let`; `parser.py` - the annotation in `parse_let_stmt`.
**You run:** `python3 -c "from parser import parse; print(parse('let x: Num = 42;'))"`

> **Do this.**
> 1. In `lexer.py`, add a `TOKEN_SPEC` entry named `COLON` whose pattern matches a single `:`.  Copy the shape of the `SEMICOLON` entry, and put the new one on the line after it.  No other token starts with `:`, so its position in the list does not matter.  The driver uses the default `TOKEN_SPEC`; if you also load `token_spec.json` somewhere, add the same entry there too.
> 2. In `ast_nodes.py`, give `Let` a new field named `annotation`.  It holds a type name (`"Num"`, `"Str"`, or `"Bool"`) or nothing, so its type is `Optional[str]` with a default of `None`.  Import `Optional` from `typing` at the top of the file if it is not there.  Make it the *last* field, after `col`, so every existing `Let(name, value, line, col)` call keeps working.
> 3. In `parser.py`, change `parse_let_stmt` to read an optional `: Type`.  The algorithm is below.

`parse_let_stmt(self)` takes no arguments besides the parser and returns a `Let` node.  The usual version already does steps 1, 2, 4, and 5; step 3 is new.

1. Expect a `LET` token.  Keep the token, because the `Let` node takes its line and column.
2. Expect an `IDENT` token for the variable's name.
3. Start with no annotation.  Peek at the next token without consuming it.  If it is a `COLON`, consume the colon, then expect an `IDENT` and keep that token's text as the annotation.
4. Expect `EQ`, parse the initializer expression, and expect `SEMICOLON`, exactly as before.
5. Build the `Let` node from the name, the value, and the `LET` token's line and column, and pass the annotation by keyword.

| Step | How to think about it |
|---|---|
| step 3 | The type name is an ordinary `IDENT` token, the same kind as the variable's name.  The parser does not check that it is `Num`, `Str`, or `Bool`; it only carries the text along.  Peeking never consumes, so an unannotated `let x = 1;` still parses as before. |

> **You should see.**  One `Program` whose `Let` node ends with `annotation='Num'`:
>
> ```text
> Program(stmts=[Let(name='x', value=Num(value=42, line=1, col=14), line=1, col=1, annotation='Num')])
> ```
>
> The Interpreter assignment's Step 4a suggests the field name `type_ann` for the same idea.  If you already did Step 4a with that name, keep it, and read `node.type_ann` wherever this page says `node.annotation`.  One name in both places is all that matters.

> **If it fails.**
> - `LexError at line 1, col 6: unexpected character ':'`: the `COLON` entry is missing from `TOKEN_SPEC`, or you added it only to `token_spec.json`.
> - `ParseError at line 1, col 6: expected EQ, found COLON`: the lexer works, but `parse_let_stmt` does not consume the colon and the type name yet.
> - `TypeError: Let.__init__() got an unexpected keyword argument 'annotation'`: the new field is not in the `Let` dataclass, or it has a different name there.
> - `TypeError: non-default argument 'annotation' follows default argument 'col'` (the last name varies with your Python version and field order): the field has no `= None` default.  Every field after `line` and `col` needs a default.

#### Run the twelve provided programs

Verify your checker against the [twelve provided programs]({{ site.baseurl }}/files/starters/typechecker/programs/), which live in `files/starters/typechecker/programs/` in the course site repository.  Seven programs must pass silently.  One of them, `11-undeclared-variable.ml`, uses a name nothing declares; the checker leaves it to the evaluator.  Five ill-typed programs must each produce a positioned error; these include the classic `let x: Num = 1 + true;` (the error must appear *before* anything runs) and a shadowing case where an inner `let x: Str` legitimately changes the type of `x` for the inner scope only.

**You write:** `runlog.txt`, produced by the command below.  No code changes, unless a program shows you a bug.
**You run:** `for f in programs/*.ml; do echo "== $f"; python3 scope_lab.py "$f"; done | tee runlog.txt`

> **Do this.**
> 1. If you have not already, copy all twelve provided programs into `programs/`.  They are named `01-` through `12-`, and the five whose names contain `bad-` are the ill-typed ones.  Keep your own test files in `mytests/`, so this loop sees only the twelve.
> 2. Run the driver over every one of them and save the output.  The `for` loop runs the checker once per file, `echo` labels each run with its file name, and `tee` prints the output and writes it to `runlog.txt` at the same time.  If the provided programs use a different file extension, change `*.ml` to match.
>
>    ```bash
>    for f in programs/*.ml; do echo "== $f"; python3 scope_lab.py "$f"; done | tee runlog.txt
>    ```
>
> 3. Read `runlog.txt` once, top to bottom, and confirm each well-typed program shows only its label and each ill-typed program shows its label and one `Type error` line.  Each of the five ill-typed programs breaks a *different* rule, so five identical messages means a branch is catching something it should not.

> **You should see.**  Twelve labels.  Seven are followed directly by the next label (silent acceptance).  Five are followed by exactly one `Type error at line L, col C: ...` line, and each of those names two types.  With the parser the activities build and the message forms from Steps 1.3 and 1.4, the whole log is exactly this.  Your positions must match; your wording after each colon may differ.
>
> ```text
> == programs/01-literals.ml
> == programs/02-arithmetic.ml
> == programs/03-comparison.ml
> == programs/04-logic.ml
> == programs/05-control.ml
> == programs/06-shadowing.ml
> == programs/07-bad-add-num-bool.ml
> Type error at line 3, col 16: '+' requires Num operands, got Num and Bool
> == programs/08-bad-annotation-mismatch.ml
> Type error at line 3, col 1: 'total' declared Num, but its initializer has type Str
> == programs/09-bad-compare-strings.ml
> Type error at line 5, col 13: '<' requires Num operands, got Str and Str
> == programs/10-bad-equality-mixed-types.ml
> Type error at line 6, col 13: '==' requires operands of the same type, got Num and Str
> == programs/11-undeclared-variable.ml
> == programs/12-bad-shadow-escapes.ml
> Type error at line 8, col 1: 'x' declared Num, but assigned a value of type Str
> ```

> **If it fails.**
> - `06-shadowing.ml` reports `'+' requires Num operands, got Str and Num` on line 9: the inner `let x: Str` leaked into the outer scope.  Something is defining into the outer table instead of the block's child table.
> - `12-bad-shadow-escapes.ml` is silent: the same leak in reverse.  After the block, `x` must look up as `Num` again, so the `Assign` of a `Str` must fail.
> - A line starting `ParseError` or `LexError` appears: a program did not parse, usually because the annotation work above is incomplete.  Re-run the parse check from that step.
> - More or fewer than twelve labels: the loop picked up extra files in `programs/`, or some of the twelve are missing.  Move your own tests to `mytests/`.

### Extension F: Theory Questions

These four questions come from the *Binding, Scope, and Environments* and *Type Systems* sessions.  Answer each in a few sentences.

**Scope.**

> **Do this.**
> 1. Which line of your class makes this language lexically scoped rather than dynamically scoped?  Quote the line and say what it would have to become for the rule to change.
> 2. Re-predict the trace program's final output under dynamic scoping, where the lookup chain follows the callers rather than the enclosing text, and name the step where the two rules first diverge.  If you conclude that they never diverge for this program, say why, and say what the program would need to contain before they could.

**Types.**

1.  Place four languages (Python, C, Haskell, and JavaScript) on the static/dynamic × strong/weak quadrant, with one sentence of justification each.
2.  Your checker makes the class language *gradually* typed in spirit: annotated declarations are checked, and unannotated territory is documented as unchecked.  State one benefit and one risk of that middle ground, using the mypy/TypeScript comparison from class.
