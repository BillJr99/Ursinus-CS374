"""The tree's node classes.  Each one remembers its line and column for error messages."""
from dataclasses import dataclass


@dataclass
class Num:
    value: float
    line: int
    col: int


@dataclass
class Var:
    name: str
    line: int
    col: int


@dataclass
class BinOp:
    op: str
    left: object
    right: object
    line: int
    col: int


@dataclass
class Let:
    name: str
    value: object
    line: int
    col: int


@dataclass
class Print:
    value: object
    line: int
    col: int
