<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374-Fall2026/gh-pages/_pages/Activities/liascript-lazy-evaluation.md

import: https://raw.githubusercontent.com/liascript/CodeRunner/master/README.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-CS374-Fall2026@gh-pages/assets/css/main.css
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

# Lazy Evaluation and Infinite Structures

Most programs you have written evaluate every expression the moment they encounter it. Add two numbers? The addition happens immediately. Build a list? Every element is computed before the list is returned. This strategy — called **eager evaluation** or **strict evaluation** — is the default in Python, Java, C, and most mainstream languages. It is easy to reason about: expressions have values, values are computed in order, and nothing is deferred.

But eager evaluation has a structural weakness. It forces you to know, before you start computing, how much you will need. You cannot ask for "the first five primes" without either pre-specifying a search limit or building a general-purpose lazy abstraction yourself. The moment your data source is conceptually infinite — the sequence of all primes, all Fibonacci numbers, all natural numbers — strict evaluation runs into a wall.

**Lazy evaluation** (also called **non-strict evaluation** or **call-by-need**) turns this on its head: values are computed only when they are actually needed, and the results are cached so that the same computation is never repeated. Haskell is lazy by default. Python and most other languages provide lazy tools as explicit abstractions — generators, iterators, and the patterns in this activity. Understanding how laziness is implemented — as **thunks**, **streams**, and **memoized closures** — illuminates both functional language design and practical Python patterns.

Arc: **the eager/lazy distinction → thunks as the primitive mechanism → streams as the data structure → the Sieve of Eratosthenes → calling conventions across languages**

---

## Directions and Group Roles

Work in your POGIL team with rotated roles (**Manager**, **Recorder**, **Presenter**, **Reflector**). Consider each model individually first — run the code, observe the output, read the prose — then discuss the Critical Thinking Questions with your group before moving on.

---

# Part I: The Problem Laziness Solves

## Model 1 — The Problem: Computing Without Knowing the End

The simplest statement of the problem: eager computation forces you to materialize the full sequence before you can work with it. If you want the first five primes, you need to supply a limit before you know where to stop. If the limit is too small, you miss answers; if it is too large, you waste work.

```python  liascript
# Eager: must generate ALL primes up to a limit
def primes_up_to(limit):
    result = []
    for n in range(2, limit + 1):
        if all(n % p != 0 for p in result):
            result.append(n)
    return result

# Problem: what if we want "the first 5 primes" without knowing the limit?
# primes_up_to(???)  # We don't know where to stop!

# Eager version requires over-approximating the limit
first_5_via_limit = primes_up_to(15)[:5]
print("First 5 primes (limit=15):", first_5_via_limit)

# What if the limit is too small?
too_small = primes_up_to(3)[:5]
print("First 5 primes (limit=3, too small):", too_small)  # Only 2 primes!

# What if we want the 1000th prime? We'd need a much larger limit.
# The eager approach couples "how many" to "up to where" — unnecessarily.

# What we WANT: generate primes on demand, stop when we have enough.
print("\nWhat we want:")
print("  - An infinite sequence of primes")
print("  - Take only as many as we need")
print("  - Never compute beyond what we asked for")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

This tension appears everywhere in computing: network packets arrive in a stream you cannot bound ahead of time; log files grow without a fixed length; a game's state space is conceptually infinite. The eager model forces an artificial ceiling onto every such problem. A lazy model lets you describe an infinite process and consume only as much as you need.

**Critical Thinking Questions (CTQs)**

> **CTQ 1.1** Run the code with `too_small = primes_up_to(3)[:5]`. The limit 3 yields fewer than 5 primes, so the slice silently returns a shorter list. How would you detect this error if you were calling `primes_up_to` from another module and did not know the true limit?

> **CTQ 1.2** `primes_up_to(15)[:5]` computes 6 primes (2, 3, 5, 7, 11, 13) before slicing down to 5. Roughly how much extra work does this represent? For the first 100 primes, the 100th prime is 541 — how many primes up to 541 would you compute unnecessarily?

> **CTQ 1.3** The phrase "on demand" means: produce the next value only when the consumer asks for it. Name two Python built-in features you already know that work this way (hint: what does `range(10**9)` return? What does `open(file)` return?).

---

# Part II: Thunks — The Primitive Mechanism

## Model 2 — Thunks: Wrapping Computation in a Function

The simplest way to defer computation: wrap it in a zero-argument function. In Haskell, the runtime does this automatically for every expression. In Python, we do it explicitly. A **thunk** is a zero-argument callable that, when called (**forced**), evaluates to the deferred value. The name comes from ALGOL compiler folklore — it described the "thunk" sound of a value landing on the stack after being computed.

Thunks are not exotic: every Python `lambda: expr` is a thunk if it takes no arguments. The key operations are `thunk(f) = f` (no-op: the lambda *is* the thunk) and `force(t) = t()` (call it to get the value). The power lies in what you can build on top.

```python  liascript
# A "thunk" is a zero-argument function that wraps a deferred computation.
def force(t):
    return t()   # evaluate the thunk by calling it

# Examples
x = lambda: 2 + 3         # not computed yet — just a closure over the expression
print("Thunk created, nothing computed yet.")
print("Forced value:", force(x))              # NOW computed: 5

# Lazy "if": only evaluate the branch we actually take
def lazy_if(cond, then_thunk, else_thunk):
    if cond:
        return force(then_thunk)
    else:
        return force(else_thunk)

# The else branch is 1/0 — would crash if evaluated eagerly
result = lazy_if(
    True,
    lambda: 42,
    lambda: 1 / 0     # never forced — no ZeroDivisionError
)
print("lazy_if result:", result)

# Regular Python 'if' is also lazy in this sense:
# The branch not taken is never evaluated.
# But function arguments are NOT lazy by default:
def eager_if(cond, then_val, else_val):
    return then_val if cond else else_val

# This WILL crash — both arguments evaluated before the call
try:
    bad = eager_if(True, 42, 1 / 0)
except ZeroDivisionError as e:
    print("eager_if crashed:", e)

# Thunks prevent the crash:
good = lazy_if(True, lambda: 42, lambda: 1 / 0)
print("lazy_if with bad branch:", good)
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

The contrast between `eager_if` and `lazy_if` reveals something profound about function calls: in a language where arguments are evaluated before the call (**by-value** or **applicative-order** evaluation), you cannot define a true conditional as a library function. The built-in `if` statement in Python, Java, and C is wired into the language precisely because argument evaluation is eager. In a lazy language like Haskell, you *can* define `myIf` as an ordinary function, because arguments are only evaluated when forced.

> **CTQ 2.1** What is the output of `force(lambda: force(lambda: force(lambda: 99)))`? How many times is `force` called? What does this tell you about the relationship between thunks and nesting?

> **CTQ 2.2** The `eager_if` function crashes even though `cond` is `True` and the result would be `42`. Explain the order of operations that causes the crash. At what exact point in the Python execution does `1/0` execute?

> **CTQ 2.3** Python's `and` and `or` are lazy (short-circuit). Write a one-line expression using `and` that safely accesses `obj.method()` only when `obj` is not `None`. How is this analogous to `lazy_if`?

> **CTQ 2.4** Suppose you wanted a `lazy_and(a_thunk, b_thunk)` function. Write it. Now argue: could you implement `lazy_and` correctly using `eager_and(a, b)`? Why or why not?

---

# Part III: Streams — Lazy Infinite Sequences

## Model 3 — Streams: Lazy Infinite Sequences

A thunk defers a single value. A **stream** uses thunks recursively to defer an entire infinite sequence. The idea is simple: a stream is a pair of a **head** (the current value, already computed) and a **tail** (a thunk that, when forced, produces the next stream). The tail is not forced until you ask for it, so the infinite sequence is never materialized all at once.

The key refinement is **memoization**: once the tail thunk has been forced, store the result so it is never recomputed. Without memoization, accessing `stream.tail.tail.tail` would re-evaluate the tail thunk three times. With memoization, each step is computed exactly once. This combination — lazy evaluation plus memoization — is called **call-by-need**, and it is what Haskell's runtime implements automatically.

```python  liascript
class Stream:
    def __init__(self, head, tail_thunk):
        self.head = head
        self._tail_thunk = tail_thunk
        self._tail = None          # None means "not yet computed"
        self._forced = False       # distinguish "not forced" from "forced to None"

    @property
    def tail(self):
        if not self._forced:
            self._tail = self._tail_thunk()   # force the thunk exactly once
            self._forced = True
        return self._tail                     # return memoized result

def stream_take(s, n):
    """Return the first n elements of stream s as a list."""
    result = []
    while n > 0 and s is not None:
        result.append(s.head)
        s = s.tail
        n -= 1
    return result

# Infinite stream of natural numbers starting at n
def count_from(n):
    return Stream(n, lambda: count_from(n + 1))

# Infinite stream of ones — self-referential!
ones = Stream(1, lambda: ones)

naturals = count_from(0)
print("First 10 naturals:", stream_take(naturals, 10))
print("First 5 ones:     ", stream_take(ones, 5))

# Map and filter over streams — they return new (lazy) streams
def stream_map(f, s):
    if s is None: return None
    return Stream(f(s.head), lambda: stream_map(f, s.tail))

def stream_filter(pred, s):
    if s is None: return None
    if pred(s.head):
        return Stream(s.head, lambda: stream_filter(pred, s.tail))
    return stream_filter(pred, s.tail)

evens   = stream_filter(lambda x: x % 2 == 0, count_from(0))
squares = stream_map(lambda x: x * x, count_from(1))

print("First 5 evens:   ", stream_take(evens, 5))
print("First 5 squares: ", stream_take(squares, 5))
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

Notice that `stream_map` and `stream_filter` return new streams immediately, without computing any elements. The lambda `lambda: stream_map(f, s.tail)` captures `f` and `s` in a closure; the actual recursive call happens only when `.tail` is accessed. Every stream operation is therefore O(1) in the number of elements consumed — no upfront work, no allocation beyond what you use.

> **CTQ 3.1** In `Stream.__init__`, why is `self._forced` necessary? Could you just check `self._tail is None` instead? Construct a case where a stream's tail legitimately produces `None` to justify the separate flag.

> **CTQ 3.2** The `ones` stream is defined as `ones = Stream(1, lambda: ones)`. Draw the structure in memory after `stream_take(ones, 3)` has been called. How many `Stream` objects exist? Which ones have been memoized?

> **CTQ 3.3** The `stream_filter` function calls itself recursively (not via a thunk) when the current head fails the predicate. What does this mean for filtering a stream where many consecutive elements fail? How might you fix it?

> **CTQ 3.4** Write `stream_zip(s1, s2)` that pairs corresponding elements from two streams, producing a stream of tuples `(s1.head, s2.head)`, `(s1.tail.head, s2.tail.head)`, etc. What is the type of the result?

---

# Part IV: The Sieve of Eratosthenes as a Stream

## Model 4 — The Sieve of Eratosthenes as a Stream

The Sieve of Eratosthenes is one of the oldest algorithms in mathematics: to find all primes, start with the integers from 2 upward, take the first element (it must be prime), remove all its multiples, and repeat on the remainder. In an eager language, you run the sieve over a bounded array. In a lazy language, the sieve can operate over an *infinite* stream of integers — the sieve never "finishes," but you can consume as many primes as you want.

The elegance of the lazy sieve is structural: `sieve(s)` is defined as "the first element of `s` (which is prime), followed by `sieve(filter out multiples of that element from the rest of s)`. This recursive definition describes an infinite process, but the thunk in the tail of each returned stream ensures that each step is deferred until the consumer asks for the next prime.

```python  liascript
class Stream:
    def __init__(self, head, tail_thunk):
        self.head = head
        self._tail_thunk = tail_thunk
        self._tail = None
        self._forced = False
    @property
    def tail(self):
        if not self._forced:
            self._tail = self._tail_thunk()
            self._forced = True
        return self._tail

def count_from(n):
    return Stream(n, lambda: count_from(n + 1))

def stream_filter(pred, s):
    if pred(s.head):
        return Stream(s.head, lambda: stream_filter(pred, s.tail))
    return stream_filter(pred, s.tail)

def stream_take(s, n):
    result = []
    while n > 0:
        result.append(s.head)
        s = s.tail
        n -= 1
    return result

def stream_nth(s, n):
    """Return the (0-indexed) nth element of stream s."""
    while n > 0:
        s = s.tail
        n -= 1
    return s.head

def sieve(s):
    p = s.head   # p is definitely prime: nothing smaller divided it
    return Stream(p, lambda: sieve(stream_filter(lambda x: x % p != 0, s.tail)))

primes = sieve(count_from(2))

print("First 10 primes:", stream_take(primes, 10))
print("First 20 primes:", stream_take(primes, 20))
print("100th prime:    ", stream_nth(primes, 99))
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

The `lambda: sieve(...)` in the tail of each returned stream is essential: without it, `sieve` would call itself immediately, which would call `sieve` again immediately, and so on — infinite recursion before a single prime is produced. The thunk inserts a suspension point: `sieve(s.tail_after_filtering)` is only called when someone accesses `.tail`, which only happens when the next prime is needed.

Memoization in `.tail` also matters here: every time `stream_take(primes, 10)` accesses `primes.tail`, it gets back the same memoized stream object rather than re-running the filter and sieve. Without memoization, consuming the 100th prime would re-evaluate every filter and sieve step at every level — exponential work instead of linear.

> **CTQ 4.1** Trace the first three steps of `sieve(count_from(2))` by hand. After accessing `.head`, what is the exact thunk stored in `.tail`? After forcing `.tail` once, what is the head of the resulting stream, and what is stored in its `.tail`?

> **CTQ 4.2** The `lambda: sieve(...)` in `sieve`'s return statement captures `p` by closure. Why is it critical that `p = s.head` is bound as a local variable before the `lambda` is created? What would go wrong if you wrote `lambda: sieve(stream_filter(lambda x: x % s.head != 0, s.tail))` instead?

> **CTQ 4.3** Each new prime `p` adds one more `stream_filter` layer to the chain. When you ask for the 1000th prime, the stream for the 999th filter must be traversed to produce the 1000th. How does memoization prevent this from being O(n²) total work?

> **CTQ 4.4** This sieve is sometimes called the "unfaithful sieve" because it is not quite as efficient as the true Sieve of Eratosthenes. In the true sieve, multiples of 2 are crossed out starting from 4, not tested for every odd number. In this stream version, `x % 2 != 0` is tested for every element in the stream. Can you think of a way to make the filter for prime `p` start at `p*p` rather than `p+1`?

---

# Part V: By-Value vs. By-Name — Language Design

## Model 5 — By-Value vs. By-Name: Call Strategies in Language Design

Every language makes a fundamental decision at each function call: when do you evaluate the arguments? The two classic answers are:

- **Call-by-value** (eager, applicative-order): evaluate all arguments before entering the function body. Python, Java, C, Ruby, and almost every mainstream language use this.
- **Call-by-name** (lazy, normal-order): pass the argument as an unevaluated expression; evaluate it (from scratch) each time it is referenced in the body.
- **Call-by-need** (lazy + memoized): like call-by-name, but cache the result the first time it is forced. This is Haskell's strategy.

R uses **call-by-promise**: arguments are wrapped in promise objects that record whether they have been evaluated yet, which enables `missing()` and lazy default arguments that refer to other parameters.

The performance trade-offs are not obvious. Call-by-name can skip work entirely for unused arguments. But if an argument is used *multiple times*, call-by-name re-evaluates it each time — potentially far more expensive than call-by-value. Call-by-need gets the best of both worlds: skip unused arguments, evaluate used arguments exactly once.

```python  liascript
import time

# --- Simulated call-by-value (eager): argument evaluated before the call ---
def unused_arg_eager(x, y):
    return x   # y is computed but never used

t0 = time.perf_counter()
result_eager = unused_arg_eager(42, sum(range(10**6)))   # sum IS computed
t1 = time.perf_counter()
print(f"By-value:  result={result_eager}, time={t1 - t0:.4f}s  (sum computed even though unused)")

# --- Simulated call-by-name (lazy): argument wrapped in a thunk ---
def unused_arg_lazy(x, y_thunk):
    return x   # y_thunk is NEVER forced

def slow_sum():
    return sum(range(10**6))

t0 = time.perf_counter()
result_lazy = unused_arg_lazy(42, slow_sum)   # slow_sum is never called
t1 = time.perf_counter()
print(f"By-name:   result={result_lazy}, time={t1 - t0:.6f}s  (sum skipped entirely)")

# --- Python's short-circuit operators ARE lazy ---
print("\nPython short-circuit laziness:")
print("False and (1/0):", False and (1 / 0))   # 1/0 never evaluated
print("True  or  (1/0):", True  or  (1 / 0))   # 1/0 never evaluated

# --- When is by-value faster? When argument is used multiple times ---
def sum_twice_eager(n, total):
    # total already computed; we use it twice for free
    return total + total

def sum_twice_lazy(n, total_thunk):
    # call-by-name: total_thunk() called TWICE — computes sum twice!
    return total_thunk() + total_thunk()

val = 1000
t0 = time.perf_counter()
_ = sum_twice_eager(val, sum(range(val)))
t1 = time.perf_counter()
print(f"\nsum_twice eager:  {t1 - t0:.6f}s")

t0 = time.perf_counter()
_ = sum_twice_lazy(val, lambda: sum(range(val)))
t1 = time.perf_counter()
print(f"sum_twice lazy:   {t1 - t0:.6f}s  (sum computed twice!)")
print("(call-by-need would memoize the first call and match eager speed)")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

The timing output makes the trade-off concrete. By-name wins when the argument is unused; by-value wins (over naive by-name) when the argument is used multiple times. Call-by-need — the combination of by-name with memoization — dominates both: it skips unused arguments and computes used arguments exactly once. The `Stream` class from Models 3 and 4 implements call-by-need manually in Python: the `.tail` property is a by-name access, and the `_forced` flag is the memoization.

> **CTQ 5.1** The by-value run shows a measurable time cost even though `y` is unused. Precisely when during the function call does Python evaluate `sum(range(10**6))`? At what point in the call stack does control return to `unused_arg_eager`?

> **CTQ 5.2** The `sum_twice_lazy` example calls `total_thunk()` twice. Under call-by-need, the second call would return the memoized result instantly. Sketch a `memoize_thunk(f)` wrapper that converts a zero-argument function into a call-by-need thunk: the first call evaluates and caches; subsequent calls return the cache.

> **CTQ 5.3** Python's `and`/`or` are lazy, but Python's function calls are eager. Is there any built-in Python function (not operator) that is lazy in its arguments? Think about `all()`, `any()`, `map()`, `filter()`. Which of these produce results lazily, and which evaluate all arguments eagerly?

> **CTQ 5.4** R passes function arguments as *promises* — unevaluated expressions that are forced on first access and then cached. A default argument in R can refer to another parameter: `function(x, y = x * 2)`. Why is this impossible in Python's by-value model, and how does R's call-by-promise make it work?

---

## Multiple Choice

[[MC]]
A thunk is `lambda: expr`. When does `expr` get evaluated?

    [( )] When the thunk is created
    [(X)] When the thunk is called (forced)
    [( )] Never, unless explicitly unboxed
    [( )] When the program exits

---

[[MC]]
The `Stream` class stores `self._tail` after the tail thunk is first forced. What is the purpose of this?

    [(X)] Avoid recomputing the tail on every access (memoization)
    [( )] Force evaluation of the tail earlier
    [( )] Allow mutation of the stream after construction
    [( )] Prevent infinite recursion in the constructor

---

[[MC]]
In call-by-name evaluation, what happens to an argument expression each time the parameter is referenced in the function body?

    [( )] It is evaluated once before the call and cached
    [(X)] It is re-evaluated from scratch each time the parameter is used
    [( )] It is evaluated at program start and stored globally
    [( )] It is never evaluated unless the programmer calls `force()`

---

[[MC]]
Python's `and` operator is lazy (short-circuit). Which of the following patterns exploits this to write safe, idiomatic Python?

    [( )] `print(x and y)` always prints both `x` and `y`
    [(X)] `obj and obj.method()` avoids calling `.method()` on `None`
    [( )] `x and y` always returns `True` or `False`
    [( )] `not x and y` is always equivalent to `not (x and y)`

---

## Exercises

### Exercise 1 — Stream Zip and Interleave (20 min)

Write `stream_zip(s1, s2)` that pairs corresponding elements from two streams, producing a stream of 2-tuples: `(s1[0], s2[0])`, `(s1[1], s2[1])`, and so on. Verify with `stream_take(stream_zip(count_from(0), count_from(10)), 5)` — you should see `[(0,10),(1,11),(2,12),(3,13),(4,14)]`.

Then write `stream_interleave(s1, s2)` that alternates elements: `s1[0]`, `s2[0]`, `s1[1]`, `s2[1]`, .... Verify by interleaving even numbers and odd numbers to recover the naturals.

### Exercise 2 — Fibonacci as a Stream (20 min)

Implement the Fibonacci sequence as a `Stream` without any loops or index variables. One elegant approach: define `fibs` in terms of `stream_zip` and `stream_map` over `fibs` itself. Another approach: define a helper `fib_from(a, b)` that returns `Stream(a, lambda: fib_from(b, a+b))`. Verify that the first 10 terms are `[0, 1, 1, 2, 3, 5, 8, 13, 21, 34]`.

### Exercise 3 — Memoize Decorator (25 min)

Write a `memoize(f)` decorator that caches the results of `f` by its arguments. Demonstrate that naive recursive Fibonacci is O(2^n) and that `memoize(fib)` (where `fib` calls the memoized version recursively) is O(n). Measure timing for `fib(30)` with and without memoization. Then connect back to streams: explain how the `_forced` flag in `Stream.tail` is memoization of a zero-argument function, making it a special case of your `memoize` decorator.

### Exercise 4 — Lazy Pipeline (30 min)

Build a lazy pipeline for processing a "stream" of integers. Implement:
- `stream_drop(s, n)`: skip the first `n` elements
- `stream_scan(f, init, s)`: running cumulative reduce (like `itertools.accumulate`)
- `stream_until(pred, s)`: take elements while the predicate holds, then stop

Using these, compute the running sum of primes until the running sum exceeds 1000, returning both the running sum and the prime that pushed it over the threshold.

---

## Reflection

**On laziness and modularity:** John Hughes's 1989 paper "Why Functional Programming Matters" argues that laziness is not just an efficiency trick — it is a *modularity* tool. It lets you separate the producer of data from the consumer of data: the producer generates infinitely; the consumer takes finitely. The producer does not need to know the consumer's stopping condition; the consumer does not need to know the producer's generation strategy. Reflect: in what other parts of software design does separation of producer and consumer improve modularity? (Think about HTTP streaming, Unix pipes, event listeners.)

**On Python generators:** Python's `yield` keyword creates generators, which are a form of laziness built into the language. Compare the `Stream` class from Model 3 to a generator function that `yield`s the same sequence. What does the generator provide that the `Stream` class does not? What does the `Stream` class provide that a generator does not? (Hint: consider re-traversal — can you go back and re-read an element of a generator after you have advanced past it?)

**On Haskell's trade-offs:** Haskell is lazy by default, which enables all the patterns in this activity without explicit thunks. But laziness is not free: every expression must be wrapped in a "thunk box" in memory, and the garbage collector must track which thunks have been forced. Haskell programmers sometimes encounter *space leaks* where unevaluated thunks accumulate faster than they are forced, exhausting memory. With eager evaluation, the memory profile of a program is predictable from its data structures. With lazy evaluation, space usage depends on evaluation order, which can be surprising. Is the expressiveness of laziness worth this trade-off? What kinds of programs benefit most from laziness?

---

## Further Reading

- **"Why Functional Programming Matters"** — John Hughes (1989): the foundational argument that laziness enables modularity; freely available online. The section on lazy lists is directly relevant to this activity.
- **SRFI-41: Streams** — Philip Bewig's Scheme implementation of lazy streams, with a thorough discussion of eager vs. lazy stream variants and the memoization requirement.
- **Haskell's Lazy I/O and its pitfalls** — search "Haskell lazy IO problems" for discussions of `hGetContents` and why mixing laziness with side effects requires care.
- **Python `itertools` documentation** — the standard library's lazy iterator tools: `itertools.count`, `itertools.takewhile`, `itertools.islice`. These are Python's production-quality equivalents of the stream operations in this activity.
- **"The Art of the Interpreter"** — Guy Steele and Gerald Sussman (1978, MIT AI Memo 452): the paper that distinguished call-by-value, call-by-name, and call-by-need formally, and showed how to implement each in a meta-circular interpreter.
- **R's promise mechanism** — search "R lazy evaluation promises" for documentation on how R implements call-by-promise and why default arguments can refer to other parameters.
