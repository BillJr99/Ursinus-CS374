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

A regular expression (regex) is a short pattern that describes a whole set of strings at once.  Every programming language uses regular expressions to say what a *token* looks like before the parser ever sees the source text.  One pattern can describe an infinite set, such as every valid identifier, so a language designer gets a compact and mathematically grounded way to state the lexical rules.  A regex is like a cookie cutter: one shape stamps out any number of matching strings from the dough of possible input.  The analogy stops there, because a regex also rejects strings that do not fit, and a cookie cutter never says no.

## Learning Goals

By the end of *today*, you will be able to:

- Define the three basic regular expression operators (concatenation, alternation, Kleene star) and write regular expressions for given string sets using only those operators
- Trace a regular expression against a target string to predict whether it matches, citing the precedence rules where they apply
- Show that each convenience in practical regex syntax (`+`, `?`, `[a-z]`, `{n,m}`) is shorthand, by rewriting a pattern in the three primitives and checking that both versions describe the same language
- Write the regular expression for a programming language token type (identifier, integer literal, floating-point literal) that a lexer specification could use
- Search a source tree with `grep`, choosing the right flags and avoiding the BRE-versus-ERE trap

Day 2 puts these into practice: Python's `re` in five verbs, how the engine backtracks, greed, and the point where regular expressions run out of power.

Regular languages are the bottom rung of the Chomsky hierarchy, which the *Grammars and the Chomsky Hierarchy* activity mapped.  They come with the most widely used notation in computing.  Today's path is the three operators, then precedence, then real token patterns built from the primitives, then regex at the shell.

> **Before You Begin**, make sure you are comfortable with the following:
>
> - Lexers and tokens: a lexer reads source text and groups characters into *tokens* (an integer literal, an identifier, a keyword).  Its job is pattern matching.  Each token type has a pattern that the text must fit.
> - Finite automata, in outline: you do not need to draw one yet.  You should know that a finite automaton is a machine with a fixed set of states and no unbounded memory.  Regular expressions and finite automata describe exactly the same class of languages, and that connection is the bridge to the next module.
> - Python `re` basics: you should know how to `import re` and call `re.search`.  If not, skim the [Python `re` HOWTO](https://docs.python.org/3/howto/regex.html) for five minutes.

---

## Directions and Group Roles

Work in your POGIL team with your rotated roles (Manager, Recorder, Presenter, Reflector).  Every model here is a predict-then-verify exercise.  Write down what you think each pattern matches *before* you press run.  The patterns you got wrong teach you more than the ones you got right, so mark them.  The Recorder posts your answers to the Class Activity Questions discussion board.  The Presenter reports out wherever your team disagreed.

---

## Key Concepts

A plain-English glossary.  Come back to it whenever one of these terms starts to feel slippery.

| Term | Plain-English meaning | Why it matters |
|------|-----------------------|----------------|
| **Regular expression** | A compact pattern that describes a whole *set* of strings at once | It is the specification language for every token type in your lexer |
| **Concatenation** | Gluing patterns side by side: "this, then that" | The invisible default operator; most of any pattern is concatenation |
| **Alternation (`\|`)** | "Either this or that" | Lets one pattern cover several spellings, like `if\|else\|while` |
| **Kleene star (`*`)** | "Zero or more repeats of the thing just before me" | The only source of infinity in a regex; identifiers of any length need it |
| **Quantifier (`*`, `+`, `?`, `{n,m}`)** | A suffix that says how many times the thing just before it may repeat | `*` is the primitive; the rest are shorthand for it |
| **Character class (`[0-9]`, `\d`)** | "Any one character from this menu" | Abbreviates a long alternation and keeps the pattern readable |
| **Anchor (`^`, `$`, `\b`)** | Matches a *position* (start, end, word edge), not a character | Stops a match from beginning or ending in the middle of a word |
| **Capture group `(...)`** | Parentheses that *remember* the text they matched | How you extract data from text instead of only detecting it |
| **Greedy quantifier** | Takes as many characters as it can, and gives some back only when forced | Explains most "my regex matched too much" surprises |
| **Token** | The smallest meaningful chunk of source code (a number, a name, an operator) | The lexer's output; one regex defines each token type |

---

# Part I: Three Operators Build Everything

## 1.  Theory: The Entire Toolkit

Every regular expression you will ever write is built from three ideas.  You can glue strings together, you can pick one of several alternatives, and you can repeat something zero or more times.  That is the whole toolkit.  Convince yourself of that before the formalism.

A regular expression denotes a set of strings, called its language.  Given expressions $r$ and $s$ that denote languages $L(r)$ and $L(s)$, the three operators are:

$$
\underbrace{r\,s}_{\text{concatenation}} \quad \underbrace{r \mid s}_{\text{alternation (union)}} \quad \underbrace{r^*}_{\text{Kleene star: zero or more}}
$$

Concatenation $r\,s$ means "a string from $r$, then a string from $s$."  Alternation $r \mid s$ means "a string from $r$ or a string from $s$."  The Kleene star $r^*$ means "zero or more strings from $r$, one after another."  Add single characters and the empty string $\varepsilon$, and you have all of it.  Everything else in practical regex is shorthand:

$$r^+ = r\,r^* \qquad r? = (r \mid \varepsilon) \qquad [abc] = (a \mid b \mid c)$$

These three operators generate exactly the regular languages.  That is the same class as the Type 3 grammars of the last module and, next module, the finite automata.  Three notations, one idea.

Precedence decides how a pattern groups when you leave out parentheses.  Star binds tightest, then concatenation, then alternation.  So `ab*c` is `a`, then zero or more `b`, then `c`.  It is *not* zero or more `ab` followed by `c`.  If you want that, write `(ab)*c`.  You met this design move in *Derivations, Parse Trees, Ambiguity, and Precedence*: a convention disambiguates the notation, and parentheses override the convention.

> **Watch out.**  The `*` in a regular expression is the Kleene star: zero or more repetitions of the element before it.  It is *not* the glob wildcard from the shell, where `*.py` means "any filename ending in `.py`."  In regex, "any characters" is `.*`, and a bare `*` with nothing before it is a syntax error.

## Examples: Parse the Pattern Before You Run It

Read each pattern the way the engine does: left to right, applying precedence.  Fill in the third column with your team *before* you look at any output.

| Pattern | How precedence groups it | What set does it denote? |
|---------|--------------------------|--------------------------|
| `ab*c` | `a` · (`b`)\* · `c` | ? |
| `(ab)*c` | (`a` · `b`)\* · `c` | ? |
| `a(b\|c)d` | `a` · (`b` \| `c`) · `d` | ? |
| `ab\|cd` | (`a` · `b`) \| (`c` · `d`) | ? |
| `[0-9]+\.[0-9]+` | one-or-more digits · literal `.` · one-or-more digits | ? |

The fourth row catches people.  Alternation binds *loosest*, so `ab|cd` means "either `ab` or `cd`."  It does not mean "`a`, then `b` or `c`, then `d`."  For each row, write two members of the set and one non-member now.

## Model 1: Read Before You Write

Commit to your predictions above.  Then run this and mark every row where the machine disagreed with you.

```python
import re

patterns = [
    ("ab*c",            ["ac", "abc", "abbc", "abbbbc", "aXc", "abab c".replace(" ", "")]),
    ("(ab)*c",          ["c", "abc", "ababc", "ac", "abbc"]),
    ("a(b|c)d",         ["abd", "acd", "ad", "abcd", "aad"]),
    ("ab|cd",           ["ab", "cd", "abd", "acd", "abcd"]),
    (r"[0-9]+\.[0-9]+", ["3.14", "0.0", "123.456", "3", ".14", "3."]),
]

for pattern, tests in patterns:
    print(f"\nPattern: {pattern!r}")
    for s in tests:
        m = re.fullmatch(pattern, s)
        print(f"  {s!r:12} -> {'MATCH' if m else 'no match'}")
```
@LIA.eval(`["main.py"]`, `none`, `python3 main.py`)

### Reading the Code

- `re.fullmatch` requires the pattern to consume the entire string.  That is the right choice for a *theory* demonstration.  A regular expression denotes a set of strings, and `fullmatch` asks exactly "is this string in that set?"  `re.search`, which Day 2 uses, asks a different question: "does the set have a member somewhere inside this string?"
- `r"[0-9]+\.[0-9]+"` uses a raw string, so `\.` reaches the regex engine as an escaped dot instead of being interpreted by Python first.  Drop the `r` and Python warns you.  Get in the habit now.
- `.` matches *any* character, so an unescaped `[0-9]+.[0-9]+` would also match `3x14`.  The escape is not decoration.

### Critical Thinking Questions

1.  For each pattern, write the denoted set in plain English and give two members and one non-member.  Where did `ab*c` versus `(ab)*c` divide the team?
2.  `ab|cd` rejects `abd` and `acd`.  Explain that using precedence, in one sentence, without using the word "obviously."
3.  Star binds tighter than concatenation, which binds tighter than `|`.  Where have you seen this exact design move before, in *Derivations, Parse Trees, Ambiguity, and Precedence*, and what notation made it unambiguous there?
4.  `re.fullmatch("(ab)*c", "c")` matches.  Which of the three operators makes the empty repetition legal, and what would you write instead if you wanted *at least one* `ab`?

### Try It Yourself

Write patterns for three specified sets.  Then check them against inputs designed to catch the usual mistakes.

```python
import re

# TODO: replace each None with a pattern using ONLY the three primitives
#       and character classes. No + or ? yet; those come in Part II.
tasks = [
    # (your pattern, description, should_match, should_not_match)
    (None, "any number of a's, then exactly one b",
        ["b", "ab", "aaab"],            ["a", "abb", "ba"]),
    (None, "the words cat or dog, nothing else",
        ["cat", "dog"],                 ["cats", "ca", "catdog"]),
    (None, "a binary string of even length (including empty)",
        ["", "01", "1010"],             ["0", "101"]),
]

for pattern, desc, yes, no in tasks:
    print(f"\n{desc}")
    if pattern is None:
        print("  (not written yet)")
        continue
    print(f"  pattern: {pattern!r}")
    for s in yes:
        ok = re.fullmatch(pattern, s)
        print(f"    {s!r:8} should MATCH   -> {'ok' if ok else 'FAILED'}")
    for s in no:
        ok = re.fullmatch(pattern, s)
        print(f"    {s!r:8} should NOT match -> {'ok' if not ok else 'FAILED'}")
```
@LIA.eval(`["main.py"]`, `none`, `python3 main.py`)

Expected output once all three are written: every line reads `ok`.  The third task is the interesting one.  Think about what "a pair of characters" looks like as a single starred group.

To remember from Part I: three operators (concatenation, alternation, star) build every regular expression, and star binds tightest while alternation binds loosest.  When precedence would group a pattern the wrong way, parentheses fix it.

---

# Part II: From Primitives to Real Token Patterns

## 2.  Theory: All the Convenience Is Sugar

Practical regex syntax is large, and almost none of it adds power.  Each convenience below expands to the three primitives:

| Shorthand | Expansion in primitives | Reads as |
|-----------|-------------------------|----------|
| `r+` | `r r*` | one or more |
| `r?` | `(r \| ε)` | optional |
| `[abc]` | `(a \| b \| c)` | one from the menu |
| `[a-c]` | `(a \| b \| c)` | one from the range |
| `r{2}` | `r r` | exactly two |
| `r{1,3}` | `(r \| rr \| rrr)` | between one and three |

This matters for two reasons.  First, the class of languages you can describe never grows, no matter how much syntax a regex dialect adds.  It stays regular.  Second, when a pattern misbehaves, expanding the sugar in your head is often the fastest way to see why.

There is one exception, and you should know it now so it does not surprise you later.  A backreference (`(a+)\1`, meaning "the same text again") leaves the regular languages behind.  Most modern "regex" engines are therefore not, strictly, regular expression engines.  Day 2 returns to this when it looks at what the engine actually does.

## Examples: Building an Identifier Pattern by Hand

Most languages define an identifier as a letter or underscore, followed by any number of letters, digits, or underscores.  Build the pattern in stages, on paper, before you run anything.

| Stage | Pattern | Reasoning |
|-------|---------|-----------|
| 1. First character, spelled out | `(a\|b\|...\|z\|A\|...\|Z\|_)` | alternation over the whole menu |
| 2. Same thing, as a class | `[a-zA-Z_]` | sugar for stage 1 |
| 3. Later characters, one of them | `[a-zA-Z0-9_]` | digits are now allowed |
| 4. Any number of later characters | `[a-zA-Z0-9_]*` | Kleene star |
| 5. Concatenate | `[a-zA-Z_][a-zA-Z0-9_]*` | the finished pattern |

Now do the same for two more token types before you look at the code:

- an integer literal: one or more digits
- a float literal: digits, a dot, digits

Write each one twice: once in the three primitives only, and once with sugar.  You are about to check that the two versions describe the same language.

## Model 2: Sugar and Primitives Describe the Same Set

This model writes each token pattern both ways and tests them against the same inputs.  If the sugar is really sugar, the two columns must agree on every row.

```python
import re

# Each entry: (name, sugary pattern, the SAME language in bare primitives)
TOKENS = [
    ("integer",
     r"[0-9]+",
     r"(0|1|2|3|4|5|6|7|8|9)(0|1|2|3|4|5|6|7|8|9)*"),

    ("identifier",
     r"[a-zA-Z_][a-zA-Z0-9_]*",
     # abbreviated menus to keep the line readable; same idea, fewer letters
     r"(a|b|c|_)(a|b|c|_|0|1|2)*"),

    ("float",
     r"[0-9]+\.[0-9]+",
     r"(0|1|2)(0|1|2)*\.(0|1|2)(0|1|2)*"),

    ("optional sign",
     r"-?[0-9]+",
     r"(-|)(0|1|2)(0|1|2)*"),
]

INPUTS = {
    "integer":       ["0", "42", "007", "", "4a", "-7"],
    "identifier":    ["a", "abc", "_a1", "c_2", "1a", "", "a-b"],
    "float":         ["1.2", "10.01", "1.", ".2", "12", "1.2.3"],
    "optional sign": ["1", "-1", "-", "--1", "12", ""],
}

for name, sugar, primitive in TOKENS:
    print(f"\n=== {name} ===")
    print(f"  sugar:     {sugar}")
    print(f"  primitive: {primitive}")
    disagreements = 0
    for s in INPUTS[name]:
        a = bool(re.fullmatch(sugar, s))
        b = bool(re.fullmatch(primitive, s))
        flag = "" if a == b else "   <-- DISAGREE"
        if a != b: disagreements += 1
        print(f"    {s!r:8} sugar={str(a):5} primitive={str(b):5}{flag}")
    print(f"  -> {'identical on every input' if not disagreements else str(disagreements) + ' disagreements'}")

print("\nWhere the two columns disagree, the primitive version has a SMALLER")
print("alphabet (only a,b,c and 0,1,2), not different power. Widen the menus")
print("and the disagreements vanish. Sugar adds no power, only readability.")
```
@LIA.eval(`["main.py"]`, `none`, `python3 main.py`)

### Reading the Code

- The `integer` row is the honest one.  `[0-9]+` and the fully spelled-out ten-way alternation agree on *every* input, because the primitive version has the full digit menu.
- The `identifier` and `float` rows shrink the alphabet on purpose so the lines stay readable.  Where they disagree, look at *which* input caused it.  It will always be a character outside the abbreviated menu, never a structural difference.
- `-?[0-9]+` versus `(-|)...` shows `?` expanding to an alternation with the empty string.  `(-|)` is legal: the right branch of the alternation is $\varepsilon$.
- Nothing here needs `re.search`.  `fullmatch` asks the set-membership question, and that question is what "these two patterns denote the same language" means.

> **Watch out.**  `[0-9]+` and `\d+` are *almost* the same thing.  In Python, `\d` matches Unicode decimal digits, which include characters like the Devanagari digit `४`.  For a lexer, that is usually not what you want, and `[0-9]` says exactly what you mean.  Be deliberate.

### Critical Thinking Questions

5.  `re.fullmatch(r"[0-9]+", "007")` matches.  Is that correct for an *integer literal* in your project language?  If you want to forbid leading zeros, write the pattern.  What did it cost in complexity?
6.  The float pattern rejects `1.` and `.2`.  Some languages accept both.  Amend the pattern to accept them and say what new ambiguity you have introduced with the lexer's other rules.
7.  Expand `[a-c]{2,3}` by hand into the three primitives.  How many alternatives does it become?  Now expand `[a-z]{2,3}` in your head and say why nobody writes patterns this way.
8.  Backreferences let you write `(a+)\1` for "some a's, then the same a's again."  Which language from *Grammars and the Chomsky Hierarchy* does that resemble, and what does its existence tell you about the word "regex" as used by working programmers?

### Try It Yourself

Write the token patterns for a small language, and make the test suite pass.

```python
import re

# TODO: fill in each pattern. These are the actual token classes you will
#       need for your lexer, so keep whatever you write here.
SPEC = {
    "INT":    None,   # one or more digits, no leading zeros unless the number IS 0
    "IDENT":  None,   # letter or underscore, then letters/digits/underscores
    "FLOAT":  None,   # digits, dot, digits (both sides required)
    "OP":     None,   # one of + - * / = < >
}

CASES = {
    "INT":   (["0", "7", "42", "1000"],        ["007", "", "4a", "-1", "1.0"]),
    "IDENT": (["x", "_x", "abc", "a1", "A_9"], ["1a", "", "a-b", "a b"]),
    "FLOAT": (["1.0", "3.14", "0.5"],          ["1", "1.", ".5", "1.2.3"]),
    "OP":    (["+", "-", "*", "/", "=", "<"],  ["++", "", "a", "<="]),
}

for name, pattern in SPEC.items():
    yes, no = CASES[name]
    print(f"\n{name}: {pattern!r}")
    if pattern is None:
        print("  (not written yet)")
        continue
    for s in yes:
        print(f"    {s!r:8} should MATCH     -> "
              f"{'ok' if re.fullmatch(pattern, s) else 'FAILED'}")
    for s in no:
        print(f"    {s!r:8} should NOT match -> "
              f"{'ok' if not re.fullmatch(pattern, s) else 'FAILED'}")
```
@LIA.eval(`["main.py"]`, `none`, `python3 main.py`)

Expected output once all four are written: every line reads `ok`.  `INT` is the hard one, because "no leading zeros unless the number is 0" is an alternation, not a repetition.

To remember from Part II: `+`, `?`, character classes, and `{n,m}` are shorthand for the three primitives, so they add readability and no power.  Backreferences are the one common feature that does add power, and they take you outside the regular languages.

---

# Part III: Regex at the Command Line

You will use regular expressions in two places this semester.  Inside Python, you write your lexer with them.  At the shell, you search your own source tree with them.  The Overview assignment asks you to submit a `grep` transcript, and you will reach for `grep` constantly once your interpreter is a few thousand lines long and "where do I construct a `BinOp` node?" becomes a search question instead of a scrolling question.

`grep` prints every line of its input that contains a match.  Everything else it does is flags.

## The flags you will use most

| Flag | Does | Use it when |
|------|------|-------------|
| `-n` | prefix each match with its line number | almost always; you want to jump there |
| `-r` | recurse into a directory tree | searching a project rather than one file |
| `-i` | ignore case | you are unsure how something was capitalized |
| `-w` | match whole words only | searching `eval` without hitting `evaluate` |
| `-v` | invert: print lines that do not match | filtering noise out of a log |
| `-c` | print only the count of matching lines | "how many `TODO`s are left?" |
| `-o` | print only the matched part, not the whole line | harvesting every token name from a file |
| `-l` | print only the filenames that matched | "which files mention `Environment`?" |
| `-E` | use extended regex syntax | any pattern with `+`, `?`, `\|`, or `()` |

```bash
grep -rn "def parse_" src/                   # every parse function, with line numbers
grep -rn --include="*.py" "Environment" .    # only Python files
grep -c "TODO" interpreter.py                # how much is left
grep -rnw "eval" src/                        # eval, not evaluate
grep -rnoE "[A-Z]+_[A-Z]+" lexer.py          # harvest SCREAMING_CASE token names
```

## The three operators, at the shell

Everything from Part I works here.  These are the same patterns, aimed at files instead of strings:

```bash
grep -nE "^def "               parser.py    # ^ anchors to the start of the line
grep -nE "return$"             parser.py    # $ anchors to the end
grep -nE "\bnum\b"             lexer.py     # \b is a word boundary: num, not number
grep -nE "[0-9]+\.[0-9]+"      lexer.py     # a float literal; note the escaped dot
grep -nE "[[:alpha:]_][[:alnum:]_]*" lexer.py   # POSIX class: an identifier
```

Two portability notes, so you learn them now rather than at 2am.  `\d` and `\w` are not POSIX and may not work in every `grep`.  The portable spellings are `[0-9]` and `[[:alnum:]_]`.  And `.` still means "any character," so a literal dot needs escaping: `[0-9]+\.[0-9]+` matches `3.14`, while `[0-9]+.[0-9]+` would also match `3x14`.

## BRE versus ERE

Plain `grep` uses POSIX Basic Regular Expressions (BRE).  In BRE, `+`, `?`, `|`, `(` and `)` are *literal characters*.  To get the meanings you know from Python, you must either escape them with a backslash or pass `-E` for Extended Regular Expressions (ERE).

| You want | BRE (plain `grep`) | ERE (`grep -E`) | Python `re` |
|---|---|---|---|
| one or more | `a\+` | `a+` | `a+` |
| optional | `a\?` | `a?` | `a?` |
| alternation | `cat\|dog` | `cat\|dog` | `cat\|dog` |
| grouping | `\(ab\)*` | `(ab)*` | `(ab)*` |
| exactly 3 | `a\{3\}` | `a{3}` | `a{3}` |

```bash
grep -n  "TODO\|FIXME" notes.md     # BRE: escaped alternation
grep -nE "TODO|FIXME"   notes.md    # ERE: reads like Python
```

**Use `-E` every time.**  The escaping rules in BRE are a historical artifact, and every pattern you write in this course is already in the syntax `-E` expects.  (`egrep` is the same thing under an older name.)

> **Check yourself.**  You run
>
> ```bash
> grep -n "lexer|parser" src/main.py
> ```
>
> and get no output, though the file plainly contains both words.  What went wrong?
>
> Plain `grep` uses BRE, where `|` is a literal character, so it searched for the seven-character string `lexer|parser`.  Use `grep -nE`, or escape it as `lexer\|parser`.

> **Watch out.**  `grep` is line-oriented, so it cannot match a pattern that spans a newline.  When you want that ("find every function whose body contains `raise`"), you have left regular-language territory and you want a parser.  That is the same boundary Day 2 draws between regular expressions and context-free grammars.  It shows up in your tools as well as in your theory.

To remember from Part III: `grep -rnE` covers nearly every search you will run, and plain `grep` treats `+`, `?`, `|`, and parentheses as literal characters.  Escape the dot when you mean a dot.

---

# Check Your Understanding

Which set does `ab*c` denote?

[(X)] An `a`, then zero or more `b`s, then a `c`
[( )] Zero or more repetitions of `ab`, then a `c`
[( )] An `a`, then a `b`, then zero or more `c`s
[( )] Any string containing `a`, `b`, and `c` in some order

---

`ab|cd` does not match `abd`.  Why?

[(X)] Alternation binds loosest, so the pattern means "either `ab` or `cd`" and neither is `abd`
[( )] `|` is a literal character in Python's `re`
[( )] `re.fullmatch` requires the pattern to be anchored
[( )] The pattern is a syntax error

---

`r+` is shorthand for which expression in the three primitives?

[(X)] `r r*`
[( )] `r*`
[( )] `(r | ε)`
[( )] `r r`

---

You run `grep -n "parse_(expr|term)" src/` and get nothing, though both functions exist.  The fix is:

[(X)] Add `-E`; plain grep uses BRE, where `(`, `)` and `|` are literal characters
[( )] Add `-i` to ignore case
[( )] Escape the underscore as `\_`
[( )] Use `-v` to invert the match

---

Adding `{n,m}`, `[a-z]`, `?` and `+` to a regex dialect:

[(X)] Adds convenience but no power; the class of describable languages stays regular
[( )] Moves the dialect up to context-free
[( )] Makes patterns match faster
[( )] Is required to describe identifiers

---

# Exercises

**Exercise 1.**  Write a regular expression for a string literal: a double quote, any number of characters that are not double quotes, then a double quote.  Now amend it to allow `\"` inside the string.  What made the second version so much harder, and what does that suggest about hand-writing lexers for string literals?

**Exercise 2.**  Expand `[ab]{1,2}c` fully into the three primitives.  Then write the same pattern for `[a-z]{1,2}c` *without* expanding, and say in one sentence why the shorthand exists.

**Exercise 3.**  For your project's token set, write the full regex specification: every token type with its pattern, in a table.  Mark the pairs where one pattern can match a prefix of another (`<` and `<=`, say) and say which must be tried first.  That ordering is a real bug source in the Lexer assignment.

**Exercise 4.**  Use `grep -rnoE` on any Python project on your machine to harvest every function name defined in it.  Show the command and the first ten lines of output.  Then explain which part of your pattern did the work and which part was there only to anchor it.

**Exercise 5.**  Prove to yourself that `.` needs escaping: run `grep -nE "[0-9]+.[0-9]+"` and `grep -nE "[0-9]+\.[0-9]+"` over the same file and show one line that only the first one matches.

---

# Reflection

In your notebook: a regular expression is a *finite* description of a possibly *infinite* set.  That is a strange and powerful thing, and you already use it every day without remarking on it.

Write a paragraph about another finite description of an infinite set that you rely on: a recipe, a rule, a definition, a piece of notation.  What does the description let you do that listing the members never could?  Then, in two sentences: which of the three operators do you think does the most work in that analogy, and why?

---

# Further Reading

- Allison, Chapter 3 §3.1-3.2, on regular expressions and their equivalence to finite automata.
- Allison, Chapter 4, on the pumping lemma (the standard tool for proving that a language is *not* regular, by showing that every long enough string in it has a piece you can repeat).  It is required for the Regex assignment's Part 4 theory questions, and we work one example in class on Day 2.
- The Python [`re` HOWTO](https://docs.python.org/3/howto/regex.html), which Day 2 works through in five verbs.
- [The Shell for Language Development](https://www.billmongan.com/Ursinus-CS374-Fall2026/Tutorials/ShellForLanguageDev), whose grep appendix goes further than Part III: named capture groups and a full log-triage walkthrough that turns unstructured log lines into structured records.

---

> **Where the practice went.**  Everything that used to be a second day of this activity (Python's `re` in five verbs, watching the engine backtrack, and the one-pattern scanner) is now the first half of the [Lab: Regex Workshop](https://www.billmongan.com/Ursinus-CS374-Fall2026/Assignments/RegexWorkshop), handed out today.  It is written as a walkthrough: run every cell, then vary it.
