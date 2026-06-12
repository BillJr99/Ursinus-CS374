# Programming Paradigms
<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://github.com/BillJr99/Ursinus-CS374-Fall2026/blob/gh-pages/_pages/Activities/liascript-paradigms.md or locally via https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374/gh-pages/_pages/Activities/liascript-paradigms.md

import: https://raw.githubusercontent.com/liascript/CodeRunner/master/README.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

# Programming Paradigms

A **paradigm** is a worldview about what a program *is*: a sequence of commands, a society of objects, a composition of functions, or a set of facts and rules. Today we tour the four major paradigms with the same small problem expressed in each, because your team's language will have to pick a side (or blend several, as most modern languages do). The arc: **imperative $\rightarrow$ object-oriented $\rightarrow$ functional $\rightarrow$ logic $\rightarrow$ multi-paradigm reality**.

---

## Directions and Group Roles

Work in your POGIL team with rotated roles (**Manager**, **Recorder**, **Presenter**, **Reflector**). Consider each model and question individually first, then discuss with your group. The Recorder posts answers to the Class Activity Questions discussion board; the Presenter reports out areas of disagreement or alternative approaches. After class, respond to the reflective prompt individually in your notebook.

---

# Part I: The Four Worldviews

## 1. Imperative and Object-Oriented

**Imperative: a program is a sequence of state changes.** The core concepts are variables (named mutable cells), assignment, and control flow (sequencing, selection, iteration). The model matches the machine: memory cells change over time. C is the archetype; most languages contain an imperative heart.

**Object-oriented: a program is a society of objects exchanging messages.** State is *encapsulated* inside objects; behavior travels with the data it governs; **polymorphism** lets the same message mean different things to different receivers. OO answers the imperative paradigm's scaling problem: when everything can mutate everything, large programs become unpredictable, so OO draws fences.

## 2. Functional and Logic

**Functional: a program is the composition of functions.** The central commitments are **immutability** (values do not change; new values are produced), **first-class functions** (functions are values that can be passed and returned), and **referential transparency** (an expression can be replaced by its value without changing behavior). Where imperative code says *do this, then that*, functional code says *the answer is this transformation of that*. Scheme, Haskell, and increasingly the cores of Python and Java.

**Logic: a program is facts and rules; the runtime searches for proofs.** In Prolog one declares `parent(tom, mary).` and rules like `ancestor(X, Y) :- parent(X, Y).`, then asks queries; the *how* belongs entirely to the engine. Logic programming is the purest case of **declarative** programming, stating what is true rather than what to do.

---

## Model 1: Same Problem, Four Ways

Count the vowels in a string.

```
# Imperative (Python)
count = 0
for ch in s:
    if ch in "aeiou":
        count = count + 1
```

```
# Object-oriented (Python)
class VowelCounter:
    def __init__(self, text): self.text = text
    def count(self):
        return sum(1 for ch in self.text if ch in "aeiou")
```

```
;; Functional (Scheme)
(length (filter (lambda (ch) (member ch '(#\a #\e #\i #\o #\u)))
                (string->list s)))
```

```
% Logic (Prolog, sketch)
vowel(a). vowel(e). vowel(i). vowel(o). vowel(u).
count_vowels(S, N) :- include(vowel, S, Vs), length(Vs, N).
```

### Critical Thinking Questions

1. Identify the mutable state in each version (there may be none). Which versions could safely run on two halves of the string in parallel and add the results, and why?
2. The OO version wraps the same logic in a class. Name one situation where that wrapping pays for itself, and one where it is ceremony.
3. In the Prolog sketch, where is the loop? What does its absence tell you about who owns control flow in logic programming?
4. Your team's language project must choose: mutable variables or immutable bindings (or both). List one implementation consequence of each choice for the *interpreter* you will build.

---

# Part II: Paradigms in the Wild

## 3. Multi-Paradigm Reality

**Pure paradigm languages are rare; blends are the norm.** Python is imperative and OO with a functional toolkit (`map`, `filter`, comprehensions, `lambda`). Java added lambdas and streams in 2014; JavaScript mixes prototypal objects with pervasive higher-order functions; Rust is imperative with functional pattern matching and an ownership discipline. The paradigm question for a designer is not *which one* but *which defaults*: what does the language make easy, and what does it make possible?

[[MC]]
A language guarantees that no value can ever be modified after creation and that functions may be stored in variables and passed as arguments. These two guarantees are the signatures of:
- ( ) The imperative paradigm
- ( ) The object-oriented paradigm
- (x) The functional paradigm
- ( ) The logic paradigm

---

## Model 2: Classify the Snippets

| Snippet | Paradigm signal |
|---------|-----------------|
| `account.deposit(50)` | ? |
| `x := x + 1` | ? |
| `(reduce + 0 prices)` | ? |
| `sibling(X,Y) :- parent(P,X), parent(P,Y).` | ? |

### Critical Thinking Questions

5. Classify each snippet and name the *single feature* that gave it away.
6. `account.deposit(50)` mutates state *and* sends a message to an object. Is OO a kind of imperative programming with better manners, or something fundamentally different? Take a team position.
7. Modern Python lets you write all four rows' ideas (the fourth via libraries). Does multi-paradigm flexibility help or hurt the *reader* of a program? Connect to tomorrow's topic, language evaluation criteria.

---

# Part III: Synthesis and Practice

## 4. Exercises

1. *Paradigm translation.* Take the imperative vowel counter and rewrite it functionally in Python using `filter` and `len` with no assignment statements. Verify both produce identical results on three inputs.
2. *Blend audit.* Pick one language a teammate knows well and list which paradigm supplies its defaults and which paradigms are available on request, with one feature as evidence each.
3. *Design straw poll.* As a team, record a provisional decision for your future language: primary paradigm, mutability default, and whether functions are first-class. You may change it later; the exercise is having reasons now.

---

## Reflection Prompt

In your notebook: which paradigm fits the way *you* naturally think about problems, and which feels most foreign? Describe one problem from another course (mathematics, biology, economics) and which paradigm would express it most directly.

---

## 5. Further Reading

- Douglas Thain. *Introduction to Compilers and Language Design*, Chapter 1.
- Peter Van Roy. "Programming Paradigms for Dummies: What Every Programmer Should Know" (2009, online). A famous map of the paradigm space.
- Shriram Krishnamurthi. *PLAI*, early chapters on the functional core.
