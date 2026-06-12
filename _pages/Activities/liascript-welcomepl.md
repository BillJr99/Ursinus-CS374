# Welcome: Why Study Programming Languages?
<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://github.com/BillJr99/Ursinus-CS374-Fall2026/blob/gh-pages/_pages/Activities/liascript-welcomepl.md or locally via https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374/gh-pages/_pages/Activities/liascript-welcomepl.md

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

The same computation, summing the squares of the even numbers in a list, in four languages:

```
# Python
total = sum(x*x for x in nums if x % 2 == 0)
```

```
// Java (classic style)
int total = 0;
for (int x : nums) { if (x % 2 == 0) { total += x * x; } }
```

```
;; Scheme
(apply + (map (lambda (x) (* x x)) (filter even? nums)))
```

```
-- SQL
SELECT SUM(x * x) FROM nums WHERE x % 2 = 0;
```

### Critical Thinking Questions

1. For each version, identify what the *programmer* must keep track of (loop counters, intermediate state, nothing?). Which version says *what* to compute and which says *how*?
2. Rank the four for readability by a newcomer, and separately for your own confidence that each is correct. Did the rankings differ? Why might they?
3. The Scheme version is built from three reusable pieces (`filter`, `map`, `apply +`). Identify the analogous pieces hiding inside the Python version's syntax.
4. Propose one computation that would be awkward in SQL but easy in Python. What does that suggest about general-purpose versus domain-specific languages?

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

### Critical Thinking Questions

5. As a team, list the tokens a lexer should produce, in order. How many are there? Did anyone's count differ, and over what (whitespace? the `=`?)?
6. The interpreter must compute `price * 2` before adding 3. Where in the pipeline is that ordering decided: the lexer, the parser, or the interpreter? Defend your answer; we will test it in week 3.
7. Suppose the text were `total = 3 + * 2`. At which stage should the error be caught, and what should a *helpful* error message say?

---

## 3. How This Course Works

The first half of the semester builds your skills bottom-up through scaffolded individual assignments: regular expressions, automata, a lexer, a parser, an interpreter. In the second half, your team **snaps those components together** into a language of your own design, developed in sprints with rotating roles, a gallery walk peer review, and a public Demo Day. Along the way we study languages as artifacts (Scheme, the lambda calculus, modern features) so your design choices are informed by sixty years of others' choices.

---

## 4. Exercises

1. *Language autobiography.* List every programming language and notation (count spreadsheets and regex!) you have used. For each, one sentence: what was it good at?
2. *Notation hunt.* Find one notation in daily life that has a syntax and a semantics but is not usually called a programming language (music notation, knitting patterns, chess notation). The Presenter shares the team's best example.
3. *Team charter.* Draft your team's working agreement: role rotation, communication, preparation norms, and disagreement resolution. The Recorder posts it.

---

## Reflection Prompt

In your notebook: describe one moment when a programming language fought you, when the thing you wanted to say was hard to express. Knowing you will design a language this semester, what would you change to make that moment easier?

---

## 5. Further Reading

- Douglas Thain. *Introduction to Compilers and Language Design* (2nd ed.), Chapter 1. Our pipeline, named and framed.
- Shriram Krishnamurthi. *Programming Languages: Application and Interpretation* (online). The interpreter-first philosophy we follow.
- Robert Nystrom. *Crafting Interpreters* (online), "A Map of the Territory."
