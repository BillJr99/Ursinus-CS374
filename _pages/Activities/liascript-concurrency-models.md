# Concurrency Models: Actors, Channels, and Transactions
<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://github.com/BillJr99/Ursinus-CS374-Fall2026/blob/gh-pages/_pages/Activities/liascript-concurrency-models.md or locally via https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374-Fall2026/gh-pages/_pages/Activities/liascript-concurrency-models.md

import: https://raw.githubusercontent.com/liascript/CodeRunner/master/README.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

# Concurrency Models: Actors, Channels, and Transactions

> **Opening Hook — The Restaurant Kitchen Analogy**
>
> Concurrency is like coordinating a busy kitchen. In a chaotic kitchen, all the chefs share the same pot — one chef adds salt while another stirs, and a third tastes to decide if it needs more. The result is unpredictable: the counter is wrong, the soup is over-salted, and nobody agrees on whose fault it is. This is **shared mutable state** — the root of race conditions, data corruption, and bugs that only appear under load. Language designers have proposed three main escapes: **actors** (each chef has their own station and their own pot; dishes are passed forward as finished items), **channels** (chefs communicate by placing items on a conveyor belt — the sender pauses until the receiver picks it up), and **transactions** (any chef can modify the shared pot, but changes only "commit" if nobody else changed the same ingredient in the meantime; otherwise the step is retried). All three approaches solve the same problem — coordinating concurrent work without chaos — but each imposes different constraints on how you structure your program.

## Learning Goals

By the end of this activity, you will be able to:

- Explain why shared mutable state causes data races, and demonstrate a race condition in Python using threads and a shared counter
- Implement the actor model using Python queues to pass immutable messages between independent workers, and explain how actors eliminate shared state
- Implement channel-based communication following the CSP model, distinguishing synchronous from buffered channels and explaining rendezvous semantics
- Compare actors, channels, and software transactional memory (STM) across the dimensions of composability, error handling, and suitability for different concurrency patterns

> **Before You Begin — Prerequisite Checklist**
>
> Before starting this activity, confirm you can answer yes to each of the following:
>
> - [ ] I know what a Python `threading.Thread` is and can write a program that starts two threads.
> - [ ] I understand that two threads running simultaneously can read and write the same variable, and I have a rough sense of why that is dangerous.
> - [ ] I have seen the word "mutex" or "lock" before, even if I have not used one in Python.
> - [ ] I completed (or reviewed) the Parallelism module, which established that pure functions are safe to parallelize.
>
> If any box is unchecked, review the Python `threading` documentation or the Parallelism activity before proceeding.

The Parallelism module showed that pure functions parallelize automatically — but programs also need *concurrency*: multiple activities interleaved in time, coordinating via communication. The language designer's central choice is **what primitive does the language expose for that coordination**? Three answers dominate modern languages: **actors** (Erlang, Akka) exchange immutable messages; **channels** (Go, Occam, CSP) synchronize on named conduits; **transactions** (Haskell STM, Clojure) compose atomic blocks. All three eliminate shared mutable state — but by different means, with different tradeoffs, suitable for different programs. The arc: **the coordination problem → actors → channels/CSP → STM → the π-calculus as foundation**.

---

## Directions and Group Roles

Work in your POGIL team with rotated roles (**Manager**, **Recorder**, **Presenter**, **Reflector**). Each Part is implemented in Python, but the focus is the *model*, not the API. The Recorder posts a comparison table at the end. After class, respond to the reflective prompt individually in your notebook.

---

# Part I: The Coordination Problem

## 1. Why Shared Memory Fails

**Intuition.** A single `counter.value += 1` looks atomic, but the processor actually executes three steps: (1) read the current value into a register, (2) add one, (3) write the result back. If two threads interleave these steps — thread A reads 42, thread B reads 42, thread A writes 43, thread B writes 43 — one increment is silently lost. This is a **race condition**: the program's output depends on the unpredictable timing of thread scheduling. Race conditions are notoriously hard to reproduce (they may appear only under heavy load) and hard to debug (adding print statements changes the timing enough to make them disappear). The model below demonstrates this concretely.

The Parallelism module established: pure functions are safe to parallelize. The hard part is the rest of the program — the stateful services, the shared counters, the bounded buffers. Shared mutable state under concurrency is the source of race conditions, deadlocks, and livelocks. Language designers have sought primitives that **eliminate** sharing as a root cause, rather than requiring programmers to manage it correctly with locks.

```python
try:
    import threading, time

    # Classic race condition: shared counter without synchronization
    class BrokenCounter:
        def __init__(self): self.value = 0
        def increment(self): self.value += 1   # read-modify-write: NOT atomic

    counter = BrokenCounter()
    threads = [threading.Thread(target=lambda: [counter.increment() for _ in range(1000)])
               for _ in range(10)]
    for t in threads: t.start()
    for t in threads: t.join()

    print(f"Expected: 10000, Got: {counter.value}  (deficit = {10000 - counter.value})")
    print("(Run multiple times to see non-determinism)")

except Exception as e:
    print(f"[conc:race] {e}")
    import traceback; traceback.print_exc()
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

> **Watch out!** CPython's Global Interpreter Lock (GIL) actually makes many Python race conditions *less* visible than they would be in Java or C++, because the GIL prevents two threads from executing Python bytecodes simultaneously. You may not always see the deficit above. But the race is still real — the GIL is released between bytecodes, not between the three steps of read-modify-write. For CPU-bound work or when using C extensions that release the GIL, races appear in full force.

---

# Part II: The Actor Model

## 2. Actors: No Sharing, Only Messages

**Intuition.** The actor model is the "each chef has their own station" solution. An actor is a tiny, self-contained process with its own private state and its own mailbox (an inbox queue). No other actor can reach in and modify that state — the only thing one actor can do to another is *drop a message in its mailbox*. The receiving actor picks up messages one at a time, processes each one, updates its own state, and optionally sends messages onward. Because nothing is shared, there are no races. Because messages are queued, no message is lost. The price: communication is asynchronous — the sender does not wait for a reply, which makes "call and wait for result" patterns more complex than a simple function call.

An **actor** is a unit of computation with:
- Its own **private state** (no other actor touches it)
- A **mailbox** (a queue of incoming messages)
- A **behavior** function: when a message arrives, compute new state and optionally send messages to other actors

This is Erlang's model (and Akka for JVM). Because no state is shared, there are no races. The only coordination is message passing — and messages are **copied** (or immutable) so the sender retains nothing.

```python
try:
    import threading, queue, time

    class Actor(threading.Thread):
        def __init__(self, name, behavior):
            super().__init__(daemon=True)
            self.name = name
            self.mailbox = queue.Queue()
            self.behavior = behavior
            self._state = {}
            self.start()

        def send(self, msg):
            self.mailbox.put(msg)

        def run(self):
            while True:
                msg = self.mailbox.get()
                if msg == 'STOP': break
                self._state = self.behavior(msg, self._state) or self._state

    # A counter actor: messages are ('increment',) or ('get', reply_actor)
    def counter_behavior(msg, state):
        count = state.get('count', 0)
        if msg[0] == 'increment':
            return {'count': count + 1}
        if msg[0] == 'get':
            msg[1].send(('value', count))   # reply to the requester
        return state

    # A "printer" actor that just prints what it receives
    def printer_behavior(msg, state):
        print(f"  [printer] received: {msg}")
        return state

    printer = Actor('printer', printer_behavior)
    counter = Actor('counter', counter_behavior)

    # Send 100 increment messages — no race condition possible
    for _ in range(100):
        counter.send(('increment',))

    # Request the final count
    time.sleep(0.05)   # let the actor process the increments
    counter.send(('get', printer))
    time.sleep(0.05)

    counter.send('STOP')
    printer.send('STOP')

except Exception as e:
    print(f"[conc:actor] {e}")
    import traceback; traceback.print_exc()
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

---

## Model 1: Actor Properties

**Intuition.** The code above shows a counter actor that is race-free by construction — not because of any lock, but because the counter's state (`state['count']`) is only ever read and written inside `counter_behavior`, which runs on a single thread (the actor's own thread). Any number of external threads can send `('increment',)` messages, but those messages are queued and processed one at a time. The mailbox *is* the synchronization primitive.

### Critical Thinking Questions

1. In the actor model, the counter's `count` variable is never shared — it lives only inside `counter_behavior`'s `state` dictionary. Why does this eliminate the race condition that the `BrokenCounter` had? What precisely is different?

2. The `get` message causes the counter to *send* a message back to the printer. This is **request-reply messaging**. How is this different from a function call that returns a value? (Hint: which is synchronous, which is asynchronous?)

3. **Fault tolerance.** Erlang's "let it crash" philosophy says: if an actor dies with an error, a *supervisor* actor restarts it. How does the mailbox abstraction enable this? What would happen to unprocessed messages if the actor crashes?

4. Two actors may send messages to each other simultaneously, causing a message in each mailbox. Neither blocks — they proceed. In a system with shared locks, both would instead wait for the other's lock: a **deadlock**. Explain why the actor model prevents this specific deadlock scenario structurally.

---

# Part III: Channels and CSP

## 3. Go-Style Channels: Synchronize on Communication

**Intuition.** Channels solve the coordination problem differently: instead of isolating state inside actors, channels give you a *meeting point* — a named conduit where one goroutine (or thread) can hand a value directly to another. With an unbuffered channel, the sender pauses until the receiver arrives at the channel to collect, and vice versa. The two parties *rendezvous* at the channel, synchronizing their progress. With a buffered channel of size N, the sender can deposit up to N items without waiting, and slows down only when the buffer is full. This back-pressure mechanism is what prevents a fast producer from overwhelming a slow consumer.

**Communicating Sequential Processes** (CSP, Tony Hoare 1978) and Go's channels take a different view: concurrency is about *synchronization points*. A **channel** is a typed conduit; a send blocks until a receiver is ready, and vice versa (for unbuffered channels). Coordination happens *at the moment of communication*, not via shared state.

```python
try:
    import threading, queue, time

    # Python queue as a Go-style channel (unbuffered = queue size 0)
    def make_chan(buffered=0):
        return queue.Queue(maxsize=buffered if buffered else 0)

    def go(fn, *args):
        t = threading.Thread(target=fn, args=args, daemon=True)
        t.start()
        return t

    # Producer/Consumer using channels
    def producer(ch, n):
        for i in range(n):
            ch.put(i)           # send to channel (blocks if full)
            print(f"  sent {i}")
        ch.put(None)            # sentinel

    def consumer(ch, results):
        while True:
            item = ch.get()     # receive from channel (blocks if empty)
            if item is None: break
            results.append(item * item)
            print(f"  received {item}, computed {item*item}")

    ch = make_chan(buffered=2)   # buffer of 2
    results = []

    p = go(producer, ch, 5)
    c = go(consumer, ch, results)

    p.join(); c.join()
    print("Squares:", results)

except Exception as e:
    print(f"[conc:chan] {e}")
    import traceback; traceback.print_exc()
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

> **Watch out!** It is tempting to think that buffered channels eliminate blocking entirely. They do not — they only defer it. A sender on a buffered channel of size 2 will still block on the *third* send if the receiver has not consumed anything yet. Removing back-pressure entirely (by using an unbounded buffer) can cause the producer to race arbitrarily far ahead, consuming memory without bound. Back-pressure is a feature, not a limitation.

**Select: waiting on multiple channels.** Go's `select` statement blocks until *any* of several channels is ready — the CSP choice operator. This is how event loops and multiplexers are written without callbacks.

```python
try:
    import threading, queue, time, random

    def make_chan(): return queue.Queue()

    def go(fn, *args):
        t = threading.Thread(target=fn, args=args, daemon=True)
        t.start()
        return t

    # Simulate a "select" on two channels by using a merge channel
    def merge(ch1, ch2, out):
        def relay(ch):
            while True:
                v = ch.get()
                if v is None:
                    out.put(None); break
                out.put(v)
        go(relay, ch1)
        go(relay, ch2)

    ticker = make_chan()
    sensor = make_chan()
    merged = make_chan()
    merge(ticker, sensor, merged)

    def send_ticks(ch):
        for i in range(3):
            time.sleep(0.01)
            ch.put(f"tick-{i}")
        ch.put(None)

    def send_sensors(ch):
        for i in range(3):
            time.sleep(0.015)
            ch.put(f"temp={20 + i}")
        ch.put(None)

    go(send_ticks, ticker)
    go(send_sensors, sensor)

    done = 0
    while done < 2:
        msg = merged.get()
        if msg is None:
            done += 1
        else:
            print(f"  received: {msg}")

except Exception as e:
    print(f"[conc:select] {e}")
    import traceback; traceback.print_exc()
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

---

## Model 2: Channels and CSP

**Intuition.** The `select` simulation above shows the fan-in pattern: two independent streams of events (ticks and sensor readings) are merged into one stream for a single consumer. In Go, `select` is built into the language; here we simulate it by spinning up relay threads. The key insight is that the *structure* of the communication topology — who sends to whom, through which channels, in what order — determines the program's concurrent behavior. CSP lets you reason about that structure precisely, which is why Go's concurrency model is considered one of the cleaner ones in production languages.

[[MC]]
In CSP/Go-style channels, an **unbuffered** channel's send operation blocks until a receiver is ready. What property does this enforce?
- ( ) The sender always finishes before the receiver starts
- (x) The send and receive happen simultaneously — the two goroutines/threads rendezvous at the channel
- ( ) Messages are dropped if no receiver is waiting
- ( ) The channel accumulates all messages until the receiver drains it

### Critical Thinking Questions

5. The actor model and CSP both eliminate shared state. What is the key difference in *when* coordination occurs? (Hint: actors are asynchronous by default; CSP channels synchronize at send.)

6. Deadlock is still possible with channels: goroutine A waits to send on `ch1` while goroutine B waits to send on `ch2`, and neither will receive the other's message. How does Go's `select` statement break this deadlock? What would the equivalent in actor-based code look like?

7. **Pipeline composition.** CSP channels compose naturally: `producer | transformer | consumer` where each stage reads from one channel and writes to another. Write the three-stage pipeline in pseudocode using channels. How does this compare to Unix pipes (`cat file | grep pattern | wc -l`)?

8. The `merge` function above creates a new output channel and relays from two inputs. This is the **fan-in** pattern. What is the **fan-out** pattern, and how would you implement it?

---

# Part IV: Software Transactional Memory

## 4. STM: Atomic Blocks Without Locks

**Intuition.** STM is the "optimistic" approach: let all the chefs work on their steps simultaneously, but at the moment each chef tries to commit their changes, check whether anyone else modified the same ingredient in the meantime. If so, undo the step and try again from scratch. If not, commit atomically. This is exactly how database transactions work, applied to in-memory variables. The key insight is that *conflicts are rare* in most programs, so the cost of occasionally retrying is lower than the cost of acquiring locks for every access. The critical constraint: the transaction body must be *pure* (no side effects like printing or writing to a file), because it may be executed more than once.

**Software Transactional Memory** (Haskell STM, Clojure refs) takes a third approach: allow threads to read and modify shared state, but inside **atomic transactions**. A transaction sees a consistent snapshot of memory; if two transactions conflict (both modified the same variable), one is *retried* automatically. No deadlocks: transactions don't hold locks, they just detect conflicts.

```python
try:
    import threading, time
    from copy import deepcopy

    # Minimal STM simulation: transactional references (TVar)
    class TVar:
        def __init__(self, value):
            self._value = value
            self._lock = threading.Lock()

        def read_committed(self):
            with self._lock: return self._value

        def write_committed(self, value):
            with self._lock: self._value = value

    class Transaction:
        def __init__(self):
            self._reads = {}    # TVar -> value at start
            self._writes = {}   # TVar -> new value

        def read(self, tvar):
            if tvar in self._writes: return self._writes[tvar]
            if tvar not in self._reads:
                self._reads[tvar] = tvar.read_committed()
            return self._reads[tvar]

        def write(self, tvar, value):
            self._writes[tvar] = value

        def commit(self):
            # Validate: check that read set hasn't changed
            for tvar, expected in self._reads.items():
                with tvar._lock:
                    if tvar._value != expected:
                        return False   # conflict — retry
            # Write
            for tvar, value in self._writes.items():
                tvar.write_committed(value)
            return True   # success

    def atomically(fn):
        """Run fn(transaction) atomically; retry on conflict."""
        attempts = 0
        while True:
            tx = Transaction()
            fn(tx)
            if tx.commit():
                return attempts + 1
            attempts += 1   # retry

    # Bank account transfer: atomically debit one, credit another
    alice = TVar(1000)
    bob   = TVar(500)

    def transfer(amount):
        def txn(tx):
            a = tx.read(alice)
            b = tx.read(bob)
            if a >= amount:
                tx.write(alice, a - amount)
                tx.write(bob, b + amount)
        return txn

    def do_transfer(amount, results, i):
        tries = atomically(transfer(amount))
        results[i] = (alice.read_committed(), bob.read_committed(), tries)

    results = [None] * 10
    threads = [threading.Thread(target=do_transfer, args=(50, results, i))
               for i in range(10)]
    for t in threads: t.start()
    for t in threads: t.join()

    print(f"Alice final: {alice.read_committed()}, Bob final: {bob.read_committed()}")
    print(f"Expected: Alice={1000-500}, Bob={500+500}")
    print(f"Total retries: {sum(r[2]-1 for r in results if r)}")

except Exception as e:
    print(f"[conc:stm] {e}")
    import traceback; traceback.print_exc()
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

---

## Model 3: Transactions and Composability

**Intuition.** The bank transfer code above shows STM's greatest strength: composability. The `transfer` function is built from two reads and two writes, but the whole thing commits as a single atomic unit. If you tried to achieve the same thing with two locks (`alice_lock` and `bob_lock`), you would face the classic deadlock: thread 1 acquires `alice_lock` and waits for `bob_lock`, while thread 2 acquires `bob_lock` and waits for `alice_lock`. STM sidesteps this entirely because transactions do not hold locks — they just record what they read, attempt a write, and retry if the world changed.

### Critical Thinking Questions

9. STM transactions can be composed: if `debit` and `credit` are each transactions, `transfer = debit AND credit` is also a transaction — and it is atomic as a unit. Why can't you compose lock-based operations this way? (What goes wrong if you write `def transfer(): debit_lock.acquire(); credit_lock.acquire(); ...`?)

10. If two transactions both read the same `TVar` and only one writes it, do they conflict? (Neither reads the other's write; both read the committed value.) What about two transactions both *writing* the same `TVar`? Which model do you think is correct, and why?

11. STM requires the transaction body to be **pure** (no irreversible side effects), because a retried transaction re-executes its body. What would go wrong if a transaction body printed to the console, and the transaction was retried 3 times?

12. Haskell's type system enforces STM purity: a `STM a` action can only be run inside `atomically`; it cannot perform IO. This is the same Curry-Howard connection as the IO monad — the type prevents the programmer from mixing transactional and effectful code. How does this relate to your interpreter's `ReturnSignal` exception: what would happen if a `return` statement inside a transaction could escape the transaction boundary?

---

# Part V: The π-Calculus — A Glimpse

## 5. Mobile Channels as a Formal Foundation

The **π-calculus** (Milner 1992) is to concurrent computation what the lambda calculus is to functional computation: a minimal formal system with one primitive (channel name) and one operation (send/receive a name over a channel). Names are *mobile* — you can send a channel name over a channel, so the communication topology can change at runtime. Every actor system and every channel-based language can be encoded in the π-calculus.

The syntax is minimal:

$$
P, Q ::=\; 0 \quad\mid\quad \bar{x}\langle y \rangle.P \quad\mid\quad x(z).P \quad\mid\quad P \mid Q \quad\mid\quad \nu x.P \quad\mid\quad !P
$$

- $0$: the idle process
- $\bar{x}\langle y \rangle.P$: send name $y$ on channel $x$, then continue as $P$
- $x(z).P$: receive a name on channel $x$, bind it to $z$, continue as $P$
- $P \mid Q$: $P$ and $Q$ running concurrently
- $\nu x.P$: create a fresh private channel $x$ for $P$
- $!P$: replicate $P$ (infinite server)

**The key reduction rule (communication):**

$$
\bar{x}\langle y \rangle.P \mid x(z).Q \;\rightarrow\; P \mid Q[z := y]
$$

When a sender on $x$ and a receiver on $x$ are running in parallel, they synchronize: the receiver's $z$ is replaced by $y$.

A function call $f(v)$ in the λ-calculus encodes as: send $v$ on channel $f$, where $f$ runs a receive. So the λ-calculus embeds in the π-calculus — concurrent computation subsumes sequential computation.

---

## Model 4: The π-Calculus

### Critical Thinking Questions

13. The π-calculus has no values, no numbers, no booleans — only channel names. Church numerals (from the Lambda Calculus activity) encode numbers as functions. How would you encode a "number" in the π-calculus? (Hint: encode it as a process that sends a fixed number of messages on a given channel.)

14. The rule $\bar{x}\langle y \rangle.P \mid x(z).Q \rightarrow P \mid Q[z := y]$ looks exactly like β-reduction: $(\lambda z. Q)\; y \rightarrow Q[z := y]$. What is the "function" here, and what is the "argument"? What is the "application"?

15. In the π-calculus, $\nu x.P$ creates a fresh private channel name — no process outside $P$ knows $x$. This is the formal counterpart of what language feature in your Mini interpreter? (Hint: think about local variables and scope.)

---

# Part VI: Comparison and Design Implications

## 6. Choosing a Concurrency Primitive

| | Actors | Channels (CSP) | STM |
|---|---|---|---|
| **Coordination** | Async message passing | Synchronous channel rendezvous | Optimistic locking with retry |
| **State sharing** | None (each actor owns state) | None (state flows through channels) | Shared, but transactional |
| **Deadlock** | Not possible (no blocking send) | Possible (channel misuse) | Not possible (no locks) |
| **Composability** | Hard (reply-to patterns) | Medium (fan-in/fan-out) | Easy (transactions compose) |
| **Side effects** | Allowed (actor's own state) | Allowed | Must be pure in transaction |
| **Used by** | Erlang, Elixir, Akka, Pony | Go, Occam, Rust (channels), Racket | Haskell STM, Clojure refs |

### Critical Thinking Questions

16. Your final project has a Concurrency extension option: `spawn expr` and `channel send/receive`. Based on today's models, which primitive would you choose to implement first — actors, channels, or STM — and why? What is the minimum viable implementation in Python?

17. All three models agree: **do not share mutable state**. Actors achieve this by encapsulation; channels achieve this by moving data through a conduit; STM achieves this by detecting and retrying conflicts. Which model requires the programmer to change their code structure the most? The least?

18. Rust's ownership system prevents data races at compile time by ensuring only one thread can hold a mutable reference at a time. In what sense is Rust's approach a *static* enforcement of the same principle all three concurrency models pursue *dynamically*?

---

# Exercises

1. **Actor calculator.** Implement a distributed calculator using actors: a `Parser` actor parses a string expression and sends the AST to an `Evaluator` actor, which sends the result to a `Printer` actor. Show that changing the Evaluator's behavior (e.g., to evaluate in floating-point instead of integer) requires no changes to Parser or Printer.

2. **Pipeline with back-pressure.** Implement a three-stage pipeline (producer → transformer → consumer) using buffered channels. Demonstrate **back-pressure**: the producer slows down when the transformer's input channel is full. Explain why this is automatically provided by buffered channels.

3. **STM bank invariant.** Extend the STM bank to enforce the invariant `alice + bob == 1500` (the total is conserved). Show that concurrent transfers never violate this invariant, even under retries. (Hint: check the invariant at the end of each transaction.)

4. **π-calculus encoding.** The λ-term `(λx. x)(5)` can be encoded in the π-calculus. Write the encoding: create a channel `fn`, a process that receives on `fn` and sends the result on a reply channel, and a process that sends `5` on `fn`. Show the reduction step that corresponds to β-reduction.

---

## Reflection Prompt

In your notebook: actors, channels, and STM all *eliminate* a feature (shared mutable state) rather than adding one. This is a recurring theme in language design — sometimes the best feature is one you cannot express. Lambda calculus has no mutation; Haskell's IO monad prevents mixing pure and impure code; STM prevents unsynchronized writes; Rust's ownership prevents dangling pointers. Is this style of design — **constraining the programmer for their own benefit** — fundamentally at odds with expressiveness? Give one example where the constraint paid off and one where it felt needlessly limiting.

---

## Further Reading

- Hoare, C.A.R. *Communicating Sequential Processes* (1985; free PDF at usingcsp.com). The foundational text; Go's channels implement this model.
- Armstrong, Joe. *Programming Erlang*, 2nd ed. (Pragmatic, 2013). Chapter 9 on fault-tolerant actor systems.
- Harris, Tim et al. "Composable Memory Transactions" (PPoPP 2005). The paper introducing Haskell STM with `retry` and `orElse`.
- Milner, Robin. *Communicating and Mobile Systems: The π-Calculus* (Cambridge, 1999). The foundational text on mobile processes.
- Go's concurrency tour: https://go.dev/tour/concurrency — interactive examples of channels and goroutines.
- Hewitt, Carl. "Actor Model of Computation" (1973). The original actor paper; free online.
