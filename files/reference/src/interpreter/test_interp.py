"""test_interp.py -- test suite for the reference interpreter.

Run with either:
    python3 -m pytest test_interp.py
    python3 test_interp.py
"""

import unittest

from ast_nodes import LogicOp, Num, Var
from parser import ParseError, parse, parse_expression
from lexer import LexError
from interp import (BreakSignal, Environment, Interpreter, LangError,
                    LangNameError, LangRuntimeError, LangTypeError,
                    LangZeroDivisionError, format_value, truthy)
from repl import report


def run(source, env=None):
    """Run a program, returning the list of printed lines."""
    lines = []
    interp = Interpreter(env=env, output=lines.append)
    interp.run(parse(source))
    return lines


def ev(source, env=None):
    """Evaluate a bare expression and return its value."""
    interp = Interpreter(env=env)
    return interp.eval_node(parse_expression(source), interp.globals)


class TestExpressions(unittest.TestCase):
    def test_arithmetic_precedence(self):
        self.assertEqual(ev("2 + 3 * 4"), 14)
        self.assertEqual(ev("(2 + 3) * 4"), 20)
        self.assertEqual(ev("8 - 3 - 2"), 3)     # left-assoc: (8-3)-2

    def test_division_is_true_division(self):
        self.assertEqual(ev("10 / 4"), 2.5)
        self.assertEqual(ev("10 / 2"), 5.0)      # documented: / yields float

    def test_unary_and_comparison(self):
        self.assertEqual(ev("--5"), 5)
        self.assertIs(ev("3 <= 3"), True)
        self.assertIs(ev("not 0"), True)
        self.assertIs(ev("not \"x\""), False)

    def test_string_concatenation(self):
        self.assertEqual(ev('"foo" + "bar"'), "foobar")

    def test_equality_cross_type_is_false(self):
        self.assertIs(ev('1 == "1"'), False)     # documented decision
        self.assertIs(ev('1 != "1"'), True)
        self.assertIs(ev("true == 1"), False)    # bool is not a number
        self.assertIs(ev("1 == 1.0"), True)      # int/float are both numbers


class TestTypeErrors(unittest.TestCase):
    def test_plus_names_both_types(self):
        with self.assertRaises(LangTypeError) as cm:
            run('let x = "hello";\nlet y = x + 1;')
        err = cm.exception
        self.assertIn("got str and int", err.message)
        self.assertEqual(err.line, 2)

    def test_unary_minus_type_error(self):
        with self.assertRaises(LangTypeError) as cm:
            run('let x = -"oops";')
        self.assertIn("unary minus requires a number, got str", cm.exception.message)

    def test_comparison_type_error(self):
        with self.assertRaises(LangTypeError) as cm:
            run('print "a" < 1;')
        self.assertIn("'<' requires numbers, got str and int", cm.exception.message)

    def test_division_by_zero(self):
        with self.assertRaises(LangZeroDivisionError) as cm:
            run("let x = 1;\nlet y = x / 0;")
        err = cm.exception
        self.assertEqual(err.message, "division by zero")
        self.assertEqual(err.line, 2)


class TestScoping(unittest.TestCase):
    def test_shadowing_prints_51_then_2(self):
        source = """let x = 2;
{
    let x = 51;
    print x;
}
print x;
"""
        self.assertEqual(run(source), ["51", "2"])

    def test_scope_restoration_inner_let_does_not_leak(self):
        env = Environment()
        run("{ let inner = 1; }", env=env)
        self.assertNotIn("inner", env)
        with self.assertRaises(LangNameError):
            env.lookup("inner")

    def test_assignment_updates_enclosing_scope(self):
        source = "let x = 1; { x = 42; } print x;"
        self.assertEqual(run(source), ["42"])

    def test_assign_undefined_raises(self):
        with self.assertRaises(LangNameError) as cm:
            run("y = 5;")
        self.assertIn("Cannot assign to undefined variable 'y'",
                      cm.exception.message)

    def test_undefined_variable_lookup(self):
        with self.assertRaises(LangNameError) as cm:
            run("print nope;")
        self.assertIn("Undefined variable 'nope'", cm.exception.message)
        self.assertEqual(cm.exception.line, 1)


class TestShortCircuit(unittest.TestCase):
    def test_bomb_test(self):
        # the assignment's bomb test: the right side must NOT be evaluated
        self.assertEqual(run("let safe = true or (1 / 0); print safe;"),
                         ["true"])

    def test_and_short_circuits(self):
        self.assertEqual(run("let safe = false and (1 / 0); print safe;"),
                         ["false"])

    def test_non_evaluation_is_observable(self):
        # instrument the right operand with a side effect and prove it
        # never fires when the left side decides
        fired = []

        class Bomb:
            pass

        class SpyInterp(Interpreter):
            def eval_node(self, node, env):
                if isinstance(node, Bomb):
                    fired.append(True)
                    return 1
                return super().eval_node(node, env)

        interp = SpyInterp()
        interp.eval_node(LogicOp("or", Num(1), Bomb()), interp.globals)
        interp.eval_node(LogicOp("and", Num(0), Bomb()), interp.globals)
        self.assertEqual(fired, [])
        # and the right side IS evaluated when the left does not decide
        interp.eval_node(LogicOp("and", Num(1), Bomb()), interp.globals)
        self.assertEqual(fired, [True])

    def test_logic_ops_return_operand_values(self):
        self.assertEqual(ev("0 or 7"), 7)
        self.assertEqual(ev('"" or "fallback"'), "fallback")
        self.assertEqual(ev("0 and 7"), 0)


class TestControlFlow(unittest.TestCase):
    def test_while_countdown(self):
        source = "let x = 3; while x > 0 { print x; x = x - 1; }"
        self.assertEqual(run(source), ["3", "2", "1"])

    def test_numeric_truthiness_in_while(self):
        source = "let x = 2; while x { print x; x = x - 1; }"
        self.assertEqual(run(source), ["2", "1"])

    def test_while_break(self):
        source = ("let x = 0; while true { x = x + 1;"
                  " if x == 3 { break; } } print x;")
        self.assertEqual(run(source), ["3"])

    def test_while_continue(self):
        source = ("let x = 0; let evens = 0; while x < 6 { x = x + 1;"
                  " if x == 1 or x == 3 or x == 5 { continue; }"
                  " evens = evens + 1; }"
                  " print evens;")
        self.assertEqual(run(source), ["3"])

    def test_break_outside_loop_is_staged_error(self):
        with self.assertRaises(LangRuntimeError) as cm:
            run("break;")
        self.assertIn("'break' outside loop", cm.exception.message)

    def test_if_else_chain(self):
        source = ("let x = 2;"
                  " if x == 1 { print \"one\"; }"
                  " else if x == 2 { print \"two\"; }"
                  " else { print \"many\"; }")
        self.assertEqual(run(source), ["two"])

    def test_determinism_fresh_environments(self):
        source = "let x = 5; while x > 0 { x = x - 1; print x * x; }"
        self.assertEqual(run(source), run(source))


class TestPrinting(unittest.TestCase):
    def test_print_formats(self):
        self.assertEqual(run('print true; print false; print 3; '
                             'print 2.5; print "hi";'),
                         ["true", "false", "3", "2.5", "hi"])

    def test_string_escapes_survive_pipeline(self):
        self.assertEqual(run(r'print "a\tb\nc";'), ["a\tb\nc"])


class TestStagedErrors(unittest.TestCase):
    """The file-runner's staged error message format (Part 3)."""

    def test_lexical_stage(self):
        try:
            parse("let x = @;")
        except LexError as exc:
            self.assertEqual(report(exc),
                             "Lexical error at line 1, col 9: unexpected character '@'")
        else:
            self.fail("expected LexError")

    def test_syntax_stage(self):
        try:
            parse("let x = 5")
        except ParseError as exc:
            self.assertEqual(report(exc),
                             "Syntax error at line 1, col 10: expected SEMICOLON, found EOF")
        else:
            self.fail("expected ParseError")

    def test_runtime_stage(self):
        try:
            run("print 1 / 0;")
        except LangError as exc:
            self.assertEqual(report(exc),
                             "Runtime error at line 1: division by zero")
        else:
            self.fail("expected LangError")


class TestReplBehavior(unittest.TestCase):
    def test_persistent_environment_across_inputs(self):
        env = Environment()
        run("let x = 10;", env=env)
        run("x = x + 5;", env=env)
        self.assertEqual(run("print x;", env=env), ["15"])

    def test_recovery_after_error_keeps_state(self):
        env = Environment()
        run("let x = 10;", env=env)
        with self.assertRaises(LangZeroDivisionError):
            run("let y = x / 0;", env=env)
        self.assertEqual(run("print x;", env=env), ["10"])

    def test_expression_value_formatting(self):
        self.assertEqual(format_value(ev("2 + 3 * 4")), "14")
        self.assertEqual(format_value(ev("1 < 2")), "true")


class TestRandomizedInvariants(unittest.TestCase):
    """Stdlib stand-ins for the assignment's Hypothesis invariants."""

    def _gen_int_expr(self, rng, depth):
        if depth == 0 or rng.random() < 0.3:
            return str(rng.randint(0, 20))
        op = rng.choice(["+", "-", "*"])
        return (f"({self._gen_int_expr(rng, depth - 1)} {op} "
                f"{self._gen_int_expr(rng, depth - 1)})")

    def test_arithmetic_agreement_with_python(self):
        # metamorphic oracle: for +,-,* integer expressions our evaluator
        # must agree with Python's own eval
        import random
        rng = random.Random(374)
        for _ in range(200):
            src = self._gen_int_expr(rng, 4)
            self.assertEqual(ev(src), eval(src), f"disagreement on {src}")

    def test_scope_restoration_property(self):
        import random
        rng = random.Random(99)
        env = Environment()
        env.define("x", 3)
        for _ in range(50):
            expr = self._gen_int_expr(rng, 3)
            run(f"{{ let v = 1; print v + {expr}; }}", env=env)
            self.assertNotIn("v", env)   # the inner let never leaks
        self.assertEqual(env.lookup("x"), 3)


if __name__ == "__main__":
    unittest.main(verbosity=2)
