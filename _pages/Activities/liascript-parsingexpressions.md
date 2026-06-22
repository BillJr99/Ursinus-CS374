# Parsing Expressions: Left Factoring, Precedence, and Iteration
<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://github.com/BillJr99/Ursinus-CS374-Fall2026/blob/gh-pages/_pages/Activities/liascript-parsingexpressions.md or locally via https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374-Fall2026/gh-pages/_pages/Activities/liascript-parsingexpressions.md

import: https://raw.githubusercontent.com/liascript/CodeRunner/master/README.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

# Parsing Expressions: Left Factoring, Precedence, and Iteration

Expression parsing is the most common and most tricky part of building any language: without deliberate grammar design, `2 + 3 * 4` can parse as `(2 + 3) * 4 = 20` instead of the correct `2 + (3 * 4) = 14`. The solution — a layered grammar where each precedence level is its own rule — is elegant, but turning that grammar into a top-down parser requires eliminating left recursion, which this module does systematically. Two complementary strategies (recursive descent with tiered functions, and Pratt parsing with numeric binding powers) solve exactly the same problem; understanding both gives you the vocabulary to handle any operator grammar you will encounter in your career.

## Learning Goals

By the end of this activity, you will be able to:

- Rewrite a left-recursive expression grammar into an equivalent iterative (loop) form suitable for recursive descent
- Implement a multi-tier expression parser that enforces operator precedence through the depth of the parsing function chain
- Trace the left-fold accumulation loop and predict the AST it produces for a given sequence of same-precedence operators
- Explain why left-folding (rather than right-folding) is required for left-associative operators such as subtraction and division
- Extend the expression grammar to include unary negation and parenthesized subexpressions, and implement the corresponding parser functions

This two-day module is the heart of your parser: turning the layered expression grammar (the cure for ambiguity) into running code, with explicit, careful attention to the move students find hardest: rewriting left recursion as the iteration pattern `term { (op) term }` and folding the loop's results into a left-leaning structure. We build it slowly, one operator tier at a time, exactly as your assignment will. The arc: **the ladder restated for descent $\rightarrow$ one tier in code $\rightarrow$ chaining operators in the loop $\rightarrow$ the full ladder with parentheses and unary minus**.

> **Before You Begin** — make sure you are comfortable with:
>
> - **Recursive-descent parsing basics**: writing a function per grammar rule, calling `peek()` / `advance()` / `expect()`, and recognizing the shape `rule -> A B C`.
> - **Operator precedence and associativity**: why `*` binds tighter than `+`, why `7 - 2 - 1` means `(7 - 2) - 1` (left-associative) rather than `7 - (2 - 1)`, and how a layered (unambiguous) grammar encodes both properties.
> - **Python dataclasses for AST nodes**: the `@dataclass` decorator, field annotations, and constructing nested node objects — you will use these when the assignment upgrades tuples to typed nodes.

---

## Directions and Group Roles

Work in your POGIL team with rotated roles (**Manager**, **Recorder**, **Presenter**, **Reflector**). Consider each model and question individually first, then discuss with your group. The Recorder posts answers to the Class Activity Questions discussion board; the Presenter reports out areas of disagreement or alternative approaches. After class, respond to the reflective prompt individually in your notebook.

---

# Part I: The Ladder, Descent-Ready (Day 1)

The unambiguous layered grammar you saw earlier used left recursion (`E -> E + T`) to enforce left-associativity — but a recursive descent parser calling itself on the left immediately spirals into infinite recursion. Part I shows the mechanical fix: replace every left-recursive rule with an equivalent `while` loop, and show that the loop's left-fold behavior preserves exactly the same associativity the recursion would have produced.

## 1. From Left Recursion to Loops, Tier by Tier

The unambiguous ladder used left recursion, which descent cannot run. We rewrite **every tier** in the loop form, and the whole grammar becomes:

```
expr   -> addsub
addsub -> muldiv { ("+" | "-") muldiv }
muldiv -> unary  { ("*" | "/") unary }
unary  -> "-" unary | primary
primary-> NUMBER | IDENT | "(" expr ")"
```

Read the shape: each tier parses one item of the *next tighter* tier, then loops over its own operators. Precedence is still the depth of the chain; associativity now lives in **how the loop folds**: if each iteration wraps the running result as the *left* child of a new node, the chain leans left, exactly what `-` and `/` require.

$$
a - b - c \;\Rightarrow\; \texttt{(("-",("-",a,b),c))} \quad \text{left fold, left lean}
$$

> **Watch out!** Left recursion (`addsub -> addsub ("+" | "-") muldiv`) is fatal for top-down parsers: a recursive descent function that begins by calling itself will loop infinitely before consuming a single token. You **must** eliminate it — either by rewriting to the loop form shown above or by using a Pratt parser — before attempting a top-down implementation.

---

## Model 0: Building an Expression Grammar — Step by Step

Before writing any parser code, you need a *correct grammar* to implement. This model builds one from scratch, showing each pitfall and its cure. By the end, you will have the "ladder grammar" your parser implements — and you will understand *why* it has the form it does.

### Step 1 — Naive Grammar (Ambiguous)

Start with the most natural expression grammar:

```
expr → expr "+" expr
      | expr "-" expr
      | expr "*" expr
      | expr "/" expr
      | "(" expr ")"
      | NUMBER
```

This grammar describes the right *language* (all arithmetic expressions), but it is **ambiguous**: the string `2 + 3 * 4` has two parse trees — one where `+` is the root and one where `*` is the root. The grammar says nothing about precedence, so a parser built from it will make arbitrary choices.

### Step 2 — Enforcing Precedence (Hierarchy of Nonterminals)

The fix is to use *separate nonterminals for each precedence level*. Lower-precedence operators go higher in the grammar (closer to `expr`), higher-precedence operators go deeper:

```
expr    → term   { ("+" | "-") term   }     # lowest precedence
term    → factor { ("*" | "/") factor }     # higher precedence
factor  → "-" factor | primary              # unary (right-associative)
primary → NUMBER | "(" expr ")"
```

The `{ ... }` notation (EBNF) means zero or more repetitions. Now `2 + 3 * 4` has only one parse tree: `term` processes `3 * 4` before `expr` processes the `+`, encoding precedence structurally.

### Step 3 — From EBNF to a While Loop

The EBNF `{ ("+" | "-") term }` translates directly into Python:

```python
def parse_expr(lexer):
    node = parse_term(lexer)              # parse first term
    while lexer.peek().type in ("PLUS", "MINUS"):
        op  = lexer.advance().value       # consume the operator
        right = parse_term(lexer)         # parse next term
        node = (op, node, right)          # fold left: build left-leaning tree
    return node
```

This is **left-associative by construction**: the existing `node` always becomes the *left* child of the new `BinOp`, so `7 - 2 - 1` parses as `(7 - 2) - 1` (correct) rather than `7 - (2 - 1)` (wrong).

### Step 4 — Why Not Left-Recursive Rules?

A natural alternative is a left-recursive grammar rule:

```
expr → expr "+" term | term       # left-recursive
```

This encodes left-associativity in the grammar itself. But a recursive-descent parser would loop forever on this rule: `parse_expr` would immediately call `parse_expr` again without consuming any input. **Left-recursive grammars cannot be parsed by LL(k) parsers.** The while-loop pattern is the LL equivalent — it produces the same *tree shape* without the infinite loop.

> **Watch out!** Left recursion and left associativity are different things. Left recursion is a property of a grammar rule; left associativity is a property of the *tree* that rule produces. The while-loop pattern achieves left associativity without left recursion.

### Step 5 — The Final EBNF Grammar

```ebnf
program  → statement* EOF
statement→ "let" IDENT "=" expr ";"
          | "print" expr ";"
          | "while" "(" expr ")" "{" statement* "}"
          | "if" "(" expr ")" "{" statement* "}" [ "else" "{" statement* "}" ]
          | IDENT "=" expr ";"
expr     → term   { ("+" | "-") term   }
term     → factor { ("*" | "/") factor }
factor   → "-" factor | primary
primary  → NUMBER | FLOAT | STRING | "true" | "false"
          | IDENT | "(" expr ")"
```

Every `{ ... }` in the EBNF becomes a `while` loop; every `[ ... ]` becomes an `if`; every `|` in a rule becomes an `if/elif` chain. The grammar *is* the code.

```python
# Demonstration: the while-loop pattern produces left-associative trees.
# We use tuples (op, left, right) as lightweight AST nodes.

def lex(src):
    """Minimal tokenizer: returns list of (type, value) pairs."""
    import re
    tokens = []
    for m in re.finditer(r'\d+(\.\d+)?|[+\-*/()]|\S+', src):
        s = m.group()
        if re.fullmatch(r'\d+', s):       tokens.append(('NUM', s))
        elif re.fullmatch(r'\d+\.\d+', s): tokens.append(('NUM', s))
        elif s in '+-*/()':               tokens.append((s, s))
        else:                              tokens.append(('IDENT', s))
    tokens.append(('EOF', ''))
    return tokens

class Parser:
    def __init__(self, src):
        self.tokens = lex(src)
        self.pos = 0

    def peek(self):
        return self.tokens[self.pos]

    def advance(self):
        tok = self.tokens[self.pos]
        self.pos += 1
        return tok

    def parse_expr(self):
        node = self.parse_term()
        while self.peek()[0] in ('+', '-'):
            op = self.advance()[1]
            right = self.parse_term()
            node = (op, node, right)   # left fold
        return node

    def parse_term(self):
        node = self.parse_primary()
        while self.peek()[0] in ('*', '/'):
            op = self.advance()[1]
            right = self.parse_primary()
            node = (op, node, right)   # left fold
        return node

    def parse_primary(self):
        tok = self.peek()
        if tok[0] == '(':
            self.advance()             # consume '('
            node = self.parse_expr()
            self.advance()             # consume ')'
            return node
        return ('NUM', self.advance()[1])

def show_tree(node, indent=0):
    prefix = "  " * indent
    if isinstance(node, tuple) and len(node) == 3:
        print(f"{prefix}({node[0]})")
        show_tree(node[1], indent+1)
        show_tree(node[2], indent+1)
    else:
        print(f"{prefix}{node[1]}")

expressions = ["2 + 3 * 4", "(2 + 3) * 4", "7 - 2 - 1", "1 + 2 + 3 + 4"]
for src in expressions:
    tree = Parser(src).parse_expr()
    print(f"=== {src} ===")
    show_tree(tree)
    print()
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

### Critical Thinking Questions

**CTQ 0.1** Run the parser on `7 - 2 - 1`. The tree should be `(-, (-, 7, 2), 1)`, which evaluates to `4`. If the tree were `(-, 7, (-, 2, 1))` instead, what value would it produce? Which is "correct" for subtraction, and what does this tell you about the importance of left-associativity?

**CTQ 0.2** The grammar has `factor → "-" factor` (unary minus, right-recursive). This rule *is* right-recursive, but it doesn't cause infinite loops in a recursive-descent parser. Why not?

**CTQ 0.3** Add a `parse_factor` method that handles unary negation: if the current token is `-`, consume it and recursively call `parse_factor`; otherwise call `parse_primary`. Test on `-3`, `--3`, and `-(2 + 3)`.

---

## Model 1: Trace the Loop

This model asks you to simulate the `parse_addsub` loop by hand so you can see exactly where associativity comes from. The key insight is that the running `node` variable acts as a left-accumulator: each new operator wraps the *accumulated result so far* as its left child, producing a left-leaning tree. Changing which side receives the accumulator changes associativity — and therefore the numeric result.

Consider `addsub` parsing the token stream for `7 - 2 - 1`.

### Critical Thinking Questions

1. Walk the loop by hand: what does the first `parse_muldiv()` return; what happens on each `while` iteration; what is the running `node` after each? The Recorder draws the tree growing.
2. Suppose the loop body instead wrapped the new operand as the left child and the running result as the right. What tree, and what wrong value, results for `7 - 2 - 1`? You have just located associativity in a single line of code.
3. Why does the loop in `addsub` test for `+` *or* `-` while leaving `*` to a different function entirely? Connect to the depth-equals-precedence principle.

---

## Code Cell

```python
# The expression parser, one tier at a time, designed to drop into the
# Parser class from the recursive descent module. Tuples for now; the AST
# module upgrades them to classes.

def parse_expr(self):
    return self.parse_addsub()

# addsub -> muldiv { ("+" | "-") muldiv }
def parse_addsub(self):
    try:
        node = self.parse_muldiv()
        while self.peek() and self.peek().type in ("PLUS", "MINUS"):
            op = self.advance().lexeme          # consume the operator
            right = self.parse_muldiv()         # parse the next operand
            node = (op, node, right)            # LEFT fold: old node goes left
        return node
    except SyntaxError:
        raise
    except Exception as e:
        print(f"[exprparser:parse_addsub] {e}")
        import traceback; traceback.print_exc()
        raise

# muldiv -> unary { ("*" | "/") unary }
def parse_muldiv(self):
    node = self.parse_unary()
    while self.peek() and self.peek().type in ("STAR", "SLASH"):
        op = self.advance().lexeme
        right = self.parse_unary()
        node = (op, node, right)
    return node

# unary -> "-" unary | primary
def parse_unary(self):
    if self.peek() and self.peek().type == "MINUS":
        self.advance()
        return ("neg", self.parse_unary())
    return self.parse_primary()

# primary -> NUMBER | IDENT | "(" expr ")"
def parse_primary(self):
    tok = self.peek()
    if tok and tok.type == "NUMBER":
        self.advance(); return ("num", float(tok.lexeme))
    if tok and tok.type == "IDENT":
        self.advance(); return ("var", tok.lexeme)
    if tok and tok.type == "LPAREN":
        self.advance()
        node = self.parse_expr()
        self.expect("RPAREN")
        return node
    raise SyntaxError(f"expected an expression, found "
                      f"{tok.lexeme!r} at line {tok.line}" if tok else "end of input")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

---

## Model 2: Precedence Table (Runnable)

Before writing parser code, it helps to see that "precedence" is just a number: a higher number means "bind tighter" (resolve sooner). This model lets you experiment with two different precedence tables on the same token stream so you can observe concretely how changing one number changes the resulting tree — and therefore the numeric result. Pay attention to the flat-precedence case: it is a useful stress-test for understanding what your parser *actually* does rather than what you think it does.

Different precedence assignments for the same token stream produce completely different trees and values. The model below encodes two precedence tables and a simple "what would this mean?" validator that folds a flat token list according to each table, showing both resulting trees.

```python
# Model 2: Two precedence tables, one token stream — two different meanings.
# We use a minimal Pratt-style fold (no full parser) just to show the shape.

PREC_STANDARD = {"+": 1, "-": 1, "*": 2, "/": 2}   # conventional
PREC_FLAT     = {"+": 1, "-": 1, "*": 1, "/": 1}   # all equal (APL-like)

def fold_left(tokens, prec_table):
    """
    Build a left-leaning tree from a flat infix token list
    [num, op, num, op, num, ...] using a simple precedence-climbing fold.
    Returns a nested tuple (op, left, right) or a number leaf.
    """
    try:
        # Convert to list of (value_or_op, is_op) pairs
        nums = []
        ops  = []
        for i, tok in enumerate(tokens):
            if i % 2 == 0:
                nums.append(float(tok))
            else:
                ops.append(tok)

        # Greedily fold higher-precedence operators first (left to right)
        result_nums = list(nums)
        result_ops  = list(ops)
        for current_prec in sorted(set(prec_table.values()), reverse=True):
            i = 0
            while i < len(result_ops):
                op = result_ops[i]
                if prec_table.get(op, 0) == current_prec:
                    node = (op, result_nums[i], result_nums[i+1])
                    result_nums = result_nums[:i] + [node] + result_nums[i+2:]
                    result_ops  = result_ops[:i] + result_ops[i+1:]
                else:
                    i += 1
        return result_nums[0]
    except Exception as e:
        print(f"[prectable:fold_left] {e}")
        import traceback; traceback.print_exc()
        return None

def evaluate(node):
    try:
        if isinstance(node, float):
            return node
        op, l, r = node
        lv, rv = evaluate(l), evaluate(r)
        if op == "+": return lv + rv
        if op == "-": return lv - rv
        if op == "*": return lv * rv
        if op == "/": return lv / rv
    except Exception as e:
        print(f"[prectable:evaluate] {e}")
        import traceback; traceback.print_exc()
        return None

def show(label, prec, tokens):
    tree = fold_left(tokens, prec)
    print(f"{label}:")
    print(f"  tree  = {tree}")
    print(f"  value = {evaluate(tree)}")

tokens = ["2", "+", "3", "*", "4"]
print(f"Token stream: {' '.join(tokens)}")
print()
show("Standard precedence (* > +)", PREC_STANDARD, tokens)
show("Flat precedence   (* = +)", PREC_FLAT,     tokens)

tokens2 = ["6", "-", "2", "-", "1"]
print()
print(f"Token stream: {' '.join(tokens2)}")
print()
show("Standard precedence (left assoc)", PREC_STANDARD, tokens2)
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

### Critical Thinking Questions

4. The standard table gives `2 + 3 * 4 = 14`; the flat table gives `20`. Trace exactly which fold step differs between the two tables for these five tokens.
5. The flat table makes all operators equal in precedence and left-associative. What value does `6 - 2 - 1` produce under flat precedence? Is it the same as under standard precedence? Explain why or why not.
6. APL evaluates all binary operators right-to-left at equal precedence. Modify `PREC_FLAT` to test that claim for `6 - 2 - 1` by changing the fold direction. What value do you expect, and does it match?
7. Annotate the correspondence: which EBNF symbol became the `while` condition, which became `advance()`, which became the recursive call? (This is the translation table earning its keep.)

---

## Model 3: Recursive Descent Expression Parser (Runnable)

This model brings everything together into a working parser you can run. The mutual call chain `parse_expr -> parse_addsub -> parse_muldiv -> parse_unary -> parse_primary -> parse_expr` encodes the entire precedence hierarchy: a function only returns to its caller after fully resolving everything at the current or tighter tiers. Notice how parentheses are handled in `parse_primary` with a single call to `parse_expr` — that one line gives parentheses the power to override every precedence level.

A self-contained recursive descent parser for `+`, `-`, `*`, `/` and parentheses. The mutual recursion `expr → addsub → muldiv → unary → primary → … → expr` gives precedence without any table.

```python
# Model 3: Complete recursive-descent expression parser (stand-alone)
# Tokens are produced by a tiny hand-written tokeniser.

import re

def tokenize(src):
    try:
        token_re = re.compile(
            r'\s*(?:(\d+(?:\.\d+)?)|([+\-*/])|(\()|(\)))')
        tokens = []
        for m in token_re.finditer(src):
            if m.group(1): tokens.append(("NUM",   m.group(1)))
            elif m.group(2): tokens.append(("OP",  m.group(2)))
            elif m.group(3): tokens.append(("LPAREN", "("))
            elif m.group(4): tokens.append(("RPAREN", ")"))
        return tokens
    except Exception as e:
        print(f"[recdescent:tokenize] {e}")
        import traceback; traceback.print_exc()
        return []

class Parser:
    def __init__(self, src):
        self.tokens = tokenize(src)
        self.pos = 0

    def peek(self):
        return self.tokens[self.pos] if self.pos < len(self.tokens) else None

    def advance(self):
        tok = self.tokens[self.pos]; self.pos += 1; return tok

    def expect(self, ttype):
        tok = self.peek()
        if tok and tok[0] == ttype:
            return self.advance()
        raise SyntaxError(f"expected {ttype}, got {tok}")

    # expr -> addsub
    def parse_expr(self):
        return self.parse_addsub()

    # addsub -> muldiv { ("+" | "-") muldiv }
    def parse_addsub(self):
        try:
            node = self.parse_muldiv()
            while self.peek() and self.peek() == ("OP", "+") or \
                  self.peek() and self.peek() == ("OP", "-"):
                op = self.advance()[1]
                node = (op, node, self.parse_muldiv())
            return node
        except SyntaxError: raise
        except Exception as e:
            print(f"[recdescent:parse_addsub] {e}")
            import traceback; traceback.print_exc(); raise

    # muldiv -> unary { ("*" | "/") unary }
    def parse_muldiv(self):
        node = self.parse_unary()
        while self.peek() and self.peek() in (("OP","*"),("OP","/")):
            op = self.advance()[1]
            node = (op, node, self.parse_unary())
        return node

    # unary -> "-" unary | primary
    def parse_unary(self):
        if self.peek() == ("OP", "-"):
            self.advance()
            return ("neg", self.parse_unary())
        return self.parse_primary()

    # primary -> NUMBER | "(" expr ")"
    def parse_primary(self):
        tok = self.peek()
        if tok and tok[0] == "NUM":
            return ("num", float(self.advance()[1]))
        if tok and tok[0] == "LPAREN":
            self.advance()
            node = self.parse_expr()
            self.expect("RPAREN")
            return node
        raise SyntaxError(f"unexpected token {tok}")

def parse(src):
    try:
        p = Parser(src)
        tree = p.parse_expr()
        return tree
    except SyntaxError as e:
        return f"SyntaxError: {e}"

for expr in ["2+3*4", "2*3+4", "(2+3)*4", "7-2-1", "-3*2", "1+2+3+4"]:
    print(f"  {expr!r:18} -> {parse(expr)}")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

### Critical Thinking Questions

8. Trace `2 + 3 * 4` through the parser call by call: list every function invoked in order and what tuple each returns. Confirm that `parse_muldiv` is called *by* `parse_addsub`, so `3 * 4` is resolved before the `+` node is built.
9. `parse_unary` calls itself for `--3`. Is that left recursion? Explain why it terminates here but `E -> E + T` would loop infinitely in a naive recursive descent.
10. `parse_primary`'s parenthesis branch calls `parse_expr`, the top of the chain. Explain why this single call makes parentheses override every precedence level, and identify the matching production in the grammar at the top of this module.

---

## Model 4: Pratt Parsing (Runnable)

Pratt parsing (also called precedence climbing) is an elegant alternative to the tiered-function approach: instead of encoding precedence by the *depth* of a function chain, it encodes it as a *number* (the binding power) and uses a single loop with a numeric comparison to decide whether to keep consuming. The result is exactly the same AST with far less boilerplate — adding a new operator means adding one entry to the `LBP` table, not writing a new function. Both parsers run on the same test cases so you can confirm they agree.

> **Watch out!** Pratt parsing is an elegant alternative that scales gracefully as your language grows, but it is easy to confuse the two binding-power roles. The **left binding power (lbp)** of an operator is how tightly it pulls in a left operand that has already been parsed; the **right binding power** passed to the recursive `expression()` call controls how tightly the operator claims tokens on its right. For left-associative operators these differ by exactly 1 (or you pass `bp` rather than `bp - 1`); for right-associative operators (like `**`) the right call must use `bp - 1` so a subsequent operator at the same level is allowed to win — see Exercise 1 for the concrete example.

A Pratt parser (precedence climbing) associates a *binding power* with each operator and decides whether to consume the next operator based on numeric comparison — no mutual recursion, no separate function per tier. Both parsers should produce the same AST for `2 + 3 * 4 - 1`.

```python
# Model 4: Pratt parser (precedence climbing) and comparison with recursive descent

import re

def tokenize(src):
    try:
        token_re = re.compile(r'\s*(?:(\d+(?:\.\d+)?)|([+\-*/])|(\()|(\)))')
        toks = []
        for m in token_re.finditer(src):
            if   m.group(1): toks.append(("NUM",    m.group(1)))
            elif m.group(2): toks.append(("OP",     m.group(2)))
            elif m.group(3): toks.append(("LPAREN", "("))
            elif m.group(4): toks.append(("RPAREN", ")"))
        return toks
    except Exception as e:
        print(f"[pratt:tokenize] {e}")
        import traceback; traceback.print_exc()
        return []

# Binding powers: left-binding-power (lbp) controls whether the operator
# "pulls in" the subexpression to its right.
LBP = {"+": 10, "-": 10, "*": 20, "/": 20}

class PrattParser:
    def __init__(self, src):
        self.tokens = tokenize(src)
        self.pos = 0

    def peek(self):
        return self.tokens[self.pos] if self.pos < len(self.tokens) else None

    def advance(self):
        tok = self.tokens[self.pos]; self.pos += 1; return tok

    def nud(self, tok):
        """Null denotation: prefix position."""
        try:
            if tok[0] == "NUM":
                return ("num", float(tok[1]))
            if tok[0] == "LPAREN":
                node = self.expression(0)
                # consume RPAREN
                if self.peek() and self.peek()[0] == "RPAREN":
                    self.advance()
                return node
            if tok == ("OP", "-"):
                return ("neg", self.expression(100))
            raise SyntaxError(f"unexpected prefix token {tok}")
        except SyntaxError: raise
        except Exception as e:
            print(f"[pratt:nud] {e}")
            import traceback; traceback.print_exc(); raise

    def led(self, tok, left):
        """Left denotation: infix position."""
        try:
            op  = tok[1]
            bp  = LBP[op]
            right = self.expression(bp)   # same bp → left assoc
            return (op, left, right)
        except Exception as e:
            print(f"[pratt:led] {e}")
            import traceback; traceback.print_exc(); raise

    def expression(self, rbp=0):
        """Parse an expression with right-binding-power floor rbp."""
        try:
            tok  = self.advance()
            left = self.nud(tok)
            while True:
                nxt = self.peek()
                if nxt is None: break
                if nxt[0] == "RPAREN": break
                op_bp = LBP.get(nxt[1], 0)
                if op_bp <= rbp: break
                left = self.led(self.advance(), left)
            return left
        except SyntaxError: raise
        except Exception as e:
            print(f"[pratt:expression] {e}")
            import traceback; traceback.print_exc(); raise

def pratt_parse(src):
    try:
        return PrattParser(src).expression(0)
    except SyntaxError as e:
        return f"SyntaxError: {e}"

# ── Recursive descent (same tokenizer) ──────────────────────────────────
class RDParser:
    def __init__(self, src):
        self.tokens = tokenize(src); self.pos = 0
    def peek(self):
        return self.tokens[self.pos] if self.pos < len(self.tokens) else None
    def advance(self):
        tok = self.tokens[self.pos]; self.pos += 1; return tok
    def parse_expr(self): return self.parse_addsub()
    def parse_addsub(self):
        node = self.parse_muldiv()
        while self.peek() and self.peek() in (("OP","+"),("OP","-")):
            op = self.advance()[1]; node = (op, node, self.parse_muldiv())
        return node
    def parse_muldiv(self):
        node = self.parse_unary()
        while self.peek() and self.peek() in (("OP","*"),("OP","/")):
            op = self.advance()[1]; node = (op, node, self.parse_unary())
        return node
    def parse_unary(self):
        if self.peek() == ("OP", "-"):
            self.advance(); return ("neg", self.parse_unary())
        return self.parse_primary()
    def parse_primary(self):
        tok = self.peek()
        if tok and tok[0] == "NUM": return ("num", float(self.advance()[1]))
        if tok and tok[0] == "LPAREN":
            self.advance(); node = self.parse_expr()
            if self.peek() and self.peek()[0] == "RPAREN": self.advance()
            return node
        raise SyntaxError(f"unexpected {tok}")

def rd_parse(src):
    try:
        return RDParser(src).parse_expr()
    except SyntaxError as e:
        return f"SyntaxError: {e}"

tests = ["2+3*4-1", "2*3+4", "(2+3)*4", "7-2-1"]
print(f"{'Expression':<18} {'Pratt':<35} {'RecDescent'}")
print("-" * 80)
for t in tests:
    pr = pratt_parse(t)
    rd = rd_parse(t)
    match = "==" if pr == rd else "!="
    print(f"{t!r:<18} {str(pr):<35} {match} {rd}")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

### Critical Thinking Questions

11. Both parsers produce identical ASTs for `2 + 3 * 4 - 1`. Now trace just the Pratt parser's `expression` calls for this input: what is the `rbp` argument on each call, and when does the `while` loop stop consuming?
12. In the recursive descent parser, adding a new precedence tier requires a new function. In the Pratt parser, what is the equivalent change? Which approach do you find easier to extend, and why?
13. Change `LBP["+"]` and `LBP["-"]` to `20` (equal to `*` and `/`). Predict what tree `2 + 3 * 4` produces under this change before running. Verify, then explain what "all equal precedence, left associative" means for expression evaluation.

---

# Part II: Stress and Extend (Day 2)

Day 2 consolidates and extends what you built on Day 1. You will first check your conceptual grip with a targeted multiple-choice question, then push the parser into new territory: right-associative operators, comparison tiers, and function-call syntax. These exercises mirror the exact extensions your project language will need, so treat them as early project work rather than isolated drills.

> **Watch out!** Right-associative operators like `**` (exponentiation) cannot be handled by the `while`-loop (left-fold) pattern — that pattern is inherently left-associative. Instead, use the original right-recursive grammar rule `power -> unary [ "^" power ]` (a single optional recursive call, not a loop), which naturally builds a right-leaning tree. In a Pratt parser the equivalent move is to pass `bp - 1` rather than `bp` as the minimum binding power for the right-hand recursive call.

## 2. Owning the Pattern

[[MC]]
In `parse_addsub`, the line `node = (op, node, right)` places the previous result as the left child. Changing nothing else, this single line determines that:
- ( ) Multiplication binds tighter than addition
- (x) Operators at this tier associate left, so `7 - 2 - 1` evaluates as `(7 - 2) - 1`
- ( ) Parentheses are honored
- ( ) The grammar is LL(1)

---

## 3. Exercises

1. *Right-associative tier.* Add exponentiation `^` binding tighter than `*` and associating right. The loop pattern will not give right association; the original right-recursive form `power -> unary [ "^" power ]` will. Implement it, and verify `2 ^ 3 ^ 2` yields the tree for `2 ^ (3 ^ 2)`.
2. *Comparison tier.* Add `< <= > >= == !=` at a tier *looser* than `addsub` (so `a + 1 < b * 2` parses sensibly). Decide and document: should `a < b < c` be legal in your language, and if so, what should it mean? (Python and C disagree; your team must choose for December.)
3. *Torture tests.* Run your full parser on: `-(3 + 4) * -2`, `((1))`, `1 + + 2` (should fail; check the message), and `8 / 4 / 2` (must be 1, not 4, once evaluated). Submit the trees or errors for each.
4. *Function calls.* Extend `primary` so an identifier may be followed by an argument list: `IDENT "(" [ expr { "," expr } ] ")"`. Note which EBNF constructs you used and which code shapes they became. Your project language will thank you.

---

## Reflection Prompt

In your notebook: the hardest conceptual move this week was seeing that a `while` loop and a left-recursive production say the same thing. Write the explanation of that equivalence you wish someone had given you on Monday, in your own words, for a future student.

---

## 4. Further Reading

- Douglas Thain. *Introduction to Compilers and Language Design*, Chapter 4.
- Robert Nystrom. *Crafting Interpreters*, "Parsing Expressions" (online): the same ladder with pictures.
- Vaughan Pratt. "Top Down Operator Precedence" (1973), the elegant alternative your instructor will sketch if time allows.
