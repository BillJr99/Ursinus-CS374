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

Think of a turnstile at a subway station.  It has exactly two states (**locked** and **unlocked**) and two transitions: inserting a coin moves it from locked to unlocked, and pushing moves it from unlocked back to locked.  That tiny machine already captures the essence of a finite automaton: a fixed set of states, arrows triggered by input symbols, and a yes/no verdict at the end.  The remarkable fact you will discover today is that this humble model is *exactly* as powerful as every pattern you wrote in the *Regular Expressions* activity.

## Learning Goals

By the end of this activity, you will be able to:

- Define a DFA as a five-tuple and trace its execution on an input string, identifying the state after each symbol and determining acceptance or rejection
- Construct a DFA for a specified regular language by identifying the finite information the machine must track and assigning one state per distinguishable memory value
- Encode a DFA as a transition table and simulate it, connecting the automaton model to the operation of a regex-based lexer
- Predict how many states a pattern needs before you draw it, by asking what the machine must remember
- Demonstrate concretely where finite memory fails, and name the language class that failure puts you in

A regular expression *describes* a set of strings; a **finite automaton** *recognizes* one.  It is a machine so simple it is just states and arrows, and yet exactly as powerful as the regex notation.  Over two days we build the machine view: **DFAs $\rightarrow$ designing them $\rightarrow$ NFAs $\rightarrow$ their surprising equivalence**, the theory under your next assignment and the engine inside every lexer, including yours.

> **Before You Begin**, make sure you can:
> - Describe what a regular expression *denotes* (the set of strings it matches), not just write one
> - Create and look up values in a Python `dict`, including a dict whose values are themselves dicts
> - Trace a simple `for` loop by hand, tracking the value of one variable through each iteration

---

## Directions and Group Roles

Work in your POGIL team with your rotated roles (**Manager**, **Recorder**, **Presenter**, **Reflector**).  Trace on paper before you run anything: every model in this deck is designed so that you can predict its output, and the moments where your prediction and the machine disagree are the ones worth talking about.  The Recorder posts your answers to the Class Activity Questions discussion board, and the Presenter reports out wherever your team disagreed or found another approach.

---

# Part I: Deterministic Finite Automata

## 1.  Theory: The Machine

**A DFA is a five-tuple** $M = (Q, \Sigma, \delta, q_0, F)$: a finite set of states $Q$, an input alphabet $\Sigma$, a transition function $\delta: Q \times \Sigma \rightarrow Q$, a start state $q_0$, and accepting states $F \subseteq Q$.  The machine reads the input one symbol at a time, moving deterministically; it **accepts** exactly when it finishes in an accepting state.

The machine's entire memory is *which state it is in*.  Finitely many states means finite memory, which is why this is the hierarchy's bottom rung.  Hold on to that sentence; Part II is built on it.

Here is a DFA accepting binary strings with an **even number of 1s**:

```
            0                0
          +---+            +---+
          v   |            v   |
   --> ((even)) --1-->  (odd)
          ^                 |
          `-------1---------+
```

Two states suffice because the machine only needs to remember one bit: the parity so far.

## Examples: Tracing `1011` by Hand

Do this trace yourself before reading the table.  The point of writing it out rather than "just running it" is that you can do this on paper in an exam, in a design meeting, or before the code exists.

| Step | State before | Symbol read | Transition used | State after |
|------|--------------|-------------|-----------------|-------------|
| 0 | - | *(start)* | - | `even` |
| 1 | `even` | `1` | `even --1--> odd` | `odd` |
| 2 | `odd` | `0` | `odd --0--> odd` | `odd` |
| 3 | `odd` | `1` | `odd --1--> even` | `even` |
| 4 | `even` | `1` | `even --1--> odd` | `odd` |

Final state `odd`, which is **not** accepting, so `1011` is **rejected**.  It has three `1`s, and this machine accepts an even count.

Two habits worth forming from this small table.  First, the `0` transitions are self-loops: reading a `0` never changes the answer, which is the machine *saying* that zeros are irrelevant to parity.  A DFA's self-loops are always a claim about what the machine chooses to ignore.  Second, the state after step 4 is the entire memory of the computation.  The machine has forgotten that it read `1011` and remembers only "odd so far."  That is exactly the limitation you will run into in CTQ 4.

## Model 1: Trace and Design

Now design two machines of your own.  Draw them; do not write code yet.

### Critical Thinking Questions

1.  Trace `1011` through the parity DFA, listing the state after each symbol.  Accepted or rejected?  The Recorder writes the trace.
2.  Design (draw) a DFA over $\{a, b\}$ accepting strings that **end in `ab`**.  How many states did your team need, and what does each state remember?
3.  Design a DFA accepting strings **containing** the substring `aa`.  Compare with question 2: ending-in versus containing changes which states are accepting.  Articulate how.
4.  Try to design a DFA for $a^n b^n$.  Where does finite memory fail you, and which prior module predicted this?

## Model 2: DFA Simulation, a Dictionary and a Loop

The formal five-tuple maps almost directly onto a Python data structure: states become string keys, the transition function becomes a `dict` of `dict`s, and the whole simulation is a loop that does one dictionary lookup per character.

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

- `EVEN_ONES` is the five-tuple, field for field: `states` is $Q$, `delta` is $\delta$, `start` is $q_0$, `accept` is $F$.  The alphabet $\Sigma$ is implicit in the keys of the inner dicts.
- `run_dfa` is the entire recognizer, and it never changes.  Only the *data* describing the machine changes.  That separation between the runner and the machine description is exactly the architecture your lexer assignment uses.
- The `if ch not in ...` guard implements the **dead state** without giving it a name.  A textbook DFA is required to have a transition for every symbol from every state, so a real one would send `abc`'s `a` to an explicit trap state.  This version short-circuits instead, which is why `"abc"` returns `False` rather than raising.
- In `ENDS_IN_AB_DFA`, look at `q_ab` on input `a`.  It goes back to `q_a`, not to `q0`.  That `a` is not wasted: it might be the start of the *next* `ab`.  Getting that arrow wrong is the single most common bug in hand-built DFAs.

### Critical Thinking Questions

5.  The empty string is accepted by `EVEN_ONES`.  Point to the line of code *and* the part of the formal definition that together make that happen, then decide whether it is correct for "even number of 1s."
6.  Encode your ends-in-`ab` DFA from CTQ 2 in the same dictionary format and test five strings.  What was mechanical and what required thought?  That split is the point: the *design* is the thinking; the *runner* is ten lines forever.
7.  `ENDS_IN_AB_DFA` has three states.  If the target were "ends in `abc`", how many states would be needed, and what would each remember?

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

Expected output once your table is filled in: the two machines agree on `aa` and `baa` and disagree on `aab` and `baab`, which contain `aa` but do not end in it.

---

# Part II: Designing DFAs, and Where They Stop

## 2.  Theory: A State Is What You Must Remember

Designing a DFA looks like art the first time and becomes mechanical the second, once you know the question to ask:

> **After reading some prefix of the input, what is the least I must remember in order to finish the job correctly?**

Every distinct answer to that question is one state.  That is the whole method.

For "even number of 1s," the answer is a single bit of parity, so there are two states.  For "ends in `ab`," the answer is how much of the pattern `ab` you have just finished: nothing, an `a`, or a whole `ab`.  Three answers, three states.  For "ends in `abc`," four.  The pattern generalizes: a pattern of length $k$ needs about $k+1$ states, because the thing you must remember is *how much of the pattern is currently in progress*.

Now turn the method against a language it cannot handle.  For $a^n b^n$, what must you remember after reading some `a`s?  The count, exactly, because you will need to demand the same number of `b`s.  And $n$ is unbounded.  Every distinct count is a distinct state, so the machine needs infinitely many states, and a DFA has finitely many by definition.

That is not a failure of cleverness.  It is a proof, and it is the same boundary you met in *Grammars and the Chomsky Hierarchy*: regular languages end exactly where unbounded counting begins.

## Examples: Deriving the Ends-in-`ab` Machine

Rather than drawing arrows and hoping, build the machine by tabulating the answer to the question.  Work down this table with your team before running the model:

| After reading... | What must I remember? | State |
|------------------|-----------------------|-------|
| `""` | nothing useful yet | `q0` |
| `"a"` | I have an `a` pending | `q_a` |
| `"ab"` | I just completed `ab` | `q_ab` |
| `"aba"` | the `b` is stale, but I have an `a` pending | `q_a` |
| `"abab"` | I just completed `ab` again | `q_ab` |
| `"b"` | nothing useful | `q0` |
| `"aa"` | still just an `a` pending, the older one is irrelevant | `q_a` |

Notice that the fourth and seventh rows *reuse* existing states.  That reuse is the finiteness: infinitely many input prefixes collapse into three buckets, because within a bucket the future behaves identically.

## Model 3: How State Count Grows, and Where It Explodes

This model builds "ends in `p`" machines automatically for patterns of increasing length, so you can watch the state count track the pattern, and then tries the same trick on $a^n b^n$ and fails on purpose.

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
- The `while k > 0 and cand[-k:] != pattern[:k]` loop is the interesting line: after reading `ch`, it finds the *longest* suffix of what you have that is still a live prefix of the pattern.  That is the same reasoning as the `q_ab --a--> q_a` arrow you were warned about in Model 2, done in general.  It is also, not coincidentally, the heart of the Knuth-Morris-Pratt string search algorithm.
- `build_anbn_up_to` is deliberately doomed.  Its state is a `(phase, count)` pair, and `max_n` caps the count because a DFA must have a finite state set.  Every choice of `max_n` yields a machine that is wrong on some legal string.
- The `<-- WRONG` marks are the point of the model.  They are not bugs in the code; they are the theorem.

> **Watch out!**  "Just use a bigger `max_n`" feels like a fix and is not one.  The definition of a regular language demands *one* machine that is correct on *all* inputs.  A family of machines, one per input size, is a different and much weaker claim.  If you find yourself saying "big enough for the inputs we care about," you have left theory and entered engineering, which is fine, but say which one you are doing.

### Critical Thinking Questions

8.  In `build_ends_with`, trace by hand what state the pattern `"abcab"` machine is in after reading `"abca"`.  Then after reading one more `b`.  Why does the machine *not* go back to state 0 when the input stops matching?
9.  Run the pattern `"aaa"` through `build_ends_with` and predict the transition on `a` from the accepting state.  Is it a self-loop?  Explain in terms of "what must I remember."
10.  The model already runs `max_n` at 3, 5, and 20, and each machine is defeated by its own witness.  Add `max_n = 500` to the list.  Which strings are handled now, and what is the witness that still defeats it?  Write the formula for the witness in terms of `max_n`, and use it to explain why no finite choice ever works.
11.  Connect back: *Grammars and the Chomsky Hierarchy* showed a stack machine handling $a^n b^n$ easily.  State in one sentence what a stack has that a state set does not.

### Try It Yourself

Use `build_ends_with` to answer CTQ 7 empirically, then break it.

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

Expected output: `"abc"` has 4 states; `"aaa"` has 4; `"abab"` has 5, and its state 4 goes to state 3 on `a`, not to 0.  Say why in one sentence.

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

**Exercise 1.**  Draw and then encode a DFA over $\{0,1\}$ accepting binary numbers divisible by 3, reading most-significant bit first.  Hint: apply the design question.  What must you remember about the number so far?

**Exercise 2.**  Take `build_ends_with` and write the mirror function `build_contains`, which accepts any string *containing* the pattern.  You should be able to do it by changing one thing about the accepting state's transitions.  Say what and why.

**Exercise 3.**  The `run_dfa` in this deck short-circuits on a missing transition instead of using an explicit dead state.  Rewrite `EVEN_ONES` as a *complete* DFA over the alphabet `{0,1,a,b,c}` with a real trap state, and confirm it gives the same answers.  Which version would you rather debug, and which is closer to the definition?

**Exercise 4.**  For your project's lexer, pick one token class (identifiers, integer literals, or string literals) and draw its DFA.  How many states?  What does each remember?  Then say whether you will actually implement it as a DFA or hand it to a regex engine, and why.

**Exercise 5.**  Instrument `run_dfa` to record the sequence of states visited, then run it on a 1000-character random binary string with `EVEN_ONES`.  How much memory did the *machine* use, as opposed to your instrumentation?  Use this to explain the phrase "finite memory" precisely.

---

# Reflection

In your notebook: the design question for a DFA is "what is the least I must remember?"  That question has nothing to do with automata; it is the question behind every cache, every summary, every progress bar, and every time you have written something down so you could stop holding it in your head.

Write a paragraph about a time you found the right thing to remember and the problem got easy.  Then write two sentences about $a^n b^n$: what does it feel like to prove that no amount of cleverness will work, rather than merely failing to find a solution?

---

# Answer Key

Worked answers to the *mechanical* questions.  The design questions (2, 3, 4, 6) are deliberately left open; bring your machines to class.

**CTQ 1.**  The trace is the table in the Examples section: `even`, `odd`, `odd`, `even`, `odd`.  Final state `odd` is not accepting, so `1011` is rejected.

**CTQ 5.**  In code, the `for` loop body never executes for `""`, so `state` is still `machine["start"]`, which is `"even"`, and `"even" in machine["accept"]` is `True`.  In the definition, $\varepsilon$ is accepted exactly when $q_0 \in F$.  It is correct: zero is an even number.

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
