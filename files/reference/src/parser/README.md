# CS374 Reference Parser + AST

This is the **instructor reference implementation** of the Parser assignment,
released with the Interpreter assignment so that nobody is blocked by a
broken parser. Python 3.10+ (tested on 3.11), standard library only. The
package is self-contained: it ships copies of the reference lexer
(`tokens.py`, `lexer.py`, `token_spec.json`, `token_spec_alt.json`) and
imports it unchanged.

> **Usage declaration policy:** you may build your Interpreter on this
> reference parser (and/or the reference lexer) instead of your own. If you
> do, declare it with one line in your Interpreter README (e.g., *"This
> submission uses the reference parser."*). There is no penalty, and your
> original Parser assignment grade stands unchanged.

## Files

| File | Purpose |
|------|---------|
| `ast_nodes.py` | all node dataclasses (documented fields, line/col positions) |
| `parser.py` | recursive descent parser, `ParseError`, `parse()`, `parse_expression()` |
| `pretty.py` | `pretty()` (indented tree view) and `unparse()` (code regeneration) |
| `tokens.py`, `lexer.py`, `token_spec*.json` | the reference lexer, imported unchanged |
| `test_parser.py` | 28 tests: run `python3 -m pytest test_parser.py` or `python3 test_parser.py` |

## Entry points

```python
from parser import parse, parse_expression, ParseError
from pretty import pretty, unparse

tree = parse("let x = 10; while x > 0 { print x; x = x - 1; }")
print(pretty(tree))       # indented structural view
print(unparse(tree))      # regenerated source; parse(unparse(tree)) == tree
```

## Grammar (matches the implementation exactly)

```
program     ::= stmt* EOF
stmt        ::= let_stmt | assign_stmt | print_stmt | if_stmt
              | while_stmt | break_stmt | continue_stmt | block
let_stmt    ::= LET IDENT EQ expr SEMICOLON
assign_stmt ::= IDENT EQ expr SEMICOLON
print_stmt  ::= PRINT expr SEMICOLON
if_stmt     ::= IF expr block ( ELSE ( if_stmt | block ) )?
while_stmt  ::= WHILE expr block
break_stmt  ::= BREAK SEMICOLON
continue_stmt ::= CONTINUE SEMICOLON
block       ::= LBRACE stmt* RBRACE

expr        ::= or_expr
or_expr     ::= and_expr ( OR and_expr )*      # left-assoc -> LogicOp("or")
and_expr    ::= not_expr ( AND not_expr )*     # left-assoc -> LogicOp("and")
not_expr    ::= NOT not_expr | comparison      # prefix -> UnaryOp("not")
comparison  ::= addsub ( (LT|LE|GT|GE|EQEQ|NEQ) addsub )?   # NON-assoc
addsub      ::= muldiv ( (PLUS|MINUS) muldiv )*             # left-assoc
muldiv      ::= unary ( (STAR|SLASH) unary )*               # left-assoc
unary       ::= MINUS unary | primary
primary     ::= INT | FLOAT | STRING | TRUE | FALSE | IDENT
              | LPAREN expr RPAREN
```

## Documented decisions

- **Dangling else:** an `else` attaches to the **nearest** `if`; the
  recursive call structure of `parse_if_stmt` enforces it (the innermost
  active `if` consumes the `ELSE` first).
- **Comparison chaining:** `a < b < c` is a syntax error, reported
  explicitly (`comparison operators do not chain; use parentheses`).
- **Assignment lookahead:** the grammar has no expression statements, so a
  statement starting with `IDENT` can only be an assignment; one token of
  lookahead suffices.
- **`break`/`continue` statements** are added beyond the Parser
  assignment's minimum grammar because the Interpreter assignment's AST
  requires `Break`/`Continue` nodes.
- **Positions never break equality:** every node's `line`/`col` fields are
  declared with `compare=False`, so the round-trip law
  `parse(unparse(parse(s))) == parse(s)` is plain `==`.
- **Numbers:** `INT` lexemes become Python `int`, `FLOAT` lexemes `float`,
  both stored in `Num.value`.
- **Unparser parenthesization rule:** parenthesize a child when its
  precedence is lower than its parent's, or equal and (a) it is the right
  child of a left-associative operator, or (b) the tier is the
  non-associative comparison tier.
- **Errors:** `ParseError` carries `.message` (`expected X, found Y`),
  `.line`, `.col`, and prints as
  `ParseError at line L, col C: expected SEMICOLON, found RBRACE`.
  (The assignment's Hypothesis property test is replaced here by a
  stdlib-only 300-tree randomized round-trip test, since the reference
  packages must be dependency-free.)
