"""CS374 Interpreter assignment, Part 4: the small static type checker.

This runs as its own pipeline stage, between parsing and evaluation, so a
type error is reported before any of the program runs.

If you did the Type Checker Starter lab, bring your checker core in here.
Part 4 then extends it to call sites, argument types, and declared return
types, which the lab does not cover.
"""

from ast_nodes import *
from interpreter import LangTypeError


class TypeEnv:
    """Mirrors Environment, but maps names to declared type names."""

    def __init__(self, parent=None):
        self._types = {}
        self._parent = parent

    # TODO: define(name, typ) and lookup(name), same shape as Environment


def check(node, tenv=None):
    """Return the type of an expression node; check a statement node and return None."""
    if tenv is None:
        tenv = TypeEnv()

    if isinstance(node, Num):
        return "Num"
    # TODO: Str -> "Str", BoolLit -> "Bool", Var -> tenv.lookup(...)
    # TODO: BinOp: arithmetic needs Num operands; comparisons yield Bool
    # TODO: LogicOp and UnaryOp("not") need Bool
    # TODO: Let: check the initializer against type_ann, then tenv.define
    # TODO: Block: check statements in TypeEnv(parent=tenv)
    # TODO: call sites: arity, argument types, declared return type
    raise NotImplementedError(f"no typing rule yet for {type(node).__name__}")
