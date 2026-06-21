# Operational Semantics: Specifying Languages with Inference Rules
<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://github.com/BillJr99/Ursinus-CS374-Fall2026/blob/gh-pages/_pages/Activities/liascript-operational-semantics.md or locally via https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374-Fall2026/gh-pages/_pages/Activities/liascript-operational-semantics.md

import: https://raw.githubusercontent.com/liascript/CodeRunner/master/README.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

# Operational Semantics: Specifying Languages with Inference Rules

When you write an interpreter, you are making decisions about what programs *mean* — but those decisions live buried in Python code, not in a form anyone else can easily check or reason about. Operational semantics is like a referee's rulebook for a programming language: it specifies exactly what each syntactic construct *does*, step by step, so there is no ambiguity about the language's behavior independent of any particular implementation. By the end of this activity you will be able to read and write these rules and see exactly how they map onto the evaluator you have already built.

## Learning Goals

By the end of this activity, you will be able to:

- Define the components of an inference rule (premises, conclusion, axiom) and interpret inference rule notation correctly
- Construct big-step derivation trees for arithmetic and conditional expressions using big-step (natural) semantics rules
- Trace small-step reduction sequences for expressions, identifying each intermediate configuration
- Compare big-step and small-step operational semantics and explain which style aligns more closely with a tree-walking interpreter
- Analyze the connection between operational semantics rules and the corresponding cases in an interpreter's `eval` function

Your interpreter is an implementation of a language — but implementations can have bugs. A **formal semantics** is a mathematical specification of the language that is separate from any implementation: you check your interpreter against the semantics, not the other way around. Today we study **operational semantics**, the dominant style in programming language theory, which defines meaning by specifying computation as a set of formal **inference rules** over program configurations. The arc: **configurations → big-step semantics → small-step semantics → connecting to your evaluator → where semantics and type systems meet**.

> **Before You Begin:** This activity assumes you can:
> - Read and trace through a recursive tree-walking interpreter (your Mini evaluator from earlier assignments)
> - Understand environments as mappings from variable names to values, and explain what variable lookup and extension mean
> - Recognize the structure of a lambda expression and explain how closures capture their defining environment
> - Write simple mathematical proofs by cases (e.g., case analysis on which constructor an expression uses)
> If any of these feel shaky, review them first.

---

## Directions and Group Roles

Work in your POGIL team with rotated roles (**Manager**, **Recorder**, **Presenter**, **Reflector**). Today is a pencil-and-paper day: every derivation is written as an inference tree, checked by another teammate. The Recorder photographs derivation trees for the discussion board. After class, respond to the reflective prompt individually in your notebook.

---

# Part I: Inference Rules

## 1. The Notation

An **inference rule** has the form:

$$
\frac{\text{premise}_1 \quad \text{premise}_2 \quad \cdots}{\text{conclusion}} \quad [\text{Rule Name}]
$$

Read it: "if all premises hold, then the conclusion holds." An **axiom** is a rule with no premises (an always-true conclusion, written with nothing above the line). A **derivation** (or proof tree) builds up a conclusion from axioms using the rules, like a mathematical proof.

**Notation for expression evaluation:** $\langle e, \sigma \rangle \Downarrow v$ means "expression $e$ in environment $\sigma$ evaluates to value $v$." (Some texts write $\sigma \vdash e \Rightarrow v$.) The environment $\sigma$ is a partial function from variable names to values.

**Notation quick-reference — formal symbol to plain English:**

| Notation | Meaning |
|----------|---------|
| `Γ ⊢ e : τ` | "In type environment Γ, expression e has type τ" |
| `⟨e, σ⟩ ⇓ v` | "Expression e, evaluated in environment σ, produces final value v" (big-step) |
| `⟨e, σ⟩ → ⟨e', σ'⟩` | "Expression e reduces to e' in one step, updating the environment" (small-step) |
| `→*` | Zero or more small-step reduction steps |
| `[x ↦ v]e` | "Substitute v for every free occurrence of x in expression e" |
| `σ[x ↦ v]` | "The environment σ extended so that x now maps to v" |
| `λx. e` | "A function with parameter x and body e" |
| Horizontal bar | "If everything above the bar holds, then the thing below the bar holds" |

> **Watch out!** The notation $\Gamma \vdash e : \tau$ (type judgment, Part IV) looks very similar to $\langle e, \sigma \rangle \Downarrow v$ (value judgment, Parts II–III), but they are different kinds of relations. $\Gamma$ maps names to *types*; $\sigma$ maps names to *values*. One is used by the type checker; the other by the evaluator. Do not mix them up when building derivation trees.

---

# Part II: Big-Step (Natural) Semantics

**Intuition:** In this section we write down the exact rules your tree-walking interpreter already follows — just in mathematical notation instead of Python. Each rule corresponds to one `if`-branch in your `eval` function: the premises are the recursive calls, and the conclusion is what the whole expression evaluates to. As you read each rule, mentally map it onto the matching Python code you wrote.

## 2. Big-Step Rules for Mini

"Big-step" semantics (also called **natural semantics** or **evaluation semantics**) defines evaluation in one jump from expression to final value — matching the recursive structure of your tree-walking interpreter.

**Literals (axioms — no premises):**

$$
\frac{}{\langle n, \sigma \rangle \Downarrow n} \quad [\text{Num}]
\qquad
\frac{}{\langle \textbf{true}, \sigma \rangle \Downarrow \textbf{true}} \quad [\text{Bool-T}]
\qquad
\frac{}{\langle \textbf{false}, \sigma \rangle \Downarrow \textbf{false}} \quad [\text{Bool-F}]
$$

**Variable lookup:**

$$
\frac{\sigma(x) = v}{\langle x, \sigma \rangle \Downarrow v} \quad [\text{Var}]
$$

**Arithmetic:**

$$
\frac{\langle e_1, \sigma \rangle \Downarrow n_1 \quad \langle e_2, \sigma \rangle \Downarrow n_2 \quad n = n_1 + n_2}{\langle e_1 + e_2, \sigma \rangle \Downarrow n} \quad [\text{Add}]
$$

(Rules for $-, *, /$ are analogous.)

**Conditionals:**

$$
\frac{\langle e_1, \sigma \rangle \Downarrow \textbf{true} \quad \langle e_2, \sigma \rangle \Downarrow v}{\langle \textbf{if}\; e_1\; \textbf{then}\; e_2\; \textbf{else}\; e_3, \sigma \rangle \Downarrow v} \quad [\text{If-T}]
$$

$$
\frac{\langle e_1, \sigma \rangle \Downarrow \textbf{false} \quad \langle e_3, \sigma \rangle \Downarrow v}{\langle \textbf{if}\; e_1\; \textbf{then}\; e_2\; \textbf{else}\; e_3, \sigma \rangle \Downarrow v} \quad [\text{If-F}]
$$

**Let binding:**

$$
\frac{\langle e_1, \sigma \rangle \Downarrow v_1 \quad \langle e_2, \sigma[x \mapsto v_1] \rangle \Downarrow v_2}{\langle \textbf{let}\; x = e_1\; \textbf{in}\; e_2, \sigma \rangle \Downarrow v_2} \quad [\text{Let}]
$$

The notation $\sigma[x \mapsto v_1]$ means "the environment $\sigma$ extended with $x$ mapping to $v_1$."

**Function abstraction and application:**

$$
\frac{}{\langle \lambda x.\, e, \sigma \rangle \Downarrow \langle \lambda x.\, e, \sigma \rangle} \quad [\text{Lam}]
\qquad
\frac{\langle e_1, \sigma \rangle \Downarrow \langle \lambda x.\, e, \sigma' \rangle \quad \langle e_2, \sigma \rangle \Downarrow v_2 \quad \langle e, \sigma'[x \mapsto v_2] \rangle \Downarrow v}{\langle e_1\; e_2, \sigma \rangle \Downarrow v} \quad [\text{App}]
$$

Notice: $[\text{Lam}]$ says a lambda evaluates to a **closure** — the function expression paired with its defining environment $\sigma'$. $[\text{App}]$ uses $\sigma'$ (not $\sigma$) to extend — this is lexical scoping in the rule.

---

## Code Cell: Deriving a Rule Machine in Python

```python
try:
    # A "rule engine" that mirrors big-step semantics as Python recursive eval.
    # Each function corresponds exactly to one or more semantic rules.

    def eval_bs(expr, env):
        """Big-step evaluation: returns a value."""

        tag = expr[0]

        # [Num] — literal
        if tag == 'num':
            return expr[1]

        # [Bool-T], [Bool-F]
        if tag == 'bool':
            return expr[1]

        # [Var]
        if tag == 'var':
            name = expr[1]
            if name not in env:
                raise NameError(f"unbound variable '{name}'")
            return env[name]

        # [Add] (and analogous rules for -, *, /)
        if tag == 'binop':
            _, op, e1, e2 = expr
            v1 = eval_bs(e1, env)
            v2 = eval_bs(e2, env)
            return {'+': v1 + v2, '-': v1 - v2,
                    '*': v1 * v2, '/': v1 / v2}[op]

        # [If-T], [If-F]
        if tag == 'if':
            _, cond, then_e, else_e = expr
            cv = eval_bs(cond, env)
            return eval_bs(then_e, env) if cv else eval_bs(else_e, env)

        # [Let]
        if tag == 'let':
            _, name, e1, e2 = expr
            v1 = eval_bs(e1, env)
            return eval_bs(e2, {**env, name: v1})

        # [Lam]: evaluates to a closure (tuple of lambda node + captured env)
        if tag == 'lam':
            return ('closure', expr, env)

        # [App]: apply a closure
        if tag == 'app':
            _, e1, e2 = expr
            fn = eval_bs(e1, env)
            arg = eval_bs(e2, env)
            if fn[0] != 'closure':
                raise TypeError(f"not a function: {fn}")
            _, lam, closure_env = fn
            _, param, body = lam    # lam = ('lam', param, body)
            return eval_bs(body, {**closure_env, param: arg})

        raise ValueError(f"unknown expression: {expr!r}")

    # Test: (lambda x. x + 1)(5) = 6
    prog = ('app',
        ('lam', 'x', ('binop', '+', ('var', 'x'), ('num', 1))),
        ('num', 5))
    print("(λx. x+1)(5) =", eval_bs(prog, {}))

    # Test: let x = 3 in let y = 4 in x * y = 12
    prog2 = ('let', 'x', ('num', 3),
             ('let', 'y', ('num', 4),
              ('binop', '*', ('var', 'x'), ('var', 'y'))))
    print("let x=3 in let y=4 in x*y =", eval_bs(prog2, {}))

    # Test: if true then 1 else 2 = 1
    prog3 = ('if', ('bool', True), ('num', 1), ('num', 2))
    print("if true then 1 else 2 =", eval_bs(prog3, {}))

except Exception as e:
    print(f"[opsem:bigstep] {e}")
    import traceback; traceback.print_exc()
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

---

**Intuition:** A derivation tree is not something you *invent* — it is something you *discover* by asking, for each sub-expression, which rule applies and what its premises require. Start at the root (the whole expression), work downward through sub-expressions, and bottom out at axioms (leaves with no premises). The tree proves that the expression evaluates to the stated value.

> **Watch out!** Inference rules are not proofs you construct freely — they are rules you *apply*. A rule fires only when its premises are all derivable. You cannot choose to skip a premise or apply a rule "partially." If you cannot derive every premise of a rule, that rule does not apply for that expression. This is different from writing a proof by assumption — here, every step must be grounded in an axiom or a previously derived judgment.

## Model 1: Building Derivation Trees

### Worked Example: Derivation Tree for `(λx. x) 5`

This traces the complete big-step derivation for applying the identity function to 5, in an empty environment `{}`.

**Goal:** show `⟨(λx. x) 5, {}⟩ ⇓ 5`

We need to apply rule `[App]`, whose three premises are:
1. Evaluate the function expression `λx. x` in `{}`
2. Evaluate the argument `5` in `{}`
3. Evaluate the body in the extended closure environment

**Premise 1 — evaluate the function:** By `[Lam]` (an axiom):

```
─────────────────────────────────────── [Lam]
⟨λx. x, {}⟩ ⇓ ⟨λx. x, {}⟩   (a closure)
```

**Premise 2 — evaluate the argument:** By `[Num]` (an axiom):

```
─────────────────── [Num]
⟨5, {}⟩ ⇓ 5
```

**Premise 3 — evaluate the body in the extended environment:** The closure environment is `{}`, extended with `x ↦ 5`, giving `{x ↦ 5}`. The body is `x`. By `[Var]`:

```
{x ↦ 5}(x) = 5
─────────────────────────── [Var]
⟨x, {x ↦ 5}⟩ ⇓ 5
```

**Putting it all together with `[App]`:**

```
──────────────────────────── [Lam]    ─────────────── [Num]    ─────────────────────────── [Var]
⟨λx. x, {}⟩ ⇓ ⟨λx. x, {}⟩          ⟨5, {}⟩ ⇓ 5             ⟨x, {x ↦ 5}⟩ ⇓ 5
─────────────────────────────────────────────────────────────────────────────────────────── [App]
⟨(λx. x) 5, {}⟩ ⇓ 5
```

The three leaves (axioms) are at the top; the root conclusion is at the bottom. Every step cites its rule name in brackets.

> **Watch out!** Notice that `[App]` uses the closure's captured environment `{}` (called `σ'` in the rule) to extend for the function body — **not** the call-site environment. For this simple example they happen to be the same (`{}`), but if the function had been defined inside a `let` binding that added variables, `σ'` would include those variables and the call-site environment would not. This asymmetry is exactly what enforces lexical (static) scoping.

### Critical Thinking Questions

1. Write the complete big-step derivation tree (using the rules above) for `(2 + 3) * 4` in an empty environment. Label every inference rule used. (The tree should have 3 leaves: two $[\text{Num}]$ axioms for 2 and 3 feeding into one $[\text{Add}]$, which feeds into the $[\text{Mul}]$ with the $[\text{Num}]$ axiom for 4.)

2. Derive `let x = 5 in x + 1` step by step. Show: (a) how `5` is evaluated by $[\text{Num}]$; (b) how `x + 1` is evaluated in the extended environment $\{x \mapsto 5\}$; (c) the final $[\text{Let}]$ rule that combines them.

3. The $[\text{App}]$ rule evaluates the argument before substituting into the function body. What evaluation strategy does this implement — call-by-value, call-by-name, or call-by-need? How would you change the rule to implement call-by-name?

4. The $[\text{Lam}]$ rule says `λx. e` evaluates to a *closure* `(λx. e, σ)` in the *current* environment. The $[\text{App}]$ rule then uses `σ'` (the closure's environment) for the function body, not the call site's environment `σ`. Write a 2-sentence explanation of why this implements **lexical scoping** rather than **dynamic scoping**.

---

# Part III: Small-Step (Structural) Semantics

**Intuition:** Rather than jumping straight from expression to final value, small-step semantics describes one tiny reduction at a time — like watching a computation frame-by-frame in a debugger. Each step rewrites the expression slightly closer to a value. The rules specify not just *what* to reduce, but also *which* sub-expression to reduce first, which is what gives the language a well-defined evaluation order.

## 3. One Step at a Time

**Small-step semantics** (also called **structural operational semantics**, SOS, or reduction semantics) describes computation as a sequence of single-step reductions. Instead of $\langle e, \sigma \rangle \Downarrow v$, we write $\langle e, \sigma \rangle \to \langle e', \sigma' \rangle$ (one reduction step) and $\to^*$ for zero or more steps. A term is in **normal form** when no rule applies.

Small-step semantics is more suitable for describing:
- Concurrent programs (interleaving of steps)
- Infinite loops (distinguished from "no value" — a loop takes infinitely many steps)
- Side effects (each step can modify the environment)

**Small-step rules for arithmetic:**

$$
\frac{}{\langle n_1 + n_2, \sigma \rangle \to \langle n_1 + n_2, \sigma \rangle \to \langle n, \sigma \rangle} \quad [\text{Add-Reduce}]
$$

where both $n_1$ and $n_2$ are already numeric values, and $n = n_1 + n_2$.

For non-values (when we must first reduce a sub-expression):

$$
\frac{\langle e_1, \sigma \rangle \to \langle e_1', \sigma' \rangle}{\langle e_1 + e_2, \sigma \rangle \to \langle e_1' + e_2, \sigma' \rangle} \quad [\text{Add-L}]
$$

$$
\frac{\langle e_2, \sigma \rangle \to \langle e_2', \sigma' \rangle}{\langle n_1 + e_2, \sigma \rangle \to \langle n_1 + e_2', \sigma' \rangle} \quad [\text{Add-R}]
$$

(where $n_1$ is already a value — $[\text{Add-R}]$ applies only once the left is a value.)

**Sequencing:** in small-step, `let x = e₁ in e₂` first reduces `e₁`:

$$
\frac{\langle e_1, \sigma \rangle \to \langle e_1', \sigma' \rangle}{\langle \textbf{let}\; x = e_1\; \textbf{in}\; e_2, \sigma \rangle \to \langle \textbf{let}\; x = e_1'\; \textbf{in}\; e_2, \sigma' \rangle} \quad [\text{Let-Step}]
$$

$$
\frac{}{\langle \textbf{let}\; x = v\; \textbf{in}\; e_2, \sigma \rangle \to \langle e_2, \sigma[x \mapsto v] \rangle} \quad [\text{Let-Val}]
$$

---

## Code Cell: Small-Step Reducer

```python
try:
    def is_value(expr):
        return expr[0] in ('num', 'bool', 'closure')

    def step(expr, env):
        """One small-step reduction. Returns (new_expr, new_env) or None if normal form."""
        tag = expr[0]

        if is_value(expr):
            return None   # already a value; no step possible

        # Variable: look up (one-step)
        if tag == 'var':
            name = expr[1]
            if name not in env:
                raise NameError(f"unbound: {name!r}")
            return (env[name], env)   # Var-Lookup

        # Add-Reduce: both sides are values
        if tag == 'binop':
            _, op, e1, e2 = expr
            if is_value(e1) and is_value(e2):
                n1, n2 = e1[1], e2[1]
                result = {'+': n1+n2, '-': n1-n2,
                          '*': n1*n2, '/': n1/n2}[op]
                return (('num', result), env)   # BinOp-Reduce
            # Add-L: reduce left first
            if not is_value(e1):
                e1p, envp = step(e1, env)
                return (('binop', op, e1p, e2), envp)
            # Add-R: reduce right once left is a value
            e2p, envp = step(e2, env)
            return (('binop', op, e1, e2p), envp)

        # If-T / If-F: reduce condition first, then select branch
        if tag == 'if':
            _, cond, then_e, else_e = expr
            if not is_value(cond):
                cp, envp = step(cond, env)
                return (('if', cp, then_e, else_e), envp)
            return ((then_e if cond[1] else else_e), env)

        # Let-Step / Let-Val
        if tag == 'let':
            _, name, e1, body = expr
            if not is_value(e1):
                e1p, envp = step(e1, env)
                return (('let', name, e1p, body), envp)
            return (body, {**env, name: e1[1]})

        # Lam: a value (no step needed)
        if tag == 'lam':
            return (('closure', expr, env), env)

        # App-Step
        if tag == 'app':
            _, e1, e2 = expr
            if not is_value(e1):
                e1p, envp = step(e1, env)
                return (('app', e1p, e2), envp)
            if not is_value(e2):
                e2p, envp = step(e2, env)
                return (('app', e1, e2p), envp)
            # App-Beta: both sides are values
            fn = e1
            if fn[0] != 'closure':
                raise TypeError(f"not a function: {fn}")
            _, lam, closure_env = fn
            _, param, body = lam
            return (body, {**closure_env, param: e2[1]})

        raise ValueError(f"unknown: {expr!r}")

    def run_steps(expr, env, max_steps=30):
        """Run small-step until normal form; print each step."""
        print(f"  Initial: {expr}")
        for i in range(max_steps):
            result = step(expr, env)
            if result is None:
                print(f"  → (normal form)")
                return expr
            expr, env = result
            print(f"  → {expr}")
        print("  (max steps reached)")
        return expr

    # (1 + 2) * 3  →  3 * 3  →  9
    prog = ('binop', '*',
            ('binop', '+', ('num', 1), ('num', 2)),
            ('num', 3))
    print("Small-step trace for (1+2)*3:")
    run_steps(prog, {})
    print()

    # let x = 4 in x + 1
    prog2 = ('let', 'x', ('num', 4),
             ('binop', '+', ('var', 'x'), ('num', 1)))
    print("Small-step trace for let x=4 in x+1:")
    run_steps(prog2, {})

except Exception as e:
    print(f"[opsem:smallstep] {e}")
    import traceback; traceback.print_exc()
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

---

**Intuition:** In small-step derivations you are writing a *sequence* of configurations, not a tree. Each line shows one application of one rule, turning the current configuration into the next. The sequence ends when the expression is a value (normal form) or gets stuck. Compare this to the derivation tree from Model 1 — the tree captures the entire computation at once, while the sequence shows one reduction at a time.

> **Watch out!** Big-step and small-step semantics for the *same* language should agree on the *final value* for any terminating program, but they are not the same relation. Big-step says nothing about intermediate states. Small-step says nothing about the final value in one step — you must follow the whole sequence. Students often confuse "the two styles agree" with "they are interchangeable" — they are not: they serve different purposes and are used to prove different properties.

## Model 2: Small-Step Derivations

### Critical Thinking Questions

5. Write the full small-step reduction sequence for `(if true then 1 else 2) + 3`:
   - Step 1: reduce `if true then 1 else 2` to `1` (which rule?)
   - Step 2: reduce `1 + 3` to `4` (which rule?)
   Connect this to the evaluation order in your Python evaluator: does it match?

6. Big-step semantics and small-step semantics should *agree* on the final value for any terminating program. Why are there *two* semantics styles if they agree? Name one thing small-step can express that big-step cannot.

7. The $[\text{Add-L}]$ rule says: reduce the **left** sub-expression first. This is a **deterministic** choice — for each expression, at most one rule applies. What would happen if you had two rules, $[\text{Add-L}]$ and $[\text{Add-R}]$, that could both apply simultaneously? Would the program still be deterministic? How does the ordering in $[\text{Add-R}]$ (which requires $e_1$ to already be a value) prevent this?

8. An **infinite loop** in big-step has no derivation at all — there is simply no proof tree. In small-step, an infinite loop produces an infinite reduction sequence: `e → e' → e'' → ...` that never reaches a normal form. Which style distinguishes "no value" (infinite loop) from "error" (stuck state, like dividing by zero) more clearly?

---

# Part IV: Type Rules and Type Safety

**Intuition:** Type rules look exactly like evaluation rules — same inference-rule notation, same tree-building process — but instead of asking "what value does this expression produce?" they ask "what *type* does this expression have?" The payoff is the type safety theorem: if you can build a type derivation for a program, the program is guaranteed never to get stuck at runtime with a type mismatch.

## 4. Types as Proof Obligations

A **type system** is a set of inference rules over types instead of values. The judgment $\Gamma \vdash e : \tau$ means "in type environment $\Gamma$, expression $e$ has type $\tau$."

$$
\frac{}{\Gamma \vdash n : \text{Int}} \quad [\text{T-Num}]
\qquad
\frac{\Gamma(x) = \tau}{\Gamma \vdash x : \tau} \quad [\text{T-Var}]
$$

$$
\frac{\Gamma \vdash e_1 : \text{Int} \quad \Gamma \vdash e_2 : \text{Int}}{\Gamma \vdash e_1 + e_2 : \text{Int}} \quad [\text{T-Add}]
$$

$$
\frac{\Gamma \vdash e_1 : \text{Bool} \quad \Gamma \vdash e_2 : \tau \quad \Gamma \vdash e_3 : \tau}{\Gamma \vdash \textbf{if}\; e_1\; \textbf{then}\; e_2\; \textbf{else}\; e_3 : \tau} \quad [\text{T-If}]
$$

$$
\frac{\Gamma, x : \tau_1 \vdash e : \tau_2}{\Gamma \vdash \lambda x.\, e : \tau_1 \to \tau_2} \quad [\text{T-Lam}]
\qquad
\frac{\Gamma \vdash e_1 : \tau_1 \to \tau_2 \quad \Gamma \vdash e_2 : \tau_1}{\Gamma \vdash e_1\; e_2 : \tau_2} \quad [\text{T-App}]
$$

**Type safety** (the Milner-Wright theorem): if $\Gamma \vdash e : \tau$ (the expression is well-typed), then either $e$ evaluates to a value of type $\tau$, or it diverges. A well-typed program never *gets stuck* (reaches a state where no rule applies but the expression is not a value).

---

## Code Cell: Type-Checking as Inference Rules

```python
try:
    # A simple type checker implementing the inference rules above

    def typecheck(expr, type_env):
        """Return the type of expr, or raise TypeError."""
        tag = expr[0]

        # [T-Num]
        if tag == 'num':   return 'Int'
        if tag == 'bool':  return 'Bool'
        if tag == 'str':   return 'Str'

        # [T-Var]
        if tag == 'var':
            name = expr[1]
            if name not in type_env:
                raise TypeError(f"unbound variable '{name}'")
            return type_env[name]

        # [T-Add] and siblings
        if tag == 'binop':
            _, op, e1, e2 = expr
            t1 = typecheck(e1, type_env)
            t2 = typecheck(e2, type_env)
            if op in ('+', '-', '*', '/'):
                if t1 != 'Int':
                    raise TypeError(f"'{op}' requires Int, got {t1}")
                if t2 != 'Int':
                    raise TypeError(f"'{op}' requires Int, got {t2}")
                return 'Int'
            if op in ('<', '>', '==', '!=', '<=', '>='):
                if t1 != t2:
                    raise TypeError(f"comparison: {t1} vs {t2}")
                return 'Bool'

        # [T-If]
        if tag == 'if':
            _, cond, then_e, else_e = expr
            tc = typecheck(cond, type_env)
            if tc != 'Bool':
                raise TypeError(f"condition must be Bool, got {tc}")
            tt = typecheck(then_e, type_env)
            te = typecheck(else_e, type_env)
            if tt != te:
                raise TypeError(f"branches must match: {tt} vs {te}")
            return tt

        # [T-Let]
        if tag == 'let':
            _, name, e1, body = expr
            t1 = typecheck(e1, type_env)
            return typecheck(body, {**type_env, name: t1})

        # [T-Lam]: require a type annotation on the parameter
        if tag == 'lam':
            _, param, param_type, body = expr   # annotated lambda
            t2 = typecheck(body, {**type_env, param: param_type})
            return (param_type, '->', t2)   # function type as tuple

        # [T-App]
        if tag == 'app':
            _, e1, e2 = expr
            t1 = typecheck(e1, type_env)
            t2 = typecheck(e2, type_env)
            if not (isinstance(t1, tuple) and t1[1] == '->'):
                raise TypeError(f"not a function type: {t1}")
            param_t, _, ret_t = t1
            if param_t != t2:
                raise TypeError(f"argument: expected {param_t}, got {t2}")
            return ret_t

        raise ValueError(f"unknown: {expr!r}")

    # Well-typed: (λx:Int. x + 1)(5) : Int
    prog = ('app',
            ('lam', 'x', 'Int', ('binop', '+', ('var', 'x'), ('num', 1))),
            ('num', 5))
    print("type of (λx:Int. x+1)(5):", typecheck(prog, {}))

    # Well-typed: if true then 1 else 2 : Int
    prog2 = ('if', ('bool', True), ('num', 1), ('num', 2))
    print("type of if true then 1 else 2:", typecheck(prog2, {}))

    # Ill-typed: if 1 then 2 else 3 (Int as condition)
    try:
        typecheck(('if', ('num', 1), ('num', 2), ('num', 3)), {})
    except TypeError as e:
        print("type error (expected):", e)

    # Ill-typed: 1 + true
    try:
        typecheck(('binop', '+', ('num', 1), ('bool', True)), {})
    except TypeError as e:
        print("type error (expected):", e)

except Exception as e:
    print(f"[opsem:types] {e}")
    import traceback; traceback.print_exc()
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

---

**Intuition:** Type safety is often stated as two lemmas — *progress* (a well-typed expression is either a value or can take a step) and *preservation* (if a well-typed expression takes a step, the result is still well-typed at the same type). Together they guarantee that well-typed programs never get stuck. As you work through the questions below, try to state each argument as one of these two lemmas.

## Model 3: Types and Safety

[[MC]]
The type safety theorem says a well-typed program either evaluates to a value of the right type or diverges. It does NOT guarantee that the program:
- ( ) Produces a value of the declared type
- ( ) Terminates
- (x) Both: terminates AND produces the right type (it may still loop)
- ( ) Does not throw exceptions

### Critical Thinking Questions

9. The $[\text{T-If}]$ rule requires both branches to have the *same* type $\tau$. Why? Give an example of a program that would be accepted if this restriction were dropped, and show what would go wrong at runtime.

10. The $[\text{T-App}]$ rule unifies the function's parameter type with the argument's type. This is essentially one step of Hindley-Milner unification. Connect this to the type inference assignment: Algorithm W automates the process of figuring out what $\tau_1$ and $\tau_2$ must be from the code, rather than requiring annotations.

11. In the small-step semantics, a **stuck state** is a configuration where no rule applies and the expression is not a value (e.g., `true + 1`). Type safety says well-typed programs cannot get stuck. Prove this informally for the $[\text{T-Add}]$ case: if `e₁ + e₂` has type Int and both `e₁` and `e₂` are values, what type must each value have, and why can the Add-Reduce rule always apply?

---

# Part V: Exercises

1. **Derive the [App] rule.** Write the complete big-step derivation tree for the application `(λx. x * x)(3)` in an empty environment. The tree should have leaves for: the lambda (closure), the argument 3, the multiplication, and the sub-expressions.

2. **Add while-loops to big-step semantics.** The rule for `while cond do body` in big-step can be written by "unrolling" one iteration:
   $$
   \frac{\langle cond, \sigma \rangle \Downarrow \textbf{false}}{\langle \textbf{while}\; cond\; \textbf{do}\; body, \sigma \rangle \Downarrow \sigma} \quad [\text{While-F}]
   $$
   Write the $[\text{While-T}]$ rule for when the condition is true (hint: evaluate body, update environment, recurse on the while loop). What is the return value of a while loop in your Mini language?

3. **Short-circuit in small-step.** Your language's `&&` short-circuits: if the left is false, the right is not evaluated. Write the small-step rules for `&&`:
   - One rule when the left is `false` (immediately reduce to `false`)
   - One rule when the left is `true` (reduce to the right sub-expression)
   - One rule for reducing the left when it is not yet a value
   Verify: do these rules capture short-circuit semantics correctly?

4. **Big-step vs. small-step for recursion.** Consider a recursive function `let f = λn. if n==0 then 1 else n * f(n-1) in f(3)`. In big-step semantics, how does the rule for function application handle the recursive reference to `f` in its own body? (What must the closure capture?) Write the $[\text{Let}]$ rule for a *letrec* (recursive let) that solves this.

---

## Reflection Prompt

In your notebook: your Python interpreter implements big-step semantics by being a big-step evaluator — each Python function call corresponds to one semantic rule. Your type checker implements the type rules. Does writing the formal rules *before* the code make implementation easier? What bugs would you have avoided in your Mini assignments if you had formal rules to check against first? And: the Curry-Howard correspondence says type rules and proof rules are the same thing — does the $[\text{T-If}]$ rule above look like a logical inference rule to you now?

---

## Further Reading

- Winskel, Glynn. *The Formal Semantics of Programming Languages* (MIT Press, 1993). Chapters 2–4 are the standard treatment of big-step and small-step semantics; this course's notation follows Winskel.
- Wright, Andrew K. and Matthias Felleisen. "A Syntactic Approach to Type Soundness" (1994). The paper that introduced the "progress + preservation" proof method for type safety.
- Pierce, Benjamin C. *Types and Programming Languages* (MIT Press, 2002), Chapters 3–9. Covers both styles with full proofs.
- Plotkin, Gordon D. "A Structural Approach to Operational Semantics" (1981, Aarhus Tech Report). The foundational paper for small-step semantics.
- Online tool: PLT Redex — run your semantics as executable specifications in DrRacket: https://redex.racket-lang.org/
