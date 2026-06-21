<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://github.com/BillJr99/Ursinus-CS374-Fall2026/blob/gh-pages/_pages/Activities/liascript-libraries.md

import: https://raw.githubusercontent.com/liascript/CodeRunner/master/README.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

# Libraries and Modules in Programming Languages

Every non-trivial program is an assembly of parts: code you wrote, code your colleagues wrote, and code the language ecosystem provides. The mechanisms that let these parts coexist — without stomping on each other's names, without loading code you don't need, and without requiring every collaborator to agree on internal naming — are collectively called the **module system**. Today you dissect Python's module system from the outside in, and then build a miniature one from scratch.

Arc: **the problem modules solve → namespaces and name lookup → dynamic loading → controlling the public API → implementing a module system**

---

## Directions and Group Roles

Work in your POGIL team with rotated roles (**Manager**, **Recorder**, **Presenter**, **Reflector**). Consider each model individually first, then discuss with your group.

---

# Part I: The Module System from the Outside

## Model 1: Python's Module System

A Python module is just a `.py` file whose top-level bindings become the module's **namespace**. `import` evaluates that file (once) and caches the resulting namespace object. The cache — `sys.modules` — prevents re-execution on repeated imports and is the source of truth for "is this module loaded?"

```python  liascript
import sys
import math
import os.path

# A module is a first-class object
print(type(math))             # <class 'module'>
print(dir(math)[:10])         # first 10 attributes of the module
print(math.pi)                # accessing a module-level name
print(math.__file__)          # where the module lives on disk

# sys.modules is the module cache
print('math' in sys.modules)  # True — already imported
print('json' in sys.modules)  # False if not yet imported

import json
print('json' in sys.modules)  # True now

# __name__ behavior
print(f"This file's __name__: {__name__}")
# When run directly: __main__; when imported: the module name
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

**Critical Thinking Questions (CTQs)**

> **CTQ 1.1** What is the difference between `import math` and `from math import pi`? After each form, what names appear in the calling module's namespace?

> **CTQ 1.2** `sys.modules` is a plain dictionary. What happens if you delete a key from it and then re-import the corresponding module? (Think through the logic of `import` before running any code.)

> **CTQ 1.3** What does the guard `if __name__ == '__main__':` check? Give a concrete scenario where forgetting this guard causes an unintended side effect when your file is imported by someone else.

> **CTQ 1.4** `math.__file__` shows the `.py` or `.so` path. Why might a module not have a `__file__` attribute at all? Name one category of Python module where this is true.

---

## Model 2: Namespaces and Symbol Tables

Python resolves every name by searching a chain of **namespaces** from innermost to outermost. The rule is called **LEGB**: Local → Enclosing → Global → Built-in. Each scope is a dictionary, and `globals()`, `locals()`, and `vars()` expose them at runtime.

```python  liascript
# Global namespace
x = 10
y = 20

def outer():
    # Enclosing namespace
    a = 100
    def inner():
        # Local namespace
        b = 200
        print(f"local vars:    {sorted(locals().keys())}")
        print(f"b={b}, a={a}, x={x}")   # LEGB lookup: b→local, a→enclosing, x→global
    inner()
    print(f"outer locals:  {sorted(locals().keys())}")

outer()

# Inspect the global namespace
g = globals()
print(f"\nglobal names: {sorted(k for k in g.keys() if not k.startswith('_'))}")

# Modules have their own namespace
import math
print(f"\nmath namespace sample: {[k for k in dir(math) if not k.startswith('_')][:8]}")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

> **CTQ 2.1** Describe the LEGB rule in your own words. If a name appears in both the local scope and the global scope, which one does Python use? What would you write to explicitly access the global one?

> **CTQ 2.2** What does `globals()` return? Is it a snapshot or a live view? Write a one-line expression that adds a new global variable at runtime using `globals()`.

> **CTQ 2.3** A module's namespace is stored in `module.__dict__`. What does that tell you about how `import math; math.pi` is implemented under the hood? Trace the attribute lookup.

> **CTQ 2.4** Python's built-in scope (the `B` in LEGB) holds names like `len`, `print`, and `True`. Where is this namespace stored? How would you shadow `len` for a single function without affecting the rest of the program?

---

# Part II: Dynamic Loading and API Control

## Model 3: Dynamic Loading with importlib

Static `import` statements are resolved at parse time (or at least before the function body runs). **Dynamic loading** resolves a module name given only as a runtime string — essential for plugin architectures, configuration-driven dispatch, and test harnesses.

```python  liascript
import importlib
import sys

# Dynamic import by string name
module_name = "math"
mod = importlib.import_module(module_name)
print(f"Dynamically loaded: {mod.__name__}")
print(f"sqrt(16) = {mod.sqrt(16)}")

# Get an attribute dynamically
func_name = "factorial"
func = getattr(mod, func_name, None)
if func:
    print(f"math.{func_name}(5) = {func(5)}")
else:
    print(f"{func_name} not found in {module_name}")

# Simulate a plugin system
PLUGINS = ["math", "os.path", "json"]
loaded = {}
for name in PLUGINS:
    try:
        loaded[name] = importlib.import_module(name)
        print(f"Loaded plugin: {name}")
    except ImportError as e:
        print(f"Failed to load {name}: {e}")

print(f"\nLoaded plugins: {list(loaded.keys())}")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

> **CTQ 3.1** What is the difference between `import math` (static) and `importlib.import_module("math")` (dynamic)? When is each approach appropriate?

> **CTQ 3.2** A plugin system reads plugin names from a config file and loads them at startup. List two concrete benefits of dynamic loading over listing every plugin with a static `import`. What would need to change in the code to add a new plugin?

> **CTQ 3.3** `getattr(mod, func_name, None)` returns `None` if the attribute does not exist, rather than raising `AttributeError`. How does this pattern relate to the "ask forgiveness, not permission" idiom in Python? When would you prefer `hasattr` + `getattr` instead?

> **CTQ 3.4** What security concern does dynamic loading introduce when the module name comes from user input? Describe a minimal mitigation strategy.

---

## Model 4: `__all__`, `__init__.py`, and Module Interfaces

A module's **public interface** is the set of names that clients are expected to use. Python enforces this convention through `__all__`: a list of names that `from module import *` will bind in the caller's namespace. Without `__all__`, the star import brings in every name that does not start with `_`.

```python  liascript
# Simulate a package's __all__ behavior
# A module can declare its public API via __all__

# Imagine this is mypackage/__init__.py:
_private_helper = "internal only"
public_api_function = "this is exported"

__all__ = ["public_api_function", "MyClass"]

class MyClass:
    def __init__(self, value):
        self.value = value
    def greet(self):
        return f"Hello from {self.value}"

class _InternalClass:
    pass

# When someone does: from mypackage import *
# they get only what's in __all__
print(f"__all__ = {__all__}")

# Demonstrate: what 'import *' would bring in from math
exec("from math import *")   # imports everything in math.__all__
import math
print(f"\nmath.__all__ exists: {hasattr(math, '__all__')}")
print(f"math has {len(dir(math))} total names")
print(f"pi is now in globals: {'pi' in dir()}")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

> **CTQ 4.1** What is the purpose of `__all__`? What happens with `from module import *` when `__all__` is defined? What happens when it is not defined?

> **CTQ 4.2** `_InternalClass` starts with an underscore. Even without `__all__`, `from module import *` will not import it. What is the convention here? Does the underscore prefix provide any real access control?

> **CTQ 4.3** Why does **namespace pollution** matter? Give a concrete example where `from module import *` in two successive lines could silently break a program.

> **CTQ 4.4** A Python **package** is a directory containing an `__init__.py`. When you write `import mypackage.submodule`, which file runs first? What is `__init__.py` for?

---

# Part III: Building a Module System

## Model 5: Implementing a Module System in a Mini Interpreter

The models above described Python's module system as a user. Now we build one. The core idea is simple: a **module** is an **environment** (a namespace), and a **module registry** is a dictionary from names to environments — exactly what `sys.modules` is.

```python  liascript
from dataclasses import dataclass, field
from typing import Any, Optional

@dataclass
class Env:
    """An environment (namespace) for the interpreter."""
    bindings: dict = field(default_factory=dict)
    parent: Optional['Env'] = None

    def define(self, name: str, value: Any):
        self.bindings[name] = value

    def lookup(self, name: str) -> Any:
        if name in self.bindings:
            return self.bindings[name]
        if self.parent:
            return self.parent.lookup(name)
        raise NameError(f"Undefined: {name}")

@dataclass
class ModuleRegistry:
    """Registry of loaded modules — like sys.modules."""
    modules: dict = field(default_factory=dict)

    def register(self, name: str, env: Env):
        self.modules[name] = env

    def load(self, name: str) -> Env:
        if name in self.modules:
            return self.modules[name]
        raise ImportError(f"No module named '{name}'")

# Simulate building a stdlib module
stdlib_env = Env()
stdlib_env.define("add", lambda a, b: a + b)
stdlib_env.define("mul", lambda a, b: a * b)
stdlib_env.define("PI", 3.14159)

# Register it in the module system
registry = ModuleRegistry()
registry.register("mymath", stdlib_env)

# Simulate "import mymath"
def do_import(registry: ModuleRegistry, module_name: str, global_env: Env):
    mod_env = registry.load(module_name)
    # Create a module object in global_env
    module_obj = {"__name__": module_name, "__env__": mod_env}
    global_env.define(module_name, module_obj)
    return module_obj

# User code: import mymath, call mymath.add(2, 3)
user_env = Env()
mod = do_import(registry, "mymath", user_env)
add_fn = mod["__env__"].lookup("add")
print(f"mymath.add(2, 3) = {add_fn(2, 3)}")
print(f"mymath.PI        = {mod['__env__'].lookup('PI')}")

# Verify the registry now holds the module
print(f"'mymath' in registry: {'mymath' in registry.modules}")

# Simulate "from mymath import mul"
def do_from_import(registry: ModuleRegistry, module_name: str,
                   name: str, target_env: Env):
    mod_env = registry.load(module_name)
    value = mod_env.lookup(name)
    target_env.define(name, value)

do_from_import(registry, "mymath", "mul", user_env)
mul_fn = user_env.lookup("mul")
print(f"mul(3, 4) = {mul_fn(3, 4)}")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

> **CTQ 5.1** How does `ModuleRegistry` relate to Python's `sys.modules`? What key operation does `registry.load` correspond to in the real import system?

> **CTQ 5.2** `do_import` binds a **module object** (a dict) into `global_env`. In Python, `import math` creates a name `math` in the caller's namespace that refers to the module object. Trace the parallel: what is the module object in Python, and how does attribute access (`math.pi`) work in terms of the module's `__dict__`?

> **CTQ 5.3** `do_from_import` copies a single binding from the module's environment into the caller's environment. After `from mymath import mul`, if you redefine `mymath.mul` in the registry, does the caller's `mul` reflect the change? Why or why not?

> **CTQ 5.4** To support **circular imports** (module A imports B, B imports A), what single change to `do_import` would prevent infinite recursion? (Hint: look at how Python handles this with a partially-initialized module entry in `sys.modules`.)

---

[[MC]]
What does `sys.modules` contain?

    [(x)] A cache of all already-imported modules
    [( )] The list of directories Python searches for modules
    [( )] The set of built-in Python functions
    [( )] The currently executing module's globals

---

[[MC]]
What is the purpose of `__all__` in a Python module?

    [(x)] It controls which names are exported with `from module import *`
    [( )] It lists all function names defined in the module
    [( )] It speeds up import by pre-caching attribute lookups
    [( )] It defines the module's required dependencies

---

[[MC]]
What is a Python **package**?

    [(x)] A directory containing an `__init__.py` file that groups related modules
    [( )] A single `.py` source file
    [( )] A compiled `.pyc` bytecode file
    [( )] A zip archive of modules installed by pip

---

[[MC]]
In the LEGB rule, when Python looks up variable `x`, where does it look **last**?

    [( )] Local scope
    [( )] Enclosing scope
    [( )] Global scope
    [(x)] Built-in scope

---

## Exercises

### Exercise 1 — Lazy Import Cache (20 min)

Write a `lazy_import(name)` function that returns a proxy: the first time the proxy is used (e.g., its attribute is accessed), it imports the module and caches it; subsequent accesses use the cached copy. You may use a plain dict as the cache. Demonstrate that the module is only loaded on first access by printing a message inside the import logic.

- (a) Implement `lazy_import(name)` returning a callable proxy object.
- (b) Show that calling `lazy_import("math")` twice loads the module only once.
- (c) Explain how this pattern is used in large frameworks to reduce startup time.

### Exercise 2 — Namespace Merge (15 min)

Implement `namespace_merge(ns1: dict, ns2: dict) -> dict` that merges two namespace dicts. If the same name appears in both, raise a custom `NamespaceConflict` exception that includes the conflicting name in its message.

- (a) Implement `NamespaceConflict` as a subclass of `Exception`.
- (b) Implement `namespace_merge` and test it with two disjoint dicts (should succeed) and two dicts with a shared key (should raise).
- (c) When would namespace merging arise in a real language runtime? (Hint: think about `import *` from two modules.)

### Exercise 3 — `from module import name` in the Mini Interpreter (25 min)

Extend the `ModuleRegistry` from Model 5 to support `from module import name` more robustly.

- (a) Add a `do_from_import_star(registry, module_name, target_env)` function that imports all names from the module (simulating `from module import *`).
- (b) Add optional `__all__` support: if `module_env` contains a binding for `"__all__"` (a list of strings), only import those names.
- (c) Demonstrate with a module that defines `__all__ = ["add", "PI"]` but also contains `_secret = 42`.

### Exercise 4 — Module Reload (20 min)

Write a `reload_module(name, registry, init_fn)` function that re-executes a module's initialization code (simulating Python's `importlib.reload`). `init_fn` is a callable that takes an `Env` and populates it.

- (a) Implement `reload_module` so it creates a fresh `Env`, calls `init_fn` on it, and updates the registry entry.
- (b) Show that code holding a reference to the **old** module object does not see the reload, but code that looks up the module via the registry does.
- (c) When is `importlib.reload` useful in practice? When is it dangerous?

---

## Reflection Prompt

Python, JavaScript (ESM/CommonJS), and Java each solved the module problem differently — Python uses a flat file-based namespace with a global cache; JavaScript ESM uses static graph analysis with live bindings; Java uses a class-loader hierarchy with explicit visibility modifiers. What are the fundamental design decisions every module system must make? Consider: separate compilation and link-time resolution, circular imports, versioning and diamond dependency problems, granularity of privacy (file, class, function), and the cost of loading code that is never used. Which design choices does Python's module system get right, and where does it show its age?

---

## Further Reading

- **Python import system documentation** — https://docs.python.org/3/reference/import.html : the authoritative description of finders, loaders, and `sys.modules`
- **PEP 328** — Imports: Multi-Line and Absolute/Relative: the rationale for Python's relative import syntax
- **PEP 302** — New Import Hooks: how to plug custom loaders into the import machinery
- **"Node.js module system"** — MDN/Node.js docs: CommonJS (`require`) vs ES Modules (`import`), and why the two coexist uneasily
- **PLAI Chapter 10** — Krishnamurthi: Recursion and Modules — a language-theoretic treatment of modules as first-class values
- **"Modular Programming with Python"** — Erik Westra: practical patterns for large Python codebases
