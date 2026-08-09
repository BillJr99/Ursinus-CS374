<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://github.com/BillJr99/Ursinus-CS374-Fall2026/blob/gh-pages/_pages/Activities/liascript-grammars-day2.md or locally via https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374/gh-pages/_pages/Activities/liascript-grammars-day2.md

import: https://raw.githubusercontent.com/liascript/CodeRunner/master/README.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

# Grammars, Day 2: Writing Context-Free Grammars

Day 1 established what a grammar *is* and where programming languages sit in the Chomsky hierarchy. Today we write them: you will build grammars for real constructs, argue about which nonterminal owns which decision, and learn to spot the left recursion that will break the parser you write in three weeks.

> This is the second of two sessions on this topic. If you have not done Day 1, start there: [Grammars](https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374/gh-pages/_pages/Activities/liascript-grammars.md).

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


> **The runnable versions of these models are on their own page.** Representing a CFG as a Python dictionary, detecting left recursion mechanically, and building parse trees as nested dicts are all in [Grammar Tooling in Python](https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374/gh-pages/_pages/Tutorials/tutorial-grammars-in-python.md). Work them after class; the left-recursion detector in particular will tell you whether a grammar you wrote can be parsed by recursive descent.

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

---

Up next: the *Derivations, Parse Trees, Ambiguity, and Precedence* activity puts these grammars to work generating — and mis-generating — programs.
