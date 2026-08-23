# mininote: a flex/bison mini-notation subset

This is the TidalCycles-style **mini-notation** subset built in the
"Parser Tables" class activity, packaged so you can build and run it
outside the browser.  It scans and parses patterns such as `bd sn`,
`bd*2`, `[bd sn]*2`, and `bd [sn sn] hh*2 ~`, builds an AST, prints the
tree, and evaluates the pattern into timed events within one cycle.

## Contents

| File | Purpose |
|------|---------|
| `mininote.l` | flex lexer spec: WORD, NUMBER, `~ [ ] * / ?`, whitespace |
| `mininote.y` | bison/yacc grammar with AST-building semantic actions |
| `ast.h` | tagged-union AST node type and constructor declarations |
| `ast.c` | constructor and tree-printer implementations (see Gaps below) |
| `eval.c` | structural-recursion evaluator (SEQ, GROUP, FAST, ATOM, REST) |
| `main.c` | driver: parse stdin, print the AST, print the event list |
| `Makefile` | standard flex/bison build |
| `samples.txt` | four sample patterns to try |

## Building with flex + bison

You need `flex`, `bison`, and a C compiler.  Then:

```sh
make
echo "bd [sn sn] hh*2 ~" | ./mininote
make test        # runs every line of samples.txt
```

The build steps, if you prefer to run them by hand:

```sh
bison -d mininote.y      # -> mininote.tab.c, mininote.tab.h
flex mininote.l          # -> lex.yy.c
cc -o mininote mininote.tab.c lex.yy.c ast.c eval.c main.c
```

Run `bison -v mininote.y` to also generate `mininote.output`, the full
LALR(1) automaton (every state and item set) which the activity walks
you through reading.

## Adapting to PLY (Python)

The Parser assignment uses Python, so you will likely translate rather
than compile this.  PLY (`ply.lex` / `ply.yacc`) mirrors flex/bison
almost line for line:

- Each flex rule becomes a `t_TOKEN` regex (e.g.
  `t_WORD = r'[a-zA-Z][a-zA-Z0-9]*'`), with whitespace in `t_ignore`.
- Each grammar production becomes a `def p_...(p):` function whose
  docstring is the BNF (e.g. `'term : term STAR NUMBER'`) and whose body
  assigns `p[0]` the way the yacc action assigns `$$` from `$1..$3`.
- The tagged-union `Node` in `ast.h` becomes a small class hierarchy or
  dataclasses: the same seven constructors.

You can equally well hand-roll a recursive descent parser for this
grammar after eliminating the left recursion in `sequence` and `term`.

## Sample patterns

Try these (also in `samples.txt`):

1. `bd sn`: a two-step sequence splitting the cycle in half
2. `bd [sn sn] hh*2 ~`: grouping, fast-repeat, and a rest
3. `[bd sn]*2`: a group repeated: four events in one cycle
4. `bd sn? hh/2 cp`: degrade (`?`) and slow (`/2`); see Gaps below

## Gaps relative to the activity

- `ast.c` is **not** listed in the activity; the activity declares the
  constructors in `ast.h` and calls `ast_print`, so this directory
  supplies straightforward implementations to make the example build.
- The `N_SLOW` and `N_DEGRADE` cases in `eval.c` are deliberately left
  unimplemented (they print a "not yet implemented" notice), exactly as
  scaffolded in the activity; implementing them is Exercises 2 and 3.
  Sample pattern 4 above parses fine but reports those notices when
  evaluated.
- The activity's compile-chain comment links with `-lfl`; because the
  lexer uses `%option noyywrap`, the flex library is not needed and the
  Makefile omits it (this also helps on macOS, where the library is
  named `-ll`).
