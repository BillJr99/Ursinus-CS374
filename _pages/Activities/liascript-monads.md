<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://github.com/BillJr99/Ursinus-CS374-Fall2026/blob/gh-pages/_pages/Activities/liascript-monads.md or locally via https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374-Fall2026/gh-pages/_pages/Activities/liascript-monads.md

import: https://raw.githubusercontent.com/liascript/CodeRunner/master/README.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

# Monads: Programmable Semicolons

## Learning Goals

By the end of this activity, you will be able to:

- Implement a `Maybe` monad in Python with `bind` (`>>=`) and `return`/`unit`, and use it to eliminate pyramid-of-doom null-checking from a multi-step pipeline
- State and verify the three monad laws (left identity, right identity, associativity) for a concrete monad implementation
- Implement a `List` monad and use it to model nondeterministic computation, explaining how `bind` distributes over the list of possibilities
- Read basic Haskell `do`-notation and translate it into the equivalent chain of `>>=` calls
- Recognize monadic patterns in Python code you already use (`with` blocks as IO monad, `async`/`await` as continuation monad, `None`-propagation as Maybe monad)

A **monad** is a design pattern for sequencing computations when something extra needs to happen between each step — propagating failure, threading state, collecting effects, or managing nondeterminism. Philip Wadler called `>>=` (pronounced "bind") a *programmable semicolon*: instead of `;` running statements silently in sequence, `>>=` runs a customizable "glue" operation between each step. Today we build the intuition bottom-up — from functions to functors to monads — and verify every construction in Python before touching Haskell. The arc: **the problem → Maybe → the three monad laws → List → do-notation → IO**.

---

## Before You Begin

> **Prerequisites for this activity**
>
> **Required:**
>
> - **Higher-order functions** — you are comfortable passing functions as arguments and returning them. You know what `map`, `filter`, and `reduce` do.
> - **Closures** — you understand that a function can "capture" variables from its enclosing scope. `lambda x: x + n` captures `n`.
> - **Type systems basics** — you have seen type annotations in Python or another language. You understand what "a function that takes an `int` and returns a `str`" means as a type.
>
> **Helpful but not required:**
>
> - **Haskell syntax** — the activity introduces every piece of Haskell syntax it uses. You do not need prior Haskell experience, but familiarity helps.
>
> **If you are rusty on any Required topic**, spend 5 minutes reviewing before continuing — monads layer heavily on all three foundations.

---

## You Already Use Monads

> **Stop. Read this before anything else.**
>
> Monads are not exotic mathematics invented to confuse you. You have already been using them for years — you just did not know the word.
>
> Here are three examples from Python you have certainly seen:
>
> **Python's `with open(...) as f:` block** is the **IO monad**. It sequences an operation (open file), ensures cleanup (close file), and threads the file handle through your code — all without you managing the lifecycle by hand.
>
> **None-safe chaining via `and`** is the **Maybe monad**. `x = d.get("key") and d["key"].upper()` short-circuits on `None` without an `if` statement. The "glue" between each step is: "if the previous step returned None, stop; otherwise keep going."
>
> **Python's `asyncio` / `async`/`await`** is the **async monad** (also called the Continuation monad). `result = await fetch(url)` looks like a normal assignment, but under the hood it suspends the coroutine, hands control back to the event loop, and resumes exactly where it left off. The "glue" between each `await` is the event loop's scheduler.
>
> **The one-sentence definition:** A monad is a design pattern for chaining computations while tracking a "side effect" — error state, IO, non-determinism, mutable state, async scheduling, etc. — in a way that is invisible to the pipeline author but customizable by the monad designer.
>
> Every monad you build today has already appeared in your programming life. The goal of this activity is to *name* what you already know.

---

## Directions and Group Roles

Work in your POGIL team with rotated roles (**Manager**, **Recorder**, **Presenter**, **Reflector**). This is a derivation day: every abstraction is *derived* from a concrete problem. Do not accept a definition until you have seen the problem it solves. The Recorder writes Python implementations on the whiteboard; the Presenter explains the monad laws. After class, respond to the reflective prompt individually in your notebook.

---

# Part I: The Problem

## 1. The Pipeline Problem — Why Monads Exist

Before we define anything, here is the problem that monads solve.

Suppose you have three operations, each of which might fail and return `None`:

- `divide(x, y)` — fails if `y == 0`
- `sqrt(x)` — fails if `x < 0`
- `log(x)` — fails if `x <= 0`

Without any monad, you get the **pyramid of doom**:

```python  liascript
def divide(x, y):
    return x / y if y != 0 else None

def safe_sqrt(x):
    return x ** 0.5 if x >= 0 else None

def safe_log(x):
    import math
    return math.log(x) if x > 0 else None

# Without monad: pyramid of doom
def pipeline_manual(x, y):
    result1 = divide(x, y)
    if result1 is not None:
        result2 = safe_sqrt(result1)
        if result2 is not None:
            result3 = safe_log(result2)
            # ... and it keeps nesting deeper with every new step
            return result3
    return None

print(pipeline_manual(4, 1))   # some float
print(pipeline_manual(-4, 1))  # None (sqrt of negative)
print(pipeline_manual(4, 0))   # None (division by zero)
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

Notice the pattern: every single step is wrapped in `if result is not None`. If you add a fourth step, you add another `if`. The logic you care about (divide, sqrt, log) is buried under boilerplate you do not care about.

Now here is the same pipeline **with the Maybe monad** (we will build this below):

```python  liascript
# With Maybe monad: flat chain
# (This is a preview — we build Maybe in the next section)

class Maybe:
    def __init__(self, value):
        self.value = value
    @classmethod
    def just(cls, x): return cls(x)
    @classmethod
    def nothing(cls): return cls(None)
    def bind(self, f):
        if self.value is None:
            return Maybe.nothing()
        return f(self.value)
    def __repr__(self):
        return f"Just({self.value})" if self.value is not None else "Nothing"

import math

def divide(x, y):
    return Maybe.nothing() if y == 0 else Maybe.just(x / y)

def safe_sqrt(x):
    return Maybe.nothing() if x < 0 else Maybe.just(x ** 0.5)

def safe_log(x):
    return Maybe.nothing() if x <= 0 else Maybe.just(math.log(x))

# With Maybe monad: flat chain — no pyramid, no repeated if-checks
result = Maybe.just(4).bind(lambda x: divide(x, 1)).bind(safe_sqrt).bind(safe_log)
print(result)

result2 = Maybe.just(4).bind(lambda x: divide(x, 0)).bind(safe_sqrt).bind(safe_log)
print(result2)  # Nothing propagates automatically
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

The `if result is not None` check still exists — but it is now inside `bind`, written once, rather than repeated by every caller. This is the core idea.

> **CTQ 0.1** In the pyramid-of-doom version, how many times is the pattern `if result is not None` written? In the monad version, how many times? Where did the other occurrences go?

> **CTQ 0.2** If you added a fourth step `safe_reciprocal(x)` (fails if `x == 0`) to the pipeline, how many lines would you add in the pyramid-of-doom version versus the monad version?

---

## 2. Chaining Operations That Can Fail

Suppose several operations each return either a value or `None` (failure). Naive chaining drowns in `if` checks:

```python  liascript
def safe_div(x, y):
    return x / y if y != 0 else None

def safe_sqrt(x):
    return x ** 0.5 if x >= 0 else None

# Without a monad: tedious, fragile
def pipeline_manual(x, y):
    t1 = safe_div(x, y)
    if t1 is None: return None
    t2 = safe_sqrt(t1)
    if t2 is None: return None
    return t2

print(pipeline_manual(4, 1))    # 2.0
print(pipeline_manual(-4, 1))   # None (sqrt of negative)
print(pipeline_manual(4, 0))    # None (division by zero)
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

The pattern `result = f(x); if result is None: return None; ...` repeats every time. A monad *abstracts* that repetition into one operator.

---

## The Maybe Monad — Full Implementation

```python  liascript
try:
    class Maybe:
        def __init__(self, value):
            self.value = value    # None means failure

        @classmethod
        def just(cls, x):
            return cls(x)         # wrap a success value

        @classmethod
        def nothing(cls):
            return cls(None)      # wrap failure

        def bind(self, f):
            # ">>= f": if we have a value, pass it to f; else propagate failure
            if self.value is None:
                return Maybe.nothing()
            return f(self.value)

        def __repr__(self):
            return f"Just({self.value})" if self.value is not None else "Nothing"

    # Wrap safe_div and safe_sqrt to return Maybe values
    def safe_div(x, y):
        return Maybe.nothing() if y == 0 else Maybe.just(x / y)

    def safe_sqrt(x):
        return Maybe.nothing() if x < 0 else Maybe.just(x ** 0.5)

    # The monadic pipeline: bind threads Maybe through the chain
    def pipeline(x, y):
        return safe_div(x, y).bind(safe_sqrt)

    print(pipeline(4, 1))    # Just(2.0)
    print(pipeline(-4, 1))   # Nothing
    print(pipeline(4, 0))    # Nothing

    # Multiple steps: x / y, then sqrt, then negate
    def multi(x, y):
        return (safe_div(x, y)
                .bind(safe_sqrt)
                .bind(lambda v: Maybe.just(-v)))

    print(multi(4, 1))   # Just(-2.0)

except Exception as e:
    print(f"[monads:maybe] {e}")
    import traceback; traceback.print_exc()
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

---

## Model 1: Interrogating Maybe

> **Watch out!** A monad is NOT a container. It is a pattern for *sequencing computations*. The container metaphor ("Maybe is a box that either has a value or is empty") is a useful first intuition, but it breaks down for the State and Continuation monads, which you will see later. Think of a monad as a *pipeline builder*, not a *box*.

### What Each Piece Does

Before the CTQs, make sure you can answer these warmup questions to yourself:

- `Maybe.just(5)` — what does this produce? What is `self.value`?
- `Maybe.nothing()` — what does this produce? What is `self.value`?
- `Maybe.just(5).bind(lambda x: Maybe.just(x * 2))` — trace through `bind` step by step. What is returned?
- `Maybe.nothing().bind(lambda x: Maybe.just(x * 2))` — trace through `bind`. Is the lambda called?

### Critical Thinking Questions

> **CTQ 1.1** In `bind`, the check `if self.value is None: return Maybe.nothing()` is the "glue" that runs between every step. What would happen to the remaining `.bind` calls in `multi(4, 0)` — are they called or skipped? Trace through.

> **CTQ 1.2** `Maybe.just(x)` is called `return` in Haskell (it *wraps* a value without doing anything else). Why is a `return` function necessary alongside `bind`? What would go wrong if you could only chain `bind` calls?

> **CTQ 1.3** The `if result is None: return None` pattern from the manual pipeline is now *inside* `bind` — the caller never writes it. Identify one other situation in your Mini interpreter where you repeated a similar check everywhere. How would a monad-like abstraction eliminate it?

> **CTQ 1.4** None-checks are a form of *implicit control flow* — the function short-circuits without the caller's knowledge. How does the Maybe monad make that control flow *explicit* while still hiding it from the pipeline author? Is this better or worse than Python's exceptions for this use case?

---

# Part I-B: Two More Concrete Monads in Python

The Maybe monad handles one specific "side effect": the possibility of failure. But monads can track any side effect. Here are two more.

## The Result Monad (aka Either)

The Maybe monad's weakness: when something fails, you get `Nothing` — but you do not know *why*. The **Result monad** (called Either in Haskell) fixes this by carrying an error message in the failure case.

```python  liascript
try:
    class Ok:
        """Represents a successful computation."""
        def __init__(self, value):
            self.value = value

        def bind(self, f):
            # Success: pass the value to f
            return f(self.value)

        def __repr__(self):
            return f"Ok({self.value})"

    class Err:
        """Represents a failed computation with an error message."""
        def __init__(self, message):
            self.message = message

        def bind(self, f):
            # Failure: skip f entirely, propagate the error
            return self

        def __repr__(self):
            return f"Err({self.message!r})"

    # Now our functions return Ok or Err instead of None
    def safe_div(x, y):
        if y == 0:
            return Err(f"Cannot divide {x} by zero")
        return Ok(x / y)

    def safe_sqrt(x):
        if x < 0:
            return Err(f"Cannot take sqrt of negative number {x}")
        return Ok(x ** 0.5)

    def safe_log(x):
        import math
        if x <= 0:
            return Err(f"Cannot take log of non-positive number {x}")
        return Ok(math.log(x))

    # Chain without try/except — errors propagate automatically
    result1 = safe_div(16, 4).bind(safe_sqrt).bind(safe_log)
    print(result1)   # Ok(some float)

    result2 = safe_div(16, 0).bind(safe_sqrt).bind(safe_log)
    print(result2)   # Err('Cannot divide 16 by zero') — error from step 1

    result3 = safe_div(-16, 4).bind(safe_sqrt).bind(safe_log)
    print(result3)   # Err('Cannot take sqrt of negative number -4.0') — error from step 2

except Exception as e:
    print(f"[monads:result] {e}")
    import traceback; traceback.print_exc()
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

> **Watch out!** Python's `list` comprehensions are syntactic sugar for the **List monad**. The expression `[y for x in xs for y in f(x)]` is exactly `xs >>= f` in Haskell's list monad. Every nested `for` clause is a monadic `bind`. You have been writing the List monad since your first Python class.

### Critical Thinking Questions

> **CTQ 1.5** In the Result monad, `Err.bind` ignores `f` and returns `self`. This means once an error occurs, *all subsequent computations are skipped*. What is the advantage of this behavior over using `try/except`? What is one disadvantage?

> **CTQ 1.6** Both `Ok` and `Err` implement `bind`, but with different behavior. This is the *same interface* with *different implementations*. What design pattern from object-oriented programming does this resemble?

> **CTQ 1.7** In `result2` above, the error message says "Cannot divide 16 by zero." The `.bind(safe_sqrt)` and `.bind(safe_log)` calls after it are still written in the code — they are just skipped at runtime. How does this compare to early-return (`if ... return None`) in terms of readability?

---

## The State Monad (Simplified)

The State monad threads a piece of mutable state through a sequence of pure functions — without actually mutating anything. Each step receives the current state, returns a value *and* a new state, and passes the new state to the next step.

Think of it like a factory assembly line where each station receives the product, modifies it, and passes it to the next station.

```python  liascript
try:
    class State:
        """
        Wraps a function: state -> (value, new_state)
        The 'state' can be anything: an integer counter, a stack, a dict, etc.
        """
        def __init__(self, run_fn):
            self._run = run_fn   # a function: s -> (value, s)

        @classmethod
        def pure(cls, x):
            # "return x" in a stateful context: don't touch the state
            return cls(lambda s: (x, s))

        def bind(self, f):
            # Run self to get (value, new_state), then run f(value) with new_state
            def run(s):
                value, new_s = self._run(s)   # step 1: run current computation
                return f(value)._run(new_s)   # step 2: run f with new state
            return State(run)

        def execute(self, initial_state):
            return self._run(initial_state)

    # State primitives
    def get():
        """Returns the current state as the value (without changing it)."""
        return State(lambda s: (s, s))

    def put(new_state):
        """Sets the state to new_state; returns None as the value."""
        return State(lambda s: (None, new_state))

    def modify(f):
        """Applies f to the current state."""
        return State(lambda s: (None, f(s)))

    # Example: thread a counter through three steps
    # Each step increments the counter by a different amount
    program = (
        modify(lambda n: n + 1)          # counter: 0 -> 1
        .bind(lambda _: modify(lambda n: n + 10))   # counter: 1 -> 11
        .bind(lambda _: modify(lambda n: n * 2))    # counter: 11 -> 22
        .bind(lambda _: get())           # read final state as value
    )

    value, final_state = program.execute(0)   # start with counter = 0
    print(f"value={value}, final_state={final_state}")  # value=22, final_state=22

    # A more realistic example: a stack machine
    def push(x):
        return modify(lambda stack: stack + [x])

    def pop():
        return State(lambda stack: (stack[-1], stack[:-1]) if stack else (None, stack))

    stack_program = (
        push(10)
        .bind(lambda _: push(20))
        .bind(lambda _: push(30))
        .bind(lambda _: pop())
        .bind(lambda top: State.pure(f"popped: {top}"))
    )

    result, remaining_stack = stack_program.execute([])
    print(result)            # popped: 30
    print(remaining_stack)   # [10, 20]

except Exception as e:
    print(f"[monads:state] {e}")
    import traceback; traceback.print_exc()
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

### Critical Thinking Questions

> **CTQ 1.8** In the State monad, `bind` calls `self._run(s)` to get a `(value, new_state)` pair, then passes `new_state` to the next step. What would happen if `bind` passed the *original* `s` to the next step instead of `new_s`? Give a concrete example of the bug this would cause.

> **CTQ 1.9** The State monad threads state without any mutable variables — `s` is never assigned to; each step receives it as a function argument and returns a new one. How does this relate to the concept of *pure functions* from the earlier activities?

> **CTQ 1.10** The container metaphor ("a monad is a box") breaks for the State monad. There is no "box" here — `State` wraps a *function*, not a value. What does this reveal about the true nature of a monad?

---

# Part II: The Three Laws

## 3. What Makes Something a Monad?

Three laws — not rules imposed from outside, but the conditions that make `bind` and `return` compose predictably. Every monad obeys them; if they fail, the abstraction breaks.

### The Laws in Plain English First

Before the formal versions, here is what each law means in English:

**Left identity** — "Wrapping then immediately unwrapping is a no-op."
If you take a value `x`, wrap it in `just(x)`, and immediately call `.bind(f)`, you should get the same result as just calling `f(x)` directly. The wrapping did not add anything.

**Right identity** — "Unwrapping then re-wrapping is a no-op."
If you have a monad `m` and you call `.bind(just)`, you should get back something equivalent to `m`. Passing the wrapped value through the identity function should not change it.

**Associativity** — "Grouping of `.bind` chains does not matter."
Just as `(1 + 2) + 3 == 1 + (2 + 3)` for addition, `(m.bind(f)).bind(g)` should equal `m.bind(lambda x: f(x).bind(g))`. You can refactor long `.bind` chains freely — extracting a sub-chain into a helper function will not change the result.

### Formal Statements

**Left identity:** `return(a).bind(f) == f(a)`

**Right identity:** `m.bind(return) == m`

**Associativity:** `(m.bind(f)).bind(g) == m.bind(lambda x: f(x).bind(g))`

The associativity law is why `bind` *is* a programmable semicolon: just as `(a; b); c` and `a; (b; c)` mean the same thing in imperative code, monadic sequencing is associative.

---

## Code Cell: Verifying the Laws

```python  liascript
try:
    # Reuse Maybe from above (re-define inline for self-containment)
    class Maybe:
        def __init__(self, value):
            self.value = value
        @classmethod
        def just(cls, x): return cls(x)
        @classmethod
        def nothing(cls): return cls(None)
        def bind(self, f):
            return Maybe.nothing() if self.value is None else f(self.value)
        def __eq__(self, other):
            return self.value == other.value
        def __repr__(self):
            return f"Just({self.value})" if self.value is not None else "Nothing"

    ret = Maybe.just    # "return" in Haskell
    f = lambda x: Maybe.just(x * 2)
    g = lambda x: Maybe.just(x + 10) if x > 0 else Maybe.nothing()

    a = 5
    m = Maybe.just(3)

    # Left identity: ret(a).bind(f) == f(a)
    lhs_li = ret(a).bind(f)
    rhs_li = f(a)
    print("left identity:", lhs_li == rhs_li, f"  ({lhs_li} == {rhs_li})")

    # Right identity: m.bind(ret) == m
    lhs_ri = m.bind(ret)
    print("right identity:", lhs_ri == m, f"  ({lhs_ri} == {m})")

    # Associativity: (m.bind(f)).bind(g) == m.bind(lambda x: f(x).bind(g))
    lhs_as = m.bind(f).bind(g)
    rhs_as = m.bind(lambda x: f(x).bind(g))
    print("associativity:", lhs_as == rhs_as, f"  ({lhs_as} == {rhs_as})")

    # Verify law holds with Nothing too
    n = Maybe.nothing()
    print("nothing + left id:", ret(None).bind(f) == f(None) if False else "N/A (f not defined for None)")
    print("nothing + right id:", n.bind(ret) == n)
    print("nothing + assoc:", n.bind(f).bind(g) == n.bind(lambda x: f(x).bind(g)))

except Exception as e:
    print(f"[monads:laws] {e}")
    import traceback; traceback.print_exc()
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

---

## Model 2: Laws in Action

[[MC]]
A programmer writes a "monad" where `m.bind(return)` returns `Maybe.nothing()` regardless of `m`. Which monad law does this violate?
- ( ) Left identity — wrapping then binding gives wrong result
- (x) Right identity — binding with the identity function must return the original monad
- ( ) Associativity — grouping of bind chains gives different results
- ( ) None; this is still a valid monad

### Critical Thinking Questions

> **CTQ 2.1** The left identity law says `return(a).bind(f) == f(a)`. In words: "wrapping `a` and immediately passing it to `f` is the same as just calling `f(a)`." Why is this important? Give an example where a `return` that *did* something extra (beyond wrapping) would break a pipeline.

> **CTQ 2.2** Associativity means you can refactor long `bind` chains freely. Give a concrete example where the non-associativity of `bind` would make refactoring dangerous — where `(m.bind(f)).bind(g) ≠ m.bind(lambda x: f(x).bind(g))`.

> **CTQ 2.3** Your Mini interpreter's evaluator has an implicit "sequential execution" order: statements run one after another. In what sense is this already a monad? What is the "glue" between each statement, and what would you have to change to make it explicit?

> **CTQ 2.4** We verified the laws hold for `Maybe.nothing()`. Does this make intuitive sense for the right identity law? If `m` is `Nothing`, then `m.bind(ret)` calls `bind` with `ret` — but `bind` on `Nothing` returns `Nothing` without calling `ret`. So `Nothing.bind(ret) == Nothing`. Why is this the *correct* behavior? What would it mean if `Nothing.bind(ret)` returned `Just(None)` instead?

---

# Part III: The List Monad — Nondeterminism

## 4. Lists as Nondeterministic Computations

The List monad treats a `[x, y, z]` as "a computation that nondeterministically returns x, y, or z." `bind` applies a function to every element and concatenates the results: it *fans out* all possibilities simultaneously.

```haskell
-- Haskell list monad (for reference)
do x <- [1, 2, 3]
   y <- [10, 20]
   return (x + y)
-- Result: [11, 21, 12, 22, 13, 23]
```

This is list comprehension — the `do` notation and `[x + y | x <- [1,2,3], y <- [10,20]]` compile to the same thing.

---

## Code Cell: The List Monad

```python  liascript
try:
    class ListM:
        def __init__(self, values):
            self.values = list(values)

        @classmethod
        def ret(cls, x):
            return cls([x])

        def bind(self, f):
            # Apply f to each element; f returns a ListM; concatenate all
            result = []
            for v in self.values:
                result.extend(f(v).values)
            return ListM(result)

        def __repr__(self):
            return f"ListM({self.values})"

    xs = ListM([1, 2, 3])
    ys = ListM([10, 20])

    # Cartesian product: all pairs (x, y)
    sums = xs.bind(lambda x: ys.bind(lambda y: ListM.ret(x + y)))
    print("sums:", sums)

    # Compare to list comprehension — same result
    lc_sums = [x + y for x in [1, 2, 3] for y in [10, 20]]
    print("list comprehension:", lc_sums)
    print("same result:", sums.values == lc_sums)

    # Pythagorean triples up to n
    def pythag(n):
        ns = ListM(range(1, n + 1))
        return (ns
            .bind(lambda a: ns
            .bind(lambda b: ns
            .bind(lambda c:
                ListM([f"({a},{b},{c})"] if a*a + b*b == c*c and a <= b <= c
                      else []
                )))))
    print("Pythagorean triples <= 10:", pythag(10))

    # Verify left identity
    f = lambda x: ListM([x, x * 2])
    print("list left id:", ListM.ret(3).bind(f).values == f(3).values)

except Exception as e:
    print(f"[monads:list] {e}")
    import traceback; traceback.print_exc()
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

---

## Model 3: Nondeterminism

### Critical Thinking Questions

> **CTQ 3.1** `bind` for `ListM` concatenates results. The "glue" here is not failure propagation (as in Maybe) but *branching*: every possibility is explored. What real-world algorithm does this resemble? (Hint: think about backtracking search and Prolog from the Language Design module.)

> **CTQ 3.2** `ListM([])` (the empty list) acts as "no solutions" — analogous to `Maybe.nothing()`. Verify that `ListM([]).bind(f)` returns `ListM([])` for any `f`. Why is this the correct "failure" behavior for nondeterminism?

> **CTQ 3.3** Python's list comprehension `[x + y for x in [1,2,3] for y in [10,20]]` produces the same result as the List monad's bind chain. In one sentence: what does the List monad's `bind` correspond to in list comprehension syntax?

> **CTQ 3.4** The "side effect" tracked by the Maybe monad is failure. The "side effect" tracked by the List monad is nondeterminism (multiple possible values). What is the "side effect" being tracked by each of the following: (a) the Result monad, (b) the State monad, (c) the IO monad?

---

# Part IV: The IO Monad — Effects in a Pure Language

## 5. Sequencing Side Effects

Haskell is a *pure* language: functions have no side effects. But programs must print output, read files, and interact with the world. The **IO monad** threads the "state of the world" implicitly through every IO-performing function, ensuring effects happen in order and are tracked by the type system.

You do not implement IO from scratch in Python (Python is impure by design), but you can *simulate* the idea: an `IO` value is a function from "current world state" to "(value, new world state)." `bind` sequences these world-transformations.

```python  liascript
# A toy IO monad that threads a "world log" instead of the real world
class IO:
    def __init__(self, run):
        self._run = run         # run : world -> (value, world)

    @classmethod
    def pure(cls, x):
        return cls(lambda w: (x, w))   # return: does nothing to the world

    def bind(self, f):
        def run(w):
            v, w2 = self._run(w)   # run self, get value + new world
            return f(v)._run(w2)   # run f(v) in the new world
        return IO(run)

    def execute(self):
        return self._run([])       # start with empty world log

# Demonstrate: pure wraps a value without touching the world
val, log = IO.pure(42).execute()
print(f"value={val}, log={log}")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

---

## Code Cell: Toy IO Monad

```python  liascript
try:
    class IO:
        def __init__(self, run):
            self._run = run

        @classmethod
        def pure(cls, x):
            return cls(lambda w: (x, w))

        def bind(self, f):
            def run(w):
                v, w2 = self._run(w)
                return f(v)._run(w2)
            return IO(run)

        def execute(self):
            val, log = self._run([])
            return val, log

    def io_print(msg):
        return IO(lambda w: (None, w + [f"PRINT: {msg}"]))

    def io_read(prompt):
        return IO(lambda w: (f"<user input for '{prompt}'>", w + [f"READ: {prompt}"]))

    # Sequence: print a greeting, read a name, print "hello name"
    program = (
        io_print("What is your name?")
        .bind(lambda _: io_read("name"))
        .bind(lambda name: io_print(f"Hello, {name}!"))
    )

    val, log = program.execute()
    print("Execution log:")
    for entry in log: print(" ", entry)

except Exception as e:
    print(f"[monads:io] {e}")
    import traceback; traceback.print_exc()
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

---

## Model 4: IO and Purity

### Critical Thinking Questions

> **CTQ 4.1** In Haskell, a function of type `Int -> IO String` is *pure* — it does not actually perform IO. It produces an `IO String` value that describes what to do. Only the runtime executes it. How does this relate to the "values are descriptions of actions" idea in the toy IO monad above?

> **CTQ 4.2** In the IO monad, `bind` sequences two world-transformations. If you swapped the order — passing `w` to `f(v)` before `self._run` — what would break? What real-world bug does this correspond to?

> **CTQ 4.3** The type of `bind` for IO is `IO a -> (a -> IO b) -> IO b`. In words: "given an IO action that produces an `a`, and a function that turns an `a` into an IO action producing a `b`, produce an IO action producing a `b`." How is this *exactly* like writing `x = await some_async_function(); return x + 1` in Python?

> **CTQ 4.4** Compare the IO monad to the State monad. In State, the "state" being threaded is explicit in your code (you pass `s` everywhere). In IO, the "state" (the real world) is hidden inside `_run`. What is the advantage of hiding it? What might be the disadvantage?

---

# Part V: Do-Notation as Syntactic Sugar

## 6. Making Monads Readable

Haskell's `do` notation desugars to `bind` chains:

```haskell
do x <- action1
   y <- action2 x
   return (x + y)

-- desugars to:
action1 >>= \x -> action2 x >>= \y -> return (x + y)
```

Python's `for` desugars similarly for the List monad, and `async`/`await` desugars for the IO/async monad. The pattern is always the same: `x <- m` becomes `m >>= \x -> rest`.

---

## Code Cell: Simulating Do-Notation

```python  liascript
try:
    # Simulate do-notation using a generator-based approach for Maybe
    class Maybe:
        def __init__(self, value): self.value = value
        @classmethod
        def just(cls, x): return cls(x)
        @classmethod
        def nothing(cls): return cls(None)
        def bind(self, f):
            return Maybe.nothing() if self.value is None else f(self.value)
        def __repr__(self):
            return f"Just({self.value})" if self.value is not None else "Nothing"

    # A helper that runs a generator as a monad's do-notation
    def do(gen_fn, monad_class=Maybe):
        def run(*args):
            gen = gen_fn(*args)
            def step(value):
                try:
                    m = gen.send(value)   # resume generator with the bound value
                    return m.bind(step)   # bind the next step
                except StopIteration as e:
                    return monad_class.just(e.value)  # wrap final return value
            try:
                m = next(gen)
                return m.bind(step)
            except StopIteration as e:
                return monad_class.just(e.value)
        return run

    def safe_div(a, b):
        return Maybe.nothing() if b == 0 else Maybe.just(a / b)

    def safe_sqrt(x):
        return Maybe.nothing() if x < 0 else Maybe.just(x ** 0.5)

    # "do-notation" using Python generators — each yield is a monadic bind
    @do
    def pipeline(x, y):
        t = yield safe_div(x, y)   # like: t <- safe_div x y
        s = yield safe_sqrt(t)     # like: s <- safe_sqrt t
        return s * 2

    print(pipeline(4, 1))    # Just(4.0)
    print(pipeline(-4, 1))   # Nothing
    print(pipeline(4, 0))    # Nothing

except Exception as e:
    print(f"[monads:do] {e}")
    import traceback; traceback.print_exc()
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

---

## Model 5: Do-Notation

[[MC]]
In Haskell's `do` notation, `x <- m` desugars to `m >>= \x -> ...rest...`. What does `_ <- io_print("hello")` (where the bound value is discarded) desugar to?
- ( ) `io_print("hello") >>= \_ -> ()`
- (x) `io_print("hello") >>= \_ -> rest` (bind with a function that ignores its argument)
- ( ) `return (io_print("hello"))`
- ( ) `io_print "hello"` (no desugaring needed)

### Critical Thinking Questions

> **CTQ 5.1** The generator-based `do` simulation uses Python's `yield` to suspend a function and resume it with a value. In the CPS activity, `yield` was described as "giving the current continuation to the caller." Reconcile: how is `yield safe_div(x, y)` in the do-notation example equivalent to `safe_div_cps(x, y, lambda t: ...)`?

> **CTQ 5.2** Haskell's do-notation works for *any* monad — Maybe, List, IO, State, Parser. What is the one thing that must be the same across all of them for the desugaring to work?

> **CTQ 5.3** Your Mini interpreter's evaluator sequences statements: `eval_block` loops over a list of statements. Is this a monad? If you wanted to add early-exit (like `return` in the middle of a block), what would the "glue" between statements need to do? (Hint: this is exactly the `ReturnSignal` exception your Mini interpreter uses — describe it as a monad.)

> **CTQ 5.4** Python's `async`/`await` syntax is do-notation for the async monad. Write out what `result = await fetch(url)` would look like if Python used Haskell-style explicit bind instead of `await`. What does the `await` keyword "hide" from the programmer?

---

# Part VI: Exercises

1. **State monad extended.** Using the `State` monad implemented above, simulate a simple stack-based calculator that evaluates Reverse Polish Notation (RPN). Push numbers onto the stack; `+` and `*` operations pop two values and push the result. Evaluate `"3 4 + 5 *"` and verify the result is 35. Implement each operation as a `State` computation and chain them with `bind`.

2. **Parser monad.** A `Parser(run)` wraps `string -> (value, rest)` or `None` on failure. Implement `pure` and `bind`; implement `char(c)` (matches a single character). Use Parser to parse the string `"abc"` character by character. This is how Parsec-style parser combinator libraries work under the hood.

3. **Fmap and Functor.** Before monad, there is **functor**: a container supporting `fmap(f)` that applies `f` inside the container without affecting the structure. Implement `fmap` for Maybe and List. Show that `m.fmap(f).fmap(g) == m.fmap(lambda x: g(f(x)))` (functor composition law).

4. **Writer monad.** A `Writer(value, log)` carries a value and an accumulated log (a list of strings). `bind` sequences computations and concatenates their logs. Implement Writer and use it to add logging to the safe arithmetic pipeline: each step logs what it computed. The final result carries the full computation trace.

5. **Law verification for Result.** Verify all three monad laws hold for your `Ok`/`Err` Result monad from Part I-B. Write a Python test function that checks each law with `Ok(5)`, `Err("fail")`, and appropriate `f` and `g` functions. What happens when you check right identity on `Err("original")` — does `Err("original").bind(Ok) == Err("original")`?

---

## Reflection Prompt

In your notebook: Philip Wadler called `>>=` a "programmable semicolon" because it lets you customize what happens between every two steps in a sequence. Your Mini interpreter's evaluator already *has* an implicit semicolon (the statement loop), but it is hardwired. If you replaced it with a monad, what capabilities would you gain? What would you lose? And: the Maybe, List, IO, and State monads all look completely different, yet they obey the same three laws. Does this surprise you — or does it feel like all "chaining" is secretly the same operation?

---

## Further Reading

- Wadler, Philip. "Monads for Functional Programming" (1995). The original tutorial; still the clearest explanation, using exactly the error-handling and state examples from today.
- Hutton, Graham and Erik Meijer. "Monadic Parser Combinators" (1996). Parsers as monads — a direct preview of Exercise 2.
- Haskell Report 2010, Chapter 3.14: `do` notation desugaring — the formal specification.
- Milewski, Bartosz. *Category Theory for Programmers* (online, free). Part III covers monads from the categorical perspective — what "monoid in the category of endofunctors" actually means.
- Dan Piponi. "You Could Have Invented Monads! (And Maybe You Already Have.)" (blog, A Neighborhood of Infinity). The single best motivating essay; shows that monads arise naturally from the problems in Part I.
- Real World Haskell, Chapter 14: Monads — practical examples in a language where monads are unavoidable.
