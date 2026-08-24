<!--
author:   CS374 Course Staff
email:    
version:  0.0.1
language: en
narrator: US English Female

comment: Build a stack-based bytecode VM for Mini, the same architecture used by CPython, the JVM, and Lua.  Render with https://liascript.github.io/course/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374-Fall2026/gh-pages/_pages/Tutorials/tutorial-bytecode-vm.md

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

Your tree-walking interpreter is correct and elegant, but every time it evaluates `x + 1` it traverses three AST nodes, looks up `x` in the environment dictionary, allocates a new addition result, and works its way back up.  For programs with tight loops or deeply recursive functions, this overhead adds up.  **Bytecode virtual machines** solve this by translating the AST once into a flat sequence of simple instructions, then running those instructions in a tight loop.  This is the architecture behind CPython, the Java Virtual Machine, Lua, Ruby's YARV, and dozens of other production runtimes.

This tutorial builds a complete bytecode VM for Mini in six phases:

1.  **Phase 0**: Why bytecode?  Comparison of execution strategies
2.  **Phase 1**: Instruction Set Architecture: the `Opcode` enum and `Instruction` dataclass
3.  **Phase 2**: The Compiler: walking the AST and emitting bytecode
4.  **Phase 3**: The VM: the dispatch loop, value stack, and call stack
5.  **Phase 4**: Functions and closures: upvalues (the Lua trick)
6.  **Phase 5**: Integration, disassembler, and performance comparison

**Prerequisites:** the Mini interpreter assignment, the Closures activity, and the Environments lecture.  You do not need to understand the JVM or CPython internals; we build everything from scratch.

---

## Phase 0: Why Bytecode?

### Three Ways to Execute a Program

When you have a parsed AST, you have three main options for executing it:

| Strategy | How it works | Startup cost | Runtime speed | Portability |
|---|---|---|---|---|
| **Tree-walking interpreter** | Recursively evaluate AST nodes | None | Slow (pointer-chasing, branching per node) | Portable (runs on any host with the interpreter) |
| **Bytecode VM** | Compile AST -> flat instruction list; run in a dispatch loop | Small (compile once) | Medium (tight loop, cache-friendly) | Portable (bytecode is platform-independent) |
| **Native compiler** | Compile AST -> machine code | Large (codegen, linking) | Fast (no interpretation overhead) | Not portable (x86 vs ARM vs RISC-V) |

Bytecode VMs hit the sweet spot: they are much faster than tree-walkers in practice (2-10×) and require far less effort to implement than a native compiler.

### Real-World Bytecode VMs

Every major dynamic language uses a bytecode VM:

- **CPython**: Python's reference implementation; compiles `.py` to `.pyc` bytecode for the CPython VM
- **JVM**: Java, Kotlin, Scala, Clojure all compile to `.class` files (JVM bytecode)
- **Lua 5.x**: direct AST-to-bytecode compiler; used in game engines and embedded systems
- **Ruby's YARV**: Yet Another Ruby VM, introduced in Ruby 1.9
- **V8 (JavaScript)**: starts with bytecode (Ignition), then JIT-compiles hot paths (TurboFan)

### Peeking at CPython's Bytecode

Python exposes its compiler through the `dis` module.  Try this in any Python 3.10+ environment:

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

You will see instructions like `LOAD_FAST`, `BINARY_OP`, `RETURN_VALUE`.  These map almost directly to what we will build.  The key observation: **each instruction is just a small integer (the opcode) plus an optional integer operand**.  No tree traversal needed at runtime.

### The Core Insight: Separation of Compilation and Execution

```
Source code
    |
    v
  Lexer  --> Token stream
    |
    v
  Parser --> AST (tree structure)
    |
    v
 Compiler --> Bytecode (flat list of instructions)   <- compile once
    |
    v
    VM     --> Result                                <- run many times
```

The compiler runs once.  The VM runs the same bytecode repeatedly, or, in the case of a REPL, compiles each expression and immediately runs it.  The bytecode can also be serialized to disk (like `.pyc` files) so that compilation cost is paid only when the source changes.

---

## Phase 1: Instruction Set Architecture

### Opcodes

An **opcode** (operation code) is an integer that names one VM operation.  We use Python's `enum.IntEnum` so opcodes can be stored compactly and printed by name.

```python
try:
    from enum import IntEnum, auto

    class Opcode(IntEnum):
        # -- Stack manipulation ------------------------------------
        PUSH_INT   = auto()   # push integer constant (operand = value)
        PUSH_FLOAT = auto()   # push float constant
        PUSH_STR   = auto()   # push string constant
        PUSH_BOOL  = auto()   # push True/False (operand = 0 or 1)
        PUSH_NIL   = auto()   # push None
        POP        = auto()   # discard top of stack
        DUP        = auto()   # duplicate top of stack
        SWAP       = auto()   # swap top two stack values

        # -- Arithmetic --------------------------------------------
        ADD  = auto()
        SUB  = auto()
        MUL  = auto()
        DIV  = auto()
        MOD  = auto()
        NEG  = auto()   # unary negation
        POW  = auto()

        # -- Comparison (push bool result) -------------------------
        EQ   = auto()
        NEQ  = auto()
        LT   = auto()
        LE   = auto()
        GT   = auto()
        GE   = auto()

        # -- Logic -------------------------------------------------
        AND  = auto()   # non-short-circuit bitwise AND (short-circuit via jumps)
        OR   = auto()   # non-short-circuit bitwise OR
        NOT  = auto()

        # -- Variable access ---------------------------------------
        LOAD_NAME   = auto()   # operand = name string; push globals[name]
        STORE_NAME  = auto()   # operand = name string; globals[name] = pop()
        LOAD_LOCAL  = auto()   # operand = slot index; push locals[slot]
        STORE_LOCAL = auto()   # operand = slot index; locals[slot] = pop()

        # -- Control flow ------------------------------------------
        JUMP          = auto()   # unconditional; operand = target index
        JUMP_IF_FALSE = auto()   # pop; jump if falsy
        JUMP_IF_TRUE  = auto()   # pop; jump if truthy

        # -- Functions ---------------------------------------------
        MAKE_FUNCTION  = auto()  # wrap a Chunk into a Function object
        MAKE_CLOSURE   = auto()  # like MAKE_FUNCTION but also captures upvalues
        CALL           = auto()  # operand = arg count; pops args + function
        RETURN         = auto()  # pop return value, restore caller frame

        # -- Built-ins ---------------------------------------------
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

An `Instruction` pairs an opcode with an optional operand.  A `Chunk` is the compiled output for one function (or the top-level program): a list of instructions, a constant pool, and a name table.

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

Before writing the compiler, let us hand-compile an expression to see what the output looks like.  Mini follows standard arithmetic precedence (`*` before `+`), so `1 + 2 * 3` parses as `1 + (2 * 3)`.

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

This flat sequence is what the VM actually executes: no tree traversal, no recursion, just a loop over a list of integers.

---

## Phase 2: The Compiler (AST -> Bytecode)

The compiler walks the AST exactly once and emits instructions in **post-order**: compile the operands first, then emit the operator.  This naturally produces the right stack layout.

### AST Node Definitions

We define a minimal AST for the Mini language.  If you already have your parser's AST classes, you would use those instead.

```python
try:
    from dataclasses import dataclass
    from typing import Any, List, Optional

    # -- Literal values --------------------------------------------
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

    # -- Variables -------------------------------------------------
    @dataclass
    class Name:
        name: str

    @dataclass
    class Assign:
        name: str
        value: Any  # expression

    # -- Arithmetic / logic ----------------------------------------
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

    # -- Control flow ----------------------------------------------
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

    # -- Functions -------------------------------------------------
    @dataclass
    class FunDecl:
        name:   str
        params: List[str]
        body:   List[Any]

    @dataclass
    class Call:
        callee: Any
        args:   List[Any]

    # -- Statements ------------------------------------------------
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

    # -- Re-define Opcode (standalone cell) ------------------------
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

    # -- Minimal AST (re-define for standalone cell) ---------------
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

    # -- Compiler --------------------------------------------------
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
                # -- Literals --------------------------------------
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

                # -- Variable read ----------------------------------
                case Name(name=n):
                    self.chunk.emit(Opcode.LOAD_NAME, n)

                # -- Assignment ------------------------------------
                case Assign(name=n, value=v):
                    self.compile(v)
                    self.chunk.emit(Opcode.STORE_NAME, n)

                # -- Binary operations -----------------------------
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

                # -- Unary operations ------------------------------
                case UnaryOp(op="-", operand=e):
                    self.compile(e)
                    self.chunk.emit(Opcode.NEG)
                case UnaryOp(op="not", operand=e):
                    self.compile(e)
                    self.chunk.emit(Opcode.NOT)

                # -- If / else -------------------------------------
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

                # -- While loop ------------------------------------
                case While(condition=cond, body=body):
                    loop_start = len(self.chunk)
                    self.compile(cond)
                    exit_jump = self.chunk.emit(Opcode.JUMP_IF_FALSE, 0)
                    self.compile_stmts(body)
                    self.chunk.emit(Opcode.JUMP, loop_start)   # back-edge
                    self.chunk.patch(exit_jump, len(self.chunk))

                # -- Function declaration --------------------------
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

                # -- Function call ---------------------------------
                case Call(callee=callee, args=args):
                    self.compile(callee)
                    for a in args:
                        self.compile(a)
                    self.chunk.emit(Opcode.CALL, len(args))

                # -- Return ----------------------------------------
                case Return(value=v):
                    self.compile(v)
                    self.chunk.emit(Opcode.RETURN)

                # -- Print statement -------------------------------
                case Print(value=v):
                    self.compile(v)
                    self.chunk.emit(Opcode.PRINT)

                # -- Block -----------------------------------------
                case Block(stmts=stmts):
                    self.compile_stmts(stmts)

                case _:
                    raise NotImplementedError(f"Compiler: unknown node {node!r}")

    # -- Demo: compile  if x > 0 { print(x); } ------------------
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

Compiling `if` and `while` requires **forward jumps**: jumps to an address that we do not know yet when we emit the jump instruction.  The solution is the **patch-back** technique:

1.  Emit `JUMP_IF_FALSE 0` (placeholder operand `0`)
2.  Compile the then-branch
3.  Now we know the target address: `len(chunk)` (the next instruction to be emitted)
4.  Overwrite the placeholder with the real address: `chunk.patch(jump_idx, len(chunk))`

This is the same technique used in production compilers.  In the code above, `compile(If(...))` uses `jump_false` and `jump_end` as the patch-back indices.

---

## Phase 3: The VM (Execute Bytecode)

### Call Frames

Each function call gets its own **call frame**: a record of the currently-executing chunk, the instruction pointer within that chunk, and the local variables for that call.

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

    # -- Function object (defined here, used by VM) ----------------
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

The VM's heart is a `while True` loop that fetches one instruction, dispatches on its opcode, and updates the stack.  This is the same structure as CPython's `ceval.c` (though that one is in C and has a few thousand lines of optimizations).

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

        # -- Stack helpers ------------------------------------------
        def push(self, v: Any):  self.stack.append(v)
        def pop(self)  -> Any:   return self.stack.pop()
        def peek(self) -> Any:   return self.stack[-1]

        # -- Entry point --------------------------------------------
        def run(self, chunk: Chunk) -> Any:
            frame = CallFrame(chunk)
            self.frames.append(frame)
            result = self._execute()
            self.frames.pop()
            return result

        # -- Main dispatch loop -------------------------------------
        def _execute(self) -> Any:
            while True:
                frame = self.frames[-1]
                instr = frame.read()
                if instr is None:
                    return self.pop() if self.stack else None

                op = Opcode(instr.opcode)

                # -- Push literals ----------------------------------
                if   op == Opcode.PUSH_INT:   self.push(instr.operand)
                elif op == Opcode.PUSH_FLOAT: self.push(instr.operand)
                elif op == Opcode.PUSH_STR:   self.push(instr.operand)
                elif op == Opcode.PUSH_BOOL:  self.push(bool(instr.operand))
                elif op == Opcode.PUSH_NIL:   self.push(None)

                # -- Stack manipulation -----------------------------
                elif op == Opcode.POP:
                    self.pop()
                elif op == Opcode.DUP:
                    self.push(self.peek())
                elif op == Opcode.SWAP:
                    a = self.pop(); b = self.pop()
                    self.push(a); self.push(b)

                # -- Arithmetic -------------------------------------
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

                # -- Comparisons ------------------------------------
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

                # -- Logic ------------------------------------------
                elif op == Opcode.NOT:
                    self.push(not self.pop())
                elif op == Opcode.AND:
                    r = self.pop(); l = self.pop(); self.push(l and r)
                elif op == Opcode.OR:
                    r = self.pop(); l = self.pop(); self.push(l or r)

                # -- Variable access --------------------------------
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

                # -- Control flow -----------------------------------
                elif op == Opcode.JUMP:
                    frame.ip = instr.operand
                elif op == Opcode.JUMP_IF_FALSE:
                    if not self.pop():
                        frame.ip = instr.operand
                elif op == Opcode.JUMP_IF_TRUE:
                    if self.pop():
                        frame.ip = instr.operand

                # -- Functions --------------------------------------
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

                # -- Built-ins --------------------------------------
                elif op == Opcode.PRINT:
                    print(self.pop())

                else:
                    raise VMError(f"Unknown opcode: {op}")

    # -- Demo: trace execution of 2 * (3 + 4) ----------------------
    print("Tracing: 2 * (3 + 4)")
    print()
    print("  Instruction        Stack after")
    print("  -----------------  ------------------")

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

    # -- (all definitions from Phase 2 and Phase 3 combined) -------
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

    # -- End-to-end test: while loop summing 1..5 ------------------
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

In a tree-walking interpreter, closures are easy: a `Closure` object holds a reference to the environment at the time of creation, and lookups walk the environment chain.  In a bytecode VM, variables live on the stack inside call frames; when a function returns, its frame is gone.  A closure that was created inside that function would be left with a dangling reference.

The **upvalue** pattern (invented for Lua 5.x by Roberto Ierusalimschy) solves this elegantly.

### The Upvalue Pattern

An **upvalue** is an indirect reference to a captured variable.  It has two states:

1.  **Open**: the captured variable is still on the stack (the enclosing function is running).  The upvalue holds a reference into the live stack frame.
2.  **Closed**: the enclosing function has returned.  The upvalue now holds the final value itself (it was "closed over").

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
        list shared with the frame's local slot - both the frame and the
        upvalue write/read through the same list, so mutations are visible.

        When the enclosing frame is popped (function returns), `close()`
        is called: the value is copied into the upvalue itself and the
        shared list is detached. Future reads go to `self.closed_value`.
        """
        cell: List[Any]   # [value] - shared with enclosing frame while open
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

    # -- Demonstrate upvalue closing --------------------------------
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

The classic test for closures is a **counter factory**: a function that returns another function, where the inner function mutates a variable from the enclosing scope.

```python
try:
    from dataclasses import dataclass, field
    from typing import Any, List, Dict, Optional
    from enum import IntEnum

    # -- Simplified closure-aware VM --------------------------------
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
    # This is exactly what a VM's closure object does - hold the captured upvalues.
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

In Lua's VM, `CLOSURE` is a single instruction that creates a closure object and immediately reads the following `UPVALUE` or `GETUPVAL` pseudo-instructions to populate the upvalue list.  CPython uses a different approach: it pre-compiles which variables are "cell variables" (captured by inner functions) vs "free variables" (captured from outer functions) and generates `MAKE_CELL`, `COPY_FREE_VARS` instructions.

---

## Phase 5: Integration and Testing

### The Disassembler

A disassembler pretty-prints the bytecode of a `Chunk` with line numbers and formatted operands.  It is invaluable for debugging the compiler.

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

    # -- Build the fib chunk by hand --------------------------------
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

    # -- compile_and_run glue function -----------------------------
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

    # -- Test 1: fibonacci -----------------------------------------
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

One of the key selling points of a bytecode VM is speed.  Let us measure the difference on Fibonacci, which exercises recursive calls heavily.

```python
try:
    import time

    # -- Tree-walking interpreter (reference) ----------------------
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
                    return {"+":  lambda: lv+rv,  "-":  lambda: lv-rv,
                            "*":  lambda: lv*rv,  "/":  lambda: lv/rv,
                            "==": lambda: lv==rv, "!=": lambda: lv!=rv,
                            "<":  lambda: lv<rv,  "<=": lambda: lv<=rv,
                            ">":  lambda: lv>rv,  ">=": lambda: lv>=rv}[op]()
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

    # -- Time the tree-walker ---------------------------------------
    tw = TreeWalker()
    for stmt in fib_ast:
        tw.eval(stmt, tw.env)

    t0 = time.perf_counter()
    tw_result = tw.env["fib"](N)
    tw_time = time.perf_counter() - t0

    # -- Time the bytecode VM ---------------------------------------
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

- [ ] **Arithmetic**: `(2 + 3) * 4 - 1` evaluates to `19`
- [ ] **Comparison**: `5 >= 5` evaluates to `True`; `5 > 5` evaluates to `False`
- [ ] **Short-circuit `and`**: `false and explode()` does not call `explode`
- [ ] **Short-circuit `or`**: `true or explode()` does not call `explode`
- [ ] **If / else**: `if 3 > 2 { print("yes"); } else { print("no"); }` prints `yes`
- [ ] **While loop**: count from 1 to 5, printing each value
- [ ] **Function call**: `fun square(x) { return x * x; }` then `square(7)` returns `49`
- [ ] **Recursion**: `fib(10)` returns `55`
- [ ] **Nested functions**: a function returning a closure correctly captures its upvalues
- [ ] **Disassembler**: `disassemble(chunk)` produces readable output for all of the above

### What Is Next: GC and JIT

**Garbage Collector**: the VM currently never frees memory.  Add a mark-and-sweep GC: the GC roots are the value stack, all call frames, and the globals table.  Everything reachable from roots is live; everything else can be reclaimed.  See the Garbage Collection tutorial for a complete implementation over a simulated heap.

**Just-in-Time Compilation**: modern VMs (V8, LuaJIT, PyPy) profile which bytecode sequences run most frequently ("hot paths") and compile those sequences to native machine code at runtime.  What makes this work is that the JIT can specialize on observed types: if `ADD` has only ever seen integers, the JIT emits a single native `ADD` instruction instead of a general dispatch.  Python 3.13's "copy-and-patch" JIT uses exactly this approach.

**Register-Based VMs**: Lua 5.0 used a stack-based VM; Lua 5.1 switched to a **register-based** VM, which reduces instruction count by 20-30% by keeping intermediate values in named registers rather than pushing and popping them.  The CPython team is exploring a register-based bytecode for CPython 3.14+.

---

## Summary

You have now built every layer of a bytecode VM:

| Phase | What you built | Key concept |
|---|---|---|
| 0 | Motivation and comparison table | Execution strategy trade-offs |
| 1 | `Opcode` enum and `Instruction`/`Chunk` dataclasses | Instruction set architecture |
| 2 | `Compiler` (AST -> `Chunk`) | Post-order traversal; patch-back for forward jumps |
| 3 | `VM` (dispatch loop, value stack, call stack) | Stack machine execution model |
| 4 | `Upvalue` and `MAKE_CLOSURE` | Closing over live stack slots |
| 5 | `disassemble`, `compile_and_run`, performance timing | Tooling and integration |

The architecture you built is not academic: it is the same design used by Lua, CPython (with a few thousand additional opcodes), and the JVM's early interpreter tier.  The primary difference between this tutorial's VM and a production VM is scale: more opcodes, optimized dispatch (computed `goto` in C, or a `switch` statement with branch prediction hints), a GC, and a JIT tier for hot loops.

---

## Appendix: Compiler Optimizations, Making Programs Faster

This appendix supports the Team Language Project's **Bytecode Compiler and Stack VM** extension: once your compiler emits bytecode, these optimization passes are the natural next step for making the programs it produces run faster.

Think of a compiler optimizer as an editor who rewrites a paragraph to say the same thing in fewer words: the meaning is perfectly preserved, but the form is tightened.  A compiler does the same thing to your program: it replaces slow, verbose machine instructions with fast, compact ones while guaranteeing that every possible input still produces the same output.  You will build five such "editors" (constant folding, dead-code elimination, CSE, inlining, and tail-call optimization), each implemented as a tree rewrite over the AST you have been building throughout the course.

### Learning Goals

By the end of this section, you will be able to:

- Implement constant folding and dead-code elimination as AST-to-AST rewrite passes, and state the correctness condition that distinguishes valid from invalid optimizations
- Implement common subexpression elimination (CSE) by identifying redundant computations in an expression and rewriting the AST to share them
- Implement function inlining as an AST substitution pass, and explain when inlining improves and when it hurts performance
- Recognize tail calls in recursive functions, apply the tail-call optimization transformation, and explain why it enables constant-stack recursion

> **Before You Begin: Prerequisites**
>
> You should be comfortable with the following before starting this section:
>
> - **AST representation**: you know how to represent a program as a tree of dataclass nodes (`Num`, `BinOp`, `Let`, `If`, etc.) and how to walk that tree recursively.
> - **Pattern matching** (`match`/`case`): Python 3.10+ structural pattern matching, used throughout every optimizer below.
> - **Pure vs. side-effectful functions**: you can distinguish between an expression that always produces the same value and one that prints, raises, or mutates state.
> - **Variable scope and substitution**: you understand what "free variable" and "bound variable" mean, and how substituting one expression for another can go wrong (variable capture).
>
> If any of these feel shaky, re-read the functional programming and lambda calculus notes before proceeding; the safety proofs in this section rely on all four.

> **"The first 90% of the code accounts for the first 90% of the development time.  The remaining 10% of the code accounts for the other 90% of the development time."**, Tom Cargill
>
> Optimizations speed up programs *without changing their meaning*.  In this appendix you will implement five core optimizations: constant folding, dead code elimination, common subexpression elimination, inlining, and tail call optimization.  Each operates on the AST or IR, the same data structures you've been building throughout the course.

---

### Model 1: What Makes an Optimization Valid?

**Intuition.**  Before you can speed anything up, you need a safety rule: *when is a transformation allowed?*  The answer is deceptively simple: a transformation is valid if and only if every valid input still produces the same observable output.  "Observable" is the key word: printing to the screen is observable; computing an unused intermediate value is not.  This section builds the mental checklist that every later optimizer will depend on.

An optimization is **valid** if it *preserves program semantics*: the optimized program produces the same observable results as the original for all valid inputs.

```python
# Some "optimizations" are INVALID - they change observable behavior

def f():
    print("side effect!")
    return 0

# INVALID: cannot fold f() + 0 -> 0 (removes the print side effect)
x = f() + 0    # prints "side effect!" and gives x=0
# "optimized": x = 0   # WRONG - side effect gone!

# VALID: can fold pure expressions
y = 2 + 3 * 4   # evaluates to 14 at compile time
# optimized: y = 14

# INVALID: cannot reorder memory operations (in a language with mutation)
a = [1, 2, 3]
def g(lst):
    lst.append(4)
    return len(lst)

# a[0] = g(a)  -- cannot reorder the call and the subscript

# VALID: can eliminate dead code
if False:
    print("never runs")
# optimized: (remove the entire if block)

print("x =", x, "  y =", y)
```
@LIA.eval(`["main.py"]`, `none`, `python3 main.py`)

**Critical Thinking Questions (CTQs)**

> **CTQ 1.1** What property of an expression makes it safe to evaluate at compile time?  (Hint: think about the "pure function" discussion from the functional programming module.)

> **CTQ 1.2** The optimizer must prove that `f()` has no observable side effects before it can eliminate `f() + 0`.  What information would the optimizer need to know about `f`?  Where would it get that information?

> **CTQ 1.3** Name three operations that are NEVER safe to optimize away, even if their result is unused.  (Think: division, function calls, I/O.)

> **Watch out!**  It is tempting to think "if the result is unused, we can delete it."  This is only safe for *pure* expressions. `f() + 0` cannot become `0` if `f` prints, writes to a file, raises an exception, or mutates global state, even though the arithmetic result is discarded.  Always ask: "What happens if I remove this entirely?" before applying any optimization.

---

### Model 2: Constant Folding and Propagation

**Intuition.**  Suppose your program contains `let x = 3 in x + 2`.  A human reader sees immediately that `x + 2` must equal `5`; there is no need to wait until run time to add those two numbers.  Constant folding does this mechanically: whenever both operands of an arithmetic node are already `Num` literals, replace the whole `BinOp` with the computed `Num`.  Constant propagation extends this: once we know `x = 3`, we can substitute `3` for every occurrence of `x` before folding, enabling further reductions downstream.  Together the two passes can collapse an entire chain of `let` bindings into a single number.

**Constant folding**: evaluate constant sub-expressions at compile time.
**Constant propagation**: substitute known constant values for variables.

```python
from dataclasses import dataclass
from typing import Any, Optional

@dataclass
class Num:
    value: float

@dataclass
class Var:
    name: str

@dataclass
class BinOp:
    op: str; left: Any; right: Any

@dataclass
class UnaryOp:
    op: str; operand: Any

@dataclass
class Let:
    name: str; value: Any; body: Any

@dataclass
class If:
    cond: Any; then_: Any; else_: Any

def fold_and_propagate(node, const_env: dict):
    """Constant folding + constant propagation in one pass."""
    match node:
        case Num():
            return node

        case Var(name=n):
            if n in const_env:
                return Num(const_env[n])   # constant propagation
            return node

        case Let(name=n, value=v, body=b):
            folded_v = fold_and_propagate(v, const_env)
            new_env = dict(const_env)
            if isinstance(folded_v, Num):
                new_env[n] = folded_v.value   # propagate this constant!
            return Let(n, folded_v, fold_and_propagate(b, new_env))

        case If(cond=c, then_=t, else_=e):
            fc = fold_and_propagate(c, const_env)
            if isinstance(fc, Num):
                # Dead branch elimination!
                if fc.value != 0:
                    return fold_and_propagate(t, const_env)
                else:
                    return fold_and_propagate(e, const_env)
            return If(fc,
                      fold_and_propagate(t, const_env),
                      fold_and_propagate(e, const_env))

        case UnaryOp(op='-', operand=o):
            fo = fold_and_propagate(o, const_env)
            if isinstance(fo, Num):
                return Num(-fo.value)
            return UnaryOp('-', fo)

        case BinOp(op=op, left=l, right=r):
            fl = fold_and_propagate(l, const_env)
            fr = fold_and_propagate(r, const_env)
            if isinstance(fl, Num) and isinstance(fr, Num):
                match op:
                    case '+': return Num(fl.value + fr.value)
                    case '-': return Num(fl.value - fr.value)
                    case '*': return Num(fl.value * fr.value)
                    case '/' if fr.value != 0: return Num(fl.value / fr.value)
            # Algebraic identities
            if isinstance(fl, Num) and fl.value == 0 and op == '+': return fr
            if isinstance(fr, Num) and fr.value == 0 and op == '+': return fl
            if isinstance(fl, Num) and fl.value == 1 and op == '*': return fr
            if isinstance(fr, Num) and fr.value == 1 and op == '*': return fl
            if isinstance(fl, Num) and fl.value == 0 and op == '*': return Num(0)
            if isinstance(fr, Num) and fr.value == 0 and op == '*': return Num(0)
            return BinOp(op, fl, fr)

def pretty(node) -> str:
    match node:
        case Num(value=v):          return str(int(v) if v == int(v) else v)
        case Var(name=n):           return n
        case Let(name=n, value=v, body=b): return f"let {n}={pretty(v)} in {pretty(b)}"
        case BinOp(op=o, left=l, right=r): return f"({pretty(l)}{o}{pretty(r)})"
        case UnaryOp(op=o, operand=x):     return f"({o}{pretty(x)})"
        case If(cond=c, then_=t, else_=e): return f"if {pretty(c)} then {pretty(t)} else {pretty(e)}"
        case _: return repr(node)

# Test cases
tests = [
    # let x = 3 in let y = x + 2 in x * y  -> let x=3 in let y=5 in 15
    Let('x', Num(3), Let('y', BinOp('+', Var('x'), Num(2)),
                        BinOp('*', Var('x'), Var('y')))),
    # if (2 > 0) then 42 else 0  -> 42  (dead code eliminated)
    If(BinOp('>', Num(2), Num(0)), Num(42), Num(0)),
    # (x + 0) * 1  -> x
    BinOp('*', BinOp('+', Var('x'), Num(0)), Num(1)),
]

for t in tests:
    result = fold_and_propagate(t, {})
    print(f"{pretty(t):50} -> {pretty(result)}")
```
@LIA.eval(`["main.py"]`, `none`, `python3 main.py`)

> **CTQ 2.1** The first test case propagates `x=3` into the body, evaluates `y=5`, then folds `3*5=15`.  What is the final result?  Is there any variable left in the output?

> **CTQ 2.2** Dead code elimination fires when the `If` condition folds to a known constant.  The `2 > 0` case reduces to `Num(1)` (true).  But our code doesn't fold `BinOp('>', Num(2), Num(0))`; fix the `fold_and_propagate` function to handle comparison operators.

> **CTQ 2.3** Constant propagation extends the `const_env` when a `let`-bound name gets a constant value.  Why do we use `new_env = dict(const_env)` (a copy) rather than mutating `const_env` directly?

---

### Model 3: Common Subexpression Elimination (CSE)

**Intuition.**  Imagine writing `(x + 1) * (x + 1)` on paper.  You would not reach for your calculator twice; you would compute `x + 1` once, write down the answer, then square it.  CSE does exactly that: it scans the expression tree for sub-trees that appear more than once (with no intervening mutation), names the shared sub-computation with a fresh `let` binding, and replaces every duplicate occurrence with that name.  The original two additions collapse into one, halving the work.  The trick is identifying "same expression" in a way that is both correct and efficient; that is what `expr_key` does below.

If the same expression appears twice and has no side effects in between, compute it once and reuse the result.

```python
from dataclasses import dataclass, field
from typing import Any

@dataclass
class Num:
    value: float

@dataclass
class Var:
    name: str

@dataclass
class BinOp:
    op: str; left: Any; right: Any

@dataclass
class Let:
    name: str; value: Any; body: Any

# Simple CSE: replace duplicate sub-expressions with shared variables
_cse_counter = 0
def fresh_name():
    global _cse_counter
    _cse_counter += 1
    return f"_cse{_cse_counter}"

def cse(node, seen: dict):
    """
    seen: maps (expr_key) -> variable_name
    Returns (optimized_node, bindings_to_wrap)
    """
    key = expr_key(node)

    # Pure expression seen before? Reuse it!
    if key in seen and is_pure(node):
        return Var(seen[key]), []

    match node:
        case Num() | Var():
            return node, []

        case BinOp(op=op, left=l, right=r):
            new_l, binds_l = cse(l, seen)
            new_r, binds_r = cse(r, seen)
            new_node = BinOp(op, new_l, new_r)
            new_key = expr_key(new_node)
            name = fresh_name()
            seen[new_key] = name
            return Var(name), binds_l + binds_r + [(name, new_node)]

        case _:
            return node, []

def expr_key(node) -> str:
    """Canonical string representation for hashing."""
    match node:
        case Num(value=v): return f"N{v}"
        case Var(name=n):  return f"V{n}"
        case BinOp(op=o, left=l, right=r): return f"({expr_key(l)}{o}{expr_key(r)})"
        case _: return repr(node)

def is_pure(node) -> bool:
    """True if the expression has no side effects."""
    match node:
        case Num() | Var():          return True
        case BinOp(left=l, right=r): return is_pure(l) and is_pure(r)
        case _:                      return False

def wrap_bindings(node, bindings):
    """Wrap the result in let-bindings for CSE temporaries."""
    for name, val in reversed(bindings):
        node = Let(name, val, node)
    return node

def pretty(node) -> str:
    match node:
        case Num(value=v):  return str(int(v) if v == int(v) else v)
        case Var(name=n):   return n
        case BinOp(op=o, left=l, right=r): return f"({pretty(l)}{o}{pretty(r)})"
        case Let(name=n, value=v, body=b):  return f"let {n}={pretty(v)} in\n  {pretty(b)}"

# Expression: (x+1)*(x+1) - x+1 computed TWICE
from dataclasses import dataclass
_cse_counter = 0

x_plus_1 = BinOp('+', Var('x'), Num(1))
expr = BinOp('*', x_plus_1, x_plus_1)

optimized_core, bindings = cse(expr, {})
optimized = wrap_bindings(optimized_core, bindings)

print("Before CSE:")
print(f"  {pretty(expr)}")
print("\nAfter CSE:")
print(f"  {pretty(optimized)}")
```
@LIA.eval(`["main.py"]`, `none`, `python3 main.py`)

> **CTQ 3.1** After CSE, `(x+1)*(x+1)` should become `let _cse1 = (x+1) in _cse1 * _cse1`.  Only ONE addition is computed instead of two.  How many operations were eliminated?

> **CTQ 3.2** Why does CSE only apply to *pure* expressions?  Give an example where applying CSE to an impure expression would change the program's behavior.

> **CTQ 3.3** CSE requires checking if two expressions are "the same."  The `expr_key` function produces a canonical string.  What's wrong with this approach if expressions contain variable names that were renamed by earlier passes?

> **Watch out!**  CSE introduces new variable bindings (`_cse1`, `_cse2`, ...).  If you run CSE before constant propagation, those new variables will block the propagation pass from recognizing constants.  If you run CSE after constant propagation, some sub-expressions that *looked* identical before may differ because their variables were replaced by different constants.  Order matters; design your pipeline intentionally.

---

### Model 4: Function Inlining

**Intuition.**  Every function call costs something: push arguments onto the stack, jump to the callee, eventually jump back, clean up.  For a tiny function like `double(x) = x + x`, the bookkeeping overhead may actually exceed the cost of the addition.  Inlining copies the function body to the call site, replacing the parameter with the actual argument; the call vanishes entirely.  As a bonus, the inlined body is now visible to the surrounding optimizations, so constant folding or CSE may fire again on the merged code.  The danger: inlining a large function (or worse, a recursive one) causes code-size explosion, so every production inliner has a size threshold.

**Inlining** replaces a function call with the function body, substituting arguments for parameters.  This eliminates call overhead and enables further optimizations.

```python
from dataclasses import dataclass
from typing import Any

@dataclass
class Num:
    value: float

@dataclass
class Var:
    name: str

@dataclass
class BinOp:
    op: str; left: Any; right: Any

@dataclass
class Let:
    name: str; value: Any; body: Any

@dataclass
class Lambda:
    param: str; body: Any

@dataclass
class App:   # function application
    func: Any; arg: Any

def substitute(node, var: str, replacement):
    """Replace all free occurrences of var with replacement."""
    match node:
        case Num():                  return node
        case Var(name=n):            return replacement if n == var else node
        case BinOp(op=o, left=l, right=r):
            return BinOp(o, substitute(l, var, replacement),
                            substitute(r, var, replacement))
        case Let(name=n, value=v, body=b):
            new_v = substitute(v, var, replacement)
            if n == var:
                return Let(n, new_v, b)   # var is shadowed in body
            return Let(n, new_v, substitute(b, var, replacement))
        case Lambda(param=p, body=b):
            if p == var: return node   # var is shadowed
            return Lambda(p, substitute(b, var, replacement))
        case App(func=f, arg=a):
            return App(substitute(f, var, replacement),
                       substitute(a, var, replacement))
        case _: return node

def inline(node, fn_env: dict, inline_limit=5):
    """Inline small functions. fn_env maps name -> Lambda."""
    match node:
        case App(func=Var(name=n), arg=a) if n in fn_env:
            lam = fn_env[n]
            if size(lam.body) <= inline_limit:  # only inline small functions
                inlined = substitute(lam.body, lam.param, inline(a, fn_env))
                return inline(inlined, fn_env)   # inline recursively!
        case App(func=f, arg=a):
            return App(inline(f, fn_env), inline(a, fn_env))
        case BinOp(op=o, left=l, right=r):
            return BinOp(o, inline(l, fn_env), inline(r, fn_env))
        case _:
            return node

def size(node) -> int:
    """Estimate node count (cost of inlining)."""
    match node:
        case Num() | Var():          return 1
        case BinOp(left=l, right=r): return 1 + size(l) + size(r)
        case Lambda(body=b):         return 1 + size(b)
        case App(func=f, arg=a):     return 1 + size(f) + size(a)
        case _:                      return 1

def pretty(node) -> str:
    match node:
        case Num(value=v):           return str(int(v) if v == int(v) else v)
        case Var(name=n):            return n
        case BinOp(op=o, left=l, right=r): return f"({pretty(l)}{o}{pretty(r)})"
        case Lambda(param=p, body=b):       return f"λ{p}.{pretty(b)}"
        case App(func=f, arg=a):            return f"{pretty(f)}({pretty(a)})"
        case Let(name=n, value=v, body=b):  return f"let {n}={pretty(v)} in {pretty(b)}"

# double = λx. x + x  - inline double(5) -> 5 + 5
double = Lambda('x', BinOp('+', Var('x'), Var('x')))
fn_env = {'double': double}

expr = App(Var('double'), Num(5))
inlined = inline(expr, fn_env)
print(f"Before: {pretty(expr)}")
print(f"After:  {pretty(inlined)}")

# Compose with constant folding: double(3+2) -> (3+2)+(3+2) -> 10
from functools import reduce
expr2 = App(Var('double'), BinOp('+', Num(3), Num(2)))
inlined2 = inline(expr2, fn_env)
print(f"\nBefore: {pretty(expr2)}")
print(f"Inlined: {pretty(inlined2)}")
# (After constant folding, this would become 10)
```
@LIA.eval(`["main.py"]`, `none`, `python3 main.py`)

> **CTQ 4.1** Inlining `double(5)` produces `5 + 5`.  Can we further fold this?  What optimization would you chain after inlining?

> **CTQ 4.2** The inline limit `inline_limit=5` prevents inlining large functions.  Why?  What happens to code size if you inline aggressively without a limit?

> **CTQ 4.3** Inlining a recursive function directly would loop forever.  How does the limit protect against this?  What more sophisticated check would be needed for a production compiler?

---

### Model 5: Tail Call Optimization (TCO)

**Intuition.**  Consider a recursive function where the very last thing it does before returning is call itself.  At the moment that recursive call happens, the current stack frame has no remaining work to do; it will just forward whatever the callee returns.  That frame is wasted space.  TCO exploits this: instead of pushing a new frame, the compiler converts the call into a backward jump that reuses the existing frame, effectively turning the recursion into a loop.  A tail-recursive function compiled with TCO uses *constant* stack space no matter how deep the recursion goes.  Functional languages like Scheme, Haskell, and Erlang mandate TCO; Python does not implement it natively, but you can simulate it with a trampoline.

A **tail call** is a function call that is the *last* action of a function.  Instead of creating a new stack frame, we can *reuse* the current frame.

```python
import sys

# Without TCO: factorial(10000) causes stack overflow in Python
def factorial_no_tco(n):
    if n <= 1: return 1
    return n * factorial_no_tco(n - 1)   # NOT a tail call: n * (...)

# With an accumulator, the recursive call IS a tail call:
def factorial_tco_helper(n, acc):
    if n <= 1: return acc
    return factorial_tco_helper(n - 1, n * acc)   # TAIL CALL: last action

def factorial_tco(n):
    return factorial_tco_helper(n, 1)

# Trampolining: simulate TCO in Python using thunks
class Thunk:
    def __init__(self, fn, *args):
        self.fn = fn; self.args = args
    def __call__(self):
        return self.fn(*self.args)

def trampoline(fn, *args):
    result = fn(*args)
    while isinstance(result, Thunk):
        result = result()
    return result

def fact_tramp(n, acc=1):
    if n <= 1: return acc
    return Thunk(fact_tramp, n - 1, n * acc)   # return thunk, not recursive call

print(f"factorial_tco(100)   = {factorial_tco(100)}")
print(f"fact_tramp(100)      = {trampoline(fact_tramp, 100)}")

# Without trampoline: would hit recursion limit at ~1000
# With trampoline: works for any n (constant stack depth!)
print(f"fact_tramp(5000)     = ...{str(trampoline(fact_tramp, 5000))[-5:]}")  # last 5 digits

# Detecting tail calls in an AST:
from dataclasses import dataclass
from typing import Any

@dataclass
class Call:
    fn_name: str; args: list

@dataclass
class If:
    cond: Any; then_: Any; else_: Any

@dataclass
class Return:
    value: Any

def is_tail_call(node, fn_name: str) -> bool:
    """Does node end with a tail call to fn_name?"""
    match node:
        case Return(value=Call(fn_name=n)) if n == fn_name:
            return True
        case If(then_=t, else_=e):
            return is_tail_call(t, fn_name) or is_tail_call(e, fn_name)
        case _:
            return False

# fact(n, acc) = if n<=1 then return acc else return fact(n-1, n*acc)
fact_body = If(None,
    Return(None),   # return acc - not a tail call to fact
    Return(Call('fact', []))   # return fact(...) - IS a tail call!
)
print(f"\nfact body has tail call to 'fact': {is_tail_call(fact_body, 'fact')}")
```
@LIA.eval(`["main.py"]`, `none`, `python3 main.py`)

> **CTQ 5.1** `factorial_no_tco` has `return n * factorial_no_tco(n-1)`.  Why is this NOT a tail call?  What computation happens after the recursive call returns?

> **CTQ 5.2** `factorial_tco_helper` has `return factorial_tco_helper(n-1, n*acc)`.  Why IS this a tail call?  What does "last action" mean precisely?

> **CTQ 5.3** Trampolining achieves tail call optimization without changing the language runtime; it works in Python, Java, or any language.  What is the tradeoff compared to a language that natively supports TCO (like Scheme or Haskell)?

> **Watch out!**  Not every recursive call in a tail position belongs to a *tail-recursive* function.  Mutual recursion (`f` calls `g`, which calls `f`) also creates tail calls, and TCO applies there too, but detecting it requires tracking which functions are in the current call chain.  The simple `is_tail_call` detector below only checks for self-recursion.  A production compiler needs to handle the mutual case, which is why Scheme's TCO guarantee covers all proper tail calls, not just self-calls.

---

### Multiple Choice

Which optimization is UNSAFE to apply to `result = print("hello") or True`?

[(X)] Replacing `print("hello")` with its constant value (it returns `None`)
[( )] Evaluating `True` at compile time
[( )] Keeping the original expression unchanged
[( )] All of the above

---

Constant propagation extends the environment with `{x: 3}` when `let x = 3`.  Why is it safe to propagate this constant throughout the body?

[( )] Because x is an integer
[(X)] Because `let` creates an immutable binding: x's value cannot change in the body
[( )] Because 3 is small enough to inline
[( )] Because the compiler checked for side effects

---

A tail call optimization converts a tail-recursive call into a loop at compile time.  What benefit does this provide?

[( )] Faster garbage collection
[(X)] Constant stack space instead of O(n) stack frames: enables deep or infinite recursion without stack overflow
[( )] Smaller bytecode
[( )] Type safety

---

### Exercises

##### Exercise 1: Fix Comparison Folding (15 min)

Extend `fold_and_propagate` from Model 2 to handle comparison operators (`>`, `<`, `>=`, `<=`, `==`, `!=`) and boolean operators (`and`, `or`, `not`).  Test: `if (2 > 1) then 42 else 0` should fold to `42`.

##### Exercise 2: Strength Reduction (20 min)

**Strength reduction** replaces expensive operations with cheaper ones:
- `x * 2` -> `x + x` (addition is faster than multiplication on some CPUs)
- `x * 4` -> `x << 2` (shift is faster than multiplication by a power of 2)
- `x / 2` -> `x >> 1` (for integer division)

Implement `strength_reduce(node)` as a tree transformation.  Test on `y * 8` and `z / 4`.

##### Exercise 3: Dead Code Elimination (20 min)

Write `eliminate_dead_code(node, live_vars: set)` that removes let-bindings whose names are never used in the body:

```
let x = expensive_computation() in 42
-> 42  (if x is never used)
```

But be careful: only eliminate if the binding expression is pure!

##### Exercise 4: Optimization Pipeline (25 min)

Combine multiple passes into a pipeline:

```python
def optimize(node):
    node = fold_and_propagate(node, {})
    node = eliminate_dead_code(node, collect_live_vars(node))
    node = inline(node, fn_env)
    node = fold_and_propagate(node, {})  # run again after inlining!
    return node
```
@LIA.eval(`["main.py"]`, `none`, `python3 main.py`)
Test the pipeline on a program that contains all four optimization opportunities.  Show before and after.

##### Exercise 5: Mini TCO (30 min, harder)

Add tail call optimization to your Mini interpreter:
1.  Write `is_tail_position(node, current_fn_name)` that returns True if a node is a tail call
2.  Modify your evaluator: when a tail call is detected, instead of recursing, update the parameters and loop (use a `while True` loop in the evaluator)
3.  Demonstrate: `fact(10000)` works without stack overflow after TCO, but fails without it

---

### Reflection

1.  **Safety vs. speed**: Every optimization in this module requires a safety proof ("this is valid because...").  What does this tell you about the relationship between semantics and optimization?  Could you optimize a language you don't have a formal semantics for?

2.  **Optimization order matters**: We ran constant folding *after* inlining.  Why?  Could you run them in the opposite order and get the same result?  What does this say about the design of an optimization pipeline?

3.  **Your final project**: Which of these optimizations would you add to your Mini language?  Which would require the most implementation effort?  Pick one and sketch the implementation.

---

### Further Reading

- **"Engineering a Compiler"**: Cooper & Torczon, Chapters 8-10: the canonical compiler optimization textbook
- **"Compilers: Principles, Techniques, and Tools"**: Aho, Lam, Sethi, Ullman (Dragon Book): Chapters 9-10
- **"Compiling with Continuations"**: Appel: how CPS enables many optimizations uniformly
- **GCC optimization flags**: `gcc -O2` enables ~50 optimizations; the manual lists them all
- **LLVM passes**: each LLVM optimization is a separate pass; the source code is readable: https://llvm.org/docs/Passes.html
- **"Hacker's Delight"**: Henry Warren: arithmetic tricks behind strength reduction
