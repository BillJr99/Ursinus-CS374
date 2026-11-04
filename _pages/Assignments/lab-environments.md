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
    - rtitle: "Optional Extensions to the Environments Lab (no points)"
      rlink: "../Tutorials/EnvironmentsExtensions"

tags:
  - interpreter
  - scope
  - types
  - languages
  - lab

---

In this lab you build one data structure and use it twice.  The data structure is a **scope table**: a class named `Environment` that maps names to what they mean, one table per block of code, with each table pointing to the block that encloses it.  In Part 1 the table maps names to *values*, which is what your interpreter needs to run a program with nested blocks.  In Part 2 the same class maps names to *types*, and you use it to check a program before it runs.  The class does not change between the parts, because scope rules and type rules walk the same chain.

You start from a provided file, `scope_lab.py`.  Everything in it is written for you except seven method bodies marked `TODO`, and a provided test file has eleven tests that turn from `FAIL` to `ok` as you finish each method.  Your `Environment` goes into the Interpreter assignment's Step 2c, and your checker is the starting point for its Part 4.

**Pair policy.**  You may do this lab in pairs.  You each submit the same files, name each other in them, and earn the same grade.  You may also work alone.  The Interpreter assignment remains individual work: you may both carry this shared `scope_lab.py` into it, but the evaluator and the checker extensions you write there must be your own.

---

## Before You Start

You need Python 3.10 or newer, plus the starter [scope_lab.py]({{ site.baseurl }}/files/starters/environments/scope_lab.py) and the tests [test_scope_lab.py]({{ site.baseurl }}/files/starters/environments/test_scope_lab.py).  On Windows, if `python3` is not found, use `python` wherever this page says `python3`.  If the terminal is new to you, read the [Dev Environment tutorial]({{ site.baseurl }}/Tutorials/DevEnvironment) first.

> **Do this.**
> 1. Make a folder named `cs374-scopes`, and download both provided files into it.
> 2. Create `notes.md` with your name (and your partner's) at the top.  It holds your trace predictions and your typing rules.  A photo of a paper page is fine.
> 3. From inside the folder, run `python3 test_scope_lab.py`.

> **You should see.**  Eleven tests, each marked `FAIL`, and no crash.  The last line reads `FAILED (failures=11)`.  That list is your to-do list, in order.

You never edit `test_scope_lab.py`, and you never change any code in `scope_lab.py` outside the seven `TODO` bodies.

---

## Part 1: The Scope Table

A block can use the names of the blocks around it, and it can also hide them with its own.  So each scope needs its own table of names and a way to reach the scope that encloses it.  Here is a program after entering one block:

```text
   inner                       outer
+-----------+   _parent    +---------------+   _parent
| x: 51     | -----------> | x: 2, y: 10   | -----------> None
+-----------+              +---------------+
```

Each box is one `Environment` object.  Its table is `self._bindings`, a dictionary, and its arrow is `self._parent`, which is `None` at the top level.  You write three methods on this class:

- `define(name, value)` creates `name` in *this* scope, which shadows (hides) any outer binding of the same name.
- `lookup(name)` returns the value of the nearest binding of `name`.
- `assign(name, value)` updates the nearest binding of `name`, and never creates one.

The difference between `define` and `assign` is the most important idea in this part: it is the difference between `let x = 1;` and `x = 1;`.  `lookup` and `assign` have the same shape, because both walk the chain:

```text
lookup(name):
    if name is in this scope's table:  return its value
    if this scope has a parent:        return parent.lookup(name)
    raise LangNameError
```

### Step 1.1: Follow One Worked Lookup

A `let` is a `define`, and entering a block makes a new `Environment` whose parent is the current one.  This code builds the picture above:

```python
outer = Environment()               # the top-level scope
outer.define("x", 2)                # let x = 2;
outer.define("y", 10)               # let y = 10;
inner = Environment(parent=outer)   # {   enter a block
inner.define("x", 51)               #     let x = 51;
inner.lookup("y")                   #     ... y ...
```

Here is the last call, one scope at a time:

```text
inner.lookup("y")
    inner holds {x: 51}.  No y, so ask the parent.
    outer.lookup("y")
        outer holds {x: 2, y: 10}.  y is here, so return 10.
    return 10
```

The lookup stopped at the first scope that had the name, and that is all shadowing is: `inner.lookup("x")` stops at `inner` and never sees the outer `x`.  The [Paper Machine slide](https://liascript.github.io/course/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374-Fall2026/gh-pages/_pages/Activities/liascript-bindingscope.md#19) in the Binding, Scope, and Environments activity works a longer example.

> **Predict.**  What does `inner.lookup("z")` do, and how many scopes does it check before it stops?

### Step 1.2: Write define and lookup

In `scope_lab.py`, replace each `raise NotImplementedError` line in `define` and `lookup` with the code its `TODO` describes, and run `python3 test_scope_lab.py`.

> **You should see.**  Tests 1, 2, and 3 marked `ok`, and the last line reads `FAILED (failures=8)`.

> **If it fails.**
> - `RecursionError: maximum recursion depth exceeded`: `lookup` called `self.lookup` instead of `self._parent.lookup`, so it asks the same scope the same question forever.
> - `AttributeError: 'NoneType' object has no attribute 'lookup'`: `lookup` asked the parent without checking that there is one.
> - Test 2 fails on `a name bound to None still counts as bound`: you used `.get` instead of `in`.

### Step 1.3: Write assign

`assign` walks the chain the same way, but it writes where `lookup` reads.  It must never write into this scope unless the name is already here, because otherwise `y = 1;` inside a block would create a new `y` and leave the outer one unchanged.  Fill in the `TODO`, and run the tests.

> **You should see.**  Tests 1 through 6 marked `ok`.  Test 6 runs the shadowing program from the Interpreter assignment and checks that it prints `51`, then `2`, then `11`.  The last line reads `FAILED (failures=5)`, because Part 2 has not started.

> **If it fails.**
> - Test 4 fails on `assign created a new y in the inner scope`: your `assign` wrote into `self._bindings` when the name was not there.  That is the define-versus-assign bug.
> - Test 5 fails with a `KeyError` in the message: `assign` indexed a dictionary instead of raising `LangNameError`.

> **Watch out.**  The Interpreter assignment's Step 5a defines the same `LangError` classes in `interpreter.py`.  When you carry your `Environment` into that assignment, keep one copy of the error classes, not two.  With two copies of `LangNameError`, an `except LangNameError` in the evaluator can miss the one your `Environment` raises.

### Step 1.4: Predict the Scope Trace, Then Run It

The test file includes this program of three nested blocks.  Predicting it by hand shows whether you can tell `define` from `assign` in real code, and this is the graded paper work for Part 1.

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

> **Do this.**
> 1. Work through the program by hand.  At each `let`, add the name to the innermost open block.  At each assignment, find the nearest block that already has the name and change it there.
> 2. In `notes.md`, under a heading `Step 1.4`, write the six values that `print` produces, in order.
> 3. Only after that, run `python3 test_scope_lab.py --trace`.
> 4. For each value you missed, write one sentence naming the rule you misapplied: define versus assign, or which scope a lookup starts in.

> **You should see.**  The eleven test results, then twenty numbered steps, each showing the chain of scopes from the innermost outward, such as `A{x=2} -> top{x=1, y=10}`.  The last six lines are the printed values.  If a Part 1 test still fails, the script prints `Finish Part 1 (tests 1 to 6) before running the trace program.` instead.

---

## Part 2: Type Checking with the Same Table

A **static type checker** reads a program's abstract syntax tree (AST) and decides whether each operation makes sense, before any of the program runs.  It never computes a value.  It remembers *types* instead: `x` is a `Num`, `s` is a `Str`.

To do that, it has to know what type each name has at each point in the program.  That is a scope question, with the same answer as in Part 1: look in this block, then in the enclosing blocks.  So the checker stores types in your `Environment`.  After `let x: Num = 1;`, the checker's table holds `{'x': 'Num'}`, and you get shadowing for free.

The starter already has `LangTypeError`, a small copy of the class AST, `check`, and `check_stmt`, which handles each statement and opens a child table for each block.  You write the rules for literals, variables, binary operators, and conditions.  Their `TODO` comments state each rule.

One idea covers all four: **if a type that a rule compares is `None`, the rule skips its check** and still returns its usual result.  `None` is the *unknown* type, which a name gets when nobody declared it.  The checker cannot prove anything about that name, so it leaves it to the evaluator, which reports `Undefined variable` when the program runs.

### Step 2.1: Follow One Worked Check

Let's check `let x: Num = 1 + true;`, where the `+` sits at line 1, column 16.  Types flow up the tree, so the checker has to type the parts before it can judge the whole:

```text
check_stmt(Let(...))
    check_expr(BinOp("+", Num(1), BoolLit(True)))
        left:  check_expr(Num(1))           gives Num
        right: check_expr(BoolLit(True))    gives Bool
        + needs two Nums, and the right one is not, so raise at the BinOp's position
```

The error stops the check before `x` is ever defined, and long before anything runs.  The message names the operator and *both* types, because either one could be the mistake:

```text
Type error at line 1, col 16: '+' requires Num operands, got Num and Bool
```

> **Predict.**  What should the checker do with `let x: Num = 1 + y;` when no `let` declares `y`?

### Step 2.2: Type Literals and Variables

A literal's type needs nothing from the table, and a variable's type is whatever its nearest declaration gave it.  Fill in the two `TODO`s for these in `check_expr`, above the final `raise`, and run the tests.

> **You should see.**  Tests 1 through 8 marked `ok`, and `FAILED (failures=3)` on the last line.  Test 8 also checks that, after `let x: Num = 1;`, the table's `_bindings` is exactly `{'x': 'Num'}`.  That is your Part 1 class holding a type.

> **If it fails.**
> - `not written yet: no typing rule yet for Str`: the branch sits below the final `raise`, tests the wrong class, or has no `return`.
> - Test 8 fails on `an undeclared name has the unknown type None`: the `Var` branch let the `LangNameError` escape.  Catch it.

### Step 2.3: Type the Binary Operators

An operator's rule depends on its family, so the starter names the three families: `ARITHMETIC`, `COMPARISON`, and `EQUALITY`.  Fill in the `TODO`, and run the tests.

> **You should see.**  Tests 1 through 10 marked `ok`, and `FAILED (failures=1)` on the last line.

> **If it fails.**
> - Test 9 fails on `must sit at the operator's position`: you raised at an operand's position.  Use `node.line` and `node.col` of the `BinOp`.
> - Test 10 fails on `two Strs may be compared with ==`: the equality family is falling into the `Num` check.  Test for `EQUALITY` first.
> - A message names only one type: format both `left` and `right` into it.

### Step 2.4: Check if and while Conditions

A condition decides which branch runs, so the checker requires a `Bool`.  Fill in `check_condition`.  The `If` and `While` nodes store only a `line`, so the error goes at the condition, since every expression node has both a `line` and a `col`.

> **You should see.**  All eleven tests marked `ok`, ending in `OK`.

Your evaluator has a truthiness rule, so `while 1 { ... }` means something when it runs.  The checker is stricter on purpose and rejects it.  The first reflection prompt asks you whether that is the right call.

### Step 2.5: Write the Four Typing Rules on Paper

A **typing rule** has premises (what must already be true about the parts) and a conclusion (what then holds for the whole).  The code tells you what you enforced, and the rule tells you whether that is what you meant.  The rule for `+` can be written with the premises above a line and the conclusion below it:

```text
e1 : Num    e2 : Num
--------------------
   e1 + e2 : Num
```

Or as a sentence: *if `e1 : Num` and `e2 : Num`, then `e1 + e2 : Num`*.

> **Do this.**
> 1. In `notes.md`, under a heading `Step 2.5`, write one rule each for literals, variables, binary operators (one per family), and conditions.  For variables, say where the type comes from and what happens when no scope declares the name.
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

The [optional extensions]({{ site.baseurl }}/Tutorials/EnvironmentsExtensions) earn no points, and I am glad to talk about them with you.

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
