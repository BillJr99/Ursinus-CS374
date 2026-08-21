---
layout: assignment
permalink: /Participation/ReadingExercises
title: "CS374: Principles of Programming Languages - Reading Exercises and Discussion Prompts"

info:
  coursenum: CS374
  points: 10
  submission: "Bring your attempts to class on the days marked on the schedule. These are low-stakes preparation, assessed as part of the 15% Class Activities and Participation component, not graded for correctness."
  goals:
    - To engage each unit's reading actively before class, by hand
    - To arrive at the working session with an attempt and a question
    - To build fluency manipulating the core objects of the course - grammars, automata, tokens, trees, environments, and terms

tags:
  - resource
  - exercises

---

Reading about a grammar is not the same as writing one; reading about beta reduction is not the same as reducing a term until it stops. The fastest way to build real fluency with programming languages is to work their core objects by hand, and to do it *before* class, so that our POGIL session starts from something you have already wrestled with. This page is a bank of short, reading-linked exercises for each unit: one or two problems you can attempt in fifteen minutes with a pencil and a Python REPL.

## Purpose

These exercises exist so that class begins where you are, not where the reading assumes you are. On the days marked **"Reading Exercise / Discussion"** on the schedule, come having attempted that unit's exercises; we will work through them together, compare approaches, and let the places you got stuck set the agenda. A genuine attempt that ran aground is worth more to the discussion than a blank page or a perfect one: the stuck points are the lesson.

## How to Use These

- **Attempt before class, not for a grade.** These are not graded for correctness. They are the preparation half of participation: arriving with an attempt is what the [participation rubric]({{ site.baseurl }}/Participation/PreparingForClass) calls proficient preparation.
- **Work by hand first, then check with code.** Derive the answer on paper, then confirm it in the REPL where you can. The by-hand pass is where the understanding forms; the code is the check.
- **Bring your stuck point.** Mark the one step that resisted you and bring it. That is your entry ticket to the discussion.
- **Keep them.** Your attempts are natural raw material for the reflection prompts that close each assignment.

## The Exercises, by Unit

### Evaluating Languages and Paradigms

- Pick two languages you know and write one sentence each naming a design choice that makes one *more readable* and the other *more writable*; be ready to defend which you value more and why.
- Take a five-line snippet in any language and classify the paradigm it primarily represents. Then rewrite it in a different paradigm (or explain why you cannot) and name what the translation cost.

### Syntax, BNF/EBNF, and Grammars

- Write a BNF grammar for a small language of your choice: for example, signed decimal numbers, or a boolean expression with `and`/`or`/`not`. Then extend it to EBNF and note what the EBNF made shorter.
- Given a short grammar from the reading, produce a leftmost derivation of one string it generates, and a string it *cannot* generate; explain how you know.

### Derivations, Parse Trees, Ambiguity, and Precedence

- Show that a given expression grammar is ambiguous by drawing two distinct parse trees for one string. Then rewrite the grammar to encode precedence and associativity so the ambiguity is gone.
- Take `2 - 3 - 4` and draw the parse tree that makes subtraction left-associative; then the one that makes it right-associative. Which does your favorite language use? Confirm in the REPL.

### Regular Expressions and Finite Automata

- Write a regular expression for a token class of your choice (identifiers, or floating-point literals) and then draw an NFA that accepts the same language.
- Convert a small NFA from the reading to a DFA by hand (subset construction on two or three input symbols), and name one string the DFA accepts.

### Tokens and Scanning

- Hand-tokenize the line `x = 12 + foo(3)` into a token stream, giving each token a type and a value. Then predict what your scanner should do with `12foo` and with `= =` versus `==`.
- Write the regular expressions your lexer would use for three token classes, and identify one pair whose patterns overlap: which rule wins, and why does order matter?

### Recursive Descent Parsing

- For a small expression grammar, write the pseudocode of the recursive-descent function for one non-terminal, and trace it by hand on a three-token input, marking where it looks ahead.
- Identify a grammar rule that would make naive recursive descent loop forever (left recursion) and rewrite it so it does not.

### Abstract Syntax Trees

- Draw the AST (not the parse tree) for `3 + 4 * 5`, and say in one sentence what the AST threw away that the parse tree kept.
- Design the node types (as Python dataclasses or a `match`/`case` shape) you would use to represent `if`/`else` and function calls in your team's language.

### Tree-Walking Interpretation, Binding, and Scope

- Evaluate `let x = 2 in let x = x + 1 in x * x` by hand, drawing the environment at each step. Then predict the answer under *dynamic* rather than lexical scope and say where they diverge.
- Trace what your evaluator does with an unbound variable, and decide what error it should raise and when.

### Type Systems

- For a small program, annotate each subexpression with the type you expect, and find one expression a static type checker would reject that a dynamic language would run. Which behavior do you prefer here, and why?
- State one guarantee a type system buys and one program it forbids that you wish it allowed.

### Functional Programming and Higher-Order Functions

- Rewrite a loop you would normally write with a `for` into `map`/`filter`/`reduce`, then say which version you find more readable and whether that is about the code or about your habits.
- Write a function that returns a function (a closure), and trace by hand what it captures.

### Lambda Calculus

- Beta-reduce `(λx. λy. x) a b` to normal form, showing each step. Then try `(λx. x x)(λx. x x)` and explain what happens.
- Using the Church encodings from the reading, verify by reduction that `SUCC ZERO` behaves like `ONE`.

## See also

- [Preparing for Each Class]({{ site.baseurl }}/Participation/PreparingForClass): the routine these exercises fit into, and the participation rubric.
