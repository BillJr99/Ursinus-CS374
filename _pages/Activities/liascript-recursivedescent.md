<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374-Fall2026/gh-pages/_pages/Activities/liascript-recursivedescent.md or locally via https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374-Fall2026/gh-pages/_pages/Activities/liascript-recursivedescent.md

import: https://raw.githubusercontent.com/liascript/CodeRunner/master/README.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

# Recursive Descent Parsing: From Grammar to Code

## Learning Goals

By the end of this activity, you will be able to:

- Translate each BNF/EBNF (Backus-Naur Form and Extended BNF) grammar production mechanically into a corresponding Python parsing function
- Implement the `peek`/`advance` token-consumption pattern and explain why one token of lookahead suffices for LL(1) grammars
- Identify left recursion in a grammar and rewrite the affected production as an iterative loop
- Construct a working recursive descent parser for a statement-level grammar including assignments, conditionals, and while loops
- Produce informative error messages by detecting and reporting unexpected tokens at each parsing decision point

Recursive descent is a way to write a parser by hand: **one function per nonterminal**, where each function's body follows its production's right-hand side.  The parser is where the grammar becomes a program, and this technique makes the translation nearly mechanical.  Today you learn the mapping, meet the one grammar shape that breaks it (left recursion), and parse real statements.  The route is the grammar-to-code mapping $\rightarrow$ a working statement parser $\rightarrow$ left recursion and lookahead $\rightarrow$ error messages worth reading.  In the *Abstract Syntax Trees* activity you designed the trees a parser should build.  Today you build the machine that produces them.

> **This activity continues on Tuesday, November 3.**  Pick up at the first part your team has not finished, and bring your notes from the earlier days.  Part II starts at *Left Recursion Kills Descent*, and Part III holds the runnable models for home.

---

## Before You Begin

> **Prerequisites.  Make sure you are comfortable with these before proceeding:**
>
> - **EBNF/BNF Grammars**: you need to read a grammar and trace derivations.  Review: [Syntax and BNF/EBNF Activity](https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374-Fall2026/gh-pages/_pages/Activities/liascript-syntaxbnf.md)
> - **Abstract Syntax Trees (ASTs)**: you need to understand what the parser is building.  Review: [AST Activity](https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374-Fall2026/gh-pages/_pages/Activities/liascript-ast.md)
>
> **Why this matters:** Recursive descent is the technique you will use to write the parser for your final project.  Every grammar rule you write becomes one Python function using the pattern below.  Once you know this pattern, the rest of the parser follows from the grammar.

---

## The Core Mapping Rule

> **The rule:** Every grammar rule becomes exactly one Python function.  The function's body is a direct, mechanical translation of the production's right-hand side.
>
> ```
> Rule:  expr -> term ( ('+' | '-') term )*
>
> Becomes:
>   def parse_expr():
>       left = parse_term()
>       while current_token in ('+', '-'):
>           op = eat(current_token)
>           right = parse_term()
>           left = BinOp(op, left, right)
>       return left
> ```
>
> | Grammar construct | Code shape |
> |---|---|
> | Nonterminal `A` | Call `parse_A()` |
> | Sequence `X Y Z` | Call `parse_X()`, then `parse_Y()`, then `parse_Z()` |
> | Terminal `'t'` | `expect('t')`, verify and consume the token |
> | Alternation `X | Y` | `if/elif` on the next token to choose a branch |
> | EBNF optional `[ X ]` | `if` the next token begins `X`, parse it |
> | EBNF repetition `{ X }` | `while` the next token begins `X`, parse it |
>
> You will use this table constantly.  Bookmark it.

---

## Directions and Group Roles

Work in your POGIL team with your rotated roles (**Manager**, **Recorder**, **Presenter**, **Reflector**).  Please think each model and question through on your own first, then talk it over with your group.  The Recorder posts your answers to the Class Activity Questions discussion board, and the Presenter reports out wherever you disagreed or found another approach.  After class, please respond to the reflective prompt on your own in your notebook.

---

# Part I: The Mapping

## 1.  One Nonterminal, One Function

The parser drives the lexer through exactly two operations.  `peek()` looks at the next token without consuming it, and `advance()` consumes it.  The parser decides what to do next by peeking at one token; that single-token look is called **lookahead**.  The set of tokens that can begin a nonterminal `X` is called the FIRST set of `X`, so "the next token begins `X`" in the table above means "the next token is in FIRST(`X`)".  A grammar is LL(1) when one token of lookahead decides every alternation.  The name stands for "Left-to-right scan, Leftmost derivation, 1 token of lookahead."  Parsing this way, where the next token predicts which rule to apply, is called predictive parsing, and recursive descent is its hand-written form.  The grammars we write for your project are LL(1) on purpose.

---

## How the Mapping Works: A Worked Example

Take a concrete expression grammar and trace how each production becomes a function.  You will perform this same transformation for every grammar rule in your project.

**Step 0.  Start with the grammar:**

```
expr   -> term  ( ('+' | '-') term  )*
term   -> factor ( ('*' | '/') factor )*
factor -> INT | '(' expr ')'
```

**Step 1.  Each nonterminal becomes a function skeleton:**

```python
def parse_expr():   ...   # handles expr
def parse_term():   ...   # handles term
def parse_factor(): ...   # handles factor
```

**Step 2.  Fill in each rule mechanically:**

`expr -> term ( ('+' | '-') term )*`
- Start with one `term` -> call `parse_term()`
- The `(...)* ` is EBNF repetition -> use a `while` loop
- Inside the loop, the alternation `'+' | '-'` -> `if peek() in ('+', '-')`

```python
def parse_expr():
    node = parse_term()          # parse the first term
    while peek() in ('+', '-'): # repetition: { ... }
        op = advance()           # consume '+' or '-'
        right = parse_term()     # parse the next term
        node = (op, node, right) # fold left: build the tree
    return node
```

**Step 3.  Do the same for `term -> factor ( ('*' | '/') factor )*`:**

```python
def parse_term():
    node = parse_factor()
    while peek() in ('*', '/'):
        op = advance()
        right = parse_factor()
        node = (op, node, right)
    return node
```

**Step 4.  For `factor -> INT | '(' expr ')'`, the alternation uses lookahead:**

```python
def parse_factor():
    if peek() is an INT:
        return ('num', advance())
    elif peek() == '(':
        advance()          # consume '('
        node = parse_expr()
        expect(')')        # consume ')'
        return node
    else:
        raise SyntaxError(...)
```

Notice that `parse_expr` calls `parse_term`, which calls `parse_factor`, which can call `parse_expr` again through the parenthesized subexpression.  This mutual recursion is the "recursive" part of "recursive descent."  The functions call each other in the same pattern that the grammar rules nest.

### Worked Example: `1 + 2 * 3` on the full ladder, with the tree

The Practice section later traces `1 + 2` on a one-level grammar, where precedence never comes up.  This example traces `1 + 2 * 3` on the full `expr / term / factor` ladder, where the answer must be 7 and not 9.

Grammar:

```
expr   -> term { ('+' | '-') term }
term   -> factor { ('*' | '/') factor }
factor -> INT | '(' expr ')'
```

Indentation shows the call stack.  `pos` is the index of the next unconsumed token; tokens are `1 + 2 * 3`.

```
call parse_expr()                      pos=0
  call parse_term()                    pos=0
    call parse_factor()                pos=0
      peek()=INT(1) -> consume         pos=1
      return ('num', 1)
    peek()='+' -> not * or /, loop does NOT run
    return ('num', 1)                  <- term returns the bare 1
  peek()='+' -> loop RUNS
  consume '+'                          pos=2
  call parse_term()                    pos=2
    call parse_factor()                pos=2
      peek()=INT(2) -> consume         pos=3
      return ('num', 2)
    peek()='*' -> loop RUNS
    consume '*'                        pos=4
    call parse_factor()                pos=4
      peek()=INT(3) -> consume         pos=5
      return ('num', 3)
    peek()=EOF -> loop ends
    return ('*', ('num',2), ('num',3)) <- the product is built HERE
  peek()=EOF -> loop ends
  return ('+', ('num',1), ('*', ...))
```

The tree that comes back:

```
        (+)
       /   \
   ('num',1)  (*)
             /   \
      ('num',2)  ('num',3)
```

Precedence happened at the two `peek()='+'` lines.  The first one is inside `parse_term`.  The `+` is not in `term`'s operator set, so `term` returns right away with the bare `1` and leaves the `+` on the input for `parse_expr` to handle.  The `*` is in `term`'s set, so the second `parse_term` call consumes it and builds the product before returning.

That is the whole mechanism: `term` sees every operator first, and it accepts only the tight ones.  The `*` node is finished and returned before the `+` node is built, so `*` sits deeper in the tree, and deeper means evaluated first.  Nothing in the code says "multiplication has higher precedence."  The grammar's layering says it, and the call stack carries it out.

Compare this with the LR table you will build in the *Parsing Expressions and Table-Driven Parsing* activity.  There, the same decision lives in one cell of a table (shift on `*`, reduce on `+`).  Here it lives in which function's loop is willing to consume which token.  Same precedence, two different places to look for it.

Remember two things from this section.  Each nonterminal is one function, and precedence comes from which function's loop consumes which operator.

---

## Model 1: Translate by Hand

Grammar fragment (statements for a small language):

```
stmt     -> printstmt | letstmt
printstmt -> "print" expr ";"
letstmt   -> "let" IDENT "=" expr ";"
```

> **Intuition:** The parser looks at the current token and decides which rule to apply.  For `stmt` there are two choices.  If the current token is `print`, take the `printstmt` path; if it is `let`, take the `letstmt` path.  This single-token decision is lookahead.  Each path then consumes tokens in the exact order the grammar specifies; this is the "descent" part.

### Critical Thinking Questions

> **CTQ 1.1** Using the translation table, write pseudocode for `parse_stmt`, `parse_printstmt`, and `parse_letstmt`.  Which single token decides the alternation in `parse_stmt`?

> **CTQ 1.2** What should `expect(SEMICOLON)` do when the next token is not a semicolon?  Write the error message you would want at 2 AM, including what it should contain (expected what, found what, where).

> **CTQ 1.3** Add `whilestmt -> "while" "(" expr ")" block` to the grammar and to your pseudocode.  Did the alternation in `parse_stmt` remain decidable by one token?  What property of the three statement keywords makes it so?

---

## Model 2: Read the Parser

> **Intuition:** The code cell below is a near-mechanical translation of the grammar from Model 1.  Before reading it, predict what you will see: three functions (`parse_stmt`, `parse_printstmt`, `parse_letstmt`), each consuming tokens in the order the grammar says.  The `parse_expr` at the bottom is a stub: it handles only numbers and identifiers.  The full expression ladder comes in a later module.  The tuple return values (`("print", value)`, `("let", name, value)`) are the roots of small AST subtrees.

```python
# A recursive descent parser for the statement grammar, atop the class lexer.
# Each function is one production; read them side by side with the grammar.

class Token:
    def __init__(self, type_, lexeme, line=1):
        self.type = type_; self.lexeme = lexeme; self.line = line
    def __repr__(self): return f"Token({self.type}, {self.lexeme!r})"

import re

TOKEN_RE = re.compile(
    r'(?P<KEYWORD>print|let)\b|'
    r'(?P<FLOAT>\d+\.\d*)|'
    r'(?P<INT>\d+)|'
    r'(?P<IDENT>[A-Za-z_]\w*)|'
    r'(?P<SEMICOLON>;)|'
    r'(?P<EQ>=)|'
    r'(?P<WS>\s+)'
)

def tokenize(src):
    tokens, line = [], 1
    for m in TOKEN_RE.finditer(src):
        kind = m.lastgroup
        if kind == "WS":
            line += m.group().count("\n"); continue
        tokens.append(Token(kind, m.group(), line))
    tokens.append(Token("EOF", "", line))
    return tokens

class Parser:
    def __init__(self, tokens):
        self.tokens = list(tokens)
        self.pos = 0

    def peek(self):
        return self.tokens[self.pos] if self.pos < len(self.tokens) else None

    def advance(self):
        tok = self.peek(); self.pos += 1; return tok

    def expect(self, ttype):
        tok = self.peek()
        if tok is None or tok.type != ttype:
            found = f"{tok.type} {tok.lexeme!r} at line {tok.line}" if tok else "end of input"
            raise SyntaxError(f"expected {ttype}, found {found}")
        return self.advance()

    # stmt -> printstmt | letstmt
    def parse_stmt(self):
        tok = self.peek()
        if tok and tok.type == "KEYWORD" and tok.lexeme == "print":
            return self.parse_printstmt()
        if tok and tok.type == "KEYWORD" and tok.lexeme == "let":
            return self.parse_letstmt()
        raise SyntaxError(f"expected a statement, found {tok.lexeme!r} at line {tok.line}" if tok
                          else "expected a statement, found end of input")

    # printstmt -> "print" expr ";"
    def parse_printstmt(self):
        self.expect("KEYWORD")              # print
        value = self.parse_expr()
        self.expect("SEMICOLON")
        return ("print", value)

    # letstmt -> "let" IDENT "=" expr ";"
    def parse_letstmt(self):
        self.expect("KEYWORD")              # let
        name = self.expect("IDENT").lexeme
        self.expect("EQ")
        value = self.parse_expr()
        self.expect("SEMICOLON")
        return ("let", name, value)

    # expr -> INT | FLOAT | IDENT     (a stub; the full ladder arrives next module)
    def parse_expr(self):
        tok = self.peek()
        if tok and tok.type in ("INT", "FLOAT", "IDENT"):
            self.advance()
            return ("num", float(tok.lexeme)) if tok.type in ("INT", "FLOAT") else ("var", tok.lexeme)
        raise SyntaxError(f"expected an expression, found {tok.lexeme!r}" if tok
                          else "expected an expression, found end of input")

# Demo: try each input and show the AST or the error
for source in ["print 42;", "let x = 7;", "let x 7;"]:
    try:
        result = Parser(tokenize(source)).parse_stmt()
        print(f"OK:    {source!r:20} -> {result}")
    except SyntaxError as e:
        print(f"ERROR: {source!r:20} -> SyntaxError: {e}")
```
@LIA.eval(`["main.py"]`, `none`, `python3 main.py`)

### Reading the Code

- Read the parser and the grammar side by side.  Every production is one function and every alternative is one branch.  This grammar has no `{ ... }` repetition yet; when the expression ladder adds one, it becomes one `while`.  There is no cleverness anywhere; the grammar *is* the control flow.
- The statement functions consume tokens only through `expect(kind)`, which checks the kind and raises if it is wrong.  The other consumer is the stub `parse_expr`, which calls `advance()` only after peeking, and the other errors come from `parse_stmt` and `parse_expr` when no alternative matches.  Every decision peeks first and then commits.  That is what makes the parser LL(1): one token of lookahead is enough to pick a branch.
- Each function returns the node it built and leaves the position one past what it consumed.  That contract lets the functions compose without any of them knowing about the others.
- The error case reports the token it *found* next to the one it wanted.  A parser that says only "syntax error" gives the user nothing to act on.  CTQ 2.6 asks you to fix that.

### Critical Thinking Questions

> **CTQ 2.4** Annotate each parser method with the production it implements (the comments start you off).  Where does the sequence rule become consecutive calls?  Where does alternation become an `if`?

> **CTQ 2.5** The parser returns tuples like `("let", "x", ("num", 7.0))`.  You have been told the parser builds a tree; where is the tree?  Identify the nesting, and connect these tuples back to the node shapes from the *Abstract Syntax Trees* activity.

> **CTQ 2.6** Run the failing case `let x 7;` and read the error.  Which `expect` fired, and does the message satisfy your 2 AM standard from CTQ 1.2?  Improve one message.

---

# Part II: Left Recursion and Lookahead

## 2.  Left Recursion Kills Descent

> **Watch out!  Left recursion sends your parser into an infinite loop.**
>
> A production is left-recursive when its right-hand side starts with the nonterminal it defines.  The grammar `E -> E + T | T` is left-recursive: `parse_E` calls `parse_E` as its very first action, before consuming any input.  The result is infinite recursion and a stack overflow.
>
> Transform it to `E -> T E'` where `E' -> + T E' | ε`.
>
> Or, equivalently, in EBNF (which is what we use in practice): `E -> T { '+' T }`
>
> The EBNF version becomes a `while` loop in code: no recursion, no infinite loop, same left-associative tree.
>
> The rule: if your grammar has `A -> A something`, rewrite it as `A -> something { something }`.

Recall the expression ladder's rule `E -> E + T | T`.  Translate it naively and `parse_E` immediately calls `parse_E`, which immediately calls `parse_E`, and so on.  The recursion never consumes a token.  Recursive descent cannot parse a left-recursive production directly.  The standard repair converts left recursion into EBNF repetition, which the translation table turns into a loop:

$$
E \rightarrow E + T \mid T \quad \Longrightarrow \quad E \rightarrow T \; \{ + \; T \}
$$

The two grammars accept the same strings.  The loop version builds the same left-leaning tree if your loop folds as it goes (the next module makes this concrete).  A related repair, left factoring, fixes alternations that share a prefix: `A -> xy | xz` becomes `A -> x (y | z)`, which restores one-token decidability.

> **Watch out!  Flipping the rule to `E -> T + E | T` stops the loop, but it changes the tree.**
>
> Moving `E` to the right end makes the rule right-recursive.  Now `parse_E` consumes a `T` before it calls itself, so every call starts further along the input and the recursion ends.  But the tree leans right: `1 + 2 + 3` parses as `1 + (2 + 3)`.  Addition gives the same number either way, so the mistake hides.  Subtraction exposes it: `8 - 4 - 2` becomes `8 - (4 - 2) = 6`, not `2`.  Use the loop `E -> T { + T }` for operators that group to the left, such as `+`, `-`, `*`, and `/`.  Keep right recursion for operators that group to the right, such as exponentiation (`2 ^ 3 ^ 2` is `2 ^ (3 ^ 2)`) and assignment (`a = b = c`); *Parsing Expressions* builds that case.
>
> Both alternatives of `E -> T + E | T` also begin with `T`, so one token of lookahead cannot choose between them.  Left-factor it to `E -> T [ + E ]`: parse one `T`, then check whether a `+` follows.

> **Watch out!  Lookahead and grammar design are linked.**
>
> Most recursive descent parsers look only at the current token to decide which rule to apply.  This is the LL(1) property from Part I: "Left-to-right scan, Leftmost derivation, 1 token of lookahead."
>
> If your grammar requires looking two or more tokens ahead, refactor the grammar, not the parser.  For example, `stmt -> IDENT '=' expr | IDENT '(' args ')'` requires seeing the token *after* the IDENT to decide which rule to use.  The fix is usually to left-factor: `stmt -> IDENT stmt_tail` where `stmt_tail -> '=' expr | '(' args ')'`.
>
> The rule: if you find yourself writing `peek_ahead(2)`, refactor the grammar first.

## Model 2b: Watch Left Recursion Kill a Parser, Then Fix It

Reading that left recursion loops forever is not the same as watching it happen.  Below are two parsers for the *same language*.  One is transcribed straight from `E -> E + T | T`, and one from `E -> T { + T }`.  Both are three lines of real logic.  Only one terminates.

```python
def tokenize(text):
    return text.replace("+", " + ").split()

def parse_T(tokens, pos):
    return tokens[pos], pos + 1

# --- VERSION 1: straight from  E -> E + T | T ------------------------------
# The first thing parse_E does is call parse_E, having consumed nothing.
calls = 0
def parse_E_left(tokens, pos):
    global calls
    calls += 1
    if calls > 20:
        raise RecursionError(
            f"parse_E called itself {calls} times and pos is still {pos}")
    left, pos2 = parse_E_left(tokens, pos)        # <-- consumes nothing first
    if pos2 < len(tokens) and tokens[pos2] == "+":
        right, pos2 = parse_T(tokens, pos2 + 1)
        return ("+", left, right), pos2
    return left, pos2

# --- VERSION 2: from  E -> T { "+" T } -------------------------------------
# Consume a T FIRST, then loop. Same language, same left-leaning tree.
def parse_E_loop(tokens, pos):
    node, pos = parse_T(tokens, pos)              # <-- consumes before looping
    while pos < len(tokens) and tokens[pos] == "+":
        right, pos = parse_T(tokens, pos + 1)
        node = ("+", node, right)                 # fold as we go: LEFT-leaning
    return node, pos

def show(node):
    if not isinstance(node, tuple):
        return str(node)
    op, l, r = node
    return f"({show(l)} {op} {show(r)})"

src = "1 + 2 + 3"
tokens = tokenize(src)
print(f"Parsing {src!r}\n")

print("=== Version 1:  E -> E + T | T  (transcribed literally) ===")
try:
    tree, _ = parse_E_left(tokens, 0)
    print(f"  {show(tree)}")
except RecursionError as e:
    print(f"  RecursionError: {e}")
    print("  The position never advanced, so no base case is reachable.")
    print("  This is not a bug in the CODE. The code is a faithful")
    print("  transcription. The bug is in the GRAMMAR's shape.")

print("\n=== Version 2:  E -> T { '+' T }  (the repair) ===")
tree, pos = parse_E_loop(tokens, 0)
print(f"  {show(tree)}   consumed {pos}/{len(tokens)} tokens")
print("  Left-leaning, which is what '+' should be: (1+2)+3, not 1+(2+3).")

print("\n=== The repair kept associativity ===")
for text in ["1 + 2", "1 + 2 + 3", "1 + 2 + 3 + 4"]:
    t, _ = parse_E_loop(tokenize(text), 0)
    print(f"  {text:16} -> {show(t)}")
```
@LIA.eval(`["main.py"]`, `none`, `python3 main.py`)

### Reading the Code

- The two versions differ by one decision: whether the *first* action consumes input.  Version 1 recurses first.  Version 2 calls `parse_T` first and only then loops.
- A call counter stops version 1, rather than Python's recursion limit, so the diagnostic can report the useful fact: `pos` is still 0 after twenty calls.  A recursive call that consumes nothing can never terminate, however deep the stack is.
- The fold `node = ("+", node, right)` inside the loop preserves **left** associativity.  Build it the other way and you get `1+(2+3)`, which looks fine for addition and is wrong for subtraction.
- The repair is not a workaround.  `E -> T { "+" T }` accepts the same language, and the loop version is what hand-written parsers in production do.

> **Watch out!**  It is tempting to "fix" left recursion by raising Python's recursion limit.  That turns an instant crash into a slower crash.  The grammar's shape is the problem.  The only fix is to rewrite the rule so the function consumes something before it recurses.

### Try It Yourself

Repair two more left-recursive rules, and confirm the tree shape survives.

```python
def tokenize(text):
    for sym in [",", "-"]:
        text = text.replace(sym, f" {sym} ")
    return text.split()

def show(node):
    if not isinstance(node, tuple):
        return str(node)
    op, l, r = node
    return f"({show(l)} {op} {show(r)})"

def parse_atom(tokens, pos):
    return tokens[pos], pos + 1

# TODO 1:  L -> L "," x | x     (a comma-separated list)
#          Rewrite as  L -> x { "," x }  and implement it here.
def parse_list(tokens, pos):
    return None, pos

# TODO 2:  E -> E "-" T | T
#          Subtraction MUST come out left-associative: 8-4-2 is 2, not 6.
def parse_sub(tokens, pos):
    return None, pos

def evaluate(node):
    if not isinstance(node, tuple):
        return float(node)
    _op, l, r = node
    return evaluate(l) - evaluate(r)

tree, _ = parse_list(tokenize("a , b , c"), 0)
print(f"  list  a , b , c   -> {show(tree) if tree else 'not implemented yet'}")

tree, _ = parse_sub(tokenize("8 - 4 - 2"), 0)
if tree:
    print(f"  sub   8 - 4 - 2   -> {show(tree)} = {evaluate(tree)}")
else:
    print(f"  sub   8 - 4 - 2   -> not implemented yet")

# TODO 3: 8 - 4 - 2 must come out as 2.0. If you get 6.0 you folded the
#         tree the wrong way. Which line changes, and why does addition
#         hide that mistake while subtraction exposes it?
```
@LIA.eval(`["main.py"]`, `none`, `python3 main.py`)

Expected output once both are implemented: `((a , b) , c)` and `((8 - 4) - 2) = 2.0`.  If subtraction gives `6.0`, reread the fold in Model 2b.

---

A teammate's `parse_expr` overflows the call stack instantly on any input.  Without seeing the code, the most likely diagnosis from today is:

[( )] The lexer returned too many tokens
[(X)] A left-recursive production was translated directly, so the function recurses before consuming input
[( )] The grammar is ambiguous
[( )] Python's recursion limit is too small for parsing

---

# Check Your Understanding

In recursive descent, one grammar nonterminal becomes:

[(X)] One function, whose body mirrors the production's structure
[( )] One entry in a parse table
[( )] One token type in the lexer
[( )] One AST node class

---

`E -> T { "+" T }` translates to a `while` loop rather than a recursive call. The loop must fold as `node = ("+", node, right)` because:

[(X)] Folding the accumulated tree on the left keeps `+` left-associative, so `1+2+3` is `(1+2)+3`
[( )] Python loops cannot build right-leaning trees
[( )] It is faster than the other order
[( )] Otherwise the loop would not terminate

---

Model 2b's version 1 fails after twenty calls with `pos` still 0. The diagnosis is:

[(X)] The recursive call happens before any input is consumed, so no base case is reachable
[( )] The tokenizer produced the wrong tokens
[( )] Python's recursion limit is set too low
[( )] The grammar is ambiguous

---

A grammar rule `stmt -> IDENT "=" expr | IDENT "(" args ")"` cannot be parsed with one token of lookahead. The standard repair is:

[(X)] Left-factor it: `stmt -> IDENT stmt_tail` with `stmt_tail -> "=" expr | "(" args ")"`
[( )] Add `peek_ahead(2)` to the parser
[( )] Make the lexer merge `IDENT =` into a single token
[( )] Rewrite it right-recursively

---

## Exercises

1.  *Extend the statement set.*  Add `whilestmt` and a brace-delimited `block -> "{" { stmt } "}"` to the parser, following the table mechanically.  Demonstrate on a two-statement loop body, and show the nested tuple structure you get.
2.  *Repair drill.*  Rewrite each as descent-ready EBNF: `L -> L "," x | x` (comma lists) and `S -> "if" E "then" S | "if" E "then" S "else" S | other` (left factor the shared prefix).  State which repair was which.
3.  *Error olympics.*  Construct five syntactically broken inputs and grade your parser's messages A through F on the 2 AM standard.  Fix the worst one and show before and after.
4.  *Lookahead limits.*  Invent a tiny grammar where one token of lookahead cannot decide an alternation but two tokens can.  What would `peek(2)` cost, and why do language designers prefer to redesign the grammar instead?

---

## Practice, Parser Tracing: Hand-Simulate a Descent Parser

These exercises give you practice with the grammar-to-code mapping and the call structure of a recursive descent parser.  You hand-simulate the exact sequence of function calls and token consumption.  They prepare you for the assignments ahead by showing the execution you will later trace in a debugger.

> *Exercises adapted from the recursive descent parsing technique covered in standard compiler texts, including Douglas Thain's *Introduction to Compilers and Language Design* (Chapter 4).*

A recursive descent parser for `expr -> term { '+' term }` will call `parse_term()` how many times for input `1 + 2 + 3`?

[( )] Once (parse_term is called one time total)
[( )] Twice (once per `+` operator)
[(X)] Three times (one for each number in the sum)
[( )] Unboundedly many (until end of input)

When parsing a statement like `if ( cond ) stmt`, the parser's call sequence is:

[( )] `parse_if_stmt()` -> `parse_cond()` -> `parse_stmt()`
[( )] `parse_stmt()` -> `parse_cond()` -> `parse_if_stmt()`
[(X)] `parse_stmt()` calls `parse_if_stmt()` when it sees `if` at the start; `parse_if_stmt()` then calls `parse_cond()` and `parse_stmt()` for its sub-parts
[( )] All three functions are called in parallel by the lexer

1.  **Hand-trace a parser call stack (simple grammar).**
   
   Grammar:
   ```
   expr -> term { '+' term }
   term -> INT
   ```
   
   Input tokens: `1 + 2`
   
   Trace the call stack step by step:
   ```
   call parse_expr()
     pos=0, peek()='1'
     call parse_term()
       consume INT('1')
       pos=1, return 1
     pos=1, peek()='+' -> loop condition true
     consume '+'
     pos=2, peek()='2'
     call parse_term()
       consume INT('2')
       pos=3, return 2
     pos=3, peek()=EOF -> loop condition false
     return tree for (1 + 2)
   ```
   
   Draw the call stack diagram: show which function called which, and in what order tokens were consumed.

2.  **Hand-trace a parser with nested alternatives (statement parser).**
   
   Grammar:
   ```
   stmt -> 'print' expr | 'let' IDENT '=' expr
   expr -> INT
   ```
   
   Input: `let x = 42`
   
   Trace:
   - `parse_stmt()` is called
   - `peek()` is `'let'` -> the first alternative ('print') fails because the lookahead is 'let', not 'print'
   - The second alternative ('let') succeeds because the lookahead matches
   - The parser follows the path for 'let IDENT = expr'
   - Show which function made which token consumption decision
   - Final tree structure (as a tuple or object)

3.  **Hand-trace a parser with repetition (zero times).**
   
   Grammar:
   ```
   stmt_list -> { stmt }
   stmt -> 'print' expr
   expr -> INT
   ```
   
   Input: empty (only EOF)
   
   Question: Does `parse_stmt_list()` on empty input:
   - Return an empty list (the `{ }` allows zero statements)?
   - Raise an error (at least one statement required)?
   
   Trace through a while loop implementation:
   ```python
   def parse_stmt_list(pos):
       stmts = []
       while pos < len(tokens) and tokens[pos].type == 'PRINT':
           new_pos = parse_stmt(tokens, pos)
           stmts.append(new_pos[0])
           pos = new_pos[1]
       return stmts, pos
   ```
   
   Show: how the loop's condition prevents any calls to `parse_stmt()` when input is empty, and what is returned.

4.  **Understand left-recursion failure (by hand).**
   
   **Bad grammar** (left-recursive):
   ```
   expr -> expr '+' term | term
   ```
   
   **Corresponding (broken) code:**
   ```python
   def parse_expr(pos):
       expr_node = parse_expr(pos)  # BUG: call parse_expr immediately, before consuming anything
       ...
   ```
   
   Trace what happens when you call `parse_expr(0)` on input `1`:
   - `parse_expr(0)` calls `parse_expr(0)` (recursion with no progress)
   - This recurses infinitely
   
   Now show the **fixed grammar** (using a while loop):
   ```
   expr -> term { '+' term }
   ```
   
   Trace the same input `1`:
   - `parse_expr(0)` calls `parse_term(0)`
   - Token consumed; the while loop condition checks for `+` -> not found
   - Loop exits and returns
   
   Explain: why does the fixed version consume a token before recursing, avoiding infinite recursion?

5.  **Integration trace: full statement parse.**
   
   Grammar:
   ```
   program -> stmt*
   stmt -> 'let' IDENT '=' expr ';'
   expr -> INT { '+' INT }
   ```
   
   Input: `let x = 1 + 2 ;`
   
   Produce a full execution trace showing:
   - Every function call (in order)
   - Every token consumed (and the position after)
   - The resulting AST tree (as nested tuples or objects)
   - Annotations explaining *why* each function was called (e.g., "called because stmt starts with 'let'")

---

# Part III: Runnable Models (at home)

## Model 3: Complete Recursive Descent Parser

> **Intuition:** The code cell below is a self-contained recursive descent parser: its tokenizer (lexer) and parser live together, with no external dependencies.  The grammar supports variable assignments, `if`/`while` statements, arithmetic with full precedence (`*` and `/` bind tighter than `+` and `-`), and `print`.  Read the parser functions top to bottom.  The call graph between functions mirrors the grammar's nesting.  The `parse_expr` -> `parse_term` -> `parse_factor` chain encodes precedence: deeper in the call stack means higher precedence.

The cell tokenizes its own input, so you can run it right away.  It parses a short multi-statement program and prints the resulting AST as nested tuples.

```python
# Complete recursive descent parser: tokenizer + parser together.
# Grammar:
#   program  -> stmt*
#   stmt     -> "if" "(" expr ")" block
#             | "while" "(" expr ")" block
#             | "print" expr ";"
#             | IDENT "=" expr ";"
#   block    -> "{" stmt* "}"
#   expr     -> term  { ("+" | "-")  term  }
#   term     -> factor { ("*" | "/") factor }
#   factor   -> INT | FLOAT | IDENT | "(" expr ")"

import re

# -- Lexer --------------------------------------------------------------------

TOKEN_RE = re.compile(
    r'(?P<FLOAT>\d+\.\d*|\.\d+)|'
    r'(?P<INT>\d+)|'
    r'(?P<KEYWORD>if|while|print)\b|'
    r'(?P<IDENT>[A-Za-z_]\w*)|'
    r'(?P<LBRACE>\{)|(?P<RBRACE>\})|'
    r'(?P<LPAREN>\()|(?P<RPAREN>\))|'
    r'(?P<SEMICOLON>;)|'
    r'(?P<EQ>=)|'
    r'(?P<ADDOP>[+\-])|'
    r'(?P<MULOP>[*/])|'
    r'(?P<WS>\s+)'
)

class Token:
    def __init__(self, type_, lexeme, line):
        self.type = type_; self.lexeme = lexeme; self.line = line
    def __repr__(self): return f"Token({self.type}, {self.lexeme!r})"

def tokenize(src):
    tokens, line = [], 1
    for m in TOKEN_RE.finditer(src):
        kind = m.lastgroup
        if kind == "WS":
            line += m.group().count("\n"); continue
        tokens.append(Token(kind, m.group(), line))
    tokens.append(Token("EOF", "", line))
    return tokens

# -- Parser -------------------------------------------------------------------

class Parser:
    def __init__(self, src):
        self.tokens = tokenize(src)
        self.pos = 0

    def peek(self):
        return self.tokens[self.pos]

    def advance(self):
        tok = self.peek()
        if tok.type != "EOF":
            self.pos += 1
        return tok

    def expect(self, ttype, lexeme=None):
        tok = self.peek()
        if tok.type != ttype or (lexeme and tok.lexeme != lexeme):
            want = f"{ttype}({lexeme!r})" if lexeme else ttype
            raise SyntaxError(
                f"expected {want}, got {tok.type}({tok.lexeme!r}) at line {tok.line}"
            )
        return self.advance()

    def match(self, ttype, lexeme=None):
        tok = self.peek()
        return tok.type == ttype and (lexeme is None or tok.lexeme == lexeme)

    # program -> stmt*
    def parse_program(self):
        stmts = []
        while self.peek().type != "EOF":
            stmts.append(self.parse_stmt())
        return ("program", stmts)

    # stmt -> if | while | print | assign
    def parse_stmt(self):
        tok = self.peek()
        if self.match("KEYWORD", "if"):     return self.parse_if()
        if self.match("KEYWORD", "while"):  return self.parse_while()
        if self.match("KEYWORD", "print"):  return self.parse_print()
        if self.match("IDENT"):             return self.parse_assign()
        raise SyntaxError(
            f"expected a statement, got {tok.type}({tok.lexeme!r}) at line {tok.line}"
        )

    def parse_if(self):
        self.expect("KEYWORD", "if")
        self.expect("LPAREN")
        cond = self.parse_expr()
        self.expect("RPAREN")
        body = self.parse_block()
        return ("if", cond, body)

    def parse_while(self):
        self.expect("KEYWORD", "while")
        self.expect("LPAREN")
        cond = self.parse_expr()
        self.expect("RPAREN")
        body = self.parse_block()
        return ("while", cond, body)

    def parse_print(self):
        self.expect("KEYWORD", "print")
        val = self.parse_expr()
        self.expect("SEMICOLON")
        return ("print", val)

    def parse_assign(self):
        name = self.expect("IDENT").lexeme
        self.expect("EQ")
        val = self.parse_expr()
        self.expect("SEMICOLON")
        return ("assign", name, val)

    def parse_block(self):
        self.expect("LBRACE")
        stmts = []
        while not self.match("RBRACE"):
            stmts.append(self.parse_stmt())
        self.expect("RBRACE")
        return ("block", stmts)

    # expr -> term { ("+"|"-") term }
    def parse_expr(self):
        node = self.parse_term()
        while self.match("ADDOP"):
            op = self.advance().lexeme
            node = (op, node, self.parse_term())
        return node

    # term -> factor { ("*"|"/") factor }
    def parse_term(self):
        node = self.parse_factor()
        while self.match("MULOP"):
            op = self.advance().lexeme
            node = (op, node, self.parse_factor())
        return node

    # factor -> INT | FLOAT | IDENT | "(" expr ")"
    def parse_factor(self):
        if self.match("INT") or self.match("FLOAT"):
            tok = self.advance()
            return ("num", float(tok.lexeme))
        if self.match("IDENT"):
            return ("var", self.advance().lexeme)
        if self.match("LPAREN"):
            self.advance()
            node = self.parse_expr()
            self.expect("RPAREN")
            return node
        tok = self.peek()
        raise SyntaxError(
            f"expected a factor, got {tok.type}({tok.lexeme!r}) at line {tok.line}"
        )

# -- Demo program -------------------------------------------------------------

src = """
x = 2 + 3 * 4;
while (x) {
    x = x - 1;
    print x;
}
if (x) {
    print x + 1;
}
"""

import pprint
ast = Parser(src).parse_program()
pprint.pprint(ast)
```
@LIA.eval(`["main.py"]`, `none`, `python3 main.py`)

### Critical Thinking Questions

> **CTQ 3.11** The parser uses two levels for expressions (`parse_expr` and `parse_term`) with `ADDOP` handled at the outer level and `MULOP` at the inner.  Trace the parsing of `2 + 3 * 4` and show which node becomes the left child versus the right child of `+`.  How does this level structure enforce precedence?

> **CTQ 3.12** `parse_block` loops `while not self.match("RBRACE")`.  What happens if the programmer forgets a closing `}`?  Write the exact error message the parser would produce, and explain which line of the parser generates it.

> **CTQ 3.13** The AST for `x = x - 1` is `('assign', 'x', ('-', ('var', 'x'), ('num', 1.0)))`.  A later "interpreter" pass walks this tree.  Write pseudocode for `eval_node` that handles `num`, `var`, `assign`, and `-` nodes, using a dict called `env` as the store.

> **CTQ 3.14** Add a `letstmt` production (`let IDENT = expr ;`) to the grammar and to the parser above.  How many lines change?  What single token in `parse_stmt`'s lookahead decides between `assign` (which also starts with an IDENT) and the new `let`?

---

## Model 4: Mini Calculator Language, Lexer, Parser, and Evaluator Together

> **Intuition:** The calculator language has only eight kinds of tokens (`INT`, `FLOAT`, `+`, `-`, `*`, `/`, `(`, `)`), plus an end-of-input marker, and three grammar rules.  It is already a complete language implementation.  The lexer breaks input into tokens, the parser turns tokens into an AST, and the evaluator walks the AST to compute the answer.  Your final project follows this same three-layer pattern, with more rules.
>
> Read this code as a template.  Swap in your own token types, your own grammar rules, and your own evaluator actions, and you have your project's core.

```python
# Mini calculator: a complete language implementation in ~80 lines.
#
# Grammar:
#   expr   -> term   { ('+' | '-') term   }
#   term   -> factor { ('*' | '/') factor }
#   factor -> INT | FLOAT | '(' expr ')'
#
# Example runs:
#   calc("2 + 3")        -> 5.0
#   calc("2 + 3 * 4")    -> 14.0   (not 20: * binds tighter)
#   calc("(2 + 3) * 4")  -> 20.0
#   calc("10 / 2 - 1")   -> 4.0

import re

# -- Layer 1: Lexer ------------------------------------------------------------
# Intuition: break the input string into meaningful chunks.
# We use a list of regex patterns and try each one at the current position.

CALC_RE = re.compile(
    r'(?P<FLOAT>\d+\.\d*)|'        # decimal: must come before INT
    r'(?P<INT>\d+)|'                 # integer
    r'(?P<PLUS>\+)|'
    r'(?P<MINUS>-)|'
    r'(?P<STAR>\*)|'
    r'(?P<SLASH>/)|'
    r'(?P<LPAREN>\()|'
    r'(?P<RPAREN>\))|'
    r'(?P<WS>\s+)'
)

class Token:
    def __init__(self, type_, value, line=1, col=1):
        self.type = type_
        self.value = value
        self.line = line
        self.col  = col
    def __repr__(self):
        return f"Token({self.type}, {self.value!r})"

def lex_calc(src):
    """Turn a source string into a list of Token objects."""
    tokens = []
    line, line_start = 1, 0
    for m in CALC_RE.finditer(src):
        kind = m.lastgroup
        col  = m.start() - line_start + 1
        if kind == "WS":
            if "\n" in m.group():
                line += m.group().count("\n")
                line_start = m.start() + m.group().rindex("\n") + 1
            continue
        tokens.append(Token(kind, m.group(), line, col))
    tokens.append(Token("EOF", "", line, 0))
    return tokens

# -- Layer 2: Parser -----------------------------------------------------------
# Intuition: turn the flat token list into a nested tree (the AST).
# Each grammar rule becomes one method; the nesting of calls mirrors the grammar.

class CalcParser:
    def __init__(self, src):
        self.tokens = lex_calc(src)
        self.pos = 0

    def peek(self):
        return self.tokens[self.pos]

    def advance(self):
        tok = self.peek()
        if tok.type != "EOF":
            self.pos += 1
        return tok

    def expect(self, ttype):
        tok = self.peek()
        if tok.type != ttype:
            raise SyntaxError(
                f"line {tok.line}, col {tok.col}: "
                f"expected {ttype}, got {tok.type}({tok.value!r})"
            )
        return self.advance()

    # expr -> term { ('+' | '-') term }
    def parse_expr(self):
        node = self.parse_term()
        while self.peek().type in ("PLUS", "MINUS"):
            op = self.advance().value   # consume '+' or '-'
            right = self.parse_term()
            node = ("binop", op, node, right)
        return node

    # term -> factor { ('*' | '/') factor }
    def parse_term(self):
        node = self.parse_factor()
        while self.peek().type in ("STAR", "SLASH"):
            op = self.advance().value
            right = self.parse_factor()
            node = ("binop", op, node, right)
        return node

    # factor -> INT | FLOAT | '(' expr ')'
    def parse_factor(self):
        tok = self.peek()
        if tok.type in ("INT", "FLOAT"):
            self.advance()
            return ("num", float(tok.value))
        if tok.type == "LPAREN":
            self.advance()              # consume '('
            node = self.parse_expr()
            self.expect("RPAREN")       # must see ')' here
            return node
        raise SyntaxError(
            f"line {tok.line}, col {tok.col}: "
            f"expected a number or '(', got {tok.type}({tok.value!r})"
        )

    def parse(self):
        ast = self.parse_expr()
        if self.peek().type != "EOF":
            tok = self.peek()
            raise SyntaxError(
                f"line {tok.line}, col {tok.col}: "
                f"unexpected token {tok.type}({tok.value!r}) after expression"
            )
        return ast

# -- Layer 3: Evaluator --------------------------------------------------------
# Intuition: walk the AST and compute the result.
# Each node type has a case; the recursive calls mirror the tree structure.

def evaluate(node):
    """Recursively evaluate an AST node, returning a float."""
    kind = node[0]
    if kind == "num":
        return node[1]                  # leaf: just return the number
    if kind == "binop":
        _, op, left, right = node
        lval = evaluate(left)           # recurse into left subtree
        rval = evaluate(right)          # recurse into right subtree
        if op == "+": return lval + rval
        if op == "-": return lval - rval
        if op == "*": return lval * rval
        if op == "/":
            if rval == 0:
                raise ZeroDivisionError("division by zero in expression")
            return lval / rval
    raise ValueError(f"unknown AST node kind: {kind!r}")

# -- Convenience wrapper --------------------------------------------------------

def calc(src):
    """Parse and evaluate a calculator expression string."""
    ast = CalcParser(src).parse()
    return evaluate(ast)

# -- Test suite ----------------------------------------------------------------

test_cases = [
    ("2 + 3",           5.0),
    ("2 + 3 * 4",       14.0),   # * binds tighter than +
    ("(2 + 3) * 4",     20.0),   # parens override precedence
    ("10 / 2 - 1",      4.0),
    ("1 + 2 + 3 + 4",   10.0),   # left-associative chain
    ("2 * (3 + 4) * 5", 70.0),
]

print("=== Calculator test suite ===")
all_pass = True
for expr, expected in test_cases:
    try:
        result = calc(expr)
        status = "PASS" if abs(result - expected) < 1e-9 else "FAIL"
        if status == "FAIL": all_pass = False
        print(f"  {status}  calc({expr!r:25}) = {result}  (expected {expected})")
    except Exception as e:
        all_pass = False
        print(f"  ERROR calc({expr!r:25}) raised {type(e).__name__}: {e}")

print()
print("All tests passed!" if all_pass else "Some tests FAILED.")

# -- Show the AST for one expression ------------------------------------------

print()
print("AST for '2 + 3 * 4':")
import pprint
pprint.pprint(CalcParser("2 + 3 * 4").parse())
print()
print("Notice: * node is nested DEEPER than + node,")
print("meaning * is evaluated first -- this is how precedence is encoded in the tree.")
```
@LIA.eval(`["main.py"]`, `none`, `python3 main.py`)

### Critical Thinking Questions

> **CTQ 4.15** The evaluator uses `evaluate(left)` and `evaluate(right)` recursively.  What is the base case that stops the recursion?  What happens if you have a deeply nested expression like `((((1 + 2))))`?

> **CTQ 4.16** The grammar has two levels (`expr` and `term`) to encode that `*` binds tighter than `+`.  Add a third level `power` for `**` (exponentiation, right-associative) with the highest precedence.  Write the grammar rule and the `parse_power` function.  Should the loop fold left or right?

> **CTQ 4.17** The test case `"2 + 3 * 4"` returns `14.0`, not `20.0`.  Trace the call sequence starting from `parse_expr()` and show exactly which functions are called and in what order.  At which point does the parser "decide" that `3 * 4` groups together before `2 +`?

> **CTQ 4.18** Extend the evaluator to support variables: add a `let x = expr` statement form (semicolon-terminated), a `dict` called `env`, and a `("var", name)` node type that looks up `name` in `env`.  Show the extended grammar, the new parser function, and the new evaluator case.

---

**In-class work stops here.**  Everything below is homework and going-deeper material: attempt the exercises before the related assignment.

> **Build your own parser at home.**  Part IV at the end of this page is Stage 2 of a step-by-step build that starts in Part VI of the *Abstract Syntax Trees* activity.  It turns the models above into your own `parser.py`, one statement form at a time.


## 4.  Further Reading

- Douglas Thain.  *Introduction to Compilers and Language Design*, Chapter 4.
- Robert Nystrom.  *Crafting Interpreters*, "Parsing Expressions" (online).
- Wirth, Niklaus.  *Compiler Construction* (online), the classic minimalist treatment.
- [Build an Interpreter](https://www.billmongan.com/Ursinus-CS374-Fall2026/Tutorials/BuildAnInterpreter): a complete recursive-descent parser (Stage 3) wired into a lexer and an evaluator.
- Panic-mode error recovery and synchronization points, for a parser that reports several syntax errors in one run: the "Synchronizing a recursive descent parser" section of *Crafting Interpreters*.  A strong stretch goal for your team language.

---

## Reflection Prompt

In your notebook: recursive descent works because the code's shape *is* the grammar's shape, a rare case of documentation that cannot drift from implementation.  Where else have you seen (or wished for) structure and description fused this way?

---

# Part IV: Build It, Stage 2 (at home)

## Build Stage 2: From Models to `parser.py`

This part continues the build that started in Part VI of [Abstract Syntax Trees](https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374-Fall2026/gh-pages/_pages/Activities/liascript-ast.md).  Finish Build Steps 1 to 9 there first, because `parser.py` imports your `ast_nodes.py`.  When you finish Build Step 22 here, go on to Part V of [Parsing Expressions](https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374-Fall2026/gh-pages/_pages/Activities/liascript-parsingexpressions.md).

As in Stage 1, each step is one slide, you type the fragment, `____R1____` is a blank answered in the **Answer Key** at the end of this page, and you run each check from inside `cs374-parser/`.

Your permanent parser keeps the shape of Models 2 and 3 and changes three things:

| In the models above | In your `parser.py` |
|---|---|
| methods on a `Parser` class, using `self` | functions that take the lexer: `parse_let_stmt(lexer)` |
| a small `Token` with `.lexeme` | your lexer's `Token` with `.value` |
| tuples such as `("let", name, value)` | your node classes, with positions: `Let(name, value, line, col)` |

The grammar for this stage has no parentheses around conditions, and it has a `block` in every `if` and `while`:

```text
program       ::= stmt* EOF
stmt          ::= let_stmt | assign_stmt | print_stmt | if_stmt
                | while_stmt | break_stmt | continue_stmt | block
let_stmt      ::= LET IDENT EQ expr SEMICOLON
assign_stmt   ::= IDENT EQ expr SEMICOLON
print_stmt    ::= PRINT expr SEMICOLON
if_stmt       ::= IF expr block ( ELSE ( if_stmt | block ) )?
while_stmt    ::= WHILE expr block
break_stmt    ::= BREAK SEMICOLON
continue_stmt ::= CONTINUE SEMICOLON
block         ::= LBRACE stmt* RBRACE
```

---

## Build Step 10: The Error Every Function Shares

Start `parser.py` with the one exception it raises.  CTQ 1.2 asked for the error message you would want at 2 AM: what was expected, what was found, and where.  `ParseError` keeps those as attributes as well as in the text, so a test can ask for the column without pattern-matching English.  A small scratch file, `check.py`, lets later checks show an error as one clean line rather than a traceback.

```python
# Step 10, parser.py
from typing import Optional

from lexer import Lexer
from ast_nodes import (Assign, BinOp, Block, BoolLit, Break, Continue, If, Let,
                       LogicOp, Num, Print, Program, Str, UnaryOp, Var, While)


class ParseError(Exception):
    """A syntax error that keeps expected, found, line, and col as attributes."""

    def __init__(self, expected: str, found: str, line: int = 0, col: int = 0):
        self.expected, self.found = expected, found
        self.line, self.col = line, col
        self.message = ____R1____
        super().__init__(f"ParseError at line {line}, col {col}: {self.message}")
```

```python
# Step 10, check.py
from parser import ParseError


def show_error(fn, *args):
    """Call fn, then print the ParseError it raises, or say that none came."""
    try:
        print("no error:", fn(*args))
    except ParseError as err:
        print(err)
```

Run this check:

```bash
python3 -c "from parser import ParseError; err = ParseError('SEMICOLON', 'RBRACE', 3, 12); print(err); print(err.found, err.line, err.col)"
```

You should see:

```text
ParseError at line 3, col 12: expected SEMICOLON, found RBRACE
RBRACE 3 12
```

> **CTQ B10** Model 2 raises Python's `SyntaxError` with a message string.  Suppose you want a test to confirm that an error lands on column 12.  What would that test have to do with Model 2's error, and what can it do with this one?

---

## Build Step 11: `expect`

Every terminal in a production becomes a call to `expect`, the same rule as the translation table in Part I.  Model 2's version lived on the class.  This one takes the lexer, and it reads the token stream only through `peek` and `advance`.  It raises on the token it peeked, so the error's position is the position of the actual mistake.

```python
# Step 11, parser.py
def expect(lexer: Lexer, token_type: str):
    """Peek for token_type; consume and return it, or raise a positioned ParseError."""
    tok = lexer.peek()
    if tok.type != ____R2____:
        raise ParseError(token_type, tok.type, tok.line, tok.col)
    return ____R3____
```

Run this check:

```bash
python3 -c "from lexer import Lexer; from parser import expect; from check import show_error; lx = Lexer('let )'); print(expect(lx, 'LET').type); show_error(expect, lx, 'IDENT')"
```

You should see:

```text
LET
ParseError at line 1, col 5: expected IDENT, found RPAREN
```

> **CTQ B11** Your lexer already has an `expect` method.  What does it raise when the type is wrong, and why would calling it from the parser give your program two kinds of syntax error?

---

## Build Step 12: A Stand-In for Expressions

Statements need expressions, but the expression ladder belongs to Stage 3.  Model 2 solved this with a stub, and you do the same: for now an expression is one primary, and a primary is one token.  Stage 3 fills in `parse_primary` and moves `parse_expr` up the ladder, and no statement function will change when that happens.

```python
# Step 12, parser.py
def parse_primary(lexer: Lexer):
    """Peek one token; consume a literal or a name and return its node."""
    tok = lexer.peek()
    if tok.type == "INT":
        lexer.advance()
        return Num(int(tok.value), tok.line, tok.col)
    raise ParseError("an expression", tok.type, tok.line, tok.col)


def parse_expr(lexer: Lexer):
    """Stand in for the whole ladder until Stage 3: one primary."""
    return parse_primary(lexer)
```

**You write:** the `IDENT` case of `parse_primary`, above the `raise`.  It consumes the token and returns a `Var` with the token's text, line, and column.

Run this check:

```bash
python3 -c "from lexer import Lexer; from parser import parse_expr; from check import show_error; print(parse_expr(Lexer('42'))); print(parse_expr(Lexer('x'))); show_error(parse_expr, Lexer(';'))"
```

You should see:

```text
Num(value=42, line=1, col=1)
Var(name='x', line=1, col=1)
ParseError at line 1, col 1: expected an expression, found SEMICOLON
```

> **CTQ B12** The error reports column 1.  What would it report on the input `; ;` if `parse_primary` called `advance` before its `peek`?  Try it, then undo the change.

---

## Build Step 13: `let`

This is Model 2's `parse_letstmt` with the three changes above.  Each terminal becomes `expect`, the nonterminal becomes a call, and the order comes straight from `let_stmt ::= LET IDENT EQ expr SEMICOLON`.  `expect` returns the token it consumed, which is how you get the name, and the `LET` token gives the node its position.

```python
# Step 13, parser.py
def parse_let_stmt(lexer: Lexer):
    """Consume LET IDENT EQ, an expression, and SEMICOLON; return a Let."""
    let_tok = expect(lexer, "LET")
    name = expect(lexer, "IDENT")
    expect(lexer, "EQ")
    value = ____R4____
    expect(lexer, "SEMICOLON")
    return Let(name.value, value, let_tok.line, let_tok.col)
```

Run this check:

```bash
python3 -c "from lexer import Lexer; from parser import parse_let_stmt; from check import show_error; print(parse_let_stmt(Lexer('let x = 1;'))); show_error(parse_let_stmt, Lexer('let x 1;'))"
```

You should see:

```text
Let(name='x', value=Num(value=1, line=1, col=9), line=1, col=1)
ParseError at line 1, col 7: expected EQ, found INT
```

> **CTQ B13** CTQ 2.6 asked which `expect` fired for `let x 7;` in Model 2.  Compare its message with the one you see here.  Which of the three facts on your 2 AM list did Model 2 already have, and which is new?

---

## Build Step 14: `print` and Assignment

`print` follows the same pattern with fewer terminals.  A `Print` node keeps only a line, as you declared it in Build Step 4.

```python
# Step 14, parser.py
def parse_print_stmt(lexer: Lexer):
    """Consume PRINT, an expression, and SEMICOLON; return a Print."""
    print_tok = expect(lexer, "PRINT")
    value = parse_expr(lexer)
    expect(lexer, "SEMICOLON")
    return Print(value, print_tok.line)
```

**You write:** `parse_assign_stmt`, from `assign_stmt ::= IDENT EQ expr SEMICOLON`.  It is `parse_let_stmt` without its first line, and its position comes from the name token.

Run this check:

```bash
python3 -c "from lexer import Lexer; from parser import parse_print_stmt, parse_assign_stmt; print(parse_print_stmt(Lexer('print x;'))); print(parse_assign_stmt(Lexer('x = 2;')))"
```

You should see:

```text
Print(value=Var(name='x', line=1, col=7), line=1)
Assign(name='x', value=Num(value=2, line=1, col=5), line=1, col=1)
```

> **CTQ B14** Both functions end by consuming a `SEMICOLON`.  Could you move that call out into whatever calls them?  What would that do to the rule that one function holds one production?

---

## Build Step 15: Dispatch on One Token

`parse_stmt` is the alternation in the grammar: one `if` per alternative, chosen by peeking.  It does not consume the token, because the function it picks starts by expecting that same token.  The rest of the statement forms join this chain as you build them, above the `raise`.

```python
# Step 15, parser.py
def parse_stmt(lexer: Lexer):
    """Peek at a statement's first token and dispatch on its type."""
    tok = lexer.peek()
    if tok.type == "LET":
        return parse_let_stmt(lexer)
    if tok.type == "IDENT":
        return parse_assign_stmt(lexer)
    if tok.type == "PRINT":
        return parse_print_stmt(lexer)
    raise ParseError("a statement", tok.type, tok.line, tok.col)
```

Run this check:

```bash
python3 -c "from lexer import Lexer; from parser import parse_stmt; from check import show_error; print(parse_stmt(Lexer('x = 1;'))); show_error(parse_stmt, Lexer('= 5;')); show_error(parse_stmt, Lexer('x 1;'))"
```

You should see:

```text
Assign(name='x', value=Num(value=1, line=1, col=5), line=1, col=1)
ParseError at line 1, col 1: expected a statement, found EQ
ParseError at line 1, col 3: expected EQ, found INT
```

> **CTQ B15** The last two errors come from different functions.  Which function raised each one, and what did `parse_stmt` know when it chose?  This check gives you the evidence for how much lookahead you need, and the explanation is yours, so the Answer Key leaves that part out.

---

## Build Step 16: A Whole Program

A program is `stmt* EOF`, and the translation table turns `stmt*` into a `while`.  `EOF` is a real token from your lexer, so the loop tests for it the way any other loop tests for a token.  `parse` is the entry point everything else uses.  It accepts an optional token specification, which it hands straight to the lexer, because the parser never looks at characters.

```python
# Step 16, parser.py
def parse_program(lexer: Lexer):
    """Parse statements until the next token is EOF; return a Program."""
    stmts = []
    while lexer.peek().type != ____R5____:
        stmts.append(parse_stmt(lexer))
    return Program(stmts)


def parse(source: str, config_path: Optional[str] = None) -> Program:
    """Parse a full program from source text."""
    return parse_program(Lexer(source, config_path=config_path))
```

Run this check:

```bash
python3 -c "from parser import parse; print(parse('let x = 1; print x;')); print(parse('')); print(parse('x := 1;', 'token_spec_alt.json'))"
```

You should see:

```text
Program(stmts=[Let(name='x', value=Num(value=1, line=1, col=9), line=1, col=1), Print(value=Var(name='x', line=1, col=18), line=1)])
Program(stmts=[])
Program(stmts=[Assign(name='x', value=Num(value=1, line=1, col=6), line=1, col=1)])
```

> **CTQ B16** The third line uses the other dialect's `:=` and builds the same `Assign`.  Which file changed what `=` looks like, and which functions in `parser.py` had to know about it?

---

## Build Step 17: A Test File That Grows with You

Every step from here on can add a test, and each test stays in the file for good.  This harness has a helper for tests that must fail.  Each test asserts on nodes and fields, and it can write `Num(1)` with no position, because Build Step 2 made `==` skip positions.

```python
# Step 17, test_parser.py
from lexer import Lexer
from parser import parse, parse_expr, ParseError
from ast_nodes import *


if __name__ == "__main__":
    tests = [f for name, f in dict(globals()).items() if name.startswith("test_")]
    failed = 0
    for t in tests:
        try:
            t()
            print("PASS", t.__name__)
        except Exception as err:      # keep going, so one break does not hide the rest
            failed += 1
            print("FAIL", t.__name__, "--", err)
    print(f"{len(tests) - failed} passed, {failed} failed")
```

```python
# Step 17, test_parser.py: add above the main block
def expr(source):
    return parse_expr(Lexer(source))


def parse_error(source):
    """Parse source, which must fail, and return the ParseError."""
    try:
        parse(source)
    except ParseError as err:
        return err
    raise AssertionError(f"no ParseError for {source!r}")


def test_let_shape():
    assert parse("let x = 1;") == Program([Let("x", Num(1))])
```

**You write:** two more tests above the main block.  `test_missing_semicolon` asserts that `let x = 5` fails with `expected SEMICOLON, found EOF` in its `message`, at line 1, column 10.  `test_bare_equals` asserts that `= 5;` fails with `expected a statement, found EQ`, at line 1, column 1.

Run this check:

```bash
python3 test_parser.py
```

You should see:

```text
PASS test_let_shape
PASS test_missing_semicolon
PASS test_bare_equals
3 passed, 0 failed
```

> **CTQ B17** Why does the harness catch `Exception` and keep going, rather than stopping at the first failure?  What would you lose in a run where three tiers are broken?

---

## Build Step 18: Blocks

A block is the same loop as `parse_program`, with braces around it, and it is a statement, so it joins the dispatch chain.  The loop stops at `EOF` as well as at `RBRACE`.  That detail is what makes an unclosed block fail in the right place.

```python
# Step 18, parser.py
def parse_block(lexer: Lexer):
    """Consume LBRACE, statements until RBRACE, then RBRACE; return a Block."""
    lb = expect(lexer, "LBRACE")
    stmts = []
    while lexer.peek().type not in ____R6____:
        stmts.append(parse_stmt(lexer))
    expect(lexer, "RBRACE")
    return Block(stmts, lb.line)
```

```python
# Step 18, parser.py: add above the final raise in parse_stmt
    if tok.type == "LBRACE":
        return parse_block(lexer)
```

```python
# Step 18, test_parser.py: add above the main block
def test_nested_blocks_shape():
    tree = parse("let x = 2; { let x = 51; print x; } print x;")
    assert len(tree.stmts) == 3 and isinstance(tree.stmts[1], Block)
    assert len(tree.stmts[1].stmts) == 2
```

Run this check:

```bash
python3 -c "from parser import parse; from ast_nodes import pretty; from check import show_error; print(pretty(parse('let x = 2; { print x; } print x;'))); show_error(parse, '{ print x;')"
```

You should see:

```text
Program
  Let x
    Num(2)
  Block
    Print
      Var(x)
  Print
    Var(x)
ParseError at line 1, col 11: expected RBRACE, found EOF
```

> **CTQ B18** CTQ 3.12 asked what Model 3's `parse_block` does on a missing `}`.  Its loop stops only at `RBRACE`.  Which message does that loop give, and why does `expected RBRACE, found EOF` serve a programmer better?

---

## Build Step 19: `while`

CTQ 1.3 added a `while` with parentheses around its condition.  This grammar has none: `while_stmt ::= WHILE expr block`.  The block's opening brace is what tells the parser the condition has ended.

```python
# Step 19, parser.py
def parse_while_stmt(lexer: Lexer):
    """Consume WHILE, a condition, and a block; return a While."""
    while_tok = expect(lexer, "WHILE")
    condition = ____R7____
    body = ____R8____
    return While(condition, body, while_tok.line)
```

**You write:** the dispatch for `WHILE` in `parse_stmt`, above the `raise`.

Run this check:

```bash
python3 -c "from parser import parse; from ast_nodes import pretty; from check import show_error; print(pretty(parse('while x { print x; x = 1; }'))); show_error(parse, 'while (x) { }')"
```

You should see:

```text
Program
  While
    Var(x)
    Block
      Print
        Var(x)
      Assign x
        Num(1)
ParseError at line 1, col 7: expected an expression, found LPAREN
```

> **CTQ B19** `while (x) { }` fails now, with your stand-in for expressions.  Predict what it does after Stage 3 gives `parse_primary` its parenthesis case, without any change to `parse_while_stmt`.

---

## Build Step 20: `if`, `else`, and `else if`

This is the one place in the statement grammar where a token after a keyword chooses between two productions: after `ELSE`, one more peek tells an `else if` from a plain `else`.  An `else if` is not a new node.  It is an `If` sitting in the outer `If`'s `else_branch`, so the recursion handles a chain of any length.

```python
# Step 20, parser.py
def parse_if_stmt(lexer: Lexer):
    """Consume IF, a condition, and a block; peek for ELSE, then an else-if or a block."""
    if_tok = expect(lexer, "IF")
    condition = parse_expr(lexer)
    then_branch = parse_block(lexer)
    else_branch = None
    if lexer.peek().type == "ELSE":
        lexer.advance()
        if lexer.peek().type == "IF":
            else_branch = ____R9____
        else:
            else_branch = parse_block(lexer)
    return If(condition, then_branch, else_branch, if_tok.line)
```

```python
# Step 20, parser.py: add above the final raise in parse_stmt
    if tok.type == "IF":
        return parse_if_stmt(lexer)
```

```python
# Step 20, test_parser.py: add above the main block
def test_else_if_chain():
    outer = parse("if a { print 1; } else if b { print 2; } else { print 3; }").stmts[0]
    assert isinstance(outer.else_branch, If)
    assert isinstance(outer.else_branch.else_branch, Block)


def test_dangling_else_attaches_to_nearest_if():
    outer = parse("if a { if b { print 1; } else { print 2; } }").stmts[0]
    assert outer.else_branch is None
    assert isinstance(outer.then_branch.stmts[0].else_branch, Block)
```

Run this check:

```bash
python3 -c "from parser import parse; from ast_nodes import pretty; print(pretty(parse('if a { print 1; } else if b { } else { print 3; }')))"
```

You should see:

```text
Program
  If
    Var(a)
    Block
      Print
        Num(1)
    Else
      If
        Var(b)
        Block
        Else
          Block
            Print
              Num(3)
```

> **CTQ B20** Trace `parse_if_stmt` on the program in `test_dangling_else_attaches_to_nearest_if`, and write down which call is running when the parser reaches `else`.  State your rule and how the parser enforces it, in your own words.  The Answer Key leaves this one out.

---

## Build Step 21: `break` and `continue`

A language with loops usually wants `break` and `continue`, so add them now.  Your lexer needs `BREAK` and `CONTINUE` tokens, listed before `IDENT` like every other keyword.  Without them, `break` lexes as a name and `parse_stmt` treats it as the start of an assignment.

```python
# Step 21, parser.py
def parse_break_stmt(lexer: Lexer):
    """Consume BREAK and SEMICOLON; return a Break."""
    tok = expect(lexer, "BREAK")
    expect(lexer, "SEMICOLON")
    return Break(tok.line)
```

```python
# Step 21, parser.py: add above the final raise in parse_stmt
    if tok.type == "BREAK":
        return parse_break_stmt(lexer)
```

```python
# Step 21, test_parser.py: add above the main block
def test_break_continue():
    body = parse("while x { break; continue; }").stmts[0].body.stmts
    assert len(body) == 2 and isinstance(body[0], Break)
    assert isinstance(body[1], Continue)
```

**You write:** `parse_continue_stmt` and its dispatch.

Run this check:

```bash
python3 -c "from parser import parse; print(parse('while x { break; continue; }'))"
```

You should see:

```text
Program(stmts=[While(condition=Var(name='x', line=1, col=7), body=Block(stmts=[Break(line=1), Continue(line=1)], line=1), line=1)])
```

> **CTQ B21** The parser accepts `break;` outside any loop.  Is that a syntax error or a meaning error?  Which phase should report it, and what field on `Break` will it use?

---

## Build Step 22: Errors Across the Whole Statement Grammar

Stage 2 ends with no new parser code.  These tests pin down the error behavior you have built, including a line number other than 1, which exercises your lexer's line counting too.  The worked `while` program has to wait for Stage 3, because its condition uses `>`.

```python
# Step 22, test_parser.py: add above the main block
def test_unclosed_block():
    assert "expected RBRACE, found EOF" in parse_error("while x { print x;").message


def test_error_position_on_later_line():
    err = parse_error("let x = 1;\nlet y = ;")
    assert (err.line, err.col) == (2, 9)
    assert err.found == "SEMICOLON"
```

**You write:** two broken programs of your own.  Run each through `show_error(parse, ...)` and decide whether its message passes your 2 AM standard.  A good parser's messages all pass this test.

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
9 passed, 0 failed
```

> **CTQ B22** `let y = ;` reports the semicolon, on line 2, column 9.  No line of `parse_let_stmt` mentions an expression error.  Follow the calls from `parse_let_stmt` down, and name the line that raised it.

**Stage 2 is done.**  Your parser reads every statement form, as long as every expression is one number or one name.  Stage 3 replaces the stand-in: go on to Part V of [Parsing Expressions](https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374-Fall2026/gh-pages/_pages/Activities/liascript-parsingexpressions.md), Build Step 23.

---

**Up next:** the *Parsing Expressions and Table-Driven Parsing* activity turns this same machinery loose on the full operator-precedence ladder, then drives the same grammar bottom-up from an LR table; together, the statement parser from today and the expression parser you build there make a complete hand-written parser.

# Answer Key

Try each blank and each piece marked **You write** before you read these.  Reading an answer first turns the step into transcription.  The checks on the slides tell you whether your own version works, so a different version that passes is fine.

### Stage 2, Build Steps 10 to 22: Blanks and Pieces You Write

- **R1** (Step 10): `f"expected {expected}, found {found}"`
- **R2** (Step 11): `token_type`
- **R3** (Step 11): `lexer.advance()`
- **R4** (Step 13): `parse_expr(lexer)`
- **R5** (Step 16): `"EOF"`
- **R6** (Step 18): `("RBRACE", "EOF")`
- **R7** (Step 19): `parse_expr(lexer)`
- **R8** (Step 19): `parse_block(lexer)`
- **R9** (Step 20): `parse_if_stmt(lexer)`

**Step 12.**

```python
# Step 12 answer, parser.py: add above the final raise in parse_primary
    if tok.type == "IDENT":
        lexer.advance()
        return Var(tok.value, tok.line, tok.col)
```

**Step 14.**

```python
# Step 14 answer, parser.py
def parse_assign_stmt(lexer: Lexer):
    """Consume IDENT EQ, an expression, and SEMICOLON; return an Assign."""
    name = expect(lexer, "IDENT")
    expect(lexer, "EQ")
    value = parse_expr(lexer)
    expect(lexer, "SEMICOLON")
    return Assign(name.value, value, name.line, name.col)
```

**Step 17.**

```python
# Step 17 answer, test_parser.py: add above the main block
def test_missing_semicolon():
    err = parse_error("let x = 5")
    assert "expected SEMICOLON, found EOF" in err.message
    assert (err.line, err.col) == (1, 10)


def test_bare_equals():
    err = parse_error("= 5;")
    assert "expected a statement, found EQ" in err.message
    assert (err.line, err.col) == (1, 1)
```

**Step 19.**

```python
# Step 19 answer, parser.py: add above the final raise in parse_stmt
    if tok.type == "WHILE":
        return parse_while_stmt(lexer)
```

**Step 21.**

```python
# Step 21 answer, parser.py
def parse_continue_stmt(lexer: Lexer):
    """Consume CONTINUE and SEMICOLON; return a Continue."""
    tok = expect(lexer, "CONTINUE")
    expect(lexer, "SEMICOLON")
    return Continue(tok.line)
```

```python
# Step 21 answer, parser.py: add above the final raise in parse_stmt
    if tok.type == "CONTINUE":
        return parse_continue_stmt(lexer)
```

### Stage 2: The Questions

**CTQ B10.**  With Model 2's error, a test has to search the message text for the number, which breaks as soon as the wording changes.  With `ParseError`, it reads `err.col`.

**CTQ B11.**  It raises `LexError`.  The parser would then report some syntax errors as `LexError` and others as `ParseError`, and a caller would have to catch both, even though a wrong token is a parsing problem and not a lexing one.

**CTQ B12.**  Column 3.  The first `;` is the mistake, but it is already gone, so the error describes the token after it.

**CTQ B13.**  Model 2 names what it expected, what it found, and the line.  The column is new.

**CTQ B14.**  Moving it would work only if every caller remembered to do it, and `if` and `while` take no semicolon, so the caller would have to know which form it called.  One function per production keeps that knowledge beside the rule it belongs to.

**CTQ B15.**  `parse_stmt` raised the error for `= 5;`, because no alternative starts with `EQ`.  `expect` raised the error for `x 1;`, from inside `parse_assign_stmt`, after `parse_stmt` had already chosen.

**CTQ B16.**  Only the token specification changed.  It maps the characters `:=` to the same token type, `EQ`, so no function in `parser.py` had to know.

**CTQ B17.**  One failure would hide every test after it, so you would fix one problem per run and never see the whole picture of what is broken.

**CTQ B18.**  It treats `EOF` as the start of another statement, so `parse_stmt` reports `expected a statement, got EOF('')`.  That names a symptom.  `expected RBRACE, found EOF` names what the programmer forgot.

**CTQ B19.**  It parses.  The parentheses become a parenthesized primary inside the condition, and the tree holds only `Var(x)`, so the program is the same as `while x { }`.

**CTQ B21.**  It is a meaning error: the sentence is well formed, and only its context is wrong.  The evaluator or a later check reports it, using `Break.line`.

**CTQ B22.**  `parse_let_stmt` calls `parse_expr`, which calls `parse_primary`, and the final `raise` in `parse_primary` raises it.
