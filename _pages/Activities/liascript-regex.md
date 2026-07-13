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

Regular expressions sit at the formal foundation of every programming language: they are the notation that defines what a *token* looks like before a parser ever sees it. Think of a regex as a cookie cutter — it describes a precise shape (a pattern) that can stamp out any number of matching strings from the dough of possible input, without caring what flavor the dough is. Because a single pattern can describe an infinite set of strings (e.g., all valid identifiers), regular expressions give language designers a compact, mathematically grounded way to specify lexical rules.

## Learning Goals

By the end of this activity, you will be able to:

- Define the three fundamental regular expression operators (concatenation, alternation, Kleene star) and construct regular expressions for specified string sets using only these operators
- Trace a regular expression against a target string to predict whether it matches, citing operator precedence rules where applicable
- Implement pattern matching, capturing, and substitution tasks using Python's `re` module (`match`, `search`, `fullmatch`, `findall`, `sub`)
- Identify the limits of regular expressions by constructing a language that requires counting or matching nested structure, and explaining why no regex can describe it
- Write the regular expression for a programming language token type (identifier, integer literal, floating-point literal) suitable for use in a lexer specification

The Chomsky hierarchy's bottom rung, regular languages, comes with the most widely used notation in computing: **regular expressions**. Over this two-day module we master them twice: as *theory* (three operators and what they can and cannot describe) and as *practice* (Python's `re` library, the tool of your next assignment and the specification language of your lexer). The arc: **the three operators $\rightarrow$ practical syntax $\rightarrow$ matching, capturing, substituting in Python $\rightarrow$ the limits**.

---

> **Before You Begin** — make sure you are comfortable with the following before diving in:
>
> - **Python `re` module basics** — you should know how to import `re` and call `re.search` or `re.match` with a pattern string; if not, skim the [Python `re` HOWTO](https://docs.python.org/3/howto/regex.html) for five minutes.
> - **Lexers and tokens** — recall that a lexer (scanner) reads source text and groups characters into *tokens* (e.g., an integer literal, an identifier, a keyword). Its job is essentially pattern matching: each token type has a pattern it must fit.
> - **Finite automata (conceptually)** — you do not need to draw one yet, but you should know that a finite automaton is a machine with a fixed set of states and no unbounded memory. Regular expressions and finite automata turn out to describe exactly the same class of languages — that connection is the bridge to the next module.

---

## Directions and Group Roles

Work in your POGIL team with rotated roles (**Manager**, **Recorder**, **Presenter**, **Reflector**). Consider each model and question individually first, then discuss with your group. The Recorder posts answers to the Class Activity Questions discussion board; the Presenter reports out areas of disagreement or alternative approaches. After class, respond to the reflective prompt individually in your notebook.

---

## Key Concepts

Before diving in, here is a plain-English glossary of the terms this activity uses. Return to this table whenever a term feels slippery.

| Term | Plain-English meaning | Why it matters |
|------|-----------------------|----------------|
| **Regular expression** | A compact pattern that describes a whole *set* of strings at once | It is the specification language for every token type in your lexer |
| **Concatenation** | Gluing patterns side by side: "this, then that" | The invisible default operator; most of any pattern is concatenation |
| **Alternation (`\|`)** | "Either this or that" | Lets one pattern cover several spellings, like `if\|else\|while` |
| **Kleene star (`*`)** | "Zero or more repeats of the thing just before me" | The only source of infinity in a regex; identifiers of any length need it |
| **Character class (`[0-9]`, `\d`)** | "Any one character from this menu" | Abbreviates long alternations and keeps patterns readable |
| **Anchor (`^`, `$`, `\b`)** | Matches a *position* (start, end, word edge), not a character | Stops a match from beginning or ending mid-word |
| **Capture group `(...)`** | Parentheses that *remember* the text they matched | How you extract data from text rather than merely detect it |
| **Greedy quantifier** | Takes as many characters as it can, giving some back only when forced | Explains most "my regex matched too much" surprises |
| **Backtracking** | The engine undoes a choice and tries the next alternative | How the engine actually searches — and why some patterns are slow |
| **Token** | The smallest meaningful chunk of source code (a number, a name, an operator) | The lexer's output; each token type is defined by one regex |

---

# Part I: Theory (Day 1)

Every regular expression you will ever write, no matter how elaborate, is built from exactly three primitive ideas. Before reading the formal definitions, convince yourself intuitively: you can glue strings together (concatenation), pick one of several alternatives (alternation), and repeat something zero or more times (Kleene star). That is the entire toolkit — the rest of regex syntax is just abbreviation.

## 1. Three Operators Build Everything

**A regular expression denotes a set of strings, built from three operations.** Given expressions $r$ and $s$ denoting languages $L(r)$ and $L(s)$:

$$
\underbrace{r\,s}_{\text{concatenation}} \quad \underbrace{r \mid s}_{\text{alternation (union)}} \quad \underbrace{r^*}_{\text{Kleene star: zero or more}}
$$

plus single characters and the empty string. Everything else in practical regex (character classes, `+`, `?`, ranges) is shorthand: $r^+ = rr^*$, $r? = (r \mid \varepsilon)$, $[abc] = (a \mid b \mid c)$. These three operators generate exactly the regular languages, the same class as Type 3 grammars and (next module) finite automata, three notations for one idea.

---

Before running any code, practice reading patterns the way a regex engine does: left to right, respecting precedence (star binds tightest, then concatenation, then alternation). The table below asks you to predict what each pattern matches — commit to a prediction first, then verify with the code. Mismatches between prediction and output are your most valuable learning signal.

> **Watch out!** The `*` in a regular expression is the **Kleene star** — it means "zero or more repetitions of the preceding element." It is *not* the glob wildcard you may know from the shell (where `*.py` means "any filename ending in `.py"`). In regex, `.*` means "any character, zero or more times," while a bare `*` with nothing before it is a syntax error.

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

[[MC]]
Matching `a*ab` against `"aaab"`, the engine's first attempt lets `a*` consume all three `a`s, and the rest of the pattern then fails. What happens next?
- ( ) The engine reports failure immediately
- ( ) The engine restarts with the reluctant interpretation of `*`
- (x) The engine backtracks: `a*` gives back one character and the rest of the pattern is retried from there
- ( ) The engine raises an exception because the pattern is ambiguous

### Critical Thinking Questions

8. In the trace for `"aaab"`, how many characters does `a*` hold on its *first* attempt, and why that many? State the general rule the engine follows when a greedy quantifier has a choice.
9. Count the attempts for `"aaab"`, `"ab"`, and `"aaa"` from the trace output. Which input forced the most work, and what property of that input caused it?
10. `a*ab` describes exactly the same set of strings as `a+b`. Verify this claim with `re.fullmatch` on all four test inputs, then explain why the second pattern never needs to backtrack on these inputs.
11. A pattern like `(a+)+b` against a long string of `a`s with **no** `b` can take exponential time. Using the decision-point idea from this model, explain in two or three sentences where all those decisions come from.

---

You have now seen how to match a single pattern; a real lexer must recognize *many* token types in a single pass over the source. The trick is to combine all token patterns into one master alternation and let Python's `finditer` do the scanning. Named groups let each alternative carry a label, so after a match you immediately know which token type fired — exactly the information a lexer needs to emit a token stream.

> **Watch out!** Quantifiers like `*`, `+`, and `?` are **greedy by default**: they consume as many characters as possible while still allowing the overall pattern to match. This is usually what you want in a lexer (match the longest token), but it can surprise you in other contexts. Append `?` to make a quantifier **non-greedy** (reluctant): `.*?` matches as *few* characters as possible. You will see this contrast demonstrated concretely in Model 3 (Greed).

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

12. The master pattern joins all specs with `|`. Why must multi-character operators like `>=` appear before single-character `>`? What happens to `>=` if you swap their order?
13. The `KEYWORD` pattern uses `\b` word boundaries. What would happen to the identifier `iffy` if keywords were matched without `\b`?
14. The `ERROR` catch-all `.` matches any single character not matched by earlier patterns. Why is this the *last* pattern rather than the first? What role does it play in error reporting?
15. The `SKIP` handler tracks newlines to maintain `line` and `line_start`. Why is accurate line/column tracking valuable for a language learner using your language?

---

Capture groups are what turn a regex from a yes/no detector into a *parser of flat records*: each group carves out one field of the matched text, and named groups label the fields. Nothing exercises this like log triage — the daily chore of turning thousands of text lines into structured data you can count, filter, and sort.

## Model 4: Log Triage — A Capture-Group Walkthrough

**Worked example.** Take one log line and the triage pattern:

```
line:    2026-09-18 08:10:22 WARN disk usage 91%
pattern: (?P<date>\d{4}-\d{2}-\d{2}) (?P<time>\d{2}:\d{2}:\d{2}) (?P<level>[A-Z]+) (?P<msg>.*)
```

The engine walks left to right, and each group records the *span* of text it consumed. Character positions (0-indexed):

```
2026-09-18 08:10:22 WARN disk usage 91%
0.........1.........2.........3........
└──date──┘ └─time─┘ └lv┘ └─────msg────┘
```

| Group | Sub-pattern | Text captured | Span (start, end) |
|-------|-------------|---------------|-------------------|
| `date` | `\d{4}-\d{2}-\d{2}` | `2026-09-18` | (0, 10) |
| `time` | `\d{2}:\d{2}:\d{2}` | `08:10:22` | (11, 19) |
| `level` | `[A-Z]+` | `WARN` | (20, 24) |
| `msg` | `.*` | `disk usage 91%` | (25, 39) |

Two details deserve attention. First, `[A-Z]+` is greedy, yet it stops cleanly after `WARN`: the next character is a space, which is not in the class `[A-Z]`, so the quantifier has nothing more it is *allowed* to take — the class boundary does the work, and no backtracking is needed. Second, `.*` in `msg` is also greedy and *does* swallow spaces, running to the end of the line (`.` matches every character except newline).

```python
import re
from collections import Counter

LOG = """\
2026-09-18 08:10:22 WARN disk usage 91%
2026-09-18 08:10:41 INFO backup started
2026-09-18 08:12:03 ERROR backup failed: disk full
2026-09-18 08:12:04 WARN retrying backup
2026-09-18 08:15:59 ERROR backup failed: disk full
2026-09-18 08:16:10 INFO alert emailed to admin
"""

PATTERN = re.compile(
    r"(?P<date>\d{4}-\d{2}-\d{2}) (?P<time>\d{2}:\d{2}:\d{2}) "
    r"(?P<level>[A-Z]+) (?P<msg>.*)")

records = []
for m in PATTERN.finditer(LOG):
    records.append(m.groupdict())
    if len(records) == 1:
        # show the spans for the first line, matching the walkthrough table
        for g in ("date", "time", "level", "msg"):
            print(f"  {g:5} = {m.group(g)!r:20} span {m.span(g)}")

print("\nTriage report:")
counts = Counter(r["level"] for r in records)
for level, n in counts.most_common():
    print(f"  {level:5} x{n}")

print("\nAll ERROR messages:")
for r in records:
    if r["level"] == "ERROR":
        print(f"  {r['time']}  {r['msg']}")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

[[MC]]
In `(?P<level>[A-Z]+) (?P<msg>.*)`, the `level` group stops at the end of `WARN` because:
- ( ) `+` is reluctant by default
- (x) The next character is a space, which is not in `[A-Z]`, so the greedy `+` has nothing more it is allowed to consume
- ( ) Named groups match at most four characters
- ( ) The `msg` group claimed the space first

### Critical Thinking Questions

16. Both `[A-Z]+` and `.*` are greedy, yet one stops at a space and the other swallows spaces to the end of the line. State the rule that predicts where any greedy quantifier stops.
17. Suppose a rogue line reads `2026-09-18 08:13:00 warning disk usage 92%` (lowercase level). Trace the pattern against it: which group's sub-pattern fails first, and what does `finditer` do with the line as a whole? Propose the smallest pattern change that would accept both spellings.
18. `m.span(g)` gives each field's exact offsets, and `m.groupdict()` gives a dictionary per line. In two sentences, relate this to your lexer: what plays the role of the token types here, and what plays the role of the token stream?
19. The `msg` group's `.*` would happily match an *empty* message (`.*` matches zero characters). Is that a bug or a feature for log triage? If your team decides empty messages are invalid, what one-character change enforces the decision?

---

This final model has two purposes: to make greedy-versus-reluctant matching concrete so it never surprises you again, and to close the theoretical loop by showing exactly where regular expressions run out of power. Both lessons point to the same underlying cause — a finite automaton has no stack, so it cannot count or remember how deeply it has nested.

> **Watch out!** Regular expressions **cannot match balanced (nested) parentheses** in general — for example, the language $\{(^n)^n \mid n \geq 0\}$ (equal numbers of open and close parens) is context-free, not regular. No matter how clever your regex, there exists a depth $n$ large enough to fool it. When you need to match nested structure, you need a parser built from a context-free grammar — exactly what the next unit covers.

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
