"""tokens.py -- the Token dataclass shared by the whole pipeline.

Reference implementation for CS374 (Ursinus College).
Matches the Lexer assignment contract (Step 1b):

* ``type``  -- the token type name (e.g. ``"LET"``, ``"IDENT"``, ``"EOF"``)
* ``value`` -- the RAW lexeme exactly as it appeared in the source
* ``line``  -- 1-indexed line of the first character of the lexeme
* ``col``   -- 1-indexed column of the first character of the lexeme
* ``decoded`` -- for STRING tokens only: the decoded value with escape
  sequences resolved (``\\n`` becomes a real newline, etc.).  ``None`` for
  every other token type.  The assignment requires storing *both* the raw
  lexeme and the decoded value; this extra field is how the reference
  implementation does it.

The EOF token has ``type == "EOF"``, ``value == ""`` and the line/col of
the position one past the last character consumed (matching the worked
example in the assignment, where ``"let x = 42;"`` yields EOF at col 12).
"""

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class Token:
    type: str                    # token type name, e.g. "LET", "IDENT", "EOF"
    value: str                   # the raw lexeme as matched in the source
    line: int                    # 1-indexed line of the lexeme's first char
    col: int                     # 1-indexed column of the lexeme's first char
    decoded: Optional[str] = None  # decoded value (STRING tokens only)
