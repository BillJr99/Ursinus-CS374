---
layout: textbook
permalink: /Tutorials/LanguageExtensions
title: "CS374: Team Language Extensions Menu"

info:
  coursenum: CS374
  eyebrow: "Tutorial"
  numbering: false
  objectives:
    - "Choose an extension that fits your language"
    - "Say what each extension asks you to build"

tags:
  - final-project
  - languages

---
# Extensions Menu

The distinctive feature is required; the Extensions Menu is where teams go deeper.  Adopting one or more extensions raises the ceiling of your language.  Depth here is credited through the project rubric (chiefly *Implementation Correctness and Integration*, *Evaluation and Testing*, and *Language Design and Documentation*), not through separate point values.  An extension counts only when it is documented in your language reference, covered by at least two dedicated test programs, and demonstrated.  A fully working extension with tests scores far better than two half-working ones without, so scope what you adopt in your proposal's sprint plan.

### Static Type Inference (Hindley-Milner)

Add a type-checking pass that runs before evaluation and infers types for every expression without user-written annotations, reporting type errors with positions and the conflicting types.  Implement let-polymorphism so a polymorphic utility (such as an identity function) works at multiple types in one program.  Include a test program that is correctly rejected.

### Transpilation to Another Language

Add a visitor-based code generator that walks your AST and emits valid Python 3 or ES2020 source as a standalone file runnable with `python3` or `node`, producing output identical to your interpreter for every test program.  Parenthesize operator precedence correctly in the target.  Document any constructs that do not transpile and the substitution your generator makes.  Make the back end a runtime flag alongside your interpreter so a test harness can diff the two execution paths across your whole suite.

### Bytecode Compiler and Stack VM

Add a two-phase back end: a compiler that lowers your AST to a linear stack-machine instruction sequence (PUSH, LOAD, STORE, ADD, JMP_IF_FALSE, CALL, RETURN, and kin) and a virtual machine that executes it, producing the same output as the tree-walking evaluator on all test programs.  Include an annotated execution trace for one non-trivial program showing each instruction, the operand stack before and after, and the program counter.

### Pattern Matching over Algebraic Data Types

Add user-definable algebraic data types (ADTs) and a `match` construct supporting at minimum constructor patterns and wildcard.  Exhaustiveness checking is recognized in grading.  Demonstrate with at least one recursive ADT (a list or tree) and a recursive function over it.

### Garbage Collector

Implement a mark-and-sweep or Cheney copying collector over your runtime environment and heap-allocated values.  Demonstrate that cyclic structures are identified and collected, include a program that would leak without a GC, and report live and dead object counts before and after a collection cycle.

### Concurrency Primitives

Add `spawn` (lightweight concurrent execution) and channel send/receive, implemented with threads, asyncio, or similar.  Demonstrate a producer/consumer program communicating through a channel, and document your memory model: are variables shared, isolated, or communicated exclusively through channels?

### Macros or Hygienic Quoting

Add a macro system that expands at parse time, with hygienic renaming so bindings introduced inside a macro body do not capture user bindings of the same name.  Demonstrate at least two macros, one structural (such as `unless`) and one that introduces a binding, plus a test case that would fail under unhygienic expansion and passes under yours.

### Foreign Function Interface

Allow calling host-language functions from your language via a `foreign` declaration, with marshalling that converts your values to host objects before the call and back after.  Demonstrate at least two foreign functions whose results feed further computation in your language.

### Libraries and Packaging

Give your language a module system: an `import` form that creates a module environment and runs its top-level code, qualified access (`mod.name`), a from-import that copies bindings into the caller's environment, and circular-import detection that raises a clean error rather than recursing forever.  Module namespaces must be isolated: private names are not reachable from outside without qualification.  Test with at least three modules, including one that imports another.

On the packaging side, structure your *implementation* as a proper package with a clean public API (`__init__.py` re-exports, `__all__`, underscore-private helpers).  Consider a plugin architecture (discovering extension modules by name pattern via `importlib` and validating each against a required interface, skipping malformed plugins with a warning) as a way to make your language's built-in library user-extensible.

### Scripting and Automation Targets

Make your language a good citizen of the shell: a file-runner that composes in pipelines (reads stdin, writes stdout, sends errors to stderr), meaningful exit codes on success and each error class, and a scripts-as-tests harness.  The harness is a driver that runs your whole sample suite, checks exit codes, prints a pass/fail line per program, and exits non-zero if anything failed.  Ship the driver and any helper scripts shellcheck-clean and portable (no GNU-only flags without a fallback), with a README explaining how to run the suite.  If your language's niche *is* automation (a build language, a text-processing language, a task-runner DSL), this extension deepens into the niche itself: demonstrate your language orchestrating real programs through pipes and redirection.

### Editor Support: Syntax Highlighting (and an Optional Diagnostic)

Give your language editor support so an audience *sees* it is a language.  Build either a [tree-sitter](https://tree-sitter.github.io/tree-sitter/) grammar for your syntax (its precedence annotations mirror the ladder you already wrote) plus a `highlights.scm` query, or, the lower-friction route, a TextMate grammar wrapped in a minimal VS Code extension.  Scope this small: keyword, number, operator, and string coloring is a complete extension.  The "wow" upgrade is one live diagnostic: pipe your interpreter's positioned error output (`line L, col C: message`, which your pipeline already emits) into VS Code's diagnostics API so a bad program shows a red squiggle at the right spot.  Demonstrate on a sample program at Demo Day, and include a README line showing how a grader installs the extension.  The [Syntax Highlighter tutorial]({{ site.baseurl }}/Tutorials/SyntaxHighlighter) is the step-by-step companion.

### Continuations and First-Class Control

Make "the rest of the computation" a value in your language.  Transform your evaluator, or a small core of it, into continuation-passing style, so that no evaluation step ever returns and each step instead hands its result to an explicit continuation; add a trampoline so that deep programs do not exhaust the host stack; then expose `call/cc`, or an equivalent escape form, to programs written in your language.  Demonstrate at least one control structure rebuilt from it, such as an early `break` out of a loop or an exception handler with `raise`, and state in `SEMANTICS.md` what a captured continuation holds and how long it remains valid.  The `call/cc` reading in the *Lambda Calculus II* activity and the [Coroutines and Generators tutorial]({{ site.baseurl }}/Tutorials/CoroutinesAndGenerators) are the starting points.

### A Lambda-Calculus Core: Church Encodings and Combinators

Give your language a pure functional core and show that other features can be built on it.  Implement capture-avoiding substitution and normal-order reduction for the untyped lambda calculus inside your project (as a mode of your language, or as its core), and encode booleans, numerals, and pairs as pure behavior, with a decoder that turns each encoding back into an ordinary value of your language.  A combinatory variant removes variables entirely: a reducer for S, K, and I, with bracket abstraction from lambda terms.  Test every encoding against hand reductions of the kind the Lambda Calculus lab asks for, and document the evaluation order your reducer uses.  The [Build a Lambda Calculus Reducer tutorial]({{ site.baseurl }}/Tutorials/LambdaCalculusReducer) is the step-by-step companion.

### Logic Programming: A Declarative Sublanguage

Add relations that hold, rather than functions that return: facts, rules, and queries answered by unification plus backtracking, either as the core of a logic-flavored niche language or as a query sublanguage inside a general-purpose one.  Demonstrate at least one relation run "backwards" (a list-append relation that splits a list as well as joining two is the classic case), and document the search order and what a query with no solution produces.  The [Prolog in the Browser with SWISH tutorial]({{ site.baseurl }}/Tutorials/Prolog) works the paradigm in SWI-Prolog with nothing to install, and is the reference for the behavior your sublanguage should reproduce.

### Contribute Upstream: An Open-Source Contribution

Instead of (or alongside) extending your own language, contribute to an existing open-source ecosystem your project touches: a pattern or transformation function in [Strudel](https://github.com/tidalcycles/strudel)/TidalCycles (a natural fit for Direction B teams), a [tree-sitter](https://tree-sitter.github.io/tree-sitter/) grammar improvement (pairs with the Editor Support extension), a step port or test-suite improvement in [Make-a-Lisp (mal)](https://github.com/kanaka/mal), or documentation and worked examples for [SWI-Prolog](https://www.swi-prolog.org/).  This counts like any other extension (credited through the existing rubric dimensions) when three conditions hold: the issue you are addressing is scoped in your proposal, the pull request is submitted with tests and documentation following the upstream project's contributing guidelines, and the maintainer exchange is documented in your report.  A merged pull request is ideal but **not required**.  A substantive review exchange is what is credited, because maintainer response times are outside your control.  A contribution to a live project, reviewed by its maintainer, is a portfolio line few graduates have.
