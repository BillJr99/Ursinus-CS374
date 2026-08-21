<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374/gh-pages/_pages/Activities/liascript-tokensscanning.md or locally via https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374/gh-pages/_pages/Activities/liascript-tokensscanning.md

import: https://raw.githubusercontent.com/liascript/CodeRunner/master/README.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

# Tokens and Scanning: Building a Lexer

Before a compiler can understand your program, it has to figure out where one meaningful chunk of text ends and the next one begins, just like a spell-checker must split a sentence into individual words before it can flag any of them as wrong. A **lexer** (also called a scanner) does exactly this: it reads a raw stream of characters and groups them into **tokens**, the smallest named units of meaning (a number, a keyword, an operator). Without this first step, the rest of the compiler has no footing; it would be trying to parse soup.

## Learning Goals

By the end of this activity, you will be able to:

- Define the structure of a token (type, lexeme, position) and explain the lexer's contract with the parser downstream
- Apply the maximal munch rule and priority ordering to resolve ambiguous tokenizations by hand and predict the output token stream for a given input string
- Implement a table-driven lexer in Python that uses an ordered token specification, a master regex, and `re.finditer` to emit a typed token stream with line and column positions
- Identify and handle lexer error conditions (illegal characters, unterminated strings) and explain why error recovery strategy must be chosen deliberately
- Construct a token specification (TOKEN_SPEC) for a new language, ordering rules correctly to enforce keyword priority over identifier patterns

Today the theory pays its first concrete dividend: we build a working **lexer**, the first stage of your project pipeline, which converts raw characters into a stream of typed **tokens** using exactly the regular machinery of the *Regular Expressions* and *Finite Automata* activities. The arc: **what a token is $\rightarrow$ the scanning rules (maximal munch, priority) $\rightarrow$ a complete Python lexer $\rightarrow$ error handling and positions**.

> **Before You Begin:** This activity assumes you can:
> - Write Python classes with __init__ and methods
> - Use Python's re module for regular expressions at a basic level
> - Understand what a token is (a named unit of source text like NUMBER or IDENTIFIER)
> If any of these feel shaky, review them first.

---

## Directions and Group Roles

Work in your POGIL team with rotated roles (**Manager**, **Recorder**, **Presenter**, **Reflector**). Consider each model and question individually first, then discuss with your group. The Recorder posts answers to the Class Activity Questions discussion board; the Presenter reports out areas of disagreement or alternative approaches. After class, respond to the reflective prompt individually in your notebook.

---

# Part I: Tokens and Rules

## 1. The Lexer's Contract

**A token is a typed unit of source text**: a pair (and usually a triple) of *type*, *lexeme*, and *position*: `(NUMBER, "42", line 3)`. The lexer's contract with the parser is to deliver a stream of tokens and to absorb everything the parser should never see: whitespace, comments, and the raggedness of raw characters. Each token type is specified by a **regular expression**, which is why the lexer is exactly as powerful as, and no more powerful than, a finite automaton.

**Two rules resolve every conflict.** When multiple patterns could match at the current position: **maximal munch** says take the *longest* match (`<=` is one token, not `<` then `=`; `forty` is an identifier, not `for` then `ty`); **priority** breaks length ties by pattern order (the lexeme `if` matches both the keyword pattern and the identifier pattern, and wins as a keyword because keywords are listed first, or are checked after via a keyword table).

---

## Model 1: Be the Lexer

Before writing any code, it helps to play the lexer yourself on a small example. This model asks you to walk through a single line of source text and decide, character by character, where each token begins and ends. The main challenge here is not ambiguity in meaning; it is ambiguity in *boundaries*: should `count2` be one token or two, and should `>=` be one token or two? Working through this by hand makes the rules you will later encode in regex feel inevitable rather than arbitrary.

Tokenize by hand: `count2 = count2 + 12 >= limit`

### Critical Thinking Questions

1. Produce the token list (type and lexeme for each). How many tokens? Where did teams differ?
2. Apply maximal munch to `count2`: why is it one identifier rather than an identifier `count` followed by a number `2`? Which rule decides, and what regex for identifiers makes it so?
3. `>=` must not become `>` then `=`. Describe the bug a parser would face downstream if the lexer got this wrong, and state the general principle about where to fix errors in a pipeline.
4. Should the lexer reject `12abc`, or emit `12` then `abc` and let the parser complain? Defend a position; real languages differ, and your project must choose.


> The worked answers to this session's models are in the **Answer Key** at the end of this page. Attempt them with your team first.

# Part II: The Lexer in Code

## 2. A Complete Tokenizer

This lexer is the seed of your assignment and your project: a token specification as data, one master pattern, and a generator that yields typed tokens with positions. Read it alongside the regex module's `finditer` discussion.

---

## Code Cell

The lexer below translates the hand-tokenization rules from Model 1 into working Python. The key insight is that by joining all the individual regex patterns into one big alternation with `|`, Python's regex engine does the scanning in a single left-to-right pass: it tries each alternative in order, picks the first one that matches, and moves on. Priority (which pattern wins when two could match) is controlled entirely by the order of entries in `TOKEN_SPEC`.

> **Watch out!** Whitespace is listed in `TOKEN_SPEC` as `SKIP` and is silently consumed. If you forget to include a whitespace pattern, the `MISMATCH` catch-all will fire on every space and your error messages will be buried in noise. Always verify that spaces and tabs are handled before testing with real programs.

```python  liascript
import re
from collections import namedtuple

Token = namedtuple("Token", ["type", "lexeme", "line", "col"])

# Order encodes priority: keywords before IDENT, two-char operators before one-char.
TOKEN_SPEC = [
    ("NUMBER",   r"\d+(\.\d+)?"),
    ("KEYWORD",  r"\b(if|else|while|let|print)\b"),
    ("IDENT",    r"[A-Za-z_][A-Za-z0-9_]*"),
    ("GE",       r">="), ("LE", r"<="), ("EQ", r"=="), ("NE", r"!="),
    ("ASSIGN",   r"="),
    ("GT",       r">"), ("LT", r"<"),
    ("PLUS",     r"\+"), ("MINUS", r"-"), ("STAR", r"\*"), ("SLASH", r"/"),
    ("LPAREN",   r"\("), ("RPAREN", r"\)"),
    ("LBRACE",   r"\{"), ("RBRACE", r"\}"),
    ("SEMI",     r";"),
    ("NEWLINE",  r"\n"),
    ("SKIP",     r"[ \t]+"),
    ("COMMENT",  r"#[^\n]*"),
    ("MISMATCH", r"."),                      # anything else: a lexical error
]
MASTER = re.compile("|".join(f"(?P<{name}>{pat})" for name, pat in TOKEN_SPEC))

def tokenize(source):
    line, line_start = 1, 0
    try:
        for m in MASTER.finditer(source):
            kind, lexeme = m.lastgroup, m.group()
            col = m.start() - line_start + 1
            if kind == "NEWLINE":
                line += 1; line_start = m.end()
            elif kind in ("SKIP", "COMMENT"):
                continue
            elif kind == "MISMATCH":
                raise SyntaxError(f"line {line}, col {col}: unexpected character {lexeme!r}")
            else:
                yield Token(kind, lexeme, line, col)
    except SyntaxError:
        raise
    except Exception as e:
        print(f"[lexer:tokenize] {e}")
        import traceback; traceback.print_exc()

code = """let count2 = 0;   # initialize
while (count2 <= 10) {
    count2 = count2 + 1;
}
print count2;
"""

for tok in tokenize(code):
    print(tok)
```
@LIA.eval(`["main.py"]`, `none`, `python3 main.py`)

---

## Model 2: Read the Machine You Built

Now that the lexer runs, this model asks you to read it as a system, connecting each design decision back to the theory. You already know the code works; the goal here is to understand *why* it is structured the way it is so you can adapt it confidently when the rules change (as they will on your project).

### Critical Thinking Questions

5. The master pattern joins every token regex with `|` into one alternation. Connect this single move to Thompson's construction from the automata module: what machine, conceptually, does `finditer` run?
6. Why must `GE` (`>=`) appear before `GT` (`>`) in the spec, given how Python's `re` alternation chooses among same-position matches? Design the two-character experiment that proves the necessity, run it, and report.
7. Keywords are matched with `\b(if|else|...)\b` *before* `IDENT`. Remove the `\b` anchors mentally: what goes wrong with the identifier `iffy`? Which scanning rule did the anchors enforce?

> **Watch out!** Keywords must always appear *before* the general identifier pattern in your `TOKEN_SPEC`. If `IDENT` comes first, the regex engine will match `if` as an identifier and never reach the KEYWORD rule, because Python's `re` alternation returns the first match, not the longest. Getting this order wrong produces a lexer that accepts `if` as a variable name, breaking every conditional in your language silently.

8. The `MISMATCH` catch-all turns unknown characters into a `SyntaxError` with line and column. Feed the lexer a `$` and verify the message. Why is reporting *position* a kindness worth the bookkeeping?

---

## Model 3: Peek/Advance Lexer Interface

The raw `tokenize()` generator works fine for printing, but a parser needs more control: it must be able to look at the next token *before* deciding whether to consume it. This model solves that problem by wrapping the generator in a `Lexer` class that buffers one token. The result is a clean, three-method interface (`peek`, `advance`, `expect`) that the parser will use exclusively; the generator becomes an implementation detail.

A parser never calls `tokenize()` directly. It needs two operations: **peek**, look at the next token without consuming it, and **advance**, consume and return it. A third operation, **expect**, consumes a token and raises an error if its type does not match. The `Lexer` class below wraps the generator and buffers exactly one token to implement these three methods.

```python  liascript
import re
from collections import namedtuple

Token = namedtuple("Token", ["type", "lexeme", "line", "col"])

TOKEN_SPEC = [
    ("NUMBER",   r"\d+(\.\d+)?"),
    ("KEYWORD",  r"\b(if|else|while|let|print)\b"),
    ("IDENT",    r"[A-Za-z_][A-Za-z0-9_]*"),
    ("GE",       r">="), ("LE", r"<="), ("EQ", r"=="), ("NE", r"!="),
    ("ASSIGN",   r"="),
    ("GT",       r">"), ("LT", r"<"),
    ("PLUS",     r"\+"), ("MINUS", r"-"), ("STAR", r"\*"), ("SLASH", r"/"),
    ("LPAREN",   r"\("), ("RPAREN", r"\)"),
    ("LBRACE",   r"\{"), ("RBRACE", r"\}"),
    ("SEMI",     r";"),
    ("NEWLINE",  r"\n"),
    ("SKIP",     r"[ \t]+"),
    ("COMMENT",  r"#[^\n]*"),
    ("MISMATCH", r"."),
]
MASTER = re.compile("|".join(f"(?P<{name}>{pat})" for name, pat in TOKEN_SPEC))
EOF_TOKEN = Token("EOF", "", -1, -1)

def _tokenize(source):
    line, line_start = 1, 0
    for m in MASTER.finditer(source):
        kind, lexeme = m.lastgroup, m.group()
        col = m.start() - line_start + 1
        if kind == "NEWLINE":
            line += 1; line_start = m.end()
        elif kind in ("SKIP", "COMMENT"):
            continue
        elif kind == "MISMATCH":
            raise SyntaxError(f"line {line}, col {col}: unexpected {lexeme!r}")
        else:
            yield Token(kind, lexeme, line, col)

class Lexer:
    """Wraps the tokenize generator with peek/advance/expect."""

    def __init__(self, source):
        self._gen = _tokenize(source)
        self._buf = None          # one-token lookahead buffer
        self._advance_buf()       # prime the buffer

    def _advance_buf(self):
        try:
            self._buf = next(self._gen)
        except StopIteration:
            self._buf = EOF_TOKEN

    def peek(self):
        """Return the next token without consuming it."""
        return self._buf

    def advance(self):
        """Consume and return the next token."""
        tok = self._buf
        self._advance_buf()
        return tok

    def expect(self, *types):
        """Consume the next token; raise SyntaxError if its type is not in types."""
        tok = self.advance()
        if tok.type not in types:
            raise SyntaxError(
                f"line {tok.line}, col {tok.col}: "
                f"expected {types}, got {tok.type!r} ({tok.lexeme!r})"
            )
        return tok

    def at_end(self):
        return self._buf.type == "EOF"

# --- Demo: two traversal styles producing identical streams ---

source = "let x = 42 + y;"

print("=== Style 1: advance until EOF ===")
lx = Lexer(source)
while not lx.at_end():
    print(lx.advance())

print()
print("=== Style 2: peek then advance (decision before consuming) ===")
lx = Lexer(source)
while not lx.at_end():
    tok = lx.peek()
    consumed = lx.advance()
    print(f"peeked {tok.type:8} -> consumed {consumed.lexeme!r}")

print()
print("=== Style 3: expect a specific sequence ===")
lx = Lexer(source)
kw   = lx.expect("KEYWORD")
name = lx.expect("IDENT")
eq   = lx.expect("ASSIGN")
val  = lx.expect("NUMBER")
print(f"let-binding: {kw.lexeme} {name.lexeme} {eq.lexeme} {val.lexeme}")
```
@LIA.eval(`["main.py"]`, `none`, `python3 main.py`)

### Critical Thinking Questions

9. The `Lexer` class stores exactly one token in `_buf`. Why is one token enough? Describe a parsing situation that would require *two* tokens of lookahead and explain how you would extend `_buf` to handle it.
10. `peek()` is a pure read: it does not change the lexer's state. Why is that guarantee important for a parser that makes decisions (e.g., "is the next token a `(`?") before consuming?
11. `expect()` raises `SyntaxError` if the type does not match. Compare this to a design where `expect()` returns `None` on mismatch instead of raising. What does the raising version give the parser author that the silent-return version does not?

---

## Model 4: Real-World Lexer Features, String Literals

The lexer built so far handles numbers, keywords, and operators, but real programs also contain string literals, and strings introduce a new complication: the content inside the quotes can contain almost anything, including characters that normally end a token. This model extends the lexer with a STRING pattern that correctly handles escape sequences, and then confronts what happens when a string is never closed.

Production lexers must handle **string literals** (e.g., `"hello world"`) and **escape sequences** (e.g., `\"`, `\\`, `\n`). The tricky part: a naive `"[^"]*"` pattern breaks on `"say \"hi\""`. The correct pattern uses a negative lookbehind or a two-alternative trick: match either an escaped character or any non-quote, non-backslash character inside the delimiters.

```python  liascript
import re
from collections import namedtuple

Token = namedtuple("Token", ["type", "lexeme", "line", "col"])

# STRING pattern: opening quote, then zero or more of (escape-seq | safe-char), closing quote.
TOKEN_SPEC = [
    ("NUMBER",   r"\d+(\.\d+)?"),
    ("STRING",   r'"(?:[^"\\]|\\.)*"'),      # <-- new: handles escape sequences
    ("KEYWORD",  r"\b(if|else|while|let|print)\b"),
    ("IDENT",    r"[A-Za-z_][A-Za-z0-9_]*"),
    ("GE",       r">="), ("LE", r"<="), ("EQ", r"=="), ("NE", r"!="),
    ("ASSIGN",   r"="),
    ("GT",       r">"), ("LT", r"<"),
    ("PLUS",     r"\+"), ("MINUS", r"-"), ("STAR", r"\*"), ("SLASH", r"/"),
    ("LPAREN",   r"\("), ("RPAREN", r"\)"),
    ("LBRACE",   r"\{"), ("RBRACE", r"\}"),
    ("SEMI",     r";"),
    ("NEWLINE",  r"\n"),
    ("SKIP",     r"[ \t]+"),
    ("COMMENT",  r"#[^\n]*"),
    ("MISMATCH", r"."),
]
MASTER = re.compile("|".join(f"(?P<{name}>{pat})" for name, pat in TOKEN_SPEC))

def tokenize(source):
    line, line_start = 1, 0
    for m in MASTER.finditer(source):
        kind, lexeme = m.lastgroup, m.group()
        col = m.start() - line_start + 1
        if kind == "NEWLINE":
            line += 1; line_start = m.end()
        elif kind in ("SKIP", "COMMENT"):
            continue
        elif kind == "MISMATCH":
            raise SyntaxError(f"line {line}, col {col}: unexpected {lexeme!r}")
        else:
            yield Token(kind, lexeme, line, col)

def unescape(raw):
    """Strip surrounding quotes and process escape sequences in a string lexeme."""
    inner = raw[1:-1]
    return inner.replace(r'\"', '"').replace(r'\\', '\\').replace(r'\n', '\n').replace(r'\t', '\t')

program = r'''
let greeting = "hello, world";
let escaped  = "say \"hi\" now";
let newlines = "line1\nline2";
print greeting;
'''

print("=== All tokens ===")
for tok in tokenize(program):
    print(tok)

print()
print("=== String values after unescaping ===")
for tok in tokenize(program):
    if tok.type == "STRING":
        print(f"  raw:       {tok.lexeme}")
        print(f"  unescaped: {unescape(tok.lexeme)!r}")

print()
print("=== What happens with an unterminated string? ===")
bad = 'let x = "oops;'
try:
    tokens = list(tokenize(bad))
    print("Tokens produced:", tokens)
    print("Note: MISMATCH absorbed the quote - no STRING token formed.")
except SyntaxError as e:
    print(f"SyntaxError: {e}")
```
@LIA.eval(`["main.py"]`, `none`, `python3 main.py`)

### Critical Thinking Questions

12. The STRING pattern is `"(?:[^"\\]|\\.)*"`. The two alternatives inside the group are `[^"\\]` (any char except quote or backslash) and `\\.` (backslash followed by any char). Explain in your own words why both alternatives are needed: what string would fail if only the first alternative existed?
13. Run the unterminated-string test. The lexer does not raise a clean error; it silently produces MISMATCH tokens. Propose a pattern change or post-processing step that would detect an unterminated string and report it with line and column.
14. `unescape()` processes `\"`, `\\`, `\n`, and `\t`. List two other escape sequences that a production language would need, and describe any ordering constraint that matters when applying multiple replacements.

---

# Part III: Hardening and Handoff (at home)

## 3. From Demo to Component

Your assignment hardens this lexer into a component your December language will import unchanged: string literals with escapes, configurable token specifications loaded from JSON, a `peek`/`advance` interface for the parser, and a test suite. The interface is the deliverable as much as the code: the parser you write next month will call `peek()` to look at the next token without consuming it and `advance()` to consume it, and nothing else.

The parser asks the lexer for the next token and receives `Token(NUMBER, "12", 4, 7)`. The information the parser will use for its *grammar* decisions is:

[(X)] The type NUMBER; the lexeme and position ride along for evaluation and error messages
[( )] The lexeme "12" alone
[( )] The line number, to enforce indentation
[( )] All fields equally, at every decision

---

## 4. Exercises

1. *String literals.* Add a `STRING` token for double-quoted strings without escapes (`"hello"`), then extend it to allow `\"` inside. Two new spec lines and three tests each; report which ordering pitfalls you hit.
2. *Peek and advance.* Wrap the generator in a `Lexer` class exposing `peek()` and `advance()` (hint: buffer one token). Demonstrate with a loop that prints tokens two different ways producing identical streams.
3. *Configurable spec.* Move `TOKEN_SPEC` into a JSON file and load it at startup; add a configuration option for the comment character. This externalization is a project requirement arriving early.
4. *Error recovery.* Instead of raising on the first bad character, collect all lexical errors and report them together at the end. Discuss in two sentences which behavior serves a programmer better, and when.
5. *Cross-language tourism.* Run your mental lexer on a Python snippet: what token must a Python-style lexer emit that ours never does? (Indentation: INDENT and DEDENT tokens, manufactured from whitespace.) One paragraph on how that bridges the lexer-parser divide.

---

## Practice: Allison, Ch. 2 §2.4: Hand-Traced Tokenization

These exercises build confidence in the maximal-munch rule and token ordering by tokenizing real programs on paper before writing code. They connect the formal lexer model to the practical parsing pipeline.

> *Exercises adapted from topics covered in *Foundations of Computing* by Chuck Allison (Fresh Sources, Inc.), used under the [MIT License](https://github.com/chuckallison/foundations-of-computing/blob/main/LICENSE).*

The lexer applies patterns in order, using maximal munch. For the input `x>=5`, if `IDENT` is listed before `GE` (`>=`) in TOKEN_SPEC, the result is:

[( )] `IDENT("x"), GE, INT(5)`: the lexer is smart enough to lookahead and reorder
[(X)] `IDENT("x"), GT, EQ, INT(5)`: `>=` is never recognized because `IDENT` greedily consumed `x`
[( )] Undefined behavior; the order doesn't matter
[( )] A `LexError` because ambiguous input

Maximal munch means the lexer matches the longest possible token. For input `<=`, if both `LT` (`<`) and `LE` (`<=`) are valid patterns:

[( )] The lexer tries `LT` first and succeeds immediately
[(X)] The lexer finds both `LT` and `LE` as possibilities and chooses `LE` (the longer match)
[( )] The lexer raises an ambiguity error
[( )] It depends on which is listed first in TOKEN_SPEC

1. **Tokenize by hand (maximal munch rules).**
   - Input: `x>=5+2`
   - Rules (in order): `IDENT` matches `[a-z]+`, `GE` matches `>=`, `PLUS` matches `+`, `INT` matches `\d+`
   - Trace through the lexer: at each position, which pattern matches? Show the token stream produced.
   - Verify: does `>=` get tokenized as one `GE` token or two (`GT, EQ`)? Why?

2. **Operator ordering matters.**
   - Suppose TOKEN_SPEC lists `EQEQ` (`==`) AFTER `EQ` (`=`). Input: `x==5`
   - Tokenize by hand using this bad ordering. What goes wrong?
   - Now reorder TOKEN_SPEC to list `EQEQ` BEFORE `EQ`, and re-tokenize. Show the correct stream.
   - Conclusion: explain in two sentences why longer operators must come first.

3. **String literals with escapes.**
   - Input: `"hello\nworld"`
   - Your STRING pattern is `"(?:[^"\\]|\\.)*"`. Trace through each character:
     - Position 0: `"`, starts the string
     - Position 1-5: `hello`, match `[^"\\]` (not quote or backslash)
     - Position 6-7: `\n`, match `\\.` (backslash followed by any char)
     - Position 8-12: `world`, match `[^"\\]` again
     - Position 13: `"`, end the string
   - Confirm: the entire 14-character string is one STRING token, not broken up.

4. **Identifying token breaks.**
   - Input: `let x = 42;`
   - Tokenize by hand with TOKEN_SPEC: `LET`, `IDENT`, `EQ`, `INT`, `SEMICOLON`, `WHITESPACE` (skip)
   - At each position, show which pattern matches and mark token boundaries. Verify: `42` is one INT token, not two separate characters.

5. **Why comments are deleted, not tokenized.**
   - Input: `x = 1 # this is a comment`
   - Tokenize, showing: (a) the tokens produced (without the comment), (b) why the lexer never produces a COMMENT token (it matches and skips).
   - Connect to Model 2 (the skipping logic): if a token's type is "COMMENT" or "WHITESPACE", the lexer silently discards it. Why is this the right design?

---

## Reflection Prompt

In your notebook: the lexer absorbs whitespace and comments so later stages never see them. What is the analogous role on a human team (the person whose filtering work is invisible exactly when done well), and what does the analogy suggest about how such work should be valued?

---

## 5. Further Reading

- Douglas Thain. *Introduction to Compilers and Language Design*, Chapter 3.
- Robert Nystrom. *Crafting Interpreters*, "Scanning" (online).
- Python `re` documentation on named groups and `finditer`.

---

Up next: the *Abstract Syntax Trees* activity builds the structure your parser will produce, and this lexer is the heart of the Lexer assignment.

# Answer Key

Work the models above with your team before reading these. Each one answers a Critical Thinking Question the session poses; seeing the answer first turns the exercise into transcription.

### Worked Example: maximal munch, position by position

Do CTQ 1 as a team before reading this. Then check the boundaries: the interesting rows are the ones where more than one pattern matches and the *longest* wins.

Input: `count2 = count2 + 12 >= limit`

| Pos | Remaining input | Patterns that match here | Longest wins | Token emitted |
|-----|-----------------|--------------------------|--------------|---------------|
| 0 | `count2 = ...` | `IDENT` -> `count2` (6 chars) | `count2` | `IDENT("count2")` |
| 6 | `_= count2 ...` | `WHITESPACE` -> ` ` | ` ` | *(skipped)* |
| 7 | `= count2 ...` | `EQ` -> `=` (1). `EQEQ` needs `==`, fails | `=` | `EQ("=")` |
| 8 | `_count2 + ...` | `WHITESPACE` | ` ` | *(skipped)* |
| 9 | `count2 + 12 ...` | `IDENT` -> `count2` (6) | `count2` | `IDENT("count2")` |
| 15 | `_+ 12 ...` | `WHITESPACE` | ` ` | *(skipped)* |
| 16 | `+ 12 >= ...` | `PLUS` -> `+` (1) | `+` | `PLUS("+")` |
| 17 | `_12 >= ...` | `WHITESPACE` | ` ` | *(skipped)* |
| 18 | `12 >= limit` | `INT` -> `12` (2). `FLOAT` needs a `.`, fails | `12` | `INT("12")` |
| 20 | `_>= limit` | `WHITESPACE` | ` ` | *(skipped)* |
| 21 | `>= limit` | **`GE` -> `>=` (2)** and `GT` -> `>` (1) | `>=` (longer) | `GE(">=")` |
| 23 | `_limit` | `WHITESPACE` | ` ` | *(skipped)* |
| 24 | `limit` | `IDENT` -> `limit` (5) | `limit` | `IDENT("limit")` |
| 29 | *(end)* | - | - | `EOF` |

**Seven tokens** plus `EOF`: `IDENT EQ IDENT PLUS INT GE IDENT`.

Two rows carry the whole lesson:

- **Position 21** is maximal munch doing real work. Both `GT` and `GE` match at that position. Take the *longest*, not the first one listed, and `>=` stays whole. This is CTQ 3: had the lexer emitted `GT` then `EQ`, the parser would see `a > = b`, which matches no production, and the error would surface as a mystifying *parse* error several stages away from the actual bug. Fix errors where the information still exists.
- **Position 0** is CTQ 2. The identifier pattern is `[A-Za-z_][A-Za-z0-9_]*`, whose second half admits digits, so the match runs to the end of `count2`, six characters, not four. There is no point at which the scanner "notices" the `2` and stops, because stopping early would not be the longest match. The same mechanism is why `iffy` is one `IDENT` and not `IF` followed by `IDENT("fy")`: `IDENT` matches four characters where `IF` matches only two.

Notice what the table does *not* contain: any decision about meaning. The scanner never asks whether `count2` was declared, or whether adding an `INT` to an `IDENT` type-checks. It only asks "how far does a pattern reach from here?", which is precisely why a regular expression is enough to do this job, and why the next stage needs a grammar instead.


> **Watch out!** The maximal munch rule always takes the *longest* possible match at the current position, not the first pattern that matches. This means `>=` is always one token, never two, and `iffy` is always one identifier, never the keyword `if` followed by `fy`. If your hand tokenization ever splits a run of identifier-legal characters mid-stream, you have violated maximal munch.

---

