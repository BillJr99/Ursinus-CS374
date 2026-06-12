# Control Flow Semantics
<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://github.com/BillJr99/Ursinus-CS374-Fall2026/blob/gh-pages/_pages/Activities/liascript-controlflowsemantics.md or locally via https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374/gh-pages/_pages/Activities/liascript-controlflowsemantics.md

import: https://raw.githubusercontent.com/liascript/CodeRunner/master/README.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

# Control Flow Semantics

`if` and `while` look trivial until you must implement them, at which point a swarm of decisions appears: what counts as true? are both branches evaluated? does `and` evaluate its right side when the left already decides? Today we pin down **control flow semantics** for your interpreter assignment, with special attention to **truthiness** and **short-circuit evaluation**, two places where languages quietly disagree. The arc: **selection semantics $\rightarrow$ truthiness $\rightarrow$ short-circuiting $\rightarrow$ iteration and its design questions**.

---

## Directions and Group Roles

Work in your POGIL team with rotated roles (**Manager**, **Recorder**, **Presenter**, **Reflector**). Consider each model and question individually first, then discuss with your group. The Recorder posts answers to the Class Activity Questions discussion board; the Presenter reports out areas of disagreement or alternative approaches. After class, respond to the reflective prompt individually in your notebook.

---

# Part I: Selection and Truth

## 1. The Semantics of If

**Selection evaluates the condition, then exactly one branch.** The "exactly one" is load-bearing: in `if (x != 0) { print 10 / x; } else { print 0; }`, evaluating the untaken branch would divide by zero. Your executor already respects this (the Python `if` inside `execute` chooses *which subtree to walk*), and naming the property matters: `if` is our first **non-strict** construct, one that deliberately does not evaluate all of its parts.

**Truthiness: what may stand as a condition?** Three coherent policies: (a) **booleans only** (Java): `if (count)` is a type error; (b) **everything has a truth value** (Python: zero, empty string, and empty collections are falsy; the rest truthy); (c) **a designated set** (C: zero is false, any nonzero number true). The policy interacts with your type system: a booleans-only language catches `if (x = 5)`-style accidents that permissive languages execute happily.

---

## Model 1: The Truthiness Tribunal

The condition values: `0`, `1`, `-3`, `""`, `"false"`, an empty list, the boolean `false`.

### Critical Thinking Questions

1. For each value, rule its truth under policies (a), (b), and (c) (write "error" where the policy rejects it). Where do the policies disagree most surprisingly? (`"false"` deserves the team's attention.)
2. The classic C bug `if (x = 5)` (assignment, not comparison) runs and is always true. Which policy, and separately which *grammar* decision (is assignment an expression?), each independently prevents it? Your language gets two chances to kill this bug; choose at least one.
3. Decide your project's truthiness policy and write the `truthy(value)` specification in `SEMANTICS.md` language: exhaustive, no "etc."

---

# Part II: Short-Circuit Evaluation

## 2. And/Or That Stop Early

**Short-circuit operators evaluate left to right and stop as soon as the answer is known**: `false and X` never evaluates `X`; `true or X` never evaluates `X`. This is not an optimization but a *semantic guarantee* programs rely on: `if (i < len(a) and a[i] > 0)` is only safe because the bounds check guards the access. Implementing it means `and`/`or` cannot be ordinary `BinOp`s (your `BinOp` case evaluates both children first, post-order); they need their own node and their own evaluation rule.

$$
\mathcal{E}[\![l \text{ and } r]\!] = \begin{cases} \mathcal{E}[\![l]\!] & \text{if } \mathcal{E}[\![l]\!] \text{ is falsy} \\ \mathcal{E}[\![r]\!] & \text{otherwise} \end{cases}
$$

(Note the Python-style refinement: returning the deciding *operand* rather than a normalized boolean is itself a design choice; Java normalizes, Python does not.)

---

## Code Cell

```python
# Short-circuit logic as its own node type: the right child is evaluated
# conditionally, unlike every BinOp. Demonstrated with a guard idiom.

class LogicOp:
    def __init__(self, op, left, right):
        self.op, self.left, self.right = op, left, right

def truthy(v):
    """Project policy goes here; this demo uses Python-style truthiness."""
    return bool(v)

def eval_logic(node, env, evaluate):
    try:
        left = evaluate(node.left, env)
        if node.op == "and":
            return evaluate(node.right, env) if truthy(left) else left
        if node.op == "or":
            return left if truthy(left) else evaluate(node.right, env)
        raise ValueError(f"unknown logical operator {node.op!r}")
    except ValueError:
        raise
    except Exception as e:
        print(f"[controlflow:eval_logic] {e}")
        import traceback; traceback.print_exc()
        raise

# Proof that the right side is skipped: a right child that would explode.
class Bomb:
    pass

def evaluate_demo(node, env):
    if isinstance(node, bool):
        return node
    if isinstance(node, Bomb):
        raise RuntimeError("the right side was evaluated!")
    if isinstance(node, LogicOp):
        return eval_logic(node, env, evaluate_demo)
    raise TypeError(f"unknown node {node!r}")

print(evaluate_demo(LogicOp("and", False, Bomb()), {}))   # False, no explosion
print(evaluate_demo(LogicOp("or",  True,  Bomb()), {}))   # True, no explosion
try:
    evaluate_demo(LogicOp("and", True, Bomb()), {})       # now it must look right
except RuntimeError as e:
    print("as expected:", e)
```

---

## Model 2: The Bomb Test

### Critical Thinking Questions

4. The Bomb proves non-evaluation by *absence of explosion*. Why is this a better test than inspecting return values, and what general testing idea (observing side effects to detect evaluation) did you just use?
5. Trace why `LogicOp` cannot be folded into your `BinOp` case: quote the one line of the BinOp evaluator that makes it impossible.
6. Your parser must give `and`/`or` a precedence tier. Should `a == b and c == d` parse as `(a == b) and (c == d)`? Place the new tier in your ladder (looser or tighter than comparison?) and justify with that example.

[[MC]]
The guarantee that `i < n and items[i] > 0` never indexes out of bounds depends on:
- ( ) The parser checking array lengths
- ( ) Operator precedence placing and below comparison
- (x) The semantic rule that and does not evaluate its right operand when the left is falsy
- ( ) The type checker proving i is a number

---

# Part III: Iteration

## 3. While, and the Questions It Raises

Your `While` executor re-evaluates the condition before each pass: definite semantics, easy to implement, and the source of three design questions your team must answer in `SEMANTICS.md`: (1) does the body create a fresh scope per iteration (the environments module's exercise); (2) do you provide `break`/`continue`, and if so, how does a tree-walker implement a statement that must terminate an *enclosing* construct (the classic implementation uses a special exception class thrown by `break` and caught by the loop, a perfect job for a custom exception); (3) will you offer a counting `for`, and is it core syntax or sugar that your parser rewrites into `while` (a *desugaring*, your first taste of compilation).

## 4. Exercises

1. *Implement the trio.* Add `LogicOp` with short-circuit `and`/`or` and a unary `not` to your lexer, parser (new tier), and evaluator. Reproduce the Bomb test inside *your* language: a right operand that would raise (divide by zero) but is never reached.
2. *Break and continue.* Implement both using custom exception classes (`BreakSignal`, `ContinueSignal`) raised by the statements and caught by the `While` executor, with the class exception-logging pattern on any *unexpected* exception. Demonstrate a search loop that exits early.
3. *Desugaring.* Implement `for (let i = 0; i < n; i = i + 1) { ... }` purely in the parser, producing the AST of the equivalent block-plus-while with no new evaluator code. Show the `pretty` output proving the rewrite.
4. *Truthiness differential.* Write one program whose output differs under booleans-only versus Python-style truthiness, and confirm your interpreter follows your documented policy on it.

---

## Reflection Prompt

In your notebook: short-circuiting means the language promises *not to look* at something. Contracts about what will not be examined are everywhere (sealed exams, privacy policies, blind review). Pick one and describe what breaks when the no-look promise is violated, in computing or out of it.

---

## 5. Further Reading

- Douglas Thain. *Introduction to Compilers and Language Design*, Chapter 6 and 7 notes on control flow.
- Robert Nystrom. *Crafting Interpreters*, "Control Flow" (online), including the break-via-exception trick.
- Robert Sebesta. *Concepts of Programming Languages*, the statement-level control structures chapter.
