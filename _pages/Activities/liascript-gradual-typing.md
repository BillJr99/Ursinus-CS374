<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374-Fall2026/gh-pages/_pages/Activities/liascript-gradual-typing.md

import: https://raw.githubusercontent.com/liascript/CodeRunner/master/README.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

# Gradual Typing: Between Static and Dynamic

Static typing catches errors at compile time but demands up-front annotations for every value; dynamic typing runs without annotations but lets bugs hide until runtime. Gradual typing is the pragmatic middle ground — like a building code that mandates inspections only in the load-bearing walls while leaving interior decoration to the owner's discretion. Languages such as TypeScript, mypy-annotated Python, and Typed Racket all make this bet, and the theory behind it is surprisingly deep.

## Learning Goals

By the end of this activity, you will be able to:

- Define gradual typing and explain how the unknown type `?` bridges statically-typed and dynamically-typed code
- Identify the consistency relation between types and distinguish it from type equality and subtyping
- Implement a bidirectional type checker that accepts gradually-typed programs and inserts runtime casts at typed/untyped boundaries
- Analyze blame assignment at static/dynamic boundaries and determine which component (caller or callee) is responsible for a cast failure
- Evaluate the correctness guarantees a gradually-typed language can and cannot provide compared to fully static or fully dynamic typing

> **Before You Begin:** This activity assumes you can:
> - Explain the difference between static and dynamic typing with a concrete example in at least one language
> - Read and write basic Python type annotations (`int`, `str`, `List[int]`, `Optional[str]`)
> - Trace through a simple recursive Python function and predict its output
>
> If any of these feel shaky, review them first.

Real-world languages rarely commit fully to either end of the static/dynamic spectrum. TypeScript adds optional types to JavaScript. mypy adds optional types to Python. Dart, Hack (PHP), and Typed Racket all make the same bet: let programmers annotate where they care about correctness, leave the rest unchecked, and insert runtime guards at the boundaries. The theory behind this approach — **gradual typing** — was formalized by Siek and Taha in 2006. It is not simply "some types, sometimes." It is a precise design with a formal consistency relation, a blame calculus for tracking contract violations, and deep consequences for what your language can and cannot guarantee.

Today you will move from pure dynamic typing (Model 1) through optional annotations (Model 2), implement a mini bi-directional type checker with a gradual consistency relation (Model 3), track blame at typed/untyped boundaries (Model 4), and wire a runtime type-checking interpreter that enforces annotated boundaries while leaving unannotated code free (Model 5).

---

## Directions and Group Roles

Work in your POGIL team with rotated roles (**Manager**, **Recorder**, **Presenter**, **Reflector**). The Recorder maintains a running glossary: every bolded term introduced is a potential exam definition. The Presenter should be prepared to walk another group through the `consistent` relation in Model 3 and explain why it is not transitive. After class, complete the reflection prompt individually in your course journal.

Each model builds on the last. Do not skip ahead.

---

## Model 1: Python's Dynamic Types in Action

Before you can appreciate the value of types, you need to feel the pain of their absence. This model shows Python at its most flexible — a single function serving wildly different argument types — and at its most hazardous, where the error only surfaces deep at runtime. Keep track of when you first know something has gone wrong versus when the program tells you.

Python is dynamically typed: there are no type annotations required, and the interpreter never checks types until it actually tries an operation. The same function can receive an `int`, a `str`, or a `list` — and it will cheerfully proceed with whichever it gets. This flexibility is genuinely useful. It is also the source of some of the hardest-to-find bugs in large codebases.

The model below shows how a single function can be called correctly and incorrectly, with the error appearing only at the moment the operation is attempted — which may be thousands of calls deep in production.

```python  liascript
def double(x):
    return x + x

print(double(5))        # 10  -- works
print(double("ha"))     # "haha" -- also works!
print(double([1,2]))    # [1,2,1,2] -- unexpected but valid

# The hazard: runtime surprises
def add_one(x):
    return x + 1

try:
    print(add_one("hello"))   # TypeError at runtime
except TypeError as e:
    print(f"Runtime error: {e}")

print("Program continues after the try/except")
# In a large codebase, this error might happen deep in production
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

> **Watch out!** `double("ha")` succeeds because `+` on strings means concatenation, not addition. Python does not check intent — it checks capability. The function works for strings, lists, and integers for completely different reasons. This is duck typing in action, and it can make unit tests deceptively quiet.

### Critical Thinking Questions

**CTQ 1.** Which call to `double` do you think the programmer intended when they wrote the function? What clue in the function body suggests one interpretation over another?

[[___ your answer here ___]]

**CTQ 2.** The error in `add_one("hello")` only appears at runtime. Imagine this call is buried inside a library function invoked after reading a configuration file at startup. At what point does the programmer learn about the error? In a 100,000-line codebase, what makes this harder to debug than a compile-time error?

[[___ your answer here ___]]

**CTQ 3.** Python chose to allow `double("ha")` even though the programmer almost certainly wrote `double` for numbers. Name one **language design advantage** of this choice (think: code reuse, expressiveness) and one **language design disadvantage** (think: documentation, correctness guarantees).

[[___ your answer here ___]]

**CTQ 4.** The `try/except` block catches the `TypeError` and lets the program continue. Is this always the right thing to do? Describe a situation where catching and continuing is appropriate and a situation where it would silently corrupt a computation.

[[___ your answer here ___]]

---

## Model 2: Type Annotations — Python's Optional Types (mypy-style)

Type annotations in Python are like sticky notes on a whiteboard: they communicate intent clearly to anyone reading the code, but the whiteboard does not enforce them — a different tool (mypy, pyright) must play that enforcement role. This model introduces the annotation vocabulary and forces you to notice the key surprise: Python runs annotated code with zero enforcement at runtime.

Python 3.5 introduced **type hints** via PEP 484. They are syntactically legal in the language, stored in `__annotations__`, and available to external tools — but Python itself **ignores them completely at runtime**. The enforcement is delegated to an optional static checker such as `mypy`. This is the essential design choice of gradual typing: annotation is voluntary, checking is opt-in, and the runtime is unchanged.

The model below covers the core of Python's annotation vocabulary: base types, `Optional`, `Union`, `List`, and `Callable`. A type checker running over this code would flag exactly one line. The interpreter will not.

```python  liascript
from typing import List, Optional, Union, Callable

# Type annotations are hints -- Python ignores them at runtime
def add_one(x: int) -> int:
    return x + 1

def greet(name: str) -> str:
    return f"Hello, {name}!"

def first(lst: List[int]) -> Optional[int]:
    return lst[0] if lst else None

# Union type: accepts int or float
def square(x: Union[int, float]) -> float:
    return float(x * x)

# Higher-order: function that takes a function
def apply_twice(f: Callable[[int], int], x: int) -> int:
    return f(f(x))

# These are all CORRECT by the type signatures
print(add_one(5))
print(greet("Alice"))
print(first([1, 2, 3]))
print(square(3))
print(apply_twice(add_one, 10))

# Python does not enforce at runtime -- this still runs:
result = add_one("hello")  # a type checker would flag this
print(f"Sneaked through: {type(result)}")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

> **Watch out!** Python type annotations are **not** enforced at runtime. `add_one("hello")` runs without any error — Python simply ignores the `: int` annotation. Only an external tool like `mypy` would flag it. Students often expect annotations to act like Java's compile-time checks; they do not.

### Critical Thinking Questions

**CTQ 5.** `Optional[int]` is shorthand for `Union[int, None]` — the value might be `None`. What does `first([])` return, and is that consistent with its declared return type `Optional[int]`? What does `first([1, 2, 3])` return?

[[___ your answer here ___]]

**CTQ 6.** A type checker would flag `add_one("hello")` as an error, but Python still runs it and prints a result. What does this tell you about the **difference between static checking and runtime behavior** in a gradual type system?

[[___ your answer here ___]]

**CTQ 7.** Write the type signature for a function `map_list` that takes a list of `int` values and a function from `int` to `str`, and returns a list of `str` values. Express it using `List` and `Callable` from the `typing` module.

[[___ your answer here ___]]

**CTQ 8.** `Union[int, float]` in `square` says the function accepts either type. Without `Union`, you would need two separate functions or an `isinstance` check. What is the cost of using `Union` types liberally throughout a large codebase? (Hint: consider what the type checker can still guarantee when a function accepts many different types.)

[[___ your answer here ___]]

---

## Model 3: Building a Mini Type Checker with the Consistency Relation

Ordinary type equality is strict: `Int` equals `Int` and nothing else. The consistency relation relaxes this by introducing a wildcard type `Any` that is compatible with everything — like a universal adapter that fits any socket. The catch is that this wildcard breaks transitivity, and that gap between what the static checker accepts and what can succeed at runtime is exactly where runtime failures live.

At the heart of gradual typing is a relation called **consistency** (written `~`). It differs from ordinary type equality. Two types are consistent if they could be the same type at runtime: `Int ~ Int` (trivially), `Any ~ Int` (a dynamic value might be an `Int`), `Int ~ Any` (an `Int` is compatible with an unknown type). But `Int ~ Str` is **false** — no runtime value is both an integer and a string.

Formally:

```
t ~ t             (reflexivity)
Any ~ t           (Any is consistent with everything)
t ~ Any           (symmetric)
```

This relation is **not transitive**: `Int ~ Any` and `Any ~ Str` are both true, but `Int ~ Str` is false. That gap is precisely where runtime failures live — and where the blame calculus (Model 4) must assign responsibility.

The code below implements a bi-directional type checker for a small expression language using `consistent` as its compatibility predicate.

```python  liascript
from dataclasses import dataclass
from typing import Any, Dict

# Types in our mini language
INT  = "Int"
BOOL = "Bool"
STR  = "Str"
DYN  = "Any"  # the gradual type -- compatible with everything

def consistent(t1, t2):
    """Two types are consistent if one is Any or they are equal."""
    return t1 == DYN or t2 == DYN or t1 == t2

# AST nodes
@dataclass
class Lit:    value: Any; ty: str
@dataclass
class Var:    name: str
@dataclass
class Add:    left: Any; right: Any
@dataclass
class Eq:     left: Any; right: Any
@dataclass
class If:     cond: Any; then_: Any; else_: Any
@dataclass
class Ann:    expr: Any; ty: str   # explicit annotation: (expr : ty)

Env = Dict[str, str]  # variable -> type

def infer(expr, env: Env) -> str:
    if isinstance(expr, Lit):
        return expr.ty
    if isinstance(expr, Var):
        return env.get(expr.name, DYN)   # unannotated vars have type Any
    if isinstance(expr, Ann):
        t = infer(expr.expr, env)
        if not consistent(t, expr.ty):
            raise TypeError(f"Annotation mismatch: got {t}, expected {expr.ty}")
        return expr.ty
    if isinstance(expr, Add):
        t1, t2 = infer(expr.left, env), infer(expr.right, env)
        if not consistent(t1, INT) or not consistent(t2, INT):
            raise TypeError(f"Add requires Int, got {t1} + {t2}")
        return INT
    if isinstance(expr, Eq):
        t1, t2 = infer(expr.left, env), infer(expr.right, env)
        if not consistent(t1, t2):
            raise TypeError(f"Eq: {t1} vs {t2}")
        return BOOL
    if isinstance(expr, If):
        tc = infer(expr.cond, env)
        if not consistent(tc, BOOL):
            raise TypeError(f"If cond must be Bool, got {tc}")
        t1 = infer(expr.then_, env)
        t2 = infer(expr.else_, env)
        if consistent(t1, t2): return t1 if t1 != DYN else t2
        raise TypeError(f"If branches: {t1} vs {t2}")
    raise ValueError(f"Unknown: {expr}")

env = {"x": INT, "name": STR}

# Well-typed programs
print(infer(Add(Var("x"), Lit(1, INT)), env))   # Int
print(infer(Eq(Var("x"), Lit(0, INT)), env))    # Bool

# Gradual: untyped var y has type Any -- consistent with everything
print(infer(Add(Var("y"), Lit(1, INT)), env))   # Int (Any + Int is OK)

# Explicit annotation accepted
print(infer(Ann(Var("x"), INT), env))           # Int

# Type error caught statically
try:
    print(infer(Add(Var("name"), Lit(1, INT)), env))
except TypeError as e:
    print(f"Type error: {e}")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

> **Watch out!** Consistency is **not** the same as subtyping. `Any` is consistent with `Int`, but `Any` is not a subtype of `Int`. Subtyping is a containment relationship; consistency is a compatibility relationship. Conflating them leads to incorrect reasoning about what the type checker actually accepts.

### Critical Thinking Questions

**CTQ 9.** `DYN = "Any"` represents an unannotated binding. What does `consistent(DYN, INT)` return, and why? Trace through the `consistent` function body to verify your answer.

[[___ your answer here ___]]

**CTQ 10.** In gradual typing, `(Any + Int) -> Int`. This means the checker accepts adding an unannotated value to an `Int` and returns `Int`. Is this **sound**? (Hint: what if the `Any` value turns out to be a `Str` at runtime? Will the addition succeed?)

[[___ your answer here ___]]

**CTQ 11.** The consistency relation is **not transitive**: `consistent(INT, DYN)` is true and `consistent(DYN, STR)` is true, but `consistent(INT, STR)` is false. Draw a small diagram showing these three types and the consistency arrows between them. Why does allowing `DYN` to be consistent with everything create this non-transitivity?

[[___ your answer here ___]]

**CTQ 12.** What does the type checker **guarantee** when a program type-checks with **no** `DYN` types at all (i.e., every variable in `env` has a concrete type and no `Var` lookup returns `DYN`)? How does this guarantee weaken when some variables are unannotated?

[[___ your answer here ___]]

---

## Model 4: The Blame Calculus — Who Gets the Error?

When two parties sign a contract, a violation needs to be traced back to whoever broke it — not to some innocent bystander in the middle. The blame calculus does exactly this for type boundaries: it tags each boundary with a label so that when a runtime cast fails, the error message names the site that made the broken promise rather than the function body that happened to discover the problem.

When a gradually-typed program fails at runtime — because a `DYN` value turned out to be the wrong type at a typed boundary — the system needs to say **which boundary** was violated. This is the **blame calculus** (Wadler and Findler, 2009). Without blame, a runtime failure deep inside a library could be misleadingly attributed to the library itself, when the real problem is that the caller passed an untyped value that violated the library's contract.

The key insight: when typed code calls untyped code, or untyped code calls typed code, a **cast** is inserted at the boundary. If the cast fails, blame is assigned to the boundary label — the name of the site that promised a value of the wrong type.

Note that TypeScript and mypy **erase** types at runtime: TypeScript compiles to plain JavaScript, and mypy-annotated Python runs without any runtime checks. This means that in practice those systems do not enforce blame semantics at runtime. The blame calculus is more of a theoretical model for understanding responsibility than a feature you get for free in everyday toolchains.

```python  liascript
class Proxy:
    """A proxy wraps a dynamic value and tracks where it came from."""
    def __init__(self, value, expected_type, blame_label):
        self.value = value
        self.expected_type = expected_type
        self.blame_label = blame_label

    def force(self):
        """Check the type when the value is actually used."""
        type_map = {int: "Int", str: "Str", bool: "Bool"}
        actual = type_map.get(type(self.value), "Unknown")
        if actual != self.expected_type:
            raise RuntimeError(
                f"Blame: {self.blame_label} -- "
                f"expected {self.expected_type}, got {actual}"
            )
        return self.value

# Simulating: typed function f: Int -> Int called with dynamic argument
def f_typed(x_proxy):
    x = x_proxy.force()   # blame fires HERE if x is not Int
    return x + 1

# Good: calling f with an actual int wrapped as a proxy
good_arg = Proxy(42, "Int", "call-site:line-10")
print(f_typed(good_arg))  # 43

# Bad: calling f with a string (common when dynamic code calls typed code)
bad_arg = Proxy("hello", "Int", "call-site:line-15")
try:
    print(f_typed(bad_arg))
except RuntimeError as e:
    print(e)

# Demonstrate: blame label identifies the boundary, not the function body
def g_typed(x_proxy):
    # g does more work before using x
    intermediate = 100
    x = x_proxy.force()
    return x + intermediate

bad_for_g = Proxy(3.14, "Int", "untyped-module:line-42")
try:
    print(g_typed(bad_for_g))
except RuntimeError as e:
    print(e)
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

### Critical Thinking Questions

**CTQ 13.** Without blame tracking, what would the error message look like if `f_typed` simply called `int(x)` and raised `ValueError` on a string? Why is knowing the **call site** more useful than knowing the **function body line** where the failure occurred?

[[___ your answer here ___]]

**CTQ 14.** TypeScript compiles to JavaScript and erases all types. mypy-annotated Python runs without any runtime checks. Given this, what happens when a TypeScript function typed `(n: number) => number` is called from JavaScript with a string? Does blame semantics apply?

[[___ your answer here ___]]

**CTQ 15.** If `f` is a typed function called from **untyped** code, should blame go to the **caller** or the **callee** when a type mismatch occurs? Justify your answer using the principle that blame should be assigned to the party that made a promise it did not keep.

[[___ your answer here ___]]

**CTQ 16.** The `Proxy` above only tracks a single `blame_label`. In a real system, typed values can pass through many boundaries (typed → untyped → typed → untyped). How might you extend `Proxy` to track a **chain** of blame labels rather than just one?

[[___ your answer here ___]]

---

## Model 5: Adding Gradual Typing to Your Language

This model is a direct bridge to your course interpreter project. The key new idea is `runtime_check`: a small function called at every typed boundary that either lets a value pass or raises an error with useful blame information. Annotated bindings are checked; unannotated ones are not. Everything else in the interpreter stays the same.

> **Watch out!** The `runtime_check` for a typed function parameter fires at **application time**, not at lambda definition time. The lambda itself is just a closure; the check happens when the function is called with a specific argument. Students sometimes expect the check at the point the `Lam` is evaluated — it is not.

The final model wires everything together: a small interpreter that supports **both typed and untyped bindings**. Annotated `let` bindings and annotated lambda parameters have their types **checked at runtime** when the value crosses the annotated boundary. Unannotated bindings pass through freely. This is the core mechanism of a gradually-typed interpreter — the static checker (Model 3) accepts programs that mix typed and untyped code; this interpreter enforces the typed parts at runtime.

The structure mirrors what you have been building in your course interpreter project. The new ingredient is `runtime_check`, which is called exactly when a value is bound to a typed name, and when a typed function is applied to an argument.

```python  liascript
from dataclasses import dataclass
from typing import Any, Optional

@dataclass
class Let:
    name: str
    ty: Optional[str]   # None = dynamic
    val: Any
    body: Any

@dataclass
class Var:    name: str
@dataclass
class Num:    value: float
@dataclass
class BinOp:  op: str; left: Any; right: Any
@dataclass
class Lam:    param: str; param_ty: Optional[str]; body: Any
@dataclass
class App:    fun: Any; arg: Any

class Env:
    def __init__(self, d=None, parent=None):
        self.d = d or {}; self.parent = parent
    def lookup(self, n):
        return self.d[n] if n in self.d else self.parent.lookup(n)
    def extend(self, n, v): return Env({n: v}, self)

@dataclass
class Closure:
    param: str; param_ty: Optional[str]; body: Any; env: Any

def runtime_check(value, expected_ty, where):
    if expected_ty is None: return value   # dynamic: no check
    actual = type(value).__name__
    ty_map = {"float": "Num", "int": "Num", "str": "Str",
              "bool": "Bool", "Closure": "Fun"}
    actual_ty = ty_map.get(actual, actual)
    if actual_ty != expected_ty:
        raise TypeError(f"[{where}] Expected {expected_ty}, got {actual_ty}")
    return value

def interp(expr, env):
    if isinstance(expr, Num): return float(expr.value)
    if isinstance(expr, Var): return env.lookup(expr.name)
    if isinstance(expr, BinOp):
        l, r = interp(expr.left, env), interp(expr.right, env)
        ops = {'+': l+r, '-': l-r, '*': l*r, '/': l/r}
        return ops[expr.op]
    if isinstance(expr, Let):
        v = interp(expr.val, env)
        v = runtime_check(v, expr.ty, f"let {expr.name}")
        return interp(expr.body, env.extend(expr.name, v))
    if isinstance(expr, Lam):
        return Closure(expr.param, expr.param_ty, expr.body, env)
    if isinstance(expr, App):
        fn = interp(expr.fun, env)
        arg = interp(expr.arg, env)
        arg = runtime_check(arg, fn.param_ty, f"call to {expr.fun}")
        return interp(fn.body, Env({fn.param: arg}, fn.env))

base_env = Env({"pi": 3.14159})

# Typed let: let x: Num = 5 in x * 2
prog1 = Let("x", "Num", Num(5), BinOp("*", Var("x"), Num(2)))
print("Typed let:", interp(prog1, base_env))

# Untyped let: let y = 5 in y * 2 (no check)
prog2 = Let("y", None, Num(5), BinOp("*", Var("y"), Num(2)))
print("Untyped let:", interp(prog2, base_env))

# Typed function: fun (x: Num) -> x + 1
typed_fn = Lam("x", "Num", BinOp("+", Var("x"), Num(1)))
prog3 = App(Let("f", None, typed_fn, Var("f")), Num(3))
print("Typed fn call:", interp(prog3, base_env))

# Typed let with wrong type: let x: Num = "hello" in x
prog4 = Let("x", "Num", Num(0), BinOp("+", Var("x"), Num(1)))
print("Well-typed annotated let:", interp(prog4, base_env))

# Demonstrate runtime_check catching a mismatch
try:
    bad = runtime_check("oops", "Num", "manual-test")
except TypeError as e:
    print(f"Caught: {e}")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

### Critical Thinking Questions

**CTQ 17.** The check `runtime_check(v, expr.ty, ...)` only runs when `expr.ty` is not `None`. What does the interpreter do with unannotated values? Can an unannotated binding ever cause a runtime type error in this interpreter?

[[___ your answer here ___]]

**CTQ 18.** If you annotate a `let` binding as `Num` but the right-hand side computes a `Closure` (e.g., `Let("f", "Num", Lam(...), ...)`), at what precise moment does the error fire? Trace through `interp` to identify the call chain.

[[___ your answer here ___]]

**CTQ 19.** Currently `runtime_check` handles `Num`, `Str`, `Bool`, and `Fun`. How would you add a `List[Num]` type to this system? Specifically, what would `runtime_check` need to do for lists — can it check the type in O(1), or must it inspect every element?

[[___ your answer here ___]]

**CTQ 20.** Compare this interpreter's behavior to the static checker from Model 3. If a program passes the static checker (Model 3), is it guaranteed to pass all runtime checks in this interpreter (Model 5)? If a program fails the static checker, does it necessarily fail at runtime? Explain both directions.

[[___ your answer here ___]]

---

## Multiple Choice

Which answer best completes each statement?

Gradual typing is "gradual" because...

[[ Type errors are only found gradually, one at a time ]]
[[ (X) Programs can mix typed and untyped code, with boundaries checked at runtime ]]
[[ Types are inferred gradually during execution ]]
[[ The type checker slows down gradually as programs grow ]]

---

`consistent(DYN, INT)` returns `True`. This means...

[[ DYN and INT are the same type ]]
[[ (X) A dynamically-typed value may be used where an Int is expected, with a runtime check inserted at the boundary ]]
[[ The program will not have any type errors ]]
[[ INT is a subtype of DYN ]]

---

In the blame calculus, blame is assigned to...

[[ (X) The code boundary that violated a type contract ]]
[[ The programmer who wrote the bug ]]
[[ The type checker ]]
[[ The line where the error was detected at runtime ]]

---

TypeScript compiles to JavaScript and erases all types. What does this mean for type safety?

[[ TypeScript programs are slower than JavaScript ]]
[[ (X) TypeScript type errors are caught at compile time but there are no runtime type checks in the generated JavaScript output ]]
[[ TypeScript and JavaScript have incompatible runtime semantics ]]
[[ TypeScript type annotations are treated as comments by the browser ]]

---

## Exercises

**Exercise 1: Extend Model 3 with `Let`**

Add a `Let` node to the `infer` function in Model 3. `Let(name, ty, val, body)` optionally annotates `name` with type `ty` (which may be `None`, meaning `DYN`). The checker should: (a) infer the type of `val`; (b) check that the inferred type is consistent with `ty` if `ty` is not `None`; (c) add `name` to the environment with the annotated type (or `DYN` if unannotated); (d) infer and return the type of `body`. Write two test cases: one that passes (annotated correctly) and one that fails (annotation mismatch).

**Exercise 2: Add `Str` type and string concatenation**

Extend Model 5's interpreter to support a `Str` type and string concatenation. Add a `StrLit` AST node whose value is a Python string and whose `runtime_check` type name is `"Str"`. Extend `BinOp` to support `"+"` on strings (concatenation). Write a test that concatenates two typed string values and one that mixes a typed `Str` with an untyped binding.

**Exercise 3: Non-transitivity and blame chains**

The consistency relation is not transitive: `consistent(INT, DYN)` and `consistent(DYN, STR)` are both true, but `consistent(INT, STR)` is false. Construct a three-module scenario (a typed module A, an untyped module B, and a typed module C) where a value flows from A through B to C. Describe precisely: (a) what check is inserted at the A→B boundary; (b) what check is inserted at the B→C boundary; (c) why non-transitivity means the B→C check can fail even when the A→B check succeeded.

---

## Reflection

> In your course journal: TypeScript, mypy, and Hack (PHP) all chose gradual typing over requiring a full switch to a statically typed language. Why might a language designer make this choice? What does it cost in terms of formal guarantees? If your final project language is dynamically typed, where would you add optional type annotations — which parts of the language would benefit most — and what would the annotation syntax look like?

---

## Further Reading

- Siek and Taha, "Gradual Typing for Functional Languages" (2006) — the paper that named and formalized the approach
- Wadler and Findler, "Well-Typed Programs Can't Be Blamed" (2009) — the blame calculus
- mypy documentation: `type: ignore` and `cast()` — how to escape the checker intentionally
- TypeScript's `unknown` vs `any` — a real-world version of this activity's `DYN` type, with `unknown` requiring an explicit narrowing check before use
- Typed Racket — a production gradually-typed language that does insert runtime checks, giving you actual blame semantics

---
