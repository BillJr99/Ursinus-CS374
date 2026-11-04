"""Lexer: turns source text into a list of tokens."""
import re
from dataclasses import dataclass


class LangError(Exception):
    """An error that knows its stage and where it happened."""

    def __init__(self, stage, message, line, col):
        super().__init__(f"{stage} error at line {line}, col {col}: {message}")


@dataclass
class Token:
    type: str
    value: str
    line: int
    col: int


# The first rule that matches wins, so keywords come before IDENT.
TOKEN_SPEC = [
    ("COMMENT",    r"#[^\n]*"),
    ("WHITESPACE", r"[ \t\n]+"),
    ("NUM",        r"[0-9]+(?:\.[0-9]+)?"),
    ("LET",        r"let(?!\w)"),
    ("PRINT",      r"print(?!\w)"),
    ("IDENT",      r"[a-zA-Z_]\w*"),
    ("PLUS",       r"\+"),
    ("MINUS",      r"-"),
    ("STAR",       r"\*"),
    ("SLASH",      r"/"),
    ("EQ",         r"="),
    ("LPAREN",     r"\("),
    ("RPAREN",     r"\)"),
    ("SEMICOLON",  r";"),
]
COMPILED = [(name, re.compile(pattern)) for name, pattern in TOKEN_SPEC]
SKIPPED = {"COMMENT", "WHITESPACE"}


def tokenize(source):
    """Return every token in source, ending with an EOF token."""
    tokens = []
    pos, line, col = 0, 1, 1
    while pos < len(source):
        for name, pattern in COMPILED:
            m = pattern.match(source, pos)
            if m:
                break
        else:
            raise LangError("Lexical", f"unexpected character {source[pos]!r}", line, col)
        text = m.group()
        if name not in SKIPPED:
            tokens.append(Token(name, text, line, col))
        pos = m.end()
        newlines = text.count("\n")
        if newlines:
            line += newlines
            col = len(text) - text.rfind("\n")
        else:
            col += len(text)
    tokens.append(Token("EOF", "", line, col))
    return tokens
