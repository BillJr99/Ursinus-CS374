<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://github.com/BillJr99/Ursinus-CS374-Fall2026/blob/gh-pages/_pages/Activities/liascript-type-inference-activity.md

import: https://raw.githubusercontent.com/liascript/CodeRunner/master/README.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

# Type Inference: How Does the Compiler Know the Types?

## Learning Goals

By the end of this activity, you will be able to:

- Explain how type inference frames type-checking as constraint generation followed by unification
- Trace the type variable assignment and constraint generation steps of Algorithm W for simple expressions and function definitions
- Implement the unification algorithm that solves a system of type equations by substitution
- Apply let-polymorphism (generalization and instantiation) to explain how the same function can be used at multiple types
- Analyze type inference failure cases and identify which constraint produces a unification error

> **Before You Begin**
>
> This activity assumes you are comfortable with:
>
> - **Type systems basics** — what types are, why they matter, and the difference between static and dynamic typing. Review: [Type Systems](liascript-type-systems.md)
> - **Python OOP** — dataclasses, inheritance, and `isinstance` checks. Review: [Types in Python](liascript-types.md)
>
> If either of those feels shaky, spend 10–15 minutes reviewing before continuing. The models here build directly on those foundations.

---

Type inference is the magic behind languages like Haskell, Rust, and OCaml where you don't write types — the compiler figures them out. At its core, it works like solving a system of equations: each expression generates type constraints (`x + 1` means `x` must be an `Int`), then unification solves the system. The result is that "if you can write it, it has a type; if it doesn't have a type, it won't compile." This is genuinely surprising — and you'll implement it from scratch today.

---

## Directions and Group Roles

Work in your POGIL team with rotated roles (**Manager**, **Recorder**, **Presenter**, **Reflector**). You will build Algorithm W piece by piece across five models, each model depending on the last. The Recorder maintains a running glossary of terms introduced. The Presenter will be asked to explain one model to another group. After class, respond to the reflective prompt individually in your notebook.

---

## Model 1: Types as Terms — A Type Algebra

### The Big Picture First

Before diving into code, here is the core intuition. Consider this simple function:

```
f(x) = x + 1

Step 1 — Assign type variables:  f : α,   x : β,   1 : Int

Step 2 — Generate constraints:   β = Int        (because x appears in x + 1, and 1 is Int,
                                                  so the + operator requires both sides to be Int)
                                  α = Int → Int  (because f takes a value of type β and returns
                                                  a value of type β + 1, which is Int)

Step 3 — Solve (unify):          substitute β = Int everywhere

Result:  f : Int → Int,   x : Int
```

This "assign unknowns, collect equations, solve" process is exactly what Algorithm W automates. Every model below implements one piece of it.

---

### Type Terms

Types in Hindley-Milner are **terms** — a small algebra with three forms: base types (`Int`, `Bool`, `Str`), function types (`t1 → t2`), and type variables (`'a`, `'b`, `'c`). Type variables are the key insight: they represent *unknown* types that the algorithm will later fill in.

```python  liascript
from dataclasses import dataclass, field
from typing import Any, Optional

# Type terms
@dataclass(frozen=True)
class TVar:    # type variable: 'a, 'b, 'c
    name: str
    def __str__(self): return f"'{self.name}"

@dataclass(frozen=True)
class TCon:    # type constructor: Int, Bool, List
    name: str
    args: tuple = ()
    def __str__(self):
        if not self.args: return self.name
        return f"({self.name} {' '.join(str(a) for a in self.args)})"

@dataclass(frozen=True)
class TFun:    # function type: t1 -> t2
    t1: Any
    t2: Any
    def __str__(self): return f"({self.t1} -> {self.t2})"

# Some type constants
Int  = TCon("Int")
Bool = TCon("Bool")
Str  = TCon("Str")
def List(t): return TCon("List", (t,))

# Type variables
a, b, c = TVar("a"), TVar("b"), TVar("c")

# Example types:
print("Some types:")
print(f"  Int:              {Int}")
print(f"  Bool:             {Bool}")
print(f"  Int -> Bool:      {TFun(Int, Bool)}")
print(f"  'a -> 'a:         {TFun(a, a)}")           # identity function
print(f"  'a -> 'b -> 'a:   {TFun(a, TFun(b, a))}")  # const function
print(f"  ('a -> 'b) -> List 'a -> List 'b: {TFun(TFun(a, b), TFun(List(a), List(b)))}")  # map

# Free type variables
def free_vars(t) -> set:
    if isinstance(t, TVar): return {t.name}
    if isinstance(t, TCon): return set().union(*[free_vars(a) for a in t.args]) if t.args else set()
    if isinstance(t, TFun): return free_vars(t.t1) | free_vars(t.t2)
    return set()

print(f"\nFree vars of ('a -> 'b -> 'a): {free_vars(TFun(a, TFun(b, a)))}")
print(f"Free vars of (Int -> Bool):     {free_vars(TFun(Int, Bool))}")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

### Critical Thinking Questions

> **CTQ 1.1** `TFun(a, TFun(b, a))` represents `'a -> 'b -> 'a`. What function has this type? (Hint: it takes two arguments and returns the first one, ignoring the second.) Write a Python lambda that has this type.

[[___ your answer here ___]]

> **CTQ 1.2** A type variable `'a` means "any type." The function `id : 'a -> 'a` says "given any type `'a`, it takes a value of that type and returns a value of that type." Why is this more useful than having `id_int : Int -> Int` and `id_bool : Bool -> Bool` as separate functions?

[[___ your answer here ___]]

> **CTQ 1.3** `free_vars` finds unbound type variables in a type. For `TFun(Int, Bool)`, there are no free variables. For `TFun(a, TFun(b, a))`, there are two. Why would a type *with* free variables be considered "polymorphic," while a type *without* free variables is "monomorphic"?

[[___ your answer here ___]]

> **CTQ 1.4** The `map` function's type `('a -> 'b) -> List 'a -> List 'b` contains two different type variables. What does the presence of *two* type variables say about `map`'s flexibility compared to a function like `reverse : List 'a -> List 'a` which has only one?

[[___ your answer here ___]]

---

## Model 2: Substitution — Replacing Type Variables with Types

### The Find-and-Replace Analogy

A substitution is like a "find and replace" for types. `{α: Int, β: Bool}` means "wherever you see α, replace it with Int; wherever you see β, replace it with Bool." So applying that substitution to `α → β` produces `Int → Bool`.

The algorithm builds up a substitution incrementally as it gathers constraints. At the end, the substitution tells us the type of every expression in the program.

> **Watch out!** `compose_subst` order matters: `compose(s1, s2)` applies s2 first, then s1. This is the function-composition convention — just like `(f ∘ g)(x) = f(g(x))` means g runs first. When composing `s1` on top of `s2`, we must apply `s1` to all of `s2`'s values so that earlier bindings are refined by later discoveries.

```python  liascript
# Substitution: dict mapping type variable names to types
# e.g., {"a": Int, "b": Bool} means 'a := Int, 'b := Bool

from dataclasses import dataclass
from typing import Any

@dataclass(frozen=True)
class TVar:
    name: str
    def __str__(self): return f"'{self.name}"

@dataclass(frozen=True)
class TCon:
    name: str
    args: tuple = ()
    def __str__(self):
        if not self.args: return self.name
        return f"({self.name} {' '.join(str(a) for a in self.args)})"

@dataclass(frozen=True)
class TFun:
    t1: Any
    t2: Any
    def __str__(self): return f"({self.t1} -> {self.t2})"

Int  = TCon("Int")
Bool = TCon("Bool")

def free_vars(t) -> set:
    if isinstance(t, TVar): return {t.name}
    if isinstance(t, TCon): return set().union(*[free_vars(a) for a in t.args]) if t.args else set()
    if isinstance(t, TFun): return free_vars(t.t1) | free_vars(t.t2)
    return set()

def apply_subst(subst: dict, t) -> Any:
    """Apply substitution to type t, recursively."""
    if isinstance(t, TVar):
        return apply_subst(subst, subst[t.name]) if t.name in subst else t
    if isinstance(t, TCon):
        return TCon(t.name, tuple(apply_subst(subst, a) for a in t.args))
    if isinstance(t, TFun):
        return TFun(apply_subst(subst, t.t1), apply_subst(subst, t.t2))
    return t

def compose_subst(s1: dict, s2: dict) -> dict:
    """Compose two substitutions: apply s1 to s2's values, then merge."""
    result = {k: apply_subst(s1, v) for k, v in s2.items()}
    result.update(s1)
    return result

# Test substitutions
subst1 = {"a": Int, "b": Bool}
t1 = TFun(TVar("a"), TVar("b"))  # 'a -> 'b
print(f"Before: {t1}")
print(f"After applying {{a:=Int, b:=Bool}}: {apply_subst(subst1, t1)}")

# Composition: first apply s2, then s1
s2 = {"c": TFun(TVar("a"), Int)}  # c := 'a -> Int
s1 = {"a": Bool}                   # a := Bool
composed = compose_subst(s1, s2)
print(f"\nComposed substitution: {composed}")
print(f"Apply composed to 'c: {apply_subst(composed, TVar('c'))}")  # should be Bool -> Int

# What about a substitution that maps a variable to itself?
identity_subst = {"a": TVar("a")}
t2 = TFun(TVar("a"), Int)
print(f"\nApply identity subst to 'a -> Int: {apply_subst(identity_subst, t2)}")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

### Critical Thinking Questions

> **CTQ 2.1** After applying `{a:=Int, b:=Bool}` to `'a -> 'b`, what is the result? Is there anything "polymorphic" left in the resulting type? What happened to the type variables?

[[___ your answer here ___]]

> **CTQ 2.2** `compose_subst(s1, s2)` means "first do s2, then do s1." Why must we apply `s1` to `s2`'s *values* when composing? Give a concrete example where forgetting to do this would produce a wrong result.

[[___ your answer here ___]]

> **CTQ 2.3** The code tests applying `{"a": TVar("a")}` (a variable mapped to itself) to `'a -> Int`. What is the result? Why is this substitution effectively a no-op, and when might the algorithm generate such a substitution?

[[___ your answer here ___]]

> **CTQ 2.4** After applying a "complete" substitution (one that maps every free variable), can the result still contain type variables? What would it mean if it does — is the expression still polymorphic, or is something wrong?

[[___ your answer here ___]]

---

## Model 3: Unification — The Heart of Type Inference

### What Unification Does

Unification asks: "Can these two types be made identical by substituting type variables?"

- `Int = Int` → yes (trivially — no substitution needed)
- `α = Int` → yes (substitute α := Int)
- `List(α) = List(Bool)` → yes (unify α with Bool, giving `{α: Bool}`)
- `Int = Bool` → **NO** (failure — this is a type error!)
- `α → β = Int → Bool` → yes (substitute α := Int, β := Bool)

The result of a successful unification is the *most general substitution* (MGU) that makes the two types equal. "Most general" means: we make only the commitments we are forced to make, leaving everything else as a free variable.

> **Watch out!** The occurs check prevents infinite types like `α = List(α)`. Without it, unification would try to build `List(List(List(...)))` forever — an infinitely nested type — and loop forever. The check catches this: if α appears inside the right-hand side, the equation has no finite solution, so we reject it as a type error.

**Unification** is the engine of type inference. When the algorithm says "this argument must be `Int` but you passed a `Bool`", that is a unification failure — a type error. When it succeeds, the result tells us exactly how to reconcile two type expressions.

```python  liascript
from dataclasses import dataclass
from typing import Any

@dataclass(frozen=True)
class TVar:
    name: str
    def __str__(self): return f"'{self.name}"

@dataclass(frozen=True)
class TCon:
    name: str
    args: tuple = ()
    def __str__(self):
        if not self.args: return self.name
        return f"({self.name} {' '.join(str(a) for a in self.args)})"

@dataclass(frozen=True)
class TFun:
    t1: Any
    t2: Any
    def __str__(self): return f"({self.t1} -> {self.t2})"

Int  = TCon("Int")
Bool = TCon("Bool")

def free_vars(t) -> set:
    if isinstance(t, TVar): return {t.name}
    if isinstance(t, TCon): return set().union(*[free_vars(a) for a in t.args]) if t.args else set()
    if isinstance(t, TFun): return free_vars(t.t1) | free_vars(t.t2)
    return set()

def apply_subst(subst: dict, t) -> Any:
    if isinstance(t, TVar):
        return apply_subst(subst, subst[t.name]) if t.name in subst else t
    if isinstance(t, TCon):
        return TCon(t.name, tuple(apply_subst(subst, a) for a in t.args))
    if isinstance(t, TFun):
        return TFun(apply_subst(subst, t.t1), apply_subst(subst, t.t2))
    return t

def compose_subst(s1: dict, s2: dict) -> dict:
    result = {k: apply_subst(s1, v) for k, v in s2.items()}
    result.update(s1)
    return result

class UnificationError(Exception): pass

def occurs_check(var_name: str, t) -> bool:
    """Return True if var_name appears in t (prevents infinite types)."""
    return var_name in free_vars(t)

def unify(t1, t2) -> dict:
    """
    Most General Unifier (MGU): find substitution S such that
    apply_subst(S, t1) == apply_subst(S, t2).
    """
    if t1 == t2:
        return {}  # no substitution needed — already equal

    if isinstance(t1, TVar):
        if occurs_check(t1.name, t2) and t2 != t1:
            raise UnificationError(f"Infinite type: {t1.name} occurs in {t2}")
        return {t1.name: t2}

    if isinstance(t2, TVar):
        return unify(t2, t1)  # symmetric: flip and try again

    if isinstance(t1, TFun) and isinstance(t2, TFun):
        s1 = unify(t1.t1, t2.t1)                           # unify parameter types
        s2 = unify(apply_subst(s1, t1.t2),                 # unify return types
                   apply_subst(s1, t2.t2))                  # (under s1)
        return compose_subst(s2, s1)

    if isinstance(t1, TCon) and isinstance(t2, TCon):
        if t1.name != t2.name or len(t1.args) != len(t2.args):
            raise UnificationError(f"Cannot unify {t1} with {t2}")
        s = {}
        for a1, a2 in zip(t1.args, t2.args):
            s = compose_subst(unify(apply_subst(s, a1), apply_subst(s, a2)), s)
        return s

    raise UnificationError(f"Cannot unify {t1} with {t2}")

# Tests
print("Unification tests:")
# 'a ~ Int => {'a: Int}
s = unify(TVar("a"), Int)
print(f"unify('a, Int) = {s}")

# 'a -> 'b ~ Int -> Bool => {'a: Int, 'b: Bool}
s = unify(TFun(TVar("a"), TVar("b")), TFun(Int, Bool))
print(f"unify('a->'b, Int->Bool) = {s}")

# ('a -> 'a) ~ (Int -> 'b) => {'a: Int, 'b: Int}
s = unify(TFun(TVar("a"), TVar("a")), TFun(Int, TVar("b")))
print(f"unify('a->'a, Int->'b) = {s}")

# Error: Int ~ Bool
try:
    unify(Int, Bool)
except UnificationError as e:
    print(f"unify(Int, Bool) => Error: {e}")

# Error: occurs check ('a ~ 'a -> Int would be infinite)
try:
    unify(TVar("a"), TFun(TVar("a"), Int))
except UnificationError as e:
    print(f"occurs check: {e}")

# Symmetry check
s_forward  = unify(TVar("a"), Int)
s_backward = unify(Int, TVar("a"))
print(f"\nunify('a, Int)  = {s_forward}")
print(f"unify(Int, 'a)  = {s_backward}")
print(f"Both yield same binding: {apply_subst(s_forward, TVar('a')) == apply_subst(s_backward, TVar('a'))}")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

### Critical Thinking Questions

> **CTQ 3.1** When unifying `'a -> 'a` with `Int -> 'b`, the result is `{'a: Int, 'b: Int}`. Trace through the `unify` code step by step to verify this. Which recursive call is responsible for establishing `'b: Int`?

[[___ your answer here ___]]

> **CTQ 3.2** What is the "occurs check" and why is it necessary? What would `'a ~ ('a -> Int)` mean if we allowed it — sketch what the resulting "type" would look like if you tried to write it out fully.

[[___ your answer here ___]]

> **CTQ 3.3** "Most general unifier" means there is no substitution that is MORE general. Why is `{'a: Int}` a valid MGU for `unify('a, Int)` but `{}` (the empty substitution) is not a valid unifier for the same pair?

[[___ your answer here ___]]

> **CTQ 3.4** The code verifies that unification is symmetric. Run it and confirm both directions give equal results. Now think about `unify('a -> 'b, 'b -> 'a)`. Without running code, predict what the MGU should be. Then verify by adding it to the code block.

[[___ your answer here ___]]

---

## Model 4: Algorithm W — Inferring Types for Expressions

### A Hand Trace Before the Code

Before reading the implementation, here is a complete hand trace of Algorithm W on `let id = λx.x in id 42`. Follow it carefully — then check that the code produces the same result.

```
W(λx.x):
  fresh α₁                          -- create a new unknown type for parameter x
  extend env with {x : α₁}
  W(x) = (∅, α₁)                   -- x has type α₁ in env {x : α₁}
  return (∅, α₁ → α₁)              -- id takes α₁ and returns α₁

W(id 42):
  W(id) = (∅, α₁ → α₁)            -- look up id in the env (instantiated fresh)
  W(42) = (∅, Int)                  -- numeric literals are Int
  fresh α₂                          -- unknown result type of the application
  unify (α₁ → α₁) with (Int → α₂) -- function type must match argument + result
    → α₁ = Int,  α₂ = Int
  result type = apply subst to α₂ = Int

Final: let id = λx.x in id 42  :  Int
```

The `let` case adds one step: after inferring the type of the bound expression, `generalize` wraps any free type variables in a `forall`. That is what lets `id` be used at multiple types in a single program.

> **Watch out!** Let-polymorphism is what makes `let id = λx.x in (id 1, id True)` work. The `id` function gets a "forall" type `∀α.α→α`, so each use can instantiate α differently — one use at `Int`, another at `Bool`. Without `let`-polymorphism, `id` would be forced to a single concrete type the first time it is used, and the second use at a different type would be a type error.

Algorithm W assigns types to every expression. It takes a **type environment** Γ (mapping variable names to type schemes) and an expression, and returns a substitution + type. The environment grows as we encounter `let` bindings and lambda parameters. The substitution grows as we unify constraints. At the end, composing all the substitutions gives us the complete type assignment for the program.

```python  liascript
from dataclasses import dataclass
from typing import Any

# --- Type terms (same as before) ---
@dataclass(frozen=True)
class TVar:
    name: str
    def __str__(self): return f"'{self.name}"

@dataclass(frozen=True)
class TCon:
    name: str
    args: tuple = ()
    def __str__(self):
        if not self.args: return self.name
        return f"({self.name} {' '.join(str(a) for a in self.args)})"

@dataclass(frozen=True)
class TFun:
    t1: Any
    t2: Any
    def __str__(self): return f"({self.t1} -> {self.t2})"

Int  = TCon("Int")
Bool = TCon("Bool")

def free_vars(t) -> set:
    if isinstance(t, TVar): return {t.name}
    if isinstance(t, TCon): return set().union(*[free_vars(a) for a in t.args]) if t.args else set()
    if isinstance(t, TFun): return free_vars(t.t1) | free_vars(t.t2)
    return set()

def apply_subst(subst: dict, t) -> Any:
    if isinstance(t, TVar):
        return apply_subst(subst, subst[t.name]) if t.name in subst else t
    if isinstance(t, TCon):
        return TCon(t.name, tuple(apply_subst(subst, a) for a in t.args))
    if isinstance(t, TFun):
        return TFun(apply_subst(subst, t.t1), apply_subst(subst, t.t2))
    return t

def compose_subst(s1: dict, s2: dict) -> dict:
    result = {k: apply_subst(s1, v) for k, v in s2.items()}
    result.update(s1)
    return result

class UnificationError(Exception): pass

def occurs_check(var_name: str, t) -> bool:
    return var_name in free_vars(t)

def unify(t1, t2) -> dict:
    if t1 == t2: return {}
    if isinstance(t1, TVar):
        if occurs_check(t1.name, t2) and t2 != t1:
            raise UnificationError(f"Infinite type: {t1.name} occurs in {t2}")
        return {t1.name: t2}
    if isinstance(t2, TVar): return unify(t2, t1)
    if isinstance(t1, TFun) and isinstance(t2, TFun):
        s1 = unify(t1.t1, t2.t1)
        s2 = unify(apply_subst(s1, t1.t2), apply_subst(s1, t2.t2))
        return compose_subst(s2, s1)
    if isinstance(t1, TCon) and isinstance(t2, TCon):
        if t1.name != t2.name or len(t1.args) != len(t2.args):
            raise UnificationError(f"Cannot unify {t1} with {t2}")
        s = {}
        for a1, a2 in zip(t1.args, t2.args):
            s = compose_subst(unify(apply_subst(s, a1), apply_subst(s, a2)), s)
        return s
    raise UnificationError(f"Cannot unify {t1} with {t2}")

# --- Type Schemes ---
class TypeScheme:
    """A polymorphic type: forall vars. type"""
    def __init__(self, vars: list, t):
        self.vars = vars  # universally quantified type variables
        self.t = t
    def __str__(self):
        if not self.vars: return str(self.t)
        return f"forall {','.join(self.vars)}. {self.t}"

# --- AST nodes ---
@dataclass
class Num: value: float
@dataclass
class Bool_: value: bool
@dataclass
class Var: name: str
@dataclass
class Lam: param: str; body: Any   # lambda x. body
@dataclass
class App: func: Any; arg: Any     # func arg
@dataclass
class Let: name: str; val: Any; body: Any

# --- Fresh type variable generator ---
_counter = [0]
def fresh() -> TVar:
    _counter[0] += 1
    return TVar(f"t{_counter[0]}")

def instantiate(scheme: TypeScheme) -> Any:
    """Replace quantified variables with fresh type variables."""
    subst = {v: fresh() for v in scheme.vars}
    return apply_subst(subst, scheme.t)

def generalize(env: dict, t) -> TypeScheme:
    """Quantify over type variables that don't appear free in env."""
    env_free = set().union(*(free_vars(s.t) for s in env.values())) if env else set()
    quantified = free_vars(t) - env_free
    return TypeScheme(list(quantified), t)

def w(env: dict, expr) -> tuple:
    """Algorithm W: returns (substitution, type)"""
    if isinstance(expr, Num):
        return {}, Int
    if isinstance(expr, Bool_):
        return {}, Bool
    if isinstance(expr, Var):
        if expr.name not in env:
            raise TypeError(f"Unbound variable: {expr.name}")
        return {}, instantiate(env[expr.name])
    if isinstance(expr, Lam):
        tv = fresh()
        new_env = {**env, expr.param: TypeScheme([], tv)}
        s1, t1 = w(new_env, expr.body)
        return s1, TFun(apply_subst(s1, tv), t1)
    if isinstance(expr, App):
        tv = fresh()
        s1, t1 = w(env, expr.func)
        s2, t2 = w({k: TypeScheme(v.vars, apply_subst(s1, v.t)) for k, v in env.items()}, expr.arg)
        s3 = unify(apply_subst(s2, t1), TFun(t2, tv))
        return compose_subst(s3, compose_subst(s2, s1)), apply_subst(s3, tv)
    if isinstance(expr, Let):
        s1, t1 = w(env, expr.val)
        env1 = {k: TypeScheme(v.vars, apply_subst(s1, v.t)) for k, v in env.items()}
        scheme = generalize(env1, t1)
        new_env = {**env1, expr.name: scheme}
        s2, t2 = w(new_env, expr.body)
        return compose_subst(s2, s1), t2
    raise TypeError(f"Unknown expression type: {type(expr)}")

# --- Tests ---
base_env = {}

# Test 1: infer type of (lambda x. x)  =>  'a -> 'a
_counter[0] = 0
s, t = w(base_env, Lam("x", Var("x")))
print(f"lambda x. x : {t}")

# Test 2: (lambda x. x) 42  =>  Int
_counter[0] = 0
s, t = w(base_env, App(Lam("x", Var("x")), Num(42)))
print(f"(lambda x. x) 42 : {t}")

# Test 3: let id = lambda x. x in id 42  =>  Int
_counter[0] = 0
s, t = w(base_env, Let("id", Lam("x", Var("x")), App(Var("id"), Num(42))))
print(f"let id = lambda x. x in id 42 : {t}")

# Test 4: let id = lambda x. x in id True  =>  Bool
_counter[0] = 0
s, t = w(base_env, Let("id", Lam("x", Var("x")), App(Var("id"), Bool_(True))))
print(f"let id = lambda x. x in id True : {t}")

# Test 5: lambda f. lambda x. f x  =>  ('a -> 'b) -> 'a -> 'b
_counter[0] = 0
s, t = w(base_env, Lam("f", Lam("x", App(Var("f"), Var("x")))))
print(f"lambda f. lambda x. f x : {t}")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

### Critical Thinking Questions

> **CTQ 4.1** When `w` processes `Lam("x", body)`, it creates a *fresh* type variable `tv` for the parameter `x`. Why does it need a fresh variable rather than reusing an existing type variable that might already be in scope?

[[___ your answer here ___]]

> **CTQ 4.2** For `App(func, arg)`, Algorithm W infers types for `func` and `arg` separately, then unifies `func`'s type with `TFun(t_arg, t_result)`. Why must `func`'s type be a function type for the application to type-check? What happens at the `unify` step if `func` is not a function?

[[___ your answer here ___]]

> **CTQ 4.3** `generalize` quantifies over free type variables in `t` that do NOT appear free in `env`. Why must we exclude variables that appear in `env`? Give a concrete example where including them would cause a type-safety violation.

[[___ your answer here ___]]

> **CTQ 4.4** The tests show `let id = λx.x in id 42` types to `Int` and `let id = λx.x in id True` types to `Bool`. In both cases, `id` has the polymorphic type `forall a. 'a -> 'a`. How does `instantiate` allow `id` to be used at different types in different calls?

[[___ your answer here ___]]

---

## Model 5: Type Errors as Unification Failures

Type errors are not a separate mechanism — they are simply unification failures. When two types cannot be made equal, Algorithm W raises an error. Understanding *where* the failure occurs tells you exactly *what* the programmer did wrong.

```python  liascript
from dataclasses import dataclass
from typing import Any

# --- Infrastructure (same as Model 4) ---
@dataclass(frozen=True)
class TVar:
    name: str
    def __str__(self): return f"'{self.name}"

@dataclass(frozen=True)
class TCon:
    name: str
    args: tuple = ()
    def __str__(self):
        if not self.args: return self.name
        return f"({self.name} {' '.join(str(a) for a in self.args)})"

@dataclass(frozen=True)
class TFun:
    t1: Any
    t2: Any
    def __str__(self): return f"({self.t1} -> {self.t2})"

Int  = TCon("Int")
Bool = TCon("Bool")

def free_vars(t) -> set:
    if isinstance(t, TVar): return {t.name}
    if isinstance(t, TCon): return set().union(*[free_vars(a) for a in t.args]) if t.args else set()
    if isinstance(t, TFun): return free_vars(t.t1) | free_vars(t.t2)
    return set()

def apply_subst(subst: dict, t) -> Any:
    if isinstance(t, TVar):
        return apply_subst(subst, subst[t.name]) if t.name in subst else t
    if isinstance(t, TCon):
        return TCon(t.name, tuple(apply_subst(subst, a) for a in t.args))
    if isinstance(t, TFun):
        return TFun(apply_subst(subst, t.t1), apply_subst(subst, t.t2))
    return t

def compose_subst(s1: dict, s2: dict) -> dict:
    result = {k: apply_subst(s1, v) for k, v in s2.items()}
    result.update(s1)
    return result

class UnificationError(Exception): pass

def occurs_check(var_name: str, t) -> bool:
    return var_name in free_vars(t)

def unify(t1, t2) -> dict:
    if t1 == t2: return {}
    if isinstance(t1, TVar):
        if occurs_check(t1.name, t2) and t2 != t1:
            raise UnificationError(f"Infinite type: {t1.name} occurs in {t2}")
        return {t1.name: t2}
    if isinstance(t2, TVar): return unify(t2, t1)
    if isinstance(t1, TFun) and isinstance(t2, TFun):
        s1 = unify(t1.t1, t2.t1)
        s2 = unify(apply_subst(s1, t1.t2), apply_subst(s1, t2.t2))
        return compose_subst(s2, s1)
    if isinstance(t1, TCon) and isinstance(t2, TCon):
        if t1.name != t2.name or len(t1.args) != len(t2.args):
            raise UnificationError(f"Cannot unify {t1} with {t2}")
        s = {}
        for a1, a2 in zip(t1.args, t2.args):
            s = compose_subst(unify(apply_subst(s, a1), apply_subst(s, a2)), s)
        return s
    raise UnificationError(f"Cannot unify {t1} with {t2}")

class TypeScheme:
    def __init__(self, vars: list, t):
        self.vars = vars
        self.t = t
    def __str__(self):
        if not self.vars: return str(self.t)
        return f"forall {','.join(self.vars)}. {self.t}"

@dataclass
class Num: value: float
@dataclass
class Bool_: value: bool
@dataclass
class Var: name: str
@dataclass
class Lam: param: str; body: Any
@dataclass
class App: func: Any; arg: Any
@dataclass
class Let: name: str; val: Any; body: Any

_counter = [0]
def fresh() -> TVar:
    _counter[0] += 1
    return TVar(f"t{_counter[0]}")

def instantiate(scheme: TypeScheme) -> Any:
    subst = {v: fresh() for v in scheme.vars}
    return apply_subst(subst, scheme.t)

def generalize(env: dict, t) -> TypeScheme:
    env_free = set().union(*(free_vars(s.t) for s in env.values())) if env else set()
    quantified = free_vars(t) - env_free
    return TypeScheme(list(quantified), t)

def w(env: dict, expr) -> tuple:
    if isinstance(expr, Num):   return {}, Int
    if isinstance(expr, Bool_): return {}, Bool
    if isinstance(expr, Var):
        if expr.name not in env:
            raise TypeError(f"Unbound variable: {expr.name}")
        return {}, instantiate(env[expr.name])
    if isinstance(expr, Lam):
        tv = fresh()
        new_env = {**env, expr.param: TypeScheme([], tv)}
        s1, t1 = w(new_env, expr.body)
        return s1, TFun(apply_subst(s1, tv), t1)
    if isinstance(expr, App):
        tv = fresh()
        s1, t1 = w(env, expr.func)
        s2, t2 = w({k: TypeScheme(v.vars, apply_subst(s1, v.t)) for k, v in env.items()}, expr.arg)
        s3 = unify(apply_subst(s2, t1), TFun(t2, tv))
        return compose_subst(s3, compose_subst(s2, s1)), apply_subst(s3, tv)
    if isinstance(expr, Let):
        s1, t1 = w(env, expr.val)
        env1 = {k: TypeScheme(v.vars, apply_subst(s1, v.t)) for k, v in env.items()}
        scheme = generalize(env1, t1)
        new_env = {**env1, expr.name: scheme}
        s2, t2 = w(new_env, expr.body)
        return compose_subst(s2, s1), t2
    raise TypeError(f"Unknown expression: {type(expr)}")

# --- Build a richer test environment ---
test_env = {
    "add":    TypeScheme([], TFun(Int, TFun(Int, Int))),
    "not_":   TypeScheme([], TFun(Bool, Bool)),
    "iszero": TypeScheme([], TFun(Int, Bool)),
}

# Test 1: Well-typed: add 1 2  =>  Int
_counter[0] = 0
s, t = w(test_env, App(App(Var("add"), Num(1)), Num(2)))
print(f"add 1 2 : {t}")

# Test 2: Well-typed: not_ (iszero 0)  =>  Bool
_counter[0] = 0
s, t = w(test_env, App(Var("not_"), App(Var("iszero"), Num(0))))
print(f"not_ (iszero 0) : {t}")

# Test 3: Ill-typed: add True 1  =>  type error
_counter[0] = 0
try:
    s, t = w(test_env, App(App(Var("add"), Bool_(True)), Num(1)))
    print(f"add True 1 : {t}")
except (UnificationError, TypeError) as e:
    print(f"Type error in 'add True 1': {e}")

# Test 4: Partial application is FINE — add 5 has type Int -> Int
_counter[0] = 0
s, t = w(test_env, App(Var("add"), Num(5)))
print(f"\nadd 5 (partial application) : {t}")

# Test 5: Let polymorphism — id used twice at same type
_counter[0] = 0
program = Let("id", Lam("x", Var("x")),
              App(App(Var("add"),
                      App(Var("id"), Num(1))),
                  App(Var("id"), Num(2))))
s, t = w(test_env, program)
print(f"\nlet id = lambda x. x in add (id 1) (id 2) : {t}")

# Test 6: Applying a non-function  =>  type error
_counter[0] = 0
try:
    s, t = w(test_env, App(Num(42), Num(1)))
    print(f"42 1 : {t}")
except (UnificationError, TypeError) as e:
    print(f"\nType error in '42 1' (applying a non-function): {e}")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

### Critical Thinking Questions

> **CTQ 5.1** `add True 1` fails because `True` has type `Bool` but `add` expects `Int`. Trace through the `App` case in Algorithm W to find the exact `unify` call that raises the error. Which two types are being unified when the error occurs?

[[___ your answer here ___]]

> **CTQ 5.2** `add 5` (partial application) succeeds with type `Int -> Int`. Why does applying a function to *too few* arguments not cause a type error? What would you have to do to trigger an arity-related error?

[[___ your answer here ___]]

> **CTQ 5.3** Test 5 uses `id` twice with `Int`. Modify the program so that `id` is used once with `Int` and once with `Bool` in the same `let` expression (for example, feed one result to `not_` and the other to `add`). Does it type-check? Why or why not?

[[___ your answer here ___]]

> **CTQ 5.4** What is the fundamental difference between a **type error** (caught by Algorithm W at compile time) and a **runtime error** (like division by zero)? Can type inference eliminate all possible program errors? If not, what can it and cannot it guarantee?

[[___ your answer here ___]]

---

## Multiple Choice

Which answer best completes each statement?

What does the "occurs check" in unification prevent?

[[ (X) Infinite types like `'a = 'a -> Int`, which would cause non-termination during type inference ]]
[[ Circular variable references at runtime ]]
[[ Using the same type variable twice in the same expression ]]
[[ Polymorphism in recursive functions ]]

---

What does `generalize(env, t)` do that `TypeScheme([], t)` does not?

[[ (X) It universally quantifies free type variables in `t` that are not constrained by `env`, enabling let-polymorphism ]]
[[ It applies a substitution to make all type variables concrete ]]
[[ It checks whether `t` contains any type errors ]]
[[ It removes duplicate type variables from `t` ]]

---

"Most General Unifier" (MGU) means:

[[ The substitution with the fewest mappings ]]
[[ (X) The substitution that makes `t1 = t2` while leaving maximum generality — any other unifier can be obtained by composing the MGU with another substitution ]]
[[ The substitution that works for the most possible programs ]]
[[ The first substitution found by the algorithm, before any optimization ]]

---

In Haskell, `length :: [a] -> Int`. What does this tell you about Algorithm W?

[[ `length` was annotated manually by the programmer ]]
[[ `length` has no type, so Haskell uses dynamic typing here ]]
[[ (X) Algorithm W inferred a polymorphic type: `length` works for any list regardless of element type ]]
[[ `length` is a special built-in that bypasses the type system ]]

---

## Exercises

**Exercise 1: Add `Plus` to the AST**

Add a `Plus` AST node that requires both arguments to be `Int` and returns `Int`. Extend `w` to handle it. Test both `Plus(Num(1), Num(2))` (should succeed with type `Int`) and `Plus(Num(1), Bool_(True))` (should fail with a type error naming `Bool` where `Int` was expected).

**Exercise 2: Add `If` to the AST**

Add `If(cond, then_e, else_e)` to the AST where `cond` must be `Bool` and both branches must have the same type. The resulting type is the type of either branch. Extend `w` to handle it. Test `If(Bool_(True), Num(1), Num(2))` (should succeed, type `Int`), `If(Num(1), Num(1), Num(2))` (should fail — condition is not `Bool`), and `If(Bool_(True), Num(1), Bool_(False))` (should fail — branches have different types).

**Exercise 3: Infer list literal types**

Implement `w_list(env, exprs)` that infers the type of a list literal: all elements must have the same type, and the result is `List[t]` for that common type. Use `TCon("List", (t,))` as the list type. Test `[Num(1), Num(2), Num(3)]` (should give `(List Int)`) and `[Num(1), Bool_(True), Num(3)]` (should fail — elements have different types).

**Exercise 4: Pretty-print inferred types**

Write a `typeof_expr(expr, env=None) -> str` function that calls Algorithm W on an expression and returns a clean, human-readable string for the inferred type. Normalize type variable names to alphabetical order (`'a`, `'b`, `'c`, ...) rather than `'t1`, `'t2`, etc. Test it on at least three examples from Models 4 and 5.

---

## Reflection

> In your notebook: Hindley-Milner type inference was published in 1978. Before it, type systems required programmers to annotate every variable and function parameter. After it, Haskell, ML, OCaml, Rust, and many others could infer types automatically throughout entire programs. What did this change about the *experience* of programming in those languages? And what are the limits — when can HM inference fail, produce confusing error messages, or require annotations after all?

---

## Further Reading

- Damas & Milner (1982) "Principal type-schemes for functional programs" — the original Algorithm W paper
- This course's Type Inference Tutorial — goes deeper on each phase of the algorithm
- This course's Type Inference Assignment — build the full system yourself
- Pierce, "Types and Programming Languages," Chapter 22 — Reconstruction
- Diehl, "Write You a Haskell" — implements HM in Haskell, for Haskell

---
