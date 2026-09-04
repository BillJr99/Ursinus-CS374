<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374-Fall2026/gh-pages/_pages/Activities/liascript-grammars-day2.md or locally via https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374-Fall2026/gh-pages/_pages/Activities/liascript-grammars-day2.md

import: https://raw.githubusercontent.com/liascript/CodeRunner/master/README.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

# Grammars, Day 2: Writing Context-Free Grammars

Today you write grammars.  Day 1 defined what a grammar is and placed programming languages in the Chomsky hierarchy.  In this session you will build grammars for real language constructs, decide which nonterminal owns each decision, and learn to spot left recursion.  Left recursion is the pattern that will break the parser you write in three weeks.

> This is the second of two sessions on this topic.  If you have not done Day 1, start there: [Grammars](https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374-Fall2026/gh-pages/_pages/Activities/liascript-grammars.md).

# Part II: Writing Context-Free Grammars (Day 2)

## Model 2: Grammar Construction Workshop

Your team will write a context-free grammar (CFG) for each of four constructs, and each construct is a little more realistic than the one before.  For each one, produce three things: the grammar, one accepted example with its derivation, and one rejected string that comes close to being accepted.

A derivation is the sequence of rewriting steps that turns the start symbol into a string.  Each line below is one sentential form, which means one intermediate string of terminals and nonterminals.

**Worked example, deriving `()()` from $S \rightarrow (S) \mid SS \mid \varepsilon$:**

```
S
  => S S             (used S -> SS)
  => ( S ) S         (used S -> (S) on left S)
  => ( ) S           (used S -> epsilon on inner S)
  => ( ) ( S )       (used S -> (S) on right S)
  => ( ) ( )         (used S -> epsilon on inner S)
```

This grammar accepts the empty string as a sentence.  That is a design choice.  It makes `()()` and `((()))` valid, and it also accepts the empty program.  Whether to allow the empty program is a language design decision, not a technical limit.

Worked example, deriving `stmt;stmt` from $L \rightarrow L\,;\,stmt \mid stmt$:

```
L
  => L ; stmt        (used L -> L ; stmt)
  => stmt ; stmt     (used L -> stmt, base case)
```

This grammar is left-recursive: the rule `L -> L ; stmt` starts with `L`, the symbol it defines.  As a mathematical description, that is fine.  As input to a recursive descent parser, it causes an infinite loop.  The same language can be written right-recursively as $L \rightarrow stmt\,;\,L \mid stmt$.

Remember two things from this model.  A derivation shows one rewriting step per line.  A rule that starts with its own name is left-recursive, and you will meet that problem again in Part III.

### Critical Thinking Questions

> **CTQ 2.5** **Balanced parentheses with content.**  Consider $S \rightarrow (S) \mid SS \mid \varepsilon$.
>
> - **Step 1:** Derive `(())` step by step.  Write every sentential form.
> - **Step 2:** Is there more than one derivation for `()()`?  Try to find two different derivation sequences that both produce `()()`.  (Hint: which $S$ do you expand first in $SS$?)
> - **Step 3:** Does having multiple derivations mean the grammar is ambiguous in the harmful sense?  Explain.
> - **Step 4:** Is allowing $S \rightarrow \varepsilon$ a design choice or a technical necessity?  What happens if you remove it?

> **CTQ 2.6** **A statement list.**  Write a CFG for one or more statements separated by semicolons, where a statement is the single terminal `stmt`.
>
> - **Step 1:** Write a grammar with `stmt` as the only terminal.  Derive `stmt;stmt;stmt`.
> - **Step 2:** Change it so that a semicolon *terminates* each statement instead of separating them.  Derive the same three-statement sequence under the new grammar.
> - **Step 3:** Which version makes the empty program legal?  Which version requires a trailing semicolon after the last statement?
> - **Step 4:** Name a real language that requires the terminator style and one that uses the separator style.

> **CTQ 2.7** **Variable declarations.**  Write a CFG for declarations like `int x;`, `float y;`, and comma lists like `int x, y, z;`.
>
> - **Step 1:** Write rules for `type` (terminals `int`, `float`), `id` (terminals `x`, `y`, `z`), and `idlist`.
> - **Step 2:** Write the `decl` rule that combines them with a semicolon.
> - **Step 3:** Derive `int x, y, z;` step by step.
> - **Step 4:** Trade with another team.  Each team tries to break the other's grammar with a legal-looking string it rejects, or an illegal string it accepts.  Report what you found.

> **CTQ 2.8** **Nested if.**  Extend the `ifstmt` rule from the BNF module so that the body may itself contain an `ifstmt`.
>
> - **Step 1:** Write the rule.  Which symbol on the right-hand side allows nesting to any depth?
> - **Step 2:** Derive a two-level nested if: `if cond then if cond then stmt`.
> - **Step 3:** Connect this to the recursion-is-memory idea from Model 1.  What does each level of nesting correspond to on the parser's call stack?
> - **Step 4:** The "dangling else" ambiguity comes from the rule `if E then S else S`: the string `if a then if b then s1 else s2` has two different parse trees.  Describe the two trees in words, and say how their meanings differ.

---

## Model 3: Test the Grammar You Just Wrote

This cell runs the grammars you wrote in Model 2.  You encode a grammar as a Python dictionary.  You give the checker one list of strings you expect it to accept and one list you expect it to reject.  The checker then tells you where your grammar disagrees with your intent.

```python
from collections import deque

def derivable(grammar, target, start="S", max_len=None):
    """Breadth-first search over sentential forms. Toy scale only."""
    limit = max_len if max_len is not None else len(target)
    seen, queue = {(start,)}, deque([(start,)])
    while queue:
        form = queue.popleft()
        if all(sym not in grammar for sym in form):
            if "".join(form) == target:
                return True
            continue
        i = next(i for i, sym in enumerate(form) if sym in grammar)
        for rhs in grammar[form[i]]:
            cand = form[:i] + tuple(rhs) + form[i+1:]
            terminals = sum(1 for sym in cand if sym not in grammar)
            if terminals <= limit and len(cand) <= limit + 4 and cand not in seen:
                seen.add(cand)
                queue.append(cand)
    return False

def check(name, grammar, accept, reject, start="S"):
    print(f"\n=== {name} ===")
    wrong = 0
    for t in accept:
        ok = derivable(grammar, t, start)
        if not ok: wrong += 1
        print(f"  {t!r:10} should be ACCEPTED -> {'ok' if ok else 'REJECTED, your grammar is too narrow'}")
    for t in reject:
        ok = derivable(grammar, t, start)
        if ok: wrong += 1
        print(f"  {t!r:10} should be REJECTED -> {'ok' if not ok else 'ACCEPTED, your grammar is too loose'}")
    print(f"  -> {'grammar matches your intent' if not wrong else str(wrong) + ' disagreement(s)'}")

# The balanced-parens grammar from the worked example: S -> (S) | SS | epsilon
PARENS = {"S": [["(", "S", ")"], ["S", "S"], []]}
check("Balanced parentheses", PARENS,
      accept=["", "()", "(())", "()()", "((()))"],
      reject=["(", ")(", "(()"])

# The statement list from CTQ 2.6, separator style: L -> L ; stmt | stmt
STMTS = {"L": [["L", ";", "s"], ["s"]]}
check("Statement list (separator style)", STMTS,
      accept=["s", "s;s", "s;s;s"],
      reject=["", ";s", "s;"], start="L")

# TODO: encode YOUR grammar from CTQ 2.7 (declarations) and CTQ 2.8 (nested if)
#       and call check() on each. Predict the verdicts before you run.
```
@LIA.eval(`["main.py"]`, `none`, `python3 main.py`)

### Reading the Code

- A grammar is a dict.  Each key is a nonterminal, and its value is a list of alternatives.  Each alternative is a *list of symbols*.  The empty list `[]` stands for $\varepsilon$, which is how `PARENS` allows the empty string.
- `derivable` always expands the leftmost nonterminal.  That is a choice, not a requirement.  CTQ 2.9 asks what changes if you pick a different one.
- The `terminals <= limit` test prunes the search and keeps it finite.  `S -> SS` can grow a form without adding any terminals, so the extra guard `len(cand) <= limit + 4` stops the search from spinning on nonterminals alone.
- `check` reports *which direction* your grammar is wrong.  Too narrow means it rejects something legal.  Too loose means it accepts something illegal.  Those are different bugs with different fixes.

> **Watch out!**  This is a brute-force search, not a parser.  It answers "is this string derivable" by trying everything.  That takes exponential time and gives you no parse tree.  A real parser answers the same question in linear time *and* hands you the structure.  Building that parser is the work of the next three weeks.

Remember two things from this model.  The checker compares your grammar against your intent and names the direction of each mismatch.  It cannot replace a parser, because it produces no tree and does not scale.

### Critical Thinking Questions

> **CTQ 2.9** The checker accepts `aabb` under $S \rightarrow aSb \mid ab$ and rejects `abab`.
>
> - **Step 1:** By hand, trace the frontier after one expansion of $S$ for the target `abab`.  What sentential forms are on it?
> - **Step 2:** Expand each form one more step.  Which forms can never lead to `abab`, and why?
> - **Step 3:** Which prefix of `abab` dooms every derivation?  State a general rule: "A string is not in $L(S \rightarrow aSb \mid ab)$ if and only if ..."

> **CTQ 2.10** Encode your CTQ 2.7 declaration grammar and run `check` on it.
>
> - **Step 1:** Write out the dict as you would type it.  What are the terminals?
> - **Step 2:** Pick three strings you expect accepted and three you expect rejected.  Record your predictions *before* running.
> - **Step 3:** If `check` reports a disagreement, is your grammar too narrow or too loose?  Fix it and rerun.

> **CTQ 2.11** Trade grammars with another team.  Run their declaration grammar through `check` with *your* test strings.  Did you find a string that breaks it?  Report what you found and what rule would fix it.

---

# Part III: Left Recursion, the Trap Waiting for Your Parser

## 2.  Theory: Where the Recursion Sits

A rule that begins by naming itself will send a recursive descent parser into an infinite loop.  You have now written several grammars, and at least one of them is probably built this way.  A nonterminal $A$ is directly left-recursive if it has a production $A \rightarrow A\,\alpha$, where the right-hand side starts with $A$ itself.

The statement-list rule from the worked example is one:

```
L -> L ; stmt | stmt
```

As a mathematical description, this rule is perfect.  As a parser, it is fatal.  In three weeks you will write one function per nonterminal.  `parse_L()` will begin by calling `parse_L()`, which begins by calling `parse_L()`, and so on forever.  No call ever consumes a token, so the recursion never reaches a base case.

The fix is to move the recursion out of first position.  These two grammars describe *the same language*:

```
E -> E + T | T                      (left-recursive)

E  -> T E'                          (right-recursive)
E' -> + T E' | ε
```

They are equivalent because they generate the same strings:

```
Left-recursive generates:   T,  T+T,  T+T+T,  T+T+T+T, ...

Right-recursive derives:
  E  => T E'
     => T + T E'          (E' -> + T E')
     => T + T + T E'      (E' -> + T E' again)
     => T + T + T         (E' -> epsilon)
```

Same strings, same left-to-right order.  But the right-recursive version never calls itself as its very first action.  `parse_E()` consumes a `T` before it recurses, so the recursion terminates.

> **Watch out!**  Left recursion and right recursion are not interchangeable once you care about *meaning*.  Left-recursive rules produce left-associative trees, which is correct for `+`, `-`, `*`, and `/`.  Right-recursive rules produce right-associative trees, which is correct for `^` and for assignment in many languages.  If you remove left recursion for the parser's sake but do not restore the associativity when you build the tree, you have a silent semantic bug: your interpreter will compute `7 - 2 - 1` as `6` instead of `4`.

Remember two things from this section.  A rule is directly left-recursive when its right-hand side starts with its own left-hand side, and recursive descent cannot handle it.  Rewriting the rule right-recursively keeps the language but changes the tree shape, so you must restore associativity yourself.

## Examples: Spot It by Eye

Before you run the detector, mark each rule as left-recursive or not, and say what a recursive descent parser would do with it first:

| Rule | Left-recursive? | What `parse_X()` does first |
|------|-----------------|-----------------------------|
| `E -> E + T` | ? | ? |
| `E -> T E'` | ? | ? |
| `T -> T * F` | ? | ? |
| `S -> ( S S )` | ? | ? |
| `A -> B c` with `B -> A d` | ? | ? |

The last row is the interesting one.  Neither rule starts with itself, and yet the pair is still a trap.

## Model 4: A Left-Recursion Detector

```python
def find_left_recursive(grammar):
    """Return the nonterminals that are DIRECTLY left-recursive: A -> A alpha."""
    return {head for head, prods in grammar.items()
            for rhs in prods if rhs and rhs[0] == head}

def report(name, grammar):
    lr = find_left_recursive(grammar)
    if lr:
        print(f"  {name:34} LEFT-RECURSIVE: {sorted(lr)}")
        print(f"  {'':34} -> recursive descent will loop forever")
    else:
        print(f"  {name:34} no direct left recursion")

# Left-recursive arithmetic (the standard textbook form)
grammar_lr = {
    "E": [["E", "+", "T"], ["T"]],
    "T": [["T", "*", "F"], ["F"]],
    "F": [["num"]],
}

# Right-recursive rewrite (suitable for recursive descent)
grammar_rr = {
    "E":  [["T", "E'"]],
    "E'": [["+", "T", "E'"], []],      # empty list = epsilon
    "T":  [["F", "T'"]],
    "T'": [["*", "F", "T'"], []],
    "F":  [["num"]],
}

grammar_bp    = {"S": [["(", "S", "S", ")"], []]}
grammar_stmts = {"L": [["L", ";", "s"], ["s"]]}

print("=== Direct left recursion ===")
report("Left-recursive arithmetic",  grammar_lr)
report("Right-recursive arithmetic", grammar_rr)
report("Balanced parentheses",       grammar_bp)
report("Statement list (separator)", grammar_stmts)

print("\n=== The one the detector MISSES ===")
grammar_indirect = {
    "A": [["B", "c"]],
    "B": [["A", "d"], ["e"]],
}
report("Indirect: A -> B c, B -> A d", grammar_indirect)
print("  ...and yet parse_A() calls parse_B(), which calls parse_A().")
print("  Neither rule begins with ITSELF, so the direct check cannot see it.")

print("\n=== Watch the loop, with a depth guard so we survive it ===")
def parse_with_guard(grammar, nt, depth=0, limit=12, path=None):
    """Simulate recursive descent taking the FIRST alternative every time."""
    path = (path or []) + [nt]
    if depth >= limit:
        print(f"    depth {limit} reached: {' -> '.join(path[:8])} ...")
        return "LOOPED"
    first = grammar[nt][0]
    if not first or first[0] not in grammar:
        return "consumed a terminal, fine"
    return parse_with_guard(grammar, first[0], depth + 1, limit, path)

for name, g, start in [("grammar_lr", grammar_lr, "E"),
                       ("grammar_rr", grammar_rr, "E"),
                       ("indirect",   grammar_indirect, "A")]:
    print(f"  {name:12} starting at {start}: {parse_with_guard(g, start)}")
```
@LIA.eval(`["main.py"]`, `none`, `python3 main.py`)

### Reading the Code

- `find_left_recursive` is a two-line check.  For every rule, it asks whether the *first* symbol of the right-hand side is the same as the left-hand side.  That is the entire definition of direct left recursion.
- `grammar_rr` introduces `E'` and `T'`, read "E-prime" and "T-prime".  This is the standard way to eliminate left recursion.  The rule `E' -> + T E' | ε` is where the repetition now lives.
- The detector reports nothing for `grammar_indirect`, and then `parse_with_guard` shows the loop happening anyway.  The gap between those two outputs is the subject of CTQ 2.13.
- `parse_with_guard` always takes the *first* alternative.  That is what a naive recursive descent parser does before it learns to look ahead.  The depth limit is there only so the cell terminates; a real parser would overflow the stack.

Remember two things from this model.  The detector catches a rule whose right-hand side starts with its own head, and nothing else.  Indirect left recursion, where two rules call each other, still loops and still needs a check by hand.

### Critical Thinking Questions

> **CTQ 2.12** Using `grammar_rr`, derive `3+5+7` step by step.  Write every sentential form and the rule used.  Then explain in one sentence what `E' -> + T E' | ε` accomplishes compared to `E -> E + T | T`.  Focus on *where* the recursion sits.

> **CTQ 2.13** The detector misses `grammar_indirect`.
>
> - **Step 1:** Write the two rules that create the cycle.
> - **Step 2:** Trace what a recursive descent parser does under them.  Where exactly is the infinite loop?
> - **Step 3:** Sketch in English how you would extend `find_left_recursive` to catch one step of indirect left recursion.  What data structure does that start to look like?

> **CTQ 2.14** For `grammar_lr`, write the first three calls on the call stack when parsing the token `3` from `3 + 5`.  Then do the same for `grammar_rr`.  Where does the stack stop growing?  Complete the rule: "a recursive descent parser can handle a grammar if and only if ..."

> **CTQ 2.15** `7 - 2 - 1` should be `4`.  Which of `grammar_lr` and `grammar_rr` produces the tree that computes it correctly?  What must you do in the *other* one to get the right answer anyway?

### Try It Yourself

Run the detector on the grammar your team drafted in Exercise 4 before you write a line of parser.

```python
def find_left_recursive(grammar):
    return {head for head, prods in grammar.items()
            for rhs in prods if rhs and rhs[0] == head}

# TODO: encode your team's program / statement / expression rules here.
#       Use lists of symbol strings; [] means epsilon.
MY_GRAMMAR = {
    "program":    [["statement", "program"], []],
    "statement":  [["expression", ";"]],
    "expression": [],          # TODO: fill this in, and try it BOTH ways:
                               #   left-recursive:  [["expression", "+", "term"], ["term"]]
                               #   right-recursive: [["term", "expression'"]]
}

lr = find_left_recursive(MY_GRAMMAR)
if lr:
    print(f"LEFT-RECURSIVE: {sorted(lr)}")
    print("Rewrite these before you start the Parser assignment, or")
    print("commit to a parsing method that tolerates them (see Table-Driven")
    print("and LR Parsing, which handles left recursion natively).")
else:
    print("No direct left recursion. Recursive descent can handle this.")
    print("Now check for INDIRECT left recursion by hand; the detector cannot.")
```
@LIA.eval(`["main.py"]`, `none`, `python3 main.py`)

Expected output: with the left-recursive `expression` filled in, the detector names it.  With the right-recursive version, it reports clean.  Keep whichever you choose.  It is the seed of your Parser assignment.

---

# Part IV: Synthesis and Practice

> **Common Mistakes**
>
> Before you attempt the exercises below, review these typical errors:
>
> - *Confusing terminals and nonterminals.*  Terminals are the actual symbols that appear in strings (like `+`, `3`, `int`, `(`).  Nonterminals are the grammar variables (like `E`, `T`, `stmt`) that get rewritten.  A finished derivation contains only terminals.
> - *Writing left-recursive rules without noticing that a recursive descent parser cannot handle them.*  `E -> E + T` is mathematically valid and is the standard textbook form, but a hand-written recursive descent parser will loop forever on it.  Always check for left recursion before you implement.
> - *Forgetting that ambiguous grammars are valid as mathematical objects but break parsers.*  An ambiguous grammar is not "wrong" in theory.  In practice it means your parser can produce different abstract syntax trees (ASTs) for the same input, which is a serious bug that is hard to diagnose.
> - *Thinking of grammars as "just syntax."*  The structure of a parse tree determines operator precedence and associativity.  `*` binds tighter than `+` in every language you have used because `T` is nested inside `E` in the grammar, not because a rule says "multiply first."  If you get the grammar structure wrong, your interpreter will compute wrong answers silently.
> - *Mixing up left recursion and right recursion when it comes to associativity.*  Left-recursive rules (`E -> E + T`) produce left-associative trees (correct for `+`, `-`, `*`, `/`).  Right-recursive rules produce right-associative trees (correct for `^` and assignment in many languages).  Choosing the wrong recursion direction is a silent semantic bug.

# Check Your Understanding

When writing a CFG for a construct, the first question to settle is:

[(X)] What the recursive case and the base case are, since every repeated or nested structure needs both
[( )] Which parsing algorithm you will use
[( )] How many tokens of lookahead you need
[( )] What the AST node classes will be called

---

A rule written `A -> A x | x` and one written `A -> x { x }` differ in:

[(X)] Parseability by recursive descent, not in the set of strings they accept
[( )] The language they generate
[( )] Whether they are context-free
[( )] Nothing at all

---

You want a list of one or more items separated by commas. The rule is:

[(X)] `list -> item { "," item }`: one required item, then zero or more comma-item pairs
[( )] `list -> { item "," }`: zero or more item-comma pairs
[( )] `list -> item "," list | ""`: which permits a trailing comma
[( )] `list -> { item } { "," }`

---

## 3.  Exercises

1.  *Hierarchy sorting.*  Classify each language into the weakest Chomsky class that can describe it, with one sentence of justification: binary strings with even parity; palindromes; strings of the form `ww` (a string repeated); legal Python indentation.
2.  *Grammar archaeology.*  Find one production in the official grammar of a language you use (Python's reference or Java's specification).  Translate it into the EBNF dialect from class, and annotate each construct.
3.  *Ambiguity hunting.*  The grammar $S \rightarrow S + S \mid S * S \mid \mathbf{num}$ is ambiguous.  Find two distinct parse trees for `1 + 2 * 3`.  For each tree, compute the value the interpreter would return.  Then state what grammar change would make the grammar unambiguous and still compute the conventional answer.
4.  *Project grammar, v0.*  As a team, draft the top three productions of your future language's grammar: `program`, `statement`, and `expression` (the last may be a stub).  These three lines are the seed of your December project.  Check each rule for left recursion and flag any that a recursive descent parser would not handle.

---

## Connections

The ideas in this activity lead directly into the next several topics in this course, and they appear in real systems you use every day.

In this course (coming soon):

- *Recursive descent parsing* (`recursivedescent` activity): You will implement `parseE()`, `parseT()`, and `parseF()` as mutually recursive functions, one per nonterminal in `grammar_rr`.  Every rule you wrote in Model 2 becomes a function.
- *Parser tables* (`parsertable` activity): LL(1) and LR(0/1) tables are built mechanically from a grammar.  The `FIRST` and `FOLLOW` sets you will compute come directly from the production rules you practiced here.

Grammars in the wild:

- *JSON*: The [official JSON grammar](https://www.json.org/json-en.html) is a small context-free grammar with about 10 production rules.  It covers objects, arrays, strings, numbers, and the four literal values.  It is a real-world CFG you can read in five minutes.
- *Python*: The [Python reference grammar](https://docs.python.org/3/reference/grammar.html) uses PEG (Parsing Expression Grammars), a close cousin of CFGs.  You will see rules like `funcdef: 'def' NAME parameters ':' suite`, which is exactly the form you practiced.
- *HTML*: HTML is *not* context-free, because attribute values can reference IDs that appear elsewhere in the document.  That is part of why browsers have a hand-written parser rather than a generated one.  It is a real case of a semantic constraint that a CFG cannot express.

---

## Practice, Allison, Ch. 4 / Reading 4.2: Context-Free Languages

These exercises cover context-free grammars and the Chomsky hierarchy.  They draw on Allison, Ch. 4 §4.2 and Ch. 6 §6.1.

> *Exercises adapted from topics covered in *Foundations of Computing* by Chuck Allison (Fresh Sources, Inc.), used under the [MIT License](https://github.com/chuckallison/foundations-of-computing/blob/main/LICENSE).*

Which of the following languages is context-free but NOT regular?

[( )] Strings over {a,b} ending in `bb`
[( )] Strings over {a,b} with an even number of `a`s
[(X)] Strings of the form a^n b^n (equal numbers of a's then b's)
[( )] The empty language

In a context-free grammar, a production rule:

[( )] Maps a pair of nonterminals to a terminal
[(X)] Maps a single nonterminal to a string of terminals and/or nonterminals
[( )] Must have exactly two alternatives
[( )] Cannot contain the empty string (epsilon)

A derivation tree (parse tree) for a grammar:

[( )] Shows only the terminals, in left-to-right order
[(X)] Shows the nonterminals used at each step, with the final string as its leaves
[( )] Is always a binary tree
[( )] Is unique for every string in the language

1.  *Write a CFG.*  Write a context-free grammar (in BNF) for the language of properly nested parentheses: `()`, `(())`, `()()`, `((()))`, and so on.  Show a derivation tree for `(()())`.

2.  *Write a CFG for expressions.*  Write a CFG for arithmetic expressions with `+`, `*`, numbers, and parentheses.  The grammar must be unambiguous and must encode that `*` binds tighter than `+`.  Show the unique parse tree for `2 + 3 * 4`.

3.  *Identify the hierarchy level.*  For each language below, identify the *lowest* level of the Chomsky hierarchy that recognizes it (regular, context-free, context-sensitive, or recursively enumerable) and justify your answer:
   - (a) Binary strings ending in `0`
   - (b) Strings of the form $a^n b^n$
   - (c) Strings of the form $a^n b^n c^n$
   - (d) All Python programs that terminate

4.  *Ambiguity.*  Show that the grammar `S -> S + S | S * S | id` is ambiguous by giving two different parse trees for `id + id * id`.  Then write an unambiguous grammar for the same language.

5.  *Chomsky Normal Form.*  Convert the grammar `S -> aSb | ε` to Chomsky Normal Form (CNF), where every rule is either `A -> BC` or `A -> a`.  What does this reveal about the structure of $a^n b^n$?

---

## Reflection Prompt

In your notebook: the hierarchy says that more expressive power costs more recognition machinery.  Where else in computing (or in life) have you met this pattern, where the price of saying more is needing more memory to listen?  Give two concrete examples from different domains.

---

## 4.  Further Reading

- Douglas Thain.  *Introduction to Compilers and Language Design*, Chapters 3 and 4.
- Noam Chomsky.  "Three Models for the Description of Language."  *IRE Transactions on Information Theory* (1956).
- Michael Sipser.  *Introduction to the Theory of Computation*, Chapters 1 and 2, for the proofs we only sketched.
- [The JSON Grammar](https://www.json.org/json-en.html): a real, readable CFG you can finish in under 15 minutes.
- [The Python Reference Grammar](https://docs.python.org/3/reference/grammar.html): a PEG variant; compare it to what you wrote in Model 2.

---

Up next: the *Derivations, Parse Trees, Ambiguity, and Precedence* activity puts these grammars to work generating (and mis-generating) programs.
