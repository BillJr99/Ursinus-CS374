---
layout: tutorial
permalink: /Tutorials/GarbageCollection
title: "CS374: Garbage Collection, Memory Management from First Principles"

info:
  coursenum: CS374
  goals:
    - "Implemented a simulated heap in Python (a dictionary from address to object) supporting allocation and deallocation"
    - "Built a working reference-counting collector and demonstrated why it leaks cyclic structures"
    - "Built a working mark-and-sweep collector with a gray/black worklist and verified it reclaims cycles"
    - "Built a working Cheney copying collector and verified it compacts the live set into a clean semi-space"
    - "Chosen and justified a GC strategy for the final project's GC extension based on the tradeoffs of each algorithm"

tags:
  - memory
  - gc
  - project-extension

---
# Tutorial: Garbage Collection, Memory Management from First Principles

## Learning Goals

By the end of this tutorial, you will have:

- Implemented a simulated heap in Python (a dictionary from address to object) supporting allocation and deallocation
- Built a working reference-counting collector and demonstrated why it leaks cyclic structures
- Built a working mark-and-sweep collector with a gray/black worklist and verified it reclaims cycles
- Built a working Cheney copying collector and verified it compacts the live set into a clean semi-space
- Chosen and justified a GC strategy for the final project's GC extension based on the tradeoffs of each algorithm

Every interpreter allocates memory for values, closures, and environments, and must eventually reclaim memory that is no longer needed.  **Garbage collection** (GC) is automatic memory management: the runtime periodically finds and frees memory that is unreachable from the program's current state.  This tutorial builds three GC algorithms from scratch in Python (simulating a heap as a dictionary), explains why each works, and shows where each breaks down.  **Prerequisites:** Python interpreter assignment (environments and closures); the course's AST and evaluator.

---

## Part 0: Why Garbage Collection?

Your current Mini interpreter runs entirely in Python's memory space; Python's own GC handles cleanup.  For the final project's GC extension, you simulate explicit memory management: your interpreter has a **heap** (an array or dictionary of objects), and your GC must find and free objects that the running program can no longer reach.

Three main strategies exist:

| Strategy | When to collect | Cost | Handles cycles? |
|---|---|---|---|
| Reference counting | On every deallocation | Low (immediate) | No (cycles leak) |
| Mark-and-sweep | When heap is full | Medium (pause) | Yes |
| Copying (Cheney) | When semi-space fills | High (moving) | Yes |

---

## Part 1: Simulated Heap

All three algorithms share a common simulated heap: a dictionary from address (integer) to object, plus a free list.

```python
try:
    class Heap:
        def __init__(self, size=64):
            self.size = size
            self.memory = {}       # addr -> {'type': ..., 'fields': {...}}
            self.free = list(range(size))   # available addresses
            self.next_addr = 0
            self.alloc_count = 0

        def alloc(self, obj_type, **fields):
            if not self.free:
                raise MemoryError("heap full - GC needed")
            addr = self.free.pop(0)
            self.memory[addr] = {'type': obj_type, **fields}
            self.alloc_count += 1
            return addr

        def get(self, addr):
            return self.memory.get(addr)

        def free_addr(self, addr):
            if addr in self.memory:
                del self.memory[addr]
                self.free.append(addr)

        def live_count(self):
            return len(self.memory)

        def snapshot(self):
            return {a: dict(v) for a, v in self.memory.items()}

    # Test the heap
    h = Heap(8)
    a = h.alloc('pair', car=1, cdr=None)
    b = h.alloc('pair', car=2, cdr=a)
    c = h.alloc('num', value=42)
    print("Allocated:", h.live_count(), "objects")
    print("Object at b:", h.get(b))
    h.free_addr(c)
    print("After freeing c:", h.live_count(), "objects")

except Exception as e:
    print(f"[gc:heap] {e}")
    import traceback; traceback.print_exc()
```

---

## Part 2: Reference Counting

**Reference counting** tracks how many references point to each object.  When the count drops to zero, the object is immediately freed.

```python
try:
    class RCHeap:
        def __init__(self, size=64):
            self.memory = {}   # addr -> {type, fields, refcount}
            self.free = list(range(size))

        def alloc(self, obj_type, **fields):
            if not self.free:
                raise MemoryError("heap full")
            addr = self.free.pop(0)
            self.memory[addr] = {'type': obj_type, 'refcount': 0, **fields}
            return addr

        def inc_ref(self, addr):
            if addr is not None and addr in self.memory:
                self.memory[addr]['refcount'] += 1

        def dec_ref(self, addr):
            if addr is None or addr not in self.memory:
                return
            self.memory[addr]['refcount'] -= 1
            if self.memory[addr]['refcount'] <= 0:
                self._collect(addr)

        def _collect(self, addr):
            obj = self.memory.pop(addr, None)
            if obj is None: return
            self.free.append(addr)
            # Decrement refs to all fields
            for key, val in obj.items():
                if key not in ('type', 'refcount') and isinstance(val, int):
                    self.dec_ref(val)   # assume integer fields may be addresses
            print(f"  [RC] freed object at {addr} (type={obj['type']!r})")

        def live_count(self):
            return len(self.memory)

    # Demonstrate reference counting
    rc = RCHeap(16)

    # Create: a -> b -> c
    c = rc.alloc('num', value=99)
    rc.inc_ref(c)         # root holds c

    b = rc.alloc('pair', car=10, cdr=c)
    rc.inc_ref(b)         # root holds b
    rc.inc_ref(c)         # b.cdr holds c (c now has refcount 2)

    a = rc.alloc('pair', car=5, cdr=b)
    rc.inc_ref(a)         # root holds a
    rc.inc_ref(b)         # a.cdr holds b (b now has refcount 2)

    print("Live objects:", rc.live_count())

    # Drop root reference to a - triggers cascading collection
    print("\nDropping root reference to a:")
    rc.dec_ref(a)        # a's refcount -> 0, collect a; b's refcount -> 1
    print("Live after drop a:", rc.live_count())

    print("\nDropping root reference to b:")
    rc.dec_ref(b)        # b's refcount -> 0, collect b; c's refcount -> 1
    print("Live after drop b:", rc.live_count())

    print("\nDropping root reference to c:")
    rc.dec_ref(c)        # c's refcount -> 0, collect c
    print("Live after drop c:", rc.live_count())

except Exception as e:
    print(f"[gc:rc] {e}")
    import traceback; traceback.print_exc()
```

**The cycle problem.**  Reference counting cannot collect cycles:

```python
try:
    rc2 = RCHeap(16)

    # Create a cycle: a.cdr = b, b.cdr = a
    a = rc2.alloc('pair', car=1, cdr=None)
    b = rc2.alloc('pair', car=2, cdr=None)
    rc2.inc_ref(a); rc2.inc_ref(b)   # roots hold a and b
    rc2.memory[a]['cdr'] = b; rc2.inc_ref(b)   # a.cdr = b (b refcount 2)
    rc2.memory[b]['cdr'] = a; rc2.inc_ref(a)   # b.cdr = a (a refcount 2)

    print("Cycle live:", rc2.live_count())
    print("Dropping roots...")
    rc2.dec_ref(a)   # a refcount -> 1 (b still points to it) - NOT collected!
    rc2.dec_ref(b)   # b refcount -> 1 (a still points to it) - NOT collected!
    print("After dropping roots:", rc2.live_count(), "(cycle leaked!)")

except Exception as e:
    print(f"[gc:rc-cycle] {e}")
    import traceback; traceback.print_exc()
```

---

## Part 3: Mark-and-Sweep

Mark-and-sweep runs in two phases:
1.  **Mark:** start from all **root** references (stack variables, global env); recursively mark every reachable object.
2.  **Sweep:** free every object that was NOT marked.

```python
try:
    class MSHeap:
        def __init__(self, size=64):
            self.memory = {}   # addr -> object dict
            self.free_list = list(range(size))
            self.roots = set()   # addresses held by the "stack"

        def alloc(self, obj_type, **fields):
            if not self.free_list:
                self.collect()
                if not self.free_list:
                    raise MemoryError("out of memory after GC")
            addr = self.free_list.pop(0)
            self.memory[addr] = {'type': obj_type, 'marked': False, **fields}
            return addr

        def add_root(self, addr):
            self.roots.add(addr)

        def remove_root(self, addr):
            self.roots.discard(addr)

        def _get_children(self, obj):
            """Return all addresses referenced by obj's fields."""
            children = []
            for k, v in obj.items():
                if k not in ('type', 'marked') and isinstance(v, int) and v in self.memory:
                    children.append(v)
            return children

        def _mark(self):
            """Mark all reachable objects from roots."""
            worklist = list(self.roots)
            while worklist:
                addr = worklist.pop()
                obj = self.memory.get(addr)
                if obj is None or obj['marked']:
                    continue
                obj['marked'] = True
                worklist.extend(self._get_children(obj))

        def _sweep(self):
            """Free all unmarked objects; unmark the rest."""
            freed = 0
            for addr in list(self.memory.keys()):
                obj = self.memory[addr]
                if not obj['marked']:
                    del self.memory[addr]
                    self.free_list.append(addr)
                    freed += 1
                else:
                    obj['marked'] = False   # reset for next GC cycle
            return freed

        def collect(self):
            print(f"  [GC] starting mark-and-sweep ({len(self.memory)} live objects)")
            self._mark()
            freed = self._sweep()
            print(f"  [GC] swept {freed} objects, {len(self.memory)} remain")

        def live_count(self): return len(self.memory)

    # Demonstrate mark-and-sweep
    ms = MSHeap(16)

    # Create a small tree: root -> a -> b, root -> c (b and c share d)
    d = ms.alloc('leaf', value=99)
    b = ms.alloc('node', left=d, right=None)
    c = ms.alloc('node', left=d, right=None)
    a = ms.alloc('node', left=b, right=c)

    ms.add_root(a)

    # Create some garbage (not reachable from any root)
    g1 = ms.alloc('garbage', x=1)
    g2 = ms.alloc('garbage', x=2)
    print(f"Live before GC: {ms.live_count()} (includes 2 garbage objects)")

    ms.collect()
    print(f"Live after GC: {ms.live_count()} (garbage collected)")

    # Demonstrate cycle collection (the key advantage over RC)
    print("\nCycle collection:")
    x = ms.alloc('cyclic', peer=None)
    y = ms.alloc('cyclic', peer=x)
    ms.memory[x]['peer'] = y   # x <-> y cycle (neither reachable from root)
    print(f"Live with cycle: {ms.live_count()}")
    ms.collect()
    print(f"Live after GC: {ms.live_count()} (cycle collected!)")

except Exception as e:
    print(f"[gc:ms] {e}")
    import traceback; traceback.print_exc()
```

---

## Part 4: Cheney's Copying Collector

**Cheney's algorithm** divides the heap into two equal **semi-spaces**: `from-space` and `to-space`.  Live objects are *copied* from `from-space` to `to-space`, which compacts the heap as a side effect.

```python
try:
    class CheneyHeap:
        def __init__(self, semi_size=32):
            self.semi_size = semi_size
            # Two semi-spaces: offsets 0..semi_size-1 and semi_size..2*semi_size-1
            self.from_start = 0
            self.to_start = semi_size
            self.memory = {}   # addr -> obj
            self.bump = self.from_start   # bump pointer in from-space
            self.roots = {}    # name -> addr (variable name -> heap address)

        def alloc(self, obj_type, **fields):
            if self.bump >= self.from_start + self.semi_size:
                self.collect()
                if self.bump >= self.from_start + self.semi_size:
                    raise MemoryError("out of memory after GC")
            addr = self.bump
            self.bump += 1
            self.memory[addr] = {'type': obj_type, 'forwarded': None, **fields}
            return addr

        def add_root(self, name, addr):
            self.roots[name] = addr

        def remove_root(self, name):
            self.roots.pop(name, None)

        def _copy(self, addr):
            """Copy object at addr to to-space; return new address."""
            obj = self.memory.get(addr)
            if obj is None: return addr
            if obj['forwarded'] is not None:
                return obj['forwarded']   # already copied
            # Bump-allocate in to-space
            new_addr = self.to_bump
            self.to_bump += 1
            new_obj = {k: v for k, v in obj.items() if k != 'forwarded'}
            new_obj['forwarded'] = None
            self.memory[new_addr] = new_obj
            obj['forwarded'] = new_addr   # leave a forwarding pointer
            return new_addr

        def collect(self):
            print(f"  [Cheney] collecting ({self.bump - self.from_start} allocated)")
            self.to_bump = self.to_start

            # Copy roots
            for name in self.roots:
                self.roots[name] = self._copy(self.roots[name])

            # Scan copied objects and update their pointers (BFS via scan pointer)
            scan = self.to_start
            while scan < self.to_bump:
                obj = self.memory[scan]
                for key, val in list(obj.items()):
                    if key not in ('type', 'forwarded') and isinstance(val, int) and val in self.memory:
                        obj[key] = self._copy(val)
                scan += 1

            # Swap semi-spaces
            self.from_start, self.to_start = self.to_start, self.from_start
            self.bump = self.to_bump   # bump is now in the new from-space
            # Clear old from-space
            for addr in list(self.memory.keys()):
                if self.to_start <= addr < self.to_start + self.semi_size:
                    del self.memory[addr]
            live = self.bump - self.from_start
            print(f"  [Cheney] {live} live objects after GC")

        def live_count(self): return self.bump - self.from_start

    heap = CheneyHeap(8)
    x = heap.alloc('num', value=10)
    y = heap.alloc('pair', car=x, cdr=None)
    heap.add_root('y', y)

    # Allocate some garbage
    _ = heap.alloc('garbage', x=1)
    _ = heap.alloc('garbage', x=2)
    print(f"Before GC: {heap.bump - heap.from_start} objects allocated")

    heap.collect()
    print(f"After GC: root y is at addr {heap.roots['y']}")
    print(f"y = {heap.memory.get(heap.roots['y'])}")

except Exception as e:
    print(f"[gc:cheney] {e}")
    import traceback; traceback.print_exc()
```

---

## Part 5: Integrating GC into Your Mini Interpreter

To add GC to your Mini interpreter:

1.  **Replace Python objects with heap addresses.**  Instead of `Closure(params, body, env)` as a Python object, allocate a closure on your simulated heap: `heap.alloc('closure', params=params, body=body, env_addr=env_addr)`.  Your evaluator holds addresses, not objects.

2.  **Thread the heap through evaluation.**  Every `eval_expr(node, env, heap)` call takes and returns a heap (or mutates a global heap).  The result is an address, not a value.

3.  **Identify GC roots.**  The GC roots are the current environment chain (the live variable bindings).  Traverse the environment chain collecting all heap addresses; pass them as roots to `collect()`.

4.  **Call GC when the heap is full.**  In `heap.alloc(...)`, if the heap is full, call `collect()` with the current roots before trying again.

5.  **Measure live/dead object counts.**  Add logging to compare `live_count()` before and after each collection cycle.

```python
try:
    # Skeleton: a GC-aware evaluator for a tiny language
    # (simplified - fields stored as Python values for clarity)

    class GCAwareEval:
        def __init__(self, heap):
            self.heap = heap
            self.global_env = {}   # name -> heap address

        def alloc_num(self, v):
            return self.heap.alloc('num', value=v)

        def alloc_closure(self, params, body, env_snapshot):
            return self.heap.alloc('closure',
                params=tuple(params),
                body=id(body),    # store body reference (simplified)
                env=dict(env_snapshot))

        def get_roots(self, env):
            return set(v for v in env.values() if isinstance(v, int))

        def eval_num(self, n, env):
            return self.alloc_num(n)

        def eval_add(self, left_addr, right_addr):
            l = self.heap.memory.get(left_addr, {}).get('value', 0)
            r = self.heap.memory.get(right_addr, {}).get('value', 0)
            return self.alloc_num(l + r)

    # Quick smoke test with MSHeap
    ms = MSHeap(32)
    ev = GCAwareEval(ms)

    a_addr = ev.eval_num(21, {})
    b_addr = ev.eval_num(21, {})
    ms.add_root(a_addr); ms.add_root(b_addr)
    sum_addr = ev.eval_add(a_addr, b_addr)
    ms.add_root(sum_addr)

    # Remove operands (they are now garbage)
    ms.remove_root(a_addr); ms.remove_root(b_addr)
    ms.collect()
    print("After GC, sum =", ms.memory.get(sum_addr, {}).get('value'))

except Exception as e:
    print(f"[gc:eval] {e}")
    import traceback; traceback.print_exc()
```

---

## Summary: Choosing a Strategy

| | Reference Counting | Mark-and-Sweep | Cheney Copying |
|---|---|---|---|
| **Pause time** | None (incremental) | Stop-the-world | Stop-the-world |
| **Handles cycles** | No | Yes | Yes |
| **Memory overhead** | 1 word per object (refcount) | 1 bit per object (mark) | 50% of heap |
| **Heap fragmentation** | Yes (no compaction) | Yes (no compaction) | No (copies compact) |
| **Cache performance** | Poor (live objects scattered) | Poor | Good (live objects dense) |
| **Implementation complexity** | Low | Medium | Medium |
| **Used by** | Swift, Python (CPython), Rust Arc | Java (old GC), Ruby | Lua, many JVMs (young gen) |

Modern production GCs (Java G1, Go's GC, V8) combine all three ideas: reference counting for quick cleanup, generational copying for young objects, and mark-and-sweep for long-lived objects.

---

## Final Project: GC Extension Checklist

If you choose the GC extension for your final project:

- [ ] Replace direct Python object allocation with `heap.alloc(...)` in your evaluator
- [ ] Every value (numbers, strings, booleans, closures, lists, environments) lives on the heap as a record
- [ ] Implement `get_roots(env)` that traverses the current environment chain
- [ ] Implement either mark-and-sweep or Cheney copying (your choice; both qualify)
- [ ] Trigger GC when `heap.alloc` fails (heap full)
- [ ] Log: before GC, after GC, show live/dead counts
- [ ] Demonstrate with a program that allocates many temporary closures (e.g., a loop computing many values); GC keeps heap bounded
- [ ] For extra credit: implement cycle detection (cyclic data structure via mutable environments)

---

## Further Reading

- Wilson, Paul R. "Uniprocessor Garbage Collection Techniques" (1992).  The definitive survey of all algorithms, readable and thorough.
- Cheney, C.J. "A Nonrecursive List Compacting Algorithm" (1970, CACM).  The original two-page paper; one of the most elegant algorithms ever published.
- Jones, Richard et al. *The Garbage Collection Handbook* (CRC Press, 2011).  The modern comprehensive reference.
- Python's GC documentation: https://docs.python.org/3/library/gc.html: explains CPython's reference counting + generational cycle collector.
- Go GC guide: https://go.dev/doc/gc-guide: explains the tri-color mark-and-sweep used in Go's runtime.
