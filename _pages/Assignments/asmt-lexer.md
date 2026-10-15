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
| **Hand-rolled Python** (the core direction) | The `Lexer` yourself, in Python, on top of the `re` module, following Parts 1-3 step by step | Python 3.10 or newer and the standard library | You want the step-by-step scaffolding in Parts 1-3 to match your code line by line.  Most students take this direction. |
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

| `# TODO` | How to write it |
|---|---|
| STRING | `("STRING", r'"[^"\n]*"')` for now: a quote, anything but a quote or newline, a quote.  Step 2c replaces the middle with an escape-aware body. |
| FLOAT before INT | `("FLOAT", r"[0-9]+\.[0-9]+")`, then `("INT", r"[0-9]+")`.  The `\.` is a literal dot; a bare `.` would match any character. |
| keywords | One tuple per keyword, such as `("IF", r"if(?!\w)")`.  `(?!\w)` means "not followed by a letter, digit, or underscore," so `iffy` fails this rule and falls through to `IDENT`. |
| two-character operators | `("LE", r"<=")`, `("GE", r">=")`, `("EQEQ", r"==")`, `("NEQ", r"!=")`, `("ARROW", r"->")`, each placed above the one-character rule it starts with. |
| single characters | Escape the ones that mean something in a regex: `r"\+"`, `r"\*"`, `r"\("`, `r"\)"`, `r"\{"`, `r"\}"`.  `;`, `:`, `,`, `/`, `=`, `<`, `>`, `!`, and `-` need no escape at this position. |

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
> 1. Below `TOKEN_SPEC` in `lexer.py`, add the `LexError` class and the `tokenize(source: str) -> Iterator[Token]` generator below.  At the current position it tries the `TOKEN_SPEC` rules with `re.match`, skips WHITESPACE and COMMENT tokens, and advances the position by the match length.
> 2. Fill in the `# TODO` lines: skipping, yielding, and the line and column bookkeeping are the whole job.  Each pattern is compiled once, up front, because a compiled pattern's `.match(source, pos)` starts matching at `pos` without copying the string.
> 3. Verify it against the provided test programs before you wrap it in a class.

```python
import re
from typing import Iterator

class LexError(Exception):
    """A lexical error.  Part 3 adds line, col, and the offending text."""
    pass

COMPILED_SPEC = [(name, re.compile(pattern)) for name, pattern in TOKEN_SPEC]

def tokenize(source: str) -> Iterator[Token]:
    pos, line, col = 0, 1, 1
    while pos < len(source):
        for name, regex in COMPILED_SPEC:
            m = regex.match(source, pos)
            if m:
                text = m.group()
                # TODO: if name is WHITESPACE or COMMENT, do not yield a token
                # TODO: otherwise yield Token(name, text, line, col)
                # TODO: advance pos by len(text); count "\n" in text to update line, col restarts at 1
                break
        else:
            raise LexError(f"unexpected character {source[pos]!r}")  # TODO (Part 3): add line and col
    yield Token("EOF", "", line, col)
```

The three `# TODO` lines are the main loop's work.  Each takes a line or two:

| `# TODO` | How to write it |
|---|---|
| skip | `if name not in ("WHITESPACE", "COMMENT"):` and put the `yield` inside it.  Skipped text still moves `pos`, `line`, and `col` forward, so the next TODO runs for every match. |
| yield | `yield Token(name, text, line, col)`.  `line` and `col` still describe where this token *starts*, because you have not advanced them yet. |
| advance | `pos = m.end()`.  Then count newlines: `newlines = text.count("\n")`.  With none, `col += len(text)`.  With some, `line += newlines` and `col = len(text) - text.rfind("\n")`, the number of characters after the last newline, plus one. |

*The column formula, worked once.*  Suppose `text` is the whitespace `"\n  "`: a newline, then two spaces, three characters in all.  `text.rfind("\n")` is 0, so `col = 3 - 0 = 3`.  The next token sits in column 3 of the new line, after two spaces in columns 1 and 2.

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
> - The loop never ends: `pos` does not move.  Check that `pos = m.end()` runs for skipped tokens too, not only inside the `if` that yields.
> - `LET` reports `col=4` instead of `col=1`: you advanced `col` before you yielded, so each token reports where the *next* one starts.  Yield first, then advance.
> - `x` on the second line of `"let\nx"` reports `col=5` instead of `col=1`: the newline branch kept adding to the old column.  After a newline, compute `col` fresh with the formula above.

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
    def __init__(self, source: str, config_path: str = None):
        # TODO (Step 2d): if config_path is given, load and validate the JSON spec
        self._tokens = tokenize(source)   # the generator from Step 1c
        self._buffer = None               # holds at most one lookahead token

    def _fill(self) -> None:
        """Pull the next token into the buffer if the buffer is empty."""
        # TODO: if self._buffer is None, take the next token from self._tokens
        # TODO: once the generator is exhausted, keep the EOF token in the buffer for good

    def peek(self) -> Token:
        # TODO: fill the buffer if needed, then return its contents WITHOUT clearing it
        raise NotImplementedError

    def advance(self) -> Token:
        # TODO: fill the buffer if needed, return its contents, and clear the buffer
        #       (an EOF token stays put, so every later call returns EOF again)
        raise NotImplementedError

    def expect(self, token_type: str) -> Token:
        # TODO: if peek().type == token_type, return advance()
        # TODO: otherwise raise LexError naming the expected type, the found type,
        #       and the found token's line and col
        raise NotImplementedError
```

### Step 2a: Implement the Lexer Class

**You write:** `lexer.py` - the `Lexer` class, below `tokenize`.
**You run:** `python3 scratch.py`, with the probe from item 2 below.

The class holds two things: the generator from Step 1c, and a one-token *buffer*.  The buffer is the lookahead.  `peek` looks at it, `advance` hands it over and empties it, and an empty buffer is refilled with `next(self._tokens)`.

| `# TODO` | How to write it |
|---|---|
| `_fill` | `if self._buffer is None: self._buffer = next(self._tokens)`.  That one `if` is the whole method. |
| keep EOF for good | Nothing extra goes in `_fill`.  The rule lives in `advance`: never clear the buffer when it holds the EOF token.  The generator yields EOF last, so an empty buffer after EOF would call `next` on a finished generator and raise `StopIteration`. |
| `peek` | `self._fill()`, then `return self._buffer`.  Do not touch the buffer. |
| `advance` | `self._fill()`, save `tok = self._buffer`, then `if tok.type != "EOF": self._buffer = None`, and `return tok`. |
| `expect` | `tok = self.peek()`.  If `tok.type == token_type`, `return self.advance()`.  Otherwise `raise LexError(...)` with a message that names `token_type`, `tok.type`, `tok.line`, and `tok.col`. |

> **Do this.**
> 1. Add the skeleton above to `lexer.py`, below `tokenize`, and implement `_fill`, `peek`, `advance`, and `expect` in that order.  The buffer holds one token, the lookahead: `peek` fills it when empty and returns its contents without clearing it, `advance` does the same and then clears it, and `expect` is two lines once the other three work.
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

# 4. Group references in re.sub, then a FUNCTION replacement for decoding escapes.
print("4. reference: ", re.sub(r"\\(.)", r"<\1>", r"it\'s a\sb"))
TOY_ESCAPES = {"'": "'", "\\": "\\", "s": " "}
def decode(body):
    # One left-to-right pass: each backslash pairs with exactly ONE following character.
    return re.sub(r"\\(.)", lambda m: TOY_ESCAPES.get(m.group(1), m.group(0)), body)
for m in TOY_STRING.finditer(source):
    print(f"   raw {m.group(0):12} body {m.group(1):10} decoded |{decode(m.group(1))}|")
bad = r"c:\\new".replace("\\\\", "\\").replace("\\n", "\n")
print("   two str.replace calls instead:", repr(bad), "<- the \\\\ became \\, and then that \\n became a newline")

# 5. Named groups and lastgroup: every rule in ONE pattern, and the match names its own rule.
SPEC = [("STR", r"'(?:[^'\\]|\\.)*'"), ("IDENT", r"[A-Za-z_]\w*"), ("WS", r"\s+")]
MASTER = re.compile("|".join(f"(?P<{name}>{pattern})" for name, pattern in SPEC))
pos = 0
while pos < len(source):
    m = MASTER.match(source, pos)
    if m.lastgroup != "WS":
        print(f"5. {m.lastgroup:5} {m.group():12} at {m.start()}")
    pos = m.end()
```

> **You should see.** 17 lines, numbered by section.  The decoded column in section 4 is wrapped in `|...|` so you can see the space that `\s` became.

```text
1. group(0): 'it\'s' | group(1): it\'s | span(0): (4, 11) | span(1): (5, 10)
2. ungrouped on 'iffy': if (matched the front of iffy)
   grouped on 'iffy':   None
   grouped on 'if (':   if
3. groups() with a capturing inner group: ("it\\'s", 's')
   groups() with (?:...) inside:          ("it\\'s",)
4. reference:  it<'>s a<s>b
   raw 'it\'s'      body it\'s      decoded |it's|
   raw 'a\sb'       body a\sb       decoded |a b|
   raw 'c:\\new'    body c:\\new    decoded |c:\new|
   two str.replace calls instead: 'c:\new' <- the \\ became \, and then that \n became a newline
5. IDENT say          at 0
5. STR   'it\'s'      at 4
5. IDENT then         at 12
5. STR   'a\sb'       at 17
5. IDENT then         at 24
5. STR   'c:\\new'    at 29
```

**Reading the code.**

- **Section 1, numbering.**  Groups are numbered by the position of their *opening* parenthesis, counting from the left and starting at 1.  Group 0 is always the whole match, so for a string literal `group(0)` is the raw lexeme (the `value` field of your `Token`) and `group(1)` is the body between the quotes, the part you decode.  The two spans differ by one character at each end: the quotes.
- **Section 2, alternation.**  `|` has the lowest precedence of any operator, so `if|else|while(?!\w)` means "`if`, *or* `else`, *or* `while` not followed by a word character."  The boundary check guards only the last branch, and `iffy` splits.  Wrap the alternatives in a group, `(?:if|else|while)(?!\w)`, and the check applies to all of them.  If you ever collapse your keyword rules into one pattern, this is the bug waiting for you.
- **Section 3, non-capturing groups.**  The string body needs parentheses to repeat "an ordinary character *or* a backslash pair" as one unit, but it does not need to remember each repetition.  A capturing inner group adds a group 2 that holds only the *last* repetition (`'s'` here), which is useless and shifts the numbering of anything after it.  `(?:...)` groups without capturing.  That is why the `STRING` rule in Step 2d's JSON is written with `(?:...)`.
- **Section 4, references and function replacements.**  In the replacement string of `re.sub`, `\1` means "whatever group 1 captured in this match," and the replacement must be a raw string, or Python turns `"\1"` into the control character `\x01` before `re` sees it.  A fixed template cannot look an escape up in a table, so `re.sub` also accepts a *function*: it calls the function once per match with the match object and inserts whatever string the function returns.  Because `\\(.)` consumes a backslash *and* the one character after it, a single left-to-right pass pairs every backslash correctly.  Two chained `str.replace` calls do not: the first turns `\\` into `\`, and the second then reads that new backslash as the start of `\n`.
- **Section 5, named groups and `lastgroup`.**  `(?P<name>...)` names a group.  Joining every rule as `(?P<NAME>pattern)` with `|` builds one master pattern that tries the rules in order (the same priority your `TOKEN_SPEC` loop gives), and `m.lastgroup` reports which named rule matched.  This is an optional alternative to Step 1c's loop over `COMPILED_SPEC`, and it is how the tokenizer example in the Python `re` documentation works.  If you adopt it, write any grouping inside a rule as `(?:...)`, so that only the rule names capture.

> **Now try this.**
> 1. In section 4, change `TOY_ESCAPES.get(m.group(1), m.group(0))` to `TOY_ESCAPES[m.group(1)]` and add `'bad\qescape'` to `source`.  Predict what happens before you run it.  Which behavior do you want for an unknown escape in your own lexer, and where does Part 3 want the error reported?
> 2. In section 5, move the `IDENT` rule above `STR` and run again.  Nothing changes.  Why not, and which pair of rules in your own `TOKEN_SPEC` *would* change if you swapped them?

### Step 2c: String Literals with Escapes

Extend the STRING pattern (or handle strings as a special case) to support four escape sequences: `\"` (a double-quote character), `\\` (a backslash), `\n` (newline, ASCII 10), and `\t` (tab, ASCII 9).

**You write:** `lexer.py` - the decoded-value field on `Token`, the new `STRING` rule, a `decode` helper, a `STRING` branch in `tokenize`, and the unterminated-string check.
**You run:** `python3 scratch.py`, with the self-test below.

> **Do this.**
> 1. Add the decoded-value field to `Token` (the TODO you left in Step 1b).  A token stores both the raw lexeme (e.g., `"a\nb"` with a backslash-n) in `value` and the decoded value (with a real newline) in the new field.
> 2. Make the STRING rule match a backslash followed by any character as one unit, so `\"` does not end the string early.  Sections 1 and 3 of the walkthrough above show the shape.
> 3. After matching, decode the four escapes into the new field with one `re.sub` and a function replacement (section 4 of the walkthrough).  Leave `value` as the raw lexeme.
> 4. An unterminated string reaches end-of-line or end-of-file without a closing `"`.  Check for an opening quote explicitly and raise `LexError` at the *opening* quote's position, not at the end of input.  Otherwise the loop falls through to the "no rule matched" branch and reports the `"` as an unexpected character: the right position but the wrong message.

> **You should see.** This worked example:

```text
source: "hello\nworld"
raw lexeme:    "hello\nworld"   (14 chars including quotes)
decoded value: hello           (with a real newline between)
               world
```

> **Building STRING in three moves.**  Work the string rule on its own with the self-test below before you move on to Step 2d.
> 1. **Shape.**  Start from the toy `TOY_STRING` in the walkthrough: swap the single quotes for double quotes, and keep the body in one capture group so `group(0)` is the raw lexeme and `group(1)` is the body.  (If your `TOKEN_SPEC` loop only ever uses `m.group()`, you can drop the outer capture group and slice the quotes off instead.  Either way, decode only the body.)
> 2. **Body.**  Inside the quotes, repeat "any character that is not `\"` or a backslash, *or* a backslash followed by any one character" as a single non-capturing group, exactly as section 3 does.  The second branch is what keeps `\"` from ending the string early.
> 3. **Decode.**  Write a dictionary with your four escapes and decode the body with one `re.sub` call and a function replacement, as section 4 does.  Do not chain `str.replace` calls: the `"c:\\new"` case below is there to catch that.
>
> Then store the raw lexeme in `value` and the decoded text in your new field.

*Where each piece goes.*  Four small edits to `lexer.py` carry the whole step.  The names here (`decoded`, `ESCAPES`, `decode`) are suggestions; use your own if you prefer.

```python
@dataclass
class Token:
    type: str
    value: str
    line: int
    col: int
    decoded: str | None = None    # only STRING tokens set it

ESCAPES = {}   # TODO: the four escapes, each mapping the letter after "\" to its character

def decode(body: str) -> str:
    # TODO: one re.sub over r"\\(.)" with a function replacement that looks up m.group(1)
    raise NotImplementedError

# Inside tokenize, where a token is about to be yielded:
#     tok = Token(name, text, line, col)
#     if name == "STRING":
#         tok.decoded = decode(m.group(1))   # group 1 is the body between the quotes
#     yield tok

# Inside tokenize, in the "no rule matched" branch, before the LexError for a bad character:
#     if source[pos] == '"':
#         # TODO: raise LexError for an unterminated string at THIS line and col
```

| `# TODO` | How to write it |
|---|---|
| the field | Done above.  The `= None` default matters: every other token is still built with four arguments, `Token(name, text, line, col)`, so the new field must not be required. |
| `ESCAPES` | `{'"': '"', "\\": "\\", "n": "\n", "t": "\t"}`.  Each key is the character after the backslash, and each value is what that escape stands for. |
| `decode` | `return re.sub(r"\\(.)", lambda m: ESCAPES.get(m.group(1), m.group(0)), body)`.  The `.get` default leaves an unknown escape such as `\q` exactly as it was, which the walkthrough's "Now try this" asks you to think about. |
| unterminated | Your `STRING` rule only matches a string that closes, so an unterminated one reaches the "no rule matched" branch with `source[pos]` equal to `"`.  Raise `LexError` there, with the current `line` and `col` (the opening quote's position) and a message that says "unterminated string." |

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
> - The `"c:\\new"` case decodes with a real newline: the decoder handled `\\` and `\n` in two separate passes.  Use one `re.sub` over `\\(.)`.
> - `KeyError` inside the decoder: the dictionary is missing one of the four escapes, or the replacement function looked up `m.group(0)` (the backslash *and* the letter) instead of `m.group(1)` (the letter alone).
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
> 2. In `Lexer.__init__`, when `config_path` is given, open it with `json.load`, compile every pattern inside a `try` block, and turn any `re.error` into a `LexError` that names the offending pattern.
> 3. Create `token_spec_alt.json`: the same rules with `//` as the comment marker and `:=` as the assignment operator.
> 4. In `scratch.py`, build `Lexer(program, "token_spec_alt.json")` on a short program written in that dialect and print its tokens.

*How the JSON reaches `tokenize`.*  Right now `tokenize` always reads the global `COMPILED_SPEC`.  Give it a parameter instead, so `Lexer` can hand it whichever rules it loaded:

```python
def load_spec(path: str) -> list:
    """Read a JSON spec and return a list of (name, compiled pattern) pairs, in file order."""
    # TODO: open the file and json.load it
    # TODO: for each [name, pattern] in data["tokens"], compile the pattern;
    #       turn an re.error into a LexError that names the rule and the pattern
    raise NotImplementedError

def tokenize(source: str, spec: list = COMPILED_SPEC) -> Iterator[Token]:
    # the body from Step 1c, with "for name, regex in COMPILED_SPEC:"
    # changed to                  "for name, regex in spec:"
    ...

# In Lexer.__init__:
#     spec = load_spec(config_path) if config_path else COMPILED_SPEC
#     self._tokens = tokenize(source, spec)
```

| `# TODO` | How to write it |
|---|---|
| load | `with open(path) as f: data = json.load(f)`.  `data["tokens"]` is then a list of two-item lists, such as `["INT", "[0-9]+"]`. |
| compile | Start `spec = []`, loop `for name, pattern in data["tokens"]:`, and inside a `try:` append `(name, re.compile(pattern))`.  Write `except re.error as e:` and `raise LexError(...)` with `name`, `pattern`, and `e` in the message.  Return `spec`. |

A JSON file has no rule order of its own beyond the order you write the lines in, and that order is still the priority.  In the alternate dialect this matters in one place: `:=` starts with `:`, so the `EQ` rule must now sit *above* `COLON`, or `:=` lexes as `COLON` followed by an `EQ` that no longer matches anything.

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

```python
class LexError(Exception):
    def __init__(self, message: str, line: int = 0, col: int = 0, text: str = ""):
        # TODO: call super().__init__ with "LexError at line {line}, col {col}: {message}"
        # TODO: store line, col, and text as attributes on self
        pass
```

| `# TODO` | How to write it |
|---|---|
| message | `super().__init__(f"LexError at line {line}, col {col}: {message}")`.  `print(e)` and `str(e)` then show this text. |
| attributes | `self.line = line`, `self.col = col`, `self.text = text`.  The defaults let Step 2d's bad-pattern error, which has no position, still use the same class. |
| the `tokenize` branch | `raise LexError(f"unexpected character {source[pos]!r}", line, col, source[pos])` |

> **Do this.**
> 1. Every `LexError` must include the line number (1-indexed) and column number (1-indexed) of the offending character, and the offending text itself (the unrecognized character or the unterminated string lexeme).  Give `LexError` three attributes (`line`, `col`, `text`) set in its constructor, and build the message from them.  Tests in Step 3c assert on the attributes, not on the string.
> 2. Fill in the `TODO (Part 3)` you left in `tokenize` so the "no rule matched" branch passes the current `line` and `col`.  Track the line by counting the `\n` characters you consume, and reset the column to 1 after each newline.
> 3. In `scratch.py`, tokenize a three-line program with `@` on line 3 and confirm the message names line 3 and the right column.

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
> - `AttributeError: 'LexError' object has no attribute 'line'`: the constructor called `super().__init__` but never set `self.line`.

### Step 3b: Two Error Modes

Implement two modes, chosen at construction time.  With `error_mode="fail_fast"` (the default), raise `LexError` on the first unrecognized character.  With `error_mode="collect_all"`, skip each unrecognized character and record its error, finish tokenizing, then raise a single `LexErrorList` that holds all the errors, so the programmer sees every mistake in one pass instead of fixing them one at a time.

**You write:** `lexer.py` - a `LexErrorList` class, an `error_mode` parameter on `tokenize` and `Lexer`, and the `collect_all` branch.
**You run:** `python3 scratch.py`, on `let @ = $;` in `collect_all` mode.

> **Do this.**
> 1. Add an `error_mode` keyword argument to `Lexer.__init__` and pass it through to `tokenize`.
> 2. Define `LexErrorList` as an exception that carries a list of `LexError` objects.
> 3. In `collect_all` mode, the "no rule matched" branch appends a `LexError`, advances `pos` and `col` by one, and keeps going.  Raise the `LexErrorList` only after the EOF token would have been produced.

```python
class LexErrorList(Exception):
    def __init__(self, errors: list):
        # TODO: call super().__init__ with a short summary such as "2 lexical errors"
        # TODO: store the list as self.errors
        pass

# In tokenize: start with errors = [] next to pos, line, col.
# In the "no rule matched" branch:
#     err = LexError(...)                  # exactly as in Step 3a
#     if error_mode == "fail_fast":
#         raise err
#     # TODO: collect_all: append err, then step past the bad character
# After the while loop, before yielding EOF:
#     # TODO: if any errors were collected, raise LexErrorList(errors)
```

| `# TODO` | How to write it |
|---|---|
| `LexErrorList` | `super().__init__(f"{len(errors)} lexical errors")`, then `self.errors = errors`. |
| collect and step | `errors.append(err)`, then `pos += 1` and `col += 1`.  Without the step, the loop tries the same bad character forever. |
| raise at the end | `if errors: raise LexErrorList(errors)`.  It goes after the loop, so every good token has already been yielded. |

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
> 1. Create `test_lexer.py` in `cs374-lexer` from the skeleton below.  It uses `unittest` from the standard library, so there is nothing to install.
> 2. Add one test method per case above, named after the case it covers (`test_munch_iffy`, `test_escape_tab`) so a failure tells you what broke.
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
    # TODO: one test per token type in the Step 1a table

# TODO: TestMaximalMunch (iffy, whiles, <=, ==, !=) and TestStringEscapes
#       (four cases; assert on the decoded value, not the raw lexeme)

class TestErrors(unittest.TestCase):
    def test_at_sign(self):
        with self.assertRaises(LexError) as cm:
            types("let x = @;")
        # TODO: assert cm.exception.line == 1 and cm.exception.col == 9
    # TODO: the other four deliberate error programs; the collect-all ones
    #       expect LexErrorList and check len(cm.exception.errors)

if __name__ == "__main__":
    unittest.main(verbosity=2)
```

Every test you need is built from one of these idioms.  Copy the one that fits, then change the source and the expected values:

| You want to check | How to write it |
|---|---|
| the token types, in order | `self.assertEqual(types("a <= b"), ["IDENT", "LE", "IDENT"])` |
| one token's value or position | `tok = Lexer("x\ny").advance()` gives the first token; call `advance()` again for the next.  Then `self.assertEqual((tok.line, tok.col), (2, 1))` |
| a decoded string | `tok = Lexer(r'"tab\there"').advance()`, then `self.assertEqual(tok.decoded, "tab\there")`, with your field name in place of `decoded` |
| an error and where it is | `with self.assertRaises(LexError) as cm:` around the code that should fail, then `self.assertEqual((cm.exception.line, cm.exception.col), (1, 9))` after the `with` block |
| collect-all errors | the same shape with `LexErrorList` and `error_mode="collect_all"`, then `self.assertEqual(len(cm.exception.errors), 2)` |

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
