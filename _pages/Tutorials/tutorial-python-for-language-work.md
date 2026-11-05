---
layout: textbook
permalink: /Tutorials/PythonForLanguageWork
title: "CS374: Python for Language Work"

info:
  coursenum: CS374
  eyebrow: "Tutorial"
  numbering: false
  objectives:
    - "Use lists, tuples, dictionaries, sets, and frozensets, and say which one fits a job"
    - "Read a JSON file and a command-line argument, and handle a missing file or key"
    - "Write a class, a dataclass, an exception, and a generator"
    - "Use compiled regular expressions and capture groups"
    - "Write a small test file with unittest"

tags:
  - python
  - reference

---
# Tutorial: Python for Language Work

Most of a language tool comes down to a few data structures and a loop, and Python makes those short to write.  If you have written Python but have not used some of these, this page has what you need.  Use it as a reference: save each block as a scratch file, or type it at `python3`, run it, and compare what you see.

## Lists, Tuples, and Dictionaries

A **list** is an ordered sequence you can change, and a **tuple** is one you cannot.  We use a tuple for a fixed pair and a list for a sequence that grows.  A **dictionary** maps keys to values.

```python
rules = [("INT", "[0-9]+"), ("IDENT", "[a-z]+")]   # a list of pairs
name, pattern = rules[0]                            # unpack a pair
print(name, pattern)

rules.append(("WS", " +"))
print(len(rules), rules[-1])

ages = {"ada": 36, "grace": 85}
print(ages["ada"])
print(ages.get("alan"))          # missing key: None, not a crash
print(ages.get("alan", 0))       # or a default you choose
print("grace" in ages)
for key, value in ages.items():
    print(key, value)
```

> **You should see.**
>
> ```text
> INT [0-9]+
> 3 ('WS', ' +')
> 36
> None
> 0
> True
> ada 36
> grace 85
> ```

`ages["alan"]` would raise a `KeyError`.  Use `[...]` when a missing key is a bug that you want to hear about, and `.get` when a missing key is a normal answer.

A dictionary's values can be dictionaries too, which is how a table with rows and columns lives in Python.  Each `[...]` goes one level deeper:

```python
table = {"red": {"go": "green", "stop": "red"}, "green": {"go": "green", "stop": "red"}}
print(table["red"])
print(table["red"]["go"])
row = table["red"]
print(row["stop"])
print(table.get("blue", {}).get("go"))   # a missing row, and then a missing column
```

> **You should see.**
>
> ```text
> {'go': 'green', 'stop': 'red'}
> green
> red
> None
> ```

## Sets and Frozensets

A **set** holds each item once, in no particular order.  Use one when you only care whether something is present.

```python
seen = set()                 # {} would make an empty dictionary
seen.add("a")
seen.update(["a", "b"])      # add every item of a list; a is still there once
print(sorted(seen))
print("a" in seen, "z" in seen)
print(sorted({"a", "b"} | {"b", "c"}))   # union
print(sorted({"a", "b"} & {"b", "c"}))   # intersection
frozen = frozenset(seen)     # the same items, and it cannot change
print({frozen: "a set as a dictionary key"}[frozenset({"b", "a"})])
```

> **You should see.**
>
> ```text
> ['a', 'b']
> True False
> ['a', 'b', 'c']
> ['b']
> a set as a dictionary key
> ```

A set can print its items in any order, so wrap it in `sorted` when you want the same output every time.  A regular set can't go inside another set or serve as a dictionary key, because it could change after Python filed it away, and a `frozenset` can.  The second Finite Automata activity has [more worked examples of `set` and `frozenset`](https://liascript.github.io/course/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374-Fall2026/gh-pages/_pages/Activities/liascript-automata-day2.md#11).

## Strings and f-strings

An f-string puts a value inside a string.  Inside the braces, `!r` shows the value the way you would type it in code, with quotes around a string, which makes a stray space visible.

```python
state, symbol = "q0", "a"
print(f"{state},{symbol}")
print(f"read {symbol!r}")
line = "let x = 1;\nprint x;"
print(line.split("\n"))
print("q0,a".split(","))
print("  spaced  ".strip())
for ch in "ab":
    print(ch)
print(len("abc"), "abc"[0], "abc"[1:])
```

> **You should see.**
>
> ```text
> q0,a
> read 'a'
> ['let x = 1;', 'print x;']
> ['q0', 'a']
> spaced
> a
> b
> 3 a bc
> ```

## Files, JSON, and the Command Line

`with open(...)` opens a file and closes it for you.  `json.load` turns a JSON file into Python objects: each JSON object becomes a dictionary, and each JSON list becomes a list.  `sys.argv` holds the words you typed on the command line, and `sys.argv[0]` is the program's own name.  Save this as `read_config.py`:

```python
import json
import sys

config = {"name": "demo", "sizes": [1, 2]}
with open("config.json", "w") as f:
    json.dump(config, f)

with open("config.json") as f:
    loaded = json.load(f)

print(loaded["name"], loaded["sizes"][1])
print(sys.argv[1:])

try:
    open("missing.json")
except FileNotFoundError:
    print("no such file")
```

Run `python3 read_config.py a b`.

> **You should see.**
>
> ```text
> demo 2
> ['a', 'b']
> no such file
> ```

Paths are measured from the folder you run the program in, so a `FileNotFoundError` usually means you are in a different folder from the one you expected.  `pwd` tells you where you are.

## Functions, Modules, and `__main__`

Importing a file runs it, so a module that prints or does work when imported gets in the way of everything that imports it.  This guard runs its code only when you run the file directly:

```python
def double(n):
    return n * 2


def main():
    print(double(21))


if __name__ == "__main__":
    main()
```

Save this as `tools.py`.  `python3 tools.py` prints `42`.  In another file, `import tools` prints nothing, and `tools.double(4)` gives `8`.

## Classes, Dataclasses, and Exceptions

A class bundles data with the functions that use it.  `__init__` runs when you make an object, and `self` is that object.

```python
class Counter:
    def __init__(self, start=0):
        self.count = start

    def bump(self):
        self.count += 1
        return self.count


c = Counter(5)
print(c.bump(), c.bump(), c.count)
```

A **dataclass** writes `__init__`, `__repr__`, and `__eq__` for you, so that a class that only holds fields takes a few lines:

```python
from dataclasses import dataclass


@dataclass
class Point:
    x: int
    y: int = 0


p = Point(3)
print(p, p.x, p == Point(3, 0))
```

An **exception** is a class too.  Subclass `Exception` to make your own, and add fields when the error should carry details.  `raise` signals it, and `try` and `except` catch it:

```python
class ConfigError(Exception):
    def __init__(self, message, line):
        super().__init__(f"line {line}: {message}")
        self.line = line


try:
    raise ConfigError("bad value", 7)
except ConfigError as e:
    print(e, "|", e.line)
```

> **You should see,** across the three blocks.
>
> ```text
> 6 7 7
> Point(x=3, y=0) 3 True
> line 7: bad value | 7
> ```

## Testing with unittest

A test file is a class with methods whose names start with `test_`.  `unittest.main()` finds and runs them.

```python
import unittest


def double(n):
    return n * 2


class TestDouble(unittest.TestCase):
    def test_positive(self):
        self.assertEqual(double(2), 4)

    def test_type_error(self):
        with self.assertRaises(TypeError):
            double(None)


if __name__ == "__main__":
    unittest.main()
```

> **You should see.** Two dots, then `Ran 2 tests`, and then `OK`.  `python3 test_file.py -v` lists each test by name, and `python3 test_file.py > output.txt 2>&1` saves everything to a file, because unittest writes its report to the error stream.

## A Lexer's Tools

A lexer uses a few Python tools, and each one has a job:

| Tool | What it is | Its job in your lexer |
|---|---|---|
| a list of `(name, pattern)` tuples | an ordered sequence of pairs | `TOKEN_SPEC`: the rules, where list order is rule priority |
| `re.compile(p)` and `.match(source, pos)` | a compiled pattern that matches only if the match starts exactly at `pos` | try one rule at the current position; `None` means "this rule does not apply here" |
| `m.group()`, `m.end()` | the matched text, and the index just past it | the lexeme, and where the next token starts |
| a generator (`yield`) | a function that hands back one value each time it is asked | `tokenize`: produce one token at a time, only when the parser asks |
| `@dataclass` | a class whose `__init__`, `__repr__`, and `__eq__` Python writes for you | `Token`: four named fields, a readable printout, and `==` that compares fields |

Two details are easy to miss.

- **`match` versus `search`.**  `.match(source, pos)` succeeds only when the pattern begins exactly at `pos`.  `.search` skips ahead to the first place the pattern appears.  A lexer must use `match`, because skipping ahead would silently jump over characters that no rule recognizes.
- **How a generator stops.**  Each call to `next(gen)` runs the function until its next `yield`.  When the function returns, the next `next(gen)` raises `StopIteration`.  A `for` loop, or `list(gen)`, catches that for you.  A `Lexer` class calls `next` directly, so it has to know this.

Save the lines below as `explore_lexer.py`, a scratch file you do not submit, and run `python3 explore_lexer.py`:

```python
import re
from dataclasses import dataclass

# 1. A token specification is a list of (name, pattern) pairs.  List order is priority.
SPEC = [("INT", r"[0-9]+"), ("IDENT", r"[a-zA-Z_]\w*"), ("WS", r"[ ]+")]
print(SPEC[0], "| first rule's name:", SPEC[0][0])

# 2. Compile once; .match(source, pos) only matches starting AT pos.
INT = re.compile(r"[0-9]+")
source = "x = 42"
print(INT.match(source, 0))                 # 'x' is not a digit: None
m = INT.match(source, 4)                    # position 4 is the '4'
print(m.group(), m.start(), m.end())        # the text, where it starts, where the next token starts
print(INT.search(source, 0).group())        # search skips ahead; a lexer must not

# 3. A generator yields values one at a time, only when asked.
def count_up(n):
    for i in range(n):
        yield i
gen = count_up(2)
print(next(gen), next(gen))
try:
    next(gen)
except StopIteration:
    print("StopIteration: the generator is used up")
print(list(count_up(3)))                    # a for loop or list() asks until it stops

# 4. A dataclass writes __init__, __repr__, and __eq__ for you.
@dataclass
class Token:
    type: str
    value: str
    line: int
    col: int
a = Token("INT", "42", 1, 5)
print(a)
print(a == Token("INT", "42", 1, 5), a.type, a.col)
```

> **You should see.**
>
> ```text
> ('INT', '[0-9]+') | first rule's name: INT
> None
> 42 4 6
> 42
> 0 1
> StopIteration: the generator is used up
> [0, 1, 2]
> Token(type='INT', value='42', line=1, col=5)
> True INT 5
> ```
>
> **Predict** before you move on: in `"x = 42"`, what does `INT.match(source, 5)` return, and what is its `end()`?

The third line shows how a lexer moves forward.  `m.end()` is 6, which is where the next token begins, so advancing the position is `pos = m.end()`.

## Capture Groups and Group References

To take a date apart and put the pieces back together in a different order, you need two tools.  A *capture group* `(...)` remembers the text it matched.  A *group reference* such as `\1` in the replacement string of `re.sub` puts that remembered text back.  This walkthrough shows both on a date conversion that runs in the opposite direction from the one you will write: it turns ISO `YYYY-MM-DD` into the European `DD.MM.YYYY`.  You see every technique here, and you still decide for yourself how to apply it to `MM/DD/YYYY`.

> **Do this.**
> 1. Create `groups_demo.py` and paste the code below into it.
> 2. Run `python3 groups_demo.py`.  This file is practice.

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

# 7. Replacing WITHIN a group: capture the context you keep, rewrite only the part you change.
cfg = "user=alice token=8f3a91 retries=3 token=77c0de"
print("7.", re.sub(r"(token=)\w+", r"\1[REDACTED]", cfg))
print("   year only:", re.sub(ISO, r"2027-\2-\3", text))
print("   \\g<1> then digits:", re.sub(ISO, r"\g<1>0101", "2026-09-18"), "| \\1 then digits:", repr(re.sub(ISO, r"\10101", "2026-09-18")))
MONTHS = {"09": "Sep", "10": "Oct", "11": "Nov"}
print("   function:", re.sub(ISO_NAMED, lambda m: f"{m.group('year')}-{MONTHS[m.group('month')]}-{m.group('day')}", text))
```

> **You should see.** Twenty lines, numbered by section.  Section 4 and section 5 print the same sentence, section 6 shows the boundaries protecting the two longer numbers, and section 7 changes one piece of each match while leaving the rest exactly as it was.

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
7. user=alice token=[REDACTED] retries=3 token=[REDACTED]
   year only: 2027-09-18 was the deadline; it moved to 2027-10-02, then to 2027-11-30
   \g<1> then digits: 20260101 | \1 then digits: 'A01'
   function: 2026-Sep-18 was the deadline; it moved to 2026-Oct-02, then to 2026-Nov-30
```

**Reading the code.**

- **Section 1, numbering.**  Groups are numbered by the position of their *opening* parenthesis, counting from the left and starting at 1, so the year is group 1, the month group 2, and the day group 3.  Group 0 is always the whole match.  `span(2)` reports where group 2 sits in the string, here characters 5 through 7.
- **Section 2, alternation.**  `|` has the lowest precedence of any operator, so `\d{4}-0[1-9]|1[0-2]-\d{2}` means "`\d{4}-0[1-9]`, *or* `1[0-2]-\d{2}`."  On `2026-12-25` the first branch fails, and the second branch matches only `12-25`, without the year.  Wrapping the alternation in parentheses confines the choice to the month position.  That is how `(0[1-9]|1[0-2])` expresses "01 through 12" and `(0[1-9]|[12]\d|3[01])` expresses "01 through 31," and the same parentheses that confine the choice also capture the result.  Notice that `2026-02-31` still passes: as P7 says, a regex checks the format and ranges, not the calendar.
- **Section 3, non-capturing groups.**  `(?:...)` groups for precedence without capturing, so every group after it moves down one number.  If you add or remove a capturing group, renumber every reference that comes after it.
- **Section 4, group references.**  In the *replacement* string of `re.sub`, `\3` means "whatever group 3 captured in this match."  `re.sub` applies the replacement to every match, so all three dates are rewritten, including the one at the very start of the string and the one at the very end.  The replacement must be a raw string: without the `r`, Python turns `"\3"` into the control character `\x03` before `re` ever sees it, as the `not raw` line shows.  `\g<3>` is the long form of `\3`.  Use it when a literal digit follows the reference, because `\30` would be read as group 30.
- **Section 5, named groups.**  `(?P<year>...)` names a group, `\g<year>` refers to it in a replacement, and `m.group("year")` or `m.groupdict()` reads it in code.  The named form gives the same result as section 4 and cannot get the order wrong by miscounting.  Step 3.2 requires named groups for the log parser.
- **Section 6, boundaries.**  Without `\b`, the pattern matches the last ten characters of `12026-09-18` and the first ten of `2026-09-180`, and rewrites those pieces of longer numbers.  `\b` on both ends requires a non-word character (or the edge of the string) just outside the date.
- **Section 7, replacing within a group.**  `re.sub` always replaces the *whole match*; there is no way to point it at "just group 2."  So to change one piece and keep the rest, capture the pieces you keep and write them back with references, and write the new text literally where the changed piece goes.  In `r"\1[REDACTED]"`, `\1` puts back `token=` and `[REDACTED]` takes the place of the value, which was matched but deliberately not captured.  In `r"2027-\2-\3"`, the year is the changed piece, so it is the one part *not* referenced.  When a literal digit follows a reference, use the `\g<1>` form: `r"\10101"` does not mean "group 1, then `0101`"; Python's `re` reads `\101` as the octal escape for the letter `A`, so the year silently disappears and you get `'A01'`, with no error to warn you.  When the new text must be *computed* from what a group captured (a lookup, arithmetic, a change of case), pass a function instead: it receives the match object, transforms the one group it cares about, and passes the others through unchanged with `m.group(...)`.

> **Now try this.**
> 1. Change the section 4 replacement to `r"\2/\3/\1"` and predict the output before you run it.
> 2. Section 7 passed `re.sub` a function in place of the replacement string.  It calls the function once per match with the match object and inserts whatever string the function returns.  Predict, then run this one, which reorders instead of transforming: `re.sub(ISO_NAMED, lambda m: f"{m.group('day')}.{m.group('month')}.{m.group('year')}", text)`.  When is a function worth the extra typing?  (One answer: when the new text needs arithmetic or a lookup, such as turning `09` into `September`.)
