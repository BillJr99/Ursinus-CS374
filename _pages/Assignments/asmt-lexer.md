---
layout: assignment
permalink: /Assignments/Lexer
title: "CS374: Principles of Programming Languages - The Lexer"

info:
  coursenum: CS374
  points: 100
  goals:
    - To specify a complete token grammar for the project language using ordered regular-expression rules
    - To harden the class tokenizer into a reusable Lexer component with peek, advance, and expect interface methods
    - To implement string literals with escape sequences and JSON-configurable token specifications
    - To report lexical errors with precise line and column positions and support both fail-fast and collect-all error modes
    - To deliver a fully tested component that the parser assignment and team project will import unchanged
  rubric:
    - weight: 30
      description: Token Specification
      preemerging: Fewer than half the required token types are defined, or patterns are so incorrect that the lexer cannot tokenize even simple programs
      beginning: Most token types are defined but several patterns are wrong (e.g., keywords not prioritized over identifiers, or operators missing from the spec)
      progressing: All required token types are defined with correct patterns, but the specification has a minor ordering or coverage gap (e.g., multi-character operators not listed before single-character ones)
      proficient: All 15+ token types are defined in the correct priority order, keywords are prioritized before IDENT, multi-character operators before single-character ones, whitespace and comments are skipped, and the spec is externalized in a loadable JSON file
    - weight: 40
      description: Lexer Implementation
      preemerging: The Lexer class does not exist or the peek/advance interface is fundamentally broken
      beginning: The Lexer class exists with peek and advance, but one or both are incorrect — e.g., peek consumes input, or advance skips tokens
      progressing: peek and advance work correctly for most inputs, but edge cases fail — e.g., repeated peek calls return different tokens, or EOF is not handled gracefully
      proficient: The Lexer class implements peek, advance, and expect correctly; peek is idempotent; both return an EOF token (not None or an exception) at end of input; expect raises a located LexError on mismatch; and the lexer imports cleanly as a module with no side effects at import time
    - weight: 30
      description: Error Handling, Positions, and Test Suite
      preemerging: Lexical errors crash Python with an unhandled exception, positions are absent, and no test suite exists
      beginning: Errors are caught and reported, but positions are missing or incorrect, and the test suite covers only a handful of token types
      progressing: Errors include line and column, the test suite covers most token types, but error recovery (collect-all mode) is missing or incorrect, and escape sequences are not fully tested
      proficient: Every error includes line, column, and the offending text; collect-all mode gathers every error in a single pass; the test suite covers all token types, all escape sequences, all maximal-munch cases, and at least five deliberate error programs with their expected messages verified
  readings:
    - rtitle: "Tokens and Scanning Activity"
      rlink: "https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374-Fall2026/gh-pages/_pages/Activities/liascript-tokensscanning.md"

tags:
  - lexer
  - languages
  - pipeline

---

This assignment turns the class tokenizer into a **component**: the first permanent piece of your language pipeline. The parser assignment imports it unchanged; your team project ships it. Every design decision you make here propagates forward, so document your interface carefully. Build in the scaffolded steps below; test after each step before moving on.

---

## Part 1: Token Specification (30 points)

### Why Order Matters

A lexer built on regular expressions applies rules in order and uses *maximal munch*: it always matches the longest possible string. Two rules produce bugs if ordered wrong:

- If `IDENT` appears before `IF`, then `if` will be tokenized as an identifier named `"if"`.
- If `LT` (`<`) appears before `LE` (`<=`), then `<=` will be tokenized as `LT` followed by `EQ`.

The correct ordering is: **keywords before identifiers**, and **longer operators before their prefixes**.

### Step 1a: Define the TOKEN_SPEC

Define a `TOKEN_SPEC` list of `(token_name, regex_pattern)` pairs that covers at minimum the following 16 token types. Every pattern must be a raw string (`r"..."`).

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
| `IDENT` | `foo`, `my_var`, `x1` | Letter or underscore, then letters/digits/underscores |
| `LE` | `<=` | Must appear before LT |
| `GE` | `>=` | Must appear before GT |
| `EQEQ` | `==` | Must appear before EQ |
| `NEQ` | `!=` | Must appear before BANG |
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

**Maximal-munch test cases you must pass:** `iffy` → `IDENT("iffy")` (not `IF` + `IDENT("ffy")`); `<=` → `LE` (not `LT` + `EQ`); `==` → `EQEQ` (not two `EQ`s); `whiles` → `IDENT("whiles")`.

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
- `iffy` → single IDENT, not IF + IDENT
- `whiles` → single IDENT
- `<=` → LE, not LT + EQ
- `==` → EQEQ, not EQ + EQ
- `!=` → NEQ, not two tokens

**String escape cases:**
- `"no escapes"` → value equals `no escapes`
- `"tab\there"` → value contains a real tab
- `"line\nbreak"` → value contains a real newline
- `"quote\"end"` → value contains a double-quote

**Deliberate error programs (five required):**
1. A program with `@` — expect `LexError at line 1, col ...`
2. An unterminated string `"hello` — expect `LexError` at the opening quote
3. A program with `$` in the middle — check position is mid-program, not line 1
4. A collect-all run with two errors — verify both are reported
5. A program with a valid token immediately after an error — verify recovery in collect-all mode

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
- What about your lexer would you change if your language used significant indentation like Python?
- The `expect` method was designed for the parser's benefit. Explain why the parser needs `expect` rather than just calling `advance` and checking the type afterward.
- If collaboration with a buddy was permitted, did you work with a buddy on this assignment? If so, who? If not, do you certify that this submission represents your own original work? Please identify any and all portions of your submission that were not originally written by you.
- Approximately how many hours it took you to finish this assignment (I will not judge you for this at all — I am simply using it to gauge if the assignments are too easy or hard)?
