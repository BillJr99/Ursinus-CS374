"""test_environment.py: behavior tests for the CS374 Environments lab.

Put this file next to your environment.py and run, from that folder:

    python3 test_environment.py            # the five behavior tests (Step 1.3)
    python3 test_environment.py --trace    # the tests, then the Part 2 trace program

The five tests are numbered to match the list in Step 1.3 of the lab page:

    1. Lookup through three levels of nesting.
    2. define in an inner scope shadows the outer binding.
    3. assign from an inner scope updates the outer binding.
    4. assign to an undefined name raises (run as the Step 1.2 usage example,
       which must print 51 then 2 first).
    5. Scope restoration: after a child scope is discarded, the outer binding
       is unchanged.

A passing run ends with "Ran 5 tests" and "OK".  A FAILED line names the
test by number, and the "If it fails" box in Step 1.3 says which method to
reread.

The --trace flag runs the three-nested-block program from Part 2 through your
class and prints the environment chain and result at every numbered step, so
you can check your paper trace.  Fill in your trace table before you run it.
"""

import contextlib
import io
import sys
import unittest

try:
    from environment import Environment, LangError, LangNameError
except ImportError as exc:
    sys.exit(
        f"Could not import from environment.py ({exc}).\n"
        "Run this script from the folder that holds environment.py, and check\n"
        "that the file defines Environment, LangError, and LangNameError."
    )


class TestEnvironment(unittest.TestCase):

    def test_1_lookup_chains_to_parent(self):
        """Behavior 1: lookup walks outward through three levels of nesting."""
        top = Environment()
        top.define("a", 1)
        mid = Environment(parent=top)
        mid.define("b", 2)
        bot = Environment(parent=mid)
        bot.define("c", 3)
        self.assertEqual(bot.lookup("c"), 3, "a name bound in the current scope")
        self.assertEqual(bot.lookup("b"), 2, "a name bound one level out")
        self.assertEqual(bot.lookup("a"), 1, "a name bound two levels out")
        self.assertEqual(mid.lookup("a"), 1, "a lookup that starts in the middle scope")
        # A name no scope in the chain defines raises the language-level error.
        with self.assertRaises(LangNameError) as caught:
            bot.lookup("nope")
        self.assertIsInstance(caught.exception, LangError)
        self.assertIn("nope", str(caught.exception),
                      "the LangNameError message must contain the variable name")

    def test_2_define_in_child_shadows(self):
        """Behavior 2: define in an inner scope shadows the outer binding without changing it."""
        outer = Environment()
        outer.define("x", 2)
        inner = Environment(parent=outer)
        inner.define("x", 51)
        self.assertEqual(inner.lookup("x"), 51, "the inner define shadows the outer x")
        self.assertEqual(outer.lookup("x"), 2, "the outer x is untouched by the inner define")
        # A define in the child never leaks a new name into the parent.
        inner.define("only_here", True)
        with self.assertRaises(LangNameError):
            outer.lookup("only_here")

    def test_3_assign_updates_nearest_enclosing(self):
        """Behavior 3: assign updates the nearest enclosing binding and never creates one."""
        outer = Environment()
        outer.define("y", 10)
        inner = Environment(parent=outer)
        inner.assign("y", 11)                       # y = 11;  inside the block, no let
        self.assertEqual(outer.lookup("y"), 11, "assign from the inner scope updated the outer y")
        self.assertEqual(inner.lookup("y"), 11)
        # If assign had created its own y in inner, this outer update would be hidden from inner.
        outer.assign("y", 12)
        self.assertEqual(inner.lookup("y"), 12,
                         "assign created a shadowing y in the inner scope instead of deferring to the parent")
        # Nearest enclosing binding wins: the middle scope's y changes, the top scope's does not.
        top = Environment()
        top.define("y", 1)
        mid = Environment(parent=top)
        mid.define("y", 2)
        bot = Environment(parent=mid)
        bot.assign("y", 3)
        self.assertEqual(mid.lookup("y"), 3, "the nearest enclosing y (in the middle scope) was updated")
        self.assertEqual(top.lookup("y"), 1, "the top-level y two levels out was left alone")

    def test_4_assign_undefined_raises(self):
        """Behavior 4: assign to an undefined name raises LangNameError (the Step 1.2 usage example)."""
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            outer = Environment()                 # the program's top-level scope
            outer.define("x", 2)                  # let x = 2;
            inner = Environment(parent=outer)     # entering the block
            inner.define("x", 51)                 # let x = 51;   shadows the outer x
            print(inner.lookup("x"))              # print x;      inside the block
            print(outer.lookup("x"))              # print x;      after the block ends
            outer.define("y", 10)                 # let y = 10;
            inner.assign("y", 11)                 # y = 11;       inside the block, no let
            print(outer.lookup("y"))              # the outer y changed
        self.assertEqual(out.getvalue().split(), ["51", "2", "11"],
                         "the shadowing program must print 51, then 2, then 11")
        with self.assertRaises(LangNameError) as caught:
            inner.assign("nope", 0)               # nope = 0;     nobody defined nope
        self.assertNotIsInstance(caught.exception, KeyError)
        self.assertIn("nope", str(caught.exception),
                      "the LangNameError message must contain the variable name")
        # The failed assign created nothing, in either scope.
        with self.assertRaises(LangNameError):
            inner.lookup("nope")
        with self.assertRaises(LangNameError):
            outer.lookup("nope")

    def test_5_scope_restoration(self):
        """Behavior 5: discarding a child scope leaves the outer bindings exactly as they should be."""
        outer = Environment()
        outer.define("x", 2)
        outer.define("y", 10)
        inner = Environment(parent=outer)        # enter the block
        inner.define("x", 51)                    # let x = 51;   shadows, must not overwrite outer x
        inner.assign("y", 11)                    # y = 11;       must update outer y through assign
        inner.define("z", 99)                    # let z = 99;   must stay in the block
        del inner                                # leave the block
        self.assertEqual(outer.lookup("x"), 2, "the outer x is restored once the block is left")
        self.assertEqual(outer.lookup("y"), 11, "the assign inside the block reached the outer y")
        with self.assertRaises(LangNameError):
            outer.lookup("z")                    # z lived only in the block
        # Re-entering a fresh block sees the outer bindings, not the old block's.
        again = Environment(parent=outer)
        self.assertEqual(again.lookup("x"), 2)
        self.assertEqual(again.lookup("y"), 11)
        with self.assertRaises(LangNameError):
            again.lookup("z")


# ---------------------------------------------------------------------------
# Part 2: the three-nested-block trace program, one call per numbered step.
# Run with:  python3 test_environment.py --trace
# ---------------------------------------------------------------------------

def _chain(env, names):
    """Render an environment chain innermost-first, like C{y=0} -> B{z=12} -> A{x=20} -> top{x=1, y=12}."""
    try:
        parts = []
        while env is not None:
            bindings = ", ".join(f"{k}={v}" for k, v in env._bindings.items())
            parts.append(f"{names.get(id(env), '?')}{{{bindings}}}")
            env = env._parent
        return " -> ".join(parts)
    except AttributeError:
        return "(chain not shown: this script reads the skeleton's _bindings and _parent attributes)"


def run_trace():
    """Run the Part 2 program step by step and print the chain and result at each step."""
    names = {}

    def show(step, line, env, result):
        print(f"step {step:>2}  {line:<14} {_chain(env, names):<48} {result}")

    print("Part 2 trace program (steps numbered as on the lab page):")
    print(f"{'':8}  {'line':<14} {'environment chain':<48} result")

    top = Environment()                                   # the program's top-level scope
    names[id(top)] = "top"
    top.define("x", 1)                                    # step 1:  let x = 1;
    show(1, "let x = 1;", top, "x=1 created in top")
    top.define("y", 10)                                   # step 2:  let y = 10;
    show(2, "let y = 10;", top, "y=10 created in top")

    a = Environment(parent=top)                           # step 3:  enter block A
    names[id(a)] = "A"
    show(3, "{", a, "enter A")
    a.define("x", 2)                                      # step 4:  let x = 2;
    show(4, "let x = 2;", a, "x=2 created in A (shadows top's x)")
    a.assign("y", a.lookup("y") + a.lookup("x"))          # step 5:  y = y + x;
    show(5, "y = y + x;", a, f"y={a.lookup('y')} assigned (nearest y is in top)")

    b = Environment(parent=a)                             # step 6:  enter block B
    names[id(b)] = "B"
    show(6, "{", b, "enter B")
    b.assign("x", b.lookup("x") * 10)                     # step 7:  x = x * 10;
    show(7, "x = x * 10;", b, f"x={b.lookup('x')} assigned (nearest x is in A)")
    b.define("z", b.lookup("y"))                          # step 8:  let z = y;
    show(8, "let z = y;", b, f"z={b.lookup('z')} created in B")

    c = Environment(parent=b)                             # step 9:  enter block C
    names[id(c)] = "C"
    show(9, "{", c, "enter C")
    c.define("y", 0)                                      # step 10: let y = 0;
    show(10, "let y = 0;", c, "y=0 created in C (shadows top's y)")
    c.assign("z", c.lookup("z") + c.lookup("x"))          # step 11: z = z + x;
    show(11, "z = z + x;", c, f"z={c.lookup('z')} assigned (nearest z is in B)")
    show(12, "print y;", c, f"prints {c.lookup('y')}")    # step 12: print y;
    show(13, "}", b, "leave C (back to B)")               # step 13: leave block C

    show(14, "print x;", b, f"prints {b.lookup('x')}")    # step 14: print x;
    show(15, "print z;", b, f"prints {b.lookup('z')}")    # step 15: print z;
    show(16, "}", a, "leave B (back to A)")               # step 16: leave block B

    show(17, "print x;", a, f"prints {a.lookup('x')}")    # step 17: print x;
    show(18, "}", top, "leave A (back to top)")           # step 18: leave block A

    show(19, "print x;", top, f"prints {top.lookup('x')}")   # step 19: print x;
    show(20, "print y;", top, f"prints {top.lookup('y')}")   # step 20: print y;

    printed = [c.lookup("y"), b.lookup("x"), b.lookup("z"), a.lookup("x"), top.lookup("x"), top.lookup("y")]
    print()
    print("The six printed values, in order (steps 12, 14, 15, 17, 19, 20):")
    for value in printed:
        print(value)


if __name__ == "__main__":
    want_trace = "--trace" in sys.argv
    argv = [arg for arg in sys.argv if arg != "--trace"]
    result = unittest.main(argv=argv, exit=False).result
    if want_trace:
        print()
        if result.wasSuccessful():
            run_trace()
        else:
            print("Fix the failing tests above before running the trace program.")
    sys.exit(0 if result.wasSuccessful() else 1)
