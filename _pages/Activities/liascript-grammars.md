<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374-Fall2026/gh-pages/_pages/Activities/liascript-grammars.md or locally via https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374-Fall2026/gh-pages/_pages/Activities/liascript-grammars.md

import: https://raw.githubusercontent.com/liascript/CodeRunner/master/README.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

# Grammars and the Chomsky Hierarchy

## Learning Goals

By the end of this activity, you will be able to:

- Classify a grammar into its Chomsky hierarchy level (Type 0-3) by examining the shape of its productions and identifying the corresponding recognizing machine
- Explain why programming language lexers use regular (Type 3) grammars and parsers use context-free (Type 2) grammars, citing the limitations of each class
- Construct a context-free grammar for a given language and produce a derivation sequence for a specific target string
- Demonstrate why certain languages (such as $a^n b^n c^n$) require a more powerful grammar class than context-free, by identifying what information no pushdown automaton can track
- Represent a grammar as a data structure and search it mechanically, so that "derivable from $S$" becomes something you can test rather than something you assert

> **Before You Begin, Prerequisite Check**
>
> This activity assumes you are comfortable with BNF syntax from the *Syntax and BNF/EBNF* activity: you can read a rule like `expr ::= expr "+" term | term`, you know what "nonterminal" and "terminal" mean, and you have seen at least one derivation step.  If any of those concepts are fuzzy, re-read your notes from that activity before proceeding.

---

A grammar is a **recipe for generating every valid sentence of a language**.  Rules like

```
E -> E + T | T
```

describe all legal arithmetic expressions, not by listing them (there are infinitely many), but by giving a finite set of rewriting instructions.  Your parser will be the mirror image: given a sentence like `3 + 4 * 5`, it traces backward through those same rules to reconstruct which recipe steps produced it.

Every parser you have ever met, from the Python interpreter that runs your code, to the browser that renders this page, to the parser you will write in a few weeks, is powered by a grammar exactly like the ones in this activity.  Understanding grammars is not an academic exercise; it is the technical foundation for recursive descent, LL(1) tables, operator precedence, and abstract syntax trees.

This two-day module puts BNF in its theoretical home.  Grammars come in **classes of power**, and the class a language needs determines the machine that can recognize it.  That is why your project has *both* a lexer, which is regular machinery, and a parser, which is context-free machinery.  Today: **formal grammars $\rightarrow$ the four-level hierarchy $\rightarrow$ what a stack buys you $\rightarrow$ where programming language constructs live**.

---

## Directions and Group Roles

Work in your POGIL team with your rotated roles (**Manager**, **Recorder**, **Presenter**, **Reflector**).  Derive on paper first, every time, and only then run the code to check yourself.  The by-hand pass is where the understanding forms; the machine is the referee.  The Recorder posts your answers to the Class Activity Questions discussion board, and the Presenter reports out wherever your team disagreed or found another approach.

---

# Part I: The Hierarchy

## 1.  Theory: Grammars, Formally

**A grammar is a four-tuple** $G = (N, \Sigma, P, S)$: nonterminals $N$, terminal alphabet $\Sigma$, productions $P$, and start symbol $S \in N$.  The **language** $L(G)$ is the set of terminal strings derivable from $S$.  Chomsky classified grammars by the *shape* their productions may take, and each restriction trades expressive power for recognition efficiency:

| Type | Name | Production shape | Recognizing machine | Example language | PL relevance |
|------|------|------------------|---------------------|-----------------|--------------|
| 3 | Regular | $A \rightarrow aB$ or $A \rightarrow a$ | Finite automaton (DFA/NFA) | All identifiers matching `[a-z][a-z0-9]*` | Lexer tokens |
| 2 | Context-free | $A \rightarrow \gamma$ (single nonterminal on the left) | Pushdown automaton (stack) | $\{a^n b^n \mid n \ge 1\}$, nested parens | Parser / syntax rules |
| 1 | Context-sensitive | $\alpha A \beta \rightarrow \alpha \gamma \beta$ (context preserved) | Linear-bounded automaton | $\{a^n b^n c^n \mid n \ge 1\}$ | Rarely used directly |
| 0 | Unrestricted | $\alpha \rightarrow \beta$ | Turing machine | Any recursively enumerable set | Semantic analysis |

Each class strictly contains the ones below it.  The engineering meaning: **the weaker the grammar class, the faster and simpler the recognizer**, so implementers always reach for the weakest class that suffices.

## Examples: Three Telltale Languages, Derived by Hand

Three languages over $\{a, b, c\}$ separate the classes cleanly:

- $L_1 = \{ a^n \mid n \ge 1 \}$: one or more a's.
- $L_2 = \{ a^n b^n \mid n \ge 1 \}$: a's followed by the *same number* of b's.
- $L_3 = \{ a^n b^n c^n \mid n \ge 1 \}$: equal counts of all three.

**Deriving `aaabbb` from the Type 2 grammar $S \rightarrow aSb \mid ab$.**

Every step replaces the *only* nonterminal $S$ with one of its two right-hand sides.  Choosing `aSb` adds one `a` on the left and one `b` on the right, keeping $S$ alive in the middle.  Choosing `ab` cashes out with the innermost pair.

```
S
  => a S b           (used S -> aSb)
  => a a S b b       (used S -> aSb again)
  => a a a b b b     (used S -> ab, the base case)
```

The memory that keeps the `a` count equal to the `b` count is the **nesting depth of the recursion**: the call stack, once you implement this as a recursive descent parser.

**Why `aab` is rejected.**

```
S => aSb => aaSbb    (now need two more characters to close)
  => aaabb           -- 5 characters, not 3
OR
S => ab              -- 2 characters only
```

There is no way to produce exactly two `a`s and one `b` under this grammar.  Every application of `aSb` adds one of each; the base case adds one of each.  The counts can never diverge.

**Now try $L_3$ yourself, on paper, before reading further.**  Take the $L_2$ grammar and try to bolt a `c` onto it.  Write down whatever you come up with, and derive `abc`, then `aabbcc`, then `aaabbbccc`.  Mark the exact point where it breaks.  That failure is the lesson.

### Critical Thinking Questions

> **CTQ 1.1** Write a Type 3 (regular) grammar for $L_1 = \{a^n \mid n \ge 1\}$.
>
> - **Step 1:** What are the only terminals you need?
> - **Step 2:** Write one rule that generates a single `a` (the base case) and one rule that generates `a` and then recurses.
> - **Step 3:** Why can you not use this same trick to count that the number of `a`s equals the number of `b`s?

> **CTQ 1.2** Using the $L_2$ grammar $S \rightarrow aSb \mid ab$:
>
> - **Step 1:** Apply exactly one production to $S$ to get a sentential form.  Which rule did you choose?  Write the result.
> - **Step 2:** Apply one more production.  Write the new sentential form.
> - **Step 3:** Continue until you reach the terminal string `aabb`.  How many total steps did it take?
> - **Step 4:** Where is the memory that guarantees the `a` count equals the `b` count?  Is it in the grammar rules themselves, or does it emerge from the derivation?

> **CTQ 1.3** $L_3 = \{a^n b^n c^n \mid n \ge 1\}$ is not context-free.  Report on the attempt you made above:
>
> - **Step 1:** Write the grammar you came up with.
> - **Step 2:** Does it derive `abc` and `aabbcc` correctly?
> - **Step 3:** Where does `aaabbbccc` produce the wrong counts or get stuck?
> - **Step 4:** In one sentence: what kind of memory would you need that a single stack cannot provide?

> **CTQ 1.4** Map to your project: matching nested parentheses in expressions is which of $L_1$, $L_2$, $L_3$ in disguise?  What does that tell you about whether your *lexer* or your *parser* must handle it, and why?

## Model 1: A Grammar as Data, Derivations as Search

A grammar is a finite set of rewriting rules, which means it is a data structure, which means you can search it.  This model turns "derivable from $S$" from a claim into a test: it stores the productions in a dictionary and does a breadth-first search over sentential forms.

This is *not* how real parsers work (that is several weeks away), and it is hopelessly slow for anything but toy inputs.  What it buys you is that every derivation you did by hand above can now be checked mechanically.

```python
from collections import deque

# A grammar is a dict: nonterminal -> list of alternatives.
# Each alternative is a string of symbols. Uppercase = nonterminal,
# lowercase = terminal, "" = epsilon.

L2 = {"S": ["aSb", "ab"]}                # { a^n b^n | n >= 1 }
L1 = {"S": ["aS",  "a"]}                 # { a^n     | n >= 1 }

NONTERMINALS = set("ABCDEFGHIJKLMNOPQRSTUVWXYZ")

def is_terminal_string(form):
    return all(sym not in NONTERMINALS for sym in form)

def expand_once(form, grammar):
    """Every sentential form reachable by rewriting ONE nonterminal."""
    out = []
    for i, sym in enumerate(form):
        if sym in NONTERMINALS:
            for alt in grammar.get(sym, []):
                out.append(form[:i] + alt + form[i+1:])
    return out

def derive(target, grammar, start="S", max_len=None, show=False):
    """BFS over sentential forms. Returns the derivation, or None."""
    limit = max_len if max_len is not None else len(target)
    seen  = {start}
    queue = deque([(start, [start])])
    while queue:
        form, path = queue.popleft()
        if form == target:
            return path
        for nxt in expand_once(form, grammar):
            # Prune: a form already longer than the target can never shrink
            # here, because no production of these grammars deletes symbols.
            if len(nxt) > limit or nxt in seen:
                continue
            seen.add(nxt)
            queue.append((nxt, path + [nxt]))
    return None

def report(target, grammar, name):
    path = derive(target, grammar)
    if path is None:
        print(f"  {name}: {target!r:12} NOT derivable")
        return
    print(f"  {name}: {target!r:12} derivable in {len(path)-1} step(s)")
    for i, form in enumerate(path):
        arrow = "   " if i == 0 else "=> "
        print(f"        {arrow}{form}")

print("=== L2 grammar:  S -> aSb | ab ===")
for s in ["ab", "aabb", "aaabbb"]:
    report(s, L2, "L2")

print("\n=== The same grammar, on strings that are NOT in L2 ===")
for s in ["aab", "abb", "ba", "aaabbbb"]:
    report(s, L2, "L2")

print("\n=== L1 grammar:  S -> aS | a  (regular) ===")
for s in ["a", "aaa", "aab"]:
    report(s, L1, "L1")
```
@LIA.eval(`["main.py"]`, `none`, `python3 main.py`)

### Reading the Code

- `L2 = {"S": ["aSb", "ab"]}` is the grammar $S \rightarrow aSb \mid ab$ written as data.  The dictionary key is the left-hand side; the list is the alternatives.
- `expand_once` is one derivation step, done every possible way at once.  It walks the sentential form looking for a nonterminal, and for each one it finds, substitutes each alternative in turn.  Your hand derivations picked *one* of these; the search tries all of them.
- The `len(nxt) > limit` prune is what makes this terminate.  Neither of these grammars has a production that shortens a form, so once a sentential form is longer than the target it is a dead end forever.
- `derive` returns the whole `path`, which is exactly the `S => aSb => aaSbb => ...` chain you wrote by hand.  Compare the printed derivation for `aaabbb` against yours.

> **Watch out!**  This BFS says "not derivable" by *exhausting the search space*, which works only because the prune bounds it.  Add a production like $S \rightarrow \varepsilon$ that shortens forms, or a rule with a nonterminal that can grow without bound, and the same code can run forever.  Deciding membership in general is much harder than this model suggests; that is what the parsing unit is about.

### Critical Thinking Questions

> **CTQ 1.5** Run `report("aabb", L2, "L2")` in your head first: how many steps should it take?  Now check against the output.  Did the machine take the same route you did, or a different one that arrives at the same string?

> **CTQ 1.6** The prune assumes no production shrinks a sentential form.  Write a two-rule grammar for which that assumption is false, and say what `derive` would do with it.

> **CTQ 1.7** `expand_once` rewrites *every* nonterminal position, not just the leftmost.  When you derived by hand, you always rewrote the only $S$ there was.  For a grammar with two nonterminals in a form, does the choice of which to rewrite change the final string?  Does it change the derivation?

### Try It Yourself

Encode your CTQ 1.1 answer as data and test it, then try to encode $L_3$ and watch it fail.

```python
from collections import deque
NONTERMINALS = set("ABCDEFGHIJKLMNOPQRSTUVWXYZ")

def expand_once(form, grammar):
    out = []
    for i, sym in enumerate(form):
        if sym in NONTERMINALS:
            for alt in grammar.get(sym, []):
                out.append(form[:i] + alt + form[i+1:])
    return out

def derive(target, grammar, start="S"):
    seen, queue = {start}, deque([start])
    while queue:
        form = queue.popleft()
        if form == target:
            return True
        for nxt in expand_once(form, grammar):
            if len(nxt) <= len(target) and nxt not in seen:
                seen.add(nxt); queue.append(nxt)
    return False

# TODO 1: write your CTQ 1.1 regular grammar for { a^n | n >= 1 } here.
MY_L1 = {"S": []}

# TODO 2: write your best attempt at a grammar for { a^n b^n c^n | n >= 1 }.
#         You will not succeed with a context-free grammar. Find out WHERE.
MY_L3 = {"S": []}

print("=== My L1 grammar ===")
for s in ["a", "aa", "aaaa", "ab"]:
    print(f"  {s!r:8} -> {derive(s, MY_L1)}")

print("\n=== My L3 attempt ===")
for s in ["abc", "aabbcc", "aaabbbccc", "aabbc", "abbc"]:
    print(f"  {s!r:12} -> {derive(s, MY_L3)}")

print("\nA correct L3 grammar accepts the first three and rejects the last two.")
print("If yours accepts aabbc or abbc, that is the leak. Where does it come from?")
```
@LIA.eval(`["main.py"]`, `none`, `python3 main.py`)

Expected output for a correct `MY_L1`: `a`, `aa`, and `aaaa` derivable; `ab` not.  For `MY_L3`: no context-free grammar gets all five right, and finding out *which* one leaks is the point of the exercise.

---

# Part II: What a Stack Buys You

## 2.  Theory: Counting Is the Dividing Line

The jump from Type 3 to Type 2 has a concrete mechanical meaning: **a finite automaton has a fixed, finite memory, and a pushdown automaton has an unbounded stack.**

A finite automaton is exactly a fixed set of states with no auxiliary storage.  To recognize $a^n b^n$ it would have to remember how many `a`s it has seen so it can demand the same number of `b`s, and $n$ is unbounded, so no fixed number of states suffices.  Push one symbol per `a`, pop one per `b`, and the problem evaporates: that is the stack, and that is Type 2.

Push the same argument one level up.  To recognize $a^n b^n c^n$ you must count the `a`s twice: once against the `b`s and once against the `c`s.  A single stack is destroyed by the first comparison, so by the time the `c`s arrive the count is gone.  That is the Type 1 boundary, and it is why "every variable must be declared before use" is not a syntax rule in any real compiler; it lives in a separate **semantic analysis** pass over the tree.

Tokens are regular; structure is context-free; meaning is neither.  The pipeline of your project is the hierarchy made architecture.

## Examples: Counting by Hand

Trace both machines on `aabb` before running anything.  For the finite-state attempt, the only memory is the state name, so write down what each state would have to mean:

| Input read | Finite automaton must remember | Stack machine's stack |
|------------|-------------------------------|----------------------|
| (start)    | "zero a's so far"             | (empty)              |
| `a`        | "one a so far"                | `a`                  |
| `aa`       | "two a's so far"              | `aa`                 |
| `aab`      | "two a's, one b"              | `a`                  |
| `aabb`     | "two a's, two b's: accept"    | (empty: accept)      |

The right column is bounded by nothing but the input.  The middle column needs a *distinct state* for every count, so for arbitrary $n$ it needs infinitely many states, and a finite automaton has finitely many by definition.  That is the whole proof, informally.

## Model 2: The Same Language, Two Machines

Watch a fixed-state recognizer fail on exactly the input where counting matters, and a stack machine succeed on the same input.

```python
# Two recognizers for { a^n b^n | n >= 1 }.
# One has a fixed, finite memory. One has a stack.

MAX_STATES = 3   # our finite machine can only count this high

def finite_state_recognizer(s):
    """A DFA-like machine with a FIXED number of states.
    It can count a's only up to MAX_STATES, because a state IS the count."""
    count = 0
    i = 0
    while i < len(s) and s[i] == "a":
        count += 1
        if count > MAX_STATES:
            return False, f"ran out of states after {MAX_STATES} a's"
        i += 1
    seen_b = 0
    while i < len(s) and s[i] == "b":
        seen_b += 1
        i += 1
    if i != len(s):
        return False, "unexpected symbol"
    return (count == seen_b and count > 0), f"counted {count} a's, {seen_b} b's"

def stack_recognizer(s, show=False):
    """A pushdown machine: push on a, pop on b. Memory is unbounded."""
    stack = []
    trace = []
    phase = "a"
    for ch in s:
        if ch == "a":
            if phase == "b":
                return False, "an 'a' after a 'b'"
            stack.append("a")
        elif ch == "b":
            phase = "b"
            if not stack:
                return False, "a 'b' with nothing to match"
            stack.pop()
        else:
            return False, f"unexpected symbol {ch!r}"
        trace.append("".join(stack) or "(empty)")
    if show:
        print(f"        stack after each symbol: {' | '.join(trace)}")
    return (phase == "b" and not stack), f"stack ended {'empty' if not stack else 'non-empty'}"

tests = ["ab", "aabb", "aaabbb", "aaaabbbb", "aab", "abb", "ba"]

print("=== Finite memory (only 3 states of counting) ===")
for s in tests:
    ok, why = finite_state_recognizer(s)
    print(f"  {s!r:12} {'accept' if ok else 'REJECT':6}  ({why})")

print("\n=== Unbounded stack ===")
for s in tests:
    ok, why = stack_recognizer(s)
    print(f"  {s!r:12} {'accept' if ok else 'REJECT':6}  ({why})")

print("\n=== Watch the stack do the counting on aaaabbbb ===")
stack_recognizer("aaaabbbb", show=True)

print("\nNotice WHERE they diverge: 'aaaabbbb' is a perfectly good member of")
print("the language, and the finite machine rejects it only because it ran")
print("out of states. Raise MAX_STATES to 4 and it works... until n = 5.")
print("No FIXED number of states works for ALL n. That is the Type 3 ceiling.")
```
@LIA.eval(`["main.py"]`, `none`, `python3 main.py`)

### Reading the Code

- `MAX_STATES = 3` is the honest part of the simulation.  A real DFA does not have a `count` variable; its state *is* the count, so a machine with three counting states can distinguish "seen one a," "seen two a's," and "seen three a's" and nothing beyond.
- `finite_state_recognizer` returns `False` on `aaaabbbb` with the reason "ran out of states."  That string is *in* the language.  The machine is not wrong about the string; it is too small to hold the question.
- `stack_recognizer` never counts anything.  It pushes and pops, and the emptiness of the stack at the end is the answer.  Nothing else is going on, which is why the $L_2$ grammar's recursion depth was the memory in Part I.
- The `phase` variable enforces that all `a`s precede all `b`s.  Without it, `abab` would be accepted, since the pushes and pops balance.

> **Watch out!**  It is tempting to say "just use a counter instead of states."  A counter that can hold arbitrary $n$ *is* unbounded memory, which is precisely what a finite automaton is defined not to have.  The moment you allow one, you have left Type 3.  The restriction is the definition, not an oversight.

### Critical Thinking Questions

> **CTQ 2.1** Raise `MAX_STATES` to 4 and rerun.  Which test now passes that did not before?  Which one still fails, and what would you have to do to fix *that* one?  Where does this argument end?

> **CTQ 2.2** `stack_recognizer` rejects `abb` with "a 'b' with nothing to match."  Which of the two failure modes is that: a string outside the language, or a machine too weak for the string?  How can you tell the difference in general?

> **CTQ 2.3** Remove the `phase` check and predict what `"abab"` does.  Then explain why balanced pushes and pops are necessary but not sufficient for this language.

> **CTQ 2.4** A language requires that every `begin` token be matched by a later `end`, with arbitrary nesting.  Which recognizer above is the right shape for it, and which stage of your project pipeline does that put it in?

### Try It Yourself

Extend the stack machine to $a^n b^n c^n$ and find out exactly where a single stack runs out.

```python
def stack_recognizer_abc(s):
    """Try to recognize { a^n b^n c^n } with ONE stack.
    Push on 'a', pop on 'b'. Then... what do you have left for 'c'?"""
    stack, phase = [], "a"
    for ch in s:
        if ch == "a":
            if phase != "a": return False, "'a' out of order"
            stack.append("a")
        elif ch == "b":
            phase = "b"
            if not stack: return False, "'b' with nothing to match"
            stack.pop()
        elif ch == "c":
            phase = "c"
            # TODO: what do you pop here? The stack was emptied by the b's.
            #       Try whatever you like. Then explain why it cannot work.
            pass
        else:
            return False, f"unexpected {ch!r}"
    return (phase == "c" and not stack), "reached the end"

for s in ["abc", "aabbcc", "aaabbbccc", "aabbc", "abcc", "aabbccc"]:
    ok, why = stack_recognizer_abc(s)
    print(f"  {s!r:12} {'accept' if ok else 'REJECT':6}  ({why})")

print("\nThe last three are NOT in the language. Does your version reject them?")
print("If it accepts any of them, say exactly which information was already")
print("gone by the time the first 'c' arrived.")
```
@LIA.eval(`["main.py"]`, `none`, `python3 main.py`)

Expected output: the first three should accept and the last three should reject, and you will not manage it with one stack.  Write down the sentence that explains why; that sentence is CTQ 1.3's answer.

---

# Check Your Understanding

A language requires that every `begin` token be matched by a later `end`, with arbitrary nesting.  The weakest grammar class that can express this requirement is:

[( )] Regular, because keywords are tokens
[(X)] Context-free, because matched nesting requires a stack's worth of memory
[( )] Context-sensitive, because two different keywords are involved
[( )] Unrestricted, because programs can be arbitrarily long

---

In Model 2, the finite-state machine rejects `aaaabbbb`.  What does that rejection tell you?

[( )] `aaaabbbb` is not in the language $a^n b^n$
[(X)] The machine has too little memory for that input; the string is perfectly legal
[( )] The stack machine must also reject it, for consistency
[( )] The grammar $S \rightarrow aSb \mid ab$ is ambiguous

---

Why do real compilers enforce "every variable must be declared before use" outside the grammar?

[(X)] The rule is not context-free, so no parser generator can express it; it goes in semantic analysis
[( )] It would make the grammar ambiguous
[( )] Parsers run before the lexer, so names are not available yet
[( )] It is a stylistic convention rather than a rule

---

In Model 1, the BFS is guaranteed to terminate because:

[(X)] No production of these grammars shortens a sentential form, so forms longer than the target are dead ends
[( )] Breadth-first search always terminates
[( )] The grammar has only one nonterminal
[( )] Python's `deque` has a maximum size

---

# Exercises

**Exercise 1.**  Write a context-free grammar for balanced parentheses over `(` and `)`, including the empty string.  Encode it in Model 1's dictionary format and confirm that it derives `(())()` and rejects `(()`.  You will need to remove or relax the length prune; say why.

**Exercise 2.**  The grammar $S \rightarrow aSb \mid ab$ generates $a^n b^n$ for $n \ge 1$.  Modify it to allow $n = 0$ as well, and derive the empty string.  What does this change do to Model 1's `derive`, and why?

**Exercise 3.**  Write a regular grammar for identifiers matching `[a-z][a-z0-9]*` in the Type 3 shape ($A \rightarrow aB$ or $A \rightarrow a$).  Then argue in two sentences why a regular grammar suffices here and a context-free one is unnecessary.

**Exercise 4.**  For your team's project language, list three constructs and classify each as regular, context-free, or neither.  For the "neither" one, say which pass of your implementation will enforce it.

**Exercise 5.**  Instrument Model 1's `derive` to count how many sentential forms it explores before finding `aaaabbbb`.  Then try `aaaaabbbbb`.  Plot or tabulate the growth and explain, in one sentence, why nobody parses this way.

---

# Reflection

In your notebook: the whole hierarchy comes down to how much a machine is allowed to remember.  Finite states remember a fixed amount; a stack remembers an unbounded amount but only in last-in-first-out order; a tape remembers everything.

Where else have you run into a problem that was easy the moment you were allowed to keep a little more state around, and impossible before that?  Write a paragraph.  Then say which of the two recognizers in Model 2 you would have written if nobody had told you about the hierarchy first, and what that says about the value of knowing the boundary before you start coding.

---

# Further Reading

- Allison, Chapter 9 §9.3, on the Chomsky hierarchy.
- Allison, Chapter 6 §6.1, on context-free grammars and derivations.
- Hopcroft, Motwani, and Ullman.  *Introduction to Automata Theory, Languages, and Computation*: the standard treatment, with the pumping lemma proofs that make Part II's informal argument rigorous.

---

> **Continued next session.**  Day 2 picks up from here and turns these ideas into grammars you write yourself: [Grammars, Day 2: Writing Context-Free Grammars](https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374-Fall2026/gh-pages/_pages/Activities/liascript-grammars-day2.md).
