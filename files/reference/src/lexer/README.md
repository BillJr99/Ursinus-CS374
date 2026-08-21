# CS374 Reference Lexer

This is the **instructor reference implementation** of the Lexer assignment,
released with the Parser assignment so that nobody is blocked by a broken
lexer. Python 3.10+ (tested on 3.11), standard library only.

> **Usage declaration policy:** you may build your Parser on this reference
> lexer instead of your own. If you do, declare it with one line in your
> Parser README (e.g., *"This submission uses the reference lexer."*).
> There is no penalty for using it, and your original Lexer assignment
> grade stands unchanged.

## Files

| File | Purpose |
|------|---------|
| `tokens.py` | the `Token` dataclass: `type`, `value` (raw lexeme), `line`, `col`, and `decoded` (STRING tokens only) |
| `lexer.py` | `TOKEN_SPEC`, the `tokenize` generator, the `Lexer` class, `LexError`, `LexErrorList` |
| `token_spec.json` | the default token specification (JSON-configurable dialect) |
| `token_spec_alt.json` | the alternate dialect: `//` comments, `:=` assignment |
| `test_lexer.py` | 23 tests: run `python3 -m pytest test_lexer.py` or `python3 test_lexer.py` |

## The interface contract

```python
from lexer import Lexer

lx = Lexer('let x = 42;')                 # or Lexer(src, config_path="token_spec.json")
lx.peek()      # -> Token, idempotent, never consumes
lx.advance()   # -> Token, consumes; returns EOF forever at end of input
lx.expect("LET")  # -> Token if it matches; else raises a located LexError
```

- `Token` fields: `type`, `value` (the **raw** lexeme), `line`, `col`
  (both 1-indexed), and `decoded` (the escape-resolved value, STRING only).
- The EOF token is `Token("EOF", "", line, col)` positioned one past the
  last character (worked example: `"let x = 42;"` gives EOF at col 12).
- Error modes: `Lexer(src)` is `fail_fast` (lazy; the first bad character
  raises `LexError` when reached); `Lexer(src, error_mode="collect_all")`
  scans the whole source at construction and raises one `LexErrorList`
  carrying `.errors` (all of them) and `.tokens` (everything still
  recognized, recovery evidence).
- Every `LexError` has `.message`, `.line`, `.col` and prints as
  `LexError at line L, col C: <message>`.

## TOKEN_SPEC ordering rationale

Ordered rules + maximal munch means order is correctness:
COMMENT/WHITESPACE first (skipped); `FLOAT` before `INT`; every keyword
(with a `\b` boundary, so `iffy` is an IDENT) before `IDENT`;
`<= >= == !=` before `< > = !`. Unterminated strings raise at the
**opening** quote's position.

## Interface decisions beyond the assignment text

- Added keyword tokens `AND`, `OR`, `NOT`, `BREAK`, `CONTINUE`; the Parser
  grammar and Interpreter AST require them, and the same component must
  serve all three assignments.
- Unknown string escapes (e.g. `\q`) raise a `LexError` rather than passing
  through silently.
- In `collect_all` mode the full scan happens in `Lexer.__init__`, and the
  `LexErrorList` carries the recovered token list.
