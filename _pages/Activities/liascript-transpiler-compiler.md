# From Interpreter to Compiler: Code Generation and Transpilation

<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://github.com/BillJr99/Ursinus-CS374-Fall2026/blob/main/_pages/Activities/liascript-transpiler-compiler.md

import: https://raw.githubusercontent.com/liascript/CodeRunner/master/README.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

# From Interpreter to Compiler: Code Generation and Transpilation

## Learning Goals

By the end of this activity, you will be able to:

- Explain the architectural difference between a tree-walking interpreter, a transpiler, and a bytecode compiler, and identify which pipeline stages each shares and where they diverge
- Implement a Visitor-pattern AST traversal that emits syntactically correct Python and JavaScript from a Mini-language AST, including correct operator precedence in the output
- Design and implement a stack-machine instruction set for a simple expression language, write a compiler that emits those instructions from an AST, and trace instruction-by-instruction execution through a virtual machine
- Run an end-to-end equivalence test confirming that the interpreter, both transpilers, and the stack machine produce identical output for the same Mini-language program

*"The difference between an interpreter and a compiler is not how smart they are about the language — it is when they do their work."*

Your tree-walking interpreter evaluates an AST **at runtime**: it visits each node and immediately computes a value. A **compiler** walks the same AST but, instead of computing values, **emits instructions** — for a virtual machine, a real CPU, or another programming language. A **transpiler** (source-to-source compiler) emits valid code in a different high-level language. All three share the same frontend (lexer, parser, AST builder); they diverge only in what the AST traversal produces.

In this module we build the complete bridge: starting from the interpreter you have already built, we add a **code generator** that emits Python bytecode (via a virtual stack machine), then a **transpiler** that emits valid JavaScript and valid Haskell. You will be able to run programs in your language by transpiling them — without writing a new frontend.

---

## 0. Setup

```python
# We assume the mini-language interpreter from the course pipeline.
# This module builds on top of the AST defined there.
# Define a minimal AST for illustration:

class Num:
    def __init__(self, value): self.value = value
class BinOp:
    def __init__(self, op, left, right): self.op = op; self.left = left; self.right = right
class Var:
    def __init__(self, name): self.name = name
class Let:
    def __init__(self, name, value, body): self.name = name; self.value = value; self.body = body
class IfExpr:
    def __init__(self, cond, then_, else_): self.cond = cond; self.then_ = then_; self.else_ = else_
class FuncDef:
    def __init__(self, param, body): self.param = param; self.body = body
class Call:
    def __init__(self, func, arg): self.func = func; self.arg = arg

print("AST nodes loaded.")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

---

# Part I: The Visitor Pattern

## 1. Why We Need the Visitor

Your tree-walking interpreter is a set of `if isinstance(node, ...)` branches inside a single `evaluate` function. This works, but as soon as you want to **also** compile, and **also** type-check, and **also** transpile the same AST, you face a choice:

- Add a second `emit_python` function with the same `if isinstance` structure (code duplication)
- Bundle evaluate/emit/typecheck methods inside the AST node classes (breaks separation of concerns)
- Use the **Visitor pattern**: define a `Visitor` interface where each node class calls back into the visitor

The Visitor pattern separates the **what to do** (the visitor) from the **what to visit** (the AST). Adding a new operation (e.g., a type checker, an optimizer, a pretty-printer) requires adding a new visitor class — not modifying the AST.

```python
class Num:
    def __init__(self, value): self.value = value
class BinOp:
    def __init__(self, op, left, right): self.op = op; self.left = left; self.right = right
class Var:
    def __init__(self, name): self.name = name
class Let:
    def __init__(self, name, value, body): self.name = name; self.value = value; self.body = body
class IfExpr:
    def __init__(self, cond, then_, else_): self.cond = cond; self.then_ = then_; self.else_ = else_
class FuncDef:
    def __init__(self, param, body): self.param = param; self.body = body
class Call:
    def __init__(self, func, arg): self.func = func; self.arg = arg

# Visitor base class
class Visitor:
    def visit(self, node):
        method_name = f"visit_{type(node).__name__}"
        method = getattr(self, method_name, self.generic_visit)
        return method(node)

    def generic_visit(self, node):
        raise NotImplementedError(f"No visitor for {type(node).__name__}")

# Interpreter as a Visitor
class Interpreter(Visitor):
    def __init__(self):
        self.env = {}

    def visit_Num(self, node):
        return node.value

    def visit_BinOp(self, node):
        left  = self.visit(node.left)
        right = self.visit(node.right)
        ops   = {'+': lambda a, b: a + b,
                 '-': lambda a, b: a - b,
                 '*': lambda a, b: a * b,
                 '/': lambda a, b: a / b if b != 0 else (_ for _ in ()).throw(ZeroDivisionError("div by zero"))}
        return ops[node.op](left, right)

    def visit_Var(self, node):
        if node.name not in self.env:
            raise NameError(f"[interp] Undefined variable: {node.name}")
        return self.env[node.name]

    def visit_Let(self, node):
        val = self.visit(node.value)
        old_env = dict(self.env)
        self.env[node.name] = val
        result = self.visit(node.body)
        self.env = old_env
        return result

    def visit_IfExpr(self, node):
        cond = self.visit(node.cond)
        return self.visit(node.then_) if cond else self.visit(node.else_)

# Test
interp = Interpreter()
# let x = 3 in x * 2 + 1
ast = Let("x", Num(3), BinOp("+", BinOp("*", Var("x"), Num(2)), Num(1)))
print("Interpreter result:", interp.visit(ast))   # 7
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

---

# Part II: Transpiler to Python

## 2. The Python Transpiler

A transpiler is a visitor that **returns strings** instead of values. Each `visit_*` method returns a Python expression string. The result of visiting the root is a complete Python expression (or program).

```python
class Num:
    def __init__(self, value): self.value = value
class BinOp:
    def __init__(self, op, left, right): self.op = op; self.left = left; self.right = right
class Var:
    def __init__(self, name): self.name = name
class Let:
    def __init__(self, name, value, body): self.name = name; self.value = value; self.body = body
class IfExpr:
    def __init__(self, cond, then_, else_): self.cond = cond; self.then_ = then_; self.else_ = else_
class FuncDef:
    def __init__(self, param, body): self.param = param; self.body = body
class Call:
    def __init__(self, func, arg): self.func = func; self.arg = arg

class Visitor:
    def visit(self, node):
        method_name = f"visit_{type(node).__name__}"
        method = getattr(self, method_name, self.generic_visit)
        return method(node)
    def generic_visit(self, node):
        raise NotImplementedError(f"No visitor for {type(node).__name__}")

ast = Let("x", Num(3), BinOp("+", BinOp("*", Var("x"), Num(2)), Num(1)))

class PythonTranspiler(Visitor):
    """Transpiles our mini-language AST to Python source code."""

    def __init__(self):
        self._indent = 0

    def visit_Num(self, node):
        return str(node.value)

    def visit_BinOp(self, node):
        left  = self.visit(node.left)
        right = self.visit(node.right)
        return f"({left} {node.op} {right})"

    def visit_Var(self, node):
        return node.name

    def visit_Let(self, node):
        # let x = e in body  ->  (lambda x: body)(e)
        val  = self.visit(node.value)
        body = self.visit(node.body)
        return f"(lambda {node.name}: {body})({val})"

    def visit_IfExpr(self, node):
        cond  = self.visit(node.cond)
        then_ = self.visit(node.then_)
        else_ = self.visit(node.else_)
        return f"({then_} if {cond} else {else_})"

    def visit_FuncDef(self, node):
        body = self.visit(node.body)
        return f"(lambda {node.param}: {body})"

    def visit_Call(self, node):
        func = self.visit(node.func)
        arg  = self.visit(node.arg)
        return f"{func}({arg})"

# Transpile and execute
py_trans = PythonTranspiler()
py_code  = py_trans.visit(ast)
print("Python code:", py_code)
result   = eval(py_code)
print("Evaluated: ", result)   # should be 7
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

---

## 3. The JavaScript Transpiler

The same AST, same visitor structure, different target language:

```python
class Num:
    def __init__(self, value): self.value = value
class BinOp:
    def __init__(self, op, left, right): self.op = op; self.left = left; self.right = right
class Var:
    def __init__(self, name): self.name = name
class Let:
    def __init__(self, name, value, body): self.name = name; self.value = value; self.body = body
class IfExpr:
    def __init__(self, cond, then_, else_): self.cond = cond; self.then_ = then_; self.else_ = else_
class FuncDef:
    def __init__(self, param, body): self.param = param; self.body = body
class Call:
    def __init__(self, func, arg): self.func = func; self.arg = arg

class Visitor:
    def visit(self, node):
        method_name = f"visit_{type(node).__name__}"
        method = getattr(self, method_name, self.generic_visit)
        return method(node)
    def generic_visit(self, node):
        raise NotImplementedError(f"No visitor for {type(node).__name__}")

ast = Let("x", Num(3), BinOp("+", BinOp("*", Var("x"), Num(2)), Num(1)))

class JavaScriptTranspiler(Visitor):
    """Transpiles our mini-language AST to JavaScript source code."""

    def visit_Num(self, node):
        return str(node.value)

    def visit_BinOp(self, node):
        left  = self.visit(node.left)
        right = self.visit(node.right)
        # JS division is floating point; add Math.trunc for integer div if needed
        if node.op == '/':
            return f"Math.trunc({left} / {right})"
        return f"({left} {node.op} {right})"

    def visit_Var(self, node):
        return node.name

    def visit_Let(self, node):
        # let x = e in body  ->  ((x) => body)(e)
        val  = self.visit(node.value)
        body = self.visit(node.body)
        return f"(({node.name}) => {body})({val})"

    def visit_IfExpr(self, node):
        cond  = self.visit(node.cond)
        then_ = self.visit(node.then_)
        else_ = self.visit(node.else_)
        return f"({cond} ? {then_} : {else_})"

    def visit_FuncDef(self, node):
        body = self.visit(node.body)
        return f"(({node.param}) => {body})"

    def visit_Call(self, node):
        func = self.visit(node.func)
        arg  = self.visit(node.arg)
        return f"{func}({arg})"

js_trans = JavaScriptTranspiler()
js_code  = js_trans.visit(ast)
print("JavaScript code:", js_code)
# Output: ((x) => ((x * 2) + 1))(3)
# Paste into browser console to verify: returns 7
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

---

## 4. The Haskell Transpiler

Haskell uses `let ... in ...` naturally for our `Let` node, and lambda syntax for `FuncDef`. The transpiler produces valid Haskell expressions:

```python
class Num:
    def __init__(self, value): self.value = value
class BinOp:
    def __init__(self, op, left, right): self.op = op; self.left = left; self.right = right
class Var:
    def __init__(self, name): self.name = name
class Let:
    def __init__(self, name, value, body): self.name = name; self.value = value; self.body = body
class IfExpr:
    def __init__(self, cond, then_, else_): self.cond = cond; self.then_ = then_; self.else_ = else_
class FuncDef:
    def __init__(self, param, body): self.param = param; self.body = body
class Call:
    def __init__(self, func, arg): self.func = func; self.arg = arg

class Visitor:
    def visit(self, node):
        method_name = f"visit_{type(node).__name__}"
        method = getattr(self, method_name, self.generic_visit)
        return method(node)
    def generic_visit(self, node):
        raise NotImplementedError(f"No visitor for {type(node).__name__}")

ast = Let("x", Num(3), BinOp("+", BinOp("*", Var("x"), Num(2)), Num(1)))

class HaskellTranspiler(Visitor):
    """Transpiles our mini-language AST to Haskell expressions."""

    def visit_Num(self, node):
        return str(node.value)

    def visit_BinOp(self, node):
        left  = self.visit(node.left)
        right = self.visit(node.right)
        if node.op == '/':
            return f"(div {left} {right})"    # integer division in Haskell
        return f"({left} {node.op} {right})"

    def visit_Var(self, node):
        return node.name

    def visit_Let(self, node):
        val  = self.visit(node.value)
        body = self.visit(node.body)
        return f"(let {node.name} = {val} in {body})"

    def visit_IfExpr(self, node):
        cond  = self.visit(node.cond)
        then_ = self.visit(node.then_)
        else_ = self.visit(node.else_)
        return f"(if {cond} then {then_} else {else_})"

    def visit_FuncDef(self, node):
        body = self.visit(node.body)
        return f"(\\{node.param} -> {body})"

    def visit_Call(self, node):
        func = self.visit(node.func)
        arg  = self.visit(node.arg)
        return f"({func} {arg})"

hs_trans = HaskellTranspiler()
hs_code  = hs_trans.visit(ast)
print("Haskell expression:", hs_code)
# Output: (let x = 3 in ((x * 2) + 1))
# Load in GHCi to verify: returns 7
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

---

[[MC]]
A transpiler differs from an interpreter in which fundamental way?

- (x) A transpiler emits code in a target language rather than executing the program; both traverse the same AST but produce different output from each node.
- ( ) A transpiler performs type-checking at compile time while an interpreter does not.
- ( ) A transpiler uses a bottom-up (LR) parser while an interpreter uses a top-down (LL) parser.
- ( ) A transpiler is always faster to execute than an interpreter because it generates native code.

---

# Part III: Stack Machine / Bytecode Compiler

## 5. Compiling to a Virtual Stack Machine

Real compilers (Python, Java, Lua) compile to a **bytecode** for a virtual stack machine. The stack machine has a simple instruction set:

| Instruction | Effect |
|---|---|
| `PUSH n` | Push constant `n` onto stack |
| `LOAD x` | Push value of variable `x` |
| `STORE x` | Pop and store in variable `x` |
| `ADD` / `SUB` / `MUL` / `DIV` | Pop two values, push result |
| `JMP_IF_FALSE label` | Pop; if 0/False, jump to label |
| `JMP label` | Unconditional jump |
| `LABEL label` | Mark this position |
| `CALL n` | Call top-of-stack function with n args |
| `RETURN` | Return top of stack |

Compilation is a visitor that emits a list of these instructions:

```python
class Num:
    def __init__(self, value): self.value = value
class BinOp:
    def __init__(self, op, left, right): self.op = op; self.left = left; self.right = right
class Var:
    def __init__(self, name): self.name = name
class Let:
    def __init__(self, name, value, body): self.name = name; self.value = value; self.body = body
class IfExpr:
    def __init__(self, cond, then_, else_): self.cond = cond; self.then_ = then_; self.else_ = else_

class Visitor:
    def visit(self, node):
        method_name = f"visit_{type(node).__name__}"
        method = getattr(self, method_name, self.generic_visit)
        return method(node)
    def generic_visit(self, node):
        raise NotImplementedError(f"No visitor for {type(node).__name__}")

ast = Let("x", Num(3), BinOp("+", BinOp("*", Var("x"), Num(2)), Num(1)))

class Bytecode:
    def __init__(self, op, *args):
        self.op   = op
        self.args = args

    def __repr__(self):
        return f"{self.op} {' '.join(str(a) for a in self.args)}".strip()

class BytecodeCompiler(Visitor):
    def __init__(self):
        self.instructions = []
        self._label_count = 0

    def fresh_label(self, prefix="L"):
        self._label_count += 1
        return f"{prefix}{self._label_count}"

    def emit(self, op, *args):
        self.instructions.append(Bytecode(op, *args))

    def visit_Num(self, node):
        self.emit("PUSH", node.value)

    def visit_Var(self, node):
        self.emit("LOAD", node.name)

    def visit_BinOp(self, node):
        self.visit(node.left)    # push left
        self.visit(node.right)   # push right
        ops = {'+': 'ADD', '-': 'SUB', '*': 'MUL', '/': 'DIV'}
        self.emit(ops[node.op])  # pop two, push result

    def visit_Let(self, node):
        self.visit(node.value)         # push value
        self.emit("STORE", node.name)  # store in variable
        self.visit(node.body)          # compile body (value is now on stack)

    def visit_IfExpr(self, node):
        else_lbl = self.fresh_label("ELSE")
        end_lbl  = self.fresh_label("END")
        self.visit(node.cond)
        self.emit("JMP_IF_FALSE", else_lbl)
        self.visit(node.then_)
        self.emit("JMP", end_lbl)
        self.emit("LABEL", else_lbl)
        self.visit(node.else_)
        self.emit("LABEL", end_lbl)

# Compile the example AST
compiler = BytecodeCompiler()
compiler.visit(ast)

print("Bytecode for: let x = 3 in x * 2 + 1")
for i, instr in enumerate(compiler.instructions):
    print(f"  {i:3d}  {instr}")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

---

## 6. Executing the Bytecode (Virtual Machine)

The bytecode interpreter is now much simpler than the tree-walking interpreter: it is a loop over a flat instruction list with a stack:

```python
class Num:
    def __init__(self, value): self.value = value
class BinOp:
    def __init__(self, op, left, right): self.op = op; self.left = left; self.right = right
class Var:
    def __init__(self, name): self.name = name
class Let:
    def __init__(self, name, value, body): self.name = name; self.value = value; self.body = body
class IfExpr:
    def __init__(self, cond, then_, else_): self.cond = cond; self.then_ = then_; self.else_ = else_

class Visitor:
    def visit(self, node):
        method_name = f"visit_{type(node).__name__}"
        method = getattr(self, method_name, self.generic_visit)
        return method(node)
    def generic_visit(self, node):
        raise NotImplementedError(f"No visitor for {type(node).__name__}")

class Bytecode:
    def __init__(self, op, *args):
        self.op   = op
        self.args = args
    def __repr__(self):
        return f"{self.op} {' '.join(str(a) for a in self.args)}".strip()

class BytecodeCompiler(Visitor):
    def __init__(self):
        self.instructions = []
        self._label_count = 0
    def fresh_label(self, prefix="L"):
        self._label_count += 1
        return f"{prefix}{self._label_count}"
    def emit(self, op, *args):
        self.instructions.append(Bytecode(op, *args))
    def visit_Num(self, node):
        self.emit("PUSH", node.value)
    def visit_Var(self, node):
        self.emit("LOAD", node.name)
    def visit_BinOp(self, node):
        self.visit(node.left)
        self.visit(node.right)
        ops = {'+': 'ADD', '-': 'SUB', '*': 'MUL', '/': 'DIV'}
        self.emit(ops[node.op])
    def visit_Let(self, node):
        self.visit(node.value)
        self.emit("STORE", node.name)
        self.visit(node.body)
    def visit_IfExpr(self, node):
        else_lbl = self.fresh_label("ELSE")
        end_lbl  = self.fresh_label("END")
        self.visit(node.cond)
        self.emit("JMP_IF_FALSE", else_lbl)
        self.visit(node.then_)
        self.emit("JMP", end_lbl)
        self.emit("LABEL", else_lbl)
        self.visit(node.else_)
        self.emit("LABEL", end_lbl)

ast = Let("x", Num(3), BinOp("+", BinOp("*", Var("x"), Num(2)), Num(1)))
compiler = BytecodeCompiler()
compiler.visit(ast)

class StackMachine:
    def __init__(self, instructions):
        self.instructions = instructions
        self.stack        = []
        self.env          = {}
        # Build label map
        self.labels = {
            instr.args[0]: i
            for i, instr in enumerate(instructions)
            if instr.op == "LABEL"
        }

    def run(self):
        pc = 0
        while pc < len(self.instructions):
            instr = self.instructions[pc]
            op    = instr.op

            if op == "PUSH":
                self.stack.append(instr.args[0])
            elif op == "LOAD":
                self.stack.append(self.env[instr.args[0]])
            elif op == "STORE":
                self.env[instr.args[0]] = self.stack.pop()
            elif op in ("ADD", "SUB", "MUL", "DIV"):
                b, a = self.stack.pop(), self.stack.pop()
                result = {'ADD': a+b, 'SUB': a-b, 'MUL': a*b, 'DIV': a//b}[op]
                self.stack.append(result)
            elif op == "JMP_IF_FALSE":
                if not self.stack.pop():
                    pc = self.labels[instr.args[0]]
                    continue
            elif op == "JMP":
                pc = self.labels[instr.args[0]]
                continue
            elif op == "LABEL":
                pass   # no-op at runtime
            pc += 1

        return self.stack[-1] if self.stack else None

vm = StackMachine(compiler.instructions)
result = vm.run()
print("VM result:", result)   # 7
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

---

# Part IV: Source Maps and Debugging

## 7. Source Maps: Connecting Output Back to Input

A **source map** connects positions in the generated code back to positions in the source. This is why browser developer tools can show you a TypeScript error on the TypeScript line, even though the browser runs JavaScript. For our bytecode, a source map is a list of `(instruction_index, source_line)` pairs.

```python
class Num:
    def __init__(self, value): self.value = value
class BinOp:
    def __init__(self, op, left, right): self.op = op; self.left = left; self.right = right
class Var:
    def __init__(self, name): self.name = name
class Let:
    def __init__(self, name, value, body): self.name = name; self.value = value; self.body = body
class IfExpr:
    def __init__(self, cond, then_, else_): self.cond = cond; self.then_ = then_; self.else_ = else_

class Visitor:
    def visit(self, node):
        method_name = f"visit_{type(node).__name__}"
        method = getattr(self, method_name, self.generic_visit)
        return method(node)
    def generic_visit(self, node):
        raise NotImplementedError(f"No visitor for {type(node).__name__}")

class Bytecode:
    def __init__(self, op, *args):
        self.op   = op
        self.args = args
    def __repr__(self):
        return f"{self.op} {' '.join(str(a) for a in self.args)}".strip()

class BytecodeCompiler(Visitor):
    def __init__(self):
        self.instructions = []
        self._label_count = 0
    def fresh_label(self, prefix="L"):
        self._label_count += 1
        return f"{prefix}{self._label_count}"
    def emit(self, op, *args):
        self.instructions.append(Bytecode(op, *args))
    def visit_Num(self, node):
        self.emit("PUSH", node.value)
    def visit_Var(self, node):
        self.emit("LOAD", node.name)
    def visit_BinOp(self, node):
        self.visit(node.left)
        self.visit(node.right)
        ops = {'+': 'ADD', '-': 'SUB', '*': 'MUL', '/': 'DIV'}
        self.emit(ops[node.op])
    def visit_Let(self, node):
        self.visit(node.value)
        self.emit("STORE", node.name)
        self.visit(node.body)
    def visit_IfExpr(self, node):
        else_lbl = self.fresh_label("ELSE")
        end_lbl  = self.fresh_label("END")
        self.visit(node.cond)
        self.emit("JMP_IF_FALSE", else_lbl)
        self.visit(node.then_)
        self.emit("JMP", end_lbl)
        self.emit("LABEL", else_lbl)
        self.visit(node.else_)
        self.emit("LABEL", end_lbl)

ast = Let("x", Num(3), BinOp("+", BinOp("*", Var("x"), Num(2)), Num(1)))

class TracingCompiler(BytecodeCompiler):
    """Extends BytecodeCompiler to emit source map entries."""

    def __init__(self):
        super().__init__()
        self.source_map = []   # (instruction_index, node_type)

    def emit(self, op, *args):
        self.source_map.append((len(self.instructions), op))
        super().emit(op, *args)

    def visit_BinOp(self, node):
        start_pc = len(self.instructions)
        super().visit_BinOp(node)
        end_pc = len(self.instructions)
        print(f"  BinOp '{node.op}' -> instructions {start_pc}..{end_pc-1}")

tc = TracingCompiler()
tc.visit(ast)
print("\nSource map excerpt (instruction index -> operation):")
for idx, op in tc.source_map[:8]:
    print(f"  {idx}: {op}")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

---

# Part V: Exercises

## 8. Exercises

1. **Extend the transpilers.** Add support for `FuncDef` and `Call` nodes to all three transpilers (Python, JavaScript, Haskell). Test with the AST for `(lambda x: x * x)(5)` — i.e., `Call(FuncDef("x", BinOp("*", Var("x"), Var("x"))), Num(5))`. All three transpilers should produce expressions that evaluate to 25 in their respective languages.

2. **Boolean support.** Add `Bool(value)` and `And(left, right)` / `Or(left, right)` nodes to the AST. Extend all three transpilers and the bytecode compiler. Python uses `and`/`or`; JavaScript uses `&&`/`||`; Haskell uses `&&`/`||`. Test with `And(Bool(True), Bool(False))`.

3. **Bytecode optimizer: constant folding.** Write a `ConstantFolder` visitor that transforms `BinOp("+", Num(2), Num(3))` into `Num(5)` before compilation. This is the simplest compiler optimization: evaluating constant expressions at compile time. Apply it to the AST before compiling to bytecode and verify that the bytecode is shorter.

4. **Transpile your own mini-language.** Take the parser you built for the mini-language assignment and add a `PythonTranspiler` backend. The transpiler should translate your language's programs into valid Python. Test by parsing a factorial program in your language and transpiling + executing it in Python. Include one program that demonstrates your language's most distinctive feature.

5. **Reflection: when to interpret, when to compile, when to transpile.** Write a one-page analysis of three real language implementation decisions: (a) why CPython compiles to `.pyc` bytecode rather than interpreting the source AST directly; (b) why TypeScript transpiles to JavaScript rather than compiling to machine code; (c) why HHVM (Facebook's PHP runtime) JIT-compiles rather than interpreting. In each case, state the tradeoff and who benefits.

---

## 9. Further Reading

- Nystrom, Robert. *Crafting Interpreters* (available free online). Part III covers bytecode compilation with a full stack machine (Clox); the code in this module is a simplified version of that approach.
- Thain, Douglas. *Introduction to Compilers and Language Design*. Chapters 8–10 cover intermediate representations, code generation, and optimization in depth.
- Gamma, Erich et al. *Design Patterns* (Addison-Wesley, 1995). Chapter on the Visitor pattern — the pattern that makes the transpiler architecture here work cleanly.
- Cooper, Keith and Linda Torczon. *Engineering a Compiler* (2nd ed., Morgan Kaufmann, 2011). The most complete modern treatment of code generation, register allocation, and optimization.
- Pereira, Fernando and Jens Palsberg. "Register Allocation After Classical SSA Elimination is NP-Complete." *FoSSaCS*, 2005. A glimpse at why real compilers are hard, even after you have a correct code generator.
