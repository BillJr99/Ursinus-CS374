---
layout: assignment
permalink: /Assignments/EnvironmentsLab
title: "CS374: Principles of Programming Languages - Lab: Environments and Scope"

info:
  coursenum: CS374
  purpose: "To build the Interpreter assignment's Environment class with a partner, covering nested scopes, define versus assign, and shadowing, and to verify it against the exact behaviors the Interpreter's evaluator depends on."
  tilt:
    task: "With a partner, implement an Environment class with parent chaining, distinguish define from assign, and verify shadowing, scope restoration, and name-error behavior against a provided test script."
    criteria: "I grade a correct Environment class that passes all provided behavior tests, and a short trace exercise that predicts scope behavior on paper.  The full breakdown is in the rubric below."
  points: 15
  goals:
    - To implement an Environment class with parent chaining supporting nested scopes
    - To distinguish definition (creating a name in the current scope) from assignment (updating the nearest enclosing binding)
    - To verify shadowing, scope restoration, and name-error behavior with tests and paper traces
  rubric:
    - weight: 10
      description: "Part 0: Before You Start - Binding and Scope"
      preemerging: Neither the shadowing trace nor the scoping probes are attempted
      beginning: The let expression is evaluated to an answer but no environment is drawn at any step
      progressing: The environment is drawn at each step and the dynamic-scope prediction is made, but the divergence step is not identified, or only one distinguishing probe program is written
      proficient: let x = 2 in let x = x + 1 in x * x is evaluated with the environment drawn at each step, under both lexical and dynamic scope, with the exact step marked where the two disagree; the unbound-variable behavior is decided with a stated error and timing; and two probe programs are written whose output differs by scoping rule, with a prediction for each under each rule
    - weight: 63
      description: "The Environment Class (Goals 1, 2)"
      preemerging: The class is missing, or lookup does not consult parent scopes
      beginning: Lookup chains to parents but define and assign are conflated, so inner assignment creates shadows instead of updating
      progressing: Define and assign are distinguished and shadowing works, but assignment to an undefined name does not raise a language-level error, or exiting a scope fails to restore the outer binding
      proficient: define creates in the current scope, assign updates the nearest enclosing binding and raises a positioned language-level name error when no binding exists, lookup chains correctly to any depth, shadowing and scope restoration pass every provided test, and the shadowing program prints 51 then 2
    - weight: 27
      description: "Scope Trace Exercise (Goal 3)"
      preemerging: The trace is missing or contradicts the submitted implementation
      beginning: The trace predicts final output only, with no per-step environment states
      progressing: The trace shows environment states per step with one prediction error against the actual run
      proficient: The trace shows the environment chain at every step, every prediction matches the actual run, and the lexical-vs-dynamic question is answered by pointing to the exact line of the class that decides it
  readings:
    - rtitle: "Binding and Scope Activity"
      rlink: "Activities/liascript-bindingscope.md"
      liapage: true
    - rtitle: "Environments Activity"
      rlink: "Activities/liascript-environments.md"
      liapage: true

tags:
  - interpreter
  - scope
  - languages
  - lab

---

In this lab you build `Environment`, the class that makes scope real in your interpreter.  An environment is the data structure that maps variable names to their values.  Each block of code gets its own environment, and each environment points to the enclosing one, so a lookup can walk outward until it finds the name.  You leave with a tested `environment.py` that the Interpreter assignment's Step 2c imports unchanged, plus a paper trace that predicts what your class will do before you run it.  You do this lab with a partner.

**Pair policy.**  You may do this lab in pairs.  You each submit the same files, name each other in them, and earn the same grade.  You may also work alone.  The Interpreter assignment remains individual work: you may both carry this shared `Environment` into it, but the evaluator around it must be your own.

---

## Before You Start

You need:

- Python 3.10 or newer.  The class uses only the standard library.
- Any editor that saves plain `.py` files, and a terminal you can run `python3` from.  If the terminal is new to you, read the [Dev Environment tutorial]({{ site.baseurl }}/Tutorials/DevEnvironment) and the [Shell for Language Development primer]({{ site.baseurl }}/Tutorials/ShellForLanguageDev) first; both are short.
- The provided behavior script [test_environment.py]({{ site.baseurl }}/files/starters/environments/test_environment.py).
- The two readings listed above (the Binding and Scope activity and the Environments activity).  Part 0 uses their vocabulary.

Make a folder for this lab and confirm your Python version from inside it (any `3.10` or higher is fine; on Windows, if `python3` is not found, use `python` wherever this page says `python3`):

```bash
mkdir cs374-environments
cd cs374-environments
python3 --version
```

```text
Python 3.11.9
```

> **Time budget.**  About two to three hours: thirty minutes on paper for Part 0, about an hour of coding for Part 1, and thirty to forty-five minutes of prediction and checking for Part 2.  See the course schedule for the assigned and due dates.

---

## Your First 15 Minutes

1.  Create `environment.py` inside `cs374-environments/` and paste in the skeleton from Step 1.1.
2.  Run `python3 environment.py` once.  A skeleton that runs and prints nothing has no syntax errors.
3.  Fill in `define` (one line: store the value in this scope's table) and the first two lines of `lookup` (if the name is in this scope's table, return it).
4.  Create `try_env.py` from Step 1.2 and run `python3 try_env.py`.  It prints `51` and `2`, then stops at the unfinished `assign`.  That crash is your to-do list.

---

## Part 0: Trace Binding and Scope on Paper

Do this part on paper before you write the class; you may do it alone even though the rest of the lab is pair work.  Put your answers at the top of `trace.md` (a photo of the paper is fine).  Two terms first.  Under lexical scope, a name refers to the binding in the enclosing text of the program.  Under dynamic scope, a name refers to the most recent binding made by any caller that is still running.

### Step 0.1: Trace the Shadowing Expression

Evaluate this expression by hand, drawing the environment at each step.  The inner binding of `x` shadows (hides) the outer one.

```text
let x = 2 in let x = x + 1 in x * x
```

> **Do this.**
> 1. Copy the table below into `trace.md` (or draw it on paper).  Step 1 is done for you as a model.
> 2. Fill in the chain and the result at every step.  Write chains innermost-first, each scope a box of bindings with an arrow to its parent, like `E1{x=2} -> E0{}` (`E0` is the empty top-level scope).  A drawn picture of boxes and arrows is just as good.
> 3. Write the final value of the whole expression under the table.

| Step | Expression being evaluated | Environment chain (lexical) | Result |
|------|----------------------------|-----------------------------|--------|
| 1 | `let x = 2 in ...` binds the outer `x` | `E1{x=2} -> E0{}` | scope `E1` entered |
| 2 | `x + 1`, evaluated inside `E1` | | |
| 3 | `let x = <step 2 result> in ...` binds the inner `x` | | |
| 4 | `x * x`, evaluated inside the inner scope | | |
| 5 | the inner `let` ends, then the outer `let` ends | | |

### Step 0.2: Predict It Under Dynamic Scope

> **Do this.**
> 1. Copy the same table again, headed "Environment chain (dynamic)", and fill it in under the dynamic rule.
> 2. Mark the exact step where the two tables first give different results.  If every row agrees for this expression, say so, and say what a program would have to contain before the two rules could disagree.

### Step 0.3: Decide the Unbound-Variable Behavior

> **Do this.**
> 1. Write a two-line expression of your own that uses an unbound variable, a name no environment in the chain defines (for example, an outer `let` that binds `x` and a body that mentions `y`).
> 2. Trace it the same way, and stop at the step where the chain runs out.
> 3. Decide what error the evaluator should raise (name the class) and at what moment: when the program is read, when the enclosing `let` is entered, or when the lookup of the name actually runs.  Write the error and the moment as one sentence in `trace.md`.  Decide this now rather than let Python decide for you.

### Step 0.4: Write Two Probe Programs for the Mystery Scoping Language

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

> **Do this.**
> 1. Write two short programs of your own whose output differs depending on the scoping rule.  Make one of them as short as you can.
> 2. For each program, write your prediction of what it prints under each rule: one line for lexical, one line for dynamic.
> 3. If both predictions for a probe match, it cannot tell the rules apart, so change it.

> **Bring to class.** Both probe programs and all four predictions.  You will run them against the mystery interpreter in the Binding and Scope session.

---

## Part 1: Build the Environment Class

Implement `Environment` in `environment.py`.  It stands alone (no AST or evaluator needed) with this interface:

- `Environment(parent=None)`: a scope with an optional enclosing scope.
- `define(name, value)`: create `name` in this scope.  This shadows any outer binding of the same name.
- `assign(name, value)`: update the nearest enclosing binding of `name`.  If no scope in the chain defines it, raise a language-level `LangNameError` (not a bare Python `KeyError`) that carries the name.
- `lookup(name)`: return the nearest enclosing binding's value, or raise `LangNameError`.

### Step 1.1: Create environment.py and Fill In the Methods

The skeleton below names every method and includes the two error classes, so the file runs on its own.  `LangError` carries a line and column that default to zero; the evaluator fills those in during the Interpreter assignment.  `lookup` and `assign` share a shape: check this scope, else defer to the parent, else raise.  The one line that separates `define` from `assign` is the point of the lab: `define` writes into this scope's table no matter what any parent holds, and `assign` never writes into this scope unless the name is already here.

> **Do this.**
> 1. Create `environment.py` in your `cs374-environments/` folder, paste in the skeleton below, and run `python3 environment.py` once.  A clean run prints nothing; a `SyntaxError` or `IndentationError` means the paste went wrong.
> 2. Replace each `raise NotImplementedError(...)` with the code the `# TODO` comments describe.  In `lookup` and `assign`, let the recursive call on `self._parent` do the walking; you do not need a loop.
> 3. Give each `LangNameError` a message that includes the variable name, such as `Undefined variable 'y'` for `lookup` and `Cannot assign to undefined variable 'y'` for `assign`.
> 4. Run `python3 environment.py` again and confirm it still prints nothing.

```python
"""environment.py: the scope table for the CS374 interpreter."""

class LangError(Exception):
    """Base class for every language-level error (same shape as Interpreter Step 5a)."""
    def __init__(self, message, line=0, col=0):
        self.message = message
        self.line = line      # the evaluator fills these in later
        self.col = col
        super().__init__(str(self))

    def __str__(self):
        return f"line {self.line}, col {self.col}: {self.message}"

class LangNameError(LangError):
    """Raised when a name has no binding anywhere in the chain."""

class Environment:
    """One scope: a table of bindings plus a link to the enclosing scope."""
    def __init__(self, parent=None):
        self._bindings = {}     # name -> value, for THIS scope only
        self._parent = parent   # the enclosing Environment, or None at top level

    def define(self, name, value):
        # TODO: store the value in this scope's table.  Do not look at the parent.
        raise NotImplementedError("define")

    def lookup(self, name):
        # TODO: if name is bound in this scope, return its value.
        # TODO: otherwise, if there is a parent, ask the parent and return its answer.
        # TODO: otherwise raise LangNameError with a message that names the variable.
        raise NotImplementedError("lookup")

    def assign(self, name, value):
        # TODO: if name is bound in this scope, update it here.
        # TODO: otherwise, if there is a parent, hand the assignment to the parent.
        # TODO: otherwise raise LangNameError.  Never create a new binding here.
        raise NotImplementedError("assign")
```

> **Watch out.** `if self._parent:` runs the parent's truthiness, and an `Environment` with no bindings is still a real parent.  Compare against `None` explicitly: `if self._parent is not None:`.

> **Watch out.** The Interpreter assignment's Step 5a defines the same `LangError` hierarchy in `interpreter.py`.  Keep one definition: import `LangError` and `LangNameError` from `environment.py`, or move them into the interpreter's error module and import them back here.  With two copies of `LangNameError`, an `except LangNameError` in the evaluator can miss the one your `Environment` raises.

### Step 1.2: Run the Usage Example

This is the Interpreter assignment's shadowing program, translated line by line into calls on your class.  A `let` is a `define`, a bare assignment is an `assign`, entering a block is a new `Environment` whose parent is the current one, and leaving the block means you stop using it.

> **Do this.** Create `try_env.py` in the same folder as `environment.py`, paste in the example below, and run `python3 try_env.py` from that folder.

```python
from environment import Environment, LangNameError

outer = Environment()                 # the program's top-level scope
outer.define("x", 2)                  # let x = 2;
inner = Environment(parent=outer)     # entering the block
inner.define("x", 51)                 # let x = 51;   shadows the outer x
print(inner.lookup("x"))              # print x;      inside the block
print(outer.lookup("x"))              # print x;      after the block ends

outer.define("y", 10)                 # let y = 10;
inner.assign("y", 11)                 # y = 11;       inside the block, no let
print(outer.lookup("y"))              # the outer y changed

try:
    inner.assign("nope", 0)           # nope = 0;     nobody defined nope
except LangNameError as err:
    print("caught:", err)
```

> **You should see.** Four lines.  The wording after `caught:` is whatever message you wrote, but it must contain the name `nope`.

```text
51
2
11
caught: line 0, col 0: Cannot assign to undefined variable 'nope'
```

> **If it fails.**
> - `ModuleNotFoundError: No module named 'environment'`: you ran the command from a different folder.  `cd` into `cs374-environments/` and run it again.
> - The third line prints `10` instead of `11`: your `assign` created a new `y` in `inner` instead of updating `outer`.  That is the define-versus-assign bug the rubric names.
> - A `KeyError` traceback instead of `caught:`: `assign` fell through to a dictionary lookup instead of raising `LangNameError`.

### Step 1.3: Run the Provided Behavior Script

The example above prints `51` then `2` even if `lookup` never consults the parent, because both `x` bindings sit in the scope where the lookup starts.  The provided `test_environment.py` checks that and four more behaviors:

1.  Lookup through three levels of nesting.
2.  `define` in an inner scope shadows the outer binding.
3.  `assign` from an inner scope updates the outer binding.
4.  `assign` to an undefined name raises.
5.  Scope restoration: after a child scope is discarded, the outer binding is unchanged.

> **Do this.**
> 1. Download [test_environment.py]({{ site.baseurl }}/files/starters/environments/test_environment.py) into `cs374-environments/`, next to `environment.py`, and run `python3 test_environment.py` from that folder.
> 2. Save the output for your submission: redirect it with `python3 test_environment.py > test_output.txt 2>&1`, or take a screenshot of the terminal.

> **You should see.** All five behaviors passing and no Python traceback.  If the script is built on `unittest`, the last lines are `Ran 5 tests` followed by `OK`.  A `FAILED` line names the behavior that broke; its number in the list above tells you which method to reread.

> **If it fails.**
> - Behavior 1 fails but Step 1.2 passed: `lookup` finds names in the current scope but never recurses to `self._parent`.
> - Behavior 3 fails: `assign` checks `self._bindings` and then creates the name there instead of deferring to the parent.
> - Behavior 5 fails: something in `define` or `assign` wrote into the parent's table directly.  Only `assign` may touch a parent, and only through the parent's own `assign`.

---

## Part 2: Predict and Check the Scope Trace

Write your predictions in `trace.md` before you run anything.  The test script comes with a short program of three nested blocks that mix `define` and `assign`.  Its shape is below, with every step numbered; if the copy in [test_environment.py]({{ site.baseurl }}/files/starters/environments/test_environment.py) differs from this listing, trace the script's copy and renumber the steps to match it.

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

### Step 2.1: Fill In the Trace Table Before You Run Anything

> **Do this.**
> 1. Copy the table below into `trace.md`, one row per numbered step, and fill in every row from the rules, not by running code.  Step 1 is done for you as a model.
> 2. Draw each chain in the same innermost-first notation as Part 0, naming the scopes `top`, `A`, `B`, and `C`.  In the Result column write the value printed (for a `print` step), the binding created or changed and in which scope (for a `let` or assignment step), or "enter" and "leave" for the braces.
> 3. Under the table, write the six values you expect `print` to produce, in order.

| Step | Line | Environment chain | Result |
|------|------|-------------------|--------|
| 1 | `let x = 1;` | `top{x=1}` | `x=1` created in `top` |
| 2 | `let y = 10;` | | |
| ... | one row per step, through step 20 `print y;` | | |

### Step 2.2: Run the Program Through Your Class and Compare

You do not have an evaluator yet, so run the program the way Step 1.2 did: translate each step into a call on your class.  This is a preview of exactly what the Interpreter assignment's `Let`, `Assign`, `Block`, and `Var` cases will do.

> **Do this.**
> 1. Create `trace_run.py` next to `environment.py` and start it from the listing below.
> 2. Finish the `# TODO`, one line per remaining step.  Each `{` becomes `Environment(parent=<the scope you are in>)`, each `}` means you go back to using the parent, and each `print` becomes a Python `print` of a `lookup`.
> 3. Run `python3 trace_run.py` and compare the six printed values with your predictions.  For any step where your prediction missed, write one sentence in `trace.md` naming the rule you misapplied (define versus assign, or which scope a lookup starts in).

```python
from environment import Environment

top = Environment()                              # the program's top-level scope
top.define("x", 1)                               # step 1:  let x = 1;
top.define("y", 10)                              # step 2:  let y = 10;
a = Environment(parent=top)                      # step 3:  enter block A
a.define("x", 2)                                 # step 4:  let x = 2;
a.assign("y", a.lookup("y") + a.lookup("x"))     # step 5:  y = y + x;
# TODO: steps 6 through 20, one line each, in the same style.
```

> **You should see.** Six lines of output, one per `print`, in the order of steps 12, 14, 15, 17, 19, and 20.  The provided script prints the same program step by step when you run `python3 test_environment.py --trace`, so you can check your table against it afterwards.  Do not look at that output before your table is filled in.  The prediction is the graded part.

### Step 2.3: Answer the Two Theory Questions

Close `trace.md` with two theory questions from the Binding and Scope session.

> **Do this.**
> 1. Which line of your class makes this language lexically scoped rather than dynamically scoped?  Quote the line and say what it would have to become for the rule to change.
> 2. Re-predict the trace program's final output under dynamic scoping, where the lookup chain follows the callers rather than the enclosing text, and name the step where the two rules first diverge.  If you conclude that they never diverge for this program, say why, and say what the program would need to contain before they could.

---

## Deliverables

Submit a ZIP containing the files below, with both partners named in `trace.md`.

| File or artifact | What it shows | Rubric row |
|------------------|---------------|------------|
| `trace.md` (top section): the shadowing trace tables, the unbound-variable decision, and two probe programs with predictions | You can settle a scope question on paper before writing code | Part 0: Before You Start |
| `environment.py` | `define`, `assign`, and `lookup` with parent chaining and `LangNameError` | The Environment Class |
| The passing `test_environment.py` output (log or screenshot) | All five behaviors pass, including the shadowing program's `51` then `2` | The Environment Class |
| `trace.md` (Part 2 section): the filled trace table, the comparison against the run, and both theory answers | Your predictions match the run, and you can point to the line that decides the scoping rule | Scope Trace Exercise |

`try_env.py` and `trace_run.py` are working files; include them if you like, but they are not graded.

---

## Self-Check Before You Submit

- [ ] Part 0's shadowing expression is traced with the environment drawn at every step, under both lexical and dynamic scope, with the diverging step marked (or the absence of one explained).
- [ ] Part 0 names the error an unbound variable raises and the moment it fires, and includes two probe programs with a prediction under each rule.
- [ ] `define` writes only into the current scope; `assign` never creates a binding, and `assign` to an undefined name raises `LangNameError` (not `KeyError`) with the name in the message.
- [ ] `lookup` chains through three levels of nesting, and `python3 test_environment.py` reports all five behaviors passing.
- [ ] The shadowing program prints `51` then `2`, and the outer binding is unchanged after the block.
- [ ] `trace.md` shows the environment chain at every step of the trace program, was written before the run, and notes any prediction that missed.
- [ ] Both theory questions are answered, and question 1 quotes the exact line of the class.
- [ ] Both partners are named in `trace.md`.

---

## Reflection Prompts

- What is the observable difference, in one example program, between a language where assignment creates bindings and one where it only updates them?
- If you worked in a pair, who did what, and name one thing your partner caught that you would have missed.  If you worked alone, note that instead.
