# Regular Expressions
<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://github.com/BillJr99/Ursinus-CS374-Fall2026/blob/gh-pages/_pages/Activities/liascript-regex.md or locally via https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374/gh-pages/_pages/Activities/liascript-regex.md

import: https://raw.githubusercontent.com/liascript/CodeRunner/master/README.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

# Regular Expressions

The Chomsky hierarchy's bottom rung, regular languages, comes with the most widely used notation in computing: **regular expressions**. Over this two-day module we master them twice: as *theory* (three operators and what they can and cannot describe) and as *practice* (Python's `re` library, the tool of your next assignment and the specification language of your lexer). The arc: **the three operators $\rightarrow$ practical syntax $\rightarrow$ matching, capturing, substituting in Python $\rightarrow$ the limits**.

---

## Directions and Group Roles

Work in your POGIL team with rotated roles (**Manager**, **Recorder**, **Presenter**, **Reflector**). Consider each model and question individually first, then discuss with your group. The Recorder posts answers to the Class Activity Questions discussion board; the Presenter reports out areas of disagreement or alternative approaches. After class, respond to the reflective prompt individually in your notebook.

---

# Part I: Theory (Day 1)

## 1. Three Operators Build Everything

**A regular expression denotes a set of strings, built from three operations.** Given expressions $r$ and $s$ denoting languages $L(r)$ and $L(s)$:

$$
\underbrace{r\,s}_{\text{concatenation}} \quad \underbrace{r \mid s}_{\text{alternation (union)}} \quad \underbrace{r^*}_{\text{Kleene star: zero or more}}
$$

plus single characters and the empty string. Everything else in practical regex (character classes, `+`, `?`, ranges) is shorthand: $r^+ = rr^*$, $r? = (r \mid \varepsilon)$, $[abc] = (a \mid b \mid c)$. These three operators generate exactly the regular languages, the same class as Type 3 grammars and (next module) finite automata, three notations for one idea.

---

## Model 1: Read Before You Write

| Pattern | Intended meaning? |
|---------|-------------------|
| `ab*c` | ? |
| `(ab)*c` | ? |
| `a(b|c)d` | ? |
| `[0-9]+\.[0-9]+` | ? |

### Critical Thinking Questions

1. For each pattern, write the set of strings in plain English and give two members and one non-member. Where did `ab*c` versus `(ab)*c` divide the team?
2. Star binds tighter than concatenation, which binds tighter than `|`. Where have you seen this exact design move (precedence by convention) earlier this week, and what notation made it unambiguous there?
3. Write a regular expression for identifiers as most languages define them: a letter or underscore, followed by any number of letters, digits, or underscores. This pattern reappears, verbatim, in your lexer.

---

# Part II: Practice (Day 2)

## 2. Python's `re` in Five Verbs

Python's `re` library adds engineering conveniences to the theory: **anchors** (`^` start, `$` end), **character classes** (`\d` digit, `\w` word character, `\s` whitespace), **groups** `(...)` that *capture* what they match, and a small API: `re.search` (find first match anywhere), `re.match` (match at the start), `re.findall` (all matches), `re.sub` (substitute), and `re.finditer` (iterate matches with positions). Raw strings (`r"..."`) keep Python's backslash handling out of your way; use them always.

---

## Code Cell

```python
import re

text = "Order #1042 shipped 2026-09-18 to Collegeville, PA 19426; order #1043 pending."

try:
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
except Exception as e:
    print(f"[regex:demo] {e}")
    import traceback; traceback.print_exc()
```

---

## Model 2: Five Verbs, One Team

### Critical Thinking Questions

4. Predict, before running, what the redaction line prints. What does `\b` (word boundary) contribute; what over-matches without it?
5. `re.match` versus `re.search`: design a one-line experiment distinguishing them, run it, and state the rule.
6. The date pattern accepts `2026-99-99`. Is that a defect of regular expressions, of this pattern, or of asking syntax to do semantics' job? Where in a language pipeline would the 99th month be caught?
7. `finditer` reports start and end offsets. Write two sentences to your future self explaining why a *lexer* needs exactly this capability and not just `findall`.

---

## 3. Greed, and the Edge of the Regular World

**Quantifiers are greedy by default**: `<.*>` against `<a><b>` matches the whole string, because `*` takes as much as possible while still permitting a match; the reluctant form `<.*?>` matches `<a>`. And the theoretical wall from the grammars module stands: regular expressions cannot match **arbitrarily nested** structure (balanced parentheses is $a^n b^n$ wearing makeup), because finite memory cannot count unboundedly. When you feel yourself fighting a regex to parse nested anything, the tool is telling you to climb one rung of the hierarchy to a parser.

[[MC]]
A teammate proposes one grand regular expression to validate fully parenthesized arithmetic of unlimited nesting depth. The principled response is:
- ( ) Increase the pattern's length until it works
- ( ) Use the re.DOTALL flag
- (x) No regular expression can do this in general, because matched nesting requires counting beyond finite memory; this is the parser's job
- ( ) Use findall instead of search

---

# Part III: Synthesis and Practice

## 4. Exercises

1. *Pattern portfolio.* Write and test patterns for: a course code (`CS374`, `MATH-111`); a time (`8:10 AM`); a quoted string with no internal quotes; a Python comment to end of line. Each with three positive and two negative test cases, run in code.
2. *Log extraction.* Given lines like `2026-09-18 08:10:22 WARN disk usage 91%`, extract a list of `(date, level, message)` triples using one `finditer` pattern with three groups.
3. *Greed lab.* Construct an input and pattern pair where greedy and reluctant quantifiers give different `group(0)` results, and explain the engine's choice in each case.
4. *Token preview.* Write the patterns for the token types your project language will need so far: identifier, integer, the operators from your expression ladder, and parentheses. Order matters when patterns overlap; note one ordering bug you anticipate (hint: `<=` versus `<`).

---

## Reflection Prompt

In your notebook: regular expressions are simultaneously beloved (irreplaceable for text work) and feared ("now you have two problems," as the joke goes). Having met both the theory and the practice, where do you think the fear actually comes from, and what working habit would prevent it?

---

## 5. Further Reading

- Douglas Thain. *Introduction to Compilers and Language Design*, Chapter 3.
- Python `re` documentation and HOWTO: https://docs.python.org/3/library/re.html
- Russ Cox. "Regular Expression Matching Can Be Simple And Fast" (online), a bridge to next module's automata.
