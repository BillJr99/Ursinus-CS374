<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374-Fall2026/gh-pages/_pages/Activities/liascript-languagedesign.md or locally via https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374-Fall2026/gh-pages/_pages/Activities/liascript-languagedesign.md

import: https://raw.githubusercontent.com/liascript/CodeRunner/master/README.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

# Language Design Studio: Sprint 0

Programming languages are not magic handed down from on high; they are deliberate design choices made by people who had a problem to solve.  Understanding those choices matters even if you never ship a language of your own, because every time you pick up a new language, reach for a library, or decide how to structure an API, you are making the same tradeoffs language designers make.  Think of it like car mechanics: you do not need to rebuild an engine to drive, but a driver who understands what the transmission does makes better decisions on icy roads.  This activity puts you in the designer's seat so you can become a more intentional user of every tool in your toolbox.

## Learning Goals

By the end of this activity, you will be able to:

- Construct a language identity statement that identifies a target niche, a distinctive feature, and the non-negotiable implementation requirements
- Evaluate two syntax variants of the same language on the criteria of readability, writability, and learnability, citing specific syntactic evidence
- Apply the language design scorecard to score and justify design decisions for your own language project
- Define the required components of a Sprint 0 language specification: grammar sketch, node inventory, and design document outline
- Compare the consequences of at least two specific syntax design choices (e.g., keyword blocks vs. brace blocks) for both users and implementers
- Weigh pattern matching, generics, ownership, and async against one another as candidates for your own language, and defend which ones earn their place
- Write an evaluator branch with `match`/`case` and say what the exhaustiveness checker does that an if-chain cannot

The team project begins today.  With the whole pipeline behind you, capped by the Church encodings of *The Lambda Calculus, Part 2*, your team will design and implement **a programming language of your own**, assembling the lexer, parser, AST, environments, and evaluator you each built into one system with an identity, a grammar, and a Demo Day.  Today is Sprint 0, which means identity, scorecard, grammar v0, and a working plan, in this order: **what makes a language yours $\rightarrow$ the design scorecard $\rightarrow$ grammar and node inventory v0 $\rightarrow$ sprint roles and cadence**.

> **Before You Begin:** This activity assumes you can:
> - Read and write a basic recursive-descent parser and understand how grammar rules map to parsing functions
> - Explain what an AST node is and how an evaluator walks the tree to produce a result
> - Describe lexical scoping: what an environment chain is and how variable lookup traverses it
>
> If any of these feel shaky, review your lexer/parser/evaluator assignments before continuing; this activity builds directly on that vocabulary.

---

## Directions and Group Roles

From today through Demo Day, your team works in **project roles, rotated every sprint**:

- **Coordinator**: owns the sprint plan, runs stand-ups, watches scope.
- **Builder(s)**: own the code increment of the sprint.
- **Evaluator**: owns the test suite, the sample programs, and release readiness.
- **Scribe**: owns the design documents, `SEMANTICS.md`, meeting notes, and decision log.

Every member holds every role at least once before Demo Day, and the Scribe records today's rotation schedule.  After class, please respond to the reflective prompt on your own in your notebook.

> **How today runs.**  Parts I through III are the workshop and they produce today's deliverables, so protect that time first.  Part IV is the feature menu and Part V is the one feature you will almost certainly use, pattern matching on your own AST nodes; if the period runs out before them, read those two at home before you write Sprint 1's evaluator.  The extension at the end holds the models for the features we only had a paragraph for.

---

When a restaurant opens, the first question isn't what goes on the menu.  It's who are we cooking for.  A fine-dining spot and a food truck can serve the same ingredients and still make completely different choices about presentation, speed, and price.  Your language works the same way.  Every syntax decision, and every feature you include or cut, follows once you have answered who this is for.  Part I helps you find that answer and commit to it before you write a single grammar rule.

# Part I: Identity

## 1.  A Language Is a Point of View

Your language needs a reason to exist beyond the assignment.  The strongest student languages pick a *niche* and let it drive decisions: a language for dice-game scripting, for turtle-style drawing, for survey logic, for recipe scaling, for music patterns, for grading rules.  The niche supplies your example programs, your Demo Day story, and the tiebreaker for every design argument ("which choice serves dice players?").  General-purpose-but-tiny is also legitimate; what is not legitimate is having no answer to "who is this for?"

**Constraints (the non-negotiables).**  Your language must include: variables with your documented scoping; arithmetic with full precedence; booleans, comparisons, and short-circuit logic; selection and iteration; strings or another non-numeric type; and at least one **distinctive feature** that required real design (functions with closures, pattern slices, a domain-specific statement, a desugared construct).  It must be implemented on your own pipeline components, ship with a REPL and a file-runner, and include at least five sample programs.

---

Imagine two cookbooks with identical recipes but one uses bullet-point steps and the other uses dense paragraphs.  The instructions are equivalent, but the experience of following them is completely different.  Syntax is your language's "cookbook format": it does not change what the program means, but it profoundly shapes how easy it is to write, read, and teach.  This model puts two syntactically different versions of the same language side by side so you can measure that difference rather than just feel it.

## Model 1: Syntax Choices Make a Language Feel Like Itself

Every language has a "feel": the texture a programmer encounters after typing thirty lines.  That feel comes from small, consistent choices: what brackets wrap blocks, whether keywords or punctuation separate constructs, how the language names assignment versus equality.  The cell below implements a tiny interpreter for *two syntax variants* of the same language to make the feel concrete and measurable.

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
print(f"  {'-'*15} {'-'*15} {'-'*15}")
for key in oa:
    print(f"  {key:<15} {oa[key]:<15} {ob[key]:<15}")

print()
print("=== Niche-driven design question ===")
print("  If your niche is 'beginner scripting for middle schoolers':")
print("    -> Variant A: fewer symbols to type, English-like")
print("    -> Variant B: matches C/Java they will encounter next, prepares them")
print()
print("  If your niche is 'scripting for existing C++ developers':")
print("    -> Variant B: familiar, zero learning overhead on syntax")
print()
print("  The right answer depends on the niche. Name your niche first.")
```
@LIA.eval(`["main.py"]`, `none`, `python3 main.py`)

> **Watch out!**  "Readability" and "writability" sound like opposites but they measure *different audiences*.  Readability asks "can a reader (possibly not the author) follow this code quickly?" whereas writability asks "can an author produce correct code quickly?"  A language can be highly writable but hard to read; terse symbol-heavy syntax like APL is the classic example.  Before answering the questions below, commit your team to which audience your niche prioritizes.

### Reading the Code

- Both variants run the *same* semantics.  Nothing below the surface differs, which is the point: everything you argue about here is syntax, and syntax is the part users meet first.
- The token counter is a crude proxy for "syntactic overhead", and crude is fine.  It gives the team a number to argue with instead of a feeling to assert.
- Punctuation-heavy syntax is denser to write and needs closer reading; keyword-heavy syntax is more typing and more skimmable.  Neither wins outright; you are choosing which of the four criteria your language spends on.

### Try It Yourself

Write the same program three ways and let the count start the argument.

```python
VARIANTS = {
    "Python-style": """
def max(a, b):
    if a > b:
        return a
    else:
        return b
""".strip(),

    "C-style": """
fn max(a, b) {
    if (a > b) {
        return a;
    } else {
        return b;
    }
}
""".strip(),

    # TODO 1: add a third variant of YOUR team's design. Lisp-style?
    #         ML-style with `let ... in`? Ruby-style with `end`?
}

PUNCT = set("(){}[];:,.")

def measure(src):
    return (len(src),
            src.count("\n") + 1,
            sum(1 for c in src if c in PUNCT),
            len(src.replace("(", " ").replace(")", " ").split()))

print("  " + "variant".ljust(16) + "chars  lines  punct  tokens")
for name, src in VARIANTS.items():
    c, l, p, w = measure(src)
    print("  " + name.ljust(16) + str(c).rjust(5) + str(l).rjust(7)
          + str(p).rjust(7) + str(w).rjust(8))

# TODO 2: which variant carries the most punctuation per line? Which would
#         a student who has seen neither find easier to read aloud? Those
#         are two different questions and may have different answers --
#         that gap IS the readability/writability trade.

# TODO 3: count is not taste. Vote in your team on which variant you would
#         rather WRITE and which you would rather READ six weeks from now,
#         and record the split. If the two votes disagree, say which one
#         your language should serve.
```
@LIA.eval(`["main.py"]`, `none`, `python3 main.py`)

Expected output: one row per variant, with the C-style version carrying noticeably more punctuation for the same program.  That number is where your design argument starts, not where it ends.

### Critical Thinking Questions

1.  Draft your scorecard: for readability, writability, reliability, and cost (of implementation, your scarcest resource), one sentence on what your language prioritizes and one on what it knowingly sacrifices, *in service of the niche*.
2.  Stress-test the niche: each teammate writes one program (five to ten lines, in imagined syntax) your users would actually want.  Do the four sketches agree on syntax?  Catalog every disagreement; each is a design decision with your team's name on it.
3.  Based on the token count table: does C-style punctuation increase writability or decrease it compared to keyword-based delimiters?  For which programmer audience?
4.  Apply the third lens: pick the two most contested decisions from question 2 and resolve each with an explicit appeal to the scorecard, recording the loser's strongest argument in the decision log.  (Decisions with recorded dissent reverse gracefully; decisions by fatigue do not.)

---

A city planner does not just dream about roads; they produce a blueprint that can be handed to a construction crew.  Before your team writes a single line of interpreter code, you need the same thing: a grammar blueprint that can be handed to your parser writer.  Part II walks you from a vague language idea to a concrete EBNF grammar and a complete inventory of every AST node your evaluator will need to handle.

# Part II: Grammar v0 and the Node Inventory

## 2.  Write It Down or It Is Not Designed

**Grammar v0.**  Produce the EBNF for your full statement set and your expression ladder, niche constructs included, in the dialect from the syntax module.  Mark every place your grammar differs from the class language, because each difference is parser work, and Sprint 1 is sized by this list.

**Node inventory.**  One table: every AST node, its fields, the parser rule that builds it, and the evaluator rule that consumes it.  Empty cells are the sprint backlog, made visible.

**`SEMANTICS.md` v0.**  Import every decision your assignments already made you document (truthiness, division by zero, scoping, loop scopes, type strictness), then add the niche feature's semantics in the same style: exhaustive, exampled, no "etc."

Think of this model as a packing checklist before a camping trip.  You flip through each category (shelter, food, first aid) and tick off what you are bringing.  The grammar skeleton works the same way: flip through each language feature, decide yes or no, and the skeleton generates the grammar rules you need to implement.  Features you skip now do not disappear; they become explicit TODOs on your sprint backlog, which is far better than discovering a missing feature on Demo Day.


> **The runnable grammar-v0 builder is in the project guide:** [The Project Language Guide](https://www.billmongan.com/Ursinus-CS374-Fall2026/Tutorials/ProjectLanguageGuide).  Use it while drafting; today's session is for deciding *what* your language is, not generating skeletons.

## Model 3: Node Inventory, Every Node Mapped

The node inventory is the living specification of your interpreter.  Every AST node class appears here with its fields, the grammar rule that emits it, and the evaluator method that handles it.  Use the cell below as a template; complete the empty cells as a team.

```python
# Node inventory generator: produces a Markdown table from a node spec.
# Fill in your team's nodes, then commit this script as 'node_inventory.py'.

# Format: (NodeClass, fields, grammar_rule, evaluator_method)
# Leave evaluator_method as "TODO" until it is implemented.
NODE_INVENTORY = [
    # -- Literals --------------------------------------------------------------
    ("NumLit",     ["value: float"],                   "primary -> NUMBER",           "eval_numlit"),
    ("StrLit",     ["value: str"],                     "primary -> STRING",           "eval_strlit"),
    ("BoolLit",    ["value: bool"],                    "primary -> 'true'|'false'",   "eval_boollit"),

    # -- Expressions ----------------------------------------------------------
    ("BinOp",      ["op: str", "left: Node", "right: Node"],
                                                       "add_expr / mul_expr / compare", "eval_binop"),
    ("UnaryOp",    ["op: str", "operand: Node"],       "unary",                      "eval_unaryop"),
    ("LogicOp",    ["op: str", "left: Node", "right: Node"],
                                                       "or_expr / and_expr",         "eval_logicop"),
    ("NotOp",      ["operand: Node"],                  "not_expr",                   "eval_notop"),
    ("VarRef",     ["name: str"],                      "primary -> IDENT",            "eval_varref"),
    ("Assign",     ["name: str", "value: Node"],       "let_stmt / assign_stmt",     "eval_assign"),
    ("Call",       ["callee: str", "args: list[Node]"],"primary -> IDENT '(' ... ')'", "eval_call"),

    # -- Statements -----------------------------------------------------------
    ("LetStmt",    ["name: str", "init: Node"],        "let_stmt",                   "eval_letstmt"),
    ("IfStmt",     ["cond: Node", "then_: Block", "else_: Block|None"],
                                                       "if_stmt",                    "eval_ifstmt"),
    ("WhileStmt",  ["cond: Node", "body: Block"],      "while_stmt",                 "eval_whilestmt"),
    ("Block",      ["stmts: list[Node]"],              "block",                      "eval_block"),
    ("PrintStmt",  ["value: Node"],                    "print_stmt",                 "eval_printstmt"),
    ("ReturnStmt", ["value: Node|None"],               "return_stmt",                "eval_returnstmt"),
    ("FunDecl",    ["name: str", "params: list[str]", "body: Block"],
                                                       "fun_decl",                   "eval_fundecl"),
    # -- Add your niche feature node here -------------------------------------
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
    status = "OK" if eval_method != "TODO" else "TODO"
    print(row([node_class, field_str[:38], grammar_rule[:33], f"{eval_method} {status}"]))

print()
todo_count = sum(1 for _, _, _, m in NODE_INVENTORY if m == "TODO")
done_count = len(NODE_INVENTORY) - todo_count
print(f"  Implemented: {done_count}/{len(NODE_INVENTORY)} nodes")
print(f"  TODO:        {todo_count}/{len(NODE_INVENTORY)} nodes  <- these are your sprint backlog")
print()
print("  Sprint 1 goal: zero TODOs for core nodes (Lit, BinOp, VarRef, Assign, If, While)")
print("  Sprint 2 goal: zero TODOs for functions and your niche feature")
```
@LIA.eval(`["main.py"]`, `none`, `python3 main.py`)

### Reading the Code

- The inventory has one row per node and four columns: the class, its fields, the grammar rule that produces it, and the evaluator method that consumes it.  A row with `TODO` in the last column is a node your parser can build and your evaluator cannot run.
- Generating the table from a spec rather than maintaining it by hand means it cannot drift.  Regenerate after every sprint and the `TODO` count is your burndown.
- The columns are the stages of your pipeline.  A node with no grammar rule can never be produced; a node with no evaluator method can never be consumed.  Both are bugs the table shows before the code does.

### Try It Yourself

Fill the inventory with your own language, and read the gaps straight off it.

```python
# (NodeClass, fields, grammar_rule, evaluator_method)
# TODO: replace every row with YOUR team's nodes. Leave evaluator_method
#       as "TODO" for anything not yet implemented -- that is the point.
NODES = [
    ("Num",   "value: float",           "primary -> NUMBER",             "eval_num"),
    ("Var",   "name: str",              "primary -> IDENT",              "eval_var"),
    ("BinOp", "op: str, left, right",   "expr -> expr OP term",          "eval_binop"),
    ("Let",   "name: str, value, body", "stmt -> 'let' IDENT '=' expr",  "TODO"),
    ("If",    "cond, then_, else_",     "stmt -> 'if' expr block",       "TODO"),
    ("While", "cond, body",             "stmt -> 'while' expr block",    "TODO"),
    ("Call",  "fn, args",               "primary -> IDENT '(' args ')'", "TODO"),
]

HEADER = ("Node", "Fields", "Grammar rule", "Evaluator")
widths = [max(len(str(r[i])) for r in list(NODES) + [HEADER]) for i in range(4)]

def line(row):
    return "| " + " | ".join(str(c).ljust(widths[i]) for i, c in enumerate(row)) + " |"

print(line(HEADER))
print("|" + "|".join("-" * (w + 2) for w in widths) + "|")
for row in NODES:
    print(line(row))

todo = [n for n in NODES if n[3] == "TODO"]
print("\n  " + str(len(NODES) - len(todo)) + " of " + str(len(NODES))
      + " nodes are wired end to end.")
if todo:
    print("  Still to implement: " + ", ".join(n[0] for n in todo))

# TODO 1: commit this as node_inventory.py and regenerate it at the end of
#         every sprint. The TODO count is your burndown chart.

# TODO 2: add a column for "example program exercising this node". Any node
#         with no example is a node you have never actually tested.

# TODO 3: is there a node with NO grammar rule? Nothing in your parser can
#         ever build it. Delete the node or write the rule.
```
@LIA.eval(`["main.py"]`, `none`, `python3 main.py`)

Expected output: a Markdown table and a count of nodes wired end to end.  Paste the table into your design document; it is a deliverable, not a warm-up.

### Critical Thinking Questions

8.  Count the TODO rows.  Each TODO is a task.  Assuming each evaluator method takes roughly 45 minutes to implement and test, estimate the total hours for Sprint 1 (core nodes only).  Is this realistic for one sprint?
9. `LogicOp` is separate from `BinOp` even though `and`/`or` look like binary operators.  What property of their evaluation requires a distinct node class?  (Hint: what must *not* happen when the left operand is false for `and`?)
10. `Call` has `callee: str`: it stores the function *name* as a string, not the function value.  What would need to change to support first-class functions (functions stored in variables and passed as arguments)?  Write the new field type.

---

A ship captain does not just know the destination; they know which rocks are in the water.  Part III shifts from "what will our language be" to "how will we actually build it without sinking."  The sprint plan and risk pre-mortem you produce here are not bureaucracy; they are the navigational chart that keeps your team coordinated when the unexpected happens (and it will).

# Part III: The Plan

## 3.  Sprints to Demo Day

The remaining weeks run in sprints aligned with in-class studio days (see the sprint studio activity for the protocols).  Each sprint ends with: a runnable increment, passing tests (the Evaluator demonstrates), updated documents (the Scribe demonstrates), and the role rotation.  The standard arc, adjusted to your design's risk: **Sprint 1** merges members' components into one pipeline running the class language; **Sprint 2** implements grammar v0's differences and the distinctive feature's skeleton; **Sprint 3** completes the feature, hardens errors, and builds the sample program suite; the **gallery walk** then triages polish from disclosure for **Demo Day**.

Before NASA launches a rocket, engineers hold a "failure review": they deliberately imagine every way the mission could go wrong and build mitigations before leaving the launchpad.  You have the same tool available right now, before a single line of your language's code is written.  A pre-mortem is more honest than optimistic planning because it starts from failure and works backward, which forces the team to name the fears they would otherwise suppress.

## Model 4: Risk Pre-Mortem, Surface Your Threats Now

The most useful planning tool is **working backwards from failure**.  Imagine it is Demo Day and your language did not work.  What went wrong?  The cell below simulates a risk pre-mortem session: teams identify the top threats, rank them by probability × impact, and assign a mitigation experiment.

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
print(f"  {'-'*6} {'-'*3} {'-'*3} {'-'*45} {'-'*30}")

sorted_risks = sorted(RISKS, key=lambda r: r[1]*r[2], reverse=True)
for desc, prob, impact, mitigation in sorted_risks:
    score = prob * impact
    bar = "#" * score + "." * (25 - score)
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
@LIA.eval(`["main.py"]`, `none`, `python3 main.py`)

> **Watch out!**  A risk score of probability × impact tells you *priority order*, not whether to act at all.  A low-probability, high-impact risk (score 5) can be more dangerous than a moderate-probability, moderate-impact risk (score 9) if you have no mitigation for it, because when it hits, it will be catastrophic.  Always read the impact column alongside the score, especially for anything with impact 5 (Demo Day failure).

### Critical Thinking Questions

11.  The highest-scoring risk is merge conflict at the parser level.  Why is the parser (not the lexer or evaluator) the most collision-prone component?  (Think about what two team members are both editing simultaneously.)
12.  "Write 3 failing tests before any sprint" is a red-green discipline.  What does a *failing* test (before the code exists) prove that a passing test cannot?  Why is it more valuable to write tests before the code?
13.  The mitigation for "Demo Day: sample programs not ready" is "1 sample program per sprint."  Rewrite this as a Definition of Done criterion: a sentence that Sprint Review will use to decide whether the sprint succeeded.

The Coordinator is allocating Sprint 1 tasks.  The niche feature (dice rolls) is exciting but risky.  The best allocation strategy is:

[( )] Assign the niche feature to Sprint 1 to demonstrate ambition early
[( )] Avoid the niche feature entirely until all core features are stable
[(X)] Prototype the niche feature's *parser rule only* this sprint to retire the parse risk, while keeping it out of the evaluator until Sprint 2
[( )] Let the niche feature's complexity drive the entire sprint plan

---

# Part IV: Choosing Your Feature Set

> **Intuition:** Each of the four features in this part is presented through the same three-lens template: the *problem* it solves (what was painful before), the *mechanism* (the language construct that solves it), and the *cost* (what the programmer gives up to get the benefit).  As you read, keep connecting back to your own interpreter project; several of these features apply directly to the code you have already written.

## 4.  Pattern Matching: Branching on Shape

**The problem.**  Code that dissects structured data degenerates into nested ifs and field accesses.  **The mechanism.**  A `match` tests a value against *patterns* that simultaneously check shape and bind variables; Python (3.10) joined Rust, Scala, and the ML family:

```python
def describe(node):
    try:
        match node:
            case ("num", n):
                return f"the number {n}"
            case ("+", left, right):
                return f"a sum of ({describe(left)}) and ({describe(right)})"
            case ("neg", inner):
                return f"the negation of {describe(inner)}"
            case _:
                return "something unrecognized"
    except Exception as e:
        print(f"[modern:describe] {e}")
        import traceback; traceback.print_exc()
        return ""

print(describe(("+", ("num", 2), ("neg", ("num", 3)))))
```
@LIA.eval(`["main.py"]`, `none`, `python3 main.py`)

The cost and the criterion.  A new syntactic form (readability spent up front, repaid in every dissection), and questions of exhaustiveness: ML-family compilers *prove* you handled every case, a reliability win your `evaluate`'s if-chain never gets.  Notice the example: pattern matching is practically purpose-built for tree walks like yours.

## 5.  Generics: Abstraction over Types

**The problem.**  A statically typed list-of-int and list-of-string need the same code twice, or an unsafe any-type escape hatch.  **The mechanism.**  Parameterize the *type itself*: `List[T]`, `def first(items: list[T]) -> T`.  The checker verifies the code once *for all* T, and call sites stay fully checked.  **The cost and the criterion.**  Type-system complexity (Java's wildcards, variance puzzles) traded for reliability-with-reuse; dynamically typed languages get the reuse for free and the checking never.  Connect to the types module: generics exist precisely to keep static typing's early binding without its duplication.

## 6.  Ownership: Memory Safety without a Garbage Collector

**The problem.**  C frees memory manually (use-after-free, leaks, security holes); Java collects garbage at runtime (safe, but with pauses and overhead).  **The mechanism.**  Rust's third way: every value has exactly **one owner**; assignment *moves* ownership; **borrows** lend access temporarily (many readers or one writer, never both); the compiler proves at compile time that no reference outlives its value, so the program needs neither `free` nor a collector.  **The cost and the criterion.**  A famously steep learning curve ("fighting the borrow checker"): writability spent for reliability *and* performance simultaneously, which is why Rust keeps winning systems-programming converts.  Binding-time lens: Rust moved memory-correctness from runtime (GC) or never (C) to compile time.

## 7.  Async/Await: Concurrency as Syntax

**The problem.**  Programs that wait (network, disk) waste their wait, and callback-based solutions shred control flow.  **The mechanism.** `async` functions are *pausable*: `await` yields control at a wait point and resumes when the result arrives, letting one thread interleave thousands of waiting tasks; the compiler transforms your straight-line code into a state machine (a *desugaring*, industrial grade).  **The cost and the criterion.**  The "function color" problem: async functions can only be awaited from async functions, splitting the ecosystem in two; writability and performance for I/O-bound work, bought with a pervasive design constraint.

## Model 5: Three Lenses, Four Features

> **Intuition:** The three-lens template (problem / mechanism / cost) is a general framework for evaluating *any* language feature, not just the four covered here.  When you encounter a new feature in the wild (Python's walrus operator `:=`, JavaScript's optional chaining `?.`, Kotlin's coroutines) you can immediately ask these three questions to understand it.  Notice that "cost" is not always a drawback: sometimes you are deliberately spending writability to buy reliability, or spending simplicity to buy performance.  The interesting question is always *whether the trade is worth it* in your target use case.

### Critical Thinking Questions

1.  Complete the jigsaw grid as a class: for each feature, the problem, the mechanism in one sentence, the criterion served, and the criterion taxed.
2.  Run the pattern-matching cell, then rewrite *your interpreter's* `evaluate` dispatch as a `match` on node classes (`case Num(value=n):` works on your classes!).  Report: lines saved, readability verdict, and one behavior the if-chain allowed that match's structure discourages.
3.  Ownership and garbage collection are both answers to "when may memory be reclaimed?"  Place C, Java/Python, and Rust on a binding-time axis for that decision, and state each position's billion-dollar risk.
4.  Which of the four features could a *tree-walking interpreter team* plausibly implement a slice of in three weeks, and which are out of reach?  Justify with reference to which pipeline stage each feature lives in (parser? evaluator? a checker between them?).

Rust achieves memory safety without a garbage collector primarily by:

[( )] Forbidding heap allocation
[( )] Checking every pointer at runtime
[(X)] Compile-time ownership and borrowing rules that prove references cannot outlive the values they point to
[( )] Running a collector only at program exit

---

# Part V: Pattern Matching, the One You Will Reach For

## Model 6: Pattern Matching (Python 3.10+ match/case)

> **Intuition:** Before `match`, writing a tree-walking evaluator in Python meant chains of `if isinstance(node, Num):` checks, followed by manual attribute accesses (`node.value`), all nested inside each other.  With `match`, you write `case Num(value=n):` and in one line you have checked the type, extracted the field, and bound it to a local variable.  The code mirrors the structure of the data it processes, which is exactly what you want when the data *is* a tree.

Python's `match` statement (PEP 634) goes far beyond a simple switch: it matches on *structure*, destructures into bindings, supports guards, and handles class patterns.  The cell below walks through each capability with your CS374 AST as the running example.

```python
import sys

# Represent AST nodes as named tuples for clean pattern matching
from collections import namedtuple

Num   = namedtuple('Num',   ['value'])
BinOp = namedtuple('BinOp', ['op', 'left', 'right'])
Var   = namedtuple('Var',   ['name'])
Let   = namedtuple('Let',   ['name', 'value', 'body'])
If    = namedtuple('If',    ['cond', 'then', 'else_'])

def evaluate(node, env=None):
    """Tree-walking evaluator using match/case."""
    if env is None:
        env = {}
    match node:
        case Num(value=n):
            return n
        case Var(name=name):
            if name not in env:
                raise NameError(f"Unbound variable: {name}")
            return env[name]
        case BinOp(op='+', left=l, right=r):
            return evaluate(l, env) + evaluate(r, env)
        case BinOp(op='-', left=l, right=r):
            return evaluate(l, env) - evaluate(r, env)
        case BinOp(op='*', left=l, right=r):
            return evaluate(l, env) * evaluate(r, env)
        case BinOp(op='/', left=l, right=r):
            denom = evaluate(r, env)
            if denom == 0:
                raise ZeroDivisionError("division by zero in AST")
            return evaluate(l, env) / denom
        case Let(name=name, value=val, body=body):
            new_env = {**env, name: evaluate(val, env)}
            return evaluate(body, new_env)
        case If(cond=c, then=t, else_=e):
            return evaluate(t, env) if evaluate(c, env) else evaluate(e, env)
        case _:
            raise TypeError(f"Unknown node type: {type(node).__name__}")

# Test: (let x = 5 in x * x + 2)
ast1 = Let('x', Num(5), BinOp('+', BinOp('*', Var('x'), Var('x')), Num(2)))
print("let x=5 in x*x+2 =", evaluate(ast1))

# Test: if 0 then 1 else 42  (0 is falsy)
ast2 = If(Num(0), Num(1), Num(42))
print("if 0 then 1 else 42 =", evaluate(ast2))

# Test: 2 + 3 * 4  (precedence encoded in AST structure)
ast3 = BinOp('+', Num(2), BinOp('*', Num(3), Num(4)))
print("2 + (3 * 4) =", evaluate(ast3))

print()
print("--- Demonstrating exhaustiveness gap ---")
# Add a new node type NOT handled by match
Call = namedtuple('Call', ['func', 'arg'])
ast4 = Call('f', Num(1))
try:
    result = evaluate(ast4)
except TypeError as e:
    print(f"Caught: {e}")
    print("A match with no wildcard arm would be a silent no-op in Python.")
    print("ML compilers warn at compile time - Python warns only at runtime.")

print()
print("--- Guard patterns (match + if) ---")
def categorize(n):
    match n:
        case x if x < 0:
            return f"{x} is negative"
        case 0:
            return "zero"
        case x if x % 2 == 0:
            return f"{x} is positive even"
        case x:
            return f"{x} is positive odd"

for val in [-3, 0, 4, 7]:
    print(f"  categorize({val}) = {categorize(val)}")
```
@LIA.eval(`["main.py"]`, `none`, `python3 main.py`)

### Reading the Code

- Each `case` names a *shape*, not a type test followed by field access.  `case BinOp(op="+", left=l, right=r)` checks the class, checks that `op` is `"+"`, and binds `l` and `r`, in one line.
- The wildcard `case _` is the exhaustiveness escape hatch.  A language with real exhaustiveness checking (Rust, Haskell, OCaml) would *refuse to compile* a match missing a case, and would stop needing the wildcard.
- The unhandled node at the end is the demonstration: Python matches nothing, falls to `case _`, and reports it at run time.  In a checked language that would have been a compile error, which is the binding-time lens applied to control flow.

### Try It Yourself

Rewrite one dispatch from your own interpreter as a `match`, and find the case you forgot.

```python
from dataclasses import dataclass
from typing import Any

@dataclass
class Num:   value: float
@dataclass
class Var:   name: str
@dataclass
class BinOp: op: str; left: Any; right: Any
@dataclass
class Neg:   expr: Any

def evaluate_ifchain(node, env):
    if isinstance(node, Num): return node.value
    if isinstance(node, Var): return env[node.name]
    if isinstance(node, BinOp):
        l, r = evaluate_ifchain(node.left, env), evaluate_ifchain(node.right, env)
        return {"+": lambda: l+r, "-": lambda: l-r,
                "*": lambda: l*r, "/": lambda: l/r}[node.op]()
    if isinstance(node, Neg): return -evaluate_ifchain(node.expr, env)
    raise ValueError(f"unknown node {type(node).__name__}")

def evaluate_match(node, env):
    match node:
        case Num(value=v):
            return v
        case Var(name=n):
            return env[n]
        case BinOp(op="+", left=l, right=r):
            return evaluate_match(l, env) + evaluate_match(r, env)
        case BinOp(op="*", left=l, right=r):
            return evaluate_match(l, env) * evaluate_match(r, env)
        # TODO 1: add the cases for "-" and "/". Note that you now write
        #         one case per operator, where the if-chain used a dict.
        #         Which reads better? Which would you rather EXTEND?
        # TODO 2: add the Neg case.
        case _:
            raise ValueError(f"unhandled: {node!r}")

env = {"x": 3.0}
tests = [("2 + 3",     BinOp("+", Num(2), Num(3))),
         ("2 * x",     BinOp("*", Num(2), Var("x"))),
         ("10 - 4",    BinOp("-", Num(10), Num(4))),
         ("-x",        Neg(Var("x")))]

for label, tree in tests:
    got_if = evaluate_ifchain(tree, env)
    try:
        got_match = evaluate_match(tree, env)
    except ValueError as e:
        got_match = f"ERROR: {e}"
    flag = "same" if got_if == got_match else "DIFFERENT"
    print(f"  {label:8} if-chain={got_if!r:8} match={got_match!r:40} {flag}")

# TODO 3: count the lines of each version once both are complete, and say
#         which one makes it harder to FORGET a case. That is the real
#         argument for match, and it is about the checker, not the syntax.
```
@LIA.eval(`["main.py"]`, `none`, `python3 main.py`)

Expected output as written: the first two rows agree, and the last two report `DIFFERENT` because `match` has no case for them yet.  Those two rows are what an exhaustiveness checker would have told you before running.

### Critical Thinking Questions

5.  The `evaluate` function uses `case Num(value=n)` to match a namedtuple.  What does Python check to decide this pattern matches: the type, the field name, the value, or all three?  Contrast with a plain `isinstance` check.
6.  The `case _:` wildcard arm raises a `TypeError`.  Remove it and run the `Call` test.  What does Python return silently?  Explain why an ML compiler's exhaustiveness check is a stronger reliability guarantee than Python's runtime behavior.
7.  The `Let` arm creates `new_env = {**env, name: ...}`.  Why does it use a *copy* of the environment rather than mutating `env` directly?  Connect this to the distinction between static and dynamic scope.
8.  Rewrite `categorize` using `if/elif/else` chains.  Count the lines.  Then describe one pattern-match capability (structural decomposition, guard, variable binding) that the `if` version cannot express without additional code.

---

> **Watch out!**  Python's `match` does **not** enforce exhaustiveness at compile time.  If no arm matches, Python silently returns `None`; it does not raise an error.  In Rust, OCaml, and Haskell, a non-exhaustive `match` is a *compile error* or at least a warning.  This means that in Python, if you add a new AST node type and forget to add a case for it, your evaluator will silently return `None` and the bug may not surface until much later.  The `case _: raise ...` wildcard arm is your manual safety net.


## 8.  Exercises (Today's Deliverables)

1.  *The one-pager.*  Language name, niche, the four-row scorecard, and the team's three-sentence pitch.  Post it; it is the cover page of your proposal.
2.  *Grammar v0 and node inventory.*  As specified above, committed to the team repository with the decision log.  Use the Model 3 skeleton as a starting point: edit the feature flags, run it, copy the output into your grammar file, then hand-edit the niche feature's rules.
3.  *Sprint 1 plan.*  The Coordinator drafts: whose lexer, whose parser, whose evaluator seed the merge (a real decision; discuss kindly), the merge order, and each member's first task with a date.
4.  *Risk pre-mortem.*  As a team, name the **three** technical risks most likely to derail you (the Model 4 template gives structure), rank them by probability × impact, assign the mitigation experiment for the top risk, and commit the result to your design repo as `RISKS.md`.
5.  *SEMANTICS.md skeleton.*  Using your prior assignment documentation, populate a `SEMANTICS.md` with at minimum: truthiness policy, division by zero policy, scoping rules (lexical or dynamic, block or function scope), variable-before-assignment behavior, and your null/absent-value policy.  Each section: the rule, an example program, and the expected output.

---
**In-class work stops here.**  Everything below is homework and going-deeper material: attempt the exercises before the related assignment.

# Check Your Understanding

Rust achieves memory safety without a garbage collector primarily by:

[( )] Forbidding heap allocation
[( )] Checking every pointer at run time
[(X)] Compile-time ownership and borrowing rules that prove references cannot outlive the values they point to
[( )] Running a collector only at program exit

---

`match` with exhaustiveness checking is safer than an if-chain mainly because:

[(X)] The checker can prove no case was forgotten, moving that error from run time to compile time
[( )] It executes faster
[( )] It permits fewer node types
[( )] It removes the need for a wildcard case

---

A function marked `async` may only be awaited from another `async` function. This is known as:

[(X)] The function colour problem: async-ness is contagious upward through every caller
[( )] Type erasure
[( )] The borrow checker
[( )] Structural typing

---

---

Two syntax variants that run identical semantics differ only in:

[(X)] Surface form, which is nevertheless what every user of the language meets first
[( )] Their expressive power
[( )] Which programs they can run
[( )] How fast they parse

---

Counting punctuation tokens per line is useful because:

[(X)] It turns a matter of taste into a number a team can argue about, without pretending the number settles it
[( )] Fewer punctuation tokens always means a better language
[( )] It predicts parser complexity
[( )] It measures readability directly

---

In the node inventory, a row whose evaluator column reads `TODO` means:

[(X)] The parser can build that node and the evaluator cannot run it, so any program using it fails at run time
[( )] The node has not been designed yet
[( )] Its grammar rule is missing
[( )] The node is optional

---

`LogicOp` needs to be a separate node class from `BinOp` because:

[(X)] Short-circuiting means its right operand must not be evaluated unconditionally, which every `BinOp` does
[( )] It returns a boolean rather than a number
[( )] It has different precedence
[( )] It takes more than two operands

---

# Extension: The Rest of the Feature Menu

> Past the 75 minutes.  Four features got a paragraph each in class and only pattern matching got a model; these are the models for the other three, plus the Python machinery you will want while building.  Read the ones your language is actually going to use, and skip the rest until it does.

## Examples: Ownership and Async, Simulated in Python

Two of the four features cannot be shown in Python directly: Python has a garbage collector, so nothing enforces ownership, and its `async` is cooperative rather than compiler-transformed.  What you *can* do is build the rules yourself and watch them bite, which is the fastest way to feel why Rust's borrow checker rejects what it rejects.

### A Borrow Checker in Thirty Lines

```python
class Owned:
    """A value with exactly one owner. Moving invalidates the source."""
    def __init__(self, value):
        self.value = value
        self.alive  = True          # False once moved out of
        self.shared = 0             # count of outstanding & borrows
        self.mutably_borrowed = False

    def move(self):
        if not self.alive:
            raise RuntimeError("use after move: this value was already moved")
        if self.shared or self.mutably_borrowed:
            raise RuntimeError("cannot move while borrowed")
        self.alive = False
        return Owned(self.value)

    def borrow(self):               # &T : many readers allowed
        if not self.alive:
            raise RuntimeError("use after move")
        if self.mutably_borrowed:
            raise RuntimeError("cannot borrow while mutably borrowed")
        self.shared += 1
        return self.value

    def borrow_mut(self):           # &mut T : exactly one writer, no readers
        if not self.alive:
            raise RuntimeError("use after move")
        if self.shared or self.mutably_borrowed:
            raise RuntimeError("cannot mutably borrow while already borrowed")
        self.mutably_borrowed = True
        return self.value

    def release(self):
        self.shared = max(0, self.shared - 1)
        self.mutably_borrowed = False

def attempt(label, fn):
    try:
        print(f"  {label:44} -> ok, {fn()!r}")
    except RuntimeError as e:
        print(f"  {label:44} -> REJECTED: {e}")

print("=== What the rules allow ===")
a = Owned("hello")
attempt("borrow twice (two readers)",  lambda: (a.borrow(), a.borrow())[1])
a.release(); a.release()

b = Owned("world")
attempt("move, then use the NEW owner", lambda: b.move().borrow())

print("\n=== What the rules reject ===")
c = Owned("data")
c.move()
attempt("use after move",               lambda: c.borrow())

d = Owned("shared")
d.borrow()
attempt("mutable borrow while shared",  lambda: d.borrow_mut())

e = Owned("locked")
e.borrow_mut()
attempt("second mutable borrow",        lambda: e.borrow_mut())

f = Owned("pinned")
f.borrow()
attempt("move while borrowed",          lambda: f.move())

print("\nRust does all four of these checks at COMPILE time, so none of")
print("these programs would ever run. Here they raise at run time, which")
print("is precisely the binding-time difference the theory section names.")
```
@LIA.eval(`["main.py"]`, `none`, `python3 main.py`)

#### Reading the Code

- `alive`, `shared`, and `mutably_borrowed` are the entire borrow checker's state.  Rust tracks the same three facts, per value, in the compiler rather than at run time.
- The rule "many readers **or** one writer, never both" appears twice: once in `borrow` (refuse if mutably borrowed) and once in `borrow_mut` (refuse if either kind of borrow is out).  That symmetry is what prevents a reader from seeing a half-written value.
- `move` invalidates the source rather than copying it.  That single line is why Rust needs no garbage collector: at any moment exactly one name is responsible for the value, so its lifetime is a static fact.
- Everything here raises at run time.  The whole Rust argument is that the *same* checks, done at compile time, cost nothing at run time and cannot be skipped by an untested path.

### Async as Interleaving, Not Parallelism

```python
import asyncio, time

async def fetch(name, delay):
    print(f"    {name} starts")
    await asyncio.sleep(delay)          # yields control here
    print(f"    {name} done after {delay}s")
    return f"{name}-result"

async def sequential():
    t0 = time.monotonic()
    a = await fetch("A", 0.3)
    b = await fetch("B", 0.3)
    return time.monotonic() - t0, [a, b]

async def concurrent():
    t0 = time.monotonic()
    results = await asyncio.gather(fetch("A", 0.3), fetch("B", 0.3))
    return time.monotonic() - t0, results

async def main():
    print("=== Awaiting one after the other ===")
    elapsed, results = await sequential()
    print(f"  elapsed {elapsed:.2f}s  {results}")

    print("\n=== Awaiting both together ===")
    elapsed, results = await concurrent()
    print(f"  elapsed {elapsed:.2f}s  {results}")

    print("\nOne thread, two tasks. The second run is not faster because")
    print("it used two CPUs; it is faster because A's WAIT overlapped B's.")

asyncio.run(main())
```
@LIA.eval(`["main.py"]`, `none`, `python3 main.py`)

#### Reading the Code

- `await asyncio.sleep(delay)` is the pause point.  Everything before it runs, control returns to the scheduler, and the rest resumes when the sleep finishes.  That is the state machine the theory section describes, and Python builds it from the generator machinery you met in *Control Flow Semantics*.
- `sequential` takes about twice as long as `concurrent` while doing identical work.  Nothing ran in parallel; the waits overlapped.
- Only `async def` functions may `await`.  Try adding `await` inside `attempt` from the borrow-checker cell above and Python refuses at compile time.  That constraint is the "function colour" problem: async-ness is contagious upward through every caller.

---

## Model 7: Dataclasses and __post_init__

> **Intuition:** A `@dataclass` is Python's shortcut for a class whose job is primarily to hold data.  Instead of writing `__init__`, `__repr__`, and `__eq__` by hand (all of which are boilerplate that mirrors the field list you already wrote as annotations), `@dataclass` generates them for you.  The `__post_init__` hook is the place to add any validation logic that goes beyond "assign these fields": it runs after the generated `__init__`, so you can check invariants and raise errors before the object escapes into the rest of the program.

Python's `@dataclass` decorator (PEP 557) auto-generates `__init__`, `__repr__`, and `__eq__` from field annotations.  The `__post_init__` hook runs *after* the generated `__init__`, allowing validation and derived fields, a lightweight version of the invariant-checking constructors common in strongly typed languages.

```python
from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class Token:
    kind: str
    value: str
    line: int = 0
    col:  int = 0

    def __post_init__(self):
        # Invariant: kind must be one of the recognized types
        valid_kinds = {'NUM', 'ID', 'OP', 'LPAREN', 'RPAREN', 'EOF'}
        if self.kind not in valid_kinds:
            raise ValueError(f"Invalid token kind {self.kind!r}; expected one of {valid_kinds}")
        # Normalize: strip whitespace from value
        self.value = self.value.strip()

@dataclass
class ASTNode:
    """Base node, not instantiated directly."""
    pass

@dataclass
class NumNode(ASTNode):
    value: float

    def __post_init__(self):
        self.value = float(self.value)   # coerce int input to float

@dataclass
class BinOpNode(ASTNode):
    op:    str
    left:  ASTNode
    right: ASTNode

    def __post_init__(self):
        if self.op not in {'+', '-', '*', '/'}:
            raise ValueError(f"Unknown operator: {self.op!r}")

@dataclass(frozen=True)   # immutable: __hash__ is auto-generated
class Symbol:
    """An interned symbol, useful as a dict key."""
    name: str

    def __post_init__(self):
        if not self.name.isidentifier():
            raise ValueError(f"{self.name!r} is not a valid identifier")

# Demonstrate auto-generated methods
t1 = Token('NUM', '  42  ', line=3, col=7)
t2 = Token('ID',  'x',      line=3, col=10)
t3 = Token('OP',  '+',      line=3, col=12)

print("Token repr:", t1)           # __repr__ auto-generated
print("Tokens equal?", t1 == t2)   # __eq__  auto-generated
print("Value after strip:", repr(t1.value))  # __post_init__ stripped spaces

print()
ast = BinOpNode('+', NumNode(2), NumNode(3))
print("AST node:", ast)
print("Left operand:", ast.left)

print()
s1 = Symbol('x')
s2 = Symbol('x')
print("Symbol('x') == Symbol('x'):", s1 == s2)
print("Same hash (frozen=True enables this):", hash(s1) == hash(s2))
print("Can use as dict key:", {s1: 'the variable x'}[s2])

print()
print("--- Invariant violation ---")
try:
    bad = Token('UNKNOWN', 'oops')
except ValueError as e:
    print(f"Caught ValueError: {e}")

try:
    bad2 = Symbol('not-valid!')
except ValueError as e:
    print(f"Caught ValueError: {e}")

print()
print("Key insight: __post_init__ moves invariant checks to object construction,")
print("ensuring no Token or ASTNode can exist in an invalid state.")
```
@LIA.eval(`["main.py"]`, `none`, `python3 main.py`)

### Critical Thinking Questions

9. `@dataclass` generates `__init__` from the annotated fields.  What is the advantage of having the generated `__init__` call `__post_init__` rather than placing validation in a separate `validate()` method you call manually?
10. `@dataclass(frozen=True)` makes instances immutable and auto-generates `__hash__`.  Explain why mutability and hashability conflict, and name a use case in your CS374 project where an immutable, hashable AST node would be useful.
11.  The `NumNode.__post_init__` coerces `self.value` to `float`.  This is a *type coercion* at construction time.  Compare this to a statically typed language where the field type annotation would prevent a non-float from being passed at all.  Which approach is more *writable*?  Which is more *reliable*?
12.  Design a `FunctionDef` dataclass for your interpreter with fields `name`, `params` (a list of strings), and `body` (an `ASTNode`).  Write the `__post_init__` that enforces: at least one parameter, no duplicate parameter names, and `body` is actually an `ASTNode`.  Write only the class definition, not the full interpreter.

---

> **Watch out!** `@dataclass(frozen=True)` makes an instance *immutable after construction*, but it is not the same as a deeply immutable object.  If a frozen dataclass has a field that holds a mutable list, the list's contents can still change; `frozen` prevents reassignment of the field itself (`obj.field = new_value` will raise `FrozenInstanceError`), but does not prevent mutation of the object the field points to (`obj.field.append(x)` still works).  For true immutability, all fields must themselves be immutable.

## Model 8: Type Annotations, Generators, and Context Managers

> **Intuition:** This model covers three Python features that look unrelated but share a common theme: each one lets you express a program's *intent* more precisely without changing its runtime behavior.  Type annotations document the expected shapes of data.  Generators let you describe a lazy sequence without materializing it.  Context managers let you express "this block needs setup and guaranteed teardown" as a first-class construct rather than a try/finally pattern you must remember to write.  All three are about making the code's intent visible and verifiable: to other programmers, to type checkers, and to the runtime.

Python's type system, generators, and context managers are three orthogonal features that each address a distinct design concern: **static documentation**, **lazy computation**, and **resource safety**.  The cell explores all three in the context of a token stream, a structure your compiler pipeline uses.

```python
from typing import Iterator, Generator, List, Optional, TypeVar
from contextlib import contextmanager
import time

T = TypeVar('T')

# -- Type annotations --------------------------------------------------------
# Annotations do not change runtime behavior in Python, but they document
# intent and enable type-checker tools (mypy, pyright) to catch errors early.

def tokenize(source: str) -> List[tuple[str, str]]:
    """Return a flat list of (kind, value) pairs."""
    tokens: List[tuple[str, str]] = []
    i = 0
    while i < len(source):
        if source[i].isspace():
            i += 1
        elif source[i].isdigit():
            j = i
            while j < len(source) and source[j].isdigit():
                j += 1
            tokens.append(('NUM', source[i:j]))
            i = j
        elif source[i].isalpha():
            j = i
            while j < len(source) and source[j].isalnum():
                j += 1
            tokens.append(('ID', source[i:j]))
            i = j
        elif source[i] in '+-*/()':
            tokens.append(('OP', source[i]))
            i += 1
        else:
            tokens.append(('UNKNOWN', source[i]))
            i += 1
    tokens.append(('EOF', ''))
    return tokens

tokens = tokenize("2 + foo * 3")
print("Tokenize result:", tokens)
print()

# -- Generators ---------------------------------------------------------------
# A generator function uses 'yield' instead of 'return'.
# It produces values lazily - only when the caller asks for the next one.
# This is ideal for token streams: no need to materialise the whole list.

def tokenize_lazy(source: str) -> Generator[tuple[str, str], None, None]:
    """Yield tokens one at a time - O(1) memory, regardless of source length."""
    i = 0
    while i < len(source):
        if source[i].isspace():
            i += 1
            continue
        elif source[i].isdigit():
            j = i
            while j < len(source) and source[j].isdigit():
                j += 1
            yield ('NUM', source[i:j])
            i = j
        elif source[i].isalpha():
            j = i
            while j < len(source) and source[j].isalnum():
                j += 1
            yield ('ID', source[i:j])
            i = j
        elif source[i] in '+-*/()':
            yield ('OP', source[i])
            i += 1
        else:
            yield ('UNKNOWN', source[i])
            i += 1
    yield ('EOF', '')

print("Lazy tokenizer (consuming one at a time):")
gen = tokenize_lazy("x + 42")
for tok in gen:
    print(f"  next token: {tok}")
print()

# Generator as infinite stream - only possible with lazy evaluation
def integers_from(n: int) -> Generator[int, None, None]:
    while True:
        yield n
        n += 1

def take(n: int, it) -> List:
    return [next(it) for _ in range(n)]

print("First 5 integers from 10:", take(5, integers_from(10)))
print()

# -- Context managers ---------------------------------------------------------
# 'with' guarantees cleanup (the __exit__ method) even if an exception occurs.
# @contextmanager lets you write a generator-based context manager.

@contextmanager
def parse_session(source: str):
    """
    A context manager that sets up and tears down a parse session.
    Guarantees: the token stream is always closed on exit.
    """
    print(f"[session] Opening parse session for: {source!r}")
    tokens = list(tokenize_lazy(source))
    session = {'tokens': tokens, 'pos': 0, 'errors': []}
    try:
        yield session
    except Exception as e:
        session['errors'].append(str(e))
        print(f"[session] Error during parse: {e}")
    finally:
        print(f"[session] Closing session. Errors: {session['errors'] or 'none'}")
        print(f"[session] Tokens consumed: {session['pos']}/{len(tokens)}")

with parse_session("2 + 3") as s:
    print("Inside session, tokens:", s['tokens'])
    s['pos'] = len(s['tokens'])   # simulate consuming all tokens

print()
with parse_session("bad $ input") as s:
    print("Inside session with bad input")
    raise ValueError("unexpected token at position 4")
```
@LIA.eval(`["main.py"]`, `none`, `python3 main.py`)

### Critical Thinking Questions

13.  The return type annotation `Generator[tuple[str, str], None, None]` has three type parameters.  Look up what each means (yield type, send type, return type).  Why is the send type `None` for a tokenizer, and when would a non-`None` send type be useful?
14.  Compare `tokenize` (returns a list) with `tokenize_lazy` (yields tokens).  For a 1 GB source file, which is preferable and why?  Identify the specific trade-off in terms of memory usage versus random access capability.
15.  The `@contextmanager` decorator wraps a generator function with a single `yield`.  The code *before* `yield` is `__enter__`; code *after* is `__exit__`.  Rewrite `parse_session` as a class with explicit `__enter__` and `__exit__` methods.  Which form is more readable, and which is more explicit about the resource lifecycle?
16.  Python's type annotations are not enforced at runtime (without a separate checker).  Name one scenario in your CS374 project where a type error that annotations would expose at type-check time actually caused a runtime bug during testing.  If you cannot recall one, invent a plausible example involving mismatched AST node types.

---

## Exercises

1.  *Feature pitch.*  Each pair writes a half-page pitch for adding their jigsaw feature (or a realistic slice of it) to the team language: the construct's syntax in your grammar's EBNF, the node it adds, the evaluator rule, and the criterion it serves.  The team votes one pitch onto the project's "stretch goals" list.
2.  *Exhaustiveness by hand.*  Add a new node type to your AST but not to your match-based evaluate.  Run it; read the failure.  Now add a `case _:` that raises a located error listing the node type.  You have hand-built the safety net ML compilers automate; one sentence on the difference.
3.  *Color audit.*  Sketch (no implementation) what adding async to your language would split: which built-ins become awaitable, which functions change color, what the REPL does with a pending value.  Conclude with a recommendation and its rationale.
4.  *Feature archaeology.*  Each teammate picks one feature that *arrived* in a mainstream language during their lifetime (Python match 2021, Java records 2020, JS async 2017, C++ lambdas 2011) and reports the proposal document's stated motivation versus what we identified today.

---

---

### Check Yourself on the Simulations

In the borrow checker, `borrow_mut` refuses when `shared > 0`. What would break if it allowed it?

[(X)] A reader could observe the value halfway through being written
[( )] The value would be freed twice
[( )] The move counter would overflow
[( )] Nothing; Rust actually permits this

---

The async simulation's concurrent run finishes in half the time of the sequential one. That is because:

[(X)] One task's waiting overlapped the other's; nothing ran on a second CPU
[( )] `asyncio.gather` spawns a thread per task
[( )] `asyncio.sleep` is faster than `time.sleep`
[( )] The second run reused the first run's cached results

---

## Reflection Prompt

In your notebook: you have criticized languages all semester; today you became answerable for one.  Which criticism you have made of other languages do you most fear earning yourself, and what will you do before Demo Day to dodge it?  Also: the node inventory has a column for "evaluator method": every empty cell in that column is a gap between what your language promises and what it delivers.  How will your team keep that gap visible rather than invisible?

---

## 9.  Further Reading

- The Rust Book, chapter 4 (ownership): https://doc.rust-lang.org/book/
- PEP 634 through 636 (Python structural pattern matching), especially 636, the tutorial.
- Bob Nystrom.  "What Color is Your Function?"  (online essay), the async critique, vividly argued.
- [Team Language Project Extensions Menu](https://www.billmongan.com/Ursinus-CS374-Fall2026/Projects/TeamLanguage): its Macros or Hygienic Quoting entry specifies exactly what a credited macro extension must do, covering C-style textual macros and their double-evaluation hazards, quasiquotation, and hygienic expansion.  [Building the Mini Language](https://www.billmongan.com/Ursinus-CS374-Fall2026/Tutorials/ProjectLanguageGuide) is the interpreter foundation to build it on.
- Objects and OOP from closures to vtables, method resolution order and the diamond problem, abstract base classes, and how vtables implement dynamic dispatch: the Python data-model docs, plus "C3 linearization" and "Python MRO".
- The expression problem: why adding new node types is easy in OOP and adding new operations is easy in functional style, and never both.  The design tension behind your evaluator; search "expression problem Wadler" and revisit it when your team debates visitor versus match.

---

- Your own assignment codebases, reread as a library you are about to depend on.
- Robert Nystrom.  *Crafting Interpreters*, "The Lox Language" chapter: a master class in specifying a small language readably.
- The project specification and rubric, reread tonight with the scorecard beside it.
- Adrian Sampson.  "A Big Picture of PL" (Cornell CS 6110 notes, online): a one-page map of the design space your team just entered.
- [Garbage Collection: Memory Management from First Principles](https://www.billmongan.com/Ursinus-CS374-Fall2026/Tutorials/GarbageCollection): the call stack and the heap, reference counting, reference cycles, mark-and-sweep and generational collection, and what memory management means for the closures and environments in your interpreter.
- [Advanced C++: Modern Memory, Templates, and the STL](https://www.billmongan.com/Ursinus-CS374-Fall2026/Tutorials/AdvancedCpp): its FFI appendix covers foreign function interfaces, calling C from Python with `ctypes`, C-compatible structs and callbacks, name mangling, and designing an `ffi(...)` primitive for your own language.  Backs the project's Foreign Function Interface extension.
- [Building a Bytecode VM for Mini](https://www.billmongan.com/Ursinus-CS374-Fall2026/Tutorials/BytecodeVM): its optimization appendix covers constant folding, dead-code elimination, common subexpression elimination, inlining, and tail-call optimization.
- [From Source to Executable: Compiling, Linking, and the ELF Format](https://www.billmongan.com/Ursinus-CS374-Fall2026/Tutorials/CompilingAndLinking): how compiled code becomes a running executable.
- [Building the Mini Language: A Complete Guide](https://www.billmongan.com/Ursinus-CS374-Fall2026/Tutorials/ProjectLanguageGuide): a complete worked path through designing and building a small language end to end, the same journey your team begins today.
- [Publishing Your Language: pip, npm, and Docker](https://www.billmongan.com/Ursinus-CS374-Fall2026/Tutorials/PublishingYourLanguage): packaging your language and shipping a Docker image, for when it works and you want the world to run it.
- Self-study topics: expression-tree folds (catamorphisms), module systems and namespaces, live-coding pattern languages and their pattern algebra (TidalCycles and Strudel), denotational and fixed-point semantics of `while`, and concurrency models (actors, channels, software transactional memory).

---

Up next: the *Closures and First-Class Functions* activity supplies the last mechanism your evaluator needs, and from here the Team Language Project's sprints carry you to Demo Day.  Come back to the feature menu at the end of each sprint: the honest question is not which features are exciting, it is which ones you have time to implement well.
