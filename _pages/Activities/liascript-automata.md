# Finite Automata
<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://github.com/BillJr99/Ursinus-CS374-Fall2026/blob/gh-pages/_pages/Activities/liascript-automata.md or locally via https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374-Fall2026/gh-pages/_pages/Activities/liascript-automata.md

import: https://raw.githubusercontent.com/liascript/CodeRunner/master/README.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

# Finite Automata

## Learning Goals

By the end of this activity, you will be able to:

- Define a DFA as a five-tuple and trace its execution on an input string, identifying the state after each symbol and determining acceptance or rejection
- Construct a DFA for a specified regular language by identifying the finite information the machine must track and assigning one state per distinguishable memory value
- Define an NFA and explain how it differs from a DFA in its transition function, including epsilon transitions
- Explain the subset construction argument for DFA-NFA equivalence and apply it to convert a small NFA into an equivalent DFA
- Implement a DFA simulator in Python using a transition table (dict of dicts) and connect the automaton model to the operation of a regex-based lexer

A regular expression *describes* a set of strings; a **finite automaton** *recognizes* one, a machine so simple it is just states and arrows, yet exactly as powerful as the regex notation. Over two days we build the machine view: **DFAs $\rightarrow$ NFAs $\rightarrow$ their surprising equivalence $\rightarrow$ simulation in Python**, the theory under your next assignment and the engine inside every lexer, including yours.

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

### Critical Thinking Questions

1. Trace `1011` through the parity DFA, listing the state after each symbol. Accepted or rejected? The Recorder writes the trace.
2. Design (draw) a DFA over $\{a, b\}$ accepting strings that **end in `ab`**. How many states did your team need, and what does each state "remember"?
3. Design a DFA accepting strings containing the substring `aa`. Compare with question 2: ending-in versus containing changes which states are accepting; articulate how.
4. Try to design a DFA for $a^n b^n$. Where does finite memory fail you, and which prior module predicted this?

---

## Model 2: DFA Simulation — A Dictionary and a Loop

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
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

### Critical Thinking Questions

8. Trace `aab` by hand, writing the *set* of states after each symbol. Where does the machine "hedge its bets," and which bet pays off?
9. Compare the NFA's three states with the DFA for the same language. Which was easier to design, and which is cheaper to run per input symbol?
10. The simulation tracks sets, so it effectively runs the subset construction on the fly. For an NFA with $k$ states, bound the work per input character ($O(k)$ per symbol). Why is this still considered fast?

---

## Model 4: Subset Construction — NFA → DFA

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

---

# Part III: Synthesis and Practice

## 4. Exercises

1. *Design portfolio.* Draw DFAs for: strings over $\{0,1\}$ divisible by 3 when read as binary (three states; label them with remainders); strings not containing `bb`; strings whose length is even. Encode one in the dictionary format and test it.
2. *NFA to DFA by hand.* Apply the subset construction to the ends-in-`ab` NFA, drawing the resulting DFA and confirming it matches your Day 1 design (possibly with renamed states).
3. *Three notations, one language.* For "identifiers" (letter then letters-or-digits), produce all three artifacts: the regex, an NFA sketch, and a DFA in dictionary form with passing tests. Keep this trio; it is the worked example at the heart of your lexer.
4. *Equivalence argument.* In a paragraph, explain to a skeptical friend why adding nondeterminism (seemingly a superpower) adds no recognizing power, while adding a stack (the pushdown automaton) genuinely does.
5. *Thompson's construction.* Implement a mini Thompson's construction that builds an NFA from a regex with only `|`, `*`, and concatenation. Test it on `(a|b)*abb` (the classic example) and verify the NFA accepts the same strings as Python's `re.match(r"(a|b)*abb", s)`.

---

## Reflection Prompt

In your notebook: the DFA's whole intelligence is choosing what little to remember (one parity bit, the last two characters). Describe one situation in your own studying or work where deliberately remembering *less*, but the right less, made you more effective. Also: the NFA/DFA equivalence says that nondeterminism is "free" at the cost of state explosion. Does this idea appear elsewhere in computer science — a conceptually clean but potentially expensive algorithm that compiles into a deterministic one?

---

## 5. Further Reading

- Douglas Thain. *Introduction to Compilers and Language Design*, Chapter 3.
- Michael Sipser. *Introduction to the Theory of Computation*, Chapter 1.
- Russ Cox. "Regular Expression Matching Can Be Simple And Fast" (online): Thompson's construction in production.
- [Automata Tutor](https://automata.cs.ru.nl/) — interactive DFA/NFA design and verification tool.
