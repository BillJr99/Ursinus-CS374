"""CS374 Parser assignment: the AST node classes.

This file is complete.  Part 3 builds these nodes as your driver reduces.  The
position fields print, but == skips them, so a test can write Num(8) and still
compare equal to a Num the parser built with a position.
"""

from dataclasses import dataclass, field
from typing import Any, List


@dataclass
class Num:
    value: int
    line: int = field(default=0, compare=False)
    col: int = field(default=0, compare=False)


@dataclass
class Var:
    name: str
    line: int = field(default=0, compare=False)
    col: int = field(default=0, compare=False)


@dataclass
class BinOp:
    op: str
    left: Any
    right: Any
    line: int = field(default=0, compare=False)
    col: int = field(default=0, compare=False)


@dataclass
class Let:
    name: str
    value: Any
    line: int = field(default=0, compare=False)


@dataclass
class Print:
    value: Any
    line: int = field(default=0, compare=False)


@dataclass
class Program:
    stmts: List[Any] = field(default_factory=list)
