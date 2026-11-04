"""CS374 Parser assignment: an LR(1) parser for one small grammar.

lexer.py and ast_nodes.py are complete.  Every TODO in this file is yours, and
the assignment page walks you through them in order, with a check after each.
"""

from lexer import tokenize
from ast_nodes import Num, Var, BinOp, Let, Print, Program


# The grammar is fixed.  Production 0 is the augmented start production.
PRODUCTIONS = [
    ("S'",      ["program"]),                     # 0
    ("program", ["program", "stmt"]),             # 1
    ("program", ["stmt"]),                        # 2
    ("stmt",    ["let", "id", "=", "expr", ";"]), # 3
    ("stmt",    ["print", "expr", ";"]),          # 4
    ("expr",    ["expr", "+", "term"]),           # 5
    ("expr",    ["expr", "-", "term"]),           # 6
    ("expr",    ["term"]),                        # 7
    ("term",    ["term", "*", "factor"]),         # 8
    ("term",    ["factor"]),                      # 9
    ("factor",  ["(", "expr", ")"]),              # 10
    ("factor",  ["num"]),                         # 11
    ("factor",  ["id"]),                          # 12
]
NONTERMINALS = {"S'", "program", "stmt", "expr", "term", "factor"}
TERMINALS = {"let", "print", "id", "num", "=", ";", "+", "-", "*", "(", ")", "$"}
SYMBOLS = ["program", "stmt", "expr", "term", "factor",   # the order build_states tries symbols,
           "let", "print", "id", "num", "=", ";", "+", "-", "*", "(", ")"]   # so that everyone gets one numbering


class ParseError(Exception):
    """Raised when the table has no action for a token."""
    def __init__(self, found, line, col):
        super().__init__(f"ParseError at line {line}, col {col}: unexpected {found}")
        self.found = found
        self.line = line
        self.col = col


# --- Part 1: items, FIRST, closure, goto ------------------------------------

def show_item(item):
    """Render (5, 1, ";") as "[expr -> expr . + term, ;]"."""
    # TODO (Step 1.1)
    raise NotImplementedError("show_item")


def first_sets():
    """Return a dict from each non-terminal to the set of terminals that can begin it."""
    # TODO (Step 1.2)
    raise NotImplementedError("first_sets")


def lookaheads(beta, a, first):
    """The terminals that can follow a non-terminal, when beta and then a come after it."""
    # TODO (Step 1.3)
    raise NotImplementedError("lookaheads")


def closure(items):
    """Return a frozenset of the items plus every item the closure rule adds."""
    # TODO (Step 1.3)
    raise NotImplementedError("closure")


def goto(state, symbol):
    """Advance the dot past symbol in every item that allows it, and close the result."""
    # TODO (Step 1.4)
    raise NotImplementedError("goto")


# --- Part 2: states, tables, and the driver ---------------------------------

def build_states():
    """Return (states, transitions): a list of frozensets, and a dict from (i, symbol) to j."""
    # TODO (Step 2.1)
    raise NotImplementedError("build_states")


def build_tables(states, transitions):
    """Return (action, goto_table, conflicts)."""
    # TODO (Step 2.2)
    raise NotImplementedError("build_tables")


def show_production(p):
    """Render production 8 as "term -> term * factor"."""
    return PRODUCTIONS[p][0] + " -> " + " ".join(PRODUCTIONS[p][1])


def drive(tokens, action, goto_table, trace=False):
    """Run the table on the tokens.  Part 3 makes this return the AST."""
    # TODO (Steps 2.3 and 3.2)
    raise NotImplementedError("drive")


# --- Part 3: the AST --------------------------------------------------------

def build_node(p, kids):
    """Return the value of production p.  kids holds the value of each right-hand symbol, in order."""
    if p == 5 or p == 6:                 # expr -> expr + term, expr -> expr - term
        left, op, right = kids
        return BinOp(op.value, left, right, op.line, op.col)
    if p == 12:                          # factor -> id
        tok = kids[0]
        return Var(tok.value, tok.line, tok.col)
    # TODO (Step 3.1): productions 8, 7, 9, 10, 11, 3, 4, 2, and 1
    raise NotImplementedError(f"no node for production {p}")


def parse(source):
    """Lex the source, build the tables once, and return the Program your driver builds."""
    states, transitions = build_states()
    action, goto_table, conflicts = build_tables(states, transitions)
    return drive(tokenize(source), action, goto_table)
