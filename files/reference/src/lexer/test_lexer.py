"""test_lexer.py -- test suite for the reference Lexer.

Run with either:
    python3 -m pytest test_lexer.py
    python3 test_lexer.py
"""

import os
import unittest

from lexer import Lexer, LexError, LexErrorList, tokenize

HERE = os.path.dirname(os.path.abspath(__file__))


def types(source, **kw):
    """Token types (excluding EOF) for a source string."""
    lx = Lexer(source, **kw)
    out = []
    while lx.peek().type != "EOF":
        out.append(lx.advance().type)
    return out


class TestTokenSpec(unittest.TestCase):
    def test_worked_example(self):
        toks = list(tokenize("let x = 42;"))
        self.assertEqual([(t.type, t.value, t.line, t.col) for t in toks], [
            ("LET", "let", 1, 1),
            ("IDENT", "x", 1, 5),
            ("EQ", "=", 1, 7),
            ("INT", "42", 1, 9),
            ("SEMICOLON", ";", 1, 11),
            ("EOF", "", 1, 12),
        ])

    def test_all_token_types(self):
        src = ('if else while let print true false and or not break continue '
               'foo 3.14 42 "s" <= >= == != = < > + - * / ( ) { } ;')
        self.assertEqual(types(src), [
            "IF", "ELSE", "WHILE", "LET", "PRINT", "TRUE", "FALSE",
            "AND", "OR", "NOT", "BREAK", "CONTINUE",
            "IDENT", "FLOAT", "INT", "STRING",
            "LE", "GE", "EQEQ", "NEQ", "EQ", "LT", "GT",
            "PLUS", "MINUS", "STAR", "SLASH",
            "LPAREN", "RPAREN", "LBRACE", "RBRACE", "SEMICOLON",
        ])

    def test_maximal_munch_keyword_prefixes(self):
        self.assertEqual(types("iffy"), ["IDENT"])
        self.assertEqual(types("whiles"), ["IDENT"])
        self.assertEqual(types("lets"), ["IDENT"])
        self.assertEqual(Lexer("iffy").peek().value, "iffy")

    def test_maximal_munch_operators(self):
        self.assertEqual(types("<="), ["LE"])
        self.assertEqual(types("=="), ["EQEQ"])
        self.assertEqual(types("!="), ["NEQ"])
        self.assertEqual(types(">="), ["GE"])
        self.assertEqual(types("<== !== >== a<=b"),
                         ["LE", "EQ", "NEQ", "EQ", "GE", "EQ",
                          "IDENT", "LE", "IDENT"])

    def test_float_before_int(self):
        lx = Lexer("3.14 42 .5")
        self.assertEqual(lx.advance().type, "FLOAT")
        self.assertEqual(lx.advance().type, "INT")
        self.assertEqual(lx.advance().type, "FLOAT")

    def test_comments_skipped_and_lines_tracked(self):
        toks = list(tokenize("# a comment\nlet x = 1; # trailing\nprint x;"))
        self.assertEqual(toks[0].type, "LET")
        self.assertEqual((toks[0].line, toks[0].col), (2, 1))
        print_tok = [t for t in toks if t.type == "PRINT"][0]
        self.assertEqual((print_tok.line, print_tok.col), (3, 1))


class TestStringEscapes(unittest.TestCase):
    def test_no_escapes(self):
        tok = Lexer('"no escapes"').peek()
        self.assertEqual(tok.type, "STRING")
        self.assertEqual(tok.value, '"no escapes"')      # raw lexeme kept
        self.assertEqual(tok.decoded, "no escapes")       # decoded value kept

    def test_all_four_escapes(self):
        self.assertEqual(Lexer(r'"tab\there"').peek().decoded, "tab\there")
        self.assertEqual(Lexer(r'"line\nbreak"').peek().decoded, "line\nbreak")
        self.assertEqual(Lexer(r'"quote\"end"').peek().decoded, 'quote"end')
        self.assertEqual(Lexer(r'"back\\slash"').peek().decoded, "back\\slash")

    def test_raw_and_decoded_differ(self):
        tok = Lexer(r'"a\nb"').peek()
        self.assertEqual(len(tok.value), 6)   # "a\nb" with quotes: 6 chars
        self.assertEqual(tok.decoded, "a\nb")
        self.assertEqual(len(tok.decoded), 3)

    def test_unsupported_escape_raises(self):
        with self.assertRaises(LexError) as cm:
            Lexer(r'"bad\qescape"').peek()
        self.assertIn("\\q", str(cm.exception))


class TestInterface(unittest.TestCase):
    def test_peek_is_idempotent(self):
        lx = Lexer("let x = 1;")
        first = lx.peek()
        for _ in range(10):
            self.assertEqual(lx.peek(), first)
        self.assertEqual(lx.advance(), first)
        self.assertEqual(lx.peek().type, "IDENT")

    def test_eof_forever(self):
        lx = Lexer("x")
        self.assertEqual(lx.advance().type, "IDENT")
        for _ in range(5):
            self.assertEqual(lx.peek().type, "EOF")
            self.assertEqual(lx.advance().type, "EOF")

    def test_two_consumption_patterns_agree(self):
        src = 'let x = 10; while x > 0 { print "hi\\n"; x = x - 1; }'
        lexer_a, lexer_b = Lexer(src), Lexer(src)
        tokens_a = []
        while lexer_a.peek().type != "EOF":
            tokens_a.append(lexer_a.advance())
        tokens_b = []
        tok = lexer_b.advance()
        while tok.type != "EOF":
            tokens_b.append(tok)
            tok = lexer_b.advance()
        self.assertEqual(tokens_a, tokens_b)

    def test_expect_success_and_failure(self):
        lx = Lexer("let x")
        self.assertEqual(lx.expect("LET").value, "let")
        with self.assertRaises(LexError) as cm:
            lx.expect("SEMICOLON")
        err = cm.exception
        self.assertIn("expected SEMICOLON", err.message)
        self.assertIn("found IDENT", err.message)
        self.assertEqual((err.line, err.col), (1, 5))


class TestJSONConfig(unittest.TestCase):
    def test_default_spec_file_matches_builtin(self):
        src = 'let x = 42; # comment'
        self.assertEqual(types(src),
                         types(src, config_path=os.path.join(HERE, "token_spec.json")))

    def test_alternate_dialect(self):
        src = "let x := 42; // a comment\nprint x;"
        lx = Lexer(src, config_path=os.path.join(HERE, "token_spec_alt.json"))
        got = []
        while lx.peek().type != "EOF":
            got.append(lx.advance().type)
        self.assertEqual(got, ["LET", "IDENT", "EQ", "INT", "SEMICOLON",
                               "PRINT", "IDENT", "SEMICOLON"])

    def test_bad_pattern_raises_lexerror(self):
        import json
        import tempfile
        bad = {"comment_char": "#", "tokens": [["BROKEN", "[unclosed"]]}
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as fh:
            json.dump(bad, fh)
            path = fh.name
        try:
            with self.assertRaises(LexError) as cm:
                Lexer("x", config_path=path)
            self.assertIn("BROKEN", str(cm.exception))
        finally:
            os.unlink(path)


class TestErrors(unittest.TestCase):
    """The five deliberate error programs required by Step 3c."""

    def test_error_1_at_sign(self):
        with self.assertRaises(LexError) as cm:
            list(tokenize("@"))
        err = cm.exception
        self.assertEqual((err.line, err.col), (1, 1))
        self.assertEqual(str(err), "LexError at line 1, col 1: unexpected character '@'")

    def test_error_2_unterminated_string(self):
        with self.assertRaises(LexError) as cm:
            list(tokenize('let s = "hello'))
        err = cm.exception
        # position of the OPENING quote, not end of input
        self.assertEqual((err.line, err.col), (1, 9))
        self.assertIn("unterminated string", err.message)

    def test_error_3_dollar_mid_program(self):
        with self.assertRaises(LexError) as cm:
            list(tokenize("let x = 1;\nlet y = $ + 2;"))
        err = cm.exception
        self.assertEqual((err.line, err.col), (2, 9))

    def test_error_4_collect_all_two_errors(self):
        with self.assertRaises(LexErrorList) as cm:
            Lexer("let @ = 1;\nlet $ = 2;", error_mode="collect_all")
        errs = cm.exception.errors
        self.assertEqual(len(errs), 2)
        self.assertEqual((errs[0].line, errs[0].col), (1, 5))
        self.assertEqual((errs[1].line, errs[1].col), (2, 5))

    def test_error_5_recovery_after_error(self):
        with self.assertRaises(LexErrorList) as cm:
            Lexer("@ let", error_mode="collect_all")
        exc = cm.exception
        self.assertEqual(len(exc.errors), 1)
        # the valid token immediately after the error was still recognized
        self.assertEqual([t.type for t in exc.tokens], ["LET", "EOF"])

    def test_fail_fast_is_lazy_until_reached(self):
        lx = Lexer("let @")
        self.assertEqual(lx.advance().type, "LET")  # fine before the error
        with self.assertRaises(LexError):
            lx.peek()


if __name__ == "__main__":
    unittest.main(verbosity=2)
