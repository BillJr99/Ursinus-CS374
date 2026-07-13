# CS374 Reference Interpreter

This is the **instructor reference implementation** of the Interpreter
assignment, released at the team-project build phase so that every team has
a working end-to-end pipeline to extend. Python 3.10+ (tested on 3.11),
standard library only. The package is fully self-contained: it ships copies
of the reference lexer and parser (`tokens.py`, `lexer.py`, `ast_nodes.py`,
`parser.py`, `pretty.py`, `token_spec*.json`) and imports them unchanged.

> **Usage declaration policy:** your team may build on this reference
> interpreter (and/or the reference lexer/parser) instead of your own.
> If you do, declare it with one line in your project README (e.g., *"This
> project builds on the reference interpreter."*). There is no penalty,
> and your original Interpreter assignment grade stands unchanged.

## Files

| File | Purpose |
|------|---------|
| `interp.py` | `Interpreter` (isinstance dispatch), `Environment`, truthiness, short-circuit `LogicOp`, `BreakSignal`/`ContinueSignal`, the `LangError` hierarchy |
| `repl.py` | file runner (`python3 repl.py program.lang`) and REPL (`python3 repl.py`) with staged error messages |
| `test_interp.py` | 35 tests: run `python3 -m pytest test_interp.py` or `python3 test_interp.py` |
| `samples/*.lang` | three end-to-end sample programs |
| the rest | reference lexer + parser, imported unchanged |

## Quick start

```
python3 repl.py samples/countdown.lang     # run a file
python3 repl.py                            # REPL: persistent env, >> prompt
python3 -m pytest test_interp.py           # test suite
```

```python
from parser import parse
from interp import Interpreter
Interpreter().run(parse('let x = 2; print x * (x + 1);'))   # prints 6
```

## Semantics decisions (the reference SEMANTICS)

1. **Truthiness:** `false`, `0`, `0.0`, `""` are falsy; everything else is
   truthy. `while x { ... }` with numeric `x` works.
2. **Short-circuit:** `and`/`or` return the deciding **operand value**
   (`0 or 7` is `7`); the right operand is never evaluated when the left
   decides — the bomb test `let safe = true or (1 / 0);` passes. `not`
   always returns a boolean.
3. **Arithmetic:** `+ - * /` require numbers; `+` also concatenates two
   strings (`"a" + 1` is a `LangTypeError` naming both types). `/` is true
   division and always yields a float; `x / 0` raises
   `LangZeroDivisionError` ("division by zero") with the position.
4. **Comparisons:** `< <= > >=` require numbers. `==`/`!=` never raise:
   operands of different types are simply unequal (`1 == "1"` is `false`);
   `bool` is its own type (`true == 1` is `false`), while `int` and `float`
   are both numbers (`1 == 1.0` is `true`).
5. **Scoping:** `let` defines a new binding in the current scope; bare
   assignment updates the existing binding wherever it lives (or raises
   `LangNameError: Cannot assign to undefined variable 'y'`). Every block
   `{ ... }` gets a child `Environment` discarded on exit; the shadowing
   program prints `51` then `2`. The while body is a block, so the loop
   body scope is **per-iteration**; a `let` inside the body does not
   survive the loop.
6. **break/continue:** implemented as `BreakSignal`/`ContinueSignal`
   exceptions caught by the `While` evaluator; escaping to the top level
   becomes `Runtime error: 'break' outside loop` (staged, not a crash).
7. **Printing:** booleans render as `true`/`false`, strings without
   quotes, ints without a decimal point, floats with one.

## Staged error format (file runner and REPL)

```
Lexical error at line L, col C: unexpected character '@'
Syntax error at line L, col C: expected SEMICOLON, found EOF
Runtime error at line L: division by zero
```

The REPL keeps one persistent `Environment` across inputs, prints the value
of a bare expression, recovers from every error class, and exits on
`quit`/`exit`/Ctrl-D. It reads one line at a time (documented choice), so
keep multi-statement constructs on one line.
