"""repl.py -- file runner and REPL for the CS374 reference interpreter.

Usage:
    python3 repl.py program.lang    # run a file, staged error messages
    python3 repl.py                 # interactive REPL

Staged error format (Part 3 of the Interpreter assignment):

    Lexical error at line L, col C: <message>
    Syntax error at line L, col C: expected X, found Y
    Runtime error at line L: <message>

The REPL keeps ONE persistent Environment across inputs, recovers from
every error class, prints the value of a bare expression, and exits on
``quit``, ``exit`` or Ctrl-D. Input is read one line at a time (the
documented choice; put multi-statement constructs on one line).
"""

import sys

from lexer import LexError, LexErrorList
from parser import ParseError, parse, parse_expression
from interp import (Environment, Interpreter, LangError, format_value)


def report(exc) -> str:
    """Map an exception from any pipeline stage to its staged message."""
    if isinstance(exc, LexErrorList):
        return "\n".join(report(e) for e in exc.errors)
    if isinstance(exc, LexError):
        return f"Lexical error at line {exc.line}, col {exc.col}: {exc.message}"
    if isinstance(exc, ParseError):
        return f"Syntax error at line {exc.line}, col {exc.col}: {exc.message}"
    if isinstance(exc, LangError):
        return f"Runtime error at line {exc.line}: {exc.message}"
    return f"Internal error: {exc}"


def run_file(path: str) -> int:
    """Lex, parse, and evaluate a source file with staged error reporting.
    Returns the process exit code."""
    try:
        with open(path, "r", encoding="utf-8") as fh:
            source = fh.read()
    except OSError as exc:
        print(f"error: cannot read {path}: {exc}", file=sys.stderr)
        return 2
    try:
        tree = parse(source)          # LexErrors surface here too (lazy lexer)
    except (LexError, ParseError) as exc:
        print(report(exc), file=sys.stderr)
        return 1
    try:
        Interpreter().run(tree)
    except LangError as exc:
        print(report(exc), file=sys.stderr)
        return 1
    return 0


def repl() -> None:
    print("CS374 reference interpreter. Type 'quit' or Ctrl-D to exit.")
    env = Environment()
    interp = Interpreter(env=env)
    while True:
        try:
            line = input(">> ")
        except EOFError:
            print()
            break
        except KeyboardInterrupt:
            print()
            continue
        stripped = line.strip()
        if not stripped:
            continue
        if stripped in ("quit", "exit"):
            break
        try:
            try:
                tree = parse(line)
            except ParseError as stmt_err:
                # not a statement -- maybe a bare expression: print its value
                try:
                    expr = parse_expression(line)
                except (LexError, ParseError):
                    raise stmt_err from None
                value = interp.eval_node(expr, env)
                print(format_value(value))
                continue
            interp.run(tree)   # converts stray break/continue to staged errors
        except (LexError, LexErrorList, ParseError, LangError) as exc:
            print(report(exc))


def main(argv) -> int:
    if len(argv) > 1:
        return run_file(argv[1])
    repl()
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
