# Building Your Language: A Complete Step-by-Step Guide

<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://github.com/BillJr99/Ursinus-CS374-Fall2026/blob/main/_pages/Tutorials/tutorial-project-language-guide.md

import: https://raw.githubusercontent.com/liascript/CodeRunner/master/README.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

# Building Your Language: A Complete Step-by-Step Guide

This tutorial walks you through every phase of building a working programming language from scratch, using a language called **Mini** as the running example. Mini is small enough to finish in a semester but rich enough to write interesting programs. By the end you will have a lexer, parser, AST, evaluator, environment, closures, and a REPL — the complete pipeline that every real compiler or interpreter contains.

Read this guide alongside the individual module activities. Each phase references the activity where the concept is developed in depth.

---

# Phase 1: Design Your Language First

## 1.1 Write Example Programs Before Anything Else

The single most important design step is writing three to five programs you want your language to run, *before* you write a line of implementation. These become your specification and your test suite.

```
# fib.mini — recursive Fibonacci
let fib = fun(n) {
  if n <= 1 { n } else { fib(n - 1) + fib(n - 2) }
};
print fib(10);

# counter.mini — mutable state via closure
let make_counter = fun() {
  let n = 0;
  fun() { n = n + 1; n }
};
let c = make_counter();
print c();
print c();
print c();

# list_sum.mini — iteration
let sum = fun(lst) {
  let total = 0;
  let i = 0;
  while i < len(lst) {
    total = total + lst[i];
    i = i + 1;
  };
  total
};
print sum([1, 2, 3, 4, 5]);
```

## 1.2 Token Table

Once you have example programs, read through them and list every distinct token kind. This table becomes Phase 2.

| Category | Examples | Token type |
|---|---|---|
| Integer literal | `42`, `0`, `100` | `INT` |
| Float literal | `3.14`, `0.5` | `FLOAT` |
| String literal | `"hello"` | `STRING` |
| Boolean | `true`, `false` | `BOOL` (as keywords) |
| Identifier | `x`, `fib`, `make_counter` | `IDENT` |
| Arithmetic | `+` `-` `*` `/` `%` | `PLUS` `MINUS` `STAR` `SLASH` `PERCENT` |
| Comparison | `==` `!=` `<` `<=` `>` `>=` | `EQEQ` `NEQ` `LT` `LE` `GT` `GE` |
| Logic | `and` `or` `not` | keywords |
| Assignment | `=` | `ASSIGN` |
| Delimiters | `(` `)` `{` `}` `[` `]` | `LPAREN` etc. |
| Punctuation | `,` `;` | `COMMA` `SEMI` |
| Keywords | `if` `else` `while` `let` `fun` `return` `print` | `KW_*` or check `.lexeme` |

## 1.3 Statement and Expression Inventory

Write the list of things your language can do; each item will become an AST node and an evaluator method.

**Statements:** `let`, `assignment`, `if/else`, `while`, `return`, `print`, `expression-statement`  
**Expressions:** arithmetic (`+`,`-`,`*`,`/`,`%`), comparison, logic (`and`,`or`,`not`), unary `-`, function call, function literal (`fun`), list literal, subscript  
**Types:** integer, float, boolean, string, list, function (closure), `nil`

---

# Phase 2: The Lexer

## 2.1 The Token Dataclass

```python
from dataclasses import dataclass

@dataclass
class Token:
    type: str
    lexeme: str
    line: int
    def __repr__(self):
        return f"Token({self.type}, {self.lexeme!r}, line={self.line})"

class LexError(Exception):
    pass
```

## 2.2 Token Constants and Keywords

```python
TK_INT      = "INT"
TK_FLOAT    = "FLOAT"
TK_STRING   = "STRING"
TK_IDENT    = "IDENT"
TK_PLUS     = "PLUS"
TK_MINUS    = "MINUS"
TK_STAR     = "STAR"
TK_SLASH    = "SLASH"
TK_PERCENT  = "PERCENT"
TK_EQEQ     = "EQEQ"
TK_NEQ      = "NEQ"
TK_LT       = "LT"
TK_LE       = "LE"
TK_GT       = "GT"
TK_GE       = "GE"
TK_ASSIGN   = "ASSIGN"
TK_LPAREN   = "LPAREN"
TK_RPAREN   = "RPAREN"
TK_LBRACE   = "LBRACE"
TK_RBRACE   = "RBRACE"
TK_LBRACKET = "LBRACKET"
TK_RBRACKET = "RBRACKET"
TK_COMMA    = "COMMA"
TK_SEMI     = "SEMI"
TK_EOF      = "EOF"

KEYWORDS = {
    "if", "else", "while", "let", "fun", "return",
    "print", "true", "false", "and", "or", "not", "nil"
}
```

## 2.3 The Lexer Class

```python
class Lexer:
    def __init__(self, source):
        self.source = source
        self.pos    = 0
        self.line   = 1

    def at_end(self):
        return self.pos >= len(self.source)

    def peek(self, offset=0):
        p = self.pos + offset
        return self.source[p] if p < len(self.source) else '\0'

    def advance(self):
        ch = self.source[self.pos]
        self.pos += 1
        if ch == '\n':
            self.line += 1
        return ch

    def skip_whitespace_and_comments(self):
        while not self.at_end():
            ch = self.peek()
            if ch in ' \t\r\n':
                self.advance()
            elif ch == '#':
                while not self.at_end() and self.peek() != '\n':
                    self.advance()
            else:
                break

    def read_number(self):
        start = self.pos
        while not self.at_end() and self.peek().isdigit():
            self.advance()
        if not self.at_end() and self.peek() == '.' and self.peek(1).isdigit():
            self.advance()
            while not self.at_end() and self.peek().isdigit():
                self.advance()
            return Token(TK_FLOAT, self.source[start:self.pos], self.line)
        return Token(TK_INT, self.source[start:self.pos], self.line)

    def read_string(self):
        self.advance()  # opening "
        start = self.pos
        result = []
        while not self.at_end() and self.peek() != '"':
            ch = self.advance()
            if ch == '\\':
                esc = self.advance()
                result.append({'n': '\n', 't': '\t', '"': '"', '\\': '\\'}.get(esc, esc))
            else:
                result.append(ch)
        if self.at_end():
            raise LexError(f"unterminated string at line {self.line}")
        self.advance()  # closing "
        return Token(TK_STRING, ''.join(result), self.line)

    def read_ident_or_keyword(self):
        start = self.pos
        while not self.at_end() and (self.peek().isalnum() or self.peek() == '_'):
            self.advance()
        word = self.source[start:self.pos]
        if word in KEYWORDS:
            return Token(word.upper(), word, self.line)
        return Token(TK_IDENT, word, self.line)

    def next_token(self):
        self.skip_whitespace_and_comments()
        if self.at_end():
            return Token(TK_EOF, "", self.line)
        line = self.line
        ch = self.peek()

        if ch.isdigit():
            return self.read_number()
        if ch == '"':
            return self.read_string()
        if ch.isalpha() or ch == '_':
            return self.read_ident_or_keyword()

        self.advance()
        two = ch + self.peek()
        if two == '==': self.advance(); return Token(TK_EQEQ,     '==', line)
        if two == '!=': self.advance(); return Token(TK_NEQ,      '!=', line)
        if two == '<=': self.advance(); return Token(TK_LE,       '<=', line)
        if two == '>=': self.advance(); return Token(TK_GE,       '>=', line)
        one_map = {
            '+': TK_PLUS, '-': TK_MINUS, '*': TK_STAR,
            '/': TK_SLASH, '%': TK_PERCENT,
            '<': TK_LT, '>': TK_GT, '=': TK_ASSIGN,
            '(': TK_LPAREN, ')': TK_RPAREN,
            '{': TK_LBRACE, '}': TK_RBRACE,
            '[': TK_LBRACKET, ']': TK_RBRACKET,
            ',': TK_COMMA, ';': TK_SEMI,
        }
        if ch in one_map:
            return Token(one_map[ch], ch, line)
        raise LexError(f"unexpected character {ch!r} at line {line}")

    def tokenize(self):
        tokens = []
        while True:
            tok = self.next_token()
            tokens.append(tok)
            if tok.type == TK_EOF:
                break
        return tokens
```

**Test Phase 2:** run `Lexer("let x = 42 + 3.14;").tokenize()` and confirm you get INT, FLOAT, PLUS, ASSIGN, IDENT, SEMI, EOF tokens with correct types and lexemes.

---

# Phase 3: The Grammar

Write the full grammar in descent-ready EBNF before touching the parser. Every left-recursive rule becomes a `while` loop; every alternative becomes an `if`.

```
program    → stmt*
stmt       → let_stmt | assign_stmt | if_stmt | while_stmt
           | return_stmt | print_stmt | expr_stmt

let_stmt   → "let" IDENT "=" expr ";"
assign_stmt → IDENT "=" expr ";"
if_stmt    → "if" expr block ("else" block)?
while_stmt → "while" expr block
return_stmt → "return" expr ";"
print_stmt → "print" expr ";"
expr_stmt  → expr ";"
block      → "{" stmt* "}"

expr       → logic
logic      → comparison (("and" | "or") comparison)*
comparison → addsub (("==" | "!=" | "<" | "<=" | ">" | ">=") addsub)?
addsub     → muldiv (("+" | "-") muldiv)*
muldiv     → unary (("*" | "/" | "%") unary)*
unary      → ("not" | "-") unary | call
call       → primary ("(" args? ")" | "[" expr "]")*
args       → expr ("," expr)*
primary    → INT | FLOAT | STRING | "true" | "false" | "nil"
           | IDENT | "(" expr ")" | "[" args? "]" | fun_expr
fun_expr   → "fun" "(" params? ")" block
params     → IDENT ("," IDENT)*
```

**Precedence check (tightest first):** call → unary → mul/div → add/sub → comparison → logic

---

# Phase 4: The AST Nodes

Every grammar construct that carries meaning gets a dataclass. Name fields after the grammar.

```python
from dataclasses import dataclass, field
from typing import List, Optional, Any

@dataclass
class Program:   stmts: List[Any]

# Statements
@dataclass
class LetStmt:   name: str; value: Any; line: int = 0
@dataclass
class AssignStmt: name: str; value: Any; line: int = 0
@dataclass
class IfStmt:    cond: Any; then_block: Any; else_block: Optional[Any]
@dataclass
class WhileStmt: cond: Any; body: Any
@dataclass
class ReturnStmt: value: Any
@dataclass
class PrintStmt: value: Any
@dataclass
class Block:     stmts: List[Any]
@dataclass
class ExprStmt:  expr: Any

# Expressions
@dataclass
class IntLit:    value: int
@dataclass
class FloatLit:  value: float
@dataclass
class StrLit:    value: str
@dataclass
class BoolLit:   value: bool
@dataclass
class NilLit:    pass
@dataclass
class Var:       name: str; line: int = 0
@dataclass
class BinOp:     op: str; left: Any; right: Any
@dataclass
class UnaryOp:   op: str; operand: Any
@dataclass
class Call:      callee: Any; args: List[Any]
@dataclass
class Subscript: obj: Any; index: Any
@dataclass
class FunExpr:   params: List[str]; body: Any
@dataclass
class ListLit:   elements: List[Any]

def pretty(node, depth=0):
    pad = "  " * depth
    name = type(node).__name__
    if isinstance(node, (IntLit, FloatLit, StrLit, BoolLit, NilLit, Var)):
        print(f"{pad}{name}({getattr(node, 'value', getattr(node, 'name', ''))})")
    elif isinstance(node, BinOp):
        print(f"{pad}BinOp({node.op!r})")
        pretty(node.left, depth+1); pretty(node.right, depth+1)
    elif isinstance(node, Block):
        print(f"{pad}Block")
        for s in node.stmts: pretty(s, depth+1)
    else:
        print(f"{pad}{name}")
        for k, v in vars(node).items():
            if isinstance(v, list):
                print(f"{pad}  {k}:")
                for item in v: pretty(item, depth+2)
            elif hasattr(v, '__class__') and v.__class__.__module__ != 'builtins':
                print(f"{pad}  {k}:"); pretty(v, depth+2)
            else:
                print(f"{pad}  {k} = {v!r}")
```

---

# Phase 5: The Parser

```python
class ParseError(Exception):
    pass

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos    = 0

    def peek(self):
        return self.tokens[self.pos]

    def advance(self):
        tok = self.tokens[self.pos]
        if tok.type != TK_EOF:
            self.pos += 1
        return tok

    def check(self, *types):
        return self.peek().type in types

    def match(self, *types):
        if self.check(*types):
            return self.advance()
        return None

    def expect(self, ttype, msg=None):
        tok = self.peek()
        if tok.type != ttype:
            desc = msg or ttype
            raise ParseError(
                f"expected {desc}, got {tok.lexeme!r} at line {tok.line}"
            )
        return self.advance()

    # --- program ---
    def parse_program(self):
        stmts = []
        while not self.check(TK_EOF):
            stmts.append(self.parse_stmt())
        return Program(stmts)

    # --- statements ---
    def parse_stmt(self):
        tok = self.peek()
        if tok.type == "LET":    return self.parse_let_stmt()
        if tok.type == "IF":     return self.parse_if_stmt()
        if tok.type == "WHILE":  return self.parse_while_stmt()
        if tok.type == "RETURN": return self.parse_return_stmt()
        if tok.type == "PRINT":  return self.parse_print_stmt()
        if tok.type == TK_LBRACE: return self.parse_block()
        # assignment or expression statement: peek ahead
        if tok.type == TK_IDENT and self.tokens[self.pos+1].type == TK_ASSIGN:
            return self.parse_assign_stmt()
        return self.parse_expr_stmt()

    def parse_let_stmt(self):
        line = self.peek().line
        self.advance()  # let
        name = self.expect(TK_IDENT, "variable name").lexeme
        self.expect(TK_ASSIGN, "'='")
        value = self.parse_expr()
        self.expect(TK_SEMI, "';'")
        return LetStmt(name, value, line)

    def parse_assign_stmt(self):
        line = self.peek().line
        name = self.advance().lexeme   # IDENT
        self.advance()                 # =
        value = self.parse_expr()
        self.expect(TK_SEMI, "';'")
        return AssignStmt(name, value, line)

    def parse_if_stmt(self):
        self.advance()  # if
        cond = self.parse_expr()
        then_block = self.parse_block()
        else_block = None
        if self.match("ELSE"):
            else_block = self.parse_block()
        return IfStmt(cond, then_block, else_block)

    def parse_while_stmt(self):
        self.advance()  # while
        cond = self.parse_expr()
        body = self.parse_block()
        return WhileStmt(cond, body)

    def parse_return_stmt(self):
        self.advance()  # return
        value = self.parse_expr()
        self.expect(TK_SEMI, "';'")
        return ReturnStmt(value)

    def parse_print_stmt(self):
        self.advance()  # print
        value = self.parse_expr()
        self.expect(TK_SEMI, "';'")
        return PrintStmt(value)

    def parse_expr_stmt(self):
        expr = self.parse_expr()
        self.expect(TK_SEMI, "';'")
        return ExprStmt(expr)

    def parse_block(self):
        self.expect(TK_LBRACE, "'{'")
        stmts = []
        while not self.check(TK_RBRACE) and not self.check(TK_EOF):
            stmts.append(self.parse_stmt())
        self.expect(TK_RBRACE, "'}'")
        return Block(stmts)

    # --- expressions (precedence ladder) ---
    def parse_expr(self):
        return self.parse_logic()

    def parse_logic(self):
        node = self.parse_comparison()
        while self.check("AND", "OR"):
            op = self.advance().lexeme
            right = self.parse_comparison()
            node = BinOp(op, node, right)
        return node

    def parse_comparison(self):
        node = self.parse_addsub()
        if self.check(TK_EQEQ, TK_NEQ, TK_LT, TK_LE, TK_GT, TK_GE):
            op = self.advance().lexeme
            right = self.parse_addsub()
            node = BinOp(op, node, right)
        return node

    def parse_addsub(self):
        node = self.parse_muldiv()
        while self.check(TK_PLUS, TK_MINUS):
            op = self.advance().lexeme
            right = self.parse_muldiv()
            node = BinOp(op, node, right)
        return node

    def parse_muldiv(self):
        node = self.parse_unary()
        while self.check(TK_STAR, TK_SLASH, TK_PERCENT):
            op = self.advance().lexeme
            right = self.parse_unary()
            node = BinOp(op, node, right)
        return node

    def parse_unary(self):
        if self.check("NOT"):
            self.advance(); return UnaryOp("not", self.parse_unary())
        if self.check(TK_MINUS):
            self.advance(); return UnaryOp("-", self.parse_unary())
        return self.parse_call()

    def parse_call(self):
        node = self.parse_primary()
        while True:
            if self.check(TK_LPAREN):
                self.advance()
                args = []
                if not self.check(TK_RPAREN):
                    args.append(self.parse_expr())
                    while self.match(TK_COMMA):
                        args.append(self.parse_expr())
                self.expect(TK_RPAREN, "')'")
                node = Call(node, args)
            elif self.check(TK_LBRACKET):
                self.advance()
                index = self.parse_expr()
                self.expect(TK_RBRACKET, "']'")
                node = Subscript(node, index)
            else:
                break
        return node

    def parse_primary(self):
        tok = self.peek()
        if tok.type == TK_INT:
            self.advance(); return IntLit(int(tok.lexeme))
        if tok.type == TK_FLOAT:
            self.advance(); return FloatLit(float(tok.lexeme))
        if tok.type == TK_STRING:
            self.advance(); return StrLit(tok.lexeme)
        if tok.type == "TRUE":
            self.advance(); return BoolLit(True)
        if tok.type == "FALSE":
            self.advance(); return BoolLit(False)
        if tok.type == "NIL":
            self.advance(); return NilLit()
        if tok.type == TK_IDENT:
            self.advance(); return Var(tok.lexeme, tok.line)
        if tok.type == TK_LPAREN:
            self.advance()
            node = self.parse_expr()
            self.expect(TK_RPAREN, "')'")
            return node
        if tok.type == TK_LBRACKET:
            self.advance()
            elements = []
            if not self.check(TK_RBRACKET):
                elements.append(self.parse_expr())
                while self.match(TK_COMMA):
                    elements.append(self.parse_expr())
            self.expect(TK_RBRACKET, "']'")
            return ListLit(elements)
        if tok.type == "FUN":
            return self.parse_fun_expr()
        raise ParseError(f"unexpected token {tok.lexeme!r} at line {tok.line}")

    def parse_fun_expr(self):
        self.advance()  # fun
        self.expect(TK_LPAREN, "'('")
        params = []
        if not self.check(TK_RPAREN):
            params.append(self.expect(TK_IDENT, "parameter name").lexeme)
            while self.match(TK_COMMA):
                params.append(self.expect(TK_IDENT, "parameter name").lexeme)
        self.expect(TK_RPAREN, "')'")
        body = self.parse_block()
        return FunExpr(params, body)
```

**Test Phase 5:** parse `let x = 1 + 2;` and call `pretty()` on the result. You should see a `Program` containing a `LetStmt` containing a `BinOp('+', IntLit(1), IntLit(2))`.

---

# Phase 6: The Environment

The environment is a linked list of dictionaries. Each dictionary represents one scope. Entering a block pushes a child; leaving it discards the child.

```python
class NameError(Exception):
    pass

class Environment:
    def __init__(self, parent=None):
        self.vars   = {}
        self.parent = parent

    def define(self, name, value):
        self.vars[name] = value

    def lookup(self, name, line=0):
        env = self
        while env is not None:
            if name in env.vars:
                return env.vars[name]
            env = env.parent
        raise NameError(f"undefined variable {name!r} at line {line}")

    def assign(self, name, value, line=0):
        env = self
        while env is not None:
            if name in env.vars:
                env.vars[name] = value
                return
            env = env.parent
        raise NameError(f"cannot assign to undefined variable {name!r} at line {line}")

    def extend(self, names, values):
        child = Environment(parent=self)
        for n, v in zip(names, values):
            child.define(n, v)
        return child
```

**Test Phase 6:** execute the shadowing program: `a=1`, `b=2` in global; create child with `b=20`, `c=30`; confirm `a+b+c = 51` in child, `b = 2` in global, `c` raises NameError in global.

---

# Phase 7: The Evaluator

```python
from dataclasses import dataclass as _dc

@_dc
class Closure:
    params: list
    body:   object
    env:    object

@_dc
class BuiltinFn:
    fn:   object
    name: str

class ReturnSignal(Exception):
    def __init__(self, value): self.value = value

class TypeError(Exception):
    pass

class Evaluator:
    def __init__(self):
        self.global_env = self._make_global_env()

    def _make_global_env(self):
        env = Environment()
        builtins = {
            "len":   BuiltinFn(len,               "len"),
            "str":   BuiltinFn(str,               "str"),
            "int":   BuiltinFn(int,               "int"),
            "float": BuiltinFn(float,             "float"),
            "type":  BuiltinFn(lambda x: type(x).__name__, "type"),
            "range": BuiltinFn(lambda n: list(range(n)), "range"),
            "append":BuiltinFn(lambda lst, x: lst + [x], "append"),
        }
        for name, val in builtins.items():
            env.define(name, val)
        return env

    def eval(self, node, env=None):
        if env is None:
            env = self.global_env
        method = "eval_" + type(node).__name__
        fn = getattr(self, method, None)
        if fn is None:
            raise NotImplementedError(f"no evaluator for {type(node).__name__}")
        return fn(node, env)

    def eval_Program(self, node, env):
        for stmt in node.stmts:
            self.eval(stmt, env)

    def eval_Block(self, node, env):
        child = Environment(parent=env)
        result = None
        for stmt in node.stmts:
            result = self.eval(stmt, child)
        return result

    def eval_LetStmt(self, node, env):
        value = self.eval(node.value, env)
        env.define(node.name, value)

    def eval_AssignStmt(self, node, env):
        value = self.eval(node.value, env)
        env.assign(node.name, value, node.line)

    def eval_IfStmt(self, node, env):
        cond = self.eval(node.cond, env)
        if self._truthy(cond):
            return self.eval(node.then_block, env)
        elif node.else_block:
            return self.eval(node.else_block, env)

    def eval_WhileStmt(self, node, env):
        while self._truthy(self.eval(node.cond, env)):
            self.eval(node.body, env)

    def eval_ReturnStmt(self, node, env):
        raise ReturnSignal(self.eval(node.value, env))

    def eval_PrintStmt(self, node, env):
        print(self.eval(node.value, env))

    def eval_ExprStmt(self, node, env):
        return self.eval(node.expr, env)

    def eval_IntLit(self, node, env):   return node.value
    def eval_FloatLit(self, node, env): return node.value
    def eval_StrLit(self, node, env):   return node.value
    def eval_BoolLit(self, node, env):  return node.value
    def eval_NilLit(self, node, env):   return None
    def eval_ListLit(self, node, env):
        return [self.eval(e, env) for e in node.elements]

    def eval_Var(self, node, env):
        return env.lookup(node.name, node.line)

    def eval_BinOp(self, node, env):
        if node.op == "and":
            left = self.eval(node.left, env)
            return left if not self._truthy(left) else self.eval(node.right, env)
        if node.op == "or":
            left = self.eval(node.left, env)
            return left if self._truthy(left) else self.eval(node.right, env)
        left  = self.eval(node.left, env)
        right = self.eval(node.right, env)
        op = node.op
        if op == '+':
            if isinstance(left, (int, float)) and isinstance(right, (int, float)):
                return left + right
            if isinstance(left, str) and isinstance(right, str):
                return left + right
            raise TypeError(f"'+' requires two numbers or two strings, got {type(left).__name__} and {type(right).__name__}")
        if op == '-': return self._num(left, op) - self._num(right, op)
        if op == '*': return self._num(left, op) * self._num(right, op)
        if op == '/':
            r = self._num(right, op)
            if r == 0: raise ZeroDivisionError("division by zero")
            return self._num(left, op) / r
        if op == '%': return self._num(left, op) % self._num(right, op)
        if op == '==': return left == right
        if op == '!=': return left != right
        if op == '<':  return self._cmp(left, right) < 0
        if op == '<=': return self._cmp(left, right) <= 0
        if op == '>':  return self._cmp(left, right) > 0
        if op == '>=': return self._cmp(left, right) >= 0
        raise TypeError(f"unknown operator {op!r}")

    def eval_UnaryOp(self, node, env):
        val = self.eval(node.operand, env)
        if node.op == '-': return -self._num(val, '-')
        if node.op == 'not': return not self._truthy(val)
        raise TypeError(f"unknown unary op {node.op!r}")

    def eval_FunExpr(self, node, env):
        return Closure(node.params, node.body, env)

    def eval_Call(self, node, env):
        callee = self.eval(node.callee, env)
        args   = [self.eval(a, env) for a in node.args]
        if isinstance(callee, BuiltinFn):
            return callee.fn(*args)
        if isinstance(callee, Closure):
            if len(args) != len(callee.params):
                raise TypeError(
                    f"expected {len(callee.params)} args, got {len(args)}")
            call_env = callee.env.extend(callee.params, args)
            try:
                return self.eval(callee.body, call_env)
            except ReturnSignal as r:
                return r.value
        raise TypeError(f"not callable: {type(callee).__name__}")

    def eval_Subscript(self, node, env):
        obj   = self.eval(node.obj, env)
        index = self.eval(node.index, env)
        if not isinstance(obj, list):
            raise TypeError(f"subscript requires a list, got {type(obj).__name__}")
        if not isinstance(index, int):
            raise TypeError(f"list index must be int, got {type(index).__name__}")
        if index < 0 or index >= len(obj):
            raise IndexError(f"index {index} out of bounds for list of length {len(obj)}")
        return obj[index]

    def _truthy(self, val):
        if val is None or val is False: return False
        if isinstance(val, (int, float)): return val != 0
        if isinstance(val, str): return len(val) > 0
        if isinstance(val, list): return len(val) > 0
        return True

    def _num(self, val, op):
        if not isinstance(val, (int, float)):
            raise TypeError(f"operator {op!r} requires a number, got {type(val).__name__}")
        return val

    def _cmp(self, a, b):
        if isinstance(a, (int, float)) and isinstance(b, (int, float)):
            return (a > b) - (a < b)
        if isinstance(a, str) and isinstance(b, str):
            return (a > b) - (a < b)
        raise TypeError(f"cannot compare {type(a).__name__} and {type(b).__name__}")
```

**Test Phase 7:** evaluate `let x = 10; print x * x;` — should print `100`. Evaluate the Fibonacci example from Phase 1.

---

# Phase 8: REPL and File Runner

```python
import sys
import argparse

def run_source(source, evaluator=None):
    ev = evaluator or Evaluator()
    try:
        tokens = Lexer(source).tokenize()
        ast    = Parser(tokens).parse_program()
        ev.eval(ast)
        return ev
    except LexError as e:
        print(f"[LexError] {e}", file=sys.stderr)
    except ParseError as e:
        print(f"[ParseError] {e}", file=sys.stderr)
    except NameError as e:
        print(f"[NameError] {e}", file=sys.stderr)
    except TypeError as e:
        print(f"[TypeError] {e}", file=sys.stderr)
    except ZeroDivisionError as e:
        print(f"[ZeroDivisionError] {e}", file=sys.stderr)
    return ev

def repl():
    print("Mini 0.1 — type 'exit' to quit")
    ev = Evaluator()
    while True:
        try:
            line = input(">>> ")
        except (EOFError, KeyboardInterrupt):
            print(); break
        if line.strip() in ("exit", "quit"):
            break
        if not line.strip():
            continue
        if not line.rstrip().endswith(';') and not line.rstrip().endswith('}'):
            line = line + ';'
        run_source(line, ev)

def run_file(path):
    try:
        with open(path) as f:
            source = f.read()
    except FileNotFoundError:
        print(f"[Error] file not found: {path!r}", file=sys.stderr)
        sys.exit(1)
    run_source(source)

def main():
    parser = argparse.ArgumentParser(description="Mini language interpreter")
    parser.add_argument("file", nargs="?", help="source file to run")
    args = parser.parse_args()
    if args.file:
        run_file(args.file)
    else:
        repl()

if __name__ == "__main__":
    main()
```

Save the full implementation in a file called `mini.py`. Run `python mini.py` for the REPL, `python mini.py hello.mini` for file execution.

---

# Phase 9: Built-in Functions

You already added builtins in Phase 7's `_make_global_env`. Add more as your language grows:

```python
# Add these to _make_global_env:
more_builtins = {
    "print":   BuiltinFn(print,             "print"),
    "input":   BuiltinFn(input,             "input"),
    "abs":     BuiltinFn(abs,               "abs"),
    "max":     BuiltinFn(max,               "max"),
    "min":     BuiltinFn(min,               "min"),
    "floor":   BuiltinFn(lambda x: int(x),  "floor"),
    "split":   BuiltinFn(str.split,         "split"),
    "join":    BuiltinFn(lambda sep, lst: sep.join(lst), "join"),
    "map":     BuiltinFn(lambda f, lst: [_call(f, [x]) for x in lst], "map"),
    "filter":  BuiltinFn(lambda f, lst: [x for x in lst if _call(f, [x])], "filter"),
    "reduce":  BuiltinFn(lambda f, lst, init: __import__('functools').reduce(
                    lambda acc, x: _call(f, [acc, x]), lst, init), "reduce"),
}

def _call(closure_or_builtin, args):
    if isinstance(closure_or_builtin, BuiltinFn):
        return closure_or_builtin.fn(*args)
    if isinstance(closure_or_builtin, Closure):
        c = closure_or_builtin
        call_env = c.env.extend(c.params, args)
        ev = Evaluator()
        try:
            return ev.eval(c.body, call_env)
        except ReturnSignal as r:
            return r.value
    raise TypeError(f"not callable: {closure_or_builtin!r}")
```

---

# Phase 10: Testing Checklist

Run every item; fix before moving on.

| Test | Expected | Pass? |
|---|---|---|
| `let x = 42; print x;` | prints `42` | |
| `let x = 1; { let x = 2; print x; }; print x;` | prints `2` then `1` | |
| `let y = 0; print (if true { y = 1; } else {}); print y;` | y is 1 after if | |
| `let n = 0; while n < 3 { n = n + 1; }; print n;` | prints `3` | |
| `let f = fun(x) { return x * x; }; print f(7);` | prints `49` | |
| `1 + "x"` | TypeError: `'+'` requires two numbers | |
| `let z = undefined_var;` | NameError: undefined | |
| `1 / 0` | ZeroDivisionError | |
| Fibonacci(10) | 55 | |
| Closure counter | 1, 2, 3 | |

```python
# test_mini.py — run with: python test_mini.py
import io, sys

def run(src):
    captured = io.StringIO()
    sys.stdout = captured
    run_source(src)
    sys.stdout = sys.__stdout__
    return captured.getvalue().strip()

assert run("print 2 + 3;") == "5"
assert run("print 10 - 3 - 2;") == "5"    # left-associative: (10-3)-2
assert run("print 2 * 3 + 1;") == "7"     # precedence: (2*3)+1
assert run("let x = 42; print x;") == "42"
assert run("let x = 1; { let x = 2; print x; }; print x;") == "2\n1"
assert run("let n = 0; while n < 3 { n = n + 1; }; print n;") == "3"
assert run("let f = fun(x) { return x * x; }; print f(9);") == "81"

fib_src = """
let fib = fun(n) {
    if n <= 1 { return n; };
    return fib(n - 1) + fib(n - 2);
};
print fib(10);
"""
assert run(fib_src) == "55"

counter_src = """
let make_counter = fun() {
    let n = 0;
    return fun() { n = n + 1; return n; };
};
let c = make_counter();
print c();
print c();
print c();
"""
assert run(counter_src) == "1\n2\n3"

print("All tests passed.")
```

---

# Extension Ideas

Once the core works, these extensions are each a focused module:

**Tail call optimization.** Replace deep function recursion with a trampoline so `fib(10000)` does not overflow the Python call stack. See the Scheme metacircular evaluator module for the trampoline pattern.

**Closures with mutable state.** Verify that your counter example works by examining that `Closure` captures `env` by reference (not by copy). If it does not, trace why and fix it.

**Macros via AST transformation.** Add a `macro` keyword that receives an unevaluated AST, transforms it, and returns a new AST to evaluate. This is how `for` loops can be sugar for `while`.

**Type annotations.** Add optional `x: Int` syntax to `let` and function parameters. Run a static pass over the AST before evaluation to catch type mismatches at compile time.

**Bytecode compiler.** Instead of tree-walking evaluation, compile the AST to a list of stack machine instructions (`PUSH`, `LOAD`, `STORE`, `ADD`, `JMP_IF_FALSE`, etc.) and write a simple stack-machine interpreter. This is the foundation of Python's own CPython VM. See the transpiler module.

---

## Further Reading

- Robert Nystrom. *Crafting Interpreters* (online, free). The definitive modern guide; the Lox language is essentially this tutorial expanded to book length.
- Douglas Thain. *Introduction to Compilers and Language Design* (online, free). Chapters 1–7 match this guide phase by phase.
- Abelson and Sussman. *SICP*, Chapter 4: the metacircular evaluator in Scheme.
- The tutorial `tutorial-build-an-interpreter.md` in this repo: a complete Mini implementation to compare against.
