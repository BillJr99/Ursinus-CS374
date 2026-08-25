<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374-Fall2026/gh-pages/_pages/Activities/liascript-types.md or locally via https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374-Fall2026/gh-pages/_pages/Activities/liascript-types.md

import: https://raw.githubusercontent.com/liascript/CodeRunner/master/README.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

# Type Systems

Every time you write

```python
def add(x, y):
    return x + y
```

you are making an implicit promise: callers will pass values that support `+`.  A **type system** is the machinery that turns an informal promise like that into an enforceable contract, checked either before your program ever runs or the instant a broken promise is exercised.  Catching a broken promise in the checker is like catching a typo before you mail the letter; catching it at runtime is like finding out when the recipient tries to read it.

## Learning Goals

By the end of this activity, you will be able to:

- Place a language on the two independent axes of type-system design (static/dynamic and strong/weak), and defend the placement with a one-line program
- Predict whether a given type error surfaces at parse time, check time, or run time, and explain what determines that
- Read and extend a type checker that walks an AST computing *types* rather than values
- Infer the types of a program's variables with no annotations present, and identify the first line a checker would reject
- Explain why gradual type systems are deliberately unsound, and what that buys
- Specify the typing rules for your team's language and justify them against the evaluation criteria

Your interpreter (now equipped with the environments of *Environments and Variable Storage*) knows what to do with `5 / 0`.  But what should it do with

```
"hello" * true
```

Today's path: **the two axes $\rightarrow$ checking before you run $\rightarrow$ inference $\rightarrow$ gradual typing**.

> **Before You Begin:** This activity assumes you can:
> - Explain the difference between a crash at parse time and one during execution
> - Read and write basic Python, including `try`/`except` and `isinstance()`
> - Describe what your interpreter's `evaluate` function does with a binary operation node
>
> If any of these feel shaky, review them first.

---

## Directions and Group Roles

Work in your POGIL team with your rotated roles (**Manager**, **Recorder**, **Presenter**, **Reflector**).  Every model in this deck runs: predict the output first, in writing, then press the run button and see whether the machine agrees with you.  The disagreements are the interesting part, so keep them.  The Recorder posts your answers to the Class Activity Questions discussion board, and the Presenter reports out wherever your team disagreed or found another approach.

---

## Key Concepts

A plain-English glossary.  Come back to it whenever one of these starts to feel slippery.

| Term | Plain-English meaning | Why it matters |
|------|-----------------------|----------------|
| **Type** | A label on a value that says which operations are licensed for it | The whole activity is about who checks these licenses, and when |
| **Type error** | An operation applied to a value outside its license, like `"hi" * {}` | The failure every type system exists to catch, early or late |
| **Static typing** | Checking happens *before* the program runs | Catches errors on every path, including paths your tests never exercise |
| **Dynamic typing** | Checking happens at the instant each operation executes | Maximum flexibility; errors surface only when the bad line actually runs |
| **Strong typing** | The language refuses to silently mix incompatible types | Broken promises stop the program instead of flowing onward as wrong values |
| **Weak typing** | The language silently converts operands so the operation can proceed | The source of `"5" - 1 == 4` surprises; convenience purchased with silence |
| **Coercion** | An implicit, automatic conversion the programmer never asked for | The defining behavior of weak typing; contrast with explicit conversion |
| **Type inference** | The checker deduces types from values and context, with no annotations written | Static safety without annotation ceremony: Rust, Haskell, TypeScript |
| **Type environment** | A mapping from variable names to their types | The checker's version of your interpreter's environment: names to types, not values |
| **Gradual typing** | Some parts of a program are checked statically, the rest stay dynamic | How mypy and TypeScript retrofit checking onto languages that started without it |

---

# Part I: The Two Axes

## 1.  Theory: Two Independent Questions

People say "strongly typed" to mean half a dozen different things.  Untangle it into two questions that have nothing to do with each other.

**When is checking done?**  **Static** typing checks before execution: Java rejects

```java
int x = "hi";
```

at compile time, without running anything.  **Dynamic** typing checks during execution, at the moment the operation runs: Python raises `TypeError` only when `"hi" * {}` is actually attempted.  Static catches errors earlier and on *all* paths, including the ones your tests never reach; dynamic permits more flexible code and faster iteration.  This is the binding-time framework from *Names, Binding, and Scope* again, applied to the type.

**How strictly is checking enforced?**  **Strong** typing refuses undefined mixtures, or demands an explicit conversion.  **Weak** typing silently **coerces** operands so the operation can proceed.  JavaScript computes

```javascript
"5" - 1     // 4
"5" + 1     // "51"
```

Python, dynamically but *strongly* typed, refuses `"5" - 1` outright.

The two axes are independent, so a language picks a point on each one.

## Examples: The Quadrant, by Hand

Before any code, place these languages yourself.  Fill in the four cells from what you already know, then compare with your team.

|                | **Static** (checked before running) | **Dynamic** (checked while running) |
|----------------|-------------------------------------|-------------------------------------|
| **Strong** (little or no silent coercion) | Haskell, Rust, Java (mostly), OCaml | **Python**, Ruby, Scheme, **your CS374 interpreter** |
| **Weak** (silent coercion or bit reinterpretation) | C, C++ | JavaScript, PHP, Perl |

Now work one expression across all four quadrants.  For each language, write down *when* the failure happens and *what* the result is:

| `"a" + 1` in ... | Quadrant | What happens |
|------------------|----------|--------------|
| Haskell | static, strong | Compile error; the program never runs |
| Python | dynamic, strong | `TypeError` at runtime, at that line |
| C | static, weak | `'a' + 1` is `98`; a `char` is just a small integer |
| JavaScript | dynamic, weak | `"a1"`; the number is coerced to a string |

Notice that the *same* expression fails in two of these and succeeds, surprisingly, in the other two.  That is the whole point of the two axes: they predict behavior that "strongly typed" alone cannot.

Your CS374 interpreter deliberately sits in the strong/dynamic box: `SEMANTICS.md` says that adding a string to a number raises a positioned `LangTypeError` at evaluation time.  That is a design choice, and stating it precisely is part of the Interpreter assignment.

> **Watch out!**  Static does not imply strong, and dynamic does not imply weak.  C is static but weak; Python is dynamic but strong.  Keep the axes separate, because collapsing them is the single most common confusion in this unit.

> **Watch out!**  Python is *not* "untyped."  Every Python value has a definite type: `type(42)` is `<class 'int'>`.  The language simply checks compatibility at runtime rather than before execution.  Calling Python "untyped" confuses the absence of *declared* types with the absence of types altogether.

## Model 1: Discover the Axes by Experiment

**Predict first.**  Before you run this, write down what each of the five probes below will print.  Then run it.

```python
# Python: dynamic (checks at runtime) + strong (refuses coercion).
# Each probe below tests ONE of those two properties.

print("=== Probe 1: is Python strong? ===")
for expr, thunk in [
    ('"5" - 1',      lambda: "5" - 1),
    ('"hello" + 42', lambda: "hello" + 42),
    ('"5" * 3',      lambda: "5" * 3),
]:
    try:
        print(f"  {expr:14} -> {thunk()!r}")
    except TypeError as e:
        print(f"  {expr:14} -> TypeError: {e}")

print("\n=== Probe 2: is Python dynamic? ===")
def risky(x):
    return x * 2        # licensed for int, float, str, list -- but not dict

for value in [5, "ab", [1, 2], {"k": 1}]:
    try:
        print(f"  risky({value!r:10}) -> {risky(value)!r}")
    except TypeError as e:
        print(f"  risky({value!r:10}) -> TypeError: {e}")

print("\n=== Probe 3: values carry types; names do not ===")
x = 42
print(f"  x = 42          -> type(x) is {type(x).__name__}")
x = "now a string"
print(f"  x = 'now a...'  -> type(x) is {type(x).__name__}")
print("  The object's type never changed; the NAME was rebound.")

print("\n=== Probe 4: the hidden-path problem ===")
def categorize(n):
    if n > 100:
        return n / 2        # only this branch divides
    return n + 1

print(f"  categorize(50)  = {categorize(50)}")
print(f"  categorize(200) = {categorize(200)}")
print("  100% line coverage on the first branch still never divides.")
print("  A static checker examines BOTH branches without running either.")

print("\n=== Probe 5: annotations are not checks ===")
def add(a: int, b: int) -> int:
    return a + b

print(f"  add('x', 'y') = {add('x', 'y')!r}")
print("  CPython ignored the annotations entirely. They are documentation.")
```
@LIA.eval(`["main.py"]`, `none`, `python3 main.py`)

### Reading the Code

- **Probe 1** tests *strength*.  Each expression is wrapped in a `lambda` so the failure happens inside the loop where we can catch it, rather than when the list is built.  Two of the three raise; `"5" * 3` succeeds because Python licenses string repetition, which is a genuine operation and not a coercion.
- **Probe 2** tests *dynamism*.  The same `risky` body succeeds for four different argument types and fails for a fifth, and nothing detected that before the call.
- **Probe 3** separates *values* from *names*.  Rebinding `x` did not mutate the integer `42`; it pointed the name at a different object.
- **Probe 4** is the argument for static checking, in five lines.  A test suite that only ever calls `categorize(50)` reports full coverage of the line it ran and never touches the division.
- **Probe 5** is the setup for Part III.  Python's annotation syntax exists, and CPython does nothing with it.

### Critical Thinking Questions

1.  Fill in the quadrant table above and name a plausible language for each cell.  For each, give the one-line program that proves the placement.
2.  JavaScript's coercion maximizes which criterion from *Evaluating Languages*, and damages which?  Use the asymmetry between `"5" + 1` and `"5" - 1` as your evidence.
3.  Probe 1 shows `"5" * 3` succeeding.  Is that coercion?  Argue both sides, then commit to an answer and say what distinguishes coercion from a legitimately overloaded operator.
4.  Probe 4 constructs a program where a test suite reports full coverage and still misses a type error.  Write a *different* two-branch program with the same property, and explain why coverage did not save you.

### Try It Yourself

Add a sixth probe that demonstrates the *strong* axis failing in the other direction: find a pair of Python types where `+` succeeds but you would argue it *should not*, and print evidence.

```python
# Probe 6: find a "+" that Python licenses but that you think it should refuse.
# Start here and replace the TODO.

candidates = [
    (True, 1),          # bool + int
    # TODO: add two more pairs of your own
]

for left, right in candidates:
    try:
        print(f"  {left!r} + {right!r} = {left + right!r}"
              f"   (types: {type(left).__name__} + {type(right).__name__})")
    except TypeError as e:
        print(f"  {left!r} + {right!r} -> TypeError: {e}")

print("\nWhich of these would a STRONGER language refuse, and what would it cost?")
```
@LIA.eval(`["main.py"]`, `none`, `python3 main.py`)

Expected output: at minimum, `True + 1 = 2  (types: bool + int)`.  Python's `bool` is a subclass of `int`, so this is licensed; decide for yourself whether it should be.

---

# Part II: Checking Types Before You Run

## 2.  Theory: A Checker Walks the Tree Computing Types

Here is the central idea of the whole unit, and it is smaller than it sounds.

Your evaluator walks the AST computing **values**.  A type checker walks the *same* AST computing **types**.  It is the same recursive traversal, over the same tree, with the same shape of case analysis; only the thing being computed changes.

Where `evaluate(BinOp("+", l, r), env)` returns a number, `infer(BinOp("+", l, r), tenv)` returns the *type* `Int`, and refuses if either side is not `Int`.  Where the evaluator carries an environment mapping names to values, the checker carries a **type environment** mapping names to types.

We write the rules as **typing judgments**.  Read

$$\Gamma \vdash e : \tau$$

as "in type environment $\Gamma$, expression $e$ has type $\tau$."  A rule has premises above the line and a conclusion below it:

$$\frac{\Gamma \vdash e_1 : \text{Int} \qquad \Gamma \vdash e_2 : \text{Int}}{\Gamma \vdash e_1 + e_2 : \text{Int}}$$

In English: if both operands check as `Int`, then the sum checks as `Int`.  Every rule you will implement is one of these, and the implementation is a direct transcription: check the premises, return the conclusion's type.

Two rules deserve special attention because they are where students' intuitions usually break:

$$\frac{\Gamma \vdash c : \text{Bool} \qquad \Gamma \vdash e_1 : \tau \qquad \Gamma \vdash e_2 : \tau}{\Gamma \vdash \texttt{if } c \texttt{ then } e_1 \texttt{ else } e_2 : \tau}$$

Both branches must have the *same* type $\tau$.  They must, because the checker has to name a single type for the whole `if` expression without knowing which branch will run.

$$\frac{\Gamma \vdash e_1 : \tau_1 \qquad \Gamma, x{:}\tau_1 \vdash e_2 : \tau_2}{\Gamma \vdash \texttt{let } x = e_1 \texttt{ in } e_2 : \tau_2}$$

The `let` rule is where the type environment grows: check the bound expression, extend $\Gamma$ with the new name, then check the body under the extended environment.  That is exactly what your interpreter's `Env.extend` does, one level up.

## Examples: A Type Derivation, by Hand

Work this one on paper before running anything.  Take the expression

```
let x = 2 in if x < 5 then x + 1 else 0
```

and derive its type bottom-up, filling in each step:

| Step | Sub-expression | Type environment $\Gamma$ | Type | Rule used |
|------|----------------|---------------------------|------|-----------|
| 1 | `2` | $\varnothing$ | `Int` | literal |
| 2 | `x` | $x{:}\text{Int}$ | `Int` | variable lookup |
| 3 | `5` | $x{:}\text{Int}$ | `Int` | literal |
| 4 | `x < 5` | $x{:}\text{Int}$ | ? | comparison |
| 5 | `x + 1` | $x{:}\text{Int}$ | ? | addition |
| 6 | `0` | $x{:}\text{Int}$ | ? | literal |
| 7 | `if ... then ... else ...` | $x{:}\text{Int}$ | ? | conditional |
| 8 | the whole `let` | $\varnothing$ | ? | let |

Now do it again for a program that *fails*:

```
let x = 2 in if x then x + 1 else 0
```

At which step does the derivation get stuck, and which premise fails?  Note that nothing was executed to find this out.

## Model 2: A Type Checker You Can Run

This is the machinery from the Examples above, transcribed.  Compare each `if isinstance(...)` branch against the corresponding judgment.

```python
from dataclasses import dataclass
from typing import Any

# --- AST for a small expression language -------------------------------------
@dataclass
class Num:  value: float
@dataclass
class Bool: value: bool
@dataclass
class Var:  name: str
@dataclass
class BinOp: op: str; left: Any; right: Any
@dataclass
class If:   cond: Any; then_e: Any; else_e: Any
@dataclass
class Let:  name: str; val: Any; body: Any

class TypeError_(Exception):
    """A type error found BEFORE the program runs."""

# --- The type environment: names to TYPES, not to values ---------------------
class TypeEnv:
    def __init__(self, bindings=None, parent=None):
        self.bindings = bindings or {}
        self.parent = parent
    def lookup(self, name):
        if name in self.bindings: return self.bindings[name]
        if self.parent:           return self.parent.lookup(name)
        raise TypeError_(f"unbound variable {name!r}")
    def extend(self, name, ty):
        return TypeEnv({name: ty}, self)

# --- The checker: same walk as evaluate(), computing types instead of values --
ARITH    = {"+", "-", "*", "/"}
COMPARE  = {"<", ">", "<=", ">=", "==", "!="}

def infer(e, tenv):
    if isinstance(e, Num):  return "Int"
    if isinstance(e, Bool): return "Bool"
    if isinstance(e, Var):  return tenv.lookup(e.name)

    if isinstance(e, BinOp):
        lt = infer(e.left, tenv)
        rt = infer(e.right, tenv)
        if e.op in ARITH:
            if lt != "Int": raise TypeError_(f"{e.op}: left operand is {lt}, expected Int")
            if rt != "Int": raise TypeError_(f"{e.op}: right operand is {rt}, expected Int")
            return "Int"                      # premises Int, Int  =>  conclusion Int
        if e.op in COMPARE:
            if lt != rt: raise TypeError_(f"{e.op}: cannot compare {lt} with {rt}")
            return "Bool"                     # premises tau, tau  =>  conclusion Bool
        raise TypeError_(f"unknown operator {e.op!r}")

    if isinstance(e, If):
        ct = infer(e.cond, tenv)
        if ct != "Bool":
            raise TypeError_(f"if: condition is {ct}, expected Bool")
        tt = infer(e.then_e, tenv)
        et = infer(e.else_e, tenv)
        if tt != et:
            raise TypeError_(f"if: branches disagree, then is {tt} but else is {et}")
        return tt                             # both branches tau  =>  conclusion tau

    if isinstance(e, Let):
        vt = infer(e.val, tenv)
        return infer(e.body, tenv.extend(e.name, vt))   # Gamma grows here

    raise TypeError_(f"unknown expression node {type(e).__name__}")

# --- The two programs from the Examples section ------------------------------
good = Let("x", Num(2),
       If(BinOp("<", Var("x"), Num(5)),
          BinOp("+", Var("x"), Num(1)),
          Num(0)))

bad  = Let("x", Num(2),
       If(Var("x"),                          # condition is Int, not Bool
          BinOp("+", Var("x"), Num(1)),
          Num(0)))

print("=== Checking, without running anything ===")
for label, prog in [("let x = 2 in if x < 5 then x+1 else 0", good),
                    ("let x = 2 in if x     then x+1 else 0", bad)]:
    try:
        print(f"  {label}\n      : {infer(prog, TypeEnv())}")
    except TypeError_ as err:
        print(f"  {label}\n      REJECTED: {err}")

print("\n=== More rejections, each naming its failing premise ===")
cases = [
    ("1 + true",                 BinOp("+", Num(1), Bool(True))),
    ("1 < true",                 BinOp("<", Num(1), Bool(True))),
    ("if true then 1 else false", If(Bool(True), Num(1), Bool(False))),
    ("y + 1  (y unbound)",       BinOp("+", Var("y"), Num(1))),
]
for label, prog in cases:
    try:
        print(f"  {label:26} : {infer(prog, TypeEnv())}")
    except TypeError_ as err:
        print(f"  {label:26} REJECTED: {err}")
```
@LIA.eval(`["main.py"]`, `none`, `python3 main.py`)

### Reading the Code

- `TypeEnv` is your interpreter's `Env` with one word changed: it maps names to *types*.  The `lookup`/`extend` pair is identical in shape.
- The `BinOp` branch is two judgments in one `if`: arithmetic demands `Int` on both sides and concludes `Int`; comparison demands only that the two sides *agree*, and concludes `Bool` regardless of what they were.
- The `If` branch enforces both premises of the conditional rule separately, so the error message can say which one failed.
- The `Let` branch is the only place `tenv` grows, and it grows by returning a *new* environment rather than mutating the old one, exactly as lexical scope requires.
- Nothing in this file evaluates anything.  There is no `+` applied to actual numbers anywhere in `infer`.

> **Watch out!**  A static checker reasons about types without ever computing a value, so it cannot catch errors that depend on runtime data: dividing by a variable that happens to be zero, or indexing an array at a position the user types in.  "Type safe" is not "bug free."  A well-typed program can still crash and can still be wrong; it just cannot fail in the specific structural ways the type system forbids.

> **Watch out!**  There is a second thing a static checker cannot see, and it is about *where* it looks rather than *when*.  A C or C++ compiler checks one **translation unit**, one source file with its headers pasted in, and then forgets everything.  It never checks a *program*.  Two files can hold flatly contradictory beliefs about the same global variable and every tool in the pipeline will wave them through, because the station that finally sees both files, the linker, matches names and has no types left to compare.  The Extension at the end of this deck compiles, links, and runs exactly that program.

### Critical Thinking Questions

5.  The comparison rule returns `Bool` no matter what its operands were, while the arithmetic rule returns `Int`.  Explain why comparison is the odd one out, in terms of what the *result* of the operation is.
6.  `If` requires both branches to have the same type.  Why can the checker not simply say "this expression is either `Int` or `Bool` depending on the condition"?  What would break downstream?
7.  Trace `infer` on the `bad` program by hand and name the exact recursive call at which it raises.  How many nodes did it visit before finding the error, and how many did it never visit?
8.  Compare the `Let` branch here with `Env.extend` in your interpreter.  What is genuinely different about them, beyond the word "type"?

### Try It Yourself

Add a `Not` node to the checker.  Its judgment is:

$$\frac{\Gamma \vdash e : \text{Bool}}{\Gamma \vdash \texttt{not } e : \text{Bool}}$$

```python
# Paste Model 2's checker above this line, or work from the skeleton below.
from dataclasses import dataclass
from typing import Any

@dataclass
class Bool: value: bool
@dataclass
class Num:  value: float
@dataclass
class Not:  expr: Any

class TypeError_(Exception): pass

def infer(e, tenv=None):
    if isinstance(e, Num):  return "Int"
    if isinstance(e, Bool): return "Bool"

    # TODO: add the Not case here.
    #   1. infer the type of e.expr
    #   2. if it is not "Bool", raise TypeError_ naming what you got
    #   3. otherwise return "Bool"

    raise TypeError_(f"unknown node {type(e).__name__}")

for label, prog in [("not true", Not(Bool(True))),
                    ("not 1",    Not(Num(1)))]:
    try:
        print(f"  {label:10} : {infer(prog)}")
    except TypeError_ as err:
        print(f"  {label:10} REJECTED: {err}")
```
@LIA.eval(`["main.py"]`, `none`, `python3 main.py`)

Expected output once your case is in place:

```
  not true   : Bool
  not 1      REJECTED: not: operand is Int, expected Bool
```

## Model 3: Inference With No Annotations Anywhere

Nothing in Model 2 required the programmer to *write* a type.  The checker deduced every one of them from the literals and the operators.  That is type inference, and this model makes the deduction visible by printing the type environment as it grows.

```python
from dataclasses import dataclass
from typing import Any

@dataclass
class Num:   value: float
@dataclass
class Bool:  value: bool
@dataclass
class Var:   name: str
@dataclass
class BinOp: op: str; left: Any; right: Any
@dataclass
class Let:   name: str; val: Any; body: Any

class TypeError_(Exception): pass

ARITH   = {"+", "-", "*", "/"}
COMPARE = {"<", ">", "<=", ">=", "==", "!="}

def infer(e, tenv):
    if isinstance(e, Num):  return "Int"
    if isinstance(e, Bool): return "Bool"
    if isinstance(e, Var):
        if e.name not in tenv: raise TypeError_(f"unbound variable {e.name!r}")
        return tenv[e.name]
    if isinstance(e, BinOp):
        lt, rt = infer(e.left, tenv), infer(e.right, tenv)
        if e.op in ARITH:
            if lt != "Int" or rt != "Int":
                raise TypeError_(f"{e.op}: needs Int and Int, got {lt} and {rt}")
            return "Int"
        if lt != rt:
            raise TypeError_(f"{e.op}: cannot compare {lt} with {rt}")
        return "Bool"
    raise TypeError_(f"unknown node {type(e).__name__}")

def check_sequence(bindings):
    """Infer a straight-line sequence of lets, printing Gamma as it grows."""
    tenv = {}
    for name, expr, shown in bindings:
        try:
            ty = infer(expr, tenv)
        except TypeError_ as err:
            print(f"  let {name} = {shown:16} REJECTED HERE: {err}")
            print(f"      Gamma at the point of failure: {tenv}")
            return
        tenv[name] = ty
        print(f"  let {name} = {shown:16} inferred {name} : {ty:4}   Gamma = {tenv}")

print("=== A program that checks ===")
check_sequence([
    ("a", Num(2),                                   "2"),
    ("b", BinOp("+", Var("a"), Num(3)),             "a + 3"),
    ("c", BinOp("<", Var("b"), Var("a")),           "b < a"),
])

print("\n=== The same program with one more line ===")
check_sequence([
    ("a", Num(2),                                   "2"),
    ("b", BinOp("+", Var("a"), Num(3)),             "a + 3"),
    ("c", BinOp("<", Var("b"), Var("a")),           "b < a"),
    ("d", BinOp("+", Var("c"), Num(1)),             "c + 1"),
])

print("\nNo annotation appears anywhere in this program.")
print("Every type above was deduced from literals and operators alone.")
```
@LIA.eval(`["main.py"]`, `none`, `python3 main.py`)

### Reading the Code

`check_sequence` is a deliberately flattened `Let` chain: instead of nesting, it threads one growing dictionary through the sequence so you can watch $\Gamma$ fill up line by line.  When inference fails, it prints $\Gamma$ *at the moment of failure*, which is the information a real compiler's error message is trying to summarize.

### Critical Thinking Questions

9.  In the second run, the checker rejects line `d`.  But the *mistake* a programmer made is arguably on line `c`, where they wrote a comparison when they meant arithmetic.  How far is the reported error from the actual mistake, and what does that predict about type-inference error messages in real compilers?
10.  Model 3 stores $\Gamma$ in a plain dictionary that it mutates, while Model 2 used a parent-chained `TypeEnv`.  For which language feature does the dictionary version break, and why?
11.  Add `let e = if c then a else b` to the first sequence.  What type is inferred, and what does the `If` rule demand of `a` and `b` for it to succeed?

### Try It Yourself

Extend the inference demo with a string type.  Add a `Str` node that infers as `"Str"`, then decide: should `+` on two `Str` values be licensed as concatenation?

```python
# Start from Model 3's infer(), then:
#   1. add a Str dataclass and its inference case
#   2. decide whether "+" accepts (Str, Str) and implement your decision
#   3. run the two probes below and check the results against your intent

# TODO: your extended infer() here.

# Probe A:  "ab" + "cd"     -- should this be Str, or a type error?
# Probe B:  "ab" + 1        -- this must be a type error either way.

print('Decide and defend: does your language license "+" on two strings?')
print('If yes, you have overloaded "+". Write the second judgment for it.')
```
@LIA.eval(`["main.py"]`, `none`, `python3 main.py`)

Expected output: whatever your design says, plus a rejection for Probe B.  Write the second typing judgment for overloaded `+` in your notes; you will need it for `SEMANTICS.md`.

---

# Part III: Gradual Typing

## 3.  Theory: Having It Both Ways, On Purpose

What if you want dynamic flexibility while prototyping and static guarantees where it matters?  **Gradual typing** (Siek and Taha, 2006) lets you annotate *some* of a program statically and leave the rest dynamic, inserting checks at the boundary between the two.

**mypy** adds gradual static typing to Python: unannotated code is given the dynamic type `Any` and passes silently, while annotated code is checked.  **TypeScript** does the same for JavaScript with `any`.

The key insight, and the thing worth carrying out of today: **gradual type systems are unsound by design.**  `Any` and `any` are escape hatches that turn checking *off*, so a program that type-checks cleanly can still fail at runtime.  That is a deliberate trade of the airtight guarantee for adoptability: you can add types to a million-line codebase one file at a time.  Contrast that with the checker you wrote in Model 2, which has no escape hatch and so is sound for the fragment it covers.

## Examples: The Same Bug, Two Languages

Here is the in-class compare.  The same mistake, written in both languages, with the checker's verdict beside it:

```python
# Python + mypy
def add(x: int, y: int) -> int:
    return x + y

add("a", 3)      # mypy: Argument 1 to "add" has incompatible type "str"
untyped = []     # inferred as Any
untyped.foo()    # mypy: no error -- Any silences the check
```

```typescript
// TypeScript
function add(x: number, y: number): number { return x + y; }

add("a", 3);          // tsc: error, string is not assignable to number
const x: any = [];    // 'any' opts out
x.foo();              // tsc: no error -- 'any' silences the check
```

Both checkers catch the first mistake and both are silent on the second.  The silence is not a bug in mypy or in `tsc`; it is the definition of gradual.

## Model 4: Build the Gradual Boundary Yourself

CPython ignores annotations, so this model reads them back with `typing.get_type_hints` and enforces them, and shows exactly where `Any` turns the enforcement off.

```python
from typing import Any, get_type_hints
import functools

def checked(fn):
    """Enforce a function's annotations at call time. Any means 'do not check'."""
    hints = get_type_hints(fn)
    @functools.wraps(fn)
    def wrapper(*args):
        names = fn.__code__.co_varnames[:fn.__code__.co_argcount]
        for name, value in zip(names, args):
            expected = hints.get(name, Any)
            if expected is Any:
                continue                      # the gradual escape hatch
            if not isinstance(value, expected):
                raise TypeError(
                    f"{fn.__name__}({name}=...): expected {expected.__name__}, "
                    f"got {type(value).__name__}")
        result = fn(*args)
        expected = hints.get("return", Any)
        if expected is not Any and not isinstance(result, expected):
            raise TypeError(f"{fn.__name__} returned {type(result).__name__}, "
                            f"expected {expected.__name__}")
        return result
    return wrapper

@checked
def add(x: int, y: int) -> int:
    return x + y

@checked
def sloppy(x: Any, y: Any) -> Any:            # fully dynamic: nothing is checked
    return x + y

@checked
def half_typed(x: int, y) -> Any:             # y unannotated => Any
    return x + y

print("=== Fully annotated: checked ===")
print(f"  add(2, 3)       = {add(2, 3)}")
try:
    add("a", 3)
except TypeError as e:
    print(f"  add('a', 3)     -> TypeError: {e}")

print("\n=== Fully dynamic: Any silences everything ===")
print(f"  sloppy('a', 'b') = {sloppy('a', 'b')!r}   (no complaint)")
try:
    sloppy("a", 3)
except TypeError as e:
    print(f"  sloppy('a', 3)  -> TypeError from PYTHON, not from the checker:")
    print(f"                     {e}")

print("\n=== Half typed: the boundary ===")
print(f"  half_typed(1, 2) = {half_typed(1, 2)}")
try:
    half_typed("a", "b")
except TypeError as e:
    print(f"  half_typed('a','b') -> TypeError: {e}")
print("  x was checked and rejected; y would have been let through.")

print("\nUnsoundness, stated plainly: sloppy() passes the checker and still")
print("blows up at runtime. That is gradual typing working as designed.")
```
@LIA.eval(`["main.py"]`, `none`, `python3 main.py`)

### Reading the Code

- `get_type_hints(fn)` is how CPython exposes annotations to *you* at runtime; the interpreter itself never consults them.
- The line `if expected is Any: continue` is the entire gradual escape hatch, in one statement.  Everything unsound about mypy and TypeScript follows from that `continue`.
- `half_typed` shows the boundary directly: one parameter is policed and the other is not, in the same call.
- The error from `sloppy("a", 3)` comes from Python's `+`, not from our checker.  Our checker approved the call.

### Critical Thinking Questions

12.  `sloppy` passes our checker and then crashes.  Restate that outcome using the word "sound," and explain what a sound checker would have done instead.
13.  TypeScript erases all types when it compiles to JavaScript, so the runtime has no type information at all.  What class of bug can therefore still occur after a clean `tsc` run, and how does that relate to `any`?
14.  Your interpreter is strong and dynamic.  Name one program that runs to completion under it but that the Model 2 checker rejects.  Is the checker's strictness a bug or a feature?  Defend your answer.

### Try It Yourself

Give `checked` a strict mode that refuses to let `Any` through, and see which of the three functions above stops working.

```python
# Modify checked() so it takes a flag:  checked(strict=True)
# In strict mode, an Any annotation (or a missing annotation) is itself an
# ERROR at decoration time, not a silent pass at call time.
#
# TODO: implement strict mode, then decorate all three functions with it and
#       report which ones are now rejected before they are ever called.

print("Which functions survive strict mode? Which do you actually want to ship?")
```
@LIA.eval(`["main.py"]`, `none`, `python3 main.py`)

Expected output: `add` survives; `sloppy` and `half_typed` are rejected at decoration time.  That is the difference between gradual and sound, made executable.

---

**In-class work stops here.**  Everything below is going-deeper material and homework.

---

# Extension: Enforcing Types at the Boundary with pydantic

Model 4 built a toy version of a real tool.  **pydantic** is the production one: it turns ordinary Python annotations into enforced contracts, validating data the instant an object is constructed and raising a precise, located error when a promise is broken.  It is the runtime strong-typing gatekeeper from Part I, packaged for real code, and it is the same discipline you are about to build into your interpreter.

```bash
pip install pydantic
```

## A First pydantic Model

A class that subclasses `BaseModel` declares its fields with ordinary type annotations; constructing an instance validates every field:

```python
from pydantic import BaseModel, ValidationError

class Token(BaseModel):
    kind: str
    lexeme: str
    line: int

# Valid: types match
t = Token(kind="NUMBER", lexeme="42", line=7)
print(t)                        # kind='NUMBER' lexeme='42' line=7

# Declared coercion: the string "7" is converted to int 7
t2 = Token(kind="NUMBER", lexeme="42", line="7")
print(type(t2.line), t2.line)   # <class 'int'> 7

# Invalid: "seven" cannot become an int -> ValidationError
try:
    Token(kind="NUMBER", lexeme="42", line="seven")
except ValidationError as e:
    print(e)                    # line: Input should be a valid integer ...
```

Both axes from Part I show up here, made concrete.  pydantic is **strong** (it refuses `"seven"` as an `int`) and yet it performs **deliberate, declared coercion** (`"7"` becomes `7`): coercion you opted into by choosing pydantic, not the silent coercion of a weakly typed language.  Turn it off entirely with strict mode (`model_config = ConfigDict(strict=True)`) and `"7"` is rejected too.

## Validators: When a Type Encodes an Invariant

A validator lets a field mean more than `int`: it can mean *a line number that must be positive*, or *an operator that must be one the language actually has*:

```python
from pydantic import BaseModel, field_validator, ValidationError

class AstNode(BaseModel):
    op: str
    line: int

    @field_validator("op")
    @classmethod
    def op_must_be_known(cls, v: str) -> str:
        allowed = {"+", "-", "*", "/"}
        if v not in allowed:
            raise ValueError(f"unknown operator {v!r}; expected one of {sorted(allowed)}")
        return v

    @field_validator("line")
    @classmethod
    def line_is_positive(cls, v: int) -> int:
        if v < 1:
            raise ValueError("line numbers start at 1")
        return v

for bad in (dict(op="%", line=3), dict(op="+", line=0)):
    try:
        AstNode(**bad)
    except ValidationError as e:
        print(e)
```

This is the same check-before-you-compute gatekeeper as Model 2, applied at the *boundary* where untrusted data (a config file, a JSON request, a serialized AST, a parsed token stream) enters your program.

> **Watch out!**  Three different things look alike and guarantee different amounts.  Plain type *hints* are never enforced by CPython: `add("a", "b")` runs until `+` fails.  `@dataclass` gives you the same annotations and also does not validate them.  A static checker like `mypy` checks before running and does nothing at runtime.  pydantic enforces the annotation *when the data arrives*.  Know which of the three you actually have.

# Extension: Structural vs. Nominal Typing

Two types can be "the same" for two different reasons.  **Nominal** typing says two types match when they have the same *name* or an explicit inheritance relationship: Java's `class Circle implements Drawable` must say so out loud.  **Structural** typing says they match when they have the same *shape*: if it has a `draw()` method, it is `Drawable`, whether or not anyone declared it.

```java
// Java: nominal. Circle is Drawable only because it SAYS it is.
interface Drawable { void draw(); }
class Circle implements Drawable { public void draw() { } }
class Blob   { public void draw() { } }   // NOT Drawable, despite having draw()
```

```typescript
// TypeScript: structural. Shape alone decides.
interface Drawable { draw(): void; }
const blob = { draw() {} };
const d: Drawable = blob;     // fine: blob has the right shape
```

Python's `Protocol` makes structural typing explicit and checkable:

```python
from typing import Protocol, runtime_checkable

@runtime_checkable
class Drawable(Protocol):
    def draw(self) -> None: ...

class Circle:
    def draw(self) -> None: print("  circle")

class Blob:
    def draw(self) -> None: print("  blob")

class Rock:
    def roll(self) -> None: print("  rock")

# Neither Circle nor Blob inherits from Drawable or from any shared base.
# They satisfy the protocol purely by having the right method.
for obj in (Circle(), Blob(), Rock()):
    name = type(obj).__name__
    print(f"{name:8} is Drawable? {isinstance(obj, Drawable)}")
```
@LIA.eval(`["main.py"]`, `none`, `python3 main.py`)

Which discipline should *your* language use?  Nominal typing gives you intent (`implements Drawable` is a promise the author made deliberately) and better error messages.  Structural typing gives you flexibility and works with types you did not write.  Say which you chose in `TYPES.md`, and why.

# Extension: Type Erasure

A third question, independent of the first two: do types survive to runtime at all?

- **Java erases generics at compile time.**  `List<String>` and `List<Integer>` are the same class at runtime; the type argument is checked and then thrown away.
- **C++ monomorphizes.**  `vector<int>` and `vector<string>` become genuinely different generated code, so nothing is erased; the binary is larger and the types are real.
- **Python keeps annotations as data but never acts on them.**  `get_type_hints` can read them back, as Model 4 did, but the interpreter never consults them.

```python
from typing import get_type_hints

def total(items: list[int]) -> int:
    return sum(items)

print("annotations, read back at runtime:")
print(f"  {get_type_hints(total)}")

print("\nnow call it with the wrong thing anyway:")
try:
    print(total(["a", "b"]))
except TypeError as e:
    print(f"  TypeError: {e}")
    print("  Note where that came from: sum(), not the annotation.")
    print("  The annotation was visible the whole time and stopped nothing.")
```
@LIA.eval(`["main.py"]`, `none`, `python3 main.py`)

Erasure is why a clean `tsc` run cannot protect you at runtime, which is CTQ 13's answer from a different angle.

---

# Extension: When Static Typing Stops at the File Boundary

Everything in Part II assumed the checker can see the program.  For C and C++ that assumption is false, and the gap is wide enough to drive a real bug through.

## Two Files That Disagree

Here is a complete program.  Read both files and predict what it prints.

```c
/* physics.c */
float gravity = 9.81f;
```

```c
/* report.c */
#include <stdio.h>

extern int gravity;

int main(void) {
    printf("gravity as int: %d\n", gravity);
    return 0;
}
```

Compile and link it the ordinary way:

```bash
gcc -c physics.c -o physics.o     # no warning
gcc -c report.c  -o report.o      # no warning
gcc physics.o report.o -o demo    # no warning
./demo
```

It prints:

```
gravity as int: 1092416963
```

No diagnostic at any stage, not even with `-Wall -Wextra`.  A number that appears nowhere in the source is now in the output.

**Why each stage stayed quiet.**  `physics.c` is internally consistent: it declares a float and initializes it with a float.  `report.c` is internally consistent too: it declares an int and prints it with `%d`.  Neither compiler invocation ever sees the other file, so neither has anything to object to.  A **translation unit** is the compiler's entire universe.

Then the linker runs, and the linker is the first tool that sees both names together.  Run `nm` on the object files and you can see everything it has to work with:

```
physics.o:   0000000000000000 D gravity
report.o:                     U gravity
```

`D` means "defined, in the data section."  `U` means "used, undefined here."  The linker matches `U gravity` to `D gravity` and it is done.  `readelf` shows the full entry, and the full entry is the point:

```
   Num:    Value          Size Type    Bind   Vis      Ndx Name
     2: 0000000000000000     4 OBJECT  GLOBAL DEFAULT    2 gravity
```

A name.  A size.  A binding.  A section.  **There is no type field.**  Not because this linker is lazy, but because there is nowhere in the format to put one: types are a per-file, compile-time idea, and by link time they have been erased.

## Model: The Same Four Bytes, Read Two Ways

Predict the printed integer before you run this.  You will not get it right, and that is the lesson: nothing about `9.81` suggests it.

```python
import struct

# --- What physics.c actually put in memory -----------------------------------
raw = struct.pack("<f", 9.81)          # 'float gravity = 9.81f;'  -> 4 bytes

print("physics.c:  float gravity = 9.81f;")
print("   bytes in memory:  " + " ".join("%02x" % b for b in raw))
print()

# --- What report.c believes those same bytes are ----------------------------
print("report.c:   extern int gravity;   printf(\"%d\", gravity);")
print("   same bytes, read as int:  " + str(struct.unpack("<i", raw)[0]))
print()
print("Neither file is wrong on its own, and neither tool objected.")
print()

# --- Why no tool objected ----------------------------------------------------
# An ELF symbol entry is roughly this much, and no more:
physics_o = ("gravity", 4, "GLOBAL", "OBJECT")
report_o  = ("gravity", 4, "GLOBAL", "OBJECT")

print("What the linker compares:")
print("   physics.o defines:  name=" + physics_o[0] + "  size=" + str(physics_o[1])
      + "  bind=" + physics_o[2] + "  kind=" + physics_o[3])
print("   report.o  uses:     name=" + report_o[0] + "  size=" + str(report_o[1])
      + "  bind=" + report_o[2] + "  kind=" + report_o[3])
print("   names match, sizes match  ->  linked, no diagnostic")
print()
print("There is no field in that entry for 'float' or 'int'. There is nowhere")
print("to put one. The compiler knew, and threw it away.")
print()

# --- The milder variant, where a size check WOULD have a chance --------------
wide = struct.pack("<d", 9.81)         # 'double gravity = 9.81;'  -> 8 bytes
print("Contrast, if physics.c had used a double instead:")
print("   double is " + str(len(wide)) + " bytes, int is " + str(len(struct.pack("<i", 0))) + " bytes")
print("   low 4 bytes read as int:  " + str(struct.unpack("<i", wide[:4])[0]))
print("   a size-comparing linker could at least warn here -- 8 != 4.")
print("   float vs int gives it nothing to notice: 4 == 4.")
```
@LIA.eval(`["main.py"]`, `none`, `python3 main.py`)

Expected output: the int is `1092416963`, which is exactly what the real C program prints.

### Reading the Code

- `struct.pack("<f", 9.81)` produces the four bytes `c3 f5 1c 41`, the IEEE-754 single-precision encoding of 9.81 on a little-endian machine.  `struct.unpack("<i", ...)` re-reads those same bytes as a two's-complement integer.  Nothing is converted; the bytes never move.  Only the *interpretation* differs, and the interpretation is exactly what the type declaration supplies.
- The tuples standing in for symbol-table entries are not a simplification for teaching.  That really is the shape of the information, which is why the mismatch is undetectable rather than merely undetected.
- The `float`/`int` pairing is chosen deliberately.  With `double`/`int` the sizes differ, 8 against 4, and a linker that compares sizes has something to complain about.  With `float`/`int` both are 4 bytes and the last possible check evaporates.

### Critical Thinking Questions

8.  Trace the *lie* through the pipeline and name, at each of the three stations from *Table-Driven and LR Parsing*, what that station knew and what it had already forgotten.  At which station did the last piece of information that could have caught this disappear?
9.  Part I placed C in the **static, weak** quadrant.  Does this bug belong to the *static* axis or the *weak* axis?  Defend your answer, then argue the opposite one; the disagreement is the useful part.
10.  The `# Extension: Type Erasure` section above showed Java erasing generic type arguments before runtime.  This section shows C erasing *all* types before linking.  State what the two erasures have in common in one sentence, and then state the difference in what each one costs you.
11.  C's actual answer is a shared header: put `extern float gravity;` in `gravity.h` and `#include` it from both files.  Explain precisely why that works, then explain precisely why it is a *convention* and not a *guarantee*.  What stops `report.c` from simply not including it?
12.  Suppose the linker did carry a type on every symbol.  Name two costs of that design.  (Think about what has to agree between two files compiled by different compilers, or in different languages, years apart.)
13.  Your project language will eventually have more than one source file.  Write the rule for `TYPES.md` in two sentences: when a name defined in one module is used in another, what checks that the two agree, and at what moment?

## What Other Languages Do About It

The bug is not inevitable.  It is the price of a specific design choice, and other languages paid a different price:

| Language | What crosses the module boundary | Can the mismatch happen? |
|---|---|---|
| **C** | A name, a size, a binding | Yes, silently, as above |
| **C++** | Mangled names for *functions*, plain names for *variables* | Yes, for variables |
| **Ada, Modula-2** | A compiled interface the compiler must check against | No, rejected at compile time |
| **Java, Go, Rust** | A module or class file carrying full type information | No, rejected at compile time |

C++ is the instructive middle case.  Compile a file with two overloads of `add` and one global, then look at the symbols:

```
0000000000000018 T _Z3adddd     <- double add(double, double)
0000000000000000 T _Z3addii     <- int    add(int, int)
0000000000000000 D gravity      <- int gravity;   ... just 'gravity'
```

Function names are **mangled**: `_Z3addii` encodes "add, taking int and int," so two files that disagree about a function's signature ask for different symbols and get an honest undefined-reference error.  That is type checking smuggled into the linker through the one field it does have, the name.  But variables are not mangled: `gravity` is `gravity`.  So C++ closes the door for functions and leaves it open for exactly the case this section is about.

> **Watch out!**  The lesson here is not "C is bad."  It is that a type system's guarantee has a **boundary**, and you should always know where the boundary is.  In C the boundary is the file.  In Java it is the program.  In Python with mypy it is "the annotated parts."  When someone tells you a language is type safe, the useful follow-up question is: *safe across what?*

---

# Check Your Understanding

`physics.c` defines `float gravity = 9.81f;` and `report.c` declares `extern int gravity;`.  The program compiles and links with no diagnostic and prints a nonsense number.  Why did static typing not catch it?

[(X)] The compiler checks one translation unit at a time, and the linker that sees both files matches symbols by name, with no type information left
[( )] `float` and `int` are compatible types in C, so there is nothing to catch
[( )] The error is data-dependent, so only a runtime check could find it
[( )] C is weakly typed, so it coerced the float to an int

---

Python raises `TypeError` on `"5" - 1`, but only when that line actually executes.  Where does Python sit on the two axes?

[( )] Static and strong
[(X)] Dynamic and strong
[( )] Static and weak
[( )] Dynamic and weak

---

C computes `'a' + 1` as `98` without complaint, and does so at compile time.  Where does that put C?

[( )] Static and strong
[( )] Dynamic and strong
[(X)] Static and weak
[( )] Dynamic and weak

---

In Model 2, the `If` rule requires both branches to have the same type.  What is the reason?

[(X)] The checker must name one type for the whole `if` expression without knowing which branch will run
[( )] Otherwise the interpreter could not evaluate the condition
[( )] It is a limitation of Python's `isinstance` that a real checker would not have
[( )] Because the branches might have side effects

---

Which of these would the Model 2 checker catch?

[(X)] `1 + true`, adding an integer to a boolean
[( )] Dividing by a variable that happens to be zero at runtime
[( )] Reading past the end of a list when the index comes from user input
[( )] A loop that never terminates

---

`untyped: Any` followed by `untyped.foo()` passes mypy cleanly and then crashes. What is the name for that property?

[(X)] Unsoundness: the checker approves a program that fails at runtime, by design
[( )] Incompleteness: the checker rejects a program that would have run fine
[( )] Type erasure: the annotations are discarded before running
[( )] Coercion: the value is silently converted

---

# Exercises

**Exercise 1. Interpreter integration.**  Wire the Model 2 checker into your interpreter as a pass that runs *before* evaluation.  Add booleans and strings as value types (with literals in your lexer and parser if they are absent) and demonstrate three programs: one that checks and runs, one that the checker rejects with a helpful positioned message, and one that the checker accepts but that still fails at runtime.  That third program is your evidence for the "type safe is not bug free" claim.

**Exercise 2. Coercion lab.**  Implement a `--weak` flag that turns two of your checker's refusals into coercions.  Write one program whose output silently *changes* between modes, and a paragraph on which mode your team ships and why, citing the criteria from *Evaluating Languages*.

**Exercise 3. Inference on paper.**  For

```
let a = 2;
let b = a + 3;
let c = b < a;
let d = c + 1;
```

infer every variable's type top to bottom and identify the first line a static checker rejects.  Note how far the *error* is from the *mistake*, and what that implies about the error messages real inference engines can produce.

**Exercise 4. Type archaeology.**  Find one real bug report or postmortem caused by implicit coercion (JavaScript and PHP folklore abounds).  Summarize the failure in two sentences and name the language rule that would have prevented it.

**Exercise 5. Runtime type tags.**  Change your interpreter's value representation so every value is a `(type_tag, raw_value)` pair:

```python
("num",  3.0)
("str",  "hi")
("bool", True)
```

Update your `BinOp` case to check the tag before operating, and show that your error messages now name the tag rather than a Python type.

**Exercise 6. Extend the checker.**  Add function types to Model 2.  A `Lam(param, param_type, body)` has type `param_type -> body_type`, and `App(fn, arg)` requires the argument's type to match the function's parameter type.  What new information does the type environment now have to carry?

---

# Reflection

In your notebook: strong typing refuses to guess what you meant; weak typing guesses.  Describe one tool or person in your life whose refusal to guess you have come to value, and what it cost you to appreciate them.

Then: in Model 3, the checker deduced `c : Bool` from context alone, with no annotation anywhere.  When you first saw that, did it feel like magic?  After writing the rules out as judgments and then as `if` branches, what makes it feel mechanical instead?

---

# Further Reading

- Douglas Thain.  *Introduction to Compilers and Language Design*, Chapter 7.
- Robert Nystrom.  *Crafting Interpreters*, "Evaluating Expressions," on runtime type checks.
- Gary Bernhardt.  "Wat" (2012): four minutes of coercion comedy with a serious lesson underneath.
- Benjamin Pierce.  *Types and Programming Languages*, the standard reference; Chapters 8 through 11 cover exactly the judgments in Part II.
- Siek and Taha.  "Gradual Typing for Functional Languages" (2006), the paper that named Part III.
- The [Hindley-Milner type inference tutorial](https://www.billmongan.com/Ursinus-CS374-Fall2026/Tutorials/TypeInference) takes Model 3's inference to its conclusion: unification, the occurs check, and Algorithm W.  Read it if you take the type-checking direction on the Interpreter assignment.

---

Up next: the *Language Design Workshop* turns the whole term on a language of your own, and the Interpreter assignment's type-checking direction builds directly on Model 2.
