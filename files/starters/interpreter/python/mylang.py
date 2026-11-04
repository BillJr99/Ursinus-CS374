"""CS374 Interpreter assignment: the file runner.

python3 mylang.py program.ml runs a file.  With no file name, it reads the
program from standard input, as in: echo 'print 1 + 2;' | python3 mylang.py
"""

import sys

from lexer import LexError
from parser import parse, ParseError
from interpreter import Interpreter, LangError, BreakSignal, ContinueSignal


def run_source(source):
    """Run one program through every stage.  Return None, or one staged error line."""
    # TODO (Step 7): turn each failure into its staged line, as the page describes.
    Interpreter().eval_node(parse(source))
    return None


if __name__ == "__main__":
    source = open(sys.argv[1]).read() if len(sys.argv) > 1 else sys.stdin.read()
    message = run_source(source)
    if message is not None:
        print(message)
        sys.exit(1)
