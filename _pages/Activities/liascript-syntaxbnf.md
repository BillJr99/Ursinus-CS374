# Syntax and BNF/EBNF
<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://github.com/BillJr99/Ursinus-CS374-Fall2026/blob/gh-pages/_pages/Activities/liascript-syntaxbnf.md or locally via https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374/gh-pages/_pages/Activities/liascript-syntaxbnf.md

import: https://raw.githubusercontent.com/liascript/CodeRunner/master/README.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

# Syntax and BNF/EBNF

English describes syntax vaguely; a language definition cannot afford vagueness. Today we learn **Backus-Naur Form (BNF)** and its extended cousin **EBNF**, the notations in which every modern language's syntax is published, and which your parser assignment will translate, rule by rule, into code. The arc: **why formal syntax $\rightarrow$ BNF mechanics $\rightarrow$ EBNF conveniences $\rightarrow$ writing grammars for real constructs**.

---

## Directions and Group Roles

Work in your POGIL team with rotated roles (**Manager**, **Recorder**, **Presenter**, **Reflector**). Consider each model and question individually first, then discuss with your group. The Recorder posts answers to the Class Activity Questions discussion board; the Presenter reports out areas of disagreement or alternative approaches. After class, respond to the reflective prompt individually in your notebook.

---

# Part I: BNF

## 1. The Notation

**A BNF grammar is a set of rewriting rules.** Each rule (a *production*) has the form

$$
\langle \text{nonterminal} \rangle \rightarrow \text{sequence of terminals and nonterminals}
$$

**Terminals** are the actual tokens of the language (`if`, `+`, identifiers); **nonterminals** (in angle brackets or capitalized) are named syntactic categories defined by the rules; one nonterminal is the **start symbol**. Alternatives are separated by `|`. A string belongs to the language exactly when it can be **derived** from the start symbol by repeatedly replacing nonterminals using the rules.

A tiny grammar for signed integers:

```
<signed>  -> <sign> <digits> | <digits>
<sign>    -> + | -
<digits>  -> <digit> | <digit> <digits>
<digit>   -> 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9
```

Note the move that makes BNF powerful: `<digits>` is defined **recursively**, using itself, which is how a finite set of rules describes infinitely many strings. Repetition in BNF *is* recursion.

---

## Model 1: Derive It

Using the grammar above, derive the string `-42`.

### Critical Thinking Questions

1. Write the derivation step by step, one rule application per line, starting from `<signed>`. The Recorder writes the team's agreed sequence.
2. How many derivation steps did `-42` take? Predict the count for `-12345` and state the general formula in terms of the number of digits.
3. Show that `4-2` cannot be derived: which rule would have to fire, and why can it not?
4. Modify the grammar so that a signed number may also be written with no digits after the sign... wait, should it? Decide as a team whether `-` alone should be a signed integer, and notice that you are now doing *language design*.

---

## 2. EBNF: Conveniences, Not New Power

**EBNF adds shorthand for the recursion patterns BNF repeats endlessly.** Braces mean zero-or-more repetition, brackets mean optional, parentheses group:

```
signed  -> [ sign ] digit { digit }
sign    -> "+" | "-"
digit   -> "0" | "1" | "2" | "3" | "4" | "5" | "6" | "7" | "8" | "9"
```

The two notations describe exactly the same languages; EBNF is sugar. The sugar matters to *you* as an implementer: when we write the parser, `{ digit }` becomes a `while` loop and `[ sign ]` becomes an `if`, a translation so mechanical you will perform it in your sleep by October.

[[MC]]
The EBNF fragment `term { ("*" | "/") term }` describes:
- ( ) Exactly one multiplication or division
- ( ) An optional single operator between two terms
- (x) A term followed by zero or more operator-term pairs, such as `a`, `a*b`, or `a*b/c`
- ( ) Nested parenthesized expressions

---

# Part II: Grammars for Real Constructs

## Model 2: Read a Real Rule

Here is a plausible EBNF rule for a programming language's `if` statement:

```
ifstmt -> "if" "(" expr ")" block [ "else" block ]
block  -> "{" { stmt } "}"
```

### Critical Thinking Questions

5. List three concrete statements this grammar accepts and two near-misses it rejects, identifying for each reject the exact point of failure.
6. Does this grammar accept `if (x) { } else { }` (empty blocks)? Point to the symbols that decide.
7. Python uses indentation instead of braces. Which rule above encodes the brace decision, and what would have to change *outside the grammar* (in the lexer) to support indentation? (Foreshadowing: lexers can emit invisible tokens.)

---

## Code Cell

```python
# A grammar is data. Here is the signed-integer EBNF as a Python structure,
# and a hand-rolled recognizer that follows it: [sign] digit {digit}.

def recognize_signed(s):
    """Return True if s matches: [ sign ] digit { digit }"""
    try:
        i = 0
        if i < len(s) and s[i] in "+-":   # [ sign ]  -> an if
            i += 1
        if i >= len(s) or not s[i].isdigit():   # digit, required
            return False
        i += 1
        while i < len(s) and s[i].isdigit():    # { digit } -> a while
            i += 1
        return i == len(s)
    except Exception as e:
        print(f"[syntaxbnf:recognize_signed] {e}")
        import traceback; traceback.print_exc()
        return False

for test in ["42", "-42", "+7", "4-2", "-", "", "007"]:
    print(f"{test!r:8} -> {recognize_signed(test)}")
```

---

## Model 3: The Translation Pattern

### Critical Thinking Questions

8. Match each EBNF construct to its code shape in the recognizer: `[ ... ]` became which statement, and `{ ... }` became which? This mapping is the entire secret of recursive descent parsing, six weeks early.
9. `007` is accepted. Is that a grammar bug, a feature, or a question for the language designer? Amend the EBNF to forbid leading zeros (except for `0` itself), then explain what the amendment costs in rule complexity.

---

# Part III: Synthesis and Practice

## 3. Exercises

1. *Phone grammar.* Write EBNF for US phone numbers allowing `610-409-3000`, `(610) 409-3000`, and `6104093000`. Trade with another team and find one string their grammar accepts that yours rejects.
2. *List literal.* Write EBNF for Python-style list literals of integers: `[]`, `[1]`, `[1, 2, 3]`, with no trailing comma. The comma placement is the lesson; expect a false start.
3. *Recognizer extension.* Extend the code cell to recognize your phone-number grammar, preserving the construct-to-code mapping (optional becomes `if`, repetition becomes `while`). Report your test cases and results.
4. *Project seed.* Draft the EBNF for *one* statement form you want in your team's language (a loop, a print, a let-binding). Keep it; these drafts accumulate into your project's grammar.

---

## Reflection Prompt

In your notebook: BNF was introduced in 1959 to define ALGOL and remains in every language manual today. Why do you think this one notation outlived nearly everything else from that era? What property would a replacement need?

---

## 4. Further Reading

- Douglas Thain. *Introduction to Compilers and Language Design*, Chapter 3.
- The Python Language Reference, section 10 (online): the full grammar of Python, in a BNF dialect, now readable to you.
- Backus et al. "Report on the Algorithmic Language ALGOL 60" (1960), where the notation debuted.
