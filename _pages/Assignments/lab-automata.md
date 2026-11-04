---
layout: assignment
permalink: /Assignments/Automata
title: "CS374: Principles of Programming Languages - Lab: Finite Automata Simulators"

info:
  coursenum: CS374
  purpose: "To build general simulators for deterministic finite automata (DFAs) and nondeterministic finite automata (NFAs) that read machine definitions from data files, so the theory beneath every lexer becomes a program you can run, and to build Thompson's construction once by hand."
  tilt:
    task: "Individually or with a partner, build DFA and NFA simulators that read machines from JSON, design one machine of each kind, and build one Thompson's construction NFA by hand."
    criteria: "I grade correct simulators that handle the stated edge cases, two annotated machine designs, and a by-hand Thompson construction.  The rubric below breaks this down in full."
  points: 15
  goals:
    - To implement general DFA and NFA simulators over machine definitions loaded from JSON
    - To design one DFA and one NFA for specified languages and encode them as data
    - To trace a small subset construction and build a Thompson's construction NFA by hand
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
      preemerging: The Thompson construction is not attempted, or is fundamentally incorrect
      beginning: The NFA for a(b|c)* is attempted but contains significant errors, such as a wrong or missing operator rule
      progressing: The NFA for a(b|c)* follows the rules with minor errors, such as a missing or misdirected epsilon arrow or an unnumbered state
      proficient: The finished Thompson NFA for a(b|c)* is correct, with every state numbered, every epsilon arrow marked, and the start and accepting states identified
  readings:
    - rtitle: "Finite Automata Activity"
      rlink: "Activities/liascript-automata.md"
      liapage: true
    - rtitle: "Grammars and the Chomsky Hierarchy Activity"
      rlink: "Activities/liascript-grammars.md"
      liapage: true
    - rtitle: "FSM Simulator (step a DFA, NFA, or epsilon-NFA one symbol at a time; it writes epsilon as $)"
      rlink: "https://ivanzuzak.info/noam/webapps/fsm_simulator/"
    - rtitle: "FSM2Regex (convert a regular expression to an automaton and back)"
      rlink: "https://ivanzuzak.info/noam/webapps/fsm2regex/"
    - rtitle: "Automata Studio (NFA to DFA by subset construction with the full subset table, and DFA minimization)"
      rlink: "https://reyescarlata0.github.io/automata-studio/"

tags:
  - automata
  - theory
  - languages
  - lab

---

In this lab you write two programs that run finite automata: a DFA simulator and an NFA simulator.  Each one reads a machine from a JSON file, so a single program runs any machine you or I give it.  These machines sit underneath every lexer, including the one you build next.  You also design one DFA and one NFA, and you build one classic construction by hand.  Parts 0 and 3 are paper work; Parts 1 and 2 are code.

**Pair policy.**  You may work in pairs or alone.  A pair can share one screen, or split the DFA and NFA halves and review each other's work.  Both partners submit the same ZIP, name each other in the writeup, and earn the same grade.  This lab needs no individual-work certification.  The reflection asks who did what instead.

---

## Background in the Class Notes

The class notes cover every idea this lab uses, with a worked example of each.  Read these before Part 0, and come back when a step points to one:

- [What a DFA is, and how to trace one](https://liascript.github.io/course/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374-Fall2026/gh-pages/_pages/Activities/liascript-automata.md#5)
- [A DFA as JSON, and in Python](https://liascript.github.io/course/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374-Fall2026/gh-pages/_pages/Activities/liascript-automata.md#15)
- [Designing a DFA by asking what it must remember](https://liascript.github.io/course/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374-Fall2026/gh-pages/_pages/Activities/liascript-automata.md#17), with [a worked machine](https://liascript.github.io/course/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374-Fall2026/gh-pages/_pages/Activities/liascript-automata.md#18)
- [What an NFA is](https://liascript.github.io/course/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374-Fall2026/gh-pages/_pages/Activities/liascript-automata-day2.md#3)
- [Reading an NFA's transitions](https://liascript.github.io/course/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374-Fall2026/gh-pages/_pages/Activities/liascript-automata-day2.md#10)
- [Python's `set` and `frozenset`](https://liascript.github.io/course/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374-Fall2026/gh-pages/_pages/Activities/liascript-automata-day2.md#11)
- [One step of an NFA: move, then close](https://liascript.github.io/course/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374-Fall2026/gh-pages/_pages/Activities/liascript-automata-day2.md#12)
- [The ε-closure](https://liascript.github.io/course/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374-Fall2026/gh-pages/_pages/Activities/liascript-automata-day2.md#17)
- [The subset construction](https://liascript.github.io/course/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374-Fall2026/gh-pages/_pages/Activities/liascript-automata-day2.md#16), and [with ε-moves and a dead state](https://liascript.github.io/course/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374-Fall2026/gh-pages/_pages/Activities/liascript-automata-day2.md#18)
- [Thompson's construction](https://liascript.github.io/course/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374-Fall2026/gh-pages/_pages/Activities/liascript-automata-day2.md#27)

---

## Part 0: Before You Start - Regular Expressions and Finite Automata

Do this part on paper before you write any code.  You may do it alone, even if you do the rest of the lab with a partner.  A regular expression and a finite automaton are two ways to describe the same set of strings.  Building both for one language is the fastest way to see that they agree.

### Step 0.1: Write a Regular Expression and a Matching NFA

**You write (on paper, then in `writeup.md` under a `## Part 0` heading):** a regular expression, a drawn NFA, and four test strings.  No code.

*Example.*  An identifier is a letter followed by any number of letters or digits.  Let `L` stand for any letter and `D` for any digit.  The regex is `L(L|D)*`, and this two-state NFA accepts the same language:

![NFA for identifiers. States q0 and q1; q0 is the start state and q1 is the only accepting state. q0 goes to q1 on a letter L, and q1 loops to itself on a letter L or a digit D.]({{ site.baseurl }}/files/dotty/lab_identifier_nfa.svg)

On `x1`, the machine moves from `q0` to `q1` on `x` and loops on `1`, so it accepts.  On `1x`, `q0` has no arrow for a digit, so it rejects.  The regex agrees, because `1x` does not start with a letter.  Choose a different token class for your own work.

> **Do this.**
> 1. Pick a token class, such as floating-point literals, integer literals with an optional sign, or string literals.
> 2. Write a regular expression for it.
> 3. Draw an NFA that accepts the same language.  Mark the start state with an incoming arrow and each accepting state with a double circle.
> 4. Test both on two strings the class should accept and two it should not.  The regex and the NFA must agree on all four.

### Step 0.2: Convert a Small NFA to a DFA by Hand

**You write (on paper, then in `writeup.md` under the same `## Part 0` heading):** a partial subset-construction table and one accepted string.  No code.

The subset construction makes one DFA state for each set of NFA states the machine could be in at once.  [The class notes work a small example](https://liascript.github.io/course/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374-Fall2026/gh-pages/_pages/Activities/liascript-automata-day2.md#16).  You trace it in full in Part 3, so a short first pass now pays off twice.

Use this NFA over `{a, b}`.  It accepts strings whose second-to-last symbol is `a`.  It starts in `q0`, accepts in `q2`, and has no ε-moves.  On each `a`, `q0` may guess that this is the second-to-last symbol:

![NFA for strings whose second-to-last symbol is a. States q0, q1, and q2; q0 is the start state and q2 is the only accepting state. q0 loops to itself on a or b, q0 goes to q1 on a, and q1 goes to q2 on a or b.]({{ site.baseurl }}/files/dotty/lab_second_to_last_nfa.svg)

| state | on `a` | on `b` |
|---|---|---|
| q0 | {q0, q1} | {q0} |
| q1 | {q2} | {q2} |
| q2 | ∅ | ∅ |

Here is the first row, worked, to show what each cell asks for.  Start at `{q0}`.  On `a`, the set holds only `q0`, and $$\delta(q0, a) = \{q0, q1\}$$, so the cell is `{q0, q1}`.  On `b`, $$\delta(q0, b) = \{q0\}$$, so the cell is `{q0}`.  The new set `{q0, q1}` is the next row to process.  In that row, each cell is the union over both states.  On `a`, for example, it is $$\delta(q0, a) \cup \delta(q1, a)$$.

> **Do this.**
> 1. Copy the NFA and its table into your notes.
> 2. Continue the subset construction from `{q0, q1}` until no new sets appear, or for at least two or three input symbols.  Write each DFA state as its full set of NFA states.  For each cell, write the union you took, in the form `q0 -> {...} ∪ q1 -> {...}`.
> 3. Name one string the resulting DFA accepts.
> 4. If the sets stopped being obvious at some step, circle that step and write one line about what got hard.

> **Bring to class.** Bring your construction even if it stalled, with the stalling step marked.  The stall is useful, because Part 2 has you automate that step.  When you assemble your submission, put this page in `writeup.md` under a Part 0 heading.  A photo of the paper is fine.

---

## Getting Started

You need Python 3.10 or newer, a terminal, and an editor such as VS Code.  The lab uses only the standard library, so there is nothing to install.  Keep your Part 0 work nearby so you have a machine in mind when you meet the JSON format.  If the terminal is new to you, read the [dev environment tutorial]({{ site.baseurl }}/Tutorials/DevEnvironment) and the [shell primer]({{ site.baseurl }}/Tutorials/ShellForLanguageDev) first.  Together they cover every command on this page.

Check your Python version:

```bash
python3 --version
```

```text
Python 3.11.4
```

Any version from 3.10 up works.  If the shell cannot find `python3`, try `python --version`, and use whichever name works for the rest of this page.  Next, create a project folder with a `machines/` folder inside it, and move into it:

```bash
mkdir -p cs374-automata/machines
cd cs374-automata
```

Open the folder in your editor and create one empty file at the top level, `writeup.md`.  It holds your Part 0 work, your test strings, your Thompson NFA, and your reflection.  You create the two Python files when the steps ask for them, and each machine goes in `machines/` as its own JSON file.  This table shows which file each step writes, so you always know where new code goes:

| Step | File you work in | What you do there |
|---|---|---|
| 0.1, 0.2 | `writeup.md` | add your Part 0 paper work |
| 1.1 | `dfa_core.py` | create a ten-line DFA runner, then leave it alone |
| 1.1, 1.4 | `machines/even_ones.json`, `machines/ends_in_ab.json` | create the DFA machine files |
| 1.2.1 to 1.2.5 | `simulator.py` | create the file, write the three checker helpers one at a time, then integrate them into the loader |
| 1.3.1 to 1.3.4 | `simulator.py` | add `run_dfa` one rule at a time, then `main` |
| 2.1, 2.3, 2.4 | `machines/ends_in_ab_nfa.json`, `machines/ab_optional.json`, `machines/eps_cycle.json`, `machines/contains_aa.json` | create the NFA machine files |
| 2.2.1, 2.2.2 | `simulator.py` | add the `nfa_move` helper, then a first `run_nfa` without ε-moves |
| 2.3.1, 2.3.2 | `simulator.py` | add `eps_closure`, then change two lines of `run_nfa` to use it |
| 3.1 | `writeup.md` | add your Thompson NFA for `a(b\|c)*` |

> **Time budget.** This lab follows the class material on regular expressions and finite automata.  The course schedule has the assigned and due dates.  Plan about three hours (with your partner, if you have one) for Parts 1 and 2, and about an hour for the paper work in Parts 0 and 3.  Write the reflection as you go, not at the end.
> - On assignment: the loader and DFA simulator work on the provided machines.
> - Midpoint: the NFA simulator and epsilon-closure work, and both designed machines are encoded and tested.
> - Due date: the Thompson NFA and writeup are assembled and the ZIP is submitted.

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

For a DFA, `delta` is a nested object.  `delta[state][symbol]` gives the next state, and the object must contain every (state, symbol) pair over the alphabet.

Here is the two-state parity machine for "even number of 1s," first as a diagram and then as the JSON you type.  In the diagram, the arrow from nowhere marks the start state, a double circle marks an accepting state, and each arrow carries the symbol that triggers it.

![DFA for an even number of 1s. States even and odd; even is the start state and the only accepting state. Each state loops to itself on 0, even goes to odd on 1, and odd goes back to even on 1.]({{ site.baseurl }}/files/dotty/even_ones.svg)

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

Each arrow in the diagram is one entry in `delta`.  The `1` arrow from `even` to `odd`, for example, is the `"1": "odd"` inside `"even"`.  The double circle is the `accept` list, and the arrow from nowhere is the `start` key.  Save the JSON as `machines/even_ones.json`.  Then trace `"0110"` and `"100"` through the diagram by hand before you trust the program:

| String | States visited | Result |
|---|---|---|
| `0110` | even → even → odd → even → even | accept |
| `100` | even → odd → odd → odd | reject |

#### Before You Code: How a DFA Lives in Python

When `json.load` reads the file above, each JSON object becomes a Python dictionary, so finding the next state takes two lookups: `delta[state]` picks the row for the current state, and `[symbol]` picks the arrow.  Together, `delta["even"]["1"]` is `'odd'`.  The class notes [walk through this with code you can run](https://liascript.github.io/course/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374-Fall2026/gh-pages/_pages/Activities/liascript-automata.md#15).

Start with this one machine, not with the full simulator.  The smallest program that runs it is about ten lines long, and you write it now in its own file, `dfa_core.py`.  Every later step builds on the same idea, so you see it work in its simplest form first.

**You write:** `machines/even_ones.json` (above) and a new file, `dfa_core.py`.
**You run:** `python3 dfa_core.py 0110` and `python3 dfa_core.py 100`.

*Write `dfa_core.py` one piece at a time.*  Each piece of the program matches one part of the diagram, so read the sentence beside each piece before you type it.

1. Bring in the two modules you need.  `json` reads the machine file, and `sys` gives you the input string from the command line.

   ```python
   import json
   import sys
   ```

2. Load the machine.  `json.load` turns the file into a Python dictionary, so `machine["start"]`, `machine["accept"]`, and `machine["delta"]` are the keys you saw in the table above.

   ```python
   with open("machines/even_ones.json") as f:
       machine = json.load(f)
   ```

3. Put the machine in its start state.  This line is the arrow from nowhere in the diagram.

   ```python
   state = machine["start"]
   ```

4. Read the input one symbol at a time.  `sys.argv[1]` is the first word you type after the program name, so in `python3 dfa_core.py 0110` it is the string `"0110"`, and looping over a string gives one character per pass.

   ```python
   for symbol in sys.argv[1]:
   ```

5. Inside the loop, follow one arrow.  `machine["delta"][state]` is the row for the current state, and `[symbol]` picks the arrow for this symbol.  This line is the transition function $$\delta(q, a)$$ written in Python.  The rest of the file loads the machine and reports the result.

   ```python
       state = machine["delta"][state][symbol]
   ```

6. After the loop, check for a double circle.  The input has run out, so the machine accepts exactly when the state it ended in is in the `accept` list.

   ```python
   if state in machine["accept"]:
       print("accept")
   else:
       print("reject")
   ```

Put together, the whole file is eleven lines:

```python
import json
import sys

with open("machines/even_ones.json") as f:
    machine = json.load(f)

state = machine["start"]
for symbol in sys.argv[1]:
    state = machine["delta"][state][symbol]

if state in machine["accept"]:
    print("accept")
else:
    print("reject")
```

> **Do this.**
> 1. Type `dfa_core.py` piece by piece as shown above, and save it in `cs374-automata`, next to the `machines/` folder.
> 2. From inside `cs374-automata`, run `python3 dfa_core.py 0110` and then `python3 dfa_core.py 100`.
> 3. **Predict** before you run it: what should `python3 dfa_core.py ""` print, and why?  Run it and check.

> **You should see.** `accept`, then `reject`, matching the hand traces above.  The empty string prints `accept`, because the loop never runs and the machine stays in `even`, which accepts.

> **Watch it run (optional).**  Add `print(symbol, "->", state)` as a second line inside the loop, indented to match the line above it.  Run `python3 dfa_core.py 0110` again.  The four lines it prints show each symbol and the state it led to, which is the "States visited" column of the trace table after the start state.  Remove the line when you are done, or keep it; either is fine.

> **If it fails.**
> - `FileNotFoundError`: you ran from a different folder.  `cd` into `cs374-automata` and try again.
> - `JSONDecodeError`: the JSON file has a missing comma or quote, and the message names the line.
> - `IndexError: list index out of range`: you forgot the input string.  Type it after the program name.
> - `KeyError: '2'`: you typed a symbol the machine does not know.  This program has no checks; Step 1.3 adds them.

`dfa_core.py` is now finished.  Leave it as it is, because you submit it.  It works for one machine whose path is written into the program, and it crashes on bad input.  The rest of Part 1 fixes both problems in a new file, `simulator.py`.

### Step 1.2: Write the Loader

A wrong machine file is the most common bug in this lab.  Your loader checks the file once, up front, and reports every problem at the same time.  That saves you from chasing a `KeyError` deep inside the simulator.

**You write:** a new file, `simulator.py`, containing `MachineError`, `is_nfa`, three small checker helpers, and `load_machine`.  Do not edit `dfa_core.py`.
**You run:** a one-line check after each helper, then `python3 -c "import simulator; simulator.load_machine('machines/even_ones.json')"`, then the same command on a broken file.

`load_machine(path)` reads a JSON file and checks that the start state, the accept states, and every transition refer only to declared states and alphabet symbols.  It collects every validation error in a list, then raises one `MachineError` that lists them, one per line.  It does not stop at the first error.  It accepts both `delta` shapes.  A DFA's `delta` is an object of objects.  An NFA's `delta` (Part 2) has `"state,symbol"` keys with list values, and the symbol half may be the special word `eps`.  The check must let `eps` through for an NFA and reject every other symbol outside the alphabet.

That is several separate checks, so you write each check as its own small helper and test it on its own.  Every helper follows one pattern.  It starts an empty list, tests one kind of condition, and when the condition fails, appends a sentence that names the bad value.  It returns the list and never raises.  Word your messages like the expected output below, so you can compare yours line by line.  Step 1.2.5 then integrates the helpers into `load_machine`, which joins their lists and raises once, so one run reports every problem.

Before you start, save this deliberately broken machine as `machines/broken.json`.  It has a misspelled start state, a misspelled accept state, and no arrow out of `odd` on `1`.  It is a test file, and you do not need to submit it.  Each helper's check runs on it.

```json
{
  "states": ["even", "odd"],
  "alphabet": ["0", "1"],
  "start": "evn",
  "accept": ["od"],
  "delta": {
    "even": {"0": "even", "1": "odd"},
    "odd":  {"0": "odd"}
  }
}
```

The helpers take a machine that is already a dictionary, so their checks load the JSON with `json.load` directly.  Only `load_machine` opens files itself.

#### Step 1.2.1: `MachineError` and `is_nfa`

> **Do this.** Create a new file, `simulator.py`, next to `dfa_core.py`.  Type in the lines below, then write the body of `is_nfa` from its `# Step` comments.

```python
import json
import sys


class MachineError(Exception):
    """Raised by load_machine with every validation problem listed at once."""


def is_nfa(machine):
    """Return True if machine is an NFA and False if it is a DFA."""
    # Step 1: Look at the values stored in machine["delta"].  A DFA's values
    #         are dictionaries, one row per state.  An NFA's values are lists
    #         of target states (Part 2).
    # Step 2: Return True if at least one of those values is a list, and
    #         False otherwise.
    ...
```

| Step | How to think about it |
|---|---|
| `is_nfa` | You only need to know whether some value is a list.  `isinstance(value, list)` answers that for one value, and `any(...)` asks it of all of them at once.  Part 2 is the first time it returns `True`. |

```bash
python3 -c "import json, simulator as s; print(s.is_nfa(json.load(open('machines/even_ones.json'))))"
```

> **You should see.** `False`: the parity machine is a DFA.

#### Step 1.2.2: Check the start and accept states

> **Do this.** Add the helper below `is_nfa`, write its body, and run the check.

```python
def check_start_and_accept(machine, states):
    """Return a list of error sentences about the start and accept states (empty if none)."""
    # Step 1: Start an empty list, errors.
    # Step 2: If the start state is not in states (the set of declared states),
    #         append an error that names it.
    # Step 3: For each accept state that is not in states, append an error
    #         that names it.
    # Step 4: Return errors.
    ...
```

| Step | How to think about it |
|---|---|
| start and accept (Steps 2 and 3) | Membership in the set of declared states is the whole test.  Inside an f-string, `!r` prints a value with quotes around it, so a stray space or a misspelling is easy to see. |

```bash
python3 -c "import json, simulator as s; m = json.load(open('machines/broken.json')); print(s.check_start_and_accept(m, set(m['states'])))"
```

> **You should see.** A list of two sentences, one per misspelling.  Your wording may differ:
>
> ```text
> ["start state 'evn' is not a declared state", "accept state 'od' is not a declared state"]
> ```

#### Step 1.2.3: Check a DFA's transitions

> **Do this.** Add the helper below, write its body, and run the check.

```python
def check_dfa_delta(machine, states, alphabet):
    """Return a list of error sentences about a DFA's delta (empty if none)."""
    # Step 1: Start an empty list, errors.
    # Step 2: For every declared state and every alphabet symbol, the pair must
    #         appear in delta, and its target must be a declared state.  A
    #         missing pair and an undeclared target are two different errors.
    # Step 3: Return errors.
    ...
```

| Step | How to think about it |
|---|---|
| DFA pairs (Step 2) | Loop over the declared states and the alphabet, not over the keys of `delta`.  A row that is missing from `delta` is exactly what you are looking for, and a loop over `delta` would never visit it.  `dict.get` with a default never crashes: a missing row can default to an empty dictionary, and a missing symbol then gives `None`.  `None` means the pair is missing, so name both the state and the symbol.  Otherwise, check that the target is declared. |

```bash
python3 -c "import json, simulator as s; m = json.load(open('machines/broken.json')); print(s.check_dfa_delta(m, set(m['states']), set(m['alphabet'])))"
```

> **You should see.**
>
> ```text
> ["missing transition for state 'odd' on symbol '1'"]
> ```
>
> Run the same command on `machines/even_ones.json` as well.  It prints `[]`, because the parity machine has every pair.

#### Step 1.2.4: Check an NFA's transitions

> **Do this.** Add the helper below and write its body.

```python
def check_nfa_delta(machine, states, alphabet):
    """Return a list of error sentences about an NFA's delta (empty if none)."""
    # Step 1: Start an empty list, errors.
    # Step 2: Check every "state,symbol" key.  Its state half must be declared.
    #         Its symbol half must be in the alphabet or be the word "eps".
    #         Every target in its list must be declared.
    # Step 3: Return errors.
    ...
```

| Step | How to think about it |
|---|---|
| NFA keys (Step 2) | Visit each key together with its list of targets; `.items()` gives you both.  Each key is one string, so split it at the comma into its state half and its symbol half.  `str.partition` or `str.split` both work.  The symbol test has two ways to pass: in the alphabet, or the word `eps`. |

You cannot test this helper until Part 2 gives you an NFA file.  Write it now anyway, because Part 2 relies on it.

#### Step 1.2.5: Integrate the checks into `load_machine`

> **Do this.** Add `load_machine` below the three helpers and write its body from its `# Step` comments.  Each check is now one call.

```python
def load_machine(path):
    """Read the JSON machine at path, check it, and return it as a dict.

    Raise one MachineError that lists every problem, one per line.
    """
    # Step 1: Open the file at path and parse it into a dictionary, machine.
    # Step 2: Build a set of the declared states and a set of the alphabet
    #         symbols, so each check is a quick membership test.
    # Step 3: Start the list errors with what check_start_and_accept returns.
    # Step 4: If is_nfa(machine) is true, add what check_nfa_delta returns.
    #         Otherwise the machine is a DFA: add what check_dfa_delta returns.
    # Step 5: If errors is not empty, raise one MachineError whose message is
    #         every error joined into one string, one per line.  Otherwise,
    #         return machine.
    ...
```

| Step | How to think about it |
|---|---|
| combine (Steps 3 and 4) | Each helper returns a list, and `+` or `list.extend` joins two lists.  Nothing raises until Step 5. |
| raise once (Step 5) | An empty list is false in an `if`.  `str.join` with a newline turns the list into one message with one problem per line. |

`simulator.py` has no command line yet, so you test it by importing it.  Test the loader on the good file first:

```bash
python3 -c "import simulator; simulator.load_machine('machines/even_ones.json')"
```

> **You should see.** Nothing.  Silence means the file passed.

Now check that the loader reports every problem at once, not just the first, on the broken machine you saved at the start of this step:

```bash
python3 -c "import simulator; simulator.load_machine('machines/broken.json')"
```

> **You should see.** A traceback that ends with one `MachineError` listing all three problems, one per line.  Your wording may differ, but every problem must appear:
>
> ```text
> simulator.MachineError: start state 'evn' is not a declared state
> accept state 'od' is not a declared state
> missing transition for state 'odd' on symbol '1'
> ```
>
> If only the first line appears, you raised the error inside a check instead of appending to `errors` and raising once at the end.

### Step 1.3: Write `run_dfa` and the Command Line

`dfa_core.py` crashes on an unknown symbol, and it has the machine path written into the program.  This step fixes both problems in `simulator.py` and adds trace mode.  The loop inside `run_dfa` is the same loop you wrote in Step 1.1; the new lines are the checks around it.

**You write:** `run_dfa` and `main` in `simulator.py`, below `load_machine`.
**You run:** a one-line check after each pass of `run_dfa`, then `python3 simulator.py machines/even_ones.json 0110 --trace`, plus the two other commands at the end of this step.

`run_dfa` does what `dfa_core.py` does, plus three things a real tool needs: it rejects an unknown symbol without crashing, it treats the empty string as valid input, and it can print a trace.  You build it in three passes, and you check each pass before starting the next.

#### Step 1.3.1: The core loop

A DFA has exactly one arrow for each state and symbol, so the machine is always in exactly one state.  That is why one variable can hold it, and why each symbol takes one lookup.  Add this skeleton below `load_machine`, and replace each `TODO` with one line of code:

```python
def run_dfa(machine, s, trace=False):
    """Run the DFA on the string s.  Return True to accept, False to reject."""
    # TODO: set state to the machine's start state.
    for symbol in s:
        # TODO: follow one arrow.  Look up the row for state, then the arrow for symbol.
    # TODO: return whether state is in the machine's accept list.
```

These are the same lines you wrote in `dfa_core.py`.  Here is the run on `01` with the parity machine, so you can compare it with what your code does:

```text
state = even                        the start state
read 0: delta["even"]["0"] is even, so state = even
read 1: delta["even"]["1"] is odd,  so state = odd
"odd" is not in the accept list, so return False
```

Plain `[...]` lookups are safe here, because the loader already proved that every state and symbol pair exists.  You need no special case for the empty string: the loop never runs, so the last line tests the start state.

```bash
python3 -c "import simulator as s; m = s.load_machine('machines/even_ones.json'); print(s.run_dfa(m, '0110'), s.run_dfa(m, '100'), s.run_dfa(m, ''))"
```

> **You should see.** `True False True`

#### Step 1.3.2: Reject an unknown symbol

The loader proved that every symbol in the alphabet has an arrow, but it knows nothing about the input string.  Try one with a symbol the machine does not have:

```bash
python3 -c "import simulator as s; m = s.load_machine('machines/even_ones.json'); print(s.run_dfa(m, '0120'))"
```

This crashes with `KeyError: '2'`, because the row for `even` has no key `"2"`.  The fix has to run before the lookup, so add it as the first thing inside the loop:

```python
    for symbol in s:
        # TODO: if symbol is not in the machine's alphabet, print the reason below and return False.
        #       reject: symbol '2' is not in the alphabet
```

`f"{symbol!r}"` prints the symbol with the quotes around it.  Run the same command again.

> **You should see.** The reason, then `False`, and no traceback:
>
> ```text
> reject: symbol '2' is not in the alphabet
> False
> ```

#### Step 1.3.3: Add the trace

The trace lets you watch the machine run, which is how you will debug the machines you design in Step 1.4.  It prints the start state once, and then the state after each move.  Add two prints, each under `if trace:` so that a normal run stays quiet:

```python
    # TODO: after setting the start state, if trace is on, print:   start: even
    # TODO: after the move in the loop, if trace is on, print:      read 1 -> odd
```

```bash
python3 -c "import simulator as s; m = s.load_machine('machines/even_ones.json'); print(s.run_dfa(m, '01', trace=True))"
```

> **You should see.**
>
> ```text
> start: even
> read 0 -> even
> read 1 -> odd
> False
> ```

#### Step 1.3.4: Integrate: add `main` and run the program

> **Do this.**
> 1. Add a `main` that takes the machine path and the input string from the command line and honors a `--trace` flag.  `main` and the `if __name__ == "__main__":` lines go last in the file, so every function they call is defined above them.
> 2. Type `main` exactly as shown; it is complete.

```python
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

`main` mentions `run_nfa`, which you do not write until Part 2.  The line still works for a DFA, because Python evaluates only the branch of `run_nfa if is_nfa(machine) else run_dfa` that it takes.  When you finish this step, `simulator.py` holds these pieces, from top to bottom:

```text
import json, import sys
class MachineError          (Step 1.2.1)
def is_nfa                  (Step 1.2.1)
def check_start_and_accept  (Step 1.2.2)
def check_dfa_delta         (Step 1.2.3)
def check_nfa_delta         (Step 1.2.4)
def load_machine            (Step 1.2.5)
def run_dfa                 (Steps 1.3.1 to 1.3.3)
def main                    (Step 1.3.4)
if __name__ == "__main__"   (Step 1.3.4, always last)
```

Test all three rules:

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
> For the empty string, `accept` alone, because the start state `even` accepts.  For the third command, a one-line reason such as `reject: symbol '2' is not in the alphabet`, then `reject`, and no traceback.

> **Checkpoint.** Test the parity machine on at least four strings it accepts and four it rejects.  Record each string and its result in `writeup.md` under a heading for the machine.

### Step 1.4: Design the Ends-in-ab DFA

To design a DFA, decide what each state must remember.  For this language the question is short: how much of the suffix `ab` has the machine just seen?  The parity machine shows the method.  Each of its two states stands for one fact about the input so far ("even number of 1s" or "odd"), and each arrow says how one more symbol changes that fact.  Do the same here, with one state for each answer to "how much of `ab` have I just seen?"  Every state needs an arrow on both `a` and `b`.  [The class notes build the mirror image, ends in `ba`, with the subset construction](https://liascript.github.io/course/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374-Fall2026/gh-pages/_pages/Activities/liascript-automata-day2.md#16), if you want to check your approach after you design yours.

> **Do this.**
> 1. Design a DFA for **Ends in ab**: strings over `{a, b}` that end with the suffix `ab`.
> 2. Draw it on paper first, then encode it as `machines/ends_in_ab.json` in the same format as the parity machine.
> 3. In `writeup.md`, annotate each state with one sentence about what it remembers about the input so far.
> 4. Test at least four strings it accepts and four it rejects, and record them next to the state annotations.

**You write:** `machines/ends_in_ab.json`, plus a heading for this machine in `writeup.md` with your state annotations and test strings.  No Python changes; `simulator.py` already runs any DFA.
**You run:** the three commands below, then your own eight test strings.

Worked example: `"aab"` -> accept; `"ba"` -> reject; `"ab"` -> accept; `""` -> reject.  Hint: you need at least three states.  You can start from this skeleton.  The state names are a suggestion, one for each answer to "how much of `ab` have I just seen?", and you may rename them.  Replace each `"TODO"` with a state name, and decide which state or states go in `accept`:

```json
{
  "states": ["none", "a", "ab"],
  "alphabet": ["a", "b"],
  "start": "none",
  "accept": ["TODO"],
  "delta": {
    "none": {"a": "TODO", "b": "TODO"},
    "a":    {"a": "TODO", "b": "TODO"},
    "ab":   {"a": "TODO", "b": "TODO"}
  }
}
```

Your loader catches any `"TODO"` you forget to replace, because `"TODO"` is not a declared state.

```bash
python3 simulator.py machines/ends_in_ab.json aab
python3 simulator.py machines/ends_in_ab.json ba
python3 simulator.py machines/ends_in_ab.json ""
```

> **You should see.** `accept`, `reject`, `reject`.  If the empty string accepts, you marked the start state as accepting.  The empty string does not end in `ab`.

> **If it fails.**
> - `MachineError` naming a missing (state, symbol) pair: a DFA needs an arrow out of every state on both `a` and `b`, including the "just saw `ab`" state.
> - `"abb"` accepts: after `ab`, reading `b` must forget the suffix entirely, not step back one state.
> - `"aab"` rejects: after `a`, another `a` must stay in the "just saw `a`" state, because the newer `a` could still start the suffix.

---

## Part 2: NFA Simulation and Design

### Step 2.1: Read the NFA Machine Format

For an NFA, `delta` maps `"state,symbol"` string keys to lists of states.  The special symbol `"eps"` marks an ε-transition, a move the machine may take without reading input.  A state may have any number of targets for a symbol, including none.  The other keys work as they do for a DFA.  Do not list `eps` in `alphabet`: it labels a transition, and it is not an input symbol.

> **Watch it run.**  The [FSM Simulator](https://ivanzuzak.info/noam/webapps/fsm_simulator/) steps a DFA, NFA, or ε-NFA one input symbol at a time and highlights the active set, the same set your `run_nfa` computes.  Its format differs from ours in two ways.  It writes ε as `$` where our JSON writes `eps`, and it lists transitions as `q0:a>q0,q1` instead of JSON keys.

Here is part of an NFA as a diagram and then as JSON.  The fragment does not say which states accept, so no state has a double circle.

![Fragment of an NFA with states q0, q1, and q2; accepting states are not shown. q0 loops to itself on a, q0 goes to q1 on a, q1 goes to q2 on b, and q0 goes to q2 on an epsilon move, drawn dashed.]({{ site.baseurl }}/files/dotty/lab_nfa_fragment.svg)

```json
"delta": {
  "q0,a": ["q0", "q1"],
  "q0,eps": ["q2"],
  "q1,b": ["q2"]
}
```

The `a` arrows out of `q0` go two ways, so `"q0,a"` lists two targets.  That is the nondeterminism.  Pairs with no arrow, such as `q1` on `a` or `q2` on anything, have no key.  Read transitions with `machine["delta"].get(key, [])`, so a missing key means "no moves" and does not raise a `KeyError`.

Before you write any NFA code, encode an NFA whose behavior you already know, so you have something to test against.  This one accepts strings over `{a, b}` that end in `ab`, and [the class notes trace `aab` through it](https://liascript.github.io/course/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374-Fall2026/gh-pages/_pages/Activities/liascript-automata-day2.md#12).  Step 2.2 checks your `run_nfa` against that trace.

![NFA for strings that end in ab. States q0, q1, and q2; q0 is the start state and q2 is the only accepting state. q0 loops to itself on a or b, q0 goes to q1 on a, and q1 goes to q2 on b.]({{ site.baseurl }}/files/dotty/example_nfa_ends_in_ab.svg)

| state | on `a` | on `b` |
|---|---|---|
| q0 | {q0, q1} | {q0} |
| q1 | ∅ | {q2} |
| q2 | ∅ | ∅ |

**You write:** `machines/ends_in_ab_nfa.json`.  It is a test file, and you do not need to submit it.
**You run:** `python3 -c "import simulator; simulator.load_machine('machines/ends_in_ab_nfa.json')"`

> **Do this.**
> 1. Start from the JSON below.  The first key, `"q0,a"`, is done for you; it is the `{q0, q1}` cell in row `q0`, column `a`, of the table above.
> 2. Add one key for each other non-empty cell of that table.  A cell that shows ∅ gets no key.
> 3. Run the loader command.  Silence means the file passed, and it also means the NFA branch of your loader accepts a correct file.

```json
{
  "states": ["q0", "q1", "q2"],
  "alphabet": ["a", "b"],
  "start": "q0",
  "accept": ["q2"],
  "delta": {
    "q0,a": ["q0", "q1"]
  }
}
```

> **If it fails.**  A `MachineError` about a symbol such as `'a"'` or `' b'` usually means a stray quote or space inside a key.  Each key is exactly a state, a comma, and a symbol, with no spaces.  When you finish, the file has three keys.

#### Before You Code: Keys and Sets

In the NFA format, `"q0,a": ["q0", "q1"]` reads as "from state `q0`, reading `a`, the machine can go to `q0` or to `q1`."  The key holds the state and the symbol in one string, and the value lists every arrow with that label.  A pair with no arrow has no key, so read with `delta.get(key, [])`.  The class notes [read a whole NFA this way](https://liascript.github.io/course/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374-Fall2026/gh-pages/_pages/Activities/liascript-automata-day2.md#10).

The machine is in a set of states, so you use a Python `set`: `moved = set()` starts one, `moved.update(targets)` adds every item of a list, `"q2" in active` tests membership, and `sorted(active)` prints it in a fixed order.  A `frozenset` is a set that cannot change, which is what `eps_closure` returns.  The class notes [show each of these with examples](https://liascript.github.io/course/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374-Fall2026/gh-pages/_pages/Activities/liascript-automata-day2.md#11).

### Step 2.2: Write `run_nfa` Without ε-Moves

Get the set of states working first, on a machine with no ε-moves.  The "ends in `ab`" NFA is that machine, and [the class notes already trace `aab` through it](https://liascript.github.io/course/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374-Fall2026/gh-pages/_pages/Activities/liascript-automata-day2.md#12).  Step 2.3 then adds ε-moves by changing two lines.

**You write:** `nfa_move` and a first version of `run_nfa` in `simulator.py`, below `run_dfa` and above `main`.
**You run:** the commands after each sub-step.

#### Step 2.2.1: One move, and why it is a union

Each state in the active set is a guess that might be right, and the machine does not know which one.  So on the next symbol, every active state moves, and the next active set keeps everything any of them can reach.  Collecting those results is [the union in the class notes' rule](https://liascript.github.io/course/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374-Fall2026/gh-pages/_pages/Activities/liascript-automata-day2.md#12).  Here is the active set `{q0, q1}` reading `b`:

```text
active state     lookup                 targets
    q0     --->  "q0,b": ["q0"]   --->    q0  \
                                                union: {q0, q2}
    q1     --->  "q1,b": ["q2"]   --->    q2  /
```

Neither result can be dropped.  Keep only `q0`'s result on `aab`, and the machine never reaches `q2`, so it wrongly rejects.  Keep only `q1`'s result on `aabab`, and the machine is left in `q2`, which has no arrows, so it wrongly rejects that too.  The union keeps every guess alive.

In pseudocode:

```text
move(active, symbol):
    moved = empty set
    for each state q in active:
        moved = moved ∪ delta(q, symbol)      # no arrow adds nothing
    return moved
```

Add this skeleton to `simulator.py`, and replace each `TODO` with one line:

```python
def nfa_move(machine, active, symbol):
    """Return every state reachable from active on one symbol."""
    moved = set()
    for state in active:
        # TODO: build this state's key, as in "q0,b".
        # TODO: look up its targets in machine["delta"], with [] if the key is missing.
        # TODO: add every target to moved.
    return moved
```

```bash
python3 -c "import simulator as s; m = s.load_machine('machines/ends_in_ab_nfa.json'); print(sorted(s.nfa_move(m, {'q0', 'q1'}, 'b')), sorted(s.nfa_move(m, {'q0'}, 'a')), s.nfa_move(m, {'q2'}, 'a'))"
```

> **You should see.** `['q0', 'q2'] ['q0', 'q1'] set()`.  The first list is the diagram above.  The last value is the empty set, because `q2` has no `a` arrow.

> **If it fails.**  If the first list holds only one state, your code kept one active state's targets and lost the other's.  Check that `moved = set()` stays above the loop, and that the loop adds to `moved` and never assigns a new value to it.

#### Step 2.2.2: One move per symbol

`run_nfa` has the same shape as `run_dfa`, with a set of states where `run_dfa` had one state:

```text
run(s):
    active = { start }
    for each symbol in s:
        active = move(active, symbol)
    accept if any state in active is an accepting state
```

The last line is the NFA's rule for accepting: the string is in the language if at least one guess worked.  In Python, `any(state in active for state in machine["accept"])` asks that question.  Add this skeleton below `nfa_move`:

```python
def run_nfa(machine, s, trace=False):
    """Run the NFA on the string s.  Return True to accept, False to reject."""
    # TODO: set active to a set holding only the start state.
    if trace:
        print(f"start: {sorted(active)}")
    for symbol in s:
        # TODO: replace active with the result of one move on this symbol.
        if trace:
            print(f"read {symbol} -> {sorted(active)}")
    # TODO: return whether any accepting state is in active.
```

You need no special cases.  If the active set becomes empty, it stays empty, and the string is rejected.  A symbol outside the alphabet has no key, so it empties the set too.  `main` already calls `run_nfa` when `is_nfa` returns true, so run the whole program:

```bash
python3 simulator.py machines/ends_in_ab_nfa.json aab --trace
python3 simulator.py machines/ends_in_ab_nfa.json aba
python3 simulator.py machines/ends_in_ab_nfa.json ""
```

> **You should see.** The same active sets as the class notes' trace of `aab`, and then two rejects:
>
> ```text
> start: ['q0']
> read a -> ['q0', 'q1']
> read a -> ['q0', 'q1']
> read b -> ['q0', 'q2']
> accept
> reject
> reject
> ```

### Step 2.3: Add ε-Moves

An ε-move reads no input, so your `run_nfa` never takes one.  Here is a machine that shows the problem.  It is [`ab?` from the class notes](https://liascript.github.io/course/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374-Fall2026/gh-pages/_pages/Activities/liascript-automata-day2.md#12): an `a`, optionally followed by a `b`.

```text
q0 --a--> q1 --b--> q2 (accepts)
           \        ^
            `---ε---'
```

**You write:** two test files, `machines/ab_optional.json` and `machines/eps_cycle.json`; `eps_closure` in `simulator.py`, below `run_nfa` and above `main`; and two changed lines in `run_nfa`.
**You run:** the commands after each sub-step.

Save this as `machines/ab_optional.json`, a test file you do not submit:

```json
{
  "states": ["q0", "q1", "q2"],
  "alphabet": ["a", "b"],
  "start": "q0",
  "accept": ["q2"],
  "delta": {"q0,a": ["q1"], "q1,b": ["q2"], "q1,eps": ["q2"]}
}
```

```bash
python3 simulator.py machines/ab_optional.json a --trace
```

> **You should see this wrong answer.**  The machine should accept `a`, but the active set stops at `q1`.  From `q1` it can reach `q2` for free, so the active set should be `{q1, q2}`.
>
> ```text
> start: ['q0']
> read a -> ['q1']
> reject
> ```

> **If it fails.**  A `MachineError` that mentions `eps` means your loader rejects `eps` as an unknown symbol.  Allow it for NFAs in `check_nfa_delta` (Step 1.2.4).

#### Step 2.3.1: Follow the free moves (`eps_closure`)

An ε-arrow is stored like any other arrow, with `eps` as the symbol, so `"q1,eps"` reads as "from `q1`, for free, the machine can go to these states."  You look it up the same way you look up `"q0,a"`.  `eps` stays out of `alphabet`, because no input string contains it.

One lookup is not enough, because free moves chain:

```text
q0 --ε--> q1 --ε--> q2
```

If the machine can be in `q0`, it can also be in `q1`, and so also in `q2`.  The lookup on `q0` finds only `q1`, so you have to look up each new state too.  Arrows can also lead back to an earlier state, so you have to remember what you already found, or a cycle runs forever.  The ε-closure of a set of states is that set plus everything reachable from it by ε-arrows alone.  In pseudocode, with a to-do list called the *frontier*:

```text
closure(states):
    closure = states                     # zero moves count
    frontier = states                    # states whose ε-arrows we have not followed
    while frontier is not empty:
        q = take one state off frontier
        for each target r of an ε-arrow out of q:
            if r is not in closure:      # this check is what stops a cycle
                add r to closure
                add r to frontier
    return closure
```

Add this skeleton below `run_nfa`:

```python
def eps_closure(machine, states):
    """Return every state reachable from states by ε-moves alone, as a frozenset."""
    closure = set(states)
    frontier = list(states)
    while frontier:
        state = frontier.pop()
        # TODO: look up this state's ε-targets, with [] if the key is missing.
        # TODO: for each target not in closure, add it to closure and append it to frontier.
    return frozenset(closure)
```

Now test the hard case, a cycle.  Save this as `machines/eps_cycle.json`, another test file you do not submit:

```json
{
  "states": ["q0", "q1", "q2"],
  "alphabet": ["a"],
  "start": "q0",
  "accept": ["q2"],
  "delta": {"q0,eps": ["q1"], "q1,eps": ["q2"], "q2,eps": ["q0"]}
}
```

Here is the closure of `{q0}` on this machine, one pass of the `while` loop per line:

```text
closure = {q0},          frontier = [q0]
take q0: targets [q1], q1 is new.      closure = {q0, q1},      frontier = [q1]
take q1: targets [q2], q2 is new.      closure = {q0, q1, q2},  frontier = [q2]
take q2: targets [q0], q0 is not new.  closure = {q0, q1, q2},  frontier = []
```

```bash
python3 -c "import simulator as s; m = s.load_machine('machines/eps_cycle.json'); print(sorted(s.eps_closure(m, {'q0'})))"
python3 -c "import simulator as s; m = s.load_machine('machines/ab_optional.json'); print(sorted(s.eps_closure(m, {'q1'})), sorted(s.eps_closure(m, {'q0'})))"
```

> **You should see.**
>
> ```text
> ['q0', 'q1', 'q2']
> ['q1', 'q2'] ['q0']
> ```
>
> The second line shows that closure only follows arrows forward, and that a state with no ε-arrows closes to itself.

> **If it fails.**
> - The command never finishes: the `if` check is missing, so the cycle runs forever.  Press Ctrl+C to stop it.
> - Only `['q0']`: new states are not going onto the frontier, so you followed one arrow and stopped.

#### Step 2.3.2: Close after each move, and at the start

The machine can take free moves at any time, so the active set must always include them.  That gives two places to close, [the *move, then ε-close* rule](https://liascript.github.io/course/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374-Fall2026/gh-pages/_pages/Activities/liascript-automata-day2.md#12).  Make one change at a time, and watch what each one fixes.

*Close after each move.*  In the loop of `run_nfa`, change the move line so that `active` becomes the `eps_closure` of what `nfa_move` returns.

```bash
python3 simulator.py machines/ab_optional.json a --trace
python3 simulator.py machines/ab_optional.json ab --trace
python3 simulator.py machines/ab_optional.json abb
```

> **You should see.** Both traces accept, and `abb` is rejected:
>
> ```text
> start: ['q0']
> read a -> ['q1', 'q2']
> accept
> start: ['q0']
> read a -> ['q1', 'q2']
> read b -> ['q2']
> accept
> reject
> ```

*Close at the start.*  The machine can also take free moves before it reads anything.  The cycle machine's start state reaches its accepting state by ε-moves alone, so it should accept the empty string:

```bash
python3 simulator.py machines/eps_cycle.json ""
```

> **You should see this wrong answer.** `reject`.  The loop never runs on the empty string, so nothing has closed the start state yet.

Change the first line of `run_nfa` so that `active` starts as the `eps_closure` of the set holding the start state.  Then run the cycle machine again, and rerun the first machine to confirm nothing broke:

```bash
python3 simulator.py machines/eps_cycle.json ""
python3 simulator.py machines/eps_cycle.json a
python3 simulator.py machines/ends_in_ab_nfa.json aab --trace
```

> **You should see.** `accept`, then `reject`, and then the same `aab` trace as Step 2.2.2.  The string `a` rejects because no state has an `a` arrow, so the active set becomes empty.  The `aab` trace does not change, because that machine has no ε-arrows and each closure leaves its set as it was.

### Step 2.4: Design the Contains-aa NFA

An NFA can guess.  Here the guess is "the `aa` starts here," and the machine keeps every guess alive at once.

> **Do this.**
> 1. Design an NFA for **Contains aa**: strings over `{a, b}` that contain the substring `aa` somewhere.
> 2. Encode it as `machines/contains_aa.json`.
> 3. Test at least four strings it accepts and four it rejects, and record them in `writeup.md`.
> 4. Include the `--trace` output for at least one accepted string, so the writeup shows the execution path.

Worked example: `"baaab"` -> accept; `"ababab"` -> reject.  Hint: let the machine guess where `aa` occurs.  The "ends in `ab`" NFA in Step 2.1 shows the pattern.  Its start state loops on every symbol while the machine has not yet guessed, and a chain of states spells out the pattern.  Here `aa` may appear anywhere, not only at the end, so your accepting state must also loop on every symbol once the pattern has appeared.  Your design must use nondeterminism; a DFA in disguise does not count.

**You write:** `machines/contains_aa.json`, plus a heading for this machine in `writeup.md` with your test strings and one `--trace` output.  No Python changes; `simulator.py` already runs any NFA.
**You run:** the two commands below, then your own eight test strings.

You can start from this skeleton.  Three states are enough: `q0` has not yet guessed, `q1` has just read the first `a` of the guessed `aa`, and `q2` has seen `aa`.  Draw the arrows on paper first.  Then replace the placeholder key with one `"state,symbol"` key for each state and symbol that has at least one arrow, and list its targets.  A pair with no arrow gets no key.  Your loader reports the placeholder if you forget to replace it, because `"TODO"` is not a declared state:

```json
{
  "states": ["q0", "q1", "q2"],
  "alphabet": ["a", "b"],
  "start": "q0",
  "accept": ["q2"],
  "delta": {
    "TODO,a": ["TODO"]
  }
}
```

> **Watch out.** At least one `"state,symbol"` key in your JSON should list two or more targets.  If every list has one entry and there is no `eps` key, you have written a DFA in NFA format.

```bash
python3 simulator.py machines/contains_aa.json baaab --trace
python3 simulator.py machines/contains_aa.json ababab
```

> **You should see.** A trace whose active set grows when the machine guesses that an `a` starts the `aa`, ending in `accept`; and `reject` for `ababab`.  Your state names will differ, but the shape looks like this:
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

## Part 3: Thompson's Construction by Hand

Part 3 is paper work for your writeup, with no code.  Thompson's construction turns a regular expression into an NFA by following fixed rules, and it joins the pieces with ε-arrows.  First see the rules build a few small fragments.  Then you build one machine yourself.

Below, `1 -x-> 2` means an arrow from state 1 to state 2 on `x`, and `2 -ε-> 3` means a free move.  Number the states in the order you create them, and keep the numbers when you reuse a fragment.

*A single symbol.*  Two new states and one arrow.  The fragment for `x` is:

![Thompson rule for a single symbol x: a start state s with one arrow labeled x to an accepting state f.]({{ site.baseurl }}/files/dotty/thompson_rule_symbol.svg)

```text
x:     1 -x-> 2                 start 1, accept 2
y:     3 -y-> 4                 start 3, accept 4
```

*Union.*  A new start with ε-arrows into both fragments, and a new accept with ε-arrows out of both.  The fragment for `x|y` reuses the two above:

![Thompson rule for union: a new start state s with dashed epsilon arrows into fragment A and fragment B, and dashed epsilon arrows from both fragments into a new accepting state f.]({{ site.baseurl }}/files/dotty/thompson_rule_union.svg)

```text
x|y:   5 -ε-> 1    5 -ε-> 3     new start 5
       2 -ε-> 6    4 -ε-> 6     new accept 6
```

*Concatenation.*  One ε-arrow from the first fragment's accept to the second fragment's start, and no new states beyond the fragments themselves.  To build `(x|y)z`, make the fragment for `z`, and join it to the union:

![Thompson rule for concatenation: fragment A, drawn as a box, joined to fragment B by one dashed epsilon arrow from A's accept to B's start.]({{ site.baseurl }}/files/dotty/thompson_rule_concat.svg)

```text
z:     7 -z-> 8                 start 7, accept 8
(x|y)z: 6 -ε-> 7                start 5, accept 8
```

States 2, 4, and 6 accepted in their own fragments, but they do not accept now.  Only the outermost accept does.  Here is the finished machine:

![The finished Thompson NFA for (x|y)z. Start state 5 has dashed epsilon arrows to 1 and 3; 1 goes to 2 on x and 3 goes to 4 on y; 2 and 4 have dashed epsilon arrows to 6; 6 has a dashed epsilon arrow to 7; 7 goes to the accepting state 8 on z.]({{ site.baseurl }}/files/dotty/thompson_xy_z.svg)

*Star.*  A new start, a new accept, and four ε-arrows: into the fragment, out of it, back around it, and straight past it for zero repetitions.  To build `(ab)*`, first make `ab` by concatenation, and then wrap it:

![Thompson rule for star: a new start state s and a new accepting state f around fragment A. Dashed epsilon arrows go from s into A (enter), from A to f (stop), from A back to its own start (repeat), and from s straight to f (zero times).]({{ site.baseurl }}/files/dotty/thompson_rule_star.svg)

```text
a:     1 -a-> 2                 start 1, accept 2
b:     3 -b-> 4                 start 3, accept 4
ab:    2 -ε-> 3                 start 1, accept 4
(ab)*: 5 -ε-> 1                 enter
       4 -ε-> 6                 stop
       4 -ε-> 1                 go around again
       5 -ε-> 6                 zero times            start 5, accept 6
```

![The finished Thompson NFA for (ab)*. Start state 5 has dashed epsilon arrows to 1 (enter) and to the accepting state 6 (zero times); 1 goes to 2 on a, 2 has a dashed epsilon arrow to 3, 3 goes to 4 on b, and 4 has dashed epsilon arrows to 6 (stop) and back to 1 (repeat).]({{ site.baseurl }}/files/dotty/thompson_ab_star.svg)

### Step 3.1: Build `a(b|c)*`

**You write (in `writeup.md` under a `## Part 3: Thompson's Construction` heading):** the finished NFA for `a(b|c)*`, either as a drawing or as a list of arrows in the form above.  No code.

> **Do this.**
> 1. Apply Thompson's construction to the regular expression `a(b|c)*`.  Work from the inside out: the single symbols, then the union, then the star, then the concatenation.
> 2. Number every state, mark every ε-arrow, and say which state is the start and which state accepts.

---

## Deliverables

Submit a ZIP that contains the files below.  List your Python version in the writeup so I can reproduce your results.

| File or artifact | What it shows | Rubric row |
|------------------|---------------|------------|
| `dfa_core.py` | the ten-line DFA runner from Step 1.1, unchanged after that step | Part 1 |
| `simulator.py` | `load_machine`, `run_dfa`, `nfa_move`, `run_nfa`, `eps_closure`, and the command-line entry point | Parts 1 and 2 |
| `machines/even_ones.json` | the provided parity machine, unchanged | Part 1 |
| `machines/ends_in_ab.json` | your designed DFA | Part 1 |
| `machines/contains_aa.json` | your designed NFA | Part 2 |
| `writeup.md` | Part 0 paper work; state annotations and test strings for both designed machines; your Thompson NFA for `a(b|c)*`; your name (and your partner's, if you worked in a pair) | Parts 0, 1, 2, 3 |

---

## Self-Check Before You Submit

- [ ] `python3 dfa_core.py 0110` prints `accept`, and `python3 dfa_core.py 100` prints `reject`.
- [ ] `python3 simulator.py machines/even_ones.json 0110` prints `accept`, and the same command with `100` prints `reject`.
- [ ] The empty string and an out-of-alphabet symbol each produce a deliberate answer, not a traceback.
- [ ] `--trace` prints a state (DFA) or a sorted set of states (NFA) after every symbol.
- [ ] `load_machine` on `machines/broken.json` raises one `MachineError` that lists all three problems.
- [ ] `eps_closure` stops on `machines/eps_cycle.json` and returns all three states.
- [ ] `python3 simulator.py machines/ends_in_ab_nfa.json aab --trace` prints the same active sets as the hand trace in the class notes.
- [ ] Each state of the Ends-in-ab DFA has a one-sentence annotation, and both designed machines have at least four accepted and four rejected test strings recorded.
- [ ] The Contains-aa NFA has at least one state with two or more targets on the same symbol.
- [ ] `writeup.md` has the Part 0 work, the Thompson NFA for `a(b|c)*`, both names, and your Python version.

---

## Reflection Prompts

- In Part 0 you converted an NFA to a DFA, and in Part 3 you built an NFA from a regular expression by following rules.  Compare the two tasks: which took more judgment, and why?
- Your simulators treat machines as data loaded from JSON.  Name one way this helped your testing that hard-coded machines would not have.
- If you worked in a pair, who did what?  Name one thing your partner caught that you would have missed.  If you worked alone, say so.
