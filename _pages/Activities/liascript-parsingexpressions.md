<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374-Fall2026/gh-pages/_pages/Activities/liascript-parsingexpressions.md or locally via https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374-Fall2026/gh-pages/_pages/Activities/liascript-parsingexpressions.md

import: https://raw.githubusercontent.com/liascript/CodeRunner/master/README.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

# Parsing Expressions: Left Factoring, Precedence, and Iteration

Expression parsing is the most common and the trickiest part of building a language.  Without a deliberate grammar, `2 + 3 * 4` can parse as `(2 + 3) * 4 = 20` instead of the correct `2 + (3 * 4) = 14`.  The fix is a layered grammar: each precedence level gets its own rule.  A top-down parser cannot run that grammar until you remove its left recursion, and this activity shows you how, one tier at a time.  The "left factoring" in the title is the family of grammar rewrites that prepare a grammar for top-down parsing; removing left recursion is the member of that family you need today.  You will see two strategies that solve the same problem: recursive descent with one function per tier, and Pratt parsing with numeric binding powers.  Knowing both lets you handle any operator grammar you meet later.

## Learning Goals

By the end of this activity, you will be able to:

- Rewrite a left-recursive expression grammar into an equivalent loop form that recursive descent can run
- Implement a multi-tier expression parser whose chain of functions enforces operator precedence
- Trace the left-fold accumulation loop and predict the abstract syntax tree (AST) it builds for a run of same-precedence operators
- Explain why left-associative operators such as subtraction and division need a left fold rather than a right fold
- Extend the grammar with unary negation and parenthesized subexpressions, and write the matching parser functions

This session turns the layered expression grammar, the cure for ambiguity you met earlier, into running code.  We spend the most time on the move students find hardest: rewriting left recursion as the pattern `term { (op) term }` and folding the loop's results into a left-leaning tree.  We build the parser slowly, one operator tier at a time, exactly as your assignment will.  The plan for today: restate the ladder for descent, write one tier in code, chain operators in the loop, then finish the full ladder with parentheses and unary minus.

> **Before You Begin**, make sure you are comfortable with:
>
> - Recursive-descent parsing basics (from the *Recursive Descent Parsing* activity): writing one function per grammar rule, calling `peek()` / `advance()` / `expect()`, and recognizing the shape `rule -> A B C`.
> - Operator precedence and associativity.  Precedence says which operator binds tighter, so `*` wins over `+`.  Associativity says how a run of equal operators groups, so `7 - 2 - 1` means `(7 - 2) - 1` (left-associative) rather than `7 - (2 - 1)`.  A layered, unambiguous grammar encodes both properties.
> - Python dataclasses for AST nodes: the `@dataclass` decorator, field annotations, and constructing nested node objects.  You will use these when the assignment upgrades tuples to typed nodes.

---

## Directions and Group Roles

Work in your POGIL team with your rotated roles (**Manager**, **Recorder**, **Presenter**, **Reflector**).  Think each model and question through on your own first, then talk it over with your group.  The Recorder posts your answers to the Class Activity Questions discussion board, and the Presenter reports out wherever you disagreed or found another approach.  After class, respond to the reflective prompt on your own in your notebook.

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

### Critical Thinking Questions

**CTQ 0.1** Run the parser on `7 - 2 - 1`.  The tree should be `(-, (-, 7, 2), 1)`, which evaluates to `4`.  If the tree were `(-, 7, (-, 2, 1))` instead, what value would it produce?  Which tree is correct for subtraction, and what does this tell you about why left-associativity matters?

**CTQ 0.2** The grammar has `factor -> "-" factor` (unary minus).  This rule is right-recursive, and it does not cause infinite loops in a recursive-descent parser.  Why not?

**CTQ 0.3** Add a `parse_factor` method that handles unary negation.  If the current token is `-`, consume it and recursively call `parse_factor`; otherwise call `parse_primary`.  Test on `-3`, `--3`, and `-(2 + 3)`.

---

## Model 1: Trace the Loop

In this model you simulate the `parse_addsub` loop by hand (the loop is in the Code Cell below) so you can see exactly where associativity comes from.  The running `node` variable is a left accumulator.  Each new operator wraps the result so far as its left child, so the tree leans left.  Change which side receives the accumulator and you change the associativity, and with it the numeric result.

Consider `addsub` parsing the token stream for `7 - 2 - 1`.

### Critical Thinking Questions

1.  Walk the loop by hand.  What does the first `parse_muldiv()` return?  What happens on each `while` iteration?  What is the running `node` after each one?  The Recorder draws the tree as it grows.
2.  Suppose the loop body instead wrapped the new operand as the left child and the running result as the right.  What tree, and what wrong value, results for `7 - 2 - 1`?  You have just located associativity in a single line of code.
3.  Why does the loop in `addsub` test for `+` or `-` while leaving `*` to a different function entirely?  Connect this to the depth-equals-precedence principle.


> The worked answers to this session's models are in the **Answer Key** at the end of this page.  Attempt them with your team first.

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
@LIA.eval(`["main.py"]`, `none`, `python3 main.py`)

---

# Part II: Stress and Extend

Part II checks and extends what you built in Part I.  First you answer one multiple-choice question about the fold.  Then you meet Pratt parsing, a second strategy that encodes precedence as numbers rather than as a chain of functions.  Finally you push the parser further: right-associative operators, comparison tiers, and function-call syntax.  Your project language will need these same extensions, so treat the exercises as early project work rather than as isolated drills.

> **Watch out!**  The `while`-loop (left-fold) pattern cannot handle right-associative operators like `**` (exponentiation), because that pattern always folds left.  Use the original right-recursive rule `power -> unary [ "^" power ]` instead.  It makes one optional recursive call, not a loop, so it builds a right-leaning tree.  In a Pratt parser the equivalent move is to pass `bp - 1` rather than `bp` as the minimum binding power for the right-hand recursive call.

## 2.  One Line Decides Associativity

In `parse_addsub`, the line `node = (op, node, right)` places the previous result as the left child.  Changing nothing else, this single line determines that:

[( )] Multiplication binds tighter than addition
[(X)] Operators at this tier associate left, so `7 - 2 - 1` evaluates as `(7 - 2) - 1`
[( )] Parentheses are honored
[( )] The grammar is LL(1)

---


## 3.  Theory: The Ladder Does Not Scale

The ladder works, and its cost is easy to count.  Every precedence level is one function.  Every one of those functions calls down to the next even when the input has nothing to do with that level.  Parsing the single token `5` in the Part I grammar still walks `expr -> addsub -> muldiv -> unary -> primary`: four calls to reach one number.

C has fifteen precedence levels.  As a ladder, that is fifteen functions, fifteen stack frames per literal, and fifteen near-identical bodies to keep in sync when you add an operator.  Adding one operator at a new level means writing a new function and editing its two neighbours.

Precedence climbing (also called Pratt parsing, after Vaughan Pratt's 1973 paper) replaces the chain of functions with a number.  Each operator gets a **binding power**: a number that says how tightly it grips its operands.  One loop then reads operators and decides, by comparing numbers alone, whether to keep going or return.

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

### Reading the Code

- `BINDING` holds the grammar's precedence structure as data.  Compare it with Part I, where the same information was spread across four function definitions and their call order.
- `if bp < min_bp: break` is precedence.  When `parse_expr` is deep inside a `*` and meets a `+`, the comparison fails and the loop returns.  Whichever caller has a low enough minimum then handles the `+`.  No function per tier is required.
- `next_min = bp + 1 if assoc == "left" else bp` is associativity, in one line.  Trace `8 - 4 - 2`: the recursive call gets minimum 11, sees `-` at power 10, refuses it, and returns, so the outer loop folds left.  For `^` the call gets minimum 30, accepts the next `^`, and folds right.
- Prefix minus is handled before the loop with a high minimum (40).  That is why `-3 + 4` groups as `(-3) + 4` and not `-(3 + 4)`.
- The ladder and this table produce **identical trees**.  They are two encodings of one grammar.  Knowing both lets you choose: the ladder reads more like the grammar, and the table scales to fifteen levels without fifteen functions.

> **Watch out!**  It is tempting to give every operator a distinct binding power so ties never happen.  Do not.  Operators at the same precedence (like `+` and `-`) must share a power, or `8 - 4 + 2` will group wrongly.  Ties are meaningful; the associativity rule exists to resolve them.

### Critical Thinking Questions

> **CTQ 3.1** Trace `2 * 3 + 4` through Model 2 by hand and name the exact comparison that fails and forces a return.  Which line of code is it?

> **CTQ 3.2** `8 - 4 - 2` and `2 ^ 3 ^ 2` differ only in the `+ 1`.  Explain, in terms of what the recursive call is allowed to absorb, why that produces opposite tree shapes.

> **CTQ 3.3** The Part I ladder is four functions; Model 2 is one function plus a five-row table.  For a language with fifteen precedence levels, count each version's cost: functions written, and frames pushed to parse the single literal `5`.

> **CTQ 3.4** Both approaches produce the same trees, so the choice is not about correctness.  State the case for each, and say which your team will use and why.

### Try It Yourself

Add operators to the table without writing a single new function.

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

Expected output as written: the first line parses fully, and the other two stop early because the operators they need are not in the table yet.  Add the rows and all three consume everything.  You never wrote a parsing function to do it.  TODO 3 asks about a chained comparison, which is two comparison operators in a row with no parentheses, such as `a < b < c`.  Python reads it as `a < b and b < c`; C reads it as `(a < b) < c`.  Your language has to pick one, or reject the form.

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

## Exercises

1.  *Right-associative tier.*  Add exponentiation `^` that binds tighter than `*` and associates right.  The loop pattern will not give right association; the original right-recursive form `power -> unary [ "^" power ]` will.  Implement it, and verify that `2 ^ 3 ^ 2` yields the tree for `2 ^ (3 ^ 2)`.
2.  *Comparison tier.*  Add `< <= > >= == !=` at a tier looser than `addsub`, so that `a + 1 < b * 2` parses sensibly.  Decide and document whether the chained comparison `a < b < c` is legal in your language, and if so, what it means.  Python and C disagree, and your team must choose for December.
3.  *Torture tests.*  Run your full parser on `-(3 + 4) * -2`, `((1))`, `1 + + 2` (this should fail; check the message), and `8 / 4 / 2` (this must be 1, not 4, once evaluated).  Submit the trees or errors for each.
4.  *Function calls.*  Extend `primary` so an identifier may be followed by an argument list: `IDENT "(" [ expr { "," expr } ] ")"`.  Note which EBNF constructs you used and which code shapes they became.  Your project language will thank you.

---

## Reflection Prompt

In your notebook: the hardest conceptual move in this activity was seeing that a `while` loop and a left-recursive production say the same thing.  Write the explanation of that equivalence you wish someone had given you at the start, in your own words, for a future student.

---

## 4.  Further Reading

- Douglas Thain.  *Introduction to Compilers and Language Design*, Chapter 4.
- Robert Nystrom.  *Crafting Interpreters*, "Parsing Expressions" (online): the same ladder with pictures.
- Vaughan Pratt.  "Top Down Operator Precedence" (1973), the original paper behind Model 2.

---

**Up next:** the *Table-Driven and LR Parsing* activity shows the bottom-up, table-driven alternative that parser generators emit.  The tiered expression parser you finished here goes directly into the Parser assignment.

# Answer Key

Work the models above with your team before reading these.  Each entry answers a Critical Thinking Question from the session; reading the answer first turns the exercise into transcription.

### Worked Example: `7 - 2 - 1`, one iteration at a time

Answer Model 1, question 1 yourself before reading.  The column that matters is `node`: watch it become its own left child.

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

**Model 1, question 2, answered.**  Swap the two children in the wrap (make the new operand the left child and the accumulator the right) and the same tokens build:

```
        (-)
       /   \
      1    (-)
          /   \
         2     7
```

which evaluates as `1 - (2 - 7) = 6`.  Wrong.  Not a parse error, not a crash: a silently wrong number, from a one-line change in which side receives the accumulator.

That is the point of the model: associativity is not a property of the `-` operator.  It is a property of which side of the wrap the accumulator lands on.  Right-associative operators (`**` in Python, `^` in many languages) are built by recursing instead of looping: `parse_pow()` calls itself for the right operand rather than accumulating in a `while`, which puts the growth on the right side of the tree instead of the left.

---

