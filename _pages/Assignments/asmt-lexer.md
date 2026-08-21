---
layout: assignment
permalink: /Assignments/Lexer
title: "CS374: Principles of Programming Languages - The Lexer"

info:
  coursenum: CS374
  purpose: "To turn the class tokenizer into the first permanent component of your language pipeline — a reusable Lexer with a stable peek/advance/expect interface that the Parser and team project import unchanged."
  tilt:
    task: "Specify an ordered token grammar, build a reusable Lexer component with peek/advance/expect, string escapes, and a configurable token specification — hand-rolled in Python or via the generator-toolchain direction (Flex or PLY) — then add positioned error reporting and a full test suite."
    criteria: "Assessed on a correctly ordered token spec, an idempotent side-effect-free Lexer interface, and precise error reporting with a full test suite, weighted 30/40/30 across the three parts; the rubric applies equivalently to whichever direction you choose. See the rubric below for the full breakdown."
  points: 100
  goals:
    - To specify a complete token grammar for the project language using ordered regular-expression rules
    - To harden the class tokenizer into a reusable Lexer component with peek, advance, and expect interface methods
    - To implement string literals with escape sequences and JSON-configurable token specifications
    - To report lexical errors with precise line and column positions and support both fail-fast and collect-all error modes
    - To deliver a fully tested component that the parser assignment and team project will import unchanged
  rubric:
    - weight: 30
      description: "Token Specification (Goal 1: specify a complete token grammar using ordered regular-expression rules)"
      preemerging: Fewer than half the token types in the specification table are defined, or patterns are so incorrect that the lexer cannot tokenize even simple programs
      beginning: Most token types are defined but several patterns are wrong (e.g., keywords not prioritized over identifiers, or operators missing from the spec)
      progressing: All required token types are defined with correct patterns, but the specification has a minor ordering or coverage gap (e.g., multi-character operators not listed before single-character ones)
      proficient: Every token type in the specification table is defined in the correct priority order — keywords before IDENT, multi-character operators before their single-character prefixes, whitespace and comments skipped — demonstrating mastery of ordered regular-expression rule specification; the spec is externalized in a loadable JSON file (or, in the generator-toolchain direction, expressed as an ordered Flex/PLY rule specification); and the lexing theory questions (Step 1d) are answered with mechanism-level reasoning about maximal munch, keyword handling, and the lexer/parser division of labor
    - weight: 40
      description: "Lexer Implementation (Goal 2: harden the tokenizer into a reusable Lexer component with peek, advance, and expect)"
      preemerging: The Lexer class does not exist or the peek/advance interface is fundamentally broken
      beginning: The Lexer class exists with peek and advance, but one or both are incorrect — e.g., peek consumes input, or advance skips tokens
      progressing: peek and advance work correctly for most inputs, but edge cases fail — e.g., repeated peek calls return different tokens, or EOF is not handled gracefully
      proficient: The Lexer class implements peek, advance, and expect correctly — peek is idempotent, both return an EOF token at end of input, expect raises a located LexError on mismatch — demonstrating that the component is ready to be imported unchanged by the parser; the lexer has no side effects at import time
    - weight: 30
      description: "Error Handling, Positions, and Test Suite (Goals 3-5: escape sequences, precise error positions, collect-all mode, and a fully tested deliverable)"
      preemerging: Lexical errors crash Python with an unhandled exception, positions are absent, and no test suite exists
      beginning: Errors are caught and reported, but positions are missing or incorrect, and the test suite covers only a handful of token types
      progressing: Errors include line and column, the test suite covers most token types, but error recovery (collect-all mode) is missing or incorrect, and escape sequences are not fully tested
      proficient: Every error includes line, column, and the offending text; collect-all mode gathers every error in a single pass without stopping; string-literal escape sequences are fully implemented; and the test suite covers all token types, all escape sequences, all maximal-munch cases, and at least five deliberate error programs with expected messages verified — demonstrating a deliverable that the team project can import unchanged
  readings:
    - rtitle: "Tokens and Scanning Activity"
      rlink: "https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374/gh-pages/_pages/Activities/liascript-tokensscanning.md"

tags:
  - lexer
  - languages
  - pipeline

---

This assignment turns the class tokenizer into a **component**: the first permanent piece of your language pipeline. The parser assignment imports it unchanged; your team project ships it. Every design decision you make here propagates forward, so document your interface carefully. Build in the scaffolded steps below; test after each step before moving on.

---

## Choose Your Direction

This is one assignment with one deliverable and one rubric, built in your choice of **direction**:

- **Hand-rolled lexer (the core direction).** Build the Lexer yourself in Python atop `re`, exactly as scaffolded in Parts 1-3 below. This is the direction most students take, and it is the one the step-by-step scaffolding assumes.
- **Generator-toolchain lexer (Flex or PLY).** Build the same component with an industrial lexer generator — Flex (C) or PLY (Python) — the tools that produce the scanners inside major compilers. This direction substitutes the *vehicle* of Parts 1 and 2 (the `TOKEN_SPEC` list, the `tokenize` generator, and the hand-written class internals) with a generator specification; the interface contract, Part 3's error/position/test requirements, the deliverable structure, and the rubric all apply equivalently. See **[The Generator-Toolchain Direction](#the-generator-toolchain-direction-flex-or-ply)** below for the full mapping.

Either way you submit a token specification, a working lexer component behind the `peek`/`advance`/`expect` contract, and positioned errors with a full test suite — graded on the same 30/40/30 rubric.

---

## Getting Started

### Environment and Setup

You need Python 3.10+ (`python --version` — record it in your readme) and the standard library only (`re`, `json`, `dataclasses`). This assignment grows the class tokenizer — and the `finditer` mini lexer you built in the Regex assignment — into a component. Start from whichever of those you trust more, and create the deliverable files up front:

```
lexer.py             # the Lexer module
token_spec.json      # default token specification (Step 2d)
token_spec_alt.json  # alternate dialect (Step 2d)
test_lexer.py        # the test suite
```

### Your First 30 Minutes

Define the `Token` dataclass from Step 1b and a `TOKEN_SPEC` with just six rules — `WHITESPACE`, `LET`, `IDENT`, `EQ`, `INT`, `SEMICOLON` — then write the `tokenize` generator from Step 1c and run it on the worked example:

```python
for tok in tokenize("let x = 42;"):
    print(tok)
```

Compare your output against the six-token listing in Step 1c, including line and column numbers. Then feed it `lets x = 42;` and confirm `lets` comes out as a single `IDENT` — if it comes out as `LET` + `IDENT("s")`, your keyword pattern is missing its boundary check, and it is far better to learn that now with six rules than later with twenty-nine.

### Suggested Pacing

See the course schedule for the assigned and due dates. Your starting point is the mini lexer you built in the **Regex Workshop lab** and grew in the Regex assignment — this assignment turns it into a permanent pipeline component. The Finite Automata Simulators lab runs alongside the start of this window; it is short by design, so plan its two to three hours into your week:

| Checkpoint | You should have |
|------------|----------------|
| On assignment | `Token` dataclass and a six-rule `tokenize` generator working (grown from your mini lexer) |
| Checkpoint 1 | Parts 1-2a: full `TOKEN_SPEC` passing all maximal-munch cases, and the core `Lexer` class with `peek`/`advance`/`expect` working |
| Checkpoint 2 | Parts 2b-2c: string escapes and JSON configuration (both dialects) |
| Due date | Part 3 error modes with precise positions and the full test suite complete; readme written; ZIP assembled and submitted |

---

## Part 1: Token Specification (30 points)

### Why Order Matters

A lexer built on regular expressions applies rules in order and uses *maximal munch*: it always matches the longest possible string. Two rules produce bugs if ordered wrong:

- If `IDENT` appears before `IF`, then `if` will be tokenized as an identifier named `"if"`.
- If `LT` (`<`) appears before `LE` (`<=`), then `<=` will be tokenized as `LT` followed by `EQ`.

The correct ordering is: **keywords before identifiers**, and **longer operators before their prefixes**.

### Step 1a: Define the TOKEN_SPEC

Define a `TOKEN_SPEC` list of `(token_name, regex_pattern)` pairs that covers, at minimum, every token type in the table below. Every pattern must be a raw string (`r"..."`).

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

**Maximal-munch test cases you must pass:** `iffy` -> `IDENT("iffy")` (not `IF` + `IDENT("ffy")`); `<=` -> `LE` (not `LT` + `EQ`); `==` -> `EQEQ` (not two `EQ`s); `whiles` -> `IDENT("whiles")`; `notable` -> `IDENT("notable")` (not `NOT` + `IDENT("able")`); `->` -> `ARROW` (not `MINUS` + `GT`); `!=` -> `NEQ` (not `BANG` + `EQ`).

### Step 1b: Token Dataclass

Define a `Token` dataclass (or namedtuple) with fields: `type` (string), `value` (string — the raw lexeme), `line` (int), `col` (int). The EOF token has type `"EOF"`, value `""`, and the line/col of the last character consumed.

### Step 1c: Baseline Tokenize Generator

Write a `tokenize(source: str) -> Iterator[Token]` generator that applies `TOKEN_SPEC` using `re.match` at the current position, skipping WHITESPACE and COMMENT tokens, and advancing the position by the match length. Verify it against the provided test programs before wrapping it in a class.

**Worked example** — source `"let x = 42;"`:

```
Token(LET,       "let", line=1, col=1)
Token(IDENT,     "x",   line=1, col=5)
Token(EQ,        "=",   line=1, col=7)
Token(INT,       "42",  line=1, col=9)
Token(SEMICOLON, ";",   line=1, col=11)
Token(EOF,       "",    line=1, col=12)
```

### Step 1d: Lexing Theory Questions (in your readme)

Three written questions from the Tokens and Scanning session, graded within Part 1's rubric row:

1. **Maximal munch, precisely.** Your spec tokenizes `<==` as `LE` then `EQ` — not `LT` then `EQEQ`, and not three single-character tokens. State the two rules (longest match, then rule order) that force this outcome, and give one input where the two rules would *disagree* about the result if applied in the other priority.
2. **Why keywords aren't the lexer's problem twice.** `iffy` must lex as one `IDENT`, never `IF` + `IDENT("fy")`. Explain the two different mechanisms that can enforce this (rule ordering with boundary-aware patterns vs. lex-as-identifier-then-reclassify against a keyword table), and name one cost of each.
3. **The division of labor.** `let 42 = x;` lexes without a single error. State in one sentence per stage why the lexer *must* accept it and which later pipeline stage rejects it — and what this says about what a token stream does and does not promise.

---

## Part 2: Lexer Class Implementation (40 points)

### The Interface Contract

The parser will use exactly three methods:

| Method | Behavior |
|--------|----------|
| `peek() -> Token` | Return the next token *without consuming it*. Idempotent: calling it ten times in a row must return the same token. |
| `advance() -> Token` | Consume and return the next token. After calling advance, the next peek/advance returns the token after the one just returned. |
| `expect(token_type: str) -> Token` | If the next token matches `token_type`, consume and return it. Otherwise raise `LexError` with the expected type, found type, and position. |

At end of input, both `peek` and `advance` return the EOF token repeatedly — they never raise `StopIteration` or return `None`.

### Step 2a: Implement the Lexer Class

```python
class Lexer:
    def __init__(self, source: str, config_path: str = None):
        ...  # load config if provided, build token stream, initialize lookahead buffer

    def peek(self) -> Token: ...
    def advance(self) -> Token: ...
    def expect(self, token_type: str) -> Token: ...
```

Use an internal buffer of one token (the lookahead). When the buffer is empty, pull the next token from your generator and fill it. `peek` returns the buffer contents without clearing it. `advance` returns the buffer contents and clears it.

### Step 2b: Verify Two Consumption Patterns

Demonstrate that a peek-driven loop and an advance-driven loop produce identical token streams:

```python
# Pattern A: peek-driven
tokens_a = []
while lexer_a.peek().type != "EOF":
    tokens_a.append(lexer_a.advance())

# Pattern B: advance-driven
tokens_b = []
tok = lexer_b.advance()
while tok.type != "EOF":
    tokens_b.append(tok)
    tok = lexer_b.advance()

assert tokens_a == tokens_b, "Consumption patterns disagree!"
```

### Step 2c: String Literals with Escapes

Extend the STRING pattern (or handle it as a special case) to support:

| Escape sequence | Decoded value |
|----------------|--------------|
| `\"` | double-quote character |
| `\\` | backslash |
| `\n` | newline (ASCII 10) |
| `\t` | tab (ASCII 9) |

Store **both** the raw lexeme (e.g., `"a\nb"` with a backslash-n) and the decoded value (with a real newline) in the Token. An unterminated string — one that reaches end-of-line or end-of-file without a closing `"` — must raise a `LexError` pointing at the *opening* quote's position, not at end of input.

**Worked example:**

```
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

Load and validate the config at `Lexer.__init__` time: every pattern must compile (catch `re.error` and raise `LexError` with the offending pattern). Demonstrate configurability with a **second JSON spec** in which the comment character is `//` and the assignment operator is `:=` — show the same `Lexer` class tokenizing a short program in that dialect.

---

## Part 3: Error Handling, Positions, and Test Suite (30 points)

### Step 3a: Precise Error Positions

Every `LexError` must include:
- The line number (1-indexed) of the offending character
- The column number (1-indexed) of the offending character
- The offending text itself (the unrecognized character or the unterminated string lexeme)

Example message format: `LexError at line 3, col 7: unexpected character '@'`

Track line numbers by counting `\n` characters consumed. Track column by resetting to 1 after each newline.

### Step 3b: Two Error Modes

Implement two modes, selectable at construction time via `error_mode="fail_fast"` (default) or `error_mode="collect_all"`:

- **fail_fast**: raise `LexError` on the first unrecognized character.
- **collect_all**: skip unrecognized characters (recording each error), finish tokenizing, then raise a single `LexErrorList` containing all errors. This allows students to see all their mistakes in one pass rather than fixing one at a time.

### Step 3c: Test Suite

Build `test_lexer.py` with at least the following test cases. Each test must assert both the token types in order and, for selected tokens, the value, line, and col.

**Token type coverage (one test per type):**
- INT, FLOAT, STRING (with escape), IDENT, IF, ELSE, WHILE, LET, PRINT, TRUE, FALSE
- All operators: PLUS, MINUS, STAR, SLASH, EQ, EQEQ, NEQ, LT, LE, GT, GE, LPAREN, RPAREN, LBRACE, RBRACE, SEMICOLON

**Maximal-munch cases:**
- `iffy` -> single IDENT, not IF + IDENT
- `whiles` -> single IDENT
- `<=` -> LE, not LT + EQ
- `==` -> EQEQ, not EQ + EQ
- `!=` -> NEQ, not two tokens

**String escape cases:**
- `"no escapes"` -> value equals `no escapes`
- `"tab\there"` -> value contains a real tab
- `"line\nbreak"` -> value contains a real newline
- `"quote\"end"` -> value contains a double-quote

**Deliberate error programs (five required):**
1. A program with `@` — expect `LexError at line 1, col ...`
2. An unterminated string `"hello` — expect `LexError` at the opening quote
3. A program with `$` in the middle — check position is mid-program, not line 1
4. A collect-all run with two errors — verify both are reported
5. A program with a valid token immediately after an error — verify recovery in collect-all mode

---

## The Generator-Toolchain Direction (Flex or PLY)

If you choose this direction, you build the same component with an industrial lexer generator instead of a hand-rolled `re` loop. The generator does the maximal-munch machinery for you; your job shifts to writing the rule specification correctly, wrapping the generated scanner behind the interface contract, and proving the same properties with the same tests. The three parts above map onto this direction as follows.

### Part 1 equivalent: the rule specification

Write a Flex `.l` file (or a PLY `tokens`/`t_*` module) covering the full token table from Step 1a. The ordering discipline is identical — generators resolve ties by rule order (Flex) or by function definition order and pattern length (PLY) — so the same bugs await you if keywords trail `IDENT` or `<` precedes `<=`. Your specification must handle:

- **Numeric literals** — integers and floats (`[0-9]+\.[0-9]*` and `[0-9]*\.[0-9]+`), with FLOAT tried before INT.
- **String literals** in double quotes with `\"`, `\\`, `\n`, `\t` escape sequences, decoded at scan time (in Flex, store the decoded string via `strdup`; in PLY, set `t.value` to the decoded text while keeping the raw lexeme available).
- **Identifiers vs. keywords** — match `[a-zA-Z_][a-zA-Z0-9_]*` and check a keyword table, returning the keyword's own token type for `if`, `else`, `while`, `let`, `print`, `true`, `false`. This is the generator idiom for "keywords before IDENT," and your readme must explain why the keyword-table approach and the rule-ordering approach are equivalent.
- **Multi-character operators** — `<=`, `>=`, `==`, `!=` as single tokens, listed so they win over their single-character prefixes.
- **Comments and whitespace** — `#` to end of line, skipped; whitespace skipped with newlines counted (`%option yylineno` in Flex; track `t.lexer.lineno` in PLY).

The pass criteria are the same maximal-munch cases from Step 1a: `iffy` -> `IDENT`, `whiles` -> `IDENT`, `<=` -> `LE`, `==` -> `EQEQ`.

### Part 2 equivalent: the component wrapper

The generated scanner hands you a next-token function (`yylex()` in Flex, `lexer.token()` in PLY). Your deliverable is still a **component with the interface contract**: wrap the generated scanner in a `Lexer` class (PLY) or a small driver module (Flex) exposing `peek`, `advance`, and `expect` with exactly the behaviors in the table above — idempotent `peek`, EOF tokens forever at end of input, and a located `LexError` from `expect` on mismatch. Demonstrate the same two consumption patterns from Step 2b agreeing. In place of Step 2d's JSON configuration, provide a **second rule specification** implementing the alternate dialect (`//` comments, `:=` assignment) and show the same wrapper driving both — the configurability requirement, met with the tools' own configuration medium.

### Part 3 applies unchanged

Precise line/column positions on every error, the fail-fast and collect-all modes, and the full test suite of Step 3c — token type coverage, maximal-munch cases, string escapes, and the five deliberate error programs — are required in this direction exactly as written. (In Flex, collect-all means your error rule records the offense and continues scanning rather than exiting.)

### Where the toolchain goes next

Flex is one half of a pair: its companion parser generator, Bison (or PLY's `yacc` module), turns a context-free grammar with precedence declarations into an LALR parser. That half is deliberately out of scope here — it is the natural continuation of this direction, and the **Parser assignment offers a matching generator-toolchain direction** where your Flex/PLY scanner feeds a Bison/PLY grammar. Choosing the generator direction now sets you up well for that one, but the two choices are independent: directions are chosen assignment by assignment.

---

## Deliverables

Submit a ZIP containing:
- `lexer.py` — the Lexer module (importable with no side effects)
- `token_spec.json` — the default token specification
- `token_spec_alt.json` — the alternate dialect specification (`//` comments, `:=` assignment)
- `test_lexer.py` — the test suite with documented test cases
- `test_output.txt` — the output of running `python test_lexer.py` (all tests passing)
- `readme.md` — approximately one page documenting the Lexer interface for the parser author (future you), including the TOKEN_SPEC ordering rationale and the two error modes

Ensure reproducibility by listing your Python version (`python --version`).

**Generator-toolchain direction:** the deliverable structure is identical with the vehicle swapped — the `.l` file (plus a `Makefile` that builds the scanner from scratch) or the PLY lexer module in place of the hand-rolled internals; the default and alternate-dialect rule specifications in place of the two JSON files; the wrapper exposing `peek`/`advance`/`expect`; the same test suite and `test_output.txt`; and a readme that additionally records your toolchain versions (`flex --version`, or your PLY version) and explains the keyword-table idiom.

---

## Grading Breakdown

| Component | Points |
|-----------|--------|
| Part 1: Token Specification | 30 |
| Part 2: Lexer Class Implementation | 40 |
| Part 3: Error Handling and Test Suite | 30 |
| **Total** | **100** |

---

## Reflection Prompts

- Which scanning rule (maximal munch or priority) caused you a real bug, and how did your tests catch it?
- Which direction did you choose, and what did that choice make easier or harder than you expected? If you took the generator toolchain: what did Flex or PLY do for you that you would otherwise have written by hand, and what did it hide that you had to recover?
- What about your lexer would you change if your language used significant indentation like Python?
- The `expect` method was designed for the parser's benefit. Explain why the parser needs `expect` rather than just calling `advance` and checking the type afterward.
- If collaboration with a buddy was permitted, did you work with a buddy on this assignment? If so, who? If not, do you certify that this submission represents your own original work? Please identify any and all portions of your submission that were not originally written by you.
- AI disclosure: list any generative-AI tools you used, for what, and how you verified the results (or state 'none').
- Approximately how many hours it took you to finish this assignment (I will not judge you for this at all — I am simply using it to gauge if the assignments are too easy or hard)?
