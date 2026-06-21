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
| `a(b\|c)d` | ? |
| `[0-9]+\.[0-9]+` | ? |

**Verify your predictions:**
```python
import re

patterns = [
    ("ab*c",          ["ac", "abc", "abbc", "abbbbc", "aXc"]),
    ("(ab)*c",        ["c", "abc", "ababc", "ac", "abbc"]),
    ("a(b|c)d",       ["abd", "acd", "ad", "abcd", "aad"]),
    (r"[0-9]+\.[0-9]+", ["3.14", "0.0", "123.456", "3", ".14", "3."]),
]

for pattern, tests in patterns:
    print(f"\nPattern: {pattern!r}")
    for s in tests:
        m = re.fullmatch(pattern, s)
        print(f"  {s!r:12} → {'MATCH' if m else 'no match'}")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

### Critical Thinking Questions

1. For each pattern, write the set of strings in plain English and give two members and one non-member. Where did `ab*c` versus `(ab)*c` divide the team?
2. Star binds tighter than concatenation, which binds tighter than `|`. Where have you seen this exact design move (precedence by convention) earlier this week, and what notation made it unambiguous there?
3. Write a regular expression for identifiers as most languages define them: a letter or underscore, followed by any number of letters, digits, or underscores. This pattern reappears, verbatim, in your lexer.

---

# Part II: Practice (Day 2)

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

## Model 3: Named Groups and the Lexer Connection

**Named groups make a mini-lexer readable:**
```python
import re

# Named groups: each token type is a named group
TOKEN_SPEC = [
    ("NUMBER",   r"\d+(?:\.\d+)?"),
    ("KEYWORD",  r"\b(?:if|else|while|let|print|true|false)\b"),
    ("IDENT",    r"[A-Za-z_]\w*"),
    ("GE",       r">="), ("LE", r"<="), ("EQ", r"=="), ("NE", r"!="),
    ("ASSIGN",   r"="),
    ("GT",       r">"),  ("LT", r"<"),
    ("PLUS",     r"\+"), ("MINUS", r"-"), ("STAR", r"\*"), ("SLASH", r"/"),
    ("LPAREN",   r"\("), ("RPAREN", r"\)"),
    ("LBRACE",   r"\{"), ("RBRACE", r"\}"),
    ("SEMI",     r";"),
    ("SKIP",     r"[ \t\n]+"),
    ("COMMENT",  r"#[^\n]*"),
    ("ERROR",    r"."),
]

MASTER = re.compile("|".join(f"(?P<{name}>{pat})" for name, pat in TOKEN_SPEC))

def lex(source):
    line, line_start = 1, 0
    for m in MASTER.finditer(source):
        kind = m.lastgroup
        lexeme = m.group()
        col = m.start() - line_start + 1
        if kind == "SKIP":
            line += lexeme.count("\n")
            if "\n" in lexeme:
                line_start = m.end() - len(lexeme) + lexeme.rfind("\n") + 1
            continue
        if kind == "COMMENT":
            continue
        if kind == "ERROR":
            raise SyntaxError(f"line {line}, col {col}: unexpected {lexeme!r}")
        yield (kind, lexeme, line, col)

src = """let count = 0;
while (count <= 10) {
    count = count + 1;
}
print count;"""

for tok in lex(src):
    print(tok)
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

### Critical Thinking Questions

8. The master pattern joins all specs with `|`. Why must multi-character operators like `>=` appear before single-character `>`? What happens to `>=` if you swap their order?
9. The `KEYWORD` pattern uses `\b` word boundaries. What would happen to the identifier `iffy` if keywords were matched without `\b`?
10. The `ERROR` catch-all `.` matches any single character not matched by earlier patterns. Why is this the *last* pattern rather than the first? What role does it play in error reporting?
11. The `SKIP` handler tracks newlines to maintain `line` and `line_start`. Why is accurate line/column tracking valuable for a language learner using your language?

---

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

[[MC]]
A teammate proposes one grand regular expression to validate fully parenthesized arithmetic of unlimited nesting depth. The principled response is:
- ( ) Increase the pattern's length until it works
- ( ) Use the re.DOTALL flag
- (x) No regular expression can do this in general, because matched nesting requires counting beyond finite memory; this is the parser's job
- ( ) Use findall instead of search

[[MC]]
The pattern `r"\b(?:if|else|while)\b"` uses `(?:...)` (non-capturing group) rather than `(...)` (capturing group). The effect is:
- ( ) The pattern fails to match keywords
- ( ) The alternation `if|else|while` is broken
- (x) The group matches but does not appear in `re.findall` results or `m.groups()`, since it's a grouping convenience only
- ( ) It makes the pattern case-insensitive

### Critical Thinking Questions

12. The greedy `<.*>` matches from the first `<` to the *last* `>`. Why does the regex engine extend the match to the last `>`? Describe the backtracking process.
13. The reluctant `<.*?>` finds each tag separately. Which is more useful for parsing HTML, and which is more useful for a lexer that needs to match string literals like `"hello"`?

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
