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

Every time you write `def add(x, y)` in Python, you are making an implicit promise: callers will pass values that support `+`.  A **type system** is the mechanism that turns informal promises like this into enforceable contracts, checked either before your program ever runs or the instant a broken promise is exercised at runtime.  Catching a broken promise in the compiler is like catching a typo before you mail a letter; catching it at runtime is like discovering the mistake only after the recipient tries to read it.  This activity will show you exactly how those two approaches differ, why the difference matters, and how to build the checking machinery into your own interpreter.

## Learning Goals

By the end of this activity, you will be able to:

- Define the two independent axes of type system design (static/dynamic and strong/weak) and place common languages on each axis
- Identify type errors in Python code and predict whether they are caught at parse time, compile time, or runtime
- Compare the trade-offs between static and dynamic typing with respect to early error detection and programming flexibility
- Explain type coercion and distinguish implicit coercion (weak typing) from explicit conversion (strong typing)
- Apply type-system concepts to specify the typing rules for a language being implemented in an interpreter project

> **Before You Begin:** This activity assumes you can:
> - Explain what a runtime error is and describe the difference between a crash that happens at parse time versus one that happens during execution
> - Read and write basic Python functions, including `try`/`except` blocks and `isinstance()` checks
> - Describe at a high level what your interpreter's evaluation (`eval`) function does with a binary operation node
>
> If any of these feel shaky, review them first.

Your interpreter (now equipped with the environments of *Environments and Variable Storage*) happily computes `5 / 0`'s error, but what should it do with `"hello" * true`?  A **type system** is a language's machinery for classifying values and rejecting senseless combinations, and the design axes (static or dynamic, strong or weak, declared or inferred) are among the most consequential your team will choose.  The path today: **what types are for $\rightarrow$ the two axes $\rightarrow$ inference $\rightarrow$ adding type errors to your interpreter**.

---

## Directions and Group Roles

Work in your POGIL team with your rotated roles (**Manager**, **Recorder**, **Presenter**, **Reflector**).  Please think each model and question through on your own first, then talk it over with your group.  The Recorder posts your answers to the Class Activity Questions discussion board, and the Presenter reports out wherever you disagreed or found another approach.  After class, please respond to the reflective prompt on your own in your notebook.

---

## Key Concepts

Here is a plain-English glossary of the terms this activity uses.  Please come back to this table whenever one of them starts to feel slippery.

| Term | Plain-English meaning | Why it matters |
|------|-----------------------|----------------|
| **Type** | A label on a value that says which operations are licensed for it | The whole activity is about who checks these licenses, and when |
| **Type error** | An operation applied to a value outside its license, like `"hi" * {}` | The failure every type system exists to catch, early or late |
| **Static typing** | Checking happens *before* the program runs | Catches errors on every path, including paths your tests never exercise |
| **Dynamic typing** | Checking happens at the instant each operation executes | Maximum flexibility; errors surface only when the bad line actually runs |
| **Strong typing** | The language refuses to silently mix incompatible types | Broken promises stop the program instead of flowing onward as wrong values |
| **Weak typing** | The language silently converts operands so the operation can proceed | The source of `"5" - 1 == 4` surprises; convenience purchased with silence |
| **Coercion** | An implicit, automatic type conversion the programmer never asked for | The defining behavior of weak typing; contrast with explicit conversion |
| **Type inference** | The checker deduces types from values and context, with no annotations written | Static safety without annotation ceremony: Rust, Haskell, TypeScript |
| **Type environment** | A mapping from variable names to their (inferred or declared) types | The checker's version of your interpreter's environment: names to types, not values |
| **Primitive type** | A type the language provides as an atom (numbers, strings, booleans) rather than one built from other types | Every language, including yours, starts from a chosen set of primitives; today's axes describe how a language polices the operations on them |

---

# Part I: The Axes

## 1.  Two Independent Questions

**A type classifies values and licenses operations**: numbers may be divided, strings concatenated, booleans tested.  A **type error** is an operation applied outside its license.  Languages differ on two independent axes:

When is checking done?  **Static** typing checks before execution (Java rejects `int x = "hi";` at compile time); **dynamic** typing checks during execution, at the moment the operation runs (Python raises `TypeError` when `"hi" * {}` is attempted).  Static catches errors earlier and on all paths, including paths your tests never run; dynamic permits more flexible code and faster iteration.  This is the binding-time framework again: the type's binding time.

**How strictly is checking enforced?**  **Strong** typing refuses undefined mixtures or requires explicit conversion; **weak** typing silently **coerces** (converts) operands to make the operation proceed.  JavaScript famously computes `"5" - 1` as `4` and `"5" + 1` as `"51"`; Python, dynamically but *strongly* typed, raises on `"5" - 1`.  The axes are independent: Python is dynamic and strong; C is static and (in places) weak.

**Inference splits the difference on ceremony.**  Statically typed languages with **type inference** (Rust, Haskell, modern Java's `var`, TypeScript) deduce types you do not write: `let n = 5` is statically known to be an integer because 5 is.  Inference buys static safety without annotation cost, at the price of error messages that can point far from the cause.

---

**Intuition for Model 1:** The two axes (static/dynamic and strong/weak) are completely independent, so a language can land in any of the four quadrants.  Think of Python refusing `"5" - 1` (strong, because no silent conversion) yet only discovering that refusal when the line actually executes (dynamic).  In contrast, a language like Haskell refuses that expression at compile time without you ever running the program (static and strong).  This model asks you to place real behaviors on those axes before you look at any code.

## Model 1: Place the Languages

| Language behavior | Static/Dynamic? | Strong/Weak? |
|-------------------|-----------------|--------------|
| Rejects `x = "hi"` at compile time when x was declared int | ? | ? |
| Raises TypeError at runtime on `"5" - 1` | ? | ? |
| Computes `"5" - 1 == 4` without complaint | ? | ? |
| Compiles `let n = 5; n = "hi"` to an error without any annotations | ? | ? |

> **Watch out!**  Static/dynamic and strong/weak are two *separate* axes; do not conflate them.  "Static" refers to *when* checking happens (before vs. during execution).  "Strong" refers to *whether* the language permits silent coercion between incompatible types.  Python is **dynamic** (checks at runtime) AND **strong** (refuses coercion).  C is **static** (compile-time) but can be **weak** in places (e.g., implicitly converting pointer types).  Any combination of the four quadrants is possible.

> **Watch out!**  Python is *not* "untyped."  Every Python value has a definite type: `type(42)` is `<class 'int'>`, `type("hi")` is `<class 'str'>`.  The language simply chooses to check type compatibility at runtime rather than before execution.  Calling Python "untyped" is a common and consequential misconception: it conflates the absence of *declared* types with the absence of types altogether.

**Verify Python's dynamic strong typing:**

```python
# Python: dynamic (checks at runtime) + strong (refuses coercion)
print("=== Python Type Behavior ===")

# Strong: refuses silent coercion
try:
    result = "5" - 1   # JavaScript would give 4; Python refuses
except TypeError as e:
    print(f"'5' - 1 -> TypeError: {e}")

# String + number: also refused
try:
    result = "hello" + 42
except TypeError as e:
    print(f"'hello' + 42 -> TypeError: {e}")

# Dynamic: no compile-time check; type errors only happen at runtime
def risky(x):
    return x * 2   # works for int, float, str - but might fail

print(f"risky(5) = {risky(5)}")
print(f"risky('ab') = {risky('ab')}")  # string * 2 = "abab" - licensed!

try:
    print(risky([1, 2]) + 1)   # list * 2 works, but list + 1 fails at runtime
except TypeError as e:
    print(f"risky([1,2]) + 1 -> TypeError: {e}")

# The "hidden path" problem:
def categorize(x):
    if x > 100:
        return x / 2     # if x is a string, crash - but test might not reach here
    return x + 1

# Tests passing doesn't mean type-safe:
print(categorize(50))     # fine
print(categorize(200))    # fine
# categorize("hello")     # would crash - static typing would catch this
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

### Critical Thinking Questions

1.  Fill the grid and name a plausible language for each row.
2.  Row 3's behavior (coercion) maximizes which criterion from the *Evaluating Languages* activity, and damages which?  Cite the `"5" + 1` versus `"5" - 1` asymmetry in JavaScript as evidence.
3.  Row 4 shows inference: the checker deduced `n`'s type from `5`.  Sketch how it would propagate types through `let m = n + 1; let s = m + "!"` and where it would report the error.  Whose line gets blamed?
4.  Testing exercises only the paths you run; static checking covers all paths.  Construct a two-branch program where dynamic typing hides a type error from a test suite that achieves 100% line coverage on the happy branch; then explain why coverage did not save you.

---

# Interlude: Enforcing Types at Runtime with pydantic

Python's type hints (`def add(x: int, y: int) -> int:`) are, by default, *documentation the interpreter ignores*; nothing checks them when the program runs.  **pydantic** is a widely used library that turns those same annotations into **enforced contracts**: it validates data against your declared types the instant an object is constructed, and raises a precise, located error the moment a promise is broken.  It is the runtime, strong-typing gatekeeper from Part I, packaged for real Python code, and it is the same discipline you are about to build into your interpreter.

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

Both behaviors from the *Type Systems* axes show up here, made concrete. pydantic is **strong** (it refuses `"seven"` as an `int`) yet it performs **deliberate, declared coercion** (`"7"` -> `7`): coercion you opted into by choosing pydantic, not the silent coercion of a weakly typed language.  Turn coercion off entirely with strict mode (`model_config = ConfigDict(strict=True)`), and `"7"` is rejected too.

## Validators: When a "Type" Encodes an Invariant

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

This is the same **check-before-you-compute** gatekeeper you will write into your interpreter's evaluator in the next section; pydantic just applies it at the *boundary* where untrusted data (a config file, a JSON request, a serialized AST, a parsed token stream) enters your program, giving you specific, located errors for free.

> **Watch out!**  Plain type *hints* (`x: int`) are never enforced by CPython at runtime: `add("a", "b")` runs until `+` fails. `@dataclass` gives you the same annotations but also does **not** validate them.  A static checker like `mypy` checks before running and does nothing at runtime. pydantic is the tool that enforces the annotation *when the data arrives*.  Know which of these three guarantees you actually have.

---


> **The interpreter half of this topic is in the lab.**  Building the runtime type checker, tracing it on a compound expression, doing type inference by hand, and the type-error postmortem all live in the [Type Checker Starter lab](https://www.billmongan.com/Ursinus-CS374/Assignments/TypeCheckerLab); that is the assignment this session sets up.

# Part III: Synthesis and Practice

---
**In-class work stops here.**  Everything below is homework and going-deeper material: attempt the exercises before the related assignment.

## 3.  Exercises

1.  *Interpreter integration.*  Wire `eval_binop` into your interpreter's `BinOp` case, add booleans and strings as value types (with literals in your lexer and parser if absent), and demonstrate three programs: one that runs, one that raises your TypeError with a helpful message, and one comparison program.
2.  *Coercion lab.*  Implement a `--weak` configuration flag that turns two refusals into coercions.  Write one program whose output silently changes between modes, and one paragraph on which mode your team ships and why, citing the evaluation criteria.
3.  *Inference on paper.*  For the program `let a = 2; let b = a + 3; let c = b < a; let d = c + 1;`, infer every variable's type top to bottom and identify the first line a static checker would reject.  Note how far the *error* is from the *mistake*, and what that implies about inference error messages.
4.  *Type archaeology.*  Find one real bug report or postmortem caused by implicit coercion (JavaScript and PHP folklore abounds).  Summarize the failure in two sentences and the language rule that would have prevented it.
5.  *Runtime type tag.*  Modify your interpreter's value representation so that every value is a `(type_tag, raw_value)` pair: `("num", 3.0)`, `("str", "hi")`, `("bool", True)`.  Update `eval_binop` to check the tag before operating.  Show that error messages now include the tag.

---

## Reflection Prompt

In your notebook: strong typing refuses to guess what you meant; weak typing guesses.  Describe one tool or person in your life whose refusals to guess you have come to value, and what it cost to appreciate them.  Then: the type inference mini-implementation shows that a checker can deduce `c: bool` from context alone, no annotation needed.  Does this feel like magic to you now?  After this activity, what makes it feel mechanical rather than magical?

---

## 4.  Further Reading

- Douglas Thain.  *Introduction to Compilers and Language Design*, Chapter 7.
- Robert Nystrom.  *Crafting Interpreters*, "Evaluating Expressions" (runtime type checks).
- Gary Bernhardt.  "Wat" (talk, 2012, online): four minutes of coercion comedy with a serious lesson.
- Benjamin Pierce.  *Types and Programming Languages* (TAPL), the gold standard reference.

---

## Going Deeper (Optional Pointers)

The core lesson above stands on its own.  The deep-dive appendices that used to follow it now live on the Tutorials shelf:

> **Going further:** the material that used to live here (Robinson unification, substitutions and the occurs check, Algorithm W, Hindley-Milner type inference, and let-polymorphism) is covered in depth in the dedicated tutorial: [Implementing Hindley-Milner Type Inference](https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374-Fall2026/gh-pages/_pages/Tutorials/tutorial-type-inference.md).  Explore it when your project or curiosity calls for it.

> **Going further:** the material that used to live here (the static/dynamic and strong/weak axes in depth, Python annotations and `mypy`, type erasure, product and sum types, structural vs. nominal typing, and gradual typing with the consistency relation and blame) is covered in depth in the dedicated guide: [Typing Disciplines: Strong vs. Weak, Static vs. Dynamic, and Gradual Typing](https://www.billmongan.com/Ursinus-CS374/Tutorials/TypingDisciplines).  Explore it when your project or curiosity calls for it.

---

Up next: the *Control Flow and Statement Semantics* activity pins down which code runs, and the Interpreter assignment's type-checking direction builds on today's axes.
