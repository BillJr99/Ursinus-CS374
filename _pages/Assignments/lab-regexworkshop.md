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

This **lab** turns regular expressions from Tuesday's theory into a tool you can use.  Work it in order.  Parts 1 and 2 are walkthroughs: I show you something, you run it, then you vary it and write down what happened.  Parts 3 and 4 are the two artifacts everything downstream grows from.  The first is the `check()` test harness with your first three passing patterns; the Regular Expressions assignment's Part 1 asks for ten.  The second is the `re.finditer` mini-lexer skeleton.  That assignment's Part 2 completes it, and the Lexer assignment later turns it into a permanent pipeline component.

Every code block here runs as it stands.  Put it in a file, run it, then change something and run it again.  Reading these blocks without running them is the one way to get nothing out of this lab.

**Pair policy.**  You may do this lab in pairs.  Driver and navigator at one screen works well here; swap at the halfway mark.  You each submit the same files and name the other in the readme, and you both get the same grade.  You may also work alone.  The Regex assignment itself remains individual work: you may both reuse this lab's shared artifacts there, but everything you add beyond them must be your own.

---

## Part 1: Python's `re` in Five Verbs (25%)

Python's `re` library adds engineering conveniences to the theory.  Anchors pin a match to a position: `^` is the start of the string and `$` is the end.  Character classes stand for one character from a set: `\d` is a digit, `\w` is a word character, and `\s` is whitespace.  Groups `(...)` capture the text they match so you can read it back later.  Five functions carry almost all the work: `re.search` (find the first match anywhere), `re.match` (match at the start), `re.findall` (all matches), `re.sub` (substitute), and `re.finditer` (iterate matches with positions).  Raw strings (`r"..."`) keep Python's own backslash handling out of your way.  Use them always.

### The walkthrough

Save this as `five_verbs.py` and run it.

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

**Reading the code.**

- `re.search` returns a match object or `None`.  That is why every use above checks `m` before reading it.  `m.group(1)` is the text captured by the first parenthesized group, not the whole match.  `m.group(0)` is the whole match.
- `re.findall` changes shape depending on your pattern.  With no groups it returns whole matches.  With exactly one group it returns only that group, which is why `r"#(\d+)"` yields bare numbers rather than `#`-prefixed ones.  With two or more groups it returns tuples.  This trips up everyone once, and the next exercise makes it trip you now, where it costs you nothing.
- `m.groups()` returns all captures at once, which is how the three-part date comes apart in one line.
- `\b` in the redaction pattern is a word boundary.  It is a zero-width assertion: it matches a position between characters, not a character itself.  Without it, `\d{5}` would match the first five digits of a longer number.
- `finditer` yields match objects with `.start()` and `.end()`, so you learn where each match sits.  Finding text and tokenizing it part company right there, and that is why Part 4 is built on `finditer` rather than `findall`.

### Now you: the `findall` shape experiment

Save this as `findall_shapes.py`.  Predict what each line prints before you run it, then run it.

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

Four nearly identical patterns give four different shapes of answer.

### What to write up

Answer these questions in `part1.md`, using output you produced:

1.  Predict, before running, what the redaction line prints.  What does `\b` contribute, and what over-matches without it?
2.  Design a one-line experiment that distinguishes `re.match` from `re.search`.  Run it, and state the rule in one sentence.
3.  The date pattern accepts `2026-99-99`.  Is that a defect of regular expressions, of this pattern, or of asking syntax to do the job of semantics?  Where in a language pipeline would the 99th month be caught?
4.  State the `findall` shape rule in one sentence you would trust on an exam.
5.  `finditer` reports start and end offsets.  Write two sentences to your future self explaining why a lexer needs exactly this capability and not only `findall`.

Complete the `TODO` in `findall_shapes.py` and include the file.

---

## Part 2: Watching the Engine Backtrack (20%)

Matching is not a single left-to-right sweep.  Whenever the pattern offers a choice, the engine makes the greedy choice first and remembers the decision point.  A star deciding how many repetitions to take is one such choice; an alternation deciding which branch to try is another.  If the rest of the pattern later fails, the engine backtracks: it returns to the most recent decision, takes the next alternative, and pushes forward again.

**Worked example.**  Match the pattern `a*ab` against `"aaab"` using `re.fullmatch`.  Read the pattern as "any number of `a`s, then one more `a`, then a `b`."  The greedy `a*` first takes every `a` it can, which turns out to be one too many.

| Step | `a*` currently holds | Rest of pattern needs | Rest of input is | Outcome |
|------|----------------------|-----------------------|------------------|---------|
| 1 | `"aaa"` (greedy maximum) | `ab` | `"b"` | `a` vs `b` fails -> **backtrack** |
| 2 | `"aa"` (gave one back) | `ab` | `"ab"` | `ab` = `ab` -> **MATCH** |

Two attempts, one backtrack.  Now trace the same pattern against `"ab"` yourself, on paper, before you run anything.

### The walkthrough

Save this as `backtrack.py` and run it.  It implements this one pattern as an explicit search that narrates every decision, then checks each verdict against Python's real engine.

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

**Reading the code.**

- `max_a` is the longest run of `a`s available, computed up front.  It is the greedy maximum: the most `a*` could possibly take.
- `for k in range(max_a, -1, -1)` counts downward.  That descending loop is greed: try the longest take first, and give characters back only when forced.  A reluctant `a*?` would count upward from 0 instead, and nothing else about the algorithm would change.
- Each iteration of that loop revisits one decision point.  The number of iterations before success is the amount of backtracking the engine did.
- The last line checks the narration against `re.fullmatch`.  This is not only a plausible story; it agrees with the real engine on every input.

> **Watch out.**  Backtracking is invisible when a match succeeds quickly, but it is still happening.  On pathological patterns, such as nested quantifiers like `(a+)+` against input that almost matches, the number of decision points explodes and matching can take exponential time.  This is called catastrophic backtracking.  Knowing where decisions accumulate is how you avoid writing such patterns.

### What to write up

Answer these in `part2.md`:

6.  In the trace for `"aaab"`, how many characters does `a*` hold on its first attempt, and why that many?  State the general rule the engine follows when a greedy quantifier has a choice.
7.  Count the attempts for `"aaab"`, `"ab"`, and `"aaa"` from your output.  Which input forced the most work, and what property of that input caused it?
8.  `a*ab` describes exactly the same set of strings as `a+b`.  Verify this with `re.fullmatch` on all four test inputs rather than taking my word for it.  Then explain why the second pattern never needs to backtrack on these inputs.
9.  A pattern like `(a+)+b` against a long string of `a`s with no `b` can take exponential time.  Using the decision-point idea from the trace, explain in two or three sentences where all those decisions come from.

---

## Part 3: Harness and Pattern Starters (30%)

Create `patterns.py` with the `check()` harness from the Regex assignment's Part 1.  Copy it verbatim.  This lab is where you get it working, so the assignment starts from a running state.  Then write and test these three patterns from the assignment's pattern library, each with at least three positive and two negative cases:

- P1 `COURSE_CODE`: department code of 2-4 capital letters, optional hyphen, three digits (`CS374`, `MATH-111` accept; `cs374`, `CS37` reject).
- P2 `INTEGER`: an optionally signed integer with no leading zeros (`42`, `-7`, `0` accept; `007`, `4.2` reject).  Anchor it: `"42abc"` must not pass.
- P3 `IDENTIFIER`: a letter or underscore followed by letters, digits, or underscores (`x`, `_tmp`, `total_1` accept; `1st`, `foo-bar` reject).

Use raw strings throughout.  Write one sentence per pattern explaining each non-trivial construct.  The assignment requires this for all ten patterns, so set the habit now.

---

## Part 4: One Pattern, Every Token (25%)

A lexer does not run one pattern at a time over the source.  It joins every token pattern into a single master alternation, gives each alternative a named group, and lets `finditer` sweep the input once.  This is why Part 1 spent so long on `finditer`.  After each match, `m.lastgroup` tells you which alternative fired, which is exactly the token type.  `m.start()` tells you where the match was, which is exactly what an error message needs.

Two rules govern that master pattern, and both bite:

- Order matters.  Alternation takes the first alternative that matches at a position, not the longest.  If `IDENT` comes before `LET`, then `let` lexes as an identifier and your keyword never fires at all.
- Gaps are not free.  `finditer` silently skips any character no alternative claims.  A lexer that skips unknown characters silently hands the parser a token stream that quietly omits the typo, and you will debug the wrong file for an hour.  Track the end of the previous match, and report anything between it and the start of the next one.

### What to build

Create `mini_lexer.py`: a single compiled alternation built from an ordered `TOKEN_SPEC` list with named groups, driven by `re.finditer`.  Your skeleton needs only three rules: `LET` (the keyword `let`), `IDENT` (Part 3's identifier pattern), and `NUMBER` (Part 3's integer pattern).  Add skipped whitespace and gap detection: report any character between matches that no rule claims, with its position, instead of dropping it silently.

Verify against this worked example: `let x = 42` -> `LET("let")`, `IDENT("x")`, *gap report for `=`*, `NUMBER("42")`.  Then confirm the ordering lesson that the Regex assignment's Part 2 builds on: `lets` must come out as one `IDENT`, not `LET` + `IDENT("s")`.  If it splits, your keyword rule is missing its boundary check or is ordered after the identifier rule.

10.  In `part2.md` or a comment at the bottom of `mini_lexer.py`: you now have two ways to find many things in one string, `findall` and `finditer`.  Say in one sentence why a lexer cannot be built on the first one.

---

## Deliverables

Submit a ZIP containing `five_verbs.py`, `findall_shapes.py` (with the `TODO` completed), `backtrack.py`, `part1.md` and `part2.md` (your written answers), `patterns.py` (harness + three tested patterns), `mini_lexer.py` (skeleton + the worked-example run captured in a comment or docstring), and a short `readme.md` naming both partners and listing your Python version.

## Grading Breakdown

This lab is worth 15 points, as the course schedule states.  Each part's weight below is a percentage of those 15 points, and the rubric rows use the same percentages.

| Component | Weight |
|-----------|--------|
| Part 1: The Five Verbs | 25% |
| Part 2: Watching the Engine Backtrack | 20% |
| Part 3: Harness and Pattern Starters | 30% |
| Part 4: One Pattern, Every Token | 25% |
| **Total** | **100% (15 points)** |

## Reflection Prompts

- Which negative test case caught a real bug in one of your patterns, and what was the fix?
- Which of the four `findall` shapes surprised you, and what will you do differently because of it?
- If you worked in a pair, who did what, and name one thing your partner caught that you would have missed.  If you worked alone, note that instead.
- AI disclosure: list any generative-AI tools you used, for what, and how you verified the results (or state 'none').
- Approximately how many hours it took you to finish this lab (I will not judge you for this at all; I am simply using it to gauge if the labs are too easy or hard)?
