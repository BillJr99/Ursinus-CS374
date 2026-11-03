"""scope_lab.py: the starter for the CS374 lab Environments and Type Checking.

One scope table, two jobs.  Part 1 builds Environment, the table that maps
names to values in nested scopes.  Part 2 reuses the very same class to map
names to *types*, and uses it to check a small program before it runs.

Everything is written for you except the bodies marked TODO:

    Part 1:  Environment.define, Environment.lookup, Environment.assign
    Part 2:  check_expr (literals, variables, binary operators)
             check_condition (the condition of an if or a while)

Run the provided tests from this folder after each method you finish:

    python3 test_scope_lab.py

The tests are numbered in the order you write the methods, so they turn from
FAIL to ok one at a time.
"""

from dataclasses import dataclass, field
from typing import Any, List, Optional


# ===========================================================================
# Errors (written for you)
# ===========================================================================

class LangError(Exception):
    """Base class for every language-level error (same shape as Interpreter Step 5a)."""

    def __init__(self, message, line=0, col=0):
        self.message = message
        self.line = line      # the evaluator fills these in later
        self.col = col
        super().__init__(str(self))

    def __str__(self):
        return f"line {self.line}, col {self.col}: {self.message}"


class LangNameError(LangError):
    """Raised when a name has no binding anywhere in the chain."""


class LangTypeError(LangError):
    """Raised by the checker on the first type error it finds."""

    def __str__(self):
        return f"Type error at line {self.line}, col {self.col}: {self.message}"


# ===========================================================================
# Part 1: the scope table
# ===========================================================================

class Environment:
    """One scope: a table of bindings plus a link to the enclosing scope.

    In Part 1 a binding maps a name to a value, such as {"x": 2}.
    In Part 2 the same class maps a name to a type name, such as {"x": "Num"}.
    The class never looks at what it stores, so it works for both.
    """

    def __init__(self, parent=None):
        self._bindings = {}     # name -> value (or type), for THIS scope only
        self._parent = parent   # the enclosing Environment, or None at top level

    def define(self, name, value):
        """Create name in THIS scope, shadowing any outer binding of the same name."""
        # TODO (Part 1, Step 1.2): store value under name in this scope's table.
        #      Do not look at the parent.
        raise NotImplementedError("define")

    def lookup(self, name):
        """Return the value of the nearest binding of name, or raise LangNameError."""
        # TODO (Part 1, Step 1.2):
        #   1. If name is bound in this scope, return its value.
        #   2. Otherwise, if there is a parent, return the parent's lookup of name.
        #   3. Otherwise raise LangNameError with a message that contains the name,
        #      such as f"Undefined variable '{name}'".
        raise NotImplementedError("lookup")

    def assign(self, name, value):
        """Update the nearest binding of name.  Never creates a binding."""
        # TODO (Part 1, Step 1.3):
        #   1. If name is bound in this scope, update it here and stop.
        #   2. Otherwise, if there is a parent, hand the assignment to the parent.
        #   3. Otherwise raise LangNameError with a message that contains the name,
        #      such as f"Cannot assign to undefined variable '{name}'".
        raise NotImplementedError("assign")


# ===========================================================================
# The AST (written for you)
#
# A small copy of the class AST: the same node names and field names as the
# class ast_nodes.py, plus the optional annotation on Let.  To run the
# checker on trees from your own parser later, replace this section with
#     from ast_nodes import *
# ===========================================================================

def _pos():
    return field(default=0, compare=False)


@dataclass
class Num:
    value: Any
    line: int = _pos()
    col: int = _pos()


@dataclass
class Str:
    value: str
    line: int = _pos()
    col: int = _pos()


@dataclass
class BoolLit:
    value: bool
    line: int = _pos()
    col: int = _pos()


@dataclass
class Var:
    name: str
    line: int = _pos()
    col: int = _pos()


@dataclass
class BinOp:
    op: str               # one of: + - * / < <= > >= == !=
    left: Any
    right: Any
    line: int = _pos()
    col: int = _pos()


@dataclass
class UnaryOp:            # used only in the optional extension
    op: str               # "-" or "not"
    operand: Any
    line: int = _pos()
    col: int = _pos()


@dataclass
class LogicOp:            # used only in the optional extension
    op: str               # "and" or "or"
    left: Any
    right: Any
    line: int = _pos()
    col: int = _pos()


@dataclass
class Let:
    name: str
    value: Any
    annotation: Optional[str] = None   # "Num", "Str", "Bool", or None
    line: int = _pos()
    col: int = _pos()


@dataclass
class Assign:             # used only in the optional extension
    name: str
    value: Any
    line: int = _pos()
    col: int = _pos()


@dataclass
class Print:
    value: Any
    line: int = _pos()


@dataclass
class Block:
    stmts: List[Any] = field(default_factory=list)
    line: int = _pos()


@dataclass
class If:
    condition: Any
    then_branch: Any
    else_branch: Any = None
    line: int = _pos()


@dataclass
class While:
    condition: Any
    body: Any = None
    line: int = _pos()


@dataclass
class Program:
    stmts: List[Any] = field(default_factory=list)


# ===========================================================================
# Part 2: the type checker
# ===========================================================================

NUM, STR, BOOL = "Num", "Str", "Bool"   # the three types this checker knows
ARITHMETIC = ("+", "-", "*", "/")       # Num and Num give Num
COMPARISON = ("<", "<=", ">", ">=")     # Num and Num give Bool
EQUALITY = ("==", "!=")                 # two equal types give Bool


def check(program):
    """Well typed: return silently.  Ill typed: raise LangTypeError."""
    tenv = Environment()                 # the Part 1 scope table, holding types
    for stmt in program.stmts:
        check_stmt(stmt, tenv)


def check_stmt(node, tenv):
    """Check one statement (written for you).  Statements have no type."""
    if isinstance(node, Print):
        check_expr(node.value, tenv)
    elif isinstance(node, Let):
        actual = check_expr(node.value, tenv)
        declared = node.annotation if node.annotation is not None else actual
        if declared is not None and actual is not None and declared != actual:
            raise LangTypeError(
                f"'{node.name}' declared {declared}, but its initializer has type {actual}",
                node.line, node.col)
        tenv.define(node.name, declared)          # the annotation is what binds
    elif isinstance(node, Block):
        inner = Environment(parent=tenv)          # a block opens a new scope
        for stmt in node.stmts:
            check_stmt(stmt, inner)
    elif isinstance(node, If):
        check_condition(node.condition, "if", tenv)
        check_stmt(node.then_branch, tenv)
        if node.else_branch is not None:
            check_stmt(node.else_branch, tenv)
    elif isinstance(node, While):
        check_condition(node.condition, "while", tenv)
        check_stmt(node.body, tenv)
    else:
        raise NotImplementedError(f"no typing rule for {type(node).__name__}")


def check_expr(node, tenv):
    """Return the type of an expression: NUM, STR, BOOL, or None for unknown.

    Raise LangTypeError at the node's own line and col when a rule fails.
    """
    if isinstance(node, Num):
        return NUM                    # the model rule: a literal needs nothing from tenv

    # TODO (Part 2, Step 2.2): literals.  A Str is STR, and a BoolLit is BOOL.

    # TODO (Part 2, Step 2.2): variables.  Look node.name up in tenv, the Part 1
    #      scope table.  A name no scope declares has the unknown type None:
    #      catch the LangNameError and return None.  The evaluator reports
    #      undefined names when the program runs.

    # TODO (Part 2, Step 2.3): binary operators.  Type both operands, then:
    #      ARITHMETIC needs Num and Num and gives NUM;
    #      COMPARISON needs Num and Num and gives BOOL;
    #      EQUALITY needs two equal types and gives BOOL.
    #      If either operand is None, skip the check and return the result type.
    #      A failed check raises LangTypeError at node.line, node.col with a
    #      message that names the operator and BOTH operand types, such as
    #      "'+' requires Num operands, got Num and Bool".

    raise NotImplementedError(f"no typing rule yet for {type(node).__name__}")


def check_condition(cond, keyword, tenv):
    """Check the condition of an if or a while (keyword is "if" or "while")."""
    # TODO (Part 2, Step 2.4): type cond.  If its type is known and is not BOOL,
    #      raise LangTypeError at cond.line, cond.col with a message that names
    #      the keyword and the type, such as "while condition must be Bool, got Num".
    raise NotImplementedError("check_condition")

