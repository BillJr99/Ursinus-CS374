"""interp.py -- reference tree-walking interpreter for the CS374 language.

Contains the language-level error hierarchy (Step 4a), the Environment
class (Step 2c), the break/continue signal exceptions (Step 2d), and the
Interpreter with isinstance dispatch (Step 1b).

Documented semantics (the reference SEMANTICS decisions):

* Truthiness: ``false``, ``0``, ``0.0`` and ``""`` are falsy; everything
  else is truthy.
* ``and``/``or`` short-circuit and return the deciding OPERAND VALUE
  (like Python), not a coerced boolean. ``not`` always returns a boolean.
* ``+`` adds two numbers or concatenates two strings; anything else is a
  LangTypeError naming both operand types.
* ``-``, ``*``, ``/`` require numbers. ``/`` is true division and always
  produces a float; division by zero raises LangZeroDivisionError.
* ``<  <=  >  >=`` require numbers. ``==``/``!=`` compare any pair;
  operands of different types (bool is its own type, int/float are both
  "number") are simply unequal -- ``==`` returns false rather than raising.
* ``let`` defines a NEW binding in the current scope; bare assignment
  updates an EXISTING binding wherever it lives, and raises LangNameError
  if the name was never defined.
* Each block ``{ ... }`` gets a child environment, discarded at the end of
  the block; since a while body is a block, the loop body's scope is
  per-iteration. A ``let`` in the loop header's block does not survive
  the loop.
* ``break``/``continue`` outside a loop are LangRuntimeErrors.
* ``print`` renders booleans as ``true``/``false``, strings without
  quotes, ints without a decimal point, floats with one.

Python 3.10+, standard library only.
"""

from typing import Any, Optional

from ast_nodes import (Assign, BinOp, Block, BoolLit, Break, Continue, If,
                       Let, LogicOp, Num, Print, Program, Str, UnaryOp, Var,
                       While)


# ---------------------------------------------------------------------------
# Step 4a: the language-level error hierarchy
# ---------------------------------------------------------------------------

class LangError(Exception):
    """Base class for every runtime-stage language error."""

    def __init__(self, message: str, line: int = 0, col: int = 0):
        self.message = message
        self.line = line
        self.col = col
        super().__init__(str(self))

    def __str__(self) -> str:
        return f"line {self.line}, col {self.col}: {self.message}"


class LangNameError(LangError): pass
class LangTypeError(LangError): pass
class LangZeroDivisionError(LangError): pass
class LangRuntimeError(LangError): pass


class InterpreterError(LangRuntimeError):
    """Internal invariant violations (e.g. an unknown node type)."""


# ---------------------------------------------------------------------------
# Step 2d: break/continue signal exceptions
# ---------------------------------------------------------------------------

class BreakSignal(Exception):
    def __init__(self, line: int = 0):
        self.line = line
        super().__init__("break")


class ContinueSignal(Exception):
    def __init__(self, line: int = 0):
        self.line = line
        super().__init__("continue")


# ---------------------------------------------------------------------------
# Step 2c: the Environment
# ---------------------------------------------------------------------------

class Environment:
    def __init__(self, parent: Optional["Environment"] = None):
        self._bindings = {}
        self._parent = parent

    def define(self, name: str, value: Any) -> None:
        """Create a new binding in THIS scope (used by Let)."""
        self._bindings[name] = value

    def lookup(self, name: str) -> Any:
        """Search this scope then enclosing scopes; LangNameError if absent."""
        if name in self._bindings:
            return self._bindings[name]
        if self._parent is not None:
            return self._parent.lookup(name)
        raise LangNameError(f"Undefined variable '{name}'")

    def assign(self, name: str, value: Any) -> None:
        """Update an existing binding wherever it lives; LangNameError if absent."""
        if name in self._bindings:
            self._bindings[name] = value
        elif self._parent is not None:
            self._parent.assign(name, value)
        else:
            raise LangNameError(f"Cannot assign to undefined variable '{name}'")

    def __contains__(self, name: str) -> bool:
        if name in self._bindings:
            return True
        return self._parent is not None and name in self._parent


# ---------------------------------------------------------------------------
# value helpers
# ---------------------------------------------------------------------------

def is_number(value: Any) -> bool:
    """True for int/float; bool is deliberately NOT a number in this language."""
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def type_name(value: Any) -> str:
    if isinstance(value, bool):
        return "bool"
    if isinstance(value, int):
        return "int"
    if isinstance(value, float):
        return "float"
    if isinstance(value, str):
        return "str"
    return type(value).__name__


def truthy(value: Any) -> bool:
    """The documented truthiness rule: false, 0, 0.0, "" are falsy."""
    if isinstance(value, bool):
        return value
    if is_number(value):
        return value != 0
    if isinstance(value, str):
        return len(value) > 0
    return value is not None


def format_value(value: Any) -> str:
    """Render a value the way `print` and the REPL display it."""
    if isinstance(value, bool):
        return "true" if value else "false"
    return str(value)


def _same_type(a: Any, b: Any) -> bool:
    """Comparable-type check for ==/!=: bool with bool, number with number,
    str with str."""
    if isinstance(a, bool) or isinstance(b, bool):
        return isinstance(a, bool) and isinstance(b, bool)
    if is_number(a) and is_number(b):
        return True
    return isinstance(a, str) and isinstance(b, str)


# ---------------------------------------------------------------------------
# the evaluator
# ---------------------------------------------------------------------------

class Interpreter:
    def __init__(self, env: Optional[Environment] = None,
                 output=None):
        self.globals = env if env is not None else Environment()
        # output: a callable taking one string (a printed line). Defaults to
        # print(); injectable for tests.
        self._output = output if output is not None else print

    # -- entry points -------------------------------------------------------
    def run(self, program: Program) -> None:
        """Evaluate a whole Program in the global environment; stray
        break/continue signals become staged runtime errors."""
        try:
            self.eval_node(program, self.globals)
        except BreakSignal as sig:
            raise LangRuntimeError("'break' outside loop", sig.line)
        except ContinueSignal as sig:
            raise LangRuntimeError("'continue' outside loop", sig.line)

    # -- Step 1b: isinstance dispatch ----------------------------------------
    def eval_node(self, node: Any, env: Environment) -> Any:
        if isinstance(node, Num):
            return node.value
        if isinstance(node, Str):
            return node.value
        if isinstance(node, BoolLit):
            return node.value
        if isinstance(node, Var):
            try:
                return env.lookup(node.name)
            except LangNameError as err:
                raise LangNameError(err.message, node.line, node.col) from None
        if isinstance(node, BinOp):
            return self._eval_binop(node, env)
        if isinstance(node, UnaryOp):
            return self._eval_unaryop(node, env)
        if isinstance(node, LogicOp):
            return self._eval_logicop(node, env)
        if isinstance(node, Let):
            env.define(node.name, self.eval_node(node.value, env))
            return None
        if isinstance(node, Assign):
            value = self.eval_node(node.value, env)
            try:
                env.assign(node.name, value)
            except LangNameError as err:
                raise LangNameError(err.message, node.line, node.col) from None
            return None
        if isinstance(node, Print):
            self._output(format_value(self.eval_node(node.value, env)))
            return None
        if isinstance(node, Block):
            child_env = Environment(parent=env)
            for stmt in node.stmts:
                self.eval_node(stmt, child_env)
            return None
        if isinstance(node, If):
            if truthy(self.eval_node(node.condition, env)):
                self.eval_node(node.then_branch, env)
            elif node.else_branch is not None:
                self.eval_node(node.else_branch, env)
            return None
        if isinstance(node, While):
            while truthy(self.eval_node(node.condition, env)):
                try:
                    self.eval_node(node.body, env)
                except BreakSignal:
                    break
                except ContinueSignal:
                    continue
            return None
        if isinstance(node, Break):
            raise BreakSignal(node.line)
        if isinstance(node, Continue):
            raise ContinueSignal(node.line)
        if isinstance(node, Program):
            for stmt in node.stmts:
                self.eval_node(stmt, env)
            return None
        raise InterpreterError(f"Unknown node type: {type(node).__name__}")

    # -- operators ------------------------------------------------------------
    def _eval_binop(self, node: BinOp, env: Environment) -> Any:
        left = self.eval_node(node.left, env)
        right = self.eval_node(node.right, env)
        op = node.op
        lt, rt = type_name(left), type_name(right)

        if op == "+":
            if is_number(left) and is_number(right):
                return left + right
            if isinstance(left, str) and isinstance(right, str):
                return left + right
            raise LangTypeError(
                f"'+' requires two numbers or two strings, got {lt} and {rt}",
                node.line, node.col)
        if op in ("-", "*", "/"):
            if not (is_number(left) and is_number(right)):
                raise LangTypeError(f"'{op}' requires numbers, got {lt} and {rt}",
                                    node.line, node.col)
            if op == "-":
                return left - right
            if op == "*":
                return left * right
            if right == 0:
                raise LangZeroDivisionError("division by zero",
                                            node.line, node.col)
            return left / right   # true division: always a float
        if op in ("<", "<=", ">", ">="):
            if not (is_number(left) and is_number(right)):
                raise LangTypeError(f"'{op}' requires numbers, got {lt} and {rt}",
                                    node.line, node.col)
            return {"<": left < right, "<=": left <= right,
                    ">": left > right, ">=": left >= right}[op]
        if op == "==":
            return _same_type(left, right) and left == right
        if op == "!=":
            return not (_same_type(left, right) and left == right)
        raise InterpreterError(f"Unknown binary operator: {op!r}",
                               node.line, node.col)

    def _eval_unaryop(self, node: UnaryOp, env: Environment) -> Any:
        if node.op == "-":
            operand = self.eval_node(node.operand, env)
            if not is_number(operand):
                raise LangTypeError(
                    f"unary minus requires a number, got {type_name(operand)}",
                    node.line, node.col)
            return -operand
        if node.op == "not":
            return not truthy(self.eval_node(node.operand, env))
        raise InterpreterError(f"Unknown unary operator: {node.op!r}",
                               node.line, node.col)

    def _eval_logicop(self, node: LogicOp, env: Environment) -> Any:
        left = self.eval_node(node.left, env)
        if node.op == "and":
            if not truthy(left):
                return left                       # right is NOT evaluated
            return self.eval_node(node.right, env)
        if node.op == "or":
            if truthy(left):
                return left                       # right is NOT evaluated
            return self.eval_node(node.right, env)
        raise InterpreterError(f"Unknown logic operator: {node.op!r}",
                               node.line, node.col)
