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

This **lab** builds the core of the Interpreter assignment's Part 4: a small static type checker that runs between parsing and evaluation.  A static type checker reads the abstract syntax tree (AST) of a program and decides whether each operation makes sense before any of the program runs.  With a partner, you get the checker working on its three simplest cases: literals, variables, and operators.  The Interpreter assignment then has you extend it on your own to call sites and return types.  Plan on one working session.

**Pair policy.**  You may do this lab in pairs.  Submit the same files, name both partners in them, and you will both earn the same grade.  Working alone is also allowed.  The Interpreter assignment remains individual work: both partners may carry this shared checker core into it, but the extension to calls and returns must be your own.

---

## Part 0: Before You Start - Type Systems (10%)

Do this part before you write the checker, and ideally before the Type Systems session.  Plan on about fifteen minutes with pencil and paper.

The point of Part 0 is to arrive with an example.  Everyone has an opinion about static typing; an example is what makes the argument worth having.

1.  Write a small program and annotate each subexpression with the type you expect it to have.  Then find one expression that a static type checker would reject but a dynamic language would run.  Say which behavior you prefer there, and why.
2.  State one guarantee a type system gives you, and one program it forbids that you wish it allowed.

Bring the program you wish the checker had allowed, even if you could not settle the question.  The unsettled cases are the ones we argue about, and Part 1 makes you take a side in code.

---

## Part 1: The Checker Core (63%)

Implement `check(program) -> None` in `typechecker.py`.  The function walks the class AST (use your Parser assignment's AST nodes, or the reference AST) and reports a type error as soon as it finds one.  A well-typed program produces no output.

The checker carries a type environment as it walks.  A type environment uses the same parent-chaining discipline as the `Environment` class from your Environments lab, but it binds each name to a *type* instead of a value.  Entering a block creates a child environment, and leaving the block discards it.

Your checker enforces these rules:

- **Literals:** numbers are `Num`, strings are `Str`, booleans are `Bool`.
- **Declarations:** `let x: Num = expr;` checks that `expr`'s type equals the annotation, then binds `x : Num` in the current scope.  A mismatch is an error naming both types.
- **Variables:** a use of `x` looks up its declared type; an undeclared use is a positioned error.
- **Operators:** `+ - * /` require `Num` operands and yield `Num`; `< <= > >=` require `Num` and yield `Bool`; `== !=` require both sides to have the same type and yield `Bool`; `and`/`or`/`not` require `Bool`.  Every violation is reported as `Type error at line L, col C: ...` naming **both** conflicting types.

A workable order of construction:

1.  Write the type environment: a way to bind a name to a type in the current scope, and a lookup that follows the parent chain.
2.  Handle literals, so the simplest programs type-check.
3.  Handle declarations and variable uses, which exercise the environment and its scoping.
4.  Handle operators one family at a time: arithmetic, then comparison, then equality, then the boolean operators.
5.  Run the provided programs after each step and keep the output as your run log.

Verify your checker against the provided programs in the course starter repo.  Six well-typed programs must pass silently.  Six ill-typed programs must each produce a positioned error; these include the classic `let x: Num = 1 + true;` (the error must appear *before* anything runs) and a shadowing case where an inner `let x: Str` legitimately changes the type of `x` for the inner scope only.

Two things to remember from this part.  The checker never evaluates anything; it only compares types.  And every error message names the position and both conflicting types.

## Part 2: Typing Rules on Paper (27%)

In `RULES.md`, state the typing rule for each construct your checker covers, one rule per construct.  A typing rule has premises (what must already be true about the parts) and a conclusion (what then holds for the whole).  Write each rule in either inference-rule layout (premises above a line, conclusion below it) or a disciplined "if... then..." sentence (e.g., *if `e1 : Num` and `e2 : Num`, then `e1 + e2 : Num`*).  For each rule, cite the function or branch in `typechecker.py` that implements it.

This document becomes the seed of the Interpreter assignment's semantics writeup.  If you later choose the full Hindley-Milner direction (type inference, which works out types with no annotations at all), these rules are exactly what inference generalizes.

Close `RULES.md` with two theory questions from the Type Systems session:

1.  Place four languages (Python, C, Haskell, and JavaScript) on the static/dynamic × strong/weak quadrant, with one sentence of justification each.
2.  Your checker makes the class language *gradually* typed in spirit: annotated declarations are checked, and unannotated territory is documented as unchecked.  State one benefit and one risk of that middle ground, using the mypy/TypeScript comparison from class.

---

## Deliverables

Submit a ZIP containing `typechecker.py`, the run log over the twelve provided programs, and `RULES.md` with both partners named.

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
- AI disclosure: list any generative-AI tools you used, for what, and how you verified the results (or state 'none').
- Approximately how many hours it took you to finish this lab (I will not judge you for this at all; I am simply using it to gauge if the labs are too easy or hard)?

## From the Type Systems Activity: A Dynamically, Strongly Typed Core

The material below was previously delivered in the *Type Systems* class session.  It lives here instead because it is this lab: a runtime checker for the interpreter you are building, traced on compound expressions, followed by a worked type-error postmortem.  Read it before you start Part 1.

## Part II: Types in Your Interpreter

**Intuition for Section 2.**  Your interpreter already evaluates binary expressions like `3.0 + 4.0`.  This section adds a gatekeeper at the top of that evaluation: before you touch the operands, check whether the combination makes sense, and raise a clear error if it does not.  Think of a bouncer who checks IDs before letting values into an operation: `float + float` gets in, `float + string` does not.  The analogy stops there, because a bouncer turns people away quietly while your checker must raise an error that names both types.

### 2.  A Dynamically, Strongly Typed Core

Your language checks types at runtime and refuses silent coercion, the same choice Python makes.  Coercion is a conversion the language performs on its own, such as turning the number `5` into the string `"5"` so that it can be concatenated.  Refusing to coerce is what makes the typing *strong*; checking while the program runs, rather than before it starts, is what makes it *dynamic*.  The implementation pattern is short: each evaluated value already carries its Python type, so the binary-operation evaluator checks the operand types before it computes.

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

Read the code in this order.  `type_name` turns a Python type into the name your error messages will print.  The first `if` in `eval_binop` handles arithmetic: it allows string concatenation, refuses booleans, computes on two floats, and refuses everything else.  The second `if` handles comparisons, which require both sides to have the same type.  The loop at the bottom runs six operand pairs, three that pass and three that fail.

#### Critical Thinking Questions

5.  Identify the lines that make this typing *strong* (refusals) versus the line that would make it *weak* if you replaced a refusal with `float(...)` coercion.  Make the weak version mentally: what does `3.0 + "cd"` return, and what bug class did you just legalize?
6.  We licensed `+` for two strings but not `*` for string and number.  Python licenses `"ab" * 3`.  Debate and record your project's policy on string repetition, and add it to `SEMANTICS.md`.
7.  Where would a *static* checker for your language live in the pipeline (between which two existing stages), and what would it walk?  You already own every data structure it needs; name them.

Python raises a TypeError on `"5" - 1` at the moment the subtraction executes, never silently converting.  On the two axes, Python is therefore:

- Statically and weakly typed
- Statically and strongly typed
- Dynamically and strongly typed
- Dynamically and weakly typed

<details><summary>Answer</summary>

Dynamically and strongly typed

</details>

A language that deduces `n: int` from `let n = 5` without requiring the programmer to write the type annotation is using:

- Dynamic typing
- Weak typing
- Type inference
- Duck typing

<details><summary>Answer</summary>

Type inference

</details>

> **Watch out!**  Duck typing (Python's "if it walks like a duck and quacks like a duck, treat it as a duck") is still a form of typing.  It is a dynamic, structural approach: compatibility is checked by whether an object supports the required operations, not by its declared class.  Saying a language "has no types" because it uses duck typing is incorrect.  Duck typing is a deliberate design choice that trades the early-error benefits of nominal or structural static checks for maximum flexibility.

---

**Intuition for Model 2.**  A dynamically typed interpreter never checks anything in advance; every check rides along with evaluation itself.  Picture evaluation as water rising from the leaves of the AST: values form at the literals and meet at each operator, and at each meeting point the bouncer from Section 2 checks the pair before combining them.  This model slows that flow to one step at a time, so you can see exactly when each check fires and, just as important, what has already happened by the time a check fails.

### Model 2: Tracing the Runtime Checker on a Compound Expression

**Worked example.**  Trace the interpreter evaluating `(3.0 + 4.0) < (2.0 * 6.0)`.  Evaluation is bottom-up (innermost first), so the checks fire in this order:

| Step | Node evaluated | Left value : type | Right value : type | Check performed | Result |
|------|----------------|-------------------|--------------------|-----------------|--------|
| 1 | `3.0 + 4.0` | `3.0` : number | `4.0` : number | `+` licensed for number, number | `7.0` |
| 2 | `2.0 * 6.0` | `2.0` : number | `6.0` : number | `*` licensed for number, number | `12.0` |
| 3 | `7.0 < 12.0` | `7.0` : number | `12.0` : number | `<` requires same type, OK | `True` |

Three checks, three passes, one final value.  Now the same trace for `(3.0 + 4.0) < ("total: " + 12.0)`:

| Step | Node evaluated | Left value : type | Right value : type | Check performed | Result |
|------|----------------|-------------------|--------------------|-----------------|--------|
| 1 | `3.0 + 4.0` | `3.0` : number | `4.0` : number | `+` licensed | `7.0` |
| 2 | `"total: " + 12.0` | `"total: "` : string | `12.0` : number | `+` **not** licensed for string, number | **TypeError** |
| 3 | `... < ...` | - | - | never reached | - |

Step 1 completed *before* the error, so its work is done and cannot be undone.  The `<` at step 3 never runs at all.  That is dynamic checking in one picture: checks are interleaved with execution, so an error stops the program in flight rather than before takeoff.

The program below performs both traces and narrates each check as it fires.

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

An interpreter with dynamic (runtime) checking evaluates `(3.0 + 4.0) < ("a" + 1.0)`.  When is the type error for `"a" + 1.0` detected?

- Before execution begins
- When the `<` comparison runs
- At the moment the `+` on `"a"` and `1.0` is evaluated, after `3.0 + 4.0` has already computed
- Never; dynamic languages coerce automatically

<details><summary>Answer</summary>

At the moment the `+` on `"a"` and `1.0` is evaluated, after `3.0 + 4.0` has already computed

</details>

#### Critical Thinking Questions

8.  The trace shows the checks firing in steps 1, 2, 3, the same order as evaluation.  State the general rule: in a dynamically typed interpreter, when does the check for an operator fire, relative to the evaluation of that operator's operands?
9.  In the failing trace, step 1 finished before the TypeError at step 2.  Suppose step 1 had been `print("charging card...")` instead of an addition.  What does this tell you about *where in a program's lifetime* you would prefer type errors to fire, and which typing discipline delivers that?
10.  Redo the failing trace as a *static* checker would perform it, before execution: rewrite the table with types only, no values.  Which columns disappear, and which check still fails?

Remember from this model: a runtime check fires only after both operands have been evaluated.  Whatever those evaluations did has already happened when the check fails.

---

**Intuition for Model 3.**  Type inference is the trick where the checker works out every variable's type from context alone: you write `let a = 2` and it deduces `a: int` without you saying so.  Mechanically, it is a tree walk.  Visit each node, compute the type it must produce, and pass that type upward.  When two branches disagree (for example, adding an `int` to a `str`), the checker reports an error *at that node*, which can be far from the actual mistake if the mistake was made pages earlier.

### Model 3: Type Inference by Hand

The program below implements Hindley-Milner style inference in miniature.  Read `infer` from the top: each `if kind == ...` branch is one typing rule, and the `let` branch is where the type environment grows.

```python
# Mini type inference: propagate types through a simple expression AST

from dataclasses import dataclass
from typing import Any, Optional

@dataclass
class TInt:   pass
@dataclass
class TFloat: pass
@dataclass
class TStr:   pass
@dataclass
class TBool:  pass
@dataclass
class TUnknown: pass  # not yet inferred

def type_str(t):
    return {TInt: "int", TFloat: "float", TStr: "str",
            TBool: "bool", TUnknown: "?"}[type(t)]

# "Type environment": name -> type
type_env = {}

def infer(expr, env):
    """Infer the type of an expression given a type environment."""
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

# Program: let a = 2; let b = a + 3; let c = b < 10; in c
print("=== Type Inference Trace ===")
program = ("let", "a", ("int",), ("let", "b", ("add", ("var", "a"), ("int",)),
           ("let", "c", ("lt", ("var", "b"), ("int",)), ("var", "c"))))
try:
    result_type = infer(program, {})
    print(f"Result type: {type_str(result_type)}")
except TypeError as e:
    print(f"Type error: {e}")

# Program with error: let a = 2; let d = a + "hello", type error
print("\n=== Type Error Program ===")
bad_program = ("let", "a", ("int",), ("add", ("var", "a"), ("str",)))
try:
    result_type = infer(bad_program, {})
    print(f"Result type: {type_str(result_type)}")
except TypeError as e:
    print(f"Type error: {e}")
```

#### Worked Example: Tracing Type Inference Step by Step

Consider the small program: `let a = 2; let b = a + 3; let c = b < 10; in c`

The `infer` function walks this AST top-down and builds a type environment (a mapping from variable names to their inferred types) as it goes:

| Step | Node visited | Type environment before | Result type deduced |
|------|-------------|------------------------|---------------------|
| 1 | `let a = ("int",)` | `{}` (empty) | literal `("int",)` -> `TInt` |
| 2 | Extend env with `a: TInt`; recurse into body | `{a: TInt}` | - |
| 3 | `let b = ("add", ("var","a"), ("int",))` | `{a: TInt}` | look up `a` -> `TInt`; literal -> `TInt`; `TInt + TInt` -> `TInt` |
| 4 | Extend env with `b: TInt`; recurse into body | `{a: TInt, b: TInt}` | - |
| 5 | `let c = ("lt", ("var","b"), ("int",))` | `{a: TInt, b: TInt}` | look up `b` -> `TInt`; literal -> `TInt`; same type -> `TBool` |
| 6 | Extend env with `c: TBool`; body is `("var","c")` | `{a: TInt, b: TInt, c: TBool}` | look up `c` -> `TBool` |
| **Final** | whole program | - | **`TBool`** |

Now trace the *error* program: `let a = 2; a + "hello"`

| Step | Node visited | Type environment | Result |
|------|-------------|-----------------|--------|
| 1 | `let a = ("int",)` | `{}` | `TInt` |
| 2 | Extend env; recurse into body `("add", ("var","a"), ("str",))` | `{a: TInt}` | - |
| 3 | left: look up `a` -> `TInt`; right: `("str",)` -> `TStr` | `{a: TInt}` | `TInt + TStr` -> **TypeError**: `cannot add int and str` |

The error is reported at the `add` node (step 3), but the root cause is the choice made at step 1.  This distance between the error location and the root cause is a recurring problem in type inference, and the reason good inference error messages are hard to write.

#### Critical Thinking Questions

11.  The inference trace shows `let a: int`, `let b: int`, `let c: bool`.  These are determined entirely from the *values* (literals), with no type annotations written.  Is this static or dynamic typing?  Explain.
12.  When inference encounters `a + "hello"`, it reports the error at the `add` expression.  But the *root cause* is that `a` was given an int value.  How far is the reported error from the root cause, and what does this say about inference error message quality?
13.  What would need to change to support `let a = 2; let b = a + 3.0;`?  (Hint: numeric type widening, `int + float -> float`.)  Modify the `infer` function to allow this.

Remember from this model: inference computes a type for every node without running the program, so it is static.  The price is that an error surfaces where the types collide, not where the mistake was made.

---

**Intuition for Model 4.**  The danger of weak typing is not crashes; it is the absence of crashes.  When a language coerces instead of refusing, a type mistake does not stop the program.  The mistake flows onward disguised as a plausible-looking value, and the first symptom appears far from the cause, often outside the program entirely.  This model performs a postmortem on one such incident, step by step, with the strong-typing alternative traced alongside for contrast.

### Model 4: A Type-Error Postmortem

**The incident.**  A checkout system written in a weakly typed language reads a price from a web form.  Form fields always arrive as *strings*, and nobody converted.  Here is the program:

```
subtotal = "19.99"                       # from the form: a STRING, not a number
shipping = 5.00
total    = (subtotal + shipping) * 1.06  # add shipping, then 6% tax
```

The intended arithmetic: `(19.99 + 5.00) * 1.06 = 24.99 * 1.06 = 26.49`.  What the weak language actually computes, step by step:

| Step | Expression | What a weak language does | Value after | What a strong language does |
|------|-----------|----------------------------|-------------|------------------------------|
| 1 | `subtotal = "19.99"` | stores the string | `"19.99"` (string) | the same; the mistake is still latent |
| 2 | `subtotal + 5.00` | coerces `5.00` -> `"5"`, then *concatenates* | `"19.995"` (string) | **TypeError: cannot add string and number**, stops here |
| 3 | `"19.995" * 1.06` | coerces `"19.995"` -> `19.995`, then multiplies | `21.1947` (number) | never reached |
| 4 | charge the customer | charges `$21.19` with no error anywhere | wrong by `$5.30` | bug reported at step 2, with a line number |

Note the direction flip.  At step 2 the `+` coerced the *number toward the string*, but at step 3 the `*` coerced the *string toward the number*.  The same pair of types flowed in opposite directions depending on the operator.  That inconsistency, not any single conversion, is what makes weak typing treacherous.  And notice what is missing from the weak column: any error, at any step.  The only symptom is money.

The program below simulates both disciplines on the same buggy input.

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

In a weakly typed language, `"19.99" + 5.0` yields `"19.995"` and `"19.995" * 1.06` yields `21.1947`.  The deepest design problem this postmortem illustrates is:

- Floating-point rounding error
- The slowness of string operations
- Silent coercion lets a type mistake flow through the program as plausible-looking wrong values instead of stopping with an error
- Strings cannot represent decimal numbers

<details><summary>Answer</summary>

Silent coercion lets a type mistake flow through the program as plausible-looking wrong values instead of stopping with an error

</details>

#### Critical Thinking Questions

14.  Walk the postmortem table: at which step did the *type* first go wrong, and at which step did the *money* first go wrong?  Why is it significant that these are different steps?
15.  Step 2 coerced number -> string, but step 3 coerced string -> number.  Write the coercion rule a language designer would have to publish to justify both choices at once.  Does the result sound principled or accidental?
16.  The weak-mode run produces no error at any point; the bug would surface only as customer complaints.  Name two other places in the software pipeline (besides the language's type system) where this bug could have been caught, and what each catch would cost compared to a step-2 TypeError.
17.  For your project language: which, if any, of these coercions will you allow?  Record the decision in `SEMANTICS.md`, citing this postmortem as evidence for or against.

Remember from this model: a strong type system reports the mistake at the line where the types first disagree.  A weak one lets the mistake travel until something outside the program notices.

---
