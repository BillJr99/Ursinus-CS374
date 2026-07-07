<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://github.com/BillJr99/Ursinus-CS374-Fall2026/blob/gh-pages/_pages/Activities/liascript-languagedesign.md or locally via https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374-Fall2026/gh-pages/_pages/Activities/liascript-languagedesign.md

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

The team project begins today: your team will design and implement **a programming language of your own**, assembling the lexer, parser, AST, environments, and evaluator you each built into one system with an identity, a grammar, and a Demo Day. Today is Sprint 0: identity, scorecard, grammar v0, and a working plan. The arc: **what makes a language yours $\rightarrow$ the design scorecard $\rightarrow$ grammar and node inventory v0 $\rightarrow$ sprint roles and cadence**.

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

## Model 2: Grammar v0 Starter — Feature Checklist

The cell below walks through a feature checklist and emits a starter grammar in EBNF. Your team modifies it; the point is to make sure no feature is forgotten.

```python
# Grammar v0 feature checklist + EBNF skeleton generator.
# Edit the feature flags to match your team's decisions, then run.

# ── Feature flags ─────────────────────────────────────────────────────────────
FEATURES = {
    # Core (required)
    "variables":        True,   # let x = expr
    "arithmetic":       True,   # + - * / with precedence
    "booleans":         True,   # true, false, and/or/not
    "comparisons":      True,   # < <= > >= == !=
    "short_circuit":    True,   # and/or lazy
    "selection":        True,   # if/else
    "iteration":        True,   # while loop
    "strings":          True,   # "hello" string type

    # Optional (mark True if your team is adding them)
    "functions":        True,   # fun f(x) { ... }
    "return":           True,   # return expr
    "for_loop":         False,  # for x in list { ... }
    "lists":            False,  # [1, 2, 3]
    "dicts":            False,  # {key: value}
    "closures":         False,  # functions capturing outer vars
    "classes":          False,  # class Foo { ... }
    "pattern_match":    False,  # match expr { ... }
    "niche_feature":    True,   # YOUR DISTINCTIVE FEATURE (name it below!)

    # Niche feature name and description (edit these):
    "_niche_name":      "dice_roll",       # e.g., "dice_roll", "turtle_move"
    "_niche_desc":      "3d6 → roll 3 six-sided dice and sum",
}

# ── EBNF skeleton builder ─────────────────────────────────────────────────────

def emit_grammar(f):
    lines = [
        "program   ::= statement* EOF",
        "",
        "statement ::= let_stmt",
        "            | if_stmt",
    ]
    if f["iteration"]:
        lines.append("            | while_stmt")
    if f["for_loop"]:
        lines.append("            | for_stmt")
    if f["functions"]:
        lines.append("            | fun_decl")
    if f["return"]:
        lines.append("            | return_stmt")
    if f["classes"]:
        lines.append("            | class_decl")
    if f["niche_feature"]:
        lines.append(f"            | {f['_niche_name']}_stmt")
    lines.append("            | expr_stmt")
    lines.append("")

    lines.append("let_stmt  ::= 'let' IDENT '=' expr ';'")
    lines.append("if_stmt   ::= 'if' '(' expr ')' block ( 'else' block )?")
    if f["iteration"]:
        lines.append("while_stmt ::= 'while' '(' expr ')' block")
    if f["for_loop"]:
        lines.append("for_stmt  ::= 'for' IDENT 'in' expr block")
    if f["functions"]:
        lines.append("fun_decl  ::= 'fun' IDENT '(' params ')' block")
        lines.append("params    ::= ( IDENT ( ',' IDENT )* )?")
    if f["return"]:
        lines.append("return_stmt ::= 'return' expr? ';'")
    if f["niche_feature"]:
        lines.append(f"  (* {f['_niche_name']}: {f['_niche_desc']} *)")
    lines.append("expr_stmt ::= expr ';'")
    lines.append("block     ::= '{' statement* '}'")
    lines.append("")

    # Expression ladder (precedence, lowest to highest)
    lines.append("(* Expression ladder — lower rules bind more loosely *)")
    lines.append("expr      ::= or_expr")
    if f["short_circuit"]:
        lines.append("or_expr   ::= and_expr ( 'or' and_expr )*")
        lines.append("and_expr  ::= not_expr ( 'and' not_expr )*")
        lines.append("not_expr  ::= 'not' not_expr | compare")
    if f["comparisons"]:
        lines.append("compare   ::= add_expr ( ( '<' | '<=' | '>' | '>=' | '==' | '!=' ) add_expr )?")
    lines.append("add_expr  ::= mul_expr ( ( '+' | '-' ) mul_expr )*")
    lines.append("mul_expr  ::= unary   ( ( '*' | '/' ) unary   )*")
    lines.append("unary     ::= '-' unary | primary")
    lines.append("")

    # Primary forms
    primaries = ["NUMBER", "STRING", "IDENT", "'(' expr ')'"]
    if f["booleans"]:
        primaries = ["'true'", "'false'"] + primaries
    if f["lists"]:
        primaries.append("'[' ( expr ( ',' expr )* )? ']'")
    if f["dicts"]:
        primaries.append("'{' ( expr ':' expr ( ',' expr ':' expr )* )? '}'")
    if f["functions"] or f["closures"]:
        primaries.append("IDENT '(' ( expr ( ',' expr )* )? ')'")
    if f["niche_feature"]:
        primaries.append(f"(* {f['_niche_name']}: add your primary form here *)")
    lines.append("primary   ::= " + ("\n            | ").join(primaries))

    return "\n".join(lines)

grammar = emit_grammar(FEATURES)
print("=== Grammar v0 Skeleton ===")
print(grammar)

print()
print("=== Feature Summary ===")
core_on    = [k for k,v in FEATURES.items() if v is True and not k.startswith("_") and k in ["variables","arithmetic","booleans","comparisons","short_circuit","selection","iteration","strings"]]
optional_on = [k for k,v in FEATURES.items() if v is True and not k.startswith("_") and k not in core_on]
optional_off = [k for k,v in FEATURES.items() if v is False and not k.startswith("_")]
print(f"  Core features ({len(core_on)}): {', '.join(core_on)}")
print(f"  Optional ON  ({len(optional_on)}): {', '.join(optional_on)}")
print(f"  Optional OFF ({len(optional_off)}): {', '.join(optional_off)}")
print()
print("  To add a feature: set the flag to True and add its grammar rule.")
print("  Each True flag = at minimum one new grammar rule + one new AST node.")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

> **Watch out!** Adding a feature flag to `True` in the skeleton does not implement the feature — it only declares intent. The real cost shows up in two places: (1) every new grammar rule becomes a new parsing function your Builder must write and test, and (2) every new grammar rule introduces at least one new AST node that your Evaluator must handle. Teams commonly underestimate Sprint 1 scope by counting features rather than counting grammar rules plus AST nodes.

### Critical Thinking Questions

5. Set `functions = True` and run. Count how many new grammar rules appear. Each new rule is a parser function your Builder must write. How does this inform Sprint 1's scope estimate?
6. The niche feature `dice_roll` appears in both `statement` and `primary`. Is `3d6` a statement (roll and discard), an expression (roll and use the value), or both? How should the grammar reflect this distinction?
7. The expression ladder encodes precedence by nesting: `or_expr` calls `and_expr` which calls `not_expr`. Add `**` (exponentiation) to the ladder with higher precedence than `*`. Write the new rule and its position in the ladder.

[[MC]]
A team's niche is dice-game scripting, and they are debating whether `3d6` should be core syntax (a lexer token and AST node) or a library function `roll(3, 6)`. The scorecard-driven way to decide is:
- ( ) Core syntax, because it is more impressive at Demo Day
- ( ) A function, because lexer changes are risky
- (x) Ask which choice best serves the niche's readability and writability, then weigh it against the implementation cost row of the scorecard
- ( ) Defer the decision until the final sprint

---

A hospital keeps a patient chart that tracks every procedure, every medication, every result. Without it, different doctors treating the same patient would have no shared source of truth. Your node inventory is that chart for your interpreter: every AST node your team agrees on becomes a row, and empty cells in the "evaluator method" column show exactly where the implementation is incomplete. This model generates a starter inventory — your job is to fill in the blank rows before Sprint 1 ends.

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

## Reflection Prompt

In your notebook: you have criticized languages all semester; today you became answerable for one. Which criticism you have made of other languages do you most fear earning yourself, and what will you do in the next two weeks to dodge it? Also: the node inventory has a column for "evaluator method" — every empty cell in that column is a gap between what your language promises and what it delivers. How will your team keep that gap visible rather than invisible?

---

## 5. Further Reading

- Your own assignment codebases, reread as a library you are about to depend on.
- Robert Nystrom. *Crafting Interpreters*, "The Lox Language" chapter: a master class in specifying a small language readably.
- The project specification and rubric, reread tonight with the scorecard beside it.
- Adrian Sampson. "A Big Picture of PL" (Cornell CS 6110 notes, online): a one-page map of the design space your team just entered.

---

## Going Deeper: Languages for Live Coding Music: Strudel and TidalCycles

Music is time made audible, and writing a language for music means designing a language whose fundamental data type is time itself. TidalCycles and Strudel make that design choice explicit: a pattern is literally a function that takes a time interval and returns the events scheduled within it. Studying these languages is studying DSL design at its most honest — every syntax decision is traceable to a constraint from live performance, and every semantic choice flows from the mathematics of cyclic time.

#### Learning Goals

By the end of this activity, you will be able to:

- Distinguish embedded DSLs from external DSLs and explain the design tradeoffs that led TidalCycles and Strudel to use a hybrid of both
- Identify how live coding's domain requirements (conciseness, modifiability at runtime, declarative time, recoverable errors) drive specific language design decisions
- Define the denotational model of a pattern as a function from time to values and trace how combinators compose patterns algebraically
- Analyze the mini-notation grammar of Strudel/TidalCycles and explain how parsing it requires a separate external language within the host language
- Evaluate how DSL design choices generalize beyond music to configuration languages, query builders, and infrastructure description languages

> **Before You Begin:** This activity assumes you can:
> - Explain what a domain-specific language (DSL) is and give one example distinct from TidalCycles
> - Read and write Python functions that return other functions (closures)
> - Describe what a recursive descent parser does at a high level
>
> If any of these feel shaky, review them first.

This module introduces **domain-specific languages (DSLs)** through two living, performing specimens: **TidalCycles**, a pattern language embedded in Haskell, and **Strudel**, its JavaScript-hosted sibling that runs in any browser. We move from **the live coding problem domain $\rightarrow$ embedded versus external DSL design $\rightarrow$ a formal model of patterns as functions of time $\rightarrow$ combinators and their algebraic laws $\rightarrow$ hands-on performance**, and in doing so we assemble the conceptual vocabulary, syntax versus semantics, host language leverage, denotation, and equational reasoning, that the rest of this unit will exercise when we build a parser for these languages ourselves.

---

#### 0. Environment & Utilities

This module requires only a web browser. Strudel runs entirely client-side at [strudel.cc](https://strudel.cc), with no installation or account; open it now in a second tab, because you will be asked to play with it throughout. The code cell below confirms that the JavaScript fragments we study are syntactically ordinary JavaScript, which is itself one of the module's central points.

---

#### Code Cell

```javascript
// Strudel expressions are ordinary JavaScript expressions: method
// chains over pattern objects. This cell only demonstrates the shape;
// the audio engine lives at strudel.cc.

const description = 'sound("bd sn [hh hh] sn")';
console.log("A Strudel program is a JS expression, e.g.:", description);
console.log("Environment ready.");
```

---

### Part I: The Problem Domain and Two Language Designs

#### 1. Live Coding as a Language Design Problem

Before studying the technical architecture, read the performance constraints as a requirements document. A live coding environment is like a cockpit instrument panel being redesigned mid-flight: every design choice must either support the pilot while flying or not require them to land. Keep these constraints in mind as you encounter each language feature — each one is answering a specific requirement from this list.

**Live coding is the practice of writing and rewriting a running program as a public performance.** A performer projects their editor, the audience watches the code change, and the music changes with it. This domain imposes unusual and instructive requirements on a programming language, and reading those requirements as a language designer would is our first exercise in this module. The program must be **concise**, because every keystroke happens on stage; it must be **modifiable while running**, because stopping the program stops the music; it must be **declarative about time**, because the performer thinks in cycles and beats rather than in callbacks and timestamps; and its errors must be **recoverable**, because a syntax error during a performance should not produce silence.

**TidalCycles and Strudel answer these requirements with the same core design.** TidalCycles, created by Alex McLean, is a library of pattern operations embedded in **Haskell**; Strudel, created by Felix Roos with McLean, reimplements the same pattern model in **JavaScript** so that it runs in a browser with zero installation. Both share a second, smaller language inside themselves: the **mini-notation**, the quoted string language of patterns like `"bd sn [hh hh] sn"`, which we will give a grammar and a parser of our own in the next module. One pattern model, two host languages, one shared inner notation: this triangle is the cleanest case study of DSL architecture you are likely to encounter, and it is why a music language has a home in a principles of programming languages course.

---

#### 2. Embedded Versus External DSLs

**An external DSL has its own syntax, lexer, and parser; an embedded DSL borrows all three from a host language.** SQL, regular expressions, and `make` are external: nothing about their syntax is Java or C. An embedded DSL (EDSL) is instead a library designed so artfully that using it feels like writing a new language, while every expression remains a legal host-language expression, parsed by the host's parser and checked by the host's type system.

**Tidal and Strudel are hybrids, and the hybrid is the lesson.** The combinator layer is embedded: `every 4 (fast 2) $ sound "bd sn"` is a legal Haskell expression, and `sound("bd sn").every(4, x => x.fast(2))` is legal JavaScript. The mini-notation layer is external: the string `"bd sn"` is opaque to Haskell and JavaScript alike, and each system ships a hand-built parser for it. The designers chose an external inner language precisely where host syntax would be too noisy, writing a drum pattern as a Haskell list of constructors would be unbearable on stage, and an embedded outer language precisely where the host's powers, higher-order functions, types, and a mature toolchain, are too valuable to give up.

**The tradeoffs generalize far beyond music.** Within the scope of the DSLs you will meet professionally, configuration languages, query builders, infrastructure description languages, the same forces recur:

| Axis | Embedded DSL | External DSL |
|------|--------------|--------------|
| Implementation cost | Low: a library | High: lexer, parser, tooling |
| Syntax freedom | Constrained by host grammar | Unlimited |
| Error messages | Host's, often confusing | Custom, can be excellent |
| Host interop | Free and total | Requires explicit bridges |
| Static checking | Inherited from host types | Must be built by hand |

[[MC]]
Strudel's designers parse `"bd sn [hh hh]"` with a dedicated parser rather than asking performers to write a JavaScript array of objects. Which DSL design consideration most directly justifies that choice?
- (x) Syntax freedom: the domain demands a notation more concise than host-language syntax permits, which is the classic argument for an external DSL layer.
- ( ) Implementation cost: external parsers are cheaper to build than JavaScript libraries.
- ( ) Static checking: strings receive stronger type checking than JavaScript objects.
- ( ) Host interop: strings cannot be passed to JavaScript functions, so a parser is mandatory.

---

##### Try It: With a Partner

One partner argues for an **embedded** design and the other for an **external** design of the following hypothetical DSL: a language for describing amateur radio antenna geometries (element lengths, spacings, and feed points) to be consumed by a simulation engine. Take four minutes per side, using the table above as your scorecard, then jointly write a two-sentence recommendation and identify which single axis dominated your decision. Be prepared to report out; different teams legitimately reach different conclusions, and the quality of the argument, not the verdict, is what we will discuss.

---

### Part II: A Formal Model of Patterns

#### 3. Patterns as Functions of Time

**The central abstraction of both languages is that a pattern is a function from a span of time to the events occurring within it.** Time is measured in **cycles**, with one cycle conventionally spanning the rational interval $[0, 1)$, the next $[1, 2)$, and so on. Writing $\mathbb{Q}$ for the rationals, a span is a pair $(b, e)$ with $b \leq e$, an event is a value paired with the span it occupies, and a pattern of values of type $a$ is, to a first approximation,

$$
\text{Pattern}\ a \;\approx\; (b, e) \mapsto \{\, (v_i,\, b_i,\, e_i) \,\} \quad \text{with each } [b_i, e_i) \subseteq \text{the queried span}
$$

In Tidal's Haskell source this is nearly literal: a `Pattern a` wraps a query function from a timespan (Tidal calls it an arc) to a list of events. The consequences of choosing **function of time** rather than **list of notes** as the denotation are profound, and each one answers a requirement from Section 1. Patterns are infinite, since you may query cycle 10,000 as easily as cycle 0, yet they occupy constant memory, because nothing is stored, only computed on demand. Patterns are pure values, so transforming one produces a new pattern without mutating a running performance, which is what makes mid-performance code replacement safe. And patterns compose, because functions compose.

**A worked query.** Take the pattern denoted by `"bd sn"` and query the span $[0, 1)$. The sequence rule divides the span evenly, yielding the event set

$$
\{\ (\texttt{bd},\ 0,\ \tfrac{1}{2}),\quad (\texttt{sn},\ \tfrac{1}{2},\ 1)\ \}
$$

Query the same pattern on $[1, 2)$ and you receive the same shape shifted by one cycle, because the pattern is cycle-periodic unless an operator says otherwise. We will implement precisely this query function, in Python against our own parser's AST in the next module, and the displayed set above is the test case you should carry with you.

---

#### Model 1: Pattern-as-Function in Python

The central insight is that a pattern is not a list — it is a function. This means patterns are naturally infinite (you can query any future cycle), composable (functions compose), and pure (transforming a pattern produces a new pattern without mutating the old one). This model translates that mathematical abstraction directly into Python using closures. Notice that `pure`, `seq`, `fast`, and the others all return functions, not data.

> **Watch out!** `pure("bd")` returns a function, not a string. You must call the returned function with a time span — e.g., `pure("bd")(0, 1)` — to get actual events. Forgetting the second call and printing the function object itself is a very common first mistake.

The cell below implements the core pattern model in Python: `pure`, `seq`, `fast`, `slow`, `rev`, and `stack` (polyrhythm). This is not audio — it is the mathematical substrate under the audio. Every event is a `(value, begin, end)` tuple; every function that returns a pattern returns a *function* from `(begin, end)` to a list of events.

```python
from fractions import Fraction

# An event is (value, begin: Fraction, end: Fraction)
def event(v, b, e):
    return (v, Fraction(b), Fraction(e))

def pure(v):
    """A pattern that emits v once per cycle, occupying the whole cycle."""
    def query(b, e):
        b, e = Fraction(b), Fraction(e)
        events = []
        c = int(b) if b == int(b) else int(b)
        while c < e:
            if Fraction(c) >= b or c == int(b):
                events.append(event(v, max(b, Fraction(c)), min(e, Fraction(c+1))))
            c += 1
        return events
    return query

def seq(*pats):
    """Divide one cycle evenly among the given patterns."""
    n = len(pats)
    def query(b, e):
        b, e = Fraction(b), Fraction(e)
        result = []
        for cycle_start in range(int(b), int(e) + 1):
            for i, p in enumerate(pats):
                slot_b = Fraction(cycle_start) + Fraction(i, n)
                slot_e = Fraction(cycle_start) + Fraction(i + 1, n)
                if slot_e <= b or slot_b >= e:
                    continue
                # Query sub-pattern in [0,1), then scale into slot
                sub_events = p(0, 1)
                for (v, sb, se) in sub_events:
                    eb = slot_b + sb / n * n   # scale back
                    ee = slot_b + se / n * n
                    eb = slot_b + sb * Fraction(1, n) * n
                    ee = slot_b + se * Fraction(1, n) * n
                    # Correct: slot occupies 1/n of a cycle; sub spans are in [0,1]
                    abs_b = slot_b + sb * Fraction(1, n)
                    abs_e = slot_b + se * Fraction(1, n)
                    if abs_e > b and abs_b < e:
                        result.append(event(v, max(abs_b, b), min(abs_e, e)))
        return result
    return query

def fast(n, pat):
    """Compress n cycles of pat into one cycle."""
    n = Fraction(n)
    def query(b, e):
        return [(v, sb / n, se / n) for (v, sb, se) in pat(b * n, e * n)]
    return query

def slow(n, pat):
    """Stretch pat across n cycles."""
    n = Fraction(n)
    def query(b, e):
        return [(v, sb * n, se * n) for (v, sb, se) in pat(b / n, e / n)]
    return query

def rev(pat):
    """Reverse the events within each cycle."""
    def query(b, e):
        b, e = Fraction(b), Fraction(e)
        result = []
        for (v, sb, se) in pat(b, e):
            # Mirror within its containing cycle
            cycle = int(sb)
            new_b = Fraction(cycle + 1) - se + Fraction(cycle)
            new_e = Fraction(cycle + 1) - sb + Fraction(cycle)
            result.append(event(v, new_b, new_e))
        return result
    return query

def stack(*pats):
    """Play patterns simultaneously (polyrhythm)."""
    def query(b, e):
        result = []
        for p in pats:
            result.extend(p(b, e))
        return sorted(result, key=lambda ev: ev[1])
    return query

# ── Tests ─────────────────────────────────────────────────────────────────────

def fmt(events):
    return [(v, float(b), float(e)) for v, b, e in events]

def show(name, events):
    print(f"  {name}")
    for v, b, e in sorted(events, key=lambda x: x[1]):
        bar = "  " + "─" * int(b * 32) + "▮" * max(1, int((e - b) * 32)) + "─" * (32 - int(e * 32))
        print(f"    ({v!r:<6} {float(b):.4f}–{float(e):.4f}){bar}")

print("=== Query: pure('bd') on [0,1) ===")
show("pure('bd')", pure("bd")(0, 1))

print()
print("=== Query: seq(pure('bd'), pure('sn')) on [0,1) ===")
p = seq(pure("bd"), pure("sn"))
show("seq bd sn", p(0, 1))

print()
print("=== Query: seq bd sn on [1,2) (should be same shape +1 cycle) ===")
show("seq bd sn [1,2)", p(1, 2))

print()
print("=== Query: fast(2, seq('bd','sn')) — double speed ===")
fast_p = fast(2, seq(pure("bd"), pure("sn")))
show("fast 2 (seq bd sn)", fast_p(0, 1))

print()
print("=== Query: stack(pure('bd'), pure('hh')) — polyrhythm ===")
poly = stack(pure("bd"), pure("hh"))
show("stack bd hh", poly(0, 1))
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

##### Critical Thinking Questions

1. `pure("bd")` returns a *function*, not a list. What property of this design allows patterns to be infinite (spanning any number of cycles) while consuming constant memory?
2. Trace `seq(pure("bd"), pure("sn"))(0, 1)` by hand: what fraction of the cycle does each event occupy? Confirm against the cell output.
3. `fast(2, p)` replays `p` twice per cycle by querying `p(2b, 2e)`. What query would `slow(3, p)` send to `p`? Write the implementation using the same technique.
4. The `rev` combinator mirrors events within each cycle. Write the algebraic law `rev(rev(p)) = p` in terms of the query function, then test it on `seq(pure("bd"), pure("sn"))` by running both and confirming the events match.

---

#### 4. Combinators and Their Laws

**A combinator is a function that builds patterns from patterns, and the important ones obey algebraic laws.** The core transformations in both languages include `fast n` (compress $n$ repetitions into each cycle), `slow n` (stretch across $n$ cycles), `rev` (reverse each cycle), and `every n f` (apply the transformation $f$ on every $n$th cycle only). Because patterns are pure functions, these combinators satisfy equations we can state and test, and equational reasoning about programs is a skill this course returns to repeatedly:

$$
\texttt{fast}\ m\ (\texttt{fast}\ n\ p) \;=\; \texttt{fast}\ (m \cdot n)\ p
\qquad\quad
\texttt{rev}\ (\texttt{rev}\ p) \;=\; p
$$

$$
\texttt{fast}\ n\ (\texttt{slow}\ n\ p) \;=\; p \qquad \text{for } n \neq 0
$$

**Currying is not a curiosity here; it is the performance interface.** In the Haskell expression `every 4 (fast 2) $ sound "bd sn"`, the subexpression `fast 2` is a **partial application**: `fast` has type `Pattern Time -> Pattern a -> Pattern a`, and supplying only the factor yields a function `Pattern a -> Pattern a`, exactly the shape `every` demands for its second argument. A Tidal performance is, syntactically, a stream of partially applied functions being composed live. Strudel, hosted in a language without curried-by-default functions, expresses the same idea with an explicit arrow: `.every(4, x => x.fast(2))`. Same denotation, different host idiom; when we study the lambda calculus in this unit's third module, you will see that the two are formally interchangeable, since currying is itself a lambda-calculus transformation.

[[MC]]
In `every 4 (fast 2) $ sound "bd sn"`, the Haskell type checker accepts `fast 2` as the second argument to `every`. What language feature makes this work?
- (x) Partial application: `fast` applied to one argument yields a function awaiting the pattern, which matches the transformation type `every` expects.
- ( ) Implicit casting: Haskell coerces the number 2 into a pattern transformation.
- ( ) Operator overloading: `fast` is redefined inside `every` to take one argument.
- ( ) Lazy evaluation: the missing argument is supplied later at run time by the audio engine.

---

#### Model 2: Algebraic Laws — Testing Equational Reasoning

Algebraic laws let you reason about programs without running them — you can replace one expression with an equivalent one just as you would in algebra. But laws need to be tested too, because implementations can be buggy even if the intended semantics are correct. This model treats the laws as runnable tests and deliberately checks a law that fails, because understanding why something is not a law is as illuminating as knowing why something is.

> **Watch out!** Floating-point comparison will silently fail for these tests. All arithmetic here uses Python's `Fraction` type for exact rational arithmetic. If you adapt this code and use `float` instead of `Fraction`, `events_equal` may return `False` for a correct implementation due to rounding.

The algebraic laws are not decoration; they are executable contracts. The cell below verifies three laws by running both sides on the same input and comparing event streams.

```python
from fractions import Fraction

# Re-use the pattern model from Model 1 (abbreviated here)
def event(v, b, e): return (v, Fraction(b), Fraction(e))

def pure(v):
    def query(b, e):
        b, e = Fraction(b), Fraction(e)
        result = []
        for c in range(int(b), int(e)+1):
            cb, ce = Fraction(c), Fraction(c+1)
            if cb < e and ce > b:
                result.append(event(v, max(b, cb), min(e, ce)))
        return result
    return query

def seq(*pats):
    n = len(pats)
    def query(b, e):
        b, e = Fraction(b), Fraction(e)
        result = []
        for c in range(int(b), int(e)+1):
            for i, p in enumerate(pats):
                sb = Fraction(c) + Fraction(i, n)
                se = Fraction(c) + Fraction(i+1, n)
                if se <= b or sb >= e: continue
                for (v, eb, ee) in p(0, 1):
                    abs_b = sb + eb * Fraction(1, n)
                    abs_e = sb + ee * Fraction(1, n)
                    if abs_e > b and abs_b < e:
                        result.append(event(v, max(abs_b, b), min(abs_e, e)))
        return result
    return query

def fast(n, pat):
    n = Fraction(n)
    def query(b, e):
        return [(v, Fraction(sb)/n, Fraction(se)/n) for (v, sb, se) in pat(b*n, e*n)]
    return query

def slow(n, pat):
    n = Fraction(n)
    def query(b, e):
        return [(v, Fraction(sb)*n, Fraction(se)*n) for (v, sb, se) in pat(b/n, e/n)]
    return query

def rev(pat):
    def query(b, e):
        b, e = Fraction(b), Fraction(e)
        result = []
        for (v, sb, se) in pat(b, e):
            c = int(sb)
            result.append(event(v, Fraction(c+1) - se + Fraction(c),
                                    Fraction(c+1) - sb + Fraction(c)))
        return result
    return query

def events_equal(e1, e2):
    key = lambda ev: (ev[0], float(ev[1]), float(ev[2]))
    return sorted(e1, key=key) == sorted(e2, key=key)

p = seq(pure("bd"), pure("sn"), pure("hh"))
SPAN = (0, 2)  # test over two cycles

print("=== Testing Algebraic Laws ===")
print()

# Law 1: fast m (fast n p) = fast (m*n) p
m, n = 2, 3
lhs = fast(m, fast(n, p))(*SPAN)
rhs = fast(m * n, p)(*SPAN)
ok = events_equal(lhs, rhs)
print(f"Law 1: fast({m}) (fast({n}) p)  =  fast({m*n}) p    {'✓' if ok else '✗ FAIL'}")
if not ok:
    print(f"  LHS events: {len(lhs)}  RHS events: {len(rhs)}")

# Law 2: rev (rev p) = p
lhs2 = rev(rev(p))(*SPAN)
rhs2 = p(*SPAN)
ok2 = events_equal(lhs2, rhs2)
print(f"Law 2: rev(rev(p))  =  p                   {'✓' if ok2 else '✗ FAIL'}")

# Law 3: fast n (slow n p) = p
n3 = 3
lhs3 = fast(n3, slow(n3, p))(*SPAN)
rhs3 = p(*SPAN)
ok3 = events_equal(lhs3, rhs3)
print(f"Law 3: fast({n3})(slow({n3})(p))  =  p           {'✓' if ok3 else '✗ FAIL'}")

# Law 4 (commutativity of fast and slow?): does fast 2 (slow 3 p) = slow 3 (fast 2 p)?
lhs4 = fast(2, slow(3, p))(*SPAN)
rhs4 = slow(3, fast(2, p))(*SPAN)
ok4 = events_equal(lhs4, rhs4)
print(f"Law 4: fast(2)(slow(3)(p)) = slow(3)(fast(2)(p))  {'✓' if ok4 else '✗ NOT a law'}")

print()
print("Note: Law 4 being FALSE means fast and slow do not commute in general.")
print("This is a real constraint on what optimizations a Tidal compiler can do.")
print()

# Show a concrete non-law as a counterexample
print("=== Counterexample for Law 4 ===")
def show_ev(events):
    return [(v, float(b), float(e)) for v, b, e in sorted(events, key=lambda x: x[1])]

print("fast(2)(slow(3)(p)) [0,1):", show_ev(fast(2, slow(3, p))(0, 1)))
print("slow(3)(fast(2)(p)) [0,1):", show_ev(slow(3, fast(2, p))(0, 1)))
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

##### Critical Thinking Questions

5. Law 3 says `fast n (slow n p) = p`. The test runs over a span of 2 cycles, not just 1. Why does testing over multiple cycles give a stronger guarantee than testing over exactly one cycle?
6. Law 4 fails — `fast` and `slow` do not commute. This means a compiler *cannot* swap their order as an optimization. Where in your CS coursework have you seen "X does not commute with Y" limit optimizations? (String concatenation? Matrix multiplication?)
7. The laws are tested empirically (by running the functions). What is one way the test could pass despite a buggy implementation? What would a *proof* require that a test cannot provide?

---

##### Try It: With a Partner

Pair up at one machine on strudel.cc, alternating **performer** and **predictor** roles per item. The predictor writes down the expected sound or event structure before the performer presses play. Start from `sound("bd sn hh sn")` and apply, cumulatively:

1. `.fast(2)`
2. then `.rev()`
3. then `.every(2, x => x.rev())`

After item 3, jointly test one algebraic law from this section empirically: pick `rev(rev(p)) = p`, encode both sides as two Strudel expressions, and confirm by ear and by the highlighted spans that they are indistinguishable. Write one sentence on why testing a law by listening is weaker evidence than the proof we could give from the definitions, and one sentence on why it is still worth doing.

---

#### Model 3: Mini-Notation Grammar — The External Language Inside

The string `"bd sn [hh hh]"` is opaque to JavaScript and Haskell alike — their parsers see it as just a string. Inside that string lives a second language with its own lexer, grammar rules, and semantics. This is the external-DSL-within-an-embedded-DSL architecture that makes Tidal and Strudel a hybrid. This model implements that inner parser from scratch, giving you the full picture from character stream to event list.

The mini-notation (`"bd sn [hh hh]"`) is an external DSL embedded in a string. It deserves a grammar of its own, because it *is* a language: tokens, grammar rules, and semantics. The cell below implements a mini-notation lexer and recursive descent parser that produces the same event structure as the formal model.

```python
import re
from fractions import Fraction

# ── Mini-notation tokens ──────────────────────────────────────────────────────
TOKEN_SPEC = [
    ("LBRACKET", r"\["),
    ("RBRACKET", r"\]"),
    ("LANGLE",   r"<"),
    ("RANGLE",   r">"),
    ("STAR",     r"\*"),
    ("SLASH",    r"/"),
    ("AT",       r"@"),
    ("BANG",     r"!"),
    ("NUMBER",   r"\d+(?:\.\d+)?"),
    ("ATOM",     r"[A-Za-z_~][A-Za-z0-9_~\-\.]*"),
    ("SPACE",    r"[ \t]+"),
]
MASTER = re.compile("|".join(f"(?P<{n}>{p})" for n, p in TOKEN_SPEC))

def tokenize(src):
    return [(m.lastgroup, m.group()) for m in MASTER.finditer(src)
            if m.lastgroup != "SPACE"]

# ── AST nodes ─────────────────────────────────────────────────────────────────
class Atom:
    def __init__(self, value): self.value = value
    def __repr__(self): return f"Atom({self.value!r})"

class Seq:
    def __init__(self, children): self.children = children
    def __repr__(self): return f"Seq({self.children!r})"

class Group:
    def __init__(self, children): self.children = children
    def __repr__(self): return f"Group({self.children!r})"

class Fast:
    def __init__(self, pat, factor): self.pat = pat; self.factor = factor
    def __repr__(self): return f"Fast({self.pat!r}, {self.factor!r})"

# ── Recursive descent parser ──────────────────────────────────────────────────
class MiniParser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def peek(self):
        return self.tokens[self.pos] if self.pos < len(self.tokens) else ("EOF", "")

    def advance(self):
        t = self.peek()
        self.pos += 1
        return t

    def parse(self):
        items = self.parse_seq()
        return Seq(items)

    def parse_seq(self):
        items = []
        while self.peek()[0] not in ("EOF", "RBRACKET", "RANGLE"):
            items.append(self.parse_item())
        return items

    def parse_item(self):
        kind, val = self.peek()
        if kind == "LBRACKET":
            self.advance()
            children = self.parse_seq()
            if self.peek()[0] == "RBRACKET":
                self.advance()
            node = Group(children)
        else:
            self.advance()
            node = Atom(val)
        # Handle *factor
        if self.peek()[0] == "STAR":
            self.advance()
            _, factor = self.advance()
            node = Fast(node, float(factor))
        return node

def parse_mini(src):
    tokens = tokenize(src)
    return MiniParser(tokens).parse()

# ── Semantics: AST → event list ───────────────────────────────────────────────
def eval_mini(node, b=0, e=1):
    b, e = Fraction(b), Fraction(e)
    span = e - b
    if isinstance(node, Atom):
        return [(node.value, b, e)]
    elif isinstance(node, Fast):
        factor = Fraction(node.factor)
        raw = eval_mini(node.pat, 0, 1)
        result = []
        for _ in range(int(factor)):
            pass  # fast: query the child multiple times in the same span
        # Compress: each repetition fits in span/factor
        sub_span = span / factor
        all_events = []
        for rep in range(int(factor)):
            offset = b + rep * sub_span
            for (v, sb, se) in eval_mini(node.pat, 0, 1):
                all_events.append((v, offset + sb * sub_span, offset + se * sub_span))
        return all_events
    elif isinstance(node, (Seq, Group)):
        children = node.children
        n = len(children)
        if n == 0: return []
        child_span = span / n
        result = []
        for i, child in enumerate(children):
            cb = b + i * child_span
            ce = cb + child_span
            result.extend(eval_mini(child, cb, ce))
        return result
    return []

# ── Tests ─────────────────────────────────────────────────────────────────────
test_cases = [
    ("bd sn",            2, 0, 1),   # 2 events, each 1/2 cycle
    ("bd sn hh sn",      4, 0, 1),   # 4 events, each 1/4 cycle
    ("bd [sn sn]",       3, 0, 1),   # bd=1/2, sn=1/4, sn=1/4
    ("bd sn*2 hh",       4, 0, 1),   # bd=1/3, sn=1/6, sn=1/6, hh=1/3
]

print("=== Mini-Notation Parser ===")
for src, expected_count, b, e in test_cases:
    ast = parse_mini(src)
    events = eval_mini(ast, b, e)
    ok = len(events) == expected_count
    print(f"  {src!r:<20} → {len(events)} events  ({'✓' if ok else f'✗ expected {expected_count}'})")
    for v, sb, se in sorted(events, key=lambda x: x[1]):
        print(f"       ({v!r:<8} {float(sb):.4f}–{float(se):.4f})")

print()
print("=== AST for 'bd [sn hh] sn' ===")
print(parse_mini("bd [sn hh] sn"))
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

##### Critical Thinking Questions

8. The mini-notation parser is a hand-written recursive descent parser. Identify the grammar rule that `parse_seq` implements and the rule that `parse_item` implements. Write both rules in EBNF.
9. `Group` subdivides its children within the group's span, while `Seq` distributes children across the whole span. What is the semantic difference between `"bd sn hh"` and `"[bd sn] hh"` in event timing?
10. `Fast` multiplies the number of events by repeating the sub-pattern. Extend the parser and evaluator to support `/n` (slow: stretch across n slots). Write the `Slow` node and its `eval_mini` case.
11. The mini-notation is an external DSL embedded in a string. Name one advantage and one disadvantage of embedding it in a string rather than giving it first-class syntax (e.g., `bd sn [hh hh]` without quotes).

---

### Part III: Synthesis & Practice

#### 5. Exercises

Exercises 1 through 3 are individual; exercises 4 and 5 are partner exercises, and at least one partner exercise should be completed before our parser-construction module, which builds directly on this vocabulary.

1. *Query by hand.* For the pattern `[bd sn]*2 hh`, compute the complete event set for the span $[0,1)$ using the formal rules of Section 3, showing the span arithmetic at each subdivision. Verify at strudel.cc and report both your derivation and the verification.
2. *A law with a proof sketch.* Using the function-of-time model from Model 1, argue in a short paragraph (with the relevant span arithmetic) why `fast m (fast n p) = fast (m*n) p` holds. Identify one assumption your argument needs.
3. *Host idiom translation.* Translate `every 3 (slow 2) $ sound "bd [sn sn]"` into Strudel's JavaScript idiom, run it, and report the event structure for cycles 0 through 3, indicating on which cycles the transformation fired.
4. *Partner: design archaeology.* With a partner, find one mini-notation feature in the Strudel documentation that we did not cover (candidates include `,` stacking, `!` replication, or `@` elongation). One partner writes its informal semantics in the style of Section 3's displayed math; the other constructs two strudel.cc examples that confirm or refute that semantics. Report both artifacts and any revision the experiments forced.
5. *Partner: the embedding boundary.* Each partner independently lists three things in a Strudel program that the JavaScript parser handles and three that the mini-notation parser handles, then reconcile your lists. Report the reconciled lists and one boundary case where you initially disagreed.
6. *Mini-notation extension.* Add support for `!` (repeat: `bd!3` = `bd bd bd`) to the Python mini-notation parser and evaluator. Write two positive test cases and one negative test case, run them, and explain how `!` differs from `*` in event distribution.

---

#### 6. Further Reading

- McLean, Alex. "Making Programming Languages to Dance to: Live Coding with Tidal." *FARM Workshop, ICFP* (2014). The design rationale for TidalCycles from its creator; short and very readable.
- Roos, Felix, and Alex McLean. "Strudel: Live Coding Patterns on the Web." *International Conference on Live Coding* (2023). The Strudel system paper, including its account of porting the pattern model from Haskell to JavaScript.
- Hudak, Paul. "Building Domain-Specific Embedded Languages." *ACM Computing Surveys* 28, 4es (1996). The classic statement of the EDSL philosophy that Tidal exemplifies.
- Fowler, Martin. *Domain-Specific Languages* (Addison-Wesley, 2010). Chapters on internal versus external DSLs generalize the tradeoff table from Section 2.
- The Strudel workshop and reference at [strudel.cc/workshop/getting-started](https://strudel.cc/workshop/getting-started). The fastest route from this module to making actual music.

---

---

## Going Deeper: A Gallery of Programming Languages: Same Problem, Different Minds

A programming language is not just a tool — it is a crystallized theory of what computation is. Every `for` loop, list comprehension, or logic clause embeds a belief about how problems should be decomposed and what the programmer should have to say explicitly. Exploring many languages through the same problem is like tasting the same dish cooked by five different chefs: the ingredients are the same, but the philosophy behind the recipe changes everything.

#### Learning Goals

By the end of this activity, you will be able to:

- Identify the five major programming paradigms (imperative, object-oriented, functional, logic, declarative) and characterize the computational worldview each embodies
- Implement the same problem in multiple paradigms in Python and explain how the choice of paradigm shapes the structure and readability of the solution
- Compare how different paradigms handle state, control flow, and abstraction, and evaluate the tradeoffs in expressiveness and correctness
- Apply the concept of paradigm as a design choice — not a fact — when selecting an approach for a given problem
- Analyze an unfamiliar language feature and classify it within the paradigm taxonomy based on its behavior

> **Before You Begin:** This activity assumes you can:
> - Write Python functions using loops, list comprehensions, and lambda expressions
> - Describe in plain English what a recursive function does on a concrete example
> - Explain what an environment (dictionary of variable-to-value mappings) is in the context of an interpreter
>
> If any of these feel shaky, review them first.

#### Introduction

Here is a fact that most programming courses hide from you: **programming languages are not tools — they are philosophical positions.**

Every language embeds a theory of computation. Every syntax reflects a model of mind. Every design choice encodes a belief about what programs should look like, what programmers should be allowed to do, and what the relationship between human thought and machine execution should be. When you write a `for` loop, you are not just iterating — you are adopting an entire worldview about how computation unfolds through time, step by step, mutation by mutation. When you write `sum(x*x for x in range(1,101) if x%2==0)`, you are making a different philosophical commitment: that computation is best described as a transformation of values, not a sequence of state changes.

This activity takes a small number of concrete problems and solves each one through five different philosophical lenses. You will not be learning five new languages today — you will be learning five ways of *thinking* about what it means to compute something. By the end, you should feel the difference viscerally: not as an abstract taxonomy from a textbook, but as a lived experience of writing (or reading) code that surprises you, delights you, or unsettles your assumptions. The "right" way to write a program is a choice, not a fact. Today you will practice making that choice consciously.

---

#### Model 1: Five Ways to Sum a List

All five snippets below compute the same number (171700), yet they read like different languages from different planets. As you read each one, ask yourself: what does the programmer have to say explicitly? What does the language figure out on its own? The answers reveal the core trade-off each paradigm is making between programmer control and language assistance.

> **The Problem:** Compute the sum of the squares of all even numbers from 1 to 100.
>
> **The Claim:** There are at least five meaningfully different ways to express this — and they reveal five different theories of what computation is.

Before we visit other languages, we stay in Python. Python is a polyglot language: it can wear multiple paradigm hats. This lets us isolate the *paradigm* from the *syntax*, and see clearly that the choice of style is a choice of mindset.

```python
# Problem: compute sum of squares of even numbers from 1 to 100
# Five paradigms, one problem

# --- Imperative (C-style thinking in Python) ---
result_imp = 0
for i in range(1, 101):
    if i % 2 == 0:
        result_imp += i * i
print(f"Imperative: {result_imp}")

# --- Object-Oriented ---
class NumberPipeline:
    def __init__(self, data): self._data = list(data)
    def filter(self, pred): return NumberPipeline(x for x in self._data if pred(x))
    def map(self, fn): return NumberPipeline(fn(x) for x in self._data)
    def reduce(self, fn, init):
        acc = init
        for x in self._data: acc = fn(acc, x)
        return acc

result_oop = (NumberPipeline(range(1, 101))
              .filter(lambda x: x % 2 == 0)
              .map(lambda x: x * x)
              .reduce(lambda a, b: a + b, 0))
print(f"OOP:        {result_oop}")

# --- Functional (higher-order functions) ---
from functools import reduce
result_fn = reduce(lambda a, b: a + b,
                   map(lambda x: x * x,
                       filter(lambda x: x % 2 == 0, range(1, 101))))
print(f"Functional: {result_fn}")

# --- Declarative (comprehension) ---
result_decl = sum(x * x for x in range(1, 101) if x % 2 == 0)
print(f"Declarative:{result_decl}")

# --- APL-inspired (array-oriented) ---
import numpy as np
nums = np.arange(1, 101)
result_apl = np.sum((nums[nums % 2 == 0]) ** 2)
print(f"Array:      {result_apl}")

# All should be 171700
assert result_imp == result_oop == result_fn == result_decl == result_apl == 171700
print("\nAll paradigms agree: 171700")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

> **Watch out!** The NumPy array-oriented version returns a NumPy scalar (`numpy.int64`), not a plain Python `int`. The `==` comparison still works, but `type(result_apl) == int` is `False`. This is a common source of subtle bugs when mixing NumPy and pure Python code.

---

**Critical Thinking Questions**

1. The imperative version uses a loop and mutation: `result_imp` changes on each iteration. The declarative version is one line and introduces no variable that changes. What does the declarative version *hide* that the imperative version *exposes*? Which is more readable — and more importantly, *readable to whom*? Does the answer change depending on whether the reader has a C background or a math background?

2. The OOP version creates a `NumberPipeline` class with `.filter()`, `.map()`, and `.reduce()` methods. What design pattern does this implement? (Hint: look up "fluent interface" and "builder pattern.") What concrete advantage does method chaining give over the nested function calls in the functional version?

3. The functional version nests `map`, `filter`, and `reduce`. The `reduce` is the *outermost* call — it appears first in the source. But it executes *last*. Why does evaluation happen inside-out? Draw the call tree if it helps.

4. NumPy's array operations can parallelize implicitly — the hardware can compute all element-wise squares at the same time. Why is this safe for the array-oriented version but potentially *unsafe* for a parallelized version of the imperative loop with a shared `result_imp` variable?

---

#### Model 2: Fibonacci — Recursion, Memoization, and Generators

The naive recursive Fibonacci is famous for being simultaneously the clearest expression of the mathematical definition and a comically slow program. The five variants here each fix the performance problem in a different way — and each fix reveals a different language design concept. Pay attention to what changes between versions and what stays the same.

> **Watch out!** `@lru_cache` caches based on argument equality. If you call `fib_memo(20)` in two different places, the second call returns the cached result instantly. But the cache is tied to the function object — a new function defined with the same body gets its own empty cache. This catches students who define their own cached function and wonder why it is still slow.

> **The Problem:** Compute Fibonacci numbers.
>
> **The Claim:** This deceptively simple problem reveals how the *same mathematical definition* can be expressed with radically different computational consequences — from exponential time to logarithmic time, and from finite lists to infinite streams.

Fibonacci is the "Hello, World" of recursion, but most courses stop at the naive version and leave students with the impression that recursion is slow. That is backwards. The naive version is slow not because it is recursive, but because it *recomputes the same subproblems*. What follows shows four ways to fix that, plus one approach that sidesteps the recursion entirely.

```python
import sys
sys.setrecursionlimit(500)

# 1. Naive recursion (beautiful but exponential)
def fib_naive(n):
    if n <= 1: return n
    return fib_naive(n-1) + fib_naive(n-2)

# 2. Memoized recursion (adds caching transparently)
from functools import lru_cache

@lru_cache(maxsize=None)
def fib_memo(n):
    if n <= 1: return n
    return fib_memo(n-1) + fib_memo(n-2)

# 3. Iterative (tail-recursive style, but imperative)
def fib_iter(n):
    a, b = 0, 1
    for _ in range(n): a, b = b, a + b
    return a

# 4. Generator (lazy, infinite sequence)
def fib_stream():
    a, b = 0, 1
    while True:
        yield a
        a, b = b, a + b

# 5. Matrix exponentiation (O(log n)) — different algorithm entirely
def mat_mul(A, B):
    return [
        [A[0][0]*B[0][0] + A[0][1]*B[1][0], A[0][0]*B[0][1] + A[0][1]*B[1][1]],
        [A[1][0]*B[0][0] + A[1][1]*B[1][0], A[1][0]*B[0][1] + A[1][1]*B[1][1]]
    ]

def mat_pow(M, n):
    if n == 1: return M
    if n % 2 == 0:
        half = mat_pow(M, n // 2)
        return mat_mul(half, half)
    return mat_mul(M, mat_pow(M, n - 1))

def fib_matrix(n):
    if n == 0: return 0
    M = [[1,1],[1,0]]
    return mat_pow(M, n)[0][1]

# Compare all at n=20
n = 20
results = {
    "Naive":    fib_naive(n),
    "Memoized": fib_memo(n),
    "Iterative":fib_iter(n),
    "Generator":next(x for i,x in enumerate(fib_stream()) if i == n),
    "Matrix":   fib_matrix(n),
}
for name, val in results.items():
    print(f"  {name:12}: fib({n}) = {val}")

# Show laziness: first 10 from the infinite stream
stream = fib_stream()
print(f"\nFirst 10: {[next(stream) for _ in range(10)]}")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

---

**Critical Thinking Questions**

1. The naive recursive solution is the most direct translation of the mathematical definition: *fib(n) = fib(n-1) + fib(n-2)*. What is its time complexity, and why? Draw a partial call tree for `fib_naive(5)` and count the number of calls to `fib_naive(2)` to build your intuition.

2. `@lru_cache` transforms the exponential-time function to linear-time without changing a single line of the recursive logic. The "what" (the recurrence relation) stays the same; only the "how" (caching) is added. What is the general term in PL design for separating the *specification* of a computation from its *implementation* strategy? (Hint: think about what a compiler does with tail-call optimization, or what a SQL optimizer does with a query.)

3. The generator `fib_stream()` represents an *infinite* sequence. What does it mean for a sequence to be "lazy"? Why would `list(fib_stream())` run forever (or until you run out of memory) while `next(stream)` is safe? What other languages build laziness into their evaluation model by default?

4. The matrix exponentiation version computes fib(n) in O(log n) time — it is a fundamentally different algorithm from any of the recursive or iterative approaches. What does this tell you about the relationship between *algorithm choice* and *paradigm choice*? Are they independent?

---

#### Model 3: Sorting — Algorithms as Philosophies

Sorting algorithms are taught as performance exercises, but viewed through a PL lens they are paradigm exercises: quicksort embodies divide-and-conquer recursion, mergesort embodies pure functional immutability, and the "specification" approach embodies the logic programming idea that you should describe what you want and let the runtime figure out how. Watch for what each style makes easy and what it hides.

> **The Problem:** Sort a list of integers.
>
> **The Claim:** Different sorting algorithms encode different philosophical commitments about how to break a problem apart, and different language paradigms make some commitments more natural to express than others.

Quicksort and mergesort are both "divide and conquer," but they divide differently and conquer differently. The third approach — describing *what it means* to be sorted rather than *how* to sort — represents the logic programming worldview. Python's production `sorted()` is a reminder that real systems optimize for different things than textbooks do.

```python
# Three sorting philosophies

# 1. Quicksort — divide and conquer with a pivot
# In Haskell this is ONE LINE: qsort [] = []; qsort (x:xs) = qsort smaller ++ [x] ++ qsort larger
# Python functional version:
def qsort(lst):
    if len(lst) <= 1: return lst
    pivot = lst[len(lst) // 2]
    left  = [x for x in lst if x < pivot]
    mid   = [x for x in lst if x == pivot]
    right = [x for x in lst if x > pivot]
    return qsort(left) + mid + qsort(right)

# 2. Mergesort — pure divide and conquer (no in-place mutation)
def mergesort(lst):
    if len(lst) <= 1: return lst
    mid = len(lst) // 2
    left  = mergesort(lst[:mid])
    right = mergesort(lst[mid:])
    return merge(left, right)

def merge(a, b):
    if not a: return b
    if not b: return a
    if a[0] <= b[0]:
        return [a[0]] + merge(a[1:], b)
    return [b[0]] + merge(a, b[1:])

# 3. "Bogo-describe" — express the property, let the runtime find a solution
# (Prolog-style thinking: describe what you want, not how to compute it)
def is_sorted(lst):
    return all(lst[i] <= lst[i+1] for i in range(len(lst)-1))

def check_sort(lst):
    """Verify a sort by SPECIFICATION: the result should be sorted and a permutation."""
    result = sorted(lst)
    assert is_sorted(result), "Not sorted!"
    assert sorted(result) == sorted(lst), "Not a permutation!"
    return result

# 4. Python's built-in Timsort — a hybrid, hyper-optimized, REAL sort
import random
data = [random.randint(1, 100) for _ in range(20)]
print(f"Input: {data}")
print(f"qsort:     {qsort(data)}")
print(f"mergesort: {mergesort(data)}")
print(f"Timsort:   {sorted(data)}")
print(f"All equal: {qsort(data) == mergesort(data) == sorted(data)}")

# The "specification" approach:
result = check_sort(data)
print(f"\nSpecification-verified sort: {result[:5]}...{result[-5:]}")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

> **Watch out!** The `merge` function above creates new lists with `[a[0]] + merge(...)` on every recursive call, giving O(n²) total allocation. This is pedagogically clean but performance-terrible for large inputs. Real mergesort implementations use in-place merging or pre-allocated buffers — a good example of the gap between a paradigm-pure implementation and a production one.

---

**Critical Thinking Questions**

1. The comment in the code shows that Haskell's quicksort fits in two lines using pattern matching on lists: `qsort [] = []` and `qsort (x:xs) = qsort smaller ++ [x] ++ qsort larger`. The Python version needs five lines to express the same idea. What does this tell you about the *expressiveness* of list pattern matching compared to Python's index-based approach? What syntactic feature of Haskell makes this possible?

2. The `merge` function in mergesort is recursive and builds entirely new lists at each step — it never modifies an existing list. What is the memory cost of this approach relative to an in-place merge? Under what circumstances would you prefer immutable mergesort over a mutation-based sort?

3. The `check_sort` function verifies that `sorted(lst)` is correct by checking two properties: (a) the output is ordered, and (b) the output is a permutation of the input. This is the *specification* of a sort. In Prolog or a constraint solver, you could write these constraints and let the runtime *generate* a sorted list rather than verify one. What ingredient is missing from `check_sort` that would make it a generator rather than a verifier?

4. Python's `sorted()` uses Timsort, a hybrid algorithm that combines merge sort and insertion sort and is specifically tuned for real-world data patterns (partially sorted runs). Why would the designers of a practical language *not* use the most theoretically elegant algorithm? What tradeoffs does Timsort make?

---

#### Model 4: Tree Operations — Pattern Matching vs. Visitor Pattern

Expression trees are the central data structure of every interpreter you will write this semester. This model shows three philosophically distinct ways to traverse the same tree: functional pattern matching (enumerate cases in a function), OOP visitor (dispatch through method overriding), and fold (replace constructors with functions). Notice that the fold produces `eval`, `count`, and `depth` from a single recursive structure — you provide the algebra, not the recursion.

> **The Problem:** Evaluate, pretty-print, count, and measure the depth of an expression tree.
>
> **The Claim:** ML/Haskell-style pattern matching and OOP's Visitor pattern solve the same extensibility problem in opposite ways. Understanding *why* they are opposites unlocks one of the deepest questions in PL design.

A binary expression tree is the central data structure of every interpreter and compiler. How you traverse it says a great deal about your programming model. In ML, you write a function and enumerate the cases. In Java, you write a class hierarchy and add methods. In category theory, you write a fold (catamorphism) that replaces each constructor with a function. All three produce the same output. None of them is "correct."

```python
from dataclasses import dataclass
from typing import Any, Optional, Callable

# A binary expression tree
@dataclass
class Leaf: value: float

@dataclass
class Add: left: Any; right: Any

@dataclass
class Mul: left: Any; right: Any

@dataclass
class Neg: child: Any

# === STYLE 1: Pattern Matching (ML/Haskell style) ===
# Haskell: eval (Leaf v) = v
#          eval (Add l r) = eval l + eval r
#          eval (Mul l r) = eval l * eval r
#          eval (Neg c) = -(eval c)
def eval_match(tree) -> float:
    match tree:
        case Leaf(value=v):      return v
        case Add(left=l, right=r): return eval_match(l) + eval_match(r)
        case Mul(left=l, right=r): return eval_match(l) * eval_match(r)
        case Neg(child=c):       return -eval_match(c)
    raise ValueError(f"Unknown: {type(tree)}")

# === STYLE 2: OOP Visitor Pattern (Java/C++ style) ===
class EvalVisitor:
    def visit(self, tree):
        method = getattr(self, f'visit_{type(tree).__name__}')
        return method(tree)
    def visit_Leaf(self, node): return node.value
    def visit_Add(self, node): return self.visit(node.left) + self.visit(node.right)
    def visit_Mul(self, node): return self.visit(node.left) * self.visit(node.right)
    def visit_Neg(self, node): return -self.visit(node.child)

class PrettyPrintVisitor:
    def visit(self, tree):
        method = getattr(self, f'visit_{type(tree).__name__}')
        return method(tree)
    def visit_Leaf(self, n): return str(n.value)
    def visit_Add(self, n): return f"({self.visit(n.left)} + {self.visit(n.right)})"
    def visit_Mul(self, n): return f"({self.visit(n.left)} * {self.visit(n.right)})"
    def visit_Neg(self, n): return f"(-{self.visit(n.child)})"

# === STYLE 3: Functional fold (catamorphism) ===
def fold(tree, leaf_fn: Callable, add_fn: Callable, mul_fn: Callable, neg_fn: Callable):
    match tree:
        case Leaf(value=v): return leaf_fn(v)
        case Add(l, r): return add_fn(fold(l,leaf_fn,add_fn,mul_fn,neg_fn),
                                     fold(r,leaf_fn,add_fn,mul_fn,neg_fn))
        case Mul(l, r): return mul_fn(fold(l,leaf_fn,add_fn,mul_fn,neg_fn),
                                     fold(r,leaf_fn,add_fn,mul_fn,neg_fn))
        case Neg(c): return neg_fn(fold(c,leaf_fn,add_fn,mul_fn,neg_fn))

# Build: -(3 + 4) * 2
tree = Mul(Neg(Add(Leaf(3), Leaf(4))), Leaf(2))

# Evaluate
print(f"Pattern match eval: {eval_match(tree)}")
print(f"Visitor eval:       {EvalVisitor().visit(tree)}")
print(f"Visitor pretty:     {PrettyPrintVisitor().visit(tree)}")
print(f"Fold eval:          {fold(tree, lambda v: v, lambda a,b: a+b, lambda a,b: a*b, lambda x: -x)}")

# Fold for count of nodes:
count = fold(tree, lambda _: 1, lambda a,b: a+b, lambda a,b: a+b, lambda x: x)
print(f"Fold node count:    {count}")

# Fold for maximum depth:
depth = fold(tree, lambda _: 1, lambda a,b: 1+max(a,b), lambda a,b: 1+max(a,b), lambda x: 1+x)
print(f"Fold depth:         {depth}")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

---

**Critical Thinking Questions**

1. Consider the following fold call:
   ```
   fold(tree, str, lambda a,b: f"(+ {a} {b})", lambda a,b: f"(* {a} {b})", lambda x: f"(- {x})")
   ```
   What would this produce for the tree `-(3 + 4) * 2`? What language's syntax does the output resemble, and what is significant about that language's use of that notation?

2. The visitor pattern makes it easy to *add new operations* (a new `Visitor` subclass) without modifying the `Leaf`, `Add`, `Mul`, or `Neg` classes. The pattern matching style makes it easy to *add new node types* (a new `case`) without modifying existing functions — but requires updating *every* match-based function when a new type appears. This tension has a name in PL design. What is it called? (Hint: it involves a "two-dimensional" design space and was named by Philip Wadler.)

3. Looking at the code for `eval_match` (12 lines with comments) versus `EvalVisitor` (6 lines), pattern matching is less verbose for *this specific case*. Under what circumstances would the visitor pattern start to look *less* verbose than pattern matching?

4. The `fold` function encodes the entire recursion structure once. `eval`, `count`, and `depth` are then just three different choices of functions to pass in — no recursion written by the caller at all. What does this tell you about the relationship between `fold` and the general concept of structural recursion over a datatype?

---

**Multiple Choice: Check Your Understanding**

What is a catamorphism?

- [( )] A pattern that matches on algebraic data types
- [(X)] A structural recursion that replaces each constructor of a datatype with a function, generalizing fold to arbitrary recursive types
- [( )] A recursive descent parser rule for a context-free grammar
- [( )] A method for detecting ambiguity in parsing

---

#### Model 5: The Same Interpreter in Three Styles

A tree-walking interpreter, a CPS interpreter, and a bytecode-plus-VM compiler all compute the same thing — they implement the same semantics, just at different altitudes. Understanding why they are equivalent (and what differs) is the conceptual foundation for the rest of the course. Trace through the CPS version slowly: the continuation `k` is "what to do with this result when it is ready," and every recursive call hands off that baton rather than waiting for it.

> **Watch out!** The tree-walker in Style 1 uses `env={}` as a default mutable argument — a classic Python footgun. Default mutable arguments are shared across all calls that use the default, so if you ever mutate `env` in place (rather than constructing a new dict with `{**env, k: v}`), you will corrupt the shared default. The code here is safe because it never mutates `env` in place, but be careful when you adapt it.

> **The Problem:** Implement a tiny interpreter for a language with numbers, addition, and let-bindings.
>
> **The Claim:** "The interpreter" is an idea, not an implementation. Tree-walkers, CPS transformations, and bytecode compilers with stack VMs all implement the same semantics — and understanding *why* they are equivalent is the beginning of understanding what programs *mean*.

This is the model that most directly connects to what you will build in this course. A let-binding like `let x = 3 in let y = 4 in x + y` is a tiny programming language. It has variables, scoping, and arithmetic. Interpreting it correctly requires thinking carefully about environments. Three radically different strategies for doing so follow.

```python
from dataclasses import dataclass
from typing import Any

@dataclass
class Num: v: float
@dataclass
class Add: l: Any; r: Any
@dataclass
class Let: name: str; val: Any; body: Any
@dataclass
class Var: name: str

# === STYLE 1: Recursive tree-walker (most common in this course) ===
def interp1(node, env={}):
    if isinstance(node, Num): return node.v
    if isinstance(node, Var): return env[node.name]
    if isinstance(node, Add): return interp1(node.l, env) + interp1(node.r, env)
    if isinstance(node, Let):
        v = interp1(node.val, env)
        return interp1(node.body, {**env, node.name: v})

# === STYLE 2: Continuation-Passing Style (CPS) ===
# Each eval call takes a "k" (continuation) — what to do NEXT with the result
def interp2(node, env, k):
    if isinstance(node, Num): return k(node.v)
    if isinstance(node, Var): return k(env[node.name])
    if isinstance(node, Add):
        return interp2(node.l, env, lambda lv:
               interp2(node.r, env, lambda rv:
               k(lv + rv)))
    if isinstance(node, Let):
        return interp2(node.val, env, lambda v:
               interp2(node.body, {**env, node.name: v}, k))

# === STYLE 3: Compilation to bytecode then VM execution ===
def compile_to_bytecode(node, env_vars=None):
    """Compile to a list of (opcode, arg) instructions."""
    if env_vars is None: env_vars = {}
    instrs = []
    if isinstance(node, Num):
        instrs.append(('PUSH', node.v))
    elif isinstance(node, Var):
        instrs.append(('LOAD', node.name))
    elif isinstance(node, Add):
        instrs.extend(compile_to_bytecode(node.l))
        instrs.extend(compile_to_bytecode(node.r))
        instrs.append(('ADD', None))
    elif isinstance(node, Let):
        instrs.extend(compile_to_bytecode(node.val))
        instrs.append(('STORE', node.name))
        instrs.extend(compile_to_bytecode(node.body))
    return instrs

def run_bytecode(instrs, env=None):
    """Stack-based VM."""
    if env is None: env = {}
    stack = []
    for op, arg in instrs:
        if op == 'PUSH': stack.append(arg)
        elif op == 'LOAD': stack.append(env[arg])
        elif op == 'ADD': b, a = stack.pop(), stack.pop(); stack.append(a + b)
        elif op == 'STORE': env[arg] = stack.pop()
    return stack[-1] if stack else None

# Test program: let x = 3 in let y = 4 in x + y
program = Let("x", Num(3), Let("y", Num(4), Add(Var("x"), Var("y"))))

r1 = interp1(program)
r2 = interp2(program, {}, lambda x: x)
bytecode = compile_to_bytecode(program)
r3 = run_bytecode(bytecode)

print(f"Tree-walk:  {r1}")
print(f"CPS:        {r2}")
print(f"Bytecode:   {r3}")
print(f"Bytecode instructions: {bytecode}")
print(f"\nAll agree: {r1 == r2 == r3}")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

---

**Critical Thinking Questions**

1. In `interp2`, every recursive call immediately passes its result to `k` — there is no "waiting for a result" and then doing more work with it. In `interp1`, the call `interp1(node.l, env)` must complete and *return* before the addition `+ interp1(node.r, env)` can proceed. Why does the CPS transformation matter for *tail-call optimization*? Which version is more amenable to being compiled to a loop?

2. The bytecode version separates compilation (`compile_to_bytecode`) from execution (`run_bytecode`). For a program that will be run *once*, this is extra work. For a program run *many times* (like a hot loop in a JVM or a frequently-called function in V8), what concrete advantage does pre-compilation to bytecode give?

3. All three interpreters produce the same result for the same input program. This is not a coincidence: they implement the same *semantics*. The study of what programs mean, independently of how they are executed, is a formal field. What is it called? (Hint: there are several sub-disciplines including denotational, operational, and axiomatic approaches.)

4. Consider which interpreter style you would use in each scenario: (a) an interactive REPL where you type one expression at a time; (b) a production compiler for a language that needs to run on a JVM; (c) a concurrent language where multiple threads execute different parts of the program simultaneously. Justify each choice in one sentence.

---

**Multiple Choice: Check Your Understanding**

Which property of pure functions makes the array-oriented approach in Model 1 safe to parallelize?

- [(X)] No shared mutable state — each element can be processed independently without coordinating with other elements
- [( )] Lazy evaluation defers computation until needed, eliminating race conditions
- [( )] Type safety prevents data races at compile time
- [( )] Immutable types are allocated on the stack rather than the heap

---

The expression `reduce(lambda a,b: a+b, map(lambda x: x*x, filter(...)))` evaluates inside-out. Why?

- [( )] Python's optimizer reverses evaluation order for performance
- [( )] `filter` always runs before `map` regardless of nesting depth
- [(X)] `filter` must produce its entire output before `map` can process any of it, because Python's `map` and `filter` are eager in this context — each stage consumes the previous stage's complete output
- [( )] The lambda calculus dictates outermost-first reduction in all cases

---

What does the visitor pattern solve that pattern matching does not?

- [(X)] Adding new operations to a fixed, closed set of types without modifying the type definitions themselves
- [( )] Handling infinite data structures efficiently without running out of memory
- [( )] Avoiding ambiguity in context-free grammars
- [( )] Enabling tail-call optimization for deeply recursive traversals

---

#### Exercises

**Exercise 1: Extend the Expression Tree**

Add a `Max` node to the tree from Model 4 (it takes the maximum of its two children's values). Implement this new node in all three traversal styles:

- **Pattern matching style**: add a new `case Max(left=l, right=r)` branch to `eval_match`.
- **Visitor style**: add `visit_Max` methods to both `EvalVisitor` and `PrettyPrintVisitor`.
- **Fold style**: add a `max_fn` parameter to `fold` and update all three call sites (eval, count, depth).

Which style required the most edits? Which required the fewest? Does your answer match your expectation from CTQ 2 in Model 4?

---

**Exercise 2: A Lazy Pipeline with itertools**

Implement the "sum of squares of even numbers from 1 to 100" problem from Model 1 using Python's `itertools` module. Specifically, use `itertools.count()` to generate an infinite stream of integers, `itertools.islice()` to take the first 100, `filter()` to keep even numbers, `map()` to square them, and `itertools.accumulate()` to compute a running sum. Take the last element of the accumulated result.

This is a *lazy pipeline* — no intermediate list is ever fully materialized. Contrast this with the NumPy array version: both avoid intermediate lists, but for different reasons. Explain the difference.

---

**Exercise 3: Add Loops to the Interpreter**

Add a `While` node to the interpreter in Model 5. A `While` node has two fields: `cond` (an expression that should evaluate to a number; nonzero means "keep looping") and `body` (an expression to evaluate repeatedly). You will also need a way to assign to variables — add an `Assign` node with `name` and `val` fields.

Implement `While` and `Assign` in all three styles:

- **Tree-walker**: straightforward — evaluate `cond`, loop while nonzero, evaluate `body` each iteration.
- **CPS**: this is the hard part. The continuation must be re-invoked on each iteration. Think carefully about what `k` means inside a loop.
- **Bytecode VM**: add `JUMP_IF_ZERO` and `JUMP` instructions. The compiler needs to emit a conditional branch, the loop body, and an unconditional back-jump.

---

**Exercise 4: Ten Languages, One Problem**

Look up and copy (with full attribution — author, language, source URL) implementations of the "sum of squares of even numbers from 1 to 100" problem in at least three languages you have never used before. Suggested languages to explore:

- **Haskell**: `sum [x^2 | x <- [1..100], even x]`
- **Erlang**: use list comprehensions
- **Clojure**: use `reduce`, `filter`, `map`, or `->>` threading macro
- **APL or J**: a one-liner using array primitives at `tryapl.org`
- **Forth**: a stack-based loop
- **Prolog**: use `aggregate_all` or `findall`

For each language you choose: (a) copy the implementation with attribution, (b) run it in an online REPL, and (c) write 2-3 sentences describing what makes the paradigm feel different from Python.

---

#### Reflection

You have now seen the same computations expressed in more than five different ways. Write a 4-5 sentence reflection addressing the following: Which paradigm felt most "natural" to you, and what does your preference reveal about how you currently think about computation? Did any paradigm *surprise* you — did a solution appear more or less complex than you expected? Thinking ahead: as you encounter more languages this semester (Racket, Haskell, Prolog, possibly others), do you expect your sense of what is "natural" to shift? Will your answer to these questions change by December, and what would it mean if it did?

---

#### Further Reading

The ideas in this activity connect to a rich literature. These are starting points, not assignments:

- **"Concepts, Techniques, and Models of Computer Programming"** — Peter Van Roy and Seif Haridi. The most comprehensive paradigm taxonomy in print. Chapter 4 covers declarative concurrency; Chapter 6 covers objects. If you want to understand why there are so many paradigms, this book explains.

- **"Why Functional Programming Matters"** — John Hughes, 1990. A short, readable paper that argues functional programming's real advantage is *composability*, not purity. Available free online. Read it before the end of the semester.

- **"Programming Language Pragmatics"** — Michael Scott. Chapter 6 covers control flow in depth; Chapter 11 covers functional languages. A solid reference for the technical material in this course.

- **APL in the browser**: `https://tryapl.org` — type `+/(2|⍳100)` and see what happens. APL's entire philosophy is that arrays are the right primitive, and operations on arrays should be single characters. It is either beautiful or horrifying, depending on your background.

- **Rosetta Code**: `https://rosettacode.org` — the same problem implemented in hundreds of languages. Look up "Fibonacci sequence" or "sorting algorithms" and browse. You will find things that don't look like programming at all.

- **"Structure and Interpretation of Computer Programs"** — Abelson, Sussman, Sussman. The classic MIT textbook. The interpreter in Model 5 is a minimal version of what you build in Chapters 3 and 4. Available free at `https://mitpress.mit.edu/sites/default/files/sicp/index.html`.

---

## Going Deeper: Memory Management: From Stack Frames to Garbage Collection

> **Opening Hook — The Hotel Room Analogy**
>
> Memory management is like running a hotel. Someone must **assign rooms** to arriving guests (allocation), track when guests check out so the rooms can be reused (deallocation), and deal with disasters: double-booking the same room (use-after-free), a room left locked with a guest inside who can never leave (memory leak), and guests who each insist the other should check out first (reference cycles). Every language makes a different design choice about who is responsible for these tasks — the programmer, the compiler, or a background collector — and each choice carries real tradeoffs in performance, safety, and predictability.

#### Learning Goals

By the end of this activity, you will be able to:

- Trace the call stack through a recursive function call, drawing the frame layout (local variables, return address, parent-frame pointer) at each push and pop
- Distinguish stack allocation from heap allocation, and explain why closures, objects, and long-lived data must live on the heap
- Describe how CPython's reference-counting collector reclaims objects immediately on zero-reference and how a cycle-detector handles reference cycles that reference counting alone cannot collect
- Explain how generational garbage collection exploits the generational hypothesis to reduce pause times, and identify the implication for your interpreter's environment and AST-node allocation strategy

> **Prerequisites:** Python programming; familiarity with functions and recursion; basic familiarity with the interpreter project
> **Goal:** Understand how programs manage memory — call stacks, heap allocation, reference counting, mark-and-sweep GC, Python's generational collector — and what this means for your interpreter implementation.

**POGIL Roles:** Driver · Recorder · Reporter · Manager

---

> **Before You Begin — Prerequisite Checklist**
>
> Before starting this activity, make sure you can answer yes to each of the following:
>
> - [ ] I can write a recursive Python function and explain what happens when it calls itself.
> - [ ] I know that Python variables hold references (not the values themselves) and that `a = b` does not copy a list.
> - [ ] I have seen the term "garbage collection" before, even if I cannot yet explain how it works.
> - [ ] I am working on (or have read the spec for) a tree-walking interpreter in Python.
>
> If any box is unchecked, spend five minutes on it before proceeding — the CTQs build on these ideas.

---

### Part I: The Call Stack

#### Model 1: Stack Frames and Recursive Calls

**Intuition.** Picture a stack of cafeteria trays. Every time a function calls another function, a new tray is placed on top. Each tray holds exactly the information that function needs to do its job: its local variables, where to return when done, and a reference back to the tray below. When a function returns, its tray is lifted off and discarded — instantly and automatically. The stack only ever grows and shrinks from the top, which makes it the fastest and simplest memory region in any program. The cost: a tray can only hold items that are needed *during* that one function call and no longer. Anything that needs to outlive the call must live somewhere else — the heap.

Every function call pushes a **frame** onto the call stack. Each frame holds:
- The function's local variables and parameters
- The return address (where execution resumes after the call returns)
- A link to the caller's frame

When a function returns, its frame is **popped** and memory is immediately reclaimed.

```python
import sys

def factorial(n, depth=0):
    indent = "  " * depth
    frame = sys._getframe()
    print(f"{indent}→ factorial({n})  [frame depth ~{depth}]")
    if n <= 1:
        result = 1
    else:
        result = n * factorial(n - 1, depth + 1)
    print(f"{indent}← returning {result}")
    return result

print("=== Call stack trace for factorial(5) ===")
print(f"Result: {factorial(5)}")
print()
print("=== Stack depth limit ===")
print(f"Python default recursion limit: {sys.getrecursionlimit()}")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

**Key observations:**
- Each recursive call creates a new frame; frames stack up during recursion.
- The stack is **LIFO**: last in, first out. Frames are popped in reverse order of creation.
- Python's default recursion limit is 1000 frames — exceeding it raises `RecursionError`.

> **Watch out!** A common misconception is that "stack overflow" means you used too much total memory. In reality, Python raises `RecursionError` after just 1000 *nested* calls — even if each frame is tiny. The limit is about *depth*, not total size. Your interpreter will hit this limit if it evaluates deeply recursive programs by making Python function calls for each recursive step.

> **Critical Thinking Questions 1–3**

**CTQ 1.** When `factorial(5)` calls `factorial(4)`, what four pieces of information are stored in the new stack frame for `factorial(4)`?

[[___ your answer here ___]]

**CTQ 2.** After `factorial(1)` returns `1`, in what order are the remaining frames popped? What does this tell you about LIFO order?

[[___ your answer here ___]]

**CTQ 3.** Tail-call optimization (TCO) allows compilers to reuse a stack frame for a tail-recursive call instead of pushing a new one. Python does NOT implement TCO. Give one design reason why Python's creators chose not to implement it.

[[___ your answer here ___]]

---

### Part II: The Heap

#### Model 2: Heap Allocation and Object Identity

**Intuition.** If the stack is a stack of cafeteria trays, the heap is the hotel storage room — a large, unstructured space where items can be placed at any time, can stay as long as needed, and can be shared by multiple guests pointing to the same locker. The key difference: the storage room does not clean itself up automatically when a guest leaves. Something (or someone) must decide when each item is no longer needed and reclaim the space. In Python, every object you create — a list, a dict, a function, even a small integer that falls outside the cache range — lives in this storage room. A variable name is just a label that points to a locker; assigning one variable to another creates a second label pointing to the *same* locker, not a copy of the contents.

The **heap** is the region of memory where objects with dynamic lifetime are allocated. Unlike the stack (which is automatically managed by function calls/returns), heap objects live until explicitly freed or collected by a garbage collector.

In Python, every object — integers, strings, lists, class instances — lives on the heap. Variables are references (pointers) to heap objects.

```python
import sys

# Every Python object is on the heap
x = [1, 2, 3]
y = x           # y is an alias — same heap object
z = [1, 2, 3]   # z is a different heap object with the same value

print("=== Object identity (memory address) ===")
print(f"id(x) = {id(x)}")
print(f"id(y) = {id(y)}  (same as x? {id(x) == id(y)})")
print(f"id(z) = {id(z)}  (same as x? {id(x) == id(z)})")
print()

print("=== Mutation through alias ===")
y.append(4)
print(f"After y.append(4): x = {x}")  # x also changed!
print()

print("=== Object sizes on the heap ===")
objects = [42, 3.14, "hello", [1,2,3], {"a": 1}, (1,2)]
for obj in objects:
    print(f"  {repr(obj):<20}  sys.getsizeof = {sys.getsizeof(obj)} bytes")
print()

print("=== Small integer caching ===")
a = 256
b = 256
c = 257
d = 257
print(f"256 is 256: {a is b}")   # True — CPython caches -5..256
print(f"257 is 257: {c is d}")   # False — outside cache range
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

> **Critical Thinking Questions 4–6**

**CTQ 4.** `y = x` does NOT copy the list — it creates an alias. Draw a memory diagram showing `x`, `y`, and `z` as pointers to heap objects after all three assignments.

[[___ your answer here ___]]

**CTQ 5.** After `y.append(4)`, why does `x` also show `[1, 2, 3, 4]`? How does this relate to aliasing?

[[___ your answer here ___]]

**CTQ 6.** CPython caches small integers (-5 to 256) so that `a = 256; b = 256; a is b` is `True`. What memory optimization does this achieve? What problem could it cause if a programmer mistakenly uses `is` instead of `==` for value comparisons?

[[___ your answer here ___]]

---

### Part III: Reference Counting

#### Model 3: Reference Counting — How CPython Frees Memory

**Intuition.** Reference counting is like a hotel room that has a small counter on the door showing how many guests currently have a key. When a new guest gets a key, the counter goes up. When a guest returns their key, the counter goes down. When the counter hits zero, the room is immediately available for the next guest — no housekeeping manager needs to make rounds; the room cleans itself the moment it becomes empty. This is CPython's primary strategy: every Python object carries a hidden integer counting how many variables (and internal structures) point to it. The beauty is speed and predictability — cleanup is instant and local. The flaw: if two guests each have each other's room number written on a note inside their rooms, both room counters stay at 1 even after both guests have left, so the rooms are never freed.

CPython's primary memory management strategy is **reference counting**: every heap object carries a counter of how many references point to it. When the counter reaches zero, the object is immediately freed.

```python
import sys
import gc

class Tracked:
    def __init__(self, name):
        self.name = name
        print(f"  [+] {name} created")
    def __del__(self):
        print(f"  [-] {name} destroyed")

# We'll track reference counts manually using sys.getrefcount
# Note: getrefcount itself adds 1 (the argument reference), so subtract 1

print("=== Reference counting demo with a list ===")
lst = [10, 20, 30]
print(f"After creation:      refcount = {sys.getrefcount(lst) - 1}")

alias = lst
print(f"After alias = lst:   refcount = {sys.getrefcount(lst) - 1}")

another = alias
print(f"After another = ...: refcount = {sys.getrefcount(lst) - 1}")

del alias
print(f"After del alias:     refcount = {sys.getrefcount(lst) - 1}")

del another
print(f"After del another:   refcount = {sys.getrefcount(lst) - 1}")

print()
print("=== The cycle problem ===")
# Reference cycles prevent refcounting from freeing objects
gc.disable()   # disable cyclic GC so we can see the leak

a = {"name": "A"}
b = {"name": "B"}
a["other"] = b   # a → b
b["other"] = a   # b → a  (cycle!)

print(f"a refcount: {sys.getrefcount(a) - 1}")  # 2 (lst var + b["other"])
print(f"b refcount: {sys.getrefcount(b) - 1}")  # 2 (lst var + a["other"])

del a, b   # remove our variables — but cycle keeps counts at 1 each
print("del a, b: objects still alive (cycle holds count > 0)")
print(f"GC counts (unreachable cyclic objects): {gc.get_count()}")

gc.enable()
gc.collect()
print(f"After gc.collect(): {gc.get_count()}")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

**Key insight:** Reference counting is fast (immediate deallocation, no GC pauses for non-cyclic objects) but **cannot handle cycles**: if object A holds a reference to B and B holds a reference to A, both counts stay above zero even when neither is reachable from the program.

> **Watch out!** Students often think `del x` destroys the object. It does not. `del x` removes the variable name `x` from the current scope, which *decrements* the reference count by one. The object is only destroyed when that count reaches **zero**. If another variable or data structure still points to the same object, `del x` has no visible effect on the object itself.

> **Critical Thinking Questions 7–9**

**CTQ 7.** When `del alias` is executed, what exactly happens to the reference count? Is the object freed at that point? Why or why not?

[[___ your answer here ___]]

**CTQ 8.** After `del a, b`, both `a` and `b` have reference count 1 (from the cycle). Draw the reference graph showing why neither object is freed.

[[___ your answer here ___]]

**CTQ 9.** Rust uses ownership and borrow-checking (compile-time) to achieve memory safety without any garbage collector. What does Rust *not* allow that Python does allow, in order to make this work?

[[___ your answer here ___]]

---

### Part IV: Mark-and-Sweep and Generational Collection

#### Model 4: Mark-and-Sweep Garbage Collection

**Intuition.** Mark-and-sweep is like a hotel manager who, every so often, walks through the entire building with a clipboard. Starting from the front desk (the program's roots — global variables and stack variables), the manager follows every key and every "room 203 can access room 411" note, marking each room that is reachable. After the full walk, any room not marked is abandoned — nobody can get to it, so it is safe to clean out and reassign. The mark phase is the walk; the sweep phase is the cleaning crew following behind. This approach handles cycles cleanly (the E→F→E loop in the example below is never reached from the front desk, so both rooms are collected), but it requires pausing the entire hotel while the manager walks — every live object must be visited every collection cycle.

When reference counting fails (cycles), a **tracing garbage collector** is needed. The classic algorithm is **mark-and-sweep**:

1. **Mark phase:** Starting from all *roots* (global variables, stack variables), traverse all reachable objects and mark them.
2. **Sweep phase:** Scan the entire heap; any unmarked object is garbage and can be freed.

```python
# Simulate mark-and-sweep on a simple object graph
# Objects are dicts with an "id", "refs" (list of object ids), and "marked" flag

def build_heap():
    heap = {
        "A": {"id": "A", "refs": ["B", "C"], "marked": False},
        "B": {"id": "B", "refs": ["D"],      "marked": False},
        "C": {"id": "C", "refs": [],          "marked": False},
        "D": {"id": "D", "refs": ["D"],       "marked": False},  # self-loop
        "E": {"id": "E", "refs": ["F"],       "marked": False},  # unreachable
        "F": {"id": "F", "refs": ["E"],       "marked": False},  # cycle, unreachable
    }
    return heap

def mark(heap, obj_id):
    obj = heap[obj_id]
    if obj["marked"]:
        return   # already visited (handles cycles)
    obj["marked"] = True
    for ref in obj["refs"]:
        mark(heap, ref)

def sweep(heap):
    freed = []
    for obj_id, obj in list(heap.items()):
        if not obj["marked"]:
            freed.append(obj_id)
            del heap[obj_id]
    return freed

# Roots: A is reachable (e.g., a global variable); E, F are not
roots = ["A"]
heap = build_heap()

print("=== Before GC ===")
print(f"Heap objects: {sorted(heap.keys())}")
print()

print("=== Mark phase ===")
for root in roots:
    mark(heap, root)
for obj_id, obj in heap.items():
    status = "REACHABLE" if obj["marked"] else "UNREACHABLE"
    print(f"  {obj_id}: {status}")
print()

print("=== Sweep phase ===")
freed = sweep(heap)
print(f"Freed (garbage): {freed}")
print(f"Surviving objects: {sorted(heap.keys())}")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

**Why E and F are collected:** Even though E→F→E forms a cycle, neither is reachable from any root. The mark phase never visits them, so the sweep phase frees both.

> **Critical Thinking Questions 10–12**

**CTQ 10.** In the mark phase, what would happen if we did NOT check `if obj["marked"]: return`? Trace through object D (which has a self-loop) to show the problem.

[[___ your answer here ___]]

**CTQ 11.** The sweep phase scans the **entire heap**. For a program with 10 million live objects and 1000 pieces of garbage, how much work does a single GC cycle do? Why is this a concern for real-time or interactive applications?

[[___ your answer here ___]]

**CTQ 12.** Java's garbage collector uses **generational** collection to address the cost you identified in CTQ 11. What is the **generational hypothesis** that makes this optimization valid?

[[___ your answer here ___]]

---

#### Model 5: Python's Generational GC and the `gc` Module

**Intuition.** The generational trick is based on a simple observation about hotel guests: most people who check in for one night are gone the next morning, but guests who have been there for a week are probably there for a while longer. It is wasteful to inspect long-stay guests every morning. Instead, the hotel divides rooms into three wings: the "new arrivals" wing (generation 0), checked every morning; the "short stay" wing (generation 1), checked weekly; and the "long stay" wing (generation 2), checked monthly. An object that survives a collection in generation 0 is moved to generation 1, and so on. Because most objects die young (a temporary list created during one expression evaluation is gone within milliseconds), the frequent gen-0 sweeps catch most garbage with very little work, and the expensive full-heap sweep is needed only rarely.

Python uses **two complementary strategies**:

1. **Reference counting** (primary): frees most objects immediately when their count hits zero.
2. **Cyclic GC** (secondary): handles cycles that reference counting misses.

The cyclic GC is **generational**, dividing objects into three generations:

- **Generation 0 (young):** Newly allocated objects. Collected frequently — every ~700 net allocations by default.
- **Generation 1 (middle-aged):** Objects that survived one gen-0 collection. Collected less often.
- **Generation 2 (old):** Objects that survived a gen-1 collection. Collected rarely.

When a generation is collected, any object that survives is **promoted** to the next generation. The intuition: if an object survived the first sweep, it is likely to survive many more, so it costs less to scan it infrequently.

**CPython's full strategy:**

1. **Primary mechanism: reference counting.** Every `Py_INCREF`/`Py_DECREF` in the C runtime. Frees most objects immediately.
2. **Secondary mechanism: cyclic GC (`gc` module).** Handles the reference cycles that refcounting misses. Uses a variant of mark-and-sweep restricted to objects that could participate in cycles (containers: lists, dicts, class instances, closures).

The combination means most memory is freed instantly (no GC pause for non-cyclic objects), and cycles are collected periodically by the generational collector.

```python
import gc
import sys

print("=== Python's generational GC configuration ===")
print(f"GC enabled: {gc.isenabled()}")
thresholds = gc.get_threshold()
print(f"Thresholds: gen0={thresholds[0]}, gen1={thresholds[1]}, gen2={thresholds[2]}")
print(f"  Meaning: gen0 collected after {thresholds[0]} (allocs - frees)")
print(f"           gen1 collected after {thresholds[1]} gen0 collections")
print(f"           gen2 collected after {thresholds[2]} gen1 collections")

print()
stats = gc.get_stats()
for i, s in enumerate(stats):
    print(f"  gen{i}: collections={s['collections']}, "
          f"collected={s['collected']}, "
          f"uncollectable={s['uncollectable']}")

print()
print("=== Demonstrating cycle collection ===")

class CyclicNode:
    def __init__(self, name):
        self.name = name
        self.other = None
    def __repr__(self):
        return f"Node({self.name})"

# Disable GC to show raw refcounting cannot handle cycles
gc.disable()
counts_before = gc.get_count()
print(f"counts before creating cycle: {counts_before}")

n1 = CyclicNode("X")
n2 = CyclicNode("Y")
n1.other = n2
n2.other = n1

del n1, n2   # refcounting cannot free them; cycle keeps counts > 0
counts_after = gc.get_count()
print(f"counts after del (GC disabled, cycle leaked): {counts_after}")

gc.enable()
collected = gc.collect(0)   # force gen0 collection
print(f"gc.collect(0) freed {collected} objects from the cycle")

print()
print("=== Reference count live demo ===")
lst = [1, 2, 3]
print(f"refcount of [1,2,3]:  {sys.getrefcount(lst) - 1}")
a = lst
print(f"after a = lst:        {sys.getrefcount(lst) - 1}")
del a
print(f"after del a:          {sys.getrefcount(lst) - 1}")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

> **Critical Thinking Questions 13–15**

**CTQ 13.** The generational hypothesis says most objects die young. Give two concrete examples of short-lived objects your interpreter creates during evaluation, and one example of a long-lived object.

[[___ your answer here ___]]

**CTQ 14.** Python collects gen0 after every 700 net allocations. Why is this threshold not 1 (collect after every allocation) and not 1,000,000 (almost never)?

[[___ your answer here ___]]

**CTQ 15.** Why does CPython's cyclic GC only consider "container" objects (lists, dicts, sets, class instances) and not integers or strings?

[[___ your answer here ___]]

---

### Part V: Implications for Your Interpreter

#### Model 6: Interpreter Memory on the Host Heap

**Intuition.** Your interpreter is a Python program that *simulates* another program. That means every "variable" in the language you are interpreting becomes a Python object on Python's own heap. Every time your interpreter evaluates a function call, it creates a new `Environment` Python object. Every closure your language creates is a Python object holding a reference to an `Environment`. You are not just dealing with Python's memory model — you are building a second memory model *inside* Python's memory model. The chains of `Environment` objects are your interpreter's call stack, living entirely on Python's heap. A poorly designed interpreter can exhaust heap memory with deeply recursive programs even before Python's recursion limit is hit, because each frame in the *interpreted* language corresponds to a heap-allocated `Environment` object, not a Python stack frame.

Your interpreter is written in Python. Every data structure you create — `Environment` objects, `Closure` objects, AST nodes — is a Python heap allocation. Python's own garbage collector manages them. This section explores what that means for interpreter memory behavior.

```python
import sys
import gc
from dataclasses import dataclass, field
from typing import Any, Optional, Dict

@dataclass
class Environment:
    bindings: Dict[str, Any] = field(default_factory=dict)
    parent: Optional['Environment'] = None

    def lookup(self, name: str) -> Any:
        if name in self.bindings:
            return self.bindings[name]
        if self.parent is not None:
            return self.parent.lookup(name)
        raise NameError(f"undefined: {name!r}")

@dataclass
class Closure:
    param: str
    body: str    # simplified: just a label
    env: Environment

print("=== Building a chain of 5 environments (simulating 5 nested calls) ===")
env = None
for i in range(5):
    new_env = Environment(bindings={f"x{i}": i * 10}, parent=env)
    env = new_env
    print(f"  env{i}: ~{sys.getsizeof(new_env)} bytes (dataclass shell only), x{i}={i*10}")

print(f"\nLooking up x0 from deepest env requires 5 parent-chain hops:")
print(f"  x0 = {env.lookup('x0')}")

# A closure captures its entire defining environment chain
closure = Closure("n", "n * n", env)
print(f"\nClosure object shell: ~{sys.getsizeof(closure)} bytes")
print("But the closure keeps the ENTIRE env chain alive via the .env pointer.")
print("If the env chain is large, the closure is a large memory root.")

# Demonstrate that the env chain stays alive as long as the closure lives
print("\n=== Releasing the env chain directly ===")
env_top = env
del env, new_env
gc.collect()
print("  del env, new_env -- but closure still holds a ref to the top env!")
print(f"  env still reachable via closure.env: {closure.env.bindings}")

print("\n=== Releasing the closure releases the chain ===")
del closure, env_top
gc.collect()
print("  gc.collect() done -- chain is now freed (no more live references).")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

The critical insight: your interpreter creates a new `Environment` Python object for every function call and every `let` binding. Each `Environment` holds a reference to its parent. A closure holds a reference to the environment where it was defined. Therefore:

- A deeply recursive program builds a long chain of `Environment` objects on Python's heap.
- A closure defined inside a deeply nested scope keeps that entire chain alive.
- If you store closures in long-lived data structures (e.g., a list of callbacks), all the environments those closures captured live as long as the list does.

> **Watch out!** A closure does not capture a *copy* of the environment — it captures a *reference* to the live `Environment` object. This means if the same environment object is mutated after the closure is created (for example, by a `set!` or assignment operation in the interpreted language), the closure sees the new value. This is intentional in languages like Python and Scheme, but surprises students who expect closures to "freeze" their environment at creation time.

> **Critical Thinking Questions 16–18**

**CTQ 16.** Your interpreter creates a new `Environment` object for every function call. Why does this mean a deeply recursive program can exhaust heap memory even if the Python call stack hasn't overflowed?

[[___ your answer here ___]]

**CTQ 17.** A closure captures its defining environment. If a function defined at top level closes over a large module-level dictionary, will that dictionary be freed when the function is no longer used? Why or why not?

[[___ your answer here ___]]

**CTQ 18.** Connect to language design: what is the tradeoff between **closures that capture by reference** (Python style — the env binding is shared) versus **closures that capture by value** (copy the binding on creation)?

[[___ your answer here ___]]

---

#### Critical Thinking Questions — Synthesis

**CTQ 19.** Place the three memory management strategies (reference counting, mark-and-sweep, manual `malloc`/`free`) in order from highest to lowest on each axis: (a) programmer cognitive burden, (b) risk of use-after-free bugs, (c) risk of memory leaks from cycles, (d) GC pause latency.

[[___ your answer here ___]]

**CTQ 20.** Rust eliminates all three strategies in favor of compile-time ownership. What does Rust's ownership system prevent that the other three strategies rely on?

[[___ your answer here ___]]

---

#### Multiple Choice Review

**Question 1.** Python's reference counting immediately frees an object when:

- [( )] The `del` keyword is used on any name bound to the object
- [(X)] The object's reference count drops to zero
- [( )] The garbage collector's mark phase marks it as dead
- [( )] The object goes out of lexical scope

**Question 2.** Which of the following CANNOT be freed by reference counting alone?

- [( )] A string with one reference
- [( )] A list appended to another list
- [(X)] Two objects that reference each other but are reachable from no root
- [( )] A function object stored in a local variable

**Question 3.** In Python's generational GC, generation 0 objects are:

- [(X)] Newly allocated; collected most frequently
- [( )] Long-lived; collected most frequently
- [( )] Collected only when the program exits
- [( )] Objects that have survived at least two collections

**Question 4.** In the mark-and-sweep algorithm, the **sweep phase**:

- [( )] Traverses all live references from the roots
- [(X)] Frees every heap object that was not marked as reachable
- [( )] Updates reference counts for each live object
- [( )] Compacts live objects to eliminate heap fragmentation

---

#### Exercises

**Exercise 1.** Modify the call stack simulation to track the maximum depth reached and the total number of frames pushed and popped. Try `factorial(10)` and `factorial(20)`:

```python
import sys

call_count = [0]
max_depth = [0]

def factorial(n, depth=0):
    call_count[0] += 1
    max_depth[0] = max(max_depth[0], depth)
    if n <= 1:
        return 1
    return n * factorial(n - 1, depth + 1)

for n in [5, 10, 15]:
    call_count[0] = 0
    max_depth[0] = 0
    result = factorial(n)
    print(f"factorial({n}) = {result}, calls={call_count[0]}, max_depth={max_depth[0]}")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

**Exercise 2.** Demonstrate aliasing vs. copying. Show that `list.copy()` creates a shallow copy (aliases inner objects) but `copy.deepcopy()` creates a fully independent copy:

```python
import copy

original = [[1, 2], [3, 4]]
shallow  = original.copy()
deep     = copy.deepcopy(original)

original[0].append(99)

print(f"original: {original}")
print(f"shallow:  {shallow}")   # inner list IS shared
print(f"deep:     {deep}")      # fully independent
print()
print(f"shallow[0] is original[0]: {shallow[0] is original[0]}")
print(f"deep[0]    is original[0]: {deep[0]    is original[0]}")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

**Exercise 3.** Build a reference-counting simulation. Implement an `RCObject` class with `inc_ref`, `dec_ref`, and `__del__` tracking. Create a cycle and show it leaks under pure refcounting:

```python
class RCObject:
    _registry = {}
    _next_id = [0]

    def __init__(self, name):
        self.name = name
        self.ref_count = 0
        self.refs = []
        RCObject._registry[name] = self

    def inc_ref(self):
        self.ref_count += 1

    def dec_ref(self):
        self.ref_count -= 1
        if self.ref_count == 0:
            print(f"  [freed] {self.name}")
            for r in self.refs:
                r.dec_ref()
            del RCObject._registry[self.name]

    def link(self, other):
        self.refs.append(other)
        other.inc_ref()

# Non-cyclic case
print("=== Non-cyclic: A → B ===")
a = RCObject("A")
b = RCObject("B")
a.inc_ref()   # root holds A
b.inc_ref()   # root holds B
a.link(b)
a.dec_ref()   # root drops A → A freed, then B freed
b.dec_ref()

print()
print("=== Cyclic: X ↔ Y (leak!) ===")
x = RCObject("X")
y = RCObject("Y")
x.inc_ref()   # root holds X
y.inc_ref()   # root holds Y
x.link(y)     # X → Y
y.link(x)     # Y → X  (cycle)
x.dec_ref()   # root drops X  -- X.ref_count = 1 (from Y), not freed
y.dec_ref()   # root drops Y  -- Y.ref_count = 1 (from X), not freed
print(f"Leaked: {list(RCObject._registry.keys())}")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

**Exercise 4.** Extend the mark-and-sweep simulation from Model 4 with a `compact` phase that renumbers objects after collection. Show that the freed slots are reusable:

```python
def build_heap():
    return {
        "A": {"refs": ["B", "C"], "marked": False, "data": "root"},
        "B": {"refs": ["D"],      "marked": False, "data": "live"},
        "C": {"refs": [],         "marked": False, "data": "live"},
        "D": {"refs": [],         "marked": False, "data": "live"},
        "E": {"refs": ["F"],      "marked": False, "data": "garbage"},
        "F": {"refs": ["E"],      "marked": False, "data": "garbage"},
    }

def mark(heap, obj_id, visited=None):
    if visited is None:
        visited = set()
    if obj_id in visited:
        return
    visited.add(obj_id)
    heap[obj_id]["marked"] = True
    for ref in heap[obj_id]["refs"]:
        mark(heap, ref, visited)

def sweep(heap):
    freed, live = [], []
    for obj_id in list(heap.keys()):
        if not heap[obj_id]["marked"]:
            freed.append(obj_id)
            del heap[obj_id]
        else:
            live.append(obj_id)
    return freed, live

heap = build_heap()
mark(heap, "A")
freed, live = sweep(heap)
print(f"Freed:    {freed}")
print(f"Survived: {live}")
print(f"Available slots for new allocations: {freed}")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

**Exercise 5.** Write an interpreter memory profiler: simulate evaluating 1000 calls of a function that returns a new list, and track how many `Environment` objects are alive at any point. Use `gc.get_objects()` to count live instances:

```python
import gc
from dataclasses import dataclass, field
from typing import Any, Optional, Dict

@dataclass
class Environment:
    bindings: Dict[str, Any] = field(default_factory=dict)
    parent: Optional['Environment'] = None

def count_envs():
    gc.collect()
    return sum(1 for obj in gc.get_objects() if isinstance(obj, Environment))

# Simulate a function that creates an env for each call but returns immediately
global_env = Environment(bindings={"pi": 3.14})

print(f"Before simulation: {count_envs()} Environment objects alive")

results = []
for i in range(100):
    call_env = Environment(bindings={"n": i}, parent=global_env)
    result = call_env.lookup("n") * call_env.lookup("pi")
    # call_env goes out of scope here — should be freed immediately

print(f"After 100 calls (no closures stored): {count_envs()} Environment objects")

# Now store closures that capture their envs
@dataclass
class Closure:
    param: str
    body: str
    env: Environment

closures = []
for i in range(100):
    call_env = Environment(bindings={"captured": i}, parent=global_env)
    closures.append(Closure("x", "captured + x", call_env))

print(f"After storing 100 closures: {count_envs()} Environment objects")
del closures
gc.collect()
print(f"After del closures: {count_envs()} Environment objects")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

---

#### Reflection

1. Your interpreter evaluates programs by building `Environment` chains. Under what conditions might a user's program trigger **memory exhaustion** even though no single object is unusually large? Propose one mitigation strategy.

2. Python's reference counting gives **deterministic destruction** (objects die immediately when unreachable). Java's GC gives **non-deterministic destruction** (objects may linger). For a language that opens files in its `__del__` method, which strategy is safer? Why?

3. A production interpreter (CPython, JVM, V8) must balance: collection frequency, pause length, throughput, and memory overhead. Pick two of these and explain the fundamental tension between them.

---

#### Further Reading

- **CPython memory management source:** `Objects/obmalloc.c`, `Modules/gcmodule.c`
- **Python docs:** `gc` module — `gc.collect()`, `gc.get_threshold()`, `gc.get_objects()`
- **Article:** *Garbage Collection for Python* — original design notes by Neil Schemenauer
- **Book:** *The Garbage Collection Handbook* — Jones, Hosking, Moss (definitive reference)
- **Rust ownership model:** *The Rust Programming Language*, Chapter 4 — Understanding Ownership

---

*End of Activity — Memory Management: Call Stack, Heap, Reference Counting, Mark-and-Sweep, Generational GC*

---

## Going Deeper: Concurrency Models: Actors, Channels, and Transactions

> **Opening Hook — The Restaurant Kitchen Analogy**
>
> Concurrency is like coordinating a busy kitchen. In a chaotic kitchen, all the chefs share the same pot — one chef adds salt while another stirs, and a third tastes to decide if it needs more. The result is unpredictable: the counter is wrong, the soup is over-salted, and nobody agrees on whose fault it is. This is **shared mutable state** — the root of race conditions, data corruption, and bugs that only appear under load. Language designers have proposed three main escapes: **actors** (each chef has their own station and their own pot; dishes are passed forward as finished items), **channels** (chefs communicate by placing items on a conveyor belt — the sender pauses until the receiver picks it up), and **transactions** (any chef can modify the shared pot, but changes only "commit" if nobody else changed the same ingredient in the meantime; otherwise the step is retried). All three approaches solve the same problem — coordinating concurrent work without chaos — but each imposes different constraints on how you structure your program.

#### Learning Goals

By the end of this activity, you will be able to:

- Explain why shared mutable state causes data races, and demonstrate a race condition in Python using threads and a shared counter
- Implement the actor model using Python queues to pass immutable messages between independent workers, and explain how actors eliminate shared state
- Implement channel-based communication following the CSP model, distinguishing synchronous from buffered channels and explaining rendezvous semantics
- Compare actors, channels, and software transactional memory (STM) across the dimensions of composability, error handling, and suitability for different concurrency patterns

> **Before You Begin — Prerequisite Checklist**
>
> Before starting this activity, confirm you can answer yes to each of the following:
>
> - [ ] I know what a Python `threading.Thread` is and can write a program that starts two threads.
> - [ ] I understand that two threads running simultaneously can read and write the same variable, and I have a rough sense of why that is dangerous.
> - [ ] I have seen the word "mutex" or "lock" before, even if I have not used one in Python.
> - [ ] I completed (or reviewed) the Parallelism module, which established that pure functions are safe to parallelize.
>
> If any box is unchecked, review the Python `threading` documentation or the Parallelism activity before proceeding.

The Parallelism module showed that pure functions parallelize automatically — but programs also need *concurrency*: multiple activities interleaved in time, coordinating via communication. The language designer's central choice is **what primitive does the language expose for that coordination**? Three answers dominate modern languages: **actors** (Erlang, Akka) exchange immutable messages; **channels** (Go, Occam, CSP) synchronize on named conduits; **transactions** (Haskell STM, Clojure) compose atomic blocks. All three eliminate shared mutable state — but by different means, with different tradeoffs, suitable for different programs. The arc: **the coordination problem → actors → channels/CSP → STM → the π-calculus as foundation**.

---

#### Directions and Group Roles

Work in your POGIL team with rotated roles (**Manager**, **Recorder**, **Presenter**, **Reflector**). Each Part is implemented in Python, but the focus is the *model*, not the API. The Recorder posts a comparison table at the end. After class, respond to the reflective prompt individually in your notebook.

---

### Part I: The Coordination Problem

#### 1. Why Shared Memory Fails

**Intuition.** A single `counter.value += 1` looks atomic, but the processor actually executes three steps: (1) read the current value into a register, (2) add one, (3) write the result back. If two threads interleave these steps — thread A reads 42, thread B reads 42, thread A writes 43, thread B writes 43 — one increment is silently lost. This is a **race condition**: the program's output depends on the unpredictable timing of thread scheduling. Race conditions are notoriously hard to reproduce (they may appear only under heavy load) and hard to debug (adding print statements changes the timing enough to make them disappear). The model below demonstrates this concretely.

The Parallelism module established: pure functions are safe to parallelize. The hard part is the rest of the program — the stateful services, the shared counters, the bounded buffers. Shared mutable state under concurrency is the source of race conditions, deadlocks, and livelocks. Language designers have sought primitives that **eliminate** sharing as a root cause, rather than requiring programmers to manage it correctly with locks.

```python
try:
    import threading, time

    # Classic race condition: shared counter without synchronization
    class BrokenCounter:
        def __init__(self): self.value = 0
        def increment(self): self.value += 1   # read-modify-write: NOT atomic

    counter = BrokenCounter()
    threads = [threading.Thread(target=lambda: [counter.increment() for _ in range(1000)])
               for _ in range(10)]
    for t in threads: t.start()
    for t in threads: t.join()

    print(f"Expected: 10000, Got: {counter.value}  (deficit = {10000 - counter.value})")
    print("(Run multiple times to see non-determinism)")

except Exception as e:
    print(f"[conc:race] {e}")
    import traceback; traceback.print_exc()
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

> **Watch out!** CPython's Global Interpreter Lock (GIL) actually makes many Python race conditions *less* visible than they would be in Java or C++, because the GIL prevents two threads from executing Python bytecodes simultaneously. You may not always see the deficit above. But the race is still real — the GIL is released between bytecodes, not between the three steps of read-modify-write. For CPU-bound work or when using C extensions that release the GIL, races appear in full force.

---

### Part II: The Actor Model

#### 2. Actors: No Sharing, Only Messages

**Intuition.** The actor model is the "each chef has their own station" solution. An actor is a tiny, self-contained process with its own private state and its own mailbox (an inbox queue). No other actor can reach in and modify that state — the only thing one actor can do to another is *drop a message in its mailbox*. The receiving actor picks up messages one at a time, processes each one, updates its own state, and optionally sends messages onward. Because nothing is shared, there are no races. Because messages are queued, no message is lost. The price: communication is asynchronous — the sender does not wait for a reply, which makes "call and wait for result" patterns more complex than a simple function call.

An **actor** is a unit of computation with:
- Its own **private state** (no other actor touches it)
- A **mailbox** (a queue of incoming messages)
- A **behavior** function: when a message arrives, compute new state and optionally send messages to other actors

This is Erlang's model (and Akka for JVM). Because no state is shared, there are no races. The only coordination is message passing — and messages are **copied** (or immutable) so the sender retains nothing.

```python
try:
    import threading, queue, time

    class Actor(threading.Thread):
        def __init__(self, name, behavior):
            super().__init__(daemon=True)
            self.name = name
            self.mailbox = queue.Queue()
            self.behavior = behavior
            self._state = {}
            self.start()

        def send(self, msg):
            self.mailbox.put(msg)

        def run(self):
            while True:
                msg = self.mailbox.get()
                if msg == 'STOP': break
                self._state = self.behavior(msg, self._state) or self._state

    # A counter actor: messages are ('increment',) or ('get', reply_actor)
    def counter_behavior(msg, state):
        count = state.get('count', 0)
        if msg[0] == 'increment':
            return {'count': count + 1}
        if msg[0] == 'get':
            msg[1].send(('value', count))   # reply to the requester
        return state

    # A "printer" actor that just prints what it receives
    def printer_behavior(msg, state):
        print(f"  [printer] received: {msg}")
        return state

    printer = Actor('printer', printer_behavior)
    counter = Actor('counter', counter_behavior)

    # Send 100 increment messages — no race condition possible
    for _ in range(100):
        counter.send(('increment',))

    # Request the final count
    time.sleep(0.05)   # let the actor process the increments
    counter.send(('get', printer))
    time.sleep(0.05)

    counter.send('STOP')
    printer.send('STOP')

except Exception as e:
    print(f"[conc:actor] {e}")
    import traceback; traceback.print_exc()
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

---

#### Model 1: Actor Properties

**Intuition.** The code above shows a counter actor that is race-free by construction — not because of any lock, but because the counter's state (`state['count']`) is only ever read and written inside `counter_behavior`, which runs on a single thread (the actor's own thread). Any number of external threads can send `('increment',)` messages, but those messages are queued and processed one at a time. The mailbox *is* the synchronization primitive.

##### Critical Thinking Questions

1. In the actor model, the counter's `count` variable is never shared — it lives only inside `counter_behavior`'s `state` dictionary. Why does this eliminate the race condition that the `BrokenCounter` had? What precisely is different?

2. The `get` message causes the counter to *send* a message back to the printer. This is **request-reply messaging**. How is this different from a function call that returns a value? (Hint: which is synchronous, which is asynchronous?)

3. **Fault tolerance.** Erlang's "let it crash" philosophy says: if an actor dies with an error, a *supervisor* actor restarts it. How does the mailbox abstraction enable this? What would happen to unprocessed messages if the actor crashes?

4. Two actors may send messages to each other simultaneously, causing a message in each mailbox. Neither blocks — they proceed. In a system with shared locks, both would instead wait for the other's lock: a **deadlock**. Explain why the actor model prevents this specific deadlock scenario structurally.

---

### Part III: Channels and CSP

#### 3. Go-Style Channels: Synchronize on Communication

**Intuition.** Channels solve the coordination problem differently: instead of isolating state inside actors, channels give you a *meeting point* — a named conduit where one goroutine (or thread) can hand a value directly to another. With an unbuffered channel, the sender pauses until the receiver arrives at the channel to collect, and vice versa. The two parties *rendezvous* at the channel, synchronizing their progress. With a buffered channel of size N, the sender can deposit up to N items without waiting, and slows down only when the buffer is full. This back-pressure mechanism is what prevents a fast producer from overwhelming a slow consumer.

**Communicating Sequential Processes** (CSP, Tony Hoare 1978) and Go's channels take a different view: concurrency is about *synchronization points*. A **channel** is a typed conduit; a send blocks until a receiver is ready, and vice versa (for unbuffered channels). Coordination happens *at the moment of communication*, not via shared state.

```python
try:
    import threading, queue, time

    # Python queue as a Go-style channel (unbuffered = queue size 0)
    def make_chan(buffered=0):
        return queue.Queue(maxsize=buffered if buffered else 0)

    def go(fn, *args):
        t = threading.Thread(target=fn, args=args, daemon=True)
        t.start()
        return t

    # Producer/Consumer using channels
    def producer(ch, n):
        for i in range(n):
            ch.put(i)           # send to channel (blocks if full)
            print(f"  sent {i}")
        ch.put(None)            # sentinel

    def consumer(ch, results):
        while True:
            item = ch.get()     # receive from channel (blocks if empty)
            if item is None: break
            results.append(item * item)
            print(f"  received {item}, computed {item*item}")

    ch = make_chan(buffered=2)   # buffer of 2
    results = []

    p = go(producer, ch, 5)
    c = go(consumer, ch, results)

    p.join(); c.join()
    print("Squares:", results)

except Exception as e:
    print(f"[conc:chan] {e}")
    import traceback; traceback.print_exc()
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

> **Watch out!** It is tempting to think that buffered channels eliminate blocking entirely. They do not — they only defer it. A sender on a buffered channel of size 2 will still block on the *third* send if the receiver has not consumed anything yet. Removing back-pressure entirely (by using an unbounded buffer) can cause the producer to race arbitrarily far ahead, consuming memory without bound. Back-pressure is a feature, not a limitation.

**Select: waiting on multiple channels.** Go's `select` statement blocks until *any* of several channels is ready — the CSP choice operator. This is how event loops and multiplexers are written without callbacks.

```python
try:
    import threading, queue, time, random

    def make_chan(): return queue.Queue()

    def go(fn, *args):
        t = threading.Thread(target=fn, args=args, daemon=True)
        t.start()
        return t

    # Simulate a "select" on two channels by using a merge channel
    def merge(ch1, ch2, out):
        def relay(ch):
            while True:
                v = ch.get()
                if v is None:
                    out.put(None); break
                out.put(v)
        go(relay, ch1)
        go(relay, ch2)

    ticker = make_chan()
    sensor = make_chan()
    merged = make_chan()
    merge(ticker, sensor, merged)

    def send_ticks(ch):
        for i in range(3):
            time.sleep(0.01)
            ch.put(f"tick-{i}")
        ch.put(None)

    def send_sensors(ch):
        for i in range(3):
            time.sleep(0.015)
            ch.put(f"temp={20 + i}")
        ch.put(None)

    go(send_ticks, ticker)
    go(send_sensors, sensor)

    done = 0
    while done < 2:
        msg = merged.get()
        if msg is None:
            done += 1
        else:
            print(f"  received: {msg}")

except Exception as e:
    print(f"[conc:select] {e}")
    import traceback; traceback.print_exc()
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

---

#### Model 2: Channels and CSP

**Intuition.** The `select` simulation above shows the fan-in pattern: two independent streams of events (ticks and sensor readings) are merged into one stream for a single consumer. In Go, `select` is built into the language; here we simulate it by spinning up relay threads. The key insight is that the *structure* of the communication topology — who sends to whom, through which channels, in what order — determines the program's concurrent behavior. CSP lets you reason about that structure precisely, which is why Go's concurrency model is considered one of the cleaner ones in production languages.

[[MC]]
In CSP/Go-style channels, an **unbuffered** channel's send operation blocks until a receiver is ready. What property does this enforce?
- ( ) The sender always finishes before the receiver starts
- (x) The send and receive happen simultaneously — the two goroutines/threads rendezvous at the channel
- ( ) Messages are dropped if no receiver is waiting
- ( ) The channel accumulates all messages until the receiver drains it

##### Critical Thinking Questions

5. The actor model and CSP both eliminate shared state. What is the key difference in *when* coordination occurs? (Hint: actors are asynchronous by default; CSP channels synchronize at send.)

6. Deadlock is still possible with channels: goroutine A waits to send on `ch1` while goroutine B waits to send on `ch2`, and neither will receive the other's message. How does Go's `select` statement break this deadlock? What would the equivalent in actor-based code look like?

7. **Pipeline composition.** CSP channels compose naturally: `producer | transformer | consumer` where each stage reads from one channel and writes to another. Write the three-stage pipeline in pseudocode using channels. How does this compare to Unix pipes (`cat file | grep pattern | wc -l`)?

8. The `merge` function above creates a new output channel and relays from two inputs. This is the **fan-in** pattern. What is the **fan-out** pattern, and how would you implement it?

---

### Part IV: Software Transactional Memory

#### 4. STM: Atomic Blocks Without Locks

**Intuition.** STM is the "optimistic" approach: let all the chefs work on their steps simultaneously, but at the moment each chef tries to commit their changes, check whether anyone else modified the same ingredient in the meantime. If so, undo the step and try again from scratch. If not, commit atomically. This is exactly how database transactions work, applied to in-memory variables. The key insight is that *conflicts are rare* in most programs, so the cost of occasionally retrying is lower than the cost of acquiring locks for every access. The critical constraint: the transaction body must be *pure* (no side effects like printing or writing to a file), because it may be executed more than once.

**Software Transactional Memory** (Haskell STM, Clojure refs) takes a third approach: allow threads to read and modify shared state, but inside **atomic transactions**. A transaction sees a consistent snapshot of memory; if two transactions conflict (both modified the same variable), one is *retried* automatically. No deadlocks: transactions don't hold locks, they just detect conflicts.

```python
try:
    import threading, time
    from copy import deepcopy

    # Minimal STM simulation: transactional references (TVar)
    class TVar:
        def __init__(self, value):
            self._value = value
            self._lock = threading.Lock()

        def read_committed(self):
            with self._lock: return self._value

        def write_committed(self, value):
            with self._lock: self._value = value

    class Transaction:
        def __init__(self):
            self._reads = {}    # TVar -> value at start
            self._writes = {}   # TVar -> new value

        def read(self, tvar):
            if tvar in self._writes: return self._writes[tvar]
            if tvar not in self._reads:
                self._reads[tvar] = tvar.read_committed()
            return self._reads[tvar]

        def write(self, tvar, value):
            self._writes[tvar] = value

        def commit(self):
            # Validate: check that read set hasn't changed
            for tvar, expected in self._reads.items():
                with tvar._lock:
                    if tvar._value != expected:
                        return False   # conflict — retry
            # Write
            for tvar, value in self._writes.items():
                tvar.write_committed(value)
            return True   # success

    def atomically(fn):
        """Run fn(transaction) atomically; retry on conflict."""
        attempts = 0
        while True:
            tx = Transaction()
            fn(tx)
            if tx.commit():
                return attempts + 1
            attempts += 1   # retry

    # Bank account transfer: atomically debit one, credit another
    alice = TVar(1000)
    bob   = TVar(500)

    def transfer(amount):
        def txn(tx):
            a = tx.read(alice)
            b = tx.read(bob)
            if a >= amount:
                tx.write(alice, a - amount)
                tx.write(bob, b + amount)
        return txn

    def do_transfer(amount, results, i):
        tries = atomically(transfer(amount))
        results[i] = (alice.read_committed(), bob.read_committed(), tries)

    results = [None] * 10
    threads = [threading.Thread(target=do_transfer, args=(50, results, i))
               for i in range(10)]
    for t in threads: t.start()
    for t in threads: t.join()

    print(f"Alice final: {alice.read_committed()}, Bob final: {bob.read_committed()}")
    print(f"Expected: Alice={1000-500}, Bob={500+500}")
    print(f"Total retries: {sum(r[2]-1 for r in results if r)}")

except Exception as e:
    print(f"[conc:stm] {e}")
    import traceback; traceback.print_exc()
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

> **Watch out!** STM's retry mechanism means the transaction body can execute *multiple times* before committing. Any code inside a transaction that has an irreversible side effect — printing output, writing to a file, sending a network packet — will happen multiple times if the transaction retries. This is why Haskell's type system uses `STM a` (a type that cannot perform IO) to make it *impossible* to write effectful code inside a transaction. In the Python simulation above, there is nothing stopping you from adding a `print` inside `txn` — but doing so would produce misleading output on retries.

---

#### Model 3: Transactions and Composability

**Intuition.** The bank transfer code above shows STM's greatest strength: composability. The `transfer` function is built from two reads and two writes, but the whole thing commits as a single atomic unit. If you tried to achieve the same thing with two locks (`alice_lock` and `bob_lock`), you would face the classic deadlock: thread 1 acquires `alice_lock` and waits for `bob_lock`, while thread 2 acquires `bob_lock` and waits for `alice_lock`. STM sidesteps this entirely because transactions do not hold locks — they just record what they read, attempt a write, and retry if the world changed.

##### Critical Thinking Questions

9. STM transactions can be composed: if `debit` and `credit` are each transactions, `transfer = debit AND credit` is also a transaction — and it is atomic as a unit. Why can't you compose lock-based operations this way? (What goes wrong if you write `def transfer(): debit_lock.acquire(); credit_lock.acquire(); ...`?)

10. If two transactions both read the same `TVar` and only one writes it, do they conflict? (Neither reads the other's write; both read the committed value.) What about two transactions both *writing* the same `TVar`? Which model do you think is correct, and why?

11. STM requires the transaction body to be **pure** (no irreversible side effects), because a retried transaction re-executes its body. What would go wrong if a transaction body printed to the console, and the transaction was retried 3 times?

12. Haskell's type system enforces STM purity: a `STM a` action can only be run inside `atomically`; it cannot perform IO. This is the same Curry-Howard connection as the IO monad — the type prevents the programmer from mixing transactional and effectful code. How does this relate to your interpreter's `ReturnSignal` exception: what would happen if a `return` statement inside a transaction could escape the transaction boundary?

---

### Part V: The π-Calculus — A Glimpse

#### 5. Mobile Channels as a Formal Foundation

The **π-calculus** (Milner 1992) is to concurrent computation what the lambda calculus is to functional computation: a minimal formal system with one primitive (channel name) and one operation (send/receive a name over a channel). Names are *mobile* — you can send a channel name over a channel, so the communication topology can change at runtime. Every actor system and every channel-based language can be encoded in the π-calculus.

The syntax is minimal:

$$
P, Q ::=\; 0 \quad\mid\quad \bar{x}\langle y \rangle.P \quad\mid\quad x(z).P \quad\mid\quad P \mid Q \quad\mid\quad \nu x.P \quad\mid\quad !P
$$

- $0$: the idle process
- $\bar{x}\langle y \rangle.P$: send name $y$ on channel $x$, then continue as $P$
- $x(z).P$: receive a name on channel $x$, bind it to $z$, continue as $P$
- $P \mid Q$: $P$ and $Q$ running concurrently
- $\nu x.P$: create a fresh private channel $x$ for $P$
- $!P$: replicate $P$ (infinite server)

**The key reduction rule (communication):**

$$
\bar{x}\langle y \rangle.P \mid x(z).Q \;\rightarrow\; P \mid Q[z := y]
$$

When a sender on $x$ and a receiver on $x$ are running in parallel, they synchronize: the receiver's $z$ is replaced by $y$.

A function call $f(v)$ in the λ-calculus encodes as: send $v$ on channel $f$, where $f$ runs a receive. So the λ-calculus embeds in the π-calculus — concurrent computation subsumes sequential computation.

---

#### Model 4: The π-Calculus

**Intuition.** Just as the lambda calculus gave us a minimal formal foundation for sequential computation (everything is a function, application is the only operation), the π-calculus gives us a minimal formal foundation for concurrent computation (everything is a channel name, send/receive is the only operation). The power comes from *mobility*: you can send a channel name over a channel, which means the communication topology can change at runtime. A function call — "send my argument to this function and wait for the reply" — is just a special case of channel communication. The reduction rule $\bar{x}\langle y \rangle.P \mid x(z).Q \rightarrow P \mid Q[z := y]$ looks almost identical to β-reduction, confirming that function application *is* a form of communication.

##### Critical Thinking Questions

13. The π-calculus has no values, no numbers, no booleans — only channel names. Church numerals (from the Lambda Calculus activity) encode numbers as functions. How would you encode a "number" in the π-calculus? (Hint: encode it as a process that sends a fixed number of messages on a given channel.)

14. The rule $\bar{x}\langle y \rangle.P \mid x(z).Q \rightarrow P \mid Q[z := y]$ looks exactly like β-reduction: $(\lambda z. Q)\; y \rightarrow Q[z := y]$. What is the "function" here, and what is the "argument"? What is the "application"?

15. In the π-calculus, $\nu x.P$ creates a fresh private channel name — no process outside $P$ knows $x$. This is the formal counterpart of what language feature in your Mini interpreter? (Hint: think about local variables and scope.)

---

### Part VI: Comparison and Design Implications

#### 6. Choosing a Concurrency Primitive

**Intuition.** All three models share one conviction: shared mutable state is the root cause of concurrency bugs, and the language should make it either impossible or self-correcting. They differ in *how*: actors prevent sharing through encapsulation (no other actor can touch your state); channels prevent sharing by forcing data to move through a single conduit at a time; STM allows sharing but detects conflicts automatically. Your choice of model shapes how you decompose a problem — actors encourage thinking in terms of independent services, channels encourage thinking in terms of data pipelines, and STM encourages thinking in terms of consistent invariants. The table below captures the key tradeoffs.

| | Actors | Channels (CSP) | STM |
|---|---|---|---|
| **Coordination** | Async message passing | Synchronous channel rendezvous | Optimistic locking with retry |
| **State sharing** | None (each actor owns state) | None (state flows through channels) | Shared, but transactional |
| **Deadlock** | Not possible (no blocking send) | Possible (channel misuse) | Not possible (no locks) |
| **Composability** | Hard (reply-to patterns) | Medium (fan-in/fan-out) | Easy (transactions compose) |
| **Side effects** | Allowed (actor's own state) | Allowed | Must be pure in transaction |
| **Used by** | Erlang, Elixir, Akka, Pony | Go, Occam, Rust (channels), Racket | Haskell STM, Clojure refs |

##### Critical Thinking Questions

16. Your final project has a Concurrency extension option: `spawn expr` and `channel send/receive`. Based on today's models, which primitive would you choose to implement first — actors, channels, or STM — and why? What is the minimum viable implementation in Python?

17. All three models agree: **do not share mutable state**. Actors achieve this by encapsulation; channels achieve this by moving data through a conduit; STM achieves this by detecting and retrying conflicts. Which model requires the programmer to change their code structure the most? The least?

18. Rust's ownership system prevents data races at compile time by ensuring only one thread can hold a mutable reference at a time. In what sense is Rust's approach a *static* enforcement of the same principle all three concurrency models pursue *dynamically*?

---

### Exercises

1. **Actor calculator.** Implement a distributed calculator using actors: a `Parser` actor parses a string expression and sends the AST to an `Evaluator` actor, which sends the result to a `Printer` actor. Show that changing the Evaluator's behavior (e.g., to evaluate in floating-point instead of integer) requires no changes to Parser or Printer.

2. **Pipeline with back-pressure.** Implement a three-stage pipeline (producer → transformer → consumer) using buffered channels. Demonstrate **back-pressure**: the producer slows down when the transformer's input channel is full. Explain why this is automatically provided by buffered channels.

3. **STM bank invariant.** Extend the STM bank to enforce the invariant `alice + bob == 1500` (the total is conserved). Show that concurrent transfers never violate this invariant, even under retries. (Hint: check the invariant at the end of each transaction.)

4. **π-calculus encoding.** The λ-term `(λx. x)(5)` can be encoded in the π-calculus. Write the encoding: create a channel `fn`, a process that receives on `fn` and sends the result on a reply channel, and a process that sends `5` on `fn`. Show the reduction step that corresponds to β-reduction.

---

#### Reflection Prompt

In your notebook: actors, channels, and STM all *eliminate* a feature (shared mutable state) rather than adding one. This is a recurring theme in language design — sometimes the best feature is one you cannot express. Lambda calculus has no mutation; Haskell's IO monad prevents mixing pure and impure code; STM prevents unsynchronized writes; Rust's ownership prevents dangling pointers. Is this style of design — **constraining the programmer for their own benefit** — fundamentally at odds with expressiveness? Give one example where the constraint paid off and one where it felt needlessly limiting.

---

#### Further Reading

- Hoare, C.A.R. *Communicating Sequential Processes* (1985; free PDF at usingcsp.com). The foundational text; Go's channels implement this model.
- Armstrong, Joe. *Programming Erlang*, 2nd ed. (Pragmatic, 2013). Chapter 9 on fault-tolerant actor systems.
- Harris, Tim et al. "Composable Memory Transactions" (PPoPP 2005). The paper introducing Haskell STM with `retry` and `orElse`.
- Milner, Robin. *Communicating and Mobile Systems: The π-Calculus* (Cambridge, 1999). The foundational text on mobile processes.
- Go's concurrency tour: https://go.dev/tour/concurrency — interactive examples of channels and goroutines.
- Hewitt, Carl. "Actor Model of Computation" (1973). The original actor paper; free online.

---

## Going Deeper: Foreign Function Interfaces: Crossing Language Boundaries

> **Imagine the United Nations General Assembly.** Each delegate speaks their own language and follows their own parliamentary customs. A simultaneous interpreter sits in a booth, listening to one language and speaking another in real time — handling not just words but idioms, formal registers, and cultural conventions that do not map one-to-one. A Foreign Function Interface is exactly that interpreter: it sits between two language runtimes, negotiating the differences in data layout, calling conventions, memory ownership, and error handling so that a function written in C can be invoked transparently from Python, Haskell, or your own mini language. Without this translator, each language would be an island; with it, every language inherits the vast ecosystem of C libraries built over 50 years.

#### Learning Goals

By the end of this activity, you will be able to:

- Explain the C Application Binary Interface (ABI) and identify why it serves as the universal interoperability layer between languages
- Use Python's `ctypes` and `cffi` to call C library functions, correctly specifying argument types, return types, and memory ownership
- Identify the challenges FFI introduces — data layout differences, memory ownership, calling conventions, and error handling — and describe how each is addressed
- Trace the lifecycle of a foreign call from the high-level language through marshaling, native execution, and unmarshaling back
- Implement a simple FFI extension mechanism in a mini interpreter that allows it to call pre-registered native functions

> **Prerequisites:** Python programming; basic C syntax; familiarity with the interpreter project
> **Goal:** Understand how languages call into native code — the C ABI, data representation, name mangling, `ctypes`/`cffi` — and implement a simple FFI extension for a mini interpreter.

**POGIL Roles:** Driver · Recorder · Reporter · Manager

> **Before You Begin**
>
> This activity assumes you are comfortable with:
>
> - Python functions, classes, and the `import` statement
> - Basic C vocabulary: functions, pointers, structs, `sizeof`, `malloc`/`free` (conceptual understanding is enough — you will not write C code)
> - The concept of a *shared library* (`.so` on Linux, `.dylib` on macOS, `.dll` on Windows) — a compiled binary that can be loaded at runtime
> - Python's `dataclass` decorator and `isinstance` checks (used in Model 5)
>
> You do **not** need to have written C code before. When C snippets appear (e.g., `int (*compar)(const void*, const void*)`), they are read-only reference points — the Python code does all the actual work. If a C type looks unfamiliar, focus on what `ctypes` does with it rather than the C syntax itself.

---

#### Preface: Why Every Language Needs to Call C

*Intuition:* Every high-level language you have ever used — Python, JavaScript, Ruby, Java — eventually bottoms out in native code. When Python opens a file, it calls a C function in the operating system. When it computes a sine, it calls a C math library. When it sends a network packet, it calls a C socket API. The FFI is the seam between the comfortable, safe, garbage-collected world of your high-level language and the raw, pointer-filled world of the operating system and hardware. Understanding that seam makes you a better programmer regardless of which side you spend most of your time on.

No programming language is an island. The operating system, graphics drivers, cryptography libraries, database engines, and compression algorithms are all written in C (or C++, which uses C's ABI for its C-compatible subset). To be useful, a language must be able to call into this world.

A **Foreign Function Interface (FFI)** is the mechanism by which one language calls functions written in another. "Foreign" means "outside the current language runtime." The most common form is calling C from a high-level language (Python, Haskell, Lua, Julia) because:

1. **C is the universal ABI:** Nearly all languages can call C; C is the *lingua franca* of system interfaces.
2. **Performance:** Native code runs without an interpreter loop.
3. **Library reuse:** Millions of battle-tested C libraries exist.

The challenge: the high-level language's runtime and the C runtime make different assumptions about data layout, memory ownership, error handling, and calling conventions.

---

#### Model 1: The C Application Binary Interface (ABI)

*Intuition:* When you call a function, the CPU needs to know: where are the arguments? (In registers? On the stack? Which ones?) Who cleans up after the call? What format does the return value come back in? The ABI is the contract that answers all of these questions. Think of it as the physical handshake protocol between two programs. C's ABI has become the universal handshake because C was the first widely-portable systems language, and every other language that wanted to talk to the operating system had to agree to shake hands on C's terms.

> **Watch out!** You must declare `argtypes` and `restype` on a `ctypes` function object before calling it. If you skip this step, `ctypes` will guess (usually defaulting to `c_int`) and you will get silent data corruption or crashes instead of a clean error. Always set both, even for functions whose return type is `void`.

An **ABI (Application Binary Interface)** defines how functions are called at the machine level: which registers hold arguments, who cleans up the stack, how structures are laid out in memory, what calling conventions are used. C's ABI is the de facto standard because it is stable, documented, and supported by every compiler on every platform.

```python
import ctypes
import sys

# ctypes gives us direct access to the C standard library
# without writing any C code ourselves

# Load the C standard library
if sys.platform == "linux":
    libc = ctypes.CDLL("libc.so.6")
elif sys.platform == "darwin":
    libc = ctypes.CDLL("libc.dylib")
else:
    libc = ctypes.msvcrt   # Windows fallback

print("=== Calling C's strlen via ctypes ===")
# strlen(const char *s) -> size_t
libc.strlen.restype  = ctypes.c_size_t
libc.strlen.argtypes = [ctypes.c_char_p]

s = b"Hello, world!"   # bytes, not str — C expects null-terminated bytes
length = libc.strlen(s)
print(f"  strlen({s!r}) = {length}")
print(f"  Python: len({s!r}) = {len(s)}")
print(f"  Same? {length == len(s)}")

print()
print("=== Calling C's abs and labs ===")
libc.abs.restype  = ctypes.c_int
libc.abs.argtypes = [ctypes.c_int]
libc.labs.restype  = ctypes.c_long
libc.labs.argtypes = [ctypes.c_long]

for v in [-42, 0, 100, -32768]:
    print(f"  abs({v:6d}) = {libc.abs(v)}")

print()
print("=== C data types and their Python equivalents ===")
type_map = [
    ("c_int",    ctypes.c_int,    42),
    ("c_long",   ctypes.c_long,   42),
    ("c_float",  ctypes.c_float,  3.14),
    ("c_double", ctypes.c_double, 3.14),
    ("c_char_p", ctypes.c_char_p, b"hello"),
    ("c_void_p", ctypes.c_void_p, None),
]
for name, ctype, example in type_map:
    obj = ctype(example) if example is not None else ctype()
    print(f"  ctypes.{name:<12} value={obj.value!r:<15} "
          f"sizeof={ctypes.sizeof(ctype)} bytes")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

**Key insight:** `ctypes` marshals Python values into C-compatible binary representations automatically for simple types. For complex types (structs, arrays, function pointers), you must describe the layout explicitly.

> **Critical Thinking Questions 1–3**

**CTQ 1.** `strlen` expects a `const char *` — a pointer to a null-terminated byte array. Why does `ctypes` require `b"Hello"` (bytes) rather than `"Hello"` (str)? What does Python's str store internally that C's `char *` does not?

[[___ your answer here ___]]

**CTQ 2.** `ctypes.c_float` has sizeof 4 bytes; `ctypes.c_double` has sizeof 8 bytes. Python's `float` is always 64-bit (a C `double`). What precision loss happens when you pass a Python `float` to a C function declared with `c_float` parameter?

[[___ your answer here ___]]

**CTQ 3.** The ABI specifies how arguments are passed: by register (x86-64 uses rdi, rsi, rdx, rcx, r8, r9 for first 6 integer args) or by stack (7th and beyond). A language that passes arguments in the wrong order or wrong registers will silently corrupt function calls. What is the responsibility of `ctypes` in this context?

[[___ your answer here ___]]

---

#### Model 2: Structs, Pointers, and Memory Layout

*Intuition:* A C struct is just a named chunk of memory. The compiler decides exactly how many bytes each field occupies and at what offset from the start of the struct — and it follows strict rules about *alignment* (each field must start at an address that is a multiple of its size). When you pass a struct across an FFI boundary, the receiving side must use *exactly* the same layout, or it will read the wrong bytes. `ctypes.Structure` exists precisely to let Python declare the layout explicitly so the two sides agree.

> **Watch out!** Struct padding is invisible in the source code but very real in memory. A struct with fields `uint8, uint32, uint16` (1+4+2 = 7 bytes naively) will actually occupy 8 or more bytes because the `uint32` field must be 4-byte aligned. Always use `ctypes.sizeof` to check the real size — never compute it by adding field sizes by hand.

C structs have a specific memory layout (with padding). When calling C functions that take or return structs, the FFI must reproduce the exact layout.

```python
import ctypes

# Define a C-compatible struct in Python
class Point(ctypes.Structure):
    _fields_ = [
        ("x", ctypes.c_double),
        ("y", ctypes.c_double),
    ]

class Rect(ctypes.Structure):
    _fields_ = [
        ("top_left",     Point),
        ("bottom_right", Point),
    ]

print("=== C struct layout ===")
p = Point(3.0, 4.0)
print(f"  Point({p.x}, {p.y})")
print(f"  sizeof(Point) = {ctypes.sizeof(Point)} bytes")
print(f"  offset(x) = {Point.x.offset}, offset(y) = {Point.y.offset}")

r = Rect(Point(0.0, 0.0), Point(10.0, 5.0))
print(f"\n  Rect: ({r.top_left.x},{r.top_left.y}) → ({r.bottom_right.x},{r.bottom_right.y})")
print(f"  sizeof(Rect) = {ctypes.sizeof(Rect)} bytes")

print()
print("=== Struct with alignment padding ===")
class Padded(ctypes.Structure):
    _fields_ = [
        ("flag",  ctypes.c_uint8),    # 1 byte
        ("value", ctypes.c_uint32),   # 4 bytes — but likely padded to 4-byte boundary
        ("extra", ctypes.c_uint16),   # 2 bytes
    ]

print(f"  Padded: flag@{Padded.flag.offset}, value@{Padded.value.offset}, "
      f"extra@{Padded.extra.offset}")
print(f"  sizeof(Padded) = {ctypes.sizeof(Padded)} bytes  "
      f"(vs naive 1+4+2=7 bytes)")

print()
print("=== Passing structs by pointer ===")
class Vec2(ctypes.Structure):
    _fields_ = [("x", ctypes.c_float), ("y", ctypes.c_float)]

def magnitude_python(v: Vec2) -> float:
    import math
    return math.sqrt(v.x**2 + v.y**2)

# Simulate how an FFI would call a C function that takes a Vec2*
v = Vec2(3.0, 4.0)
ptr = ctypes.byref(v)    # byref creates a pointer to v without copying
print(f"  Vec2(3, 4) at address {id(v):#x}")
print(f"  magnitude = {magnitude_python(v):.4f}")

print()
print("=== C arrays ===")
IntArray5 = ctypes.c_int * 5
arr = IntArray5(10, 20, 30, 40, 50)
print(f"  C array of 5 ints: {list(arr)}")
print(f"  sizeof = {ctypes.sizeof(arr)} bytes ({ctypes.sizeof(ctypes.c_int)} × 5)")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

> **Critical Thinking Questions 4–6**

**CTQ 4.** The `Padded` struct has `sizeof` greater than 1+4+2=7. The compiler adds **padding** between fields to align them to their natural alignment. Why does alignment matter? What hardware problem does misaligned access cause on x86? On ARM?

[[___ your answer here ___]]

**CTQ 5.** `ctypes.byref(v)` passes a pointer to `v` without copying. If the C function modifies the struct through the pointer, the Python object `v` is also modified. How does this differ from Python's normal parameter passing semantics? When is this desirable? When is it dangerous?

[[___ your answer here ___]]

**CTQ 6.** Structs can be passed **by value** (C copies the struct) or **by pointer** (C receives an address). For large structs, passing by pointer is more efficient. But it also means the callee can modify the original. How do languages like Rust use the type system to make this safe?

[[___ your answer here ___]]

---

#### Model 3: Callbacks — C Calling Back into Python

*Intuition:* The FFI translator analogy runs in both directions. When you hire an interpreter for a UN session, sometimes the foreign delegate asks the interpreter a question — the interpreter must be able to respond, not just relay. Callbacks are the same: a C library like `qsort` does not just receive data; it calls back into your code to ask "which of these two items is larger?" The Python function you provide becomes, for the duration of the C call, a first-class participant in C's execution — it must speak C's calling convention fluently, which is what `ctypes.CFUNCTYPE` arranges.

> **Watch out!** C holds a raw function pointer to your Python callback — just a memory address. Python's garbage collector does not know about this. If the Python object wrapping the callback is collected (because no Python variable refers to it anymore), the memory address becomes invalid, and the next time C calls it your program will crash or produce undefined behavior. Always store callback objects in a variable that stays alive for as long as C might invoke them.

The FFI is bidirectional: not only can Python call C, but C can call Python functions (callbacks). This is used for event handlers, sort comparators, and error handlers.

```python
import ctypes

# Define a C-compatible function type for a callback
# int (*comparator)(const void*, const void*)  -- used by qsort
COMPARATOR = ctypes.CFUNCTYPE(
    ctypes.c_int,         # return type
    ctypes.c_void_p,      # arg 1: const void*
    ctypes.c_void_p,      # arg 2: const void*
)

# Load libc for qsort
import sys
libc = ctypes.CDLL("libc.so.6" if sys.platform == "linux" else "libc.dylib")
libc.qsort.argtypes = [
    ctypes.c_void_p,   # base: pointer to array
    ctypes.c_size_t,   # nmemb: number of elements
    ctypes.c_size_t,   # size: size of each element
    COMPARATOR,        # compar: the callback
]
libc.qsort.restype = None

print("=== Python callback called by C's qsort ===")

call_count = [0]

def python_compare(a_ptr, b_ptr):
    """C calls this function with pointers to two ints."""
    call_count[0] += 1
    a = ctypes.cast(a_ptr, ctypes.POINTER(ctypes.c_int)).contents.value
    b = ctypes.cast(b_ptr, ctypes.POINTER(ctypes.c_int)).contents.value
    return (a > b) - (a < b)   # -1, 0, or 1

c_compare = COMPARATOR(python_compare)   # wrap Python fn in C function type

IntArray = ctypes.c_int * 8
data = IntArray(64, 12, 99, 3, 47, 28, 7, 55)
print(f"  Before sort: {list(data)}")

libc.qsort(data, len(data), ctypes.sizeof(ctypes.c_int), c_compare)
print(f"  After sort:  {list(data)}")
print(f"  Comparator called {call_count[0]} times")

print()
print("=== Callback memory management pitfall ===")
# CRITICAL: the C library holds a raw function pointer.
# If the Python callback object is garbage collected, the pointer becomes dangling.
# You MUST keep a reference to c_compare alive as long as C might call it.
print("  Danger: if c_compare is not kept alive, the function pointer is dangling!")
print("  Safe: store callbacks in a list that outlives the C call.")
callbacks = [c_compare]   # this reference keeps the callback alive

print()
print("=== Type-safe callback wrapper ===")
# A safer pattern: wrap in a class that manages the lifetime
class SafeCallback:
    def __init__(self, fn, c_type):
        self._fn = fn
        self._c_fn = c_type(fn)
    @property
    def c_ptr(self):
        return self._c_fn
    def __del__(self):
        print(f"  SafeCallback destroyed: {self._fn.__name__}")

def my_handler(x: int, y: int) -> int:
    return x - y

HANDLER = ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_int, ctypes.c_int)
cb = SafeCallback(my_handler, HANDLER)
print(f"  Direct test of callback: my_handler(10, 3) = {cb.c_ptr(10, 3)}")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

> **Critical Thinking Questions 7–9**

**CTQ 7.** `COMPARATOR = ctypes.CFUNCTYPE(c_int, c_void_p, c_void_p)` describes the function signature. What would happen if you passed a Python function with the wrong signature (e.g., one that takes only one argument instead of two)?

[[___ your answer here ___]]

**CTQ 8.** The comment warns: "if c_compare is garbage collected, the pointer becomes dangling." Why can't Python's garbage collector know that C is holding a reference? What would a language with linear types (like Rust) do differently?

[[___ your answer here ___]]

**CTQ 9.** `qsort` calls the comparator multiple times on different pairs. The comparator modifies `call_count` — a Python list (mutable container). This works because Python closures capture by reference. If the comparator modified a Python integer directly (`count = count + 1`), it would fail due to Python's scoping rules. Why? What does this reveal about closures and rebinding?

[[___ your answer here ___]]

---

#### Model 4: Name Mangling and Symbol Resolution

*Intuition:* When a program links against a library, it looks up function names in the library's *symbol table* — a dictionary inside the compiled binary. C's symbol for `strlen` is literally the string `"strlen"`. C++ cannot do this for overloaded functions: `foo(int)` and `foo(double)` both spell `foo`, but they are different functions with different machine code. C++ solves this by *mangling* the name — encoding the parameter types into the symbol string so that `foo(int)` becomes something like `_ZN3foo1iE`. This is the "name" the linker actually looks up. FFI tools must understand mangling to call C++ functions correctly.

C uses simple symbol names (`strlen`, `printf`). C++ mangles names to encode type signatures. Understanding this is essential for building FFI tools.

```python
import ctypes
import ctypes.util
import sys

print("=== Finding shared library paths ===")
math_lib_name = ctypes.util.find_library("m")
c_lib_name    = ctypes.util.find_library("c")
print(f"  libm path: {math_lib_name}")
print(f"  libc path: {c_lib_name}")

print()
print("=== Dynamic symbol lookup ===")
if sys.platform != "win32":
    # RTLD_DEFAULT looks up symbols in all loaded libraries
    libc = ctypes.CDLL(None)    # None = look in all currently loaded libraries
    
    # Manually look up a symbol by name
    try:
        printf_ptr = ctypes.cast(
            ctypes.c_void_p.in_dll(libc, "printf") if hasattr(ctypes.c_void_p, 'in_dll')
            else None,
            ctypes.c_void_p
        )
        print(f"  printf found in libc")
    except (OSError, AttributeError):
        print("  (symbol inspection not available on this platform)")

print()
print("=== Python's own C API via ctypes ===")
# CPython exports its C API as a shared library (libpython)
# We can call internal Python C API functions — carefully!
py = ctypes.pythonapi

# PyList_New(Py_ssize_t len) -> PyObject*
py.PyList_New.restype = ctypes.py_object
py.PyList_New.argtypes = [ctypes.c_ssize_t]
new_list = py.PyList_New(0)
print(f"  PyList_New(0) via C API: {new_list!r}  type={type(new_list).__name__}")

# Py_GetVersion() -> const char*
py.Py_GetVersion.restype = ctypes.c_char_p
version_str = py.Py_GetVersion()
print(f"  Py_GetVersion(): {version_str.decode()[:50]}...")

print()
print("=== What C++ name mangling looks like ===")
# C++ compilers mangle function names to encode their full type signatures.
# 'void MyClass::foo(int, double)' might become '_ZN7MyClass3fooEid'
# Tools like 'c++filt' unmangle them.
# In Python, you can see this pattern by simulating it:
def mangle_simple(class_name: str, method_name: str, param_types: list) -> str:
    """Simplified Itanium ABI mangling (GNU/Clang style)."""
    type_codes = {"int": "i", "double": "d", "float": "f", "bool": "b",
                  "char": "c", "void": "v", "long": "l"}
    params = "".join(type_codes.get(t, "?") for t in param_types)
    n = len(class_name)
    m = len(method_name)
    return f"_ZN{n}{class_name}{m}{method_name}E{params}"

examples = [
    ("MyClass", "foo",    ["int", "double"]),
    ("Vector",  "push",   ["int"]),
    ("Matrix",  "mult",   ["double", "double"]),
]
print("  C++ name mangling (simplified):")
for cls, fn, params in examples:
    mangled = mangle_simple(cls, fn, params)
    print(f"    {cls}::{fn}({', '.join(params)}) -> {mangled}")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

> **Critical Thinking Questions 10–12**

**CTQ 10.** C's simple symbol names (`strlen`) mean that a shared library can only export one `strlen`. C++ name mangling allows overloaded functions (`foo(int)` and `foo(double)`) to coexist in the same library. What does this tell you about C's type system at the ABI level?

[[___ your answer here ___]]

**CTQ 11.** `ctypes.CDLL(None)` loads symbols from all currently loaded libraries, including the Python interpreter itself. Why is calling Python's internal C API this way dangerous? What invariant must you preserve?

[[___ your answer here ___]]

**CTQ 12.** When writing an FFI for your mini language, you could either (a) call into C at the C ABI level (like ctypes) or (b) call Python functions directly. Option (b) is simpler. What would you lose by choosing (b) rather than (a)? Under what circumstances would (a) be necessary?

[[___ your answer here ___]]

---

#### Model 5: Implementing a Simple FFI in a Mini Interpreter

*Intuition:* Now that you understand the mechanics of crossing the language boundary, you can add that crossing point to your own interpreter. The key design decision is: what does an FFI call look like *in your language's syntax*, and how does the interpreter translate that into an actual call? This model shows the minimum viable implementation: an `FfiCall` AST node carries the library name, function name, type annotations, and arguments. The interpreter's `eval_node` function dispatches it to a registry that handles the marshaling. Even a simple version like this is enough to give your mini language access to the entire C standard library.

A language interpreter can support FFI by letting programs call Python built-ins or C functions by name. Here is a minimal implementation.

```python
from dataclasses import dataclass, field
from typing import Any, Dict, Callable, List, Optional
import ctypes
import sys

@dataclass
class FfiCall:
    """AST node: call a foreign function by name with given arguments."""
    lib_name: str
    func_name: str
    arg_types: List[str]   # e.g., ["int", "int"]
    ret_type: str           # e.g., "int"
    args: List[Any]        # evaluated argument AST nodes

@dataclass
class Num:
    value: float

@dataclass
class Str_:
    value: str

class FFIRegistry:
    """Manages loaded libraries and their function signatures."""
    CTYPES_MAP = {
        "int":    ctypes.c_int,
        "long":   ctypes.c_long,
        "double": ctypes.c_double,
        "float":  ctypes.c_float,
        "str":    ctypes.c_char_p,
        "void":   None,
    }

    def __init__(self):
        self._libs: Dict[str, Any] = {}
        self._python_fns: Dict[str, Callable] = {}
        # Pre-load safe Python built-ins as "python" library
        self._python_fns.update({
            "abs":   abs,
            "len":   len,
            "str":   str,
            "int":   int,
            "float": float,
            "max":   max,
            "min":   min,
        })

    def load_lib(self, name: str, path: str):
        self._libs[name] = ctypes.CDLL(path)

    def call(self, lib_name: str, func_name: str,
             arg_types: List[str], ret_type: str, args: List[Any]) -> Any:
        if lib_name == "python":
            fn = self._python_fns.get(func_name)
            if fn is None:
                raise NameError(f"python.{func_name} not in FFI registry")
            return fn(*args)
        
        lib = self._libs.get(lib_name)
        if lib is None:
            raise ImportError(f"Library {lib_name!r} not loaded")
        
        fn = getattr(lib, func_name)
        fn.argtypes = [self.CTYPES_MAP[t] for t in arg_types]
        fn.restype  = self.CTYPES_MAP.get(ret_type, ctypes.c_int)
        
        # Convert Python values to C values
        c_args = []
        for val, t in zip(args, arg_types):
            if t == "str":
                c_args.append(val.encode() if isinstance(val, str) else val)
            else:
                c_args.append(val)
        
        result = fn(*c_args)
        if isinstance(result, bytes):
            return result.decode()
        return result

def eval_node(node, env, ffi: FFIRegistry):
    if isinstance(node, Num):
        return node.value
    if isinstance(node, Str_):
        return node.value
    if isinstance(node, FfiCall):
        evaluated_args = [eval_node(a, env, ffi) for a in node.args]
        return ffi.call(node.lib_name, node.func_name,
                        node.arg_types, node.ret_type, evaluated_args)
    raise ValueError(f"unknown node: {node!r}")

ffi = FFIRegistry()

# Load libc for math operations
if sys.platform == "linux":
    ffi.load_lib("libc", "libc.so.6")
    ffi.load_lib("libm", "libm.so.6")
elif sys.platform == "darwin":
    ffi.load_lib("libc", "libc.dylib")
    ffi.load_lib("libm", "libm.dylib")

print("=== Mini interpreter FFI calls ===")

env = {}

# call python.abs(-42) -> int
call_abs = FfiCall("python", "abs", ["int"], "int", [Num(-42)])
print(f"  python.abs(-42) = {eval_node(call_abs, env, ffi)}")

# call python.max(3, 7) -> int
call_max = FfiCall("python", "max", ["int", "int"], "int", [Num(3), Num(7)])
print(f"  python.max(3, 7) = {eval_node(call_max, env, ffi)}")

# call libc.strlen("hello") -> int (only on Linux/Mac)
if sys.platform in ("linux", "darwin"):
    call_strlen = FfiCall("libc", "strlen", ["str"], "int", [Str_("hello world")])
    print(f"  libc.strlen('hello world') = {eval_node(call_strlen, env, ffi)}")
    
    call_sqrt = FfiCall("libm" if sys.platform == "linux" else "libc",
                        "sqrt", ["double"], "double", [Num(9.0)])
    try:
        print(f"  sqrt(9.0) = {eval_node(call_sqrt, env, ffi)}")
    except Exception as e:
        print(f"  (sqrt not available: {e})")

print()
print("=== FFI in language syntax (hypothetical) ===")
print("  Your language could expose FFI as a built-in statement:")
print("  ffi load 'libc.so.6' as libc;")
print("  let n = ffi call libc.strlen(str: 'hello');")
print("  print n;   # 5")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

> **Critical Thinking Questions 13–15**

**CTQ 13.** The `FFIRegistry` uses a "Python" pseudo-library for safe built-ins and C libraries for native code. What is the advantage of keeping these in the same `FfiCall` AST node vs. having separate `NativeFn` and `PythonFn` nodes?

[[___ your answer here ___]]

**CTQ 14.** FFI calls bypass your interpreter's type checker. A language-level type error (e.g., passing a string where `c_int` is expected) will become a ctypes exception rather than a friendly language error. How would you add a "type gate" to the FFI call path?

[[___ your answer here ___]]

**CTQ 15.** A language with FFI can call any C function, including `malloc`, `free`, `exec`, and `system`. This breaks memory safety and security. How do languages like Haskell (via `Foreign.Unsafe`) or Rust (via `unsafe`) signal that FFI code requires special trust?

[[___ your answer here ___]]

---

#### Multiple Choice Review

**Question 1.** `ctypes.c_char_p` in Python represents:

- [( )] A Python `str` object
- [(X)] A C-style null-terminated `char*` pointer, accepting `bytes`
- [( )] A single character (1 byte)
- [( )] A wide character (2 bytes) for Unicode

**Question 2.** When a C function takes a struct by value, the caller:

- [(X)] Copies the entire struct onto the stack (or into registers per ABI)
- [( )] Passes a pointer to the struct, which C dereferences automatically
- [( )] Converts the struct to a byte string first
- [( )] Returns an error unless the struct is marked `extern "C"`

**Question 3.** C++ name mangling is needed because:

- [( )] C++ is compiled to a different object format than C
- [(X)] C++ allows function overloading, so multiple functions can have the same name but different parameter types
- [( )] The linker requires all symbols to be prefixed with the namespace
- [( )] C++ uses a garbage collector that must track all function names

**Question 4.** Keeping a reference to a `ctypes.CFUNCTYPE` callback alive while C might call it is necessary because:

- [( )] ctypes functions are reference-counted independently
- [(X)] Python's garbage collector will free the callback if no Python reference remains, leaving C with a dangling pointer
- [( )] C copies the function body into its own memory on first call
- [( )] ctypes registers all callbacks globally and they are never freed

---

#### Exercises

**Exercise 1.** Use `ctypes` to call C's `qsort` with a Python comparator that sorts strings by length (shortest first), falling back to lexicographic order for equal-length strings:

```python
import ctypes
import sys

if sys.platform not in ("linux", "darwin"):
    print("Skipping: not Linux/macOS")
else:
    libc = ctypes.CDLL("libc.so.6" if sys.platform == "linux" else "libc.dylib")
    
    # qsort signature: void qsort(void *base, size_t nmemb, size_t size,
    #                             int (*compar)(const void *, const void *))
    COMP = ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_void_p, ctypes.c_void_p)
    
    words = ["banana", "kiwi", "apple", "fig", "cherry", "date"]
    
    # To qsort strings, we'll sort indices and use Python for the comparison
    indices = list(range(len(words)))
    IdxArray = ctypes.c_int * len(indices)
    c_indices = IdxArray(*indices)
    
    def compare_by_length(a_ptr, b_ptr):
        a_idx = ctypes.cast(a_ptr, ctypes.POINTER(ctypes.c_int)).contents.value
        b_idx = ctypes.cast(b_ptr, ctypes.POINTER(ctypes.c_int)).contents.value
        wa, wb = words[a_idx], words[b_idx]
        if len(wa) != len(wb):
            return len(wa) - len(wb)
        return (wa > wb) - (wa < wb)
    
    comp_fn = COMP(compare_by_length)
    libc.qsort.argtypes = [ctypes.c_void_p, ctypes.c_size_t,
                           ctypes.c_size_t, COMP]
    libc.qsort.restype = None
    libc.qsort(c_indices, len(c_indices), ctypes.sizeof(ctypes.c_int), comp_fn)
    
    sorted_words = [words[c_indices[i]] for i in range(len(c_indices))]
    print(f"Sorted by length: {sorted_words}")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

**Exercise 2.** Extend the `FFIRegistry` from Model 5 to support type coercion and better error messages. Add a `validate_and_coerce` method that checks types and converts Python values:

```python
import ctypes
import sys

class SafeFFIRegistry:
    CTYPES_MAP = {
        "int":    ctypes.c_int,
        "double": ctypes.c_double,
        "str":    ctypes.c_char_p,
    }
    PYTHON_TYPES = {
        "int":    (int, float),
        "double": (int, float),
        "str":    (str, bytes),
    }
    
    def __init__(self):
        self._python_fns = {
            "abs": abs, "max": max, "min": min,
            "len": len, "str": str, "int": int,
        }

    def validate_and_coerce(self, val, expected_type: str):
        if expected_type not in self.PYTHON_TYPES:
            raise TypeError(f"Unknown FFI type: {expected_type!r}")
        allowed = self.PYTHON_TYPES[expected_type]
        if not isinstance(val, allowed):
            raise TypeError(
                f"FFI type mismatch: expected {expected_type} "
                f"(Python {allowed}), got {type(val).__name__}"
            )
        if expected_type == "str" and isinstance(val, str):
            return val.encode()
        if expected_type == "int" and isinstance(val, float):
            if val != int(val):
                raise ValueError(f"Cannot coerce {val} to int without precision loss")
            return int(val)
        return val

    def call_python(self, func_name: str, arg_types: list, args: list):
        fn = self._python_fns.get(func_name)
        if fn is None:
            raise NameError(f"python.{func_name} not registered")
        coerced = [self.validate_and_coerce(v, t) for v, t in zip(args, arg_types)]
        return fn(*coerced)

ffi = SafeFFIRegistry()

print("=== Safe FFI with type validation ===")

# Valid calls
for fn, types, args in [
    ("abs",   ["int"],        [-42]),
    ("max",   ["int", "int"], [3, 7]),
    ("len",   ["str"],        ["hello"]),
]:
    result = ffi.call_python(fn, types, args)
    print(f"  python.{fn}({args}) = {result}")

# Invalid calls (should produce clear errors)
bad_calls = [
    ("abs",   ["int"],  ["not_a_number"]),
    ("max",   ["int", "int"], [3.5, 7]),
]
for fn, types, args in bad_calls:
    try:
        ffi.call_python(fn, types, args)
    except (TypeError, ValueError) as e:
        print(f"  python.{fn}({args}) -> {type(e).__name__}: {e}")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

**Exercise 3.** Implement a minimal "safe FFI" for your mini language that allows calling Python's `math` module functions. Add lexer/parser support for the syntax `ffi("math", "sqrt", 9.0)`:

```python
import math
import re
from dataclasses import dataclass
from typing import Any, List

@dataclass
class FfiExpr:
    module: str
    func_name: str
    args: List[Any]

SAFE_MODULES = {
    "math": math,
    "os.path": __import__("os.path"),
}

def eval_ffi(node: FfiExpr):
    mod = SAFE_MODULES.get(node.module)
    if mod is None:
        raise ImportError(f"Module {node.module!r} not in FFI allowlist")
    fn = getattr(mod, node.func_name, None)
    if fn is None:
        raise AttributeError(f"{node.module}.{node.func_name} not found")
    return fn(*node.args)

# Simulate parsing 'ffi("math", "sqrt", 9.0)'
def parse_ffi_call(src: str) -> FfiExpr:
    m = re.match(r'ffi\("([^"]+)",\s*"([^"]+)"((?:,\s*[\d.]+)*)\)', src)
    if not m:
        raise SyntaxError(f"Invalid ffi call: {src!r}")
    module, fn_name = m.group(1), m.group(2)
    args_str = m.group(3)
    args = [float(a.strip()) for a in args_str.split(",") if a.strip()]
    return FfiExpr(module, fn_name, args)

test_calls = [
    'ffi("math", "sqrt", 25.0)',
    'ffi("math", "floor", 3.7)',
    'ffi("math", "pow", 2.0, 10.0)',
]

print("=== Safe FFI for math module ===")
for src in test_calls:
    node = parse_ffi_call(src)
    result = eval_ffi(node)
    print(f"  {src} = {result}")

# Security: try to call an unsafe module
try:
    bad = FfiExpr("os", "system", ["rm -rf /"])
    eval_ffi(bad)
except ImportError as e:
    print(f"\n  Security block: {e}")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

---

#### Reflection

1. The FFI is fundamentally an "escape hatch" from your language's safety guarantees. A type-safe language can call unsafe C code via FFI. How do language designers manage this tension? Name the strategies used by Python, Haskell, and Rust respectively.

2. Your mini interpreter runs Python as its host language. This means your "FFI" to Python is essentially free — you can call any Python function. But if your language was a compiled language generating machine code, FFI would require real ABI compatibility. What would change in your implementation?

3. The `SAFE_MODULES` allowlist in Exercise 3 prevents calling `os.system` via FFI. Is a whitelist the right security model for an FFI? What are the limitations of this approach?

---

#### Further Reading

- **Python docs:** `ctypes` — A foreign function library for Python
- **Python docs:** `cffi` — C Foreign Function Interface for Python (higher-level alternative to ctypes)
- **Article:** *How Python calls C* — deep dive into CPython's API
- **Rust book:** Chapter, "Unsafe Rust" — `extern "C"` and `unsafe fn`
- **Haskell wiki:** `Foreign Function Interface` — `Foreign.Ptr`, `Foreign.Marshal`
- **Paper:** *A Semantic Framework for C (and the Rest)* — Norrish (1998), the formal semantics behind C's ABI behavior
- **Talk:** Brandon Williams, "ctypes Without the Boilerplate" — automating struct generation from C headers

---

*End of Activity — Foreign Function Interfaces: C ABI, ctypes, callbacks, name mangling, interpreter FFI implementation*

---

## Going Deeper: Denotational Semantics: Programs as Mathematical Functions

You already know that a program *runs* — but what does it *mean*? Denotational semantics answers that question by mapping every program to a precise mathematical object: a function, a set, or a value in a carefully chosen domain. Think of it like translating a recipe into a mathematical function where the input ingredients map deterministically to the output dish — the function captures the meaning of the recipe independently of any particular cook's technique. This mathematical view lets us prove two programs are equivalent, reason about infinite loops, and understand language features without ever running a single instruction.

#### Learning Goals

By the end of this activity, you will be able to:

- Define denotational semantics and explain how it differs from operational and axiomatic semantics
- Apply the compositionality principle to construct semantic functions for compound expressions in a simple language
- Identify the mathematical domain (integers, functions, or lifted types) appropriate for modeling a given language construct
- Explain how denotational semantics handles non-termination using the bottom element and domain theory
- Compare two programs for semantic equivalence by evaluating their denotations on the same environment

> **"The meaning of a program is a function from inputs to outputs."**
>
> Denotational semantics gives us a way to assign a precise mathematical meaning — a *denotation* — to every program, independent of how any computer would execute it. Today you'll see how to define the meaning of a language mathematically, and why this matters for reasoning about programs.

> **Before You Begin — Prerequisites**
>
> Make sure you are comfortable with the following before diving in:
>
> - **Functions as mathematical mappings**: a function `f : A → B` assigns to each element of `A` exactly one element of `B`. No side effects, no "running" — just a mapping.
> - **Basic set notation**: `∈` (element of), `→` (function type), `×` (product), and the idea of a domain as a set of values.
> - **Operational semantics (big-step rules)**: you should have seen rules of the form `⟨e, σ⟩ ⇓ v` that describe how an expression evaluates to a value in an environment. Denotational semantics covers the same ground but with functions instead of rules.
>
> If any of these feel shaky, skim your notes from the Operational Semantics activity before continuing.

#### Directions and Roles

Work in groups of 3–4. Rotate roles every 20 minutes.

- **Facilitator**: Keeps discussion on track; ensures everyone contributes.
- **Recorder**: Writes down answers and code that the group agrees on.
- **Reporter**: Presents findings to the class; explains the group's reasoning.
- **Reflector**: Monitors group process; writes the reflection at the end.

---

#### Notation Quick Reference

The mathematical notation used in denotational semantics is compact but unfamiliar at first. Use this table as a decoder ring throughout the activity:

| Notation | Meaning |
|----------|---------|
| `⟦e⟧ρ` | "The meaning of expression `e` in environment `ρ`" |
| `ρ[x ↦ v]` | "Environment `ρ` extended with `x` mapping to value `v`" |
| `⊥` | "Bottom" — the value representing non-termination or no information |
| `D → D` | The set of all functions from domain `D` to domain `D` |
| `⊑` | "Approximates" — the information ordering on a domain |
| `⊔` | Least upper bound (join) of a chain of approximations |
| `fix(F)` | The least fixed point of function `F` |

---

#### Model 1 — Three Ways to Define a Language

**Intuition.** Before diving into notation, orient yourself: there are three popular frameworks for giving a programming language a formal meaning. Operational semantics says "meaning is how a machine runs the program." Axiomatic semantics says "meaning is what the program guarantees (pre/post-conditions)." Denotational semantics takes a more ambitious stance — it says "meaning is a timeless mathematical object that the program *is*, not just what it *does*." Each view illuminates different properties, and knowing all three lets you pick the right tool for any proof.

> **Watch out!** Denotational semantics is about assigning *mathematical meaning*, not describing *execution steps*. When you write `⟦e₁ + e₂⟧ σ = ⟦e₁⟧ σ + ⟦e₂⟧ σ`, you are defining a mathematical equality between functions — you are not saying which operand evaluates first, or how many machine steps it takes. This is the key philosophical shift from operational semantics.

There are three main styles of formal semantics:

| Style | Defines meaning as... | Good for... |
|-------|----------------------|-------------|
| **Operational** | Reduction rules (how a machine steps) | Proving execution properties, implementing interpreters |
| **Denotational** | Mathematical functions (what programs *are*) | Compositional reasoning, equivalence proofs |
| **Axiomatic** | Pre/post-condition logic (what programs *guarantee*) | Program verification, Hoare logic |

In **denotational semantics**, we write a *semantic function* `⟦·⟧` that maps syntactic programs to mathematical objects:

```
⟦e⟧ : Env → Value
⟦s⟧ : Store → Store
```

The key property is **compositionality**: the meaning of a compound expression is defined entirely in terms of the meanings of its parts. `⟦e₁ + e₂⟧ = ⟦e₁⟧ + ⟦e₂⟧` — the meaning of an addition is the sum of the meanings.

**Critical Thinking Questions (CTQs)**

> **CTQ 1.1** Compositionality says "the meaning of a whole is a function of the meanings of its parts." Give an example where this is NOT true in natural language (e.g., idioms). Why doesn't this problem occur in programming languages?

> **CTQ 1.2** The operational semantics of a `while` loop requires a transition rule that "runs" the loop. How might you define the *denotational* meaning of a `while` loop without running anything?

> **CTQ 1.3** What does it mean to say two programs are "semantically equivalent" in the denotational sense?

---

#### Model 2 — A Tiny Language and its Denotations

**Intuition.** The best way to internalize denotational semantics is to work through a concrete, small language. The **Arith** language below has no mutation and no loops — it is a pure expression language. Each expression, given an environment mapping variables to integers, evaluates to exactly one integer. The semantic function `⟦·⟧` formalizes this: it is just a carefully structured recursive definition. Notice that the Python implementation that follows is not merely an interpreter that *approximates* the semantics — structurally, it *is* the semantics, expressed in executable form.

Consider a tiny arithmetic language **Arith** with the grammar:

```
e ::= n                  -- integer literal
    | x                  -- variable  
    | e₁ + e₂            -- addition
    | e₁ * e₂            -- multiplication
    | let x = e₁ in e₂  -- local binding
    | if e₁ then e₂ else e₃  -- conditional
```

**Domain**: the set of integers `ℤ`, plus a special `⊥` (bottom) for errors/non-termination.

**Environment**: `Env = Var → ℤ`  (a function from variables to integers)

**Semantic function** `⟦·⟧ : Arith → Env → ℤ`:

```
⟦n⟧ σ         = n                         (literal)
⟦x⟧ σ         = σ(x)                      (variable lookup)
⟦e₁ + e₂⟧ σ  = ⟦e₁⟧ σ + ⟦e₂⟧ σ          (addition)
⟦e₁ * e₂⟧ σ  = ⟦e₁⟧ σ × ⟦e₂⟧ σ          (multiplication)
⟦let x = e₁ in e₂⟧ σ = ⟦e₂⟧ (σ[x ↦ ⟦e₁⟧ σ])   (let: extend env)
⟦if e₁ then e₂ else e₃⟧ σ =
    ⟦e₂⟧ σ,  if ⟦e₁⟧ σ ≠ 0
    ⟦e₃⟧ σ,  if ⟦e₁⟧ σ = 0
```

Here `σ[x ↦ v]` means "the environment σ updated to map x to v."

Let's implement this in Python — the implementation IS the semantics:

```python  liascript
def arith_eval(expr, env):
    """Denotational evaluator for Arith.
    expr is a tuple-based AST; env is a dict."""
    match expr:
        case ('num', n):
            return n
        case ('var', x):
            if x not in env:
                raise ValueError(f"Unbound variable: {x}")
            return env[x]
        case ('add', e1, e2):
            return arith_eval(e1, env) + arith_eval(e2, env)
        case ('mul', e1, e2):
            return arith_eval(e1, env) * arith_eval(e2, env)
        case ('let', x, e1, e2):
            v1 = arith_eval(e1, env)
            new_env = {**env, x: v1}   # σ[x ↦ v1]
            return arith_eval(e2, new_env)
        case ('if', cond, then, else_):
            if arith_eval(cond, env) != 0:
                return arith_eval(then, env)
            else:
                return arith_eval(else_, env)

# Test: let x = 3 in let y = x + 1 in x * y
prog = ('let', 'x', ('num', 3),
          ('let', 'y', ('add', ('var', 'x'), ('num', 1)),
            ('mul', ('var', 'x'), ('var', 'y'))))
result = arith_eval(prog, {})
print(f"let x=3 in let y=x+1 in x*y = {result}")  # 3 * 4 = 12

# Test: if 1 then 42 else 0
result2 = arith_eval(('if', ('num', 1), ('num', 42), ('num', 0)), {})
print(f"if 1 then 42 else 0 = {result2}")  # 42
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

**CTQs**

> **CTQ 2.1** The denotational rule for `let x = e₁ in e₂` creates a *new* environment rather than mutating the existing one. What does this say about the semantics of variable binding in this language? Is this lexical or dynamic scope?

> **CTQ 2.2** Compare `arith_eval` with a typical interpreter. What's the key structural difference? (Hint: look at how recursion is used.)

> **CTQ 2.3** The semantic function `⟦·⟧` takes an *expression* and an *environment* and returns a *value*. What *type* would you assign to `⟦·⟧` in a typed language like Haskell?

---

#### Model 3 — Adding State: Stores and Commands

**Intuition.** Pure expressions always return a value — they have no side effects. But real programs *change* memory: `x := x + 1` transforms the store. Denotational semantics handles this elegantly by treating each command as a mathematical function from stores to stores. Sequencing `c₁ ; c₂` is then just function composition: first transform the store with `c₁`, then pipe the resulting store into `c₂`. The tough case is loops — because a loop may run zero, one, or arbitrarily many times, we cannot write a finite semantic equation for it. This is where fixed points enter the picture.

> **Watch out!** Fixed points are necessary to give `while` loops a denotational meaning. You cannot write `⟦while e do c⟧` as a simple equation involving only `⟦e⟧` and `⟦c⟧` without some notion of iteration to infinity. The fixed-point operator `fix(F)` captures exactly "the behavior you get if you unroll the loop as many times as needed." If the loop never terminates, the fixed point is `⊥` — no output at all.

The Arith language above is *pure* — no mutation. Now we add imperative features. The key idea: **commands** transform the *store* (memory).

```
c ::= x := e            -- assignment
    | c₁ ; c₂           -- sequence  
    | if e then c₁ else c₂   -- conditional command
    | while e do c       -- loop
    | skip               -- no-op
```

**Domain for commands**: `Cmd → Store → Store` (commands are *state transformers*)

```
⟦skip⟧ s              = s
⟦x := e⟧ s            = s[x ↦ ⟦e⟧ s]
⟦c₁ ; c₂⟧ s           = ⟦c₂⟧ (⟦c₁⟧ s)
⟦if e then c₁ else c₂⟧ s =
    ⟦c₁⟧ s,  if ⟦e⟧ s ≠ 0
    ⟦c₂⟧ s,  if ⟦e⟧ s = 0
```

The tricky case is `while`:

```
⟦while e do c⟧ =  fix(F)
  where F(f)(s) = if ⟦e⟧ s ≠ 0 then f(⟦c⟧ s) else s
```

This uses a **fixed point** — `while` is the *least fixed point* of the function `F`. The loop runs until the condition is false, and `fix` captures exactly that iteration mathematically.

```python  liascript
def cmd_eval(cmd, store):
    """Denotational evaluator for imperative commands.
    store is a dict (mutable, but we always return a new one)."""
    match cmd:
        case ('skip',):
            return dict(store)
        case ('assign', x, e):
            v = arith_eval(e, store)
            return {**store, x: v}
        case ('seq', c1, c2):
            s1 = cmd_eval(c1, store)
            return cmd_eval(c2, s1)
        case ('if_cmd', e, c1, c2):
            if arith_eval(e, store) != 0:
                return cmd_eval(c1, store)
            else:
                return cmd_eval(c2, store)
        case ('while', e, c):
            # Iterative fixed point — compute until convergence
            s = dict(store)
            for _ in range(10000):   # safety limit
                if arith_eval(e, s) == 0:
                    return s
                s = cmd_eval(c, s)
            raise RuntimeError("Loop did not terminate (limit reached)")

def arith_eval(expr, env):
    match expr:
        case ('num', n):        return n
        case ('var', x):        return env.get(x, 0)
        case ('add', e1, e2):   return arith_eval(e1, env) + arith_eval(e2, env)
        case ('mul', e1, e2):   return arith_eval(e1, env) * arith_eval(e2, env)
        case ('sub', e1, e2):   return arith_eval(e1, env) - arith_eval(e2, env)
        case ('neg_cmp', e):    return 0 if arith_eval(e, env) != 0 else 1
        case ('lte', e1, e2):   return 1 if arith_eval(e1, env) <= arith_eval(e2, env) else 0

# Compute factorial(5) iteratively: n=5, result=1, while n>0: result*=n; n-=1
factorial_prog = (
    'seq', ('assign', 'n', ('num', 5)),
    ('seq', ('assign', 'result', ('num', 1)),
     ('while', ('var', 'n'),
      ('seq', ('assign', 'result', ('mul', ('var', 'result'), ('var', 'n'))),
               ('assign', 'n', ('sub', ('var', 'n'), ('num', 1)))))))

final_store = cmd_eval(factorial_prog, {})
print(f"5! = {final_store['result']}")   # 120
print(f"Final store: {final_store}")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

**CTQs**

> **CTQ 3.1** The denotational meaning of a command is a function from stores to stores. What is the denotational meaning of a non-terminating loop (one that runs forever)? What mathematical object represents this? (Hint: `⊥` — bottom.)

> **CTQ 3.2** Sequence `c₁ ; c₂` is defined as function composition: `⟦c₁ ; c₂⟧ = ⟦c₂⟧ ∘ ⟦c₁⟧`. Write this using the standard Haskell composition operator `(.)`. What does this tell you about the relationship between sequential imperative programming and function composition?

> **CTQ 3.3** The `while` loop uses a "fixed point." Informally: a fixed point of `F` is a value `x` such that `F(x) = x`. If `F(f)(s) = if condition then f(body(s)) else s`, what does `F(identity)(s)` return? What does `F(F(identity))(s)` return? What pattern do you see?

---

#### Model 4 — Domains and Partial Orders (The Math Behind Denotational Semantics)

**Intuition.** In Models 2 and 3 we hand-waved over a crucial detail: what *is* the domain of values when a program might not terminate? A regular set of integers has no room for "no answer." Domain theory solves this by enriching every set with a special least element `⊥` (bottom) and equipping it with a partial order that measures *how much information* a value carries. The meaning of `while` is then built up as an infinite sequence of approximations — each one handles one more possible iteration depth — and the true meaning is the limit of that sequence. This is the mathematical machinery that makes denotational semantics rigorous.

> **Watch out!** Domain theory exists specifically to handle infinite loops and partial functions. Without it, denotational semantics would be inconsistent: the `while` rule would reference itself with no well-founded base case. The key insight is that the chain `f₀ ⊑ f₁ ⊑ f₂ ⊑ ...` always has a least upper bound in a CPO, so the limit is always well-defined — even when the program diverges (in which case the limit is `⊥`).

Non-termination forces us to be careful. We can't just say "the meaning of a non-terminating program is undefined" — we need a mathematical object `⊥` ("bottom") that represents "no answer."

**Domain**: a set `D` with a partial order `⊑` ("approximates") where:
- `⊥ ⊑ d` for all `d ∈ D` (⊥ approximates everything)
- The order reflects "more information": `⊥` = no info, concrete values = full info

**Chain**: a sequence `d₀ ⊑ d₁ ⊑ d₂ ⊑ ...` of increasingly informative approximations

**Complete partial order (CPO)**: every chain has a least upper bound (lub) `⊔`

The meaning of `while` is built up as a chain:

```
f₀ = ⊥         (no iterations: always diverges)
f₁ = F(⊥)      (0 or 1 iterations)
f₂ = F(F(⊥))   (0, 1, or 2 iterations)
...
⟦while e do c⟧ = ⊔ₙ fₙ   (the limit of the chain)
```

```python  liascript
{% raw %}
# Simulate the chain approximation of while-loop semantics
# Each approximation f_k handles at most k iterations

def make_approximation(k, e_fn, c_fn):
    """Build the k-th approximation of while e do c."""
    if k == 0:
        # f_0: always diverge (return None = ⊥)
        return lambda store: None
    else:
        f_prev = make_approximation(k - 1, e_fn, c_fn)
        def f_k(store):
            if e_fn(store) == 0:
                return store              # condition false: exit
            new_store = c_fn(store)
            return f_prev(new_store)     # run body, then apply previous approx
        return f_k

# countdown: n := n - 1, condition: n > 0
def condition(s): return s.get('n', 0)          # true while n != 0
def body(s): return {**s, 'n': s['n'] - 1}      # n := n - 1

print("Chain approximations for 'while n>0 do n:=n-1':")
for k in range(6):
    f = make_approximation(k, condition, body)
    result = f({'n': 3})
    print(f"  f_{k}({{'n': 3}}) = {result}")

# The true fixed point (least upper bound) handles all finite cases:
print("\nTrue semantics (least fixed point):")
import functools
def while_lfp(e_fn, c_fn):
    def run(store):
        s = dict(store)
        while e_fn(s) != 0:
            s = c_fn(s)
        return s
    return run

lfp = while_lfp(condition, body)
print(f"  lfp({{'n': 3}}) = {lfp({'n': 3})}")
print(f"  lfp({{'n': 0}}) = {lfp({'n': 0})}")
{% endraw %}
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

**CTQs**

> **CTQ 4.1** Look at the chain output. At what `k` does `f_k({'n': 3})` first return a non-⊥ result? What does this tell you about how many iterations the loop runs on input `n=3`?

> **CTQ 4.2** If the loop runs forever (e.g., `while 1 do skip`), the chain `f_0, f_1, f_2, ...` is an infinite chain all equal to `⊥`. What is `⊔ₙ fₙ` in this case? Is this the right answer?

> **CTQ 4.3** The CPO approach was developed by Dana Scott and Christopher Strachey in the 1970s. Before this, there was no rigorous mathematical foundation for programming language semantics. Why does this matter for language design today?

---

#### Model 5 — Denotational Semantics for Functions

**Intuition.** So far, values have been integers and stores. But what is the denotation of a *function*? Naturally, it should be a mathematical function — a lambda expression `λx.e` in the object language becomes a genuine `λv. ...` in the mathematics. The twist is that values now include functions, so the domain `V` must satisfy `V ≅ ... + (V → V) + ...` — a self-referential equation. This is not a contradiction: Dana Scott showed in the 1970s that such domain equations have solutions using fixed points of domain constructors. Python sidesteps all this theory because its runtime already supports first-class functions and recursion — but understanding the math tells you *why* the implementation works.

Functions are the hardest part. In the denotational semantics of lambda calculus:

```
⟦λx.e⟧ σ  =  λv. ⟦e⟧ (σ[x ↦ v])
⟦e₁ e₂⟧ σ  =  (⟦e₁⟧ σ) (⟦e₂⟧ σ)
```

The denotation of a lambda is a *mathematical function*. The denotation of an application is *function application*. Perfect compositionality.

But what domain do functions live in? If `V` is the domain of values, then functions have type `V → V`. But that means `V` must contain `V → V` as a subset — a self-referential domain equation!

```
V ≅ ℤ + Bool + (V → V) + ...
```

Scott's breakthrough: **domain equations can be solved** using fixed points of domain constructors. The solution is a domain `D∞` where:

```
D∞ ≅ {⊥} + ℤ + Bool + (D∞ →_c D∞)    (continuous functions)
```

For our purposes, Python handles this automatically:

```python  liascript
# Denotational semantics for lambda calculus in Python
# Values ARE Python functions — the domain equation is solved by Python's object system

def denote(expr, env):
    """⟦expr⟧ env — denotational evaluation of lambda calculus expressions."""
    match expr:
        case ('num', n):
            return n
        case ('bool', b):
            return b
        case ('var', x):
            return env[x]
        case ('lam', x, body):
            # ⟦λx.e⟧ σ = λv. ⟦e⟧ (σ[x↦v])
            return lambda v: denote(body, {**env, x: v})
        case ('app', f, arg):
            # ⟦e1 e2⟧ σ = (⟦e1⟧ σ)(⟦e2⟧ σ)
            return denote(f, env)(denote(arg, env))
        case ('add', e1, e2):
            return denote(e1, env) + denote(e2, env)
        case ('mul', e1, e2):
            return denote(e1, env) * denote(e2, env)
        case ('sub', e1, e2):
            return denote(e1, env) - denote(e2, env)
        case ('if_e', cond, then_, else_):
            return denote(then_, env) if denote(cond, env) else denote(else_, env)
        case ('letrec', f, x, body, cont):
            # letrec f = λx.body in cont  — using Python's fixed-point trick
            def rec(*args):
                new_env = {**env, f: rec}
                return denote(('app', ('lam', x, body), args[0]), new_env)
            return denote(cont, {**env, f: rec})

# Church numeral 2 applied: (λf. λx. f(f(x))) (λy. y+1) 0 = 2
church_2 = ('lam', 'f', ('lam', 'x', ('app', ('var','f'), ('app', ('var','f'), ('var','x')))))
succ = ('lam', 'y', ('add', ('var','y'), ('num', 1)))
two = denote(('app', ('app', church_2, succ), ('num', 0)), {})
print(f"Church 2 applied to (+1) at 0 = {two}")   # 2

# Recursive factorial using letrec
fact_def = ('letrec', 'fact', 'n',
    ('if_e', ('var', 'n'),
        ('mul', ('var', 'n'), ('app', ('var', 'fact'), ('sub', ('var', 'n'), ('num', 1)))),
        ('num', 1)),
    ('app', ('var', 'fact'), ('num', 5)))

print(f"5! = {denote(fact_def, {})}")   # 120
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

**CTQs**

> **CTQ 5.1** The denotation of `(λf. λx. f(f(x)))` is a Python lambda that returns a lambda. Trace through `denote(church_2, {})`. What Python object is returned? What does calling it twice do?

> **CTQ 5.2** In the `letrec` case, `rec` references itself. This implements the fixed-point operator `Y` directly in the meta-language (Python). Compare this to the Y combinator from the lambda calculus activity. What are the similarities?

> **CTQ 5.3** If we replaced Python with a *pure* mathematical framework (no mutation, no self-reference in the host language), we would need `Y` to define recursion. Why is this not a problem in practice when building an interpreter?

---

#### Multiple Choice

In denotational semantics, what does the "semantic function" `⟦·⟧` map?

    [( )] Machine state to machine state
    [( )] Tokens to parse trees
    [(x)] Syntactic programs to mathematical objects (functions, values, domains)
    [( )] Types to type judgments

---

The denotational meaning of `c₁ ; c₂` (sequence) is:

    [( )] Run c₁ and c₂ in parallel, then merge stores
    [(x)] Function composition: apply `⟦c₁⟧` to the store, then apply `⟦c₂⟧` to the result
    [( )] Run c₁, check for errors, then conditionally run c₂
    [( )] Concatenate the bytecode of c₁ and c₂

---

What is `⊥` (bottom) in domain theory?

    [(x)] The least element representing non-termination / no information
    [( )] The boolean value `False`
    [( )] An empty list
    [( )] A syntax error

---

Why does defining `⟦while e do c⟧` require a fixed point?

    [( )] Because loops are circular in memory
    [( )] Because `while` modifies a shared variable
    [(x)] Because the loop body can execute zero or more times — only the least fixed point captures all finite iteration depths plus non-termination
    [( )] Because sequential composition requires commutativity

---

#### Exercises

##### Exercise 1 — Denotational Meaning of Boolean Operators (15 min)

Extend the Arith evaluator with Boolean expressions:

```
b ::= true | false | e₁ = e₂ | e₁ < e₂ | b₁ ∧ b₂ | b₁ ∨ b₂ | ¬b
```

Write the semantic equations (mathematical notation) AND implement them in Python. Test on: `(3 + 1 = 4) ∧ ¬(2 < 1)`.

##### Exercise 2 — Proving Program Equivalence (20 min)

Use the semantic equations to prove that these two programs are semantically equivalent (have the same denotation for all stores and environments):

```
Program 1:  x := x + 1; x := x + 1
Program 2:  x := x + 2
```

Show your work using the semantic equations for `assign` and `seq`.

##### Exercise 3 — Non-Termination as ⊥ (20 min)

Consider the program `while 1 do skip` (infinite loop). 

1. Write the chain: `f₀(s)`, `f₁(s)`, `f₂(s)`, ... for this loop.
2. What is the least upper bound `⊔ₙ fₙ`?
3. Implement this using the `make_approximation` function from Model 4. What does `make_approximation(100, lambda s: 1, lambda s: s)({'x': 0})` return?
4. Why is `⊥` the *right* answer for a non-terminating program, rather than "undefined" or an exception?

##### Exercise 4 — Denotational Semantics for Mini (30 min, harder)

The Mini language has closures and recursion. Write the denotational semantic equations for:

```
⟦fun(x) -> e⟧ σ  =  ?
⟦f(a)⟧ σ          =  ?
⟦let f(x) = e₁ in e₂⟧ σ  =  ?   (recursive definition)
```

Implement `denote_mini(expr, env)` extending Model 5's `denote` function to handle the tuple-based Mini AST. Test with:
- `(fun (x) -> x + 1)(41)` should give `42`
- Recursive `fact(5)` using `letrec` should give `120`

---

#### Reflection

*(Write your answers individually, then discuss with your group.)*

1. **Operational vs. Denotational**: Your tree-walking Mini interpreter uses operational semantics (reduction rules). What would it mean to instead define Mini's semantics denotationally? What would change in the implementation?

2. **Equivalence**: The denotational approach lets us *prove* two programs equivalent by showing their denotations are equal functions. Give an example from your Mini programs where you might want to prove equivalence (e.g., proving an optimization is correct).

3. **Connection to Types**: In the Curry-Howard activity, we saw that "types are propositions." Denotational semantics adds another layer: "types are domains" (sets with structure). How do these two views connect?

---

#### Further Reading

- **"Outline of a Mathematical Theory of Computation"** — Dana Scott (1970): foundational paper establishing domain theory
- **"The Denotational Semantics of Programming Languages"** — Tennent (1976): accessible introduction
- **"Semantics of Programming Languages"** — Gunter (1992): textbook treatment with CPOs
- **"Denotational Semantics"** — Schmidt (1986): free online at https://people.cs.ksu.edu/~schmidt/text/densem.html
- **TAPL Ch. 5** — The Untyped Lambda Calculus — Pierce: connects operational to denotational
- **Haskell's semantics** — bottom (`⊥`) is directly expressible: `undefined :: a`; GHC uses denotational reasoning for optimization via "free theorems"

---

## Going Deeper: Compiler Optimizations: Making Programs Faster

Think of a compiler optimizer as an editor who rewrites a paragraph to say the same thing in fewer words — the meaning is perfectly preserved, but the form is tightened. A compiler does the same thing to your program: it replaces slow, verbose machine instructions with fast, compact ones while guaranteeing that every possible input still produces the same output. Today you will build five such "editors" — constant folding, dead-code elimination, CSE, inlining, and tail-call optimization — each implemented as a tree rewrite over the AST you have been building all semester.

#### Learning Goals

By the end of this activity, you will be able to:

- Implement constant folding and dead-code elimination as AST-to-AST rewrite passes, and state the correctness condition that distinguishes valid from invalid optimizations
- Implement common subexpression elimination (CSE) by identifying redundant computations in an expression and rewriting the AST to share them
- Implement function inlining as an AST substitution pass, and explain when inlining improves and when it hurts performance
- Recognize tail calls in recursive functions, apply the tail-call optimization transformation, and explain why it enables constant-stack recursion

> **Before You Begin — Prerequisites**
>
> You should be comfortable with the following before starting this activity:
>
> - **AST representation**: you know how to represent a program as a tree of dataclass nodes (`Num`, `BinOp`, `Let`, `If`, etc.) and how to walk that tree recursively.
> - **Pattern matching** (`match`/`case`): Python 3.10+ structural pattern matching — used throughout every optimizer below.
> - **Pure vs. side-effectful functions**: you can distinguish between an expression that always produces the same value and one that prints, raises, or mutates state.
> - **Variable scope and substitution**: you understand what "free variable" and "bound variable" mean, and how substituting one expression for another can go wrong (variable capture).
>
> If any of these feel shaky, re-read the functional programming and lambda calculus notes before proceeding — the safety proofs in this activity rely on all four.

> **"The first 90% of the code accounts for the first 90% of the development time. The remaining 10% of the code accounts for the other 90% of the development time."** — Tom Cargill
>
> Optimizations speed up programs *without changing their meaning*. Today you will implement five core optimizations: constant folding, dead code elimination, common subexpression elimination, inlining, and tail call optimization. Each operates on the AST or IR — the same data structures you've been building all semester.

#### Directions and Roles

Work in groups of 3–4. Rotate roles every 20 minutes.

- **Facilitator**: Keeps discussion on track; ensures everyone contributes.
- **Recorder**: Writes down answers and code that the group agrees on.
- **Reporter**: Presents findings to the class; explains the group's reasoning.
- **Reflector**: Monitors group process; writes the reflection at the end.

---

#### Model 1 — What Makes an Optimization Valid?

**Intuition.** Before you can speed anything up, you need a safety rule: *when is a transformation allowed?* The answer is deceptively simple — a transformation is valid if and only if every valid input still produces the same observable output. "Observable" is the key word: printing to the screen is observable; computing an unused intermediate value is not. This section builds the mental checklist that every later optimizer will depend on.

An optimization is **valid** if it *preserves program semantics* — the optimized program produces the same observable results as the original for all valid inputs.

```python  liascript
# Some "optimizations" are INVALID — they change observable behavior

def f():
    print("side effect!")
    return 0

# INVALID: cannot fold f() + 0 → 0 (removes the print side effect)
x = f() + 0    # prints "side effect!" and gives x=0
# "optimized": x = 0   # WRONG — side effect gone!

# VALID: can fold pure expressions
y = 2 + 3 * 4   # evaluates to 14 at compile time
# optimized: y = 14

# INVALID: cannot reorder memory operations (in a language with mutation)
a = [1, 2, 3]
def g(lst):
    lst.append(4)
    return len(lst)

# a[0] = g(a)  -- cannot reorder the call and the subscript

# VALID: can eliminate dead code
if False:
    print("never runs")
# optimized: (remove the entire if block)

print("x =", x, "  y =", y)
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

**Critical Thinking Questions (CTQs)**

> **CTQ 1.1** What property of an expression makes it safe to evaluate at compile time? (Hint: think about the "pure function" discussion from the functional programming module.)

> **CTQ 1.2** The optimizer must prove that `f()` has no observable side effects before it can eliminate `f() + 0`. What information would the optimizer need to know about `f`? Where would it get that information?

> **CTQ 1.3** Name three operations that are NEVER safe to optimize away, even if their result is unused. (Think: division, function calls, I/O.)

> **Watch out!** It is tempting to think "if the result is unused, we can delete it." This is only safe for *pure* expressions. `f() + 0` cannot become `0` if `f` prints, writes to a file, raises an exception, or mutates global state — even though the arithmetic result is discarded. Always ask: "What happens if I remove this entirely?" before applying any optimization.

---

#### Model 2 — Constant Folding and Propagation

**Intuition.** Suppose your program contains `let x = 3 in x + 2`. A human reader sees immediately that `x + 2` must equal `5` — there is no need to wait until run time to add those two numbers. Constant folding does this mechanically: whenever both operands of an arithmetic node are already `Num` literals, replace the whole `BinOp` with the computed `Num`. Constant propagation extends this: once we know `x = 3`, we can substitute `3` for every occurrence of `x` before folding, enabling further reductions downstream. Together the two passes can collapse an entire chain of `let` bindings into a single number.

**Constant folding**: evaluate constant sub-expressions at compile time.
**Constant propagation**: substitute known constant values for variables.

```python  liascript
from dataclasses import dataclass
from typing import Any, Optional

@dataclass
class Num:
    value: float

@dataclass
class Var:
    name: str

@dataclass
class BinOp:
    op: str; left: Any; right: Any

@dataclass
class UnaryOp:
    op: str; operand: Any

@dataclass
class Let:
    name: str; value: Any; body: Any

@dataclass
class If:
    cond: Any; then_: Any; else_: Any

def fold_and_propagate(node, const_env: dict):
    """Constant folding + constant propagation in one pass."""
    match node:
        case Num():
            return node

        case Var(name=n):
            if n in const_env:
                return Num(const_env[n])   # constant propagation
            return node

        case Let(name=n, value=v, body=b):
            folded_v = fold_and_propagate(v, const_env)
            new_env = dict(const_env)
            if isinstance(folded_v, Num):
                new_env[n] = folded_v.value   # propagate this constant!
            return Let(n, folded_v, fold_and_propagate(b, new_env))

        case If(cond=c, then_=t, else_=e):
            fc = fold_and_propagate(c, const_env)
            if isinstance(fc, Num):
                # Dead branch elimination!
                if fc.value != 0:
                    return fold_and_propagate(t, const_env)
                else:
                    return fold_and_propagate(e, const_env)
            return If(fc,
                      fold_and_propagate(t, const_env),
                      fold_and_propagate(e, const_env))

        case UnaryOp(op='-', operand=o):
            fo = fold_and_propagate(o, const_env)
            if isinstance(fo, Num):
                return Num(-fo.value)
            return UnaryOp('-', fo)

        case BinOp(op=op, left=l, right=r):
            fl = fold_and_propagate(l, const_env)
            fr = fold_and_propagate(r, const_env)
            if isinstance(fl, Num) and isinstance(fr, Num):
                match op:
                    case '+': return Num(fl.value + fr.value)
                    case '-': return Num(fl.value - fr.value)
                    case '*': return Num(fl.value * fr.value)
                    case '/' if fr.value != 0: return Num(fl.value / fr.value)
            # Algebraic identities
            if isinstance(fl, Num) and fl.value == 0 and op == '+': return fr
            if isinstance(fr, Num) and fr.value == 0 and op == '+': return fl
            if isinstance(fl, Num) and fl.value == 1 and op == '*': return fr
            if isinstance(fr, Num) and fr.value == 1 and op == '*': return fl
            if isinstance(fl, Num) and fl.value == 0 and op == '*': return Num(0)
            if isinstance(fr, Num) and fr.value == 0 and op == '*': return Num(0)
            return BinOp(op, fl, fr)

def pretty(node) -> str:
    match node:
        case Num(value=v):          return str(int(v) if v == int(v) else v)
        case Var(name=n):           return n
        case Let(name=n, value=v, body=b): return f"let {n}={pretty(v)} in {pretty(b)}"
        case BinOp(op=o, left=l, right=r): return f"({pretty(l)}{o}{pretty(r)})"
        case UnaryOp(op=o, operand=x):     return f"({o}{pretty(x)})"
        case If(cond=c, then_=t, else_=e): return f"if {pretty(c)} then {pretty(t)} else {pretty(e)}"
        case _: return repr(node)

# Test cases
tests = [
    # let x = 3 in let y = x + 2 in x * y  → let x=3 in let y=5 in 15
    Let('x', Num(3), Let('y', BinOp('+', Var('x'), Num(2)),
                        BinOp('*', Var('x'), Var('y')))),
    # if (2 > 0) then 42 else 0  → 42  (dead code eliminated)
    If(BinOp('>', Num(2), Num(0)), Num(42), Num(0)),
    # (x + 0) * 1  → x
    BinOp('*', BinOp('+', Var('x'), Num(0)), Num(1)),
]

for t in tests:
    result = fold_and_propagate(t, {})
    print(f"{pretty(t):50} → {pretty(result)}")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

> **CTQ 2.1** The first test case propagates `x=3` into the body, evaluates `y=5`, then folds `3*5=15`. What is the final result? Is there any variable left in the output?

> **CTQ 2.2** Dead code elimination fires when the `If` condition folds to a known constant. The `2 > 0` case reduces to `Num(1)` (true). But our code doesn't fold `BinOp('>', Num(2), Num(0))` — fix the `fold_and_propagate` function to handle comparison operators.

> **CTQ 2.3** Constant propagation extends the `const_env` when a `let`-bound name gets a constant value. Why do we use `new_env = dict(const_env)` (a copy) rather than mutating `const_env` directly?

---

#### Model 3 — Common Subexpression Elimination (CSE)

**Intuition.** Imagine writing `(x + 1) * (x + 1)` on paper. You would not reach for your calculator twice — you would compute `x + 1` once, write down the answer, then square it. CSE does exactly that: it scans the expression tree for sub-trees that appear more than once (with no intervening mutation), names the shared sub-computation with a fresh `let` binding, and replaces every duplicate occurrence with that name. The original two additions collapse into one, halving the work. The trick is identifying "same expression" in a way that is both correct and efficient — that is what `expr_key` does below.

If the same expression appears twice and has no side effects in between, compute it once and reuse the result.

```python  liascript
from dataclasses import dataclass, field
from typing import Any

@dataclass
class Num:
    value: float

@dataclass
class Var:
    name: str

@dataclass
class BinOp:
    op: str; left: Any; right: Any

@dataclass
class Let:
    name: str; value: Any; body: Any

# Simple CSE: replace duplicate sub-expressions with shared variables
_cse_counter = 0
def fresh_name():
    global _cse_counter
    _cse_counter += 1
    return f"_cse{_cse_counter}"

def cse(node, seen: dict):
    """
    seen: maps (expr_key) → variable_name
    Returns (optimized_node, bindings_to_wrap)
    """
    key = expr_key(node)

    # Pure expression seen before? Reuse it!
    if key in seen and is_pure(node):
        return Var(seen[key]), []

    match node:
        case Num() | Var():
            return node, []

        case BinOp(op=op, left=l, right=r):
            new_l, binds_l = cse(l, seen)
            new_r, binds_r = cse(r, seen)
            new_node = BinOp(op, new_l, new_r)
            new_key = expr_key(new_node)
            name = fresh_name()
            seen[new_key] = name
            return Var(name), binds_l + binds_r + [(name, new_node)]

        case _:
            return node, []

def expr_key(node) -> str:
    """Canonical string representation for hashing."""
    match node:
        case Num(value=v): return f"N{v}"
        case Var(name=n):  return f"V{n}"
        case BinOp(op=o, left=l, right=r): return f"({expr_key(l)}{o}{expr_key(r)})"
        case _: return repr(node)

def is_pure(node) -> bool:
    """True if the expression has no side effects."""
    match node:
        case Num() | Var():          return True
        case BinOp(left=l, right=r): return is_pure(l) and is_pure(r)
        case _:                      return False

def wrap_bindings(node, bindings):
    """Wrap the result in let-bindings for CSE temporaries."""
    for name, val in reversed(bindings):
        node = Let(name, val, node)
    return node

def pretty(node) -> str:
    match node:
        case Num(value=v):  return str(int(v) if v == int(v) else v)
        case Var(name=n):   return n
        case BinOp(op=o, left=l, right=r): return f"({pretty(l)}{o}{pretty(r)})"
        case Let(name=n, value=v, body=b):  return f"let {n}={pretty(v)} in\n  {pretty(b)}"

# Expression: (x+1)*(x+1) — x+1 computed TWICE
from dataclasses import dataclass
_cse_counter = 0

x_plus_1 = BinOp('+', Var('x'), Num(1))
expr = BinOp('*', x_plus_1, x_plus_1)

optimized_core, bindings = cse(expr, {})
optimized = wrap_bindings(optimized_core, bindings)

print("Before CSE:")
print(f"  {pretty(expr)}")
print("\nAfter CSE:")
print(f"  {pretty(optimized)}")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

> **CTQ 3.1** After CSE, `(x+1)*(x+1)` should become `let _cse1 = (x+1) in _cse1 * _cse1`. Only ONE addition is computed instead of two. How many operations were eliminated?

> **CTQ 3.2** Why does CSE only apply to *pure* expressions? Give an example where applying CSE to an impure expression would change the program's behavior.

> **CTQ 3.3** CSE requires checking if two expressions are "the same." The `expr_key` function produces a canonical string. What's wrong with this approach if expressions contain variable names that were renamed by earlier passes?

> **Watch out!** CSE introduces new variable bindings (`_cse1`, `_cse2`, …). If you run CSE before constant propagation, those new variables will block the propagation pass from recognizing constants. If you run CSE after constant propagation, some sub-expressions that *looked* identical before may differ because their variables were replaced by different constants. Order matters — design your pipeline intentionally.

---

#### Model 4 — Function Inlining

**Intuition.** Every function call costs something: push arguments onto the stack, jump to the callee, eventually jump back, clean up. For a tiny function like `double(x) = x + x`, the bookkeeping overhead may actually exceed the cost of the addition. Inlining copies the function body to the call site, replacing the parameter with the actual argument — the call vanishes entirely. As a bonus, the inlined body is now visible to the surrounding optimizations, so constant folding or CSE may fire again on the merged code. The danger: inlining a large function (or worse, a recursive one) causes code-size explosion, so every production inliner has a size threshold.

**Inlining** replaces a function call with the function body, substituting arguments for parameters. This eliminates call overhead and enables further optimizations.

```python  liascript
from dataclasses import dataclass
from typing import Any

@dataclass
class Num:
    value: float

@dataclass
class Var:
    name: str

@dataclass
class BinOp:
    op: str; left: Any; right: Any

@dataclass
class Let:
    name: str; value: Any; body: Any

@dataclass
class Lambda:
    param: str; body: Any

@dataclass
class App:   # function application
    func: Any; arg: Any

def substitute(node, var: str, replacement):
    """Replace all free occurrences of var with replacement."""
    match node:
        case Num():                  return node
        case Var(name=n):            return replacement if n == var else node
        case BinOp(op=o, left=l, right=r):
            return BinOp(o, substitute(l, var, replacement),
                            substitute(r, var, replacement))
        case Let(name=n, value=v, body=b):
            new_v = substitute(v, var, replacement)
            if n == var:
                return Let(n, new_v, b)   # var is shadowed in body
            return Let(n, new_v, substitute(b, var, replacement))
        case Lambda(param=p, body=b):
            if p == var: return node   # var is shadowed
            return Lambda(p, substitute(b, var, replacement))
        case App(func=f, arg=a):
            return App(substitute(f, var, replacement),
                       substitute(a, var, replacement))
        case _: return node

def inline(node, fn_env: dict, inline_limit=5):
    """Inline small functions. fn_env maps name → Lambda."""
    match node:
        case App(func=Var(name=n), arg=a) if n in fn_env:
            lam = fn_env[n]
            if size(lam.body) <= inline_limit:  # only inline small functions
                inlined = substitute(lam.body, lam.param, inline(a, fn_env))
                return inline(inlined, fn_env)   # inline recursively!
        case App(func=f, arg=a):
            return App(inline(f, fn_env), inline(a, fn_env))
        case BinOp(op=o, left=l, right=r):
            return BinOp(o, inline(l, fn_env), inline(r, fn_env))
        case _:
            return node

def size(node) -> int:
    """Estimate node count (cost of inlining)."""
    match node:
        case Num() | Var():          return 1
        case BinOp(left=l, right=r): return 1 + size(l) + size(r)
        case Lambda(body=b):         return 1 + size(b)
        case App(func=f, arg=a):     return 1 + size(f) + size(a)
        case _:                      return 1

def pretty(node) -> str:
    match node:
        case Num(value=v):           return str(int(v) if v == int(v) else v)
        case Var(name=n):            return n
        case BinOp(op=o, left=l, right=r): return f"({pretty(l)}{o}{pretty(r)})"
        case Lambda(param=p, body=b):       return f"λ{p}.{pretty(b)}"
        case App(func=f, arg=a):            return f"{pretty(f)}({pretty(a)})"
        case Let(name=n, value=v, body=b):  return f"let {n}={pretty(v)} in {pretty(b)}"

# double = λx. x + x  — inline double(5) → 5 + 5
double = Lambda('x', BinOp('+', Var('x'), Var('x')))
fn_env = {'double': double}

expr = App(Var('double'), Num(5))
inlined = inline(expr, fn_env)
print(f"Before: {pretty(expr)}")
print(f"After:  {pretty(inlined)}")

# Compose with constant folding: double(3+2) → (3+2)+(3+2) → 10
from functools import reduce
expr2 = App(Var('double'), BinOp('+', Num(3), Num(2)))
inlined2 = inline(expr2, fn_env)
print(f"\nBefore: {pretty(expr2)}")
print(f"Inlined: {pretty(inlined2)}")
# (After constant folding, this would become 10)
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

> **CTQ 4.1** Inlining `double(5)` produces `5 + 5`. Can we further fold this? What optimization would you chain after inlining?

> **CTQ 4.2** The inline limit `inline_limit=5` prevents inlining large functions. Why? What happens to code size if you inline aggressively without a limit?

> **CTQ 4.3** Inlining a recursive function directly would loop forever. How does the limit protect against this? What more sophisticated check would be needed for a production compiler?

---

#### Model 5 — Tail Call Optimization (TCO)

**Intuition.** Consider a recursive function where the very last thing it does before returning is call itself. At the moment that recursive call happens, the current stack frame has no remaining work to do — it will just forward whatever the callee returns. That frame is wasted space. TCO exploits this: instead of pushing a new frame, the compiler converts the call into a backward jump that reuses the existing frame, effectively turning the recursion into a loop. A tail-recursive function compiled with TCO uses *constant* stack space no matter how deep the recursion goes. Functional languages like Scheme, Haskell, and Erlang mandate TCO; Python does not implement it natively, but you can simulate it with a trampoline.

A **tail call** is a function call that is the *last* action of a function. Instead of creating a new stack frame, we can *reuse* the current frame.

```python  liascript
import sys

# Without TCO: factorial(10000) causes stack overflow in Python
def factorial_no_tco(n):
    if n <= 1: return 1
    return n * factorial_no_tco(n - 1)   # NOT a tail call: n * (...)

# With an accumulator, the recursive call IS a tail call:
def factorial_tco_helper(n, acc):
    if n <= 1: return acc
    return factorial_tco_helper(n - 1, n * acc)   # TAIL CALL: last action

def factorial_tco(n):
    return factorial_tco_helper(n, 1)

# Trampolining: simulate TCO in Python using thunks
class Thunk:
    def __init__(self, fn, *args):
        self.fn = fn; self.args = args
    def __call__(self):
        return self.fn(*self.args)

def trampoline(fn, *args):
    result = fn(*args)
    while isinstance(result, Thunk):
        result = result()
    return result

def fact_tramp(n, acc=1):
    if n <= 1: return acc
    return Thunk(fact_tramp, n - 1, n * acc)   # return thunk, not recursive call

print(f"factorial_tco(100)   = {factorial_tco(100)}")
print(f"fact_tramp(100)      = {trampoline(fact_tramp, 100)}")

# Without trampoline: would hit recursion limit at ~1000
# With trampoline: works for any n (constant stack depth!)
print(f"fact_tramp(5000)     = ...{str(trampoline(fact_tramp, 5000))[-5:]}")  # last 5 digits

# Detecting tail calls in an AST:
from dataclasses import dataclass
from typing import Any

@dataclass
class Call:
    fn_name: str; args: list

@dataclass
class If:
    cond: Any; then_: Any; else_: Any

@dataclass
class Return:
    value: Any

def is_tail_call(node, fn_name: str) -> bool:
    """Does node end with a tail call to fn_name?"""
    match node:
        case Return(value=Call(fn_name=n)) if n == fn_name:
            return True
        case If(then_=t, else_=e):
            return is_tail_call(t, fn_name) or is_tail_call(e, fn_name)
        case _:
            return False

# fact(n, acc) = if n<=1 then return acc else return fact(n-1, n*acc)
fact_body = If(None,
    Return(None),   # return acc — not a tail call to fact
    Return(Call('fact', []))   # return fact(...) — IS a tail call!
)
print(f"\nfact body has tail call to 'fact': {is_tail_call(fact_body, 'fact')}")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

> **CTQ 5.1** `factorial_no_tco` has `return n * factorial_no_tco(n-1)`. Why is this NOT a tail call? What computation happens after the recursive call returns?

> **CTQ 5.2** `factorial_tco_helper` has `return factorial_tco_helper(n-1, n*acc)`. Why IS this a tail call? What does "last action" mean precisely?

> **CTQ 5.3** Trampolining achieves tail call optimization without changing the language runtime — it works in Python, Java, or any language. What is the tradeoff compared to a language that natively supports TCO (like Scheme or Haskell)?

> **Watch out!** Not every recursive call in a tail position belongs to a *tail-recursive* function. Mutual recursion (`f` calls `g`, which calls `f`) also creates tail calls, and TCO applies there too — but detecting it requires tracking which functions are in the current call chain. The simple `is_tail_call` detector below only checks for self-recursion. A production compiler needs to handle the mutual case, which is why Scheme's TCO guarantee covers all proper tail calls, not just self-calls.

---

#### Multiple Choice

Which optimization is UNSAFE to apply to `result = print("hello") or True`?

    [(x)] Replacing `print("hello")` with its constant value (it returns `None`)
    [( )] Evaluating `True` at compile time
    [( )] Keeping the original expression unchanged
    [( )] All of the above

---

Constant propagation extends the environment with `{x: 3}` when `let x = 3`. Why is it safe to propagate this constant throughout the body?

    [( )] Because x is an integer
    [(x)] Because `let` creates an immutable binding — x's value cannot change in the body
    [( )] Because 3 is small enough to inline
    [( )] Because the compiler checked for side effects

---

A tail call optimization converts a tail-recursive call into a loop at compile time. What benefit does this provide?

    [( )] Faster garbage collection
    [(x)] Constant stack space instead of O(n) stack frames — enables deep or infinite recursion without stack overflow
    [( )] Smaller bytecode
    [( )] Type safety

---

#### Exercises

##### Exercise 1 — Fix Comparison Folding (15 min)
Extend `fold_and_propagate` from Model 2 to handle comparison operators (`>`, `<`, `>=`, `<=`, `==`, `!=`) and boolean operators (`and`, `or`, `not`). Test: `if (2 > 1) then 42 else 0` should fold to `42`.

##### Exercise 2 — Strength Reduction (20 min)
**Strength reduction** replaces expensive operations with cheaper ones:
- `x * 2` → `x + x` (addition is faster than multiplication on some CPUs)
- `x * 4` → `x << 2` (shift is faster than multiplication by a power of 2)
- `x / 2` → `x >> 1` (for integer division)

Implement `strength_reduce(node)` as a tree transformation. Test on `y * 8` and `z / 4`.

##### Exercise 3 — Dead Code Elimination (20 min)
Write `eliminate_dead_code(node, live_vars: set)` that removes let-bindings whose names are never used in the body:

```
let x = expensive_computation() in 42
→ 42  (if x is never used)
```

But be careful: only eliminate if the binding expression is pure!

##### Exercise 4 — Optimization Pipeline (25 min)
Combine multiple passes into a pipeline:
```python  liascript
def optimize(node):
    node = fold_and_propagate(node, {})
    node = eliminate_dead_code(node, collect_live_vars(node))
    node = inline(node, fn_env)
    node = fold_and_propagate(node, {})  # run again after inlining!
    return node
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)
Test the pipeline on a program that contains all four optimization opportunities. Show before and after.

##### Exercise 5 — Mini TCO (30 min, harder)
Add tail call optimization to your Mini interpreter:
1. Write `is_tail_position(node, current_fn_name)` that returns True if a node is a tail call
2. Modify your evaluator: when a tail call is detected, instead of recursing, update the parameters and loop (use a `while True` loop in the evaluator)
3. Demonstrate: `fact(10000)` works without stack overflow after TCO, but fails without it

---

#### Reflection

*(Write your answers individually, then discuss with your group.)*

1. **Safety vs. speed**: Every optimization in this module requires a safety proof ("this is valid because..."). What does this tell you about the relationship between semantics and optimization? Could you optimize a language you don't have a formal semantics for?

2. **Optimization order matters**: We ran constant folding *after* inlining. Why? Could you run them in the opposite order and get the same result? What does this say about the design of an optimization pipeline?

3. **Your final project**: Which of today's optimizations would you add to your Mini language? Which would require the most implementation effort? Pick one and sketch the implementation.

---

#### Further Reading

- **"Engineering a Compiler"** — Cooper & Torczon, Chapters 8-10: the canonical compiler optimization textbook
- **"Compilers: Principles, Techniques, and Tools"** — Aho, Lam, Sethi, Ullman (Dragon Book): Chapters 9-10
- **"Compiling with Continuations"** — Appel: how CPS enables many optimizations uniformly
- **GCC optimization flags** — `gcc -O2` enables ~50 optimizations; the manual lists them all
- **LLVM passes** — each LLVM optimization is a separate pass; the source code is readable: https://llvm.org/docs/Passes.html
- **"Hacker's Delight"** — Henry Warren: arithmetic tricks behind strength reduction

---

## Going Deeper: Libraries and Modules in Programming Languages

Library design is a form of language design. When you reach for `pathlib`, `requests`, or `pandas`, you are not just calling functions — you are working inside a *mini-language* purpose-built for a domain. A well-designed library API should feel like the language was extended exactly for your problem: the vocabulary fits, the operations compose naturally, and you rarely have to fight the underlying language to express your intent. A poorly designed library feels like assembling flat-pack furniture in a language you barely speak — technically possible, but exhausting. This activity examines the machinery underneath library design: how Python's module system isolates names, loads code on demand, and lets library authors control what they expose to the outside world.

#### Learning Goals

By the end of this activity, you will be able to:

- Explain how Python's module system uses namespaces and `sys.modules` to isolate names and prevent re-execution on repeated imports
- Trace name resolution through nested scopes and module namespaces, predicting which binding is selected for a given identifier
- Implement a minimal module system in Python — loading, caching, and exposing a controlled public API — from first principles
- Compare explicit exports (`__all__`, `__init__.py`) with fully open namespaces and evaluate the encapsulation tradeoffs
- Analyze circular import scenarios and explain why they arise and how module caching either resolves or deepens them

> **Before You Begin**
>
> This activity assumes you are comfortable with:
>
> - **Python functions and scope** — you should know what a local variable is and have a rough sense that Python looks up names in some order (local before global).
> - **Basic `import` usage** — you have written `import math` or `from os import path` before, even if you have never thought about *why* it works.
> - **Dictionaries** — module namespaces, `sys.modules`, and the mini-interpreter in Part III are all built on Python dicts.
>
> You do *not* need prior knowledge of how interpreters work — Part III builds that understanding from scratch.

Every non-trivial program is an assembly of parts: code you wrote, code your colleagues wrote, and code the language ecosystem provides. The mechanisms that let these parts coexist — without stomping on each other's names, without loading code you don't need, and without requiring every collaborator to agree on internal naming — are collectively called the **module system**. Today you dissect Python's module system from the outside in, and then build a miniature one from scratch.

Arc: **the problem modules solve → namespaces and name lookup → dynamic loading → controlling the public API → implementing a module system**

---

#### Directions and Group Roles

Work in your POGIL team with rotated roles (**Manager**, **Recorder**, **Presenter**, **Reflector**). Consider each model individually first, then discuss with your group.

---

### Part I: The Module System from the Outside

#### Model 1: Python's Module System

**Intuition.** Imagine you and a colleague each define a variable called `result` at the top of your respective files. Without modules, these names would collide. A module is Python's answer: each `.py` file gets its own *namespace* — a private dictionary of names — so your `result` and your colleague's `result` never interfere. When you `import math`, Python evaluates `math.py` once, stores the resulting namespace object in a cache called `sys.modules`, and hands you a reference to it. Every subsequent `import math` anywhere in the program returns the *same cached object* — `math.py` is never evaluated twice. That single fact explains a surprising amount of Python's runtime behavior.

A Python module is just a `.py` file whose top-level bindings become the module's **namespace**. `import` evaluates that file (once) and caches the resulting namespace object. The cache — `sys.modules` — prevents re-execution on repeated imports and is the source of truth for "is this module loaded?"

```python  liascript
import sys
import math
import os.path

# A module is a first-class object
print(type(math))             # <class 'module'>
print(dir(math)[:10])         # first 10 attributes of the module
print(math.pi)                # accessing a module-level name
print(math.__file__)          # where the module lives on disk

# sys.modules is the module cache
print('math' in sys.modules)  # True — already imported
print('json' in sys.modules)  # False if not yet imported

import json
print('json' in sys.modules)  # True now

# __name__ behavior
print(f"This file's __name__: {__name__}")
# When run directly: __main__; when imported: the module name
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

> **Watch out!** `sys.modules` is a *live, mutable* dictionary. If a module has side effects (prints output, opens a file, registers a handler) those side effects fire the *first* time the module is imported — never again on re-import, because the cache is hit. This means the order in which modules are first imported can change your program's observable behavior in ways that are hard to debug. Prefer modules with no top-level side effects; put startup logic inside `if __name__ == '__main__':` or explicit initialization functions.

**Critical Thinking Questions (CTQs)**

> **CTQ 1.1** What is the difference between `import math` and `from math import pi`? After each form, what names appear in the calling module's namespace?

> **CTQ 1.2** `sys.modules` is a plain dictionary. What happens if you delete a key from it and then re-import the corresponding module? (Think through the logic of `import` before running any code.)

> **CTQ 1.3** What does the guard `if __name__ == '__main__':` check? Give a concrete scenario where forgetting this guard causes an unintended side effect when your file is imported by someone else.

> **CTQ 1.4** `math.__file__` shows the `.py` or `.so` path. Why might a module not have a `__file__` attribute at all? Name one category of Python module where this is true.

---

#### Model 2: Namespaces and Symbol Tables

**Intuition.** Every name in Python — `x`, `print`, `Counter` — is resolved by searching a chain of dictionaries in a fixed order. The rule is **LEGB**: Local first, then Enclosing (for nested functions), then Global (the module's top-level dict), then Built-in (Python's built-in names like `len` and `True`). Python stops at the first dictionary that contains the name. This is not just trivia: it is the mechanism that makes closures work, that lets you shadow a built-in inside a function without breaking it globally, and that explains exactly what `globals()` and `locals()` return. Each scope is a real Python dictionary you can inspect and even mutate at runtime.

Python resolves every name by searching a chain of **namespaces** from innermost to outermost. The rule is called **LEGB**: Local → Enclosing → Global → Built-in. Each scope is a dictionary, and `globals()`, `locals()`, and `vars()` expose them at runtime.

```python  liascript
# Global namespace
x = 10
y = 20

def outer():
    # Enclosing namespace
    a = 100
    def inner():
        # Local namespace
        b = 200
        print(f"local vars:    {sorted(locals().keys())}")
        print(f"b={b}, a={a}, x={x}")   # LEGB lookup: b→local, a→enclosing, x→global
    inner()
    print(f"outer locals:  {sorted(locals().keys())}")

outer()

# Inspect the global namespace
g = globals()
print(f"\nglobal names: {sorted(k for k in g.keys() if not k.startswith('_'))}")

# Modules have their own namespace
import math
print(f"\nmath namespace sample: {[k for k in dir(math) if not k.startswith('_')][:8]}")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

> **CTQ 2.1** Describe the LEGB rule in your own words. If a name appears in both the local scope and the global scope, which one does Python use? What would you write to explicitly access the global one?

> **CTQ 2.2** What does `globals()` return? Is it a snapshot or a live view? Write a one-line expression that adds a new global variable at runtime using `globals()`.

> **CTQ 2.3** A module's namespace is stored in `module.__dict__`. What does that tell you about how `import math; math.pi` is implemented under the hood? Trace the attribute lookup.

> **CTQ 2.4** Python's built-in scope (the `B` in LEGB) holds names like `len`, `print`, and `True`. Where is this namespace stored? How would you shadow `len` for a single function without affecting the rest of the program?

---

### Part II: Dynamic Loading and API Control

#### Model 3: Dynamic Loading with importlib

**Intuition.** A static `import` at the top of a file is like hardwiring a component into a circuit board — it is always there, whether you use it or not. Dynamic loading is like a hot-swappable module bay: you decide *at runtime* which code to load, based on configuration, user input, or the capabilities of the current system. This pattern is essential for plugin architectures (a text editor that loads language-specific formatters on demand), feature flags (loading a fast C extension if available, falling back to a pure-Python implementation), and test harnesses (replacing real modules with mocks). The key tool is `importlib.import_module(name)`, which accepts a string and returns the module object — just as if you had written `import name`.

Static `import` statements are resolved at parse time (or at least before the function body runs). **Dynamic loading** resolves a module name given only as a runtime string — essential for plugin architectures, configuration-driven dispatch, and test harnesses.

```python  liascript
import importlib
import sys

# Dynamic import by string name
module_name = "math"
mod = importlib.import_module(module_name)
print(f"Dynamically loaded: {mod.__name__}")
print(f"sqrt(16) = {mod.sqrt(16)}")

# Get an attribute dynamically
func_name = "factorial"
func = getattr(mod, func_name, None)
if func:
    print(f"math.{func_name}(5) = {func(5)}")
else:
    print(f"{func_name} not found in {module_name}")

# Simulate a plugin system
PLUGINS = ["math", "os.path", "json"]
loaded = {}
for name in PLUGINS:
    try:
        loaded[name] = importlib.import_module(name)
        print(f"Loaded plugin: {name}")
    except ImportError as e:
        print(f"Failed to load {name}: {e}")

print(f"\nLoaded plugins: {list(loaded.keys())}")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

> **Watch out!** Dynamic loading is a security surface. If the string passed to `importlib.import_module` comes from user input — a config file, a URL parameter, a command-line flag — a malicious user can cause your program to import arbitrary code. Always validate dynamic module names against an explicit allowlist (e.g., `assert name in ALLOWED_PLUGINS`) before loading. Never pass unsanitized user input directly to `import_module`.

> **CTQ 3.1** What is the difference between `import math` (static) and `importlib.import_module("math")` (dynamic)? When is each approach appropriate?

> **CTQ 3.2** A plugin system reads plugin names from a config file and loads them at startup. List two concrete benefits of dynamic loading over listing every plugin with a static `import`. What would need to change in the code to add a new plugin?

> **CTQ 3.3** `getattr(mod, func_name, None)` returns `None` if the attribute does not exist, rather than raising `AttributeError`. How does this pattern relate to the "ask forgiveness, not permission" idiom in Python? When would you prefer `hasattr` + `getattr` instead?

> **CTQ 3.4** What security concern does dynamic loading introduce when the module name comes from user input? Describe a minimal mitigation strategy.

---

#### Model 4: `__all__`, `__init__.py`, and Module Interfaces

**Intuition.** A library's public API is a *promise*. Everything you expose to callers is something you must maintain and keep stable; everything you keep internal can change freely. Python has no access modifiers like `private` or `protected` — by convention, names starting with `_` are internal, and `__all__` explicitly lists what `from module import *` should export. This is library design as a language design decision: by controlling what names you expose, you are defining the vocabulary of your mini-language. A well-curated `__all__` tells callers exactly which abstractions they are supposed to think in, and shields them from implementation details they should not depend on.

A module's **public interface** is the set of names that clients are expected to use. Python enforces this convention through `__all__`: a list of names that `from module import *` will bind in the caller's namespace. Without `__all__`, the star import brings in every name that does not start with `_`.

```python  liascript
# Simulate a package's __all__ behavior
# A module can declare its public API via __all__

# Imagine this is mypackage/__init__.py:
_private_helper = "internal only"
public_api_function = "this is exported"

__all__ = ["public_api_function", "MyClass"]

class MyClass:
    def __init__(self, value):
        self.value = value
    def greet(self):
        return f"Hello from {self.value}"

class _InternalClass:
    pass

# When someone does: from mypackage import *
# they get only what's in __all__
print(f"__all__ = {__all__}")

# Demonstrate: what 'import *' would bring in from math
exec("from math import *")   # imports everything in math.__all__
import math
print(f"\nmath.__all__ exists: {hasattr(math, '__all__')}")
print(f"math has {len(dir(math))} total names")
print(f"pi is now in globals: {'pi' in dir()}")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

> **CTQ 4.1** What is the purpose of `__all__`? What happens with `from module import *` when `__all__` is defined? What happens when it is not defined?

> **CTQ 4.2** `_InternalClass` starts with an underscore. Even without `__all__`, `from module import *` will not import it. What is the convention here? Does the underscore prefix provide any real access control?

> **CTQ 4.3** Why does **namespace pollution** matter? Give a concrete example where `from module import *` in two successive lines could silently break a program.

> **CTQ 4.4** A Python **package** is a directory containing an `__init__.py`. When you write `import mypackage.submodule`, which file runs first? What is `__init__.py` for?

---

### Part III: Building a Module System

#### Model 5: Implementing a Module System in a Mini Interpreter

**Intuition.** The best way to truly understand a mechanism is to build a stripped-down version of it. A module system has three core parts: (1) an **environment** — a dictionary mapping names to values, which is what a module *is*; (2) a **registry** — a dictionary mapping module names to their environments, which is what `sys.modules` *is*; and (3) **import operations** — procedures that look up a name in the registry and copy bindings into the caller's environment. Everything else in Python's real import system (finders, loaders, bytecode caching, relative imports) is elaboration on these three ideas. The mini-interpreter here is deliberately bare-bones so each concept is visible without distraction.

The models above described Python's module system as a user. Now we build one. The core idea is simple: a **module** is an **environment** (a namespace), and a **module registry** is a dictionary from names to environments — exactly what `sys.modules` is.

```python  liascript
from dataclasses import dataclass, field
from typing import Any, Optional

@dataclass
class Env:
    """An environment (namespace) for the interpreter."""
    bindings: dict = field(default_factory=dict)
    parent: Optional['Env'] = None

    def define(self, name: str, value: Any):
        self.bindings[name] = value

    def lookup(self, name: str) -> Any:
        if name in self.bindings:
            return self.bindings[name]
        if self.parent:
            return self.parent.lookup(name)
        raise NameError(f"Undefined: {name}")

@dataclass
class ModuleRegistry:
    """Registry of loaded modules — like sys.modules."""
    modules: dict = field(default_factory=dict)

    def register(self, name: str, env: Env):
        self.modules[name] = env

    def load(self, name: str) -> Env:
        if name in self.modules:
            return self.modules[name]
        raise ImportError(f"No module named '{name}'")

# Simulate building a stdlib module
stdlib_env = Env()
stdlib_env.define("add", lambda a, b: a + b)
stdlib_env.define("mul", lambda a, b: a * b)
stdlib_env.define("PI", 3.14159)

# Register it in the module system
registry = ModuleRegistry()
registry.register("mymath", stdlib_env)

# Simulate "import mymath"
def do_import(registry: ModuleRegistry, module_name: str, global_env: Env):
    mod_env = registry.load(module_name)
    # Create a module object in global_env
    module_obj = {"__name__": module_name, "__env__": mod_env}
    global_env.define(module_name, module_obj)
    return module_obj

# User code: import mymath, call mymath.add(2, 3)
user_env = Env()
mod = do_import(registry, "mymath", user_env)
add_fn = mod["__env__"].lookup("add")
print(f"mymath.add(2, 3) = {add_fn(2, 3)}")
print(f"mymath.PI        = {mod['__env__'].lookup('PI')}")

# Verify the registry now holds the module
print(f"'mymath' in registry: {'mymath' in registry.modules}")

# Simulate "from mymath import mul"
def do_from_import(registry: ModuleRegistry, module_name: str,
                   name: str, target_env: Env):
    mod_env = registry.load(module_name)
    value = mod_env.lookup(name)
    target_env.define(name, value)

do_from_import(registry, "mymath", "mul", user_env)
mul_fn = user_env.lookup("mul")
print(f"mul(3, 4) = {mul_fn(3, 4)}")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

> **CTQ 5.1** How does `ModuleRegistry` relate to Python's `sys.modules`? What key operation does `registry.load` correspond to in the real import system?

> **CTQ 5.2** `do_import` binds a **module object** (a dict) into `global_env`. In Python, `import math` creates a name `math` in the caller's namespace that refers to the module object. Trace the parallel: what is the module object in Python, and how does attribute access (`math.pi`) work in terms of the module's `__dict__`?

> **CTQ 5.3** `do_from_import` copies a single binding from the module's environment into the caller's environment. After `from mymath import mul`, if you redefine `mymath.mul` in the registry, does the caller's `mul` reflect the change? Why or why not?

> **Watch out!** Circular imports are one of the most confusing bugs in Python. Module A imports B; during B's initialization, B imports A — but A is not fully initialized yet, so the partially-built module object is what B gets. If B tries to access a name from A that has not been defined yet in A's initialization sequence, you get an `AttributeError` or `ImportError`, even though the `import` statement itself succeeds. The fix Python uses — inserting a placeholder entry into `sys.modules` before running the module body — prevents infinite recursion but does not prevent partially-initialized modules from being used. The real fix is to restructure your dependencies to avoid the cycle.

> **CTQ 5.4** To support **circular imports** (module A imports B, B imports A), what single change to `do_import` would prevent infinite recursion? (Hint: look at how Python handles this with a partially-initialized module entry in `sys.modules`.)

---

[[MC]]
What does `sys.modules` contain?

    [(x)] A cache of all already-imported modules
    [( )] The list of directories Python searches for modules
    [( )] The set of built-in Python functions
    [( )] The currently executing module's globals

---

[[MC]]
What is the purpose of `__all__` in a Python module?

    [(x)] It controls which names are exported with `from module import *`
    [( )] It lists all function names defined in the module
    [( )] It speeds up import by pre-caching attribute lookups
    [( )] It defines the module's required dependencies

---

[[MC]]
What is a Python **package**?

    [(x)] A directory containing an `__init__.py` file that groups related modules
    [( )] A single `.py` source file
    [( )] A compiled `.pyc` bytecode file
    [( )] A zip archive of modules installed by pip

---

[[MC]]
In the LEGB rule, when Python looks up variable `x`, where does it look **last**?

    [( )] Local scope
    [( )] Enclosing scope
    [( )] Global scope
    [(x)] Built-in scope

---

#### Exercises

##### Exercise 1 — Lazy Import Cache (20 min)

Write a `lazy_import(name)` function that returns a proxy: the first time the proxy is used (e.g., its attribute is accessed), it imports the module and caches it; subsequent accesses use the cached copy. You may use a plain dict as the cache. Demonstrate that the module is only loaded on first access by printing a message inside the import logic.

- (a) Implement `lazy_import(name)` returning a callable proxy object.
- (b) Show that calling `lazy_import("math")` twice loads the module only once.
- (c) Explain how this pattern is used in large frameworks to reduce startup time.

##### Exercise 2 — Namespace Merge (15 min)

Implement `namespace_merge(ns1: dict, ns2: dict) -> dict` that merges two namespace dicts. If the same name appears in both, raise a custom `NamespaceConflict` exception that includes the conflicting name in its message.

- (a) Implement `NamespaceConflict` as a subclass of `Exception`.
- (b) Implement `namespace_merge` and test it with two disjoint dicts (should succeed) and two dicts with a shared key (should raise).
- (c) When would namespace merging arise in a real language runtime? (Hint: think about `import *` from two modules.)

##### Exercise 3 — `from module import name` in the Mini Interpreter (25 min)

Extend the `ModuleRegistry` from Model 5 to support `from module import name` more robustly.

- (a) Add a `do_from_import_star(registry, module_name, target_env)` function that imports all names from the module (simulating `from module import *`).
- (b) Add optional `__all__` support: if `module_env` contains a binding for `"__all__"` (a list of strings), only import those names.
- (c) Demonstrate with a module that defines `__all__ = ["add", "PI"]` but also contains `_secret = 42`.

##### Exercise 4 — Module Reload (20 min)

Write a `reload_module(name, registry, init_fn)` function that re-executes a module's initialization code (simulating Python's `importlib.reload`). `init_fn` is a callable that takes an `Env` and populates it.

- (a) Implement `reload_module` so it creates a fresh `Env`, calls `init_fn` on it, and updates the registry entry.
- (b) Show that code holding a reference to the **old** module object does not see the reload, but code that looks up the module via the registry does.
- (c) When is `importlib.reload` useful in practice? When is it dangerous?

---

#### Reflection Prompt

Python, JavaScript (ESM/CommonJS), and Java each solved the module problem differently — Python uses a flat file-based namespace with a global cache; JavaScript ESM uses static graph analysis with live bindings; Java uses a class-loader hierarchy with explicit visibility modifiers. What are the fundamental design decisions every module system must make? Consider: separate compilation and link-time resolution, circular imports, versioning and diamond dependency problems, granularity of privacy (file, class, function), and the cost of loading code that is never used. Which design choices does Python's module system get right, and where does it show its age?

---

#### Further Reading

- **Python import system documentation** — https://docs.python.org/3/reference/import.html : the authoritative description of finders, loaders, and `sys.modules`
- **PEP 328** — Imports: Multi-Line and Absolute/Relative: the rationale for Python's relative import syntax
- **PEP 302** — New Import Hooks: how to plug custom loaders into the import machinery
- **"Node.js module system"** — MDN/Node.js docs: CommonJS (`require`) vs ES Modules (`import`), and why the two coexist uneasily
- **PLAI Chapter 10** — Krishnamurthi: Recursion and Modules — a language-theoretic treatment of modules as first-class values
- **"Modular Programming with Python"** — Erik Westra: practical patterns for large Python codebases
