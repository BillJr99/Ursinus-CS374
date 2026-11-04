"""CS374 Parser assignment, Part 1: an LR(1) calculator.

lexer.py is complete.  Every TODO in this file is yours, and the assignment page
walks you through them in order, with a check after each.
"""

import sys

from lexer import tokenize


# The grammar is fixed.  Production 0 is the augmented start production.
PRODUCTIONS = [
    ("S'", ["E"]),               # 0
    ("E",  ["E", "+", "T"]),     # 1
    ("E",  ["E", "-", "T"]),     # 2
    ("E",  ["T"]),               # 3
    ("T",  ["T", "*", "F"]),     # 4
    ("T",  ["T", "/", "F"]),     # 5
    ("T",  ["F"]),               # 6
    ("F",  ["(", "E", ")"]),     # 7
    ("F",  ["num"]),             # 8
]
NONTERMINALS = {"S'", "E", "T", "F"}
# The order build_states tries symbols, so that everyone gets the same state numbers.
SYMBOLS = ["E", "T", "F", "num", "+", "-", "*", "/", "(", ")"]


class ParseError(Exception):
    """Raised when the table has no action for a token."""
    def __init__(self, found, col):
        super().__init__(f"ParseError at col {col}: unexpected {found}")
        self.found = found
        self.col = col


# --- Items, FIRST, closure, and goto ----------------------------------------

def show_item(item):
    """Render (1, 1, "+") as "[E -> E . + T, +]"."""
    # TODO (Step 1.2)
    raise NotImplementedError("show_item")


def first_sets():
    """Return a dict from each non-terminal to the set of terminals that can begin it."""
    # TODO (Step 1.3)
    raise NotImplementedError("first_sets")


def lookaheads(beta, a, first):
    """The terminals that can follow a non-terminal, when beta and then a come after it."""
    # TODO (Step 1.4)
    raise NotImplementedError("lookaheads")


def closure(items):
    """Return a frozenset of the items plus every item the closure rule adds."""
    # TODO (Step 1.4)
    raise NotImplementedError("closure")


def goto(state, symbol):
    """Advance the dot past symbol in every item that allows it, and close the result."""
    # TODO (Step 1.5)
    raise NotImplementedError("goto")


# --- States and tables ------------------------------------------------------

def build_states():
    """Return (states, transitions): every reachable state, and each edge (i, symbol) -> j."""
    # TODO (Step 1.6)
    raise NotImplementedError("build_states")


def build_tables(states, transitions):
    """Return (action, goto_table, conflicts), read straight off the states."""
    # TODO (Step 1.7)
    raise NotImplementedError("build_tables")


# --- The driver: it computes on each reduction ------------------------------

def reduce_value(p, v):
    """Return the value of production p's left side, given the values v of its right side."""
    if p == 1:              # E -> E + T
        return v[0] + v[2]
    if p == 3:              # E -> T
        return v[0]
    if p == 8:              # F -> num
        return int(v[0])
    # TODO (Step 1.8): productions 2, 4, 5, 6, and 7.
    raise NotImplementedError(f"production {p}")


def run(tokens, action, goto_table):
    """Run the shift-reduce parse from the tables, and return the calculator's answer."""
    # TODO (Step 1.8)
    raise NotImplementedError("run")


def calculate(text):
    """Build the tables once and run them on text."""
    states, transitions = build_states()
    action, goto_table, conflicts = build_tables(states, transitions)
    return run(tokenize(text), action, goto_table)


if __name__ == "__main__":
    print(calculate(sys.argv[1]))
