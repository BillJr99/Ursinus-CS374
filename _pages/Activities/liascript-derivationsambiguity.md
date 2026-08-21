<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374/gh-pages/_pages/Activities/liascript-derivationsambiguity.md or locally via https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374/gh-pages/_pages/Activities/liascript-derivationsambiguity.md

import: https://raw.githubusercontent.com/liascript/CodeRunner/master/README.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

# Derivations, Parse Trees, Ambiguity, and Precedence

Consider the English sentence "I saw the man with the telescope." Did you use the telescope to see him, or did he have the telescope? Both readings are grammatically valid; the sentence is ambiguous. Formal grammars for programming languages can have exactly the same problem: a single expression like `2 + 3 * 4` can fit the grammar in two different ways, producing two different parse trees with two different values. Unlike the telescope sentence, ambiguity in a grammar is silent and dangerous; your parser will just pick one interpretation and quietly give you the wrong answer.

## Learning Goals

By the end of this activity, you will be able to:

- Construct a leftmost derivation and draw the corresponding parse tree for a given string under a provided context-free grammar
- Define grammar ambiguity precisely and demonstrate it by producing two distinct parse trees for the same string under an ambiguous grammar
- Explain how a layered (stratified) expression grammar encodes operator precedence and associativity in its structure rather than in external rules
- Construct an unambiguous expression grammar that enforces a specified precedence and associativity for multiple operator levels, and verify it by deriving a target expression
- Analyze an existing grammar to determine whether it correctly captures left or right associativity, and modify it to reverse the associativity if needed

A grammar of the kind you wrote in *Grammars and the Chomsky Hierarchy* can accept the right strings and still mean the wrong things: if `2 + 3 * 4` has *two* parse trees, the language has two meanings for one program. Today we build, slowly and deliberately, the standard cure: a layered expression grammar in which **precedence and associativity live in the grammar's shape**. This build-up is the single most important preparation for your parser assignment. The arc: **derivations and trees $\rightarrow$ ambiguity diagnosed $\rightarrow$ the layered grammar, constructed step by step $\rightarrow$ associativity**.

---

> **Before You Begin**, make sure you are comfortable with the following ideas before working through the models:
>
> - **BNF/EBNF grammar notation**: you can read a rule like `E -> E + T | T` and name its nonterminals, terminals, and alternative productions.
> - **Parse trees**: you know that a parse tree shows which productions were applied to derive a string, with the start symbol at the root and input tokens as leaves.
> - **Left vs. right associativity**: you know that `a - b - c` evaluates as `(a - b) - c` in most languages (left-associative), and that `2 ^ 3 ^ 2` evaluates as `2 ^ (3 ^ 2)` in languages where exponentiation is right-associative.
>
> If any of these feel shaky, review your grammar notes before continuing.

---

## Directions and Group Roles

Work in your POGIL team with rotated roles (**Manager**, **Recorder**, **Presenter**, **Reflector**). Consider each model and question individually first, then discuss with your group. The Recorder posts answers to the Class Activity Questions discussion board; the Presenter reports out areas of disagreement or alternative approaches. After class, respond to the reflective prompt individually in your notebook.

---

# Part I: Trees and the Disease

## 1. From Derivations to Parse Trees

*Intuition: A derivation is a recipe, a sequence of grammar rule applications that turns a start symbol into a string of tokens. A parse tree is that same recipe drawn as a picture, where the cooking order no longer matters. The shape of the tree is what your interpreter will actually execute, so two different trees for the same string mean two different programs hiding in identical source code.*

**A parse tree records a derivation with the order forgotten.** The root is the start symbol; each internal node is a nonterminal whose children are the right-hand side of the production applied to it; the leaves, read left to right, spell the input. A **leftmost derivation** always expands the leftmost nonterminal first; every parse tree corresponds to exactly one leftmost derivation, which is why we can speak of trees and derivations interchangeably.

**The tree is the meaning.** When your interpreter evaluates `2 + 3 * 4`, it will evaluate children before parents; the *shape* of the tree therefore decides whether the answer is 14 or 20. Syntax design is meaning design.

---

## Model 1: One String, Two Trees

*Intuition: The grammar `E -> E + E | E * E | num` looks perfectly reasonable at first glance: it says an expression can be a sum, a product, or a number. The problem is that it says nothing about which operation groups first, so a parser following it has equal freedom to build either tree. This model makes that ambiguity concrete by constructing both trees by hand.*

> **Watch out!** An ambiguous grammar produces **multiple valid parse trees for the same input string**. This is not a runtime error or a warning; the grammar and parser will both succeed, and you will get a silently wrong result. Always look for witness strings (inputs with two trees) when you design a grammar.

The naive expression grammar:

```
E -> E + E | E * E | num
```

### Critical Thinking Questions

1. Draw (on paper or the board) **two distinct parse trees** for `2 + 3 * 4` under this grammar. The Recorder photographs or transcribes both.
2. Evaluate each tree bottom-up (children before parents). Which tree yields 14 and which 20? Mark on each tree the node where the meanings diverge.
3. State the definition this exercise has earned: a grammar is **ambiguous** when... (finish the sentence precisely; "confusing" is not precise).
4. Is ambiguity a property of the *string*, the *grammar*, or the *language*? Test your answer: could a different grammar for the same language be unambiguous?


> The worked answers to this session's models are in the **Answer Key** at the end of this page. Attempt them with your team first.

# Part II: The Cure, Built One Layer at a Time

## 2. Step 1: Separate the Precedence Levels

*Intuition: The fix for ambiguity is to take the precedence rules that lived in your head ("multiply before you add") and bake them into the grammar's structure. Each precedence level gets its own nonterminal, and the nonterminals are chained so that tighter-binding operators always appear deeper in the tree, meaning they always evaluate first.*

> **Watch out!** Fixing ambiguity requires **rewriting the grammar**, not just adding a note to the parser. A parser that reads an ambiguous grammar and "picks the right tree by convention" is fragile: different parser generators may pick differently, and the ambiguity can resurface in edge cases you didn't test.

**The insight: make the grammar's shape mirror the binding strength.** Operators that bind tighter should live *deeper* in the grammar, so they end up *lower* in every tree. We introduce one nonterminal per precedence level. Start with two levels, addition (loose) and multiplication (tight):

```
E -> E + T | T        (expressions: additions of terms)
T -> T * F | F        (terms: multiplications of factors)
F -> num | ( E )      (factors: atoms, and the reset button)
```

Walk the logic: an `E` is a sum of `T`s; each `T` is a product of `F`s; a parenthesized `E` is demoted back to an atom, which is why parentheses override everything. Try to derive the 20-valued tree for `2 + 3 * 4` now: you cannot, because `*` can only appear *inside* a `T`, below any `+`.

---

## Model 2: Verify the Cure

*Intuition: The best way to convince yourself the layered grammar actually works is to try to derive the "wrong" tree and fail. If you cannot build a tree where `+` sits below `*`, the grammar has successfully encoded precedence. Work through the leftmost derivation step by step; each expansion will force you down the nonterminal chain in only one valid way.*

### Critical Thinking Questions

5. Derive `2 + 3 * 4` from the layered grammar (leftmost derivation, every step). Confirm exactly one tree exists and that it evaluates to 14.
6. Derive `(2 + 3) * 4`. Identify the production that lets the parentheses hoist the addition above the multiplication.
7. Add a new tightest-binding level: exponentiation `^`. Decide as a team where the new nonterminal slots into the chain `E, T, F`, write the modified grammar, and verify on `2 * 3 ^ 2` (should be 18, not 36).

## 3. Step 2: Associativity Is Direction of Recursion

*Intuition: Once you have separate precedence levels, you still need to decide how a chain of the same operator groups: does `5 - 2 - 1` mean `(5-2)-1 = 2` or `5-(2-1) = 4`? The grammar encodes this entirely through which side the recursion appears on: left recursion means the leftmost operation groups first (left-associativity), and right recursion means the rightmost groups first.*

> **Watch out!** Operator precedence and associativity are **two separate things encoded in two separate grammar properties**. Precedence is controlled by the depth of the nonterminal in the chain (deeper = tighter binding). Associativity is controlled by which side of the production the recursive nonterminal appears on (left side = left-associative). Getting one right does not automatically get the other right.

Look again at `E -> E + T`. The recursion is on the **left**, so `a - b - c` parses as `(a - b) - c`: **left-associative**, which is what subtraction requires (5 - 2 - 1 is 2, not 4). Had we written `E -> T + E`, the same operator would group to the right. Exponentiation conventionally associates right (`2 ^ 3 ^ 2` is `2 ^ (3 ^ 2)` = 512), so its rule should recurse on the right. **Associativity is not an annotation; it is which side the recursion sits on.**

$$
E \rightarrow E + T \ \text{(left assoc.)} \qquad P \rightarrow F \,\hat{}\, P \mid F \ \text{(right assoc.)}
$$

In the layered grammar, multiplication binds tighter than addition because:

[( )] The parser checks a precedence table at runtime
[( )] Multiplication appears earlier in the file
[(X)] The multiplication rule lives deeper in the nonterminal chain, forcing `*` nodes lower in every parse tree
[( )] The lexer tags `*` with higher priority

---

## Code Cell

```python
# Feel the trees: two hand-built trees for 2 + 3 * 4, evaluated bottom-up.
# Tuples encode nodes: (op, left, right) or a number leaf.

def evaluate(node):
    try:
        if isinstance(node, (int, float)):
            return node
        op, left, right = node
        l, r = evaluate(left), evaluate(right)
        return l + r if op == "+" else l * r
    except Exception as e:
        print(f"[derivations:evaluate] {e}")
        import traceback; traceback.print_exc()
        return None

tree_correct = ("+", 2, ("*", 3, 4))     # the layered grammar's only tree
tree_wrong   = ("*", ("+", 2, 3), 4)     # the tree the naive grammar also allowed

print("layered grammar tree :", evaluate(tree_correct))   # 14
print("ambiguous alternative:", evaluate(tree_wrong))     # 20

# Associativity: 5 - 2 - 1 both ways (treat "+" as "-" mentally, or extend evaluate)
left_assoc  = ("-", ("-", 5, 2), 1)      # (5-2)-1 = 2   <- E -> E - T
right_assoc = ("-", 5, ("-", 2, 1))      # 5-(2-1) = 4   <- E -> T - E
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

---


> **The runnable versions are on their own page.** A derivation tracer, an ambiguity detector, and a tree-comparison harness are in [Grammar Tooling in Python](https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374/gh-pages/_pages/Tutorials/tutorial-grammars-in-python.md). Use the ambiguity detector on your own project grammar before you build a parser on it.

## Model 7: The Dangling Else

*Intuition: Ambiguity is not limited to arithmetic expressions. Any grammar rule that allows a construct to attach to more than one parent can be ambiguous. The dangling `else` is the most famous example from real language design; virtually every language that has `if/else` has had to make an explicit choice to resolve it.*

Expression ambiguity is not the only kind. Consider:

```
stmt -> "if" expr "then" stmt
      | "if" expr "then" stmt "else" stmt
      | "other"
```

The string `if A then if B then other else other` has two trees: the `else` can attach to either `if`.

### Critical Thinking Questions

17. Sketch both attachments. Which `if` owns the `else` in C, Java, and Python's grammar tradition (the conventional answer: the *nearest* unmatched `if`)?
18. Your team's language must resolve this. List the three standard remedies (grammar rewriting, a disambiguating rule in the parser, or required braces/end markers) and pick one for your project, recording the rationale.

---

# Part III: Synthesis and Practice

## 4. Exercises

1. *Full ladder.* Write the complete unambiguous grammar for expressions with `+ - * / ^`, unary minus, parentheses, numbers, and identifiers, with conventional precedence and associativity. This grammar is, nearly verbatim, the one your parser assignment implements; invest accordingly.
2. *Tree drawing drill.* For `1 + 2 * (3 + 4) - 5`, draw the unique parse tree under your full ladder and evaluate it bottom-up, showing the value at every internal node.
3. *Ambiguity hunt.* Each teammate writes a small grammar (three to five rules) that is secretly ambiguous; the team finds a witness string with two trees for each. Hardest-to-spot ambiguity wins.
4. *Convention archaeology.* Find one language whose precedence or associativity surprises you (APL evaluates right-to-left; Smalltalk gives all binary operators equal precedence). Report the rule and one expression where it bites.

---

## Practice: Allison, Ch. 6 §6.1-6.2: Derivation Trees and Ambiguous Grammars

> *Exercises adapted from topics covered in *Foundations of Computing* by Chuck Allison (Fresh Sources, Inc.), used under the [MIT License](https://github.com/chuckallison/foundations-of-computing/blob/main/LICENSE).*

A grammar is ambiguous if:

[( )] It has more than one nonterminal
[( )] Some of its rules are left-recursive
[(X)] Some string in the language has two or more distinct parse trees
[( )] It generates an infinite language

Left-recursion in a grammar rule causes a problem for:

[( )] LR parsers
[(X)] LL (recursive-descent) parsers
[( )] Both equally
[( )] Neither (left-recursion is handled by both parser types)

The "dangling else" ambiguity occurs because:

[( )] The `else` keyword is reserved in most languages
[( )] `if` and `else` have the same precedence
[(X)] The grammar does not specify which `if` an `else` belongs to when they are nested
[( )] The parser cannot distinguish `if` from `else` tokens

1. *Derivation tree practice.* For the unambiguous ladder grammar (expr -> term { ("+"|"-") term }, term -> factor { ("*"|"/") factor }, factor -> NUMBER | "(" expr ")"), draw the unique derivation tree for `3 - 1 - 1`. Show both the tree and the bottom-up evaluation order.

2. *Leftmost vs. rightmost derivation.* Using the grammar `S -> S + S | id`, give both the leftmost and the rightmost derivation for `id + id + id`. Show that this grammar has more than two parse trees for this string.

3. *Eliminate ambiguity.* The following grammar for `if/else` is ambiguous:
   ```
   stmt -> "if" expr "then" stmt
         | "if" expr "then" stmt "else" stmt
         | OTHER
   ```
   Write an unambiguous version that implements the "nearest enclosing if" convention (each `else` matches the most recent unmatched `if`). Demonstrate on `if e1 then if e2 then s1 else s2`.

4. *Associativity in parse trees.* Show that the grammar `E -> E - E | NUMBER` produces two parse trees for `5 - 3 - 1`. Modify the grammar to enforce left-associativity and draw the single parse tree that results.

5. *EBNF to BNF.* Convert the EBNF rule `expr -> term { ("+" | "-") term }` to standard BNF (no `{...}` or `[...]`). How does the BNF version encode left-associativity? Compare the derivation trees produced by both versions for `1 + 2 + 3`.

---

## Reflection Prompt

In your notebook: precedence conventions are pure social agreement; mathematics worked fine before PEMDAS was standardized. What does today suggest about how much of "correctness" in computing is convention, and who gets to set it? Connect to one convention your team will set unilaterally in December.

---

## 5. Further Reading

- Douglas Thain. *Introduction to Compilers and Language Design*, Chapter 4.
- Robert Nystrom. *Crafting Interpreters*, "Representing Code" and "Parsing Expressions" (online), the same layering with beautiful diagrams.
- Aho, Lam, Sethi, Ullman. *Compilers: Principles, Techniques, and Tools*, section 4.3, for the formal treatment.

---

Up next: the *Regular Expressions* activity drops to the hierarchy's bottom rung, and the Regular Expressions assignment, handed out now, puts it to work.

# Answer Key

Work the models above with your team before reading these. Each one answers a Critical Thinking Question the session poses; seeing the answer first turns the exercise into transcription.

### Worked Example: both trees for `2 + 3 * 4`, drawn

Do CTQ 1 yourself first. Then check against this: the point is not the answer, it is seeing that *both* derivations are legal under the same grammar.

**Tree A, `+` on top (multiply first, value 14):**

```
            E
          / | \
         E  +  E
         |     /|\
        num   E * E
         |    |   |
         2   num num
              |   |
              3   4
```

Leftmost derivation for Tree A, one production per line:

```
E
=> E + E          (used E -> E + E)
=> num + E        (used E -> num, leftmost E first)
=> 2 + E
=> 2 + E * E      (used E -> E * E)
=> 2 + num * E    (used E -> num)
=> 2 + 3 * E
=> 2 + 3 * num    (used E -> num)
=> 2 + 3 * 4
```

**Tree B, `*` on top (add first, value 20):**

```
            E
          / | \
         E  *  E
        /|\     |
       E + E   num
       |   |    |
      num num   4
       |   |
       2   3
```

Leftmost derivation for Tree B:

```
E
=> E * E          (used E -> E * E)
=> E + E * E      (used E -> E + E on the leftmost E)
=> num + E * E    (used E -> num)
=> 2 + E * E
=> 2 + num * E    (used E -> num)
=> 2 + 3 * E
=> 2 + 3 * num    (used E -> num)
=> 2 + 3 * 4
```

**Both derivations end at the same string.** That is the whole definition: the grammar admits two distinct leftmost derivations of `2 + 3 * 4`, so it is ambiguous. Note the divergence is at the *very first step* (`E -> E + E` versus `E -> E * E`) and everything after is forced. CTQ 2 asks where the meanings diverge; it is the root node, and nothing below it.


---

### Worked Example: the layered grammar admits only one tree

CTQ 5 asks you to derive `2 + 3 * 4` from the layered grammar. Here is that derivation, and then the failure you should try to produce for the other tree.

```
E
=> E + T          (used E -> E + T)
=> T + T          (used E -> T)
=> F + T          (used T -> F)
=> num + T        (used F -> num)
=> 2 + T
=> 2 + T * F      (used T -> T * F)
=> 2 + F * F      (used T -> F)
=> 2 + num * F    (used F -> num)
=> 2 + 3 * F
=> 2 + 3 * num    (used F -> num)
=> 2 + 3 * 4
```

The resulting tree, with `*` forced below `+`:

```
            E
          / | \
         E  +  T
         |    /|\
         T   T * F
         |   |    |
         F   F   num
         |   |    |
        num num   4
         |   |
         2   3
```

**Now try to build Tree B and watch it fail.** To put `*` at the root you would need `E -> E * ...`, but no production for `E` mentions `*` at all; `*` appears only in `T -> T * F`, and every `T` sits *below* an `E`. There is no path. That impossibility is the cure working: precedence is not a convention the parser applies, it is a shape the grammar cannot violate.

For CTQ 6, the production that lets parentheses win is `F -> ( E )`. It demotes a whole expression back down to a factor, which is why `(2 + 3) * 4` can put `+` beneath `*`:

```
E => T => T * F => F * F => ( E ) * F => ( E + T ) * F => ... => ( 2 + 3 ) * 4
```


---

