<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://github.com/BillJr99/Ursinus-CS374-Fall2026/blob/gh-pages/_pages/Activities/liascript-syntaxbnf.md or locally via https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374/gh-pages/_pages/Activities/liascript-syntaxbnf.md

import: https://raw.githubusercontent.com/liascript/CodeRunner/master/README.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

# Syntax and BNF/EBNF

Every programming language has rules about what programs are allowed to look like, rules that are too precise to describe in plain English. BNF (Backus-Naur Form) and its extension EBNF are the standard notations for writing those rules down exactly. Think of BNF like a recipe template: it describes the *structure* of a valid dish (a statement, an expression, a declaration) without pinning down the specific ingredients, and from a finite set of such templates you can generate infinitely many valid programs, just as a handful of recipe patterns can describe every possible meal. After judging languages by criteria in *Evaluating Languages*, today you learn the notation those languages are defined in.

## Learning Goals

By the end of this activity, you will be able to:

- Define the components of a BNF grammar (terminals, nonterminals, productions, start symbol) and identify each in a given grammar
- Construct a derivation sequence for a target string using a provided BNF grammar, applying one rule per step
- Translate EBNF shorthand constructs (repetition `{ }`, optional `[ ]`, grouping `( )`) into their equivalent BNF recursive rules
- Write a BNF or EBNF grammar for a simple programming language construct such as an integer literal, an identifier, or an arithmetic expression
- Explain how EBNF constructs map directly to parser implementation patterns (while loop, if statement) in recursive descent

English describes syntax vaguely; a language definition cannot afford vagueness. Today we learn **Backus-Naur Form (BNF)** and its extended cousin **EBNF**, the notations in which every modern language's syntax is published, and which your parser assignment will translate, rule by rule, into code. The arc: **why formal syntax $\rightarrow$ BNF mechanics $\rightarrow$ EBNF conveniences $\rightarrow$ writing grammars for real constructs**.

> **Before You Begin:** This activity assumes you can:
> - Read a Python function definition and identify its parts (name, parameters, body)
> - Understand that programming languages have rules about what is valid syntax
> - Know what a recursive definition is
> If any of these feel shaky, review them first.

---

## Directions and Group Roles

Work in your POGIL team with rotated roles (**Manager**, **Recorder**, **Presenter**, **Reflector**). Consider each model and question individually first, then discuss with your group. The Recorder posts answers to the Class Activity Questions discussion board; the Presenter reports out areas of disagreement or alternative approaches. After class, respond to the reflective prompt individually in your notebook.

---

# Part I: BNF

This part introduces the core BNF notation and gives you practice deriving strings from a grammar by hand. The goal is to internalize the mechanical process of rule application before we add EBNF's conveniences on top.

## 1. The Notation

A grammar rule says "this category of thing can be built from these smaller pieces." You start with one big category (the start symbol) and keep substituting until only concrete tokens remain; that substitution sequence is a derivation. The key insight is that recursion lets a tiny grammar describe an infinite language.

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

> **Watch out!** Beginners often confuse **terminals** and **nonterminals**. Terminals (`0`, `1`, `+`, `-`) are the actual characters that appear in a valid program; you cannot substitute them further. Nonterminals (`<digit>`, `<digits>`, `<signed>`) are placeholders that must eventually be replaced. If you apply a rule to a terminal or forget to replace a nonterminal, your derivation is invalid.

---

## Model 1: Derive It

In this model you practice writing out a derivation step by step, the same mechanical process a parser performs automatically. Each step replaces exactly one nonterminal with one of its alternatives. Work slowly at first; the discipline of one-rule-at-a-time is what makes derivations checkable.

Using the grammar above, derive the string `-42`.

### Critical Thinking Questions

1. Write the derivation step by step, one rule application per line, starting from `<signed>`. The Recorder writes the team's agreed sequence.
2. How many derivation steps did `-42` take? Predict the count for `-12345` and state the general formula in terms of the number of digits.
3. Show that `4-2` cannot be derived: which rule would have to fire, and why can it not?

### Worked Example: deriving `-42`

Do CTQ 1 as a team first. One rule application per line, and the rule used named on the right; that discipline is what makes a derivation checkable by someone else.

```
<signed>
=> <sign> <number>          (used <signed> -> <sign> <number>)
=> - <number>               (used <sign> -> -)
=> - <digit> <number>       (used <number> -> <digit> <number>)
=> - 4 <number>             (used <digit> -> 4)
=> - 4 <digit>              (used <number> -> <digit>)
=> - 4 2                    (used <digit> -> 2)
= -42
```

Six steps. **CTQ 2's formula:** one step for `<signed>`, one for the sign, then for a $d$-digit number you need $d$ applications of a `<number>` rule and $d$ applications of `<digit>`, so $2 + 2d$ steps in total. For `-42` that is $2 + 4 = 6$ yes, and for `-12345` it predicts $2 + 10 = 12$.

**CTQ 3, answered.** `4-2` cannot be derived because the only rule that produces a `-` is `<sign> -> -`, and `<sign>` appears exactly once in `<signed> -> <sign> <number>`, at the very front. There is no production anywhere that puts a `-` *between* digits, so no sequence of rule applications can reach it. This grammar describes signed numerals, not subtraction; the string `4-2` belongs to a different language.
4. Modify the grammar so that a signed number may also be written with no digits after the sign... wait, should it? Decide as a team whether `-` alone should be a signed integer, and notice that you are now doing *language design*.

---

## 2. EBNF: Conveniences, Not New Power

EBNF doesn't make grammars more powerful; every EBNF grammar can be rewritten in plain BNF. What EBNF adds is readability: instead of a recursive rule with two alternatives, you write a loop symbol. More importantly, those symbols map almost one-to-one onto the code you will write when implementing a parser.

> **Watch out!** In BNF and EBNF, the `|` symbol means **alternation** ("or" between two grammar choices); it is *not* the bitwise OR operator you know from Python or C. Writing `"+" | "-"` in a grammar means "either a plus sign or a minus sign," not a bitwise operation on two values.

**EBNF adds shorthand for the recursion patterns BNF repeats endlessly.** Braces mean zero-or-more repetition, brackets mean optional, parentheses group:

```
signed  -> [ sign ] digit { digit }
sign    -> "+" | "-"
digit   -> "0" | "1" | "2" | "3" | "4" | "5" | "6" | "7" | "8" | "9"
```

The two notations describe exactly the same languages; EBNF is sugar. The sugar matters to *you* as an implementer: when we write the parser, `{ digit }` becomes a `while` loop and `[ sign ]` becomes an `if`, a translation so mechanical you will perform it in your sleep by October.

The EBNF fragment `term { ("*" | "/") term }` describes:

[( )] Exactly one multiplication or division
[( )] An optional single operator between two terms
[(X)] A term followed by zero or more operator-term pairs, such as `a`, `a*b`, or `a*b/c`
[( )] Nested parenthesized expressions

---

# Part II: Grammars for Real Constructs

Now that you can read and write basic grammars, this part applies that skill to the kinds of constructs you see in real programming languages. You will also watch a grammar come to life as executable Python code, making the connection between notation and implementation concrete.

## Model 2: Read a Real Rule

Reading a grammar for a construct you already know well (like `if`) is a good way to check your understanding of the notation. As you work through this model, notice how design decisions you take for granted (where braces go, whether `else` is optional) are captured precisely in a single line of grammar.

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

The code cell above shows the EBNF-to-code mapping at work: `[ sign ]` became an `if` statement and `{ digit }` became a `while` loop. This is not a coincidence; it is the systematic translation rule that you will apply throughout the parser project. Every optional construct becomes a conditional; every repeated construct becomes a loop.

### Critical Thinking Questions

8. Match each EBNF construct to its code shape in the recognizer: `[ ... ]` became which statement, and `{ ... }` became which? This mapping is the entire secret of recursive descent parsing, six weeks early.
9. `007` is accepted. Is that a grammar bug, a feature, or a question for the language designer? Amend the EBNF to forbid leading zeros (except for `0` itself), then explain what the amendment costs in rule complexity.

---


> **The runnable version, a grammar as a Python dictionary, is in [Grammar Tooling in Python](https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374/gh-pages/_pages/Tutorials/tutorial-grammars-in-python.md),** alongside the left-recursion detector and derivation tracer that use the same representation.

# Part III: Synthesis and Practice (At Home)

> These two models are at-home reinforcement, not in-class work. Do them before the next session.

## Model 5 (At Home): BNF vs EBNF, Two Notations, One Language

This model makes the equivalence between BNF and EBNF concrete by running both side by side on the same inputs. After this exercise you should be comfortable translating between the two forms, a skill you will need when reading language manuals (which often use BNF) and when writing parsers (where EBNF maps more directly to code).

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

14. Both columns should agree on every row. If they disagree, that is a bug in one recognizer; find it and explain the fix. (They should agree; this question asks you to *verify* equivalence, not just trust it.)
15. The BNF version uses recursion; the EBNF version uses a `while` loop. Which is easier to read, and which maps more directly to the grammar notation? Does the answer change when the grammar has nested repetition?
16. The BNF `list_tail` handles the empty case by returning `pos` unchanged. In a grammar with *two* optional suffixes, what would BNF require that EBNF avoids?

---


## Model 6 (At Home): FIRST Sets (Preview)

So far you have been deriving strings by applying rules manually. A real parser has to make that choice automatically: when it sees the next token, it needs to know which rule to try. FIRST sets are the lookup table that answers that question: given a nonterminal and the next token, which alternative fires? This model gives you an early glimpse of that machinery before it is covered in depth later.

The **FIRST set** of a grammar symbol is the set of terminals that can begin a string derivable from that symbol. Parsers use FIRST sets to decide which rule to apply without backtracking: if the next token is in `FIRST(A)`, try rule A. Computing FIRST sets is a fixed-point algorithm: start with the obvious cases (a terminal's FIRST is itself; an epsilon production contributes epsilon) and iterate until nothing changes.

```python  liascript
{% raw %}
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
{% endraw %}
```
@LIA.eval(`["main.py"]`, `none`, `python3 main.py`)

### Critical Thinking Questions

17. `FIRST(expr)` and `FIRST(term)` should be identical. Explain why: trace the derivation path from `expr` to see which terminals can appear first.
18. `FIRST(expr_rest)` contains `+`, `-`, and `ε`. Why does the presence of `ε` in a FIRST set matter to a parser when `expr_rest` appears in the *middle* of a longer alternative like `["term", "expr_rest"]`?
19. The algorithm iterates until `changed` is False (a fixed-point computation). Construct a tiny grammar where the FIRST set of one nonterminal only becomes complete after *two* iterations, and trace the two rounds.
20. FOLLOW sets (which tokens can come *after* a nonterminal) are needed alongside FIRST sets to build a complete LL(1) parse table. Without computing them, predict: what would `FOLLOW(expr_rest)` contain in this grammar, and why?

---


The exercises below ask you to write grammars from scratch, which is harder than reading them. Start by listing a few example strings the grammar should accept, then figure out what rule structure generates all of them. The final exercise seeds your project grammar; keep what you write.

## 3. Exercises

1. *Phone grammar.* Write EBNF for US phone numbers allowing `610-409-3000`, `(610) 409-3000`, and `6104093000`. Trade with another team and find one string their grammar accepts that yours rejects.
2. *List literal.* Write EBNF for Python-style list literals of integers: `[]`, `[1]`, `[1, 2, 3]`, with no trailing comma. The comma placement is the lesson; expect a false start.
3. *Recognizer extension.* Extend the code cell to recognize your phone-number grammar, preserving the construct-to-code mapping (optional becomes `if`, repetition becomes `while`). Report your test cases and results.
4. *Project seed.* Draft the EBNF for *one* statement form you want in your team's language (a loop, a print, a let-binding). Keep it; these drafts accumulate into your project's grammar.

---

## Practice (At Home): Allison, Ch. 4: Hand-Traced Grammar Recognition

These exercises build confidence in the mapping between notation and code by writing small recognizer functions from grammar rules and tracing them on sample inputs. They directly support the *Recursive Descent Parsing* activity and the Parser assignment.

> *Exercises adapted from topics covered in *Foundations of Computing* by Chuck Allison (Fresh Sources, Inc.), used under the [MIT License](https://github.com/chuckallison/foundations-of-computing/blob/main/LICENSE).*

In a recognizer function for `IDENT "=" expr`, if the input is `x = 2 + 3`, which of the following matches?

[( )] The entire string is one IDENT
[(X)] IDENT matches `x`, literal `=` matches `=`, IDENT for `expr` would attempt to match `2` (and fail because `2` is not an identifier)
[( )] The rule accepts any input as long as the characters `=` appears somewhere
[( )] IDENT, `=`, and expr all must match *exactly once* each, in any order

For the grammar rule `expr -> term { ('+' | '-') term }`, the { ... } repetition becomes a `while` loop in code. The loop continues as long as:

[( )] There are more tokens
[(X)] The next token is `+` or `-` (i.e., matches one of the alternatives inside the braces)
[( )] The parser has consumed at least one term
[( )] End of input is not reached

1. **Write a recognizer from a grammar rule.**
   Grammar: `identifier -> LETTER { LETTER | DIGIT | '_' }`
   Write a Python function `recognize_identifier(tokens, pos)` that:
   - Checks if `tokens[pos]` is a LETTER
   - Loops while `tokens[pos+i]` is a LETTER, DIGIT, or underscore
   - Returns the position after the last valid character (or None if the first character is not a LETTER)
   
   Test: `recognize_identifier(['x','1','2','_'], 0)` should return 4 (consumed all).
   Test: `recognize_identifier(['1','2','x'], 0)` should return None (first token not a LETTER).

2. **Trace a recognizer on input.**
   Grammar: `list -> INT { ',' INT }`
   Function (provided):
   ```python
   def recognize_list(tokens, pos):
       if pos >= len(tokens) or tokens[pos] != 'INT':
           return None
       pos += 1
       while pos < len(tokens) and tokens[pos] == ',':
           if pos + 1 >= len(tokens) or tokens[pos + 1] != 'INT':
               return pos   # trailing comma error: stop here
           pos += 2
       return pos
   ```
   
   Trace on input `['INT', ',', 'INT', ',', 'INT']`:
   - Initial: `pos = 0`, first token is INT -> advance to `pos = 1`
   - Loop iteration 1: token at `pos=1` is `,` -> advance to `pos=2`, check `pos+1=3` is INT -> advance to `pos=3`
   - Loop iteration 2: token at `pos=3` is `,` -> advance to `pos=4`, check `pos+1=5` is beyond bounds -> return 4
   - Result: recognizer returns 4, but there are 5 tokens. Explain: why does it stop early?

3. **Implement optional groups.**
   Grammar: `declaration -> 'let' IDENT [ '=' expr ]` (where `[ ]` means optional)
   
   Write `recognize_declaration(tokens, pos)` that:
   - Expects `let` at current position
   - Expects IDENT next
   - Checks if the next token is `=`; if yes, expects an expr after it; if no, stops (expr is optional)
   
   Test on: `['let', 'x']` (should return 2, no `=` found)
   Test on: `['let', 'x', '=', 'INT']` (should return 4, `=` and expr found)

4. **Precedence via rule nesting.**
   Grammar:
   ```
   expr -> term { '+' term }
   term -> factor { '*' factor }
   factor -> INT | '(' expr ')'
   ```
   
   Write all three recognizer functions. Trace on input `['INT', '+', 'INT', '*', 'INT']`:
   - Call `recognize_expr` at position 0
   - Inside: calls `recognize_term` -> calls `recognize_factor` -> consumes INT at 0 -> returns 1
   - Loop in expr: token at 1 is `+` -> loop body calls `recognize_term` again -> which eventually consumes tokens 2-4 (INT * INT)
   - Final result: which function recognized the entire input, and did the tree reflect correct precedence (multiplication before addition)?

5. **Error position reporting.**
   Grammar: `statement -> 'print' expr ';'`
   
   Function:
   ```python
   def recognize_statement(tokens, pos):
       if pos >= len(tokens) or tokens[pos] != 'print':
           return (None, pos)
       pos += 1
       new_pos = recognize_expr(tokens, pos)
       if new_pos is None:
           return (None, pos)   # error: return position where expr failed
       if new_pos >= len(tokens) or tokens[new_pos] != ';':
           return (None, new_pos)  # error: return position where semicolon missing
       return (new_pos + 1, None)
   ```
   
   Input: `['print', 'IDENT', 'PLUS']` (missing semicolon)
   Trace: why does the function return `(None, 3)` rather than `(None, 2)`? How would you improve the error message to say "expected `;` at position 3" rather than just returning position 3?

---

## Reflection Prompt

In your notebook: BNF was introduced in 1959 to define ALGOL and remains in every language manual today. Why do you think this one notation outlived nearly everything else from that era? What property would a replacement need?

---

## 4. Further Reading

- Douglas Thain. *Introduction to Compilers and Language Design*, Chapter 3.
- The Python Language Reference, section 10 (online): the full grammar of Python, in a BNF dialect, now readable to you.
- Backus et al. "Report on the Algorithmic Language ALGOL 60" (1960), where the notation debuted.

---

Up next: the *Grammars and the Chomsky Hierarchy* activity places BNF in its theoretical home, and these grammar-writing skills feed directly into the Parser assignment.
