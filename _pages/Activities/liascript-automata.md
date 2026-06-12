# Finite Automata
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

## 2. Simulation: A DFA Is a Dictionary and a Loop

---

## Code Cell

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

def run_dfa(machine, s):
    try:
        state = machine["start"]
        for ch in s:
            if ch not in machine["delta"][state]:
                return False          # symbol outside the alphabet: reject
            state = machine["delta"][state][ch]
        return state in machine["accept"]
    except Exception as e:
        print(f"[automata:run_dfa] {e}")
        import traceback; traceback.print_exc()
        return False

for s in ["", "1", "11", "1011", "0000", "10101"]:
    print(f"{s!r:9} -> {run_dfa(EVEN_ONES, s)}")
```

---

### Critical Thinking Questions

5. The empty string is accepted. Point to the line of code and the part of the formal definition that together make that happen, and decide whether it is correct for "even number of 1s."
6. Encode your ends-in-`ab` DFA from Model 1 in the same dictionary format and test five strings. What was mechanical and what required thought? (That split is the point: the *design* is the thinking; the *runner* is ten lines forever.)

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

---

## Code Cell

```python
# NFA simulation by tracking the SET of possible states: the subset
# construction performed lazily, one input symbol at a time.

ENDS_IN_AB = {
    "start": {"q0"},
    "accept": {"q2"},
    "delta": {                      # sets of successor states
        ("q0", "a"): {"q0", "q1"},  # loop, or guess the ending starts here
        ("q0", "b"): {"q0"},
        ("q1", "b"): {"q2"},
    },
}

def run_nfa(machine, s):
    try:
        current = set(machine["start"])
        for ch in s:
            nxt = set()
            for state in current:
                nxt |= machine["delta"].get((state, ch), set())
            current = nxt
            if not current:
                return False
        return bool(current & machine["accept"])
    except Exception as e:
        print(f"[automata:run_nfa] {e}")
        import traceback; traceback.print_exc()
        return False

for s in ["ab", "aab", "abab", "ba", "a", "b", "aabb"]:
    print(f"{s!r:9} -> {run_nfa(ENDS_IN_AB, s)}")
```

---

## Model 2: Watching Nondeterminism

### Critical Thinking Questions

7. Trace `aab` by hand, writing the *set* of states after each symbol. Where does the machine "hedge its bets," and which bet pays off?
8. Compare the NFA's three states with your Day 1 DFA for the same language. Which was easier to design, and which is cheaper to run per input symbol? State the trade in one sentence.
9. The simulation tracks sets, so it effectively runs the subset construction on the fly. For an NFA with $k$ states, bound the work per input character. Why is this still considered fast?
10. Sketch (boxes and epsilon arrows, no code) Thompson's construction for the regex `a(b|c)*`. Count states. This sketch is precisely how `re` engines and lexer generators are born.

---

# Part III: Synthesis and Practice

## 4. Exercises

1. *Design portfolio.* Draw DFAs for: strings over $\{0,1\}$ divisible by 3 when read as binary (three states; label them with remainders); strings not containing `bb`; strings whose length is even. Encode one in the dictionary format and test it.
2. *NFA to DFA by hand.* Apply the subset construction to the ends-in-`ab` NFA, drawing the resulting DFA and confirming it matches your Day 1 design (possibly with renamed states).
3. *Three notations, one language.* For "identifiers" (letter then letters-or-digits), produce all three artifacts: the regex, an NFA sketch, and a DFA in dictionary form with passing tests. Keep this trio; it is the worked example at the heart of your lexer.
4. *Equivalence argument.* In a paragraph, explain to a skeptical friend why adding nondeterminism (seemingly a superpower) adds no recognizing power, while adding a stack (the pushdown automaton) genuinely does.

---

## Reflection Prompt

In your notebook: the DFA's whole intelligence is choosing what little to remember (one parity bit, the last two characters). Describe one situation in your own studying or work where deliberately remembering *less*, but the right less, made you more effective.

---

## 5. Further Reading

- Douglas Thain. *Introduction to Compilers and Language Design*, Chapter 3.
- Michael Sipser. *Introduction to the Theory of Computation*, Chapter 1.
- Russ Cox. "Regular Expression Matching Can Be Simple And Fast" (online): Thompson's construction in production.
