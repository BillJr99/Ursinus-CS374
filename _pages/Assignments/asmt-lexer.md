---
layout: assignment
permalink: /Assignments/Lexer
title: "CS374: Principles of Programming Languages - The Lexer"

info:
  coursenum: CS374
  purpose: "To turn the class tokenizer into the first permanent component of your language pipeline: a reusable Lexer with a stable peek/advance/expect interface that the Parser and the team project import unchanged."
  tilt:
    task: "Specify an ordered token grammar.  Build a reusable Lexer component with peek/advance/expect, string escapes, and a configurable token specification, either hand-rolled in Python or in the generator-toolchain direction (Flex or PLY).  Then add positioned error reporting and a full test suite."
    criteria: "I assess your work on a correctly ordered token spec, an idempotent side-effect-free Lexer interface, and precise error reporting with a full test suite.  The rubric applies the same way to whichever direction you choose.  The full breakdown is in the rubric below."
  points: 100
  goals:
    - To specify a complete token grammar for the project language using ordered regular-expression rules
    - To harden the class tokenizer into a reusable Lexer component with peek, advance, and expect interface methods
    - To implement string literals with escape sequences and JSON-configurable token specifications
    - To report lexical errors with precise line and column positions and support both fail-fast and collect-all error modes
    - To deliver a fully tested component that the parser assignment and team project will import unchanged
  rubric:
    - weight: 10
      description: "Part 0: Before You Start - Tokens and Scanning"
      preemerging: The line is not tokenized and no token-class patterns are written
      beginning: The line is tokenized but tokens carry no types, or the awkward cases are not addressed
      progressing: The line is hand-tokenized with types and values and three patterns are written, but no overlapping pair is identified, or the 12foo and == cases are answered without reasoning
      proficient: x = 12 + foo(3) is hand-tokenized with a type and value per token; 12foo and = = versus == are each answered with a defended position; three token-class patterns are written and one overlapping pair is identified with a statement of which rule wins and why order matters
    - weight: 27
      description: "Token Specification (Goal 1: specify a complete token grammar using ordered regular-expression rules)"
      preemerging: Fewer than half the token types in the specification table are defined, or the patterns are so incorrect that the lexer cannot tokenize even simple programs
      beginning: Most token types are defined but several patterns are wrong (e.g., keywords not prioritized over identifiers, or operators missing from the spec)
      progressing: All required token types are defined with correct patterns, but the specification has a minor ordering or coverage gap (e.g., multi-character operators not listed before single-character ones)
      proficient: Every token type in the specification table is defined in the correct priority order (keywords before IDENT, multi-character operators before their single-character prefixes, whitespace and comments skipped), showing command of ordered regular-expression rules; the spec is externalized in a loadable JSON file (or, in the generator-toolchain direction, expressed as an ordered Flex/PLY rule specification); and the lexing theory questions (Step 1d) are answered with mechanism-level reasoning about maximal munch, keyword handling, and the lexer/parser division of labor
    - weight: 36
      description: "Lexer Implementation (Goal 2: harden the tokenizer into a reusable Lexer component with peek, advance, and expect)"
      preemerging: The Lexer class does not exist or the peek/advance interface is fundamentally broken
      beginning: The Lexer class exists with peek and advance, but one or both are incorrect (e.g., peek consumes input, or advance skips tokens)
      progressing: peek and advance work correctly for most inputs, but edge cases fail (e.g., repeated peek calls return different tokens, or EOF is not handled gracefully)
      proficient: The Lexer class implements peek, advance, and expect correctly; peek is idempotent, both return an EOF token at end of input, and expect raises a located LexError on mismatch, showing that the component is ready to be imported unchanged by the parser; the lexer has no side effects at import time
    - weight: 27
      description: "Error Handling, Positions, and Test Suite (Goals 3-5: escape sequences, precise error positions, collect-all mode, and a fully tested deliverable)"
      preemerging: Lexical errors crash Python with an unhandled exception, positions are absent, and no test suite exists
      beginning: Errors are caught and reported, but positions are missing or incorrect, and the test suite covers only a handful of token types
      progressing: Errors include line and column and the test suite covers most token types, but error recovery (collect-all mode) is missing or incorrect, and escape sequences are not fully tested
      proficient: Every error includes line, column, and the offending text; collect-all mode gathers every error in a single pass without stopping; string-literal escape sequences are fully implemented; and the test suite covers all token types, all escape sequences, all maximal-munch cases, and at least five deliberate error programs with expected messages verified, showing a deliverable that the team project can import unchanged
  readings:
    - rtitle: "Tokens and Scanning Activity"
      rlink: "Activities/liascript-tokensscanning.md"
      liapage: true
    - rtitle: "regex101 (interactive regex tester; set the Flavor to Python, and switch to PCRE only to use its step-by-step debugger)"
      rlink: "https://regex101.com/"
    - rtitle: "pythex (tests patterns with Python's own re module, in your browser)"
      rlink: "https://pythex.org/"

tags:
  - lexer
  - languages
  - pipeline

---
In this assignment you turn the class tokenizer into a **component**: a module that other code imports and uses without changing it.  You leave with a `Lexer` class behind a three-method contract (`peek`, `advance`, and `expect`), a token specification you can swap out with a JSON file, and a test suite that proves both.  The Parser assignment imports this Lexer unchanged and your team project ships it, so every design decision you make here carries forward.  Test after each step before you move on.

---

## Part 0: Before You Start (Tokens and Scanning)

Do this part first, on paper, before you write any lexer code.  A scanner (the program that splits source text into tokens) is easy to write for input that behaves and interesting to write for input that does not.  The awkward cases below are the ones this assignment turns on, so form an opinion about them before you implement anything.  It takes about twenty minutes.

> **Do this.**
> 1. Hand-tokenize the line `x = 12 + foo(3)` into a token stream.  Give each token a type and a value.
> 2. Predict what your scanner should do with `12foo`, and with `= =` versus `==`.
> 3. Write the regular expressions your lexer would use for three token classes.
> 4. Identify one pair of those patterns that overlap.  Which rule wins, and why does order matter?

> **Bring to class.** Your answer for `12foo`: one token, two tokens, or an error.  Bring it even if you are not confident.  Disagreement about these cases is the point, and Part 1's ordered `TOKEN_SPEC` is where your answer becomes a design decision you have to live with.

---

## Choose Your Direction

This is one assignment with one deliverable and one rubric.  You build it in one of two directions.

| Direction | What you build | What you need | Pick this if |
|-----------|----------------|---------------|--------------|
| **Hand-rolled Python** (the core direction) | The `Lexer` yourself, in Python, on top of the `re` module, following Parts 1-3 step by step | Python 3.10 or newer and the standard library | You want step-by-step guidance through Parts 1-3: worked code at the start, then algorithms, then specifications you implement on your own.  Most students take this direction. |
| **Generator toolchain** (Flex or PLY) | The same component from a generator specification: a Flex `.l` file (for C) or a PLY `tokens`/`t_*` module (for Python), wrapped behind the same `peek`/`advance`/`expect` contract | Flex with a C compiler and `make`, or the PLY package for Python | You want hands-on time with the tools that produce the scanners inside major compilers, and you are comfortable mapping Parts 1-3 onto a generator yourself. |

The generator direction replaces the *vehicle* of Parts 1 and 2 (the `TOKEN_SPEC` list, the `tokenize` generator, and the hand-written class internals) with a generator specification.  The interface contract, Part 3's error, position, and test requirements, the deliverables, and the rubric apply the same way in both directions.  See **[The Generator-Toolchain Direction](#the-generator-toolchain-direction-flex-or-ply)** below for the full mapping.

---

## Getting Started

You need:

- Python 3.10 or newer, with only the standard library (`re`, `json`, and `dataclasses`).  There is nothing to install.  Record the version in your readme.
- Your class tokenizer.  This assignment grows it into a component, and the patterns you tested in the Regex assignment's `patterns.py` are a good source for its rules.
- A terminal and an editor.  If either is new to you, work through the [dev environment page]({{ site.baseurl }}/Tutorials/DevEnvironment) and the [shell primer]({{ site.baseurl }}/Tutorials/ShellForLanguageDev) first.

Confirm your Python version from the terminal.  On some machines the command is `python` rather than `python3`; use whichever one reports 3.10 or newer.

```bash
python3 --version
```

```text
Python 3.11.4
```

Make one folder for the assignment (`mkdir cs374-lexer`, then `cd cs374-lexer`) and create the five deliverable files in it up front so each part has a home: `lexer.py` (the Lexer module), `token_spec.json` and `token_spec_alt.json` (the two specifications from Step 2d), `test_lexer.py` (the test suite), and `readme.md` (interface notes and the Step 1d answers).  Run every command in this assignment from inside that folder.

This table shows which file each step works in, so you always know where new code goes.  The three scratch files are for trying things out, and you do not submit them.

| Step | File you work in | What you do there |
|---|---|---|
| Before You Code | `explore_lexer.py` (scratch) | run a short tour of `re`, generators, and dataclasses |
| 1a | `lexer.py` | grow `TOKEN_SPEC` to the full token table |
| 1b | `lexer.py` | define the `Token` dataclass |
| 1c | `lexer.py` | add `LexError` and the `tokenize` generator |
| 1a to 3b | `scratch.py` (scratch) | print tokens and probe each new feature |
| 1d | `readme.md` | answer the three theory questions under `Lexing Theory` |
| 2a, 2b | `lexer.py` | add the `Lexer` class: `peek`, `advance`, `expect` |
| before 2c | `groups_lexer_demo.py` (scratch) | run the capture-group walkthrough |
| 2c | `lexer.py` | add string escapes and the decoded-value field |
| 2d | `token_spec.json`, `token_spec_alt.json`, `lexer.py` | move the rules to JSON and load them |
| 3a, 3b | `lexer.py` | add error positions and the two error modes |
| 3c | `test_lexer.py`, then `test_output.txt` | write the test suite and save its output |

> **Time budget.** Part 0 takes about twenty minutes on paper.  The first thirty minutes at the keyboard get you a six-rule lexer printing tokens.  Plan the rest across the checkpoints in the pacing table below and budget roughly ten to twelve hours in total; Part 3's test suite takes longer than it looks.

### Your First 30 Minutes

> **Do this.**
> 1. In `lexer.py`, define the `Token` dataclass from Step 1b and a `TOKEN_SPEC` with just six rules: `WHITESPACE`, `LET`, `IDENT`, `EQ`, `INT`, `SEMICOLON`.
> 2. Write the `tokenize` generator from Step 1c under it.
> 3. Create `scratch.py` in the same folder with two lines: `from lexer import tokenize`, then a loop that prints each token of `tokenize("let x = 42;")`.  Keeping the demo out of `lexer.py` is what "no side effects at import time" means.
> 4. Run `python3 scratch.py` from the `cs374-lexer` folder.  You should see six lines, one per token, matching the listing in Step 1c, with line and column numbers.  The "Before You Code" section below explains every Python feature these two steps use.
> 5. Change the source to `"lets x = 42;"` and run again: `lets` must come out as a single `IDENT`.

> **If it fails.**
> - `lets` comes out as `LET` followed by `IDENT("s")`: your keyword pattern is missing its boundary check.  Add a negative lookahead such as `(?!\w)` after the keyword.  Learn that now with six rules, not later with thirty-seven.
> - `ModuleNotFoundError: No module named 'lexer'`: you ran the command from a different folder.  `cd` into `cs374-lexer` and run it again.

### Suggested Pacing

See the course schedule for the assigned and due dates.  Your starting point is the class tokenizer, together with the tested patterns from the **Regular Expressions** assignment.  Bring both with you and Part 1 becomes an extension rather than a blank page.  The Finite Automata Simulators lab falls inside this window and builds the state-machine reasoning Part 1 asks for.

| Checkpoint | You should have |
|------------|----------------|
| On assignment | `Token` dataclass and a six-rule `tokenize` generator working (grown from the class tokenizer) |
| Checkpoint 1 | Parts 1-2a: full `TOKEN_SPEC` passing all maximal-munch cases, and the core `Lexer` class with `peek`/`advance`/`expect` working |
| Automata lab due | Parts 2b-2c: string escapes and JSON configuration (both dialects) |
| Due date | Part 3 error modes with precise positions and the full test suite complete; readme written; ZIP assembled and submitted |

---

## Part 1: Token Specification

> **Why this matters.** The lexer you want follows *maximal munch*: at each position, it takes the longest token it can.  The `tokenize` loop in Step 1c does not search for the longest match, though: it tries the rules in order and takes the *first* one that matches.  So rule order is how this lexer gets maximal munch, and order the rules wrong and you get bugs: if `IDENT` appears before `IF`, then `if` lexes as an identifier named `"if"`; if `LT` (`<`) appears before `LE` (`<=`), then `<=` lexes as `LT` followed by `EQ`.  Keywords go before identifiers, and longer operators before their prefixes.  (A generator such as Flex works the other way around: it takes the longest match across all rules and uses rule order only to break ties.  Step 1d's first question asks you to reason about both rules.)

### Before You Code: How a Lexer Lives in Python

Part 1 leans on a few Python tools, and each one has a job in the lexer.  Here they are side by side before you rely on them.

| Tool | What it is | Its job in your lexer |
|---|---|---|
| a list of `(name, pattern)` tuples | an ordered sequence of pairs | `TOKEN_SPEC`: the rules, where list order is rule priority |
| `re.compile(p)` and `.match(source, pos)` | a compiled pattern that matches only if the match starts exactly at `pos` | try one rule at the current position; `None` means "this rule does not apply here" |
| `m.group()`, `m.end()` | the matched text, and the index just past it | the lexeme, and where the next token starts |
| a generator (`yield`) | a function that hands back one value each time it is asked | `tokenize`: produce one token at a time, only when the parser asks |
| `@dataclass` | a class whose `__init__`, `__repr__`, and `__eq__` Python writes for you | `Token`: four named fields, a readable printout, and `==` that compares fields |

Two details are easy to miss.

- **`match` versus `search`.**  `.match(source, pos)` succeeds only when the pattern begins exactly at `pos`.  `.search` skips ahead to the first place the pattern appears.  A lexer must use `match`, because skipping ahead would silently jump over characters that no rule recognizes.
- **How a generator stops.**  Each call to `next(gen)` runs the function until its next `yield`.  When the function returns, the next `next(gen)` raises `StopIteration`.  A `for` loop, or `list(gen)`, catches that for you.  Step 2a's `Lexer` calls `next` directly, so it has to know this.

Save the lines below as `explore_lexer.py`, a scratch file you do not submit, and run `python3 explore_lexer.py`:

```python
import re
from dataclasses import dataclass

# 1. A token specification is a list of (name, pattern) pairs.  List order is priority.
SPEC = [("INT", r"[0-9]+"), ("IDENT", r"[a-zA-Z_]\w*"), ("WS", r"[ ]+")]
print(SPEC[0], "| first rule's name:", SPEC[0][0])

# 2. Compile once; .match(source, pos) only matches starting AT pos.
INT = re.compile(r"[0-9]+")
source = "x = 42"
print(INT.match(source, 0))                 # 'x' is not a digit: None
m = INT.match(source, 4)                    # position 4 is the '4'
print(m.group(), m.start(), m.end())        # the text, where it starts, where the next token starts
print(INT.search(source, 0).group())        # search skips ahead; a lexer must not

# 3. A generator yields values one at a time, only when asked.
def count_up(n):
    for i in range(n):
        yield i
gen = count_up(2)
print(next(gen), next(gen))
try:
    next(gen)
except StopIteration:
    print("StopIteration: the generator is used up")
print(list(count_up(3)))                    # a for loop or list() asks until it stops

# 4. A dataclass writes __init__, __repr__, and __eq__ for you.
@dataclass
class Token:
    type: str
    value: str
    line: int
    col: int
a = Token("INT", "42", 1, 5)
print(a)
print(a == Token("INT", "42", 1, 5), a.type, a.col)
```

> **You should see.**
>
> ```text
> ('INT', '[0-9]+') | first rule's name: INT
> None
> 42 4 6
> 42
> 0 1
> StopIteration: the generator is used up
> [0, 1, 2]
> Token(type='INT', value='42', line=1, col=5)
> True INT 5
> ```
>
> **Predict** before you move on: in `"x = 42"`, what does `INT.match(source, 5)` return, and what is its `end()`?

The third line shows how a lexer moves forward.  `m.end()` is 6, which is where the next token begins, so advancing the position is `pos = m.end()`.

### Step 1a: Define the TOKEN_SPEC

**You write:** `lexer.py` - the full `TOKEN_SPEC` list.
**You run:** `python3 scratch.py` on each of the seven maximal-munch cases below, once Step 1c's `tokenize` works.

> **Do this.**
> 1. In `lexer.py`, grow your six-rule `TOKEN_SPEC`, a list of `(token_name, regex_pattern)` pairs with each pattern written as a raw string (`r"..."`), until it covers every row of the table below in the priority order the Notes column requires.
> 2. Put a boundary check (`(?!\w)`) on every keyword so that `iffy` falls through to `IDENT`.
> 3. List every multi-character operator before the single-character operator it starts with.

```python
TOKEN_SPEC = [
    ("COMMENT",    r"#[^\n]*"),
    ("WHITESPACE", r"[ \t\n]+"),
    # TODO: STRING (double-quoted; Step 2c adds escapes)
    # TODO: FLOAT before INT
    # TODO: every keyword, each with a (?!\w) boundary check, before IDENT
    ("IDENT",      r"[a-zA-Z_][a-zA-Z0-9_]*"),
    # TODO: LE, GE, EQEQ, NEQ, ARROW before LT, GT, EQ, BANG, MINUS
    # TODO: the remaining single-character operators and punctuation
]
```

| `# TODO` | How to think about it |
|---|---|
| STRING | For now, a string is a double quote, then any run of characters that are neither a double quote nor a newline, then a closing double quote.  Step 2c replaces the middle with an escape-aware body. |
| FLOAT before INT | A float is one or more digits, a literal dot, and one or more digits.  Escape the dot: a bare `.` in a regex matches any character.  `INT` is the digits alone, and it goes second so that `3.14` is not cut off at `3`. |
| keywords | Worked example: `("IF", r"if(?!\w)")`.  `(?!\w)` means "not followed by a letter, digit, or underscore," so `iffy` fails this rule and falls through to `IDENT`.  Write the other ten keywords the same way. |
| two-character operators | Worked example: `("LE", r"<=")`, placed above `LT`.  `GE`, `EQEQ`, `NEQ`, and `ARROW` follow the same shape, each above the one-character rule it starts with. |
| single characters | Six of them mean something in a regex and need a backslash: `+`, `*`, `(`, `)`, `{`, and `}`.  `;`, `:`, `,`, `/`, `=`, `<`, `>`, `!`, and `-` need no escape at this position. |

| Token Name | Example Lexemes | Notes |
|------------|----------------|-------|
| `COMMENT` | `# this is a comment` | Match to end of line; to be skipped |
| `WHITESPACE` | ` `, `\t`, `\n` | Skip; track newlines for line counting |
| `STRING` | `"hello"`, `"a\nb"` | Double-quoted; see Part 3 for escapes |
| `FLOAT` | `3.14`, `0.5` | Must appear before INT |
| `INT` | `42`, `0` | Non-negative; sign handled by unary minus |
| `IF` | `if` | Must appear before IDENT |
| `ELSE` | `else` | Must appear before IDENT |
| `WHILE` | `while` | Must appear before IDENT |
| `LET` | `let` | Must appear before IDENT |
| `PRINT` | `print` | Must appear before IDENT |
| `TRUE` | `true` | Must appear before IDENT |
| `FALSE` | `false` | Must appear before IDENT |
| `AND` | `and` | Must appear before IDENT; used by the Parser's `and_expr` |
| `OR` | `or` | Must appear before IDENT; used by the Parser's `or_expr` |
| `NOT` | `not` | Must appear before IDENT; used by the Parser's `not_expr` |
| `FUN` | `fun` | Must appear before IDENT; used by function definitions |
| `IDENT` | `foo`, `my_var`, `x1` | Letter or underscore, then letters/digits/underscores |
| `LE` | `<=` | Must appear before LT |
| `GE` | `>=` | Must appear before GT |
| `EQEQ` | `==` | Must appear before EQ |
| `NEQ` | `!=` | Must appear before BANG |
| `BANG` | `!` | Logical negation; must appear after NEQ |
| `ARROW` | `->` | Return-type annotation; must appear before MINUS |
| `EQ` | `=` | Assignment |
| `LT` | `<` | |
| `GT` | `>` | |
| `PLUS` | `+` | |
| `MINUS` | `-` | |
| `STAR` | `*` | |
| `SLASH` | `/` | |
| `LPAREN` | `(` | |
| `RPAREN` | `)` | |
| `LBRACE` | `{` | |
| `RBRACE` | `}` | |
| `SEMICOLON` | `;` | |
| `COLON` | `:` | Type annotations, e.g. `let x: Num = 42;` |
| `COMMA` | `,` | Parameter and argument lists |

**Maximal-munch test cases you must pass:** `iffy` -> `IDENT("iffy")` (not `IF` + `IDENT("fy")`); `<=` -> `LE` (not `LT` + `EQ`); `==` -> `EQEQ` (not two `EQ`s); `whiles` -> `IDENT("whiles")`; `notable` -> `IDENT("notable")` (not `NOT` + `IDENT("able")`); `->` -> `ARROW` (not `MINUS` + `GT`); `!=` -> `NEQ` (not `BANG` + `EQ`).  Once Step 1c's `tokenize` works, run each of the seven through `scratch.py`.  If any one of them splits, the fix is the order of two rules in `TOKEN_SPEC`, never the loop.

### Step 1b: Token Dataclass

**You write:** `lexer.py` - the `Token` dataclass, at the top of the file.
**You run:** nothing yet; Step 1c prints your first tokens.

A `Token` is one labeled piece of source text together with where it came from.  Define it at the top of `lexer.py` as a dataclass (or namedtuple) with four fields: `type` (string), `value` (string, the raw lexeme), `line` (int), and `col` (int).  The EOF (end-of-file) token has type `"EOF"`, value `""`, and the line and column just past the last character consumed (where the next character would have been), so `"let x = 42;"` ends with EOF at col 12.  Step 2c adds one more field for the decoded value of a string literal.

```python
from dataclasses import dataclass

@dataclass
class Token:
    type: str     # e.g. "IDENT"
    value: str    # the raw lexeme, e.g. "foo"
    line: int     # 1-indexed line of the first character
    col: int      # 1-indexed column of the first character
    # TODO (Step 2c): add a field for the decoded value of a STRING token
```

### Step 1c: Baseline Tokenize Generator

**You write:** `lexer.py` - `LexError`, `COMPILED_SPEC`, and the `tokenize` generator, below `TOKEN_SPEC`.
**You run:** `python3 scratch.py`, with `scratch.py` printing every token of `tokenize("let x = 42;")`.

> **Do this.**
> 1. Below `TOKEN_SPEC` in `lexer.py`, add the `LexError` class, `COMPILED_SPEC`, and the `tokenize(source: str) -> Iterator[Token]` generator from the skeleton below.  At the current position it tries the `TOKEN_SPEC` rules with `.match`, skips WHITESPACE and COMMENT tokens, and advances the position by the match length.
> 2. Write the body of each numbered step.  Skipping, yielding, and the line and column bookkeeping are the whole job.  Each pattern is compiled once, up front, because a compiled pattern's `.match(source, pos)` starts matching at `pos` without copying the string.
> 3. Verify it against the provided test programs before you wrap it in a class.

```python
import re
from typing import Iterator

class LexError(Exception):
    """A lexical error.  Part 3 adds line, col, and the offending text.  An empty body is enough for now."""

# COMPILED_SPEC: one (name, compiled pattern) pair per TOKEN_SPEC rule, in the same order.

def tokenize(source: str) -> Iterator[Token]:
    """Yield one Token per lexeme in source, skipping WHITESPACE and COMMENT, then one EOF token."""
    # Step 1: start at position 0, on line 1, in column 1.
    # Step 2: repeat while the position is still inside source.
    # Step 3:   try each (name, compiled pattern) pair in COMPILED_SPEC, in order, at the current position.
    # Step 4:   on the FIRST rule that matches, take its text.  Unless the rule is WHITESPACE or
    #           COMMENT, yield a Token built from the rule name, the text, and the current line and col.
    # Step 5:   move the position past the match, update line and col, and stop trying rules.
    # Step 6:   if no rule matched, raise LexError naming the unexpected character.  (Part 3 adds line and col.)
    # Step 7: after the loop, yield the EOF token at the current line and col.
    ...
```

Steps 4 and 5 are the main loop's work, and each takes a line or two.  The table covers the steps that need the most thought:

| Step | How to think about it |
|---|---|
| Step 3 and Step 6 | You need to know, after trying every rule, whether any of them matched.  A flag variable works.  So does Python's `for` ... `else`: the `else` block runs only when the loop finishes without a `break`. |
| Step 4, skip | A membership test against the two skipped names decides whether to yield.  Skipped text still moves the position, line, and column forward, so Step 5 runs for every match. |
| Step 4, yield | Yield *before* you advance.  At that moment `line` and `col` still describe where this token starts. |
| Step 5, advance | The match object already knows where the next token begins (the `m.end()` you met in Before You Code).  Then look at the newlines in the matched text.  `str.count("\n")` tells you how many lines to add.  With no newline, the column grows by the length of the text.  With one or more, the column is the number of characters after the *last* newline, plus one, and `str.rfind("\n")` tells you where that last newline sits. |

*The column rule, worked once.*  Suppose `text` is the whitespace `"\n  "`: a newline, then two spaces, three characters in all.  `text.rfind("\n")` is 0.  Two characters follow it, so the next token sits in column 3 of the new line, after the two spaces in columns 1 and 2.

> **You should see.** For the source `"let x = 42;"`, one token per line.  `@dataclass` writes the `Token(type=..., ...)` format for you:
>
> ```text
> Token(type='LET', value='let', line=1, col=1)
> Token(type='IDENT', value='x', line=1, col=5)
> Token(type='EQ', value='=', line=1, col=7)
> Token(type='INT', value='42', line=1, col=9)
> Token(type='SEMICOLON', value=';', line=1, col=11)
> Token(type='EOF', value='', line=1, col=12)
> ```
>
> After Step 2c adds the decoded-value field, each line also ends with that field, for example `decoded=None)`.

> **If it fails.**
> - The loop never ends: the position does not move.  Check that Step 5 runs for skipped tokens too, not only inside the branch that yields.
> - `LET` reports `col=4` instead of `col=1`: you advanced `col` before you yielded, so each token reports where the *next* one starts.  Yield first, then advance.
> - `x` on the second line of `"let\nx"` reports `col=5` instead of `col=1`: the newline branch kept adding to the old column.  After a newline, compute `col` fresh with the column rule above.

### Step 1d: Lexing Theory Questions (in your readme)

**You write (in `readme.md` under a `Lexing Theory` heading):** three short answers.  No code.

Answer three written questions from the Tokens and Scanning session.  They are graded within Part 1's rubric row.

1.  **Maximal munch, precisely.**  Your spec tokenizes `<==` as `LE` then `EQ`, not `LT` then `EQEQ`, and not three single-character tokens.  State the two rules (longest match, then rule order) that force this outcome.  Then give one input where the two rules would *disagree* about the result if you applied them in the other priority.
2.  **Why keywords aren't the lexer's problem twice.**  `iffy` must lex as one `IDENT`, never `IF` + `IDENT("fy")`.  Explain the two different mechanisms that can enforce this: rule ordering with boundary-aware patterns, versus lexing as an identifier and then reclassifying against a keyword table.  Name one cost of each.
3.  **The division of labor.**  `let 42 = x;` lexes without a single error.  In one sentence per stage, state why the lexer *must* accept it and which later pipeline stage rejects it.  Then say what this tells you about what a token stream does and does not promise.

> **Paste into your submission.** Put all three answers in `readme.md` under a heading named `Lexing Theory`, so I can find them next to your interface notes.

---

## Part 2: Lexer Class Implementation

> **Why this matters.** The parser will use exactly three methods, and it will assume they behave exactly as the table below says.  This is the interface contract: the promise your component makes to code you have not written yet.  If `peek` quietly consumes a token, the parser's lookahead logic breaks in ways that show up three assignments from now.  At end of input, both `peek` and `advance` return the EOF token repeatedly; they never raise `StopIteration` or return `None`.

| Method | Behavior |
|--------|----------|
| `peek() -> Token` | Return the next token *without consuming it*. Idempotent: calling it ten times in a row must return the same token. |
| `advance() -> Token` | Consume and return the next token. After calling advance, the next peek/advance returns the token after the one just returned. |
| `expect(token_type: str) -> Token` | If the next token matches `token_type`, consume and return it. Otherwise raise `LexError` with the expected type, found type, and position. |

```python
class Lexer:
    def __init__(self, source: str, config_path: str = None): ...
    def _fill(self) -> None: ...
    def peek(self) -> Token: ...
    def advance(self) -> Token: ...
    def expect(self, token_type: str) -> Token: ...
```

### Step 2a: Implement the Lexer Class

**You write:** `lexer.py` - the `Lexer` class, below `tokenize`.
**You run:** `python3 scratch.py`, with the probe from item 2 below.

The class holds two things: the generator from Step 1c, and a one-token *buffer*.  The buffer is the lookahead.  `peek` looks at it, `advance` hands it over and empties it, and an empty buffer is refilled by asking the generator for its next token.  Here is the algorithm for each method.  The attribute names `_tokens` and `_buffer` are suggestions.

**`__init__(source, config_path=None)`**
1. Call `tokenize(source)` and keep the generator it returns in `_tokens`.  Nothing is lexed yet; the generator waits until it is asked.
2. Set `_buffer` to `None`, which means "empty."
3. Ignore `config_path` for now.  Step 2d uses it.

**`_fill()`**
1. If the buffer is empty, ask the generator for one token and store it in the buffer.
2. If the buffer already holds a token, do nothing.  This is what makes `peek` idempotent.

**`peek()`**
1. Fill the buffer.
2. Return the token in the buffer.  Leave the buffer alone.

**`advance()`**
1. Fill the buffer.
2. Remember the token in the buffer.
3. Empty the buffer, *unless* that token is EOF.
4. Return the token you remembered.

The EOF exception in step 3 is the edge case to get right.  The generator yields EOF last and then stops.  If you emptied the buffer after EOF, the next `_fill` would ask a finished generator for a token, and Python would raise `StopIteration`.  Keeping EOF in the buffer for good means every later call returns EOF again.

**`expect(token_type)`**
1. Peek at the next token.
2. If its type equals `token_type`, advance and return that token.
3. Otherwise raise `LexError` with a message that names the expected type, the found type, and the found token's line and column.

> **Do this.**
> 1. Add the class to `lexer.py`, below `tokenize`, and implement `__init__`, `_fill`, `peek`, `advance`, and `expect` in that order, following the algorithms above.  `expect` is two short steps once the other three work.
> 2. Replace the body of `scratch.py` with this probe and run `python3 scratch.py`:
>
> ```python
> from lexer import Lexer
> lx = Lexer("let x = 42;")
> print(lx.peek())
> print(lx.peek())      # same token again: peek is idempotent
> print(lx.advance())   # same token a third time, now consumed
> print(lx.expect("IDENT"))
> for _ in range(4):
>     print(lx.advance())   # EQ, INT, SEMICOLON, then EOF
> print(lx.advance())       # EOF again, never StopIteration
> ```

> **You should see.** The `LET` token printed three times, then `IDENT`, `EQ`, `INT`, `SEMICOLON`, and two `EOF` tokens in a row:
>
> ```text
> Token(type='LET', value='let', line=1, col=1)
> Token(type='LET', value='let', line=1, col=1)
> Token(type='LET', value='let', line=1, col=1)
> Token(type='IDENT', value='x', line=1, col=5)
> Token(type='EQ', value='=', line=1, col=7)
> Token(type='INT', value='42', line=1, col=9)
> Token(type='SEMICOLON', value=';', line=1, col=11)
> Token(type='EOF', value='', line=1, col=12)
> Token(type='EOF', value='', line=1, col=12)
> ```

> **If it fails.**
> - The second line is `IDENT`: your `peek` is consuming input.  `peek` must never set the buffer back to `None`.
> - `StopIteration` on the last line: `advance` cleared the buffer after handing out EOF, so `_fill` called `next` on a finished generator.  Keep EOF in the buffer.
> - `AttributeError: 'NoneType' object has no attribute 'type'`: `peek` or `advance` returned the buffer before calling `_fill`.

### Step 2b: Verify Two Consumption Patterns

**You write:** `scratch.py` - two lexers over one source, and the two loops below.
**You run:** `python3 scratch.py`

> **Do this.**
> 1. A parser sometimes drives the lexer with `peek` and sometimes with `advance`, so show that both produce identical token streams: in `scratch.py`, build `lexer_a` and `lexer_b` over the same source string, paste the two loops below under them, and run `python3 scratch.py`.

```python
from lexer import Lexer

source = "let total = x1 <= 42; # done\nprint total;"
lexer_a = Lexer(source)                    # two separate lexers: each has its own buffer
lexer_b = Lexer(source)

tokens_a = []                              # Pattern A: peek-driven
while lexer_a.peek().type != "EOF":
    tokens_a.append(lexer_a.advance())

tokens_b = []                              # Pattern B: advance-driven
tok = lexer_b.advance()
while tok.type != "EOF":
    tokens_b.append(tok)
    tok = lexer_b.advance()

assert tokens_a == tokens_b, "Consumption patterns disagree!"
```

The `==` in the `assert` compares two lists of `Token` objects field by field.  It works only because `@dataclass` wrote `__eq__` for you.  A plain class would compare object identity, and the assertion would fail even when every field matched.

> **You should see.** No output at all; a silent run means the assertion passed.  If you see `AssertionError: Consumption patterns disagree!`, print both lists and find the first index where they differ.  The culprit is almost always `advance` failing to clear the buffer, or `peek` clearing it.

### Before Step 2c: Groups and Group References, a Walkthrough

Step 2c asks you to do two things with one string literal: match the whole lexeme (quotes and all) as a single token, and then take its body apart to decode the escapes.  Python's `re` library does both with *capture groups*: parentheses `(...)` remember the text they matched, `m.group(n)` reads that text back, and a group reference such as `\1` in `re.sub` puts it back into a replacement.  This walkthrough shows each technique on a toy language whose strings use single quotes and three escapes of their own (`\'`, `\\`, and `\s` for a space), so you see every move without being handed the double-quoted, four-escape version Step 2c asks for.

> **Do this.**
> 1. Create `groups_lexer_demo.py` in `cs374-lexer` and paste the code below into it.
> 2. Run `python3 groups_lexer_demo.py`.  This file is practice, like `scratch.py`, and is not a deliverable.

```python
import re

# A toy language with SINGLE-quoted strings and three escapes: \'  \\  \s (a space).
# Your lexer's STRING is double-quoted with four escapes; the techniques carry over unchanged.
source = r"say 'it\'s' then 'a\sb' then 'c:\\new'"

# 1. Numbering: group(0) is the whole lexeme, group(1) is the first ( from the left.
TOY_STRING = re.compile(r"'((?:[^'\\]|\\.)*)'")
m = TOY_STRING.search(source)
print("1. group(0):", m.group(0), "| group(1):", m.group(1), "| span(0):", m.span(0), "| span(1):", m.span(1))

# 2. Alternation inside a group.  A lookahead after an ungrouped | guards only the LAST branch.
print("2. ungrouped on 'iffy':", re.match(r"if|else|while(?!\w)", "iffy").group(0), "(matched the front of iffy)")
print("   grouped on 'iffy':  ", re.match(r"(?:if|else|while)(?!\w)", "iffy"))
print("   grouped on 'if (':  ", re.match(r"(?:if|else|while)(?!\w)", "if (").group(0))

# 3. Non-capturing groups.  Make the inner group capturing and watch the numbering shift:
#    a repeated group keeps only its LAST repetition.
m = re.search(r"'(([^'\\]|\\.)*)'", source)
print("3. groups() with a capturing inner group:", m.groups())
m = TOY_STRING.search(source)
print("   groups() with (?:...) inside:         ", m.groups())

# 4. Group references in re.sub, then a FUNCTION replacement.
print("4. reference: ", re.sub(r"\\(.)", r"<\1>", r"it\'s a\sb"))
def shout(m):
    # re.sub calls this once per match and inserts whatever string it returns.
    return m.group(1).upper()
print("   function:  ", re.sub(r"\\(.)", shout, r"it\'s a\sb"))
for m in TOY_STRING.finditer(source):
    # One left-to-right pass: each backslash pairs with exactly ONE following character.
    shouted = re.sub(r"\\(.)", shout, m.group(1))
    print(f"   raw {m.group(0):12} body {m.group(1):10} shouted |{shouted}|")
bad = r"c:\\new".replace("\\\\", "\\").replace("\\n", "\n")
print("   two str.replace calls instead:", repr(bad), "<- the \\\\ became \\, and then that \\n became a newline")

# 5. Named groups and lastgroup: every rule in ONE pattern, and the match names its own rule.
SPEC = [("STR", r"'(?:[^'\\]|\\.)*'"), ("IDENT", r"[A-Za-z_]\w*"), ("WS", r"\s+")]
MASTER = re.compile("|".join(f"(?P<{name}>{pattern})" for name, pattern in SPEC))
for pos in (0, 3, 4):
    m = MASTER.match(source, pos)       # try every rule, in order, at one position
    print(f"5. at {pos}: {m.lastgroup:5} |{m.group()}| ends at {m.end()}")
```

> **You should see.** 15 lines, numbered by section.  The shouted column in section 4, and each lexeme in section 5, is wrapped in `|...|` so you can see exactly where it starts and ends.

```text
1. group(0): 'it\'s' | group(1): it\'s | span(0): (4, 11) | span(1): (5, 10)
2. ungrouped on 'iffy': if (matched the front of iffy)
   grouped on 'iffy':   None
   grouped on 'if (':   if
3. groups() with a capturing inner group: ("it\\'s", 's')
   groups() with (?:...) inside:          ("it\\'s",)
4. reference:  it<'>s a<s>b
   function:   it's aSb
   raw 'it\'s'      body it\'s      shouted |it's|
   raw 'a\sb'       body a\sb       shouted |aSb|
   raw 'c:\\new'    body c:\\new    shouted |c:\new|
   two str.replace calls instead: 'c:\new' <- the \\ became \, and then that \n became a newline
5. at 0: IDENT |say| ends at 3
5. at 3: WS    | | ends at 4
5. at 4: STR   |'it\'s'| ends at 11
```

**Reading the code.**

- **Section 1, numbering.**  Groups are numbered by the position of their *opening* parenthesis, counting from the left and starting at 1.  Group 0 is always the whole match, so for a string literal `group(0)` is the raw lexeme (the `value` field of your `Token`) and `group(1)` is the body between the quotes, the part you decode.  The two spans differ by one character at each end: the quotes.
- **Section 2, alternation.**  `|` has the lowest precedence of any operator, so `if|else|while(?!\w)` means "`if`, *or* `else`, *or* `while` not followed by a word character."  The boundary check guards only the last branch, and `iffy` splits.  Wrap the alternatives in a group, `(?:if|else|while)(?!\w)`, and the check applies to all of them.  If you ever collapse your keyword rules into one pattern, this is the bug waiting for you.
- **Section 3, non-capturing groups.**  The string body needs parentheses to repeat "an ordinary character *or* a backslash pair" as one unit, but it does not need to remember each repetition.  A capturing inner group adds a group 2 that holds only the *last* repetition (`'s'` here), which is useless and shifts the numbering of anything after it.  `(?:...)` groups without capturing.  That is why the `STRING` rule in Step 2d's JSON is written with `(?:...)`.
- **Section 4, references and function replacements.**  In the replacement string of `re.sub`, `\1` means "whatever group 1 captured in this match," and the replacement must be a raw string, or Python turns `"\1"` into the control character `\x01` before `re` sees it.  A fixed template cannot look an escape up in a table, so `re.sub` also accepts a *function*: it calls the function once per match with the match object and inserts whatever string the function returns.  `shout` only uppercases the character after the backslash, so `\s` became `S`, not a space.  Your decoder needs a function that turns each escape into the character it stands for.  Because `\\(.)` consumes a backslash *and* the one character after it, a single left-to-right pass pairs every backslash correctly.  Two chained `str.replace` calls do not: the first turns `\\` into `\`, and the second then reads that new backslash as the start of `\n`.
- **Section 5, named groups and `lastgroup`.**  `(?P<name>...)` names a group.  Joining every rule as `(?P<NAME>pattern)` with `|` builds one master pattern that tries the rules in order (the same priority your `TOKEN_SPEC` loop gives), and `m.lastgroup` reports which named rule matched.  The demo matches at three fixed positions: position 3 is the space after `say`, so `WS` wins there.  It never moves forward on its own.  A tokenizer built this way still needs the loop you write in Step 1c: start at 0, match, skip whitespace and comments, record the rest, and continue from where the match ended.  This is an optional alternative to Step 1c's loop over `COMPILED_SPEC`, and it is how the tokenizer example in the Python `re` documentation works.  If you adopt it, write any grouping inside a rule as `(?:...)`, so that only the rule names capture.

> **Now try this.**
> 1. Add `'bad\qescape'` to `source`.  Predict what section 4 prints for it before you run it.  The toy language has no `\q` escape.  Your decoder will look each escape up in a table of known ones.  Which behavior do you want for an unknown escape in your own lexer: keep it as written, or raise an error?  If you raise, where does Part 3 want the error reported?
> 2. In section 5, move the `IDENT` rule above `STR` and run again.  Nothing changes.  Why not, and which pair of rules in your own `TOKEN_SPEC` *would* change if you swapped them?

### Step 2c: String Literals with Escapes

Extend the STRING pattern (or handle strings as a special case) to support four escape sequences: `\"` (a double-quote character), `\\` (a backslash), `\n` (newline, ASCII 10), and `\t` (tab, ASCII 9).

**You write:** `lexer.py` - the decoded-value field on `Token`, the new `STRING` rule, a `decode` helper, a `STRING` branch in `tokenize`, and the unterminated-string check.
**You run:** `python3 scratch.py`, with the self-test below.

> **Do this.**
> 1. **The field.**  Add a fifth field to `Token` for the decoded value (the TODO you left in Step 1b).  Only `STRING` tokens set it.  Give it a default of `None`, so every other token is still built with four arguments.  A token stores both the raw lexeme (e.g., `"a\nb"` with a backslash-n) in `value` and the decoded value (with a real newline) in the new field.
> 2. **The rule.**  The `STRING` rule matches a whole double-quoted literal, quotes included, and a backslash together with the one character after it counts as a single unit.  So `\"` does not end the string early, and `"quote\"end"` is one token.
> 3. **The decoder.**  Write `decode(body: str) -> str`.  It takes the raw text between the quotes and returns that text with each of the four escapes replaced by the character it stands for.  It works in one left-to-right pass, so `c:\\new` decodes to a backslash followed by the letter `n`, never to a newline.  The empty body decodes to the empty string.
> 4. **The branch.**  When `tokenize` matches a `STRING`, it sets the new field to `decode` of the body and leaves `value` as the raw lexeme.
> 5. **Unterminated strings.**  An unterminated string reaches end-of-line or end-of-file without a closing `"`.  Raise `LexError` at the *opening* quote's position, with a message that says the string is unterminated, not at the end of input.  Otherwise the loop falls through to the "no rule matched" branch and reports the `"` as an unexpected character: the right position but the wrong message.
>
> Sections 1, 3, and 4 of the walkthrough above show every regex move this step needs.

> **You should see.** This worked example:

```text
source: "hello\nworld"
raw lexeme:    "hello\nworld"   (14 chars including quotes)
decoded value: hello           (with a real newline between)
               world
```

Paste this self-test into `scratch.py`, set `DECODED_FIELD` to the name of your new field, and run `python3 scratch.py`.  Every line prints `ok` once the rule and the decoder are right.

```python
from lexer import tokenize

DECODED_FIELD = "decoded"   # TODO: the name you gave the decoded-value field in Step 2c

STRING_CASES = [
    (r'"no escapes"',    "no escapes"),
    (r'"tab\there"',     "tab\there"),     # a real tab
    (r'"line\nbreak"',   "line\nbreak"),   # a real newline
    (r'"quote\"end"',    'quote"end'),     # the \" did not end the string
    (r'"back\\slash"',   "back\\slash"),   # one real backslash
    (r'"c:\\new"',       "c:\\new"),       # a backslash, then the letter n: NOT a newline
    (r'""',              ""),              # the empty string
]

for lexeme, expected in STRING_CASES:
    tok = next(tokenize(lexeme + " after"))
    got = getattr(tok, DECODED_FIELD, None)
    good = tok.type == "STRING" and tok.value == lexeme and got == expected
    print("ok      " if good else "MISMATCH", f"{lexeme:16} -> {tok.type} raw={tok.value!r} decoded={got!r}")
```

> **If it fails.**
> - `MISMATCH` with type `IDENT` or a raw value that stops early (for example `"quote\"`), or a `LexError` on the escaped quote: the string ended at the escaped quote.  The backslash branch of the body is missing, or it comes *after* a branch that already accepts `\`.
> - The `"c:\\new"` case decodes with a real newline: the decoder handled `\\` and `\n` in two separate passes.  One pass that pairs each backslash with exactly one following character avoids this.
> - `KeyError` inside the decoder: the table is missing one of the four escapes, or the lookup used the whole match (the backslash *and* the letter) instead of the letter alone.
> - `TypeError` about a missing argument when an `INT` or `IDENT` token is built: the new field has no default.
> - `decoded=None` on every line: `DECODED_FIELD` does not match the field name you added to `Token`.

### Step 2d: JSON Configuration

**You write:** `token_spec.json`, `token_spec_alt.json`, and in `lexer.py` a `load_spec` helper, a `spec` parameter on `tokenize`, and the `config_path` branch of `Lexer.__init__`.
**You run:** `python3 scratch.py`, building `Lexer(program, "token_spec_alt.json")`.

Move TOKEN_SPEC to a JSON file with this structure:

```json
{
  "comment_char": "#",
  "tokens": [
    ["COMMENT",    "#[^\n]*"],
    ["WHITESPACE", "[ \t\n]+"],
    ["STRING",     "\"(?:[^\"\\\\]|\\\\.)*\""],
    ...
  ]
}
```

> **Do this.**
> 1. Create `token_spec.json` in `cs374-lexer` and copy every rule from your `TOKEN_SPEC` into it, in the same order.  JSON has its own escaping and no raw strings, so a regex backslash becomes two characters in the file: the pattern `\.` is written `"\\."`, and a regex backslash that must itself be escaped becomes `\\\\`.  The `STRING` line above shows the doubled form.
> 2. Write `load_spec(path: str) -> list`.  It reads the JSON file at `path` and returns a list of `(name, compiled pattern)` pairs, one per entry in `"tokens"`, in file order.  If a pattern does not compile, it raises a `LexError` that names the rule or the pattern, never a bare `re.error`.
> 3. Give `tokenize` a second parameter, `spec`, that defaults to `COMPILED_SPEC`, and have it try the rules in `spec` instead of always reading the global.  Every call you already wrote still works unchanged.
> 4. In `Lexer.__init__`, when `config_path` is given, lex with the rules from `load_spec(config_path)`.  Without it, use `COMPILED_SPEC`.
> 5. Create `token_spec_alt.json`: the same rules with `//` as the comment marker and `:=` as the assignment operator.
> 6. In `scratch.py`, build `Lexer(program, "token_spec_alt.json")` on a short program written in that dialect and print its tokens.

A JSON file has no rule order of its own beyond the order you write the lines in, and that order is still the priority.  In the alternate dialect this matters in one place, so follow this rule: `:=` starts with `:`, so list the `EQ` rule (now `:=`) *above* `COLON` in `token_spec_alt.json`.  If `COLON` comes first, `:=` lexes as `COLON` followed by an `=` that no rule matches anymore.

For example, this program in the alternate dialect:

```python
from lexer import Lexer

lx = Lexer("let n := 10; // start\nprint n;", "token_spec_alt.json")
tok = lx.advance()
while True:
    print(tok.type, repr(tok.value), tok.line, tok.col)
    if tok.type == "EOF":
        break
    tok = lx.advance()
```

> **You should see.** The dialect program tokenizes with `EQ` tokens whose value is `:=`, and any `// ...` text disappears as a comment:
>
> ```text
> LET 'let' 1 1
> IDENT 'n' 1 5
> EQ ':=' 1 7
> INT '10' 1 10
> SEMICOLON ';' 1 12
> PRINT 'print' 2 1
> IDENT 'n' 2 7
> SEMICOLON ';' 2 8
> EOF '' 2 9
> ```
>
> Then change a pattern to something invalid such as `"("` and confirm the constructor raises a `LexError` naming that pattern, not a bare `re.error`.  The wording of the message is yours; it must name the rule or the pattern.

> **If it fails.**
> - `COLON` then `LexError` at `=`: `EQ` (now `:=`) sits below `COLON` in `token_spec_alt.json`.  Move it up.
> - `json.decoder.JSONDecodeError: Invalid \escape`: a regex backslash was written once.  In JSON, `\.` must be `"\\."`.
> - The `//` comment comes out as two `SLASH` tokens: the `COMMENT` rule still reads `#[^\n]*`, or it sits below `SLASH`.

---

## Part 3: Error Handling, Positions, and Test Suite

### Step 3a: Precise Error Positions

**You write:** `lexer.py` - a `LexError` constructor that stores `line`, `col`, and `text`, and the `TODO (Part 3)` in `tokenize`.
**You run:** `python3 scratch.py`, on the three-line program below.

An exception is an ordinary class, so it can carry data the way `Token` does.  Store the three facts as attributes, then build the message from them.  Tests read the attributes, and people read the message.

> **Do this.**
> 1. Every `LexError` must include the line number (1-indexed) and column number (1-indexed) of the offending character, and the offending text itself (the unrecognized character or the unterminated string lexeme).
> 2. Give `LexError` the constructor `__init__(self, message: str, line: int = 0, col: int = 0, text: str = "")`.  It stores `line`, `col`, and `text` as attributes of the same names.  Tests in Step 3c assert on the attributes, not on the string.
> 3. `str(e)` (and so `print(e)`) must read `LexError at line L, col C: message`, with the stored line and column in place of `L` and `C`.  The defaults let Step 2d's bad-pattern error, which has no position, use the same class.
> 4. Fill in the `TODO (Part 3)` you left in `tokenize`, so the "no rule matched" branch passes the current line, the current column, and the offending character.  The unterminated-string error from Step 2c passes the opening quote's position the same way.
> 5. In `scratch.py`, tokenize a three-line program with `@` on line 3 and confirm the message names line 3 and the right column.

```python
from lexer import tokenize, LexError

program = "let a = 1;\nlet b = 2;\nlet c @ 3;"
try:
    list(tokenize(program))
except LexError as e:
    print(e)
    print(e.line, e.col, repr(e.text))
```

> **You should see.**
>
> ```text
> LexError at line 3, col 7: unexpected character '@'
> 3 7 '@'
> ```

> **If it fails.**
> - `line 1` on the third line: `line` never grew.  Whitespace is where newlines live, so the newline counting from Step 1c must run for skipped tokens too.
> - `AttributeError: 'LexError' object has no attribute 'line'`: the constructor passed the message to `Exception` but never stored the line on the object.

### Step 3b: Two Error Modes

Implement two modes, chosen at construction time.  With `error_mode="fail_fast"` (the default), raise `LexError` on the first unrecognized character.  With `error_mode="collect_all"`, skip each unrecognized character and record its error, finish tokenizing, then raise a single `LexErrorList` that holds all the errors, so the programmer sees every mistake in one pass instead of fixing them one at a time.

**You write:** `lexer.py` - a `LexErrorList` class, an `error_mode` parameter on `tokenize` and `Lexer`, and the `collect_all` branch.
**You run:** `python3 scratch.py`, on `let @ = $;` in `collect_all` mode.

> **Do this.**
> 1. Add an `error_mode` keyword argument, defaulting to `"fail_fast"`, to both `tokenize` and `Lexer.__init__`.  `Lexer` passes its value through to `tokenize`.
> 2. Define `LexErrorList(errors: list)`, an exception that keeps the list of `LexError` objects in an `errors` attribute.  Its message is a short summary such as `2 lexical errors`.
> 3. In `fail_fast` mode, nothing changes from Step 3a.
> 4. In `collect_all` mode, each unrecognized character produces one `LexError` with its own line and column, and is then skipped.  Lexing resumes at the very next character, and later columns stay correct.
> 5. Every good token still comes out, in order.  The `LexErrorList` is raised at the point where the EOF token would have been yielded, and only if at least one error was recorded.  A clean source in `collect_all` mode ends with EOF as usual.

Try it with this probe in `scratch.py`:

```python
from lexer import Lexer, LexErrorList

lx = Lexer("let @ = $;", error_mode="collect_all")
try:
    while lx.peek().type != "EOF":
        print(lx.advance().type)
except LexErrorList as el:
    print(len(el.errors), "errors")
    for e in el.errors:
        print(" ", e)
```

> **You should see.** With `error_mode="collect_all"`, the source `let @ = $;` produces a `LexErrorList` holding two errors (col 5 and col 9), and the tokens between them (`EQ`, `SEMICOLON`) still come out:
>
> ```text
> LET
> EQ
> SEMICOLON
> 2 errors
>   LexError at line 1, col 5: unexpected character '@'
>   LexError at line 1, col 9: unexpected character '$'
> ```

> **If it fails.**
> - The run hangs: the `collect_all` branch appended the error but never moved `pos` past the bad character.
> - Only one error, at col 5: the branch still raised instead of appending.  Check that `error_mode` reaches `tokenize` from `Lexer.__init__`.
> - The second error says col 8: `col` was not advanced along with `pos` when you skipped the `@`.

### Step 3c: Test Suite

Build `test_lexer.py` with at least the test cases below.  Each test must assert the token types in order and, for selected tokens, the value, line, and col.

**You write:** `test_lexer.py` - one test method per case below, grouped into test classes.
**You run:** `python3 test_lexer.py`, then `python3 test_lexer.py > test_output.txt 2>&1` once everything passes.

- **Token type coverage (one test per type in the Step 1a table):** every token type in the table, as the rubric requires.  That is the literals INT, FLOAT, STRING (with escape), and IDENT; every keyword: IF, ELSE, WHILE, LET, PRINT, TRUE, FALSE, AND, OR, NOT, FUN; and every operator and punctuation token: PLUS, MINUS, STAR, SLASH, EQ, EQEQ, NEQ, BANG, ARROW, LT, LE, GT, GE, LPAREN, RPAREN, LBRACE, RBRACE, SEMICOLON, COLON, COMMA.  For the two skipped types, COMMENT and WHITESPACE, assert that they produce no token (for example, `x # note` lexes to just IDENT, and the newline in `x\ny` advances `line` on the second IDENT).
- **Maximal-munch cases:** `iffy` -> single IDENT, not IF + IDENT; `whiles` -> single IDENT; `<=` -> LE, not LT + EQ; `==` -> EQEQ, not EQ + EQ; `!=` -> NEQ, not two tokens.
- **String escape cases:** `"no escapes"` -> value equals `no escapes`; `"tab\there"` -> value contains a real tab; `"line\nbreak"` -> value contains a real newline; `"quote\"end"` -> value contains a double-quote.
- **Deliberate error programs (five required):**
  1. A program with `@`: expect `LexError at line 1, col ...`
  2. An unterminated string `"hello`: expect `LexError` at the opening quote
  3. A program with `$` in the middle: check position is mid-program, not line 1
  4. A collect-all run with two errors: verify both are reported
  5. A program with a valid token immediately after an error: verify recovery in collect-all mode

> **Do this.**
> 1. Create `test_lexer.py` in `cs374-lexer`, starting from the frame below.  It uses `unittest` from the standard library, so there is nothing to install.  The `types` helper and the one example test are given; every other test is yours.
> 2. Add one test method per case above, grouped into test classes (for example `TestTokenTypes`, `TestMaximalMunch`, `TestStringEscapes`, and `TestErrors`), and name each method after the case it covers (`test_munch_iffy`, `test_escape_tab`) so a failure tells you what broke.
> 3. Run `python3 test_lexer.py`.  When everything passes, save the output for your submission with `python3 test_lexer.py > test_output.txt 2>&1` (`unittest` writes its report to standard error, so you must redirect both streams).

```python
import unittest
from lexer import Lexer, LexError, LexErrorList

def types(source: str, **kwargs) -> list:   # token types for source, excluding EOF
    lx = Lexer(source, **kwargs)
    out = []
    while lx.peek().type != "EOF":
        out.append(lx.advance().type)
    return out

class TestTokenTypes(unittest.TestCase):
    def test_int(self):
        self.assertEqual(types("42"), ["INT"])

if __name__ == "__main__":
    unittest.main(verbosity=2)
```

The error tests check *where* an error happened, so assert on the exception's `line` and `col` attributes, not on its message; `unittest`'s `assertRaises` documentation shows how to get the raised exception back.

Write the `r` before a test's source string whenever it contains a backslash.  Without it, Python turns `"\t"` into a real tab before your lexer ever sees the backslash.

> **You should see.** One line per test ending in `ok`, then a summary like the one below.  The number of tests is yours; the last word must be `OK`.

```text
----------------------------------------------------------------------
Ran 47 tests in 0.012s

OK
```

> **If it fails.**
> - A test in `TestStringEscapes` fails on `"tab\there"`: you compared against the raw lexeme (which still has a backslash and a `t`) instead of the decoded value.
> - The suite passes when run, but `test_output.txt` is empty: you forgot `2>&1`.

---

## The Generator-Toolchain Direction (Flex or PLY)

### What you build

In this direction, you build the same component with a lexer generator instead of a hand-rolled `re` loop.  The generator handles the maximal-munch machinery for you.  Your job shifts to three things: write the rule specification correctly, wrap the generated scanner behind the interface contract, and prove the same properties with the same tests.  The three parts above map onto this direction as follows.  The course tutorials on [Flex and Bison]({{ site.baseurl }}/Tutorials/FlexAndBison) and on the [PLY lexer and parser]({{ site.baseurl }}/Tutorials/PLYLexerAndParser) cover the tools' own mechanics.

> **What this direction requires.** Part 0 and the Getting Started ramp apply as written, with your rule file in place of `lexer.py`'s `TOKEN_SPEC`.  Part 1 becomes a rule specification, Part 2 becomes a wrapper around the generated scanner, and Part 3 applies unchanged.  You still submit a `test_lexer.py`, a `test_output.txt`, and a readme; the readme also records your toolchain versions and explains the keyword-table idiom.

### Part 1 equivalent: the rule specification

Write a Flex `.l` file (or a PLY `tokens`/`t_*` module) that covers the full token table from Step 1a.  The ordering discipline is the same.  Generators resolve ties by rule order (Flex) or by function definition order and pattern length (PLY), so the same bugs await you if keywords trail `IDENT` or `<` precedes `<=`.  Your specification must handle:

- **Numeric literals**: integers and floats (`[0-9]+\.[0-9]*` and `[0-9]*\.[0-9]+`), with FLOAT tried before INT.
- **String literals** in double quotes with `\"`, `\\`, `\n`, `\t` escape sequences, decoded at scan time (in Flex, store the decoded string via `strdup`; in PLY, set `t.value` to the decoded text while keeping the raw lexeme available).
- **Identifiers vs. keywords**: match `[a-zA-Z_][a-zA-Z0-9_]*` and check a keyword table, returning the keyword's own token type for `if`, `else`, `while`, `let`, `print`, `true`, `false`, `and`, `or`, `not`, `fun`.  This is the generator idiom for "keywords before IDENT."  Your readme must explain why the keyword-table approach and the rule-ordering approach are equivalent.
- **Multi-character operators**: `<=`, `>=`, `==`, `!=` as single tokens, listed so they win over their single-character prefixes.
- **Comments and whitespace**: `#` to end of line, skipped; whitespace skipped with newlines counted (`%option yylineno` in Flex; track `t.lexer.lineno` in PLY).

The pass criteria are the same maximal-munch cases from Step 1a: `iffy` -> `IDENT`, `whiles` -> `IDENT`, `<=` -> `LE`, `==` -> `EQEQ`.

### Part 2 equivalent: the component wrapper

The generated scanner hands you a next-token function: `yylex()` in Flex, `lexer.token()` in PLY.  Your deliverable is still a component with the interface contract.  Wrap the generated scanner in a `Lexer` class (PLY) or a small driver module (Flex) that exposes `peek`, `advance`, and `expect` with exactly the behaviors in the table above: an idempotent `peek`, EOF tokens forever at end of input, and a located `LexError` from `expect` on mismatch.  The one-token buffer from the skeleton in Part 2 is the same idea; only the source of the next token changes.  Show the same two consumption patterns from Step 2b agreeing.

In place of Step 2d's JSON configuration, provide a second rule specification that implements the alternate dialect (`//` comments, `:=` assignment), and show the same wrapper driving both.  This meets the configurability requirement using the tools' own configuration medium.

### Part 3 applies unchanged

This direction requires precise line and column positions on every error, the fail-fast and collect-all modes, and the full test suite of Step 3c (token type coverage, maximal-munch cases, string escapes, and the five deliberate error programs), exactly as written.  (In Flex, collect-all means your error rule records the offense and continues scanning rather than exiting.)

### Where the toolchain goes next

Flex is one half of a pair.  Its companion parser generator, Bison (or PLY's `yacc` module), turns a context-free grammar with precedence declarations into an LALR (look-ahead LR) parser.  That half is deliberately out of scope here.  It is the natural continuation of this direction, and the Parser assignment offers a matching generator-toolchain direction where your Flex/PLY scanner feeds a Bison/PLY grammar.  Choosing the generator direction now sets you up well for that one, but the two choices are independent: you choose a direction assignment by assignment.

---

## Deliverables

Submit a ZIP containing the files below, and list your Python version (`python --version`) in the readme so that I can reproduce your results.

| File or artifact | What it shows | Rubric row |
|------------------|---------------|------------|
| `lexer.py` | The Lexer module, importable with no side effects | Token Specification; Lexer Implementation |
| `token_spec.json` | The default token specification, in priority order | Token Specification |
| `token_spec_alt.json` | The alternate dialect specification (`//` comments, `:=` assignment) | Token Specification; Lexer Implementation |
| `test_lexer.py` | The test suite with documented test cases | Error Handling, Positions, and Test Suite |
| `test_output.txt` | The output of running `python test_lexer.py` (all tests passing) | Error Handling, Positions, and Test Suite |
| `readme.md` | Approximately one page documenting the Lexer interface for the parser author (future you), including the TOKEN_SPEC ordering rationale, the two error modes, and the Step 1d answers | Token Specification; Lexer Implementation |
| Part 0 answers (in `readme.md` under a `Part 0` heading) | Your hand-tokenization, the `12foo` and `==` positions, and the three patterns with the overlapping pair | Part 0: Tokens and Scanning |

**Generator-toolchain direction:** the deliverable structure is identical with the vehicle swapped.  Submit the `.l` file (plus a `Makefile` that builds the scanner from scratch) or the PLY lexer module in place of the hand-rolled internals; the default and alternate-dialect rule specifications in place of the two JSON files; the wrapper exposing `peek`/`advance`/`expect`; the same test suite and `test_output.txt`; and a readme that also records your toolchain versions (`flex --version`, or your PLY version) and explains the keyword-table idiom.

---

## Self-Check Before You Submit

- [ ] Every token type in the Step 1a table is in my spec, keywords come before `IDENT`, and every multi-character operator comes before its single-character prefix.
- [ ] All seven maximal-munch cases from Step 1a pass, including `notable` and `->`.
- [ ] `import lexer` in a fresh Python session prints nothing and runs nothing.
- [ ] Calling `peek()` ten times in a row returns the same token, and `advance()` at end of input returns EOF every time without raising.
- [ ] `expect()` on a mismatch raises a `LexError` that names the expected type, the found type, and the position.
- [ ] Every `LexError` carries a 1-indexed line, a 1-indexed column, and the offending text; an unterminated string points at its opening quote.
- [ ] `collect_all` mode reports every error from one pass, and tokens after an error still come out.
- [ ] `test_output.txt` ends in `OK`, and the readme lists my Python version, the ordering rationale, the two error modes, and the Step 1d answers.

---

## Reflection Prompts

- Which scanning rule (maximal munch or priority) caused you a real bug, and how did your tests catch it?
- Which direction did you choose, and what did that choice make easier or harder than you expected?  If you took the generator toolchain: what did Flex or PLY do for you that you would otherwise have written by hand, and what did it hide that you had to recover?
- What about your lexer would you change if your language used significant indentation like Python?
- The `expect` method was designed for the parser's benefit.  Explain why the parser needs `expect` rather than just calling `advance` and checking the type afterward.
