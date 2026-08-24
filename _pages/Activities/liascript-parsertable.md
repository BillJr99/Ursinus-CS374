<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374-Fall2026/gh-pages/_pages/Activities/liascript-parsertable.md or locally via https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374-Fall2026/gh-pages/_pages/Activities/liascript-parsertable.md

import: https://raw.githubusercontent.com/liascript/CodeRunner/master/README.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

# Table-Driven and LR Parsing

Table-driven parsers, LL(1) and LR, replace moment-to-moment grammar reasoning with a lookup.  Think of a parsing table like a GPS route precomputed from every intersection: instead of rethinking the best path each time you reach a fork, you simply consult the table and execute the move it prescribes.  The table was built once, offline, from the grammar's FIRST and FOLLOW sets; at parse time all the "thinking" has already been done.  This makes table-driven parsers fast, systematic, and amenable to machine generation, which is exactly why industrial parser generators emit them.

## Learning Goals

By the end of this activity, you will be able to:

- Execute a shift-reduce parse by hand, maintaining a stack-and-input table and selecting shift or reduce at each step
- Explain why left-recursive grammar rules that defeat recursive descent are handled naturally by an LR parser
- Identify shift-reduce and reduce-reduce conflicts in an LR grammar and describe the grammar restructuring or precedence declaration needed to resolve each
- Compare LL(1) and LR(1) parsing strategies on the dimensions of grammar coverage, implementation complexity, and error-message quality
- Determine which parsing strategy (hand-written descent vs. table-driven generator) is appropriate for a given language design scenario

> **Before You Begin**
>
> This activity assumes you can:
> - Read and write grammars in BNF (Backus-Naur Form), including how `|` separates alternatives and how nonterminals recursively expand
> - Explain what FIRST and FOLLOW sets are and why they matter for predicting which production to apply
> - Describe how a recursive-descent parser works: one function per nonterminal, calling itself when it encounters a nonterminal in the production
>
> If any of these feel shaky, revisit the recursive-descent and grammar modules before continuing.

The recursive descent of the *Recursive Descent Parsing* and *Parsing Expressions* activities is top-down: it predicts what must come next.  The industrial-strength alternative works **bottom-up**: an **LR parser** shifts tokens onto a stack and reduces them to nonterminals when it recognizes a completed right-hand side, driven entirely by a precomputed table.  In a single class session we learn to *read and execute* this machinery by hand, because parser generators (yacc, bison, ANTLR) emit it, error messages reference it, and the left recursion that broke descent is exactly what LR handles natively.  The path today: **shift-reduce intuition $\rightarrow$ executing a parse by hand $\rightarrow$ conflicts $\rightarrow$ when to use which technology**.

---

## Directions and Group Roles

Work in your POGIL team with your rotated roles (**Manager**, **Recorder**, **Presenter**, **Reflector**).  Please think each model and question through on your own first, then talk it over with your group.  The Recorder posts your answers to the Class Activity Questions discussion board, and the Presenter reports out wherever you disagreed or found another approach.  After class, please respond to the reflective prompt on your own in your notebook.

---

# Part I: The Shift-Reduce Idea

Recursive descent builds a parse tree from the root downward, predicting what has to come next.  Shift-reduce parsing does the opposite.  It reads tokens left to right, stacking them up until it recognizes a completed right-hand side, and then collapses that stack into the corresponding nonterminal.  The tree grows from the leaves upward, one reduction at a time.

## 1.  Bottom-Up in One Picture

An LR parser maintains a stack and looks at one input token.  At each step it consults a table and performs one of two moves: **shift** (push the next input token onto the stack) or **reduce** (the top of the stack matches some production's right-hand side; pop it and push the production's left-hand nonterminal).  Accept when the stack holds exactly the start symbol and the input is exhausted.  The parse is a *rightmost derivation discovered in reverse*: the tree grows from the leaves upward, which is why left-recursive rules like `E -> E + T` are not merely tolerable but natural; the parser simply reduces `E + T` to `E` whenever it sees one completed on the stack.

Using the ladder grammar (`E -> E + T | T`, `T -> T * F | F`, `F -> num | ( E )`), the parse of `2 + 3`:

| Stack | Input | Action |
|-------|-------|--------|
| | `2 + 3 $` | shift |
| `2` | `+ 3 $` | reduce `F -> num` |
| `F` | `+ 3 $` | reduce `T -> F` |
| `T` | `+ 3 $` | reduce `E -> T` |
| `E` | `+ 3 $` | shift |
| `E +` | `3 $` | shift |
| `E + 3` | `$` | reduce `F -> num`, then `T -> F` |
| `E + T` | `$` | reduce `E -> E + T` |
| `E` | `$` | **accept** |

Check your reading of the table before moving on:

In the trace above, the single token `2` is reduced through `F -> num`, `T -> F`, and `E -> T` *before* the `+` is shifted.  What makes those three reductions necessary?

[( )] An LR parser must alternate one shift with one reduce
[(X)] The production that will eventually consume the `+` is `E -> E + T`, which requires an `E` (not a bare `num`) on the stack to the left of the `+`
[( )] The token `2` is ambiguous until it has been reduced
[( )] Reductions shrink the stack so it cannot overflow

In the second-to-last row, the stack `E + T` with input `$` is reduced using the production `E -> E +` [[T]], after which the stack holds only the start symbol and the parser accepts.

---

## Worked Example: Building the Table by Hand

The trace above used a table without saying where the table came from.  That is the gap this section closes: an LR parser is a stack plus a *table*, and the table is not magic: it is a finite automaton over **items**, and you can build it with a pencil.

An **item** is a production with a dot marking how much of the right-hand side we have already seen. `T -> T . * F` means "we are partway through `T -> T * F`; we have the `T`, we expect a `*` next."

First, **augment** the grammar with a new start production so acceptance is a single, unambiguous event:

```
0.  E' -> E
1.  E  -> E + T
2.  E  -> T
3.  T  -> T * F
4.  T  -> F
5.  F  -> num
6.  F  -> ( E )
```

### Step 1: closure of the start state

Start from the single item `E' -> . E`.  The **closure** rule says: if the dot sits immediately before a non-terminal, add every production for that non-terminal with the dot at the front.  Repeat until nothing new appears.

| Added because | Item |
|---|---|
| we start here | `E' -> . E` |
| dot before `E` | `E -> . E + T` |
| dot before `E` | `E -> . T` |
| dot before `T` | `T -> . T * F` |
| dot before `T` | `T -> . F` |
| dot before `F` | `F -> . num` |
| dot before `F` | `F -> . ( E )` |

That set of seven items **is** state `I0`.  Notice what closure means: standing at the very beginning of the input, the parser is simultaneously "about to parse an E, and a T, and an F, and a num, and a `(`."  It commits to nothing until it sees a token.

### Step 2: GOTO, one transition, worked

`GOTO(I, X)` advances the dot past `X` in every item that has the dot before `X`, then takes the closure.  Take `GOTO(I0, T)`:

- Items in `I0` with the dot before `T`: `E -> . T` and `T -> . T * F`
- Advance the dot: `E -> T .` and `T -> T . * F`
- Closure adds nothing (no dot sits before a non-terminal)

So `I2 = { E -> T . , T -> T . * F }`.  **This one state is the whole precedence story.**  It contains a completed item (`E -> T .`, meaning "reduce") *and* an item expecting more input (`T -> T . * F`, meaning "shift the `*`").  Which one fires depends entirely on the lookahead token, and that is exactly the shift-reduce decision CTQ 2 asks about, sitting in a single state you just built by hand.

Repeating this for every state and every symbol gives twelve states.  Here are the ones you need:

| State | Items |
|---|---|
| `I0` | the seven items above |
| `I1` | `E' -> E .` , `E -> E . + T` |
| `I2` | `E -> T .` , `T -> T . * F` |
| `I3` | `T -> F .` |
| `I4` | `F -> num .` |
| `I6` | `E -> E + . T` , `T -> . T * F` , `T -> . F` , `F -> . num` , `F -> . ( E )` |
| `I7` | `T -> T * . F` , `F -> . num` , `F -> . ( E )` |
| `I8` | `E -> E + T .` , `T -> T . * F` |
| `I9` | `T -> T * F .` |

### Step 3: fill in ACTION and GOTO

Now read the table straight off the states.  A dot before a **terminal** means *shift to the target state*.  A **completed** item (dot at the end) means *reduce by that production*, on every token in the FOLLOW set of its left-hand side. `E' -> E .` on `$` means *accept*.

`FOLLOW(E) = { + ) $ }` and `FOLLOW(T) = FOLLOW(F) = { * + ) $ }`.

| State | `num` | `*` | `+` | `$` | -> E | -> T | -> F |
|---|---|---|---|---|---|---|---|
| 0 | s4 | | | | 1 | 2 | 3 |
| 1 | | | s6 | **accept** | | | |
| 2 | | s7 | r2 | r2 | | | |
| 3 | | r4 | r4 | r4 | | | |
| 4 | | r5 | r5 | r5 | | | |
| 6 | s4 | | | | | 8 | 3 |
| 7 | s4 | | | | | | 9 |
| 8 | | s7 | r1 | r1 | | | |
| 9 | | r3 | r3 | r3 | | | |

Look at **row 2**: on `*` the parser shifts, on `+` or `$` it reduces `E -> T`.  That single row is where `*` binds tighter than `+`.  Nobody decided it at parse time; it fell out of the item set.  Compare that to recursive descent, where the same precedence lives in the *shape of your function calls*.

> **Check yourself.**  In row 8 (`E -> E + T .` and `T -> T . * F`), why is there an `s7` under `*` rather than a reduce?  Because `T . * F` is still expecting a `*`; reducing `E -> E + T` first would build `(2+3)*4` instead of `2+(3*4)`.  That is CTQ 2's answer, visible in one table cell.

---

## Model 1: Drive the Machine

The example above walked through `2 + 3` step by step.  Now your team will execute the same algorithm on a slightly more complex input and confront a key decision: when two tokens compete for precedence, the lookahead token is what breaks the tie.  The table already encodes that decision; your job here is to discover *why* the lookahead is necessary by watching what goes wrong without it.

### Critical Thinking Questions

1.  Execute the shift-reduce parse of `2 * 3 + 4` as a team, producing the full stack-input-action table.  The Recorder keeps the official copy; expect 12 to 14 rows.
2.  At the configuration stack `E + T`, input `* 4 $` (during a parse of `2 + 3 * 4`), the parser must NOT reduce `E -> E + T` yet.  Explain what would go wrong with precedence if it did, and what the parser does instead.  (The table encodes this choice; you just discovered why the table needs the lookahead token.)
3.  Identify, in your question 1 table, the exact row where the tree for `2 * 3` finished forming.  Bottom-up means the subtree existed before its parent; point to the evidence.
4.  Recursive descent could not run `E -> E + T`; the LR machine prefers it.  In one sentence each, say where the "memory of the left context" lives in each technique (the call stack versus the explicit stack).

> **Watch out!**  LR parsers read left-to-right but reduce from the right end of the stack; this confuses students about which "direction" they should be thinking.  The key is that a reduction always fires on the *top* of the stack (the rightmost symbols currently seen), not on the leftmost.  "LR" means Left-to-right scan, Rightmost derivation in reverse: the tree you are building is a rightmost derivation discovered backwards, bottom-up.

### Run the Machine

The table above is data.  Below it is wired to a driver of about twenty lines, so you can check the parse you just did by hand against what the algorithm actually does, and watch the precedence decision from row 2 happen in real time.

```python
# The ACTION/GOTO table transcribed EXACTLY from the table above.
#   ("s", n) = shift and go to state n
#   ("r", n) = reduce by production n
#   ("acc",) = accept
PRODUCTIONS = {                   # number: (lhs, length of rhs)
    1: ("E", 3),                  # E -> E + T
    2: ("E", 1),                  # E -> T
    3: ("T", 3),                  # T -> T * F
    4: ("T", 1),                  # T -> F
    5: ("F", 1),                  # F -> num
}
RHS_TEXT = {1: "E + T", 2: "T", 3: "T * F", 4: "F", 5: "num"}

ACTION = {
    (0, "num"): ("s", 4),
    (1, "+"):   ("s", 6),   (1, "$"): ("acc",),
    (2, "*"):   ("s", 7),   (2, "+"): ("r", 2),  (2, "$"): ("r", 2),
    (3, "*"):   ("r", 4),   (3, "+"): ("r", 4),  (3, "$"): ("r", 4),
    (4, "*"):   ("r", 5),   (4, "+"): ("r", 5),  (4, "$"): ("r", 5),
    (6, "num"): ("s", 4),
    (7, "num"): ("s", 4),
    (8, "*"):   ("s", 7),   (8, "+"): ("r", 1),  (8, "$"): ("r", 1),
    (9, "*"):   ("r", 3),   (9, "+"): ("r", 3),  (9, "$"): ("r", 3),
}
GOTO = {
    (0, "E"): 1, (0, "T"): 2, (0, "F"): 3,
    (6, "T"): 8, (6, "F"): 3,
    (7, "F"): 9,
}

def parse(tokens, trace=True):
    tokens = list(tokens) + ["$"]
    states  = [0]          # the state stack
    symbols = []           # the symbol stack, for display
    pos = 0
    step = 0
    if trace:
        print(f"  {'step':>4}  {'stack':<20} {'input':<14} action")
    while True:
        step += 1
        state = states[-1]
        tok   = tokens[pos]
        entry = ACTION.get((state, tok))
        stack_str = " ".join(symbols) or "-"
        input_str = " ".join(tokens[pos:])
        if entry is None:
            if trace:
                print(f"  {step:>4}  {stack_str:<20} {input_str:<14} ERROR: no action for "
                      f"state {state} on {tok!r}")
            return None
        if entry[0] == "acc":
            if trace:
                print(f"  {step:>4}  {stack_str:<20} {input_str:<14} accept")
            return symbols[-1]
        if entry[0] == "s":
            if trace:
                print(f"  {step:>4}  {stack_str:<20} {input_str:<14} shift -> s{entry[1]}")
            symbols.append(tok); states.append(entry[1]); pos += 1
        else:
            n = entry[1]
            lhs, length = PRODUCTIONS[n]
            del states[-length:]
            del symbols[-length:]
            symbols.append(lhs)
            states.append(GOTO[(states[-1], lhs)])
            if trace:
                print(f"  {step:>4}  {stack_str:<20} {input_str:<14} "
                      f"reduce r{n}: {lhs} -> {RHS_TEXT[n]}")

print("=== 2 + 3, the parse worked by hand above ===")
parse(["num", "+", "num"])

print("\n=== 2 * 3 + 4, CTQ 1's parse ===")
parse(["num", "*", "num", "+", "num"])

print("\n=== 2 + 3 * 4: watch state 8 refuse to reduce on '*' ===")
parse(["num", "+", "num", "*", "num"])

print("\n=== And an input the table rejects ===")
parse(["num", "+", "+"])
```
@LIA.eval(`["main.py"]`, `none`, `python3 main.py`)

### Reading the Code

- `ACTION` and `GOTO` are the two tables from the worked example, transcribed with no interpretation added.  The driver never looks at the grammar; it only looks these up.  That is what "table-driven" means, and it is why a generator like yacc can emit these tables and reuse one driver for every language.
- The whole algorithm is four cases: shift, reduce, accept, error.  There is no recursion and no per-nonterminal function, which is the structural opposite of recursive descent.
- The reduce case pops `length` entries from *both* stacks and then consults `GOTO` with the state now on top.  Popping the right number of symbols is the only bookkeeping in the entire parser.
- In the third parse, look for the step where the stack is `E + T` and the input begins with `*`.  The table says `s7`, not reduce, which is precedence happening: reducing there would have built `(2+3)*4`.  That is CTQ 2's answer as a line of output.
- The last parse ends in `ERROR: no action for state ... on '+'`.  A table-driven parser detects an error the instant it reaches an empty cell, which is one of LR's real advantages: errors are found at the earliest possible token.

### Try It Yourself

Use the driver to find where the tree is built, and then break the table on purpose.

```python
PRODUCTIONS = {1: ("E", 3), 2: ("E", 1), 3: ("T", 3), 4: ("T", 1), 5: ("F", 1)}
RHS_TEXT    = {1: "E + T", 2: "T", 3: "T * F", 4: "F", 5: "num"}
ACTION = {
    (0, "num"): ("s", 4),
    (1, "+"):   ("s", 6),   (1, "$"): ("acc",),
    (2, "*"):   ("s", 7),   (2, "+"): ("r", 2),  (2, "$"): ("r", 2),
    (3, "*"):   ("r", 4),   (3, "+"): ("r", 4),  (3, "$"): ("r", 4),
    (4, "*"):   ("r", 5),   (4, "+"): ("r", 5),  (4, "$"): ("r", 5),
    (6, "num"): ("s", 4),
    (7, "num"): ("s", 4),
    (8, "*"):   ("s", 7),   (8, "+"): ("r", 1),  (8, "$"): ("r", 1),
    (9, "*"):   ("r", 3),   (9, "+"): ("r", 3),  (9, "$"): ("r", 3),
}
GOTO = {(0,"E"):1, (0,"T"):2, (0,"F"):3, (6,"T"):8, (6,"F"):3, (7,"F"):9}

def parse(tokens, action=ACTION, quiet=False):
    tokens = list(tokens) + ["$"]
    states, symbols, pos, reductions = [0], [], 0, []
    while True:
        entry = action.get((states[-1], tokens[pos]))
        if entry is None:
            if not quiet: print(f"    ERROR at {tokens[pos]!r}")
            return None, reductions
        if entry[0] == "acc":
            return symbols[-1], reductions
        if entry[0] == "s":
            symbols.append(tokens[pos]); states.append(entry[1]); pos += 1
        else:
            lhs, length = PRODUCTIONS[entry[1]]
            reductions.append(RHS_TEXT[entry[1]] + " -> " + lhs)
            del states[-length:]; del symbols[-length:]
            symbols.append(lhs); states.append(GOTO[(states[-1], lhs)])

print("=== The reduction sequence IS the derivation, backwards ===")
for src in [["num","+","num","*","num"], ["num","*","num","+","num"]]:
    _, reds = parse(src)
    print(f"  {' '.join(src)}")
    for i, r in enumerate(reds, 1):
        print(f"      {i}. {r}")
    print()

# TODO 1: in the first parse, which reduction number built the subtree for
#         3 * 4? Bottom-up means the subtree existed before its parent --
#         point at the line that proves it. (This is CTQ 3.)

# TODO 2: break precedence on purpose. Copy ACTION, change (8, "*") from
#         ("s", 7) to ("r", 1), and reparse "num + num * num". What tree
#         does the reduction sequence describe now, and which arithmetic
#         answer would it produce?

# TODO 3: that one cell is where * binds tighter than +. Compare with
#         recursive descent: where does the same fact live there?
```
@LIA.eval(`["main.py"]`, `none`, `python3 main.py`)

Expected output: the two reduction sequences, each ending in `T -> E`.  For TODO 2, changing that single cell turns `2 + 3 * 4` into the tree for `(2 + 3) * 4`, which is the same wrong answer the ambiguous grammar produced back in *Derivations, Parse Trees, Ambiguity, and Precedence*.

---

# Part II: Conflicts and Choices

A parsing table cell with two entries is a conflict: the grammar gave the parser two equally valid moves at the same point, and it cannot choose without additional information.  Conflicts are not crashes; they are diagnostic messages telling you that the grammar (or the language) is ambiguous or requires more lookahead than the parser class provides.

## 2.  When the Table Cannot Decide

A grammar produces a conflict when some table cell needs two actions.  A **shift-reduce conflict** arises when the parser could either extend the current phrase or close it (the dangling else is the canonical case: shift the `else` or reduce the bare `if`); a **reduce-reduce conflict** arises when two completed productions match the same stack top.  Conflicts are the LR world's version of the descent world's non-LL(1) alternations: a sign the grammar (or the language) is ambiguous or needs more lookahead.  Tools resolve some conflicts with declared precedence; the rest demand grammar surgery, the same surgery skills you built in the ambiguity module.

A parser generator reports a shift-reduce conflict on the team's grammar at the token `else`.  The most informative first response is:

[( )] Increase the parser's stack size
[( )] Switch to recursive descent, which has no tables
[(X)] Recognize the dangling else ambiguity and either restructure the grammar or accept the tool's default of shifting, documenting the choice
[( )] Delete the else construct

> **Watch out!**  A conflict in the parsing table (whether LL(1) or LR) means the grammar is not in the class the table was built for.  For LL(1) tables specifically, any cell with more than one entry means the grammar is not LL(1) and the table-driven parser is undefined for that grammar.  The right response is always to diagnose *why* the conflict arose (ambiguity? left recursion? missing factoring?) rather than picking an entry arbitrarily.

---

## Model 2: Technology Selection

Now that you have seen how the machinery works, the practical question is whether to build it yourself or let a generator do it.  This is not a trivial decision: the choice affects error messages, grammar expressiveness, and how much work it takes to change the language later.  Real-world production compilers have landed on both sides of this debate.

Your project must choose its parsing technology; most teams hand-write recursive descent, and you should know what you are declining.

Your project grammar contains the left-recursive list rule `args -> args "," expr | expr`.  Which statement about the two technologies is correct?

[( )] Both require rewriting the rule before they can parse it
[(X)] A generated LR parser handles the rule as written; a hand-written recursive descent parser requires rewriting it as `args -> expr { "," expr }`
[( )] Recursive descent handles it as written; LR requires the rewrite
[( )] Neither technology can parse comma-separated lists

### Critical Thinking Questions

5.  Compare hand-written descent versus a generated LR parser on four axes: error message quality you control, grammar restrictions (left recursion, factoring), effort to change the grammar mid-project, and what you learn by writing it.  Fill the matrix as a team.
6.  Python's own parser moved from a hand-written LL variant to a PEG-based generator in 2020 after decades; major C compilers use hand-written descent for error-message control.  What do these production choices suggest about the matrix you just filled?
7.  Write your team's one-paragraph technology decision for the project, citing two cells of your matrix.  File it with your design documents.

---

# Part III: Runnable Models

## Model 3: FIRST and FOLLOW Sets

Before you can build a parse table, you need to know two things about every nonterminal: what tokens can start a phrase derived from it (FIRST), and what tokens can legally appear right after it in any sentential form (FOLLOW).  The code below computes both sets automatically for a grammar you provide; run it, then use the output to answer the questions that follow.

**FIRST(A)** is the set of terminals that can begin any string derived from A. **FOLLOW(A)** is the set of terminals (and `$`) that can appear immediately after A in some sentential form.  Together they power LL(1) table construction: the parse table entry for nonterminal A on lookahead token t is the production to use when t ∈ FIRST(RHS), or when ε is derivable from RHS and t ∈ FOLLOW(A).

```python
# Compute FIRST and FOLLOW sets for a context-free grammar.
# Grammar is represented as a dict: NT -> list of productions (lists of symbols).
# Use '' (empty string) to represent epsilon.

EPSILON = ''
EOF     = '$'

def compute_first(grammar):
    """
    Compute FIRST(X) for every symbol X in the grammar.
    FIRST(terminal) = {terminal}
    FIRST(NT)       = union over all productions of FIRST of each RHS
    """
    first = {}
    # Initialize: terminals map to themselves, NTs start empty
    all_symbols = set(grammar.keys())
    for nt in grammar:
        first[nt] = set()

    changed = True
    while changed:
        changed = False
        for nt, productions in grammar.items():
            for prod in productions:
                if prod == [EPSILON]:
                    if EPSILON not in first[nt]:
                        first[nt].add(EPSILON)
                        changed = True
                    continue
                for sym in prod:
                    if sym not in all_symbols:
                        # sym is a terminal
                        if sym not in first[nt]:
                            first[nt].add(sym)
                            changed = True
                        break   # terminals don't derive epsilon
                    else:
                        # sym is a nonterminal: add FIRST(sym) - {epsilon}
                        new = first[sym] - {EPSILON}
                        if not new.issubset(first[nt]):
                            first[nt] |= new
                            changed = True
                        if EPSILON not in first[sym]:
                            break   # can't skip past sym
                else:
                    # All symbols can derive epsilon
                    if EPSILON not in first[nt]:
                        first[nt].add(EPSILON)
                        changed = True
    return first

def first_of_string(symbols, first_sets, grammar_nts):
    """Compute FIRST of a sequence of symbols."""
    result = set()
    for sym in symbols:
        if sym == EPSILON:
            result.add(EPSILON)
            break
        if sym not in grammar_nts:
            result.add(sym)   # terminal
            break
        result |= (first_sets[sym] - {EPSILON})
        if EPSILON not in first_sets[sym]:
            break
    else:
        result.add(EPSILON)
    return result

def compute_follow(grammar, first):
    """Compute FOLLOW(A) for each nonterminal A."""
    nts = set(grammar.keys())
    start = next(iter(grammar))   # first NT is the start symbol
    follow = {nt: set() for nt in nts}
    follow[start].add(EOF)

    changed = True
    while changed:
        changed = False
        for nt, productions in grammar.items():
            for prod in productions:
                if prod == [EPSILON]:
                    continue
                for i, sym in enumerate(prod):
                    if sym not in nts:
                        continue   # only track NTs
                    beta = prod[i+1:]
                    first_beta = first_of_string(beta, first, nts) if beta else {EPSILON}
                    # Add FIRST(beta) - {epsilon} to FOLLOW(sym)
                    new_terms = first_beta - {EPSILON}
                    if not new_terms.issubset(follow[sym]):
                        follow[sym] |= new_terms
                        changed = True
                    # If epsilon in FIRST(beta), add FOLLOW(nt) to FOLLOW(sym)
                    if EPSILON in first_beta:
                        if not follow[nt].issubset(follow[sym]):
                            follow[sym] |= follow[nt]
                            changed = True
    return follow

# Grammar: E -> E + T | T,  T -> T * F | F,  F -> ( E ) | num
# (Left-recursive - fine for LR; LL(1) needs a rewritten version)
# LL(1)-compatible version:
#   E  -> T E'
#   E' -> + T E' | epsilon
#   T  -> F T'
#   T' -> * F T' | epsilon
#   F  -> ( E ) | num

grammar = {
    'E':  [['T', "E'"]],
    "E'": [['+', 'T', "E'"], [EPSILON]],
    'T':  [['F', "T'"]],
    "T'": [['*', 'F', "T'"], [EPSILON]],
    'F':  [['(', 'E', ')'], ['num']],
}

first  = compute_first(grammar)
follow = compute_follow(grammar, first)

print("FIRST sets:")
for nt in grammar:
    symbols = sorted(x if x else 'ε' for x in first[nt])
    print(f"  FIRST({nt:<4}) = " + "{ " + ", ".join(symbols) + " }")

print()
print("FOLLOW sets:")
for nt in grammar:
    symbols = sorted(follow[nt])
    print(f"  FOLLOW({nt:<4}) = " + "{ " + ", ".join(symbols) + " }")
```
@LIA.eval(`["main.py"]`, `none`, `python3 main.py`)

### Critical Thinking Questions

8. `FIRST(E')` contains `+` and `ε`.  Explain *why* `ε` is in `FIRST(E')` by tracing the grammar rule for `E'`.  Then explain what a parser does when it sees a lookahead not in `FIRST(E')`: does it error immediately, or consult `FOLLOW`?
9. `FOLLOW(E')` should equal `FOLLOW(E)`.  Verify this from the printed output and justify it from the grammar rule `E -> T E'`: when does the parser need to know what follows `E'`?
10.  The original left-recursive grammar (`E -> E + T | T`) cannot be used directly for LL(1) parsing.  Explain why, in terms of what the parser would have to do on the first token when predicting `E`.
11.  Add a new production `E' -> - T E'` (subtraction) to the grammar dict and re-run.  Predict before running: which FIRST set changes, which FOLLOW sets change, and whether an LL(1) conflict arises.

> **Watch out!**  When a nonterminal A can derive ε (i.e., ε ∈ FIRST(A)), computing the parse table for any production that contains A requires you to also consult FOLLOW(A), not just FIRST(A).  Students commonly skip this step and then wonder why the table rejects valid inputs.  The rule is: if ε ∈ FIRST(α) for production `B -> α`, add that production to `table[B][t]` for every `t ∈ FOLLOW(B)` as well.

## Model: From Source to Running Program, Compile, Link, Load

Today's generated parsers are one station on an industrial assembly line, and this ten-minute model walks the rest of it.  Your interpreter runs programs directly from the tree; a compiled language like C takes three more steps between source text and running behavior:

1.  **Compile.**  Each source file is translated *separately* into an **object file**: machine code plus a **symbol table** listing the names it defines (`main`, `parse_expr`) and the names it uses but cannot find (`printf`, `yylex`).  An object file is a puzzle piece with labeled tabs and labeled holes.
2.  **Link.**  The **linker** fits the pieces together: every "uses" hole must be filled by exactly one "defines" tab, drawn from your other object files or from libraries.  Two definitions of the same name is a *duplicate symbol* error; zero is the famous *undefined reference*.  **Static linking** copies library code into the executable; **dynamic linking** leaves a note to find it later.
3.  **Load.**  When you run the program, the **loader** places the executable into memory, resolves the dynamic-library notes against `.so`/`.dll` files on the system, and jumps to the entry point.  Only now does behavior exist.

The mini-notation scaffold you can build with flex and bison goes through exactly this pipeline: `flex` and `bison` generate C, the C compiler makes object files, the linker joins them with the C library, and the loader runs the result.

**CTQ (teams, 3 minutes):** Your interpreter reports an undefined variable *while the program runs*; a C program reports an undefined function *before it ever runs*.  Which of the three stations above catches the C error, and what does that tell you about when each language *binds names*?

    [[?]] Hint: the error message "undefined reference to `foo`" comes from the tool that matches tabs to holes.

Which statement about the pipeline is correct?

- [( )] The compiler must see the whole program at once, which is why C builds are slow
- [(X)] Each file compiles separately; the linker is the first station that sees the whole program's names together
- [( )] The loader recompiles the program each time it runs
- [( )] Static and dynamic linking differ only in file size, never in behavior

> **Going deeper:** the full story (object-file formats, symbol tables you can inspect with `nm`, linker maps, and dynamic loading) is the [From Source to Executable: Compiling, Linking, and the ELF Format](https://www.billmongan.com/Ursinus-CS374-Fall2026/Tutorials/CompilingAndLinking) tutorial.

---

**In-class work stops here.**  Everything below is homework and going-deeper material: attempt the exercises before the related assignment.

## Model 4 (At Home): LL(1) Parse Table Construction and Table-Driven Parser

Armed with FIRST and FOLLOW, building the LL(1) table is a purely mechanical process: iterate over every production, look at what tokens can start it, and fill in the corresponding table cells.  The table-driven parser then replaces the call stack of recursive descent with an explicit stack and a loop, same logic, different bookkeeping.

With FIRST and FOLLOW sets in hand, the LL(1) parse table is mechanical: for each production `A -> α`, add it to table[A][t] for every `t ∈ FIRST(α) - {ε}`, and for every `t ∈ FOLLOW(A)` if `ε ∈ FIRST(α)`.  A conflict (two entries in one cell) means the grammar is not LL(1).

```python
# Build the LL(1) parse table and run a table-driven LL(1) parser.

EPSILON = ''
EOF     = '$'

# Reuse the grammar and set-computation functions from the previous cell.
def compute_first(grammar):
    first = {nt: set() for nt in grammar}
    nts = set(grammar.keys())
    changed = True
    while changed:
        changed = False
        for nt, productions in grammar.items():
            for prod in productions:
                if prod == [EPSILON]:
                    if EPSILON not in first[nt]:
                        first[nt].add(EPSILON); changed = True
                    continue
                for sym in prod:
                    if sym not in nts:
                        if sym not in first[nt]:
                            first[nt].add(sym); changed = True
                        break
                    else:
                        new = first[sym] - {EPSILON}
                        if not new.issubset(first[nt]):
                            first[nt] |= new; changed = True
                        if EPSILON not in first[sym]:
                            break
                else:
                    if EPSILON not in first[nt]:
                        first[nt].add(EPSILON); changed = True
    return first

def first_of_string(symbols, first_sets, nts):
    result = set()
    for sym in symbols:
        if sym == EPSILON:
            result.add(EPSILON); break
        if sym not in nts:
            result.add(sym); break
        result |= (first_sets[sym] - {EPSILON})
        if EPSILON not in first_sets[sym]:
            break
    else:
        result.add(EPSILON)
    return result

def compute_follow(grammar, first):
    nts = set(grammar.keys())
    start = next(iter(grammar))
    follow = {nt: set() for nt in nts}
    follow[start].add(EOF)
    changed = True
    while changed:
        changed = False
        for nt, productions in grammar.items():
            for prod in productions:
                if prod == [EPSILON]: continue
                for i, sym in enumerate(prod):
                    if sym not in nts: continue
                    beta = prod[i+1:]
                    fb = first_of_string(beta, first, nts) if beta else {EPSILON}
                    new = fb - {EPSILON}
                    if not new.issubset(follow[sym]):
                        follow[sym] |= new; changed = True
                    if EPSILON in fb:
                        if not follow[nt].issubset(follow[sym]):
                            follow[sym] |= follow[nt]; changed = True
    return follow

def build_ll1_table(grammar, first, follow):
    """
    Build the LL(1) parse table.
    Returns (table, conflicts) where table[NT][terminal] = production (list),
    and conflicts is a list of (NT, terminal) cells with multiple entries.
    """
    nts = set(grammar.keys())
    table = {nt: {} for nt in nts}
    conflicts = []

    for nt, productions in grammar.items():
        for prod in productions:
            if prod == [EPSILON]:
                first_alpha = {EPSILON}
            else:
                first_alpha = first_of_string(prod, first, nts)

            for t in first_alpha - {EPSILON}:
                if t in table[nt]:
                    conflicts.append((nt, t, table[nt][t], prod))
                table[nt][t] = prod

            if EPSILON in first_alpha:
                for t in follow[nt]:
                    if t in table[nt]:
                        conflicts.append((nt, t, table[nt][t], [EPSILON]))
                    table[nt][t] = [EPSILON]
    return table, conflicts

def ll1_parse(tokens, grammar, table, start='E'):
    """
    Table-driven LL(1) parser.
    tokens: list of terminal strings, ending with '$'.
    Returns a trace of (stack, input, action) triples.
    """
    nts = set(grammar.keys())
    stack = [EOF, start]
    pos = 0
    trace = []

    while stack:
        top = stack[-1]
        current = tokens[pos] if pos < len(tokens) else EOF
        stack_str = ' '.join(reversed(stack))
        input_str = ' '.join(tokens[pos:])

        if top == EOF and current == EOF:
            trace.append((stack_str, input_str, 'ACCEPT'))
            return trace, True
        elif top == current:
            trace.append((stack_str, input_str, f'match {current!r}'))
            stack.pop()
            pos += 1
        elif top in nts:
            if current in table[top]:
                production = table[top][current]
                prod_str = ' '.join(production) if production != [EPSILON] else 'ε'
                trace.append((stack_str, input_str, f'{top} -> {prod_str}'))
                stack.pop()
                if production != [EPSILON]:
                    for sym in reversed(production):
                        stack.append(sym)
            else:
                trace.append((stack_str, input_str, f'ERROR: no entry for {top} on {current!r}'))
                return trace, False
        else:
            trace.append((stack_str, input_str, f'ERROR: expected {top!r}, got {current!r}'))
            return trace, False

    return trace, False

grammar = {
    'E':  [['T', "E'"]],
    "E'": [['+', 'T', "E'"], [EPSILON]],
    'T':  [['F', "T'"]],
    "T'": [['*', 'F', "T'"], [EPSILON]],
    'F':  [['(', 'E', ')'], ['num']],
}

first  = compute_first(grammar)
follow = compute_follow(grammar, first)
table, conflicts = build_ll1_table(grammar, first, follow)

print("LL(1) Parse Table (non-empty cells):")
for nt in grammar:
    for term, prod in sorted(table[nt].items()):
        prod_str = ' '.join(prod) if prod != [EPSILON] else 'ε'
        print(f"  table[{nt}][{term!r}] = {prod_str}")

if conflicts:
    print("\nCONFLICTS (grammar is NOT LL(1)):")
    for c in conflicts:
        print(f"  {c}")
else:
    print("\nNo conflicts - grammar is LL(1).")

# Run the parser on 'num + num * num $'
tokens_input = ['num', '+', 'num', '*', 'num', '$']
print(f"\nParsing: {' '.join(tokens_input[:-1])}")
print(f"{'Stack':<35} {'Input':<25} Action")
print("-" * 75)
trace, accepted = ll1_parse(tokens_input, grammar, table)
for stack, inp, action in trace:
    print(f"{stack:<35} {inp:<25} {action}")
print(f"\nResult: {'ACCEPTED' if accepted else 'REJECTED'}")
```
@LIA.eval(`["main.py"]`, `none`, `python3 main.py`)

### Critical Thinking Questions

12.  The table cell `table['E'']['num']` is empty (no entry).  Look at the FOLLOW set of `E'` and explain: what action should the parser take when the stack top is `E'` and the lookahead is something in `FOLLOW(E')` but not `FIRST(E')`?
13.  Trace the parse of `num + num * num` by hand using the printed table before running; predict the first five rows of the trace.  After running, compare with your prediction and identify any step you got wrong.
14.  An LL(1) grammar has *at most one* entry per table cell.  If you added the production `E' -> - T E'` to the grammar, which cell would now have two entries, and what conflict type would that be?
15.  The table-driven parser and a recursive-descent parser for the same LL(1) grammar compute *identical* derivations.  The table version uses an explicit stack while descent uses the call stack.  Identify one practical engineering advantage of each approach.

---

## Model 5 (At Home): Shift-Reduce Conflicts Explained

You have seen what a conflict is in the abstract; now see concrete examples.  The code below simulates two classic conflict scenarios, the dangling else (shift-reduce) and indistinguishable nonterminals (reduce-reduce), and shows how declared operator precedence can resolve the first kind without restructuring the grammar.

A **shift-reduce conflict** occurs when the LR parser, in some configuration (stack + lookahead), can either (a) shift the lookahead token onto the stack, or (b) reduce the stack top using a completed production.  The canonical example is the **dangling else**, but conflicts arise whenever a grammar is ambiguous or requires more than the available lookahead.

```python
# Illustrate shift-reduce and reduce-reduce conflicts by simulating
# a simplified LR(0) conflict detector on small grammars.

def find_lr0_conflicts(grammar_str):
    """
    Very simplified LR(0) conflict detector.
    grammar_str: list of productions as strings like "E -> E + T"
    We look for grammars where the same RHS suffix appears in both
    a 'can reduce' and a 'can shift' context.
    
    This is a pedagogical simulator, not a full LR table builder.
    It demonstrates the CONCEPT of conflicts, not full LR(0) construction.
    """
    productions = []
    for line in grammar_str:
        lhs, rhs_str = line.split(' -> ')
        for rhs in rhs_str.split(' | '):
            productions.append((lhs.strip(), rhs.strip().split()))

    print("Productions:")
    for i, (lhs, rhs) in enumerate(productions):
        print(f"  [{i}] {lhs} -> {' '.join(rhs)}")
    print()
    return productions

# Dangling else grammar (ambiguous)
print("=== Dangling Else Grammar (ambiguous) ===")
dangling_else = [
    "S -> if E then S",
    "S -> if E then S else S",
    "S -> other",
    "E -> cond",
]
prods = find_lr0_conflicts(dangling_else)

print("Configuration demonstrating the conflict:")
print("  Stack: ... if E then S")
print("  Input: else ...")
print()
print("  Option 1: REDUCE using [S -> if E then S]")
print("            => The 'else' will attach to an outer 'if' (if one exists)")
print()
print("  Option 2: SHIFT 'else'")
print("            => The 'else' will attach to the INNER 'if' (nearest-if rule)")
print()
print("  Convention: shift wins (YACC/Bison default) = nearest 'if' binding.")
print("  This is the RIGHT behavior for most languages but requires a CHOICE,")
print("  meaning the grammar is AMBIGUOUS.")
print()

# Reduce-reduce conflict grammar
print("=== Reduce-Reduce Conflict Grammar ===")
rr_grammar = [
    "S -> A c",
    "S -> B c",
    "A -> a b",
    "B -> a b",
]
find_lr0_conflicts(rr_grammar)

print("Configuration demonstrating the conflict:")
print("  Stack: ... a b")
print("  Input: c ...")
print()
print("  Option 1: REDUCE using [A -> a b]")
print("  Option 2: REDUCE using [B -> a b]")
print()
print("  The parser cannot distinguish A from B using only 'a b' on the stack!")
print("  This grammar is ambiguous; A and B are indistinguishable.")
print("  Fix: merge A and B into a single nonterminal, or change their RHS.")
print()

# Demonstrate precedence as conflict resolution
print("=== Precedence as Conflict Resolution ===")
print("""
Grammar:  E -> E + E | E * E | num   (ambiguous)

Config 1:  Stack: E + E   Input: + ...
  Conflict: reduce [E -> E + E]  OR  shift '+'
  Resolution via precedence: both '+' have equal precedence, LEFT assoc
  => REDUCE (left associativity: 1+2+3 = (1+2)+3)

Config 2:  Stack: E + E   Input: * ...
  Conflict: reduce [E -> E + E]  OR  shift '*'
  Resolution via precedence: '*' has higher precedence than '+'
  => SHIFT (let '*' bind more tightly: 1+2*3 = 1+(2*3))

Declared precedence rules in yacc/bison translate directly into
conflict-resolution entries in the parse table, replacing ambiguity
with a documented, predictable choice.
""")

print("=== Summary of Conflict Types ===")
conflicts = [
    ("Shift-Reduce", "Can extend OR close the current phrase",
     "Dangling else, operator precedence",
     "Declare precedence/associativity, or restructure grammar"),
    ("Reduce-Reduce", "Two completed productions match the stack top",
     "Indistinguishable nonterminals, over-general grammar",
     "Merge nonterminals, add distinguishing tokens, use LR(1)"),
]
print(f"{'Type':<18} {'Cause':<40} {'Example':<30} Fix")
print("-" * 120)
for ctype, cause, example, fix in conflicts:
    print(f"{ctype:<18} {cause:<40} {example:<30} {fix}")
```
@LIA.eval(`["main.py"]`, `none`, `python3 main.py`)

### Critical Thinking Questions

16.  In the dangling-else conflict, both shift and reduce produce *syntactically valid* parse trees.  They differ only in *meaning*.  Write the two ASTs for `if a then if b then s1 else s2` corresponding to each choice, and state which one matches Python's behavior.
17.  The reduce-reduce conflict arises because `A -> a b` and `B -> a b` have *identical* right-hand sides.  Explain why an LR(1) parser (which uses one token of lookahead *after* a reduction, not just before) still cannot resolve this conflict without grammar changes.
18.  Declared precedence (yacc's `%left`, `%right`, `%nonassoc`) resolves shift-reduce conflicts by turning the ambiguous grammar into a deterministic one *without* restructuring it.  Describe the trade-off: what is gained (writability of the grammar spec) and what is lost (clarity of the formal grammar)?
19.  Your CS374 recursive-descent parser handles precedence via *grammar structure* (the E/T/F ladder).  An LR parser can handle it via *declarations*.  Which approach would be easier to modify if your language added a new operator with a precedence between `+` and `*`?  Justify by describing the required changes in each approach.

---

# Check Your Understanding

"Table-driven" parsing means:

[(X)] One fixed driver algorithm reads ACTION/GOTO tables that a generator produced from the grammar
[( )] The parser consults a precedence table at each operator
[( )] The grammar is stored as a table instead of as rules
[( )] Each nonterminal has a table of its alternatives

---

In the parse of `2 + 3 * 4`, the stack reaches `E + T` with `*` next and the table says shift, not reduce. That cell is where:

[(X)] `*` binds tighter than `+`; reducing there would have built `(2+3)*4`
[( )] The parser recovers from an error
[( )] The grammar's ambiguity is detected
[( )] Associativity is decided

---

A shift-reduce conflict means:

[(X)] Some table cell has both a shift and a reduce available, so the grammar is not LR(1) as written
[( )] The input contains a syntax error
[( )] The stack and the input disagree
[( )] Two productions have the same right-hand side

---

Recursive descent cannot use `E -> E + T` but an LR parser prefers it. The difference is where the left context is remembered:

[(X)] Recursive descent keeps it on the call stack, which left recursion never gets to build; LR keeps it on an explicit stack it has already filled
[( )] LR parsers have a larger recursion limit
[( )] Recursive descent reads right-to-left
[( )] LR parsers rewrite the grammar internally

---

An LR parser reports an error the moment it reaches an empty table cell. That gives it:

[(X)] The viable-prefix property: it never shifts a token that cannot start a legal continuation
[( )] Faster parsing on legal input
[( )] Better error messages by default
[( )] The ability to parse ambiguous grammars

---

## 3.  Exercises

1.  *Full trace.*  Produce the complete shift-reduce table for `( 2 + 3 ) * 4`, marking the row where each reduction's subtree completes.  Compare the final tree with the AST your descent parser builds for the same input: they must match.
2.  *Conflict construction.*  Write a three-rule grammar that has a reduce-reduce conflict, demonstrate the conflicting configuration with a concrete stack and lookahead, and repair the grammar.
3.  *Dangling else, LR edition.*  Show the exact stack and input configuration where the dangling else forces the shift-or-reduce choice, and state which choice yields the conventional nearest-if binding.
4.  *Generator field trip.*  (Optional, recommended.)  Feed the ladder grammar to an online ANTLR or lark playground, parse `2 + 3 * 4`, and compare the produced tree with your hand trace.  One paragraph: what did the tool hide, and was hiding it good?

---

## Practice: Allison, Ch. 5: Pushdown Automata (Readings 5.1 and 5.2)

These exercises cover pushdown automata (PDAs) and their relationship to context-free grammars.  PDAs are the theoretical model underlying LR and LL parsers; understanding them deepens your intuition for shift-reduce parsing.

> *Exercises adapted from topics covered in *Foundations of Computing* by Chuck Allison (Fresh Sources, Inc.), used under the [MIT License](https://github.com/chuckallison/foundations-of-computing/blob/main/LICENSE).*

A pushdown automaton (PDA) differs from a finite automaton primarily because:

[( )] It reads input from right to left
[( )] It has more than one start state
[(X)] It has access to an unbounded stack in addition to finite states
[( )] It can move without reading input (epsilon transitions only)

The language a^n b^n (equal numbers of a's then b's) is recognized by a PDA because:

[( )] It is a regular language, recognizable by any finite automaton
[(X)] The PDA pushes 'a's onto the stack and pops one for each 'b', checking balance
[( )] The PDA uses its states (not the stack) to count the a's
[( )] The stack stores the entire input before processing begins

The connection between PDAs and context-free grammars is:

[( )] Every PDA can be converted to a regular expression
[( )] PDAs recognize only a subset of context-free languages
[(X)] PDAs and CFGs recognize exactly the same class of languages (the context-free languages)
[( )] CFGs are strictly more powerful than PDAs

In an LR(0) shift-reduce parser, the stack corresponds to:

[( )] The remaining unconsumed input
[(X)] The portion of the input already read, organized as a pushdown automaton's stack contents
[( )] The set of all parse trees built so far
[( )] The lookahead buffer

1.  *PDA design.*  Design a PDA (state diagram or transition table) that accepts the language $\{a^n b^n \mid n \geq 0\}$. Your PDA should: push `a` onto the stack on input `a`, pop one stack symbol for each `b`, and accept by empty stack.  Trace it on `aabb` and `aaabbb`.

2.  *PDA for balanced parentheses.*  Design a PDA for the language of properly nested parentheses (e.g., `()`, `(())`, `(()())`).  Trace it on `(())` and on the malformed input `(()`.

3.  *PDA to CFG.* The language $\{ww^R \mid w \in \{a,b\}^*\}$ (strings that are palindromes) is context-free.  Write a CFG for it, then describe how a PDA would recognize it.  What is the key operation the PDA performs at the midpoint?

4.  *Shift-reduce as PDA.* A shift-reduce parser is a PDA in disguise.  For the simple grammar `E -> E + T | T` and `T -> id`, trace the shift-reduce actions on input `id + id`:
   - List each action (SHIFT or REDUCE) and the stack contents after each step
   - Identify the two "PDA states" (reading input vs. reducing)
   - Explain what is pushed and popped at each reduction step

5.  *Grammar to PDA.* Given a context-free grammar, there is a standard algorithm to construct a PDA that recognizes the same language (the "top-down PDA").  Apply it to the grammar `S -> aSb | ε`.  Write out the PDA's transition rules and trace it on `aabb`.

---

## Answer Key: Model 1, CTQ 1, the full parse of `2 * 3 + 4`

Attempt this as a team **before** you read it.  Fourteen rows, using the ACTION/GOTO table you built above.  Stack entries are written `symbol(state)`; state 0 is always at the bottom.

| # | Stack | Input | Action |
|---|-------|-------|--------|
| 1 | `0` | `2 * 3 + 4 $` | shift 4 |
| 2 | `0 2(4)` | `* 3 + 4 $` | reduce `F -> num`, goto 3 |
| 3 | `0 F(3)` | `* 3 + 4 $` | reduce `T -> F`, goto 2 |
| 4 | `0 T(2)` | `* 3 + 4 $` | **shift 7** (row 2, column `*`) |
| 5 | `0 T(2) *(7)` | `3 + 4 $` | shift 4 |
| 6 | `0 T(2) *(7) 3(4)` | `+ 4 $` | reduce `F -> num`, goto 9 |
| 7 | `0 T(2) *(7) F(9)` | `+ 4 $` | reduce `T -> T * F`, goto 2 |
| 8 | `0 T(2)` | `+ 4 $` | reduce `E -> T`, goto 1 |
| 9 | `0 E(1)` | `+ 4 $` | shift 6 |
| 10 | `0 E(1) +(6)` | `4 $` | shift 4 |
| 11 | `0 E(1) +(6) 4(4)` | `$` | reduce `F -> num`, goto 3 |
| 12 | `0 E(1) +(6) F(3)` | `$` | reduce `T -> F`, goto 8 |
| 13 | `0 E(1) +(6) T(8)` | `$` | reduce `E -> E + T`, goto 1 |
| 14 | `0 E(1)` | `$` | **accept** |

**CTQ 3 answered from this table:** the subtree for `2 * 3` finishes at **row 7**, where `T -> T * F` reduces three stack symbols into one `T`.  Everything above row 7 is that subtree being built; everything below is it being used.  The parent `E -> E + T` does not reduce until row 13, six rows *after* its own child existed.  That is what "bottom-up" means, and the row numbers are the evidence.

**Contrast with row 4.**  At `0 T(2)` with `*` next, the parser shifts instead of reducing `E -> T`.  Had it reduced, `2` would have become a complete `E` and the `*` would have had to attach to it, yielding `(2) * (3 + 4)`.  Precedence is decided in exactly one table cell.

---

## Reflection Prompt

In your notebook: the LR table is compiled knowledge, decisions made once, ahead of time, then executed mindlessly and fast, while your descent parser decides everything live.  Where in your own work do you prefer compiled-ahead decisions (checklists, routines) versus live judgment, and what does each cost?

---

## 4.  Further Reading

- Douglas Thain.  *Introduction to Compilers and Language Design*, Chapter 5 (LR parsing).
- Aho, Lam, Sethi, Ullman.  *Compilers*, sections 4.5 through 4.7, for table construction we executed but did not build.
- Donald Knuth.  "On the Translation of Languages from Left to Right."  (1965).  Where LR was born.
- [Flex and Bison from Zero to a Working Language](https://www.billmongan.com/Ursinus-CS374-Fall2026/Tutorials/FlexAndBison): installing Flex and Bison, a complete `.l`/`.y` walkthrough of a calculator language with variables, and an appendix on LR(0) item-set construction and how Yacc builds and resolves its parse tables.  The ready-to-build mini-notation scaffold is in the course examples at [files/examples/mininote/](https://www.billmongan.com/Ursinus-CS374-Fall2026/files/examples/mininote/).
- [Building a Bytecode VM for Mini](https://www.billmongan.com/Ursinus-CS374-Fall2026/Tutorials/BytecodeVM): compiling expressions to bytecode and executing them on a stack machine.
- [From Source to Executable: Compiling, Linking, and the ELF Format](https://www.billmongan.com/Ursinus-CS374-Fall2026/Tutorials/CompilingAndLinking): object files, symbol tables, static and dynamic linking, loaders, and the path from source to executable.

---

Up next: the *Tree-Walking Interpretation* activity finally gives parsed programs their meaning; the front end is complete.
