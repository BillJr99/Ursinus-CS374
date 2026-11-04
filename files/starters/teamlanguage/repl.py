"""The REPL and the file-runner.

    python3 repl.py                  opens the REPL
    python3 repl.py samples/a.lang   runs one program
"""
import sys

from interpreter import run
from lexer import LangError


def run_file(path):
    with open(path) as f:
        source = f.read()
    try:
        run(source)
    except LangError as e:
        print(e)
        return 1
    return 0


def repl():
    env = {}
    while True:
        try:
            line = input(">>> ")
        except EOFError:
            print()
            return 0
        try:
            run(line, env)
        except LangError as e:
            print(e)


if __name__ == "__main__":
    sys.exit(run_file(sys.argv[1]) if len(sys.argv) > 1 else repl())
