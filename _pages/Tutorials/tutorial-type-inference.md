<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374/gh-pages/_pages/Tutorials/tutorial-type-inference.md

import: https://raw.githubusercontent.com/liascript/CodeRunner/master/README.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

# Tutorial: Implementing Hindley-Milner Type Inference

## Learning Goals

By the end of this tutorial, you will have:

- Implemented Robinson's unification algorithm with the occurs check and verified it on composed type expressions
- Implemented `apply` and `compose` for type substitutions and confirmed substitution composition is associative
- Implemented Algorithm W that walks the Mini AST and returns a principal type for every expression node
- Implemented let-polymorphism (generalization and instantiation) so that a polymorphic identity function type-checks at multiple types in the same scope
- Produced clear, position-tagged type error messages that name both conflicting types and the source location

Hindley-Milner (HM) type inference deduces the type of every expression without any type annotations. It powers Haskell, OCaml, and Rust's type inference. This tutorial walks you step-by-step through building a complete HM inference engine over the Mini language AST: types, unification with occurs check, Algorithm W, and let-polymorphism. Each phase includes working Python code you can run and test before moving to the next. **Prerequisites:** the Type Systems activity, the Curry-Howard activity, and your Mini interpreter assignment.

---

## Phase 0: The Big Picture

The algorithm has four components, built in order:

1. **Type terms**: the language of types: `Int`, `Bool`, `α` (type variable), `α -> β` (function type)
2. **Substitution**: mapping from type variable names to types; `apply(subst, type)` replaces variables
3. **Unification**: given two types, find the most general substitution making them equal
4. **Algorithm W**: walk the AST, generate and solve type constraints, return the principal type

---

## Phase 1: Type Terms

```python
try:
    from dataclasses import dataclass
    from typing import FrozenSet, Dict, Any, Optional
    from itertools import count

    # Global counter for fresh type variables
    _counter = count()
    def fresh() -> str:
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
        def __str__(self): return f"({self.param} -> {self.ret})"

    @dataclass(frozen=True)
    class TList:
        elem: Any
        def __str__(self): return f"[{self.elem}]"

    # Convenience constants
    TInt  = TCon("Int")
    TBool = TCon("Bool")
    TStr  = TCon("Str")
    TNil  = TCon("Nil")   # the type of None/nil

    # Test: build some types
    a, b = TVar("α"), TVar("β")
    id_type = TFun(a, a)
    print("identity type:", id_type)
    print("Int -> Bool:", TFun(TInt, TBool))
    print("[Int]:", TList(TInt))

except Exception as e:
    print(f"[hm:types] {e}")
    import traceback; traceback.print_exc()
```

---

## Phase 2: Substitution

A substitution is a `dict` mapping variable names to types. `apply(subst, typ)` replaces all free type variables in `typ` with their mapped values. `compose(s2, s1)` creates a new substitution that first applies `s1` then `s2`.

```python
try:
    from dataclasses import dataclass
    from itertools import count

    _counter = count()
    def fresh(): return f"α{next(_counter)}"

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
        param: object; ret: object
        def __str__(self): return f"({self.param} -> {self.ret})"
    @dataclass(frozen=True)
    class TList:
        elem: object
        def __str__(self): return f"[{self.elem}]"
    TInt = TCon("Int"); TBool = TCon("Bool"); TStr = TCon("Str")

    def apply(subst: dict, typ) -> object:
        """Apply substitution to a type (recursively)."""
        if isinstance(typ, TVar):
            # Chase chains: if α maps to β, and β maps to Int, return Int
            if typ.name in subst:
                return apply(subst, subst[typ.name])
            return typ
        if isinstance(typ, TCon):
            return typ
        if isinstance(typ, TFun):
            return TFun(apply(subst, typ.param), apply(subst, typ.ret))
        if isinstance(typ, TList):
            return TList(apply(subst, typ.elem))
        raise TypeError(f"unknown type: {typ!r}")

    def compose(s2: dict, s1: dict) -> dict:
        """Compose: apply s2 to all values of s1, then add s2's bindings."""
        result = {k: apply(s2, v) for k, v in s1.items()}
        result.update({k: v for k, v in s2.items() if k not in result})
        return result

    def free_vars(typ) -> frozenset:
        """Set of free type variable names in typ."""
        if isinstance(typ, TVar):   return frozenset({typ.name})
        if isinstance(typ, TCon):   return frozenset()
        if isinstance(typ, TFun):   return free_vars(typ.param) | free_vars(typ.ret)
        if isinstance(typ, TList):  return free_vars(typ.elem)
        raise TypeError(f"unknown type: {typ!r}")

    # Test substitution
    s = {"α0": TInt, "α1": TBool}
    t = TFun(TVar("α0"), TVar("α1"))
    print("Before apply:", t)
    print("After apply:", apply(s, t))

    # Chain resolution: α0 -> α1 -> Int
    s2 = {"α0": TVar("α1"), "α1": TInt}
    print("Chain: α0 in {α0->α1, α1->Int}:", apply(s2, TVar("α0")))

    # Composition
    s_a = {"α0": TVar("α1")}     # first: substitute α0 -> α1
    s_b = {"α1": TInt}           # then: substitute α1 -> Int
    composed = compose(s_b, s_a)
    print("compose({α1->Int}, {α0->α1}):", composed)
    print("α0 after compose:", apply(composed, TVar("α0")))

except Exception as e:
    print(f"[hm:subst] {e}")
    import traceback; traceback.print_exc()
```

**Common mistake:** forgetting to chase chains in `apply`. Always apply recursively when following a variable.

---

## Phase 3: Unification

Unification finds the most general substitution (MGU) that makes two types equal. The occurs check prevents creating infinite types like `α = List α`.

```python
try:
    from dataclasses import dataclass
    from itertools import count

    _counter = count()
    def fresh(): return f"α{next(_counter)}"

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
        param: object; ret: object
        def __str__(self): return f"({self.param} -> {self.ret})"
    @dataclass(frozen=True)
    class TList:
        elem: object
        def __str__(self): return f"[{self.elem}]"
    TInt = TCon("Int"); TBool = TCon("Bool")

    def apply(subst, typ):
        if isinstance(typ, TVar):
            return apply(subst, subst[typ.name]) if typ.name in subst else typ
        if isinstance(typ, TCon): return typ
        if isinstance(typ, TFun): return TFun(apply(subst, typ.param), apply(subst, typ.ret))
        if isinstance(typ, TList): return TList(apply(subst, typ.elem))
        raise TypeError(f"unknown: {typ!r}")

    def compose(s2, s1):
        result = {k: apply(s2, v) for k, v in s1.items()}
        result.update({k: v for k, v in s2.items() if k not in result})
        return result

    def free_vars(typ):
        if isinstance(typ, TVar):  return frozenset({typ.name})
        if isinstance(typ, TCon):  return frozenset()
        if isinstance(typ, TFun):  return free_vars(typ.param) | free_vars(typ.ret)
        if isinstance(typ, TList): return free_vars(typ.elem)
        raise TypeError(f"unknown: {typ!r}")

    def occurs(name: str, typ) -> bool:
        return name in free_vars(typ)

    def unify(t1, t2, subst=None) -> dict:
        """Return a substitution that unifies t1 and t2, or raise TypeError."""
        if subst is None: subst = {}
        t1 = apply(subst, t1)
        t2 = apply(subst, t2)

        # Already equal (includes identical constants)
        if t1 == t2:
            return subst

        # Bind type variable (check occurs first)
        if isinstance(t1, TVar):
            if occurs(t1.name, t2):
                raise TypeError(f"occurs check failed: {t1} appears in {t2}")
            return compose({t1.name: t2}, subst)

        if isinstance(t2, TVar):
            return unify(t2, t1, subst)   # symmetric: t2 is a variable

        # Both TFun: unify components
        if isinstance(t1, TFun) and isinstance(t2, TFun):
            s1 = unify(t1.param, t2.param, subst)
            return unify(apply(s1, t1.ret), apply(s1, t2.ret), s1)

        # Both TList: unify elements
        if isinstance(t1, TList) and isinstance(t2, TList):
            return unify(t1.elem, t2.elem, subst)

        raise TypeError(f"cannot unify {t1} with {t2}")

    # Tests
    # 1. Variable binds to constant
    s = unify(TVar("α0"), TInt)
    print("unify(α0, Int):", s)

    # 2. Unify function types
    s = unify(TFun(TVar("α0"), TVar("α1")), TFun(TInt, TBool))
    print("unify(α0->α1, Int->Bool):", s)

    # 3. Occurs check failure
    try:
        unify(TVar("α0"), TList(TVar("α0")))
    except TypeError as e:
        print("occurs check:", e)

    # 4. Constant mismatch
    try:
        unify(TInt, TBool)
    except TypeError as e:
        print("mismatch:", e)

    # 5. Unify with substitution already in place
    s = {"α0": TInt}
    s2 = unify(TVar("α0"), TVar("α1"), s)
    print("unify α0 α1 with {α0->Int}:", s2, "-> α1 =", apply(s2, TVar("α1")))

except Exception as e:
    print(f"[hm:unify] {e}")
    import traceback; traceback.print_exc()
```

**Key insight:** always `apply(subst, ...)` BEFORE checking for variables or constants. This "chases" existing substitution chains before deciding what to do.

---

## Phase 4: Algorithm W

Algorithm W walks the AST and infers types. For each node, it either returns a known type or generates fresh type variables and unifies to solve constraints.

```python
try:
    from dataclasses import dataclass, field
    from typing import Dict, FrozenSet, Any
    from itertools import count
    from copy import deepcopy

    _counter = count()
    def fresh(): return f"α{next(_counter)}"

    # --- Type terms (inline) ---
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
        param: object; ret: object
        def __str__(self): return f"({self.param} -> {self.ret})"
    @dataclass(frozen=True)
    class TList:
        elem: object
        def __str__(self): return f"[{self.elem}]"
    TInt = TCon("Int"); TBool = TCon("Bool"); TStr = TCon("Str"); TNil = TCon("Nil")

    def apply(subst, typ):
        if isinstance(typ, TVar):
            return apply(subst, subst[typ.name]) if typ.name in subst else typ
        if isinstance(typ, TCon): return typ
        if isinstance(typ, TFun): return TFun(apply(subst, typ.param), apply(subst, typ.ret))
        if isinstance(typ, TList): return TList(apply(subst, typ.elem))
        raise TypeError(f"unknown: {typ!r}")
    def compose(s2, s1):
        r = {k: apply(s2, v) for k, v in s1.items()}
        r.update({k: v for k, v in s2.items() if k not in r})
        return r
    def free_vars(typ):
        if isinstance(typ, TVar):  return frozenset({typ.name})
        if isinstance(typ, TCon):  return frozenset()
        if isinstance(typ, TFun):  return free_vars(typ.param) | free_vars(typ.ret)
        if isinstance(typ, TList): return free_vars(typ.elem)
        return frozenset()
    def occurs(name, typ): return name in free_vars(typ)
    def unify(t1, t2, subst=None):
        if subst is None: subst = {}
        t1 = apply(subst, t1); t2 = apply(subst, t2)
        if t1 == t2: return subst
        if isinstance(t1, TVar):
            if occurs(t1.name, t2): raise TypeError(f"occurs: {t1} in {t2}")
            return compose({t1.name: t2}, subst)
        if isinstance(t2, TVar): return unify(t2, t1, subst)
        if isinstance(t1, TFun) and isinstance(t2, TFun):
            s1 = unify(t1.param, t2.param, subst)
            return unify(apply(s1, t1.ret), apply(s1, t2.ret), s1)
        if isinstance(t1, TList) and isinstance(t2, TList):
            return unify(t1.elem, t2.elem, subst)
        raise TypeError(f"cannot unify {t1} with {t2}")

    # --- Algorithm W ---
    def infer(expr, env: dict, subst=None):
        """Return (subst, type). env maps names to types or TypeSchemes."""
        if subst is None: subst = {}
        tag = expr[0]

        # Literals
        if tag == 'int':   return (subst, TInt)
        if tag == 'float': return (subst, TInt)   # simplify: no TFloat
        if tag == 'bool':  return (subst, TBool)
        if tag == 'str':   return (subst, TStr)
        if tag == 'nil':   return (subst, TList(TVar(fresh())))   # nil : [α]

        # Variable
        if tag == 'var':
            name = expr[1]
            if name not in env:
                raise TypeError(f"unbound variable '{name}'")
            t = env[name]
            # Instantiate a TypeScheme if present (Phase 5)
            if hasattr(t, 'instantiate'):
                t = t.instantiate()
            return (subst, apply(subst, t))

        # Unary minus: operand must be Int -> result Int
        if tag == 'neg':
            _, e = expr
            s1, t1 = infer(e, env, subst)
            s2 = unify(t1, TInt, s1)
            return (s2, TInt)

        # Binary arithmetic
        if tag == 'binop':
            _, op, e1, e2 = expr
            s1, t1 = infer(e1, env, subst)
            s2, t2 = infer(e2, env, s1)
            if op in ('+', '-', '*', '/', '%'):
                s3 = unify(t1, TInt, s2)
                s4 = unify(t2, TInt, s3)
                return (s4, TInt)
            if op in ('<', '>', '<=', '>=', '==', '!='):
                # comparison: both sides must match each other
                tv = TVar(fresh())
                s3 = unify(t1, tv, s2)
                s4 = unify(t2, apply(s3, tv), s3)
                return (s4, TBool)
            if op in ('and', 'or'):
                s3 = unify(t1, TBool, s2)
                s4 = unify(t2, TBool, s3)
                return (s4, TBool)
            raise TypeError(f"unknown op: {op!r}")

        # If expression
        if tag == 'if':
            _, cond, then_e, else_e = expr
            s1, tc = infer(cond, env, subst)
            s2 = unify(tc, TBool, s1)
            s3, tt = infer(then_e, env, s2)
            if else_e is None:
                return (s3, TNil)   # no else: return Nil
            s4, te = infer(else_e, env, s3)
            s5 = unify(tt, te, s4)
            return (s5, apply(s5, tt))

        # Let statement (monomorphic for now - Phase 5 adds polymorphism)
        if tag == 'let':
            _, name, val = expr
            s1, t1 = infer(val, env, subst)
            new_env = {**env, name: apply(s1, t1)}
            return (s1, TNil)

        # Function expression: λ(params) body
        if tag == 'fun':
            _, params, body = expr
            param_types = {p: TVar(fresh()) for p in params}
            new_env = {**env, **param_types}
            s1, ret_type = infer(body, new_env, subst)
            # Build the curried function type
            fn_type = apply(s1, ret_type)
            for p in reversed(params):
                fn_type = TFun(apply(s1, param_types[p]), fn_type)
            return (s1, fn_type)

        # Function call
        if tag == 'call':
            _, callee, args = expr
            s1, callee_type = infer(callee, env, subst)
            arg_types = []
            s = s1
            for arg in args:
                s, t = infer(arg, env, s)
                arg_types.append(t)
            ret = TVar(fresh())
            # Build expected type: arg1 -> arg2 -> ... -> ret
            expected = ret
            for t in reversed(arg_types):
                expected = TFun(t, expected)
            s2 = unify(callee_type, expected, s)
            return (s2, apply(s2, ret))

        raise ValueError(f"unknown node: {expr!r}")

    # --- Tests ---
    env = {}

    # let x = 42  -> x: Int
    s, t = infer(('let', 'x', ('int', 42)), env)
    print(f"let x = 42 -> {t}")

    # 1 + 2 -> Int
    s, t = infer(('binop', '+', ('int', 1), ('int', 2)), env)
    print(f"1 + 2 -> {t}")

    # (λx. x + 1) -> (Int -> Int)
    s, t = infer(('fun', ['x'], ('binop', '+', ('var', 'x'), ('int', 1))), env)
    print(f"λx. x+1 -> {apply(s, t)}")

    # (λx. x)(5) -> Int
    s, t = infer(('call',
                  ('fun', ['x'], ('var', 'x')),
                  [('int', 5)]), env)
    print(f"(λx. x)(5) -> {apply(s, t)}")

    # if true then 1 else 2 -> Int
    s, t = infer(('if', ('bool', True), ('int', 1), ('int', 2)), env)
    print(f"if true then 1 else 2 -> {t}")

    # Type error: if 1 then 2 else 3
    try:
        infer(('if', ('int', 1), ('int', 2), ('int', 3)), env)
    except TypeError as e:
        print(f"type error (expected): {e}")

    # Type error: 1 + true
    try:
        infer(('binop', '+', ('int', 1), ('bool', True)), env)
    except TypeError as e:
        print(f"type error (expected): {e}")

except Exception as e:
    print(f"[hm:alg-w] {e}")
    import traceback; traceback.print_exc()
```

---

## Phase 5: Let-Polymorphism

Without polymorphism, `let id = λx. x in id(1); id(true)` fails: the first call forces `x: Int`, and the second call on the same `id` then fails with type `Bool`. **Let-polymorphism** (Milner's key insight) generalizes the type of `id` before adding it to the environment: `id: ∀α. α -> α`. Each use of `id` gets a fresh copy of `α`.

```python
try:
    from dataclasses import dataclass
    from itertools import count

    _counter = count()
    def fresh(): return f"β{next(_counter)}"   # use β to distinguish from Phase 4

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
        param: object; ret: object
        def __str__(self): return f"({self.param} -> {self.ret})"
    TInt = TCon("Int"); TBool = TCon("Bool")

    def apply(s, t):
        if isinstance(t, TVar): return apply(s, s[t.name]) if t.name in s else t
        if isinstance(t, TCon): return t
        if isinstance(t, TFun): return TFun(apply(s, t.param), apply(s, t.ret))
        return t
    def free_vars(t):
        if isinstance(t, TVar):  return frozenset({t.name})
        if isinstance(t, TCon):  return frozenset()
        if isinstance(t, TFun):  return free_vars(t.param) | free_vars(t.ret)
        return frozenset()
    def occurs(n, t): return n in free_vars(t)
    def compose(s2, s1):
        r = {k: apply(s2, v) for k, v in s1.items()}
        r.update({k: v for k, v in s2.items() if k not in r})
        return r
    def unify(t1, t2, s=None):
        if s is None: s = {}
        t1, t2 = apply(s, t1), apply(s, t2)
        if t1 == t2: return s
        if isinstance(t1, TVar):
            if occurs(t1.name, t2): raise TypeError(f"occurs: {t1} in {t2}")
            return compose({t1.name: t2}, s)
        if isinstance(t2, TVar): return unify(t2, t1, s)
        if isinstance(t1, TFun) and isinstance(t2, TFun):
            s1 = unify(t1.param, t2.param, s)
            return unify(apply(s1, t1.ret), apply(s1, t2.ret), s1)
        raise TypeError(f"cannot unify {t1} with {t2}")

    # --- TypeScheme: ∀ quantified_vars. body ---
    @dataclass
    class TypeScheme:
        quantified: frozenset   # set of variable names
        body: object

        def instantiate(self):
            """Replace each quantified variable with a fresh one."""
            renaming = {v: TVar(fresh()) for v in self.quantified}
            return apply(renaming, self.body)

        def __str__(self):
            if not self.quantified: return str(self.body)
            qs = " ".join(sorted(self.quantified))
            return f"∀{qs}. {self.body}"

    def env_free_vars(env: dict) -> frozenset:
        """All free type variables mentioned in the environment."""
        result = frozenset()
        for t in env.values():
            if isinstance(t, TypeScheme):
                result |= free_vars(t.body) - t.quantified
            else:
                result |= free_vars(t)
        return result

    def generalize(env: dict, typ) -> TypeScheme:
        """Generalize typ over variables not free in env."""
        quantified = free_vars(typ) - env_free_vars(env)
        return TypeScheme(quantified, typ)

    # --- Polymorphic Algorithm W (only showing Let and Var changes) ---
    def infer_poly(expr, env, subst=None):
        if subst is None: subst = {}
        tag = expr[0]

        if tag == 'int':  return (subst, TInt)
        if tag == 'bool': return (subst, TBool)

        if tag == 'var':
            name = expr[1]
            t = env.get(name)
            if t is None: raise TypeError(f"unbound: {name!r}")
            if isinstance(t, TypeScheme):
                return (subst, t.instantiate())   # fresh copy for each use
            return (subst, apply(subst, t))

        if tag == 'fun':
            _, params, body = expr
            param_vars = {p: TVar(fresh()) for p in params}
            new_env = {**env, **param_vars}
            s1, ret = infer_poly(body, new_env, subst)
            ft = apply(s1, ret)
            for p in reversed(params):
                ft = TFun(apply(s1, param_vars[p]), ft)
            return (s1, ft)

        if tag == 'call':
            _, callee, args = expr
            s1, ct = infer_poly(callee, env, subst)
            s, arg_types = s1, []
            for arg in args:
                s, t = infer_poly(arg, env, s)
                arg_types.append(t)
            ret = TVar(fresh())
            expected = ret
            for t in reversed(arg_types): expected = TFun(t, expected)
            s2 = unify(ct, expected, s)
            return (s2, apply(s2, ret))

        if tag == 'binop':
            _, op, e1, e2 = expr
            s1, t1 = infer_poly(e1, env, subst)
            s2, t2 = infer_poly(e2, env, s1)
            if op == '+':
                s3 = unify(t1, TInt, s2); s4 = unify(t2, TInt, s3)
                return (s4, TInt)

        if tag == 'let_poly':   # use let_poly to distinguish
            _, name, val, body = expr
            s1, t1 = infer_poly(val, env, subst)
            # KEY: generalize before adding to env
            scheme = generalize({k: apply(s1, v) for k, v in env.items()},
                                 apply(s1, t1))
            new_env = {**env, name: scheme}
            s2, t2 = infer_poly(body, new_env, s1)
            return (s2, t2)

        raise ValueError(f"unknown: {expr!r}")

    # Test: let id = λx. x in (id(1), id(true)) - must type-check
    # id(1) uses id: Int -> Int
    # id(true) uses id: Bool -> Bool
    prog = ('let_poly', 'id',
            ('fun', ['x'], ('var', 'x')),
            ('call', ('var', 'id'), [('int', 42)]))

    s, t = infer_poly(prog, {})
    print(f"let id=λx.x in id(42) -> {t}")

    # Using id at Bool:
    prog2 = ('let_poly', 'id',
             ('fun', ['x'], ('var', 'x')),
             ('call', ('var', 'id'), [('bool', True)]))
    s, t = infer_poly(prog2, {})
    print(f"let id=λx.x in id(true) -> {t}")

    # Self-application (should fail - occurs check):
    try:
        infer_poly(('fun', ['f'], ('call', ('var', 'f'), [('var', 'f')])), {})
    except TypeError as e:
        print(f"self-application fails (expected): {e}")

    # Show that id has a polymorphic type:
    s, id_scheme = {}, TVar(fresh())
    base_env = {}
    s1, id_type = infer_poly(('fun', ['x'], ('var', 'x')), base_env)
    scheme = generalize(base_env, apply(s1, id_type))
    print(f"id's type scheme: {scheme}")

except Exception as e:
    print(f"[hm:poly] {e}")
    import traceback; traceback.print_exc()
```

---

## Phase 6: Error Messages

Good error messages include: the source line, the conflicting types, and context. Wrap every `TypeError` in a richer class:

```python
try:
    class TypeErrorMsg(Exception):
        def __init__(self, msg, line=None, context=None):
            self.msg = msg
            self.line = line
            self.context = context
            super().__init__(str(self))

        def __str__(self):
            parts = ["[TypeError]"]
            if self.line: parts.append(f"line {self.line}")
            if self.context: parts.append(f"in {self.context}")
            parts.append(self.msg)
            return " ".join(parts)

    def unify_with_context(t1, t2, subst, line=None, context=None):
        """Unify with a helpful error if it fails."""
        try:
            from itertools import count  # reuse unify from above conceptually
            # (would import from the actual module in real code)
            # Simplified version for demo:
            if str(t1) != str(t2) and 'α' not in str(t1) and 'α' not in str(t2):
                raise TypeError(f"cannot unify {t1} with {t2}")
            return subst
        except TypeError as e:
            raise TypeErrorMsg(
                f"expected {t1}, got {t2}",
                line=line,
                context=context)

    # Simulate an error from checking the condition of an if-statement
    try:
        unify_with_context("Int", "Bool", {}, line=7, context="condition of 'if'")
    except TypeErrorMsg as e:
        print(e)

    # Better: call-site context
    try:
        unify_with_context("Int", "Str", {}, line=12,
                           context="argument 1 of call to 'concat'")
    except TypeErrorMsg as e:
        print(e)

except Exception as e:
    print(f"[hm:errors] {e}")
    import traceback; traceback.print_exc()
```

---

## Phase 7: Putting It All Together

Here is the minimal complete HM inferencer that handles the Mini language's expression nodes:

| Mini node | Type rule |
|---|---|
| `IntLit` | `TInt` |
| `FloatLit` | `TFloat` (or `TInt` if simplified) |
| `StrLit` | `TStr` |
| `BoolLit` | `TBool` |
| `NilLit` | `TList(fresh())` |
| `Var(name)` | lookup in env; instantiate if TypeScheme |
| `BinOp('+', l, r)` | unify l=Int, r=Int -> Int (or overloaded for Str) |
| `BinOp('<', l, r)` | unify l=r=fresh TV -> Bool |
| `BinOp('and', l, r)` | unify l=r=Bool -> Bool |
| `UnaryOp('-', e)` | unify e=Int -> Int |
| `UnaryOp('not', e)` | unify e=Bool -> Bool |
| `IfStmt(c, t, e)` | unify c=Bool, unify t=e -> unified type |
| `LetStmt(x, val)` | infer val; generalize; add to env |
| `FunExpr(params, body)` | fresh vars for params; infer body -> TFun |
| `Call(f, args)` | infer f; infer args; unify f = arg1->...->ret |
| `ReturnStmt(e)` | infer e (return type handled at function level) |
| `PrintStmt(e)` | infer e (any type); return TNil |

**Threading substitutions correctly is the #1 implementation challenge.** Every call to `infer` takes the *current* `subst` and returns an *updated* subst. Use the returned substitution in all subsequent calls.

---

## Common Pitfalls

1. **Forgetting to apply the substitution before returning.** After unification, always do `apply(final_subst, the_type)` before returning from a branch.

2. **Not threading the substitution.** If you call `infer(e1, env, subst)` and get back `s1`, then call `infer(e2, env, subst)` (not `s1`), you lose constraints from the first inference.

3. **Generalizing too early.** Generalize only in `let` bindings, not at every variable use. Generalizing inside a function body produces unsound polymorphism.

4. **Missing occurs check.** Without it, `id(id)` would produce a circular type `α = α -> α`, and `apply` would loop forever.

5. **Mutating the environment.** The type environment should be immutable (use `{**env, name: scheme}` for extension); mutations cause inference to fail on later branches.

---

## Further Reading

- Damas, Luis and Milner, Robin. "Principal Type-Schemes for Functional Programs" (POPL 1982). The original HM paper; 9 pages, completely readable.
- Cardelli, Luca. "Basic Polymorphic Typechecking" (1987, free online). A tutorial implementation much like this one, in Pascal.
- The Tree-Walking Interpreter assignment's static-typing direction (https://www.billmongan.com/Ursinus-CS374/Assignments/Interpreter): apply this tutorial to your language's AST.
- Pierce, Benjamin C. *Types and Programming Languages*, Chapters 22-23. The rigorous treatment.
