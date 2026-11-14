<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374-Fall2026/gh-pages/_pages/Activities/liascript-parsingexpressions.md or locally via https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374-Fall2026/gh-pages/_pages/Activities/liascript-parsingexpressions.md

import: https://raw.githubusercontent.com/liascript/CodeRunner/master/README.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

# Parsing Expressions, Part 1: Left Factoring and Precedence

Expression parsing is the most common and the trickiest part of building a language.  Without a deliberate grammar, `2 + 3 * 4` can parse as `(2 + 3) * 4 = 20` instead of the correct `2 + (3 * 4) = 14`.  The fix is a layered grammar: each precedence level gets its own rule.  A top-down parser cannot run that grammar until you remove its left recursion, and this activity shows you how, one tier at a time.  The title names two separate grammar rewrites that prepare a grammar for top-down parsing: left factoring pulls a shared prefix out of competing alternatives, and left-recursion removal turns a rule that calls itself first into a loop.  Left-recursion removal is the one you need today.  You will see two top-down strategies that solve the same problem: recursive descent with one function per tier, and Pratt parsing with numeric binding powers.

Next session turns the parse upside down, with *Parsing, Part 2*: the same grammar driven bottom-up from a table.

## Learning Goals

By the end of this activity, you will be able to:

- Rewrite a left-recursive expression grammar into an equivalent loop form that recursive descent can run
- Implement a multi-tier expression parser whose chain of functions enforces operator precedence
- Trace the left-fold accumulation loop and predict the abstract syntax tree (AST) it builds for a run of same-precedence operators
- Explain why left-associative operators such as subtraction and division need a left fold rather than a right fold
- Extend the grammar with unary negation and parenthesized subexpressions, and write the matching parser functions
- Encode the same precedence ladder as a table of binding powers, and explain how a single `+ 1` decides associativity

> **Before You Begin**, make sure you are comfortable with:
>
> - Recursive-descent parsing basics (from the *Recursive Descent Parsing* activity): writing one function per grammar rule, calling `peek()` / `advance()` / `expect()`, and recognizing the shape of a grammar rule in code
> - Operator precedence and associativity.  Precedence says which operator binds tighter, so `*` wins over `+`.  Associativity says how a run of equal operators groups, so `7 - 2 - 1` means `(7 - 2) - 1`.
> - Reading and writing grammars in BNF (Backus-Naur Form), including how `|` separates alternatives and how nonterminals recursively expand.
> - Python dataclasses for AST nodes: the `@dataclass` decorator, field annotations, and constructing nested node objects.

---

## Directions and Group Roles

Work in your POGIL team with your rotated roles (**Manager**, **Recorder**, **Presenter**, **Reflector**).  Think each model and question through on your own first, then talk it over with your group.

---

## How Today Runs

| Segment | What your team does |
|---------|---------------------|
| Roles and the problem | Rotate roles; the Manager writes `2 + 3 * 4` on the board with its two possible trees, and the team agrees on which one is correct and why |
| Part I: The Ladder, Descent-Ready | Run Model 0, answer CTQs 0.1-0.3, then walk `7 - 2 - 1` through the loop by hand in Model 1 and locate associativity in one line of code |
| Part II: Stress and Extend | Answer the associativity check, trace binding powers by hand, run Model 2, and answer CTQs 2.1-2.2 |

---

# Part I: The Ladder, Descent-Ready

The unambiguous layered grammar you saw earlier used left recursion (`E -> E + T`) to force left-associativity.  A recursive descent function for that rule begins by calling itself, so it never consumes a token and never stops.  Part I gives you the mechanical fix.  Replace every left-recursive rule with an equivalent `while` loop, then check that the loop folds left and so keeps the associativity the recursion would have produced.

## 1.  From Left Recursion to Loops, Tier by Tier

Rewrite every tier in loop form and the whole grammar becomes:

```
expr   -> addsub
addsub -> muldiv { ("+" | "-") muldiv }
muldiv -> unary  { ("*" | "/") unary }
unary  -> "-" unary | primary
primary-> NUMBER | IDENT | "(" expr ")"
```

Read the shape.  Each tier parses one item of the next tighter tier, then loops over its own operators.  Precedence is still the depth of the chain.  Associativity now lives in **how the loop folds**: each iteration wraps the running result as the left child of a new node, so the chain leans left, which is exactly what `-` and `/` require.

$$
a - b - c \;\Rightarrow\; \texttt{(("-",("-",a,b),c))} \quad \text{left fold, left lean}
$$

> **Watch out!**  Left recursion (`addsub -> addsub ("+" | "-") muldiv`) is fatal for top-down parsers.  A recursive descent function that begins by calling itself loops forever before it consumes a single token.  Remove it before you attempt a top-down implementation, either by rewriting to the loop form above or by using a Pratt parser.

---

## Model 0: The Expression Grammar, Recap and Final Form

You need a correct grammar before you write any parser code.  You built this grammar piece by piece in the *Recursive Descent Parsing* activity.  The recap box compresses that construction, and the final ladder grammar your parser implements follows it.

> **Recap, from the *Recursive Descent Parsing* activity:**
>
> - A naive rule like `expr -> expr "+" expr | expr "*" expr | NUMBER` describes the right language but is ambiguous: it says nothing about precedence.
> - The cure is one nonterminal per precedence level.  Lower-precedence operators sit closer to `expr`; higher-precedence operators sit deeper in the ladder.
> - Left recursion (`expr -> expr "+" term`) encodes left-associativity but sends a top-down parser into infinite recursion before it consumes a single token.  The EBNF (Extended Backus-Naur Form) repetition `expr -> term { ("+" | "-") term }` says the same thing in a form descent can run.
> - In code, `{ ... }` becomes a `while` loop that folds left: the running node always becomes the left child of the new node, so `7 - 2 - 1` parses as `(7 - 2) - 1`.
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

Every `{ ... }` in the EBNF becomes a `while` loop.  Every `[ ... ]` becomes an `if`.  Every `|` in a rule becomes an `if/elif` chain.  The grammar is the code.

The demonstration below implements the `expr` and `term` tiers with tuples `(op, left, right)` as lightweight AST nodes.  Run it and compare each printed tree with the grammar.

<!-- run: id=cs374-liascript-parsingexpressions-1 viz=env -->
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
@LIA.eval(`["main.py"]`, `none`, `python3 main.py`)
[Visualize this example](https://billjr99.github.io/Ursinus-CS374-Fall2026/viz/#cs374-liascript-parsingexpressions-1) <!-- code-viz link -->

### Critical Thinking Questions

**CTQ 0.1** Run the parser on `7 - 2 - 1`.  The tree should be `(-, (-, 7, 2), 1)`, which evaluates to `4`.  If the tree were `(-, 7, (-, 2, 1))` instead, what value would it produce?  Which tree is correct for subtraction, and what does this tell you about why left-associativity matters?

**CTQ 0.2** The grammar has `factor -> "-" factor` (unary minus).  This rule is right-recursive, and it does not cause infinite loops in a recursive-descent parser.  Why not?

**CTQ 0.3** Add a `parse_factor` method that handles unary negation.  If the current token is `-`, consume it and recursively call `parse_factor`; otherwise call `parse_primary`.  Test on `-3`, `--3`, and `-(2 + 3)`.

---

## Model 1: Trace the Loop

In this model you simulate the `parse_addsub` loop by hand (the loop is in the Code Cell below) so you can see exactly where associativity comes from.  The running `node` variable is a left accumulator.  Each new operator wraps the result so far as its left child, so the tree leans left.  Change which side receives the accumulator and you change the associativity, and with it the numeric result.

Consider `addsub` parsing the token stream for `7 - 2 - 1`.

### Critical Thinking Questions

**CTQ 1.1** Walk the loop by hand.  What does the first `parse_muldiv()` return?  What happens on each `while` iteration?  What is the running `node` after each one?  The Recorder draws the tree as it grows.

**CTQ 1.2** Suppose the loop body instead wrapped the new operand as the left child and the running result as the right.  What tree, and what wrong value, results for `7 - 2 - 1`?  You have just located associativity in a single line of code.

**CTQ 1.3** Why does the loop in `addsub` test for `+` or `-` while leaving `*` to a different function entirely?  Connect this to the depth-equals-precedence principle.

> The worked answers to this session's models are in the **Answer Key** at the end of this page.  Attempt them with your team first.

## Code Cell

<!-- run: id=cs374-liascript-parsingexpressions-2 viz=env -->
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
@LIA.eval(`["main.py"]`, `none`, `python3 main.py`)
[Visualize this example](https://billjr99.github.io/Ursinus-CS374-Fall2026/viz/#cs374-liascript-parsingexpressions-2) <!-- code-viz link -->

---

# Part II: Stress and Extend

Part II checks and extends what you built in Part I.  First you answer one multiple-choice question about the fold.  Then you meet Pratt parsing, a second strategy that encodes precedence as numbers rather than as a chain of functions.  Finally you push the parser further: right-associative operators, comparison tiers, and function-call syntax.  Your project language will need these same extensions, so treat the exercises as early project work rather than as isolated drills.

> **Watch out!**  The `while`-loop (left-fold) pattern cannot handle right-associative operators like `**` (exponentiation), because that pattern always folds left.  Use the original right-recursive rule `power -> unary [ "^" power ]` instead.  It makes one optional recursive call, not a loop, so it builds a right-leaning tree.  In a Pratt parser the equivalent move is to pass `bp` rather than `bp + 1` as the minimum binding power for the right-hand recursive call, as Model 2 below shows.

## 2.  One Line Decides Associativity

In `parse_addsub`, the line `node = (op, node, right)` places the previous result as the left child.  Changing nothing else, this single line determines that:

[( )] Multiplication binds tighter than addition
[(X)] Operators at this tier associate left, so `7 - 2 - 1` evaluates as `(7 - 2) - 1`
[( )] Parentheses are honored
[( )] The grammar is LL(1)

---

## 3.  Theory: The Ladder Does Not Scale

The ladder works, and its cost is easy to count.  Every precedence level is one function.  Every one of those functions calls down to the next even when the input has nothing to do with that level.  Parsing the single token `5` in the Part I grammar still walks `expr -> addsub -> muldiv -> unary -> primary`: five functions on the stack to reach one number.

C has fifteen precedence levels.  As a ladder, that is fifteen functions, fifteen stack frames per literal, and fifteen near-identical bodies to keep in sync when you add an operator.  Adding one operator at a new level means writing a new function and editing its two neighbors.

Precedence climbing, and its close relative Pratt parsing (after Vaughan Pratt's 1973 paper), replace the chain of functions with a number.  Each operator gets a **binding power**: a number that says how tightly it grips its operands.  One loop then reads operators and decides, by comparing numbers alone, whether to keep going or return.  The two were developed independently and organize their code differently (Pratt attaches a parsing function to each token, and precedence climbing loops over a precedence table), but they share the same core loop and build the same trees.  The loop below is that shared core.

The rule is short enough to state completely:

- Parse a left operand.
- While the next token is an operator whose binding power is at least the minimum we were given, consume it and recursively parse its right operand.  Pass a minimum of `bp + 1` for left-associative operators, or `bp` for right-associative ones.
- Fold and repeat.

That `+ 1` is the whole associativity mechanism.  Passing `bp + 1` means the recursive call will not absorb an operator of equal power, so that operator comes back to the loop and folds on the left.  Passing `bp` lets the recursion swallow it, so it folds on the right.

## Examples: Binding Powers, by Hand

Assign binding powers to the ladder from Part I, tightest last:

| Operator | Tier in the ladder | Binding power | Associates |
|----------|-------------------|---------------|------------|
| `+` `-`  | addsub  | 10 | left |
| `*` `/`  | muldiv  | 20 | left |
| `^`      | power   | 30 | **right** |

Now trace `2 + 3 * 4` by hand with a minimum binding power of 0:

1. Parse the left operand: `2`.
2. Next token is `+`, power 10, and 10 >= 0, so consume it.  Recurse for the right operand with a minimum of 11.
3. Inside that call, parse `3`.  Next is `*`, power 20, and 20 >= 11, so consume it and recurse with a minimum of 21.
4. Inside that call, parse `4`.  Next token is end of input, so return `4`.
5. Fold `3 * 4` and return it.  Back in step 2's call, next is end of input, so return.
6. Fold `2 + (3 * 4)`.

Now do `2 * 3 + 4` yourself and find the step where the comparison fails and forces a return.  That failure is precedence, expressed as arithmetic instead of as a call chain.

## Model 2: The Whole Ladder, as a Table

<!-- run: id=cs374-liascript-parsingexpressions-3 viz=env -->
```python
def tokenize(text):
    out, i = [], 0
    while i < len(text):
        c = text[i]
        if c.isspace():
            i += 1
        elif c.isdigit():
            j = i
            while j < len(text) and text[j].isdigit():
                j += 1
            out.append(text[i:j]); i = j
        else:
            out.append(c); i += 1
    return out

# The ENTIRE precedence table. Adding an operator means adding a row.
#   symbol: (binding power, associativity)
BINDING = {
    "+": (10, "left"),
    "-": (10, "left"),
    "*": (20, "left"),
    "/": (20, "left"),
    "^": (30, "right"),
}

def parse_expr(tokens, pos=0, min_bp=0):
    # --- the left operand -------------------------------------------------
    tok = tokens[pos]; pos += 1
    if tok == "(":
        left, pos = parse_expr(tokens, pos, 0)
        assert tokens[pos] == ")", "expected )"
        pos += 1
    elif tok == "-":                       # prefix minus binds very tightly
        operand, pos = parse_expr(tokens, pos, 40)
        left = ("neg", operand)
    else:
        left = tok

    # --- the loop that IS the ladder --------------------------------------
    while pos < len(tokens):
        op = tokens[pos]
        if op not in BINDING:
            break
        bp, assoc = BINDING[op]
        if bp < min_bp:
            break                          # this operator belongs to our caller
        pos += 1
        next_min = bp + 1 if assoc == "left" else bp
        right, pos = parse_expr(tokens, pos, next_min)
        left = (op, left, right)
    return left, pos

def show(node):
    if not isinstance(node, tuple):
        return str(node)
    if node[0] == "neg":
        return f"(-{show(node[1])})"
    op, l, r = node
    return f"({show(l)} {op} {show(r)})"

print("=== One loop, one table, the whole ladder ===")
for src in ["2 + 3 * 4", "2 * 3 + 4", "(2 + 3) * 4",
            "8 - 4 - 2", "2 ^ 3 ^ 2", "2 * 3 ^ 2", "-3 + 4"]:
    tree, pos = parse_expr(tokenize(src))
    print(f"  {src:14} -> {show(tree)}")

print("\n=== The same trees the ladder built ===")
print("  8 - 4 - 2 came out LEFT-leaning  because '-' passes bp + 1")
print("  2 ^ 3 ^ 2 came out RIGHT-leaning because '^' passes bp")
print("  That single '+ 1' is the entire associativity mechanism.")
```
@LIA.eval(`["main.py"]`, `none`, `python3 main.py`)
[Visualize this example](https://billjr99.github.io/Ursinus-CS374-Fall2026/viz/#cs374-liascript-parsingexpressions-3) <!-- code-viz link -->

### Reading the Code

- `BINDING` holds the grammar's precedence structure as data.  Compare it with Part I, where the same information was spread across four function definitions and their call order.
- `if bp < min_bp: break` is precedence.  When `parse_expr` is deep inside a `*` and meets a `+`, the comparison fails and the loop returns.  Whichever caller has a low enough minimum then handles the `+`.  No function per tier is required.
- `next_min = bp + 1 if assoc == "left" else bp` is associativity, in one line.  Trace `8 - 4 - 2`: the recursive call gets minimum 11, sees `-` at power 10, refuses it, and returns, so the outer loop folds left.  For `^` the call gets minimum 30, accepts the next `^`, and folds right.
- Prefix minus is handled before the loop with a high minimum (40).  That is why `-3 + 4` groups as `(-3) + 4` and not `-(3 + 4)`.
- The ladder and this table produce **identical trees**.  They are two encodings of one grammar.  Knowing both lets you choose: the ladder reads more like the grammar, and the table scales to fifteen levels without fifteen functions.

> **Watch out!**  It is tempting to give every operator a distinct binding power so ties never happen.  Do not.  Operators at the same precedence (like `+` and `-`) must share a power, or `8 - 4 + 2` will group wrongly.  Ties are meaningful; the associativity rule exists to resolve them.

### Critical Thinking Questions

> **CTQ 2.1** Trace `2 * 3 + 4` through Model 2 by hand and name the exact comparison that fails and forces a return.  Which line of code is it?

> **CTQ 2.2** `8 - 4 - 2` and `2 ^ 3 ^ 2` differ only in the `+ 1`.  Explain, in terms of what the recursive call is allowed to absorb, why that produces opposite tree shapes.

> **CTQ 2.3** The Part I ladder is five functions; Model 2 is one function plus a five-row table.  For a language with fifteen precedence levels, count each version's cost: functions written, and frames pushed to parse the single literal `5`.

> **CTQ 2.4** Both approaches produce the same trees, so the choice is not about correctness.  State the case for each, and say which your team will use and why.

### Try It Yourself

Add operators to the table without writing a single new function.

<!-- run: id=cs374-liascript-parsingexpressions-4 viz=env -->
```python
def tokenize(text):
    out, i = [], 0
    while i < len(text):
        c = text[i]
        if c.isspace():
            i += 1
        elif c.isdigit():
            j = i
            while j < len(text) and text[j].isdigit():
                j += 1
            out.append(text[i:j]); i = j
        elif text[i:i+2] in ("<=", ">=", "==", "!="):
            out.append(text[i:i+2]); i += 2
        else:
            out.append(c); i += 1
    return out

BINDING = {
    "+": (10, "left"),  "-": (10, "left"),
    "*": (20, "left"),  "/": (20, "left"),
    "^": (30, "right"),
    # TODO 1: add the comparison operators < <= > >= == != at a power
    #         LOOSER than + and - , so that  a + 1 < b * 2  groups as
    #         (a + 1) < (b * 2). What number does that mean?
    #
    # TODO 2: add  &&  and  ||  looser still, with && binding tighter
    #         than ||, so  a || b && c  is  a || (b && c).
}

def parse_expr(tokens, pos=0, min_bp=0):
    tok = tokens[pos]; pos += 1
    if tok == "(":
        left, pos = parse_expr(tokens, pos, 0)
        pos += 1
    elif tok == "-":
        operand, pos = parse_expr(tokens, pos, 40)
        left = ("neg", operand)
    else:
        left = tok
    while pos < len(tokens):
        op = tokens[pos]
        if op not in BINDING:
            break
        bp, assoc = BINDING[op]
        if bp < min_bp:
            break
        pos += 1
        right, pos = parse_expr(tokens, pos, bp + 1 if assoc == "left" else bp)
        left = (op, left, right)
    return left, pos

def show(node):
    if not isinstance(node, tuple):
        return str(node)
    if node[0] == "neg":
        return f"(-{show(node[1])})"
    op, l, r = node
    return f"({show(l)} {op} {show(r)})"

for src in ["1 + 2 * 3", "1 + 2 < 3 * 4", "1 < 2 && 3 < 4 || 5 < 6"]:
    tree, pos = parse_expr(tokenize(src))
    consumed = "all" if pos == len(tokenize(src)) else f"only {pos}"
    print(f"  {src:26} -> {show(tree):34} (consumed {consumed})")

# TODO 3: your language must decide whether  a < b < c  is legal, and if
#         so what it means. Python chains it (a < b and b < c); C parses
#         it as (a < b) < c, comparing a boolean against c. Which does
#         your table produce right now? Write the decision into SEMANTICS.md.
```
@LIA.eval(`["main.py"]`, `none`, `python3 main.py`)
[Visualize this example](https://billjr99.github.io/Ursinus-CS374-Fall2026/viz/#cs374-liascript-parsingexpressions-4) <!-- code-viz link -->

Expected output as written: the first line parses fully, and the other two stop early because the operators they need are not in the table yet.  Add the rows and all three consume everything.  You never wrote a parsing function to do it.  TODO 3 asks about a chained comparison, which is two comparison operators in a row with no parentheses, such as `a < b < c`.  Python reads it as `a < b and b < c`; C reads it as `(a < b) < c`.  Your language has to pick one, or reject the form.

---

---

**In-class work stops here.**  Everything below is homework and going-deeper material.

> **Build your own parser at home.**  Part III, after the Further Reading, is Stage 3 of a step-by-step build that starts in Part VI of the *Abstract Syntax Trees* activity.  It turns the Code Cell in Part I into your own expression ladder, one tier at a time.

---

# Check Your Understanding

In precedence climbing, an operator's binding power encodes:

[(X)] Its precedence: how tightly it grips its operands relative to other operators
[( )] How many tokens of lookahead it needs
[( )] Its position in the token stream
[( )] Whether it is prefix or infix

---

For a left-associative operator the recursive call gets `bp + 1`; for a right-associative one it gets `bp`. The `+ 1` works because:

[(X)] It stops the recursive call absorbing another operator of equal power, so that one returns and folds on the left
[( )] It skips one token
[( )] It increases the operator's precedence by one level
[( )] It prevents infinite recursion

---

`+` and `-` must be given the *same* binding power rather than distinct ones because:

[(X)] They are at one precedence level; distinct powers would make `8 - 4 + 2` group wrongly
[( )] The parser cannot compare unequal numbers
[( )] Otherwise subtraction would become right-associative
[( )] It saves memory in the table

---

The Part I ladder and Model 2's table produce identical trees. The practical difference is:

[(X)] Cost and maintenance: fifteen precedence levels need fifteen functions in a ladder but fifteen table rows and one loop here
[( )] The ladder cannot express right associativity
[( )] The table cannot handle parentheses
[( )] Only the ladder is LL(1)

---

## 3.  Exercises

1.  *Right-associative tier.*  Add exponentiation `^` that binds tighter than `*` and associates right.  The loop pattern will not give right association; the original right-recursive form `power -> unary [ "^" power ]` will.  Implement it, and verify that `2 ^ 3 ^ 2` yields the tree for `2 ^ (3 ^ 2)`.
2.  *Comparison tier.*  Add `< <= > >= == !=` at a tier looser than `addsub`, so that `a + 1 < b * 2` parses sensibly.  Decide and document whether the chained comparison `a < b < c` is legal in your language, and if so, what it means.  Python and C disagree, and your team must choose for December.
3.  *Torture tests.*  Run your full parser on `-(3 + 4) * -2`, `((1))`, `1 + + 2` (this should fail; check the message), and `8 / 4 / 2` (this must be 1, not 4, once evaluated).  Submit the trees or errors for each.
4.  *Function calls.*  Extend `primary` so an identifier may be followed by an argument list: `IDENT "(" [ expr { "," expr } ] ")"`.  Note which EBNF constructs you used and which code shapes they became.  Your project language will thank you.

---

## Reflection Prompt

In your notebook: the hardest conceptual move in the descent half was seeing that a `while` loop and a left-recursive production say the same thing.  Write the explanation of that equivalence you wish someone had given you at the start, in your own words, for a future student.

---

## 4.  Further Reading

- Douglas Thain.  *Introduction to Compilers and Language Design*, Chapter 4, and Chapter 5 for LR parsing.
- Robert Nystrom.  *Crafting Interpreters*, "Parsing Expressions" (online): the same ladder with pictures.
- Vaughan Pratt.  "Top Down Operator Precedence" (1973), the original paper behind Model 2.

---

# Part III: Build It, Stage 3 (at home)

## Build Stage 3: The Ladder in `parser.py`

This part continues the build from Part VI of [Abstract Syntax Trees](https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374-Fall2026/gh-pages/_pages/Activities/liascript-ast.md) and Part IV of [Recursive Descent](https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374-Fall2026/gh-pages/_pages/Activities/liascript-recursivedescent.md).  Finish Build Steps 1 to 22 there first.  When you finish Build Step 32 here, go back to Part VII of Abstract Syntax Trees for the last stage.

As before, each step is one slide, you type the fragment, `____P1____` is a blank answered in the **Answer Key** at the end of this page, and you run each check from inside `cs374-parser/`.

The Code Cell in Part I already has `parse_addsub`, `parse_muldiv`, `parse_unary`, and `parse_primary`.  Your permanent versions keep its logic and its left fold, and they change what Stage 2 changed: functions that take `lexer`, `tok.value` in place of `tok.lexeme`, and nodes with positions in place of tuples.  They also add three tiers above `addsub`, because the language has comparisons and logic:

```text
expr        ::= or_expr
or_expr     ::= and_expr ( OR and_expr )*                     left-fold, LogicOp
and_expr    ::= not_expr ( AND not_expr )*                    left-fold, LogicOp
not_expr    ::= NOT not_expr | comparison                     prefix, UnaryOp
comparison  ::= addsub ( ( LT|LE|GT|GE|EQEQ|NEQ ) addsub )?   does not chain
addsub      ::= muldiv ( ( PLUS | MINUS ) muldiv )*           left-fold, BinOp
muldiv      ::= unary ( ( STAR | SLASH ) unary )*             left-fold, BinOp
unary       ::= MINUS unary | primary
primary     ::= INT | FLOAT | STRING | TRUE | FALSE | IDENT
              | LPAREN expr RPAREN
```

You climb from the bottom, and `parse_expr` moves up one rung each time, so every check runs on a working parser.

---

## Build Step 23: The Rest of the Literals

Stage 2's `parse_primary` knows integers and names.  The remaining literals are short cases, added above the `raise`.  Each one converts the token's text once, here, so that nothing later has to wonder whether `value` is still a string.

```python
# Step 23, parser.py: add above the final raise in parse_primary
    if tok.type == "FLOAT":
        lexer.advance()
        return Num(float(tok.value), tok.line, tok.col)
    if tok.type == "STRING":
        lexer.advance()
        return Str(____P1____, tok.line, tok.col)
    if tok.type in ("TRUE", "FALSE"):
        lexer.advance()
        return BoolLit(____P2____, tok.line, tok.col)
```

This check has quotes and a backslash in its input, so it is easier as a scratch file than as a command line.

```python
# Step 23, try_literals.py
from lexer import Lexer
from parser import parse_expr

for source in ['3.14', r'"a\nb"', 'true', 'false']:
    print(parse_expr(Lexer(source)))
```

**You write:** a test, `test_literals`, above the main block of `test_parser.py`, that asserts the first three of these trees with `==`.  Remember that `r'"a\nb"'` must give `Str("a\nb")`, with a real newline in the value.

Run this check:

```bash
python3 try_literals.py
```

You should see:

```text
Num(value=3.14, line=1, col=1)
Str(value='a\nb', line=1, col=1)
BoolLit(value=True, line=1, col=1)
BoolLit(value=False, line=1, col=1)
```

> **CTQ B23** Your `STRING` token holds both a raw `value` and a `decoded` one.  What would go wrong in `unparse`, in Stage 4, if the node stored the raw one?

---

## Build Step 24: Parentheses and Unary Minus

A parenthesis calls back up to the loosest tier, which is where the *recursive* in recursive descent shows up: inside parentheses, the whole ladder starts over.  The parser returns the inner expression itself and builds no node for the parentheses, because the tree's shape already records the grouping.

```python
# Step 24, parser.py: add above the final raise in parse_primary
    if tok.type == "LPAREN":
        lexer.advance()
        inner = ____P3____
        expect(lexer, "RPAREN")
        return inner
```

```python
# Step 24, parser.py
def parse_unary(lexer: Lexer):
    """Peek for MINUS; consume it and recurse, else fall through to a primary."""
    tok = lexer.peek()
    if tok.type == "MINUS":
        lexer.advance()
        return UnaryOp("-", ____P4____, tok.line, tok.col)
    return parse_primary(lexer)
```

```python
# Step 24, parser.py: replace parse_expr
def parse_expr(lexer: Lexer):
    """Delegate to the highest tier built so far."""
    return parse_unary(lexer)
```

```python
# Step 24, test_parser.py: add above the main block
def test_unary_minus_nests():
    assert expr("--x") == UnaryOp("-", UnaryOp("-", Var("x")))
```

Run this check:

```bash
python3 -c "from parser import parse; print(parse('print --x;').stmts[0].value); print(parse('while (x) { }').stmts[0].condition)"
```

You should see:

```text
UnaryOp(op='-', operand=UnaryOp(op='-', operand=Var(name='x', line=1, col=9), line=1, col=8), line=1, col=7)
Var(name='x', line=1, col=8)
```

> **CTQ B24** CTQ 0.2 asked why `factor -> "-" factor` does not loop forever although it is recursive.  Point to the line in `parse_unary` that answers it.  What does the second line of this output tell you about your prediction in CTQ B19?

---

## Build Step 25: The First Fold

Model 1 traced this loop by hand on `7 - 2 - 1`.  Here it builds real nodes, and each node's position is its operator's position, so a later type error can point at the `/` itself.

```python
# Step 25, parser.py
def parse_muldiv(lexer: Lexer):
    """Parse a unary, then fold left while the next token is STAR or SLASH."""
    left = parse_unary(lexer)
    while lexer.peek().type in ("STAR", "SLASH"):
        op = lexer.advance()
        right = parse_unary(lexer)
        left = ____P5____
    return left
```

```python
# Step 25, test_parser.py: add above the main block
def test_left_associativity_division():
    assert expr("8 / 4 / 2") == BinOp("/", BinOp("/", Num(8), Num(4)), Num(2))
```

**You write:** move `parse_expr` up one rung, so it returns what `parse_muldiv` returns.

Run this check:

```bash
python3 -c "from lexer import Lexer; from parser import parse_expr; print(parse_expr(Lexer('8 / 4 / 2'))); print(parse_expr(Lexer('--x * 3')))"
```

You should see:

```text
BinOp(op='/', left=BinOp(op='/', left=Num(value=8, line=1, col=1), right=Num(value=4, line=1, col=5), line=1, col=3), right=Num(value=2, line=1, col=9), line=1, col=7)
BinOp(op='*', left=UnaryOp(op='-', operand=UnaryOp(op='-', operand=Var(name='x', line=1, col=3), line=1, col=2), line=1, col=1), right=Num(value=3, line=1, col=7), line=1, col=5)
```

> **CTQ B25** Read the positions in the first line of output.  Which `/` has column 7, and which node holds it?  What does that tell you about which operator became the root?

---

## Build Step 26: `addsub`, One Rung Up

The next tier differs from `parse_muldiv` in two things: the operators its loop tests for, and the function its operands come from.  Change only one of them and the ladder skips a rung.

```python
# Step 26, parser.py
def parse_addsub(lexer: Lexer):
    """Parse a muldiv, then fold left while the next token is PLUS or MINUS."""
    left = ____P6____
    while lexer.peek().type in ____P7____:
        op = lexer.advance()
        right = parse_muldiv(lexer)
        left = BinOp(op.value, left, right, op.line, op.col)
    return left
```

**You write:** move `parse_expr` up to `parse_addsub`, and add three tree-shape tests: `2 + 3 * 4` puts the `*` under the `+`, `8 - 3 - 2` nests on the left, and `(2 + 3) * 4` puts the `+` under the `*`.

Run this check:

```bash
python3 -c "from parser import parse; from ast_nodes import pretty; print(pretty(parse('print 2 + 3 * 4;'))); print(pretty(parse('print (2 + 3) * 4;')))"
```

You should see:

```text
Program
  Print
    BinOp(+)
      Num(2)
      BinOp(*)
        Num(3)
        Num(4)
Program
  Print
    BinOp(*)
      BinOp(+)
        Num(2)
        Num(3)
      Num(4)
```

> **CTQ B26** Suppose `parse_addsub` called `parse_unary` instead of `parse_muldiv` for its operands.  What tree would `2 + 3 * 4` give, and what would the parser do at the `*`?

---

## Build Step 27: Comparisons Do Not Chain

A comparison looks like a fold and is not one.  Exercise 2 and the TODO under Model 2 pointed out that Python and C give `a < b < c` different meanings.  This language makes it a syntax error.  Without the second check, the parser stops quietly after `a < b`, and the stray `<` surfaces later as an error that names the wrong problem.

```python
# Step 27, parser.py
COMPARISON_OPS = ("LT", "LE", "GT", "GE", "EQEQ", "NEQ")


def parse_comparison(lexer: Lexer):
    """Parse an addsub; if a comparison operator follows, consume it and one more addsub."""
    left = parse_addsub(lexer)
    ____P8____ lexer.peek().type in COMPARISON_OPS:
        op = lexer.advance()
        left = BinOp(op.value, left, parse_addsub(lexer), op.line, op.col)
        tok = lexer.peek()
        if tok.type in COMPARISON_OPS:
            raise ParseError("one comparison (comparisons do not chain; use parentheses)",
                             tok.type, tok.line, tok.col)
    return left
```

```python
# Step 27, test_parser.py: add above the main block
def test_comparison_does_not_chain():
    err = parse_error("print a < b < c;")
    assert "do not chain" in err.message and err.found == "LT"
```

**You write:** move `parse_expr` up to `parse_comparison`.

Run this check:

```bash
python3 -c "from parser import parse; from check import show_error; print(parse('print a + 1 <= b;').stmts[0].value.op); show_error(parse, 'print a < b < c;'); show_error(parse, 'print (a < b) < c;')"
```

You should see:

```text
<=
ParseError at line 1, col 13: expected one comparison (comparisons do not chain; use parentheses), found LT
no error: Program(stmts=[Print(value=BinOp(op='<', left=BinOp(op='<', left=Var(name='a', line=1, col=8), right=Var(name='b', line=1, col=12), line=1, col=10), right=Var(name='c', line=1, col=17), line=1, col=15), line=1)])
```

> **CTQ B27** The last line says `no error`, although it has the same three names and two `<` tokens.  What is different about the tree it builds?  What must `unparse` do, in Stage 4, to bring that program back?

---

## Build Step 28: `not`

`not` is `parse_unary`'s pattern, moved up the ladder.  It sits above comparison, so `not a < b` means `not (a < b)`, unlike the unary minus, which binds tighter than anything else.  Consuming the `NOT` before the recursive call is what keeps the recursion from running forever.

```python
# Step 28, parser.py
def parse_not(lexer: Lexer):
    """Peek for NOT; consume it and recurse, else fall through to a comparison."""
    tok = lexer.peek()
    if tok.type == "NOT":
        lexer.advance()
        return UnaryOp("not", ____P9____, tok.line, tok.col)
    return ____P10____
```

```python
# Step 28, test_parser.py: add above the main block
def test_not_binds_looser_than_comparison():
    assert expr("not a < b") == UnaryOp("not", BinOp("<", Var("a"), Var("b")))
```

**You write:** move `parse_expr` up to `parse_not`.

Run this check:

```bash
python3 -c "from parser import parse; from ast_nodes import pretty; print(pretty(parse('print not not ok;'))); print(pretty(parse('print not a < b;')))"
```

You should see:

```text
Program
  Print
    UnaryOp(not)
      UnaryOp(not)
        Var(ok)
Program
  Print
    UnaryOp(not)
      BinOp(<)
        Var(a)
        Var(b)
```

> **CTQ B28** A `RecursionError` on `not not ok` means one specific line is in the wrong order.  Which line, and why does that error match what the *Recursive Descent* activity said about left recursion?

---

## Build Step 29: `and`, `or`, and the Top of the Ladder

The last two tiers are left folds again, and they build `LogicOp` rather than `BinOp`.  An evaluator needs `LogicOp`, because `and` and `or` must short-circuit.  `or` is the loosest tier, so this is where `parse_expr` finally stops moving.

```python
# Step 29, parser.py
def parse_and(lexer: Lexer):
    """Parse a not_expr, then fold left while the next token is AND."""
    left = parse_not(lexer)
    while lexer.peek().type == "AND":
        op = lexer.advance()
        left = LogicOp("and", left, parse_not(lexer), op.line, op.col)
    return left
```

```python
# Step 29, parser.py: replace parse_expr
def parse_expr(lexer: Lexer):
    """Delegate to the loosest tier, parse_or."""
    return parse_or(lexer)
```

```python
# Step 29, test_parser.py: add above the main block
def test_or_over_and():
    want = LogicOp("or", Var("a"), LogicOp("and", Var("b"), Var("c")))
    assert expr("a or b and c") == want
```

**You write:** `parse_or`, which folds `parse_and` operands over `OR` tokens.

Run this check:

```bash
python3 -c "from parser import parse; from ast_nodes import pretty; print(pretty(parse('print a or b and not c;')))"
```

You should see:

```text
Program
  Print
    LogicOp(or)
      Var(a)
      LogicOp(and)
        Var(b)
        UnaryOp(not)
          Var(c)
```

> **CTQ B29** Count the calls from `parse_expr` down to `parse_primary` for the single token `42`.  How many functions run, and how many of them build a node?  Connect your answer to the single-child chains that the *Abstract Syntax Trees* activity says an AST collapses.

---

## Build Step 30: An Entry Point for One Expression

`parse` reads programs, and a bare `x + 1` is not one.  A tool such as a REPL may want to read one expression, so `parse_expression` provides that.  It has a job `parse_expr` does not: `parse_expr` stops when its tier runs out of operators and leaves the rest of the input alone, so this function must check that nothing is left over.

```python
# Step 30, parser.py
def parse_expression(source: str):
    """Parse one bare expression; any token left over is a ParseError."""
    lexer = Lexer(source)
    tree = parse_expr(lexer)
    tok = lexer.peek()
    if tok.type != ____P11____:
        raise ParseError("EOF after expression", tok.type, tok.line, tok.col)
    return tree
```

```python
# Step 30, test_parser.py: add at the top
from parser import parse_expression
```

Run this check:

```bash
python3 -c "from lexer import Lexer; from parser import parse_expr, parse_expression; from check import show_error; print(parse_expression('1')); print(parse_expr(Lexer('1 2'))); show_error(parse_expression, '1 2')"
```

You should see:

```text
Num(value=1, line=1, col=1)
Num(value=1, line=1, col=1)
ParseError at line 1, col 3: expected EOF after expression, found INT
```

> **CTQ B30** The second line parsed `1 2` with no complaint.  Why is that correct behavior for `parse_expr` when a `let` statement calls it, and wrong for a REPL?

---

## Build Step 31: The Worked Program

Every piece of a small `while` program now exists, so this check uses all three stages.  The nodes and `pretty` came from Stage 1, the statements from Stage 2, and the condition's `>` from this stage.  Compare the output with Build Step 9: you built that tree by hand, and the parser now builds it from text.

```python
# Step 31, test_parser.py: add above the main block
WHILE_SOURCE = "let x = 10;\nwhile x > 0 {\n    print x;\n    x = x - 1;\n}"


def test_worked_while_example():
    assert parse(WHILE_SOURCE) == Program([
        Let("x", Num(10)),
        While(BinOp(">", Var("x"), Num(0)),
              Block([Print(Var("x")), Assign("x", BinOp("-", Var("x"), Num(1)))])),
    ])


def test_positions_recorded():
    tree = parse("let x = 1;\nprint x + 2;")
    assert (tree.stmts[0].line, tree.stmts[0].col) == (1, 1)
    assert (tree.stmts[1].value.line, tree.stmts[1].value.col) == (2, 9)
```

**You write:** `test_pretty_worked_example`, which asserts that `pretty(parse(WHILE_SOURCE))` equals the fourteen lines this check prints, joined with newlines.

Run this check:

```bash
python3 -c "from parser import parse; from ast_nodes import pretty; print(pretty(parse('let x = 10; while x > 0 { print x; x = x - 1; }')))"
```

You should see:

```text
Program
  Let x
    Num(10)
  While
    BinOp(>)
      Var(x)
      Num(0)
    Block
      Print
        Var(x)
      Assign x
        BinOp(-)
          Var(x)
          Num(1)
```

> **CTQ B31** Write this program's call trace, starting `parse_program`, `parse_stmt`, `parse_let_stmt`, `parse_expr`.  Write that trace now, while the ladder is fresh.  It is your own write-up, so the Answer Key leaves it out.

---

## Build Step 32: The Suite So Far

The ladder is complete, so the last two broken programs can finally give the right errors.  Stage 2 could not reach them, because they fail inside an expression.

<!-- run: id=cs374-liascript-parsingexpressions-13 viz=env -->
```python
# Step 32, test_parser.py: add above the main block
def test_bad_operator():
    err = parse_error("let x = 5 + * 3;")
    assert "expected an expression, found STAR" in err.message
    assert (err.line, err.col) == (1, 13)


def test_mismatched_paren():
    assert "expected RPAREN, found SEMICOLON" in parse_error("print (1 + 2;").message
```
[Visualize this example](https://billjr99.github.io/Ursinus-CS374-Fall2026/viz/#cs374-liascript-parsingexpressions-13) <!-- code-viz link -->

**You write:** one test of your own.  Pick an expression that mixes at least three tiers, draw its tree on paper, and assert that shape.

Run this check:

```bash
python3 test_parser.py
```

You should see this.  If you added tests of your own, your list is longer:

```text
PASS test_let_shape
PASS test_missing_semicolon
PASS test_bare_equals
PASS test_nested_blocks_shape
PASS test_else_if_chain
PASS test_dangling_else_attaches_to_nearest_if
PASS test_break_continue
PASS test_unclosed_block
PASS test_error_position_on_later_line
PASS test_literals
PASS test_unary_minus_nests
PASS test_left_associativity_division
PASS test_precedence_mul_over_add
PASS test_left_associativity_subtraction
PASS test_parentheses_override_precedence
PASS test_comparison_does_not_chain
PASS test_not_binds_looser_than_comparison
PASS test_or_over_and
PASS test_worked_while_example
PASS test_positions_recorded
PASS test_pretty_worked_example
PASS test_bad_operator
PASS test_mismatched_paren
23 passed, 0 failed
```

> **CTQ B32** The LR table in *Parsing, Part 2* decides that `*` binds tighter than `+` in one cell.  Find the place in your `parser.py` where the same decision lives.  Is it a line, or something about how the functions call each other?

**Stage 3 is done.**  You have a complete parser.  Go back to Part VII of [Abstract Syntax Trees](https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374-Fall2026/gh-pages/_pages/Activities/liascript-ast.md), Build Step 33, for the unparser and the round trip that test the whole thing.

---

---

**Up next:** *Parsing, Part 2* drives this same grammar bottom-up from an LR table.

# Answer Key

Work the models above with your team before reading these.  Each entry answers a Critical Thinking Question from the session; reading the answer first turns the exercise into transcription.

### Worked Example: `7 - 2 - 1`, one iteration at a time

Answer CTQ 1.1 yourself before reading.  The column that matters is `node`: watch it become its own left child.

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

Evaluated bottom-up: `(7 - 2) = 5`, then `5 - 1 = 4`.  Correct.

**CTQ 1.2, answered.**  Swap the two children in the wrap (make the new operand the left child and the accumulator the right) and the same tokens build:

```
        (-)
       /   \
      1    (-)
          /   \
         2     7
```

which evaluates as `1 - (2 - 7) = 6`.  Wrong.  Not a parse error, not a crash: a silently wrong number, from a one-line change in which side receives the accumulator.

That is the point of the model: associativity is not a property of the `-` operator.  It is a property of which side of the wrap the accumulator lands on.  Right-associative operators (`**` in Python, `^` in many languages) are built by recursing instead of looping: `parse_pow()` calls itself for the right operand rather than accumulating in a `while`, which puts the growth on the right side of the tree instead of the left.

### Stage 3, Build Steps 23 to 32: Blanks and Pieces You Write

Try each blank and each piece marked **You write** before you read these.  The checks on the slides tell you whether your own version works, so a different version that passes is fine.

- **P1** (Step 23): `tok.decoded`
- **P2** (Step 23): `tok.type == "TRUE"`
- **P3** (Step 24): `parse_expr(lexer)`
- **P4** (Step 24): `parse_unary(lexer)`
- **P5** (Step 25): `BinOp(op.value, left, right, op.line, op.col)`
- **P6** (Step 26): `parse_muldiv(lexer)`
- **P7** (Step 26): `("PLUS", "MINUS")`
- **P8** (Step 27): `if`
- **P9** (Step 28): `parse_not(lexer)`
- **P10** (Step 28): `parse_comparison(lexer)`
- **P11** (Step 30): `"EOF"`

**Step 23.**

```python
# Step 23 answer, test_parser.py: add above the main block
def test_literals():
    assert expr("3.14") == Num(3.14)
    assert expr(r'"a\nb"') == Str("a\nb")
    assert expr("true") == BoolLit(True)
```

**Step 25.**

```python
# Step 25 answer, parser.py: replace parse_expr
def parse_expr(lexer: Lexer):
    """Delegate to the highest tier built so far."""
    return parse_muldiv(lexer)
```

**Step 26.**

```python
# Step 26 answer, parser.py: replace parse_expr
def parse_expr(lexer: Lexer):
    """Delegate to the highest tier built so far."""
    return parse_addsub(lexer)
```

```python
# Step 26 answer, test_parser.py: add above the main block
def test_precedence_mul_over_add():
    assert expr("2 + 3 * 4") == BinOp("+", Num(2), BinOp("*", Num(3), Num(4)))


def test_left_associativity_subtraction():
    assert expr("8 - 3 - 2") == BinOp("-", BinOp("-", Num(8), Num(3)), Num(2))


def test_parentheses_override_precedence():
    assert expr("(2 + 3) * 4") == BinOp("*", BinOp("+", Num(2), Num(3)), Num(4))
```

**Step 27.**

```python
# Step 27 answer, parser.py: replace parse_expr
def parse_expr(lexer: Lexer):
    """Delegate to the highest tier built so far."""
    return parse_comparison(lexer)
```

**Step 28.**

```python
# Step 28 answer, parser.py: replace parse_expr
def parse_expr(lexer: Lexer):
    """Delegate to the highest tier built so far."""
    return parse_not(lexer)
```

**Step 29.**

```python
# Step 29 answer, parser.py
def parse_or(lexer: Lexer):
    """Parse an and_expr, then fold left while the next token is OR."""
    left = parse_and(lexer)
    while lexer.peek().type == "OR":
        op = lexer.advance()
        left = LogicOp("or", left, parse_and(lexer), op.line, op.col)
    return left
```

**Step 31.**

```python
# Step 31 answer, test_parser.py: add above the main block
def test_pretty_worked_example():
    want = ["Program", "  Let x", "    Num(10)", "  While", "    BinOp(>)",
            "      Var(x)", "      Num(0)", "    Block", "      Print",
            "        Var(x)", "      Assign x", "        BinOp(-)",
            "          Var(x)", "          Num(1)"]
    assert pretty(parse(WHILE_SOURCE)) == "\n".join(want)
```

### Stage 3: The Questions

**CTQ B23.**  The raw lexeme keeps its quotes and escapes, so `unparse` would add a second pair of quotes around text that already has them, and escape what was already escaped.

**CTQ B24.**  `lexer.advance()` runs before the recursive call, so each call starts one token further on and the input runs out.  The second line shows `Var(name='x', line=1, col=8)`: the parentheses left no trace, so `while (x) { }` now parses.

**CTQ B25.**  The second `/` is at column 7, and the outer node holds it.  The last operator of the run became the root, which is what a left fold produces, and it is why the first `/` is evaluated first.

**CTQ B26.**  The operands of `+` would be `2` and `3`, and the `*` would be left over, so the program fails at the `*`, with `expected SEMICOLON, found STAR` in a `print` statement.  The ladder skipped a rung.

**CTQ B27.**  Its left operand is the parenthesized comparison, so the source shows the tree's shape and nothing chains.  `unparse` must keep the parentheses on the left side as well, which is the rule for the comparison level.

**CTQ B28.**  The `lexer.advance()` line.  If the recursive call came first, it would run on the same `NOT` token forever: a call that consumes nothing can never terminate, the same failure as a left-recursive rule.

**CTQ B29.**  Nine functions run: `parse_expr`, `parse_or`, `parse_and`, `parse_not`, `parse_comparison`, `parse_addsub`, `parse_muldiv`, `parse_unary`, and `parse_primary`.  Only `parse_primary` builds a node.  The chain of calls is the parse tree's single-child chain, and it leaves nothing behind in the AST.

**CTQ B30.**  A `let` statement needs `parse_expr` to stop at the first token that cannot continue the expression, because that token is the `;` it expects next.  A REPL has nobody after it, so a leftover token means the user's input was wrong.

**CTQ B32.**  It is not a line.  It lives in how the functions call each other: `parse_addsub` takes its operands from `parse_muldiv`, so a `*` is consumed and folded before `parse_addsub` ever sees it.
