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
> - Understand what a token is (a named unit of source text like INT or IDENT)
> If any of these feel shaky, review them first.

---

## Directions and Group Roles

Work in your POGIL team with your rotated roles (**Manager**, **Recorder**, **Presenter**, **Reflector**).  Think each model and question through on your own first, then talk it over with your group.  The Recorder posts your answers to the Class Activity Questions discussion board.  The Presenter reports out wherever you disagreed or found another approach.  After class, respond to the reflection prompt on your own in your notebook.

---

# Part I: Tokens and Rules

## 1.  The Lexer's Contract

A token has three parts: a type, a lexeme, and a position.  The type names the kind of thing the lexer found, such as `INT` or `IDENT`.  The lexeme is the exact text it matched.  The position says where that text sits in the source file.  Put together, `(INT, "42", line 3)` is one token.  Each token type is described by a regular expression, which is why a lexer has exactly the power of a finite automaton and no more.

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

The master-alternation trick rests on named groups, which the next cell shows on one line: a name on each alternative lets one pattern carry many alternatives and still report which one matched.  Here it becomes a real lexer: a token specification stored as data, one master pattern built from that data, and a generator that yields typed tokens with positions, plus an error path.  Positions and errors are what separate a regex demo from a lexer.  The parser needs both when it has to tell a student where their program went wrong.

This code is the seed of your Lexer assignment and of your project.

---

## Named Groups in One Line

A plain group `(...)` captures text you can read back by number.  A named group, `(?P<name>...)`, captures the same text and lets you read it back by name.  Every name used below has a job: `group("key")` reads one capture, `groupdict()` returns every capture as a dictionary, and `lastgroup` names the last group that matched.

```python
import re
import traceback

# Two named groups: key and value, around an equals sign.
SETTING = re.compile(r"(?P<key>[A-Za-z_]\w*)\s*=\s*(?P<value>\S+)")

try:
    m = SETTING.fullmatch("port = 8080")
    print(m.group("key"), "|", m.group("value"), "|", m.lastgroup)
    print(m.groupdict())
except Exception as e:
    print(f"[tokens:named_groups] {e}")
    traceback.print_exc()
```
@LIA.eval(`["main.py"]`, `none`, `python3 main.py`)

You should see:

```text
port | 8080 | value
{'key': 'port', 'value': '8080'}
```

Here both groups match, so `lastgroup` is simply the last one, `value`.  The lexer below puts each token type in its own named group and joins them with `|`.  At any position only one alternative matches, so `lastgroup` names the token type that fired.

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
    ("FLOAT",    r"\d+\.\d+"),
    ("INT",      r"\d+"),
    ("KEYWORD",  r"\b(if|else|while|let|print)\b"),
    ("IDENT",    r"[A-Za-z_][A-Za-z0-9_]*"),
    ("GE",       r">="), ("LE", r"<="), ("EQEQ", r"=="), ("NE", r"!="),
    ("EQ",       r"="),
    ("GT",       r">"), ("LT", r"<"),
    ("PLUS",     r"\+"), ("MINUS", r"-"), ("STAR", r"\*"), ("SLASH", r"/"),
    ("LPAREN",   r"\("), ("RPAREN", r"\)"),
    ("LBRACE",   r"\{"), ("RBRACE", r"\}"),
    ("SEMICOLON", r";"),
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
  `EQEQ`, and `NE` come before `EQ`, `GT`, and `LT`, so `>=` is one token rather than two.
  `FLOAT` comes before `INT` for the same reason: listed after it, `3.14` would lex as `INT 3`
  and leave `.14` behind.
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

> **Watch out!**  If a token pattern needs a helper group, such as an optional
> fraction `\d+(\.\d+)?`, the plain `(...)` is an *unnamed* capture.  It happens to
> work with `m.lastgroup`, which reports the last *named* group, but nesting an extra
> capture inside a named alternative is a habit that will bite you later.  Write
> `(?:\.\d+)?` instead, and keep every helper group non-capturing.

- The token names match the Lexer assignment: `EQ` is `=`, `EQEQ` is `==`, `SEMICOLON`
  is `;`, and numbers are `INT` or `FLOAT`.  This deck folds every keyword into one
  `KEYWORD` type for brevity; the Lexer assignment gives each keyword its own type.

### Try It Yourself

This `TOKEN_SPEC` is missing a token type your language needs.  Run the tests and
watch what a missing pattern does to a perfectly reasonable line of source.  Then add
the pattern in the right place.

```python
import re
from collections import namedtuple

Token = namedtuple("Token", ["type", "lexeme", "line", "col"])

TOKEN_SPEC = [
    ("FLOAT",    r"\d+\.\d+"),
    ("INT",      r"\d+"),
    ("KEYWORD",  r"\b(?:if|else|while|let|print)\b"),
    ("IDENT",    r"[A-Za-z_][A-Za-z0-9_]*"),
    # TODO 1: a STRING token, a double quote to the next double quote.
    #         Where must it go in this list, and why does it matter?
    ("GE", r">="), ("LE", r"<="), ("EQEQ", r"=="), ("NE", r"!="),
    ("EQ", r"="), ("GT", r">"), ("LT", r"<"),
    ("PLUS", r"\+"), ("MINUS", r"-"), ("STAR", r"\*"), ("SLASH", r"/"),
    ("LPAREN", r"\("), ("RPAREN", r"\)"),
    ("SEMICOLON", r";"), ("NEWLINE", r"\n"), ("SKIP", r"[ \t]+"),
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
        print(f"    line {t.line} col {t.col:2}  {t.type:9} {t.lexeme!r}{flag}")
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

### Check Your Answer: Order Is Priority

Answer CTQ 6 and CTQ 7 before you run this.  The cell below runs both experiments: the same input through two specs that differ only in order, and the same input through two keyword patterns that differ only in the `\b` anchors.

```python
import re
import traceback

try:
    GOOD = re.compile(r"(?P<GE>>=)|(?P<GT>>)|(?P<EQ>=)|(?P<IDENT>[A-Za-z_]\w*)|(?P<INT>\d+)|(?P<SKIP>\s+)")
    BAD  = re.compile(r"(?P<GT>>)|(?P<GE>>=)|(?P<EQ>=)|(?P<IDENT>[A-Za-z_]\w*)|(?P<INT>\d+)|(?P<SKIP>\s+)")
    for name, pat in (("GE first", GOOD), ("GT first", BAD)):
        print(name, [(m.lastgroup, m.group()) for m in pat.finditer("x >= 5") if m.lastgroup != "SKIP"])

    NOB = re.compile(r"(?P<KEYWORD>if|else|while)|(?P<IDENT>[A-Za-z_]\w*)|(?P<SKIP>\s+)")
    WB  = re.compile(r"(?P<KEYWORD>\b(?:if|else|while)\b)|(?P<IDENT>[A-Za-z_]\w*)|(?P<SKIP>\s+)")
    for name, pat in (("no \\b", NOB), ("with \\b", WB)):
        print(name, [(m.lastgroup, m.group()) for m in pat.finditer("iffy")])
except Exception as e:
    print(f"[tokens:order_priority] {e}")
    traceback.print_exc()
```
@LIA.eval(`["main.py"]`, `none`, `python3 main.py`)

You should see:

```text
GE first [('IDENT', 'x'), ('GE', '>='), ('INT', '5')]
GT first [('IDENT', 'x'), ('GT', '>'), ('EQ', '='), ('INT', '5')]
no \b [('KEYWORD', 'if'), ('IDENT', 'fy')]
with \b [('IDENT', 'iffy')]
```

### Reading the Code

- `GOOD` and `BAD` hold the same six patterns.  Only the order of `GE` and `GT` differs, and that alone splits `>=` into `GT` then `EQ`.  The engine tried `GT` first, it matched, and `GE` never got a turn.
- Without `\b`, `KEYWORD` matches the first two letters of `iffy` and `IDENT` picks up the leftover `fy`.  The anchors demand a word boundary after the keyword, so the keyword alternative fails at position 0 and `IDENT` takes all four characters.
- Each experiment holds everything fixed except the one thing under test.  That is the shape of a good answer to CTQ 6.

---

## Model 3: Peek/Advance Lexer Interface

The raw `tokenize()` generator is fine for printing, but a parser needs more control.  It must look at the next token before it decides whether to consume it.  A parser therefore never calls `tokenize()` directly.  It uses three operations: **peek** returns the next token without consuming it, **advance** consumes the next token and returns it, and **expect** consumes the next token and raises an error if its type is not the one the parser asked for.  The `Lexer` class below wraps the generator and buffers exactly one token to provide these three methods.  The parser will use only this interface, and the generator becomes an implementation detail.

```python
import re
from collections import namedtuple

Token = namedtuple("Token", ["type", "lexeme", "line", "col"])

TOKEN_SPEC = [
    ("FLOAT",    r"\d+\.\d+"),
    ("INT",      r"\d+"),
    ("KEYWORD",  r"\b(if|else|while|let|print)\b"),
    ("IDENT",    r"[A-Za-z_][A-Za-z0-9_]*"),
    ("GE",       r">="), ("LE", r"<="), ("EQEQ", r"=="), ("NE", r"!="),
    ("EQ",       r"="),
    ("GT",       r">"), ("LT", r"<"),
    ("PLUS",     r"\+"), ("MINUS", r"-"), ("STAR", r"\*"), ("SLASH", r"/"),
    ("LPAREN",   r"\("), ("RPAREN", r"\)"),
    ("LBRACE",   r"\{"), ("RBRACE", r"\}"),
    ("SEMICOLON", r";"),
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
    print(f"peeked {tok.type:9} -> consumed {consumed.lexeme!r}")

print()
print("=== Style 3: expect a specific sequence ===")
lx = Lexer(source)
kw   = lx.expect("KEYWORD")
name = lx.expect("IDENT")
eq   = lx.expect("EQ")
val  = lx.expect("INT")
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
    ("FLOAT",    r"\d+\.\d+"),
    ("INT",      r"\d+"),
    ("STRING",   r'"(?:[^"\\]|\\.)*"'),      # <-- new: handles escape sequences
    ("KEYWORD",  r"\b(if|else|while|let|print)\b"),
    ("IDENT",    r"[A-Za-z_][A-Za-z0-9_]*"),
    ("GE",       r">="), ("LE", r"<="), ("EQEQ", r"=="), ("NE", r"!="),
    ("EQ",       r"="),
    ("GT",       r">"), ("LT", r"<"),
    ("PLUS",     r"\+"), ("MINUS", r"-"), ("STAR", r"\*"), ("SLASH", r"/"),
    ("LPAREN",   r"\("), ("RPAREN", r"\)"),
    ("LBRACE",   r"\{"), ("RBRACE", r"\}"),
    ("SEMICOLON", r";"),
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

ESCAPES = {'"': '"', "\\": "\\", "n": "\n", "t": "\t"}

def unescape(raw):
    """Strip surrounding quotes and decode escapes in ONE left-to-right pass."""
    body = raw[1:-1]
    return re.sub(r"\\(.)", lambda m: ESCAPES.get(m.group(1), m.group(0)), body)

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
print("=== One pass versus chained replace on c:\\\\new ===")
try:
    path = r'"c:\\new"'
    print("one pass:       ", repr(unescape(path)))
    print("chained replace:", repr(path[1:-1].replace("\\\\", "\\").replace("\\n", "\n")))
except Exception as e:
    print(f"[tokens:unescape] {e}")
    import traceback; traceback.print_exc()

print()
print("=== What happens with an unterminated string? ===")
bad = 'let x = "oops;'
try:
    tokens = list(tokenize(bad))
    print("Tokens produced:", tokens)
except SyntaxError as e:
    print(f"SyntaxError: {e}")
    print("No STRING pattern matched, so the quote fell through to MISMATCH:")
    print("the error names a stray character, not an unterminated string.")
```
@LIA.eval(`["main.py"]`, `none`, `python3 main.py`)

You should see:

```text
=== All tokens ===
Token(type='KEYWORD', lexeme='let', line=2, col=1)
Token(type='IDENT', lexeme='greeting', line=2, col=5)
Token(type='EQ', lexeme='=', line=2, col=14)
Token(type='STRING', lexeme='"hello, world"', line=2, col=16)
Token(type='SEMICOLON', lexeme=';', line=2, col=30)
Token(type='KEYWORD', lexeme='let', line=3, col=1)
Token(type='IDENT', lexeme='escaped', line=3, col=5)
Token(type='EQ', lexeme='=', line=3, col=14)
Token(type='STRING', lexeme='"say \\"hi\\" now"', line=3, col=16)
Token(type='SEMICOLON', lexeme=';', line=3, col=32)
Token(type='KEYWORD', lexeme='let', line=4, col=1)
Token(type='IDENT', lexeme='newlines', line=4, col=5)
Token(type='EQ', lexeme='=', line=4, col=14)
Token(type='STRING', lexeme='"line1\\nline2"', line=4, col=16)
Token(type='SEMICOLON', lexeme=';', line=4, col=30)
Token(type='KEYWORD', lexeme='print', line=5, col=1)
Token(type='IDENT', lexeme='greeting', line=5, col=7)
Token(type='SEMICOLON', lexeme=';', line=5, col=15)

=== String values after unescaping ===
  raw:       "hello, world"
  unescaped: 'hello, world'
  raw:       "say \"hi\" now"
  unescaped: 'say "hi" now'
  raw:       "line1\nline2"
  unescaped: 'line1\nline2'

=== One pass versus chained replace on c:\\new ===
one pass:        'c:\\new'
chained replace: 'c:\new'

=== What happens with an unterminated string? ===
SyntaxError: line 1, col 9: unexpected '"'
No STRING pattern matched, so the quote fell through to MISMATCH:
the error names a stray character, not an unterminated string.
```

> **Watch out!**  The chained version is not wrong because of a typo.  Its first `replace` turns `\\` into one real backslash, and its second `replace` then reads that new backslash, plus the `n` after it, as the start of `\n`.  One replacement fed the next.  The one-pass `re.sub` consumes each backslash together with the character after it, so nothing it produces is ever scanned again.  When you read the output, remember that `repr` shows a real backslash doubled.  So `'c:\\new'` is `c`, `:`, one backslash, then `new`, which is correct, while `'c:\new'` holds a real newline character.

### Critical Thinking Questions

12.  The STRING pattern is `"(?:[^"\\]|\\.)*"`.  The two alternatives inside the group are `[^"\\]` (any char except quote or backslash) and `\\.` (backslash followed by any char).  Explain in your own words why both alternatives are needed: what string would fail if only the first alternative existed?
13.  Run the unterminated-string test.  The lexer does raise, but at the stray quote and with a generic message, because the quote fell through to `MISMATCH`.  Propose a pattern change or post-processing step that would detect an unterminated string and report it as one, with line and column.
14. `unescape()` processes `\"`, `\\`, `\n`, and `\t`.  List two other escape sequences that a production language would need, and describe any ordering constraint that matters when applying multiple replacements.  A single `re.sub` pass, as in the cell above, avoids the ordering problem entirely.

---

# Part III: Hardening and Handoff (at home)

## 3.  From Demo to Component

Your assignment turns this lexer into a component that your December language will import unchanged.  It adds string literals with escapes, token specifications loaded from JSON, a `peek`/`advance` interface for the parser, and a test suite.  The interface matters as much as the code.  The parser you write next month will call `peek()` to look at the next token without consuming it and `advance()` to consume it, and nothing else.

The parser asks the lexer for the next token and receives `Token(INT, "12", 4, 7)`.  The information the parser will use for its *grammar* decisions is:

[(X)] The type INT; the lexeme and position ride along for evaluation and error messages
[( )] The lexeme "12" alone
[( )] The line number, to enforce indentation
[( )] All fields equally, at every decision

### Build It Yourself: How the Steps Work

The demos above each ran in their own box, and each box started over.  A component cannot work that way, so from here on you build one real set of files on your own machine.  Each step below adds one small piece, you type that piece in, and you run one check before you move on.  When you finish, you have a working lexer that you wrote: `lexer.py`, `token_spec.json`, `token_spec_alt.json`, and `test_lexer.py`.  These are the code files the Lexer assignment asks for, so you are building your assignment as you go.

Make a folder for the work and run every command from inside it:

```bash
mkdir cs374-lexer
cd cs374-lexer
```

Here is how to read each step:

- **The first comment in a code block is a direction, not code.**  It names the file and says where the lines go, such as `# lexer.py: add just above the line with ...`.  Do not type that comment.  Type everything under it.
- **A blank such as `____1____` is yours to work out.**  It stands for one or more lines that you write.  Try it first, and then compare with **Lexer Build: Blanks** in the Answer Key at the end of this page.
- **These blocks have no run button.**  Each one depends on the file you have built so far, and only your machine has that file.  Run the commands in your terminal.  On some machines the command is `python` rather than `python3`.
- **`scratch.py` is for checks only.**  Replace its contents at each check.  You do not submit it.
- **Stop when a check does not match.**  Each check tests only what its step added, so the bug is almost always in the lines you just typed.

Your component uses the assignment's names, so a few things change from the Part II demo:

| Part II demo | Your component | Why it changes |
|--------------|----------------|----------------|
| `Token` namedtuple with a `lexeme` field | `Token` dataclass with a `value` field | The Lexer assignment's tokens use `value` |
| One `KEYWORD` type | One type per keyword, such as `IF` and `LET` | The parser can ask for `expect("LET")` directly |
| `NE`, `SKIP`, `NEWLINE`, `MISMATCH` | `NEQ`, `WHITESPACE`, and no catch-all rule | Whitespace absorbs newlines, and no rule matching at all is now the error case |
| A master pattern and `finditer` | A loop that tries each rule with `.match(source, pos)` | The loop can name a broken rule in a JSON file and can resume after a bad character |

The demo's ideas all carry over: rule order is priority, a generator yields the tokens, and one buffered token gives you lookahead.

### Build Step 1: The Token

A token is one labeled piece of source text and where it came from.  Part II used a namedtuple.  Here you use a dataclass, because the next assignments read its fields by name and because it gives you a printout and an `==` for free.  You use `json` and `Optional` in later steps, so you can leave them in the imports now.

```python
# lexer.py: start the file with these lines
import json
import re
from dataclasses import dataclass
from typing import Iterator, Optional


@dataclass(frozen=True)
class Token:
    type: str    # the rule name, such as "IDENT"
    value: str   # the raw lexeme, exactly as it appears in the source
    line: int    # 1-indexed line of the first character
    col: int     # 1-indexed column of the first character
```

Check it.

```python
# scratch.py
from lexer import Token

a = Token("INT", "42", 1, 5)
print(a)
print(a == Token("INT", "42", 1, 5), a.type, a.col)
```

Run it:

```bash
python3 scratch.py
```

You should see:

```text
Token(type='INT', value='42', line=1, col=5)
True INT 5
```

15. `frozen=True` makes a token read-only.  Add `a.col = 9` to `scratch.py` and predict what happens before you run it.  `peek()` will hand the same token object to every caller who asks.  Why does that make read-only tokens a good idea?

### Build Step 2: The First Six Rules

Let's start small.  With six rules you can lex `let x = 42;`, and every later rule is one more line in this list.  `(?!\w)` means "not followed by a letter, digit, or underscore."  It does the same job here as the trailing `\b` from CTQ 7.  The `\r` in `WHITESPACE` lets you lex a file saved with Windows line endings.

```python
# lexer.py: add at the end of the file
TOKEN_SPEC = [
    ("WHITESPACE", r"[ \t\r\n]+"),
    ("INT",        r"\d+"),
    ("LET",        r"let(?!\w)"),
    ("IDENT",      r"[a-zA-Z_][a-zA-Z0-9_]*"),
    ("EQ",         r"="),
    ("SEMICOLON",  r";"),
]

# One (name, compiled pattern) pair per rule, in the same order.
____1____
```

Check it.

```python
# scratch.py
from lexer import TOKEN_SPEC, COMPILED_SPEC

print(len(COMPILED_SPEC), COMPILED_SPEC[2][0])
LET = COMPILED_SPEC[2][1]
print(LET.match("let x"))
print(LET.match("lets x"))
```

Run it:

```bash
python3 scratch.py
```

You should see:

```text
6 LET
<re.Match object; span=(0, 3), match='let'>
None
```

16. Model 2's keyword pattern put `\b` on both ends of the keyword.  This rule guards only the end.  Why can it leave off the front?  Think about where `.match(source, pos)` starts and what the previous token already consumed.

### Build Step 3: Track the Line and Column

Part II kept a `line_start` variable and handled newlines as tokens of their own.  Now one `WHITESPACE` match can hold several newlines, so you need a helper that takes any matched text and works out where the next token starts.  Suppose the text is a newline and then two spaces.  The next token sits in column 3 of the new line, after the spaces in columns 1 and 2.

```python
# lexer.py: add at the end of the file
def advance_position(text: str, line: int, col: int) -> tuple[int, int]:
    """Return the (line, col) just past text, given that text starts at (line, col)."""
    newlines = text.count("\n")
    if newlines == 0:
        return line, col + len(text)
    # The new column counts the characters after the LAST newline, plus one.
    return line + newlines, ____2____
```

Check it.

```python
# scratch.py
from lexer import advance_position as a

print(a("let", 1, 1), a("\n  ", 1, 4), a("x\ny\n", 2, 3))
```

Run it:

```bash
python3 scratch.py
```

You should see:

```text
(1, 4) (2, 3) (4, 1)
```

17. This helper must also run for text the lexer skips, such as whitespace and comments.  What goes wrong in your error messages if it runs only for tokens you yield?

### Build Step 4: Find the First Rule That Matches

This helper is the priority rule from Part I, written as a loop.  It stops at the first rule that matches, so list order decides.  The earlier `finditer` demo did this inside one big alternation, and now you can see it happen.

```python
# lexer.py: add at the end of the file
def match_rule(spec, source: str, pos: int):
    """Return (name, match) for the FIRST rule in spec that matches at pos, or None."""
    for name, pattern in spec:
        m = pattern.match(source, pos)
        if m and m.end() > pos:
            return name, m
    return None
```

Check it.

```python
# scratch.py
from lexer import match_rule, COMPILED_SPEC as S

name, m = match_rule(S, "let x", 0)
print(name, repr(m.group()), m.end())
print(match_rule(S, "let x", 3)[0])
print(match_rule(S, "@", 0))
```

Run it:

```bash
python3 scratch.py
```

You should see:

```text
LET 'let' 3
WHITESPACE
None
```

18. Look at `m.end() > pos`.  Your own rules never match empty text, but a JSON file can hold any pattern, and you load those in a later step.  Suppose a rule's pattern is `a*` and the next character is `b`.  What would the lexer do without this test?

### Build Step 5: An Error That Knows Where It Happened

The Part II lexer raised a `SyntaxError` with the position folded into its message.  A parser or a test that wants the column would have to pick it back out of a string.  Here the error stores its facts as attributes and builds the message from them.  The defaults let an error with no position, such as a broken JSON file, use the same class.

```python
# lexer.py: add just above the line with `TOKEN_SPEC = [`
class LexError(Exception):
    """A lexical error, with its position in the source."""

    def __init__(self, message: str, line: int = 0, col: int = 0, text: str = ""):
        self.message = message
        self.line = line
        self.col = col
        self.text = text
        super().__init__(message)

    def __str__(self) -> str:
        return ____3____
```

Your message must read `LexError at line L, col C: message`, with the stored values in place of `L`, `C`, and `message`.  Check it.

```python
# scratch.py
from lexer import LexError

e = LexError("unexpected character '@'", 3, 7, "@")
print(e)
print(e.line, e.col, repr(e.text))
print(LexError("no position"))
```

Run it:

```bash
python3 scratch.py
```

You should see:

```text
LexError at line 3, col 7: unexpected character '@'
3 7 '@'
LexError at line 0, col 0: no position
```

19. The Interpreter assignment prints `Lexical error at line L, col C: <message>`.  Which attributes does it read to build that line, and what would it have to do if `LexError` held only one formatted string?

### Build Step 6: Scan One Token

Now put the helpers to work at a single position.  `scan_one` asks `match_rule` for a rule, turns no match into a `LexError`, and decides whether the text becomes a token.  It always hands back the text it consumed, because the caller must move past skipped text too.

```python
# lexer.py: add at the end of the file
SKIPPED = {"COMMENT", "WHITESPACE"}


def scan_one(spec, source: str, pos: int, line: int, col: int):
    """Return (text consumed at pos, Token or None if that text is skipped)."""
    found = match_rule(spec, source, pos)
    if found is None:
        ch = source[pos]
        raise LexError(f"unexpected character {ch!r}", line, col, ch)
    name, m = found
    text = m.group()
    if name in SKIPPED:
        return text, None
    return text, Token(name, text, line, col)
```

Check it.

```python
# scratch.py
from lexer import scan_one, COMPILED_SPEC as S, LexError

print(scan_one(S, "let x", 0, 1, 1))
print(scan_one(S, "let x", 3, 1, 4))
try:
    scan_one(S, "let @", 4, 1, 5)
except LexError as e:
    print(e)
```

Run it:

```bash
python3 scratch.py
```

You should see:

```text
('let', Token(type='LET', value='let', line=1, col=1))
(' ', None)
LexError at line 1, col 5: unexpected character '@'
```

20. Part II ended its spec with a `MISMATCH` rule that matched any character.  What did you gain by removing that rule and treating "no rule matched" as the error?  Think about what happens when someone loads a JSON spec and forgets the catch-all.

### Build Step 7: The tokenize Generator

The generator is short because the helpers hold the hard parts.  It starts at line 1, column 1, scans one piece at a time, and ends with an `EOF` token placed just past the last character.  Printing stays in `scratch.py`, so importing `lexer.py` runs nothing.

```python
# lexer.py: add at the end of the file
def tokenize(source: str) -> Iterator[Token]:
    """Yield one Token per lexeme in source, then one EOF token."""
    pos, line, col = 0, 1, 1
    while pos < len(source):
        text, tok = scan_one(COMPILED_SPEC, source, pos, line, col)
        if tok is not None:
            yield tok
        pos += len(text)
        ____4____
    yield Token("EOF", "", line, col)
```

Check it.

```python
# scratch.py
from lexer import tokenize

for tok in tokenize("let x = 42;"):
    print(tok)
print([t.type for t in tokenize("lets")])
```

Run it:

```bash
python3 scratch.py
```

You should see:

```text
Token(type='LET', value='let', line=1, col=1)
Token(type='IDENT', value='x', line=1, col=5)
Token(type='EQ', value='=', line=1, col=7)
Token(type='INT', value='42', line=1, col=9)
Token(type='SEMICOLON', value=';', line=1, col=11)
Token(type='EOF', value='', line=1, col=12)
['IDENT', 'EOF']
```

21. The generator yields before it updates `line` and `col`.  Swap those two steps in your head.  What would `LET` report as its column, and why?

### Build Step 8: Every Keyword

Let's grow the table.  The Lexer assignment requires `IF`, `ELSE`, `WHILE`, `LET`, `PRINT`, `TRUE`, `FALSE`, `AND`, `OR`, `NOT`, and `FUN`.  A language with loops also wants `BREAK` and `CONTINUE`, so you add those now.  Each keyword gets its own type and its own boundary check, and every one of them goes above `IDENT`.  You already have `LET`.  Two more are shown here, and Blank 5 stands for the other ten.

```python
# lexer.py: add just above the line with `("IDENT",`
    ("IF",         r"if(?!\w)"),
    ("ELSE",       r"else(?!\w)"),
    ____5____
```

Check it.

```python
# scratch.py
from lexer import tokenize

src = "if else while let print true false and or not fun break continue"
print(" ".join(t.type for t in tokenize(src)))
for word in ["iffy", "whiles", "notable", "lets", "continued"]:
    print(word, [t.type for t in tokenize(word)])
```

Run it:

```bash
python3 scratch.py
```

You should see:

```text
IF ELSE WHILE LET PRINT TRUE FALSE AND OR NOT FUN BREAK CONTINUE EOF
iffy ['IDENT', 'EOF']
whiles ['IDENT', 'EOF']
notable ['IDENT', 'EOF']
lets ['IDENT', 'EOF']
continued ['IDENT', 'EOF']
```

22. Suppose you kept Part II's single `KEYWORD` type.  What would the parser have to do with each keyword token that `expect("LET")` lets it skip?

### Build Step 9: Two-Character Operators

Python's alternation and your loop both take the first rule that matches, so a longer operator must come before any shorter operator it starts with.  These five go above `EQ`, and the next step adds the one-character operators below them.  Blank 6 stands for the rules for `!=` and `->`, named `NEQ` and `ARROW`.

```python
# lexer.py: add just above the line with `("EQ",`
    ("LE",         r"<="),
    ("GE",         r">="),
    ("EQEQ",       r"=="),
    ____6____
```

Check it.

```python
# scratch.py
from lexer import tokenize

print(" ".join(t.type for t in tokenize("<= >= == != ->")))
```

Run it:

```bash
python3 scratch.py
```

You should see:

```text
LE GE EQEQ NEQ ARROW EOF
```

23. CTQ 6 had you test `GE` against `GT`.  Name every other pair of operators in the Lexer assignment's table where the order of the two rules can change the result.  You should find five pairs in all, counting `GE` and `GT`.

### Build Step 10: One-Character Operators and Punctuation

This step finishes the operators.  Six of these characters mean something in a regex, so they need a backslash: `+`, `*`, `(`, `)`, `{`, and `}`.  `COLON` carries type annotations such as `let x: Num = 42;`, `COMMA` separates parameters and arguments, and `BANG` is the Parser grammar's other negation.  Blank 7 stands for `STAR`.  Blank 8 stands for the four bracket rules, `LPAREN`, `RPAREN`, `LBRACE`, and `RBRACE`.

```python
# lexer.py: add just above the line with `("SEMICOLON",`
    ("LT",         r"<"),
    ("GT",         r">"),
    ("BANG",       r"!"),
    ("PLUS",       r"\+"),
    ("MINUS",      r"-"),
    ____7____
    ("SLASH",      r"/"),
    ____8____
    ("COLON",      r":"),
    ("COMMA",      r","),
```

Check it.

```python
# scratch.py
from lexer import tokenize

src = "fun f(a: Num, b: Num) -> Num { print !a + -b * (a / b); }"
print(" ".join(t.type for t in tokenize(src)))
for op in ["<=", "==", "->", "!="]:
    print(op, [t.type for t in tokenize(op)])
```

Run it:

```bash
python3 scratch.py
```

You should see:

```text
FUN IDENT LPAREN IDENT COLON IDENT COMMA IDENT COLON IDENT RPAREN ARROW IDENT LBRACE PRINT BANG IDENT PLUS MINUS IDENT STAR LPAREN IDENT SLASH IDENT RPAREN SEMICOLON RBRACE EOF
<= ['LE', 'EOF']
== ['EQEQ', 'EOF']
-> ['ARROW', 'EOF']
!= ['NEQ', 'EOF']
```

24. Move your `ARROW` rule below `MINUS` for a moment and predict what `->` prints.  Run it to confirm, and then move the rule back.  What would a parser see at a return-type annotation if you had shipped that order?

### Build Step 11: Comments and Floats

`COMMENT` goes first, so it sits at the top of the table as the assignment shows it.  `FLOAT` goes above `INT` for the reason Part II gave: listed after it, `3.14` would lex as `INT 3` and leave `.14` behind.  This time you write `FLOAT` yourself, as digits, a literal dot, and digits.

```python
# lexer.py: add just above the line with `("WHITESPACE",`
    ("COMMENT",    r"#[^\n]*"),
```

Then:

```python
# lexer.py: add just above the line with `("INT",`
    ____9____
```

Check it.  The table now has 38 rules.  The one still missing is `STRING`.

```python
# scratch.py
from lexer import tokenize, TOKEN_SPEC

print(len(TOKEN_SPEC), TOKEN_SPEC[0][0])
src = "# a comment\nlet pi = 3.14; # trailing\nprint pi;"
for t in tokenize(src):
    print(t.type, repr(t.value), t.line, t.col)
```

Run it:

```bash
python3 scratch.py
```

You should see:

```text
38 COMMENT
LET 'let' 2 1
IDENT 'pi' 2 5
EQ '=' 2 8
FLOAT '3.14' 2 10
SEMICOLON ';' 2 14
PRINT 'print' 3 1
IDENT 'pi' 3 7
SEMICOLON ';' 3 9
EOF '' 3 10
```

25. Your `FLOAT` needs digits on both sides of the dot.  What does your lexer do with `3.` and with `.5`?  Try both, and say whether you would keep that behavior for your language.

### Build Step 12: The Lexer Class, from Model 3

Model 3 already gave you the idea: wrap the generator, buffer one token, and let the parser use `peek`, `advance`, and `expect`.  Your class keeps that design and makes these changes for the assignment's contract:

- **The buffer fills on demand.**  Model 3 filled its buffer in `__init__` and refilled it right after each consume.  Here `None` means empty, and `_fill` asks the generator only when a caller needs a token.
- **`EOF` comes from the generator.**  Model 3 used a fixed `EOF_TOKEN` at line -1.  Your generator already yields one with a real position.
- **`expect` takes one type and consumes nothing on a mismatch.**  You write it in Build Step 14.
- **`at_end` goes away.**  `peek().type == "EOF"` says the same thing, and the parser needs only the three methods.

```python
# lexer.py: add at the end of the file
class Lexer:
    """One token of lookahead over tokenize: peek, advance, and expect."""

    def __init__(self, source: str):
        self._tokens = tokenize(source)   # nothing is lexed yet
        self._buffer = None               # None means empty

    def _fill(self) -> None:
        if self._buffer is None:
            ____10____

    def peek(self) -> Token:
        self._fill()
        return self._buffer
```

Check it.  The first line reaches into `_buffer` only to watch it work.  The parser never will.

```python
# scratch.py
from lexer import Lexer

lx = Lexer("let x")
print(lx._buffer)
print(lx.peek())
print(lx.peek())
```

Run it:

```bash
python3 scratch.py
```

You should see:

```text
None
Token(type='LET', value='let', line=1, col=1)
Token(type='LET', value='let', line=1, col=1)
```

26. Take the source `let @` and Model 3's refill-after-consume design.  The parser calls `advance()` to get `let`.  What happens, and why is that the wrong moment to report the `@`?  What does filling on demand change?

### Build Step 13: Advance, and EOF Forever

`advance` hands over the buffered token and empties the buffer.  There is one edge case to get right.  The generator yields `EOF` last and then stops.  If you empty the buffer after `EOF`, the next `_fill` calls `next` on a finished generator, and Python raises `StopIteration`.  The contract says `peek` and `advance` return `EOF` forever, so `EOF` stays in the buffer for good.

```python
# lexer.py: add at the end of the file

    def advance(self) -> Token:
        self._fill()
        tok = self._buffer
        # Empty the buffer, unless this token is EOF.
        ____11____
        return tok
```

Check it.

```python
# scratch.py
from lexer import Lexer

lx = Lexer("x")
print(lx.advance())
print(lx.advance())
print(lx.advance())
```

Run it:

```bash
python3 scratch.py
```

You should see:

```text
Token(type='IDENT', value='x', line=1, col=1)
Token(type='EOF', value='', line=1, col=2)
Token(type='EOF', value='', line=1, col=2)
```

27. CTQ 10 asked why `peek` must be a pure read.  Now look at `_fill`, which `peek` calls and which changes `_buffer`.  In what sense is `peek` still a pure read from the parser's point of view?

### Build Step 14: Expect

Model 3's `expect` advanced first and then checked the type, so a mismatch had already consumed the token.  The contract asks for the opposite order: look first, and consume only on a match.  It raises a `LexError` that names the expected type, the found type, and the position.  Blank 12 is the mismatch check, and it is yours to write.

```python
# lexer.py: add at the end of the file

    def expect(self, token_type: str) -> Token:
        """Consume and return the next token if its type matches; otherwise raise."""
        tok = self.peek()
        ____12____
        return self.advance()
```

Check it.  Word your message the same way as the output below, because a later test reads it.

```python
# scratch.py
from lexer import Lexer, LexError

lx = Lexer("let x")
print(lx.expect("LET"))
try:
    lx.expect("INT")
except LexError as e:
    print(e)
print(lx.peek())
```

Run it:

```bash
python3 scratch.py
```

You should see:

```text
Token(type='LET', value='let', line=1, col=1)
LexError at line 1, col 5: expected INT, found IDENT
Token(type='IDENT', value='x', line=1, col=5)
```

That completes the contract.  A parser can now run on your lexer for any program without string literals.

28. CTQ 11 compared raising to returning `None`.  Here is a different comparison: why does it help a parser's error message if a failed `expect` leaves the token in place?

### Build Step 15: The STRING Rule

Model 4 gave you the pattern `"(?:[^"\\]|\\.)*"`: a quote, then any run of ordinary characters or backslash pairs, then a quote.  It has one weakness.  Its first alternative accepts a raw newline, so a forgotten closing quote swallows the following lines up to the next quote in the file.  For your rule, start from Model 4's pattern and add `\n` to the characters that the first alternative excludes.  Write the whole rule as a raw string, and use single quotes around it, because the pattern contains double quotes.

```python
# lexer.py: add just above the line with `("FLOAT",`
    ____13____
```

Check it on its own, before `tokenize` does anything new with it.  `True` means the text is one whole literal.

```python
# scratch.py
import re
from lexer import TOKEN_SPEC

STRING = re.compile(dict(TOKEN_SPEC)["STRING"])
for lexeme in [r'"no escapes"', r'"quote\"end"', r'"c:\\new"', r'""', r'"open', r'"a" "b"', '"a\nb"']:
    print(f"{lexeme!r:18}", bool(STRING.fullmatch(lexeme)))
```

Run it:

```bash
python3 scratch.py
```

You should see:

```text
'"no escapes"'     True
'"quote\\"end"'    True
'"c:\\\\new"'      True
'""'               True
'"open'            False
'"a" "b"'          False
'"a\nb"'           False
```

29. CTQ 12 explained why the pattern needs both alternatives.  Now take the source `let a = "open` and, on the next line, `let b = "x";`.  With Model 4's pattern, which text becomes the `STRING` token, and where would the programmer's first error message point?

### Build Step 16: Decode the Escapes

The token keeps the raw lexeme in `value`, but your program wants the text the literal stands for.  Model 4's `unescape` does this in one left-to-right `re.sub` pass, and its Watch Out showed why one pass is the right choice.  You make one change.  Model 4 left an unknown escape as written, so a typo such as `\q` passes silently.  Here it raises a `LexError`.  `decode` takes the body, the text between the quotes, and the position of the opening quote.

```python
# lexer.py: add just above the line with `SKIPPED = `
ESCAPES = {'"': '"', "\\": "\\", "n": "\n", "t": "\t"}


def decode(body: str, line: int = 0, col: int = 0) -> str:
    """Resolve the escapes in a string body in one left-to-right pass."""

    def replace(m):
        if m.group(1) not in ESCAPES:
            message = f"unsupported escape sequence \\{m.group(1)} in string literal"
            raise LexError(message, line, col, f'"{body}"')
        ____14____

    return re.sub(r"\\(.)", replace, body)
```

Check it.  `repr` shows a real tab as `\t`, a real newline as `\n`, and one real backslash as `\\`.

```python
# scratch.py
from lexer import decode, LexError

for body in [r"no escapes", r"tab\there", r"line\nbreak", r"quote\"end", r"c:\\new", ""]:
    print(f"{body:12} -> {decode(body)!r}")
try:
    decode(r"bad\qescape", 2, 9)
except LexError as e:
    print(e)
```

Run it:

```bash
python3 scratch.py
```

You should see:

```text
no escapes   -> 'no escapes'
tab\there    -> 'tab\there'
line\nbreak  -> 'line\nbreak'
quote\"end   -> 'quote"end'
c:\\new      -> 'c:\\new'
             -> ''
LexError at line 2, col 9: unsupported escape sequence \q in string literal
```

30. `decode` is a pure function of its input, and only `tokenize` will call it for real.  Why check it on its own first?  What would a wrong answer on the `c:\\new` line tell you that a wrong token from `tokenize` could not?

### Build Step 17: Put the Decoded Text on the Token

Two small edits connect the pieces.  `Token` gains a fifth field that only `STRING` tokens set.  Its default of `None` means every other token is still built with four arguments.  Then `scan_one` fills it in, passing the body without its quotes.  Every token now prints with `decoded=None` at the end, unless it is a string.

```python
# lexer.py: add just below the line with `1-indexed column`
    decoded: Optional[str] = None   # the resolved text, on STRING tokens only
```

Then:

```python
# lexer.py: replace the line with `return text, Token(name, text, line, col)`
    if name == "STRING":
        return text, Token(name, text, line, col, ____15____)
    return text, Token(name, text, line, col)
```

Check it.

```python
# scratch.py
from lexer import tokenize

tok = next(tokenize(r'"hello\nworld" after'))
print(tok)
print(len(tok.value), len(tok.decoded))
print(tok.decoded)
print(next(tokenize("after")))
```

Run it:

```bash
python3 scratch.py
```

You should see:

```text
Token(type='STRING', value='"hello\\nworld"', line=1, col=1, decoded='hello\nworld')
14 11
hello
world
Token(type='IDENT', value='after', line=1, col=1, decoded=None)
```

31. A parser builds its `Str` node from `tok.decoded`, not from `tok.value`.  What would end up inside your string values if it used `tok.value`?  Then name one use for `tok.value` on a string token.

### Build Step 18: Unterminated Strings

Run `let s = "open;` through your lexer right now and you get `unexpected character '"'`.  That is the right place but the wrong message, the same weakness you saw in Model 4 and CTQ 13.  No rule matches a quote that never closes, so the new check goes in the "no rule matched" branch.  There a quote at the current position can only mean one thing.  The error's `text` holds the unterminated lexeme, from the quote to the end of its line.

```python
# lexer.py: replace the line with `raise LexError(f"unexpected character {ch!r}", line, col, ch)`
        if ch == '"':
            lexeme = source[pos:].split("\n")[0]
            ____16____
        raise LexError(f"unexpected character {ch!r}", line, col, ch)
```

Your message must include the words `unterminated string`.  Check it.

```python
# scratch.py
from lexer import tokenize, LexError

for src in ['let s = "open;', 'let a = 1;\nlet s = "open\nlet b = 2;', "let c @ 3;"]:
    try:
        list(tokenize(src))
    except LexError as e:
        print(e, "|", repr(e.text))
```

Run it:

```bash
python3 scratch.py
```

You should see:

```text
LexError at line 1, col 9: unterminated string literal | '"open;'
LexError at line 2, col 9: unterminated string literal | '"open'
LexError at line 1, col 7: unexpected character '@' | '@'
```

32. The error points at the opening quote, not at the end of the line where the lexer gave up.  Why is the opening quote more useful to the person fixing the program?

### Build Step 19: Move the Rules to JSON

So far your rules live in Python.  The assignment also wants them in a file, so that a new dialect means a new file rather than new code.  The file has this shape: `{"comment_char": "#", "tokens": [[name, pattern], ...]}`.  JSON has no raw strings, so every regex backslash doubles.  `\.` becomes `\\.` in the file.  You do not need to retype 39 rules and double each backslash by hand.  A short script writes the file from your `TOKEN_SPEC`, and `json.dump` does the doubling.

```python
# make_spec.py: start the file with these lines
import json

from lexer import TOKEN_SPEC


def write_spec(path, comment_char, rules):
    with open(path, "w", encoding="utf-8") as f:
        json.dump({"comment_char": comment_char, "tokens": rules}, f, indent=2)


write_spec("token_spec.json", "#", TOKEN_SPEC)
```

Check it.  The last two lines of output are the `STRING` and `FLOAT` patterns as the file stores them.

```python
# scratch.py
import json

with open("token_spec.json", encoding="utf-8") as f:
    config = json.load(f)
print(len(config["tokens"]), config["tokens"][0][0], config["comment_char"])
with open("token_spec.json", encoding="utf-8") as f:
    for row in f:
        if "\\." in row:
            print(row.strip())
```

Run it:

```bash
python3 make_spec.py
python3 scratch.py
```

You should see:

```text
39 COMMENT #
"\"(?:[^\"\\\\\\n]|\\\\.)*\""
"\\d+\\.\\d+"
```

You submit `token_spec.json`.  `make_spec.py` is a helper, and you can include it or not.  The assignment's table has 37 rules, and yours has 39 because of `BREAK` and `CONTINUE`.

33. Your `TOKEN_SPEC` and `token_spec.json` now hold the same rules in two places.  What happens if you add a rule to the list and forget to run `make_spec.py`?  Which later step will catch it?

### Build Step 20: Load a Spec

`load_spec` reads the file and compiles each rule into the `(name, compiled pattern)` pairs that `match_rule` already takes.  A person edits this file by hand, so a broken pattern is a normal mistake, and it should come back as a `LexError` that names the rule.  This is why you compile each rule on its own.

```python
# lexer.py: add just above the line with `class Lexer:`
def load_spec(path: str) -> list:
    """Read a JSON token spec and return its (name, compiled pattern) pairs, in file order."""
    with open(path, encoding="utf-8") as f:
        config = json.load(f)
    if "tokens" not in config:
        raise LexError(f"config {path!r} is missing a 'tokens' list")
    compiled = []
    for name, pattern in config["tokens"]:
        try:
            ____17____
        except re.error as err:
            raise LexError(f"invalid pattern for token {name}: {pattern!r} ({err})") from err
    return compiled
```

Check it.

```python
# scratch.py
from lexer import load_spec, LexError

s = load_spec("token_spec.json")
print(len(s), s[0][0], type(s[0][1]).__name__)
with open("bad_spec.json", "w", encoding="utf-8") as f:
    f.write('{"tokens": [["BROKEN", "("]]}')
try:
    load_spec("bad_spec.json")
except LexError as e:
    print(e)
```

Run it:

```bash
python3 scratch.py
```

You should see:

```text
39 COMMENT Pattern
LexError at line 0, col 0: invalid pattern for token BROKEN: '(' (missing ), unterminated subpattern at position 0)
```

34. Suppose you joined these patterns into a Part II style master pattern and one of them was broken.  What could your error message say about which rule was at fault?

### Build Step 21: Let tokenize and Lexer Take a Spec

Your helpers already accept a spec, so this is a matter of passing one through.  `tokenize` gets a `spec` parameter that defaults to your built-in rules, so every call you already wrote still works.  `Lexer` gets the `config_path` parameter from the contract.

```python
# lexer.py: replace the line with `def tokenize(source: str) -> Iterator[Token]:`
def tokenize(source: str, spec=COMPILED_SPEC) -> Iterator[Token]:
```

Then:

```python
# lexer.py: replace the line with `text, tok = scan_one(COMPILED_SPEC, source, pos, line, col)`
        text, tok = scan_one(spec, source, pos, line, col)
```

Then:

```python
# lexer.py: replace the whole `def __init__(self, source: str):` definition
    def __init__(self, source: str, config_path: Optional[str] = None):
        spec = ____18____
        self._tokens = tokenize(source, spec)   # nothing is lexed yet
        self._buffer = None                     # None means empty
```

Check it.

```python
# scratch.py
from lexer import Lexer, tokenize, load_spec

src = "let total = x1 <= 42; # done\nprint total;"
print(list(tokenize(src, load_spec("token_spec.json"))) == list(tokenize(src)))
print(Lexer("let x = 1;", "token_spec.json").advance())
```

Run it:

```bash
python3 scratch.py
```

You should see:

```text
True
Token(type='LET', value='let', line=1, col=1, decoded=None)
```

35. `Lexer(source)` with no path uses `TOKEN_SPEC` and never opens `token_spec.json`.  If you fix a pattern only in the JSON file, which of these two runs sees the fix: `Lexer(source)` or `Lexer(source, "token_spec.json")`?

### Build Step 22: The Alternate Dialect

The alternate dialect uses `//` for comments and `:=` for assignment, and it needs no change to `lexer.py`.  Only two patterns differ, and the token type names stay the same, so `:=` is still an `EQ` and a parser would never notice.  Add these lines to your helper script.

```python
# make_spec.py: add at the end of the file

ALT_PATTERNS = {"COMMENT": r"//[^\n]*", "EQ": r":="}
____19____
write_spec("token_spec_alt.json", "//", alt_rules)
```

Blank 19 builds `alt_rules`: the same rules in the same order, with each name found in `ALT_PATTERNS` taking its new pattern.  Check it.

```python
# scratch.py
from lexer import Lexer

lx = Lexer("let n := 10; // start\nprint n;", "token_spec_alt.json")
tok = lx.advance()
while True:
    print(tok.type, repr(tok.value), tok.line, tok.col)
    if tok.type == "EOF":
        break
    tok = lx.advance()
```

Run it:

```bash
python3 make_spec.py
python3 scratch.py
```

You should see:

```text
LET 'let' 1 1
IDENT 'n' 1 5
EQ ':=' 1 7
INT '10' 1 10
SEMICOLON ';' 1 12
PRINT 'print' 2 1
IDENT 'n' 2 7
SEMICOLON ';' 2 8
EOF '' 2 9
```

36. Order still matters in the dialect.  `:=` starts with `:`, and `//` starts with `/`.  Which rule must sit above `COLON`, and which must sit above `SLASH`?  Does your table already have them in that order?

37. Nothing in your lexer reads `comment_char`.  Which rule does the real work of recognizing a comment?  What would you have to change for `comment_char` to control it?

### Build Step 23: Two Error Modes

A programmer with three typos should not have to run the lexer three times.  In `collect_all` mode the lexer records each error, keeps going, and raises them together at the end.  `fail_fast` stays the default.  This step adds the exception and passes the mode through.  The next step uses it.  Nothing changes in behavior yet, so your earlier checks still print what they printed.

```python
# lexer.py: add just above the line with `TOKEN_SPEC = [`
class LexErrorList(Exception):
    """Every error from one collect_all pass, in source order."""

    def __init__(self, errors: list):
        self.errors = errors
        super().__init__(f"{len(errors)} lexical error(s)")
```

Then:

```python
# lexer.py: replace the line with `def tokenize(source: str, spec=COMPILED_SPEC) -> Iterator[Token]:`
def tokenize(source: str, spec=COMPILED_SPEC, error_mode: str = "fail_fast") -> Iterator[Token]:
```

Then:

```python
# lexer.py: replace the whole `def __init__(self, source: str, config_path` definition
    def __init__(self, source: str, config_path: Optional[str] = None, error_mode: str = "fail_fast"):
        if error_mode not in ("fail_fast", "collect_all"):
            raise ValueError(f"unknown error_mode: {error_mode!r}")
        spec = ____18____
        self._tokens = tokenize(source, spec, error_mode)   # nothing is lexed yet
        self._buffer = None                                 # None means empty
```

Blank 18 is the same line you wrote in Build Step 21.  Check it.

```python
# scratch.py
from lexer import Lexer, LexError, LexErrorList

el = LexErrorList([LexError("a", 1, 2, "@")])
print(el, "|", len(el.errors), el.errors[0].col)
print(Lexer("x", error_mode="collect_all").peek())
try:
    Lexer("x", error_mode="sometimes")
except ValueError as e:
    print(e)
```

Run it:

```bash
python3 scratch.py
```

You should see:

```text
1 lexical error(s) | 1 2
Token(type='IDENT', value='x', line=1, col=1, decoded=None)
unknown error_mode: 'sometimes'
```

38. `Lexer` checks `error_mode` itself rather than leaving the check to `tokenize`.  `tokenize` is a generator.  If only `tokenize` checked, when would a misspelled mode finally raise?

### Build Step 24: The `collect_all` Branch

`scan_one` already raises a `LexError` for every kind of lexical error, so `tokenize` can catch them all in one place.  In `fail_fast` mode it raises the error again.  In `collect_all` mode it records the error, skips the offending text, and continues.  `err.text` is exactly the text to skip: one bad character, one unterminated string, or one string with a bad escape.  The list is raised at the point where `EOF` would have been yielded, and only if something went wrong.  Three small edits to `tokenize` do it.

```python
# lexer.py: add just below the line with `pos, line, col = 0, 1, 1`
    errors = []
```

Then:

```python
# lexer.py: replace the line with `text, tok = scan_one(spec, source, pos, line, col)`
        try:
            text, tok = scan_one(spec, source, pos, line, col)
        except LexError as err:
            if error_mode == "fail_fast":
                raise
            errors.append(err)
            ____20____
```

Then:

```python
# lexer.py: add just above the line with `yield Token("EOF", "", line, col)`
    if errors:
        raise LexErrorList(errors)
```

Blank 20 sets `text` and `tok` so that the rest of the loop skips the bad text and yields nothing.  Check it.

```python
# scratch.py
from lexer import Lexer, LexErrorList

for src in ["let @ = $;", 'let s = "bad\\q" @\nlet t = "open;\nprint t;']:
    lx = Lexer(src, error_mode="collect_all")
    try:
        while lx.peek().type != "EOF":
            print(lx.advance().type, end=" ")
    except LexErrorList as el:
        print("\n" + str(el))
        for e in el.errors:
            print(" ", e)
```

Run it:

```bash
python3 scratch.py
```

You should see:

```text
LET EQ SEMICOLON 
2 lexical error(s)
  LexError at line 1, col 5: unexpected character '@'
  LexError at line 1, col 9: unexpected character '$'
LET IDENT EQ LET IDENT EQ PRINT IDENT SEMICOLON 
3 lexical error(s)
  LexError at line 1, col 9: unsupported escape sequence \q in string literal
  LexError at line 1, col 17: unexpected character '@'
  LexError at line 2, col 9: unterminated string literal
```

39. After a `LexError` or a `LexErrorList` escapes, the generator is finished.  What does one more call to `peek()` do?  Why does the parser not need this case to behave any better?

### Build Step 25: The Test Frame

The checks so far proved each piece once, and you replaced them as you went.  A test suite keeps them, so a change next month cannot quietly break something that works today.  You use `unittest`, which comes with Python.  The `types` helper gives the token types for a source string, without `EOF`, and every test class below uses it.  You use `os` and `tempfile` in a later step.

```python
# test_lexer.py: start the file with these lines
import os
import tempfile
import unittest

from lexer import Lexer, LexError, LexErrorList, tokenize


def types(source: str, **kwargs) -> list:
    lx = Lexer(source, **kwargs)
    out = []
    ____21____
    return out


class TestTokenTypes(unittest.TestCase):
    def test_int(self):
        self.assertEqual(types("42"), ["INT"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
```

Blank 21 is the loop that peeks for `EOF` and appends the type of each token it consumes.  Check it.

```bash
python3 test_lexer.py
```

You should see the output below.  The time on the `Ran` line will differ, here and in every test run that follows, and Python 3.10 prints a slightly shorter name in parentheses on each test line.

```text
test_int (__main__.TestTokenTypes.test_int) ... ok

----------------------------------------------------------------------
Ran 1 test in 0.000s

OK
```

40. `types` drives the lexer through `peek` and `advance`, not through `tokenize`.  Why is that the better choice for tests of a component the parser will use?

### Build Step 26: Token Types

New tests go above the `if __name__` line, and these two belong to `TestTokenTypes`, the last class in the file.  The first pins the worked example down to its columns.  The second puts every token type in one source string, so a missing or misplaced rule shows up at once.

```python
# test_lexer.py: add just above the line with `if __name__`
    def test_worked_example(self):
        got = [(t.type, t.line, t.col) for t in tokenize("let x = 42;")]
        self.assertEqual(got, [("LET", 1, 1), ("IDENT", 1, 5), ("EQ", 1, 7), ("INT", 1, 9),
                               ("SEMICOLON", 1, 11), ("EOF", 1, 12)])

    def test_every_type_at_once(self):
        src = ('if else while let print true false and or not fun break continue foo '
               '3.14 42 "s" <= >= == != ! -> = < > + - * / ( ) { } ; : ,')
        self.assertEqual(" ".join(types(src)),
                         "IF ELSE WHILE LET PRINT TRUE FALSE AND OR NOT FUN BREAK CONTINUE IDENT "
                         "FLOAT INT STRING LE GE EQEQ NEQ BANG ARROW EQ LT GT PLUS MINUS STAR "
                         "SLASH LPAREN RPAREN LBRACE RBRACE SEMICOLON COLON COMMA")
```

Check it.  A class name after the file name runs just that class.

```bash
python3 test_lexer.py TestTokenTypes
```

You should see:

```text
test_every_type_at_once (__main__.TestTokenTypes.test_every_type_at_once) ... ok
test_int (__main__.TestTokenTypes.test_int) ... ok
test_worked_example (__main__.TestTokenTypes.test_worked_example) ... ok

----------------------------------------------------------------------
Ran 3 tests in 0.001s

OK
```

**You write:** the assignment's rubric asks for one test per token type, so `test_every_type_at_once` is a safety net and not the whole job.  Add one short method per type to this class, in the shape of `test_int`.  Include `COMMENT` and `WHITESPACE`, which should produce no token.

### Build Step 27: Maximal Munch

These are the seven cases the assignment requires.  If one of them ever splits, the fix is the order of two rules in `TOKEN_SPEC`, not the loop.

```python
# test_lexer.py: add just above the line with `if __name__`
class TestMaximalMunch(unittest.TestCase):
    def test_munch_iffy(self):
        self.assertEqual(types("iffy"), ["IDENT"])
    def test_munch_whiles(self):
        self.assertEqual(types("whiles"), ["IDENT"])
    def test_munch_notable(self):
        self.assertEqual(types("notable"), ["IDENT"])
    def test_munch_le(self):
        self.assertEqual(types("<="), ["LE"])
    def test_munch_eqeq(self):
        self.assertEqual(types("=="), ["EQEQ"])
    def test_munch_neq(self):
        self.assertEqual(types("!="), ["NEQ"])
    ____22____
```

Blank 22 is the seventh case, a method named `test_munch_arrow`.  Check it.

```bash
python3 test_lexer.py TestMaximalMunch
```

You should see:

```text
test_munch_arrow (__main__.TestMaximalMunch.test_munch_arrow) ... ok
test_munch_eqeq (__main__.TestMaximalMunch.test_munch_eqeq) ... ok
test_munch_iffy (__main__.TestMaximalMunch.test_munch_iffy) ... ok
test_munch_le (__main__.TestMaximalMunch.test_munch_le) ... ok
test_munch_neq (__main__.TestMaximalMunch.test_munch_neq) ... ok
test_munch_notable (__main__.TestMaximalMunch.test_munch_notable) ... ok
test_munch_whiles (__main__.TestMaximalMunch.test_munch_whiles) ... ok

----------------------------------------------------------------------
Ran 7 tests in 0.000s

OK
```

41. These tests all pass today.  Pick one and describe the exact edit to `TOKEN_SPEC` that would make it fail.  Try the edit, watch the test catch it, and put the rule back.

### Build Step 28: Floats, Comments, and Positions

A float must stay one token, and a comment must disappear without throwing off the line count.  Both of these failures would look fine in a one-line demo, so they earn their own tests.

```python
# test_lexer.py: add just above the line with `if __name__`
class TestPositions(unittest.TestCase):
    def test_float_before_int(self):
        self.assertEqual(types("3.14 42 0.5"), ["FLOAT", "INT", "FLOAT"])

    def test_comments_skipped_and_lines_tracked(self):
        toks = list(tokenize("# a comment\nlet x = 1; # trailing\nprint x;"))
        self.assertEqual((toks[0].type, toks[0].line, toks[0].col), ("LET", 2, 1))
        last = toks[-3]
        self.assertEqual((last.type, last.line, last.col), ("IDENT", 3, 7))
```

Check it.

```bash
python3 test_lexer.py TestPositions
```

You should see:

```text
test_comments_skipped_and_lines_tracked (__main__.TestPositions.test_comments_skipped_and_lines_tracked) ... ok
test_float_before_int (__main__.TestPositions.test_float_before_int) ... ok

----------------------------------------------------------------------
Ran 2 tests in 0.000s

OK
```

**You write:** add a test that a tab counts as one column and that the column resets after a newline.  For example, `y` in `"x\n\ty"` should report line 2, column 2.

### Build Step 29: String Escapes

Write the `r` before a test's source string whenever it contains a backslash.  Without it, Python turns `"\t"` into a real tab before your lexer ever sees the backslash.  The helper `decoded` reads the resolved text of the first token.

```python
# test_lexer.py: add just above the line with `if __name__`
class TestStringEscapes(unittest.TestCase):
    def decoded(self, lexeme):
        return Lexer(lexeme).peek().decoded

    def test_escape_none(self):
        self.assertEqual(self.decoded('"no escapes"'), "no escapes")
    def test_escape_tab(self):
        self.assertEqual(self.decoded(r'"tab\there"'), "tab\there")
    def test_escape_newline(self):
        self.assertEqual(self.decoded(r'"line\nbreak"'), "line\nbreak")
    def test_escape_quote(self):
        self.assertEqual(self.decoded(r'"quote\"end"'), 'quote"end')
    def test_escape_backslash_then_n(self):
        self.assertEqual(self.decoded(r'"c:\\new"'), "c:\\new")
    ____23____
```

Blank 23 is two more methods.  `test_raw_and_decoded_differ` checks that `r'"a\nb"'` keeps 6 characters in `value` and has 3 in `decoded`.  `test_unknown_escape_raises` checks that `r'"bad\qescape"'` raises a `LexError` whose text contains `\q`.  Check it.

```bash
python3 test_lexer.py TestStringEscapes
```

You should see:

```text
test_escape_backslash_then_n (__main__.TestStringEscapes.test_escape_backslash_then_n) ... ok
test_escape_newline (__main__.TestStringEscapes.test_escape_newline) ... ok
test_escape_none (__main__.TestStringEscapes.test_escape_none) ... ok
test_escape_quote (__main__.TestStringEscapes.test_escape_quote) ... ok
test_escape_tab (__main__.TestStringEscapes.test_escape_tab) ... ok
test_raw_and_decoded_differ (__main__.TestStringEscapes.test_raw_and_decoded_differ) ... ok
test_unknown_escape_raises (__main__.TestStringEscapes.test_unknown_escape_raises) ... ok

----------------------------------------------------------------------
Ran 7 tests in 0.001s

OK
```

42. Delete the `r` from the source string in `test_escape_tab` and predict the result.  Does the test still pass?  If it does, what has it stopped testing?

### Build Step 30: The Contract, Part One

The contract is a promise to code you have not written yet.  These tests are how you keep it.  Calling `peek` ten times must change nothing, and `EOF` must keep coming.

```python
# test_lexer.py: add just above the line with `if __name__`
class TestInterface(unittest.TestCase):
    def test_peek_is_idempotent(self):
        lx = Lexer("let x = 1;")
        first = lx.peek()
        for _ in range(10):
            self.assertEqual(lx.peek(), first)
        self.assertEqual(lx.advance(), first)
        self.assertEqual(lx.peek().type, "IDENT")

    def test_eof_forever(self):
        lx = Lexer("x")
        lx.advance()
        for _ in range(5):
            self.assertEqual(lx.peek().type, "EOF")
            self.assertEqual(lx.advance().type, "EOF")
```

Check it.

```bash
python3 test_lexer.py TestInterface
```

You should see:

```text
test_eof_forever (__main__.TestInterface.test_eof_forever) ... ok
test_peek_is_idempotent (__main__.TestInterface.test_peek_is_idempotent) ... ok

----------------------------------------------------------------------
Ran 2 tests in 0.000s

OK
```

43. `assertEqual(lx.peek(), first)` compares two `Token` objects.  Which line of your `Token` definition makes that comparison look at the fields, and what would a plain class compare instead?

### Build Step 31: The Contract, Part Two

A parser sometimes drives the lexer with `peek` and sometimes with `advance`, so show that both produce the same stream.  This is the two-way check you saw as Style 1 and Style 2 in Model 3, and now it runs every time.  Both tests go in `TestInterface`, which is still the last class in the file.

```python
# test_lexer.py: add just above the line with `if __name__`
    def test_expect_mismatch_consumes_nothing(self):
        lx = Lexer("let x")
        self.assertEqual(lx.expect("LET").value, "let")
        with self.assertRaises(LexError) as cm:
            lx.expect("SEMICOLON")
        self.assertIn("expected SEMICOLON, found IDENT", cm.exception.message)
        self.assertEqual((cm.exception.line, cm.exception.col), (1, 5))
        self.assertEqual(lx.peek().type, "IDENT")

    def test_two_consumption_patterns_agree(self):
        src = 'let x = 10; while x > 0 { print "hi\\n"; x = x - 1; }'
        self.assertEqual(self.peek_driven(src), self.advance_driven(src))

    ____24____
```

Blank 24 is two helper methods, `peek_driven` and `advance_driven`.  Each builds its own `Lexer` and returns the list of tokens before `EOF`.  `peek_driven` loops while `peek` is not `EOF`.  `advance_driven` calls `advance` and stops when the token it got is `EOF`.  Check it.

```bash
python3 test_lexer.py TestInterface
```

You should see:

```text
test_eof_forever (__main__.TestInterface.test_eof_forever) ... ok
test_expect_mismatch_consumes_nothing (__main__.TestInterface.test_expect_mismatch_consumes_nothing) ... ok
test_peek_is_idempotent (__main__.TestInterface.test_peek_is_idempotent) ... ok
test_two_consumption_patterns_agree (__main__.TestInterface.test_two_consumption_patterns_agree) ... ok

----------------------------------------------------------------------
Ran 4 tests in 0.001s

OK
```

44. The two helpers must each build their own `Lexer`.  What would happen if they shared one?

### Build Step 32: JSON Specs

These tests read the JSON files you generated, so run them from your project folder.  The first test catches the drift from CTQ 33.  The third writes a broken spec into a temporary folder that disappears when the test ends.

```python
# test_lexer.py: add just above the line with `if __name__`
class TestJSONConfig(unittest.TestCase):
    def test_default_file_matches_builtin(self):
        src = "let x = 42; # comment\nprint x;"
        self.assertEqual(types(src), types(src, config_path="token_spec.json"))

    def test_alternate_dialect(self):
        got = types("let x := 42; // a comment\nprint x;", config_path="token_spec_alt.json")
        self.assertEqual(got, ["LET", "IDENT", "EQ", "INT", "SEMICOLON", "PRINT", "IDENT", "SEMICOLON"])

    def test_bad_pattern_raises_lexerror(self):
        with tempfile.TemporaryDirectory() as folder:
            path = os.path.join(folder, "bad.json")
            with open(path, "w", encoding="utf-8") as f:
                f.write('{"tokens": [["BROKEN", "("]]}')
            with self.assertRaises(LexError) as cm:
                Lexer("x", config_path=path)
        self.assertIn("BROKEN", str(cm.exception))
```

Check it.

```bash
python3 test_lexer.py TestJSONConfig
```

You should see:

```text
test_alternate_dialect (__main__.TestJSONConfig.test_alternate_dialect) ... ok
test_bad_pattern_raises_lexerror (__main__.TestJSONConfig.test_bad_pattern_raises_lexerror) ... ok
test_default_file_matches_builtin (__main__.TestJSONConfig.test_default_file_matches_builtin) ... ok

----------------------------------------------------------------------
Ran 3 tests in 0.001s

OK
```

**You write:** add a test that a JSON file with no `tokens` key raises a `LexError`, using the same temporary-folder pattern.

### Build Step 33: Errors That Stop

The assignment requires five deliberate error programs.  The error tests check where an error happened, so they read the `line`, `col`, and `text` attributes rather than the wording of the message.  Here are the three `fail_fast` programs.  Each uses `list(tokenize(...))`, which runs the generator to its end.

```python
# test_lexer.py: add just above the line with `if __name__`
class TestErrors(unittest.TestCase):
    def located(self, source):
        with self.assertRaises(LexError) as cm:
            list(tokenize(source))
        return cm.exception.line, cm.exception.col, cm.exception.text

    def test_error_at_sign(self):
        self.assertEqual(self.located("@"), (1, 1, "@"))

    def test_error_unterminated_string_at_opening_quote(self):
        self.assertEqual(self.located('let s = "hello'), (1, 9, '"hello'))

    def test_error_dollar_mid_program(self):
        self.assertEqual(self.located("let x = 1;\nlet y = $ + 2;"), (2, 9, "$"))
```

Check it.

```bash
python3 test_lexer.py TestErrors
```

You should see:

```text
test_error_at_sign (__main__.TestErrors.test_error_at_sign) ... ok
test_error_dollar_mid_program (__main__.TestErrors.test_error_dollar_mid_program) ... ok
test_error_unterminated_string_at_opening_quote (__main__.TestErrors.test_error_unterminated_string_at_opening_quote) ... ok

----------------------------------------------------------------------
Ran 3 tests in 0.000s

OK
```

45. `test_error_dollar_mid_program` expects line 2, and the lexer reached the `$` by way of line 1.  Which line of `lexer.py` would have to be broken for this test to report line 1?

### Build Step 34: Errors That Keep Going

The last two required programs use `collect_all`.  One shows that the list holds every error.  The other shows recovery: a valid token right after an error still comes out.  A third test pins down a promise from Build Step 12, that `fail_fast` reports a bad character only when the parser reaches it.  These tests stay in `TestErrors`.

```python
# test_lexer.py: add just above the line with `if __name__`
    def test_collect_all_reports_every_error(self):
        with self.assertRaises(LexErrorList) as cm:
            types("let @ = 1;\nlet $ = 2;", error_mode="collect_all")
        got = [(e.line, e.col) for e in cm.exception.errors]
        self.assertEqual(got, [(1, 5), (2, 5)])

    def test_collect_all_recovers_the_next_token(self):
        lx = Lexer("@ let", error_mode="collect_all")
        self.assertEqual(lx.advance().type, "LET")
        with self.assertRaises(LexErrorList):
            lx.advance()

    def test_fail_fast_waits_until_the_error_is_reached(self):
        lx = Lexer("let @")
        ____25____
```

Blank 25 checks that the first `advance` returns `LET` and that the next `peek` raises a `LexError`.  Check it.

```bash
python3 test_lexer.py TestErrors
```

You should see:

```text
test_collect_all_recovers_the_next_token (__main__.TestErrors.test_collect_all_recovers_the_next_token) ... ok
test_collect_all_reports_every_error (__main__.TestErrors.test_collect_all_reports_every_error) ... ok
test_error_at_sign (__main__.TestErrors.test_error_at_sign) ... ok
test_error_dollar_mid_program (__main__.TestErrors.test_error_dollar_mid_program) ... ok
test_error_unterminated_string_at_opening_quote (__main__.TestErrors.test_error_unterminated_string_at_opening_quote) ... ok
test_fail_fast_waits_until_the_error_is_reached (__main__.TestErrors.test_fail_fast_waits_until_the_error_is_reached) ... ok

----------------------------------------------------------------------
Ran 6 tests in 0.001s

OK
```

46. In `test_collect_all_recovers_the_next_token`, the `LexErrorList` comes from the second `advance`, not from the line that builds the `Lexer`.  What did that design cost a parser in `collect_all` mode, and what did it gain?

### Build Step 35: Run It All

You are done building.  One last pass checks the whole component the way a parser would use it.  Importing `lexer.py` must print nothing, and the full suite must pass.  The command below also saves the suite's report for your submission.  `unittest` writes its report to standard error, so the `2>&1` is required.

```bash
python3 -c "import lexer"
python3 test_lexer.py
python3 test_lexer.py > test_output.txt 2>&1
```

You should see the output below, plus any tests you added under **You write**, which raise the count.

```text
test_collect_all_recovers_the_next_token (__main__.TestErrors.test_collect_all_recovers_the_next_token) ... ok
test_collect_all_reports_every_error (__main__.TestErrors.test_collect_all_reports_every_error) ... ok
test_error_at_sign (__main__.TestErrors.test_error_at_sign) ... ok
test_error_dollar_mid_program (__main__.TestErrors.test_error_dollar_mid_program) ... ok
test_error_unterminated_string_at_opening_quote (__main__.TestErrors.test_error_unterminated_string_at_opening_quote) ... ok
test_fail_fast_waits_until_the_error_is_reached (__main__.TestErrors.test_fail_fast_waits_until_the_error_is_reached) ... ok
test_eof_forever (__main__.TestInterface.test_eof_forever) ... ok
test_expect_mismatch_consumes_nothing (__main__.TestInterface.test_expect_mismatch_consumes_nothing) ... ok
test_peek_is_idempotent (__main__.TestInterface.test_peek_is_idempotent) ... ok
test_two_consumption_patterns_agree (__main__.TestInterface.test_two_consumption_patterns_agree) ... ok
test_alternate_dialect (__main__.TestJSONConfig.test_alternate_dialect) ... ok
test_bad_pattern_raises_lexerror (__main__.TestJSONConfig.test_bad_pattern_raises_lexerror) ... ok
test_default_file_matches_builtin (__main__.TestJSONConfig.test_default_file_matches_builtin) ... ok
test_munch_arrow (__main__.TestMaximalMunch.test_munch_arrow) ... ok
test_munch_eqeq (__main__.TestMaximalMunch.test_munch_eqeq) ... ok
test_munch_iffy (__main__.TestMaximalMunch.test_munch_iffy) ... ok
test_munch_le (__main__.TestMaximalMunch.test_munch_le) ... ok
test_munch_neq (__main__.TestMaximalMunch.test_munch_neq) ... ok
test_munch_notable (__main__.TestMaximalMunch.test_munch_notable) ... ok
test_munch_whiles (__main__.TestMaximalMunch.test_munch_whiles) ... ok
test_comments_skipped_and_lines_tracked (__main__.TestPositions.test_comments_skipped_and_lines_tracked) ... ok
test_float_before_int (__main__.TestPositions.test_float_before_int) ... ok
test_escape_backslash_then_n (__main__.TestStringEscapes.test_escape_backslash_then_n) ... ok
test_escape_newline (__main__.TestStringEscapes.test_escape_newline) ... ok
test_escape_none (__main__.TestStringEscapes.test_escape_none) ... ok
test_escape_quote (__main__.TestStringEscapes.test_escape_quote) ... ok
test_escape_tab (__main__.TestStringEscapes.test_escape_tab) ... ok
test_raw_and_decoded_differ (__main__.TestStringEscapes.test_raw_and_decoded_differ) ... ok
test_unknown_escape_raises (__main__.TestStringEscapes.test_unknown_escape_raises) ... ok
test_every_type_at_once (__main__.TestTokenTypes.test_every_type_at_once) ... ok
test_int (__main__.TestTokenTypes.test_int) ... ok
test_worked_example (__main__.TestTokenTypes.test_worked_example) ... ok

----------------------------------------------------------------------
Ran 32 tests in 0.003s

OK
```

Your lexer is finished, and you typed all of it.  To complete the Lexer assignment you still need `readme.md`, with your Part 0 answers, your Lexing Theory answers, the ordering rationale, and the two error modes, as the assignment's Deliverables table lists.

47. Build Step 8 added `BREAK` and `CONTINUE` before anything used them.  Build Step 22 added a whole dialect with no change to `lexer.py`.  Compare the two.  Which future changes does your design make cheap, and which would still need new Python?

---

# Check Your Understanding

A lexer's job, stated precisely, is to:

[(X)] Turn a character stream into a token stream, discarding whitespace and comments
[( )] Turn a token stream into a tree
[( )] Check that the program is syntactically legal
[( )] Resolve names to their declarations

---

Given the input `12foo`, a lexer with patterns for INT and IDENT will most likely produce:

[(X)] INT `12` followed by IDENT `foo`, because each match starts fresh at the current position
[( )] A single IDENT `12foo`
[( )] A lexical error, since the two patterns overlap
[( )] A single INT `12`, discarding the rest

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

The lexer tries the patterns in TOKEN_SPEC order at each position.  For the input `x>=5`, if `IDENT` is listed before `GE` (`>=`) in TOKEN_SPEC, the result is:

[(X)] `IDENT("x"), GE, INT(5)`: `IDENT` cannot match `>` at all, so its place relative to `GE` does not matter here
[( )] `IDENT("x"), GT, EQ, INT(5)`: `>=` is never recognized because `IDENT` greedily consumed `x`
[( )] Undefined behavior; the order doesn't matter
[( )] A `LexError` because ambiguous input

Python's `re` alternation takes the first alternative that matches at a position, not the longest.  For input `<=`, if `LT` (`<`) is listed before `LE` (`<=`) in TOKEN_SPEC:

[(X)] The lexer emits `LT` for `<`: the order in TOKEN_SPEC decides, which is why two-character operators go first
[( )] The lexer finds both `LT` and `LE` as possibilities and chooses `LE` (the longer match)
[( )] The lexer raises an ambiguity error
[( )] The lexer emits `LE`, because maximal munch is automatic

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
| 6 | `_= count2 ...` | `WHITESPACE` -> `' '` | `' '` | *(skipped)* |
| 7 | `= count2 ...` | `EQ` -> `=` (1). `EQEQ` needs `==`, fails | `=` | `EQ("=")` |
| 8 | `_count2 + ...` | `WHITESPACE` | `' '` | *(skipped)* |
| 9 | `count2 + 12 ...` | `IDENT` -> `count2` (6) | `count2` | `IDENT("count2")` |
| 15 | `_+ 12 ...` | `WHITESPACE` | `' '` | *(skipped)* |
| 16 | `+ 12 >= ...` | `PLUS` -> `+` (1) | `+` | `PLUS("+")` |
| 17 | `_12 >= ...` | `WHITESPACE` | `' '` | *(skipped)* |
| 18 | `12 >= limit` | `INT` -> `12` (2). `FLOAT` needs a `.`, fails | `12` | `INT("12")` |
| 20 | `_>= limit` | `WHITESPACE` | `' '` | *(skipped)* |
| 21 | `>= limit` | **`GE` -> `>=` (2)** and `GT` -> `>` (1) | `>=` (longer) | `GE(">=")` |
| 23 | `_limit` | `WHITESPACE` | `' '` | *(skipped)* |
| 24 | `limit` | `IDENT` -> `limit` (5) | `limit` | `IDENT("limit")` |
| 29 | *(end)* | - | - | `EOF` |

**Seven tokens** plus `EOF`: `IDENT EQ IDENT PLUS INT GE IDENT`.

Two rows carry the whole lesson:

- Position 21 is maximal munch doing real work.  Both `GT` and `GE` match at that position.  Take the *longest*, and `>=` stays whole.  (The Part II lexer gets the same result a different way: Python's alternation takes the first pattern that matches, so `TOKEN_SPEC` lists `GE` before `GT`.)  This is CTQ 3.  Had the lexer emitted `GT` then `EQ`, the parser would see `a > = b`, which matches no production.  The error would surface as a confusing *parse* error several stages away from the real bug.  Fix errors where the information still exists.
- Position 0 is CTQ 2.  The identifier pattern is `[A-Za-z_][A-Za-z0-9_]*`.  Its second half admits digits, so the match runs to the end of `count2`: six characters, not four.  The scanner never "notices" the `2` and stops, because stopping early would not be the longest match.  The same mechanism is why `iffy` is one `IDENT` and not `IF` followed by `IDENT("fy")`: `IDENT` matches four characters where `IF` matches only two.

Notice what the table does *not* contain: any decision about meaning.  The scanner never asks whether `count2` was declared, or whether adding an `INT` to an `IDENT` type-checks.  It only asks "how far does a pattern reach from here?"  That is why a regular expression is enough to do this job, and why the next stage needs a grammar instead.


> **Watch out!**  The maximal munch rule always takes the *longest* possible match at the current position.  So `>=` is always one token, never two, and `iffy` is always one identifier, never the keyword `if` followed by `fy`.  When you trace by hand, compare lengths.  When you write the regex lexer, Python's alternation takes the *first* pattern that matches, so you get maximal munch by listing longer patterns first (`GE` before `GT`) and anchoring keywords with `\b`.  If your hand tokenization ever splits a run of identifier-legal characters mid-stream, you have violated maximal munch.

---

### Lexer Build: Blanks

These are the blanks from Build Steps 1 to 35.  Try each one first.  Your version may differ and still be right, as long as the step's check prints the same output.

**Blank 1 (Build Step 2).**  Compile each rule once, up front.

```python
COMPILED_SPEC = [(name, re.compile(pattern)) for name, pattern in TOKEN_SPEC]
```

**Blank 2 (Build Step 3).**  `rfind` gives the index of the last newline, so the subtraction counts the characters after it, plus one.

```python
len(text) - text.rfind("\n")
```

**Blank 3 (Build Step 5).**  The message comes from the stored attributes.

```python
f"LexError at line {self.line}, col {self.col}: {self.message}"
```

**Blank 4 (Build Step 7).**  This line runs for skipped text too, which is why it sits outside the `if`.

```python
line, col = advance_position(text, line, col)
```

**Blank 5 (Build Step 8).**  These are the other ten keywords, in the same shape as `IF`.

```python
("WHILE",      r"while(?!\w)"),
("PRINT",      r"print(?!\w)"),
("TRUE",       r"true(?!\w)"),
("FALSE",      r"false(?!\w)"),
("AND",        r"and(?!\w)"),
("OR",         r"or(?!\w)"),
("NOT",        r"not(?!\w)"),
("FUN",        r"fun(?!\w)"),
("BREAK",      r"break(?!\w)"),
("CONTINUE",   r"continue(?!\w)"),
```

**Blank 6 (Build Step 9).**  Neither `!` nor `-` means anything special at this position in a regex.

```python
("NEQ",        r"!="),
("ARROW",      r"->"),
```

**Blank 7 (Build Step 10).**  A bare `*` means "zero or more," so it needs the backslash.

```python
("STAR",       r"\*"),
```

**Blank 8 (Build Step 10).**  All four brackets mean something in a regex.

```python
("LPAREN",     r"\("),
("RPAREN",     r"\)"),
("LBRACE",     r"\{"),
("RBRACE",     r"\}"),
```

**Blank 9 (Build Step 11).**  A bare `.` matches any character, so the dot needs its backslash.

```python
("FLOAT",      r"\d+\.\d+"),
```

**Blank 10 (Build Step 12).**  This asks the generator for one token.

```python
self._buffer = next(self._tokens)
```

**Blank 11 (Build Step 13).**  `EOF` stays in the buffer for good.

```python
if tok.type != "EOF":
    self._buffer = None
```

**Blank 12 (Build Step 14).**  The `peek` above it consumed nothing, so a mismatch leaves the token in place.

```python
if tok.type != token_type:
    message = f"expected {token_type}, found {tok.type}"
    raise LexError(message, tok.line, tok.col, tok.value)
```

**Blank 13 (Build Step 15).**  The only change from Model 4 is the `\n` inside the first alternative.

```python
("STRING",     r'"(?:[^"\\\n]|\\.)*"'),
```

**Blank 14 (Build Step 16).**  Look up the letter alone, not the whole match with its backslash.

```python
return ESCAPES[m.group(1)]
```

**Blank 15 (Build Step 17).**  The slice drops the two quotes, and the position goes along for any error.

```python
decode(text[1:-1], line, col)
```

**Blank 16 (Build Step 18).**  The position is the opening quote, because `line` and `col` have not moved.

```python
raise LexError("unterminated string literal", line, col, lexeme)
```

**Blank 17 (Build Step 20).**  `re.compile` is what can raise `re.error`, so it belongs inside the `try`.

```python
compiled.append((name, re.compile(pattern)))
```

**Blank 18 (Build Steps 21 and 23).**  With no path, the lexer uses the built-in rules.

```python
load_spec(config_path) if config_path else COMPILED_SPEC
```

**Blank 19 (Build Step 22).**  `get` falls back to the rule's own pattern when the name is not in the dictionary.

```python
alt_rules = [(name, ALT_PATTERNS.get(name, pattern)) for name, pattern in TOKEN_SPEC]
```

**Blank 20 (Build Step 24).**  The rest of the loop then moves past the bad text and yields nothing.

```python
text, tok = err.text, None
```

**Blank 21 (Build Step 25).**  The peek decides, and the advance consumes.

```python
while lx.peek().type != "EOF":
    out.append(lx.advance().type)
```

**Blank 22 (Build Step 27).**  `ARROW` must beat `MINUS`.

```python
def test_munch_arrow(self):
    self.assertEqual(types("->"), ["ARROW"])
```

**Blank 23 (Build Step 29).**  The first test shows that the token keeps both forms.

```python
def test_raw_and_decoded_differ(self):
    tok = Lexer(r'"a\nb"').peek()
    self.assertEqual((len(tok.value), len(tok.decoded)), (6, 3))
def test_unknown_escape_raises(self):
    with self.assertRaises(LexError) as cm:
        Lexer(r'"bad\qescape"').peek()
    self.assertIn("\\q", str(cm.exception))
```

**Blank 24 (Build Step 31).**  Pattern A looks first, and pattern B consumes first.

```python
def peek_driven(self, src):
    lx, out = Lexer(src), []
    while lx.peek().type != "EOF":
        out.append(lx.advance())
    return out
def advance_driven(self, src):
    lx, out = Lexer(src), []
    tok = lx.advance()
    while tok.type != "EOF":
        out.append(tok)
        tok = lx.advance()
    return out
```

**Blank 25 (Build Step 34).**  The `LET` comes out cleanly, and the error waits for the next token.

```python
self.assertEqual(lx.advance().type, "LET")
with self.assertRaises(LexError):
    lx.peek()
```

### Lexer Build: Critical Thinking Answers

15. `a.col = 9` raises `dataclasses.FrozenInstanceError`.  Every caller of `peek()` gets the same object, so if one caller could edit it, the next caller would see a different token, and `peek` would no longer be idempotent.
16. `.match(source, pos)` only tries at `pos`, and `pos` is always where the previous token ended.  The previous match took all the word characters it could, so a keyword cannot begin in the middle of a word.  Only the end can run on, as `let` does in `lets`.
17. Positions drift.  Every newline lives in skipped whitespace, so every token after the first newline reports line 1, and every column counts from the wrong place.
18. It would loop forever.  `a*` matches the empty string at `b`, so the position never moves, and `tokenize` asks again at the same spot.  `m.end() > pos` makes that rule count as no match, so the next rule gets its turn.
19. It reads `line`, `col`, and `message`.  With only a formatted string, it would have to pick those values back out of the text, and any change to the wording would break it.
20. The lexer can no longer forget its error case.  With a catch-all rule, a spec that omits it would make `finditer` skip the unmatched characters without a word.  Here the error lives in the code, so it applies to every spec the lexer loads.
21. `LET` would report column 4, where the next token's space begins.  Each token would report where the next piece starts rather than where it starts itself.
22. It would have to compare `tok.value` against the keyword text at every decision, as in `tok.type == "KEYWORD" and tok.value == "let"`.  The parser would be redoing lexical work, and `expect` could no longer say which keyword it wanted by type alone.
23. `LE` and `LT`, `GE` and `GT`, `EQEQ` and `EQ`, `NEQ` and `BANG`, `ARROW` and `MINUS`.  In each pair, the longer operator starts with the shorter one, so the longer one goes first.
24. `->` prints `['MINUS', 'GT']`.  A parser reading `fun f() -> Num { ... }` would find `MINUS` where the grammar allows only `ARROW` or a block, and it would report a syntax error at a line that is correct.
25. `3.` lexes as `INT 3`, and then the `.` raises `unexpected character '.'`.  `.5` raises at the `.` right away.  Either choice is defensible if you can say why.  Requiring digits on both sides keeps the rule simple and makes these typos into errors, while accepting `3.` and `.5` is friendlier and matches Python.
26. The refill inside `advance` runs into the `@` while it is fetching the next token, so `advance` raises and the parser never receives `let`.  The error is reported for a token the parser did not ask for yet.  With filling on demand, `advance` returns `let`, and the error comes when the parser next asks for a token.
27. `_fill` changes the internal state only by moving a token from the generator into the buffer.  It consumes nothing that the parser can see: every call to `peek` returns the same token, and the following `advance` returns that token too.  What matters is what the parser can observe.
28. The token is still there for the message.  The parser can report what it found and where, and a higher-level rule can peek at the same token and try something else.  When the token is already consumed, the parser has moved past the place where the problem happened.
29. The `STRING` token is everything from the first quote through the opening quote on the next line: `"open`, a newline, and `let b = "`.  The first error then lands at the quote after the `x`, on a line that the programmer wrote correctly.  Excluding `\n` keeps the error on the line with the real mistake.
30. A wrong answer here can only come from `decode` or `ESCAPES`.  Through `tokenize`, the same symptom could also come from the `STRING` rule, the slice that strips the quotes, or the `Token` field.  Checking the piece alone narrows the search to a few lines.
31. The quotes and the backslash escapes would end up inside your string values, so `print "a\nb";` would print the quotes and a backslash and an `n`.  `tok.value` is useful where you want the source text exactly as written, such as in an error message that quotes the literal.
32. The opening quote is where the string the programmer forgot to close begins.  The end of the line only tells them where the lexer gave up, and in a long file that can look like a different problem.
33. The two copies drift.  `Lexer(source)` knows the new rule, and `Lexer(source, "token_spec.json")` does not.  `test_default_file_matches_builtin` in Build Step 32 catches this for the source it tests, so a good habit is to run `make_spec.py` whenever you edit the list.
34. It could say only that the combined pattern failed to compile, with an offset into a very long string.  You would have to count your way back to the rule at fault.  Compiling each rule on its own means the `except` knows `name`.
35. Only `Lexer(source, "token_spec.json")` sees it.  So edit the list first, and then regenerate the file, and the two runs will agree.
36. `EQ` must sit above `COLON`, so that `:=` is not cut into `COLON` and a leftover `=`.  `COMMENT` must sit above `SLASH`, so that `//` is not two `SLASH` tokens.  Yes: `COMMENT` is first, and `EQ` comes before the block of one-character rules that holds `COLON`.  Your `alt_rules` keep that order, because they change only the patterns.
37. The `COMMENT` rule does the work.  `comment_char` only records the choice for a person reading the file.  To make it control comments, `load_spec` would read it and build the `COMMENT` pattern with `re.escape(comment_char) + r"[^\n]*"`.  The dialect file would then state the comment marker once rather than twice.
38. Not until the first `peek` or `advance`, because a generator's body does not start until someone asks for a value.  Even then, `tokenize` would need an explicit check, because any mode other than `fail_fast` would quietly act like `collect_all`.  Checking in `__init__` reports the typo on the line that made it.
39. It raises `StopIteration`, because `next` runs on a finished generator.  The parser does not hit this because it stops at the first error it receives.  It does not catch a lexical error and then keep reading from the same lexer.  If you want the contract to hold here too, `_fill` can catch `StopIteration` the way Model 3 did.
40. The parser will reach the lexer only through `peek` and `advance`, so a test through those methods covers the path the parser will use, including the buffer.  A bug in `Lexer` could hide from a test that calls only `tokenize`.
41. Any edit that puts a shorter rule above its longer partner works.  For example, move `ARROW` below `MINUS`, and `test_munch_arrow` fails with `['MINUS', 'GT']`.  Moving `IDENT` above the keywords also works, but it breaks other tests instead, because `iffy` is an `IDENT` either way.  That is worth noticing: `test_munch_iffy` guards the boundary check, not this order.
42. Without the `r`, Python puts a real tab into the source string before the lexer sees it.  The test still passes, because a real tab is an ordinary string character, but it no longer tests the escape at all.
43. `@dataclass` writes `__eq__`, which compares the fields.  A plain class would compare object identity.  That would pass here, because `peek` returns the same object, but it would fail a comparison between two separately built lists, as in Build Step 31.
44. The first helper would use up the tokens, and the second would see only `EOF`.  The comparison would then fail for a reason that has nothing to do with the lexer's contract.
45. The newline bookkeeping in `advance_position`, or the line that calls it in `tokenize`.  If `line` never grows, every error reports line 1.
46. A parser in `collect_all` mode sees good tokens first and hears about errors only at the end, so it may do work on a program that is already known to be bad.  In return, the tokens still come out one at a time, in the same order, and the same `peek` and `advance` calls work in both modes.
47. A new dialect that only changes patterns is a new JSON file.  A new keyword or operator is one rule in the table plus a run of `make_spec.py`.  New Python is still needed when a token needs behavior beyond a pattern, as `STRING` needed `decode`, or when the lexer needs state, as significant indentation would.

---

