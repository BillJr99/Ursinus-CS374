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
- Your class tokenizer, or the `finditer` mini lexer you built in the Regex assignment.  This assignment grows one of those into a component, so start from whichever you trust more.
- A terminal and an editor.  If either is new to you, work through the [dev environment page]({{ site.baseurl }}/Tutorials/DevEnvironment) and the [shell primer]({{ site.baseurl }}/Tutorials/ShellForLanguageDev) first.

Confirm your Python version from the terminal.  On some machines the command is `python` rather than `python3`; use whichever one reports 3.10 or newer.

```bash
python3 --version
```

```text
Python 3.11.4
```

Make one folder for the assignment (`mkdir cs374-lexer`, then `cd cs374-lexer`) and create the five deliverable files in it up front so each part has a home: `lexer.py` (the Lexer module), `token_spec.json` and `token_spec_alt.json` (the two specifications from Step 2d), `test_lexer.py` (the test suite), and `readme.md` (interface notes and the Step 1d answers).  Run every command in this assignment from inside that folder.

> **Time budget.** Part 0 takes about twenty minutes on paper.  The first thirty minutes at the keyboard get you a six-rule lexer printing tokens.  Plan the rest across the checkpoints in the pacing table below and budget roughly ten to twelve hours in total; Part 3's test suite takes longer than it looks.

### Your First 30 Minutes

> **Do this.**
> 1. In `lexer.py`, define the `Token` dataclass from Step 1b and a `TOKEN_SPEC` with just six rules: `WHITESPACE`, `LET`, `IDENT`, `EQ`, `INT`, `SEMICOLON`.
> 2. Write the `tokenize` generator from Step 1c under it.
> 3. Create `scratch.py` in the same folder with two lines: `from lexer import tokenize`, then a loop that prints each token of `tokenize("let x = 42;")`.  Keeping the demo out of `lexer.py` is what "no side effects at import time" means.
> 4. Run `python3 scratch.py` from the `cs374-lexer` folder.  You should see six lines, one per token, matching the listing in Step 1c, with line and column numbers.
> 5. Change the source to `"lets x = 42;"` and run again: `lets` must come out as a single `IDENT`.

> **If it fails.**
> - `lets` comes out as `LET` followed by `IDENT("s")`: your keyword pattern is missing its boundary check.  Add a negative lookahead such as `(?!\w)` after the keyword.  Learn that now with six rules, not later with twenty-nine.
> - `ModuleNotFoundError: No module named 'lexer'`: you ran the command from a different folder.  `cd` into `cs374-lexer` and run it again.

### Suggested Pacing

See the course schedule for the assigned and due dates.  Your starting point is the mini lexer you built in the **Regular Expressions** assignment, Part 3, which you submit the day this assignment opens.  Bring that file with you and Part 1 becomes an extension rather than a blank page.  The Finite Automata Simulators lab falls inside this window and builds the state-machine reasoning Part 1 asks for.

| Checkpoint | You should have |
|------------|----------------|
| On assignment | `Token` dataclass and a six-rule `tokenize` generator working (grown from your mini lexer) |
| Checkpoint 1 | Parts 1-2a: full `TOKEN_SPEC` passing all maximal-munch cases, and the core `Lexer` class with `peek`/`advance`/`expect` working |
| Automata lab due | Parts 2b-2c: string escapes and JSON configuration (both dialects) |
| Due date | Part 3 error modes with precise positions and the full test suite complete; readme written; ZIP assembled and submitted |

---

## Part 1: Token Specification

> **Why this matters.** A lexer built on regular expressions applies its rules in order and uses *maximal munch*: at each position, it matches the longest string it can.  Order the rules wrong and you get bugs: if `IDENT` appears before `IF`, then `if` lexes as an identifier named `"if"`; if `LT` (`<`) appears before `LE` (`<=`), then `<=` lexes as `LT` followed by `EQ`.  Keywords go before identifiers, and longer operators before their prefixes.

### Step 1a: Define the TOKEN_SPEC

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

| Token Name | Example Lexemes | Notes |
|------------|----------------|-------|
| `COMMENT` | `# this is a comment` | Match to end of line; to be skipped |
| `WHITESPACE` | ` `, `\t`, `\n` | Skip; track newlines for line counting |
| `STRING` | `"hello"`, `"a\nb"` | Double-quoted; see Part 3 for escapes |
| `FLOAT` | `3.14`, `-0.5` | Must appear before INT |
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

**Maximal-munch test cases you must pass:** `iffy` -> `IDENT("iffy")` (not `IF` + `IDENT("ffy")`); `<=` -> `LE` (not `LT` + `EQ`); `==` -> `EQEQ` (not two `EQ`s); `whiles` -> `IDENT("whiles")`; `notable` -> `IDENT("notable")` (not `NOT` + `IDENT("able")`); `->` -> `ARROW` (not `MINUS` + `GT`); `!=` -> `NEQ` (not `BANG` + `EQ`).  Once Step 1c's `tokenize` works, run each of the seven through `scratch.py`.  If any one of them splits, the fix is the order of two rules in `TOKEN_SPEC`, never the loop.

### Step 1b: Token Dataclass

A `Token` is one labeled piece of source text together with where it came from.  Define it at the top of `lexer.py` as a dataclass (or namedtuple) with four fields: `type` (string), `value` (string, the raw lexeme), `line` (int), and `col` (int).  The EOF token has type `"EOF"`, value `""`, and the line and column of the last character consumed.  Step 2c adds one more field for the decoded value of a string literal.

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

> **You should see.** For the source `"let x = 42;"`, one token per line:

```text
Token(LET,       "let", line=1, col=1)
Token(IDENT,     "x",   line=1, col=5)
Token(EQ,        "=",   line=1, col=7)
Token(INT,       "42",  line=1, col=9)
Token(SEMICOLON, ";",   line=1, col=11)
Token(EOF,       "",    line=1, col=12)
```

### Step 1d: Lexing Theory Questions (in your readme)

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

> **You should see.** The `LET` token printed three times, then `IDENT("x")`, then `EQ`, `INT`, `SEMICOLON`, and two `EOF` tokens in a row.  If the third line is `IDENT`, your `peek` is consuming input.

### Step 2b: Verify Two Consumption Patterns

> **Do this.**
> 1. A parser sometimes drives the lexer with `peek` and sometimes with `advance`, so show that both produce identical token streams: in `scratch.py`, build `lexer_a` and `lexer_b` over the same source string, paste the two loops below under them, and run `python3 scratch.py`.

```python
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

> **You should see.** No output at all; a silent run means the assertion passed.  If you see `AssertionError: Consumption patterns disagree!`, print both lists and find the first index where they differ.  The culprit is almost always `advance` failing to clear the buffer, or `peek` clearing it.

### Step 2c: String Literals with Escapes

Extend the STRING pattern (or handle strings as a special case) to support four escape sequences: `\"` (a double-quote character), `\\` (a backslash), `\n` (newline, ASCII 10), and `\t` (tab, ASCII 9).

> **Do this.**
> 1. Add the decoded-value field to `Token` (the TODO you left in Step 1b).  A token stores both the raw lexeme (e.g., `"a\nb"` with a backslash-n) in `value` and the decoded value (with a real newline) in the new field.
> 2. Make the STRING rule match a backslash followed by any character as one unit, so `\"` does not end the string early.
> 3. After matching, decode the four escapes into the new field.  Leave `value` as the raw lexeme.
> 4. An unterminated string reaches end-of-line or end-of-file without a closing `"`.  Check for an opening quote explicitly and raise `LexError` at the *opening* quote's position, not at the end of input.  Otherwise the loop falls through to the "no rule matched" branch and reports the `"` as an unexpected character: the right position but the wrong message.

> **You should see.** This worked example:

```text
source: "hello\nworld"
raw lexeme:    "hello\nworld"   (14 chars including quotes)
decoded value: hello           (with a real newline between)
               world
```

### Step 2d: JSON Configuration

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

> **You should see.** The dialect program tokenizes with `EQ` tokens whose value is `:=`, and any `// ...` text disappears as a comment.  Change a pattern to something invalid such as `"("` and confirm the constructor raises a `LexError` naming that pattern, not a bare `re.error`.

---

## Part 3: Error Handling, Positions, and Test Suite

### Step 3a: Precise Error Positions

> **Do this.**
> 1. Every `LexError` must include the line number (1-indexed) and column number (1-indexed) of the offending character, and the offending text itself (the unrecognized character or the unterminated string lexeme).  Give `LexError` three attributes (`line`, `col`, `text`) set in its constructor, and build the message from them.  Tests in Step 3c assert on the attributes, not on the string.
> 2. Fill in the `TODO (Part 3)` you left in `tokenize` so the "no rule matched" branch passes the current `line` and `col`.  Track the line by counting the `\n` characters you consume, and reset the column to 1 after each newline.
> 3. In `scratch.py`, tokenize a three-line program with `@` on line 3 and confirm the message names line 3 and the right column.

> **You should see.** `LexError at line 3, col 7: unexpected character '@'`

### Step 3b: Two Error Modes

Implement two modes, chosen at construction time.  With `error_mode="fail_fast"` (the default), raise `LexError` on the first unrecognized character.  With `error_mode="collect_all"`, skip each unrecognized character and record its error, finish tokenizing, then raise a single `LexErrorList` that holds all the errors, so the programmer sees every mistake in one pass instead of fixing them one at a time.

> **Do this.**
> 1. Add an `error_mode` keyword argument to `Lexer.__init__` and pass it through to `tokenize`.
> 2. Define `LexErrorList` as an exception that carries a list of `LexError` objects.
> 3. In `collect_all` mode, the "no rule matched" branch appends a `LexError`, advances `pos` and `col` by one, and keeps going.  Raise the `LexErrorList` only after the EOF token would have been produced.

> **You should see.** With `error_mode="collect_all"`, the source `let @ = $;` produces a `LexErrorList` holding two errors (col 5 and col 9), and the tokens between them (`EQ`, `SEMICOLON`) still come out.

### Step 3c: Test Suite

Build `test_lexer.py` with at least the test cases below.  Each test must assert the token types in order and, for selected tokens, the value, line, and col.

- **Token type coverage (one test per type):** INT, FLOAT, STRING (with escape), IDENT, IF, ELSE, WHILE, LET, PRINT, TRUE, FALSE, and all operators: PLUS, MINUS, STAR, SLASH, EQ, EQEQ, NEQ, LT, LE, GT, GE, LPAREN, RPAREN, LBRACE, RBRACE, SEMICOLON.
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

In this direction, you build the same component with a lexer generator instead of a hand-rolled `re` loop.  The generator does the maximal-munch machinery for you.  Your job shifts to three things: write the rule specification correctly, wrap the generated scanner behind the interface contract, and prove the same properties with the same tests.  The three parts above map onto this direction as follows.  The course tutorials on [Flex and Bison]({{ site.baseurl }}/Tutorials/FlexAndBison) and on the [PLY lexer and parser]({{ site.baseurl }}/Tutorials/PLYLexerAndParser) cover the tools' own mechanics.

> **What this direction requires.** Part 0 and the Getting Started ramp apply as written, with your rule file in place of `lexer.py`'s `TOKEN_SPEC`.  Part 1 becomes a rule specification, Part 2 becomes a wrapper around the generated scanner, and Part 3 applies unchanged.  You still submit a `test_lexer.py`, a `test_output.txt`, and a readme; the readme also records your toolchain versions and explains the keyword-table idiom.

### Part 1 equivalent: the rule specification

Write a Flex `.l` file (or a PLY `tokens`/`t_*` module) that covers the full token table from Step 1a.  The ordering discipline is the same.  Generators resolve ties by rule order (Flex) or by function definition order and pattern length (PLY), so the same bugs await you if keywords trail `IDENT` or `<` precedes `<=`.  Your specification must handle:

- **Numeric literals**: integers and floats (`[0-9]+\.[0-9]*` and `[0-9]*\.[0-9]+`), with FLOAT tried before INT.
- **String literals** in double quotes with `\"`, `\\`, `\n`, `\t` escape sequences, decoded at scan time (in Flex, store the decoded string via `strdup`; in PLY, set `t.value` to the decoded text while keeping the raw lexeme available).
- **Identifiers vs. keywords**: match `[a-zA-Z_][a-zA-Z0-9_]*` and check a keyword table, returning the keyword's own token type for `if`, `else`, `while`, `let`, `print`, `true`, `false`.  This is the generator idiom for "keywords before IDENT."  Your readme must explain why the keyword-table approach and the rule-ordering approach are equivalent.
- **Multi-character operators**: `<=`, `>=`, `==`, `!=` as single tokens, listed so they win over their single-character prefixes.
- **Comments and whitespace**: `#` to end of line, skipped; whitespace skipped with newlines counted (`%option yylineno` in Flex; track `t.lexer.lineno` in PLY).

The pass criteria are the same maximal-munch cases from Step 1a: `iffy` -> `IDENT`, `whiles` -> `IDENT`, `<=` -> `LE`, `==` -> `EQEQ`.

### Part 2 equivalent: the component wrapper

The generated scanner hands you a next-token function: `yylex()` in Flex, `lexer.token()` in PLY.  Your deliverable is still a component with the interface contract.  Wrap the generated scanner in a `Lexer` class (PLY) or a small driver module (Flex) that exposes `peek`, `advance`, and `expect` with exactly the behaviors in the table above: an idempotent `peek`, EOF tokens forever at end of input, and a located `LexError` from `expect` on mismatch.  The one-token buffer from the skeleton in Part 2 is the same idea; only the source of the next token changes.  Show the same two consumption patterns from Step 2b agreeing.

In place of Step 2d's JSON configuration, provide a second rule specification that implements the alternate dialect (`//` comments, `:=` assignment), and show the same wrapper driving both.  This meets the configurability requirement using the tools' own configuration medium.

### Part 3 applies unchanged

This direction requires precise line and column positions on every error, the fail-fast and collect-all modes, and the full test suite of Step 3c (token type coverage, maximal-munch cases, string escapes, and the five deliberate error programs), exactly as written.  (In Flex, collect-all means your error rule records the offense and continues scanning rather than exiting.)

### Where the toolchain goes next

Flex is one half of a pair.  Its companion parser generator, Bison (or PLY's `yacc` module), turns a context-free grammar with precedence declarations into an LALR parser.  That half is deliberately out of scope here.  It is the natural continuation of this direction, and the Parser assignment offers a matching generator-toolchain direction where your Flex/PLY scanner feeds a Bison/PLY grammar.  Choosing the generator direction now sets you up well for that one, but the two choices are independent: you choose a direction assignment by assignment.

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
