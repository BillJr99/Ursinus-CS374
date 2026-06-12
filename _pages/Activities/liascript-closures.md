# Closures and First-Class Functions
<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://github.com/BillJr99/Ursinus-CS374-Fall2026/blob/gh-pages/_pages/Activities/liascript-closures.md or locally via https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374/gh-pages/_pages/Activities/liascript-closures.md

import: https://raw.githubusercontent.com/liascript/CodeRunner/master/README.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

# Closures and First-Class Functions

Every thread of the semester knots together today: when a language with **first-class functions** and **static scope** lets a function escape the scope where it was born, the function must carry its birthplace with it. That bundle of code plus captured environment is a **closure**, the mechanism behind `make_adder`, behind every Church encoding you ran in Python, and behind the function feature your team may add to your interpreter. The arc: **the problem closures solve $\rightarrow$ the mechanism, drawn precisely $\rightarrow$ closures in your interpreter $\rightarrow$ the loop-variable trap**.

---

## Directions and Group Roles

Work in your POGIL team with rotated roles (**Manager**, **Recorder**, **Presenter**, **Reflector**). Consider each model and question individually first, then discuss with your group. The Recorder posts answers to the Class Activity Questions discussion board; the Presenter reports out areas of disagreement or alternative approaches. After class, respond to the reflective prompt individually in your notebook.

---

# Part I: The Problem and the Mechanism

## 1. A Function Outlives Its Scope

Recall `make_adder`:

```python
def make_adder(n):
    def adder(x):
        return x + n
    return adder

add5 = make_adder(5)
print(add5(10))      # 15... but make_adder returned long ago. Where does n live?
```

By the lifetime rules of the environments module, `make_adder`'s local scope should die at return, taking `n` with it, yet `add5` still finds `n = 5`. **The resolution: a function value is not just code; it is a closure, a pair of (code, defining environment)**, and when `adder` was created, it captured a reference to the environment where `n` was bound. That environment survives, not because of magic, but because something (the closure) still points to it: lifetime follows reachability.

**Calling a closure resurrects its birthplace.** The call `add5(10)` creates a fresh environment for the parameters (`x = 10`) whose **parent is the closure's captured environment**, not the caller's. The body's `n` resolves up the *captured* chain: this is static scoping enforced at runtime, and it is the entire difference between lexical and dynamic scope, implemented in one decision about which parent pointer to use.

$$
\text{closure} = \langle \text{params}, \text{body}, E_{\text{def}} \rangle
\qquad
\text{call: } E_{\text{call}} = \text{Environment}(\text{parent} = E_{\text{def}})
$$

---

## Model 1: Draw the Capture

### Critical Thinking Questions

1. Draw the environment diagram at `print(add5(10))`: the global frame, the (still-alive) `make_adder` frame holding `n = 5`, the call frame holding `x = 10`, and every parent arrow. Which arrow embodies "static scope"?
2. Run `add3 = make_adder(3)` too. How many `make_adder` environments now exist? What does each closure's captured pointer prove about whether closures *copy* or *reference* their environment?
3. Replay the scope module's `show`/`demo` program: explain in closure vocabulary why static scope printed 10, identifying precisely which environment `show`'s closure captured.
4. In the lambda calculus, $(\lambda n. \lambda x.\, x + n)\, 5$ reduces to $\lambda x.\, x + 5$ by *substitution*: the 5 is pasted in, and no environment exists. State the relationship: closures are an *implementation strategy* for what substitution *specifies*. Why might an interpreter prefer environments to literal substitution? (Think cost of copying large bodies.)

---

# Part II: Closures in Your Interpreter

## 2. Twenty Lines to First-Class Functions

Adding functions to your language requires: a `FunDef` node and a `Call` node from the parser; a `Closure` value created at definition time capturing the *current* environment; and a call rule that builds the new environment on the captured parent. The code is short because the environments module did the heavy lifting.

---

## Code Cell

```python
# First-class functions with closures, in the interpreter architecture.
# Assumes Environment from the environments module.

class FunDef:                        # fun name(params) { body }
    def __init__(self, name, params, body):
        self.name, self.params, self.body = name, params, body

class Call:                          # name(args...)
    def __init__(self, callee, args):
        self.callee, self.args = callee, args

class Closure:
    """A function VALUE: code plus the environment where it was defined."""
    def __init__(self, params, body, env):
        self.params, self.body, self.env = params, body, env

class ReturnSignal(Exception):
    def __init__(self, value): self.value = value

def execute_fundef(node, env):
    env.define(node.name, Closure(node.params, node.body, env))   # capture HERE

def eval_call(node, env, evaluate, execute):
    try:
        fn = evaluate(node.callee, env)
        if not isinstance(fn, Closure):
            raise TypeError("attempted to call a non-function value")
        if len(node.args) != len(fn.params):
            raise TypeError(f"expected {len(fn.params)} arguments, got {len(node.args)}")
        # THE closure rule: parent is the DEFINING env, not the calling env
        local = Environment(parent=fn.env)
        for name, arg in zip(fn.params, node.args):
            local.define(name, evaluate(arg, env))   # args evaluated in CALLER's env
        try:
            execute(fn.body, local)
        except ReturnSignal as r:
            return r.value
        return None
    except (TypeError, ReturnSignal):
        raise
    except Exception as e:
        print(f"[closures:eval_call] {e}")
        import traceback; traceback.print_exc()
        raise
```

---

## Model 2: The One Line That Chooses Lexical Scope

### Critical Thinking Questions

5. Find the single line that decides static-versus-dynamic scope, and write the one-token change that would make your language dynamically scoped. (You now possess the power early Lisp implementers stumbled into.)
6. Arguments are evaluated in `env` (the caller's environment) but bound in `local` (parented on the *definer's*). Construct a program where confusing those two environments changes the output.
7. `ReturnSignal` rides an exception out of nested blocks to the call boundary, exactly like `break` did for loops. State the shared implementation idea in one sentence, and note what would go wrong if `eval_call` caught *all* exceptions rather than only `ReturnSignal`.
8. Trace your language running the `make_adder` program (write it in your language's syntax first). Confirm the diagram from Model 1 falls out of the code.

[[MC]]
Two closures created by separate calls to make_adder(5) and make_adder(3) return different results for the same input because:
- ( ) The function body's code differs between them
- (x) Each closure captured a different defining environment, in which n is bound to a different value
- ( ) Python caches the most recent return value
- ( ) Closures copy the global environment at call time

---

# Part III: The Trap, and Practice

## 3. The Loop-Variable Trap

The famous surprise:

```python
fns = [lambda: i for i in range(3)]
print([f() for f in fns])     # [2, 2, 2], not [0, 1, 2]
```

All three lambdas captured the *same* binding of `i` (closures reference, never copy), and by call time that one binding holds 2. The standard fixes (a default argument `lambda i=i: i`, or a factory function) work by creating a *fresh binding per iteration*, which is exactly the per-iteration-scope design question from your environments exercise, now revealed as the difference between `[2,2,2]` and `[0,1,2]` in every language that combines closures with loops (JavaScript's `var`-to-`let` migration was this exact repair, at ecosystem scale).

## 4. Exercises

1. *Ship functions.* Integrate today's nodes into your full pipeline (lexer keywords, parser rules `fundef` and call-in-primary from the expressions module, evaluator). Demonstrate: a plain function, a recursive `factorial(5)`, and `make_adder` working in *your* language. (Why does recursion already work? Examine what `execute_fundef` defined, and where.)
2. *Counter objects.* In your language or Python, build `make_counter()` returning a function that increments and returns a captured count. You have implemented state without classes; one paragraph on what this suggests about whether your language needs objects at all (closures are the poor man's objects, and vice versa, as the koan goes).
3. *Trap tour.* Reproduce the loop-variable trap in your language (if your loops and closures permit) or in Python, apply both fixes, and explain each fix's mechanism in environment-diagram terms.
4. *Scope flip experiment.* Apply the one-token change from question 5, rerun the scope module's `show`/`demo` program in your language, and report the output flip with the diagram of what the call-parented chain resolved.

---

## Reflection Prompt

In your notebook: a closure carries its context everywhere, so it always means what it meant at home; dynamically scoped code means whatever its surroundings impose. People can resemble both. When has carrying your own context served you, and when has adapting to the caller been the wiser semantics?

---

## 5. Further Reading

- Robert Nystrom. *Crafting Interpreters*, "Functions" and "Closures" (online): our exact implementation, then optimized.
- Abelson and Sussman. *SICP*, section 3.2.
- Douglas Thain. *Introduction to Compilers and Language Design*, Chapter 7.
