---
layout: assignment
permalink: /Assignments/Regex
title: "CS374: Principles of Programming Languages - Regular Expressions"

info:
  coursenum: CS374
  purpose: "To build a working command of regular expressions by writing a tested pattern library, a finditer-based mini lexer, and a realistic log parser, and to learn the vocabulary you need to explain why a pattern behaves the way it does."
  tilt:
    task: "Work through four scaffolded parts: a ten-pattern library, a re.finditer mini lexer, a regex text transformer and log parser, and a written analysis of regex limits."
    criteria: "I grade this on the correctness of your patterns, mini lexer, and log parser, and on the depth of your greedy/lazy, anchors, and Chomsky-limits analysis.  Each part is worth 25 points, and the rubric below spells out each row."
  points: 100
  goals:
    - To write and test a library of regular expressions for real-world data patterns
    - To build a mini lexer using re.finditer and a TOKEN_SPEC ordered list
    - To apply regular expressions to realistic log-parsing and data-extraction tasks
    - To articulate the difference between greedy and lazy quantifiers, anchors, and capture groups
    - To explain the theoretical limits of regular languages and connect them to the Chomsky hierarchy
  rubric:
    - weight: 25
      description: "Pattern Library (Goal 1)"
      preemerging: Fewer than five patterns are provided, or most patterns match clearly wrong strings on the provided test cases
      beginning: Most patterns are provided, but several fail on edge cases (e.g., missing anchors allow partial matches, or character classes are too broad or too narrow)
      progressing: All ten patterns pass the provided positive and negative test cases, but two or more patterns have minor issues that would fail on hidden test inputs (e.g., permitting leading zeros in integers, or not anchoring a pattern that should be anchored)
      proficient: All ten patterns pass all provided and hidden test cases; every pattern is a raw string; each pattern is named, each non-trivial construct has a one-sentence explanation, and each pattern is tested with at least three positive and two negative cases through the check() harness
    - weight: 25
      description: "Mini Lexer with re.finditer (Goal 2)"
      preemerging: The mini lexer is not implemented, or it uses re.match in a loop rather than re.finditer with alternation
      beginning: The mini lexer uses finditer, but the TOKEN_SPEC ordering is wrong (e.g., keywords are not listed before identifiers), so some inputs get incorrect token types
      progressing: The mini lexer produces correct token types for most inputs, but one or more token types are misclassified, and gaps between matches (unrecognized characters) are not detected
      proficient: The mini lexer uses a single compiled alternation pattern with named groups; produces the correct token type and value for every input; detects and reports gaps (unrecognized characters) with their position; and handles the maximal-munch ordering correctly for all test cases
    - weight: 25
      description: "Text Transformer and Log Parser (Goals 1, 3)"
      preemerging: Neither the transformer nor the log parser is implemented, or both produce clearly wrong output
      beginning: One of the two is implemented but produces incorrect output on several provided inputs (e.g., the date conversion uses the wrong group references, or the log parser drops some records)
      progressing: Both are implemented and produce correct output on the provided inputs, but the log parser does not handle malformed lines, or the transformer does not handle edge cases (e.g., dates at the start or end of a string)
      proficient: Both the text transformer and the log parser work correctly on all provided and hidden inputs; malformed log lines are detected and reported with their line number; the configuration lives in a JSON file; and the errors.txt output is generated correctly
    - weight: 25
      description: "Pattern Analysis and Limits Discussion (Goals 4, 5)"
      preemerging: No analysis is provided, or the analysis restates the course notes without applying the concepts to the student's own patterns
      beginning: The analysis addresses greedy vs. lazy and anchors, but the explanations are superficial and the examples do not clearly show the difference
      progressing: The analysis covers greedy vs. lazy, anchors, and groups with working examples, but the Chomsky hierarchy discussion is missing or incorrect
      proficient: The analysis demonstrates greedy vs. lazy with a concrete input where the two produce different results, explains anchors with a pattern that fails without them, explains named groups with groupdict(), and includes a correct paragraph on why balanced parentheses require a context-free grammar, naming the Chomsky level and the pipeline component that handles it
  readings:
    - rtitle: "Regular Expressions Activity"
      rlink: "Activities/liascript-regex.md"
      liapage: true
    - rtitle: "Python re Documentation"
      rlink: "https://docs.python.org/3/library/re.html"

tags:
  - regex
  - languages

---

In this assignment you write regular expressions, test them, and use them to build a small lexer, a text transformer, and a log parser.  A regular expression (regex) is a pattern that describes a set of strings, and Python's `re` module matches text against such patterns.  The assignment has four parts worth 25 points each.  Each part is tested on its own, so complete them in order.  Write every pattern as a raw string (`r"..."`) so that backslashes reach the regex engine unchanged.  Part 4 is a written analysis, and it ends with a question about what regular expressions cannot do; answer it in your writeup.

---

## Getting Started

### Environment and Setup

You need Python 3.10 or newer; run `python --version` to confirm.  The `re` and `json` modules are part of the standard library, so there is nothing to install.  Create these files now so each part has a home:

```
patterns.py      # Part 1
mini_lexer.py    # Part 2
transformer.py   # Part 3a-3b
log_parser.py    # Part 3c
config.json      # Part 3c configuration
readme.md        # Part 4 answers
```

### Your First 30 Minutes

Get one pattern passing before you write any others:

1.  Copy the `check()` harness from Part 1 into `patterns.py`.
2.  Add pattern P1, `COURSE_CODE`, and its test call:

```python
COURSE_CODE = r"[A-Z]{2,4}-?\d{3}"

check("COURSE_CODE", COURSE_CODE,
      should_match=["CS374", "MATH111", "BIO-101"],
      should_not_match=["cs374", "CS3741"])
```

3.  Run `python patterns.py` and confirm that you see a `PASS` line.
4.  Break the pattern on purpose: remove the `-?` and run again.  Watch `check()` report the failure.

That loop (edit, run, read the failure) is the whole workflow for Part 1.  Once it works for one pattern, the other nine repeat the same cycle.

This assignment goes out alongside the Regular Expressions class session and the Regex Workshop lab.  The lab is due mid-assignment, and it completes your first patterns and the mini lexer skeleton for you.  Bring your lab files straight into Parts 1 and 2: the lab is a head start on this assignment, not separate work.

### Suggested Pacing

See the course schedule for the assigned and due dates.  A suggested sequence:

| Checkpoint | You should have |
|------------|----------------|
| On assignment | `check()` harness working (from the Regex Workshop lab); patterns P1-P3 passing |
| Checkpoint 1 | Part 1 complete: all ten patterns with test cases |
| Lab due | Part 2 complete: mini lexer (grown from the lab's skeleton) passing the ordering table |
| Checkpoint 2 | Part 3 complete: transformer and log parser producing the sample output |
| Due date | Part 4 analysis written; deliverables assembled and submitted |

---

## Part 1: Pattern Library (25 points)

Part 1 asks for ten tested patterns.  You test each one with the `check()` harness below, which reports every string that matched when it should not have, and every string that failed to match when it should have.

### The check() Harness

Add this harness to `patterns.py` once, before you write any patterns:

```python
import re

def check(name: str, pattern: str, should_match: list, should_not_match: list):
    """Run pattern against positive and negative test cases. Report all failures."""
    compiled = re.compile(pattern)
    failures = []
    for s in should_match:
        if not compiled.fullmatch(s):
            failures.append(f"  SHOULD match but did NOT: {s!r}")
    for s in should_not_match:
        if compiled.fullmatch(s):
            failures.append(f"  Should NOT match but DID: {s!r}")
    if failures:
        print(f"FAIL {name}:")
        for f in failures: print(f)
    else:
        print(f"PASS {name} ({len(should_match)} positive, {len(should_not_match)} negative)")
```

`fullmatch` succeeds only when the pattern matches the entire string, from the first character to the last.  That is deliberate.  A pattern that matches only the first part of `CS3741` is too permissive, and `fullmatch` exposes it.

### Required Patterns (10 total)

Write a `re.compile`d pattern for each item below.  Use the name shown, and test each pattern with `check()` using at least three positive and two negative cases.  The lists under each pattern give you starting cases.

**P1 `COURSE_CODE`:** Ursinus course codes: two to four capital letters, an optional hyphen, then exactly three digits.
- Match: `CS374`, `MATH111`, `BIO-101`, `ENGL-201`
- No match: `cs374`, `CS3741`, `CS-37`, `374`

**P2 `IDENTIFIER`:** A legal programming identifier.  It starts with a letter or underscore, and any mix of letters, digits, and underscores may follow.  The pattern must match the full string.
- Match: `foo`, `_bar`, `x1`, `my_var_2`
- No match: `1foo`, `-x`, `foo bar`, `"x"`

**P3 `DECIMAL`:** A decimal number with an optional sign and an optional fractional part.  The integer part is required, so a bare `.` or a trailing dot such as `3.` is not valid.
- Match: `3`, `-3`, `+3.14`, `0.5`, `-0.001`
- No match: `.5`, `3.`, `--3`, `3..14`, `abc`

**P4 `TIME_12H`:** A 12-hour clock time.  The hour is 1-12.  Minutes are optional, but when present they must be two digits.  The meridiem (`AM` or `PM`) is required and follows a single space.
- Match: `8 AM`, `12:00 PM`, `1:30 AM`, `11:59 PM`
- No match: `13:00 AM`, `0:00 AM`, `8:5 PM`, `8AM`, `8:00`

**P5 `EMAIL`:** A practical email address (not RFC-compliant): one or more word characters or dots before `@`, then a domain of word characters and dots with at least one dot.
- Match: `user@example.com`, `bill.j@ursinus.edu`, `x@y.z`
- No match: `@example.com`, `user@`, `user@com`, `user @example.com`

**P6 `US_PHONE`:** A US phone number in the format `(NXX) NXX-XXXX`, where N is a digit from 2 to 9.
- Match: `(215) 555-1234`, `(800) 123-4567`
- No match: `215-555-1234`, `(015) 555-1234`, `(215)555-1234`

**P7 `ISO_DATE`:** An ISO 8601 date, `YYYY-MM-DD`.  Month is 01-12 and day is 01-31.  A regex cannot check how many days a particular month has, so validate only the format and these ranges.
- Match: `2026-09-18`, `2000-01-01`, `1999-12-31`
- No match: `26-09-18`, `2026-9-18`, `2026-13-01`, `2026-00-15`

**P8 `HEX_COLOR`:** A CSS hex color: a `#` followed by exactly 3 or 6 hexadecimal digits, in either upper or lower case.
- Match: `#fff`, `#FFF`, `#1a2b3c`, `#ABC`
- No match: `#gg1122`, `fff`, `#1234`, `#12345g`

**P9 `IPV4_ADDRESS`:** An IPv4 address: four groups of 1-3 digits separated by dots.  Validate the format and the 1-3 digit length of each octet.  Checking the 0-255 range is encouraged but not required.
- Match: `192.168.1.1`, `10.0.0.0`, `255.255.255.255`, `0.0.0.0`
- No match: `192.168.1`, `192.168.1.1.1`, `abc.def.ghi.jkl`

**P10 `MARKDOWN_LINK`:** A Markdown hyperlink `[text](url)`, where text is any run of non-`]` characters and url is any run of non-`)` characters.
- Match: `[Google](https://google.com)`, `[CS374](../index.html)`, `[x](y)`
- No match: `[Google]`, `(https://google.com)`, `Google(https://google.com)`

---

## Part 2: Mini Lexer Using re.finditer (25 points)

Part 2 builds a lexer, a program that splits source text into tokens, out of a single regex and `re.finditer`.  A token is a labeled piece of source text such as a keyword, a number, or an operator.

### The finditer Approach

A production lexer does not call `re.match` in a loop at each position.  Instead it joins every token pattern into one large alternation (a list of patterns separated by `|`) and calls `re.finditer`, which returns every non-overlapping match in a single pass.  Each alternative is a named group, `(?P<NAME>pattern)`, so each match reports which token rule fired through `m.lastgroup`.

```python
import re

TOKEN_SPEC = [
    ("WHITESPACE",  r"[ \t\n]+"),
    ("FLOAT",       r"\d+\.\d+"),
    ("INT",         r"\d+"),
    ("IF",          r"if(?!\w)"),   # negative lookahead prevents matching "iffy"
    ("IDENT",       r"[a-zA-Z_]\w*"),
    ("PLUS",        r"\+"),
    ("MINUS",       r"-"),
    ("EQ",          r"="),
    ("LPAREN",      r"\("),
    ("RPAREN",      r"\)"),
    ("SEMICOLON",   r";"),
]

# Build the master pattern: (?P<NAME>pattern)|(?P<NAME2>pattern2)|...
MASTER = re.compile(
    "|".join(f"(?P<{name}>{pat})" for name, pat in TOKEN_SPEC)
)
```

Order matters in `TOKEN_SPEC`.  At each position the engine tries the alternatives left to right and takes the first one that matches.  So `FLOAT` must come before `INT` (otherwise `3.14` lexes as `3`), and every keyword must come before `IDENT`.  This ordering is how the alternation achieves maximal munch, the rule that a lexer takes the longest token available at each position.  The `(?!\w)` after `if` is a negative lookahead: it succeeds only when the next character is not a word character, so `iffy` falls through to `IDENT`.

### Step 2a: Implement mini_lex()

Add `mini_lex()` to `mini_lexer.py`.  It walks the matches in order and checks that each match starts where the previous one ended.  Any gap means a character matched no rule, and the function raises `LexError` at that position.  `LexError` is not defined in this snippet; declare it as an `Exception` subclass in your file.

```python
def mini_lex(source: str) -> list:
    """Return a list of (token_type, value, start_pos) tuples, skipping whitespace.
    Raise LexError on any character that matches no rule (a gap in finditer coverage)."""
    tokens = []
    pos = 0
    for m in MASTER.finditer(source):
        if m.start() != pos:
            raise LexError(f"Unrecognized character {source[pos]!r} at position {pos}")
        kind = m.lastgroup
        if kind != "WHITESPACE":
            tokens.append((kind, m.group(), m.start()))
        pos = m.end()
    if pos != len(source):
        raise LexError(f"Unrecognized character {source[pos]!r} at position {pos}")
    return tokens
```

### Step 2b: Extend the Token Spec

Extend `TOKEN_SPEC` to cover the language in the table below.  Use at least 15 token types, and include every keyword, operator, and literal listed.  Put the negative lookahead `(?!\w)` on every keyword so that `iffy` does not tokenize as `IF`.

| Category | Tokens |
|----------|--------|
| Keywords | `if`, `else`, `while`, `let`, `print`, `true`, `false`, `and`, `or`, `not`, `fun` |
| Literals | `INT` (`42`), `FLOAT` (`3.14`), `STRING` (`"hello"`), `IDENT` (`my_var`) |
| Two-char operators | `<=`, `>=`, `==`, `!=`, `->` |
| One-char operators | `=`, `<`, `>`, `+`, `-`, `*`, `/`, `!` |
| Punctuation | `(`, `)`, `{`, `}`, `;`, `:`, `,` |
| Skipped | whitespace, `# comment to end of line` |

The Lexer assignment asks you to tokenize this same language with a reusable component, so the work you do here carries forward directly.  The table above has everything you need; you do not need that assignment sheet to finish this one.

### Step 2c: Verify Ordering and Maximal Munch

Run `mini_lex` on each input below and confirm that the output matches the expected token types.  If `iffy` comes back as `IF`, or `3.14` comes back as `INT`, fix the order of `TOKEN_SPEC`.

| Input | Expected |
|-------|----------|
| `if` | `[("IF", "if", 0)]` |
| `iffy` | `[("IDENT", "iffy", 0)]` |
| `3.14` | `[("FLOAT", "3.14", 0)]` |
| `3` | `[("INT", "3", 0)]` |
| `let x = 1;` | `LET IDENT EQ INT SEMICOLON` |
| `@` | `LexError at position 0` |

---

## Part 3: Regex-Based Text Transformer and Log Parser (25 points)

Part 3 uses regexes to change text and to pull structured data out of a log file.  It has three steps: a text transformer, a greedy versus lazy demonstration, and a log parser.

### Step 3a: Text Transformer

In `transformer.py`, write a `transform(text: str) -> str` function that applies these three substitutions, in this order:

1.  Redact emails: replace every email address with `[EMAIL]` using `re.sub`.  Use P5 from Part 1 without anchoring, because the address sits inside a longer sentence.
2.  Normalize dates: convert `MM/DD/YYYY` dates to ISO `YYYY-MM-DD`.  Capture month, day, and year as groups, then reorder them with group references in the replacement string (e.g., `r"\3-\1-\2"`).
3.  Redact phone numbers: replace US phone numbers (P6 from Part 1) with `[PHONE]`.

Demonstrate the function on this input paragraph:

```
Contact MONGAN, WILLIAM at billmongan@gmail.com or call (610) 555-0192.
The registration deadline was 09/01/2026.
A second contact: support@ursinus.edu, deadline 12/15/2026.
```

Expected output (approximately):

```
Contact MONGAN, WILLIAM at [EMAIL] or call [PHONE].
The registration deadline was 2026-09-01.
A second contact: [EMAIL], deadline 2026-12-15.
```

### Step 3b: Greedy vs. Lazy Demonstration

A greedy quantifier (`*`) matches as much text as it can.  A lazy quantifier (`*?`) matches as little as it can.  Show one input string and two patterns where the two produce different captures:

```python
import re
text = '<b>bold</b> and <i>italic</i>'
greedy = re.search(r'<.*>',  text)   # greedy
lazy   = re.search(r'<.*?>', text)   # lazy
print(f"Greedy: {greedy.group()!r}")
print(f"Lazy:   {lazy.group()!r}")
```

Expected:

```
Greedy: '<b>bold</b> and <i>italic</i>'
Lazy:   '<b>'
```

In a comment, explain in one sentence why greedy captured more.

### Step 3c: Log Parser

In `log_parser.py`, write a `parse_log(log_path: str, config_path: str)` function for the provided server log.  Each line looks like `2026-09-18 08:10:22 WARN disk usage 91% on /dev/sda1`.  The function must:

1.  Use one `re.finditer` pattern with named groups to extract `date`, `time`, `level`, and `message` from each log line.
2.  Report counts by level (how many INFO, WARN, and ERROR lines).
3.  Report the earliest and latest timestamps, as strings in `YYYY-MM-DD HH:MM:SS` format.
4.  Extract every percentage value (`\d+%`) mentioned in WARN lines and report the maximum.
5.  Write all ERROR lines, each prefixed with its original line number, to `errors.txt`.

The named-group pattern must match this line format exactly:

```
YYYY-MM-DD HH:MM:SS LEVEL message text here
```

Sample output:

```
Counts: INFO=42, WARN=8, ERROR=3
Earliest: 2026-09-01 00:01:14
Latest:   2026-09-18 23:59:59
Max WARN percentage: 91%
ERROR lines written to errors.txt
```

Store both the input log path and the output `errors.txt` path in a JSON configuration file rather than in the code:

```json
{
  "log_path": "server.log",
  "errors_path": "errors.txt"
}
```

---

## Part 4: Pattern Analysis (25 points)

Answer the four questions below in `readme.md`.  Each answer must be at least one paragraph and must include a concrete example from your own work in this assignment.

### Q1: Greedy vs. Lazy

Explain the difference between greedy (`*`, `+`) and lazy (`*?`, `+?`) quantifiers, using the specific example from Step 3b.  Then state when you would prefer lazy over greedy in production code.

### Q2: Anchors

An anchor is a pattern element that matches a position rather than a character.  Explain the difference between `^`, `$`, `\A`, and `\Z`.  Show a pattern from your Part 1 library where removing the anchors (or switching from `fullmatch` to `search`) would cause a false positive.  State which anchor approach you used in each Part 1 pattern and why.

### Q3: Named Groups

Explain the difference between plain groups `(...)`, non-capturing groups `(?:...)`, and named groups `(?P<name>...)`.  Show how `groupdict()` differs from `groups()` using your log parser pattern from Step 3c.

### Q4: The Limits of Regular Expressions

In one paragraph, explain why no regular expression can validate balanced nested parentheses in general.  Your explanation must:
- Reference the pumping lemma for regular languages (by name; you do not need to reproduce the full proof) (taught in the Regular Expressions class session with a worked example; see Allison Ch. 4).
- Name the level of the Chomsky hierarchy that handles context-free languages.
- Name the component of your language pipeline (from the Lexer, Parser, and Interpreter assignments) whose job it is to handle balanced nesting.

---

## Deliverables

Submit a ZIP containing:
- `patterns.py`: all ten patterns with the check() harness and test calls
- `mini_lexer.py`: the mini lexer with extended TOKEN_SPEC
- `transformer.py`: the text transformer
- `log_parser.py`: the log parser
- `config.json`: the log parser configuration
- `errors.txt`: the generated errors file from the provided log
- `test_output.txt`: output of running all four modules
- `readme.md`: approximately one page including the four analysis answers and the limits paragraph

List your Python version so that your results can be reproduced.

---

## Grading Breakdown

| Component | Points |
|-----------|--------|
| Part 1: Pattern Library | 25 |
| Part 2: Mini Lexer with re.finditer | 25 |
| Part 3: Text Transformer and Log Parser | 25 |
| Part 4: Pattern Analysis | 25 |
| **Total** | **100** |

---

## Reflection Prompts

- Which pattern took the most revisions, and what misconception did the failures expose?
- Where did you choose a simpler pattern over a perfectly precise one, and how did you document the tradeoff?
- After completing Part 2, what are the limits of a regex-only lexer?  Name one thing this `finditer` loop cannot do that a hand-written scanner with `peek`/`advance` can.  You'll build exactly that in the Lexer assignment.
- If collaboration with a buddy was permitted, did you work with a buddy on this assignment?  If so, who?  If not, do you certify that this submission represents your own original work?  Please identify any and all portions of your submission that were not originally written by you.
- AI disclosure: list any generative-AI tools you used, for what, and how you verified the results (or state 'none').
- Approximately how many hours it took you to finish this assignment (I will not judge you for this at all; I am simply using it to gauge if the assignments are too easy or hard)?
