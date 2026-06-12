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
    - To connect automata to the regular expressions and lexer of the surrounding course
  rubric:
    - weight: 60
      description: Algorithm and Implementation
      preemerging: The simulators fail to run or fail most provided machines due to major issues
      beginning: The simulators run but fail on several provided test cases due to one or more minor issues
      progressing: The simulators pass the provided test cases but would fail in a general case due to a minor issue such as mishandling the empty string or symbols outside the alphabet
      proficient: Correct DFA and NFA simulators pass the provided and hidden test cases, handle the empty string and out-of-alphabet symbols deliberately, and would be reasonably expected to handle the general case
    - weight: 30
      description: Design Portfolio and Analysis
      preemerging: Few or no machines are designed, or designs are incorrect
      beginning: Machines are designed but several are incorrect or untested
      progressing: All required machines are designed, encoded, and tested, with limited explanation of state meanings
      proficient: All required machines are designed with each state's meaning documented, encoded, and tested, and the subset construction is carried out by hand with the result verified by simulation against the original NFA
    - weight: 10
      description: Writeup and Submission
      preemerging: An incomplete submission is provided
      beginning: The program is submitted, but not according to the directions in one or more ways
      progressing: The program is submitted according to the directions with a minor omission, with at least superficial responses to the reflection prompts
      proficient: The program is submitted according to the directions, including a readme writeup and thoughtful answers to the reflection prompts
  readings:
    - rtitle: "Finite Automata Activity"
      rlink: "https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374/gh-pages/_pages/Activities/liascript-automata.md"
    - rtitle: "Grammars and the Chomsky Hierarchy Activity"
      rlink: "https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374/gh-pages/_pages/Activities/liascript-grammars.md"

tags:
  - automata
  - theory
  - languages

---

In this assignment you will build the machines beneath your lexer: general simulators for DFAs and NFAs that read machine definitions as data, plus a design portfolio of machines you create. Build in the small scaffolded steps below; each step has its own tests.

## Part 1: Machine Format and Loader

Machines are JSON files following the class dictionary format: `states`, `alphabet`, `start`, `accept`, and `delta` (for the DFA, `delta[state][symbol] = state`; for the NFA, `delta` maps `"state,symbol"` keys to lists of states, and the symbol `"eps"` denotes an epsilon transition).

1a. Write `load_machine(path)` that reads a JSON machine and validates it: the start state exists, accept states exist, and every transition references declared states and alphabet symbols. Report all validation errors with specifics, using the class exception pattern.

## Part 2: The DFA Simulator (scaffolded)

2a. Implement `run_dfa(machine, s)` returning `True`/`False`, treating any symbol outside the alphabet as an immediate reject with a reported reason.

2b. Add a `--trace` mode that prints the state after each symbol (this trace is your debugging instrument for Part 4).

2c. Test against the provided machines (even-ones parity; binary divisible by 3) on the provided string sets, including the empty string.

## Part 3: The NFA Simulator (scaffolded)

3a. Implement `eps_closure(machine, states)` returning the set reachable through epsilon transitions alone (a small graph search; document your approach).

3b. Implement `run_nfa(machine, s)` by tracking the set of possible states: take the epsilon closure of the start set, then for each symbol, move every current state and close again; accept when the final set intersects the accept set.

3c. Test against the provided machines (ends-in-ab; contains aa; an epsilon-transition machine for `a(b|c)*` built by Thompson's construction).

## Part 4: Design Portfolio

Design, encode as JSON, document (one sentence per state: what it remembers), and test each of the following, with at least four accepted and four rejected strings per machine:

1. A DFA over `{0,1}` for strings with an odd number of 0s **and** an even number of 1s (hint: four states, a product of two parities).
2. A DFA over `{a,b}` for strings not containing `bb`.
3. An NFA for strings over `{a,b}` whose third-from-last symbol is `a` (lean into nondeterminism: guess where the ending starts).
4. The subset construction, by hand, of machine 3: show the construction table in your writeup, encode the resulting DFA as JSON, and verify by simulation that the DFA and NFA agree on all your test strings. Report how many states the DFA needed versus the NFA.

## Deliverables

Submit a ZIP containing your code, all machine JSON files, your test runs, the subset-construction table, and a readme writeup of approximately one page connecting these simulators to the lexer you will build next (which component of the lexer plays the role of your simulators?). Ensure reproducibility by listing software version information.

## Reflection Prompts

- For machine 3, contrast designing the NFA with designing its DFA: where did the work move?
- Your simulators treat machines as data. Name one benefit this brought during testing that hard-coded machines would have denied you.
- If collaboration with a buddy was permitted, did you work with a buddy on this assignment? If so, who? If not, do you certify that this submission represents your own original work? Please identify any and all portions of your submission that were not originally written by you.
- Approximately how many hours it took you to finish this assignment (I will not judge you for this at all...I am simply using it to gauge if the assignments are too easy or hard)?
