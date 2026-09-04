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

A finite automaton is a machine with a fixed set of states, arrows between those states that fire on input symbols, and a yes or no verdict when the input ends.  A subway turnstile is one.  It has two states, **locked** and **unlocked**, and two transitions: a coin moves it from locked to unlocked, and a push moves it from unlocked back to locked.  The turnstile never gives a verdict, so the analogy stops there.  Today you will see that this small model recognizes exactly the patterns you wrote in the *Regular Expressions* activity, no more and no less.

## Learning Goals

By the end of this activity, you will be able to:

- Define a DFA (deterministic finite automaton) as a five-tuple and trace it on an input string, naming the state after each symbol and deciding acceptance or rejection
- Build a DFA for a given regular language by finding the finite information the machine must track and assigning one state per distinct memory value
- Encode a DFA as a transition table, simulate it, and connect that simulation to the way a regex-based lexer runs
- Predict how many states a pattern needs before you draw it, by asking what the machine must remember
- Show concretely where finite memory fails, and name the language class that failure puts you in

A regular expression *describes* a set of strings.  A finite automaton *recognizes* one: you hand it a string and it answers yes or no.  The machine is only states and arrows, and it is exactly as powerful as regex notation.  Over two days we build the machine view in this order: **DFAs $\rightarrow$ designing them $\rightarrow$ NFAs (nondeterministic finite automata) $\rightarrow$ their equivalence**.  This is the theory under your next assignment and the engine inside every lexer, including yours.

> **Before You Begin**, make sure you can:
> - Describe what a regular expression *denotes* (the set of strings it matches), rather than only writing one
> - Create and look up values in a Python `dict`, including a dict whose values are themselves dicts
> - Trace a simple `for` loop by hand, tracking the value of one variable through each iteration

---

## Directions and Group Roles

Work in your POGIL team with your rotated roles (**Manager**, **Recorder**, **Presenter**, **Reflector**).  Trace each model on paper before you run it.  Every model in this deck lets you predict its output, and the places where your prediction and the machine disagree are the ones worth discussing.  The Recorder posts your answers to the Class Activity Questions discussion board.  The Presenter reports out wherever your team disagreed or found another approach.

---

# Part I: Deterministic Finite Automata

## 1.  Theory: The Machine

A DFA is a five-tuple $M = (Q, \Sigma, \delta, q_0, F)$.  Each part has a plain meaning:

- $Q$ is a finite set of states.  A state is the machine's whole memory at one moment.
- $\Sigma$ is the input alphabet: the set of symbols the machine can read.
- $\delta: Q \times \Sigma \rightarrow Q$ is the transition function.  Given the current state and one input symbol, it names the next state.  There is exactly one next state, and that is what "deterministic" means.
- $q_0$ is the start state.
- $F \subseteq Q$ is the set of accepting states.

The machine reads the input one symbol at a time and follows $\delta$ at each step.  It **accepts** the string exactly when the last symbol leaves it in an accepting state.

The machine's entire memory is which state it is in.  Finitely many states means finite memory, and finite memory is why the DFA sits on the bottom rung of the Chomsky hierarchy.  Hold on to that sentence; Part II is built on it.

Here is a DFA that accepts binary strings with an even number of 1s:

```
            0                0
          +---+            +---+
          v   |            v   |
   --> ((even)) --1-->  (odd)
          ^                 |
          `-------1---------+
```

Two states are enough because the machine only needs to remember one bit: the parity of the 1s so far.

Remember two things from this section.  A DFA is states, an alphabet, a transition function, a start state, and accepting states.  Its only memory is the state it is in right now.

## Examples: Tracing `1011` by Hand

Trace this yourself before you read the table.  Writing it out matters because you can do this on paper in an exam or a design meeting, before any code exists.

| Step | State before | Symbol read | Transition used | State after |
|------|--------------|-------------|-----------------|-------------|
| 0 | - | *(start)* | - | `even` |
| 1 | `even` | `1` | `even --1--> odd` | `odd` |
| 2 | `odd` | `0` | `odd --0--> odd` | `odd` |
| 3 | `odd` | `1` | `odd --1--> even` | `even` |
| 4 | `even` | `1` | `even --1--> odd` | `odd` |

The final state is `odd`, which is not accepting, so the machine rejects `1011`.  The string has three `1`s, and this machine accepts only an even count.

Two habits come from this small table.  First, the `0` transitions are self-loops.  Reading a `0` never changes the answer, so the machine is saying that zeros do not matter to parity.  A self-loop is always a claim about what the machine chooses to ignore.  Second, the state after step 4 is the entire memory of the run.  The machine has forgotten that it read `1011`; it remembers only "odd so far."  That is the limitation you will meet in CTQ 4 (Critical Thinking Question 4).

## Model 1: Trace and Design

Now design two machines of your own.  Draw them; do not write code yet.

### Critical Thinking Questions

1.  Trace `1011` through the parity DFA and list the state after each symbol.  Is the string accepted or rejected?  The Recorder writes the trace.
2.  Draw a DFA over $\{a, b\}$ that accepts strings that end in `ab`.  How many states did your team need, and what does each state remember?
3.  Draw a DFA that accepts strings containing the substring `aa`.  Compare it with question 2: "ends in" versus "contains" changes which states are accepting.  Explain how.
4.  Try to draw a DFA for $a^n b^n$.  Where does finite memory fail you, and which earlier module predicted this?

## Model 2: DFA Simulation, a Dictionary and a Loop

The five-tuple maps almost directly onto Python data.  States become string keys.  The transition function becomes a `dict` of `dict`s.  The simulation is one loop that does one dictionary lookup per character.

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

print("=== Even-ones DFA ===")
for s in ["", "1", "11", "1011", "0000", "10101", "abc"]:
    print(f"  {s!r:9} -> {run_dfa(EVEN_ONES, s)}")

print("\n=== Trace of '1011' (compare against your table) ===")
run_dfa(EVEN_ONES, "1011", trace=True)

# Ends-in-ab DFA (3 states: nothing useful, saw an a, saw ab)
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
@LIA.eval(`["main.py"]`, `none`, `python3 main.py`)

### Reading the Code

- `EVEN_ONES` is the five-tuple, field for field: `states` is $Q$, `delta` is $\delta$, `start` is $q_0$, and `accept` is $F$.  The alphabet $\Sigma$ is implicit in the keys of the inner dicts.
- `run_dfa` is the entire recognizer, and it never changes.  Only the data that describes the machine changes.  Your lexer assignment uses the same split between the runner and the machine description.
- The `if ch not in ...` guard implements a dead state without naming it.  A dead state is a trap: once the machine enters it, no further input can lead to acceptance.  A textbook DFA must have a transition for every symbol from every state, so a complete version would send the `a` in `abc` to an explicit trap state.  This version returns early instead, which is why `"abc"` returns `False` rather than raising an error.
- In `ENDS_IN_AB_DFA`, look at `q_ab` on input `a`.  It goes to `q_a`, not to `q0`.  That `a` is not wasted; it might be the start of the next `ab`.  Getting that arrow wrong is the most common bug in hand-built DFAs.

### Critical Thinking Questions

5.  `EVEN_ONES` accepts the empty string.  Point to the line of code *and* the part of the formal definition that together make that happen.  Then decide whether accepting it is correct for "even number of 1s."
6.  Encode your ends-in-`ab` DFA from CTQ 2 in the same dictionary format and test five strings.  What was mechanical, and what required thought?  That split is the point: the design is the thinking, and the runner is ten lines that never change.
7.  `ENDS_IN_AB_DFA` has three states.  If the target were "ends in `abc`", how many states would you need, and what would each remember?

### Try It Yourself

Build the "contains `aa`" machine from CTQ 3 and see how it differs from "ends in `aa`".

```python
def run_dfa(machine, s):
    state = machine["start"]
    for ch in s:
        if ch not in machine["delta"].get(state, {}):
            return False
        state = machine["delta"][state][ch]
    return state in machine["accept"]

# TODO: fill in the delta table for "contains the substring aa".
# Hint: once you have SEEN aa, no later input can un-see it. What does that
# say about the transitions out of your accepting state?
CONTAINS_AA = {
    "start": "q0",
    "accept": {"q_seen"},
    "delta": {
        "q0":     {"a": "q_a", "b": "q0"},
        "q_a":    {"a": "?",   "b": "?"},     # TODO
        "q_seen": {"a": "?",   "b": "?"},     # TODO
    },
}

# For contrast, here is ENDS in aa, already done for you.
ENDS_IN_AA = {
    "start": "p0",
    "accept": {"p_aa"},
    "delta": {
        "p0":   {"a": "p_a",  "b": "p0"},
        "p_a":  {"a": "p_aa", "b": "p0"},
        "p_aa": {"a": "p_aa", "b": "p0"},
    },
}

tests = ["aa", "aab", "baa", "baab", "aba", "b", ""]
print(f"  {'input':8} {'contains aa':>12} {'ends in aa':>12}")
for s in tests:
    print(f"  {s!r:8} {str(run_dfa(CONTAINS_AA, s)):>12} {str(run_dfa(ENDS_IN_AA, s)):>12}")

print("\nWhich inputs do the two machines disagree on? That disagreement IS the")
print("difference between 'contains' and 'ends in'. Name it in one sentence.")
```
@LIA.eval(`["main.py"]`, `none`, `python3 main.py`)

Expected output once you fill in the table: the two machines agree on `aa` and `baa` and disagree on `aab` and `baab`, which contain `aa` but do not end in it.

---

# Part II: Designing DFAs, and Where They Stop

## 2.  Theory: A State Is What You Must Remember

Designing a DFA looks like art the first time and becomes mechanical the second, once you know the question to ask:

> **After reading some prefix of the input, what is the least I must remember to finish the job correctly?**

Every distinct answer to that question is one state.  That is the whole method.

For "even number of 1s," the answer is one bit of parity, so there are two states.  For "ends in `ab`," the answer is how much of the pattern `ab` you have just finished: nothing, an `a`, or a whole `ab`.  Three answers, three states.  For "ends in `abc`," four.  In general, a pattern of length $k$ needs about $k+1$ states, because the thing you must remember is how much of the pattern is in progress right now.

Now turn the method on a language it cannot handle.  For $a^n b^n$, what must you remember after reading some `a`s?  The exact count, because you will need to demand the same number of `b`s.  And $n$ has no upper bound.  Every distinct count is a distinct state, so the machine needs infinitely many states, and a DFA has finitely many by definition.

That is not a failure of cleverness.  It is a proof, and it is the same boundary you met in *Grammars and the Chomsky Hierarchy*: regular languages end exactly where unbounded counting begins.

Remember two things from this section.  Each distinct thing the machine must remember is one state.  When that set of things is unbounded, no DFA exists.

## Examples: Deriving the Ends-in-`ab` Machine

Instead of drawing arrows and hoping, build the machine by tabulating the answer to the design question.  Work down this table with your team before you run the model:

| After reading... | What must I remember? | State |
|------------------|-----------------------|-------|
| `""` | nothing useful yet | `q0` |
| `"a"` | I have an `a` pending | `q_a` |
| `"ab"` | I just completed `ab` | `q_ab` |
| `"aba"` | the `b` is stale, but I have an `a` pending | `q_a` |
| `"abab"` | I just completed `ab` again | `q_ab` |
| `"b"` | nothing useful | `q0` |
| `"aa"` | still just an `a` pending, the older one is irrelevant | `q_a` |

The fourth and seventh rows reuse existing states.  That reuse is the finiteness: infinitely many input prefixes collapse into three buckets, because within a bucket the future behaves the same way.

## Model 3: How State Count Grows, and Where It Explodes

This model builds "ends in `p`" machines automatically for patterns of increasing length, so you can watch the state count follow the pattern length.  It then tries the same trick on $a^n b^n$ and fails on purpose.

```python
def build_ends_with(pattern, alphabet):
    """Build a DFA accepting strings that END WITH `pattern`.
    A state is 'how many characters of the pattern I have just completed'."""
    n = len(pattern)
    delta = {}
    for i in range(n + 1):                 # states 0..n
        delta[i] = {}
        for ch in alphabet:
            # Longest suffix of (first i chars of pattern) + ch that is
            # itself a prefix of pattern. THIS is the "what must I remember".
            cand = pattern[:i] + ch
            k = min(len(cand), n)
            while k > 0 and cand[-k:] != pattern[:k]:
                k -= 1
            delta[i][ch] = k
    return {"start": 0, "accept": {n}, "delta": delta}

def run_dfa(m, s):
    state = m["start"]
    for ch in s:
        if ch not in m["delta"].get(state, {}):
            return False
        state = m["delta"][state][ch]
    return state in m["accept"]

print("=== 'Ends with P': one state per amount-of-pattern-completed ===")
probes = ["abc", "abcab", "cab", "ccca", "abcabc"]
for pattern in ["a", "ab", "abc", "abca", "abcab"]:
    m = build_ends_with(pattern, "abc")
    accepted = [s for s in probes if run_dfa(m, s)]
    print(f"  pattern {pattern!r:8} -> {len(m['delta'])} states, "
          f"accepts {accepted if accepted else 'none of the probes'}")

print("\n  A pattern of length k needs k+1 states. Finite pattern, finite machine.")

print("\n=== Now try the same idea on a^n b^n ===")
def build_anbn_up_to(max_n, alphabet="ab"):
    """Count a's in the state, then require the same number of b's.
    We can only build states up to max_n, because a DFA has FINITELY many."""
    delta = {}
    for i in range(max_n + 1):
        delta[("a", i)] = {}
        if i < max_n:
            delta[("a", i)]["a"] = ("a", i + 1)
        if i > 0:
            delta[("a", i)]["b"] = ("b", i - 1)
    for i in range(max_n + 1):
        delta[("b", i)] = {}
        if i > 0:
            delta[("b", i)]["b"] = ("b", i - 1)
    return {"start": ("a", 0), "accept": {("b", 0)}, "delta": delta}

def in_anbn(s):
    """The ground truth: is s really of the form a^n b^n for some n >= 1?"""
    n = len(s) // 2
    return n >= 1 and s == "a" * n + "b" * n

for max_n in [3, 5, 20]:
    m = build_anbn_up_to(max_n)
    # Every machine gets its OWN witness: one more a's and b's than it can count.
    witness = "a" * (max_n + 1) + "b" * (max_n + 1)
    tests = ["ab", "aabb", "aaabbb", "aaaabbbb", "aab"]
    if witness not in tests:
        tests.append(witness)
    print(f"\n  a machine with room to count to {max_n} "
          f"({len(m['delta'])} states):")
    for s in tests:
        verdict = run_dfa(m, s)
        shown = s if len(s) <= 14 else s[:6] + "..." + s[-4:]
        mark = "" if verdict == in_anbn(s) else "   <-- WRONG, and this string IS legal"
        print(f"    {shown:16} -> {str(verdict):5}{mark}")

print("\n  Look at the last line of each block. Every machine, however many")
print("  states you give it, is wrong on the string with one more pair than")
print("  it can count, and that string is always a legal member of a^n b^n.")
print("  The fix is always 'add more states', so there is no finite number")
print("  that finishes the job. That is the regular-language ceiling, and it")
print("  is why a^n b^n needs the stack you met in the Grammars activity.")
```
@LIA.eval(`["main.py"]`, `none`, `python3 main.py`)

### Reading the Code

- `build_ends_with` is the Examples table, automated.  Its state is the integer `i`, meaning "I have just completed the first `i` characters of the pattern."
- The `while k > 0 and cand[-k:] != pattern[:k]` loop is the interesting line.  After reading `ch`, it finds the longest suffix of what you have that is still a live prefix of the pattern.  That is the `q_ab --a--> q_a` arrow from Model 2, done in general.  It is also the heart of the Knuth-Morris-Pratt string search algorithm.
- `build_anbn_up_to` is doomed on purpose.  Its state is a `(phase, count)` pair, and `max_n` caps the count because a DFA must have a finite state set.  Every choice of `max_n` gives a machine that is wrong on some legal string.
- The `<-- WRONG` marks are the point of the model.  They are not bugs in the code; they are the theorem.

> **Watch out!**  "Just use a bigger `max_n`" feels like a fix and is not one.  The definition of a regular language demands one machine that is correct on all inputs.  A family of machines, one per input size, is a different and much weaker claim.  If you find yourself saying "big enough for the inputs we care about," you have left theory and entered engineering.  That is fine, but say which one you are doing.

### Critical Thinking Questions

8.  In `build_ends_with`, trace by hand which state the `"abcab"` machine is in after reading `"abca"`, and then after one more `b`.  Why does the machine *not* go back to state 0 when the input stops matching?
9.  Run the pattern `"aaa"` through `build_ends_with` and predict the transition on `a` from the accepting state.  Is it a self-loop?  Explain in terms of "what must I remember."
10.  The model runs `max_n` at 3, 5, and 20, and each machine loses to its own witness.  Add `max_n = 500` to the list.  Which strings are handled now, and which witness still defeats it?  Write the formula for the witness in terms of `max_n`, then use it to explain why no finite choice ever works.
11.  Connect back: *Grammars and the Chomsky Hierarchy* showed a stack machine handling $a^n b^n$ easily.  State in one sentence what a stack has that a state set does not.

### Try It Yourself

Use `build_ends_with` to answer CTQ 7 by experiment, then break it.

```python
def build_ends_with(pattern, alphabet):
    n = len(pattern)
    delta = {}
    for i in range(n + 1):
        delta[i] = {}
        for ch in alphabet:
            cand = pattern[:i] + ch
            k = min(len(cand), n)
            while k > 0 and cand[-k:] != pattern[:k]:
                k -= 1
            delta[i][ch] = k
    return {"start": 0, "accept": {n}, "delta": delta}

def run_dfa(m, s):
    state = m["start"]
    for ch in s:
        if ch not in m["delta"].get(state, {}):
            return False
        state = m["delta"][state][ch]
    return state in m["accept"]

# TODO 1: how many states does "ends in abc" need? Predict, then check.
# TODO 2: try the pattern "aaa" over the alphabet "ab" and print its delta.
#         Explain the transition from state 3 on input 'a'.
# TODO 3: try the pattern "abab". State 4 on input 'a' does NOT go to 0.
#         Where does it go, and why is that the right answer?

for pattern in ["abc", "aaa", "abab"]:
    m = build_ends_with(pattern, "ab" if set(pattern) <= set("ab") else "abc")
    print(f"\npattern {pattern!r}: {len(m['delta'])} states")
    for state, row in m["delta"].items():
        mark = " (accepting)" if state in m["accept"] else ""
        print(f"    state {state}{mark}: {row}")
```
@LIA.eval(`["main.py"]`, `none`, `python3 main.py`)

Expected output: `"abc"` has 4 states, `"aaa"` has 4, and `"abab"` has 5.  State 4 of the `"abab"` machine goes to state 3 on `a`, not to 0.  Say why in one sentence.

---

# Check Your Understanding

A DFA's entire memory, at any moment during a run, consists of:

[(X)] Which state it is currently in
[( )] The state plus the input read so far
[( )] The state plus a stack of previously visited states
[( )] The whole input string, which it can re-read

---

In `ENDS_IN_AB_DFA`, the transition `q_ab --a--> q_a` (rather than to `q0`) is there because:

[(X)] That `a` may be the first character of the next `ab`, so it must not be thrown away
[( )] `q0` is the start state and cannot be re-entered
[( )] Every accepting state must have a self-loop
[( )] It makes the machine smaller

---

Why can no DFA recognize $a^n b^n$?

[(X)] It would need a distinct state per possible count of a's, and the count is unbounded
[( )] The language is not context-free
[( )] DFAs cannot read the same symbol twice
[( )] `a` and `b` cannot both appear in one alphabet

---

A pattern of length $k$ needs roughly how many states in an "ends with" DFA?

[( )] $2^k$
[(X)] $k+1$, one per amount of the pattern currently completed
[( )] $k$, one per character
[( )] It depends on the size of the alphabet, not on $k$

---

# Exercises

**Exercise 1.**  Draw, then encode, a DFA over $\{0,1\}$ that accepts binary numbers divisible by 3, reading the most significant bit first.  Hint: apply the design question.  What must you remember about the number so far?

**Exercise 2.**  Start from `build_ends_with` and write the mirror function `build_contains`, which accepts any string that *contains* the pattern.  You can do it by changing one thing about the accepting state's transitions.  Say what and why.

**Exercise 3.**  The `run_dfa` in this deck returns early on a missing transition instead of using an explicit dead state.  Rewrite `EVEN_ONES` as a *complete* DFA over the alphabet `{0,1,a,b,c}` with a real trap state, and confirm it gives the same answers.  Which version would you rather debug, and which is closer to the definition?

**Exercise 4.**  For your project's lexer, pick one token class (identifiers, integer literals, or string literals) and draw its DFA.  How many states does it have, and what does each remember?  Then say whether you will implement it as a DFA or hand it to a regex engine, and why.

**Exercise 5.**  Instrument `run_dfa` to record the sequence of states it visits, then run it on a 1000-character random binary string with `EVEN_ONES`.  How much memory did the *machine* use, apart from your instrumentation?  Use the answer to explain the phrase "finite memory" precisely.

---

# Reflection

The design question for a DFA is "what is the least I must remember?"  That question is not really about automata.  It is the question behind every cache, every summary, and every progress bar, and behind every time you wrote something down so you could stop holding it in your head.

In your notebook, write a paragraph about a time you found the right thing to remember and the problem got easy.  Then write two sentences about $a^n b^n$: what does it feel like to prove that no amount of cleverness will work, rather than merely failing to find a solution?

---

# Answer Key

Worked answers to the *mechanical* questions.  The design questions (2, 3, 4, 6) are left open on purpose; bring your machines to class.

**CTQ 1.**  The trace is the table in the Examples section: `even`, `odd`, `odd`, `even`, `odd`.  Final state `odd` is not accepting, so `1011` is rejected.

**CTQ 5.**  In code, the `for` loop body never runs for `""`, so `state` is still `machine["start"]`, which is `"even"`, and `"even" in machine["accept"]` is `True`.  In the definition, $\varepsilon$ is accepted exactly when $q_0 \in F$.  It is correct: zero is an even number.

**CTQ 7.**  Four states, remembering: nothing, just saw `a`, just saw `ab`, just saw `abc`.

**CTQ 8.**  After `"abca"` the `"abcab"` machine is in state 4 (it has completed `abca`).  After one more `b` it is in state 5, which is accepting.  It does not reset to 0 mid-input because a partial match is still live information.

**CTQ 9.**  Yes, a self-loop.  For pattern `"aaa"`, state 3 on input `a` stays at 3: the last three characters are still `aaa`, so the machine has still "just completed" the pattern.

**CTQ 10.**  With `max_n = 500`, every short test is handled, but the witness `"a"*501 + "b"*501` is not.  The witness is always `"a"*(max_n+1) + "b"*(max_n+1)`, so for any finite `max_n` you can name a legal string the machine rejects.  That is the whole argument.

---

# Further Reading

- Allison, Chapter 2 §2.1-2.2, on deterministic and non-deterministic finite automata.
- Allison, Chapter 2 §2.4, on machines with output and lexical analysis.
- Hopcroft, Motwani, and Ullman, *Introduction to Automata Theory*: the Myhill-Nerode theorem makes the "what must I remember" method into a precise statement about the minimum number of states.

---

> **Continued next session.**  Day 2 picks up from here: [Finite Automata, Day 2: Nondeterminism and Equivalence](https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374-Fall2026/gh-pages/_pages/Activities/liascript-automata-day2.md).
