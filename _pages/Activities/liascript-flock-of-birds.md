# Flock of Birds: Combinatory Logic and the SKI Calculus

<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://github.com/BillJr99/Ursinus-CS374-Fall2026/blob/main/_pages/Activities/liascript-flock-of-birds.md

import: https://raw.githubusercontent.com/liascript/CodeRunner/master/README.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

# Flock of Birds: Combinatory Logic and the SKI Calculus

Think of combinators as **LEGO bricks for computation**. Each brick does exactly one simple, self-contained thing — snap the identity brick onto the constant brick, snap that onto the compose brick — and from a handful of primitive pieces you can build any computation that any computer can perform. No names, no variables, no environment. Just bricks clicking together.

## Learning Goals

By the end of this activity, you will be able to:

- Reduce combinatory logic expressions (I, K, S, B, C, W, M) to normal form using the combinator reduction rules, circling the active redex at each step
- Translate lambda expressions into combinator form using bracket abstraction, eliminating all variable bindings
- Implement the standard combinator birds in Python and verify their reduction behavior by execution
- Explain why S and K together are computationally complete (Schönfinkel's theorem) and connect this to the Church-Turing thesis
- Derive familiar higher-order functions (function composition, `flip`, `const`, identity) directly from combinator definitions

> **Before You Begin — Prerequisites**
>
> This activity assumes you are comfortable with:
>
> - **Lambda calculus syntax** — you can read $\lambda x.\ e$ and know that it means "a function that takes $x$ and returns $e$"
> - **Beta-reduction** — you can apply a lambda term to an argument by substituting the argument for the bound variable
> - **Currying** — you understand that `lambda a: lambda b: a` is a two-argument function written as two nested one-argument functions
> - **Python lambdas** — `lambda x: x + 1` is valid Python and returns a callable
>
> If any of these feel shaky, review the Lambda Calculus module before continuing. Combinators are built directly on top of that material; every reduction rule here is just beta-reduction with no bound variables.

*"To every combination there corresponds a unique bird."* — Raymond Smullyan, *To Mock a Mockingbird* (1985)

In the lambda calculus module we built computation from three syntactic forms: variables, abstraction, and application. Today we take the abstraction away. **Combinatory logic** is the lambda calculus with no bound variables — no $\lambda x$, no substitution, no alpha-conversion, no capture to fear. Only application and a small fixed collection of **combinators**: functions with no free variables whose behavior is defined entirely by how they transform their arguments. In 1924, Moses Schönfinkel proved that just two combinators, **S** and **K**, suffice to express any computable function. The birds are named in Raymond Smullyan's puzzle book, and Gabriel Lebec's 2016 London talk "*A Flock of Functions*" demonstrates the entire menagerie live in JavaScript. By the end of this module you will reduce terms in the combinator calculus by hand, implement all the birds in Python, derive familiar operations (function composition, `flip`, `const`, `id`) directly from the birds, and understand why SKI completeness is the combinatory-logic version of the Church-Turing thesis.

---

## 0. Environment

```python
# Every bird is a Python callable. We verify by running the cells below.
# No libraries required.
print("Ready to meet the flock.")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

---

# Part I: The Birds Themselves

## 1. Notation and Reduction Rules

Before diving into the rules, orient yourself: in the lambda calculus you had *variables*, *abstractions* ($\lambda x.\ e$), and *application*. Combinatory logic throws out variables and abstractions entirely. What remains? Application only — and a small fixed menu of named functions (the "birds") whose behavior is completely captured by simple rewrite rules. Each rule says: "when this bird receives enough arguments, rewrite the whole expression." There is no substitution, no renaming, no environment to thread around. Reduction is pure term rewriting, like rearranging LEGO bricks according to a picture.

**Combinatory terms** are built from:

- **Constants**: the combinators themselves (I, K, S, B, C, W, M, …)
- **Application**: writing two terms next to each other, left-associative

That is the entire syntax. There are no variables and no abstractions. A **reduction rule** for each combinator states how it consumes arguments from the right:

$$
\mathbf{I}\ a \;\Rightarrow\; a
$$
$$
\mathbf{K}\ a\ b \;\Rightarrow\; a
$$
$$
\mathbf{S}\ a\ b\ c \;\Rightarrow\; a\ c\ (b\ c)
$$

Application associates left, so $\mathbf{S}\ a\ b\ c$ means $(((\mathbf{S}\ a)\ b)\ c)$. A **redex** in combinatory logic is any subterm of the form $\mathbf{I}\ a$, $\mathbf{K}\ a\ b$, or $\mathbf{S}\ a\ b\ c$ (and analogously for other combinators). Reduction is confluent, exactly as in the lambda calculus, because the combinators are derived from it.

> **Watch out! — Argument counting**
>
> A combinator only fires when it has received *all* of its required arguments. $\mathbf{K}\ a$ is a partially applied function — it is waiting for its second argument and does *not* yet reduce. $\mathbf{S}\ a\ b$ is similarly stuck. Writing $\mathbf{S}\ a\ b\ c$ is what triggers the rule. If you try to reduce a term and nothing fires, check whether every combinator in the term is fully saturated.

**The translation from lambda calculus to combinators** (bracket abstraction) works by structural recursion:

$$
[x]\ x = \mathbf{I}
$$
$$
[x]\ e = \mathbf{K}\ e \quad (x \notin \mathrm{FV}(e))
$$
$$
[x]\ (e_1\ e_2) = \mathbf{S}\ ([x]\ e_1)\ ([x]\ e_2) \quad (x \in \mathrm{FV}(e_1 e_2))
$$

Every lambda term becomes a combinator expression — free of variables, yet computationally identical. The gain is conceptual: reduction is pure term rewriting, no environment, no substitution machinery.

---

### Try It: Individually — Reduce by Hand

Reduce each expression to normal form, one rule application per line, circling the redex at each step.

1. $\mathbf{I}\ (\mathbf{K}\ a\ b)$
2. $\mathbf{K}\ (\mathbf{I}\ a)\ b$
3. $\mathbf{S}\ \mathbf{K}\ \mathbf{K}\ a$ — what well-known combinator does this behave like?

Hint for (3): what does $\mathbf{K}\ a\ (\_)$ do to any second argument?

---

## 2. The Identity Bird — **I** (Idiot)

This is the simplest possible LEGO brick: snap it onto anything and that thing comes straight out the other side unchanged. It seems useless in isolation, but it becomes essential as a "do nothing" placeholder when you need a function in a slot that does not actually transform its argument. It also shows up in the derivation of every other combinator from S and K.

$$
\mathbf{I}\ a = a
$$

The Idiot bird passes its argument through unchanged. In lambda calculus it is $\lambda a.\ a$. In Haskell it is `id`. In mathematics it is the identity function on every set. Note that $\mathbf{I}$ is not primitive given S and K: $\mathbf{S}\ \mathbf{K}\ \mathbf{K}\ a \Rightarrow \mathbf{K}\ a\ (\mathbf{K}\ a) \Rightarrow a$, so $\mathbf{I} = \mathbf{S}\ \mathbf{K}\ \mathbf{K}$.

```python
I = lambda a: a

print(I(42))          # 42
print(I("hello"))     # hello
print(I(I)(42))       # 42  -- identity of identity is still identity
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

---

## 3. The Kestrel — **K** (Constant)

The Kestrel is the "ignore and keep" brick. You hand it a value, and no matter what else you stack on top, it will always return that original value. This turns out to encode the Boolean *true* in Church encodings — because `if true then x else y` means "take two branches, return the first." Connect to the LEGO analogy: K is a brick with a trap door; everything that enters the second slot falls straight through and disappears.

$$
\mathbf{K}\ a\ b = a
$$

The Kestrel takes two arguments and returns the first, discarding the second. In lambda calculus it is $\lambda a.\ \lambda b.\ a$ — the encoding of **true** in Church booleans! In Haskell it is `const`. In Python:

```python
I = lambda a: a
K = lambda a: lambda b: a

print(K("first")("second"))   # first
print(K(42)("anything"))      # 42

# K is Church true
true  = K
false = lambda a: lambda b: b   # we'll derive this from KI below
KI    = K(I)                    # KI a b = K I a b = I b = b -- this IS Church false!
print(KI("ignored")("returned"))  # returned -- K(I) behaves as false / second-selector
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

---

## 4. The Bluebird — **B** (Compose)

The Bluebird is the pipeline brick. Snap two bricks together end-to-end: the output of the second feeds into the input of the first. This is Haskell's `.` operator, and it is how real functional programs are built — not by writing big monolithic functions, but by composing small single-purpose ones. Notice that the argument order matters: $\mathbf{B}\ f\ g$ means "do $g$ first, then $f$," which is the standard mathematical right-to-left composition.

$$
\mathbf{B}\ f\ g\ x = f\ (g\ x)
$$

The Bluebird composes two functions: apply $g$ first, then $f$. In lambda calculus it is $\lambda f.\ \lambda g.\ \lambda x.\ f\ (g\ x)$. In Haskell it is `(.)`. It is one of the most-used birds in practice because function composition is the primary method of building programs in functional style.

```python
K = lambda a: lambda b: a
B = lambda f: lambda g: lambda x: f(g(x))

double  = lambda x: x * 2
add_one = lambda x: x + 1

double_then_add = B(add_one)(double)   # add 1 after doubling
add_then_double = B(double)(add_one)   # double after adding 1

print(double_then_add(5))  # (5*2)+1 = 11
print(add_then_double(5))  # (5+1)*2 = 12

# B is derivable: B = S (K S) K
S = lambda a: lambda b: lambda c: a(c)(b(c))
B_from_SK = S(K(S))(K)
print(B_from_SK(add_one)(double)(5))  # 11 -- same as B(add_one)(double)(5)
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

---

## 5. The Cardinal — **C** (Flip)

The Cardinal is the "swap the inputs" brick. When you have a two-argument function and the arguments are arriving in the wrong order — perhaps you want to partially apply the *second* argument first — the Cardinal flips them for you. Haskell calls this `flip`, and it appears constantly when adapting library functions for use in pipelines and point-free style.

$$
\mathbf{C}\ f\ a\ b = f\ b\ a
$$

The Cardinal flips the argument order of a two-argument function. In lambda calculus it is $\lambda f.\ \lambda a.\ \lambda b.\ f\ b\ a$. In Haskell it is `flip`.

```python
K = lambda a: lambda b: a
S = lambda f: lambda g: lambda x: f(x)(g(x))
B = lambda f: lambda g: lambda x: f(g(x))
C = lambda f: lambda a: lambda b: f(b)(a)

subtract = lambda x: lambda y: x - y   # curried subtraction
subtract_from_10 = C(subtract)(10)      # flip: now b goes first
print(subtract_from_10(3))              # 10 - 3 = 7 (without flip: 3 - 10 = -7)

# C is derivable: C = S (B B S) (K K)
C_from_SK = S(B(B)(S))(K(K))
print(C_from_SK(subtract)(10)(3))   # 7
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

---

## 6. The Starling — **S** (the Power Bird)

The Starling is the "fork and merge" brick — the one that makes the calculus powerful enough to compute anything. Given $x$, it routes $x$ down two separate paths simultaneously: one path feeds $x$ into $f$, producing a function; the other path feeds $x$ into $g$, producing an argument; then the results are merged by application. This is the combinator encoding of *sharing*: the same input reaches two different parts of a computation. Without this sharing capability, the calculus could only compute linear functions.

$$
\mathbf{S}\ f\ g\ x = f\ x\ (g\ x)
$$

The Starling is the heart of the calculus. It passes $x$ to both $f$ and $g$, then applies the result of $f(x)$ to the result of $g(x)$. This is the combinator version of *sharing an argument*: both branches see $x$, so duplication is built in. **S and K together are Turing complete**: any computable function can be expressed using only these two birds.

```python
K = lambda a: lambda b: a
S = lambda f: lambda g: lambda x: f(x)(g(x))

# S K K = I
SKK = S(K)(K)
print(SKK(42))   # 42

# The power of S: apply a function to a value AND its "environment"
# This is what makes S the basis for closures and environments
add  = lambda x: lambda y: x + y
succ = S(add)(K(1))   # succ x = add x (K 1 x) = add x 1 = x + 1
print(succ(5))   # 6
print(succ(10))  # 11
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

---

## 7. The Mockingbird — **M** (Self-Application)

The Mockingbird is the "danger" brick — handle with care. It takes whatever you hand it and makes it eat itself. Applied to a safe function, this produces interesting behavior (self-duplication, mirroring). Applied to itself, it produces $\Omega$: the combinator equivalent of an infinite loop. The Mockingbird is the combinatory seed from which fixed-point combinators and recursion grow; it demonstrates that non-termination is an intrinsic feature of any sufficiently expressive system.

$$
\mathbf{M}\ a = a\ a
$$

The Mockingbird applies its argument to itself. In lambda calculus it is $\lambda a.\ a\ a$. It is the self-application operator, and $\mathbf{M}\ \mathbf{M}$ is the combinatory equivalent of $\Omega$ — it reduces forever. But applied carefully, the Mockingbird is the basis for fixed-point combinators and recursion in the combinator calculus.

```python
# We can't actually call M(M) -- infinite loop! 
# But M applied to other combinators is safe:
I = lambda a: a
K = lambda a: lambda b: a
M = lambda a: a(a)

print(M(I)(42))      # I(I)(42) = I(42) = 42
print(M(K)("a"))     # K(K)("a") = K  -- a function, not a value we can print easily

# M applied to a saturated-enough combinator:
double = lambda x: x * 2
# M doesn't make sense on double alone since double takes one arg; 
# but M(double) = double(double) and double is not a valid argument to double
# This shows M is "dangerous" -- it only makes sense with combinators that expect functions
print("M is the self-application bird")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

> **Watch out! — Do not evaluate M(M)**
>
> `M(M)` in Python will immediately raise a `RecursionError` (or spin forever). The Mockingbird is safe only when its argument is a function that can meaningfully accept a function as input. Before running any expression involving M, ask: "does this argument expect a callable?" If not, do not apply M.

---

## 8. The Warbler — **W** (Duplicate)

The Warbler is the "copy and double-feed" brick. It takes a two-argument function and collapses its two inputs into one: whatever you hand it, it hands to $f$ twice. This is subtly different from the Mockingbird: M makes $x$ eat *itself*, while W feeds $x$ to an *external* two-argument function $f$. The Warbler is how you derive "diagonal" operations — squaring, equality-with-self, duplication — without ever naming the argument twice.

$$
\mathbf{W}\ f\ x = f\ x\ x
$$

The Warbler duplicates its second argument, passing it twice to $f$. This is different from $\mathbf{M}$: $\mathbf{W}$ feeds $x$ to a two-argument function $f$, not to $x$ itself.

```python
W = lambda f: lambda x: f(x)(x)

# W with add: add x x = 2x (doubling!)
add = lambda x: lambda y: x + y
double_via_W = W(add)
print(double_via_W(5))   # add 5 5 = 10
print(double_via_W(7))   # add 7 7 = 14

# W as a way to express "apply diagonal"
eq = lambda x: lambda y: x == y
is_zero = W(lambda x: lambda y: x == 0 and y == 0)
print(W(eq)(5))    # eq 5 5 = True
print(W(eq)(5))    # True -- a number always equals itself
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

---

# Part II: Derivation and the Completeness of SKI

## 9. Everything from S, K, I

You have now met seven birds. Here is the remarkable fact: you do not need seven. You need *two*. S and K alone — two LEGO bricks — can simulate every other bird, every lambda term, every computable function. This is Schönfinkel's 1924 theorem, the combinatory-logic counterpart of the Church-Turing thesis. The bracket abstraction algorithm in Section 1 is the constructive proof: it tells you mechanically how to turn any lambda term into an SKI expression. The derivations below make this concrete.

The true power of combinatory logic is that S and K suffice for *any* lambda term. The bracket abstraction algorithm (Section 1) converts any lambda term to an equivalent SKI expression. Let us derive B, C, and W from SKI to see this concretely.

**Deriving B (Compose) from SKI:**

We want $\mathbf{B}\ f\ g\ x = f\ (g\ x)$. Use $[x]\ (f\ (g\ x))$:

$$
[x]\ (f\ (g\ x)) = \mathbf{S}\ ([x]\ f)\ ([x]\ (g\ x)) = \mathbf{S}\ (\mathbf{K}\ f)\ (\mathbf{S}\ (\mathbf{K}\ g)\ \mathbf{I})
$$

So $\mathbf{B} = \mathbf{S}\ (\mathbf{K}\ \mathbf{S})\ \mathbf{K}$ (with one more step of abstraction). Verify:

$$
\mathbf{S}\ (\mathbf{K}\ \mathbf{S})\ \mathbf{K}\ f\ g\ x \Rightarrow \mathbf{K}\ \mathbf{S}\ f\ (\mathbf{K}\ f)\ g\ x \Rightarrow \mathbf{S}\ (\mathbf{K}\ f)\ g\ x \Rightarrow \mathbf{K}\ f\ x\ (g\ x) \Rightarrow f\ (g\ x)
$$

```python
# Verify B = S(KS)K
S = lambda f: lambda g: lambda x: f(x)(g(x))
K = lambda a: lambda b: a
I_bird = S(K)(K)

B_from_SK = S(K(S))(K)

add_one = lambda x: x + 1
double  = lambda x: x * 2

print(B_from_SK(add_one)(double)(5))   # 11: same as add_one(double(5))
print(B_from_SK(str)(double)(5))       # "10": str(double(5))
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

> **Watch out! — SKI expressions grow quickly**
>
> The naive bracket abstraction algorithm can produce expressions that are exponentially larger than the original lambda term — a two-variable lambda can become dozens of S, K, and I tokens. This is why real compilers (e.g., Turner 1979) use optimized combinators like B and C to keep the output manageable. When you do bracket abstraction by hand in the exercises, count your tokens; if the result seems enormous, double-check your steps.

---

[[MC]]
Which reduction sequence correctly shows that $\mathbf{K}\ \mathbf{I}\ a\ b \Rightarrow b$ (i.e., that $\mathbf{K}\ \mathbf{I}$ is **false** / the second-argument selector)?
- (x) $\mathbf{K}\ \mathbf{I}\ a \Rightarrow \mathbf{I}$, then $\mathbf{I}\ b \Rightarrow b$. Each step fires one combinator rule.
- ( ) $\mathbf{K}\ \mathbf{I}\ a\ b \Rightarrow \mathbf{K}\ b$, then $\mathbf{K}\ b \Rightarrow b$.
- ( ) $\mathbf{K}\ \mathbf{I}\ a\ b \Rightarrow \mathbf{I}\ \mathbf{I}\ b \Rightarrow b$. K fires on I and b simultaneously.
- ( ) The reduction diverges because $\mathbf{K}\ \mathbf{I}$ contains no redex.

---

## 10. The Y Combinator in SK

This section pulls together everything: if S and K are computationally complete, and if recursion is a computable operation, then S and K can express recursion — without any `def`, without any name, without any environment. The Y combinator written in pure SK is startling precisely because it looks like nothing else you have seen: a wall of S, K, and I with no variables anywhere. Yet it satisfies $Y\ g = g\ (Y\ g)$ for any $g$. The derivation in the Y combinator module explains *why* this works; here the goal is to see that it is expressible at all.

Recall from the lambda calculus module that the Y combinator satisfies $Y\ g = g\ (Y\ g)$. In strict (applicative-order) languages we use the Z combinator instead. In pure SK combinatory logic:

$$
\mathbf{Y} = \mathbf{S}\ (\mathbf{K}\ (\mathbf{S}\ \mathbf{I}\ \mathbf{I}))\ (\mathbf{S}\ (\mathbf{S}\ (\mathbf{K}\ \mathbf{S})\ \mathbf{K})\ (\mathbf{K}\ (\mathbf{S}\ \mathbf{I}\ \mathbf{I})))
$$

This derivation of Y from S and K — without any variables, without any lambda, without any notion of binding — is the combinatory logic proof that recursion is not a primitive: it is computable from application alone.

```python
# Z combinator (applicative-order Y) in combinatory style
# We build it from our birds to show the connection
Z = lambda f: (lambda x: f(lambda v: x(x)(v)))(lambda x: f(lambda v: x(x)(v)))

# factorial without def, without recursion primitives, only Z and lambdas
step = lambda self: lambda n: 1 if n == 0 else n * self(n - 1)
factorial = Z(step)
print([factorial(n) for n in range(8)])   # [1, 1, 2, 6, 24, 120, 720, 5040]

# Fibonacci the same way
fib_step = lambda self: lambda n: n if n <= 1 else self(n-1) + self(n-2)
fib = Z(fib_step)
print([fib(n) for n in range(10)])   # [0,1,1,2,3,5,8,13,21,34]
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

---

# Part III: The Flock in Practice

## 11. Gabriel Lebec's Birds in JavaScript — and in Python

The birds stop being an abstract curiosity the moment you recognize them in code you already write. Every time you call `map(lambda x: x + 1, lst)` you are using I. Every time you write `key=lambda _: 0` you are using K. Every time you write `sorted(lst, key=lambda x: -x)` you are using a partial application of C. Gabriel Lebec's talk makes this explicit for JavaScript; this section makes it explicit for Python. The punchline: **combinators are not exotic theory — they are the names for the patterns you reach for every day without knowing it**.

Gabriel Lebec's 2016 talk "*A Flock of Functions*" demonstrates that every standard higher-order function in JavaScript is a bird in disguise. The key insight is that **you already use combinators every day** — you just call them `const`, `id`, `flip`, `compose`, and `curry`. Here is the full correspondence, in Python:

```python
# === The Flock — Python Edition ===
# Inspired by Gabriel Lebec's "A Flock of Functions" (2016)

# Primitive birds
I = lambda a: a                                      # Idiot / id
K = lambda a: lambda b: a                            # Kestrel / const
S = lambda f: lambda g: lambda x: f(x)(g(x))        # Starling

# Derived birds (all from SKI)
B = lambda f: lambda g: lambda x: f(g(x))           # Bluebird / compose
C = lambda f: lambda a: lambda b: f(b)(a)           # Cardinal / flip
W = lambda f: lambda x: f(x)(x)                     # Warbler / duplicate
M = lambda a: a(a)                                   # Mockingbird / self-apply
T = lambda a: lambda f: f(a)                         # Thrush / apply / pipe-right
V = lambda a: lambda b: lambda f: f(a)(b)            # Vireo / pair constructor

KI = K(I)   # False / second-selector

# Pair operations via Vireo
pair = V
fst  = lambda p: p(K)
snd  = lambda p: p(KI)

p = pair(1)(2)
print(fst(p), snd(p))   # 1 2

# Church numerals from K and I
zero  = K(I)                             # λf.λx.x -- apply f zero times
once  = lambda f: lambda x: f(x)         # λf.λx.fx -- apply f once
twice = lambda f: lambda x: f(f(x))      # λf.λx.f(fx)

to_int = lambda n: n(lambda k: k + 1)(0)
succ = lambda n: lambda f: lambda x: f(n(f)(x))

print(to_int(zero))   # 0
print(to_int(once))   # 1
print(to_int(twice))  # 2
print(to_int(succ(twice)))  # 3
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

---

## 12. Point-Free Style: Programming Without Variables

Point-free programming is what happens when you take the combinator philosophy all the way to the surface of your code. Instead of writing `lambda x: f(g(x))` — which names $x$ even though $x$ appears in only one place — you write `B(f)(g)`, which says "compose f and g" without ever mentioning what they are applied to. This is not just an aesthetic preference: in Haskell it is the dominant style, because it emphasizes what transformations are being composed rather than what data they act on. The LEGO metaphor completes here: point-free code is a blueprint describing how bricks connect, not a sequence of operations on a specific piece.

**Point-free** (or "tacit") programming uses only combinators and function composition — no named variables, no lambdas. It is the ultimate expression of the combinatory-logic philosophy, and it is the standard style in Haskell. Here is the connection:

```python
from functools import reduce
B = lambda f: lambda g: lambda x: f(g(x))
W = lambda f: lambda x: f(x)(x)

# Point-full (with explicit variable x):
def square_then_add_one_v1(x):
    return x * x + 1

# Point-free (x never appears):
square   = W(lambda x: lambda y: x * y)  # W(mul) x = mul x x = x*x
add_one  = lambda x: x + 1
square_then_add_one = B(add_one)(square)  # compose: add_one . square

print(square_then_add_one(5))   # 26
print(square_then_add_one(3))   # 10

# A pipeline of birds: reduce with curried B using explicit application
pipeline = lambda *fns: reduce(lambda a, b: B(a)(b), fns) if len(fns) > 1 else fns[0]

process = pipeline(lambda s: s.replace(" ", "_"), str.lower, str.strip)
print(process("  Hello World  "))   # hello_world
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

---

### Try It: With a Partner — Bird Identification

For each Python expression below, identify which bird (I, K, S, B, C, W, M, KI) it instantiates. One partner argues; the other challenges. Write the combinator reduction rule that proves the claim.

1. `lambda x: x`
2. `lambda x: lambda y: x`
3. `lambda f: lambda g: lambda x: f(g(x))`
4. `lambda f: lambda x: f(x)(x)`
5. `lambda x: lambda y: lambda z: x(z)(y(z))`
6. `lambda f: lambda a: lambda b: f(b)(a)`
7. `lambda a: lambda b: lambda f: f(a)(b)` — which bird pairs data?

---

## 13. Exercises

1. **Reduction transcripts.** Reduce to normal form, one combinator rule per line, circling the redex:
   - (a) $\mathbf{B}\ f\ (\mathbf{B}\ g\ h)\ x$ — show this equals $\mathbf{B}\ (\mathbf{B}\ f\ g)\ h\ x$ (associativity of composition)
   - (b) $\mathbf{C}\ \mathbf{K}\ a\ b$ — what does this return, and what lambda term is it equivalent to?
   - (c) $\mathbf{W}\ \mathbf{K}\ a$ — one step is enough; what does it return?

2. **Bracket abstraction.** Use the three-rule bracket abstraction algorithm to convert $\lambda x.\ \lambda y.\ y\ x$ to an SKI expression. Verify by reducing your expression on two concrete arguments.

3. **Flock identification.** A colleague writes `f = lambda x: lambda _: x`. Which bird is this? Write the bird's one-line reduction rule, its lambda term, its Haskell name, and the two-word English description that explains what it does to its arguments.

4. **Pairs from birds.** Using only I, K, KI, V (Vireo), implement `swap` (exchange the components of a pair) as a bird expression, with no lambda. Verify on `pair(1)(2)`.

5. **SKI Turing completeness (research).** The combinator $\mathbf{S}\ \mathbf{K}$ applied to itself loops: $\mathbf{S}\ \mathbf{K}\ (\mathbf{S}\ \mathbf{K}) \Rightarrow \mathbf{K}\ (\mathbf{S}\ \mathbf{K})\ (\mathbf{K}\ (\mathbf{S}\ \mathbf{K})) \Rightarrow \mathbf{S}\ \mathbf{K}$. Write a one-paragraph explanation of why the existence of a non-terminating term (like $\Omega$ in the lambda calculus) is *necessary* for a system to be Turing complete, connecting to the Halting Problem.

---

## 14. Further Reading

- Smullyan, Raymond. *To Mock a Mockingbird* (Knopf, 1985). The source of the bird names; a puzzle book that teaches combinatory logic through delightful ornithological fiction.
- Lebec, Gabriel. "Lambda as JS, or A Flock of Functions: Combinators, Lambda Calculus, and Church Encodings in JavaScript." London Functional Programmers Meetup, 2016. **This is the direct inspiration for this module.** Slides: https://speakerdeck.com/glebec/lambda-as-js-or-a-flock-of-functions-combinators-lambda-calculus-and-church-encodings-in-javascript — Source: https://github.com/glebec/lambda-talk — Watch the recording; every combinator in this activity appears there in JavaScript.
- Curry, H. B. and R. Feys. *Combinatory Logic, Volume I* (North-Holland, 1958). The foundational text.
- Hindley, J. Roger and Jonathan P. Seldin. *Lambda-Calculus and Combinators: An Introduction* (Cambridge UP, 2008). Modern, rigorous, and accessible.
- Turner, David. "Another Algorithm for Bracket Abstraction." *Journal of Symbolic Logic* 44(2), 1979. The optimized bracket abstraction that compilers actually use, avoiding the SKI expansion explosion.
- Tromp, John. "Binary Lambda Calculus and Combinatory Logic." *Randomness and Complexity* (World Scientific, 2007). SK programs as bit strings; the smallest known universal computer.
