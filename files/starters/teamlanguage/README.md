# A small working language to start from

This folder is a complete language, small on purpose: numbers, the four arithmetic operators, parentheses, `let`, and `print`.  Your team language can start here, so the project needs nothing from any other assignment.

```bash
python3 repl.py                     # opens the REPL; type: print 1 + 2;
python3 repl.py samples/hello.lang  # runs one program
python3 -m unittest discover tests  # runs the tests
```

Each stage is one file, and each one does one job:

| File | Job |
|---|---|
| `lexer.py` | turns source text into tokens |
| `parser.py` | turns tokens into a tree, by recursive descent |
| `ast_nodes.py` | the tree's node classes |
| `interpreter.py` | walks the tree and runs it |
| `repl.py` | the REPL and the file-runner |

To add a feature, touch the stages in order.  A new token goes in `lexer.py`, a new rule in `parser.py`, a new node in `ast_nodes.py`, and a new case in `interpreter.py`.  A test in `tests/` goes first, so that you can watch it fail and then pass.
