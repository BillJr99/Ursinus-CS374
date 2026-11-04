"""CS374 Parser assignment: the lexer for the calculator.

This file is complete.  tokenize(source) returns a list of Tokens that always
ends with a "$" token.  A token's type is the terminal name the grammar uses.
"""

import re
from dataclasses import dataclass


class LexError(Exception):
    """Raised on a character the calculator does not allow."""
    def __init__(self, char, col):
        super().__init__(f"LexError at col {col}: unexpected character {char!r}")
        self.col = col


@dataclass
class Token:
    type: str      # the terminal: num, id, =, +, -, *, /, (, ), or $
    value: str     # the text it came from
    col: int       # 1-indexed column


RULES = re.compile(r"(?P<skip>[ \t]+)|(?P<num>[0-9]+)|(?P<id>[a-zA-Z_][a-zA-Z0-9_]*)|(?P<sym>[=+\-*/()])")


def tokenize(source):
    tokens = []
    pos = 0
    while pos < len(source):
        m = RULES.match(source, pos)
        if m is None:
            raise LexError(source[pos], pos + 1)
        if m.lastgroup == "num":
            tokens.append(Token("num", m.group(), pos + 1))
        elif m.lastgroup == "id":
            tokens.append(Token("id", m.group(), pos + 1))
        elif m.lastgroup == "sym":
            tokens.append(Token(m.group(), m.group(), pos + 1))
        pos = m.end()
    tokens.append(Token("$", "", pos + 1))
    return tokens
