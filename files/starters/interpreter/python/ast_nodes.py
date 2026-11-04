"""CS374 Interpreter assignment: the AST node classes.  This file is complete."""

from dataclasses import dataclass, field
from typing import Any, List


@dataclass
class Num:
    value: Any                                      # a Python int or float
    line: int = field(default=0, compare=False)


@dataclass
class BoolLit:
    value: bool
    line: int = field(default=0, compare=False)


@dataclass
class Var:
    name: str
    line: int = field(default=0, compare=False)


@dataclass
class BinOp:
    op: str                                         # + - * / < <= > >= == !=
    left: Any
    right: Any
    line: int = field(default=0, compare=False)


@dataclass
class UnaryOp:
    op: str                                         # - or not
    operand: Any
    line: int = field(default=0, compare=False)


@dataclass
class LogicOp:
    op: str                                         # and or or, separate from BinOp because they short-circuit
    left: Any
    right: Any
    line: int = field(default=0, compare=False)


@dataclass
class Let:
    name: str
    value: Any
    line: int = field(default=0, compare=False)


@dataclass
class Assign:
    name: str
    value: Any
    line: int = field(default=0, compare=False)


@dataclass
class Print:
    value: Any
    line: int = field(default=0, compare=False)


@dataclass
class Block:
    stmts: List[Any] = field(default_factory=list)
    line: int = field(default=0, compare=False)


@dataclass
class If:
    condition: Any
    then_branch: Any                                # always a Block
    else_branch: Any                                # a Block, another If, or None
    line: int = field(default=0, compare=False)


@dataclass
class While:
    condition: Any
    body: Any                                       # always a Block
    line: int = field(default=0, compare=False)


@dataclass
class Break:
    line: int = field(default=0, compare=False)


@dataclass
class Continue:
    line: int = field(default=0, compare=False)


@dataclass
class Program:
    stmts: List[Any] = field(default_factory=list)
