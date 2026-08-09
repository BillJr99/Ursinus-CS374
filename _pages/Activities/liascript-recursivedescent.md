<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://github.com/BillJr99/Ursinus-CS374-Fall2026/blob/gh-pages/_pages/Activities/liascript-recursivedescent.md or locally via https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374/gh-pages/_pages/Activities/liascript-recursivedescent.md

import: https://raw.githubusercontent.com/liascript/CodeRunner/master/README.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

# Recursive Descent Parsing: From Grammar to Code

## Learning Goals

By the end of this activity, you will be able to:

- Translate each BNF/EBNF grammar production mechanically into a corresponding Python parsing function
- Implement the `peek`/`advance` token-consumption pattern and explain why one token of lookahead suffices for LL(1) grammars
- Identify left recursion in a grammar and rewrite the affected production as an iterative loop
- Construct a working recursive descent parser for a statement-level grammar including assignments, conditionals, and while loops
- Produce informative error messages by detecting and reporting unexpected tokens at each parsing decision point

The parser is where the grammar becomes a program, and **recursive descent** is the technique that makes the translation nearly mechanical: **one function per nonterminal**, where each function's body mirrors its production's right-hand side. Over two days we learn the mapping, meet its one famous landmine (left recursion), and parse real statements. The arc: **the grammar-to-code mapping $\rightarrow$ a working statement parser $\rightarrow$ left recursion and lookahead $\rightarrow$ error messages worth reading**. In the *Abstract Syntax Trees* activity you designed the trees a parser should build; today you build the machine that produces them.

---

## Before You Begin

> **Prerequisites — make sure you are comfortable with these before proceeding:**
>
> - **EBNF/BNF Grammars** — you need to read a grammar and trace derivations. Review: [Syntax and BNF/EBNF Activity](https://liascript.github.io/course/?https://github.com/BillJr99/Ursinus-CS374-Fall2026/blob/gh-pages/_pages/Activities/liascript-syntaxbnf.md)
> - **Abstract Syntax Trees (ASTs)** — you need to understand what the parser is building. Review: [AST Activity](https://liascript.github.io/course/?https://github.com/BillJr99/Ursinus-CS374-Fall2026/blob/gh-pages/_pages/Activities/liascript-ast.md)
>
> **Why this matters:** Recursive descent is the technique you will use to write the parser for your final project. Every grammar rule you write will directly become a Python function using the pattern below. Master this pattern and the rest of the parser writes itself.

---

## The Core Mapping Rule

> **The one rule that unlocks everything:**
>
> Every grammar rule becomes **exactly one Python function**. The function's body is a direct, mechanical translation of the production's right-hand side.
>
> ```
> Rule:  expr → term ( ('+' | '-') term )*
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
> | Terminal `'t'` | `expect('t')` — verify and consume the token |
> | Alternation `X \| Y` | `if/elif` on the next token to choose a branch |
> | EBNF optional `[ X ]` | `if` the next token begins `X`, parse it |
> | EBNF repetition `{ X }` | `while` the next token begins `X`, parse it |
>
> You will use this table constantly. Bookmark it.

---

## Directions and Group Roles

Work in your POGIL team with rotated roles (**Manager**, **Recorder**, **Presenter**, **Reflector**). Consider each model and question individually first, then discuss with your group. The Recorder posts answers to the Class Activity Questions discussion board; the Presenter reports out areas of disagreement or alternative approaches. After class, respond to the reflective prompt individually in your notebook.

---

# Part I: The Mapping (Day 1)

## 1. One Nonterminal, One Function

The parser drives the lexer through exactly two operations: `peek()` (look at the next token without consuming) and `advance()` (consume it). A grammar is **LL(1)**, parseable by this technique with one token of lookahead, when every alternation can be decided by peeking at a single token; the grammars we write for your project are designed to be LL(1) on purpose.

---

## How the Mapping Works: A Worked Example

Let's take a concrete expression grammar and trace exactly how each production becomes a function. This is the same transformation you will perform for every grammar rule in your project.

**Step 0 — Start with the grammar:**

```
expr   → term  ( ('+' | '-') term  )*
term   → factor ( ('*' | '/') factor )*
factor → NUMBER | '(' expr ')'
```

**Step 1 — Each nonterminal becomes a function skeleton:**

```
def parse_expr():   ...   # handles expr
def parse_term():   ...   # handles term
def parse_factor(): ...   # handles factor
```

**Step 2 — Fill in each rule mechanically:**

`expr → term ( ('+' | '-') term )*`
- Start with one `term` → call `parse_term()`
- The `(...)* ` is EBNF repetition → use a `while` loop
- Inside the loop, the alternation `'+' | '-'` → `if peek() in ('+', '-')`

```
def parse_expr():
    node = parse_term()          # parse the first term
    while peek() in ('+', '-'): # repetition: { ... }
        op = advance()           # consume '+' or '-'
        right = parse_term()     # parse the next term
        node = (op, node, right) # fold left: build the tree
    return node
```

**Step 3 — Do the same for `term → factor ( ('*' | '/') factor )*`:**

```
def parse_term():
    node = parse_factor()
    while peek() in ('*', '/'):
        op = advance()
        right = parse_factor()
        node = (op, node, right)
    return node
```

**Step 4 — For `factor → NUMBER | '(' expr ')'`, the alternation uses lookahead:**

```
def parse_factor():
    if peek() is a NUMBER:
        return ('num', advance())
    elif peek() == '(':
        advance()          # consume '('
        node = parse_expr()
        expect(')')        # consume ')'
        return node
    else:
        raise SyntaxError(...)
```

**Key insight:** Notice that `parse_expr` calls `parse_term`, which calls `parse_factor`, which can call back to `parse_expr` (via the parenthesized subexpression). This is the **recursive** part of "recursive descent" — the mutual recursion between functions mirrors the nesting in the grammar.

### Worked Example: `1 + 2 * 3` on the full ladder, with the tree

The Practice section later traces `1 + 2` on a one-level grammar, where precedence never comes up. This is the one that matters: `1 + 2 * 3` on the full `expr / term / factor` ladder, where the answer must be 7 and not 9.

Grammar:

```
expr   -> term { ('+' | '-') term }
term   -> factor { ('*' | '/') factor }
factor -> NUMBER | '(' expr ')'
```

Indentation shows the call stack. `pos` is the index of the next unconsumed token; tokens are `1 + 2 * 3`.

```
call parse_expr()                      pos=0
  call parse_term()                    pos=0
    call parse_factor()                pos=0
      peek()=NUMBER(1) -> consume      pos=1
      return ('num', 1)
    peek()='+' -> not * or /, loop does NOT run
    return ('num', 1)                  <- term returns the bare 1
  peek()='+' -> loop RUNS
  consume '+'                          pos=2
  call parse_term()                    pos=2
    call parse_factor()                pos=2
      peek()=NUMBER(2) -> consume      pos=3
      return ('num', 2)
    peek()='*' -> loop RUNS
    consume '*'                        pos=4
    call parse_factor()                pos=4
      peek()=NUMBER(3) -> consume      pos=5
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

**Where precedence actually happened.** Look at the two `peek()='+' `lines. The *first* one is inside `parse_term`, and `+` is not in `term`'s operator set, so `term` returns immediately with just `1`. The `+` is left on the input for `parse_expr` to handle. The `*`, by contrast, *is* in `term`'s set, so the second `parse_term` call consumes it and builds the product before returning.

That is the whole mechanism: **`term` gets first refusal on every operator, and it only accepts the tight ones.** The `*` node is finished and returned before the `+` node is ever constructed, so `*` ends up deeper in the tree — and deeper means evaluated first. Nothing in the code says "multiplication has higher precedence." The grammar's layering says it, and the call stack enacts it.

Compare this against the LR table you will build in the *Table-Driven and LR Parsing* activity: there, the same decision lives in one cell of a table (shift on `*`, reduce on `+`). Here it lives in which function's loop is willing to consume which token. Same precedence, two completely different places to look for it.


---

## Model 1: Translate by Hand

Grammar fragment (statements for a small language):

```
stmt     -> printstmt | letstmt
printstmt -> "print" expr ";"
letstmt   -> "let" IDENT "=" expr ";"
```

> **Intuition:** The parser's job is to look at the current token and decide which rule to apply. For `stmt`, there are two choices: if the current token is `print`, take the `printstmt` path; if it's `let`, take the `letstmt` path. This single-token decision is called **lookahead**. Each path then consumes tokens in the exact order the grammar specifies — this is the "descent" part.

### Critical Thinking Questions

> **CTQ 1.1** Using the translation table, write pseudocode for `parse_stmt`, `parse_printstmt`, and `parse_letstmt`. Which single token decides the alternation in `parse_stmt`?

> **CTQ 1.2** What should `expect(SEMI)` do when the next token is not a semicolon? Write the error message you would want at 2 AM, including what it should contain (expected what, found what, where).

> **CTQ 1.3** Add `whilestmt -> "while" "(" expr ")" block` to the grammar and to your pseudocode. Did the alternation in `parse_stmt` remain decidable by one token? What property of the three statement keywords makes it so?

---

## Model 2: Read the Parser

> **Intuition:** The code cell below is a near-mechanical translation of the grammar from Model 1. Before reading it, predict what you'll see: three functions (`parse_stmt`, `parse_printstmt`, `parse_letstmt`), each consuming tokens in the order the grammar says. The `parse_expr` at the bottom is a **stub** — it only handles numbers and identifiers; the full expression ladder comes in a later module. Notice how the tuple return values (`("print", value)`, `("let", name, value)`) are the roots of little AST subtrees.

```python  liascript
# A recursive descent parser for the statement grammar, atop the class lexer.
# Each function is one production; read them side by side with the grammar.

class Token:
    def __init__(self, type_, lexeme, line=1):
        self.type = type_; self.lexeme = lexeme; self.line = line
    def __repr__(self): return f"Token({self.type}, {self.lexeme!r})"

import re

TOKEN_RE = re.compile(
    r'(?P<KEYWORD>print|let)\b|'
    r'(?P<NUMBER>\d+(?:\.\d*)?)|'
    r'(?P<IDENT>[A-Za-z_]\w*)|'
    r'(?P<SEMI>;)|'
    r'(?P<ASSIGN>=)|'
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
        self.expect("SEMI")
        return ("print", value)

    # letstmt -> "let" IDENT "=" expr ";"
    def parse_letstmt(self):
        self.expect("KEYWORD")              # let
        name = self.expect("IDENT").lexeme
        self.expect("ASSIGN")
        value = self.parse_expr()
        self.expect("SEMI")
        return ("let", name, value)

    # expr -> NUMBER | IDENT     (a stub; the full ladder arrives next module)
    def parse_expr(self):
        tok = self.peek()
        if tok and tok.type in ("NUMBER", "IDENT"):
            self.advance()
            return ("num", float(tok.lexeme)) if tok.type == "NUMBER" else ("var", tok.lexeme)
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
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

### Critical Thinking Questions

> **CTQ 2.4** Annotate each parser method with the production it implements (the comments start you off). Where does the sequence rule become consecutive calls? Where does alternation become an `if`?

> **CTQ 2.5** The parser returns tuples like `("let", "x", ("num", 7.0))`. You have been told the parser builds a tree; where is the tree? Identify the nesting, and connect these tuples back to the node shapes from the *Abstract Syntax Trees* activity.

> **CTQ 2.6** Run the failing case `let x 7;` and read the error. Which `expect` fired, and does the message satisfy your 2 AM standard from CTQ 1.2? Improve one message.

---

# Part II: The Landmine and the Lookahead (Day 2)

## 2. Left Recursion Kills Descent

> **Watch out! Left recursion will infinite-loop your parser.**
>
> The grammar `E → E + T | T` is **left-recursive**: `parse_E` calls `parse_E` as its very first action, before consuming any input. This causes infinite recursion and a stack overflow.
>
> **Transform it to:** `E → T E'` where `E' → + T E' | ε`
>
> Or equivalently in EBNF (which is what we use in practice): `E → T { '+' T }`
>
> The EBNF version uses a `while` loop in code — no recursion, no infinite loop, same left-associative tree.
>
> **The rule:** If your grammar has `A → A something`, rewrite it as `A → something { something }`.

Recall the expression ladder's rule `E -> E + T | T`. Translate it naively: `parse_E` immediately calls `parse_E`, which immediately calls `parse_E`... infinite recursion before consuming a single token. **Left-recursive productions cannot be parsed by recursive descent directly.** The standard repair converts left recursion into EBNF repetition, which the translation table turns into a loop:

$$
E \rightarrow E + T \mid T \quad \Longrightarrow \quad E \rightarrow T \; \{ + \; T \}
$$

The two grammars accept the same strings; the loop version builds the *same left-leaning tree* if your loop folds as it goes (next module makes this concrete). Likewise **left factoring** repairs alternations that share a prefix: `A -> xy | xz` becomes `A -> x (y | z)`, restoring one-token decidability.

> **Watch out! Lookahead and grammar design are linked.**
>
> Most recursive descent parsers only look at the **current token** to decide which rule to apply. This is called **LL(1)** — "Left-to-right scan, Leftmost derivation, 1 token of lookahead."
>
> If your grammar requires looking 2+ tokens ahead, your grammar probably needs refactoring, not your parser. For example, a grammar like `stmt → IDENT '=' expr | IDENT '(' args ')'` requires seeing the token *after* the IDENT to decide which rule to use. The fix is usually to left-factor: `stmt → IDENT stmt_tail` where `stmt_tail → '=' expr | '(' args ')'`.
>
> **The rule:** If you find yourself writing `peek_ahead(2)`, refactor the grammar first.

[[MC]]
A teammate's `parse_expr` overflows the call stack instantly on any input. Without seeing the code, the most likely diagnosis from today is:
- ( ) The lexer returned too many tokens
- (x) A left-recursive production was translated directly, so the function recurses before consuming input
- ( ) The grammar is ambiguous
- ( ) Python's recursion limit is too small for parsing

---

## 3. Exercises

1. *Extend the statement set.* Add `whilestmt` and a brace-delimited `block -> "{" { stmt } "}"` to the parser, following the table mechanically. Demonstrate on a two-statement loop body, and show the nested tuple structure you get.
2. *Repair drill.* Rewrite each as descent-ready EBNF: `L -> L "," x | x` (comma lists) and `S -> "if" E "then" S | "if" E "then" S "else" S | other` (left factor the shared prefix). State which repair was which.
3. *Error olympics.* Construct five syntactically broken inputs and grade your parser's messages A through F on the 2 AM standard. Fix the worst one and show before and after.
4. *Lookahead limits.* Invent a tiny grammar where one token of lookahead cannot decide an alternation but two tokens can. What would `peek(2)` cost, and why do language designers prefer to redesign the grammar instead?

---

## Practice — Parser Tracing: Hand-Simulate a Descent Parser

These exercises build confidence in the grammar-to-code mapping and the call structure of a recursive descent parser by hand-simulating the exact sequence of function calls and token consumption. They prepare you for the parser assignment by showing the execution you will later trace in a debugger.

> *Exercises adapted from the recursive descent parsing technique covered in standard compiler texts, including Douglas Thain's *Introduction to Compilers and Language Design* (Chapter 4).*

[[MC]]
A recursive descent parser for `expr → term { '+' term }` will call `parse_term()` how many times for input `1 + 2 + 3`?
- ( ) Once (parse_term is called one time total)
- ( ) Twice (once per `+` operator)
- (x) Three times (one for each number in the sum)
- ( ) Unboundedly many (until end of input)

[[MC]]
When parsing a statement like `if ( cond ) stmt`, the parser's call sequence is:
- ( ) `parse_if_stmt()` → `parse_cond()` → `parse_stmt()`
- ( ) `parse_stmt()` → `parse_cond()` → `parse_if_stmt()`
- (x) `parse_stmt()` calls `parse_if_stmt()` when it sees `if` at the start; `parse_if_stmt()` then calls `parse_cond()` and `parse_stmt()` for its sub-parts
- ( ) All three functions are called in parallel by the lexer

1. **Hand-trace a parser call stack (simple grammar).**
   
   Grammar:
   ```
   expr → term { '+' term }
   term → INT
   ```
   
   Input tokens: `1 + 2`
   
   Trace the call stack step by step:
   ```
   call parse_expr()
     pos=0, peek()='1'
     call parse_term()
       consume INT('1')
       pos=1, return 1
     pos=1, peek()='+' → loop condition true
     consume '+'
     pos=2, peek()='2'
     call parse_term()
       consume INT('2')
       pos=3, return 3
     pos=3, peek()=EOF → loop condition false
     return tree for (1 + 2)
   ```
   
   Draw the call stack diagram: show which function called which, and in what order tokens were consumed.

2. **Hand-trace a parser with nested alternatives (statement parser).**
   
   Grammar:
   ```
   stmt → 'print' expr | 'let' IDENT '=' expr
   expr → INT
   ```
   
   Input: `let x = 42`
   
   Trace:
   - `parse_stmt()` is called
   - `peek()` is `'let'` → checks first alternative ('print') — fails because lookahead is 'let' not 'print'
   - Checks second alternative ('let') — succeeds because lookahead matches
   - Calls the path for 'let IDENT = expr'
   - Show which function made which token consumption decision
   - Final tree structure (as a tuple or object)

3. **Hand-trace a parser with repetition (zero times).**
   
   Grammar:
   ```
   stmt_list → { stmt }
   stmt → 'print' expr
   expr → INT
   ```
   
   Input: empty (just EOF)
   
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

4. **Understand left-recursion failure (by hand).**
   
   **Bad grammar** (left-recursive):
   ```
   expr → expr '+' term | term
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
   expr → term { '+' term }
   ```
   
   Trace the same input `1`:
   - `parse_expr(0)` calls `parse_term(0)`
   - Token consumed; the while loop condition checks for `+` → not found
   - Loop exits and returns
   
   Explain: why does the fixed version consume a token before recursing, avoiding infinite recursion?

5. **Integration trace: full statement parse.**
   
   Grammar:
   ```
   program → stmt*
   stmt → 'let' IDENT '=' expr ';'
   expr → INT { '+' INT }
   ```
   
   Input: `let x = 1 + 2 ;`
   
   Produce a full execution trace showing:
   - Every function call (in order)
   - Every token consumed (and the position after)
   - The resulting AST tree (as nested tuples or objects)
   - Annotations explaining *why* each function was called (e.g., "called because stmt starts with 'let'")

---

# Part III: Runnable Models (Day 2, continued)

## Model 3: Complete Recursive Descent Parser

> **Intuition:** The code cell below is a **self-contained recursive descent parser** — it includes its own tokenizer (lexer) and parser together, with no external dependencies. The grammar it parses supports variable assignments, `if`/`while` statements, arithmetic with full precedence (`*` and `/` bind tighter than `+` and `-`), and `print`. Read the parser functions top-to-bottom and notice that the call graph between functions exactly mirrors the grammar's nesting. The `parse_expr` → `parse_term` → `parse_factor` chain is how precedence is encoded: deeper in the call stack = higher precedence.

The code cell below is a **self-contained recursive descent parser** for a mini-language that includes: variable assignments, `if`/`while` statements, arithmetic expressions with full precedence (add/subtract at one level, multiply/divide at a higher level), and `print`. It tokenizes its own input so you can run it immediately, then parses a short multi-statement program and prints the resulting AST as nested tuples.

```python  liascript
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
#   factor   -> NUMBER | IDENT | "(" expr ")"

import re

# ── Lexer ────────────────────────────────────────────────────────────────────

TOKEN_RE = re.compile(
    r'(?P<FLOAT>\d+\.\d*|\.\d+)|'
    r'(?P<NUMBER>\d+)|'
    r'(?P<KEYWORD>if|while|print)\b|'
    r'(?P<IDENT>[A-Za-z_]\w*)|'
    r'(?P<LBRACE>\{)|(?P<RBRACE>\})|'
    r'(?P<LPAREN>\()|(?P<RPAREN>\))|'
    r'(?P<SEMI>;)|'
    r'(?P<ASSIGN>=)|'
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

# ── Parser ───────────────────────────────────────────────────────────────────

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
        self.expect("SEMI")
        return ("print", val)

    def parse_assign(self):
        name = self.expect("IDENT").lexeme
        self.expect("ASSIGN")
        val = self.parse_expr()
        self.expect("SEMI")
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

    # factor -> NUMBER | IDENT | "(" expr ")"
    def parse_factor(self):
        if self.match("NUMBER") or self.match("FLOAT"):
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

# ── Demo program ─────────────────────────────────────────────────────────────

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
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

### Critical Thinking Questions

> **CTQ 3.11** The parser uses two levels for expressions (`parse_expr` and `parse_term`) with `ADDOP` handled at the outer level and `MULOP` at the inner. Trace the parsing of `2 + 3 * 4` and show which node becomes the left child versus the right child of `+`. How does this level structure enforce precedence?

> **CTQ 3.12** `parse_block` loops `while not self.match("RBRACE")`. What happens if the programmer forgets a closing `}`? Write the exact error message the parser would produce, and explain which line of the parser generates it.

> **CTQ 3.13** The AST for `x = x - 1` is `('assign', 'x', ('-', ('var', 'x'), ('num', 1.0)))`. A later "interpreter" pass walks this tree. Write pseudocode for `eval_node` that handles `num`, `var`, `assign`, and `-` nodes, using a dict called `env` as the store.

> **CTQ 3.14** Add a `letstmt` production (`let IDENT = expr ;`) to the grammar and to the parser above. How many lines change? What single token in `parse_stmt`'s lookahead decides between `assign` (which also starts with an IDENT) and the new `let`?

---

## Model 4: Mini Calculator Language — Lexer, Parser, and Evaluator Together

> **Intuition:** This is the payoff. The calculator language has only five kinds of tokens — numbers, `+`, `*`, `(`, `)` — and three grammar rules. Yet it is already a complete language implementation: the lexer breaks input into tokens, the parser turns tokens into an AST, and the evaluator walks the AST to compute the answer. Everything you need to build a language for your final project follows this same three-layer pattern, just with more rules.
>
> Read this code as a template: swap in your own token types, your own grammar rules, and your own evaluator actions, and you have your project's core.

```python  liascript
# Mini calculator: a complete language implementation in ~80 lines.
#
# Grammar:
#   expr   -> term   { ('+' | '-') term   }
#   term   -> factor { ('*' | '/') factor }
#   factor -> NUMBER | '(' expr ')'
#
# Example runs:
#   calc("2 + 3")        -> 5.0
#   calc("2 + 3 * 4")    -> 14.0   (not 20: * binds tighter)
#   calc("(2 + 3) * 4")  -> 20.0
#   calc("10 / 2 - 1")   -> 4.0

import re

# ── Layer 1: Lexer ────────────────────────────────────────────────────────────
# Intuition: break the input string into meaningful chunks.
# We use a list of regex patterns and try each one at the current position.

CALC_RE = re.compile(
    r'(?P<NUMBER>\d+(?:\.\d*)?)|'   # integer or decimal
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

# ── Layer 2: Parser ───────────────────────────────────────────────────────────
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

    # factor -> NUMBER | '(' expr ')'
    def parse_factor(self):
        tok = self.peek()
        if tok.type == "NUMBER":
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

# ── Layer 3: Evaluator ────────────────────────────────────────────────────────
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

# ── Convenience wrapper ────────────────────────────────────────────────────────

def calc(src):
    """Parse and evaluate a calculator expression string."""
    ast = CalcParser(src).parse()
    return evaluate(ast)

# ── Test suite ────────────────────────────────────────────────────────────────

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

# ── Show the AST for one expression ──────────────────────────────────────────

print()
print("AST for '2 + 3 * 4':")
import pprint
pprint.pprint(CalcParser("2 + 3 * 4").parse())
print()
print("Notice: * node is nested DEEPER than + node,")
print("meaning * is evaluated first -- this is how precedence is encoded in the tree.")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

### Critical Thinking Questions

> **CTQ 4.15** The evaluator uses `evaluate(left)` and `evaluate(right)` recursively. What is the base case that stops the recursion? What happens if you have a deeply nested expression like `((((1 + 2))))`?

> **CTQ 4.16** The grammar has two levels (`expr` and `term`) to encode that `*` binds tighter than `+`. Add a third level `power` for `**` (exponentiation, right-associative) with the highest precedence. Write the grammar rule and the `parse_power` function. Should the loop fold left or right?

> **CTQ 4.17** The test case `"2 + 3 * 4"` returns `14.0`, not `20.0`. Trace the call sequence starting from `parse_expr()` and show exactly which functions are called and in what order. At which point does the parser "decide" that `3 * 4` groups together before `2 +`?

> **CTQ 4.18** Extend the evaluator to support variables: add a `let x = expr` statement form (semicolon-terminated), a `dict` called `env`, and a `("var", name)` node type that looks up `name` in `env`. Show the extended grammar, the new parser function, and the new evaluator case.

---

---
**🛑 In-class work stops here.** Everything below is homework and going-deeper material — attempt the exercises before the related assignment.

## Going Deeper (Optional Pointers)

> **Going further:** the extra complete parsers that used to live here are best replaced by one polished pipeline: the dedicated tutorial [Build an Interpreter](https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374/gh-pages/_pages/Tutorials/tutorial-build-an-interpreter.md) contains a complete recursive-descent parser (Stage 3) wired into a lexer and evaluator. The error-*recovering* parser that reports several syntax errors in one run by synchronizing at statement boundaries is a self-study topic — keywords: "panic-mode error recovery," "synchronization points," and the "Synchronizing a recursive descent parser" section of *Crafting Interpreters* — and makes a strong Parser-assignment stretch goal.

---

## 4. Further Reading

- Douglas Thain. *Introduction to Compilers and Language Design*, Chapter 4.
- Robert Nystrom. *Crafting Interpreters*, "Parsing Expressions" (online).
- Wirth, Niklaus. *Compiler Construction* (online), the classic minimalist treatment.

---

## Reflection Prompt

In your notebook: recursive descent works because the code's shape *is* the grammar's shape, a rare case of documentation that cannot drift from implementation. Where else have you seen (or wished for) structure and description fused this way?

---

**Up next:** the *Parsing Expressions* activity turns this same machinery loose on the full operator-precedence ladder; together, the statement parser from today and the expression parser you build there form the core of the Parser assignment.
