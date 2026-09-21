"""CS374 Interpreter assignment: starter file.

Everything here is already printed in the assignment page; it is collected
into one file so that you spend your time on the evaluator rather than on
transcription.  Nothing is finished for you: every TODO is still yours.

Build order (see the assignment): Step 1b dispatch, then Steps 2a-2d, then
Step 5a's error audit.
"""

from ast_nodes import *


# --- Step 5a: the language-level error hierarchy ---------------------------
# Defined up front because Environment raises LangNameError below.  Step 5a
# has you audit every raise in this file to carry a class, a message naming
# the offending value, and a line and column.

class LangError(Exception):
    def __init__(self, message, line=0, col=0):
        self.message = message
        self.line = line
        self.col = col

    def __str__(self):
        return f"line {self.line}, col {self.col}: {self.message}"


class LangNameError(LangError): pass
class LangTypeError(LangError): pass
class LangZeroDivisionError(LangError): pass
class LangRuntimeError(LangError): pass


class InterpreterError(Exception):
    """Raised when the evaluator meets a node class it has no branch for."""
    pass


# --- Step 2d: loop control signals -----------------------------------------
# Exceptions, because break and continue have to unwind out of however many
# nested evaluation calls the loop body happens to be deep in.

class BreakSignal(Exception): pass
class ContinueSignal(Exception): pass


# --- Step 2c: the Environment ----------------------------------------------
# This is the class you built and tested in the Environments and Scope lab.
# If you did that lab, drop your version in here; the tests you already wrote
# should still pass.

class Environment:
    def __init__(self, parent=None):
        self._bindings = {}
        self._parent = parent

    def define(self, name: str, value):
        """Create a new binding in THIS scope (used by Let)."""
        self._bindings[name] = value

    def lookup(self, name: str):
        """Search this scope then parent scopes; raise LangNameError if not found."""
        if name in self._bindings:
            return self._bindings[name]
        if self._parent:
            return self._parent.lookup(name)
        raise LangNameError(f"Undefined variable '{name}'")

    def assign(self, name: str, value):
        """Update an existing binding wherever it lives; raise LangNameError if not found."""
        if name in self._bindings:
            self._bindings[name] = value
        elif self._parent:
            self._parent.assign(name, value)
        else:
            raise LangNameError(f"Cannot assign to undefined variable '{name}'")


# --- Steps 1b and 2a-2d: the evaluator -------------------------------------

class Interpreter:
    def __init__(self):
        self.globals = Environment()

    def eval_node(self, node, env=None):
        if env is None:
            env = self.globals

        if isinstance(node, Num):
            raise NotImplementedError("Num")
        elif isinstance(node, Str):
            raise NotImplementedError("Str")
        elif isinstance(node, Program):
            raise NotImplementedError("Program")
        # TODO: one elif branch per remaining node type from Step 1a.
        #       BoolLit, Var, BinOp, UnaryOp, LogicOp, Let, Assign, Print,
        #       Block, If, While, Break, Continue
        else:
            raise InterpreterError(f"Unknown node type: {type(node).__name__}")

    def truthy(self, value):
        """Your truthiness policy from Part 0, in one place so it stays consistent."""
        raise NotImplementedError("truthy")
