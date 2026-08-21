---
layout: assignment
permalink: /Assignments/RegexWorkshop
title: "CS374: Principles of Programming Languages - Lab: Regex Workshop"

info:
  coursenum: CS374
  purpose: "To get the Regular Expressions assignment off the ground with a partner — a working test harness, your first tested patterns, and the finditer mini-lexer skeleton that the Regex and Lexer assignments both grow."
  tilt:
    task: "With a partner, stand up the check() test harness, write and test three patterns from the Regex assignment's pattern library, and build the skeleton of the re.finditer mini lexer with a three-rule TOKEN_SPEC."
    criteria: "Assessed on a working harness with three passing tested patterns and a mini-lexer skeleton that tokenizes the worked example correctly, weighted 50/50 across the two parts; see the rubric below for the full breakdown."
  points: 100
  goals:
    - To set up a repeatable test harness for regular expression patterns
    - To write and test anchored, character-class, and quantified patterns against positive and negative cases
    - To build a re.finditer mini lexer skeleton with an ordered TOKEN_SPEC and named groups
  rubric:
    - weight: 50
      description: "Harness and Pattern Starters (Goals 1, 2)"
      preemerging: The harness does not run, or no pattern passes its test cases
      beginning: The harness runs but only one pattern passes, or patterns lack negative test cases
      progressing: All three patterns pass but a case is mislabeled (e.g., a negative case that actually matches), or raw strings are not used
      proficient: The check() harness runs cleanly; all three patterns pass at least three positive and two negative cases each, use raw strings, and carry a one-sentence explanation of each non-trivial construct
    - weight: 50
      description: "Mini-Lexer Skeleton (Goal 3)"
      preemerging: The skeleton is missing or uses re.match in a loop rather than re.finditer with alternation
      beginning: finditer is used but the TOKEN_SPEC ordering is wrong (keywords not before identifiers), misclassifying the worked example
      progressing: The worked example tokenizes correctly but gaps (unrecognized characters) pass silently
      proficient: A single compiled alternation with named groups tokenizes the worked example with correct types and values, keyword-before-identifier ordering is demonstrated, and gaps are detected and reported with their position
  readings:
    - rtitle: "Regular Expressions Activity"
      rlink: "https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374/gh-pages/_pages/Activities/liascript-regex.md"
    - rtitle: "Python re Documentation"
      rlink: "https://docs.python.org/3/library/re.html"

tags:
  - regex
  - languages
  - lab

---

This **lab** is the on-ramp for the Regular Expressions assignment, handed out the same day. In one sitting with a partner, you will build the two artifacts that everything in that assignment grows from: the `check()` test harness with your first three passing patterns (the assignment's Part 1 asks for ten), and the `re.finditer` mini-lexer skeleton (which the assignment's Part 2 completes, and the Lexer assignment later turns into a permanent pipeline component). Budget **two to three hours**.

**Pair policy:** this lab may be completed **in pairs** — driver/navigator at one screen works well here, swapping at the halfway mark. Both partners submit the same files, each naming the other in the readme, and both earn the same grade. (You may also work alone.) The Regex assignment itself remains individual work: you may both reuse this lab's shared artifacts there, but everything you add beyond them must be your own.

---

## Part 1: Harness and Pattern Starters (50 points)

Create `patterns.py` with the `check()` harness from the Regex assignment's Part 1 (copy it verbatim — this lab is where you get it working, so the assignment starts from a running state). Then write and test these three patterns from the assignment's pattern library, each with **at least three positive and two negative cases**:

- **P1 `COURSE_CODE`** — department code of 2-4 capital letters, optional hyphen, three digits (`CS374`, `MATH-111` accept; `cs374`, `CS37` reject).
- **P2 `INTEGER`** — an optionally signed integer with no leading zeros (`42`, `-7`, `0` accept; `007`, `4.2` reject). Anchor it — `"42abc"` must not pass.
- **P3 `IDENTIFIER`** — a letter or underscore followed by letters, digits, or underscores (`x`, `_tmp`, `total_1` accept; `1st`, `foo-bar` reject).

Use raw strings throughout, and write one sentence per pattern explaining each non-trivial construct — the assignment requires this for all ten patterns, so set the habit now.

## Part 2: Mini-Lexer Skeleton (50 points)

Create `mini_lexer.py`: a single compiled alternation built from an ordered `TOKEN_SPEC` list with named groups, driven by `re.finditer`. Your skeleton needs only three rules — `LET` (the keyword `let`), `IDENT` (Part 1's identifier pattern), and `NUMBER` (Part 1's integer pattern) — plus skipped whitespace and gap detection: any character between matches that no rule claims is reported with its position, not silently dropped.

Verify against this worked example: `let x = 42` → `LET("let")`, `IDENT("x")`, *gap report for `=`*, `NUMBER("42")`. Then confirm the ordering lesson that the Regex assignment's Part 2 builds on: `lets` must come out as one `IDENT`, not `LET` + `IDENT("s")` — if it splits, your keyword rule is missing its boundary check or is ordered after the identifier rule.

---

## Deliverables

Submit a ZIP containing `patterns.py` (harness + three tested patterns), `mini_lexer.py` (skeleton + the worked-example run captured in a comment or docstring), and a short `readme.md` naming both partners and listing your Python version.

## Grading Breakdown

| Component | Points |
|-----------|--------|
| Part 1: Harness and Pattern Starters | 50 |
| Part 2: Mini-Lexer Skeleton | 50 |
| **Total** | **100** |

## Reflection Prompts

- Which negative test case caught a real bug in one of your patterns, and what was the fix?
- If you worked in a pair, who did what, and name one thing your partner caught that you would have missed. If you worked alone, note that instead.
- AI disclosure: list any generative-AI tools you used, for what, and how you verified the results (or state 'none').
- Approximately how many hours it took you to finish this lab (I will not judge you for this at all — I am simply using it to gauge if the labs are too easy or hard)?
