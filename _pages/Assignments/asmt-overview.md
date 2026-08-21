---
layout: assignment
permalink: /Assignments/Overview
title: "CS374: Principles of Programming Languages - Overview"

info:
  coursenum: CS374
  purpose: "To confirm your Python toolchain and capture a baseline of your relationship with languages before the build begins."
  tilt:
    task: "Verify your environment with the starter script and write a short Language Autobiography."
    criteria: "Assessed on a verified environment and a specific, reflective autobiography; see the rubric below for the full breakdown."
  points: 100
  goals:
    - To verify a working Python development environment for the semester's build
    - To demonstrate baseline command-line, git, and Python-environment fluency by navigating a shell, committing to a repository, and creating a reproducible environment with uv
    - To reflect on your language background as a baseline for the course
    - To run the provided starter script that exercises the libraries used throughout the semester
  rubric:
    - weight: 40
      description: Environment Setup and Verification
      preemerging: Little or no evidence that the environment was attempted
      beginning: Some components verified, but the transcript is missing or incomplete, or only one or two of the three verification steps are completed
      progressing: Python environment verified with a complete transcript including version information; the starter script ran but with a minor failure (missing library, wrong Python version) documented with a hypothesis and fix attempt, or the command-line and git checkpoint is incomplete
      proficient: Python 3.10 or later verified; the starter script produces the expected banner; editor/IDE identified; all three verification steps produce transcript evidence; the command-line and git checkpoint (Part 1.5) is complete, showing shell navigation and search, a git commit pushed to a remote, and a uv environment; any failure is documented with error text, hypothesis, and resolution
    - weight: 40
      description: Language Autobiography
      preemerging: The autobiography is missing or does not address any of the four prompts
      beginning: The autobiography addresses some prompts superficially, without specific examples
      progressing: All four prompts are addressed with specific examples drawn from the student's own experience, with limited connection to course themes (parsing, semantics, scoping)
      proficient: All four prompts are addressed with specific examples; the "language fought you" entry uses precise vocabulary (syntax, semantics, type, scope, evaluation order); the reflection question is stated as a genuinely open question, not a question whose answer the student already knows
    - weight: 20
      description: Submission
      preemerging: No submission, or the submission is missing major components
      beginning: The submission is present but disorganized, transcript and autobiography are hard to tell apart, or one is missing
      progressing: All required components are present in one file, with a minor omission such as an unlabeled transcript section
      proficient: A single, well-organized PDF (or Markdown) containing a complete labeled transcript for every verification step and all four autobiography prompts, with the collaboration, AI-disclosure, and time questions answered
  readings:
    - rtitle: "Welcome Activity"
      rlink: "https://www.billmongan.com/Ursinus-CS374-Overview"
    - rtitle: "Thain, Chapter 1"
    - rtitle: "uv: the Python environment manager we standardize on (Part 1.5)"
      rlink: "https://docs.astral.sh/uv/"
    - rtitle: "Setup (Route A): The Course Development Environment - Docker, Git, and GitHub (Tutorial)"
      rlink: "https://www.billmongan.com/Ursinus-CS374-Fall2026/Tutorials/DevEnvironment"
    - rtitle: "Setup (Part 1.5): Shell Skills for Language Development - the step-by-step tutorial article this assignment's shell work follows"
      rlink: "https://www.billmongan.com/Ursinus-CS374-Fall2026/Tutorials/ShellForLanguageDev"

tags:
  - intro
  - languages

---

The purpose of this warmup is to confirm your tools before the build begins and to capture your current relationship with programming languages as a baseline you will revisit at semester end. (Your team charter is **not** part of this assignment; you will draft it with the [Team Language Project]({{ site.baseurl }}/Projects/TeamLanguage) Design-Phase Submission and sign it with the Proposal.)

The Warmup is the Teams-based onboarding survey; the Overview is the technical setup + Language Autobiography; they are separate deliverables.

One pointer before you begin: several assignments this semester offer **directions** (equivalent ways of meeting the same deliverable) and some of those directions build toward live-coded music. If making a language that makes music appeals to you, skim the [Music and Live-Coding guide]({{ site.baseurl }}/Projects/TeamLanguage#the-music-and-live-coding-path) this week. Directions are chosen assignment-by-assignment later, inside each assignment; nothing is committed now.

---

## Part 1: Environment Verification

This course builds a language implementation in Python, incrementally, across six assignments. The final pipeline connects a lexer, parser, AST, environments, and an evaluator; every stage uses `re` (regular expressions), `json` (configuration files), and Python's structural pattern matching (`match`/`case`, available in Python 3.10+). Verify that all three work before the build begins.

Complete this part by **one of two routes**; the transcript requirement at the end applies to whichever you choose.

### Route A (recommended): the course dev container

Set up the course Docker container by following the [Development Environment tutorial]({{ site.baseurl }}/Tutorials/DevEnvironment): one container image with the entire semester's toolchain preinstalled (Python 3.11, pytest, hypothesis, PLY, and flex/bison/gcc/make for the generator-toolchain directions), bind-mounted onto a `cs374-work` GitHub repository you create in the tutorial. Then:

1. Copy `warmup_check.py` (from Step 2 of Route B below) into your `cs374-work` repository.
2. Enter the container and run it **inside the container**: `python3 warmup_check.py`. Include the full transcript (the container prompt, `python3 --version`, and the script's banner output) in your submission.
3. Complete Step 3 of Route B (editor/IDE) as written; VS Code with the Dev Containers extension, opened inside the course container, is the recommended answer and satisfies all three bullets.

Route A students skip Steps 1-2 of Route B on the host: the tutorial's toolchain verification plus the in-container `warmup_check.py` transcript covers them.

### Route B: native install

**Step 1: Confirm Python 3.10 or later.**

```bash
python3 --version
```

If the version is earlier than 3.10, install a newer version or use a virtual environment. On macOS, `brew install python@3.12`; on Windows, download from python.org; on Linux, `sudo apt install python3.12` (Debian/Ubuntu) or equivalent.

**Step 2: Run the starter script.**

Download `warmup_check.py` from the course site (or copy it from below) and run it. It exercises `re`, `json`, and `match`/`case`, and prints a confirmation banner if all three pass. Note: on Windows consoles that garble the yes/no characters, run with `PYTHONIOENCODING=utf-8` or read the True/False values instead.

```python
# warmup_check.py: CS374 environment verification script
# Run with: python3 warmup_check.py

import sys, re, json

EXPECTED_PYTHON = (3, 10)

def check_python_version():
    v = sys.version_info
    ok = (v.major, v.minor) >= EXPECTED_PYTHON
    print(f"[{'✓' if ok else '✗'}] Python {v.major}.{v.minor}.{v.micro}  "
          f"(need >= {EXPECTED_PYTHON[0]}.{EXPECTED_PYTHON[1]})")
    return ok

def check_re():
    # Test: tokenize a tiny expression
    pattern = re.compile(r"(?P<NUM>\d+)|(?P<PLUS>\+)|(?P<WS>\s+)")
    tokens = [(m.lastgroup, m.group()) for m in pattern.finditer("1 + 2")
              if m.lastgroup != "WS"]
    ok = tokens == [("NUM", "1"), ("PLUS", "+"), ("NUM", "2")]
    print(f"[{'✓' if ok else '✗'}] re module: tokenized '1 + 2' -> {tokens}")
    return ok

def check_json():
    data = json.loads('{"language": "Mini", "version": 1, "strict": true}')
    ok = data["language"] == "Mini" and data["version"] == 1
    print(f"[{'✓' if ok else '✗'}] json module: parsed {data}")
    return ok

def check_match_case():
    # Requires Python 3.10+
    def classify(x):
        match x:
            case int(n) if n < 0:  return "negative int"
            case int(n):           return "non-negative int"
            case str(s):           return f"string '{s}'"
            case _:                return "other"
    tests = [(-1, "negative int"), (5, "non-negative int"), ("hi", "string 'hi'")]
    ok = all(classify(v) == expected for v, expected in tests)
    print(f"[{'✓' if ok else '✗'}] match/case: all {len(tests)} structural tests passed")
    return ok

def check_dataclasses():
    from dataclasses import dataclass
    @dataclass
    class Token:
        type: str
        value: str
        line: int = 1
    t = Token("NUM", "42")
    ok = t.type == "NUM" and t.line == 1
    print(f"[{'✓' if ok else '✗'}] dataclasses: Token{t} constructed correctly")
    return ok

results = [
    check_python_version(),
    check_re(),
    check_json(),
    check_match_case(),
    check_dataclasses(),
]

print()
if all(results):
    print("=" * 50)
    print("  CS374 environment verified. ✓")
    print("  You are ready to build a language.")
    print("=" * 50)
else:
    failed = sum(1 for r in results if not r)
    print(f"  {failed} check(s) failed. See above for details.")
    print("  Document each failure verbatim and bring it to class.")
```

**Step 3: Identify your editor or IDE.**

State which editor or IDE you will use for the semester and confirm that you can:
- Open, edit, and save a Python file.
- Run a Python file from within the editor (or from its integrated terminal).
- Set a breakpoint and inspect a variable in the debugger.

Recommended editors: VS Code (with Python extension), PyCharm Community Edition, or any editor you already know. Avoid IDEs that hide the command line entirely; you will need `python3`, `git`, and occasionally `pip` directly.

**Capture a transcript** (copy-paste or screenshot) of all three steps: for Route A, that means the in-container `warmup_check.py` run with `python3 --version`, plus the editor step. If any step fails, document the error text verbatim, your hypothesis about the cause, and what you tried to fix it. A well-documented failure with a follow-up plan earns full credit for that step.

---

## Part 1.5: Command-Line and Git Checkpoint

You will build one language across six assignments, each importing the previous stage's component *unchanged*, all from the terminal and all under version control. This checkpoint confirms those underlying tools work before the pipeline depends on them. You do not need to be a shell expert: you need to navigate, version your work, and create a reproducible environment. The two required-setup tutorials teach all of it, so nothing is repeated here: work through the [Course Development Environment]({{ site.baseurl }}/Tutorials/DevEnvironment) for the container, git identity, and the daily loop, and [Shell Skills for Language Development]({{ site.baseurl }}/Tutorials/ShellForLanguageDev) (a step-by-step article with a *Try it* checkpoint per step) for navigation, `grep`, redirection, and the test harness. The **Command-Line Survival** links below fill any remaining gaps.

**Container-route note (Route A):** perform the git steps of this checkpoint **from inside the course container**, against the `cs374-work` GitHub repository you created in the [Development Environment tutorial]({{ site.baseurl }}/Tutorials/DevEnvironment); the tutorial's practice section (create `hello.py`, run, commit, push) is exactly this checkpoint, so its transcript satisfies the shell-navigation and git items below. The `uv` step still runs on your host (the container image already pins the course packages; `uv` is your reproducible-environment tool for the native route and anywhere outside the container).

Complete each step and capture the terminal output:

1. **Navigate and search.** Create a course directory, enter it, list it, and run one search: `mkdir -p ~/cs374 && cd ~/cs374 && pwd && ls -la`, then use `grep -n` (or `rg`) to find a token in a file and paste the command. Searching text is the daily reality of lexer and parser work, the same regular expressions you will use in the Regex assignment. ([regex101](https://regex101.com/) is your friend there.)
2. **Version control.** Create a git repository, commit a file, and push to a remote (your GitHub Classroom repo or a throwaway GitHub repo): `git init`; add a file; `git add`; `git commit -m "first commit"`; `git remote add origin <url>`; `git push -u origin main`. Paste `git log --oneline`. Your team will live in git during the capstone, so start now.
3. **Reproducible Python with uv.** Install [uv](https://docs.astral.sh/uv/), the fast modern Python environment manager we standardize on this term, and create a project environment: `uv venv`, then `uv run python --version`, then `uv add pytest` (you will write test suites all semester). Paste the output. (If you cannot install uv, fall back to `python -m venv` + `pip`, and note the fallback in your submission.)

### Command-Line Survival: reference (use as needed)

- [tldr pages](https://tldr.sh/): example-first cheat sheets (`tldr grep`).
- [explainshell](https://explainshell.com/): annotates any command line flag by flag.
- [ShellCheck](https://www.shellcheck.net/): lints shell scripts (you will use it in the project's scripting-targets extension).
- [regex101](https://regex101.com/): interactive regex tester, directly useful for the Regex and Lexer assignments.

### Part 1.5 Checklist

- [ ] A shell transcript showing directory creation, navigation, and a `grep`/`rg` search
- [ ] A `git log --oneline` transcript showing at least one commit pushed to a remote
- [ ] A `uv` (or documented fallback) transcript creating an environment and adding `pytest`

---

## Part 2: Language Autobiography

The purpose of this section is to capture your relationship with programming languages at the start of the course, as a baseline you will revisit in your final report. Write approximately one page (400-600 words), addressing all four prompts below.

**Prompt 1: Your language history.**
List every programming language and formal notation you have used: count regex, SQL, spreadsheets, HTML, configuration languages, shell scripts. For each, write one sentence explaining what it was good at, from your perspective as a user. Do not worry about precision; candid impressions count more than textbook accuracy here.

*Example opening:* "Python (four years): excellent for data exploration because the REPL makes it easy to try ideas without a compile step. SQL (one semester): surprisingly good at expressing 'find all rows where' queries, but I found joins hard to visualize..."

**Prompt 2: A moment the language fought you.**
Describe one specific moment when a language was harder to use than you expected: something you wanted to express that the language made difficult, surprising, or impossible. Be concrete: name the language, the construct you were trying to write, and what the language made you do instead.

*What to aim for:* an answer that uses at least one of these words precisely: syntax, semantics, type, scope, evaluation order, binding. You do not need to know all these words yet; use the ones you know and leave placeholders for the ones you don't.

**Prompt 3: A moment of elegance.**
Describe one feature of any language (or of a language feature you read about) that felt elegant the first time you understood it. "Elegant" can mean surprisingly concise, surprisingly general, or surprisingly consistent.

**Prompt 4: An open question.**
Pose one question about how programming languages work that you hope this course will answer. The best questions are ones you genuinely do not know the answer to, not questions whose answer you can look up in Wikipedia.

*Examples of good questions:* "Why does Python have both `is` and `==`, and what is actually different between them at the implementation level?" "How does a compiler know which variables a closure needs to capture?" "Is there a way to guarantee that a recursion terminates without running it?"

---

## Deliverables

Submit a **single PDF** (preferred) or Markdown file containing:
1. The verification transcript for all three environment steps.
2. The command-line and git checkpoint transcript (Part 1.5: navigation/search, git commit/push, uv environment).
3. The language autobiography (all four prompts, approximately one page).

Please also answer the following questions in your submission:

- If collaboration with a buddy was permitted, did you work with a buddy on this assignment? If so, who? If not, do you certify that this submission represents your own original work? Please identify any and all portions of your submission that were not originally written by you.
- AI disclosure: list any generative-AI tools you used, for what, and how you verified the results (or state 'none').
- Approximately how many hours it took you to finish this assignment (I will not judge you for this at all; I am simply using it to gauge if the assignments are too easy or hard).
