---
layout: assignment
permalink: /Assignments/Interpreter
title: "CS374: Principles of Programming Languages - The Interpreter"

info:
  coursenum: CS374
  purpose: "To give a small language its meaning, by walking through a tree-walking evaluator one kind of node at a time, with nested scopes, control flow, and staged errors."
  tilt:
    task: "For one given language, with its lexer and parser provided, write the evaluator in your choice of Python or C with Flex and Bison: expressions, an environment with nested scopes, control flow, and staged errors.  Then state your language's rules in a short SEMANTICS.md."
    criteria: "I grade this on a correct evaluator that passes the provided programs and hidden ones, scopes that behave as the language's rules say, short-circuit logic and loop control that work, staged errors with line numbers, and a SEMANTICS.md whose examples show real output.  The rubric applies the same way to both options."
  points: 100
  goals:
    - To evaluate expressions over an AST with strong dynamic typing
    - To implement nested scopes with an environment that distinguishes definition from assignment
    - To implement short-circuit logic, conditionals, loops, break, and continue
    - To report errors by stage, with line numbers, and never with a crash
    - To state a language's semantics precisely, with examples that show real output
  rubric:
    - weight: 10
      description: "Part 0: Trace by Hand"
      preemerging: No trace is attempted
      beginning: The program is traced, but the environment is not shown at each step
      progressing: The environment is shown at every step, but the printed values are wrong, or the scopes are not told apart
      proficient: The program is traced one statement at a time, showing which scope holds each name and the value each step produces
    - weight: 25
      description: "Expressions (Goal 1)"
      preemerging: The evaluator does not run, or handles only literals
      beginning: Arithmetic runs, but type errors crash or are not raised, or a boolean counts as a number
      progressing: Arithmetic and comparisons work, but one case is wrong, such as division by zero crashing, or equality across types
      proficient: Literals, unary minus, arithmetic, comparison, and equality are all correct; type errors name the operator and both types at the right line; division by zero is a language error; and the provided expression programs pass
    - weight: 25
      description: "Environments and Scopes (Goal 2)"
      preemerging: There is no environment, or all names share one flat table
      beginning: Names can be defined and read, but a block's names leak out, or assignment creates new names
      progressing: Blocks scope correctly, but one case is wrong, such as assignment failing to reach an outer scope
      proficient: "`let` creates a binding in the current scope; assignment changes the nearest existing binding and never creates one; lookup follows the parent links; every block gets a new scope; undefined names are language errors with a line number; and the provided scope programs pass"
    - weight: 20
      description: "Control Flow (Goal 3)"
      preemerging: Conditions or loops are missing
      beginning: "`if` and `while` run, but `and` and `or` always evaluate both sides, or `break` and `continue` are missing"
      progressing: Most control flow works, but one case is wrong, such as `continue` ending the loop, or a `break` inside an `if` not reaching its loop
      proficient: "`and` and `or` short-circuit and return an operand; `if`, `else if`, and `while` follow the truthiness rule; `break` and `continue` reach the nearest loop from any depth; and the provided control-flow programs pass"
    - weight: 10
      description: "Staged Errors (Goal 4)"
      preemerging: Errors crash with a traceback or a C fault
      beginning: Some errors are reported, but with no stage or no line
      progressing: Most errors carry their stage and line, but one class does not, such as a stray `break`
      proficient: Every lexical, syntax, and runtime error prints one staged line with its line number, and a stray `break` or `continue` is a runtime error
    - weight: 10
      description: "SEMANTICS.md and Your Own Programs (Goal 5)"
      preemerging: No SEMANTICS.md, or no programs of your own
      beginning: Rules are stated with no examples, or the output shown is not real
      progressing: Most rules have examples and real output, but one is missing or vague
      proficient: Each of the four rules is stated in one or two sentences, with an example program and its real output; and three programs of your own, each with a `.expected` file, pass
  readings:
    - rtitle: "Tree-Walking Interpretation Activity"
      rlink: "Activities/liascript-interpretation.md"
      liapage: true
    - rtitle: "Binding, Scope, and Environments Activity"
      rlink: "Activities/liascript-bindingscope.md"
      liapage: true
    - rtitle: "Control Flow Semantics Activity"
      rlink: "Activities/liascript-controlflowsemantics.md"
      liapage: true
    - rtitle: "Flex and Bison, Complete (Tutorial, for the Flex and Bison option)"
      rlink: "../Tutorials/FlexAndBison"
    - rtitle: "Build a Complete Interpreter in Python (Tutorial, not required)"
      rlink: "../Tutorials/BuildAnInterpreter"

tags:
  - interpreter
  - languages
  - pipeline

---

A parser hands you a tree, and a tree does nothing on its own.  In this assignment you write the part that gives it meaning: an evaluator that walks the tree and runs each node.  The lexer and parser are provided for one small language, so this assignment does not depend on your earlier work.  You choose the language you write the evaluator in.

## Choose Your Option

The two options use the same language, pass the same test programs, and are graded by the same rubric.

| Option | You are given | You write | Pick this if |
|---|---|---|---|
| **Python** | `lexer.py`, `parser.py`, `ast_nodes.py` | `interpreter.py`, `mylang.py` | you want to spend your time on the evaluator itself |
| **Flex and Bison** | `scanner.l`, `parser.y`, `ast.h`, `ast.c`, `main.c`, `Makefile` | `eval.c` | you want to read a generated scanner and parser, and to see what Python was doing for you |

The steps below are the same in both, so each step explains the idea once and then shows what it looks like in each option.

## Before You Start

Make a folder named `cs374-interpreter`.  From the [starter kit]({{ site.baseurl }}/files/starters/interpreter/), copy in the files of your option (`python/` or `flexbison/`) and the `programs/` folder.  Each program in `programs/` has a `.expected` file with its exact output.  Then make sure it runs.

*Python*, with Python 3.10 or newer:

```bash
python3 test_interpreter.py
echo 'print 42;' | python3 mylang.py
```

*Flex and Bison*, with `flex`, `bison`, `gcc`, and `make` installed (on Ubuntu or WSL, `sudo apt install flex bison gcc make`):

```bash
make test
echo 'print 42;' | ./mylang
```

> **You should see.** A list of `FAIL` lines ending in `0 passed, 16 failed`, and then an error about a node with no case yet.  That is your to-do list.  The `PASS` lines grow as you work, and you are done with the code when you reach `16 passed, 0 failed`.

The grammar your parser accepts, so you know what trees to expect:

```text
stmt   ->  let ID = expr ;  |  ID = expr ;  |  print expr ;
        |  if expr block ( else ( if ... | block ) )?  |  while expr block
        |  break ;  |  continue ;  |  block
block  ->  { stmt* }
expr   ->  or, and, not, then comparisons, then + -, then * /, then unary -, then
           NUM  |  true  |  false  |  ID  |  ( expr )
```

---

## Part 0: Trace by Hand

An evaluator is a function from a tree and an environment to a value, and almost every bug is a disagreement between what you thought the environment held and what it held.  So trace one program on paper first, in `notes.md`:

```text
let x = 2;
let y = x + 3;
{
    let x = 10;
    print x * y;
}
print x;
```

> **Do this.** Go one statement at a time.  At every step, write which scope holds each name, and what value the step produced.  The two `print`s are the interesting ones: if you get `50` and then `2`, your model of scope is right.

---

## Part 1: Expressions

### Step 1: Literals and print

The evaluator is one function that looks at the kind of node and does what that kind means.  A leaf holds its answer, and any other node calls the evaluator on its children first.  That recursion is all a tree walker is.

*Python.*  `eval_node` is an `isinstance` chain, and `Num` and `Program` are done for you.  Add two branches:

```python
        elif isinstance(node, BoolLit):
            ...  # TODO: return the value the node holds, as Num does.
        elif isinstance(node, Print):
            ...  # TODO: evaluate node.value, and print format_value of the result.
```

*Flex and Bison.*  C keeps expressions and statements apart: `eval` returns a `Value`, and `exec` runs a statement.  `N_NUM` is done for you.  Add `N_BOOL` to `eval`, using `make_bool`, and `N_PRINT` to `exec`, using `print_value`.

> **You should see.** `PASS 01-print.ml`.

### Step 2: Arithmetic and type errors

Your language has strong dynamic typing: `true + 1` is an error when it runs.  You check before you compute, because the host language would happily do something else.  Python would call that `2`, and in C a boolean is a number underneath.

```text
eval BinOp:
    left = eval left child
    right = eval right child
    if either is not a number: type error naming the operator and both types
    if op is / and right is 0: division by zero error
    apply the operator
```

Unary minus is the same with one child, and its message is `unary minus requires a number, got bool`.  The message for the rest reads exactly `'+' requires numbers, got bool and num`.

*Python.*  Add `UnaryOp` and `BinOp` branches, using `is_number` and `type_name`, and raise `LangTypeError(message, node.line)` or `LangZeroDivisionError("division by zero", node.line)`.  A dictionary from operator to a two-argument `lambda` saves you four `if`s, and it will hold the comparisons in Step 3.

*Flex and Bison.*  Add `N_NEG` and `N_BINOP` to `eval`, testing `v.is_bool`, and use `RUNTIME_ERROR(n->line, "...", ...)`, which prints the staged line and stops.  An inner `switch (n->op)` picks the operator.

> **You should see.** `PASS 02-arithmetic.ml`.  Programs 03 and 04 pass after Step 7, once errors print as staged lines.  For now, `print true + 1;` should raise your error in Python, and should already print its line in C.

### Step 3: Comparison and logic

Comparisons are `BinOp`s too.  `<`, `<=`, `>`, and `>=` need numbers and give a boolean, so they share the number check.  `==` and `!=` take any pair, and values of different types are simply not equal, so `true == 1` is false.  Do that check before the number check.

`and` and `or` are different: they must not evaluate the right side when the left side already decides the answer.  This is a rule of the language and not an optimization, because `true or (1 / 0)` must not raise an error.  So they cannot share the `BinOp` code, which evaluates both children first.

```text
eval and:                                  eval or:
    left = eval left child                     left = eval left child
    if left is not truthy: return left         if left is truthy: return left
    return eval right child                    return eval right child
```

Truthiness lives in one function, so that every construct agrees: `false` and `0` are false, and everything else is true.  `not` gives a real boolean, the opposite of its operand's truthiness.

*Python.*  Fill in `truthy`, testing `is False` so that you do not depend on `0 == False`.  Add a `LogicOp` branch, and add `"not"` to your `UnaryOp` branch.

*Flex and Bison.*  Fill in `truthy`, and add `N_AND`, `N_OR`, and `N_NOT` to `eval`.

> **You should see.** `PASS 05-logic.ml`.

---

## Part 2: Environments

### Step 4: Scopes

An environment answers "what does this name mean right now?"  One scope is a table of names plus a link to the scope that encloses it.  A lookup checks its own table and then follows the links outward, so the nearest binding wins:

```text
{ let x = 51; print x; }        block scope:   x = 51    ---parent--->    global scope:   x = 2
print x;

lookup x from the block finds 51.  Lookup x from the global scope finds 2.
```

Three operations cover every use, and the difference between the last two is the point:

```text
define(name, value):   put it in THIS scope, even if an outer scope has the name.  (let)
lookup(name):          this scope, then each parent.  Not found anywhere is an error.
assign(name, value):   find the nearest scope that has the name, and change it there.  Not found is an error.
```

A block makes a new scope whose parent is the current one, and runs its statements there.  When the block ends, nothing refers to that scope any more, so its names are gone.

*Python.*  Fill in the three methods of `Environment` in `interpreter.py`.  The messages read `Undefined variable 'x'` and `Cannot assign to undefined variable 'x'`, and each error carries the `line` passed in.  Then add four branches to `eval_node`:

```python
        elif isinstance(node, Var):
            ...  # TODO: return env.lookup(node.name, node.line).
        elif isinstance(node, Let):
            ...  # TODO: evaluate node.value in env, then env.define it.
        elif isinstance(node, Assign):
            ...  # TODO: evaluate node.value in env, then env.assign it, with node.line.
        elif isinstance(node, Block):
            ...  # TODO: make Environment(env), and evaluate each of node.stmts in it, not in env.
```

*Flex and Bison.*  Fill in `env_define`, which puts a new `Binding` at the front of this scope's list, and `env_find`, which searches this scope and then each parent and returns the `Binding` or `NULL`.  Assignment is `env_find` plus a change to `->value`, and `NULL` means the error.  Add `N_VAR` to `eval`, and `N_LET` and `N_ASSIGN` to `exec`.  `N_BLOCK` is `return exec_list(n->a, env_new(env));`.  You do not need to free scopes for programs this small.

> **You should see.** `PASS 06-scope.ml`.  If `x` prints `51` both times, your block ran in the parent scope, or `let` called assign.

---

## Part 3: Control Flow

### Step 5: If and while

`if` evaluates its condition, asks `truthy`, and runs one branch.  An `else if` is just an `else` branch that is itself an `if`, so it needs no special case.  `while` evaluates its condition again on every pass, which is what lets the body change the answer.

```text
exec while:
    while truthy(eval condition):
        run the body
```

The body is a block, and a block makes a new scope each time it runs, so a `let` in the body starts fresh on each pass and does not survive the loop.

*Python.*  Add `If` and `While` branches.  *Flex and Bison.*  Add `N_IF` and `N_WHILE` to `exec`, keeping what `exec` returns for Step 6, and remember `n->c` may be `NULL`.

> **You should see.** `PASS` for programs 09 and 10.  Program 11 passes after Step 7.

### Step 6: Break and continue

A `break` may sit inside an `if` inside a block inside the loop.  So when it runs, every call between it and the loop has to stop, and the loop has to find out why.  The two options do this differently, and comparing them is worth a minute.

*Python.*  An exception does the unwinding for you.  A `Break` branch raises `BreakSignal(node.line)`, and `Continue` raises `ContinueSignal(node.line)`.  Every call in between stops on its own.  The `While` branch catches them around the one line that runs the body, inside the loop:

```python
            while ...:
                try:
                    ...  # TODO: run the body
                except BreakSignal:
                    ...  # TODO: leave the Python loop
                except ContinueSignal:
                    ...  # TODO: go back to the condition
```

Put the `try` around the whole loop instead, and `continue` ends the loop, because nothing is left to run.

*Flex and Bison.*  C has no exceptions, so `exec` returns how each statement finished: `S_NORMAL`, `S_BREAK`, or `S_CONTINUE`.  `N_BREAK` sets `signal_line = n->line` and returns `S_BREAK`.  `exec_list` already stops early and passes the signal up.  So `N_IF` and `N_BLOCK` need only return what they ran, and `N_WHILE` is where it stops: `S_BREAK` leaves the loop, `S_CONTINUE` goes back to the condition, and the `while` itself returns `S_NORMAL`.

> **You should see.** `PASS` for programs 12 and 13.

---

## Part 4: Errors and Meaning

### Step 7: Staged errors

A user should be able to tell a typo from a mistake in logic without reading a traceback.  So every error names the stage that caught it.  A program that fails to parse never starts running, so it prints nothing before its error:

```text
Lexical error at line 2: unexpected character '@'
Syntax error at line 2
Runtime error at line 2: division by zero
Runtime error at line 2: 'break' outside loop
```

*Python.*  Fill in `run_source` in `mylang.py`.  It returns `None`, or one of these lines:

```python
def run_source(source):
    """Run one program through every stage.  Return None, or one staged error line."""
    # TODO: parse the source.  A LexError gives the Lexical line, using err.line and err.message.
    #       A ParseError gives the Syntax line.  Return as soon as one happens.
    # TODO: evaluate the tree.  Any LangError gives the Runtime line.  They share one parent class,
    #       so one except covers them all.
    # TODO: a BreakSignal or a ContinueSignal that gets this far was outside any loop.  They are not
    #       LangErrors, so they need their own excepts.
    return None
```

*Flex and Bison.*  The scanner and parser already print their lines, and `RUNTIME_ERROR` prints the rest.  One case is left: in `run_program`, a signal other than `S_NORMAL` that reaches the top was outside any loop.  Report it at `signal_line`.

> **You should see.** `16 passed, 0 failed`.

### Step 8: SEMANTICS.md and your own programs

A language is only as well defined as what you can say about it.  Write `SEMANTICS.md` with one section per rule below.  Each section states the rule in one or two sentences, gives a short program, and shows that program's real output.  Run them, and paste what they print.  If your prose and your program disagree, one of them is wrong.

1. **Truthiness.**  Which values are false, and what does `print 0 or 5;` print?
2. **Scope.**  Where does `let` define, and where does assignment reach?
3. **Loop scope.**  Does a `let` in a loop body survive the loop?
4. **Types.**  What does `print true + 1;` do, and what does `print true == 1;` do?

Then add three programs of your own to `programs/`, each with a `.expected` file.  Aim each at something the provided programs do not check, such as a `break` in a nested loop.

---

## Deliverables

Submit a ZIP containing:

| File | What it shows | Rubric row |
|------|---------------|------------|
| `notes.md` | your Part 0 trace | Part 0 |
| `interpreter.py` and `mylang.py`, or `eval.c` | your evaluator | Expressions; Environments and Scopes; Control Flow; Staged Errors |
| `SEMANTICS.md` | the four rules, with real output | SEMANTICS.md and Your Own Programs |
| `programs/` | the provided programs and your three | SEMANTICS.md and Your Own Programs |

Leave the provided files unchanged, since I run your evaluator with the originals and with hidden programs.

## Self-Check Before You Submit

- [ ] The test runner ends in `0 failed`, including your three programs.
- [ ] `true or (1 / 0)` prints `true`, with no error.
- [ ] A `let` in a block does not change the outer name, and an assignment in a block does.
- [ ] `continue` goes back to the condition, and `break` leaves only the nearest loop.
- [ ] Every example in `SEMANTICS.md` shows output you actually ran.

## Reflection Prompts

- Point to the exact line in your code that makes a block's names disappear when it ends.
- Short-circuiting is a rule of the language.  What behavior would change if `and` and `or` evaluated both sides?
- Python's exceptions and C's returned signals both carry a `break` out to its loop.  What does each one make easy, and what does each one hide?
