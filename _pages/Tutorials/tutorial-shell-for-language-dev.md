---
layout: tutorial
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

This tutorial teaches the shell skills you need to build, test, and ship your CS374 final-project interpreter. You already know Python. This tutorial bridges the gap between "I can run it in my IDE" and "I can run, test, and debug it confidently from the command line."

The examples assume your interpreter is invoked as `python3 mylang.py <sourcefile>`, your source files use the extension `.ml`, test cases live in `tests/`, and expected outputs live in `expected/`. Adapt paths to match your actual layout.

---

## Section 1: Running Your Interpreter from the Terminal

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

### Exit codes — why they matter

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

Exit code `0` means success. Any non-zero code means failure. The shell, CI systems, and your test harness all read this code to decide whether the run passed. If you forget to set it, Python exits with `0` even when your interpreter crashed internally — your test harness will then falsely report every run as a pass.

Check the exit code of the last command with `$?`:

```bash
python3 mylang.py tests/bad_syntax.ml
echo $?          # prints 1 if your interpreter exited with sys.exit(1)
```

---

## Section 2: I/O Redirection for Testing

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

## Section 3: Writing a Shell Test Harness

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

**`for test in tests/*.ml`** — The shell expands the glob `tests/*.ml` into a list of matching file paths before the loop starts. Each iteration assigns one path to the variable `test`.

**`name=$(basename "$test" .ml)`** — `$()` runs a command in a subshell and captures its stdout as a string. `basename` strips the directory prefix and, when given a second argument, also strips that suffix. So `tests/fibonacci.ml` becomes `fibonacci`.

**`actual=$(python3 mylang.py "$test" 2>&1)`** — Runs your interpreter and captures both stdout and stderr into the variable `actual`. The quotes around `"$test"` prevent word-splitting if the filename contains spaces.

**`diff -q <(echo "$actual") "$expected" > /dev/null 2>&1`** — `diff -q` exits with `0` if the files are identical and `1` if they differ, but prints nothing (`-q` is "quiet" mode). We discard any remaining output with `> /dev/null 2>&1`. The condition `[ -f "$expected" ]` guards against test cases that do not yet have a corresponding expected file.

**`((PASS++))`** — Arithmetic in bash uses `(( ))`. This increments the counter.

**`[ $FAIL -eq 0 ]`** — This is the last command in the script, so its exit code becomes the script's exit code. If `FAIL` is zero the condition is true and the script exits `0`. If any tests failed it exits `1`. CI tools pick this up automatically.

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

## Section 4: Makefile for Your Language Project

A `Makefile` gives every contributor — including you after a vacation — a single consistent interface. `make run FILE=tests/fib.ml`, `make test`, `make clean` all just work.

### Complete Makefile

Save this as `Makefile` at the root of your project. **Indented lines must use a real tab character, not spaces** — Make requires this.

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

**`$(wildcard pattern)`** — expands to all files matching `pattern`. Unlike shell globbing, this works inside variable assignments.

**`$(notdir paths)`** — strips the directory prefix from each path in the list. `tests/fibonacci.ml` becomes `fibonacci.ml`.

**`$(basename paths)`** — strips the file extension. `fibonacci.ml` becomes `fibonacci`. Combining with `notdir` gives you bare test names.

**`$(addprefix prefix, list)`** — prepends `prefix` to every word in `list`. `$(addprefix test-, fibonacci sorting)` produces `test-fibonacci test-sorting`.

**Pattern rule `test-%`** — the `%` wildcard matches any string. When make needs to build `test-fibonacci`, it matches this rule with `%` bound to `fibonacci`. Inside the recipe, `$*` expands to the matched stem (`fibonacci`).

**`@` prefix** — suppresses echoing the command itself before running it. Without `@`, make prints each command line before executing it; `@` hides it so your output is cleaner.

**`$<` and `$@`** — `$@` is the target name; `$<` is the first prerequisite. Useful in compilation rules (e.g., compiling `.c` to `.o`) but not needed in this Makefile.

**`.PHONY`** — declares that `run`, `test`, `generate-expected`, and `clean` are not real files. Without this, if a file named `test` existed in the directory, `make test` would do nothing because `test` would appear up to date.

---

## Section 5: Useful Shell One-Liners for Debugging

### Count lines in your test suite

```bash
wc -l tests/*.ml
```

Shows the line count of every test file plus a total. Useful for a quick sanity check when adding new tests.

### Find all evaluator functions

```bash
grep -r "def eval_" src/
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

## Section 6: Environment Variables for Configuration

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

No additional configuration needed — the exit code from the script tells GitHub whether the job passed or failed.

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
| Search for a pattern | `grep -r "def eval_" src/` |
| Clean caches | `make clean` |
