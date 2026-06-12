# Grammars and the Chomsky Hierarchy
<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://github.com/BillJr99/Ursinus-CS374-Fall2026/blob/gh-pages/_pages/Activities/liascript-grammars.md or locally via https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374/gh-pages/_pages/Activities/liascript-grammars.md

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

---

### Critical Thinking Questions

9. The checker confirms `aabb` and rejects `abab`. Trace why `abab` fails: which prefix dooms every derivation?
10. Replace the grammar dictionary with your balanced-parentheses grammar from question 5 (use `(` and `)` as terminals) and verify three strings each way. What had to change, and what did not?

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
