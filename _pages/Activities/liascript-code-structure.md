# Code Structure: Expressions and Conditionals
<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://github.com/BillJr99/Ursinus-CS374-Fall2026/blob/gh-pages/_pages/Activities/liascript-code-structure.md

import: https://raw.githubusercontent.com/liascript/CodeRunner/master/README.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

# Code Structure: Expressions and Conditionals

> **Think about city zoning for a moment.** A well-planned city separates residential neighborhoods from industrial districts from commercial zones — not because mixing them is physically impossible, but because keeping related things together prevents conflicts and makes the city easier to navigate. Programming languages do the same thing with *modules*, *namespaces*, and *packages*. The way a language carves up code into named, bounded units reflects its philosophy about separation of concerns: who owns what, what is visible to whom, and how names from different places coexist without colliding. In this activity, you will explore how expression structure — the building blocks *inside* those units — is designed in functional languages.

## Learning Goals

By the end of this activity, you will be able to:

- Distinguish expressions from statements and explain the significance of treating `if` and `let` as expressions rather than statements
- Implement `let`-binding as an expression form and trace how it extends the environment for the scope of its body
- Construct a small expression evaluator that handles arithmetic, conditionals, and local variable binding
- Compare strict (eager) and short-circuit (lazy) evaluation of boolean expressions and identify where each is semantically necessary
- Analyze how sequencing is encoded as a language construct and explain its relationship to side effects

CS374 — Principles of Programming Languages | Week 7

Reference: PLAI (Programming Languages: Application and Interpretation) Ch. 7

> **Before You Begin**
>
> This activity assumes you are comfortable with:
>
> - Writing and calling Python functions, including lambda expressions
> - Basic Python data structures (lists, dicts) and comprehensions
> - The concept of *scope* — that a variable defined inside a function is not visible outside it
> - Python's `dataclass` decorator (used in Models 4–5); a quick review: `@dataclass` auto-generates `__init__` from field annotations
>
> You do **not** need prior exposure to Scheme or Haskell, though the activity will introduce small snippets of each. If you have never seen Scheme syntax before, note that `(f a b)` means "call function `f` with arguments `a` and `b`" — the function name comes first, inside the parentheses.

---

## Directions and Group Roles

This is a POGIL (Process Oriented Guided Inquiry Learning) activity. Work in groups of 3–4. Each person takes a role:

- **Facilitator**: Keeps the group on task, ensures everyone participates, and watches the clock.
- **Recorder**: Writes down the group's answers and keeps notes for the group.
- **Reporter**: Prepares to share the group's findings with the class when called upon.
- **Reflector**: Monitors group dynamics, notes what is working well, and identifies any confusion.

Roles may rotate between activities. Everyone should contribute to the critical thinking questions, even if only one person records the answers.

**Learning Goals for This Activity:**

- Distinguish between *expressions* (which produce a value) and *statements* (which produce side effects)
- Understand `let` as an expression and how it models local variable binding
- Explore sequencing as a language construct
- Build a small expression evaluator with conditionals and let bindings
- Understand short-circuit (lazy) evaluation vs. strict evaluation

---

## Model 1: Expressions vs Statements

In programming language theory, a key distinction is between **expressions** and **statements**.

- An **expression** is a syntactic form that *evaluates to a value*. For example, `3 + 4` evaluates to `7`.
- A **statement** is a syntactic form that *performs an action* (a side effect) and does not necessarily produce a value. For example, a `print` call or an assignment statement.

In many functional languages (Haskell, Scheme, ML), `if` is an **expression** — it always produces a value. In Python, `if` is a **statement** by default, although Python provides a *conditional expression* (the ternary operator) as well. Python 3.8+ also introduced the walrus operator (`:=`) as a limited form of assignment expression.

The code below demonstrates these distinctions in Python and shows how we can simulate a strict if-expression.

```python
# Python: if-expression (ternary)
x = 10
label = "positive" if x > 0 else "non-positive"
print(f"x={x}, label={label}")

# Demonstrate: assignment is a statement (not an expression)
# In Python 3.8+, the walrus operator := creates assignment expressions
import re
text = "Hello, world! My number is 42."
if m := re.search(r'\d+', text):
    print(f"Found number: {m.group()}")
else:
    print("No number found")

# In a pure expression language, everything has a value
# Simulate: evaluate a conditional as an expression
def iif(cond, then_val, else_val):
    """Strict if-expression (both branches always evaluated)."""
    return then_val if cond else else_val

result = iif(5 > 3, "yes", "no")
print(f"iif result: {result}")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

### Critical Thinking Questions

1. What is the difference between an expression and a statement? Give one example of each from the code above.

2. Could every statement be rewritten as an expression? Consider an assignment statement like `x = 5`. What would it mean to treat that as an expression (what value would it produce)? What language does exactly this?

3. What are the tradeoffs of treating `if` as an expression (as in Haskell) versus treating it as a statement (as in Java)? Think about code clarity, composability, and how `if` can be nested inside other expressions.

4. The `iif` function above is called a *strict* if-expression. What does "evaluation order" mean in this context, and how does `iif` differ from Python's built-in ternary `x if cond else y` in terms of when each branch is evaluated?

---

## Model 2: Let Expressions and Local Binding

In functional languages like Scheme and Haskell, `let` is an **expression** that introduces local variable bindings. For example, in Scheme:

```
(let ((x 5) (y 3)) (+ x y))
```

This evaluates to `8`: `x` is bound to `5`, `y` is bound to `3`, and the body `(+ x y)` is evaluated in that local scope.

In Python, local binding is accomplished through assignment statements, which are not expressions. However, we can *simulate* the semantics of `let` using a higher-order function to better understand what `let` means as a language construct.

An important distinction: `let` (non-recursive) evaluates all binding values in the *outer* environment, while `letrec` (recursive let) allows the bindings to refer to each other, which is necessary for mutually recursive definitions.

```python
# In Scheme: (let ((x 5) (y 3)) (+ x y))
# Python doesn't have let as an expression, but we can simulate it:

def let(bindings, body):
    """Simulate a let expression: evaluate body with given bindings."""
    return body(**bindings)

result = let(
    {"x": 5, "y": 3},
    lambda x, y: x + y
)
print(f"let x=5, y=3 in x+y = {result}")

# Nested let:
result2 = let(
    {"a": 10},
    lambda a: let(
        {"b": a * 2},
        lambda b: b + 1
    )
)
print(f"let a=10 in let b=a*2 in b+1 = {result2}")

# Python's walrus operator as a limited let-expression:
# (Python 3.8+)
data = [1, 5, 3, 8, 2, 9, 4]
result3 = [y for x in data if (y := x * 2) > 8]
print(f"doubled values > 8: {result3}")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

### Critical Thinking Questions

1. Why is `let` useful as an expression rather than a statement? How does treating `let` as an expression affect composability — can you nest `let` inside another expression?

2. How does the `let` simulation above capture the semantics of `let` in functional languages? What role does the `body` lambda play? What is the environment in which `body` is evaluated?

3. What is the difference between `let` (non-recursive) and `letrec` (recursive)? Give an example of a definition that requires `letrec` but cannot be expressed with plain `let`. Hint: think about a recursive function.

4. How does Python's variable scoping (function-local scope, closures) differ from Scheme's `let` scoping? In Python, does a variable defined inside a function leak out? How does this compare to a `let` binding in Scheme?

---

## Model 3: Sequencing and Begin

In purely functional languages, there are no statements and no side effects — every construct is an expression. But even functional languages need to do things in *order*, particularly when dealing with I/O or mutable state.

The `begin` form in Scheme sequences expressions and returns the value of the *last* one:

```
(begin
  (display "step 1")
  (display "step 2")
  42)   ; returns 42
```

Python's sequence of statements is the natural analog, but it is not an expression — you can't embed a sequence of statements inside a larger expression. The Python `begin` simulation below models Scheme's behavior explicitly.

```python
# Simulate Scheme's (begin e1 e2 ... en) — returns last value
def begin(*exprs):
    """Evaluate expressions in order, return the last value."""
    result = None
    for expr in exprs:
        result = expr() if callable(expr) else expr
    return result

counter = [0]

def increment():
    counter[0] += 1
    return counter[0]

value = begin(
    lambda: print("step 1: incrementing"),
    increment,
    lambda: print(f"step 2: counter is now {counter[0]}"),
    increment,
    lambda: print(f"step 3: counter is now {counter[0]}"),
    increment,
)
print(f"Final value: {value}")

# Python's sequence of statements IS sequencing, but not as an expression
# Show that list comprehensions are essentially sequenced expressions:
squares = [x**2 for x in range(1, 6)]
print(f"Squares: {squares}")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

### Critical Thinking Questions

1. What does "sequencing" mean in a programming language? Why do we need it even in a language that is primarily expression-based?

2. Why does `begin` return the *last* value rather than the first? In what situations might it be useful to have a form that sequences expressions but discards all values except the last?

3. In Python, how is sequencing expressed differently from a functional language like Scheme? Is Python's sequencing (a block of statements) usable inside an expression? Give an example of where this limitation is noticeable.

4. What would happen if a language had no sequencing at all — only pure expressions with no side effects? What kinds of programs would be impossible or very difficult to write? What kinds of programs might actually be *easier* to reason about?

---

## Model 4: Building an Expression Evaluator

PLAI Ch. 7 focuses on building an interpreter for a language with conditionals and let bindings. In this model, we implement a small evaluator for an expression language that includes arithmetic, booleans, conditionals (`If`), and local bindings (`LetExpr`).

This interpreter models the *substitution model*: when we encounter a `LetExpr`, we extend the environment with the new binding rather than substituting directly. This is a key concept in interpreter design.

Notice that `If` only evaluates **one** branch — the correct branch based on the condition. This is called *lazy* or *call-by-need* conditional evaluation.

```python
from dataclasses import dataclass
from typing import Any

@dataclass
class Num:
    value: float

@dataclass
class Bool:
    value: bool

@dataclass
class BinOp:
    op: str    # '+', '-', '*', '/', '<', '>', '==', 'and', 'or'
    left: Any
    right: Any

@dataclass
class If:
    cond: Any
    then_expr: Any
    else_expr: Any

@dataclass
class LetExpr:
    name: str
    value_expr: Any
    body_expr: Any

@dataclass
class Var:
    name: str

def eval_expr(expr, env: dict) -> Any:
    if isinstance(expr, Num):
        return expr.value
    if isinstance(expr, Bool):
        return expr.value
    if isinstance(expr, Var):
        if expr.name not in env:
            raise NameError(f"Undefined variable: {expr.name}")
        return env[expr.name]
    if isinstance(expr, BinOp):
        l = eval_expr(expr.left, env)
        r = eval_expr(expr.right, env)
        ops = {
            '+': l + r, '-': l - r, '*': l * r,
            '/': l / r if r != 0 else (_ for _ in ()).throw(ZeroDivisionError()),
            '<': l < r, '>': l > r, '==': l == r,
            'and': l and r, 'or': l or r,
        }
        return ops[expr.op]
    if isinstance(expr, If):
        cond_val = eval_expr(expr.cond, env)
        if cond_val:
            return eval_expr(expr.then_expr, env)
        else:
            return eval_expr(expr.else_expr, env)
    if isinstance(expr, LetExpr):
        val = eval_expr(expr.value_expr, env)
        new_env = {**env, expr.name: val}  # extend env
        return eval_expr(expr.body_expr, new_env)
    raise ValueError(f"Unknown expression type: {type(expr)}")

# Test: if x > 5 then x * 2 else x + 1
# with x = 7
program = If(
    BinOp('>', Var('x'), Num(5)),
    BinOp('*', Var('x'), Num(2)),
    BinOp('+', Var('x'), Num(1))
)
env = {"x": 7}
result = eval_expr(program, env)
print(f"if x>5 then x*2 else x+1 where x=7 = {result}")

# Test: let y = x * 2 in if y > 10 then y else 0
program2 = LetExpr(
    "y",
    BinOp('*', Var('x'), Num(2)),
    If(BinOp('>', Var('y'), Num(10)), Var('y'), Num(0))
)
print(f"let y=x*2 in if y>10 then y else 0 where x=7: {eval_expr(program2, env)}")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

### Critical Thinking Questions

1. Why does the `If` node in `eval_expr` only evaluate *one* of `then_expr` or `else_expr`? What would go wrong if both branches were always evaluated? Give a concrete example involving a side effect or an error.

2. What is "short-circuit evaluation"? How does it relate to the behavior of `If` in this evaluator? Is the `BinOp` for `'and'` in this evaluator short-circuit or strict? How can you tell?

3. In `LetExpr`, we create a new env dict with `{**env, expr.name: val}` rather than modifying the existing one. Why is this important? What problem would arise if we wrote `env[expr.name] = val` instead, especially in the presence of nested let expressions?

4. What would happen if both branches of `If` were always evaluated (strict semantics)? This is called *strict conditional evaluation*. Name one advantage and one disadvantage of strict evaluation compared to lazy conditional evaluation.

---

## Model 5: Short-Circuit Evaluation and Lazy Conditionals

We saw in Model 4 that the `If` node only evaluates one branch. Python's `and` and `or` operators exhibit similar behavior: they use **short-circuit evaluation** (also called *lazy* or *non-strict* evaluation).

- `A and B`: if `A` is `False`, Python does **not** evaluate `B`.
- `A or B`: if `A` is `True`, Python does **not** evaluate `B`.

This is crucial for correctness (avoiding errors) and performance (avoiding expensive computations). The code below demonstrates short-circuit evaluation and contrasts it with strict evaluation, then shows how to build a lazy conditional using thunks (zero-argument functions that delay evaluation).

```python
# Short-circuit evaluation
def safe_divide(a, b):
    return a / b if b != 0 else None

# Without short-circuit, this would call safe_divide(10, 0) even when False
x = 0
# Python's 'and' is short-circuit: doesn't evaluate right side if left is False
result1 = x != 0 and (10 / x > 1)
print(f"x!=0 and 10/x>1 = {result1}")  # False, no ZeroDivisionError

# Python's 'or' is short-circuit too
def expensive_computation():
    print("  (expensive computation called)")
    return 42

cached = None
value = cached or expensive_computation()
print(f"cached or expensive: {value}")

# Simulate strict vs lazy evaluation in our evaluator
import time

def make_lazy(thunk):
    """Wrap a computation to be lazy (only evaluate when called)."""
    computed = [False]
    result = [None]
    def force():
        if not computed[0]:
            result[0] = thunk()
            computed[0] = True
        return result[0]
    return force

def lazy_if(cond, then_thunk, else_thunk):
    """Lazy conditional: only evaluates the chosen branch."""
    return then_thunk() if cond else else_thunk()

# Demonstrate: lazy if avoids computing both branches
print("\nLazy if demonstration:")
answer = lazy_if(
    True,
    lambda: (print("  evaluating THEN"), 42)[1],
    lambda: (print("  evaluating ELSE"), 0)[1]
)
print(f"Result: {answer}")  # Only prints "evaluating THEN"
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

### Critical Thinking Questions

1. What is short-circuit evaluation and why is it important? Give an example from the code above where short-circuit evaluation prevents a runtime error that strict evaluation would cause.

2. Give an original example (not from the code above) where short-circuit evaluation of `or` is useful for avoiding an expensive computation. Describe what the "expensive" part would be and why it is safe to skip.

3. What is the difference between "lazy" and "strict" conditional evaluation? In `lazy_if`, how do lambda expressions (thunks) delay evaluation until the branch is chosen? What is the overhead cost of using thunks?

4. How does Python's `and`/`or` short-circuiting relate to the `If` node in the evaluator from Model 4? Are they handling laziness in the same way? What is the key difference in how Python implements short-circuiting versus how `lazy_if` implements it above?

---

## Multiple Choice

**Question 1:** In a functional language where `if` is an expression, what must be true?

[[MC]]
- [( )] Only the condition is evaluated; neither branch is evaluated until explicitly called
- [(X)] Both branches exist syntactically, but only one is evaluated based on the condition
- [( )] Both branches are always evaluated eagerly, and the result is selected after
- [( )] The condition and both branches are always evaluated to check for errors

---

**Question 2:** In Scheme, `let` binds all variables simultaneously using the *outer* environment. `letrec` allows bindings to refer to each other. Which of the following **requires** `letrec` and cannot be expressed with plain `let`?

[[MC]]
- [( )] `(let ((x 1) (y 2)) (+ x y))`
- [( )] `(let ((x 5)) (let ((y x)) y))`
- [(X)] `(letrec ((even? (lambda (n) (if (= n 0) #t (odd? (- n 1))))) (odd? (lambda (n) (if (= n 0) #f (even? (- n 1)))))) (even? 4))`
- [( )] `(let ((f (lambda (x) (* x 2)))) (f 5))`

---

**Question 3:** Consider the `BinOp` case in the expression evaluator from Model 4. Both `eval_expr(expr.left, env)` and `eval_expr(expr.right, env)` are called before performing the operation. What does this mean about the evaluator's strategy for `BinOp`?

[[MC]]
- [( )] It uses lazy evaluation — operands are evaluated only when needed
- [(X)] It uses strict (eager) evaluation — both operands are always evaluated before the operation
- [( )] It uses short-circuit evaluation — the right operand may not be evaluated
- [( )] It uses call-by-name — operands are substituted unevaluated into the operation

---

**Question 4:** Python's `or` operator short-circuits. Given `result = f() or g()`, when is `g()` **not** called?

[[MC]]
- [( )] When `g()` would raise an exception
- [( )] When both `f()` and `g()` return `True`
- [(X)] When `f()` returns a truthy value
- [( )] When `f()` returns `False` or `None`

---

## Exercises

**Exercise 1: While Loop as an Expression**

Add a `While` loop to the expression evaluator from Model 4. Define a new dataclass `WhileExpr(cond, body)`. The evaluator should execute `body` repeatedly as long as `cond` evaluates to `True`, and return the **number of iterations** performed as its value. Add it to `eval_expr` and test it with a small example (e.g., count from 1 to 5 using a mutable variable in the environment).

*Hint:* You will need to allow the environment to be updated during the loop body, which means reconsidering the immutability of `env`. Discuss with your group how to handle this while keeping the evaluator as clean as possible.

**Exercise 2: Not and Cond**

Extend the expression evaluator with two new constructs:

- `NotExpr(expr)` — a unary operator that negates a boolean expression.
- `CondExpr(clauses, else_expr)` — a multi-branch conditional, where `clauses` is a list of `(condition, result)` pairs. It evaluates each condition in order and returns the result of the first truthy one; if none match, it evaluates `else_expr`.

Add both to `eval_expr` and write a test that uses `CondExpr` to classify a number as "negative", "zero", or "positive".

**Exercise 3: Sequential Let (let*)**

In Scheme, `let*` allows each binding to see the bindings that came before it (sequential binding). For example:

```
(let* ((x 2) (y (* x 3))) y)  ; y = 6, because y sees x
```

Write a Python function `let_star(bindings_list, body)` where `bindings_list` is a list of `(name, value)` pairs evaluated sequentially (each sees the previous ones) and `body` is a lambda taking keyword arguments for all bindings. Test it with at least two bindings where the second depends on the first.

**Exercise 4: Short-Circuit BinOp in the Evaluator**

The `BinOp` case in the evaluator from Model 4 always evaluates both operands before performing the operation. This means `'and'` and `'or'` are strict, not short-circuit.

Modify `eval_expr` so that `BinOp` with `op='and'` and `op='or'` use short-circuit evaluation: for `'and'`, if the left side is `False`, do not evaluate the right side; for `'or'`, if the left side is `True`, do not evaluate the right side.

Write a test that demonstrates the difference — construct an expression where strict evaluation would raise a `ZeroDivisionError` but lazy/short-circuit evaluation succeeds.

---

## Reflection Prompt

In Python, `if` is a statement; in Haskell, `if` is an expression. What practical difference does this make when writing code? Write 3–4 sentences considering: where you can place an `if`, how it affects composability (e.g., can you use `if` inside a list comprehension, as a function argument, or inside another expression directly?), and whether you think expression-based `if` or statement-based `if` leads to clearer code in typical programming tasks.

---

## Further Reading

- **PLAI Ch. 7** — Conditionals and Bindings: the primary reference for this activity. Covers how interpreters handle `if` and `let` at the semantic level.
- **"Structure and Interpretation of Computer Programs" (SICP) Ch. 1.1** — Expressions: introduces the expression-based model of computation in Scheme and motivates why everything being an expression simplifies reasoning.
- **Python PEP 572** — Assignment Expressions (the walrus operator `:=`): the design rationale behind adding a limited expression-form assignment to Python, including discussion of the tradeoffs and rejected alternatives.
- **Wadler, "Theorems for Free" (1989)** — A research paper explaining why purely expression-based (purely functional) languages have desirable mathematical properties, including the ability to reason about programs using equational reasoning.
