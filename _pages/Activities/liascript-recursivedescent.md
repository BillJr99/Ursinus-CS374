# Recursive Descent Parsing: From Grammar to Code
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

The parser is where the grammar becomes a program, and **recursive descent** is the technique that makes the translation nearly mechanical: **one function per nonterminal**, where each function's body mirrors its production's right-hand side. Over two days we learn the mapping, meet its one famous landmine (left recursion), and parse real statements. The arc: **the grammar-to-code mapping $\rightarrow$ a working statement parser $\rightarrow$ left recursion and lookahead $\rightarrow$ error messages worth reading**.

---

## Directions and Group Roles

Work in your POGIL team with rotated roles (**Manager**, **Recorder**, **Presenter**, **Reflector**). Consider each model and question individually first, then discuss with your group. The Recorder posts answers to the Class Activity Questions discussion board; the Presenter reports out areas of disagreement or alternative approaches. After class, respond to the reflective prompt individually in your notebook.

---

# Part I: The Mapping (Day 1)

## 1. One Nonterminal, One Function

**The translation table you already half-know** (you built it in the BNF module's recognizer):

| Grammar construct | Code shape |
|-------------------|-----------|
| Nonterminal `A` | Function `parse_A()` |
| Sequence `X Y Z` | Call `parse_X()`, then `parse_Y()`, then `parse_Z()` |
| Terminal `t` | `expect(t)`: verify and consume the token |
| Alternation `X \| Y` | `if` on the next token (lookahead) to choose a branch |
| EBNF optional `[ X ]` | `if` next token begins `X`: parse it |
| EBNF repetition `{ X }` | `while` next token begins `X`: parse it |

The parser drives the lexer through exactly two operations: `peek()` (look at the next token without consuming) and `advance()` (consume it). A grammar is **LL(1)**, parseable by this technique with one token of lookahead, when every alternation can be decided by peeking at a single token; the grammars we write for your project are designed to be LL(1) on purpose.

---

## Model 1: Translate by Hand

Grammar fragment (statements for a small language):

```
stmt     -> printstmt | letstmt
printstmt -> "print" expr ";"
letstmt   -> "let" IDENT "=" expr ";"
```

### Critical Thinking Questions

1. Using the table, write pseudocode for `parse_stmt`, `parse_printstmt`, and `parse_letstmt`. Which single token decides the alternation in `parse_stmt`?
2. What should `expect(SEMI)` do when the next token is not a semicolon? Write the error message you would want at 2 AM, including what it should contain (expected what, found what, where).
3. Add `whilestmt -> "while" "(" expr ")" block` to the grammar and to your pseudocode. Did the alternation in `parse_stmt` remain decidable by one token? What property of the three statement keywords makes it so?

---

## Code Cell

```python
# A recursive descent parser for the statement grammar, atop the class lexer.
# Each function is one production; read them side by side with the grammar.

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
        try:
            tok = self.peek()
            if tok and tok.type == "KEYWORD" and tok.lexeme == "print":
                return self.parse_printstmt()
            if tok and tok.type == "KEYWORD" and tok.lexeme == "let":
                return self.parse_letstmt()
            raise SyntaxError(f"expected a statement, found {tok.lexeme!r} at line {tok.line}" if tok
                              else "expected a statement, found end of input")
        except SyntaxError:
            raise
        except Exception as e:
            print(f"[parser:parse_stmt] {e}")
            import traceback; traceback.print_exc()
            raise

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

# Demo (uses tokenize from the scanning module):
# for source in ["print 42;", "let x = 7;", "let x 7;"]:
#     try:
#         print(source, "->", Parser(tokenize(source)).parse_stmt())
#     except SyntaxError as e:
#         print(source, "-> SyntaxError:", e)
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

---

## Model 2: Read the Parser

### Critical Thinking Questions

4. Annotate each parser method with the production it implements (the comments start you off). Where does the sequence rule become consecutive calls? Where does alternation become an `if`?
5. The parser returns tuples like `("let", "x", ("num", 7.0))`. You have been told the parser builds a tree; where is the tree? Identify the nesting, two modules early.
6. Run the failing case `let x 7;` and read the error. Which `expect` fired, and does the message satisfy your 2 AM standard from question 2? Improve one message.

---

# Part II: The Landmine and the Lookahead (Day 2)

## 2. Left Recursion Kills Descent

Recall the expression ladder's rule `E -> E + T | T`. Translate it naively: `parse_E` immediately calls `parse_E`, which immediately calls `parse_E`... infinite recursion before consuming a single token. **Left-recursive productions cannot be parsed by recursive descent directly.** The standard repair converts left recursion into EBNF repetition, which the translation table turns into a loop:

$$
E \rightarrow E + T \mid T \quad \Longrightarrow \quad E \rightarrow T \; \{ + \; T \}
$$

The two grammars accept the same strings; the loop version builds the *same left-leaning tree* if your loop folds as it goes (next module makes this concrete). Likewise **left factoring** repairs alternations that share a prefix: `A -> xy | xz` becomes `A -> x (y | z)`, restoring one-token decidability.

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

## Reflection Prompt

In your notebook: recursive descent works because the code's shape *is* the grammar's shape, a rare case of documentation that cannot drift from implementation. Where else have you seen (or wished for) structure and description fused this way?

---

# Part III: Runnable Models

## Model 3: Complete Recursive Descent Parser

The code cell below is a **self-contained recursive descent parser** for a mini-language that includes: variable assignments, `if`/`while` statements, arithmetic expressions with full precedence (add/subtract at one level, multiply/divide at a higher level), and `print`. It tokenizes its own input so you can run it immediately, then parses a short multi-statement program and prints the resulting AST as nested tuples.

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

11. The parser uses two levels for expressions (`parse_expr` and `parse_term`) with `ADDOP` handled at the outer level and `MULOP` at the inner. Trace the parsing of `2 + 3 * 4` and show which node becomes the left child versus the right child of `+`. How does this level structure enforce precedence?
12. `parse_block` loops `while not self.match("RBRACE")`. What happens if the programmer forgets a closing `}`? Write the exact error message the parser would produce, and explain which line of the parser generates it.
13. The AST for `x = x - 1` is `('assign', 'x', ('-', ('var', 'x'), ('num', 1.0)))`. A later "interpreter" pass walks this tree. Write pseudocode for `eval_node` that handles `num`, `var`, `assign`, and `-` nodes, using a dict called `env` as the store.
14. Add a `letstmt` production (`let IDENT = expr ;`) to the grammar and to the parser above. How many lines change? What single token in `parse_stmt`'s lookahead decides between `assign` (which also starts with an IDENT) and the new `let`?

---

## Model 4: Error Recovery

Generic "parse error" messages waste everyone's time. This model shows a drop-in replacement for `expect` that reports the exact token mismatch with location, plus a **synchronize** method that skips to the next semicolon or closing brace so the parser can continue and report multiple errors in one run.

```python
# Error-recovering parser shell.  Paste into the Model 3 Parser class
# (or run standalone: it re-tokenizes a broken program).

import re

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
    def __init__(self, type_, lexeme, line, col):
        self.type = type_; self.lexeme = lexeme
        self.line = line; self.col = col
    def __repr__(self): return f"Token({self.type}, {self.lexeme!r}, {self.line}:{self.col})"

def tokenize(src):
    tokens, line, line_start = [], 1, 0
    for m in TOKEN_RE.finditer(src):
        kind = m.lastgroup
        col = m.start() - line_start + 1
        if kind == "WS":
            for ch in m.group():
                if ch == "\n":
                    line += 1; line_start = m.start() + m.group().index(ch) + 1
            continue
        tokens.append(Token(kind, m.group(), line, col))
    tokens.append(Token("EOF", "", line, 0))
    return tokens

class ParseError(Exception):
    pass

class RecoveringParser:
    SYNC_TOKENS = {"SEMI", "RBRACE", "EOF"}

    def __init__(self, src):
        self.tokens = tokenize(src)
        self.pos = 0
        self.errors = []

    def peek(self):
        return self.tokens[self.pos]

    def advance(self):
        tok = self.peek()
        if tok.type != "EOF": self.pos += 1
        return tok

    def expect(self, ttype, lexeme=None):
        tok = self.peek()
        match_type = tok.type == ttype
        match_lex  = (lexeme is None) or (tok.lexeme == lexeme)
        if match_type and match_lex:
            return self.advance()
        want = f"'{lexeme}'" if lexeme else ttype
        got  = f"'{tok.lexeme}'" if tok.lexeme else "end of input"
        msg = (f"line {tok.line}, col {tok.col}: "
               f"expected {want}, got {got} ({tok.type})")
        self.errors.append(msg)
        raise ParseError(msg)

    def synchronize(self):
        """Skip tokens until a likely statement boundary."""
        while self.peek().type not in self.SYNC_TOKENS:
            self.advance()
        if self.peek().type == "SEMI":
            self.advance()   # consume the semicolon

    def parse_assign(self):
        name = self.expect("IDENT").lexeme
        self.expect("ASSIGN")           # will error if missing
        # ... (rest of expression parsing omitted for brevity)
        self.expect("SEMI")
        return ("assign", name)

    def parse_program(self):
        stmts = []
        while self.peek().type != "EOF":
            try:
                tok = self.peek()
                if tok.type == "IDENT":
                    stmts.append(self.parse_assign())
                else:
                    self.errors.append(
                        f"line {tok.line}, col {tok.col}: "
                        f"unexpected token '{tok.lexeme}' ({tok.type})"
                    )
                    self.advance()
            except ParseError:
                self.synchronize()
        return stmts

# ── Test broken programs ──────────────────────────────────────────────────────

broken_programs = [
    "x = 5\ny = 3;",          # missing semicolon after first statement
    "x  5;",                  # missing '='
    "print 2 + ;",            # missing operand
]

for prog in broken_programs:
    p = RecoveringParser(prog)
    p.parse_program()
    if p.errors:
        print(f"Input: {prog!r}")
        for e in p.errors: print(" ", e)
    else:
        print(f"Input: {prog!r} -> no errors")
    print()
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

### Critical Thinking Questions

15. The error message format is `line {line}, col {col}: expected '{want}', got '{got}' ({type})`. Which three pieces of information are most useful for a programmer staring at the broken file at 2 AM? Rank them and justify your ranking.
16. `synchronize` skips to the next `SEMI`, `RBRACE`, or `EOF`. What class of errors will this strategy miss (i.e., never catch), and what class might it report twice? Give a concrete example of each.
17. Change `broken_programs[0]` to `"x = 5 y = 3;"` (no newline, missing semicolon mid-line). Predict the exact error message before running, then verify. What does this reveal about how the parser's location tracking handles implicit line continuation?

---

## Model 5: Left Recursion Elimination

This model shows the transformation in code: first a **broken** parser that uses a left-recursive rule and overflows the stack, then the **repaired** version using a loop, and finally a verification that both produce the same left-leaning tree shape.

```python
# Left recursion demo and elimination.
# Grammar A (left-recursive, BROKEN for recursive descent):
#   E -> E "+" T | T
# Grammar B (repaired with EBNF, safe for recursive descent):
#   E -> T { "+" T }

import sys
sys.setrecursionlimit(50)    # expose the crash quickly; lower than default

# ── Minimal token stream ─────────────────────────────────────────────────────

def lex(src):
    tokens = []
    for ch in src.split():
        if ch.lstrip('-').isdigit():
            tokens.append(("NUM", int(ch)))
        elif ch == '+':
            tokens.append(("PLUS", '+'))
        else:
            tokens.append(("IDENT", ch))
    tokens.append(("EOF", None))
    return tokens

class SimpleParser:
    def __init__(self, src):
        self.tokens = lex(src); self.pos = 0
    def peek(self): return self.tokens[self.pos]
    def advance(self):
        t = self.peek()
        if t[0] != "EOF": self.pos += 1
        return t
    def parse_T(self):
        t = self.advance()
        return ("num", t[1])

# ── Version A: left-recursive (will crash) ──────────────────────────────────

class BrokenParser(SimpleParser):
    def parse_E(self):
        # E -> E "+" T | T   (left-recursive: calls itself before any input)
        left = self.parse_E()             # <-- infinite recursion here
        if self.peek()[0] == "PLUS":
            self.advance()
            right = self.parse_T()
            return ("+", left, right)
        return left

# ── Version B: repaired with EBNF loop ──────────────────────────────────────

class FixedParser(SimpleParser):
    def parse_E(self):
        # E -> T { "+" T }   (no left recursion; builds the same left-leaning tree)
        node = self.parse_T()
        while self.peek()[0] == "PLUS":
            self.advance()
            node = ("+", node, self.parse_T())   # fold left as we go
        return node

# ── Demonstrate ──────────────────────────────────────────────────────────────

print("=== Broken parser (expect RecursionError) ===")
try:
    BrokenParser("1 + 2 + 3").parse_E()
except RecursionError as e:
    print("RecursionError: left-recursive parse_E() called itself before consuming input")

print()
print("=== Fixed parser (EBNF loop) ===")
for src in ["1 + 2", "1 + 2 + 3", "1 + 2 + 3 + 4"]:
    tree = FixedParser(src).parse_E()
    print(f"  {src!r:18} -> {tree}")

# Expected tree for "1 + 2 + 3":
# ('+', ('+', ('num', 1), ('num', 2)), ('num', 3))
# Note the left-leaning structure: (1+2) computed first, as left-assoc demands.
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

### Critical Thinking Questions

18. The repaired parser builds `('+', ('+', ('num', 1), ('num', 2)), ('num', 3))` for `1 + 2 + 3`. Draw this tree. Which subtree corresponds to "1 + 2" and which to the final `+ 3`? How does the tree structure encode left-associativity?
19. The same transformation applies to right-recursive grammars like `E -> T "**" E | T` (right-associative exponentiation). Rewrite it in EBNF. Should the loop fold left or right to preserve right-associativity? Show the tree for `2 ** 3 ** 4`.
20. `sys.setrecursionlimit(50)` makes the crash happen on a short input. What would happen without this limit if the input had 100 `+` operators? Relate this to why grammar designers avoid left recursion rather than just increasing the recursion limit.

---

## 4. Further Reading

- Douglas Thain. *Introduction to Compilers and Language Design*, Chapter 4.
- Robert Nystrom. *Crafting Interpreters*, "Parsing Expressions" (online).
- Wirth, Niklaus. *Compiler Construction* (online), the classic minimalist treatment.
