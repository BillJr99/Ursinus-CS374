"""Interpreter: walks the tree.  One case per node class."""
from ast_nodes import BinOp, Let, Num, Print, Var
from lexer import LangError
from parser import parse


def evaluate(node, env):
    """Return the value of an expression node."""
    if isinstance(node, Num):
        return node.value
    if isinstance(node, Var):
        if node.name not in env:
            raise LangError("Runtime", f"undefined variable {node.name!r}", node.line, node.col)
        return env[node.name]
    if isinstance(node, BinOp):
        left = evaluate(node.left, env)
        right = evaluate(node.right, env)
        if node.op == "+":
            return left + right
        if node.op == "-":
            return left - right
        if node.op == "*":
            return left * right
        if right == 0:
            raise LangError("Runtime", "division by zero", node.line, node.col)
        return left / right
    raise TypeError(f"no evaluate case for {type(node).__name__}")


def execute(node, env, output=print):
    """Run one statement node."""
    if isinstance(node, Let):
        env[node.name] = evaluate(node.value, env)
    elif isinstance(node, Print):
        output(show(evaluate(node.value, env)))
    else:
        raise TypeError(f"no execute case for {type(node).__name__}")


def show(value):
    """Print whole numbers without a trailing .0."""
    return str(int(value)) if value == int(value) else str(value)


def run(source, env=None, output=print):
    """Parse source and run it.  Pass an env to keep variables between calls, as the REPL does."""
    env = {} if env is None else env
    for stmt in parse(source):
        execute(stmt, env, output)
