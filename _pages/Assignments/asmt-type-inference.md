---
layout: assignment
permalink: /Assignments/TypeInference
title: "CS374: Principles of Programming Languages - Type Inference"

info:
  coursenum: CS374
  points: 100
  goals:
    - To implement Robinson's unification algorithm with the occurs check
    - To implement Algorithm W for Hindley-Milner type inference over a Mini-language AST
    - To implement let-polymorphism by generalizing and instantiating type schemes
    - To produce clear, position-tagged type error messages
  rubric:
    - weight: 30
      description: Unification and Substitution
      preemerging: Unification is not implemented or fails on basic cases
      beginning: Unification handles trivial cases but fails on composed types or does not apply substitution transitively
      progressing: Unification works for composed types with a minor defect such as missing occurs check allowing infinite types
      proficient: Unification correctly handles all cases including occurs check, composed types, and transitive substitution composition; raises a clear TypeError naming both conflicting types on failure
    - weight: 35
      description: Algorithm W Type Inference
      preemerging: Algorithm W is not implemented or infers incorrect types for basic expressions
      beginning: Algorithm W infers types for literals and variables but fails on function application or let
      progressing: Algorithm W infers correct types for most expressions but has a defect in one case (e.g., incorrect constraint for binary operators, or missing generalization for let)
      proficient: Algorithm W infers correct principal types for all node types in the Mini AST (literals, variables, binary operators, if, let, fun, call) and threads substitutions correctly throughout
    - weight: 20
      description: Let-Polymorphism
      preemerging: Let-generalization is not implemented; let-bound functions are monomorphic
      beginning: Generalization exists but does not correctly exclude variables free in the environment, causing unsoundness
      progressing: Generalization and instantiation work for simple polymorphic let (e.g., identity function), but a complex case such as nested let or self-application fails
      proficient: Let-generalization correctly quantifies over variables not free in the current environment; instantiation refreshes every quantified variable; polymorphic identity applied to both Int and Bool in the same scope type-checks correctly
    - weight: 15
      description: Error Messages and Submission
      preemerging: No error messages; the typechecker crashes or returns no useful information on failure
      beginning: Type errors are reported but without source position or with messages that are difficult to understand
      progressing: Type errors report the conflicting types, with minor omissions such as missing position or unclear variable names
      proficient: Every type error names both conflicting types, cites the source line and expression context, and suggests what the programmer may have intended (e.g., "expected Int, got Bool in condition of if at line 7")
  readings:
    - rtitle: "Type Systems Activity"
      rlink: "https://liascript.github.io/course/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374-Fall2026/gh-pages/_pages/Activities/liascript-type-systems.md"
    - rtitle: "Tutorial: Build an Interpreter"
      rlink: "https://liascript.github.io/course/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374-Fall2026/gh-pages/_pages/Tutorials/tutorial-build-an-interpreter.md"

tags:
  - types
  - inference
  - hindley-milner
  - languages

---

This assignment implements **Hindley-Milner type inference** on top of the Mini language interpreter you already built. Rather than requiring type annotations, HM inference deduces the type of every expression automatically — the same algorithm that underlies Haskell, OCaml, and Rust's type system. Build in the order below; each part has a runnable test at the end.

## Background

A **type** in HM is one of:
- A **type variable** `α`, `β`, ... (unknown, to be solved)
- A **type constant** `Int`, `Bool`, `Str`, `Nil`
- A **function type** `τ₁ → τ₂`
- A **list type** `[τ]`

A **substitution** `σ` maps type variables to types. Applying `σ` to a type replaces all free type variables with their mapped types. **Unification** of two types finds the most general substitution that makes them equal.

**Algorithm W** walks the AST and, at each node, either returns a known type or generates fresh type variables constrained by the node's structure, then unifies to solve. **Let-polymorphism** (Milner's key insight) generalizes the type of a let-bound name over all its free type variables before adding it to the environment, then instantiates (refreshes) those variables on every use.

## Starter Code

```python
# types.py
import string
from dataclasses import dataclass, field
from typing import Dict, FrozenSet, Optional, Tuple, Any
from itertools import count

# --- Type terms ---

_counter = count()

def fresh():
    return f"α{next(_counter)}"

@dataclass(frozen=True)
class TVar:
    name: str
    def __str__(self): return self.name

@dataclass(frozen=True)
class TCon:
    name: str
    def __str__(self): return self.name

@dataclass(frozen=True)
class TFun:
    param: Any
    ret:   Any
    def __str__(self): return f"({self.param} → {self.ret})"

@dataclass(frozen=True)
class TList:
    elem: Any
    def __str__(self): return f"[{self.elem}]"

TInt  = TCon("Int")
TBool = TCon("Bool")
TStr  = TCon("Str")
TNil  = TCon("Nil")

# --- Substitution ---

def apply(subst: Dict, typ) -> Any:
    if isinstance(typ, TVar):
        return apply(subst, subst[typ.name]) if typ.name in subst else typ
    if isinstance(typ, TCon):
        return typ
    if isinstance(typ, TFun):
        return TFun(apply(subst, typ.param), apply(subst, typ.ret))
    if isinstance(typ, TList):
        return TList(apply(subst, typ.elem))
    raise TypeError(f"unknown type term {typ!r}")

def compose(s2: Dict, s1: Dict) -> Dict:
    result = {k: apply(s2, v) for k, v in s1.items()}
    result.update({k: v for k, v in s2.items() if k not in result})
    return result

def free_vars(typ) -> FrozenSet[str]:
    if isinstance(typ, TVar):  return frozenset({typ.name})
    if isinstance(typ, TCon):  return frozenset()
    if isinstance(typ, TFun):  return free_vars(typ.param) | free_vars(typ.ret)
    if isinstance(typ, TList): return free_vars(typ.elem)
    raise TypeError(f"unknown type term {typ!r}")
```

## Part 1: Unification (30 points)

Implement `unify(t1, t2, subst=None) -> Dict` in `types.py`. The algorithm:

1. Apply the current substitution to both types.
2. If both are identical type constants or variables after applying, return the current substitution unchanged.
3. If one is a type variable `α` not occurring in the other, extend the substitution with `{α: other}` (after the **occurs check**: if `α` appears inside `other`, raise a `TypeError` because no finite type can equal itself).
4. If both are `TFun` or both are `TList`, recursively unify the components (compose the substitutions).
5. Otherwise, raise a `TypeError` naming both types.

```python
def occurs(var_name: str, typ) -> bool:
    return var_name in free_vars(typ)

def unify(t1, t2, subst=None):
    if subst is None: subst = {}
    t1, t2 = apply(subst, t1), apply(subst, t2)
    if t1 == t2:
        return subst
    if isinstance(t1, TVar):
        if occurs(t1.name, t2):
            raise TypeError(f"occurs check: {t1} appears in {t2}")
        return compose({t1.name: t2}, subst)
    if isinstance(t2, TVar):
        return unify(t2, t1, subst)
    if isinstance(t1, TFun) and isinstance(t2, TFun):
        s1 = unify(t1.param, t2.param, subst)
        return unify(apply(s1, t1.ret), apply(s1, t2.ret), s1)
    if isinstance(t1, TList) and isinstance(t2, TList):
        return unify(t1.elem, t2.elem, subst)
    raise TypeError(f"cannot unify {t1} with {t2}")
```

**Test:** confirm these outcomes:
- `unify(TVar("a"), TInt)` → `{"a": TInt}`
- `unify(TFun(TVar("a"), TVar("b")), TFun(TInt, TBool))` → `{"a": TInt, "b": TBool}`
- `unify(TVar("a"), TList(TVar("a")))` → TypeError (occurs check)
- `unify(TInt, TBool)` → TypeError

## Part 2: Algorithm W (35 points)

Implement `infer(node, env, subst=None) -> Tuple[subst, type]` in `infer.py`. Import your AST nodes from your Mini parser. For each node type:

```
IntLit, FloatLit → return (subst, TInt) or (subst, TFloat)
StrLit           → return (subst, TStr)
BoolLit          → return (subst, TBool)
NilLit           → return (subst, TList(TVar(fresh())))

Var(name)        → look up name in env; if absent raise TypeError with line info
                   if it's a TypeScheme, instantiate it

UnaryOp("-")     → infer operand; unify with TInt; return (subst, TInt)
UnaryOp("not")   → infer operand; unify with TBool; return (subst, TBool)

BinOp("+"/"-"/"*"/"/"...) →
    infer left; infer right (under composed subst);
    unify both with TInt (or handle "+" for strings too);
    return (subst, TInt)

BinOp("=="/"!="/"<"/...)  →
    infer left; infer right; unify both to a fresh TVar tv;
    return (subst, TBool)

BinOp("and"/"or") → infer both, unify both with TBool; return (subst, TBool)

IfStmt(cond, then, else) →
    infer cond; unify with TBool;
    infer then; infer else (if present);
    unify then-type with else-type (or Nil if no else);
    return unified result type

LetStmt(name, value) →
    infer value type;
    generalize over free vars not in env;
    extend env with (name → TypeScheme);
    return (subst, TNil)

FunExpr(params, body) →
    assign fresh type variables to all params;
    extend env with those bindings;
    infer body type;
    return (subst, TFun(param_types..., body_type))

Call(callee, args) →
    infer callee type; infer each arg;
    create fresh return variable ret;
    unify callee_type with TFun(arg_types..., ret);
    return (subst, apply(subst, ret))
```

**Test:** infer the type of each:
- `let x = 42;` → `x: Int`
- `fun(x) { x }` → `α → α` (identity, polymorphic)
- `fun(x) { x + 1 }` → `Int → Int`
- `if true { 1 } else { 2 }` → `Int`
- `if true { 1 } else { "oops" }` → TypeError

## Part 3: Let-Polymorphism (20 points)

Without generalization, the identity function `let id = fun(x) { x }; id(1); id(true)` would fail because the first call would fix `x: Int` and the second would fail. Implement:

```python
# In types.py

@dataclass
class TypeScheme:
    quantified: FrozenSet[str]   # bound type variables (∀ α. ...)
    body:       Any

    def instantiate(self) -> Any:
        fresh_map = {v: TVar(fresh()) for v in self.quantified}
        return apply(fresh_map, self.body)

    def __str__(self):
        if not self.quantified: return str(self.body)
        qs = " ".join(sorted(self.quantified))
        return f"∀{qs}. {self.body}"

def generalize(env_free_vars: FrozenSet[str], typ) -> TypeScheme:
    quantified = free_vars(typ) - env_free_vars
    return TypeScheme(quantified, typ)

def env_free_vars(type_env: Dict) -> FrozenSet[str]:
    result = frozenset()
    for scheme in type_env.values():
        if isinstance(scheme, TypeScheme):
            result |= free_vars(scheme.body) - scheme.quantified
        else:
            result |= free_vars(scheme)
    return result
```

When inferring `LetStmt`, generalize the inferred type before storing it in the environment. When looking up a variable bound to a `TypeScheme`, call `instantiate()` to get a fresh copy.

**Test:**
```python
# id(1) and id(true) must both type-check
src = "let id = fun(x) { return x; }; let a = id(1); let b = id(true);"
```

**Test for unsoundness:** the following must fail (self-application is untypeable in HM):
```python
# fun(f) { f(f) }  — f would need type α → α where α = α → α
```

## Part 4: Error Messages (15 points)

Improve every `TypeError` you raise to include:
- The source line number (from your `Var` and `LetStmt` nodes' `line` fields)
- The two conflicting types written in readable form
- A short contextual description ("in condition of if", "in argument 1 of call to f", etc.)

Example messages:
```
[TypeError] line 7: condition of 'if' must be Bool, got Int
[TypeError] line 12: '+' requires Int operands, got Str and Int
[TypeError] line 3: function 'double' expects Int, got Bool for parameter 'x'
[TypeError] line 5: cannot unify Int with Bool (inferred from let 'result')
```

## Deliverables

Submit a ZIP containing:
- `types.py` — type terms, substitution, unification, TypeScheme
- `infer.py` — Algorithm W over your Mini AST nodes
- `test_types.py` — tests for Parts 1–3 with `assert` statements for both success and expected failures
- `examples/` — at least five `.mini` source files that demonstrate: a rejected type error, a let-polymorphic function used at two types, a higher-order function, a recursive function (if you implement letrec inference), and one program of your own choice
- A `README.md` of approximately one page: which type errors caught bugs you did not expect; what was hard about threading substitutions; how HM compares to the dynamic type checking in your interpreter

## Reflection Prompts

- HM inference finds the *most general* (principal) type. Explain in one paragraph what "most general" means operationally: if two different substitutions both satisfy all the constraints, which one does Algorithm W pick, and why is that the right choice for a user?
- Where in your evaluator do runtime `TypeError`s get thrown? For each such location, describe what HM would catch statically that currently waits until runtime.
- If collaboration with a buddy was permitted, did you work with a buddy on this assignment? If so, who? If not, do you certify that this submission represents your own original work? Please identify any and all portions of your submission that were not originally written by you.
- Approximately how many hours did this assignment take?
