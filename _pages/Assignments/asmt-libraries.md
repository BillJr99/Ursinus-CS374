---
layout: assignment
permalink: /Assignments/Libraries
title: "CS374: Principles of Programming Languages - Libraries and Modules"

info:
  coursenum: CS374
  purpose: "To understand how languages implement libraries and modules — the mechanisms that let programs grow beyond a single file — from Python packages and dynamic loading to namespaces and a toy interpreter's own module system."
  tilt:
    task: "Build a structured Python package with a clean public API, a dynamic importlib plugin loader, a set of namespace and LEGB analyses, and an import system for a mini interpreter."
    criteria: "Assessed on a well-encapsulated package, a validating plugin loader, correct namespace analyses, and a working interpreter module system, each part worth 25 points; see the rubric below for the full breakdown."
  points: 100
  goals:
    - To create well-structured Python packages with proper public APIs using __all__ and __init__.py
    - To implement a dynamic plugin system using importlib and runtime attribute lookup
    - To understand Python's namespace model (LEGB rule) and how modules participate in it
    - To design and implement a minimal module system in a toy interpreter

  rubric:
    - weight: 25
      description: Package Structure and Public API
      preemerging: The package directory is missing __init__.py, or the module cannot be imported at all; there is no use of __all__
      beginning: The package can be imported, but __all__ is either absent or incorrect — e.g., it lists private names starting with underscore, or it omits names that should be public; the submodule structure is flat instead of nested
      progressing: The package structure is correct and __all__ accurately controls what `from pkg import *` exports; however, the __init__.py does not re-export the convenience API, so callers must import from submodules directly instead of from the package root
      proficient: The package has a clean hierarchy with at least two submodules; __init__.py re-exports the intended public surface via __all__; private helpers are prefixed with _; the public API is documented with docstrings; importing the package root gives the user everything they need without knowing the internal layout
    - weight: 25
      description: Dynamic Plugin System
      preemerging: The plugin loader is not implemented, or it uses exec() or eval() to load plugins rather than importlib; there is no handling for missing plugins
      beginning: importlib.import_module is used but the loader does not discover plugins automatically — plugins must be hard-coded by name in the loader; or errors from missing plugins crash the application
      progressing: The plugin loader discovers and loads plugins correctly; errors from missing or malformed plugins are caught and logged rather than propagated; however, the plugin interface contract is not checked — malformed plugins that lack required functions are silently accepted and crash later
      proficient: The loader discovers plugins by name pattern (e.g., any module in the plugins/ directory); it validates each plugin against a required interface (checks for the expected function names using hasattr); malformed or missing plugins are reported with a clear warning and skipped; the system runs correctly with 0, 1, or multiple valid plugins; the design is tested with at least one deliberately malformed plugin
    - weight: 25
      description: Namespace Analysis
      preemerging: The namespace exercises are not attempted, or all solutions use global variables rather than closures or enclosing scopes
      beginning: Most namespace questions are answered but one or more are incorrect — e.g., the student cannot predict whether a shadowing assignment affects the enclosing scope without nonlocal, or confuses the module dict (__dict__) with globals()
      progressing: All namespace exercises produce correct output; the student correctly distinguishes local/enclosing/global/built-in scopes; but the LEGB diagram or written explanation is incomplete or contains a factual error
      proficient: All six namespace exercises produce correct output with the predicted behavior written as assertions before running; the LEGB diagram is correct and annotated with at least one concrete example per scope level; the module introspection exercises use dir(), vars(), and __dict__ correctly; the writeup explains in one paragraph why Python chose LEGB over dynamic scoping
    - weight: 25
      description: Mini Interpreter Module System
      preemerging: The interpreter extension is not attempted, or the implementation does not use separate Env objects for modules — instead all names are stored in one flat dictionary
      beginning: Module environments are created and registered, but lookup does not traverse the module boundary correctly — e.g., a module's private names can be accessed from outside without qualification
      progressing: The module system correctly isolates module namespaces from the global environment; import and attribute access (module.name) work for the provided tests; however, from-import is not implemented, or circular imports cause infinite recursion rather than a clean error
      proficient: The interpreter extension implements import (creates a ModuleEnv, runs the module's init code), qualified attribute access (mod.name), and from-import (copies a binding into the caller's env); circular imports are detected and raise ImportError; the system is tested with at least three modules including one that imports another

  readings:
    - rtitle: "Libraries Activity"
      rlink: "https://liascript.github.io/course/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374-Fall2026/gh-pages/_pages/Activities/liascript-languagedesign.md"
    - rtitle: "Python Import System Documentation"
      rlink: "https://docs.python.org/3/reference/import.html"
    - rtitle: "PLAI Ch. 10 — Recursion and Modules"
      rlink: "https://www.plai.org/"

tags:
  - modules
  - packages
  - namespaces
  - dynamic-loading
  - interpreter

---

This assignment explores how programming languages implement libraries and modules — the mechanisms that let programs grow beyond a single file. You will build a well-structured Python package, implement a dynamic plugin loader, analyze Python's namespace model, and extend a toy interpreter with import support.

---

## Part 1: Package Structure and Public API (25 points)

### What You Are Building

You will create a Python package called `minimath` that provides basic mathematical operations organized into submodules.

### Step 1a: Directory Structure

Create the following layout:

```
minimath/
    __init__.py
    arithmetic.py
    stats.py
    _internal.py
```

- `arithmetic.py` — provides `add`, `sub`, `mul`, `div`, `power`, `absolute`
- `stats.py` — provides `mean`, `median`, `mode`, `std_dev`, `variance`
- `_internal.py` — provides helper `_clamp(value, lo, hi)` used internally (not exported)

### Step 1b: Implement the Submodules

**`arithmetic.py`:**

```python
"""Basic arithmetic operations."""

__all__ = ["add", "sub", "mul", "div", "power", "absolute"]

def add(a: float, b: float) -> float:
    """Return a + b."""
    return a + b

def sub(a: float, b: float) -> float:
    """Return a - b."""
    return a - b

def mul(a: float, b: float) -> float:
    """Return a * b."""
    return a * b

def div(a: float, b: float) -> float:
    """Return a / b. Raises ZeroDivisionError if b is 0."""
    if b == 0:
        raise ZeroDivisionError("division by zero")
    return a / b

def power(base: float, exp: float) -> float:
    """Return base ** exp."""
    return base ** exp

def absolute(x: float) -> float:
    """Return the absolute value of x."""
    return x if x >= 0 else -x
```

**`stats.py`:**  
Implement `mean(data)`, `median(data)`, `mode(data)` (return most frequent element, first on tie), `variance(data)` (population variance), and `std_dev(data)`. Each must raise `ValueError` on an empty list. Import and use `_clamp` from `_internal` for any clamping needed in your implementation.

**`_internal.py`:**

```python
"""Internal helpers — not part of the public API."""

def _clamp(value: float, lo: float, hi: float) -> float:
    """Clamp value to [lo, hi]."""
    return max(lo, min(hi, value))
```

### Step 1c: The Package Root (`__init__.py`)

Make the package convenient to use by re-exporting the public surface:

```python
"""minimath — a minimal math package."""

from .arithmetic import add, sub, mul, div, power, absolute
from .stats import mean, median, mode, variance, std_dev

__all__ = [
    "add", "sub", "mul", "div", "power", "absolute",
    "mean", "median", "mode", "variance", "std_dev",
]

__version__ = "1.0.0"
```

### Step 1d: Verify the Public API

Write `test_minimath.py` that:
1. Imports only from the package root: `from minimath import add, mean, ...`
2. Verifies that `_clamp` is NOT accessible via `from minimath import *` or `import minimath._internal`  
   (it should raise `ImportError` or `AttributeError`)
3. Tests every exported function with at least three inputs, including edge cases

```python
from minimath import *
print(dir())          # should NOT contain '_clamp' or '_internal'
assert add(2, 3) == 5
assert mean([1, 2, 3, 4, 5]) == 3.0
# ... more tests
```

---

## Part 2: Dynamic Plugin System (25 points)

### What You Are Building

A simple plugin-based transformation pipeline. Each plugin is a Python module that exports a `transform(text: str) -> str` function. The loader discovers and chains plugins at runtime.

### Step 2a: The Plugin Interface

A valid plugin module must export:

```python
NAME: str             # plugin display name
VERSION: str          # e.g., "1.0"
def transform(text: str) -> str: ...   # the transformation
```

### Step 2b: Write Three Plugins

Create `plugins/` directory with at least three plugin modules:

**`plugins/uppercase_plugin.py`:**
```python
NAME = "Uppercase"
VERSION = "1.0"

def transform(text: str) -> str:
    return text.upper()
```

**`plugins/word_count_plugin.py`:**
```python
NAME = "WordCount"
VERSION = "1.0"

def transform(text: str) -> str:
    words = text.split()
    return f"{text}\n[{len(words)} words]"
```

Write a third plugin of your own design (suggestions: `reverse_plugin.py`, `censor_plugin.py` that replaces a set of words, `title_case_plugin.py`).

Also create an **intentionally malformed** plugin `plugins/broken_plugin.py` that is missing the `transform` function — the loader must handle this gracefully.

### Step 2c: The Plugin Loader

Write `loader.py`:

```python
import importlib
import importlib.util
import sys
from pathlib import Path

REQUIRED_INTERFACE = ["NAME", "VERSION", "transform"]

def load_plugins(plugin_dir: str) -> list:
    """
    Discover all *_plugin.py files in plugin_dir, validate them against
    REQUIRED_INTERFACE, and return a list of valid plugin modules.
    Invalid plugins are logged to stderr and skipped.
    """
    plugins = []
    plugin_path = Path(plugin_dir)
    
    for py_file in sorted(plugin_path.glob("*_plugin.py")):
        module_name = py_file.stem
        spec = importlib.util.spec_from_file_location(module_name, py_file)
        mod = importlib.util.module_from_spec(spec)
        try:
            spec.loader.exec_module(mod)
        except Exception as e:
            print(f"[WARN] Failed to load {module_name}: {e}", file=sys.stderr)
            continue
        
        # Validate interface
        missing = [attr for attr in REQUIRED_INTERFACE if not hasattr(mod, attr)]
        if missing:
            print(f"[WARN] Plugin {module_name} missing: {missing}", file=sys.stderr)
            continue
        
        print(f"[INFO] Loaded plugin: {mod.NAME} v{mod.VERSION}")
        plugins.append(mod)
    
    return plugins

def apply_pipeline(text: str, plugins: list) -> str:
    """Apply each plugin's transform in order."""
    result = text
    for plugin in plugins:
        result = plugin.transform(result)
    return result
```

### Step 2d: A Driver

Write `main.py` that loads all plugins from `plugins/`, prints the loaded plugins, then applies the pipeline to an input string and prints the result:

```bash
python3 main.py "Hello, world"
# [INFO] Loaded plugin: Uppercase v1.0
# [INFO] Loaded plugin: WordCount v1.0
# [INFO] Loaded plugin: MyPlugin v1.0
# [WARN] Plugin broken_plugin missing: ['transform']
# Result:
# HELLO, WORLD
# [2 words]
```

---

## Part 3: Namespace Analysis (25 points)

For each exercise, **first predict the output** (write it as a comment), then run the code and verify. If your prediction was wrong, explain why.

### Step 3a: LEGB Lookup Order

```python
x = "global"

def outer():
    x = "enclosing"
    def inner():
        # x = "local"   # UNCOMMENT THIS ONE AT A TIME
        print(x)
    inner()

outer()
print(x)
```

Run this four ways:
1. As written (local `x` commented out)
2. With the local `x` uncommented
3. With `nonlocal x` added before the local assignment
4. After adding `global x` before the local assignment and changing it to `x = "modified"`

Predict and explain all four outputs.

### Step 3b: Module Namespaces

```python
import math
import json

# Question 1: are these the same object?
import math as m1
import math as m2
print(m1 is m2)

# Question 2: what is math.__dict__?
print(type(math.__dict__))
print(len(math.__dict__))

# Question 3: add a name to math's namespace
math.MY_CONSTANT = 42
print(math.MY_CONSTANT)

# Question 4: does the change persist across re-import?
import math
print(hasattr(math, 'MY_CONSTANT'))
```

Predict all four outputs. Explain what `sys.modules` caching means for question 1 and 4.

### Step 3c: Name Shadowing Hazards

```python
from math import sqrt

def sqrt(x):           # shadows math.sqrt
    return x ** 0.5

print(sqrt(16))        # which sqrt?

# Restore the original
from math import sqrt
print(sqrt(16))        # back to math.sqrt
```

Explain the hazard here. How does `import math` followed by `math.sqrt` avoid it?

### Step 3d: `__all__` and `import *`

Create a file `mymodule.py`:
```python
__all__ = ["public_func", "PUBLIC_CONST"]

PUBLIC_CONST = 42
public_func = lambda x: x + 1
_private = "hidden"
_PrivateClass = object
```

In a separate script, do `from mymodule import *` and inspect `dir()`. Verify that `_private` and `_PrivateClass` are not imported.

Then remove `__all__` from `mymodule.py` and repeat. What changes?

### Step 3e: LEGB Diagram

Draw a diagram (ASCII art is fine) showing the four namespace layers for this code:

```python
PI = 3.14159       # global

def circle_area(r):
    def helper(radius):
        area = PI * radius ** 2   # local
        return area
    return helper(r)
```

Label which scope each name (`PI`, `r`, `helper`, `radius`, `area`) lives in.

### Step 3f: Written Response

In your `readme.md`, answer in 2–3 sentences: Python uses lexical (static) scoping with the LEGB rule. How would programs behave differently under dynamic scoping? Give a concrete example showing the difference.

---

## Part 4: Mini Interpreter Module System (25 points)

You are given the following base interpreter:

```python
from dataclasses import dataclass, field
from typing import Any, Optional

@dataclass
class Env:
    bindings: dict = field(default_factory=dict)
    parent: Optional['Env'] = None
    
    def define(self, name: str, value: Any):
        self.bindings[name] = value
    
    def lookup(self, name: str) -> Any:
        if name in self.bindings:
            return self.bindings[name]
        if self.parent:
            return self.parent.lookup(name)
        raise NameError(f"Undefined: '{name}'")
    
    def assign(self, name: str, value: Any):
        if name in self.bindings:
            self.bindings[name] = value
            return
        if self.parent:
            self.parent.assign(name, value)
            return
        raise NameError(f"Cannot assign undefined: '{name}'")

# AST node types
@dataclass
class Num:
    value: float

@dataclass
class Var:
    name: str

@dataclass
class BinOp:
    op: str
    left: Any
    right: Any

@dataclass
class Let:
    name: str
    value: Any
    body: Any

def eval_node(node, env: Env) -> Any:
    if isinstance(node, Num):
        return node.value
    if isinstance(node, Var):
        return env.lookup(node.name)
    if isinstance(node, BinOp):
        l = eval_node(node.left, env)
        r = eval_node(node.right, env)
        ops = {'+': l+r, '-': l-r, '*': l*r, '/': l/r}
        return ops[node.op]
    if isinstance(node, Let):
        val = eval_node(node.value, env)
        new_env = Env(parent=env)
        new_env.define(node.name, val)
        return eval_node(node.body, new_env)
    raise ValueError(f"Unknown node: {type(node)}")
```

### Step 4a: ModuleEnv and ModuleRegistry

Add:

```python
@dataclass
class ModuleRegistry:
    modules: dict = field(default_factory=dict)
    loading: set = field(default_factory=set)  # for cycle detection
    
    def register(self, name: str, env: Env):
        self.modules[name] = env
    
    def load(self, name: str) -> Env:
        if name in self.loading:
            raise ImportError(f"Circular import detected: '{name}'")
        if name in self.modules:
            return self.modules[name]
        raise ImportError(f"No module named '{name}'")
```

### Step 4b: Import AST Nodes and Eval Cases

Add two new AST nodes and their eval cases:

**`Import(module_name, alias)`** — binds the module object under `alias` (or `module_name` if alias is `None`) in the current env.

**`GetAttr(obj_expr, attr_name)`** — evaluates `obj_expr` to a module dict, then looks up `attr_name` in that dict.

```python
@dataclass
class Import:
    module_name: str
    alias: Optional[str] = None

@dataclass
class GetAttr:
    obj_expr: Any
    attr_name: str
```

Extend `eval_node`:

```python
if isinstance(node, Import):
    mod_env = registry.load(node.module_name)
    module_obj = {"__name__": node.module_name, "__env__": mod_env}
    bind_name = node.alias or node.module_name
    env.define(bind_name, module_obj)
    return module_obj

if isinstance(node, GetAttr):
    obj = eval_node(node.obj_expr, env)
    if isinstance(obj, dict) and "__env__" in obj:
        return obj["__env__"].lookup(node.attr_name)
    raise TypeError(f"Cannot get attribute of {type(obj)}")
```

You'll need to thread `registry` through `eval_node`. Change its signature to `eval_node(node, env, registry=None)`.

### Step 4c: From-Import

Add **`FromImport(module_name, names)`** which copies specific names from a module into the current env:

```python
@dataclass
class FromImport:
    module_name: str
    names: list  # list of str
```

Implement it in `eval_node`.

### Step 4d: Test

Write at least three tests:

```python
# Test 1: import a module and access its values
mymath = Env()
mymath.define("PI", 3.14159)
mymath.define("add", lambda a, b: a + b)

registry = ModuleRegistry()
registry.register("mymath", mymath)

global_env = Env()
# import mymath
result = eval_node(Import("mymath"), global_env, registry)
# mymath.PI
pi = eval_node(GetAttr(Var("mymath"), "PI"), global_env, registry)
assert abs(pi - 3.14159) < 1e-5, f"Expected ~3.14159, got {pi}"
print(f"Test 1 passed: mymath.PI = {pi}")

# Test 2: from-import
global_env2 = Env()
eval_node(FromImport("mymath", ["PI", "add"]), global_env2, registry)
assert global_env2.lookup("PI") == 3.14159
print("Test 2 passed: from-import works")

# Test 3: circular import detection
circ_env = Env()
registry2 = ModuleRegistry()
registry2.loading.add("circ")  # simulate mid-load state
try:
    registry2.load("circ")
    print("Test 3 FAILED: should have raised ImportError")
except ImportError as e:
    print(f"Test 3 passed: {e}")
```

---

## Deliverables

Submit a ZIP containing:
- `minimath/` — the complete package directory
- `test_minimath.py` — Part 1 tests
- `plugins/` — the plugin directory with at least 3 valid plugins and 1 broken plugin
- `loader.py` — Part 2 plugin loader
- `main.py` — Part 2 driver
- `namespace_exercises.py` — Part 3 exercises with predicted vs actual outputs as comments
- `interpreter.py` — Part 4 extended interpreter
- `test_interpreter.py` — Part 4 tests
- `readme.md` — approximately one page including the LEGB diagram, the dynamic-scoping comparison, and the reflection

---

## Grading Breakdown

| Component | Points |
|-----------|--------|
| Part 1: Package Structure and Public API | 25 |
| Part 2: Dynamic Plugin System | 25 |
| Part 3: Namespace Analysis | 25 |
| Part 4: Mini Interpreter Module System | 25 |
| **Total** | **100** |

---

## Reflection Prompts

- Python's module system uses a global cache (`sys.modules`). What is the benefit of this design? What problem would arise without it? Give a concrete scenario involving circular imports.
- In Part 2, the plugin loader validates the interface with `hasattr`. How does this compare to how a statically-typed language (like Java) enforces interface contracts? What is lost and what is gained?
- In Part 4, each module gets its own `Env`. How does this relate to the concept of closures you explored in the Functional Programming assignment? In what sense is a module a closure over its top-level definitions?
- If collaboration with a buddy was permitted, did you work with a buddy on this assignment? If so, who? If not, do you certify that this submission represents your own original work? Please identify any and all portions of your submission that were not originally written by you.
- Approximately how many hours it took you to finish this assignment?
