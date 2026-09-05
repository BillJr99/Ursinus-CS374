<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374-Fall2026/gh-pages/_pages/Activities/liascript-tokensscanning.md or locally via https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374-Fall2026/gh-pages/_pages/Activities/liascript-tokensscanning.md

import: https://raw.githubusercontent.com/liascript/CodeRunner/master/README.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

# Tokens and Scanning: Building a Lexer

A compiler reads your program as one long stream of characters.  Its first job is to decide where one meaningful piece of text ends and the next begins, the way a spell-checker splits a sentence into words before it can flag any of them.  The program that does this job is the **lexer**, also called the scanner.  It groups characters into tokens, the smallest named units of a program: a number, a keyword, an operator.  Every later stage of the compiler works on tokens, not on characters, so nothing else can start until this step is done.

## Learning Goals

By the end of this activity, you will be able to:

- Define the structure of a token (type, lexeme, position) and explain the lexer's contract with the parser downstream
- Apply the maximal munch rule and priority ordering to resolve ambiguous tokenizations by hand and predict the output token stream for a given input string
- Implement a table-driven lexer in Python that uses an ordered token specification, a master regex, and `re.finditer` to emit a typed token stream with line and column positions
- Identify and handle lexer error conditions (illegal characters, unterminated strings) and explain why an error recovery strategy must be chosen deliberately
- Construct a token specification (TOKEN_SPEC) for a new language, ordering rules correctly to enforce keyword priority over identifier patterns

Today you build a working lexer, the first stage of your project pipeline.  It turns raw characters into a stream of typed tokens using only the regular-language tools from the *Regular Expressions* and *Finite Automata* activities.  The activity runs in four steps: what a token is, the two scanning rules (maximal munch and priority), a complete Python lexer, and finally error handling and positions.

> **Before You Begin:** This activity assumes you can:
> - Write Python classes with `__init__` and methods
> - Use Python's `re` module for regular expressions at a basic level
> - Understand what a token is (a named unit of source text like NUMBER or IDENTIFIER)
> If any of these feel shaky, review them first.

---

## Directions and Group Roles

Work in your POGIL team with your rotated roles (**Manager**, **Recorder**, **Presenter**, **Reflector**).  Think each model and question through on your own first, then talk it over with your group.  The Recorder posts your answers to the Class Activity Questions discussion board.  The Presenter reports out wherever you disagreed or found another approach.  After class, respond to the reflection prompt on your own in your notebook.

---

# Part I: Tokens and Rules

## 1.  The Lexer's Contract

A token has three parts: a type, a lexeme, and a position.  The type names the kind of thing the lexer found, such as `NUMBER` or `IDENT`.  The lexeme is the exact text it matched.  The position says where that text sits in the source file.  Put together, `(NUMBER, "42", line 3)` is one token.  Each token type is described by a regular expression, which is why a lexer has exactly the power of a finite automaton and no more.

The lexer's contract with the parser (the stage that comes next) has two halves.  The lexer delivers a stream of tokens.  It also absorbs everything the parser should never see: whitespace, comments, and the raggedness of raw characters.

Two rules settle every case where more than one pattern could match at the current position.  The first rule is **maximal munch**: take the longest match.  So `<=` is one token, not `<` followed by `=`, and `forty` is one identifier, not the keyword `for` followed by `ty`.  The second rule is priority: when two matches have the same length, the pattern listed first wins.  A keyword is a word the language reserves, like `if` or `while`.  An identifier is a name the programmer chose, like `count2` or `limit`.  The lexeme `if` matches both the keyword pattern and the identifier pattern at the same length.  It becomes a keyword either because keywords are listed before identifiers, or because the lexer matches it as an identifier and then looks it up in a keyword table.

---

## Model 1: Be the Lexer

Before you write any code, play the lexer yourself on one line of source text.  Walk through the text character by character and decide where each token begins and ends.  The hard part is not what the text means.  The hard part is the boundaries: is `count2` one token or two, and is `>=` one token or two?  Deciding these cases by hand shows why the regex rules you write later have to be the way they are.

Tokenize by hand: `count2 = count2 + 12 >= limit`

### Critical Thinking Questions

1.  Produce the token list (type and lexeme for each).  How many tokens did you get?  Where did teams differ?
2.  Apply maximal munch to `count2`.  Why is it one identifier rather than the identifier `count` followed by the number `2`?  Which rule decides, and what identifier regex makes it so?
3.  `>=` must not become `>` then `=`.  Describe the bug a parser would face downstream if the lexer split it, and state the general principle about where to fix errors in a pipeline.
4.  Should the lexer reject `12abc`, or emit `12` then `abc` and let the parser complain?  Defend a position.  Real languages differ, and your project must choose.


> The worked answers to this session's models are in the **Answer Key** at the end of this page.  Attempt them with your team first.

# Part II: The Lexer in Code

## 2.  A Complete Tokenizer

You met the master-alternation trick in Part 4 of the *Regex Workshop* lab.  There it showed that named groups let one pattern carry many alternatives.  Here it becomes a real lexer: a token specification stored as data, one master pattern built from that data, and a generator that yields typed tokens with positions, plus an error path.  Positions and errors are what separate a regex demo from a lexer.  The parser needs both when it has to tell a student where their program went wrong.

This code is the seed of your Lexer assignment and of your project.

---

## Code Cell

The lexer below turns the hand rules from Model 1 into Python.  It joins every token regex into one big alternation with `|`.  Python's regex engine then scans the source in a single left-to-right pass: at each position it tries the alternatives in order, takes the first one that matches, and moves on.  The order of entries in `TOKEN_SPEC` decides priority, and nothing else does.

> **Watch out!**  Whitespace is listed in `TOKEN_SPEC` as `SKIP` and is consumed without producing a token.  If you leave out the whitespace pattern, the `MISMATCH` catch-all fires on every space and buries your real error messages in noise.  Check that spaces and tabs are handled before you test with real programs.

```python
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

### Reading the Code

- `TOKEN_SPEC` is an ordered list, and that order is the priority rule from Part I in
  executable form.  `KEYWORD` comes before `IDENT`, so `if` is a keyword.  `GE`, `LE`,
  `EQ`, and `NE` come before `ASSIGN`, `GT`, and `LT`, so `>=` is one token rather than two.
- `MASTER` joins every pattern into one alternation with named groups.  Python's
  alternation is first-match, not longest-match.  The engine does not measure lengths
  for you, so you get maximal munch here by ordering the patterns.  Put `LT` before
  `LE` and `<=` quietly becomes two tokens.
- `m.lastgroup` names the alternative that fired.  That one attribute is the entire
  type dispatch of the lexer.
- `line` and `line_start` are the only mutable state.  The code computes `col` as
  `m.start() - line_start + 1`, which is why the column resets at every newline.
  Track this yourself and you get error messages a person can act on.
- `tokenize` is a generator: it yields tokens one at a time instead of building a
  list.  The parser can start work before the whole file is scanned, and a syntax
  error can stop the scan early.
- `MISMATCH` is last and matches `.`, so the scanner always makes progress and always
  has something specific to complain about.

> **Watch out!**  `NUMBER` uses `\d+(\.\d+)?`, which contains an *unnamed* capture
> group.  It happens to work here because `m.lastgroup` reports the last *named*
> group.  Nesting an extra capture inside a named alternative is still a habit that
> will bite you later.  Write `(?:\.\d+)?` instead, and keep every helper group
> non-capturing.

### Try It Yourself

This `TOKEN_SPEC` is missing a token type your language needs.  Run the tests and
watch what a missing pattern does to a perfectly reasonable line of source.  Then add
the pattern in the right place.

```python
import re
from collections import namedtuple

Token = namedtuple("Token", ["type", "lexeme", "line", "col"])

TOKEN_SPEC = [
    ("NUMBER",   r"\d+(?:\.\d+)?"),
    ("KEYWORD",  r"\b(?:if|else|while|let|print)\b"),
    ("IDENT",    r"[A-Za-z_][A-Za-z0-9_]*"),
    # TODO 1: a STRING token, a double quote to the next double quote.
    #         Where must it go in this list, and why does it matter?
    ("GE", r">="), ("LE", r"<="), ("EQ", r"=="), ("NE", r"!="),
    ("ASSIGN", r"="), ("GT", r">"), ("LT", r"<"),
    ("PLUS", r"\+"), ("MINUS", r"-"), ("STAR", r"\*"), ("SLASH", r"/"),
    ("LPAREN", r"\("), ("RPAREN", r"\)"),
    ("SEMI", r";"), ("NEWLINE", r"\n"), ("SKIP", r"[ \t]+"),
    ("COMMENT", r"#[^\n]*"),
    ("MISMATCH", r"."),
]
MASTER = re.compile("|".join(f"(?P<{n}>{p})" for n, p in TOKEN_SPEC))

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
            yield Token("ERROR", lexeme, line, col)
        else:
            yield Token(kind, lexeme, line, col)

CASES = [
    ('let x = 1;',              "the baseline: should scan cleanly"),
    ('let s = "hi there";',     "needs STRING; without it, watch it shatter"),
    ('if x != 1 print x;',      "!= must stay one token"),
    ('let n = 3.14;',           "a float is ONE number token"),
]

for src, note in CASES:
    print(f"\n{src!r}   ({note})")
    for t in tokenize(src):
        flag = "   <-- ERROR" if t.type == "ERROR" else ""
        print(f"    line {t.line} col {t.col:2}  {t.type:8} {t.lexeme!r}{flag}")
```
@LIA.eval(`["main.py"]`, `none`, `python3 main.py`)

Expected output before your edit: the second case shatters.  It emits `ERROR '"'`,
then `IDENT 'hi'`, `IDENT 'there'`, then another `ERROR`.  After you add `STRING` in
the right place, that line is one token.  Keep this `TOKEN_SPEC`; the Lexer assignment
starts from it.

---

## Model 2: Read the Machine You Built

The lexer runs.  Now read it as a system and connect each design decision back to the theory.  You already know the code works.  The goal here is to understand why it is built the way it is, so you can change it with confidence when the rules change on your project.

### Critical Thinking Questions

5.  The master pattern joins every token regex with `|` into one alternation.  Connect this single move to Thompson's construction from the automata module: what machine, conceptually, does `finditer` run?
6.  Why must `GE` (`>=`) appear before `GT` (`>`) in the spec, given how Python's `re` alternation chooses among same-position matches?  Design the two-character experiment that proves the necessity, run it, and report.
7.  Keywords are matched with `\b(if|else|...)\b` *before* `IDENT`.  Remove the `\b` anchors mentally: what goes wrong with the identifier `iffy`?  Which scanning rule did the anchors enforce?

> **Watch out!**  Keywords must always appear *before* the general identifier pattern in your `TOKEN_SPEC`.  If `IDENT` comes first, the regex engine matches `if` as an identifier and never reaches the KEYWORD rule, because Python's `re` alternation returns the first match, not the longest.  Get this order wrong and your lexer accepts `if` as a variable name, which breaks every conditional in your language without any error message.

8.  The `MISMATCH` catch-all turns unknown characters into a `SyntaxError` with line and column.  Feed the lexer a `$` and verify the message.  Why is reporting *position* a kindness worth the bookkeeping?

---

## Model 3: Peek/Advance Lexer Interface

The raw `tokenize()` generator is fine for printing, but a parser needs more control.  It must look at the next token before it decides whether to consume it.  A parser therefore never calls `tokenize()` directly.  It uses three operations: **peek** returns the next token without consuming it, **advance** consumes the next token and returns it, and **expect** consumes the next token and raises an error if its type is not the one the parser asked for.  The `Lexer` class below wraps the generator and buffers exactly one token to provide these three methods.  The parser will use only this interface, and the generator becomes an implementation detail.

```python
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

9.  The `Lexer` class stores exactly one token in `_buf`.  Why is one token enough?  Describe a parsing situation that would require *two* tokens of lookahead and explain how you would extend `_buf` to handle it.
10. `peek()` is a pure read: it does not change the lexer's state.  Why is that guarantee important for a parser that makes decisions (for example, "is the next token a `(`?") before consuming?
11. `expect()` raises `SyntaxError` if the type does not match.  Compare this to a design where `expect()` returns `None` on mismatch instead of raising.  What does the raising version give the parser author that the silent-return version does not?

---

## Model 4: Real-World Lexer Features, String Literals

The lexer so far handles numbers, keywords, and operators.  Real programs also contain **string literals** such as `"hello world"`, and strings bring a new problem: the text inside the quotes can contain almost anything, including characters that normally end a token.  An escape sequence is a backslash followed by one character that stands for something else, such as `\"` for a quote, `\\` for a backslash, or `\n` for a newline.  A naive pattern like `"[^"]*"` stops at the first quote it sees, so it breaks on `"say \"hi\""`.  The correct pattern uses a negative lookbehind or a two-alternative trick: inside the delimiters, match either an escaped character or any character that is neither a quote nor a backslash.  This model adds that STRING pattern and then looks at what happens when a string is never closed.

```python
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

12.  The STRING pattern is `"(?:[^"\\]|\\.)*"`.  The two alternatives inside the group are `[^"\\]` (any char except quote or backslash) and `\\.` (backslash followed by any char).  Explain in your own words why both alternatives are needed: what string would fail if only the first alternative existed?
13.  Run the unterminated-string test.  The lexer does not raise a clean error; it silently produces MISMATCH tokens.  Propose a pattern change or post-processing step that would detect an unterminated string and report it with line and column.
14. `unescape()` processes `\"`, `\\`, `\n`, and `\t`.  List two other escape sequences that a production language would need, and describe any ordering constraint that matters when applying multiple replacements.

---

# Part III: Hardening and Handoff (at home)

## 3.  From Demo to Component

Your assignment turns this lexer into a component that your December language will import unchanged.  It adds string literals with escapes, token specifications loaded from JSON, a `peek`/`advance` interface for the parser, and a test suite.  The interface matters as much as the code.  The parser you write next month will call `peek()` to look at the next token without consuming it and `advance()` to consume it, and nothing else.

The parser asks the lexer for the next token and receives `Token(NUMBER, "12", 4, 7)`.  The information the parser will use for its *grammar* decisions is:

[(X)] The type NUMBER; the lexeme and position ride along for evaluation and error messages
[( )] The lexeme "12" alone
[( )] The line number, to enforce indentation
[( )] All fields equally, at every decision

---

# Check Your Understanding

A lexer's job, stated precisely, is to:

[(X)] Turn a character stream into a token stream, discarding whitespace and comments
[( )] Turn a token stream into a tree
[( )] Check that the program is syntactically legal
[( )] Resolve names to their declarations

---

Given the input `12foo`, a lexer with patterns for NUMBER and IDENT will most likely produce:

[(X)] NUMBER `12` followed by IDENT `foo`, because each match starts fresh at the current position
[( )] A single IDENT `12foo`
[( )] A lexical error, since the two patterns overlap
[( )] A single NUMBER `12`, discarding the rest

---

Keywords like `if` and `while` are usually recognized by:

[(X)] Matching them as identifiers first, then checking the lexeme against a keyword set
[( )] Listing each keyword as its own regex before the identifier pattern, which also works but scales worse
[( )] The parser rather than the lexer
[( )] A separate pass over the token stream

---

Lexers use regular grammars and parsers use context-free grammars because:

[(X)] Token structure needs no nesting, and the weaker class buys a much faster recognizer
[( )] Regular grammars are easier to write by hand
[( )] Context-free grammars cannot describe identifiers
[( )] It is a historical convention with no technical reason

---

## 4.  Exercises

1.  *String literals.*  Add a `STRING` token for double-quoted strings without escapes (`"hello"`), then extend it to allow `\"` inside.  Write two new spec lines and three tests for each.  Report which ordering pitfalls you hit.
2.  *Peek and advance.*  Wrap the generator in a `Lexer` class that exposes `peek()` and `advance()` (hint: buffer one token).  Demonstrate it with a loop that prints the tokens two different ways and produces identical streams.
3.  *Configurable spec.*  Move `TOKEN_SPEC` into a JSON file and load it at startup.  Add a configuration option for the comment character.  This externalization is a project requirement arriving early.
4.  *Error recovery.*  Instead of raising on the first bad character, collect all lexical errors and report them together at the end.  Discuss in two sentences which behavior serves a programmer better, and when.
5.  *Cross-language tourism.*  Run your mental lexer on a Python snippet.  What token must a Python-style lexer emit that ours never does?  (Indentation: INDENT and DEDENT tokens, manufactured from whitespace.)  Write one paragraph on how that bridges the lexer-parser divide.

---

## Practice: Allison, Ch. 2 §2.4: Hand-Traced Tokenization

These exercises build your confidence in the maximal munch rule and token ordering.  You tokenize real programs on paper before you write code, which connects the formal lexer model to the parsing pipeline you will build.

> *Exercises adapted from topics covered in *Foundations of Computing* by Chuck Allison (Fresh Sources, Inc.), used under the [MIT License](https://github.com/chuckallison/foundations-of-computing/blob/main/LICENSE).*

The lexer applies patterns in order, using maximal munch.  For the input `x>=5`, if `IDENT` is listed before `GE` (`>=`) in TOKEN_SPEC, the result is:

[( )] `IDENT("x"), GE, INT(5)`: the lexer is smart enough to lookahead and reorder
[(X)] `IDENT("x"), GT, EQ, INT(5)`: `>=` is never recognized because `IDENT` greedily consumed `x`
[( )] Undefined behavior; the order doesn't matter
[( )] A `LexError` because ambiguous input

Maximal munch means the lexer matches the longest possible token.  For input `<=`, if both `LT` (`<`) and `LE` (`<=`) are valid patterns:

[( )] The lexer tries `LT` first and succeeds immediately
[(X)] The lexer finds both `LT` and `LE` as possibilities and chooses `LE` (the longer match)
[( )] The lexer raises an ambiguity error
[( )] It depends on which is listed first in TOKEN_SPEC

1.  **Tokenize by hand (maximal munch rules).**
   - Input: `x>=5+2`
   - Rules (in order): `IDENT` matches `[a-z]+`, `GE` matches `>=`, `PLUS` matches `+`, `INT` matches `\d+`
   - Trace through the lexer: at each position, which pattern matches?  Show the token stream produced.
   - Verify: does `>=` get tokenized as one `GE` token or two (`GT, EQ`)?  Why?

2.  **Operator ordering matters.**
   - Suppose TOKEN_SPEC lists `EQEQ` (`==`) AFTER `EQ` (`=`).  Input: `x==5`
   - Tokenize by hand using this bad ordering.  What goes wrong?
   - Now reorder TOKEN_SPEC to list `EQEQ` BEFORE `EQ`, and re-tokenize.  Show the correct stream.
   - Conclusion: explain in two sentences why longer operators must come first.

3.  **String literals with escapes.**
   - Input: `"hello\nworld"`
   - Your STRING pattern is `"(?:[^"\\]|\\.)*"`.  Trace through each character:
     - Position 0: `"`, starts the string
     - Position 1-5: `hello`, match `[^"\\]` (not quote or backslash)
     - Position 6-7: `\n`, match `\\.` (backslash followed by any char)
     - Position 8-12: `world`, match `[^"\\]` again
     - Position 13: `"`, end the string
   - Confirm: the entire 14-character string is one STRING token, not broken up.

4.  **Identifying token breaks.**
   - Input: `let x = 42;`
   - Tokenize by hand with TOKEN_SPEC: `LET`, `IDENT`, `EQ`, `INT`, `SEMICOLON`, `WHITESPACE` (skip)
   - At each position, show which pattern matches and mark token boundaries.  Verify: `42` is one INT token, not two separate characters.

5.  **Why comments are deleted, not tokenized.**
   - Input: `x = 1 # this is a comment`
   - Tokenize, showing: (a) the tokens produced (without the comment), (b) why the lexer never produces a COMMENT token (it matches and skips).
   - Connect to Model 2 (the skipping logic): if a token's type is "COMMENT" or "WHITESPACE", the lexer silently discards it.  Why is this the right design?

---

## Reflection Prompt

In your notebook: the lexer absorbs whitespace and comments so later stages never see them.  What is the analogous role on a human team (the person whose filtering work is invisible exactly when done well), and what does the analogy suggest about how such work should be valued?

---

## 5.  Further Reading

- Douglas Thain.  *Introduction to Compilers and Language Design*, Chapter 3.
- Robert Nystrom.  *Crafting Interpreters*, "Scanning" (online).
- Python `re` documentation on named groups and `finditer`.

---

Up next: the *Abstract Syntax Trees* activity builds the structure your parser will produce.  This lexer is the heart of the Lexer assignment.

# Answer Key

Work the models above with your team before reading these.  Each answer matches a Critical Thinking Question the session poses.  Seeing the answer first turns the exercise into transcription.

### Worked Example: maximal munch, position by position

Do CTQ 1 as a team before reading this.  Then check the boundaries.  The interesting rows are the ones where more than one pattern matches and the *longest* wins.

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

- Position 21 is maximal munch doing real work.  Both `GT` and `GE` match at that position.  Take the *longest*, not the first one listed, and `>=` stays whole.  This is CTQ 3.  Had the lexer emitted `GT` then `EQ`, the parser would see `a > = b`, which matches no production.  The error would surface as a confusing *parse* error several stages away from the real bug.  Fix errors where the information still exists.
- Position 0 is CTQ 2.  The identifier pattern is `[A-Za-z_][A-Za-z0-9_]*`.  Its second half admits digits, so the match runs to the end of `count2`: six characters, not four.  The scanner never "notices" the `2` and stops, because stopping early would not be the longest match.  The same mechanism is why `iffy` is one `IDENT` and not `IF` followed by `IDENT("fy")`: `IDENT` matches four characters where `IF` matches only two.

Notice what the table does *not* contain: any decision about meaning.  The scanner never asks whether `count2` was declared, or whether adding an `INT` to an `IDENT` type-checks.  It only asks "how far does a pattern reach from here?"  That is why a regular expression is enough to do this job, and why the next stage needs a grammar instead.


> **Watch out!**  The maximal munch rule always takes the *longest* possible match at the current position, not the first pattern that matches.  So `>=` is always one token, never two, and `iffy` is always one identifier, never the keyword `if` followed by `fy`.  If your hand tokenization ever splits a run of identifier-legal characters mid-stream, you have violated maximal munch.

---

