<!--
author:   CS374 Course Staff
email:    
version:  0.0.1
language: en
narrator: US English Female
comment:  Macros and metaprogramming — code that writes code, and why hygiene matters.
import:   https://raw.githubusercontent.com/liaScript/mermaid_template/master/README.md
link:     https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.3.0/css/all.min.css
-->

# Macros and Metaprogramming: Code that Writes Code

> Picture a pastry chef who, before turning on the oven, sits down with the recipe and rewrites every "1 cup sugar" as "200 grams sugar," every "1 stick butter" as "113 grams butter," and so on. The *transformation* happens before baking begins — the chef does not weigh things mid-recipe, they transform the recipe first. Macros work the same way: before the program runs, the macro system rewrites certain pieces of your code into different, fully expanded code. By the time execution starts, every macro call has already been replaced by ordinary code.

## Learning Goals

By the end of this activity, you will be able to:

- Define macros and explain how they differ from functions by operating on unevaluated syntax rather than values
- Identify hygiene problems in naive macros and explain how hygienic macro systems prevent variable capture
- Implement a simple macro expander that transforms AST nodes before evaluation in a mini interpreter
- Compare macro systems across languages (Lisp, Rust, Julia, Elixir) and evaluate the expressiveness-versus-safety tradeoffs each makes
- Apply metaprogramming techniques to define new control-flow constructs that cannot be expressed as ordinary functions

> **"Macros are the most powerful feature in Lisp — and the most dangerous."**
>
> Languages like Lisp, Rust, Julia, and Elixir give programmers the ability to extend the language itself at compile time. Today you'll discover *why* macros are powerful, *what* hygienic macros solve, and *how* to implement a macro system in Mini.

## Directions and Roles

Work in groups of 3–4. Rotate roles every 20 minutes.

- **Facilitator**: Keeps discussion on track; ensures everyone contributes.
- **Recorder**: Writes down answers and code that the group agrees on.
- **Reporter**: Presents findings to the class; explains the group's reasoning.
- **Reflector**: Monitors group process; writes the reflection at the end.

---

## Model 1 — What is a Macro?

A **function** receives *values* as arguments and returns a value. A **macro** receives *syntax* (unevaluated AST nodes) as arguments and returns *syntax* that replaces the macro call at compile time.

```
            Function:   arguments evaluated BEFORE the call
            Macro:      arguments NOT evaluated; macro produces new syntax
```

Example — Python's `assert` is macro-like: `assert cond, msg` evaluates differently than a function call would, because if `cond` is False, it raises with the *expression text* of `cond`.

In languages without macros, you cannot define `assert` yourself — it requires compiler support. With macros, you can define `assert`, `while`, `or`, `and`, and even new loop constructs as library code.

```python  liascript
# The problem: Python's "and" short-circuits, but a function "my_and" does not
def my_and(a, b):
    return a and b   # evaluates b even if a is False!

def side_effect():
    print("Side effect!")
    return True

# With 'and': side effect only runs if first arg is True
print("Testing short-circuit:")
result1 = False and side_effect()  # side_effect NOT called
print(f"False and side_effect() = {result1}")

# With function: side effect ALWAYS runs
result2 = my_and(False, side_effect())  # side_effect IS called!
print(f"my_and(False, side_effect()) = {result2}")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

**Critical Thinking Questions (CTQs)**

> **CTQ 1.1** Python's `and`/`or` short-circuit but `my_and(a, b)` does not. Why? What would need to change about Python's evaluation strategy to allow `my_and` to short-circuit?

> **CTQ 1.2** `assert cond, msg` works by accessing the *source text* of `cond`. Could you implement this as a regular Python function? Why or why not?

> **CTQ 1.3** Name three features in Python that are "macro-like" (i.e., they have special evaluation rules that can't be replicated with a function). Examples: `with`, `yield`, `@decorator`.

---

## Model 2 — Textual Macros: The C Preprocessor

The simplest macros are **textual substitution** (C's `#define`):

```c
#define SQUARE(x)   ((x) * (x))
#define MAX(a, b)   ((a) > (b) ? (a) : (b))
#define DEBUG_PRINT(x) printf("%s = %d\n", #x, (x))
```

Textual macros are powerful but dangerous because they operate on *text*, not *syntax*:

```python  liascript
# Simulate C-style textual macro expansion in Python
import re

def expand_macros(code: str, macros: dict) -> str:
    """Simple textual macro expander (like C preprocessor)."""
    for name, (params, body) in macros.items():
        pattern = rf'{re.escape(name)}\(([^)]+)\)'
        def replacer(m):
            args = [a.strip() for a in m.group(1).split(',')]
            result = body
            for param, arg in zip(params, args):
                result = result.replace(param, arg)
            return result
        code = re.sub(pattern, replacer, code)
    return code

macros = {
    'SQUARE': (['x'], '((x) * (x))'),
    'MAX':    (['a', 'b'], '((a) > (b) ? (a) : (b))'),
}

# Safe usage
print(expand_macros('int s = SQUARE(5);', macros))

# DANGEROUS: SQUARE(1+2) → ((1+2) * (1+2)) — fine with parens
print(expand_macros('int s = SQUARE(1+2);', macros))

# MAX with side effects — double evaluation!
# MAX(f(), g()) → ((f()) > (g()) ? (f()) : (g()))
# f() is called TWICE!
print(expand_macros('int m = MAX(f(), g());', macros))
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

**CTQs**

> **CTQ 2.1** What is the double-evaluation problem with `MAX(f(), g())`? Why is this a problem in C code?

> **CTQ 2.2** Without the extra parentheses in `((x) * (x))`, what goes wrong with `SQUARE(1+2)`? Try it by removing the parens.

> **CTQ 2.3** The C preprocessor is called "textual" because it operates on source text, not AST nodes. What bug can occur with `MAX(a, b)` if `a` contains a newline? (Hint: think about multi-line expressions.)

---

## Model 3 — AST Macros: Quoting and Quasiquoting

Proper macro systems operate on **AST nodes**, not text. This requires two operations:

- **Quote** (`'`): freeze an expression as data — don't evaluate it
- **Quasiquote** (`` ` ``): like quote, but with **unquote** (`,`) holes that ARE evaluated

In Scheme/Lisp notation:
```scheme
'(1 2 3)          ; quoted list — the data [1, 2, 3]
`(1 ,(+ 1 1) 3)   ; quasiquoted — evaluates the unquoted part → [1, 2, 3]
`(let ,x ,val)    ; builds a let-node with x and val substituted in
```

```python  liascript
# Implementing quasiquote for our tuple-based AST
def quote(expr):
    """Return expr as data (don't evaluate)."""
    return expr

def quasiquote(template, bindings):
    """
    Fill in 'holes' (strings starting with '$') in a nested tuple template.
    $name → look up name in bindings dict.
    """
    match template:
        case str() if template.startswith('$'):
            return bindings[template[1:]]
        case tuple():
            return tuple(quasiquote(item, bindings) for item in template)
        case list():
            return [quasiquote(item, bindings) for item in template]
        case _:
            return template

# Example: build an AST for "while cond do body" using quasiquote
# Our tuple AST: ('while', condition, body_block)

def make_while_macro(cond_ast, body_ast):
    """Macro: while(cond, body) → ('while', cond, body)"""
    return quasiquote(('while', '$cond', '$body'), 
                      {'cond': cond_ast, 'body': body_ast})

# Build: while (x > 0) do { x = x - 1 }
while_node = make_while_macro(
    ('gt', ('var', 'x'), ('num', 0)),
    ('assign', 'x', ('sub', ('var', 'x'), ('num', 1)))
)
print("while macro expansion:")
print(while_node)

# Build a swap macro: swap(a, b) → let tmp=a in (a:=b; b:=tmp)
def make_swap_macro(a_name, b_name):
    tmp = f'_tmp_{a_name}_{b_name}'  # avoid name clashes (manual hygiene)
    return quasiquote(
        ('seq',
            ('assign', '$tmp', ('var', '$a')),
            ('seq',
                ('assign', '$a', ('var', '$b')),
                ('assign', '$b', ('var', '$tmp')))),
        {'tmp': tmp, 'a': a_name, 'b': b_name}
    )

swap_ab = make_swap_macro('x', 'y')
print("\nswap macro expansion for (x, y):")
print(swap_ab)
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

**CTQs**

> **CTQ 3.1** The `make_swap_macro` generates a fresh name `_tmp_x_y` to avoid name clashes. What would go wrong if we just used `tmp` as the name? Write a code example where this would cause a bug.

> **CTQ 3.2** Compare `quasiquote` here with Python's f-strings. What's similar? What's different? (Hint: f-strings work on text, quasiquote works on AST.)

> **CTQ 3.3** In Scheme, `define-syntax` / `syntax-rules` is the standard macro system. It's "pattern-based" — you write the input pattern and the output template. What are the benefits over our `quasiquote` approach?

---

## Model 4 — The Hygiene Problem and Hygienic Macros

**Unhygienic macros** can accidentally *capture* variables from the context they're expanded in:

```python  liascript
# The classic hygiene problem
# Suppose we define a macro "or2(a, b)" that avoids double-evaluation:
# It expands to: let _tmp = a in (if _tmp then _tmp else b)

def expand_or2(a_ast, b_ast):
    """Unhygienic 'or' macro — uses a temporary variable."""
    return ('let', '_tmp', a_ast,
            ('if', ('var', '_tmp'), ('var', '_tmp'), b_ast))

# Safe usage:
print("or2(x > 0, y > 0) expands to:")
print(expand_or2(('gt', ('var', 'x'), ('num', 0)),
                 ('gt', ('var', 'y'), ('num', 0))))

# HYGIENE BUG: What if the user's code HAS a variable called _tmp?
# or2(_tmp, x > 0) — but _tmp is the user's variable!
# expands to: let _tmp = _tmp in (if _tmp then _tmp else (x > 0))
# The user's _tmp is shadowed by our macro's _tmp!
broken = expand_or2(('var', '_tmp'), ('gt', ('var', 'x'), ('num', 0)))
print("\nor2(_tmp, x>0) — BROKEN expansion:")
print(broken)
# The 'let _tmp = _tmp' binds a NEW _tmp to itself — looks up user's _tmp,
# but then inside the body, ('var', '_tmp') refers to the MACRO's _tmp.
# For simple literals this is OK, but in general the user's _tmp is captured.

# Hygienic solution: use a fresh, globally unique name
_gensym_counter = 0
def gensym(prefix='_g'):
    global _gensym_counter
    _gensym_counter += 1
    return f'{prefix}{_gensym_counter}'

def expand_or2_hygienic(a_ast, b_ast):
    """Hygienic 'or' macro — uses a fresh unique name."""
    tmp = gensym('_or_tmp')   # guaranteed fresh
    return ('let', tmp, a_ast,
            ('if', ('var', tmp), ('var', tmp), b_ast))

print("\nHygienic or2(_tmp, x>0):")
print(expand_or2_hygienic(('var', '_tmp'), ('gt', ('var', 'x'), ('num', 0))))
# Now the fresh name won't clash with _tmp
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

**CTQs**

> **CTQ 4.1** In `expand_or2(('var', '_tmp'), ...)`, what is the expansion? Trace through it carefully: what does `('let', '_tmp', ('var', '_tmp'), ...)` mean — which `_tmp` is the binding, and which is the reference?

> **CTQ 4.2** The `gensym` function generates names like `_or_tmp1`. Why is this guaranteed to be hygienic? What assumption does it rely on?

> **CTQ 4.3** Scheme's `syntax-rules` macros are *automatically* hygienic — the macro system tracks which names were introduced by the macro vs. which came from the call site. What information would our simple system need to track to do this automatically?

---

## Model 5 — Implementing a Macro Expander for Mini

A complete macro system for Mini needs:
1. A way to *define* macros (as functions from AST → AST)
2. An *expander* that walks the AST and expands macro calls before evaluation
3. A `gensym` for hygiene

```python  liascript
from dataclasses import dataclass, field
from typing import Any, Callable

# Macro registry
_macros: dict[str, Callable] = {}
_gensym_counter = 0

def gensym(prefix='g'):
    global _gensym_counter
    _gensym_counter += 1
    return f'__{prefix}{_gensym_counter}__'

def defmacro(name: str):
    """Decorator to register a macro."""
    def decorator(fn):
        _macros[name] = fn
        return fn
    return decorator

def macroexpand(ast):
    """Expand all macros in ast (post-order: expand leaves first)."""
    match ast:
        case ('call', ('var', name), args) if name in _macros:
            # Expand macro: pass raw AST args, get new AST back
            expanded = _macros[name](*args)
            return macroexpand(expanded)   # expand the result too!
        case tuple():
            return tuple(macroexpand(child) for child in ast)
        case list():
            return [macroexpand(child) for child in ast]
        case _:
            return ast

# Define a 'when' macro: when(cond, body) → if cond then body else nil
@defmacro('when')
def when_macro(cond_ast, body_ast):
    return ('if', cond_ast, body_ast, ('nil',))

# Define 'swap!' macro: swap!(a, b) → hygienic temp-var swap
@defmacro('swap!')
def swap_macro(a_ast, b_ast):
    # Only works for variable names
    assert a_ast[0] == 'var' and b_ast[0] == 'var', "swap! requires variable names"
    a_name = a_ast[1]
    b_name = b_ast[1]
    tmp = gensym('swap')
    return ('seq',
        ('let', tmp, ('var', a_name)),
        ('seq',
            ('assign', a_name, ('var', b_name)),
            ('assign', b_name, ('var', tmp))))

# Define 'unless' macro: unless(cond, body) → if not cond then body else nil
@defmacro('unless')
def unless_macro(cond_ast, body_ast):
    return ('if', ('not', cond_ast), body_ast, ('nil',))

# Test macroexpansion
print("when(x > 0, print(x)) expands to:")
ast1 = ('call', ('var', 'when'), [('gt', ('var', 'x'), ('num', 0)), ('print', ('var', 'x'))])
print(macroexpand(ast1))

print("\nswap!(x, y) expands to:")
ast2 = ('call', ('var', 'swap!'), [('var', 'x'), ('var', 'y')])
print(macroexpand(ast2))
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

**CTQs**

> **CTQ 5.1** `macroexpand` is called *recursively* on the result of a macro expansion (`return macroexpand(expanded)`). Why? What kind of macros require this?

> **CTQ 5.2** The expander here uses a **call-site pattern**: `('call', ('var', name), args)`. What are the limitations of this approach? Could a macro `(if ...)` be handled the same way?

> **CTQ 5.3** Macros are expanded *before* evaluation. What does this mean for error messages? If a macro produces malformed AST, when does the error occur? How does this make debugging harder?

---

## Multiple Choice

What is the key difference between a macro and a function?

    [( )] Macros are faster than functions at runtime
    [(x)] Macros receive unevaluated syntax and return new syntax; functions receive evaluated values
    [( )] Macros are only available in Lisp-family languages
    [( )] Macros cannot take arguments

---

What is the "hygiene problem" in macro systems?

    [( )] Macros that contain too many nested levels
    [(x)] A macro-introduced variable accidentally captures or is captured by a user variable of the same name
    [( )] Macros that are too slow to expand
    [( )] Using macros to define recursive functions

---

`gensym` generates unique names to achieve hygiene. Which of the following is also needed for full hygiene?

    [( )] A faster garbage collector
    [(x)] Tracking which names were introduced by the macro vs. by the call-site context, to prevent *both* directions of capture
    [( )] Converting all macros to functions
    [( )] Using static scoping instead of dynamic scoping

---

When does macro expansion happen in a typical language implementation?

    [( )] At runtime, when the macro call is first encountered
    [(x)] At compile time / before evaluation, during a pass over the AST
    [( )] During lexing, by transforming token streams
    [( )] Only in interpreted languages, not compiled ones

---

## Exercises

### Exercise 1 — `and2` and `or2` Macros (15 min)

Implement *hygienic* `and2(a, b)` and `or2(a, b)` macros that short-circuit:
- `and2(a, b)` → evaluate `a`; if falsy, return it; otherwise return `b`
- `or2(a, b)` → evaluate `a`; if truthy, return it; otherwise return `b`

Test that `and2(false, side_effect())` does NOT evaluate `side_effect()` (demonstrate with a print in the side effect).

### Exercise 2 — `let*` Macro (20 min)

In Scheme, `let*` allows sequential bindings where later bindings can use earlier ones:

```scheme
(let* ((x 1) (y (+ x 1)) (z (* y 2))) z)   ; → 4
```

Implement `let_star([('x', e1), ('y', e2), ...], body_ast)` as a macro that expands to nested `let`:

```
let x = e1 in (let y = e2 in (... body))
```

### Exercise 3 — `define-syntax` Style Pattern Matching (25 min)

Implement a `syntax_rules` function that lets you define macros via patterns:

```python
cond_macro = syntax_rules('cond', [
    ('(cond)', lambda: ('nil',)),
    ('(cond (else e))', lambda e: e),
    ('(cond (test expr) . rest)', 
     lambda test, expr, rest: ('if', test, expr, ('call', ('var', 'cond'), rest)))
])
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

Test it on: `(cond ((x > 0) (print "pos")) (else (print "non-pos")))`.

### Exercise 4 — Macro Expansion in Mini (30 min, harder)

Integrate the macro expander into your Mini interpreter pipeline:

1. Add a `MacroDef` AST node: `MacroDef(name: str, params: list[str], body: Expr)`
2. In the macro expander, handle `MacroDef` by registering the macro (evaluate the body as AST → AST function)
3. Write a Mini program that defines `unless` and `swap!` using the macro system
4. Demonstrate that the expanded code evaluates correctly

---

## Reflection

*(Write your answers individually, then discuss with your group.)*

1. Languages like C, C++, and Rust have macro systems. Haskell and OCaml do NOT have true macros (they have Template Haskell / PPX, which are cumbersome). Is this a good tradeoff? What do you lose by not having macros?

2. Lisp programmers often say "Lisp macros let you extend the language." Give a concrete example of a language feature that would be impossible to add as a library function, but easy to add as a macro.

3. The final project has a "macros and hygienic quoting" extension option. How would you design the syntax for macro definitions in Mini? Write a sample Mini program that uses a macro.

---

## Further Reading

- **"On Lisp"** — Paul Graham (free at https://paulgraham.com/onlisp.html): the classic book on Lisp macros
- **Scheme `syntax-rules`** — R7RS Section 4.3: https://r7rs.org/
- **Rust procedural macros** — The Rust Reference: https://doc.rust-lang.org/reference/procedural-macros.html
- **"Macros that Work Together"** — Flatt et al. (2012): how Racket achieves full hygienic macros
- **"Hygienic Macro Expansion"** — Kohlbecker et al. (1986): original hygiene paper
- **Julia macros** — https://docs.julialang.org/en/v1/manual/metaprogramming/: modern example of AST macros in a scientific language
