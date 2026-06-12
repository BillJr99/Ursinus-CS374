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

## 4. Further Reading

- Douglas Thain. *Introduction to Compilers and Language Design*, Chapter 4.
- Robert Nystrom. *Crafting Interpreters*, "Parsing Expressions" (online).
- Wirth, Niklaus. *Compiler Construction* (online), the classic minimalist treatment.
