<!--
author:   CS374 Course Team
email:    
version:  0.0.1
language: en
narrator: US English Female
comment:  Coroutines and Generators — yield, send, async/await desugaring, green threads, implementing generators in an interpreter
import:   https://raw.githubusercontent.com/liaScript/coderunner/master/README.md
link:     https://cdn.jsdelivr.net/chartist.min.css
-->

# Coroutines and Generators: Pausable Computation

## Learning Goals

By the end of this activity, you will be able to:

- Define coroutines and generators and explain how `yield` captures a continuation to pause and resume computation
- Trace the execution of a generator function step-by-step, predicting what value each `next()` call produces
- Implement lazy infinite sequences using generator functions and compare their memory use to eager list-based equivalents
- Explain how `async`/`await` desugars to a state machine and identify where suspension points occur
- Extend a simple interpreter to support generator objects with `yield` and `send` semantics

> **Prerequisites:** Python functions and closures; basic continuations from the CPS activity
> **Goal:** Understand generators as semi-coroutines, how `yield` captures a continuation, how `async/await` desugars to state machines, and how to add generator support to a simple interpreter.

**POGIL Roles:** Driver · Recorder · Reporter · Manager

---

## Preface: Why Functions Are Too Rigid

A function is called, runs to completion, and returns. This works for most computations — but not all:

- **Infinite sequences:** How do you iterate over all prime numbers? You can't return them all.
- **Cooperative multitasking:** How does one task yield the CPU to another without OS threads?
- **Asynchronous I/O:** How does a function pause while waiting for data without blocking everything?
- **Two-way communication:** How does a producer send values to a consumer one at a time?

All four problems share a structure: a computation needs to **pause at an arbitrary point** and later **resume from exactly where it left off**. This is the essence of a **coroutine**.

---

## Model 1: Generators as Lazy Sequences

A Python **generator function** uses `yield` instead of (or in addition to) `return`. Calling it returns a **generator object** — an object that remembers where the function paused.

```python
import sys

# A regular function computes a finite list eagerly
def first_n_squares_eager(n):
    result = []
    for i in range(n):
        result.append(i * i)
    return result

# A generator function produces values lazily, one at a time
def squares_lazy():
    i = 0
    while True:                  # infinite sequence!
        yield i * i              # pause here, return i*i to caller
        i += 1                   # resume here on next()

print("=== Eager list ===")
xs = first_n_squares_eager(5)
print(f"  type: {type(xs)}, values: {xs}")
print(f"  memory: ~{sys.getsizeof(xs)} bytes (all in RAM)")

print()
print("=== Lazy generator ===")
gen = squares_lazy()
print(f"  type: {type(gen)}")
print(f"  memory: ~{sys.getsizeof(gen)} bytes (no values stored)")
print()

print("  First 7 values (pulled on demand):")
for i, val in enumerate(gen):
    print(f"    next() #{i+1} → {val}")
    if i >= 6:
        break

print()
print("=== Generator protocol: __iter__ and __next__ ===")
gen2 = squares_lazy()
print(f"  next(gen2) = {next(gen2)}")
print(f"  next(gen2) = {next(gen2)}")
print(f"  next(gen2) = {next(gen2)}")

print()
print("=== yield expression inside a for loop ===")
def first_n(gen, n):
    return [next(gen) for _ in range(n)]

print(f"  First 10 squares: {first_n(squares_lazy(), 10)}")

print()
print("=== Finite generator: StopIteration ===")
def countdown(n):
    while n >= 0:
        yield n
        n -= 1

cd = countdown(3)
for v in cd:
    print(f"  {v}", end=" ")
print()

try:
    next(cd)   # already exhausted
except StopIteration:
    print("  StopIteration raised on exhausted generator")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

**Key insight:** A generator function's stack frame is **frozen** at every `yield`. The local variables, loop counter, and instruction pointer are all preserved. `next()` thaws the frame and continues from the yield point.

> **Critical Thinking Questions 1–3**

**CTQ 1.** An infinite list `first_n_squares_eager(1_000_000)` allocates a list of 1 million integers in RAM before returning. A generator `squares_lazy()` uses ~200 bytes regardless of how many values you pull. What architectural difference explains this?

[[___ your answer here ___]]

**CTQ 2.** The generator object remembers "where it was." What four pieces of state must be preserved in the frozen frame to allow resumption at the `yield` point? (Hint: same things a stack frame normally stores.)

[[___ your answer here ___]]

**CTQ 3.** `for v in countdown(3)` implicitly calls `next()` and catches `StopIteration`. Write the desugared version using a `while True` loop with explicit `try/except StopIteration`. What does this reveal about how `for` loops work in Python?

[[___ your answer here ___]]

---

## Model 2: `yield` as a Two-Way Channel (`send` and `throw`)

Generators are not just output pipelines — they can **receive** values via `.send()`. This makes them true **coroutines** (two-way communication channels).

```python
def running_average():
    """Coroutine: receives numbers via send(), yields running average."""
    total = 0.0
    count = 0
    avg = None
    while True:
        value = yield avg         # send avg out AND receive new value in
        if value is None:
            break
        total += value
        count += 1
        avg = total / count

print("=== Bidirectional coroutine with send() ===")
coro = running_average()
result = next(coro)       # must prime the coroutine (run to first yield)
print(f"  initial yield: {result}")   # None (no avg yet)

for v in [10, 20, 30, 40, 50]:
    result = coro.send(v)
    print(f"  sent {v:2d}, received avg = {result:.2f}")

coro.close()   # sends GeneratorExit; coroutine can clean up in try/finally

print()
print("=== throw(): injecting exceptions ===")
def safe_counter():
    n = 0
    while True:
        try:
            yield n
            n += 1
        except ValueError as e:
            print(f"  resetting because: {e}")
            n = 0

sc = safe_counter()
for _ in range(4):
    print(f"  next() → {next(sc)}")
sc.throw(ValueError, "manual reset!")
for _ in range(3):
    print(f"  next() → {next(sc)}")
sc.close()

print()
print("=== yield from: delegating to a sub-generator ===")
def gen_a():
    yield "a1"
    yield "a2"

def gen_b():
    yield "b1"
    yield from gen_a()   # delegate: transparently yields a1, a2
    yield "b2"

print("  yield from chain:")
for v in gen_b():
    print(f"  {v}")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

> **Critical Thinking Questions 4–6**

**CTQ 4.** `value = yield avg` is a single expression that both sends `avg` out AND receives the next `send()` value in. Draw the communication diagram between the driver code and the coroutine. What is the invariant about when `value` gets its value?

[[___ your answer here ___]]

**CTQ 5.** `next(coro)` is equivalent to `coro.send(None)`. Why must you "prime" a coroutine with `next()` (or `send(None)`) before calling `.send(value)`? What is the coroutine's execution state before and after priming?

[[___ your answer here ___]]

**CTQ 6.** `yield from gen_a()` in `gen_b()` is transparent: values pass through `gen_b` as if `gen_a` were inlined. `send()` and `throw()` values also pass through. What design problem does `yield from` solve that plain `for v in gen_a(): yield v` does not handle?

[[___ your answer here ___]]

---

## Model 3: How `yield` Captures a Continuation

`yield` is a **delimited continuation** — it captures the rest of the computation up to the nearest coroutine boundary. This connects generators to the CPS transformation you have already seen.

```python
# Manual CPS transformation of a generator
# Original generator:
#   def gen():
#       yield 1
#       yield 2
#       yield 3
#
# In CPS, "the rest of gen after yield 1" becomes a continuation k1.
# We model this as explicit states.

from dataclasses import dataclass
from typing import Callable, Any, Optional

@dataclass
class GeneratorState:
    """Manual state machine equivalent of a generator."""
    state: int = 0     # which 'yield' are we at?
    # local variables would go here

def gen_state_machine():
    """Models: def gen(): yield 1; yield 2; yield 3"""
    g = GeneratorState()
    while True:
        if g.state == 0:
            g.state = 1
            yield 1           # continuation: state 1
        elif g.state == 1:
            g.state = 2
            yield 2           # continuation: state 2
        elif g.state == 2:
            g.state = 3
            yield 3           # continuation: state 3
        else:
            return             # StopIteration

print("=== State machine equivalent of a 3-yield generator ===")
for v in gen_state_machine():
    print(f"  {v}")

print()
print("=== Python actually compiles generators to state machines ===")
def original_gen():
    yield 1
    yield 2
    yield 3

import dis
print("  Bytecode of original_gen (showing YIELD_VALUE / RESUME):")
for instr in dis.get_instructions(original_gen):
    if instr.opname in ('YIELD_VALUE', 'RETURN_VALUE', 'RESUME', 'LOAD_CONST',
                        'GEN_START', 'RETURN_CONST', 'LOAD_FAST'):
        print(f"    {instr.offset:3d}  {instr.opname:<20} {instr.argval!r}")

print()
print("=== Generators and first-class continuations ===")
# call/cc (call-with-current-continuation) generalizes yield:
# it captures the ENTIRE continuation, not just to the nearest coroutine boundary.
# Python doesn't have call/cc, but we can simulate limited versions.

def make_generator_cps():
    """Shows that 'yield' is equivalent to saving/restoring execution state."""
    continuations = []
    
    def step():
        results = []
        for state in [1, 2, 3]:
            results.append(state)    # 'yield state' captured here
        return results
    
    return step()

print("  Generator-as-CPS result:", make_generator_cps())
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

> **Critical Thinking Questions 7–9**

**CTQ 7.** The state machine version of `gen()` tracks which `yield` the function has reached using an integer state variable. Where does Python store this state in a real generator? (Hint: look at what a generator object contains.)

[[___ your answer here ___]]

**CTQ 8.** A generator's continuation is **delimited** — it runs until the next `yield` or the function returns. A true first-class continuation (Scheme's `call/cc`) captures the **entire remaining computation**. Give an example of something `call/cc` can express that generators cannot.

[[___ your answer here ___]]

**CTQ 9.** The bytecode output shows `YIELD_VALUE` and `RESUME` instructions. Explain what the Python VM does when it hits `YIELD_VALUE`: what changes in the VM's execution state, and what happens to the generator object's frame?

[[___ your answer here ___]]

---

## Model 4: `async`/`await` — Generators Over I/O

Python's `async def` / `await` syntax is syntactic sugar built on generators. An `async` function is a **coroutine** that yields control when waiting for I/O, and an event loop resumes it when the awaited operation completes.

```python
import asyncio
import time

# Simulate async I/O with asyncio.sleep
async def fetch_data(source: str, delay: float) -> str:
    print(f"  [{time.monotonic():.2f}s] Starting fetch from {source}...")
    await asyncio.sleep(delay)    # yields to event loop; other tasks run here
    print(f"  [{time.monotonic():.2f}s] Finished fetch from {source}")
    return f"data from {source}"

async def main_sequential():
    """Sequential: fetch one at a time. Total time ≈ sum of delays."""
    start = time.monotonic()
    a = await fetch_data("server_A", 0.05)
    b = await fetch_data("server_B", 0.05)
    elapsed = time.monotonic() - start
    print(f"  Sequential: got {a!r}, {b!r} in {elapsed:.3f}s")

async def main_concurrent():
    """Concurrent: both fetches run in parallel via asyncio.gather."""
    start = time.monotonic()
    a, b = await asyncio.gather(
        fetch_data("server_A", 0.05),
        fetch_data("server_B", 0.05),
    )
    elapsed = time.monotonic() - start
    print(f"  Concurrent: got {a!r}, {b!r} in {elapsed:.3f}s")

print("=== Sequential async (awaits one at a time) ===")
asyncio.run(main_sequential())

print()
print("=== Concurrent async (gather runs both at once) ===")
asyncio.run(main_concurrent())

print()
print("=== Desugaring: async/await as generator syntax ===")
# Before async/await syntax existed (Python 2 era), coroutines were
# written using generators with yield from.
# Here is the mental model (not real Python 2, but illustrative):

def old_style_coroutine():
    """Equivalent to: async def coroutine(): await asyncio.sleep(0.01)"""
    print("  about to 'yield' (simulating await)")
    yield   # pause; event loop does work here
    print("  resumed after 'yield'")

def old_event_loop(coro):
    gen = coro()
    try:
        next(gen)    # run until first yield
        print("  [event loop] doing other work...")
        next(gen)    # resume after yield
    except StopIteration:
        pass

old_event_loop(old_style_coroutine)
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

> **Critical Thinking Questions 10–12**

**CTQ 10.** In `main_concurrent`, both `fetch_data` calls appear to run simultaneously, yet Python has a Global Interpreter Lock (GIL). Explain how concurrency is achieved without true parallelism. What kind of waiting does `asyncio.sleep` simulate?

[[___ your answer here ___]]

**CTQ 11.** The "function color" problem: an `async` function can only be awaited from another `async` function. This means `async` "infects" callers all the way up the call chain. Why does this structural constraint exist? What would break if you could `await` from a regular function?

[[___ your answer here ___]]

**CTQ 12.** The desugaring demo shows that `await` desugars to `yield`. Describe how an event loop works in terms of generators: what does the event loop do when a coroutine yields? What does it do when the awaited I/O completes?

[[___ your answer here ___]]

---

## Model 5: Implementing a Generator in a Mini Interpreter

Adding generator support to an interpreter requires preserving the function's execution state across multiple calls. The cleanest approach uses Python's own generators as the implementation mechanism.

```python
from dataclasses import dataclass, field
from typing import Any, Optional, Iterator

# --- AST nodes ---
@dataclass
class Num:
    value: float

@dataclass
class Var:
    name: str

@dataclass
class BinOp:
    op: str
    left: Any
    right: Any

@dataclass
class Yield_:          # our language's 'yield' statement
    value: Any

@dataclass
class GeneratorDef:
    param: str
    body: list         # list of statements (each is an AST node)

@dataclass
class Call:
    func: Any
    arg: Any

# --- Environment ---
class Env:
    def __init__(self, parent=None):
        self.bindings = {}
        self.parent = parent
    def lookup(self, name):
        if name in self.bindings: return self.bindings[name]
        if self.parent: return self.parent.lookup(name)
        raise NameError(f"undefined: {name!r}")
    def define(self, name, val):
        self.bindings[name] = val

# --- Generator object produced by calling a GeneratorDef ---
class GeneratorObj:
    def __init__(self, param, body, closure_env, arg):
        self._iter = self._run(param, body, closure_env, arg)
    
    def _run(self, param, body, closure_env, arg):
        env = Env(parent=closure_env)
        env.define(param, arg)
        for stmt in body:
            if isinstance(stmt, Yield_):
                yield eval_expr(stmt.value, env)
            else:
                eval_expr(stmt, env)   # side-effecting statement
    
    def __iter__(self):
        return self
    
    def __next__(self):
        return next(self._iter)

def eval_expr(node, env):
    if isinstance(node, Num):
        return node.value
    if isinstance(node, Var):
        return env.lookup(node.name)
    if isinstance(node, BinOp):
        l = eval_expr(node.left, env)
        r = eval_expr(node.right, env)
        return {"+": l+r, "-": l-r, "*": l*r, "/": l/r}[node.op]
    if isinstance(node, GeneratorDef):
        return node   # a generator definition evaluates to itself (like a closure)
    if isinstance(node, Call):
        fn = eval_expr(node.func, env)
        arg = eval_expr(node.arg, env)
        if isinstance(fn, GeneratorDef):
            return GeneratorObj(fn.param, fn.body, env, arg)
        raise TypeError(f"not callable: {fn!r}")
    raise ValueError(f"unknown node: {node!r}")

# Demo: generator that yields 0, 1, 4, 9, ... (squares up to n)
# Equivalent to:
#   gen squares(n):
#       i = 0
#       while i <= n:
#           yield i * i
#           i = i + 1
# We'll approximate with a fixed body producing first 5 squares:

global_env = Env()
global_env.define("squares_of_5", GeneratorDef(
    param="start",
    body=[
        Yield_(BinOp("*", Var("start"), Var("start"))),
        Yield_(BinOp("*", BinOp("+", Var("start"), Num(1)), BinOp("+", Var("start"), Num(1)))),
        Yield_(BinOp("*", BinOp("+", Var("start"), Num(2)), BinOp("+", Var("start"), Num(2)))),
    ]
))

print("=== Mini interpreter with generator support ===")
call_node = Call(Var("squares_of_5"), Num(0))
gen_obj = eval_expr(call_node, global_env)

print(f"Generator object: {type(gen_obj).__name__}")
for val in gen_obj:
    print(f"  yielded: {val}")

print()
print("=== Key insight: Python's generator IS our interpreter's continuation ===")
print("  Each 'yield eval_expr(...)' in _run captures the frame's state.")
print("  next() on the GeneratorObj resumes exactly where _run paused.")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

> **Critical Thinking Questions 13–15**

**CTQ 13.** The `GeneratorObj._run` method is itself a Python generator (it uses `yield`). This means we are using Python's generator mechanism to implement our interpreter's generator mechanism. What is the technical term for this implementation strategy? What is the risk?

[[___ your answer here ___]]

**CTQ 14.** In the mini interpreter, calling `squares_of_5(0)` creates a new `GeneratorObj` with its own private `Env`. If you called `squares_of_5(0)` twice, you would get two independent generators. How does this differ from calling a regular function twice?

[[___ your answer here ___]]

**CTQ 15.** The body of `GeneratorDef` is evaluated lazily — statements only run when `next()` is called. If the generator body has a side effect (like printing), when does that side effect occur? Give an example where this laziness causes surprising behavior.

[[___ your answer here ___]]

---

## Multiple Choice Review

**Question 1.** A Python generator function `def g(): yield 1; yield 2` called as `g()` returns:

- [( )] The value `1` immediately
- [( )] A list `[1, 2]`
- [(X)] A generator object that yields `1` then `2` when iterated
- [( )] Nothing; the function body has not executed yet

**Question 2.** `coro.send(value)` on a generator/coroutine:

- [( )] Calls the function with `value` as an argument
- [(X)] Resumes the coroutine and makes `value` the result of the `yield` expression
- [( )] Appends `value` to the generator's output sequence
- [( )] Resets the generator to its initial state

**Question 3.** The "function color" problem with `async/await` means:

- [( )] Async functions run faster than regular functions
- [(X)] Async functions can only be awaited from other async functions, propagating up the call chain
- [( )] Async functions cannot call regular functions
- [( )] Async functions require multiple OS threads

**Question 4.** A generator captures its execution state by:

- [( )] Allocating a new heap object for each yielded value
- [( )] Using OS threads with mutex locks
- [(X)] Freezing the stack frame (locals, instruction pointer) as a heap-allocated object
- [( )] Copying all local variables into a global dictionary

---

## Exercises

**Exercise 1.** Implement a `pipeline` that chains generators: `map_gen`, `filter_gen`, and `take_gen`. Use them to compute the first 5 even squares:

```python
def integers_from(n):
    while True:
        yield n
        n += 1

def map_gen(gen, f):
    for v in gen:
        yield f(v)

def filter_gen(gen, pred):
    for v in gen:
        if pred(v):
            yield v

def take_gen(gen, n):
    for i, v in enumerate(gen):
        if i >= n:
            break
        yield v

# Compute: first 5 even perfect squares
squares = map_gen(integers_from(0), lambda n: n * n)
even_squares = filter_gen(squares, lambda n: n % 2 == 0)
result = list(take_gen(even_squares, 5))
print(f"First 5 even squares: {result}")

# Compare memory: eager vs lazy
eager = [n*n for n in range(10000) if (n*n) % 2 == 0][:5]
print(f"Eager (computed 10000, kept 5): {eager}")
print(f"Lazy (computed exactly 5): {result}")
print("Both produce the same answer; lazy is O(1) memory.")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

**Exercise 2.** Implement a cooperative multitasking scheduler using generators. Each "task" is a generator that yields to give up control. The scheduler runs tasks in round-robin:

```python
def task_a():
    for i in range(3):
        print(f"  task_a: step {i}")
        yield   # give up control

def task_b():
    for i in range(4):
        print(f"  task_b: step {i}")
        yield   # give up control

def scheduler(*tasks):
    """Round-robin cooperative scheduler."""
    active = [t() for t in tasks]
    while active:
        next_round = []
        for gen in active:
            try:
                next(gen)   # run task until its next yield
                next_round.append(gen)
            except StopIteration:
                print(f"  [task finished]")
        active = next_round

print("=== Cooperative multitasking with generators ===")
scheduler(task_a, task_b)
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

**Exercise 3.** Implement a `memoize_gen` that caches yielded values so that the generator can be replayed from the beginning without recomputing:

```python
class ReplayableGen:
    def __init__(self, gen_fn, *args, **kwargs):
        self._gen_fn = gen_fn
        self._args = args
        self._kwargs = kwargs
        self._cache = []
        self._gen = gen_fn(*args, **kwargs)
        self._done = False
    
    def __iter__(self):
        idx = 0
        while True:
            if idx < len(self._cache):
                yield self._cache[idx]
            elif self._done:
                return
            else:
                try:
                    val = next(self._gen)
                    self._cache.append(val)
                    yield val
                except StopIteration:
                    self._done = True
                    return
            idx += 1

def expensive_gen(n):
    for i in range(n):
        print(f"  [computing {i}]")
        yield i * i

rg = ReplayableGen(expensive_gen, 4)

print("First pass (computes each value):")
for v in rg:
    print(f"  got {v}")

print()
print("Second pass (reads from cache, no recomputation):")
for v in rg:
    print(f"  got {v}")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

**Exercise 4.** Extend the mini interpreter from Model 5 to support a `while` loop inside generator bodies. Add a `While` AST node and a `Assign` node so you can write:

```
gen count_up(start):
    while start <= 5:
        yield start
        start = start + 1
```

```python
from dataclasses import dataclass
from typing import Any

@dataclass
class Num:
    value: float

@dataclass  
class Var:
    name: str

@dataclass
class BinOp:
    op: str
    left: Any
    right: Any

@dataclass
class Compare:
    op: str
    left: Any
    right: Any

@dataclass
class Yield_:
    value: Any

@dataclass
class Assign:
    name: str
    value: Any

@dataclass
class While:
    condition: Any
    body: list

@dataclass
class GeneratorDef:
    param: str
    body: list

class Env:
    def __init__(self, parent=None):
        self.bindings = {}
        self.parent = parent
    def lookup(self, name):
        if name in self.bindings: return self.bindings[name]
        if self.parent: return self.parent.lookup(name)
        raise NameError(f"undefined: {name!r}")
    def define(self, name, val):
        self.bindings[name] = val
    def assign(self, name, val):
        if name in self.bindings:
            self.bindings[name] = val
            return
        if self.parent:
            self.parent.assign(name, val)
            return
        raise NameError(f"assign to undefined: {name!r}")

def eval_node(node, env):
    if isinstance(node, Num): return node.value
    if isinstance(node, Var): return env.lookup(node.name)
    if isinstance(node, BinOp):
        l, r = eval_node(node.left, env), eval_node(node.right, env)
        return {"+": l+r, "-": l-r, "*": l*r}[node.op]
    if isinstance(node, Compare):
        l, r = eval_node(node.left, env), eval_node(node.right, env)
        return {"<=": l<=r, "<": l<r, ">=": l>=r}[node.op]
    if isinstance(node, Assign):
        val = eval_node(node.value, env)
        env.assign(node.name, val)
        return val
    if isinstance(node, Yield_):
        return ("yield", eval_node(node.value, env))
    if isinstance(node, While):
        while eval_node(node.condition, env):
            for stmt in node.body:
                result = eval_node(stmt, env)
                if isinstance(result, tuple) and result[0] == "yield":
                    yield result[1]
        return
    raise ValueError(f"unknown: {node!r}")

def run_generator(gen_def: GeneratorDef, arg, parent_env):
    env = Env(parent=parent_env)
    env.define(gen_def.param, arg)
    for stmt in gen_def.body:
        yield from run_node_yielding(stmt, env)

def run_node_yielding(node, env):
    if isinstance(node, Yield_):
        yield eval_node(node.value, env)
    elif isinstance(node, While):
        while eval_node(node.condition, env):
            for stmt in node.body:
                yield from run_node_yielding(stmt, env)
    elif isinstance(node, Assign):
        eval_node(node, env)

# count_up(start): while start <= 5: yield start; start = start + 1
global_env = Env()
count_up = GeneratorDef(
    param="start",
    body=[
        While(
            condition=Compare("<=", Var("start"), Num(5)),
            body=[
                Yield_(Var("start")),
                Assign("start", BinOp("+", Var("start"), Num(1)))
            ]
        )
    ]
)

print("count_up(1):")
for val in run_generator(count_up, 1, global_env):
    print(f"  {val}")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

**Exercise 5.** Implement a simple async event loop using generators. Create a `Task` class, an `EventLoop` that runs tasks cooperatively, and simulate I/O with time-delayed wake-ups:

```python
import time
from dataclasses import dataclass, field
from typing import Any, List, Callable

@dataclass
class Future:
    result: Any = None
    done: bool = False
    callbacks: List[Callable] = field(default_factory=list)
    
    def set_result(self, value):
        self.result = value
        self.done = True
        for cb in self.callbacks:
            cb(value)

class SimpleEventLoop:
    def __init__(self):
        self._ready = []       # (gen, send_value) pairs
        self._sleeping = []    # (wake_time, gen) pairs
    
    def call_soon(self, gen, value=None):
        self._ready.append((gen, value))
    
    def call_later(self, delay, gen):
        self._sleeping.append((time.monotonic() + delay, gen))
    
    def run(self, coro):
        gen = coro()
        self.call_soon(gen)
        
        while self._ready or self._sleeping:
            # Wake up sleeping tasks
            now = time.monotonic()
            still_sleeping = []
            for wake_time, gen in self._sleeping:
                if now >= wake_time:
                    self.call_soon(gen)
                else:
                    still_sleeping.append((wake_time, gen))
            self._sleeping = still_sleeping
            
            # Run ready tasks
            if self._ready:
                gen, value = self._ready.pop(0)
                try:
                    signal = gen.send(value)
                    if isinstance(signal, tuple) and signal[0] == "sleep":
                        self.call_later(signal[1], gen)
                except StopIteration:
                    pass

def sleep(seconds):
    """Our language's equivalent of asyncio.sleep."""
    yield ("sleep", seconds)

def fake_io_task(name, delay):
    print(f"  [{time.monotonic():.3f}] {name} starting")
    yield from sleep(delay)
    print(f"  [{time.monotonic():.3f}] {name} done after {delay}s")
    return f"result from {name}"

def main_coro():
    yield from fake_io_task("task_A", 0.03)
    yield from fake_io_task("task_B", 0.02)
    print("  all tasks done")

print("=== Simple generator-based event loop ===")
loop = SimpleEventLoop()
loop.run(main_coro)
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

---

## Reflection

1. Generators, coroutines, and async/await are all variations on the same idea: pausable computation. Map each to a concept from the CPS activity: where is the continuation stored in each case?

2. Python added `async def` / `await` as dedicated syntax rather than using bare generators. What usability problem did this solve? What did it give up?

3. Your interpreter currently evaluates expressions to completion. If you wanted to add generator support to your language, where in the evaluation pipeline would the most significant changes go? What data structure would you need to add?

---

## Further Reading

- **Python docs:** Generator Expressions, `yield from`, `asyncio` event loop
- **PEP 255** — Simple Generators (the original Python generator proposal)
- **PEP 342** — Coroutines via Enhanced Generators (added `send`, `throw`, `close`)
- **PEP 3156** — Asynchronous I/O Support (asyncio)
- **Talk:** David Beazley, "Python Concurrency from the Ground Up" (PyCon 2015)
- **Talk:** David Beazley, "Generators: The Final Frontier" (PyCon 2014) — builds an event loop from scratch
- **Paper:** Moura & Ierusalimschy (2009), "Revisiting Coroutines" — theory of semi-coroutines vs full coroutines
- **Book:** *Crafting Interpreters* — Nystrom, Chapter 26 (closures → generators is a natural extension)

---

*End of Activity — Coroutines and Generators: yield, send, async/await, state machines, interpreter implementation*
