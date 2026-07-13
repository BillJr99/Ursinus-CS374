---
layout: assignment
permalink: /Assignments/Regex
title: "CS374: Principles of Programming Languages - Regular Expressions"

info:
  coursenum: CS374
  purpose: "To build a working command of regular expressions — writing tested pattern libraries, a finditer-based mini lexer, and realistic data extraction — plus the vocabulary to reason about why a pattern behaves the way it does."
  tilt:
    task: "Work through four scaffolded parts: a ten-pattern library, a re.finditer mini lexer, a regex text transformer and log parser, and a written analysis of regex limits."
    criteria: "Assessed on the correctness of your patterns, mini lexer, and log parser and the depth of your greedy/lazy, anchors, and Chomsky-limits analysis, each part worth 25 points; see the rubric below for the full breakdown."
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
      beginning: Most patterns are provided but several fail on edge cases (e.g., missing anchors allow partial matches, or character classes are too broad or too narrow)
      progressing: All ten patterns pass the provided positive and negative test cases, but two or more patterns have minor issues that would fail on hidden test inputs (e.g., permitting leading zeros in integers, or not anchoring a pattern that should be anchored)
      proficient: All ten patterns pass all provided and hidden test cases; raw strings are used throughout; each pattern is named, accompanied by a one-sentence explanation of each non-trivial construct, and tested with at least three positive and two negative cases via the check() harness
    - weight: 25
      description: "Mini Lexer with re.finditer (Goal 2)"
      preemerging: The mini lexer is not implemented, or it uses re.match in a loop rather than re.finditer with alternation
      beginning: The mini lexer uses finditer but the TOKEN_SPEC ordering is wrong (e.g., keywords not before identifiers), producing incorrect token types for some inputs
      progressing: The mini lexer produces correct token types for most inputs, but one or more token types are misclassified and gaps between matches (unrecognized characters) are not detected
      proficient: The mini lexer uses a single compiled alternation pattern with named groups; produces correct token type and value for every input; detects and reports gaps (unrecognized characters) with their position; and handles the maximal-munch ordering correctly for all test cases
    - weight: 25
      description: "Text Transformer and Log Parser (Goals 1, 3)"
      preemerging: Neither the transformer nor the log parser is implemented, or both produce clearly wrong output
      beginning: One of the two is implemented but produces incorrect output on several provided inputs (e.g., date conversion uses the wrong group references, or the log parser drops some records)
      progressing: Both are implemented and produce correct output on the provided inputs, but the log parser does not handle malformed lines, or the transformer does not handle edge cases (e.g., dates at the start or end of a string)
      proficient: Both the text transformer and the log parser work correctly on all provided and hidden inputs; malformed log lines are detected and reported with their line number; the configuration is externalized in a JSON file; and the errors.txt output is generated correctly
    - weight: 25
      description: "Pattern Analysis and Limits Discussion (Goals 4, 5)"
      preemerging: No analysis is provided, or the analysis is a generic restatement of course notes without applying concepts to the student's patterns
      beginning: The analysis addresses greedy vs. lazy and anchors, but the explanations are superficial and the examples do not clearly illustrate the difference
      progressing: The analysis covers greedy vs. lazy, anchors, and groups with working examples, but the Chomsky hierarchy discussion is missing or incorrect
      proficient: The analysis demonstrates greedy vs. lazy with a concrete input where the two produce different results, explains anchors with a pattern that fails without them, explains named groups with groupdict(), and includes a correct paragraph on why balanced parentheses require a context-free grammar, naming the Chomsky level and the pipeline component that handles it
  readings:
    - rtitle: "Regular Expressions Activity"
      rlink: "https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374/gh-pages/_pages/Activities/liascript-regex.md"
    - rtitle: "Python re Documentation"
      rlink: "https://docs.python.org/3/library/re.html"

tags:
  - regex
  - languages

---

In this assignment you will build fluency with regular expressions in four scaffolded parts, ending with a realistic log-extraction task. Use raw strings (`r"..."`) throughout. Each part is independently tested; do not skip ahead. The assignment concludes with a theoretical limits question that you must answer in your writeup.

---

## Getting Started

### Environment and Setup

You need Python 3.10+ (`python --version` to confirm) and nothing else — `re` and `json` are in the standard library. Create the files you will submit up front, so each part has a home:

```
patterns.py      # Part 1
mini_lexer.py    # Part 2
transformer.py   # Part 3a-3b
log_parser.py    # Part 3c
config.json      # Part 3c configuration
readme.md        # Part 4 answers
```

### Your First 30 Minutes

Copy the `check()` harness from Part 1 into `patterns.py`, then write and test exactly one pattern — P1, `COURSE_CODE`:

```python
COURSE_CODE = r"[A-Z]{2,4}-?\d{3}"

check("COURSE_CODE", COURSE_CODE,
      should_match=["CS374", "MATH111", "BIO-101"],
      should_not_match=["cs374", "CS3741"])
```

Run `python patterns.py` and confirm you see a `PASS` line. Then break it on purpose: remove the `-?` and rerun to watch `check()` report the failure. That edit-run-read-failure loop is the whole workflow for Part 1 — once it works for one pattern, the remaining nine are repetitions of the same cycle.

This assignment is handed out on Tuesday, September 15 — the day of the dedicated Regular Expressions class session — alongside the **Regex Workshop lab**, which is due one week later and completes your first patterns and the mini-lexer skeleton for you. Bring your lab artifacts into Parts 1 and 2 directly: the lab is a head start on this assignment, not separate work.

### Suggested Pacing

This assignment is handed out on Tuesday of week 3 and due on Thursday of week 4:

| Checkpoint | You should have |
|------------|----------------|
| Week 3 (Tue) — assigned | `check()` harness working (from the Regex Workshop lab); patterns P1–P3 passing |
| Week 3 (Thu) | Part 1 complete: all ten patterns with test cases |
| Week 4 (Tue) — lab due | Part 2 complete: mini lexer (grown from the lab's skeleton) passing the ordering table |
| Midweek | Part 3 complete: transformer and log parser producing the sample output |
| Week 4 (Thu) — due | Part 4 analysis written; deliverables assembled and submitted |

---

## Part 1: Pattern Library (25 points)

### The check() Harness

Before writing any patterns, implement this harness once:

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

Note: `fullmatch` requires the pattern to match the *entire* string. This is intentional — anchoring the test exposes patterns that are too permissive.

### Required Patterns (10 total)

Write a `re.compile`d pattern for each, named as shown, with **at least three positive and two negative test cases** via `check()`.

**P1 — `COURSE_CODE`:** Ursinus course codes: two to four capital letters, an optional hyphen, then exactly three digits.
- Match: `CS374`, `MATH111`, `BIO-101`, `ENGL-201`
- No match: `cs374`, `CS3741`, `CS-37`, `374`

**P2 — `IDENTIFIER`:** A legal programming identifier: starts with a letter or underscore, followed by any combination of letters, digits, and underscores. Must match the full string.
- Match: `foo`, `_bar`, `x1`, `my_var_2`
- No match: `1foo`, `-x`, `foo bar`, `"x"`

**P3 — `DECIMAL`:** A decimal number with an optional sign and optional fractional part. The integer part is required; a bare `.` or a number like `3.` (trailing dot without digits) is not valid.
- Match: `3`, `-3`, `+3.14`, `0.5`, `-0.001`
- No match: `.5`, `3.`, `--3`, `3..14`, `abc`

**P4 — `TIME_12H`:** A 12-hour clock time. Hour is 1–12. Minutes are optional but, if present, must be two digits. Meridiem (`AM` or `PM`) is required and separated by a space.
- Match: `8 AM`, `12:00 PM`, `1:30 AM`, `11:59 PM`
- No match: `13:00 AM`, `0:00 AM`, `8:5 PM`, `8AM`, `8:00`

**P5 — `EMAIL`:** A practical (not RFC-compliant) email address: one or more word characters or dots before `@`, then a domain of word characters and dots with at least one dot.
- Match: `user@example.com`, `bill.j@ursinus.edu`, `x@y.z`
- No match: `@example.com`, `user@`, `user@com`, `user @example.com`

**P6 — `US_PHONE`:** A US phone number in the format `(NXX) NXX-XXXX` where N is 2–9.
- Match: `(215) 555-1234`, `(800) 123-4567`
- No match: `215-555-1234`, `(015) 555-1234`, `(215)555-1234`

**P7 — `ISO_DATE`:** An ISO 8601 date `YYYY-MM-DD`. Month 01–12, day 01–31 (exact day-of-month validation is beyond regex — just validate the format and ranges).
- Match: `2026-09-18`, `2000-01-01`, `1999-12-31`
- No match: `26-09-18`, `2026-9-18`, `2026-13-01`, `2026-00-15`

**P8 — `HEX_COLOR`:** A CSS hex color: a `#` followed by exactly 3 or 6 hex digits (case-insensitive).
- Match: `#fff`, `#FFF`, `#1a2b3c`, `#ABC`
- No match: `#gg1122`, `fff`, `#1234`, `#12345g`

**P9 — `IPV4_ADDRESS`:** An IPv4 address: four groups of 1–3 digits separated by dots. (Exact 0–255 range validation is encouraged but not required — validate format and that each octet is 1–3 digits.)
- Match: `192.168.1.1`, `10.0.0.0`, `255.255.255.255`, `0.0.0.0`
- No match: `192.168.1`, `192.168.1.1.1`, `abc.def.ghi.jkl`

**P10 — `MARKDOWN_LINK`:** A Markdown hyperlink `[text](url)` where text is any non-`]` characters and url is any non-`)` characters.
- Match: `[Google](https://google.com)`, `[CS374](../index.html)`, `[x](y)`
- No match: `[Google]`, `(https://google.com)`, `Google(https://google.com)`

---

## Part 2: Mini Lexer Using re.finditer (25 points)

### The finditer Approach

Rather than calling `re.match` in a loop at each position, a production lexer builds one large alternation pattern and uses `re.finditer` to find all non-overlapping matches in a single pass.

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

### Step 2a: Implement mini_lex()

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

Extend TOKEN_SPEC to cover the full language from the Lexer assignment (at least 15 token types, including all keywords, operators, and literals from Part 1 of the Lexer assignment). Use negative lookahead `(?!\w)` on all keywords to prevent `iffy` from tokenizing as `IF`.

### Step 2c: Verify Ordering and Maximal Munch

Run `mini_lex` on each of these inputs and verify the output matches the expected token types:

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

### Step 3a: Text Transformer

Write a `transform(text: str) -> str` function that applies all three substitutions to the input text:

1. **Redact emails:** Replace every email address (use P5 from Part 1, without anchoring) with `[EMAIL]` using `re.sub`.
2. **Normalize dates:** Convert `MM/DD/YYYY` format dates to ISO `YYYY-MM-DD` using group references in the replacement string (e.g., `r"\3-\1-\2"` with groups for month, day, year).
3. **Redact phone numbers:** Replace US phone numbers (P6 from Part 1) with `[PHONE]`.

Apply all three in sequence. Demonstrate on this input paragraph:

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

Show a single input string and two patterns where `.*` (greedy) and `.*?` (lazy) produce different captures:

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

In a comment, explain in one sentence *why* greedy captured more.

### Step 3c: Log Parser

Given the provided server log file (lines like `2026-09-18 08:10:22 WARN disk usage 91% on /dev/sda1`), write a `parse_log(log_path: str, config_path: str)` function that:

1. Uses one `re.finditer` pattern with named groups to extract `date`, `time`, `level`, and `message` from each log line.
2. Reports counts by level (how many INFO, WARN, ERROR lines).
3. Reports the earliest and latest timestamps (as strings in `YYYY-MM-DD HH:MM:SS` format).
4. Extracts every percentage value (`\d+%`) mentioned in WARN lines and reports the maximum.
5. Writes all ERROR lines, prefixed with their original line number, to `errors.txt`.

The named-group pattern must match this line format exactly:

```
YYYY-MM-DD HH:MM:SS LEVEL message text here
```

**Sample output:**
```
Counts: INFO=42, WARN=8, ERROR=3
Earliest: 2026-09-01 00:01:14
Latest:   2026-09-18 23:59:59
Max WARN percentage: 91%
ERROR lines written to errors.txt
```

Externalize both the input log path and the output `errors.txt` path in a JSON configuration file:

```json
{
  "log_path": "server.log",
  "errors_path": "errors.txt"
}
```

---

## Part 4: Pattern Analysis (25 points)

Answer each of the following four questions in your writeup. Each answer must be at least one paragraph and must include a concrete example from your own work in this assignment.

### Q1: Greedy vs. Lazy

Explain the difference between greedy (`*`, `+`) and lazy (`*?`, `+?`) quantifiers. Use the specific example from Step 3b. Under what circumstances would you prefer lazy over greedy in production code?

### Q2: Anchors

Explain the difference between `^`, `$`, `\A`, and `\Z`. Show a pattern from your Part 1 library where removing the anchors (or switching from `fullmatch` to `search`) would cause a false positive. State which anchor approach you used in each Part 1 pattern and why.

### Q3: Named Groups

Explain the difference between plain groups `(...)`, non-capturing groups `(?:...)`, and named groups `(?P<name>...)`. Show how `groupdict()` differs from `groups()` using your log parser pattern from Step 3c.

### Q4: The Limits of Regular Expressions

In one paragraph, explain why no regular expression can validate balanced nested parentheses in general. Your explanation must:
- Reference the pumping lemma for regular languages (by name; you do not need to reproduce the full proof) (taught in the Sep 15 session with a worked example; see Allison Ch. 4).
- Name the level of the Chomsky hierarchy that handles context-free languages.
- Name the component of your language pipeline (from the Lexer, Parser, and Interpreter assignments) whose job it is to handle balanced nesting.

---

## Deliverables

Submit a ZIP containing:
- `patterns.py` — all ten patterns with the check() harness and test calls
- `mini_lexer.py` — the mini lexer with extended TOKEN_SPEC
- `transformer.py` — the text transformer
- `log_parser.py` — the log parser
- `config.json` — the log parser configuration
- `errors.txt` — the generated errors file from the provided log
- `test_output.txt` — output of running all four modules
- `readme.md` — approximately one page including the four analysis answers and the limits paragraph

Ensure reproducibility by listing your Python version.

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
- After completing Part 2, what is the main difference between your mini lexer and the Lexer class you built in the Lexer assignment?
- If collaboration with a buddy was permitted, did you work with a buddy on this assignment? If so, who? If not, do you certify that this submission represents your own original work? Please identify any and all portions of your submission that were not originally written by you.
- AI disclosure: list any generative-AI tools you used, for what, and how you verified the results (or state 'none').
- Approximately how many hours it took you to finish this assignment (I will not judge you for this at all — I am simply using it to gauge if the assignments are too easy or hard)?
