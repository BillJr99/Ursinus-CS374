---
layout: assignment
permalink: /Assignments/RegexWorkshop
title: "CS374: Principles of Programming Languages - Lab: Regex Workshop"

info:
  coursenum: CS374
  purpose: "To move from regular expressions as theory to regular expressions as a working tool: Python's re library in five verbs, the backtracking the engine does when a quantifier has a choice, a repeatable test harness, and the one-pattern scanner that the Regex and Lexer assignments both grow from."
  tilt:
    task: "Work the four walkthroughs below by running and varying every cell, then build the check() harness with three tested patterns and the re.finditer mini lexer with an ordered TOKEN_SPEC and gap detection."
    criteria: "I grade this on your worked answers to the two walkthrough sections, a running harness with three fully tested patterns, and a mini lexer that tokenizes the worked example correctly and reports gaps, weighted 25/20/30/25 across the four parts.  The rubric below breaks it down in full."
  points: 15
  goals:
    - To use Python's re API deliberately, knowing what search, match, findall, sub, and finditer each return and why the shape of findall depends on your groups
    - To explain backtracking as a search over decision points, and to recognize the patterns where those decisions explode
    - To set up a repeatable test harness for regular expression patterns and write anchored, character-class, and quantified patterns against positive and negative cases
    - To build a re.finditer mini lexer with a single compiled alternation, named groups, ordered rules, and gap detection
  rubric:
    - weight: 25
      description: "The Five Verbs (Goal 1)"
      preemerging: The cells were not run, or the written answers restate the documentation without evidence from output
      beginning: The cells were run but the findall shape experiment is unanswered, or the answers do not distinguish group(0) from group(1)
      progressing: All questions are answered from real output, but the finditer rewrite is missing or does not report positions
      proficient: Every question is answered from output you produced, the findall shape rule is stated in one sentence you would trust on an exam, and the finditer rewrite prints full text, capture, and start position for each match
    - weight: 20
      description: "Backtracking (Goal 2)"
      preemerging: No trace is produced, or the trace does not correspond to the pattern
      beginning: The trace for one input is correct but the attempt counts are not compared across inputs
      progressing: All traces are correct and compared, but the explanation of catastrophic backtracking does not identify where the decisions come from
      proficient: Traces are correct for every input, the input that forced the most work is identified with the property that caused it, the equivalence of a*ab and a+b is verified rather than asserted, and the exponential case is explained in terms of accumulated decision points
    - weight: 30
      description: "Harness and Pattern Starters (Goal 3)"
      preemerging: The harness does not run, or no pattern passes its test cases
      beginning: The harness runs but only one pattern passes, or patterns lack negative test cases
      progressing: All three patterns pass but a case is mislabeled (e.g., a negative case that actually matches), or raw strings are not used
      proficient: The check() harness runs cleanly; all three patterns pass at least three positive and two negative cases each, use raw strings, and carry a one-sentence explanation of each non-trivial construct
    - weight: 25
      description: "Mini-Lexer Skeleton (Goal 4)"
      preemerging: The skeleton is missing or uses re.match in a loop rather than re.finditer with alternation
      beginning: finditer is used but the TOKEN_SPEC ordering is wrong (keywords not before identifiers), misclassifying the worked example
      progressing: The worked example tokenizes correctly but gaps (unrecognized characters) pass silently
      proficient: A single compiled alternation with named groups tokenizes the worked example with correct types and values, keyword-before-identifier ordering is demonstrated, and gaps are detected and reported with their position
  readings:
    - rtitle: "Regular Expressions Activity"
      rlink: "Activities/liascript-regex.md"
      liapage: true
    - rtitle: "Python re Documentation"
      rlink: "https://docs.python.org/3/library/re.html"

tags:
  - regex
  - languages
  - lab

---

This **lab** turns the regular-expression theory from class into a tool you can use.  You leave with three things: a set of `re` experiments you ran and varied yourself, a `check()` test harness with your first three passing patterns, and a `re.finditer` mini lexer that tokenizes `let x = 42` and reports the one character it does not recognize.  All three feed the [Regular Expressions assignment]({{ site.baseurl }}/Assignments/Regex) directly: its Part 1 grows the harness to ten patterns, its Part 2 completes the mini lexer, and the Lexer assignment later turns the same lexer into a permanent pipeline component.

Work the parts in order.  Parts 1 and 2 are walkthroughs: I show you something, you run it, then you vary it and write down what happened.  Parts 3 and 4 build the two artifacts everything downstream grows from, in the same rhythm.  Every code block here runs as it stands.  Put it in a file, run it, change something, and run it again.  Reading these blocks without running them is the one way to get nothing out of this lab.

**Pair policy.**  You may do this lab in pairs.  Driver and navigator at one screen works well; swap at the start of Part 3.  You each submit the same files, name the other in the readme, and both get the same grade.  You may also work alone.  The Regex assignment itself remains individual work: you may both reuse this lab's shared artifacts there, but everything you add beyond them must be your own.

---

## Before You Start

You need:

- Python 3.10 or newer.  The `re` module is in the standard library, so there is nothing to install.
- A text editor (VS Code or any editor you like) and a terminal.  If either is new to you, work through the [dev environment page]({{ site.baseurl }}/Tutorials/DevEnvironment) and the [shell primer]({{ site.baseurl }}/Tutorials/ShellForLanguageDev) first.
- The Regular Expressions activity and the Python `re` documentation (both in the readings above) open in a browser tab.

> **Do this.**
> 1. Create a folder named `cs374-regex` somewhere you will find again.  Every file in this lab lives there, and the Regex assignment's files join them later.
> 2. Open a terminal in that folder.  In VS Code, choose File > Open Folder, pick `cs374-regex`, then Terminal > New Terminal.
> 3. Confirm that Python answers:
>
> ```bash
> python3 --version
> ```

> **You should see.** One line naming a Python version 3.10 or newer.  Write it down; the readme asks for it.  If the command is not found on Windows, try `python --version` or `py --version`, and use that spelling in place of `python3` for the rest of the lab.  A version below 3.10 means installing a current Python from python.org, then reopening the terminal.

```text
Python 3.11.15
```

> **Time budget.** About 3 hours, roughly 45 minutes per part.  Budget more if the terminal is new to you.

### Your First 15 Minutes

1.  Create `five_verbs.py` in `cs374-regex`, paste the Step 1.1 code into it, and run `python3 five_verbs.py`.  Compare its six lines with the **You should see** box there.
2.  Replace `19426` in the text with `194260` and run again.  The `[ZIP]` disappears, because `\b\d{5}\b` no longer finds five digits with a boundary on both sides.
3.  Put `19426` back.  That loop (edit, run, read the output) is the entire method for this lab.

### Suggested Pacing

See the course schedule for the assigned and due dates.  This lab is due partway through the Regex assignment, whose pacing table expects your harness and mini lexer to arrive from here.

| Checkpoint | You should have |
|------------|-----------------|
| First sitting | Parts 1 and 2 run and varied; `part1.md` answered; `part2.md` started |
| Halfway mark | `part2.md` answered; partners swap driver and navigator |
| Before you submit | `patterns.py` passing all three patterns; `mini_lexer.py` tokenizing the worked example and reporting the gap; `readme.md` written |

---

## Part 1: Python's `re` in Five Verbs (25%)

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

## Part 2: Watching the Engine Backtrack (20%)

Matching is not a single left-to-right sweep.  Whenever the pattern offers a choice (how many repetitions a star takes, which branch of an alternation to try), the engine makes the greedy choice first and remembers the decision point.  If the rest of the pattern later fails, the engine backtracks: it returns to the most recent decision, takes the next alternative, and pushes forward again.

**Worked example.**  Match `a*ab` against `"aaab"` with `re.fullmatch`.  Read the pattern as "any number of `a`s, then one more `a`, then a `b`."  The greedy `a*` first takes every `a` it can, which is one too many.

| Step | `a*` currently holds | Rest of pattern needs | Rest of input is | Outcome |
|------|----------------------|-----------------------|------------------|---------|
| 1 | `"aaa"` (greedy maximum) | `ab` | `"b"` | `a` vs `b` fails -> **backtrack** |
| 2 | `"aa"` (gave one back) | `ab` | `"ab"` | `ab` = `ab` -> **MATCH** |

Two attempts, one backtrack.  Now trace the same pattern against `"ab"` on paper before you run anything.

### Step 2.1: The walkthrough

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

> **Checkpoint.** Compare the `'ab'` block with your paper trace.  If your trace had `a*` start with `''` instead of `'a'`, you traced a reluctant star, not a greedy one.  Step 2.2 lets you run that version too.

**Reading the code.**  `max_a` is the greedy maximum, the most `a*` could possibly take.  The descending loop `range(max_a, -1, -1)` is greed itself: try the longest take first, and give characters back only when forced.  A reluctant `a*?` would count upward from 0, and nothing else would change.  Each iteration revisits one decision point, so the number of iterations before success is the amount of backtracking the engine did, and the last line confirms the narration agrees with `re.fullmatch` on every input.

> **Watch out.** Backtracking is invisible when a match succeeds quickly, but it is still happening.  On pathological patterns, such as nested quantifiers like `(a+)+` against input that almost matches, the number of decision points explodes and matching can take exponential time.  This is called catastrophic backtracking.  Knowing where decisions accumulate is how you avoid writing such patterns.

### Step 2.2: Now you: vary the search

Two small edits to `backtrack.py` produce the evidence Questions 7 and 8 ask for.

> **Do this.**
> 1. Below the existing loop, add a second loop over the same four inputs that prints `bool(re.fullmatch(r"a*ab", s))` next to `bool(re.fullmatch(r"a+b", s))`.
> 2. Run again and confirm the two columns agree on every input.
> 3. Flip the greed: change `range(max_a, -1, -1)` to `range(0, max_a + 1)`, run once more, and count the attempts for `"aaab"` and `"ab"`.  This is the reluctant `a*?`.
> 4. Change the range back before you submit, so the file you hand in traces the greedy engine.

> **You should see.** From step 2, four lines where both patterns agree: match, match, no match, no match.  From step 3, the `'aaab'` block takes three attempts (holding `''`, then `'a'`, then `'aa'`) and the `'ab'` block takes one, the mirror image of the greedy counts.

### Step 2.3: What to write up

Create `part2.md` and answer these in it:

6.  In the trace for `"aaab"`, how many characters does `a*` hold on its first attempt, and why that many?  State the general rule the engine follows when a greedy quantifier has a choice.
7.  Count the attempts for `"aaab"`, `"ab"`, and `"aaa"` from your output.  Which input forced the most work, and what property of that input caused it?
8.  `a*ab` describes exactly the same set of strings as `a+b`.  Verify this with `re.fullmatch` on all four test inputs rather than taking my word for it.  Then explain why the second pattern never needs to backtrack on these inputs.
9.  A pattern like `(a+)+b` against a long string of `a`s with no `b` can take exponential time.  Using the decision-point idea from the trace, explain in two or three sentences where all those decisions come from.
{: start="6"}

---

## Part 3: Harness and Pattern Starters (30%)

A test harness is a small function that runs your pattern against strings you already know the answer for and reports every disagreement.  The `check()` harness below is the one from the Regex assignment's Part 1, copied verbatim, so that assignment starts from a running state.  It uses `fullmatch`, which succeeds only when the pattern matches the entire string.  That is deliberate: a pattern that matches only the front of `42abc` is too permissive, and `fullmatch` exposes it without `^` and `$` written by hand.

### Step 3.1: The walkthrough: one pattern through the harness

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

### Step 3.2: Now you: `INTEGER` and `IDENTIFIER`

Write and test the next two patterns from the assignment's pattern library: P2 `INTEGER` (an optionally signed integer with no leading zeros) and P3 `IDENTIFIER` (a letter or underscore followed by letters, digits, or underscores).  Each needs at least three positive and two negative cases; the starters below give the minimum, and you may add more.

> **Do this.**
> 1. Append the skeleton below to `patterns.py`, under the `COURSE_CODE` check.
> 2. Replace each `TODO` pattern with your own, keeping the raw-string `r"..."` form.
> 3. Run `python3 patterns.py` after each pattern until all three lines say `PASS`.

```python
# P2 INTEGER: an optionally signed integer with no leading zeros.
# TODO: write the pattern.  Decide what "no leading zeros" means for "0" itself.
INTEGER = r"TODO"
check("INTEGER", INTEGER,
      should_match=["42", "-7", "0"],
      should_not_match=["007", "4.2", "42abc"])

# P3 IDENTIFIER: a letter or underscore, then any mix of letters, digits, and underscores.
# TODO: write the pattern.
IDENTIFIER = r"TODO"
check("IDENTIFIER", IDENTIFIER,
      should_match=["x", "_tmp", "total_1"],
      should_not_match=["1st", "foo-bar"])
```

> **You should see.** Three `PASS` lines and nothing else.

```text
PASS COURSE_CODE (3 positive, 2 negative)
PASS INTEGER (3 positive, 3 negative)
PASS IDENTIFIER (3 positive, 2 negative)
```

> **If it fails.**
> - `Should NOT match but DID: '007'`: your integer pattern allows leading zeros.  Zero on its own is a special case; every other integer starts with `1` through `9`.
> - `SHOULD match but did NOT: '0'`: you excluded zero along with the leading zeros.  Add it back as its own alternative.
> - `Should NOT match but DID: '42abc'` cannot happen under `fullmatch`; if you see it, you switched the harness to `search` or `match`.  Switch it back.

### Step 3.3: What to write up

Use raw strings throughout.  Write one sentence per pattern explaining each non-trivial construct, as a comment directly above the pattern in `patterns.py`, the way the `COURSE_CODE` comment does.  The assignment requires this for all ten patterns, so set the habit now.

---

## Part 4: One Pattern, Every Token (25%)

A lexer does not run one pattern at a time over the source.  It joins every token pattern into a single master alternation, gives each alternative a named group, and lets `finditer` sweep the input once.  After each match, `m.lastgroup` names the alternative that fired, which is the token type, and `m.start()` says where it was, which is what an error message needs.

Two rules govern that master pattern, and both bite:

- Order matters.  Alternation takes the first alternative that matches at a position, not the longest.  If `IDENT` comes before `LET`, then `let` lexes as an identifier and your keyword never fires.
- Gaps are not free.  `finditer` silently skips any character no alternative claims, and a lexer that does the same hands the parser a token stream that quietly omits the typo.  Track the end of the previous match, and report anything between it and the start of the next one.

### Step 4.1: The walkthrough: watch `finditer` sweep

This probe builds the master pattern from an ordered `TOKEN_SPEC` and prints every match, whitespace included, so you can see the gap with your own eyes.

> **Do this.**
> 1. Create `mini_lexer.py` in `cs374-regex` and paste the code below into it.
> 2. Replace the two `TODO` patterns with your `IDENTIFIER` and `INTEGER` patterns from Part 3.  Paste the pattern text itself; do not import `patterns.py`, or its `check()` calls will run every time the lexer starts.
> 3. Run `python3 mini_lexer.py`.

```python
import re

# Ordered: the engine tries these left to right at each position.
TOKEN_SPEC = [
    ("WHITESPACE", r"[ \t\n]+"),
    ("LET",        r"let"),      # the keyword, listed before IDENT on purpose
    ("IDENT",      r"TODO"),     # TODO: paste your Part 3 IDENTIFIER pattern
    ("NUMBER",     r"TODO"),     # TODO: paste your Part 3 INTEGER pattern
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

### Step 4.2: Now you: `mini_lex()` with gap detection

Turn the probe into the skeleton the Regex assignment's Part 2 completes.  `mini_lex()` returns a list of `(token_type, value, start_pos)` tuples, skips whitespace, and reports any unclaimed character with its position instead of dropping it.  Three rules are enough here: `LET`, `IDENT`, and `NUMBER`.

> **Do this.**
> 1. In `mini_lexer.py`, replace the `print("master pattern:", ...)` line and the probe loop with the skeleton below.
> 2. Fill in the three `TODO`s.  `pos` always holds where the previous match ended; a match that starts anywhere else means something was skipped.
> 3. Run `python3 mini_lexer.py`, check both lines against the box below, then copy them into a comment or the module docstring at the top of `mini_lexer.py`.  That captured run is part of the deliverable.

```python
def mini_lex(source: str) -> list:
    """Return a list of (token_type, value, start_pos) tuples, skipping whitespace.
    Report, with its position, any text between matches that no rule claims."""
    tokens = []
    pos = 0                                  # where the previous match ended
    for m in MASTER.finditer(source):
        # TODO: if m.start() != pos, the text source[pos:m.start()] was skipped.
        #       Report it and its position instead of dropping it silently.
        # TODO: unless m.lastgroup is "WHITESPACE", append
        #       (m.lastgroup, m.group(), m.start()) to tokens.
        pos = m.end()
    # TODO: if pos != len(source), the tail of the input was skipped too. Report it.
    return tokens

if __name__ == "__main__":
    for src in ["let x = 42", "lets"]:
        print(f"{src!r} -> {mini_lex(src)}")
```

> **You should see.** `let x = 42` gives `LET`, `IDENT("x")`, a gap report for `=`, then `NUMBER("42")`.  The wording of the gap line is yours, but it must name `'='` and position 6.  Then `lets` comes out as one `IDENT`, not `LET` plus `IDENT("s")`.

```text
GAP: unrecognized '=' at position 6
'let x = 42' -> [('LET', 'let', 0), ('IDENT', 'x', 4), ('NUMBER', '42', 8)]
'lets' -> [('IDENT', 'lets', 0)]
```

> **If it fails.**
> - `'lets' -> [('LET', 'let', 0), ('IDENT', 's', 3)]`: your keyword rule is missing its boundary check.  `let` on its own matches the front of `lets`; the rule needs to insist that no word character follows (a `\b` after `let` is the simplest fix).  This is the ordering lesson the Regex assignment's Part 2 builds on.
> - `('IDENT', 'let', 0)` appears: the keyword rule is ordered after the identifier rule.
> - No gap line at all: your first `TODO` is not firing.  Print `pos` and `m.start()` inside the loop to see where they disagree.

### Step 4.3: What to write up

10.  In `part2.md` or a comment at the bottom of `mini_lexer.py`: you now have two ways to find many things in one string, `findall` and `finditer`.  Say in one sentence why a lexer cannot be built on the first one.
{: start="10"}

---

## Deliverables

Submit a ZIP of your `cs374-regex` folder containing the files below.

| File or artifact | What it shows | Rubric row |
|------------------|---------------|------------|
| `five_verbs.py` | The Part 1 walkthrough, run as it stands | The Five Verbs |
| `findall_shapes.py` | The shape experiment with the `finditer` `TODO` completed | The Five Verbs |
| `part1.md` | Answers to Questions 1-5, from your own output | The Five Verbs |
| `backtrack.py` | The narrated trace, with the `a+b` comparison from Step 2.2 | Backtracking |
| `part2.md` | Answers to Questions 6-9 (and Question 10 if you put it here) | Backtracking |
| `patterns.py` | The `check()` harness plus three tested patterns with one-sentence explanations | Harness and Pattern Starters |
| `mini_lexer.py` | The skeleton, with the worked-example run captured in a comment or docstring, and Question 10 if not in `part2.md` | Mini-Lexer Skeleton |
| `readme.md` | Both partners' names (or a note that you worked alone) and your Python version | All rows |

---

## Self-Check Before You Submit

- [ ] Every answer in `part1.md` and `part2.md` cites output you produced, not the documentation.
- [ ] `findall_shapes.py` prints full text, captured digits, and start position for each match.
- [ ] `part2.md` compares attempt counts across `"aaab"`, `"ab"`, and `"aaa"`, and Question 8 shows the `re.fullmatch` verification rather than asserting it.
- [ ] `python3 patterns.py` prints three `PASS` lines; every pattern is a raw string with at least three positive and two negative cases and a one-sentence comment.
- [ ] `python3 mini_lexer.py` tokenizes `let x = 42` with the right types and values, reports the `=` gap with position 6, and lexes `lets` as one `IDENT`.
- [ ] `mini_lexer.py` builds one compiled alternation with named groups and uses `re.finditer`, not `re.match` in a loop.
- [ ] `readme.md` names both partners (or says you worked alone) and lists your Python version.

---

## Grading Breakdown

This lab is worth 15 points, as the course schedule states.  Each part's weight below is a percentage of those 15 points, and the rubric rows use the same percentages.

| Component | Weight |
|-----------|--------|
| Part 1: The Five Verbs | 25% |
| Part 2: Watching the Engine Backtrack | 20% |
| Part 3: Harness and Pattern Starters | 30% |
| Part 4: One Pattern, Every Token | 25% |
| **Total** | **100% (15 points)** |

---

## Reflection Prompts

- Which negative test case caught a real bug in one of your patterns, and what was the fix?
- Which of the four `findall` shapes surprised you, and what will you do differently because of it?
- If you worked in a pair, who did what, and name one thing your partner caught that you would have missed.  If you worked alone, note that instead.
