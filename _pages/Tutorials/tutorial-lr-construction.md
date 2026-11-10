---
layout: textbook
permalink: /Tutorials/LRConstruction
title: "CS374: Building an LR Parser from the Grammar Up"

info:
  coursenum: CS374
  eyebrow: "Tutorial"
  numbering: false
  objectives:
    - To explain what an LR item is and why the dot carries all of the parser's state
    - To implement closure as a fixed-point computation and say why a single pass is wrong
    - To implement GOTO and build the canonical collection of item sets
    - To compute FOLLOW and explain why an SLR parser cannot fill in a reduce cell without it
    - To build ACTION and GOTO tables from three rules, and to record conflicts rather than overwrite them
    - To write the shift-reduce driver and read its stack-input-action trace
    - To diagnose a shift-reduce and a reduce-reduce conflict down to the state and the two items that disagree
    - To place SLR(1) against LALR(1) and LR(1), and to say which one Bison builds
    - To build a grammar's item NFA and turn it into the LR DFA with the subset construction
    - To find the next state after a reduce from the production number and the state the pop exposes
    - To build a top-down PDA from a grammar, and to describe the LR parser as a PDA

readings:
  - rtitle: "Allison, Ch. 5: Pushdown Automata, and Ch. 6 §6.3: Equivalence of PDAs and Context-Free Grammars"
  - rtitle: "Compilers: Principles, Techniques, and Tools (Aho, Lam, Sethi, Ullman), Chapter 4.6-4.7"
  - rtitle: "Bison Manual: Understanding Your Parser (the .output automaton)"
    rlink: "https://www.gnu.org/software/bison/manual/html_node/Understanding.html"

tags:
  - parser
  - lr
  - parsing
  - tables
  - pipeline
---

# Building an LR Parser from the Grammar Up

This tutorial is a companion to the **Parser assignment**, where you build LR(1) tables and a shift-reduce driver.  It builds SLR(1) (Simple LR with one token of lookahead), which is simpler, on a *different, smaller grammar* than the assignment uses.  That is deliberate.  You can read every line here, run it, and take it apart, and the assignment's work is still yours to do.  The last section says how SLR(1) and LR(1) differ.

You already know recursive descent from Part 2.  This tutorial takes you from "I wrote one function per non-terminal" to "I built the table a generator emits, and I know why each cell holds what it holds."

Two companions sit beside it.  The [Parsing, Part 2 activity]({{ site.lia_viewer_url }}{{ site.raw_pages_url }}Activities/liascript-parsing2.md) builds the assignment's larger grammar by hand and prints the correct closure, item sets, FOLLOW sets, and table, which makes it the answer key for Part 4.  The [Flex and Bison tutorial]({{ site.baseurl }}/Tutorials/FlexAndBison) goes the other way, generating a parser with real tools, and its appendix reads an actual `bison -v` automaton.

Throughout, the grammar is:

```
0: S' -> E          the augmented start production
1: E  -> E + T
2: E  -> T
3: T  -> n
```

Four productions, one left-recursive rule, no precedence.  It is the smallest grammar that still shows every part of the algorithm.

---

## Section 1: Why a table at all

A recursive descent parser keeps its state in the Python call stack.  When `parse_expr` calls `parse_term`, the fact that "we are partway through an expression and expecting a term" lives in a stack frame you never look at directly.  That works, and Part 2 proves it works, but it has two costs.  Left recursion loops forever, so you rewrote the grammar to suit the parser.  And the parser's knowledge is implicit, so there is nothing to inspect when it goes wrong.

An LR parser inverts both.  It keeps an explicit stack of states, and it decides what to do by looking up one cell of a table.  The table is built once, before any input arrives, from the grammar alone.  At parse time all of the reasoning has already happened, which is why generators emit tables.  It is also why left recursion is natural here rather than merely tolerated.  The parser reduces `E + T` to `E` whenever it sees one completed on the stack, and never has to guess ahead.

Two moves are available at every step.  **Shift** pushes the next input token onto the stack.  **Reduce** recognizes that the top of the stack matches some production's right-hand side, pops it, and pushes that production's left-hand non-terminal.  Accept when the stack holds the start symbol and the input is exhausted.  The parse is a rightmost derivation discovered in reverse, so the tree grows from the leaves upward.

---

## Section 2: Items, and why the dot is the whole idea

An **item** is a production with a dot somewhere in its right-hand side.  The dot marks how much of that production the parser has already seen.

`E -> E . + T` says: we are working on production 1, we have an `E` on the stack, and we expect a `+` next.  `E -> E + T .` says: production 1 is complete, and a reduce is available.

That is the entire representation.  A parser state is a *set* of items, because at a given moment several productions may still be live, and the parser commits to none of them until the input decides.

Represent an item as the pair `(production_index, dot_position)` and a state as a `frozenset` of items.  The `frozenset` matters: states are compared for equality and used as dictionary keys, and a mutable `set` cannot be either.

```python
PRODUCTIONS = [("S'", ["E"]), ("E", ["E", "+", "T"]), ("E", ["T"]), ("T", ["n"])]
NONTERMINALS = {"S'", "E", "T"}
TERMINALS = {"n", "+", "$"}

def show_item(item):
    """Render (prod, dot) as 'E -> E . + T'."""
    lhs, rhs = PRODUCTIONS[item[0]]
    body = rhs[:item[1]] + ["."] + rhs[item[1]:]
    return "%s -> %s" % (lhs, " ".join(body))
```

Write this helper first.  Every checkpoint below is something you read, and an item printed as a tuple is unreadable.

---

## Section 3: Closure, and why one pass is wrong

**The rule.** If the dot sits immediately before a non-terminal, the parser is also about to begin parsing that non-terminal, so add every production for it with the dot at the front.

**Why it is a fixed point.** The rule feeds itself.  Start from `S' -> . E`.  The dot sits before `E`, so add `E -> . E + T` and `E -> . T`.  That second item now has a dot before `T`, which was not true of anything in the original set, so the rule applies again and adds `T -> . n`.  A single pass over the starting item would have stopped after two additions and produced a state that is wrong.

So closure loops until a full pass adds nothing.  That is the definition of a fixed point, and it is the single most common place this algorithm is implemented incorrectly.

```python
def closure(items):
    """Close a set of items under the dot-before-a-nonterminal rule."""
    result, changed = set(items), True
    while changed:
        changed = False
        for p, dot in list(result):            # list(): we mutate while iterating
            lhs, rhs = PRODUCTIONS[p]
            if dot >= len(rhs) or rhs[dot] not in NONTERMINALS:
                continue                        # completed, or dot before a terminal
            for q, (qlhs, _) in enumerate(PRODUCTIONS):
                if qlhs == rhs[dot] and (q, 0) not in result:
                    result.add((q, 0))
                    changed = True              # only when the set actually grew
    return frozenset(result)
```

Line 13, `changed = True` under the `not in result` test on line 11, is the fixed-point guard.  Setting `changed = True` unconditionally gives you an infinite loop; setting it only when `add` was new gives you termination.

> **You should see.** `closure({(0, 0)})` returns four items:
>
> ```
> E -> . E + T
> E -> . T
> S' -> . E
> T -> . n
> ```
>
> That set *is* state `I0`.  Read what it means: standing at the very start of the input, the parser is simultaneously about to parse an `E`, and a `T`, and an `n`.  It has committed to nothing.

> **If you see two items instead of four**, your loop is a single pass.  Trace the chain above: `S' -> . E` pulls in the `E` productions, and only then does `E -> . T` pull in the `T` production.

---

## Section 4: GOTO, the transition function

`GOTO(I, X)` answers "if the parser is in state `I` and consumes `X`, where does it land?"  Advance the dot past `X` in every item that has the dot before `X`, then take the closure of the result.

```python
def goto(state, symbol):
    """Advance the dot past `symbol` in every item that has the dot before it."""
    moved = {(p, dot + 1) for p, dot in state
             if dot < len(PRODUCTIONS[p][1]) and PRODUCTIONS[p][1][dot] == symbol}
    return closure(moved) if moved else frozenset()
```

The closure on the last line is not decoration.  After advancing past `+` in `E -> E . + T` you hold `E -> E + . T`, whose dot now sits before a non-terminal, so the `T` productions must come in.  Skip that closure and you get states that look almost right and a table that is quietly broken.

---

## Section 5: The canonical collection

Now enumerate every reachable state.  Start from `closure({(0, 0)})`, and for each state and each grammar symbol compute `GOTO`.  Each set you have not seen becomes a new state.  Stop when nothing new appears.

Two details decide whether your numbering matches anyone else's.  Walk the symbols in a fixed order, and number states in discovery order.  Change either and you get the same machine with different labels, which is correct but harder to compare against a printed table.

```python
SYMBOLS = ["n", "+", "E", "T"]          # fixed order fixes the numbering

def build_states():
    """Return (states, transitions): the canonical collection and the GOTO edges."""
    start = closure({(0, 0)})
    states, index, transitions, work = [start], {start: 0}, {}, [0]
    while work:
        i = work.pop(0)
        for sym in SYMBOLS:
            t = goto(states[i], sym)
            if not t:
                continue
            if t not in index:                  # a state we have not seen
                index[t] = len(states)
                states.append(t)
                work.append(index[t])
            transitions[(i, sym)] = index[t]
    return states, transitions
```

> **You should see.** Six states.
>
> ```
> I0: E -> . E + T , E -> . T , S' -> . E , T -> . n
> I1: T -> n .
> I2: E -> E . + T , S' -> E .
> I3: E -> T .
> I4: E -> E + . T , T -> . n
> I5: E -> E + T .
> ```
>
> `I2` is worth a second look.  It holds a completed item (`S' -> E .`, which on `$` means accept) beside an item expecting more input (`E -> E . + T`, which on `+` means shift).  The lookahead token alone decides which fires.  That coexistence is the shift-reduce decision, sitting in one state you just built.

> **If you find fewer than six states**, you are probably comparing states with `==` on mutable sets, or not keying your index by the `frozenset`, so equal states are being merged or duplicated.  **More than six** usually means `goto` is not taking the closure.

---

## Section 6: FOLLOW, and why SLR needs it

A completed item says a reduce is *available*, not that it is *correct*.  Consider `I3 = { E -> T . }`.  Should the parser reduce `E -> T` on every possible token?  No: reducing on a token that can never legally follow an `E` would accept nonsense.

An SLR(1) parser resolves this with the simplest rule available: reduce by a completed item exactly on the tokens in the FOLLOW set of its left-hand side.  Formally, for a completed item $$A \rightarrow \alpha\,.$$ in state $$i$$,

$$
\text{ACTION}[i][a] = \text{reduce } A \rightarrow \alpha \quad \text{for every } a \in \text{FOLLOW}(A)
$$

So you cannot fill in a single reduce cell before computing FOLLOW.  FOLLOW in turn needs FIRST, and both are fixed-point computations for the same reason closure is: adding to one set can enable an addition to another.

Seed `FOLLOW(S')` with `$`, the end-of-input marker.  Then, for each production $$A \rightarrow \alpha B \beta$$: everything in $$\text{FIRST}(\beta)$$ goes into $$\text{FOLLOW}(B)$$, and if $$B$$ is last, everything in $$\text{FOLLOW}(A)$$ goes into $$\text{FOLLOW}(B)$$.

> **You should see.** `FOLLOW(E) = { $ + }` and `FOLLOW(T) = { $ + }`.
>
> Read where each token came from.  `$` reaches `FOLLOW(E)` from the seed through `S' -> E`, and `+` reaches it from `E -> E + T`, where `E` is followed directly by a terminal.  `FOLLOW(T)` inherits both through `E -> T`, where `T` sits last.

---

## Section 7: The table, from three rules and one refusal

Everything now reads straight off the states.

1. A dot before a **terminal** `a` in state `i`, with an edge to `j`, gives `ACTION[i][a] = ("s", j)`.
2. A **completed** item for production `p`, other than production 0, gives `ACTION[i][a] = ("r", p)` for every `a` in `FOLLOW` of its left-hand side.
3. The completed item `S' -> E .` gives `ACTION[i]["$"] = ("acc",)`.
4. If a cell already holds a *different* action, that is a **conflict**.  Record it and leave the existing entry alone.

Rule 4 is the one that matters, and it is where a generator differs from a toy.  A parser that silently keeps whichever action it wrote last will happily parse an ambiguous grammar, badly, and never tell you.  Recording the collision is what turns your code into a diagnostic tool, and Section 9 is where that pays off.

> **You should see**, for the six-state machine, an empty conflict list and this table:
>
> | State | `n` | `+` | `$` | -> E | -> T |
> |---|---|---|---|---|---|
> | 0 | s1 | | | 2 | 3 |
> | 1 | | r3 | r3 | | |
> | 2 | | s4 | **acc** | | |
> | 3 | | r2 | r2 | | |
> | 4 | s1 | | | | 5 |
> | 5 | | r1 | r1 | | |
>
> Row 2 is the accept row and the shift row at once, which is `I2`'s two items showing up as two cells.  Rows 1, 3, and 5 are pure reduce rows, and each one reduces on exactly `{ +, $ }`, which is the FOLLOW set doing its job.

> **If reduce actions appear under every terminal**, you skipped Section 6 and are reducing unconditionally.  That table parses valid input correctly, which is what makes the bug so easy to miss.

---

## Section 8: The driver

The driver is smaller than the construction.  Keep a stack of state numbers beside a stack of symbols, read one token of lookahead, and loop on `ACTION[state][token]`:

- **Shift** pushes the token and the target state onto the two stacks, and advances the input.
- **Reduce** by $$A \rightarrow \alpha$$ pops $$|\alpha|$$ entries from both stacks, then pushes `A` with `GOTO[exposed_state][A]`.  Pop first, then read the newly exposed state; reading it before the pop is the classic off-by-one here.
- **Accept** ends the loop.
- Anything else is a syntax error.  Name the state and the token, because that pair is the whole diagnosis.

> **You should see**, for `n + n`:
>
> | Stack | Input | Action |
> |---|---|---|
> | | `n + n $` | shift |
> | `n` | `+ n $` | reduce `T -> n` |
> | `T` | `+ n $` | reduce `E -> T` |
> | `E` | `+ n $` | shift |
> | `E +` | `n $` | shift |
> | `E + n` | `$` | reduce `T -> n` |
> | `E + T` | `$` | reduce `E -> E + T` |
> | `E` | `$` | **accept** |
>
> Two things in that trace are the whole point.  The first `n` is reduced all the way up through `T -> n` and `E -> T` *before* the `+` is shifted, because the table says so in rows 1 and 3.  And `E -> E + T` reduces a left-recursive production without any of the rewriting Part 2 required, which is the promise from Section 1 being kept.

---

## Section 9: Conflicts, and what they look like from inside

A conflict is not an error message a tool invents.  It is two items in one state that disagree, and now you can see both.

**Shift-reduce.** Add `E -> T + E` beside `E -> E + T`, making `+` both left and right associative:

```
added production 4: E -> T + E
states: 8   conflicts: 2
  state 3, token '+': shift-reduce  (s5 vs r2)
    items in state 3:
      E -> T .
      E -> T . + E
```

Read the two items.  `E -> T .` says production 2 is complete, so reduce.  `E -> T . + E` says a `+` is expected next, so shift.  On the token `+`, both apply, and nothing in the grammar says which.  A precedence declaration can resolve this one, which is exactly what `%left` in a Bison file does: it tells the generator to prefer one action in a state like this, without changing the grammar.

**Reduce-reduce.** Instead add `E -> n` beside `T -> n`:

```
added production 4: E -> n
states: 7   conflicts: 2
  state 1, token '$': reduce-reduce  (r3 vs r4)
    items in state 1:
      E -> n .
      T -> n .
```

Here both items are complete, and `FOLLOW(E)` and `FOLLOW(T)` overlap, so on `$` the parser has two finished productions and no basis to choose.  No precedence declaration helps: the grammar genuinely says an `n` on its own is both a `T` and an `E`.  This one needs the grammar restructured.

**Both kinds, as Bison reports them.**  Here are two small grammars you can run yourself.  The first is ambiguous about `id + id * id`:

```text
%token ID
%%
e : e '+' e
  | e '*' e
  | ID
  ;
```

```text
$ bison -v sr.y
sr.y: warning: 4 shift/reduce conflicts [-Wconflicts-sr]
```

After `e + e`, with `*` next, the parser can reduce to `(id + id) * id` or shift toward `id + (id * id)`.  The `-v` flag writes `sr.output`, which lists each state and its conflicts.  Giving each precedence level its own nonterminal removes the ambiguity, and Bison then prints nothing:

```text
%token ID
%%
e : e '+' t
  | t
  ;
t : t '*' f
  | f
  ;
f : ID
  ;
```

The second grammar is ambiguous about what one token *is*:

```text
%token ID
%%
s : a b
  | c d
  ;
a : ID ;
c : ID ;
b : ID ;
d : ID ;
```

```text
$ bison -v rr.y
rr.y: warning: 1 reduce/reduce conflict [-Wconflicts-rr]
rr.y:7.5-6: warning: rule useless in parser due to conflicts [-Wother]
```

After the first `ID`, the parser has two finished productions, `a : ID` and `c : ID`, and the next token is `ID` either way.  Bison keeps the rule listed first, so `c : ID` can never fire, which is what "useless" means here.  Distinct tokens let the next token decide, and Bison then prints nothing:

```text
%token ID_A ID_C ID_B ID_D
%%
s : a b
  | c d
  ;
a : ID_A ;
c : ID_C ;
b : ID_B ;
d : ID_D ;
```

That distinction is the practical lesson.  A shift-reduce conflict is often a precedence question you can declare your way out of.  A reduce-reduce conflict is usually a design problem in the grammar.

---

## Section 10: SLR, LALR, and what Bison actually builds

What you built is **SLR(1)**, the simplest useful member of the LR family.  Its one simplification is the one from Section 6: it reduces on all of `FOLLOW(A)`, regardless of which state it is in.

That is sometimes too coarse.  A token can be in `FOLLOW(A)` globally while being impossible at *this* particular point in the parse, and SLR will place a reduce action there anyway.  The result is a conflict that is not really a conflict, and a grammar SLR rejects that a stronger method accepts.

**LR(1)** fixes it by carrying a lookahead token inside each item, so `[A -> α . , a]` means "reduce only on `a`".  It is precise and its state count explodes.  **LALR(1)** merges LR(1) states that share the same items but differ only in lookahead, keeping almost all of the precision at SLR's state count.  That trade is why **LALR(1) is what Bison and PLY build**.  It is also why `bison -v` output repays reading once you have built one of these by hand.  The states in `mininote.output` are the same kind of object as the ones you just enumerated.

The Parser assignment builds LR(1) directly, on a small enough grammar that the state count stays manageable.  It does not ask you for LALR, which is the interesting next step if you want it.

### LR(1) items, by hand

Here is the move from SLR to LR(1) on the smallest grammar that shows it.

```text
0  S' -> S
1  S  -> C C
2  C  -> c C
3  C  -> d
```

An LR(1) item adds a lookahead: `[C -> d ., c]` means "I have seen a complete `C`, and I reduce it only if the next token is `c`."  Closure changes in one place.  From an item `[A -> x . B y, a]`, you add `[B -> . z, b]` for every production `B -> z`, where `b` is each token that can come right after this `B`.  That is what `y` can begin with, or `a` if `y` is empty.

Start with `[S' -> . S, $]`.  The dot is before `S`, nothing follows it, so `S`'s item gets `$`.  In `[S -> . C C, $]` the dot is before a `C`, and another `C` follows, so its lookaheads are `FIRST(C)`, which is `c` and `d`.  Those items have the dot before a terminal, so nothing else is added:

```text
[S' -> . S, $]
[S  -> . C C, $]
[C  -> . c C, c]   [C -> . c C, d]
[C  -> . d, c]     [C -> . d, d]
```

Goto moves the dot and keeps the lookahead, and then closes.  Move past the first `C`, and the second `C` now has nothing after it, so the lookahead `$` comes down from the item above it:

```text
[S -> C . C, $]
[C -> . c C, $]
[C -> . d, $]
```

Now follow `d` from both of those states.  The production is the same, and the states differ:

```text
from the first state:   [C -> d ., c]  [C -> d ., d]
from the second state:  [C -> d ., $]
```

The machine remembers which `C` it is reading.  After the first `C` another must come, so `$` is an error there and the table has no reduce on it.  After the second, only `$` can follow.  SLR would reduce on all of `FOLLOW(C)` in both places.  This precision is what LR(1) buys, and the price is the state count: this grammar has ten LR(1) states.

---

## Section 11: Taking this to the assignment's grammar

The Parser assignment has you write these functions for LR(1), on a grammar with two precedence levels and parentheses.  It computes about thirty states, which is too many to do by hand, so three habits save time.

Compute one small result and check it before you go on.  The assignment gives you a check after each function for this reason.

Keep every piece that repeats until nothing changes in the same shape, because FIRST sets, closure, and the set of states are all *fixed points*: you start small and keep going until a whole pass adds nothing.

And when the table is done, read one row.  Find the state holding both `E -> T .` and `T -> T . * F`.  It shifts on `*` and reduces on `+`, and that one row is where `*` binds tighter than `+`.  Nothing decided it at parse time.  It fell out of the item sets, which is the result this whole tutorial exists to make believable.

---

## Section 12: A second grammar, by hand

Here is the whole construction once more on a small grammar with no arithmetic in it, so you can see every state.  References: [LR parsing, part 1](https://www.youtube.com/watch?v=APJ_Eh60Qwo) and [part 2](https://www.youtube.com/watch?v=0kiTNN2kHyY).

```text
S' -> S        (production 0, the augmented start)
S  -> X y x    (production 1)
X  -> x X      (production 2)
X  -> y        (production 3)
```

Because this is a bottom-up parser (the R in LR), we need to know where we are in each production, and whether the whole production has been read.  The `.` marks where we are.  There are finitely many places to put it, so the dots give us a finite set of states.

*State 0* starts from `S' -> .S`.  The dot sits to the left of `S`, so we add the `S` productions, and then we repeat for any nonterminal with a dot before it.  This is the closure:

```text
State 0:  S' -> .S
          S  -> .X y x
          X  -> .x X
          X  -> .y
```

*The other states.*  From each state, take one transition per symbol after a dot: move the dot over that symbol, then take the closure.

```text
State 1 (0 on S):  S' -> S .
State 2 (0 on X):  S  -> X . y x
State 3 (0 on x):  X  -> x . X
                   X  -> .x X
                   X  -> .y
State 4 (0 on y):  X  -> y .
State 5 (2 on y):  S  -> X y . x
State 6 (3 on X):  X  -> x X .
State 7 (5 on x):  S  -> X y x .
```

State 3 on `x` comes back to state 3, because the items are the same, and state 3 on `y` goes to state 4.

*The table has one row per state.*  ACTION has a column for each terminal, plus `$` for the end of the string.  GOTO has a column for each nonterminal, leaving out `S'`.  Fill in the state each symbol leads to.  A transition on a terminal is a shift, because the dot has not reached the end of the production.  State 1 accepts on `$`.  In states 4, 6, and 7 the dot has reached the end, so those rows reduce by the production they hold: state 4 is `X -> y .` (production 3), state 6 is `X -> x X .` (production 2), and state 7 is `S -> X y x .` (production 1).  This is LR(0), so a reduce state reduces on every input.

| State | `x` | `y` | `$` | `S` | `X` |
|---|---|---|---|---|---|
| 0 | s3 | s4 | | 1 | 2 |
| 1 | | | acc | | |
| 2 | | s5 | | | |
| 3 | s3 | s4 | | | 6 |
| 4 | r3 | r3 | r3 | | |
| 5 | s7 | | | | |
| 6 | r2 | r2 | r2 | | |
| 7 | r1 | r1 | r1 | | |

Notice that each reduce fills its whole row, which is LR(0): the rule from Section 7 limited reduces to FOLLOW, and this table has not applied it yet.  It works here because no state mixes a completed item with anything else.  Apply FOLLOW, or carry LR(1) lookaheads, and rows 4 and 6 keep their reduce only on `y`, and row 7 only on `$`.  The states do not change.

### Where the eight states come from: an NFA of items

The states above came from closure and GOTO.  There is a second way to get them, and it uses the construction from the Automata lab: build an NFA from the grammar, then turn it into a DFA with the subset construction.  The DFA that comes out is exactly the eight states above, which shows that closure and GOTO were the subset construction all along.

**Step 1: every item is an NFA state.**  Put the dot in every possible place in every production.  This grammar has eleven items, so the NFA has eleven states, `i0` to `i10`.  The start state is `i0`, the item `S' -> . S`.

**Step 2: two kinds of arrow.**

- *Moving the dot over a symbol is an arrow on that symbol.*  `S -> X . y x` goes to `S -> X y . x` on `y`.  This is the same move as reading one character in a lab NFA, except that the symbol can be a nonterminal.
- *A dot just before a nonterminal `B` gets an ε (epsilon) arrow to every item `B -> . w`.*  The parser is about to start a `B` and has not decided which production it is, so the NFA tries all of them for free.  This is where the nondeterminism comes from.
- An item with the dot at the far right has no arrows out.  It is finished, and it is where a reduce will happen.

| NFA state | Item | Arrows out |
|---|---|---|
| `i0` | `S' -> . S` | on `S` to `i1`; ε to `i2` |
| `i1` | `S' -> S .` | none |
| `i2` | `S -> . X y x` | on `X` to `i3`; ε to `i6` and `i9` |
| `i3` | `S -> X . y x` | on `y` to `i4` |
| `i4` | `S -> X y . x` | on `x` to `i5` |
| `i5` | `S -> X y x .` | none |
| `i6` | `X -> . x X` | on `x` to `i7` |
| `i7` | `X -> x . X` | on `X` to `i8`; ε to `i6` and `i9` |
| `i8` | `X -> x X .` | none |
| `i9` | `X -> . y` | on `y` to `i10` |
| `i10` | `X -> y .` | none |

**Step 3: the subset construction.**  Start with the ε-closure of the start state, then follow each symbol and close again, exactly as in the lab's `run_nfa`.  Closure in Section 3 *is* the ε-closure, and GOTO in Section 4 *is* "move on the symbol, then take the ε-closure."

| DFA state | How it is built | NFA states in it |
|---|---|---|
| 0 | ε-closure of `{i0}`: `i0` reaches `i2`, and `i2` reaches `i6` and `i9` | `i0`, `i2`, `i6`, `i9` |
| 1 | state 0 on `S`: move to `i1`; nothing to close | `i1` |
| 2 | state 0 on `X`: move to `i3` | `i3` |
| 3 | state 0 on `x`: move to `i7`, and `i7`'s ε arrows add `i6` and `i9` | `i6`, `i7`, `i9` |
| 4 | state 0 on `y`, and also state 3 on `y`: move to `i10` | `i10` |
| 5 | state 2 on `y`: move to `i4` | `i4` |
| 6 | state 3 on `X`: move to `i8` | `i8` |
| 7 | state 5 on `x`: move to `i5` | `i5` |

State 3 on `x` moves to `i7` again, which closes to the same three items, so it is state 3 again.  That is the loop on `x` in the DFA.

The program below builds the NFA from the grammar and runs the subset construction on it.

```python
# items_nfa.py: the grammar's item NFA, and the subset construction that turns it into the LR(0) DFA.
PRODS = [("S'", ["S"]), ("S", ["X", "y", "x"]), ("X", ["x", "X"]), ("X", ["y"])]
NONTERMINALS = {"S'", "S", "X"}

# Every item is one NFA state: (production, dot position).
ITEMS = [(p, d) for p, (lhs, rhs) in enumerate(PRODS) for d in range(len(rhs) + 1)]

def show(item):
    lhs, rhs = PRODS[item[0]]
    return lhs + " -> " + " ".join(rhs[:item[1]] + ["."] + rhs[item[1]:])

def edges(item):
    """The NFA's arrows out of one item: one on the symbol after the dot,
    and an epsilon arrow to each production of that symbol if it is a nonterminal."""
    p, d = item
    rhs = PRODS[p][1]
    if d == len(rhs):
        return []                                   # dot at the end: no arrows out
    out = [(rhs[d], (p, d + 1))]                    # move the dot over the next symbol
    if rhs[d] in NONTERMINALS:
        out += [("eps", (q, 0)) for q, (lhs, _) in enumerate(PRODS) if lhs == rhs[d]]
    return out

print("NFA states and arrows:")
for i, item in enumerate(ITEMS):
    arrows = ", ".join("%s -> i%d" % (sym, ITEMS.index(dst)) for sym, dst in edges(item))
    print("  i%-2d %-16s %s" % (i, show(item), arrows or "(none)"))

def eps_closure(states):
    """Follow epsilon arrows until nothing new appears (a visited set, as in the Automata lab)."""
    result, frontier = set(states), list(states)
    while frontier:
        for sym, dst in edges(frontier.pop()):
            if sym == "eps" and dst not in result:
                result.add(dst)
                frontier.append(dst)
    return frozenset(result)

def move(states, symbol):
    return {dst for s in states for sym, dst in edges(s) if sym == symbol}

# Subset construction: each DFA state is the epsilon closure of a set of items.
start = eps_closure({(0, 0)})
dfa, order, work = {}, [start], [start]
while work:
    S = work.pop(0)
    for symbol in ["S", "X", "x", "y"]:
        T = move(S, symbol)
        if T:
            T = eps_closure(T)
            if T not in order:
                order.append(T)
                work.append(T)
            dfa[(order.index(S), symbol)] = order.index(T)

print("\nDFA states (subset construction):")
for n, S in enumerate(order):
    names = ", ".join("i%d" % ITEMS.index(it) for it in sorted(S))
    print("  state %d = [%s]: %s" % (n, names, "; ".join(show(it) for it in sorted(S))))
print("\nDFA arrows:")
for (src, sym), dst in sorted(dfa.items()):
    print("  state %d on %s -> state %d" % (src, sym, dst))
```

It prints:

```text
NFA states and arrows:
  i0  S' -> . S        S -> i1, eps -> i2
  i1  S' -> S .        (none)
  i2  S -> . X y x     X -> i3, eps -> i6, eps -> i9
  i3  S -> X . y x     y -> i4
  i4  S -> X y . x     x -> i5
  i5  S -> X y x .     (none)
  i6  X -> . x X       x -> i7
  i7  X -> x . X       X -> i8, eps -> i6, eps -> i9
  i8  X -> x X .       (none)
  i9  X -> . y         y -> i10
  i10 X -> y .         (none)

DFA states (subset construction):
  state 0 = [i0, i2, i6, i9]: S' -> . S; S -> . X y x; X -> . x X; X -> . y
  state 1 = [i1]: S' -> S .
  state 2 = [i3]: S -> X . y x
  state 3 = [i6, i7, i9]: X -> . x X; X -> x . X; X -> . y
  state 4 = [i10]: X -> y .
  state 5 = [i4]: S -> X y . x
  state 6 = [i8]: X -> x X .
  state 7 = [i5]: S -> X y x .

DFA arrows:
  state 0 on S -> state 1
  state 0 on X -> state 2
  state 0 on x -> state 3
  state 0 on y -> state 4
  state 2 on y -> state 5
  state 3 on X -> state 6
  state 3 on x -> state 3
  state 3 on y -> state 4
  state 5 on x -> state 7
```

The DFA's state numbers come out in the same order as the hand construction, because both take the symbols in the same order.  The NFA is a picture of the grammar, and the DFA is what the parser runs.

### Reading a table entry: `s3`, `r3`, and a bare `1`

A table cell tells the parser what to do next, and there are five kinds of entry. The letter says which action to take, and the number means something different for each letter, so read the letter first.

| Entry | Where it appears | What the number means | What the parser does |
|---|---|---|---|
| `s3` | ACTION, under a terminal | State 3 | **Shift.** Push the current token, push state 3, and move to the next token. This is the only entry that consumes input. |
| `r3` | ACTION, under a terminal or `$` | Production 3 | **Reduce.** The right-hand side of production 3 is on top of the stack. Pop it, push the left-hand side, and then use GOTO to find the next state. The input does not move. |
| `1` (no letter) | GOTO, under a nonterminal | State 1 | **Go to state 1.** Push the state. This entry is only ever read during a reduce, right after the left-hand side has been pushed. |
| `acc` | ACTION, under `$` | Nothing | **Accept.** The whole input is a valid sentence. |
| blank | Anywhere | Nothing | **Syntax error.** No valid sentence continues this way. |

The most common mistake is reading `r3` as "go to state 3." In this grammar, `s3` goes to state 3, which is the state after reading an `x`. `r3` applies production 3, `X -> y`. State 3 and production 3 have nothing to do with each other, and they only happen to share a number.

GOTO entries have no letter because there is only one thing a GOTO can do. A nonterminal never appears in the input, so the parser can never shift one. A nonterminal arrives on the stack only because a reduce just put it there, and the only remaining question is which state comes next. A terminal column needs a letter because a terminal can be shifted, or it can be the lookahead that triggers a reduce.

### Filling in the table, step by step

Start with the numbered productions and the finished DFA. Production 0 is the augmented start, and its number is never used in an `r` entry.

1. **Draw the grid.** Make one row per state. Make one ACTION column per terminal, plus one for `$`. Here that is `x`, `y` and `$`. Make one GOTO column per nonterminal, leaving out the augmented start. Here that is `S` and `X`.
2. **Take the states in order.** For each state, look at every arrow leaving it, and look at every item with the dot at the far right.
3. **An arrow on a terminal `t` to state `n` is a shift.** Write `sn` in that row, under `t`.
4. **An arrow on a nonterminal `A` to state `n` is a GOTO.** Write the bare number `n` in that row, under `A`.
5. **A dot at the far right of production `p` is a reduce.** Write `rp`. Which columns get it depends on the kind of table: every terminal column and `$` in LR(0), every token in FOLLOW of the left-hand side in SLR, and only the item's own lookahead in LR(1).
6. **The item `S' -> S .` is the exception.** Write `acc` under `$`, and do not write a reduce.
7. **Leave everything else blank.** A blank cell means a syntax error.
8. **If a cell needs a second entry, stop and write both.** That cell is a conflict.

Here is every state of the grammar, and exactly what each one writes in the LR(0) version.

| State | Items in the state | What to write |
|---|---|---|
| 0 | `S' -> . S`, `S -> . X y x`, `X -> . x X`, `X -> . y` | arrow on nonterminal `S` to state 1: write `1` under `S`; arrow on nonterminal `X` to state 2: write `2` under `X`; arrow on terminal `x` to state 3: write `s3` under `x`; arrow on terminal `y` to state 4: write `s4` under `y` |
| 1 | `S' -> S .` | `S' -> S .` is complete: write `acc` under `$` |
| 2 | `S -> X . y x` | arrow on terminal `y` to state 5: write `s5` under `y` |
| 3 | `X -> . x X`, `X -> x . X`, `X -> . y` | arrow on nonterminal `X` to state 6: write `6` under `X`; arrow on terminal `x` to state 3: write `s3` under `x`; arrow on terminal `y` to state 4: write `s4` under `y` |
| 4 | `X -> y .` | `X -> y .` is complete, and it is production 3: write `r3` under `x`, `y` and `$` |
| 5 | `S -> X y . x` | arrow on terminal `x` to state 7: write `s7` under `x` |
| 6 | `X -> x X .` | `X -> x X .` is complete, and it is production 2: write `r2` under `x`, `y` and `$` |
| 7 | `S -> X y x .` | `S -> X y x .` is complete, and it is production 1: write `r1` under `x`, `y` and `$` |

The finished LR(0) table, with the three kinds of entry in the same grid:

| State | `x` | `y` | `$` | `S` | `X` |
|---|---|---|---|---|---|
| 0 | s3 | s4 | | 1 | 2 |
| 1 | | | acc | | |
| 2 | | s5 | | | |
| 3 | s3 | s4 | | | 6 |
| 4 | r3 | r3 | r3 | | |
| 5 | s7 | | | | |
| 6 | r2 | r2 | r2 | | |
| 7 | r1 | r1 | r1 | | |

Row 0 shows all three shapes of an arrow at once. The `x` and `y` arrows consume input, so they become `s3` and `s4`. The `S` and `X` arrows do not, so they stay as the bare numbers `1` and `2`.

### Adding the lookaheads, cell by cell

An LR(1) item carries the token that must come next, so `[X -> y . , y]` means "I have a complete `X`, and I reduce only if the next token is `y`." The closure rule says that from `[A -> w . B z, a]` we add `[B -> . r, b]`, where `b` is each token that can start `z`, or `a` when `z` is empty.

| Item we expand | What follows the nonterminal | Items added |
|---|---|---|
| `[S' -> . S, $]` | Nothing, so we inherit `$` | `[S -> . X y x, $]` |
| `[S -> . X y x, $]` | `y` | `[X -> . x X, y]` and `[X -> . y, y]` |
| `[X -> x . X, y]` (state 3) | Nothing, so we inherit `y` | `[X -> . x X, y]` and `[X -> . y, y]` |

Every `X` in this language is followed by `y`, and `S` is followed only by `$`. The reduce rows change as follows, and nothing else does.

| Row | Item | LR(0) wrote | LR(1) keeps | Cells erased |
|---|---|---|---|---|
| 4 | `[X -> y . , y]` | `r3` under `x`, `y`, `$` | `r3` under `y` | `x` and `$` |
| 6 | `[X -> x X . , y]` | `r2` under `x`, `y`, `$` | `r2` under `y` | `x` and `$` |
| 7 | `[S -> X y x . , $]` | `r1` under `x`, `y`, `$` | `r1` under `$` | `x` and `y` |

The DFA still has the same eight states. On a harder grammar LR(1) also splits states, because two items can match while their lookaheads differ.

You could program this as a chain of `if` statements: if the state is 0 and the input is `x`, then shift to state 3, and so on.  Generated parsers such as yacc use a table instead.  Because each token was shifted onto the stack, a reduction knows the inputs to its production.

*Parsing `xyyx`.*  First, for intuition, build the string with the grammar: `S` gives `X y x`, `X -> x X` gives `x X y x`, and `X -> y` gives `x y y x`.  The parser finds those same steps in reverse order.

This trace keeps one stack with symbols and states mixed, and the top is on the right.  Section 8 keeps two stacks, which holds the same information.  A shift pushes the token and the state.  A reduce by a production of length $$n$$ pops $$2n$$ items and pushes the nonterminal, and then GOTO on the state below it gives the next state to push.

```text
[0]                 x, state 0: s3, push x and 3
[0 x 3]             y, state 3: s4, push y and 4
[0 x 3 y 4]         y, state 4: r3, X -> y, pop 2 and push X
[0 x 3 X]           state 3 on X: goto 6, push 6
[0 x 3 X 6]         y, state 6: r2, X -> x X, pop 4 and push X
[0 X]               state 0 on X: goto 2, push 2
[0 X 2]             y, state 2: s5, push y and 5
[0 X 2 y 5]         x, state 5: s7, push x and 7
[0 X 2 y 5 x 7]     $, state 7: r1, S -> X y x, pop 6 and push S
[0 S]               state 0 on S: goto 1, push 1
[0 S 1]             $, state 1: accept
```

Notice that a reduce does not consume the input.  The parser is still looking at the third character after both reductions, and only then does it shift that `y`.

### Tracing `xyyx`, move by move

Before tracing, build the string with the grammar: `S` gives `X y x`, `X -> x X` gives `x X y x`, and `X -> y` gives `x y y x`. The parser finds those same three productions in reverse order: production 3, then 2, then 1.

The stack holds symbols and states in turn, and the top is on the right. At every move, the parser reads the state on top and the next token, and looks up that one cell in the LR(1) table.

| Stack before the move | Next token | Cell | What the parser does |
|---|---|---|---|
| `[0]` | `x` | row 0, column `x`: `s3` | Shift: push `x`, push state 3, and move past `x` in the input. |
| `[0 x 3]` | `y` | row 3, column `y`: `s4` | Shift: push `y`, push state 4, and move past `y` in the input. |
| `[0 x 3 y 4]` | `y` | row 4, column `y`: `r3` | Reduce by production 3, `X -> y`. Pop 2 items, which exposes state 3. Push `X`. Row 3, column `X` holds `6`, so push 6. The input does not move. |
| `[0 x 3 X 6]` | `y` | row 6, column `y`: `r2` | Reduce by production 2, `X -> x X`. Pop 4 items, which exposes state 0. Push `X`. Row 0, column `X` holds `2`, so push 2. The input does not move. |
| `[0 X 2]` | `y` | row 2, column `y`: `s5` | Shift: push `y`, push state 5, and move past `y` in the input. |
| `[0 X 2 y 5]` | `x` | row 5, column `x`: `s7` | Shift: push `x`, push state 7, and move past `x` in the input. |
| `[0 X 2 y 5 x 7]` | `$` | row 7, column `$`: `r1` | Reduce by production 1, `S -> X y x`. Pop 6 items, which exposes state 0. Push `S`. Row 0, column `S` holds `1`, so push 1. The input does not move. |
| `[0 S 1]` | `$` | row 1, column `$`: `acc` | Accept. |

There are three things to notice. Both reductions happen while the next token stays `y`, because a reduce does not consume input. A reduce pops twice the length of the right-hand side, because each symbol has a state above it. And the state number after a reduce comes from the row exposed by the pop, not from the row the parser was just in.

### After a reduce: the production number, then the state the pop exposes

The `xyyx` trace has only one reduce of each kind, so it hides the step that is easiest to get wrong: after a reduce, which state comes next?  A longer string, `xxyyx`, makes the answer change partway through.

**The rule for every reduce.**

1. **`rn` names production `n`, not state `n`.**  Look `n` up in the numbered list of productions.  `r2` means `X -> x X`, and state 2 has nothing to do with it.
2. **Pop twice the length of the right-hand side.**  Each symbol on the stack has its state above it.  `X -> x X` has two symbols, so pop 4 items.
3. **Read the state that is now on top.**  Call it the *exposed state*.  It is the state the parser was in just before it started reading this right-hand side.
4. **Push the left-hand side, then push GOTO[exposed state, left-hand side].**  The reduce entry never says where to go next.  The GOTO column of the exposed state's row does.
5. **Leave the input where it is.**  Look up the same next character again, now in the new top state.

**Build the string first.**  Each step rewrites the rightmost nonterminal:

```text
S  =>  X y x        production 1
   =>  x X y x      production 2
   =>  x x X y x    production 2
   =>  x x y y x    production 3
```

The parser finds these four productions in reverse order: 3, then 2, then 2 again, then 1.

**The trace, on the LR(1) table.**

| Stack before the move | Next | Cell | What the parser does |
|---|---|---|---|
| `[0]` | `x` | row 0, `x`: `s3` | Shift: push `x` and state 3.  Move to the next character. |
| `[0 x 3]` | `x` | row 3, `x`: `s3` | Shift: push `x` and state 3.  Move to the next character. |
| `[0 x 3 x 3]` | `y` | row 3, `y`: `s4` | Shift: push `y` and state 4.  Move to the next character. |
| `[0 x 3 x 3 y 4]` | `y` | row 4, `y`: `r3` | Production 3 is `X -> y`.  Pop 2, which exposes state **3**.  Push `X`.  Row 3, column `X` holds 6, so push **6**.  The next character is still `y`. |
| `[0 x 3 x 3 X 6]` | `y` | row 6, `y`: `r2` | Production 2 is `X -> x X`.  Pop 4, which exposes state **3**.  Push `X`.  Row 3, column `X` holds 6, so push **6**.  The next character is still `y`. |
| `[0 x 3 X 6]` | `y` | row 6, `y`: `r2` | Production 2 again.  Pop 4, which this time exposes state **0**.  Push `X`.  Row 0, column `X` holds 2, so push **2**.  The next character is still `y`. |
| `[0 X 2]` | `y` | row 2, `y`: `s5` | Shift: push `y` and state 5.  Move to the next character. |
| `[0 X 2 y 5]` | `x` | row 5, `x`: `s7` | Shift: push `x` and state 7.  Move to the next character. |
| `[0 X 2 y 5 x 7]` | `$` | row 7, `$`: `r1` | Production 1 is `S -> X y x`.  Pop 6, which exposes state **0**.  Push `S`.  Row 0, column `S` holds 1, so push **1**. |
| `[0 S 1]` | `$` | row 1, `$`: `acc` | Accept. |

**Look at the two `r2` moves.**  Both happen in state 6, on the same next character `y`, and both apply the same production.  The first goes to state 6, and the second goes to state 2.  The only difference is the state the pop exposes.  The first `X` is built inside another `x X`, so the pop lands in state 3, the state that was waiting for that inner `X`.  The second `X` is the one at the front of `S -> X y x`, so the pop lands in state 0.

This is why the next state cannot be stored in the reduce entry.  A reduce knows *what* it built, but only the exposed state knows *where that piece fits*.  When the parser first entered the exposed state, one of its items had the dot just before the left-hand side, such as `X -> x . X` in state 3.  GOTO moves the dot over that whole `X` at once, as if the `X` had been read from the input as a single character.

Here is every reduce in this grammar, and where it can go:

| Reduce | Production | Items popped | If the pop exposes state 0 | If the pop exposes state 3 |
|---|---|---|---|---|
| `r3` | `X -> y` | 2 | GOTO[0, `X`] = 2 | GOTO[3, `X`] = 6 |
| `r2` | `X -> x X` | 4 | GOTO[0, `X`] = 2 | GOTO[3, `X`] = 6 |
| `r1` | `S -> X y x` | 6 | GOTO[0, `S`] = 1 | cannot happen: an `S` is only ever built from state 0 |

The driver below prints the same trace, and after every reduce it prints the production, the exposed state, and the GOTO lookup.

```python
# reduce_trace.py: the LR(1) table, and a driver that says out loud what each reduce does.
PROD = {1: ("S", ["X", "y", "x"]), 2: ("X", ["x", "X"]), 3: ("X", ["y"])}
ACTION = {
    (0, "x"): "s3", (0, "y"): "s4",
    (1, "$"): "acc",
    (2, "y"): "s5",
    (3, "x"): "s3", (3, "y"): "s4",
    (4, "y"): "r3",
    (5, "x"): "s7",
    (6, "y"): "r2",
    (7, "$"): "r1",
}
GOTO = {(0, "S"): 1, (0, "X"): 2, (3, "X"): 6}

def parse(text):
    tokens = list(text) + ["$"]
    stack, pos = [0], 0
    while True:
        state, tok = stack[-1], tokens[pos]
        act = ACTION.get((state, tok))
        print("%-24s next %s  %s" % (" ".join(map(str, stack)), tok, act or "ERROR"))
        if act is None or act == "acc":
            return act == "acc"
        n = int(act[1:])
        if act[0] == "s":                      # s n: n is a STATE
            stack += [tok, n]
            pos += 1
        else:                                  # r n: n is a PRODUCTION
            lhs, rhs = PROD[n]
            del stack[-2 * len(rhs):]          # pop each symbol and the state above it
            exposed = stack[-1]                # where we were before reading the rhs
            nxt = GOTO[(exposed, lhs)]
            print("%24s   production %d is %s -> %s: pop %d, exposed state %d, GOTO[%d, %s] = %d"
                  % ("", n, lhs, " ".join(rhs), 2 * len(rhs), exposed, exposed, lhs, nxt))
            stack += [lhs, nxt]                # the input does not move

print(parse("xxyyx"))
```

It prints:

```text
0                        next x  s3
0 x 3                    next x  s3
0 x 3 x 3                next y  s4
0 x 3 x 3 y 4            next y  r3
                           production 3 is X -> y: pop 2, exposed state 3, GOTO[3, X] = 6
0 x 3 x 3 X 6            next y  r2
                           production 2 is X -> x X: pop 4, exposed state 3, GOTO[3, X] = 6
0 x 3 X 6                next y  r2
                           production 2 is X -> x X: pop 4, exposed state 0, GOTO[0, X] = 2
0 X 2                    next y  s5
0 X 2 y 5                next x  s7
0 X 2 y 5 x 7            next $  r1
                           production 1 is S -> X y x: pop 6, exposed state 0, GOTO[0, S] = 1
0 S 1                    next $  acc
True
```

**Check yourself.**  Trace `yyx`.  Which state does the `r3` expose, and where does it go?  (State 0, so GOTO[0, `X`] = 2.  In `xyyx` the same `r3` exposed state 3 and went to 6.)

### Tracing `xyx`, and where the error appears

`xyx` is not in the language, because the string needs a `y` after the `X` and this one has an `x` there. Here it is on the LR(1) table:

| Stack before the move | Next token | Cell | What the parser does |
|---|---|---|---|
| `[0]` | `x` | row 0, column `x`: `s3` | Shift: push `x`, push state 3, and move past `x` in the input. |
| `[0 x 3]` | `y` | row 3, column `y`: `s4` | Shift: push `y`, push state 4, and move past `y` in the input. |
| `[0 x 3 y 4]` | `x` | row 4, column `x`: blank | Stop with an error. The parser names state 4 and token `x`. |

Here is the same input on the LR(0) table:

| Stack before the move | Next token | Cell | What the parser does |
|---|---|---|---|
| `[0]` | `x` | row 0, column `x`: `s3` | Shift: push `x`, push state 3, and move past `x` in the input. |
| `[0 x 3]` | `y` | row 3, column `y`: `s4` | Shift: push `y`, push state 4, and move past `y` in the input. |
| `[0 x 3 y 4]` | `x` | row 4, column `x`: `r3` | Reduce by production 3, `X -> y`. Pop 2 items, which exposes state 3. Push `X`. Row 3, column `X` holds `6`, so push 6. The input does not move. |
| `[0 x 3 X 6]` | `x` | row 6, column `x`: `r2` | Reduce by production 2, `X -> x X`. Pop 4 items, which exposes state 0. Push `X`. Row 0, column `X` holds `2`, so push 2. The input does not move. |
| `[0 X 2]` | `x` | row 2, column `x`: blank | Stop with an error. The parser names state 2 and token `x`. |

Both tables reject the string, and both are correct. The LR(0) table makes two reductions first, because its rows 4 and 6 reduce on every token, while the LR(1) table stops as soon as the bad token arrives. No shift happens after the bad token in either table. The practical difference is the error message: LR(1) can report "expected `y`, found `x`" from state 4 with the input in the place the error occurred.

### The grammar as a pushdown automaton

Allison §6.3 says that every context-free grammar has a pushdown automaton (PDA) that accepts the same language.  There are two standard ways to build one from a grammar, and both are parsers.  The first works top down, like recursive descent.  The second is the LR parser above.

**The top-down PDA, built straight from the grammar.**  It needs only one state.  The stack holds the part of the sentence that still has to be matched, with the top on the left.

- Start with `S` on the stack, above a bottom marker `$`.
- For each production `A -> w`, add an ε move: pop `A` and push `w`, with `w`'s first symbol on top.  This grammar gives three: pop `S` and push `X y x`; pop `X` and push `x X`; pop `X` and push `y`.
- For each terminal `a`, add a move that reads `a` from the input and pops `a` from the stack.  This grammar gives two, for `x` and `y`.
- Accept when the input is used up and only `$` is left on the stack.

Here it is on `xyyx`:

| Stack (top on the left) | Input left | Move |
|---|---|---|
| `S $` | `x y y x` | Expand `S -> X y x`. |
| `X y x $` | `x y y x` | Expand `X -> x X`.  The other choice was `X -> y`, so this is a guess. |
| `x X y x $` | `x y y x` | Match `x`. |
| `X y x $` | `y y x` | Expand `X -> y`.  Another guess. |
| `y y x $` | `y y x` | Match `y`. |
| `y x $` | `y x` | Match `y`. |
| `x $` | `x` | Match `x`. |
| `$` | (empty) | Accept. |

This PDA is nondeterministic.  With `X` on top it has two moves and must guess.  One character of lookahead removes the guess here: an `x` next means `X -> x X`, and a `y` next means `X -> y`.  A PDA that guesses with one character of lookahead is LL(1), and it is what recursive descent did with one function per nonterminal.  It expands productions 1, 2, 3, which is a leftmost derivation, from the root down.

**The bottom-up PDA is the LR parser.**  Its finite control is the DFA built above, and its stack holds states, with the grammar symbols between them so we can read it.

- A shift reads one character and pushes it and its state.
- A reduce by `A -> w` is an ε move.  It pops `w` with its states, exposing a state `e`, and pushes `A` and GOTO[`e`, `A`].
- It accepts when state 1 sees `$`.

It finds the same productions in the opposite order (3, 2, 1, a rightmost derivation in reverse), and the table makes every move deterministic, so it never guesses.

One caution about this example.  The language of this grammar is `x* y y x`, which is regular, so a plain DFA could *recognize* it without any stack.  The parser needs the stack anyway, because it has to report *which productions* built the string, and the nesting of `x X` inside `x X` is exactly what the stack remembers.  For a language with real nesting, such as balanced parentheses, the stack is needed even just to say yes or no.

---

## Section 13: Values on the stack

A parser that only accepts is not much use, so where does the arithmetic happen?  On the reduces.  Each stack entry can carry a value, as if the entries were objects, and each reduction computes a new value from the ones it pops.  Here is `A*2+1` with `A` set to 5, using this grammar and table from the [Wikipedia LR parser article](https://en.wikipedia.org/wiki/LR_parser#Bottom-up_parse_steps_for_example_A*2_+_1):

```text
1: Sums     -> Sums + Products
2: Sums     -> Products
3: Products -> Products * Value
4: Products -> Value
5: Value    -> int
6: Value    -> id
```

| State | `*` | `+` | `$` | `int` | `id` | `Sums` | `Products` | `Value` |
|---|---|---|---|---|---|---|---|---|
| 0 | | | | s8 | s9 | 1 | 4 | 7 |
| 1 | | s2 | acc | | | | | |
| 2 | | | | s8 | s9 | | 3 | 7 |
| 3 | s5 | r1 | r1 | | | | | |
| 4 | s5 | r2 | r2 | | | | | |
| 5 | | | | s8 | s9 | | | 6 |
| 6 | r3 | r3 | r3 | | | | | |
| 7 | r4 | r4 | r4 | | | | | |
| 8 | r5 | r5 | r5 | | | | | |
| 9 | r6 | r6 | r6 | | | | | |

Quotes mark an input digit, so it does not look like a state number.  Each reduce also shows the value it computes.

```text
[0]                            A, state 0: s9
[0 A 9]                        *, state 9: r6, Value -> id          Value = 5
[0 Value 7]                    *, state 7: r4, Products -> Value    Products = 5
[0 Products 4]                 *, state 4: s5
[0 Products 4 * 5]             2, state 5: s8
[0 Products 4 * 5 '2' 8]       +, state 8: r5, Value -> int         Value = 2
[0 Products 4 * 5 Value 6]     +, state 6: r3, Products -> Products * Value    Products = 5 * 2 = 10
[0 Products 4]                 +, state 4: r2, Sums -> Products     Sums = 10
[0 Sums 1]                     +, state 1: s2
[0 Sums 1 + 2]                 1, state 2: s8
[0 Sums 1 + 2 '1' 8]           $, state 8: r5, Value -> int         Value = 1
[0 Sums 1 + 2 Value 7]         $, state 7: r4, Products -> Value    Products = 1
[0 Sums 1 + 2 Products 3]      $, state 3: r1, Sums -> Sums + Products    Sums = 10 + 1 = 11
[0 Sums 1]                     $, state 1: accept, and the answer is 11
```

After each pop, GOTO pushes the next state, which is why every reduce line above is followed by a stack with a new state on top.  Row 4 is where `*` binds tighter than `+`: it shifts on `*` and reduces on `+`.  This is what a Bison action does when it computes `$$` from `$1` and `$3`: see the [Flex and Bison tutorial]({{ site.baseurl }}/Tutorials/FlexAndBison).

### Tracing `A*2+1` with values, move by move

Here each stack entry also carries a value. `A` is an identifier whose value is 5. A shift of a token brings in the token's value, and a reduce computes a new value from the entries it pops. Each entry is printed as a symbol, its value, and the state above it. The operators carry no value.

| Stack (each symbol with its value) | Next | Cell | What the parser does | Value computed |
|---|---|---|---|---|
| `[0]` | `A` | row 0, `id`: `s9` | Shift `A`, and push state 9. | |
| `[0  A=5 9]` | `*` | row 9, `*`: `r6` | Reduce by 6, `Value -> id`. Pop 1 entry, exposing state 0. Row 0, `Value` holds `7`. | `Value` = 5 |
| `[0  Value=5 7]` | `*` | row 7, `*`: `r4` | Reduce by 4, `Products -> Value`. Pop 1 entry, exposing state 0. Row 0, `Products` holds `4`. | `Products` = 5 |
| `[0  Products=5 4]` | `*` | row 4, `*`: `s5` | Shift `*`, and push state 5. | |
| `[0  Products=5 4  * 5]` | `2` | row 5, `int`: `s8` | Shift `2`, and push state 8. | |
| `[0  Products=5 4  * 5  2=2 8]` | `+` | row 8, `+`: `r5` | Reduce by 5, `Value -> int`. Pop 1 entry, exposing state 5. Row 5, `Value` holds `6`. | `Value` = 2 |
| `[0  Products=5 4  * 5  Value=2 6]` | `+` | row 6, `+`: `r3` | Reduce by 3, `Products -> Products * Value`. Pop 3 entries, exposing state 0. Row 0, `Products` holds `4`. | `Products` = 5 * 2 = 10 |
| `[0  Products=10 4]` | `+` | row 4, `+`: `r2` | Reduce by 2, `Sums -> Products`. Pop 1 entry, exposing state 0. Row 0, `Sums` holds `1`. | `Sums` = 10 |
| `[0  Sums=10 1]` | `+` | row 1, `+`: `s2` | Shift `+`, and push state 2. | |
| `[0  Sums=10 1  + 2]` | `1` | row 2, `int`: `s8` | Shift `1`, and push state 8. | |
| `[0  Sums=10 1  + 2  1=1 8]` | `$` | row 8, `$`: `r5` | Reduce by 5, `Value -> int`. Pop 1 entry, exposing state 2. Row 2, `Value` holds `7`. | `Value` = 1 |
| `[0  Sums=10 1  + 2  Value=1 7]` | `$` | row 7, `$`: `r4` | Reduce by 4, `Products -> Value`. Pop 1 entry, exposing state 2. Row 2, `Products` holds `3`. | `Products` = 1 |
| `[0  Sums=10 1  + 2  Products=1 3]` | `$` | row 3, `$`: `r1` | Reduce by 1, `Sums -> Sums + Products`. Pop 3 entries, exposing state 0. Row 0, `Sums` holds `1`. | `Sums` = 10 + 1 = 11 |
| `[0  Sums=11 1]` | `$` | row 1, `$`: `acc` | Accept. The value on top is the answer. | **11** |

Three moments are worth stopping on. First, at `[0 Products=5 4]` with `*` next, row 4 says `s5`, so the parser holds on to the 5 and waits for the right operand. Second, at `[0 Products=5 4 * 5 Value=2 6]` with `+` next, row 6 says `r3`, and 5 times 2 happens here. Third, at `[0 Products=10 4]` with `+` next, row 4 says `r2`. The same row 4 shifted on `*` and reduces on `+`, which is exactly where "`*` binds tighter than `+`" lives. The multiplication finishes before the addition can start, and no tree was ever built.

---

## Section 14: Conflicts, Read From the Table

A conflict is a table cell with two entries. It is not a crash. It means the grammar lets one state, on one token, do two different things, and the table has room for only one.

**A shift/reduce conflict: which operator goes first?** The grammar below is ambiguous, because `id + id * id` has two parse trees. Save it as `sr.y`.

```c
%token ID
%%
e: e '+' e | e '*' e | ID ;
%%
```

Bison numbers the productions from 1: rule 1 is `e: e '+' e`, rule 2 is `e: e '*' e`, and rule 3 is `e: ID`. Run `bison -v -b sr sr.y`, and it prints:

```text
sr.y: warning: 4 shift/reduce conflicts [-Wconflicts-sr]
```

The `-v` flag writes `sr.output`. The state after `e + e` reads:

```text
State 6

    1 e: e . '+' e
    1  | e '+' e .
    2  | e . '*' e

    '+'  shift, and go to state 4
    '*'  shift, and go to state 5

    '+'       [reduce using rule 1 (e)]
    '*'       [reduce using rule 1 (e)]
    $default  reduce using rule 1 (e)
```

Bison prints the dot as a bullet; it is a period here so that it matches the rest of this page. Read it as a table row. The second item is complete, so it wants `r1`. The first and third items have the dot before an operator, so they want to shift. In our notation the row holds:

| State | `+` | `*` |
|---|---|---|
| 6 | `s4` or `r1` | `s5` or `r1` |
| 7 | `s4` or `r2` | `s5` or `r2` |

State 7 is the same situation after `e * e`. Two states with two cells each makes the 4 in the warning.

Now take `2 + 3 * 4`. The parser has shifted and reduced up to `e + e` on the stack, and `*` is next. That is state 6, column `*`.

| Choice | What happens | The tree | The value |
|---|---|---|---|
| Reduce by rule 1 | `2 + 3` becomes `e` now, and `*` comes later | `(2 + 3) * 4` | 20 |
| Shift | `*` goes on the stack, and `3 * 4` finishes first | `2 + (3 * 4)` | 14 |

Nothing in the grammar says which one is right. Bison picks the shift, prints the warning, and puts the reduce it threw away in square brackets. There are two ways out. We can restructure the grammar with one nonterminal per level, or we can declare precedence with `%left`.

**A reduce/reduce conflict: what is this token?** Save this as `rr.y`.

```c
%token ID
%%
s: a b | c d ;
a: ID ; b: ID ; c: ID ; d: ID ;
%%
```

The rules are numbered 1 `s: a b`, 2 `s: c d`, 3 `a: ID`, 4 `b: ID`, 5 `c: ID`, 6 `d: ID`. Bison prints:

```text
rr.y: warning: 1 reduce/reduce conflict [-Wconflicts-rr]
rr.y:4.20-21: warning: rule useless in parser due to conflicts [-Wother]
```

And the state after the first `ID`:

```text
State 1

    3 a: ID .
    5 c: ID .

    ID        reduce using rule 3 (a)
    ID        [reduce using rule 5 (c)]
    $default  reduce using rule 3 (a)
```

Both items are complete, and each one can be followed by `ID`, so the cell in state 1, column `ID`, holds `r3` or `r5`. Nothing is being shifted here. The parser has one token and two names for it, and the next token is `ID` either way. Bison keeps the rule that appears first in the file. As a result, `c: ID` can never fire, which is what "useless" means, and the second alternative `s: c d` can never match.

A precedence declaration cannot help, because no operator is involved. The fix is to change the grammar so the next token can tell the two apart, for example by using different tokens.

**Which is worse?** A shift/reduce conflict is often a precedence question that we can declare away. A reduce/reduce conflict usually means two different meanings cannot be told apart, so it is a design problem.

**The dangling else: a shift/reduce conflict we usually keep.** Save this as `de.y`.

```c
%token IF THEN ELSE COND OTHER
%%
s: IF COND THEN s
 | IF COND THEN s ELSE s
 | OTHER
 ;
%%
```

Bison prints `de.y: warning: 1 shift/reduce conflict [-Wconflicts-sr]`, and the state reads:

```text
State 7

    1 s: IF COND THEN s .
    2  | IF COND THEN s . ELSE s

    ELSE  shift, and go to state 8

    ELSE      [reduce using rule 1 (s)]
    $default  reduce using rule 1 (s)
```

Given `if c then if c then x else y`, the stack holds the inner `if ... then s`, and `ELSE` is next. Reducing would finish the inner `if` and give the `else` to the outer one. Shifting gives the `else` to the nearest `if`, which is what almost every language wants. So we accept the default, and write `%expect 1` at the top of the file to record that we chose it. Bison then stays quiet unless the count changes.

**How Bison settles a conflict when nothing else says how:** a shift/reduce conflict becomes a shift, and a reduce/reduce conflict goes to the rule listed first in the file.

---

## Section 15: `tiny.y`, Line by Line

Here is the same machine, generated for us. Save this as `tiny.y`.

```c
%{
#include <stdio.h>
#include <ctype.h>
int yylex(void);
void yyerror(const char *s) { fprintf(stderr, "error: %s\n", s); }
%}
%token NUM
%left '+'
%left '*'
%%
input: /* nothing */ | input expr '\n' { printf("%d\n", $2); } ;
expr:  expr '+' expr  { $$ = $1 + $3; }
     | expr '*' expr  { $$ = $1 * $3; }
     | NUM            { $$ = $1; }
     ;
%%
int yylex(void) {
    int c = getchar();
    while (c == ' ') c = getchar();
    if (isdigit(c)) { ungetc(c, stdin); scanf("%d", &yylval); return NUM; }
    return c == EOF ? 0 : c;
}
int main(void) { return yyparse(); }
```

| Piece of the file | What it does |
|---|---|
| The block between `%{` and `%}` | C code copied into the generated parser as it stands. `yyerror` is what Bison calls on a syntax error. |
| `%token NUM` | Declares a terminal that the lexer returns. Single characters like `'+'` need no declaration. |
| `%left '+'` | Gives `+` a precedence level, and says that two `+` in a row group to the left. |
| `%left '*'` | Gives `*` a higher level, because a later line binds tighter. |
| The `input` rule | Zero or more lines, each an `expr` and a newline. Its action prints the value of the `expr`, which is `$2`, the second symbol. |
| `expr '+' expr` and its action | `$1` and `$3` are the values on the stack under the first and third symbols. `$$` is the value of the new `expr`. The action runs when the rule is reduced. |
| `NUM` and its action | Copies the token's value to the `expr`. |
| `yylex` | Skips spaces. For a digit, it reads the whole number into `yylval` and returns `NUM`. Otherwise it returns the character itself, or 0 at the end of the input. |

Build and run it:

```bash
bison -d -v tiny.y
gcc tiny.tab.c -o tiny
printf '2 + 3 * 4\n2*3+4\n' | ./tiny
```

```text
14
10
```

`-d` writes the header, and `-v` writes `tiny.output`, the states in readable form.

**How `%left` chooses.** Each rule takes the precedence of its last terminal. In a state with a shift/reduce conflict, Bison compares the rule against the next token. If the rule is higher, it reduces. If the token is higher, it shifts. If they are equal, `%left` reduces, so that `2+3+4` groups as `(2+3)+4`.

| Input | Stack | Next | Rule against token | Decision |
|---|---|---|---|---|
| `2 + 3 * 4` | `expr(2) + expr(3)` | `*` | `+` rule is lower than `*` | Shift, so `3 * 4` is 12, then `2 + 12` is 14 |
| `2*3+4` | `expr(2) * expr(3)` | `+` | `*` rule is higher than `+` | Reduce, so `2 * 3` is 6, then `6 + 4` is 10 |

So with `%left` in place, state 8 (after `expr + expr`) shifts only on `*`:

```text
State 8

    3 expr: expr . '+' expr
    3     | expr '+' expr .
    4     | expr . '*' expr

    '*'  shift, and go to state 6

    $default  reduce using rule 3 (expr)
```

**Now delete the two `%left` lines and rebuild.** Bison prints:

```text
tiny.y: warning: 4 shift/reduce conflicts [-Wconflicts-sr]
```

The program still runs, and now it prints:

```text
14
14
```

Without precedence, every conflict becomes a shift. Follow each input:

| Input | Stack | Next | Conflict goes to | Then |
|---|---|---|---|---|
| `2 + 3 * 4` | `expr(2) + expr(3)` | `*` | Shift | `3 * 4` is 12, then `2 + 12` is 14, the right answer by luck |
| `2*3+4` | `expr(2) * expr(3)` | `+` | Shift | The stack grows to `expr(2) * expr(3) + expr(4)`. At the newline, `3 + 4` reduces to 7, then `2 * 7` is 14 |

`2*3+4` came out as `2*(3+4)`. The first input looks right only because shifting happens to be what `*` needed. That is why a warning about conflicts deserves attention, even when the first test passes.

Now `tiny.output` shows the cell with two entries. State 8 reads:

```text
State 8

    3 expr: expr . '+' expr
    3     | expr '+' expr .
    4     | expr . '*' expr

    '+'  shift, and go to state 6
    '*'  shift, and go to state 7

    '+'       [reduce using rule 3 (expr)]
    '*'       [reduce using rule 3 (expr)]
    $default  reduce using rule 3 (expr)
```

The bracketed lines are the moves Bison discarded. State 9, after `expr * expr`, has the same two conflicts with rule 4, which makes four in all. Put the `%left` lines back when you are done.

The question to ask of any grammar is where "`*` binds tighter than `+`" lives. In recursive descent it was which function calls which. In the LR table it was one cell. In Bison it is the order of two `%left` lines.
