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

This two-day module places BNF in its theoretical home. Grammars come in **classes of power**, and the class a language needs determines the machine that can recognize it, which is why your project has *both* a lexer (regular machinery) and a parser (context-free machinery). The arc: **formal grammars $\rightarrow$ the four-level hierarchy $\rightarrow$ where programming language constructs live $\rightarrow$ writing context-free grammars for real constructs**.

---

## Directions and Group Roles

Work in your POGIL team with rotated roles (**Manager**, **Recorder**, **Presenter**, **Reflector**). Consider each model and question individually first, then discuss with your group. The Recorder posts answers to the Class Activity Questions discussion board; the Presenter reports out areas of disagreement or alternative approaches. After class, respond to the reflective prompt individually in your notebook.

---

# Part I: The Hierarchy (Day 1)

## 1. Grammars, Formally

**A grammar is a four-tuple** $G = (N, \Sigma, P, S)$: nonterminals $N$, terminal alphabet $\Sigma$, productions $P$, and start symbol $S \in N$. The **language** $L(G)$ is the set of terminal strings derivable from $S$. Chomsky classified grammars by the *shape* their productions may take, and each restriction trades expressive power for recognition efficiency:

| Type | Name | Production shape | Recognizing machine |
|------|------|------------------|---------------------|
| 3 | Regular | $A \rightarrow aB$ or $A \rightarrow a$ | Finite automaton |
| 2 | Context-free | $A \rightarrow \gamma$ (single nonterminal on the left) | Pushdown automaton (stack) |
| 1 | Context-sensitive | $\alpha A \beta \rightarrow \alpha \gamma \beta$ (context preserved) | Linear-bounded automaton |
| 0 | Unrestricted | $\alpha \rightarrow \beta$ | Turing machine |

Each class strictly contains the ones below it. The engineering meaning: **the weaker the grammar class, the faster and simpler the recognizer**, so implementers always reach for the weakest class that suffices.

---

## Model 1: The Telltale Languages

Three languages over $\{a, b, c\}$:

- $L_1 = \{ a^n \mid n \ge 1 \}$: one or more a's.
- $L_2 = \{ a^n b^n \mid n \ge 1 \}$: a's followed by the *same number* of b's.
- $L_3 = \{ a^n b^n c^n \mid n \ge 1 \}$: equal counts of all three.

### Critical Thinking Questions

1. Write a regular (Type 3) grammar for $L_1$. Now try for $L_2$ and articulate exactly what goes wrong: what must the grammar "remember," and why can rules of shape $A \rightarrow aB$ not remember it?
2. Here is a Type 2 grammar for $L_2$: $S \rightarrow aSb \mid ab$. Derive `aaabbb` step by step. Where, intuitively, is the "memory" hiding?
3. $L_3$ is the classic language that is *not* context-free. Try to extend the $L_2$ trick and report where it breaks. (You need not prove it; feeling the wall is the point.)
4. Map to your project: matching nested parentheses in expressions is which of these three languages in disguise? What does that tell you about whether your *lexer* or your *parser* must handle it?

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

### Critical Thinking Questions

5. **Balanced parentheses with content.** Write a CFG for expressions like `()`, `(())`, `()()`, over just parentheses. Hint: think `S -> (S) | SS | empty` and then debate whether allowing empty is a design choice or a necessity.
6. **A statement list.** Write a CFG for one-or-more statements separated by semicolons, where a statement is just the terminal `stmt`. Now modify it to *terminate* each statement with a semicolon instead. Which version makes the empty program legal?
7. **Variable declarations.** Write a CFG for declarations like `int x;`, `float y;`, and comma lists `int x, y, z;`. Trade with another team; each tries to break the other's grammar with a legal-looking string it rejects or an illegal string it accepts.
8. **Nested if.** Extend the `ifstmt` rule from the BNF module so that the body may itself contain `ifstmt`. Identify the production that creates the nesting, and connect it to the recursion-is-memory insight from Model 1.

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

9. The checker confirms `aabb` and rejects `abab`. Trace why `abab` fails: which prefix dooms every derivation?
10. Replace the grammar dictionary with your balanced-parentheses grammar from question 5 (use `(` and `)` as terminals) and verify three strings each way. What had to change, and what did not?

---

## Model 3: Python CFG Representation (Runnable)

A grammar can be represented as a Python `dict` mapping each nonterminal to a list of right-hand sides (each RHS is itself a list of symbols). The breadth-first derivation checker below tests membership for short strings. Run it and observe which strings are in the language.

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

11. `1+2*3` is accepted and `2++3` is rejected. Without running any code, trace the first three sentential forms BFS explores for `1+2*3` starting from `E`. What production fires first in a leftmost derivation?
12. This grammar is left-recursive (`E -> E + T`). The BFS still terminates because of the length bound `len(candidate) <= len(target) * 2`. Explain why a top-down *recursive descent* parser would loop infinitely on the same grammar but BFS does not.
13. Add a rule `F -> "(" E ")"` (using the symbols `"("` and `")"`) and add `"(2+3)"` to the test list. Predict whether it will be accepted before running, then verify. What does this tell you about where parentheses must sit in the precedence hierarchy?

---

## Model 4: Left Recursion Detection (Runnable)

Before converting a grammar to recursive descent we need to know which nonterminals are directly left-recursive. A nonterminal $A$ is directly left-recursive if it has a production $A \rightarrow A\,\alpha$ for some $\alpha$.

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

14. `grammar_rr` introduces `E'` and `T'` (read "E-prime"). These are the standard *left-recursion elimination* trick. Explain, in one sentence, what `E' -> + T E' | ε` accomplishes compared to `E -> E + T | T`.
15. The detector only finds *direct* left recursion (A → A…). Indirect left recursion would require A → B… and B → A…. Sketch how you would extend `find_left_recursive` to detect one step of indirect left recursion. You do not need to implement it; a clear English description is enough.
16. Why does a recursive descent parser loop forever on `grammar_lr` but successfully parse on `grammar_rr`? Trace the call stack for the first two tokens of `3 + 5` under each grammar.

---

## Model 5: Parse Trees as Python Dicts (Runnable)

A parse tree is a nested dictionary `{"node": label, "children": [...]}`. Building one by hand for `2 + 3 * 4` under the layered grammar and pretty-printing it shows directly that the `*` subtree is nested *inside* the `+` subtree — operator precedence made structurally explicit.

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

17. In `correct_tree`, the `*` node is a *child* of `+`. In `wrong_tree`, `+` is a child of `*`. Explain why "deeper in the tree" corresponds to "tighter binding" when the interpreter evaluates children before parents.
18. The pretty-printer uses indentation level to show depth. Sketch (on paper) how the indented output for `correct_tree` would look, and verify it matches the program's output. Does the deepest line correspond to the highest-precedence operation?
19. Extend the `tree` / `leaf` / `evaluate` code (mentally or on paper) to handle the string `(2 + 3) * 4`. What node becomes the root, and how does the parenthesis change the tree's shape compared to `2 + 3 * 4`?

---

# Part III: Synthesis and Practice

## 3. Exercises

1. *Hierarchy sorting.* Classify each into the weakest sufficient class, with one sentence of justification: binary strings with even parity; palindromes; strings of the form `ww` (a string repeated); legal Python indentation.
2. *Grammar archaeology.* Find one production in the official grammar of a language you use (Python's reference or Java's specification) and translate it into the EBNF dialect from class, annotating each construct.
3. *Project grammar, v0.* As a team, draft the top three productions of your future language's grammar: `program`, `statement`, and `expression` (the last may be a stub). These three lines are the seed of your December project.

---

## Reflection Prompt

In your notebook: the hierarchy says more expressive power costs more recognition machinery. Where else in computing (or in life) have you met this pattern, that the price of saying more is needing more memory to listen?

---

## 4. Further Reading

- Douglas Thain. *Introduction to Compilers and Language Design*, Chapters 3 and 4.
- Noam Chomsky. "Three Models for the Description of Language." *IRE Transactions on Information Theory* (1956).
- Michael Sipser. *Introduction to the Theory of Computation*, Chapters 1 and 2, for proofs we waved at.
