"""lexer.py -- reference Lexer for the CS374 project language.

This is the first permanent component of the language pipeline.  The
Parser imports it unchanged through exactly three methods:

    peek()               -> Token   (idempotent; never consumes)
    advance()            -> Token   (consume and return the next token)
    expect(token_type)   -> Token   (advance if it matches, else LexError)

At end of input both ``peek`` and ``advance`` return the EOF token
forever -- they never raise StopIteration or return None.

Error modes (selected at construction time):

    Lexer(src)                              # fail_fast (default)
    Lexer(src, error_mode="collect_all")    # gather every error, then
                                            # raise one LexErrorList

In ``fail_fast`` mode the source is tokenized lazily, so the LexError
surfaces from the first ``peek``/``advance`` that reaches the offending
character.  In ``collect_all`` mode the entire source is tokenized in a
single pass at construction time; if any errors were recorded the
constructor raises ``LexErrorList``, which carries both ``.errors`` (the
list of LexErrors) and ``.tokens`` (every token that was still
recognized, demonstrating recovery).

A JSON token specification may be supplied via ``config_path``; see
``token_spec.json`` (default dialect) and ``token_spec_alt.json``
(``//`` comments, ``:=`` assignment) for the format.

Python 3.10+, standard library only.  Importing this module has no side
effects.
"""

import json
import re
from typing import Iterator, List, Optional, Tuple

from tokens import Token


class LexError(Exception):
    """A lexical error with a precise 1-indexed position.

    ``str(err)`` renders the assignment's required format, e.g.::

        LexError at line 3, col 7: unexpected character '@'
    """

    def __init__(self, message: str, line: int = 0, col: int = 0):
        self.message = message
        self.line = line
        self.col = col
        super().__init__(str(self))

    def __str__(self) -> str:
        return f"LexError at line {self.line}, col {self.col}: {self.message}"


class LexErrorList(Exception):
    """Raised in collect_all mode after the whole source has been scanned.

    Attributes:
        errors -- list of LexError, in source order
        tokens -- every token that was still successfully recognized
                  (recovery evidence: lexing continued past each error)
    """

    def __init__(self, errors: List[LexError], tokens: List[Token]):
        self.errors = errors
        self.tokens = tokens
        summary = "; ".join(str(e) for e in errors)
        super().__init__(f"{len(errors)} lexical error(s): {summary}")


# ---------------------------------------------------------------------------
# Default token specification (ordered!).
#
# Ordering rules (Part 1 of the assignment):
#   * COMMENT and WHITESPACE first (skipped).
#   * FLOAT before INT (else "3.14" lexes as INT(3) '.' INT(14)).
#   * Keywords before IDENT, each with a \b boundary so "iffy" is an IDENT.
#   * Multi-character operators (<= >= == !=) before their one-char prefixes.
#
# NOTE (spec reconciliation): the Parser assignment's grammar uses OR, AND
# and NOT tokens, and the Interpreter assignment adds Break/Continue nodes.
# The lexer assignment's minimum table omits them, so this reference spec
# adds the keywords AND, OR, NOT, BREAK, CONTINUE (before IDENT, like every
# other keyword) so the same component serves all three assignments.
# ---------------------------------------------------------------------------
TOKEN_SPEC: List[Tuple[str, str]] = [
    ("COMMENT",    r"#[^\n]*"),
    ("WHITESPACE", r"[ \t\r\n]+"),
    ("STRING",     r'"(?:[^"\\\n]|\\.)*"'),
    ("FLOAT",      r"(?:\d+\.\d*|\.\d+)"),
    ("INT",        r"\d+"),
    ("IF",         r"if\b"),
    ("ELSE",       r"else\b"),
    ("WHILE",      r"while\b"),
    ("LET",        r"let\b"),
    ("PRINT",      r"print\b"),
    ("TRUE",       r"true\b"),
    ("FALSE",      r"false\b"),
    ("AND",        r"and\b"),
    ("OR",         r"or\b"),
    ("NOT",        r"not\b"),
    ("BREAK",      r"break\b"),
    ("CONTINUE",   r"continue\b"),
    ("IDENT",      r"[A-Za-z_][A-Za-z0-9_]*"),
    ("LE",         r"<="),
    ("GE",         r">="),
    ("EQEQ",       r"=="),
    ("NEQ",        r"!="),
    ("EQ",         r"="),
    ("LT",         r"<"),
    ("GT",         r">"),
    ("PLUS",       r"\+"),
    ("MINUS",      r"-"),
    ("STAR",       r"\*"),
    ("SLASH",      r"/"),
    ("LPAREN",     r"\("),
    ("RPAREN",     r"\)"),
    ("LBRACE",     r"\{"),
    ("RBRACE",     r"\}"),
    ("SEMICOLON",  r";"),
]

_SKIP_TYPES = {"COMMENT", "WHITESPACE"}

_ESCAPES = {'"': '"', "\\": "\\", "n": "\n", "t": "\t"}


def decode_string(raw: str, line: int, col: int) -> str:
    """Decode a raw STRING lexeme (including its quotes) to its value.

    Supports exactly the four escapes required by the assignment:
    \\" (quote), \\\\ (backslash), \\n (newline), \\t (tab).
    Any other escape sequence raises a LexError positioned at the string's
    opening quote (an interface decision; the assignment leaves unknown
    escapes unspecified, and erroring loudly beats silent surprises).
    """
    body = raw[1:-1]
    out = []
    i = 0
    while i < len(body):
        ch = body[i]
        if ch == "\\":
            if i + 1 >= len(body):  # cannot happen with the STRING regex
                raise LexError("dangling backslash in string literal", line, col)
            esc = body[i + 1]
            if esc not in _ESCAPES:
                raise LexError(f"unsupported escape sequence '\\{esc}' in string literal",
                               line, col)
            out.append(_ESCAPES[esc])
            i += 2
        else:
            out.append(ch)
            i += 1
    return "".join(out)


def _compile_spec(spec: List[Tuple[str, str]]) -> List[Tuple[str, "re.Pattern"]]:
    compiled = []
    for name, pattern in spec:
        try:
            compiled.append((name, re.compile(pattern)))
        except re.error as exc:
            raise LexError(f"invalid pattern for token {name}: {pattern!r} ({exc})")
    return compiled


def _core_tokenize(source: str,
                   spec: List[Tuple[str, str]],
                   errors: Optional[List[LexError]] = None) -> Iterator[Token]:
    """Ordered-rules / maximal-munch scanner.

    Yields every non-skipped token, then a single EOF token.  If ``errors``
    is a list (collect_all mode), unrecognized characters are recorded there
    and skipped; otherwise (fail_fast) the first one raises LexError.
    """
    compiled = _compile_spec(spec)
    pos, line, col = 0, 1, 1
    n = len(source)
    while pos < n:
        for name, regex in compiled:
            m = regex.match(source, pos)
            if m and m.end() > pos:
                text = m.group(0)
                if name not in _SKIP_TYPES:
                    if name == "STRING":
                        yield Token(name, text, line, col,
                                    decoded=decode_string(text, line, col))
                    else:
                        yield Token(name, text, line, col)
                # advance the position and the line/col counters
                newlines = text.count("\n")
                if newlines:
                    line += newlines
                    col = len(text) - text.rfind("\n")
                else:
                    col += len(text)
                pos = m.end()
                break
        else:
            ch = source[pos]
            if ch == '"':
                err = LexError("unterminated string literal", line, col)
            else:
                err = LexError(f"unexpected character {ch!r}", line, col)
            if errors is None:
                raise err
            errors.append(err)
            # recover: skip the offending character and continue the pass
            if ch == "\n":
                line += 1
                col = 1
            else:
                col += 1
            pos += 1
    yield Token("EOF", "", line, col)


def tokenize(source: str) -> Iterator[Token]:
    """Baseline generator from Step 1c: default spec, fail-fast."""
    return _core_tokenize(source, TOKEN_SPEC)


class Lexer:
    """The reusable Lexer component (Part 2 of the assignment)."""

    def __init__(self, source: str, config_path: Optional[str] = None,
                 error_mode: str = "fail_fast"):
        if error_mode not in ("fail_fast", "collect_all"):
            raise ValueError(f"unknown error_mode: {error_mode!r}")
        self.source = source
        self.error_mode = error_mode
        self.spec = self._load_config(config_path) if config_path else TOKEN_SPEC
        _compile_spec(self.spec)  # validate every pattern up front
        self._buffer: Optional[Token] = None  # one-token lookahead
        self._eof: Optional[Token] = None
        if error_mode == "collect_all":
            errors: List[LexError] = []
            self.tokens = list(_core_tokenize(source, self.spec, errors))
            if errors:
                raise LexErrorList(errors, self.tokens)
            self._stream = iter(self.tokens)
        else:
            self._stream = _core_tokenize(source, self.spec)

    # -- configuration ----------------------------------------------------
    @staticmethod
    def _load_config(config_path: str) -> List[Tuple[str, str]]:
        with open(config_path, "r", encoding="utf-8") as fh:
            config = json.load(fh)
        if "tokens" not in config or not isinstance(config["tokens"], list):
            raise LexError(f"config {config_path!r} is missing a 'tokens' list")
        return [(name, pattern) for name, pattern in config["tokens"]]

    # -- the interface contract -------------------------------------------
    def _pull(self) -> Token:
        if self._eof is not None:
            return self._eof            # EOF forever
        tok = next(self._stream)
        if tok.type == "EOF":
            self._eof = tok
        return tok

    def peek(self) -> Token:
        """Return the next token WITHOUT consuming it (idempotent)."""
        if self._buffer is None:
            self._buffer = self._pull()
        return self._buffer

    def advance(self) -> Token:
        """Consume and return the next token (EOF forever at end)."""
        tok = self.peek()
        self._buffer = None
        return tok

    def expect(self, token_type: str) -> Token:
        """Consume the next token if it matches, else raise a located LexError."""
        tok = self.peek()
        if tok.type != token_type:
            raise LexError(f"expected {token_type}, found {tok.type}",
                           tok.line, tok.col)
        return self.advance()
