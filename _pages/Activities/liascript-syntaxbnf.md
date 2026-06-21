# Syntax and BNF/EBNF
<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://github.com/BillJr99/Ursinus-CS374-Fall2026/blob/gh-pages/_pages/Activities/liascript-syntaxbnf.md or locally via https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374-Fall2026/gh-pages/_pages/Activities/liascript-syntaxbnf.md

import: https://raw.githubusercontent.com/liascript/CodeRunner/master/README.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

# Syntax and BNF/EBNF

English describes syntax vaguely; a language definition cannot afford vagueness. Today we learn **Backus-Naur Form (BNF)** and its extended cousin **EBNF**, the notations in which every modern language's syntax is published, and which your parser assignment will translate, rule by rule, into code. The arc: **why formal syntax $\rightarrow$ BNF mechanics $\rightarrow$ EBNF conveniences $\rightarrow$ writing grammars for real constructs**.

---

## Directions and Group Roles

Work in your POGIL team with rotated roles (**Manager**, **Recorder**, **Presenter**, **Reflector**). Consider each model and question individually first, then discuss with your group. The Recorder posts answers to the Class Activity Questions discussion board; the Presenter reports out areas of disagreement or alternative approaches. After class, respond to the reflective prompt individually in your notebook.

---

# Part I: BNF

## 1. The Notation

**A BNF grammar is a set of rewriting rules.** Each rule (a *production*) has the form

$$
\langle \text{nonterminal} \rangle \rightarrow \text{sequence of terminals and nonterminals}
$$

**Terminals** are the actual tokens of the language (`if`, `+`, identifiers); **nonterminals** (in angle brackets or capitalized) are named syntactic categories defined by the rules; one nonterminal is the **start symbol**. Alternatives are separated by `|`. A string belongs to the language exactly when it can be **derived** from the start symbol by repeatedly replacing nonterminals using the rules.

A tiny grammar for signed integers:

```
<signed>  -> <sign> <digits> | <digits>
<sign>    -> + | -
<digits>  -> <digit> | <digit> <digits>
<digit>   -> 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9
```

Note the move that makes BNF powerful: `<digits>` is defined **recursively**, using itself, which is how a finite set of rules describes infinitely many strings. Repetition in BNF *is* recursion.

---

## Model 1: Derive It

Using the grammar above, derive the string `-42`.

### Critical Thinking Questions

1. Write the derivation step by step, one rule application per line, starting from `<signed>`. The Recorder writes the team's agreed sequence.
2. How many derivation steps did `-42` take? Predict the count for `-12345` and state the general formula in terms of the number of digits.
3. Show that `4-2` cannot be derived: which rule would have to fire, and why can it not?
4. Modify the grammar so that a signed number may also be written with no digits after the sign... wait, should it? Decide as a team whether `-` alone should be a signed integer, and notice that you are now doing *language design*.

---

## 2. EBNF: Conveniences, Not New Power

**EBNF adds shorthand for the recursion patterns BNF repeats endlessly.** Braces mean zero-or-more repetition, brackets mean optional, parentheses group:

```
signed  -> [ sign ] digit { digit }
sign    -> "+" | "-"
digit   -> "0" | "1" | "2" | "3" | "4" | "5" | "6" | "7" | "8" | "9"
```

The two notations describe exactly the same languages; EBNF is sugar. The sugar matters to *you* as an implementer: when we write the parser, `{ digit }` becomes a `while` loop and `[ sign ]` becomes an `if`, a translation so mechanical you will perform it in your sleep by October.

[[MC]]
The EBNF fragment `term { ("*" | "/") term }` describes:
- ( ) Exactly one multiplication or division
- ( ) An optional single operator between two terms
- (x) A term followed by zero or more operator-term pairs, such as `a`, `a*b`, or `a*b/c`
- ( ) Nested parenthesized expressions

---

# Part II: Grammars for Real Constructs

## Model 2: Read a Real Rule

Here is a plausible EBNF rule for a programming language's `if` statement:

```
ifstmt -> "if" "(" expr ")" block [ "else" block ]
block  -> "{" { stmt } "}"
```

### Critical Thinking Questions

5. List three concrete statements this grammar accepts and two near-misses it rejects, identifying for each reject the exact point of failure.
6. Does this grammar accept `if (x) { } else { }` (empty blocks)? Point to the symbols that decide.
7. Python uses indentation instead of braces. Which rule above encodes the brace decision, and what would have to change *outside the grammar* (in the lexer) to support indentation? (Foreshadowing: lexers can emit invisible tokens.)

---

## Code Cell

```python  liascript
# A grammar is data. Here is the signed-integer EBNF as a Python structure,
# and a hand-rolled recognizer that follows it: [sign] digit {digit}.

def recognize_signed(s):
    """Return True if s matches: [ sign ] digit { digit }"""
    try:
        i = 0
        if i < len(s) and s[i] in "+-":   # [ sign ]  -> an if
            i += 1
        if i >= len(s) or not s[i].isdigit():   # digit, required
            return False
        i += 1
        while i < len(s) and s[i].isdigit():    # { digit } -> a while
            i += 1
        return i == len(s)
    except Exception as e:
        print(f"[syntaxbnf:recognize_signed] {e}")
        import traceback; traceback.print_exc()
        return False

for test in ["42", "-42", "+7", "4-2", "-", "", "007"]:
    print(f"{test!r:8} -> {recognize_signed(test)}")
```
@LIA.eval(`["main.py"]`, `none`, `python3 main.py`)

---

## Model 3: The Translation Pattern

### Critical Thinking Questions

8. Match each EBNF construct to its code shape in the recognizer: `[ ... ]` became which statement, and `{ ... }` became which? This mapping is the entire secret of recursive descent parsing, six weeks early.
9. `007` is accepted. Is that a grammar bug, a feature, or a question for the language designer? Amend the EBNF to forbid leading zeros (except for `0` itself), then explain what the amendment costs in rule complexity.

---

## Model 4: Grammar as a Python Data Structure

A grammar is just data: a mapping from nonterminal names to lists of alternatives, where each alternative is a list of symbols. Terminals are plain strings; nonterminals are wrapped to distinguish them. The checker below walks a token sequence against an arithmetic-expression grammar and reports whether it is valid.

The grammar for arithmetic expressions:

```
expr   -> term { ("+" | "-") term }
term   -> factor { ("*" | "/") factor }
factor -> NUMBER | "(" expr ")"
```

```python  liascript
# Grammar as a Python dict: each key is a nonterminal, each value is
# a list of alternatives. Each alternative is a list of symbols.
# "t:X" means terminal X; "n:X" means nonterminal X.

GRAMMAR = {
    "expr":   [["n:term", "n:expr_rest"]],
    "expr_rest": [["t:+", "n:term", "n:expr_rest"],
                  ["t:-", "n:term", "n:expr_rest"],
                  []],                          # epsilon (empty)
    "term":   [["n:factor", "n:term_rest"]],
    "term_rest": [["t:*", "n:factor", "n:term_rest"],
                  ["t:/", "n:factor", "n:term_rest"],
                  []],
    "factor": [["t:NUM"], ["t:(", "n:expr", "t:)"]],
}

def parse(tokens, rule, pos):
    """Try to match 'rule' starting at tokens[pos].
    Returns (success, new_pos). Tries each alternative in order."""
    if rule not in GRAMMAR:
        return False, pos
    for alt in GRAMMAR[rule]:
        ok, npos = match_alt(tokens, alt, pos)
        if ok:
            return True, npos
    return False, pos

def match_alt(tokens, alt, pos):
    cur = pos
    for sym in alt:
        if sym.startswith("t:"):
            term = sym[2:]
            if cur >= len(tokens) or tokens[cur] != term:
                return False, pos   # backtrack to original pos
            cur += 1
        elif sym.startswith("n:"):
            ok, cur = parse(tokens, sym[2:], cur)
            if not ok:
                return False, pos
    return True, cur

def check(tokens):
    ok, end = parse(tokens, "expr", 0)
    return ok and end == len(tokens)

test_cases = [
    (["NUM", "+", "NUM"],                   True,  "a + b"),
    (["NUM", "*", "NUM", "+", "NUM"],       True,  "a*b + c"),
    (["(", "NUM", "+", "NUM", ")"],         True,  "(a + b)"),
    (["NUM", "+"],                          False, "a + (missing rhs)"),
    (["*", "NUM"],                          False, "* a (no lhs)"),
    (["NUM", "NUM"],                        False, "a b (no operator)"),
    (["NUM", "+", "NUM", "*", "NUM"],       True,  "a + b*c"),
]

print(f"{'tokens':<35} {'expect':>6}  {'got':>6}  {'pass':>4}")
print("-" * 58)
for tokens, expected, label in test_cases:
    result = check(tokens)
    status = "OK" if result == expected else "FAIL"
    print(f"{label:<35} {str(expected):>6}  {str(result):>6}  {status:>4}")
```
@LIA.eval(`["main.py"]`, `none`, `python3 main.py`)

### Critical Thinking Questions

10. The grammar stores `expr_rest` and `term_rest` as separate rules to encode left-associative repetition without left recursion. Why is left recursion (`expr -> expr "+" term`) a problem for a top-down recognizer like this one? Describe the infinite loop that would occur.
11. `match_alt` returns `(False, pos)` — the *original* position — on failure, not the furthest position reached. Why does restoring the original position matter when there are multiple alternatives?
12. The grammar currently uses token strings like `"NUM"`, `"+"`, `"*"`. Sketch how you would extend this representation to carry actual lexemes (e.g., distinguish integer literal `3` from float `3.14`) without rewriting the entire matching engine.
13. The checker only returns True/False. What would a *parse tree* version return instead, and what would one node of that tree look like as a Python value?

---

## Model 5: BNF vs EBNF — Two Notations, One Language

BNF encodes repetition as *recursion*, which forces an extra nonterminal and two alternatives for every repeated construct. EBNF adds `*` and `+` as sugar. The recognizer below demonstrates that both styles accept exactly the same strings for a comma-separated list grammar.

**BNF version** (repetition via recursion):
```
list     -> item list_tail
list_tail -> "," item list_tail | (empty)
item     -> NUMBER
```

**EBNF version** (repetition via `{ }`):
```
list -> item { "," item }
item -> NUMBER
```

```python  liascript
# Both recognizers operate on a flat list of token strings.
# Tokens are "NUM" for any number, "," for comma.

def bnf_list(tokens):
    """BNF-style: list -> item list_tail"""
    pos = bnf_item(tokens, 0)
    if pos is None:
        return False
    pos = bnf_list_tail(tokens, pos)
    return pos == len(tokens)

def bnf_item(tokens, pos):
    if pos < len(tokens) and tokens[pos] == "NUM":
        return pos + 1
    return None

def bnf_list_tail(tokens, pos):
    """list_tail -> ',' item list_tail | epsilon"""
    if pos < len(tokens) and tokens[pos] == ",":
        pos2 = bnf_item(tokens, pos + 1)
        if pos2 is None:
            return pos          # comma with no following item: stay before comma
        return bnf_list_tail(tokens, pos2)
    return pos                  # epsilon: consume nothing

def ebnf_list(tokens):
    """EBNF-style: list -> item { ',' item }"""
    if not tokens or tokens[0] != "NUM":
        return False
    pos = 1
    while pos < len(tokens):
        if tokens[pos] != ",":
            break
        if pos + 1 >= len(tokens) or tokens[pos + 1] != "NUM":
            break
        pos += 2
    return pos == len(tokens)

test_cases = [
    (["NUM"],                               True,  "single item"),
    (["NUM", ",", "NUM"],                   True,  "two items"),
    (["NUM", ",", "NUM", ",", "NUM"],       True,  "three items"),
    ([],                                    False, "empty"),
    (["NUM", ","],                          False, "trailing comma"),
    ([",", "NUM"],                          False, "leading comma"),
    (["NUM", "NUM"],                        False, "missing comma"),
]

print(f"{'description':<20} {'tokens':<30} {'BNF':>4} {'EBNF':>5} {'agree':>6}")
print("-" * 68)
for tokens, expected, label in test_cases:
    b = bnf_list(tokens)
    e = ebnf_list(tokens)
    agree = "YES" if b == e else "NO"
    tok_str = str(tokens)[:28]
    print(f"{label:<20} {tok_str:<30} {str(b):>4} {str(e):>5} {agree:>6}")
```
@LIA.eval(`["main.py"]`, `none`, `python3 main.py`)

### Critical Thinking Questions

14. Both columns should agree on every row. If they disagree, that is a bug in one recognizer — find it and explain the fix. (They should agree; this question asks you to *verify* equivalence, not just trust it.)
15. The BNF version uses recursion; the EBNF version uses a `while` loop. Which is easier to read, and which maps more directly to the grammar notation? Does the answer change when the grammar has nested repetition?
16. The BNF `list_tail` handles the empty case by returning `pos` unchanged. In a grammar with *two* optional suffixes, what would BNF require that EBNF avoids?

---

## Model 6: FIRST Sets (Preview)

The **FIRST set** of a grammar symbol is the set of terminals that can begin a string derivable from that symbol. Parsers use FIRST sets to decide which rule to apply without backtracking: if the next token is in `FIRST(A)`, try rule A. Computing FIRST sets is a fixed-point algorithm: start with the obvious cases (a terminal's FIRST is itself; an epsilon production contributes epsilon) and iterate until nothing changes.

```python  liascript
# Grammar for arithmetic expressions (token-level, no whitespace).
# We represent each production as a list of symbols.
# "" means epsilon (empty string).

PRODS = {
    "expr":      [["term", "expr_rest"]],
    "expr_rest": [["+", "term", "expr_rest"],
                  ["-", "term", "expr_rest"],
                  [""]],                       # epsilon
    "term":      [["factor", "term_rest"]],
    "term_rest": [["*", "factor", "term_rest"],
                  ["/", "factor", "term_rest"],
                  [""]],
    "factor":    [["NUM"], ["(", "expr", ")"]],
}
NONTERMINALS = set(PRODS.keys())
EPSILON = ""

def compute_first(prods):
    first = {nt: set() for nt in prods}

    def first_of_symbol(sym):
        if sym == EPSILON:
            return {EPSILON}
        if sym not in NONTERMINALS:
            return {sym}          # terminal: FIRST is itself
        return first[sym]

    changed = True
    while changed:
        changed = False
        for nt, alternatives in prods.items():
            for alt in alternatives:
                # Walk alt left-to-right; add FIRST(sym) - {ε}.
                # Continue to next sym only if ε ∈ FIRST(sym).
                add_eps = True
                for sym in alt:
                    contrib = first_of_symbol(sym) - {EPSILON}
                    before = len(first[nt])
                    first[nt] |= contrib
                    if len(first[nt]) > before:
                        changed = True
                    if EPSILON not in first_of_symbol(sym):
                        add_eps = False
                        break
                if add_eps:
                    before = len(first[nt])
                    first[nt].add(EPSILON)
                    if len(first[nt]) > before:
                        changed = True
    return first

first_sets = compute_first(PRODS)

print("FIRST sets for arithmetic expression grammar:")
print()
for nt in ["expr", "expr_rest", "term", "term_rest", "factor"]:
    tokens = sorted(t for t in first_sets[nt] if t != EPSILON)
    has_eps = EPSILON in first_sets[nt]
    eps_str = " + ε" if has_eps else ""
    print(f"  FIRST({nt:<12}) = {{ {', '.join(tokens)} }}{eps_str}")

print()
print("Parser decision table (which rule fires for each lookahead):")
print()
for nt in ["expr", "expr_rest", "term", "term_rest", "factor"]:
    for i, alt in enumerate(PRODS[nt]):
        alt_str = " ".join(alt) if alt != [""] else "ε"
        # Compute FIRST of this alternative
        alt_first = set()
        add_eps = True
        for sym in alt:
            sf = first_sets.get(sym, {sym}) if sym != "" else {EPSILON}
            alt_first |= sf - {EPSILON}
            if EPSILON not in sf:
                add_eps = False
                break
        if add_eps:
            alt_first.add(EPSILON)
        triggers = sorted(t for t in alt_first if t != EPSILON)
        print(f"  {nt} -> {alt_str:<30} fires on: {triggers}")
```
@LIA.eval(`["main.py"]`, `none`, `python3 main.py`)

### Critical Thinking Questions

17. `FIRST(expr)` and `FIRST(term)` should be identical. Explain why: trace the derivation path from `expr` to see which terminals can appear first.
18. `FIRST(expr_rest)` contains `+`, `-`, and `ε`. Why does the presence of `ε` in a FIRST set matter to a parser when `expr_rest` appears in the *middle* of a longer alternative like `["term", "expr_rest"]`?
19. The algorithm iterates until `changed` is False (a fixed-point computation). Construct a tiny grammar where the FIRST set of one nonterminal only becomes complete after *two* iterations, and trace the two rounds.
20. FOLLOW sets (which tokens can come *after* a nonterminal) are needed alongside FIRST sets to build a complete LL(1) parse table. Without computing them, predict: what would `FOLLOW(expr_rest)` contain in this grammar, and why?

---

# Part III: Synthesis and Practice

## 3. Exercises

1. *Phone grammar.* Write EBNF for US phone numbers allowing `610-409-3000`, `(610) 409-3000`, and `6104093000`. Trade with another team and find one string their grammar accepts that yours rejects.
2. *List literal.* Write EBNF for Python-style list literals of integers: `[]`, `[1]`, `[1, 2, 3]`, with no trailing comma. The comma placement is the lesson; expect a false start.
3. *Recognizer extension.* Extend the code cell to recognize your phone-number grammar, preserving the construct-to-code mapping (optional becomes `if`, repetition becomes `while`). Report your test cases and results.
4. *Project seed.* Draft the EBNF for *one* statement form you want in your team's language (a loop, a print, a let-binding). Keep it; these drafts accumulate into your project's grammar.

---

## Reflection Prompt

In your notebook: BNF was introduced in 1959 to define ALGOL and remains in every language manual today. Why do you think this one notation outlived nearly everything else from that era? What property would a replacement need?

---

## 4. Further Reading

- Douglas Thain. *Introduction to Compilers and Language Design*, Chapter 3.
- The Python Language Reference, section 10 (online): the full grammar of Python, in a BNF dialect, now readable to you.
- Backus et al. "Report on the Algorithmic Language ALGOL 60" (1960), where the notation debuted.
