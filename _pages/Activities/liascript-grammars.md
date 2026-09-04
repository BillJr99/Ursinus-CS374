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

- Classify a grammar into its Chomsky hierarchy level (Type 0 through Type 3) by looking at the shape of its productions, and name the machine that recognizes that level
- Explain why a programming language lexer uses a regular (Type 3) grammar and a parser uses a context-free (Type 2) grammar, and state what each class cannot do
- Write a context-free grammar for a given language and produce a derivation for a specific target string
- Show why some languages (such as $a^n b^n c^n$) need a grammar class more powerful than context-free, by naming the information that no pushdown automaton can keep
- Store a grammar as a data structure and search it by machine, so that "derivable from $S$" becomes a test you can run rather than a claim you make

> **Before You Begin: Prerequisite Check**
>
> This activity assumes you are comfortable with Backus-Naur Form (BNF) from the *Syntax and BNF/EBNF* activity.  You can read a rule like `expr ::= expr "+" term | term`, you know what "nonterminal" and "terminal" mean, and you have seen at least one derivation step.  If any of those ideas are fuzzy, re-read your notes from that activity before you continue.

---

A grammar is a finite set of rewriting rules that generates every valid sentence of a language.  The rule

```
E -> E + T | T
```

describes every legal arithmetic expression.  It cannot list them, because there are infinitely many.  Instead it gives a finite set of instructions for building them.  Your parser works in the opposite direction.  Given a sentence like `3 + 4 * 5`, it traces back through the same rules to find which steps produced that sentence.

Every parser you use runs on a grammar like the ones in this activity: the Python interpreter that runs your code, the browser that renders this page, and the parser you will write in a few weeks.  Grammars are the technical foundation for recursive descent, LL(1) parsing tables, operator precedence, and abstract syntax trees.

This two-day module puts BNF in its theoretical home.  Grammars come in classes of increasing power, and the class a language needs decides which machine can recognize it.  That is why your project has both a lexer (regular machinery) and a parser (context-free machinery).  Today covers four topics in order: formal grammars, the four-level hierarchy, what a stack buys you, and where programming language constructs live in the hierarchy.

---

## Directions and Group Roles

Work in your POGIL (Process Oriented Guided Inquiry Learning) team with your rotated roles: Manager, Recorder, Presenter, and Reflector.  Derive on paper first, every time.  Run the code only after that, to check yourself.  The by-hand pass is where the understanding forms; the machine is the referee.  The Recorder posts your answers to the Class Activity Questions discussion board.  The Presenter reports out wherever your team disagreed or found another approach.

---

# Part I: The Hierarchy

## 1.  Theory: Grammars, Formally

A grammar has four parts, written $G = (N, \Sigma, P, S)$.  $N$ is the set of nonterminals, the symbols you can still rewrite.  $\Sigma$ is the terminal alphabet, the symbols that appear in finished sentences.  $P$ is the set of productions, the rewriting rules.  $S \in N$ is the start symbol.  The language $L(G)$ is the set of terminal strings you can derive from $S$.

Chomsky sorted grammars into four types by the shape their productions may take.  This ordering is the Chomsky hierarchy.  Each restriction on production shape trades expressive power for a faster and simpler recognizer:

| Type | Name | Production shape | Recognizing machine | Example language | PL relevance |
|------|------|------------------|---------------------|-----------------|--------------|
| 3 | Regular | $A \rightarrow aB$ or $A \rightarrow a$ | Finite automaton (DFA/NFA) | All identifiers matching `[a-z][a-z0-9]*` | Lexer tokens |
| 2 | Context-free | $A \rightarrow \gamma$ (single nonterminal on the left) | Pushdown automaton (stack) | $\{a^n b^n \mid n \ge 1\}$, nested parens | Parser / syntax rules |
| 1 | Context-sensitive | $\alpha A \beta \rightarrow \alpha \gamma \beta$ (context preserved) | Linear-bounded automaton | $\{a^n b^n c^n \mid n \ge 1\}$ | Rarely used directly |
| 0 | Unrestricted | $\alpha \rightarrow \beta$ | Turing machine | Any recursively enumerable set | Semantic analysis |

Here is what each row means, starting from the most restricted type.

- Type 3, regular: every production produces one terminal, optionally followed by one nonterminal.  A finite automaton recognizes these languages.  A deterministic finite automaton (DFA) has exactly one next state for each input symbol; a nondeterministic finite automaton (NFA) may have several.  Both have a fixed number of states and no other memory.
- Type 2, context-free: the left side of every production is a single nonterminal, so a rule applies no matter what surrounds that nonterminal.  A pushdown automaton, which is a finite automaton plus a stack, recognizes these languages.
- Type 1, context-sensitive: a production may rewrite a nonterminal only when particular symbols surround it, and the surrounding symbols stay in place.  A linear-bounded automaton, which is a Turing machine whose tape is limited to the length of the input, recognizes these languages.
- Type 0, unrestricted: any string of symbols may rewrite to any other string.  A Turing machine recognizes these languages.  The languages at this level are called recursively enumerable: a machine can list every member, but it may never halt on a string that is not a member.

Each type strictly contains the type with the higher number: every regular language is also context-free, and every context-free language is also context-sensitive.  The engineering meaning is direct.  The weaker the grammar class, the faster and simpler the recognizer.  Implementers always reach for the weakest class that suffices.

## Examples: Three Telltale Languages, Derived by Hand

Three languages over the alphabet $\{a, b, c\}$ separate the classes cleanly:

- $L_1 = \{ a^n \mid n \ge 1 \}$: one or more a's.
- $L_2 = \{ a^n b^n \mid n \ge 1 \}$: some a's followed by the *same number* of b's.
- $L_3 = \{ a^n b^n c^n \mid n \ge 1 \}$: equal counts of all three letters.

**Deriving `aaabbb` from the Type 2 grammar $S \rightarrow aSb \mid ab$.**

Every step replaces the only nonterminal, $S$, with one of its two right-hand sides.  Choosing `aSb` adds one `a` on the left and one `b` on the right, and keeps $S$ alive in the middle.  Choosing `ab` finishes the derivation with the innermost pair.

```
S
  => a S b           (used S -> aSb)
  => a a S b b       (used S -> aSb again)
  => a a a b b b     (used S -> ab, the base case)
```

The memory that keeps the `a` count equal to the `b` count is the nesting depth of the recursion.  When you implement this grammar as a recursive descent parser, that depth is the call stack.

Why the grammar rejects `aab`.

```
S => aSb => aaSbb    (now need two more characters to close)
  => aaabb           (5 characters, not 3)
OR
S => ab              (2 characters only)
```

No derivation produces exactly two `a`s and one `b` under this grammar.  Every use of `aSb` adds one of each letter, and the base case adds one of each.  The counts can never differ.

Now try $L_3$ yourself, on paper, before you read further.  Take the $L_2$ grammar and try to add a `c` to it.  Write down whatever you come up with.  Derive `abc`, then `aabbcc`, then `aaabbbccc`.  Mark the exact point where your grammar breaks.  That failure is what this section teaches.

### Critical Thinking Questions

Each critical thinking question (CTQ) below builds on the derivations you did above.

> **CTQ 1.1** Write a Type 3 (regular) grammar for $L_1 = \{a^n \mid n \ge 1\}$.
>
> - Step 1: What are the only terminals you need?
> - Step 2: Write one rule that generates a single `a` (the base case) and one rule that generates `a` and then recurses.
> - Step 3: Why can you not use this same trick to check that the number of `a`s equals the number of `b`s?

> **CTQ 1.2** Use the $L_2$ grammar $S \rightarrow aSb \mid ab$.
>
> - Step 1: Apply exactly one production to $S$ to get a sentential form.  Which rule did you choose?  Write the result.
> - Step 2: Apply one more production.  Write the new sentential form.
> - Step 3: Continue until you reach the terminal string `aabb`.  How many total steps did it take?
> - Step 4: Where is the memory that guarantees the `a` count equals the `b` count?  Is it in the grammar rules themselves, or does it emerge from the derivation?

> **CTQ 1.3** $L_3 = \{a^n b^n c^n \mid n \ge 1\}$ is not context-free.  Report on the attempt you made above.
>
> - Step 1: Write the grammar you came up with.
> - Step 2: Does it derive `abc` and `aabbcc` correctly?
> - Step 3: Where does `aaabbbccc` produce the wrong counts or get stuck?
> - Step 4: In one sentence: what kind of memory would you need that a single stack cannot provide?

> **CTQ 1.4** Map this to your project.  Matching nested parentheses in expressions is which of $L_1$, $L_2$, or $L_3$ in disguise?  What does that tell you about whether your *lexer* or your *parser* must handle it, and why?

## Model 1: A Grammar as Data, Derivations as Search

A grammar is a finite set of rewriting rules.  That makes it a data structure, and you can search a data structure.  This model turns "derivable from $S$" from a claim into a test.  It stores the productions in a dictionary and runs a breadth-first search (BFS) over sentential forms.  A sentential form is any string of terminals and nonterminals you can reach from $S$.  BFS visits every form reachable in one step before any form reachable in two steps, and so on.

Real parsers do not work this way (that topic is several weeks away), and this search is hopelessly slow on anything but toy inputs.  What it buys you is a check: the machine can now verify every derivation you did by hand above.

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

- `L2 = {"S": ["aSb", "ab"]}` is the grammar $S \rightarrow aSb \mid ab$ written as data.  The dictionary key is the left-hand side.  The list holds the alternatives.
- `expand_once` is one derivation step, done every possible way at once.  It walks the sentential form looking for a nonterminal.  For each one it finds, it substitutes each alternative in turn.  Your hand derivations picked *one* of these; the search tries all of them.
- The `len(nxt) > limit` prune is what makes the search terminate.  Neither grammar has a production that shortens a form, so a sentential form longer than the target is a dead end forever.
- `derive` returns the whole `path`.  That path is the `S => aSb => aaSbb => ...` chain you wrote by hand.  Compare the printed derivation for `aaabbb` against yours.

> **Watch out!**  This BFS says "not derivable" only after it *exhausts the search space*, and that works only because the prune bounds the space.  Add a production like $S \rightarrow \varepsilon$ that shortens forms, or a rule with a nonterminal that can grow without bound, and the same code can run forever.  Deciding membership in general is much harder than this model suggests.  That difficulty is what the parsing unit is about.

### Critical Thinking Questions

> **CTQ 1.5** Run `report("aabb", L2, "L2")` in your head first: how many steps should it take?  Now check against the output.  Did the machine take the same route you did, or a different one that arrives at the same string?

> **CTQ 1.6** The prune assumes no production shrinks a sentential form.  Write a two-rule grammar for which that assumption is false, and say what `derive` would do with it.

> **CTQ 1.7** `expand_once` rewrites *every* nonterminal position, not only the leftmost.  When you derived by hand, you always rewrote the only $S$ there was.  For a grammar with two nonterminals in a form, does the choice of which one to rewrite change the final string?  Does it change the derivation?

### Try It Yourself

Encode your CTQ 1.1 answer as data and test it.  Then try to encode $L_3$ and watch it fail.

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

Expected output for a correct `MY_L1`: `a`, `aa`, and `aaaa` derivable; `ab` not.  For `MY_L3`: no context-free grammar gets all five right.  Finding out *which* string leaks is the point of the exercise.

---

# Part II: What a Stack Buys You

## 2.  Theory: Counting Is the Dividing Line

The jump from Type 3 to Type 2 has one concrete mechanical meaning: a finite automaton has a fixed, finite memory, and a pushdown automaton has an unbounded stack.

A finite automaton is a fixed set of states with no other storage.  To recognize $a^n b^n$, it would have to remember how many `a`s it has seen, so that it can demand the same number of `b`s.  But $n$ is unbounded, so no fixed number of states is enough.  Give the machine a stack, push one symbol per `a`, and pop one per `b`, and the problem disappears.  That stack is the difference, and that difference is Type 2.

Apply the same argument one level up.  To recognize $a^n b^n c^n$, you must count the `a`s twice: once against the `b`s and once against the `c`s.  The first comparison empties the single stack, so the count is gone by the time the `c`s arrive.  That is the Type 1 boundary.  It is also why "every variable must be declared before use" is not a syntax rule in any real compiler.  That check lives in a separate semantic analysis pass, which walks the tree after the parser builds it.

Tokens are regular.  Structure is context-free.  Meaning is neither.  Your project pipeline (lexer, then parser, then semantic analysis) follows the hierarchy one level per stage.

## Examples: Counting by Hand

Trace both machines on `aabb` before you run anything.  For the finite-state attempt, the only memory is the state name, so write down what each state would have to mean:

| Input read | Finite automaton must remember | Stack machine's stack |
|------------|-------------------------------|----------------------|
| (start)    | "zero a's so far"             | (empty)              |
| `a`        | "one a so far"                | `a`                  |
| `aa`       | "two a's so far"              | `aa`                 |
| `aab`      | "two a's, one b"              | `a`                  |
| `aabb`     | "two a's, two b's: accept"    | (empty: accept)      |

Nothing bounds the right column except the input itself.  The middle column needs a *distinct state* for every count.  For arbitrary $n$, that means infinitely many states, and a finite automaton has finitely many by definition.  That is the whole proof, stated informally.

## Model 2: The Same Language, Two Machines

This model shows a fixed-state recognizer failing on exactly the input where counting matters, and a stack machine succeeding on the same input.

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

- `MAX_STATES = 3` is the honest part of the simulation.  A real DFA has no `count` variable; its state *is* the count.  A machine with three counting states can tell apart "seen one a," "seen two a's," and "seen three a's," and nothing beyond that.
- `finite_state_recognizer` returns `False` on `aaaabbbb` with the reason "ran out of states."  That string is *in* the language.  The machine is not wrong about the string; it is too small to hold the question.
- `stack_recognizer` never counts anything.  It pushes and pops, and the emptiness of the stack at the end is the answer.  Nothing else happens, which is why the $L_2$ grammar's recursion depth was the memory in Part I.
- The `phase` variable enforces that all `a`s come before all `b`s.  Without it, the machine would accept `abab`, because the pushes and pops balance.

> **Watch out!**  It is tempting to say "use a counter instead of states."  A counter that can hold arbitrary $n$ *is* unbounded memory, which is exactly what a finite automaton is defined not to have.  The moment you allow one, you have left Type 3.  The restriction is the definition, not an oversight.

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

Expected output: the first three strings should accept and the last three should reject, and you will not manage that with one stack.  Write down the sentence that explains why.  That sentence is the answer to CTQ 1.3.

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

**Exercise 5.**  Instrument Model 1's `derive` to count how many sentential forms it explores before it finds `aaaabbbb`.  Then try `aaaaabbbbb`.  Plot or tabulate the growth and explain, in one sentence, why nobody parses this way.

---

# Reflection

In your notebook: the whole hierarchy comes down to how much a machine is allowed to remember.  Finite states remember a fixed amount.  A stack remembers an unbounded amount, but only in last-in-first-out order.  A tape remembers everything.

Where else have you run into a problem that became easy the moment you could keep a little more state around, and was impossible before that?  Write a paragraph.  Then say which of the two recognizers in Model 2 you would have written if nobody had told you about the hierarchy first, and what that says about the value of knowing the boundary before you start coding.

---

# Further Reading

- Allison, Chapter 9 §9.3, on the Chomsky hierarchy.
- Allison, Chapter 6 §6.1, on context-free grammars and derivations.
- Hopcroft, Motwani, and Ullman.  *Introduction to Automata Theory, Languages, and Computation*: the standard treatment, with the pumping lemma proofs that make Part II's informal argument rigorous.

---

> **Continued next session.**  Day 2 picks up from here and turns these ideas into grammars you write yourself: [Grammars, Day 2: Writing Context-Free Grammars](https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374-Fall2026/gh-pages/_pages/Activities/liascript-grammars-day2.md).
