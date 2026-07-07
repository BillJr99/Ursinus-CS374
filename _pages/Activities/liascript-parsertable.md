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
{% raw %}
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
{% endraw %}
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

## Practice — Allison, Ch. 5: Pushdown Automata (Readings 5.1 and 5.2)

These exercises cover pushdown automata (PDAs) and their relationship to context-free grammars. PDAs are the theoretical model underlying LR and LL parsers; understanding them deepens your intuition for shift-reduce parsing.

> *Exercises adapted from topics covered in *Foundations of Computing* by Chuck Allison (Fresh Sources, Inc.), used under the [MIT License](https://github.com/chuckallison/foundations-of-computing/blob/main/LICENSE).*

[[MC]]
A pushdown automaton (PDA) differs from a finite automaton primarily because:
- ( ) It reads input from right to left
- ( ) It has more than one start state
- (x) It has access to an unbounded stack in addition to finite states
- ( ) It can move without reading input (epsilon transitions only)

[[MC]]
The language a^n b^n (equal numbers of a's then b's) is recognized by a PDA because:
- ( ) It is a regular language, recognizable by any finite automaton
- (x) The PDA pushes 'a's onto the stack and pops one for each 'b', checking balance
- ( ) The PDA uses its states (not the stack) to count the a's
- ( ) The stack stores the entire input before processing begins

[[MC]]
The connection between PDAs and context-free grammars is:
- ( ) Every PDA can be converted to a regular expression
- ( ) PDAs recognize only a subset of context-free languages
- (x) PDAs and CFGs recognize exactly the same class of languages (the context-free languages)
- ( ) CFGs are strictly more powerful than PDAs

[[MC]]
In an LR(0) shift-reduce parser, the stack corresponds to:
- ( ) The remaining unconsumed input
- (x) The portion of the input already read, organized as a pushdown automaton's stack contents
- ( ) The set of all parse trees built so far
- ( ) The lookahead buffer

1. *PDA design.* Design a PDA (state diagram or transition table) that accepts the language $\{a^n b^n \mid n \geq 0\}$. Your PDA should: push `a` onto the stack on input `a`, pop one stack symbol for each `b`, and accept by empty stack. Trace it on `aabb` and `aaabbb`.

2. *PDA for balanced parentheses.* Design a PDA for the language of properly nested parentheses (e.g., `()`, `(())`, `(()())`). Trace it on `(())` and on the malformed input `(()`.

3. *PDA to CFG.* The language $\{ww^R \mid w \in \{a,b\}^*\}$ (strings that are palindromes) is context-free. Write a CFG for it, then describe how a PDA would recognize it. What is the key operation the PDA performs at the midpoint?

4. *Shift-reduce as PDA.* A shift-reduce parser is a PDA in disguise. For the simple grammar `E → E + T | T` and `T → id`, trace the shift-reduce actions on input `id + id`:
   - List each action (SHIFT or REDUCE) and the stack contents after each step
   - Identify the two "PDA states" (reading input vs. reducing)
   - Explain what is pushed and popped at each reduction step

5. *Grammar to PDA.* Given a context-free grammar, there is a standard algorithm to construct a PDA that recognizes the same language (the "top-down PDA"). Apply it to the grammar `S → aSb | ε`. Write out the PDA's transition rules and trace it on `aabb`.

---

## Reflection Prompt

In your notebook: the LR table is compiled knowledge, decisions made once, ahead of time, then executed mindlessly and fast, while your descent parser decides everything live. Where in your own work do you prefer compiled-ahead decisions (checklists, routines) versus live judgment, and what does each cost?

---

## 4. Further Reading

- Douglas Thain. *Introduction to Compilers and Language Design*, Chapter 5 (LR parsing).
- Aho, Lam, Sethi, Ullman. *Compilers*, sections 4.5 through 4.7, for table construction we executed but did not build.
- Donald Knuth. "On the Translation of Languages from Left to Right." (1965). Where LR was born.

## Going Deeper: Scanners and Parsers with Flex and Yacc: Building a Mini-Notation Parser

Flex and Bison are the power tools of language implementation: you describe *what* to recognize — token shapes in a regular expression, grammar rules in BNF — and the framework generates *how* to do it, compiling your specification into a C scanner and an LALR(1) parser without you ever touching a parsing table by hand. This division of labor is the same one used inside production compilers like `gcc` and `clang`: a small, human-readable specification drives a large, machine-generated recognizer. By the end of this module you will have built a working scanner and parser for a real domain-specific language used in live coding music, and you will understand every layer of the pipeline from character stream to abstract syntax tree.

#### Learning Goals

By the end of this activity, you will be able to:

- Write Flex lexer rules using regular expressions and explain how the tool compiles them into a DFA for token recognition
- Write Yacc/Bison grammar productions and semantic actions that construct an AST from recognized tokens
- Explain the two-stage pipeline (character stream → tokens → AST) and justify why each stage requires a different class of automaton
- Define the mini-notation grammar for sequences, groups, repetition, and rests, and trace the parse of a sample pattern string
- Implement a Flex/Bison parser for a domain-specific language and verify correctness by evaluating the resulting AST against expected musical timing output

This module develops **lexical analysis** and **syntax analysis** by building a real scanner and parser, using **flex** and **yacc** (GNU bison), for the **mini-notation** shared by the live coding music languages **TidalCycles** and **Strudel**. We move from **language classes $\rightarrow$ regular expressions and DFAs $\rightarrow$ context-free grammars $\rightarrow$ LALR(1) parsing $\rightarrow$ abstract syntax trees $\rightarrow$ semantics**, so that by the end of the module a string like `bd [sn sn] hh*2 ~` becomes a tree, and that tree becomes a timeline of musical events you can hear in your head, and verify in code.

---

> **Before You Begin** — this module assumes you are comfortable with:
>
> - **Regular expression syntax** — character classes `[a-z]`, quantifiers `*`, `+`, `?`, and alternation `|`; you should be able to read a regex and predict what strings it matches
> - **BNF grammar notation** — writing productions in the form `A → α | β`, identifying terminals and nonterminals, and tracing a derivation step by step
> - **Shift-reduce parsing concepts** — you should understand what it means to shift a token onto the stack, reduce a sequence of stack symbols by a grammar rule, and why conflicts arise; review the LR parsing notes from the earlier module if any of this feels shaky

---

#### 0. Environment & Utilities

This module uses the classic C toolchain for language processing. We need `flex` (a scanner generator), `bison` (a parser generator compatible with the original `yacc`), and a C compiler. The commands below verify the environment; no internet access is required once these tools are installed.

---

#### Code Cell

```bash
# On Debian/Ubuntu (or the course container):
#   sudo apt-get install flex bison gcc
# On macOS with Homebrew:
#   brew install flex bison

flex --version
bison --version
gcc --version

echo "Environment ready."
```

---

#### 1. Why a Music Language Is a Perfect Parsing Target

**Mini-notation is a small external DSL embedded inside a larger host language.** In TidalCycles, the host is Haskell; in Strudel, the host is JavaScript. In both, the string between quotes in an expression such as `sound "bd sn [hh hh] sn"` is not host-language code at all. It is a separate language with its own lexical and syntactic rules, and both systems contain a dedicated parser for it. When you write a mini-notation parser, you are reproducing a component that ships inside real, widely used software, which makes this one of the most honest parsing exercises available to us.

**The language is small enough to master and rich enough to be interesting.** A pattern describes one **cycle** of musical time, conventionally the interval $[0, 1)$. The constructs we will parse in this module are:

| Construct | Example | Informal meaning |
|-----------|---------|------------------|
| Sequence | `bd sn hh` | Divide the cycle evenly among the elements |
| Rest | `~` | Silence occupying one slot |
| Group | `[sn sn]` | A subsequence occupying a single slot |
| Fast | `hh*4` | Repeat the element 4 times within its slot |
| Slow | `bd/2` | Stretch the element across 2 cycles |
| Degrade | `hh?` | Play the element with probability $\tfrac{1}{2}$ |

In the assignment that accompanies this module, you will extend the grammar with alternation `<a b c>`, Euclidean rhythms `bd(3,8)`, and polymeter `{a b, c d e}`.

**Syntax and semantics will be cleanly separated.** The parser's job ends when it produces an **abstract syntax tree (AST)**; a separate evaluator walks that tree and assigns each event a span of musical time. Holding that boundary firmly is the central discipline of this course, and we will see in Section 8 that the evaluator is where the musical meaning lives.

---

#### 2. Where Mini-Notation Sits in the Chomsky Hierarchy

**Tokens are regular; structure is context-free.** Recall the language classes from our earlier modules. The individual tokens of mini-notation, sample names like `bd`, integers like `8`, and single-character operators, are each describable by **regular expressions**, so a finite automaton suffices to recognize them. The bracketing structure is another matter: groups nest arbitrarily, as in `[[bd sn] [hh [cp cp]]]`, and we proved earlier in the course that the language of balanced brackets

$$
L = \{\, [^n\, ]^n : n \geq 0 \,\}
$$

is not regular, by a pumping-lemma argument: a DFA with $k$ states cannot distinguish $[^k$ from $[^{k+j}$ for some $j > 0$, so it must accept some unbalanced string if it accepts all balanced ones. Nesting therefore demands at least a **context-free grammar**, and this division of labor is exactly why the classical pipeline has two stages:

$$
\text{characters} \xrightarrow{\ \text{flex (regular)}\ } \text{tokens} \xrightarrow{\ \text{yacc (context-free)}\ } \text{AST}
$$

**This is the same architecture as every production compiler.** Clang, `javac`, and the Strudel mini-notation parser (written with a parsing expression grammar tool in JavaScript) all separate a lexical layer from a syntactic layer. Within the scope of languages whose tokens are regular and whose structure is context-free, which covers nearly every programming language you will encounter, this two-stage design is the standard engineering decomposition.

[[MC]]
A classmate proposes recognizing the entire mini-notation, including arbitrarily nested groups, with one large regular expression. Which statement best evaluates this proposal?
- ( ) It works, because every finite string is regular and all patterns are finite strings.
- (x) It fails in general, because matching arbitrarily nested brackets requires counting that no finite automaton can perform.
- ( ) It works only if the regular expression engine supports the `*` operator.
- ( ) It fails because regular expressions cannot describe multi-character tokens like `bd`.

---

#### 3. Lexical Analysis: From Regular Expressions to a Scanner

**A flex specification is a list of (pattern, action) pairs.** Flex compiles each regular expression into an NFA via Thompson's construction, merges them, and applies the subset construction to obtain a single DFA, so the generated scanner runs in time $O(n)$ in the input length $n$, touching each character a constant number of times. Two disambiguation rules govern the merged automaton, and you should commit them to memory because they explain almost every surprising scanner behavior you will ever debug:

**Maximal munch.** The scanner always takes the longest match available. Given input `bd2`, the `WORD` rule consumes all three characters rather than stopping at `bd`.

**Rule priority.** Among rules matching the same longest lexeme, the one listed first in the specification wins. If a keyword rule and an identifier rule both match `if`, listing the keyword first makes it a keyword.

> **Watch out!** Flex rules match the *longest* token first, not the *first* rule in the file. If two rules can both match at the current position, Flex always takes whichever produces the longer lexeme — only if two rules tie on length does rule order (priority) break the tie. A common beginner mistake is writing a keyword rule after an identifier rule and expecting priority to kick in when in fact both rules match the same length, so order matters there; but for rules that match *different* lengths, priority is irrelevant.

**The token set for our subset.** We need names, numbers, the rest symbol, brackets, and three operator characters:

$$
\texttt{WORD} = [a\text{-}zA\text{-}Z][a\text{-}zA\text{-}Z0\text{-}9]^* \qquad \texttt{NUMBER} = [0\text{-}9]^+
$$

with the single-character tokens `~ [ ] * / ?` passed through directly.

---

#### Code Cell

```c
/* mininotation.l : flex specification for the mini-notation subset.
   Each rule pairs a regular expression with a C action.
   Compile chain:  flex mininotation.l  ->  lex.yy.c            */

%{
#include "mininotation.tab.h"   /* token codes generated by bison */
#include <stdlib.h>
#include <string.h>
%}

%option noyywrap

%%

[a-zA-Z][a-zA-Z0-9]*   { yylval.str = strdup(yytext); return WORD;   }
[0-9]+                 { yylval.num = atoi(yytext);   return NUMBER; }
"~"                    { return REST;   }
"["                    { return LBRACK; }
"]"                    { return RBRACK; }
"*"                    { return STAR;   }
"/"                    { return SLASH;  }
"?"                    { return QMARK;  }
[ \t\r\n]+             { /* whitespace separates tokens; discard */  }
.                      { fprintf(stderr, "[lexer] unexpected character '%s'\n", yytext); }

%%
```

The `yylval` union carries each token's **semantic value** (the lexeme string for a `WORD`, the integer for a `NUMBER`) across the interface to the parser, while the return value carries the **token category**. Distinguishing category from value is the lexical analogue of the syntax/semantics boundary we maintain throughout the pipeline.

---

##### Try It: Individually

Before reading further, predict the token stream that this scanner emits for the input `bd [sn sn]*2 ~`. Write your answer as a sequence of (category, value) pairs, then check it against the table below.

| Lexeme | Category | Semantic value |
|--------|----------|----------------|
| `bd` | `WORD` | `"bd"` |
| `[` | `LBRACK` | (none) |
| `sn` | `WORD` | `"sn"` |
| `sn` | `WORD` | `"sn"` |
| `]` | `RBRACK` | (none) |
| `*` | `STAR` | (none) |
| `2` | `NUMBER` | `2` |
| `~` | `REST` | (none) |

Notice that whitespace has vanished entirely, and that the scanner has no opinion about whether `]` was ever preceded by a matching `[`. Balance is the parser's problem.

---

##### Model 1: Python Equivalent of the Flex Scanner

**What you are about to see:** The Flex `.l` file you just read is real C code, but to *run* and *observe* the scanner interactively we will first express the same logic in Python. The two implementations are mechanically identical in behavior — both compile a list of (regex, token-type) pairs into a single combined pattern and return the longest match — but Python lets you execute and modify the scanner right here in the browser without a C compiler. Once you are confident about what the scanner produces, Sections 6–8 return to the C/Bison side where the full pipeline lives.

Flex compiles each rule's regex into an NFA (Thompson's construction), merges all NFAs into one, applies the subset construction to get a single DFA, and walks that DFA character by character. Python's `re` module does exactly the same thing under the hood. Here is the flex scanner above written as Python, so you can run it and inspect every token:

```python
import re

# Same token spec as mininotation.l, in order.
# Rule priority: FIRST match in the list wins among equal-length matches.
# Maximal munch: re always takes the longest match.
TOKEN_SPEC = [
    ("WORD",   r"[a-zA-Z][a-zA-Z0-9]*"),
    ("NUMBER", r"[0-9]+"),
    ("REST",   r"~"),
    ("LBRACK", r"\["),
    ("RBRACK", r"\]"),
    ("STAR",   r"\*"),
    ("SLASH",  r"/"),
    ("QMARK",  r"\?"),
    ("WS",     r"[ \t\r\n]+"),
    ("ERROR",  r"."),
]

MASTER = re.compile("|".join(f"(?P<{name}>{pat})" for name, pat in TOKEN_SPEC))

def scan(source):
    tokens = []
    for m in MASTER.finditer(source):
        kind, lexeme = m.lastgroup, m.group()
        if kind == "WS":
            continue          # discard whitespace, just like the flex rule
        if kind == "ERROR":
            raise SyntaxError(f"unexpected: {lexeme!r}")
        tokens.append((kind, lexeme))
    return tokens

for src in ["bd sn hh", "bd [sn sn]*2 ~", "hh*4 ~ hh*4 ~", "[bd [sn sn]]/2"]:
    toks = scan(src)
    print(f"{src!r}")
    for kind, lex in toks:
        print(f"  ({kind}, {lex!r})")
    print()
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

##### Critical Thinking Questions — *Solo*

- The `ERROR` catch-all `.` appears last. What happens if you move it to the top of `TOKEN_SPEC`? Try predicting, then test by swapping its position.
- Maximal munch: what does the scanner produce for the input `bd2`? Is `bd2` one token or two? Which rule consumes it, and why?
- This Python scanner and the flex scanner produce identical token streams for the same input. What *implementation* is different between them (hint: flex builds a C DFA at compile time), and why does that matter for production use?

---

#### 4. A Grammar for the Mini-Notation

**We now give the structure of patterns as a context-free grammar.** Let $G = (V, \Sigma, R, S)$ with start symbol `pattern`. We write the productions in the notation yacc accepts, where `|` separates alternatives:

```
pattern  -> sequence

sequence -> sequence term
          | term

term     -> term STAR NUMBER
          | term SLASH NUMBER
          | term QMARK
          | atom

atom     -> WORD
          | REST
          | LBRACK sequence RBRACK
```

Three design decisions in this grammar repay close reading, because each one encodes a fact about the language into the shape of the productions.

**Left recursion implements left associativity, and yacc welcomes it.** The production `sequence -> sequence term` grows sequences to the left, so `bd sn hh` parses as `((bd sn) hh)`. A bottom-up LALR parser handles left recursion in constant stack space per reduction, whereas a top-down recursive-descent parser would loop forever on it. This is precisely opposite to the transformation you performed when we built recursive-descent parsers by hand earlier in the semester, and recognizing which parser family you are targeting is part of grammar literacy.

**Postfix operators bind tightly because `term` is recursive through itself.** In `hh*2?`, the derivation forces `(hh*2)?`: degrade applies to the already-sped-up element. The grammar, not a comment in the documentation, is what guarantees this.

**Nesting comes for free.** Because `atom` can derive `LBRACK sequence RBRACK` and `sequence` derives `term` derives `atom`, groups nest to any depth with no further mechanism. Compare the contortions Section 2 showed a regular language would require.

**A derivation, worked in full.** For the input `bd [sn sn]`, one leftmost derivation is:

$$
\begin{aligned}
\texttt{pattern} &\Rightarrow \texttt{sequence} \\
&\Rightarrow \texttt{sequence}\ \texttt{term} \\
&\Rightarrow \texttt{term}\ \texttt{term} \\
&\Rightarrow \texttt{atom}\ \texttt{term} \\
&\Rightarrow \texttt{WORD(bd)}\ \texttt{term} \\
&\Rightarrow \texttt{WORD(bd)}\ \texttt{atom} \\
&\Rightarrow \texttt{WORD(bd)}\ \texttt{LBRACK}\ \texttt{sequence}\ \texttt{RBRACK} \\
&\Rightarrow^{*} \texttt{WORD(bd)}\ \texttt{LBRACK}\ \texttt{WORD(sn)}\ \texttt{WORD(sn)}\ \texttt{RBRACK}
\end{aligned}
$$

---

##### Try It: With a Partner

Work in pairs, with one of you serving as **derivation writer** and the other as **verifier**, then swap roles for the second string. For each input below, the writer produces a leftmost derivation on paper while the verifier independently draws the parse tree, and you then reconcile the two artifacts, which must agree.

1. `hh*4 ~ hh*4 ~`
2. `[bd [sn sn]]/2`

When you reconcile, discuss this question and record a one-sentence answer: in string 2, does `/2` apply to the inner group `[sn sn]` or the outer group? Which production in the grammar settles the question?

---

[[MC]]
In the grammar above, the input `bd*2/3` parses with which effective grouping, and why?
- (x) `(bd*2)/3`, because `term` is left-recursive through the postfix operator productions, so operators accumulate left to right.
- ( ) `bd*(2/3)`, because `NUMBER SLASH NUMBER` forms a fraction at the lexical level.
- ( ) The input is a syntax error, because two postfix operators may never apply to one atom.
- ( ) The grouping is ambiguous, and yacc resolves it arbitrarily at run time.

---

#### 5. How Yacc Parses: LR Items, States, and the LALR(1) Idea

**Yacc builds a shift-reduce parser driven by a finite automaton over grammar items.** An **LR(0) item** is a production with a dot marking parsing progress, such as

$$
\texttt{term} \rightarrow \texttt{term} \cdot \texttt{STAR}\ \texttt{NUMBER}
$$

which reads "we have parsed a `term` and will accept this production if `STAR NUMBER` comes next." The parser generator closes sets of items into **states**, connects them with transitions on grammar symbols, and emits two tables: an **action** table (shift, reduce, accept, or error, indexed by state and lookahead token) and a **goto** table (next state after a reduction). At run time the parser is breathtakingly simple, which is the point: a loop, a stack, and table lookups, running in $O(n)$ time and using stack space proportional to the deepest nesting in the input.

##### Pseudocode

```
function LR-PARSE(tokens):
    push state 0
    a = first token
    loop:
        s = state on top of stack
        if ACTION[s, a] = shift t:
            push a, push state t
            a = next token
        else if ACTION[s, a] = reduce (A -> beta):
            pop 2 * |beta| entries
            t = state now on top
            push A, push GOTO[t, A]
            (run the semantic action for A -> beta here)
        else if ACTION[s, a] = accept:
            return the finished parse
        else:
            report syntax error at a
```

##### Model 2: Shift-Reduce Parsing in Python

**What you are about to see:** The pseudocode above describes LR parsing in the abstract; this model makes it concrete by running it step by step for a small arithmetic grammar. You will see the two-stack (state stack + symbol stack) loop in action and read a printed trace of every shift and reduce decision. Pay attention to the moment when the parser chooses to shift `*` rather than reducing an already-complete `+` expression — that single decision is where operator precedence lives in an LR parser, and spotting it in the trace will make the conflict discussion that follows much easier to understand.

Before reading the bison output, run the algorithm yourself on a tiny grammar. The code below simulates a shift-reduce parser for simple arithmetic expressions (`n + n * n`) with an explicit stack and action trace — the same algorithm bison generates for the mini-notation, just with a hand-written action table instead of a generated one.

```python
# Shift-reduce parser trace for: E → E+T | T,  T → T*F | F,  F → n
# ACTION table and GOTO table are encoded as dicts (state, symbol) → action.
# Actions: ("shift", next_state), ("reduce", rule), "accept", "error"

# Grammar rules: name → (symbols_to_pop, nonterminal_to_push)
RULES = {
    "E→E+T": (3, "E"),  # pop E, +, T  → push E
    "E→T":   (1, "E"),
    "T→T*F": (3, "T"),
    "T→F":   (1, "T"),
    "F→n":   (1, "F"),
}

# Minimal LR(0) action table for this grammar (hand-constructed, state 0-11)
ACTION = {
    (0,"n"):  ("shift",5),  (0,"("):  ("shift",4),
    (1,"+"):  ("shift",6),  (1,"$"):  "accept",
    (2,"+"):  ("reduce","E→T"), (2,"*"): ("shift",7), (2,"$"): ("reduce","E→T"),
    (3,"+"):  ("reduce","T→F"), (3,"*"): ("reduce","T→F"), (3,"$"): ("reduce","T→F"),
    (4,"n"):  ("shift",5),  (4,"("):  ("shift",4),
    (5,"+"):  ("reduce","F→n"), (5,"*"): ("reduce","F→n"), (5,"$"): ("reduce","F→n"),
    (6,"n"):  ("shift",5),  (6,"("):  ("shift",4),
    (7,"n"):  ("shift",5),  (7,"("):  ("shift",4),
    (8,"+"):  ("shift",6),  (8,")"):  ("shift",11),
    (9,"+"):  ("reduce","E→E+T"), (9,"*"): ("shift",7),
              (9,")"): ("reduce","E→E+T"), (9,"$"): ("reduce","E→E+T"),
    (10,"+"): ("reduce","T→T*F"), (10,"*"): ("reduce","T→T*F"),
              (10,")"): ("reduce","T→T*F"), (10,"$"): ("reduce","T→T*F"),
    (11,"+"): ("reduce","F→(E)"), (11,"*"): ("reduce","F→(E)"),
              (11,")"): ("reduce","F→(E)"), (11,"$"): ("reduce","F→(E)"),
}
GOTO = {
    (0,"E"):1, (0,"T"):2, (0,"F"):3,
    (4,"E"):8, (4,"T"):2, (4,"F"):3,
    (6,"T"):9, (6,"F"):3,
    (7,"F"):10,
}

def lr_parse(tokens):
    tokens = tokens + ["$"]
    stack = [0]        # state stack
    sym_stack = []     # symbol stack (for display)
    pos = 0

    print(f"{'Stack':35} {'Remaining':18} Action")
    print("-" * 75)

    while True:
        state = stack[-1]
        tok   = tokens[pos]
        disp_stack = " ".join(str(x) for x in sym_stack) or "⊥"
        disp_rest  = " ".join(tokens[pos:])
        action = ACTION.get((state, tok), "error")

        if action == "accept":
            print(f"{disp_stack:35} {disp_rest:18} ACCEPT ✓")
            return
        elif action == "error":
            print(f"{disp_stack:35} {disp_rest:18} ERROR at {tok!r}")
            return
        elif action[0] == "shift":
            _, next_state = action
            print(f"{disp_stack:35} {disp_rest:18} SHIFT  {tok} → state {next_state}")
            sym_stack.append(tok); stack.append(next_state); pos += 1
        elif action[0] == "reduce":
            rule = action[1]
            pop_n, lhs = RULES[rule]
            for _ in range(pop_n): sym_stack.pop(); stack.pop()
            top = stack[-1]
            goto_state = GOTO[(top, lhs)]
            sym_stack.append(lhs); stack.append(goto_state)
            print(f"{disp_stack:35} {disp_rest:18} REDUCE {rule}")

print("=== n + n * n (right operand tighter) ===")
lr_parse(["n", "+", "n", "*", "n"])
print()
print("=== n * n + n (left operand tighter) ===")
lr_parse(["n", "*", "n", "+", "n"])
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

##### Critical Thinking Questions — *Pairs*

- In the first trace (`n + n * n`), at what point does the parser shift `*` instead of reducing the first `n + n`? What state and lookahead determine this decision?
- In the RULES table, `"E→E+T": (3, "E")` pops 3 symbols. What are those 3 symbols, and why does popping them from the stack correspond to "recognizing a complete E+T"?
- If you added `"E→E+E"` to the grammar (making addition left-recursive in a second way), which `ACTION` table entry would conflict with an existing one? This is a shift/reduce conflict — identify the state and the competing actions.

---

**LALR(1) is LR(1) with merged states.** Full LR(1) tables distinguish states by lookahead and grow large; LALR(1) merges LR(1) states that share the same item cores, keeping the table compact at the cost of accepting a slightly smaller family of grammars. Our mini-notation grammar is comfortably LALR(1): you can verify with `bison -v mininotation.y`, which writes the full automaton, every state and item set, to `mininotation.output`. Reading that file once, slowly, will teach you more about LR parsing than any lecture, and we will do exactly that in the partner activity below.

**Conflicts are the diagnostic signal.** A **shift/reduce conflict** means some state sees a lookahead for which both shifting and reducing are table-legal; a **reduce/reduce conflict** means two completed productions compete. Our grammar produces neither, but you will manufacture one, deliberately, in a moment, because learning to read conflict reports is the practical skill that separates people who can use parser generators from people who fight them.

> **Watch out!** A shift/reduce conflict almost always signals an **ambiguous grammar** — the same token sequence has two valid parse trees. Bison resolves the conflict silently by defaulting to *shift* (which usually gives the right answer for dangling-else style ambiguities), but it will still print a warning. Never ignore that warning: if your grammar has a conflict you did not anticipate, Bison's silent default resolution may produce parse trees that are subtly wrong and very difficult to debug downstream. Always read the `.output` file and confirm that the chosen resolution matches your intent.

---

##### Try It: With a Partner

One partner is the **saboteur** and the other is the **diagnostician**; swap after the first round. The saboteur makes exactly one of the following edits to the grammar, without telling the diagnostician which:

1. Change `sequence -> sequence term` to the ambiguous `sequence -> sequence sequence | term`.
2. Add a redundant production `atom -> WORD QMARK` alongside the existing `term -> term QMARK`.

Run `bison -v mininotation.y`. The diagnostician must, using only bison's stderr output and the `.output` file, identify which edit was made, name the conflict type, and point to the state and item set where it arises. Record the state number and one sentence of explanation before swapping.

---

#### 6. The Yacc Specification: Grammar Plus Semantic Actions

**What you are about to see:** Section 4 gave the grammar as pure BNF; this section adds the second half — the *semantic actions* that fire each time a production is reduced, building up AST nodes from the bottom of the tree to the top. Think of the grammar productions as a recipe ("when you see a `term` followed by `STAR NUMBER`, you have a fast-repeat construct") and the actions as the kitchen instructions that assemble the result ("wrap the term node in a new `N_FAST` node carrying the integer"). After reading the Yacc file, you should be able to mentally simulate one reduction and know exactly which `$$` assignment runs.

**Each production carries an action that builds one AST node.** In yacc actions, `$$` denotes the semantic value of the left-hand side and `$1, $2, \ldots` the values of the right-hand-side symbols in order. The actions below are deliberately uniform: every production either passes a subtree upward or wraps its children in exactly one new node. When actions stay this disciplined, the AST is a faithful image of the derivation, and debugging the parser reduces to printing trees.

---

#### Code Cell

```c
/* mininotation.y : bison/yacc specification with AST-building actions.
   Compile chain:
     bison -d mininotation.y      -> mininotation.tab.c, mininotation.tab.h
     flex  mininotation.l         -> lex.yy.c
     gcc -o mininote mininotation.tab.c lex.yy.c ast.c eval.c -lfl        */

%{
#include <stdio.h>
#include <stdlib.h>
#include "ast.h"

int  yylex(void);
void yyerror(const char *msg) {
    fprintf(stderr, "[parser] %s\n", msg);
}

Node *ast_root = NULL;
%}

%union {
    char *str;
    int   num;
    struct Node *node;
}

%token <str> WORD
%token <num> NUMBER
%token REST LBRACK RBRACK STAR SLASH QMARK

%type <node> pattern sequence term atom

%%

pattern  : sequence                      { ast_root = $1; }
         ;

sequence : sequence term                 { $$ = seq_append($1, $2); }
         | term                          { $$ = seq_new($1);        }
         ;

term     : term STAR NUMBER              { $$ = node_fast($1, $3);  }
         | term SLASH NUMBER             { $$ = node_slow($1, $3);  }
         | term QMARK                    { $$ = node_degrade($1);   }
         | atom                          { $$ = $1;                 }
         ;

atom     : WORD                          { $$ = node_atom($1);      }
         | REST                          { $$ = node_rest();        }
         | LBRACK sequence RBRACK        { $$ = node_group($2);     }
         ;

%%
```

---

**The AST node type is a small tagged union, the C ancestor of the algebraic data types you know from Haskell.** When we study TidalCycles' host language, you will meet the direct analogue, and seeing the C encoding first makes the Haskell version feel like a kindness:

---

#### Code Cell

```c
/* ast.h : tagged-union AST for mini-notation.
   Compare with a Haskell ADT, which says the same thing in five lines:
     data Node = Atom String | Rest | Seq [Node] | Group Node
               | Fast Node Int | Slow Node Int | Degrade Node        */

#ifndef AST_H
#define AST_H

typedef enum { N_ATOM, N_REST, N_SEQ, N_GROUP,
               N_FAST, N_SLOW, N_DEGRADE } NodeType;

typedef struct Node {
    NodeType type;
    char *name;              /* N_ATOM: sample name                  */
    int factor;              /* N_FAST / N_SLOW: the integer operand */
    struct Node **children;  /* N_SEQ: ordered children              */
    int nchildren;
    struct Node *child;      /* unary wrappers: GROUP, FAST, SLOW,
                                DEGRADE                              */
} Node;

Node *node_atom(char *name);
Node *node_rest(void);
Node *seq_new(Node *first);
Node *seq_append(Node *seq, Node *next);
Node *node_group(Node *seq);
Node *node_fast(Node *child, int k);
Node *node_slow(Node *child, int k);
Node *node_degrade(Node *child);

#endif
```

---

##### Try It: Individually

Draw, by hand, the AST that the actions above construct for the input `bd [sn sn] hh*2 ~`. Label every node with its `NodeType`. Then answer in one sentence each:

1. How many `N_SEQ` nodes does your tree contain, and why is the answer not one?
2. Which node is the parent of the `N_FAST` node, and which production created that parent?

---

#### 7. Driving the Pipeline End to End

**A small `main` connects the stages.** The program reads a pattern from standard input, invokes `yyparse()`, which internally calls `yylex()` on demand, and then hands the resulting tree to a printer and an evaluator.

---

#### Code Cell

```c
/* main.c : end-to-end driver.
   Example session:
     $ echo "bd [sn sn] hh*2 ~" | ./mininote
     SEQ
       ATOM bd
       GROUP
         SEQ
           ATOM sn
           ATOM sn
       FAST 2
         ATOM hh
       REST
     events in cycle [0,1):
       bd   [0.000, 0.250)
       sn   [0.250, 0.375)
       sn   [0.375, 0.500)
       hh   [0.500, 0.625)
       hh   [0.625, 0.750)                                            */

#include <stdio.h>
#include "ast.h"

extern int yyparse(void);
extern Node *ast_root;

void ast_print(Node *n, int depth);             /* in ast.c  */
void eval_pattern(Node *n, double t0, double t1); /* in eval.c */

int main(void) {
    if (yyparse() != 0 || ast_root == NULL) {
        fprintf(stderr, "[main] parse failed\n");
        return 1;
    }
    ast_print(ast_root, 0);
    printf("events in cycle [0,1):\n");
    eval_pattern(ast_root, 0.0, 1.0);
    return 0;
}
```

---

#### 8. Semantics: From Trees to Time

**What you are about to see:** Everything up to this point — the scanner, the grammar, the AST — was purely *structural*: we recognized and organized the input without deciding what it *means*. This section assigns musical meaning to each AST node type via structural recursion, one equation (and one C `case`) per node type. The key insight is that `SEQ` subdivides time, `FAST` further subdivides each copy, and `GROUP` is completely transparent (it was only needed by the *parser* to capture nesting; once the tree is built, the group brackets have done their job). Work through the equations for `[bd sn]*2` by hand before running the code.

> **Watch out!** It is tempting to put musical interpretation logic *inside* the parser actions themselves — for example, computing event spans directly in the Yacc `%%` section. Resist this: mixing parsing and evaluation collapses the syntax/semantics boundary and makes both sides harder to test, extend, and reason about. The AST exists precisely to give you a clean handoff point. If you ever find yourself computing time spans inside a grammar action, that is a sign to stop and push the logic into the evaluator instead.

**Now, and only now, do we assign meaning.** The denotation of a pattern is a set of **events**, each a sample name paired with a half-open time span $[t_0, t_1) \subseteq [0, 1)$ within the cycle. We define the evaluation function $\mathcal{E}[\![\, n \,]\!](t_0, t_1)$ by structural recursion on the AST, one clause per node type, and this is your first denotational semantics written in C rather than on a whiteboard:

$$
\mathcal{E}[\![\, \texttt{SEQ}(c_1, \ldots, c_k) \,]\!](t_0, t_1) \;=\; \bigcup_{i=1}^{k}\; \mathcal{E}[\![\, c_i \,]\!]\!\left( t_0 + \tfrac{(i-1)\,\Delta}{k},\; t_0 + \tfrac{i\,\Delta}{k} \right), \quad \Delta = t_1 - t_0
$$

$$
\mathcal{E}[\![\, \texttt{FAST}(c, m) \,]\!](t_0, t_1) \;=\; \bigcup_{j=0}^{m-1}\; \mathcal{E}[\![\, c \,]\!]\!\left( t_0 + \tfrac{j\,\Delta}{m},\; t_0 + \tfrac{(j+1)\,\Delta}{m} \right)
$$

$$
\mathcal{E}[\![\, \texttt{ATOM}(s) \,]\!](t_0, t_1) = \{ (s, t_0, t_1) \} \qquad
\mathcal{E}[\![\, \texttt{REST} \,]\!](t_0, t_1) = \varnothing
$$

A `GROUP` is semantically transparent, evaluating its child on the same span, because the brackets did their work during parsing by controlling how the tree was built. Read that sentence twice: it is the clearest example in this module of syntax and semantics dividing the labor.

---

#### Code Cell

```c
/* eval.c : structural recursion implementing the semantics above.
   Each case implements exactly one displayed equation; the SEQ case
   implements the first equation, and the FAST case the second.      */

#include <stdio.h>
#include "ast.h"

void eval_pattern(Node *n, double t0, double t1) {
    double span = t1 - t0;
    switch (n->type) {

    case N_ATOM:                       /* E[[ATOM s]](t0,t1) = {(s,t0,t1)} */
        printf("  %-4s [%.3f, %.3f)\n", n->name, t0, t1);
        break;

    case N_REST:                       /* E[[REST]] = empty set            */
        break;

    case N_SEQ:                        /* subdivide the span evenly        */
        for (int i = 0; i < n->nchildren; i++) {
            double a = t0 + span * i       / n->nchildren;
            double b = t0 + span * (i + 1) / n->nchildren;
            eval_pattern(n->children[i], a, b);
        }
        break;

    case N_GROUP:                      /* transparent: same span           */
        eval_pattern(n->child, t0, t1);
        break;

    case N_FAST:                       /* m copies, each on span/m         */
        for (int j = 0; j < n->factor; j++) {
            double a = t0 + span * j       / n->factor;
            double b = t0 + span * (j + 1) / n->factor;
            eval_pattern(n->child, a, b);
        }
        break;

    case N_SLOW:
        /* Scaffolded for you: SLOW stretches its child across `factor`
           cycles, so within THIS cycle you play a 1/factor "window" of
           the child. Decide which window, and justify your choice in a
           comment. Hint: you will need a notion of the current cycle
           number; consider passing it as a parameter.                  */
        fprintf(stderr, "[eval_pattern:N_SLOW] not yet implemented\n");
        break;

    case N_DEGRADE:
        /* Scaffolded for you: with probability 1/2, evaluate the child;
           otherwise emit nothing. For reproducible grading, seed the
           generator deterministically: srand(42) once in main.         */
        fprintf(stderr, "[eval_pattern:N_DEGRADE] not yet implemented\n");
        break;
    }
}
```

---

**Verification against the reference implementation.** Strudel runs in any browser at [strudel.cc](https://strudel.cc). Enter `sound("bd [sn sn] hh*2 ~")`, press play, and watch the highlighted event spans in the editor; they are the very intervals your evaluator prints. Within the subset we implemented, your C program and a production live coding system now agree on the meaning of every pattern, and that agreement, a hand-built artifact validated against a real language, is the experience this course is designed around.

[[MC]]
For the input `[bd sn]*2`, how many events does the semantics above produce in one cycle, and on what spans?
- ( ) Two events: `bd` on $[0, 0.5)$ and `sn` on $[0.5, 1)$.
- (x) Four events: `bd` on $[0, 0.25)$, `sn` on $[0.25, 0.5)$, `bd` on $[0.5, 0.75)$, `sn` on $[0.75, 1)$.
- ( ) Two events: `bd` on $[0, 0.25)$ and `sn` on $[0.25, 0.5)$, with silence afterward.
- ( ) Eight events, because the group doubles and the sequence doubles again.

---

### Part III: Synthesis & Practice

#### 9. Exercises

The first three exercises are designed for individual work in class today; the final two are partner exercises, and you should complete at least one of them with a classmate before the next session.

1. *Trace the tables.* Run `bison -v mininotation.y` and open `mininotation.output`. For the input `bd*2`, list, in order, every shift and reduce action the parser performs, citing state numbers from the file. Report the maximum stack depth reached.
2. *Implement SLOW.* Complete the `N_SLOW` case in `eval.c`, extending `eval_pattern` with a cycle-number parameter. Demonstrate on `bd/2 sn` across cycles 0 and 1, and report the printed event list for both cycles.
3. *Implement DEGRADE reproducibly.* Complete the `N_DEGRADE` case with a deterministic seed, run `hh*8?` three times, and confirm identical output across runs. Report the surviving event spans.
4. *Partner: grammar extension.* With a partner, extend the grammar and lexer to support alternation `<a b c>`, which plays one element per cycle in rotation. One partner writes the flex and yacc changes; the other writes the `N_ALT` evaluator case; integrate and test on `bd <sn cp hh>` across three cycles. Report which design questions required negotiation between the syntax side and the semantics side.
5. *Partner: break it and read the report.* Each partner independently introduces one grammar ambiguity, exchanges files, and diagnoses the other's conflict using only the `.output` file, naming the conflict type and the state where it occurs. Report both diagnoses and confirm them against the original edits.

---

#### 10. Further Reading

- Aho, Lam, Sethi, and Ullman. *Compilers: Principles, Techniques, and Tools* (2nd ed., 2006). Chapters 3 and 4 are the canonical treatment of lexical analysis and LR parsing; Section 4.7 covers the LALR construction used by yacc.
- Levine, John. *flex & bison* (O'Reilly, 2009). The practical handbook for the exact tools used in this module, including conflict debugging workflows.
- McLean, Alex. "Making Programming Languages to Dance to: Live Coding with Tidal." *FARM Workshop, ICFP* (2014). The design rationale for TidalCycles and its mini-notation, written by the language's creator.
- The Strudel project, [strudel.cc](https://strudel.cc) and its documentation. The reference implementation against which we validated our evaluator; the mini-notation parser source is openly available and worth reading after this module.
- Johnson, Stephen C. "Yacc: Yet Another Compiler-Compiler." *Bell Laboratories Computing Science Technical Report 32* (1975). The original report; short, readable, and historically grounding.

---

## Going Deeper: LL and LR Parsing: Tables, Conflicts, and How Yacc Works

Your recursive descent parser is already an LL parser — you just haven't seen the table yet. Every function is a row, every `if` on the lookahead token is a column lookup, and every time you call a sub-function you are pushing a frame onto the implicit parse stack. This activity makes that hidden machinery explicit, then flips the whole picture upside-down to show how LR parsers — the kind yacc and bison generate — read the same tokens from the opposite direction and handle grammars that would tie recursive descent in knots.

#### Learning Goals

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

#### 0. Running Grammar

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

### Part I: LL(1) Parsing

#### 1. FIRST Sets

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

#### 2. FOLLOW Sets

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

#### 3. LL(1) Parsing Table Construction

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

#### 4. LL(1) Table-Driven Parsing

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

### Part II: LR Parsing

#### 5. The LR Idea: Bottom-Up with a Stack

LR parsing feels backward at first: instead of predicting what to expand next (LL's "top-down" view), LR parsers collect tokens on a stack and wait until they have seen a complete right-hand side — then they collapse it back to the left-hand side (a "reduction"). Think of it like assembling a sentence by collecting words until you can label a phrase, then treating the labeled phrase as a single unit for the next level up.

**LR parsers** work bottom-up: they shift tokens onto a stack and **reduce** (replace a handle matching a production's RHS with its LHS) when they have seen enough. The "L" means left-to-right scan; "R" means rightmost derivation in reverse; "k" is the lookahead.

The key data structures are:
- **Stack**: holds states (integers) encoding what has been seen so far
- **Action table** $\mathrm{ACTION}[s, a]$: for state $s$ and lookahead $a$, either **shift** to a new state, **reduce** by a production, **accept**, or **error**
- **Goto table** $\mathrm{GOTO}[s, A]$: after reducing to nonterminal $A$ in state $s$, go to this new state

The tables encode a **push-down automaton** built from the grammar.

#### 6. LR(0) Items and the Canonical Collection

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

#### 7. SLR(1) Tables: Adding Lookahead

**SLR(1)** (Simple LR) uses FOLLOW sets to decide when to reduce:

- **Shift** action for state $s$ on terminal $a$: if $\mathrm{goto}(s, a) = s'$, put $\mathrm{ACTION}[s, a] = \mathrm{shift}\ s'$
- **Reduce** action: if $[A \to \alpha \bullet]$ is in state $s$ and $a \in \mathrm{FOLLOW}(A)$, put $\mathrm{ACTION}[s, a] = \mathrm{reduce}\ A \to \alpha$
- **Accept**: if $[S' \to S\ \bullet]$ is in state $s$, put $\mathrm{ACTION}[s, \$] = \mathrm{accept}$

An **SLR conflict** occurs when the same cell gets two actions:
- **Shift-reduce conflict**: both a shift and a reduce are valid. Often resolved by **precedence** (Yacc does this for `+` vs `*`).
- **Reduce-reduce conflict**: two different reductions. Usually indicates a grammar problem.

**LALR(1)** (Look-Ahead LR) is SLR(1) with more precise lookahead sets — not FOLLOW(A) globally, but the specific lookahead valid for each particular reduce in each state. LALR(1) is what yacc/bison implements, and it handles most practical programming language grammars.

---

##### Try It: With a Partner — Build the SLR Table by Hand

Use the simple grammar $S \to (S) \mid x$ and the item sets built above.

1. Partner A computes FOLLOW sets for $S$ and $S'$.
2. Partner B lists all states with a reduce item (dot at end).
3. Together, fill in the ACTION and GOTO tables.
4. Trace the parse of `( x )` using your table.

Report: Did any state have a conflict? What would it mean if it did?

---

#### 8. How Yacc/Bison Uses LALR(1)

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

#### 9. LL vs. LR: The Practical Comparison

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

#### 10. Exercises

1. **FIRST and FOLLOW by hand.** Compute FIRST and FOLLOW for every nonterminal in the grammar:
   $$G: S \to A\ B,\quad A \to a\ A \mid \epsilon,\quad B \to b\ B \mid b$$
   Build the LL(1) table and identify any conflicts. If there is a conflict, explain whether left-factoring or another transformation can resolve it.

2. **Table-driven parse trace.** Using the LL(1) table from Section 3, trace the parse of `( id + id )` step by step: show the stack, input, and action at each step. What is the sequence of productions used?

3. **Left recursion elimination.** Transform the grammar $E \to E + T \mid T$, $T \to T * F \mid F$, $F \to (E) \mid \mathbf{id}$ into an equivalent non-left-recursive grammar. Compute FIRST and FOLLOW sets for the transformed grammar. Compare it to our running grammar — is it the same?

4. **LR(0) item construction.** For the grammar $S \to a S b \mid a b$, construct all LR(0) item sets by hand. Draw the automaton. Identify which states have reduce items, and determine which tokens (using FOLLOW sets) trigger each reduction.

5. **Bison conflict resolution.** The grammar fragment `stmt → IF expr THEN stmt | IF expr THEN stmt ELSE stmt` is the classic dangling-else ambiguity. In bison, the default conflict resolution is shift (matching `else` with the nearest `if`). Write the bison `%prec` declaration that enforces this explicitly, and trace the parse of `if e1 then if e2 then s1 else s2` showing when shift wins over reduce.

---

#### 11. Further Reading

- Aho, Alfred V., Monica Lam, Ravi Sethi, and Jeffrey Ullman. *Compilers: Principles, Techniques, and Tools* (2nd ed., "Dragon Book"). Chapters 4-5 are the standard reference for LL and LR parsing, FIRST/FOLLOW, and table construction.
- Thain, Douglas. *Introduction to Compilers and Language Design*. Chapter 5 covers recursive descent; Chapter 6 covers LR parsing; available free at the course textbook link.
- Grune, Dick and Ceriel Jacobs. *Parsing Techniques: A Practical Guide* (2nd ed., Springer, 2008). Free PDF. The most comprehensive survey of parsing algorithms.
- DeRemer, Franklin and Thomas Pennello. "Efficient Computation of LALR(1) Look-Ahead Sets." *ACM TOPLAS* 4(4), 1982. The algorithm bison actually uses.
- Parr, Terence. *The Definitive ANTLR 4 Reference* (Pragmatic Bookshelf, 2013). LL(*) — the generalization of LL(1) that ANTLR implements, with arbitrary lookahead.

## Going Deeper: The Compilation and Linking Process

> **Opening hook:** Think of translating a novel from French to English, but the book is enormous so several translators each handle a separate chapter independently. Each translator (the **compiler**) converts their chapter from French to English without knowing exactly what page numbers the other chapters will land on — they leave placeholders like "see Chapter 7" wherever they cross-reference another chapter. When all the translated chapters are done, an editor (the **linker**) gathers them, resolves every placeholder to a real page number, and stitches them into one coherent book. The final book is your executable: one continuous object where every function call points to the exact address of the function it calls.

#### Learning Goals

By the end of this activity, you will be able to:

- Enumerate and describe each stage of the compilation pipeline — preprocessing, parsing, semantic analysis, code generation, assembly, and linking — and identify the input and output artifact of each stage
- Explain the role of symbol tables and relocation records in the object-file format, and trace how the linker resolves external references across separately compiled modules
- Distinguish static linking from dynamic linking, and reason about the tradeoffs of each for program startup time, binary size, and library versioning
- Map the compilation pipeline stages onto your course interpreter project, identifying which stages you have already implemented and which stages a full compiler would add

**CS374: Principles of Programming Languages — Week 9**

**References:** Compilers (Dragon Book) Ch. 2 and Ch. 8

---

> **Before You Begin**
>
> This activity assumes you are comfortable with:
>
> - Writing and calling Python functions; understanding what a **stack frame** is (local variables, return address)
> - Basic familiarity with how your interpreter project parses source code into an AST and evaluates it
> - The concept of a **dictionary** (hash map) as a data structure — symbol tables are essentially dictionaries
> - What a **memory address** is: an integer that identifies a location in the computer's RAM
>
> You do *not* need prior knowledge of assembly language or operating systems. All machine-level concepts are introduced here via Python simulations.

---

#### Directions and Group Roles

This is a **POGIL (Process-Oriented Guided Inquiry Learning)** activity. Work in groups of 3–4. Each person takes a role:

| Role | Responsibility |
|------|----------------|
| **Manager** | Keeps the group on task; ensures everyone participates |
| **Recorder** | Writes down the group's answers to Critical Thinking Questions |
| **Presenter** | Shares the group's findings with the class |
| **Reflector** | Monitors the group process; leads the reflection at the end |

**Learning Objectives:** By the end of this activity you will be able to:

1. Describe the stages of the compilation pipeline from source code to executable.
2. Explain what bytecode is and how a stack-based virtual machine executes it.
3. Define symbol tables, object files, and the role of the linker.
4. Distinguish between static and dynamic linking.
5. Connect Python's import system to the concept of dynamic linking.

---

#### Model 1: The Compilation Pipeline

**Intuition:** Your source code is just a string of characters — the computer has no idea what `def add(x, y): return x + y` means until something translates it into instructions a CPU can execute. That translation happens in a pipeline of stages, each with a well-defined input and output. By the time we reach the end of the pipeline, we have gone from "English-like text" to "numbered machine operations." Python exposes this pipeline through its built-in tools so you can watch each stage happen in real time. Notice that even an interpreted language like Python goes through compilation — it just compiles to *bytecode* (instructions for a software CPU) rather than native machine code.

A compiler translates source code through several stages before producing executable code. In a traditional C/C++ compiler (like GCC or LLVM), those stages are:

1. **Lexical Analysis (Scanning):** Convert characters to tokens.
2. **Parsing:** Build an Abstract Syntax Tree (AST).
3. **Semantic Analysis:** Type-check and annotate the AST.
4. **Intermediate Code Generation:** Produce an IR (e.g., three-address code).
5. **Optimization:** Improve the IR.
6. **Code Generation:** Emit assembly or machine code.
7. **Linking:** Combine object files into an executable.

Python exposes these stages through its `compile()`, `ast`, and `dis` modules, letting us observe them directly.

```python
import dis
import ast

# Stage 1: Source code
source = """
def add(x, y):
    return x + y

result = add(3, 4)
print(result)
"""

# Stage 2: Parse to AST
tree = ast.parse(source)
print("=== AST dump (first 300 chars) ===")
print(ast.dump(tree, indent=2)[:300] + "...")

# Stage 3: Compile to bytecode
code = compile(source, "<string>", "exec")
print("\n=== Bytecode for 'add' function ===")
for const in code.co_consts:
    if hasattr(const, 'co_name') and const.co_name == 'add':
        dis.dis(const)
        break

# Stage 4: Execute
exec(code)
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

> **Watch out!** "Python is interpreted, not compiled" is a common but misleading claim. Python *does* compile your source code — to bytecode — every time you run a `.py` file. The difference from C is that Python's target is a *software* CPU (the CPython VM) rather than a *hardware* CPU. The `.pyc` files you may have seen in `__pycache__/` are the cached bytecode output of this compilation step. Saying Python is "interpreted" means the bytecode is executed by a software interpreter, not that compilation never happens.

**Critical Thinking Questions (CTQs) — Model 1**

1. List the stages of compilation shown in the code comments above (Stage 1 through Stage 4). How do they map onto the seven stages described in the introduction?

2. What does "compile to bytecode" mean? In your own words, describe what bytecode is and why it is produced instead of machine code directly.

3. Python bytecode runs on the CPython interpreter (a virtual machine), while C code compiles to native machine code that runs on a CPU. What is the key difference? What is the tradeoff in portability versus performance?

4. What does `dis.dis()` show you? Look at the output: what information does each line of the disassembly contain?

---

#### Model 2: Python Bytecode in Depth

**Intuition:** Imagine evaluating `a * b + c` on an old-fashioned desk calculator with a single display window. You must press buttons in a specific order: recall `a`, recall `b`, press multiply (the result sits in the display), recall `c`, press add. The display is a stack with one slot — each operation pops its inputs from the display and pushes its result back. CPython's virtual machine works the same way, just with a deeper stack. Every expression in your Python program gets compiled down to a sequence of these push/pop operations (LOAD, BINARY_OP, RETURN) that any first-year CS student could execute by hand given the instruction list.

CPython uses a **stack-based virtual machine** to execute bytecode. Every operation either pushes values onto a stack, pops them off, or both. Understanding the stack machine helps you understand how any expression is evaluated at the lowest level.

The bytecode for `a * b + c` follows this sequence of stack operations:

```
LOAD_FAST a       → stack: [a]
LOAD_FAST b       → stack: [a, b]
BINARY_MULTIPLY   → stack: [a*b]
LOAD_FAST c       → stack: [a*b, c]
BINARY_ADD        → stack: [a*b+c]
RETURN_VALUE      → returns a*b+c, stack: []
```

```python
import dis
import opcode

# A simple function to disassemble
def compute(a, b, c):
    return a * b + c

print("=== Bytecode for compute(a, b, c): a*b + c ===")
dis.dis(compute)

print("\n=== Bytecode details ===")
code = compute.__code__
print(f"co_varnames: {code.co_varnames}")   # local variable names
print(f"co_consts:   {code.co_consts}")     # literal constants
print(f"co_argcount: {code.co_argcount}")   # number of arguments
print(f"co_stacksize:{code.co_stacksize}")  # max stack depth needed

# Trace execution manually:
# LOAD_FAST a   → stack: [a]
# LOAD_FAST b   → stack: [a, b]
# BINARY_MULTIPLY → stack: [a*b]
# LOAD_FAST c   → stack: [a*b, c]
# BINARY_ADD    → stack: [a*b+c]
# RETURN_VALUE  → returns a*b+c

print("\nCompute(3, 4, 5) =", compute(3, 4, 5))
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

**Critical Thinking Questions (CTQs) — Model 2**

1. CPython uses a stack-based virtual machine. When `LOAD_FAST a` executes, what happens to the stack? Trace through the full execution of `compute(2, 3, 4)` step by step, showing the stack contents after each instruction.

2. Why is a stack a natural data structure for expression evaluation? Think about how postfix (Reverse Polish Notation) notation works and how it relates to what you see here.

3. The code object attribute `co_stacksize` tells CPython how much stack space to pre-allocate. How would a compiler determine the required stack size for a function? (Hint: think about the maximum stack depth during execution.)

4. A **register-based** architecture (like a real CPU or the Dalvik VM used in early Android) uses a fixed set of named registers instead of a stack. What would the instructions for `a * b + c` look like in a register-based design? What is one advantage of each approach?

---

#### Model 3: Object Files and Symbol Tables

**Intuition:** When your team splits a large project across multiple files and each person compiles their own file independently, the compiler cannot know the final addresses of functions defined in *other* files — those files haven't been compiled yet, or might not even exist. So the compiler produces an **object file** that is like a translated chapter with blanks left wherever a cross-reference to another chapter belongs. The object file also ships a **symbol table** — a two-column list: "here is what I *define* (with its address)" and "here is what I *need* but didn't define (blank for now)." The linker reads all these lists and fills in every blank.

When a compiler processes a single source file, it produces an **object file** (`.o` on Linux/Mac, `.obj` on Windows). An object file contains:

- **Machine code** (or bytecode) for the functions defined in that file.
- A **symbol table** listing every name the file *defines* (exports) and every name it *references* but does not define (imports).

The symbol table is the key data structure that enables separate compilation: you can compile `math.c` and `main.c` independently, then combine them later.

```python
from dataclasses import dataclass, field
from typing import Optional

@dataclass
class Symbol:
    name: str
    defined: bool        # True = defined here; False = referenced but not defined
    value: Optional[int] = None  # address/offset (None if undefined)
    exported: bool = True  # visible to other modules

@dataclass
class ObjectFile:
    name: str
    symbols: dict = field(default_factory=dict)
    code: list = field(default_factory=list)   # simulated instructions
    
    def define(self, name: str, value: int, exported: bool = True):
        self.symbols[name] = Symbol(name, defined=True, value=value, exported=exported)
    
    def reference(self, name: str):
        if name not in self.symbols:
            self.symbols[name] = Symbol(name, defined=False)
    
    def undefined_refs(self):
        return [s for s in self.symbols.values() if not s.defined]
    
    def exported_symbols(self):
        return [s for s in self.symbols.values() if s.defined and s.exported]

# Simulate math.o: defines add, mul; references nothing
math_obj = ObjectFile("math.o")
math_obj.define("add", 0x1000)
math_obj.define("mul", 0x1020)

# Simulate main.o: references add and mul from math.o
main_obj = ObjectFile("main.o")
main_obj.define("main", 0x2000)
main_obj.reference("add")   # from math.o
main_obj.reference("mul")   # from math.o
main_obj.reference("printf")  # from libc — still unresolved at this stage

print("math.o exports:", [s.name for s in math_obj.exported_symbols()])
print("main.o undefined refs:", [s.name for s in main_obj.undefined_refs()])
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

> **Watch out!** An undefined reference in an object file is **not** a compile-time error. The C compiler happily produces `main.o` even though it references `printf` without seeing its definition — it just records the reference in the symbol table. The error only fires at **link time**, when the linker discovers no object file or library provides the definition. This is why you can get "successful" compilation but a failing `gcc` invocation: the compile step passed but the link step failed.

**Critical Thinking Questions (CTQs) — Model 3**

1. What is a **symbol table**? What two kinds of information does it record for each symbol, according to the `Symbol` dataclass above?

2. What is the difference between a *defined* symbol and a *referenced* symbol? Give a concrete example: if `main.c` calls `sqrt()` from the math library, which file has `sqrt` as defined, and which file has it as referenced?

3. After compiling `main.c` to `main.o` (but *before* linking), `printf` appears as an undefined reference. Why? Is this an error at compile time? When must it be resolved?

4. The `ObjectFile` class has an `exported` flag on each symbol. What does it mean for a symbol to be *not exported* (i.e., `exported=False`)? In C, what keyword makes a function private to a translation unit?

---

#### Model 4: Linking — Resolving Symbols

**Intuition:** The linker is like a fact-checker working through every "see Chapter 7, page X" placeholder in the assembled manuscript. It builds a master index (the global symbol table) from all the chapter-level indexes, then walks through every placeholder and writes in the correct page number. If any placeholder references a chapter that was never submitted — say, `printf` from the C library was never included — the fact-checker stops and reports an error: "undefined reference." This is the linker error you have probably seen when you forgot to link a library (`-lm` for math, for example). The linker *refuses* to produce the book until every cross-reference is resolved.

The **linker** takes multiple object files, merges their symbol tables, resolves all undefined references, and assigns final addresses. If any symbol is still undefined after processing all object files (and any requested libraries), the linker reports an error and refuses to produce an executable.

```python
from dataclasses import dataclass, field
from typing import Optional

@dataclass
class Symbol:
    name: str
    defined: bool
    value: Optional[int] = None
    obj_file: str = ""

@dataclass
class Linker:
    object_files: list = field(default_factory=list)
    symbol_table: dict = field(default_factory=dict)  # global view
    base_address: int = 0x4000
    errors: list = field(default_factory=list)
    
    def add_object(self, name: str, exports: list, references: list):
        self.object_files.append(name)
        for sym_name, addr in exports:
            if sym_name in self.symbol_table and self.symbol_table[sym_name].defined:
                self.errors.append(f"Duplicate symbol: {sym_name}")
            else:
                self.symbol_table[sym_name] = Symbol(sym_name, True, addr, name)
        for ref in references:
            if ref not in self.symbol_table:
                self.symbol_table[ref] = Symbol(ref, False, obj_file=name)
    
    def link(self):
        unresolved = [s for s in self.symbol_table.values() if not s.defined]
        if unresolved:
            for sym in unresolved:
                self.errors.append(f"Undefined reference: '{sym.name}' (needed by {sym.obj_file})")
        if self.errors:
            print("LINK ERRORS:")
            for e in self.errors:
                print(f"  {e}")
            return False
        print("Link successful!")
        print("Symbol table:")
        for name, sym in sorted(self.symbol_table.items()):
            print(f"  {name:20} @ 0x{sym.value or 0:04x}  ({sym.obj_file})")
        return True

linker = Linker()
linker.add_object("math.o",
    exports=[("add", 0x1000), ("mul", 0x1020)],
    references=[])
linker.add_object("main.o",
    exports=[("main", 0x2000)],
    references=["add", "mul"])  # printf still missing — simulate no libc
linker.link()
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

**Critical Thinking Questions (CTQs) — Model 4**

1. What does "linking" accomplish? In one or two sentences, describe the linker's job using the vocabulary from this model (symbol table, undefined references, object files).

2. The `link()` method above reports a link error because `printf` is never added as an export. In a real build, how would you fix this? What does "linking against libc" mean in practice?

3. What is a "duplicate symbol" error, and when does it occur? Give a realistic scenario in which two object files might accidentally define the same symbol name.

> **Watch out!** A common source of duplicate-symbol errors in C is a **function definition placed in a header file** (`.h`) that is included in multiple `.c` files. Each `.c` file compiles the definition into its own `.o`, and the linker finds two copies. The fix is to put only *declarations* (prototypes) in header files and *definitions* in exactly one `.c` file. C's `inline` keyword or `static` modifier can also scope a definition to a single translation unit.

4. **Static linking** copies library code directly into the executable at link time. **Dynamic linking** leaves references unresolved until the program is loaded or run. List one advantage and one disadvantage of each approach. (Think about: executable size, memory usage when multiple programs use the same library, and ease of updating the library.)

---

#### Model 5: Static vs. Dynamic Linking and Python's Import System

**Intuition:** Static linking is like photocopying the relevant pages of a reference book into your own report — every reader of your report gets a self-contained document, but your report is bulkier and cannot benefit from corrections made to the original book later. Dynamic linking is like writing "see the library's copy of *Reference Book X*, page 47" — your report is slim, multiple readers share the same library book, and if the library updates its copy everyone benefits automatically. Python's `import` system is the clearest high-level example of dynamic linking: modules are found and loaded on demand, cached so they are only loaded once, and swappable by inserting a replacement into `sys.modules`.

In static linking, all dependencies are baked into the executable at build time. In dynamic linking, the operating system's **dynamic linker/loader** (e.g., `ld.so` on Linux) resolves symbol references at load time or even at first use (lazy binding). Python's `import` statement is a high-level version of dynamic linking: Python searches `sys.path` for modules, loads them on demand, and caches them in `sys.modules`.

| Concept | OS Dynamic Linking | Python Import |
|---------|-------------------|---------------|
| Search path | `LD_LIBRARY_PATH` | `sys.path` |
| Loaded library cache | `ld.so` internal table | `sys.modules` |
| Lazy loading | Lazy binding (PLT/GOT) | Import on first `import` statement |
| Injecting a fake library | `LD_PRELOAD` | Inserting into `sys.modules` |

```python
import sys
import importlib
import os

# Python's import system = dynamic linking
# sys.path is the "library search path" (like LD_LIBRARY_PATH)
print("Python module search path (sys.path):")
for p in sys.path[:5]:
    print(f"  {p}")

# Finding a module = symbol lookup in dynamic library
spec = importlib.util.find_spec("math")
if spec:
    print(f"\nmath module found at: {spec.origin}")
    print(f"math module loader: {type(spec.loader).__name__}")

# Demonstrate lazy loading: the module isn't loaded until you import it
print(f"\n'json' in sys.modules before import: {'json' in sys.modules}")
import json
print(f"'json' in sys.modules after import:  {'json' in sys.modules}")

# sys.modules is the "dynamic linker cache" — modules loaded once
import math as m1
import math as m2
print(f"\nm1 is m2 (same object, loaded once): {m1 is m2}")

# Simulating LD_PRELOAD: inject a module into sys.modules
class FakeMath:
    pi = 3.0  # "wrong" value
    def sqrt(self, x): return x ** 0.5

sys.modules['math_fake'] = FakeMath()
import importlib
fake = importlib.import_module('math_fake')
print(f"\nFakeMath.pi = {fake.pi}")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

**Critical Thinking Questions (CTQs) — Model 5**

1. How is Python's `sys.path` analogous to the operating system's `LD_LIBRARY_PATH`? What would happen if you removed all entries from `sys.path`?

2. What role does `sys.modules` play? How is it analogous to the dynamic linker's loaded-library cache? Why is it important that `import math` returns the *same object* no matter how many times you call it?

3. **Lazy loading** means a module is not imported until the `import` statement is actually reached during execution (not when the program starts). When would lazy loading be beneficial? Can you think of a scenario where eager loading (loading everything at startup) might be preferable?

4. The code above injects a `FakeMath` class into `sys.modules['math_fake']`. On Linux, `LD_PRELOAD` allows you to inject a shared library that overrides symbols from other libraries. What **security concern** does this technique raise in both contexts? How do operating systems and language runtimes defend against abuse of this mechanism?

---

#### Multiple Choice

**Question 1**

[[MC]] During compilation, what does a **symbol table** contain?

[( )] The names of all variables, guaranteed to be unique across all files
[(X)] Names and addresses of defined and referenced symbols in a translation unit
[( )] The machine-code addresses of all function calls in the final executable
[( )] A mapping from variable names to their data types

---

**Question 2**

[[MC]] CPython uses a **stack-based** virtual machine. Which of the following best describes how a binary operation like `BINARY_ADD` works in this model?

[( )] It reads two named registers, adds them, and writes the result to a third register
[(X)] It pops two values from the top of the stack, adds them, and pushes the result back
[( )] It looks up both operands by name in the local variable table and stores the sum
[( )] It increments a single accumulator register by the value on top of the stack

---

**Question 3**

[[MC]] Which of the following is the most accurate distinction between **static linking** and **dynamic linking**?

[( )] Static linking is used only for C programs; dynamic linking is used only for interpreted languages
[( )] In static linking, the linker checks for undefined symbols but does not resolve them until runtime
[(X)] In static linking, library code is copied into the executable at build time; in dynamic linking, references are resolved at load time or runtime by the OS loader
[( )] Dynamic linking is always faster at runtime because the library code is pre-compiled

---

**Question 4**

[[MC]] What does `dis.dis(func)` display?

[( )] The source code of `func` with syntax highlighting
[( )] A call graph showing which functions `func` calls
[(X)] The CPython bytecode instructions that implement `func`, including offsets, opcodes, and operands
[( )] The compiled machine code (assembly) that the CPU will execute

---

#### Exercises

**Exercise 1: Implement a Simple Stack-Based Virtual Machine**

Write a `SimpleVM` class with a Python `list` as its stack and methods for the following opcodes: `PUSH(val)`, `POP()`, `ADD()`, `MUL()`, `DUP()` (duplicate top of stack), and `PRINT()` (print and discard top of stack).

Then, "compile" the expression `(3 + 4) * 2` to a list of instructions and execute them using your VM. Verify that the final printed result is `14`.

**Starter code:**

```python
class SimpleVM:
    def __init__(self):
        self.stack = []
    
    def PUSH(self, val):
        # TODO: push val onto self.stack
        pass
    
    def POP(self):
        # TODO: pop and return the top value
        pass
    
    def ADD(self):
        # TODO: pop two values, push their sum
        pass
    
    def MUL(self):
        # TODO: pop two values, push their product
        pass
    
    def DUP(self):
        # TODO: duplicate the top of the stack
        pass
    
    def PRINT(self):
        # TODO: pop and print the top value
        pass
    
    def run(self, program):
        for instr, *args in program:
            getattr(self, instr)(*args)

# "Compile" (3 + 4) * 2 to instructions
program = [
    ("PUSH", 3),
    ("PUSH", 4),
    ("ADD",),
    ("PUSH", 2),
    ("MUL",),
    ("PRINT",),
]

vm = SimpleVM()
vm.run(program)
# Expected output: 14
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

**Exercise 2: Add a Relocation Table to ObjectFile**

In a real object file, the compiler doesn't know the final addresses of symbols in other modules. It leaves **relocations**: placeholders in the code that the linker must patch. Extend the `ObjectFile` class from Model 3 to track a relocation table — a list of `(instruction_offset, symbol_name)` pairs.

Then implement a `patch(symbol_table)` method on `ObjectFile` that iterates over the relocations and prints what address would be written at each offset once the linker has resolved all symbols.

**Starter code:**

```python
from dataclasses import dataclass, field
from typing import Optional

@dataclass
class Symbol:
    name: str
    defined: bool
    value: Optional[int] = None
    exported: bool = True

@dataclass
class ObjectFile:
    name: str
    symbols: dict = field(default_factory=dict)
    relocations: list = field(default_factory=list)  # NEW: list of (offset, sym_name)
    
    def define(self, name: str, value: int, exported: bool = True):
        self.symbols[name] = Symbol(name, defined=True, value=value, exported=exported)
    
    def reference(self, name: str):
        if name not in self.symbols:
            self.symbols[name] = Symbol(name, defined=False)
    
    def add_relocation(self, offset: int, symbol_name: str):
        # TODO: record that at byte `offset` in this object file's code,
        # the address of `symbol_name` must be patched in
        pass
    
    def patch(self, global_symbol_table: dict):
        # TODO: for each (offset, sym_name) in self.relocations,
        # look up sym_name in global_symbol_table and print:
        # "Patch offset 0x{offset:04x}: write address 0x{addr:04x} (symbol '{sym_name}')"
        pass

# Test
math_obj = ObjectFile("math.o")
math_obj.define("add", 0x1000)
math_obj.define("mul", 0x1020)

main_obj = ObjectFile("main.o")
main_obj.define("main", 0x2000)
main_obj.reference("add")
main_obj.reference("mul")
main_obj.add_relocation(0x2010, "add")  # at offset 0x2010, need address of 'add'
main_obj.add_relocation(0x2018, "mul")  # at offset 0x2018, need address of 'mul'

# Build global symbol table from math.o
global_syms = {**math_obj.symbols, **main_obj.symbols}
main_obj.patch(global_syms)
# Expected:
# Patch offset 0x2010: write address 0x1000 (symbol 'add')
# Patch offset 0x2018: write address 0x1020 (symbol 'mul')
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

**Exercise 3: Implement a DynamicLinker Class**

Implement a `DynamicLinker` class that simulates the runtime behavior of a dynamic linker. It should support:

- `load_library(name, exports)`: Register a library by name with a dict mapping symbol names to addresses.
- `resolve(symbol)`: Search all loaded libraries for the symbol and return its address, or raise an error if not found.
- `show_loaded()`: Print all currently loaded libraries and their exported symbols.

Test it by loading a simulated `libmath.so` and `libc.so`, then resolving several symbols.

**Starter code:**

```python
class DynamicLinker:
    def __init__(self):
        self.libraries = {}  # name -> {symbol: address}
    
    def load_library(self, name: str, exports: dict):
        # TODO: store the library's exports in self.libraries
        pass
    
    def resolve(self, symbol: str) -> int:
        # TODO: search self.libraries for the symbol
        # Return its address if found
        # Raise a RuntimeError if not found in any library
        pass
    
    def show_loaded(self):
        # TODO: print each loaded library and its exported symbols
        pass

# Test
dl = DynamicLinker()
dl.load_library("libmath.so", {"sqrt": 0x7f001000, "pow": 0x7f001040, "log": 0x7f001080})
dl.load_library("libc.so",    {"printf": 0x7f002000, "malloc": 0x7f002200, "free": 0x7f002300})

dl.show_loaded()

print("\nResolving symbols:")
for sym in ["printf", "sqrt", "malloc", "log"]:
    addr = dl.resolve(sym)
    print(f"  {sym:10} -> 0x{addr:08x}")

# Try resolving an undefined symbol
try:
    dl.resolve("undefined_func")
except RuntimeError as e:
    print(f"\nExpected error: {e}")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

**Exercise 4: Walk an AST to Find All Function Calls**

Use Python's `ast` module to walk an AST and collect all `Call` nodes, printing the name of each function being called and the line number. This simulates the work a compiler does when it encounters a call instruction and must generate a reference to the callee's symbol.

**Starter code:**

```python
import ast

source = """
import math

def hypotenuse(a, b):
    return math.sqrt(a**2 + b**2)

def area_of_circle(r):
    return math.pi * r**2

def main():
    h = hypotenuse(3, 4)
    a = area_of_circle(5)
    print(f"Hypotenuse: {h}, Area: {a}")
    result = sorted([3, 1, 2], key=lambda x: -x)
    print(result)

main()
"""

tree = ast.parse(source)

print("Function calls found (simulating symbol reference collection):")
print(f"{'Line':>5}  {'Call'}")
print("-" * 40)

for node in ast.walk(tree):
    if isinstance(node, ast.Call):
        # TODO: determine the name of the function being called
        # Hint: node.func may be an ast.Name (func.id) or ast.Attribute (func.attr)
        # Print the line number (node.lineno) and the call name
        pass

# Expected output should include calls to:
# math.sqrt, math.pi (attribute access), hypotenuse, area_of_circle,
# print (twice), sorted, main
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

---

#### Reflection

> **Prompt:** "Compilation is a pipeline: scan → parse → semantic analysis → optimization → code generation → link. After exploring Python's bytecode and a simulated linker, which stage surprises you most, and why?"

Write 3–4 sentences. Consider: What did you assume was simple that turns out to be complex? What new appreciation do you have for language runtime design? How do these concepts change the way you think about writing programs?

---

#### Further Reading

- **Compilers: Principles, Techniques, and Tools** (Aho, Lam, Sethi, Ullman — the "Dragon Book"), Chapter 2: A Simple Syntax-Directed Translator
- **Dragon Book**, Chapter 8: Intermediate Code Generation
- [Python `dis` — Disassembler for Python bytecode](https://docs.python.org/3/library/dis.html) — official documentation
- [Python `ast` — Abstract Syntax Trees](https://docs.python.org/3/library/ast.html) — official documentation
- **Ian Lance Taylor's Linkers blog series** — a deep, technical walkthrough of how linkers work in practice (search "Ian Lance Taylor linkers blog")
- **"Static and Dynamic Linking" video:** https://youtube.com/watch?v=UdMRcJwvWIY
- [CPython internals: how bytecode is executed](https://devguide.python.org/internals/compiler/) — CPython developer's guide
- **"Linkers and Loaders"** by John Levine — a book-length treatment of everything from object file formats to dynamic linking
