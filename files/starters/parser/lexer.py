"""CS374 Parser assignment: the lexer for this assignment's grammar.

This file is complete, so that your parser does not depend on any earlier work.
tokenize(source) returns a list of Tokens that always ends with a "$" token.
A token's type is the terminal name the grammar uses.
"""

import re
from dataclasses import dataclass


class LexError(Exception):
    """Raised on a character the language does not allow."""
    def __init__(self, char, line, col):
        super().__init__(f"LexError at line {line}, col {col}: unexpected character {char!r}")
        self.line = line
        self.col = col


@dataclass
class Token:
    type: str      # the terminal: let, print, id, num, =, ;, +, -, *, (, ), or $
    value: str     # the text it came from
    line: int      # 1-indexed source line
    col: int       # 1-indexed source column


KEYWORDS = {"let", "print"}
RULES = re.compile(r"(?P<skip>[ \t\n]+|#[^\n]*)|(?P<num>[0-9]+)|(?P<word>[A-Za-z_][A-Za-z0-9_]*)|(?P<sym>[=;+\-*()])")


def tokenize(source):
    tokens = []
    pos, line, col = 0, 1, 1
    while pos < len(source):
        m = RULES.match(source, pos)
        if m is None:
            raise LexError(source[pos], line, col)
        text = m.group()
        if m.lastgroup == "num":
            tokens.append(Token("num", text, line, col))
        elif m.lastgroup == "word":
            tokens.append(Token(text if text in KEYWORDS else "id", text, line, col))
        elif m.lastgroup == "sym":
            tokens.append(Token(text, text, line, col))
        newlines = text.count("\n")
        if newlines:
            line += newlines
            col = len(text) - text.rfind("\n")
        else:
            col += len(text)
        pos = m.end()
    tokens.append(Token("$", "", line, col))
    return tokens
