<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374-Fall2026/gh-pages/_pages/Tutorials/tutorial-grammars-in-python.md

import: https://raw.githubusercontent.com/liascript/CodeRunner/master/README.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

# Grammar Tooling in Python

Companion to the *Grammars and the Chomsky Hierarchy* and *Derivations, Parse Trees, Ambiguity, and Precedence* activities.

Those two class sessions are about reasoning: what a grammar *is*, why an ambiguous one admits two trees, and how layering nonterminals encodes precedence.  You do that reasoning with a pencil, in your team, on paper.

This page is the other half: the runnable versions.  Every model below was originally embedded in one of those sessions, and each one is a small Python program you execute rather than discuss: representing a grammar as a dictionary, detecting left recursion mechanically, generating derivations, and comparing the trees an ambiguous grammar produces against the trees a layered one produces.

**Run these at your own pace, after the session that introduces the idea.**  They are not required unless an assignment says so, but two of them are useful scaffolding: the left-recursion detector tells you whether a grammar you wrote can be parsed by recursive descent, and the ambiguity comparison is the fastest way to check your own grammar design before you build a parser on top of it.

## Model 3: Python CFG Representation (Runnable)

A grammar can be represented as a Python `dict` mapping each nonterminal to a list of right-hand sides (each RHS is itself a list of symbols).  The breadth-first derivation checker below tests membership for short strings.  Run it and observe which strings are in the language.

The grammar being checked encodes **operator precedence** directly through structure:

```
E -> E + T | T       (+ is low precedence, handled at the top level)
T -> T * F | F       (* is higher precedence, handled one level deeper)
F -> 0 | 1 | ... | 9 (digits are leaves)
```

A worked derivation of `2+3*4`:

```
E
  => E + T           (E -> E + T)
  => T + T           (E -> T, leftmost E)
  => F + T           (T -> F)
  => 2 + T           (F -> 2)
  => 2 + T * F       (T -> T * F)
  => 2 + F * F       (T -> F)
  => 2 + 3 * F       (F -> 3)
  => 2 + 3 * 4       (F -> 4)
```

The `*` sub-expression is deeper in the derivation (and in the tree), which means it is evaluated first; that is **how layered grammars encode precedence**.

```python
# Model 3: CFG as a Python dict + membership checker
# Grammar: arithmetic over single-digit numbers with + and *
# E -> E + T | T
# T -> T * F | F
# F -> num
# (we use right-recursive stand-ins so BFS stays finite)

GRAMMAR = {
    "E": [["E", "+", "T"], ["T"]],
    "T": [["T", "*", "F"], ["F"]],
    "F": [["0"], ["1"], ["2"], ["3"], ["4"],
          ["5"], ["6"], ["7"], ["8"], ["9"]],
}

def derivable(target, grammar, start="E", max_steps=20):
    """BFS over sentential forms; returns True if target is reachable."""
    try:
        nonterminals = set(grammar.keys())
        frontier = [tuple([start])]
        visited = {tuple([start])}
        for _ in range(max_steps):
            next_frontier = []
            for form in frontier:
                # all-terminal: check
                if all(sym not in nonterminals for sym in form):
                    if "".join(form) == target:
                        return True
                    continue
                # expand the FIRST nonterminal (leftmost derivation)
                idx = next(i for i, s in enumerate(form) if s in nonterminals)
                for rhs in grammar[form[idx]]:
                    candidate = form[:idx] + tuple(rhs) + form[idx+1:]
                    # prune: terminal prefix must match target prefix
                    term_prefix = "".join(
                        s for s in candidate if s not in nonterminals)
                    if not target.startswith(term_prefix[:len(term_prefix)]):
                        continue
                    if candidate not in visited and len(candidate) <= len(target) * 2:
                        visited.add(candidate)
                        next_frontier.append(candidate)
            frontier = next_frontier
        return False
    except Exception as e:
        print(f"[cfgcheck:derivable] {e}")
        import traceback; traceback.print_exc()
        return False

tests = ["2+3", "2*3", "1+2*3", "2++3", "2+", "+2", "9*8*7"]
for s in tests:
    print(f"  {s!r:12} in L(G)? {derivable(s, GRAMMAR)}")
```
@LIA.eval(`["main.py"]`, `none`, `python3 main.py`)

### Critical Thinking Questions

> **CTQ 3.11** `1+2*3` is accepted and `2++3` is rejected.
>
> - **Step 1:** Write the first three sentential forms that BFS explores for `1+2*3` starting from `E` (leftmost derivation).  Which production fires first?
> - **Step 2:** At what point does the derivation "commit" to the `*` being inside the `T` subtree rather than the `E` subtree?
> - **Step 3:** For `2++3`: after one or two expansion steps, identify the sentential form that can never be completed into `2++3`.  Explain why.

> **CTQ 3.12** This grammar is left-recursive (`E -> E + T`).  The BFS still terminates because of the length bound `len(candidate) <= len(target) * 2`.
>
> - **Step 1:** Simulate what a top-down recursive descent parser does when it calls `parseE()` and the current grammar rule is `E -> E + T`.  Write out the call sequence.
> - **Step 2:** Why does that sequence never terminate?
> - **Step 3:** BFS avoids infinite loops using the `visited` set and the length bound.  Explain which of those two mechanisms prevents the loop that recursive descent falls into.

> **CTQ 3.13** Add a rule `F -> "(" E ")"` (using the symbols `(` and `)`) and add `"(2+3)"` to the test list.
>
> - **Step 1:** Write the modified `GRAMMAR` dict entry for `F`.
> - **Step 2:** Before running, predict whether `(2+3)` will be accepted.  Trace the derivation by hand.
> - **Step 3:** Now predict `(2+3)*4`.  What does the grammar say about the precedence of parenthesized sub-expressions vs. `*`?

---

## Model 4: Left Recursion Detection (Runnable)

Before converting a grammar to recursive descent we need to know which nonterminals are directly left-recursive.  A nonterminal $A$ is directly left-recursive if it has a production $A \rightarrow A\,\alpha$ for some $\alpha$.

**Worked example, left-recursion elimination:**

The standard left-recursive rule `E -> E + T | T` and its right-recursive equivalent `E -> T E'` with `E' -> + T E' | ε` express the *same language* but have very different parser behavior.  Here is why they are equivalent:

```
Left-recursive generates:   T,  T+T,  T+T+T,  T+T+T+T, ...
Right-recursive generates:
  E  => T E'
     => T + T E'          (E' -> + T E')
     => T + T + T E'      (E' -> + T E' again)
     => T + T + T         (E' -> epsilon)
```

Same strings, same left-to-right order, but the right-recursive version never calls itself as its very first action, so recursive descent can handle it.

```python
# Model 4: Detecting direct left recursion in a grammar dict

def find_left_recursive(grammar):
    """Return the set of nonterminals that are directly left-recursive."""
    try:
        left_recursive = set()
        for head, productions in grammar.items():
            for rhs in productions:
                if rhs and rhs[0] == head:
                    left_recursive.add(head)
        return left_recursive
    except Exception as e:
        print(f"[lrdetect:find_left_recursive] {e}")
        import traceback; traceback.print_exc()
        return set()

def report(name, grammar):
    lr = find_left_recursive(grammar)
    if lr:
        print(f"{name}: LEFT-RECURSIVE nonterminals = {sorted(lr)}")
    else:
        print(f"{name}: no direct left recursion found")

# Left-recursive arithmetic grammar (standard textbook form)
grammar_lr = {
    "E": [["E", "+", "T"], ["T"]],
    "T": [["T", "*", "F"], ["F"]],
    "F": [["num"]],
}

# Right-recursive rewrite (suitable for recursive descent)
grammar_rr = {
    "E":  [["T", "E'"]],
    "E'": [["+", "T", "E'"], []],   # empty list = epsilon
    "T":  [["F", "T'"]],
    "T'": [["*", "F", "T'"], []],
    "F":  [["num"]],
}

# Balanced-parens grammar (no left recursion)
grammar_bp = {
    "S": [["(", "S", "S", ")"], []],
}

report("Left-recursive arithmetic", grammar_lr)
report("Right-recursive (LL) arithmetic", grammar_rr)
report("Balanced parentheses", grammar_bp)
```
@LIA.eval(`["main.py"]`, `none`, `python3 main.py`)

### Critical Thinking Questions

> **CTQ 4.14** `grammar_rr` introduces `E'` and `T'` (read "E-prime").  These are the standard *left-recursion elimination* trick.
>
> - **Step 1:** Using `grammar_rr`, derive `3+5+7` step by step.  Write every sentential form.
> - **Step 2:** At each step, write which production rule you used (e.g., `E -> T E'`).
> - **Step 3:** In one sentence, explain what `E' -> + T E' | ε` accomplishes compared to `E -> E + T | T`.  Focus on where the recursion sits (first position vs. last position).

> **CTQ 4.15** The detector only finds *direct* left recursion (A -> A...).  Indirect left recursion would require A -> B... and B -> A....
>
> - **Step 1:** Write a small example grammar with indirect left recursion between two nonterminals `A` and `B`.  Show the two production rules that create the cycle.
> - **Step 2:** Trace what a recursive descent parser does when it tries to parse a string under your indirect grammar.  Where does the infinite loop occur?
> - **Step 3:** Sketch in English (no code required) how you would extend `find_left_recursive` to detect one step of indirect left recursion.

> **CTQ 4.16** Why does a recursive descent parser loop forever on `grammar_lr` but successfully parse on `grammar_rr`?
>
> - **Step 1:** For `grammar_lr`, write the first three calls on the call stack when parsing the token `3` from the string `3 + 5`.
> - **Step 2:** For `grammar_rr`, write the first three calls on the call stack for the same input.  Where does the stack stop growing?
> - **Step 3:** State the general rule: a recursive descent parser can handle a grammar if and only if ... (complete the sentence in terms of left recursion).

---

## Model 5: Parse Trees as Python Dicts (Runnable)

A parse tree is a nested dictionary `{"node": label, "children": [...]}`.  Building one by hand for `2 + 3 * 4` under the layered grammar and pretty-printing it shows directly that the `*` subtree is nested *inside* the `+` subtree, operator precedence made structurally explicit.

**Parse tree for `2 + 3 * 4` under the layered grammar (the CORRECT interpretation):**

```
        E
       / \
      E   T
      |  /|\
      T T * F
      | |   |
      F F   4
      | |
      2 3
```

This tree computes `3 * 4` first (it is deeper), then adds `2`.  Result: 14.

**The WRONG tree the naive flat grammar would also permit:**

```
        E
       /|\
      E * E
     /|\   \
    E + E   E
    |   |   |
    2   3   4
```

This tree computes `2 + 3` first, then multiplies by `4`.  Result: 20.  Same string, different structure, different value; this is the harm of an ambiguous grammar.

**Two different parse trees prove ambiguity.**  A grammar is **ambiguous** if any string in its language has two or more distinct parse trees.  Ambiguity is not just an aesthetic problem: it means the grammar gives two different computation orders for the same expression.  Every parser you write must work from an *unambiguous* grammar; the layered `E/T/F` structure is the standard fix.

```python
# Model 5: Parse trees as nested dicts + pretty printer

def leaf(val):
    return {"node": str(val), "children": []}

def tree(label, *children):
    return {"node": label, "children": list(children)}

def pretty(t, indent=0):
    """Indented ASCII art of the parse tree."""
    try:
        prefix = "  " * indent
        print(f"{prefix}{t['node']}")
        for child in t["children"]:
            pretty(child, indent + 1)
    except Exception as e:
        print(f"[parsetree:pretty] {e}")
        import traceback; traceback.print_exc()

def evaluate(t):
    """Evaluate the tree bottom-up."""
    try:
        if not t["children"]:
            return float(t["node"])
        op = t["node"]
        vals = [evaluate(c) for c in t["children"]]
        if op == "+": return vals[0] + vals[1]
        if op == "*": return vals[0] * vals[1]
        if op == "-": return vals[0] - vals[1]
        if op == "/": return vals[0] / vals[1]
    except Exception as e:
        print(f"[parsetree:evaluate] {e}")
        import traceback; traceback.print_exc()
        return None

# Parse tree for  2 + 3 * 4  under the LAYERED grammar (only one tree)
#        E
#       /|\
#      E + T
#      |  /|\
#      T T * F
#      | |   |
#      F F   4
#      | |
#      2 3
correct_tree = tree("+",
                    leaf(2),
                    tree("*", leaf(3), leaf(4)))

# The WRONG tree the naive grammar also permits
wrong_tree = tree("*",
                  tree("+", leaf(2), leaf(3)),
                  leaf(4))

print("=== Correct parse tree for 2 + 3 * 4 ===")
pretty(correct_tree)
print(f"Value: {evaluate(correct_tree)}")   # 14

print()
print("=== Naive grammar's alternate tree (WRONG) ===")
pretty(wrong_tree)
print(f"Value: {evaluate(wrong_tree)}")     # 20

print()
# Associativity: 7 - 2 - 1  left-associative
left_tree  = tree("-", tree("-", leaf(7), leaf(2)), leaf(1))
right_tree = tree("-", leaf(7), tree("-", leaf(2), leaf(1)))
print(f"Left-assoc  (7-2)-1 = {evaluate(left_tree)}")   # 2
print(f"Right-assoc 7-(2-1) = {evaluate(right_tree)}")  # 6
```
@LIA.eval(`["main.py"]`, `none`, `python3 main.py`)

### Critical Thinking Questions

> **CTQ 5.17** In `correct_tree`, the `*` node is a *child* of `+`.  In `wrong_tree`, `+` is a child of `*`.
>
> - **Step 1:** Trace `evaluate(correct_tree)` by hand, starting from the leaves.  Write each sub-call and its return value.
> - **Step 2:** Now trace `evaluate(wrong_tree)` the same way.  Where does the computation diverge?
> - **Step 3:** Explain in one sentence why "deeper in the tree" corresponds to "tighter binding" when the interpreter evaluates children before parents.

> **CTQ 5.18** The pretty-printer uses indentation level to show depth.
>
> - **Step 1:** Before running the code, sketch (on paper) what the indented output for `correct_tree` will look like.  Label each line with its depth.
> - **Step 2:** Run the code and compare.  Does the deepest indented line correspond to the highest-precedence operation?
> - **Step 3:** For the associativity example at the bottom: draw the two trees for `7-2-1` (left-assoc and right-assoc) using the same ASCII style shown in the model explanation above.

> **CTQ 5.19** Extend the `tree` / `leaf` / `evaluate` code (mentally or on paper) to handle `(2 + 3) * 4`.
>
> - **Step 1:** Which node becomes the root?
> - **Step 2:** How does the tree's shape change compared to `2 + 3 * 4`?
> - **Step 3:** What is the value, and which sub-expression is evaluated first?  Connect this back to how parentheses override the grammar's default precedence levels.

---

# From the Derivations and Ambiguity Activity: Runnable Models

The three models below were previously embedded in the *Derivations, Parse Trees, Ambiguity, and Precedence* class session.  The session itself is pencil work: drawing two trees for one string, writing derivations by hand.  These are the mechanical versions: a derivation tracer, an ambiguity detector, and a side-by-side comparison of the trees an ambiguous grammar produces against the trees a layered one produces.

## Model 4: Derivation Tracer (Runnable)

*Intuition: A leftmost derivation and a rightmost derivation of the same string take different paths through the grammar, but they always arrive at the same parse tree.  Running the tracer below lets you watch both paths step by step and confirm they converge.  Pay attention to how many steps each takes; it turns out they must be equal, and understanding why solidifies your mental model of what a derivation actually is.*

A leftmost derivation always expands the leftmost nonterminal at each step; a rightmost derivation always expands the rightmost one.  Watching them side by side makes it concrete that **both derivations produce the same parse tree** even though the step sequences differ.

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
    print(f"-- {label} derivation from {start} --")
    form = [start]
    print("  " + " ".join(form))
    for step in expand(form, grammar, leftmost=(label=="Leftmost")):
        print("  " + " ".join(step))
    print()

show_derivation("E", GRAMMAR, "Leftmost")
show_derivation("E", GRAMMAR, "Rightmost")
```
@LIA.eval(`["main.py"]`, `none`, `python3 main.py`)

### Critical Thinking Questions

8.  Both derivations start from `E` and end at the same terminal string.  What is that string?  (Read the last printed line of each derivation.)
9.  Count the number of steps in the leftmost versus rightmost derivation.  Are they the same?  Explain why the number of steps must always be equal for a given derivation of a given string.
10.  The tracer always picks the first production for each nonterminal.  Modify the grammar so `F -> ["num"]` is listed *before* `F -> ["(", "E", ")"]` (swap the two entries).  Predict how the derivation changes; will it be shorter, longer, or the same length?

---

## Model 5: Ambiguity Detector (Runnable)

*Intuition: To prove a grammar is ambiguous, you only need one witness: a single string that has two distinct parse trees.  The code below systematically generates all parse trees up to a depth limit for the naive grammar `E -> E + E | id` and checks whether any string gets more than one.  For `a + b + c` it finds two, which is the formal proof that the grammar is ambiguous.*

An ambiguous grammar lets the same string be derived via two *different* leftmost derivations, which means two different parse trees.  The detector below generates all parse trees up to a size bound for a naive expression grammar and reports strings that have more than one tree.

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
@LIA.eval(`["main.py"]`, `none`, `python3 main.py`)

### Critical Thinking Questions

11.  The detector finds two trees for `a + b + c`.  Write out both trees using nested parentheses notation (e.g., `((a+b)+c)` and `(a+(b+c))`).  Which tree does the *left-recursive* grammar `E -> E + T | T` force?  Which does the *right-recursive* form force?
12.  For *addition*, both trees give the same numeric value.  Name a binary operator where `(a OP b) OP c ≠ a OP (b OP c)`, and verify with concrete numbers.  This is why ambiguity matters even when the two trees share a root operator.
13.  The grammar `E -> E + E | id` is ambiguous; `E -> E + T | T` with `T -> id` is not.  Describe in one sentence the structural property of the unambiguous grammar that forces exactly one parse tree.

---

## Model 6: Disambiguating by Convention (Runnable)

*Intuition: This model puts the two grammars side by side in runnable code so you can see the concrete difference.  The ambiguous grammar allows two distinct tree shapes for `2 + 3 * 4`; the layered grammar produces only one.  Tracing the printed tree shapes will make the structural difference between "precedence encoded in grammar" and "precedence enforced externally" tangible.*

The standard cure for expression ambiguity is to stratify the grammar: one nonterminal per precedence level, left recursion on the left for left-associativity.  The model below builds parse trees under both the ambiguous and the unambiguous grammar for the same string and shows they differ in shape.

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

# -- Ambiguous grammar: could group either way --------------------------
ambig_tree_A = node("+", leaf(2), node("*", leaf(3), leaf(4)))  # correct
ambig_tree_B = node("*", node("+", leaf(2), leaf(3)), leaf(4))  # also valid under naive grammar

# -- Unambiguous (layered) grammar: only one tree possible --------------
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
@LIA.eval(`["main.py"]`, `none`, `python3 main.py`)

### Critical Thinking Questions

14.  In `ambig_tree_B`, the `*` node is the root and `+` is its left child.  Under the *layered* grammar `E -> E + T | T`, explain precisely why this tree is *not derivable*; which rule is violated?
15.  The unambiguous grammar encodes left-associativity through *left recursion* (`E -> E + T`).  If you changed this rule to `E -> T + E`, what would change about associativity?  Verify with `5 - 2 - 1`.
16.  Look at `left_assoc` versus `right_assoc` for `5 - 2 - 1`.  The values are 2 and 4.  Now consider a purely additive expression `5 + 2 + 1`.  Would left vs. right associativity produce different values?  What does this tell you about when associativity "matters"?

---

## Model 4: Grammar as a Python Data Structure

A grammar written on paper and a grammar stored as a Python dictionary are the same thing; the dictionary just makes the structure explicit enough to run.  This model shows how the recursive structure of a grammar translates directly into mutually recursive functions, one per nonterminal.  Notice especially how left recursion is avoided: instead of `expr -> expr "+" term`, the grammar uses a separate `expr_rest` rule.

> **Watch out!**  **Left recursion** (a rule of the form `A -> A ...`) causes an infinite loop in top-down (recursive descent) parsers because the parser calls itself immediately without consuming any input.  The standard fix is to rewrite the rule using a right-recursive helper or an explicit `_rest` nonterminal, as this grammar does.

A grammar is just data: a mapping from nonterminal names to lists of alternatives, where each alternative is a list of symbols.  Terminals are plain strings; nonterminals are wrapped to distinguish them.  The checker below walks a token sequence against an arithmetic-expression grammar and reports whether it is valid.

The grammar for arithmetic expressions:

```
expr   -> term { ("+" | "-") term }
term   -> factor { ("*" | "/") factor }
factor -> NUMBER | "(" expr ")"
```

```python
# Grammar as a Python dict: each key is a nonterminal, each value is
# a list of alternatives. Each alternative is a list of symbols.
# "t:X" means terminal X; "n:X" means nonterminal X.

GRAMMAR = {
    "expr":   [["n:term", "n:expr_rest"]],
    "expr_rest": [["t:+", "n:term", "n:expr_rest"],
                  ["t:-", "n:term", "n:expr_rest"],
                  []],                          # epsilon (empty)
    "term":   [["n:factor", "n:term_rest"]],
    "term_rest": [["t:*", "n:factor", "n:term_rest"],
                  ["t:/", "n:factor", "n:term_rest"],
                  []],
    "factor": [["t:NUM"], ["t:(", "n:expr", "t:)"]],
}

def parse(tokens, rule, pos):
    """Try to match 'rule' starting at tokens[pos].
    Returns (success, new_pos). Tries each alternative in order."""
    if rule not in GRAMMAR:
        return False, pos
    for alt in GRAMMAR[rule]:
        ok, npos = match_alt(tokens, alt, pos)
        if ok:
            return True, npos
    return False, pos

def match_alt(tokens, alt, pos):
    cur = pos
    for sym in alt:
        if sym.startswith("t:"):
            term = sym[2:]
            if cur >= len(tokens) or tokens[cur] != term:
                return False, pos   # backtrack to original pos
            cur += 1
        elif sym.startswith("n:"):
            ok, cur = parse(tokens, sym[2:], cur)
            if not ok:
                return False, pos
    return True, cur

def check(tokens):
    ok, end = parse(tokens, "expr", 0)
    return ok and end == len(tokens)

test_cases = [
    (["NUM", "+", "NUM"],                   True,  "a + b"),
    (["NUM", "*", "NUM", "+", "NUM"],       True,  "a*b + c"),
    (["(", "NUM", "+", "NUM", ")"],         True,  "(a + b)"),
    (["NUM", "+"],                          False, "a + (missing rhs)"),
    (["*", "NUM"],                          False, "* a (no lhs)"),
    (["NUM", "NUM"],                        False, "a b (no operator)"),
    (["NUM", "+", "NUM", "*", "NUM"],       True,  "a + b*c"),
]

print(f"{'tokens':<35} {'expect':>6}  {'got':>6}  {'pass':>4}")
print("-" * 58)
for tokens, expected, label in test_cases:
    result = check(tokens)
    status = "OK" if result == expected else "FAIL"
    print(f"{label:<35} {str(expected):>6}  {str(result):>6}  {status:>4}")
```
@LIA.eval(`["main.py"]`, `none`, `python3 main.py`)

### Critical Thinking Questions

10.  The grammar stores `expr_rest` and `term_rest` as separate rules to encode left-associative repetition without left recursion.  Why is left recursion (`expr -> expr "+" term`) a problem for a top-down recognizer like this one?  Describe the infinite loop that would occur.
11. `match_alt` returns `(False, pos)` (the *original* position) on failure, not the furthest position reached.  Why does restoring the original position matter when there are multiple alternatives?
12.  The grammar currently uses token strings like `"NUM"`, `"+"`, `"*"`.  Sketch how you would extend this representation to carry actual lexemes (e.g., distinguish integer literal `3` from float `3.14`) without rewriting the entire matching engine.
13.  The checker only returns True/False.  What would a *parse tree* version return instead, and what would one node of that tree look like as a Python value?

---

---
**In-class work stops here.**  Everything below is homework and going-deeper material: attempt the exercises before the related assignment.

