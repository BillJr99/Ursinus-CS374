<!--
author:   CS374 Course Staff
email:    
version:  0.0.1
language: en
narrator: US English Female
comment:  Denotational semantics — giving mathematical meaning to programs through functions.
import:   https://raw.githubusercontent.com/liaScript/mermaid_template/master/README.md
link:     https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.3.0/css/all.min.css
-->

# Denotational Semantics: Programs as Mathematical Functions

> **"The meaning of a program is a function from inputs to outputs."**
>
> Denotational semantics gives us a way to assign a precise mathematical meaning — a *denotation* — to every program, independent of how any computer would execute it. Today you'll see how to define the meaning of a language mathematically, and why this matters for reasoning about programs.

## Directions and Roles

Work in groups of 3–4. Rotate roles every 20 minutes.

- **Facilitator**: Keeps discussion on track; ensures everyone contributes.
- **Recorder**: Writes down answers and code that the group agrees on.
- **Reporter**: Presents findings to the class; explains the group's reasoning.
- **Reflector**: Monitors group process; writes the reflection at the end.

---

## Model 1 — Three Ways to Define a Language

There are three main styles of formal semantics:

| Style | Defines meaning as... | Good for... |
|-------|----------------------|-------------|
| **Operational** | Reduction rules (how a machine steps) | Proving execution properties, implementing interpreters |
| **Denotational** | Mathematical functions (what programs *are*) | Compositional reasoning, equivalence proofs |
| **Axiomatic** | Pre/post-condition logic (what programs *guarantee*) | Program verification, Hoare logic |

In **denotational semantics**, we write a *semantic function* `⟦·⟧` that maps syntactic programs to mathematical objects:

```
⟦e⟧ : Env → Value
⟦s⟧ : Store → Store
```

The key property is **compositionality**: the meaning of a compound expression is defined entirely in terms of the meanings of its parts. `⟦e₁ + e₂⟧ = ⟦e₁⟧ + ⟦e₂⟧` — the meaning of an addition is the sum of the meanings.

**Critical Thinking Questions (CTQs)**

> **CTQ 1.1** Compositionality says "the meaning of a whole is a function of the meanings of its parts." Give an example where this is NOT true in natural language (e.g., idioms). Why doesn't this problem occur in programming languages?

> **CTQ 1.2** The operational semantics of a `while` loop requires a transition rule that "runs" the loop. How might you define the *denotational* meaning of a `while` loop without running anything?

> **CTQ 1.3** What does it mean to say two programs are "semantically equivalent" in the denotational sense?

---

## Model 2 — A Tiny Language and its Denotations

Consider a tiny arithmetic language **Arith** with the grammar:

```
e ::= n                  -- integer literal
    | x                  -- variable  
    | e₁ + e₂            -- addition
    | e₁ * e₂            -- multiplication
    | let x = e₁ in e₂  -- local binding
    | if e₁ then e₂ else e₃  -- conditional
```

**Domain**: the set of integers `ℤ`, plus a special `⊥` (bottom) for errors/non-termination.

**Environment**: `Env = Var → ℤ`  (a function from variables to integers)

**Semantic function** `⟦·⟧ : Arith → Env → ℤ`:

```
⟦n⟧ σ         = n                         (literal)
⟦x⟧ σ         = σ(x)                      (variable lookup)
⟦e₁ + e₂⟧ σ  = ⟦e₁⟧ σ + ⟦e₂⟧ σ          (addition)
⟦e₁ * e₂⟧ σ  = ⟦e₁⟧ σ × ⟦e₂⟧ σ          (multiplication)
⟦let x = e₁ in e₂⟧ σ = ⟦e₂⟧ (σ[x ↦ ⟦e₁⟧ σ])   (let: extend env)
⟦if e₁ then e₂ else e₃⟧ σ =
    ⟦e₂⟧ σ,  if ⟦e₁⟧ σ ≠ 0
    ⟦e₃⟧ σ,  if ⟦e₁⟧ σ = 0
```

Here `σ[x ↦ v]` means "the environment σ updated to map x to v."

Let's implement this in Python — the implementation IS the semantics:

```python  liascript
def arith_eval(expr, env):
    """Denotational evaluator for Arith.
    expr is a tuple-based AST; env is a dict."""
    match expr:
        case ('num', n):
            return n
        case ('var', x):
            if x not in env:
                raise ValueError(f"Unbound variable: {x}")
            return env[x]
        case ('add', e1, e2):
            return arith_eval(e1, env) + arith_eval(e2, env)
        case ('mul', e1, e2):
            return arith_eval(e1, env) * arith_eval(e2, env)
        case ('let', x, e1, e2):
            v1 = arith_eval(e1, env)
            new_env = {**env, x: v1}   # σ[x ↦ v1]
            return arith_eval(e2, new_env)
        case ('if', cond, then, else_):
            if arith_eval(cond, env) != 0:
                return arith_eval(then, env)
            else:
                return arith_eval(else_, env)

# Test: let x = 3 in let y = x + 1 in x * y
prog = ('let', 'x', ('num', 3),
          ('let', 'y', ('add', ('var', 'x'), ('num', 1)),
            ('mul', ('var', 'x'), ('var', 'y'))))
result = arith_eval(prog, {})
print(f"let x=3 in let y=x+1 in x*y = {result}")  # 3 * 4 = 12

# Test: if 1 then 42 else 0
result2 = arith_eval(('if', ('num', 1), ('num', 42), ('num', 0)), {})
print(f"if 1 then 42 else 0 = {result2}")  # 42
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

**CTQs**

> **CTQ 2.1** The denotational rule for `let x = e₁ in e₂` creates a *new* environment rather than mutating the existing one. What does this say about the semantics of variable binding in this language? Is this lexical or dynamic scope?

> **CTQ 2.2** Compare `arith_eval` with a typical interpreter. What's the key structural difference? (Hint: look at how recursion is used.)

> **CTQ 2.3** The semantic function `⟦·⟧` takes an *expression* and an *environment* and returns a *value*. What *type* would you assign to `⟦·⟧` in a typed language like Haskell?

---

## Model 3 — Adding State: Stores and Commands

The Arith language above is *pure* — no mutation. Now we add imperative features. The key idea: **commands** transform the *store* (memory).

```
c ::= x := e            -- assignment
    | c₁ ; c₂           -- sequence  
    | if e then c₁ else c₂   -- conditional command
    | while e do c       -- loop
    | skip               -- no-op
```

**Domain for commands**: `Cmd → Store → Store` (commands are *state transformers*)

```
⟦skip⟧ s              = s
⟦x := e⟧ s            = s[x ↦ ⟦e⟧ s]
⟦c₁ ; c₂⟧ s           = ⟦c₂⟧ (⟦c₁⟧ s)
⟦if e then c₁ else c₂⟧ s =
    ⟦c₁⟧ s,  if ⟦e⟧ s ≠ 0
    ⟦c₂⟧ s,  if ⟦e⟧ s = 0
```

The tricky case is `while`:

```
⟦while e do c⟧ =  fix(F)
  where F(f)(s) = if ⟦e⟧ s ≠ 0 then f(⟦c⟧ s) else s
```

This uses a **fixed point** — `while` is the *least fixed point* of the function `F`. The loop runs until the condition is false, and `fix` captures exactly that iteration mathematically.

```python  liascript
def cmd_eval(cmd, store):
    """Denotational evaluator for imperative commands.
    store is a dict (mutable, but we always return a new one)."""
    match cmd:
        case ('skip',):
            return dict(store)
        case ('assign', x, e):
            v = arith_eval(e, store)
            return {**store, x: v}
        case ('seq', c1, c2):
            s1 = cmd_eval(c1, store)
            return cmd_eval(c2, s1)
        case ('if_cmd', e, c1, c2):
            if arith_eval(e, store) != 0:
                return cmd_eval(c1, store)
            else:
                return cmd_eval(c2, store)
        case ('while', e, c):
            # Iterative fixed point — compute until convergence
            s = dict(store)
            for _ in range(10000):   # safety limit
                if arith_eval(e, s) == 0:
                    return s
                s = cmd_eval(c, s)
            raise RuntimeError("Loop did not terminate (limit reached)")

def arith_eval(expr, env):
    match expr:
        case ('num', n):        return n
        case ('var', x):        return env.get(x, 0)
        case ('add', e1, e2):   return arith_eval(e1, env) + arith_eval(e2, env)
        case ('mul', e1, e2):   return arith_eval(e1, env) * arith_eval(e2, env)
        case ('sub', e1, e2):   return arith_eval(e1, env) - arith_eval(e2, env)
        case ('neg_cmp', e):    return 0 if arith_eval(e, env) != 0 else 1
        case ('lte', e1, e2):   return 1 if arith_eval(e1, env) <= arith_eval(e2, env) else 0

# Compute factorial(5) iteratively: n=5, result=1, while n>0: result*=n; n-=1
factorial_prog = (
    'seq', ('assign', 'n', ('num', 5)),
    ('seq', ('assign', 'result', ('num', 1)),
     ('while', ('var', 'n'),
      ('seq', ('assign', 'result', ('mul', ('var', 'result'), ('var', 'n'))),
               ('assign', 'n', ('sub', ('var', 'n'), ('num', 1)))))))

final_store = cmd_eval(factorial_prog, {})
print(f"5! = {final_store['result']}")   # 120
print(f"Final store: {final_store}")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

**CTQs**

> **CTQ 3.1** The denotational meaning of a command is a function from stores to stores. What is the denotational meaning of a non-terminating loop (one that runs forever)? What mathematical object represents this? (Hint: `⊥` — bottom.)

> **CTQ 3.2** Sequence `c₁ ; c₂` is defined as function composition: `⟦c₁ ; c₂⟧ = ⟦c₂⟧ ∘ ⟦c₁⟧`. Write this using the standard Haskell composition operator `(.)`. What does this tell you about the relationship between sequential imperative programming and function composition?

> **CTQ 3.3** The `while` loop uses a "fixed point." Informally: a fixed point of `F` is a value `x` such that `F(x) = x`. If `F(f)(s) = if condition then f(body(s)) else s`, what does `F(identity)(s)` return? What does `F(F(identity))(s)` return? What pattern do you see?

---

## Model 4 — Domains and Partial Orders (The Math Behind Denotational Semantics)

Non-termination forces us to be careful. We can't just say "the meaning of a non-terminating program is undefined" — we need a mathematical object `⊥` ("bottom") that represents "no answer."

**Domain**: a set `D` with a partial order `⊑` ("approximates") where:
- `⊥ ⊑ d` for all `d ∈ D` (⊥ approximates everything)
- The order reflects "more information": `⊥` = no info, concrete values = full info

**Chain**: a sequence `d₀ ⊑ d₁ ⊑ d₂ ⊑ ...` of increasingly informative approximations

**Complete partial order (CPO)**: every chain has a least upper bound (lub) `⊔`

The meaning of `while` is built up as a chain:

```
f₀ = ⊥         (no iterations: always diverges)
f₁ = F(⊥)      (0 or 1 iterations)
f₂ = F(F(⊥))   (0, 1, or 2 iterations)
...
⟦while e do c⟧ = ⊔ₙ fₙ   (the limit of the chain)
```

```python  liascript
# Simulate the chain approximation of while-loop semantics
# Each approximation f_k handles at most k iterations

def make_approximation(k, e_fn, c_fn):
    """Build the k-th approximation of while e do c."""
    if k == 0:
        # f_0: always diverge (return None = ⊥)
        return lambda store: None
    else:
        f_prev = make_approximation(k - 1, e_fn, c_fn)
        def f_k(store):
            if e_fn(store) == 0:
                return store              # condition false: exit
            new_store = c_fn(store)
            return f_prev(new_store)     # run body, then apply previous approx
        return f_k

# countdown: n := n - 1, condition: n > 0
def condition(s): return s.get('n', 0)          # true while n != 0
def body(s): return {**s, 'n': s['n'] - 1}      # n := n - 1

print("Chain approximations for 'while n>0 do n:=n-1':")
for k in range(6):
    f = make_approximation(k, condition, body)
    result = f({'n': 3})
    print(f"  f_{k}({{'n': 3}}) = {result}")

# The true fixed point (least upper bound) handles all finite cases:
print("\nTrue semantics (least fixed point):")
import functools
def while_lfp(e_fn, c_fn):
    def run(store):
        s = dict(store)
        while e_fn(s) != 0:
            s = c_fn(s)
        return s
    return run

lfp = while_lfp(condition, body)
print(f"  lfp({{'n': 3}}) = {lfp({'n': 3})}")
print(f"  lfp({{'n': 0}}) = {lfp({'n': 0})}")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

**CTQs**

> **CTQ 4.1** Look at the chain output. At what `k` does `f_k({'n': 3})` first return a non-⊥ result? What does this tell you about how many iterations the loop runs on input `n=3`?

> **CTQ 4.2** If the loop runs forever (e.g., `while 1 do skip`), the chain `f_0, f_1, f_2, ...` is an infinite chain all equal to `⊥`. What is `⊔ₙ fₙ` in this case? Is this the right answer?

> **CTQ 4.3** The CPO approach was developed by Dana Scott and Christopher Strachey in the 1970s. Before this, there was no rigorous mathematical foundation for programming language semantics. Why does this matter for language design today?

---

## Model 5 — Denotational Semantics for Functions

Functions are the hardest part. In the denotational semantics of lambda calculus:

```
⟦λx.e⟧ σ  =  λv. ⟦e⟧ (σ[x ↦ v])
⟦e₁ e₂⟧ σ  =  (⟦e₁⟧ σ) (⟦e₂⟧ σ)
```

The denotation of a lambda is a *mathematical function*. The denotation of an application is *function application*. Perfect compositionality.

But what domain do functions live in? If `V` is the domain of values, then functions have type `V → V`. But that means `V` must contain `V → V` as a subset — a self-referential domain equation!

```
V ≅ ℤ + Bool + (V → V) + ...
```

Scott's breakthrough: **domain equations can be solved** using fixed points of domain constructors. The solution is a domain `D∞` where:

```
D∞ ≅ {⊥} + ℤ + Bool + (D∞ →_c D∞)    (continuous functions)
```

For our purposes, Python handles this automatically:

```python  liascript
# Denotational semantics for lambda calculus in Python
# Values ARE Python functions — the domain equation is solved by Python's object system

def denote(expr, env):
    """⟦expr⟧ env — denotational evaluation of lambda calculus expressions."""
    match expr:
        case ('num', n):
            return n
        case ('bool', b):
            return b
        case ('var', x):
            return env[x]
        case ('lam', x, body):
            # ⟦λx.e⟧ σ = λv. ⟦e⟧ (σ[x↦v])
            return lambda v: denote(body, {**env, x: v})
        case ('app', f, arg):
            # ⟦e1 e2⟧ σ = (⟦e1⟧ σ)(⟦e2⟧ σ)
            return denote(f, env)(denote(arg, env))
        case ('add', e1, e2):
            return denote(e1, env) + denote(e2, env)
        case ('mul', e1, e2):
            return denote(e1, env) * denote(e2, env)
        case ('sub', e1, e2):
            return denote(e1, env) - denote(e2, env)
        case ('if_e', cond, then_, else_):
            return denote(then_, env) if denote(cond, env) else denote(else_, env)
        case ('letrec', f, x, body, cont):
            # letrec f = λx.body in cont  — using Python's fixed-point trick
            def rec(*args):
                new_env = {**env, f: rec}
                return denote(('app', ('lam', x, body), args[0]), new_env)
            return denote(cont, {**env, f: rec})

# Church numeral 2 applied: (λf. λx. f(f(x))) (λy. y+1) 0 = 2
church_2 = ('lam', 'f', ('lam', 'x', ('app', ('var','f'), ('app', ('var','f'), ('var','x')))))
succ = ('lam', 'y', ('add', ('var','y'), ('num', 1)))
two = denote(('app', ('app', church_2, succ), ('num', 0)), {})
print(f"Church 2 applied to (+1) at 0 = {two}")   # 2

# Recursive factorial using letrec
fact_def = ('letrec', 'fact', 'n',
    ('if_e', ('var', 'n'),
        ('mul', ('var', 'n'), ('app', ('var', 'fact'), ('sub', ('var', 'n'), ('num', 1)))),
        ('num', 1)),
    ('app', ('var', 'fact'), ('num', 5)))

print(f"5! = {denote(fact_def, {})}")   # 120
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

**CTQs**

> **CTQ 5.1** The denotation of `(λf. λx. f(f(x)))` is a Python lambda that returns a lambda. Trace through `denote(church_2, {})`. What Python object is returned? What does calling it twice do?

> **CTQ 5.2** In the `letrec` case, `rec` references itself. This implements the fixed-point operator `Y` directly in the meta-language (Python). Compare this to the Y combinator from the lambda calculus activity. What are the similarities?

> **CTQ 5.3** If we replaced Python with a *pure* mathematical framework (no mutation, no self-reference in the host language), we would need `Y` to define recursion. Why is this not a problem in practice when building an interpreter?

---

## Multiple Choice

In denotational semantics, what does the "semantic function" `⟦·⟧` map?

    [( )] Machine state to machine state
    [( )] Tokens to parse trees
    [(x)] Syntactic programs to mathematical objects (functions, values, domains)
    [( )] Types to type judgments

---

The denotational meaning of `c₁ ; c₂` (sequence) is:

    [( )] Run c₁ and c₂ in parallel, then merge stores
    [(x)] Function composition: apply `⟦c₁⟧` to the store, then apply `⟦c₂⟧` to the result
    [( )] Run c₁, check for errors, then conditionally run c₂
    [( )] Concatenate the bytecode of c₁ and c₂

---

What is `⊥` (bottom) in domain theory?

    [(x)] The least element representing non-termination / no information
    [( )] The boolean value `False`
    [( )] An empty list
    [( )] A syntax error

---

Why does defining `⟦while e do c⟧` require a fixed point?

    [( )] Because loops are circular in memory
    [( )] Because `while` modifies a shared variable
    [(x)] Because the loop body can execute zero or more times — only the least fixed point captures all finite iteration depths plus non-termination
    [( )] Because sequential composition requires commutativity

---

## Exercises

### Exercise 1 — Denotational Meaning of Boolean Operators (15 min)

Extend the Arith evaluator with Boolean expressions:

```
b ::= true | false | e₁ = e₂ | e₁ < e₂ | b₁ ∧ b₂ | b₁ ∨ b₂ | ¬b
```

Write the semantic equations (mathematical notation) AND implement them in Python. Test on: `(3 + 1 = 4) ∧ ¬(2 < 1)`.

### Exercise 2 — Proving Program Equivalence (20 min)

Use the semantic equations to prove that these two programs are semantically equivalent (have the same denotation for all stores and environments):

```
Program 1:  x := x + 1; x := x + 1
Program 2:  x := x + 2
```

Show your work using the semantic equations for `assign` and `seq`.

### Exercise 3 — Non-Termination as ⊥ (20 min)

Consider the program `while 1 do skip` (infinite loop). 

1. Write the chain: `f₀(s)`, `f₁(s)`, `f₂(s)`, ... for this loop.
2. What is the least upper bound `⊔ₙ fₙ`?
3. Implement this using the `make_approximation` function from Model 4. What does `make_approximation(100, lambda s: 1, lambda s: s)({'x': 0})` return?
4. Why is `⊥` the *right* answer for a non-terminating program, rather than "undefined" or an exception?

### Exercise 4 — Denotational Semantics for Mini (30 min, harder)

The Mini language has closures and recursion. Write the denotational semantic equations for:

```
⟦fun(x) -> e⟧ σ  =  ?
⟦f(a)⟧ σ          =  ?
⟦let f(x) = e₁ in e₂⟧ σ  =  ?   (recursive definition)
```

Implement `denote_mini(expr, env)` extending Model 5's `denote` function to handle the tuple-based Mini AST. Test with:
- `(fun (x) -> x + 1)(41)` should give `42`
- Recursive `fact(5)` using `letrec` should give `120`

---

## Reflection

*(Write your answers individually, then discuss with your group.)*

1. **Operational vs. Denotational**: Your tree-walking Mini interpreter uses operational semantics (reduction rules). What would it mean to instead define Mini's semantics denotationally? What would change in the implementation?

2. **Equivalence**: The denotational approach lets us *prove* two programs equivalent by showing their denotations are equal functions. Give an example from your Mini programs where you might want to prove equivalence (e.g., proving an optimization is correct).

3. **Connection to Types**: In the Curry-Howard activity, we saw that "types are propositions." Denotational semantics adds another layer: "types are domains" (sets with structure). How do these two views connect?

---

## Further Reading

- **"Outline of a Mathematical Theory of Computation"** — Dana Scott (1970): foundational paper establishing domain theory
- **"The Denotational Semantics of Programming Languages"** — Tennent (1976): accessible introduction
- **"Semantics of Programming Languages"** — Gunter (1992): textbook treatment with CPOs
- **"Denotational Semantics"** — Schmidt (1986): free online at https://people.cs.ksu.edu/~schmidt/text/densem.html
- **TAPL Ch. 5** — The Untyped Lambda Calculus — Pierce: connects operational to denotational
- **Haskell's semantics** — bottom (`⊥`) is directly expressible: `undefined :: a`; GHC uses denotational reasoning for optimization via "free theorems"
