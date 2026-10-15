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

    # TODO: define(name, typ) and lookup(name).  They behave like Environment's, with one
    #       difference: a name no scope declares has the unknown type None, not an error.


def check(node, tenv=None):
    """Return the type of an expression node; check a statement node and return None."""
    if tenv is None:
        tenv = TypeEnv()

    if isinstance(node, Num):
        return "Num"
    # TODO: one rule per node type, following the typing-rules table in Part 4 of the
    #       assignment page.  The Num rule above is the model.
    #   - the other literals, and variable references (an undeclared name is unknown, None;
    #     the Run stage reports it, and every rule skips its check when a side is None)
    #   - binary, logical, and unary operators: what each requires and what it produces
    #   - let with a type annotation, and blocks (a block opens a new scope for its body)
    #   - call sites: arity, argument types, and the declared return type
    raise NotImplementedError(f"no typing rule yet for {type(node).__name__}")
