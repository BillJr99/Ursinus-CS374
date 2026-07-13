<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://github.com/BillJr99/Ursinus-CS374-Fall2026/blob/gh-pages/_pages/Activities/liascript-automata.md or locally via https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374/gh-pages/_pages/Activities/liascript-automata.md

import: https://raw.githubusercontent.com/liascript/CodeRunner/master/README.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

# Finite Automata

Think of a turnstile at a subway station. It has exactly two states — **locked** and **unlocked** — and two transitions: inserting a coin moves it from locked to unlocked, and pushing moves it from unlocked back to locked. That tiny machine already captures the essence of a finite automaton: a fixed set of states, arrows triggered by input symbols, and a yes/no verdict at the end. The remarkable fact you will discover today is that this humble model is *exactly* as powerful as every regular expression you have ever written.

## Learning Goals

By the end of this activity, you will be able to:

- Define a DFA as a five-tuple and trace its execution on an input string, identifying the state after each symbol and determining acceptance or rejection
- Construct a DFA for a specified regular language by identifying the finite information the machine must track and assigning one state per distinguishable memory value
- Define an NFA and explain how it differs from a DFA in its transition function, including epsilon transitions
- Explain the subset construction argument for DFA-NFA equivalence and apply it to convert a small NFA into an equivalent DFA
- Implement a DFA simulator in Python using a transition table (dict of dicts) and connect the automaton model to the operation of a regex-based lexer

A regular expression *describes* a set of strings; a **finite automaton** *recognizes* one, a machine so simple it is just states and arrows, yet exactly as powerful as the regex notation. Over two days we build the machine view: **DFAs $\rightarrow$ NFAs $\rightarrow$ their surprising equivalence $\rightarrow$ simulation in Python**, the theory under your next assignment and the engine inside every lexer, including yours.

> **Before You Begin** — make sure you can:
> - Describe what a regular expression *denotes* (the set of strings it matches), not just write one
> - Create and look up values in a Python `dict`, including a dict whose values are themselves dicts
> - Trace a simple `for` loop by hand, tracking the value of one variable through each iteration

---

## Directions and Group Roles

Work in your POGIL team with rotated roles (**Manager**, **Recorder**, **Presenter**, **Reflector**). Consider each model and question individually first, then discuss with your group. The Recorder posts answers to the Class Activity Questions discussion board; the Presenter reports out areas of disagreement or alternative approaches. After class, respond to the reflective prompt individually in your notebook.

---

# Part I: Deterministic Finite Automata (Day 1)

## 1. The Machine

**A DFA is a five-tuple** $M = (Q, \Sigma, \delta, q_0, F)$: a finite set of states $Q$, an input alphabet $\Sigma$, a transition function $\delta: Q \times \Sigma \rightarrow Q$, a start state $q_0$, and accepting states $F \subseteq Q$. The machine reads the input one symbol at a time, moving deterministically; it **accepts** exactly when it finishes in an accepting state. The machine's entire memory is *which state it is in*: finitely many states, finite memory, hence the hierarchy's bottom rung.

A DFA accepting binary strings with an **even number of 1s**:

```
            0                0
          ┌───┐            ┌───┐
          ▼   │            ▼   │
   ──► ((even)) ──1──►  (odd)
          ▲                 │
          └───────1─────────┘
```

Two states suffice because the machine only needs to remember one bit: the parity so far.

---

## Model 1: Trace and Design

Before writing any code, you need to be comfortable *tracing* a DFA by hand — following the arrows one symbol at a time. The parity machine above is the ideal warm-up: it has only two states, so every transition is obvious, yet it handles an infinite set of strings correctly. Once tracing feels mechanical, designing your own DFA becomes a matter of asking "what is the minimum information I need to remember at each step?"

### Critical Thinking Questions

1. Trace `1011` through the parity DFA, listing the state after each symbol. Accepted or rejected? The Recorder writes the trace.
2. Design (draw) a DFA over $\{a, b\}$ accepting strings that **end in `ab`**. How many states did your team need, and what does each state "remember"?
3. Design a DFA accepting strings containing the substring `aa`. Compare with question 2: ending-in versus containing changes which states are accepting; articulate how.
4. Try to design a DFA for $a^n b^n$. Where does finite memory fail you, and which prior module predicted this?

---

## Model 2: DFA Simulation — A Dictionary and a Loop

The formal five-tuple maps almost directly onto a Python data structure: states become string keys, the transition function becomes a `dict` of `dict`s, and the entire simulation is a loop that does one dictionary lookup per character. Reading this code, notice that the *logic* never changes — only the data describing the machine does. That separation between the runner and the machine description is exactly the architecture your lexer assignment will use.

```python
# DFA as data: states are strings, delta is a dict of dicts.
# This representation is exactly what your Automata assignment generalizes.

EVEN_ONES = {
    "states": {"even", "odd"},
    "start": "even",
    "accept": {"even"},
    "delta": {
        "even": {"0": "even", "1": "odd"},
        "odd":  {"0": "odd",  "1": "even"},
    },
}

def run_dfa(machine, s, trace=False):
    state = machine["start"]
    if trace: print(f"  start: {state}")
    for ch in s:
        if ch not in machine["delta"].get(state, {}):
            if trace: print(f"  '{ch}': DEAD (no transition)")
            return False
        state = machine["delta"][state][ch]
        if trace: print(f"  '{ch}' → {state}")
    accepted = state in machine["accept"]
    if trace: print(f"  final: {state} → {'ACCEPT' if accepted else 'REJECT'}")
    return accepted

# Test the parity DFA
print("=== Even-ones DFA ===")
for s in ["", "1", "11", "1011", "0000", "10101", "abc"]:
    print(f"  {s!r:9} → {run_dfa(EVEN_ONES, s)}")

# Trace one input
print("\n=== Trace of '1011' ===")
run_dfa(EVEN_ONES, "1011", trace=True)

# Ends-in-ab DFA (4 states: start, saw_a, saw_ab, neither)
ENDS_IN_AB_DFA = {
    "start": "q0",
    "accept": {"q_ab"},
    "delta": {
        "q0":   {"a": "q_a",  "b": "q0"},
        "q_a":  {"a": "q_a",  "b": "q_ab"},
        "q_ab": {"a": "q_a",  "b": "q0"},
    },
}
print("\n=== Ends-in-ab DFA ===")
for s in ["ab", "aab", "abab", "ba", "a", "b", "aabb", ""]:
    print(f"  {s!r:7} → {run_dfa(ENDS_IN_AB_DFA, s)}")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

### Critical Thinking Questions

5. The empty string is accepted by `EVEN_ONES`. Point to the line of code and the part of the formal definition that together make that happen, and decide whether it is correct for "even number of 1s."
6. Encode your ends-in-`ab` DFA from Model 1 in the same dictionary format and test five strings. What was mechanical and what required thought? (That split is the point: the *design* is the thinking; the *runner* is ten lines forever.)
7. The `ENDS_IN_AB_DFA` has 3 states. If the target were "ends in `abc`", how many states would be needed, and what would each state remember?

---

# Part II: Nondeterminism and Equivalence (Day 2)

## 3. NFAs: Generous Machines

**A nondeterministic finite automaton (NFA)** relaxes the rules: a state may have *several* arrows for one symbol, *none*, and even **epsilon transitions** that move without consuming input ($\delta: Q \times (\Sigma \cup \{\varepsilon\}) \rightarrow \mathcal{P}(Q)$). An NFA accepts if **any** path of choices leads to acceptance, as if the machine explored all options in parallel. NFAs are usually far easier to design (the "ends in `ab`" NFA is just three states in a line with a self-loop), and they are what regular expressions compile into naturally: concatenation chains machines, `|` forks with epsilons, `*` loops back with epsilons (Thompson's construction).

**The punchline: NFAs are no more powerful.** The **subset construction** converts any NFA to a DFA whose states are *sets* of NFA states (tracking everywhere the NFA could be), giving:

$$
\text{regex} \equiv \text{NFA} \equiv \text{DFA}
$$

with a worst-case exponential blowup in state count ($2^{|Q|}$ subsets) as the price of determinism, a classic time-space-simplicity trade.

> **Watch out!** NFAs and DFAs recognize *exactly the same class of languages* — neither is more powerful. NFAs are simply more *compact to write*: the ends-in-`ab` NFA needs 3 states while the equivalent DFA needs 4. The equivalence is proven by the subset construction, not assumed.

[[MC]]
An NFA has 4 states. The subset-construction DFA recognizing the same language has at most:
- ( ) 4 states
- ( ) 8 states
- (x) 16 states, one per subset of the NFA's states
- ( ) Unboundedly many states

[[MC]]
The NFA "ends in ab" has 3 states: start/loop (q0), saw-a (q1), saw-ab (q2). The key non-determinism is at q0 on input 'a': the machine can stay in q0 (still looping) OR move to q1 (guessing the ending starts here). This non-determinism means:
- ( ) The machine will fail on inputs where multiple paths exist
- ( ) The machine requires exponential time to simulate
- (x) The machine accepts if ANY choice of path leads to an accepting state
- ( ) The machine requires the programmer to specify which path to take

---

## Model 3: NFA Simulation

Simulating an NFA does not require any magic or backtracking. Instead of tracking a single current state, the simulator tracks the *set* of all states the NFA could be in right now — every live path, simultaneously. Each input symbol advances every state in that set and unions the results. This is the subset construction running lazily, one character at a time, and it costs at most $O(k)$ work per symbol for a $k$-state NFA.

```python
{% raw %}
# NFA simulation by tracking the SET of possible states: the subset
# construction performed lazily, one input symbol at a time.

ENDS_IN_AB_NFA = {
    "start": frozenset({"q0"}),
    "accept": frozenset({"q2"}),
    "delta": {                       # sets of successor states
        ("q0", "a"): frozenset({"q0", "q1"}),  # loop OR guess ending starts
        ("q0", "b"): frozenset({"q0"}),
        ("q1", "b"): frozenset({"q2"}),
        # no transition from q2: it's a dead end (accepting, but no moves)
    },
}

def run_nfa(machine, s, trace=False):
    current = set(machine["start"])
    if trace: print(f"  start: {{{', '.join(sorted(current))}}}")
    for ch in s:
        nxt = set()
        for state in current:
            nxt |= machine["delta"].get((state, ch), frozenset())
        current = nxt
        if trace: print(f"  '{ch}' → {{{', '.join(sorted(current))}}}")
        if not current:
            if trace: print(f"  DEAD STATE (all paths exhausted)")
            return False
    accepted = bool(current & machine["accept"])
    if trace: print(f"  → {'ACCEPT' if accepted else 'REJECT'}")
    return accepted

print("=== NFA: ends-in-ab ===")
for s in ["ab", "aab", "abab", "ba", "a", "b", "aabb", ""]:
    print(f"  {s!r:7} → {run_nfa(ENDS_IN_AB_NFA, s)}")

print("\n=== Trace of 'aab' ===")
run_nfa(ENDS_IN_AB_NFA, "aab", trace=True)
{% endraw %}
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

> **Watch out!** An NFA does not "guess" which path to take — that framing makes it sound like luck is involved. The machine *explores all paths simultaneously*, and it accepts if *any* of them reaches an accepting state. The simulation above makes this concrete: `current` is always a set, never a single lucky choice.

### Critical Thinking Questions

8. Trace `aab` by hand, writing the *set* of states after each symbol. Where does the machine "hedge its bets," and which bet pays off?
9. Compare the NFA's three states with the DFA for the same language. Which was easier to design, and which is cheaper to run per input symbol?
10. The simulation tracks sets, so it effectively runs the subset construction on the fly. For an NFA with $k$ states, bound the work per input character ($O(k)$ per symbol). Why is this still considered fast?

---

## Model 4: Subset Construction — NFA → DFA

The subset construction is the key insight that connects NFAs to DFAs. Each DFA state corresponds to a *frozenset* of NFA states — "the set of places the NFA could be after reading this much input." The algorithm simply performs a reachability search over those sets, building the DFA transition table as it goes. Once you see the code, you will notice that Model 3's simulation was already doing this implicitly on every input string.

```python
# Full subset construction: convert an NFA to an equivalent DFA.
# DFA states = frozensets of NFA states.

def subset_construction(nfa):
    """Convert NFA to DFA via subset construction."""
    start = nfa["start"]  # already a frozenset
    dfa_states = {}       # frozenset → dict of transitions
    worklist = [start]
    visited = {start}

    while worklist:
        current_set = worklist.pop()
        dfa_states[current_set] = {}

        # Find all symbols that lead somewhere from this set of NFA states
        alphabet = set()
        for state in current_set:
            for (s, ch) in nfa["delta"]:
                if s in current_set:
                    alphabet.add(ch)

        for ch in alphabet:
            # Compute the set of NFA states reachable on this symbol
            next_set = frozenset(
                s2 for s1 in current_set
                for s2 in nfa["delta"].get((s1, ch), frozenset())
            )
            if next_set:
                dfa_states[current_set][ch] = next_set
                if next_set not in visited:
                    visited.add(next_set)
                    worklist.append(next_set)

    # Accepting DFA states: any set containing an NFA accept state
    dfa_accept = {s for s in dfa_states if s & nfa["accept"]}

    return {"start": start, "accept": dfa_accept, "delta_sets": dfa_states}

ENDS_IN_AB_NFA = {
    "start": frozenset({"q0"}),
    "accept": frozenset({"q2"}),
    "delta": {
        ("q0", "a"): frozenset({"q0", "q1"}),
        ("q0", "b"): frozenset({"q0"}),
        ("q1", "b"): frozenset({"q2"}),
    },
}

dfa = subset_construction(ENDS_IN_AB_NFA)

print("=== Subset Construction Result ===")
print(f"DFA states ({len(dfa['delta_sets'])} total):")
for state_set, transitions in sorted(dfa['delta_sets'].items(), key=str):
    is_start  = "→" if state_set == dfa["start"] else " "
    is_accept = "*" if state_set in dfa["accept"] else " "
    state_name = "{" + ",".join(sorted(state_set)) + "}"
    print(f"  {is_start}{is_accept} {state_name}: {dict(sorted((k,'{'+','.join(sorted(v))+'}') for k,v in transitions.items()))}")

# Verify: run strings through the DFA-from-subset-construction
def run_dfa_subset(dfa, s):
    state = dfa["start"]
    for ch in s:
        state = dfa["delta_sets"].get(state, {}).get(ch)
        if state is None: return False
    return state in dfa["accept"]

print("\n=== Verification (NFA vs constructed DFA) ===")
for s in ["ab", "aab", "abab", "ba", "a", "b", ""]:
    nfa_result = bool(frozenset(
        s2 for path_state in ENDS_IN_AB_NFA["start"]
        for s2 in (ENDS_IN_AB_NFA["delta"].get((path_state, s[-1:]), frozenset()) if s else ENDS_IN_AB_NFA["start"])
    ) & ENDS_IN_AB_NFA["accept"]) if s else False
    # Simpler: just use the run_nfa from above
    dfa_result = run_dfa_subset(dfa, s)
    print(f"  {s!r:7}: DFA={dfa_result}")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

### Critical Thinking Questions

11. How many DFA states did the subset construction produce for the ends-in-ab NFA? Was there exponential blowup? (For this NFA, the answer is no — why not?)
12. The subset construction creates DFA states that are *sets* of NFA states. In what sense is this DFA tracking "where the NFA might be"?
13. Sketch Thompson's construction (boxes and epsilon arrows) for the regex `a(b|c)*`. How many states does it produce, and why is an NFA the natural output of a regex compiler rather than a DFA?

> **Watch out!** The subset construction is the *theoretical* bridge between NFAs and DFAs, but in practice it can produce exponentially many DFA states ($2^{|Q|}$ in the worst case). Real regex engines typically simulate the NFA directly (as in Model 3) to avoid this blowup, while still running in linear time on the input string.

---

# Part III: Synthesis and Practice

## 4. Exercises

1. *Design portfolio.* Draw DFAs for: strings over $\{0,1\}$ divisible by 3 when read as binary (three states; label them with remainders); strings not containing `bb`; strings whose length is even. Encode one in the dictionary format and test it.
2. *NFA to DFA by hand.* Apply the subset construction to the ends-in-`ab` NFA, drawing the resulting DFA and confirming it matches your Day 1 design (possibly with renamed states).
3. *Three notations, one language.* For "identifiers" (letter then letters-or-digits), produce all three artifacts: the regex, an NFA sketch, and a DFA in dictionary form with passing tests. Keep this trio; it is the worked example at the heart of your lexer.
4. *Equivalence argument.* In a paragraph, explain to a skeptical friend why adding nondeterminism (seemingly a superpower) adds no recognizing power, while adding a stack (the pushdown automaton) genuinely does.
5. *Thompson's construction.* Implement a mini Thompson's construction that builds an NFA from a regex with only `|`, `*`, and concatenation. Test it on `(a|b)*abb` (the classic example) and verify the NFA accepts the same strings as Python's `re.match(r"(a|b)*abb", s)`.

---

# Part IV: Formal Language Theory in Practice — Adapted Examples

These three models adapt Python programs from *Foundations of Computing* by Chuck Allison (Fresh Sources, Inc.), used under the [MIT License](https://github.com/chuckallison/foundations-of-computing/blob/main/LICENSE). Each is rewritten to fit the dict representation used above; the ideas are Allison's and the code is adapted for CS374.

---

## Model 5: Ends-With-b — A Concrete DFA Runner

The "ends-with-b" DFA has exactly two states: *not-ending-in-b* (start) and *just-saw-b* (accepting). Its transition table is small enough to verify by hand before running, making it ideal for building confidence in DFA tracing. The runner below is the same function as Model 2 applied to a new machine description — the runner never changes, only the data does.

> *Adapted from [`end_with_b.py`](https://github.com/chuckallison/foundations-of-computing/blob/main/code/end_with_b.py) in *Foundations of Computing* by Chuck Allison (Fresh Sources, Inc.), used under the [MIT License](https://github.com/chuckallison/foundations-of-computing/blob/main/LICENSE).*

```python
# DFA: strings over {a, b} that end with 'b'.
# State 0: start / "last char was not b"
# State 1: "last char was b"  ← accepting
# Adapted from Allison, Figure 2-1.

ENDS_WITH_B = {
    "start":  0,
    "accept": {1},
    "delta": {
        0: {"a": 0, "b": 1},
        1: {"a": 0, "b": 1},
    },
}

def run_dfa(machine, s, trace=False):
    state = machine["start"]
    if trace: print(f"  start: {state}")
    for ch in s:
        row = machine["delta"].get(state, {})
        if ch not in row:
            if trace: print(f"  '{ch}': DEAD STATE")
            return False
        state = row[ch]
        if trace: print(f"  '{ch}' → {state}")
    ok = state in machine["accept"]
    if trace: print(f"  final: {state} → {'ACCEPT' if ok else 'REJECT'}")
    return ok

tests = [("b",True),("ab",True),("ba",False),("abb",True),
         ("bba",False),("",False),("aaab",True),("abba",False)]
print("=== Ends-with-b DFA ===")
all_pass = True
for s, expected in tests:
    got = run_dfa(ENDS_WITH_B, s)
    ok  = (got == expected)
    all_pass = all_pass and ok
    print(f"  {'PASS' if ok else 'FAIL'}  {s!r:8} → {got}")
print(f"\nAll {len(tests)} tests passed: {all_pass}")
print("\n=== Trace of 'aab' ===")
run_dfa(ENDS_WITH_B, "aab", trace=True)
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

**CTQ M5.1** If you changed `"accept": {1}` to `"accept": {0, 1}`, which new strings would now be accepted? Explain by tracing through `run_dfa` on the empty string `""`.

**CTQ M5.2** Extend this machine to accept strings ending in `"bb"`. How many states do you need, and what does each state remember about the last two characters?

---

## Model 6: Is the Language Empty? — DFS Reachability

A fundamental question about any finite automaton: *does it accept anything at all?* If no accepting state is reachable from the start state, the language is empty. This is a graph-reachability question solved by DFS: treat the NFA's transition graph as a directed graph and search for any accepting node, stopping as soon as one is found.

> *Adapted from [`empty.py`](https://github.com/chuckallison/foundations-of-computing/blob/main/code/empty.py) in *Foundations of Computing* by Chuck Allison (Fresh Sources, Inc.), used under the [MIT License](https://github.com/chuckallison/foundations-of-computing/blob/main/LICENSE).*

```python
# Is the language of an NFA empty?
# Empty iff no accepting state is reachable from the start state.
# Algorithm: DFS treating the transition graph as a directed graph.
# Adapted from Allison, Figure 2-9.

def language_is_empty(nfa):
    """Return True if no accepting state is reachable from start."""
    graph = {}
    for (src, _sym), dests in nfa["delta"].items():
        graph.setdefault(src, set()).update(dests)

    visited, stack = set(), list(nfa["start"])
    while stack:
        node = stack.pop()
        if node in visited:
            continue
        visited.add(node)
        if node in nfa["accept"]:
            return False     # accepting state found: NOT empty
        for neighbor in graph.get(node, set()):
            if neighbor not in visited:
                stack.append(neighbor)
    return True              # no accepting state reachable: IS empty

# Test 1: ends-in-ab NFA — language is NOT empty
ENDS_IN_AB = {
    "start":  frozenset({"q0"}),
    "accept": frozenset({"q2"}),
    "delta": {
        ("q0","a"): frozenset({"q0","q1"}),
        ("q0","b"): frozenset({"q0"}),
        ("q1","b"): frozenset({"q2"}),
    },
}
# Test 2: accepting state is unreachable — language IS empty
DEAD_ACCEPT = {
    "start":  frozenset({"s0"}),
    "accept": frozenset({"s2"}),
    "delta":  {("s0","a"): frozenset({"s1"})},
}
# Test 3: start state IS an accepting state — language contains the empty string
ACCEPTS_EPSILON = {
    "start":  frozenset({"q0"}),
    "accept": frozenset({"q0"}),
    "delta":  {},
}
print(f"ends-in-ab empty?      {language_is_empty(ENDS_IN_AB)}")
print(f"dead-accept empty?     {language_is_empty(DEAD_ACCEPT)}")
print(f"accepts-epsilon empty? {language_is_empty(ACCEPTS_EPSILON)}")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

**CTQ M6.1** The DFS ignores *which symbol* labels each transition — it treats the NFA as a plain directed graph. Why is this correct for the emptiness question? What would need to change if we also wanted to find a *witness string* (the shortest string accepted)?

**CTQ M6.2** Replace the DFS stack with a `collections.deque` (BFS). Does the emptiness answer change? What does change, and when would BFS be preferable for finding a witness string?

**CTQ M6.3** Construct an NFA with 10 states whose language is empty. Describe its structure in one sentence — what makes every accepting state unreachable?

---

## Model 7: Binary Addition as a Carry-State Machine

Can a finite automaton *compute*? Yes — if it produces output on each transition rather than only a yes/no verdict at the end. This is a **Mealy machine**. Binary addition is the perfect case: the carry from one column is exactly one bit of state, so a 2-state machine handles addition of any length. Each step reads a pair of bits, outputs a sum bit, and transitions to the next carry state — $n$ steps for two $n$-bit numbers.

> *Adapted from [`binadd.py`](https://github.com/chuckallison/foundations-of-computing/blob/main/code/binadd.py) in *Foundations of Computing* by Chuck Allison (Fresh Sources, Inc.), used under the [MIT License](https://github.com/chuckallison/foundations-of-computing/blob/main/LICENSE).*

```python
# Binary addition via a 2-state carry automaton (Mealy machine).
# State  = carry-in bit (0 or 1).
# Input  = pair of bits from each operand, least-significant bit first.
# Output = sum bit for this position.
# Adapted from Allison, Figure 2-42.

def binary_add(x: int, y: int) -> int:
    def to_lsb(n):
        if n == 0: return [0]
        bits = []
        while n:
            bits.append(n & 1)
            n >>= 1
        return bits   # least-significant bit first

    a, b = to_lsb(x), to_lsb(y)
    length = max(len(a), len(b))
    a += [0] * (length - len(a))
    b += [0] * (length - len(b))

    carry = 0       # machine state
    result_bits = []
    for ba, bb in zip(a, b):
        total = ba + bb + carry
        result_bits.append(total % 2)   # output bit
        carry = total // 2              # next state
    if carry:
        result_bits.append(1)

    return sum(bit * (2**i) for i, bit in enumerate(result_bits))

print("=== Carry-state binary adder ===")
pairs = [(0,0),(1,0),(3,5),(7,1),(13,9),(255,1),(100,156)]
all_pass = True
for x, y in pairs:
    got = binary_add(x, y)
    ok  = (got == x + y)
    all_pass = all_pass and ok
    print(f"  {'PASS' if ok else 'FAIL'}  {x:3} + {y:3} = {got:4}  (expected {x+y})")
print(f"\nAll tests passed: {all_pass}")

print("\n=== Carry-state trace: 13 + 9 ===")
a_bits = [1,0,1,1]; b_bits = [1,0,0,1]; carry = 0
for i,(ba,bb) in enumerate(zip(a_bits, b_bits)):
    total = ba + bb + carry
    out   = total % 2; carry = total // 2
    print(f"  col {i}: ({ba}+{bb}+carry_in={carry-(total//2-carry)}) → sum_bit={out}, carry_out={carry}")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

**CTQ M7.1** The `carry` variable is the machine's only state and takes exactly two values. Draw the Mealy machine: two nodes (labeled 0 and 1) with arrows labeled `(bit_a, bit_b) / sum_bit`. How many arrows does the complete diagram have?

**CTQ M7.2** The machine handles numbers of any length using exactly 2 states. What would change — in the *number of states*, not the implementation — if you extended the machine to base-10 addition?

**CTQ M7.3** The machine processes bits least-significant first, which is natural for carry propagation. Redesign it to process most-significant first. What additional data structure do you need, and why?

---

## Practice — Allison Readings 2.1 and 2.2

[[MC]]
A DFA accepting binary strings representing multiples of 3 needs at minimum:
- (x) 3 states — one per remainder mod 3
- ( ) 4 states
- ( ) 2 states (even/odd)
- ( ) Infinitely many states (since there are infinitely many multiples of 3)

[[MC]]
Which of the following languages has NO finite automaton that recognizes it?
- ( ) Strings over {a,b} with an even number of `a`s
- ( ) Strings over {a,b} ending with `bb`
- (x) Strings over {a,b} with equal numbers of `a`s and `b`s
- ( ) Strings over {a,b} not containing `aa` as a substring

[[MC]]
An NFA with 5 states is converted to a DFA via the subset construction. The DFA has at most:
- ( ) 5 states
- ( ) 10 states
- (x) 32 states — one per subset of the 5 NFA states
- ( ) 25 states

1. *Divisibility DFA.* Draw a DFA over $\{0,1\}$ that accepts binary numbers divisible by 3. Label each state with the remainder it represents. Verify on: `0` (0), `11` (3), `110` (6), `101` (5).

2. *Substring DFA.* Construct a DFA over $\{a,b\}$ that accepts strings containing both `aa` and `bb` as substrings. How many states? Label each with which combination (neither, only-aa, only-bb, both) it tracks.

3. *NFA for union.* Draw an NFA for "strings over $\{a,b\}$ containing `ab` or `ba`." Use nondeterminism to keep the state count low, then implement it in the dict format from Model 3 and test on `ab`, `ba`, `aaa`, `bbb`, `abba`.

4. *Subset construction by hand.* Apply the subset construction to: states $\{0,1,2\}$, start $\{0\}$, accept $\{2\}$, $\delta(0,a)=\{0,1\}$, $\delta(0,b)=\{0\}$, $\delta(1,b)=\{2\}$. List all DFA states (as subsets) and their transitions. How many DFA states result?

---

## Reflection Prompt

In your notebook: the DFA's whole intelligence is choosing what little to remember (one parity bit, the last two characters). Describe one situation in your own studying or work where deliberately remembering *less*, but the right less, made you more effective. Also: the NFA/DFA equivalence says that nondeterminism is "free" at the cost of state explosion. Does this idea appear elsewhere in computer science — a conceptually clean but potentially expensive algorithm that compiles into a deterministic one?

---

## 5. Further Reading

- Douglas Thain. *Introduction to Compilers and Language Design*, Chapter 3.
- Michael Sipser. *Introduction to the Theory of Computation*, Chapter 1.
- Russ Cox. "Regular Expression Matching Can Be Simple And Fast" (online): Thompson's construction in production.
- [Automata Tutor](https://automata.cs.ru.nl/) — interactive DFA/NFA design and verification tool.
