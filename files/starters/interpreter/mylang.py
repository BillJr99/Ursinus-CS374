"""CS374 Interpreter assignment, Part 3: file runner and REPL.

Each stage catches its own error class and prints a message that names the
stage, so a user can tell a lexing problem from a parsing problem from a
runtime one without reading a Python traceback.
"""

import sys
import traceback

from lexer import LexError            # TODO: match your lexer's error class name
from parser import parse, ParseError
from interpreter import Interpreter, LangError, BreakSignal, ContinueSignal


def run_source(source, interp):
    """Run one program through every stage.  Return None, or one staged error line.

    Both run_file and repl go through this helper, so each stage's try is
    written exactly once (Step 3a).
    """
    # TODO: Lex stage: turn the source into a tree; a LexError becomes "Lexical error at line L, col C: ..."
    #       and a ParseError becomes "Syntax error at line L, col C: ..."
    # TODO (Step 4c): Type stage: check the whole tree; a LangTypeError becomes "Type error at line L, col C: ..."
    # TODO: Run stage: evaluate the tree; any LangError becomes "Runtime error at line L: ..."
    # TODO: a BreakSignal that escapes -> "Runtime error at line L: 'break' outside loop";
    #       a ContinueSignal that escapes -> the same, with 'continue' in place of 'break'
    return None


def run_file(path):
    source = open(path).read()
    message = run_source(source, Interpreter())
    if message is not None:
        print(message)
        sys.exit(1)                  # exit after printing any error


def repl():
    """Step 3b: one persistent Environment, recovery after every error class."""
    interp = Interpreter()           # ONE interpreter for the session, so ONE global Environment
    while True:
        # TODO: read a line with input(">> "); leave the loop on EOFError
        # TODO: leave the loop on "quit" or "exit"
        # TODO: run the line through run_source(line, interp); print any message and keep looping
        raise NotImplementedError("repl")


if __name__ == "__main__":
    try:
        run_file(sys.argv[1]) if len(sys.argv) > 1 else repl()
    except Exception as e:
        print(f"[mylang:__main__] {e}")
        traceback.print_exc()
        sys.exit(2)
