# Monads: Programmable Semicolons
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

A **monad** is a design pattern for sequencing computations when something extra needs to happen between each step — propagating failure, threading state, collecting effects, or managing nondeterminism. Philip Wadler called `>>=` (pronounced "bind") a *programmable semicolon*: instead of `;` running statements silently in sequence, `>>=` runs a customizable "glue" operation between each step. Today we build the intuition bottom-up — from functions to functors to monads — and verify every construction in Python before touching Haskell. The arc: **the problem → Maybe → the three monad laws → List → do-notation → IO**.

---

## Directions and Group Roles

Work in your POGIL team with rotated roles (**Manager**, **Recorder**, **Presenter**, **Reflector**). This is a derivation day: every abstraction is *derived* from a concrete problem. Do not accept a definition until you have seen the problem it solves. The Recorder writes Python implementations on the whiteboard; the Presenter explains the monad laws. After class, respond to the reflective prompt individually in your notebook.

---

# Part I: The Problem

## 1. Chaining Operations That Can Fail

Suppose several operations each return either a value or `None` (failure). Naive chaining drowns in `if` checks:

```python
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

## Code Cell: The Maybe Monad

```python
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

### Critical Thinking Questions

1. In `bind`, the check `if self.value is None: return Maybe.nothing()` is the "glue" that runs between every step. What would happen to the remaining `.bind` calls in `multi(4, 0)` — are they called or skipped? Trace through.

2. `Maybe.just(x)` is called `return` in Haskell (it *wraps* a value without doing anything else). Why is a `return` function necessary alongside `bind`? What would go wrong if you could only chain `bind` calls?

3. The `if result is None: return None` pattern from the manual pipeline is now *inside* `bind` — the caller never writes it. Identify one other situation in your Mini interpreter where you repeated a similar check everywhere. How would a monad-like abstraction eliminate it?

4. None-checks are a form of *implicit control flow* — the function short-circuits without the caller's knowledge. How does the Maybe monad make that control flow *explicit* while still hiding it from the pipeline author? Is this better or worse than Python's exceptions for this use case?

---

# Part II: The Three Laws

## 2. What Makes Something a Monad?

Three laws — not rules imposed from outside, but the conditions that make `bind` and `return` compose predictably. Every monad obeys them; if they fail, the abstraction breaks.

**Left identity:** `return(a).bind(f) == f(a)`
Wrapping a value and immediately binding is the same as just calling f.

**Right identity:** `m.bind(return) == m`
Binding with "wrap and do nothing" is the identity on monads.

**Associativity:** `(m.bind(f)).bind(g) == m.bind(lambda x: f(x).bind(g))`
The grouping of `bind` chains does not matter.

The associativity law is why `bind` *is* a programmable semicolon: just as `(a; b); c` and `a; (b; c)` mean the same thing in imperative code, monadic sequencing is associative.

---

## Code Cell: Verifying the Laws

```python
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
    print("left identity:", ret(a).bind(f) == f(a))

    # Right identity: m.bind(ret) == m
    print("right identity:", m.bind(ret) == m)

    # Associativity: (m.bind(f)).bind(g) == m.bind(lambda x: f(x).bind(g))
    lhs = m.bind(f).bind(g)
    rhs = m.bind(lambda x: f(x).bind(g))
    print("associativity:", lhs == rhs, "→", lhs)

    # Verify law breaks with Nothing
    n = Maybe.nothing()
    print("nothing + right id:", n.bind(ret) == n)

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

5. The left identity law says `return(a).bind(f) == f(a)`. In words: "wrapping `a` and immediately passing it to `f` is the same as just calling `f(a)`." Why is this important? Give an example where a `return` that *did* something extra (beyond wrapping) would break a pipeline.

6. Associativity means you can refactor long `bind` chains freely. Give a concrete example where the non-associativity of `bind` would make refactoring dangerous — where `(m.bind(f)).bind(g) ≠ m.bind(lambda x: f(x).bind(g))`.

7. Your Mini interpreter's evaluator has an implicit "sequential execution" order: statements run one after another. In what sense is this already a monad? What is the "glue" between each statement, and what would you have to change to make it explicit?

---

# Part III: The List Monad — Nondeterminism

## 3. Lists as Nondeterministic Computations

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

```python
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
    print("Pythagorean triples ≤ 10:", pythag(10))

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

8. `bind` for `ListM` concatenates results. The "glue" here is not failure propagation (as in Maybe) but *branching*: every possibility is explored. What real-world algorithm does this resemble? (Hint: think about backtracking search and Prolog from the Language Design module.)

9. `ListM([])` (the empty list) acts as "no solutions" — analogous to `Maybe.nothing()`. Verify that `ListM([]).bind(f)` returns `ListM([])` for any `f`. Why is this the correct "failure" behavior for nondeterminism?

10. Python's list comprehension `[x + y for x in [1,2,3] for y in [10,20]]` produces the same result as the List monad's bind chain. In one sentence: what does the List monad's `bind` correspond to in list comprehension syntax?

---

# Part IV: The IO Monad — Effects in a Pure Language

## 4. Sequencing Side Effects

Haskell is a *pure* language: functions have no side effects. But programs must print output, read files, and interact with the world. The **IO monad** threads the "state of the world" implicitly through every IO-performing function, ensuring effects happen in order and are tracked by the type system.

You do not implement IO from scratch in Python (Python is impure by design), but you can *simulate* the idea: an `IO` value is a function from "current world state" to "(value, new world state)." `bind` sequences these world-transformations.

```python
# A toy IO monad that threads a "world log" instead of the real world
class IO:
    def __init__(self, run):
        self._run = run         # run : world → (value, world)

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

```python
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

11. In Haskell, a function of type `Int -> IO String` is *pure* — it does not actually perform IO. It produces an `IO String` value that describes what to do. Only the runtime executes it. How does this relate to the "values are descriptions of actions" idea in the toy IO monad above?

12. In the IO monad, `bind` sequences two world-transformations. If you swapped the order — passing `w` to `f(v)` before `self._run` — what would break? What real-world bug does this correspond to?

13. The type of `bind` for IO is `IO a -> (a -> IO b) -> IO b`. In words: "given an IO action that produces an `a`, and a function that turns an `a` into an IO action producing a `b`, produce an IO action producing a `b`." How is this *exactly* like writing `x = await some_async_function(); return x + 1` in Python?

---

# Part V: Do-Notation as Syntactic Sugar

## 5. Making Monads Readable

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

```python
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

14. The generator-based `do` simulation uses Python's `yield` to suspend a function and resume it with a value. In the CPS activity, `yield` was described as "giving the current continuation to the caller." Reconcile: how is `yield safe_div(x, y)` in the do-notation example equivalent to `safe_div_cps(x, y, lambda t: ...)`?

15. Haskell's do-notation works for *any* monad — Maybe, List, IO, State, Parser. What is the one thing that must be the same across all of them for the desugaring to work?

16. Your Mini interpreter's evaluator sequences statements: `eval_block` loops over a list of statements. Is this a monad? If you wanted to add early-exit (like `return` in the middle of a block), what would the "glue" between statements need to do? (Hint: this is exactly the `ReturnSignal` exception your Mini interpreter uses — describe it as a monad.)

---

# Part VI: Exercises

1. **State monad.** A `State(run)` wraps a function `s → (value, s)`. Implement `pure` and `bind` for State; implement `get` (returns the current state) and `put(s)` (sets the state). Use State to implement a counter: thread an integer state through three functions that each increment it by different amounts. Verify by running `program.execute(0)` and checking the final state.

2. **Parser monad.** A `Parser(run)` wraps `string → (value, rest)` or `None` on failure. Implement `pure` and `bind`; implement `char(c)` (matches a single character). Use Parser to parse the string `"abc"` character by character. This is how Parsec-style parser combinator libraries work under the hood.

3. **Fmap and Functor.** Before monad, there is **functor**: a container supporting `fmap(f)` that applies `f` inside the container without affecting the structure. Implement `fmap` for Maybe and List. Show that `m.fmap(f).fmap(g) == m.fmap(lambda x: g(f(x)))` (functor composition law).

4. **Writer monad.** A `Writer(value, log)` carries a value and an accumulated log (a list of strings). `bind` sequences computations and concatenates their logs. Implement Writer and use it to add logging to the safe arithmetic pipeline: each step logs what it computed. The final result carries the full computation trace.

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
