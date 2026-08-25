---
layout: assignment
permalink: /Assignments/Automata
title: "CS374: Principles of Programming Languages - Lab: Finite Automata Simulators"

info:
  coursenum: CS374
  purpose: "To make the theory beneath every lexer executable by building general DFA and NFA simulators driven by machine definitions loaded as data, and to trace the subset and Thompson's constructions once by hand."
  tilt:
    task: "With a partner, build DFA and NFA simulators that read machines from JSON, design one machine of each kind, and trace the subset construction and Thompson's construction by hand on small examples."
    criteria: "I assess your work on correct simulators that handle the deliberate edge cases, two annotated machine designs, and by-hand construction traces, weighted 40/40/20 across the three parts.  The rubric below breaks it down in full."
  points: 100
  goals:
    - To implement general DFA and NFA simulators over machine definitions loaded from JSON
    - To design one DFA and one NFA for specified languages and encode them as data
    - To trace the subset construction and Thompson's construction by hand on small examples
    - To connect automata to the regular expressions and lexer of the surrounding course
  rubric:
    - weight: 10
      description: "Part 0: Before You Start - Regular Expressions and Finite Automata"
      preemerging: Neither the regular expression nor the NFA is attempted
      beginning: A regular expression is written but no NFA is drawn, or the subset construction is not started
      progressing: A regex and a matching NFA are given and the subset construction is begun, but it stalls without the stalling step identified, or no accepted string is named
      proficient: A regular expression for a token class of your choice is given with an NFA that accepts the same language; a small NFA is converted to a DFA by hand over two or three input symbols; one string the DFA accepts is named; and if the state set stopped being obvious, that exact step is marked
    - weight: 36
      description: "DFA Simulation and Design (Goals 1, 2)"
      preemerging: The DFA simulator fails to run or fails most provided machines due to major structural errors
      beginning: The DFA simulator runs but fails on several test cases due to minor issues such as incorrect transition lookups or missing alphabet validation
      progressing: The DFA simulator passes the provided test cases but mishandles edge cases such as the empty string or symbols outside the alphabet, or the designed DFA lacks state annotations
      proficient: A correct DFA simulator passes all provided test machines, handles the empty string and out-of-alphabet symbols deliberately, supports trace mode, and runs the designed DFA with documented state meanings and passing tests
    - weight: 36
      description: "NFA Simulation and Design (Goals 1, 2)"
      preemerging: The NFA simulator is missing or fails to compute epsilon-closures correctly
      beginning: The NFA simulator runs but produces incorrect results on several machines due to epsilon-closure errors or incorrect powerset tracking
      progressing: The NFA simulator passes the provided test cases but would fail on machines with epsilon cycles, or the designed NFA does not actually use nondeterminism
      proficient: A correct NFA simulator correctly computes epsilon-closures with cycle detection, tracks the set of active states, and passes all provided test machines plus the designed NFA with traced execution paths
    - weight: 18
      description: "By-Hand Constructions (Goals 3, 4)"
      preemerging: Neither construction is attempted, or both traces are fundamentally incorrect
      beginning: One construction is traced but the other is missing, or both contain significant errors
      progressing: Both constructions are traced with minor errors (e.g., a missed epsilon-closure or an unlabeled fragment), or the lexer-connection paragraph is missing
      proficient: The subset-construction table is complete and correct, every Thompson fragment is labeled step by step, and the writeup includes a clear paragraph connecting the simulators to the lexer (which component of the lexer plays the role of your simulators?)
  readings:
    - rtitle: "Finite Automata Activity"
      rlink: "Activities/liascript-automata.md"
      liapage: true
    - rtitle: "Grammars and the Chomsky Hierarchy Activity"
      rlink: "Activities/liascript-grammars.md"
      liapage: true

tags:
  - automata
  - theory
  - languages
  - lab

---

In this **lab** you'll build the machines beneath your lexer.  That means general simulators for DFAs and NFAs that read machine definitions as data, one machine design of each kind, and a by-hand trace of the two classic constructions.  The simulators are short programs, and you can check their correctness against the worked traces below.  The constructions are paper exercises, so there is no code to write for those.

**Pair policy.**  You may do this lab **in pairs**.  Work together at one screen or split the DFA and NFA halves and review each other's work; either way, both of you submit the same ZIP, each naming the other in the writeup, and you both earn the same grade.  You may also work alone if you prefer.  Unlike the programming assignments, no individual-work certification is required here; the reflection asks who did what instead.

---

## Part 0: Before You Start — Regular Expressions and Finite Automata (10 points)

Do this one **on paper, before you write any simulator code**, and ideally before the Finite Automata session.  You may do it alone even though the rest of this lab is pair work.

The equivalence of regular expressions and finite automata is the first place this course claims two very different-looking things are the same.  You will believe it once you have built both for a language of your own and watched them agree.  Subset construction by hand is tedious exactly once; after that it is a tool you have.

1.  **Write a regular expression** for a token class of your choice — identifiers, or floating-point literals — and then **draw an NFA** that accepts the same language.
2.  **Convert a small NFA from the reading to a DFA by hand**, doing subset construction over two or three input symbols, and name one string the resulting DFA accepts.

Bring the construction even if it stalled, and **mark the subset-construction step where the state set stopped being obvious**.  That stall is the useful part, and Part 2 of this lab will have you automate exactly the step you got stuck on.

---

## Getting Started

### Environment and Setup

You need Python 3.10+ and the standard library only (`json` for machine files).  Create the layout from the Deliverables section up front:

```
simulator.py       # loader, run_dfa, run_nfa, CLI
machines/          # one JSON file per machine
writeup.md         # construction traces and reflection
```

### Your First 15 Minutes

Do not start with the simulator; start with a machine.  Copy the two-state parity machine JSON from Part 1 into `machines/even_ones.json`, then write the smallest possible `run_dfa`:

```python
import json, sys

machine = json.load(open("machines/even_ones.json"))
state = machine["start"]
for symbol in sys.argv[1]:
    state = machine["delta"][state][symbol]
print("accept" if state in machine["accept"] else "reject")
```

Run `python simulator.py 0110` (accept) and `python simulator.py 101` (reject), matching the traces shown in Part 1.  Once this ten-line core works, the rest of Part 1 is a matter of wrapping it in validation and `--trace`; you already know the heart of it is right.

### Suggested Pacing

This lab is handed out once the class sessions on regular expressions and finite automata are behind you; see the course schedule for the assigned and due dates.  One focused session with your partner covers Parts 1-2; the paper constructions fit in a second short sitting:

| Checkpoint | You should have |
|------------|----------------|
| On assignment | Loader and DFA simulator working against the provided machines |
| Midpoint | NFA simulator with epsilon-closure working; both designed machines encoded and tested |
| Due date | Construction traces and writeup assembled; ZIP submitted |

---

## Part 1: DFA Simulation and Design (36 points)

### Machine Format

All machines are JSON files with the following keys:

| Key | Type | Meaning |
|-----|------|---------|
| `states` | list of strings | all state names |
| `alphabet` | list of strings | all input symbols (each a single character) |
| `start` | string | the initial state |
| `accept` | list of strings | the accepting states |
| `delta` | object | transition function |

For DFAs, `delta` is a nested object: `delta[state][symbol]` gives the next state.  Every (state, symbol) pair in the alphabet must appear.

**Example, the two-state parity machine for "even number of 1s":**

```json
{
  "states": ["even", "odd"],
  "alphabet": ["0", "1"],
  "start": "even",
  "accept": ["even"],
  "delta": {
    "even": {"0": "even", "1": "odd"},
    "odd":  {"0": "odd",  "1": "even"}
  }
}
```

Trace on `"0110"`: even -> even -> odd -> even -> even.  Accepts. yes  
Trace on `"101"`: even -> odd -> even -> odd.  Rejects. yes

### Step 1a: Loader and DFA Simulator

Write `load_machine(path)` that reads a JSON file and validates that the start state, accept states, and every transition reference only declared states and alphabet symbols (collect *all* validation errors and raise a single `MachineError` listing them).  Then implement `run_dfa(machine, s) -> bool`.  Rules:
- Any symbol in `s` that is not in the machine's alphabet is an immediate reject; print a reason (do not crash).
- The empty string `""` is valid input; it tests whether the start state is an accept state.
- With flag `--trace`, print the current state after processing each symbol.

Test against the parity machine above (provided) with **at least four accepted strings and four rejected strings**.

### Step 1b: One DFA Design

Design, encode as JSON, and annotate each state with one sentence explaining what it "remembers":

**DFA, Ends in ab:** strings over `{a, b}` that end with the suffix `ab`.  
Worked example: `"aab"` -> accept; `"ba"` -> reject; `"ab"` -> accept; `""` -> reject.  
Hint: you need at least three states: track what suffix of `ab` has been seen most recently.

Test with at least four accepted and four rejected strings.

---

## Part 2: NFA Simulation and Design (36 points)

### NFA Machine Format

For NFAs, `delta` maps `"state,symbol"` string keys to *lists* of states.  The special symbol `"eps"` denotes an epsilon (ε) transition.  A state may have zero or more targets for any symbol.

**Example fragment:**

```json
"delta": {
  "q0,a": ["q0", "q1"],
  "q0,eps": ["q2"],
  "q1,b": ["q2"]
}
```

### Step 2a: Epsilon-Closure and NFA Simulator

Implement `eps_closure(machine, states) -> frozenset`, a small graph reachability computation: start with the given set of states and repeatedly follow `"eps"` transitions until no new states are discovered, handling cycles (a state may epsilon-transition back to itself or to a predecessor).

**Example:** If `q0 -ε-> q1`, `q1 -ε-> q2`, and `q2 -ε-> q0`, then `eps_closure(m, {"q0"}) = {"q0", "q1", "q2"}`.

Then implement `run_nfa(machine, s) -> bool`:
1.  Compute the epsilon-closure of `{start}` as the initial set of active states.
2.  For each symbol in `s`, compute the union of all `delta["state,symbol"]` lists over all active states, then take the epsilon-closure of that union.
3.  Accept if the final active set intersects the accept set.

### Step 2b: One NFA Design

Design, encode, and test with **at least four accepted and four rejected strings**:

**NFA, Contains aa:** strings over `{a, b}` containing the substring `aa` somewhere.  
Worked example: `"baaab"` -> accept; `"ababab"` -> reject.  
Hint: nondeterministically guess where `aa` occurs: your design should really use nondeterminism, not be a DFA in disguise.

---

## Part 3: By-Hand Constructions (18 points)

These are **paper exercises** in your writeup, no code.  The class sessions covered both algorithms; here you trace each once, on a small example, so you have personally executed what the lexer-generator tools automate.

### Step 3a: Subset Construction Trace

Apply the subset construction to your **Contains aa** NFA from Part 2 to produce an equivalent DFA. Draw the construction table:

| Powerset State | on `a` | on `b` | Accepting? |
|----------------|--------|--------|------------|
| {q0} | ... | ... | No/Yes |
| ... | | | |

Start with `eps_closure({start})`; for each unmarked powerset state, compute its transitions and epsilon-close the results; mark a powerset state as accepting if it contains any NFA accept state; continue until no unmarked states remain.  Document how many DFA states result.

### Step 3b: Thompson's Construction Trace

Apply Thompson's construction to the regular expression `a(b|c)*`.  Show each sub-expression and its fragment, labeling every state and every ε-transition:
1.  Fragment for `a`.
2.  Fragments for `b` and `c`.
3.  Fragment for `b|c` (union).
4.  Fragment for `(b|c)*` (Kleene star).
5.  Concatenation: `a` then `(b|c)*`.

For reference, the fragment rules: a single character is start -> accept labeled with that character; concatenation connects A's accept to B's start with ε; union adds a new start with ε to both fragments and ε from both accepts to a new shared accept; Kleene star adds a new start with ε to the fragment's start and to a new accept, with ε from the fragment's accept back to its start and on to the new accept.

---

## Deliverables

Submit a ZIP containing:
- `simulator.py`: the loader, DFA simulator, and NFA simulator with CLI entry point
- `machines/`: all JSON machine files (the provided parity machine plus your designed DFA and NFA)
- `writeup.md`: the subset-construction table, the Thompson's construction fragments, a paragraph connecting these simulators to the lexer you will build next (which component of the lexer plays the role of your simulators?), and both partners' names

Ensure reproducibility by listing your Python version.

---

## Grading Breakdown

| Component | Points |
|-----------|--------|
| Part 0: Regular Expressions and Finite Automata | 10 |
| Part 1: DFA Simulation and Design | 36 |
| Part 2: NFA Simulation and Design | 36 |
| Part 3: By-Hand Constructions | 18 |
| **Total** | **100** |

---

## Reflection Prompts

- Contrast designing the NFA with tracing its equivalent DFA via subset construction: where did the complexity move?
- Your simulators treat machines as data (loaded from JSON).  Name one benefit this brought during testing that hard-coded machines would have denied you.
- If you worked in a pair, who did what, and name one thing your partner caught that you would have missed.  If you worked alone, note that instead.
- AI disclosure: list any generative-AI tools you used, for what, and how you verified the results (or state 'none').
- Approximately how many hours it took you to finish this lab (I will not judge you for this at all; I am simply using it to gauge if the labs are too easy or hard)?
