# Evaluating Languages: Readability, Writability, Reliability
<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://github.com/BillJr99/Ursinus-CS374-Fall2026/blob/gh-pages/_pages/Activities/liascript-languageevaluation.md or locally via https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374/gh-pages/_pages/Activities/liascript-languageevaluation.md

import: https://raw.githubusercontent.com/liascript/CodeRunner/master/README.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

# Evaluating Languages: Readability, Writability, Reliability

"Which language is best?" is a bad question; "best *for what*, judged *by what criteria*" is an engineering question. Today we adopt the classical evaluation framework (readability, writability, reliability, and cost) and the design tradeoffs that connect them, because every choice your team makes in December will trade one criterion against another. The arc: **the criteria $\rightarrow$ the design features that drive them $\rightarrow$ tradeoffs in real languages $\rightarrow$ a scorecard for your own design**.

---

## Directions and Group Roles

Work in your POGIL team with rotated roles (**Manager**, **Recorder**, **Presenter**, **Reflector**). Consider each model and question individually first, then discuss with your group. The Recorder posts answers to the Class Activity Questions discussion board; the Presenter reports out areas of disagreement or alternative approaches. After class, respond to the reflective prompt individually in your notebook.

---

# Part I: The Criteria

## 1. Four Lenses

**Readability** is the ease with which programs can be read and understood, and it dominates total cost because code is read far more often than written. It is driven by *simplicity* (few constructs, few ways to do one thing), *orthogonality* (a small set of features combinable without special cases), and *syntax design* (meaningful keywords, consistent forms).

**Writability** is the ease of creating programs: *expressivity* (powerful, concise operations like list comprehensions), *abstraction support* (functions, classes, modules), and fit between the language and the problem domain.

**Reliability** is the likelihood that programs behave as intended: *type checking* (catching misuse early), *exception handling*, *aliasing restrictions* (fewer ways for two names to surprise you by referring to one cell), and, foundationally, readability and writability themselves, since code that is hard to read hides its bugs.

**Cost** totals the lifecycle: training, writing, compiling, executing, maintaining, and the price of unreliability. A language fast to write but cryptic to read shifts cost from author to maintainer; a language with heavyweight checking shifts cost from runtime failures to compile-time friction.

---

## Model 1: Orthogonality Under the Microscope

In C, `a + b` works for ints and floats, arrays cannot be added or returned from functions by value, and `struct`s can be returned but not compared with `==`. In Python, `+` works for numbers, strings, and lists, but `{} + {}` fails, and `set + set` fails while `set | set` succeeds.

### Critical Thinking Questions

1. Define orthogonality in your own words using these examples: which special cases break the "features combine uniformly" promise in each language?
2. A maximally orthogonal language sounds ideal. Propose one danger of *too much* orthogonality (hint: if everything combines with everything, what can the reader assume about any expression?).
3. Score C and Python (low/medium/high) on each of the four criteria for the task "a 200-line data cleaning script maintained by rotating student workers." Defend your most contested cell.

---

# Part II: Tradeoffs

## 2. There Is No Free Criterion

**Reliability versus cost of execution.** Java checks every array index at runtime; C does not. One buys memory safety with cycles; the other buys speed with vulnerability (buffer overflows remain a top security flaw class decades later).

**Writability versus readability.** APL and Perl achieve astonishing concision; their critics call them write-only. Python's design explicitly privileges the reader ("readability counts"), accepting more keystrokes.

**Flexibility versus reliability.** Dynamic typing (Python) lets any variable hold anything, which speeds exploration and defers type errors to runtime, possibly in production. Static typing (Java, Rust) front-loads the friction. Modern designs hedge: type *inference* (the compiler deduces types you did not write) and *gradual typing* (Python's optional annotations) try to buy reliability without the ceremony.

[[MC]]
A team adds implicit type coercion to their language so that `"3" + 4` yields `7`, reasoning that it improves writability. The most likely cost, in this framework, is to:
- ( ) Execution speed only
- (x) Reliability, because errors that types would have caught now produce silently wrong values
- ( ) Training cost only
- ( ) Nothing; coercion is free

---

## Model 2: The Billion-Dollar Hindsight

Tony Hoare called the null reference his "billion-dollar mistake." Languages have responded differently: Java retains null and added `Optional`; Kotlin makes nullability part of the type (`String?` versus `String`); Rust has no null, only `Option<T>` which the compiler forces you to unwrap explicitly.

### Critical Thinking Questions

4. Express each of the three responses as a position in the reliability-versus-writability tradeoff. Which shifts the cost of absence-handling earliest?
5. Your project language will have to decide what happens when a variable is used before assignment. Enumerate three possible designs (error at parse time, error at run time, default value) and score each on reliability and writability.
6. Hoare's mistake survived fifty years because it was *convenient*. Name one convenience in a language you use that you now suspect is somebody's future billion-dollar regret.

---

# Part III: Synthesis and Practice

## 3. Exercises

1. *Criteria audit.* Choose one feature of a language you know (Python indentation blocks, Java checked exceptions, C pointers, JavaScript `==` coercion). Write a half-page evaluation through all four lenses, ending with a verdict: keep, modify, or remove, and why.
2. *Scorecard draft.* Create your team's language-design scorecard: the four criteria as rows, with a sentence per row stating what your language will prioritize and what it will knowingly sacrifice. This scorecard reappears in your project proposal.
3. *Holy war defusal.* Find one online "language X versus Y" argument and translate its two loudest claims into this framework. Does the disagreement survive translation, or does it dissolve into different weightings of the same criteria?

---

## Reflection Prompt

In your notebook: recall the language feature that most confused you as a beginning programmer. Through today's lenses, was the confusion a readability failure, a reliability failure, or a teaching failure? What would you change?

---

## 4. Further Reading

- Douglas Thain. *Introduction to Compilers and Language Design*, Chapter 1.
- Robert Sebesta. *Concepts of Programming Languages*, Chapter 1 (the canonical source of this framework; any edition, library reserve).
- Tony Hoare. "Null References: The Billion Dollar Mistake" (talk, 2009, online).
