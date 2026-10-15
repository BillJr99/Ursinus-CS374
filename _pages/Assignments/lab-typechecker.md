---
layout: assignment
permalink: /Assignments/TypeCheckerLab
title: "CS374: Principles of Programming Languages - Lab: Type Checker Starter"

info:
  coursenum: CS374
  purpose: "To build the core of the Interpreter assignment's required static type checker, individually or with a partner, covering literal, variable, and operator checks over the class AST, all running before any code is evaluated."
  tilt:
    task: "Individually or with a partner, implement a checker that walks the class AST with a type environment, verifying annotated declarations, variable uses, and operator applications, and reporting positioned type errors."
    criteria: "I grade this on a checker that accepts the well-typed programs and rejects each ill-typed program with a positioned two-type error message, plus a set of typing-rule statements written on paper.  See the rubric below for the full breakdown."
  points: 15
  goals:
    - To implement a static checking pass over the class AST using a type environment that mirrors the Environment class
    - To check annotated declarations, variable uses, and operator applications, reporting errors with positions and both conflicting types
    - To state typing rules precisely on paper before encoding them
  rubric:
    - weight: 10
      description: "Part 0: Before You Start - Type Systems"
      preemerging: No program is annotated and no rejected expression is found
      beginning: A program is annotated but no expression is identified that a checker would reject
      progressing: An annotated program and a rejected expression are given, but the write-up does not state a preference between the static and dynamic behavior, or names no guarantee and no forbidden program
      proficient: Each subexpression of a small program is annotated with its expected type; one expression a static checker rejects but a dynamic language would run is identified, with a defended preference for one behavior; and one guarantee a type system buys is stated alongside one program it forbids that you wish it allowed
    - weight: 63
      description: "The Checker Core (Goals 1, 2)"
      preemerging: The checker is missing, or it never rejects an ill-typed program
      beginning: The checker rejects some ill-typed programs but misses operator mismatches, or it crashes on programs it should reject cleanly
      progressing: All provided ill-typed programs are rejected, but error messages lack positions or name only one of the two conflicting types
      proficient: Every provided well-typed program is accepted and every ill-typed program rejected with a message of the form "Type error at line L, col C" naming both conflicting types; the type environment correctly scopes annotations through nested blocks
    - weight: 27
      description: "Typing Rules on Paper (Goal 3)"
      preemerging: No rules are written, or they contradict the implemented checker
      beginning: Rules are written for literals only
      progressing: Rules cover literals, variables, and operators but at least one rule is imprecise about its premises
      proficient: Each covered construct has a precise rule (premises above, conclusion below, or a disciplined if/then sentence), and each rule cites the checker function that implements it
  readings:
    - rtitle: "Type Systems Activity"
      rlink: "Activities/liascript-types.md"
      liapage: true
    - rtitle: "Core Tutorial: Typing Disciplines, Strong vs. Weak, Static vs. Dynamic, and Gradual Typing"
      rlink: "../Tutorials/TypingDisciplines"

tags:
  - interpreter
  - types
  - languages
  - lab

---

This **lab** builds the core of the Interpreter assignment's Part 4: a small static type checker that runs between parsing and evaluation.  A static type checker reads the abstract syntax tree (AST) of a program and decides whether each operation makes sense before any of the program runs.  Working alone or with a partner (see the pair policy below), you get the checker working on its three simplest cases: literals, variables, and operators.  You leave with a `typechecker.py` that accepts seven of the twelve provided programs and rejects the five ill-typed ones, a run log that shows it doing so, and a `RULES.md` that states each typing rule you implemented.  The Interpreter assignment then has you extend the checker on your own to call sites and return types.  Plan on one working session.

**Pair policy.**  You may do this lab in pairs.  Submit the same files, name both partners in them, and you will both earn the same grade.  Working alone is also allowed.  The Interpreter assignment remains individual work: both partners may carry this shared checker core into it, but the extension to calls and returns must be your own.

---

## Before You Start

- An AST to walk: the node classes from your Parser assignment, or the [reference parser and AST]({{ site.baseurl }}/files/reference/reference-parser.zip) released with the Interpreter assignment hand-out.  If your submission builds on a reference component, say so in one line in your submission; that is the entire requirement, and it costs no points.
- The `Environment` class from your Environments lab.  The type environment you build in Part 1 has the same shape and borrows its method names.
- Python 3.10 or newer; `python3 --version` should print `Python 3.10` or later.  Nothing needs to be installed; the checker is standard-library Python.
- A terminal and an editor.  If the terminal is still new to you, the [Course Development Environment]({{ site.baseurl }}/Tutorials/DevEnvironment) and [Shell Skills for Language Development]({{ site.baseurl }}/Tutorials/ShellForLanguageDev) tutorials cover everything this lab asks you to type.

Make one folder for the lab and copy your AST, parser, and lexer files into it, so `typechecker.py` can import them with a plain `import`.  If you build on the reference parser, unzip it and copy its `ast_nodes.py`, `parser.py`, `lexer.py`, and `tokens.py` into the folder.  Then make a `programs/` folder and copy the [twelve provided programs]({{ site.baseurl }}/files/starters/typechecker/programs/) into it now, because Steps 1.4 and 1.5 run them.  Make an empty `mytests/` folder too, for the small test programs you write along the way.  The steps below assume this layout:

```text
cs374-typechecker/
  ast_nodes.py       # your AST node classes (or the reference copy); Step 1.3 adds a field to Let
  parser.py          # your parser (or the reference copy); Step 1.3 teaches let to read ": Num"
  lexer.py           # your lexer (or the reference copy); Step 1.3 adds a COLON token
  tokens.py          # the reference lexer's Token class, if you use the reference lexer
  typechecker.py     # Part 1: type environment, check(), and a file driver
  programs/          # the twelve provided programs, 01- through 12-
  mytests/           # your own small test programs (not submitted)
  runlog.txt         # Step 1.5: the checker's output over all twelve programs
  RULES.md           # Part 0 write-up and Part 2 typing rules
  model1_strong.py   # Part 0 worked models (yours to keep; not submitted)
  model2_trace.py
  model3_infer.py
  model4_postmortem.py
  explore_tenv.py    # Step 1.1 scratch file (not submitted)
```

Each step below names the one file you work in.  This table is the whole map, so you can see where each piece lands before you start:

| Step | File you work in | What you do there |
|---|---|---|
| Part 0 paper | `RULES.md` (top), or a photo of your page | answer the four paper questions |
| Models 1 to 4 | `model1_strong.py`, `model2_trace.py`, `model3_infer.py`, `model4_postmortem.py` | paste each script, run it, and compare the output |
| 1.1 | `explore_tenv.py` | try a type environment in plain dicts (scratch, not submitted) |
| 1.1 | `typechecker.py` | create the file from the skeleton; fill in `define` and `lookup` |
| 1.2 | `typechecker.py`, `mytests/literals.ml` | type `Str` and `BoolLit`; check `Print` |
| 1.3 | `lexer.py`, `ast_nodes.py`, `parser.py` | add the `COLON` token, the `annotation` field, and the `: Type` in `parse_let_stmt` |
| 1.3 | `typechecker.py`, `mytests/declare.ml`, `mytests/undeclared.ml`, `mytests/mismatch.ml` | check `Let`, `Var`, `Block`, and `Assign` |
| 1.4 | `typechecker.py`, `mytests/add_bool.ml` | check `BinOp`, `LogicOp`, `UnaryOp`, `If`, and `While` |
| 1.5 | `runlog.txt` | run all twelve provided programs and keep the output |
| 2.1, 2.2 | `RULES.md` | write one typing rule per construct, then the two theory answers |

This lab lands inside the Interpreter assignment's window; see the course schedule for the assigned and due dates.

> **Time budget.**  About three hours in one working session: fifteen minutes on the paper exercise, forty-five minutes reading and running the four worked models, an hour and a half on the checker, and thirty minutes writing the rules.

---

## Part 0: Worked Models (read before you code)

Part 0 opens with a short paper exercise, which is the graded piece.  The rest is four worked models from the Type Systems class session: a runtime checker for the interpreter you are building, a trace of it on compound expressions, inference by hand, and a type-error postmortem.  Each model has a script you can run and questions to talk through (with your partner, if you have one).  Read all four before you start Part 1.

### Type Systems on Paper

Plan on about fifteen minutes with pencil and paper.  Everyone has an opinion about static typing; an example is what makes the argument worth having.

**You write (at the top of `RULES.md`, or on paper you photograph):** the annotated program, the rejected expression with your preference, and the guarantee and forbidden program.  No code.

> **Do this.**
> 1. Write a small program and annotate each subexpression with the type you expect it to have.
> 2. Find one expression in it that a static type checker would reject but a dynamic language would run.  Say which behavior you prefer there, and why.
> 3. State one guarantee a type system gives you, and one program it forbids that you wish it allowed.
> 4. Write your answers at the top of `RULES.md`, or put a photo of your page in the ZIP.

> **Bring to class.**  The program you wish the checker had allowed, even if you could not settle the question.  The unsettled cases are the ones we argue about, and Part 1 makes you take a side in code.

### Model 1: A Dynamically, Strongly Typed Core

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

Those refusals are the whole lab in miniature.  The checker you write in Part 1 produces the same kind of message, with two differences: it names a line and column, and it fires before the program runs rather than while it runs.

`type_name` turns a Python type into the name the error messages print.  The first `if` in `eval_binop` handles arithmetic: it allows string concatenation, refuses booleans, computes on two floats, and refuses everything else.  The second `if` handles comparisons, which require both sides to have the same type.

#### Critical Thinking Questions

1.  Identify the lines that make this typing *strong* (refusals) versus the line that would make it *weak* if you replaced a refusal with `float(...)` coercion.  Make the weak version mentally: what does `3.0 + "cd"` return, and what bug class did you just legalize?
2.  We licensed `+` for two strings but not `*` for string and number.  Python licenses `"ab" * 3`.  Debate and record your project's policy on string repetition, and add it to `SEMANTICS.md` (the Interpreter assignment's semantics document).
3.  Where would a *static* checker for your language live in the pipeline (between which two existing stages), and what would it walk?  You already own every data structure it needs; name them.

Python raises a TypeError on `"5" - 1` at the moment the subtraction executes, never silently converting.  On the two axes, is Python statically and weakly typed, statically and strongly typed, dynamically and strongly typed, or dynamically and weakly typed?

> **Answer.**  Dynamically and strongly typed.

A language that deduces `n: int` from `let n = 5` without requiring the programmer to write the type annotation is using dynamic typing, weak typing, type inference, or duck typing?

> **Answer.**  Type inference.

> **Watch out.**  Duck typing (Python's "if it walks like a duck and quacks like a duck, treat it as a duck") is still a form of typing: a dynamic, structural one, where compatibility is checked by whether an object supports the required operations rather than by its declared class.  Saying a language "has no types" because it uses duck typing is incorrect.

### Model 2: Tracing the Runtime Checker on a Compound Expression

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

#### Critical Thinking Questions

4.  The trace shows the checks firing in steps 1, 2, 3, the same order as evaluation.  State the general rule: in a dynamically typed interpreter, when does the check for an operator fire, relative to the evaluation of that operator's operands?
5.  In the failing trace, step 1 finished before the TypeError at step 2.  Suppose step 1 had been `print("charging card...")` instead of an addition.  What does this tell you about *where in a program's lifetime* you would prefer type errors to fire, and which typing discipline delivers that?
6.  Redo the failing trace as a *static* checker would perform it, before execution: rewrite the table with types only, no values.  Which columns disappear, and which check still fails?
{: start="4"}

### Model 3: Type Inference by Hand

Type inference is the trick where the checker works out every variable's type from context alone: you write `let a = 2` and it deduces `a: int` without you saying so.  Mechanically, it is a tree walk.  Visit each node, compute the type it must produce, and pass that type upward.  When two branches disagree (for example, adding an `int` to a `str`), the checker reports an error *at that node*, which can be far from the actual mistake.

The script below is a miniature of bottom-up type inference: it works out each `let` binding's type from its initializer, with no annotations.  It is not full Hindley-Milner inference, which adds type variables and unification so that it can also infer the types of function parameters; here every expression's type is fixed by its parts, so a single bottom-up walk is enough.  Each `if kind == ...` branch of `infer` is one typing rule, and the `let` branch is where the type environment grows.  This is the closest model to what you build in Part 1: your checker walks the same way and keeps the same kind of environment, but reads the type from the annotation on each `let` instead of deducing it from the initializer.

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

#### Critical Thinking Questions

7.  The inference trace shows `let a: int`, `let b: int`, `let c: bool`.  These are determined entirely from the *values* (literals), with no type annotations written.  Is this static or dynamic typing?  Explain.
8.  When inference encounters `a + "hello"`, it reports the error at the `add` expression.  But the *root cause* is that `a` was given an int value.  How far is the reported error from the root cause, and what does this say about inference error message quality?
9.  What would need to change to support `let a = 2; let b = a + 3.0;`?  (Hint: numeric type widening, `int + float -> float`.)  Modify the `infer` function to allow this.
{: start="7"}

### Model 4: A Type-Error Postmortem

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

#### Critical Thinking Questions

10.  Walk the postmortem table: at which step did the *type* first go wrong, and at which step did the *money* first go wrong?  Why is it significant that these are different steps?
11.  Step 2 coerced number -> string, but step 3 coerced string -> number.  Write the coercion rule a language designer would have to publish to justify both choices at once.  Does the result sound principled or accidental?
12.  The weak-mode run produces no error at any point; the bug would surface only as customer complaints.  Name two other places in the software pipeline (besides the language's type system) where this bug could have been caught, and what each catch would cost compared to a step-2 TypeError.
13.  For your project language: which, if any, of these coercions will you allow?  Record the decision in `SEMANTICS.md`, citing this postmortem as evidence for or against.
{: start="10"}

---

## Part 1: Build the Checker Core

Implement `check(program) -> None` in `typechecker.py`.  The function walks the class AST (your Parser assignment's AST nodes, or the reference AST) and reports a type error as soon as it finds one.  A well-typed program produces no output.  The checker carries a type environment as it walks: the same parent-chaining discipline as the `Environment` class from your Environments lab, but each name is bound to a *type* instead of a value.  Entering a block creates a child environment, and leaving the block discards it.

Your checker enforces these rules:

- **Literals:** numbers are `Num`, strings are `Str`, booleans are `Bool`.
- **Declarations:** `let x: Num = expr;` checks that `expr`'s type equals the annotation, then binds `x : Num` in the current scope.  A mismatch is an error naming both types.
- **Variables:** a use of `x` looks up its declared type.  An undeclared name has no type the checker can know, so its type is *unknown*: the checker skips every check that involves it, and the evaluator reports the undefined name when the program runs.
- **Operators:** `+ - * /` require `Num` operands and yield `Num`; `< <= > >=` require `Num` and yield `Bool`; `== !=` require both sides to have the same type and yield `Bool`; `and`/`or`/`not` require `Bool`.  Every violation is reported as `Type error at line L, col C: ...` naming **both** conflicting types.

The five steps below build the checker in the order that keeps it testable at every stage.  Run the provided programs after each step and keep the output as your run log.

### Step 1.1: Write the type environment

The environment comes first because every later rule either binds into it or looks up from it.  The skeleton below is the whole file; each later step fills one group of `TODO` markers.

#### Before You Code: How a Type Environment Lives in Python

Picture the checker halfway through program `06-shadowing.ml`.  It has read `let x: Num = 1;` at the top, and it has just stepped inside the `{ ... }` block and read `let x: Str = "inner";`.  At that moment it needs to remember two facts: the outer `x` is a `Num`, and the inner `x` is a `Str`.  It does not need to remember the values `1` or `"inner"` at all.  A type checker remembers types, never values.

That makes the type environment simpler than your `Environment` class.  Every piece is something you have already used:

| Idea | In Python | Example |
|---|---|---|
| a type | a plain string | `"Num"`, `"Str"`, `"Bool"`, kept in the constants `NUM`, `STR`, `BOOL` |
| one scope | a `dict` from each name to its type string | `{"x": "Num"}` |
| a nested block | a new, empty scope that remembers its parent | `TypeEnvironment(parent=env)` |
| declare a name | store a key in this scope's dict only | `self.bindings[name] = typ` |
| look up a name | this scope's dict first, then the parent's, and so on | `"x" in self.bindings`, then `self.parent` |
| a name no scope has | `None`, meaning "unknown type"; the checker skips it, and the evaluator reports the name at run time | `return None` |
| a type error | an `Exception` subclass that carries a line and a column | `LangTypeError(message, line, col)` |

Two details in that table matter later.  First, shadowing is free: the inner block writes `x` into its *own* dict, so the outer dict still says `Num`, and when the block ends you simply stop using the inner dict.  Second, `LangTypeError` subclasses `Exception`, not Python's built-in `TypeError`.  That is deliberate.  If your checker has a bug, such as adding `None + 1`, Python raises its own `TypeError`.  You want that bug to crash loudly with a traceback, not to be caught by the driver and printed as if it were a type error in the program you are checking.

To see all of this before you rely on it, save the lines below as `explore_tenv.py`, a scratch file you do not submit, and run `python3 explore_tenv.py` from inside `cs374-typechecker`:

```python
# explore_tenv.py: a scratch file you do not submit.
outer = {"x": "Num"}        # one scope: a dict from each name to its type name
inner = {}                  # a nested block starts with an empty dict of its own
inner["x"] = "Str"          # an inner let x: Str shadows the outer x
print(outer["x"], inner["x"])
print("y" in outer, outer.get("y"))   # a name no scope has: None, meaning unknown
print(inner.get("z", outer.get("z", "not found")))

class PositionedError(Exception):
    def __init__(self, message, line, col):
        super().__init__(message)
        self.line, self.col = line, col

    def __str__(self):
        return f"Type error at line {self.line}, col {self.col}: {self.args[0]}"

try:
    raise PositionedError("'+' requires Num operands, got Num and Bool", 1, 16)
except PositionedError as err:
    print(err)
    print(err.line, err.col, err.args[0])
```

> **You should see.**
>
> ```text
> Num Str
> False None
> not found
> Type error at line 1, col 16: '+' requires Num operands, got Num and Bool
> 1 16 '+' requires Num operands, got Num and Bool
> ```
>
> `print(err)` calls `__str__`, which is how the driver at the bottom of `typechecker.py` prints the graded message.  `err.args[0]` is the message by itself, without the position.  **Predict** before you move on: if a third dict sat inside `inner`, how many dicts would a lookup of `x` have to check, and which one would answer?

**You write:** `typechecker.py` - the whole skeleton below, then `define` and `lookup` in `TypeEnvironment`.
**You run:** `python3 -c "from typechecker import TypeEnvironment as T; g = T(); g.define('x', 'Num'); print(T(parent=g).lookup('x'))"`

> **Do this.**
> 1. Create `typechecker.py` in `cs374-typechecker/` and paste the skeleton below into it.
> 2. Adjust the `import` lines at the top to your own AST, parser, and lexer file names if they differ from the reference layout.
> 3. Fill in `define` and `lookup` in `TypeEnvironment`.  Mirror your `Environment` class: `define` binds in this scope only, and `lookup` walks the parent chain.
> 4. Run the smoke test from the same folder:
>
> ```bash
> python3 -c "from typechecker import TypeEnvironment as T; g = T(); g.define('x', 'Num'); print(T(parent=g).lookup('x'))"
> ```

```python
# typechecker.py: a small static type checker over the class AST.
# The checker never evaluates anything; it only compares types.
import sys
from ast_nodes import (Num, Str, BoolLit, Var, BinOp, UnaryOp, LogicOp,
                       Let, Assign, Print, Block, If, While, Program)
from parser import parse, ParseError   # parse(source) -> Program
from lexer import LexError

NUM, STR, BOOL = "Num", "Str", "Bool"   # the three types this checker knows

class LangTypeError(Exception):
    """Raised on the first type error found.  str(err) is the graded message."""
    def __init__(self, message: str, line: int, col: int):
        super().__init__(message)
        self.line, self.col = line, col

    def __str__(self):
        return f"Type error at line {self.line}, col {self.col}: {self.args[0]}"

class TypeEnvironment:
    """Same parent chain as Environment, but each name maps to a type name."""
    def __init__(self, parent=None):
        self.bindings = {}
        self.parent = parent

    def define(self, name: str, typ: str) -> None:
        # TODO (Step 1.1): bind name to typ in THIS scope only, so an inner
        #       `let x: Str` shadows an outer `let x: Num`
        pass

    def lookup(self, name: str) -> str | None:
        # TODO (Step 1.1): this scope's binding, else ask the parent;
        #       return None when no scope in the chain has it (an unknown type)
        pass

def check(program: Program) -> None:
    """Well typed: return silently.  Ill typed: raise LangTypeError."""
    env = TypeEnvironment()
    for stmt in program.stmts:
        check_stmt(stmt, env)

def check_stmt(node, env: TypeEnvironment) -> None:
    """Check one statement.  Statements have no type, so this returns None."""
    if isinstance(node, Print):
        # TODO (Step 1.2): check the printed expression; any type may be printed
        pass
    elif isinstance(node, Let):
        # TODO (Step 1.3): actual = check_expr(node.value, env); on a mismatch with
        #       node.annotation raise LangTypeError naming BOTH types at
        #       node.line, node.col; otherwise env.define(...)
        pass
    elif isinstance(node, Block):
        # TODO (Step 1.3): check each statement in a child TypeEnvironment(parent=env)
        pass
    elif isinstance(node, Assign):
        # TODO (Step 1.3): the new value's type must equal the declared type
        pass
    elif isinstance(node, (If, While)):
        # TODO (Step 1.4): check the condition, then the branches or the body
        pass
    else:
        raise NotImplementedError(f"no typing rule yet for {type(node).__name__}")

def check_expr(node, env: TypeEnvironment) -> str:
    """Return the type of an expression (None if unknown), or raise LangTypeError."""
    if isinstance(node, Num):
        return NUM
    # TODO (Step 1.2): Str and BoolLit
    # TODO (Step 1.3): Var, via env.lookup; an undeclared name's type is None (unknown)
    # TODO (Step 1.4): BinOp, LogicOp, UnaryOp, one operator family at a time
    raise NotImplementedError(f"no typing rule yet for {type(node).__name__}")

if __name__ == "__main__":
    # File driver: python3 typechecker.py programs/some_program.ml
    source = open(sys.argv[1]).read()
    try:
        check(parse(source))
    except (LangTypeError, ParseError, LexError) as err:
        print(err)
        sys.exit(1)
```

The driver also catches `ParseError` and `LexError`, so a program that does not parse prints one positioned line instead of a traceback.  You will be glad of that in Step 1.3, while the parser is learning to read annotations.  Only `LangTypeError` lines go in your run log; the other two should never appear there.

| `# TODO` | How to write it |
|---|---|
| `define` | One line: store `typ` under the key `name` in `self.bindings`.  Do not look at `self.parent`; a declaration always lands in the current scope. |
| `lookup` | Three cases, in order.  If `name in self.bindings`, return that entry.  Otherwise, if `self.parent is not None`, return `self.parent.lookup(name)`, which lets the parent repeat the same three cases.  Otherwise `return None`: no scope declares the name, so its type is unknown.  A loop that walks `scope = scope.parent` works just as well as recursion. |

> **You should see.**  One line, `Num`: the child scope found a name bound in its parent.

> **If it fails.**
> - `ModuleNotFoundError: No module named 'ast_nodes'` (or `parser`, or `tokens`): the AST, parser, and lexer files are not in the same folder as `typechecker.py`, or their names differ from the `import` lines.
> - `ImportError: cannot import name 'Str'` (or `BoolLit`, `LogicOp`): the Parser assignment made these classes optional, and your AST represents those constructs another way (for example, `and`/`or` as a `BinOp`).  Delete the missing names from the `import` line, and handle those constructs in the branch for the node class your parser actually produces.
> - `ImportError: cannot import name 'ParseError'` (or `LexError`): your own parser or lexer names its error class differently.  Import the name it actually uses, and put that name in the driver's `except` tuple.
> - `None` prints instead of `Num`: `lookup` still ends in `pass`, it checks this scope but never asks `self.parent`, or it finds the parent's answer but forgets to `return` it.

Once `TypeEnvironment` can define a name in one scope and find it from a child scope, the rest of Part 1 is filling in the `TODO` branches one node type at a time.

### Step 1.2: Type the literals

A literal's type never depends on anything else: `42` is a `Num` wherever it appears.  These are the easiest rules, and they let you run the checker on a whole file for the first time.

**You write:** `typechecker.py` - the `Str` and `BoolLit` branches of `check_expr` and the `Print` branch of `check_stmt`; and a test file, `mytests/literals.ml`.
**You run:** `python3 typechecker.py mytests/literals.ml`, then the one-line check below.

> **Do this.**
> 1. In `check_expr`, add branches for `Str` and `BoolLit` next to the `Num` branch, returning `STR` and `BOOL`.
> 2. Fill the `Print` case in `check_stmt`: call `check_expr` on its expression and discard the result.  Printing any type is fine; the expression inside must be well typed.
> 3. Create `mytests/literals.ml` containing one print statement per literal type, and run `python3 typechecker.py mytests/literals.ml`.  It has the same three statements as the provided `01-literals.ml`, without the comment line:
>
>    ```text
>    print 42;
>    print "hello";
>    print true;
>    ```

| `# TODO` | How to write it |
|---|---|
| `Str` and `BoolLit` | Copy the shape of the `Num` branch twice: `if isinstance(node, Str):` then `return STR`, and the same for `BoolLit` and `BOOL`.  Put them above the final `raise`, or the `raise` runs first. |
| `Print` | Replace `pass` with `check_expr(node.value, env)`.  The reference `Print` node calls its expression `value`; if yours uses another field name, use that.  Ignore the returned type. |

> **You should see.**  Nothing at all: a well-typed program produces no output.  Silence is easy to fake, though, so ask `check_expr` directly for the three literal types:
>
> ```bash
> python3 -c "from parser import parse; from typechecker import check_expr, TypeEnvironment; print([check_expr(s.value, TypeEnvironment()) for s in parse(open('mytests/literals.ml').read()).stmts])"
> ```
>
> ```text
> ['Num', 'Str', 'Bool']
> ```

> **If it fails.**
> - `NotImplementedError: no typing rule yet for Str` (or `BoolLit`): the new branch sits below the final `raise` in `check_expr`, tests the wrong class name, or is missing its `return`.  Without `return`, Python runs on past the branch and reaches the `raise`.
> - `AttributeError: 'Print' object has no attribute 'value'`: your `Print` node stores its expression under another field name.  Open `ast_nodes.py` and use that name.

### Step 1.3: Check declarations and variable uses

Declarations put names into the environment, variable uses take them back out, and blocks decide which environment is current.  These three together are what the rubric means by "scopes annotations through nested blocks."

> **Watch out.**  The reference AST's `Let` node has the fields `name`, `value`, `line`, and `col`, and the reference `parse_let_stmt` reads `let x = expr;` with no annotation.  The Interpreter assignment's Part 4 says `let` statements carry, or are extended to carry, type annotations.  If you are building on the reference parser (or your own parser has no annotation yet), add an `annotation` field to `Let` and teach the `let` rule to read the `: Num` between the name and the `=`.  Budget ten minutes for this before you fill the `Let` branch.

#### First, carry the annotation from the source to the `Let` node

Right now `let x: Num = 42;` does not even get past the lexer, because the reference lexer has no token for `:`.  The annotation has to survive three stages to reach the checker: the lexer must produce a `COLON` token, the parser must read `COLON` and a type name inside `parse_let_stmt`, and the `Let` node must have a field to hold the name.  If your own lexer and parser already do all three, skip to the checker work below, and read `node.annotation` as whatever your field is called.

**You write:** `lexer.py` - one new `COLON` entry in `TOKEN_SPEC`; `ast_nodes.py` - one new field on `Let`; `parser.py` - the annotation in `parse_let_stmt`.
**You run:** `python3 -c "from parser import parse; print(parse('let x: Num = 42;'))"`

> **Do this.**
> 1. In `lexer.py`, add `("COLON", r":"),` to `TOKEN_SPEC`, on the line after `SEMICOLON`.  No other token starts with `:`, so its position in the list does not matter.  The driver uses the default `TOKEN_SPEC`; if you also load `token_spec.json` somewhere, add `["COLON", ":"]` there too.
> 2. In `ast_nodes.py`, add this as the *last* field of `Let`, after `col`.  `Optional` is already imported at the top of the reference file.  Putting it last keeps every existing `Let(name, value, line, col)` call working.
>
>    ```python
>        annotation: Optional[str] = None  # declared type name ("Num", "Str", "Bool"), or None
>    ```
>
> 3. In `parser.py`, change `parse_let_stmt` to match the skeleton below, and fill its one `TODO`.

```python
    def parse_let_stmt(self):
        let_tok = self.expect("LET")
        name = self.expect("IDENT")
        annotation = None
        # TODO: if the next token is a COLON, consume it, then expect an IDENT
        #       (the type name) and keep that token's text in annotation
        self.expect("EQ")
        value = self.parse_expr()
        self.expect("SEMICOLON")
        return Let(name.value, value, let_tok.line, let_tok.col,
                   annotation=annotation)
```

| `# TODO` | How to write it |
|---|---|
| read `: Type` | Test `if self.peek().type == "COLON":`.  Inside, call `self.advance()` to consume the colon, then `annotation = self.expect("IDENT").value`.  The type name is an ordinary `IDENT` token, the same kind `name` is.  `peek` never consumes, so an unannotated `let x = 1;` still parses as before. |

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

#### Then, check declarations, variable uses, blocks, and assignments

**You write:** `typechecker.py` - the `Let`, `Block`, and `Assign` branches of `check_stmt` and the `Var` branch of `check_expr`; and three test files in `mytests/`.
**You run:** `python3 typechecker.py mytests/declare.ml`, then the same command on `mytests/undeclared.ml` and `mytests/mismatch.ml`.

> **Do this.**
> 1. Fill the `Let` branch of `check_stmt`: type the initializer, compare it with the annotation, raise `LangTypeError` naming both types on a mismatch, and otherwise `define` the name with its annotated type.
> 2. Fill the `Var` branch of `check_expr`: return `env.lookup(node.name)`.  An undeclared name comes back as `None`, an unknown type.  The checker does not report it; the evaluator does, with `LangNameError`, when the program runs.
> 3. Fill the `Block` branch of `check_stmt`: create `TypeEnvironment(parent=env)` and check each statement with it.  Do not bind anything from the block into the outer environment.
> 4. Add `Assign` to `check_stmt`: the new value's type must equal the variable's declared type, looked up through the chain.
> 5. Test with a well-typed declaration and an undeclared-variable program of your own.  The provided shadowing program and `let x: Num = 1 + true;` come after Step 1.4.

The `Var` branch is one line.  It goes in `check_expr`, above the final `raise`:

```python
    if isinstance(node, Var):
        return env.lookup(node.name)    # None for a name no scope declares
```

An unknown type travels upward like any other.  Every rule that compares two types must let `None` through without reporting it, and the hint tables in this step and the next show the one-line test that does it.  This is a decision about *which stage* reports an undefined name: the checker reports only what it can prove about types, and the evaluator reports names it cannot find.

The `Let` and `Assign` branches replace their `pass` lines in `check_stmt`:

```python
    elif isinstance(node, Let):
        actual = check_expr(node.value, env)
        declared = node.annotation
        # TODO: if declared is None, decide what an unannotated let means
        # TODO: if actual != declared, raise LangTypeError naming BOTH types
        #       at node.line, node.col
        # TODO: env.define(...) the name with its declared type
    elif isinstance(node, Block):
        # TODO: inner = TypeEnvironment(parent=env); check each statement in inner
        pass
    elif isinstance(node, Assign):
        # TODO: look up the declared type (None for an undeclared name: skip the check)
        # TODO: type the new value; a mismatch names BOTH types
        pass
```

| `# TODO` | How to write it |
|---|---|
| unknown types | Before you compare two types, let `None` through.  In `Let`, raise only `if actual is not None and actual != declared:`.  In `Assign`, raise only when both `declared` and `actual` are not `None` and they differ.  `None` means a name nobody declared, and the evaluator reports that name when the program runs. |
| `Let`, unannotated | Every provided program annotates its `let`s, so `None` never reaches you here.  If your parser allows `let x = 1;`, the simplest choice is to use the initializer's type: `declared = actual`. |
| `Let`, mismatch | `if actual is not None and actual != declared:` then raise with a message that contains both strings, for example `f"'{node.name}' declared {declared}, but its initializer has type {actual}"`.  The position is the `Let` node's own `node.line, node.col`. |
| `Let`, define | `env.define(node.name, declared)`.  Use the *declared* type, not `actual`; after the mismatch check they are equal, but the rule says the annotation is what binds. |
| `Block` | `inner = TypeEnvironment(parent=env)`, then `for stmt in node.stmts:` and `check_stmt(stmt, inner)`.  Nothing is copied back; when the loop ends, `inner` is simply forgotten.  That one line is the whole scoping rule. |
| `Assign`, lookup | `declared = env.lookup(node.name)`.  If it is `None`, the variable was never declared, so skip the type check; the evaluator reports the name. |
| `Assign`, mismatch | `actual = check_expr(node.value, env)`; if neither is `None` and they differ, raise naming both, for example `f"'{node.name}' declared {declared}, but assigned a value of type {actual}"`. |

Save the three test programs below in `mytests/`.  `declare.ml` is well typed and uses a nested block; `undeclared.ml` uses a `y` that no `let` declares, which the checker leaves to the evaluator; `mismatch.ml` gives a `Num` declaration a `Str`.

`mytests/declare.ml`:

```text
let x: Num = 5;
x = 7;
print x;
{
    let y: Str = "inner";
    print y;
}
```

`mytests/undeclared.ml`:

```text
let x: Num = 5;
print y;
```

`mytests/mismatch.ml`:

```text
let x: Num = "five";
```

> **You should see.**  Silence for `declare.ml` and for `undeclared.ml`, and one line for `mismatch.ml`.  The checker cannot type `y`, so it says nothing about it; when the program runs, the evaluator reports `Undefined variable 'y'`, which is the Interpreter assignment's Run stage.  With the reference parser and the example message from the hint table, the three runs print exactly this:
>
> ```text
> Type error at line 1, col 1: 'x' declared Num, but its initializer has type Str
> ```

> **If it fails.**
> - `undeclared.ml` prints a `Type error` naming `y`: the `Var` branch still reports a missing name.  Return `lookup`'s `None` instead; the evaluator reports undefined names.
> - `declare.ml` and `mismatch.ml` pass, but a later program such as `08` or `12` misses its error: the `Let` branch never calls `env.define`, so every later lookup returns `None` and every check is skipped.
> - `mismatch.ml` prints nothing: the comparison uses the wrong pair (for example `declared != declared`), or `node.annotation` is `None` because the parser did not store it.  Re-run the parse check above.
> - `NotImplementedError: no typing rule yet for BinOp`: one of your test lines uses an operator.  That is Step 1.4's job; keep this step's tests operator free.

### Step 1.4: Check the operators, one family at a time

Operators are where most ill-typed programs fail, and where a message that names only one type is easiest to write by accident.  Every operator error names both operand types.

**You write:** `typechecker.py` - the `BinOp`, `LogicOp`, and `UnaryOp` branches of `check_expr`, the `If`/`While` branch of `check_stmt`; and a test file, `mytests/add_bool.ml`, containing the one line `let x: Num = 1 + true;`.
**You run:** `python3 typechecker.py mytests/add_bool.ml`, then the provided programs listed in the table after the hints.

> **Do this.**
> 1. Arithmetic first.  In `check_expr`, handle `BinOp` with `op` in `+ - * /`: both operands must be `NUM`, and the result is `NUM`.
> 2. Comparison next: `< <= > >=` require `NUM` operands and yield `BOOL`.
> 3. Equality: `== !=` require both sides to have the same type and yield `BOOL`.
> 4. Boolean operators last: `LogicOp` (`and`, `or`) requires `BOOL` on both sides and yields `BOOL`; `UnaryOp` with `not` requires `BOOL` and yields `BOOL`; `UnaryOp` with `-` requires `NUM` and yields `NUM`.
> 5. Add `If` and `While` to `check_stmt`: check the condition, then check each branch or body as a `Block`.  Whether the condition must be `BOOL` is a design decision you make here; the first reflection prompt asks you to defend it.
> 6. After each family, run the driver on the provided programs that exercise it.

All three expression branches go in `check_expr`, above the final `raise`.  Each one types its operands first and then decides:

```python
    if isinstance(node, BinOp):
        left = check_expr(node.left, env)
        right = check_expr(node.right, env)
        if node.op in ("+", "-", "*", "/"):
            # TODO (Step 1.4, item 1): both NUM, else raise naming left and right; return NUM
            pass
        if node.op in ("<", "<=", ">", ">="):
            # TODO (Step 1.4, item 2): both NUM, else raise naming left and right; return BOOL
            pass
        if node.op in ("==", "!="):
            # TODO (Step 1.4, item 3): left == right, else raise naming both; return BOOL
            pass
    if isinstance(node, LogicOp):
        # TODO (Step 1.4, item 4): type both sides; both BOOL, else raise naming both; return BOOL
        pass
    if isinstance(node, UnaryOp):
        # TODO (Step 1.4, item 4): type node.operand; "not" needs BOOL, "-" needs NUM
        pass
```

The `If`/`While` branch replaces its `pass` in `check_stmt`:

```python
    elif isinstance(node, (If, While)):
        # TODO (Step 1.4, item 5): type node.condition and apply your condition rule
        # TODO (Step 1.4, item 5): If: check node.then_branch, and node.else_branch if it
        #       is not None.  While: check node.body
        pass
```

| `# TODO` | How to write it |
|---|---|
| unknown operand | First, `if left is None or right is None:` return the result type without checking: `NUM` for arithmetic, `BOOL` for comparison and equality.  An unknown operand comes from an undeclared name, which the evaluator reports. |
| arithmetic | `if left != NUM or right != NUM:` then `raise LangTypeError(f"'{node.op}' requires Num operands, got {left} and {right}", node.line, node.col)`.  After the `if`, `return NUM`.  The message prints `left` and `right`, the two types you actually found, so it names both even when only one is wrong. |
| comparison | The same test and message as arithmetic, but `return BOOL`. |
| equality | `if left != right:` then raise naming both, for example `f"'{node.op}' requires operands of the same type, got {left} and {right}"`.  Then `return BOOL`.  Two `Str`s pass here, though they fail at `<`. |
| `LogicOp` | Type `node.left` and `node.right` the same way as `BinOp`, then `if left is not None and right is not None and (left != BOOL or right != BOOL):` raise naming both, and `return BOOL`. |
| `UnaryOp` | `operand = check_expr(node.operand, env)`, then `wanted = BOOL if node.op == "not" else NUM`.  If `operand is not None and operand != wanted`, raise naming the operator, `wanted`, and `operand`.  Return `wanted`.  A unary operator has only one operand, so "both types" here means the expected one and the actual one. |
| condition | `cond = check_expr(node.condition, env)`.  If you require `Bool`, raise when `cond is not None and cond != BOOL`.  The reference `If` and `While` nodes store only a `line`, so raise at `node.condition.line, node.condition.col`, which every expression node has. |
| branches and body | `check_stmt(node.then_branch, env)`, and the same for `node.else_branch` when it is not `None`; for `While`, `check_stmt(node.body, env)`.  Each one is a `Block`, so your `Block` branch makes the child scope for you.  An `else if` chain arrives as an `If` in `else_branch`, which `check_stmt` already handles. |

Run the provided programs as each family lands.  Each row lists what works once you have finished that item of the **Do this** list and every item above it:

| After you finish | Run | Expected |
|---|---|---|
| item 1, arithmetic | `mytests/add_bool.ml`, `programs/07-bad-add-num-bool.ml` | one `'+' requires Num operands` line each |
| items 2 and 3, comparison and equality | `programs/03-comparison.ml`, `09-bad-compare-strings.ml`, `10-bad-equality-mixed-types.ml` | silence for 03; one error line each for 09 and 10 |
| item 4, boolean and unary | `programs/02-arithmetic.ml`, `04-logic.ml` | silence for both; 02 needs unary `-`, so it waits until here |
| item 5, conditions | `programs/05-control.ml` | silence |

> **You should see.**  For `let x: Num = 1 + true;` on line 1, one line of the form `Type error at line 1, col 16: '+' requires Num operands, got Num and Bool`, and nothing else.  The column is wherever your parser recorded the `BinOp` node, and the wording after the colon is yours, provided both types appear in it.
>
> ```text
> Type error at line 1, col 16: '+' requires Num operands, got Num and Bool
> ```
>
> The provided `07-bad-add-num-bool.ml` has the same line after two comment lines, so it reports `line 3, col 16`.

> **If it fails.**
> - The message names one type: you formatted the expected type but not the actual one, or the other way around.  Both must appear.
> - `NotImplementedError` on a program it should reject: an operator family is still missing.  Read the node name in the message.
> - A program with an error on line 5 also prints output from line 1: something is evaluating.  The checker calls no evaluator and prints nothing except the error.
> - `NotImplementedError: no typing rule yet for BinOp` (or `LogicOp`, `UnaryOp`) although you wrote that branch: its success path has no `return`, so Python runs on past it to the final `raise`.  Each operator branch returns a type when its check passes.
> - A program with a non-`Bool` condition crashes with `AttributeError: 'While' object has no attribute 'col'` (or `'If'`): you raised at `node.col` on an `If` or `While`.  Use the condition's position.

### Step 1.5: Run the twelve provided programs and keep the log

Verify your checker against the [twelve provided programs]({{ site.baseurl }}/files/starters/typechecker/programs/), which live in `files/starters/typechecker/programs/` in the course site repository.  Seven programs must pass silently.  One of them, `11-undeclared-variable.ml`, uses a name nothing declares; the checker leaves it to the evaluator.  Five ill-typed programs must each produce a positioned error; these include the classic `let x: Num = 1 + true;` (the error must appear *before* anything runs) and a shadowing case where an inner `let x: Str` legitimately changes the type of `x` for the inner scope only.

**You write:** `runlog.txt`, produced by the command below.  No code changes, unless a program shows you a bug.
**You run:** `for f in programs/*.ml; do echo "== $f"; python3 typechecker.py "$f"; done | tee runlog.txt`

> **Do this.**
> 1. If you have not already, copy all twelve provided programs into `programs/`.  They are named `01-` through `12-`, and the five whose names contain `bad-` are the ill-typed ones.  Keep your own test files in `mytests/`, so this loop sees only the twelve.
> 2. Run the driver over every one of them and save the output.  The `for` loop runs the checker once per file, `echo` labels each run with its file name, and `tee` prints the output and writes it to `runlog.txt` at the same time.  If the provided programs use a different file extension, change `*.ml` to match.
>
>    ```bash
>    for f in programs/*.ml; do echo "== $f"; python3 typechecker.py "$f"; done | tee runlog.txt
>    ```
>
> 3. Read `runlog.txt` once, top to bottom, and confirm each well-typed program shows only its label and each ill-typed program shows its label and one `Type error` line.  Each of the five ill-typed programs breaks a *different* rule, so five identical messages means a branch is catching something it should not.

> **You should see.**  Twelve labels.  Seven are followed directly by the next label (silent acceptance).  Five are followed by exactly one `Type error at line L, col C: ...` line, and each of those names two types.  With the reference parser and the example messages from the hint tables, the whole log is exactly this.  Your positions must match; your wording after each colon may differ.
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
> - `06-shadowing.ml` reports `'+' requires Num operands, got Str and Num` on line 9: the inner `let x: Str` leaked into the outer scope.  The `Block` branch is defining into `env` instead of its own child environment.
> - `12-bad-shadow-escapes.ml` is silent: the same leak in reverse.  After the block, `x` must look up as `Num` again, so the `Assign` of a `Str` must fail.
> - A line starting `ParseError` or `LexError` appears: a program did not parse, usually because the annotation work at the start of Step 1.3 is incomplete.  Re-run the parse check from that step.
> - More or fewer than twelve labels: the loop picked up extra files in `programs/`, or some of the twelve are missing.  Move your own tests to `mytests/`.

---

## Part 2: Write the Typing Rules on Paper

In `RULES.md`, state the typing rule for each construct your checker covers, one rule per construct.  A typing rule has premises (what must already be true about the parts) and a conclusion (what then holds for the whole).  Writing the rules after the code is deliberate: the code tells you what you actually enforced, and the rule tells you whether that was what you meant.  This document becomes the seed of the Interpreter assignment's semantics writeup, and if you later choose the full Hindley-Milner direction (type inference, which works out types with no annotations at all), these rules are exactly what inference generalizes.

### Step 2.1: State one rule per construct and cite its code

**You write (in `RULES.md`, below your Part 0 answers):** one typing rule per construct your checker covers, each followed by the name of the branch in `typechecker.py` that implements it.  No new code.

> **Do this.**
> 1. Create `RULES.md` in your lab folder, with your name (and your partner's, if you worked in a pair) at the top (below your Part 0 answers, if you typed them there).
> 2. For each construct the checker covers (each literal type, variable use, `let` declaration, and each operator family), write one rule in either inference-rule layout (premises above a line, conclusion below it) or a disciplined "if... then..." sentence.
> 3. Under each rule, name the function or branch in `typechecker.py` that implements it (for example, "the `BinOp` branch of `check_expr` for `+ - * /`").
> 4. Check each rule against its cited code.  If the code enforces a premise the rule does not state, or the rule states one the code does not check, fix whichever is wrong.  Confirm the cited code raises an error naming both types whenever a premise fails.

The two layouts say the same thing.  In inference-rule layout, the rule for `+` is:

```text
e1 : Num    e2 : Num
--------------------
   e1 + e2 : Num
```

As a sentence: *if `e1 : Num` and `e2 : Num`, then `e1 + e2 : Num`*.  Either form is acceptable; what is graded is that every premise is stated and none is missing.

### Step 2.2: Answer the two theory questions

Close `RULES.md` with two theory questions from the Type Systems session:

**You write (at the end of `RULES.md`):** one short answer to each question below.  No code.

1.  Place four languages (Python, C, Haskell, and JavaScript) on the static/dynamic × strong/weak quadrant, with one sentence of justification each.
2.  Your checker makes the class language *gradually* typed in spirit: annotated declarations are checked, and unannotated territory is documented as unchecked.  State one benefit and one risk of that middle ground, using the mypy/TypeScript comparison from class.

---

## Deliverables

Submit a ZIP containing the files below, with your name (and your partner's, if you worked in a pair) in `RULES.md`.

| File or artifact | What it shows | Rubric row |
|------------------|---------------|------------|
| Part 0 write-up (at the top of `RULES.md`, or a photo of your page) | The annotated program, the rejected expression with your defended preference, and the guarantee and forbidden program | Part 0: Before You Start - Type Systems |
| `typechecker.py` | The type environment, `check()`, and the literal, variable, declaration, and operator rules | The Checker Core |
| `runlog.txt` | The checker's output over the twelve provided programs: seven silent, five positioned errors | The Checker Core |
| `RULES.md` | One rule per construct with its implementing function cited, and the two theory questions | Typing Rules on Paper |

## Self-Check Before You Submit

- [ ] Every one of the seven programs the checker accepts (the six well-typed ones and `11-undeclared-variable.ml`) produces no output.
- [ ] Every one of the five ill-typed programs produces exactly one `Type error at line L, col C: ...` line, and that line names both conflicting types.
- [ ] `let x: Num = 1 + true;` is rejected before anything runs, and the shadowing program's inner `let x: Str` is accepted for the inner scope only.
- [ ] The checker calls no evaluator and prints nothing except the error.
- [ ] `RULES.md` has one rule per construct the checker covers, each with its premises stated and its implementing function cited.
- [ ] `RULES.md` answers the quadrant question and the gradual-typing question.
- [ ] Your name, and your partner's if you worked in a pair, is in `RULES.md`, and any reference component you built on is declared in one line.

## Reflection Prompts

- Your checker rejects `while 1 { ... }` if you require a `Bool` condition, though the evaluator's truthiness rule would happily run it.  Which behavior do you consider correct for the class language, and why?
- If you worked in a pair, who did what, and name one thing your partner caught that you would have missed.  If you worked alone, note that instead.
