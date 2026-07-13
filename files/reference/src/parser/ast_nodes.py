"""ast_nodes.py -- AST node dataclasses for the CS374 project language.

Reference implementation. The node inventory reconciles the Parser
assignment (Step 2a) with the Interpreter assignment (Step 1a): it
includes the optional Str / BoolLit / LogicOp nodes (the interpreter
requires LogicOp to be separate from BinOp for short-circuit evaluation)
and the Break / Continue nodes the interpreter adds.

Design decision: every node carries source-position fields
``line``/``col`` declared with ``compare=False``, so two trees that
differ only in positions are structurally equal. This keeps the
round-trip law ``parse(unparse(parse(s))) == parse(s)`` a plain ``==``
even though unparsing does not preserve exact positions.
"""

from dataclasses import dataclass, field
from typing import Any, List, Optional


def _pos():
    return field(default=0, compare=False)


# -- expressions -------------------------------------------------------------

@dataclass
class Num:
    value: Any            # the numeric value, already parsed (int or float)
    line: int = _pos()    # 1-indexed source line (0 if synthesized)
    col: int = _pos()     # 1-indexed source column


@dataclass
class Str:
    value: str            # decoded string value (escape sequences resolved)
    line: int = _pos()
    col: int = _pos()


@dataclass
class BoolLit:
    value: bool           # True or False
    line: int = _pos()
    col: int = _pos()


@dataclass
class Var:
    name: str             # variable name as it appears in source
    line: int = _pos()
    col: int = _pos()


@dataclass
class BinOp:
    op: str               # one of: + - * / < <= > >= == !=
    left: Any             # left operand expression
    right: Any            # right operand expression
    line: int = _pos()
    col: int = _pos()


@dataclass
class UnaryOp:
    op: str               # "-" or "not"
    operand: Any          # the operand expression
    line: int = _pos()
    col: int = _pos()


@dataclass
class LogicOp:
    op: str               # "and" or "or" -- separate from BinOp for short-circuit
    left: Any             # left operand expression
    right: Any            # right operand expression (may never be evaluated!)
    line: int = _pos()
    col: int = _pos()


# -- statements --------------------------------------------------------------

@dataclass
class Let:
    name: str             # variable name being defined (new binding)
    value: Any            # initializer expression
    line: int = _pos()
    col: int = _pos()


@dataclass
class Assign:
    name: str             # variable name being updated (must already exist)
    value: Any            # new value expression
    line: int = _pos()
    col: int = _pos()


@dataclass
class Print:
    value: Any            # expression to evaluate and print
    line: int = _pos()


@dataclass
class Block:
    stmts: List[Any] = field(default_factory=list)  # statements, in order
    line: int = _pos()


@dataclass
class If:
    condition: Any        # test expression
    then_branch: Any      # always a Block
    else_branch: Any = None  # Block, If (else-if chain), or None
    line: int = _pos()


@dataclass
class While:
    condition: Any        # test expression, re-evaluated each iteration
    body: Any = None      # always a Block
    line: int = _pos()


@dataclass
class Break:
    line: int = _pos()    # source line, for "break outside loop" errors


@dataclass
class Continue:
    line: int = _pos()


@dataclass
class Program:
    stmts: List[Any] = field(default_factory=list)  # top-level statements
