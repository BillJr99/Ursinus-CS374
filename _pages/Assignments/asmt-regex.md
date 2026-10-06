---
layout: assignment
permalink: /Assignments/Regex
title: "CS374: Principles of Programming Languages - Regular Expressions"

info:
  coursenum: CS374
  purpose: "To build a working command of regular expressions, starting from Python's re library and the backtracking the engine does when a quantifier has a choice, and ending with a tested pattern library, a text transformer, and a realistic log parser."
  tilt:
    task: "Work through three parts: the re API and backtracking, a tested ten-pattern library built on the check() harness, and a text transformer and log parser."
    criteria: "I grade this on your Part 1 write-ups and on the correctness of your patterns, transformer, and log parser.  The rubric below spells out each row."
  points: 100
  goals:
    - To use Python's re API deliberately, knowing what search, match, findall, sub, and finditer each return, and to explain backtracking as a search over decision points
    - To write and test a library of regular expressions for real-world data patterns against positive and negative cases
    - To apply regular expressions to realistic log-parsing and data-extraction tasks
  rubric:
    - weight: 25
      description: "The re API and Backtracking (Goal 1)"
      preemerging: The cells were not run, or the written answers restate the documentation without evidence from output
      beginning: The cells were run but the findall shape experiment is unanswered, or the answers do not distinguish group(0) from group(1)
      progressing: The questions are answered from real output and the traces are correct, but the finditer rewrite does not report positions
      proficient: Every question is answered from output you produced, the findall shape rule is stated in one sentence you would trust on an exam, and the finditer rewrite prints full text, capture, and start position for each match
    - weight: 40
      description: "Pattern Library and the check() Harness (Goal 2)"
      preemerging: The harness does not run, or fewer than five patterns are provided
      beginning: The harness runs but several patterns fail on edge cases, such as missing anchors that allow partial matches, or character classes that are too broad or too narrow
      progressing: All ten patterns pass the provided positive and negative test cases, but two or more would fail on hidden inputs, for example by permitting leading zeros in an integer or by leaving a pattern unanchored that should be anchored
      proficient: All ten patterns pass all provided and hidden test cases; every pattern is a raw string; each is named, carries a one-sentence explanation of each non-trivial construct, and is tested with at least three positive and two negative cases through the check() harness
    - weight: 35
      description: "Text Transformer and Log Parser (Goals 2, 3)"
      preemerging: Neither the transformer nor the log parser is implemented, or both produce clearly wrong output
      beginning: One of the two is implemented but produces incorrect output on several provided inputs, for example a date conversion using the wrong group references, or a log parser that drops records
      progressing: Both are implemented and produce correct output on the provided inputs, but the log parser does not handle malformed lines, or the transformer fails on edge cases such as dates at the start or end of a string
      proficient: Both work correctly on all provided and hidden inputs; malformed log lines are detected and reported with their line number; the configuration lives in a JSON file; and the errors.txt output is generated correctly
  readings:
    - rtitle: "Regular Expressions Activity"
      rlink: "Activities/liascript-regex.md"
      liapage: true
    - rtitle: "Python re Documentation"
      rlink: "https://docs.python.org/3/library/re.html"
    - rtitle: "regex101 (interactive regex tester; set the Flavor to Python, and switch to PCRE only to use its step-by-step debugger)"
      rlink: "https://regex101.com/"
    - rtitle: "pythex (tests patterns with Python's own re module, in your browser)"
      rlink: "https://pythex.org/"

tags:
  - regex
  - languages

---

In this assignment you learn Python's regular-expression library by running it, then use it to build a tested pattern library, a text transformer, and a log parser.  A regular expression (regex) is a pattern that describes a set of strings, and Python's `re` module matches text against such patterns.  Parts 1 and 2 build the `check()` harness and the pattern library, and Part 3 puts those patterns to work on realistic text.

Work the parts in order, because I test each one on its own and each part uses what the one before it built.  Part 1 is a walkthrough: I show you something, you run it, then you vary it and write down what happened.  Every code block here runs as it stands, so put it in a file, run it, change something, and run it again.  Reading these blocks without running them is the one way to get nothing out of this assignment.  Write every pattern as a raw string (`r"..."`) so that backslashes reach the regex engine unchanged.

**Pair policy.**  Parts 1 and 2 may be done in pairs, with driver and navigator at one screen and a swap at the start of Part 2.  If you pair, you each submit the same files for those parts and name the other in your readme.  Part 3 is individual work.

---

## Getting Started

### Environment and Setup

Before you start, you need:

- Python 3.10 or newer.  The `re` and `json` modules are part of the standard library, so there is nothing to install.
- A text editor (VS Code or any editor you like) and a terminal.  If the terminal is new to you, read the [dev environment page]({{ site.baseurl }}/Tutorials/DevEnvironment) and the [shell primer]({{ site.baseurl }}/Tutorials/ShellForLanguageDev) first; both are short.

Confirm your Python version from the terminal:

```bash
python3 --version
```

You should see one line such as `Python 3.12.3`; any version 3.10 or newer is fine.  If the terminal says `python3` is not found (common on Windows), use `python` in place of `python3` in every command on this page.

> **Do this.** Make a project folder, move into it, and create the six files below: `writeups.md` (Part 1 and the reflection), `patterns.py` (Part 2), `transformer.py` (Part 3), `log_parser.py` and `config.json` (Part 3), and `readme.md`.  Every command on this page runs from inside this folder.  `touch` works in the macOS and Linux shells and in Git Bash on Windows; you can also save each new empty file from your editor into `cs374-regex/`.
>
> ```bash
> mkdir cs374-regex
> cd cs374-regex
> touch writeups.md patterns.py transformer.py log_parser.py config.json readme.md
> ```

> **Time budget.** The three parts are sized roughly alike.  Spread them across the assignment window using the pacing table below.

### Your First 30 Minutes

Get one pattern passing, then break it on purpose, so you know what both outcomes look like.

1. Open `patterns.py` and paste the `check()` harness from Step 2.1 at the top of the file.
2. Below the harness, add pattern P1 and its test call:

   ```python
   COURSE_CODE = r"[A-Z]{2,4}-?\d{3}"

   check("COURSE_CODE", COURSE_CODE,
         should_match=["CS374", "MATH111", "BIO-101"],
         should_not_match=["cs374", "CS3741"])
   ```
3. Save, then run `python3 patterns.py` from inside `cs374-regex/`.  You should see one line, `PASS COURSE_CODE (3 positive, 2 negative)`; the numbers count the test cases you supplied.
4. Remove the `-?` from `COURSE_CODE`, save, and run again.  You should see `FAIL COURSE_CODE:` followed by one indented line for each string the pattern got wrong, here `SHOULD match but did NOT: 'BIO-101'`.
5. Put the `-?` back and confirm the `PASS` line returns.

That loop (edit, run, read the failure) is the whole workflow for this assignment.  `check()` never tells you a pattern is right in general; it tells you exactly which string it got wrong, and that string is your next clue.  Part 3 replaces the `PASS` line with printed text or an output file, but the loop is the same.

### Suggested Pacing

See the course schedule for the assigned and due dates.  Finish Parts 1 and 2 first; Part 3 builds on both.  A suggested sequence:

| Checkpoint | You should have |
|------------|----------------|
| On assignment | Part 1 complete: the five verbs and the backtracking traces written up |
| Checkpoint 1 | Part 2 complete: the `check()` harness and all ten patterns with test cases |
| Checkpoint 2 | Part 3 transformer producing the sample output |
| Due date | Part 3 log parser complete; deliverables assembled and submitted |

---

## Part 1: The `re` API, and Watching the Engine Backtrack

Python's `re` library adds engineering conveniences to the theory.  Anchors pin a match to a position: `^` is the start of the string and `$` is the end.  Character classes stand for one character from a set: `\d` is a digit, `\w` is a word character, and `\s` is whitespace.  Groups `(...)` capture the text they match so you can read it back later.  Five functions carry almost all the work: `re.search` (first match anywhere), `re.match` (match at the start), `re.findall` (all matches), `re.sub` (substitute), and `re.finditer` (iterate matches with positions).  Raw strings (`r"..."`) keep Python's own backslash handling out of your way.  Use them always.

### Step 1.1: The walkthrough

> **Do this.**
> 1. Create `five_verbs.py` in `cs374-regex` and paste the code below into it.
> 2. Run `python3 five_verbs.py` from that folder.  If Python says `can't open file ... No such file or directory`, your terminal is not in `cs374-regex`; change into it (the shell primer shows `cd`) and run again.

```python
import re

text = "Order #1042 shipped 2026-09-18 to Collegeville, PA 19426; order #1043 pending."

# search: first match, or None
m = re.search(r"#(\d+)", text)
print("first order number:", m.group(1) if m else "none")

# findall: all matches of the capture group
print("all order numbers:", re.findall(r"#(\d+)", text))

# groups: pull apart a date
m = re.search(r"(\d{4})-(\d{2})-(\d{2})", text)
if m:
    year, month, day = m.groups()
    print(f"shipped on day {day} of month {month}, {year}")

# sub: redact zip codes
print(re.sub(r"\b\d{5}\b", "[ZIP]", text))

# finditer: positions, the lexer's best friend
for m in re.finditer(r"order", text, flags=re.IGNORECASE):
    print(f"'order' at characters {m.start()}-{m.end()}")
```

> **You should see.** Six lines.  The fourth is the sentence with the zip code replaced, and the last two give character offsets.

```text
first order number: 1042
all order numbers: ['1042', '1043']
shipped on day 18 of month 09, 2026
Order #1042 shipped 2026-09-18 to Collegeville, PA [ZIP]; order #1043 pending.
'order' at characters 0-5
'order' at characters 58-63
```

> **Now try this.**
> 1. Replace `19426` in the text with `194260` and run the file again.  The `[ZIP]` disappears, because `\b\d{5}\b` no longer finds five digits with a boundary on both sides.
> 2. Put `19426` back and confirm the redaction returns.  That loop (edit, run, read the output) is the entire method for this assignment.

**Reading the code.**

- `re.search` returns a match object or `None`, which is why every use above checks `m` before reading it.  `m.group(1)` is the text captured by the first parenthesized group, `m.group(0)` is the whole match, and `m.groups()` returns all captures at once.
- `re.findall` changes shape with your pattern: no groups gives whole matches, exactly one group gives only that group (so `r"#(\d+)"` yields bare numbers), and two or more groups give tuples.  This trips up everyone once; the next step makes it trip you now, where it costs nothing.
- `\b` is a word boundary, a zero-width assertion that matches a position between characters rather than a character.  Without it, `\d{5}` would match the first five digits of a longer number.  `finditer` yields match objects with `.start()` and `.end()`, so you learn where each match sits, and that is why a lexer is built on `finditer` rather than `findall`.

### Step 1.2: Now you: the `findall` shape experiment

Four nearly identical patterns give four different shapes of answer.  Predict first, then run; that is what makes the shape rule stick.

> **Do this.**
> 1. Create `findall_shapes.py` in the same folder and paste the code below into it.
> 2. Before you run it, write down what you expect each of the four lines to print.
> 3. Run `python3 findall_shapes.py` and compare.
> 4. Complete the `TODO` at the bottom of the file and run it again.

```python
import re

text = "CS374 meets TR, MATH-111 meets MWF, CS173 meets TR"

experiments = [
    (r"[A-Z]+-?\d+",              "no groups"),
    (r"([A-Z]+)-?\d+",            "one group"),
    (r"([A-Z]+)-?(\d+)",          "two groups"),
    (r"(?:[A-Z]+)-?(\d+)",        "one capturing, one non-capturing"),
]

for pattern, label in experiments:
    print(f"  {label:34} findall -> {re.findall(pattern, text)}")

# TODO: rewrite the last experiment with finditer and print, for each match,
#       the full text (m.group(0)), the captured digits, and m.start().
```

> **You should see.** Before the `TODO`, four lines in four shapes: strings, strings, tuples, strings.  After it, three more lines in a layout of your choosing: `CS374` with digits `374` at position 0, `MATH-111` with `111` at 16, and `CS173` with `173` at 36.

```text
  no groups                          findall -> ['CS374', 'MATH-111', 'CS173']
  one group                          findall -> ['CS', 'MATH', 'CS']
  two groups                         findall -> [('CS', '374'), ('MATH', '111'), ('CS', '173')]
  one capturing, one non-capturing   findall -> ['374', '111', '173']
```

### Step 1.3: What to write up

Open `writeups.md` in `cs374-regex` (you created it in Getting Started) and answer these questions in it, using output you produced.  The Reflection Prompts at the end of the assignment go in the same file.

1.  Predict, before running, what the redaction line prints.  What does `\b` contribute, and what over-matches without it?
2.  Design a one-line experiment that distinguishes `re.match` from `re.search`.  Run it, and state the rule in one sentence.
3.  The date pattern accepts `2026-99-99`.  Is that a defect of regular expressions, of this pattern, or of asking syntax to do the job of semantics?  Where in a language pipeline would the 99th month be caught?
4.  State the `findall` shape rule in one sentence you would trust on an exam.
5.  `finditer` reports start and end offsets.  Write two sentences to your future self explaining why a lexer needs exactly this capability and not only `findall`.

Complete the `TODO` in `findall_shapes.py` and include the file.

---

### Watching the engine backtrack

Matching is not a single left-to-right sweep.  Whenever the pattern offers a choice (how many repetitions a star takes, which branch of an alternation to try), the engine makes the greedy choice first and remembers the decision point.  If the rest of the pattern later fails, the engine backtracks: it returns to the most recent decision, takes the next alternative, and pushes forward again.

**Worked example.**  Match `a*ab` against `"aaab"` with `re.fullmatch`.  Read the pattern as "any number of `a`s, then one more `a`, then a `b`."  The greedy `a*` first takes every `a` it can, which is one too many.

| Step | `a*` currently holds | Rest of pattern needs | Rest of input is | Outcome |
|------|----------------------|-----------------------|------------------|---------|
| 1 | `"aaa"` (greedy maximum) | `ab` | `"b"` | `a` vs `b` fails -> **backtrack** |
| 2 | `"aa"` (gave one back) | `ab` | `"ab"` | `ab` = `ab` -> **MATCH** |

Two attempts, one backtrack.  Now trace the same pattern against `"ab"` on paper before you run anything.

### Step 1.4: The walkthrough

This script implements `a*ab` as an explicit search that narrates every decision, then checks each verdict against Python's real engine.

> **Do this.**
> 1. Create `backtrack.py` in `cs374-regex` and paste the code below into it.
> 2. Run `python3 backtrack.py`.

```python
import re

def trace_a_star_ab(s):
    """Match a*ab against ALL of s, narrating each backtracking step."""
    max_a = 0
    while max_a < len(s) and s[max_a] == "a":
        max_a += 1                    # the longest run of a's available to a*
    for k in range(max_a, -1, -1):    # greedy: try the LONGEST take first
        rest = s[k:]
        print(f"  a* holds {'a'*k!r:8} rest of input = {rest!r:8}", end=" ")
        if rest == "ab":
            print("-> literal 'ab' fits: MATCH")
            return True
        print("-> literal 'ab' does not fit: backtrack (give back one 'a')")
    print("  no choices left: overall FAILURE")
    return False

for s in ["aaab", "ab", "b", "aaa"]:
    print(f"Pattern a*ab vs {s!r}:")
    mine = trace_a_star_ab(s)
    real = bool(re.fullmatch(r"a*ab", s))
    print(f"  re.fullmatch agrees: {real == mine} (engine says {'MATCH' if real else 'no match'})\n")
```

> **You should see.** Four blocks, one per input.  Each narrated line is one attempt, and every block ends with `re.fullmatch agrees: True`.

```text
Pattern a*ab vs 'aaab':
  a* holds 'aaa'    rest of input = 'b'      -> literal 'ab' does not fit: backtrack (give back one 'a')
  a* holds 'aa'     rest of input = 'ab'     -> literal 'ab' fits: MATCH
  re.fullmatch agrees: True (engine says MATCH)

Pattern a*ab vs 'ab':
  a* holds 'a'      rest of input = 'b'      -> literal 'ab' does not fit: backtrack (give back one 'a')
  a* holds ''       rest of input = 'ab'     -> literal 'ab' fits: MATCH
  re.fullmatch agrees: True (engine says MATCH)

Pattern a*ab vs 'b':
  a* holds ''       rest of input = 'b'      -> literal 'ab' does not fit: backtrack (give back one 'a')
  no choices left: overall FAILURE
  re.fullmatch agrees: True (engine says no match)

Pattern a*ab vs 'aaa':
  a* holds 'aaa'    rest of input = ''       -> literal 'ab' does not fit: backtrack (give back one 'a')
  a* holds 'aa'     rest of input = 'a'      -> literal 'ab' does not fit: backtrack (give back one 'a')
  a* holds 'a'      rest of input = 'aa'     -> literal 'ab' does not fit: backtrack (give back one 'a')
  a* holds ''       rest of input = 'aaa'    -> literal 'ab' does not fit: backtrack (give back one 'a')
  no choices left: overall FAILURE
  re.fullmatch agrees: True (engine says no match)
```

> **Checkpoint.** Compare the `'ab'` block with your paper trace.  If your trace had `a*` start with `''` instead of `'a'`, you traced a reluctant star, not a greedy one.

**Reading the code.**  `max_a` is the greedy maximum, the most `a*` could possibly take.  The descending loop `range(max_a, -1, -1)` is greed itself: try the longest take first, and give characters back only when forced.  A reluctant `a*?` would count upward from 0, and nothing else would change.  Each iteration revisits one decision point, so the number of iterations before success is the amount of backtracking the engine did, and the last line confirms the narration agrees with `re.fullmatch` on every input.

> **Watch out.** Backtracking is invisible when a match succeeds quickly, but it is still happening.  On pathological patterns, such as nested quantifiers like `(a+)+` against input that almost matches, the number of decision points explodes and matching can take exponential time.  This is called catastrophic backtracking.  Knowing where decisions accumulate is how you avoid writing such patterns.

---

## Part 2: The Harness and the Pattern Library

A test harness is a small function that runs your pattern against strings you already know the answer for and reports every disagreement.  The `check()` harness below is the one you pasted in Your First 30 Minutes.  It uses `fullmatch`, which succeeds only when the pattern matches the entire string.  That is deliberate: a pattern that matches only the front of `42abc` is too permissive, and `fullmatch` exposes it without `^` and `$` written by hand.

### Step 2.1: The walkthrough: one pattern through the harness

> **Do this.**
> 1. Create `patterns.py` in `cs374-regex` and paste the code below into it.
> 2. Run `python3 patterns.py`.
> 3. Break the pattern on purpose: delete the `-?` from `COURSE_CODE` and run again.  Read what the harness says, then put the `-?` back.

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

# P1 COURSE_CODE: 2-4 capital letters, an optional hyphen, then exactly three digits.
# {2,4} bounds the letter run; -? makes the hyphen optional; \d{3} is exactly three digits.
COURSE_CODE = r"[A-Z]{2,4}-?\d{3}"
check("COURSE_CODE", COURSE_CODE,
      should_match=["CS374", "MATH-111", "BIO101"],
      should_not_match=["cs374", "CS37"])
```

> **You should see.** One `PASS` line with the case counts.  With the `-?` removed, the harness prints `FAIL COURSE_CODE:` and names the string that stopped matching, `SHOULD match but did NOT: 'MATH-111'`; restore it and the `PASS` line comes back.  That loop (edit, run, read the failure) is the whole workflow for this part and for the ten patterns in the assignment.

```text
PASS COURSE_CODE (3 positive, 2 negative)
```

### Step 2.2: Write the Ten Required Patterns

> **Do this.** For each of P1 through P10, add this block to `patterns.py` below the harness, in the shape P1 took in Your First 30 Minutes, and run `python3 patterns.py` after each one:
> 1. A comment with one sentence per non-trivial construct in the pattern (a lookahead, a bounded repeat, an alternation).  The rubric asks for this sentence.
> 2. The pattern itself, as a raw string, named exactly as shown in the list.
> 3. A `check()` call with at least three `should_match` and two `should_not_match` strings, starting from the lists below and adding your own.

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

> **You should see.** After the tenth pattern, `python3 patterns.py` prints ten `PASS` lines and no `FAIL` lines.  The counts in parentheses are your own case counts, so yours will differ from these once you add cases.

```text
PASS COURSE_CODE (4 positive, 4 negative)
PASS IDENTIFIER (4 positive, 4 negative)
PASS DECIMAL (5 positive, 5 negative)
PASS TIME_12H (4 positive, 5 negative)
PASS EMAIL (3 positive, 4 negative)
PASS US_PHONE (3 positive, 3 negative)
PASS ISO_DATE (3 positive, 4 negative)
PASS HEX_COLOR (4 positive, 4 negative)
PASS IPV4_ADDRESS (4 positive, 3 negative)
PASS MARKDOWN_LINK (3 positive, 3 negative)
```

> **If it fails.**
> - `Should NOT match but DID`: the pattern is too permissive.  A character class is too broad, a quantifier allows too many repeats, or an optional piece lets a wrong string through.
> - `SHOULD match but did NOT`: the pattern is too strict.  The usual causes are a literal that needs escaping (`.`, `+`, `(`, `)`, `[`) or a piece that should be optional but has no `?`.
> - `re.error` before any `PASS` or `FAIL` line: the pattern itself does not compile.  Look for an unbalanced bracket or parenthesis; the message reports the position.
> - Still stuck on *why*?  Paste the pattern and a failing string into [pythex](https://pythex.org/), which runs Python's own `re` in your browser, or into [regex101](https://regex101.com/) with the Flavor set to Python, whose explanation pane names what every piece of the pattern matches.  The harness stays the test of record; these tools only help you see the mismatch.

> **Watch out.**
> - P6 lists only two positive cases.  The rubric requires at least three, so add your own to every pattern that falls short.
> - I run hidden test cases too.  The rubric names two common misses: permitting leading zeros where the description forbids them, and leaving a pattern unanchored that should be anchored.  Add the negative cases you would use to catch those before I do.
> - `check()` uses `fullmatch`, so a pattern passes here with or without `^` and `$`.  Decide deliberately which approach each pattern takes, because Part 3 reuses P5 and P6 without anchors.

---

## Part 3: Regex-Based Text Transformer and Log Parser

### Step 3.0: Groups and Group References, a Walkthrough

The date step of the transformer asks you to take a date apart and put the pieces back together in a different order.  Two tools do that work.  A *capture group* `(...)` remembers the text it matched.  A *group reference* such as `\1` in the replacement string of `re.sub` puts that remembered text back.  This walkthrough shows both on a date conversion that runs in the opposite direction from the one you will write: it turns ISO `YYYY-MM-DD` into the European `DD.MM.YYYY`.  You see every technique here, and you still decide for yourself how to apply it to `MM/DD/YYYY`.

> **Do this.**
> 1. Create `groups_demo.py` in `cs374-regex` and paste the code below into it.
> 2. Run `python3 groups_demo.py`.  This file is practice, like `five_verbs.py`, and is not a deliverable.

```python
import re

text = "2026-09-18 was the deadline; it moved to 2026-10-02, then to 2026-11-30"

# 1. Numbering: each ( opens a group, counted left to right from 1.  Group 0 is the whole match.
m = re.search(r"(\d{4})-(\d{2})-(\d{2})", text)
print("1. group(0):", m.group(0), "| group(1):", m.group(1), "| group(2):", m.group(2), "| group(3):", m.group(3))
print("   groups():", m.groups(), "| span(2):", m.span(2))

# 2. Alternation inside a group.  Without the parentheses, | splits the WHOLE pattern in two.
print("2. ungrouped:", re.search(r"\d{4}-0[1-9]|1[0-2]-\d{2}", "2026-12-25").group(0))
print("   grouped:  ", re.search(r"\d{4}-(0[1-9]|1[0-2])-\d{2}", "2026-12-25").group(0))
ISO = r"(\d{4})-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01])"
for s in ["2026-09-18", "2026-13-01", "2026-02-31", "2026-00-15"]:
    print(f"   fullmatch {s}: {bool(re.fullmatch(ISO, s))}")

# 3. Non-capturing groups (?:...) group without taking a number.
m = re.search(r"(?:\d{4})-(\d{2})-(\d{2})", text)
print("3. with (?:...) on the year, group(1) is now the month:", m.group(1), "| groups():", m.groups())

# 4. Group references in re.sub: \1, \2, \3 in the replacement mean "the text group n captured".
print("4.", re.sub(ISO, r"\3.\2.\1", text))
print("   not raw: ", repr(re.sub(ISO, "\3.\2.\1", "2026-09-18")))
print("   \\g<n> form:", re.sub(ISO, r"\g<3>.\g<2>.\g<1>", "2026-09-18"))

# 5. Named groups: (?P<name>...) in the pattern, \g<name> in the replacement, m.group("name") in code.
ISO_NAMED = r"(?P<year>\d{4})-(?P<month>0[1-9]|1[0-2])-(?P<day>0[1-9]|[12]\d|3[01])"
print("5.", re.sub(ISO_NAMED, r"\g<day>.\g<month>.\g<year>", text))
m = re.search(ISO_NAMED, text)
print("   m.group('month'):", m.group("month"), "| m.groupdict():", m.groupdict())

# 6. Word boundaries keep the pattern from rewriting part of a longer number.
noisy = "ids 12026-09-18 and 2026-09-180, real date 2026-09-18"
print("6. no \\b:  ", re.sub(ISO, r"\3.\2.\1", noisy))
print("   with \\b:", re.sub(r"\b" + ISO + r"\b", r"\3.\2.\1", noisy))
```

> **You should see.** Sixteen lines, numbered by section.  Section 4 and section 5 print the same sentence, and section 6 shows the boundaries protecting the two longer numbers.

```text
1. group(0): 2026-09-18 | group(1): 2026 | group(2): 09 | group(3): 18
   groups(): ('2026', '09', '18') | span(2): (5, 7)
2. ungrouped: 12-25
   grouped:   2026-12-25
   fullmatch 2026-09-18: True
   fullmatch 2026-13-01: False
   fullmatch 2026-02-31: True
   fullmatch 2026-00-15: False
3. with (?:...) on the year, group(1) is now the month: 09 | groups(): ('09', '18')
4. 18.09.2026 was the deadline; it moved to 02.10.2026, then to 30.11.2026
   not raw:  '\x03.\x02.\x01'
   \g<n> form: 18.09.2026
5. 18.09.2026 was the deadline; it moved to 02.10.2026, then to 30.11.2026
   m.group('month'): 09 | m.groupdict(): {'year': '2026', 'month': '09', 'day': '18'}
6. no \b:   ids 118.09.2026 and 18.09.20260, real date 18.09.2026
   with \b: ids 12026-09-18 and 2026-09-180, real date 18.09.2026
```

**Reading the code.**

- **Section 1, numbering.**  Groups are numbered by the position of their *opening* parenthesis, counting from the left and starting at 1, so the year is group 1, the month group 2, and the day group 3.  Group 0 is always the whole match.  `span(2)` reports where group 2 sits in the string, here characters 5 through 7.
- **Section 2, alternation.**  `|` has the lowest precedence of any operator, so `\d{4}-0[1-9]|1[0-2]-\d{2}` means "`\d{4}-0[1-9]`, *or* `1[0-2]-\d{2}`."  On `2026-12-25` the first branch fails, and the second branch matches only `12-25`, without the year.  Wrapping the alternation in parentheses confines the choice to the month position.  That is how `(0[1-9]|1[0-2])` expresses "01 through 12" and `(0[1-9]|[12]\d|3[01])` expresses "01 through 31," and the same parentheses that confine the choice also capture the result.  Notice that `2026-02-31` still passes: as P7 says, a regex checks the format and ranges, not the calendar.
- **Section 3, non-capturing groups.**  `(?:...)` groups for precedence without capturing, so every group after it moves down one number.  If you add or remove a capturing group, renumber every reference that comes after it.
- **Section 4, group references.**  In the *replacement* string of `re.sub`, `\3` means "whatever group 3 captured in this match."  `re.sub` applies the replacement to every match, so all three dates are rewritten, including the one at the very start of the string and the one at the very end.  The replacement must be a raw string: without the `r`, Python turns `"\3"` into the control character `\x03` before `re` ever sees it, as the `not raw` line shows.  `\g<3>` is the long form of `\3`.  Use it when a literal digit follows the reference, because `\30` would be read as group 30.
- **Section 5, named groups.**  `(?P<year>...)` names a group, `\g<year>` refers to it in a replacement, and `m.group("year")` or `m.groupdict()` reads it in code.  The named form gives the same result as section 4 and cannot get the order wrong by miscounting.  Step 3.2 requires named groups for the log parser.
- **Section 6, boundaries.**  Without `\b`, the pattern happily matches the last ten characters of `12026-09-18` and the first ten of `2026-09-180`, and rewrites those pieces of longer numbers.  `\b` on both ends requires a non-word character (or the edge of the string) just outside the date.

> **Now try this.**
> 1. Change the section 4 replacement to `r"\2/\3/\1"` and predict the output before you run it.
> 2. `re.sub` also accepts a function in place of the replacement string.  It calls the function once per match with the match object and inserts whatever string the function returns.  Predict, then run: `re.sub(ISO_NAMED, lambda m: f"{m.group('day')}.{m.group('month')}.{m.group('year')}", text)`.  When is a function worth the extra typing?  (One answer: when the new text needs arithmetic or a lookup, such as turning `09` into `September`.)

### Step 3.1: Text Transformer

In `transformer.py`, write a `transform(text: str) -> str` function that applies these three substitutions, in this order:

1.  Redact emails: replace every email address with `[EMAIL]` using `re.sub`.  Use P5 from Part 2 without anchoring, because the address sits inside a longer sentence.
2.  Normalize dates: convert `MM/DD/YYYY` dates to ISO `YYYY-MM-DD`.  Capture month, day, and year as groups, then reorder them with group references in the replacement string (e.g., `r"\3-\1-\2"`).
3.  Redact phone numbers: replace US phone numbers (P6 from Part 2) with `[PHONE]`.

> **Building `US_DATE` in three moves.**  Work the date step on its own first, with the self-test below, before you wire it into `transform`.
> 1. **Shape.**  Write the literal layout with three capture groups: two digits, a `/`, two digits, a `/`, four digits.  Run the self-test.  The three valid dates convert, but some of the "left unchanged" cases get rewritten.
> 2. **Ranges.**  Replace the month group and the day group with grouped alternations, as section 2 of Step 3.0 did for ISO dates.  Keep each alternation inside its parentheses, so the group count stays at three.
> 3. **Edges.**  Put `\b` at both ends of the pattern, as section 6 of Step 3.0 did.
>
> Then write `DATE_ISO`.  Number your groups left to right (which one is the month here, which the day, which the year?) and list them in the order ISO wants, separated by `-`.  Keep it a raw string.

Paste this self-test below the skeleton in `transformer.py`.  Every line prints `ok` once `US_DATE` and `DATE_ISO` are right.  The last three cases must come through *unchanged*.

```python
DATE_CASES = [
    ("09/01/2026 opened registration",       "2026-09-01 opened registration"),     # date at the start
    ("registration closed 12/15/2026",        "registration closed 2026-12-15"),     # date at the end
    ("from 01/05/2026 to 05/01/2026",         "from 2026-01-05 to 2026-05-01"),      # two dates in one line
    ("13/01/2026 is not a month",             "13/01/2026 is not a month"),          # month out of range
    ("9/1/2026 has single digits",            "9/1/2026 has single digits"),         # MM/DD/YYYY needs two digits
    ("ticket 109/01/20265 is not a date",     "ticket 109/01/20265 is not a date"),  # digits run past the edges
]

for given, expected in DATE_CASES:
    got = re.sub(US_DATE, DATE_ISO, given)
    print("ok      " if got == expected else "MISMATCH", repr(got))
```

> **Do this.**
> 1. Open `transformer.py` and paste the skeleton below.  The three-line input paragraph you must demonstrate on is already in `SAMPLE`.
> 2. Fill in the three patterns and the three `re.sub` calls at the `# TODO` markers, copying P5 and P6 from `patterns.py` and stripping any anchors, then run `python3 transformer.py`.

```python
import re

EMAIL = r"..."      # TODO: P5 from Part 2, without anchors
US_DATE = r"..."    # TODO: MM/DD/YYYY, with month, day, and year as three capture groups (see Step 3.0)
DATE_ISO = r"..."   # TODO: replacement string that reorders the groups into YYYY-MM-DD
US_PHONE = r"..."   # TODO: P6 from Part 2, without anchors

def transform(text: str) -> str:
    """Redact emails, normalize MM/DD/YYYY dates to ISO, then redact phone numbers."""
    # TODO: three re.sub calls, in the order listed above
    return text

SAMPLE = """Contact MONGAN, WILLIAM at jane.doe@example.com or call (610) 555-0192.
The registration deadline was 09/01/2026.
A second contact: support@ursinus.edu, deadline 12/15/2026."""

if __name__ == "__main__":
    print(transform(SAMPLE))
```

> **You should see.** These three lines.  Everything outside the redacted and converted pieces stays exactly as it was in `SAMPLE`.

```text
Contact MONGAN, WILLIAM at [EMAIL] or call [PHONE].
The registration deadline was 2026-09-01.
A second contact: [EMAIL], deadline 2026-12-15.
```

> **If it fails.**
> - Nothing is replaced: the pattern still carries `^` and `$` (or `\A` and `\Z`) from Part 2, so it can only match a whole string, never a piece of one.
> - The date prints as `01-09-2026` or `09-01-2026`: the group references in the replacement string are in the wrong order.  Count the capture groups left to right.
> - The output contains `\x01`, `\x02`, or odd symbols where the date should be: the replacement string is missing its `r` prefix, so Python turned `\1` into a control character (section 4 of Step 3.0).
> - Only part of a date changes, or the output has empty slots such as `--` where a group should be: an alternation such as `0[1-9]|1[0-2]` is not wrapped in parentheses, so `|` split the whole pattern (section 2 of Step 3.0).
> - `re.error: invalid group reference`: the replacement names a group number the pattern does not have.  Count the capturing parentheses again, and remember that `(?:...)` does not count.
> - `13/01/2026` or `109/01/20265` gets rewritten: the month range or the `\b` boundaries are missing (moves 2 and 3 above).
> - The phone number survives: the parentheses in the pattern are not escaped, so `(` opens a group instead of matching a literal `(`.

### Step 3.2: Log Parser

In `log_parser.py`, write a `parse_log(log_path: str, config_path: str)` function for the provided server log, [server.log]({{ site.baseurl }}/files/starters/regex/server.log).  Each line looks like `2026-09-18 08:10:22 WARN disk usage 91% on /dev/sda1`.  The function must:

1.  Use one `re.finditer` pattern with named groups to extract `date`, `time`, `level`, and `message` from each log line.
2.  Report counts by level (how many INFO, WARN, and ERROR lines).
3.  Report the earliest and latest timestamps, as strings in `YYYY-MM-DD HH:MM:SS` format.
4.  Extract every percentage value (`\d+%`) mentioned in WARN lines and report the maximum.
5.  Write all ERROR lines, each prefixed with its original line number, to `errors.txt`.

The named-group pattern must match the line format `YYYY-MM-DD HH:MM:SS LEVEL message text here` exactly.  Store both the input log path and the output `errors.txt` path in a JSON configuration file rather than in the code.  A JSON file holds data as nested names and values, and Python's `json.load` reads it into a dictionary.

> **Do this.** Paste the two-key object below into `config.json`, and save the provided server log, [server.log]({{ site.baseurl }}/files/starters/regex/server.log), in `cs374-regex/` under the name it points to, `server.log`.  Then paste the skeleton into `log_parser.py`, fill in the pattern and the `# TODO` markers, and run `python3 log_parser.py`.

```json
{
  "log_path": "server.log",
  "errors_path": "errors.txt"
}
```

```python
import json
import re

LINE = re.compile(r"...")   # TODO: named groups date, time, level, message

def parse_log(log_path: str, config_path: str) -> None:
    """Parse the log at log_path.  Read the errors.txt path from the JSON at config_path."""
    with open(config_path) as f:
        config = json.load(f)
    # TODO: read the log, run LINE.finditer over it, and collect from the named groups:
    #   counts by level, the earliest and latest timestamps, the maximum WARN percentage
    # TODO: write every ERROR line, prefixed with its line number, to config["errors_path"]
    # TODO: print the five report lines shown below

if __name__ == "__main__":
    with open("config.json") as f:
        cfg = json.load(f)
    parse_log(cfg["log_path"], "config.json")
```

> **You should see.** Five report lines in this shape, and a new `errors.txt` in `cs374-regex/`.  The numbers come from the provided log, so match the shape, not these exact values.  Open `errors.txt` and confirm each line begins with its line number from the original log.

```text
Counts: INFO=42, WARN=8, ERROR=3
Earliest: 2026-09-01 00:01:14
Latest:   2026-09-18 23:59:59
Max WARN percentage: 91%
ERROR lines written to errors.txt
```

> **If it fails.**
> - `FileNotFoundError: server.log`: the log is not in `cs374-regex/`, or you ran the command from a different folder.
> - Every count is zero: the pattern matches nothing.  If you anchored it with `^` and `$` and run `finditer` over the whole file, add the `re.MULTILINE` flag so the anchors match at each line, not only at the ends of the file.
> - `KeyError: 'date'`: a named group is misspelled, or the pattern uses a plain group `(...)` where a named group `(?P<date>...)` is required.

> **Watch out.** The rubric's proficient descriptor asks for more than the five items above: malformed lines (any line that does not fit the format) must be detected and reported with their line number rather than silently dropped, the configuration must live in `config.json`, and `errors.txt` must be generated by the program, not written by hand.  `enumerate(lines, start=1)` is the simplest way to keep a line number next to each line.

---

## Deliverables

Submit one repository or archive containing the following.

- `writeups.md`, carrying your answers to the "What to write up" prompts in Part 1.
- `patterns.py`, the `check()` harness and all ten patterns with their positive and negative cases.
- `transformer.py` and `log_parser.py`, with the JSON configuration file the log parser reads and the `errors.txt` it produces.
- `readme.md`, naming your partner if you paired on Parts 1 and 2, and listing anything you could not finish.

Every pattern is a raw string.  Every file runs as submitted; a file that raises on import earns the preemerging row for whatever it was meant to demonstrate.

---

## Self-Check Before You Submit

Work down this list with the files open, because each row is something I check first.

- Every code file runs from a clean shell without editing a path.
- Every pattern is a raw string, and each non-trivial construct carries a one-sentence explanation.
- Every pattern has at least three positive and two negative cases, and the negative cases genuinely fail.
- The log parser names the line number of every malformed line, and its configuration lives in JSON rather than in the code.

---

## Reflection Prompts

Answer these in `writeups.md`, in a paragraph each.

- Which of the five `re` verbs did you reach for most, and which one did you misuse at least once before the output corrected you?
- Name the moment in Part 1 where the engine did more work than you expected.  What property of the pattern caused it, and how would you recognize that property in a pattern someone else wrote?
