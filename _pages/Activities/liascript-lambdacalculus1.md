# The Lambda Calculus, Part 1: Syntax and Reduction
<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://github.com/BillJr99/Ursinus-CS374-Fall2026/blob/gh-pages/_pages/Activities/liascript-lambdacalculus1.md or locally via https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374/gh-pages/_pages/Activities/liascript-lambdacalculus1.md

import: https://raw.githubusercontent.com/liascript/CodeRunner/master/README.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

# The Lambda Calculus, Part 1: Syntax and Reduction

Beneath Scheme, beneath Python's `lambda`, beneath every functional language, sits a formal system from 1936 with **three forms of expression and one rule of computation**: Alonzo Church's **lambda calculus**, in which functions are the only thing that exists, and computing means substituting arguments into bodies. Today we learn to read it and to reduce expressions **by hand**, the way Church did, because by-hand reduction is the only way the system becomes real. The arc: **the three forms $\rightarrow$ free and bound variables $\rightarrow$ beta reduction by hand $\rightarrow$ alpha renaming when names collide**.

---

## Directions and Group Roles

Work in your POGIL team with rotated roles (**Manager**, **Recorder**, **Presenter**, **Reflector**). Today is a whiteboard day: every reduction is written out stepwise, and teammates check each other's substitutions character by character. The Recorder photographs the board for the discussion post. After class, respond to the reflective prompt individually in your notebook.

---

# Part I: The Whole Language

## 1. Three Forms

A lambda expression is exactly one of:

$$
e ::= x \;\mid\; (\lambda x.\, e) \;\mid\; (e_1\; e_2)
$$

a **variable**; an **abstraction** (a function of one parameter $x$ with body $e$, written `λx.e`); or an **application** ($e_1$ applied to $e_2$). That is the entire grammar; there are no numbers, no booleans, no operators (Part 2 builds them all *from functions*). Conventions: application associates left ($f\,a\,b$ means $((f\,a)\,b)$), the body of a λ extends as far right as possible, and multi-parameter functions are nested single-parameter ones: $\lambda x y. e$ abbreviates $\lambda x. (\lambda y. e)$, the trick called **currying**, after Haskell Curry.

**Bound and free.** In $\lambda x.\, x\, y$: the $x$ in the body is **bound** by the λ; $y$ is **free** (it refers to something outside). Binding here is your scope module's lexical scoping, in its original mathematical form: a λ is a binder, its body is the scope.

---

## Model 1: Parse by Eye

### Critical Thinking Questions

1. Fully parenthesize each, then circle binders and underline free variables: (a) $\lambda x. x$; (b) $\lambda x. \lambda y. x$; (c) $(\lambda x. x\, x)(\lambda x. x\, x)$; (d) $\lambda x. x\, (\lambda y. y\, x)$.
2. Expression (b) takes two arguments (curried) and returns the first. What familiar Python one-liner is it? Write the Python.
3. In (d), the inner $x$ at the far right: bound by which λ? Apply the innermost-enclosing-binder rule and connect it, by name, to the environment chain's lookup walk.
4. Why does the grammar need no precedence ladder? (You answered this once for Scheme; the lambda calculus is where Scheme got it.)

---

# Part II: Computation Is Substitution

## 2. Beta Reduction

**The one rule.** An application of an abstraction to an argument reduces by substituting:

$$
(\lambda x.\, e)\; a \;\;\rightarrow_\beta\;\; e[x := a]
$$

read "$e$ with every *free* occurrence of $x$ replaced by $a$." A **redex** is any subexpression of that shape; an expression with no redexes is in **normal form**: the answer. Reduce stepwise, one redex at a time, drawing an arrow per step.

Worked example, fully spelled out:

$$
(\lambda x. \lambda y.\, x)\; A\; B
\;\rightarrow_\beta\; (\lambda y.\, A)\; B
\;\rightarrow_\beta\; A
$$

Step 1 substituted $A$ for $x$ in $\lambda y. x$; the $y$-abstraction remained, now constant; step 2 applied it to $B$, which was discarded because $y$ never occurs in the body. The function selected its first argument: behavior, from substitution alone.

---

## Model 2: Reduce by Hand

### Critical Thinking Questions

5. Reduce, one arrow per step, all the way to normal form: (a) $(\lambda x.\, x)\, z$; (b) $(\lambda x.\, x\, x)(\lambda y.\, y)$; (c) $(\lambda x. \lambda y.\, y)\; A\; B$ (compare with the worked example: what does *this* function select?); (d) $(\lambda f. \lambda x.\, f\, (f\, x))\; g\; a$.
6. Expression (d)'s result applies $g$ twice. You wrote `twice(f)` in Python last week; write the lambda calculus term and the Python side by side. Which is which?
7. Now reduce $(\lambda x.\, x\, x)(\lambda x.\, x\, x)$, the famous **Omega**. Perform two steps. What do you notice, and what does Omega prove about whether every expression has a normal form?
8. In (d) you had a choice of which redex to reduce first at one point. Try the other order; does the normal form change? (The Church-Rosser theorem says it cannot; you have just collected one data point.)

---

## 3. Alpha Renaming: When Names Collide

Substitution has one trap: **capture**. Reduce $(\lambda x. \lambda y.\, x)\; y$ naively and the free $y$ we substitute lands inside $\lambda y$, where it is suddenly, wrongly, bound: the meaning changed. The repair is **alpha renaming**: bound names are arbitrary ($\lambda y. e$ and $\lambda z. e[y := z]$ are the same function), so rename the binder first:

$$
(\lambda x. \lambda y.\, x)\; y \;=_\alpha\; (\lambda x. \lambda z.\, x)\; y \;\rightarrow_\beta\; \lambda z.\, y
$$

The result correctly returns the *free* $y$, whatever it refers to outside. Capture is the shadowing bug from your scope module, in formal dress, and alpha renaming is the formal version of "pick a fresh local name."

[[MC]]
The reduction $(\lambda x. \lambda y.\, x\, y)\; y \rightarrow \lambda y.\, y\, y$ is wrong because:
- ( ) Application associates left
- ( ) The expression was already in normal form
- (x) The substituted free y was captured by the inner binder; alpha-renaming the inner λy is required first
- ( ) Beta reduction may only be applied once per expression

---

# Part III: Synthesis and Practice

## 4. Exercises

1. *Reduction portfolio.* Reduce to normal form, showing every step: $(\lambda x.\, x)(\lambda y.\, y)(z)$; $(\lambda f.\, f\, a)(\lambda x.\, x)$; $(\lambda x. \lambda y.\, y\, x)\; p\; (\lambda q.\, q)$; and one capture trap of your own design, solved with explicit alpha renaming.
2. *Python mirror.* Express exercises 1's first three in Python lambdas and verify by execution that each normal form matches Python's answer (use strings or small functions as the free-variable stand-ins).
3. *Currying made real.* Write Python's `add = lambda x: lambda y: x + y` and call `add(3)(4)`. Then write the lambda calculus term it transliterates. One sentence: what does partial application (`add(3)` alone) *mean*, in both notations?
4. *The scope bridge.* Write a paragraph mapping vocabulary across your three systems: λ-binder, `let`-declaration, and environment `define`; free variable and name resolved in an outer scope; alpha renaming and shadow-avoidance. This paragraph is your study sheet for the closures module.

---

## Reflection Prompt

In your notebook: Church built this system in 1936 to study what "computable" means, with no machine in mind, and it turned out equivalent to Turing's machines. Does it change your view of programming to learn that its functional core predates computers? What, then, is a programming language *about*?

---

## 5. Further Reading

- Raul Rojas. "A Tutorial Introduction to the Lambda Calculus" (online): short and gentle.
- Henk Barendregt and Erik Barendsen. "Introduction to Lambda Calculus" (online notes), for the formal substitution definition.
- Gabriel Lebec. "Lambda as JS, or A Flock of Functions" (talk and slides), which Part 2 follows: https://speakerdeck.com/glebec/lambda-as-js-or-a-flock-of-functions-combinators-lambda-calculus-and-church-encodings-in-javascript
- **Lambda Py** — run the calculus interactively in your browser: https://finsberg.github.io/pycombinator/docs/lambda-talk.html — experiment with the reductions from today's module without installing anything.
