# The Compilation and Linking Process
<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://github.com/BillJr99/Ursinus-CS374-Fall2026/blob/gh-pages/_pages/Activities/liascript-compiler-linker.md

import: https://raw.githubusercontent.com/liascript/CodeRunner/master/README.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

# The Compilation and Linking Process

> **Opening hook:** Think of translating a novel from French to English, but the book is enormous so several translators each handle a separate chapter independently. Each translator (the **compiler**) converts their chapter from French to English without knowing exactly what page numbers the other chapters will land on — they leave placeholders like "see Chapter 7" wherever they cross-reference another chapter. When all the translated chapters are done, an editor (the **linker**) gathers them, resolves every placeholder to a real page number, and stitches them into one coherent book. The final book is your executable: one continuous object where every function call points to the exact address of the function it calls.

## Learning Goals

By the end of this activity, you will be able to:

- Enumerate and describe each stage of the compilation pipeline — preprocessing, parsing, semantic analysis, code generation, assembly, and linking — and identify the input and output artifact of each stage
- Explain the role of symbol tables and relocation records in the object-file format, and trace how the linker resolves external references across separately compiled modules
- Distinguish static linking from dynamic linking, and reason about the tradeoffs of each for program startup time, binary size, and library versioning
- Map the compilation pipeline stages onto your course interpreter project, identifying which stages you have already implemented and which stages a full compiler would add

**CS374: Principles of Programming Languages — Week 9**

**References:** Compilers (Dragon Book) Ch. 2 and Ch. 8

---

> **Before You Begin**
>
> This activity assumes you are comfortable with:
>
> - Writing and calling Python functions; understanding what a **stack frame** is (local variables, return address)
> - Basic familiarity with how your interpreter project parses source code into an AST and evaluates it
> - The concept of a **dictionary** (hash map) as a data structure — symbol tables are essentially dictionaries
> - What a **memory address** is: an integer that identifies a location in the computer's RAM
>
> You do *not* need prior knowledge of assembly language or operating systems. All machine-level concepts are introduced here via Python simulations.

---

## Directions and Group Roles

This is a **POGIL (Process-Oriented Guided Inquiry Learning)** activity. Work in groups of 3–4. Each person takes a role:

| Role | Responsibility |
|------|----------------|
| **Manager** | Keeps the group on task; ensures everyone participates |
| **Recorder** | Writes down the group's answers to Critical Thinking Questions |
| **Presenter** | Shares the group's findings with the class |
| **Reflector** | Monitors the group process; leads the reflection at the end |

**Learning Objectives:** By the end of this activity you will be able to:

1. Describe the stages of the compilation pipeline from source code to executable.
2. Explain what bytecode is and how a stack-based virtual machine executes it.
3. Define symbol tables, object files, and the role of the linker.
4. Distinguish between static and dynamic linking.
5. Connect Python's import system to the concept of dynamic linking.

---

## Model 1: The Compilation Pipeline

**Intuition:** Your source code is just a string of characters — the computer has no idea what `def add(x, y): return x + y` means until something translates it into instructions a CPU can execute. That translation happens in a pipeline of stages, each with a well-defined input and output. By the time we reach the end of the pipeline, we have gone from "English-like text" to "numbered machine operations." Python exposes this pipeline through its built-in tools so you can watch each stage happen in real time. Notice that even an interpreted language like Python goes through compilation — it just compiles to *bytecode* (instructions for a software CPU) rather than native machine code.

A compiler translates source code through several stages before producing executable code. In a traditional C/C++ compiler (like GCC or LLVM), those stages are:

1. **Lexical Analysis (Scanning):** Convert characters to tokens.
2. **Parsing:** Build an Abstract Syntax Tree (AST).
3. **Semantic Analysis:** Type-check and annotate the AST.
4. **Intermediate Code Generation:** Produce an IR (e.g., three-address code).
5. **Optimization:** Improve the IR.
6. **Code Generation:** Emit assembly or machine code.
7. **Linking:** Combine object files into an executable.

Python exposes these stages through its `compile()`, `ast`, and `dis` modules, letting us observe them directly.

```python
import dis
import ast

# Stage 1: Source code
source = """
def add(x, y):
    return x + y

result = add(3, 4)
print(result)
"""

# Stage 2: Parse to AST
tree = ast.parse(source)
print("=== AST dump (first 300 chars) ===")
print(ast.dump(tree, indent=2)[:300] + "...")

# Stage 3: Compile to bytecode
code = compile(source, "<string>", "exec")
print("\n=== Bytecode for 'add' function ===")
for const in code.co_consts:
    if hasattr(const, 'co_name') and const.co_name == 'add':
        dis.dis(const)
        break

# Stage 4: Execute
exec(code)
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

> **Watch out!** "Python is interpreted, not compiled" is a common but misleading claim. Python *does* compile your source code — to bytecode — every time you run a `.py` file. The difference from C is that Python's target is a *software* CPU (the CPython VM) rather than a *hardware* CPU. The `.pyc` files you may have seen in `__pycache__/` are the cached bytecode output of this compilation step. Saying Python is "interpreted" means the bytecode is executed by a software interpreter, not that compilation never happens.

**Critical Thinking Questions (CTQs) — Model 1**

1. List the stages of compilation shown in the code comments above (Stage 1 through Stage 4). How do they map onto the seven stages described in the introduction?

2. What does "compile to bytecode" mean? In your own words, describe what bytecode is and why it is produced instead of machine code directly.

3. Python bytecode runs on the CPython interpreter (a virtual machine), while C code compiles to native machine code that runs on a CPU. What is the key difference? What is the tradeoff in portability versus performance?

4. What does `dis.dis()` show you? Look at the output: what information does each line of the disassembly contain?

---

## Model 2: Python Bytecode in Depth

**Intuition:** Imagine evaluating `a * b + c` on an old-fashioned desk calculator with a single display window. You must press buttons in a specific order: recall `a`, recall `b`, press multiply (the result sits in the display), recall `c`, press add. The display is a stack with one slot — each operation pops its inputs from the display and pushes its result back. CPython's virtual machine works the same way, just with a deeper stack. Every expression in your Python program gets compiled down to a sequence of these push/pop operations (LOAD, BINARY_OP, RETURN) that any first-year CS student could execute by hand given the instruction list.

CPython uses a **stack-based virtual machine** to execute bytecode. Every operation either pushes values onto a stack, pops them off, or both. Understanding the stack machine helps you understand how any expression is evaluated at the lowest level.

The bytecode for `a * b + c` follows this sequence of stack operations:

```
LOAD_FAST a       → stack: [a]
LOAD_FAST b       → stack: [a, b]
BINARY_MULTIPLY   → stack: [a*b]
LOAD_FAST c       → stack: [a*b, c]
BINARY_ADD        → stack: [a*b+c]
RETURN_VALUE      → returns a*b+c, stack: []
```

```python
import dis
import opcode

# A simple function to disassemble
def compute(a, b, c):
    return a * b + c

print("=== Bytecode for compute(a, b, c): a*b + c ===")
dis.dis(compute)

print("\n=== Bytecode details ===")
code = compute.__code__
print(f"co_varnames: {code.co_varnames}")   # local variable names
print(f"co_consts:   {code.co_consts}")     # literal constants
print(f"co_argcount: {code.co_argcount}")   # number of arguments
print(f"co_stacksize:{code.co_stacksize}")  # max stack depth needed

# Trace execution manually:
# LOAD_FAST a   → stack: [a]
# LOAD_FAST b   → stack: [a, b]
# BINARY_MULTIPLY → stack: [a*b]
# LOAD_FAST c   → stack: [a*b, c]
# BINARY_ADD    → stack: [a*b+c]
# RETURN_VALUE  → returns a*b+c

print("\nCompute(3, 4, 5) =", compute(3, 4, 5))
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

**Critical Thinking Questions (CTQs) — Model 2**

1. CPython uses a stack-based virtual machine. When `LOAD_FAST a` executes, what happens to the stack? Trace through the full execution of `compute(2, 3, 4)` step by step, showing the stack contents after each instruction.

2. Why is a stack a natural data structure for expression evaluation? Think about how postfix (Reverse Polish Notation) notation works and how it relates to what you see here.

3. The code object attribute `co_stacksize` tells CPython how much stack space to pre-allocate. How would a compiler determine the required stack size for a function? (Hint: think about the maximum stack depth during execution.)

4. A **register-based** architecture (like a real CPU or the Dalvik VM used in early Android) uses a fixed set of named registers instead of a stack. What would the instructions for `a * b + c` look like in a register-based design? What is one advantage of each approach?

---

## Model 3: Object Files and Symbol Tables

**Intuition:** When your team splits a large project across multiple files and each person compiles their own file independently, the compiler cannot know the final addresses of functions defined in *other* files — those files haven't been compiled yet, or might not even exist. So the compiler produces an **object file** that is like a translated chapter with blanks left wherever a cross-reference to another chapter belongs. The object file also ships a **symbol table** — a two-column list: "here is what I *define* (with its address)" and "here is what I *need* but didn't define (blank for now)." The linker reads all these lists and fills in every blank.

When a compiler processes a single source file, it produces an **object file** (`.o` on Linux/Mac, `.obj` on Windows). An object file contains:

- **Machine code** (or bytecode) for the functions defined in that file.
- A **symbol table** listing every name the file *defines* (exports) and every name it *references* but does not define (imports).

The symbol table is the key data structure that enables separate compilation: you can compile `math.c` and `main.c` independently, then combine them later.

```python
from dataclasses import dataclass, field
from typing import Optional

@dataclass
class Symbol:
    name: str
    defined: bool        # True = defined here; False = referenced but not defined
    value: Optional[int] = None  # address/offset (None if undefined)
    exported: bool = True  # visible to other modules

@dataclass
class ObjectFile:
    name: str
    symbols: dict = field(default_factory=dict)
    code: list = field(default_factory=list)   # simulated instructions
    
    def define(self, name: str, value: int, exported: bool = True):
        self.symbols[name] = Symbol(name, defined=True, value=value, exported=exported)
    
    def reference(self, name: str):
        if name not in self.symbols:
            self.symbols[name] = Symbol(name, defined=False)
    
    def undefined_refs(self):
        return [s for s in self.symbols.values() if not s.defined]
    
    def exported_symbols(self):
        return [s for s in self.symbols.values() if s.defined and s.exported]

# Simulate math.o: defines add, mul; references nothing
math_obj = ObjectFile("math.o")
math_obj.define("add", 0x1000)
math_obj.define("mul", 0x1020)

# Simulate main.o: references add and mul from math.o
main_obj = ObjectFile("main.o")
main_obj.define("main", 0x2000)
main_obj.reference("add")   # from math.o
main_obj.reference("mul")   # from math.o
main_obj.reference("printf")  # from libc — still unresolved at this stage

print("math.o exports:", [s.name for s in math_obj.exported_symbols()])
print("main.o undefined refs:", [s.name for s in main_obj.undefined_refs()])
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

> **Watch out!** An undefined reference in an object file is **not** a compile-time error. The C compiler happily produces `main.o` even though it references `printf` without seeing its definition — it just records the reference in the symbol table. The error only fires at **link time**, when the linker discovers no object file or library provides the definition. This is why you can get "successful" compilation but a failing `gcc` invocation: the compile step passed but the link step failed.

**Critical Thinking Questions (CTQs) — Model 3**

1. What is a **symbol table**? What two kinds of information does it record for each symbol, according to the `Symbol` dataclass above?

2. What is the difference between a *defined* symbol and a *referenced* symbol? Give a concrete example: if `main.c` calls `sqrt()` from the math library, which file has `sqrt` as defined, and which file has it as referenced?

3. After compiling `main.c` to `main.o` (but *before* linking), `printf` appears as an undefined reference. Why? Is this an error at compile time? When must it be resolved?

4. The `ObjectFile` class has an `exported` flag on each symbol. What does it mean for a symbol to be *not exported* (i.e., `exported=False`)? In C, what keyword makes a function private to a translation unit?

---

## Model 4: Linking — Resolving Symbols

**Intuition:** The linker is like a fact-checker working through every "see Chapter 7, page X" placeholder in the assembled manuscript. It builds a master index (the global symbol table) from all the chapter-level indexes, then walks through every placeholder and writes in the correct page number. If any placeholder references a chapter that was never submitted — say, `printf` from the C library was never included — the fact-checker stops and reports an error: "undefined reference." This is the linker error you have probably seen when you forgot to link a library (`-lm` for math, for example). The linker *refuses* to produce the book until every cross-reference is resolved.

The **linker** takes multiple object files, merges their symbol tables, resolves all undefined references, and assigns final addresses. If any symbol is still undefined after processing all object files (and any requested libraries), the linker reports an error and refuses to produce an executable.

```python
from dataclasses import dataclass, field
from typing import Optional

@dataclass
class Symbol:
    name: str
    defined: bool
    value: Optional[int] = None
    obj_file: str = ""

@dataclass
class Linker:
    object_files: list = field(default_factory=list)
    symbol_table: dict = field(default_factory=dict)  # global view
    base_address: int = 0x4000
    errors: list = field(default_factory=list)
    
    def add_object(self, name: str, exports: list, references: list):
        self.object_files.append(name)
        for sym_name, addr in exports:
            if sym_name in self.symbol_table and self.symbol_table[sym_name].defined:
                self.errors.append(f"Duplicate symbol: {sym_name}")
            else:
                self.symbol_table[sym_name] = Symbol(sym_name, True, addr, name)
        for ref in references:
            if ref not in self.symbol_table:
                self.symbol_table[ref] = Symbol(ref, False, obj_file=name)
    
    def link(self):
        unresolved = [s for s in self.symbol_table.values() if not s.defined]
        if unresolved:
            for sym in unresolved:
                self.errors.append(f"Undefined reference: '{sym.name}' (needed by {sym.obj_file})")
        if self.errors:
            print("LINK ERRORS:")
            for e in self.errors:
                print(f"  {e}")
            return False
        print("Link successful!")
        print("Symbol table:")
        for name, sym in sorted(self.symbol_table.items()):
            print(f"  {name:20} @ 0x{sym.value or 0:04x}  ({sym.obj_file})")
        return True

linker = Linker()
linker.add_object("math.o",
    exports=[("add", 0x1000), ("mul", 0x1020)],
    references=[])
linker.add_object("main.o",
    exports=[("main", 0x2000)],
    references=["add", "mul"])  # printf still missing — simulate no libc
linker.link()
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

**Critical Thinking Questions (CTQs) — Model 4**

1. What does "linking" accomplish? In one or two sentences, describe the linker's job using the vocabulary from this model (symbol table, undefined references, object files).

2. The `link()` method above reports a link error because `printf` is never added as an export. In a real build, how would you fix this? What does "linking against libc" mean in practice?

3. What is a "duplicate symbol" error, and when does it occur? Give a realistic scenario in which two object files might accidentally define the same symbol name.

4. **Static linking** copies library code directly into the executable at link time. **Dynamic linking** leaves references unresolved until the program is loaded or run. List one advantage and one disadvantage of each approach. (Think about: executable size, memory usage when multiple programs use the same library, and ease of updating the library.)

---

## Model 5: Static vs. Dynamic Linking and Python's Import System

**Intuition:** Static linking is like photocopying the relevant pages of a reference book into your own report — every reader of your report gets a self-contained document, but your report is bulkier and cannot benefit from corrections made to the original book later. Dynamic linking is like writing "see the library's copy of *Reference Book X*, page 47" — your report is slim, multiple readers share the same library book, and if the library updates its copy everyone benefits automatically. Python's `import` system is the clearest high-level example of dynamic linking: modules are found and loaded on demand, cached so they are only loaded once, and swappable by inserting a replacement into `sys.modules`.

In static linking, all dependencies are baked into the executable at build time. In dynamic linking, the operating system's **dynamic linker/loader** (e.g., `ld.so` on Linux) resolves symbol references at load time or even at first use (lazy binding). Python's `import` statement is a high-level version of dynamic linking: Python searches `sys.path` for modules, loads them on demand, and caches them in `sys.modules`.

| Concept | OS Dynamic Linking | Python Import |
|---------|-------------------|---------------|
| Search path | `LD_LIBRARY_PATH` | `sys.path` |
| Loaded library cache | `ld.so` internal table | `sys.modules` |
| Lazy loading | Lazy binding (PLT/GOT) | Import on first `import` statement |
| Injecting a fake library | `LD_PRELOAD` | Inserting into `sys.modules` |

```python
import sys
import importlib
import os

# Python's import system = dynamic linking
# sys.path is the "library search path" (like LD_LIBRARY_PATH)
print("Python module search path (sys.path):")
for p in sys.path[:5]:
    print(f"  {p}")

# Finding a module = symbol lookup in dynamic library
spec = importlib.util.find_spec("math")
if spec:
    print(f"\nmath module found at: {spec.origin}")
    print(f"math module loader: {type(spec.loader).__name__}")

# Demonstrate lazy loading: the module isn't loaded until you import it
print(f"\n'json' in sys.modules before import: {'json' in sys.modules}")
import json
print(f"'json' in sys.modules after import:  {'json' in sys.modules}")

# sys.modules is the "dynamic linker cache" — modules loaded once
import math as m1
import math as m2
print(f"\nm1 is m2 (same object, loaded once): {m1 is m2}")

# Simulating LD_PRELOAD: inject a module into sys.modules
class FakeMath:
    pi = 3.0  # "wrong" value
    def sqrt(self, x): return x ** 0.5

sys.modules['math_fake'] = FakeMath()
import importlib
fake = importlib.import_module('math_fake')
print(f"\nFakeMath.pi = {fake.pi}")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

**Critical Thinking Questions (CTQs) — Model 5**

1. How is Python's `sys.path` analogous to the operating system's `LD_LIBRARY_PATH`? What would happen if you removed all entries from `sys.path`?

2. What role does `sys.modules` play? How is it analogous to the dynamic linker's loaded-library cache? Why is it important that `import math` returns the *same object* no matter how many times you call it?

3. **Lazy loading** means a module is not imported until the `import` statement is actually reached during execution (not when the program starts). When would lazy loading be beneficial? Can you think of a scenario where eager loading (loading everything at startup) might be preferable?

4. The code above injects a `FakeMath` class into `sys.modules['math_fake']`. On Linux, `LD_PRELOAD` allows you to inject a shared library that overrides symbols from other libraries. What **security concern** does this technique raise in both contexts? How do operating systems and language runtimes defend against abuse of this mechanism?

---

## Multiple Choice

**Question 1**

[[MC]] During compilation, what does a **symbol table** contain?

[( )] The names of all variables, guaranteed to be unique across all files
[(X)] Names and addresses of defined and referenced symbols in a translation unit
[( )] The machine-code addresses of all function calls in the final executable
[( )] A mapping from variable names to their data types

---

**Question 2**

[[MC]] CPython uses a **stack-based** virtual machine. Which of the following best describes how a binary operation like `BINARY_ADD` works in this model?

[( )] It reads two named registers, adds them, and writes the result to a third register
[(X)] It pops two values from the top of the stack, adds them, and pushes the result back
[( )] It looks up both operands by name in the local variable table and stores the sum
[( )] It increments a single accumulator register by the value on top of the stack

---

**Question 3**

[[MC]] Which of the following is the most accurate distinction between **static linking** and **dynamic linking**?

[( )] Static linking is used only for C programs; dynamic linking is used only for interpreted languages
[( )] In static linking, the linker checks for undefined symbols but does not resolve them until runtime
[(X)] In static linking, library code is copied into the executable at build time; in dynamic linking, references are resolved at load time or runtime by the OS loader
[( )] Dynamic linking is always faster at runtime because the library code is pre-compiled

---

**Question 4**

[[MC]] What does `dis.dis(func)` display?

[( )] The source code of `func` with syntax highlighting
[( )] A call graph showing which functions `func` calls
[(X)] The CPython bytecode instructions that implement `func`, including offsets, opcodes, and operands
[( )] The compiled machine code (assembly) that the CPU will execute

---

## Exercises

**Exercise 1: Implement a Simple Stack-Based Virtual Machine**

Write a `SimpleVM` class with a Python `list` as its stack and methods for the following opcodes: `PUSH(val)`, `POP()`, `ADD()`, `MUL()`, `DUP()` (duplicate top of stack), and `PRINT()` (print and discard top of stack).

Then, "compile" the expression `(3 + 4) * 2` to a list of instructions and execute them using your VM. Verify that the final printed result is `14`.

**Starter code:**

```python
class SimpleVM:
    def __init__(self):
        self.stack = []
    
    def PUSH(self, val):
        # TODO: push val onto self.stack
        pass
    
    def POP(self):
        # TODO: pop and return the top value
        pass
    
    def ADD(self):
        # TODO: pop two values, push their sum
        pass
    
    def MUL(self):
        # TODO: pop two values, push their product
        pass
    
    def DUP(self):
        # TODO: duplicate the top of the stack
        pass
    
    def PRINT(self):
        # TODO: pop and print the top value
        pass
    
    def run(self, program):
        for instr, *args in program:
            getattr(self, instr)(*args)

# "Compile" (3 + 4) * 2 to instructions
program = [
    ("PUSH", 3),
    ("PUSH", 4),
    ("ADD",),
    ("PUSH", 2),
    ("MUL",),
    ("PRINT",),
]

vm = SimpleVM()
vm.run(program)
# Expected output: 14
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

**Exercise 2: Add a Relocation Table to ObjectFile**

In a real object file, the compiler doesn't know the final addresses of symbols in other modules. It leaves **relocations**: placeholders in the code that the linker must patch. Extend the `ObjectFile` class from Model 3 to track a relocation table — a list of `(instruction_offset, symbol_name)` pairs.

Then implement a `patch(symbol_table)` method on `ObjectFile` that iterates over the relocations and prints what address would be written at each offset once the linker has resolved all symbols.

**Starter code:**

```python
from dataclasses import dataclass, field
from typing import Optional

@dataclass
class Symbol:
    name: str
    defined: bool
    value: Optional[int] = None
    exported: bool = True

@dataclass
class ObjectFile:
    name: str
    symbols: dict = field(default_factory=dict)
    relocations: list = field(default_factory=list)  # NEW: list of (offset, sym_name)
    
    def define(self, name: str, value: int, exported: bool = True):
        self.symbols[name] = Symbol(name, defined=True, value=value, exported=exported)
    
    def reference(self, name: str):
        if name not in self.symbols:
            self.symbols[name] = Symbol(name, defined=False)
    
    def add_relocation(self, offset: int, symbol_name: str):
        # TODO: record that at byte `offset` in this object file's code,
        # the address of `symbol_name` must be patched in
        pass
    
    def patch(self, global_symbol_table: dict):
        # TODO: for each (offset, sym_name) in self.relocations,
        # look up sym_name in global_symbol_table and print:
        # "Patch offset 0x{offset:04x}: write address 0x{addr:04x} (symbol '{sym_name}')"
        pass

# Test
math_obj = ObjectFile("math.o")
math_obj.define("add", 0x1000)
math_obj.define("mul", 0x1020)

main_obj = ObjectFile("main.o")
main_obj.define("main", 0x2000)
main_obj.reference("add")
main_obj.reference("mul")
main_obj.add_relocation(0x2010, "add")  # at offset 0x2010, need address of 'add'
main_obj.add_relocation(0x2018, "mul")  # at offset 0x2018, need address of 'mul'

# Build global symbol table from math.o
global_syms = {**math_obj.symbols, **main_obj.symbols}
main_obj.patch(global_syms)
# Expected:
# Patch offset 0x2010: write address 0x1000 (symbol 'add')
# Patch offset 0x2018: write address 0x1020 (symbol 'mul')
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

**Exercise 3: Implement a DynamicLinker Class**

Implement a `DynamicLinker` class that simulates the runtime behavior of a dynamic linker. It should support:

- `load_library(name, exports)`: Register a library by name with a dict mapping symbol names to addresses.
- `resolve(symbol)`: Search all loaded libraries for the symbol and return its address, or raise an error if not found.
- `show_loaded()`: Print all currently loaded libraries and their exported symbols.

Test it by loading a simulated `libmath.so` and `libc.so`, then resolving several symbols.

**Starter code:**

```python
class DynamicLinker:
    def __init__(self):
        self.libraries = {}  # name -> {symbol: address}
    
    def load_library(self, name: str, exports: dict):
        # TODO: store the library's exports in self.libraries
        pass
    
    def resolve(self, symbol: str) -> int:
        # TODO: search self.libraries for the symbol
        # Return its address if found
        # Raise a RuntimeError if not found in any library
        pass
    
    def show_loaded(self):
        # TODO: print each loaded library and its exported symbols
        pass

# Test
dl = DynamicLinker()
dl.load_library("libmath.so", {"sqrt": 0x7f001000, "pow": 0x7f001040, "log": 0x7f001080})
dl.load_library("libc.so",    {"printf": 0x7f002000, "malloc": 0x7f002200, "free": 0x7f002300})

dl.show_loaded()

print("\nResolving symbols:")
for sym in ["printf", "sqrt", "malloc", "log"]:
    addr = dl.resolve(sym)
    print(f"  {sym:10} -> 0x{addr:08x}")

# Try resolving an undefined symbol
try:
    dl.resolve("undefined_func")
except RuntimeError as e:
    print(f"\nExpected error: {e}")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

**Exercise 4: Walk an AST to Find All Function Calls**

Use Python's `ast` module to walk an AST and collect all `Call` nodes, printing the name of each function being called and the line number. This simulates the work a compiler does when it encounters a call instruction and must generate a reference to the callee's symbol.

**Starter code:**

```python
import ast

source = """
import math

def hypotenuse(a, b):
    return math.sqrt(a**2 + b**2)

def area_of_circle(r):
    return math.pi * r**2

def main():
    h = hypotenuse(3, 4)
    a = area_of_circle(5)
    print(f"Hypotenuse: {h}, Area: {a}")
    result = sorted([3, 1, 2], key=lambda x: -x)
    print(result)

main()
"""

tree = ast.parse(source)

print("Function calls found (simulating symbol reference collection):")
print(f"{'Line':>5}  {'Call'}")
print("-" * 40)

for node in ast.walk(tree):
    if isinstance(node, ast.Call):
        # TODO: determine the name of the function being called
        # Hint: node.func may be an ast.Name (func.id) or ast.Attribute (func.attr)
        # Print the line number (node.lineno) and the call name
        pass

# Expected output should include calls to:
# math.sqrt, math.pi (attribute access), hypotenuse, area_of_circle,
# print (twice), sorted, main
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

---

## Reflection

> **Prompt:** "Compilation is a pipeline: scan → parse → semantic analysis → optimization → code generation → link. After exploring Python's bytecode and a simulated linker, which stage surprises you most, and why?"

Write 3–4 sentences. Consider: What did you assume was simple that turns out to be complex? What new appreciation do you have for language runtime design? How do these concepts change the way you think about writing programs?

---

## Further Reading

- **Compilers: Principles, Techniques, and Tools** (Aho, Lam, Sethi, Ullman — the "Dragon Book"), Chapter 2: A Simple Syntax-Directed Translator
- **Dragon Book**, Chapter 8: Intermediate Code Generation
- [Python `dis` — Disassembler for Python bytecode](https://docs.python.org/3/library/dis.html) — official documentation
- [Python `ast` — Abstract Syntax Trees](https://docs.python.org/3/library/ast.html) — official documentation
- **Ian Lance Taylor's Linkers blog series** — a deep, technical walkthrough of how linkers work in practice (search "Ian Lance Taylor linkers blog")
- **"Static and Dynamic Linking" video:** https://youtube.com/watch?v=UdMRcJwvWIY
- [CPython internals: how bytecode is executed](https://devguide.python.org/internals/compiler/) — CPython developer's guide
- **"Linkers and Loaders"** by John Levine — a book-length treatment of everything from object file formats to dynamic linking
