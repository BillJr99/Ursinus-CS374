"""pretty.py -- pretty-printer and unparser for the CS374 AST.

pretty(node)  -> an indented structural rendering (two spaces per level),
                 matching the format shown in the Parser assignment.
unparse(node) -> valid source code that re-parses to a structurally equal
                 tree (the round-trip law).

Parenthesization rule (Step 3b): a child expression is wrapped in
parentheses when its operator binds LOOSER than its parent's (lower
precedence), or when it sits at the SAME precedence level and is the right
child of a left-associative operator. Comparisons are non-associative, so
a comparison child of a comparison is parenthesized on either side.
"""

from ast_nodes import (Assign, BinOp, Block, BoolLit, Break, Continue, If,
                       Let, LogicOp, Num, Print, Program, Str, UnaryOp, Var,
                       While)

# ---------------------------------------------------------------------------
# pretty printer
# ---------------------------------------------------------------------------

def _bool_text(value: bool) -> str:
    return "true" if value else "false"


def pretty(node, indent: int = 0) -> str:
    """Return an indented structural view of the tree (2 spaces per level)."""
    pad = "  " * indent
    nxt = indent + 1

    if isinstance(node, Program):
        lines = [pad + "Program"]
        lines += [pretty(s, nxt) for s in node.stmts]
        return "\n".join(lines)
    if isinstance(node, Block):
        lines = [pad + "Block"]
        lines += [pretty(s, nxt) for s in node.stmts]
        return "\n".join(lines)
    if isinstance(node, Let):
        return "\n".join([pad + f"Let {node.name}", pretty(node.value, nxt)])
    if isinstance(node, Assign):
        return "\n".join([pad + f"Assign {node.name}", pretty(node.value, nxt)])
    if isinstance(node, Print):
        return "\n".join([pad + "Print", pretty(node.value, nxt)])
    if isinstance(node, If):
        lines = [pad + "If", pretty(node.condition, nxt),
                 pretty(node.then_branch, nxt)]
        if node.else_branch is not None:
            lines.append(pad + "  Else")
            lines.append(pretty(node.else_branch, indent + 2))
        return "\n".join(lines)
    if isinstance(node, While):
        return "\n".join([pad + "While", pretty(node.condition, nxt),
                          pretty(node.body, nxt)])
    if isinstance(node, Break):
        return pad + "Break"
    if isinstance(node, Continue):
        return pad + "Continue"
    if isinstance(node, BinOp):
        return "\n".join([pad + f"BinOp({node.op})",
                          pretty(node.left, nxt), pretty(node.right, nxt)])
    if isinstance(node, LogicOp):
        return "\n".join([pad + f"LogicOp({node.op})",
                          pretty(node.left, nxt), pretty(node.right, nxt)])
    if isinstance(node, UnaryOp):
        return "\n".join([pad + f"UnaryOp({node.op})",
                          pretty(node.operand, nxt)])
    if isinstance(node, Num):
        return pad + f"Num({node.value})"
    if isinstance(node, Str):
        return pad + f"Str({node.value!r})"
    if isinstance(node, BoolLit):
        return pad + f"BoolLit({_bool_text(node.value)})"
    if isinstance(node, Var):
        return pad + f"Var({node.name})"
    raise TypeError(f"pretty: unknown node type {type(node).__name__}")


# ---------------------------------------------------------------------------
# unparser
# ---------------------------------------------------------------------------

# precedence of each expression operator, loosest to tightest
_PREC = {"or": 1, "and": 2, "not": 3,
         "<": 4, "<=": 4, ">": 4, ">=": 4, "==": 4, "!=": 4,
         "+": 5, "-": 5, "*": 6, "/": 6}
_UNARY_MINUS_PREC = 7
_ATOM_PREC = 100
_COMPARISON_PREC = 4


def _prec(node) -> int:
    if isinstance(node, (BinOp, LogicOp)):
        return _PREC[node.op]
    if isinstance(node, UnaryOp):
        return _PREC["not"] if node.op == "not" else _UNARY_MINUS_PREC
    return _ATOM_PREC


def _escape(value: str) -> str:
    return (value.replace("\\", "\\\\").replace('"', '\\"')
                 .replace("\n", "\\n").replace("\t", "\\t"))


def _child(child, parent_prec: int, is_right: bool) -> str:
    """Unparse a child, parenthesizing per the Step 3b rule."""
    text = unparse_expr(child)
    child_prec = _prec(child)
    needs = child_prec < parent_prec
    if child_prec == parent_prec:
        if parent_prec == _COMPARISON_PREC:
            needs = True                      # non-assoc: never chain bare
        elif is_right:
            needs = True                      # right child of left-assoc op
    return f"({text})" if needs else text


def unparse_expr(node) -> str:
    if isinstance(node, Num):
        return repr(node.value)
    if isinstance(node, Str):
        return f'"{_escape(node.value)}"'
    if isinstance(node, BoolLit):
        return _bool_text(node.value)
    if isinstance(node, Var):
        return node.name
    if isinstance(node, (BinOp, LogicOp)):
        p = _PREC[node.op]
        return f"{_child(node.left, p, False)} {node.op} {_child(node.right, p, True)}"
    if isinstance(node, UnaryOp):
        p = _prec(node)
        operand = unparse_expr(node.operand)
        if _prec(node.operand) < p:
            operand = f"({operand})"
        return f"not {operand}" if node.op == "not" else f"-{operand}"
    raise TypeError(f"unparse_expr: unknown node type {type(node).__name__}")


def _unparse_stmt(node, indent: int) -> str:
    pad = "    " * indent

    if isinstance(node, Let):
        return f"{pad}let {node.name} = {unparse_expr(node.value)};"
    if isinstance(node, Assign):
        return f"{pad}{node.name} = {unparse_expr(node.value)};"
    if isinstance(node, Print):
        return f"{pad}print {unparse_expr(node.value)};"
    if isinstance(node, Break):
        return f"{pad}break;"
    if isinstance(node, Continue):
        return f"{pad}continue;"
    if isinstance(node, Block):
        inner = "\n".join(_unparse_stmt(s, indent + 1) for s in node.stmts)
        return f"{pad}{{\n{inner}\n{pad}}}" if node.stmts else f"{pad}{{\n{pad}}}"
    if isinstance(node, If):
        head = f"{pad}if {unparse_expr(node.condition)} " \
               + _unparse_stmt(node.then_branch, indent).lstrip()
        if node.else_branch is None:
            return head
        else_text = _unparse_stmt(node.else_branch, indent).lstrip()
        return f"{head} else {else_text}"
    if isinstance(node, While):
        return f"{pad}while {unparse_expr(node.condition)} " \
               + _unparse_stmt(node.body, indent).lstrip()
    raise TypeError(f"unparse: unknown statement type {type(node).__name__}")


def unparse(node) -> str:
    """Regenerate valid source code from any AST node."""
    if isinstance(node, Program):
        return "\n".join(_unparse_stmt(s, 0) for s in node.stmts)
    if isinstance(node, (Let, Assign, Print, Block, If, While, Break, Continue)):
        return _unparse_stmt(node, 0)
    return unparse_expr(node)
