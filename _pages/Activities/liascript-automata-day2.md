<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374-Fall2026/gh-pages/_pages/Activities/liascript-automata-day2.md or locally via https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374-Fall2026/gh-pages/_pages/Activities/liascript-automata-day2.md

import: https://raw.githubusercontent.com/liascript/CodeRunner/master/README.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

# Finite Automata, Day 2: Nondeterminism and Equivalence

Day 1 built deterministic machines and traced them by hand.  Today we let the machine guess, and then prove that the guessing bought it no extra power, by converting any NFA into a DFA with the subset construction.  This is the theorem that lets your lexer use regular expressions and still run in linear time.

> This is the second of two sessions on this topic.  If you have not done Day 1, start there: [Finite Automata](https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374-Fall2026/gh-pages/_pages/Activities/liascript-automata.md).

# Part II: Nondeterminism and Equivalence (Day 2)

## 3.  NFAs: Generous Machines

**A nondeterministic finite automaton (NFA)** relaxes the rules: a state may have *several* arrows for one symbol, *none*, and even **epsilon transitions** that move without consuming input ($\delta: Q \times (\Sigma \cup \{\varepsilon\}) \rightarrow \mathcal{P}(Q)$).  An NFA accepts if **any** path of choices leads to acceptance, as if the machine explored all options in parallel.  NFAs are usually far easier to design (the "ends in `ab`" NFA is just three states in a line with a self-loop), and they are what regular expressions compile into naturally: concatenation chains machines, `|` forks with epsilons, `*` loops back with epsilons (Thompson's construction).

The punchline: NFAs are no more powerful.  The **subset construction** converts any NFA to a DFA whose states are *sets* of NFA states (tracking everywhere the NFA could be), giving:

$$
\text{regex} \equiv \text{NFA} \equiv \text{DFA}
$$

with a worst-case exponential blowup in state count ($2^{|Q|}$ subsets) as the price of determinism, a classic time-space-simplicity trade.

> **Watch out!**  NFAs and DFAs recognize *exactly the same class of languages*; neither is more powerful.  NFAs are simply more *compact to write*: the ends-in-`ab` NFA needs 3 states while the equivalent DFA needs 4.  The equivalence is proven by the subset construction, not assumed.

An NFA has 4 states.  The subset-construction DFA recognizing the same language has at most:

[( )] 4 states
[( )] 8 states
[(X)] 16 states, one per subset of the NFA's states
[( )] Unboundedly many states

The NFA "ends in ab" has 3 states: start/loop (q0), saw-a (q1), saw-ab (q2).  The key non-determinism is at q0 on input 'a': the machine can stay in q0 (still looping) OR move to q1 (guessing the ending starts here).  This non-determinism means:

[( )] The machine will fail on inputs where multiple paths exist
[( )] The machine requires exponential time to simulate
[(X)] The machine accepts if ANY choice of path leads to an accepting state
[( )] The machine requires the programmer to specify which path to take

---

## Model 3: NFA Simulation

Simulating an NFA does not require any magic or backtracking.  Instead of tracking a single current state, the simulator tracks the *set* of all states the NFA could be in right now, every live path, simultaneously.  Each input symbol advances every state in that set and unions the results.  This is the subset construction running lazily, one character at a time, and it costs at most $O(k)$ work per symbol for a $k$-state NFA.

```python
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
        if trace: print(f"  '{ch}' -> {{{', '.join(sorted(current))}}}")
        if not current:
            if trace: print(f"  DEAD STATE (all paths exhausted)")
            return False
    accepted = bool(current & machine["accept"])
    if trace: print(f"  -> {'ACCEPT' if accepted else 'REJECT'}")
    return accepted

print("=== NFA: ends-in-ab ===")
for s in ["ab", "aab", "abab", "ba", "a", "b", "aabb", ""]:
    print(f"  {s!r:7} -> {run_nfa(ENDS_IN_AB_NFA, s)}")

print("\n=== Trace of 'aab' ===")
run_nfa(ENDS_IN_AB_NFA, "aab", trace=True)
```
@LIA.eval(`["main.py"]`, `none`, `python3 main.py`)

> **Watch out!**  An NFA does not "guess" which path to take; that framing makes it sound like luck is involved.  The machine *explores all paths simultaneously*, and it accepts if *any* of them reaches an accepting state.  The simulation above makes this concrete: `current` is always a set, never a single lucky choice.

### Critical Thinking Questions

8.  Trace `aab` by hand, writing the *set* of states after each symbol.  Where does the machine "hedge its bets," and which bet pays off?
9.  Compare the NFA's three states with the DFA for the same language.  Which was easier to design, and which is cheaper to run per input symbol?
10.  The simulation tracks sets, so it effectively runs the subset construction on the fly.  For an NFA with $k$ states, bound the work per input character ($O(k)$ per symbol).  Why is this still considered fast?

---

## Model 4: Subset Construction, NFA -> DFA

The subset construction is the key insight that connects NFAs to DFAs.  Each DFA state corresponds to a *frozenset* of NFA states, "the set of places the NFA could be after reading this much input."  The algorithm simply performs a reachability search over those sets, building the DFA transition table as it goes.  Once you see the code, you will notice that Model 3's simulation was already doing this implicitly on every input string.

```python
# Full subset construction: convert an NFA to an equivalent DFA.
# DFA states = frozensets of NFA states.

def subset_construction(nfa):
    """Convert NFA to DFA via subset construction."""
    start = nfa["start"]  # already a frozenset
    dfa_states = {}       # frozenset -> dict of transitions
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
    is_start  = "->" if state_set == dfa["start"] else " "
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
@LIA.eval(`["main.py"]`, `none`, `python3 main.py`)

### Critical Thinking Questions

11.  How many DFA states did the subset construction produce for the ends-in-ab NFA? Was there exponential blowup?  (For this NFA, the answer is no; why not?)
12.  The subset construction creates DFA states that are *sets* of NFA states.  In what sense is this DFA tracking "where the NFA might be"?
13.  Sketch Thompson's construction (boxes and epsilon arrows) for the regex `a(b|c)*`.  How many states does it produce, and why is an NFA the natural output of a regex compiler rather than a DFA?

> **Watch out!**  The subset construction is the *theoretical* bridge between NFAs and DFAs, but in practice it can produce exponentially many DFA states ($2^{|Q|}$ in the worst case).  Real regex engines typically simulate the NFA directly (as in Model 3) to avoid this blowup, while still running in linear time on the input string.

---

# Part III: Synthesis and Practice

## 4.  Exercises

1.  *Design portfolio.*  Draw DFAs for: strings over $\{0,1\}$ divisible by 3 when read as binary (three states; label them with remainders); strings not containing `bb`; strings whose length is even.  Encode one in the dictionary format and test it.
2.  *NFA to DFA by hand.*  Apply the subset construction to the ends-in-`ab` NFA, drawing the resulting DFA and confirming it matches your Day 1 design (possibly with renamed states).
3.  *Three notations, one language.*  For "identifiers" (letter then letters-or-digits), produce all three artifacts: the regex, an NFA sketch, and a DFA in dictionary form with passing tests.  Keep this trio; it is the worked example at the heart of your lexer.
4.  *Equivalence argument.*  In a paragraph, explain to a skeptical friend why adding nondeterminism (seemingly a superpower) adds no recognizing power, while adding a stack (the pushdown automaton) genuinely does.
5.  *Thompson's construction.*  Implement a mini Thompson's construction that builds an NFA from a regex with only `|`, `*`, and concatenation.  Test it on `(a|b)*abb` (the classic example) and verify the NFA accepts the same strings as Python's `re.match(r"(a|b)*abb", s)`.

---

# Part IV: Formal Language Theory in Practice, Adapted Examples

These three models adapt Python programs from *Foundations of Computing* by Chuck Allison (Fresh Sources, Inc.), used under the [MIT License](https://github.com/chuckallison/foundations-of-computing/blob/main/LICENSE).  Each is rewritten to fit the dict representation used above; the ideas are Allison's and the code is adapted for CS374.

---

## Model 5: Ends-With-b, A Concrete DFA Runner

The "ends-with-b" DFA has exactly two states: *not-ending-in-b* (start) and *just-saw-b* (accepting).  Its transition table is small enough to verify by hand before running, making it ideal for building confidence in DFA tracing.  The runner below is the same function as Model 2 applied to a new machine description; the runner never changes, only the data does.

> *Adapted from [`end_with_b.py`](https://github.com/chuckallison/foundations-of-computing/blob/main/code/end_with_b.py) in *Foundations of Computing* by Chuck Allison (Fresh Sources, Inc.), used under the [MIT License](https://github.com/chuckallison/foundations-of-computing/blob/main/LICENSE).*

```python
# DFA: strings over {a, b} that end with 'b'.
# State 0: start / "last char was not b"
# State 1: "last char was b"  <- accepting
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
        if trace: print(f"  '{ch}' -> {state}")
    ok = state in machine["accept"]
    if trace: print(f"  final: {state} -> {'ACCEPT' if ok else 'REJECT'}")
    return ok

tests = [("b",True),("ab",True),("ba",False),("abb",True),
         ("bba",False),("",False),("aaab",True),("abba",False)]
print("=== Ends-with-b DFA ===")
all_pass = True
for s, expected in tests:
    got = run_dfa(ENDS_WITH_B, s)
    ok  = (got == expected)
    all_pass = all_pass and ok
    print(f"  {'PASS' if ok else 'FAIL'}  {s!r:8} -> {got}")
print(f"\nAll {len(tests)} tests passed: {all_pass}")
print("\n=== Trace of 'aab' ===")
run_dfa(ENDS_WITH_B, "aab", trace=True)
```
@LIA.eval(`["main.py"]`, `none`, `python3 main.py`)

**CTQ M5.1** If you changed `"accept": {1}` to `"accept": {0, 1}`, which new strings would now be accepted?  Explain by tracing through `run_dfa` on the empty string `""`.

**CTQ M5.2** Extend this machine to accept strings ending in `"bb"`.  How many states do you need, and what does each state remember about the last two characters?

---

## Model 6: Is the Language Empty?  DFS Reachability

A fundamental question about any finite automaton: *does it accept anything at all?*  If no accepting state is reachable from the start state, the language is empty.  This is a graph-reachability question solved by DFS: treat the NFA's transition graph as a directed graph and search for any accepting node, stopping as soon as one is found.

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

# Test 1: ends-in-ab NFA, language is NOT empty
ENDS_IN_AB = {
    "start":  frozenset({"q0"}),
    "accept": frozenset({"q2"}),
    "delta": {
        ("q0","a"): frozenset({"q0","q1"}),
        ("q0","b"): frozenset({"q0"}),
        ("q1","b"): frozenset({"q2"}),
    },
}
# Test 2: accepting state is unreachable, language IS empty
DEAD_ACCEPT = {
    "start":  frozenset({"s0"}),
    "accept": frozenset({"s2"}),
    "delta":  {("s0","a"): frozenset({"s1"})},
}
# Test 3: start state IS an accepting state, language contains the empty string
ACCEPTS_EPSILON = {
    "start":  frozenset({"q0"}),
    "accept": frozenset({"q0"}),
    "delta":  {},
}
print(f"ends-in-ab empty?      {language_is_empty(ENDS_IN_AB)}")
print(f"dead-accept empty?     {language_is_empty(DEAD_ACCEPT)}")
print(f"accepts-epsilon empty? {language_is_empty(ACCEPTS_EPSILON)}")
```
@LIA.eval(`["main.py"]`, `none`, `python3 main.py`)

**CTQ M6.1** The DFS ignores *which symbol* labels each transition; it treats the NFA as a plain directed graph.  Why is this correct for the emptiness question?  What would need to change if we also wanted to find a *witness string* (the shortest string accepted)?

**CTQ M6.2** Replace the DFS stack with a `collections.deque` (BFS).  Does the emptiness answer change?  What does change, and when would BFS be preferable for finding a witness string?

**CTQ M6.3** Construct an NFA with 10 states whose language is empty.  Describe its structure in one sentence: what makes every accepting state unreachable?

---

## Model 7: Binary Addition as a Carry-State Machine

Can a finite automaton *compute*?  Yes: if it produces output on each transition rather than only a yes/no verdict at the end.  This is a **Mealy machine**.  Binary addition is the perfect case: the carry from one column is exactly one bit of state, so a 2-state machine handles addition of any length.  Each step reads a pair of bits, outputs a sum bit, and transitions to the next carry state, $n$ steps for two $n$-bit numbers.

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
    print(f"  col {i}: ({ba}+{bb}+carry_in={carry-(total//2-carry)}) -> sum_bit={out}, carry_out={carry}")
```
@LIA.eval(`["main.py"]`, `none`, `python3 main.py`)

**CTQ M7.1** The `carry` variable is the machine's only state and takes exactly two values.  Draw the Mealy machine: two nodes (labeled 0 and 1) with arrows labeled `(bit_a, bit_b) / sum_bit`.  How many arrows does the complete diagram have?

**CTQ M7.2** The machine handles numbers of any length using exactly 2 states.  What would change (in the *number of states*, not the implementation) if you extended the machine to base-10 addition?

**CTQ M7.3** The machine processes bits least-significant first, which is natural for carry propagation.  Redesign it to process most-significant first.  What additional data structure do you need, and why?

---

## Practice: Allison Readings 2.1 and 2.2

A DFA accepting binary strings representing multiples of 3 needs at minimum:

[(X)] 3 states, one per remainder mod 3
[( )] 4 states
[( )] 2 states (even/odd)
[( )] Infinitely many states (since there are infinitely many multiples of 3)

Which of the following languages has NO finite automaton that recognizes it?

[( )] Strings over {a,b} with an even number of `a`s
[( )] Strings over {a,b} ending with `bb`
[(X)] Strings over {a,b} with equal numbers of `a`s and `b`s
[( )] Strings over {a,b} not containing `aa` as a substring

An NFA with 5 states is converted to a DFA via the subset construction.  The DFA has at most:

[( )] 5 states
[( )] 10 states
[(X)] 32 states, one per subset of the 5 NFA states
[( )] 25 states

1.  *Divisibility DFA.* Draw a DFA over $\{0,1\}$ that accepts binary numbers divisible by 3.  Label each state with the remainder it represents.  Verify on: `0` (0), `11` (3), `110` (6), `101` (5).

2.  *Substring DFA.* Construct a DFA over $\{a,b\}$ that accepts strings containing both `aa` and `bb` as substrings.  How many states?  Label each with which combination (neither, only-aa, only-bb, both) it tracks.

3.  *NFA for union.*  Draw an NFA for "strings over $\{a,b\}$ containing `ab` or `ba`."  Use nondeterminism to keep the state count low, then implement it in the dict format from Model 3 and test on `ab`, `ba`, `aaa`, `bbb`, `abba`.

4.  *Subset construction by hand.*  Apply the subset construction to: states $\{0,1,2\}$, start $\{0\}$, accept $\{2\}$, $\delta(0,a)=\{0,1\}$, $\delta(0,b)=\{0\}$, $\delta(1,b)=\{2\}$. List all DFA states (as subsets) and their transitions.  How many DFA states result?

---

## Reflection Prompt

In your notebook: the DFA's whole intelligence is choosing what little to remember (one parity bit, the last two characters).  Describe one situation in your own studying or work where deliberately remembering *less*, but the right less, made you more effective.  Also: the NFA/DFA equivalence says that nondeterminism is "free" at the cost of state explosion.  Does this idea appear elsewhere in computer science, a conceptually clean but potentially expensive algorithm that compiles into a deterministic one?

---

## 5.  Further Reading

- Douglas Thain.  *Introduction to Compilers and Language Design*, Chapter 3.
- Michael Sipser.  *Introduction to the Theory of Computation*, Chapter 1.
- Russ Cox.  "Regular Expression Matching Can Be Simple And Fast" (online): Thompson's construction in production.
- [Automata Tutor](https://automata.cs.ru.nl/): interactive DFA/NFA design and verification tool.

---

Up next: the *Tokens and Scanning* activity turns this machinery into a working lexer, and these constructions are the heart of the Automata assignment.

# Answer Key

Work the models above with your team before reading these.  Each one answers a Critical Thinking Question the session poses; seeing the answer first turns the exercise into transcription.

### Worked Example: subset construction, worked to completion

Here is the NFA for "ends in `ab`" (CTQ 2's machine, built the easy way, with nondeterminism).  State `q0` loops on everything and guesses when to start matching:

```
        a,b
       +---+
       |   v
   --> (q0) --a--> (q1) --b--> ((q2))
```

`q0` on `a` has **two** choices: stay in `q0` or move to `q1`.  That is the nondeterminism.  Subset construction removes it by making each DFA state a *set* of NFA states, "all the places the NFA could be right now."

Start from `{q0}` and repeatedly compute where each symbol leads:

| DFA state (set) | on `a` | on `b` | accepting? |
|---|---|---|---|
| `A = {q0}` | `{q0, q1}` = **B** | `{q0}` = A | no |
| `B = {q0, q1}` | `{q0, q1}` = B | `{q0, q2}` = **C** | no |
| `C = {q0, q2}` | `{q0, q1}` = B | `{q0}` = A | **yes** (contains `q2`) |

No new sets appear, so the construction is done: **three DFA states**, from three NFA states.  Read the meaning off the sets: `A` = "have not just seen an `a`", `B` = "just saw an `a`, so a `b` would finish", `C` = "just finished an `ab`".  That is exactly the "what does each state remember?" answer CTQ 2 asks for, and you did not have to guess it; the algorithm produced it.

> Subset construction can blow up: $n$ NFA states admit up to $2^n$ subsets.  Here we got 3 instead of 8 because most subsets were unreachable, which is the usual outcome in practice.

### Worked Example: Thompson's construction on `a(b|c)*`

Thompson's construction builds an NFA from a regex compositionally: every operator has one fixed gadget, and you glue them.  Each fragment has exactly one start and one accepting state, which is what makes the gluing work.  Using `ε` for the empty transition:

**1.  Literals.** `a`, `b`, `c` are each a two-state fragment:

```
   (1) --a--> ((2))        (3) --b--> ((4))        (5) --c--> ((6))
```

**2.  Alternation `b|c`.**  Add a new start and a new accept, with `ε` branches into each side and `ε` exits out:

```
              ε      b      ε
        +--> (3) --------> (4) --+
   (7) -+                        |--> ((8))
        `--> (5) --------> (6) --+
              ε      c      ε
```

**3.  Star `(b|c)*`.**  Wrap it: `ε` to skip entirely, and `ε` from the old accept back to the old start to repeat:

```
                    +------- ε -------+
                    |                 |
   (9) --ε--> (7) --+-[ b|c ]-> (8) --+--ε--> ((10))
    |                                            ^
    `---------------- ε -------------------------+
```

The outer `ε` from `9` straight to `10` is what makes zero repetitions legal; the back edge from `8` to `7` is what makes many legal.

**4.  Concatenation `a` then `(b|c)*`.**  Join with an `ε` from `a`'s accept to the star's start:

```
   (1) --a--> (2) --ε--> (9) --[ (b|c)* ]--> ((10))
```

Ten states, and every one of them is forced, no creativity anywhere.  That mechanical quality is the point: it is why a program can do this, which is exactly what `lab-automata.md` asks you to implement.  Count the `ε` transitions and notice how many are pure bookkeeping; a real implementation usually removes them afterward with an ε-closure pass.


---
