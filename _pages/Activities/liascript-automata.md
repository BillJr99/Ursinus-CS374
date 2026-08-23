<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374-Fall2026/gh-pages/_pages/Activities/liascript-automata.md or locally via https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374-Fall2026/gh-pages/_pages/Activities/liascript-automata.md

import: https://raw.githubusercontent.com/liascript/CodeRunner/master/README.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

# Finite Automata

Think of a turnstile at a subway station. It has exactly two states (**locked** and **unlocked**) and two transitions: inserting a coin moves it from locked to unlocked, and pushing moves it from unlocked back to locked. That tiny machine already captures the essence of a finite automaton: a fixed set of states, arrows triggered by input symbols, and a yes/no verdict at the end. The remarkable fact you will discover today is that this humble model is *exactly* as powerful as every pattern you wrote in the *Regular Expressions* activity.

## Learning Goals

By the end of this activity, you will be able to:

- Define a DFA as a five-tuple and trace its execution on an input string, identifying the state after each symbol and determining acceptance or rejection
- Construct a DFA for a specified regular language by identifying the finite information the machine must track and assigning one state per distinguishable memory value
- Define an NFA and explain how it differs from a DFA in its transition function, including epsilon transitions
- Explain the subset construction argument for DFA-NFA equivalence and apply it to convert a small NFA into an equivalent DFA
- Implement a DFA simulator in Python using a transition table (dict of dicts) and connect the automaton model to the operation of a regex-based lexer

A regular expression *describes* a set of strings; a **finite automaton** *recognizes* one, a machine so simple it is just states and arrows, yet exactly as powerful as the regex notation. Over two days we build the machine view: **DFAs $\rightarrow$ NFAs $\rightarrow$ their surprising equivalence $\rightarrow$ simulation in Python**, the theory under your next assignment and the engine inside every lexer, including yours.

> **Before You Begin**, make sure you can:
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
          +---+            +---+
          v   |            v   |
   --> ((even)) --1-->  (odd)
          ^                 |
          `-------1---------+
```

Two states suffice because the machine only needs to remember one bit: the parity so far.

---

## Model 1: Trace and Design

Before writing any code, you need to be comfortable *tracing* a DFA by hand, following the arrows one symbol at a time. The parity machine above is the ideal warm-up: it has only two states, so every transition is obvious, yet it handles an infinite set of strings correctly. Once tracing feels mechanical, designing your own DFA becomes a matter of asking "what is the minimum information I need to remember at each step?"

### Critical Thinking Questions

1. Trace `1011` through the parity DFA, listing the state after each symbol. Accepted or rejected? The Recorder writes the trace.
2. Design (draw) a DFA over $\{a, b\}$ accepting strings that **end in `ab`**. How many states did your team need, and what does each state "remember"?
3. Design a DFA accepting strings containing the substring `aa`. Compare with question 2: ending-in versus containing changes which states are accepting; articulate how.
4. Try to design a DFA for $a^n b^n$. Where does finite memory fail you, and which prior module predicted this?

### Worked Example: tracing `1011`, as a static table

CTQ 1 asks for this trace. Do it first; then check. The point of writing it as a table rather than "running it" is that you can do this on paper in an exam, in a design meeting, or when the code is not written yet.

| Step | State before | Symbol read | Transition used | State after |
|------|--------------|-------------|-----------------|-------------|
| 0 | - | *(start)* | - | `even` |
| 1 | `even` | `1` | `even --1--> odd` | `odd` |
| 2 | `odd` | `0` | `odd --0--> odd` | `odd` |
| 3 | `odd` | `1` | `odd --1--> even` | `even` |
| 4 | `even` | `1` | `even --1--> odd` | `odd` |

Final state `odd`, which is **not** an accepting state, so `1011` is **rejected**. It has three `1`s, and this machine accepts an even count.

Two habits worth forming from this small table. First, the `0` transitions are self-loops: reading a `0` never changes the answer, which is the machine *saying* that zeros are irrelevant to parity. A DFA's self-loops are always a claim about what the machine chooses to ignore. Second, the state after step 4 is the entire memory of the computation: the machine has forgotten that it read `1011` and remembers only "odd so far." That is the whole limitation you will run into in CTQ 4.


> The worked answers to this session's models are in the **Answer Key** at the end of this page. Attempt them with your team first.

## Model 2: DFA Simulation, A Dictionary and a Loop

The formal five-tuple maps almost directly onto a Python data structure: states become string keys, the transition function becomes a `dict` of `dict`s, and the entire simulation is a loop that does one dictionary lookup per character. Reading this code, notice that the *logic* never changes; only the data describing the machine does. That separation between the runner and the machine description is exactly the architecture your lexer assignment will use.

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
        if trace: print(f"  '{ch}' -> {state}")
    accepted = state in machine["accept"]
    if trace: print(f"  final: {state} -> {'ACCEPT' if accepted else 'REJECT'}")
    return accepted

# Test the parity DFA
print("=== Even-ones DFA ===")
for s in ["", "1", "11", "1011", "0000", "10101", "abc"]:
    print(f"  {s!r:9} -> {run_dfa(EVEN_ONES, s)}")

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
    print(f"  {s!r:7} -> {run_dfa(ENDS_IN_AB_DFA, s)}")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

### Critical Thinking Questions

5. The empty string is accepted by `EVEN_ONES`. Point to the line of code and the part of the formal definition that together make that happen, and decide whether it is correct for "even number of 1s."
6. Encode your ends-in-`ab` DFA from Model 1 in the same dictionary format and test five strings. What was mechanical and what required thought? (That split is the point: the *design* is the thinking; the *runner* is ten lines forever.)
7. The `ENDS_IN_AB_DFA` has 3 states. If the target were "ends in `abc`", how many states would be needed, and what would each state remember?

---


> **Continued next session.** Day 2 picks up from here: [Finite Automata, Day 2: Nondeterminism and Equivalence](https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374-Fall2026/gh-pages/_pages/Activities/liascript-automata-day2.md).
