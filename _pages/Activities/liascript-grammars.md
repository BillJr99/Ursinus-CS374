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

## Learning Goals

By the end of this activity, you will be able to:

- Classify a grammar into its Chomsky hierarchy level (Type 0–3) by examining the shape of its productions and identifying the corresponding recognizing machine
- Explain why programming language lexers use regular (Type 3) grammars and parsers use context-free (Type 2) grammars, citing the limitations of each class
- Construct a context-free grammar for a given language and produce a derivation sequence for a specific target string
- Demonstrate why certain languages (such as $a^n b^n c^n$) require a more powerful grammar class than context-free, by identifying what information no pushdown automaton can track
- Write a context-free grammar for a real programming construct (expressions, conditionals, or function calls) and verify it by deriving at least two distinct valid programs

> **Before You Begin — Prerequisite Check**
>
> This activity assumes you are comfortable with BNF syntax from the *Syntax and BNF/EBNF* activity: you can read a rule like `expr ::= expr "+" term | term`, you know what "nonterminal" and "terminal" mean, and you have seen at least one derivation step. If any of those concepts are fuzzy, re-read your notes from that activity before proceeding.

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

**Tokens are regular; structure is context-free; meaning is neither.** Identifiers, numbers, and keywords have regular shape, so lexers are built from finite automata (the *Finite Automata* activity's topic). Nesting (balanced braces, expressions inside expressions) requires counting, so parsers use context-free grammars and a stack. And some rules, famously "every variable must be declared before use," are not context-free at all; real compilers enforce them in a separate **semantic analysis** pass over the tree rather than burdening the grammar. The pipeline of your project is the hierarchy made architecture.

A language requires that every `begin` token be matched by a later `end`, with arbitrary nesting. The weakest grammar class that can express this requirement is:

[( )] Regular, because keywords are tokens
[(X)] Context-free, because matched nesting requires a stack's worth of memory
[( )] Context-sensitive, because two different keywords are involved
[( )] Unrestricted, because programs can be arbitrarily long

---


> **Continued next session.** Day 2 picks up from here: [Grammars, Day 2: Writing Context-Free Grammars](https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374/gh-pages/_pages/Activities/liascript-grammars-day2.md).
