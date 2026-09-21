#!/usr/bin/env python3
"""Entry point matching the name the Interpreter assignment asks you to build.

    python3 mylang.py program.ml    # run a file, staged error messages
    python3 mylang.py               # REPL: persistent env, >> prompt

The implementation lives in repl.py; this module exists so that the reference
pipeline is driven by the same command line as your own deliverable, and so
that the commands printed in the assignment work unchanged against it.
"""

import sys

from repl import main

if __name__ == "__main__":
    sys.exit(main(sys.argv))
