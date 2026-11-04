"""CS374 Interpreter assignment: the evaluator.

The lexer, parser, and node classes are complete, so this is the file you write.
Every TODO is yours, and the assignment page walks through them in order.
"""

from ast_nodes import *


class LangError(Exception):
    """A language-level error, carrying the source line."""
    def __init__(self, message, line=0):
        super().__init__(message)
        self.message = message
        self.line = line


class LangNameError(LangError): pass
class LangTypeError(LangError): pass
class LangZeroDivisionError(LangError): pass
class LangRuntimeError(LangError): pass


class BreakSignal(Exception):
    """Raised by a Break node; caught by the nearest enclosing While."""
    def __init__(self, line=0):
        super().__init__("break")
        self.line = line


class ContinueSignal(Exception):
    """Raised by a Continue node; caught by the nearest enclosing While."""
    def __init__(self, line=0):
        super().__init__("continue")
        self.line = line


def is_number(value):
    """True for int and float.  bool is a subclass of int in Python, so rule it out."""
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def type_name(value):
    """The name your error messages print: bool or num."""
    return "bool" if isinstance(value, bool) else "num"


def format_value(value):
    """The text print shows: true or false, and 3 rather than 3.0."""
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    return str(value)


class Environment:
    """One scope: a table of names, plus a link to the scope that encloses it."""
    def __init__(self, parent=None):
        self._bindings = {}
        self._parent = parent

    def define(self, name, value):
        """Create a binding in THIS scope.  let uses this."""
        # TODO (Step 4)
        raise NotImplementedError("define")

    def lookup(self, name, line=0):
        """Return the nearest binding's value, or raise LangNameError."""
        # TODO (Step 4)
        raise NotImplementedError("lookup")

    def assign(self, name, value, line=0):
        """Change the nearest existing binding, or raise LangNameError.  It never creates one."""
        # TODO (Step 4)
        raise NotImplementedError("assign")


class Interpreter:
    def __init__(self):
        self.globals = Environment()   # one scope for the top level of the program

    def eval_node(self, node, env=None):
        if env is None:
            env = self.globals

        if isinstance(node, Program):
            for stmt in node.stmts:
                self.eval_node(stmt, env)
        elif isinstance(node, Num):
            return node.value
        # TODO (Step 1): BoolLit and Print
        # TODO (Step 2): UnaryOp "-" and BinOp + - * /
        # TODO (Step 3): BinOp comparisons, LogicOp, and UnaryOp "not"
        # TODO (Step 4): Var, Let, Assign, and Block
        # TODO (Step 5): If and While
        # TODO (Step 6): Break and Continue
        else:
            raise NotImplementedError(type(node).__name__)

    def truthy(self, value):
        """false and 0 are false, and everything else is true."""
        # TODO (Step 3)
        raise NotImplementedError("truthy")
