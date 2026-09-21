---
layout: assignment
permalink: /Assignments/Regex
title: "CS374: Principles of Programming Languages - Regular Expressions"

info:
  coursenum: CS374
  purpose: "To build a working command of regular expressions, starting from Python's re library and the backtracking the engine does when a quantifier has a choice, and ending with a tested pattern library, a finditer mini lexer, a realistic log parser, and the vocabulary to explain why a pattern behaves the way it does."
  tilt:
    task: "Work through five parts: the re API and backtracking, a tested ten-pattern library built on the check() harness, a re.finditer mini lexer with an ordered TOKEN_SPEC and gap detection, a text transformer and log parser, and a written analysis of what regular expressions cannot do."
    criteria: "I grade this on the correctness of your patterns, mini lexer, transformer, and log parser, and on the depth of your greedy/lazy, anchors, and Chomsky-limits analysis.  The rubric below spells out each row."
  points: 100
  goals:
    - To use Python's re API deliberately, knowing what search, match, findall, sub, and finditer each return, and to explain backtracking as a search over decision points
    - To write and test a library of regular expressions for real-world data patterns against positive and negative cases
    - To build a mini lexer using re.finditer with a single compiled alternation, named groups, ordered rules, and gap detection
    - To apply regular expressions to realistic log-parsing and data-extraction tasks
    - To explain the theoretical limits of regular languages and connect them to the Chomsky hierarchy
  rubric:
    - weight: 15
      description: "The re API and Backtracking (Goal 1)"
      preemerging: The cells were not run, or the written answers restate the documentation without evidence from output
      beginning: The cells were run but the findall shape experiment is unanswered, or the answers do not distinguish group(0) from group(1)
      progressing: The questions are answered from real output and the traces are correct, but the finditer rewrite does not report positions, or the attempt counts are not compared across inputs
      proficient: Every question is answered from output you produced, the findall shape rule is stated in one sentence you would trust on an exam, the finditer rewrite prints full text, capture, and start position for each match, and the input that forced the most backtracking is identified with the property that caused it
    - weight: 25
      description: "Pattern Library and the check() Harness (Goal 2)"
      preemerging: The harness does not run, or fewer than five patterns are provided
      beginning: The harness runs but several patterns fail on edge cases, such as missing anchors that allow partial matches, or character classes that are too broad or too narrow
      progressing: All ten patterns pass the provided positive and negative test cases, but two or more would fail on hidden inputs, for example by permitting leading zeros in an integer or by leaving a pattern unanchored that should be anchored
      proficient: All ten patterns pass all provided and hidden test cases; every pattern is a raw string; each is named, carries a one-sentence explanation of each non-trivial construct, and is tested with at least three positive and two negative cases through the check() harness
    - weight: 25
      description: "Mini Lexer with re.finditer (Goal 3)"
      preemerging: The mini lexer is not implemented, or it uses re.match in a loop rather than re.finditer with alternation
      beginning: The mini lexer uses finditer, but the TOKEN_SPEC ordering is wrong, for example with keywords listed after identifiers, so some inputs get incorrect token types
      progressing: The mini lexer produces correct token types for most inputs, but one or more token types are misclassified, or gaps between matches are not detected
      proficient: The mini lexer uses a single compiled alternation pattern with named groups; produces the correct token type and value for every input; detects and reports gaps with their position; and handles maximal-munch ordering correctly for all test cases
    - weight: 20
      description: "Text Transformer and Log Parser (Goals 2, 4)"
      preemerging: Neither the transformer nor the log parser is implemented, or both produce clearly wrong output
      beginning: One of the two is implemented but produces incorrect output on several provided inputs, for example a date conversion using the wrong group references, or a log parser that drops records
      progressing: Both are implemented and produce correct output on the provided inputs, but the log parser does not handle malformed lines, or the transformer fails on edge cases such as dates at the start or end of a string
      proficient: Both work correctly on all provided and hidden inputs; malformed log lines are detected and reported with their line number; the configuration lives in a JSON file; and the errors.txt output is generated correctly
    - weight: 15
      description: "Pattern Analysis and Limits Discussion (Goals 1, 5)"
      preemerging: No analysis is provided, or the analysis restates the course notes without applying the concepts to your own patterns
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

In this assignment you learn Python's regular-expression library by running it, then use it to build a tested pattern library, a small lexer, a text transformer, and a log parser.  A regular expression (regex) is a pattern that describes a set of strings, and Python's `re` module matches text against such patterns.  Parts 1 through 3 build the two artifacts everything downstream grows from, the `check()` harness and the `re.finditer` mini lexer, and the Lexer assignment later turns that lexer into a permanent pipeline component.

Work the parts in order, because I test each one on its own and each part uses what the one before it built.  Part 1 is a walkthrough: I show you something, you run it, then you vary it and write down what happened.  Every code block here runs as it stands, so put it in a file, run it, change something, and run it again.  Reading these blocks without running them is the one way to get nothing out of this assignment.  Write every pattern as a raw string (`r"..."`) so that backslashes reach the regex engine unchanged.  Part 5 is a written analysis, and it ends with a question about what regular expressions cannot do; answer it in your writeup.

**Pair policy.**  Parts 1 through 3 may be done in pairs, with driver and navigator at one screen and a swap at the start of Part 2.  If you pair, you each submit the same files for those parts and name the other in your readme.  Parts 4 and 5 are individual work.

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

> **Do this.** Make a project folder, move into it, and create the six files below: `patterns.py` (Part 2), `mini_lexer.py` (Part 3), `transformer.py` (Part 4), `log_parser.py` and `config.json` (Part 3c), and `readme.md` (Part 4).  Every command on this page runs from inside this folder.  `touch` works in the macOS and Linux shells and in Git Bash on Windows; you can also save each new empty file from your editor into `cs374-regex/`.
>
> ```bash
> mkdir cs374-regex
> cd cs374-regex
> touch patterns.py mini_lexer.py transformer.py log_parser.py config.json readme.md
> ```

> **Time budget.** Parts 1 through 3 are the build, and they are sized alike.  Part 4 is about the same again, and Part 5 is writing rather than code.  Spread them across the assignment window using the pacing table below.

### Your First 30 Minutes

Get one pattern passing, then break it on purpose, so you know what both outcomes look like.

1. Open `patterns.py` and paste the `check()` harness from Step 1a at the top of the file.
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

That loop (edit, run, read the failure) is the whole workflow for this assignment.  `check()` never tells you a pattern is right in general; it tells you exactly which string it got wrong, and that string is your next clue.  Parts 2 and 3 replace the `PASS` line with a printed token list or an output file, but the loop is the same.

### Suggested Pacing

See the course schedule for the assigned and due dates.  A suggested sequence:

| Checkpoint | You should have |
|------------|----------------|
| On assignment | Part 1 complete: the five verbs and the backtracking traces written up |
| Checkpoint 1 | Part 2 complete: the `check()` harness and all ten patterns with test cases |
| Checkpoint 2 | Part 3 complete: the mini lexer passing the ordering table and reporting gaps |
| Checkpoint 3 | Part 4 complete: transformer and log parser producing the sample output |
| Due date | Part 5 analysis written; deliverables assembled and submitted |

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
> 2. Put `19426` back and confirm the redaction returns.  That loop (edit, run, read the output) is the entire method for Parts 1 through 3.

**Reading the code.**

- `re.search` returns a match object or `None`, which is why every use above checks `m` before reading it.  `m.group(1)` is the text captured by the first parenthesized group, `m.group(0)` is the whole match, and `m.groups()` returns all captures at once.
- `re.findall` changes shape with your pattern: no groups gives whole matches, exactly one group gives only that group (so `r"#(\d+)"` yields bare numbers), and two or more groups give tuples.  This trips up everyone once; the next step makes it trip you now, where it costs nothing.
- `\b` is a word boundary, a zero-width assertion that matches a position between characters rather than a character.  Without it, `\d{5}` would match the first five digits of a longer number.  `finditer` yields match objects with `.start()` and `.end()`, so you learn where each match sits, and that is why Part 4 is built on `finditer` rather than `findall`.

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

Create `part1.md` in `cs374-regex` and answer these questions in it, using output you produced:

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

> **Checkpoint.** Compare the `'ab'` block with your paper trace.  If your trace had `a*` start with `''` instead of `'a'`, you traced a reluctant star, not a greedy one.  Step 1.5 lets you run that version too.

**Reading the code.**  `max_a` is the greedy maximum, the most `a*` could possibly take.  The descending loop `range(max_a, -1, -1)` is greed itself: try the longest take first, and give characters back only when forced.  A reluctant `a*?` would count upward from 0, and nothing else would change.  Each iteration revisits one decision point, so the number of iterations before success is the amount of backtracking the engine did, and the last line confirms the narration agrees with `re.fullmatch` on every input.

> **Watch out.** Backtracking is invisible when a match succeeds quickly, but it is still happening.  On pathological patterns, such as nested quantifiers like `(a+)+` against input that almost matches, the number of decision points explodes and matching can take exponential time.  This is called catastrophic backtracking.  Knowing where decisions accumulate is how you avoid writing such patterns.

### Step 1.5: Now you: vary the search

Two small edits to `backtrack.py` produce the evidence Questions 7 and 8 ask for.

> **Do this.**
> 1. Below the existing loop, add a second loop over the same four inputs that prints `bool(re.fullmatch(r"a*ab", s))` next to `bool(re.fullmatch(r"a+b", s))`.
> 2. Run again and confirm the two columns agree on every input.
> 3. Flip the greed: change `range(max_a, -1, -1)` to `range(0, max_a + 1)`, run once more, and count the attempts for `"aaab"` and `"ab"`.  This is the reluctant `a*?`.
> 4. Change the range back before you submit, so the file you hand in traces the greedy engine.

> **You should see.** From step 2, four lines where both patterns agree: match, match, no match, no match.  From step 3, the `'aaab'` block takes three attempts (holding `''`, then `'a'`, then `'aa'`) and the `'ab'` block takes one, the mirror image of the greedy counts.

### Step 1.6: What to write up

Create `part2.md` and answer these in it:

6.  In the trace for `"aaab"`, how many characters does `a*` hold on its first attempt, and why that many?  State the general rule the engine follows when a greedy quantifier has a choice.
7.  Count the attempts for `"aaab"`, `"ab"`, and `"aaa"` from your output.  Which input forced the most work, and what property of that input caused it?
8.  `a*ab` describes exactly the same set of strings as `a+b`.  Verify this with `re.fullmatch` on all four test inputs rather than taking my word for it.  Then explain why the second pattern never needs to backtrack on these inputs.
9.  A pattern like `(a+)+b` against a long string of `a`s with no `b` can take exponential time.  Using the decision-point idea from the trace, explain in two or three sentences where all those decisions come from.
{: start="6"}

---

## Part 2: The Harness and the Pattern Library

A test harness is a small function that runs your pattern against strings you already know the answer for and reports every disagreement.  The `check()` harness below is the one from the Regex assignment's Part 1, copied verbatim, so that assignment starts from a running state.  It uses `fullmatch`, which succeeds only when the pattern matches the entire string.  That is deliberate: a pattern that matches only the front of `42abc` is too permissive, and `fullmatch` exposes it without `^` and `$` written by hand.

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

> **Watch out.**
> - P6 lists only two positive cases.  The rubric requires at least three, so add your own to every pattern that falls short.
> - I run hidden test cases too.  The rubric names two common misses: permitting leading zeros where the description forbids them, and leaving a pattern unanchored that should be anchored.  Add the negative cases you would use to catch those before I do.
> - `check()` uses `fullmatch`, so a pattern passes here with or without `^` and `$`.  Decide deliberately which approach each pattern takes.  Q2 in Part 5 asks which anchor approach you used in each pattern and why, and Part 3 reuses P5 and P6 without anchors.

---

## Part 3: Mini Lexer Using re.finditer

A lexer does not run one pattern at a time over the source.  It joins every token pattern into a single master alternation, gives each alternative a named group, and lets `finditer` sweep the input once.  After each match, `m.lastgroup` names the alternative that fired, which is the token type, and `m.start()` says where it was, which is what an error message needs.

Two rules govern that master pattern, and both bite:

- Order matters.  Alternation takes the first alternative that matches at a position, not the longest.  If `IDENT` comes before `LET`, then `let` lexes as an identifier and your keyword never fires.
- Gaps are not free.  `finditer` silently skips any character no alternative claims, and a lexer that does the same hands the parser a token stream that quietly omits the typo.  Track the end of the previous match, and report anything between it and the start of the next one.

### Step 3.1: The walkthrough: watch `finditer` sweep

This probe builds the master pattern from an ordered `TOKEN_SPEC` and prints every match, whitespace included, so you can see the gap with your own eyes.

> **Do this.**
> 1. Create `mini_lexer.py` in `cs374-regex` and paste the code below into it.
> 2. Replace the two `TODO` patterns with your `IDENTIFIER` and `INTEGER` patterns from Part 2.  Paste the pattern text itself; do not import `patterns.py`, or its `check()` calls will run every time the lexer starts.
> 3. Run `python3 mini_lexer.py`.

```python
import re

# Ordered: the engine tries these left to right at each position.
TOKEN_SPEC = [
    ("WHITESPACE", r"[ \t\n]+"),
    ("LET",        r"let"),      # the keyword, listed before IDENT on purpose
    ("IDENT",      r"TODO"),     # TODO: paste your Part 2 IDENTIFIER pattern
    ("NUMBER",     r"TODO"),     # TODO: paste your Part 2 INTEGER pattern
]

# One compiled alternation: (?P<WHITESPACE>...)|(?P<LET>...)|(?P<IDENT>...)|(?P<NUMBER>...)
MASTER = re.compile("|".join(f"(?P<{name}>{pat})" for name, pat in TOKEN_SPEC))
print("master pattern:", MASTER.pattern)

source = "let x = 42"
for m in MASTER.finditer(source):
    print(f"  {m.lastgroup:10} {m.group()!r:6} at {m.start()}-{m.end()}")
```

> **You should see.** The joined pattern (showing your own `IDENT` and `NUMBER` text), then six match lines.  Read the offsets: 5-6 is a space, 7-8 is a space, and nothing claims 6-7.  That is the `=`, and `finditer` dropped it without a word.

```text
  LET        'let'  at 0-3
  WHITESPACE ' '    at 3-4
  IDENT      'x'    at 4-5
  WHITESPACE ' '    at 5-6
  WHITESPACE ' '    at 7-8
  NUMBER     '42'   at 8-10
```

> **If it fails.**
> - `IDENT 'let' at 0-3` with no `LET` line: `IDENT` is ordered before `LET` in `TOKEN_SPEC`.
> - `re.error: redefinition of group name`: two rules share a name.  Every name in `TOKEN_SPEC` must be unique.

### Step 3.2: Implement mini_lex()

`mini_lex()` walks the matches in order and checks that each match starts where the previous one ended.  Any gap means a character matched no rule, and the function raises `LexError` at that position.

> **Do this.**
> 1. Open `mini_lexer.py` and paste the `TOKEN_SPEC` and `MASTER` code from Step 3.1 at the top, then the code below (the `LexError` class, `mini_lex()`, and a main block that lexes one sample line).
> 2. Run `python3 mini_lexer.py`.

```python
class LexError(Exception):
    """Raised when a character matches no rule in TOKEN_SPEC."""
    pass

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

if __name__ == "__main__":
    print(mini_lex("if x = 3.14;"))
```

> **You should see.** Five tuples, one per token.  Whitespace is consumed but not listed.  The third value in each tuple is the index in the source string where that token starts.

```text
[('IF', 'if', 0), ('IDENT', 'x', 3), ('EQ', '=', 5), ('FLOAT', '3.14', 7), ('SEMICOLON', ';', 11)]
```

### Step 3.3: Extend the Token Spec

Extend `TOKEN_SPEC` to cover the language in the table below.  Use at least 15 token types, include every keyword, operator, and literal listed, and put the negative lookahead `(?!\w)` on every keyword so that `iffy` does not tokenize as `IF`.  The Lexer assignment tokenizes this same language with a reusable component, so this work carries forward directly; the table has everything you need.

| Category | Tokens |
|----------|--------|
| Keywords | `if`, `else`, `while`, `let`, `print`, `true`, `false`, `and`, `or`, `not`, `fun` |
| Literals | `INT` (`42`), `FLOAT` (`3.14`), `STRING` (`"hello"`), `IDENT` (`my_var`) |
| Two-char operators | `<=`, `>=`, `==`, `!=`, `->` |
| One-char operators | `=`, `<`, `>`, `+`, `-`, `*`, `/`, `!` |
| Punctuation | `(`, `)`, `{`, `}`, `;`, `:`, `,` |
| Skipped | whitespace, `# comment to end of line` |

> **Do this.**
> 1. Replace `TOKEN_SPEC` in `mini_lexer.py` with the skeleton below and fill in each `# TODO`.  Name each keyword's token type in capitals (`LET`, `WHILE`, and so on); the ordering table in Step 2c expects `LET`.  Place each two-character operator above its one-character prefix, for the same reason `FLOAT` sits above `INT`.
> 2. "Skipped" means `mini_lex()` consumes the match but does not add a tuple, exactly as it does for `WHITESPACE`.  Extend the `if kind != "WHITESPACE"` test so it skips comments too.
> 3. Run `python3 mini_lexer.py` after each group of entries, not after all of them.
>
> ```python
> TOKEN_SPEC = [
>     ("WHITESPACE",  r"[ \t\n]+"),
>     ("COMMENT",     r"..."),            # TODO: a '#' and everything to the end of the line
>     ("FLOAT",       r"\d+\.\d+"),
>     ("INT",         r"\d+"),
>     ("STRING",      r"..."),            # TODO: double-quoted text
>     # TODO: one entry per keyword, each ending in (?!\w), all placed before IDENT
>     ("IF",          r"if(?!\w)"),
>     ("IDENT",       r"[a-zA-Z_]\w*"),
>     # TODO: two-character operators
>     # TODO: one-character operators
>     # TODO: punctuation
> ]
> ```

> **If it fails.**
> - `re.error: redefinition of group name`: two entries in `TOKEN_SPEC` share a name.  Every name must be unique because each becomes a named group.
> - `let` still comes back as `IDENT`, or `<=` comes back as `LT` then `EQ`: the keyword or two-character entry sits below the rule that beat it, or the keyword lacks its `(?!\w)` lookahead.

### Step 3.4: Verify Ordering and Maximal Munch

Run `mini_lex` on each input below and confirm that the output matches the expected token types.  If `iffy` comes back as `IF`, the keyword is missing its `(?!\w)` lookahead; if `3.14` comes back as `INT`, `FLOAT` sits below `INT`; if `@` prints a token instead of `LexError`, one of your patterns is too broad (an unescaped `.` is the usual cause).

| Input | Expected |
|-------|----------|
| `if` | `[("IF", "if", 0)]` |
| `iffy` | `[("IDENT", "iffy", 0)]` |
| `3.14` | `[("FLOAT", "3.14", 0)]` |
| `3` | `[("INT", "3", 0)]` |
| `let x = 1;` | `LET IDENT EQ INT SEMICOLON` |
| `@` | `LexError at position 0` |

> **Do this.**
> 1. Replace the main block at the bottom of `mini_lexer.py` with the loop below, and keep it there: its output is part of `test_output.txt` in the Deliverables.  It runs all six inputs and catches the `LexError` so the last input does not end the program.
> 2. Run `python3 mini_lexer.py` and compare each line to the table.
>
> ```python
> if __name__ == "__main__":
>     for src in ["if", "iffy", "3.14", "3", "let x = 1;", "@"]:
>         try:
>             print(f"{src!r:14} -> {mini_lex(src)}")
>         except LexError as e:
>             print(f"{src!r:14} -> LexError: {e}")
> ```

> **You should see.** Six lines, one per input, matching the table row for row.

```text
'if'           -> [('IF', 'if', 0)]
'iffy'         -> [('IDENT', 'iffy', 0)]
'3.14'         -> [('FLOAT', '3.14', 0)]
'3'            -> [('INT', '3', 0)]
'let x = 1;'   -> [('LET', 'let', 0), ('IDENT', 'x', 4), ('EQ', '=', 6), ('INT', '1', 8), ('SEMICOLON', ';', 9)]
'@'            -> LexError: Unrecognized character '@' at position 0
```

---

## Part 4: Regex-Based Text Transformer and Log Parser

### Step 4.1: Text Transformer

In `transformer.py`, write a `transform(text: str) -> str` function that applies these three substitutions, in this order:

1.  Redact emails: replace every email address with `[EMAIL]` using `re.sub`.  Use P5 from Part 2 without anchoring, because the address sits inside a longer sentence.
2.  Normalize dates: convert `MM/DD/YYYY` dates to ISO `YYYY-MM-DD`.  Capture month, day, and year as groups, then reorder them with group references in the replacement string (e.g., `r"\3-\1-\2"`).
3.  Redact phone numbers: replace US phone numbers (P6 from Part 2) with `[PHONE]`.

> **Do this.**
> 1. Open `transformer.py` and paste the skeleton below.  The three-line input paragraph you must demonstrate on is already in `SAMPLE`.
> 2. Fill in the three patterns and the three `re.sub` calls at the `# TODO` markers, copying P5 and P6 from `patterns.py` and stripping any anchors, then run `python3 transformer.py`.

```python
import re

EMAIL = r"..."      # TODO: P5 from Part 2, without anchors
US_DATE = r"..."    # TODO: MM/DD/YYYY, with month, day, and year as three capture groups
US_PHONE = r"..."   # TODO: P6 from Part 2, without anchors

def transform(text: str) -> str:
    """Redact emails, normalize MM/DD/YYYY dates to ISO, then redact phone numbers."""
    # TODO: three re.sub calls, in the order listed above
    return text

SAMPLE = """Contact MONGAN, WILLIAM at billmongan@gmail.com or call (610) 555-0192.
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
> - The phone number survives: the parentheses in the pattern are not escaped, so `(` opens a group instead of matching a literal `(`.

### Step 4.2: Greedy vs. Lazy Demonstration

A greedy quantifier (`*`) matches as much text as it can.  A lazy quantifier (`*?`) matches as little as it can.  Show one input string and two patterns where the two produce different captures.

> **Do this.**
> 1. Add the code below to `transformer.py`, inside the main block after the `transform(SAMPLE)` call, so one run prints both demonstrations.
> 2. In a comment next to the two `re.search` lines, explain in one sentence why greedy captured more, then run `python3 transformer.py` again.

```python
import re
text = '<b>bold</b> and <i>italic</i>'
greedy = re.search(r'<.*>',  text)   # greedy
lazy   = re.search(r'<.*?>', text)   # lazy
print(f"Greedy: {greedy.group()!r}")
print(f"Lazy:   {lazy.group()!r}")
```

> **You should see.** Two lines after the transformer output.  The greedy pattern runs to the last `>` in the string; the lazy one stops at the first.  You use this exact example again in Q1 of Part 4, so keep the input string and both patterns unchanged.

```text
Greedy: '<b>bold</b> and <i>italic</i>'
Lazy:   '<b>'
```

### Step 4.3: Log Parser

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

> **Watch out.** The rubric's top row asks for more than the five items above: malformed lines (any line that does not fit the format) must be detected and reported with their line number rather than silently dropped, the configuration must live in `config.json`, and `errors.txt` must be generated by the program, not written by hand.  `enumerate(lines, start=1)` is the simplest way to keep a line number next to each line.

---

## Part 5: Pattern Analysis

Answer the four questions below in `readme.md` under headings `Q1` through `Q4`.  Each answer must be at least one paragraph and must quote a pattern, an input, or an output from your own files; restating the course notes without your own example earns the lowest rubric row.  End the file with the Python version you used (`python3 --version`), so that I can reproduce your results.

### Q1: Greedy vs. Lazy

Explain the difference between greedy (`*`, `+`) and lazy (`*?`, `+?`) quantifiers, using the specific example from Step 3b.  Then state when you would prefer lazy over greedy in production code.

### Q2: Anchors

An anchor is a pattern element that matches a position rather than a character.  Explain the difference between `^`, `$`, `\A`, and `\Z`.  Show a pattern from your Part 2 library where removing the anchors (or switching from `fullmatch` to `search`) would cause a false positive.  State which anchor approach you used in each Part 1 pattern and why.

### Q3: Named Groups

Explain the difference between plain groups `(...)`, non-capturing groups `(?:...)`, and named groups `(?P<name>...)`.  Show how `groupdict()` differs from `groups()` using your log parser pattern from Step 3c.

### Q4: The Limits of Regular Expressions

In one paragraph, explain why no regular expression can validate balanced nested parentheses in general.  Your explanation must:
- Reference the pumping lemma for regular languages (by name; you do not need to reproduce the full proof) (taught in the Regular Expressions class session with a worked example; see Allison Ch. 4).
- Name the level of the Chomsky hierarchy that handles context-free languages.
- Name the component of your language pipeline (from the Lexer, Parser, and Interpreter assignments) whose job it is to handle balanced nesting.

---

---

## Deliverables

Submit one repository or archive containing the following.

- `writeups.md`, carrying your answers to the "What to write up" prompts in Part 1, and your Part 5 analysis.
- `patterns.py`, the `check()` harness and all ten patterns with their positive and negative cases.
- `mini_lex.py`, the `re.finditer` lexer with its ordered `TOKEN_SPEC` and gap detection.
- `transform.py` and `logparse.py`, with the JSON configuration file the log parser reads and the `errors.txt` it produces.
- `readme.md`, naming your partner if you paired on Parts 1 through 3, and listing anything you could not finish.

Every pattern is a raw string.  Every file runs as submitted; a file that raises on import earns the preemerging row for whatever it was meant to demonstrate.

---

## Self-Check Before You Submit

Work down this list with the files open, because each row is something I check first.

- Every code file runs from a clean shell without editing a path.
- Every pattern is a raw string, and each non-trivial construct carries a one-sentence explanation.
- Every pattern has at least three positive and two negative cases, and the negative cases genuinely fail.
- The mini lexer reports gaps with their position rather than skipping them silently.
- The log parser names the line number of every malformed line, and its configuration lives in JSON rather than in the code.
- Part 5 answers the Chomsky question by naming the level and the pipeline component, not just by saying that regexes cannot count.

---

## Reflection Prompts

Answer these in `writeups.md`, in a paragraph each.

- Which of the five `re` verbs did you reach for most, and which one did you misuse at least once before the output corrected you?
- Name the moment in Part 1 where the engine did more work than you expected.  What property of the pattern caused it, and how would you recognize that property in a pattern someone else wrote?
- Your mini lexer orders its token rules deliberately.  Describe what breaks if that order is wrong, using a concrete input from your own test set.
- Part 5 asks what regular expressions cannot do.  Having built one lexer with them, where would you refuse to use a regex in the interpreter you are going to write this term?
