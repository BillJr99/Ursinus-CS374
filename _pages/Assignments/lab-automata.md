---
layout: assignment
permalink: /Assignments/Automata
title: "CS374: Principles of Programming Languages - Lab: Finite Automata Simulators"

info:
  coursenum: CS374
  purpose: "To build general simulators for deterministic finite automata (DFAs) and nondeterministic finite automata (NFAs) that read machine definitions from data files, so the theory beneath every lexer becomes a program you can run, and to trace the subset construction and Thompson's construction once by hand."
  tilt:
    task: "With a partner, build DFA and NFA simulators that read machines from JSON, design one machine of each kind, and trace the subset construction and Thompson's construction by hand on small examples."
    criteria: "I grade correct simulators that handle the stated edge cases, two annotated machine designs, and by-hand construction traces.  The rubric below breaks this down in full."
  points: 15
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
      preemerging: The DFA simulator fails to run, or fails most provided machines because of major structural errors
      beginning: The DFA simulator runs but fails several test cases because of minor issues such as incorrect transition lookups or missing alphabet validation
      progressing: The DFA simulator passes the provided test cases but mishandles edge cases such as the empty string or symbols outside the alphabet, or the designed DFA lacks state annotations
      proficient: A correct DFA simulator passes all provided test machines, handles the empty string and out-of-alphabet symbols deliberately, supports trace mode, and runs the designed DFA with documented state meanings and passing tests
    - weight: 36
      description: "NFA Simulation and Design (Goals 1, 2)"
      preemerging: The NFA simulator is missing, or fails to compute epsilon-closures correctly
      beginning: The NFA simulator runs but produces incorrect results on several machines because of epsilon-closure errors or incorrect powerset tracking
      progressing: The NFA simulator passes the provided test cases but would fail on machines with epsilon cycles, or the designed NFA does not actually use nondeterminism
      proficient: A correct NFA simulator computes epsilon-closures with cycle detection, tracks the set of active states, and passes all provided test machines plus the designed NFA with traced execution paths
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

In this lab you build the machines beneath your lexer: general simulators for deterministic finite automata (DFAs) and nondeterministic finite automata (NFAs).  A finite automaton is a small machine that reads a string one symbol at a time, moves between states, and accepts or rejects the string when the input runs out.  A DFA has exactly one next state for each state and symbol.  An NFA may have several next states, or none, and it may move without reading a symbol at all.  Your simulators read each machine's definition from a JSON data file instead of hard-coding it, so one program runs every machine you or I hand it.  You also design one machine of each kind and trace two classic constructions by hand; Parts 0 and 3 are paper exercises with no code.  You leave with a working DFA and NFA engine, two machines you designed yourself, and a by-hand feel for the two algorithms that turn regular expressions into the tables inside every lexer generator.

**Pair policy.**  You may do this lab in pairs.  Work together at one screen, or split the DFA and NFA halves and review each other's work.  Either way, both of you submit the same ZIP, each naming the other in the writeup, and you both earn the same grade.  You may also work alone if you prefer.  Unlike the programming assignments, no individual-work certification is required here; the reflection asks who did what instead.

---

## Part 0: Before You Start - Regular Expressions and Finite Automata

Do this part on paper before you write any simulator code.  You may do it alone even though the rest of this lab is pair work.  A regular expression and a finite automaton are two ways to describe the same set of strings, and building both for one language is the fastest way to see that they agree.

### Step 0.1: Write a Regular Expression and a Matching NFA

> **Do this.**
> 1. Pick a token class, such as identifiers or floating-point literals.
> 2. Write a regular expression for it.
> 3. Draw an NFA that accepts the same language.  Mark the start state with an incoming arrow and each accepting state with a double circle.
> 4. Check both against two strings the class should accept and two it should not.  The regex and the NFA must agree on all four.

### Step 0.2: Convert a Small NFA to a DFA by Hand

The subset construction makes one DFA state for each set of NFA states the machine could be in at once.  You trace it in full in Part 3, so a short first pass here pays off twice.

> **Do this.**
> 1. Take a small NFA from the Finite Automata activity in the readings.
> 2. Apply the subset construction over two or three input symbols.  Each DFA state is a set of NFA states; write each set out in full.
> 3. Name one string the resulting DFA accepts.
> 4. If the state set stopped being obvious at some step, circle that step and write one line saying what got hard.

> **Bring to class.** Bring the construction even if it stalled, with the stalling step marked.  That stall is the useful part: Part 2 has you automate exactly that step.  When you assemble your submission, put this page in `writeup.md` under a Part 0 heading (a photo of the paper is fine).

---

## Getting Started

You need Python 3.10 or newer (only the standard library is used, so there is nothing to install), a terminal, an editor such as VS Code, and your Part 0 paper work so you have a machine in mind when you meet the JSON format.  If the terminal is new to you, read the [dev environment tutorial]({{ site.baseurl }}/Tutorials/DevEnvironment) and the [shell primer]({{ site.baseurl }}/Tutorials/ShellForLanguageDev) first; they cover every command on this page.

Confirm your Python version:

```bash
python3 --version
```

```text
Python 3.11.4
```

Any version 3.10 or newer works.  If the command is not found, try `python --version` instead, and use whichever name works for the rest of this page.  Then create a project folder with a `machines/` folder inside it and move into it:

```bash
mkdir -p cs374-automata/machines
cd cs374-automata
```

Open the folder in your editor and create two empty files at the top level: `simulator.py` (the loader, `run_dfa`, `eps_closure`, `run_nfa`, and the command line) and `writeup.md` (Part 0 work, construction traces, and reflection).  Each machine goes in `machines/` as its own JSON file.

> **Time budget.** This lab follows the class material on regular expressions and finite automata; see the course schedule for the assigned and due dates.  One focused session with your partner covers Parts 1 and 2; plan on about three hours.  The paper work in Parts 0 and 3 fits in a second sitting of about an hour.  Write the reflection as you go rather than at the end.
> - On assignment: loader and DFA simulator working against the provided machines.
> - Midpoint: NFA simulator with epsilon-closure working; both designed machines encoded and tested.
> - Due date: construction traces and writeup assembled; ZIP submitted.

### Your First 15 Minutes

Start with a machine, not with the simulator.  The smallest program that runs one machine is ten lines, and once it works, the rest of Part 1 is wrapping it in validation, a machine-file argument, and `--trace`.

> **Do this.**
> 1. Copy the parity machine JSON from Step 1.1 into `machines/even_ones.json`.
> 2. In `simulator.py`, write a ten-line core: `json.load` the file, set `state` to `machine["start"]`, and for each symbol of `sys.argv[1]` set `state = machine["delta"][state][symbol]`.
> 3. Print `accept` if the final state is in `machine["accept"]`, otherwise `reject`.
> 4. From inside `cs374-automata`, run `python3 simulator.py 0110` and then `python3 simulator.py 100`.  You should see `accept`, then `reject`, matching the traces in Step 1.1.
> 5. A `FileNotFoundError` means you ran from a different folder; a `JSONDecodeError` means a missing comma or quote, and the message names the line.

---

## Part 1: DFA Simulation and Design

### Step 1.1: Read the Machine Format and Encode the Parity Machine

Every machine is a JSON (JavaScript Object Notation) file with these keys:

| Key | Type | Meaning |
|-----|------|---------|
| `states` | list of strings | all state names |
| `alphabet` | list of strings | all input symbols (each a single character) |
| `start` | string | the initial state |
| `accept` | list of strings | the accepting states |
| `delta` | object | transition function |

For a DFA, `delta` is a nested object: `delta[state][symbol]` gives the next state, and every (state, symbol) pair over the alphabet must appear.

Here is the two-state parity machine for "even number of 1s", first as a state diagram and then as the JSON you type in.  In the diagram, `start -->` marks the start state, double parentheses mark an accepting state, and each arrow carries the symbol that triggers it.

```text
             0                        0
           +----+                   +----+
           |    |                   |    |
           |    v         1         |    v
  start -->((even))--------------->( odd )
              ^                       |
              |           1           |
              +-----------------------+
```

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

Every arrow in the diagram is one entry in `delta`: the `1` arrow from `even` to `odd` is the `"1": "odd"` inside `"even"`.  The double parentheses are the `accept` list, and the `start -->` arrow is the `start` key.  If you skipped Your First 15 Minutes, save the JSON as `machines/even_ones.json` now.  Then trace `"0110"` and `"100"` through the diagram with your finger before you trust the program to do it:

```text
"0110": even -> even -> odd -> even -> even    accept
"100":  even -> odd -> odd -> odd              reject
```

### Step 1.2: Write the Loader

A wrong machine file is the most common bug in this lab.  A loader that checks the file once, up front, and names every problem at the same time saves you from chasing a `KeyError` deep inside the simulator.

> **Do this.**
> 1. Replace the ten-line core in `simulator.py` with the skeleton below and fill in the `# TODO` lines.
> 2. `load_machine(path)` reads a JSON file and checks that the start state, the accept states, and every transition refer only to declared states and alphabet symbols.
> 3. Collect every validation error into a list and raise a single `MachineError` that lists them, one per line.  Do not stop at the first one.
> 4. Accept both `delta` shapes.  A DFA's `delta` is an object of objects.  An NFA's `delta` (Part 2) has `"state,symbol"` keys with list values, and the symbol half may be the special word `eps`.  Write the check so `eps` passes for an NFA and nothing else outside the alphabet does.

```python
import json
import sys


class MachineError(Exception):
    """Raised by load_machine with every validation problem listed at once."""


def is_nfa(machine):
    # An NFA's delta values are lists of states; a DFA's are objects (Part 2).
    return any(isinstance(v, list) for v in machine["delta"].values())


def load_machine(path):
    with open(path) as f:
        machine = json.load(f)
    errors = []
    states = set(machine["states"])
    alphabet = set(machine["alphabet"])
    # TODO: the start state must be in states
    # TODO: every accept state must be in states
    # TODO: DFA: every delta[state][symbol] must name a declared state, and
    #       every (state, symbol) pair over the alphabet must appear
    # TODO: NFA: every "state,symbol" key must split into a declared state and
    #       either an alphabet symbol or "eps"; every target must be declared
    if errors:
        raise MachineError("\n".join(errors))
    return machine
```

Check the loader against the good file first:

```bash
python3 -c "import simulator; simulator.load_machine('machines/even_ones.json')"
```

> **You should see.** Nothing at all; silence means the file passed.  Now change `"accept": ["even"]` to `"accept": ["evn"]` in `machines/even_ones.json`, save, and run the same command again.  This time you should see a traceback ending in a line like `simulator.MachineError: accept state 'evn' is not a declared state` (your wording may differ).  Put `"even"` back before you continue.

### Step 1.3: Write `run_dfa` and the Command Line

The ten-line core crashed on a symbol it did not know and had the machine path hard-coded.  This step fixes both and adds trace mode.

> **Do this.**
> 1. Add `run_dfa(machine, s, trace=False) -> bool` below the loader, with these rules:
>    - Any symbol in `s` that is not in the machine's alphabet is an immediate reject.  Print a reason; do not crash.
>    - The empty string `""` is valid input.  It tests whether the start state is an accept state.
>    - With `trace` on, print the current state after each symbol.
> 2. Add a `main` that takes the machine path and the input string from the command line and honors a `--trace` flag.

```python
def run_dfa(machine, s, trace=False):
    state = machine["start"]
    if trace:
        print(f"start: {state}")
    for symbol in s:
        # TODO: if symbol is not in the alphabet, print a reason and return False
        # TODO: move to machine["delta"][state][symbol]
        # TODO: if trace, print f"read {symbol} -> {state}"
        pass
    return state in machine["accept"]


def main(argv):
    # Usage: python3 simulator.py <machine.json> <string> [--trace]
    trace = "--trace" in argv
    args = [a for a in argv if a != "--trace"]
    machine = load_machine(args[0])
    s = args[1] if len(args) > 1 else ""
    run = run_nfa if is_nfa(machine) else run_dfa   # run_nfa arrives in Part 2
    print("accept" if run(machine, s, trace) else "reject")


if __name__ == "__main__":
    main(sys.argv[1:])
```

Try all three rules:

```bash
python3 simulator.py machines/even_ones.json 0110 --trace
python3 simulator.py machines/even_ones.json ""
python3 simulator.py machines/even_ones.json 0120
```

> **You should see.** For the first command, one state per symbol and then the verdict:
>
> ```text
> start: even
> read 0 -> even
> read 1 -> odd
> read 1 -> even
> read 0 -> even
> accept
> ```
>
> For the empty string, `accept` on its own, because the start state `even` is accepting.  For the third command, a one-line reason such as `reject: symbol '2' is not in the alphabet` followed by `reject`, and no traceback.

> **Checkpoint.** Test against the parity machine with at least four accepted strings and four rejected strings.  Record each string and its result in `writeup.md` under a heading for the machine.

### Step 1.4: Design the Ends-in-ab DFA

Designing a DFA means deciding what each state needs to remember.  Here the answer is short: how much of the suffix `ab` has the machine seen most recently?

> **Do this.**
> 1. Design a DFA for **Ends in ab**: strings over `{a, b}` that end with the suffix `ab`.
> 2. Draw it on paper first, then encode it as `machines/ends_in_ab.json` in the same format as the parity machine.
> 3. In `writeup.md`, annotate each state with one sentence saying what it "remembers" about the input so far.
> 4. Test with at least four accepted and four rejected strings, and record them in the writeup next to the state annotations.

Worked example: `"aab"` -> accept; `"ba"` -> reject; `"ab"` -> accept; `""` -> reject.  Hint: you need at least three states.

```bash
python3 simulator.py machines/ends_in_ab.json aab
python3 simulator.py machines/ends_in_ab.json ba
python3 simulator.py machines/ends_in_ab.json ""
```

> **You should see.** `accept`, `reject`, `reject`.  If the empty string accepts, your start state is marked accepting; the empty string does not end in `ab`.

> **If it fails.**
> - `MachineError` naming a missing (state, symbol) pair: a DFA needs a transition out of every state on both `a` and `b`, including the "just saw `ab`" state.
> - `"abb"` accepts: after `ab`, reading `b` must forget the suffix entirely, not step back one state.
> - `"aab"` rejects: after `a`, reading another `a` must stay in the "just saw `a`" state, because the newer `a` could still start the suffix.

---

## Part 2: NFA Simulation and Design

### Step 2.1: Read the NFA Machine Format

For an NFA, `delta` maps `"state,symbol"` string keys to lists of states.  The special symbol `"eps"` marks an epsilon (ε) transition, a move the machine may take without reading any input.  A state may have zero or more targets for any symbol.  The other keys work as they do for a DFA; do not list `eps` in `alphabet`, because it is a transition label, not an input symbol.

Here is a fragment of an NFA, as a diagram and then as JSON.  The fragment does not say which states accept, so none are double-circled.

```text
            a
          +----+
          |    |
          |    v        a               b
  ... -->( q0 )--------------->( q1 )--------------->( q2 )
            |                                          ^
            |                  eps                     |
            +------------------------------------------+
```

```json
"delta": {
  "q0,a": ["q0", "q1"],
  "q0,eps": ["q2"],
  "q1,b": ["q2"]
}
```

The `a` arrows out of `q0` go two ways, so `"q0,a"` lists two targets: that is the nondeterminism.  Pairs with no arrow (`q1` on `a`, or `q2` on anything) have no key, so read transitions with `machine["delta"].get(key, [])` and a missing key means "no moves" instead of a `KeyError`.

### Step 2.2: Implement the Epsilon-Closure

The epsilon-closure of a set of states is every state you can reach from that set by following only `"eps"` transitions, including the starting states themselves.  Start with the given set, follow every `"eps"` transition out of it and add the targets, and repeat until no new state appears.  A state may epsilon-transition back to itself or to a predecessor, and your loop must still stop; the check "is this target already in the closure?" is the whole of cycle detection.  For example, if `q0 -ε-> q1`, `q1 -ε-> q2`, and `q2 -ε-> q0`, then `eps_closure(m, {"q0"}) = {"q0", "q1", "q2"}`.

> **Do this.**
> 1. Add `eps_closure(machine, states) -> frozenset` to `simulator.py` and fill in the `# TODO` lines.  It returns a `frozenset` so a closure can sit inside another set later.
> 2. Save the three-state cycle below as `machines/eps_cycle.json`.  It is a test machine only; you do not need to submit it.
> 3. Run the check command.

```python
def eps_closure(machine, states):
    """Every state reachable from `states` by eps moves alone, including `states`."""
    closure = set(states)
    frontier = list(states)   # states whose eps edges you have not followed yet
    while frontier:
        state = frontier.pop()
        # TODO: look up machine["delta"].get(f"{state},eps", [])
        # TODO: for each target not already in closure, add it and push it on frontier
        pass
    return frozenset(closure)
```

```json
{
  "states": ["q0", "q1", "q2"],
  "alphabet": ["a"],
  "start": "q0",
  "accept": ["q2"],
  "delta": {"q0,eps": ["q1"], "q1,eps": ["q2"], "q2,eps": ["q0"]}
}
```

```bash
python3 -c "import simulator as s; m = s.load_machine('machines/eps_cycle.json'); print(sorted(s.eps_closure(m, {'q0'})))"
```

> **You should see.** `['q0', 'q1', 'q2']` on one line.

> **If it fails.**
> - The command never finishes: you push targets onto the frontier without checking whether they are already in the closure, so the cycle runs forever.  Press Ctrl+C to stop it.
> - `['q0']` only: you read `delta["q0,eps"]` once instead of following eps edges out of every newly added state.
> - `MachineError` mentioning `eps`: your loader from Step 1.2 rejects `eps` as an unknown symbol.  Allow it for NFAs.

### Step 2.3: Implement `run_nfa`

A DFA is in one state at a time.  An NFA is in a set of states at a time, and `run_nfa` tracks that set:

1.  Compute the epsilon-closure of `{start}` as the initial set of active states.
2.  For each symbol in `s`, take the union of all `delta["state,symbol"]` lists over all active states, then take the epsilon-closure of that union.
3.  Accept if the final active set shares at least one state with the accept set.

> **Do this.**
> 1. Add `run_nfa(machine, s, trace=False) -> bool` below `eps_closure` and fill in the `# TODO` lines.  `main` from Step 1.3 already picks `run_nfa` when `is_nfa` says so.
> 2. With `trace` on, print the sorted active set after each symbol, the NFA counterpart of the single state a DFA prints.

```python
def run_nfa(machine, s, trace=False):
    active = eps_closure(machine, {machine["start"]})
    if trace:
        print(f"start: {sorted(active)}")
    for symbol in s:
        # TODO: union machine["delta"].get(f"{state},{symbol}", []) over every state in active
        # TODO: active = eps_closure(machine, that union)
        # TODO: if trace, print f"read {symbol} -> {sorted(active)}"
        pass
    return any(state in machine["accept"] for state in active)
```

Smoke-test it on the cycle machine from Step 2.2:

```bash
python3 simulator.py machines/eps_cycle.json ""
python3 simulator.py machines/eps_cycle.json a
```

> **You should see.** `accept`, then `reject`.  The empty string accepts because the epsilon-closure of `q0` already contains the accepting state `q2`.  The string `a` rejects because no state has an `a` move, so the active set becomes empty and stays empty.  An empty active set is a reject, never a crash.

### Step 2.4: Design the Contains-aa NFA

An NFA lets you guess.  Here the guess is "the `aa` starts here," and the machine keeps every guess alive at once.

> **Do this.**
> 1. Design an NFA for **Contains aa**: strings over `{a, b}` containing the substring `aa` somewhere.
> 2. Encode it as `machines/contains_aa.json`.
> 3. Test with at least four accepted and four rejected strings, and record them in `writeup.md`.
> 4. Include the `--trace` output for at least one accepted string in the writeup, so the execution path is visible.

Worked example: `"baaab"` -> accept; `"ababab"` -> reject.  Hint: nondeterministically guess where `aa` occurs.  Your design should really use nondeterminism, not be a DFA in disguise.

> **Watch out.** At least one `"state,symbol"` key in your JSON should list two or more targets.  If every list has exactly one entry and there is no `eps` key, you have written a DFA in NFA clothing.

```bash
python3 simulator.py machines/contains_aa.json baaab --trace
python3 simulator.py machines/contains_aa.json ababab
```

> **You should see.** A trace whose active set grows when the machine guesses that an `a` starts the `aa`, then `accept`; and `reject` for `ababab`.  Your state names will differ, but the shape looks like this:
>
> ```text
> start: ['q0']
> read b -> ['q0']
> read a -> ['q0', 'q1']
> read a -> ['q0', 'q1', 'q2']
> read a -> ['q0', 'q1', 'q2']
> read b -> ['q0', 'q2']
> accept
> ```

---

## Part 3: By-Hand Constructions

These are paper exercises in your writeup, with no code.  You trace each algorithm once on a small example, so you have run by hand what lexer-generator tools automate.

### Step 3.1: Trace the Subset Construction

> **Do this.**
> 1. Apply the subset construction to your Contains aa NFA from Part 2 to produce an equivalent DFA.
> 2. Fill in the construction table below in `writeup.md`, one row per powerset state.
> 3. Record how many DFA states result.

The algorithm:

1.  Start with `eps_closure({start})` as the first powerset state.
2.  For each powerset state you have not yet processed, compute its transitions on each symbol and epsilon-close the results.  Each result is a new row if you have not seen it before.
3.  Mark a powerset state as accepting if it contains any NFA accept state.
4.  Continue until every powerset state has been processed.

> **Paste into your submission.** Copy this table into `writeup.md` and fill it in.

| Powerset State | on `a` | on `b` | Accepting? |
|----------------|--------|--------|------------|
| {q0} | ... | ... | No/Yes |
| ... | | | |

> **Checkpoint.** Your simulator can confirm your table.  Run `python3 simulator.py machines/contains_aa.json <string> --trace` for a few strings: every set the trace prints should be one of your powerset states, and the arrows between them should match your `on a` and `on b` columns.

### Step 3.2: Trace Thompson's Construction

Thompson's construction turns a regular expression into an NFA one operator at a time, gluing small fragments together with ε-transitions.

> **Do this.**
> 1. Apply Thompson's construction to the regular expression `a(b|c)*` in `writeup.md`.
> 2. Show each sub-expression and its fragment, labeling every state and every ε-transition, in this order:
>    1. Fragment for `a`.
>    2. Fragments for `b` and `c`.
>    3. Fragment for `b|c` (union).
>    4. Fragment for `(b|c)*` (Kleene star).
>    5. Concatenation: `a` then `(b|c)*`.

For reference, the fragment rules are:

- A single character: a start state and an accept state joined by one transition labeled with that character.
- Concatenation of A then B: connect A's accept to B's start with ε.
- Union of A and B: add a new start with ε to both fragments' starts, and ε from both accepts to a new shared accept.
- Kleene star of A: add a new start with ε to A's start and to a new accept, plus ε from A's accept back to A's start and on to the new accept.

### Step 3.3: Connect the Simulators to Your Lexer

> **Do this.**
> 1. Write one paragraph in `writeup.md` connecting these simulators to the lexer you will build next.  Which component of the lexer plays the role of your simulators?

---

## Deliverables

Submit a ZIP containing the files below.  List your Python version in the writeup so I can reproduce your results.

| File or artifact | What it shows | Rubric row |
|------------------|---------------|------------|
| `simulator.py` | `load_machine`, `run_dfa`, `eps_closure`, `run_nfa`, and the command-line entry point | Parts 1 and 2 |
| `machines/even_ones.json` | the provided parity machine, unchanged | Part 1 |
| `machines/ends_in_ab.json` | your designed DFA | Part 1 |
| `machines/contains_aa.json` | your designed NFA | Part 2 |
| `writeup.md` | Part 0 paper work; state annotations and test strings for both designed machines; the subset-construction table with the DFA state count; the Thompson's construction fragments; the paragraph connecting these simulators to the lexer you will build next (which component of the lexer plays the role of your simulators?); both partners' names | Parts 0, 1, 2, 3 |

---

## Self-Check Before You Submit

- [ ] `python3 simulator.py machines/even_ones.json 0110` prints `accept`, and the same command with `100` prints `reject`.
- [ ] The empty string and an out-of-alphabet symbol each produce a deliberate answer, not a traceback.
- [ ] `--trace` prints a state (DFA) or a sorted set of states (NFA) after every symbol.
- [ ] `load_machine` on a deliberately broken file raises one `MachineError` that lists every problem.
- [ ] `eps_closure` stops on `machines/eps_cycle.json` and returns all three states.
- [ ] Each state of the Ends-in-ab DFA has a one-sentence annotation, and both designed machines have at least four accepted and four rejected test strings recorded.
- [ ] The Contains-aa NFA has at least one state with two or more targets on the same symbol.
- [ ] `writeup.md` has the Part 0 work, the subset-construction table with the DFA state count, every Thompson fragment labeled, the lexer paragraph, both names, and your Python version.

---

## Reflection Prompts

- Contrast designing the NFA with tracing its equivalent DFA via subset construction: where did the complexity move?
- Your simulators treat machines as data (loaded from JSON).  Name one benefit this brought during testing that hard-coded machines would have denied you.
- If you worked in a pair, who did what, and name one thing your partner caught that you would have missed.  If you worked alone, note that instead.
