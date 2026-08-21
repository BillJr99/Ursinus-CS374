<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://github.com/BillJr99/Ursinus-CS374-Fall2026/blob/gh-pages/_pages/Activities/liascript-parsingexpressions.md or locally via https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374/gh-pages/_pages/Activities/liascript-parsingexpressions.md

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

This session is the heart of your parser: turning the layered expression grammar (the cure for ambiguity) into running code, with explicit, careful attention to the move students find hardest: rewriting left recursion as the iteration pattern `term { (op) term }` and folding the loop's results into a left-leaning structure. We build it slowly, one operator tier at a time, exactly as your assignment will. The arc: **the ladder restated for descent $\rightarrow$ one tier in code $\rightarrow$ chaining operators in the loop $\rightarrow$ the full ladder with parentheses and unary minus**.

> **Before You Begin** — make sure you are comfortable with:
>
> - **Recursive-descent parsing basics** (from the *Recursive Descent Parsing* activity): writing a function per grammar rule, calling `peek()` / `advance()` / `expect()`, and recognizing the shape `rule -> A B C`.
> - **Operator precedence and associativity**: why `*` binds tighter than `+`, why `7 - 2 - 1` means `(7 - 2) - 1` (left-associative) rather than `7 - (2 - 1)`, and how a layered (unambiguous) grammar encodes both properties.
> - **Python dataclasses for AST nodes**: the `@dataclass` decorator, field annotations, and constructing nested node objects — you will use these when the assignment upgrades tuples to typed nodes.

---

## Directions and Group Roles

Work in your POGIL team with rotated roles (**Manager**, **Recorder**, **Presenter**, **Reflector**). Consider each model and question individually first, then discuss with your group. The Recorder posts answers to the Class Activity Questions discussion board; the Presenter reports out areas of disagreement or alternative approaches. After class, respond to the reflective prompt individually in your notebook.

---

# Part I: The Ladder, Descent-Ready

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

## Model 0: The Expression Grammar — Recap and Final Form

Before writing any parser code, you need a *correct grammar* to implement. You built this grammar's ingredients piece by piece in the *Recursive Descent Parsing* activity; the recap box below compresses that construction, and the final ladder grammar your parser implements follows.

> **Recap — from the *Recursive Descent Parsing* activity:**
>
> - A naive rule like `expr -> expr "+" expr | expr "*" expr | NUMBER` describes the right language but is **ambiguous** — it says nothing about precedence.
> - The cure is one nonterminal per precedence level: lower-precedence operators sit closer to `expr`, higher-precedence operators sit deeper in the ladder.
> - Left recursion (`expr -> expr "+" term`) encodes left-associativity but sends a top-down parser into infinite recursion before it consumes a single token; the EBNF repetition `expr -> term { ("+" | "-") term }` says the same thing in a form descent can run.
> - In code, `{ ... }` becomes a `while` loop that **folds left** — the running node always becomes the *left* child of the new node — so `7 - 2 - 1` parses as `(7 - 2) - 1`.
>
> If any bullet feels shaky, review that activity before continuing.

### The Final EBNF Grammar

```ebnf
program  -> statement* EOF
statement-> "let" IDENT "=" expr ";"
          | "print" expr ";"
          | "while" "(" expr ")" "{" statement* "}"
          | "if" "(" expr ")" "{" statement* "}" [ "else" "{" statement* "}" ]
          | IDENT "=" expr ";"
expr     -> term   { ("+" | "-") term   }
term     -> factor { ("*" | "/") factor }
factor   -> "-" factor | primary
primary  -> NUMBER | FLOAT | STRING | "true" | "false"
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

**CTQ 0.2** The grammar has `factor -> "-" factor` (unary minus, right-recursive). This rule *is* right-recursive, but it doesn't cause infinite loops in a recursive-descent parser. Why not?

**CTQ 0.3** Add a `parse_factor` method that handles unary negation: if the current token is `-`, consume it and recursively call `parse_factor`; otherwise call `parse_primary`. Test on `-3`, `--3`, and `-(2 + 3)`.

---

## Model 1: Trace the Loop

This model asks you to simulate the `parse_addsub` loop by hand so you can see exactly where associativity comes from. The key insight is that the running `node` variable acts as a left-accumulator: each new operator wraps the *accumulated result so far* as its left child, producing a left-leaning tree. Changing which side receives the accumulator changes associativity — and therefore the numeric result.

Consider `addsub` parsing the token stream for `7 - 2 - 1`.

### Critical Thinking Questions

1. Walk the loop by hand: what does the first `parse_muldiv()` return; what happens on each `while` iteration; what is the running `node` after each? The Recorder draws the tree growing.
2. Suppose the loop body instead wrapped the new operand as the left child and the running result as the right. What tree, and what wrong value, results for `7 - 2 - 1`? You have just located associativity in a single line of code.
3. Why does the loop in `addsub` test for `+` *or* `-` while leaving `*` to a different function entirely? Connect to the depth-equals-precedence principle.


> The worked answers to this session's models are in the **Answer Key** at the end of this page. Attempt them with your team first.

## Code Cell

```python
# The expression parser, one tier at a time, designed to drop into the
# Parser class from the Recursive Descent Parsing activity. Tuples for now;
# the assignment upgrades them to the typed node classes you met in the
# Abstract Syntax Trees activity.

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

# Part II: Stress and Extend

Part II consolidates and extends what you built in Part I. You will first check your conceptual grip with a targeted multiple-choice question, then meet **Pratt parsing** — a second strategy that encodes precedence as numbers rather than as a chain of functions — and finally push the parser into new territory: right-associative operators, comparison tiers, and function-call syntax. These exercises mirror the exact extensions your project language will need, so treat them as early project work rather than isolated drills.

> **Watch out!** Right-associative operators like `**` (exponentiation) cannot be handled by the `while`-loop (left-fold) pattern — that pattern is inherently left-associative. Instead, use the original right-recursive grammar rule `power -> unary [ "^" power ]` (a single optional recursive call, not a loop), which naturally builds a right-leaning tree. In a Pratt parser the equivalent move is to pass `bp - 1` rather than `bp` as the minimum binding power for the right-hand recursive call.

## 2. Owning the Pattern

In `parse_addsub`, the line `node = (op, node, right)` places the previous result as the left child. Changing nothing else, this single line determines that:

[( )] Multiplication binds tighter than addition
[(X)] Operators at this tier associate left, so `7 - 2 - 1` evaluates as `(7 - 2) - 1`
[( )] Parentheses are honored
[( )] The grammar is LL(1)

---


> **The runnable models for this session are on the tutorial shelf.** The precedence-table generator, a complete recursive-descent expression parser, and Pratt parsing are in [Parser Combinators and Runnable Parsing Models](https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374/gh-pages/_pages/Tutorials/tutorial-parser-combinators.md).

## 3. Exercises

1. *Right-associative tier.* Add exponentiation `^` binding tighter than `*` and associating right. The loop pattern will not give right association; the original right-recursive form `power -> unary [ "^" power ]` will. Implement it, and verify `2 ^ 3 ^ 2` yields the tree for `2 ^ (3 ^ 2)`.
2. *Comparison tier.* Add `< <= > >= == !=` at a tier *looser* than `addsub` (so `a + 1 < b * 2` parses sensibly). Decide and document: should `a < b < c` be legal in your language, and if so, what should it mean? (Python and C disagree; your team must choose for December.)
3. *Torture tests.* Run your full parser on: `-(3 + 4) * -2`, `((1))`, `1 + + 2` (should fail; check the message), and `8 / 4 / 2` (must be 1, not 4, once evaluated). Submit the trees or errors for each.
4. *Function calls.* Extend `primary` so an identifier may be followed by an argument list: `IDENT "(" [ expr { "," expr } ] ")"`. Note which EBNF constructs you used and which code shapes they became. Your project language will thank you.

---

## Reflection Prompt

In your notebook: the hardest conceptual move in this activity was seeing that a `while` loop and a left-recursive production say the same thing. Write the explanation of that equivalence you wish someone had given you at the start, in your own words, for a future student.

---

## 4. Further Reading

- Douglas Thain. *Introduction to Compilers and Language Design*, Chapter 4.
- Robert Nystrom. *Crafting Interpreters*, "Parsing Expressions" (online): the same ladder with pictures.
- Vaughan Pratt. "Top Down Operator Precedence" (1973), the original paper behind Model 4.

---

**Up next:** the *Table-Driven and LR Parsing* activity shows the bottom-up, table-driven alternative that parser generators emit; the tiered expression parser you finished here goes directly into the Parser assignment.

# Answer Key

Work the models above with your team before reading these. Each one answers a Critical Thinking Question the session poses; seeing the answer first turns the exercise into transcription.

### Worked Example: `7 - 2 - 1`, one iteration at a time

Answer CTQ 1 yourself before reading. The column that matters is `node` — watch it become its own left child.

| Point in the loop | `node` (the accumulator) | Tokens left | What just happened |
|---|---|---|---|
| before the loop | `7` | `- 2 - 1` | `parse_muldiv()` returned the bare `7` |
| iteration 1, after wrap | `(- 7 2)` | `- 1` | saw `-`, parsed `2`, wrapped: old `node` became the **left** child |
| iteration 2, after wrap | `(- (- 7 2) 1)` | *(none)* | saw `-`, parsed `1`, wrapped again: the whole subtree became the left child |
| loop exits | `(- (- 7 2) 1)` | - | next token is not `+` or `-` |

The tree, leaning left:

```
        (-)
       /   \
     (-)    1
    /   \
   7     2
```

Evaluated bottom-up: `(7 - 2) = 5`, then `5 - 1 = 4`. Correct.

**CTQ 2, answered.** Swap the two children in the wrap — make the *new* operand the left child and the accumulator the right — and the same tokens build:

```
        (-)
       /   \
      1    (-)
          /   \
         2     7
```

which evaluates as `1 - (2 - 7) = 6`. Wrong. Not a parse error, not a crash — a silently wrong number, from a one-line change in which side receives the accumulator.

That is the point of the model: **associativity is not a property of the `-` operator, it is a property of which side of the wrap the accumulator lands on.** Right-associative operators (`**` in Python, `^` in many languages) are built by *recursing* instead of looping — `parse_pow()` calls itself for the right operand rather than accumulating in a `while` — which puts the growth on the right side of the tree instead of the left.

---

