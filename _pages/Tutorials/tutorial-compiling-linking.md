<!--
author:   CS374 Course Staff
email:    
version:  0.0.1
language: en
narrator: US English Female
comment:  From source to executable — the complete compile-link pipeline, ELF/EXE format, object files, and how interpreted languages differ.
import:   https://raw.githubusercontent.com/liaScript/mermaid_template/master/README.md
link:     https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.3.0/css/all.min.css
-->

# From Source to Executable: Compiling, Linking, and the ELF Format

## Learning Goals

By the end of this tutorial, you will have:

- Traced a C source file through all four pipeline stages (preprocessor, compiler, assembler, linker) using `gcc -save-temps` and inspected each intermediate artifact
- Read an ELF binary's section headers with `readelf` and identified the `.text`, `.data`, `.rodata`, and `.bss` sections
- Explained the difference between static and dynamic linking and predicted which symbols will be unresolved at compile time vs. resolved at load time
- Contrasted the compiled pipeline with how interpreted languages (Python, JavaScript) execute source code at runtime
- Applied this knowledge to explain why a bytecode VM sits between a tree-walking interpreter and a native compiler in the execution-strategy spectrum

> **"Every program you run went through a pipeline you've never seen."**
>
> When you type `gcc hello.c -o hello`, a remarkable chain of tools transforms text into a binary that the operating system can map directly into memory and execute. This tutorial traces that chain step by step — from C source to ELF binary — and then contrasts it with how interpreted languages (Python, JavaScript) work instead.

---

## Part 0: The Big Picture

The complete pipeline from C source to running process:

```
Source (.c)
    │
    ▼  C preprocessor (cpp)
Preprocessed (.i)     — macros expanded, includes substituted
    │
    ▼  C compiler (cc1)
Assembly (.s)         — human-readable machine code mnemonics
    │
    ▼  Assembler (as)
Object file (.o)      — machine code + symbol table + relocation records
    │
    ▼  Linker (ld)
Executable (ELF/EXE)  — all objects combined, addresses resolved
    │
    ▼  OS loader
Process               — loaded into virtual memory, started at entry point
```

```bash
# See all intermediate files (GCC's -save-temps flag):
gcc -save-temps hello.c -o hello
ls *.i *.s *.o hello    # all four stages preserved
```

```bash
# Or step by step manually:
gcc -E hello.c -o hello.i      # preprocess only
gcc -S hello.i -o hello.s      # compile to assembly
gcc -c hello.s -o hello.o      # assemble to object file
gcc hello.o -o hello           # link to executable
```

---

## Part 1: The Preprocessor

The C preprocessor (`cpp`) handles `#include`, `#define`, `#ifdef`, and `#pragma` — it's a text substitution engine that runs *before* the compiler sees any code.

```c
/* hello.c */
#include <stdio.h>      /* textually paste stdio.h here */
#define GREETING "Hello, World!"

int main() {
    printf(GREETING "\n");   /* GREETING replaced by string literal */
    return 0;
}
```

After preprocessing (`gcc -E hello.c`), `#include <stdio.h>` is replaced by thousands of lines of declarations from `/usr/include/stdio.h`, and `GREETING` is replaced by `"Hello, World!"`.

**Key preprocessor directives:**

| Directive | Effect |
|-----------|--------|
| `#include <file>` | Insert system header (searches include path) |
| `#include "file"` | Insert local header (searches current directory first) |
| `#define NAME val` | Text substitution macro |
| `#define FUNC(x) ((x)*(x))` | Function-like macro (dangerous! double-eval) |
| `#ifdef / #ifndef` | Conditional compilation |
| `#pragma once` | Include guard (modern, portable alternative to `#ifndef HEADER_H_`) |

**Why preprocessing matters for language design:** The C preprocessor is essentially a *macro system* at the text level — the same problem as unhygienic macros in Lisp. Languages that adopted later (Rust, D) replaced it with hygienic macro systems that operate on AST nodes instead of text.

---

## Part 2: Assembly — The Compiler's Output

The compiler transforms C into **assembly language** — human-readable mnemonics for machine instructions:

```c
/* add.c */
int add(int a, int b) {
    return a + b;
}
```

Compiles to (`gcc -S -O0 add.c -o add.s` — no optimization):

```asm
add:
    pushq   %rbp              ; save caller's base pointer
    movq    %rsp, %rbp        ; set up our stack frame
    movl    %edi, -4(%rbp)    ; store parameter a on stack
    movl    %esi, -8(%rbp)    ; store parameter b on stack
    movl    -4(%rbp), %edx    ; load a into edx
    movl    -8(%rbp), %eax    ; load b into eax
    addl    %edx, %eax        ; eax = a + b (result in eax by convention)
    popq    %rbp              ; restore base pointer
    ret                       ; return (caller reads result from eax)
```

With optimization (`-O2`):

```asm
add:
    leal    (%rdi,%rsi), %eax  ; eax = a + b (one instruction!)
    ret
```

**The calling convention (System V AMD64 ABI):**
- Arguments: RDI, RSI, RDX, RCX, R8, R9 (first 6 integer args), then stack
- Return value: RAX (integer), XMM0 (floating point)
- Caller-saved: RAX, RCX, RDX, RSI, RDI, R8-R11
- Callee-saved: RBX, RSP, RBP, R12-R15

**The stack frame:**

```
High address
┌─────────────────────┐
│   caller's frame    │  ← RBP (after prologue)
├─────────────────────┤
│  return address     │  ← pushed by CALL instruction
├─────────────────────┤  ← RBP points here (our frame)
│  saved RBP          │  ← pushed by push %rbp
├─────────────────────┤
│  local variable a   │  ← -4(%rbp)
├─────────────────────┤
│  local variable b   │  ← -8(%rbp)
└─────────────────────┘  ← RSP (stack pointer)
Low address
```

**Key insight:** The call stack you see in debuggers is this structure. When a function returns, `ret` pops the return address from the stack and jumps to it — this is why stack overflow crashes programs (the stack pointer goes past the stack's memory limit).

---

## Part 3: Object Files and Symbol Tables

The assembler converts assembly to **object files** (`.o`) — binary files containing machine code but with *unresolved references* (symbols).

```bash
# Inspect an object file
nm hello.o          # list symbols: T = defined, U = undefined
objdump -d hello.o  # disassemble machine code
readelf -s hello.o  # detailed symbol table
```

An object file has multiple **sections**:

| Section | Contents |
|---------|----------|
| `.text` | Compiled machine code (read-only, executable) |
| `.data` | Initialized global variables (read-write) |
| `.bss` | Uninitialized global variables (just reserves size; zero-filled at load) |
| `.rodata` | Read-only data (string literals, const globals) |
| `.symtab` | Symbol table: names + their locations |
| `.rel.text` | Relocation records: "fix up this address when linking" |
| `.debug_*` | DWARF debug information (line numbers, variable names) |

**The symbol table** maps names to addresses (or marks them undefined):

```
Symbol table example for main.o that calls printf:
  T main       0x0000  (defined here, in .text at offset 0)
  U printf     -----   (undefined — must be resolved by linker)
```

**Relocation records** tell the linker "at byte offset X in .text, fill in the address of symbol Y":

```
Relocation:
  OFFSET        TYPE      SYMBOL
  0x15          R_X86_64_PLT32  printf
  # meaning: at offset 0x15 in .text, write the address of printf
```

---

## Part 4: The Linker — Combining Object Files

The **linker** (`ld`, usually invoked via `gcc`) takes multiple object files (and libraries) and produces an executable by:

1. **Merging sections**: All `.text` sections → one `.text` segment; all `.data` → one `.data` segment
2. **Symbol resolution**: For each `U` (undefined) symbol, find which other `.o` file defines it
3. **Relocation**: Fill in all the placeholder addresses with actual virtual addresses

```yaml
main.o:   defines main, uses printf (undefined)
libc.a:   contains printf.o which defines printf

Linker:
  1. Merge .text sections: main code + printf code
  2. Assign virtual addresses: .text starts at 0x401000
  3. Resolve: main's call to printf → patch with printf's address
  4. Output executable ELF with all addresses filled in
```

**Static vs Dynamic Linking:**

| | Static Linking | Dynamic Linking |
|-|----------------|-----------------|
| Libraries | Copied into executable | Referenced by name; loaded at runtime |
| Executable size | Larger (includes all library code) | Smaller (shared libraries on disk) |
| Startup | Faster (no runtime lookup) | Slightly slower (PLT/GOT overhead) |
| Updates | Recompile required | Library update takes effect immediately |
| Symbol | `.a` (archive) | `.so` (shared object) / `.dll` |

```bash
# See what dynamic libraries a program needs:
ldd /bin/ls
# linux-vdso.so.1 (virtual syscall library)
# libselinux.so.1 → /lib/x86_64-linux-gnu/libselinux.so.1
# libc.so.6 → /lib/x86_64-linux-gnu/libc.so.6
```

---

## Part 5: The ELF Format (Linux/macOS Executable)

**ELF** (Executable and Linkable Format) is the binary format used by Linux, macOS (Mach-O is similar), and most Unix systems. Windows uses **PE** (Portable Executable) format — structurally very similar.

```
ELF File Layout:
┌─────────────────────────────────┐
│  ELF Header (64 bytes)          │  magic number, arch, entry point address
├─────────────────────────────────┤
│  Program Header Table           │  describes segments (for OS loader)
│   LOAD segment 1: .text .rodata │  read+execute, maps to virtual address
│   LOAD segment 2: .data .bss    │  read+write
│   DYNAMIC segment               │  dynamic linking info
├─────────────────────────────────┤
│  .text section                  │  machine code
├─────────────────────────────────┤
│  .rodata section                │  string literals, const data
├─────────────────────────────────┤
│  .data section                  │  initialized globals
├─────────────────────────────────┤
│  .bss section                   │  (just a size; zero-filled at load)
├─────────────────────────────────┤
│  .symtab / .strtab              │  symbol table (stripped in release)
├─────────────────────────────────┤
│  .debug_info, .debug_line       │  DWARF debug info (if -g was used)
├─────────────────────────────────┤
│  Section Header Table           │  metadata about each section
└─────────────────────────────────┘
```

**Reading an ELF file:**

```bash
# The "magic number" — all ELF files start with these 4 bytes:
xxd hello | head -1
# 7f 45 4c 46  → \x7f E L F

# Full ELF header:
readelf -h hello
# Magic:   7f 45 4c 46 02 01 01 00  ...
# Class:   ELF64 (64-bit)
# Data:    2's complement, little endian
# Type:    EXEC (executable file)
# Machine: Advanced Micro Devices X86-64
# Entry:   0x401060  ← this is where execution starts (_start, not main!)
# PH off:  64       ← program header table offset
# SH off:  ...      ← section header table offset

# Sections:
readelf -S hello
# [Nr] Name       Type    Address    Size
# [13] .text      PROGBITS 0x401060  0x...  AX (alloc+execute)
# [15] .rodata    PROGBITS 0x...     0x...  A  (alloc, read-only)
# [24] .data      PROGBITS 0x...     0x...  WA (write+alloc)
# [25] .bss       NOBITS   0x...     0x...  WA (zero-filled)

# Disassemble:
objdump -d hello | head -40
```

**The entry point is `_start`, not `main`!**

```asm
_start:
    ; Set up arguments for main
    ; argc is in rdi, argv on stack
    call main         ; call programmer's main()
    ; After main returns, call exit():
    mov  %eax, %edi   ; exit code = main's return value
    call exit
```

The C runtime (`crt0.o` / `crt1.o`) provides `_start`, which sets up argc/argv, calls `main`, and calls `exit`. This is automatically linked in by `gcc`.

---

## Part 6: The OS Loader — From File to Process

When you run `./hello`, the OS executes a **loader** (`execve` syscall on Linux) that:

1. **Reads the ELF header** to find segment info
2. **Maps segments into virtual memory** using `mmap`:
   - `.text` → read+execute (shared between multiple running instances)
   - `.data` + `.bss` → read+write (private per process)
3. **Maps the stack** (a region of anonymous memory)
4. **Loads shared libraries** (`.so` files listed in `.dynamic`) via the *dynamic linker* (`ld.so`)
5. **Resolves dynamic symbols** (fills in the Global Offset Table / Procedure Linkage Table)
6. **Transfers control** to the entry point (`_start`)

**Virtual Memory Layout (typical Linux x86-64 process):**

```
0xFFFFFFFFFFFFFFFF  (kernel space — not accessible from user mode)
0x00007FFFFFFFFFFF  ┐
                    │  Stack (grows downward)
                    │  [argc, argv, environment variables]
0x00007FFF_XXXX     ┘
                    
0x00007F00_XXXX     ┐
                    │  Shared libraries (.so files)
                    │  libc.so, ld.so, etc.
0x00007EFF_XXXX     ┘
                    
0x00600000          ┐
0x00601000          │  .data (initialized globals, read-write)
                    │  .bss  (zero-initialized globals)
0x00602000          ┘
                    
0x00400000          ┐
0x00401000          │  .text (code, read-only + executable)
                    │  .rodata (string literals, read-only)
0x00402000          ┘
```

```bash
# See a running process's memory map:
cat /proc/$(pgrep hello)/maps
# 00400000-00401000 r-xp  /path/to/hello  (code)
# 00601000-00602000 rw-p  /path/to/hello  (data)
# 7f...-7f...      r-xp  /lib/libc.so.6  (libc)
# 7ffe...-7fff...  rw-p  [stack]
```

---

## Part 7: The PE/EXE Format (Windows)

Windows executables use **PE** (Portable Executable) format — structurally similar to ELF but with different field names and conventions:

```
PE File Layout:
┌──────────────────────────────────┐
│  DOS Header (64 bytes)           │  starts with "MZ" magic number
│  DOS Stub ("This program cannot  │  tiny DOS program (prints error on DOS)
│  be run in DOS mode")            │
├──────────────────────────────────┤
│  PE Header ("PE\0\0" signature)  │  COFF header + optional header
│   Machine: IMAGE_FILE_MACHINE_   │  AMD64 or ARM64
│   Sections: 5                    │
│   Characteristics: EXECUTABLE    │
├──────────────────────────────────┤
│  Section Table                   │  metadata for each section
├──────────────────────────────────┤
│  .text                           │  machine code
│  .rdata                          │  read-only data (const, imports)
│  .data                           │  initialized globals
│  .bss / (folded into .data)      │  zero-initialized globals
│  .idata                          │  import directory (DLL imports)
│  .edata                          │  export directory
│  .rsrc                           │  resources (icons, strings, dialogs)
│  .reloc                          │  base relocation table
└──────────────────────────────────┘
```

**Differences from ELF:**
- The `MZ` header (from Mark Zbikowski, 1981) is a legacy artifact
- PE uses **DLL** (Dynamic Link Library) instead of `.so`; imports listed in `.idata`
- PE sections use different names: `.rdata` instead of `.rodata`, `.idata` for imports
- PE files have a **preferred base address** (0x400000 for EXE, 0x10000000 for DLL); ASLR randomizes this at load time

```bash
# On Linux, inspect a PE/EXE file with:
wine hello.exe    # run under Wine
objdump -p hello.exe | head -30    # PE header info
```

---

## Part 8: How Interpreted Languages Work Instead

When you run `python3 script.py`, no ELF is produced. Instead:

**Python's execution model:**

```
script.py
    │
    ▼  Python lexer/parser
AST (Abstract Syntax Tree)
    │
    ▼  Python compiler (compile())
Bytecode (.pyc)          ← cached in __pycache__/
    │
    ▼  CPython interpreter (ceval.c)
Values (Python objects)
```

```python  
import dis
import py_compile

def fib(n):
    if n <= 1: return n
    return fib(n-1) + fib(n-2)

# See CPython bytecode:
dis.dis(fib)
```

CPython bytecode output for `fib`:

```
  2           0 LOAD_FAST                0 (n)
              2 LOAD_CONST               1 (1)
              4 COMPARE_OP               1 (<=)
              6 POP_JUMP_IF_FALSE       12

  2           8 LOAD_FAST                0 (n)
             10 RETURN_VALUE

  3          12 LOAD_GLOBAL              0 (fib)
             14 LOAD_FAST                0 (n)
             16 LOAD_CONST               1 (1)
             18 BINARY_SUBTRACT
             20 CALL_FUNCTION            1
             ...
```

**Key differences from native compilation:**

| | Native (C/C++) | Interpreted (Python) |
|-|----------------|----------------------|
| Output | ELF/EXE binary | Bytecode (+ interpreter) |
| Type checks | At compile time | At runtime |
| Memory layout | Explicit (int = 4 bytes) | Boxed objects (int = 28 bytes!) |
| Dispatch | Direct function call | Dynamic lookup + vtable |
| Startup | Microseconds | ~50ms (import time) |
| Optimization | Full (LLVM passes) | Limited (peephole only) |
| Portability | Compile per arch | Bytecode = arch-independent |

**Why Python's `int` is 28 bytes:**

```python  
import sys
print(sys.getsizeof(42))     # 28 bytes — not 4!
print(sys.getsizeof(True))   # 28 bytes
print(sys.getsizeof("hi"))   # 51 bytes
# Python ints are Python objects with: refcount + type pointer + value
```

**JavaScript's JIT compilation:**

V8 (Chrome/Node.js) goes further:

```
JavaScript source
    │
    ▼  Parser
AST
    │
    ▼  Ignition (bytecode interpreter)
Bytecode            ← runs initially
    │
    ▼  TurboFan (JIT compiler, when "hot")
Native machine code ← recompiles frequently-executed functions
```

This is called **Just-In-Time (JIT) compilation**: start interpreted, profile which functions are hot, then compile those to native code. V8 can achieve 50–80% of C++ performance for some workloads.

---

## Part 9: Building a Mini Compiler (Putting It Together)

Here is a minimal C program that illustrates the full pipeline:

```c
/* mini_calc.c — compile with: gcc -O2 -o mini_calc mini_calc.c */
#include <stdio.h>

/* This function will be in .text */
static int add(int a, int b) {
    return a + b;
}

/* This string will be in .rodata */
static const char* greeting = "Result: %d\n";

/* This global will be in .data */
int call_count = 0;

/* This uninitialized global will be in .bss */
int last_result;

int main(int argc, char* argv[]) {
    call_count++;
    last_result = add(3, 4);
    printf(greeting, last_result);
    return 0;
}
```

```bash
# Compile and inspect each stage:
gcc -E mini_calc.c -o mini_calc.i   # preprocess
gcc -S -O2 mini_calc.c -o mini_calc.s  # to assembly
gcc -c mini_calc.c -o mini_calc.o       # to object
gcc mini_calc.o -o mini_calc            # link

# Inspect sections in the object file:
objdump -h mini_calc.o
# .text   (code for add + main)
# .rodata (the "Result: %d\n" string)
# .data   (call_count = 0)
# .bss    (last_result, size 4)
# .symtab (add, greeting, call_count, last_result, main, printf=U)

# See final sizes:
size mini_calc
#    text    data     bss     dec     hex filename
#    1234     560       8    1802     70a mini_calc
```

---

## Part 10: Headers, Translation Units, and the Include Model

Understanding why `#include` works the way it does:

```c
/* math_utils.h — DECLARATION only (interface) */
#ifndef MATH_UTILS_H    /* include guard — prevents double-inclusion */
#define MATH_UTILS_H

int add(int a, int b);      /* function declaration */
extern int call_count;      /* extern: defined elsewhere */
typedef struct { int x, y; } Point;

#endif

/* math_utils.c — DEFINITION (implementation) */
#include "math_utils.h"

int call_count = 0;         /* definition: reserves storage */

int add(int a, int b) {     /* definition: provides code */
    call_count++;
    return a + b;
}

/* main.c — uses math_utils */
#include "math_utils.h"     /* paste the declarations */
#include <stdio.h>

int main() {
    printf("%d\n", add(3, 4));   /* call_count and add are undefined here */
    return 0;                     /* resolved by linker via math_utils.o */
}
```

```bash
# Compile separately (each .c = one translation unit):
gcc -c math_utils.c -o math_utils.o
gcc -c main.c -o main.o
# Link:
gcc math_utils.o main.o -o program

# This is how large C projects work: Makefile compiles .c files
# independently, only relinking when needed.
```

**The One Definition Rule (ODR):** Every symbol must be *declared* in every translation unit that uses it (via headers), but *defined* in exactly one. Violating ODR causes linker errors (`undefined reference`) or undefined behavior (multiple definitions).

---

## Summary: The Full Pipeline

```
hello.c
  │  #include → paste headers, expand #define
  ▼
hello.i   (preprocessed source)
  │  parse → AST → IR → code generation
  ▼
hello.s   (x86-64 assembly)
  │  assemble each instruction
  ▼
hello.o   (ELF object: .text .data .bss .symtab .rel.text)
  │  merge sections, resolve symbols, fill relocations
  ▼
hello     (ELF executable: all sections, addresses assigned)
  │  mmap segments into virtual memory, run _start
  ▼
Process   (running in virtual address space)
```

**Interpreted languages take a shortcut**: Python parses and compiles to bytecode (`.pyc`), then the Python interpreter (itself a compiled ELF/EXE) runs the bytecode. The bytecode is portable but slower; JIT compilers (V8, PyPy, JVM HotSpot) add a native-code path for hot functions.

---

## Exercises

### Exercise 1 — Inspect Your Own Compiler (20 min)

Run `gcc -save-temps hello.c -o hello` on a simple C program. Examine each intermediate file: `.i`, `.s`, `.o`, and the final binary. Using `objdump -h hello.o`, identify which section contains each piece of data.

### Exercise 2 — Symbol Hunt (15 min)

Write a C program with: one initialized global int, one uninitialized global int, one string literal, and one function. Predict which section each goes in. Verify with `nm` and `objdump -h`.

### Exercise 3 — Linking Error Diagnosis (20 min)

Create two `.c` files where one calls a function defined in the other. Compile each to `.o` separately, then:
1. Try linking only one `.o` (observe the undefined reference error)
2. Link both (should succeed)
3. Add a second definition of the function in a third `.c` file and try linking all three (observe the multiple definition error)

### Exercise 4 — Python Bytecode (15 min)

Use `dis.dis()` to disassemble a Python function you've written. Identify: LOAD_FAST vs LOAD_GLOBAL, CALL_FUNCTION, and any JUMP instructions. Map each bytecode instruction back to a line of source code.

### Exercise 5 — Compare Memory Sizes (15 min)

Write a C program that uses `sizeof` to print the size of `int`, `long`, `double`, `char*`, and a struct. Then write an equivalent Python program using `sys.getsizeof`. Why are the Python sizes so much larger? Explain in terms of Python's object model.

---

## Further Reading

- **"Computer Systems: A Programmer's Perspective"** — Bryant & O'Hallaron: the canonical source on ELF, linking, and the memory system (Chapters 7-9)
- **"Linkers and Loaders"** — John Levine (free online): deep dive into the linker
- **ELF specification** — https://refspecs.linuxfoundation.org/elf/elf.pdf
- **`man elf`** — the Linux manual page for the ELF format
- **"Inside the Python Virtual Machine"** — free online: CPython bytecode in detail
- **V8 blog** — https://v8.dev/blog: how JavaScript JIT compilation works
- **`objdump`, `readelf`, `nm`, `ldd`** — the four essential binary analysis tools; try `man objdump`
