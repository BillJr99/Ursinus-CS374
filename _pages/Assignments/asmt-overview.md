---
layout: assignment
permalink: /Assignments/Overview
title: "CS374: Principles of Programming Languages - Overview"

info:
  coursenum: CS374
  purpose: "To confirm your Python toolchain, judge two languages you already use against the course's evaluation criteria, and capture a baseline of your relationship with languages before the build begins."
  tilt:
    task: "Argue readability and writability tradeoffs in two languages you already know and translate a snippet across paradigms, verify your environment with the starter script, and write a short Language Autobiography."
    criteria: "I assess your work on a defended pair of language judgments and an honest paradigm translation, a verified environment, and a specific, reflective autobiography.  The rubric below has the details."
  points: 100
  goals:
    - To turn the reading's evaluation criteria into judgments you can defend about languages you already use
    - To classify a snippet's paradigm and name what it costs to translate it into another
    - To verify a working Python development environment for the semester's build
    - To demonstrate baseline command-line, git, and Python-environment fluency by navigating a shell, authenticating to GitHub with an SSH key, cloning and committing to a repository, and creating a reproducible environment with uv
    - To reflect on your language background as a baseline for the course
    - To run the provided starter script that exercises the libraries used throughout the semester
  rubric:
    - weight: 10
      description: "Part 0: Evaluating Languages and Paradigms"
      preemerging: Neither the language comparison nor the paradigm translation is attempted
      beginning: Two languages are named and a snippet is classified, but the claims are asserted without a design choice pointed to in either language
      progressing: Each language is tied to a specific design choice and the snippet is translated, but the write-up does not say what the translation cost, or does not commit to which criterion you value more
      proficient: Each of the two languages is tied to a named design choice that makes it more readable or more writable; the paradigm of the snippet is classified and it is translated (or the write-up argues concretely why it cannot be); the translation cost is named; and you say which criterion you would give up and why
    - weight: 36
      description: Environment Setup and Verification
      preemerging: Little or no evidence that the environment was attempted
      beginning: Some components verified, but the transcript is missing or incomplete, or only one or two of the three verification steps are completed
      progressing: Python environment verified with a complete transcript including version information; the starter script ran but with a minor failure (missing library, wrong Python version) documented with a hypothesis and fix attempt, or the command-line and git checkpoint is incomplete
      proficient: Python 3.10 or later verified; the starter script produces the expected banner; editor/IDE identified; all three verification steps produce transcript evidence; the command-line and git checkpoint (Part 1.5) is complete, showing shell navigation and search, an SSH key registered with GitHub and verified with `ssh -T`, a git commit pushed to a remote over SSH, and a uv environment; any failure is documented with error text, hypothesis, and resolution
    - weight: 36
      description: Language Autobiography
      preemerging: The autobiography is missing or does not address any of the four prompts
      beginning: The autobiography addresses some prompts superficially, without specific examples
      progressing: All four prompts are addressed with specific examples drawn from the student's own experience, with limited connection to course themes (parsing, semantics, scoping)
      proficient: All four prompts are addressed with specific examples; the "language fought you" entry uses precise vocabulary (syntax, semantics, type, scope, evaluation order); the reflection question is stated as an open question, not a question whose answer the student already knows
    - weight: 18
      description: Submission
      preemerging: No submission, or the submission is missing major components
      beginning: The submission is present but disorganized, transcript and autobiography are hard to tell apart, or one is missing
      progressing: All required components are present in one file, with a minor omission such as an unlabeled transcript section
      proficient: A single, well-organized PDF (or Markdown) containing a complete labeled transcript for every verification step and all four autobiography prompts, with the collaboration and time questions answered
  readings:
    - rtitle: "Welcome Activity"
      rlink: "https://www.billmongan.com/Ursinus-CS374-Overview"
    - rtitle: "Thain, Chapter 1"
    - rtitle: "uv: the Python environment manager we standardize on (Part 1.5)"
      rlink: "https://docs.astral.sh/uv/"
    - rtitle: "Setup (Route A): The Course Development Environment - Docker, Git, and GitHub (Tutorial)"
      rlink: "../Tutorials/DevEnvironment"
    - rtitle: "Setup (Part 1.5): Shell Skills for Language Development, the step-by-step tutorial article this assignment's shell work follows"
      rlink: "../Tutorials/ShellForLanguageDev"
    - rtitle: "GitHub: Connecting to GitHub with SSH (generate a key, add it to your account, and test it)"
      rlink: "https://docs.github.com/en/authentication/connecting-to-github-with-ssh"

tags:
  - intro
  - languages

---
Welcome to CS374!  This warmup has two jobs: to confirm your tools before the build begins, and to capture your current relationship with programming languages as a baseline you'll come back to at the end of the semester.

One pointer before you begin.  Several assignments this semester offer **directions**, which are equivalent ways of meeting the same deliverable, and some of those directions build toward live-coded music.  If a language that makes music appeals to you, please skim the [Music and Live-Coding guide]({{ site.baseurl }}/Projects/TeamLanguage#the-music-and-live-coding-path) this week.  You choose directions later, inside each assignment, so nothing is committed now.

---

## Start Here: What This Assignment Covers

This assignment is nine stages.  Each stage ends with one command whose output you paste into your submission, so you can always tell whether a stage is done.  Work down the table in order, and use the last column to find the steps.

| Stage | What you do | The command that proves it | What you paste | Where to find the steps |
|---|---|---|---|---|
| 0 | Judge two languages and translate a snippet, with a pencil | none | Your two judgments and the translation, under a `Part 0` heading | Part 0 |
| 1 | Open a terminal, learn to move around and save a file, and confirm Python 3.10 or later, installing Python and pip if you have to | `python3 --version` | The version line, and the pip version line if you installed Python here | Part 1, *Terminal Basics*, Step 1, and *Installing Python and pip* |
| 2 | Save and run the starter script | `python3 warmup_check.py` | The script's banner, and the container prompt if you ran it there | Part 1, Step 2 |
| 3 | Name your editor and prove it can run and debug a file | none | One sentence per bullet | Part 1, Step 3 |
| 4 | Navigate a shell and search a file | `grep -n "let" sample.txt` | The commands and their output | Part 1.5, Step 1 |
| 5 | Authenticate to GitHub with an SSH key | `ssh -T git@github.com` | The greeting that names your username | Part 1.5, Step 2 |
| 6 | Clone or create a repository, then commit and push | `git log --oneline` | The log showing a pushed commit | Part 1.5, Step 3 |
| 7 | Create a reproducible Python environment | `uv run python --version` | The output of the uv commands | Part 1.5, Step 4 |
| 8 | Write the Language Autobiography | none | Four labeled prompts, about a page | Part 2 |

### Three things to know before you begin

- **Do the stages in this order.**  Stage 0 comes first, and it needs no computer.  Stages 1 through 3 are the environment; Stages 4 through 7 use that environment; Stage 8 needs no tools and can be written while anything downloads.
- **If a stage fails, document it and move on.**  A documented failure earns full credit for that stage: quote the error verbatim, state your hypothesis about the cause, and say what you tried.  Work down the Troubleshooting table at the end of this page before you post in the course channel.
- **You need:** a laptop you can install software on, a GitHub account, and a few gigabytes of free disk.  If any of those is a problem, say so this week rather than in week four.

---

## Part 0: Thinking About Languages You Already Know

> **In this part:** Stage 0 of the map.  You will make two judgments about languages you already use, and translate a small snippet from one paradigm into another.  No computer needed.

Do this one **first**, before the rest of the assignment.  It takes about fifteen minutes and a pencil, and it is the only part of this assignment that has nothing to do with your toolchain.

Readability and writability are easy words to nod at and hard to use well.  They only get sharp when you point them at code you have actually written, in languages you have actually argued about.

### 1. Two languages you already know

Pick two.  Write **one sentence each** naming a specific *design choice* that makes one of them more **readable** and the other more **writable**.  A design choice is something concrete: significant whitespace, mandatory type annotations, operator overloading, list comprehensions, semicolons, `null`.  It is not a mood.

Then say which of the two criteria you would give up if you had to, and why.

### 2. A snippet across paradigms

Take about five lines of code in any language and classify the paradigm it primarily represents (imperative, object-oriented, functional, declarative).  Then rewrite it in a *different* paradigm, and name what the translation cost you: lines, clarity, performance, or something you could no longer express at all.

If you cannot finish the translation, that is a real answer and it earns full credit, as long as you say precisely where it broke and why.  An argument you could not finish is more useful to me than a clean page.

**What to bring to class:** the sticking point.  The translation that stalled, or the design choice you could not call good or bad.  That is what we start from.

> **Paste into your submission:** both parts, under a heading `Part 0`.

---

## Part 1: Getting Your Python Toolchain Working

> **In this part:** Stages 1 to 3 of the map.  You will pick a route, learn (or refresh) a few terminal basics, check your Python version, run the starter script, and name the editor you'll use all semester.

This course builds a language implementation in Python, incrementally, across six assignments.  The final pipeline connects a lexer, parser, AST, environments, and an evaluator; every stage uses `re` (regular expressions), `json` (configuration files), and Python's structural pattern matching (`match`/`case`, available in Python 3.10+).  Verify that all three work before the build begins.

### Which route should I take?

A route decides *where* the three steps of this part run.  The steps are the same on both routes.

| | Route A (recommended): the course dev container | Route B: native install |
|---|---|---|
| Who it is for | Anyone whose laptop can run Docker Desktop | Anyone whose laptop cannot run Docker |
| What you install | Docker Desktop and the course container, by following the [Development Environment tutorial]({{ site.baseurl }}/Tutorials/DevEnvironment) through its Step 4 | Python 3.10 or later, with pip (see *Installing Python and pip* under Step 1) |
| Where Step 2 runs | Inside the container, at the `student@...:/workspace$` prompt | In your own terminal |
| What you skip | Nothing; the tutorial's Step 4 toolchain checks go in your transcript as well | The tutorial |

**You do not have to decide yet.**  Step 1 is identical on both routes: if `python3 --version` on your own machine says 3.10 or later, Route B already works.

Route A is still the one I recommend, because the container carries the entire semester's toolchain (Python 3.11, pytest, hypothesis, PLY, `uv`, a Scheme for the functional programming assignment, and flex/bison/gcc/make for the generator-toolchain directions) and every later assignment assumes it.

Decide at Step 2: if Docker Desktop installs and the tutorial's `docker run hello-world` succeeds, run Step 2 inside the container; if Docker will not run on your machine, run it natively and say so in your transcript.

### Terminal Basics: Opening One, Moving Around, and Saving a File

Every step on this page happens at a terminal, and several ask you to save a file.  Here is how, on every system this course supports.  Come back to this section whenever a step says "open a terminal," "`cd`," or "save it."

#### Opening a terminal

| System | How to open it | What the prompt looks like |
|---|---|---|
| macOS | Press Cmd+Space, type `Terminal`, press Enter (Terminal also lives in **Applications > Utilities**) | `you@laptop ~ %` |
| Windows, PowerShell | Open the Start menu, type `PowerShell`, press Enter (not "Command Prompt").  On Windows 11, right-clicking the Start button and choosing **Terminal** opens PowerShell too | `PS C:\Users\you>` |
| Windows, WSL2 Ubuntu | Open the Start menu, type `Ubuntu`, press Enter (Step 1 of the Development Environment tutorial installs it) | `you@laptop:~$` |
| Linux | Press Ctrl+Alt+T, or open Terminal from the applications menu | `you@laptop:~$` |
| VS Code, on any system | Press Ctrl+` (backtick), or **View > Terminal**.  It opens in the folder you have open | one of the above |
| The course container | `docker compose run --rm cs374` from `cs374-work/.devcontainer/`, or **Reopen in Container** in VS Code | `student@a1b2c3d4e5f6:/workspace$` |

#### Printing where you are, and moving around

The terminal always has a current folder, and every relative path is measured from it.  These commands work the same in every shell above, including PowerShell:

```bash
pwd               # print the folder you are in
ls                # list what is here (ls -la also shows hidden files; in PowerShell, plain ls)
cd ~              # go to your home folder
mkdir -p ~/cs374  # make a folder for this course (in PowerShell: mkdir ~/cs374)
cd ~/cs374        # go into it
cd ..             # go up one level
```

`~` is your home folder: `/Users/you` on macOS, `C:\Users\you` in PowerShell, and `/home/you` in WSL2 Ubuntu.  From WSL2, your Windows files are under `/mnt/c/Users/you`.  `~` does *not* work in the old Windows Command Prompt, which is one reason to use PowerShell or Ubuntu instead.

Do all of this course's work in `~/cs374`, or in the `cs374-work` clone from the tutorial on Route A, so that every `cd ~/cs374` on this page lands in the same place.

Two habits worth building right away: press **Tab** to complete a name you have started typing, and press the up arrow to recall the previous command.

#### Saving a file

When a step says "save this as `warmup_check.py`," first `cd` into the folder the file belongs in, then use one of these:

- **nano**, on macOS, Linux, WSL2, and inside the course container.  Run `nano warmup_check.py`, paste the contents (Cmd+V on macOS; right-click or Ctrl+Shift+V in Ubuntu), press **Ctrl+O** then **Enter** to write the file, then **Ctrl+X** to exit.
- **vim**, present on every Unix system.  Run `vim warmup_check.py`, press **i** to enter insert mode, paste, press **Esc**, then type `:wq` and press **Enter** to write and quit.  If you get stuck, press **Esc**, type `:q!`, and press **Enter** to leave without saving.
- **VS Code**, on any system.  From the folder, run `code .` to open it (or **File > Open Folder**), then **File > New File**, paste, and press **Ctrl+S** (Cmd+S on macOS) to save under the name the step gives.  Type the name with its extension, `warmup_check.py`, and check that the editor did not add `.txt`.
- **PowerShell without nano.**  Run `notepad warmup_check.py`, click **Yes** to create the file, paste, save, and close Notepad.  For a one-line file, `Set-Content sample.txt "let x = 1;"` writes it directly.

#### Checking that the file landed where you meant it to

Run `ls` and see the file's name; run `cat warmup_check.py` and see its contents.  If `ls` does not show it, you saved into a different folder than the one you are in, and `pwd` tells you which one that is.

With those basics in hand, here are the three verification steps.

### Step 1: Checking your Python version

**Do this.**  Open a terminal and run:

```bash
python3 --version
```

On Windows in PowerShell, the command is `python --version`, since Windows Python installs as `python`.

**What you should see.**  `Python 3.10.x` or later.  Inside the course container, `Python 3.11.x`.

> **Paste into your submission:** the version line, and the `python3 -m pip --version` line as well if you installed Python in the next section.

**If it goes wrong.**  `command not found` on Windows usually means you typed `python3` where PowerShell wants `python`.  If the command is genuinely missing, or the version is earlier than 3.10, install a current Python by following *Installing Python and pip* just below, then rerun this step in a new terminal.  On Route A this can only happen on your host; the container's Python is 3.11 and needs nothing.

#### Installing Python and pip

Only do this section if Step 1 came up short.  It applies to Route B, and to Route A only for what runs on your host: the `uv` step in Part 1.5 (which brings its own Python) and the `python -m venv` fallback there (which does not).

**Do this.**  Check both halves first, Python and its package installer, pip:

```bash
python3 --version
python3 -m pip --version
```

In PowerShell, spell them `python --version` and `python -m pip --version`.  If both print a version and the first is 3.10 or later, skip to Step 2.  Otherwise, install Python for your system from the row below.  Install **3.11 or later** to match the container; 3.10 is the hard floor, because the starter script and the whole build use `match`/`case`.  Every row brings pip with it.

| System | How to install Python (pip comes with it) | Then |
|---|---|---|
| **macOS, with Homebrew** | `brew install python@3.12`.  If you do not have [Homebrew](https://brew.sh/), install it first with the one-line command on its home page; it is also the easiest way to install uv in Part 1.5 | Open a new terminal window |
| **macOS, without Homebrew** | Download the macOS installer from [python.org/downloads](https://www.python.org/downloads/) and run it | Open a new terminal window |
| **Windows, PowerShell** | Download the Windows installer from [python.org/downloads](https://www.python.org/downloads/), run it, and on its first screen check the box that adds Python to `PATH` before you click **Install Now**.  Or, in PowerShell, `winget install --id Python.Python.3.12 -e` | Open a new PowerShell window, so the updated `PATH` loads |
| **WSL2 Ubuntu, or Linux** | `sudo apt update && sudo apt install python3 python3-pip python3-venv`.  Ubuntu ships Python 3 but not pip or `venv`, which is why all three packages are named.  If that Python is older than 3.10, `sudo apt install python3.12` adds a newer one alongside it, invoked as `python3.12` | Nothing; the commands work in the same window |

> **What pip is, and why every pip command on this page starts with `python3 -m`.**  pip is Python's package installer, the tool that fetches libraries such as `pytest` from the [Python Package Index](https://pypi.org/) and puts them where `import` can find them.  It has shipped inside Python since version 3.4, so installing Python installs pip.  A machine can hold several Pythons, though (Apple's developer tools add one, Homebrew adds another, and each `uv` environment has its own), and a bare `pip install` may target a different one than the `python3` you run scripts with.  `python3 -m pip install pytest` runs pip *from inside* the Python you name, so the library lands where that Python will look for it.  That is the entire reason the page writes it this way.  Natively, pip also belongs inside a *virtual environment*, a per-project copy of the library folder; the pip row of the table in Part 1.5, Step 4 shows how to make and activate one, and every native `pip install` on this page assumes you have.

**What you should see.**  In a new terminal, `python3 --version` prints `Python 3.12.x` (or whatever you installed), and `python3 -m pip --version` prints a pip version followed by the path of the Python it belongs to.  Check that the path points at the Python you just installed.

> **Paste into your submission:** both version lines, with your Step 1 transcript.

**If it goes wrong.**  `python3: command not found` (or `'python' is not recognized`) right after installing means the terminal predates the install; open a new one.  On Windows, if typing `python` opens the Microsoft Store, Python is not installed yet: close the Store and run the installer above, and if the Store keeps opening afterwards, open **Manage app execution aliases** from the Start menu and turn off the `python.exe` and `python3.exe` entries.  `No module named pip` means pip was skipped: `python3 -m ensurepip --upgrade` restores it on macOS and Windows, and `sudo apt install python3-pip` does on Ubuntu.  On a fresh Mac, typing `python3` may offer to install Apple's Command Line Tools instead; that copy of Python 3 is several versions old and may be below the 3.10 floor, so install a current one from the table anyway.  If Homebrew complains that your macOS version is unsupported or a pre-release, run `brew update` first and retry.  `error: externally-managed-environment` from `pip install` on Ubuntu or Debian is handled in Part 1.5, Step 4.  The Stage 1 rows of the Troubleshooting table collect all of these.

> **A note on uv.**  `uv`, which Part 1.5 installs, can also fetch a Python of its own (`uv python install 3.12`) and run scripts with it (`uv run python warmup_check.py`).  Install a system Python first anyway, so that `python3` works in every terminal and every editor, and so that the `python -m venv` fallback has something to run.

### Step 2: Saving and running the starter script

**Do this.**  Save the script below as `warmup_check.py`, using any of the ways in *Terminal Basics* above.  On Route A, save it in your `cs374-work` repository, which is `/workspace` inside the container; on Route B, save it in `~/cs374`.  It exercises `re`, `json`, and `match`/`case`, and prints a confirmation banner if all three pass.

```python
# warmup_check.py: CS374 environment verification script
# Run with: python3 warmup_check.py

import sys, re, json

EXPECTED_PYTHON = (3, 10)

def check_python_version():
    v = sys.version_info
    ok = (v.major, v.minor) >= EXPECTED_PYTHON
    print(f"[{'OK' if ok else 'FAIL'}] Python {v.major}.{v.minor}.{v.micro}  "
          f"(need >= {EXPECTED_PYTHON[0]}.{EXPECTED_PYTHON[1]})")
    return ok

def check_re():
    # Test: tokenize a tiny expression
    pattern = re.compile(r"(?P<NUM>\d+)|(?P<PLUS>\+)|(?P<WS>\s+)")
    tokens = [(m.lastgroup, m.group()) for m in pattern.finditer("1 + 2")
              if m.lastgroup != "WS"]
    ok = tokens == [("NUM", "1"), ("PLUS", "+"), ("NUM", "2")]
    print(f"[{'OK' if ok else 'FAIL'}] re module: tokenized '1 + 2' -> {tokens}")
    return ok

def check_json():
    data = json.loads('{"language": "Mini", "version": 1, "strict": true}')
    ok = data["language"] == "Mini" and data["version"] == 1
    print(f"[{'OK' if ok else 'FAIL'}] json module: parsed {data}")
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
    print(f"[{'OK' if ok else 'FAIL'}] match/case: all {len(tests)} structural tests passed")
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
    print(f"[{'OK' if ok else 'FAIL'}] dataclasses: Token{t} constructed correctly")
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
    print("  CS374 environment verified. OK")
    print("  You are ready to build a language.")
    print("=" * 50)
else:
    failed = sum(1 for r in results if not r)
    print(f"  {failed} check(s) failed. See above for details.")
    print("  Document each failure verbatim and bring it to class.")
```

Then run it from the directory the file lives in:

| Route | Where you run it | The commands |
|---|---|---|
| A | At the container prompt | `cd /workspace`, then `python3 --version`, then `python3 warmup_check.py` |
| B, macOS, Linux, or WSL2 | In your own terminal | `cd ~/cs374`, then `python3 warmup_check.py` |
| B, Windows PowerShell | In PowerShell | `cd ~/cs374`, then `python warmup_check.py` |

VS Code's Run button (the triangle in the top right, with the Python extension installed) runs the same command in its integrated terminal, and either transcript is fine for your submission.

**What you should see.**  Five `[OK]` lines and the banner `CS374 environment verified. OK`.  On Windows consoles that garble the yes/no characters, run with `PYTHONIOENCODING=utf-8` or read the True/False values instead.

> **Paste into your submission:** the full transcript: the prompt (including the container prompt on Route A), `python3 --version`, and the script's output.

**If it goes wrong.**  `can't open file ... No such file or directory` means you are running from a different directory than the one you saved into; `ls` (or `dir`) shows which.  A `[FAIL]` on the Python version line means Step 1 needs another pass.  A `SyntaxError` at `match x:` means the Python that ran is older than 3.10, whatever `python3 --version` said in a different window.

### Step 3: Choosing your editor

**Do this.**  State which editor or IDE you will use for the semester and confirm that you can:

- Open, edit, and save a Python file.
- Run a Python file from within the editor (or from its integrated terminal).
- Set a breakpoint and inspect a variable in the debugger.

Recommended editors: VS Code (with the Python extension), PyCharm Community Edition, or any editor you already know.  On Route A, VS Code with the Dev Containers extension, opened inside the course container, is the recommended answer and satisfies all three bullets.

Avoid IDEs that hide the command line entirely; you will need `python3`, `git`, and occasionally `pip` directly.

> **Paste into your submission:** the editor's name and one sentence per bullet saying how you confirmed it.

### Wrapping up Part 1

**Capture a transcript** (copy-paste or screenshot) of all three steps.  If any step fails, document the error text verbatim, your hypothesis about the cause, and what you tried to fix it.  A well-documented failure with a follow-up plan earns full credit for that step.

---

## Part 1.5: Getting Comfortable with the Shell and Git

> **In this part:** Stages 4 to 7 of the map.  You will move around a shell and search a file, connect to GitHub with an SSH key, clone (or create) a repository and push a commit to it, and make a reproducible Python environment with uv.

You will build one language across six assignments, each importing the previous stage's component *unchanged*, all from the terminal and all under version control.  This checkpoint confirms those underlying tools work before the pipeline depends on them.

You don't need to be a shell expert.  You need to navigate, version your work, and create a reproducible environment.

The steps below are complete on their own.  Two tutorials go deeper when you want them: the [Course Development Environment]({{ site.baseurl }}/Tutorials/DevEnvironment) for the container, git identity, and the daily loop, and [Shell Skills for Language Development]({{ site.baseurl }}/Tutorials/ShellForLanguageDev), whose Step 0 covers opening a terminal, navigation, and `grep`, and whose later steps build the test harness you will want by the first programming assignment.  The **Handy References** links at the end of this part fill any remaining gaps.

> **Route A note.**  Do the git steps of this checkpoint **from inside the course container**, against the `cs374-work` GitHub repository you created in the [Development Environment tutorial]({{ site.baseurl }}/Tutorials/DevEnvironment).  The tutorial's practice section (create `hello.py`, run, commit, push) is exactly this checkpoint, so its transcript satisfies the shell-navigation and git items below.
>
> Create the SSH key in Step 2 on your host anyway, because that is where it belongs.  The `uv` step runs on your host on both routes; the container already pins the course packages, and `uv` is your reproducible-environment tool for everything outside the container.

Complete each step and capture the terminal output.

### Step 1: Moving around and searching a file

**Do this.**  Create a course directory, enter it, and list it:

```bash
mkdir -p ~/cs374 && cd ~/cs374 && pwd && ls -la
```

The directory is empty at this point, so make a file for the search to find.  Redirecting a couple of lines into a file is the quickest way; typing them into an editor (`nano sample.txt`, or any of the ways in *Terminal Basics* above) or copying in a `.py` file you already have works just as well:

```bash
printf 'let x = 1;\nlet y = x + 2;\nprint y;\n' > sample.txt
cat sample.txt
```

`touch sample.txt` creates the file but leaves it empty, and a search over an empty file matches nothing, so put a line or two inside it.

In native PowerShell, the equivalent is `Set-Content sample.txt "let x = 1;"`, since `printf` and `grep` are Unix shell tools, and `Select-String` is the PowerShell search command.  Running these from WSL2 or Git Bash keeps the commands as written.

Now run one search with `grep -n` (or `rg`):

```bash
grep -n "let" sample.txt
```

**What you should see.**  `pwd` prints a path ending in `cs374`, `cat` prints your three lines, and `grep` prints `1:let x = 1;` and `2:let y = x + 2;`, each with its line number.

> **Paste into your submission:** every command above with its output.

Searching text is the daily reality of lexer and parser work, the same regular expressions you will use in the Regex assignment, and [regex101](https://regex101.com/) is your friend there.

### Step 2: Connecting to GitHub with an SSH key

You will push to GitHub all semester, and GitHub has not accepted account passwords over HTTPS for years, so settle authentication now rather than discovering it at your first `git push`.

SSH (Secure Shell) is the protocol; the key is a file pair, one half private and one half public.  Use a key you already have, or create one.  Follow 2a through 2d in order; the alternatives after Step 3 replace specific sub-steps, and you should choose at most one.

#### 2a. Check for a key you already have

```bash
ls -al ~/.ssh
```

Look for a pair such as `id_ed25519` and `id_ed25519.pub`.  If a pair is there and you know it is registered with GitHub, jump to 2d.

#### 2b. Create a key

Ed25519 is the current default; use `ssh-keygen -t rsa -b 4096` instead only on a system too old to support it.

```bash
ssh-keygen -t ed25519 -C "your_email@example.com"
```

Accept the default path (`~/.ssh/id_ed25519`).  A passphrase is optional and worth setting; if you set one, load the key into the agent so you are not retyping it every push: `eval "$(ssh-agent -s)"`, then `ssh-add ~/.ssh/id_ed25519`.

#### 2c. Register the public key with GitHub

Print it with `cat ~/.ssh/id_ed25519.pub` and copy the entire line, then on GitHub open **Settings -> SSH and GPG keys -> New SSH key**, title it so you can tell which machine it belongs to, and paste.

Paste the `.pub` file and nothing else: the file *without* `.pub` is your private key, and it never leaves your machine, never goes in a repository, and never gets pasted into a web form.

#### 2d. Test it

```bash
ssh -T git@github.com
```

**What you should see.**  The first connection asks you to confirm GitHub's host fingerprint; answering `yes` is expected.  Success looks like `Hi YOURUSERNAME! You've successfully authenticated, but GitHub does not provide shell access.`  That is the success message, not an error: GitHub is telling you the key works and that SSH to GitHub is only ever used for git, never for a login shell.

> **Paste into your submission:** that output.

From here on, use the SSH remote form, `git@github.com:YOURUSERNAME/REPO.git`, rather than the `https://` URL.  If you already cloned over HTTPS, switch the existing remote rather than re-cloning:

```bash
git remote set-url origin git@github.com:YOURUSERNAME/REPO.git
```

> **Route A and credentials inside the container.**  This key lives on your **host** machine, which is where you just made it.  Inside the container, Step 5 of the [Development Environment tutorial]({{ site.baseurl }}/Tutorials/DevEnvironment) recommends a repository-scoped personal access token (PAT) instead, and shows the read-only key mount if you would rather use this key there.  That is why the tutorial clones `cs374-work` over HTTPS: the token authenticates HTTPS pushes.  Either way, create and register the key here.

### Step 3: Cloning, committing, and pushing

Get a repository on your machine, commit a file to it, and push that commit back to GitHub.

Which command starts you off depends on where the repository already exists, and this is the distinction worth learning once rather than guessing at every semester: **clone** when the repository is already on GitHub, and `git init` only when it is not.

#### 3a. Get the repository onto your machine

If the repository already exists on GitHub (your GitHub Classroom repository, or the `cs374-work` repository you created in the [Development Environment tutorial]({{ site.baseurl }}/Tutorials/DevEnvironment)), clone it.  Cloning downloads the full repository, sets `origin` to the URL you cloned from, and leaves you in a working copy that is already connected, so there is no `git remote add` afterward.

Copy the address from the green **Code** button on the repository page, choosing the **SSH** tab so you get the `git@github.com:` form the key you just tested authenticates:

```bash
cd ~/cs374
git clone git@github.com:YOURUSERNAME/REPO.git
cd REPO
git remote -v
```

`git clone` creates a *new folder* named after the repository, inside whatever directory you run it from, which is why you `cd` into it on the next line.  `git remote -v` should print your SSH URL twice, once for fetch and once for push; that is your evidence the working copy is wired to GitHub.

A repository with no commits yet clones with a warning that it is empty, and that is fine, since the commit below is about to fill it.

If you are starting from a folder on your machine instead, with no repository on GitHub yet, create the repository on GitHub first (**+ > New repository**, no README, which keeps the histories from conflicting), then `git init` locally and attach that remote by hand:

```bash
git init
git remote add origin git@github.com:YOURUSERNAME/REPO.git
```

#### 3b. Commit and push

Git versions files, so the repository needs at least one file in it before there is anything to commit; create that file the way you created `sample.txt` above, with a redirect, an editor, or a copy of something you already have:

```bash
printf '# CS374 scratch repository\n' > README.md
git add README.md
git commit -m "first commit"
git push -u origin main
```

**What you should see.**  `git commit` prints a line beginning `[main` with your message, and `git push` ends with `main -> main` and does not prompt for a username or password.

> **Paste into your submission:** the output of `git log --oneline`, run after the push.  Your team will live in git during the capstone, so start now.

**If it goes wrong.**  Three things commonly go sideways here:

- `git commit` without `-m` drops you into an editor, and `:q!` leaves it if that editor turns out to be `vim`.
- `git push` complains if your default branch is not named `main`, which `git branch -M main` fixes.
- A `git clone` that asks for a password means you copied the HTTPS address rather than the SSH one, so `git remote set-url origin git@github.com:YOURUSERNAME/REPO.git` puts it right without re-cloning.

### Other ways to do Steps 2 and 3

Choose at most one of these, and verify with `ssh -T git@github.com` either way.

#### The GitHub CLI, and the one I would take on native Windows

The [GitHub CLI](https://cli.github.com/), the `gh` command, does the entire exchange in 2b through 2c for you.  Install it (`winget install --id GitHub.cli` in PowerShell, `brew install gh` on macOS, or your package manager on Linux), then run `gh auth login`, choose **GitHub.com**, choose **SSH** as the protocol, and answer yes when it offers to generate a new SSH key and upload it to your account.

That one prompt replaces `ssh-keygen`, the `cat` of the `.pub` file, and the paste into Settings.  Verify it exactly as in 2d and paste that output; `gh` also clones for you, with `gh repo clone YOURUSERNAME/REPO` in place of the `git clone` in 3a.

#### VS Code, for the clone in 3a

It drives the same git underneath, so the result is identical.  With no folder open, the Source Control view (Ctrl+Shift+G, or Cmd+Shift+G on macOS) offers a **Clone Repository** button; from anywhere, the Command Palette (Ctrl+Shift+P, or Cmd+Shift+P) runs **Git: Clone**.

Either one asks for the repository address, where you paste the same SSH URL, then asks which local folder to put it in, `~/cs374` here, and offers to open the clone when it finishes.  Say yes: the integrated terminal (Ctrl+`) then opens already inside the repository, which is where you run `git log --oneline` for your transcript.

The palette also offers **Clone from GitHub**, which lets you pick from a list of your repositories instead of pasting a URL, though it signs you in to GitHub inside VS Code and authenticates as that account rather than with your key.  This is the same editor you identified in Part 1, Step 3, so if you set a breakpoint there you already have it installed.

#### GitHub Desktop, for 3a and 3b

[GitHub Desktop](https://desktop.github.com/) is the graphical client; it bundles Git for Windows, which is where `ssh-keygen` and Git Bash come from, and it handles its own authentication so you can clone, commit, and push without touching a key at all.

Paste `git log --oneline` from Repository > Open in terminal, which is the same transcript the command-line route produces.  Create the key in Step 2 anyway, because the checklist asks for the `ssh -T` output.

> **Telling the two GitHub downloads apart on native Windows without WSL2.**  `gh` is the command-line tool, a separate install rather than something GitHub Desktop brings along, though installing both is common and they coexist happily.  GitHub Desktop is the graphical client just described.  Either one spares you the manual key dance; the Ubuntu or WSL2 route gives you the standard Unix tooling instead, and every command on this page then works as written.

### Step 4: Making a reproducible Python environment with uv

**Do this.**  Install [uv](https://docs.astral.sh/uv/), the fast modern Python environment manager we standardize on this term, using the row for your system:

| System | Install uv | Then |
|---|---|---|
| **macOS, with Homebrew** | `brew install uv` | Nothing; Homebrew's directory is already on your `PATH` |
| **macOS, Linux, or WSL2 Ubuntu** | The standalone installer: the one-line `curl` command in the first block below the table | Open a new terminal, or run `source $HOME/.local/bin/env`, so that `~/.local/bin` is on your `PATH` |
| **Windows, PowerShell** | The standalone installer: the one-line `powershell` command in the second block below the table, or `winget install --id=astral-sh.uv -e` | Open a new PowerShell window |
| **Any system, through pipx** | `pipx install uv`.  pipx itself comes from `brew install pipx` on a Mac, `sudo apt install pipx` on Ubuntu or WSL2, or `python -m pip install --user pipx` on Windows, each followed by `pipx ensurepath` | Open a new terminal, so that pipx's `~/.local/bin` is on your `PATH` |
| **Any system, through pip** | `python3 -m pip install uv` (PowerShell: `python -m pip install uv`) | Nothing, though on Ubuntu this meets the `externally-managed-environment` refusal described below, so use the `curl` or pipx row there |

The two standalone installer lines, which do not fit in a table cell:

```bash
# macOS, Linux, or WSL2 Ubuntu
curl -LsSf https://astral.sh/uv/install.sh | sh
```

```powershell
# Windows, in PowerShell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Confirm the install with `uv --version`.

> **pip, pipx, or uv?**  All three install packages from the [Python Package Index](https://pypi.org/), and they divide the work cleanly.  **pip** installs a library into one particular Python, for that Python's scripts to import.  **pipx** installs a *program* written in Python (uv, `ruff`, `black`, `jupyter`) into a private environment of its own and puts its command on your `PATH`, so tools never fight over versions.  **uv** does both jobs per project, and pins what it installed in `pyproject.toml` so a teammate can rebuild the same environment; that reproducibility is why the course standardizes on it.  `pytest` is the instructive case, because it is both a library your tests import and a program you run:
>
> | Tool | The command | What it does, and when to use it |
> |---|---|---|
> | **pip, inside a virtual environment** | macOS, Linux, or WSL2: `cd ~/cs374`, `python3 -m venv .venv`, `source .venv/bin/activate`, then `python3 -m pip install pytest`.  PowerShell: `cd ~/cs374`, `python -m venv .venv`, `.\.venv\Scripts\Activate.ps1`, then `python -m pip install pytest` | A virtual environment is a private copy of Python's library folder for one project, kept in `.venv`, so that the library lands there rather than in the system Python.  Activating it (the prompt gains a `(.venv)` prefix) makes `python3` and `pip` mean that copy for the rest of the terminal session, so activate it again in every new terminal.  Installing without one works on macOS and Windows but is a habit to unlearn: it stops with `error: externally-managed-environment` on Ubuntu, Debian, and a fresh WSL2 Ubuntu, and it mixes every project's libraries together.  If PowerShell refuses to run the activation script, run `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser` once, then retry.  This is the documented fallback if uv will not install |
> | **uv** | `cd ~/cs374`, `uv init`, `uv add pytest`, then `uv run pytest` | Creates the project's own environment in `~/cs374/.venv`, records `pytest` in `pyproject.toml`, and runs it there, where it can import your interpreter's modules.  This is the course way, and it is what the commands below do |
> | **pipx** | `pipx install pytest` | Works, because pytest is a program, but installs it into a private environment that cannot see your project's code or libraries, so your test suite's imports fail.  Right for a standalone tool such as uv, wrong for a project's test runner |

Then, in your `~/cs374` directory, create a project and an environment, and add `pytest`, because you will write test suites all semester:

```bash
cd ~/cs374
uv init
uv venv
uv run python --version
uv add pytest
```

`uv init` writes a `pyproject.toml`, which is what `uv add` records the dependency in; without it, `uv add` stops with a message about a missing project.

**What you should see.**  `uv run python --version` prints a Python version, and `uv add pytest` prints `Installed` lines that include `pytest`.  A bare `pytest` afterward would say `no tests ran`, which is correct, because there are no tests yet.

> **Paste into your submission:** the output of all four commands.

**If it goes wrong.**  What I am checking is that the tools are installed and on your PATH, so the output that fails this step is `uv: command not found` or `pytest: command not found`, not a complaint about a missing project.  `uv: command not found` right after the installer means the terminal predates it; open a new one, or run `source $HOME/.local/bin/env`.  On a Mac, if `brew install uv` complains that your macOS version is unsupported, run `brew update` and retry.  If you cannot install uv, fall back to `python3 -m venv .venv`, `source .venv/bin/activate`, and `python3 -m pip install pytest` (PowerShell: `python -m venv .venv`, `.\.venv\Scripts\Activate.ps1`, `python -m pip install pytest`), and note the fallback in your submission.

### Handy References for the Command Line

Use these as needed; none of them is required reading.

- [Shell Skills for Language Development]({{ site.baseurl }}/Tutorials/ShellForLanguageDev): Step 0 for the terminal basics this checkpoint uses, and Steps 1 through 6 for the test harness and Makefile you will want by the first programming assignment.
- [tldr pages](https://tldr.sh/): example-first cheat sheets (`tldr grep`).
- [explainshell](https://explainshell.com/): annotates any command line flag by flag.
- [ShellCheck](https://www.shellcheck.net/): lints shell scripts (you will use it in the project's scripting-targets extension).
- [regex101](https://regex101.com/): interactive regex tester, directly useful for the Regex and Lexer assignments.

### Part 1.5 Checklist

- [ ] A shell transcript showing directory creation, navigation, and a `grep`/`rg` search
- [ ] The output of `ssh -T git@github.com`, showing your GitHub username
- [ ] A `git log --oneline` transcript showing at least one commit pushed to a remote over SSH
- [ ] A `uv` (or documented fallback) transcript creating an environment and adding `pytest`

---

## Part 2: Your Language Autobiography

> **In this part:** Stage 8 of the map.  You will write about a page answering four prompts about your history with programming languages.  No tools needed, so this is a good one to write while something is downloading.

The purpose of this section is to capture your relationship with programming languages at the start of the course, as a baseline you will revisit in your final report.  Write approximately one page (400-600 words), addressing all four prompts below.

### Prompt 1: Your language history

List every programming language and formal notation you have used, and please count regex, SQL, spreadsheets, HTML, configuration languages, and shell scripts.  For each one, write a sentence on what it was good at from your perspective as a user.  Don't worry about precision here; I want your candid impressions more than textbook accuracy.

*Example opening:* "Python (four years): excellent for data exploration because the REPL makes it easy to try ideas without a compile step.  SQL (one semester): surprisingly good at expressing 'find all rows where' queries, but I found joins hard to visualize..."

### Prompt 2: A moment the language fought you

Describe one specific moment when a language was harder to use than you expected, meaning something you wanted to express that the language made difficult, surprising, or impossible.  Please be concrete, and name the language, the construct you were trying to write, and what the language made you do instead.

*What to aim for:* an answer that uses at least one of these words precisely: syntax, semantics, type, scope, evaluation order, binding.  You do not need to know all these words yet; use the ones you know and leave placeholders for the ones you don't.

### Prompt 3: A moment of elegance

Describe one feature of any language (or of a language feature you read about) that felt elegant the first time you understood it.  "Elegant" can mean surprisingly concise, surprisingly general, or surprisingly consistent.

### Prompt 4: An open question

Pose one question about how programming languages work that you hope this course will answer.  The best questions are the ones you don't know the answer to, and not the ones you could look up in Wikipedia.

*Examples of good questions:* "Why does Python have both `is` and `==`, and what is actually different between them at the implementation level?"  "How does a compiler know which variables a closure needs to capture?"  "Is there a way to guarantee that a recursion terminates without running it?"

---

## Troubleshooting

Work down this table before you post in the course channel.  The Stage column matches the map at the top of the page.  If none of it helps, post the exact command you ran and its full output.

| Stage | Symptom | Likely cause | Fix |
|---|---|---|---|
| 1 | `python3: command not found` or `'python3' is not recognized` on Windows | Windows Python installs as `python` | Use `python` wherever this page says `python3` |
| 1 | `python3 --version` prints 3.9 or earlier | An older Python is first on your PATH | Install 3.10 or later as in *Installing Python and pip*, open a new terminal, and check `which python3` (PowerShell: `Get-Command python`) |
| 1 | `python3: command not found` on macOS or Linux, or `python` opens the Microsoft Store on Windows | Python is not installed, or the terminal window predates the install | Install it from *Installing Python and pip*, then open a new terminal.  On Windows, if the Store keeps opening afterwards, turn off the `python.exe` and `python3.exe` entries under **Manage app execution aliases** |
| 1 | `No module named pip` | Python was installed without its package installer | `python3 -m ensurepip --upgrade` on macOS and Windows; `sudo apt install python3-pip` on Ubuntu and WSL2 |
| 1 | `python3 -m pip --version` names a different Python than the one you just installed | Several Pythons on the machine, and `PATH` finds an older one first | `which python3` (PowerShell: `Get-Command python`) shows which one wins; open a new terminal after the install, and always write `python3 -m pip` rather than a bare `pip` |
| 1 | On a Mac, Homebrew says your macOS version is unsupported or a pre-release, and `brew install` fails | Your copy of Homebrew predates your macOS upgrade | `brew update`, then rerun the install.  Homebrew needs macOS Sonoma (14) or later |
| 1 | `cd ~/cs374` says the path does not exist, or lands somewhere odd | You are in the old Windows Command Prompt, where `~` is not your home folder | Open PowerShell or Ubuntu instead, or use `cd %USERPROFILE%\cs374` there |
| 1 | `Cannot connect to the Docker daemon`, or `docker` is not a command inside Ubuntu | Docker Desktop is not running, or its WSL integration is off | Start Docker Desktop; on Windows, **Settings -> Resources -> WSL Integration**, switch **Ubuntu** on, **Apply & Restart**; the tutorial's Step 10 has the rest |
| 2 | `can't open file 'warmup_check.py': No such file or directory` | You are running from a different folder than the one you saved into | `pwd` (or `cd` alone in Command Prompt) shows where you are; `ls` shows what is there; `cd` to the folder that has the file |
| 2 | `SyntaxError` at the line `match x:` | The Python that ran is older than 3.10, whatever another window said | Run `python3 --version` in the *same* terminal, and fix Step 1 there |
| 2 | The banner's check marks print as odd characters | A Windows console encoding | Run with `PYTHONIOENCODING=utf-8`, or read the `OK`/`FAIL` words instead |
| 4 | `grep` or `printf` is not recognized | You are in native PowerShell, where these are Unix commands | Use `Set-Content` and `Select-String` as Step 1 shows, or run the commands from WSL2 or Git Bash |
| 5 | `ssh-keygen` is not recognized on Windows | OpenSSH is not installed, or the window predates it | Open a new PowerShell window; if it persists, install GitHub Desktop (which bundles Git for Windows) or the GitHub CLI and use the alternative after Step 3 |
| 5 | `git@github.com: Permission denied (publickey)` | The key is not loaded in the agent, or its public half was never added to GitHub | `ssh-add -l` lists loaded keys and `ssh-add ~/.ssh/id_ed25519` loads yours; confirm the contents of `id_ed25519.pub` appear under Settings -> SSH and GPG keys; then retest with `ssh -T git@github.com` |
| 6 | `git push` asks for a password, then rejects it | The remote is the HTTPS address rather than the SSH one | `git remote set-url origin git@github.com:YOURUSERNAME/REPO.git`, then `git remote -v` to confirm, then push again |
| 6 | `git push` says `src refspec main does not match any` | Your default branch has another name, or nothing is committed yet | `git branch -M main`, confirm `git log --oneline` shows a commit, then push again |
| 6 | `git commit` opened an editor and you cannot get out | You omitted `-m`, and the editor is `vim` | Press **Esc**, type `:q!`, press **Enter**, then rerun `git commit -m "first commit"` |
| 7 | `uv: command not found` | Not installed, or not on `PATH` yet | Install it from the table in Part 1.5, Step 4 (`brew install uv` on a Mac with Homebrew, the `curl` or PowerShell installer elsewhere), then open a new terminal or run `source $HOME/.local/bin/env`; if it still fails, use the documented `python -m venv` fallback and say so |
| 7 | `brew install uv` says your macOS version is unsupported | Homebrew is older than your macOS | `brew update`, then rerun `brew install uv` |
| 7 | `error: externally-managed-environment` from `pip install` | Ubuntu and Debian protect the system Python from pip, and you installed outside a virtual environment | `python3 -m venv ~/cs374/.venv`, `source ~/cs374/.venv/bin/activate`, then rerun the install in that terminal; or use `uv add`, which never touches the system Python |
| 7 | PowerShell: `Activate.ps1 cannot be loaded because running scripts is disabled on this system` | The default execution policy blocks the activation script | `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser` once, then rerun `.\.venv\Scripts\Activate.ps1` |
| 7 | `uv add` complains that no `pyproject.toml` was found | You skipped `uv init` | Run `uv init` in the same directory, then rerun `uv add pytest` |

---

## Self-Check Before You Submit

Hold your submission against the rubric's `proficient` column:

- [ ] One file, PDF preferred, with each component **clearly labeled**.
- [ ] Part 0 is under its own `Part 0` heading, with both language judgments and the paradigm translation.
- [ ] The Part 1 transcript covers all three steps and shows the `python3 --version` line and the script's banner, copied verbatim.
- [ ] Which route you took (A or B) is stated, and a Route A transcript shows the container prompt.
- [ ] Part 1.5: the navigation and `grep` transcript, the `ssh -T git@github.com` greeting, a `git log --oneline` showing a pushed commit, and the uv (or documented fallback) output.
- [ ] Any failure is quoted exactly, with a hypothesis and what you tried.
- [ ] The autobiography answers all four prompts and is about a page.
- [ ] Collaboration, AI-disclosure, and hours questions answered at the end.
