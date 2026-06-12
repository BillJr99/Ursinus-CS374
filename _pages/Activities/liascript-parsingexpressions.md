# Parsing Expressions: Left Factoring, Precedence, and Iteration
<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://github.com/BillJr99/Ursinus-CS374-Fall2026/blob/gh-pages/_pages/Activities/liascript-parsingexpressions.md or locally via https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374/gh-pages/_pages/Activities/liascript-parsingexpressions.md

import: https://raw.githubusercontent.com/liascript/CodeRunner/master/README.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

# Parsing Expressions: Left Factoring, Precedence, and Iteration

This two-day module is the heart of your parser: turning the layered expression grammar (the cure for ambiguity) into running code, with explicit, careful attention to the move students find hardest: rewriting left recursion as the iteration pattern `term { (op) term }` and folding the loop's results into a left-leaning structure. We build it slowly, one operator tier at a time, exactly as your assignment will. The arc: **the ladder restated for descent $\rightarrow$ one tier in code $\rightarrow$ chaining operators in the loop $\rightarrow$ the full ladder with parentheses and unary minus**.

---

## Directions and Group Roles

Work in your POGIL team with rotated roles (**Manager**, **Recorder**, **Presenter**, **Reflector**). Consider each model and question individually first, then discuss with your group. The Recorder posts answers to the Class Activity Questions discussion board; the Presenter reports out areas of disagreement or alternative approaches. After class, respond to the reflective prompt individually in your notebook.

---

# Part I: The Ladder, Descent-Ready (Day 1)

## 1. From Left Recursion to Loops, Tier by Tier

The unambiguous ladder used left recursion, which descent cannot run. We rewrite **every tier** in the loop form, and the whole grammar becomes:

```
expr   -> addsub
addsub -> muldiv { ("+" | "-") muldiv }
muldiv -> unary  { ("*" | "/") unary }
unary  -> "-" unary | primary
primary-> NUMBER | IDENT | "(" expr ")"
```

Read the shape: each tier parses one item of the *next tighter* tier, then loops over its own operators. Precedence is still the depth of the chain; associativity now lives in **how the loop folds**: if each iteration wraps the running result as the *left* child of a new node, the chain leans left, exactly what `-` and `/` require.

$$
a - b - c \;\Rightarrow\; \texttt{(("-",("-",a,b),c))} \quad \text{left fold, left lean}
$$

---

## Model 1: Trace the Loop

Consider `addsub` parsing the token stream for `7 - 2 - 1`.

### Critical Thinking Questions

1. Walk the loop by hand: what does the first `parse_muldiv()` return; what happens on each `while` iteration; what is the running `node` after each? The Recorder draws the tree growing.
2. Suppose the loop body instead wrapped the new operand as the left child and the running result as the right. What tree, and what wrong value, results for `7 - 2 - 1`? You have just located associativity in a single line of code.
3. Why does the loop in `addsub` test for `+` *or* `-` while leaving `*` to a different function entirely? Connect to the depth-equals-precedence principle.

---

## Code Cell

```python
# The expression parser, one tier at a time, designed to drop into the
# Parser class from the recursive descent module. Tuples for now; the AST
# module upgrades them to classes.

def parse_expr(self):
    return self.parse_addsub()

# addsub -> muldiv { ("+" | "-") muldiv }
def parse_addsub(self):
    try:
        node = self.parse_muldiv()
        while self.peek() and self.peek().type in ("PLUS", "MINUS"):
            op = self.advance().lexeme          # consume the operator
            right = self.parse_muldiv()         # parse the next operand
            node = (op, node, right)            # LEFT fold: old node goes left
        return node
    except SyntaxError:
        raise
    except Exception as e:
        print(f"[exprparser:parse_addsub] {e}")
        import traceback; traceback.print_exc()
        raise

# muldiv -> unary { ("*" | "/") unary }
def parse_muldiv(self):
    node = self.parse_unary()
    while self.peek() and self.peek().type in ("STAR", "SLASH"):
        op = self.advance().lexeme
        right = self.parse_unary()
        node = (op, node, right)
    return node

# unary -> "-" unary | primary
def parse_unary(self):
    if self.peek() and self.peek().type == "MINUS":
        self.advance()
        return ("neg", self.parse_unary())
    return self.parse_primary()

# primary -> NUMBER | IDENT | "(" expr ")"
def parse_primary(self):
    tok = self.peek()
    if tok and tok.type == "NUMBER":
        self.advance(); return ("num", float(tok.lexeme))
    if tok and tok.type == "IDENT":
        self.advance(); return ("var", tok.lexeme)
    if tok and tok.type == "LPAREN":
        self.advance()
        node = self.parse_expr()
        self.expect("RPAREN")
        return node
    raise SyntaxError(f"expected an expression, found "
                      f"{tok.lexeme!r} at line {tok.line}" if tok else "end of input")
```

---

## Model 2: Read the Tiers

### Critical Thinking Questions

4. Annotate the correspondence: which EBNF symbol became the `while` condition, which became `advance()`, which became the recursive call? (This is the translation table earning its keep.)
5. Trace `2 + 3 * 4` through the functions, listing every call in order and the tuple each returns. Confirm the multiplication nests *inside* the addition without any precedence table existing anywhere.
6. `parse_unary` calls itself for `--x`. Is that recursion left recursion? Why does it terminate where `E -> E + T` would not?
7. `parse_primary`'s parenthesis case calls all the way back up to `parse_expr`. Explain how this single call makes parentheses override every precedence level, and find the matching production in the grammar.

---

# Part II: Stress and Extend (Day 2)

## 2. Owning the Pattern

[[MC]]
In `parse_addsub`, the line `node = (op, node, right)` places the previous result as the left child. Changing nothing else, this single line determines that:
- ( ) Multiplication binds tighter than addition
- (x) Operators at this tier associate left, so `7 - 2 - 1` evaluates as `(7 - 2) - 1`
- ( ) Parentheses are honored
- ( ) The grammar is LL(1)

---

## 3. Exercises

1. *Right-associative tier.* Add exponentiation `^` binding tighter than `*` and associating right. The loop pattern will not give right association; the original right-recursive form `power -> unary [ "^" power ]` will. Implement it, and verify `2 ^ 3 ^ 2` yields the tree for `2 ^ (3 ^ 2)`.
2. *Comparison tier.* Add `< <= > >= == !=` at a tier *looser* than `addsub` (so `a + 1 < b * 2` parses sensibly). Decide and document: should `a < b < c` be legal in your language, and if so, what should it mean? (Python and C disagree; your team must choose for December.)
3. *Torture tests.* Run your full parser on: `-(3 + 4) * -2`, `((1))`, `1 + + 2` (should fail; check the message), and `8 / 4 / 2` (must be 1, not 4, once evaluated). Submit the trees or errors for each.
4. *Function calls.* Extend `primary` so an identifier may be followed by an argument list: `IDENT "(" [ expr { "," expr } ] ")"`. Note which EBNF constructs you used and which code shapes they became. Your project language will thank you.

---

## Reflection Prompt

In your notebook: the hardest conceptual move this week was seeing that a `while` loop and a left-recursive production say the same thing. Write the explanation of that equivalence you wish someone had given you on Monday, in your own words, for a future student.

---

## 4. Further Reading

- Douglas Thain. *Introduction to Compilers and Language Design*, Chapter 4.
- Robert Nystrom. *Crafting Interpreters*, "Parsing Expressions" (online): the same ladder with pictures.
- Vaughan Pratt. "Top Down Operator Precedence" (1973), the elegant alternative your instructor will sketch if time allows.
