# Modern Language Features
<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://github.com/BillJr99/Ursinus-CS374-Fall2026/blob/gh-pages/_pages/Activities/liascript-modernfeatures.md or locally via https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374/gh-pages/_pages/Activities/liascript-modernfeatures.md

import: https://raw.githubusercontent.com/liascript/CodeRunner/master/README.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

# Modern Language Features

Language design did not stop with the features your interpreter implements; it accelerated. Today we survey four ideas that define the current generation (pattern matching, generics, memory safety through ownership, and async concurrency), each through the lenses you have built: what problem it solves, what it costs, and which evaluation criterion it serves. Your project pitches a feature menu next week; today stocks the menu. The arc: **pattern matching $\rightarrow$ generics $\rightarrow$ ownership $\rightarrow$ async $\rightarrow$ choosing for your language**.

---

## Directions and Group Roles

Work in your POGIL team with rotated roles (**Manager**, **Recorder**, **Presenter**, **Reflector**). Today runs as a jigsaw: each pair takes one feature as primary, then teaches it back using the three-lens template (problem, mechanism, cost). After class, respond to the reflective prompt individually in your notebook.

---

# Part I: The Features

## 1. Pattern Matching: Branching on Shape

**The problem.** Code that dissects structured data degenerates into nested ifs and field accesses. **The mechanism.** A `match` tests a value against *patterns* that simultaneously check shape and bind variables; Python (3.10) joined Rust, Scala, and the ML family:

```python
def describe(node):
    try:
        match node:
            case ("num", n):
                return f"the number {n}"
            case ("+", left, right):
                return f"a sum of ({describe(left)}) and ({describe(right)})"
            case ("neg", inner):
                return f"the negation of {describe(inner)}"
            case _:
                return "something unrecognized"
    except Exception as e:
        print(f"[modern:describe] {e}")
        import traceback; traceback.print_exc()
        return ""

print(describe(("+", ("num", 2), ("neg", ("num", 3)))))
```

**The cost and the criterion.** A new syntactic form (readability spent up front, repaid in every dissection), and questions of exhaustiveness: ML-family compilers *prove* you handled every case, a reliability win your `evaluate`'s if-chain never gets. Notice the example: pattern matching is practically purpose-built for tree walks like yours.

## 2. Generics: Abstraction over Types

**The problem.** A statically typed list-of-int and list-of-string need the same code twice, or an unsafe any-type escape hatch. **The mechanism.** Parameterize the *type itself*: `List[T]`, `def first(items: list[T]) -> T`. The checker verifies the code once *for all* T, and call sites stay fully checked. **The cost and the criterion.** Type-system complexity (Java's wildcards, variance puzzles) traded for reliability-with-reuse; dynamically typed languages get the reuse for free and the checking never. Connect to the types module: generics exist precisely to keep static typing's early binding without its duplication.

## 3. Ownership: Memory Safety without a Garbage Collector

**The problem.** C frees memory manually (use-after-free, leaks, security holes); Java collects garbage at runtime (safe, but with pauses and overhead). **The mechanism.** Rust's third way: every value has exactly **one owner**; assignment *moves* ownership; **borrows** lend access temporarily (many readers or one writer, never both); the compiler proves at compile time that no reference outlives its value, so the program needs neither `free` nor a collector. **The cost and the criterion.** A famously steep learning curve ("fighting the borrow checker"): writability spent for reliability *and* performance simultaneously, which is why Rust keeps winning systems-programming converts. Binding-time lens: Rust moved memory-correctness from runtime (GC) or never (C) to compile time.

## 4. Async/Await: Concurrency as Syntax

**The problem.** Programs that wait (network, disk) waste their wait, and callback-based solutions shred control flow. **The mechanism.** `async` functions are *pausable*: `await` yields control at a wait point and resumes when the result arrives, letting one thread interleave thousands of waiting tasks; the compiler transforms your straight-line code into a state machine (a *desugaring*, industrial grade). **The cost and the criterion.** The "function color" problem: async functions can only be awaited from async functions, splitting the ecosystem in two; writability and performance for I/O-bound work, bought with a pervasive design constraint.

---

## Model 1: Three Lenses, Four Features

### Critical Thinking Questions

1. Complete the jigsaw grid as a class: for each feature, the problem, the mechanism in one sentence, the criterion served, and the criterion taxed.
2. Run the pattern-matching cell, then rewrite *your interpreter's* `evaluate` dispatch as a `match` on node classes (`case Num(value=n):` works on your classes!). Report: lines saved, readability verdict, and one behavior the if-chain allowed that match's structure discourages.
3. Ownership and garbage collection are both answers to "when may memory be reclaimed?" Place C, Java/Python, and Rust on a binding-time axis for that decision, and state each position's billion-dollar risk.
4. Which of the four features could a *tree-walking interpreter team* plausibly implement a slice of in three weeks, and which are out of reach? Justify with reference to which pipeline stage each feature lives in (parser? evaluator? a checker between them?).

[[MC]]
Rust achieves memory safety without a garbage collector primarily by:
- ( ) Forbidding heap allocation
- ( ) Checking every pointer at runtime
- (x) Compile-time ownership and borrowing rules that prove references cannot outlive the values they point to
- ( ) Running a collector only at program exit

---

# Part II: Stocking Your Menu

## 2. Exercises

1. *Feature pitch.* Each pair writes a half-page pitch for adding their jigsaw feature (or an honest slice of it) to the team language: the construct's syntax in your grammar's EBNF, the node it adds, the evaluator rule, and the criterion it serves. The team votes one pitch onto the project's "stretch goals" list.
2. *Exhaustiveness by hand.* Add a new node type to your AST but not to your match-based evaluate. Run it; read the failure. Now add a `case _:` that raises a located error listing the node type. You have hand-built the safety net ML compilers automate; one sentence on the difference.
3. *Color audit.* Sketch (no implementation) what adding async to your language would split: which built-ins become awaitable, which functions change color, what the REPL does with a pending value. Conclude with a recommendation and its rationale.
4. *Feature archaeology.* Each teammate picks one feature that *arrived* in a mainstream language during their lifetime (Python match 2021, Java records 2020, JS async 2017, C++ lambdas 2011) and reports the proposal document's stated motivation versus what we identified today.

---

## Reflection Prompt

In your notebook: every feature today moved some check or transformation to an earlier binding time at the price of language complexity. Is there a complexity budget beyond which a language should stop adding features, and who in a language community should hold that budget? Answer as the designer you are about to be.

---

## 3. Further Reading

- The Rust Book, chapter 4 (ownership): https://doc.rust-lang.org/book/
- PEP 634 through 636 (Python structural pattern matching), especially 636, the tutorial.
- Bob Nystrom. "What Color is Your Function?" (online essay), the async critique, vividly argued.
