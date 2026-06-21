<!--
author:   CS374 Course Team
email:    
version:  0.0.1
language: en
narrator: US English Female
comment:  Memory Management — Call Stack, Heap, Reference Counting, Mark-and-Sweep, Generational GC, Interpreter Implications
import:   https://raw.githubusercontent.com/liaScript/coderunner/master/README.md
link:     https://cdn.jsdelivr.net/chartist.min.css
-->

# Memory Management: From Stack Frames to Garbage Collection

## Learning Goals

By the end of this activity, you will be able to:

- Trace the call stack through a recursive function call, drawing the frame layout (local variables, return address, parent-frame pointer) at each push and pop
- Distinguish stack allocation from heap allocation, and explain why closures, objects, and long-lived data must live on the heap
- Describe how CPython's reference-counting collector reclaims objects immediately on zero-reference and how a cycle-detector handles reference cycles that reference counting alone cannot collect
- Explain how generational garbage collection exploits the generational hypothesis to reduce pause times, and identify the implication for your interpreter's environment and AST-node allocation strategy

> **Prerequisites:** Python programming; familiarity with functions and recursion; basic familiarity with the interpreter project
> **Goal:** Understand how programs manage memory — call stacks, heap allocation, reference counting, mark-and-sweep GC, Python's generational collector — and what this means for your interpreter implementation.

**POGIL Roles:** Driver · Recorder · Reporter · Manager

---

# Part I: The Call Stack

## Model 1: Stack Frames and Recursive Calls

Every function call pushes a **frame** onto the call stack. Each frame holds:
- The function's local variables and parameters
- The return address (where execution resumes after the call returns)
- A link to the caller's frame

When a function returns, its frame is **popped** and memory is immediately reclaimed.

```python
import sys

def factorial(n, depth=0):
    indent = "  " * depth
    frame = sys._getframe()
    print(f"{indent}→ factorial({n})  [frame depth ~{depth}]")
    if n <= 1:
        result = 1
    else:
        result = n * factorial(n - 1, depth + 1)
    print(f"{indent}← returning {result}")
    return result

print("=== Call stack trace for factorial(5) ===")
print(f"Result: {factorial(5)}")
print()
print("=== Stack depth limit ===")
print(f"Python default recursion limit: {sys.getrecursionlimit()}")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

**Key observations:**
- Each recursive call creates a new frame; frames stack up during recursion.
- The stack is **LIFO**: last in, first out. Frames are popped in reverse order of creation.
- Python's default recursion limit is 1000 frames — exceeding it raises `RecursionError`.

> **Critical Thinking Questions 1–3**

**CTQ 1.** When `factorial(5)` calls `factorial(4)`, what four pieces of information are stored in the new stack frame for `factorial(4)`?

[[___ your answer here ___]]

**CTQ 2.** After `factorial(1)` returns `1`, in what order are the remaining frames popped? What does this tell you about LIFO order?

[[___ your answer here ___]]

**CTQ 3.** Tail-call optimization (TCO) allows compilers to reuse a stack frame for a tail-recursive call instead of pushing a new one. Python does NOT implement TCO. Give one design reason why Python's creators chose not to implement it.

[[___ your answer here ___]]

---

# Part II: The Heap

## Model 2: Heap Allocation and Object Identity

The **heap** is the region of memory where objects with dynamic lifetime are allocated. Unlike the stack (which is automatically managed by function calls/returns), heap objects live until explicitly freed or collected by a garbage collector.

In Python, every object — integers, strings, lists, class instances — lives on the heap. Variables are references (pointers) to heap objects.

```python
import sys

# Every Python object is on the heap
x = [1, 2, 3]
y = x           # y is an alias — same heap object
z = [1, 2, 3]   # z is a different heap object with the same value

print("=== Object identity (memory address) ===")
print(f"id(x) = {id(x)}")
print(f"id(y) = {id(y)}  (same as x? {id(x) == id(y)})")
print(f"id(z) = {id(z)}  (same as x? {id(x) == id(z)})")
print()

print("=== Mutation through alias ===")
y.append(4)
print(f"After y.append(4): x = {x}")  # x also changed!
print()

print("=== Object sizes on the heap ===")
objects = [42, 3.14, "hello", [1,2,3], {"a": 1}, (1,2)]
for obj in objects:
    print(f"  {repr(obj):<20}  sys.getsizeof = {sys.getsizeof(obj)} bytes")
print()

print("=== Small integer caching ===")
a = 256
b = 256
c = 257
d = 257
print(f"256 is 256: {a is b}")   # True — CPython caches -5..256
print(f"257 is 257: {c is d}")   # False — outside cache range
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

> **Critical Thinking Questions 4–6**

**CTQ 4.** `y = x` does NOT copy the list — it creates an alias. Draw a memory diagram showing `x`, `y`, and `z` as pointers to heap objects after all three assignments.

[[___ your answer here ___]]

**CTQ 5.** After `y.append(4)`, why does `x` also show `[1, 2, 3, 4]`? How does this relate to aliasing?

[[___ your answer here ___]]

**CTQ 6.** CPython caches small integers (-5 to 256) so that `a = 256; b = 256; a is b` is `True`. What memory optimization does this achieve? What problem could it cause if a programmer mistakenly uses `is` instead of `==` for value comparisons?

[[___ your answer here ___]]

---

# Part III: Reference Counting

## Model 3: Reference Counting — How CPython Frees Memory

CPython's primary memory management strategy is **reference counting**: every heap object carries a counter of how many references point to it. When the counter reaches zero, the object is immediately freed.

```python
import sys
import gc

class Tracked:
    def __init__(self, name):
        self.name = name
        print(f"  [+] {name} created")
    def __del__(self):
        print(f"  [-] {name} destroyed")

# We'll track reference counts manually using sys.getrefcount
# Note: getrefcount itself adds 1 (the argument reference), so subtract 1

print("=== Reference counting demo with a list ===")
lst = [10, 20, 30]
print(f"After creation:      refcount = {sys.getrefcount(lst) - 1}")

alias = lst
print(f"After alias = lst:   refcount = {sys.getrefcount(lst) - 1}")

another = alias
print(f"After another = ...: refcount = {sys.getrefcount(lst) - 1}")

del alias
print(f"After del alias:     refcount = {sys.getrefcount(lst) - 1}")

del another
print(f"After del another:   refcount = {sys.getrefcount(lst) - 1}")

print()
print("=== The cycle problem ===")
# Reference cycles prevent refcounting from freeing objects
gc.disable()   # disable cyclic GC so we can see the leak

a = {"name": "A"}
b = {"name": "B"}
a["other"] = b   # a → b
b["other"] = a   # b → a  (cycle!)

print(f"a refcount: {sys.getrefcount(a) - 1}")  # 2 (lst var + b["other"])
print(f"b refcount: {sys.getrefcount(b) - 1}")  # 2 (lst var + a["other"])

del a, b   # remove our variables — but cycle keeps counts at 1 each
print("del a, b: objects still alive (cycle holds count > 0)")
print(f"GC counts (unreachable cyclic objects): {gc.get_count()}")

gc.enable()
gc.collect()
print(f"After gc.collect(): {gc.get_count()}")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

**Key insight:** Reference counting is fast (immediate deallocation, no GC pauses for non-cyclic objects) but **cannot handle cycles**: if object A holds a reference to B and B holds a reference to A, both counts stay above zero even when neither is reachable from the program.

> **Critical Thinking Questions 7–9**

**CTQ 7.** When `del alias` is executed, what exactly happens to the reference count? Is the object freed at that point? Why or why not?

[[___ your answer here ___]]

**CTQ 8.** After `del a, b`, both `a` and `b` have reference count 1 (from the cycle). Draw the reference graph showing why neither object is freed.

[[___ your answer here ___]]

**CTQ 9.** Rust uses ownership and borrow-checking (compile-time) to achieve memory safety without any garbage collector. What does Rust *not* allow that Python does allow, in order to make this work?

[[___ your answer here ___]]

---

# Part IV: Mark-and-Sweep and Generational Collection

## Model 4: Mark-and-Sweep Garbage Collection

When reference counting fails (cycles), a **tracing garbage collector** is needed. The classic algorithm is **mark-and-sweep**:

1. **Mark phase:** Starting from all *roots* (global variables, stack variables), traverse all reachable objects and mark them.
2. **Sweep phase:** Scan the entire heap; any unmarked object is garbage and can be freed.

```python
# Simulate mark-and-sweep on a simple object graph
# Objects are dicts with an "id", "refs" (list of object ids), and "marked" flag

def build_heap():
    heap = {
        "A": {"id": "A", "refs": ["B", "C"], "marked": False},
        "B": {"id": "B", "refs": ["D"],      "marked": False},
        "C": {"id": "C", "refs": [],          "marked": False},
        "D": {"id": "D", "refs": ["D"],       "marked": False},  # self-loop
        "E": {"id": "E", "refs": ["F"],       "marked": False},  # unreachable
        "F": {"id": "F", "refs": ["E"],       "marked": False},  # cycle, unreachable
    }
    return heap

def mark(heap, obj_id):
    obj = heap[obj_id]
    if obj["marked"]:
        return   # already visited (handles cycles)
    obj["marked"] = True
    for ref in obj["refs"]:
        mark(heap, ref)

def sweep(heap):
    freed = []
    for obj_id, obj in list(heap.items()):
        if not obj["marked"]:
            freed.append(obj_id)
            del heap[obj_id]
    return freed

# Roots: A is reachable (e.g., a global variable); E, F are not
roots = ["A"]
heap = build_heap()

print("=== Before GC ===")
print(f"Heap objects: {sorted(heap.keys())}")
print()

print("=== Mark phase ===")
for root in roots:
    mark(heap, root)
for obj_id, obj in heap.items():
    status = "REACHABLE" if obj["marked"] else "UNREACHABLE"
    print(f"  {obj_id}: {status}")
print()

print("=== Sweep phase ===")
freed = sweep(heap)
print(f"Freed (garbage): {freed}")
print(f"Surviving objects: {sorted(heap.keys())}")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

**Why E and F are collected:** Even though E→F→E forms a cycle, neither is reachable from any root. The mark phase never visits them, so the sweep phase frees both.

> **Critical Thinking Questions 10–12**

**CTQ 10.** In the mark phase, what would happen if we did NOT check `if obj["marked"]: return`? Trace through object D (which has a self-loop) to show the problem.

[[___ your answer here ___]]

**CTQ 11.** The sweep phase scans the **entire heap**. For a program with 10 million live objects and 1000 pieces of garbage, how much work does a single GC cycle do? Why is this a concern for real-time or interactive applications?

[[___ your answer here ___]]

**CTQ 12.** Java's garbage collector uses **generational** collection to address the cost you identified in CTQ 11. What is the **generational hypothesis** that makes this optimization valid?

[[___ your answer here ___]]

---

## Model 5: Python's Generational GC and the `gc` Module

Python uses **two complementary strategies**:

1. **Reference counting** (primary): frees most objects immediately when their count hits zero.
2. **Cyclic GC** (secondary): handles cycles that reference counting misses.

The cyclic GC is **generational**, dividing objects into three generations:

- **Generation 0 (young):** Newly allocated objects. Collected frequently — every ~700 net allocations by default.
- **Generation 1 (middle-aged):** Objects that survived one gen-0 collection. Collected less often.
- **Generation 2 (old):** Objects that survived a gen-1 collection. Collected rarely.

When a generation is collected, any object that survives is **promoted** to the next generation. The intuition: if an object survived the first sweep, it is likely to survive many more, so it costs less to scan it infrequently.

**CPython's full strategy:**

1. **Primary mechanism: reference counting.** Every `Py_INCREF`/`Py_DECREF` in the C runtime. Frees most objects immediately.
2. **Secondary mechanism: cyclic GC (`gc` module).** Handles the reference cycles that refcounting misses. Uses a variant of mark-and-sweep restricted to objects that could participate in cycles (containers: lists, dicts, class instances, closures).

The combination means most memory is freed instantly (no GC pause for non-cyclic objects), and cycles are collected periodically by the generational collector.

```python
import gc
import sys

print("=== Python's generational GC configuration ===")
print(f"GC enabled: {gc.isenabled()}")
thresholds = gc.get_threshold()
print(f"Thresholds: gen0={thresholds[0]}, gen1={thresholds[1]}, gen2={thresholds[2]}")
print(f"  Meaning: gen0 collected after {thresholds[0]} (allocs - frees)")
print(f"           gen1 collected after {thresholds[1]} gen0 collections")
print(f"           gen2 collected after {thresholds[2]} gen1 collections")

print()
stats = gc.get_stats()
for i, s in enumerate(stats):
    print(f"  gen{i}: collections={s['collections']}, "
          f"collected={s['collected']}, "
          f"uncollectable={s['uncollectable']}")

print()
print("=== Demonstrating cycle collection ===")

class CyclicNode:
    def __init__(self, name):
        self.name = name
        self.other = None
    def __repr__(self):
        return f"Node({self.name})"

# Disable GC to show raw refcounting cannot handle cycles
gc.disable()
counts_before = gc.get_count()
print(f"counts before creating cycle: {counts_before}")

n1 = CyclicNode("X")
n2 = CyclicNode("Y")
n1.other = n2
n2.other = n1

del n1, n2   # refcounting cannot free them; cycle keeps counts > 0
counts_after = gc.get_count()
print(f"counts after del (GC disabled, cycle leaked): {counts_after}")

gc.enable()
collected = gc.collect(0)   # force gen0 collection
print(f"gc.collect(0) freed {collected} objects from the cycle")

print()
print("=== Reference count live demo ===")
lst = [1, 2, 3]
print(f"refcount of [1,2,3]:  {sys.getrefcount(lst) - 1}")
a = lst
print(f"after a = lst:        {sys.getrefcount(lst) - 1}")
del a
print(f"after del a:          {sys.getrefcount(lst) - 1}")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

> **Critical Thinking Questions 13–15**

**CTQ 13.** The generational hypothesis says most objects die young. Give two concrete examples of short-lived objects your interpreter creates during evaluation, and one example of a long-lived object.

[[___ your answer here ___]]

**CTQ 14.** Python collects gen0 after every 700 net allocations. Why is this threshold not 1 (collect after every allocation) and not 1,000,000 (almost never)?

[[___ your answer here ___]]

**CTQ 15.** Why does CPython's cyclic GC only consider "container" objects (lists, dicts, sets, class instances) and not integers or strings?

[[___ your answer here ___]]

---

# Part V: Implications for Your Interpreter

## Model 6: Interpreter Memory on the Host Heap

Your interpreter is written in Python. Every data structure you create — `Environment` objects, `Closure` objects, AST nodes — is a Python heap allocation. Python's own garbage collector manages them. This section explores what that means for interpreter memory behavior.

```python
import sys
import gc
from dataclasses import dataclass, field
from typing import Any, Optional, Dict

@dataclass
class Environment:
    bindings: Dict[str, Any] = field(default_factory=dict)
    parent: Optional['Environment'] = None

    def lookup(self, name: str) -> Any:
        if name in self.bindings:
            return self.bindings[name]
        if self.parent is not None:
            return self.parent.lookup(name)
        raise NameError(f"undefined: {name!r}")

@dataclass
class Closure:
    param: str
    body: str    # simplified: just a label
    env: Environment

print("=== Building a chain of 5 environments (simulating 5 nested calls) ===")
env = None
for i in range(5):
    new_env = Environment(bindings={f"x{i}": i * 10}, parent=env)
    env = new_env
    print(f"  env{i}: ~{sys.getsizeof(new_env)} bytes (dataclass shell only), x{i}={i*10}")

print(f"\nLooking up x0 from deepest env requires 5 parent-chain hops:")
print(f"  x0 = {env.lookup('x0')}")

# A closure captures its entire defining environment chain
closure = Closure("n", "n * n", env)
print(f"\nClosure object shell: ~{sys.getsizeof(closure)} bytes")
print("But the closure keeps the ENTIRE env chain alive via the .env pointer.")
print("If the env chain is large, the closure is a large memory root.")

# Demonstrate that the env chain stays alive as long as the closure lives
print("\n=== Releasing the env chain directly ===")
env_top = env
del env, new_env
gc.collect()
print("  del env, new_env -- but closure still holds a ref to the top env!")
print(f"  env still reachable via closure.env: {closure.env.bindings}")

print("\n=== Releasing the closure releases the chain ===")
del closure, env_top
gc.collect()
print("  gc.collect() done -- chain is now freed (no more live references).")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

The critical insight: your interpreter creates a new `Environment` Python object for every function call and every `let` binding. Each `Environment` holds a reference to its parent. A closure holds a reference to the environment where it was defined. Therefore:

- A deeply recursive program builds a long chain of `Environment` objects on Python's heap.
- A closure defined inside a deeply nested scope keeps that entire chain alive.
- If you store closures in long-lived data structures (e.g., a list of callbacks), all the environments those closures captured live as long as the list does.

> **Critical Thinking Questions 16–18**

**CTQ 16.** Your interpreter creates a new `Environment` object for every function call. Why does this mean a deeply recursive program can exhaust heap memory even if the Python call stack hasn't overflowed?

[[___ your answer here ___]]

**CTQ 17.** A closure captures its defining environment. If a function defined at top level closes over a large module-level dictionary, will that dictionary be freed when the function is no longer used? Why or why not?

[[___ your answer here ___]]

**CTQ 18.** Connect to language design: what is the tradeoff between **closures that capture by reference** (Python style — the env binding is shared) versus **closures that capture by value** (copy the binding on creation)?

[[___ your answer here ___]]

---

## Critical Thinking Questions — Synthesis

**CTQ 19.** Place the three memory management strategies (reference counting, mark-and-sweep, manual `malloc`/`free`) in order from highest to lowest on each axis: (a) programmer cognitive burden, (b) risk of use-after-free bugs, (c) risk of memory leaks from cycles, (d) GC pause latency.

[[___ your answer here ___]]

**CTQ 20.** Rust eliminates all three strategies in favor of compile-time ownership. What does Rust's ownership system prevent that the other three strategies rely on?

[[___ your answer here ___]]

---

## Multiple Choice Review

**Question 1.** Python's reference counting immediately frees an object when:

- [( )] The `del` keyword is used on any name bound to the object
- [(X)] The object's reference count drops to zero
- [( )] The garbage collector's mark phase marks it as dead
- [( )] The object goes out of lexical scope

**Question 2.** Which of the following CANNOT be freed by reference counting alone?

- [( )] A string with one reference
- [( )] A list appended to another list
- [(X)] Two objects that reference each other but are reachable from no root
- [( )] A function object stored in a local variable

**Question 3.** In Python's generational GC, generation 0 objects are:

- [(X)] Newly allocated; collected most frequently
- [( )] Long-lived; collected most frequently
- [( )] Collected only when the program exits
- [( )] Objects that have survived at least two collections

**Question 4.** In the mark-and-sweep algorithm, the **sweep phase**:

- [( )] Traverses all live references from the roots
- [(X)] Frees every heap object that was not marked as reachable
- [( )] Updates reference counts for each live object
- [( )] Compacts live objects to eliminate heap fragmentation

---

## Exercises

**Exercise 1.** Modify the call stack simulation to track the maximum depth reached and the total number of frames pushed and popped. Try `factorial(10)` and `factorial(20)`:

```python
import sys

call_count = [0]
max_depth = [0]

def factorial(n, depth=0):
    call_count[0] += 1
    max_depth[0] = max(max_depth[0], depth)
    if n <= 1:
        return 1
    return n * factorial(n - 1, depth + 1)

for n in [5, 10, 15]:
    call_count[0] = 0
    max_depth[0] = 0
    result = factorial(n)
    print(f"factorial({n}) = {result}, calls={call_count[0]}, max_depth={max_depth[0]}")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

**Exercise 2.** Demonstrate aliasing vs. copying. Show that `list.copy()` creates a shallow copy (aliases inner objects) but `copy.deepcopy()` creates a fully independent copy:

```python
import copy

original = [[1, 2], [3, 4]]
shallow  = original.copy()
deep     = copy.deepcopy(original)

original[0].append(99)

print(f"original: {original}")
print(f"shallow:  {shallow}")   # inner list IS shared
print(f"deep:     {deep}")      # fully independent
print()
print(f"shallow[0] is original[0]: {shallow[0] is original[0]}")
print(f"deep[0]    is original[0]: {deep[0]    is original[0]}")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

**Exercise 3.** Build a reference-counting simulation. Implement an `RCObject` class with `inc_ref`, `dec_ref`, and `__del__` tracking. Create a cycle and show it leaks under pure refcounting:

```python
class RCObject:
    _registry = {}
    _next_id = [0]

    def __init__(self, name):
        self.name = name
        self.ref_count = 0
        self.refs = []
        RCObject._registry[name] = self

    def inc_ref(self):
        self.ref_count += 1

    def dec_ref(self):
        self.ref_count -= 1
        if self.ref_count == 0:
            print(f"  [freed] {self.name}")
            for r in self.refs:
                r.dec_ref()
            del RCObject._registry[self.name]

    def link(self, other):
        self.refs.append(other)
        other.inc_ref()

# Non-cyclic case
print("=== Non-cyclic: A → B ===")
a = RCObject("A")
b = RCObject("B")
a.inc_ref()   # root holds A
b.inc_ref()   # root holds B
a.link(b)
a.dec_ref()   # root drops A → A freed, then B freed
b.dec_ref()

print()
print("=== Cyclic: X ↔ Y (leak!) ===")
x = RCObject("X")
y = RCObject("Y")
x.inc_ref()   # root holds X
y.inc_ref()   # root holds Y
x.link(y)     # X → Y
y.link(x)     # Y → X  (cycle)
x.dec_ref()   # root drops X  -- X.ref_count = 1 (from Y), not freed
y.dec_ref()   # root drops Y  -- Y.ref_count = 1 (from X), not freed
print(f"Leaked: {list(RCObject._registry.keys())}")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

**Exercise 4.** Extend the mark-and-sweep simulation from Model 4 with a `compact` phase that renumbers objects after collection. Show that the freed slots are reusable:

```python
def build_heap():
    return {
        "A": {"refs": ["B", "C"], "marked": False, "data": "root"},
        "B": {"refs": ["D"],      "marked": False, "data": "live"},
        "C": {"refs": [],         "marked": False, "data": "live"},
        "D": {"refs": [],         "marked": False, "data": "live"},
        "E": {"refs": ["F"],      "marked": False, "data": "garbage"},
        "F": {"refs": ["E"],      "marked": False, "data": "garbage"},
    }

def mark(heap, obj_id, visited=None):
    if visited is None:
        visited = set()
    if obj_id in visited:
        return
    visited.add(obj_id)
    heap[obj_id]["marked"] = True
    for ref in heap[obj_id]["refs"]:
        mark(heap, ref, visited)

def sweep(heap):
    freed, live = [], []
    for obj_id in list(heap.keys()):
        if not heap[obj_id]["marked"]:
            freed.append(obj_id)
            del heap[obj_id]
        else:
            live.append(obj_id)
    return freed, live

heap = build_heap()
mark(heap, "A")
freed, live = sweep(heap)
print(f"Freed:    {freed}")
print(f"Survived: {live}")
print(f"Available slots for new allocations: {freed}")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

**Exercise 5.** Write an interpreter memory profiler: simulate evaluating 1000 calls of a function that returns a new list, and track how many `Environment` objects are alive at any point. Use `gc.get_objects()` to count live instances:

```python
import gc
from dataclasses import dataclass, field
from typing import Any, Optional, Dict

@dataclass
class Environment:
    bindings: Dict[str, Any] = field(default_factory=dict)
    parent: Optional['Environment'] = None

def count_envs():
    gc.collect()
    return sum(1 for obj in gc.get_objects() if isinstance(obj, Environment))

# Simulate a function that creates an env for each call but returns immediately
global_env = Environment(bindings={"pi": 3.14})

print(f"Before simulation: {count_envs()} Environment objects alive")

results = []
for i in range(100):
    call_env = Environment(bindings={"n": i}, parent=global_env)
    result = call_env.lookup("n") * call_env.lookup("pi")
    # call_env goes out of scope here — should be freed immediately

print(f"After 100 calls (no closures stored): {count_envs()} Environment objects")

# Now store closures that capture their envs
@dataclass
class Closure:
    param: str
    body: str
    env: Environment

closures = []
for i in range(100):
    call_env = Environment(bindings={"captured": i}, parent=global_env)
    closures.append(Closure("x", "captured + x", call_env))

print(f"After storing 100 closures: {count_envs()} Environment objects")
del closures
gc.collect()
print(f"After del closures: {count_envs()} Environment objects")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

---

## Reflection

1. Your interpreter evaluates programs by building `Environment` chains. Under what conditions might a user's program trigger **memory exhaustion** even though no single object is unusually large? Propose one mitigation strategy.

2. Python's reference counting gives **deterministic destruction** (objects die immediately when unreachable). Java's GC gives **non-deterministic destruction** (objects may linger). For a language that opens files in its `__del__` method, which strategy is safer? Why?

3. A production interpreter (CPython, JVM, V8) must balance: collection frequency, pause length, throughput, and memory overhead. Pick two of these and explain the fundamental tension between them.

---

## Further Reading

- **CPython memory management source:** `Objects/obmalloc.c`, `Modules/gcmodule.c`
- **Python docs:** `gc` module — `gc.collect()`, `gc.get_threshold()`, `gc.get_objects()`
- **Article:** *Garbage Collection for Python* — original design notes by Neil Schemenauer
- **Book:** *The Garbage Collection Handbook* — Jones, Hosking, Moss (definitive reference)
- **Rust ownership model:** *The Rust Programming Language*, Chapter 4 — Understanding Ownership

---

*End of Activity — Memory Management: Call Stack, Heap, Reference Counting, Mark-and-Sweep, Generational GC*
