<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374-Fall2026/gh-pages/_pages/Activities/liascript-lambdacalculus2.md or locally via https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374-Fall2026/gh-pages/_pages/Activities/liascript-lambdacalculus2.md

import: https://raw.githubusercontent.com/liascript/CodeRunner/master/README.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

# Lambda Calculus II and Closures: Church Encodings, Combinators, and First-Class Functions

## Learning Goals

By the end of this activity, you will be able to:

- Define and reduce the named combinators I, K, KI, and C as pure lambda terms, and check their behavior by hand reduction and by running Python
- Encode booleans as lambda terms (Church booleans) and write `AND`, `OR`, `NOT`, and `IF-THEN-ELSE` using only function application
- Encode natural numbers as Church numerals and write successor, addition, and multiplication as lambda functions
- Show that every combinator with no free variables can be given a permanent name, and connect this to referential transparency
- Trace the full reduction of an arithmetic expression written in Church numeral notation to its normal form
- Derive a fixed-point combinator twice: once by refactoring a self-applying factorial until the machinery separates from the logic, and once algebraically by solving $\textbf{Y}\, f = f\, (\textbf{Y}\, f)$ for a self-application
- Put any recursive function into generator form, so it takes the rest of the recursion as a parameter instead of calling itself by name
- Define a closure as a pair of code and its defining environment, and explain why a language with first-class functions and static scope needs it
- Trace environment diagrams for closure creation and invocation, identifying captured variable bindings and parent environment pointers
- Implement closure creation and application in an interpreter by storing and restoring the defining environment at call time
- Compare the fixed-point combinator and the captured, mutable binding as two unrelated ways of supplying what the bare calculus lacks

> **Before You Begin**
>
> This activity builds directly on **Lambda Calculus I** and on **Binding, Scope, and Environments**.  Before you start, you should be comfortable with:
>
> - Writing and reading lambda expressions (e.g., `λx.λy. x`)
> - Performing beta reduction step by step
> - Telling free variables from bound variables
> - Applying multi-argument (curried) functions
> - Tracing a variable lookup through an environment chain, and explaining the difference between a value and a binding
> - Reading and writing Python functions that define and return inner functions
>
> If any of those feel shaky, review the [Lambda Calculus I activity](liascript-lambdacalculus1.md) and the [Binding, Scope, and Environments activity](liascript-bindingscope.md) before continuing.

---

Everything you need to compute can be built from functions alone.  The lambda calculus has no numbers, no booleans, and no if-statements.  Alonzo Church showed that you can encode all of them as pure lambda terms, and today you build that encoding from scratch in Python.  We follow the same path as Gabriel Lebec's talk "A Flock of Functions" (our companion reading, in JavaScript): named combinators, then Church booleans, then Church numerals and arithmetic, then recursion with no names at all.  You check each construction twice, once by hand and once by running it.

Then we cross from the calculus to the machine.  A **closure** is a function packaged together with the environment that was in force when the function was created.  That package is how a function can still read a variable after the scope that created the variable has returned, and it is how your interpreter will run every capturing lambda your team's language allows.  The session closes by setting the two halves side by side: the fixed-point combinator buys self-reference with no names and no memory, and the closure buys names that persist, with memory you are allowed to change.

---

## Directions and Group Roles

Work in your POGIL team with your rotated roles (**Manager**, **Recorder**, **Presenter**, **Reflector**).  Whiteboard day again: every claimed equality gets a stepwise reduction or a Python check, verified by a teammate.  The Recorder posts your answers to the Class Activity Questions discussion board, and the Presenter reports out wherever you disagreed or found another approach.  After class, please respond to the reflective prompt on your own in your notebook.

## Today's 75 Minutes

Seven parts in one period means the reductions happen on the whiteboard and the Python checks happen fast.  Parts II and III are the material the Lambda Calculus lab asks you to reduce by hand, so protect that time first.

| Minutes | Segment | What your team does |
|---------|---------|---------------------|
| 0-5 | Roles and whiteboard rules | Rotate roles; agree who verifies each reduction before it counts |
| 5-15 | Parts I and II: Combinators and Church Booleans | Answer CTQ 1.1, run the boolean cell, and reduce CTQs 2.1-2.3 at the board |
| 15-30 | Part III: Numbers as Repetition | Reduce `SUCC ZERO` and `PLUS TWO THREE` together, run the encodings, and answer CTQs 3.1-3.3 |
| 30-45 | Part IV: Recursion Without Names | Walk Steps 0 through 5, run Model 4, and answer CTQ 4.1 |
| 45-55 | Part V: Closures, the Problem and the Mechanism | Run `make_adder`, answer CTQs 5.1 and 5.2, then run Model 5 and answer CTQs 5.4-5.5 |
| 55-67 | Part VI: Closures in Your Own Interpreter | Fill the by-hand table, run Model 6 under both settings, and answer CTQs 6.1-6.3 |
| 67-75 | Part VII: Two Ways to Get What the Calculus Lacks | Read section 8 aloud and answer CTQs 7.1 and 7.2 |

If the period runs short, the Try It Yourself blocks and CTQs 1.2, 2.4, 3.4, 4.2-4.3, 5.3, 6.4, and 7.3 move to homework.  Everything after **In-class work stops here** is self-paced: the exercises and four extensions covering Church pairs and the predecessor, the backwards derivation of $\textbf{Y}$ and why strictness matters, the loop-variable trap, and closures compared with objects.  The pairs extension supplies the `PRED` that Part IV's factorial uses.

---

# Part I: The Flock

## 1.  Combinators: Closed Terms with Names

A **combinator** is a lambda expression with no free variables.  Because nothing inside it depends on the surrounding context, it means the same thing wherever you write it, so it can safely be given a name.  The famous combinators have bird names.  The names come from Raymond Smullyan's puzzle book, and Lebec's talk follows the same tradition:

$$
\textbf{I} = \lambda x.\, x \quad \text{(Identity, the Idiot bird)}
$$
$$
\textbf{K} = \lambda x. \lambda y.\, x \quad \text{(the Kestrel: constant-maker)}
$$
$$
\textbf{KI} = \lambda x. \lambda y.\, y \quad \text{(Kite: discards the first)}
$$
$$
\textbf{C} = \lambda f. \lambda a. \lambda b.\, f\, b\, a \quad \text{(Cardinal: flips arguments)}
$$

You already reduced **K** $A\, B \rightarrow A$ and **KI** $A\, B \rightarrow B$ in *The Lambda Calculus, Part 1*, before they had names.  In Part II, these two selectors become TRUE and FALSE.

---

## Model 1: Combinators as Birds

### Critical Thinking Questions

> **CTQ 1.1** Verify by reduction that $\textbf{C}\, \textbf{K}\, A\, B$ behaves exactly like $\textbf{KI}\, A\, B$.  (The Cardinal of the Kestrel is the Kite: flipping "take the first" gives "take the second.")

> **CTQ 1.2** Write each combinator as a Python lambda (`K = lambda x: lambda y: x`, and so on) and verify question 1 by running it with strings for $A$ and $B$.

> **CTQ 1.3** Why must a combinator have no free variables before it deserves a permanent name?  Connect your answer to purity from the functional module: a closed term can be replaced by its name anywhere without changing the meaning of the program, which is what referential transparency means.

Recap: a combinator is a closed lambda term, and closed terms can be named because they mean the same thing everywhere.  K selects its first argument and KI selects its second, and that pair of selectors is all we need for Part II.

---

# Part II: Truth, Built from Selection

> **Intuition before booleans:** An `if` does one job: it selects one of two things.  So we define the booleans as the selectors.  TRUE is `lambda x: lambda y: x`, which keeps the first argument, and FALSE is `lambda x: lambda y: y`, which keeps the second.  If/then/else is then application: write `b(then_branch)(else_branch)` and the boolean picks the branch itself.

## 2.  Church Booleans

A **Church boolean** is a truth value encoded as a function of two arguments that returns one of them.  You already have both selectors from Part I:

$$
\textbf{TRUE} = \textbf{K} = \lambda x. \lambda y.\, x \qquad \textbf{FALSE} = \textbf{KI} = \lambda x. \lambda y.\, y
$$

With this encoding, `if b then t else e` is the application $b\, t\, e$.  No special form is needed, because the boolean itself is the conditional.  Logic follows by function surgery, which means writing each operator by choosing what its arguments select:

$$
\textbf{NOT} = \lambda b.\, b\, \textbf{FALSE}\, \textbf{TRUE} \qquad
\textbf{AND} = \lambda p. \lambda q.\, p\, q\, p \qquad
\textbf{OR} = \lambda p. \lambda q.\, p\, p\, q
$$

> **Watch out!**  Church booleans are functions, not values.  `TRUE(a)(b)` returns `a`, and that is the entire definition.  The if-then-else `IF b t f = b(t)(f)` works because TRUE selects its first argument and FALSE selects its second.  There is no conditional syntax; the boolean is the branch selector.

> **Watch out!**  A Python `lambda` returns a single expression.  For multi-argument Church terms, use curried lambdas: `lambda x: lambda y: x`, not `lambda x,y: x`.  The curried form is what makes `TRUE(a)(b)` work: the first call returns another function, and that function accepts `b`.

**Step-by-step reduction: NOT TRUE**

```
NOT TRUE
= (λb. b FALSE TRUE) (λx.λy. x)
->β (λx.λy. x) FALSE TRUE
->β (λy. FALSE) TRUE
->β FALSE  OK
```

**Step-by-step reduction: AND TRUE FALSE**

```
AND TRUE FALSE
= (λp.λq. p q p) TRUE FALSE
->β (λq. TRUE q TRUE) FALSE
->β TRUE FALSE TRUE
= (λx.λy. x) FALSE TRUE
->β (λy. FALSE) TRUE
->β FALSE  OK
```

**Decode helper, "peek inside" a Church boolean:**

```python
TRUE  = lambda x: lambda y: x
FALSE = lambda x: lambda y: y

def church_to_bool(b):
    return b(True)(False)

print("church_to_bool(TRUE)  =", church_to_bool(TRUE))
print("church_to_bool(FALSE) =", church_to_bool(FALSE))
```
@LIA.eval(`["main.py"]`, `none`, `python3 main.py`)

The helper hands a Church boolean Python's built-in `True` and `False` as its two arguments.  TRUE selects its first argument, so it returns `True`; FALSE returns `False`.  This is your window into the encoding.

### Church Booleans: Runnable

```python
# Church booleans: TRUE selects first, FALSE selects second.
TRUE  = lambda x: lambda y: x          # K  (Kestrel)
FALSE = lambda x: lambda y: y          # KI (Kite)
NOT   = lambda b: b(FALSE)(TRUE)
AND   = lambda p: lambda q: p(q)(p)
OR    = lambda p: lambda q: p(p)(q)
XOR   = lambda p: lambda q: p(NOT(q))(q)

# Decode helper: peek inside any Church boolean
def church_to_bool(b):
    return b(True)(False)

show_bool = lambda b: b("TRUE")("FALSE")   # a boolean selects its own name

print("=== Church Booleans ===")
print("church_to_bool(TRUE)  =", church_to_bool(TRUE))
print("church_to_bool(FALSE) =", church_to_bool(FALSE))
print("NOT TRUE        =", show_bool(NOT(TRUE)))
print("NOT FALSE       =", show_bool(NOT(FALSE)))
print("AND TRUE FALSE  =", show_bool(AND(TRUE)(FALSE)))
print("OR  FALSE TRUE  =", show_bool(OR(FALSE)(TRUE)))
print("XOR TRUE  TRUE  =", show_bool(XOR(TRUE)(TRUE)))
print("XOR TRUE  FALSE =", show_bool(XOR(TRUE)(FALSE)))

# if-then-else is just application: b(then)(else)
print("\n=== Church if-then-else ===")
print("if TRUE  then 'yes' else 'no' =", TRUE("yes")("no"))
print("if FALSE then 'yes' else 'no' =", FALSE("yes")("no"))
```
@LIA.eval(`["main.py"]`, `none`, `python3 main.py`)

---

## Model 2: Prove the Logic

### Critical Thinking Questions

> **CTQ 2.1** Reduce $\textbf{NOT}\, \textbf{TRUE}$ step by step to $\textbf{FALSE}$.  (Substitute, then let TRUE select.)  The trace above is a guide; write your own with every substitution made explicit.

> **CTQ 2.2** Reduce $\textbf{AND}\, \textbf{TRUE}\, \textbf{FALSE}$ and $\textbf{AND}\, \textbf{FALSE}\, \textbf{TRUE}$.  Explain in one sentence why `p q p` works: when is the answer "whatever q is," and when is it "p itself"?

> **CTQ 2.3** $\textbf{AND}$ never examines $q$ when $p$ is FALSE.  Which semantics from the control-flow module did you get for free, and why is it free here?

> **CTQ 2.4** Does applying $\textbf{C}$ to a Church boolean flip its selections?  Reduce $\textbf{C}\, \textbf{TRUE}\, A\, B$ and compare the result with $\textbf{FALSE}\, A\, B$.

Recap: a Church boolean is a selector, so if-then-else is plain application and NOT, AND, and OR are built by choosing what the boolean selects.  Because AND returns `q` only when `p` is TRUE, short-circuit evaluation falls out of the encoding without any extra rule.

---

# Part III: Numbers as Repetition

> **Intuition before numerals:** Zero is "apply f zero times": `lambda f: lambda x: x`.  One is "apply f once": `lambda f: lambda x: f(x)`.  The number N is "apply f N times to x."  Addition is "apply f m+n times."  Multiplication is "apply (n copies of f) m times."  The number is the iteration count; no digits are stored anywhere.

## 3.  Church Numerals

A **Church numeral** encodes the number $n$ as the act of applying a function $n$ times:

$$
\textbf{0} = \lambda f. \lambda x.\, x \qquad
\textbf{1} = \lambda f. \lambda x.\, f\, x \qquad
\textbf{2} = \lambda f. \lambda x.\, f\, (f\, x) \qquad
\textbf{3} = \lambda f. \lambda x.\, f\, (f\, (f\, x))
$$

You met $\textbf{2}$ in *The Lambda Calculus, Part 1* as `twice`.  Arithmetic becomes composition of repetitions:

$$
\textbf{SUCC} = \lambda n. \lambda f. \lambda x.\, f\, (n\, f\, x) \qquad
\textbf{PLUS} = \lambda m. \lambda n. \lambda f. \lambda x.\, m\, f\, (n\, f\, x) \qquad
\textbf{MULT} = \lambda m. \lambda n. \lambda f.\, m\, (n\, f)
$$

Read PLUS aloud: "apply $f$ $n$ times to $x$, then $m$ more times."  Read MULT: "$n$ copies of $f$, repeated $m$ times."

> **Watch out!**  Church numerals are iteration counts, not numbers.  `TWO f x = f(f(x))` applies `f` twice to `x`.  The numeral does not contain the digit 2; it is the behavior of applying something twice.  This is why `church_to_int` works: you hand it the successor function on machine integers and the seed 0, and count how many times successor fires.

**Step-by-step reduction: SUCC ZERO reduces to ONE**

```
SUCC ZERO
= (λn.λf.λx. f (n f x)) (λf.λx. x)
->β λf.λx. f ((λf.λx. x) f x)
->β λf.λx. f ((λx. x) x)
->β λf.λx. f x
= ONE  OK
```

**Step-by-step reduction: PLUS TWO THREE reduces to FIVE**

`SUCC` shows the shape.  Addition shows why the encoding is more than a trick.  Recall `PLUS = λm.λn.λf.λx. m f (n f x)`: "apply `f` `m` times on top of applying it `n` times."

```
PLUS TWO THREE
= (λm.λn.λf.λx. m f (n f x)) (λf.λx. f (f x)) (λf.λx. f (f (f x)))

->β  (λn.λf.λx. TWO f (n f x)) THREE            substitute m := TWO
->β  λf.λx. TWO f (THREE f x)                   substitute n := THREE

    ; expand THREE f x first:
    THREE f x = (λf.λx. f (f (f x))) f x
    ->β (λx. f (f (f x))) x
    ->β f (f (f x))

->   λf.λx. TWO f (f (f (f x)))

    ; now expand TWO f applied to that:
    TWO f (f (f (f x))) = (λf.λx. f (f x)) f (f (f (f x)))
    ->β (λx. f (f x)) (f (f (f x)))
    ->β f (f (f (f (f x))))

->   λf.λx. f (f (f (f (f x))))
=   FIVE  OK                                    five applications of f
```

Count the `f`s at each stage: `THREE f x` contributes three, and `TWO f` wraps two more around them.  Addition of Church numerals is function composition, counted.  You get `m + n` applications of `f` because you applied `f` `n` times and then `m` more times to the result.  Nothing was added; things were nested.

Try `MULT TWO THREE = λf.λx. m (n f) x` on your own with the same method, and watch why it gives six.  `n f` is "apply `f` three times" treated as a single function, and `m` applies that function twice.

**Decode helper, "peek inside" a Church numeral:**

```python
ZERO = lambda f: lambda x: x
SUCC = lambda n: lambda f: lambda x: f(n(f)(x))

def church_to_int(n):
    return n(lambda x: x + 1)(0)

ONE = SUCC(ZERO)
TWO = SUCC(ONE)
print("church_to_int(ZERO) =", church_to_int(ZERO))
print("church_to_int(ONE)  =", church_to_int(ONE))
print("church_to_int(TWO)  =", church_to_int(TWO))
```
@LIA.eval(`["main.py"]`, `none`, `python3 main.py`)

The helper hands the numeral the successor function on Python ints and the seed 0.  If the numeral applies its function twice (as TWO does), you get `0 + 1 + 1 = 2`.  The number of applications is exactly the Church numeral's value.

---

## Church Encodings: Runnable

```python
# Church encodings, executable. Python lambdas ARE lambda calculus terms.

TRUE  = lambda x: lambda y: x          # K  (Kestrel)
FALSE = lambda x: lambda y: y          # KI (Kite)
NOT   = lambda b: b(FALSE)(TRUE)
AND   = lambda p: lambda q: p(q)(p)
OR    = lambda p: lambda q: p(p)(q)
XOR   = lambda p: lambda q: p(NOT(q))(q)

show_bool = lambda b: b("TRUE")("FALSE")    # a boolean selects its own name

# Decode helpers
def church_to_bool(b):
    return b(True)(False)

def church_to_int(n):
    return n(lambda x: x + 1)(0)

print("=== Church Numerals ===")
ZERO  = lambda f: lambda x: x
SUCC  = lambda n: lambda f: lambda x: f(n(f)(x))
PLUS  = lambda m: lambda n: lambda f: lambda x: m(f)(n(f)(x))
MULT  = lambda m: lambda n: lambda f: m(n(f))
EXP   = lambda m: lambda n: n(m)    # m^n; shockingly simple

ONE, TWO = SUCC(ZERO), SUCC(SUCC(ZERO))
THREE    = PLUS(ONE)(TWO)
SIX      = MULT(TWO)(THREE)
EIGHT    = EXP(TWO)(THREE)   # 2^3

print("church_to_int(ZERO)  =", church_to_int(ZERO))
print("church_to_int(ONE)   =", church_to_int(ONE))
print("church_to_int(TWO)   =", church_to_int(TWO))
print("ONE, TWO, 1+2, 2*3  =", church_to_int(ONE), church_to_int(TWO), church_to_int(THREE), church_to_int(SIX))
print("2^3 =", church_to_int(EIGHT))

# if-then-else is just application: b(then)(else)
print("\n=== Church if-then-else ===")
print("if TRUE: 'yes'  =", TRUE("yes")("no"))
print("if FALSE: 'yes' =", FALSE("yes")("no"))

# ISZERO: apply (lambda x: FALSE) n times to TRUE. If n=0, never applied.
ISZERO = lambda n: n(lambda _: FALSE)(TRUE)
print("\n=== ISZERO ===")
for n, val in [(ZERO, "ZERO"), (ONE, "ONE"), (TWO, "TWO")]:
    print(f"ISZERO({val}) = {show_bool(ISZERO(n))}")
```
@LIA.eval(`["main.py"]`, `none`, `python3 main.py`)

---

### Reading the Code

- Every "value" here is a function, and nothing else exists.  `TRUE` and `FALSE` are not booleans in disguise; they are selectors.  `IF` works by applying its condition to the two branches and letting the condition choose.
- `church_to_int` is a decoder, not part of the encoding.  A Church numeral `n` means "apply `f` to `x`, `n` times."  Handing it Python's successor and `0` is only one way to read it back out.
- `SUCC` wraps one more application around whatever it was given.  That is why numerals compose without any arithmetic anywhere in sight.
- `ISZERO` applies `lambda _: FALSE` exactly `n` times to `TRUE`.  Applied zero times, the `TRUE` survives untouched; applied even once, it is gone.  With no numbers available, that is the only way to ask "is this zero?".

### Try It Yourself

Build operators the deck has not given you, using nothing but functions.

```python
TRUE  = lambda x: lambda y: x
FALSE = lambda x: lambda y: y
IF    = lambda b: lambda t: lambda f: b(t)(f)

ZERO  = lambda f: lambda x: x
SUCC  = lambda n: lambda f: lambda x: f(n(f)(x))
ADD   = lambda m: lambda n: lambda f: lambda x: m(f)(n(f)(x))
MULT  = lambda m: lambda n: lambda f: m(n(f))

to_int  = lambda n: n(lambda k: k + 1)(0)
to_bool = lambda b: b(True)(False)

ONE, TWO = SUCC(ZERO), SUCC(SUCC(ZERO))
THREE    = SUCC(TWO)

print("=== What you already have ===")
print("  to_int(THREE)            = " + str(to_int(THREE)))
print("  to_int(ADD(TWO)(THREE))  = " + str(to_int(ADD(TWO)(THREE))))
print("  to_int(MULT(TWO)(THREE)) = " + str(to_int(MULT(TWO)(THREE))))

# TODO 1: AND, OR, NOT. A Church boolean IS a selector, so each of these
#         is written by choosing what p should select.
#         Hint for the first: AND = lambda p: lambda q: p(q)(p)
AND = lambda p: lambda q: p            # replace me
OR  = lambda p: lambda q: p            # replace me
NOT = lambda p: p                      # replace me

print("\n=== Your booleans (all True until you fix the stubs) ===")
for name, expr in [("AND(TRUE)(FALSE)", AND(TRUE)(FALSE)),
                   ("AND(TRUE)(TRUE)",  AND(TRUE)(TRUE)),
                   ("OR(FALSE)(TRUE)",  OR(FALSE)(TRUE)),
                   ("NOT(TRUE)",        NOT(TRUE))]:
    print("  " + name.ljust(20) + " = " + str(to_bool(expr)))
print("  want: False, True, True, False")

# TODO 2: POW(m)(n) is m to the power n, and it is SHORTER than MULT.
#         Think about what happens when you apply one numeral to another.
POW = lambda m: lambda n: m            # replace me
print("\n  to_int(POW(TWO)(THREE)) = " + str(to_int(POW(TWO)(THREE))) + "   (want 8)")

# TODO 3: to_int decodes by counting. Decode THREE a DIFFERENT way: hand it
#         a function that appends to a string, so THREE becomes "fff".
#         What does that tell you about what a numeral actually is?
```
@LIA.eval(`["main.py"]`, `none`, `python3 main.py`)

Expected output: the first three lines are 3, 5 and 6.  Your four booleans all print `True` because the stubs return `p`, and `POW` reports 2 instead of 8.  Fix the stubs and the wanted values appear.

## Model 3: Interrogate the Encodings

### Critical Thinking Questions

> **CTQ 3.1** `church_to_int` decodes a numeral by handing it the successor function on machine integers and the seed 0.  Explain why this works in one sentence that begins "A Church numeral n is...".

> **CTQ 3.2** Reduce $\textbf{SUCC}\; \textbf{1}$ by hand to confirm it is $\textbf{2}$ (expect two or three careful steps).  The trace for `SUCC ZERO` above is a model; repeat the pattern one numeral up.

> **CTQ 3.3** Verify in code that $\textbf{MULT}\, \textbf{2}\, \textbf{3}$ and $\textbf{PLUS}\, \textbf{3}\, \textbf{3}$ decode equally.  Then explain why MULT is so short: what is `n(f)`, and what does `m` do to that?

> **CTQ 3.4** Where is the data?  A Church numeral stores no digits anywhere.  Connect this to the lesson from homoiconicity week, and to the claim "data is frozen behavior."

Under Church encoding, the expression `b(t)(e)` where b is a Church boolean implements if-then-else because:

[( )] Python evaluates booleans specially
[(X)] TRUE and FALSE are themselves selector functions returning their first and second arguments respectively
[( )] The lambda calculus has a built-in conditional form
[( )] t and e must be numerals

Recap: a Church numeral is a function that applies `f` to `x` a fixed number of times, so the number is the count of applications.  Addition nests one numeral's applications inside another's, and multiplication treats `n f` as a single function and repeats it `m` times.

---

# Part IV: Recursion Without Names

## 4.  The Problem: A Lambda Has No Name to Call

A lambda term has no name at the moment you write it, so it cannot call itself by name.  Every recursive function you have written before today worked because a name was bound before the body ran: `sumlist` calls `sumlist`, and `fact` calls `fact`.  The pure calculus has no `define`, so there is nothing to recurse through.

Everything else on today's list survived the reduction to functions.  Booleans became selectors and numerals became repetition.  Repetition itself is the one thing that looks like it needs something the calculus does not have.

State the goal precisely before pushing any symbols.  A **fixed point** of a function $f$ is a value $v$ with $f\, v = v$.  We want a term $\textbf{Y}$ that finds one for every $f$:

$$
\textbf{Y}\, f \;=_\beta\; f\, (\textbf{Y}\, f)
$$

This is the **fixed-point equation**, and a term that satisfies it is a **fixed-point combinator**.  Read it as a promise.  If $f$ is a function that, handed "the rest of the recursion," produces one more layer of a recursive definition, then $\textbf{Y}\, f$ is that definition unrolled as far as anyone ever asks for it.

We build that term from a factorial that cannot be written, fixing one problem at a time until a combinator falls out.  An extension at the end of this page then derives the same term backwards from the equation above in four lines, as a check that the construction was not a lucky accident.

> **Watch out!**  Nothing in this Part defines recursion in terms of recursion.  Every step is beta reduction, and the finished $\textbf{Y}$ is a closed term you could write on a whiteboard from memory.  If a step ever feels circular, find where the repeated subterm came from: it always came from substituting, never from calling something by name.

---

## 5.  Deriving the Combinator One Step at a Time

### Step 0: The Term You Cannot Write

Here is factorial as you want to write it, using the encodings from Part III and the predecessor `PRED` built from pairs in the extension at the end of this page:

$$
\text{FACT} = \lambda n.\, \text{IF}\, (\text{ISZERO}\, n)\, \overline{1}\, (\text{MULT}\, n\, (\;???\;(\text{PRED}\, n)))
$$

The whole exercise is that box.  In Scheme, `define` puts `FACT` there before the body ever runs.  Here there is no `define`, the term has no name, and a term cannot refer to itself.  So stop reaching outward for a name, and ask instead what a lambda term can get at.

It can get at its arguments.  That is the only thing it can get at.

### Step 1: Hand the Function a Copy of Itself

If a function cannot reach itself, hand it itself.  Add a parameter for it and pass the whole term in as an ordinary argument:

$$
F = \lambda \textit{self}.\, \lambda n.\, \text{IF}\, (\text{ISZERO}\, n)\, \overline{1}\, (\text{MULT}\, n\, ((\textit{self}\ \textit{self})\, (\text{PRED}\, n)))
$$

Two things to notice.  The recursive call is $(\textit{self}\ \textit{self})$ rather than $\textit{self}$, because $\textit{self}$ arrives as a function still waiting to be handed a copy of itself.  And you do not start $F$ by calling it on a number; you start it by applying it to itself, $F\, F$.

Watch the recursion appear out of pure substitution:

```
F F 3
= (λself. λn. IF (ISZERO n) 1 (MULT n ((self self) (PRED n)))) F 3
->β (λn. IF (ISZERO n) 1 (MULT n ((F F) (PRED n)))) 3      <- self := F
->β IF (ISZERO 3) 1 (MULT 3 ((F F) 2))
->β MULT 3 ((F F) 2)                                        <- (F F) again: back where we began
->β MULT 3 (MULT 2 ((F F) 1))
->β MULT 3 (MULT 2 (MULT 1 ((F F) 0)))
->β MULT 3 (MULT 2 (MULT 1 1))                              <- ISZERO 0 selects the base case
=  6                                                        OK
```

That is a working recursive factorial with no name anywhere in it.  The problem is solved.  Everything after this point is refactoring, not new power; the goal is only to make the term tolerable to read.

### Step 2: Hide the Self-Application Behind a Name

The body of $F$ is unpleasant because it says $(\textit{self}\ \textit{self})$ where a reader wants to see "factorial of."  The plumbing has leaked into the arithmetic.  So bind the plumbing to a local name.  There are no `let` forms here either, but a `let` is only an applied lambda, so write it as one:

$$
F = \lambda \textit{self}.\, \underbrace{(\lambda \textit{rec}.\, \lambda n.\, \text{IF}\, (\text{ISZERO}\, n)\, \overline{1}\, (\text{MULT}\, n\, (\textit{rec}\, (\text{PRED}\, n))))}_{\text{clean: this is just factorial}}\, \underbrace{(\lambda v.\, ((\textit{self}\ \textit{self})\, v))}_{\text{the plumbing}}
$$

The underbraced left half now reads exactly like factorial written with a helper called $\textit{rec}$.  The right half is the self-application, wrapped in $\lambda v$ so that it is handed along as a function rather than run on the spot.  Remember that wrapper.  In Step 5 we throw it away, and in section 12 (an extension) we find out that it mattered after all.

### Step 3: Lift the Logic Out

The clean half no longer mentions $\textit{self}$, so nothing keeps it inside $F$.  Pull it out and give it a name of its own:

$$
G = \lambda \textit{rec}.\, \lambda n.\, \text{IF}\, (\text{ISZERO}\, n)\, \overline{1}\, (\text{MULT}\, n\, (\textit{rec}\, (\text{PRED}\, n)))
$$

$$
F = \lambda \textit{self}.\, G\, (\lambda v.\, ((\textit{self}\ \textit{self})\, v))
\qquad\qquad
\text{FACT} = F\, F
$$

$G$ is the **generator**: a function that takes "the rest of the recursion" as a parameter and never names itself.  It is not recursive.  It has no name of its own, so it cannot mention one.  It is an ordinary function of one argument that calls whatever it is handed, and every recursive function you will ever write can be put in this shape.

### Step 4: Abstract Over the Generator

$F$ mentions $G$ only because we typed $G$ there.  Nothing about $F$ is specific to factorial, so make $G$ a parameter and inline $F$ into $F\, F$:

$$
\textbf{Z} = \lambda f.\, (\lambda x.\, f\, (\lambda v.\, ((x\, x)\, v)))\, (\lambda x.\, f\, (\lambda v.\, ((x\, x)\, v)))
$$

Now $\text{FACT} = \textbf{Z}\, G$.  This is a combinator: closed, generic, and finished.  Hand it any generator and it hands you back the recursive function that generator describes.  Nothing about factorials survives in it.

### Step 5: Strip the Delay

One piece is still unexplained.  What is $\lambda v.\, ((x\, x)\, v)$ doing?  It takes an argument and passes it straight to $(x\, x)$, unchanged.  It computes nothing.

In the pure calculus, $\lambda v.\, (M\, v)$ and $M$ are interchangeable whenever $v$ is not free in $M$.  That is the **eta rule**.  So delete the wrapper:

$$
\textbf{Y} = \lambda f.\, (\lambda x.\, f\, (x\, x))\, (\lambda x.\, f\, (x\, x))
$$

That is the Y combinator, the classic fixed-point combinator.  Notice how it arrived: nobody invented it, and it was left behind when the last piece of scaffolding was removed.  $\textbf{Y}$ is $\textbf{Z}$ with one eta-expansion undone.  Remember that, because section 12 is about the one situation in which undoing it is a catastrophe.

---

## Model 4: The Five Steps, Running

Every step above is executable.  Run the cell and watch the machinery separate itself from the factorial one line at a time.  Each `print` corresponds to one numbered step.

```python
# The derivation, each step runnable, so you can watch the machinery
# separate itself from the factorial one line at a time.

# Step 0 does not appear here, because it cannot be written:
#     lambda n: 1 if n == 0 else n * ???(n - 1)
# There is no name to put where ??? is.

# Step 1: hand the function a copy of itself, as an ordinary argument.
step1 = lambda self, n: 1 if n == 0 else n * self(self, n - 1)
print("step1 :", step1(step1, 5), "  called as step1(step1, 5)")

# Step 1, curried, one argument at a time, as the calculus insists.
# 'self' is a function you must apply to itself before you can use it.
step1c = lambda self: lambda n: 1 if n == 0 else n * self(self)(n - 1)
print("step1c:", step1c(step1c)(5), "  called as step1c(step1c)(5)")

# Step 2: the body is ugly because self(self) is spelled out inside it.
# Bind that self-application to a name so the body reads like factorial.
step2 = lambda self: (
    lambda rec: lambda n: 1 if n == 0 else n * rec(n - 1)
)(lambda v: self(self)(v))
print("step2 :", step2(step2)(5), "  the inner body now says rec(n - 1)")

# Step 3: that inner body never mentions self, so lift it out.  fact_gen is
# pure factorial logic: not recursive, no name of its own, calls what it gets.
fact_gen = lambda rec: lambda n: 1 if n == 0 else n * rec(n - 1)
step3 = lambda self: fact_gen(lambda v: self(self)(v))
print("step3 :", step3(step3)(5), "  logic and machinery now separate")

# Step 4: step3 mentions fact_gen only because we typed it there.  Abstract
# over it and nothing about factorial is left.  What remains is a combinator.
Z = lambda f: (lambda x: f(lambda v: (x(x))(v)))(
               lambda x: f(lambda v: (x(x))(v)))
print("step4 :", Z(fact_gen)(5), "  Z(fact_gen), and Z knows nothing of factorials")

# Proof that nothing about factorial survived: hand Z other generators.
fib_gen = lambda rec: lambda n: n if n < 2 else rec(n - 1) + rec(n - 2)
sum_gen = lambda rec: lambda xs: 0 if not xs else xs[0] + rec(xs[1:])
print()
print("Z(fib_gen)(10)           =", Z(fib_gen)(10))
print("Z(sum_gen)([1, 2, 3, 4]) =", Z(sum_gen)([1, 2, 3, 4]))

# Expected output:
# step1 : 120   called as step1(step1, 5)
# step1c: 120   called as step1c(step1c)(5)
# step2 : 120   the inner body now says rec(n - 1)
# step3 : 120   logic and machinery now separate
# step4 : 120   Z(fact_gen), and Z knows nothing of factorials
#
# Z(fib_gen)(10)           = 55
# Z(sum_gen)([1, 2, 3, 4]) = 10
```
@LIA.eval(`["main.py"]`, `none`, `python3 main.py`)

### Reading the Code

- Every step prints `120`.  That is the point: no step adds power, and steps 2 through 4 are refactoring.  All the difficulty lives in step 1, and step 1 is three tokens long.
- `step1` and `step1c` differ only in currying.  Python lets you write `self(self, n - 1)` with a comma.  The calculus has no commas, so `(self self) (PRED n)` is the honest spelling, and `step1c` is the one to compare against the math.
- `fact_gen` is the shape worth memorizing.  It takes `rec`, calls `rec(n - 1)` exactly where a recursive call belongs, and is not recursive itself.  You can bend any recursive function into this shape mechanically.
- `Z(fib_gen)` and `Z(sum_gen)` show that step 4 finished the job.  If any trace of factorial had survived in `Z`, those two lines could not work.

### Critical Thinking Questions

> **CTQ 4.1** Take the reduction of `F F 3` in Step 1 and continue it for `F F 4`, writing every substitution.  At which arrow does the term `(F F)` reappear, and what would happen to the reduction if `ISZERO` never selected the base case?

> **CTQ 4.2** Step 2 claims the two halves are "clean" and "plumbing."  Circle every occurrence of $\textit{self}$ in Step 2's term.  How many are in the clean half?  Why does that number make Step 3 possible?

> **CTQ 4.3** Write `sum_gen` for Scheme lists rather than Python lists, in the same shape as `fact_gen`, using `null?`, `car`, and `cdr`.  Then say in one sentence what `rec` stands in for.

---

# Part V: Closures, the Problem and the Mechanism

A language has **first-class functions** when a function is an ordinary value: you can store it in a variable, pass it as an argument, and return it from another function.  A language has static scope when a name refers to the variable declared where the function was written.  Put those two rules together and a function can escape the scope where it was born.  To keep working, it must carry that scope with it.  What it carries is the environment chain you built in *Binding, Scope, and Environments*.  The bundle of code plus captured environment is a closure.  It is the mechanism behind `make_adder`, behind every Church encoding you ran in Python today, and behind the function values your interpreter supports.

### Key Concepts

This glossary defines the terms the activity uses.  Come back to it whenever a term starts to feel slippery.

| Term | Plain-English meaning | Why it matters |
|------|-----------------------|----------------|
| **Closure** | A function bundled with the environment where it was defined | The mechanism that lets a function read variables after their scope ends |
| **First-class function** | A function treated as an ordinary value: stored, passed, returned | Without this, closures never arise; with it, they are unavoidable |
| **Defining environment** | The scope chain in effect at the moment a function is created | This is what the closure captures, never the caller's environment |
| **Captured variable** | A variable from an enclosing scope that an inner function reads or writes | The closure keeps that variable alive after its scope returns |
| **Capture by reference** | The closure holds a pointer to the *binding*, not a snapshot of the value | Explains why closures see later changes, and the loop-variable trap |
| **Lexical (static) scope** | Names resolve where the function was *written* in the source | The rule Python, JavaScript, and Scheme use; implemented by one parent-pointer choice |
| **Dynamic scope** | Names resolve in whoever *called* the function | The historical alternative; a contrast that shows what lexical scope buys |
| **Environment diagram** | Boxes for scopes, arrows for parent and capture pointers | The picture that makes every closure question answerable |
| **Loop-variable trap** | All closures made in a loop share one binding, so all see its final value | The most common closure bug in Python and JavaScript alike |
| **Factory function** | A function whose every call creates a fresh scope and returns a closure over it | The standard fix for the trap, and the pattern behind `make_adder` |
| **Mutable cell / `nonlocal`** | The way an inner function assigns into a captured binding | How closures hold changing *state* as well as constants |

---

A function defined inside another function keeps reading the variables of its birth environment after the enclosing function has returned.  One analogy: a contractor trained in your workshop still knows the workshop's tools and rules after the workshop closes.  The analogy stops there, because the contractor carries a memory of the workshop while a closure carries a live link to it.  This section uses the classic `make_adder` example to show why this behavior is necessary and useful.

## 6.  A Function Outlives Its Scope

```python
def make_adder(n):
    def adder(x):
        return x + n
    return adder

add5  = make_adder(5)
add10 = make_adder(10)

print(f"add5(3)  = {add5(3)}")    # 8
print(f"add10(3) = {add10(3)}")   # 13

# make_adder has RETURNED, yet n=5 and n=10 still live somewhere.
# Where?
print(f"add5's closure cells: {add5.__closure__[0].cell_contents}")
print(f"add10's closure cells: {add10.__closure__[0].cell_contents}")
```
@LIA.eval(`["main.py"]`, `none`, `python3 main.py`)

By the lifetime rules of the environments module, `make_adder`'s local scope should die at `return` and take `n` with it.  Yet `add5` still finds `n = 5`.  The resolution is that **a function value is not just code; it is a closure**, a pair of `(code, defining_environment)`.  When Python created `adder`, it captured a reference to the environment where `n` was bound.  That environment survives because the closure still points to it.  Lifetime follows reachability: an environment stays alive as long as something, such as a closure, can still reach it.

$$\text{closure} = \langle \text{params}, \text{body}, E_{\text{def}} \rangle$$

Calling a closure brings its birthplace back into use.  The call `add5(10)` creates a fresh environment for the parameter (`x = 10`).  The parent of that environment is the closure's captured environment (where `n = 5`), not the caller's environment.  That parent choice is static scoping enforced at runtime.  The entire difference between lexical and dynamic scope is one decision about which parent pointer to use.

Remember two things from this section.  A closure is code plus its defining environment.  A call runs the body in a child of that captured environment.

**Critical Thinking Questions (CTQs)**

> **CTQ 5.1** Draw the environment diagram at `print(add5(3))`: the global frame, the still-alive `make_adder` frame holding `n = 5`, the call frame holding `x = 3`, and every parent arrow.  Which arrow embodies "static scope"?

> **CTQ 5.2** After `add5 = make_adder(5)` and `add10 = make_adder(10)`, how many `make_adder` environments exist at the same time?  What does each closure's captured pointer tell you about whether closures *copy* or *reference* their environment?

> **CTQ 5.3** In the lambda calculus, `(λn. λx. x + n) 5` reduces to `λx. x + 5` by *substitution*: the 5 is pasted into the body.  State the relationship: closures are an *implementation strategy* for what substitution *specifies*.  Why might an interpreter prefer environments over literal substitution for large function bodies?

---

A closure holds a live reference to a variable binding.  Any change to that variable after the closure is created is visible through the closure.  One analogy: a closure is a security camera pointed at a shelf, not a photograph of the shelf.  When you look at the feed later, you see whatever is on the shelf now.  The analogy stops at the camera's one-way view, because a closure can also write to the shelf through `nonlocal` or a mutable cell.

> **Watch out!**  A common mistake is to think a closure *copies* the value of a variable at the moment the closure is created.  It does not.  It captures a *reference* to the binding.  If the variable changes after the closure is defined, the closure sees the new value.  The `get_x` example below demonstrates this directly.

## Model 5: Closures Capture, Not Copy

```python
# CRITICAL: closures capture the VARIABLE BINDING, not the value at capture time

x = 10

def get_x():
    return x    # captures the variable x, not the value 10

print(f"get_x() = {get_x()}")   # 10

x = 99
print(f"After x=99, get_x() = {get_x()}")   # 99, the closure sees the new value!

# Contrast: a default argument captures the VALUE at definition time
def get_x_snapshot(val=x):
    return val

x = 42
print(f"get_x_snapshot() = {get_x_snapshot()}")   # 99, not 42, captured at def time

# Multiple closures sharing a mutable cell:
def make_counter():
    count = [0]   # list so we can mutate it (Python 2 workaround; Python 3 uses nonlocal)
    def increment():
        count[0] += 1
        return count[0]
    def reset():
        count[0] = 0
    return increment, reset

inc, rst = make_counter()
print(inc(), inc(), inc())   # 1 2 3
rst()
print(inc())                 # 1, both closures share the same count cell
```
@LIA.eval(`["main.py"]`, `none`, `python3 main.py`)

> **CTQ 5.4** `get_x()` returns 99 after `x = 99`.  What does this prove about whether closures copy or reference the captured binding?

> **CTQ 5.5** The `make_counter` example has TWO closures (`increment` and `reset`) that share ONE captured environment containing `count`.  Draw the environment diagram.  Which arrow makes them share state?

### Reading the Code

These notes cover the Model 5 code.

- The first block reassigns the captured variable *after* the closure is built, and the closure reports the new value.  That proves capture by reference.  If the closure had copied, it would still report the old value.
- The default-argument contrast is the control case.  `get_x_snapshot(val=x)` evaluates `x` once, at definition, and stores the result in `val`.  It is not a closure over `x` at all.
- The shared-mutable-cell block is the same mechanism used on purpose.  Two functions closing over one binding is how you get an object with two methods, which is where the Extension on closures and objects goes.

### Try It Yourself

Find out, by experiment, exactly what Python keeps in a closure.

```python
def make():
    secret = "original"
    hidden  = "never used by the inner function"
    def peek():
        return secret            # only 'secret' is referenced
    def poke(v):
        nonlocal secret
        secret = v
    return peek, poke

peek, poke = make()
print("=== Capture is by reference, not by value ===")
print(f"  peek()          -> {peek()!r}")
poke("changed")
print(f"  after poke      -> {peek()!r}")

print("\n=== What is actually in the closure? ===")
names = peek.__code__.co_freevars
cells = [c.cell_contents for c in (peek.__closure__ or ())]
print(f"  peek captured: {dict(zip(names, cells))}")

# TODO 1: 'hidden' was in scope when peek was defined, but is it captured?
#         Look at the printed dict and say why or why not. What does that
#         tell you about what a closure costs in memory?

# TODO 2: peek and poke were made by the SAME call to make(). Print
#         poke.__closure__ too and compare the cell objects with
#         `peek.__closure__[0] is poke.__closure__[0]`. What does the
#         answer say about how they share state?

# TODO 3: call make() a second time and confirm the new peek is unaffected
#         by the old poke. How many 'secret' variables exist now?
```
@LIA.eval(`["main.py"]`, `none`, `python3 main.py`)

Expected output: `'original'`, then `'changed'`, then a dict with exactly one entry.  The absence of `hidden` from that dict is the answer to TODO 1.

---

# Part VI: Closures in Your Own Interpreter

## 7.  Theory: One Field, One Line

Part V used Python to show you *its* closures.  Now you build your own.  It takes very little: a closure is a three-field record, and the entire static-versus-dynamic decision is one word in one line.

When the evaluator meets a function expression, it does **not** evaluate the body.  It packages three things and returns them:

```
Closure(param, body, env)
```

The `param` and `body` come straight off the abstract syntax tree (AST).  The third field, `env`, is the environment at the moment the function was created.  This is the function's lexical environment: the scope chain in force where the function appears in the source.  Capturing it is the one thing this record exists to do.

When the evaluator later meets a call, it evaluates the function, evaluates the argument, and then evaluates the body in

```
closure.env.extend(closure.param, argument)
```

Read that line carefully, because the session turns on it.  The body runs in a child of the closure's captured environment, not a child of the environment where the call sits.  Change `closure.env` to the caller's `env` on that one line and you have written a dynamically scoped language.  Nothing else has to change.

## Examples: Which Environment Wins, by Hand

Take this program and work out both answers before running anything:

```
let x = 10 in
let f = fun y -> x + y in
let x = 99 in
  f(1)
```

Fill in the table.  The only question that matters is which `x` the body of `f` sees.

| Rule | Which `x` does `f`'s body find | Result |
|------|-------------------------------|--------|
| Lexical: body runs in a child of `closure.env` | the `x` in scope where `fun` was written | ? |
| Dynamic: body runs in a child of the caller's `env` | the `x` in scope where `f(1)` was written | ? |

Now say which line of code you would change to move from one row to the other.  There is exactly one.

## Model 6: Build the Closure, Then Flip the Switch

This is a complete evaluator for a language with first-class functions.  The `LEXICAL` flag at the top selects which environment a call body runs in, and the *same* program runs under both settings.

```python
from dataclasses import dataclass
from typing import Any

@dataclass
class Num:  value: float
@dataclass
class Var:  name: str
@dataclass
class Add:  left: Any; right: Any
@dataclass
class Fun:  param: str; body: Any
@dataclass
class Call: fn: Any; arg: Any
@dataclass
class Let:  name: str; val: Any; body: Any

class Env:
    def __init__(self, bindings=None, parent=None):
        self.bindings = bindings or {}
        self.parent = parent
    def lookup(self, name):
        env = self
        while env is not None:
            if name in env.bindings:
                return env.bindings[name]
            env = env.parent
        raise NameError(f"undefined: {name!r}")
    def extend(self, name, value):
        return Env({name: value}, self)

@dataclass
class Closure:
    param: str
    body:  Any
    env:   Any          # <-- THE capture. Everything else is bookkeeping.

def interp(e, env, lexical):
    if isinstance(e, Num): return e.value
    if isinstance(e, Var): return env.lookup(e.name)
    if isinstance(e, Add): return interp(e.left, env, lexical) + interp(e.right, env, lexical)

    if isinstance(e, Fun):
        return Closure(e.param, e.body, env)        # capture the DEFINING env

    if isinstance(e, Let):
        v = interp(e.val, env, lexical)
        return interp(e.body, env.extend(e.name, v), lexical)

    if isinstance(e, Call):
        fn  = interp(e.fn,  env, lexical)
        arg = interp(e.arg, env, lexical)
        if not isinstance(fn, Closure):
            raise TypeError(f"not a function: {fn!r}")
        # ------------------------------------------------------------------
        # THE ONE LINE. fn.env is lexical scope; env is dynamic scope.
        base = fn.env if lexical else env
        # ------------------------------------------------------------------
        return interp(fn.body, base.extend(fn.param, arg), lexical)

    raise ValueError(f"unknown node: {type(e).__name__}")

#   let x = 10 in let f = fun y -> x + y in let x = 99 in f(1)
program = Let("x", Num(10),
          Let("f", Fun("y", Add(Var("x"), Var("y"))),
          Let("x", Num(99),
          Call(Var("f"), Num(1)))))

print("=== The same program, the same evaluator, one line different ===")
for lexical in (True, False):
    label = "lexical (fn.env)" if lexical else "dynamic (env)"
    print(f"  {label:20} -> {interp(program, Env(), lexical)}")

print("\n  11 means the body found the x that was in scope where 'fun' was")
print("     written. 100 means it found the x in scope at the call.")

# A second program, to show this is not a fluke of that one shape.
#   let n = 1 in
#   let bump = fun k -> n + k in
#   let n = 500 in bump(bump(0))
program2 = Let("n", Num(1),
           Let("bump", Fun("k", Add(Var("n"), Var("k"))),
           Let("n", Num(500),
           Call(Var("bump"), Call(Var("bump"), Num(0))))))

print("\n=== Nested calls, same switch ===")
for lexical in (True, False):
    label = "lexical" if lexical else "dynamic"
    print(f"  {label:20} -> {interp(program2, Env(), lexical)}")
```
@LIA.eval(`["main.py"]`, `none`, `python3 main.py`)

### Reading the Code

- The `Fun` branch is three words long and never touches the body.  A function value is *not* a running thing.  It is a suspended thing plus the environment it was suspended in.
- `Closure.env` is the single field that implements static scope.  The evaluator fills it in at `Fun`, reads it at `Call`, and never modifies it.
- `base = fn.env if lexical else env` is the entire scoping discipline of the language, on one line.  Every hard question about scope reduces to which of those two names you write there.
- `extend` returns a *new* `Env` rather than mutating.  That is what lets two calls to the same closure run without seeing each other's arguments, and it is why recursion works at all.
- `Call` evaluates `fn` and `arg` in the *current* `env` under both settings.  Only the body's environment changes.  Getting that wrong gives a language where even the argument expression resolves strangely.

> **Watch out!**  It is tempting to store the *values* of the free variables in the closure instead of the environment: capture `x = 10` rather than a pointer to the frame holding `x`.  That works until something reassigns `x`.  Then your closure reads a stale copy while Python's would see the update.  Model 5 already showed the difference; this is where you either preserve it or lose it.

Remember two things from this part.  `Fun` captures the defining environment and evaluates nothing.  `Call` extends that captured environment, and swapping it for the caller's environment is the whole difference between lexical and dynamic scope.

### Critical Thinking Questions

> **CTQ 6.1** Run the model and record all four numbers.  For the first program, which result is 11 and which is 100?  Explain each in one sentence using the words "defining" and "calling."

> **CTQ 6.2** `Closure` holds `env`, but `Env.extend` never copies bindings.  If some later statement reassigns `x` in the captured frame, does the closure see the new value or the old one?  Which of the two capture strategies from Model 5 does that make this?

> **CTQ 6.3** Recursion is not implemented anywhere in this evaluator, yet `bump(bump(0))` works.  What would you have to add for a function to call *itself* by name, and why is that harder than it looks?  (Hint: at the moment `Fun` runs, is the function's own name in `env` yet?)

> **CTQ 6.4** Write down what your team's language does, and put it in `SEMANTICS.md` as one sentence naming the environment a call body runs in.

### Try It Yourself

Add recursion, which is the one thing the model above cannot do.

```python
from dataclasses import dataclass
from typing import Any

@dataclass
class Num:  value: float
@dataclass
class Var:  name: str
@dataclass
class Add:  left: Any; right: Any
@dataclass
class Mul:  left: Any; right: Any
@dataclass
class If0:  test: Any; then_e: Any; else_e: Any
@dataclass
class Fun:  param: str; body: Any
@dataclass
class Call: fn: Any; arg: Any
@dataclass
class Let:  name: str; val: Any; body: Any

class Env:
    def __init__(self, bindings=None, parent=None):
        self.bindings = bindings or {}
        self.parent = parent
    def lookup(self, name):
        env = self
        while env is not None:
            if name in env.bindings: return env.bindings[name]
            env = env.parent
        raise NameError(f"undefined: {name!r}")
    def extend(self, name, value):
        return Env({name: value}, self)

@dataclass
class Closure:
    param: str; body: Any; env: Any

def interp(e, env):
    if isinstance(e, Num): return e.value
    if isinstance(e, Var): return env.lookup(e.name)
    if isinstance(e, Add): return interp(e.left, env) + interp(e.right, env)
    if isinstance(e, Mul): return interp(e.left, env) * interp(e.right, env)
    if isinstance(e, If0):
        return interp(e.then_e, env) if interp(e.test, env) == 0 else interp(e.else_e, env)
    if isinstance(e, Fun):  return Closure(e.param, e.body, env)
    if isinstance(e, Let):
        v = interp(e.val, env)
        return interp(e.body, env.extend(e.name, v))
    if isinstance(e, Call):
        fn, arg = interp(e.fn, env), interp(e.arg, env)
        return interp(fn.body, fn.env.extend(fn.param, arg))
    raise ValueError(type(e).__name__)

#   let fact = fun n -> if0 n then 1 else n * fact(n - 1) in fact(5)
fact_body = If0(Var("n"),
                Num(1),
                Mul(Var("n"), Call(Var("fact"), Add(Var("n"), Num(-1)))))
program = Let("fact", Fun("n", fact_body), Call(Var("fact"), Num(5)))

try:
    print(f"  fact(5) = {interp(program, Env())}")
except NameError as err:
    print(f"  fact(5) -> NameError: {err}")
    print("  The closure captured env BEFORE 'fact' was bound into it,")
    print("  so the body cannot see its own name.")

# TODO 1: fix it. The trick has a name: tie the knot. After building the
#         Closure for fact, reach into the closure's captured environment
#         and define "fact" to point at the closure itself.
#         Two lines, and fact(5) prints 120.
#
# TODO 2: having done that, draw the environment. It now contains a
#         pointer to a closure whose env is that same environment. What
#         is that structure called, and what does it mean for the garbage
#         collector?
#
# TODO 3: most real languages give recursion its own form (letrec, or a
#         'def' statement) rather than making the programmer tie the knot.
#         Which does your language do, and why?
```
@LIA.eval(`["main.py"]`, `none`, `python3 main.py`)

Expected output as written: a `NameError` naming `fact`, with the explanation.  Once TODO 1 is in, `fact(5) = 120`.  Those two lines are why `letrec` exists at all.

---

# Part VII: Two Ways to Get What the Calculus Lacks

## 8.  A Combinator and a Captured Binding

In Part IV you derived $\textbf{Z}$ and then $\textbf{Y}$, and used $\textbf{Z}$ to make a function call itself with no name anywhere in the term.  The generator `fact_gen` took "the rest of the recursion" as an ordinary parameter, and the combinator supplied it.  Nothing was captured and nothing was mutated.  There was only application and substitution.

The closure of Parts V and VI is nothing like that.  A closure gets its power from holding on to a *binding*, and `set!` gets its power from writing to that binding.  The counter remembers because the frame outlived the call that made it, and because somebody was allowed to change what the frame holds.

The two mechanisms are unrelated.  One is pure and needs no notion of memory at all; the other is nothing but memory.  Neither is derivable from the other in any obvious way.  And yet both exist to buy the same missing thing.  The bare calculus gives you no way to refer back to something, whether that something is a function you are in the middle of defining or a value you set on the last call.  The combinator buys self-reference without names.  The closure buys names that persist without a global.

This is also why CTQ 6.3 was harder than it looked.  When `Fun` runs, the function's own name is not in `env` yet, so a closure cannot capture it.  The fix in the Try It Yourself is to reach into the captured environment afterward and point the name at the closure.  That is called *tying the knot*, and it is the mutation-based answer to exactly the problem $\textbf{Y}$ solves without mutation.  Your interpreter is free to pick either one.  Most real languages pick the knot, because it is cheaper and because programmers want to write the name.

## Model 7: Choose Your Mechanism

> **CTQ 7.1** Scheme ships both mechanisms.  Write `factorial` twice, once with `define` and a self-reference, once with $\textbf{Z}$ and a generator.  Which one would you hand a first-year student, and which one would you rather implement in your evaluator?  Notice those may not be the same answer.

> **CTQ 7.2** Tying the knot creates a cycle: an environment holds a closure whose captured environment is that same environment.  $\textbf{Z}$ creates no cycle at all.  What does that difference cost a garbage collector, and does it change your answer to CTQ 7.1?

> **CTQ 7.3** A memoized function keeps a cache in a captured binding, so it mutates on every miss.  Could you memoize a $\textbf{Z}$-built function without introducing any mutation?  If not, say precisely what would have to change about the language.

---

**In-class work stops here.**  Everything below is homework and going-deeper material; attempt the exercises before the Lambda Calculus lab is due and before your team's next sprint.

# Check Your Understanding

`TRUE = \x.\y.x` and `FALSE = \x.\y.y`. A Church boolean is best described as:

[(X)] A selector: a function that picks one of the two things handed to it
[( )] A number in disguise, 1 for true and 0 for false
[( )] A primitive the lambda calculus provides
[( )] A pair whose first element is a flag

---

`IF = \b.\t.\f. b t f` works because:

[(X)] The boolean itself does the choosing; `IF` only hands it the two branches
[( )] It compares `b` against `TRUE`
[( )] It evaluates both branches and discards one
[( )] It relies on short-circuit evaluation

---

The Church numeral `THREE` is:

[(X)] A function that applies its first argument to its second, three times
[( )] The literal 3, encoded in binary
[( )] A list of three elements
[( )] A pair of `TWO` and `SUCC`

---

`ISZERO n` applies `\_.FALSE` to `TRUE`, `n` times. That decides zero because:

[(X)] Applied zero times the `TRUE` is never replaced; applied any positive number of times it becomes `FALSE`
[( )] It compares `n` against `ZERO` directly
[( )] `FALSE` absorbs any further application
[( )] Church numerals carry a zero flag

---

`PRED` is far harder than `SUCC` because:

[(X)] A numeral can only build applications outward, so removing one means rebuilding the count, classically with a pair that lags one behind
[( )] Subtraction is undefined on natural numbers
[( )] It requires the Y combinator
[( )] `SUCC` is not invertible in principle

---

The lambda calculus needs a fixed-point combinator because:

[(X)] A term has no name at the moment it is written, so a function cannot call itself by name
[( )] Beta reduction cannot express repetition
[( )] Church numerals are too weak to count loop iterations
[( )] Substitution is not powerful enough to duplicate a term

---

$\textbf{Y}$ diverges in Scheme but $\textbf{Z}$ does not, because:

[(X)] Scheme evaluates arguments before calling, so Y's inner `(x x)` re-triggers before `f` can reach its base case; Z's extra lambda makes that self-application a value instead
[( )] Z has a base case built into it and Y does not
[( )] Y is not a closed term, so Scheme cannot bind its free variables
[( )] Scheme's `lambda` is not the same construct as the calculus's abstraction

---

A closure is created when the evaluator meets a function expression. What does it store?

[(X)] The parameter, the unevaluated body, and the environment in force at that moment
[( )] The parameter, the body, and the values of every free variable, copied out
[( )] The fully evaluated body, ready to return on the next call
[( )] Only the body; the environment is looked up again at call time

---

In Model 6, changing `base = fn.env` to `base = env` in the `Call` branch turns the language from lexically scoped to dynamically scoped. Why is that one line enough?

[(X)] It is the only place the body's environment is chosen; everything else already threads environments unchanged
[( )] It also changes how `Fun` captures, because the two share a reference
[( )] It changes name lookup, which is what scope means
[( )] It is not enough; `Env.lookup` must change too

---

`fact(5)` raises `NameError` in the Try It Yourself because:

[(X)] The closure captured the environment *before* `fact` was bound into it, so the body cannot see its own name
[( )] Recursion requires a stack, which the evaluator does not have
[( )] `If0` evaluates both branches, so it never terminates
[( )] `Let` does not extend the environment

---

`[lambda: i for i in range(3)]` returns three functions that all print `2`. This is because:

[(X)] All three closed over the same binding of `i`, and by call time it holds the loop's final value
[( )] Python evaluates lambdas lazily and only the last one survives
[( )] List comprehensions reuse one function object
[( )] `range(3)` is exhausted before the lambdas run

---

## 9.  Exercises

1.  *Pairs.*  Define $\textbf{PAIR} = \lambda a. \lambda b. \lambda f.\, f\, a\, b$, with $\textbf{FST} = \lambda p.\, p\, \textbf{K}$ and $\textbf{SND} = \lambda p.\, p\, \textbf{KI}$.  Verify in Python.  Then say what data structure you built from nothing, and what your AST could, in principle, be encoded as.
2.  *IS-ZERO.*  Define $\textbf{ISZERO} = \lambda n.\, n\, (\lambda x.\, \textbf{FALSE})\, \textbf{TRUE}$ and verify it on 0, 1, and 2.  Explain the trick: what happens to TRUE if $f$ is applied even once?
3.  *XOR.*  Build XOR from the flock (any correct construction).  Verify all four input pairs in code, and present your reduction for one pair on the board.
4.  *Flock report.*  Watch or skim Lebec's "A Flock of Functions" (linked below) and write a half page on one construction he presents that we did not build today.  Reduce or verify it yourself.
5.  *Church list.*  Build a Church-encoded linked list: `NIL`, `CONS(head)(tail)`, `HEAD`, `TAIL`, `ISNIL`.  Represent the list `[1, 2, 3]` as Church numerals in a Church list, and write a `to_python_list` function that decodes it.
6.  *Tie the knot.*  Write `sumlist-generator` so that $\textbf{Z}$ turns it into a function that sums a Scheme list.  Then write the same thing the ordinary way, with `define` and a self-reference, and say in two sentences what the name was doing that $\textbf{Z}$ now does instead.
7.  *Mechanical audit.*  Choose one Church-encoding reduction you performed by hand in this module (for example, $\textbf{ISZERO}\, \overline{1}$ or $\textbf{FST}\, (\textbf{PAIR}\, a\, b)$) and verify it mechanically using Lambda-Py / pycombinator (https://finsberg.github.io/pycombinator/docs/lambda-talk.html) or your own Python reducer.  Include the transcript, and reconcile in one sentence: did the machine agree with your hand derivation step for step, and if not, which artifact erred?
8.  *Integrate closures into Mini (30 min).*  Add closures to your Mini interpreter:
    1.  Add `FunDef(name, params, body)` and `Call(callee, args)` AST nodes
    2.  In the parser, add `fun name(params) { body }` syntax and `name(args)` call syntax
    3.  In the evaluator, implement `execute_fundef` (create closure, bind name) and `eval_call` (create child env, run body, catch ReturnSignal)
    4.  Demonstrate: a plain function, `factorial(5)`, and `make_adder` working in your language
9.  *Counter objects (15 min).*  Build `make_counter()` using closures (not a class) that returns an increment function.  Then build `make_account(balance)` with `deposit(amount)` and `withdraw(amount)` methods.  Demonstrate shared state between the two returned functions.
10.  *Trap tour (15 min).*  Reproduce the loop-variable trap in your language (or Python), apply both fixes, and explain each fix's mechanism with environment diagrams.
11.  *Scope flip experiment (20 min).*  Apply the one-line change from Model 6 (`base = fn.env` becomes `base = env`) to make your interpreter dynamically scoped.  Rerun the `show`/`demo` program from Model 2 of the *Binding, Scope, and Environments* activity in your language.  Report the output difference and explain with a diagram which environment chain the dynamically scoped version follows.

---

## Reflection Prompt

In your notebook, answer both prompts.  First: numbers, booleans, pairs, and conditionals all dissolved into functions today.  Does anything in computing now seem irreducibly data to you, or is it functions all the way down?  Defend your answer with one example, knowing that your December language will choose what to make primitive.  Second: a closure carries its context everywhere, so it always means what it meant at home.  Dynamically scoped code means whatever its surroundings currently impose.  People can resemble both: some carry their context everywhere; others adapt to whoever is calling.  When has carrying your own context served you, and when has adapting to the caller been the wiser semantics?

---

## 10.  Further Reading

- Gabriel Lebec.  "Lambda as JS, or A Flock of Functions": https://speakerdeck.com/glebec/lambda-as-js-or-a-flock-of-functions-combinators-lambda-calculus-and-church-encodings-in-javascript (talk recording also online).  This is the companion reading for the lambda calculus half of today's module; every Python cell in Parts I through IV mirrors a section of that talk.
- **Lambda-Py / pycombinator**: combinators and Church encodings in Python.  Run every Church encoding from today interactively in your browser: https://finsberg.github.io/pycombinator/docs/lambda-talk.html
- Raymond Smullyan.  *To Mock a Mockingbird* (1985): the combinator birds.
- Raul Rojas.  "A Tutorial Introduction to the Lambda Calculus" (online), sections on encodings.
- [Build a Lambda Calculus Reducer](https://www.billmongan.com/Ursinus-CS374-Fall2026/Tutorials/LambdaCalculusReducer): builds the derivation from Part IV one step at a time in Python, from a factorial that takes a copy of itself through to the machinery separated out, and then implements the reducer that checks your hand reductions mechanically.  The Team Language Project's optional [lambda-calculus core extension](https://www.billmongan.com/Ursinus-CS374-Fall2026/Projects/TeamLanguage#extensions-menu) builds on the Church encodings from this activity.
- `call/cc`: capturing the rest of the computation as a value, and deriving break, return, exceptions, cooperative schedulers, generators, and backtracking from it.  The Team Language Project's optional [continuations extension](https://www.billmongan.com/Ursinus-CS374-Fall2026/Projects/TeamLanguage#extensions-menu) builds on this.
- The Curry-Howard correspondence: propositions as types, products and sums, the empty type and absurdity, and a glimpse of dependent types.  Philip Wadler, *Propositions as Types*.
- **"Crafting Interpreters"**, Robert Nystrom, "Functions" and "Closures" chapters (online, free): our exact implementation, then optimized
- **SICP Section 3.2**, Abelson & Sussman: the environment model of evaluation
- **"The Art of the Interpreter"**, Steele & Sussman (1978): closures invented and explained
- **Python `__closure__`**, CPython exposes closures via `fn.__closure__`: introspect live closures
- **JavaScript `let` vs `var`**, MDN: the real-world consequence of the loop-variable trap at ecosystem scale

## Going Further (at home)

The core lesson above stands on its own.  Two self-paced tutorials extend today's mechanism into runtime territory that feeds the Interpreter assignment's extensions and the team project:

- [Coroutines and Generators: Pausable Computation](https://www.billmongan.com/Ursinus-CS374-Fall2026/Tutorials/CoroutinesAndGenerators): how `yield` freezes a stack frame, how `async`/`await` desugars to a state machine, and how to add generator objects to your interpreter
- [Error Handling: From Return Codes to Algebraic Effects](https://www.billmongan.com/Ursinus-CS374-Fall2026/Tutorials/ErrorHandling): return codes, exceptions, Option/Maybe, Result/Either, and designing error propagation for your interpreter

---

# Extension: Pairs and the Predecessor (self-paced)

> Past the 75 minutes.  Nothing in class assumes it, although Part IV's factorial borrows `PRED` from here.

> **Intuition before pairs:** A pair stores two values.  The pair itself is a function that waits for a "selector": `lambda sel: sel(a)(b)`.  FST passes `lambda x: lambda y: x` (which is TRUE, or K) to get the first element; SND passes `lambda x: lambda y: y` (which is FALSE, or KI) to get the second.  You built the selectors when you built booleans, so pairs come for free.

## Model 8: Pairs and the Predecessor

**Church pairs: building linked data from functions:**

```python
# Church pairs: PAIR a b f = f a b
# FST p = p K  (select first)
# SND p = p KI (select second)

TRUE  = lambda x: lambda y: x   # K
FALSE = lambda x: lambda y: y   # KI

# Decode helpers
def church_to_int(n):
    return n(lambda k: k + 1)(0)

ZERO  = lambda f: lambda x: x
SUCC  = lambda n: lambda f: lambda x: f(n(f)(x))

PAIR = lambda a: lambda b: lambda f: f(a)(b)
FST  = lambda p: p(TRUE)
SND  = lambda p: p(FALSE)

print("=== Church Pairs ===")
p = PAIR("hello")("world")
print(f"FST (PAIR 'hello' 'world') = {FST(p)!r}")
print(f"SND (PAIR 'hello' 'world') = {SND(p)!r}")

# Numeric pairs for predecessor: PAIR n (n-1)
# Increment a pair: (n,m) -> (SUCC n, n)  i.e., shift right
shift = lambda p: PAIR(SUCC(FST(p)))(FST(p))

# PRED n: start from (0,0), apply shift n times, take SND
ZERO_PAIR = PAIR(ZERO)(ZERO)
PRED = lambda n: SND(n(shift)(ZERO_PAIR))

# Build some numerals
ONE = SUCC(ZERO); TWO = SUCC(ONE); THREE = SUCC(TWO); FOUR = SUCC(THREE)

print("\n=== Predecessor ===")
print(f"PRED(0) = {church_to_int(PRED(ZERO))}")   # 0 (special case)
print(f"PRED(1) = {church_to_int(PRED(ONE))}")    # 0
print(f"PRED(2) = {church_to_int(PRED(TWO))}")    # 1
print(f"PRED(4) = {church_to_int(PRED(FOUR))}")   # 3

# Subtraction from predecessor:
MINUS = lambda m: lambda n: n(PRED)(m)
print(f"\n4 - 2 = {church_to_int(MINUS(FOUR)(TWO))}")   # 2
print(f"3 - 4 = {church_to_int(MINUS(THREE)(FOUR))}")   # 0 (floored)
```
@LIA.eval(`["main.py"]`, `none`, `python3 main.py`)

### Critical Thinking Questions

> **CTQ 8.1** The pair-based predecessor works by shifting: `(0,0) -> (1,0) -> (2,1) -> (3,2)`.  After applying shift $n$ times to $(0,0)$, what is the SND?  Why does `PRED(ZERO)` return ZERO rather than negative one?

> **CTQ 8.2** Subtraction `m - n` is defined as "apply PRED n times to m."  What is `3 - 5` under this definition?  This is called *monus* (truncated subtraction).  Is this a bug or a deliberate design choice?

> **CTQ 8.3** You now have booleans, conditionals, numerals, arithmetic, and pairs.  What other data structures (lists, trees) could you build from Church pairs?  Sketch the encoding for a two-element list [a, b].

Recap: a pair is a function holding two values and waiting for a selector, and the selectors are the booleans you already built.  The predecessor works by shifting a pair `n` times from `(0,0)` and keeping the second element, which lags one step behind.

---

# Extension: Y from the Equation, and Why Strictness Matters (self-paced)

> Past the 75 minutes.  Nothing in class assumes it.  Read it before you choose an evaluation order for your team's language.

## 11.  The Same Term, Derived Backwards from the Equation

The construction in Part IV is honest but long.  Now that we know what we are looking for, here is the four-line derivation.  It works from the fixed-point equation rather than from a factorial.

We want a $\textbf{Y}$ with $\textbf{Y}\, f = f\, (\textbf{Y}\, f)$.  The only device we have for making a term reproduce itself is self-application, which Part 1 showed us in $\Omega = (\lambda x.\, x\, x)\, (\lambda x.\, x\, x)$.  So guess that $\textbf{Y}\, f$ is a self-application, write $\textbf{Y} = \lambda f.\, W\, W$, and solve for $W$:

```
Want:   W W  =  f (W W)

Read it as a specification for W: applied to an argument x,
W must return f applied to (x x).  Write exactly that down:

        W  =  λx. f (x x)

Check it, by substituting W for x:

        W W = (λx. f (x x)) (λx. f (x x))
            ->β f ((λx. f (x x)) (λx. f (x x)))
             =  f (W W)                          OK

So      Y  =  λf. (λx. f (x x)) (λx. f (x x))
```

This is the same term the construction produced, reached from the other end.  $\Omega$ was the raw material both times: Step 1's $F\, F$ is a self-application, and so is $W\, W$.  The only difference between $\Omega$ and $\textbf{Y}$ is that $\textbf{Y}$ leaves a place for $f$ to do work on the way around the loop.

**The full reduction, with every substitution named**

```
Y = λf. W W          where W = λx. f (x x)

Y f
= (λf. (λx. f (x x)) (λx. f (x x))) f
->β (λx. f (x x)) (λx. f (x x))          <- substitute f for the bound f
                                            this is W W
->β f ((λx. f (x x)) (λx. f (x x)))      <- substitute W for x in f (x x)
=  f (W W)
=  f (Y f)                                OK
```

Keep going and the pattern is the whole story of recursion:

```
Y f  ->β* f (W W)
     ->β* f (f (W W))
     ->β* f (f (f (W W)))
     ->β* ...
```

Each arrow wraps one more $f$ around the same self-applying core.  Nothing decides to stop, and nothing ever will: the term has no normal form.  What stops is the computation, when some $f$ finally ignores the argument it was handed because `ISZERO n` selected the base case.  That distinction is real and useful: a divergent term can compute a terminating function, as long as evaluation never demands the divergent part.

> **Watch out!**  "$\textbf{Y}$ has no normal form" and "$\textbf{Y}\, f$ never terminates" are different claims, and only the first is true.  Under normal-order reduction, `Y fact-gen 3` gets to 6 in finitely many steps, because the base case discards the unexpanded remainder before it is ever needed.

---

## 12.  Strictness: Why Y Hangs and Z Does Not

Everything in section 11 contracted the outermost redex first.  That strategy is **normal order**: reduce the function before its arguments.  Scheme, Python, JavaScript, and nearly every language you will be paid to write use call-by-value instead: an argument is reduced to a value before the function receiving it runs.

Under call-by-value, $\textbf{Y}$ is a disaster, and it fails before $f$ ever executes a single instruction:

```
Y f
->β W W                    where W = λx. f (x x)
->β f (W W)                to call f, first reduce its ARGUMENT (W W):
      W W ->β f (W W)      to call f, first reduce its argument (W W):
        W W ->β f (W W)    ...
                           f is never applied to anything.  No base case is
                           ever tested, because no test is ever reached.
```

The loop is not in the factorial.  It is in the machinery, and it spins before the factorial gets a turn.

Now put back the wrapper we deleted in Step 5, and follow the same rule:

```
Z f
->β V V                    where V = λx. f (λv. ((x x) v))
->β f (λv. ((V V) v))      the argument to f is now a LAMBDA.  A lambda is
                           already a value, so call-by-value stops right
                           here and hands it to f, which runs.          OK
```

That is the entire fix.  $\lambda v.\, ((x\, x)\, v)$ computes nothing, but it is a value.  Under call-by-value, the difference between a value and a computation is the difference between stopping and not stopping.  The self-application inside the wrapper happens later, when the recursive call is made on a real argument $v$.

So the two combinators sit exactly one eta step apart, and your evaluation order decides which one you want:

| | $\textbf{Y} = \lambda f.\, (\lambda x.\, f\, (x\, x))\, (\lambda x.\, f\, (x\, x))$ | $\textbf{Z} = \lambda f.\, (\lambda x.\, f\, (\lambda v.\, ((x\, x)\, v)))\, (\lambda x.\, f\, (\lambda v.\, ((x\, x)\, v)))$ |
|---|---|---|
| Normal order / lazy (Haskell) | works | works |
| Call-by-value (Scheme, Python) | diverges immediately | works |
| Difference | one eta-expansion | |

> **Watch out!**  "Y does not work" is the wrong lesson.  $\textbf{Y}$ works perfectly; our machines' evaluation order does not suit it.  The distinction matters because your December language will have to choose an evaluation order, and this is one of the first places where that choice becomes visible to an ordinary programmer.

---

## Model 9: Y, Z, and the Order of Evaluation

```python
# Y and Z in Python.  Python is call-by-value, exactly like Scheme, so this
# cell is a fair test of the claim section 12 makes about Y.
import sys

# The classical Y, transcribed straight off the lambda term.
Y = lambda f: (lambda x: f(x(x)))(lambda x: f(x(x)))

# Z: the same term with each self-application wrapped in one more lambda.
Z = lambda f: (lambda x: f(lambda v: (x(x))(v)))(lambda x: f(lambda v: (x(x))(v)))

# The generator from Step 3.  Notice what is NOT in it: fact_gen never
# mentions its own name.  It takes the rest of the recursion as a parameter.
fact_gen = lambda self: lambda n: 1 if n == 0 else n * self(n - 1)

factorial = Z(fact_gen)
print("Z: factorial(0) =", factorial(0))
print("Z: factorial(5) =", factorial(5))

# The same machinery with two recursive calls instead of one.
fib_gen = lambda self: lambda n: n if n < 2 else self(n - 1) + self(n - 2)
print("Z: fib(10)      =", Z(fib_gen)(10))

# Now watch Y fail, for exactly the reason section 12 gives.  Note where it
# fails: building Y(fact_gen) is already enough.  We never get to call it.
sys.setrecursionlimit(300)
try:
    Y(fact_gen)
    print("Y: built a function (this does not happen in a strict language)")
except RecursionError:
    print("Y: RecursionError before f ran even once")
sys.setrecursionlimit(1000)

# Expected output:
# Z: factorial(0) = 1
# Z: factorial(5) = 120
# Z: fib(10)      = 55
# Y: RecursionError before f ran even once
```
@LIA.eval(`["main.py"]`, `none`, `python3 main.py`)

Here are the same three definitions in Scheme.  They sit closer to the lambda terms because Scheme's `lambda` is the calculus's abstraction:

```scheme
; The Z combinator, transcribed from the term in section 12.
(define Z
  (lambda (f)
    ((lambda (x) (f (lambda (v) ((x x) v))))
     (lambda (x) (f (lambda (v) ((x x) v)))))))

; fact-generator is not recursive.  It takes "self" as a parameter and calls
; (self n) wherever a recursive call belongs.  It never names itself.
(define fact-generator
  (lambda (self)
    (lambda (n)
      (if (= n 0)
          1
          (* n (self (- n 1)))))))

(define factorial (Z fact-generator))

(factorial 5)                ; 120
(factorial 0)                ; 1
```

**Step-by-step: (factorial 3)**

```
(Z fact-generator)
 = (fact-generator self)          where self = (lambda (v) ((x x) v))
 = (lambda (n) (if (= n 0) 1 (* n (self (- n 1)))))

(factorial 3)
->  (* 3 (self 2))               ; calling self unfolds Z one more level
->  (* 3 (* 2 (self 1)))
->  (* 3 (* 2 (* 1 (self 0))))
->  (* 3 (* 2 (* 1 1)))          ; n = 0, base case, self is never called again
=   6                                                                       OK
```

### Reading the Code

- `fact-generator` is a plain function of one argument with no state, no mutation, and no name pointing back at itself.  Every recursive function you wrote before today needed that name.  This one does not, and that is the whole result.
- Each call to `self` is another application of `Z` to `fact-generator`.  That is the fixed-point equation $(\textbf{Z}\, f) = (f\, (\textbf{Z}\, f))$ cashed in one unfolding at a time, and the trace above is that equation applied four times.
- The recursion stops because `n = 0` selects the `1` branch, so `self` is never called.  Delay is not what makes it terminate.  Delay keeps the machinery from running away before the base case can be tested.
- `(lambda (v) ...)` is the only textual difference between `Y` and `Z`.  In a strict language, it is the difference between a factorial and a hung REPL.

### Critical Thinking Questions

> **CTQ 9.1** Section 11 derived $\textbf{Y}$ in four lines and section 5 took five steps.  What does the long derivation tell you that the short one does not?  Answer in terms of what a student could reconstruct from memory a week later.

> **CTQ 9.2** Write `fib-generator` in Scheme, in the same shape as `fact-generator`, and hand it to `Z`.  It has two recursive calls rather than one.  Does anything about `Z` have to change?  Predict first, then check.

> **CTQ 9.3** $\lambda v.\, (M\, v)$ and $M$ are interchangeable in the calculus, yet swapping one for the other turns a working factorial into a hang.  How can two terms be equal and still behave differently?  Say exactly what "equal" quantifies over, and what it says nothing about.

> **CTQ 9.4** In the simply typed lambda calculus, $x\, x$ cannot be assigned a type at all, so $\textbf{Y}$ is not typable and every well-typed program terminates.  Connect this to the *Type Systems* activity: what did the type system buy, what did it cost, and by what mechanism do Haskell and ML get recursion back?

> **CTQ 9.5** `fact-generator` receives the rest of the recursion as a parameter.  `make-counter`, from the Scheme activity, got its persistence from `set!` on a captured variable instead.  Both supply something the bare calculus lacks.  Which would you rather explain to a first-year student, and which would you rather implement in your interpreter?  They need not be the same answer.

> **CTQ 9.6** Your tree-walking interpreter has to make recursion work somehow.  Find the place in it where a function's own name becomes visible inside its body, and say whether your implementation is closer to $\textbf{Z}$ or closer to `set!`.  Put the answer in `SEMANTICS.md` in one sentence.

### Try It Yourself

```python
# Start from the Model 9 cell.

# TODO 1: write mult_gen so that Z(mult_gen) multiplies two numbers using
#         only addition and recursion.  The generator takes exactly one
#         parameter, so you must decide where the second argument goes.

# TODO 2: instrument Z so it prints one line every time self is called.
#         Run factorial(4) and count the lines.  Does the count match the
#         hand trace in Model 9?

# TODO 3: define Y_lazy, a version of Y that works in Python by delaying the
#         WHOLE call site rather than the self-application.  Compare it with
#         Z and say which one you would put in a language specification.
```
@LIA.eval(`["main.py"]`, `none`, `python3 main.py`)

Recap: a recursive function becomes a generator when it takes the rest of the recursion as a parameter, and a fixed-point combinator turns any generator into the recursive function it describes.  Y and Z differ by one eta-expansion, and under call-by-value that wrapper is what keeps the machinery from spinning before the base case is tested.

---

# Extension: The Loop-Variable Trap (self-paced)

> Past the 75 minutes.  Nothing in class assumes it.  You met the trap in Part V of *Binding, Scope, and Environments*; this extension draws it as boxes.

The loop-variable trap is one of the most common beginner bugs in Python and JavaScript alike.  It happens when every closure created in a loop captures the same variable binding instead of its own private copy.  One analogy: every worker on a factory floor shares one whiteboard for the current job number.  By the time any worker reads the board, the number has moved on to the last job.  The analogy stops at the sharing, because the fix in code is to give each closure its own board, which a factory cannot do by rewriting one line.

> **Watch out!**  When you write `[lambda: i for i in range(3)]`, all three lambdas capture *one* variable `i`, the same loop variable.  By the time any of them is called, the loop has finished and `i` is `2`.  This is not a bug in Python.  It is the correct behavior of reference capture.  The two fixes shown (default argument and factory function) both work by creating a separate binding per iteration.

## 13.  The Famous Python Bug

```python
# The loop-variable trap, every Python programmer falls into this once
fns = [lambda: i for i in range(3)]
print("Results:", [f() for f in fns])     # [2, 2, 2], not [0, 1, 2]!

# Why? All three lambdas captured the SAME binding of 'i'.
# By the time they're called, i == 2.
print("i after loop:", end=" ")
try:
    print(i)  # i still exists after the loop! (Python scoping quirk)
except NameError:
    print("not available")

# Fix 1: default argument captures VALUE at definition time
fns_fixed1 = [lambda i=i: i for i in range(3)]
print("Fix 1 (default arg):", [f() for f in fns_fixed1])   # [0, 1, 2]

# Fix 2: factory function creates a new scope per iteration
def make_fn(i):
    return lambda: i

fns_fixed2 = [make_fn(i) for i in range(3)]
print("Fix 2 (factory):", [f() for f in fns_fixed2])   # [0, 1, 2]

# The lesson: each iteration needs its OWN binding, not a shared one
# JavaScript's 'let' fixed this at the ecosystem scale (was 'var' before)
```
@LIA.eval(`["main.py"]`, `none`, `python3 main.py`)

> **CTQ 10.1** All three lambdas captured the same `i` binding.  After the loop, what is `i`?  Why do all three lambdas return 2?

> **CTQ 10.2** Fix 1 uses `lambda i=i: i`.  Python evaluates the outer `i` (the default argument value) at *definition time*, which captures the current value.  Why does this work, while the capture in the original version does not?

> **CTQ 10.3** Fix 2 uses a factory function `make_fn(i)` that creates a new scope.  Draw the environment diagram showing why each returned lambda has a *different* captured environment.

> **CTQ 10.4** JavaScript's historic `var` scoping caused the same bug; `let` was introduced to fix it.  How does `let` create "per-iteration" scope?  Why can't `var` do this?

---

The code above showed the trap and two fixes.  The notes below explain the code, the Try It Yourself asks you to predict five variants, and Model 10 then draws the trap as boxes.  The broken and fixed versions differ by exactly one thing (how many environment boxes exist), and the box diagram makes the bug visible at a glance.

### Reading the Code

- `[lambda: i for i in range(3)]` builds three functions that all close over the *same* `i`.  Nothing about that is a bug.  It is capture-by-reference doing exactly what Model 5 demonstrated on purpose.
- The two fixes attack different halves.  The default argument stops closing over `i` at all, so there is nothing to share.  The factory function makes a new binding per iteration, so there are three `i`s to close over instead of one.
- JavaScript's `var` had this exact shape, and `let` changed it by giving loop bodies per-iteration bindings.  You made the same decision in the Model 6 Try It Yourself of *Binding, Scope, and Environments*; JavaScript made it at ecosystem scale.

### Try It Yourself

Predict, then check, which of these five loops has the trap.

```python
def factory(v):
    return lambda: v

print("=== Five loops. Which give [0, 1, 2]? ===")

a = [lambda: i for i in range(3)]
b = [lambda i=i: i for i in range(3)]
c = [factory(i) for i in range(3)]
d = []
for i in range(3):
    d.append(lambda: i)
e = []
for i in range(3):
    e.append(factory(i))

# TODO: predict all five BEFORE running. Write your predictions down.
for name, fns in [("a  comprehension, bare lambda", a),
                  ("b  comprehension, default arg", b),
                  ("c  comprehension, factory    ", c),
                  ("d  for-loop, bare lambda     ", d),
                  ("e  for-loop, factory         ", e)]:
    print(f"  {name} -> {[f() for f in fns]}")

print("\nTwo of these share one binding and three do not.")
print("For each, say WHERE the per-iteration binding comes from,")
print("or why there isn't one.")
```
@LIA.eval(`["main.py"]`, `none`, `python3 main.py`)

Expected output: `a` and `d` give `[2, 2, 2]`; `b`, `c`, and `e` give `[0, 1, 2]`.  If you predicted the comprehension and the for-loop would differ, note that they do not.  The comprehension's scope is not what saves you.

## Model 10: The Loop Trap, Drawn as Boxes

**Broken:** `fns = [lambda: i for i in range(3)]`.  The comprehension runs in a single scope, so there is exactly one box holding `i`, and every lambda's capture arrow points at it:

```
        +----------------------------+
        | comprehension scope        |
        |   i = 2   (final value)    |
        +----------------------------+
             ^         ^         ^
             |         |         |
           lam0      lam1      lam2
   three closures, ONE shared box: all see i = 2 at call time
```

**Fixed (factory):** `fns = [make_fn(i) for i in range(3)]`.  Each *call* to `make_fn` creates a fresh box, and each lambda captures its own:

```
   +-----------+   +-----------+   +-----------+
   | E0: i = 0 |   | E1: i = 1 |   | E2: i = 2 |
   +-----------+   +-----------+   +-----------+
        ^               ^               ^
        |               |               |
      lam0            lam1            lam2
   three closures, three boxes: one binding per closure
```

Here is the broken version's history as a timeline.  The trap is a *timing* bug: capture is by reference, and the calls happen after the last write.

| Loop step | Shared box's `i` | Closures created so far | What each would return *if called now* |
|-----------|------------------|-------------------------|----------------------------------------|
| iteration 0 | 0 | lam0 | lam0 -> 0 |
| iteration 1 | 1 | lam0, lam1 | both -> 1 |
| iteration 2 | 2 | lam0, lam1, lam2 | all -> 2 |
| after the loop (calls happen here) | 2 | all three | **all -> 2** |

```python
# Evidence for the diagrams: inspect the closure cells directly
broken = [lambda: i for i in range(3)]
print("broken results:", [f() for f in broken])
print("one shared box?",
      broken[0].__closure__[0] is broken[1].__closure__[0] is broken[2].__closure__[0])

def make_fn(i):
    return lambda: i

fixed = [make_fn(i) for i in range(3)]
print("\nfixed results:", [f() for f in fixed])
print("distinct boxes?",
      fixed[0].__closure__[0] is not fixed[1].__closure__[0])
print("each box's contents:", [f.__closure__[0].cell_contents for f in fixed])

# Fix 1 (default argument) is different again: no closure at all
fix1 = [lambda i=i: i for i in range(3)]
print("\nfix1 results:", [f() for f in fix1])
print("fix1 closures:", [f.__closure__ for f in fix1])   # [None, None, None]
```
@LIA.eval(`["main.py"]`, `none`, `python3 main.py`)

`fns = [lambda: i for i in range(3)]` yields functions that all return 2, and `fns[0].__closure__[0] is fns[1].__closure__[0]` prints `True`.  Together these show:

[( )] The lambdas were compiled to the same code object, which forces one result
[(X)] All three closures captured the very same binding (cell) for `i`, whose final value is 2
[( )] Python evaluates lambda bodies eagerly at definition time
[( )] The list comprehension copied the last lambda three times

Remember two things from this part.  Closures made in one scope share one binding, so they all see its final value.  A factory call makes a fresh scope, so each closure gets its own binding.

**Critical Thinking Questions (CTQs)**

> **CTQ 10.5** Which single line of the cell's output is direct evidence for the "three arrows, one box" picture?  Which line is evidence for "three boxes"?

> **CTQ 10.6** In the fixed diagram, what act creates each new box: the `lambda` *definition*, or the *call* to `make_fn`?  Justify your answer with the environment-creation rule from Part VI (a call builds a new environment).

> **CTQ 10.7** Fix 1's lambdas report `__closure__ = None`; they are not closures at all.  Where does each one's `i` live instead, and why does that location make capture unnecessary?

---

Two closures created by separate calls to `make_adder(5)` and `make_adder(3)` return different results for the same input because:

[( )] The function body's code differs between them
[(X)] Each closure captured a different defining environment in which `n` is bound to a different value
[( )] Python caches the most recent return value
[( )] Closures copy the global environment at call time

---

# Extension: Closures vs. Objects (self-paced)

> Past the 75 minutes.  Nothing in class assumes it.  Read it before your team decides whether its language gets objects, closures, or both.

Objects and closures do the same job.  Both bundle state with behavior, and both control which code can reach that state.  They look different at first: an object is a class instance with named fields, and a closure is a function bundled with hidden environment variables.  This model builds a counter both ways, side by side, so you can see the parallel directly.

> **Watch out!**  Closures are not limited to functional languages.  Python, JavaScript, Ruby, and Java (through lambdas) all have closures.  A common misconception is that "closures = Haskell/Scheme only."  In modern JavaScript, you use a closure every time you write a callback, an event handler, or a `useEffect` hook in React.

## 14.  Closures and Objects Are Two Views of One Idea

A well-known saying in the field puts it this way: "Closures are a poor man's objects; objects are a poor man's closures."  Each can stand in for the other.  They are dual.

```python
# Objects approach: counter using a class
class Counter:
    def __init__(self, start=0):
        self._count = start
    def increment(self):
        self._count += 1
        return self._count
    def reset(self):
        self._count = 0
    def value(self):
        return self._count

# Closures approach: counter using closures (no class!)
def make_counter(start=0):
    count = [start]   # mutable cell
    return {
        'increment': lambda: (count.__setitem__(0, count[0] + 1), count[0])[1],
        'reset':     lambda: count.__setitem__(0, 0),
        'value':     lambda: count[0],
    }

obj_counter = Counter(0)
clo_counter = make_counter(0)

obj_counter.increment(); obj_counter.increment()
print(f"Object counter: {obj_counter.value()}")

clo_counter['increment'](); clo_counter['increment']()
print(f"Closure counter: {clo_counter['value']()}")

# Both share mutable state via different mechanisms:
# Object: self._count (field in object's dictionary)
# Closure: count (binding in captured environment)
# They are structurally dual.
```
@LIA.eval(`["main.py"]`, `none`, `python3 main.py`)

> **CTQ 11.1** In the closure-based counter, `count` is a shared mutable cell.  In the object-based counter, `self._count` is a field.  What is the structural difference?  What is the conceptual difference?

> **CTQ 11.2** The closure counter uses a list `[start]` to work around Python's scoping rules for `nonlocal`.  Rewrite it using `nonlocal count` (Python 3) instead of a list.  Why is `nonlocal` cleaner?

> **CTQ 11.3** Languages like OCaml and Haskell have closures but no classes.  Java before version 8 had classes but no lambdas; its nearest thing to a closure was an anonymous inner class, an object that could capture only `final` local variables.  From what you now know about the implementation of each, argue: which is more fundamental?

---

Up next: the *Sprint Studio* sessions hand the room to your team's language, starting with Sprints 1-2 and the Gallery Walk, where the Tree-Walking Interpreter is due.  Closures complete the environment story that assignment depends on, and the Church encodings you built here are the ones the Lambda Calculus lab asks you to reduce by hand.
