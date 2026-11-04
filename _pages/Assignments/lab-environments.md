---
layout: textbook
permalink: /Assignments/EnvironmentsLab
title: "CS374: Principles of Programming Languages - Tutorial: Environments and Type Checking"

info:
  coursenum: CS374
  eyebrow: "Tutorial"
  numbering: false
  objectives:
    - "Trace how a name is found through a chain of nested scopes"
    - "Tell define from assign in real code"
    - "Reuse the same scope table to check types before a program runs"

tags:
  - scope
  - types
  - tutorial

---

This is a walkthrough, and there is nothing to submit.  It shows you the one data structure your interpreter needs for variables, and then uses that structure a second time to check types.  Type the code into a file named `scopes.py` as you go, and run it, because watching it work is the point.

## Part 1: The Scope Table

A block can use the names of the blocks around it, and it can also hide them with its own.  So each scope needs its own table of names and a link to the scope that encloses it.  Here is a program after entering one block:

```text
   inner                       outer
+-----------+   _parent    +---------------+   _parent
| x: 51     | -----------> | x: 2, y: 10   | -----------> None
+-----------+              +---------------+
```

Each box is one `Environment` object:

```python
class LangNameError(Exception):
    pass


class Environment:
    def __init__(self, parent=None):
        self._bindings = {}
        self._parent = parent

    def define(self, name, value):
        self._bindings[name] = value

    def lookup(self, name):
        if name in self._bindings:
            return self._bindings[name]
        if self._parent is not None:
            return self._parent.lookup(name)
        raise LangNameError(f"Undefined variable '{name}'")

    def assign(self, name, value):
        if name in self._bindings:
            self._bindings[name] = value
        elif self._parent is not None:
            self._parent.assign(name, value)
        else:
            raise LangNameError(f"Undefined variable '{name}'")
```

The difference between `define` and `assign` is the most important idea here, and it is the difference between `let x = 1;` and `x = 1;`.  `define` always writes into this scope, which is how an inner `x` hides an outer one.  `assign` walks outward and updates the nearest `x` that already exists, and it never creates one.  `lookup` walks outward the same way, and stops at the first scope that has the name.

Now run a small program.  Each `let` is a `define`, and entering a block makes a new `Environment` whose parent is the current one:

```python
outer = Environment()               # let x = 2;  let y = 10;
outer.define("x", 2)
outer.define("y", 10)

inner = Environment(parent=outer)   # {
inner.define("x", 51)               #     let x = 51;
inner.assign("y", inner.lookup("y") + 1)   # y = y + 1;
print(inner.lookup("x"))            #     print x;
                                    # }
print(outer.lookup("x"))            # print x;
print(outer.lookup("y"))            # print y;
```

> **Predict, then run.**  What do the three prints show?  You should see `51`, `2`, and `11`.  The inner `let x` made a new `x` and left the outer one alone, and `y = y + 1` had no `let`, so it changed the outer `y`.

Here is the `y` lookup inside the block, one scope at a time:

```text
inner.lookup("y")
    inner holds {x: 51}.  No y, so ask the parent.
    outer.lookup("y")
        outer holds {x: 2, y: 10}.  y is here, so return 10.
```

## Part 2: Type Checking with the Same Table

A **static type checker** decides whether each operation makes sense before any of the program runs.  It never computes a value.  It remembers *types* instead: `x` is a `Num`, `s` is a `Str`.  To do that, it has to know the type of each name at each point in the program, which is the same question as Part 1: look in this block, and then in the enclosing blocks.  So the checker stores types in the same `Environment`.

Types flow up the tree, so the checker types the parts before it judges the whole.  This small checker represents an expression as a tuple, which keeps the idea in view:

```python
def type_of(node, tenv):
    kind = node[0]
    if kind == "num":
        return "Num"
    if kind == "bool":
        return "Bool"
    if kind == "var":
        try:
            return tenv.lookup(node[1])
        except LangNameError:
            return None                 # undeclared: unknown, so the evaluator reports it
    if kind == "+":
        left = type_of(node[1], tenv)
        right = type_of(node[2], tenv)
        if left in ("Num", None) and right in ("Num", None):
            return "Num"
        raise TypeError(f"'+' requires Num operands, got {left} and {right}")
    raise TypeError(f"no rule for {kind}")
```

`None` is the *unknown* type, which a name gets when nobody declared it.  The checker cannot prove anything about that name, so it skips the check and leaves the error to the evaluator.  The message names both types, because either one could be the mistake.

Try it:

```python
tenv = Environment()
tenv.define("x", "Num")             # let x: Num = 1;

print(type_of(("+", ("var", "x"), ("num", 1)), tenv))
print(type_of(("+", ("var", "z"), ("num", 1)), tenv))
try:
    type_of(("+", ("var", "x"), ("bool", True)), tenv)
except TypeError as e:
    print(e)
```

> **Predict, then run.**  You should see `Num` twice, and then `'+' requires Num operands, got Num and Bool`.  The second line is `Num` even though `z` was never declared, because an unknown type passes the check.

A rule like the one in the `+` branch can also be written on paper, with what must be true above the line and what then holds below it:

```text
e1 : Num    e2 : Num
--------------------
   e1 + e2 : Num
```

The Interpreter assignment uses this `Environment`, so you can carry the class straight into your work there.  If you want to go further, the [optional extensions]({{ site.baseurl }}/Tutorials/EnvironmentsExtensions) trace lexical and dynamic scope and build a fuller checker.
