<!--
author:   CS374 Course Team
email:    
version:  0.0.1
language: en
narrator: US English Female
comment:  Error Handling Strategies — Return Codes, Exceptions, Option/Maybe, Result/Either, Monadic Propagation, Interpreter Error Design
import:   https://raw.githubusercontent.com/liaScript/coderunner/master/README.md
link:     https://cdn.jsdelivr.net/chartist.min.css
-->

# Error Handling: From Return Codes to Algebraic Effects

## Learning Goals

By the end of this activity, you will be able to:

- Compare error-handling strategies (return codes, checked/unchecked exceptions, Option/Maybe, Result/Either) and identify the tradeoffs each makes in static safety, composability, and caller burden
- Implement the Option and Result types in Python and use them to propagate errors without exceptions
- Apply monadic chaining (`flatMap`/`bind`) to thread errors through a pipeline without nested conditionals
- Analyze how a language's error strategy shapes the user experience of writing and reading code in that language
- Design error handling for a mini interpreter, choosing an appropriate strategy and justifying the choice

> **Prerequisites:** Python programming, familiarity with exceptions, basic type system concepts
> **Goal:** Compare how different languages approach errors — return codes, checked/unchecked exceptions, Option/Maybe, Result/Either, monadic propagation — and understand how each choice shapes language design and user experience.

**POGIL Roles:** Driver · Recorder · Reporter · Manager

---

## Preface: Why Error Handling Is a Language Design Problem

Every program encounters errors: bad input, missing files, network failures, type mismatches, division by zero. A language's error handling strategy determines:

- **When** errors are detected (statically vs. dynamically)
- **How** errors are represented (return values, exceptions, types)
- **Who** is responsible for handling them (caller vs. callee)
- **What** happens when errors are ignored (silently continue, crash, type error)
- **How** errors compose (deeply nested error propagation)

There is no single best answer — each approach makes different tradeoffs, and understanding them will inform how you design error handling in your own interpreter.

---

## Model 1: Return Codes — The C Approach

The oldest strategy: functions return a special value (typically -1 or NULL) to signal failure. The caller is responsible for checking the return value.

```python
# Simulating the C-style return code pattern in Python
import os
import errno as errno_module

# Simulate a C-style library with return code conventions
ENOENT = 2    # No such file or directory
EACCES = 13   # Permission denied
EINVAL = 22   # Invalid argument

def c_style_open(filename, mode):
    """Returns (fd, errno_code). fd=-1 on error."""
    if not isinstance(filename, str):
        return -1, EINVAL
    if filename == "/etc/shadow":
        return -1, EACCES
    if not filename.startswith("/") and "." not in filename:
        return -1, ENOENT
    # Success: return a fake fd and errno=0
    return 42, 0

def c_style_read(fd, nbytes):
    """Returns (data, errno_code). data=None on error."""
    if fd < 0:
        return None, EINVAL
    if fd == 42:
        return "file contents", 0
    return None, ENOENT

# Caller must check EVERY return value
print("=== C-style return code usage ===")

fd, err = c_style_open("myfile.txt", "r")
if err != 0:
    print(f"open failed: errno={err}")
else:
    data, err = c_style_read(fd, 1024)
    if err != 0:
        print(f"read failed: errno={err}")
    else:
        print(f"read succeeded: {data!r}")

print()
print("=== What happens if caller forgets to check? ===")
fd2, _ = c_style_open("/etc/shadow", "r")   # error ignored
data2, _ = c_style_read(fd2, 1024)          # called with invalid fd
print(f"data2 = {data2!r}")   # None — silently wrong

print()
print("=== The errno global pattern (real C) ===")
# In real C, errno is a global modified as a side effect
# This breaks in multithreaded code unless errno is thread-local
try:
    with open("nonexistent_file_xyz.txt") as f:
        pass
except OSError as e:
    print(f"Python wraps errno: e.errno={e.errno}, e.strerror={e.strerror!r}")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

**The fundamental problem with return codes:** They can be silently ignored. The language provides no mechanism to force the caller to check. In large codebases, forgotten checks cause mysterious bugs far from the actual failure.

> **Critical Thinking Questions 1–3**

**CTQ 1.** In the example above, `c_style_read(fd2, 1024)` is called with an invalid fd and returns `None` silently. What real-world bugs does this pattern cause? Give a concrete example from systems programming.

[[___ your answer here ___]]

**CTQ 2.** The `errno` global variable breaks in multi-threaded C programs. Why? What does this tell you about global mutable state as an error mechanism?

[[___ your answer here ___]]

**CTQ 3.** Return codes have one significant advantage over exceptions: they are explicit in the type signature. `int read(int fd, void *buf, size_t count)` returns -1 on error. How does this relate to the caller-callee contract in a statically typed language?

[[___ your answer here ___]]

---

## Model 2: Exceptions — Non-Local Control Flow

Exceptions decouple error signaling from error handling. A function can raise an exception at any depth; the nearest matching `catch`/`except` in the call stack handles it.

```python
import traceback

# Python: unchecked exceptions — no declaration required
def parse_int(s):
    return int(s)   # raises ValueError if s is not a valid integer

def read_config(filename):
    with open(filename) as f:   # raises FileNotFoundError or PermissionError
        return f.read()

def process(filename):
    text = read_config(filename)
    value = parse_int(text.strip())
    return value * 2

print("=== Unchecked exceptions (Python style) ===")
print("1. Happy path:")
try:
    # create a temp file
    with open("/tmp/test_config.txt", "w") as f:
        f.write("  42  ")
    print(f"   result = {process('/tmp/test_config.txt')}")
except Exception as e:
    print(f"   error: {e}")

print("2. File not found:")
try:
    print(f"   result = {process('/nonexistent/file.txt')}")
except FileNotFoundError as e:
    print(f"   caught FileNotFoundError: {e}")

print("3. Bad integer:")
try:
    with open("/tmp/test_config.txt", "w") as f:
        f.write("not a number")
    print(f"   result = {process('/tmp/test_config.txt')}")
except ValueError as e:
    print(f"   caught ValueError: {e}")

print("4. Catching too broadly (dangerous):")
try:
    print(f"   result = {process('/nonexistent.txt')}")
except Exception as e:
    print(f"   caught ANYTHING: {type(e).__name__}: {e}")
    # We swallowed a bug — maybe KeyboardInterrupt?

print()
print("=== Exception hierarchy ===")
# Python exceptions form a tree: BaseException > Exception > ...
examples = [ValueError("bad"), TypeError("type"), FileNotFoundError("no file"),
            KeyboardInterrupt(), MemoryError()]
for ex in examples:
    mro = [c.__name__ for c in type(ex).__mro__]
    print(f"  {type(ex).__name__}: {' > '.join(mro[:4])}")

print()
print("=== finally: the cleanup guarantee ===")
class Resource:
    def __init__(self, name):
        self.name = name
        print(f"  opened {name}")
    def close(self):
        print(f"  closed {self.name}")

def risky_operation(r, should_fail):
    try:
        if should_fail:
            raise RuntimeError("something went wrong")
        return "success"
    finally:
        r.close()   # ALWAYS runs, even on exception

r = Resource("db_connection")
try:
    result = risky_operation(r, should_fail=True)
except RuntimeError as e:
    print(f"  caught: {e}")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

### Checked vs. Unchecked Exceptions

**Java-style checked exceptions:** The compiler forces callers to either catch or declare every checked exception. `IOException`, `SQLException` are checked; `NullPointerException`, `ArrayIndexOutOfBoundsException` are unchecked.

**Python/C++/C#-style unchecked exceptions:** No compile-time enforcement. Callers may or may not catch. The risk: a function silently throws an exception that callers don't know about.

> **Critical Thinking Questions 4–6**

**CTQ 4.** In Python, `except Exception` catches almost every exception. Why is this considered dangerous? What would a disciplined exception-handling policy look like?

[[___ your answer here ___]]

**CTQ 5.** Java's checked exceptions were controversial and were rejected in C# and Kotlin. The argument against: they pollute call signatures with exception declarations that bubble all the way up. The argument for: callers can't ignore failure modes. Which position do you find more compelling? Why?

[[___ your answer here ___]]

**CTQ 6.** Exceptions are a form of non-local control flow — they break the normal call/return pattern. A function that throws "jumps" to a catch block potentially many frames up the call stack. What debugging challenges does this create compared to return codes?

[[___ your answer here ___]]

---

## Model 3: Option / Maybe — Explicit Absence

Many errors boil down to "there is no value here." The **Option** type (Haskell's `Maybe`, Rust's `Option`, Scala's `Option`) makes absence explicit in the type system rather than using `null` or raising an exception.

```python
from __future__ import annotations
from dataclasses import dataclass
from typing import TypeVar, Generic, Callable

T = TypeVar("T")
U = TypeVar("U")

@dataclass(frozen=True)
class Some(Generic[T]):
    value: T
    def is_some(self): return True
    def is_none(self): return False
    def unwrap(self): return self.value
    def map(self, f: Callable[[T], U]) -> "Option[U]":
        return Some(f(self.value))
    def and_then(self, f: Callable[[T], "Option[U]"]) -> "Option[U]":
        return f(self.value)
    def unwrap_or(self, default: T) -> T:
        return self.value
    def __repr__(self): return f"Some({self.value!r})"

@dataclass(frozen=True)
class Nothing:
    def is_some(self): return False
    def is_none(self): return True
    def unwrap(self): raise ValueError("called unwrap() on Nothing")
    def map(self, f): return self
    def and_then(self, f): return self
    def unwrap_or(self, default): return default
    def __repr__(self): return "Nothing"

Option = Some | Nothing
NOTHING = Nothing()

# Functions that might fail return Option instead of raising
def safe_div(x: float, y: float) -> Option:
    if y == 0:
        return NOTHING
    return Some(x / y)

def safe_head(lst: list) -> Option:
    if not lst:
        return NOTHING
    return Some(lst[0])

def parse_positive_int(s: str) -> Option:
    try:
        n = int(s)
        return Some(n) if n > 0 else NOTHING
    except ValueError:
        return NOTHING

print("=== Option/Maybe usage ===")
print(safe_div(10, 2))        # Some(5.0)
print(safe_div(10, 0))        # Nothing
print(safe_head([1, 2, 3]))   # Some(1)
print(safe_head([]))          # Nothing

print()
print("=== Chaining with and_then (flatMap) ===")
# Process: parse → divide → take head
def pipeline(s: str, divisor: float) -> Option:
    return (parse_positive_int(s)
            .map(float)
            .and_then(lambda x: safe_div(x, divisor)))

print(f"pipeline('12', 4)   = {pipeline('12', 4)}")    # Some(3.0)
print(f"pipeline('12', 0)   = {pipeline('12', 0)}")    # Nothing (div by zero)
print(f"pipeline('-5', 4)   = {pipeline('-5', 4)}")    # Nothing (not positive)
print(f"pipeline('abc', 4)  = {pipeline('abc', 4)}")   # Nothing (parse fail)

print()
print("=== unwrap_or for defaults ===")
result = pipeline("bad", 4).unwrap_or(0.0)
print(f"pipeline('bad', 4).unwrap_or(0.0) = {result}")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

> **Critical Thinking Questions 7–9**

**CTQ 7.** The Option type forces callers to handle the absence case explicitly (they can't just use the value without checking). How does this differ from the behavior of `None` in Python, where calling a method on `None` raises `AttributeError` at runtime?

[[___ your answer here ___]]

**CTQ 8.** `and_then` (also called `flatMap` or `>>=` in Haskell) sequences Option computations so that if any step returns `Nothing`, the whole chain returns `Nothing`. What is the control flow equivalent of this? (Hint: think about what happens in an imperative `if ... return None` chain.)

[[___ your answer here ___]]

**CTQ 9.** Python's `Optional[T]` type hint (`from typing import Optional`) annotates a value that may be `None`. How does this differ from the `Option` type implemented above, in terms of static guarantees?

[[___ your answer here ___]]

---

## Model 4: Result / Either — Typed Errors

Option discards error information ("it failed" but not "why it failed"). **Result** (Rust, Swift) or **Either** (Haskell) carries both the success value and a structured error value.

```python
from __future__ import annotations
from dataclasses import dataclass
from typing import TypeVar, Generic, Callable

T = TypeVar("T")
E = TypeVar("E")
U = TypeVar("U")

@dataclass(frozen=True)
class Ok(Generic[T]):
    value: T
    def is_ok(self): return True
    def is_err(self): return False
    def unwrap(self): return self.value
    def unwrap_err(self): raise ValueError("called unwrap_err() on Ok")
    def map(self, f): return Ok(f(self.value))
    def map_err(self, f): return self
    def and_then(self, f): return f(self.value)
    def __repr__(self): return f"Ok({self.value!r})"

@dataclass(frozen=True)
class Err(Generic[E]):
    error: E
    def is_ok(self): return False
    def is_err(self): return True
    def unwrap(self): raise ValueError(f"called unwrap() on Err({self.error!r})")
    def unwrap_err(self): return self.error
    def map(self, f): return self
    def map_err(self, f): return Err(f(self.error))
    def and_then(self, f): return self
    def __repr__(self): return f"Err({self.error!r})"

# Result = Ok[T] | Err[E]
# Richer errors: use a dataclass hierarchy
@dataclass(frozen=True)
class ParseError:
    input: str
    message: str

@dataclass(frozen=True)
class MathError:
    operation: str
    message: str

@dataclass(frozen=True)
class IOError_:
    filename: str
    message: str

def parse_number(s: str):
    try:
        return Ok(float(s))
    except ValueError:
        return Err(ParseError(s, f"cannot parse {s!r} as number"))

def safe_sqrt(x: float):
    if x < 0:
        return Err(MathError("sqrt", f"sqrt of negative: {x}"))
    import math
    return Ok(math.sqrt(x))

def load_number(filename: str):
    try:
        with open(filename) as f:
            return parse_number(f.read().strip())
    except FileNotFoundError:
        return Err(IOError_(filename, "file not found"))

print("=== Result type ===")
print(parse_number("3.14"))     # Ok(3.14)
print(parse_number("xyz"))      # Err(ParseError(...))
print(safe_sqrt(9.0))           # Ok(3.0)
print(safe_sqrt(-1.0))          # Err(MathError(...))

print()
print("=== Chaining Results ===")
def process(s: str):
    return parse_number(s).and_then(safe_sqrt)

print(f"process('9')   = {process('9')}")
print(f"process('-1')  = {process('-1')}")
print(f"process('abc') = {process('abc')}")

print()
print("=== Pattern matching on Result (Python 3.10+) ===")
for test in ["16", "-4", "not_a_number"]:
    result = process(test)
    match result:
        case Ok(value=v):
            print(f"  sqrt({test}) = {v:.4f}")
        case Err(error=ParseError(input=i, message=m)):
            print(f"  parse error for {i!r}: {m}")
        case Err(error=MathError(operation=op, message=m)):
            print(f"  math error in {op}: {m}")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

> **Critical Thinking Questions 10–12**

**CTQ 10.** `Err` carries a *typed* error value. What advantage does this have over Python's exception hierarchy where you catch by exception class? Give a scenario where typed errors are significantly cleaner.

[[___ your answer here ___]]

**CTQ 11.** In Rust, if you call `.unwrap()` on an `Err`, the program panics (crashes with a message). This is intentional: `unwrap()` is a way of saying "I know this can't fail, and if it does, crash loudly." How does this compare to the `except Exception` anti-pattern in Python?

[[___ your answer here ___]]

**CTQ 12.** Rust's `?` operator desugars to: "if this is `Err`, return the error from the current function; otherwise, unwrap the `Ok` value." Implement a Python decorator or helper that provides similar behavior for the `Result` type above:

```python
# Your implementation of a "question mark operator" helper
# (This one doesn't need @LIA.eval — think about it with your group)
```

How would you use it to write a multi-step `Result`-chaining function without deeply nested `and_then` calls?

[[___ your answer here ___]]

---

## Model 5: Error Propagation in Your Interpreter

Your interpreter must handle runtime errors: undefined variables, type mismatches, division by zero, stack overflow. How you design this affects usability.

```python
from dataclasses import dataclass
from typing import Any, Optional

@dataclass
class SourceLocation:
    line: int
    column: int
    def __str__(self):
        return f"line {self.line}, col {self.column}"

@dataclass
class InterpreterError(Exception):
    message: str
    location: Optional[SourceLocation] = None
    def __str__(self):
        loc = f" at {self.location}" if self.location else ""
        return f"RuntimeError{loc}: {self.message}"

@dataclass
class UndefinedVariableError(InterpreterError):
    name: str = ""
    def __str__(self):
        loc = f" at {self.location}" if self.location else ""
        return f"UndefinedVariable{loc}: '{self.name}' is not defined"

@dataclass
class TypeMismatchError(InterpreterError):
    expected: str = ""
    got: str = ""
    def __str__(self):
        loc = f" at {self.location}" if self.location else ""
        return f"TypeError{loc}: expected {self.expected}, got {self.got}"

@dataclass
class DivisionByZeroError(InterpreterError):
    def __str__(self):
        loc = f" at {self.location}" if self.location else ""
        return f"DivisionByZero{loc}"

# A mini environment + evaluator that produces good errors
class Environment:
    def __init__(self, parent=None):
        self.bindings = {}
        self.parent = parent

    def lookup(self, name: str, loc: SourceLocation = None) -> Any:
        if name in self.bindings:
            return self.bindings[name]
        if self.parent:
            return self.parent.lookup(name, loc)
        raise UndefinedVariableError(
            message=f"'{name}' is not defined",
            location=loc,
            name=name
        )

    def define(self, name: str, value: Any):
        self.bindings[name] = value

def eval_binop(op: str, left: Any, right: Any, loc: SourceLocation) -> Any:
    if op == "+":
        if isinstance(left, (int, float)) and isinstance(right, (int, float)):
            return left + right
        if isinstance(left, str) and isinstance(right, str):
            return left + right
        raise TypeMismatchError(
            message=f"operator '+' requires matching numeric or string operands",
            location=loc,
            expected="int/float or str",
            got=f"{type(left).__name__} and {type(right).__name__}"
        )
    if op == "/":
        if not isinstance(left, (int, float)):
            raise TypeMismatchError(message="'/' requires numbers", location=loc,
                                    expected="number", got=type(left).__name__)
        if right == 0:
            raise DivisionByZeroError(message="division by zero", location=loc)
        return left / right
    raise InterpreterError(f"unknown operator '{op}'", loc)

print("=== Good interpreter error messages ===")
env = Environment()
env.define("x", 10)
env.define("name", "Alice")

loc1 = SourceLocation(3, 5)
loc2 = SourceLocation(7, 12)
loc3 = SourceLocation(9, 8)

test_cases = [
    ("x + 5",       lambda: eval_binop("+", env.lookup("x"), 5, loc1)),
    ("x / 0",       lambda: eval_binop("/", env.lookup("x"), 0, loc2)),
    ("x + name",    lambda: eval_binop("+", env.lookup("x"), env.lookup("name"), loc3)),
    ("undefined_var", lambda: env.lookup("undefined_var", SourceLocation(11, 3))),
]

for label, fn in test_cases:
    try:
        result = fn()
        print(f"  {label} => {result}")
    except InterpreterError as e:
        print(f"  {label} => {e}")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

> **Critical Thinking Questions 13–15**

**CTQ 13.** The `SourceLocation` dataclass carries line and column numbers. Where in your interpreter pipeline would you attach source locations to AST nodes? (Hint: the lexer knows the position of each token.)

[[___ your answer here ___]]

**CTQ 14.** The evaluator raises `InterpreterError` subclasses. This is a form of exception-based error propagation. What would the `Result`-based alternative look like? What are the tradeoffs between the two approaches for an interpreter?

[[___ your answer here ___]]

**CTQ 15.** When an error occurs during the evaluation of a deeply nested expression (e.g., inside a function call inside a `let` body inside another function), what information would you want in the error message? How does a **stack trace** differ from a single source location?

[[___ your answer here ___]]

---

## Model 6: Comparative Survey

```python
# Demonstrate three idioms for "find element or fail" in Python
from typing import Optional

data = [10, 20, 30, 40, 50]

# Strategy 1: Return None (sentinel value)
def find_sentinel(lst, target) -> Optional[int]:
    for i, v in enumerate(lst):
        if v == target:
            return i
    return None   # caller must check

# Strategy 2: Raise exception
def find_exception(lst, target) -> int:
    for i, v in enumerate(lst):
        if v == target:
            return i
    raise ValueError(f"{target} not found in list")

# Strategy 3: Return (value, ok) tuple (Go style)
def find_tuple(lst, target):
    for i, v in enumerate(lst):
        if v == target:
            return i, True
    return -1, False

# Strategy 4: Return Result type
from dataclasses import dataclass

@dataclass
class NotFoundError:
    target: object

def find_result(lst, target):
    for i, v in enumerate(lst):
        if v == target:
            return ("ok", i)
    return ("err", NotFoundError(target))

print("=== Comparing four error strategies ===")
for target in [30, 99]:
    print(f"\nSearching for {target}:")
    
    r = find_sentinel(data, target)
    print(f"  sentinel:  {r!r}  (caller must check for None)")
    
    try:
        r = find_exception(data, target)
        print(f"  exception: found at index {r}")
    except ValueError as e:
        print(f"  exception: raised {e!r}")
    
    idx, ok = find_tuple(data, target)
    print(f"  tuple:     ({idx}, {ok})  (caller must check ok)")
    
    tag, val = find_result(data, target)
    if tag == "ok":
        print(f"  result:    Ok({val})")
    else:
        print(f"  result:    Err({val})")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

> **Critical Thinking Questions 16–18**

**CTQ 16.** Fill in this comparison table for your group:

| Strategy | Can be ignored? | Carries error info? | Composable? | Statically checked? |
|----------|----------------|--------------------|-----------|--------------------|
| Return None/sentinel | | | | |
| Exception | | | | |
| (value, ok) tuple | | | | |
| Result/Either type | | | | |

Which row has the best profile? Why might languages still use the others?

[[___ your answer here ___]]

**CTQ 17.** Go's (value, error) tuple idiom has been criticized for being verbose — every call site requires `if err != nil { return nil, err }`. The `Result` type with `?` in Rust addresses this. What is the fundamental insight that makes `?` (or monadic bind `>>=`) cleaner than manual propagation?

[[___ your answer here ___]]

**CTQ 18.** **Algebraic effects** (a research direction in PL) generalize both exceptions and coroutines: you define an "effect" (like `raise IOException`), and the effect handler is separate from both the raiser and the call chain. How does this differ from exception handling? What new flexibility does it provide?

[[___ your answer here ___]]

---

## Multiple Choice Review

**Question 1.** In Python, `except Exception` catches:

- [( )] All exceptions including `SystemExit` and `KeyboardInterrupt`
- [(X)] Most exceptions, but not `BaseException` subclasses like `SystemExit`
- [( )] Only subclasses of `RuntimeError`
- [( )] Only exceptions explicitly raised with `raise`

**Question 2.** Rust's `Option<T>` type prevents:

- [( )] All runtime panics
- [( )] Division by zero
- [(X)] Using a potentially-absent value without first checking whether it is present
- [( )] Stack overflow from deep recursion

**Question 3.** Java's checked exceptions require the caller to:

- [(X)] Either catch the exception or declare it in the method signature
- [( )] Catch the exception in the same function that throws it
- [( )] Use a `Result` type instead of throwing
- [( )] Handle all exceptions with a single `catch (Exception e)`

**Question 4.** The `finally` block in Python runs:

- [( )] Only when no exception was raised
- [( )] Only when an exception was raised and caught
- [( )] Only when an exception was raised and not caught
- [(X)] Always, whether or not an exception was raised or caught

---

## Exercises

**Exercise 1.** Implement a `safe_chain` decorator that converts any function returning a value (or raising an exception) into a function returning `Result`. Then use it to build a pipeline without explicit try/except at every step:

```python
from dataclasses import dataclass
from typing import Any, Callable

@dataclass(frozen=True)
class Ok:
    value: Any
    def and_then(self, f): return f(self.value)
    def map(self, f): return Ok(f(self.value))
    def __repr__(self): return f"Ok({self.value!r})"

@dataclass(frozen=True)
class Err:
    error: Any
    def and_then(self, f): return self
    def map(self, f): return self
    def __repr__(self): return f"Err({self.error!r})"

def safe(fn: Callable) -> Callable:
    def wrapper(*args, **kwargs):
        try:
            return Ok(fn(*args, **kwargs))
        except Exception as e:
            return Err(str(e))
    return wrapper

# Wrap risky operations
safe_int  = safe(int)
safe_sqrt = safe(__import__('math').sqrt)
safe_div  = safe(lambda a, b: a / b)

# Build a pipeline using and_then
for s in ["16", "-4", "abc"]:
    result = safe_int(s).map(float).and_then(safe_sqrt)
    print(f"sqrt(int({s!r})) = {result}")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

**Exercise 2.** Implement a "stack trace" for your interpreter. Maintain a call stack (list of strings) that records function names as they are entered/exited. When an error occurs, attach the current stack trace to the error:

```python
from dataclasses import dataclass, field
from typing import List, Any, Optional

call_stack: List[str] = []

@dataclass
class InterpreterError(Exception):
    message: str
    stack_trace: List[str] = field(default_factory=list)
    def __str__(self):
        trace = "\n  ".join(reversed(self.stack_trace))
        return f"Error: {self.message}\nCall stack:\n  {trace}"

def enter_function(name: str):
    call_stack.append(name)

def exit_function():
    call_stack.pop()

def raise_error(message: str):
    raise InterpreterError(message, list(call_stack))

# Simulate a call chain: main → foo → bar → baz → error
def baz():
    enter_function("baz")
    try:
        raise_error("undefined variable 'x'")
    finally:
        exit_function()

def bar():
    enter_function("bar")
    try:
        baz()
    finally:
        exit_function()

def foo():
    enter_function("foo")
    try:
        bar()
    finally:
        exit_function()

def main():
    enter_function("main")
    try:
        foo()
    finally:
        exit_function()

try:
    main()
except InterpreterError as e:
    print(e)
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

**Exercise 3.** Compare Python's `Optional[T]` type hint (from `typing`) with the `Option` dataclass from Model 3. Write a function that accepts `Optional[int]` and one that accepts your `Option` type. Show what happens at runtime when a caller passes `None` vs. `Nothing()` to each:

```python
from typing import Optional
from dataclasses import dataclass

@dataclass(frozen=True)
class Some:
    value: object
    def map(self, f): return Some(f(self.value))
    def unwrap_or(self, d): return self.value

@dataclass(frozen=True)
class Nothing:
    def map(self, f): return self
    def unwrap_or(self, d): return d

Option = Some | Nothing

def double_optional(x: Optional[int]) -> Optional[int]:
    if x is None:
        return None
    return x * 2

def double_option(x: Option) -> Option:
    return x.map(lambda v: v * 2)

print("Optional[int]:")
print(f"  double_optional(5)    = {double_optional(5)}")
print(f"  double_optional(None) = {double_optional(None)}")
# What happens if caller ignores the hint and passes a string?
print(f"  double_optional('hi') = {double_optional('hi')}")  # runtime error or wrong answer?

print()
print("Option type:")
print(f"  double_option(Some(5))   = {double_option(Some(5))}")
print(f"  double_option(Nothing()) = {double_option(Nothing())}")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

**Exercise 4.** Add structured error reporting to a mini expression evaluator. Extend the evaluator to collect ALL errors in an expression (not just the first one) before reporting them:

```python
from dataclasses import dataclass, field
from typing import List, Any

@dataclass
class EvalError:
    expr: str
    message: str
    def __str__(self): return f"  [{self.expr}]: {self.message}"

def eval_expr(expr: str, env: dict) -> tuple:
    """Returns (value_or_None, list_of_errors)."""
    errors: List[EvalError] = []
    
    # Very simplified: handle 'a + b', 'a / b', integer literals, variable names
    expr = expr.strip()
    
    for op in ["+", "-", "*", "/"]:
        if op in expr:
            parts = expr.split(op, 1)
            left_s, right_s = parts[0].strip(), parts[1].strip()
            left_v, left_errs = eval_expr(left_s, env)
            right_v, right_errs = eval_expr(right_s, env)
            errors.extend(left_errs)
            errors.extend(right_errs)
            if left_v is None or right_v is None:
                return None, errors
            if op == "/" and right_v == 0:
                errors.append(EvalError(expr, "division by zero"))
                return None, errors
            ops = {"+": lambda a,b: a+b, "-": lambda a,b: a-b,
                   "*": lambda a,b: a*b, "/": lambda a,b: a/b}
            return ops[op](left_v, right_v), errors
    
    try:
        return int(expr), errors
    except ValueError:
        pass
    
    if expr in env:
        return env[expr], errors
    
    errors.append(EvalError(expr, f"undefined variable '{expr}'"))
    return None, errors

env = {"x": 10, "y": 5}
tests = ["x + y", "x / 0", "x + z", "10 + 3"]

for t in tests:
    value, errors = eval_expr(t, env)
    if errors:
        print(f"eval({t!r}): ERRORS:")
        for e in errors:
            print(e)
    else:
        print(f"eval({t!r}) = {value}")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

**Exercise 5.** Design an error hierarchy for a complete interpreter. Create a class hierarchy of `InterpreterError` subclasses covering: lexer errors (invalid character, unterminated string), parser errors (unexpected token, missing closing paren), and runtime errors (undefined variable, type mismatch, division by zero, stack overflow). Write a function that pretty-prints any error with its category, location, and a helpful suggestion:

```python
from dataclasses import dataclass
from typing import Optional

@dataclass
class SourceLocation:
    line: int
    col: int
    source_line: str = ""
    def __str__(self):
        pointer = " " * self.col + "^"
        return f"  {self.source_line}\n  {pointer}"

@dataclass
class InterpreterError(Exception):
    message: str
    location: Optional[SourceLocation] = None
    suggestion: str = ""
    
    @property
    def category(self): return "Error"
    
    def pretty(self) -> str:
        parts = [f"{self.category}: {self.message}"]
        if self.location:
            parts.append(str(self.location))
        if self.suggestion:
            parts.append(f"  Hint: {self.suggestion}")
        return "\n".join(parts)

@dataclass
class LexError(InterpreterError):
    @property
    def category(self): return "LexError"

@dataclass
class ParseError(InterpreterError):
    @property
    def category(self): return "ParseError"

@dataclass
class UndefinedVar(InterpreterError):
    name: str = ""
    @property
    def category(self): return "RuntimeError"

@dataclass
class TypeError_(InterpreterError):
    expected: str = ""
    got: str = ""
    @property
    def category(self): return "TypeError"

# Demo
errors = [
    LexError("unexpected character '@'",
             SourceLocation(3, 7, "  let x = @value"),
             "Valid identifiers start with a letter or underscore"),
    ParseError("expected ')' but found 'end of input'",
               SourceLocation(5, 20, "  (let x (+ x 1)"),
               "Check for unmatched parentheses"),
    UndefinedVar("variable 'y' is not defined",
                 SourceLocation(8, 12, "  let z = x + y"),
                 "Did you mean 'x'? Or define 'y' before using it",
                 name="y"),
    TypeError_("operator '+' requires numeric operands",
               SourceLocation(11, 10, "  print(1 + \"hello\")"),
               "Use str() to convert numbers to strings, or int() for the reverse",
               expected="number", got="str"),
]

for err in errors:
    print(err.pretty())
    print()
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

---

## Reflection

1. Your interpreter currently raises Python exceptions for runtime errors. A user of your language sees a Python traceback rather than a clean error message. Describe the two changes needed to give users clean, localized error messages.

2. A language designer is choosing between checked exceptions (Java-style) and `Result` types (Rust-style) for a new systems language. The language emphasizes correctness and will be used for network services. Which would you recommend, and what tradeoff are you accepting?

3. Go's philosophy is "errors are values" — errors are returned, not thrown. Haskell's philosophy is "errors are types" — absence and failure are encoded in the type system. Python's philosophy is "errors are exceptions" — errors interrupt control flow. Each philosophy has a consistent design vision. Which appeals most to you, and why?

---

## Further Reading

- **Python docs:** `exceptions` — the full exception hierarchy
- **Rust book:** Chapter 9, "Error Handling" — `panic!`, `Result`, and the `?` operator
- **Haskell wiki:** `Maybe` and `Either` monads
- **Paper:** *Exceptional Syntax* — Benton & Kennedy (2001), on typed exceptions
- **Talk:** *Inventing on Principle* — Bret Victor (mentions error feedback loops)
- **Research:** Algebraic effects and handlers — Plotkin & Pretnar (2009); the Koka language
- **Book:** *Crafting Interpreters* — Robert Nystrom, Chapter 14 (runtime errors with source locations)

---

*End of Activity — Error Handling: Return Codes, Exceptions, Option/Maybe, Result/Either, Interpreter Error Design*
