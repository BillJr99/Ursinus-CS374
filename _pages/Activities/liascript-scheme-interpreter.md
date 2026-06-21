# The Metacircular Evaluator: Scheme in Python

<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://github.com/BillJr99/Ursinus-CS374-Fall2026/blob/main/_pages/Activities/liascript-scheme-interpreter.md

import: https://raw.githubusercontent.com/liascript/CodeRunner/master/README.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

# The Metacircular Evaluator: Scheme in Python

A **metacircular evaluator** is an interpreter for a language written in that language itself, or (as here) written in a language so structurally similar that the evaluation rules read like a direct transcription of the language's own semantics. This two-day module builds a complete Scheme interpreter in Python. The interpreter is small enough to fit in one screen and powerful enough to run recursive programs. The arc: **why Scheme first $\rightarrow$ s-expression parsing $\rightarrow$ the evaluator as a dispatch table $\rightarrow$ environments as closures $\rightarrow$ tail-call optimization**.

Abelson and Sussman open SICP Chapter 4 with the evaluator-as-program idea: once you can write the evaluator, you understand the language completely. You have already built a Mini language interpreter. Here you build one for a language that was designed to be easy to interpret, and compare the effort.

---

## Directions and Group Roles

Work in your POGIL team with rotated roles (**Manager**, **Recorder**, **Presenter**, **Reflector**). Today is hands-on: the Manager drives all code cells, every teammate predicts output before running. The Recorder posts answers to the Class Activity Questions discussion board; the Presenter reports out areas of disagreement or alternative interpretations. After class, respond to the reflective prompt individually in your notebook.

---

# Part I: Why Scheme First? (Day 1)

## 1. Scheme as an Interpreter's Best Friend

Scheme is the ideal first interpreter to write, for four concrete reasons:

- **S-expression syntax means the AST is already in the source.** `(+ (* 2 3) 4)` is a parenthesized prefix list; its nesting is the parse tree. There is no operator precedence to recover, no associativity to resolve, no statement-expression distinction. The tokenizer and parser together are fewer than thirty lines.
- **Minimal special forms.** The entire language requires exactly six: `lambda`, `if`, `define`, `quote`, `let`, and `begin`. Every other construct (`cond`, `letrec`, `and`, `or`) is either a library function or sugar for these six.
- **Dynamic typing.** Values carry their types; the evaluator never consults a type environment. A number is a number; a list is a list; a procedure is a procedure. No inference, no annotations.
- **Used in SICP to explain computation itself.** Abelson and Sussman's metacircular evaluator is the central object of Chapter 4; building one puts you in direct conversation with that tradition.

Contrast this with your Mini language: it has infix arithmetic (requiring a precedence grammar), multiple statement forms, and a richer syntax that demanded a real recursive-descent parser. Scheme trades syntactic familiarity for structural transparency.

---

## Code Cell

```python
import re

def tokenize_scheme(source):
    token_pat = r'\"(?:[^\"\\]|\\.)*\"|\(|\)|[^\s()\";]+|;[^\n]*'
    tokens = re.findall(token_pat, source)
    return [t for t in tokens if not t.startswith(';')]

def parse_atom(token):
    try:
        return int(token)
    except ValueError:
        pass
    try:
        return float(token)
    except ValueError:
        pass
    if token.startswith('"'):
        return token[1:-1]
    if token == '#t':
        return True
    if token == '#f':
        return False
    return token

def parse_sexp(tokens, pos=0):
    if pos >= len(tokens):
        raise SyntaxError("unexpected end of input")
    token = tokens[pos]
    if token == '(':
        lst = []
        pos += 1
        while pos < len(tokens) and tokens[pos] != ')':
            item, pos = parse_sexp(tokens, pos)
            lst.append(item)
        if pos >= len(tokens):
            raise SyntaxError("missing closing parenthesis")
        return lst, pos + 1
    elif token == ')':
        raise SyntaxError("unexpected ')'")
    else:
        return parse_atom(token), pos + 1

def read(source):
    tokens = tokenize_scheme(source)
    expr, _ = parse_sexp(tokens)
    return expr

try:
    print(read("(+ 1 2)"))
    print(read("(if (> x 0) x (- 0 x))"))
    print(read("(lambda (x y) (+ x y))"))
    print(read("(define (fact n) (if (= n 0) 1 (* n (fact (- n 1)))))"))
except Exception as e:
    print(f"[parser] {e}")
    import traceback; traceback.print_exc()
```

---

## Model 1: The S-expression Structure

The output of `read` on `(+ 1 2)` is the Python list `['+', 1, 2]`. The head is the operator; the tail is the argument list. Nested expressions nest lists:

```
(+ (* 2 3) 4)      →  ['+', ['*', 2, 3], 4]
(if (> x 0) x 0)   →  ['if', ['>', 'x', 0], 'x', 0]
(lambda (x) x)     →  ['lambda', ['x'], 'x']
```

Atoms (numbers, booleans, strings) parse to their Python equivalents. Symbols parse to Python strings. A compound form `(f a b ...)` parses to a Python list whose first element names the head.

### Critical Thinking Questions

1. `(+ 1 2)` parses to `['+', 1, 2]`. What Python type is the atom `1`? What Python type is the symbol `'+'`? Why does the same Python type serve both roles, and how will the evaluator tell them apart?
2. What Python type represents a compound form `(f a b ...)`? How do you distinguish a parsed compound form from a parsed atom at runtime, without any class hierarchy?
3. Given a parsed form `x`, write the Python condition (no more than one line) that determines whether `x` is a special form named `'if'`. How does this compare to checking `isinstance(node, IfNode)` in your Mini interpreter?
4. In your Mini language, what was the most complex part of the parser? Why does that complexity not appear here?

---

# Part II: The Evaluator (Day 1 continued)

## 2. Environments

The environment chain is structurally identical to the one you built in the environments module. The only difference is the constructor signature, which accepts a list of parameter names and a list of argument values and zips them into the initial dictionary.

## Code Cell

```python
class Env:
    def __init__(self, params=(), args=(), outer=None):
        self.d = dict(zip(params, args))
        self.outer = outer

    def find(self, name):
        if name in self.d:
            return self.d
        if self.outer:
            return self.outer.find(name)
        raise NameError(f"unbound variable: {name!r}")

    def __setitem__(self, name, val):
        self.d[name] = val

    def __getitem__(self, name):
        return self.find(name)[name]

try:
    g = Env(params=['x', 'y'], args=[3, 4])
    inner = Env(params=['z'], args=[10], outer=g)
    print(inner['x'])
    print(inner['z'])
    g['w'] = 99
    print(inner['w'])
    inner['x']
except NameError as e:
    print(f"NameError: {e}")
except Exception as e:
    print(f"[env] {e}")
    import traceback; traceback.print_exc()
```

---

## 3. The Evaluator

`scheme_eval` is a single function that dispatches on the shape of the parsed expression. Self-evaluating forms return immediately. Symbols do an environment lookup. Compound forms dispatch on the head: special forms have named cases; everything else is a function call.

## Code Cell

```python
import operator
import math

class Procedure:
    def __init__(self, params, body, env):
        self.params = params
        self.body = body
        self.env = env

    def __call__(self, *args):
        return scheme_eval(self.body, Env(self.params, args, self.env))

    def __repr__(self):
        return f"#<procedure ({' '.join(self.params)})>"

def scheme_eval(x, env):
    if isinstance(x, bool) or not isinstance(x, (str, list)):
        return x
    if isinstance(x, str):
        return env[x]
    head = x[0]
    if head == 'quote':
        return x[1]
    if head == 'if':
        _, test, then, *rest = x
        branch = then if scheme_eval(test, env) else (rest[0] if rest else False)
        return scheme_eval(branch, env)
    if head == 'define':
        _, name, val = x
        env[name] = scheme_eval(val, env)
        return None
    if head == 'lambda':
        _, params, body = x
        return Procedure(params, body, env)
    if head == 'begin':
        result = None
        for expr in x[1:]:
            result = scheme_eval(expr, env)
        return result
    if head == 'let':
        _, bindings, body = x
        params = [b[0] for b in bindings]
        args = [scheme_eval(b[1], env) for b in bindings]
        return scheme_eval(body, Env(params, args, env))
    proc = scheme_eval(head, env)
    args = [scheme_eval(arg, env) for arg in x[1:]]
    return proc(*args)

def make_global_env():
    env = Env()
    env.d.update({
        '+': lambda *a: sum(a),
        '-': lambda a, b=None: -a if b is None else a - b,
        '*': lambda a, b: a * b,
        '/': lambda a, b: a / b,
        '=': operator.eq,
        '<': operator.lt,
        '>': operator.gt,
        '<=': operator.le,
        '>=': operator.ge,
        'not': operator.not_,
        'and': lambda a, b: a and b,
        'or': lambda a, b: a or b,
        'cons': lambda a, b: [a] + (b if isinstance(b, list) else [b]),
        'car': lambda x: x[0],
        'cdr': lambda x: x[1:],
        'null?': lambda x: x == [],
        'list': lambda *a: list(a),
        'display': print,
        'newline': lambda: print(),
        '#t': True,
        '#f': False,
    })
    return env

def run(source, env):
    return scheme_eval(read(source), env)

try:
    g = make_global_env()
    print(run("(+ 1 2)", g))
    print(run("(if #t 42 0)", g))
    run("(define x 10)", g)
    print(run("(* x x)", g))
    run("(define fact (lambda (n) (if (= n 0) 1 (* n (fact (- n 1))))))", g)
    print(run("(fact 10)", g))
    print(run("(let ((a 3) (b 4)) (+ a b))", g))
except Exception as e:
    print(f"[eval] {e}")
    import traceback; traceback.print_exc()
```

---

## Model 2: Running the Evaluator

The evaluator's dispatch is a direct translation of Scheme's evaluation rules. Each special form is a named case; function calls are the default. The `Procedure` class captures the parameter list, body, and the **defining environment** at lambda creation time.

### Critical Thinking Questions

1. Why is `(quote x)` needed? Write what happens if the evaluator encounters the symbol `x` without `quote` and `x` is not bound in the environment. Give a concrete example where `quote` is necessary.
2. The `Procedure` constructor stores `env`, the environment at the point the `lambda` is evaluated, not the environment at the point the function is *called*. What scoping rule does this implement? What would change if you used the call-site environment instead?
3. The evaluator handles `let` by desugaring it: `(let ((x 3) (y 4)) (+ x y))` is treated as if it were `((lambda (x y) (+ x y)) 3 4)`. Write out the desugared form explicitly, then trace `scheme_eval` on it for two levels to show that the result is 7.
4. Consider `(define fact (lambda (n) (if (= n 0) 1 (* n (fact (- n 1))))))`. When the `lambda` is evaluated, `fact` is not yet bound in the environment. Yet the recursive call `(fact (- n 1))` works. Trace exactly when and where `fact` is resolved: is it at lambda creation time, or at each call time? Why does the chain-of-environments design make this work?

---

[[MC]]
In the metacircular evaluator, evaluating `(lambda (x) (+ x 1))` in the global environment:
- (x) Returns a Procedure object that closes over the global environment
- ( ) Immediately calls the function with no argument
- ( ) Looks up `lambda` in the environment and signals an error if not found
- ( ) Returns the symbol `lambda`

---

# Part III: Tail Calls and Optimization (Day 2)

## 4. The Cost of Naive Recursion

Scheme programs that use recursion as iteration can require millions of recursive calls. In Python, function call depth is limited (typically 1000 frames by default). A straightforward recursive loop will crash:

## Code Cell

```python
try:
    g2 = make_global_env()
    run("(define loop (lambda (n) (if (= n 0) (quote done) (loop (- n 1)))))", g2)
    print(run("(loop 5)", g2))
    print(run("(loop 500)", g2))
    print(run("(loop 5000)", g2))
except RecursionError as e:
    print(f"RecursionError: {e}")
except Exception as e:
    print(f"[tco] {e}")
    import traceback; traceback.print_exc()
```

---

## 5. Proper Tail Calls

A **tail call** is a function call that is the last action of the calling function: the caller has nothing left to do after the call returns except return that same value. The Scheme standard requires that tail calls not consume stack space. This is called **proper tail recursion** or **tail call optimization (TCO)**.

The key insight: if the caller has nothing left to do, its stack frame is not needed after the call. We can reuse it (or, in Python where we cannot control frames directly, simulate the same effect with a loop).

A **trampoline** implements this. Instead of making the tail call directly, the evaluator returns a `Thunk` — a suspended call — to an outer loop that keeps driving execution until it gets a real value. The stack never grows past one frame deep.

## Code Cell

```python
class Thunk:
    def __init__(self, fn, *args):
        self.fn = fn
        self.args = args

def trampoline(val):
    while isinstance(val, Thunk):
        val = val.fn(*val.args)
    return val

def scheme_eval_tco(x, env):
    while True:
        if isinstance(x, bool) or not isinstance(x, (str, list)):
            return x
        if isinstance(x, str):
            return env[x]
        head = x[0]
        if head == 'quote':
            return x[1]
        if head == 'if':
            _, test, then, *rest = x
            x = then if scheme_eval_tco(test, env) else (rest[0] if rest else False)
            continue
        if head == 'define':
            _, name, val = x
            env[name] = scheme_eval_tco(val, env)
            return None
        if head == 'lambda':
            _, params, body = x
            return ProcedureTCO(params, body, env)
        if head == 'begin':
            for expr in x[1:-1]:
                scheme_eval_tco(expr, env)
            x = x[-1]
            continue
        if head == 'let':
            _, bindings, body = x
            params = [b[0] for b in bindings]
            args = [scheme_eval_tco(b[1], env) for b in bindings]
            env = Env(params, args, env)
            x = body
            continue
        proc = scheme_eval_tco(head, env)
        args = [scheme_eval_tco(arg, env) for arg in x[1:]]
        if isinstance(proc, ProcedureTCO):
            env = Env(proc.params, args, proc.env)
            x = proc.body
            continue
        return proc(*args)

class ProcedureTCO:
    def __init__(self, params, body, env):
        self.params = params
        self.body = body
        self.env = env

    def __call__(self, *args):
        return scheme_eval_tco(self.body, Env(self.params, args, self.env))

    def __repr__(self):
        return f"#<procedure ({' '.join(self.params)})>"

def make_global_env_tco():
    env = Env()
    env.d.update({
        '+': lambda *a: sum(a),
        '-': lambda a, b=None: -a if b is None else a - b,
        '*': lambda a, b: a * b,
        '/': lambda a, b: a / b,
        '=': operator.eq,
        '<': operator.lt,
        '>': operator.gt,
        '<=': operator.le,
        '>=': operator.ge,
        'not': operator.not_,
        'and': lambda a, b: a and b,
        'or': lambda a, b: a or b,
        'cons': lambda a, b: [a] + (b if isinstance(b, list) else [b]),
        'car': lambda x: x[0],
        'cdr': lambda x: x[1:],
        'null?': lambda x: x == [],
        'list': lambda *a: list(a),
        'display': print,
        'newline': lambda: print(),
        '#t': True,
        '#f': False,
    })
    return env

def run_tco(source, env):
    return scheme_eval_tco(read(source), env)

try:
    g3 = make_global_env_tco()
    run_tco("(define loop (lambda (n) (if (= n 0) (quote done) (loop (- n 1)))))", g3)
    print(run_tco("(loop 5)", g3))
    print(run_tco("(loop 100000)", g3))
    run_tco("(define fact-iter (lambda (n acc) (if (= n 0) acc (fact-iter (- n 1) (* n acc)))))", g3)
    run_tco("(define fact (lambda (n) (fact-iter n 1)))", g3)
    print(run_tco("(fact 10)", g3))
except RecursionError as e:
    print(f"RecursionError: {e}")
except Exception as e:
    print(f"[tco] {e}")
    import traceback; traceback.print_exc()
```

---

## Model 3: Tail Calls

The TCO evaluator replaces function call recursion with a `while True` loop. When a tail call is detected (the called procedure is a `ProcedureTCO` and the call is in tail position), the evaluator rebinds `x` and `env` and loops rather than recursing. The stack depth stays constant.

### Critical Thinking Questions

1. The expression `(+ n (loop (- n 1)))` contains a call to `loop`. Is this call in tail position? Explain: what does the evaluator still need to do with the result of `loop` after it returns, and why does that prevent tail-call optimization here?
2. In `(if cond (loop a) (loop b))`, both `(loop a)` and `(loop b)` are calls. Are both in tail position? In `scheme_eval_tco`, which case handles the `if` form, and how does it ensure the selected branch is handled without a recursive call to `scheme_eval_tco`?
3. The TCO evaluator converts tail recursion into a `while True` loop by reassigning `x` and `env`. Compare this to the `{term}*` repetition pattern in a recursive-descent parser, where a left-recursive rule is converted into a loop to avoid infinite recursion. In both cases, recursion in the specification becomes iteration in the implementation. State the structural analogy precisely: what is the "recursive call" in each case, and what is the "loop body"?

---

[[MC]]
The key property that makes tail-call optimization possible is:
- ( ) The function being called is pure (no side effects)
- (x) The result of the call IS the result of the caller, so the caller's stack frame is not needed after the call
- ( ) The function is defined at the top level
- ( ) The function takes exactly one argument

---

# Part IV: Exercises

## 6. Exercises

1. **Add `cond`.** Add `(cond (test1 result1) (test2 result2) ... (else default))` as a special form in `scheme_eval`. The `else` keyword is treated as a test that always passes. Demonstrate it classifying integers as negative, zero, or positive using `(cond ((< n 0) (quote negative)) ((= n 0) (quote zero)) (else (quote positive)))`.

2. **Add `letrec`.** `let` evaluates all binding expressions in the *outer* environment, so bindings cannot refer to each other. `letrec` allows mutually recursive bindings by first creating placeholder bindings in a new environment, then evaluating and installing the values in that same environment. Implement `letrec` as a special form and verify that `(letrec ((fact (lambda (n) (if (= n 0) 1 (* n (fact (- n 1))))))) (fact 5))` returns 120.

3. **Add `set!`.** Implement `(set! name val)` which finds the existing binding for `name` in the environment chain (using the `assign`-style walk, not defining a new binding) and updates it. Use it to implement a mutable counter: `(define count 0)` followed by `(set! count (+ count 1))` three times, then print `count`. Compare this to your Mini language's assignment statement.

4. **Port Mini programs.** Take three programs you wrote for your Mini language interpreter assignments and translate them to run in this Scheme evaluator. For each one, record: (a) whether the translation was straightforward, (b) one thing that was easier in Scheme, (c) one thing that was harder or impossible without extending the evaluator, and (d) the line count in Mini source versus Scheme source.

5. **Mutual recursion.** Using only `define` (no `letrec`), define `even?` and `odd?` in the global environment: `(define (even? n) (if (= n 0) #t (odd? (- n 1))))` and `(define (odd? n) (if (= n 0) #f (even? (- n 1))))`. (Use the `(define (f x) body)` shorthand by first parsing it manually, or add that shorthand as a third exercise extension.) Does mutual recursion work? Explain why the global-environment design makes forward references possible in a way that a single-pass compiler would not.

---

## Reflection Prompt

In your notebook: the metacircular evaluator is fewer than 50 lines of Python (excluding the built-in library), yet it runs all of core Scheme, including recursion, closures, and higher-order functions. Abelson and Sussman present this as evidence that computation itself is simple: complexity lives in the *libraries*, not the *language kernel*. Does that match what you experienced building your Mini interpreter? Identify two places where your Mini interpreter's complexity came from the language features themselves, and two places where it came from the implementation machinery (parsing, environment wiring, error handling). Is the 50-line figure honest, or does it hide work that your Mini interpreter made explicit?

---

## Further Reading

- Abelson and Sussman. *Structure and Interpretation of Computer Programs*, Chapter 4: the original metacircular evaluator, with a full treatment of the environment model and tail calls.
- Peter Norvig. "lispy.py" (online, norvig.com): a 90-line Scheme interpreter in Python, the canonical short reference implementation.
- Kent Dybvig. *The Scheme Programming Language*, 4th ed. (free online, scheme.com): the authoritative reference, with a clear exposition of proper tail recursion.
- Daniel P. Friedman and Matthias Felleisen. *The Little Schemer*: recursive descent through a tiny mind, structured as a dialogue, with the Y combinator as its final destination.
