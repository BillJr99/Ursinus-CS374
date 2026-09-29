"""test_parser.py -- test suite for the reference parser + AST tooling.

Run with either:
    python3 -m pytest test_parser.py
    python3 test_parser.py
"""

import unittest

from ast_nodes import (Assign, BinOp, Block, BoolLit, If, Let, LogicOp, Num,
                       Print, Program, Str, UnaryOp, Var, While, Break)
from parser import ParseError, parse, parse_expression
from pretty import pretty, unparse


class TestExpressionLadder(unittest.TestCase):
    def test_precedence_mul_over_add(self):
        # 2 + 3 * 4 => the multiplication nests under the addition
        self.assertEqual(parse_expression("2 + 3 * 4"),
                         BinOp("+", Num(2), BinOp("*", Num(3), Num(4))))

    def test_left_associativity_division(self):
        # 8 / 4 / 2 => (8/4)/2
        self.assertEqual(parse_expression("8 / 4 / 2"),
                         BinOp("/", BinOp("/", Num(8), Num(4)), Num(2)))

    def test_left_associativity_subtraction(self):
        # 8 - 3 - 2 => (8-3)-2 = 3, not 8-(3-2) = 7
        self.assertEqual(parse_expression("8 - 3 - 2"),
                         BinOp("-", BinOp("-", Num(8), Num(3)), Num(2)))

    def test_unary_minus_nests(self):
        self.assertEqual(parse_expression("--x"),
                         UnaryOp("-", UnaryOp("-", Var("x"))))

    def test_parentheses_override_precedence(self):
        self.assertEqual(parse_expression("(2 + 3) * 4"),
                         BinOp("*", BinOp("+", Num(2), Num(3)), Num(4)))

    def test_or_over_and(self):
        # a or b and c => a or (b and c)
        self.assertEqual(parse_expression("a or b and c"),
                         LogicOp("or", Var("a"),
                                 LogicOp("and", Var("b"), Var("c"))))

    def test_not_binds_looser_than_comparison(self):
        # not a < b => not (a < b)
        self.assertEqual(parse_expression("not a < b"),
                         UnaryOp("not", BinOp("<", Var("a"), Var("b"))))

    def test_comparison_does_not_chain(self):
        with self.assertRaises(ParseError) as cm:
            parse_expression("a < b < c")
        err = cm.exception
        self.assertIn("do not chain", err.message)
        self.assertEqual((err.line, err.col), (1, 7))

    def test_literals(self):
        self.assertEqual(parse_expression("3.14"), Num(3.14))
        self.assertEqual(parse_expression("true"), BoolLit(True))
        self.assertEqual(parse_expression(r'"a\nb"'), Str("a\nb"))


class TestStatements(unittest.TestCase):
    def test_worked_while_example(self):
        source = """let x = 10;
while x > 0 {
    print x;
    x = x - 1;
}"""
        tree = parse(source)
        self.assertEqual(tree, Program(stmts=[
            Let(name="x", value=Num(10)),
            While(
                condition=BinOp(">", Var("x"), Num(0)),
                body=Block(stmts=[
                    Print(Var("x")),
                    Assign("x", BinOp("-", Var("x"), Num(1))),
                ])),
        ]))

    def test_else_if_chain(self):
        tree = parse("if a { print 1; } else if b { print 2; } else { print 3; }")
        outer = tree.stmts[0]
        self.assertIsInstance(outer, If)
        self.assertIsInstance(outer.else_branch, If)       # else-if is a nested If
        self.assertIsInstance(outer.else_branch.else_branch, Block)

    def test_dangling_else_attaches_to_nearest_if(self):
        tree = parse("if a { if b { print 1; } else { print 2; } }")
        outer = tree.stmts[0]
        inner = outer.then_branch.stmts[0]
        self.assertIsNone(outer.else_branch)               # outer has NO else
        self.assertIsInstance(inner.else_branch, Block)    # inner got the else

    def test_break_continue(self):
        tree = parse("while true { break; continue; }")
        body = tree.stmts[0].body.stmts
        self.assertEqual(len(body), 2)
        self.assertIsInstance(body[0], Break)

    def test_nested_blocks_and_shadowing_shape(self):
        tree = parse("let x = 2; { let x = 51; print x; } print x;")
        self.assertEqual(len(tree.stmts), 3)
        self.assertIsInstance(tree.stmts[1], Block)
        self.assertEqual(len(tree.stmts[1].stmts), 2)

    def test_positions_recorded(self):
        tree = parse("let x = 1;\nprint x + 2;")
        let_stmt = tree.stmts[0]
        self.assertEqual((let_stmt.line, let_stmt.col), (1, 1))
        plus = tree.stmts[1].value
        self.assertEqual((plus.line, plus.col), (2, 9))


class TestErrorReporting(unittest.TestCase):
    """The five provided broken programs (Step 3d), with positions checked."""

    def _err(self, source):
        with self.assertRaises(ParseError) as cm:
            parse(source)
        return cm.exception

    def test_missing_semicolon(self):
        err = self._err("let x = 5")
        self.assertIn("expected SEMICOLON, found EOF", err.message)
        self.assertEqual((err.line, err.col), (1, 10))

    def test_unclosed_block(self):
        err = self._err("while true { print x;")
        self.assertIn("expected RBRACE, found EOF", err.message)

    def test_bad_operator(self):
        err = self._err("let x = 5 + * 3;")
        self.assertIn("expected an expression, found STAR", err.message)
        self.assertEqual((err.line, err.col), (1, 13))

    def test_mismatched_paren(self):
        err = self._err("print (1 + 2;")
        self.assertIn("expected RPAREN, found SEMICOLON", err.message)

    def test_bare_equals(self):
        err = self._err("= 5;")
        self.assertIn("expected a statement, found EQ", err.message)
        self.assertEqual((err.line, err.col), (1, 1))

    def test_error_position_on_later_line(self):
        err = self._err("let x = 1;\nlet y = ;")
        self.assertEqual(err.line, 2)
        self.assertEqual(err.col, 9)


class TestPrettyAndUnparse(unittest.TestCase):
    def test_pretty_worked_example(self):
        source = "let x = 10;\nwhile x > 0 {\n  print x;\n  x = x - 1;\n}"
        self.assertEqual(pretty(parse(source)), "\n".join([
            "Program",
            "  Let x",
            "    Num(10)",
            "  While",
            "    BinOp(>)",
            "      Var(x)",
            "      Num(0)",
            "    Block",
            "      Print",
            "        Var(x)",
            "      Assign x",
            "        BinOp(-)",
            "          Var(x)",
            "          Num(1)",
        ]))

    def test_unparse_no_needless_parens(self):
        self.assertEqual(unparse(BinOp("+", Num(2), BinOp("*", Num(3), Num(4)))),
                         "2 + 3 * 4")

    def test_unparse_required_parens(self):
        self.assertEqual(unparse(BinOp("*", Num(2), BinOp("+", Num(3), Num(4)))),
                         "2 * (3 + 4)")

    def test_unparse_right_child_same_precedence(self):
        # 8 - (3 - 2) must keep its parentheses (right child, left-assoc)
        tree = BinOp("-", Num(8), BinOp("-", Num(3), Num(2)))
        self.assertEqual(unparse(tree), "8 - (3 - 2)")
        self.assertEqual(parse_expression(unparse(tree)), tree)

    def test_unparse_string_escapes(self):
        self.assertEqual(unparse(Str('quote " tab \t nl \n')),
                         r'"quote \" tab \t nl \n"')

    ROUND_TRIP_PROGRAMS = [
        "let x = 42;",
        "let x = 2 + 3 * 4 - 1;",
        "print (2 + 3) * 4;",
        "print 8 / 4 / 2;",
        "print -x * 3;",
        "print --x;",
        "print not a and b or c;",
        "print not (a and b);",
        "print a < b == true;" .replace("< b ==", "< b;\nprint c =="),  # split: no chains
        'let s = "tab\\there \\"quoted\\" back\\\\slash";\nprint s + "!";',
        "let x = 2;\n{\n    let x = 51;\n    print x;\n}\nprint x;",
        "if a { print 1; } else if b { print 2; } else { print 3; }",
        "while x > 0 {\n    x = x - 1;\n    if x == 2 { break; } else { continue; }\n}",
        "if x >= 10 { print x * (x + 1); }",
        "print 3.14 * r * r;",
        "print true or 1 / 0;",
    ]

    def test_round_trip_all_programs(self):
        # the round-trip law: parse(unparse(parse(s))) == parse(s)
        for source in self.ROUND_TRIP_PROGRAMS:
            tree1 = parse(source)
            source2 = unparse(tree1)
            tree2 = parse(source2)
            self.assertEqual(tree2, tree1,
                             f"round-trip failed on: {source!r} -> {source2!r}")
            self.assertEqual(pretty(tree2), pretty(tree1))

    def test_random_expression_round_trip(self):
        # A stdlib-only stand-in for the Hypothesis property test: generate
        # 300 random expression trees, assert parse(unparse(t)) == t.
        import random
        rng = random.Random(374)

        def gen(depth):
            if depth == 0 or rng.random() < 0.3:
                return rng.choice([Num(rng.randint(0, 99)),
                                   Num(round(rng.uniform(0, 9), 2)),
                                   Var(rng.choice("xyz")),
                                   BoolLit(rng.random() < 0.5)])
            kind = rng.random()
            if kind < 0.55:
                op = rng.choice(["+", "-", "*", "/"])
                return BinOp(op, gen(depth - 1), gen(depth - 1))
            if kind < 0.70:
                op = rng.choice(["<", "<=", ">", ">=", "==", "!="])
                # comparisons cannot nest comparisons without parens; the
                # unparser must insert them -- so allow any children here
                return BinOp(op, gen(depth - 1), gen(depth - 1))
            if kind < 0.90:
                return LogicOp(rng.choice(["and", "or"]),
                               gen(depth - 1), gen(depth - 1))
            return UnaryOp(rng.choice(["-", "not"]), gen(depth - 1))

        for _ in range(300):
            tree = gen(4)
            text = unparse(tree)
            self.assertEqual(parse_expression(text), tree,
                             f"round-trip failed: {text!r}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
