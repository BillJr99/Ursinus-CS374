---
layout: assignment
permalink: /Assignments/TypeCheckerLab
title: "CS374: Principles of Programming Languages - Lab: Type Checker Starter"

info:
  coursenum: CS374
  purpose: "To build the core of the Interpreter assignment's required static type checker with a partner, covering literal, variable, and operator checks over the class AST, all running before any code is evaluated."
  tilt:
    task: "With a partner, implement a checker that walks the class AST with a type environment, verifying annotated declarations, variable uses, and operator applications, and reporting positioned type errors."
    criteria: "I grade this on a checker that accepts the well-typed programs and rejects each ill-typed program with a positioned two-type error message, plus a set of typing-rule statements written on paper, weighted 70/30 across the two parts.  See the rubric below for the full breakdown."
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

This **lab** builds the core of the Interpreter assignment's Part 4: a small static type checker that runs between parsing and evaluation.  A static type checker reads the abstract syntax tree (AST) of a program and decides whether each operation makes sense before any of the program runs.  With a partner, you get the checker working on its three simplest cases: literals, variables, and operators.  You leave with a `typechecker.py` that accepts six well-typed programs and rejects six ill-typed ones, a run log that shows it doing so, and a `RULES.md` that states each typing rule you implemented.  The Interpreter assignment then has you extend the checker on your own to call sites and return types.  Plan on one working session.

**Pair policy.**  You may do this lab in pairs.  Submit the same files, name both partners in them, and you will both earn the same grade.  Working alone is also allowed.  The Interpreter assignment remains individual work: both partners may carry this shared checker core into it, but the extension to calls and returns must be your own.

---

## Before You Start

- An AST to walk: the node classes from your Parser assignment, or the [reference parser and AST]({{ site.baseurl }}/files/reference/reference-parser.zip) released with the Interpreter assignment hand-out.  If your submission builds on a reference component, say so in one line in your submission; that is the entire requirement, and it costs no points.
- The `Environment` class from your Environments lab.  The type environment you build in Part 1 has the same shape and borrows its method names.
- Python 3.10 or newer; `python3 --version` should print `Python 3.10` or later.  Nothing needs to be installed; the checker is standard-library Python.
- A terminal and an editor.  If the terminal is still new to you, the [Course Development Environment]({{ site.baseurl }}/Tutorials/DevEnvironment) and [Shell Skills for Language Development]({{ site.baseurl }}/Tutorials/ShellForLanguageDev) tutorials cover everything this lab asks you to type.

Make one folder for the lab and copy your AST and parser files into it, so `typechecker.py` can import them with a plain `import`.  The steps below assume this layout:

```text
cs374-typechecker/
  ast_nodes.py       # your AST node classes (or the reference copy)
  parser.py          # your parser (or the reference copy), plus its lexer
  lexer.py
  typechecker.py     # Part 1: type environment, check(), and a file driver
  programs/          # the twelve provided programs, copied from the course starter repo
  runlog.txt         # Part 1: the checker's output over all twelve programs
  RULES.md           # Part 0 write-up and Part 2 typing rules
  model1_strong.py   # Part 0 worked models (yours to keep; not submitted)
```

### Your First 15 Minutes

1. Copy the Model 1 script from Part 0 into `model1_strong.py` and run `python3 model1_strong.py`.  Three operations pass and three are refused with a message naming both types.
2. That refusal is the whole lab in miniature.  Your checker in Part 1 produces the same kind of message, with two differences: it names a line and column, and it fires before the program runs rather than while it runs.
3. Create `typechecker.py` from the skeleton in Step 1.1 and run its smoke test.
4. Once `TypeEnvironment` can define a name in one scope and find it from a child scope, the rest of Part 1 is filling in the `TODO` branches one node type at a time.

This lab lands inside the Interpreter assignment's window; see the course schedule for the assigned and due dates.

> **Time budget.**  About three hours in one working session: fifteen minutes on the paper exercise, forty-five minutes reading and running the four worked models, an hour and a half on the checker, and thirty minutes writing the rules.

---

## Part 0: Worked Models (read before you code)

Part 0 opens with a short paper exercise, which is the graded piece (10%).  The rest is four worked models from the Type Systems class session: a runtime checker for the interpreter you are building, a trace of it on compound expressions, inference by hand, and a type-error postmortem.  Each model has a script you can run and questions to talk through with your partner.  Read all four before you start Part 1.

### Type Systems on Paper (10%)

Plan on about fifteen minutes with pencil and paper.  Everyone has an opinion about static typing; an example is what makes the argument worth having.

> **Do this.**
> 1. Write a small program and annotate each subexpression with the type you expect it to have.
> 2. Find one expression in it that a static type checker would reject but a dynamic language would run.  Say which behavior you prefer there, and why.
> 3. State one guarantee a type system gives you, and one program it forbids that you wish it allowed.
> 4. Write your answers at the top of `RULES.md`, or put a photo of your page in the ZIP.

> **Bring to class.**  The program you wish the checker had allowed, even if you could not settle the question.  The unsettled cases are the ones we argue about, and Part 1 makes you take a side in code.

### Model 1: A Dynamically, Strongly Typed Core

Your interpreter already evaluates binary expressions like `3.0 + 4.0`.  This model adds a gatekeeper at the top of that evaluation: before it touches the operands, it checks whether the combination makes sense and raises an error naming both types if it does not.  The language checks types at runtime and refuses silent coercion, the same choice Python makes.  Coercion is a conversion the language performs on its own, such as turning the number `5` into the string `"5"` so that it can be concatenated.  Refusing to coerce is what makes the typing *strong*; checking while the program runs, rather than before it starts, is what makes it *dynamic*.

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

An interpreter with dynamic (runtime) checking evaluates `(3.0 + 4.0) < ("a" + 1.0)`.  When is the type error for `"a" + 1.0` detected: before execution begins, when the `<` comparison runs, at the moment the `+` on `"a"` and `1.0` is evaluated (after `3.0 + 4.0` has already computed), or never, because dynamic languages coerce automatically?

> **Answer.**  At the moment the `+` on `"a"` and `1.0` is evaluated, after `3.0 + 4.0` has already computed.

#### Critical Thinking Questions

4.  The trace shows the checks firing in steps 1, 2, 3, the same order as evaluation.  State the general rule: in a dynamically typed interpreter, when does the check for an operator fire, relative to the evaluation of that operator's operands?
5.  In the failing trace, step 1 finished before the TypeError at step 2.  Suppose step 1 had been `print("charging card...")` instead of an addition.  What does this tell you about *where in a program's lifetime* you would prefer type errors to fire, and which typing discipline delivers that?
6.  Redo the failing trace as a *static* checker would perform it, before execution: rewrite the table with types only, no values.  Which columns disappear, and which check still fails?

### Model 3: Type Inference by Hand

Type inference is the trick where the checker works out every variable's type from context alone: you write `let a = 2` and it deduces `a: int` without you saying so.  Mechanically, it is a tree walk.  Visit each node, compute the type it must produce, and pass that type upward.  When two branches disagree (for example, adding an `int` to a `str`), the checker reports an error *at that node*, which can be far from the actual mistake.

The script below implements Hindley-Milner style inference in miniature.  Each `if kind == ...` branch of `infer` is one typing rule, and the `let` branch is where the type environment grows.  This is the closest model to what you build in Part 1: your checker walks the same way and keeps the same kind of environment, but reads the type from the annotation on each `let` instead of deducing it from the initializer.

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

Follow the environment through the good program.  It starts empty; `let a = 2` binds `a: TInt`; `let b = a + 3` looks up `a`, types the literal, applies `TInt + TInt -> TInt`, and binds `b: TInt`; `let c = b < 10` binds `c: TBool`; the body `("var", "c")` looks up `TBool`.  In the error program, the environment holds `{a: TInt}` when `add` finds `TInt + TStr` and raises.  The error is reported at the `add` node, but the root cause is the choice made at the first `let`.  That distance between the error location and the root cause is a recurring problem in type inference, and the reason good inference error messages are hard to write.

#### Critical Thinking Questions

7.  The inference trace shows `let a: int`, `let b: int`, `let c: bool`.  These are determined entirely from the *values* (literals), with no type annotations written.  Is this static or dynamic typing?  Explain.
8.  When inference encounters `a + "hello"`, it reports the error at the `add` expression.  But the *root cause* is that `a` was given an int value.  How far is the reported error from the root cause, and what does this say about inference error message quality?
9.  What would need to change to support `let a = 2; let b = a + 3.0;`?  (Hint: numeric type widening, `int + float -> float`.)  Modify the `infer` function to allow this.

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

In a weakly typed language, `"19.99" + 5.0` yields `"19.995"` and `"19.995" * 1.06` yields `21.1947`.  Is the deepest design problem this postmortem illustrates floating-point rounding error, the slowness of string operations, silent coercion letting a type mistake flow through the program as plausible-looking wrong values instead of stopping with an error, or the inability of strings to represent decimal numbers?

> **Answer.**  Silent coercion lets a type mistake flow through the program as plausible-looking wrong values instead of stopping with an error.

#### Critical Thinking Questions

10.  Walk the postmortem table: at which step did the *type* first go wrong, and at which step did the *money* first go wrong?  Why is it significant that these are different steps?
11.  Step 2 coerced number -> string, but step 3 coerced string -> number.  Write the coercion rule a language designer would have to publish to justify both choices at once.  Does the result sound principled or accidental?
12.  The weak-mode run produces no error at any point; the bug would surface only as customer complaints.  Name two other places in the software pipeline (besides the language's type system) where this bug could have been caught, and what each catch would cost compared to a step-2 TypeError.
13.  For your project language: which, if any, of these coercions will you allow?  Record the decision in `SEMANTICS.md`, citing this postmortem as evidence for or against.

---

## Part 1: Build the Checker Core (63%)

Implement `check(program) -> None` in `typechecker.py`.  The function walks the class AST (your Parser assignment's AST nodes, or the reference AST) and reports a type error as soon as it finds one.  A well-typed program produces no output.  The checker carries a type environment as it walks: the same parent-chaining discipline as the `Environment` class from your Environments lab, but each name is bound to a *type* instead of a value.  Entering a block creates a child environment, and leaving the block discards it.

Your checker enforces these rules:

- **Literals:** numbers are `Num`, strings are `Str`, booleans are `Bool`.
- **Declarations:** `let x: Num = expr;` checks that `expr`'s type equals the annotation, then binds `x : Num` in the current scope.  A mismatch is an error naming both types.
- **Variables:** a use of `x` looks up its declared type; an undeclared use is a positioned error.
- **Operators:** `+ - * /` require `Num` operands and yield `Num`; `< <= > >=` require `Num` and yield `Bool`; `== !=` require both sides to have the same type and yield `Bool`; `and`/`or`/`not` require `Bool`.  Every violation is reported as `Type error at line L, col C: ...` naming **both** conflicting types.

The five steps below build the checker in the order that keeps it testable at every stage.  Run the provided programs after each step and keep the output as your run log.

### Step 1.1: Write the type environment

The environment comes first because every later rule either binds into it or looks up from it.  The skeleton below is the whole file; each later step fills one group of `TODO` markers.

> **Do this.**
> 1. Create `typechecker.py` in `cs374-typechecker/` and paste the skeleton below into it.
> 2. Adjust the two `import` lines at the top to your own AST and parser file names if they differ from the reference layout.
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
from parser import parse            # parse(source) -> Program

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

    def lookup(self, name: str) -> str:
        # TODO (Step 1.1): this scope's binding, else ask the parent;
        #       raise KeyError(name) when no scope in the chain has it
        pass

def check(program: Program) -> None:
    """Well typed: return silently.  Ill typed: raise LangTypeError."""
    env = TypeEnvironment()
    for stmt in program.stmts:
        check_stmt(stmt, env)

def check_stmt(node, env: TypeEnvironment) -> None:
    if isinstance(node, Let):
        # TODO (Step 1.3): actual = check_expr(node.value, env); on a mismatch with
        #       node.annotation raise LangTypeError naming BOTH types at
        #       node.line, node.col; otherwise env.define(...)
        pass
    elif isinstance(node, Block):
        # TODO (Step 1.3): check each statement in a child TypeEnvironment(parent=env)
        pass
    else:
        # TODO (Steps 1.3 and 1.4): Assign, Print, If, While: check the
        #       expressions they contain; If and While bodies are Blocks
        pass

def check_expr(node, env: TypeEnvironment) -> str:
    """Return the type of an expression, or raise LangTypeError."""
    if isinstance(node, Num):
        return NUM
    # TODO (Step 1.2): Str and BoolLit
    # TODO (Step 1.3): Var, via env.lookup; an undeclared name is a positioned error
    # TODO (Step 1.4): BinOp, LogicOp, UnaryOp, one operator family at a time
    raise NotImplementedError(f"no typing rule yet for {type(node).__name__}")

if __name__ == "__main__":
    # File driver: python3 typechecker.py programs/some_program.ml
    source = open(sys.argv[1]).read()
    try:
        check(parse(source))
    except LangTypeError as err:
        print(err)
        sys.exit(1)
```

> **You should see.**  One line, `Num`: the child scope found a name bound in its parent.

> **If it fails.**
> - `ModuleNotFoundError: No module named 'ast_nodes'` (or `parser`): the AST and parser files are not in the same folder as `typechecker.py`, or their names differ from the `import` lines.
> - `None` prints instead of `Num`: `lookup` still ends in `pass`.
> - `KeyError: 'x'`: `lookup` checks this scope but never asks `self.parent`.

### Step 1.2: Type the literals

> **Do this.**
> 1. In `check_expr`, add branches for `Str` and `BoolLit` next to the `Num` branch, returning `STR` and `BOOL`.
> 2. Add the `Print` case to `check_stmt`: call `check_expr` on its expression and discard the result.  Printing any type is fine; the expression inside must be well typed.
> 3. Create `programs/literals.ml` containing one print statement per literal type, and run `python3 typechecker.py programs/literals.ml`.

> **You should see.**  Nothing at all: a well-typed program produces no output.  If you want proof the checker ran, add a temporary `print` at the top of `check` and remove it afterward.

### Step 1.3: Check declarations and variable uses

Declarations put names into the environment, variable uses take them back out, and blocks decide which environment is current.  These three together are what the rubric means by "scopes annotations through nested blocks."

> **Watch out.**  The reference AST's `Let` node has the fields `name`, `value`, `line`, and `col`, and the reference `parse_let_stmt` reads `let x = expr;` with no annotation.  The Interpreter assignment's Part 4 says `let` statements carry, or are extended to carry, type annotations.  If you are building on the reference parser (or your own parser has no annotation yet), add an `annotation: str` field to `Let` and teach the `let` rule to read the `: Num` between the name and the `=`.  Budget ten minutes for this before you fill the `Let` branch.

> **Do this.**
> 1. Fill the `Let` branch of `check_stmt`: type the initializer, compare it with the annotation, raise `LangTypeError` naming both types on a mismatch, and otherwise `define` the name with its annotated type.
> 2. Fill the `Var` branch of `check_expr`: return `env.lookup(node.name)`.  Catch the `KeyError` and re-raise it as a `LangTypeError` at the variable's line and column, so an undeclared use is a positioned error.
> 3. Fill the `Block` branch of `check_stmt`: create `TypeEnvironment(parent=env)` and check each statement with it.  Do not bind anything from the block into the outer environment.
> 4. Add `Assign` to `check_stmt`: the new value's type must equal the variable's declared type, looked up through the chain.
> 5. Test with a well-typed declaration and an undeclared-variable program of your own.  The provided shadowing program and `let x: Num = 1 + true;` come after Step 1.4.

> **You should see.**  Silence for the well-typed declaration.  For a use of an undeclared `y` on line 2, one line such as `Type error at line 2, col 7: undeclared variable 'y'`, with the column wherever your parser recorded the `Var` node.

### Step 1.4: Check the operators, one family at a time

Operators are where most ill-typed programs fail, and where a message that names only one type is easiest to write by accident.  Every operator error names both operand types.

> **Do this.**
> 1. Arithmetic first.  In `check_expr`, handle `BinOp` with `op` in `+ - * /`: both operands must be `NUM`, and the result is `NUM`.
> 2. Comparison next: `< <= > >=` require `NUM` operands and yield `BOOL`.
> 3. Equality: `== !=` require both sides to have the same type and yield `BOOL`.
> 4. Boolean operators last: `LogicOp` (`and`, `or`) requires `BOOL` on both sides and yields `BOOL`; `UnaryOp` with `not` requires `BOOL` and yields `BOOL`; `UnaryOp` with `-` requires `NUM` and yields `NUM`.
> 5. Add `If` and `While` to `check_stmt`: check the condition, then check each branch or body as a `Block`.  Whether the condition must be `BOOL` is a design decision you make here; the first reflection prompt asks you to defend it.
> 6. After each family, run the driver on the provided programs that exercise it.

> **You should see.**  For `let x: Num = 1 + true;` on line 1, one line of the form `Type error at line 1, col 16: '+' requires Num operands, got Num and Bool`, and nothing else.  The column is wherever your parser recorded the `BinOp` node, and the wording after the colon is yours, provided both types appear in it.

> **If it fails.**
> - The message names one type: you formatted the expected type but not the actual one, or the other way around.  Both must appear.
> - `NotImplementedError` on a program it should reject: an operator family is still missing.  Read the node name in the message.
> - A program with an error on line 5 also prints output from line 1: something is evaluating.  The checker calls no evaluator and prints nothing except the error.

### Step 1.5: Run the twelve provided programs and keep the log

Verify your checker against the provided programs in the course starter repo.  Six well-typed programs must pass silently.  Six ill-typed programs must each produce a positioned error; these include the classic `let x: Num = 1 + true;` (the error must appear *before* anything runs) and a shadowing case where an inner `let x: Str` legitimately changes the type of `x` for the inner scope only.

> **Do this.**
> 1. Copy all twelve provided programs into `programs/`.
> 2. Run the driver over every one of them and save the output.  The `for` loop runs the checker once per file, `echo` labels each run with its file name, and `tee` prints the output and writes it to `runlog.txt` at the same time.  If the provided programs use a different file extension, change `*.ml` to match.
>
> ```bash
> for f in programs/*.ml; do echo "== $f"; python3 typechecker.py "$f"; done | tee runlog.txt
> ```
>
> 3. Read `runlog.txt` once, top to bottom, and confirm each well-typed program shows only its label and each ill-typed program shows its label and one `Type error` line.

> **You should see.**  Twelve labels.  Six are followed directly by the next label (silent acceptance).  Six are followed by exactly one `Type error at line L, col C: ...` line naming two types.

```text
== programs/<a well-typed program>.ml
== programs/<the 1 + true program>.ml
Type error at line 1, col 16: '+' requires Num operands, got Num and Bool
== programs/<the shadowing program>.ml
```

---

## Part 2: Write the Typing Rules on Paper (27%)

In `RULES.md`, state the typing rule for each construct your checker covers, one rule per construct.  A typing rule has premises (what must already be true about the parts) and a conclusion (what then holds for the whole).  Writing the rules after the code is deliberate: the code tells you what you actually enforced, and the rule tells you whether that was what you meant.  This document becomes the seed of the Interpreter assignment's semantics writeup, and if you later choose the full Hindley-Milner direction (type inference, which works out types with no annotations at all), these rules are exactly what inference generalizes.

### Step 2.1: State one rule per construct and cite its code

> **Do this.**
> 1. Create `RULES.md` in your lab folder, with both partners named at the top (below your Part 0 answers, if you typed them there).
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

1.  Place four languages (Python, C, Haskell, and JavaScript) on the static/dynamic × strong/weak quadrant, with one sentence of justification each.
2.  Your checker makes the class language *gradually* typed in spirit: annotated declarations are checked, and unannotated territory is documented as unchecked.  State one benefit and one risk of that middle ground, using the mypy/TypeScript comparison from class.

---

## Deliverables

Submit a ZIP containing the files below, with both partners named in `RULES.md`.

| File or artifact | What it shows | Rubric row |
|------------------|---------------|------------|
| Part 0 write-up (at the top of `RULES.md`, or a photo of your page) | The annotated program, the rejected expression with your defended preference, and the guarantee and forbidden program | Part 0: Before You Start - Type Systems |
| `typechecker.py` | The type environment, `check()`, and the literal, variable, declaration, and operator rules | The Checker Core |
| `runlog.txt` | The checker's output over the twelve provided programs: six silent, six positioned errors | The Checker Core |
| `RULES.md` | One rule per construct with its implementing function cited, and the two theory questions | Typing Rules on Paper |

## Self-Check Before You Submit

- [ ] Every one of the six well-typed programs produces no output.
- [ ] Every one of the six ill-typed programs produces exactly one `Type error at line L, col C: ...` line, and that line names both conflicting types.
- [ ] `let x: Num = 1 + true;` is rejected before anything runs, and the shadowing program's inner `let x: Str` is accepted for the inner scope only.
- [ ] The checker calls no evaluator and prints nothing except the error.
- [ ] `RULES.md` has one rule per construct the checker covers, each with its premises stated and its implementing function cited.
- [ ] `RULES.md` answers the quadrant question and the gradual-typing question.
- [ ] Both partners are named in `RULES.md`, and any reference component you built on is declared in one line.

## Grading Breakdown

This lab is worth 15 points, as the course schedule states.  Each part's weight below is a percentage of those 15 points, and the rubric rows use the same percentages.

| Component | Weight |
|-----------|--------|
| Part 0: Type Systems | 10% |
| Part 1: The Checker Core | 63% |
| Part 2: Typing Rules on Paper | 27% |
| **Total** | **100% (15 points)** |

## Reflection Prompts

- Your checker rejects `while 1 { ... }` if you require a `Bool` condition, though the evaluator's truthiness rule would happily run it.  Which behavior do you consider correct for the class language, and why?
- If you worked in a pair, who did what, and name one thing your partner caught that you would have missed.  If you worked alone, note that instead.
