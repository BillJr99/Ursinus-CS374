"""CS374 Interpreter assignment: starter test file.

The three tests below are the ones the assignment spells out, seeded so that
you have a working harness from the first minute.  They FAIL until you fill
in the matching evaluator branches, and that is the point: each one turns
green as you finish the step it belongs to.

Run with:   python3 -m pytest test_interpreter.py
       or:  python3 test_interpreter.py
"""

import io
import traceback
from contextlib import redirect_stdout

from parser import parse
from interpreter import Interpreter


def run(source):
    """Evaluate a program in a fresh interpreter, returning (value, printed output)."""
    buf = io.StringIO()
    with redirect_stdout(buf):
        value = Interpreter().eval_node(parse(source))
    return value, buf.getvalue()


# --- Step 2b: the bomb test ------------------------------------------------
# If the right operand of `or` is ever evaluated, this raises instead of
# passing.  That is the whole test.

def test_bomb():
    Interpreter().eval_node(parse('let safe = true or (1 / 0);'))


# --- Step 2c: scopes -------------------------------------------------------
# The shadowing program from the assignment and from the Environments lab.
# The inner `let` shadows; the bare assignment reaches outward.

def test_shadowing_prints_51_then_2():
    _, out = run("""
        let x = 2;
        {
            let x = 51;
            print x;
        }
        print x;
    """)
    assert out.split() == ["51", "2"], f"got {out.split()!r}"


# --- Step 2e: the first required invariant ---------------------------------
# Property-based, over generated programs rather than fixed ones.  Bring the
# recursive AST generator you wrote for the Parser assignment.

try:
    from hypothesis import given
    # TODO: import or paste your recursive AST generator, e.g. exprs()
    #
    # @given(tree=exprs())
    # def test_determinism(tree):
    #     assert run_tree(tree) == run_tree(tree)
    #
    # TODO: test_scope_restoration, and one of
    #       test_short_circuit_non_evaluation / test_arithmetic_agreement
except ImportError:                      # hypothesis not installed yet
    pass


if __name__ == "__main__":
    tests = [f for name, f in dict(globals()).items()
             if name.startswith("test_") and callable(f)]
    failed = 0
    for t in tests:
        try:
            t()
            print("PASS", t.__name__)
        except Exception as err:
            failed += 1
            print(f"FAIL {t.__name__} -- [{type(err).__name__}] {err}")
            traceback.print_exc()
    print(f"{len(tests) - failed} passed, {failed} failed")
