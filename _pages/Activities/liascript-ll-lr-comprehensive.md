# LL and LR Parsing: Tables, Conflicts, and How Yacc Works

<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://github.com/BillJr99/Ursinus-CS374-Fall2026/blob/main/_pages/Activities/liascript-ll-lr-comprehensive.md

import: https://raw.githubusercontent.com/liascript/CodeRunner/master/README.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

# LL and LR Parsing: Tables, Conflicts, and How Yacc Works

Your recursive descent parser is already an LL parser — you just haven't seen the table yet. Every function is a row, every `if` on the lookahead token is a column lookup, and every time you call a sub-function you are pushing a frame onto the implicit parse stack. This activity makes that hidden machinery explicit, then flips the whole picture upside-down to show how LR parsers — the kind yacc and bison generate — read the same tokens from the opposite direction and handle grammars that would tie recursive descent in knots.

## Learning Goals

By the end of this activity, you will be able to:

- Compute FIRST and FOLLOW sets by hand for any context-free grammar and use them to populate an LL(1) parsing table
- Identify LL(1) conflicts in a parsing table and determine whether the conflict arises from ambiguity, left recursion, or shared FIRST sets
- Construct the LR(0) item sets and SLR(1) parsing table for a small grammar and execute a simulated bottom-up parse
- Explain what yacc/bison does internally when given a `.y` grammar file, connecting LR item construction to the generated parse table
- Compare LL(1) and SLR(1)/LALR(1) parsing power, identifying grammars that one technique accepts and the other rejects

> **Before You Begin:** This activity assumes you can:
> - Write a simple recursive descent parser for an arithmetic expression grammar
> - Explain what a context-free grammar production rule means (e.g., `E -> T E'`)
> - Trace through a small Python dictionary-based algorithm and predict its output
>
> If any of these feel shaky, review them first.

*"The LL(1) condition is exactly the condition under which you can parse without backtracking: always knowing what to do from one token."*

You have already implemented a **recursive descent parser** — an LL(k) parser in procedural disguise. Every function in your parser corresponds to a nonterminal; every `if` on the current token corresponds to a table lookup. In this module we make that correspondence explicit by constructing the actual **LL(1) parsing table** from your grammar, then turn the table bottom-up to understand **LR parsing** — the more powerful technique that yacc, bison, and most production parsers use. By the end you will be able to: compute FIRST and FOLLOW sets by hand for any context-free grammar; construct an LL(1) table and identify conflicts; construct LR(0) items and an SLR(1) table; and explain precisely what yacc does when it processes your `.y` grammar file.

---

## 0. Running Grammar

We will use one grammar throughout the module:

$$
\begin{aligned}
E  &\to T\ E' \\
E' &\to \mathbf{+}\ T\ E' \mid \epsilon \\
T  &\to F\ T' \\
T' &\to \mathbf{*}\ F\ T' \mid \epsilon \\
F  &\to \mathbf{(}\ E\ \mathbf{)} \mid \mathbf{id}
\end{aligned}
$$

This grammar generates arithmetic expressions with addition and multiplication, where `*` binds tighter than `+`, and it is **left-factored** (no two alternatives for the same nonterminal begin with the same token). The original grammar $E \to E + T \mid T$ has left recursion, which LL parsers cannot handle; left-factoring eliminates it. We will return to left recursion when we discuss LR parsing, where it is not a problem.

---

# Part I: LL(1) Parsing

## 1. FIRST Sets

Think of FIRST sets as answering the question: "If I am about to expand nonterminal $A$, what token could possibly appear at the front of whatever $A$ generates?" It is the set of valid lookaheads that make each production viable. The algorithm is a fixed-point iteration — keep adding tokens until nothing changes — and the tricky case is nullable symbols ($\epsilon$-producing nonterminals) which let the following symbol "bleed through."

$\mathrm{FIRST}(\alpha)$ is the set of terminal symbols that can begin a string derived from $\alpha$. If $\alpha \Rightarrow^* \epsilon$, then $\epsilon \in \mathrm{FIRST}(\alpha)$.

**Algorithm (FIRST for a nonterminal $A$):**
1. For each production $A \to X_1\ X_2\ \ldots\ X_k$:
   - Add $\mathrm{FIRST}(X_1) \setminus \{\epsilon\}$
   - If $\epsilon \in \mathrm{FIRST}(X_1)$, also add $\mathrm{FIRST}(X_2) \setminus \{\epsilon\}$
   - Continue until either some $X_i$ cannot derive $\epsilon$, or all have been added
   - If all $X_i$ can derive $\epsilon$, add $\epsilon$ to $\mathrm{FIRST}(A)$
2. Repeat until no changes.

For terminals: $\mathrm{FIRST}(a) = \{a\}$; $\mathrm{FIRST}(\epsilon) = \{\epsilon\}$.

**Worked example on our grammar:**

| Symbol | FIRST |
|--------|-------|
| $F$    | $\{(\text{,}\ \mathbf{id}\}$ |
| $T'$   | $\{*, \epsilon\}$ |
| $T$    | $\mathrm{FIRST}(F) = \{(,\ \mathbf{id}\}$ |
| $E'$   | $\{+, \epsilon\}$ |
| $E$    | $\mathrm{FIRST}(T) = \{(,\ \mathbf{id}\}$ |

```python
# Computing FIRST sets programmatically
from collections import defaultdict

EPSILON = 'ε'

# Grammar as a dict: nonterminal -> list of productions (each production = list of symbols)
grammar = {
    'E':  [['T', "E'"]],
    "E'": [['+', 'T', "E'"], [EPSILON]],
    'T':  [['F', "T'"]],
    "T'": [['*', 'F', "T'"], [EPSILON]],
    'F':  [['(', 'E', ')'], ['id']],
}
terminals = {'+', '*', '(', ')', 'id', '$', EPSILON}

def compute_first(grammar, terminals):
    first = defaultdict(set)
    for t in terminals:
        first[t] = {t}

    changed = True
    while changed:
        changed = False
        for nt, productions in grammar.items():
            for prod in productions:
                for sym in prod:
                    addition = first[sym] - {EPSILON}
                    if not addition.issubset(first[nt]):
                        first[nt] |= addition
                        changed = True
                    if EPSILON not in first[sym]:
                        break
                else:
                    if EPSILON not in first[nt]:
                        first[nt].add(EPSILON)
                        changed = True
    return first

first = compute_first(grammar, terminals)
for sym in ['E', "E'", 'T', "T'", 'F']:
    print(f"FIRST({sym:3s}) = {sorted(first[sym])}")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

> **Watch out!** FIRST is computed for **grammar symbols** (nonterminals and terminals), not for input tokens. `FIRST('id')` is always `{'id'}` — terminals have trivial FIRST sets. The interesting work is for nonterminals, especially nullable ones. Students often compute FIRST for just one production and forget to take the union across all productions for the same nonterminal.

---

## 2. FOLLOW Sets

FOLLOW sets answer the question: "After fully expanding $A$, what token could legitimately come next?" They are needed specifically for $\epsilon$-productions: if $A$ can disappear, the parser needs to know when it is safe to apply that $\epsilon$-production (the lookahead must be something in FOLLOW($A$)). The algorithm propagates FOLLOW backwards through the grammar — a dependency that makes it trickier than FIRST.

$\mathrm{FOLLOW}(A)$ is the set of terminals that can appear immediately after $A$ in some sentential form. It always includes **$\$** for the start symbol.

**Algorithm:**
1. $\$ \in \mathrm{FOLLOW}(S)$ (start symbol)
2. For each production $A \to \alpha B \beta$:
   - Add $\mathrm{FIRST}(\beta) \setminus \{\epsilon\}$ to $\mathrm{FOLLOW}(B)$
   - If $\epsilon \in \mathrm{FIRST}(\beta)$, add $\mathrm{FOLLOW}(A)$ to $\mathrm{FOLLOW}(B)$
3. Repeat until no changes.

```python
from collections import defaultdict

EPSILON = 'ε'

grammar = {
    'E':  [['T', "E'"]],
    "E'": [['+', 'T', "E'"], [EPSILON]],
    'T':  [['F', "T'"]],
    "T'": [['*', 'F', "T'"], [EPSILON]],
    'F':  [['(', 'E', ')'], ['id']],
}
terminals = {'+', '*', '(', ')', 'id', '$', EPSILON}

def compute_first(grammar, terminals):
    first = defaultdict(set)
    for t in terminals:
        first[t] = {t}
    changed = True
    while changed:
        changed = False
        for nt, productions in grammar.items():
            for prod in productions:
                for sym in prod:
                    addition = first[sym] - {EPSILON}
                    if not addition.issubset(first[nt]):
                        first[nt] |= addition
                        changed = True
                    if EPSILON not in first[sym]:
                        break
                else:
                    if EPSILON not in first[nt]:
                        first[nt].add(EPSILON)
                        changed = True
    return first

first = compute_first(grammar, terminals)

def compute_follow(grammar, first, start='E'):
    follow = defaultdict(set)
    follow[start].add('$')

    changed = True
    while changed:
        changed = False
        for nt, productions in grammar.items():
            for prod in productions:
                for i, sym in enumerate(prod):
                    if sym in terminals or sym == EPSILON:
                        continue
                    # sym is a nonterminal; look at what follows it
                    beta = prod[i+1:]
                    # FIRST(beta) minus epsilon
                    first_beta = set()
                    all_nullable = True
                    for s in beta:
                        first_beta |= first[s] - {EPSILON}
                        if EPSILON not in first[s]:
                            all_nullable = False
                            break
                    else:
                        all_nullable = True
                    addition = first_beta - {EPSILON}
                    if not addition.issubset(follow[sym]):
                        follow[sym] |= addition
                        changed = True
                    if all_nullable or beta == []:
                        if not follow[nt].issubset(follow[sym]):
                            follow[sym] |= follow[nt]
                            changed = True
    return follow

follow = compute_follow(grammar, first)
for sym in ['E', "E'", 'T', "T'", 'F']:
    print(f"FOLLOW({sym:3s}) = {sorted(follow[sym])}")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

---

## 3. LL(1) Parsing Table Construction

The table fuses FIRST and FOLLOW into a single lookup structure: row = nonterminal being expanded, column = lookahead token, cell = which production to use. A grammar is LL(1) if and only if every cell has at most one entry. Two productions landing in the same cell mean the one-token lookahead is ambiguous — the parser cannot decide without more information.

> **Watch out!** A grammar can be unambiguous and still fail to be LL(1) — left recursion and shared FIRST sets both cause LL(1) conflicts in perfectly unambiguous grammars. Do not conflate "not LL(1)" with "ambiguous."

The **LL(1) parsing table** $M[A, a]$ specifies: when parsing nonterminal $A$ with lookahead token $a$, which production should we use?

**Construction rule:** For each production $A \to \alpha$:
1. For each terminal $a \in \mathrm{FIRST}(\alpha)$: set $M[A, a] = A \to \alpha$
2. If $\epsilon \in \mathrm{FIRST}(\alpha)$: for each $b \in \mathrm{FOLLOW}(A)$: set $M[A, b] = A \to \alpha$

**A grammar is LL(1) if and only if no table entry has more than one production.**

```python
from collections import defaultdict

EPSILON = 'ε'

grammar = {
    'E':  [['T', "E'"]],
    "E'": [['+', 'T', "E'"], [EPSILON]],
    'T':  [['F', "T'"]],
    "T'": [['*', 'F', "T'"], [EPSILON]],
    'F':  [['(', 'E', ')'], ['id']],
}
terminals = {'+', '*', '(', ')', 'id', '$', EPSILON}

def compute_first(grammar, terminals):
    first = defaultdict(set)
    for t in terminals:
        first[t] = {t}
    changed = True
    while changed:
        changed = False
        for nt, productions in grammar.items():
            for prod in productions:
                for sym in prod:
                    addition = first[sym] - {EPSILON}
                    if not addition.issubset(first[nt]):
                        first[nt] |= addition
                        changed = True
                    if EPSILON not in first[sym]:
                        break
                else:
                    if EPSILON not in first[nt]:
                        first[nt].add(EPSILON)
                        changed = True
    return first

def compute_follow(grammar, first, start='E'):
    follow = defaultdict(set)
    follow[start].add('$')
    changed = True
    while changed:
        changed = False
        for nt, productions in grammar.items():
            for prod in productions:
                for i, sym in enumerate(prod):
                    if sym in terminals or sym == EPSILON:
                        continue
                    beta = prod[i+1:]
                    first_beta = set()
                    all_nullable = True
                    for s in beta:
                        first_beta |= first[s] - {EPSILON}
                        if EPSILON not in first[s]:
                            all_nullable = False
                            break
                    else:
                        all_nullable = True
                    addition = first_beta - {EPSILON}
                    if not addition.issubset(follow[sym]):
                        follow[sym] |= addition
                        changed = True
                    if all_nullable or beta == []:
                        if not follow[nt].issubset(follow[sym]):
                            follow[sym] |= follow[nt]
                            changed = True
    return follow

first = compute_first(grammar, terminals)
follow = compute_follow(grammar, first)

def build_ll1_table(grammar, first, follow, terminals):
    table = defaultdict(dict)
    conflicts = []

    for nt, productions in grammar.items():
        for prod in productions:
            # compute FIRST of this production's right-hand side
            first_rhs = set()
            all_nullable = True
            for sym in prod:
                first_rhs |= first[sym] - {EPSILON}
                if EPSILON not in first[sym]:
                    all_nullable = False
                    break
            if prod == [EPSILON] or all_nullable:
                first_rhs.add(EPSILON)

            for a in first_rhs - {EPSILON}:
                if a in table[nt]:
                    conflicts.append((nt, a, table[nt][a], prod))
                table[nt][a] = prod

            if EPSILON in first_rhs:
                for b in follow[nt]:
                    if b in table[nt]:
                        conflicts.append((nt, b, table[nt][b], prod))
                    table[nt][b] = prod

    return table, conflicts

ll1_table, conflicts = build_ll1_table(grammar, first, follow, terminals)

# Display the table
nonterminals = ['E', "E'", 'T', "T'", 'F']
tok_order    = ['id', '+', '*', '(', ')', '$']

print(f"{'':5s}", end="")
for tok in tok_order:
    print(f"{tok:15s}", end="")
print()
print("-" * 95)
for nt in nonterminals:
    print(f"{nt:5s}", end="")
    for tok in tok_order:
        cell = " -> " + " ".join(ll1_table[nt].get(tok, ['']))
        print(f"{cell:15s}", end="")
    print()

print("\nConflicts:", conflicts if conflicts else "None — grammar is LL(1)!")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

---

## 4. LL(1) Table-Driven Parsing

Once the table exists, parsing is a deterministic stack machine — no backtracking, no recursion, just push, pop, and table lookup. This model lets you see explicitly what your recursive descent parser was doing implicitly: the call stack becomes a literal stack of grammar symbols, and each function-call/return maps to a push/pop pair.

With the table in hand, the parser is a simple stack machine:

1. Initialize stack: `[$, S]` (start symbol on top, $ at bottom)
2. Repeat:
   - If top of stack is terminal $a$ and input is $a$: **match** — pop and advance input
   - If top of stack is terminal $a$ ≠ input: **error**
   - If top of stack is nonterminal $A$: look up $M[A, \text{lookahead}]$; **replace** $A$ with the production's RHS
   - If top of stack is $ and input is $: **accept**

```python
from collections import defaultdict

EPSILON = 'ε'

grammar = {
    'E':  [['T', "E'"]],
    "E'": [['+', 'T', "E'"], [EPSILON]],
    'T':  [['F', "T'"]],
    "T'": [['*', 'F', "T'"], [EPSILON]],
    'F':  [['(', 'E', ')'], ['id']],
}
terminals = {'+', '*', '(', ')', 'id', '$', EPSILON}

def compute_first(grammar, terminals):
    first = defaultdict(set)
    for t in terminals:
        first[t] = {t}
    changed = True
    while changed:
        changed = False
        for nt, productions in grammar.items():
            for prod in productions:
                for sym in prod:
                    addition = first[sym] - {EPSILON}
                    if not addition.issubset(first[nt]):
                        first[nt] |= addition
                        changed = True
                    if EPSILON not in first[sym]:
                        break
                else:
                    if EPSILON not in first[nt]:
                        first[nt].add(EPSILON)
                        changed = True
    return first

def compute_follow(grammar, first, start='E'):
    follow = defaultdict(set)
    follow[start].add('$')
    changed = True
    while changed:
        changed = False
        for nt, productions in grammar.items():
            for prod in productions:
                for i, sym in enumerate(prod):
                    if sym in terminals or sym == EPSILON:
                        continue
                    beta = prod[i+1:]
                    first_beta = set()
                    all_nullable = True
                    for s in beta:
                        first_beta |= first[s] - {EPSILON}
                        if EPSILON not in first[s]:
                            all_nullable = False
                            break
                    else:
                        all_nullable = True
                    addition = first_beta - {EPSILON}
                    if not addition.issubset(follow[sym]):
                        follow[sym] |= addition
                        changed = True
                    if all_nullable or beta == []:
                        if not follow[nt].issubset(follow[sym]):
                            follow[sym] |= follow[nt]
                            changed = True
    return follow

def build_ll1_table(grammar, first, follow, terminals):
    table = defaultdict(dict)
    conflicts = []
    for nt, productions in grammar.items():
        for prod in productions:
            first_rhs = set()
            all_nullable = True
            for sym in prod:
                first_rhs |= first[sym] - {EPSILON}
                if EPSILON not in first[sym]:
                    all_nullable = False
                    break
            if prod == [EPSILON] or all_nullable:
                first_rhs.add(EPSILON)
            for a in first_rhs - {EPSILON}:
                if a in table[nt]:
                    conflicts.append((nt, a, table[nt][a], prod))
                table[nt][a] = prod
            if EPSILON in first_rhs:
                for b in follow[nt]:
                    if b in table[nt]:
                        conflicts.append((nt, b, table[nt][b], prod))
                    table[nt][b] = prod
    return table, conflicts

first = compute_first(grammar, terminals)
follow = compute_follow(grammar, first)
ll1_table, _ = build_ll1_table(grammar, first, follow, terminals)

def ll1_parse(tokens, table, start='E'):
    """
    tokens: list of terminal strings, ending with '$'
    Returns: list of (action, detail) pairs showing the parse
    """
    stack   = ['$', start]
    pos     = 0
    trace   = []

    while stack:
        top     = stack[-1]
        current = tokens[pos]
        stack_str = " ".join(reversed(stack))

        if top == '$' and current == '$':
            trace.append(("ACCEPT", ""))
            return trace

        elif top == current:  # terminal match
            trace.append(("MATCH", current))
            stack.pop()
            pos += 1

        elif top in terminals:
            trace.append(("ERROR", f"Expected {top}, got {current}"))
            return trace

        elif current in table[top]:
            prod = table[top][current]
            trace.append(("PREDICT", f"{top} -> {' '.join(prod)}"))
            stack.pop()
            if prod != [EPSILON]:
                for sym in reversed(prod):
                    stack.append(sym)

        else:
            trace.append(("ERROR", f"No table entry for [{top}, {current}]"))
            return trace

    return trace

tokens = ['id', '+', 'id', '*', 'id', '$']
print("Parsing:", " ".join(tokens[:-1]))
for action, detail in ll1_parse(tokens, ll1_table):
    print(f"  {action:8s}  {detail}")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

---

[[MC]]
A grammar has a production $A \to \alpha \mid \beta$ where $\mathrm{FIRST}(\alpha) \cap \mathrm{FIRST}(\beta) \neq \emptyset$. What does this mean for LL(1) parsing?

- (x) It is a conflict: the LL(1) table will have two entries for the same cell, so the parser cannot decide which alternative to use with one token of lookahead.
- ( ) It is fine: the parser backtracks, trying $\alpha$ first and then $\beta$ if $\alpha$ fails.
- ( ) It means the grammar is ambiguous, and ambiguous grammars can never be parsed by any algorithm.
- ( ) The grammar needs left-factoring to move shared prefixes into a common alternative; after factoring, the grammar is unambiguous.

---

# Part II: LR Parsing

## 5. The LR Idea: Bottom-Up with a Stack

LR parsing feels backward at first: instead of predicting what to expand next (LL's "top-down" view), LR parsers collect tokens on a stack and wait until they have seen a complete right-hand side — then they collapse it back to the left-hand side (a "reduction"). Think of it like assembling a sentence by collecting words until you can label a phrase, then treating the labeled phrase as a single unit for the next level up.

**LR parsers** work bottom-up: they shift tokens onto a stack and **reduce** (replace a handle matching a production's RHS with its LHS) when they have seen enough. The "L" means left-to-right scan; "R" means rightmost derivation in reverse; "k" is the lookahead.

The key data structures are:
- **Stack**: holds states (integers) encoding what has been seen so far
- **Action table** $\mathrm{ACTION}[s, a]$: for state $s$ and lookahead $a$, either **shift** to a new state, **reduce** by a production, **accept**, or **error**
- **Goto table** $\mathrm{GOTO}[s, A]$: after reducing to nonterminal $A$ in state $s$, go to this new state

The tables encode a **push-down automaton** built from the grammar.

## 6. LR(0) Items and the Canonical Collection

An LR(0) item is a production with a bookmark (the dot) that says "I have seen this much of the right-hand side so far." The set of all possible bookmarked states the parser could be in, connected by transitions, forms a finite automaton — the "canonical collection." Understanding this automaton is the key to understanding what shift-reduce conflicts mean and why some grammars are hard to parse.

An **LR(0) item** is a production with a dot marking how much has been recognized:

$$
E' \to E\ \bullet \qquad \text{(E has been seen; we might reduce)}
$$
$$
E' \to \bullet\ E \qquad \text{(we are about to see E)}
$$

The **closure** of a set of items: if $[A \to \alpha \bullet B \beta]$ is in the set and $B \to \gamma$ is a production, add $[B \to \bullet \gamma]$.

The **goto** function: $\mathrm{goto}(I, X)$ = closure of all items in $I$ where the dot is advanced over $X$.

```python
# LR(0) item construction for a simpler grammar: S' -> S, S -> ( S ) | x
simple_grammar = {
    "S'": [["S"]],
    "S":  [["(", "S", ")"], ["x"]],
}

def closure(items, grammar):
    result = set(items)
    changed = True
    while changed:
        changed = False
        for (nt, prod, dot) in list(result):
            if dot < len(prod):
                sym = prod[dot]
                if sym in grammar:
                    for p in grammar[sym]:
                        item = (sym, tuple(p), 0)
                        if item not in result:
                            result.add(item)
                            changed = True
    return frozenset(result)

def goto_set(items, sym, grammar):
    advanced = set()
    for (nt, prod, dot) in items:
        if dot < len(prod) and prod[dot] == sym:
            advanced.add((nt, prod, dot + 1))
    return closure(advanced, grammar) if advanced else frozenset()

# Build all item sets
start_item = ("S'", tuple(simple_grammar["S'"][0]), 0)
start_set  = closure({start_item}, simple_grammar)
states     = [start_set]
state_map  = {start_set: 0}
transitions= {}

to_process = [start_set]
all_syms   = list(simple_grammar.keys()) + ['(', ')', 'x']

while to_process:
    current = to_process.pop()
    s_id    = state_map[current]
    for sym in all_syms:
        g = goto_set(current, sym, simple_grammar)
        if g:
            if g not in state_map:
                state_map[g] = len(states)
                states.append(g)
                to_process.append(g)
            transitions[(s_id, sym)] = state_map[g]

> **Watch out!** The closure operation adds items for every production of each nonterminal that appears after a dot — including transitively. A single starting item can generate a large closure. Students often compute closure for only the directly referenced nonterminal and miss the transitive additions.

print(f"LR(0) automaton: {len(states)} states")
for sid, items in enumerate(states):
    print(f"\nState {sid}:")
    for nt, prod, dot in sorted(items):
        before = " ".join(prod[:dot])
        after  = " ".join(prod[dot:])
        print(f"  {nt} -> {before} . {after}")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

---

## 7. SLR(1) Tables: Adding Lookahead

**SLR(1)** (Simple LR) uses FOLLOW sets to decide when to reduce:

- **Shift** action for state $s$ on terminal $a$: if $\mathrm{goto}(s, a) = s'$, put $\mathrm{ACTION}[s, a] = \mathrm{shift}\ s'$
- **Reduce** action: if $[A \to \alpha \bullet]$ is in state $s$ and $a \in \mathrm{FOLLOW}(A)$, put $\mathrm{ACTION}[s, a] = \mathrm{reduce}\ A \to \alpha$
- **Accept**: if $[S' \to S\ \bullet]$ is in state $s$, put $\mathrm{ACTION}[s, \$] = \mathrm{accept}$

An **SLR conflict** occurs when the same cell gets two actions:
- **Shift-reduce conflict**: both a shift and a reduce are valid. Often resolved by **precedence** (Yacc does this for `+` vs `*`).
- **Reduce-reduce conflict**: two different reductions. Usually indicates a grammar problem.

**LALR(1)** (Look-Ahead LR) is SLR(1) with more precise lookahead sets — not FOLLOW(A) globally, but the specific lookahead valid for each particular reduce in each state. LALR(1) is what yacc/bison implements, and it handles most practical programming language grammars.

---

### Try It: With a Partner — Build the SLR Table by Hand

Use the simple grammar $S \to (S) \mid x$ and the item sets built above.

1. Partner A computes FOLLOW sets for $S$ and $S'$.
2. Partner B lists all states with a reduce item (dot at end).
3. Together, fill in the ACTION and GOTO tables.
4. Trace the parse of `( x )` using your table.

Report: Did any state have a conflict? What would it mean if it did?

---

## 8. How Yacc/Bison Uses LALR(1)

When you write a `.y` file for bison, the tool:

1. Reads your productions and builds the LALR(1) automaton (equivalent to computing the LR(1) canonical collection and then merging states with identical cores but different lookaheads)
2. Constructs the ACTION and GOTO tables
3. Uses `%left`, `%right`, `%nonassoc`, and `%prec` to resolve shift-reduce conflicts by operator precedence and associativity
4. Emits a C parser (`yyparse`) that is a table-driven stack machine

**The `%left`/`%right` directives do not change the grammar** — they just tell bison which table cell to fill when there is a shift-reduce conflict. For `+` declared `%left`, a conflict between shifting another `+` and reducing the current expression resolves in favor of reduce (left-associative). For `*` declared with higher precedence than `+`, a conflict between `*` and the end of an additive expression resolves to shift.

```c
/* Minimal Bison grammar for our running example */
%token ID
%left '+' '-'
%left '*' '/'
%right UMINUS      /* unary minus, highest precedence */
%%
expr : expr '+' expr   { $$ = $1 + $3; }
     | expr '-' expr   { $$ = $1 - $3; }
     | expr '*' expr   { $$ = $1 * $3; }
     | expr '/' expr   { $$ = $1 / $3; }
     | '-' expr %prec UMINUS  { $$ = -$2; }
     | '(' expr ')'   { $$ = $2; }
     | ID             { $$ = sym_lookup($1); }
     ;
%%
```

This grammar is **ambiguous** (multiple parse trees for `a + b * c`) but the `%left`/`%right` declarations resolve all shift-reduce conflicts, effectively making the parser behave as if it parsed the unambiguous grammar from our running example. Writing the ambiguous grammar and using precedence declarations is idiomatic bison style.

---

## 9. LL vs. LR: The Practical Comparison

| Property | LL(1) | LR(1) / LALR(1) |
|---|---|---|
| Direction | Top-down, leftmost derivation | Bottom-up, rightmost derivation in reverse |
| Implementation | Recursive descent | Table-driven stack machine |
| Left recursion | **Cannot handle** (infinite loop) | Handles naturally |
| Left factoring | Required to eliminate common prefixes | Not required |
| Power | Strictly weaker | Strictly stronger |
| Error messages | Very good (natural position in recursion) | Harder to produce good messages |
| Lookahead | One token (LL(1)) | One token (LALR(1)) |
| Generated by | LL parser generators (ANTLR default mode) | yacc, bison, MENHIR, most production tools |
| Hand-written? | Yes — recursive descent is natural | Rarely — too complex to build by hand |

**The key practical insight:** recursive descent is LL(1) implemented as code. The function call stack *is* the parser stack. When you refactored your grammar to eliminate left recursion and common prefixes, you were making it LL(1). LR(1) parsers can handle the original left-recursive grammar directly — that is why bison is so popular for complex grammars.

---

## 10. Exercises

1. **FIRST and FOLLOW by hand.** Compute FIRST and FOLLOW for every nonterminal in the grammar:
   $$G: S \to A\ B,\quad A \to a\ A \mid \epsilon,\quad B \to b\ B \mid b$$
   Build the LL(1) table and identify any conflicts. If there is a conflict, explain whether left-factoring or another transformation can resolve it.

2. **Table-driven parse trace.** Using the LL(1) table from Section 3, trace the parse of `( id + id )` step by step: show the stack, input, and action at each step. What is the sequence of productions used?

3. **Left recursion elimination.** Transform the grammar $E \to E + T \mid T$, $T \to T * F \mid F$, $F \to (E) \mid \mathbf{id}$ into an equivalent non-left-recursive grammar. Compute FIRST and FOLLOW sets for the transformed grammar. Compare it to our running grammar — is it the same?

4. **LR(0) item construction.** For the grammar $S \to a S b \mid a b$, construct all LR(0) item sets by hand. Draw the automaton. Identify which states have reduce items, and determine which tokens (using FOLLOW sets) trigger each reduction.

5. **Bison conflict resolution.** The grammar fragment `stmt → IF expr THEN stmt | IF expr THEN stmt ELSE stmt` is the classic dangling-else ambiguity. In bison, the default conflict resolution is shift (matching `else` with the nearest `if`). Write the bison `%prec` declaration that enforces this explicitly, and trace the parse of `if e1 then if e2 then s1 else s2` showing when shift wins over reduce.

---

## 11. Further Reading

- Aho, Alfred V., Monica Lam, Ravi Sethi, and Jeffrey Ullman. *Compilers: Principles, Techniques, and Tools* (2nd ed., "Dragon Book"). Chapters 4-5 are the standard reference for LL and LR parsing, FIRST/FOLLOW, and table construction.
- Thain, Douglas. *Introduction to Compilers and Language Design*. Chapter 5 covers recursive descent; Chapter 6 covers LR parsing; available free at the course textbook link.
- Grune, Dick and Ceriel Jacobs. *Parsing Techniques: A Practical Guide* (2nd ed., Springer, 2008). Free PDF. The most comprehensive survey of parsing algorithms.
- DeRemer, Franklin and Thomas Pennello. "Efficient Computation of LALR(1) Look-Ahead Sets." *ACM TOPLAS* 4(4), 1982. The algorithm bison actually uses.
- Parr, Terence. *The Definitive ANTLR 4 Reference* (Pragmatic Bookshelf, 2013). LL(*) — the generalization of LL(1) that ANTLR implements, with arbitrary lookahead.
