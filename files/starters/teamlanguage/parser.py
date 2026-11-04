"""Parser: turns tokens into a tree, one function per grammar rule.

    program -> stmt*
    stmt    -> "let" IDENT "=" expr ";" | "print" expr ";"
    expr    -> term (("+" | "-") term)*
    term    -> factor (("*" | "/") factor)*
    factor  -> NUM | IDENT | "(" expr ")"
"""
from ast_nodes import BinOp, Let, Num, Print, Var
from lexer import LangError, tokenize


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def peek(self):
        return self.tokens[self.pos]

    def advance(self):
        token = self.tokens[self.pos]
        if token.type != "EOF":
            self.pos += 1
        return token

    def expect(self, kind):
        token = self.peek()
        if token.type != kind:
            raise LangError("Parse", f"expected {kind}, found {token.type}", token.line, token.col)
        return self.advance()

    def program(self):
        stmts = []
        while self.peek().type != "EOF":
            stmts.append(self.stmt())
        return stmts

    def stmt(self):
        token = self.peek()
        if token.type == "LET":
            self.advance()
            name = self.expect("IDENT").value
            self.expect("EQ")
            value = self.expr()
            self.expect("SEMICOLON")
            return Let(name, value, token.line, token.col)
        if token.type == "PRINT":
            self.advance()
            value = self.expr()
            self.expect("SEMICOLON")
            return Print(value, token.line, token.col)
        raise LangError("Parse", f"expected a statement, found {token.type}", token.line, token.col)

    def expr(self):
        return self.left_fold(self.term, {"PLUS", "MINUS"})

    def term(self):
        return self.left_fold(self.factor, {"STAR", "SLASH"})

    def left_fold(self, next_tier, operators):
        """One tier of the precedence ladder.  The loop makes these operators left-associative."""
        left = next_tier()
        while self.peek().type in operators:
            op = self.advance()
            left = BinOp(op.value, left, next_tier(), op.line, op.col)
        return left

    def factor(self):
        token = self.peek()
        if token.type == "NUM":
            self.advance()
            return Num(float(token.value), token.line, token.col)
        if token.type == "IDENT":
            self.advance()
            return Var(token.value, token.line, token.col)
        if token.type == "LPAREN":
            self.advance()
            inner = self.expr()
            self.expect("RPAREN")
            return inner
        raise LangError("Parse", f"expected an expression, found {token.type}", token.line, token.col)


def parse(source):
    """Return the list of statement nodes for source."""
    return Parser(tokenize(source)).program()
