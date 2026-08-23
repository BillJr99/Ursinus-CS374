---
layout: assignment
permalink: /Assignments/ParticipationExercises/
title: "CS374: Principles of Programming Languages - Participation Exercises and Discussion Prompts"

info:
  coursenum: CS374
  points: 10
  submission: "Please bring your attempts to class on the days marked on the schedule.  I assess these within the 15% Class Activities and Participation component, and I do not grade them for correctness."
  goals:
    - To engage each unit's reading actively before class, by hand
    - To arrive at the working session with an attempt and a question
    - To build fluency manipulating the core objects of the course (grammars, automata, tokens, trees, environments, and terms)

tags:
  - resource
  - exercises

---

Reading about a grammar is not the same as writing one, and reading about beta reduction is not the same as reducing a term until it stops.  You build real fluency with programming languages by working their core objects by hand, and by doing it *before* class, so our POGIL session starts from something you have already wrestled with.  This page is a bank of short, reading-linked exercises for each unit.  Each one is a problem or two you can attempt in fifteen minutes with a pencil and a Python REPL.

## Purpose

These exercises exist so that class begins where you actually are, and not where the reading assumes you are.  I hand out each unit's exercises on the schedule on the day they prepare you for, as a **Participation: Exercise** deliverable linking to that unit's page, so please come to that class having attempted them.  We'll work through them together, compare approaches, and let the places you got stuck set the agenda for the session.

## How to Use These

- **Attempt them before class, and not for a grade.**  I don't grade these for correctness.  They are the preparation half of participation, and arriving with an attempt is what the [participation rubric]({{ site.baseurl }}/Participation/PreparingForClass) calls proficient preparation.
- **Work by hand first, then check with code.**  Derive the answer on paper, then confirm it in the REPL where you can.  The by-hand pass is where the understanding forms; the code is the check.
- **Bring your stuck point.**  Mark the one step that resisted you and bring it.  That is your entry ticket to the discussion.
- **Keep them.**  Your attempts are natural raw material for the reflection prompts that close each assignment.

## The Exercises, by Unit

Each unit has its own page with that unit's exercises, the framing for why they are worth doing by
hand, and a link to the activity deck for the session they prepare you for.  The schedule hands out
the right page on the right day; the list below is the whole arc at a glance.

1.  **[Evaluating Languages and Paradigms]({{ site.baseurl }}/Assignments/ParticipationExercises/EvaluatingLanguages)** - for *Programming Paradigms and Evaluating Languages*.  Name a readability and a writability tradeoff in two languages you already use, then translate a snippet across paradigms.
2.  **[Syntax, BNF/EBNF, and Grammars]({{ site.baseurl }}/Assignments/ParticipationExercises/SyntaxAndGrammars)** - for *Grammars and the Chomsky Hierarchy*.  Write a small BNF grammar of your own, extend it to EBNF, and derive a string it generates and one it cannot.
3.  **[Derivations, Parse Trees, Ambiguity, and Precedence]({{ site.baseurl }}/Assignments/ParticipationExercises/DerivationsAndAmbiguity)** - for *Derivations, Parse Trees, Ambiguity, and Precedence*.  Draw two parse trees for one ambiguous string, then rewrite the grammar so only one of them survives.
4.  **[Regular Expressions and Finite Automata]({{ site.baseurl }}/Assignments/ParticipationExercises/RegexAndAutomata)** - for *Regular Expressions, Day 1: Theory*.  Write a regex for a token class, draw the NFA that matches it, and convert a small NFA to a DFA by hand.
5.  **[Tokens and Scanning]({{ site.baseurl }}/Assignments/ParticipationExercises/TokensAndScanning)** - for *Tokens and Scanning: Building a Lexer*.  Hand-tokenize a line, then decide what your scanner does with `12foo` and with overlapping token patterns.
6.  **[Abstract Syntax Trees]({{ site.baseurl }}/Assignments/ParticipationExercises/AbstractSyntaxTrees)** - for *Abstract Syntax Trees*.  Draw an AST, name what it discarded, and design the node types for `if`/`else` and calls in your language.
7.  **[Recursive Descent Parsing]({{ site.baseurl }}/Assignments/ParticipationExercises/RecursiveDescent)** - for *Recursive Descent Parsing: From Grammar to Code*.  Write and hand-trace one recursive-descent function, then rewrite a left-recursive rule so it terminates.
8.  **[Tree-Walking Interpretation, Binding, and Scope]({{ site.baseurl }}/Assignments/ParticipationExercises/BindingAndScope)** - for *Tree-Walking Interpretation* and again for *Binding and Scope*.  Evaluate a shadowing expression by hand under both lexical and dynamic scope, drawing the environment at each step.
9.  **[Type Systems]({{ site.baseurl }}/Assignments/ParticipationExercises/TypeSystems)** - for *Type Systems*.  Annotate a program's types, then name one program a checker forbids that you wish it allowed.
10.  **[Functional Programming and Higher-Order Functions]({{ site.baseurl }}/Assignments/ParticipationExercises/FunctionalProgramming)** - for *Functional Programming and Higher-Order Functions*.  Rewrite a `for` loop with `map`/`filter`/`reduce`, then write a closure and trace what it captured.
11.  **[Lambda Calculus]({{ site.baseurl }}/Assignments/ParticipationExercises/LambdaCalculus)** - for *Lambda Calculus I: Syntax and Beta Reduction*.  Beta-reduce a term to normal form, meet one that never reaches it, and check `SUCC ZERO` against `ONE`.

## See also

- [Preparing for Each Class]({{ site.baseurl }}/Participation/PreparingForClass): the routine these exercises fit into, and the participation rubric.
