---
layout: textbook
permalink: /Tutorials/EnvironmentsExtensions
title: "CS374: Optional Extensions to the Environments Tutorial"

info:
  coursenum: CS374
  eyebrow: "Tutorial"
  numbering: false
  objectives:
    - "Trace lexical and dynamic scope by hand on the same program"
    - "Work through models of runtime type checking, type inference, and a type-error postmortem"
    - "Extend the tutorial's checker with the remaining type rules, and run it on real source files"

tags:
  - scope
  - types
  - tutorial

---

Everything here is optional and earns no points.  These sections go deeper into both halves of [Environments and Type Checking]({{ site.baseurl }}/Assignments/EnvironmentsLab): paper traces of lexical and dynamic scope, worked models of type systems, the remaining type rules, and running the checker on real source files.  Where a section asks for written answers, put them in `notes.md` under the section's name.

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

> **Have ready.** Both probe programs and all four predictions.  Run them against the Mystery Scoping Language interpreter in Part II of the *Binding and Scope* activity.

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

This extension opens with a short paper exercise, then four worked models: a runtime checker for the interpreter you are building, a trace of it on compound expressions, inference by hand, and a type-error postmortem.  Each model has a script you can run and questions to talk through (with your partner, if you have one).  They go further than Part 2 into what a type system buys and costs.

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

The checker you wrote in Part 2 produces the same kind of message, with two differences: it names a line and column, and it fires before the program runs rather than while it runs.

`type_name` turns a Python type into the name the error messages print.  The first `if` in `eval_binop` handles arithmetic: it allows string concatenation, refuses booleans, computes on two floats, and refuses everything else.  The second `if` handles comparisons, which require both sides to have the same type.

##### Critical Thinking Questions

1.  Identify the lines that make this typing *strong* (refusals) versus the line that would make it *weak* if you replaced a refusal with `float(...)` coercion.  Make the weak version mentally: what does `3.0 + "cd"` return, and what bug class did you just legalize?
2.  We licensed `+` for two strings but not `*` for string and number.  Python licenses `"ab" * 3`.  Debate and record your project's policy on string repetition, and add it to `SEMANTICS.md` (your team language's semantics document).
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

Weak typing is dangerous because the program does not crash.  When a language coerces instead of refusing, a type mistake flows onward as a plausible-looking value, and the first symptom appears far from the cause, often outside the program entirely.

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

The checker in Part 2 handles literals, variables, binary operators, and conditions.  The class language has three more constructs, and the starter's AST already includes their node classes: `Assign`, `LogicOp`, and `UnaryOp`.  Right now `check_stmt` and `check_expr` raise `NotImplementedError` for them.  Each rule below follows the same unknown-type rule as Part 2: when a type it compares is `None`, it skips the check.

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

> **You should see.**  Twelve labels.  Seven are followed directly by the next label (silent acceptance).  Five are followed by exactly one `Type error at line L, col C: ...` line, and each of those names two types.  With the parser the activities build and the message forms from Steps 2.3 and 2.4, the whole log is exactly this.  Your positions must match; your wording after each colon may differ.
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

These four questions come from the *Binding and Scope*, *Scope Chains and Closures*, and *Type Systems* sessions.  Answer each in a few sentences.

**Scope.**

> **Do this.**
> 1. Which line of your class makes this language lexically scoped rather than dynamically scoped?  Quote the line and say what it would have to become for the rule to change.
> 2. Re-predict the trace program's final output under dynamic scoping, where the lookup chain follows the callers rather than the enclosing text, and name the step where the two rules first diverge.  If you conclude that they never diverge for this program, say why, and say what the program would need to contain before they could.

**Types.**

1.  Place four languages (Python, C, Haskell, and JavaScript) on the static/dynamic × strong/weak quadrant, with one sentence of justification each.
2.  Your checker makes the class language *gradually* typed in spirit: annotated declarations are checked, and unannotated territory is documented as unchecked.  State one benefit and one risk of that middle ground, using the mypy/TypeScript comparison from class.
