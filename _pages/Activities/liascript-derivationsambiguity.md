# Derivations, Parse Trees, Ambiguity, and Precedence
<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://github.com/BillJr99/Ursinus-CS374-Fall2026/blob/gh-pages/_pages/Activities/liascript-derivationsambiguity.md or locally via https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374/gh-pages/_pages/Activities/liascript-derivationsambiguity.md

import: https://raw.githubusercontent.com/liascript/CodeRunner/master/README.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

# Derivations, Parse Trees, Ambiguity, and Precedence

A grammar that accepts the right strings can still mean the wrong things: if `2 + 3 * 4` has *two* parse trees, the language has two meanings for one program. Today we build, slowly and deliberately, the standard cure: a layered expression grammar in which **precedence and associativity live in the grammar's shape**. This build-up is the single most important preparation for your parser assignment. The arc: **derivations and trees $\rightarrow$ ambiguity diagnosed $\rightarrow$ the layered grammar, constructed step by step $\rightarrow$ associativity**.

---

## Directions and Group Roles

Work in your POGIL team with rotated roles (**Manager**, **Recorder**, **Presenter**, **Reflector**). Consider each model and question individually first, then discuss with your group. The Recorder posts answers to the Class Activity Questions discussion board; the Presenter reports out areas of disagreement or alternative approaches. After class, respond to the reflective prompt individually in your notebook.

---

# Part I: Trees and the Disease

## 1. From Derivations to Parse Trees

**A parse tree records a derivation with the order forgotten.** The root is the start symbol; each internal node is a nonterminal whose children are the right-hand side of the production applied to it; the leaves, read left to right, spell the input. A **leftmost derivation** always expands the leftmost nonterminal first; every parse tree corresponds to exactly one leftmost derivation, which is why we can speak of trees and derivations interchangeably.

**The tree is the meaning.** When your interpreter evaluates `2 + 3 * 4`, it will evaluate children before parents; the *shape* of the tree therefore decides whether the answer is 14 or 20. Syntax design is meaning design.

---

## Model 1: One String, Two Trees

The naive expression grammar:

```
E -> E + E | E * E | num
```

### Critical Thinking Questions

1. Draw (on paper or the board) **two distinct parse trees** for `2 + 3 * 4` under this grammar. The Recorder photographs or transcribes both.
2. Evaluate each tree bottom-up (children before parents). Which tree yields 14 and which 20? Mark on each tree the node where the meanings diverge.
3. State the definition this exercise has earned: a grammar is **ambiguous** when... (finish the sentence precisely; "confusing" is not precise).
4. Is ambiguity a property of the *string*, the *grammar*, or the *language*? Test your answer: could a different grammar for the same language be unambiguous?

---

# Part II: The Cure, Built One Layer at a Time

## 2. Step 1: Separate the Precedence Levels

**The insight: make the grammar's shape mirror the binding strength.** Operators that bind tighter should live *deeper* in the grammar, so they end up *lower* in every tree. We introduce one nonterminal per precedence level. Start with two levels, addition (loose) and multiplication (tight):

```
E -> E + T | T        (expressions: additions of terms)
T -> T * F | F        (terms: multiplications of factors)
F -> num | ( E )      (factors: atoms, and the reset button)
```

Walk the logic: an `E` is a sum of `T`s; each `T` is a product of `F`s; a parenthesized `E` is demoted back to an atom, which is why parentheses override everything. Try to derive the 20-valued tree for `2 + 3 * 4` now: you cannot, because `*` can only appear *inside* a `T`, below any `+`.

---

## Model 2: Verify the Cure

### Critical Thinking Questions

5. Derive `2 + 3 * 4` from the layered grammar (leftmost derivation, every step). Confirm exactly one tree exists and that it evaluates to 14.
6. Derive `(2 + 3) * 4`. Identify the production that lets the parentheses hoist the addition above the multiplication.
7. Add a new tightest-binding level: exponentiation `^`. Decide as a team where the new nonterminal slots into the chain `E, T, F`, write the modified grammar, and verify on `2 * 3 ^ 2` (should be 18, not 36).

---

## 3. Step 2: Associativity Is Direction of Recursion

Look again at `E -> E + T`. The recursion is on the **left**, so `a - b - c` parses as `(a - b) - c`: **left-associative**, which is what subtraction requires (5 - 2 - 1 is 2, not 4). Had we written `E -> T + E`, the same operator would group to the right. Exponentiation conventionally associates right (`2 ^ 3 ^ 2` is `2 ^ (3 ^ 2)` = 512), so its rule should recurse on the right. **Associativity is not an annotation; it is which side the recursion sits on.**

$$
E \rightarrow E + T \ \text{(left assoc.)} \qquad P \rightarrow F \,\hat{}\, P \mid F \ \text{(right assoc.)}
$$

[[MC]]
In the layered grammar, multiplication binds tighter than addition because:
- ( ) The parser checks a precedence table at runtime
- ( ) Multiplication appears earlier in the file
- (x) The multiplication rule lives deeper in the nonterminal chain, forcing `*` nodes lower in every parse tree
- ( ) The lexer tags `*` with higher priority

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

---

## Model 3: The Dangling Else

Expression ambiguity is not the only kind. Consider:

```
stmt -> "if" expr "then" stmt
      | "if" expr "then" stmt "else" stmt
      | "other"
```

The string `if A then if B then other else other` has two trees: the `else` can attach to either `if`.

### Critical Thinking Questions

8. Sketch both attachments. Which `if` owns the `else` in C, Java, and Python's grammar tradition (the conventional answer: the *nearest* unmatched `if`)?
9. Your team's language must resolve this. List the three standard remedies (grammar rewriting, a disambiguating rule in the parser, or required braces/end markers) and pick one for your project, recording the rationale.

---

# Part III: Synthesis and Practice

## 4. Exercises

1. *Full ladder.* Write the complete unambiguous grammar for expressions with `+ - * / ^`, unary minus, parentheses, numbers, and identifiers, with conventional precedence and associativity. This grammar is, nearly verbatim, the one your parser assignment implements; invest accordingly.
2. *Tree drawing drill.* For `1 + 2 * (3 + 4) - 5`, draw the unique parse tree under your full ladder and evaluate it bottom-up, showing the value at every internal node.
3. *Ambiguity hunt.* Each teammate writes a small grammar (three to five rules) that is secretly ambiguous; the team finds a witness string with two trees for each. Hardest-to-spot ambiguity wins.
4. *Convention archaeology.* Find one language whose precedence or associativity surprises you (APL evaluates right-to-left; Smalltalk gives all binary operators equal precedence). Report the rule and one expression where it bites.

---

## Reflection Prompt

In your notebook: precedence conventions are pure social agreement; mathematics worked fine before PEMDAS was standardized. What does today suggest about how much of "correctness" in computing is convention, and who gets to set it? Connect to one convention your team will set unilaterally in December.

---

## 5. Further Reading

- Douglas Thain. *Introduction to Compilers and Language Design*, Chapter 4.
- Robert Nystrom. *Crafting Interpreters*, "Representing Code" and "Parsing Expressions" (online), the same layering with beautiful diagrams.
- Aho, Lam, Sethi, Ullman. *Compilers: Principles, Techniques, and Tools*, section 4.3, for the formal treatment.
