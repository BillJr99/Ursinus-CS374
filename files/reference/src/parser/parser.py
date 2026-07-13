"""parser.py -- reference recursive descent parser for the CS374 language.

Implements the grammar ladder from the Parser assignment, importing the
reference Lexer unchanged:

    program     ::= stmt* EOF
    stmt        ::= let_stmt | assign_stmt | print_stmt | if_stmt
                  | while_stmt | break_stmt | continue_stmt | block
    let_stmt    ::= LET IDENT EQ expr SEMICOLON
    assign_stmt ::= IDENT EQ expr SEMICOLON
    print_stmt  ::= PRINT expr SEMICOLON
    if_stmt     ::= IF expr block ( ELSE ( if_stmt | block ) )?
    while_stmt  ::= WHILE expr block
    break_stmt  ::= BREAK SEMICOLON          (added for the Interpreter asmt)
    continue_stmt ::= CONTINUE SEMICOLON     (added for the Interpreter asmt)
    block       ::= LBRACE stmt* RBRACE

    expr        ::= or_expr
    or_expr     ::= and_expr ( OR and_expr )*        left-assoc, LogicOp
    and_expr    ::= not_expr ( AND not_expr )*       left-assoc, LogicOp
    not_expr    ::= NOT not_expr | comparison        prefix, UnaryOp("not")
    comparison  ::= addsub ( ( LT|LE|GT|GE|EQEQ|NEQ ) addsub )?   NON-assoc
    addsub      ::= muldiv ( ( PLUS | MINUS ) muldiv )*           left-assoc
    muldiv      ::= unary ( ( STAR | SLASH ) unary )*             left-assoc
    unary       ::= MINUS unary | primary
    primary     ::= INT | FLOAT | STRING | TRUE | FALSE | IDENT
                  | LPAREN expr RPAREN

Dangling else: the ELSE clause is consumed by the innermost if_stmt still
being parsed, so an else always attaches to the NEAREST if (the standard
resolution -- the recursive call structure enforces it).

Comparison chaining (``a < b < c``) is a syntax error; the parser detects
it explicitly and reports it, rather than leaving a confusing
"expected SEMICOLON" behind.

Every ParseError carries the expected/found token types and the 1-indexed
line and column of the offending token:

    ParseError at line 3, col 12: expected SEMICOLON, found RBRACE
"""

from typing import Optional

from lexer import Lexer, LexError  # imported unchanged from the Lexer assignment
from ast_nodes import (Assign, BinOp, Block, BoolLit, Break, Continue, If,
                       Let, LogicOp, Num, Print, Program, Str, UnaryOp, Var,
                       While)


class ParseError(Exception):
    """A syntax error with expected/found information and a position."""

    def __init__(self, message: str, line: int = 0, col: int = 0):
        self.message = message
        self.line = line
        self.col = col
        super().__init__(str(self))

    def __str__(self) -> str:
        return f"ParseError at line {self.line}, col {self.col}: {self.message}"


_COMPARISON_OPS = {"LT": "<", "LE": "<=", "GT": ">", "GE": ">=",
                   "EQEQ": "==", "NEQ": "!="}


class Parser:
    def __init__(self, lexer: Lexer):
        self.lexer = lexer

    # -- helpers ------------------------------------------------------------
    def peek(self):
        return self.lexer.peek()

    def advance(self):
        return self.lexer.advance()

    def expect(self, token_type: str):
        """Like Lexer.expect, but raises ParseError (the parser's error class)."""
        tok = self.peek()
        if tok.type != token_type:
            raise ParseError(f"expected {token_type}, found {tok.type}",
                             tok.line, tok.col)
        return self.advance()

    # -- expression ladder (tightest binding at the bottom) ------------------
    def parse_primary(self):
        tok = self.peek()
        if tok.type == "INT":
            self.advance()
            return Num(int(tok.value), tok.line, tok.col)
        if tok.type == "FLOAT":
            self.advance()
            return Num(float(tok.value), tok.line, tok.col)
        if tok.type == "STRING":
            self.advance()
            return Str(tok.decoded, tok.line, tok.col)
        if tok.type == "TRUE":
            self.advance()
            return BoolLit(True, tok.line, tok.col)
        if tok.type == "FALSE":
            self.advance()
            return BoolLit(False, tok.line, tok.col)
        if tok.type == "IDENT":
            self.advance()
            return Var(tok.value, tok.line, tok.col)
        if tok.type == "LPAREN":
            self.advance()
            expr = self.parse_expr()
            self.expect("RPAREN")
            return expr
        raise ParseError(f"expected an expression, found {tok.type}",
                         tok.line, tok.col)

    def parse_unary(self):
        tok = self.peek()
        if tok.type == "MINUS":
            self.advance()
            return UnaryOp("-", self.parse_unary(), tok.line, tok.col)
        return self.parse_primary()

    def parse_muldiv(self):
        left = self.parse_unary()
        while self.peek().type in ("STAR", "SLASH"):
            op_tok = self.advance()
            right = self.parse_unary()
            left = BinOp("*" if op_tok.type == "STAR" else "/",
                         left, right, op_tok.line, op_tok.col)
        return left

    def parse_addsub(self):
        left = self.parse_muldiv()
        while self.peek().type in ("PLUS", "MINUS"):
            op_tok = self.advance()
            right = self.parse_muldiv()
            left = BinOp("+" if op_tok.type == "PLUS" else "-",
                         left, right, op_tok.line, op_tok.col)
        return left

    def parse_comparison(self):
        left = self.parse_addsub()
        if self.peek().type in _COMPARISON_OPS:
            op_tok = self.advance()
            right = self.parse_addsub()
            left = BinOp(_COMPARISON_OPS[op_tok.type], left, right,
                         op_tok.line, op_tok.col)
            # comparisons are non-associative: a < b < c is a syntax error
            nxt = self.peek()
            if nxt.type in _COMPARISON_OPS:
                raise ParseError(
                    "comparison operators do not chain; use parentheses",
                    nxt.line, nxt.col)
        return left

    def parse_not(self):
        tok = self.peek()
        if tok.type == "NOT":
            self.advance()
            return UnaryOp("not", self.parse_not(), tok.line, tok.col)
        return self.parse_comparison()

    def parse_and(self):
        left = self.parse_not()
        while self.peek().type == "AND":
            op_tok = self.advance()
            left = LogicOp("and", left, self.parse_not(),
                           op_tok.line, op_tok.col)
        return left

    def parse_or(self):
        left = self.parse_and()
        while self.peek().type == "OR":
            op_tok = self.advance()
            left = LogicOp("or", left, self.parse_and(),
                           op_tok.line, op_tok.col)
        return left

    def parse_expr(self):
        return self.parse_or()

    # -- statements ----------------------------------------------------------
    def parse_let_stmt(self):
        let_tok = self.expect("LET")
        name = self.expect("IDENT")
        self.expect("EQ")
        value = self.parse_expr()
        self.expect("SEMICOLON")
        return Let(name.value, value, let_tok.line, let_tok.col)

    def parse_assign_stmt(self):
        # Lookahead strategy: a statement beginning with IDENT can only be
        # an assignment in this grammar (there are no expression
        # statements), so one token of lookahead suffices -- consume IDENT,
        # then EQ must follow.
        name = self.expect("IDENT")
        self.expect("EQ")
        value = self.parse_expr()
        self.expect("SEMICOLON")
        return Assign(name.value, value, name.line, name.col)

    def parse_print_stmt(self):
        print_tok = self.expect("PRINT")
        value = self.parse_expr()
        self.expect("SEMICOLON")
        return Print(value, print_tok.line)

    def parse_block(self):
        lb = self.expect("LBRACE")
        stmts = []
        while self.peek().type not in ("RBRACE", "EOF"):
            stmts.append(self.parse_stmt())
        self.expect("RBRACE")
        return Block(stmts, lb.line)

    def parse_if_stmt(self):
        if_tok = self.expect("IF")
        condition = self.parse_expr()
        then_branch = self.parse_block()
        else_branch = None
        if self.peek().type == "ELSE":
            self.advance()
            if self.peek().type == "IF":
                else_branch = self.parse_if_stmt()   # else-if chain
            else:
                else_branch = self.parse_block()
        return If(condition, then_branch, else_branch, if_tok.line)

    def parse_while_stmt(self):
        while_tok = self.expect("WHILE")
        condition = self.parse_expr()
        body = self.parse_block()
        return While(condition, body, while_tok.line)

    def parse_break_stmt(self):
        tok = self.expect("BREAK")
        self.expect("SEMICOLON")
        return Break(tok.line)

    def parse_continue_stmt(self):
        tok = self.expect("CONTINUE")
        self.expect("SEMICOLON")
        return Continue(tok.line)

    def parse_stmt(self):
        tok = self.peek()
        if tok.type == "LET":
            return self.parse_let_stmt()
        if tok.type == "IDENT":
            return self.parse_assign_stmt()
        if tok.type == "PRINT":
            return self.parse_print_stmt()
        if tok.type == "IF":
            return self.parse_if_stmt()
        if tok.type == "WHILE":
            return self.parse_while_stmt()
        if tok.type == "BREAK":
            return self.parse_break_stmt()
        if tok.type == "CONTINUE":
            return self.parse_continue_stmt()
        if tok.type == "LBRACE":
            return self.parse_block()
        raise ParseError(f"expected a statement, found {tok.type}",
                         tok.line, tok.col)

    def parse_program(self):
        stmts = []
        while self.peek().type != "EOF":
            stmts.append(self.parse_stmt())
        return Program(stmts)


# -- module-level convenience entry points -----------------------------------

def parse(source: str, config_path: Optional[str] = None) -> Program:
    """Parse a full program from source text."""
    return Parser(Lexer(source, config_path=config_path)).parse_program()


def parse_expression(source: str):
    """Parse a single bare expression (used by the REPL). The entire input
    must be consumed -- trailing tokens are a ParseError."""
    parser = Parser(Lexer(source))
    expr = parser.parse_expr()
    tok = parser.peek()
    if tok.type != "EOF":
        raise ParseError(f"expected EOF after expression, found {tok.type}",
                         tok.line, tok.col)
    return expr
