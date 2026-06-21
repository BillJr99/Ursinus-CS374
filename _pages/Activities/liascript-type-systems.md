# Type Systems: From Annotations to Inference

<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://github.com/BillJr99/Ursinus-CS374-Fall2026/blob/main/_pages/Activities/liascript-type-systems.md

import: https://raw.githubusercontent.com/liascript/CodeRunner/master/README.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

# Type Systems: From Annotations to Inference

*"A type system is a tractable syntactic method for proving the absence of certain program behaviors by classifying phrases according to the kinds of values they compute."* — Benjamin Pierce, *Types and Programming Languages*

A type is a **proof** carried in the program, checked by the compiler, that a value will be used consistently. When the checker passes, you have a machine-verified claim that the program is free of entire classes of errors — not just the errors you thought to test for, but all errors of that shape. This module traces the design space: from **dynamic typing** (types checked at runtime), through **static typing** (types checked at compile time), to **type inference** (types deduced by the compiler without annotations), to the beautiful algorithm at the heart of Haskell's type system — **Hindley-Milner**, the method that lets you write:

```haskell
map f xs = foldr (\x acc -> f x : acc) [] xs
```

without a single type annotation and have the compiler prove that `map :: (a -> b) -> [a] -> [b]` for *every* type `a` and `b`.

---

## Directions

Work in your POGIL team. Solo sections are for individual reflection first; group sections require all four roles.

---

# Part I: Static vs. Dynamic Typing

## 1. The Core Tradeoff

**Dynamic typing** (Python, JavaScript, Ruby, Lisp): types are attached to *values* at runtime. A variable has no type; its current value does. Type errors are caught when the offending operation actually runs.

**Static typing** (Java, Haskell, Rust, TypeScript): types are attached to *expressions* at compile time. A variable has a declared (or inferred) type; the compiler verifies consistency before the program runs. Type errors are caught before any execution.

```python
# Dynamic typing: this runs without error until the bad line
def add(a, b):
    return a + b

print(add(1, 2))        # 3 — fine
print(add("a", "b"))    # "ab" — also fine! + is overloaded
print(add(1, "hello"))  # TypeError at runtime: unsupported operand types
```

```
-- Static typing (Haskell): this fails at COMPILE time, before any execution
-- add :: Int -> Int -> Int
-- add a b = a + b
-- main = putStrLn (add 1 "hello")
-- Error: Couldn't match type '[Char]' with 'Int'
-- Expected type: Int, Actual type: String
```

---

### Model 1: Type Error Timing

```python
# When does Python catch this error? Trace the execution.

def always_fails(x):
    return x + 1   # will fail if x is not a number

def sometimes_called(flag, x):
    if flag:
        return always_fails(x)
    return 42

# This line is fine:
print(sometimes_called(False, "hello"))   # 42

# This line fails at runtime:
try:
    print(sometimes_called(True, "hello"))
except TypeError as e:
    print(f"[TypeError] {e}")

# The bug was already in the code when we ran line 1.
# A static type checker would have flagged it before line 1 ran.
```

### Critical Thinking Questions — *Solo*

1. In the `sometimes_called` function, the bug is present whether or not `flag` is `True`. Under dynamic typing, when is the bug discovered? Under static typing, when would it be discovered?
2. Name three program behaviors that a type system cannot detect (i.e., programs that type-check but are still wrong).
3. Python has `typing.py` with annotations: `def always_fails(x: int) -> int`. These are not enforced by Python at runtime, but tools like `mypy` check them statically. Is this static typing, dynamic typing, or something in between? What does the existence of these tools suggest about the tradeoff?

---

## 2. Type Inference: Types Without Annotations

**Type inference** is the ability to deduce a type from context without the programmer writing it. Every language has some: even Java infers the type of a local variable with `var x = 3` (Java 10+). Full inference — where the programmer writes almost no type annotations — is the achievement of Hindley-Milner.

```python
# Python's runtime cannot infer types, but we can reason about them.
# What is the type of each expression?

x = 3            # int
y = 3.14         # float
z = x + y        # float (implicit promotion)
f = lambda a: a  # for every type T, T -> T (polymorphic)
g = lambda a: a + 1  # int -> int (because + 1 constrains a to int)
h = lambda a: len(a) # for sequences: list/str/... -> int
```

```haskell
-- Haskell's compiler deduces ALL of these without a single annotation:
x = 3          -- x :: Num a => a
y = 3.14       -- y :: Fractional a => a
f = \a -> a    -- f :: a -> a          (id)
g = \a -> a+1  -- g :: Num a => a -> a
h = length     -- h :: [a] -> Int
compose f g x = f (g x)  -- compose :: (b -> c) -> (a -> b) -> a -> c
```

---

# Part II: The Hindley-Milner Algorithm

## 3. Types as Terms

In Hindley-Milner, **types** are first-class objects, just like lambda terms:

$$
\tau ::= \alpha \mid T \mid \tau_1 \to \tau_2 \mid T[\tau_1, \ldots, \tau_n]
$$

- $\alpha, \beta, \gamma, \ldots$ are **type variables** (unknown types)
- $\mathbf{Int}, \mathbf{Bool}, \mathbf{String}$ are **type constants**
- $\tau_1 \to \tau_2$ is a **function type** (input $\tau_1$, output $\tau_2$)
- $\mathbf{List}[\tau]$, $\mathbf{Maybe}[\tau]$ are **parameterized types**

A **type scheme** (or polytype) $\forall \alpha.\ \tau$ means "for all types $\alpha$, this has type $\tau$." The identity function `id :: forall a. a -> a` says: whatever type you hand me, I return the same type.

## 4. Unification: Solving Type Equations

**Unification** is the algorithm that, given two type terms, finds a substitution (a mapping from type variables to types) that makes them equal.

$$
\text{unify}(\alpha \to \mathbf{Int}, \ \mathbf{Bool} \to \beta) \Rightarrow \{\alpha \mapsto \mathbf{Bool},\ \beta \mapsto \mathbf{Int}\}
$$

**Unification fails** if the terms have incompatible structure:

$$
\text{unify}(\mathbf{Int}, \ \mathbf{Bool}) \Rightarrow \text{fail}
$$

$$
\text{unify}(\alpha, \ \alpha \to \alpha) \Rightarrow \text{fail (occurs check)}
$$

The **occurs check** prevents the infinite type $\alpha = \alpha \to \alpha$, which would require an infinitely deep type.

```python
# Unification in Python

class TypeVar:
    def __init__(self, name): self.name = name
    def __repr__(self): return self.name

class TypeConst:
    def __init__(self, name): self.name = name
    def __repr__(self): return self.name

class FuncType:
    def __init__(self, inp, out): self.inp = inp; self.out = out
    def __repr__(self): return f"({self.inp} -> {self.out})"

Int  = TypeConst("Int")
Bool = TypeConst("Bool")

def occurs(var, typ):
    """Does type variable `var` appear in `typ`? (Occurs check)"""
    if isinstance(typ, TypeVar):   return typ.name == var.name
    if isinstance(typ, TypeConst): return False
    if isinstance(typ, FuncType):  return occurs(var, typ.inp) or occurs(var, typ.out)
    return False

def apply_subst(subst, typ):
    """Apply a substitution dict to a type."""
    if isinstance(typ, TypeVar):
        return apply_subst(subst, subst[typ.name]) if typ.name in subst else typ
    if isinstance(typ, TypeConst):
        return typ
    if isinstance(typ, FuncType):
        return FuncType(apply_subst(subst, typ.inp), apply_subst(subst, typ.out))
    return typ

def unify(t1, t2, subst=None):
    """Return a substitution that unifies t1 and t2, or raise TypeError."""
    if subst is None: subst = {}
    t1 = apply_subst(subst, t1)
    t2 = apply_subst(subst, t2)

    if isinstance(t1, TypeConst) and isinstance(t2, TypeConst):
        if t1.name == t2.name: return subst
        raise TypeError(f"Cannot unify {t1} with {t2}")

    if isinstance(t1, TypeVar):
        if isinstance(t2, TypeVar) and t1.name == t2.name: return subst
        if occurs(t1, t2): raise TypeError(f"Occurs check: {t1} in {t2}")
        subst[t1.name] = t2; return subst

    if isinstance(t2, TypeVar):
        return unify(t2, t1, subst)

    if isinstance(t1, FuncType) and isinstance(t2, FuncType):
        subst = unify(t1.inp, t2.inp, subst)
        return unify(apply_subst(subst, t1.out), apply_subst(subst, t2.out), subst)

    raise TypeError(f"Cannot unify {t1} with {t2}")

# Examples
a, b = TypeVar("α"), TypeVar("β")

# unify(α -> Int, Bool -> β)  =>  {α: Bool, β: Int}
result = unify(FuncType(a, Int), FuncType(Bool, b))
print("Subst:", result)   # {'α': Bool, 'β': Int}

# unify(Int, Bool) => fail
try:
    unify(Int, Bool)
except TypeError as e:
    print("Expected failure:", e)

# occurs check: unify(α, α -> α) => fail
try:
    unify(a, FuncType(a, a))
except TypeError as e:
    print("Occurs check failure:", e)
```

---

## 5. Algorithm W: Inferring Types for Lambda Expressions

**Algorithm W** (Damas and Milner, 1982) takes an expression and an environment mapping variables to type schemes, and returns the most general type for the expression along with the substitution needed.

```python
# Simplified Algorithm W for our Mini language AST

from dataclasses import dataclass
from typing import Dict, Tuple

class TypeScheme:
    def __init__(self, bound_vars, typ):
        self.bound_vars = bound_vars  # list of TypeVar names
        self.typ = typ

    def instantiate(self, fresh_var):
        """Replace bound vars with fresh type variables."""
        subst = {v: fresh_var(v) for v in self.bound_vars}
        return apply_subst(subst, self.typ)

    def __repr__(self):
        if self.bound_vars:
            return f"∀{','.join(self.bound_vars)}.{self.typ}"
        return str(self.typ)

counter = [0]
def fresh():
    counter[0] += 1
    return TypeVar(f"t{counter[0]}")

def generalize(env_vars, typ):
    """Create a type scheme by universally quantifying free variables not in env."""
    free_in_type = free_type_vars(typ)
    free_in_env  = set().union(*(free_type_vars(t) for t in env_vars))
    quantified   = free_in_type - free_in_env
    return TypeScheme(list(quantified), typ)

def free_type_vars(typ):
    if isinstance(typ, TypeVar):   return {typ.name}
    if isinstance(typ, TypeConst): return set()
    if isinstance(typ, FuncType):  return free_type_vars(typ.inp) | free_type_vars(typ.out)
    return set()

# W for simple expressions
def infer(node, env):
    """
    Returns (substitution, type) for node given type environment env.
    env maps variable names to TypeScheme.
    """
    from ast_nodes import Num, Bool, Var, BinOp, Fun, App, Let

    if isinstance(node, Num):
        return {}, Int
    if isinstance(node, Bool):
        return {}, Bool
    if isinstance(node, Var):
        if node.name not in env:
            raise TypeError(f"[typecheck] Unbound variable: {node.name}")
        return {}, env[node.name].instantiate(lambda v: fresh())
    if isinstance(node, Fun):
        param_type = fresh()
        new_env    = {**env, node.param: TypeScheme([], param_type)}
        s, body_type = infer(node.body, new_env)
        return s, FuncType(apply_subst(s, param_type), body_type)
    if isinstance(node, App):
        s1, func_type = infer(node.func, env)
        s2, arg_type  = infer(node.arg,  {k: TypeScheme(v.bound_vars, apply_subst(s1, v.typ))
                                           for k, v in env.items()})
        result_type = fresh()
        s3 = unify(apply_subst(s2, func_type), FuncType(arg_type, result_type))
        combined = {**s1, **s2, **s3}
        return combined, apply_subst(combined, result_type)
    if isinstance(node, Let):
        s1, val_type = infer(node.value, env)
        scheme       = generalize(set(apply_subst(s1, v.typ) for v in env.values()), val_type)
        new_env      = {**{k: TypeScheme(v.bound_vars, apply_subst(s1, v.typ)) for k, v in env.items()},
                        node.name: scheme}
        s2, body_type = infer(node.body, new_env)
        return {**s1, **s2}, body_type
    raise TypeError(f"[typecheck] Unknown node: {type(node).__name__}")

print("Algorithm W defined.")
```

---

[[MC]]
The type of `map` in Haskell is `(a -> b) -> [a] -> [b]`. The type variable `a` can be instantiated to `Int`, making the type `(Int -> b) -> [Int] -> [b]`. This is called:

- (x) Parametric polymorphism (generics): the same code works for all types; the type variables are placeholders for any type.
- ( ) Ad-hoc polymorphism (overloading): the function has different implementations for different types.
- ( ) Subtype polymorphism (inheritance): the type variables range over subtypes of a base class.
- ( ) Type coercion: integers are automatically converted to match the type variable.

---

## 6. Type Errors as Proof Failures

When the type checker rejects a program, it is not arbitrarily strict — it has found a proof that the program **cannot be correct** under the type discipline. The error message is a witness to the inconsistency.

```python
# Simulating what a type checker would say about a common bug

# "Bug": applying a non-function
# Python: crashes at runtime
try:
    x = 5
    result = x(3)   # TypeError: 'int' object is not callable
except TypeError as e:
    print(f"Runtime: {e}")

# Haskell equivalent (conceptual):
# x :: Int
# x 3  =>  type error: "Int" is not a function
# The type checker knows Int cannot be applied to anything,
# because Int has no instance of the function arrow (->) type.

# What the occurs check prevents:
# If we allowed α = α -> α, then:
#   (λx. x x) :: α -> α  (applying x to x requires α = α -> α)
# This type has no finite representation.
# Languages that allow this (System U) are not normalizing:
# they allow non-terminating programs to type-check.
print("Type error examples shown.")
```

---

## 7. Exercises

1. **Unification by hand.** Solve each unification problem, showing the substitution or explaining the failure:
   - $\text{unify}(\alpha \to \beta, \ \mathbf{Int} \to \mathbf{Bool})$
   - $\text{unify}(\alpha \to \alpha, \ \mathbf{Int} \to \beta)$
   - $\text{unify}((\alpha \to \beta) \to \gamma, \ (\mathbf{Int} \to \beta) \to (\mathbf{Bool} \to \mathbf{String}))$
   - $\text{unify}(\alpha, \ \mathbf{List}[\alpha])$ — why does this fail?

2. **Type derivation.** Derive the type of `fun f -> fun x -> f (f x)` using Algorithm W (on paper, not code). What is the most general type? This is the Church numeral 2.

3. **Add type checking to your interpreter.** Implement a `TypeChecker` class (using the `Visitor` pattern from the transpiler module) that annotates each AST node with its inferred type, using the unification algorithm from Section 4. Your type checker should report type errors with location information before evaluation begins. Test it on: `(fun x -> x + 1) true` (type error) and `let f = fun x -> x in f 1 + f 2` (polymorphic let, should type-check).

4. **Compare error messages.** Write a program in both Python and Java that applies a non-function to an argument. Run both. Compare the error messages: which is more informative? Which catches the error earlier? Which gives the programmer more information about *why* the error occurred?

5. **Hindley-Milner in Haskell.** Load GHCi (`ghci`). Type `:t map`, `:t fst`, `:t flip`, `:t ($)`. For each, explain in English what the universally-quantified type variables mean, and give two concrete instantiations (e.g., `map` can be `(Int -> String) -> [Int] -> [String]` or `(Bool -> Char) -> [Bool] -> [Char]`).

---

## 8. Further Reading

- Pierce, Benjamin C. *Types and Programming Languages* (MIT Press, 2002). The standard reference. Chapters 9–22 cover simply-typed lambda calculus, subtyping, and System F.
- Damas, Luis and Robin Milner. "Principal Type-Schemes for Functional Programs." *POPL '82*. The original Algorithm W paper; 7 pages.
- Cardelli, Luca and Peter Wegner. "On Understanding Types, Data Abstraction, and Polymorphism." *ACM Computing Surveys* 17(4), 1985. The definitive taxonomy of type-system concepts.
- Heeren, Bastiaan, Jurriaan Hage, and Doaitse Swierstra. "Helium, for Learning Haskell." *Haskell Workshop*, 2003. How to give type errors that help beginners rather than intimidating them.
