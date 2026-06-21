# Derivations, Parse Trees, Ambiguity, and Precedence
<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://github.com/BillJr99/Ursinus-CS374-Fall2026/blob/gh-pages/_pages/Activities/liascript-derivationsambiguity.md or locally via https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374-Fall2026/gh-pages/_pages/Activities/liascript-derivationsambiguity.md

import: https://raw.githubusercontent.com/liascript/CodeRunner/master/README.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

# Derivations, Parse Trees, Ambiguity, and Precedence

## Learning Goals

By the end of this activity, you will be able to:

- Construct a leftmost derivation and draw the corresponding parse tree for a given string under a provided context-free grammar
- Define grammar ambiguity precisely and demonstrate it by producing two distinct parse trees for the same string under an ambiguous grammar
- Explain how a layered (stratified) expression grammar encodes operator precedence and associativity in its structure rather than in external rules
- Construct an unambiguous expression grammar that enforces a specified precedence and associativity for multiple operator levels, and verify it by deriving a target expression
- Analyze an existing grammar to determine whether it correctly captures left or right associativity, and modify it to reverse the associativity if needed

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
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

---

## Model 4: Derivation Tracer (Runnable)

A leftmost derivation always expands the leftmost nonterminal at each step; a rightmost derivation always expands the rightmost one. Watching them side by side makes it concrete that **both derivations produce the same parse tree** even though the step sequences differ.

```python
# Model 4: Leftmost and rightmost derivation tracer for simple CFGs

GRAMMAR = {
    "E": [["E", "+", "T"], ["T"]],
    "T": [["T", "*", "F"], ["F"]],
    "F": [["(", "E", ")"], ["num"]],
}
TERMINALS = {"+", "*", "(", ")", "num"}

def is_terminal(sym):
    return sym in TERMINALS

def expand(form, grammar, leftmost=True):
    """Yield each step of a leftmost (or rightmost) derivation for `form`."""
    try:
        idx_fn = next if leftmost else lambda it: list(it)[-1]  # pick position
        while any(not is_terminal(s) for s in form):
            # Find the nonterminal to expand
            positions = [i for i, s in enumerate(form) if not is_terminal(s)]
            idx = positions[0] if leftmost else positions[-1]
            sym = form[idx]
            # Use the FIRST production (just to pick one derivation path)
            rhs = grammar[sym][0]
            form = form[:idx] + rhs + form[idx+1:]
            yield list(form)
            if len(form) > 30:   # safety: stop runaway expansions
                yield ["... (truncated)"]
                return
    except Exception as e:
        print(f"[derivation:expand] {e}")
        import traceback; traceback.print_exc()

def show_derivation(start, grammar, label):
    print(f"── {label} derivation from {start} ──")
    form = [start]
    print("  " + " ".join(form))
    for step in expand(form, grammar, leftmost=(label=="Leftmost")):
        print("  " + " ".join(step))
    print()

show_derivation("E", GRAMMAR, "Leftmost")
show_derivation("E", GRAMMAR, "Rightmost")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

### Critical Thinking Questions

10. Both derivations start from `E` and end at the same terminal string. What is that string? (Read the last printed line of each derivation.)
11. Count the number of steps in the leftmost versus rightmost derivation. Are they the same? Explain why the number of steps must always be equal for a given derivation of a given string.
12. The tracer always picks the first production for each nonterminal. Modify the grammar so `F -> ["num"]` is listed *before* `F -> ["(", "E", ")"]` (swap the two entries). Predict how the derivation changes — will it be shorter, longer, or the same length?

---

## Model 5: Ambiguity Detector (Runnable)

An ambiguous grammar lets the same string be derived via two *different* leftmost derivations, which means two different parse trees. The detector below generates all parse trees up to a size bound for a naive expression grammar and reports strings that have more than one tree.

```python
# Model 5: Find two distinct parse trees for a + b + c under an ambiguous grammar
# Grammar: E -> E + E | id
# We represent trees as nested tuples for easy comparison.

AMBIGUOUS = {
    "E": [("E", "+", "E"), ("id",)],
}

def gen_trees(sym, depth=0, max_depth=4):
    """Generate all parse trees for sym as nested tuples."""
    try:
        if sym not in AMBIGUOUS:
            yield sym   # terminal
            return
        if depth > max_depth:
            return
        for rhs in AMBIGUOUS[sym]:
            # Collect all combinations of subtrees for each symbol in rhs
            combos = [list(gen_trees(s, depth+1, max_depth)) for s in rhs]
            # Cartesian product
            from itertools import product as cart_product
            for combo in cart_product(*combos):
                if len(rhs) == 1:
                    yield combo[0]
                else:
                    yield (rhs[1], combo[0], combo[2])   # (op, left, right) shape
    except Exception as e:
        print(f"[ambiguity:gen_trees] {e}")
        import traceback; traceback.print_exc()

def leaves(tree):
    """Collect the leaf terminals in left-to-right order."""
    if not isinstance(tree, tuple):
        return [tree]
    result = []
    for child in tree:
        result.extend(leaves(child))
    return result

def trees_for(target_leaves, sym="E", max_depth=4):
    """Return all distinct trees whose leaves match target_leaves."""
    try:
        seen = set()
        matches = []
        for t in gen_trees(sym, max_depth=max_depth):
            if leaves(t) == target_leaves and t not in seen:
                seen.add(t)
                matches.append(t)
        return matches
    except Exception as e:
        print(f"[ambiguity:trees_for] {e}")
        import traceback; traceback.print_exc()
        return []

target = ["id", "id", "id"]   # represents  a + b + c
found = trees_for(target)

print(f"Trees for 'a + b + c' under E -> E + E | id:")
for i, t in enumerate(found, 1):
    print(f"  Tree {i}: {t}")

if len(found) >= 2:
    print(f"\nGrammar IS ambiguous: found {len(found)} distinct parse trees.")
    print("Tree 1 evaluates left-first  (like (a+b)+c)")
    print("Tree 2 evaluates right-first (like a+(b+c))")
    print("For addition they give the same number, but for subtraction they would not.")
else:
    print("Only one tree found (grammar may be unambiguous for this input).")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

### Critical Thinking Questions

13. The detector finds two trees for `a + b + c`. Write out both trees using nested parentheses notation (e.g., `((a+b)+c)` and `(a+(b+c))`). Which tree does the *left-recursive* grammar `E -> E + T | T` force? Which does the *right-recursive* form force?
14. For *addition*, both trees give the same numeric value. Name a binary operator where `(a OP b) OP c ≠ a OP (b OP c)`, and verify with concrete numbers. This is why ambiguity matters even when the two trees share a root operator.
15. The grammar `E -> E + E | id` is ambiguous; `E -> E + T | T` with `T -> id` is not. Describe in one sentence the structural property of the unambiguous grammar that forces exactly one parse tree.

---

## Model 6: Disambiguating by Convention (Runnable)

The standard cure for expression ambiguity is to stratify the grammar: one nonterminal per precedence level, left recursion on the left for left-associativity. The model below builds parse trees under both the ambiguous and the unambiguous grammar for the same string and shows they differ in shape.

```python
# Model 6: Compare trees from ambiguous vs. unambiguous (layered) grammar

def leaf(v):   return {"op": None, "val": v,  "left": None, "right": None}
def node(op, l, r): return {"op": op, "val": None, "left": l, "right": r}

def pretty(t, indent=0):
    """Indented ASCII art."""
    try:
        pad = "  " * indent
        if t["op"] is None:
            print(f"{pad}{t['val']}")
        else:
            print(f"{pad}({t['op']})")
            pretty(t["left"],  indent + 1)
            pretty(t["right"], indent + 1)
    except Exception as e:
        print(f"[disambig:pretty] {e}")
        import traceback; traceback.print_exc()

def evaluate(t):
    try:
        if t["op"] is None:
            return t["val"]
        l, r = evaluate(t["left"]), evaluate(t["right"])
        if t["op"] == "+": return l + r
        if t["op"] == "-": return l - r
        if t["op"] == "*": return l * r
        if t["op"] == "/": return l / r
    except Exception as e:
        print(f"[disambig:evaluate] {e}")
        import traceback; traceback.print_exc()
        return None

# String: 2 + 3 * 4

# ── Ambiguous grammar: could group either way ──────────────────────────
ambig_tree_A = node("+", leaf(2), node("*", leaf(3), leaf(4)))  # correct
ambig_tree_B = node("*", node("+", leaf(2), leaf(3)), leaf(4))  # also valid under naive grammar

# ── Unambiguous (layered) grammar: only one tree possible ──────────────
# E -> E + T | T    T -> T * F | F    F -> num
unambig_tree = node("+", leaf(2), node("*", leaf(3), leaf(4)))

print("=== Ambiguous grammar, Tree A (+ is root) ===")
pretty(ambig_tree_A)
print(f"Value = {evaluate(ambig_tree_A)}")   # 14

print()
print("=== Ambiguous grammar, Tree B (* is root) ===")
pretty(ambig_tree_B)
print(f"Value = {evaluate(ambig_tree_B)}")   # 20

print()
print("=== Unambiguous (layered) grammar: only Tree A is derivable ===")
pretty(unambig_tree)
print(f"Value = {evaluate(unambig_tree)}")   # 14

print()
# Associativity comparison for 5 - 2 - 1
left_assoc  = node("-", node("-", leaf(5), leaf(2)), leaf(1))
right_assoc = node("-", leaf(5), node("-", leaf(2), leaf(1)))
print(f"Left-assoc  (5-2)-1 = {evaluate(left_assoc)}")   # 2  (correct)
print(f"Right-assoc 5-(2-1) = {evaluate(right_assoc)}")  # 4  (wrong for subtraction)
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

### Critical Thinking Questions

16. In `ambig_tree_B`, the `*` node is the root and `+` is its left child. Under the *layered* grammar `E -> E + T | T`, explain precisely why this tree is *not derivable* — which rule is violated?
17. The unambiguous grammar encodes left-associativity through *left recursion* (`E -> E + T`). If you changed this rule to `E -> T + E`, what would change about associativity? Verify with `5 - 2 - 1`.
18. Look at `left_assoc` versus `right_assoc` for `5 - 2 - 1`. The values are 2 and 4. Now consider a purely additive expression `5 + 2 + 1`. Would left vs. right associativity produce different values? What does this tell you about when associativity "matters"?

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
