# CS374 Reference Implementations — Staged Pipeline Releases

If an earlier stage of your language pipeline is broken, you should never be
blocked on the next assignment. Each reference implementation below is
released **when the assignment that depends on it is handed out**, so you can
swap it in for your own component and keep moving.

## Release schedule

| Release | Zip | Released | With |
|---------|-----|----------|------|
| Reference **Lexer** | `reference-lexer.zip` | **Oct 15** | the Parser assignment hand-out |
| Reference **Parser + AST** | `reference-parser.zip` | **Oct 27** | the Interpreter assignment hand-out |
| Reference **Interpreter** | `reference-interpreter.zip` | **Nov 12** | the team-project build phase |

Each zip is **self-contained**: the parser zip includes a copy of the
reference lexer, and the interpreter zip includes copies of both the
reference lexer and parser, so unzipping one directory gives you a complete
working pipeline up to that stage. Uncompressed copies live in `src/`
(`src/lexer/`, `src/parser/`, `src/interpreter/`).

## Usage policy

- **Declare it.** If your submission builds on a reference component, say
  so in one line in your README (e.g., *"This submission uses the reference
  lexer."*). That is the entire requirement.
- **No penalty.** Using a reference component never costs points on the
  current assignment. The current assignment is graded on the work it asks
  for, not on the stages beneath it.
- **Your original grade stands.** Using the reference lexer for the Parser
  assignment does not change your Lexer assignment grade — that grade was
  earned on its own deadline and stays as-is. The reference releases exist
  so one rough week doesn't cascade through the semester.
- **Mix freely.** You may use the reference lexer with your own parser, or
  your own lexer with the reference parser — the interfaces are exactly the
  assignment contracts (`peek`/`advance`/`expect`; the AST node dataclasses).

## Requirements

Python 3.10+ (developed and tested on 3.11), standard library only. Each
directory has its own README, and its test suite runs with either
`python3 -m pytest test_*.py` or plain `python3 test_*.py`.
