---
layout: assignment
permalink: /Assignments/FinalProject
title: "CS374: Principles of Programming Languages - Final Project: Design Your Own Language"

info:
  coursenum: CS374
  points: 200
  goals:
    - To synthesize all course concepts (scanning, parsing, ASTs, evaluation, scoping, type systems) into a single working language implementation
    - To make original language design decisions and defend them
    - To implement at least one non-trivial language feature beyond the Mini interpreter baseline
    - To document and present a complete language specification
  rubric:
    - weight: 30
      description: "Language Design and Specification (Goals 2, 4)"
      preemerging: No language specification is provided; the design is a copy of Mini with no distinguishing choices
      beginning: A specification exists but is incomplete or internally inconsistent
      progressing: The specification covers syntax (EBNF), semantics, and design rationale with minor omissions
      proficient: The specification gives complete EBNF grammar, operational semantics for all constructs, a rationale for every non-default design decision, and at least three example programs that motivate the design; the specification is self-consistent and could be reimplemented from scratch by another team
    - weight: 40
      description: "Implementation (Goals 1, 3)"
      preemerging: No working interpreter or compiler; the code does not run
      beginning: A running implementation exists but fails on more than two of the provided test categories
      progressing: All core features (variables, control flow, functions, recursion) work; at least one extension feature is implemented with a minor defect
      proficient: All core features pass the test suite; at least one extension feature is fully implemented and tested; the implementation is modular (separate lexer, parser, AST, evaluator/compiler); error messages name the offending construct and line number; the implementation handles all provided test programs correctly
    - weight: 20
      description: "Testing (Goals 1, 3)"
      preemerging: Fewer than three test programs; no expected-output comparison
      beginning: Tests exist but do not cover the extension feature or edge cases
      progressing: At least eight test programs covering core and extension features; a test harness diffs actual vs expected output with minor gaps
      proficient: At least twelve test programs; the harness runs all tests and reports PASS/FAIL; tests include edge cases (empty input, recursion depth, type error recovery); test coverage includes the extension feature's stated semantics
    - weight: 10
      description: "Presentation and Writeup (Goals 2, 4)"
      preemerging: No presentation or writeup
      beginning: A presentation exists but the design rationale and extension feature are not explained clearly
      progressing: The presentation covers design, implementation, and demo with minor time management issues; the README is mostly complete
      proficient: 10-minute presentation covers: motivation (what problem the language solves), key design decisions with tradeoffs, live demo of at least two programs, lessons learned; README is a complete language reference; the team fielded at least two Q&A questions from peers confidently
  readings:
    - rtitle: "Tutorial: Build a Complete Mini Language"
      rlink: "https://liascript.github.io/course/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374-Fall2026/gh-pages/_pages/Tutorials/tutorial-project-language-guide.md"
    - rtitle: "Transpilers and Compilers Activity"
      rlink: "https://liascript.github.io/course/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374-Fall2026/gh-pages/_pages/Activities/liascript-transpiler-compiler.md"
    - rtitle: "Type Systems Activity"
      rlink: "https://liascript.github.io/course/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374-Fall2026/gh-pages/_pages/Activities/liascript-type-systems.md"

tags:
  - final-project
  - language-design
  - implementation
  - languages

---

This is the capstone assignment of CS374. You will design and implement a small but complete programming language — one that reflects deliberate choices rather than defaults, and that you can run, demo, and explain. The language should do something interesting or solve a real problem. Every prior assignment in this course (lexer, parser, AST, interpreter, transpiler, type inference) has been a component of this final assembly; your language inherits whatever subset of those components you choose to build on, adapt, or replace.

## Teams

Solo or pairs allowed. Teams of three require a third extension feature (see the Extension Menu below). List your team composition in your Week 1 proposal.

## Baseline Requirements

Every submitted language must include all of the following components. Partial implementations in any area will be reflected in the Implementation rubric row.

### Lexer

- At least 20 distinct token types
- Handles: integers, floats, strings with at least two escape sequences (e.g., `\n`, `\"`), identifiers, keywords, operators, and comments (at least one comment style)
- Skips whitespace and blank lines without producing tokens
- Tracks line numbers and embeds them in all error messages

### Parser and AST

- Produces a concrete abstract syntax tree from a token stream
- Implemented via recursive descent, Flex/Bison, or a parser combinator library
- Zero ambiguity: every syntactically valid program has exactly one parse tree
- Handles all language constructs listed below; rejects invalid programs with a syntax error that includes a line number

### Required AST Node Types

- Literals: integer, float, string, boolean
- Variable reference
- Binary operators (arithmetic, comparison, logical)
- Unary operators (negation, logical not)
- If/else conditional
- While loop or for loop
- Function definition
- Function call
- Return statement
- Print or output statement

### Evaluator / Interpreter or Compiler

- Variables with static scoping via a lexical environment chain
- First-class functions with closures (a function defined inside another function must close over its enclosing environment)
- Recursion (demonstrate with factorial or Fibonacci)
- At minimum a file-runner (`python mylang.py program.ext`); a REPL is recommended

### Error Messages

The following three error classes must include both a line number and the name of the offending construct:

- Undefined variable reference
- Wrong-arity function call
- Type mismatch in an operator or built-in function

## Extension Menu (choose at least one)

Select at least one extension from the list below. Teams of three must select at least three. Each extension must be documented in the README and covered by at least two dedicated test programs. Partial credit is available within an extension but a fully working extension with tests scores substantially higher than two half-working extensions with no tests.

### 1. Static Type Inference (Hindley-Milner)

Add a type-checking pass that runs before evaluation and infers types for every expression without requiring user-written type annotations. The pass must report type errors with line numbers and the conflicting types. Implement let-polymorphism so that an identity function or similar polymorphic utility works correctly at multiple types within the same program. Demonstrate the type error path with a test program that should be rejected.

### 2. Transpilation to Python or JavaScript

Add a visitor-based code generator that walks your AST and emits valid Python 3 or ES2020 source code. The generated output must be a standalone file that can be run with `python3` or `node` and must produce byte-for-byte identical results to your interpreter for every test program. Document any language features that do not transpile (e.g., custom escape sequences) and what substitution your generator makes.

### 3. Bytecode Compiler and Stack VM

Add a two-phase backend: a compiler that lowers your AST to a linear sequence of stack machine instructions (PUSH, POP, ADD, CALL, JUMP, etc.), and a virtual machine that executes those instructions. The VM must run all test programs and produce the same output as the tree-walking interpreter. Submit an annotated execution trace for at least one non-trivial program showing each instruction, the operand stack before and after, and the program counter.

### 4. Pattern Matching over Algebraic Data Types

Add user-definable algebraic data types (`data Pair = Pair(a, b)`) and a `match` expression or statement (`match expr { case Pattern: stmt ... }`). Patterns must at minimum support constructor patterns and wildcard (`_`). Exhaustiveness checking is optional but recommended and will be recognized in grading. Demonstrate with at least one recursive ADT (e.g., a linked list or binary tree) and a recursive function over it.

### 5. Garbage Collector

Implement a mark-and-sweep or Cheney copying garbage collector over your runtime environment and heap-allocated values. Demonstrate that cyclic data structures (two objects referencing each other) are correctly identified and collected. Your submission must include a program that would leak memory without a GC, and output that reports live and dead object counts before and after a collection cycle.

### 6. Concurrency Primitives

Add `spawn expr` (lightweight concurrent execution) and `channel` send/receive operations. Implement using Python threads, asyncio, or a similar mechanism. Demonstrate a producer/consumer program in which two concurrent units communicate via a channel and the main program collects results. Document the memory model: are variables shared, isolated, or communicated exclusively through channels?

### 7. Macros or Hygienic Quoting

Add a macro system: `macro name(params) body` that expands at parse time (before evaluation). Implement hygienic renaming so that bindings introduced inside a macro body do not accidentally capture user bindings with the same name. Demonstrate at least two macros: one structural (e.g., `unless`) and one that introduces a new binding (e.g., `swap!`). Show a test case that would fail under unhygienic expansion and passes under your system.

### 8. Foreign Function Interface

Allow calling Python built-in functions or library functions from your language via a `foreign` declaration (e.g., `foreign sqrt from math`). Implement marshalling that converts your language's value types to Python objects before the call and converts the Python return value back to your language's types. Demonstrate calling at least two foreign functions (e.g., `math.sqrt` and `len`) within programs that use the results in further computation.

## Timeline

The project runs for approximately six weeks. Each milestone has a lightweight deliverable; milestones are not graded separately but falling behind will hurt the final submission quality.

- **Week 1 — Language Proposal:** Submit a one-page document (PDF or plain text) containing: your language's name, its target domain or intended use, one motivating example program (3–5 lines written in your proposed syntax), which extension(s) you will implement, and your team composition with a brief note on how you will divide work.

- **Week 2 — Lexer Complete:** Submit your lexer source file(s) and a token table (token type, regex or description, example lexeme). Include at least three tokenization test cases showing input string → expected token stream, run against your actual lexer.

- **Week 3 — Parser and AST Complete:** Submit your parser and AST node definitions, your complete EBNF grammar (one production per line), and a pretty-printed parse tree (or S-expression dump) for your Week 1 motivating example program.

- **Week 4 — Working Core Interpreter:** Submit your interpreter or evaluator and a test harness with at least six passing test programs covering variables, arithmetic, conditionals, loops, and recursion.

- **Week 5 — Extension Feature Implemented:** Add the test programs that exercise your extension feature to the test harness. All Week 4 tests must still pass. Submit a brief progress note (one paragraph) describing what remains before final submission.

- **Week 6 — Final Submission and Presentations:** Final code, full test suite, README, and slides due at the start of the presentation session. See Deliverables below.

## Deliverables

Submit a ZIP archive (or a link to a public or course-accessible repository) containing all of the following. Missing items will be reflected in the rubric.

- All source files for your language implementation (e.g., `lexer.py`, `parser.py`, `ast_nodes.py`, `evaluator.py`, or `calc.l`, `calc.y`, etc.)
- A `Makefile` or `run.sh` that builds and runs a given source file: `make run FILE=tests/hello.ext` or `./run.sh tests/hello.ext`
- `tests/` directory containing at least 12 test programs written in your language, each named descriptively (e.g., `tests/fibonacci.ext`, `tests/closure_counter.ext`)
- `expected/` directory containing the expected output for each test program, named to match (e.g., `expected/fibonacci.txt`)
- `test_runner.py` (or a `make test` target) that runs every test program, diffs actual output against expected output, and reports PASS or FAIL for each test with a final summary count
- `README.md` serving as the language reference (~2 pages minimum), covering: complete EBNF syntax, prose description of every language construct's semantics, description of the extension feature and how to use it, known limitations or unimplemented edge cases, and instructions for running the interpreter and test suite
- Presentation slides in PDF format or a public link

## Language Design Constraints

These constraints exist to ensure that every submission represents original design work rather than a thin wrapper around an existing language.

- Your language must not be a trivial renaming of Python syntax or the Mini language from course activities. Surface-level syntactic changes (renaming `print` to `say`) do not count as design decisions.
- At least two design decisions must differ substantively from Mini. The following are accepted examples: a different default scoping rule (e.g., dynamic scoping, or block scoping without closures), lazy vs. eager evaluation, immutable-by-default bindings (requiring an explicit `mut` annotation to reassign), a different string escape character, a different comment syntax, static vs. dynamic typing, a different truthiness definition, or a different division semantics.
- Every non-default design decision must be documented in the README with a one-sentence rationale explaining why you made that choice rather than following the Mini default.

## Suggested Language Ideas

The following ideas are provided to spark creativity. You are not required to choose from this list; a compelling original idea is always welcome.

1. **Music notation language** — Notes, chords, and rhythms as first-class values; functions that compose musical phrases; transpiles to MIDI events or ASCII tab notation.
2. **Recipe DSL** — Ingredients, cooking steps, and a `serves N` construct; built-in unit conversion (cups to milliliters, Fahrenheit to Celsius); scales a recipe by a factor.
3. **SQL-like language for in-memory lists** — `select`, `where`, `group by`, and `order by` over Python list values; functions that compose queries; demonstrates that SQL-style operations can be first-class.
4. **Cellular automaton language** — Define transition rules as pattern-to-output mappings; a `grid` literal syntax; `step N` advances the world N generations; renders each generation as ASCII art.
5. **Turtle graphics language** — `forward N`, `turn N`, `pen up`, `pen down`, and color commands; programs produce SVG files; demonstrate drawing a recursive fractal.
6. **Probabilistic programming language** — `sample dist` draws from a named distribution; `condition expr` rejects samples that do not satisfy a predicate; `estimate N` runs N samples and reports a posterior approximation.
7. **Stack-based (Forth-like) language** — Programs are sequences of words separated by whitespace; words are functions on an implicit stack; user-definable words via `: name ... ;`; demonstrate a sorting word.
8. **Educational arithmetic language** — Plain-English syntax (`add 3 to 4`, `multiply result by 2`); animated step-by-step evaluation trace showing each sub-expression; designed for children learning order of operations.
9. **Logic programming language** — Facts and rules (`parent(tom, bob).`); a query mechanism (`?- ancestor(tom, X)`); depth-first search with backtracking; demonstrate a family-relationship query.
10. **Constraint language** — Variables declared with numeric ranges; constraint expressions that propagate bounds; solve by arc consistency followed by search; demonstrate a simple Sudoku or scheduling problem.

## Grading Flexibility Note

The rubric rewards completeness, correctness, and thoughtfulness rather than ambition that outstrips execution. A language with one extension feature fully implemented, fully tested, and clearly documented will score higher than a language that lists three extension features but delivers none of them in working condition. Similarly, the presentation component rewards the ability to explain design choices under questioning — a skill that matters in every software engineering context, from code review to technical interview to architectural discussion. A polished demo of a small language that does one thing well is more compelling than a rushed demo of a large language that works intermittently.

## Reflection Prompts (required in README)

Your README must include a section titled "Reflection" that answers all of the following prompts. Thoughtful, specific answers are expected; generic or one-sentence answers will not receive full credit for the Presentation and Writeup rubric row.

- What design decision are you most proud of, and why? Point to the specific construct in your language and describe the alternative you rejected.
- What constraint did you discover during implementation that forced you to change a design decision you had already committed to? What was the original decision, what broke, and what did you replace it with?
- How does your language's scoping rule differ from Python's, and what programs are easier or harder to write in your language as a result? Give a concrete example.
- If you had another two weeks, what would you change or add first, and why? Be specific about the implementation work it would require.
- If collaboration with a buddy was permitted, did you work with a buddy on this assignment? If so, who? If not, do you certify that this submission represents your own original work? Please identify any and all portions of your submission that were not originally written by you.
- Approximately how many hours did this assignment take?
