# Table-Driven and LR Parsing
<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://github.com/BillJr99/Ursinus-CS374-Fall2026/blob/gh-pages/_pages/Activities/liascript-parsertable.md or locally via https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374-Fall2026/gh-pages/_pages/Activities/liascript-parsertable.md

import: https://raw.githubusercontent.com/liascript/CodeRunner/master/README.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

# Table-Driven and LR Parsing

Table-driven parsers — LL(1) and LR — replace moment-to-moment grammar reasoning with a lookup. Think of a parsing table like a GPS route precomputed from every intersection: instead of rethinking the best path each time you reach a fork, you simply consult the table and execute the move it prescribes. The table was built once, offline, from the grammar's FIRST and FOLLOW sets; at parse time all the "thinking" has already been done. This makes table-driven parsers fast, systematic, and amenable to machine generation — which is exactly why industrial parser generators emit them.

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
> - Describe how a recursive-descent parser works — one function per nonterminal, calling itself when it encounters a nonterminal in the production
>
> If any of these feel shaky, revisit the recursive-descent and grammar modules before continuing.

Recursive descent is top-down: it predicts what must come next. The industrial-strength alternative works **bottom-up**: an **LR parser** shifts tokens onto a stack and reduces them to nonterminals when it recognizes a completed right-hand side, driven entirely by a precomputed table. Over two days we learn to *read and execute* this machinery by hand, because parser generators (yacc, bison, ANTLR) emit it, error messages reference it, and the left recursion that broke descent is exactly what LR handles natively. The arc: **shift-reduce intuition $\rightarrow$ executing a parse by hand $\rightarrow$ conflicts $\rightarrow$ when to use which technology**.

---

## Directions and Group Roles

Work in your POGIL team with rotated roles (**Manager**, **Recorder**, **Presenter**, **Reflector**). Consider each model and question individually first, then discuss with your group. The Recorder posts answers to the Class Activity Questions discussion board; the Presenter reports out areas of disagreement or alternative approaches. After class, respond to the reflective prompt individually in your notebook.

---

# Part I: The Shift-Reduce Idea (Day 1)

Recursive descent builds a parse tree from the root downward, predicting what must come next. Shift-reduce parsing does the opposite: it reads tokens left-to-right, stacking them up until it recognizes a completed right-hand side, then collapses that stack into the corresponding nonterminal. The tree grows from the leaves upward, one reduction at a time.

## 1. Bottom-Up in One Picture

**An LR parser maintains a stack and looks at one input token.** At each step it consults a table and performs one of two moves: **shift** (push the next input token onto the stack) or **reduce** (the top of the stack matches some production's right-hand side; pop it and push the production's left-hand nonterminal). Accept when the stack holds exactly the start symbol and the input is exhausted. The parse is a *rightmost derivation discovered in reverse*: the tree grows from the leaves upward, which is why left-recursive rules like `E -> E + T` are not merely tolerable but natural; the parser simply reduces `E + T` to `E` whenever it sees one completed on the stack.

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

---

## Model 1: Drive the Machine

The example above walked through `2 + 3` step by step. Now your team will execute the same algorithm on a slightly more complex input and confront a key decision: when two tokens compete for precedence, the lookahead token is what breaks the tie. The table already encodes that decision — your job here is to discover *why* the lookahead is necessary by watching what goes wrong without it.

### Critical Thinking Questions

1. Execute the shift-reduce parse of `2 * 3 + 4` as a team, producing the full stack-input-action table. The Recorder keeps the official copy; expect 12 to 14 rows.
2. At the configuration stack `E + T`, input `* 4 $` (during a parse of `2 + 3 * 4`), the parser must NOT reduce `E -> E + T` yet. Explain what would go wrong with precedence if it did, and what the parser does instead. (The table encodes this choice; you just discovered why the table needs the lookahead token.)
3. Identify, in your question 1 table, the exact row where the tree for `2 * 3` finished forming. Bottom-up means the subtree existed before its parent; point to the evidence.
4. Recursive descent could not run `E -> E + T`; the LR machine prefers it. In one sentence each, say where the "memory of the left context" lives in each technique (the call stack versus the explicit stack).

> **Watch out!** LR parsers read left-to-right but reduce from the right end of the stack — this confuses students about which "direction" they should be thinking. The key is that a reduction always fires on the *top* of the stack (the rightmost symbols currently seen), not on the leftmost. "LR" means Left-to-right scan, Rightmost derivation in reverse — the tree you are building is a rightmost derivation discovered backwards, bottom-up.

---

# Part II: Conflicts and Choices (Day 2)

A parsing table cell with two entries is a conflict: the grammar gave the parser two equally valid moves at the same point, and it cannot choose without additional information. Conflicts are not crashes — they are diagnostic messages telling you that the grammar (or the language) is ambiguous or requires more lookahead than the parser class provides.

## 2. When the Table Cannot Decide

**A grammar produces a conflict when some table cell needs two actions.** A **shift-reduce conflict** arises when the parser could either extend the current phrase or close it (the dangling else is the canonical case: shift the `else` or reduce the bare `if`); a **reduce-reduce conflict** arises when two completed productions match the same stack top. Conflicts are the LR world's version of the descent world's non-LL(1) alternations: a sign the grammar (or the language) is ambiguous or needs more lookahead. Tools resolve some conflicts with declared precedence; the rest demand grammar surgery, the same surgery skills you built in the ambiguity module.

[[MC]]
A parser generator reports a shift-reduce conflict on the team's grammar at the token `else`. The most informative first response is:
- ( ) Increase the parser's stack size
- ( ) Switch to recursive descent, which has no tables
- (x) Recognize the dangling else ambiguity and either restructure the grammar or accept the tool's default of shifting, documenting the choice
- ( ) Delete the else construct

> **Watch out!** A conflict in the parsing table — whether LL(1) or LR — means the grammar is not in the class the table was built for. For LL(1) tables specifically, any cell with more than one entry means the grammar is not LL(1) and the table-driven parser is undefined for that grammar. The right response is always to diagnose *why* the conflict arose (ambiguity? left recursion? missing factoring?) rather than picking an entry arbitrarily.

---

## Model 2: Technology Selection

Now that you have seen how the machinery works, the practical question is whether to build it yourself or let a generator do it. This is not a trivial decision — the choice affects error messages, grammar expressiveness, and how much work it takes to change the language later. Real-world production compilers have landed on both sides of this debate.

Your project must choose its parsing technology; most teams hand-write recursive descent, and you should know what you are declining.

### Critical Thinking Questions

5. Compare hand-written descent versus a generated LR parser on four axes: error message quality you control, grammar restrictions (left recursion, factoring), effort to change the grammar mid-project, and what you learn by writing it. Fill the matrix as a team.
6. Python's own parser moved from a hand-written LL variant to a PEG-based generator in 2020 after decades; major C compilers use hand-written descent for error-message control. What do these production choices suggest about the matrix you just filled?
7. Write your team's one-paragraph technology decision for the project, citing two cells of your matrix. File it with your design documents.

---

# Part III: Runnable Models

## Model 3: FIRST and FOLLOW Sets

Before you can build a parse table, you need to know two things about every nonterminal: what tokens can start a phrase derived from it (FIRST), and what tokens can legally appear right after it in any sentential form (FOLLOW). The code below computes both sets automatically for a grammar you provide — run it, then use the output to answer the questions that follow.

**FIRST(A)** is the set of terminals that can begin any string derived from A. **FOLLOW(A)** is the set of terminals (and `$`) that can appear immediately after A in some sentential form. Together they power LL(1) table construction: the parse table entry for nonterminal A on lookahead token t is the production to use when t ∈ FIRST(RHS) — or when ε is derivable from RHS and t ∈ FOLLOW(A).

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
# (Left-recursive — fine for LR; LL(1) needs a rewritten version)
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
    print(f"  FIRST({nt:<4}) = {{ {', '.join(symbols)} }}")

print()
print("FOLLOW sets:")
for nt in grammar:
    symbols = sorted(follow[nt])
    print(f"  FOLLOW({nt:<4}) = {{ {', '.join(symbols)} }}")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

### Critical Thinking Questions

8. `FIRST(E')` contains `+` and `ε`. Explain *why* `ε` is in `FIRST(E')` by tracing the grammar rule for `E'`. Then explain what a parser does when it sees a lookahead not in `FIRST(E')` — does it error immediately, or consult `FOLLOW`?
9. `FOLLOW(E')` should equal `FOLLOW(E)`. Verify this from the printed output and justify it from the grammar rule `E -> T E'`: when does the parser need to know what follows `E'`?
10. The original left-recursive grammar (`E -> E + T | T`) cannot be used directly for LL(1) parsing. Explain why, in terms of what the parser would have to do on the first token when predicting `E`.
11. Add a new production `E' -> - T E'` (subtraction) to the grammar dict and re-run. Predict before running: which FIRST set changes, which FOLLOW sets change, and whether an LL(1) conflict arises.

> **Watch out!** When a nonterminal A can derive ε (i.e., ε ∈ FIRST(A)), computing the parse table for any production that contains A requires you to also consult FOLLOW(A) — not just FIRST(A). Students commonly skip this step and then wonder why the table rejects valid inputs. The rule is: if ε ∈ FIRST(α) for production `B -> α`, add that production to `table[B][t]` for every `t ∈ FOLLOW(B)` as well.

---

## Model 4: LL(1) Parse Table Construction and Table-Driven Parser

Armed with FIRST and FOLLOW, building the LL(1) table is a purely mechanical process: iterate over every production, look at what tokens can start it, and fill in the corresponding table cells. The table-driven parser then replaces the call stack of recursive descent with an explicit stack and a loop — same logic, different bookkeeping.

With FIRST and FOLLOW sets in hand, the LL(1) parse table is mechanical: for each production `A -> α`, add it to table[A][t] for every `t ∈ FIRST(α) - {ε}`, and for every `t ∈ FOLLOW(A)` if `ε ∈ FIRST(α)`. A conflict (two entries in one cell) means the grammar is not LL(1).

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
                trace.append((stack_str, input_str, f'{top} → {prod_str}'))
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
    print("\nNo conflicts — grammar is LL(1).")

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
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

### Critical Thinking Questions

12. The table cell `table['E'']['num']` is empty (no entry). Look at the FOLLOW set of `E'` and explain: what action should the parser take when the stack top is `E'` and the lookahead is something in `FOLLOW(E')` but not `FIRST(E')`?
13. Trace the parse of `num + num * num` by hand using the printed table before running — predict the first five rows of the trace. After running, compare with your prediction and identify any step you got wrong.
14. An LL(1) grammar has *at most one* entry per table cell. If you added the production `E' -> - T E'` to the grammar, which cell would now have two entries, and what conflict type would that be?
15. The table-driven parser and a recursive-descent parser for the same LL(1) grammar compute *identical* derivations. The table version uses an explicit stack while descent uses the call stack. Identify one practical engineering advantage of each approach.

---

## Model 5: Shift-Reduce Conflicts Explained

You have seen what a conflict is in the abstract; now see concrete examples. The code below simulates two classic conflict scenarios — the dangling else (shift-reduce) and indistinguishable nonterminals (reduce-reduce) — and shows how declared operator precedence can resolve the first kind without restructuring the grammar.

A **shift-reduce conflict** occurs when the LR parser, in some configuration (stack + lookahead), can either (a) shift the lookahead token onto the stack, or (b) reduce the stack top using a completed production. The canonical example is the **dangling else**, but conflicts arise whenever a grammar is ambiguous or requires more than the available lookahead.

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
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

### Critical Thinking Questions

16. In the dangling-else conflict, both shift and reduce produce *syntactically valid* parse trees. They differ only in *meaning*. Write the two ASTs for `if a then if b then s1 else s2` corresponding to each choice, and state which one matches Python's behavior.
17. The reduce-reduce conflict arises because `A -> a b` and `B -> a b` have *identical* right-hand sides. Explain why an LR(1) parser (which uses one token of lookahead *after* a reduction, not just before) still cannot resolve this conflict without grammar changes.
18. Declared precedence (yacc's `%left`, `%right`, `%nonassoc`) resolves shift-reduce conflicts by turning the ambiguous grammar into a deterministic one *without* restructuring it. Describe the trade-off: what is gained (writability of the grammar spec) and what is lost (clarity of the formal grammar)?
19. Your CS374 recursive-descent parser handles precedence via *grammar structure* (the E/T/F ladder). An LR parser can handle it via *declarations*. Which approach would be easier to modify if your language added a new operator with a precedence between `+` and `*`? Justify by describing the required changes in each approach.

---

## 3. Exercises

1. *Full trace.* Produce the complete shift-reduce table for `( 2 + 3 ) * 4`, marking the row where each reduction's subtree completes. Compare the final tree with the AST your descent parser builds for the same input: they must match.
2. *Conflict construction.* Write a three-rule grammar that has a reduce-reduce conflict, demonstrate the conflicting configuration with a concrete stack and lookahead, and repair the grammar.
3. *Dangling else, LR edition.* Show the exact stack and input configuration where the dangling else forces the shift-or-reduce choice, and state which choice yields the conventional nearest-if binding.
4. *Generator field trip.* (Optional, recommended.) Feed the ladder grammar to an online ANTLR or lark playground, parse `2 + 3 * 4`, and compare the produced tree with your hand trace. One paragraph: what did the tool hide, and was hiding it good?

---

## Reflection Prompt

In your notebook: the LR table is compiled knowledge, decisions made once, ahead of time, then executed mindlessly and fast, while your descent parser decides everything live. Where in your own work do you prefer compiled-ahead decisions (checklists, routines) versus live judgment, and what does each cost?

---

## 4. Further Reading

- Douglas Thain. *Introduction to Compilers and Language Design*, Chapter 5 (LR parsing).
- Aho, Lam, Sethi, Ullman. *Compilers*, sections 4.5 through 4.7, for table construction we executed but did not build.
- Donald Knuth. "On the Translation of Languages from Left to Right." (1965). Where LR was born.
