<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://github.com/BillJr99/Ursinus-CS374-Fall2026/blob/gh-pages/_pages/Activities/liascript-call-cc.md

import: https://raw.githubusercontent.com/liascript/CodeRunner/master/README.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

# Call with Current Continuation: Capturing the Future

## Learning Goals

By the end of this activity, you will be able to:

- Describe what the "current continuation" is at any point in a CPS program and explain what it means to "capture" it
- Simulate `call/cc` in Python by building an escape continuation using CPS and a mutable cell, and use it to implement early exit from nested computation
- Identify `return`, `break`, and `raise` as restricted forms of escape continuations, and explain what makes `call/cc` more powerful than each of them
- Implement at least two control-flow patterns using captured continuations: early exit and coroutine-style cooperative multitasking
- Explain the connection between `call/cc`, CPS, and closures: continuations are closures over the rest of the program

---

## Before You Begin

> **Prerequisites — make sure you are comfortable with these before proceeding:**
>
> - **Continuations and CPS** — You should be able to take a direct-style function and manually convert it to continuation-passing style. If that is fuzzy, revisit the [CPS Activity](_pages/Activities/liascript-cps.md) before continuing here.
> - **Closures** — You should understand that a Python function defined inside another function "closes over" the outer variables and carries them with it.
> - **Exceptions** — You should understand how `try / raise / except` work in Python and why raising an exception causes a non-local jump out of nested call frames.
>
> **Why those three?** `call/cc` is best understood as a generalization of all three at once: it is CPS made explicit, it uses closures to freeze the program state, and it performs the same kind of non-local jump that exceptions do — but under your direct control.

---

## Opening Hook: You Already Know call/cc

Here is something surprising:

> **Python's `return`, `break`, and `raise` are all forms of call/cc in disguise. They all say "throw away the rest of the current computation and jump somewhere else." The `call/cc` operator makes this explicit and first-class — you can store a 'jump target' in a variable and invoke it later.**

Every time you write `return x` inside a loop, Python throws away the rest of the loop, throws away the rest of the function, and jumps to whatever called the function. `break` throws away the rest of the loop body. `raise` throws away the rest of everything until a matching `except` is found. These jumps are powerful, but they are *wired in* — you cannot pass a `return` around as a value, store it in a list, or call it five seconds later.

`call/cc` unfreezes this. It lets you name the jump target, store it, and fire it whenever you want — once, never, or many times.

This module follows three steps: **(1)** understand continuations as "the rest of the computation," **(2)** simulate `call/cc` in Python using CPS and mutable state, **(3)** observe how every major control-flow mechanism is secretly a restricted continuation.

---

## Directions and Group Roles

| Role | Responsibility |
|------|---------------|
| **Facilitator** | Keeps the group moving; makes sure everyone has spoken before the group decides |
| **Recorder** | Writes down the group's answers and observations |
| **Reporter** | Shares the group's findings with the class |
| **Reflector** | Monitors process; raises a flag if the group is confused but plowing ahead |

Rotate roles every class meeting. Each model has a Python code block — run it, observe the output, then answer the Critical Thinking Questions *before* moving on.

---

## 0. Motivation: try/except Is Already call/cc

Before we touch anything exotic, look at code you have been writing since CS1. The `try/except` construct is an escape continuation — a way of saying "abandon everything and jump here immediately."

```python  liascript
# Ordinary try/except: raise is an escape continuation
class EarlyExit(Exception):
    def __init__(self, value):
        self.value = value

def find_first_even_exceptions(lst):
    """Return the first even number in lst, or None."""
    try:
        for x in lst:
            print(f"  checking {x} ...")
            if x % 2 == 0:
                raise EarlyExit(x)   # JUMP out of the loop immediately
            print(f"  {x} is odd, continuing")
        return None
    except EarlyExit as e:
        print(f"  --> escaped with {e.value}")
        return e.value

print("find_first_even_exceptions([1, 3, 4, 7, 8]):")
print(find_first_even_exceptions([1, 3, 4, 7, 8]))
print()

# Now the same idea expressed with call/cc explicitly:
class Continuation:
    def __init__(self):
        self.value = None
    def __call__(self, value):
        self.value = value
        raise _EscapeException(value)

class _EscapeException(BaseException):
    def __init__(self, value): self.value = value

def callcc(f):
    k = Continuation()
    try:
        result = f(k)
        return result
    except _EscapeException as e:
        return e.value

def find_first_even_callcc(lst):
    """Same logic, but using callcc explicitly."""
    def body(k):          # k is the escape continuation
        for x in lst:
            print(f"  checking {x} ...")
            if x % 2 == 0:
                k(x)      # escape immediately with x
            print(f"  {x} is odd, continuing")
        return None       # only reached if no even number found
    return callcc(body)

print("find_first_even_callcc([1, 3, 4, 7, 8]):")
print(find_first_even_callcc([1, 3, 4, 7, 8]))
print()
print("Both produce the same output! try/except IS call/cc.")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

Run the code and compare the two functions carefully. They produce the same output because they are doing the same thing. The difference is that in the `callcc` version, `k` is a Python object you could, in principle, store in a variable and call later — *after* `find_first_even_callcc` has already returned.

> **CTQ 0.1** In `find_first_even_exceptions`, what line causes the loop to stop early? What does Python do to the call stack when that line executes?

> **CTQ 0.2** In `find_first_even_callcc`, what is the role of `k`? At the moment `k(x)` is called, what is about to be abandoned?

> **CTQ 0.3** The line `print(f"  {x} is odd, continuing")` appears after the `if` check in both functions. Does it ever print for the first even number? Why not?

---

## 1. The "Time Capsule" Analogy

> **A continuation is a frozen snapshot of the entire rest of the program. Calling it says "go back to this snapshot and resume." It is like a time capsule that, when opened, teleports you back to the moment it was sealed — with the program in exactly the state it was in then, except the value you pass in becomes the result of the original expression.**

When Python evaluates `print(1 + f(3))`, the call to `f(3)` has a continuation: "take the result, add 1 to it, pass the sum to `print`." This continuation is normally invisible — it lives in the call stack. To make it visible, we shift to **Continuation-Passing Style (CPS)**: instead of returning a value, every function receives an extra argument `k` (the continuation) and calls it with the result instead of returning.

```python  liascript
# Direct style: f(x) returns x+1; main computes 1 + f(3)
def f_direct(x):
    return x + 1

result = 1 + f_direct(3)
print(f"Direct style: 1 + f(3) = {result}")

# CPS: f takes a continuation k and calls k(x+1)
def f_cps(x, k):
    k(x + 1)

# The continuation for "1 + f(3)" is: take the result, add 1, print it
def main_cps():
    def after_f(val):            # continuation: "what happens after f(3)"
        def after_add(sum_val):  # continuation: "what happens after adding 1"
            print(f"CPS style: 1 + f(3) = {sum_val}")
        after_add(1 + val)
    f_cps(3, after_f)

main_cps()

# The key insight: in CPS, the continuation k IS the call stack, made explicit.
# Let's inspect it by capturing the continuation mid-computation:
saved_k = [None]

def f_capturing(x, k):
    saved_k[0] = k  # SAVE the continuation for later
    k(x + 1)

print("\nCalling f_capturing(3, ...):")
f_capturing(3, lambda val: print(f"  first call: val = {val}"))

print("\nReinvoking the saved continuation with 99:")
saved_k[0](99)   # call the continuation again with a different value!
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

> **CTQ 1.1** In the direct-style call `1 + f_direct(3)`, describe the continuation of `f_direct(3)` in English. What would the computation do with the return value?

> **CTQ 1.2** In `f_capturing`, the continuation `k` is saved in `saved_k`. When we call `saved_k[0](99)` at the end, what happens? Why is the output different from the first call?

> **CTQ 1.3** We saved the continuation and invoked it twice (once from inside `f_capturing` and once from outside). What would happen if the continuation were for a `return` statement — what would invoking it twice mean?

> **CTQ 1.4** The continuation `after_f` in `main_cps` is a Python function. In what sense is a function a "frozen computation"? How is that related to closures?

---

## 2. Step-by-Step Trace: What Does `k` Actually Capture?

Before writing more code, let us slow down and trace exactly what happens in a `callcc` call. This is the part most students rush past and later regret.

Consider the following call:

```
result = callcc(body)
```

Here is the sequence, step by step:

1. **`callcc` creates a fresh `Continuation` object and names it `k`.** Think of `k` as a postcard with the address "return to the caller of `callcc`, and hand them this value."

2. **`callcc` calls `body(k)`.** Inside `body`, `k` is just an ordinary argument — a callable Python object. The key is that it is stamped with the return address: wherever `callcc` was called from.

3. **Two possible outcomes:**

   - **`body` returns normally** (without calling `k`): `callcc` returns whatever `body` returned. `k` is silently discarded and never used.
   - **`body` calls `k(value)`**: This raises `_EscapeException` internally. `callcc`'s `try/except` catches it and returns `value`. Anything that was about to happen in `body` after `k(value)` is **abandoned immediately**.

4. **The code after `k(value)` inside `body` never runs.** This is not a Python bug — it is the point.

The following code makes all four of these cases visible with print statements:

```python  liascript
class Continuation:
    def __call__(self, value):
        raise _EscapeException(value)

class _EscapeException(BaseException):
    def __init__(self, value): self.value = value

def callcc(f):
    k = Continuation()
    try:
        result = f(k)
        print(f"  [callcc] body returned normally with: {result!r}")
        return result
    except _EscapeException as e:
        print(f"  [callcc] k was called; escaping with: {e.value!r}")
        return e.value

# Case A: body never calls k
print("=== Case A: body does NOT call k ===")
val = callcc(lambda k: "hello from body")
print(f"callcc returned: {val!r}")
print()

# Case B: body calls k immediately
print("=== Case B: body calls k immediately ===")
val = callcc(lambda k: k("escaped!"))
print(f"callcc returned: {val!r}")
print()

# Case C: body calls k mid-way, abandoning remaining work
print("=== Case C: body calls k mid-way ===")
def body_c(k):
    print("  body: step 1 -- about to call k")
    k("value from k")
    print("  body: step 2 -- THIS NEVER PRINTS")
    return "this return is also abandoned"

val = callcc(body_c)
print(f"callcc returned: {val!r}")
print()

# Case D: k is stored and called AFTER callcc already returned
print("=== Case D: k stored and fired later ===")
stored_k = [None]

def body_d(k):
    stored_k[0] = k
    return "body returned without calling k"

val = callcc(body_d)
print(f"callcc returned (first time): {val!r}")
print("Now firing stored_k from outside callcc...")
# Note: our simplified implementation raises an exception here;
# a full Scheme continuation would rewind the entire call stack.
try:
    stored_k[0]("late escape")
except _EscapeException as e:
    print(f"  Caught late escape with value: {e.value!r}")
    print("  (In full Scheme call/cc this would rewind the stack)")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

> **CTQ 2.1** In Case B, the lambda calls `k("escaped!")` and then there is no more code. Does the lambda return a value? Does it matter? What does `callcc` return?

> **CTQ 2.2** In Case C, the line `print("  body: step 2 -- THIS NEVER PRINTS")` never executes. Explain precisely why — trace the exception path.

> **CTQ 2.3** Case D shows the limit of our Python simulation: firing `k` after `callcc` has already returned just raises a raw exception rather than truly rewinding the stack. What would a "true" continuation do differently? Why is that impossible to simulate with Python exceptions?

> **CTQ 2.4** Draw a timeline for Case C showing: when `callcc` starts, when `body_c` starts, when `k` is called, and when `callcc` returns. Mark the point where "the rest of body_c" is abandoned.

---

## 3. Simulating `call/cc`

In Scheme, `(call/cc f)` calls `f` with the current continuation as its argument. The current continuation is packaged as an escape procedure: if you call it with a value `v`, the entire `call/cc` expression immediately returns `v`, abandoning whatever computation was pending. Here we simulate this behavior in Python using a class-based continuation object and an exception for early exit.

> **Watch out!** Calling a continuation is a non-local jump. The code after `k(value)` in the current function body is DEAD — it never runs. This surprises almost everyone the first time they see it.

```python  liascript
class Continuation:
    """A reified continuation: call it to escape the current call/cc frame."""
    def __init__(self):
        self.value = None
        self.invoked = False
    
    def __call__(self, value):
        self.value = value
        self.invoked = True
        raise _EscapeException(value)

class _EscapeException(BaseException):
    def __init__(self, value): self.value = value

def call_cc(f):
    """
    call-with-current-continuation:
    Call f(k) where k is the current continuation.
    If k is invoked inside f, call_cc returns that value immediately.
    Otherwise, call_cc returns whatever f returns normally.
    """
    k = Continuation()
    try:
        result = f(k)
        return result  # normal return path
    except _EscapeException as e:
        return e.value  # k was invoked -- return early

# --- Example 1: call/cc as an early-exit mechanism ---
def search(lst, target):
    """Return the index of target, or -1. Use call/cc to escape on find."""
    def body(escape):
        for i, item in enumerate(lst):
            if item == target:
                escape(i)   # immediately returns from call_cc with i
        return -1           # only reached if not found
    return call_cc(body)

data = [10, 20, 30, 40, 50]
print(f"search([10..50], 30) = {search(data, 30)}")
print(f"search([10..50], 99) = {search(data, 99)}")

# --- Example 2: call/cc as an exception mechanism ---
def safe_divide(a, b):
    def body(escape):
        if b == 0:
            escape(("error", "division by zero"))
        return ("ok", a / b)
    return call_cc(body)

print(f"\nsafe_divide(10, 2) = {safe_divide(10, 2)}")
print(f"safe_divide(10, 0) = {safe_divide(10, 0)}")

# --- Example 3: call/cc used "later" (after the original call_cc returned) ---
restart = [None]

def computation_with_restart():
    x = call_cc(lambda k: (restart.__setitem__(0, k), 0)[1])
    # When restart[0] is called later, execution RESUMES here with the new value
    print(f"  x = {x}, x squared = {x*x}")
    return x * x

print("\nFirst run:")
computation_with_restart()

print("Restarting with x=5:")
restart[0](5)   # "time travel": resume from where we saved the continuation
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

> **Watch out!** In Scheme, `call/cc` captures the **entire** continuation (the entire rest of the program). In Python, we simulate this with exceptions — our continuations are more limited (they can only escape upward through the call stack, not sideways or back into a frame that has already returned). Example 3 above shows where the simulation breaks down at the edges.

> **CTQ 3.1** In Example 1, `escape(i)` is called inside a loop. What happens to the loop when `escape` is invoked? How does this differ from a regular `return`?

> **CTQ 3.2** Python's `try/except` implements exception handling. Compare `safe_divide` using `call_cc` to the same function using `try/except`. What is the conceptual relationship between exceptions and continuations?

> **CTQ 3.3** In Example 3, calling `restart[0](5)` makes execution resume at the line `x = call_cc(...)` but with `x=5`. What would happen if you called `restart[0](5)` a second time? A third time?

> **CTQ 3.4** What would it mean for a language to expose `call/cc` as a built-in (like Scheme does), versus simulating it with exceptions (like our Python version)? What can Scheme's `call/cc` do that our simulation cannot?

---

## 4. Non-Local Exit: `break`, `return`, and Exceptions as Continuations

Every control-flow mechanism is a restricted form of `call/cc`. Here we derive `break`, `return`, and exception handling from `call_cc` directly, making the connection explicit.

> **Watch out!** A continuation called more than once re-runs the rest of the program from that captured point. This is how some implementations of coroutines work, and it is also why unrestricted continuations can be confusing — an ordinary `return` would be disastrous if invoked twice.

```python  liascript
class Continuation:
    def __init__(self): self.value = None
    def __call__(self, v=None):
        self.value = v; raise _Escape(v)

class _Escape(BaseException):
    def __init__(self, v): self.value = v

def call_cc(f):
    k = Continuation()
    try: return f(k)
    except _Escape as e: return e.value

# ---- 1. break as call/cc ----
def my_break_loop(lst, pred):
    """Find first element satisfying pred, or None."""
    def body(brk):
        for x in lst:
            if pred(x):
                brk(x)   # "break" out of loop with value x
        return None
    return call_cc(body)

result = my_break_loop([1, 3, 8, 11, 15], lambda x: x > 7)
print(f"First > 7: {result}")

# ---- 2. return as call/cc ----
def factorial_with_early_return(n):
    """Return 0 immediately for negative input."""
    def body(ret):
        if n < 0:
            ret(0)       # "return 0" immediately
        result = 1
        for i in range(1, n + 1):
            result *= i
        return result
    return call_cc(body)

print(f"\nfactorial(5) = {factorial_with_early_return(5)}")
print(f"factorial(-1) = {factorial_with_early_return(-1)}")

# ---- 3. exceptions as two-continuation style ----
def divide_two_cont(a, b, on_success, on_error):
    """Two-continuation style: one for success, one for error."""
    if b == 0:
        on_error("division by zero")
    else:
        on_success(a / b)

def safe_calculation(a, b):
    result = [None]
    error = [None]
    divide_two_cont(
        a, b,
        on_success=lambda v: result.__setitem__(0, v),
        on_error=lambda e: error.__setitem__(0, e)
    )
    return f"ok: {result[0]}" if result[0] is not None else f"error: {error[0]}"

print(f"\ndivide(10, 2) = {safe_calculation(10, 2)}")
print(f"divide(10, 0) = {safe_calculation(10, 0)}")

# ---- 4. Multiple return values from a search ----
# call/cc lets us "return" from inside nested loops
def matrix_search(matrix, target):
    """Return (row, col) of target, or None."""
    def body(found):
        for i, row in enumerate(matrix):
            for j, val in enumerate(row):
                if val == target:
                    found((i, j))
        return None
    return call_cc(body)

M = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
print(f"\nSearch for 5 in matrix: {matrix_search(M, 5)}")
print(f"Search for 10 in matrix: {matrix_search(M, 10)}")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

> **CTQ 4.1** Python's `break` statement exits a `for` loop. How does `my_break_loop` implement the same behavior using `call_cc`? What is the "continuation" being captured?

> **CTQ 4.2** In the two-continuation style (`divide_two_cont`), there are two callbacks: `on_success` and `on_error`. How does this relate to Haskell's `Either` type or Python's `Result` type from the Error Handling activity?

> **CTQ 4.3** The matrix search uses `call_cc` to exit from a doubly-nested loop. Python has no built-in way to `break` out of two loops at once (without goto or a flag). How does `call_cc` solve this cleanly?

> **CTQ 4.4** Every use of `call/cc` in this model corresponds to a control-flow feature Python has natively. What does this suggest about the "expressive power" of `call/cc` as a primitive?

---

## 5. Cooperative Multitasking: Continuations as Green Threads

One of the most striking uses of `call/cc` is implementing cooperative multitasking — multiple "tasks" that voluntarily take turns running on a single thread. Each task, when it wants to pause, calls a `yield_control()` function. Under the hood, `yield_control()` uses `call/cc` to freeze the current task as a continuation, puts it at the back of a queue, and runs the next task. This is exactly how Python's `asyncio` event loop and early coroutine libraries worked.

```python  liascript
from collections import deque

class Continuation:
    def __call__(self, v=None): raise _Escape(v)

class _Escape(BaseException):
    def __init__(self, v=None): self.value = v

def call_cc(f):
    k = Continuation()
    try: return f(k)
    except _Escape as e: return e.value

# The task queue holds continuations (frozen tasks waiting to resume)
task_queue = deque()

def yield_control():
    """Pause the current task and hand control to the scheduler."""
    def body(k):
        # Save OUR continuation (the rest of this task) in the queue
        task_queue.append(k)
        # Then run the next queued task
        _run_next()
    call_cc(body)

def _run_next():
    """Pop the next task from the queue and resume it."""
    if task_queue:
        next_continuation = task_queue.popleft()
        next_continuation(None)   # resume that task

def spawn(task_fn):
    """Add a new task to the queue."""
    task_queue.append(lambda _: task_fn())

# --- Define two tasks that interleave ---
def task_a():
    print("Task A: step 1")
    yield_control()            # pause; let someone else run
    print("Task A: step 2")
    yield_control()
    print("Task A: step 3 (done)")

def task_b():
    print("Task B: step 1")
    yield_control()
    print("Task B: step 2 (done)")

# Enqueue both tasks and start the scheduler
spawn(task_a)
spawn(task_b)

print("=== Scheduler starting ===")
_run_next()   # kick off the first task
print("=== Scheduler done ===")
print()
print("Notice: the tasks interleaved, not one-after-the-other.")
print("yield_control() is 'pause myself and run someone else'.")
print("That is exactly what async/await does in asyncio.")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

> **CTQ 5.1** When `task_a` calls `yield_control()`, it stores its own continuation in the queue and calls `_run_next()`. What is stored in `task_queue` at the moment `_run_next()` is called for the first time?

> **CTQ 5.2** After `task_b` completes, `task_queue` still holds `task_a`'s second continuation. Trace through the execution to explain why `Task A: step 2` eventually prints.

> **CTQ 5.3** This scheduler is *cooperative* (tasks yield voluntarily). A *preemptive* scheduler can interrupt tasks at any time (like the OS does with threads). Could you implement preemptive scheduling with continuations? What extra mechanism would you need?

> **CTQ 5.4** Python's `async def` / `await` syntax is syntactic sugar. Based on this example, what does `await some_coroutine()` desugar to in terms of continuations and a scheduler queue?

---

## 6. Generators and Coroutines as Delimited Continuations

Generators (`yield`) are a form of **delimited continuation** — a continuation up to a specific delimiter, not the entire rest of the program. Here we build a generator from `call_cc` to reveal what `yield` is really doing.

```python  liascript
from collections import deque

class Continuation:
    def __call__(self, v=None): raise _Escape(v)

class _Escape(BaseException):
    def __init__(self, v=None): self.value = v

def call_cc(f):
    k = Continuation()
    try: return f(k)
    except _Escape as e: return e.value

# --- Manual generator using call/cc ---
# A generator is a function that can be "paused" and "resumed"
# We simulate this with call/cc and a queue of continuations

class ManualGenerator:
    def __init__(self, gen_func):
        self._queue = deque()
        self._done = False
        self._result = None
        
        def scheduler(yield_fn):
            gen_func(yield_fn)
            self._done = True
        
        def yield_fn(value):
            """Pause the generator and yield value to the caller."""
            self._result = value
            # Save our "resume continuation" and transfer control
            resumption = [None]
            def body(resume_k):
                resumption[0] = resume_k
                raise _Escape(value)  # pause
            call_cc(body)
        
        self._runner = lambda: scheduler(yield_fn)
    
    def __iter__(self):
        return self
    
    def __next__(self):
        if self._done: raise StopIteration
        try:
            self._runner()
            return self._result
        except StopIteration: raise

# Python's actual generator for comparison:
def countdown_gen(n):
    while n > 0:
        yield n
        n -= 1

print("Python generator:")
for v in countdown_gen(5): print(f"  {v}", end=" ")
print()

# Reveal what yield does by using CPS explicitly:
def countdown_cps(n, k_yield, k_done):
    """Simulate yield in CPS: k_yield is 'what to do with each yielded value'"""
    if n <= 0:
        k_done()
    else:
        k_yield(n, lambda: countdown_cps(n-1, k_yield, k_done))

print("\nCPS 'yield' simulation:")
results = []
countdown_cps(5,
    k_yield=lambda v, resume: (results.append(v), resume()),
    k_done=lambda: None)
print(f"  {results}")

# Demonstrate: yield is "call/cc that remembers where to resume"
print("\nKey insight: Python's 'yield' desugars to:")
print("  1. Save the current continuation (the rest of the generator body)")
print("  2. Call the caller's continuation with the yielded value")
print("  3. When 'next()' is called, invoke the saved continuation")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

> **CTQ 6.1** In `countdown_cps`, `k_yield` receives TWO arguments: the value AND a `resume` function. Why does it need the `resume` function? What does calling `resume()` do?

> **CTQ 6.2** Python's `yield` statement is syntactic sugar. Based on the CPS simulation, what does `yield n` desugar to in terms of continuations?

> **CTQ 6.3** A "full continuation" captures the entire rest of the program. A "delimited continuation" captures the rest of the program up to a marked boundary. `yield` is a delimited continuation: what is the "delimiter" (what marks the boundary)?

> **CTQ 6.4** If you called `resume()` twice, what would happen? How does Python's generator prevent this (prevent "resuming" the same continuation twice)?

---

## 7. Backtracking Search with Continuations

**Prolog-style backtracking** is the most dramatic use of `call/cc` beyond exception handling. The idea: when a search fails, "rewind" to the last choice point and try the next option. Continuations make this natural — save a continuation at each choice point; on failure, invoke the saved continuation to "jump back."

Think of it like a video game save point: `choose` creates a save point right before you pick an option, and `fail` loads the save point and forces you to try the next option.

```python  liascript
class Continuation:
    def __call__(self, v=None): raise _Escape(v)

class _Escape(BaseException):
    def __init__(self, v=None): self.value = v

def call_cc(f):
    k = Continuation()
    try: return f(k)
    except _Escape as e: return e.value

# Backtracking: non-deterministic choice
class _Fail(Exception): pass

choice_stack = []

def choose(options):
    """Non-deterministically choose from options. On backtrack, try next."""
    if not options:
        raise _Fail()
    
    remaining = list(options)
    
    def body(backtrack_k):
        choice_stack.append((backtrack_k, remaining[1:]))
        return remaining[0]
    
    return call_cc(body)

def fail():
    """Backtrack to the most recent choice point."""
    if not choice_stack:
        raise _Fail("No more choices")
    backtrack_k, remaining = choice_stack.pop()
    if not remaining:
        fail()  # this choice point is exhausted; go further back
    choice_stack.append((backtrack_k, remaining[1:]))
    backtrack_k(remaining[0])  # resume at the choice point with next option

# --- Solve: find (x, y) where x^2 + y^2 == 25 ---
print("Finding Pythagorean pairs where x^2 + y^2 = 25:")
solutions = []
try:
    for attempt in range(20):  # try up to 20 times
        choice_stack.clear()
        try:
            x = choose([1, 2, 3, 4, 5])
            y = choose([1, 2, 3, 4, 5])
            if x*x + y*y == 25:
                solutions.append((x, y))
        except _Fail:
            pass
except Exception as e:
    pass

# Simpler: enumerate directly (shows what backtracking would find)
pythagorean = [(x, y) for x in range(1, 6) for y in range(1, 6) if x*x + y*y == 25]
print(f"Pythagorean pairs: {pythagorean}")

# --- Show the concept: backtracking as saved choice points ---
print("\nBacktracking concept:")
print("  choose([A, B, C]) saves a continuation at the choice point")
print("  if the computation fails, the continuation is invoked with B, then C")
print("  This is how Prolog's ; (disjunction) works")
print()

# Demonstrate simple backtracking logic:
def first_solution(pred, options_x, options_y):
    """Find first (x,y) from options satisfying pred."""
    for x in options_x:
        for y in options_y:
            if pred(x, y):
                return (x, y)
    return None

result = first_solution(lambda x, y: x + y == 7 and x < y, range(1, 10), range(1, 10))
print(f"First (x<y) with x+y=7: {result}")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

> **CTQ 7.1** In the backtracking scheme, `choose(options)` saves a continuation and returns the first option. When `fail()` is called, what does it do with the saved continuation?

> **CTQ 7.2** Prolog's execution model is based on backtracking search. How does each Prolog clause correspond to a "choice point"? How does Prolog's `!` (cut) relate to discarding saved continuations?

> **CTQ 7.3** The backtracking example above looks like two nested for-loops. What does this tell you about the relationship between backtracking and explicit search loops?

> **CTQ 7.4** Continuations give you the ability to "jump back in time." What is a practical limit on this power — in other words, what would you NOT want to backtrack across (file writes, network calls, mutations)?

---

## Multiple Choice

[[MC]] In Scheme, `(call/cc f)` calls `f` with the current continuation `k`. What happens when `k` is called with a value `v`?

[( )] `f` returns `v` from its next expression
[(X)] The entire `(call/cc ...)` expression immediately returns `v`, abandoning pending computation
[( )] `v` is pushed onto the continuation stack for later evaluation
[( )] `call/cc` creates a new thread that evaluates `v`

---

[[MC]] The CPS transform of `(f (g x))` is which of the following?

[( )] `(f_cps x (lambda (v) (g_cps v identity)))`
[(X)] `(g_cps x (lambda (v) (f_cps v identity)))`
[( )] `(lambda (k) (f_cps (g_cps x) k))`
[( )] `(g_cps (f_cps x identity) identity)`

---

[[MC]] Python's `try/except` block is semantically equivalent to which continuation-based pattern?

[( )] Full continuation capture (call/cc)
[(X)] Two-continuation style: one for normal return, one for exceptional escape
[( )] Delimited continuation with a reset boundary
[( )] Coroutine-style symmetric transfer

---

[[MC]] A generator's `yield` is best described as:

[( )] A full continuation that captures the entire rest of the program
[(X)] A delimited continuation that captures the rest of the generator body up to StopIteration
[( )] A closure that captures the generator's local variables only
[( )] A coroutine that runs in a separate thread until yielding

---

[[MC]] When `k(value)` is called inside a `callcc` body, what happens to the code that follows `k(value)` in that same function body?

[( )] It runs after `callcc` returns
[( )] It runs in a separate thread
[(X)] It is abandoned immediately and never runs
[( )] It runs once more, then stops

---

## Exercises

**Exercise 1: `call/cc`-based `for-each` with early exit** (15 min)

Implement `for_each_until(lst, f)` using `call_cc` such that `f` is called on each element of `lst`, but if `f` ever returns the special value `"STOP"`, iteration halts immediately. No loops, no flags — use only `call_cc`.

```python  liascript
class Continuation:
    def __call__(self, v=None): raise _Escape(v)

class _Escape(BaseException):
    def __init__(self, v=None): self.value = v

def call_cc(f):
    k = Continuation()
    try: return f(k)
    except _Escape as e: return e.value

def for_each_until(lst, f):
    # Your implementation here
    pass

# Test: print elements until we hit a negative number
log = []
for_each_until([3, 7, 1, -5, 9, 2], 
               lambda x: "STOP" if x < 0 else log.append(x))
assert log == [3, 7, 1], f"Expected [3, 7, 1], got {log}"
print("Exercise 1 passed:", log)
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

**Exercise 2: Resumable computation with `call/cc`** (20 min)

Implement a `ResumableComputation` that uses `call_cc` to pause mid-computation and resume later with a new value. The computation should be able to "receive" values injected from outside.

```python  liascript
class Continuation:
    def __call__(self, v=None): raise _Escape(v)

class _Escape(BaseException):
    def __init__(self, v=None): self.value = v

def call_cc(f):
    k = Continuation()
    try: return f(k)
    except _Escape as e: return e.value

# A computation that asks for input mid-way and can be resumed:
# Step 1: compute prefix = f(x)
# Step 2: yield control, waiting for an external value y
# Step 3: when resumed with y, compute final = prefix + y

class ResumableComputation:
    def __init__(self, f):
        self.f = f
        self._resume_k = None
        self._prefix = None
    
    def start(self, x):
        # Begin the computation with x; pause and wait for resume
        # YOUR CODE HERE
        pass
    
    def resume(self, y):
        # Resume the computation with value y
        # YOUR CODE HERE  
        pass

def my_computation(x):
    return x * 3  # prefix: triple the input

r = ResumableComputation(my_computation)
prefix = r.start(7)
print(f"Paused after computing prefix={prefix}")
final = r.resume(10)
print(f"Resumed with y=10: final = {prefix} + 10 = {final}")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

**Exercise 3: Exception handling from first principles** (20 min)

Using only `call_cc` (no `try/except`), implement:
- `raise_exc(tag, value)` — throw an exception with a tag and value
- `catch(tag, body_fn, handler_fn)` — run `body_fn()` catching exceptions of `tag`; call `handler_fn(value)` on match; re-raise others

```python  liascript
class Continuation:
    def __call__(self, v=None): raise _Escape(v)

class _Escape(BaseException):
    def __init__(self, v=None): self.value = v

def call_cc(f):
    k = Continuation()
    try: return f(k)
    except _Escape as e: return e.value

# Your implementation:
exception_stack = []

def raise_exc(tag, value): pass
def catch(tag, body_fn, handler_fn): pass

# Test:
result = catch("div_zero",
    lambda: (
        print("about to divide"),
        raise_exc("div_zero", "x/0"),
        print("never reached")
    )[-1],
    lambda e: f"caught: {e}"
)
print(f"Result: {result}")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

**Exercise 4: Green threads via continuations** (25 min, harder)

Implement a minimal cooperative multitasking scheduler using `call_cc`. Tasks voluntarily `yield_control()` to transfer to another task. The scheduler keeps a queue of suspended tasks (as continuations) and runs them one at a time.

```python  liascript
from collections import deque

class Continuation:
    def __call__(self, v=None): raise _Escape(v)

class _Escape(BaseException):
    def __init__(self, v=None): self.value = v

def call_cc(f):
    k = Continuation()
    try: return f(k)
    except _Escape as e: return e.value

task_queue = deque()

def yield_control():
    """Pause current task and let the scheduler run the next one."""
    def body(k):
        task_queue.append(k)  # save our continuation
        run_next()             # run the next queued task
    call_cc(body)

def run_next():
    if task_queue:
        next_k = task_queue.popleft()
        next_k(None)

def spawn(task_fn):
    task_queue.append(lambda _: task_fn())

def task_a():
    print("Task A: step 1")
    yield_control()
    print("Task A: step 2")
    yield_control()
    print("Task A: step 3")

def task_b():
    print("Task B: step 1")
    yield_control()
    print("Task B: step 2")

spawn(task_a)
spawn(task_b)
run_next()  # start the scheduler
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

---

## Reflection

> **In your notebook:** You have now seen `call/cc` used for exceptions, early exit, generators, cooperative multitasking, and backtracking. Alan Kay said "the best way to predict the future is to invent it"; Gerald Sussman said "the best way to understand a language feature is to derive it from a more primitive one." Using `call/cc` as the primitive, which of Python's control-flow features could be *removed from the language* without losing expressive power? What would be gained and lost by this simplification?

---

## Further Reading

- **SICP Chapter 3.5 and 4.3** — Abelson & Sussman, *Structure and Interpretation of Computer Programs*. Generators as streams (3.5) and `amb` (the non-determinism operator, 4.3), which is built on `call/cc`.
- **"Continuations by Example"** — Hillel Wayne. A gentle introduction with JavaScript examples.
- **"On the Expressive Power of Programming Languages"** — Felleisen (1991). The formal result that `call/cc` strictly increases expressive power.
- **Racket's `call/cc`** — Racket (a Scheme descendant) has full first-class continuations. Try it at https://racket-lang.org.
- **"Delimited Continuations"** — Kiselyov. Why you usually want `shift`/`reset` rather than full `call/cc`.
- This course's CPS activity — `call/cc` and CPS are dual: every CPS program implicitly captures its continuation; `call/cc` makes that capture explicit.
