---
layout: assignment
permalink: /Assignments/Transpiler
title: "CS374: Principles of Programming Languages - The Transpiler"

info:
  coursenum: CS374
  purpose: "To add new back ends to your language's front end — Python and JavaScript transpilers plus a stack-machine bytecode compiler and VM — and weigh the tradeoffs among interpretation, transpilation, and compilation."
  tilt:
    task: "Using the Visitor pattern, transpile Mini ASTs to runnable Python and JavaScript, compile them to stack-machine bytecode with a VM, and verify all four back ends produce identical output."
    criteria: "Assessed on correct Visitor-based transpilers, a working bytecode compiler and stack machine, cross-backend equivalence testing, and a comparative writeup, weighted 40/30/20/10; see the rubric below for the full breakdown."
  points: 100
  goals:
    - To implement the Visitor pattern for AST traversal and code generation
    - To transpile Mini language ASTs to two or more target languages (Python and JavaScript minimum)
    - To implement a stack-machine bytecode compiler and a virtual machine to run the bytecode
    - To understand the design tradeoffs between interpretation, transpilation, and compilation
  rubric:
    - weight: 40
      description: "Transpiler Implementation (Goals 1–2: implement the Visitor pattern and transpile Mini ASTs to Python and JavaScript)"
      preemerging: No working transpiler; visitors are missing or produce incorrect output
      beginning: A visitor exists and handles some nodes but fails on control flow or function definitions
      progressing: Transpilation to at least one target language works for all node types with a minor defect such as incorrect operator precedence in the output or missing newlines around blocks
      proficient: Both target transpilers produce syntactically correct, runnable output for all provided Mini programs using the Visitor pattern — demonstrating Goals 1 and 2; Python output runs under Python 3; JavaScript output runs under Node.js; operator precedence is correctly parenthesized in the output; and the output is idiomatic for each target
    - weight: 30
      description: "Bytecode Compiler and Stack Machine (Goal 3: implement a stack-machine bytecode compiler and a virtual machine to run the bytecode)"
      preemerging: No bytecode compiler exists
      beginning: A bytecode compiler exists but generates incorrect code for arithmetic or control flow
      progressing: The bytecode compiler handles expressions and simple statements correctly but fails on function calls or closures
      proficient: The bytecode compiler generates correct sequences for all expressions, statements, if/while, and function calls — demonstrating Goal 3; the stack machine executes them and produces the same output as the interpreter; an annotated trace of one program's execution (instruction, stack state, environment) is included
    - weight: 20
      description: "Testing and Comparison (Goal 4: understand the design tradeoffs between interpretation, transpilation, and compilation through end-to-end equivalence testing)"
      preemerging: No systematic testing; transpiler output is not verified against the interpreter
      beginning: Ad-hoc tests exist but the outputs of the transpiler and interpreter are not directly compared
      progressing: A test harness runs each Mini program through the interpreter, both transpilers, and the stack machine, comparing outputs; minor discrepancies exist on edge cases
      proficient: All four execution paths (interpreter, Python transpile-and-run, JS transpile-and-run, stack machine) produce identical output for the full test suite — demonstrating Goal 4 through concrete cross-backend verification; discrepancies are documented and explained; the harness is part of the submission
    - weight: 10
      description: "Writeup and Reflection (Goal 4: articulate the design tradeoffs between interpretation, transpilation, and compilation)"
      preemerging: An incomplete submission is provided
      beginning: The program is submitted, but not according to the directions in one or more ways
      progressing: The program is submitted according to the directions with a minor omission
      proficient: The submission includes a README explaining the design decisions for each target language, a table comparing the four execution approaches on the correctness/speed/debuggability axes, and thoughtful answers to the reflection prompts — demonstrating Goal 4 through articulated analysis of language implementation tradeoffs
  readings:
    - rtitle: "Transpilers and Compilers Activity"
      rlink: "https://liascript.github.io/course/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374-Fall2026/gh-pages/_pages/Activities/liascript-transpiler-compiler.md"
    - rtitle: "Tutorial: Build an Interpreter"
      rlink: "https://liascript.github.io/course/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374-Fall2026/gh-pages/_pages/Tutorials/tutorial-build-an-interpreter.md"

tags:
  - transpiler
  - compiler
  - bytecode
  - visitor
  - languages

---

This assignment adds three new *back ends* to your interpreter's front end (lexer + parser + AST): a Python transpiler, a JavaScript transpiler, and a stack-machine bytecode compiler with a virtual machine. The front end is unchanged; the choice of back end is a runtime flag. This is the architecture of every real language tool.

## Setup

Your starter point is the parser and AST from the Parser assignment. Import them unchanged. Create:

```
transpiler/
  lexer.py         (imported unchanged)
  parser.py        (imported unchanged)
  ast_nodes.py     (imported unchanged)
  visitor.py       (Part 1)
  python_target.py (Part 2a)
  js_target.py     (Part 2b)
  bytecode.py      (Part 3)
  vm.py            (Part 4)
  test_all.py      (Part 5)
  run.py           (the unified entry point)
```

The entry point `run.py` accepts a flag: `python run.py --target py foo.mini` runs the Python transpiler; `--target js` runs JavaScript; `--target vm` runs the stack machine; `--target interp` runs your interpreter. All four must produce identical stdout for all test programs.

## Part 1: The Visitor Base Class (10 points)

```python
# visitor.py
class Visitor:
    def visit(self, node):
        method = "visit_" + type(node).__name__
        fn = getattr(self, method, self.visit_default)
        return fn(node)

    def visit_default(self, node):
        raise NotImplementedError(
            f"{type(self).__name__} has no handler for {type(node).__name__}"
        )
```

Verify: subclass `Visitor` with a `PrettyPrinter` that re-implements your pretty-printer from the parser assignment using `visit_*` methods. Confirm it produces identical output to the original.

## Part 2: Transpilers (40 points)

### 2a: Python Target

Transpile every Mini AST node to Python source. Key mappings:

| Mini | Python |
|---|---|
| `let x = expr;` | `x = expr` |
| `if cond { ... } else { ... }` | `if cond:\n    ...\nelse:\n    ...` |
| `while cond { ... }` | `while cond:\n    ...` |
| `fun(params) { ... }` | `lambda params: (body)` or a `def` if the body has statements |
| `return expr;` | `return expr` |
| `print expr;` | `print(expr)` |
| `f(args)` | `f(args)` |

Indentation: maintain an `indent` counter; increment on entering a block, decrement on leaving.

**Test:** transpile `fib.mini` (the Fibonacci program from your test suite), save the output to `fib.py`, run `python fib.py`, and verify the result matches your interpreter.

### 2b: JavaScript Target

Same structure, different mappings:

| Mini | JavaScript |
|---|---|
| `let x = expr;` | `let x = expr;` |
| `if cond { ... }` | `if (cond) { ... }` |
| `while cond { ... }` | `while (cond) { ... }` |
| `fun(params) { ... }` | `(params) => { ... }` |
| `print expr;` | `console.log(expr);` |
| `true`/`false`/`nil` | `true`/`false`/`null` |

**Test:** transpile `fib.mini` to `fib.js`, run `node fib.js`, verify identical output.

### Operator Precedence Parenthesization

Both transpilers must parenthesize `BinOp` nodes correctly in their target language. The rule: wrap a `BinOp` child in parentheses whenever the child's operator has *lower* precedence than the parent's. A clean implementation uses a precedence table:

```python
PRECEDENCE = {"or": 1, "and": 2, "==": 3, "!=": 3, "<": 4, "<=": 4,
              ">": 4, ">=": 4, "+": 5, "-": 5, "*": 6, "/": 6, "%": 6}
```

Pass the parent's precedence into recursive calls and wrap when needed.

## Part 3: Bytecode Compiler (20 points)

Define an instruction set for a stack machine. Each instruction is a named tuple or dataclass.

| Instruction | Effect |
|---|---|
| `PUSH val` | push literal value |
| `LOAD name` | push value of variable |
| `STORE name` | pop and bind to variable |
| `ADD/SUB/MUL/DIV/MOD` | pop two, push result |
| `EQ/NEQ/LT/LE/GT/GE` | pop two, push boolean |
| `AND/OR/NOT` | logical ops |
| `NEG` | negate top |
| `PRINT` | pop and print |
| `JMP_IF_FALSE label` | pop; jump if falsy |
| `JMP label` | unconditional jump |
| `LABEL label` | anchor for jumps |
| `CALL n` | pop n args and callee, push result |
| `MAKE_FUN params body_instrs` | build closure and push |
| `RETURN` | return top of stack from function |

Compile each AST node to a flat list of these instructions. Use a label counter to generate unique labels for if/while branches.

**Worked example:** `let x = 2 + 3;` compiles to:
```
PUSH 2
PUSH 3
ADD
STORE x
```

And `if cond { A } else { B }` compiles to:
```
(compile cond)
JMP_IF_FALSE else_label
(compile A)
JMP end_label
LABEL else_label
(compile B)
LABEL end_label
```

**Test:** compile your five test programs and print the bytecode listing for one of them (include this listing in your writeup).

## Part 4: The Stack Machine VM (10 points)

```python
# vm.py — skeleton
class VM:
    def __init__(self, instructions):
        self.instructions = instructions
        self.ip    = 0       # instruction pointer
        self.stack = []
        self.env   = {}      # current variable bindings (flat for now)

    def run(self):
        while self.ip < len(self.instructions):
            instr = self.instructions[self.ip]
            self.ip += 1
            self.execute(instr)

    def execute(self, instr):
        name = instr[0]
        if name == "PUSH":   self.stack.append(instr[1])
        elif name == "LOAD": self.stack.append(self.env[instr[1]])
        elif name == "STORE": self.env[instr[1]] = self.stack.pop()
        elif name == "ADD":
            b, a = self.stack.pop(), self.stack.pop()
            self.stack.append(a + b)
        # ... implement the rest ...
        elif name == "JMP_IF_FALSE":
            if not self.stack.pop():
                self.ip = self.label_index(instr[1])
        elif name == "JMP":
            self.ip = self.label_index(instr[1])
        elif name == "LABEL":
            pass  # labels are pre-indexed before run()
        elif name == "PRINT":
            print(self.stack.pop())

    def label_index(self, label):
        for i, instr in enumerate(self.instructions):
            if instr[0] == "LABEL" and instr[1] == label:
                return i
        raise RuntimeError(f"undefined label: {label!r}")
```

Extend `execute` to handle all instructions. For function calls, push a stack frame (saved ip, saved env) onto a call stack.

**Test:** run all five test programs through the VM and confirm they produce the same output as the interpreter.

## Part 5: Test Harness (10 points)

Write `test_all.py` that:
1. For each `.mini` file in a `tests/` directory:
2. Runs the interpreter and captures stdout
3. Transpiles to Python, runs `python output.py`, captures stdout
4. Transpiles to JavaScript, runs `node output.js`, captures stdout
5. Compiles to bytecode, runs the VM, captures stdout
6. Asserts all four outputs are identical; prints PASS or FAIL with the program name

Provide at least eight test programs covering: arithmetic, variable scoping, if/else, while loop, recursive function (Fibonacci), higher-order function (function passed as argument), string operations, list operations.

## Deliverables

Submit a ZIP containing all source files, the `tests/` directory with your `.mini` test programs, `test_all.py` and its output showing all eight tests passing, and a `README.md` (~1.5 pages) that includes:
- The bytecode listing for one test program
- A table comparing the four execution approaches on: correctness, speed (wall-clock time for fib(30)), debuggability, and portability
- One paragraph on each target language: what was easy, what was hard, and one Mini construct you had to handle unexpectedly

## Reflection Prompts

- The visitor pattern dispatches on node type at runtime. Where in your interpreter did you do the same thing without calling it that?
- Your Python and JavaScript outputs are correct — but are they readable? Describe one change you made (or would make) to produce more idiomatic output in one target language.
- The stack machine is slower than the interpreter for short programs. For which kinds of programs might bytecode execution be faster, and why?
- If collaboration with a buddy was permitted, did you work with a buddy on this assignment? If so, who? If not, do you certify that this submission represents your own original work? Please identify any and all portions of your submission that were not originally written by you.
- Approximately how many hours did this assignment take?
