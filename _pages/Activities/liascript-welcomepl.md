# Welcome: Why Study Programming Languages?
<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://github.com/BillJr99/Ursinus-CS374-Fall2026/blob/gh-pages/_pages/Activities/liascript-welcomepl.md or locally via https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374-Fall2026/gh-pages/_pages/Activities/liascript-welcomepl.md

import: https://raw.githubusercontent.com/liascript/CodeRunner/master/README.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

# Welcome: Why Study Programming Languages?

By December, your team will have built a programming language of your own: a lexer, a parser, and an interpreter, assembled from components you write one assignment at a time. Today we ask why that journey is worth taking. We move from **what a language is $\rightarrow$ why languages differ $\rightarrow$ the pipeline from text to behavior $\rightarrow$ how this course works**.

---

## Directions and Group Roles

Throughout this course, we work in POGIL-style teams of three or four with rotating roles:

- **Manager**: keeps the team on task and watches the time.
- **Recorder**: writes the team's answers on the Class Activity Questions discussion board.
- **Presenter**: reports the team's findings to the class.
- **Reflector**: notes what helped or hindered the team, and shares one observation at the end.

Consider each model below and answer the questions provided. First reflect on the questions on your own briefly, before discussing and comparing your thoughts with your group. Report out on areas of disagreement or items for which your group identified alternative approaches. After class, respond to the reflective prompt individually in your notebook.

---

## 1. Languages All the Way Down

**A programming language is a precise notation for computation.** It is an agreement among three parties: the human who writes, the machine that executes, and, most often forgotten, the *other humans who read*. Every language is a set of design decisions about syntax (what programs look like), semantics (what programs mean), and pragmatics (what programs are easy or hard to express).

**You already speak several.** Python, probably Java or C, perhaps SQL or regular expressions; each made different choices. Studying *principles* of programming languages means learning the design space itself, so that the next language you meet (or invent) is a configuration of familiar choices rather than a new world.

**Three payoffs.** First, you become a better programmer in every language, because you see through syntax to the semantics beneath. Second, you become able to *build* languages: configuration formats, query languages, and domain-specific notations are everyday engineering artifacts. Third, you join an intellectual tradition connecting logic, linguistics, and computing, from the lambda calculus of the 1930s to the languages being designed this year.

---

## Model 1: One Idea, Four Notations

The same computation — summing the squares of the even numbers in a list — in four notations:

**Python (imperative/functional blend):**
```python
nums = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
total = sum(x*x for x in nums if x % 2 == 0)
print(total)  # 220
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

**Python OO style:**
```python
nums = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

class VowelCounter:  # reusing class structure for illustration
    def __init__(self, data): self.data = data
    def sum_even_squares(self):
        return sum(x*x for x in self.data if x % 2 == 0)

vc = VowelCounter(nums)
print(vc.sum_even_squares())  # 220
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

**Scheme-style functional (Python simulation):**
```python
from functools import reduce

nums = list(range(1, 11))
even = list(filter(lambda x: x % 2 == 0, nums))
squared = list(map(lambda x: x * x, even))
total = reduce(lambda a, b: a + b, squared, 0)
print(total)  # 220
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

**All four approaches — same answer, different mental models:**
```python
nums = list(range(1, 11))

# Imperative: explicit state
total_imp = 0
for x in nums:
    if x % 2 == 0:
        total_imp += x * x

# Functional: composition
from functools import reduce
total_func = reduce(lambda a,b: a+b, map(lambda x: x*x, filter(lambda x: x%2==0, nums)), 0)

# Comprehension: declarative
total_comp = sum(x*x for x in nums if x % 2 == 0)

print(f"Imperative: {total_imp}")
print(f"Functional: {total_func}")
print(f"Comprehension: {total_comp}")
print(f"All equal? {total_imp == total_func == total_comp}")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

### Critical Thinking Questions

1. For each version, identify what the *programmer* must keep track of (loop counters, intermediate state, nothing?). Which version says *what* to compute and which says *how*?
2. Rank the four for readability by a newcomer, and separately for your own confidence that each is correct. Did the rankings differ? Why might they?
3. The Scheme-style version is built from three reusable pieces (`filter`, `map`, `reduce`). Identify the analogous pieces hiding inside the Python comprehension.
4. Propose one computation that would be awkward to express declaratively but easy imperatively. What does that suggest about general-purpose versus domain-specific languages?

---

## 2. From Text to Behavior: The Pipeline

**Every implementation answers the same question: how does this string of characters become behavior?** The classical pipeline, which is also the skeleton of this course and of your project, proceeds in stages:

$$
\text{characters} \xrightarrow{\text{lexer}} \text{tokens} \xrightarrow{\text{parser}} \text{syntax tree} \xrightarrow{\text{interpreter}} \text{value}
$$

The **lexer** (scanner) groups characters into meaningful units called tokens, using the machinery of regular expressions and finite automata. The **parser** assembles tokens into a tree according to a grammar. The **interpreter** walks the tree, computing values within environments that give names their meanings. A **compiler** shares the front half and differs at the back, emitting code instead of computing values; we focus on interpretation, and the principles transfer.

[[MC]]
In the pipeline above, the component whose job is to decide that the characters `c`, `o`, `u`, `n`, `t` form a single identifier token is:
- (x) The lexer
- ( ) The parser
- ( ) The interpreter
- ( ) The operating system

---

## Model 2: Be the Pipeline

Consider the source text: `total = 3 + price * 2`

**A minimal Python tokenizer — watch the pipeline live:**
```python
import re

source = "total = 3 + price * 2"

# A simple token spec: (type, pattern)
TOKEN_SPEC = [
    ("NUMBER",  r"\d+(\.\d*)?"),
    ("IDENT",   r"[A-Za-z_]\w*"),
    ("ASSIGN",  r"="),
    ("PLUS",    r"\+"),
    ("STAR",    r"\*"),
    ("WS",      r"\s+"),
]

master = "|".join(f"(?P<{name}>{pat})" for name, pat in TOKEN_SPEC)
tokens = []
for m in re.finditer(master, source):
    kind = m.lastgroup
    if kind != "WS":
        tokens.append((kind, m.group()))

for tok in tokens:
    print(tok)
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

### Critical Thinking Questions

5. As a team, list the tokens the lexer produced. How many are there? Did anyone's count differ?
6. The interpreter must compute `price * 2` before adding 3. Where in the pipeline is that ordering decided: the lexer, the parser, or the interpreter? Defend your answer.
7. Suppose the text were `total = 3 + * 2`. At which stage should the error be caught, and what should a *helpful* error message say?

---

## Model 3: Python's Own Pipeline

Python itself uses the same pipeline. You can inspect every stage:

```python
import ast, dis, tokenize, io

source = "total = 3 + 2 * 5"

# Stage 1: Tokens
print("=== TOKENS ===")
tokens = list(tokenize.generate_tokens(io.StringIO(source).readline))
for tok in tokens:
    if tok.type not in (tokenize.NL, tokenize.NEWLINE, tokenize.ENDMARKER):
        print(f"  {tokenize.tok_name[tok.type]:10} {tok.string!r}")

# Stage 2: AST
print("\n=== AST ===")
tree = ast.parse(source)
print(ast.dump(tree, indent=2))

# Stage 3: Bytecode (compiled)
print("\n=== BYTECODE ===")
code = compile(source, "<string>", "exec")
dis.dis(code)
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

### Critical Thinking Questions

8. How many tokens does Python produce for `total = 3 + 2 * 5`? Which token is the operator precedence information *not* encoded in (it appears in the AST instead)?
9. The AST shows a `BinOp` with `Mult` nested inside `Add`. How does the tree *encode* precedence without any explicit precedence rules?
10. The bytecode shows `BINARY_OP` instructions. These are the *output* of Python's compiler. What is the input to an interpreter, by contrast?

---

## 3. How This Course Works

The first half of the semester builds your skills bottom-up through scaffolded individual assignments: regular expressions, automata, a lexer, a parser, an interpreter. In the second half, your team **snaps those components together** into a language of your own design, developed in sprints with rotating roles, a gallery walk peer review, and a public Demo Day. Along the way we study languages as artifacts (Scheme, the lambda calculus, modern features) so your design choices are informed by sixty years of others' choices.

---

## 4. Exercises

1. *Language autobiography.* List every programming language and notation (count spreadsheets and regex!) you have used. For each, one sentence: what was it good at?
2. *Notation hunt.* Find one notation in daily life that has a syntax and a semantics but is not usually called a programming language (music notation, knitting patterns, chess notation). The Presenter shares the team's best example.
3. *Tokenizer extension.* Extend the minimal tokenizer above to also recognize `(`, `)`, `-`, `/`, and floating-point numbers like `3.14`. Test it on `result = (a - 3.14) / b`. How many tokens does it produce?
4. *Pipeline trace.* Manually trace the three stages of the pipeline for the expression `2 * (x + 1)`: list tokens, draw the parse tree, and show the evaluation order.
5. *Team charter.* Draft your team's working agreement: role rotation, communication, preparation norms, and disagreement resolution. The Recorder posts it.

---

## Reflection Prompt

In your notebook: describe one moment when a programming language fought you — when the thing you wanted to say was hard to express. Knowing you will design a language this semester, what would you change to make that moment easier? And after seeing Python's own tokens/AST/bytecode pipeline, does Python feel more or less like magic to you?

---

## 5. Further Reading

- Douglas Thain. *Introduction to Compilers and Language Design* (2nd ed.), Chapter 1. Our pipeline, named and framed.
- Shriram Krishnamurthi. *Programming Languages: Application and Interpretation* (online). The interpreter-first philosophy we follow.
- Robert Nystrom. *Crafting Interpreters* (online), "A Map of the Territory."
- The `ast` module docs: `help(ast)` in Python shows every node type you'll encounter.
