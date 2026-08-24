---
layout: notes
permalink: /Tutorials/ParserCombinators
title: "CS374: Parser Combinators, Parsers as First-Class Values"

info:
  coursenum: CS374
  goals:
    - "Implemented the core `Parser` type as a function from `(str, int)` to `(value, int) | None` and built atomic parsers for single characters and character classes"
    - "Implemented the four fundamental combinators: `seq` (sequence), `alt` (alternation), `many` (repetition), and `map` (transformation)"
    - "Built a complete expression parser for Mini arithmetic that handles operator precedence without separate grammar notation"
    - "Connected parser combinators to the monad abstraction from the Monads activity and explained what `bind` does in the parsing context"
    - "Compared the combinator parser to the recursive-descent parser from the interpreter assignment, identifying the tradeoffs in readability, error messages, and extensibility"

tags:
  - parsing
  - combinators

---
# Tutorial: Parser Combinators, Parsers as First-Class Values

## Learning Goals

By the end of this tutorial, you will have:

- Implemented the core `Parser` type as a function from `(str, int)` to `(value, int) | None` and built atomic parsers for single characters and character classes
- Implemented the four fundamental combinators: `seq` (sequence), `alt` (alternation), `many` (repetition), and `map` (transformation)
- Built a complete expression parser for Mini arithmetic that handles operator precedence without separate grammar notation
- Connected parser combinators to the monad abstraction from the Monads activity and explained what `bind` does in the parsing context
- Compared the combinator parser to the recursive-descent parser from the interpreter assignment, identifying the tradeoffs in readability, error messages, and extensibility

A **parser combinator library** builds parsers by composing small parser values with combinator functions.  A parser is simply a function from a string position to either `(value, new_position)` on success or `None` on failure.  Combinators (`seq`, `alt`, `many`, `map`) combine parsers into larger parsers the same way function composition combines functions.  The result is a recursive-descent parser written in the host language's normal expression syntax, with no separate grammar notation.  This tutorial walks from the atomic building block up to a complete expression parser for Mini's arithmetic, all in ~200 lines of Python.  **Prerequisites:** Monads activity (parsers form a monad); Lambda Calculus and Recursive Descent activities.

---

## Part 0: The Core Idea

A **parser** is a value of type:

```
Parser[A] = str × int -> (A × int) | None
```

Given the full input string and a current position, it returns either `(value, next_position)` or `None` (failure).  The entire combinator library is built on this representation.

```python
try:
    # The simplest possible parser: match one exact character
    def char(c):
        def parse(s, pos):
            if pos < len(s) and s[pos] == c:
                return (c, pos + 1)
            return None
        return parse

    # Test it
    p = char('a')
    print(p("abc", 0))   # ('a', 1) - success
    print(p("abc", 1))   # None     - 'b' != 'a'
    print(p("", 0))      # None     - out of bounds

except Exception as e:
    print(f"[pc:char] {e}")
    import traceback; traceback.print_exc()
```

Every parser in this tutorial is a function built by calling combinators.  There are no classes yet, just functions returning functions.

---

## Part 1: Atomic Parsers

The primitives parse individual characters or character classes.

```python
try:
    import re

    def char(c):
        def parse(s, pos):
            if pos < len(s) and s[pos] == c:
                return (c, pos + 1)
            return None
        return parse

    def satisfy(pred, name="char"):
        """Match any character satisfying pred."""
        def parse(s, pos):
            if pos < len(s) and pred(s[pos]):
                return (s[pos], pos + 1)
            return None
        return parse

    def regex(pattern, flags=0):
        """Match a regex anchored at the current position."""
        rx = re.compile(pattern, flags)
        def parse(s, pos):
            m = rx.match(s, pos)
            if m:
                return (m.group(0), m.end())
            return None
        return parse

    def lit(string):
        """Match a literal string."""
        n = len(string)
        def parse(s, pos):
            if s[pos:pos+n] == string:
                return (string, pos + n)
            return None
        return parse

    def eof():
        """Match the end of input."""
        def parse(s, pos):
            return (None, pos) if pos == len(s) else None
        return parse

    # Quick tests
    digit = satisfy(str.isdigit, "digit")
    alpha = satisfy(str.isalpha, "letter")
    whitespace = regex(r'\s+')

    print(digit("5abc", 0))        # ('5', 1)
    print(alpha("hello", 0))       # ('h', 1)
    print(whitespace("  abc", 0))  # ('  ', 2)
    print(lit("if")("if x", 0))   # ('if', 2)

except Exception as e:
    print(f"[pc:atomic] {e}")
    import traceback; traceback.print_exc()
```

---

## Part 2: Combinator Primitives

Four combinators build everything else: `seq` (sequence), `alt` (choice), `many` (repetition), and `map` (transform result).

```python
try:
    import re

    # --- Re-define atomics inline for self-contained cell ---
    def satisfy(pred):
        def parse(s, pos):
            return (s[pos], pos+1) if pos < len(s) and pred(s[pos]) else None
        return parse
    def regex(pat):
        rx = re.compile(pat)
        def parse(s, pos):
            m = rx.match(s, pos)
            return (m.group(0), m.end()) if m else None
        return parse
    def lit(string):
        n = len(string)
        def parse(s, pos):
            return (string, pos+n) if s[pos:pos+n] == string else None
        return parse

    # --- The four core combinators ---

    def seq(*parsers):
        """Run parsers left-to-right; return list of results. Fails if any fails."""
        def parse(s, pos):
            results = []
            for p in parsers:
                out = p(s, pos)
                if out is None: return None
                val, pos = out
                results.append(val)
            return (results, pos)
        return parse

    def alt(*parsers):
        """Try each parser in order; return first success."""
        def parse(s, pos):
            for p in parsers:
                out = p(s, pos)
                if out is not None:
                    return out
            return None
        return parse

    def many(p):
        """Match p zero or more times; return list of results."""
        def parse(s, pos):
            results = []
            while True:
                out = p(s, pos)
                if out is None: break
                val, pos = out
                results.append(val)
            return (results, pos)
        return parse

    def many1(p):
        """Match p one or more times."""
        def parse(s, pos):
            out = p(s, pos)
            if out is None: return None
            val, pos = out
            results = [val]
            while True:
                out = p(s, pos)
                if out is None: break
                v, pos = out
                results.append(v)
            return (results, pos)
        return parse

    def pmap(p, fn):
        """Transform the result of p with fn."""
        def parse(s, pos):
            out = p(s, pos)
            return (fn(out[0]), out[1]) if out is not None else None
        return parse

    def between(left, p, right):
        """Parse left, then p, then right; return p's result."""
        return pmap(seq(left, p, right), lambda r: r[1])

    def skip(p):
        """Run p and discard its result (return None as value)."""
        return pmap(p, lambda _: None)

    # Quick tests
    digit = satisfy(str.isdigit)
    alpha = satisfy(str.isalpha)

    digits = pmap(many1(digit), lambda ds: int(''.join(ds)))
    print("digits:", digits("123abc", 0))     # (123, 3)

    word = pmap(many1(alpha), ''.join)
    print("word:", word("hello world", 0))    # ('hello', 5)

    either = alt(digits, word)
    print("alt a:", either("42", 0))           # (42, 2)
    print("alt b:", either("hi", 0))           # ('hi', 2)

    ws = skip(regex(r'\s*'))                   # optional whitespace, discard
    tok = lambda p: seq(p, ws)[0] if False else pmap(seq(p, ws), lambda r: r[0])
    # Simplified token: parse p then skip whitespace
    def token(p):
        ws_ = regex(r'\s*')
        def parse(s, pos):
            out = p(s, pos)
            if out is None: return None
            val, pos = out
            ws_out = ws_(s, pos)
            if ws_out: _, pos = ws_out
            return (val, pos)
        return parse

    number = token(digits)
    print("number+ws:", number("42   rest", 0))  # (42, 6)

except Exception as e:
    print(f"[pc:combinators] {e}")
    import traceback; traceback.print_exc()
```

---

## Part 3: Recursive Parsers and `forward`

Parsers for grammars with recursion (like expressions) need forward references: `expr` calls `term` which calls `factor` which calls `expr` for parenthesized sub-expressions.  A `forward` cell solves this cleanly.

```python
try:
    import re

    # --- Minimal combinator library (inline) ---
    def satisfy(pred):
        def p(s, i): return (s[i], i+1) if i < len(s) and pred(s[i]) else None
        return p
    def regex(pat):
        rx = re.compile(pat)
        def p(s, i):
            m = rx.match(s, i)
            return (m.group(0), m.end()) if m else None
        return p
    def lit(string):
        n = len(string)
        def p(s, i): return (string, i+n) if s[i:i+n] == string else None
        return p
    def seq(*ps):
        def p(s, i):
            res, pos = [], i
            for q in ps:
                out = q(s, pos)
                if out is None: return None
                v, pos = out; res.append(v)
            return (res, pos)
        return p
    def alt(*ps):
        def p(s, i):
            for q in ps:
                out = q(s, i)
                if out is not None: return out
            return None
        return p
    def many(q):
        def p(s, i):
            res, pos = [], i
            while True:
                out = q(s, pos)
                if out is None: break
                v, pos = out; res.append(v)
            return (res, pos)
        return p
    def pmap(q, fn):
        def p(s, i):
            out = q(s, i)
            return (fn(out[0]), out[1]) if out else None
        return p
    def token(q):
        ws = regex(r'\s*')
        def p(s, i):
            out = q(s, i)
            if not out: return None
            v, i2 = out
            m = ws(s, i2)
            return (v, m[1] if m else i2)
        return p

    # A forward-reference cell: a mutable parser slot
    class Forward:
        def __init__(self): self._inner = None
        def set(self, p): self._inner = p
        def __call__(self, s, i):
            return self._inner(s, i)

    # Build a simple arithmetic parser: expr = term (('+' | '-') term)*
    expr = Forward()
    term = Forward()
    factor = Forward()

    number = token(pmap(regex(r'\d+(\.\d*)?'), float))
    lparen = token(lit('('))
    rparen = token(lit(')'))
    add_op = token(alt(lit('+'), lit('-')))
    mul_op = token(alt(lit('*'), lit('/')))

    # factor = number | '(' expr ')'
    factor.set(alt(
        number,
        pmap(seq(lparen, expr, rparen), lambda r: r[1])
    ))

    # term = factor (('*' | '/') factor)*
    def build_term(s, i):
        out = factor(s, i)
        if out is None: return None
        val, pos = out
        while True:
            op_out = mul_op(s, pos)
            if op_out is None: break
            op, pos = op_out
            rhs_out = factor(s, pos)
            if rhs_out is None: return None
            rhs, pos = rhs_out
            val = val * rhs if op == '*' else val / rhs
        return (val, pos)
    term.set(build_term)

    # expr = term (('+' | '-') term)*
    def build_expr(s, i):
        out = term(s, i)
        if out is None: return None
        val, pos = out
        while True:
            op_out = add_op(s, pos)
            if op_out is None: break
            op, pos = op_out
            rhs_out = term(s, pos)
            if rhs_out is None: return None
            rhs, pos = rhs_out
            val = val + rhs if op == '+' else val - rhs
        return (val, pos)
    expr.set(build_expr)

    # Test the parser
    tests = [
        "1 + 2",
        "2 + 3 * 4",
        "(2 + 3) * 4",
        "10 / 2 - 1",
        "2 * (3 + 4) * (1 + 1)",
    ]
    for t in tests:
        result = expr(t, 0)
        print(f"  {t!r:30s} = {result[0] if result else 'PARSE FAILURE'}")

except Exception as e:
    print(f"[pc:recursive] {e}")
    import traceback; traceback.print_exc()
```

---

## Part 4: Parsers as a Monad

Notice that `seq` + `pmap` together implement monadic bind for parsers:

```
p.bind(f) = pmap(seq(p, ...), ...)
```

More precisely: `Parser` is a monad where:
- `return(x)` is a parser that consumes nothing and returns `x`
- `p.bind(f)` runs `p`, takes its value, feeds it to `f` to get a second parser, then runs that parser at the new position

This is exactly the *Parser monad* from the Monads activity Exercise 2!

```python
try:
    # The Parser monad, explicitly
    class Parser:
        def __init__(self, fn):
            self._fn = fn

        def __call__(self, s, pos=0):
            return self._fn(s, pos)

        @classmethod
        def pure(cls, value):
            """return: consume nothing, return value."""
            return cls(lambda s, pos: (value, pos))

        def bind(self, f):
            """>>= : run self, feed result to f, run resulting parser."""
            def run(s, pos):
                out = self(s, pos)
                if out is None: return None
                val, pos2 = out
                return f(val)(s, pos2)
            return Parser(run)

        def map(self, fn):
            return self.bind(lambda v: Parser.pure(fn(v)))

        def then(self, other):
            """Run self then other; return other's result."""
            return self.bind(lambda _: other)

        def skip(self, other):
            """Run self then other; return self's result."""
            return self.bind(lambda v: other.map(lambda _: v))

    # Primitive parsers as Parser objects
    def char_p(c):
        return Parser(lambda s, pos:
            (c, pos+1) if pos < len(s) and s[pos] == c else None)

    import re
    def regex_p(pat):
        rx = re.compile(pat)
        return Parser(lambda s, pos:
            (m.group(0), m.end()) if (m := rx.match(s, pos)) else None)

    def lit_p(string):
        n = len(string)
        return Parser(lambda s, pos:
            (string, pos+n) if s[pos:pos+n] == string else None)

    # "do-notation" via method chaining
    # Parse "N + M" and return the sum:
    ws = regex_p(r'\s*')
    def tok(p): return p.skip(ws)

    number = tok(regex_p(r'\d+').map(int))
    plus   = tok(lit_p('+'))

    sum_parser = (
        number
        .bind(lambda left:
            plus
            .then(number)
            .map(lambda right: left + right))
    )

    print("sum parser:", sum_parser("3 + 4", 0))   # (7, 5)
    print("fails on:", sum_parser("3 - 4", 0))      # None

except Exception as e:
    print(f"[pc:monad] {e}")
    import traceback; traceback.print_exc()
```

The connection is complete: **the Parser monad is the Monads activity's Exercise 2**, and `do`-notation lets you write parsers that look like grammars.

---

## Part 5: A Complete Mini Expression Parser with AST

Putting it all together: parse Mini arithmetic expressions into AST nodes.

```python
try:
    import re
    from dataclasses import dataclass
    from typing import Optional

    # --- Minimal Parser monad (inline) ---
    class P:
        def __init__(self, fn): self._fn = fn
        def __call__(self, s, pos=0): return self._fn(s, pos)
        @classmethod
        def pure(cls, v): return cls(lambda s, p: (v, p))
        def bind(self, f):
            def run(s, pos):
                out = self(s, pos)
                return None if out is None else f(out[0])(s, out[1])
            return P(run)
        def map(self, fn): return self.bind(lambda v: P.pure(fn(v)))
        def then(self, other): return self.bind(lambda _: other)
        def skip(self, other): return self.bind(lambda v: other.map(lambda _: v))
        @classmethod
        def alt(cls, *ps):
            def run(s, pos):
                for p in ps:
                    out = p(s, pos)
                    if out is not None: return out
                return None
            return cls(run)
        @classmethod
        def many(cls, q):
            def run(s, pos):
                results, cur = [], pos
                while True:
                    out = q(s, cur)
                    if out is None: break
                    v, cur = out; results.append(v)
                return (results, cur)
            return cls(run)

    def tok(pat, fn=None):
        rx = re.compile(pat + r'\s*')
        def run(s, pos):
            m = rx.match(s, pos)
            if not m: return None
            v = m.group(1) if m.lastindex else m.group(0).strip()
            return (fn(v) if fn else v, m.end())
        return P(run)

    # --- AST nodes ---
    @dataclass
    class Num:
        value: float
        def __repr__(self): return f"Num({self.value})"

    @dataclass
    class BinOp:
        op: str
        left: object
        right: object
        def __repr__(self): return f"BinOp({self.op!r}, {self.left}, {self.right})"

    @dataclass
    class UnaryMinus:
        operand: object
        def __repr__(self): return f"Neg({self.operand})"

    # --- Grammar ---
    class FwdP:
        def __init__(self): self._p = None
        def set(self, p): self._p = p
        def __call__(self, s, pos): return self._p(s, pos)

    expr_p   = FwdP()
    term_p   = FwdP()
    unary_p  = FwdP()
    primary_p = FwdP()

    number_p = tok(r'(\d+(?:\.\d*)?)', float).map(Num)
    lparen   = tok(r'\(')
    rparen   = tok(r'\)')
    minus_tok = tok(r'-')
    add_op   = P.alt(tok(r'\+'), tok(r'-'))
    mul_op   = P.alt(tok(r'\*'), tok(r'/'))

    # primary = number | '(' expr ')'
    primary_p.set(P.alt(
        number_p,
        P(lambda s, pos: (
            (lambda inner_out:
                None if inner_out is None else
                (lambda rp_out:
                    None if rp_out is None else
                    (inner_out[0], rp_out[1])
                )(rparen(s, inner_out[1]))
            )(P(expr_p)(s, lparen(s, pos)[1]) if lparen(s, pos) else None)
        ) if lparen(s, pos) else None)
    ))

    # Simpler primary using bind
    def make_primary():
        def paren_expr(s, pos):
            out = lparen(s, pos)
            if out is None: return None
            _, pos2 = out
            out2 = expr_p(s, pos2)
            if out2 is None: return None
            val, pos3 = out2
            out3 = rparen(s, pos3)
            if out3 is None: return None
            return (val, out3[1])
        return P.alt(number_p, P(paren_expr))

    primary_p.set(make_primary())

    # unary = '-' unary | primary
    def make_unary():
        def unary_minus(s, pos):
            out = minus_tok(s, pos)
            if out is None: return None
            _, pos2 = out
            out2 = unary_p(s, pos2)
            if out2 is None: return None
            v, pos3 = out2
            return (UnaryMinus(v), pos3)
        return P.alt(P(unary_minus), primary_p)

    unary_p.set(make_unary())

    # term = unary (('*' | '/') unary)*
    def left_assoc(base, op_p):
        def run(s, pos):
            out = base(s, pos)
            if out is None: return None
            val, pos2 = out
            while True:
                op_out = op_p(s, pos2)
                if op_out is None: break
                op, pos3 = op_out
                rhs_out = base(s, pos3)
                if rhs_out is None: break
                rhs, pos2 = rhs_out
                val = BinOp(op, val, rhs)
            return (val, pos2)
        return P(run)

    term_p.set(left_assoc(P(unary_p), mul_op))
    expr_p.set(left_assoc(P(term_p), add_op))

    # Evaluate the AST
    def eval_ast(node):
        if isinstance(node, Num): return node.value
        if isinstance(node, UnaryMinus): return -eval_ast(node.operand)
        if isinstance(node, BinOp):
            l, r = eval_ast(node.left), eval_ast(node.right)
            return l + r if node.op == '+' else l - r if node.op == '-' else l * r if node.op == '*' else l / r

    tests = [
        "1 + 2",
        "2 + 3 * 4",
        "(2 + 3) * 4",
        "-5 + 3",
        "10 / (2 + 3)",
    ]
    for src in tests:
        result = expr_p(src + " ", 0)
        if result:
            tree, _ = result
            print(f"  {src!r:20s}  tree: {tree}  value: {eval_ast(tree)}")
        else:
            print(f"  {src!r:20s}  PARSE FAILURE")

except Exception as e:
    print(f"[pc:mini] {e}")
    import traceback; traceback.print_exc()
```

---

## Part 6: Haskell's Parsec, The Industrial Version

Python's combinator library above mirrors Haskell's **Parsec** (and its successor **Megaparsec**), which is used in real production compilers (Pandoc, GHC extensions).  Parsec's operators are:

| Python | Haskell Parsec | Meaning |
|---|---|---|
| `seq(p, q)` | `p >> q` or `do {x<-p; y<-q; ...}` | sequence |
| `alt(p, q)` | `p <|> q` | choice |
| `pmap(p, f)` | `fmap f p` or `p <$> f` | transform result |
| `many(p)` | `many p` | zero or more |
| `many1(p)` | `some p` | one or more |
| `between(l, p, r)` | `between l r p` | surrounded |
| `P.pure(v)` | `pure v` or `return v` | inject value |
| `p.bind(f)` | `p >>= f` | monadic bind |

A Parsec parser for the same arithmetic grammar looks like:

```haskell
-- Haskell Parsec (reference - do not run)
import Text.Parsec

expr :: Parsec String () Double
expr = do
  t <- term
  ts <- many (do op <- oneOf "+-"; t2 <- term; return (op, t2))
  return (foldl applyOp t ts)
  where
    applyOp acc ('+', r) = acc + r
    applyOp acc ('-', r) = acc - r
    applyOp _   (_, r)   = r

term :: Parsec String () Double
term = do
  f <- factor
  fs <- many (do op <- oneOf "*/"; f2 <- factor; return (op, f2))
  return (foldl applyOp f fs)
  where ...
```

The `do`-notation is the same monadic sequencing you saw in the Monads activity, here used for parsing.

---

## Part 7: Error Recovery and Committed Choice

A real parser combinator library needs **committed choice** (also called *cut* in Prolog): once a prefix is consumed, stop trying alternatives and report an error rather than silently backtracking.  This prevents confusing error messages.

Parsec achieves this with `try`: `try p <|> q` backtracks on failure of `p`; plain `p <|> q` commits once `p` consumes input.

```python
try:
    # Simulating committed choice: once a keyword prefix matches, error if
    # the rest fails rather than falling through to the next alternative.

    import re

    class ParseError(Exception):
        def __init__(self, msg, pos): super().__init__(msg); self.pos = pos

    def committed_alt(primary_p, fallback_p, commit_p):
        """Try commit_p (peek); if it matches, run primary_p with hard errors.
           Otherwise run fallback_p."""
        def run(s, pos):
            peek = commit_p(s, pos)
            if peek is not None:
                out = primary_p(s, pos)
                if out is None:
                    raise ParseError(
                        f"Parse error at pos {pos}: expected more after '{s[pos:pos+10]!r}'", pos)
                return out
            return fallback_p(s, pos)
        return run  # (just a function, not Parser object, for simplicity)

    print("committed_alt defined (see Parsec's 'try' for the full story)")

except Exception as e:
    print(f"[pc:error] {e}")
    import traceback; traceback.print_exc()
```

---

## Summary

| Concept | Python implementation | Haskell Parsec |
|---|---|---|
| Parser type | `fn(str, int) -> (A, int) \| None` | `Parsec s u a` |
| Atomic | `char`, `satisfy`, `regex`, `lit` | `char`, `satisfy`, `string` |
| Sequence | `seq(p, q)` | `p >> q`, `do` |
| Choice | `alt(p, q)` | `p <\|> q` |
| Repetition | `many(p)`, `many1(p)` | `many`, `some` |
| Transform | `pmap(p, fn)` | `fmap fn p` |
| Monadic bind | `p.bind(f)` | `p >>= f` |
| Forward ref | `Forward` class | `mfix`, recursive `do` |
| Error | `raise ParseError` | `unexpected`, `<?>`  |

**Key insight:** a parser combinator library is just the Parser monad, and the Parser monad is just a function.  All the power of recursive-descent parsing, all the composability of functional programming, in ~100 lines of Python.

---

## Further Reading

- Hutton, Graham and Meijer, Erik.  "Monadic Parser Combinators" (1996).  The original paper; builds the full library you saw today.
- Leijen, Daan.  *Parsec: A practical parser library* (2001).  The Haskell library this tutorial mirrors.
- Megaparsec (Haskell): https://hackage.haskell.org/package/megaparsec: the modern successor.
- Python's `parsy` library: https://parsy.readthedocs.io: a production-quality Python combinator library.
- Norvig, Peter.  "How to Write a Spell Checker" and "Lispy": two famous small parsers in Python; identify the combinator pattern in each.

# From the Parsing Expressions Activity: Runnable Models

The three models below were previously embedded in the *Parsing Expressions* class session.  They are code you run rather than reasoning you do together, so they live here.  Pratt parsing in particular is beyond the grammar the Parser assignment requires; it is here because it is the technique most real hand-written parsers actually use.

## Model 2: Precedence Table (Runnable)

Before writing parser code, it helps to see that "precedence" is just a number: a higher number means "bind tighter" (resolve sooner).  This model lets you experiment with two different precedence tables on the same token stream so you can observe concretely how changing one number changes the resulting tree, and therefore the numeric result.  Pay attention to the flat-precedence case: it is a useful stress-test for understanding what your parser *actually* does rather than what you think it does.

Different precedence assignments for the same token stream produce completely different trees and values.  The model below encodes two precedence tables and a simple "what would this mean?" validator that folds a flat token list according to each table, showing both resulting trees.

```python
# Model 2: Two precedence tables, one token stream - two different meanings.
# We use a minimal Pratt-style fold (no full parser) just to show the shape.

PREC_STANDARD = {"+": 1, "-": 1, "*": 2, "/": 2}   # conventional
PREC_FLAT     = {"+": 1, "-": 1, "*": 1, "/": 1}   # all equal (APL-like)

def fold_left(tokens, prec_table):
    """
    Build a left-leaning tree from a flat infix token list
    [num, op, num, op, num, ...] using a simple precedence-climbing fold.
    Returns a nested tuple (op, left, right) or a number leaf.
    """
    try:
        # Convert to list of (value_or_op, is_op) pairs
        nums = []
        ops  = []
        for i, tok in enumerate(tokens):
            if i % 2 == 0:
                nums.append(float(tok))
            else:
                ops.append(tok)

        # Greedily fold higher-precedence operators first (left to right)
        result_nums = list(nums)
        result_ops  = list(ops)
        for current_prec in sorted(set(prec_table.values()), reverse=True):
            i = 0
            while i < len(result_ops):
                op = result_ops[i]
                if prec_table.get(op, 0) == current_prec:
                    node = (op, result_nums[i], result_nums[i+1])
                    result_nums = result_nums[:i] + [node] + result_nums[i+2:]
                    result_ops  = result_ops[:i] + result_ops[i+1:]
                else:
                    i += 1
        return result_nums[0]
    except Exception as e:
        print(f"[prectable:fold_left] {e}")
        import traceback; traceback.print_exc()
        return None

def evaluate(node):
    try:
        if isinstance(node, float):
            return node
        op, l, r = node
        lv, rv = evaluate(l), evaluate(r)
        if op == "+": return lv + rv
        if op == "-": return lv - rv
        if op == "*": return lv * rv
        if op == "/": return lv / rv
    except Exception as e:
        print(f"[prectable:evaluate] {e}")
        import traceback; traceback.print_exc()
        return None

def show(label, prec, tokens):
    tree = fold_left(tokens, prec)
    print(f"{label}:")
    print(f"  tree  = {tree}")
    print(f"  value = {evaluate(tree)}")

tokens = ["2", "+", "3", "*", "4"]
print(f"Token stream: {' '.join(tokens)}")
print()
show("Standard precedence (* > +)", PREC_STANDARD, tokens)
show("Flat precedence   (* = +)", PREC_FLAT,     tokens)

tokens2 = ["6", "-", "2", "-", "1"]
print()
print(f"Token stream: {' '.join(tokens2)}")
print()
show("Standard precedence (left assoc)", PREC_STANDARD, tokens2)
```

### Critical Thinking Questions

4.  The standard table gives `2 + 3 * 4 = 14`; the flat table gives `20`.  Trace exactly which fold step differs between the two tables for these five tokens.
5.  The flat table makes all operators equal in precedence and left-associative.  What value does `6 - 2 - 1` produce under flat precedence?  Is it the same as under standard precedence?  Explain why or why not.
6.  APL evaluates all binary operators right-to-left at equal precedence.  Modify `PREC_FLAT` to test that claim for `6 - 2 - 1` by changing the fold direction.  What value do you expect, and does it match?
7.  Annotate the correspondence: which EBNF symbol became the `while` condition, which became `advance()`, which became the recursive call?  (This is the translation table earning its keep.)

---

## Model 3: Recursive Descent Expression Parser (Runnable)

This model brings everything together into a working parser you can run.  The mutual call chain `parse_expr -> parse_addsub -> parse_muldiv -> parse_unary -> parse_primary -> parse_expr` encodes the entire precedence hierarchy: a function only returns to its caller after fully resolving everything at the current or tighter tiers.  Notice how parentheses are handled in `parse_primary` with a single call to `parse_expr`; that one line gives parentheses the power to override every precedence level.

A self-contained recursive descent parser for `+`, `-`, `*`, `/` and parentheses.  The mutual recursion `expr -> addsub -> muldiv -> unary -> primary -> ... -> expr` gives precedence without any table.

```python
# Model 3: Complete recursive-descent expression parser (stand-alone)
# Tokens are produced by a tiny hand-written tokeniser.

import re

def tokenize(src):
    try:
        token_re = re.compile(
            r'\s*(?:(\d+(?:\.\d+)?)|([+\-*/])|(\()|(\)))')
        tokens = []
        for m in token_re.finditer(src):
            if m.group(1): tokens.append(("NUM",   m.group(1)))
            elif m.group(2): tokens.append(("OP",  m.group(2)))
            elif m.group(3): tokens.append(("LPAREN", "("))
            elif m.group(4): tokens.append(("RPAREN", ")"))
        return tokens
    except Exception as e:
        print(f"[recdescent:tokenize] {e}")
        import traceback; traceback.print_exc()
        return []

class Parser:
    def __init__(self, src):
        self.tokens = tokenize(src)
        self.pos = 0

    def peek(self):
        return self.tokens[self.pos] if self.pos < len(self.tokens) else None

    def advance(self):
        tok = self.tokens[self.pos]; self.pos += 1; return tok

    def expect(self, ttype):
        tok = self.peek()
        if tok and tok[0] == ttype:
            return self.advance()
        raise SyntaxError(f"expected {ttype}, got {tok}")

    # expr -> addsub
    def parse_expr(self):
        return self.parse_addsub()

    # addsub -> muldiv { ("+" | "-") muldiv }
    def parse_addsub(self):
        try:
            node = self.parse_muldiv()
            while self.peek() and self.peek() == ("OP", "+") or \
                  self.peek() and self.peek() == ("OP", "-"):
                op = self.advance()[1]
                node = (op, node, self.parse_muldiv())
            return node
        except SyntaxError: raise
        except Exception as e:
            print(f"[recdescent:parse_addsub] {e}")
            import traceback; traceback.print_exc(); raise

    # muldiv -> unary { ("*" | "/") unary }
    def parse_muldiv(self):
        node = self.parse_unary()
        while self.peek() and self.peek() in (("OP","*"),("OP","/")):
            op = self.advance()[1]
            node = (op, node, self.parse_unary())
        return node

    # unary -> "-" unary | primary
    def parse_unary(self):
        if self.peek() == ("OP", "-"):
            self.advance()
            return ("neg", self.parse_unary())
        return self.parse_primary()

    # primary -> NUMBER | "(" expr ")"
    def parse_primary(self):
        tok = self.peek()
        if tok and tok[0] == "NUM":
            return ("num", float(self.advance()[1]))
        if tok and tok[0] == "LPAREN":
            self.advance()
            node = self.parse_expr()
            self.expect("RPAREN")
            return node
        raise SyntaxError(f"unexpected token {tok}")

def parse(src):
    try:
        p = Parser(src)
        tree = p.parse_expr()
        return tree
    except SyntaxError as e:
        return f"SyntaxError: {e}"

for expr in ["2+3*4", "2*3+4", "(2+3)*4", "7-2-1", "-3*2", "1+2+3+4"]:
    print(f"  {expr!r:18} -> {parse(expr)}")
```

### Critical Thinking Questions

8.  Trace `2 + 3 * 4` through the parser call by call: list every function invoked in order and what tuple each returns.  Confirm that `parse_muldiv` is called *by* `parse_addsub`, so `3 * 4` is resolved before the `+` node is built.
9. `parse_unary` calls itself for `--3`.  Is that left recursion?  Explain why it terminates here but `E -> E + T` would loop infinitely in a naive recursive descent.
10. `parse_primary`'s parenthesis branch calls `parse_expr`, the top of the chain.  Explain why this single call makes parentheses override every precedence level, and identify the matching production in the grammar at the top of this module.

---

## Model 4: Pratt Parsing (Runnable)

Pratt parsing (also called precedence climbing) is an elegant alternative to the tiered-function approach: instead of encoding precedence by the *depth* of a function chain, it encodes it as a *number* (the binding power) and uses a single loop with a numeric comparison to decide whether to keep consuming.  The result is exactly the same AST with far less boilerplate: adding a new operator means adding one entry to the `LBP` table, not writing a new function.  Both parsers run on the same test cases so you can confirm they agree.

> **Watch out!**  Pratt parsing is an elegant alternative that scales gracefully as your language grows, but it is easy to confuse the two binding-power roles.  The **left binding power (lbp)** of an operator is how tightly it pulls in a left operand that has already been parsed; the **right binding power** passed to the recursive `expression()` call controls how tightly the operator claims tokens on its right.  For left-associative operators these differ by exactly 1 (or you pass `bp` rather than `bp - 1`); for right-associative operators (like `**`) the right call must use `bp - 1` so a subsequent operator at the same level is allowed to win; see Exercise 1 for the concrete example.

A Pratt parser (precedence climbing) associates a *binding power* with each operator and decides whether to consume the next operator based on numeric comparison: no mutual recursion, no separate function per tier.  Both parsers should produce the same AST for `2 + 3 * 4 - 1`.

```python
# Model 4: Pratt parser (precedence climbing) and comparison with recursive descent

import re

def tokenize(src):
    try:
        token_re = re.compile(r'\s*(?:(\d+(?:\.\d+)?)|([+\-*/])|(\()|(\)))')
        toks = []
        for m in token_re.finditer(src):
            if   m.group(1): toks.append(("NUM",    m.group(1)))
            elif m.group(2): toks.append(("OP",     m.group(2)))
            elif m.group(3): toks.append(("LPAREN", "("))
            elif m.group(4): toks.append(("RPAREN", ")"))
        return toks
    except Exception as e:
        print(f"[pratt:tokenize] {e}")
        import traceback; traceback.print_exc()
        return []

# Binding powers: left-binding-power (lbp) controls whether the operator
# "pulls in" the subexpression to its right.
LBP = {"+": 10, "-": 10, "*": 20, "/": 20}

class PrattParser:
    def __init__(self, src):
        self.tokens = tokenize(src)
        self.pos = 0

    def peek(self):
        return self.tokens[self.pos] if self.pos < len(self.tokens) else None

    def advance(self):
        tok = self.tokens[self.pos]; self.pos += 1; return tok

    def nud(self, tok):
        """Null denotation: prefix position."""
        try:
            if tok[0] == "NUM":
                return ("num", float(tok[1]))
            if tok[0] == "LPAREN":
                node = self.expression(0)
                # consume RPAREN
                if self.peek() and self.peek()[0] == "RPAREN":
                    self.advance()
                return node
            if tok == ("OP", "-"):
                return ("neg", self.expression(100))
            raise SyntaxError(f"unexpected prefix token {tok}")
        except SyntaxError: raise
        except Exception as e:
            print(f"[pratt:nud] {e}")
            import traceback; traceback.print_exc(); raise

    def led(self, tok, left):
        """Left denotation: infix position."""
        try:
            op  = tok[1]
            bp  = LBP[op]
            right = self.expression(bp)   # same bp -> left assoc
            return (op, left, right)
        except Exception as e:
            print(f"[pratt:led] {e}")
            import traceback; traceback.print_exc(); raise

    def expression(self, rbp=0):
        """Parse an expression with right-binding-power floor rbp."""
        try:
            tok  = self.advance()
            left = self.nud(tok)
            while True:
                nxt = self.peek()
                if nxt is None: break
                if nxt[0] == "RPAREN": break
                op_bp = LBP.get(nxt[1], 0)
                if op_bp <= rbp: break
                left = self.led(self.advance(), left)
            return left
        except SyntaxError: raise
        except Exception as e:
            print(f"[pratt:expression] {e}")
            import traceback; traceback.print_exc(); raise

def pratt_parse(src):
    try:
        return PrattParser(src).expression(0)
    except SyntaxError as e:
        return f"SyntaxError: {e}"

# -- Recursive descent (same tokenizer) ----------------------------------
class RDParser:
    def __init__(self, src):
        self.tokens = tokenize(src); self.pos = 0
    def peek(self):
        return self.tokens[self.pos] if self.pos < len(self.tokens) else None
    def advance(self):
        tok = self.tokens[self.pos]; self.pos += 1; return tok
    def parse_expr(self): return self.parse_addsub()
    def parse_addsub(self):
        node = self.parse_muldiv()
        while self.peek() and self.peek() in (("OP","+"),("OP","-")):
            op = self.advance()[1]; node = (op, node, self.parse_muldiv())
        return node
    def parse_muldiv(self):
        node = self.parse_unary()
        while self.peek() and self.peek() in (("OP","*"),("OP","/")):
            op = self.advance()[1]; node = (op, node, self.parse_unary())
        return node
    def parse_unary(self):
        if self.peek() == ("OP", "-"):
            self.advance(); return ("neg", self.parse_unary())
        return self.parse_primary()
    def parse_primary(self):
        tok = self.peek()
        if tok and tok[0] == "NUM": return ("num", float(self.advance()[1]))
        if tok and tok[0] == "LPAREN":
            self.advance(); node = self.parse_expr()
            if self.peek() and self.peek()[0] == "RPAREN": self.advance()
            return node
        raise SyntaxError(f"unexpected {tok}")

def rd_parse(src):
    try:
        return RDParser(src).parse_expr()
    except SyntaxError as e:
        return f"SyntaxError: {e}"

tests = ["2+3*4-1", "2*3+4", "(2+3)*4", "7-2-1"]
print(f"{'Expression':<18} {'Pratt':<35} {'RecDescent'}")
print("-" * 80)
for t in tests:
    pr = pratt_parse(t)
    rd = rd_parse(t)
    match = "==" if pr == rd else "!="
    print(f"{t!r:<18} {str(pr):<35} {match} {rd}")
```

### Critical Thinking Questions

11.  Both parsers produce identical ASTs for `2 + 3 * 4 - 1`.  Now trace just the Pratt parser's `expression` calls for this input: what is the `rbp` argument on each call, and when does the `while` loop stop consuming?
12.  In the recursive descent parser, adding a new precedence tier requires a new function.  In the Pratt parser, what is the equivalent change?  Which approach do you find easier to extend, and why?
13.  Change `LBP["+"]` and `LBP["-"]` to `20` (equal to `*` and `/`).  Predict what tree `2 + 3 * 4` produces under this change before running.  Verify, then explain what "all equal precedence, left associative" means for expression evaluation.

---

