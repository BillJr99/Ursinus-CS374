<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://github.com/BillJr99/Ursinus-CS374-Fall2026/blob/gh-pages/_pages/Activities/liascript-cps.md or locally via https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374-Fall2026/gh-pages/_pages/Activities/liascript-cps.md

import: https://raw.githubusercontent.com/liascript/CodeRunner/master/README.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

# Continuation-Passing Style: Control Flow as First-Class Values

## Learning Goals

By the end of this activity, you will be able to:

- Mechanically transform a direct-style function into continuation-passing style (CPS), making every return explicit as a call to a continuation `k`
- Explain why CPS converts every call into a tail call and why tail calls do not grow the stack
- Implement a trampoline that executes a CPS computation in O(1) stack space using an iterative loop
- Identify the continuation at each point in a computation and describe what "the rest of the program" means at that point
- Recognize CPS as the common underlying mechanism behind tail-call optimization, exceptions, generators, async/await, and `call/cc`

Continuation-Passing Style (CPS) transforms "what to do next" into an explicit first-class value called a **continuation** — a function representing the rest of the computation. Every function in CPS takes an extra argument `k` — the continuation — and instead of returning a value to its caller, it calls `k` with that result directly. This single idea unifies tail-call optimization, exceptions, async/await, generators, coroutines, and `call/cc` under one conceptual roof, revealing that these features, which appear very different on the surface, are all variations of the same underlying mechanism: the explicit manipulation of control flow as data.

---

> **Before You Begin — Prerequisites**
>
> This activity assumes you are comfortable with **closures** (functions that capture variables from their enclosing scope) and **higher-order functions** (functions that accept or return other functions). If either of those concepts feels shaky, review the [Closures activity](../closures/) before continuing. In CPS, nearly every step involves passing a function as an argument and calling it inside another function — closures are not optional background material here, they are the core mechanism.

---

## Why This Matters: The Stack Overflow Problem

Python's call stack has a limit of roughly 1,000 frames by default. That limit exists because the interpreter stores each active function call on a fixed-size stack in memory. Try summing a list of 10,000 elements with naive recursion and Python will stop you:

```python  liascript
import sys, traceback

def sum_list(lst):
    if len(lst) == 0:
        return 0
    return lst[0] + sum_list(lst[1:])   # non-tail call: pending addition after return

# Try with a small list first (works fine)
print("sum_list([1,2,3,4,5]) =", sum_list([1, 2, 3, 4, 5]))

# Now try 2000 elements — likely hits the recursion limit
try:
    result = sum_list(list(range(2000)))
    print("sum_list(range(2000)) =", result, "(succeeded — your limit is higher than default)")
except RecursionError as e:
    print("RecursionError with 2000 elements:", e)
    print("(Python's default recursion limit is", sys.getrecursionlimit(), "frames)")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

The problem is not the recursion itself — it is the **pending work** that accumulates on the stack. Each call to `sum_list` cannot return until its recursive call returns, because the addition `lst[0] + (...)` is still waiting. Python keeps every one of those frames alive simultaneously.

CPS transforms this so that every call becomes a **tail call** — no pending work remains on the stack after the call. Once every call is a tail call, a technique called **trampolining** can run the computation inside a simple `while` loop, using O(1) stack space regardless of list size. You will build all of this from scratch in this activity.

---

## Notation Bridge: Direct Style to CPS

Before diving in, here is a quick translation table. The left column shows familiar direct-style code; the right column shows its CPS equivalent. The key pattern is: wherever direct style *returns* a value, CPS *calls the continuation* `k` with that value instead.

| Direct Style | CPS Style | What changed |
|---|---|---|
| `return x` | `k(x)` | "return" becomes "call `k` with" |
| `f(x)` | `f_k(x, k)` | every function gains an extra `k` argument |
| `y = f(x); g(y)` | `f_k(x, lambda y: g_k(y, k))` | sequencing becomes nested lambdas |
| `if b: e1 else: e2` | `(lambda: k(e1))() if b else (lambda: k(e2))()` | both branches call `k` |
| `return f(g(x))` | `g_k(x, lambda v: f_k(v, k))` | inner call names its result, outer call uses it |

The notation `f_k` is a naming convention meaning "CPS version of `f`." Some authors write `f_cps` instead. Both mean the same thing: a version of `f` that takes an extra continuation argument and calls it with the result instead of returning.

---

## Step-by-Step CPS Transformation of Factorial

Here is how to mechanically transform `factorial` from direct style to CPS. Read through each step before running any code — the goal is to understand the algorithm before you see it execute.

**Original direct style:**

```
def factorial(n):
    if n == 0:
        return 1           # base case: returns 1
    else:
        return n * factorial(n - 1)   # non-tail: pending multiplication
```

**Step 1 — Add the continuation parameter `k`.**
Every CPS function accepts `k` as its last argument.

```
def factorial_k(n, k):
    if n == 0:
        ...
    else:
        ...
```

**Step 2 — Replace `return value` with `k(value)` in the base case.**
There is no pending work after the base case, so we just hand the result to `k`.

```
def factorial_k(n, k):
    if n == 0:
        k(1)               # was: return 1
    else:
        ...
```

**Step 3 — Handle the recursive case.**
In direct style: `return n * factorial(n-1)`.
The pending work is the multiplication `n * (...)`. We must capture that as a closure.

- The recursive call becomes `factorial_k(n-1, ...)`.
- The "..." is a lambda that receives the result of `factorial(n-1)`, multiplies by `n`, and passes the product to the *outer* `k`.
- Written out: `factorial_k(n-1, lambda result: k(n * result))`

```
def factorial_k(n, k):
    if n == 0:
        k(1)                                         # base: call k with 1
    else:
        factorial_k(n - 1, lambda result: k(n * result))  # recursive tail call
```

**Why this is now tail-recursive:**
After the `else` branch executes `factorial_k(n-1, ...)`, there is nothing left for the current call to do. The multiplication `n * result` will happen *inside* the lambda, which is called later. The current stack frame can be discarded immediately. The pending work moved from the stack to the heap (the closure).

> **Watch out! — Closures and variable capture**
>
> In the lambda `lambda result: k(n * result)`, the variable `n` is captured from the enclosing scope. In Python, this works correctly here because `n` is a function parameter — each call to `factorial_k` creates a new `n` binding. Lambda parameters (like `result`) also create new bindings. The danger arises with **loop variables**: if you wrote `for n in range(5): lambdas.append(lambda: n)`, all lambdas would capture the same `n` and all would print `4`. When writing CPS by hand inside loops, use a default argument trick (`lambda result, _n=n: _n * result`) to freeze the value at creation time, as you will see in the trampoline code later.

> **Watch out! — What the continuation `k` represents**
>
> The continuation `k` is "the rest of the computation." When `factorial_k(5, k)` is called, `k` is a function that knows what to do with the answer `120` once it arrives — perhaps print it, perhaps multiply it by something else, perhaps store it. Every function in CPS takes `k` and calls it with its result instead of returning. This means the result never travels back up the call stack; it always travels *forward* through the continuation chain.

---

## Directions and Group Roles

**This is a POGIL activity.** Work in groups of three or four. Assign the following roles before you begin, and rotate roles with each new Part.

| Role | Responsibility |
|------|---------------|
| **Manager** | Keeps the group on task and on time; ensures everyone contributes; escalates to the instructor when the group is stuck for more than two minutes |
| **Recorder** | Writes down the group's agreed answers; ensures the written responses are complete and legible |
| **Presenter** | Speaks for the group during class discussion; prepares to explain the group's reasoning, not just the answer |
| **Reflector** | Monitors group process; notes what strategies are working or not; leads the end-of-part reflection check-in |

> **Ground rule:** No one moves on until the Recorder has written down an answer that every member can explain independently. If one person is confused, the group is not done.

---

## Part I: Direct Style vs. CPS

### Model 1: Two Ways to Write Factorial

Consider the factorial function written two different ways. Read both carefully before answering the questions below.

**Direct Style** — the familiar recursive version:

```python  liascript
def fact_direct(n):
    if n == 0:
        return 1
    else:
        return n * fact_direct(n - 1)

# Call it:
# fact_direct(5) => 120
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

**CPS Style** — every function takes an extra argument `k` (the continuation):

```python  liascript
def fact_cps(n, k):
    if n == 0:
        k(1)
    else:
        fact_cps(n - 1, lambda result: k(n * result))

# Call it with the identity continuation:
# fact_cps(5, lambda x: x)  => 120 (returned from identity)
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

**Key insight:** In the direct style, the Python call stack implicitly records "we still need to multiply by `n` after the recursive call returns." In the CPS version, that pending work is made *explicit* as a closure: `lambda result: k(n * result)`. The continuation **is** the stack frame. When there are no more stack frames to push because all pending work lives in closures, every call is a tail call.

### Runnable Model: Comparing Both Versions

Run the cell below to see both versions produce the same output.

```python  liascript
import sys
import traceback

try:
    # ── Direct Style ──────────────────────────────────────────────
    def fact_direct(n):
        if n == 0:
            return 1
        else:
            return n * fact_direct(n - 1)

    # ── CPS Style ────────────────────────────────────────────────
    def fact_cps(n, k):
        if n == 0:
            k(1)
        else:
            fact_cps(n - 1, lambda result: k(n * result))

    # Identity continuation: just return the value as-is
    identity = lambda x: x

    # We capture the result by storing it in a mutable container
    # because Python lambdas cannot assign to outer variables directly.
    result_box = [None]
    def capture(x):
        result_box[0] = x

    print("Direct style:  fact_direct(6) =", fact_direct(6))

    fact_cps(6, capture)
    print("CPS style:     fact_cps(6, capture) =>", result_box[0])

    # Trace the first few steps manually
    print()
    print("Tracing fact_cps(3, print):")
    print("  Each step shows what k is called with:")
    fact_cps(3, lambda x: print("  Final k receives:", x))

except Exception as e:
    print("[cps:factorial] Error:", e)
    traceback.print_exc()
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

### Critical Thinking Questions — Part I

**CTQ 1.1** In `fact_cps`, look at the two branches:

- Branch `n == 0`: calls `k(1)`
- Branch `n > 0`: calls `fact_cps(n - 1, lambda result: k(n * result))`

Which expression in *each* branch is in **tail position** (i.e., is the very last thing the function does before it "returns")?

[[___]]
<script>true</script>

> In the `n == 0` branch, the tail call is `k(1)`. In the `n > 0` branch, the tail call is `fact_cps(n - 1, ...)`. Crucially, **every** branch ends with exactly one tail call — there is no pending work after either recursive call. The pending multiplication has been absorbed into the new continuation closure.

---

**CTQ 1.2** The **identity continuation** is `lambda x: x`. When you call `fact_cps(5, lambda x: x)`, what does this continuation *do* with the final result? What is its role in the computation?

[[___]]
<script>true</script>

> The identity continuation simply returns its argument unchanged. It plays the role of "the top-level program that receives the final answer." In a full CPS-transformed program, the outermost call is always supplied with the identity (or a print/store continuation) because there is nothing left to do after the last result is produced.

---

**CTQ 1.3** Trace `fact_cps(3, lambda x: x)` step by step. At each step, write down:
(a) the value of `n`,
(b) the current continuation `k` (describe it as a closure, e.g., `lambda result: outer_k(3 * result)`),
(c) what call is made next.

[[___]]
<script>true</script>

> **Step 1:** `n=3`, `k = identity`. Since `n != 0`, call `fact_cps(2, lambda r: identity(3 * r))`.
>
> **Step 2:** `n=2`, `k = lambda r: identity(3*r)`. Call `fact_cps(1, lambda r: k_prev(2 * r))`.
>
> **Step 3:** `n=1`, `k = lambda r: k_prev(2*r)`. Call `fact_cps(0, lambda r: k_prev2(1*r))`.
>
> **Step 4:** `n=0`. Call `k(1)`. The chain unwinds: `1*1=1`, then `2*1=2`, then `3*2=6`. The identity continuation receives `6`.
>
> Notice how the chain of closures perfectly mirrors the chain of stack frames in the direct version — but the closures live on the heap, not the stack.

---

**CTQ 1.4** Direct-style `fact_direct` is *not* tail-recursive: after the recursive call, there is still a multiplication to do. Yet `fact_cps` **is** tail-recursive. Explain precisely how the CPS transform converts the non-tail recursive direct version into a tail-recursive CPS version. What happened to the pending multiplication?

[[___]]
<script>true</script>

> In `fact_direct`, the pending work `n * (...)` is stored implicitly on the call stack. The CPS transform takes that pending work and packages it into a new closure — the new continuation — which is passed *down* into the recursive call. The recursive call now has nothing left to do after it completes (because it never returns — it calls its continuation instead), so it is trivially in tail position. The multiplication did not disappear; it moved from the stack to the heap, encoded inside a closure. This is why CPS enables tail-call optimization even for functions that were originally non-tail-recursive: the transform relocates all pending work into explicit data structures.

---

## Part II: The CPS Transform Algorithm

### Model 2: The Mechanical CPS Transform

CPS transformation is a *systematic* algorithm. The core rule is:

> **For every subexpression, give it a name, then pass that name to a fresh continuation.**

Consider transforming `f(g(x)) + h(y)` from direct style to CPS. We want a function `transform(k)` that, when called, eventually calls `k` with the result of the whole expression.

**Step-by-step CPS transform of `f(g(x)) + h(y)`:**

```
Direct:     f(g(x)) + h(y)

Step 1: g(x) is the innermost call. Name its result v1.
        g_cps(x, lambda v1: ...)

Step 2: Apply f to v1. Name its result v2.
        g_cps(x, lambda v1:
            f_cps(v1, lambda v2: ...))

Step 3: h(y) is independent. Name its result v3.
        g_cps(x, lambda v1:
            f_cps(v1, lambda v2:
                h_cps(y, lambda v3: ...)))

Step 4: Add v2 and v3. Pass to original continuation k.
        g_cps(x, lambda v1:
            f_cps(v1, lambda v2:
                h_cps(y, lambda v3:
                    k(v2 + v3))))
```

Notice the **inside-out** structure: the outermost operation (`+`) ends up deepest in the nesting. The nesting order in CPS is the *reverse* of the evaluation order in direct style. This is because continuations represent "the future," and the most distant future is the outermost continuation.

### Model 3: CPS Fibonacci

Here is Fibonacci in direct style and in CPS. The CPS version uses a single continuation that accumulates the final sum.

```python  liascript
import sys
import traceback

try:
    # Direct style Fibonacci
    def fib_direct(n):
        if n <= 1:
            return n
        return fib_direct(n - 1) + fib_direct(n - 2)

    # CPS Fibonacci
    # fib_cps(n, k) eventually calls k(fib(n))
    def fib_cps(n, k):
        if n <= 1:
            k(n)
        else:
            # First compute fib(n-1), then inside that continuation
            # compute fib(n-2), then add them and pass to k
            fib_cps(n - 1, lambda v1:
                fib_cps(n - 2, lambda v2:
                    k(v1 + v2)))

    result_box = [None]
    def capture(x):
        result_box[0] = x

    print("Direct fib(8) =", fib_direct(8))

    sys.setrecursionlimit(5000)
    fib_cps(8, capture)
    print("CPS    fib(8) =", result_box[0])

    # Show the inside-out structure for fib(3)
    print()
    print("fib_cps(3, print) traces:")
    fib_cps(3, lambda x: print("  k receives:", x))

except RecursionError as e:
    print("[cps:fibonacci] RecursionError:", e)
    print("  (Try a smaller n, or see Part V on trampolining)")
except Exception as e:
    print("[cps:fibonacci] Error:", e)
    traceback.print_exc()
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

### Multiple Choice: CPS Form for `add(mul(2, 3), 4)`

Which of the following is the **correct** CPS form for `add(mul(2, 3), 4)`?

Assume `mul_cps(a, b, k)` and `add_cps(a, b, k)` are the CPS versions of multiply and add.

[( )] `add_cps(mul_cps(2, 3, identity), 4, k)`
[(X)] `mul_cps(2, 3, lambda v: add_cps(v, 4, k))`
[( )] `k(add_cps(mul_cps(2, 3, k), 4, k))`
[( )] `mul_cps(2, 3, k); add_cps(result, 4, k)`

> **Correct: option B.** The multiplication happens first (innermost subexpression). Its result `v` is passed to a continuation that performs the addition, and the addition's result is passed to the original continuation `k`. Option A incorrectly calls `mul_cps` and expects it to *return* a value (direct style thinking). Options C and D mix direct and CPS style.

### Critical Thinking Questions — Part II

**CTQ 2.1** The claim is: "Every CPS function ends with exactly one tail call." Verify this for both branches of `fib_cps`:

- In the `n <= 1` branch, what is the single tail call?
- In the `n > 0` branch, identify each tail call as you read through the nesting.

[[___]]
<script>true</script>

> In the `n <= 1` branch: `k(n)` is the single tail call — the function does nothing after calling `k`.
>
> In the `n > 0` branch: the function's own tail call is `fib_cps(n-1, ...)`. Inside the lambda passed as its continuation, the tail call is `fib_cps(n-2, ...)`. Inside *that* lambda, the tail call is `k(v1 + v2)`. Every lambda in the chain ends with exactly one tail call — this is the defining structural property of CPS.

---

**CTQ 2.2** Consider the conditional expression `if a then b else c`. Write its CPS transform. Both branches should call the continuation `k`.

[[___]]
<script>true</script>

> ```
> def cond_cps(a, b_cps, c_cps, k):
>     if a:
>         b_cps(k)   # b_cps takes a continuation and calls it with b's result
>     else:
>         c_cps(k)   # c_cps takes a continuation and calls it with c's result
> ```
>
> The key point: both branches call `k` with their result. There is no "join point" after the conditional in CPS — both paths pass control forward through the same continuation. This makes conditional expressions structurally identical to function calls in CPS.

---

**CTQ 2.3** The CPS transform claims to remove *all* non-tail calls from a program. Explain in your own words why this is true. (Hint: Where does the pending work go?)

[[___]]
<script>true</script>

> Every non-tail call has pending work that needs to happen after the call returns. The CPS transform captures that pending work as a closure (the new continuation) and passes it as an argument to the called function. The called function's only job at its leaf is to call that continuation. Because all pending work is now in closures (heap-allocated data), no pending work remains on the call stack. Every call in the resulting CPS code is therefore a tail call — there is nothing left to do after any call completes, because "what to do next" has already been handed off as a data value.

---

**CTQ 2.4** Suppose you implement a CPS interpreter in Python that uses Python's own call stack to evaluate the CPS chain (i.e., Python evaluates each closure call by pushing a new stack frame). What specific risk does this create, and what is the standard solution? (This problem is the subject of Part V.)

[[___]]
<script>true</script>

> Even though every call in the CPS code is a tail call *logically*, Python does not optimize tail calls — it pushes a new stack frame for every function call regardless. A deep chain of CPS continuations therefore creates a deep Python call stack and will eventually raise `RecursionError`. The standard solution is **trampolining**: instead of calling each continuation directly, wrap it in a `Thunk` (a zero-argument lambda or object). A top-level loop (the trampoline) then repeatedly calls the thunk, unwrapping one step at a time. This replaces the implicit call stack with an explicit loop, using O(1) stack space regardless of program depth.

---

## Part III: Exceptions as Continuations

### Model 4: Two-Continuation Style

Ordinary CPS uses one continuation `k` representing "what to do on success." We can model exceptions by adding a *second* continuation `h` (the **handler** or escape continuation) representing "what to do on error."

Every function takes both continuations and chooses which one to invoke:

```
def f_cps(args, k, h):
    if error_condition:
        h(error_value)   # escape: jump to the handler
    else:
        k(result)        # normal: pass result forward
```

The `try/except` construct in direct style corresponds to:

- Setting up a new handler `h` that wraps the except-block
- Passing that `h` through the entire continuation chain inside the try-block
- Any function anywhere in the chain can call `h` directly, bypassing all intermediate `k` continuations

### Runnable Model: CPS Division with Error Handler

```python  liascript
import traceback

try:
    # safe_div_cps(a, b, k, h):
    #   - calls k(a/b) on success
    #   - calls h("division by zero") on error
    def safe_div_cps(a, b, k, h):
        if b == 0:
            h("division by zero: {} / {}".format(a, b))
        else:
            k(a / b)

    # A computation: compute (10 / x) + (6 / y)
    # In CPS with error handling, both divisions share the same handler h
    def compute_cps(x, y, k, h):
        safe_div_cps(10, x, lambda v1:
            safe_div_cps(6, y, lambda v2:
                k(v1 + v2),
            h),
        h)

    # Success handler: just print
    def on_success(result):
        print("  Result:", result)

    # Error handler: print a message
    def on_error(msg):
        print("  Error caught by handler:", msg)

    print("compute_cps(2, 3, ...):")
    compute_cps(2, 3, on_success, on_error)

    print("compute_cps(0, 3, ...):")
    compute_cps(0, 3, on_success, on_error)

    print("compute_cps(2, 0, ...):")
    compute_cps(2, 0, on_success, on_error)

    # Nested handlers: inner try/except in CPS
    print()
    print("Nested handler demo (inner catches, outer does not see the error):")
    def inner_on_error(msg):
        print("  Inner handler caught:", msg)
        # Recover by calling the outer success continuation with a default
        on_success(-999.0)

    compute_cps(5, 0, on_success, inner_on_error)

except Exception as e:
    print("[cps:exceptions] Error:", e)
    traceback.print_exc()
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

### Critical Thinking Questions — Part III

**CTQ 3.1** When `safe_div_cps(10, 0, k, h)` calls `h("division by zero")`, what happens to the continuation `k`? Does `k` ever get called? Trace the control flow through `compute_cps(2, 0, on_success, on_error)` to explain where control goes.

[[___]]
<script>true</script>

> When `h` is called, `k` is completely bypassed — it is never called. In `compute_cps(2, 0, ...)`:
> 1. `safe_div_cps(10, 2, lambda v1: ..., h)` succeeds, so it calls `lambda v1: ...` with `v1 = 5.0`.
> 2. Inside that continuation, `safe_div_cps(6, 0, lambda v2: k(v1+v2), h)` is called. Since `y=0`, it calls `h("division by zero: 6 / 0")`.
> 3. `h` is `on_error`, which prints the message. The continuation `lambda v2: k(v1+v2)` is never called.
>
> The handler `h` acts as a "side exit" from the continuation chain. Normal flow threads through the `k` chain; exceptional flow jumps directly to `h`, discarding all intermediate continuations.

---

**CTQ 3.2** In direct-style Python, `raise` can "jump over" multiple stack frames at once — an exception thrown inside a deeply nested helper reaches a `try/except` many levels up without executing any of the intermediate code. Explain why this same behavior emerges naturally in the two-continuation CPS model. Where is the "distance to the handler" encoded?

[[___]]
<script>true</script>

> In the two-continuation model, the handler `h` is not stored in any stack frame — it is passed as a *data argument* through the entire continuation chain. Every function in the chain receives `h` and must explicitly pass it further down. When any function calls `h(error)`, it invokes that function directly, bypassing the entire chain of `k` continuations that are waiting. The "distance to the handler" is not encoded anywhere — from `h`'s perspective, there is no distance at all. It is just a function that gets called. The intermediate `k` closures are simply never invoked, and since no one holds a reference that forces their evaluation, they become garbage. This is exactly what "jumping over stack frames" means: in CPS, the stack frames are just closures, and you can skip them by holding a direct reference to a far-away continuation.

---

**CTQ 3.3** A `finally` clause must execute whether or not an exception occurs. Design a two-continuation scheme to implement `finally`. How many continuations do you need? What does each one do?

[[___]]
<script>true</script>

> You still need two continuations, but you wrap *both* of them to first execute the finally-block:
>
> ```python
> def try_finally_cps(body_cps, finally_cps, k, h):
>     # k_with_finally: on success, run finally, then k
>     def k_with_finally(result):
>         finally_cps(lambda _: k(result), h)
>
>     # h_with_finally: on error, run finally, then re-raise via h
>     def h_with_finally(err):
>         finally_cps(lambda _: h(err), h)
>
>     body_cps(k_with_finally, h_with_finally)
> ```
>
> Both `k` and `h` are wrapped so that the finally-block runs before control passes on. The finally-block itself is CPS-transformed and takes its own continuation — this is how even cleanup code participates in the CPS chain without breaking the model.

---

## Part IV: Async/Await as CPS in Disguise

### Model 5: Callbacks, Generators, and Async

Consider how Python (and Node.js) approaches asynchronous I/O. In callback style:

```python  liascript
def fetch_user(user_id, on_done):
    # ... eventually calls on_done(user_data)
    pass

def fetch_posts(user, on_done):
    # ... eventually calls on_done(posts)
    pass

# Callback-style usage:
fetch_user(42, lambda user:
    fetch_posts(user, lambda posts:
        print("Got posts:", posts)))
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

This **is** CPS. `on_done` is the continuation. Nesting callbacks is manually writing the CPS transform.

Now compare `async/await`:

```python  liascript
async def get_user_posts():
    user = await fetch_user(42)     # fetch_user_cps(42, lambda user: ...)
    posts = await fetch_posts(user)  # fetch_posts_cps(user, lambda posts: ...)
    print("Got posts:", posts)
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

The `await` keyword *is* the continuation application. The compiler desugars `x = await expr; body` into `expr_cps(lambda x: body_cps(...))`. Python generates a state machine (a `coroutine` object) that is exactly a heap-allocated continuation.

Similarly, Python **generators** are "stackless coroutines" — they capture the continuation at the `yield` point:

```python  liascript
def my_gen():
    yield 1        # "call my caller's continuation with 1, then wait"
    yield 2        # "call my caller's continuation with 2, then wait"
    yield 3        # "call my caller's continuation with 3, then wait"
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

Each `yield` is a `k(value)` call where `k` is "send the value to whoever is iterating over me, then resume when they call next()."

### Runnable Model: Manual CPS Simulation of a Simple Event Loop

```python  liascript
import traceback
from collections import deque

try:
    # A minimal "event loop" driven by CPS callbacks.
    # Tasks are (function, args) pairs enqueued for later execution.
    event_queue = deque()

    def schedule(fn, *args):
        """Schedule fn(*args) to run on the next event loop tick."""
        event_queue.append((fn, args))

    def run_loop():
        """Run until there are no more scheduled tasks."""
        while event_queue:
            fn, args = event_queue.popleft()
            fn(*args)

    # Simulated async operations using CPS + scheduling
    def async_add(a, b, k):
        """Asynchronously add a+b, then call k with the result."""
        def _work():
            result = a + b
            k(result)
        schedule(_work)

    def async_mul(a, b, k):
        """Asynchronously multiply a*b, then call k with the result."""
        def _work():
            result = a * b
            k(result)
        schedule(_work)

    # Manual CPS async program:
    # Compute (2 + 3) * 4 using async operations
    print("Starting async computation: (2 + 3) * 4")

    def start():
        async_add(2, 3, lambda sum_result:
            async_mul(sum_result, 4, lambda product:
                print("  Async result: (2+3)*4 =", product)))

    schedule(start)
    run_loop()

    # Compare to: synchronous CPS chain
    print()
    print("Same computation in synchronous CPS:")
    result_box = [None]

    def add_cps(a, b, k):
        k(a + b)

    def mul_cps(a, b, k):
        k(a * b)

    add_cps(2, 3, lambda s: mul_cps(s, 4, lambda p: result_box.__setitem__(0, p)))
    print("  Sync CPS result:", result_box[0])

    # Python generator as a resumable continuation
    print()
    print("Generator as resumable continuation:")

    def counting_gen():
        print("  [gen] about to yield 1")
        yield 1
        print("  [gen] resumed after 1, about to yield 2")
        yield 2
        print("  [gen] resumed after 2, about to yield 3")
        yield 3
        print("  [gen] done")

    g = counting_gen()
    for val in g:
        print("  [caller] received:", val)

except Exception as e:
    print("[cps:async] Error:", e)
    traceback.print_exc()
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

### Critical Thinking Questions — Part IV

**CTQ 4.1** When a Python generator executes `yield value`, what does it "capture" at that moment? Describe in terms of continuations: what is the continuation of a `yield` expression, and who holds it?

[[___]]
<script>true</script>

> When a generator yields, Python captures the **entire execution state** of the generator function: the program counter (where to resume), all local variables, and the value stack at that point. This captured state is exactly a **continuation** — it is "the rest of the generator's computation, waiting for the next `next()` call." The generator object itself holds this continuation. The caller's loop (or `for` statement) holds the reference to the generator object. When the caller calls `next(g)`, it is applying that stored continuation, resuming the generator from where it left off. `yield value` is therefore `k_caller(value)` where `k_caller` is the continuation of whoever is iterating.

---

**CTQ 4.2** Callback-based APIs in Node.js (and early Python async code) require deeply nested callbacks for sequential asynchronous operations — a phenomenon called "callback hell." Explain precisely why this nesting arises in terms of CPS. What does the nesting structure *encode*?

[[___]]
<script>true</script>

> Callback hell arises because sequential operations in CPS have **lexically nested continuations**. If operation B must happen after operation A, then B's code must appear inside A's callback. If C must happen after B, C's code must appear inside B's callback (which is inside A's callback). The nesting depth equals the length of the sequential chain. This nesting is not incidental — it is the direct encoding of **sequential ordering** in CPS: the inner closures capture the outer closures' variables (the results of previous operations), which is exactly what sequential data flow requires. `async/await` does not eliminate this structure; it just lets the programmer write it as flat sequential code while the compiler generates the nested closures automatically.

---

**CTQ 4.3** The equivalence `async def f(): x = await g(); return x + 1` and `g_cps(lambda x: k(x + 1))` is claimed. Walk through the desugaring step by step. What does `await` *do* to the continuation? Where does `k` come from in the async version?

[[___]]
<script>true</script>

> Step 1: `async def f()` declares `f` as a coroutine. When called, it returns a coroutine object without running any code yet. The coroutine object *is* a suspended continuation — the entire body of `f` is waiting.
>
> Step 2: `x = await g()` means: run `g()` to get an awaitable; when that awaitable completes with a result, bind the result to `x` and continue. The "continue" part is the rest of `f`'s body — i.e., `return x + 1`. This rest-of-body is exactly the continuation `lambda x: k(x + 1)`, where `k` is the continuation of whoever awaited `f()`.
>
> Step 3: `return x + 1` in an async function calls the implicit outer continuation `k` with `x + 1`. The Python runtime provides `k` as the mechanism that signals the outer `await` (if any) or the event loop's task scheduler that `f` has completed.
>
> So `await` performs: "pass the rest of this coroutine as a continuation to the awaitable, and suspend until that continuation is invoked."

---

## Part V: Trampolining

### Model 6: The Stack Overflow Problem and Its Solution

In Python and JavaScript, every function call pushes a stack frame. CPS programs can chain thousands of tail calls, each one pushing a new frame — even though logically each frame is immediately garbage (there is no pending work). This causes `RecursionError` in Python even for simple CPS computations on large inputs.

**The trampoline pattern works in three steps:**

1. Instead of calling the next continuation directly, **return a thunk** — a zero-argument function (or wrapper object) that represents "the next step to execute."
2. The caller (the trampoline loop) receives the thunk but does NOT call it immediately inside the current frame. It first returns from the current frame, then calls the thunk.
3. A top-level `while` loop (the trampoline) keeps calling thunks until a non-thunk value emerges. This loop uses exactly one stack frame per step.

```
Without trampoline (stack grows):
  fact_tramp(5, k)
    fact_tramp(4, k2)        <-- frame stacked on top of 5's frame
      fact_tramp(3, k3)      <-- frame stacked on top of 4's frame
        ...                  <-- keeps growing

With trampoline (constant stack):
  trampoline loop iteration 1: calls fact_tramp(5, k)  -> returns Thunk(fact_tramp, 4, k2)
  trampoline loop iteration 2: calls fact_tramp(4, k2) -> returns Thunk(fact_tramp, 3, k3)
  trampoline loop iteration 3: calls fact_tramp(3, k3) -> returns Thunk(...)
  ...
  At every iteration, the previous frame is GONE before the next one starts.
```

**The key rule:** A trampolined CPS function must **return** a `Thunk` for its recursive tail call instead of **calling** it directly. This one change — `return Thunk(f, args)` instead of `f(args)` — is what makes trampolining work.

### Runnable Model: Thunk Class and Trampoline

```python  liascript
import traceback

try:
    # ── Thunk: represents a deferred computation ─────────────────
    class Thunk:
        """
        A Thunk wraps a callable and its arguments.
        It represents 'do this computation, but not yet.'
        The trampoline loop will call it when it's ready.
        """
        def __init__(self, fn, *args):
            self.fn = fn
            self.args = args

        def __call__(self):
            return self.fn(*self.args)

        def __repr__(self):
            return "Thunk({}, {})".format(self.fn.__name__, self.args)

    # ── Trampoline: the iterative unwrapper ──────────────────────
    def trampoline(thunk_or_value):
        """
        Run a trampolined computation to completion.
        Keeps calling thunks until a non-Thunk value is produced.
        Uses O(1) stack space regardless of program depth.
        """
        result = thunk_or_value
        steps = 0
        while isinstance(result, Thunk):
            result = result()
            steps += 1
        return result, steps

    # ── Trampolined CPS factorial ────────────────────────────────
    # Instead of calling fact_cps(n-1, new_k) directly (which pushes a frame),
    # we return a Thunk wrapping that call (which pops back to the trampoline).
    def fact_tramp(n, k):
        """
        Trampolined CPS factorial.
        Returns a Thunk instead of making a direct recursive call.
        """
        if n == 0:
            return k(1)
        else:
            return Thunk(fact_tramp, n - 1, lambda result, _n=n, _k=k: _k(_n * result))

    # The final continuation stores the result and returns a non-Thunk value
    result_box = [None]
    def final_k(x):
        result_box[0] = x
        return x

    print("Trampolined factorial:")
    for n in [5, 10, 20, 100]:
        result_box[0] = None
        val, steps = trampoline(Thunk(fact_tramp, n, final_k))
        print("  fact_tramp({}) = {} ({} trampoline steps)".format(
            n, result_box[0], steps))

    # ── Show the O(1) stack depth ────────────────────────────────
    print()
    print("Demonstrating O(1) stack depth:")
    import sys

    max_depth = [0]
    call_count = [0]

    def fact_tramp_traced(n, k):
        call_count[0] += 1
        # Measure current Python call stack depth
        current_depth = 0
        frame = sys._getframe(0)
        while frame is not None:
            current_depth += 1
            frame = frame.f_back
        if current_depth > max_depth[0]:
            max_depth[0] = current_depth

        if n == 0:
            return k(1)
        else:
            return Thunk(fact_tramp_traced, n - 1,
                         lambda result, _n=n, _k=k: _k(_n * result))

    result_box[0] = None
    trampoline(Thunk(fact_tramp_traced, 50, final_k))
    print("  fact(50): max observed stack depth =", max_depth[0],
          "(constant regardless of n)")
    print("  Total thunk invocations:", call_count[0])

    # ── Non-trampolined CPS for comparison ───────────────────────
    print()
    print("For comparison, naive CPS factorial at n=500 (may hit recursion limit):")
    def fact_naive_cps(n, k):
        if n == 0:
            k(1)
        else:
            fact_naive_cps(n - 1, lambda result, _n=n, _k=k: _k(_n * result))

    original_limit = sys.getrecursionlimit()
    sys.setrecursionlimit(600)
    try:
        result_box[0] = None
        fact_naive_cps(500, lambda x: result_box.__setitem__(0, x))
        print("  Naive CPS fact(500) =", result_box[0], "(succeeded)")
    except RecursionError:
        print("  Naive CPS fact(500): RecursionError! (as expected without trampolining)")
    finally:
        sys.setrecursionlimit(original_limit)

    print()
    print("Trampolined version at n=500:")
    result_box[0] = None
    trampoline(Thunk(fact_tramp, 500, final_k))
    print("  Trampolined fact(500) ends in ...{}".format(
        str(result_box[0])[-6:]))
    print("  (succeeded)")

except Exception as e:
    print("[cps:trampoline] Error:", e)
    traceback.print_exc()
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

### Critical Thinking Questions — Part V

**CTQ 5.1** In `fact_tramp`, the recursive branch returns `Thunk(fact_tramp, n-1, new_k)` instead of calling `fact_tramp(n-1, new_k)` directly. Why does wrapping in a `Thunk` prevent the immediate recursion that would otherwise occur?

[[___]]
<script>true</script>

> Calling `fact_tramp(n-1, new_k)` immediately invokes the function, pushing a new stack frame before the current frame has popped. This is what causes recursive stack growth.
>
> Returning `Thunk(fact_tramp, n-1, new_k)` instead constructs a `Thunk` object (heap allocation, O(1) work) and **returns** it — immediately popping the current stack frame. No recursive call has been made yet. The trampoline loop receives the `Thunk`, calls it (one frame), gets back another `Thunk` or a value, and repeats. At any moment, there is at most one active stack frame beyond the trampoline loop itself. The work that would have been encoded as nested stack frames is now encoded as a chain of `Thunk` objects on the heap, traversed iteratively.

---

**CTQ 5.2** The trampoline loop uses O(1) stack space regardless of program depth. Explain why. Be specific about what is on the stack at each iteration of the loop, and contrast this with what would be on the stack during a naive recursive CPS execution of the same program.

[[___]]
<script>true</script>

> **Trampoline loop:** At each iteration, the stack contains: (1) the trampoline loop frame, (2) one `Thunk.__call__` frame, (3) one `fact_tramp` frame. After `fact_tramp` returns a new `Thunk`, frames (2) and (3) are popped. The loop assigns the returned `Thunk` to `result` and iterates. Stack depth is always exactly 3 frames (or a constant) — independent of `n`.
>
> **Naive CPS:** `fact_cps(n, k)` calls `fact_cps(n-1, new_k)` without returning first. Frame for `n` stays on the stack while frame for `n-1` is added. Frame for `n-1` stays while `n-2` is added. After `n` calls, the stack has `n` frames for `fact_cps` plus frames for the intermediate lambda continuations. Stack depth is O(n).
>
> The trampoline trades stack depth for heap allocation: each `Thunk` object lives on the heap but stack depth stays constant.

---

**CTQ 5.3** In the Scheme tail-call activity (which you may have completed earlier in this course), Scheme guarantees proper tail calls by having the interpreter reuse the current stack frame instead of pushing a new one. Compare this to trampolining: what is the *same* about both approaches, and what is *different*?

[[___]]
<script>true</script>

> **Same goal:** Both achieve O(1) stack space for tail-call chains. Both allow unbounded recursion through tail calls without stack overflow. Both make it practical to write programs in CPS or continuation-heavy recursive style.
>
> **Different mechanisms:**
>
> - Scheme TCO is implemented by the *runtime/compiler*: when a call is in tail position, the runtime overwrites the current activation record with the new call's arguments and jumps (does not push a new frame). The programmer writes normal recursive code; the optimization is invisible.
>
> - Trampolining is implemented by the *programmer* (or a library): the programmer explicitly wraps tail calls in `Thunk` objects and calls the trampoline. The optimization is visible in the code structure.
>
> **Practical difference:** Scheme TCO is transparent and works for mutually recursive functions automatically. Trampolining requires the programmer to identify and wrap every tail call, and the trampoline must be entered at the top level. In languages without TCO (Python, Java, JavaScript without explicit optimization), trampolining is the standard workaround for writing recursive programs that would otherwise overflow the stack.

---

## Exercises

> **Watch out! — Before the exercises: closures and loop variables**
>
> The exercises below ask you to write CPS functions by hand. Watch for this common mistake: if you build a continuation inside a loop or a function that rebinds a variable, all closures you create in that loop will share the *same* variable reference. Example: `[lambda: i for i in range(3)]` produces three lambdas that all return `2` (the final value of `i`), not `0`, `1`, `2`. Fix it with a default argument: `[lambda _i=i: _i for i in range(3)]`. The trampolined factorial above uses this pattern: `lambda result, _n=n, _k=k: _k(_n * result)`.

> **Watch out! — Before the exercises: the continuation is always the last argument**
>
> By convention throughout these exercises, the continuation `k` is always the *last* argument to any CPS function. When composing CPS functions, the inner function receives the outer function's continuation as its `k`. The outermost call always receives a final "sink" continuation (e.g., `print` or a `capture` function) that consumes the answer without passing it further.

### Exercise 1: CPS-Transform `map`

In direct style, `map(f, lst)` applies `f` to each element of `lst` and returns a new list. In CPS, every call to `f` must use `f_cps`, and the result should be passed to `k` only once — after all elements have been processed.

Write `map_cps(f_cps, lst, k)` such that `k` receives the complete mapped list. Your implementation should be fully CPS: no intermediate returns, only tail calls to continuations.

```python  liascript
import traceback

try:
    # map_cps(f_cps, lst, k):
    #   f_cps is a CPS function: f_cps(x, k) calls k(f(x))
    #   lst is the input list
    #   k is called with the fully mapped list as its argument

    def map_cps(f_cps, lst, k):
        if len(lst) == 0:
            k([])
        else:
            f_cps(lst[0], lambda head:
                map_cps(f_cps, lst[1:], lambda tail:
                    k([head] + tail)))

    # A CPS version of "double": double_cps(x, k) calls k(2*x)
    def double_cps(x, k):
        k(x * 2)

    # A CPS version of "square": square_cps(x, k) calls k(x*x)
    def square_cps(x, k):
        k(x * x)

    result_box = [None]
    def capture(x):
        result_box[0] = x

    lst = [1, 2, 3, 4, 5]
    print("Input list:", lst)

    map_cps(double_cps, lst, capture)
    print("map double:", result_box[0])

    map_cps(square_cps, lst, capture)
    print("map square:", result_box[0])

    # Compare to Python's built-in map
    print("Direct map double:", list(map(lambda x: x * 2, lst)))
    print("Direct map square:", list(map(lambda x: x * x, lst)))

except Exception as e:
    print("[cps:map] Error:", e)
    traceback.print_exc()
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

**Exercise 1 Questions:**

1. In `map_cps`, how many times is `k` called during the evaluation of `map_cps(double_cps, [1,2,3], k)`? Trace through the execution to verify.
2. Modify `map_cps` to also handle errors: if `f_cps` takes a handler argument `h`, propagate `h` through the entire chain.

---

### Exercise 2: CPS Interpreter for a Tiny Expression Language

Consider the following tiny expression language:

- `Num(n)` — a numeric literal
- `Add(left, right)` — addition of two sub-expressions
- `Let(name, value_expr, body_expr)` — bind `name` to the result of `value_expr` in `body_expr`

Write `eval_cps(node, env, k)` that evaluates `node` in environment `env` and calls `k` with the result. Every recursive call should be a tail call (CPS style).

```python  liascript
import traceback

try:
    # AST node constructors (using simple dicts for clarity)
    def Num(n):
        return {"type": "Num", "value": n}

    def Add(left, right):
        return {"type": "Add", "left": left, "right": right}

    def Let(name, value_expr, body_expr):
        return {"type": "Let", "name": name, "value": value_expr, "body": body_expr}

    def Var(name):
        return {"type": "Var", "name": name}

    # CPS interpreter
    def eval_cps(node, env, k):
        """
        Evaluate node in environment env (a dict), then call k with the result.
        All recursive calls are tail calls.
        """
        t = node["type"]

        if t == "Num":
            k(node["value"])

        elif t == "Var":
            if node["name"] not in env:
                raise NameError("Unbound variable: " + node["name"])
            k(env[node["name"]])

        elif t == "Add":
            # Evaluate left, then right, then add and call k
            eval_cps(node["left"], env, lambda left_val:
                eval_cps(node["right"], env, lambda right_val:
                    k(left_val + right_val)))

        elif t == "Let":
            # Evaluate value_expr, bind result to name, evaluate body in extended env
            eval_cps(node["value"], env, lambda val:
                eval_cps(node["body"], dict(list(env.items()) + [(node["name"], val)]), k))

        else:
            raise ValueError("Unknown node type: " + t)

    # Test programs
    env0 = {}

    result_box = [None]
    def capture(x):
        result_box[0] = x

    eval_cps(Num(42), env0, capture)
    print("Num(42) =>", result_box[0])

    eval_cps(Add(Num(3), Num(4)), env0, capture)
    print("Add(3, 4) =>", result_box[0])

    # let x = 5 in x + 10
    prog3 = Let("x", Num(5), Add(Var("x"), Num(10)))
    eval_cps(prog3, env0, capture)
    print("let x=5 in x+10 =>", result_box[0])

    # let x = 3 in let y = x+2 in x+y
    prog4 = Let("x", Num(3),
                Let("y", Add(Var("x"), Num(2)),
                    Add(Var("x"), Var("y"))))
    eval_cps(prog4, env0, capture)
    print("let x=3; y=x+2; x+y =>", result_box[0])   # Expected: 3 + 5 = 8

except NameError as e:
    print("[cps:interpreter] NameError:", e)
except Exception as e:
    print("[cps:interpreter] Error:", e)
    traceback.print_exc()
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

**Exercise 2 Questions:**

1. In `eval_cps` for `Add`, the left sub-expression is evaluated before the right. How would you modify the interpreter to evaluate them in *right-to-left* order? Does the final result change for well-typed programs?
2. Add a `Mul(left, right)` case to the interpreter. How many lines of new code are needed compared to the `Add` case?

---

### Exercise 3: Implementing `call/cc`

`call-with-current-continuation` (call/cc) is a control operator that captures the **current continuation** — everything the program was about to do — and passes it as a first-class function to the user's function `f`. If `f` calls that captured continuation with a value, control jumps back to where `call/cc` was called, as if it had returned that value.

In CPS, `call/cc` is straightforward: since `k` already *is* the current continuation, we just pass `k` to `f`.

```python  liascript
import traceback

try:
    # callcc(f, k):
    #   Captures the current continuation k.
    #   Calls f with (k, k) — passing k both as the "escape" continuation
    #   and as the normal continuation.
    #   If f calls k(val), control returns to the call/cc site with val.

    def callcc(f, k):
        """
        call-with-current-continuation in CPS.
        f is a CPS function: f(escape, k) where escape IS k.
        """
        f(k, k)

    # ── Example 1: Normal use (no escape) ───────────────────────
    print("Example 1: callcc with normal return")
    def example1(k_outer):
        callcc(lambda escape, k: k(100),
               lambda result: k_outer("result from callcc: " + str(result)))

    example1(print)

    # ── Example 2: Early escape using callcc ────────────────────
    print()
    print("Example 2: early escape from search using callcc")

    def early_exit_search(lst, k):
        """
        Find the first negative in lst.
        Use callcc so that finding a match immediately calls k (the escape).
        """
        def search_body(escape, k_inner):
            found = None
            for item in lst:
                if item < 0:
                    found = item
                    break
            if found is not None:
                escape(found)
            else:
                k_inner(None)

        callcc(search_body, k)

    result_box = [None]
    def store(x):
        result_box[0] = x

    early_exit_search([3, 7, 2, -4, 8, -1], store)
    print("  First negative in [3,7,2,-4,8,-1]:", result_box[0])

    early_exit_search([1, 2, 3, 4, 5], store)
    print("  First negative in [1,2,3,4,5]:", result_box[0])

    # ── Example 3: Capture and re-invoke a continuation ──────────
    print()
    print("Example 3: demonstrating that callcc captures k as a first-class value")

    log = []

    def demo_capture(k_outer):
        # callcc passes k_outer to the body as 'escape'
        # The body records it and calls k_outer normally
        callcc(
            lambda escape, k_inner: (
                log.append("escape continuation captured"),
                log.append("escape is k_outer: {}".format(escape is k_outer)),
                k_inner("hello from inside callcc")
            )[-1],
            lambda msg: k_outer("wrapper saw: " + msg)
        )

    demo_capture(lambda s: log.append("outer received: " + str(s)))
    for entry in log:
        print(" ", entry)

except Exception as e:
    print("[cps:callcc] Error:", e)
    traceback.print_exc()
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

**Exercise 3 Questions:**

1. In the CPS model, `callcc(f, k)` is implemented as simply `f(k, k)`. Why is the continuation `k` passed *twice*? What role does each copy play?
2. A continuation captured by `call/cc` can be called *multiple times* (a "multi-shot continuation"). What would happen to the program state each time you called the same continuation? Why does this make multi-shot continuations dangerous to use carelessly?
3. Python's `return` statement is a restricted form of `call/cc` that can only be used once (single-shot, upward-only). What restriction does `return` impose that `call/cc` lifts?

---

### Exercise 4: Manual Generator via CPS Closures

Python generators hide their continuation machinery. In this exercise you will build a simple "generator" manually using closures and CPS-style state, revealing exactly what `yield` is doing under the hood.

```python  liascript
import traceback

try:
    # We want to build a generator equivalent to:
    #
    #   def count_up(start, stop):
    #       n = start
    #       while n < stop:
    #           yield n
    #           n += 1
    #
    # A manual generator is an object with a send_next() method.
    # Internally it stores its continuation: "what to do when send_next() is called."

    class ManualGenerator:
        """
        A generator implemented using explicit CPS-style state.
        The '_resume' field holds the continuation for the next send_next() call.
        """

        def __init__(self, start, stop):
            self.stop = stop
            self._done = False
            self._value = None
            self._resume = None
            self._build(start)

        def _build(self, n):
            """
            Set up the continuation for the range [n, stop).
            Each step: yield n, then build for n+1.
            """
            if n >= self.stop:
                def done_step():
                    self._done = True
                    self._value = None
                self._resume = done_step
            else:
                def make_step(current_n):
                    def step():
                        self._value = current_n
                        # After yielding current_n, prepare the next step
                        self._build(current_n + 1)
                    return step
                self._resume = make_step(n)

        def send_next(self):
            """
            Advance the generator one step (like Python's next()).
            Returns (value, has_value): has_value is False when exhausted.
            """
            if self._done:
                return None, False
            self._resume()
            if self._done:
                return None, False
            return self._value, True

        def __iter__(self):
            while True:
                val, ok = self.send_next()
                if not ok:
                    break
                yield val

    # Test the manual generator
    print("Manual generator for range(2, 7):")
    gen = ManualGenerator(2, 7)
    values = []
    while True:
        val, ok = gen.send_next()
        if not ok:
            break
        values.append(val)
    print("  Values:", values)

    # Compare to Python generator
    print()
    print("Python generator for range(2, 7):")
    def py_gen(start, stop):
        n = start
        while n < stop:
            yield n
            n += 1

    print("  Values:", list(py_gen(2, 7)))

    # Show that the manual generator is iterable
    print()
    print("Manual generator using __iter__:")
    gen2 = ManualGenerator(10, 15)
    print("  Values:", list(gen2))

    # Demonstrate the continuation structure explicitly
    print()
    print("Peeking at the continuation chain:")
    gen3 = ManualGenerator(0, 4)
    print("  _resume is callable:", callable(gen3._resume))
    v1, _ = gen3.send_next()
    print("  After first send_next(): value =", v1, ", _resume points to next step")
    v2, _ = gen3.send_next()
    print("  After second send_next(): value =", v2)
    print("  The _resume field IS the saved continuation of the generator")

except Exception as e:
    print("[cps:generator] Error:", e)
    traceback.print_exc()
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

**Exercise 4 Questions:**

1. In `ManualGenerator`, where is the "continuation" stored? What does it contain at each point during the generator's lifetime?
2. In the Python generator `py_gen`, when `yield n` executes, what happens to the local variable `n` and the loop state? How does the `ManualGenerator` preserve equivalent information?
3. Python's `send(value)` method on generators can *pass a value back into* a paused generator (unlike `next()`, which always sends `None`). What would you need to add to `ManualGenerator` to support `send(value)`? How does this connect to the two-way nature of continuations?

---

## Reflection Prompt

Take five minutes individually, then discuss with your group before the Recorder writes a shared response.

> **Every control flow structure you use daily — function calls, exceptions, async/await, generators, loops via recursion — has a CPS explanation. Does this make you feel that these are fundamentally the *same* thing, or fundamentally *different* things sharing a costume? What does your answer reveal about what a programming language *is*?**

Consider these sub-questions to guide your discussion:

- If they are the *same* thing (all just continuations), does that mean the differences between `return`, `raise`, `yield`, and `await` are merely *syntactic sugar* — or do the different affordances matter beyond aesthetics?
- If they are *different* things that CPS merely *encodes*, then what makes one control structure distinct from another? Is it the *type* of continuation (upward-only, reusable, shared), the *number* of continuations (k, h, both), or something else?
- Felleisen (1991) proved that `call/cc` cannot be encoded in lambda calculus without CPS transformation — it requires a change in the *evaluation strategy* of the language. What does this say about the relationship between syntax, semantics, and expressiveness?
- When you write `async/await` in Python or JavaScript, you are using a feature the language designers added explicitly. If CPS is "already there" underneath, why did those keywords need to be added at all?

[[___]]
<script>true</script>

---

## Further Reading

- **Appel, Andrew W.** *Compiling with Continuations.* Cambridge University Press, 1992. — The definitive reference for CPS as an intermediate representation in optimizing compilers. Shows how every compiler optimization (inlining, closure conversion, register allocation) has a natural CPS formulation.

- **Scheme R7RS specification, Section 6.10:** `call-with-current-continuation`. The canonical definition of `call/cc` in a language that has supported it since 1975. Available at [r7rs.org](https://r7rs.org).

- **Felleisen, Matthias.** "On the Expressive Power of Programming Languages." *Science of Computer Programming* 17(1-3), 1991. — Proves formally that `call/cc` (and therefore CPS) adds strictly more expressive power than the untyped lambda calculus. Foundational for understanding what "expressive power" means rigorously.

- **Python PEP 342** (Coroutines via Enhanced Generators) and **PEP 3156** (Asynchronous I/O Support). Available at [peps.python.org](https://peps.python.org). — The design documents explaining how CPython implements generators and asyncio as CPS state machines.

- **Piponi, Dan.** "The Mother of All Monads." *A Neighborhood of Infinity* (blog), 2008. Available at [blog.sigfpe.com](http://blog.sigfpe.com/2008/12/mother-of-all-monads.html). — Shows that the continuation monad (the Haskell formalization of CPS) is the "universal" monad from which all other monads can be derived. Connects CPS to the broader theory of computational effects.

- **Reynolds, John C.** "Definitional Interpreters for Higher-Order Programming Languages." *Higher-Order and Symbolic Computation* 11(4), 1998 (reprint of 1972 original). — The paper that introduced CPS transformation as a program analysis and compilation technique, predating even Scheme's adoption of `call/cc`.
