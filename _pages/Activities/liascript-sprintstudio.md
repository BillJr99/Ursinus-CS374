# Sprint Studio and Gallery Walk
<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://github.com/BillJr99/Ursinus-CS374-Fall2026/blob/gh-pages/_pages/Activities/liascript-sprintstudio.md or locally via https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374/gh-pages/_pages/Activities/liascript-sprintstudio.md

import: https://raw.githubusercontent.com/liascript/CodeRunner/master/README.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

# Sprint Studio and Gallery Walk

Studio days are structured work time for the team language project: a stand-up, focused build time, and, on designated days, the formal **gallery walk** peer review that feeds your final sprint. This page is the protocol for every studio day; the gallery walk sections apply on the scheduled walk day. The arc: **stand-up $\rightarrow$ build $\rightarrow$ gallery walk $\rightarrow$ triage $\rightarrow$ release checklist**.

---

## Directions and Group Roles

Project roles (rotated by sprint) are in effect: **Coordinator**, **Builder(s)**, **Evaluator**, **Scribe**. The Scribe maintains today's living document: stand-up notes, all feedback received verbatim, and the triaged backlog the team leaves with.

---

## 1. Stand-Up (10 minutes)

Each team answers, in two minutes at the board, exactly four questions: What runs end-to-end today (which sample programs pass)? What is the riskiest unfinished piece of the sprint? What does the test suite report this week (a number of passing tests, not an adjective)? What do you need from the instructor or another team? The discipline is *saying the number*; "mostly working" is not a status.

---

## Model 1: Sprint Velocity — Measuring What "Done" Looks Like

A sprint velocity is a *count*, not a feeling. The Evaluator tracks two numbers: **stories completed** (AST nodes with passing tests) and **tests passing**. The cell below simulates a three-sprint project and visualizes the velocity trend, because a slowing velocity three sprints before Demo Day is early warning, not bad luck.

```python
# Sprint health dashboard: velocity, test coverage, and projection.
# Edit the DATA dict to reflect your team's actual numbers each sprint.

DATA = {
    "Sprint 1": {
        "nodes_planned": 8,
        "nodes_done":    6,
        "tests_passing": 14,
        "tests_total":   18,
        "sample_programs_running": 1,
        "known_failures": ["string concatenation crashes", "nested if not parsed"],
    },
    "Sprint 2": {
        "nodes_planned": 6,
        "nodes_done":    5,
        "tests_passing": 22,
        "tests_total":   26,
        "sample_programs_running": 3,
        "known_failures": ["function return value sometimes None"],
    },
    "Sprint 3": {
        "nodes_planned": 4,
        "nodes_done":    4,
        "tests_passing": 30,
        "tests_total":   30,
        "sample_programs_running": 5,
        "known_failures": [],
    },
}

TOTAL_NODES = 18  # total nodes in the node inventory

print("=" * 60)
print("SPRINT HEALTH DASHBOARD")
print("=" * 60)
print()

completed_so_far = 0
for sprint, d in DATA.items():
    velocity = d["nodes_done"] / d["nodes_planned"] if d["nodes_planned"] else 0
    test_pct  = d["tests_passing"] / d["tests_total"] * 100 if d["tests_total"] else 0
    bar_v     = "█" * d["nodes_done"] + "░" * (d["nodes_planned"] - d["nodes_done"])
    bar_t     = "█" * (d["tests_passing"] // 2) + "░" * ((d["tests_total"] - d["tests_passing"]) // 2)

    print(f"── {sprint} ──────────────────────────────────")
    print(f"  Nodes:   [{bar_v}]  {d['nodes_done']}/{d['nodes_planned']} ({velocity*100:.0f}%)")
    print(f"  Tests:   [{bar_t}]  {d['tests_passing']}/{d['tests_total']} ({test_pct:.0f}%)")
    print(f"  Samples: {d['sample_programs_running']} running")
    if d["known_failures"]:
        print(f"  Known failures ({len(d['known_failures'])}):")
        for f in d["known_failures"]:
            print(f"    • {f}")
    else:
        print(f"  Known failures: none ✓")
    completed_so_far += d["nodes_done"]
    print()

remaining = TOTAL_NODES - completed_so_far
last_velocity = DATA["Sprint 3"]["nodes_done"] / DATA["Sprint 3"]["nodes_planned"]
sprints_needed = remaining / (last_velocity * DATA["Sprint 3"]["nodes_planned"]) if last_velocity > 0 else float("inf")

print("── Projection ─────────────────────────────────────")
print(f"  Total nodes:        {TOTAL_NODES}")
print(f"  Completed so far:   {completed_so_far}")
print(f"  Remaining:          {remaining}")
print(f"  Last sprint rate:   {last_velocity*100:.0f}% ({DATA['Sprint 3']['nodes_done']}/{DATA['Sprint 3']['nodes_planned']})")
if remaining == 0:
    print(f"  → All nodes complete! Ready for Demo Day polish. ✓")
elif sprints_needed <= 1:
    print(f"  → On track: ~{sprints_needed:.1f} sprints to clear remaining nodes.")
else:
    print(f"  → WARNING: at current rate, ~{sprints_needed:.1f} more sprints needed. Re-scope now.")

print()
print("  Rule: a sprint with more than 2 known failures is not done.")
print("  Rule: test_pct < 80% triggers a test-debt sprint before new features.")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

### Critical Thinking Questions

1. The dashboard reports "known failures." Why is it *better* to list them than to omit them? Connect to the gallery walk protocol's requirement that every host show at least one failure.
2. If the projection says "2.3 more sprints" and only 1 sprint remains, what are the two legitimate responses? (Hint: one improves execution; the other improves scope.) Which is harder, and why?
3. "Mostly working" is not a status. Rewrite each of these non-statuses as a measurable status using the dashboard's vocabulary: "the parser is almost done," "tests are passing," "the niche feature is nearly complete."

---

## 2. Build Time

Builders build the sprint increment; the Evaluator extends the test suite *ahead of* the features (a failing test is a specification); the Scribe keeps `SEMANTICS.md` and the decision log current as choices happen, not after; the Coordinator defends scope against good ideas that belong in the future-work list. Mid-studio checkpoint: the Coordinator confirms the sprint goal is still achievable or re-scopes it *now*, aloud.

---

## Model 2: The Red-Green Discipline — Writing Tests Before Code

The Evaluator's job is to write **failing tests** before the Builder writes the code they test. A failing test is a specification: it states precisely what the code must do before the code exists. The cell below demonstrates the discipline by running a test suite against a deliberately incomplete interpreter, showing which tests fail (red), which pass (green), and what the gap is.

```python
# Demonstrate red-green testing: tests written first, implementation following.
# Edit the 'implemented' set to simulate different sprint states.

# ── Sprint State ──────────────────────────────────────────────────────────────
# Set each feature to True when it is implemented in your interpreter.
IMPLEMENTED = {
    "NumLit":     True,
    "StrLit":     True,
    "BoolLit":    True,
    "BinOp_arith": True,
    "BinOp_compare": True,
    "LetStmt":    True,
    "VarRef":     True,
    "IfStmt":     True,
    "WhileStmt":  False,   # ← not yet implemented
    "FunDecl":    False,   # ← not yet implemented
    "Call":       False,   # ← not yet implemented
    "ReturnStmt": False,
    "PrintStmt":  True,
    "LogicOp":    False,   # short-circuit
    "StringConcat": False, # "a" + "b"
}

# ── Test Registry ─────────────────────────────────────────────────────────────
# Each test: (description, required_feature, expected_output)
TESTS = [
    ("Integer literal",          "NumLit",       "42"),
    ("String literal",           "StrLit",       "hello"),
    ("Boolean literal",          "BoolLit",      "true"),
    ("Addition 2+3",             "BinOp_arith",  "5"),
    ("Subtraction 10-4",         "BinOp_arith",  "6"),
    ("Multiplication 3*4",       "BinOp_arith",  "12"),
    ("Division 10/4",            "BinOp_arith",  "2.5"),
    ("Comparison 3 < 5",         "BinOp_compare","true"),
    ("Equality 5 == 5",          "BinOp_compare","true"),
    ("Let x = 5; print x",       "LetStmt",      "5"),
    ("Variable reference",       "VarRef",       "10"),
    ("If true print yes",        "IfStmt",       "yes"),
    ("If false print no",        "IfStmt",       "no"),
    ("While count down",         "WhileStmt",    "0"),
    ("Function declaration",     "FunDecl",      None),
    ("Function call",            "Call",         "42"),
    ("Return statement",         "ReturnStmt",   "7"),
    ("Print statement",          "PrintStmt",    "hello world"),
    ("Short-circuit: and",       "LogicOp",      "false"),
    ("Short-circuit: or",        "LogicOp",      "true"),
    ("String concat 'a'+'b'",    "StringConcat", "ab"),
]

# ── Run and Report ─────────────────────────────────────────────────────────────
passing = [t for t in TESTS if IMPLEMENTED.get(t[1], False)]
failing = [t for t in TESTS if not IMPLEMENTED.get(t[1], False)]

print("=" * 55)
print(f"  TEST RESULTS — Sprint {sum(IMPLEMENTED.values())}/{len(IMPLEMENTED)} features")
print("=" * 55)
print()
print("  ✓ PASSING")
for desc, feat, expected in passing:
    print(f"    ✓  {desc}")

print()
print("  ✗ FAILING (specification written, not yet implemented)")
for desc, feat, expected in failing:
    label = f"[{feat}]"
    print(f"    ✗  {desc:<35} {label}")

print()
print(f"  Summary: {len(passing)}/{len(TESTS)} tests passing ({len(passing)/len(TESTS)*100:.0f}%)")
print()
if len(failing) == 0:
    print("  All tests green. Sprint goal met. ✓")
elif len(failing) <= 3:
    print(f"  {len(failing)} test(s) remaining. Sprint finish is this session.")
else:
    print(f"  {len(failing)} tests still failing. Evaluate sprint scope with Coordinator.")
print()
print("  Key: failing tests ARE the sprint backlog. Each ✗ is the next task.")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

### Critical Thinking Questions

4. The test for `FunDecl` has `expected_output = None` — no known output yet, just a known requirement. What does this represent in the red-green discipline, and why is it still worth writing the test?
5. If the Evaluator writes 5 new failing tests at the start of the sprint, and the Builder closes 3 of them, what is the sprint's velocity? Is a sprint with 2 remaining failing tests "done"?
6. The test suite acts as executable documentation of the language's semantics. Which is more authoritative: a test that passes, or the corresponding entry in `SEMANTICS.md`? What should you do when they disagree?

---

## 3. Gallery Walk Protocol (40 minutes, designated days)

Stations: each team's language runs live (REPL up, sample programs ready) beside two artifacts: the grammar one-pager and the current test results table. Half of each team hosts; half walks; swap at the midpoint.

Walkers leave one structured card per station, with exactly three fields:

- **Strength**: one specific thing that works, precisely named ("the error message for an unclosed brace points at the opening brace's line").
- **Question**: one genuine question the demo raised, ideally about a seam or a semantics decision ("what does your `for` desugar to, and does the loop variable survive?").
- **Risk**: the one thing most likely to fail on Demo Day, stated kindly and concretely.

Hosts demonstrate honestly: at least one **known failure case** must be shown at every station (a program that breaks the parser, a semantics corner still undecided). A demo that hides its failures is rehearsing a deception; your `SEMANTICS.md` deserves better.

---

## Model 3: Feedback Triage — Turning Gallery Walk Cards into Backlog

The Scribe collects all gallery walk cards and triages them live. The cell below simulates triage: take each card, classify it into a bucket, and produce an actionable backlog sorted by priority.

```python
# Gallery walk feedback triage simulator.
# FEEDBACK: list of (team, type, text) where type is "strength"|"question"|"risk"
# Edit FEEDBACK to reflect what your team actually received today.

FEEDBACK = [
    ("Team Amber", "strength", "Error message names the exact line and column for undefined variable"),
    ("Team Amber", "question", "What does the loop variable contain after the while exits?"),
    ("Team Amber", "risk",     "Function with no return statement: silently returns None or crashes?"),

    ("Team Cobalt", "strength", "Niche feature (dice rolls) parses cleanly in three contexts"),
    ("Team Cobalt", "question", "Can you pass a function as an argument to another function?"),
    ("Team Cobalt", "risk",     "REPL does not recover from a parse error — requires restart"),

    ("Team Jade",   "strength", "Sample programs are polished and diverse (five different patterns)"),
    ("Team Jade",   "question", "String equality: == or a separate 'equals' operator?"),
    ("Team Jade",   "risk",     "Nested function calls crash on more than two levels of nesting"),

    ("Instructor",  "question", "Does your scoping rule apply inside while loop bodies?"),
    ("Instructor",  "risk",     "SEMANTICS.md says null returns default-value, but the code raises"),
]

# ── Triage rules ──────────────────────────────────────────────────────────────
# Each "risk" and "question" becomes a backlog item.
# Classify into: FIX (blocks demo), DISCLOSE (acknowledged, out of scope), FUTURE

def triage_item(text):
    """Heuristic classifier — replace with your team's actual judgment."""
    crash_words = ["crash", "restart", "None", "raises", "fails", "breaks"]
    if any(w.lower() in text.lower() for w in crash_words):
        return "FIX"
    scope_words = ["first-class", "pass a function", "nested", "two levels"]
    if any(w.lower() in text.lower() for w in scope_words):
        return "FUTURE"
    return "DISCLOSE"

print("=" * 60)
print("  GALLERY WALK TRIAGE REPORT")
print("=" * 60)
print()

buckets = {"FIX": [], "DISCLOSE": [], "FUTURE": [], "STRENGTH": []}
for team, kind, text in FEEDBACK:
    if kind == "strength":
        buckets["STRENGTH"].append((team, text))
    else:
        bucket = triage_item(text)
        buckets[bucket].append((team, kind, text))

print("  ✓ STRENGTHS (keep and amplify)")
for team, text in buckets["STRENGTH"]:
    print(f"    [{team}] {text}")

print()
print(f"  🔴 FIX BEFORE DEMO DAY ({len(buckets['FIX'])} items)")
for team, kind, text in buckets["FIX"]:
    print(f"    [{team}] {text}")
    print(f"           → Assign to: ___  Due: ___  Done when: ___")

print()
print(f"  🟡 DISCLOSE AT DEMO DAY ({len(buckets['DISCLOSE'])} items)")
for team, kind, text in buckets["DISCLOSE"]:
    print(f"    [{team}] {text}")
    print(f"           → Disclosure wording: ___")

print()
print(f"  🔵 FUTURE WORK ({len(buckets['FUTURE'])} items)")
for team, kind, text in buckets["FUTURE"]:
    print(f"    [{team}] {text}")

print()
print(f"  Totals: {len(buckets['FIX'])} fix / {len(buckets['DISCLOSE'])} disclose / {len(buckets['FUTURE'])} future")
print()
print("  Scribe: fill in the blanks above and commit BACKLOG.md before end of day.")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

### Critical Thinking Questions

7. Two items are classified as DISCLOSE: known limitations acknowledged at Demo Day rather than fixed. Why is a well-worded disclosure *preferable* to a rushed fix made the night before? What risks does a rushed fix introduce?
8. The Instructor's risk item says "SEMANTICS.md says X, but the code does Y." Which one is right? Write the policy your team will follow when documentation and implementation disagree.
9. As a walker, you notice a language with much better error messages than yours. Should you copy their approach, ask how they did it, or note it as a future-work item? Use the triage categories to articulate the difference.

---

## 4. Triage (20 minutes, after the walk)

Cluster the cards and sort every item into exactly one bucket: **Fix before Demo Day** (breaks the core story), **Disclose at Demo Day** (real, acknowledged, out of scope), or **Future work** (report material). The discipline is the middle bucket: mature engineering names its known defects. The Scribe converts bucket one into assigned, dated backlog items before anyone leaves.

---

## 5. Demo Day Release Checklist

Before Demo Day, the Evaluator verifies and signs each line:

1. The REPL and the file-runner both work from a fresh clone following the readme, in under three minutes.
2. All sample programs (five minimum, including one that shows off the niche) run with committed expected outputs.
3. The test suite passes and its results table is current in the repository.
4. `SEMANTICS.md` and the grammar document match what the implementation actually does today.
5. One failure case is rehearsed and its disclosure worded.
6. Every teammate can run the demo and explain the distinctive feature solo.
7. Reproducibility: Python version listed, any dependencies pinned, setup tested by the teammate who did not write it.

```python
# Release checklist automator: enforces the 7-item checklist as code.
# Run this before Demo Day. Each check must return True to pass.

import os, subprocess, sys

def check(label, result, guidance=""):
    status = "✓" if result else "✗"
    print(f"  {status}  {label}")
    if not result and guidance:
        print(f"        → {guidance}")
    return result

print("=" * 55)
print("  DEMO DAY RELEASE CHECKLIST")
print("=" * 55)
print()

results = []

# Check 1: README exists and contains setup instructions
readme_ok = os.path.exists("README.md") or os.path.exists("readme.md")
results.append(check("README exists with setup instructions", readme_ok,
    "Create README.md with: Python version, install steps, 'python main.py' usage"))

# Check 2: sample programs exist
samples = [f for f in os.listdir(".") if f.startswith("sample") and f.endswith(".lang")]
results.append(check(f"Sample programs present ({len(samples)} found, 5 required)",
    len(samples) >= 5,
    "Add sample_01.lang through sample_05.lang; one must show the niche feature"))

# Check 3: test suite file exists
test_file = os.path.exists("test_lang.py") or os.path.exists("tests.py")
results.append(check("Test suite file exists", test_file,
    "Create test_lang.py; run it; commit passing output"))

# Check 4: SEMANTICS.md exists and is non-empty
sem_ok = os.path.exists("SEMANTICS.md") and os.path.getsize("SEMANTICS.md") > 500
results.append(check("SEMANTICS.md exists and is non-trivial (>500 bytes)", sem_ok,
    "Must cover: scoping, truthiness, division, strings, null/absent-value policy"))

# Check 5: grammar file exists
grammar_ok = os.path.exists("grammar.ebnf") or os.path.exists("GRAMMAR.md")
results.append(check("Grammar document present", grammar_ok,
    "grammar.ebnf or GRAMMAR.md must match current implementation"))

# Check 6: main entry point is runnable
entry_ok = os.path.exists("main.py") or os.path.exists("lang.py")
results.append(check("Entry point (main.py or lang.py) exists", entry_ok,
    "python main.py --repl and python main.py program.lang must both work"))

# Check 7: no Python syntax errors in main entry point
if entry_ok:
    entry_file = "main.py" if os.path.exists("main.py") else "lang.py"
    try:
        result = subprocess.run([sys.executable, "-m", "py_compile", entry_file],
                                capture_output=True)
        syntax_ok = result.returncode == 0
    except Exception:
        syntax_ok = False
    results.append(check(f"Entry point has no Python syntax errors", syntax_ok,
        f"Run: python -m py_compile {entry_file}"))
else:
    results.append(check("Entry point syntax check (skipped: no entry file)", False,
        "Create main.py first"))

print()
passed = sum(results)
total  = len(results)
print(f"  {passed}/{total} checks passed")
if passed == total:
    print("  → Ready for Demo Day. ✓")
elif passed >= total - 1:
    print("  → One item remaining. Fix it today.")
else:
    print(f"  → {total - passed} items remaining. Triage them now.")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

### Critical Thinking Questions

10. The checklist runs automated checks, but check 6 ("every teammate can demo the distinctive feature solo") cannot be automated. Why does this check matter, and what would a *passing* version of it look like as an observable event rather than a feeling?
11. Check 4 requires SEMANTICS.md to be non-trivial (>500 bytes). Is this a good proxy for "SEMANTICS.md is complete"? Propose a better automated check.
12. The checklist is run *before* Demo Day. On what day should the Evaluator first run it, and what should happen if any check fails with three days remaining?

---

## Reflection Prompt

In your notebook: compare the feedback your team received today with the error messages your language gives its users. Both are diagnostics offered to someone mid-effort. What makes each actionable or useless, and what will you change in one of them this week? Also: the stand-up discipline says "say the number." What is one domain — not software — where you have benefited from someone insisting on numbers over adjectives?

---

## 6. Further Reading

- The project specification's Demo Day rubric, reread tonight.
- Robert Nystrom. *Crafting Interpreters*, the "Challenges" sections of your weakest chapter, as triage inspiration.
- Tom DeMarco and Timothy Lister. *Peopleware*, Chapter 11: the cost of not measuring.
- Kent Beck. *Test-Driven Development: By Example* — the red-green-refactor cycle your Evaluator role embodies.
