# Continuation-Passing Style: Control Flow as First-Class Values
<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://github.com/BillJr99/Ursinus-CS374-Fall2026/blob/gh-pages/_pages/Activities/liascript-cps.md or locally via https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374/gh-pages/_pages/Activities/liascript-cps.md

import: https://raw.githubusercontent.com/liascript/CodeRunner/master/README.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

# Continuation-Passing Style: Control Flow as First-Class Values

**Continuation-Passing Style** (CPS) transforms every function's implicit "what happens next" into an explicit first-class argument called a *continuation* — a function that receives the result and carries on. The payoff is startling: once control flow is a value, tail-call optimization, exceptions, `async`/`await`, generators, coroutines, and `call/cc` are all the same idea wearing different coats. The arc: **direct style → CPS → the CPS transform → exceptions → async/await → trampolining**.

---

## Directions and Group Roles

Work in your POGIL team with rotated roles (**Manager**, **Recorder**, **Presenter**, **Reflector**). Every code cell is executable in-browser; every reduction is traced by hand on the whiteboard. The Recorder captures continuations drawn as boxes-with-holes; the Presenter explains why async/await is secretly CPS. After class, respond to the reflective prompt individually in your notebook.

---

# Part I: Direct Style vs. CPS

## 1. What Is a Continuation?

In **direct style**, a function returns to its caller implicitly — the call stack encodes "what to do next." In **CPS**, that implicit stack frame becomes an explicit argument: a closure `k` called the **continuation**. Instead of returning a value, every function calls `k` with its result as the last thing it does.

Compare:

```python
# Direct style
def fact(n):
    if n == 0: return 1
    return n * fact(n - 1)

# CPS: k is "what to do with the result"
def fact_cps(n, k):
    if n == 0:
        k(1)           # base case: hand 1 to the continuation
    else:
        fact_cps(n - 1, lambda v: k(n * v))   # recursive call is the last thing we do
```

The **identity continuation** `lambda x: x` says "return x to the top level." Calling `fact_cps(5, lambda x: x)` computes `5!` and hands 120 back.

---

## Code Cell: Direct vs CPS Factorial

```python
try:
    # Direct style
    def fact(n):
        if n == 0: return 1
        return n * fact(n - 1)

    # CPS style
    def fact_cps(n, k):
        if n == 0:
            return k(1)
        else:
            return fact_cps(n - 1, lambda v: k(n * v))

    # The identity continuation: just return the answer
    identity = lambda x: x

    print("fact(5)        =", fact(5))
    print("fact_cps(5, I) =", fact_cps(5, identity))

    # A non-identity continuation: square the result
    print("fact_cps(5, sq)=", fact_cps(5, lambda x: x * x))

except Exception as e:
    print(f"[cps:direct] {e}")
    import traceback; traceback.print_exc()
```

---

## Model 1: Tracing a Continuation Chain

Each nested `lambda` in the CPS version is a stack frame made explicit. Trace `fact_cps(3, I)`:

```
fact_cps(3, I)
  fact_cps(2, λv: I(3*v))
    fact_cps(1, λv: (λv: I(3*v))(2*v))
      fact_cps(0, λv: (λv: (λv: I(3*v))(2*v))(1*v))
        k(1)   -- base case
```

The chain of lambdas IS the call stack, frozen in closures.

### Critical Thinking Questions

1. In the CPS `fact_cps`, which call is in tail position — `fact_cps(n-1, ...)` or `k(n * v)` or something else? Why does *every* call in a fully-CPS-transformed function end up in tail position?

2. What is the effect of calling `fact_cps(3, lambda x: print("result:", x))` compared to `fact_cps(3, lambda x: x)`? What does this reveal about the power of the continuation argument?

3. Trace `fact_cps(3, lambda x: x)` step by step as above. Write out each intermediate lambda (call it `k₀`, `k₁`, `k₂`) and show what value each `k` receives when called.

4. A tail call is a call whose value is immediately returned without further processing. In the CPS `fact_cps`, every call is a tail call. Why does this let a CPS interpreter replace the call stack with a single loop? (Hint: draw the stack depth as the trace above executes.)

---

# Part II: The CPS Transform

## 2. Mechanically Transforming to CPS

Any expression can be CPS-transformed by the following rules:

- **Literal / variable:** `x` → `λk. k(x)`
- **Application `f(a)`:** compute `f`, compute `a`, then call `f` with `a` and the current continuation: `λk. cps(f)(λfv. cps(a)(λav. fv(av, k)))`
- **If:** both branches call `k`

The key insight: **subexpressions are named** and their continuations are threaded inward. The expression tree turns inside-out: the deepest subexpression is computed first and its result flows outward.

**Example:** transform `add(mul(2, 3), 4)`:
```
Direct:  add(mul(2, 3), 4)

CPS step 1: name the arguments
  let t1 = mul(2, 3) in add(t1, 4)

CPS step 2: CPS each binding (innermost first)
  λk. mul_cps(2, 3, λt1.
        add_cps(t1, 4, k))
```

---

## Code Cell: CPS Fibonacci

```python
try:
    # Fibonacci in CPS — both recursive calls threaded through continuations
    def fib_cps(n, k):
        if n <= 1:
            return k(n)
        return fib_cps(n - 1, lambda a:
               fib_cps(n - 2, lambda b:
                   k(a + b)))

    # Print fib(0) through fib(10)
    results = []
    for i in range(11):
        fib_cps(i, lambda x: results.append(x))
    print("fib(0..10) =", results)

except Exception as e:
    print(f"[cps:fib] {e}")
    import traceback; traceback.print_exc()
```

---

## Model 2: The CPS Transform

[[MC]]
Which of the following is correct CPS form for the expression `add(mul(2, 3), 4)`, where arithmetic functions have been CPS-transformed to take an extra continuation `k`?
- ( ) `λk. add_cps(mul_cps(2, 3, k), 4, k)`
- (x) `λk. mul_cps(2, 3, λt. add_cps(t, 4, k))`
- ( ) `λk. k(add_cps(mul_cps(2, 3, identity), 4, identity))`
- ( ) `add_cps(2, mul_cps(3, 4, k), k)`

### Critical Thinking Questions

5. Show that in `fib_cps`, every call to `fib_cps` or `k` is in tail position. (There are no more operations after the call.) What does this imply about the call stack depth when the program runs?

6. CPS-transform the conditional `if a then b else c` by hand. Both branches must call `k`. Write the resulting lambda expression with `cps(a)`, `cps(b)`, `cps(c)` as placeholders.

7. After a full CPS transform, **all non-tail calls are gone** — every call is a tail call. Explain in one sentence why this is true by construction (what the CPS rules do to nested calls).

8. A naive Python CPS interpreter still risks stack overflow because Python does not optimize tail calls. Which language feature from your Scheme interpreter activity solves this without modifying Python's runtime?

---

# Part III: Exceptions as Two Continuations

## 3. Failure Continuations

The CPS representation of exceptions is immediate: give every function **two** continuations — a success continuation `k` and an escape continuation `h` (for handler). To throw an exception, ignore `k` and call `h`. To catch, provide a new `h`.

```python
# CPS division: two continuations
def div_cps(a, b, k, h):
    if b == 0:
        h("division by zero")   # escape: call the handler
    else:
        k(a / b)                # success: call normal continuation
```

A `try/except` block just installs a new handler `h` around the guarded code and restores the previous one on exit.

---

## Code Cell: Exceptions as Continuations

```python
try:
    def div_cps(a, b, k, h):
        if b == 0:
            return h(ZeroDivisionError("division by zero in CPS"))
        return k(a / b)

    def safe_compute_cps(x, y, k, h):
        return div_cps(x, y,
            lambda result: k(result * 2),   # success: double the quotient
            h)                               # propagate the handler

    # Success path
    safe_compute_cps(10, 2,
        lambda v: print("result:", v),
        lambda e: print("error:", e))

    # Error path — the escape continuation fires
    safe_compute_cps(10, 0,
        lambda v: print("result:", v),
        lambda e: print("caught:", e))

except Exception as e:
    print(f"[cps:except] {e}")
    import traceback; traceback.print_exc()
```

---

## Model 3: Escape Continuations

### Critical Thinking Questions

9. When `safe_compute_cps(10, 0, k, h)` is called, draw the call graph. At what point does the control flow jump directly to `h` without executing the `lambda result: k(result * 2)` closure?

10. In a deep chain of CPS functions `f → g → h → ... → div_cps`, the handler `h` is threaded through every call. When an error is thrown, "jumping over" intermediate frames means ignoring their `k`s. In what way is this exactly what Python's `raise` does physically on the call stack? In what way is the CPS version cleaner?

11. Describe how to implement a `finally` clause: code that runs whether the result is a success or an error. You have two continuations to work with. Write pseudo-CPS for:
    ```python
    try:
        result = risky_op()
    finally:
        cleanup()
    return result
    ```

---

# Part IV: Async/Await as CPS in Disguise

## 4. Callbacks, Promises, and the Continuation in Plain Sight

Every callback-based API is CPS by another name. `fs.readFile(path, callback)` is `readFile_cps(path, k)` — the callback IS the continuation. The famous "callback hell" is CPS written by hand without discipline.

```javascript
// Callback hell (CPS by hand, not by design)
readFile(path1, function(a) {
  readFile(path2, function(b) {
    readFile(path3, function(c) {
      process(a, b, c);
    });
  });
});
```

**Promises** give the continuation a name: `.then(k)`. **Async/await** hides the continuation entirely: `let x = await expr` desugars to `expr_cps(λx. rest_of_function)`. The `async` keyword marks "this function may pass its remainder as a continuation to something else."

Python's **generator** is a semi-continuation: `yield value` suspends the function and hands `value` to the caller, then resumes where it left off when the caller calls `next()`. The resumption point is a saved continuation.

---

## Code Cell: Simulated Async Event Loop

```python
try:
    from collections import deque

    # A toy event loop: a queue of (callback, value) pairs
    _queue = deque()

    def schedule(callback, value=None):
        _queue.append((callback, value))

    def run_loop():
        while _queue:
            callback, value = _queue.popleft()
            callback(value)

    # "Async" read: simulates non-blocking I/O by scheduling a callback
    def async_read(data, k):
        schedule(k, data)   # hand the data to the continuation later

    def async_process(path1, path2, k):
        async_read(f"contents_of_{path1}", lambda a:
            async_read(f"contents_of_{path2}", lambda b:
                k(f"combined: {a} + {b}")))

    # Start the computation — control returns immediately
    async_process("fileA", "fileB", lambda result: print(result))

    # The event loop drives it forward
    run_loop()

except Exception as e:
    print(f"[cps:async] {e}")
    import traceback; traceback.print_exc()
```

---

## Model 4: Async as CPS

### Critical Thinking Questions

12. In `async_process`, the two `lambda` closures ARE continuations. When `async_read(path1, λa. ...)` is called, `λa` is not called immediately — it is scheduled. What Python feature does `await` correspond to in the hand-coded version above?

13. Python generators use `yield` to suspend. A generator object's `__next__()` call resumes the generator. In one sentence: what is the "continuation" that `yield` captures?

14. JavaScript's `async`/`await` transforms callback-style code into code that *looks* sequential. What does this tell you about the relationship between CPS and imperative programming?

---

# Part V: Trampolining

## 5. The Stack Overflow Problem and Its Solution

Even though CPS puts every call in tail position, Python and JavaScript do not eliminate tail calls — each `k(result)` still adds a stack frame. Deep CPS chains overflow.

**Trampolining** escapes this: instead of calling `k(result)` directly, return a **Thunk** — a zero-argument closure that defers the call. A top-level loop (the trampoline) unboxes Thunks until the computation is done.

```
trampoline(thunk):
  while thunk is a Thunk:
    thunk = thunk()   # one step, O(1) stack
  return thunk        # final value
```

The stack never grows: each "call" is really just the loop advancing by one thunk.

---

## Code Cell: Trampolined CPS Factorial

```python
try:
    class Thunk:
        def __init__(self, fn):
            self.fn = fn
        def __call__(self):
            return self.fn()

    def trampoline(thunk):
        result = thunk
        while isinstance(result, Thunk):
            result = result()
        return result

    def fact_tramp(n, k):
        if n == 0:
            return k(1)
        return Thunk(lambda n=n, k=k:
            fact_tramp(n - 1, lambda v, n=n, k=k: k(n * v)))

    # Works for large n without stack overflow
    result = trampoline(fact_tramp(10, lambda x: x))
    print("10! =", result)

    # This would stack-overflow direct CPS at ~1000; trampolining handles it
    result = trampoline(fact_tramp(500, lambda x: x))
    print("500! ends in ...%d" % (result % 10**6))

except Exception as e:
    print(f"[cps:trampoline] {e}")
    import traceback; traceback.print_exc()
```

---

## Model 5: Why Trampolining Works

### Critical Thinking Questions

15. `fact_tramp` never calls `fact_tramp` recursively — it returns a `Thunk`. The `trampoline` loop is the only thing that calls thunks. Why does this mean the Python call stack never grows deeper than `trampoline → fact_tramp` (two frames)?

16. The trampoline loop runs in O(n) time and O(1) *stack* space for a depth-n computation. Explain the difference between stack space and heap space in this context. Where do the intermediate closures `lambda v: k(n * v)` live?

17. Connect trampolining to the Scheme evaluator from the Scheme Interpreter activity: the `trampoline` loop there was also used to implement tail-call optimization. Both achieve the same result (no stack growth on tail calls) via different mechanisms. In one sentence each: how does Scheme's TCO work, and how does trampolining work, and what is their common "shape"?

---

# Part VI: Exercises

1. **CPS `map`**. Write `map_cps(f_cps, lst, k)` that applies `f_cps` (a CPS function) to each element of `lst` and calls `k(result_list)` with the mapped list. Every call must be in tail position. Test with `f_cps = lambda x, k: k(x * 2)`.

2. **CPS expression interpreter**. Write `eval_cps(node, env, k)` for a tiny AST with `Num(v)`, `Add(left, right)`, and `Let(name, val, body)`. Each case calls `k` with the value; `Let` extends the environment before evaluating `body`. Compare the structure with your Mini interpreter's `eval_expr` — which logic belongs in the CPS continuation and which in the semantic action?

3. **`call/cc` (call-with-current-continuation)**. `callcc(f)` captures the current continuation `k` and passes it to `f`; calling that saved `k` anywhere (even later) returns its argument to the point where `callcc` was called. Implement a toy `callcc` in Python using a class that stores `k` and raises a special exception to "jump back":
   ```python
   class Escape(Exception):
       def __init__(self, value): self.value = value

   def callcc(f, k):
       saved_k = lambda v: (_ for _ in ()).throw(Escape(v))
       try:
           return f(saved_k, k)
       except Escape as e:
           return k(e.value)
   ```
   Demonstrate early exit from a loop using `callcc`.

4. **Async generator**. Python's `async for` iterates over an async generator. Explain how each `yield` in an async generator is a CPS step: the generator body up to `yield` is the current computation, and the `yield` value is passed to a continuation (the `async for` loop body). Write a manual simulation using closures and the toy event loop from Model 4.

---

## Reflection Prompt

In your notebook: every control flow structure you use daily — function calls, exceptions, `async`/`await`, generators, loops via recursion — has a CPS explanation. Does this make them feel like fundamentally the same thing, or fundamentally different things sharing a costume? What does your answer reveal about what a programming language *is* — a collection of features, or one idea expressed many ways? Connect to the lambda calculus week: if functions are the only primitive, is a continuation just a function?

---

## Further Reading

- Appel, Andrew W. *Compiling with Continuations* (Cambridge, 1992). The standard reference for CPS as a compiler IR; GCC, MLton, and Chicken Scheme all use CPS internally.
- Scheme R7RS, section 6.10: `call-with-current-continuation` — the formal specification.
- Felleisen, Matthias. "On the Expressive Power of Programming Languages" (1991). Proves that CPS is strictly more expressive than any language without first-class control operators.
- Python PEP 342 (generators as coroutines) and PEP 3156 (asyncio) — how CPython implements these features and their relationship to CPS.
- Dan Piponi. "The Mother of All Monads" (blog, A Neighborhood of Infinity). The continuation monad contains every other monad; read after the Monads activity.
- Danvy, Olivier and Andrzej Filinski. "Representing Control: A Study of the CPS Transformation" (1992). The definitive paper on the CPS transform algorithm used in Part II.
