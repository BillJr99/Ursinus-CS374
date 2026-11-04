"""Every samples/NAME.lang must print exactly what samples/NAME.expected says."""
import glob
import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from interpreter import run  # noqa: E402
from lexer import LangError  # noqa: E402


def lines_of(source):
    out = []
    run(source, output=out.append)
    return out


class TestSamples(unittest.TestCase):
    def test_samples(self):
        paths = glob.glob(os.path.join(ROOT, "samples", "*.lang"))
        self.assertTrue(paths)
        for path in paths:
            with self.subTest(path=path):
                with open(path) as f:
                    source = f.read()
                with open(path[:-len(".lang")] + ".expected") as f:
                    expected = f.read().splitlines()
                self.assertEqual(lines_of(source), expected)

    def test_left_associative(self):
        self.assertEqual(lines_of("print 7 - 2 - 1;"), ["4"])

    def test_errors_name_stage_and_position(self):
        cases = [("print @;", "Lexical error at line 1, col 7"),
                 ("let = 1;", "Parse error at line 1, col 5"),
                 ("print y;", "Runtime error at line 1, col 7"),
                 ("print 1 / 0;", "Runtime error at line 1, col 9")]
        for source, message in cases:
            with self.subTest(source=source):
                with self.assertRaises(LangError) as caught:
                    lines_of(source)
                self.assertIn(message, str(caught.exception))


if __name__ == "__main__":
    unittest.main()
