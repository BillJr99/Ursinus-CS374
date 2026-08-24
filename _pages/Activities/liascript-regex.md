<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374-Fall2026/gh-pages/_pages/Activities/liascript-regex.md or locally via https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374-Fall2026/gh-pages/_pages/Activities/liascript-regex.md

import: https://raw.githubusercontent.com/liascript/CodeRunner/master/README.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

# Regular Expressions

Regular expressions sit at the formal foundation of every programming language: they are the notation that defines what a *token* looks like before a parser ever sees it.  Think of a regex as a cookie cutter: it describes a precise shape (a pattern) that can stamp out any number of matching strings from the dough of possible input, without caring what flavor the dough is.  Because a single pattern can describe an infinite set of strings (e.g., all valid identifiers), regular expressions give language designers a compact, mathematically grounded way to specify lexical rules.

## Learning Goals

By the end of this activity, you will be able to:

- Define the three fundamental regular expression operators (concatenation, alternation, Kleene star) and construct regular expressions for specified string sets using only these operators
- Trace a regular expression against a target string to predict whether it matches, citing operator precedence rules where applicable
- Implement pattern matching, capturing, and substitution tasks using Python's `re` module (`match`, `search`, `fullmatch`, `findall`, `sub`)
- Identify the limits of regular expressions by constructing a language that requires counting or matching nested structure, and explaining why no regex can describe it
- Write the regular expression for a programming language token type (identifier, integer literal, floating-point literal) suitable for use in a lexer specification

The Chomsky hierarchy's bottom rung (mapped in *Grammars and the Chomsky Hierarchy*), regular languages, comes with the most widely used notation in computing: **regular expressions**.  Over this two-day module we master them twice: as *theory* (three operators and what they can and cannot describe) and as *practice* (Python's `re` library, the tool of your next assignment and the specification language of your lexer).  We take today in this order: **the three operators $\rightarrow$ practical syntax $\rightarrow$ matching, capturing, substituting in Python $\rightarrow$ the limits**.

---

> **Before You Begin**, make sure you are comfortable with the following before diving in:
>
> - **Python `re` module basics**: you should know how to import `re` and call `re.search` or `re.match` with a pattern string; if not, skim the [Python `re` HOWTO](https://docs.python.org/3/howto/regex.html) for five minutes.
> - **Lexers and tokens**: recall that a lexer (scanner) reads source text and groups characters into *tokens* (e.g., an integer literal, an identifier, a keyword).  Its job is essentially pattern matching: each token type has a pattern it must fit.
> - **Finite automata (conceptually)**: you do not need to draw one yet, but you should know that a finite automaton is a machine with a fixed set of states and no unbounded memory.  Regular expressions and finite automata turn out to describe exactly the same class of languages; that connection is the bridge to the next module.

---

## Directions and Group Roles

Work in your POGIL team with your rotated roles (**Manager**, **Recorder**, **Presenter**, **Reflector**).  Please think each model and question through on your own first, then talk it over with your group.  The Recorder posts your answers to the Class Activity Questions discussion board, and the Presenter reports out wherever you disagreed or found another approach.  After class, please respond to the reflective prompt on your own in your notebook.

---

## Key Concepts

Here is a plain-English glossary of the terms this activity uses.  Please come back to this table whenever one of them starts to feel slippery.

| Term | Plain-English meaning | Why it matters |
|------|-----------------------|----------------|
| **Regular expression** | A compact pattern that describes a whole *set* of strings at once | It is the specification language for every token type in your lexer |
| **Concatenation** | Gluing patterns side by side: "this, then that" | The invisible default operator; most of any pattern is concatenation |
| **Alternation (`\|`)** | "Either this or that" | Lets one pattern cover several spellings, like `if\|else\|while` |
| **Kleene star (`*`)** | "Zero or more repeats of the thing just before me" | The only source of infinity in a regex; identifiers of any length need it |
| **Character class (`[0-9]`, `\d`)** | "Any one character from this menu" | Abbreviates long alternations and keeps patterns readable |
| **Anchor (`^`, `$`, `\b`)** | Matches a *position* (start, end, word edge), not a character | Stops a match from beginning or ending mid-word |
| **Capture group `(...)`** | Parentheses that *remember* the text they matched | How you extract data from text rather than merely detect it |
| **Greedy quantifier** | Takes as many characters as it can, giving some back only when forced | Explains most "my regex matched too much" surprises |
| **Backtracking** | The engine undoes a choice and tries the next alternative | How the engine actually searches, and why some patterns are slow |
| **Token** | The smallest meaningful chunk of source code (a number, a name, an operator) | The lexer's output; each token type is defined by one regex |

---

---

## Regex at the Command Line: `grep`

You will use regular expressions this semester in two places: inside Python, where you write your lexer, and at the shell, where you search your own source tree.  The Overview assignment already asks you to submit a `grep` transcript, and you will reach for it constantly once your interpreter is a few thousand lines, and "where do I construct a `BinOp` node?" is a `grep` question rather than a scrolling question.

`grep` prints every **line** of its input that contains a match.  That is the whole idea.  Everything else is flags.

### The flags that earn their keep

| Flag | Does | Use it when |
|------|------|-------------|
| `-n` | prefix each match with its line number | almost always, you want to jump there |
| `-r` | recurse into a directory tree | searching a project rather than one file |
| `-i` | ignore case | you are unsure how something was capitalized |
| `-w` | match whole words only | searching `eval` without hitting `evaluate` |
| `-v` | invert: print lines that do **not** match | filtering noise out of a log |
| `-c` | print only the count of matching lines | "how many `TODO`s are left?" |
| `-o` | print only the matched part, not the whole line | harvesting every token name from a file |
| `-l` | print only the filenames that matched | "which files mention `Environment`?" |
| `-E` | use **extended** regex syntax | any pattern with `+`, `?`, `|`, or `()` |

```bash
grep -rn "def parse_" src/              # every parse function, with line numbers
grep -rn --include="*.py" "Environment" .   # only Python files
grep -c "TODO" interpreter.py           # how much is left
grep -rnw "eval" src/                   # eval, not evaluate
grep -rnoE "[A-Z]+_[A-Z]+" lexer.py     # harvest SCREAMING_CASE token names
```

### The one thing that surprises everyone: BRE vs ERE

Plain `grep` uses **POSIX Basic Regular Expressions (BRE)**, where `+`, `?`, `|`, `(` and `)` are *literal characters*.  To get the meanings you know from Python, you must either escape them with a backslash or pass `-E` for **Extended** regular expressions.

| You want | BRE (plain `grep`) | ERE (`grep -E`) | Python `re` |
|---|---|---|---|
| one or more | `a\+` | `a+` | `a+` |
| optional | `a\?` | `a?` | `a?` |
| alternation | `cat\|dog` | `cat\|dog` | `cat\|dog` |
| grouping | `\(ab\)*` | `(ab)*` | `(ab)*` |
| exactly 3 | `a\{3\}` | `a{3}` | `a{3}` |

```bash
grep -n  "TODO\|FIXME" notes.md    # BRE: escaped alternation
grep -nE "TODO|FIXME"   notes.md    # ERE: reads like Python
```

**Just use `-E`.**  The escaping rules in BRE are a historical artifact, and every pattern you write in this course will already be in the syntax `-E` expects.  (`egrep` is the same thing under an older name.)


> Worked grep examples (character classes, anchors, and the POSIX-vs-Python portability traps) are in [The Shell for Language Development](https://www.billmongan.com/Ursinus-CS374/Tutorials/ShellForLanguageDev), required prep for today.

# Part I: Theory (Day 1)

Every regular expression you will ever write, no matter how elaborate, is built from exactly three primitive ideas.  Before reading the formal definitions, convince yourself intuitively: you can glue strings together (concatenation), pick one of several alternatives (alternation), and repeat something zero or more times (Kleene star).  That is the entire toolkit; the rest of regex syntax is just abbreviation.

## 1.  Three Operators Build Everything

A regular expression denotes a set of strings, built from three operations.  Given expressions $r$ and $s$ denoting languages $L(r)$ and $L(s)$:

$$
\underbrace{r\,s}_{\text{concatenation}} \quad \underbrace{r \mid s}_{\text{alternation (union)}} \quad \underbrace{r^*}_{\text{Kleene star: zero or more}}
$$

plus single characters and the empty string.  Everything else in practical regex (character classes, `+`, `?`, ranges) is shorthand: $r^+ = rr^*$, $r? = (r \mid \varepsilon)$, $[abc] = (a \mid b \mid c)$. These three operators generate exactly the regular languages, the same class as Type 3 grammars and (next module) finite automata, three notations for one idea.

---

Before running any code, practice reading patterns the way a regex engine does: left to right, respecting precedence (star binds tightest, then concatenation, then alternation).  The table below asks you to predict what each pattern matches; commit to a prediction first, then verify with the code.  Mismatches between prediction and output are your most valuable learning signal.

> **Watch out!**  The `*` in a regular expression is the **Kleene star**: it means "zero or more repetitions of the preceding element."  It is *not* the glob wildcard you may know from the shell (where `*.py` means "any filename ending in `.py"`).  In regex, `.*` means "any character, zero or more times," while a bare `*` with nothing before it is a syntax error.

## Model 1: Read Before You Write

| Pattern | Intended meaning? |
|---------|-------------------|
| `ab*c` | ? |
| `(ab)*c` | ? |
| `a(b\|c)d` | ? |
| `[0-9]+\.[0-9]+` | ? |

**Verify your predictions:**

```python
import re

patterns = [
    ("ab*c",          ["ac", "abc", "abbc", "abbbbc", "aXc"]),
    ("(ab)*c",        ["c", "abc", "ababc", "ac", "abbc"]),
    ("a(b|c)d",       ["abd", "acd", "ad", "abcd", "aad"]),
    (r"[0-9]+\.[0-9]+", ["3.14", "0.0", "123.456", "3", ".14", "3."]),
]

for pattern, tests in patterns:
    print(f"\nPattern: {pattern!r}")
    for s in tests:
        m = re.fullmatch(pattern, s)
        print(f"  {s!r:12} -> {'MATCH' if m else 'no match'}")
```
@LIA.eval(`["main.py"]`, `none`, `python3 main.py`)

### Critical Thinking Questions

1.  For each pattern, write the set of strings in plain English and give two members and one non-member.  Where did `ab*c` versus `(ab)*c` divide the team?
2.  Star binds tighter than concatenation, which binds tighter than `|`.  Where have you seen this exact design move (precedence by convention) before, in the *Derivations, Parse Trees, Ambiguity, and Precedence* activity, and what notation made it unambiguous there?
3.  Write a regular expression for identifiers as most languages define them: a letter or underscore, followed by any number of letters, digits, or underscores.  This pattern reappears, verbatim, in your lexer.

---


> **Continued next session.**  Day 2 picks up from here: [Regular Expressions, Day 2: Practice](https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374-Fall2026/gh-pages/_pages/Activities/liascript-regex-day2.md).
