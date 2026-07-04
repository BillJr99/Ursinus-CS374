# Tutorial: Building a Bytecode VM for Mini

<!--
author:   CS374 Course Staff
email:    
version:  0.0.1
language: en
narrator: US English Female

comment: Build a stack-based bytecode VM for Mini — the same architecture used by CPython, the JVM, and Lua. Render with https://liascript.github.io/course/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374-Fall2026/gh-pages/_pages/Tutorials/tutorial-bytecode-vm.md

import: https://raw.githubusercontent.com/liascript/CodeRunner/master/README.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

# Tutorial: Building a Bytecode VM for Mini

## Learning Goals

By the end of this tutorial, you will have:

- Defined a Mini instruction set architecture (`Opcode` enum and `Instruction` dataclass) and explained why a flat instruction list is more cache-friendly than an AST
- Implemented a compiler that walks the Mini AST and emits bytecode instructions with a constant pool and jump backpatching
- Implemented a stack-based VM dispatch loop that executes bytecode using a value stack and a call stack of frames
- Implemented upvalues (the Lua trick) so that closures in the VM correctly capture variables from enclosing frames
- Verified that the VM produces identical output to the tree-walking interpreter on all provided test programs and measured the speedup

Your tree-walking interpreter is correct and elegant — but every time it evaluates `x + 1` it traverses three AST nodes, looks up `x` in the environment dictionary, allocates a new addition result, and works its way back up. For programs with tight loops or deeply recursive functions, this overhead adds up. **Bytecode virtual machines** solve this by translating the AST once into a flat sequence of simple instructions, then running those instructions in a tight loop. This is the architecture behind CPython, the Java Virtual Machine, Lua, Ruby's YARV, and dozens of other production runtimes.

This tutorial builds a complete bytecode VM for Mini in six phases:

1. **Phase 0** — Why bytecode? Comparison of execution strategies
2. **Phase 1** — Instruction Set Architecture: the `Opcode` enum and `Instruction` dataclass
3. **Phase 2** — The Compiler: walking the AST and emitting bytecode
4. **Phase 3** — The VM: the dispatch loop, value stack, and call stack
5. **Phase 4** — Functions and closures: upvalues (the Lua trick)
6. **Phase 5** — Integration, disassembler, and performance comparison

**Prerequisites:** the Mini interpreter assignment, the Closures activity, and the Environments lecture. You do not need to understand the JVM or CPython internals — we build everything from scratch.

---

## Phase 0: Why Bytecode?

### Three Ways to Execute a Program

When you have a parsed AST, you have three main options for executing it:

| Strategy | How it works | Startup cost | Runtime speed | Portability |
|---|---|---|---|---|
| **Tree-walking interpreter** | Recursively evaluate AST nodes | None | Slow (pointer-chasing, branching per node) | Portable (runs on any host with the interpreter) |
| **Bytecode VM** | Compile AST → flat instruction list; run in a dispatch loop | Small (compile once) | Medium (tight loop, cache-friendly) | Portable (bytecode is platform-independent) |
| **Native compiler** | Compile AST → machine code | Large (codegen, linking) | Fast (no interpretation overhead) | Not portable (x86 vs ARM vs RISC-V) |

Bytecode VMs hit the sweet spot: they are much faster than tree-walkers in practice (2–10×) and require far less effort to implement than a native compiler.

### Real-World Bytecode VMs

Every major dynamic language uses a bytecode VM:

- **CPython** — Python's reference implementation; compiles `.py` to `.pyc` bytecode for the CPython VM
- **JVM** — Java, Kotlin, Scala, Clojure all compile to `.class` files (JVM bytecode)
- **Lua 5.x** — direct AST-to-bytecode compiler; used in game engines and embedded systems
- **Ruby's YARV** — Yet Another Ruby VM, introduced in Ruby 1.9
- **V8 (JavaScript)** — starts with bytecode (Ignition), then JIT-compiles hot paths (TurboFan)

### Peeking at CPython's Bytecode

Python exposes its compiler through the `dis` module. Try this in any Python 3.10+ environment:

```python
try:
    import dis

    def add(a, b):
        return a + b

    dis.dis(add)
    print()

    def fib(n):
        if n <= 1:
            return n
        return fib(n - 1) + fib(n - 2)

    dis.dis(fib)
except Exception as e:
    print(f"Error: {e}")
```

You will see instructions like `LOAD_FAST`, `BINARY_OP`, `RETURN_VALUE`. These map almost directly to what we will build. The key observation: **each instruction is just a small integer (the opcode) plus an optional integer operand**. No tree traversal needed at runtime.

### The Core Insight: Separation of Compilation and Execution

```
Source code
    │
    ▼
  Lexer  ──► Token stream
    │
    ▼
  Parser ──► AST (tree structure)
    │
    ▼
 Compiler ──► Bytecode (flat list of instructions)   ← compile once
    │
    ▼
    VM     ──► Result                                ← run many times
```

The compiler runs once. The VM runs the same bytecode repeatedly — or, in the case of a REPL, compiles each expression and immediately runs it. The bytecode can also be serialized to disk (like `.pyc` files) so that compilation cost is paid only when the source changes.

---

## Phase 1: Instruction Set Architecture

### Opcodes

An **opcode** (operation code) is an integer that names one VM operation. We use Python's `enum.IntEnum` so opcodes can be stored compactly and printed by name.

```python
try:
    from enum import IntEnum, auto

    class Opcode(IntEnum):
        # ── Stack manipulation ────────────────────────────────────
        PUSH_INT   = auto()   # push integer constant (operand = value)
        PUSH_FLOAT = auto()   # push float constant
        PUSH_STR   = auto()   # push string constant
        PUSH_BOOL  = auto()   # push True/False (operand = 0 or 1)
        PUSH_NIL   = auto()   # push None
        POP        = auto()   # discard top of stack
        DUP        = auto()   # duplicate top of stack
        SWAP       = auto()   # swap top two stack values

        # ── Arithmetic ────────────────────────────────────────────
        ADD  = auto()
        SUB  = auto()
        MUL  = auto()
        DIV  = auto()
        MOD  = auto()
        NEG  = auto()   # unary negation
        POW  = auto()

        # ── Comparison (push bool result) ─────────────────────────
        EQ   = auto()
        NEQ  = auto()
        LT   = auto()
        LE   = auto()
        GT   = auto()
        GE   = auto()

        # ── Logic ─────────────────────────────────────────────────
        AND  = auto()   # non-short-circuit bitwise AND (short-circuit via jumps)
        OR   = auto()   # non-short-circuit bitwise OR
        NOT  = auto()

        # ── Variable access ───────────────────────────────────────
        LOAD_NAME   = auto()   # operand = name string; push globals[name]
        STORE_NAME  = auto()   # operand = name string; globals[name] = pop()
        LOAD_LOCAL  = auto()   # operand = slot index; push locals[slot]
        STORE_LOCAL = auto()   # operand = slot index; locals[slot] = pop()

        # ── Control flow ──────────────────────────────────────────
        JUMP          = auto()   # unconditional; operand = target index
        JUMP_IF_FALSE = auto()   # pop; jump if falsy
        JUMP_IF_TRUE  = auto()   # pop; jump if truthy

        # ── Functions ─────────────────────────────────────────────
        MAKE_FUNCTION  = auto()  # wrap a Chunk into a Function object
        MAKE_CLOSURE   = auto()  # like MAKE_FUNCTION but also captures upvalues
        CALL           = auto()  # operand = arg count; pops args + function
        RETURN         = auto()  # pop return value, restore caller frame

        # ── Built-ins ─────────────────────────────────────────────
        PRINT        = auto()    # pop and print
        LOAD_BUILTIN = auto()    # operand = builtin name

    print("Opcodes defined:", len(Opcode), "instructions")
    for op in list(Opcode)[:6]:
        print(f"  {op.name:20s} = {op.value}")
    print("  ...")
except Exception as e:
    print(f"Error: {e}")
```

### Instructions and Chunks

An `Instruction` pairs an opcode with an optional operand. A `Chunk` is the compiled output for one function (or the top-level program): a list of instructions, a constant pool, and a name table.

```python
try:
    from dataclasses import dataclass, field
    from typing import Any, List, Optional

    @dataclass
    class Instruction:
        opcode:  int        # one of the Opcode enum values
        operand: Any = None # integer offset, constant value, or name string

        def __repr__(self):
            if self.operand is None:
                return f"{self.opcode}"
            return f"{self.opcode}({self.operand!r})"

    @dataclass
    class Chunk:
        """Compiled bytecode for one function or the top-level program."""
        name:         str               = "<module>"
        instructions: List[Instruction] = field(default_factory=list)
        # constants and names are embedded directly in operands for simplicity;
        # a production VM would use separate constant/name pools for space savings.

        def emit(self, opcode: int, operand: Any = None) -> int:
            """Append one instruction; return its index."""
            idx = len(self.instructions)
            self.instructions.append(Instruction(opcode, operand))
            return idx

        def patch(self, idx: int, operand: Any):
            """Overwrite the operand of instruction at idx (for forward jumps)."""
            self.instructions[idx].operand = operand

        def __len__(self):
            return len(self.instructions)

    # Smoke test
    chunk = Chunk("test")
    chunk.emit(1, 42)   # PUSH_INT 42  (opcode value 1)
    chunk.emit(1, 58)   # PUSH_INT 58
    chunk.emit(9)       # ADD
    print("Chunk has", len(chunk), "instructions")
    for i, instr in enumerate(chunk.instructions):
        print(f"  {i:3d}  {instr}")
except Exception as e:
    print(f"Error: {e}")
```

### Hand-Compiled Example: `1 + 2 * 3`

Before writing the compiler, let us hand-compile an expression to see what the output looks like. Mini follows standard arithmetic precedence (`*` before `+`), so `1 + 2 * 3` parses as `1 + (2 * 3)`.

```
;; Expression: 1 + 2 * 3
;; Parsed as:  Add(Num(1), Mul(Num(2), Num(3)))
;;
;; Stack grows to the right; top is rightmost.

PUSH_INT 1       ; stack: [1]
PUSH_INT 2       ; stack: [1, 2]
PUSH_INT 3       ; stack: [1, 2, 3]
MUL              ; pop 3,2; push 6     stack: [1, 6]
ADD              ; pop 6,1; push 7     stack: [7]

;; Final result: 7 (sits on top of stack)
```

This flat sequence is what the VM actually executes — no tree traversal, no recursion, just a loop over a list of integers.

---

## Phase 2: The Compiler (AST → Bytecode)

The compiler walks the AST exactly once and emits instructions in **post-order**: compile the operands first, then emit the operator. This naturally produces the right stack layout.

### AST Node Definitions

We define a minimal AST for the Mini language. If you already have your parser's AST classes, you would use those instead.

```python
try:
    from dataclasses import dataclass
    from typing import Any, List, Optional

    # ── Literal values ────────────────────────────────────────────
    @dataclass
    class Num:
        value: float

    @dataclass
    class Bool:
        value: bool

    @dataclass
    class Str:
        value: str

    @dataclass
    class Nil:
        pass

    # ── Variables ─────────────────────────────────────────────────
    @dataclass
    class Name:
        name: str

    @dataclass
    class Assign:
        name: str
        value: Any  # expression

    # ── Arithmetic / logic ────────────────────────────────────────
    @dataclass
    class BinOp:
        op:    str   # "+", "-", "*", "/", "%", "**",
                     # "==", "!=", "<", "<=", ">", ">=",
                     # "and", "or"
        left:  Any
        right: Any

    @dataclass
    class UnaryOp:
        op:    str   # "-", "not"
        operand: Any

    # ── Control flow ──────────────────────────────────────────────
    @dataclass
    class If:
        condition: Any
        then_body: List[Any]   # list of statements
        else_body: List[Any]

    @dataclass
    class While:
        condition: Any
        body: List[Any]

    @dataclass
    class Return:
        value: Any

    # ── Functions ─────────────────────────────────────────────────
    @dataclass
    class FunDecl:
        name:   str
        params: List[str]
        body:   List[Any]

    @dataclass
    class Call:
        callee: Any
        args:   List[Any]

    # ── Statements ────────────────────────────────────────────────
    @dataclass
    class Print:
        value: Any

    @dataclass
    class Block:
        stmts: List[Any]

    print("AST node types defined.")
except Exception as e:
    print(f"Error: {e}")
```

### The Compiler Class

```python
try:
    from dataclasses import dataclass, field
    from typing import Any, List, Dict, Optional
    from enum import IntEnum, auto

    # ── Re-define Opcode (standalone cell) ────────────────────────
    class Opcode(IntEnum):
        PUSH_INT=1; PUSH_FLOAT=2; PUSH_STR=3; PUSH_BOOL=4; PUSH_NIL=5
        POP=6; DUP=7; SWAP=8
        ADD=9; SUB=10; MUL=11; DIV=12; MOD=13; NEG=14; POW=15
        EQ=16; NEQ=17; LT=18; LE=19; GT=20; GE=21
        AND=22; OR=23; NOT=24
        LOAD_NAME=25; STORE_NAME=26; LOAD_LOCAL=27; STORE_LOCAL=28
        JUMP=29; JUMP_IF_FALSE=30; JUMP_IF_TRUE=31
        MAKE_FUNCTION=32; MAKE_CLOSURE=33; CALL=34; RETURN=35
        PRINT=36; LOAD_BUILTIN=37

    @dataclass
    class Instruction:
        opcode: int
        operand: Any = None
        def __repr__(self):
            return f"{Opcode(self.opcode).name}({self.operand!r})" if self.operand is not None else f"{Opcode(self.opcode).name}"

    @dataclass
    class Chunk:
        name: str = "<module>"
        instructions: List[Instruction] = field(default_factory=list)
        def emit(self, opcode: int, operand: Any = None) -> int:
            idx = len(self.instructions)
            self.instructions.append(Instruction(opcode, operand))
            return idx
        def patch(self, idx: int, operand: Any):
            self.instructions[idx].operand = operand
        def __len__(self): return len(self.instructions)

    # ── Minimal AST (re-define for standalone cell) ───────────────
    @dataclass
    class Num: value: float
    @dataclass
    class Bool: value: bool
    @dataclass
    class Str: value: str
    @dataclass
    class Nil: pass
    @dataclass
    class Name: name: str
    @dataclass
    class Assign: name: str; value: Any
    @dataclass
    class BinOp: op: str; left: Any; right: Any
    @dataclass
    class UnaryOp: op: str; operand: Any
    @dataclass
    class If: condition: Any; then_body: List[Any]; else_body: List[Any]
    @dataclass
    class While: condition: Any; body: List[Any]
    @dataclass
    class Return: value: Any
    @dataclass
    class FunDecl: name: str; params: List[str]; body: List[Any]
    @dataclass
    class Call: callee: Any; args: List[Any]
    @dataclass
    class Print: value: Any
    @dataclass
    class Block: stmts: List[Any]

    # ── Compiler ──────────────────────────────────────────────────
    _BINOP_OPCODES = {
        "+": Opcode.ADD, "-": Opcode.SUB, "*": Opcode.MUL,
        "/": Opcode.DIV, "%": Opcode.MOD, "**": Opcode.POW,
        "==": Opcode.EQ, "!=": Opcode.NEQ,
        "<":  Opcode.LT, "<=": Opcode.LE,
        ">":  Opcode.GT, ">=": Opcode.GE,
    }

    class Compiler:
        def __init__(self, name: str = "<module>"):
            self.chunk = Chunk(name)

        def compile_stmts(self, stmts: List[Any]):
            for stmt in stmts:
                self.compile(stmt)

        def compile(self, node: Any):
            """Compile one AST node, leaving its value on the stack (for expressions)
            or not (for statements that use POP or STORE_NAME)."""
            match node:
                # ── Literals ──────────────────────────────────────
                case Num(value=v) if isinstance(v, int):
                    self.chunk.emit(Opcode.PUSH_INT, v)
                case Num(value=v):
                    self.chunk.emit(Opcode.PUSH_FLOAT, v)
                case Bool(value=v):
                    self.chunk.emit(Opcode.PUSH_BOOL, int(v))
                case Str(value=v):
                    self.chunk.emit(Opcode.PUSH_STR, v)
                case Nil():
                    self.chunk.emit(Opcode.PUSH_NIL)

                # ── Variable read ──────────────────────────────────
                case Name(name=n):
                    self.chunk.emit(Opcode.LOAD_NAME, n)

                # ── Assignment ────────────────────────────────────
                case Assign(name=n, value=v):
                    self.compile(v)
                    self.chunk.emit(Opcode.STORE_NAME, n)

                # ── Binary operations ─────────────────────────────
                case BinOp(op="and", left=l, right=r):
                    # Short-circuit: if left is falsy, skip right
                    self.compile(l)
                    self.chunk.emit(Opcode.DUP)         # keep left on stack for result
                    jump_idx = self.chunk.emit(Opcode.JUMP_IF_FALSE, 0)  # placeholder
                    self.chunk.emit(Opcode.POP)          # discard left; use right as result
                    self.compile(r)
                    self.chunk.patch(jump_idx, len(self.chunk))

                case BinOp(op="or", left=l, right=r):
                    # Short-circuit: if left is truthy, skip right
                    self.compile(l)
                    self.chunk.emit(Opcode.DUP)
                    jump_idx = self.chunk.emit(Opcode.JUMP_IF_TRUE, 0)  # placeholder
                    self.chunk.emit(Opcode.POP)
                    self.compile(r)
                    self.chunk.patch(jump_idx, len(self.chunk))

                case BinOp(op=op, left=l, right=r):
                    self.compile(l)
                    self.compile(r)
                    self.chunk.emit(_BINOP_OPCODES[op])

                # ── Unary operations ──────────────────────────────
                case UnaryOp(op="-", operand=e):
                    self.compile(e)
                    self.chunk.emit(Opcode.NEG)
                case UnaryOp(op="not", operand=e):
                    self.compile(e)
                    self.chunk.emit(Opcode.NOT)

                # ── If / else ─────────────────────────────────────
                case If(condition=cond, then_body=then_b, else_body=else_b):
                    self.compile(cond)
                    # Jump over then-branch if condition is false
                    jump_false = self.chunk.emit(Opcode.JUMP_IF_FALSE, 0)
                    self.compile_stmts(then_b)
                    # Jump over else-branch after then-branch
                    jump_end = self.chunk.emit(Opcode.JUMP, 0)
                    # Patch the JUMP_IF_FALSE to land here (start of else)
                    self.chunk.patch(jump_false, len(self.chunk))
                    self.compile_stmts(else_b)
                    # Patch the end-jump to land here (after else)
                    self.chunk.patch(jump_end, len(self.chunk))

                # ── While loop ────────────────────────────────────
                case While(condition=cond, body=body):
                    loop_start = len(self.chunk)
                    self.compile(cond)
                    exit_jump = self.chunk.emit(Opcode.JUMP_IF_FALSE, 0)
                    self.compile_stmts(body)
                    self.chunk.emit(Opcode.JUMP, loop_start)   # back-edge
                    self.chunk.patch(exit_jump, len(self.chunk))

                # ── Function declaration ──────────────────────────
                case FunDecl(name=name, params=params, body=body):
                    inner = Compiler(name)
                    # Compile params as STORE_LOCAL into the new chunk
                    for i, p in enumerate(reversed(params)):
                        inner.chunk.emit(Opcode.STORE_LOCAL, p)
                    inner.compile_stmts(body)
                    # Implicit return None if no explicit return
                    inner.chunk.emit(Opcode.PUSH_NIL)
                    inner.chunk.emit(Opcode.RETURN)
                    self.chunk.emit(Opcode.MAKE_FUNCTION, inner.chunk)
                    self.chunk.emit(Opcode.STORE_NAME, name)

                # ── Function call ─────────────────────────────────
                case Call(callee=callee, args=args):
                    self.compile(callee)
                    for a in args:
                        self.compile(a)
                    self.chunk.emit(Opcode.CALL, len(args))

                # ── Return ────────────────────────────────────────
                case Return(value=v):
                    self.compile(v)
                    self.chunk.emit(Opcode.RETURN)

                # ── Print statement ───────────────────────────────
                case Print(value=v):
                    self.compile(v)
                    self.chunk.emit(Opcode.PRINT)

                # ── Block ─────────────────────────────────────────
                case Block(stmts=stmts):
                    self.compile_stmts(stmts)

                case _:
                    raise NotImplementedError(f"Compiler: unknown node {node!r}")

    # ── Demo: compile  if x > 0 { print(x); } ──────────────────
    prog = [
        Assign("x", Num(5)),
        If(
            condition=BinOp(">", Name("x"), Num(0)),
            then_body=[Print(Name("x"))],
            else_body=[]
        )
    ]

    c = Compiler()
    c.compile_stmts(prog)

    print("Bytecode for: x = 5; if x > 0 { print(x); }")
    print()
    for i, instr in enumerate(c.chunk.instructions):
        print(f"  {i:3d}  {instr}")
except Exception as e:
    import traceback; traceback.print_exc()
```

### The Patch-Back Technique for Forward Jumps

Compiling `if` and `while` requires **forward jumps** — jumps to an address that we do not know yet when we emit the jump instruction. The solution is the **patch-back** technique:

1. Emit `JUMP_IF_FALSE 0` (placeholder operand `0`)
2. Compile the then-branch
3. Now we know the target address: `len(chunk)` (the next instruction to be emitted)
4. Overwrite the placeholder with the real address: `chunk.patch(jump_idx, len(chunk))`

This is the same technique used in production compilers. In the code above, `compile(If(...))` uses `jump_false` and `jump_end` as the patch-back indices.

---

## Phase 3: The VM (Execute Bytecode)

### Call Frames

Each function call gets its own **call frame** — a record of the currently-executing chunk, the instruction pointer within that chunk, and the local variables for that call.

```python
try:
    from dataclasses import dataclass, field
    from typing import Any, List, Dict, Optional
    from enum import IntEnum, auto

    class Opcode(IntEnum):
        PUSH_INT=1; PUSH_FLOAT=2; PUSH_STR=3; PUSH_BOOL=4; PUSH_NIL=5
        POP=6; DUP=7; SWAP=8
        ADD=9; SUB=10; MUL=11; DIV=12; MOD=13; NEG=14; POW=15
        EQ=16; NEQ=17; LT=18; LE=19; GT=20; GE=21
        AND=22; OR=23; NOT=24
        LOAD_NAME=25; STORE_NAME=26; LOAD_LOCAL=27; STORE_LOCAL=28
        JUMP=29; JUMP_IF_FALSE=30; JUMP_IF_TRUE=31
        MAKE_FUNCTION=32; MAKE_CLOSURE=33; CALL=34; RETURN=35
        PRINT=36; LOAD_BUILTIN=37

    @dataclass
    class Instruction:
        opcode: int
        operand: Any = None

    @dataclass
    class Chunk:
        name: str = "<module>"
        instructions: List[Instruction] = field(default_factory=list)
        def emit(self, opcode, operand=None):
            idx = len(self.instructions)
            self.instructions.append(Instruction(opcode, operand))
            return idx
        def patch(self, idx, operand):
            self.instructions[idx].operand = operand
        def __len__(self): return len(self.instructions)

    @dataclass
    class CallFrame:
        chunk:  Any        # the Chunk being executed
        ip:     int = 0    # instruction pointer (index into chunk.instructions)
        locals: Dict[str, Any] = field(default_factory=dict)

        def read(self) -> Optional[Instruction]:
            """Fetch the current instruction and advance ip."""
            if self.ip >= len(self.chunk.instructions):
                return None
            instr = self.chunk.instructions[self.ip]
            self.ip += 1
            return instr

    # ── Function object (defined here, used by VM) ────────────────
    @dataclass
    class Function:
        name:   str
        params: List[str]
        chunk:  Any   # Chunk

        def __repr__(self):
            return f"<function {self.name}/{len(self.params)}>"

    print("CallFrame and Function defined.")
    # Quick smoke test
    chunk = Chunk("test")
    frame = CallFrame(chunk)
    print("Empty frame ip:", frame.ip)
except Exception as e:
    import traceback; traceback.print_exc()
```

### The VM Dispatch Loop

The VM's heart is a `while True` loop that fetches one instruction, dispatches on its opcode, and updates the stack. This is the same structure as CPython's `ceval.c` (though that one is in C and has a few thousand lines of optimizations).

```python
try:
    from dataclasses import dataclass, field
    from typing import Any, List, Dict, Optional
    from enum import IntEnum

    class Opcode(IntEnum):
        PUSH_INT=1; PUSH_FLOAT=2; PUSH_STR=3; PUSH_BOOL=4; PUSH_NIL=5
        POP=6; DUP=7; SWAP=8
        ADD=9; SUB=10; MUL=11; DIV=12; MOD=13; NEG=14; POW=15
        EQ=16; NEQ=17; LT=18; LE=19; GT=20; GE=21
        AND=22; OR=23; NOT=24
        LOAD_NAME=25; STORE_NAME=26; LOAD_LOCAL=27; STORE_LOCAL=28
        JUMP=29; JUMP_IF_FALSE=30; JUMP_IF_TRUE=31
        MAKE_FUNCTION=32; MAKE_CLOSURE=33; CALL=34; RETURN=35
        PRINT=36; LOAD_BUILTIN=37

    @dataclass
    class Instruction:
        opcode: int; operand: Any = None

    @dataclass
    class Chunk:
        name: str = "<module>"
        instructions: List[Instruction] = field(default_factory=list)
        def emit(self, op, operand=None):
            idx = len(self.instructions)
            self.instructions.append(Instruction(op, operand))
            return idx
        def patch(self, idx, v): self.instructions[idx].operand = v
        def __len__(self): return len(self.instructions)

    @dataclass
    class CallFrame:
        chunk: Any; ip: int = 0
        locals: Dict[str, Any] = field(default_factory=dict)
        def read(self):
            if self.ip >= len(self.chunk.instructions): return None
            instr = self.chunk.instructions[self.ip]; self.ip += 1; return instr

    @dataclass
    class Function:
        name: str; params: List[str]; chunk: Any
        def __repr__(self): return f"<function {self.name}/{len(self.params)}>"

    class VMError(RuntimeError): pass

    class VM:
        def __init__(self):
            self.stack:   List[Any]       = []
            self.frames:  List[CallFrame] = []
            self.globals: Dict[str, Any]  = {}

        # ── Stack helpers ──────────────────────────────────────────
        def push(self, v: Any):  self.stack.append(v)
        def pop(self)  -> Any:   return self.stack.pop()
        def peek(self) -> Any:   return self.stack[-1]

        # ── Entry point ────────────────────────────────────────────
        def run(self, chunk: Chunk) -> Any:
            frame = CallFrame(chunk)
            self.frames.append(frame)
            result = self._execute()
            self.frames.pop()
            return result

        # ── Main dispatch loop ─────────────────────────────────────
        def _execute(self) -> Any:
            while True:
                frame = self.frames[-1]
                instr = frame.read()
                if instr is None:
                    return self.pop() if self.stack else None

                op = Opcode(instr.opcode)

                # ── Push literals ──────────────────────────────────
                if   op == Opcode.PUSH_INT:   self.push(instr.operand)
                elif op == Opcode.PUSH_FLOAT: self.push(instr.operand)
                elif op == Opcode.PUSH_STR:   self.push(instr.operand)
                elif op == Opcode.PUSH_BOOL:  self.push(bool(instr.operand))
                elif op == Opcode.PUSH_NIL:   self.push(None)

                # ── Stack manipulation ─────────────────────────────
                elif op == Opcode.POP:
                    self.pop()
                elif op == Opcode.DUP:
                    self.push(self.peek())
                elif op == Opcode.SWAP:
                    a = self.pop(); b = self.pop()
                    self.push(a); self.push(b)

                # ── Arithmetic ─────────────────────────────────────
                elif op == Opcode.ADD:
                    r = self.pop(); l = self.pop(); self.push(l + r)
                elif op == Opcode.SUB:
                    r = self.pop(); l = self.pop(); self.push(l - r)
                elif op == Opcode.MUL:
                    r = self.pop(); l = self.pop(); self.push(l * r)
                elif op == Opcode.DIV:
                    r = self.pop(); l = self.pop()
                    if r == 0: raise VMError("Division by zero")
                    self.push(l / r)
                elif op == Opcode.MOD:
                    r = self.pop(); l = self.pop(); self.push(l % r)
                elif op == Opcode.POW:
                    r = self.pop(); l = self.pop(); self.push(l ** r)
                elif op == Opcode.NEG:
                    self.push(-self.pop())

                # ── Comparisons ────────────────────────────────────
                elif op == Opcode.EQ:
                    r = self.pop(); l = self.pop(); self.push(l == r)
                elif op == Opcode.NEQ:
                    r = self.pop(); l = self.pop(); self.push(l != r)
                elif op == Opcode.LT:
                    r = self.pop(); l = self.pop(); self.push(l <  r)
                elif op == Opcode.LE:
                    r = self.pop(); l = self.pop(); self.push(l <= r)
                elif op == Opcode.GT:
                    r = self.pop(); l = self.pop(); self.push(l >  r)
                elif op == Opcode.GE:
                    r = self.pop(); l = self.pop(); self.push(l >= r)

                # ── Logic ──────────────────────────────────────────
                elif op == Opcode.NOT:
                    self.push(not self.pop())
                elif op == Opcode.AND:
                    r = self.pop(); l = self.pop(); self.push(l and r)
                elif op == Opcode.OR:
                    r = self.pop(); l = self.pop(); self.push(l or r)

                # ── Variable access ────────────────────────────────
                elif op == Opcode.LOAD_NAME:
                    name = instr.operand
                    if name in frame.locals:   self.push(frame.locals[name])
                    elif name in self.globals: self.push(self.globals[name])
                    else: raise VMError(f"Undefined variable: {name!r}")
                elif op == Opcode.STORE_NAME:
                    name = instr.operand
                    v = self.pop()
                    frame.locals[name] = v
                    self.globals[name] = v  # also store globally for top-level
                elif op == Opcode.LOAD_LOCAL:
                    self.push(frame.locals[instr.operand])
                elif op == Opcode.STORE_LOCAL:
                    frame.locals[instr.operand] = self.pop()

                # ── Control flow ───────────────────────────────────
                elif op == Opcode.JUMP:
                    frame.ip = instr.operand
                elif op == Opcode.JUMP_IF_FALSE:
                    if not self.pop():
                        frame.ip = instr.operand
                elif op == Opcode.JUMP_IF_TRUE:
                    if self.pop():
                        frame.ip = instr.operand

                # ── Functions ──────────────────────────────────────
                elif op == Opcode.MAKE_FUNCTION:
                    inner_chunk = instr.operand
                    fn = Function(inner_chunk.name, [], inner_chunk)
                    self.push(fn)
                elif op == Opcode.CALL:
                    arg_count = instr.operand
                    args = [self.pop() for _ in range(arg_count)]
                    args.reverse()
                    fn = self.pop()
                    if not isinstance(fn, Function):
                        raise VMError(f"Called non-function: {fn!r}")
                    new_frame = CallFrame(fn.chunk)
                    # Bind arguments as locals
                    for i, (param, val) in enumerate(zip(fn.params, args)):
                        new_frame.locals[param] = val
                    # Also handle positional binds from STORE_LOCAL in the chunk
                    self.frames.append(new_frame)
                elif op == Opcode.RETURN:
                    ret_val = self.pop()
                    self.frames.pop()
                    self.push(ret_val)
                    if len(self.frames) == 0:
                        return ret_val

                # ── Built-ins ──────────────────────────────────────
                elif op == Opcode.PRINT:
                    print(self.pop())

                else:
                    raise VMError(f"Unknown opcode: {op}")

    # ── Demo: trace execution of 2 * (3 + 4) ──────────────────────
    print("Tracing: 2 * (3 + 4)")
    print()
    print("  Instruction        Stack after")
    print("  ─────────────────  ──────────────────")

    steps = [
        (Opcode.PUSH_INT, 2,  "[2]"),
        (Opcode.PUSH_INT, 3,  "[2, 3]"),
        (Opcode.PUSH_INT, 4,  "[2, 3, 4]"),
        (Opcode.ADD,      None,"[2, 7]"),
        (Opcode.MUL,      None,"[14]"),
    ]
    for op, operand, stack_after in steps:
        name = op.name
        operand_str = f" {operand}" if operand is not None else ""
        print(f"  {name+operand_str:<20s} {stack_after}")

    # Actually run it
    chunk = Chunk("demo")
    chunk.emit(Opcode.PUSH_INT, 2)
    chunk.emit(Opcode.PUSH_INT, 3)
    chunk.emit(Opcode.PUSH_INT, 4)
    chunk.emit(Opcode.ADD)
    chunk.emit(Opcode.MUL)

    vm = VM()
    result = vm.run(chunk)
    print()
    print(f"Result: {result}")   # should be 14
except Exception as e:
    import traceback; traceback.print_exc()
```

### Running the Compiler Output Through the VM

Now we can connect the compiler from Phase 2 to the VM:

```python
try:
    from dataclasses import dataclass, field
    from typing import Any, List, Dict, Optional
    from enum import IntEnum

    # ── (all definitions from Phase 2 and Phase 3 combined) ───────
    class Opcode(IntEnum):
        PUSH_INT=1; PUSH_FLOAT=2; PUSH_STR=3; PUSH_BOOL=4; PUSH_NIL=5
        POP=6; DUP=7; SWAP=8
        ADD=9; SUB=10; MUL=11; DIV=12; MOD=13; NEG=14; POW=15
        EQ=16; NEQ=17; LT=18; LE=19; GT=20; GE=21
        AND=22; OR=23; NOT=24
        LOAD_NAME=25; STORE_NAME=26; LOAD_LOCAL=27; STORE_LOCAL=28
        JUMP=29; JUMP_IF_FALSE=30; JUMP_IF_TRUE=31
        MAKE_FUNCTION=32; MAKE_CLOSURE=33; CALL=34; RETURN=35
        PRINT=36; LOAD_BUILTIN=37

    @dataclass
    class Instruction:
        opcode: int; operand: Any = None
        def __repr__(self):
            name = Opcode(self.opcode).name
            return f"{name}({self.operand!r})" if self.operand is not None else name

    @dataclass
    class Chunk:
        name: str = "<module>"
        instructions: List[Instruction] = field(default_factory=list)
        def emit(self, op, operand=None):
            idx = len(self.instructions); self.instructions.append(Instruction(op, operand)); return idx
        def patch(self, idx, v): self.instructions[idx].operand = v
        def __len__(self): return len(self.instructions)

    @dataclass
    class Num: value: float
    @dataclass
    class Bool: value: bool
    @dataclass
    class Str: value: str
    @dataclass
    class Nil: pass
    @dataclass
    class Name: name: str
    @dataclass
    class Assign: name: str; value: Any
    @dataclass
    class BinOp: op: str; left: Any; right: Any
    @dataclass
    class UnaryOp: op: str; operand: Any
    @dataclass
    class If: condition: Any; then_body: List[Any]; else_body: List[Any]
    @dataclass
    class While: condition: Any; body: List[Any]
    @dataclass
    class Return: value: Any
    @dataclass
    class FunDecl: name: str; params: List[str]; body: List[Any]
    @dataclass
    class Call: callee: Any; args: List[Any]
    @dataclass
    class Print: value: Any
    @dataclass
    class Block: stmts: List[Any]

    _BINOP_OPCODES = {
        "+": Opcode.ADD, "-": Opcode.SUB, "*": Opcode.MUL,
        "/": Opcode.DIV, "%": Opcode.MOD, "**": Opcode.POW,
        "==": Opcode.EQ, "!=": Opcode.NEQ,
        "<":  Opcode.LT, "<=": Opcode.LE, ">":  Opcode.GT, ">=": Opcode.GE,
    }

    class Compiler:
        def __init__(self, name="<module>"):
            self.chunk = Chunk(name)
        def compile_stmts(self, stmts):
            for s in stmts: self.compile(s)
        def compile(self, node):
            match node:
                case Num(value=v) if isinstance(v, int): self.chunk.emit(Opcode.PUSH_INT, v)
                case Num(value=v): self.chunk.emit(Opcode.PUSH_FLOAT, v)
                case Bool(value=v): self.chunk.emit(Opcode.PUSH_BOOL, int(v))
                case Str(value=v): self.chunk.emit(Opcode.PUSH_STR, v)
                case Nil(): self.chunk.emit(Opcode.PUSH_NIL)
                case Name(name=n): self.chunk.emit(Opcode.LOAD_NAME, n)
                case Assign(name=n, value=v): self.compile(v); self.chunk.emit(Opcode.STORE_NAME, n)
                case BinOp(op="and", left=l, right=r):
                    self.compile(l); self.chunk.emit(Opcode.DUP)
                    j = self.chunk.emit(Opcode.JUMP_IF_FALSE, 0); self.chunk.emit(Opcode.POP)
                    self.compile(r); self.chunk.patch(j, len(self.chunk))
                case BinOp(op="or", left=l, right=r):
                    self.compile(l); self.chunk.emit(Opcode.DUP)
                    j = self.chunk.emit(Opcode.JUMP_IF_TRUE, 0); self.chunk.emit(Opcode.POP)
                    self.compile(r); self.chunk.patch(j, len(self.chunk))
                case BinOp(op=op, left=l, right=r):
                    self.compile(l); self.compile(r); self.chunk.emit(_BINOP_OPCODES[op])
                case UnaryOp(op="-", operand=e): self.compile(e); self.chunk.emit(Opcode.NEG)
                case UnaryOp(op="not", operand=e): self.compile(e); self.chunk.emit(Opcode.NOT)
                case If(condition=c, then_body=t, else_body=e):
                    self.compile(c); jf = self.chunk.emit(Opcode.JUMP_IF_FALSE, 0)
                    self.compile_stmts(t); je = self.chunk.emit(Opcode.JUMP, 0)
                    self.chunk.patch(jf, len(self.chunk)); self.compile_stmts(e)
                    self.chunk.patch(je, len(self.chunk))
                case While(condition=c, body=b):
                    start = len(self.chunk); self.compile(c)
                    ex = self.chunk.emit(Opcode.JUMP_IF_FALSE, 0)
                    self.compile_stmts(b); self.chunk.emit(Opcode.JUMP, start)
                    self.chunk.patch(ex, len(self.chunk))
                case FunDecl(name=n, params=params, body=body):
                    inner = Compiler(n)
                    for p in reversed(params): inner.chunk.emit(Opcode.STORE_LOCAL, p)
                    inner.compile_stmts(body)
                    inner.chunk.emit(Opcode.PUSH_NIL); inner.chunk.emit(Opcode.RETURN)
                    self.chunk.emit(Opcode.MAKE_FUNCTION, inner.chunk)
                    self.chunk.emit(Opcode.STORE_NAME, n)
                case Call(callee=cal, args=args):
                    self.compile(cal)
                    for a in args: self.compile(a)
                    self.chunk.emit(Opcode.CALL, len(args))
                case Return(value=v): self.compile(v); self.chunk.emit(Opcode.RETURN)
                case Print(value=v): self.compile(v); self.chunk.emit(Opcode.PRINT)
                case Block(stmts=ss): self.compile_stmts(ss)
                case _: raise NotImplementedError(f"Unknown node: {node!r}")

    @dataclass
    class CallFrame:
        chunk: Any; ip: int = 0
        locals: Dict[str, Any] = field(default_factory=dict)
        def read(self):
            if self.ip >= len(self.chunk.instructions): return None
            instr = self.chunk.instructions[self.ip]; self.ip += 1; return instr

    @dataclass
    class Function:
        name: str; params: List[str]; chunk: Any
        def __repr__(self): return f"<function {self.name}/{len(self.params)}>"

    class VMError(RuntimeError): pass

    class VM:
        def __init__(self):
            self.stack = []; self.frames = []; self.globals = {}
        def push(self, v): self.stack.append(v)
        def pop(self): return self.stack.pop()
        def peek(self): return self.stack[-1]
        def run(self, chunk):
            frame = CallFrame(chunk); self.frames.append(frame)
            result = self._execute(); return result
        def _execute(self):
            while True:
                if not self.frames: return self.pop() if self.stack else None
                frame = self.frames[-1]; instr = frame.read()
                if instr is None:
                    self.frames.pop(); continue
                op = Opcode(instr.opcode)
                if   op == Opcode.PUSH_INT:   self.push(instr.operand)
                elif op == Opcode.PUSH_FLOAT: self.push(instr.operand)
                elif op == Opcode.PUSH_STR:   self.push(instr.operand)
                elif op == Opcode.PUSH_BOOL:  self.push(bool(instr.operand))
                elif op == Opcode.PUSH_NIL:   self.push(None)
                elif op == Opcode.POP:        self.pop()
                elif op == Opcode.DUP:        self.push(self.peek())
                elif op == Opcode.SWAP:
                    a = self.pop(); b = self.pop(); self.push(a); self.push(b)
                elif op == Opcode.ADD:  r=self.pop(); l=self.pop(); self.push(l+r)
                elif op == Opcode.SUB:  r=self.pop(); l=self.pop(); self.push(l-r)
                elif op == Opcode.MUL:  r=self.pop(); l=self.pop(); self.push(l*r)
                elif op == Opcode.DIV:
                    r=self.pop(); l=self.pop()
                    if r == 0: raise VMError("Division by zero")
                    self.push(l/r)
                elif op == Opcode.MOD:  r=self.pop(); l=self.pop(); self.push(l%r)
                elif op == Opcode.POW:  r=self.pop(); l=self.pop(); self.push(l**r)
                elif op == Opcode.NEG:  self.push(-self.pop())
                elif op == Opcode.EQ:   r=self.pop(); l=self.pop(); self.push(l==r)
                elif op == Opcode.NEQ:  r=self.pop(); l=self.pop(); self.push(l!=r)
                elif op == Opcode.LT:   r=self.pop(); l=self.pop(); self.push(l<r)
                elif op == Opcode.LE:   r=self.pop(); l=self.pop(); self.push(l<=r)
                elif op == Opcode.GT:   r=self.pop(); l=self.pop(); self.push(l>r)
                elif op == Opcode.GE:   r=self.pop(); l=self.pop(); self.push(l>=r)
                elif op == Opcode.NOT:  self.push(not self.pop())
                elif op == Opcode.AND:  r=self.pop(); l=self.pop(); self.push(l and r)
                elif op == Opcode.OR:   r=self.pop(); l=self.pop(); self.push(l or r)
                elif op == Opcode.LOAD_NAME:
                    n = instr.operand
                    if n in frame.locals: self.push(frame.locals[n])
                    elif n in self.globals: self.push(self.globals[n])
                    else: raise VMError(f"Undefined: {n!r}")
                elif op == Opcode.STORE_NAME:
                    v = self.pop(); frame.locals[instr.operand] = v; self.globals[instr.operand] = v
                elif op == Opcode.LOAD_LOCAL:  self.push(frame.locals[instr.operand])
                elif op == Opcode.STORE_LOCAL: frame.locals[instr.operand] = self.pop()
                elif op == Opcode.JUMP:          frame.ip = instr.operand
                elif op == Opcode.JUMP_IF_FALSE:
                    if not self.pop(): frame.ip = instr.operand
                elif op == Opcode.JUMP_IF_TRUE:
                    if self.pop(): frame.ip = instr.operand
                elif op == Opcode.MAKE_FUNCTION:
                    fn = Function(instr.operand.name, [], instr.operand); self.push(fn)
                elif op == Opcode.CALL:
                    n_args = instr.operand
                    args = [self.pop() for _ in range(n_args)]; args.reverse()
                    fn = self.pop()
                    if not isinstance(fn, Function): raise VMError(f"Not callable: {fn!r}")
                    new_frame = CallFrame(fn.chunk)
                    for p, v in zip(fn.params, args): new_frame.locals[p] = v
                    self.frames.append(new_frame)
                elif op == Opcode.RETURN:
                    ret = self.pop(); self.frames.pop(); self.push(ret)
                elif op == Opcode.PRINT: print(self.pop())
                else: raise VMError(f"Unknown opcode {op}")

    # ── End-to-end test: while loop summing 1..5 ──────────────────
    prog = [
        Assign("sum", Num(0)),
        Assign("i",   Num(1)),
        While(
            condition=BinOp("<=", Name("i"), Num(5)),
            body=[
                Assign("sum", BinOp("+", Name("sum"), Name("i"))),
                Assign("i",   BinOp("+", Name("i"),   Num(1))),
            ]
        ),
        Print(Name("sum")),
    ]

    c = Compiler(); c.compile_stmts(prog)
    vm = VM(); vm.run(c.chunk)   # should print 15
except Exception as e:
    import traceback; traceback.print_exc()
```

---

## Phase 4: Functions and Closures

### Why Closures Are Tricky for VMs

In a tree-walking interpreter, closures are easy: a `Closure` object holds a reference to the environment at the time of creation, and lookups walk the environment chain. In a bytecode VM, variables live on the stack inside call frames — when a function returns, its frame is gone. A closure that was created inside that function would be left with a dangling reference.

The **upvalue** pattern (invented for Lua 5.x by Roberto Ierusalimschy) solves this elegantly.

### The Upvalue Pattern

An **upvalue** is an indirect reference to a captured variable. It has two states:

1. **Open** — the captured variable is still on the stack (the enclosing function is running). The upvalue holds a reference into the live stack frame.
2. **Closed** — the enclosing function has returned. The upvalue now holds the final value itself (it was "closed over").

```python
try:
    from dataclasses import dataclass, field
    from typing import Any, List, Dict, Optional
    from enum import IntEnum

    class Opcode(IntEnum):
        PUSH_INT=1; PUSH_FLOAT=2; PUSH_STR=3; PUSH_BOOL=4; PUSH_NIL=5
        POP=6; DUP=7; SWAP=8
        ADD=9; SUB=10; MUL=11; DIV=12; MOD=13; NEG=14; POW=15
        EQ=16; NEQ=17; LT=18; LE=19; GT=20; GE=21
        AND=22; OR=23; NOT=24
        LOAD_NAME=25; STORE_NAME=26; LOAD_LOCAL=27; STORE_LOCAL=28
        JUMP=29; JUMP_IF_FALSE=30; JUMP_IF_TRUE=31
        MAKE_FUNCTION=32; MAKE_CLOSURE=33; CALL=34; RETURN=35
        PRINT=36; LOAD_BUILTIN=37
        LOAD_UPVALUE=38; STORE_UPVALUE=39

    @dataclass
    class Upvalue:
        """
        Indirect reference to a captured variable.

        While the enclosing call frame is alive, `cell` is a one-element
        list shared with the frame's local slot — both the frame and the
        upvalue write/read through the same list, so mutations are visible.

        When the enclosing frame is popped (function returns), `close()`
        is called: the value is copied into the upvalue itself and the
        shared list is detached. Future reads go to `self.closed_value`.
        """
        cell: List[Any]   # [value] — shared with enclosing frame while open
        is_open: bool = True

        @property
        def value(self) -> Any:
            return self.cell[0]

        @value.setter
        def value(self, v: Any):
            self.cell[0] = v

        def close(self):
            """Detach from the stack frame; save the current value."""
            saved = self.cell[0]
            self.cell = [saved]   # replace with a fresh independent list
            self.is_open = False

        def __repr__(self):
            state = "open" if self.is_open else "closed"
            return f"Upvalue({self.cell[0]!r}, {state})"

    @dataclass
    class Function:
        name:     str
        params:   List[str]
        chunk:    Any
        upvalues: List[Upvalue] = field(default_factory=list)
        def __repr__(self): return f"<function {self.name}/{len(self.params)}>"

    # ── Demonstrate upvalue closing ────────────────────────────────
    # Simulate: the enclosing frame has a local variable `count = 0`
    shared_cell = [0]               # the "slot" in the enclosing frame

    uv = Upvalue(cell=shared_cell)
    print(f"Initially:           {uv}")   # open, value=0

    shared_cell[0] = 7              # enclosing frame updates the variable
    print(f"After frame writes 7: {uv}")  # still open, value=7

    uv.close()                      # enclosing function returns
    shared_cell[0] = 99             # frame is gone; this would be a dangling write
    print(f"After close():        {uv}")  # closed, still value=7 (captured correctly)
    print(f"Reading upvalue:      {uv.value}")
except Exception as e:
    import traceback; traceback.print_exc()
```

### Closure Factory: Counter Example

The classic test for closures is a **counter factory** — a function that returns another function, where the inner function mutates a variable from the enclosing scope.

```python
try:
    from dataclasses import dataclass, field
    from typing import Any, List, Dict, Optional
    from enum import IntEnum

    # ── Simplified closure-aware VM ────────────────────────────────
    # We model closures using Python's own closures for clarity.
    # In a real VM, you would use the Upvalue mechanism from above.

    class Opcode(IntEnum):
        PUSH_INT=1; PUSH_FLOAT=2; PUSH_STR=3; PUSH_BOOL=4; PUSH_NIL=5
        POP=6; DUP=7; SWAP=8
        ADD=9; SUB=10; MUL=11; DIV=12; MOD=13; NEG=14; POW=15
        EQ=16; NEQ=17; LT=18; LE=19; GT=20; GE=21
        AND=22; OR=23; NOT=24
        LOAD_NAME=25; STORE_NAME=26; LOAD_LOCAL=27; STORE_LOCAL=28
        JUMP=29; JUMP_IF_FALSE=30; JUMP_IF_TRUE=31
        MAKE_FUNCTION=32; MAKE_CLOSURE=33; CALL=34; RETURN=35
        PRINT=36; LOAD_BUILTIN=37

    @dataclass
    class Instruction:
        opcode: int; operand: Any = None

    @dataclass
    class Chunk:
        name: str = "<module>"
        instructions: List[Instruction] = field(default_factory=list)
        def emit(self, op, operand=None):
            idx = len(self.instructions); self.instructions.append(Instruction(op, operand)); return idx
        def patch(self, idx, v): self.instructions[idx].operand = v
        def __len__(self): return len(self.instructions)

    # For the closure demo, we use a Python-level callable that wraps state.
    # This is exactly what a VM's closure object does — hold the captured upvalues.
    class MiniClosure:
        def __init__(self, name, fn):
            self._fn = fn
        def __call__(self, *args):
            return self._fn(*args)
        def __repr__(self):
            return f"<closure {self._fn.__name__}>"

    # Simulate compiling and running:
    #
    #   fun make_counter() {
    #       let count = 0;
    #       fun inc() {
    #           count = count + 1;
    #           return count;
    #       }
    #       return inc;
    #   }
    #
    #   let counter = make_counter();
    #   print(counter());   # 1
    #   print(counter());   # 2
    #   print(counter());   # 3

    def make_counter_vm():
        """Simulate what the VM does when executing make_counter()."""
        # The upvalue cell: a shared mutable container
        count_cell = [0]

        def inc():
            count_cell[0] += 1   # mutates the shared cell
            return count_cell[0]

        return MiniClosure("inc", inc)

    counter = make_counter_vm()
    print("counter():", counter())   # 1
    print("counter():", counter())   # 2
    print("counter():", counter())   # 3

    # Two independent counters share nothing
    c1 = make_counter_vm()
    c2 = make_counter_vm()
    print()
    print("c1:", c1(), c1())   # 1 2
    print("c2:", c2())         # 1  (independent)
    print("c1:", c1())         # 3  (unaffected by c2)
except Exception as e:
    import traceback; traceback.print_exc()
```

### What `MAKE_CLOSURE` Does Differently from `MAKE_FUNCTION`

| `MAKE_FUNCTION` | `MAKE_CLOSURE` |
|---|---|
| Wraps a `Chunk` into a `Function` | Same, but also captures upvalues |
| No captured state | Holds a list of `Upvalue` objects |
| Used for top-level functions | Used for nested functions and lambdas |
| Operand: the inner `Chunk` | Operand: `(inner Chunk, upvalue_descriptors)` |

In Lua's VM, `CLOSURE` is a single instruction that creates a closure object and immediately reads the following `UPVALUE` or `GETUPVAL` pseudo-instructions to populate the upvalue list. CPython uses a different approach: it pre-compiles which variables are "cell variables" (captured by inner functions) vs "free variables" (captured from outer functions) and generates `MAKE_CELL`, `COPY_FREE_VARS` instructions.

---

## Phase 5: Integration and Testing

### The Disassembler

A disassembler pretty-prints the bytecode of a `Chunk` with line numbers and formatted operands. It is invaluable for debugging the compiler.

```python
try:
    from dataclasses import dataclass, field
    from typing import Any, List, Dict, Optional
    from enum import IntEnum

    class Opcode(IntEnum):
        PUSH_INT=1; PUSH_FLOAT=2; PUSH_STR=3; PUSH_BOOL=4; PUSH_NIL=5
        POP=6; DUP=7; SWAP=8
        ADD=9; SUB=10; MUL=11; DIV=12; MOD=13; NEG=14; POW=15
        EQ=16; NEQ=17; LT=18; LE=19; GT=20; GE=21
        AND=22; OR=23; NOT=24
        LOAD_NAME=25; STORE_NAME=26; LOAD_LOCAL=27; STORE_LOCAL=28
        JUMP=29; JUMP_IF_FALSE=30; JUMP_IF_TRUE=31
        MAKE_FUNCTION=32; MAKE_CLOSURE=33; CALL=34; RETURN=35
        PRINT=36; LOAD_BUILTIN=37

    @dataclass
    class Instruction:
        opcode: int; operand: Any = None

    @dataclass
    class Chunk:
        name: str = "<module>"
        instructions: List[Instruction] = field(default_factory=list)
        def emit(self, op, operand=None):
            idx = len(self.instructions); self.instructions.append(Instruction(op, operand)); return idx
        def patch(self, idx, v): self.instructions[idx].operand = v
        def __len__(self): return len(self.instructions)

    def disassemble(chunk: Chunk, indent: int = 0):
        """Pretty-print bytecode. Recursively disassembles nested chunks."""
        prefix = "  " * indent
        print(f"{prefix}=== {chunk.name} ===")
        for i, instr in enumerate(chunk.instructions):
            try:
                op = Opcode(instr.opcode)
                op_name = op.name
            except ValueError:
                op_name = f"UNKNOWN({instr.opcode})"

            # Format the operand
            if instr.operand is None:
                operand_str = ""
            elif isinstance(instr.operand, Chunk):
                operand_str = f"<chunk:{instr.operand.name}>"
            elif isinstance(instr.operand, str):
                operand_str = f"{instr.operand!r}"
            else:
                operand_str = str(instr.operand)

            print(f"{prefix}  {i:4d}  {op_name:<20s} {operand_str}")

            # Recurse into nested chunks (functions)
            if isinstance(instr.operand, Chunk):
                disassemble(instr.operand, indent + 2)

    # ── Build the fib chunk by hand ────────────────────────────────
    #
    # fun fib(n) {
    #   if n <= 1 { return n; }
    #   return fib(n-1) + fib(n-2);
    # }
    #
    # Bytecode for fib (body only; n is in locals["n"]):

    fib_chunk = Chunk("fib")

    # Prologue: bind parameter n from stack
    fib_chunk.emit(Opcode.STORE_LOCAL, "n")

    # if n <= 1
    fib_chunk.emit(Opcode.LOAD_LOCAL,  "n")
    fib_chunk.emit(Opcode.PUSH_INT,    1)
    fib_chunk.emit(Opcode.LE)
    jump_false = fib_chunk.emit(Opcode.JUMP_IF_FALSE, 0)   # placeholder

    # then: return n
    fib_chunk.emit(Opcode.LOAD_LOCAL, "n")
    fib_chunk.emit(Opcode.RETURN)

    # patch the JUMP_IF_FALSE to land here
    fib_chunk.patch(jump_false, len(fib_chunk))

    # return fib(n-1) + fib(n-2)
    # -- fib(n-1) --
    fib_chunk.emit(Opcode.LOAD_NAME,  "fib")
    fib_chunk.emit(Opcode.LOAD_LOCAL, "n")
    fib_chunk.emit(Opcode.PUSH_INT,   1)
    fib_chunk.emit(Opcode.SUB)
    fib_chunk.emit(Opcode.CALL, 1)

    # -- fib(n-2) --
    fib_chunk.emit(Opcode.LOAD_NAME,  "fib")
    fib_chunk.emit(Opcode.LOAD_LOCAL, "n")
    fib_chunk.emit(Opcode.PUSH_INT,   2)
    fib_chunk.emit(Opcode.SUB)
    fib_chunk.emit(Opcode.CALL, 1)

    # -- add them --
    fib_chunk.emit(Opcode.ADD)
    fib_chunk.emit(Opcode.RETURN)

    disassemble(fib_chunk)
except Exception as e:
    import traceback; traceback.print_exc()
```

### `compile_and_run`: The Full Pipeline

```python
try:
    from dataclasses import dataclass, field
    from typing import Any, List, Dict
    from enum import IntEnum

    class Opcode(IntEnum):
        PUSH_INT=1; PUSH_FLOAT=2; PUSH_STR=3; PUSH_BOOL=4; PUSH_NIL=5
        POP=6; DUP=7; SWAP=8
        ADD=9; SUB=10; MUL=11; DIV=12; MOD=13; NEG=14; POW=15
        EQ=16; NEQ=17; LT=18; LE=19; GT=20; GE=21
        AND=22; OR=23; NOT=24
        LOAD_NAME=25; STORE_NAME=26; LOAD_LOCAL=27; STORE_LOCAL=28
        JUMP=29; JUMP_IF_FALSE=30; JUMP_IF_TRUE=31
        MAKE_FUNCTION=32; MAKE_CLOSURE=33; CALL=34; RETURN=35
        PRINT=36; LOAD_BUILTIN=37

    @dataclass
    class Instruction:
        opcode: int; operand: Any = None
        def __repr__(self):
            name = Opcode(self.opcode).name
            return f"{name}({self.operand!r})" if self.operand is not None else name

    @dataclass
    class Chunk:
        name: str = "<module>"
        instructions: List[Instruction] = field(default_factory=list)
        def emit(self, op, operand=None):
            idx = len(self.instructions); self.instructions.append(Instruction(op, operand)); return idx
        def patch(self, idx, v): self.instructions[idx].operand = v
        def __len__(self): return len(self.instructions)

    @dataclass
    class Num: value: float
    @dataclass
    class Bool: value: bool
    @dataclass
    class Str: value: str
    @dataclass
    class Nil: pass
    @dataclass
    class Name: name: str
    @dataclass
    class Assign: name: str; value: Any
    @dataclass
    class BinOp: op: str; left: Any; right: Any
    @dataclass
    class UnaryOp: op: str; operand: Any
    @dataclass
    class If: condition: Any; then_body: List[Any]; else_body: List[Any]
    @dataclass
    class While: condition: Any; body: List[Any]
    @dataclass
    class Return: value: Any
    @dataclass
    class FunDecl: name: str; params: List[str]; body: List[Any]
    @dataclass
    class Call: callee: Any; args: List[Any]
    @dataclass
    class Print: value: Any

    _OPS = {"+":Opcode.ADD,"-":Opcode.SUB,"*":Opcode.MUL,"/":Opcode.DIV,
            "%":Opcode.MOD,"**":Opcode.POW,"==":Opcode.EQ,"!=":Opcode.NEQ,
            "<":Opcode.LT,"<=":Opcode.LE,">":Opcode.GT,">=":Opcode.GE}

    class Compiler:
        def __init__(self, name="<module>"): self.chunk = Chunk(name)
        def compile_stmts(self, ss):
            for s in ss: self.compile(s)
        def compile(self, node):
            match node:
                case Num(value=v) if isinstance(v,int): self.chunk.emit(Opcode.PUSH_INT,v)
                case Num(value=v): self.chunk.emit(Opcode.PUSH_FLOAT,v)
                case Bool(value=v): self.chunk.emit(Opcode.PUSH_BOOL,int(v))
                case Str(value=v): self.chunk.emit(Opcode.PUSH_STR,v)
                case Nil(): self.chunk.emit(Opcode.PUSH_NIL)
                case Name(name=n): self.chunk.emit(Opcode.LOAD_NAME,n)
                case Assign(name=n,value=v): self.compile(v); self.chunk.emit(Opcode.STORE_NAME,n)
                case BinOp(op="and",left=l,right=r):
                    self.compile(l); self.chunk.emit(Opcode.DUP)
                    j=self.chunk.emit(Opcode.JUMP_IF_FALSE,0); self.chunk.emit(Opcode.POP)
                    self.compile(r); self.chunk.patch(j,len(self.chunk))
                case BinOp(op="or",left=l,right=r):
                    self.compile(l); self.chunk.emit(Opcode.DUP)
                    j=self.chunk.emit(Opcode.JUMP_IF_TRUE,0); self.chunk.emit(Opcode.POP)
                    self.compile(r); self.chunk.patch(j,len(self.chunk))
                case BinOp(op=op,left=l,right=r): self.compile(l); self.compile(r); self.chunk.emit(_OPS[op])
                case UnaryOp(op="-",operand=e): self.compile(e); self.chunk.emit(Opcode.NEG)
                case UnaryOp(op="not",operand=e): self.compile(e); self.chunk.emit(Opcode.NOT)
                case If(condition=c,then_body=t,else_body=e):
                    self.compile(c); jf=self.chunk.emit(Opcode.JUMP_IF_FALSE,0)
                    self.compile_stmts(t); je=self.chunk.emit(Opcode.JUMP,0)
                    self.chunk.patch(jf,len(self.chunk)); self.compile_stmts(e)
                    self.chunk.patch(je,len(self.chunk))
                case While(condition=c,body=b):
                    start=len(self.chunk); self.compile(c)
                    ex=self.chunk.emit(Opcode.JUMP_IF_FALSE,0)
                    self.compile_stmts(b); self.chunk.emit(Opcode.JUMP,start)
                    self.chunk.patch(ex,len(self.chunk))
                case FunDecl(name=n,params=params,body=body):
                    inner=Compiler(n)
                    for p in reversed(params): inner.chunk.emit(Opcode.STORE_LOCAL,p)
                    inner.compile_stmts(body)
                    inner.chunk.emit(Opcode.PUSH_NIL); inner.chunk.emit(Opcode.RETURN)
                    self.chunk.emit(Opcode.MAKE_FUNCTION,inner.chunk)
                    self.chunk.emit(Opcode.STORE_NAME,n)
                case Call(callee=cal,args=args):
                    self.compile(cal)
                    for a in args: self.compile(a)
                    self.chunk.emit(Opcode.CALL,len(args))
                case Return(value=v): self.compile(v); self.chunk.emit(Opcode.RETURN)
                case Print(value=v): self.compile(v); self.chunk.emit(Opcode.PRINT)
                case _: raise NotImplementedError(f"Unknown: {node!r}")

    @dataclass
    class CallFrame:
        chunk: Any; ip: int = 0
        locals: Dict[str,Any] = field(default_factory=dict)
        def read(self):
            if self.ip>=len(self.chunk.instructions): return None
            instr=self.chunk.instructions[self.ip]; self.ip+=1; return instr

    @dataclass
    class Function:
        name: str; params: List[str]; chunk: Any
        def __repr__(self): return f"<function {self.name}/{len(self.params)}>"

    class VM:
        def __init__(self): self.stack=[]; self.frames=[]; self.globals={}
        def push(self,v): self.stack.append(v)
        def pop(self): return self.stack.pop()
        def run(self,chunk):
            self.frames.append(CallFrame(chunk)); return self._execute()
        def _execute(self):
            while True:
                if not self.frames: return self.pop() if self.stack else None
                frame=self.frames[-1]; instr=frame.read()
                if instr is None: self.frames.pop(); continue
                op=Opcode(instr.opcode)
                if   op==Opcode.PUSH_INT:   self.push(instr.operand)
                elif op==Opcode.PUSH_FLOAT: self.push(instr.operand)
                elif op==Opcode.PUSH_STR:   self.push(instr.operand)
                elif op==Opcode.PUSH_BOOL:  self.push(bool(instr.operand))
                elif op==Opcode.PUSH_NIL:   self.push(None)
                elif op==Opcode.POP:        self.pop()
                elif op==Opcode.DUP:        self.push(self.stack[-1])
                elif op==Opcode.ADD:  r=self.pop();l=self.pop();self.push(l+r)
                elif op==Opcode.SUB:  r=self.pop();l=self.pop();self.push(l-r)
                elif op==Opcode.MUL:  r=self.pop();l=self.pop();self.push(l*r)
                elif op==Opcode.DIV:
                    r=self.pop();l=self.pop()
                    if r==0: raise RuntimeError("Division by zero")
                    self.push(l/r)
                elif op==Opcode.MOD:  r=self.pop();l=self.pop();self.push(l%r)
                elif op==Opcode.POW:  r=self.pop();l=self.pop();self.push(l**r)
                elif op==Opcode.NEG:  self.push(-self.pop())
                elif op==Opcode.EQ:   r=self.pop();l=self.pop();self.push(l==r)
                elif op==Opcode.NEQ:  r=self.pop();l=self.pop();self.push(l!=r)
                elif op==Opcode.LT:   r=self.pop();l=self.pop();self.push(l<r)
                elif op==Opcode.LE:   r=self.pop();l=self.pop();self.push(l<=r)
                elif op==Opcode.GT:   r=self.pop();l=self.pop();self.push(l>r)
                elif op==Opcode.GE:   r=self.pop();l=self.pop();self.push(l>=r)
                elif op==Opcode.NOT:  self.push(not self.pop())
                elif op==Opcode.AND:  r=self.pop();l=self.pop();self.push(l and r)
                elif op==Opcode.OR:   r=self.pop();l=self.pop();self.push(l or r)
                elif op==Opcode.LOAD_NAME:
                    n=instr.operand
                    if n in frame.locals: self.push(frame.locals[n])
                    elif n in self.globals: self.push(self.globals[n])
                    else: raise RuntimeError(f"Undefined: {n!r}")
                elif op==Opcode.STORE_NAME:
                    v=self.pop(); frame.locals[instr.operand]=v; self.globals[instr.operand]=v
                elif op==Opcode.LOAD_LOCAL: self.push(frame.locals[instr.operand])
                elif op==Opcode.STORE_LOCAL: frame.locals[instr.operand]=self.pop()
                elif op==Opcode.JUMP: frame.ip=instr.operand
                elif op==Opcode.JUMP_IF_FALSE:
                    if not self.pop(): frame.ip=instr.operand
                elif op==Opcode.JUMP_IF_TRUE:
                    if self.pop(): frame.ip=instr.operand
                elif op==Opcode.MAKE_FUNCTION:
                    self.push(Function(instr.operand.name,[],instr.operand))
                elif op==Opcode.CALL:
                    n_args=instr.operand; args=[self.pop() for _ in range(n_args)]; args.reverse()
                    fn=self.pop()
                    if not isinstance(fn,Function): raise RuntimeError(f"Not callable: {fn!r}")
                    nf=CallFrame(fn.chunk)
                    # Parameters are bound via STORE_LOCAL at top of function chunk.
                    # Push them onto the stack so STORE_LOCAL can pop them.
                    for v in reversed(args): self.push(v)
                    self.frames.append(nf)
                elif op==Opcode.RETURN:
                    ret=self.pop(); self.frames.pop(); self.push(ret)
                elif op==Opcode.PRINT: print(self.pop())
                else: raise RuntimeError(f"Unknown opcode {op}")

    # ── compile_and_run glue function ─────────────────────────────
    def compile_and_run(stmts, verbose=False):
        c = Compiler()
        c.compile_stmts(stmts)
        if verbose:
            print("=== Bytecode ===")
            for i, instr in enumerate(c.chunk.instructions):
                print(f"  {i:4d}  {instr}")
            print()
        vm = VM()
        vm.run(c.chunk)
        return vm

    # ── Test 1: fibonacci ─────────────────────────────────────────
    fib_prog = [
        FunDecl("fib", ["n"], [
            If(
                condition=BinOp("<=", Name("n"), Num(1)),
                then_body=[Return(Name("n"))],
                else_body=[]
            ),
            Return(BinOp("+",
                Call(Name("fib"), [BinOp("-", Name("n"), Num(1))]),
                Call(Name("fib"), [BinOp("-", Name("n"), Num(2))]),
            ))
        ]),
        Print(Call(Name("fib"), [Num(10)])),
    ]

    print("fib(10) =", end=" ")
    compile_and_run(fib_prog)
except Exception as e:
    import traceback; traceback.print_exc()
```

### Performance Comparison: Tree-Walker vs Bytecode VM

One of the key selling points of a bytecode VM is speed. Let us measure the difference on Fibonacci, which exercises recursive calls heavily.

```python
try:
    import time

    # ── Tree-walking interpreter (reference) ──────────────────────
    class TreeWalker:
        def __init__(self):
            self.env = {}

        def eval(self, node, env=None):
            if env is None: env = self.env
            match node:
                case Num(value=v): return v
                case Bool(value=v): return v
                case Name(name=n):
                    if n in env: return env[n]
                    raise RuntimeError(f"Undefined: {n!r}")
                case Assign(name=n, value=v):
                    result = self.eval(v, env); env[n] = result; return result
                case BinOp(op=op, left=l, right=r):
                    lv = self.eval(l, env); rv = self.eval(r, env)
                    return {"+":lv+rv, "-":lv-rv, "*":lv*rv, "/":lv/rv,
                            "==":lv==rv, "!=":lv!=rv, "<":lv<rv,
                            "<=":lv<=rv, ">":lv>rv, ">=":lv>=rv}[op]
                case If(condition=c, then_body=t, else_body=e):
                    branch = t if self.eval(c, env) else e
                    for s in branch: self.eval(s, env)
                case FunDecl(name=n, params=params, body=body):
                    closure_env = dict(env)
                    def make_fn(p=params, b=body, ce=closure_env):
                        def call(*args):
                            local = dict(ce)
                            for param, val in zip(p, args): local[param] = val
                            result = None
                            for stmt in b:
                                try: result = self.eval(stmt, local)
                                except _Return as ret: return ret.value
                            return result
                        return call
                    env[n] = make_fn(); return None
                case Call(callee=cal, args=args):
                    fn = self.eval(cal, env)
                    arg_vals = [self.eval(a, env) for a in args]
                    return fn(*arg_vals)
                case Return(value=v):
                    raise _Return(self.eval(v, env))
                case _: raise NotImplementedError(f"TreeWalker: {node!r}")

    class _Return(Exception):
        def __init__(self, value): self.value = value

    from dataclasses import dataclass, field
    from typing import Any, List, Dict
    from enum import IntEnum

    class Opcode(IntEnum):
        PUSH_INT=1; PUSH_FLOAT=2; PUSH_STR=3; PUSH_BOOL=4; PUSH_NIL=5
        POP=6; DUP=7; SWAP=8
        ADD=9; SUB=10; MUL=11; DIV=12; MOD=13; NEG=14; POW=15
        EQ=16; NEQ=17; LT=18; LE=19; GT=20; GE=21
        AND=22; OR=23; NOT=24
        LOAD_NAME=25; STORE_NAME=26; LOAD_LOCAL=27; STORE_LOCAL=28
        JUMP=29; JUMP_IF_FALSE=30; JUMP_IF_TRUE=31
        MAKE_FUNCTION=32; MAKE_CLOSURE=33; CALL=34; RETURN=35
        PRINT=36; LOAD_BUILTIN=37

    @dataclass
    class Instruction:
        opcode: int; operand: Any = None

    @dataclass
    class Chunk:
        name: str = "<module>"
        instructions: List[Instruction] = field(default_factory=list)
        def emit(self,op,operand=None):
            idx=len(self.instructions); self.instructions.append(Instruction(op,operand)); return idx
        def patch(self,idx,v): self.instructions[idx].operand=v
        def __len__(self): return len(self.instructions)

    @dataclass
    class Num: value: float
    @dataclass
    class Bool: value: bool
    @dataclass
    class Name: name: str
    @dataclass
    class Assign: name: str; value: Any
    @dataclass
    class BinOp: op: str; left: Any; right: Any
    @dataclass
    class If: condition: Any; then_body: List[Any]; else_body: List[Any]
    @dataclass
    class While: condition: Any; body: List[Any]
    @dataclass
    class Return: value: Any
    @dataclass
    class FunDecl: name: str; params: List[str]; body: List[Any]
    @dataclass
    class Call: callee: Any; args: List[Any]
    @dataclass
    class Print: value: Any

    _OPS2 = {"+":Opcode.ADD,"-":Opcode.SUB,"*":Opcode.MUL,"/":Opcode.DIV,
             "%":Opcode.MOD,"**":Opcode.POW,"==":Opcode.EQ,"!=":Opcode.NEQ,
             "<":Opcode.LT,"<=":Opcode.LE,">":Opcode.GT,">=":Opcode.GE}

    class Compiler2:
        def __init__(self,name="<module>"): self.chunk=Chunk(name)
        def compile_stmts(self,ss):
            for s in ss: self.compile(s)
        def compile(self,node):
            match node:
                case Num(value=v) if isinstance(v,int): self.chunk.emit(Opcode.PUSH_INT,v)
                case Num(value=v): self.chunk.emit(Opcode.PUSH_FLOAT,v)
                case Name(name=n): self.chunk.emit(Opcode.LOAD_NAME,n)
                case Assign(name=n,value=v): self.compile(v); self.chunk.emit(Opcode.STORE_NAME,n)
                case BinOp(op=op,left=l,right=r): self.compile(l); self.compile(r); self.chunk.emit(_OPS2[op])
                case If(condition=c,then_body=t,else_body=e):
                    self.compile(c); jf=self.chunk.emit(Opcode.JUMP_IF_FALSE,0)
                    self.compile_stmts(t); je=self.chunk.emit(Opcode.JUMP,0)
                    self.chunk.patch(jf,len(self.chunk)); self.compile_stmts(e)
                    self.chunk.patch(je,len(self.chunk))
                case FunDecl(name=n,params=params,body=body):
                    inner=Compiler2(n)
                    for p in reversed(params): inner.chunk.emit(Opcode.STORE_LOCAL,p)
                    inner.compile_stmts(body)
                    inner.chunk.emit(Opcode.PUSH_NIL); inner.chunk.emit(Opcode.RETURN)
                    self.chunk.emit(Opcode.MAKE_FUNCTION,inner.chunk)
                    self.chunk.emit(Opcode.STORE_NAME,n)
                case Call(callee=cal,args=args):
                    self.compile(cal)
                    for a in args: self.compile(a)
                    self.chunk.emit(Opcode.CALL,len(args))
                case Return(value=v): self.compile(v); self.chunk.emit(Opcode.RETURN)
                case _: raise NotImplementedError(f"{node!r}")

    @dataclass
    class CallFrame2:
        chunk: Any; ip: int = 0
        locals: Dict[str,Any] = field(default_factory=dict)
        def read(self):
            if self.ip>=len(self.chunk.instructions): return None
            instr=self.chunk.instructions[self.ip]; self.ip+=1; return instr

    @dataclass
    class Function2:
        name: str; params: List[str]; chunk: Any
        def __repr__(self): return f"<fn {self.name}>"

    class VM2:
        def __init__(self): self.stack=[]; self.frames=[]; self.globals={}
        def push(self,v): self.stack.append(v)
        def pop(self): return self.stack.pop()
        def run(self,chunk): self.frames.append(CallFrame2(chunk)); return self._execute()
        def _execute(self):
            while True:
                if not self.frames: return self.pop() if self.stack else None
                frame=self.frames[-1]; instr=frame.read()
                if instr is None: self.frames.pop(); continue
                op=Opcode(instr.opcode)
                if   op==Opcode.PUSH_INT: self.push(instr.operand)
                elif op==Opcode.PUSH_NIL: self.push(None)
                elif op==Opcode.ADD:  r=self.pop();l=self.pop();self.push(l+r)
                elif op==Opcode.SUB:  r=self.pop();l=self.pop();self.push(l-r)
                elif op==Opcode.LE:   r=self.pop();l=self.pop();self.push(l<=r)
                elif op==Opcode.LOAD_NAME:
                    n=instr.operand
                    if n in frame.locals: self.push(frame.locals[n])
                    elif n in self.globals: self.push(self.globals[n])
                    else: raise RuntimeError(f"Undefined: {n!r}")
                elif op==Opcode.STORE_NAME:
                    v=self.pop(); frame.locals[instr.operand]=v; self.globals[instr.operand]=v
                elif op==Opcode.LOAD_LOCAL: self.push(frame.locals[instr.operand])
                elif op==Opcode.STORE_LOCAL: frame.locals[instr.operand]=self.pop()
                elif op==Opcode.JUMP: frame.ip=instr.operand
                elif op==Opcode.JUMP_IF_FALSE:
                    if not self.pop(): frame.ip=instr.operand
                elif op==Opcode.MAKE_FUNCTION: self.push(Function2(instr.operand.name,[],instr.operand))
                elif op==Opcode.CALL:
                    n_args=instr.operand; args=[self.pop() for _ in range(n_args)]; args.reverse()
                    fn=self.pop()
                    nf=CallFrame2(fn.chunk)
                    for v in reversed(args): self.push(v)
                    self.frames.append(nf)
                elif op==Opcode.RETURN:
                    ret=self.pop(); self.frames.pop(); self.push(ret)
                else: pass  # silently skip unimplemented opcodes in this minimal VM

    fib_ast = [
        FunDecl("fib", ["n"], [
            If(
                condition=BinOp("<=", Name("n"), Num(1)),
                then_body=[Return(Name("n"))],
                else_body=[]
            ),
            Return(BinOp("+",
                Call(Name("fib"), [BinOp("-", Name("n"), Num(1))]),
                Call(Name("fib"), [BinOp("-", Name("n"), Num(2))]),
            ))
        ]),
    ]

    N = 22  # use 22 instead of 30 to keep the demo fast in a browser sandbox

    # ── Time the tree-walker ───────────────────────────────────────
    tw = TreeWalker()
    for stmt in fib_ast:
        tw.eval(stmt, tw.env)

    t0 = time.perf_counter()
    tw_result = tw.env["fib"](N)
    tw_time = time.perf_counter() - t0

    # ── Time the bytecode VM ───────────────────────────────────────
    c2 = Compiler2(); c2.compile_stmts(fib_ast)
    vm2 = VM2(); vm2.run(c2.chunk)

    t0 = time.perf_counter()
    # Call fib(N) via the VM
    call_chunk = Chunk("call_fib")
    call_chunk.emit(Opcode.LOAD_NAME, "fib")
    call_chunk.emit(Opcode.PUSH_INT, N)
    call_chunk.emit(Opcode.CALL, 1)
    vm2.run(call_chunk)
    vm_result = vm2.pop() if vm2.stack else None
    vm_time = time.perf_counter() - t0

    print(f"fib({N})")
    print(f"  Tree-walker:  result={tw_result}, time={tw_time*1000:.1f} ms")
    print(f"  Bytecode VM:  result={vm_result}, time={vm_time*1000:.1f} ms")
    if tw_time > 0:
        print(f"  Speedup: {tw_time/vm_time:.1f}x" if vm_time > 0 else "  (VM too fast to measure)")
except Exception as e:
    import traceback; traceback.print_exc()
```

### Test Checklist

Before submitting your bytecode VM implementation, verify all of the following:

- [ ] **Arithmetic** — `(2 + 3) * 4 - 1` evaluates to `19`
- [ ] **Comparison** — `5 >= 5` evaluates to `True`; `5 > 5` evaluates to `False`
- [ ] **Short-circuit `and`** — `false and explode()` does not call `explode`
- [ ] **Short-circuit `or`** — `true or explode()` does not call `explode`
- [ ] **If / else** — `if 3 > 2 { print("yes"); } else { print("no"); }` prints `yes`
- [ ] **While loop** — count from 1 to 5, printing each value
- [ ] **Function call** — `fun square(x) { return x * x; }` then `square(7)` returns `49`
- [ ] **Recursion** — `fib(10)` returns `55`
- [ ] **Nested functions** — a function returning a closure correctly captures its upvalues
- [ ] **Disassembler** — `disassemble(chunk)` produces readable output for all of the above

### What Is Next: GC and JIT

**Garbage Collector** — the VM currently never frees memory. Add a mark-and-sweep GC: the GC roots are the value stack, all call frames, and the globals table. Everything reachable from roots is live; everything else can be reclaimed. See the Garbage Collection tutorial for a complete implementation over a simulated heap.

**Just-in-Time Compilation** — modern VMs (V8, LuaJIT, PyPy) profile which bytecode sequences run most frequently ("hot paths") and compile those sequences to native machine code at runtime. The key insight is that the JIT can specialize on observed types: if `ADD` has only ever seen integers, the JIT emits a single native `ADD` instruction instead of a general dispatch. Python 3.13's "copy-and-patch" JIT uses exactly this approach.

**Register-Based VMs** — Lua 5.0 used a stack-based VM; Lua 5.1 switched to a **register-based** VM, which reduces instruction count by 20–30% by keeping intermediate values in named registers rather than pushing and popping them. The CPython team is exploring a register-based bytecode for CPython 3.14+.

---

## Summary

You have now built every layer of a bytecode VM:

| Phase | What you built | Key concept |
|---|---|---|
| 0 | Motivation and comparison table | Execution strategy trade-offs |
| 1 | `Opcode` enum and `Instruction`/`Chunk` dataclasses | Instruction set architecture |
| 2 | `Compiler` (AST → `Chunk`) | Post-order traversal; patch-back for forward jumps |
| 3 | `VM` (dispatch loop, value stack, call stack) | Stack machine execution model |
| 4 | `Upvalue` and `MAKE_CLOSURE` | Closing over live stack slots |
| 5 | `disassemble`, `compile_and_run`, performance timing | Tooling and integration |

The architecture you built is not academic — it is the same design used by Lua, CPython (with a few thousand additional opcodes), and the JVM's early interpreter tier. The primary difference between this tutorial's VM and a production VM is scale: more opcodes, optimized dispatch (computed `goto` in C, or a `switch` statement with branch prediction hints), a GC, and a JIT tier for hot loops.
