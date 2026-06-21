# Parallelism for Free: Functional Programming at Scale

<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://github.com/BillJr99/Ursinus-CS374-Fall2026/blob/main/_pages/Activities/liascript-functional-parallel.md

import: https://raw.githubusercontent.com/liascript/CodeRunner/master/README.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

# Parallelism for Free: Functional Programming at Scale

## Learning Goals

By the end of this activity, you will be able to:

- Explain why pure functions are trivially parallelizable and formally define the independence theorem for `map`
- Identify race conditions in shared-state concurrent code and contrast them with race-free functional equivalents
- Implement parallel data processing pipelines in Python using `multiprocessing` and `concurrent.futures`
- Construct a MapReduce computation by decomposing a problem into independent map phases and a reduction phase
- Compare the parallelism models of functional languages (Erlang, Haskell) with Python's multiprocessing approach and evaluate their tradeoffs

*"Pure functions are like electricity from nuclear power — you get massive energy with no visible moving parts, and purity is your containment vessel."*

Every processor you will touch for the rest of your career has multiple cores. The modern GPU has thousands of them. **The central promise of functional programming is that pure functions parallelize automatically**: if a function has no side effects and reads no shared state, two calls to it can run concurrently with zero synchronization. No mutexes. No race conditions. No deadlocks. This is not a minor convenience; it is a fundamental shift in how software scales.

In this module we trace that promise from the theory (why purity enables parallelism, mathematically) through the practice (Python's `multiprocessing`, `concurrent.futures`, and a worked MapReduce implementation) to the industrial scale at which functional languages like Erlang and Haskell operate. The authentic parallel assignment that follows this module asks you to parallelize a data processing pipeline over millions of records using only the tools you build here.

---

## Directions and Group Roles

Work in your POGIL team (**Manager, Recorder, Presenter, Reflector**). Individual sections are marked *Solo*; partner sections are marked *Pairs*; group sections are unmarked and require all four roles. Post the Recorder's shared answers to the Class Activity discussion.

---

# Part I: The Theory — Why Purity Enables Parallelism

## 1. The Race Condition, Formally

A **race condition** occurs when two threads read and write a shared variable, and the final value depends on the order of execution — an order the scheduler, not the programmer, controls. Race conditions are the central hazard of concurrent imperative programming, and they are notoriously hard to test for: the test passes because the scheduler happened to run threads in the right order that morning.

**A pure function cannot participate in a race condition.** The mathematical reason: a pure function $f$ satisfies $f(x) = f(x)$ for all $x$ at all times — its result is a function of its argument alone. No thread can change what $f(5)$ returns by writing to shared state, because $f$ reads no shared state. Two calls $f(5)$ and $f(7)$ are **independent** by construction; they can execute on two different cores with no coordination at all.

**The independence theorem for `map`:** If $f$ is pure, then

$$
\mathrm{map}(f, [x_1, x_2, \ldots, x_n])
$$

is *trivially parallelizable*: the $n$ applications $f(x_1), f(x_2), \ldots, f(x_n)$ have no dependencies between them and can execute in any order, or simultaneously, yielding the same result.

---

### Model 1: Pure vs. Impure Parallelism

```python
import threading

# ---- IMPURE: race condition ----
total_bad = 0
def add_to_total(x):
    global total_bad
    total_bad += x   # read-modify-write: NOT atomic!

threads = [threading.Thread(target=add_to_total, args=(i,)) for i in range(100)]
for t in threads: t.start()
for t in threads: t.join()
print("Impure sum (may be wrong):", total_bad)   # probably not 4950

# ---- PURE: no shared state ----
from functools import reduce
numbers = list(range(100))
pure_sum = reduce(lambda a, b: a + b, numbers, 0)
print("Pure sum (always correct):", pure_sum)   # always 4950
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

### Critical Thinking Questions — *Solo then Group*

1. Run the impure version several times. Does `total_bad` always equal 4950? Why or why not? What specific hardware interleaving causes the discrepancy?
2. The pure `reduce` is sequential. How is it *safer* than the threaded impure version even before parallelism enters the picture?
3. Identify the exact line in `add_to_total` that contains the race condition and explain why Python's GIL does NOT fully protect against it for all operations.

---

## 2. The MapReduce Pattern

**MapReduce** is the computational pattern that Google used to index the web, and that Hadoop, Spark, and modern cloud pipelines all implement. It has two phases:

1. **Map**: Apply a pure function to each element of a large dataset (parallelizable over all elements)
2. **Reduce**: Combine results using an associative operation (parallelizable as a tree)

The word count problem is the "Hello, World" of MapReduce. Given a corpus of documents:

- **Map**: each document → list of (word, 1) pairs
- **Shuffle** (sort by key — often handled by the framework)
- **Reduce**: for each unique word, sum the counts

```python
from functools import reduce
from collections import defaultdict

# A tiny corpus
corpus = [
    "the quick brown fox jumps over the lazy dog",
    "the dog barked at the fox",
    "quick brown foxes are quick",
]

# MAP: pure function, document -> (word, count) pairs
def word_map(document):
    return [(word, 1) for word in document.lower().split()]

# SHUFFLE: group by key (in real MapReduce, this is a distributed sort)
def shuffle(pairs):
    groups = defaultdict(list)
    for key, val in pairs:
        groups[key].append(val)
    return dict(groups)

# REDUCE: pure function, (key, [values]) -> (key, total)
def word_reduce(key_values):
    key, values = key_values
    return (key, reduce(lambda a, b: a + b, values, 0))

# Pipeline
all_pairs  = reduce(lambda a, b: a + b, map(word_map, corpus), [])
grouped    = shuffle(all_pairs)
word_count = dict(map(word_reduce, grouped.items()))

for word, count in sorted(word_count.items(), key=lambda x: -x[1])[:10]:
    print(f"  {word:15s}: {count}")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

---

### Critical Thinking Questions — *Pairs*

4. In the MapReduce pipeline above, which phases could run on different cores simultaneously? Draw a diagram showing which operations could overlap on a 4-core machine.
5. The reduce phase requires an **associative** operation. What would go wrong if we used subtraction instead of addition in the word-count reducer? Construct a concrete counterexample.
6. The shuffle/sort step is the bottleneck in distributed MapReduce. Why can't shuffle be parallelized as freely as map? What property of the sorted output makes it necessary to coordinate?

---

# Part II: The Practice — Python Multiprocessing

## 3. `multiprocessing.Pool.map`: The Parallel Map

Python's `multiprocessing` module spawns true OS processes, bypassing the GIL. `Pool.map(f, iterable)` is a parallel implementation of `map(f, iterable)`: it distributes the work across a pool of worker processes and collects results. Because each worker runs `f` on its slice of the data with no shared memory, the only requirement is that `f` is a **pure function** (or close enough — side effects to *separate* files are fine).

```python
import multiprocessing
import time
import math

def is_prime(n):
    """Pure function: no side effects, result depends only on n."""
    if n < 2: return False
    if n == 2: return True
    if n % 2 == 0: return False
    for i in range(3, int(math.sqrt(n)) + 1, 2):
        if n % i == 0:
            return False
    return True

numbers = list(range(100_000, 101_000))

# Sequential (always correct, always reproducible)
t0 = time.perf_counter()
seq_primes = [n for n in numbers if is_prime(n)]
t1 = time.perf_counter()
print(f"Sequential: {len(seq_primes)} primes in {t1-t0:.4f}s")

# Demonstrate: same pure function, same result regardless of execution order
# On a real machine: pool = multiprocessing.Pool(); results = pool.map(is_prime, numbers)
par_results = list(map(is_prime, numbers))   # identical logic, sequential for sandbox
par_primes  = [n for n, p in zip(numbers, par_results) if p]
assert seq_primes == par_primes
print(f"Pure function guarantee: {len(par_primes)} primes — result identical whether sequential or parallel ✓")
print("Key: is_prime reads only its argument → Pool.map(is_prime, numbers) is safe to parallelize")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

---

## 4. `concurrent.futures`: The High-Level Interface

`concurrent.futures.ProcessPoolExecutor` is the modern, higher-level parallel map. It uses the same process-pool model but with a cleaner interface that works well with `map`, `submit`, and `as_completed`.

```python
import math
import time

def compute_heavy(n):
    """CPU-bound: sum of square roots of all divisors of n."""
    return sum(math.sqrt(i) for i in range(1, n+1) if n % i == 0)

data = list(range(1, 200))

t0 = time.perf_counter()
results = list(map(compute_heavy, data))
t1 = time.perf_counter()
print(f"Sequential: {len(results)} values in {t1-t0:.4f}s")

# On a real machine with ProcessPoolExecutor:
#   with ProcessPoolExecutor() as ex:
#       results = list(ex.map(compute_heavy, data))
# Interface is identical — only execution location changes.

top5 = sorted(zip(data, results), key=lambda x: -x[1])[:5]
print("Top 5 by divisor-sqrt-sum:")
for n, v in top5:
    print(f"  n={n:3d}: {v:.4f}")
print()
print("compute_heavy is pure: no closures, no shared state → picklable, safe for ProcessPoolExecutor")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

---

### Try It: *Group Activity* — Parallel Word Count

Extend the MapReduce pipeline from Section 2 to use `Pool.map` for the map phase. The corpus should be a list of 1000 sentences (you can generate them). Measure the speedup. Report:
- Sequential time for map phase
- Parallel time for map phase
- Speedup ratio
- Whether results are identical (they must be)

---

# Part III: Haskell — Parallelism as a Library

## 5. Sparks and Strategies in Haskell

Haskell's purity guarantee enables the runtime to parallelize evaluation **automatically and safely**. The `Control.Parallel` module provides two primitives:

- `par :: a -> b -> b` — evaluate `a` in a separate spark (lightweight thread), return `b`
- `pseq :: a -> b -> b` — evaluate `a` to weak head normal form, then return `b`

These combine into **evaluation strategies** in `Control.Parallel.Strategies`:

```haskell
-- Standard parallel map in Haskell
import Control.Parallel.Strategies

parMap :: Strategy b -> (a -> b) -> [a] -> [b]
parMap strat f xs = map f xs `using` parList strat

-- Usage: parallel prime check
primes :: [Int] -> [Bool]
primes xs = parMap rdeepseq isPrime xs
  where
    isPrime n = n > 1 && all (\d -> n `mod` d /= 0) [2..floor (sqrt (fromIntegral n))]

-- Parallel Fibonacci (contrived but illustrative)
fib :: Int -> Int
fib 0 = 0
fib 1 = 1
fib n = let a = fib (n-1)
            b = fib (n-2)
        in  a `par` b `pseq` (a + b)
```

**Why this works:** Haskell's type system enforces purity at compile time. A function in the `IO` monad (which can have side effects) cannot be passed to `parMap rdeepseq`. The compiler's type checker is a proof that parallelism is safe.

**The key concept:** `par x y` evaluates `x` as a *spark* (a hint to the runtime that `x` can be evaluated on another core) while returning `y` immediately. It is not a command ("evaluate this now on a thread") but a *hint* that is safe because `x` being pure means its evaluation cannot affect `y`. The runtime optimizes spark scheduling.

---

## 6. Erlang and the Actor Model

Haskell uses shared-nothing processes with message passing; so does **Erlang**, the language built for massive concurrency in telephone switches (now WhatsApp, Discord, RabbitMQ). Erlang's model is:

- Processes are **ultra-lightweight** (millions can run concurrently)
- **No shared memory** between processes (functional data only)
- Communication via **message passing** with immutable messages
- **Let it crash**: processes are supervised; failures restart cleanly

```erlang
% Erlang: parallel map via spawning
-module(pmap).
-export([pmap/2]).

pmap(F, List) ->
    Parent = self(),
    Pids = [spawn(fun() -> Parent ! {self(), F(X)} end) || X <- List],
    [receive {Pid, Result} -> Result end || Pid <- Pids].

% Usage:
% pmap:pmap(fun(X) -> X * X end, [1, 2, 3, 4, 5]).
% returns [1, 4, 9, 16, 25]
```

The pattern — spawn one lightweight process per element, collect results via message passing — works with millions of elements because Erlang processes use ~300 bytes of memory each (versus ~8KB for a kernel thread).

---

### Critical Thinking Questions — *Group*

7. In Erlang's `pmap`, what guarantees that the `receive` loop collects results in the *same order* as the input list, even though processes might finish in different orders? (Hint: look at what is sent back.)
8. Compare Python's `multiprocessing.Pool.map` and Erlang's process-based `pmap`. Both achieve parallelism. What are three concrete differences in their cost model, and when would you prefer each?
9. Haskell's `par` is described as a "hint." What does it mean for a parallelism primitive to be a hint rather than a command, and what property of Haskell's semantics allows the hint to be safely ignored by the runtime?

---

# Part IV: Exercises — Building the Parallel Pipeline

## 7. Exercises

1. **Parallel image statistics.** Write a `parallel_map` that, given a list of 200 integers representing "pixel brightness" values, computes for each: whether it is above-average, its squared deviation from the mean, and its percentile rank (0-100). Implement this as a pure function on each pixel and run it in parallel. The mean must be computed sequentially first (why?), and the per-pixel computations are then independent. Report speedup.

2. **Word frequency pipeline.** Extend the MapReduce from Section 2 to handle a real text file (find a Project Gutenberg plain-text book). Use `Pool.map` for the map phase. Report: total unique words, top-20 most frequent, time comparison sequential vs. parallel.

3. **Parallel matrix multiply (conceptual).** Matrix multiplication $C = A \times B$ has $C_{ij} = \sum_k A_{ik} B_{kj}$. Show that computing each element $C_{ij}$ is a pure function of rows of $A$ and columns of $B$. Implement `par_matmul(A, B)` using `Pool.map` where the pure function computes one row of $C$. Verify on 50×50 random matrices that the result matches `np.dot(A, B)`.

4. **The cost of purity: profiling.** Pure functional style often creates extra copies of data rather than mutating in place. Write a benchmark that processes a list of one million integers in two ways: (a) functional style using `map` and `filter` chains; (b) imperative style using a single `for` loop with mutation. Measure wall-clock time and memory usage (`tracemalloc`). Discuss the tradeoff: when does the parallelizability of (a) outweigh its overhead, and at what input size does (b) win on a single core?

5. **Functional parallel design document.** You are designing a language feature for a new functional language that makes parallelism *explicit but safe*. Write a one-page design document: (a) the syntax for your parallel-map construct; (b) the type-system rule that ensures only pure functions can be parallelized; (c) how the compiler would detect purity statically; (d) one real-world pipeline (e.g., log analysis, image processing, ML feature extraction) that your construct would handle well. Use examples.

---

## 8. Reflection Prompt

The MapReduce pattern was invented at Google because sorting, grouping, and aggregating billions of records required spreading computation across thousands of machines without any of those machines sharing memory or state. Your sequential `reduce` from week 1 already had the right shape; only the "map" being pure was needed to scale it to a datacenter. In your notebook, write a paragraph about one domain you care about (biology, music, economics, sports analytics, social science) where a dataset is large enough that sequential processing is a bottleneck, and sketch the map function and reduce function that would parallelize it.

---

## 9. Further Reading

- Dean, Jeffrey and Sanjay Ghemawat. "MapReduce: Simplified Data Processing on Large Clusters." *OSDI '04*, USENIX, 2004. The original Google paper; beautifully written and accessible.
- Marlow, Simon. *Parallel and Concurrent Programming in Haskell* (O'Reilly, 2013). Free online. The definitive guide to `par`, `pseq`, and strategies.
- Armstrong, Joe. *Programming Erlang: Software for a Concurrent World* (Pragmatic Bookshelf, 2013). The creator of Erlang explains the actor model.
- Sutter, Herb. "The Free Lunch Is Over." *Dr. Dobb's Journal*, 2005. The foundational essay on why multicore requires a programming model change.
- Wadler, Philip. "Comprehending Monads." *Mathematical Structures in Computer Science* 2(4), 1992. Why the monad structure of `IO` in Haskell is what permits the type system to enforce purity and thus safe parallelism.
