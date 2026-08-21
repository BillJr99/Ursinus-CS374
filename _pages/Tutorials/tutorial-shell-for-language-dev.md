---
layout: default-standard
permalink: /Tutorials/ShellForLanguageDev
title: "CS374: Shell Skills for Language Development"

info:
  coursenum: CS374
  goals:
    - To use the terminal to run, test, and debug your language interpreter
    - To pipe interpreter output and compare it against expected output
    - To write a shell test harness that runs all test programs and reports PASS/FAIL
    - To use environment variables and exit codes to integrate with CI pipelines
    - To create a Makefile or run.sh that standardizes how your language is invoked

readings:
  - rtitle: "The Missing Semester of Your CS Education (Shell)"
    rlink: "https://missing.csail.mit.edu/2020/shell-tools/"
  - rtitle: "GNU Make Manual"
    rlink: "https://www.gnu.org/software/make/manual/make.html"

tags:
  - shell
  - tools
  - testing
  - final-project
---

# Shell Skills for Language Development

This tutorial teaches the shell skills you need to build, test, and ship your CS374 final-project interpreter. You already know Python. This bridges the gap between "I can run it in my IDE" and "I can run, test, and debug it confidently from the command line."

**Work through it at a terminal, not in a chair.** Each step below ends with a **Try it** box: a small, concrete thing to run against your own interpreter before moving on. By the last step you will have an executable interpreter, a test harness that reports PASS/FAIL, a Makefile that standardizes how your language is invoked, and a CI job that fails the build when a test regresses.

**What you need before you start.** A working interpreter you can run (even one that only prints a token stream is enough to follow along) and a terminal in the [course development environment]({{ site.baseurl }}/Tutorials/DevEnvironment).

**The running example.** Your interpreter is invoked as `python3 mylang.py <sourcefile>`, your source files use the extension `.ml`, test cases live in `tests/`, and expected outputs live in `expected/`. Adapt the paths to match your actual layout as you go.

| Step | You will build | Time |
|---|---|---|
| 1 | An interpreter you can run directly, with meaningful exit codes | 15 min |
| 2 | Output captured and diffed against expected results | 15 min |
| 3 | `test_runner.sh`, a harness that runs every test and reports PASS/FAIL | 30 min |
| 4 | A `Makefile` so `make test` is the only command anyone needs | 20 min |
| 5 | A debugging toolkit of shell one-liners | 20 min |
| 6 | Environment-variable configuration and a CI job | 25 min |

---

## Step 1: Run Your Interpreter from the Terminal

### Basic invocation

The simplest way to run your interpreter on a source file:

```bash
python3 mylang.py tests/fibonacci.ml
```

If your project is organized as a Python package (a directory with `__init__.py`), you can invoke it as a module instead:

```bash
python3 -m mylang tests/fibonacci.ml
```

Both forms work fine. The module form is slightly more portable because Python resolves the package root automatically regardless of where you `cd`.

### Making your interpreter executable directly

Add a **shebang line** as the very first line of `mylang.py`:

```python
#!/usr/bin/env python3
```

Then mark the file executable:

```bash
chmod +x mylang.py
```

Now you can invoke it without spelling out `python3`:

```bash
./mylang.py tests/fibonacci.ml
```

The `./` prefix is required because the current directory is not on your `PATH` by default. If you copy the file somewhere on your `PATH` (e.g., `~/.local/bin/`), you can drop the `./` entirely.

### Exit codes, why they matter

Your interpreter should call `sys.exit()` with a meaningful code before it terminates:

```python
import sys

def main():
    # ... run the interpreter ...
    if error_occurred:
        sys.exit(1)   # non-zero = failure
    else:
        sys.exit(0)   # zero = success
```

Exit code `0` means success. Any non-zero code means failure. The shell, CI systems, and your test harness all read this code to decide whether the run passed. If you forget to set it, Python exits with `0` even when your interpreter crashed internally; your test harness will then falsely report every run as a pass.

Check the exit code of the last command with `$?`:

```bash
python3 mylang.py tests/bad_syntax.ml
echo $?          # prints 1 if your interpreter exited with sys.exit(1)
```

---

> **Try it.** Add a shebang to your interpreter, `chmod +x` it, and run it as `./mylang.py` on a test program. Then run it on a program with a deliberate syntax error and check `echo $?`; if it prints `0`, your interpreter is lying about failure, and every harness you build later will believe it. Fix that now with `sys.exit(1)`.

---

## Step 2: Capture and Compare Output with Redirection

### Capturing output to a file

Redirect standard output to a file with `>`:

```bash
python3 mylang.py tests/fibonacci.ml > output.txt
```

The file `output.txt` is created (or overwritten) with everything the interpreter printed to stdout. This is how you build your `expected/` directory in the first place.

### Capturing stderr alongside stdout

By default `>` only redirects stdout. If your interpreter writes error messages to stderr, capture both streams with `2>&1`:

```bash
python3 mylang.py tests/bad.ml > output.txt 2>&1
```

`2>&1` means "redirect file descriptor 2 (stderr) to wherever file descriptor 1 (stdout) currently points." Order matters: write `> file 2>&1`, not `2>&1 > file`.

### Comparing output with diff

The `diff` command reports every line that differs between two files. A zero exit code means the files are identical; non-zero means they differ:

```bash
diff expected/fibonacci.txt output.txt
```

You can skip the intermediate file entirely using a **process substitution** `<(...)`. Everything inside `<(...)` runs as a subshell and its stdout is presented to the outer command as if it were a file:

```bash
diff expected/fibonacci.txt <(python3 mylang.py tests/fibonacci.ml)
```

This is the pattern your test harness will use for every test case.

### Appending vs overwriting

`>` overwrites. `>>` appends:

```bash
python3 mylang.py tests/case1.ml >> all_output.txt
python3 mylang.py tests/case2.ml >> all_output.txt
```

### Piping output through other commands

`|` sends the stdout of one command to the stdin of the next:

```bash
python3 mylang.py tests/fibonacci.ml | head -5    # first five lines of output
python3 mylang.py tests/fibonacci.ml | wc -l      # count output lines
python3 mylang.py tests/fibonacci.ml | sort        # sort output lines
```

---

> **Try it.** Pick one test program, run it, and save the output as its expected file. Now change one line of your evaluator so the result is wrong, and run the `diff` again; you should see exactly what changed. Undo the change. That diff is the whole idea behind Step 3.

---

## Step 3: Write a Shell Test Harness

Once you have more than two or three test cases, running them by hand becomes impractical. A shell script can run all of them automatically and print a summary.

### Complete test_runner.sh

Save this as `test_runner.sh` at the root of your project:

```bash
#!/bin/bash
PASS=0; FAIL=0
for test in tests/*.ml; do
    name=$(basename "$test" .ml)
    expected="expected/${name}.txt"
    actual=$(python3 mylang.py "$test" 2>&1)
    if [ -f "$expected" ] && diff -q <(echo "$actual") "$expected" > /dev/null 2>&1; then
        echo "PASS: $name"
        ((PASS++))
    else
        echo "FAIL: $name"
        if [ -f "$expected" ]; then
            diff <(echo "$actual") "$expected"
        fi
        ((FAIL++))
    fi
done
echo "Results: $PASS passed, $FAIL failed"
[ $FAIL -eq 0 ]  # exit 0 if all pass, 1 if any fail
```

Make it executable:

```bash
chmod +x test_runner.sh
./test_runner.sh
```

### Line-by-line explanation

**`for test in tests/*.ml`**: The shell expands the glob `tests/*.ml` into a list of matching file paths before the loop starts. Each iteration assigns one path to the variable `test`.

**`name=$(basename "$test" .ml)`**: `$()` runs a command in a subshell and captures its stdout as a string. `basename` strips the directory prefix and, when given a second argument, also strips that suffix. So `tests/fibonacci.ml` becomes `fibonacci`.

**`actual=$(python3 mylang.py "$test" 2>&1)`**: Runs your interpreter and captures both stdout and stderr into the variable `actual`. The quotes around `"$test"` prevent word-splitting if the filename contains spaces.

**`diff -q <(echo "$actual") "$expected" > /dev/null 2>&1`**: `diff -q` exits with `0` if the files are identical and `1` if they differ, but prints nothing (`-q` is "quiet" mode). We discard any remaining output with `> /dev/null 2>&1`. The condition `[ -f "$expected" ]` guards against test cases that do not yet have a corresponding expected file.

**`((PASS++))`**: Arithmetic in bash uses `(( ))`. This increments the counter.

**`[ $FAIL -eq 0 ]`**: This is the last command in the script, so its exit code becomes the script's exit code. If `FAIL` is zero the condition is true and the script exits `0`. If any tests failed it exits `1`. CI tools pick this up automatically.

### Creating the expected/ directory

Run this once after you are confident your interpreter produces the right output:

```bash
mkdir -p expected
for f in tests/*.ml; do
    name=$(basename "$f" .ml)
    python3 mylang.py "$f" > "expected/${name}.txt" 2>&1
done
```

Commit both `tests/` and `expected/` to git so the test harness has something to compare against.

---

> **Try it.** Save `test_runner.sh`, `chmod +x` it, and run it. Every test should report PASS. Now break one on purpose and confirm the harness reports FAIL *and* exits non-zero (`echo $?`); a harness that always exits `0` will make CI green no matter what.

---

## Step 4: Standardize the Commands with a Makefile

A `Makefile` gives every contributor (including you after a vacation) a single consistent interface. `make run FILE=tests/fib.ml`, `make test`, `make clean` all just work.

### Complete Makefile

Save this as `Makefile` at the root of your project. **Indented lines must use a real tab character, not spaces**; Make requires this.

```makefile
INTERP = python3 mylang.py
EXT    = .ml
TESTS  = $(wildcard tests/*$(EXT))
NAMES  = $(basename $(notdir $(TESTS)))

run:
	$(INTERP) $(FILE)

test: $(addprefix test-, $(NAMES))

test-%:
	@echo -n "Testing $*... "
	@diff <($(INTERP) tests/$*$(EXT) 2>&1) expected/$*.txt && echo PASS || echo FAIL

generate-expected:
	@for f in tests/*$(EXT); do \
		name=$$(basename $$f $(EXT)); \
		python3 mylang.py $$f > expected/$$name.txt 2>&1; \
	done

clean:
	find . -name __pycache__ -exec rm -rf {} + 2>/dev/null; true

.PHONY: run test generate-expected clean
```

### Usage

```bash
make run FILE=tests/fibonacci.ml    # run one file
make test                           # run all tests
make generate-expected              # regenerate expected/ directory
make clean                          # remove __pycache__ directories
```

### Makefile concept reference

**`$(wildcard pattern)`**: expands to all files matching `pattern`. Unlike shell globbing, this works inside variable assignments.

**`$(notdir paths)`**: strips the directory prefix from each path in the list. `tests/fibonacci.ml` becomes `fibonacci.ml`.

**`$(basename paths)`**: strips the file extension. `fibonacci.ml` becomes `fibonacci`. Combining with `notdir` gives you bare test names.

**`$(addprefix prefix, list)`**: prepends `prefix` to every word in `list`. `$(addprefix test-, fibonacci sorting)` produces `test-fibonacci test-sorting`.

**Pattern rule `test-%`**: the `%` wildcard matches any string. When make needs to build `test-fibonacci`, it matches this rule with `%` bound to `fibonacci`. Inside the recipe, `$*` expands to the matched stem (`fibonacci`).

**`@` prefix**: suppresses echoing the command itself before running it. Without `@`, make prints each command line before executing it; `@` hides it so your output is cleaner.

**`$<` and `$@`**: `$@` is the target name; `$<` is the first prerequisite. Useful in compilation rules (e.g., compiling `.c` to `.o`) but not needed in this Makefile.

**`.PHONY`**: declares that `run`, `test`, `generate-expected`, and `clean` are not real files. Without this, if a file named `test` existed in the directory, `make test` would do nothing because `test` would appear up to date.

---

> **Try it.** Run `make test`, then `make clean`. Hand the command to a teammate who has never run your project and see whether it works on their machine without further explanation. That is the bar the Makefile has to clear.

---

## Step 5: Build a Debugging Toolkit of One-Liners

### Count lines in your test suite

```bash
wc -l tests/*.ml
```

Shows the line count of every test file plus a total. Useful for a quick sanity check when adding new tests.

### Find all evaluator functions

```bash
grep -rn "def eval_" src/
```

`-r` searches recursively through the `src/` directory. Prints every line matching `def eval_`, with the filename and line number prepended. Replace `src/` with `.` to search the entire project.

### Quick inline REPL

```bash
python3 -c "import mylang; print(mylang.tokenize('1+2'))"
```

`-c` runs a Python expression directly without opening a file. Useful for testing a single function in isolation without writing a scratch file.

### Measure interpreter performance

```bash
time python3 mylang.py tests/fibonacci.ml
```

Prints real (wall-clock), user (CPU), and sys (kernel) time after the program finishes. If your fibonacci test takes more than a second, look for an accidental O(n²) algorithm.

### Syntax-check a module without running it

```bash
python3 -m py_compile lexer.py
```

Parses `lexer.py` and reports any syntax errors, but does not execute the module. Fast way to catch a typo before running the full test suite.

### Step through an interpreter crash with pdb

```bash
python3 -m pdb mylang.py tests/crash.ml
```

Launches Python's built-in debugger. Useful commands inside pdb:

| Command | Effect |
|---------|--------|
| `n` | Execute next line (step over) |
| `s` | Step into a function call |
| `c` | Continue running until the next breakpoint or crash |
| `p expr` | Print the value of `expr` |
| `l` | List source lines around the current position |
| `q` | Quit pdb |

When your interpreter raises an unhandled exception, pdb drops you into a post-mortem prompt exactly at the crashing line. Type `p` followed by any variable to inspect its value.

### Search for a keyword across all test programs

```bash
grep -l "letrec" tests/*.ml
```

`-l` prints only file names, not matching lines. Useful for finding which test cases exercise a particular language feature.

### Show differences between two runs

```bash
diff <(python3 mylang.py tests/scoping.ml) <(python3 mylang_old.py tests/scoping.ml)
```

Both process substitutions run in parallel and their outputs are compared directly. No temporary files needed.

---

> **Try it.** Use `grep -rn` to find every place your evaluator dispatches on a node type. Then run your interpreter on a program that crashes it, under `python3 -m pdb`, and walk to the failing frame. Both are faster than adding print statements, and neither requires an IDE.

---

## Step 6: Configure with Environment Variables and Wire Up CI

Environment variables let you add debug flags to your interpreter without changing any source file or command-line argument parsing.

### Passing a variable for one command

Prefix the assignment directly before the command:

```bash
DEBUG=1 python3 mylang.py tests/scoping.ml
```

The variable `DEBUG` is set to `"1"` for that single invocation only. It does not persist in your shell session after the command finishes.

### Reading env vars in Python

```python
import os
import sys

DEBUG = os.environ.get("DEBUG", "0") == "1"

def eval_expr(expr, env):
    if DEBUG:
        print(f"[eval] {expr}", file=sys.stderr)
    # ... rest of evaluator ...
```

`os.environ.get("DEBUG", "0")` returns the value of the `DEBUG` variable if it is set, or `"0"` if it is not. Comparing to `"1"` gives you a boolean. Writing debug output to `sys.stderr` keeps it separate from program output so your diff-based tests still work correctly.

### Combining multiple flags

```bash
DEBUG=1 TRACE_ENV=1 python3 mylang.py tests/closures.ml
```

```python
DEBUG     = os.environ.get("DEBUG",     "0") == "1"
TRACE_ENV = os.environ.get("TRACE_ENV", "0") == "1"

def lookup(name, env):
    if TRACE_ENV:
        print(f"[env] looking up {name!r} in {list(env.keys())}", file=sys.stderr)
    # ... rest of lookup ...
```

### Exporting variables for the whole session

If you want a flag active for every command in your terminal session, use `export`:

```bash
export DEBUG=1
python3 mylang.py tests/fibonacci.ml   # DEBUG is set
python3 mylang.py tests/scoping.ml     # DEBUG is still set
unset DEBUG                             # remove it when done
```

### Using env vars in your Makefile

```makefile
debug:
	DEBUG=1 $(INTERP) $(FILE)
```

Now `make debug FILE=tests/scoping.ml` runs the interpreter with debug output enabled.

### CI integration with exit codes and env vars

Most CI systems (GitHub Actions, GitLab CI, etc.) treat any non-zero exit code as a build failure. Because `test_runner.sh` exits with `1` when any test fails, you can wire it directly into a CI job:

```yaml
# .github/workflows/test.yml
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: chmod +x test_runner.sh && ./test_runner.sh
```

No additional configuration needed; the exit code from the script tells GitHub whether the job passed or failed.

---

> **Try it.** Add a `DEBUG` check to your interpreter that prints the token stream when `DEBUG=1` is set, and confirm `DEBUG=1 python3 mylang.py tests/scoping.ml` behaves differently from the plain invocation. Then commit the CI workflow and watch the job run on a push, including one push where a test is deliberately broken, so you see it fail.

---

## Quick Reference

| Task | Command |
|------|---------|
| Run interpreter | `python3 mylang.py tests/fib.ml` |
| Capture output | `python3 mylang.py tests/fib.ml > out.txt` |
| Capture stdout + stderr | `python3 mylang.py tests/fib.ml > out.txt 2>&1` |
| Inline diff (no temp file) | `diff expected/fib.txt <(python3 mylang.py tests/fib.ml)` |
| Check last exit code | `echo $?` |
| Run all tests | `./test_runner.sh` or `make test` |
| Regenerate expected output | `make generate-expected` |
| Run with debug flag | `DEBUG=1 python3 mylang.py tests/scoping.ml` |
| Syntax-check a module | `python3 -m py_compile lexer.py` |
| Debug a crash | `python3 -m pdb mylang.py tests/crash.ml` |
| Time a run | `time python3 mylang.py tests/fibonacci.ml` |
| Search for a pattern | `grep -rn "def eval_" src/` |
| Search, extended regex | `grep -rnE "parse_(expr\|term)" src/` |
| Search, whole word only | `grep -rnw "eval" src/` |
| Count matches | `grep -c "TODO" interpreter.py` |
| Print only the match | `grep -rnoE "[A-Z]+_[A-Z]+" lexer.py` |
| List matching files only | `grep -rl "Environment" src/` |
| Invert (lines *without*) | `grep -v "^#" grammar.bnf` |
| Clean caches | `make clean` |

## Appendix: grep in Depth and Capture Groups

The *Regular Expressions* class session keeps a compact grep primer - the flag table and the BRE-vs-ERE trap - because the Overview assignment grades a grep transcript. The longer material below moved here: worked grep examples, named groups, and a full log-triage walkthrough that uses capture groups to turn unstructured log lines into structured records.

### Log Triage: A Capture-Group Walkthrough

**Worked example.** Take one log line and the triage pattern:

```
line:    2026-09-18 08:10:22 WARN disk usage 91%
pattern: (?P<date>\d{4}-\d{2}-\d{2}) (?P<time>\d{2}:\d{2}:\d{2}) (?P<level>[A-Z]+) (?P<msg>.*)
```

The engine walks left to right, and each group records the *span* of text it consumed. Character positions (0-indexed):

```
2026-09-18 08:10:22 WARN disk usage 91%
0.........1.........2.........3........
`--date--+ `-time-+ `lv+ `-----msg----+
```

| Group | Sub-pattern | Text captured | Span (start, end) |
|-------|-------------|---------------|-------------------|
| `date` | `\d{4}-\d{2}-\d{2}` | `2026-09-18` | (0, 10) |
| `time` | `\d{2}:\d{2}:\d{2}` | `08:10:22` | (11, 19) |
| `level` | `[A-Z]+` | `WARN` | (20, 24) |
| `msg` | `.*` | `disk usage 91%` | (25, 39) |

Two details deserve attention. First, `[A-Z]+` is greedy, yet it stops cleanly after `WARN`: the next character is a space, which is not in the class `[A-Z]`, so the quantifier has nothing more it is *allowed* to take: the class boundary does the work, and no backtracking is needed. Second, `.*` in `msg` is also greedy and *does* swallow spaces, running to the end of the line (`.` matches every character except newline).

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

**Check yourself.** In `(?P<level>[A-Z]+) (?P<msg>.*)`, why does the `level` group stop at the end of `WARN`?

<details><summary>Answer</summary>

The next character is a space, which is not in `[A-Z]`, so the greedy `+` has nothing more it is allowed to consume. It is not that `+` is reluctant (it is not), nor that named groups have a length limit (they do not).

</details>

### Critical Thinking Questions

16. Both `[A-Z]+` and `.*` are greedy, yet one stops at a space and the other swallows spaces to the end of the line. State the rule that predicts where any greedy quantifier stops.
17. Suppose a rogue line reads `2026-09-18 08:13:00 warning disk usage 92%` (lowercase level). Trace the pattern against it: which group's sub-pattern fails first, and what does `finditer` do with the line as a whole? Propose the smallest pattern change that would accept both spellings.
18. `m.span(g)` gives each field's exact offsets, and `m.groupdict()` gives a dictionary per line. In two sentences, relate this to your lexer: what plays the role of the token types here, and what plays the role of the token stream?
19. The `msg` group's `.*` would happily match an *empty* message (`.*` matches zero characters). Is that a bug or a feature for log triage? If your team decides empty messages are invalid, what one-character change enforces the decision?

---

This final model has two purposes: to make greedy-versus-reluctant matching concrete so it never surprises you again, and to close the theoretical loop by showing exactly where regular expressions run out of power. Both lessons point to the same underlying cause: a finite automaton has no stack, so it cannot count or remember how deeply it has nested.

> **Watch out!** Regular expressions **cannot match balanced (nested) parentheses** in general: for example, the language $\{(^n)^n \mid n \geq 0\}$ (equal numbers of open and close parens) is context-free, not regular. No matter how clever your regex, there exists a depth $n$ large enough to fool it. When you need to match nested structure, you need a parser built from a context-free grammar, exactly what the next unit covers.

### Named Groups and the Lexer Connection

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

### Critical Thinking Questions

12. The master pattern joins all specs with `|`. Why must multi-character operators like `>=` appear before single-character `>`? What happens to `>=` if you swap their order?
13. The `KEYWORD` pattern uses `\b` word boundaries. What would happen to the identifier `iffy` if keywords were matched without `\b`?
14. The `ERROR` catch-all `.` matches any single character not matched by earlier patterns. Why is this the *last* pattern rather than the first? What role does it play in error reporting?
15. The `SKIP` handler tracks newlines to maintain `line` and `line_start`. Why is accurate line/column tracking valuable for a language learner using your language?

---

Capture groups are what turn a regex from a yes/no detector into a *parser of flat records*: each group carves out one field of the matched text, and named groups label the fields. Nothing exercises this like log triage: the daily chore of turning thousands of text lines into structured data you can count, filter, and sort.

### Character classes and anchors behave as you expect

```bash
grep -nE "^def "        parser.py   # ^ anchors to start of line
grep -nE "return$"      parser.py   # $ anchors to end of line
grep -nE "\bnum\b"      lexer.py    # \b is a word boundary: num, not number
grep -nE "[0-9]+\.[0-9]+" lexer.py   # a float literal; note the escaped dot
grep -nE "[[:alpha:]_][[:alnum:]_]*" lexer.py   # POSIX class = an identifier
```

Two portability notes worth knowing now rather than at 2am: `\d` and `\w` are **not** POSIX and may not work in every `grep`; the portable spellings are `[0-9]` and `[[:alnum:]_]`. And `.` still means "any character," so a literal dot needs escaping: `[0-9]+\.[0-9]+` matches `3.14`, while `[0-9]+.[0-9]+` would also match `3x14`.

**Check yourself.** You run `grep -n "lexer|parser" src/main.py` and get no output, though the file plainly contains both words. What went wrong?

<details><summary>Answer</summary>

Plain `grep` uses BRE, where `|` is a literal character; it searched for the string `lexer|parser`. Use `grep -nE`, or escape it as `lexer\|parser`.

</details>

> **Watch out!** `grep` is line-oriented, so it cannot match a pattern that spans a newline. When you find yourself wanting that ("find every function whose body contains `raise`") you have left `grep`'s regular-language territory and want a parser. That is the same boundary this activity's final section draws between regular expressions and context-free grammars, and it shows up in your tools as well as in your theory.


