---
layout: assignment
permalink: /Assignments/Functional
title: "CS374: Principles of Programming Languages - Functional Programming"

info:
  coursenum: CS374
  points: 100
  goals:
    - To write pure functional Python using map, filter, reduce, and higher-order functions without assignment or loops
    - To write recursive Scheme functions over lists following the base case and recursive case pattern
    - To implement Church encodings and verify them by execution
    - To compare functional expression across languages with the course evaluation criteria
  rubric:
    - weight: 40
      description: Functional Python
      preemerging: The solutions fail to run or rely pervasively on loops and assignment
      beginning: The solutions run but several use loops or assignment where the directions forbid them
      progressing: The solutions are correct and respect the constraints, with a minor lapse such as one unnecessary intermediate mutation
      proficient: Correct solutions respect the no-loop and no-assignment constraints throughout, use the combinators idiomatically, and pass the provided and hidden test cases
    - weight: 35
      description: Scheme Programming
      preemerging: The Scheme functions fail to run or are fundamentally incorrect
      beginning: The functions run but several fail their test cases due to one or more minor issues
      progressing: The functions are correct on the provided test cases, with a minor structural issue such as a missing base case guard
      proficient: Correct recursive functions follow the base and recursive case pattern, pass the provided and hidden test cases, and the AST evaluator exercise demonstrates a working interpreter over nested lists
    - weight: 15
      description: Church Encodings
      preemerging: The encodings are missing or incorrect
      beginning: Some encodings work but verification is incomplete
      progressing: The required encodings work with execution-based verification, with limited explanation
      proficient: The required encodings work with execution-based verification, and the writeup includes one hand reduction matching the executed result
    - weight: 10
      description: Writeup and Submission
      preemerging: An incomplete submission is provided
      beginning: The program is submitted, but not according to the directions in one or more ways
      progressing: The program is submitted according to the directions with a minor omission, with at least superficial responses to the reflection prompts
      proficient: The program is submitted according to the directions, including a readme writeup with the comparative analysis and thoughtful answers to the reflection prompts
  readings:
    - rtitle: "Functional Programming Activity"
      rlink: "https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374/gh-pages/_pages/Activities/liascript-functional.md"
    - rtitle: "Scheme Activity"
      rlink: "https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374/gh-pages/_pages/Activities/liascript-scheme.md"
    - rtitle: "Lambda Calculus Part 2 Activity"
      rlink: "https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374/gh-pages/_pages/Activities/liascript-lambdacalculus2.md"

tags:
  - functional
  - scheme
  - lambda-calculus

---

This assignment exercises the functional paradigm three ways: disciplined Python, idiomatic Scheme, and the lambda calculus executed. The constraints are the content: where the directions say no loops and no assignments, the constraint is teaching you the paradigm.

## Part 1: Functional Python (no loops, no assignment statements within the solution logic)

Implement and test, using only `map`, `filter`, `functools.reduce`, `lambda`, comprehension-free composition, and recursion:

1a. `total_length(words)`: the total characters across words longer than three letters.

1b. `product_of_odds(nums)`: the product of the odd numbers (define the empty case and document it).

1c. `longest(words)`: the longest word, via a single `reduce`.

1d. `compose(*fns)`: variadic left-to-right composition, demonstrated with `compose(str.strip, str.lower, len)`.

1e. `my_map(f, xs)` and `my_reduce(f, xs, seed)`: recursive implementations (no loops), property-tested against the built-ins on at least five inputs each, with the class exception pattern.

## Part 2: Scheme

In Racket (or an online Scheme), implement and test with at least three cases each:

2a. `(my-length lst)`, `(my-append lst1 lst2)`, and `(my-reverse lst)` recursively.

2b. `(my-map f lst)`, `(my-filter pred lst)`, and `(my-reduce f seed lst)` following the base and recursive case pattern.

2c. `(count-if pred lst)` built by composing your 2b functions rather than fresh recursion.

2d. The capstone: `(evaluate tree)` over nested-list ASTs like `'(* (+ 2 3) 4)` supporting `+ - * /`, tested on at least four trees including a nested one. In a comment, state how many lines this took compared with your Python interpreter's expression evaluator, and why.

## Part 3: Church Encodings (Python)

3a. Define `TRUE`, `FALSE`, `NOT`, `AND`, `OR` as Python lambdas and verify all of `NOT`'s and `AND`'s truth tables by execution with a `show_bool` decoder.

3b. Define `ZERO`, `SUCC`, `PLUS`, `MULT` and a `to_int` decoder; verify `2 + 3 = 5` and `2 * 3 = 6` by execution.

3c. Define `PAIR`, `FST`, `SND` and verify; in one sentence, state what data structure you built from functions alone.

3d. In your writeup, include one complete hand reduction (every step) of `AND TRUE FALSE` to `FALSE`, and confirm it matches your executed result.

## Part 4: Comparative Analysis (in the readme)

In approximately half a page, compare expressing 2b's functions in Scheme against 1e's in Python through the readability and writability criteria: which language made the recursive pattern clearer, what syntax helped or hurt, and one observation about what your December language should borrow.

## Deliverables

Submit a ZIP containing your Python solutions with tests, your Scheme source with a transcript of the test runs, the Church encoding file with verification output, and a readme writeup of approximately one page including Part 4 and the hand reduction. Ensure reproducibility by listing software version information for both Python and your Scheme implementation.

## Reflection Prompts

- Which constraint (no loops, or no assignment) changed your thinking more, and what did it force you to see?
- After 2d, state in one sentence why Scheme made the AST evaluator so short.
- If collaboration with a buddy was permitted, did you work with a buddy on this assignment? If so, who? If not, do you certify that this submission represents your own original work? Please identify any and all portions of your submission that were not originally written by you.
- Approximately how many hours it took you to finish this assignment (I will not judge you for this at all...I am simply using it to gauge if the assignments are too easy or hard)?
