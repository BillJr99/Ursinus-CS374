"""CS374 Interpreter assignment: the parser.  This file is complete.

parse(source) returns a Program.  It is a recursive descent parser with one
function per precedence level, so the tree already holds precedence and
associativity by the time your evaluator sees it.
"""

from lexer import tokenize
from ast_nodes import (Num, BoolLit, Var, BinOp, UnaryOp, LogicOp, Let, Assign,
                       Print, Block, If, While, Break, Continue, Program)


class ParseError(Exception):
    """Raised on a syntax error."""
    def __init__(self, message, line):
        super().__init__(message)
        self.message = message
        self.line = line


class Parser:
    def __init__(self, source):
        self.tokens = tokenize(source)
        self.pos = 0

    def peek(self):
        return self.tokens[self.pos]

    def advance(self):
        tok = self.tokens[self.pos]
        self.pos += 1
        return tok

    def expect(self, token_type):
        tok = self.peek()
        if tok.type != token_type:
            raise ParseError(f"expected {token_type}, found {tok.type}", tok.line)
        return self.advance()

    def program(self):
        stmts = []
        while self.peek().type != "EOF":
            stmts.append(self.stmt())
        return Program(stmts)

    def stmt(self):
        tok = self.peek()
        if tok.type == "let":
            self.advance()
            name = self.expect("ID")
            self.expect("=")
            value = self.expr()
            self.expect(";")
            return Let(name.value, value, tok.line)
        if tok.type == "ID":
            self.advance()
            self.expect("=")
            value = self.expr()
            self.expect(";")
            return Assign(tok.value, value, tok.line)
        if tok.type == "print":
            self.advance()
            value = self.expr()
            self.expect(";")
            return Print(value, tok.line)
        if tok.type == "if":
            return self.if_stmt()
        if tok.type == "while":
            self.advance()
            condition = self.expr()
            return While(condition, self.block(), tok.line)
        if tok.type == "break":
            self.advance()
            self.expect(";")
            return Break(tok.line)
        if tok.type == "continue":
            self.advance()
            self.expect(";")
            return Continue(tok.line)
        if tok.type == "{":
            return self.block()
        raise ParseError(f"expected a statement, found {tok.type}", tok.line)

    def if_stmt(self):
        tok = self.expect("if")
        condition = self.expr()
        then_branch = self.block()
        else_branch = None
        if self.peek().type == "else":
            self.advance()
            else_branch = self.if_stmt() if self.peek().type == "if" else self.block()
        return If(condition, then_branch, else_branch, tok.line)

    def block(self):
        tok = self.expect("{")
        stmts = []
        while self.peek().type not in ("}", "EOF"):
            stmts.append(self.stmt())
        self.expect("}")
        return Block(stmts, tok.line)

    def expr(self):
        return self.or_expr()

    def or_expr(self):
        left = self.and_expr()
        while self.peek().type == "or":
            op = self.advance()
            left = LogicOp("or", left, self.and_expr(), op.line)
        return left

    def and_expr(self):
        left = self.not_expr()
        while self.peek().type == "and":
            op = self.advance()
            left = LogicOp("and", left, self.not_expr(), op.line)
        return left

    def not_expr(self):
        if self.peek().type == "not":
            op = self.advance()
            return UnaryOp("not", self.not_expr(), op.line)
        return self.comparison()

    def comparison(self):
        left = self.addsub()
        if self.peek().type in ("<", "<=", ">", ">=", "==", "!="):
            op = self.advance()
            left = BinOp(op.value, left, self.addsub(), op.line)
        return left

    def addsub(self):
        left = self.muldiv()
        while self.peek().type in ("+", "-"):
            op = self.advance()
            left = BinOp(op.value, left, self.muldiv(), op.line)
        return left

    def muldiv(self):
        left = self.unary()
        while self.peek().type in ("*", "/"):
            op = self.advance()
            left = BinOp(op.value, left, self.unary(), op.line)
        return left

    def unary(self):
        if self.peek().type == "-":
            op = self.advance()
            return UnaryOp("-", self.unary(), op.line)
        return self.primary()

    def primary(self):
        tok = self.peek()
        if tok.type == "NUM":
            self.advance()
            return Num(float(tok.value) if "." in tok.value else int(tok.value), tok.line)
        if tok.type in ("true", "false"):
            self.advance()
            return BoolLit(tok.type == "true", tok.line)
        if tok.type == "ID":
            self.advance()
            return Var(tok.value, tok.line)
        if tok.type == "(":
            self.advance()
            inner = self.expr()
            self.expect(")")
            return inner
        raise ParseError(f"expected an expression, found {tok.type}", tok.line)


def parse(source):
    return Parser(source).program()
