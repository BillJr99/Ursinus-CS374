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

---

## Section 11: Taking this to the assignment's grammar

Part 4 uses the ladder grammar, which adds three things this tutorial's grammar does not have:

| Addition | What it costs you |
|---|---|
| `T -> T * F`, a second precedence tier | Twelve states instead of six, and the state that holds both `E -> T .` and `T -> T . * F` |
| `F -> ( E )` | `)` enters the FOLLOW sets, which changes several reduce rows |
| A larger symbol set | Your discovery order may number states differently from the printed table |

Three pieces of advice, in order of how much time they save.

Check every step against the [class activity]({{ site.lia_viewer_url }}{{ site.raw_pages_url }}Activities/liascript-parsing2.md) before moving to the next one.  The activity prints the correct closure, the twelve item sets, the FOLLOW sets, and the full ACTION and GOTO table, so you never have to wonder whether a bug is upstream or downstream.

If your numbering diverges from the activity's, document the mapping rather than renaming states by hand.  Renumbering by hand is how you introduce an error into code that was correct.

And read row 2 of the finished table when you get there.  In the ladder grammar it shifts on `*` and reduces on `+`, and that single row is where `*` binds tighter than `+`.  Nothing decided it at parse time.  It fell out of the item sets, which is the result this whole tutorial exists to make believable.

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
