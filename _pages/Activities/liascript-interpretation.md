# Tree-Walking Interpretation
<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://github.com/BillJr99/Ursinus-CS374-Fall2026/blob/gh-pages/_pages/Activities/liascript-interpretation.md or locally via https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374/gh-pages/_pages/Activities/liascript-interpretation.md

import: https://raw.githubusercontent.com/liascript/CodeRunner/master/README.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

# Tree-Walking Interpretation

The pipeline completes its first full circuit: this two-day module builds the **evaluator**, the recursive tree walk that turns ASTs into values, upgrading your pretty-printer's skeleton into an interpreter. With lexer, parser, and evaluator joined, you will run a program in a language that exists because you built it. The arc: **evaluation as recursion $\rightarrow$ the evaluator in code $\rightarrow$ semantics decisions hiding in plain sight $\rightarrow$ the REPL**.

---

## Directions and Group Roles

Work in your POGIL team with rotated roles (**Manager**, **Recorder**, **Presenter**, **Reflector**). Consider each model and question individually first, then discuss with your group. The Recorder posts answers to the Class Activity Questions discussion board; the Presenter reports out areas of disagreement or alternative approaches. After class, respond to the reflective prompt individually in your notebook.

---

# Part I: Evaluation Is a Fold over the Tree (Day 1)

## 1. The Recursive Definition of Meaning

**The value of a node is defined in terms of the values of its children.** This is denotational thinking made executable:

$$
\mathcal{E}[\![\text{Num}(n)]\!] = n \qquad
\mathcal{E}[\![\text{BinOp}(+, l, r)]\!] = \mathcal{E}[\![l]\!] + \mathcal{E}[\![r]\!]
$$

and so on for every node class: evaluate children first (post-order, exactly as Model 2 of the AST module predicted), then combine with the node's operation. Where the pretty-printer printed, the evaluator returns; the recursion structure is identical, which is why a tree walk is the most honest possible name.

---

## Code Cell

```python
# The evaluator: one dispatch per node class, post-order recursion.
# Uses the Node classes from the AST module; Var lookup arrives properly
# in the environments module, so today variables live in one plain dict.

def evaluate(node, env):
    try:
        if isinstance(node, Num):
            return node.value
        if isinstance(node, Var):
            if node.name not in env:
                raise NameError(f"undefined variable {node.name!r}")
            return env[node.name]
        if isinstance(node, UnaryOp):
            val = evaluate(node.operand, env)
            return -val if node.op == "-" else val
        if isinstance(node, BinOp):
            left = evaluate(node.left, env)      # children first:
            right = evaluate(node.right, env)    # post-order traversal
            if node.op == "+": return left + right
            if node.op == "-": return left - right
            if node.op == "*": return left * right
            if node.op == "/":
                if right == 0:
                    raise ZeroDivisionError("division by zero in your language")
                return left / right
            raise ValueError(f"unknown operator {node.op!r}")
        raise TypeError(f"cannot evaluate node {node!r}")
    except (NameError, ZeroDivisionError, ValueError, TypeError):
        raise
    except Exception as e:
        print(f"[interp:evaluate] {e}")
        import traceback; traceback.print_exc()
        raise

env = {"price": 5.0}
tree = BinOp("+", Num(3), BinOp("*", Var("price"), Num(2)))   # 3 + price * 2
print(evaluate(tree, env))    # 13.0
```

---

## Model 1: The Moment of Meaning

### Critical Thinking Questions

1. Trace `evaluate` on the tree above, writing every call with its arguments and return value, in order. Where in your trace does the multiplication happen relative to the addition, and which week's design decision (which module) put it there?
2. The evaluator never consults precedence, parentheses, or the grammar. State precisely where precedence "went," and why this separation of concerns is the architecture lesson of the whole pipeline.
3. We chose to make division by zero an error with a custom message. List two other behaviors your team could have chosen (return infinity, return zero) and one language that made each choice. Record your project's decision.
4. Compare `evaluate` and `pretty` line by line. Write the general recipe: to add a new *consumer* of the AST (a type checker, an optimizer, a compiler), what do you write and what do you never touch?

---

# Part II: Statements, State, and the REPL (Day 2)

## 2. Executing Statements

Expressions produce values; **statements produce effects**: an `Assign` updates the environment, a `Print` writes output, a `Block` executes children in order, a `While` re-evaluates its condition. The executor therefore threads the environment through:

```
def execute(stmt, env):
    Assign(name, e)   -> env[name] = evaluate(e, env)
    Print(e)          -> print(evaluate(e, env))
    Block(stmts)      -> for s in stmts: execute(s, env)
    If(c, t, o)       -> execute(t if truthy(evaluate(c, env)) else o, env)
    While(c, body)    -> while truthy(evaluate(c, env)): execute(body, env)
```

Notice `truthy`: your language must decide what counts as true (only a boolean? any nonzero number? an empty string?), a semantics decision with daily consequences, and notice that `While` contains a *Python* `while`: a tree-walker borrows the host language's control flow, which is both its charm and its performance ceiling.

[[MC]]
In a tree-walking interpreter, executing the program's `while` loop one million times will re-walk the loop body's subtree one million times. The principal cost this design accepts, relative to compilation, is:
- ( ) Incorrect results on large inputs
- (x) Repeated traversal and dispatch overhead per execution of the same code
- ( ) Loss of operator precedence
- ( ) The inability to support variables

---

## Model 2: The First Run

Wire the full pipeline: `tokenize` (scanning module) into `Parser` (descent and expressions modules) producing AST nodes (AST module) into `execute`. Run, as a team:

```
let n = 5;
let total = 0;
while (n > 0) {
    total = total + n;
    n = n - 1;
}
print total;
```

### Critical Thinking Questions

5. Predict the output before running; then run. If they differ, the bug hunt order is lexer, parser tree (use `pretty`!), evaluator: justify that order in one sentence about where each kind of symptom originates.
6. Print the environment after execution. Should `n` still exist after the loop? Defend your language's answer; both choices are defensible and your project must document one.
7. Add a deliberate bug for a teammate to find: change one character anywhere in the pipeline. Time the hunt with and without `pretty` available. What did the tree printer buy?

---

## 3. Exercises

1. *Complete the executor.* Implement `execute` for all your statement nodes with the exception pattern from class, define and document `truthy` for your language, and demonstrate the summation program plus an `if/else` program.
2. *The REPL.* Write the read-evaluate-print loop: prompt, read a line, tokenize, parse, execute against a persistent environment, repeat, catching and printing every error class without dying. Your language now has an interactive shell; transcript required.
3. *Error taxonomy.* Construct one program each that fails in the lexer, the parser, and the evaluator. Verify each error message names its stage and location; improve the worst one.
4. *Semantics memo.* Document three semantics decisions your team made today (truthiness, division by zero, loop variable persistence) in a `SEMANTICS.md` your project will grow all semester.

---

## Reflection Prompt

In your notebook: you have now run a program in a language whose every component you understand, with no magic remaining between the characters and the answer. How does that change how you regard the languages you use daily, and what magic do you now most want to dispel next?

---

## 4. Further Reading

- Douglas Thain. *Introduction to Compilers and Language Design*, Chapter 5 and interpretation notes.
- Robert Nystrom. *Crafting Interpreters*, "Evaluating Expressions" and "Statements and State" (online): our exact path, expanded.
- Shriram Krishnamurthi. *PLAI*, the interpreter chapters, for the denotational view.
