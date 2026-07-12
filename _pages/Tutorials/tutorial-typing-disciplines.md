---
layout: tutorial
permalink: /Tutorials/TypingDisciplines
title: "CS374: Typing Disciplines — Strong vs. Weak, Static vs. Dynamic, and Gradual Typing"

info:
  coursenum: CS374
  goals:
    - To distinguish the static/dynamic axis (when types are checked) from the strong/weak axis (how strictly types are enforced)
    - To place real languages in the strong/weak by static/dynamic quadrant with concrete examples
    - To explain gradual typing and why mypy and TypeScript are unsound by design
    - To connect these disciplines to your interpreter's dynamic typing and the Hindley-Milner type-checking direction

readings:
  - rtitle: "mypy Documentation"
    rlink: "https://mypy.readthedocs.io/"
  - rtitle: "TypeScript Playground (try the examples live)"
    rlink: "https://www.typescriptlang.org/play"
  - rtitle: "Siek and Taha, Gradual Typing for Functional Languages (the founding paper)"
    rlink: "https://scholar.google.com/scholar?q=Gradual+Typing+for+Functional+Languages+Siek+Taha"

tags:
  - types
  - static-typing
  - dynamic-typing
  - gradual-typing
  - languages
---

# Typing Disciplines: Strong vs. Weak, Static vs. Dynamic, and Gradual Typing

This is the core companion for the **Type Systems** unit. It pins down two axes that are constantly confused, places real languages on them, and then looks at **gradual typing** — the discipline behind mypy and TypeScript that lets a single program be part-checked and part-unchecked. It connects directly to the two type stories in your own pipeline: the **dynamic** typing your Interpreter enforces at runtime, and the **static** Hindley-Milner checker offered as a direction of that assignment.

---

## Section 1: Two independent axes

People say "strongly typed" to mean many things. Untangle it into two *independent* questions:

- **Static vs. dynamic — *when* are types checked?**
  - **Static:** before the program runs, by a type checker (C, Java, Haskell, Rust, TypeScript).
  - **Dynamic:** as the program runs, when an operation is attempted (Python, Ruby, JavaScript, your CS374 interpreter).
- **Strong vs. weak — *how strictly* are type rules enforced (how much implicit coercion / reinterpretation of bits is allowed)?**
  - **Strong:** the language refuses nonsensical operations rather than silently coercing (Python raises on `"a" + 1`; Haskell won't compile it).
  - **Weak:** the language silently coerces or reinterprets values (C lets you cast a pointer to an int; JavaScript makes `"a" + 1` the string `"a1"` and `[] + {}` a string).

These axes are independent — a language picks a point on *each*.

---

## Section 2: The quadrant

|                | **Static** (checked before running) | **Dynamic** (checked while running) |
|----------------|--------------------------------------|--------------------------------------|
| **Strong** (little/no silent coercion) | Haskell, Rust, Java (mostly), OCaml | **Python**, Ruby, Scheme, **your CS374 interpreter** |
| **Weak** (silent coercion / bit reinterpretation) | C, C++ (implicit conversions, casts) | JavaScript, PHP, Perl |

Worked contrasts to try:

- `"a" + 1`
  - **Python** (strong/dynamic): `TypeError` at runtime.
  - **Haskell** (strong/static): compile error.
  - **JavaScript** (weak/dynamic): `"a1"` — silent coercion.
  - **C** (weak/static): `'a' + 1` is `98` — a `char` is just a small int.
- Your **CS374 interpreter** deliberately sits in the *strong/dynamic* box: `SEMANTICS.md` says adding a string to a number raises a `LangTypeError` at evaluation time. That is a design choice, and stating it precisely is part of the Interpreter assignment.

> **Common misconception:** "static" does not imply "strong," and "dynamic" does not imply "weak." C is static but weak; Python is dynamic but strong. Keep the axes separate.

---

## Section 3: Where your pipeline lives

You have built (or will build) *both* type stories:

- The **tree-walking interpreter** enforces types **dynamically and strongly** — `"a" + 1` gets as far as evaluation and then raises a positioned `LangTypeError`. The rule lives in `SEMANTICS.md`.
- The **Hindley-Milner type-checking direction** moves the *same* language to **static** checking — it rejects `"a" + 1` *before evaluation ever begins*, the way Haskell and OCaml do, and documents each rule in `TYPES.md`. Notice this direction is also *stricter* than the dynamic version in places (it requires `if`/`while` conditions to be `Bool`, not merely truthy).

Choosing the type-checking direction is literally moving your language one column left in the quadrant.

---

## Section 4: Gradual typing — mypy and TypeScript

What if you want *both* — dynamic flexibility during prototyping and static guarantees where it matters? **Gradual typing** (Siek and Taha, 2006) lets you annotate *some* parts of a program with static types and leave others dynamic, inserting runtime checks at the boundary between the two.

- **mypy** adds gradual static typing to Python. Unannotated code is treated as the dynamic type `Any` and passes silently; annotated code is checked.
- **TypeScript** does the same for JavaScript.

Try the same buggy snippet under both (this is the in-class compare):

```python
# Python + mypy
def add(x: int, y: int) -> int:
    return x + y

add("a", 3)     # mypy: error: Argument 1 to "add" has incompatible type "str"
untyped = []    # inferred Any
untyped.foo()   # mypy: no error — Any silences the check
```

```typescript
// TypeScript
function add(x: number, y: number): number { return x + y; }
add("a", 3);              // tsc: error, string not assignable to number
const x: any = [];        // 'any' opts out
x.foo();                  // tsc: no error — 'any' silences the check
```

**The key insight — gradual type systems are *unsound* by design.** `Any` (mypy) and `any` (TypeScript) are escape hatches that turn checking *off*, so a type-checked program can still fail at runtime. That is a deliberate trade: adoptability and flexibility in exchange for the airtight guarantee a fully static language like Haskell gives you. Contrast this with your HM checker, which has no `Any` escape hatch and so is sound for the fragment it covers.

---

## Section 5: Discussion prompts (POGIL)

1. Place Go, Elixir, and Rust in the quadrant. Where is each, and what evidence (a one-line program) puts it there?
2. TypeScript compiles to JavaScript and then *erases* all types — the runtime has no type information. What class of bug can therefore still occur at runtime despite a clean `tsc`? How does that relate to `Any`?
3. Your interpreter is strong/dynamic. Name one program that runs to completion under it but is *rejected* by the HM type-checking direction. Why is the checker stricter, and is that a bug or a feature?
4. Weakly-typed C lets you reinterpret an `int`'s bits as a `float`. Name one situation where that is genuinely useful and one where it is a catastrophe.

---

## Reference

- [mypy documentation](https://mypy.readthedocs.io/) and [TypeScript Playground](https://www.typescriptlang.org/play)
- Siek & Taha, "Gradual Typing for Functional Languages" (2006) — the founding paper
- Your own `SEMANTICS.md` (dynamic rules) and `TYPES.md` (static rules) from the Interpreter assignment
