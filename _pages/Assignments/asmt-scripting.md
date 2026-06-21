---
layout: assignment
permalink: /Assignments/Scripting
title: "CS374: Principles of Programming Languages - Shell Scripting"

info:
  coursenum: CS374
  points: 100
  goals:
    - To write correct shell scripts using variables, conditionals, loops, and functions
    - To chain Unix commands into pipelines using pipes and redirection
    - To process text files using sed, awk, grep, and sort
    - To understand how scripting languages expose OS services and compose programs

  rubric:
    - weight: 25
      description: Variables, Control Flow, and Functions
      preemerging: Scripts fail to run due to syntax errors, or the shebang line is missing; variable usage is incorrect (unquoted, or $ missing)
      beginning: Most scripts run but one or more control-flow constructs are wrong — e.g., the for-loop iterates over the wrong set, the if-test uses = instead of ==, or a function is defined but never called
      progressing: All control-flow constructs work correctly, but quoting is inconsistent (e.g., unquoted variables that would break on filenames with spaces), or the function for argument validation is missing
      proficient: All scripts run correctly with proper quoting throughout; variables are consistently declared with `local` inside functions; the argument-validation function rejects bad inputs with an informative error message and non-zero exit code; edge cases (empty list, zero, negative numbers) all produce the correct output
    - weight: 25
      description: Pipelines and I/O Redirection
      preemerging: Pipelines are not used; instead, intermediate files are written and read manually, or commands are chained with semicolons rather than pipes
      beginning: Most pipelines run but produce incorrect output — e.g., sort order is wrong, uniq is applied before sort, or grep pattern is unanchored and produces false positives
      progressing: All pipelines produce correct output for the provided inputs, but the scripts are not portable — they use GNU-only flags (e.g., grep -P without checking availability) or hard-coded absolute paths
      proficient: All pipelines produce correct output; the scripts handle edge cases (empty input, files with no newlines); commands are composed correctly with |, >, >>, and 2> where appropriate; the word-frequency pipeline uses at least four chained commands and is accompanied by a step-by-step annotation explaining what each stage does
    - weight: 25
      description: Text Processing with grep/sed/awk
      preemerging: The text-processing tasks are solved with Python or another non-shell tool, rather than the required commands
      beginning: Some grep/sed/awk tasks run but produce partially correct output — e.g., sed replaces only the first occurrence per line (missing /g), or the awk field index is off by one
      progressing: All text-processing tasks produce correct output for the provided test files, but the patterns are brittle — e.g., the email regex matches strings that are not valid emails, or the log-parser awk script assumes a fixed column count that breaks on multi-word fields
      proficient: All tasks produce correct output; regular expressions are anchored appropriately (^ and $ where needed); the awk log-parser handles multi-word fields using FS or a field separator; error lines are separated from normal lines using stderr redirection; the solution is tested against at least two additional self-constructed test cases
    - weight: 25
      description: Script Composition and Portability
      preemerging: Scripts are written as monolithic blobs with no functions; there is no Makefile or driver script that ties the parts together
      beginning: Some functions are factored out but they do not use parameters — they rely on global variables instead; the driver script runs the tasks but does not check exit codes
      progressing: Functions use parameters, return appropriate exit codes, and are tested in isolation; the driver script checks exit codes but does not print a summary of pass/fail results
      proficient: All scripts are composed of well-named functions with parameters and exit codes; the driver script runs all tasks, checks each exit code, prints a colored pass/fail line for each, and exits with a non-zero code if any task failed; the scripts pass shellcheck with no errors; a README explains how to run the suite

  readings:
    - rtitle: "Programming Paradigms Activity"
      rlink: "https://liascript.github.io/course/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374-Fall2026/gh-pages/_pages/Activities/liascript-paradigms.md"
    - rtitle: "Bash Syntax Reference"
      rlink: "https://tiswww.case.edu/php/chet/bash/bashref.html"
    - rtitle: "Bash Scripting Tutorial for Beginners"
      rlink: "https://linuxconfig.org/bash-scripting-tutorial-for-beginners"

tags:
  - scripting
  - bash
  - shell
  - pipelines
  - text-processing

---

This assignment develops fluency in shell scripting as a programming paradigm. Bash scripts compose Unix programs through pipes and redirection, treating the OS itself as a library of callable functions. The constraints here are the content: use the shell's built-in constructs rather than reaching for Python.

---

## Background: The Scripting Paradigm

A scripting language lives close to its host environment. In Bash, every command is a program; every pipe connects two programs via stdout/stdin; every `$()` captures a program's output as a string. This composition model — small programs wired together — is a distinct paradigm with its own strengths (leverage existing Unix tools) and weaknesses (string-only data model, whitespace fragility).

---

## Part 1: Variables, Control Flow, and Functions (25 points)

### Step 1a: Number Utilities

Write a script `numbers.sh` that defines the following Bash functions:

**`is_even n`** — prints `even` if `n` is even, `odd` otherwise. Use `$(( n % 2 ))`.

**`sum_to n`** — prints the sum of integers 1 through n using a `for` loop.

**`factorial n`** — prints n! using a `while` loop. Handle `n=0` (result is 1).

**`fizzbuzz n`** — prints the classic FizzBuzz sequence from 1 to n: print "Fizz" for multiples of 3, "Buzz" for multiples of 5, "FizzBuzz" for both, the number otherwise.

After defining the functions, your script must call each one with at least three different arguments and print the results.

```bash
#!/usr/bin/env bash
set -euo pipefail

is_even() {
    local n=$1
    if (( n % 2 == 0 )); then
        echo "even"
    else
        echo "odd"
    fi
}

# ... (implement the rest)

is_even 4   # even
is_even 7   # odd
sum_to 10   # 55
factorial 5 # 120
fizzbuzz 15
```

### Step 1b: Array Operations

**`array_max arr`** — takes array elements as arguments (`"${@}"`), prints the maximum.

**`array_sum arr`** — prints the sum of all arguments.

**`array_contains val arr`** — prints `yes` if `val` appears in the remaining arguments, `no` otherwise.

```bash
array_max 3 1 4 1 5 9 2 6    # 9
array_sum 1 2 3 4 5           # 15
array_contains 4 1 2 3 4 5   # yes
array_contains 7 1 2 3 4 5   # no
```

### Step 1c: Argument Validation

Write a function `require_int name value` that checks whether `value` is an integer. If not, it should print an error message to stderr (`>&2`) and `exit 1`. Use this function to validate all inputs to the functions above.

```bash
require_int "n" "abc"   # prints error to stderr, exits with code 1
require_int "n" "42"    # succeeds silently
```

**Test:** Run `bash numbers.sh abc` and confirm you get a non-zero exit code: `echo $?`.

---

## Part 2: Pipelines and I/O Redirection (25 points)

### Step 2a: Word Frequency Pipeline

Create a file `words.txt` with at least 30 words (you choose the content — a paragraph of prose works well). Write a one-line pipeline that prints the 10 most frequent words in descending order of frequency:

```bash
cat words.txt | tr -s '[:space:]' '\n' | tr '[:upper:]' '[:lower:]' | \
    sed "s/[^a-z]//g" | grep -v '^$' | sort | uniq -c | \
    sort -rn | head -10
```

Save this pipeline in `wordfreq.sh`. Add a comment above each `|` stage explaining what that stage does. The output format should be:
```
   7 the
   5 and
   ...
```

### Step 2b: File Statistics

Write `filestats.sh` that accepts a directory path as `$1` and prints:
- Total number of files (not directories) in the directory tree
- Total size in bytes (use `du` or `wc`)
- Name of the largest file
- Number of files grouped by extension (`.py`, `.md`, `.txt`, etc.)

```bash
#!/usr/bin/env bash
set -euo pipefail

DIR="${1:-.}"  # default to current directory

echo "=== File Statistics for $DIR ==="
echo "Total files: $(find "$DIR" -type f | wc -l)"
echo "Largest file: $(find "$DIR" -type f -exec du -b {} + | sort -rn | head -1 | awk '{print $2}')"
echo ""
echo "Files by extension:"
find "$DIR" -type f | grep -oP '\.[^.]+$' | sort | uniq -c | sort -rn
```

Extend this script to also redirect error messages (from files you can't read) to `errors.log` using `2>errors.log`.

### Step 2c: Process Substitution

Demonstrate process substitution (`<()`) by comparing two sorted versions of a file:

```bash
# Compare two commands' outputs without temporary files
diff <(sort file1.txt) <(sort file2.txt)
```

Create `compare.sh` that takes two file paths and prints lines that appear in the first file but not the second, and lines in the second but not the first (set difference). Use `diff` and process substitution.

---

## Part 3: Text Processing with grep, sed, and awk (25 points)

### Step 3a: grep — Pattern Matching

Create `patterns.sh`. For each task, write a single `grep` command (with any needed flags):

1. Find all lines in a text file that contain an email address (pattern: `word@word.word`)
2. Find all lines that contain a number with exactly 4 digits
3. Find all Python function definitions (lines starting with `def `)
4. Count how many blank lines are in a file (`-c` flag)
5. Find all TODO comments in a directory of `.py` files, printing filename and line number (`-rn`)

Test each with a file you create. Show the command and its output.

### Step 3b: sed — Stream Editing

Create `transform.sh`. For each task, write a single `sed` command:

1. Replace all occurrences of `colour` with `color` in a file (global replace)
2. Delete all blank lines from a file
3. Add a `#` comment character to the beginning of every line
4. Print only lines 5 through 10 of a file (`-n '5,10p'`)
5. Swap the first and second comma-separated fields on each line (e.g., `Alice,Smith` → `Smith,Alice`)

### Step 3c: awk — Field-Based Processing

Create a log file `access.log` with the Apache common log format:
```
127.0.0.1 - frank [10/Oct/2000:13:55:36 -0700] "GET /index.html HTTP/1.0" 200 2326
127.0.0.1 - mary [10/Oct/2000:13:56:00 -0700] "GET /page.html HTTP/1.0" 404 512
10.0.0.1  - bob  [10/Oct/2000:14:01:00 -0700] "POST /submit HTTP/1.1" 200 1024
```
Add at least 10 more lines with varied IPs, users, status codes, and byte counts.

Write `logparse.sh` with awk scripts for:
1. Print the IP address and status code for every request
2. Count requests per unique IP address
3. Print only 404 errors with their URLs
4. Compute the total bytes transferred (sum of the last field)
5. Print the top 3 most-requested URLs (combine awk with sort/uniq)

---

## Part 4: Script Composition and Portability (25 points)

### Step 4a: A Reusable Library

Create `lib.sh` containing reusable functions that can be sourced by other scripts:

```bash
#!/usr/bin/env bash
# lib.sh — reusable utility functions

log_info()  { echo "[INFO]  $*" >&2; }
log_warn()  { echo "[WARN]  $*" >&2; }
log_error() { echo "[ERROR] $*" >&2; }

die() {
    log_error "$1"
    exit "${2:-1}"
}

require_command() {
    command -v "$1" >/dev/null 2>&1 || die "Required command not found: $1"
}

require_file() {
    [[ -f "$1" ]] || die "Required file not found: $1"
}

require_dir() {
    [[ -d "$1" ]] || die "Required directory not found: $1"
}
```

Add at least three more utility functions of your choice (suggestions: `confirm_yn`, `trim_whitespace`, `url_encode`).

### Step 4b: A Driver Script

Create `run_all.sh` that sources `lib.sh` and runs each of your earlier scripts as a test case:

```bash
#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "$0")/lib.sh"

PASS=0
FAIL=0

run_test() {
    local name="$1"
    shift
    if "$@" >/dev/null 2>&1; then
        echo -e "\033[32mPASS\033[0m $name"
        (( PASS++ )) || true
    else
        echo -e "\033[31mFAIL\033[0m $name (exit code $?)"
        (( FAIL++ )) || true
    fi
}

run_test "is_even 4"       bash numbers.sh even_test
run_test "sum_to 10"       bash numbers.sh sum_test
run_test "wordfreq"        bash wordfreq.sh
run_test "logparse 404s"   bash logparse.sh 404
# Add tests for each part

echo ""
echo "Results: $PASS passed, $FAIL failed"
[[ $FAIL -eq 0 ]]  # exit 0 if all passed, 1 otherwise
```

Adapt the test invocations to match how your scripts actually work.

### Step 4c: shellcheck

Install and run `shellcheck` on all your scripts:

```bash
shellcheck numbers.sh wordfreq.sh filestats.sh compare.sh \
           patterns.sh transform.sh logparse.sh lib.sh run_all.sh
```

Fix all warnings. Common issues shellcheck catches:
- Unquoted variables: `$var` → `"$var"`
- `[ ]` vs `[[ ]]` usage
- `local` declarations in functions
- Useless cat (anti-pattern)

Include the `shellcheck` output (showing no errors) in your submission.

---

## Deliverables

Submit a ZIP containing:
- `numbers.sh` — Part 1a/1b/1c
- `wordfreq.sh` — Part 2a with annotated pipeline
- `filestats.sh` — Part 2b
- `compare.sh` — Part 2c
- `patterns.sh` — Part 3a
- `transform.sh` — Part 3b
- `logparse.sh` — Part 3c
- `lib.sh` — Part 4a
- `run_all.sh` — Part 4b
- `words.txt`, `access.log` — test data files
- `shellcheck_output.txt` — clean shellcheck run
- `readme.md` — approximately one page: describe one surprise you encountered about how Bash handles types or quoting, and explain how the scripting paradigm differs from the functional paradigm explored in the Functional Programming assignment

---

## Grading Breakdown

| Component | Points |
|-----------|--------|
| Part 1: Variables, Control Flow, Functions | 25 |
| Part 2: Pipelines and I/O Redirection | 25 |
| Part 3: Text Processing (grep/sed/awk) | 25 |
| Part 4: Composition and Portability | 25 |
| **Total** | **100** |

---

## Reflection Prompts

- Shell scripts treat everything as strings, while Python has a rich type system. What are the practical consequences of the "everything is a string" model? Give one example where it helped and one where it hurt you in this assignment.
- Bash functions don't return values — they print to stdout and communicate status via exit codes. How does this compare to a language with explicit return types? What design pattern does it enable (hint: think about pipelines)?
- You used `grep`, `sed`, and `awk` — three separate tools each with its own language. How does this compare to having one unified text-processing language? What is the Unix philosophy argument for the multi-tool approach?
- If collaboration with a buddy was permitted, did you work with a buddy on this assignment? If so, who? If not, do you certify that this submission represents your own original work? Please identify any and all portions of your submission that were not originally written by you.
- Approximately how many hours it took you to finish this assignment?
