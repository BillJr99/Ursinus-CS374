---
layout: assignment
permalink: /Assignments/Automata
title: "CS374: Principles of Programming Languages - Lab: Finite Automata Simulators"

info:
  coursenum: CS374
  purpose: "To build general simulators for deterministic finite automata (DFAs) and nondeterministic finite automata (NFAs) that read machine definitions from data files, so the theory beneath every lexer becomes a program you can run, and to trace the subset construction and Thompson's construction once by hand."
  tilt:
    task: "Individually or with a partner, build DFA and NFA simulators that read machines from JSON, design one machine of each kind, and trace the subset construction and Thompson's construction by hand on small examples."
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

In this lab you write two programs that run finite automata: a DFA simulator and an NFA simulator.  Each one reads a machine from a JSON file, so a single program runs any machine you or I give it.  These machines sit underneath every lexer, including the one you build next.  You also design one DFA and one NFA, and you trace two classic constructions by hand.  Parts 0 and 3 are paper work; Parts 1 and 2 are code.

**Pair policy.**  You may work in pairs or alone.  A pair can share one screen, or split the DFA and NFA halves and review each other's work.  Both partners submit the same ZIP, name each other in the writeup, and earn the same grade.  This lab needs no individual-work certification.  The reflection asks who did what instead.

The rest of this opening defines every idea the lab uses and works an example of each, so this page is all you need to finish.  The Finite Automata activity in the readings covers the same material if you want a second explanation.

### Finite automata in one paragraph

A finite automaton has a finite set of states and an alphabet of input symbols.  One state is the start state, and some states are accepting states.  A transition function $$\delta$$ says where to go on each symbol.  To run one, begin in the start state and read the input one symbol at a time, following one arrow per symbol.  When the input runs out, accept if you are in an accepting state; otherwise reject.  The empty string `""` reads no symbols.  It is accepted only when the start state is accepting.

### DFA versus NFA

A DFA (deterministic finite automaton) has one arrow out of every state on every symbol.  It never has a choice, so it is always in one state.

An NFA (nondeterministic finite automaton) relaxes both rules.  A state may have several arrows on the same symbol, or none.  It may also have ε-transitions (epsilon transitions): arrows the machine may follow without reading any input.  An NFA accepts a string if any sequence of choices ends in an accepting state.

You do not have to guess which choice is right.  Follow every choice at once, and keep track of the set of states the NFA could be in right now.  We call that set the *active set*.  Tracking it is how `run_nfa` works in Part 2, and it is also how the subset construction works in Part 3.

### ε-closure: the free moves

An ε-transition costs no input.  So if the NFA could be in state $$q$$, it could also be in every state it can reach from $$q$$ by ε-moves alone.  The ε-closure of a set $$S$$, written $$E(S)$$, is $$S$$ plus every state reachable from a state in $$S$$ by zero or more ε-transitions.  Because zero moves count, every state is in its own closure.

*Example.*  Suppose the only ε-arrows are $$q_0 \xrightarrow{\varepsilon} q_1$$ and $$q_1 \xrightarrow{\varepsilon} q_2$$.  Then $$E(\{q_0\}) = \{q_0, q_1, q_2\}$$, $$E(\{q_1\}) = \{q_1, q_2\}$$, and $$E(\{q_2\}) = \{q_2\}$$.  Closure follows arrows forward only, so $$q_0$$ is not in $$E(\{q_1\})$$.

### One step of an NFA: the union, then the closure

Both `run_nfa` and the subset construction repeat one rule.  If the active set is $$S$$ and the next symbol is $$a$$, the next active set is

$$
\text{next}(S, a) \;=\; E\Big(\bigcup_{q \in S} \delta(q, a)\Big).
$$

The rule has two parts:

1. Move, by taking a union.  For every state $$q$$ in $$S$$, look up where $$q$$ goes on $$a$$.  Each lookup gives a set, which may be empty.  Take the union of all those sets.  The result holds every state the NFA can reach on that one `a` from anywhere it might be now.
2. Close.  Take the ε-closure of that union, because after reading `a` the machine may also slide along free moves.

Remember it as *move, then ε-close*.  If no state in $$S$$ has an arrow on $$a$$, the union is empty and so is its closure.  The NFA is then stuck, and it rejects every string that begins this way.  Close the start of a run, too.  The first active set is $$E(\{\text{start}\})$$, not $$\{\text{start}\}$$.

*Worked example 1, with no ε-moves: "ends in `ab`".*  This NFA over `{a, b}` starts in `q0` and accepts in `q2`.  It has one choice to make: on `a`, `q0` can stay where it is or guess that this `a` begins the final `ab`.

![NFA for strings that end in ab. States q0, q1, and q2; q0 is the start state and q2 is the only accepting state. q0 loops to itself on a or b, q0 goes to q1 on a, and q1 goes to q2 on b.]({{ site.baseurl }}/files/dotty/example_nfa_ends_in_ab.svg)

| state | on `a` | on `b` |
|---|---|---|
| q0 | {q0, q1} | {q0} |
| q1 | ∅ | {q2} |
| q2 | ∅ | ∅ |

Run it on `aab`.  The machine has no ε-arrows, so each closure leaves the set unchanged.

| Step | Union of the moves | Active set |
|---|---|---|
| start | (nothing read yet) | {q0} |
| read `a` | q0 → {q0, q1} | {q0, q1} |
| read `a` | q0 → {q0, q1} ∪ q1 → ∅ | {q0, q1} |
| read `b` | q0 → {q0} ∪ q1 → {q2} | {q0, q2} |
| end | {q0, q2} contains the accepting state q2 | accept |

Look closely at the last step.  The active set `{q0, q1}` moves on `b` to $$\delta(q0, b) \cup \delta(q1, b) = \{q0\} \cup \{q2\} = \{q0, q2\}$$.  Each state in the set contributes its own targets, and the union collects them.

*Worked example 2, with an ε-move: `ab?`.*  This NFA accepts an `a`, optionally followed by a `b`.  It starts in `q0` and accepts in `q2`.  The ε-arrow from `q1` to `q2` makes the `b` optional.

![Epsilon-NFA for a followed by an optional b. States q0, q1, and q2; q0 is the start state and q2 is the only accepting state. q0 goes to q1 on a, q1 goes to q2 on b, and q1 also goes to q2 on an epsilon move, drawn dashed.]({{ site.baseurl }}/files/dotty/example_epsnfa_ab_optional.svg)

Run it on `a`:

| Step | Move | Close | Active set |
|---|---|---|---|
| start | (nothing read yet) | E({q0}) = {q0} | {q0} |
| read `a` | q0 → {q1} | E({q1}) = {q1, q2} | {q1, q2} |
| end | | {q1, q2} contains q2 | accept |

Skip the closure after the move and the active set is `{q1}`, so `a` is wrongly rejected.  A missing closure, at the start or after a move, is the most common bug in this lab.

### The subset construction: the same step, done ahead of time

`run_nfa` computes active sets for one input string at a time.  The subset construction, also called the powerset construction, computes every reachable active set in advance and turns those sets into a DFA.  Each DFA state is one set of NFA states, called a *powerset state*.  Its transition on a symbol is the step you just saw:

$$
\delta_D(S, a) \;=\; E\Big(\bigcup_{q \in S} \delta(q, a)\Big).
$$

In words: a powerset state's transition on a symbol is the ε-closure of the union of every state reachable on that symbol from the states in the set.  The algorithm searches for those sets:

1. The DFA's start state is $$E(\{\text{start}\})$$.
2. Keep a list of powerset states you have found but not yet processed.  To process a set $$S$$, compute $$\delta_D(S, a)$$ for every symbol $$a$$ in the alphabet.  If a result is a set you have not seen, it is a new powerset state; add it to the list.
3. A powerset state accepts if it contains at least one accepting NFA state.
4. Stop when you have processed every powerset state.

A result can be the empty set ∅.  That is a real DFA state, called a *dead state*.  It loops to itself on every symbol and never accepts.  Give it a row in your table like any other state.

*Worked example 1: "ends in `ab`," from above.*

| Set being processed | Symbol | Union of the moves | Result | New? |
|---|---|---|---|---|
| {q0} | `a` | q0 → {q0, q1} | {q0, q1} | new |
| {q0} | `b` | q0 → {q0} | {q0} | |
| {q0, q1} | `a` | q0 → {q0, q1} ∪ q1 → ∅ | {q0, q1} | |
| {q0, q1} | `b` | q0 → {q0} ∪ q1 → {q2} | {q0, q2} | new |
| {q0, q2} | `a` | q0 → {q0, q1} ∪ q2 → ∅ | {q0, q1} | |
| {q0, q2} | `b` | q0 → {q0} ∪ q2 → ∅ | {q0} | |

Nothing is left to process, so the construction stops.  Collecting the results gives the DFA:

| Powerset state | on `a` | on `b` | Accepting? |
|---|---|---|---|
| {q0} | {q0, q1} | {q0} | No |
| {q0, q1} | {q0, q1} | {q0, q2} | No |
| {q0, q2} | {q0, q1} | {q0} | Yes (contains q2) |

Three NFA states allow up to $$2^3 = 8$$ subsets, but only three are reachable.  You can read a meaning off each one.  `{q0}` means no part of `ab` is in progress; `{q0, q1}` means the input just ended in `a`; `{q0, q2}` means it just ended in `ab`.  Compare the `aab` trace above: every set it printed is a row of this table.

*Worked example 2: `ab?`, from above, with closures and a dead state.*

The start state is E({q0}) = {q0}.

| Set being processed | Symbol | Move | Close | New? |
|---|---|---|---|---|
| {q0} | `a` | {q1} | {q1, q2} | new |
| {q0} | `b` | ∅ | ∅ | new (dead state) |
| {q1, q2} | `a` | ∅ | ∅ | |
| {q1, q2} | `b` | {q2} | {q2} | new |
| {q2} | `a` | ∅ | ∅ | |
| {q2} | `b` | ∅ | ∅ | |
| ∅ | `a` | ∅ | ∅ | |
| ∅ | `b` | ∅ | ∅ | |

| Powerset state | on `a` | on `b` | Accepting? |
|---|---|---|---|
| {q0} | {q1, q2} | ∅ | No |
| {q1, q2} | ∅ | {q2} | Yes |
| {q2} | ∅ | ∅ | Yes |
| ∅ | ∅ | ∅ | No |

### Thompson's construction: regex to NFA

Thompson's construction builds an NFA from a regular expression.  It follows fixed rules and needs no judgment, which is why lexer generators and regex engines can run it automatically.

*Why it works.*  Every regular expression is built from single symbols with three operators: concatenation (`AB`, A then B), union (`A|B`, A or B), and star (`A*`, A zero or more times).  The construction has one rule for a single symbol and one rule for each operator.  You apply the rules from the inside of the expression outward, so the NFA is assembled the same way the regex was.

*Why the result is an NFA.*  Union and star are choices.  `A|B` means "take either branch," and `A*` means "go around again, or stop."  An NFA states a choice directly, as two ε-arrows leaving one state, and the active-set method follows both arrows.  Resolving every choice in advance is the subset construction's job, not this one's.

*The rule every fragment obeys.*  Each fragment has one start state and one accepting state.  No arrows enter its start, and none leave its accept.  This rule lets fragments connect like plugs: to combine two fragments, you join one fragment's accept to another's start (or to a new state) with an ε-arrow.  Once a fragment is wired into a larger one, its old accepting state stops accepting.  In the finished NFA, only the outermost fragment's accept state accepts.

In the pictures below, `[ A ]` stands for a fragment you have already built for the sub-expression A.  Its start is on the left and its accept is on the right.

*Rule 1: a single symbol `x`.*  Create two states and one arrow.  The fragment accepts only the one-symbol string `x`.

![Thompson rule for a single symbol x: a start state s with one arrow labeled x to an accepting state f.]({{ site.baseurl }}/files/dotty/thompson_rule_symbol.svg)

*Rule 2: concatenation `AB`.*  Join A's accept to B's start with one ε-arrow.  The new fragment starts where A starts and accepts where B accepts, and it needs no new states.  Once A has matched its part of the input, the machine slides into B for free, and B matches the rest.

![Thompson rule for concatenation: fragment A, drawn as a box, joined to fragment B by one dashed epsilon arrow from A's accept to B's start.]({{ site.baseurl }}/files/dotty/thompson_rule_concat.svg)

*Rule 3: union `A|B`.*  Add a new start `s` with ε-arrows into both fragments.  Add a new accept `f` with ε-arrows out of both.  At `s` the machine would have to guess which branch the input follows.  The active set follows both, and the branch that matches reaches `f`.

![Thompson rule for union: a new start state s with dashed epsilon arrows into fragment A and fragment B, and dashed epsilon arrows from both fragments into a new accepting state f.]({{ site.baseurl }}/files/dotty/thompson_rule_union.svg)

*Rule 4: star `A*`.*  Add a new start `s`, a new accept `f`, and four ε-arrows.

![Thompson rule for star: a new start state s and a new accepting state f around fragment A. Dashed epsilon arrows go from s into A (enter), from A to f (stop), from A back to its own start (repeat), and from s straight to f (zero times).]({{ site.baseurl }}/files/dotty/thompson_rule_star.svg)

Each of the four arrows has one job:

| ε-arrow | its job |
|---|---|
| `s` to A's start | enter A to match one repetition |
| A's accept to `f` | stop after any number of repetitions |
| A's accept back to A's start | go around again for another repetition |
| `s` straight to `f` | match zero repetitions, so `A*` accepts the empty string |

Leave out the `s`-to-`f` arrow and `A*` becomes "one or more" (`A+`).  Leave out the back arrow and it becomes "zero or one" (`A?`).

*How to apply the rules.*  Start by reading the regex's structure.  Star binds tightest, then concatenation, then union, so `ab*|c` means `(a(b*))|c`.  Build fragments for the single symbols first.  Then apply each operator's rule to fragments you have already built, working outward.  Number the states in the order you create them, and keep those numbers when you reuse a fragment.  A reader can then find every earlier fragment inside the final machine.  Each rule adds at most two states, so the NFA has at most twice as many states as the regex has symbols and operators.

*Worked example 1: `(x|y)z`, a union and then a concatenation.*

| Step | Sub-expression | Rule | New states and arrows | Start, accept |
|---|---|---|---|---|
| 1 | `x` | 1 | 1 −x→ 2 | 1, 2 |
| 1 | `y` | 1 | 3 −y→ 4 | 3, 4 |
| 2 | `x\|y` | 3 | 5 −ε→ 1, 5 −ε→ 3, 2 −ε→ 6, 4 −ε→ 6 | 5, 6 |
| 3 | `z` | 1 | 7 −z→ 8 | 7, 8 |
| 4 | `(x\|y)z` | 2 | 6 −ε→ 7 | 5, 8 |

![The finished Thompson NFA for (x|y)z. Start state 5 has dashed epsilon arrows to 1 and 3; 1 goes to 2 on x and 3 goes to 4 on y; 2 and 4 have dashed epsilon arrows to 6; 6 has a dashed epsilon arrow to 7; 7 goes to the accepting state 8 on z.]({{ site.baseurl }}/files/dotty/thompson_xy_z.svg)

The finished NFA has eight states.  It starts at 5 and accepts only at 8.  States 2, 4, and 6 accepted in their own fragments, but they no longer do.  Check it on `yz` with the active-set method: $$E(\{5\}) = \{5, 1, 3\}$$; on `y`, move to $$\{4\}$$ and close to $$\{4, 6, 7\}$$; on `z`, move to $$\{8\}$$, which accepts.  Now try `xy`.  After `x` the active set is $$\{2, 6, 7\}$$.  None of those states has a `y` arrow, so the set becomes empty and the NFA rejects `xy`.

*Worked example 2: `(ab)*`, a concatenation and then a star.*

| Step | Sub-expression | Rule | New states and arrows | Start, accept |
|---|---|---|---|---|
| 1 | `a` | 1 | 1 −a→ 2 | 1, 2 |
| 1 | `b` | 1 | 3 −b→ 4 | 3, 4 |
| 2 | `ab` | 2 | 2 −ε→ 3 | 1, 4 |
| 3 | `(ab)*` | 4 | 5 −ε→ 1 (enter), 4 −ε→ 6 (stop), 4 −ε→ 1 (repeat), 5 −ε→ 6 (zero times) | 5, 6 |

![The finished Thompson NFA for (ab)*. Start state 5 has dashed epsilon arrows to 1 (enter) and to the accepting state 6 (zero times); 1 goes to 2 on a, 2 has a dashed epsilon arrow to 3, 3 goes to 4 on b, and 4 has dashed epsilon arrows to 6 (stop) and back to 1 (repeat).]({{ site.baseurl }}/files/dotty/thompson_ab_star.svg)

Trace three strings:

| String | Step | Move | Close | Active set |
|---|---|---|---|---|
| `""` | start | | E({5}) | {1, 5, 6}: contains 6, accept (zero repetitions) |
| `abab` | start | | E({5}) | {1, 5, 6} |
| | read `a` | {2} | E({2}) | {2, 3} |
| | read `b` | {4} | E({4}) | {1, 4, 6} (the repeat arrow puts 1 back in play) |
| | read `a` | {2} | E({2}) | {2, 3} |
| | read `b` | {4} | E({4}) | {1, 4, 6}: contains 6, accept |
| `aba` | after the second `a` | | | {2, 3}: no 6, reject |

A person would draw `(ab)*` with two states, so hand-drawn NFAs are often smaller than Thompson's.  The advantage of Thompson's construction is that a program can follow it mechanically.  The subset construction can tidy the result afterward.

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

The subset construction makes one DFA state for each set of NFA states the machine could be in at once.  The opening of this page explains it under *The subset construction*.  You trace it in full in Part 3, so a short first pass now pays off twice.

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

Open the folder in your editor and create one empty file at the top level, `writeup.md`.  It holds your Part 0 work, your test strings, your construction traces, and your reflection.  You create the two Python files when the steps ask for them, and each machine goes in `machines/` as its own JSON file.  This table shows which file each step writes, so you always know where new code goes:

| Step | File you work in | What you do there |
|---|---|---|
| 0.1, 0.2 | `writeup.md` | add your Part 0 paper work |
| 1.1 | `dfa_core.py` | create a ten-line DFA runner, then leave it alone |
| 1.1, 1.4 | `machines/even_ones.json`, `machines/ends_in_ab.json` | create the DFA machine files |
| 1.2 | `simulator.py` | create the file with the loader |
| 1.3 | `simulator.py` | add `run_dfa` and `main` |
| 2.1, 2.2, 2.4 | `machines/ends_in_ab_nfa.json`, `machines/eps_cycle.json`, `machines/contains_aa.json` | create the NFA machine files |
| 2.2 | `simulator.py` | add `eps_closure` |
| 2.3 | `simulator.py` | add `run_nfa` |
| 3.1 to 3.3 | `writeup.md` | add the construction traces and the lexer paragraph |

> **Time budget.** This lab follows the class material on regular expressions and finite automata.  The course schedule has the assigned and due dates.  Plan about three hours (with your partner, if you have one) for Parts 1 and 2, and about an hour for the paper work in Parts 0 and 3.  Write the reflection as you go, not at the end.
> - On assignment: the loader and DFA simulator work on the provided machines.
> - Midpoint: the NFA simulator and epsilon-closure work, and both designed machines are encoded and tested.
> - Due date: the construction traces and writeup are assembled and the ZIP is submitted.

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

Every program in this lab works on the same Python objects, so it is worth meeting them once before you write any of it.  When `json.load` reads the file above, each JSON object becomes a Python dictionary (`dict`) and each JSON list becomes a Python `list`.  The machine is therefore one dictionary with five keys, and the moves sit in `machine["delta"]`, which is a dictionary of dictionaries.

Finding the next state takes two lookups, one per level.  The first picks the row for the current state, and the second picks the arrow for the symbol:

| In the diagram | In the JSON | In Python | Value |
|---|---|---|---|
| the row of arrows out of `even` | `"even": {"0": "even", "1": "odd"}` | `delta["even"]` | `{'0': 'even', '1': 'odd'}` |
| the arrow out of `even` on `1` | `"1": "odd"` inside `"even"` | `delta["even"]["1"]` | `'odd'` |
| the next state, in general | | `delta[state][symbol]` | $$\delta(q, a)$$ |

Two more operations cover the rest of the DFA work:

- **Looking up a key that may be missing.**  `delta["happy"]` raises a `KeyError`, because there is no state named `happy`.  `delta.get("happy")` returns `None` instead, and `delta.get("happy", {})` returns the default you supply, here an empty dictionary.  You use `.get` in the loader (Step 1.2), whose job is to find missing pairs and report them.  You use plain `[...]` in `run_dfa` (Step 1.3), because by then the loader has proved that every pair exists.
- **Testing membership.**  `state in machine["accept"]` asks whether a state accepts, and `symbol in machine["alphabet"]` asks whether a symbol is legal.  Both are lists, which is fine for machines this small.  Turning them into sets with `set(...)` makes the test faster on large machines, and that change is optional.

To see all of this before you rely on it, save the lines below as `explore_dfa.py`, a scratch file you do not submit, and run `python3 explore_dfa.py` from inside `cs374-automata`:

```python
import json

with open("machines/even_ones.json") as f:
    machine = json.load(f)
delta = machine["delta"]

print(type(machine).__name__, sorted(machine))  # a dict, and its five keys
print(delta["even"])                            # the row for state even
print(delta["even"]["1"])                       # one arrow: even on 1
row = delta["even"]
print(row["0"])                                 # the same idea, in two steps
print(delta.get("happy"))                       # no such state: None, not a crash
print(delta.get("happy", {}).get("1"))          # missing row, then missing arrow
print("even" in machine["accept"], "2" in machine["alphabet"])
```

> **You should see.**
>
> ```text
> dict ['accept', 'alphabet', 'delta', 'start', 'states']
> {'0': 'even', '1': 'odd'}
> odd
> even
> None
> None
> True False
> ```
>
> **Predict** before you move on: what does `delta["odd"]["1"]` print, and which arrow in the diagram is it?

Start with this one machine, not with the full simulator.  The smallest program that runs it is about ten lines long, and you write it now in its own file, `dfa_core.py`.  Every later step builds on the same idea, so it pays to see it work in its plainest form first.

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

5. Inside the loop, follow one arrow.  `machine["delta"][state]` is the row for the current state, and `[symbol]` picks the arrow for this symbol.  This line is the transition function $$\delta(q, a)$$ written in Python, and it is the whole simulation.

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

**You write:** a new file, `simulator.py`, containing `MachineError`, `is_nfa`, and `load_machine`.  Do not edit `dfa_core.py`.
**You run:** `python3 -c "import simulator; simulator.load_machine('machines/even_ones.json')"`, then the same command on a broken file.

> **Do this.**
> 1. Create a new file, `simulator.py`, next to `dfa_core.py`.  Type in the skeleton below, and then fill in the `# TODO` lines using the hints after it.
> 2. `load_machine(path)` reads a JSON file and checks that the start state, the accept states, and every transition refer only to declared states and alphabet symbols.
> 3. Collect every validation error in a list, then raise one `MachineError` that lists them, one per line.  Do not stop at the first error.
> 4. Accept both `delta` shapes.  A DFA's `delta` is an object of objects.  An NFA's `delta` (Part 2) has `"state,symbol"` keys with list values, and the symbol half may be the special word `eps`.  Your check must let `eps` through for an NFA and reject every other symbol outside the alphabet.

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

    # The start state must be declared.  This first check is done for you;
    # every other check follows the same pattern.
    if machine["start"] not in states:
        errors.append(f"start state {machine['start']!r} is not a declared state")

    # TODO: every accept state must be in states

    if is_nfa(machine):
        # TODO: NFA: every "state,symbol" key must split into a declared state and
        #       either an alphabet symbol or "eps"; every target must be declared
        pass
    else:
        # TODO: DFA: every (state, symbol) pair over the alphabet must appear, and
        #       every delta[state][symbol] must name a declared state
        pass

    if errors:
        raise MachineError("\n".join(errors))
    return machine
```

The worked start-state check shows the pattern for every other check.  Test one condition, and when it fails, append a sentence to `errors` that names the bad value.  `!r` prints the value with quotes around it, so a stray space or a misspelling is easy to see.  Fill in the remaining checks one at a time, and replace each `pass` once its branch has real code:

| `# TODO` | How to write it |
|---|---|
| accept states | Loop `for state in machine["accept"]:` and append an error for each `state` that is not in `states`. |
| DFA pairs | Write two nested loops, `for state in machine["states"]:` and `for symbol in machine["alphabet"]:`.  Read the target with `target = machine["delta"].get(state, {}).get(symbol)`.  `.get` returns `None` instead of crashing, so `target is None` means the pair is missing; append an error that names both `state` and `symbol`.  Otherwise, if `target` is not in `states`, append an error that names the target. |
| NFA keys | Loop `for key, targets in machine["delta"].items():`.  Split the key with `state, _, symbol = key.partition(",")`.  Append an error if `state` is not in `states`, if `symbol` is neither in `alphabet` nor equal to `"eps"`, or if any entry of `targets` is not in `states`. |

You cannot test the NFA branch until Part 2 gives you an NFA file.  Write it now anyway, because Part 2 relies on it.

`simulator.py` has no command line yet, so you test it by importing it.  Test the loader on the good file first:

```bash
python3 -c "import simulator; simulator.load_machine('machines/even_ones.json')"
```

> **You should see.** Nothing.  Silence means the file passed.

Now check that the loader reports every problem at once, not just the first.  Save this deliberately broken machine as `machines/broken.json`.  It has a misspelled start state, a misspelled accept state, and no arrow out of `odd` on `1`.  It is a test file, and you do not need to submit it.

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
**You run:** `python3 simulator.py machines/even_ones.json 0110 --trace`, plus the two other commands after the code.

> **Do this.**
> 1. Add `run_dfa(machine, s, trace=False) -> bool` below the loader.  It must follow these rules:
>    - A symbol in `s` that is not in the alphabet causes an immediate reject.  Print a reason; do not crash.
>    - The empty string `""` is valid input.  It tests whether the start state accepts.
>    - With `trace` on, print the current state after each symbol.
> 2. Add a `main` that takes the machine path and the input string from the command line and honors a `--trace` flag.  `main` and the `if __name__ == "__main__":` lines go last in the file, so every function they call is defined above them.
> 3. Type `main` exactly as shown; it is complete.  Fill in the three `# TODO` lines in `run_dfa`, then delete its `pass`.

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

Each `# TODO` in `run_dfa` is one or two lines:

| `# TODO` | How to write it |
|---|---|
| unknown symbol | `if symbol not in machine["alphabet"]:` then `print(f"reject: symbol {symbol!r} is not in the alphabet")` and `return False`. |
| move | `state = machine["delta"][state][symbol]`, the same line as in `dfa_core.py`.  It is safe now, because the loader already proved that every pair exists.  *Before You Code: How a DFA Lives in Python* in Step 1.1 shows the two lookups. |
| trace | `if trace:` then `print(f"read {symbol} -> {state}")`. |

`main` mentions `run_nfa`, which you do not write until Part 2.  The line still works for a DFA, because Python evaluates only the branch of `run_nfa if is_nfa(machine) else run_dfa` that it takes.  When you finish this step, `simulator.py` holds these pieces, from top to bottom:

```text
import json, import sys
class MachineError        (Step 1.2)
def is_nfa                (Step 1.2)
def load_machine          (Step 1.2)
def run_dfa               (Step 1.3)
def main                  (Step 1.3)
if __name__ == "__main__" (Step 1.3, always last)
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

To design a DFA, decide what each state must remember.  For this language the question is short: how much of the suffix `ab` has the machine just seen?  The parity machine shows the method.  Each of its two states stands for one fact about the input so far ("even number of 1s" or "odd"), and each arrow says how one more symbol changes that fact.  Do the same here, with one state for each answer to "how much of `ab` have I just seen?"  Every state needs an arrow on both `a` and `b`.  The subset-construction table for the "ends in `ab`" NFA at the top of this page is one correct answer.  Try to design yours without looking, then compare.

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

Before you write any NFA code, encode an NFA whose behavior you already know, so you have something to test against.  The "ends in `ab`" NFA at the top of this page has a transition table and a worked trace of `aab`, and Step 2.3 checks your `run_nfa` against that trace.

**You write:** `machines/ends_in_ab_nfa.json`.  It is a test file, and you do not need to submit it.
**You run:** `python3 -c "import simulator; simulator.load_machine('machines/ends_in_ab_nfa.json')"`

> **Do this.**
> 1. Start from the JSON below.  The first key, `"q0,a"`, is done for you; it is the `{q0, q1}` cell in row `q0`, column `a`, of the table at the top of this page.
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

#### Before You Code: How an NFA Lives in Python

An NFA changes two things about the Python objects you used for the DFA.  Its moves are looked up by one string key instead of two nested keys, and the machine is in a *set* of states instead of one state.

*Moves, keyed by a string pair.*  You build the key from a state and a symbol with an f-string, `f"{state},{symbol}"`, so `q0` on `a` becomes the key `"q0,a"`.  The value is a list, because one label can lead to several states.  A pair with no arrow has no key at all, so you read moves with `delta.get(key, [])`.  A missing key then reads as "no moves," an empty list, and the loop that uses it simply does nothing.

*ε-moves are just another key.*  An ε-arrow from `q1` is stored under `"q1,eps"`, and you read it with `delta.get(f"{state},eps", [])`, exactly like any other move.  `eps` never goes in `alphabet`, because the alphabet lists the symbols a string can contain, and no input string ever contains an ε.

*Several states at once: a Python set.*  The active set is a Python `set`, and each property of a set matches something the NFA needs:

| The NFA needs | A Python `set` gives | In code |
|---|---|---|
| each state listed once, even if two arrows reach it | no duplicates | `{"q2", "q2"} == {"q2"}` |
| `{q0, q1}` and `{q1, q0}` to be the same set | order does not matter | `{"q1", "q0"} == {"q0", "q1"}` |
| the union of every active state's moves | `update` adds a whole list at once | `moved.update(targets)` |
| "is any accepting state active?" | fast membership | `"q2" in active` |

Watch one trap.  `{}` is an empty *dictionary*, not an empty set.  Write an empty set as `set()`.

*Why `eps_closure` returns a `frozenset`.*  A `set` can change after you build it, so Python will not let you put one inside another set or use one as a dictionary key.  A `frozenset` holds the same states and cannot change, so it can go in both places.  You need that in Part 3, where each row of the subset-construction table is a set of NFA states, and you have to ask "have I seen this set before?"  Python compares frozensets by their contents, so the order you wrote the states in never matters.

To see these pieces work on the "ends in `ab`" NFA from Step 2.1, save the lines below as `explore_nfa.py`, another scratch file you do not submit, and run `python3 explore_nfa.py`:

```python
import json

with open("machines/ends_in_ab_nfa.json") as f:
    nfa = json.load(f)
delta = nfa["delta"]

state, symbol = "q0", "a"
key = f"{state},{symbol}"
print(repr(key), "->", delta.get(key, []))      # two targets: the nondeterminism
print(repr("q1,a"), "->", delta.get("q1,a", []))  # no arrow: an empty list

active = {"q0", "q1"}        # the NFA could be in either state
moved = set()                # not {}: that is an empty dict
for state in sorted(active): # sorted only so the printout has a fixed order
    targets = delta.get(f"{state},b", [])
    print(f"  {state} on b -> {targets}")
    moved.update(targets)
print("moved:", sorted(moved))

print(type({}).__name__, type(set()).__name__)
print({"q1", "q0"} == {"q0", "q1"})
seen = {frozenset({"q0"}), frozenset({"q0", "q1"})}
print(frozenset({"q1", "q0"}) in seen)
try:
    { {"q0"} }   # a set inside a set
except TypeError as e:
    print("TypeError:", e)
```

> **You should see.**
>
> ```text
> 'q0,a' -> ['q0', 'q1']
> 'q1,a' -> []
>   q0 on b -> ['q0']
>   q1 on b -> ['q2']
> moved: ['q0', 'q2']
> dict set
> True
> True
> TypeError: unhashable type: 'set'
> ```
>
> The `moved` line is the last row of the `aab` trace at the top of this page: the set `{q0, q1}` moves on `b` to $$\{q0\} \cup \{q2\} = \{q0, q2\}$$.  Your `run_nfa` in Step 2.3 does this once per symbol.

*ε-moves, one pass at a time.*  The closure works from a to-do list called the *frontier*.  Here is the cycle machine of Step 2.2 (`q0 -ε-> q1`, `q1 -ε-> q2`, `q2 -ε-> q0`), closed by hand from `{q0}`, one pass of the loop per row:

| Pass | Take off the frontier | Its ε-targets | New ones added | `closure` after | `frontier` after |
|---|---|---|---|---|---|
| start | | | | {q0} | [q0] |
| 1 | q0 | [q1] | q1 | {q0, q1} | [q1] |
| 2 | q1 | [q2] | q2 | {q0, q1, q2} | [q2] |
| 3 | q2 | [q0] | none, since q0 is already in `closure` | {q0, q1, q2} | [] |

The frontier is empty after pass 3, so the loop stops, even though the arrows form a cycle.  Step 2.2 turns this table into code.

### Step 2.2: Implement the Epsilon-Closure

The epsilon-closure of a set of states holds every state you can reach from the set by following only `"eps"` transitions, plus the starting states themselves.  To compute it, start with the given set and follow every `"eps"` transition out of it, adding each target.  Repeat until no new state appears.  An ε-arrow may lead back to the same state or to an earlier one, and your loop must still stop.  One check handles every cycle: is this target already in the closure?  For example, if `q0 -ε-> q1`, `q1 -ε-> q2`, and `q2 -ε-> q0`, then `eps_closure(m, {"q0"}) = {"q0", "q1", "q2"}`.

**You write:** `eps_closure` in `simulator.py`, below `run_dfa` and above `main`; and a new test file, `machines/eps_cycle.json`.
**You run:** the one-line check command after the code.

> **Do this.**
> 1. Add `eps_closure(machine, states) -> frozenset` to `simulator.py` and fill in the `# TODO` lines.  It returns a `frozenset` so that a closure can sit inside another set later.
> 2. Save the three-state cycle below as `machines/eps_cycle.json`.  It is a test machine, and you do not need to submit it.
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

The loop works from a to-do list.  `frontier` holds the states whose ε-arrows you have not followed yet.  Each pass takes one state off the list, follows its ε-arrows, and puts every newly found state on the list, so that its ε-arrows get followed too.  When the list is empty, nothing new can be reached.  Fill in the two `# TODO` lines, then delete the `pass`:

| `# TODO` | How to write it |
|---|---|
| look up | `targets = machine["delta"].get(f"{state},eps", [])`.  A state with no ε-arrows gets `[]`, so the next loop simply does nothing. |
| add and push | `for target in targets:` then `if target not in closure:` then `closure.add(target)` and `frontier.append(target)`.  The `not in closure` test is the cycle check: a state you have already found is never pushed again. |

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
> - Only `['q0']`: you read `delta["q0,eps"]` once instead of following eps edges out of every newly added state.
> - A `MachineError` that mentions `eps`: your loader from Step 1.2 rejects `eps` as an unknown symbol.  Allow it for NFAs.

### Step 2.3: Implement `run_nfa`

A DFA is in one state at a time; an NFA is in a set of states.  `run_nfa` tracks that set:

1.  Start with the epsilon-closure of `{start}` as the active set.
2.  For each symbol in `s`, take the union of the `delta["state,symbol"]` lists of all active states, then take the epsilon-closure of that union.
3.  Accept if the final active set contains at least one accepting state.

Step 2 is the "move, then ε-close" rule from *One step of an NFA* at the top of this page.  Students most often get the union wrong.  On each symbol, every active state contributes the targets of its own `"state,symbol"` key, and you must collect all of them.  In code, the union is a loop that grows one set:

| Active state | Lookup | `moved` so far |
|---|---|---|
| q0 | `delta.get("q0,b", [])` gives `["q0"]` | {q0} |
| q1 | `delta.get("q1,b", [])` gives `["q2"]` | {q0, q2} |

Then `active = eps_closure(machine, moved)`.

Python's set union does this: `moved |= set(targets)`, or `moved.update(targets)`.  A state with no key adds nothing.  If no state adds anything, `moved` is empty, and it stays empty for the rest of the input.

**You write:** `run_nfa` in `simulator.py`, below `eps_closure` and above `main`.
**You run:** the `--trace` command on `machines/ends_in_ab_nfa.json`, then the two commands on `machines/eps_cycle.json`.

> **Do this.**
> 1. Add `run_nfa(machine, s, trace=False) -> bool` below `eps_closure` and fill in the `# TODO` lines.  `main` from Step 1.3 already calls `run_nfa` when `is_nfa` returns true.
> 2. With `trace` on, print the sorted active set after each symbol.  It replaces the single state that `run_dfa` prints.

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

The three `# TODO` lines replace the `pass`:

| `# TODO` | How to write it |
|---|---|
| union | Start an empty set with `moved = set()`.  Then loop `for state in active:` and call `moved.update(machine["delta"].get(f"{state},{symbol}", []))`.  This loop is the table above, one row per active state, and it is the loop you ran by hand in `explore_nfa.py`. |
| close | `active = eps_closure(machine, moved)`.  Leave this out and the `ab?` example at the top of this page rejects `a`. |
| trace | `if trace:` then `print(f"read {symbol} -> {sorted(active)}")`. |

`run_nfa` does not check for symbols outside the alphabet.  It does not need to, because no key mentions such a symbol, so `moved` comes out empty and the string is rejected.

Test it first on the "ends in `ab`" NFA from Step 2.1.  The opening of this page traces `aab` through this machine by hand, so you already know every line the program should print:

```bash
python3 simulator.py machines/ends_in_ab_nfa.json aab --trace
```

> **You should see.** The same active sets as the hand trace, in the same order:
>
> ```text
> start: ['q0']
> read a -> ['q0', 'q1']
> read a -> ['q0', 'q1']
> read b -> ['q0', 'q2']
> accept
> ```
>
> If the last set holds only one state, such as `['q2']` or `['q0']`, instead of `['q0', 'q2']`, your union kept only one active state's targets.  Create `moved` once per symbol, before the inner loop, and add to it inside the loop.

Then test it on the cycle machine from Step 2.2:

```bash
python3 simulator.py machines/eps_cycle.json ""
python3 simulator.py machines/eps_cycle.json a
```

> **You should see.** `accept`, then `reject`.  The empty string accepts because the epsilon-closure of `q0` already contains the accepting state `q2`.  The string `a` rejects because no state has an `a` move, so the active set becomes empty and stays empty.  An empty active set is a reject, never a crash.

### Step 2.4: Design the Contains-aa NFA

An NFA can guess.  Here the guess is "the `aa` starts here," and the machine keeps every guess alive at once.

> **Do this.**
> 1. Design an NFA for **Contains aa**: strings over `{a, b}` that contain the substring `aa` somewhere.
> 2. Encode it as `machines/contains_aa.json`.
> 3. Test at least four strings it accepts and four it rejects, and record them in `writeup.md`.
> 4. Include the `--trace` output for at least one accepted string, so the writeup shows the execution path.

Worked example: `"baaab"` -> accept; `"ababab"` -> reject.  Hint: let the machine guess where `aa` occurs.  The "ends in `ab`" NFA at the top of this page shows the pattern.  Its start state loops on every symbol while the machine has not yet guessed, and a chain of states spells out the pattern.  Here `aa` may appear anywhere, not only at the end, so your accepting state must also loop on every symbol once the pattern has appeared.  Your design must use nondeterminism; a DFA in disguise does not count.

**You write:** `machines/contains_aa.json`, plus a heading for this machine in `writeup.md` with your test strings and one `--trace` output.  No Python changes; `simulator.py` already runs any NFA.
**You run:** the two commands below, then your own eight test strings.

You can start from this skeleton.  Three states are enough: one that has not yet guessed, one that has just read the first `a` of the guessed `aa`, and one that has seen `aa`.  Replace each `["TODO"]` with the list of target states for that key, and add or remove keys as your design needs.  Your loader reports any `"TODO"` you forget, because it is not a declared state:

```json
{
  "states": ["q0", "q1", "q2"],
  "alphabet": ["a", "b"],
  "start": "q0",
  "accept": ["q2"],
  "delta": {
    "q0,a": ["TODO"],
    "q0,b": ["TODO"],
    "q1,a": ["TODO"],
    "q2,a": ["TODO"],
    "q2,b": ["TODO"]
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

## Part 3: By-Hand Constructions

Part 3 is paper work for your writeup, with no code.  You trace each algorithm once on a small example, by hand, so you know what lexer-generator tools do for you.

### Step 3.1: Trace the Subset Construction

**You write (in `writeup.md` under a `## Part 3.1: Subset Construction` heading):** the filled-in table below and the number of DFA states.
**You run:** `python3 simulator.py machines/contains_aa.json <string> --trace` on a few strings, to check your table (see the Checkpoint below).

> **Do this.**
> 1. Apply the subset construction to your Contains aa NFA from Part 2 to produce an equivalent DFA.
> 2. Fill in the construction table below in `writeup.md`, one row per powerset state.
> 3. Record how many DFA states result.

The algorithm, from *The subset construction* at the top of this page:

1.  Start with `eps_closure({start})` as the first powerset state.
2.  For each powerset state you have not yet processed, compute its transition on each symbol.  Take the union of the targets of every NFA state in the set on that symbol, then epsilon-close the union.  A result you have not seen before is a new row.
3.  Mark a powerset state as accepting if it contains any NFA accept state.
4.  Continue until you have processed every powerset state.

*What each cell means.*  The cell in row $$S$$, column `a`, answers one question: if the NFA could be in any state of $$S$$, where could it be after reading one `a`?  Fill it in with three moves, and show them in your writeup the way the worked examples at the top of this page do:

| Move | Work for row {q0, q1}, column `a` | Purpose |
|---|---|---|
| list | q0 → {q0, q1}; q1 → ∅ | look up each state on `a` |
| union | {q0, q1} ∪ ∅ = {q0, q1} | collect every target |
| close | E({q0, q1}) = {q0, q1} | follow ε-moves (this NFA has none) |

Then check whether the result already has a row.  Compare sets by their contents, not by the order you wrote them: `{q1, q0}` and `{q0, q1}` are the same row.  Once you have written a row's set, give it a short name (A, B, C, ...).  If a cell comes out as ∅, add a dead-state row for ∅, as in the `ab?` example.  For Contains aa, watch what happens after the machine has seen `aa`.  The sets that contain your accepting state may keep growing for a few rows before they settle.

> **Paste into your submission.** Copy this table into `writeup.md` and fill it in.

| Powerset State | on `a` | on `b` | Accepting? |
|----------------|--------|--------|------------|
| {q0} | ... | ... | No/Yes |
| ... | | | |

> **Checkpoint.** Your simulator can check your table.  Run `python3 simulator.py machines/contains_aa.json <string> --trace` on a few strings.  Every set the trace prints should be one of your powerset states, and the steps between them should match your `on a` and `on b` columns.

> **A second check, after you finish the table.**  [Automata Studio](https://reyescarlata0.github.io/automata-studio/) runs the subset construction on an NFA you enter and prints the full subset table, so you can compare it with yours row by row.  Build your table by hand first.  The rubric grades the trace you wrote, not one a tool printed.

### Step 3.2: Trace Thompson's Construction

**You write (in `writeup.md` under a `## Part 3.2: Thompson's Construction` heading):** five labeled fragments, one per sub-expression, ending with the finished NFA.  A step table like the worked examples' tables is enough; a drawing of the final NFA is welcome but not required.  No code.

Thompson's construction turns a regular expression into an NFA one operator at a time, joining small fragments with ε-transitions.  Read the fragment pictures and the worked `(x|y)z` example under *Thompson's construction* at the top of this page first.  This step adds a star to the same procedure.  Work from the inside of the expression outward.  The innermost pieces are single symbols, and each operator wraps or joins fragments you have already built.  Number the states in the order you create them, and keep the numbers when you reuse a fragment.  A reader can then find every earlier fragment inside the final machine.

> **Do this.**
> 1. Apply Thompson's construction to the regular expression `a(b|c)*` in `writeup.md`.
> 2. Show each sub-expression and its fragment, and label every state and every ε-transition, in this order:
>    1. Fragment for `a`.
>    2. Fragments for `b` and `c`.
>    3. Fragment for `b|c` (union).
>    4. Fragment for `(b|c)*` (Kleene star).
>    5. Concatenation: `a` then `(b|c)*`.

For reference, here are the fragment rules:

- A single character: a start state and an accept state joined by one transition labeled with that character.
- Concatenation of A then B: connect A's accept to B's start with ε.
- Union of A and B: add a new start with ε to both fragments' starts, and ε from both accepts to a new shared accept.
- Kleene star of A: add a new start with ε to A's start and to a new accept.  Add ε from A's accept back to A's start, and from A's accept to the new accept.

### Step 3.3: Connect the Simulators to Your Lexer

**You write (in `writeup.md` under a `## Part 3.3: Lexer Connection` heading):** one paragraph.  No code.

> **Do this.**
> 1. Write one paragraph in `writeup.md` that connects these simulators to the lexer you build next.  Which component of the lexer plays the role of your simulators?

A lexer, or scanner, reads source code one character at a time and groups the characters into tokens such as identifiers, numbers, and operators.  A regular expression describes each token class, like the identifier regex in Step 0.1.  In your paragraph, place each piece of this lab in that pipeline.  Start with the regex for each token.  Thompson's construction builds an NFA from it, and the subset construction builds a DFA from that NFA.  Last comes the loop that feeds characters through a machine and checks for acceptance.

---

## Deliverables

Submit a ZIP that contains the files below.  List your Python version in the writeup so I can reproduce your results.

| File or artifact | What it shows | Rubric row |
|------------------|---------------|------------|
| `dfa_core.py` | the ten-line DFA runner from Step 1.1, unchanged after that step | Part 1 |
| `simulator.py` | `load_machine`, `run_dfa`, `eps_closure`, `run_nfa`, and the command-line entry point | Parts 1 and 2 |
| `machines/even_ones.json` | the provided parity machine, unchanged | Part 1 |
| `machines/ends_in_ab.json` | your designed DFA | Part 1 |
| `machines/contains_aa.json` | your designed NFA | Part 2 |
| `writeup.md` | Part 0 paper work; state annotations and test strings for both designed machines; the subset-construction table with the DFA state count; the Thompson's construction fragments; the paragraph connecting these simulators to the lexer you will build next (which component of the lexer plays the role of your simulators?); your name (and your partner's, if you worked in a pair) | Parts 0, 1, 2, 3 |

---

## Self-Check Before You Submit

- [ ] `python3 dfa_core.py 0110` prints `accept`, and `python3 dfa_core.py 100` prints `reject`.
- [ ] `python3 simulator.py machines/even_ones.json 0110` prints `accept`, and the same command with `100` prints `reject`.
- [ ] The empty string and an out-of-alphabet symbol each produce a deliberate answer, not a traceback.
- [ ] `--trace` prints a state (DFA) or a sorted set of states (NFA) after every symbol.
- [ ] `load_machine` on `machines/broken.json` raises one `MachineError` that lists all three problems.
- [ ] `eps_closure` stops on `machines/eps_cycle.json` and returns all three states.
- [ ] `python3 simulator.py machines/ends_in_ab_nfa.json aab --trace` prints the same active sets as the hand trace at the top of this page.
- [ ] Each state of the Ends-in-ab DFA has a one-sentence annotation, and both designed machines have at least four accepted and four rejected test strings recorded.
- [ ] The Contains-aa NFA has at least one state with two or more targets on the same symbol.
- [ ] `writeup.md` has the Part 0 work, the subset-construction table with the DFA state count, every Thompson fragment labeled, the lexer paragraph, both names, and your Python version.

---

## Reflection Prompts

- You designed the NFA and then traced its equivalent DFA with the subset construction.  Compare the two tasks: where did the complexity move?
- Your simulators treat machines as data loaded from JSON.  Name one way this helped your testing that hard-coded machines would not have.
- If you worked in a pair, who did what?  Name one thing your partner caught that you would have missed.  If you worked alone, say so.
