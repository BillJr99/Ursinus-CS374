# Table-Driven and LR Parsing
<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://github.com/BillJr99/Ursinus-CS374-Fall2026/blob/gh-pages/_pages/Activities/liascript-parsertable.md or locally via https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374/gh-pages/_pages/Activities/liascript-parsertable.md

import: https://raw.githubusercontent.com/liascript/CodeRunner/master/README.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

# Table-Driven and LR Parsing

Recursive descent is top-down: it predicts what must come next. The industrial-strength alternative works **bottom-up**: an **LR parser** shifts tokens onto a stack and reduces them to nonterminals when it recognizes a completed right-hand side, driven entirely by a precomputed table. Over two days we learn to *read and execute* this machinery by hand, because parser generators (yacc, bison, ANTLR) emit it, error messages reference it, and the left recursion that broke descent is exactly what LR handles natively. The arc: **shift-reduce intuition $\rightarrow$ executing a parse by hand $\rightarrow$ conflicts $\rightarrow$ when to use which technology**.

---

## Directions and Group Roles

Work in your POGIL team with rotated roles (**Manager**, **Recorder**, **Presenter**, **Reflector**). Consider each model and question individually first, then discuss with your group. The Recorder posts answers to the Class Activity Questions discussion board; the Presenter reports out areas of disagreement or alternative approaches. After class, respond to the reflective prompt individually in your notebook.

---

# Part I: The Shift-Reduce Idea (Day 1)

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

### Critical Thinking Questions

1. Execute the shift-reduce parse of `2 * 3 + 4` as a team, producing the full stack-input-action table. The Recorder keeps the official copy; expect 12 to 14 rows.
2. At the configuration stack `E + T`, input `* 4 $` (during a parse of `2 + 3 * 4`), the parser must NOT reduce `E -> E + T` yet. Explain what would go wrong with precedence if it did, and what the parser does instead. (The table encodes this choice; you just discovered why the table needs the lookahead token.)
3. Identify, in your question 1 table, the exact row where the tree for `2 * 3` finished forming. Bottom-up means the subtree existed before its parent; point to the evidence.
4. Recursive descent could not run `E -> E + T`; the LR machine prefers it. In one sentence each, say where the "memory of the left context" lives in each technique (the call stack versus the explicit stack).

---

# Part II: Conflicts and Choices (Day 2)

## 2. When the Table Cannot Decide

**A grammar produces a conflict when some table cell needs two actions.** A **shift-reduce conflict** arises when the parser could either extend the current phrase or close it (the dangling else is the canonical case: shift the `else` or reduce the bare `if`); a **reduce-reduce conflict** arises when two completed productions match the same stack top. Conflicts are the LR world's version of the descent world's non-LL(1) alternations: a sign the grammar (or the language) is ambiguous or needs more lookahead. Tools resolve some conflicts with declared precedence; the rest demand grammar surgery, the same surgery skills you built in the ambiguity module.

[[MC]]
A parser generator reports a shift-reduce conflict on the team's grammar at the token `else`. The most informative first response is:
- ( ) Increase the parser's stack size
- ( ) Switch to recursive descent, which has no tables
- (x) Recognize the dangling else ambiguity and either restructure the grammar or accept the tool's default of shifting, documenting the choice
- ( ) Delete the else construct

---

## Model 2: Technology Selection

Your project must choose its parsing technology; most teams hand-write recursive descent, and you should know what you are declining.

### Critical Thinking Questions

5. Compare hand-written descent versus a generated LR parser on four axes: error message quality you control, grammar restrictions (left recursion, factoring), effort to change the grammar mid-project, and what you learn by writing it. Fill the matrix as a team.
6. Python's own parser moved from a hand-written LL variant to a PEG-based generator in 2020 after decades; major C compilers use hand-written descent for error-message control. What do these production choices suggest about the matrix you just filled?
7. Write your team's one-paragraph technology decision for the project, citing two cells of your matrix. File it with your design documents.

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
