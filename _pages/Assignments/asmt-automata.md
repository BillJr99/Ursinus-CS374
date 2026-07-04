---
layout: assignment
permalink: /Assignments/Automata
title: "CS374: Principles of Programming Languages - Finite Automata Simulator"

info:
  coursenum: CS374
  points: 100
  goals:
    - To implement general DFA and NFA simulators over machine definitions loaded from JSON
    - To design automata for specified languages and encode them as data
    - To demonstrate the subset construction by hand and verify it by simulation
    - To apply Thompson's construction to convert a regular expression to an NFA
    - To connect automata to the regular expressions and lexer of the surrounding course
  rubric:
    - weight: 25
      description: "DFA Design and Simulation (Goals 1, 2)"
      preemerging: The DFA simulator fails to run or fails most provided machines due to major structural errors
      beginning: The DFA simulator runs but fails on several test cases due to minor issues such as incorrect transition lookups or missing alphabet validation
      progressing: The DFA simulator passes the provided test cases but mishandles edge cases such as the empty string, symbols outside the alphabet, or trap states
      proficient: A correct DFA simulator passes all provided and hidden test cases, handles the empty string and out-of-alphabet symbols deliberately, supports trace mode, and runs all three required DFA designs with documented state meanings
    - weight: 25
      description: "NFA Design and Simulation (Goals 1, 2)"
      preemerging: The NFA simulator is missing or fails to compute epsilon-closures correctly
      beginning: The NFA simulator runs but produces incorrect results on several machines due to epsilon-closure errors or incorrect powerset tracking
      progressing: The NFA simulator passes the provided test cases but would fail on machines with epsilon cycles or machines that require epsilon closure at the final step
      proficient: A correct NFA simulator correctly computes epsilon-closures with cycle detection, tracks the powerset of states, and passes all provided and hidden test cases including all three required NFA designs with traced execution paths
    - weight: 25
      description: "Subset Construction (Goals 2, 3)"
      preemerging: The subset construction is not attempted or the resulting DFA is fundamentally incorrect
      beginning: The subset construction table is partially complete but the encoded DFA diverges from the NFA on several test strings
      progressing: The subset construction table is complete and the DFA is correctly encoded, but simulation agreement with the NFA is only verified on a few strings
      proficient: The subset construction is carried out fully by hand with every powerset state documented, the resulting DFA is encoded as JSON, and simulation agreement with the original NFA is verified programmatically across the full test suite
    - weight: 25
      description: "Thompson's Construction and Writeup (Goals 4, 5)"
      preemerging: Thompson's construction is not attempted or produces a machine that accepts clearly wrong strings
      beginning: Thompson's construction produces a machine for simple cases but fails on concatenation or union of sub-expressions
      progressing: Thompson's construction produces a correct NFA for the given regex and is verified by simulation, with limited explanation of the construction steps
      proficient: Thompson's construction is applied step-by-step with each fragment labeled, the final NFA is encoded as JSON, verified by simulation, and the writeup connects automata theory to the lexer pipeline with thoughtful reflection
  readings:
    - rtitle: "Finite Automata Activity"
      rlink: "https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374-Fall2026/gh-pages/_pages/Activities/liascript-automata.md"
    - rtitle: "Grammars and the Chomsky Hierarchy Activity"
      rlink: "https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374-Fall2026/gh-pages/_pages/Activities/liascript-grammars.md"

tags:
  - automata
  - theory
  - languages

---

In this assignment you will build the machines beneath your lexer: general simulators for DFAs and NFAs that read machine definitions as data, plus a design portfolio of machines you create, a hand-executed subset construction, and a Thompson's construction NFA. Build in the small scaffolded steps below; each step has its own tests. The point is not just that the code works — it is that you understand *why* it works, which the design portfolio and writeup capture.

---

## Part 1: DFA Design and Simulation (25 points)

### Machine Format

All machines are JSON files with the following keys:

| Key | Type | Meaning |
|-----|------|---------|
| `states` | list of strings | all state names |
| `alphabet` | list of strings | all input symbols (each a single character) |
| `start` | string | the initial state |
| `accept` | list of strings | the accepting states |
| `delta` | object | transition function |

For DFAs, `delta` is a nested object: `delta[state][symbol]` gives the next state. Every (state, symbol) pair in the alphabet must appear.

**Example — the two-state parity machine for "even number of 1s":**

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

Trace on `"0110"`: even → even → odd → even → even. Accepts. ✓  
Trace on `"101"`: even → odd → even → odd. Rejects. ✓

### Step 1a: Loader and Validator

Write `load_machine(path)` that reads a JSON file and validates:
- The start state appears in `states`.
- Every accept state appears in `states`.
- For a DFA, every (state, symbol) pair defined in `delta` references only declared states and alphabet symbols.
- Collect *all* validation errors (not just the first) and raise a single `MachineError` listing them.

### Step 1b: DFA Simulator

Implement `run_dfa(machine, s) -> bool`. Rules:
- Any symbol in `s` that is not in the machine's alphabet is an immediate reject; print a reason (do not crash).
- The empty string `""` is valid input; it tests whether the start state is an accept state.
- With flag `--trace`, print the current state after processing each symbol.

### Step 1c: DFA Design Portfolio

Design, encode as JSON, annotate each state with one sentence explaining what it "remembers," and test each machine below with **at least four accepted strings and four rejected strings**:

**DFA 1 — Even ones:** strings over `{0, 1}` containing an even number of 1s (include 0 ones as even).  
Worked example: `"0110"` → 2 ones (even) → accept; `"111"` → 3 ones (odd) → reject.

**DFA 2 — Ends in ab:** strings over `{a, b}` that end with the suffix `ab`.  
Worked example: `"aab"` → accept; `"ba"` → reject; `"ab"` → accept; `""` → reject.  
Hint: you need at least three states — track what suffix of `ab` has been seen most recently.

**DFA 3 — Binary divisible by 3:** strings over `{0, 1}` (big-endian binary) whose numeric value is divisible by 3. Include the empty string (value 0, divisible) and `"0"`.  
Worked example: `"110"` = 6 → accept; `"111"` = 7 → reject; `"0"` = 0 → accept.  
Hint: three states, each representing the current remainder mod 3.

---

## Part 2: NFA Design and Simulation (25 points)

### NFA Machine Format

For NFAs, `delta` maps `"state,symbol"` string keys to *lists* of states. The special symbol `"eps"` denotes an epsilon (ε) transition. A state may have zero or more targets for any symbol.

**Example fragment:**

```json
"delta": {
  "q0,a": ["q0", "q1"],
  "q0,eps": ["q2"],
  "q1,b": ["q2"]
}
```

### Step 2a: Epsilon-Closure

Implement `eps_closure(machine, states) -> frozenset`. This is a small graph reachability computation:
- Start with the given set of states.
- Repeatedly follow `"eps"` transitions until no new states are discovered.
- Handle cycles (a state may epsilon-transition back to itself or to a predecessor).

**Example:** If `q0 -ε→ q1`, `q1 -ε→ q2`, and `q2 -ε→ q0`, then `eps_closure(m, {"q0"}) = {"q0", "q1", "q2"}`.

### Step 2b: NFA Simulator

Implement `run_nfa(machine, s) -> bool`:
1. Compute the epsilon-closure of `{start}` as the initial set of active states.
2. For each symbol in `s`, compute the union of all `delta["state,symbol"]` lists over all active states, then take the epsilon-closure of that union.
3. Accept if the final active set intersects the accept set.

### Step 2c: NFA Design Portfolio

Design, encode, and test each NFA below with **at least four accepted and four rejected strings**:

**NFA 1 — Ends in ab:** the same language as DFA 2, but designed as an NFA. Use nondeterminism to "guess" where the suffix begins (fewer states, ε-free version possible with 3 states).

**NFA 2 — Contains aa:** strings over `{a, b}` containing the substring `aa` somewhere.  
Worked example: `"baaab"` → accept; `"ababab"` → reject.  
Hint: nondeterministically guess where `aa` occurs.

**NFA 3 — Third-from-last is a:** strings over `{a, b}` whose third-from-last symbol is `a`.  
Worked example: `"aab"` → the 3rd-from-last of `"aab"` is `a` → accept; `"bab"` → 3rd-from-last is `b` → reject.  
Hint: with NFA, guess nondeterministically where the last three symbols begin — the machine needs only 4 states.

---

## Part 3: Subset Construction — NFA to DFA (25 points)

Apply the subset construction to **NFA 3** (third-from-last is `a`) to produce an equivalent DFA.

### Step 3a: Hand Construction (in your writeup)

Draw the construction table with these columns:

| Powerset State | on `a` | on `b` | Accepting? |
|----------------|--------|--------|------------|
| {q0} | ... | ... | No/Yes |
| ... | | | |

Rules:
- Start with `eps_closure({q0_nfa})`.
- For each unmarked powerset state, compute its transitions and epsilon-close the results.
- Mark a powerset state as accepting if it contains any NFA accept state.
- Continue until no unmarked states remain.

Document how many DFA states result, and whether any are unreachable.

### Step 3b: Encode and Verify

Encode the resulting DFA as JSON. Run both the original NFA and the new DFA over the same test suite (all eight strings from Part 2, NFA 3). They must agree on every string — acceptance and rejection. Report any disagreement as a bug.

---

## Part 4: Thompson's Construction for a Regex (25 points)

Apply Thompson's construction to the regular expression `a(b|c)*d`.

### Background

Thompson's construction builds an NFA by composing small fragments:
- **Single character `x`:** one start state → one accept state, labeled `x`.
- **Concatenation `AB`:** connect the accept state of fragment A to the start of fragment B with ε.
- **Union `A|B`:** new start with ε-transitions to both A and B; both A and B's accept states ε-transition to a new shared accept.
- **Kleene star `A*`:** new start with ε to A's start and to a new accept; A's accept ε-transitions back to A's start and also to the new accept.

### Step 4a: Construction Steps (in your writeup)

Show each sub-expression and its fragment:
1. Fragment for `a`.
2. Fragment for `b`.
3. Fragment for `c`.
4. Fragment for `b|c` (union of 2 and 3).
5. Fragment for `(b|c)*` (Kleene star of 4).
6. Fragment for `d`.
7. Concatenation: `a` then `(b|c)*` then `d`.

Label every state (e.g., q0 through q_n) and every ε-transition.

### Step 4b: Encode and Verify

Encode the final NFA as JSON. Test it on:
- `"ad"` → accept
- `"abd"` → accept
- `"abcd"` → accept
- `"abbbcd"` → accept
- `"a"` → reject (no `d`)
- `"bd"` → reject (no leading `a`)
- `"acd"` → accept
- `""` → reject

---

## Deliverables

Submit a ZIP containing:
- `simulator.py` — the loader, DFA simulator, and NFA simulator with CLI entry point
- `machines/` — all JSON machine files (3 DFAs, 3 NFAs, 1 subset-construction DFA, 1 Thompson's NFA)
- `tests/` — test runner and output logs showing all test results
- `writeup.md` — approximately one page covering: the subset-construction table, Thompson's construction step-by-step, and a paragraph connecting these simulators to the lexer you will build next (which component of the lexer plays the role of your simulators?)

Ensure reproducibility by listing Python version. Run `python simulator.py --help` to confirm the CLI is documented.

---

## Grading Breakdown

| Component | Points |
|-----------|--------|
| Part 1: DFA Design and Simulation | 25 |
| Part 2: NFA Design and Simulation | 25 |
| Part 3: Subset Construction | 25 |
| Part 4: Thompson's Construction and Writeup | 25 |
| **Total** | **100** |

---

## Reflection Prompts

- For NFA 3, contrast designing the NFA with designing its equivalent DFA via subset construction: where did the complexity move?
- Your simulators treat machines as data (loaded from JSON). Name one benefit this brought during testing that hard-coded machines would have denied you.
- After completing Thompson's construction, describe one way the resulting NFA differs structurally from the hand-designed NFAs in Part 2.
- If collaboration with a buddy was permitted, did you work with a buddy on this assignment? If so, who? If not, do you certify that this submission represents your own original work? Please identify any and all portions of your submission that were not originally written by you.
- Approximately how many hours it took you to finish this assignment (I will not judge you for this at all — I am simply using it to gauge if the assignments are too easy or hard)?
