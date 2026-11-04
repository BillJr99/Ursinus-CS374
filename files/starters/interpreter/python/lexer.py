"""CS374 Interpreter assignment: the lexer.  This file is complete.

tokenize(source) returns a list of Tokens that always ends with an EOF token.
"""

import re
from dataclasses import dataclass


class LexError(Exception):
    """Raised on a character the language does not allow."""
    def __init__(self, message, line):
        super().__init__(message)
        self.message = message
        self.line = line


@dataclass
class Token:
    type: str
    value: str
    line: int


KEYWORDS = {"let", "print", "if", "else", "while", "break", "continue",
            "true", "false", "and", "or", "not"}
RULES = re.compile(r"""
    (?P<SKIP>[ \t\n]+|\#[^\n]*)
  | (?P<NUM>[0-9]+(?:\.[0-9]+)?)
  | (?P<WORD>[A-Za-z_][A-Za-z0-9_]*)
  | (?P<OP><=|>=|==|!=|[-+*/<>=;(){}])
""", re.VERBOSE)


def tokenize(source):
    tokens = []
    pos, line = 0, 1
    while pos < len(source):
        m = RULES.match(source, pos)
        if m is None:
            raise LexError(f"unexpected character '{source[pos]}'", line)
        text = m.group()
        if m.lastgroup == "NUM":
            tokens.append(Token("NUM", text, line))
        elif m.lastgroup == "WORD":
            tokens.append(Token(text if text in KEYWORDS else "ID", text, line))
        elif m.lastgroup == "OP":
            tokens.append(Token(text, text, line))
        line += text.count("\n")
        pos = m.end()
    tokens.append(Token("EOF", "", line))
    return tokens
