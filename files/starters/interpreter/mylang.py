"""CS374 Interpreter assignment, Part 3: file runner and REPL.

Each stage catches its own error class and prints a message that names the
stage, so a user can tell a lexing problem from a parsing problem from a
runtime one without reading a Python traceback.
"""

import sys
import traceback

from lexer import LexError            # TODO: match your lexer's error class name
from parser import parse, ParseError
from interpreter import Interpreter, LangError


def run_file(path):
    source = open(path).read()
    # TODO: lex, catching LexError -> "Lexical error at line L, col C: ..."
    # TODO: parse, catching ParseError -> "Syntax error at line L, col C: ..."
    # TODO: typecheck (Part 4), catching LangTypeError -> "Type error at line L, col C: ..."
    # TODO: evaluate, catching LangError subclasses -> "Runtime error at line L: ..."
    # exit after printing any error
    raise NotImplementedError("run_file")


def repl():
    """Step 3b: one persistent Environment, recovery after every error class."""
    # TODO: read a line, run it, print the value or a staged error, and loop.
    #       The environment must SURVIVE an error, so the session continues.
    #       Exit cleanly on 'quit' and on EOF (Ctrl-D).
    raise NotImplementedError("repl")


if __name__ == "__main__":
    try:
        run_file(sys.argv[1]) if len(sys.argv) > 1 else repl()
    except Exception as e:
        print(f"[mylang:__main__] {e}")
        traceback.print_exc()
        sys.exit(2)
