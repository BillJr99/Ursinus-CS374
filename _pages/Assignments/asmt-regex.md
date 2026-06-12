---
layout: assignment
permalink: /Assignments/Regex
title: "CS374: Principles of Programming Languages - Regular Expressions"

info:
  coursenum: CS374
  points: 100
  goals:
    - To write and test regular expressions for matching, extraction, and substitution using Python's re library
    - To use groups, anchors, character classes, and quantifiers deliberately, including greedy versus reluctant behavior
    - To apply regular expressions to a realistic log-parsing task with positions via finditer
    - To articulate the limits of regular languages
  rubric:
    - weight: 60
      description: Algorithm and Implementation
      preemerging: The patterns fail to run or fail most provided test cases due to major issues
      beginning: The patterns run but fail on several provided test cases due to one or more minor issues
      progressing: The patterns pass the provided test cases but would fail in a general case due to a minor issue such as a missing anchor or an over-permissive class
      proficient: Correct patterns pass the provided and hidden test cases and would be reasonably expected to handle the general case, with greedy versus reluctant behavior controlled deliberately
    - weight: 30
      description: Code Quality and Documentation
      preemerging: Code commenting and structure are absent, or code structure departs significantly from best practice
      beginning: Code commenting and structure is limited in ways that reduce the readability of the program
      progressing: Code documentation is present that re-states the explicit code definitions
      proficient: Code is documented at non-trivial points in a manner that enhances the readability of the program, raw strings are used throughout, patterns are named and explained, and exceptions are handled with located messages and tracebacks
    - weight: 10
      description: Writeup and Submission
      preemerging: An incomplete submission is provided
      beginning: The program is submitted, but not according to the directions in one or more ways
      progressing: The program is submitted according to the directions with a minor omission, with at least superficial responses to the reflection prompts
      proficient: The program is submitted according to the directions, including a readme writeup describing the solution and thoughtful answers to the reflection prompts
  readings:
    - rtitle: "Regular Expressions Activity"
      rlink: "https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374/gh-pages/_pages/Activities/liascript-regex.md"
    - rtitle: "Python re Documentation"
      rlink: "https://docs.python.org/3/library/re.html"

tags:
  - regex
  - languages

---

In this assignment you will build fluency with regular expressions in four scaffolded parts, ending with a realistic extraction task. Use raw strings (`r"..."`) throughout, and wrap demonstration code in the exception pattern from class.

## Part 1: Matching Warmups (20 points of Part 1-3 credit)

Write a pattern for each, with at least three positive and two negative test cases run in code via a provided `check(pattern, should_match, should_not_match)` harness you implement once:

1. An Ursinus course code: two to four capital letters, an optional hyphen, then exactly three digits (`CS374`, `MATH-111`).
2. A legal identifier: a letter or underscore followed by letters, digits, or underscores.
3. A decimal number with an optional sign and optional fractional part (`-3`, `3.14`, `+0.5`, but not `.` or `3.`).
4. A 12-hour clock time with optional minutes and required meridiem (`8 AM`, `8:10 AM`, but not `13:00 AM` and not `8:5 PM`).

## Part 2: Extraction with Groups (scaffolded)

Given the provided sample of registrar-style lines such as:

```
MONGAN, WILLIAM | CS374-A | MWF 1:00 PM | PFAHLER 012
```

2a. Write one pattern with named groups extracting last name, first name, course, section, days, time, and room from a single line, and demonstrate it with `groupdict()`.

2b. Apply it with `finditer` over the whole multi-line sample, producing a list of dictionaries, and report the count of records found.

2c. One sample line is deliberately malformed. Your code must detect and report it (with its line number) rather than silently skipping it; explain your detection approach in a comment.

## Part 3: Substitution

3a. Redact all email addresses in a provided paragraph to `[EMAIL]` using `re.sub` (a practical, not perfect, email pattern is fine; state your simplifications).

3b. Convert dates from `MM/DD/YYYY` to ISO `YYYY-MM-DD` throughout a text using group references in the replacement.

3c. Demonstrate one greedy-versus-reluctant difference: a pattern and input where `.*` and `.*?` produce different extractions, with both outputs shown and one sentence of explanation.

## Part 4: Application: Log Triage

Given the provided server log (lines like `2026-09-18 08:10:22 WARN disk usage 91% on /dev/sda1`), write a program that:

1. Extracts `(date, time, level, message)` tuples with one `finditer` pattern.
2. Reports counts by level and the earliest and latest timestamps.
3. Extracts every percentage mentioned in WARN lines and reports the maximum.
4. Writes the ERROR lines, with their original line numbers, to `errors.txt`.

Externalize the input and output file paths in a small JSON configuration file.

## Limits Question (required in the writeup)

In your readme, explain in one paragraph why no regular expression can validate balanced nested parentheses in general, referencing the appropriate level of the Chomsky hierarchy, and name the component of your upcoming pipeline whose job that is.

## Deliverables

Submit a ZIP containing your code, your JSON configuration, your test harness and test runs, the generated `errors.txt`, and a readme writeup of approximately one page. Ensure reproducibility by fixing random seeds (where applicable) and listing software version information.

## Reflection Prompts

- Which pattern took the most revisions, and what misconception did the failures expose?
- Where did you choose a simpler pattern over a perfectly precise one, and how did you document the tradeoff?
- If collaboration with a buddy was permitted, did you work with a buddy on this assignment? If so, who? If not, do you certify that this submission represents your own original work? Please identify any and all portions of your submission that were not originally written by you.
- Approximately how many hours it took you to finish this assignment (I will not judge you for this at all...I am simply using it to gauge if the assignments are too easy or hard)?
