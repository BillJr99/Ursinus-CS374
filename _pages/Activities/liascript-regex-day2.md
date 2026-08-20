<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://github.com/BillJr99/Ursinus-CS374-Fall2026/blob/gh-pages/_pages/Activities/liascript-regex-day2.md or locally via https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374/gh-pages/_pages/Activities/liascript-regex-day2.md

import: https://raw.githubusercontent.com/liascript/CodeRunner/master/README.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

# Regular Expressions, Day 2: Practice

Day 1 covered the three operators every regular expression is built from, and why the engine backtracks. Today we put them to work in Python: `re` in five verbs, `finditer` as the lexer's best friend, and the boundary where regular expressions stop being enough and you need a grammar instead.

> This is the second of two sessions on this topic. If you have not done Day 1, start there: [Regular Expressions](https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374/gh-pages/_pages/Activities/liascript-regex.md).

# Part II: Practice (Day 2)

Now that you can read and write the formal operators, the next step is wielding them in real code. Python's `re` module is the standard bridge between theory and practice: it accepts the same notation you have been studying and gives you a handful of functions that cover virtually every text-processing task you will encounter, including building the lexer for your course project.

## 2. Python's `re` in Five Verbs

Python's `re` library adds engineering conveniences to the theory: **anchors** (`^` start, `$` end), **character classes** (`\d` digit, `\w` word character, `\s` whitespace), **groups** `(...)` that *capture* what they match, and a small API: `re.search` (find first match anywhere), `re.match` (match at the start), `re.findall` (all matches), `re.sub` (substitute), and `re.finditer` (iterate matches with positions). Raw strings (`r"..."`) keep Python's backslash handling out of your way; use them always.

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
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

### Critical Thinking Questions

4. Predict, before running, what the redaction line prints. What does `\b` (word boundary) contribute; what over-matches without it?
5. `re.match` versus `re.search`: design a one-line experiment distinguishing them, run it, and state the rule.
6. The date pattern accepts `2026-99-99`. Is that a defect of regular expressions, of this pattern, or of asking syntax to do semantics' job? Where in a language pipeline would the 99th month be caught?
7. `finditer` reports start and end offsets. Write two sentences to your future self explaining why a *lexer* needs exactly this capability and not just `findall`.

---

Matching is not always a single left-to-right sweep. Whenever the pattern offers a choice — a star deciding how many repetitions to take, or an alternation deciding which branch to try — the engine makes the greedy choice first and *remembers the decision point*. If the rest of the pattern later fails, the engine **backtracks**: it returns to the most recent decision, tries the next alternative, and pushes forward again. Watching one backtracking match in slow motion demystifies greedy behavior now and prepares you for the automata view in the next module.

> **Watch out!** Backtracking is invisible when a match succeeds quickly, but it is still happening. On pathological patterns (nested quantifiers like `(a+)+` against input that *almost* matches), the number of decision points explodes and matching can take exponential time — so-called *catastrophic backtracking*. Knowing where decisions accumulate is how you avoid writing such patterns.

## Model 2: Watching the Engine Backtrack

**Worked example.** Match the pattern `a*ab` against the string `"aaab"` using `re.fullmatch`. Read the pattern as: "any number of `a`s, then one more `a`, then a `b`." The greedy `a*` first swallows every `a` it can — one too many, as it turns out.

| Step | `a*` currently holds | Rest of pattern needs | Rest of input is | Outcome |
|------|----------------------|-----------------------|------------------|---------|
| 1 | `"aaa"` (greedy maximum) | `ab` | `"b"` | `a` vs `b` fails → **backtrack** |
| 2 | `"aa"` (gave one back) | `ab` | `"ab"` | `ab` = `ab` → **MATCH** |

Two attempts, one backtrack. Now trace the same pattern against `"ab"` yourself before running the cell: `a*` first holds `"a"`, the rest of the pattern needs `ab` but only `"b"` remains — fail; backtrack so `a*` holds `""`, the rest of the input is `"ab"` — match on the second attempt again.

Run the cell below: it implements this specific pattern as an explicit search that narrates every decision, then confirms each verdict against Python's real engine.

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
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

Matching `a*ab` against `"aaab"`, the engine's first attempt lets `a*` consume all three `a`s, and the rest of the pattern then fails. What happens next?

[( )] The engine reports failure immediately
[( )] The engine restarts with the reluctant interpretation of `*`
[(X)] The engine backtracks: `a*` gives back one character and the rest of the pattern is retried from there
[( )] The engine raises an exception because the pattern is ambiguous

### Critical Thinking Questions

8. In the trace for `"aaab"`, how many characters does `a*` hold on its *first* attempt, and why that many? State the general rule the engine follows when a greedy quantifier has a choice.
9. Count the attempts for `"aaab"`, `"ab"`, and `"aaa"` from the trace output. Which input forced the most work, and what property of that input caused it?
10. `a*ab` describes exactly the same set of strings as `a+b`. Verify this claim with `re.fullmatch` on all four test inputs, then explain why the second pattern never needs to backtrack on these inputs.
11. A pattern like `(a+)+b` against a long string of `a`s with **no** `b` can take exponential time. Using the decision-point idea from this model, explain in two or three sentences where all those decisions come from.

---

You have now seen how to match a single pattern; a real lexer must recognize *many* token types in a single pass over the source. The trick is to combine all token patterns into one master alternation and let Python's `finditer` do the scanning. Named groups let each alternative carry a label, so after a match you immediately know which token type fired — exactly the information a lexer needs to emit a token stream.

> **Watch out!** Quantifiers like `*`, `+`, and `?` are **greedy by default**: they consume as many characters as possible while still allowing the overall pattern to match. This is usually what you want in a lexer (match the longest token), but it can surprise you in other contexts. Append `?` to make a quantifier **non-greedy** (reluctant): `.*?` matches as *few* characters as possible. You will see this contrast demonstrated concretely in Model 3 (Greed).


> **Named groups and the log-triage walkthrough moved to the shell tutorial.** Both are in [The Shell for Language Development](https://www.billmongan.com/Ursinus-CS374-Fall2026/Tutorials/ShellForLanguageDev), which is required prep for this session — named groups are how each token type gets its own label in your lexer.

## 3. Greed, and the Edge of the Regular World

**Quantifiers are greedy by default**: `<.*>` against `<a><b>` matches the whole string, because `*` takes as much as possible while still permitting a match; the reluctant form `<.*?>` matches `<a>`. And the theoretical wall stands: regular expressions cannot match **arbitrarily nested** structure (balanced parentheses is $a^n b^n$ wearing makeup), because finite memory cannot count unboundedly.

**Greedy vs reluctant — a concrete experiment:**

```python
import re

html = "<b>bold</b> and <i>italic</i>"

print("Greedy <.*>:")
m = re.search(r"<.*>", html)
print(f"  match: {m.group()!r}")

print("\nReluctant <.*?>:")
for m in re.finditer(r"<.*?>", html):
    print(f"  match: {m.group()!r}")

print("\nNested structure — why regex fails:")
balanced = "(a(b)c)"
print(f"  Testing {balanced!r}")
# This pattern CANNOT correctly handle arbitrary nesting:
bad_pattern = r"\([^()]*\)"
print(f"  Simple pattern: {re.findall(bad_pattern, balanced)}")
# finds "(b)" but not the outer "(a(b)c)" — proves finite memory limit

# For truly nested structures, you need a parser (CFG), not regex:
import ast
try:
    tree = ast.parse("(1 + (2 * 3))", mode="eval")
    print(f"  ast.parse handles nesting: {ast.dump(tree)[:60]}...")
except:
    pass
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

A teammate proposes one grand regular expression to validate fully parenthesized arithmetic of unlimited nesting depth. The principled response is:

[( )] Increase the pattern's length until it works
[( )] Use the re.DOTALL flag
[(X)] No regular expression can do this in general, because matched nesting requires counting beyond finite memory; this is the parser's job
[( )] Use findall instead of search

The pattern `r"\b(?:if|else|while)\b"` uses `(?:...)` (non-capturing group) rather than `(...)` (capturing group). The effect is:

[( )] The pattern fails to match keywords
[( )] The alternation `if|else|while` is broken
[(X)] The group matches but does not appear in `re.findall` results or `m.groups()`, since it's a grouping convenience only
[( )] It makes the pattern case-insensitive

### Critical Thinking Questions

20. The greedy `<.*>` matches from the first `<` to the *last* `>`. Why does the regex engine extend the match to the last `>`? Describe the backtracking process, using the decision-point vocabulary from Model 2.
21. The reluctant `<.*?>` finds each tag separately. Which is more useful for parsing HTML, and which is more useful for a lexer that needs to match string literals like `"hello"`?

---

# Part III: Synthesis and Practice

## 4. Exercises

1. *Pattern portfolio.* Write and test patterns for: a course code (`CS374`, `MATH-111`); a time (`8:10 AM`); a quoted string with no internal quotes; a Python comment to end of line. Each with three positive and two negative test cases, run in code.
2. *Log extraction.* Given lines like `2026-09-18 08:10:22 WARN disk usage 91%`, extract a list of `(date, level, message)` triples using one `finditer` pattern with three named groups.
3. *Greed lab.* Construct an input and pattern pair where greedy and reluctant quantifiers give different `group(0)` results, and explain the engine's choice in each case.
4. *Token preview.* Write the patterns for the token types your project language will need so far: identifier, integer, the operators from your expression ladder, and parentheses. Order matters when patterns overlap; note one ordering bug you anticipate (hint: `<=` versus `<`).
5. *Regex limits proof.* Write a Python function `is_balanced(s)` that returns True iff `s` has balanced parentheses, using a stack (not regex). Then explain in two sentences why this function cannot be replaced by any regular expression.

---

## Reflection Prompt

In your notebook: regular expressions are simultaneously beloved (irreplaceable for text work) and feared ("now you have two problems," as the joke goes). Having met both the theory and the practice, where do you think the fear actually comes from, and what working habit would prevent it? Now that you have built a lexer using regex, does the fear make more or less sense?

---

## 5. Further Reading

- Douglas Thain. *Introduction to Compilers and Language Design*, Chapter 3.
- Python `re` documentation and HOWTO: https://docs.python.org/3/library/re.html
- Russ Cox. "Regular Expression Matching Can Be Simple And Fast" (online), a bridge to next module's automata.
- [regex101.com](https://regex101.com) — interactive regex tester with explanation of each match step.

---

Up next: the *Finite Automata* activity builds the machines that execute these patterns — and everything here feeds the Regular Expressions assignment.
