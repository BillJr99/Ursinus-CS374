<!--
author:   CS374 Course Team
email:    
version:  0.0.1
language: en
narrator: US English Female
comment:  Foreign Function Interface — C ABI, calling conventions, ctypes, cffi, implementing FFI in an interpreter
import:   https://raw.githubusercontent.com/liaScript/coderunner/master/README.md
link:     https://cdn.jsdelivr.net/chartist.min.css
-->

# Foreign Function Interfaces: Crossing Language Boundaries

> **Prerequisites:** Python programming; basic C syntax; familiarity with the interpreter project
> **Goal:** Understand how languages call into native code — the C ABI, data representation, name mangling, `ctypes`/`cffi` — and implement a simple FFI extension for a mini interpreter.

**POGIL Roles:** Driver · Recorder · Reporter · Manager

---

## Preface: Why Every Language Needs to Call C

No programming language is an island. The operating system, graphics drivers, cryptography libraries, database engines, and compression algorithms are all written in C (or C++, which uses C's ABI for its C-compatible subset). To be useful, a language must be able to call into this world.

A **Foreign Function Interface (FFI)** is the mechanism by which one language calls functions written in another. "Foreign" means "outside the current language runtime." The most common form is calling C from a high-level language (Python, Haskell, Lua, Julia) because:

1. **C is the universal ABI:** Nearly all languages can call C; C is the *lingua franca* of system interfaces.
2. **Performance:** Native code runs without an interpreter loop.
3. **Library reuse:** Millions of battle-tested C libraries exist.

The challenge: the high-level language's runtime and the C runtime make different assumptions about data layout, memory ownership, error handling, and calling conventions.

---

## Model 1: The C Application Binary Interface (ABI)

An **ABI (Application Binary Interface)** defines how functions are called at the machine level: which registers hold arguments, who cleans up the stack, how structures are laid out in memory, what calling conventions are used. C's ABI is the de facto standard because it is stable, documented, and supported by every compiler on every platform.

```python
import ctypes
import sys

# ctypes gives us direct access to the C standard library
# without writing any C code ourselves

# Load the C standard library
if sys.platform == "linux":
    libc = ctypes.CDLL("libc.so.6")
elif sys.platform == "darwin":
    libc = ctypes.CDLL("libc.dylib")
else:
    libc = ctypes.msvcrt   # Windows fallback

print("=== Calling C's strlen via ctypes ===")
# strlen(const char *s) -> size_t
libc.strlen.restype  = ctypes.c_size_t
libc.strlen.argtypes = [ctypes.c_char_p]

s = b"Hello, world!"   # bytes, not str — C expects null-terminated bytes
length = libc.strlen(s)
print(f"  strlen({s!r}) = {length}")
print(f"  Python: len({s!r}) = {len(s)}")
print(f"  Same? {length == len(s)}")

print()
print("=== Calling C's abs and labs ===")
libc.abs.restype  = ctypes.c_int
libc.abs.argtypes = [ctypes.c_int]
libc.labs.restype  = ctypes.c_long
libc.labs.argtypes = [ctypes.c_long]

for v in [-42, 0, 100, -32768]:
    print(f"  abs({v:6d}) = {libc.abs(v)}")

print()
print("=== C data types and their Python equivalents ===")
type_map = [
    ("c_int",    ctypes.c_int,    42),
    ("c_long",   ctypes.c_long,   42),
    ("c_float",  ctypes.c_float,  3.14),
    ("c_double", ctypes.c_double, 3.14),
    ("c_char_p", ctypes.c_char_p, b"hello"),
    ("c_void_p", ctypes.c_void_p, None),
]
for name, ctype, example in type_map:
    obj = ctype(example) if example is not None else ctype()
    print(f"  ctypes.{name:<12} value={obj.value!r:<15} "
          f"sizeof={ctypes.sizeof(ctype)} bytes")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

**Key insight:** `ctypes` marshals Python values into C-compatible binary representations automatically for simple types. For complex types (structs, arrays, function pointers), you must describe the layout explicitly.

> **Critical Thinking Questions 1–3**

**CTQ 1.** `strlen` expects a `const char *` — a pointer to a null-terminated byte array. Why does `ctypes` require `b"Hello"` (bytes) rather than `"Hello"` (str)? What does Python's str store internally that C's `char *` does not?

[[___ your answer here ___]]

**CTQ 2.** `ctypes.c_float` has sizeof 4 bytes; `ctypes.c_double` has sizeof 8 bytes. Python's `float` is always 64-bit (a C `double`). What precision loss happens when you pass a Python `float` to a C function declared with `c_float` parameter?

[[___ your answer here ___]]

**CTQ 3.** The ABI specifies how arguments are passed: by register (x86-64 uses rdi, rsi, rdx, rcx, r8, r9 for first 6 integer args) or by stack (7th and beyond). A language that passes arguments in the wrong order or wrong registers will silently corrupt function calls. What is the responsibility of `ctypes` in this context?

[[___ your answer here ___]]

---

## Model 2: Structs, Pointers, and Memory Layout

C structs have a specific memory layout (with padding). When calling C functions that take or return structs, the FFI must reproduce the exact layout.

```python
import ctypes

# Define a C-compatible struct in Python
class Point(ctypes.Structure):
    _fields_ = [
        ("x", ctypes.c_double),
        ("y", ctypes.c_double),
    ]

class Rect(ctypes.Structure):
    _fields_ = [
        ("top_left",     Point),
        ("bottom_right", Point),
    ]

print("=== C struct layout ===")
p = Point(3.0, 4.0)
print(f"  Point({p.x}, {p.y})")
print(f"  sizeof(Point) = {ctypes.sizeof(Point)} bytes")
print(f"  offset(x) = {Point.x.offset}, offset(y) = {Point.y.offset}")

r = Rect(Point(0.0, 0.0), Point(10.0, 5.0))
print(f"\n  Rect: ({r.top_left.x},{r.top_left.y}) → ({r.bottom_right.x},{r.bottom_right.y})")
print(f"  sizeof(Rect) = {ctypes.sizeof(Rect)} bytes")

print()
print("=== Struct with alignment padding ===")
class Padded(ctypes.Structure):
    _fields_ = [
        ("flag",  ctypes.c_uint8),    # 1 byte
        ("value", ctypes.c_uint32),   # 4 bytes — but likely padded to 4-byte boundary
        ("extra", ctypes.c_uint16),   # 2 bytes
    ]

print(f"  Padded: flag@{Padded.flag.offset}, value@{Padded.value.offset}, "
      f"extra@{Padded.extra.offset}")
print(f"  sizeof(Padded) = {ctypes.sizeof(Padded)} bytes  "
      f"(vs naive 1+4+2=7 bytes)")

print()
print("=== Passing structs by pointer ===")
class Vec2(ctypes.Structure):
    _fields_ = [("x", ctypes.c_float), ("y", ctypes.c_float)]

def magnitude_python(v: Vec2) -> float:
    import math
    return math.sqrt(v.x**2 + v.y**2)

# Simulate how an FFI would call a C function that takes a Vec2*
v = Vec2(3.0, 4.0)
ptr = ctypes.byref(v)    # byref creates a pointer to v without copying
print(f"  Vec2(3, 4) at address {id(v):#x}")
print(f"  magnitude = {magnitude_python(v):.4f}")

print()
print("=== C arrays ===")
IntArray5 = ctypes.c_int * 5
arr = IntArray5(10, 20, 30, 40, 50)
print(f"  C array of 5 ints: {list(arr)}")
print(f"  sizeof = {ctypes.sizeof(arr)} bytes ({ctypes.sizeof(ctypes.c_int)} × 5)")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

> **Critical Thinking Questions 4–6**

**CTQ 4.** The `Padded` struct has `sizeof` greater than 1+4+2=7. The compiler adds **padding** between fields to align them to their natural alignment. Why does alignment matter? What hardware problem does misaligned access cause on x86? On ARM?

[[___ your answer here ___]]

**CTQ 5.** `ctypes.byref(v)` passes a pointer to `v` without copying. If the C function modifies the struct through the pointer, the Python object `v` is also modified. How does this differ from Python's normal parameter passing semantics? When is this desirable? When is it dangerous?

[[___ your answer here ___]]

**CTQ 6.** Structs can be passed **by value** (C copies the struct) or **by pointer** (C receives an address). For large structs, passing by pointer is more efficient. But it also means the callee can modify the original. How do languages like Rust use the type system to make this safe?

[[___ your answer here ___]]

---

## Model 3: Callbacks — C Calling Back into Python

The FFI is bidirectional: not only can Python call C, but C can call Python functions (callbacks). This is used for event handlers, sort comparators, and error handlers.

```python
import ctypes

# Define a C-compatible function type for a callback
# int (*comparator)(const void*, const void*)  -- used by qsort
COMPARATOR = ctypes.CFUNCTYPE(
    ctypes.c_int,         # return type
    ctypes.c_void_p,      # arg 1: const void*
    ctypes.c_void_p,      # arg 2: const void*
)

# Load libc for qsort
import sys
libc = ctypes.CDLL("libc.so.6" if sys.platform == "linux" else "libc.dylib")
libc.qsort.argtypes = [
    ctypes.c_void_p,   # base: pointer to array
    ctypes.c_size_t,   # nmemb: number of elements
    ctypes.c_size_t,   # size: size of each element
    COMPARATOR,        # compar: the callback
]
libc.qsort.restype = None

print("=== Python callback called by C's qsort ===")

call_count = [0]

def python_compare(a_ptr, b_ptr):
    """C calls this function with pointers to two ints."""
    call_count[0] += 1
    a = ctypes.cast(a_ptr, ctypes.POINTER(ctypes.c_int)).contents.value
    b = ctypes.cast(b_ptr, ctypes.POINTER(ctypes.c_int)).contents.value
    return (a > b) - (a < b)   # -1, 0, or 1

c_compare = COMPARATOR(python_compare)   # wrap Python fn in C function type

IntArray = ctypes.c_int * 8
data = IntArray(64, 12, 99, 3, 47, 28, 7, 55)
print(f"  Before sort: {list(data)}")

libc.qsort(data, len(data), ctypes.sizeof(ctypes.c_int), c_compare)
print(f"  After sort:  {list(data)}")
print(f"  Comparator called {call_count[0]} times")

print()
print("=== Callback memory management pitfall ===")
# CRITICAL: the C library holds a raw function pointer.
# If the Python callback object is garbage collected, the pointer becomes dangling.
# You MUST keep a reference to c_compare alive as long as C might call it.
print("  Danger: if c_compare is not kept alive, the function pointer is dangling!")
print("  Safe: store callbacks in a list that outlives the C call.")
callbacks = [c_compare]   # this reference keeps the callback alive

print()
print("=== Type-safe callback wrapper ===")
# A safer pattern: wrap in a class that manages the lifetime
class SafeCallback:
    def __init__(self, fn, c_type):
        self._fn = fn
        self._c_fn = c_type(fn)
    @property
    def c_ptr(self):
        return self._c_fn
    def __del__(self):
        print(f"  SafeCallback destroyed: {self._fn.__name__}")

def my_handler(x: int, y: int) -> int:
    return x - y

HANDLER = ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_int, ctypes.c_int)
cb = SafeCallback(my_handler, HANDLER)
print(f"  Direct test of callback: my_handler(10, 3) = {cb.c_ptr(10, 3)}")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

> **Critical Thinking Questions 7–9**

**CTQ 7.** `COMPARATOR = ctypes.CFUNCTYPE(c_int, c_void_p, c_void_p)` describes the function signature. What would happen if you passed a Python function with the wrong signature (e.g., one that takes only one argument instead of two)?

[[___ your answer here ___]]

**CTQ 8.** The comment warns: "if c_compare is garbage collected, the pointer becomes dangling." Why can't Python's garbage collector know that C is holding a reference? What would a language with linear types (like Rust) do differently?

[[___ your answer here ___]]

**CTQ 9.** `qsort` calls the comparator multiple times on different pairs. The comparator modifies `call_count` — a Python list (mutable container). This works because Python closures capture by reference. If the comparator modified a Python integer directly (`count = count + 1`), it would fail due to Python's scoping rules. Why? What does this reveal about closures and rebinding?

[[___ your answer here ___]]

---

## Model 4: Name Mangling and Symbol Resolution

C uses simple symbol names (`strlen`, `printf`). C++ mangles names to encode type signatures. Understanding this is essential for building FFI tools.

```python
import ctypes
import ctypes.util
import sys

print("=== Finding shared library paths ===")
math_lib_name = ctypes.util.find_library("m")
c_lib_name    = ctypes.util.find_library("c")
print(f"  libm path: {math_lib_name}")
print(f"  libc path: {c_lib_name}")

print()
print("=== Dynamic symbol lookup ===")
if sys.platform != "win32":
    # RTLD_DEFAULT looks up symbols in all loaded libraries
    libc = ctypes.CDLL(None)    # None = look in all currently loaded libraries
    
    # Manually look up a symbol by name
    try:
        printf_ptr = ctypes.cast(
            ctypes.c_void_p.in_dll(libc, "printf") if hasattr(ctypes.c_void_p, 'in_dll')
            else None,
            ctypes.c_void_p
        )
        print(f"  printf found in libc")
    except (OSError, AttributeError):
        print("  (symbol inspection not available on this platform)")

print()
print("=== Python's own C API via ctypes ===")
# CPython exports its C API as a shared library (libpython)
# We can call internal Python C API functions — carefully!
py = ctypes.pythonapi

# PyList_New(Py_ssize_t len) -> PyObject*
py.PyList_New.restype = ctypes.py_object
py.PyList_New.argtypes = [ctypes.c_ssize_t]
new_list = py.PyList_New(0)
print(f"  PyList_New(0) via C API: {new_list!r}  type={type(new_list).__name__}")

# Py_GetVersion() -> const char*
py.Py_GetVersion.restype = ctypes.c_char_p
version_str = py.Py_GetVersion()
print(f"  Py_GetVersion(): {version_str.decode()[:50]}...")

print()
print("=== What C++ name mangling looks like ===")
# C++ compilers mangle function names to encode their full type signatures.
# 'void MyClass::foo(int, double)' might become '_ZN7MyClass3fooEid'
# Tools like 'c++filt' unmangle them.
# In Python, you can see this pattern by simulating it:
def mangle_simple(class_name: str, method_name: str, param_types: list) -> str:
    """Simplified Itanium ABI mangling (GNU/Clang style)."""
    type_codes = {"int": "i", "double": "d", "float": "f", "bool": "b",
                  "char": "c", "void": "v", "long": "l"}
    params = "".join(type_codes.get(t, "?") for t in param_types)
    n = len(class_name)
    m = len(method_name)
    return f"_ZN{n}{class_name}{m}{method_name}E{params}"

examples = [
    ("MyClass", "foo",    ["int", "double"]),
    ("Vector",  "push",   ["int"]),
    ("Matrix",  "mult",   ["double", "double"]),
]
print("  C++ name mangling (simplified):")
for cls, fn, params in examples:
    mangled = mangle_simple(cls, fn, params)
    print(f"    {cls}::{fn}({', '.join(params)}) -> {mangled}")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

> **Critical Thinking Questions 10–12**

**CTQ 10.** C's simple symbol names (`strlen`) mean that a shared library can only export one `strlen`. C++ name mangling allows overloaded functions (`foo(int)` and `foo(double)`) to coexist in the same library. What does this tell you about C's type system at the ABI level?

[[___ your answer here ___]]

**CTQ 11.** `ctypes.CDLL(None)` loads symbols from all currently loaded libraries, including the Python interpreter itself. Why is calling Python's internal C API this way dangerous? What invariant must you preserve?

[[___ your answer here ___]]

**CTQ 12.** When writing an FFI for your mini language, you could either (a) call into C at the C ABI level (like ctypes) or (b) call Python functions directly. Option (b) is simpler. What would you lose by choosing (b) rather than (a)? Under what circumstances would (a) be necessary?

[[___ your answer here ___]]

---

## Model 5: Implementing a Simple FFI in a Mini Interpreter

A language interpreter can support FFI by letting programs call Python built-ins or C functions by name. Here is a minimal implementation.

```python
from dataclasses import dataclass, field
from typing import Any, Dict, Callable, List, Optional
import ctypes
import sys

@dataclass
class FfiCall:
    """AST node: call a foreign function by name with given arguments."""
    lib_name: str
    func_name: str
    arg_types: List[str]   # e.g., ["int", "int"]
    ret_type: str           # e.g., "int"
    args: List[Any]        # evaluated argument AST nodes

@dataclass
class Num:
    value: float

@dataclass
class Str_:
    value: str

class FFIRegistry:
    """Manages loaded libraries and their function signatures."""
    CTYPES_MAP = {
        "int":    ctypes.c_int,
        "long":   ctypes.c_long,
        "double": ctypes.c_double,
        "float":  ctypes.c_float,
        "str":    ctypes.c_char_p,
        "void":   None,
    }

    def __init__(self):
        self._libs: Dict[str, Any] = {}
        self._python_fns: Dict[str, Callable] = {}
        # Pre-load safe Python built-ins as "python" library
        self._python_fns.update({
            "abs":   abs,
            "len":   len,
            "str":   str,
            "int":   int,
            "float": float,
            "max":   max,
            "min":   min,
        })

    def load_lib(self, name: str, path: str):
        self._libs[name] = ctypes.CDLL(path)

    def call(self, lib_name: str, func_name: str,
             arg_types: List[str], ret_type: str, args: List[Any]) -> Any:
        if lib_name == "python":
            fn = self._python_fns.get(func_name)
            if fn is None:
                raise NameError(f"python.{func_name} not in FFI registry")
            return fn(*args)
        
        lib = self._libs.get(lib_name)
        if lib is None:
            raise ImportError(f"Library {lib_name!r} not loaded")
        
        fn = getattr(lib, func_name)
        fn.argtypes = [self.CTYPES_MAP[t] for t in arg_types]
        fn.restype  = self.CTYPES_MAP.get(ret_type, ctypes.c_int)
        
        # Convert Python values to C values
        c_args = []
        for val, t in zip(args, arg_types):
            if t == "str":
                c_args.append(val.encode() if isinstance(val, str) else val)
            else:
                c_args.append(val)
        
        result = fn(*c_args)
        if isinstance(result, bytes):
            return result.decode()
        return result

def eval_node(node, env, ffi: FFIRegistry):
    if isinstance(node, Num):
        return node.value
    if isinstance(node, Str_):
        return node.value
    if isinstance(node, FfiCall):
        evaluated_args = [eval_node(a, env, ffi) for a in node.args]
        return ffi.call(node.lib_name, node.func_name,
                        node.arg_types, node.ret_type, evaluated_args)
    raise ValueError(f"unknown node: {node!r}")

ffi = FFIRegistry()

# Load libc for math operations
if sys.platform == "linux":
    ffi.load_lib("libc", "libc.so.6")
    ffi.load_lib("libm", "libm.so.6")
elif sys.platform == "darwin":
    ffi.load_lib("libc", "libc.dylib")
    ffi.load_lib("libm", "libm.dylib")

print("=== Mini interpreter FFI calls ===")

env = {}

# call python.abs(-42) -> int
call_abs = FfiCall("python", "abs", ["int"], "int", [Num(-42)])
print(f"  python.abs(-42) = {eval_node(call_abs, env, ffi)}")

# call python.max(3, 7) -> int
call_max = FfiCall("python", "max", ["int", "int"], "int", [Num(3), Num(7)])
print(f"  python.max(3, 7) = {eval_node(call_max, env, ffi)}")

# call libc.strlen("hello") -> int (only on Linux/Mac)
if sys.platform in ("linux", "darwin"):
    call_strlen = FfiCall("libc", "strlen", ["str"], "int", [Str_("hello world")])
    print(f"  libc.strlen('hello world') = {eval_node(call_strlen, env, ffi)}")
    
    call_sqrt = FfiCall("libm" if sys.platform == "linux" else "libc",
                        "sqrt", ["double"], "double", [Num(9.0)])
    try:
        print(f"  sqrt(9.0) = {eval_node(call_sqrt, env, ffi)}")
    except Exception as e:
        print(f"  (sqrt not available: {e})")

print()
print("=== FFI in language syntax (hypothetical) ===")
print("  Your language could expose FFI as a built-in statement:")
print("  ffi load 'libc.so.6' as libc;")
print("  let n = ffi call libc.strlen(str: 'hello');")
print("  print n;   # 5")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

> **Critical Thinking Questions 13–15**

**CTQ 13.** The `FFIRegistry` uses a "Python" pseudo-library for safe built-ins and C libraries for native code. What is the advantage of keeping these in the same `FfiCall` AST node vs. having separate `NativeFn` and `PythonFn` nodes?

[[___ your answer here ___]]

**CTQ 14.** FFI calls bypass your interpreter's type checker. A language-level type error (e.g., passing a string where `c_int` is expected) will become a ctypes exception rather than a friendly language error. How would you add a "type gate" to the FFI call path?

[[___ your answer here ___]]

**CTQ 15.** A language with FFI can call any C function, including `malloc`, `free`, `exec`, and `system`. This breaks memory safety and security. How do languages like Haskell (via `Foreign.Unsafe`) or Rust (via `unsafe`) signal that FFI code requires special trust?

[[___ your answer here ___]]

---

## Multiple Choice Review

**Question 1.** `ctypes.c_char_p` in Python represents:

- [( )] A Python `str` object
- [(X)] A C-style null-terminated `char*` pointer, accepting `bytes`
- [( )] A single character (1 byte)
- [( )] A wide character (2 bytes) for Unicode

**Question 2.** When a C function takes a struct by value, the caller:

- [(X)] Copies the entire struct onto the stack (or into registers per ABI)
- [( )] Passes a pointer to the struct, which C dereferences automatically
- [( )] Converts the struct to a byte string first
- [( )] Returns an error unless the struct is marked `extern "C"`

**Question 3.** C++ name mangling is needed because:

- [( )] C++ is compiled to a different object format than C
- [(X)] C++ allows function overloading, so multiple functions can have the same name but different parameter types
- [( )] The linker requires all symbols to be prefixed with the namespace
- [( )] C++ uses a garbage collector that must track all function names

**Question 4.** Keeping a reference to a `ctypes.CFUNCTYPE` callback alive while C might call it is necessary because:

- [( )] ctypes functions are reference-counted independently
- [(X)] Python's garbage collector will free the callback if no Python reference remains, leaving C with a dangling pointer
- [( )] C copies the function body into its own memory on first call
- [( )] ctypes registers all callbacks globally and they are never freed

---

## Exercises

**Exercise 1.** Use `ctypes` to call C's `qsort` with a Python comparator that sorts strings by length (shortest first), falling back to lexicographic order for equal-length strings:

```python
import ctypes
import sys

if sys.platform not in ("linux", "darwin"):
    print("Skipping: not Linux/macOS")
else:
    libc = ctypes.CDLL("libc.so.6" if sys.platform == "linux" else "libc.dylib")
    
    # qsort signature: void qsort(void *base, size_t nmemb, size_t size,
    #                             int (*compar)(const void *, const void *))
    COMP = ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_void_p, ctypes.c_void_p)
    
    words = ["banana", "kiwi", "apple", "fig", "cherry", "date"]
    
    # To qsort strings, we'll sort indices and use Python for the comparison
    indices = list(range(len(words)))
    IdxArray = ctypes.c_int * len(indices)
    c_indices = IdxArray(*indices)
    
    def compare_by_length(a_ptr, b_ptr):
        a_idx = ctypes.cast(a_ptr, ctypes.POINTER(ctypes.c_int)).contents.value
        b_idx = ctypes.cast(b_ptr, ctypes.POINTER(ctypes.c_int)).contents.value
        wa, wb = words[a_idx], words[b_idx]
        if len(wa) != len(wb):
            return len(wa) - len(wb)
        return (wa > wb) - (wa < wb)
    
    comp_fn = COMP(compare_by_length)
    libc.qsort.argtypes = [ctypes.c_void_p, ctypes.c_size_t,
                           ctypes.c_size_t, COMP]
    libc.qsort.restype = None
    libc.qsort(c_indices, len(c_indices), ctypes.sizeof(ctypes.c_int), comp_fn)
    
    sorted_words = [words[c_indices[i]] for i in range(len(c_indices))]
    print(f"Sorted by length: {sorted_words}")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

**Exercise 2.** Extend the `FFIRegistry` from Model 5 to support type coercion and better error messages. Add a `validate_and_coerce` method that checks types and converts Python values:

```python
import ctypes
import sys

class SafeFFIRegistry:
    CTYPES_MAP = {
        "int":    ctypes.c_int,
        "double": ctypes.c_double,
        "str":    ctypes.c_char_p,
    }
    PYTHON_TYPES = {
        "int":    (int, float),
        "double": (int, float),
        "str":    (str, bytes),
    }
    
    def __init__(self):
        self._python_fns = {
            "abs": abs, "max": max, "min": min,
            "len": len, "str": str, "int": int,
        }

    def validate_and_coerce(self, val, expected_type: str):
        if expected_type not in self.PYTHON_TYPES:
            raise TypeError(f"Unknown FFI type: {expected_type!r}")
        allowed = self.PYTHON_TYPES[expected_type]
        if not isinstance(val, allowed):
            raise TypeError(
                f"FFI type mismatch: expected {expected_type} "
                f"(Python {allowed}), got {type(val).__name__}"
            )
        if expected_type == "str" and isinstance(val, str):
            return val.encode()
        if expected_type == "int" and isinstance(val, float):
            if val != int(val):
                raise ValueError(f"Cannot coerce {val} to int without precision loss")
            return int(val)
        return val

    def call_python(self, func_name: str, arg_types: list, args: list):
        fn = self._python_fns.get(func_name)
        if fn is None:
            raise NameError(f"python.{func_name} not registered")
        coerced = [self.validate_and_coerce(v, t) for v, t in zip(args, arg_types)]
        return fn(*coerced)

ffi = SafeFFIRegistry()

print("=== Safe FFI with type validation ===")

# Valid calls
for fn, types, args in [
    ("abs",   ["int"],        [-42]),
    ("max",   ["int", "int"], [3, 7]),
    ("len",   ["str"],        ["hello"]),
]:
    result = ffi.call_python(fn, types, args)
    print(f"  python.{fn}({args}) = {result}")

# Invalid calls (should produce clear errors)
bad_calls = [
    ("abs",   ["int"],  ["not_a_number"]),
    ("max",   ["int", "int"], [3.5, 7]),
]
for fn, types, args in bad_calls:
    try:
        ffi.call_python(fn, types, args)
    except (TypeError, ValueError) as e:
        print(f"  python.{fn}({args}) -> {type(e).__name__}: {e}")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

**Exercise 3.** Implement a minimal "safe FFI" for your mini language that allows calling Python's `math` module functions. Add lexer/parser support for the syntax `ffi("math", "sqrt", 9.0)`:

```python
import math
import re
from dataclasses import dataclass
from typing import Any, List

@dataclass
class FfiExpr:
    module: str
    func_name: str
    args: List[Any]

SAFE_MODULES = {
    "math": math,
    "os.path": __import__("os.path"),
}

def eval_ffi(node: FfiExpr):
    mod = SAFE_MODULES.get(node.module)
    if mod is None:
        raise ImportError(f"Module {node.module!r} not in FFI allowlist")
    fn = getattr(mod, node.func_name, None)
    if fn is None:
        raise AttributeError(f"{node.module}.{node.func_name} not found")
    return fn(*node.args)

# Simulate parsing 'ffi("math", "sqrt", 9.0)'
def parse_ffi_call(src: str) -> FfiExpr:
    m = re.match(r'ffi\("([^"]+)",\s*"([^"]+)"((?:,\s*[\d.]+)*)\)', src)
    if not m:
        raise SyntaxError(f"Invalid ffi call: {src!r}")
    module, fn_name = m.group(1), m.group(2)
    args_str = m.group(3)
    args = [float(a.strip()) for a in args_str.split(",") if a.strip()]
    return FfiExpr(module, fn_name, args)

test_calls = [
    'ffi("math", "sqrt", 25.0)',
    'ffi("math", "floor", 3.7)',
    'ffi("math", "pow", 2.0, 10.0)',
]

print("=== Safe FFI for math module ===")
for src in test_calls:
    node = parse_ffi_call(src)
    result = eval_ffi(node)
    print(f"  {src} = {result}")

# Security: try to call an unsafe module
try:
    bad = FfiExpr("os", "system", ["rm -rf /"])
    eval_ffi(bad)
except ImportError as e:
    print(f"\n  Security block: {e}")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

---

## Reflection

1. The FFI is fundamentally an "escape hatch" from your language's safety guarantees. A type-safe language can call unsafe C code via FFI. How do language designers manage this tension? Name the strategies used by Python, Haskell, and Rust respectively.

2. Your mini interpreter runs Python as its host language. This means your "FFI" to Python is essentially free — you can call any Python function. But if your language was a compiled language generating machine code, FFI would require real ABI compatibility. What would change in your implementation?

3. The `SAFE_MODULES` allowlist in Exercise 3 prevents calling `os.system` via FFI. Is a whitelist the right security model for an FFI? What are the limitations of this approach?

---

## Further Reading

- **Python docs:** `ctypes` — A foreign function library for Python
- **Python docs:** `cffi` — C Foreign Function Interface for Python (higher-level alternative to ctypes)
- **Article:** *How Python calls C* — deep dive into CPython's API
- **Rust book:** Chapter, "Unsafe Rust" — `extern "C"` and `unsafe fn`
- **Haskell wiki:** `Foreign Function Interface` — `Foreign.Ptr`, `Foreign.Marshal`
- **Paper:** *A Semantic Framework for C (and the Rest)* — Norrish (1998), the formal semantics behind C's ABI behavior
- **Talk:** Brandon Williams, "ctypes Without the Boilerplate" — automating struct generation from C headers

---

*End of Activity — Foreign Function Interfaces: C ABI, ctypes, callbacks, name mangling, interpreter FFI implementation*
