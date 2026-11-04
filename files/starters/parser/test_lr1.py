"""CS374 Parser assignment: the test file.  Run with: python3 test_lr1.py

The first tests check your tables.  The rest check the trees your driver builds.
Tests compare nodes, never printed text, so a test keeps passing when a repr changes.
"""

from ast_nodes import Num, Var, BinOp, Let, Print, Program
from lr1 import (build_states, build_tables, closure, goto, parse, ParseError)


def test_closure_has_thirteen_items():
    assert len(closure({(0, 0, "$")})) == 13


def test_thirty_eight_states_and_no_conflicts():
    states, transitions = build_states()
    action, goto_table, conflicts = build_tables(states, transitions)
    assert len(states) == 38, f"got {len(states)} states"
    assert conflicts == [], f"got conflicts: {conflicts}"


def test_multiplication_binds_tighter():
    assert parse("print 1 + 2 * 3;") == Program(
        [Print(BinOp("+", Num(1), BinOp("*", Num(2), Num(3))))])


def test_subtraction_left_associates():
    assert parse("print 8 - 3 - 2;") == Program(
        [Print(BinOp("-", BinOp("-", Num(8), Num(3)), Num(2)))])


def test_bad_token_raises_positioned_error():
    try:
        parse("print 1 ) ;")
    except ParseError as err:
        assert (err.line, err.col, err.found) == (1, 9, ")"), f"got {err.line}, {err.col}, {err.found}"
    else:
        assert False, "a stray ) should not parse"


# TODO (Step 3.3): at least four tests of your own: parentheses, a let, a two-statement
#                  program, and one more program that must raise a ParseError.


if __name__ == "__main__":
    tests = [f for name, f in dict(globals()).items() if name.startswith("test_")]
    failed = 0
    for t in tests:
        try:
            t()
            print("PASS", t.__name__)
        except Exception as err:         # keep going, so one break does not hide the rest
            failed += 1
            print("FAIL", t.__name__, "--", repr(err))
    print(f"{len(tests) - failed} passed, {failed} failed")
