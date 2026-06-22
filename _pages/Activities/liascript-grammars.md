# Grammars and the Chomsky Hierarchy
<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://github.com/BillJr99/Ursinus-CS374-Fall2026/blob/gh-pages/_pages/Activities/liascript-grammars.md or locally via https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374-Fall2026/gh-pages/_pages/Activities/liascript-grammars.md

import: https://raw.githubusercontent.com/liascript/CodeRunner/master/README.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

# Grammars and the Chomsky Hierarchy

## Learning Goals

By the end of this activity, you will be able to:

- Classify a grammar into its Chomsky hierarchy level (Type 0–3) by examining the shape of its productions and identifying the corresponding recognizing machine
- Explain why programming language lexers use regular (Type 3) grammars and parsers use context-free (Type 2) grammars, citing the limitations of each class
- Construct a context-free grammar for a given language and produce a derivation sequence for a specific target string
- Demonstrate why certain languages (such as $a^n b^n c^n$) require a more powerful grammar class than context-free, by identifying what information no pushdown automaton can track
- Write a context-free grammar for a real programming construct (expressions, conditionals, or function calls) and verify it by deriving at least two distinct valid programs

> **Before You Begin — Prerequisite Check**
>
> This activity assumes you are comfortable with BNF syntax from the previous activity: you can read a rule like `expr ::= expr "+" term | term`, you know what "nonterminal" and "terminal" mean, and you have seen at least one derivation step. If any of those concepts are fuzzy, re-read your notes from the BNF activity before proceeding.

---

A grammar is a **recipe for generating every valid sentence of a language**. Rules like `E -> E + T | T` describe all legal arithmetic expressions, not by listing them (there are infinitely many), but by giving a finite set of rewriting instructions. Your parser will be the mirror image: given a sentence like `3 + 4 * 5`, it traces backward through those same rules to reconstruct which recipe steps produced it.

Every parser you have ever encountered — from the Python interpreter that runs your code, to the browser that renders this page, to the parser you will write in a few weeks — is powered by a grammar exactly like the ones in this activity. Understanding grammars is not an academic exercise. It is the technical foundation for every subsequent topic in this course: recursive descent, LL(1) tables, operator precedence, and abstract syntax trees all follow directly from the ideas you will work through today.

---

This two-day module places BNF in its theoretical home. Grammars come in **classes of power**, and the class a language needs determines the machine that can recognize it, which is why your project has *both* a lexer (regular machinery) and a parser (context-free machinery). The arc: **formal grammars $\rightarrow$ the four-level hierarchy $\rightarrow$ where programming language constructs live $\rightarrow$ writing context-free grammars for real constructs**.

---

## Directions and Group Roles

Work in your POGIL team with rotated roles (**Manager**, **Recorder**, **Presenter**, **Reflector**). Consider each model and question individually first, then discuss with your group. The Recorder posts answers to the Class Activity Questions discussion board; the Presenter reports out areas of disagreement or alternative approaches. After class, respond to the reflective prompt individually in your notebook.

---

# Part I: The Hierarchy (Day 1)

## 1. Grammars, Formally

**A grammar is a four-tuple** $G = (N, \Sigma, P, S)$: nonterminals $N$, terminal alphabet $\Sigma$, productions $P$, and start symbol $S \in N$. The **language** $L(G)$ is the set of terminal strings derivable from $S$. Chomsky classified grammars by the *shape* their productions may take, and each restriction trades expressive power for recognition efficiency:

| Type | Name | Production shape | Recognizing machine | Example language | PL relevance |
|------|------|------------------|---------------------|-----------------|--------------|
| 3 | Regular | $A \rightarrow aB$ or $A \rightarrow a$ | Finite automaton (DFA/NFA) | All identifiers matching `[a-z][a-z0-9]*` | Lexer tokens |
| 2 | Context-free | $A \rightarrow \gamma$ (single nonterminal on the left) | Pushdown automaton (stack) | $\{a^n b^n \mid n \ge 1\}$, nested parens | Parser / syntax rules |
| 1 | Context-sensitive | $\alpha A \beta \rightarrow \alpha \gamma \beta$ (context preserved) | Linear-bounded automaton | $\{a^n b^n c^n \mid n \ge 1\}$ | Rarely used directly |
| 0 | Unrestricted | $\alpha \rightarrow \beta$ | Turing machine | Any recursively enumerable set | Semantic analysis |

Each class strictly contains the ones below it. The engineering meaning: **the weaker the grammar class, the faster and simpler the recognizer**, so implementers always reach for the weakest class that suffices.

---

## Model 1: The Telltale Languages

Three languages over $\{a, b, c\}$:

- $L_1 = \{ a^n \mid n \ge 1 \}$: one or more a's.
- $L_2 = \{ a^n b^n \mid n \ge 1 \}$: a's followed by the *same number* of b's.
- $L_3 = \{ a^n b^n c^n \mid n \ge 1 \}$: equal counts of all three.

**Worked example — deriving `aaabbb` from the Type 2 grammar $S \rightarrow aSb \mid ab$:**

Every step replaces the *only* nonterminal $S$ with one of its two right-hand sides. When we choose `aSb` we add one `a` on the left and one `b` on the right, keeping $S$ alive in the middle. When we choose `ab` we cash out with the innermost pair.

```
S
  => a S b           (used S -> aSb)
  => a a S b b       (used S -> aSb again)
  => a a a b b b     (used S -> ab, the base case)
```

The "memory" that keeps the `a` count equal to the `b` count is the **nesting depth of the recursion** — the call stack, when we implement this as a recursive descent parser.

**Worked example — why `aab` is rejected:**

```
S => aSb => aaSbb    (now need two more chars to close)
  => aaabb           -- 5 chars, not 3
OR
S => ab              -- 2 chars only
```

There is no way to produce exactly two `a`s and one `b` under this grammar.

### Critical Thinking Questions

> **CTQ 1.1** Write a Type 3 (regular) grammar for $L_1 = \{a^n \mid n \ge 1\}$.
>
> - **Step 1:** What are the only terminals you need?
> - **Step 2:** Write one rule that generates a single `a` (the base case) and one rule that generates `a` and then recurses.
> - **Step 3:** Why can you not use this same trick to count that the number of `a`s equals the number of `b`s?

> **CTQ 1.2** Using the $L_2$ grammar $S \rightarrow aSb \mid ab$:
>
> - **Step 1:** Apply exactly one production to $S$ to get a sentential form. Which rule did you choose? Write the result.
> - **Step 2:** Apply one more production. Write the new sentential form.
> - **Step 3:** Continue until you reach the terminal string `aabb`. How many total steps did it take?
> - **Step 4:** Where is the "memory" that guarantees the `a` count equals the `b` count? Is it in the grammar rules themselves, or does it emerge from the derivation?

> **CTQ 1.3** $L_3 = \{a^n b^n c^n \mid n \ge 1\}$ is not context-free. Try to write a Type 2 grammar for it:
>
> - **Step 1:** Start with the $L_2$ grammar idea. Can you add a `c` for every `ab` pair?
> - **Step 2:** Write whatever grammar you come up with and derive `abc` and `aabbcc`. Does it work for those?
> - **Step 3:** Now try to derive `aaabbbccc`. Where does your grammar produce the wrong counts or get stuck?
> - **Step 4:** In one sentence: what kind of "memory" would you need that a single stack cannot provide?

> **CTQ 1.4** Map to your project: matching nested parentheses in expressions is which of $L_1$, $L_2$, $L_3$ in disguise? What does that tell you about whether your *lexer* or your *parser* must handle it, and why?

---

## 2. Where Programming Languages Live

**Tokens are regular; structure is context-free; meaning is neither.** Identifiers, numbers, and keywords have regular shape, so lexers are built from finite automata (next week's topic). Nesting (balanced braces, expressions inside expressions) requires counting, so parsers use context-free grammars and a stack. And some rules, famously "every variable must be declared before use," are not context-free at all; real compilers enforce them in a separate **semantic analysis** pass over the tree rather than burdening the grammar. The pipeline of your project is the hierarchy made architecture.

[[MC]]
A language requires that every `begin` token be matched by a later `end`, with arbitrary nesting. The weakest grammar class that can express this requirement is:
- ( ) Regular, because keywords are tokens
- (x) Context-free, because matched nesting requires a stack's worth of memory
- ( ) Context-sensitive, because two different keywords are involved
- ( ) Unrestricted, because programs can be arbitrarily long

---

# Part II: Writing Context-Free Grammars (Day 2)

## Model 2: Grammar Construction Workshop

Your team will write CFGs for increasingly real constructs. For each, produce the grammar, one accepted example with its derivation, and one rejected near-miss.

**Worked example — deriving `()()` from $S \rightarrow (S) \mid SS \mid \varepsilon$:**

```
S
  => S S             (used S -> SS)
  => ( S ) S         (used S -> (S) on left S)
  => ( ) S           (used S -> epsilon on inner S)
  => ( ) ( S )       (used S -> (S) on right S)
  => ( ) ( )         (used S -> epsilon on inner S)
```

This grammar treats the empty string as a sentence, which is a design choice: it makes `()()` and `((()))` valid but also accepts the empty program. Whether to allow the empty program is a language design decision, not a technical limitation.

**Worked example — deriving `stmt;stmt` from $L \rightarrow L\,;\,stmt \mid stmt$:**

```
L
  => L ; stmt        (used L -> L ; stmt)
  => stmt ; stmt     (used L -> stmt, base case)
```

Note that this grammar is **left-recursive** (`L -> L ; stmt` starts with `L`). That is fine as a mathematical description, but it will cause a recursive descent parser to loop forever. The same language can be described right-recursively as $L \rightarrow stmt\,;\,L \mid stmt$.

### Critical Thinking Questions

> **CTQ 2.5** **Balanced parentheses with content.** Consider $S \rightarrow (S) \mid SS \mid \varepsilon$.
>
> - **Step 1:** Derive `(())` step by step. Write every sentential form.
> - **Step 2:** Is there more than one derivation for `()()`? Try to find two different derivation sequences that both produce `()()`. (Hint: which $S$ do you expand first in $SS$?)
> - **Step 3:** Does having multiple derivations mean the grammar is ambiguous in the harmful sense? Explain.
> - **Step 4:** Is allowing $S \rightarrow \varepsilon$ a design choice or a technical necessity? What happens if you remove it?

> **CTQ 2.6** **A statement list.** Write a CFG for one-or-more statements separated by semicolons, where a statement is just the terminal `stmt`.
>
> - **Step 1:** Write a grammar with `stmt` as the only terminal. Derive `stmt;stmt;stmt`.
> - **Step 2:** Modify it to *terminate* each statement with a semicolon instead of separating them. Derive the same three-statement sequence under the new grammar.
> - **Step 3:** Which version makes the empty program legal? Which version requires a trailing semicolon after the last statement?
> - **Step 4:** Name a real language that requires the terminator style and one that uses the separator style.

> **CTQ 2.7** **Variable declarations.** Write a CFG for declarations like `int x;`, `float y;`, and comma lists `int x, y, z;`.
>
> - **Step 1:** Write rules for `type` (terminals `int`, `float`), `id` (terminal `x`, `y`, `z`), and `idlist`.
> - **Step 2:** Write the `decl` rule that combines them with a semicolon.
> - **Step 3:** Derive `int x, y, z;` step by step.
> - **Step 4:** Trade with another team: each tries to break the other's grammar with a legal-looking string it rejects, or an illegal string it accepts. Report what you found.

> **CTQ 2.8** **Nested if.** Extend the `ifstmt` rule from the BNF module so that the body may itself contain `ifstmt`.
>
> - **Step 1:** Write the rule. Which symbol on the right-hand side enables arbitrary nesting?
> - **Step 2:** Derive a two-level nested if: `if cond then if cond then stmt`.
> - **Step 3:** Connect to the recursion-is-memory insight from Model 1: what does each level of nesting correspond to in terms of the parser's call stack?
> - **Step 4:** The "dangling else" ambiguity arises from `if E then S else S` — two different parse trees exist for `if a then if b then s1 else s2`. Describe, in words, the two trees and their different meanings.

---

## Code Cell

```python
# A CFG as data, and a brute-force derivation checker for tiny grammars.
# This is NOT how real parsers work (that is weeks away), but it makes
# "derivable from S" concrete and testable.

from itertools import count

GRAMMAR = {            # S -> aSb | ab   (the language a^n b^n)
    "S": [["a", "S", "b"], ["a", "b"]],
}

def derivable(target, start="S", max_steps=12):
    """Breadth-first search over derivations; fine for short strings only."""
    try:
        frontier = [[start]]
        for _ in range(max_steps):
            next_frontier = []
            for form in frontier:
                if all(sym not in GRAMMAR for sym in form):   # all terminals
                    if "".join(form) == target:
                        return True
                    continue
                i = next(i for i, sym in enumerate(form) if sym in GRAMMAR)
                for rhs in GRAMMAR[form[i]]:
                    candidate = form[:i] + rhs + form[i+1:]
                    if len([s for s in candidate if s not in GRAMMAR]) <= len(target):
                        next_frontier.append(candidate)
            frontier = next_frontier
        return False
    except Exception as e:
        print(f"[grammars:derivable] {e}")
        import traceback; traceback.print_exc()
        return False

for s in ["ab", "aabb", "aaabbb", "aab", "ba", "abab"]:
    print(f"{s:8} -> {derivable(s)}")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

---

### Critical Thinking Questions

> **CTQ 2.9** The checker confirms `aabb` and rejects `abab`.
>
> - **Step 1:** Manually trace the BFS frontier after one expansion of `S` for the target `abab`. What sentential forms are on the frontier?
> - **Step 2:** For each form on the frontier, try expanding one more step. Which forms can never lead to `abab`, and why?
> - **Step 3:** Which prefix of `abab` dooms every derivation? State a general rule: "A string is not in $L(S \rightarrow aSb \mid ab)$ if and only if ..."

> **CTQ 2.10** Replace the grammar dictionary with your balanced-parentheses grammar from CTQ 2.5 (use `(` and `)` as terminals) and verify three strings each way.
>
> - **Step 1:** Write out the new `GRAMMAR` dict as you would type it. What are the terminals? What are the productions?
> - **Step 2:** Pick three strings you expect to be accepted and three you expect to be rejected. Record your predictions before running.
> - **Step 3:** What had to change in the grammar dict, and what did not? (Consider: the `derivable` function itself, the start symbol, the loop.)

---

## Model 3: Python CFG Representation (Runnable)

A grammar can be represented as a Python `dict` mapping each nonterminal to a list of right-hand sides (each RHS is itself a list of symbols). The breadth-first derivation checker below tests membership for short strings. Run it and observe which strings are in the language.

The grammar being checked encodes **operator precedence** directly through structure:

```
E -> E + T | T       (+ is low precedence, handled at the top level)
T -> T * F | F       (* is higher precedence, handled one level deeper)
F -> 0 | 1 | ... | 9 (digits are leaves)
```

A worked derivation of `2+3*4`:

```
E
  => E + T           (E -> E + T)
  => T + T           (E -> T, leftmost E)
  => F + T           (T -> F)
  => 2 + T           (F -> 2)
  => 2 + T * F       (T -> T * F)
  => 2 + F * F       (T -> F)
  => 2 + 3 * F       (F -> 3)
  => 2 + 3 * 4       (F -> 4)
```

The `*` sub-expression is deeper in the derivation (and in the tree), which means it is evaluated first — that is **how layered grammars encode precedence**.

```python
# Model 3: CFG as a Python dict + membership checker
# Grammar: arithmetic over single-digit numbers with + and *
# E -> E + T | T
# T -> T * F | F
# F -> num
# (we use right-recursive stand-ins so BFS stays finite)

GRAMMAR = {
    "E": [["E", "+", "T"], ["T"]],
    "T": [["T", "*", "F"], ["F"]],
    "F": [["0"], ["1"], ["2"], ["3"], ["4"],
          ["5"], ["6"], ["7"], ["8"], ["9"]],
}

def derivable(target, grammar, start="E", max_steps=20):
    """BFS over sentential forms; returns True if target is reachable."""
    try:
        nonterminals = set(grammar.keys())
        frontier = [tuple([start])]
        visited = {tuple([start])}
        for _ in range(max_steps):
            next_frontier = []
            for form in frontier:
                # all-terminal: check
                if all(sym not in nonterminals for sym in form):
                    if "".join(form) == target:
                        return True
                    continue
                # expand the FIRST nonterminal (leftmost derivation)
                idx = next(i for i, s in enumerate(form) if s in nonterminals)
                for rhs in grammar[form[idx]]:
                    candidate = form[:idx] + tuple(rhs) + form[idx+1:]
                    # prune: terminal prefix must match target prefix
                    term_prefix = "".join(
                        s for s in candidate if s not in nonterminals)
                    if not target.startswith(term_prefix[:len(term_prefix)]):
                        continue
                    if candidate not in visited and len(candidate) <= len(target) * 2:
                        visited.add(candidate)
                        next_frontier.append(candidate)
            frontier = next_frontier
        return False
    except Exception as e:
        print(f"[cfgcheck:derivable] {e}")
        import traceback; traceback.print_exc()
        return False

tests = ["2+3", "2*3", "1+2*3", "2++3", "2+", "+2", "9*8*7"]
for s in tests:
    print(f"  {s!r:12} in L(G)? {derivable(s, GRAMMAR)}")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

### Critical Thinking Questions

> **CTQ 3.11** `1+2*3` is accepted and `2++3` is rejected.
>
> - **Step 1:** Write the first three sentential forms that BFS explores for `1+2*3` starting from `E` (leftmost derivation). Which production fires first?
> - **Step 2:** At what point does the derivation "commit" to the `*` being inside the `T` subtree rather than the `E` subtree?
> - **Step 3:** For `2++3`: after one or two expansion steps, identify the sentential form that can never be completed into `2++3`. Explain why.

> **CTQ 3.12** This grammar is left-recursive (`E -> E + T`). The BFS still terminates because of the length bound `len(candidate) <= len(target) * 2`.
>
> - **Step 1:** Simulate what a top-down recursive descent parser does when it calls `parseE()` and the current grammar rule is `E -> E + T`. Write out the call sequence.
> - **Step 2:** Why does that sequence never terminate?
> - **Step 3:** BFS avoids infinite loops using the `visited` set and the length bound. Explain which of those two mechanisms prevents the loop that recursive descent falls into.

> **CTQ 3.13** Add a rule `F -> "(" E ")"` (using the symbols `(` and `)`) and add `"(2+3)"` to the test list.
>
> - **Step 1:** Write the modified `GRAMMAR` dict entry for `F`.
> - **Step 2:** Before running, predict whether `(2+3)` will be accepted. Trace the derivation by hand.
> - **Step 3:** Now predict `(2+3)*4`. What does the grammar say about the precedence of parenthesized sub-expressions vs. `*`?

---

## Model 4: Left Recursion Detection (Runnable)

Before converting a grammar to recursive descent we need to know which nonterminals are directly left-recursive. A nonterminal $A$ is directly left-recursive if it has a production $A \rightarrow A\,\alpha$ for some $\alpha$.

**Worked example — left-recursion elimination:**

The standard left-recursive rule `E -> E + T | T` and its right-recursive equivalent `E -> T E'` with `E' -> + T E' | ε` express the *same language* but have very different parser behavior. Here is why they are equivalent:

```
Left-recursive generates:   T,  T+T,  T+T+T,  T+T+T+T, ...
Right-recursive generates:
  E  => T E'
     => T + T E'          (E' -> + T E')
     => T + T + T E'      (E' -> + T E' again)
     => T + T + T         (E' -> epsilon)
```

Same strings, same left-to-right order, but the right-recursive version never calls itself as its very first action — so recursive descent can handle it.

```python
# Model 4: Detecting direct left recursion in a grammar dict

def find_left_recursive(grammar):
    """Return the set of nonterminals that are directly left-recursive."""
    try:
        left_recursive = set()
        for head, productions in grammar.items():
            for rhs in productions:
                if rhs and rhs[0] == head:
                    left_recursive.add(head)
        return left_recursive
    except Exception as e:
        print(f"[lrdetect:find_left_recursive] {e}")
        import traceback; traceback.print_exc()
        return set()

def report(name, grammar):
    lr = find_left_recursive(grammar)
    if lr:
        print(f"{name}: LEFT-RECURSIVE nonterminals = {sorted(lr)}")
    else:
        print(f"{name}: no direct left recursion found")

# Left-recursive arithmetic grammar (standard textbook form)
grammar_lr = {
    "E": [["E", "+", "T"], ["T"]],
    "T": [["T", "*", "F"], ["F"]],
    "F": [["num"]],
}

# Right-recursive rewrite (suitable for recursive descent)
grammar_rr = {
    "E":  [["T", "E'"]],
    "E'": [["+", "T", "E'"], []],   # empty list = epsilon
    "T":  [["F", "T'"]],
    "T'": [["*", "F", "T'"], []],
    "F":  [["num"]],
}

# Balanced-parens grammar (no left recursion)
grammar_bp = {
    "S": [["(", "S", "S", ")"], []],
}

report("Left-recursive arithmetic", grammar_lr)
report("Right-recursive (LL) arithmetic", grammar_rr)
report("Balanced parentheses", grammar_bp)
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

### Critical Thinking Questions

> **CTQ 4.14** `grammar_rr` introduces `E'` and `T'` (read "E-prime"). These are the standard *left-recursion elimination* trick.
>
> - **Step 1:** Using `grammar_rr`, derive `3+5+7` step by step. Write every sentential form.
> - **Step 2:** At each step, write which production rule you used (e.g., `E -> T E'`).
> - **Step 3:** In one sentence, explain what `E' -> + T E' | ε` accomplishes compared to `E -> E + T | T`. Focus on where the recursion sits (first position vs. last position).

> **CTQ 4.15** The detector only finds *direct* left recursion (A → A…). Indirect left recursion would require A → B… and B → A….
>
> - **Step 1:** Write a small example grammar with indirect left recursion between two nonterminals `A` and `B`. Show the two production rules that create the cycle.
> - **Step 2:** Trace what a recursive descent parser does when it tries to parse a string under your indirect grammar. Where does the infinite loop occur?
> - **Step 3:** Sketch in English (no code required) how you would extend `find_left_recursive` to detect one step of indirect left recursion.

> **CTQ 4.16** Why does a recursive descent parser loop forever on `grammar_lr` but successfully parse on `grammar_rr`?
>
> - **Step 1:** For `grammar_lr`, write the first three calls on the call stack when parsing the token `3` from the string `3 + 5`.
> - **Step 2:** For `grammar_rr`, write the first three calls on the call stack for the same input. Where does the stack stop growing?
> - **Step 3:** State the general rule: a recursive descent parser can handle a grammar if and only if ... (complete the sentence in terms of left recursion).

---

## Model 5: Parse Trees as Python Dicts (Runnable)

A parse tree is a nested dictionary `{"node": label, "children": [...]}`. Building one by hand for `2 + 3 * 4` under the layered grammar and pretty-printing it shows directly that the `*` subtree is nested *inside* the `+` subtree — operator precedence made structurally explicit.

**Parse tree for `2 + 3 * 4` under the layered grammar (the CORRECT interpretation):**

```
        E
       / \
      E   T
      |  /|\
      T T * F
      | |   |
      F F   4
      | |
      2 3
```

This tree computes `3 * 4` first (it is deeper), then adds `2`. Result: 14.

**The WRONG tree the naive flat grammar would also permit:**

```
        E
       /|\
      E * E
     /|\   \
    E + E   E
    |   |   |
    2   3   4
```

This tree computes `2 + 3` first, then multiplies by `4`. Result: 20. Same string, different structure, different value — this is the harm of an ambiguous grammar.

**Two different parse trees prove ambiguity.** A grammar is **ambiguous** if any string in its language has two or more distinct parse trees. Ambiguity is not just an aesthetic problem: it means the grammar gives two different computation orders for the same expression. Every parser you write must work from an *unambiguous* grammar; the layered `E/T/F` structure is the standard fix.

```python
# Model 5: Parse trees as nested dicts + pretty printer

def leaf(val):
    return {"node": str(val), "children": []}

def tree(label, *children):
    return {"node": label, "children": list(children)}

def pretty(t, indent=0):
    """Indented ASCII art of the parse tree."""
    try:
        prefix = "  " * indent
        print(f"{prefix}{t['node']}")
        for child in t["children"]:
            pretty(child, indent + 1)
    except Exception as e:
        print(f"[parsetree:pretty] {e}")
        import traceback; traceback.print_exc()

def evaluate(t):
    """Evaluate the tree bottom-up."""
    try:
        if not t["children"]:
            return float(t["node"])
        op = t["node"]
        vals = [evaluate(c) for c in t["children"]]
        if op == "+": return vals[0] + vals[1]
        if op == "*": return vals[0] * vals[1]
        if op == "-": return vals[0] - vals[1]
        if op == "/": return vals[0] / vals[1]
    except Exception as e:
        print(f"[parsetree:evaluate] {e}")
        import traceback; traceback.print_exc()
        return None

# Parse tree for  2 + 3 * 4  under the LAYERED grammar (only one tree)
#        E
#       /|\
#      E + T
#      |  /|\
#      T T * F
#      | |   |
#      F F   4
#      | |
#      2 3
correct_tree = tree("+",
                    leaf(2),
                    tree("*", leaf(3), leaf(4)))

# The WRONG tree the naive grammar also permits
wrong_tree = tree("*",
                  tree("+", leaf(2), leaf(3)),
                  leaf(4))

print("=== Correct parse tree for 2 + 3 * 4 ===")
pretty(correct_tree)
print(f"Value: {evaluate(correct_tree)}")   # 14

print()
print("=== Naive grammar's alternate tree (WRONG) ===")
pretty(wrong_tree)
print(f"Value: {evaluate(wrong_tree)}")     # 20

print()
# Associativity: 7 - 2 - 1  left-associative
left_tree  = tree("-", tree("-", leaf(7), leaf(2)), leaf(1))
right_tree = tree("-", leaf(7), tree("-", leaf(2), leaf(1)))
print(f"Left-assoc  (7-2)-1 = {evaluate(left_tree)}")   # 2
print(f"Right-assoc 7-(2-1) = {evaluate(right_tree)}")  # 6
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

### Critical Thinking Questions

> **CTQ 5.17** In `correct_tree`, the `*` node is a *child* of `+`. In `wrong_tree`, `+` is a child of `*`.
>
> - **Step 1:** Trace `evaluate(correct_tree)` by hand, starting from the leaves. Write each sub-call and its return value.
> - **Step 2:** Now trace `evaluate(wrong_tree)` the same way. Where does the computation diverge?
> - **Step 3:** Explain in one sentence why "deeper in the tree" corresponds to "tighter binding" when the interpreter evaluates children before parents.

> **CTQ 5.18** The pretty-printer uses indentation level to show depth.
>
> - **Step 1:** Before running the code, sketch (on paper) what the indented output for `correct_tree` will look like. Label each line with its depth.
> - **Step 2:** Run the code and compare. Does the deepest indented line correspond to the highest-precedence operation?
> - **Step 3:** For the associativity example at the bottom: draw the two trees for `7-2-1` (left-assoc and right-assoc) using the same ASCII style shown in the model explanation above.

> **CTQ 5.19** Extend the `tree` / `leaf` / `evaluate` code (mentally or on paper) to handle `(2 + 3) * 4`.
>
> - **Step 1:** Which node becomes the root?
> - **Step 2:** How does the tree's shape change compared to `2 + 3 * 4`?
> - **Step 3:** What is the value, and which sub-expression is evaluated first? Connect this back to how parentheses override the grammar's default precedence levels.

---

# Part III: Synthesis and Practice

> **Common Mistakes**
>
> Before attempting the exercises below, review these typical errors:
>
> - **Confusing terminals and nonterminals.** Terminals are the actual symbols that appear in strings (like `+`, `3`, `int`, `(`). Nonterminals are the grammar variables (like `E`, `T`, `stmt`) that get rewritten. A finished derivation contains only terminals.
> - **Writing left-recursive rules without realizing a recursive descent parser cannot handle them.** `E -> E + T` is mathematically valid and even the standard textbook form, but a hand-written recursive descent parser will loop forever on it. Always check for left recursion before implementing.
> - **Forgetting that ambiguous grammars are valid as mathematical objects but break parsers.** An ambiguous grammar is not "wrong" in theory, but it means your parser will non-deterministically produce different ASTs for the same input — a catastrophic bug that is hard to diagnose.
> - **Thinking of grammars as "just syntax."** The structure of a parse tree determines operator precedence and associativity. The reason `*` binds tighter than `+` in every language you have used is that `T` is nested inside `E` in the grammar, not because a rule says "multiply first." If you get the grammar structure wrong, your interpreter will compute wrong answers silently.
> - **Confusing left-recursive and right-recursive in terms of associativity.** Left-recursive rules (`E -> E + T`) produce left-associative trees (correct for `+`, `-`, `*`, `/`). Right-recursive rules produce right-associative trees (correct for `^` and assignment in many languages). Choosing the wrong recursion direction is a silent semantic bug.

## 3. Exercises

1. *Hierarchy sorting.* Classify each language into the weakest sufficient Chomsky class, with one sentence of justification: binary strings with even parity; palindromes; strings of the form `ww` (a string repeated); legal Python indentation.
2. *Grammar archaeology.* Find one production in the official grammar of a language you use (Python's reference or Java's specification) and translate it into the EBNF dialect from class, annotating each construct.
3. *Ambiguity hunting.* The grammar $S \rightarrow S + S \mid S * S \mid \mathbf{num}$ is ambiguous. Find two distinct parse trees for `1 + 2 * 3`. For each tree, compute the value the interpreter would return. Then state what grammar change would make the grammar unambiguous and still compute the conventional answer.
4. *Project grammar, v0.* As a team, draft the top three productions of your future language's grammar: `program`, `statement`, and `expression` (the last may be a stub). These three lines are the seed of your December project. Check each rule for left recursion and flag any that a recursive descent parser would not handle.

---

## Connections

The ideas in this activity connect directly to the next several topics in this course and to real systems you use every day:

**In this course (coming soon):**

- **Recursive descent parsing** (`recursivedescent` activity): You will implement `parseE()`, `parseT()`, `parseF()` as mutually recursive functions, one per nonterminal in `grammar_rr`. Every rule you wrote in Model 2 becomes a function.
- **Parser tables** (`parsertable` activity): LL(1) and LR(0/1) tables are built mechanically from a grammar. The `FIRST` and `FOLLOW` sets you will compute are derived directly from the production rules you practiced here.

**Grammars in the wild:**

- **JSON**: The [official JSON grammar](https://www.json.org/json-en.html) is a small context-free grammar with about 10 production rules. It covers objects, arrays, strings, numbers, and the four literal values. It is a beautiful example of a real-world CFG you can read in five minutes.
- **Python**: The [Python reference grammar](https://docs.python.org/3/reference/grammar.html) uses PEG (Parsing Expression Grammars), a close cousin of CFGs. You will see rules like `funcdef: 'def' NAME parameters ':' suite` — exactly the form you practiced.
- **HTML**: HTML is *not* context-free (attribute values can reference IDs that appear elsewhere in the document), which is part of why browsers have a hand-rolled parser rather than a generated one. This is a real instance of a semantic constraint being too powerful for a CFG.

---

## Practice — Allison, Ch. 4 / Reading 4.2: Context-Free Languages

These exercises cover context-free grammars and the Chomsky hierarchy, drawn from Allison, Ch. 4 §4.2 and Ch. 6 §6.1.

> *Exercises adapted from topics covered in *Foundations of Computing* by Chuck Allison (Fresh Sources, Inc.), used under the [MIT License](https://github.com/chuckallison/foundations-of-computing/blob/main/LICENSE).*

[[MC]]
Which of the following languages is context-free but NOT regular?
- ( ) Strings over {a,b} ending in `bb`
- ( ) Strings over {a,b} with an even number of `a`s
- (x) Strings of the form a^n b^n (equal numbers of a's then b's)
- ( ) The empty language

[[MC]]
In a context-free grammar, a production rule:
- ( ) Maps a pair of nonterminals to a terminal
- (x) Maps a single nonterminal to a string of terminals and/or nonterminals
- ( ) Must have exactly two alternatives
- ( ) Cannot contain the empty string (epsilon)

[[MC]]
A derivation tree (parse tree) for a grammar:
- ( ) Shows only the terminals, in left-to-right order
- (x) Shows the nonterminals used at each step, with the final string as its leaves
- ( ) Is always a binary tree
- ( ) Is unique for every string in the language

1. *Write a CFG.* Write a context-free grammar (in BNF) for the language of properly nested parentheses: `()`, `(())`, `()()`, `((()))`, etc. Show a derivation tree for `(()())`.

2. *Write a CFG for expressions.* Write a CFG for arithmetic expressions with `+`, `*`, numbers, and parentheses that is **unambiguous** and correctly encodes that `*` binds tighter than `+`. Show the unique parse tree for `2 + 3 * 4`.

3. *Identify the hierarchy level.* For each language below, identify the *lowest* level of the Chomsky hierarchy that recognizes it (regular, context-free, context-sensitive, or recursively enumerable) and justify your answer:
   - (a) Binary strings ending in `0`
   - (b) Strings of the form $a^n b^n$
   - (c) Strings of the form $a^n b^n c^n$
   - (d) All Python programs that terminate

4. *Ambiguity.* Show that the grammar `S → S + S | S * S | id` is ambiguous by giving two different parse trees for `id + id * id`. Then write an unambiguous grammar for the same language.

5. *Chomsky Normal Form.* Convert the grammar `S → aSb | ε` to Chomsky Normal Form (CNF), where every rule is either `A → BC` or `A → a`. What does this reveal about the structure of $a^n b^n$?

---

## Reflection Prompt

In your notebook: the hierarchy says more expressive power costs more recognition machinery. Where else in computing (or in life) have you met this pattern — that the price of saying more is needing more memory to listen? Give two concrete examples from different domains.

---

## 4. Further Reading

- Douglas Thain. *Introduction to Compilers and Language Design*, Chapters 3 and 4.
- Noam Chomsky. "Three Models for the Description of Language." *IRE Transactions on Information Theory* (1956).
- Michael Sipser. *Introduction to the Theory of Computation*, Chapters 1 and 2, for proofs we waved at.
- [The JSON Grammar](https://www.json.org/json-en.html) — a real, readable CFG in under 15 minutes.
- [The Python Reference Grammar](https://docs.python.org/3/reference/grammar.html) — PEG variant; compare to what you wrote in Model 2.
