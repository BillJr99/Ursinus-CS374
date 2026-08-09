<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://github.com/BillJr99/Ursinus-CS374-Fall2026/blob/gh-pages/_pages/Activities/liascript-languagedesign.md or locally via https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374/gh-pages/_pages/Activities/liascript-languagedesign.md

import: https://raw.githubusercontent.com/liascript/CodeRunner/master/README.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

# Language Design Studio: Sprint 0

Programming languages are not magic handed down from on high — they are deliberate design choices made by people who had a problem to solve. Understanding those choices matters even if you never ship a language of your own, because every time you pick up a new language, reach for a library, or decide how to structure an API, you are making the same tradeoffs language designers make. Think of it like car mechanics: you do not need to rebuild an engine to drive, but a driver who understands what the transmission does makes better decisions on icy roads. This activity puts you in the designer's seat so you can become a more intentional user of every tool in your toolbox.

## Learning Goals

By the end of this activity, you will be able to:

- Construct a language identity statement that identifies a target niche, a distinctive feature, and the non-negotiable implementation requirements
- Evaluate two syntax variants of the same language on the criteria of readability, writability, and learnability, citing specific syntactic evidence
- Apply the language design scorecard to score and justify design decisions for your own language project
- Define the required components of a Sprint 0 language specification: grammar sketch, node inventory, and design document outline
- Compare the consequences of at least two specific syntax design choices (e.g., keyword blocks vs. brace blocks) for both users and implementers

The team project begins today: with the whole pipeline behind you — capped by the Church encodings of *The Lambda Calculus, Part 2* — your team will design and implement **a programming language of your own**, assembling the lexer, parser, AST, environments, and evaluator you each built into one system with an identity, a grammar, and a Demo Day. Today is Sprint 0: identity, scorecard, grammar v0, and a working plan. The arc: **what makes a language yours $\rightarrow$ the design scorecard $\rightarrow$ grammar and node inventory v0 $\rightarrow$ sprint roles and cadence**.

> **Before You Begin:** This activity assumes you can:
> - Read and write a basic recursive-descent parser and understand how grammar rules map to parsing functions
> - Explain what an AST node is and how an evaluator walks the tree to produce a result
> - Describe lexical scoping: what an environment chain is and how variable lookup traverses it
>
> If any of these feel shaky, review your lexer/parser/evaluator assignments before continuing — this activity builds directly on that vocabulary.

---

## Directions and Group Roles

From today through Demo Day, your team works in **project roles, rotated every sprint**:

- **Coordinator**: owns the sprint plan, runs stand-ups, watches scope.
- **Builder(s)**: own the code increment of the sprint.
- **Evaluator**: owns the test suite, the sample programs, and release readiness.
- **Scribe**: owns the design documents, `SEMANTICS.md`, meeting notes, and decision log.

Every member holds every role at least once before Demo Day; the Scribe records today's rotation schedule. After class, respond to the reflective prompt individually in your notebook.

---

When a restaurant opens, the first question is not "what goes on the menu" but "who are we cooking for?" A fine-dining spot and a food truck may serve the same ingredients but make completely different choices about presentation, speed, and price. Your language works the same way: every syntax decision, every feature you include or cut, flows naturally once you have answered "who is this for?" Part I helps you find and commit to that answer before you write a single grammar rule.

# Part I: Identity

## 1. A Language Is a Point of View

**Your language needs a reason to exist beyond the assignment.** The strongest student languages pick a *niche* and let it drive decisions: a language for dice-game scripting, for turtle-style drawing, for survey logic, for recipe scaling, for music patterns, for grading rules. The niche supplies your example programs, your Demo Day story, and the tiebreaker for every design argument ("which choice serves dice players?"). General-purpose-but-tiny is also legitimate; what is not legitimate is having no answer to "who is this for?"

**Constraints (the non-negotiables).** Your language must include: variables with your documented scoping; arithmetic with full precedence; booleans, comparisons, and short-circuit logic; selection and iteration; strings or another non-numeric type; and at least one **distinctive feature** that required real design (functions with closures, pattern slices, a domain-specific statement, a desugared construct). It must be implemented on your own pipeline components, ship with a REPL and a file-runner, and include at least five sample programs.

---

Imagine two cookbooks with identical recipes but one uses bullet-point steps and the other uses dense paragraphs. The instructions are equivalent, but the experience of following them is completely different. Syntax is your language's "cookbook format" — it does not change what the program means, but it profoundly shapes how easy it is to write, read, and teach. This model puts two syntactically different versions of the same language side by side so you can measure that difference rather than just feel it.

## Model 1: Syntax Choices Make a Language Feel Like Itself

Every language has a "feel" — the texture a programmer encounters after typing thirty lines. That feel comes from small, consistent choices: what brackets wrap blocks, whether keywords or punctuation separate constructs, how the language names assignment versus equality. The cell below implements a tiny interpreter for *two syntax variants* of the same language to make the feel concrete and measurable.

```python
# Two syntax variants of the same tiny language.
# Variant A: Python-style (keyword blocks, colon, indentation)
# Variant B: C-style (brace blocks, semicolons, no colon)
# Both run the same semantics; only the surface differs.
# Team exercise: evaluate each variant on readability/writability/learnability.

PROGRAM_A = """
let x = 10
let y = 20
if x < y:
    print "x is smaller"
else:
    print "y is not larger"
while x > 0:
    x = x - 3
print x
"""

PROGRAM_B = """
let x = 10;
let y = 20;
if (x < y) {
    print "x is smaller";
} else {
    print "y is not larger";
}
while (x > 0) {
    x = x - 3;
}
print x;
"""

import re

def tokenize_simple(source, style):
    """Minimal tokenizer for the two-variant demo."""
    tokens = []
    patterns = [
        ("KW",   r'\b(?:let|if|else|while|print)\b'),
        ("ID",   r'[A-Za-z_]\w*'),
        ("NUM",  r'\d+'),
        ("STR",  r'"[^"]*"'),
        ("OP",   r'[<>!=]=|[<>=+\-*/]'),
        ("PUNC", r'[(){}\[\]:;,]'),
        ("NL",   r'\n'),
        ("WS",   r'[ \t]+'),
    ]
    master = re.compile("|".join(f"(?P<{n}>{p})" for n, p in patterns))
    for m in master.finditer(source):
        kind = m.lastgroup
        val = m.group()
        if kind not in ("WS",):
            tokens.append((kind, val))
    return tokens

toks_a = tokenize_simple(PROGRAM_A, "A")
toks_b = tokenize_simple(PROGRAM_B, "B")

print("=== Variant A token stream (Python-style) ===")
print("  " + " ".join(v for k, v in toks_a if k != "NL"))
print()
print("=== Variant B token stream (C-style) ===")
print("  " + " ".join(v for k, v in toks_b if k != "NL" and v != ";"))
print()

# Count syntactic overhead: punctuation tokens vs keyword tokens
def syntax_overhead(tokens):
    puncs = sum(1 for k, v in tokens if k == "PUNC")
    kws   = sum(1 for k, v in tokens if k == "KW")
    ids   = sum(1 for k, v in tokens if k == "ID")
    return {"punctuation": puncs, "keywords": kws, "identifiers": ids}

oa = syntax_overhead(toks_a)
ob = syntax_overhead(toks_b)
print("=== Syntactic overhead comparison ===")
print(f"  {'Metric':<15} {'A (Python)':<15} {'B (C-style)':<15}")
print(f"  {'─'*15} {'─'*15} {'─'*15}")
for key in oa:
    print(f"  {key:<15} {oa[key]:<15} {ob[key]:<15}")

print()
print("=== Niche-driven design question ===")
print("  If your niche is 'beginner scripting for middle schoolers':")
print("    → Variant A: fewer symbols to type, English-like")
print("    → Variant B: matches C/Java they will encounter next, prepares them")
print()
print("  If your niche is 'scripting for existing C++ developers':")
print("    → Variant B: familiar, zero learning overhead on syntax")
print()
print("  The right answer depends on the niche. Name your niche first.")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

> **Watch out!** "Readability" and "writability" sound like opposites but they measure *different audiences*. Readability asks "can a reader (possibly not the author) follow this code quickly?" whereas writability asks "can an author produce correct code quickly?" A language can be highly writable but hard to read — terse symbol-heavy syntax like APL is the classic example. Before answering the questions below, commit your team to which audience your niche prioritizes.

### Critical Thinking Questions

1. Draft your scorecard: for readability, writability, reliability, and cost (of implementation, your scarcest resource), one sentence on what your language prioritizes and one on what it knowingly sacrifices, *in service of the niche*.
2. Stress-test the niche: each teammate writes one program (five to ten lines, in imagined syntax) your users would actually want. Do the four sketches agree on syntax? Catalog every disagreement; each is a design decision with your team's name on it.
3. Based on the token count table: does C-style punctuation increase writability or decrease it compared to keyword-based delimiters? For which programmer audience?
4. Apply the third lens: pick the two most contested decisions from question 2 and resolve each with an explicit appeal to the scorecard, recording the loser's strongest argument in the decision log. (Decisions with recorded dissent reverse gracefully; decisions by fatigue do not.)

---

A city planner does not just dream about roads — they produce a blueprint that can be handed to a construction crew. Before your team writes a single line of interpreter code, you need the same thing: a grammar blueprint that can be handed to your parser writer. Part II walks you from a vague language idea to a concrete EBNF grammar and a complete inventory of every AST node your evaluator will need to handle.

# Part II: Grammar v0 and the Node Inventory

## 2. Write It Down or It Is Not Designed

**Grammar v0.** Produce the EBNF for your full statement set and your expression ladder, niche constructs included, in the dialect from the syntax module. Mark every place your grammar differs from the class language, because each difference is parser work, and Sprint 1 is sized by this list.

**Node inventory.** One table: every AST node, its fields, the parser rule that builds it, and the evaluator rule that consumes it. Empty cells are the sprint backlog, made visible.

**`SEMANTICS.md` v0.** Import every decision your assignments already made you document (truthiness, division by zero, scoping, loop scopes, type strictness), then add the niche feature's semantics in the same style: exhaustive, exampled, no "etc."

Think of this model as a packing checklist before a camping trip. You flip through each category — shelter, food, first aid — and tick off what you are bringing. The grammar skeleton works the same way: flip through each language feature, decide yes or no, and the skeleton generates the grammar rules you need to implement. Features you skip now do not disappear — they become explicit TODOs on your sprint backlog, which is far better than discovering a missing feature on Demo Day.


> **The runnable grammar-v0 builder is in the project guide:** [The Project Language Guide](https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374/gh-pages/_pages/Tutorials/tutorial-project-language-guide.md). Use it while drafting; today's session is for deciding *what* your language is, not generating skeletons.

## Model 3: Node Inventory — Every Node Mapped

The node inventory is the living specification of your interpreter. Every AST node class appears here with its fields, the grammar rule that emits it, and the evaluator method that handles it. Use the cell below as a template; complete the empty cells as a team.

```python
# Node inventory generator: produces a Markdown table from a node spec.
# Fill in your team's nodes, then commit this script as 'node_inventory.py'.

# Format: (NodeClass, fields, grammar_rule, evaluator_method)
# Leave evaluator_method as "TODO" until it is implemented.
NODE_INVENTORY = [
    # ── Literals ──────────────────────────────────────────────────────────────
    ("NumLit",     ["value: float"],                   "primary → NUMBER",           "eval_numlit"),
    ("StrLit",     ["value: str"],                     "primary → STRING",           "eval_strlit"),
    ("BoolLit",    ["value: bool"],                    "primary → 'true'|'false'",   "eval_boollit"),

    # ── Expressions ──────────────────────────────────────────────────────────
    ("BinOp",      ["op: str", "left: Node", "right: Node"],
                                                       "add_expr / mul_expr / compare", "eval_binop"),
    ("UnaryOp",    ["op: str", "operand: Node"],       "unary",                      "eval_unaryop"),
    ("LogicOp",    ["op: str", "left: Node", "right: Node"],
                                                       "or_expr / and_expr",         "eval_logicop"),
    ("NotOp",      ["operand: Node"],                  "not_expr",                   "eval_notop"),
    ("VarRef",     ["name: str"],                      "primary → IDENT",            "eval_varref"),
    ("Assign",     ["name: str", "value: Node"],       "let_stmt / assign_stmt",     "eval_assign"),
    ("Call",       ["callee: str", "args: list[Node]"],"primary → IDENT '(' … ')'", "eval_call"),

    # ── Statements ───────────────────────────────────────────────────────────
    ("LetStmt",    ["name: str", "init: Node"],        "let_stmt",                   "eval_letstmt"),
    ("IfStmt",     ["cond: Node", "then_: Block", "else_: Block|None"],
                                                       "if_stmt",                    "eval_ifstmt"),
    ("WhileStmt",  ["cond: Node", "body: Block"],      "while_stmt",                 "eval_whilestmt"),
    ("Block",      ["stmts: list[Node]"],              "block",                      "eval_block"),
    ("PrintStmt",  ["value: Node"],                    "print_stmt",                 "eval_printstmt"),
    ("ReturnStmt", ["value: Node|None"],               "return_stmt",                "eval_returnstmt"),
    ("FunDecl",    ["name: str", "params: list[str]", "body: Block"],
                                                       "fun_decl",                   "eval_fundecl"),
    # ── Add your niche feature node here ─────────────────────────────────────
    ("NicheNode",  ["(your fields here)"],             "(your grammar rule)",        "TODO"),
]

# Render as Markdown table
col_widths = [20, 40, 35, 22]
header = ["Node Class", "Fields", "Grammar Rule", "Evaluator Method"]
separator = ["-" * w for w in col_widths]

def row(cells):
    return "| " + " | ".join(str(c).ljust(col_widths[i]) for i, c in enumerate(cells)) + " |"

print(row(header))
print(row(separator))
for node_class, fields, grammar_rule, eval_method in NODE_INVENTORY:
    field_str = ", ".join(fields)
    status = "✓" if eval_method != "TODO" else "TODO"
    print(row([node_class, field_str[:38], grammar_rule[:33], f"{eval_method} {status}"]))

print()
todo_count = sum(1 for _, _, _, m in NODE_INVENTORY if m == "TODO")
done_count = len(NODE_INVENTORY) - todo_count
print(f"  Implemented: {done_count}/{len(NODE_INVENTORY)} nodes")
print(f"  TODO:        {todo_count}/{len(NODE_INVENTORY)} nodes  ← these are your sprint backlog")
print()
print("  Sprint 1 goal: zero TODOs for core nodes (Lit, BinOp, VarRef, Assign, If, While)")
print("  Sprint 2 goal: zero TODOs for functions and your niche feature")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

### Critical Thinking Questions

8. Count the TODO rows. Each TODO is a task. Assuming each evaluator method takes roughly 45 minutes to implement and test, estimate the total hours for Sprint 1 (core nodes only). Is this realistic for one sprint?
9. `LogicOp` is separate from `BinOp` even though `and`/`or` look like binary operators. What property of their evaluation requires a distinct node class? (Hint: what must *not* happen when the left operand is false for `and`?)
10. `Call` has `callee: str` — it stores the function *name* as a string, not the function value. What would need to change to support first-class functions (functions stored in variables and passed as arguments)? Write the new field type.

---

A ship captain does not just know the destination — they know which rocks are in the water. Part III shifts from "what will our language be" to "how will we actually build it without sinking." The sprint plan and risk pre-mortem you produce here are not bureaucracy; they are the navigational chart that keeps your team coordinated when the unexpected happens (and it will).

# Part III: The Plan

## 3. Sprints to Demo Day

The remaining weeks run in sprints aligned with in-class studio days (see the sprint studio activity for the protocols). Each sprint ends with: a runnable increment, passing tests (the Evaluator demonstrates), updated documents (the Scribe demonstrates), and the role rotation. The standard arc, adjusted to your design's risk: **Sprint 1** merges members' components into one pipeline running the class language; **Sprint 2** implements grammar v0's differences and the distinctive feature's skeleton; **Sprint 3** completes the feature, hardens errors, and builds the sample program suite; the **gallery walk** then triages polish from disclosure for **Demo Day**.

Before NASA launches a rocket, engineers hold a "failure review" — they deliberately imagine every way the mission could go wrong and build mitigations before leaving the launchpad. You have the same tool available right now, before a single line of your language's code is written. A pre-mortem is more honest than optimistic planning because it starts from failure and works backward, which forces the team to name the fears they would otherwise suppress.

## Model 4: Risk Pre-Mortem — Surface Your Threats Now

The most useful planning tool is **working backwards from failure**. Imagine it is Demo Day and your language did not work. What went wrong? The cell below simulates a risk pre-mortem session: teams identify the top threats, rank them by probability × impact, and assign a mitigation experiment.

```python
# Risk pre-mortem template.
# Fill in your team's top five risks; run to see the priority matrix.

RISKS = [
    # (description,                          probability 1-5, impact 1-5, mitigation_experiment)
    ("Merge conflict: two members' parsers clash",    4, 5, "designate one parser 'canon' on Day 1"),
    ("Niche feature too hard to parse",               3, 4, "prototype niche parser rule this week"),
    ("Evaluator semantics underdocumented",           4, 3, "complete SEMANTICS.md before any eval code"),
    ("Tests written after code (no red-green cycle)", 3, 3, "write 3 failing tests before any sprint"),
    ("Demo Day: sample programs not ready",           2, 5, "1 sample program per sprint, not all in Sprint 3"),
]

# Compute risk score = probability × impact
print("=== Risk Pre-Mortem Matrix ===")
print()
print(f"  {'Score':<6} {'P':<3} {'I':<3} {'Risk':<45} {'First Experiment'}")
print(f"  {'─'*6} {'─'*3} {'─'*3} {'─'*45} {'─'*30}")

sorted_risks = sorted(RISKS, key=lambda r: r[1]*r[2], reverse=True)
for desc, prob, impact, mitigation in sorted_risks:
    score = prob * impact
    bar = "█" * score + "░" * (25 - score)
    print(f"  {score:<6} {prob:<3} {impact:<3} {desc[:43]:<45} {mitigation[:28]}")

print()
top_risk = sorted_risks[0]
print(f"  Highest-priority risk: {top_risk[0]}")
print(f"  Mitigation this week:  {top_risk[3]}")
print()
print("  Rule: the team must retire the top risk before writing any Sprint 1 code.")
print("  A 'retirement experiment' is the smallest proof that the risk does not materialize.")
print()
print("=== Sprint 1 Commitment ===")
sprint1_goals = [
    "All members' lexers tokenize the same 10-line test program identically",
    "Designated parser handles: let, if/else, while, +/-/*//, comparisons",
    "Evaluator runs the 3 provided sample programs without crashing",
    "SEMANTICS.md covers: scoping, truthiness, division, string behavior",
    "Node inventory has zero TODOs for core nodes",
]
for i, goal in enumerate(sprint1_goals, 1):
    print(f"  {i}. {goal}")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

> **Watch out!** A risk score of probability × impact tells you *priority order*, not whether to act at all. A low-probability, high-impact risk (score 5) can be more dangerous than a moderate-probability, moderate-impact risk (score 9) if you have no mitigation for it — because when it hits, it will be catastrophic. Always read the impact column alongside the score, especially for anything with impact 5 (Demo Day failure).

### Critical Thinking Questions

11. The highest-scoring risk is merge conflict at the parser level. Why is the parser — not the lexer or evaluator — the most collision-prone component? (Think about what two team members are both editing simultaneously.)
12. "Write 3 failing tests before any sprint" is a red-green discipline. What does a *failing* test (before the code exists) prove that a passing test cannot? Why is it more valuable to write tests before the code?
13. The mitigation for "Demo Day: sample programs not ready" is "1 sample program per sprint." Rewrite this as a Definition of Done criterion: a sentence that Sprint Review will use to decide whether the sprint succeeded.

[[MC]]
The Coordinator is allocating Sprint 1 tasks. The niche feature (dice rolls) is exciting but risky. The best allocation strategy is:
- ( ) Assign the niche feature to Sprint 1 to demonstrate ambition early
- ( ) Avoid the niche feature entirely until all core features are stable
- (x) Prototype the niche feature's *parser rule only* this sprint to retire the parse risk, while keeping it out of the evaluator until Sprint 2
- ( ) Let the niche feature's complexity drive the entire sprint plan

---

## 4. Exercises (Today's Deliverables)

1. *The one-pager.* Language name, niche, the four-row scorecard, and the team's three-sentence pitch. Post it; it is the cover page of your proposal.
2. *Grammar v0 and node inventory.* As specified above, committed to the team repository with the decision log. Use the Model 2 skeleton as a starting point — edit the feature flags, run it, copy the output into your grammar file, then hand-edit the niche feature's rules.
3. *Sprint 1 plan.* The Coordinator drafts: whose lexer, whose parser, whose evaluator seed the merge (a real decision; discuss kindly), the merge order, and each member's first task with a date.
4. *Risk pre-mortem.* As a team, name the **three** technical risks most likely to derail you (the Model 4 template gives structure), rank them by probability × impact, assign the mitigation experiment for the top risk, and commit the result to your design repo as `RISKS.md`.
5. *SEMANTICS.md skeleton.* Using your prior assignment documentation, populate a `SEMANTICS.md` with at minimum: truthiness policy, division by zero policy, scoping rules (lexical or dynamic, block or function scope), variable-before-assignment behavior, and your null/absent-value policy. Each section: the rule, an example program, and the expected output.

---
**🛑 In-class work stops here.** Everything below is homework and going-deeper material — attempt the exercises before the related assignment.

## Reflection Prompt

In your notebook: you have criticized languages all semester; today you became answerable for one. Which criticism you have made of other languages do you most fear earning yourself, and what will you do before Demo Day to dodge it? Also: the node inventory has a column for "evaluator method" — every empty cell in that column is a gap between what your language promises and what it delivers. How will your team keep that gap visible rather than invisible?

---

## 5. Further Reading

- Your own assignment codebases, reread as a library you are about to depend on.
- Robert Nystrom. *Crafting Interpreters*, "The Lox Language" chapter: a master class in specifying a small language readably.
- The project specification and rubric, reread tonight with the scorecard beside it.
- Adrian Sampson. "A Big Picture of PL" (Cornell CS 6110 notes, online): a one-page map of the design space your team just entered.

---

## Going Deeper (Optional Pointers)

The core studio above stands on its own. The deep-dive appendices that used to follow it now live on the [Tutorials shelf](https://www.billmongan.com/Ursinus-CS374-Fall2026/Tutorials/) — follow whichever pointer your project or curiosity calls for.

> **Going further:** the material that used to live here — the call stack and the heap, reference counting, reference cycles, mark-and-sweep and generational collection, and what memory management means for the closures and environments in your interpreter — is covered in depth in the dedicated tutorial: [Garbage Collection — Memory Management from First Principles](https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374/gh-pages/_pages/Tutorials/tutorial-garbage-collection.md). Explore it when your project or curiosity calls for it.

> **Going further:** the material that used to live here — foreign function interfaces, calling C from Python with `ctypes`, C-compatible structs and callbacks, name mangling, and designing an `ffi(...)` primitive for your own language — now lives as the FFI appendix of [Advanced C++: Modern Memory, Templates, and the STL](https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374/gh-pages/_pages/Tutorials/tutorial-cpp-advanced.md). It backs the project's **Foreign Function Interface** extension — explore it when your project or curiosity calls for it.

> **Going further:** the compiler optimization passes that used to live here — constant folding, dead-code elimination, common subexpression elimination, inlining, and tail-call optimization — now live as an appendix of [Building a Bytecode VM for Mini](https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374/gh-pages/_pages/Tutorials/tutorial-bytecode-vm.md), and how compiled code becomes a running executable is covered in depth in [From Source to Executable: Compiling, Linking, and the ELF Format](https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374/gh-pages/_pages/Tutorials/tutorial-compiling-linking.md). The broader survey of evaluation strategies is self-study — keywords: tree-walking interpreter, continuation-passing style, bytecode VM — compare them on your own. Explore these when your project or curiosity calls for it.

> **Going further:** the complete worked path through designing and building a small language end to end (the same journey your team begins today) is covered in depth in the dedicated tutorial: [Building the Mini Language: A Complete Guide](https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374/gh-pages/_pages/Tutorials/tutorial-project-language-guide.md). The expression-tree folds, the five-paradigm "same problem, different minds" gallery, and the modules-and-namespaces material are self-study topics — keywords: catamorphism / fold, programming paradigms comparison, module systems and namespaces. Explore them when your project or curiosity calls for it.

> **Going further:** when your language works and you want the world to run it — packaging for pip and npm, and shipping a Docker image — the path is covered in depth in the dedicated guide: [Publishing Your Language — pip, npm, and Docker](https://www.billmongan.com/Ursinus-CS374-Fall2026/Tutorials/PublishingYourLanguage). Explore it as Demo Day approaches.

> **Going further:** a few former appendices are now self-study topics: live-coding pattern languages and their pattern algebra (TidalCycles and Strudel), denotational semantics and fixed-point semantics of `while`, and concurrency models (actors, channels, software transactional memory) — search those keywords when curiosity calls. Church numerals return in the Lambda Calculus activities and in [Implementing a Lambda Calculus Reducer](https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374/gh-pages/_pages/Tutorials/tutorial-lambda-calculus-reducer.md).

---

Up next: the *Closures and First-Class Functions* activity supplies the last mechanism your evaluator needs — and from here the Team Language Project's sprints carry you to Demo Day.
