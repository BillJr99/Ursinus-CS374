---
layout: assignment
permalink: /Assignments/Lexer
title: "CS374: Principles of Programming Languages - The Lexer"

info:
  coursenum: CS374
  points: 100
  goals:
    - To harden the class tokenizer into a reusable Lexer component with a peek and advance interface
    - To implement string literals with escape sequences and JSON-configurable token specifications
    - To report lexical errors with line and column positions
    - To deliver a tested component that the parser assignment and the team project will import unchanged
  rubric:
    - weight: 60
      description: Algorithm and Implementation
      preemerging: The lexer fails to run or fails most provided programs due to major issues
      beginning: The lexer runs but fails on several provided test programs due to one or more minor issues
      progressing: The lexer passes the provided test programs but would fail in a general case due to a minor issue such as a pattern-ordering bug or an unhandled escape
      proficient: A correct lexer passes the provided and hidden test programs, applies maximal munch and priority correctly, handles string escapes, and would be reasonably expected to handle the general case
    - weight: 20
      description: Component Interface and Configuration
      preemerging: The lexer is a script without a reusable interface
      beginning: A class exists but peek or advance is missing or incorrect
      progressing: The Lexer class with peek and advance works, with the token specification partially externalized
      proficient: The Lexer class exposes a correct peek and advance interface, the token specification and comment character load from JSON configuration, and the component imports cleanly into a separate test program
    - weight: 10
      description: Error Reporting and Testing
      preemerging: Lexical errors crash without information, or no tests exist
      beginning: Errors are reported without positions, or the test suite is minimal
      progressing: Errors include line and column, and a test suite covers the major token types
      proficient: Errors include line, column, and the offending text, an error-recovery mode collects all errors in one pass, and the test suite covers every token type plus at least five deliberate error cases
    - weight: 10
      description: Writeup and Submission
      preemerging: An incomplete submission is provided
      beginning: The program is submitted, but not according to the directions in one or more ways
      progressing: The program is submitted according to the directions with a minor omission, with at least superficial responses to the reflection prompts
      proficient: The program is submitted according to the directions, including a readme writeup and thoughtful answers to the reflection prompts
  readings:
    - rtitle: "Tokens and Scanning Activity"
      rlink: "https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374/gh-pages/_pages/Activities/liascript-tokensscanning.md"

tags:
  - lexer
  - languages
  - pipeline

---

This assignment turns the class tokenizer into a **component**: the first permanent piece of your language pipeline. The parser assignment imports it; your team project ships it. Build in the scaffolded steps below.

## Part 1: The Core (from class to component)

1a. Start from the class token specification and `tokenize` generator. Verify it against the provided test programs before changing anything (a known-good baseline).

1b. Wrap it in a `Lexer` class with the interface the parser will use: `peek()` returns the next token without consuming it; `advance()` consumes and returns it; both return a designated `EOF` token at end of input (decide and document its behavior on repeated calls).

1c. Demonstrate that two different consumption patterns (a peek-driven loop and an advance-driven loop) produce identical token streams on the same program.

## Part 2: Strings with Escapes (scaffolded)

2a. Add a `STRING` token for double-quoted strings without escapes.

2b. Extend it to support the escapes `\"`, `\\`, `\n`, and `\t`, with the *decoded* text stored in the token (the lexeme `"a\nb"` carries a real newline in its value field; keep the raw lexeme too).

2c. An unterminated string must produce a lexical error pointing at the opening quote's line and column, not at end of file.

## Part 3: Configuration

3a. Move the token specification to a JSON file (list of `[name, pattern]` pairs, order significant), loaded at `Lexer` construction, with the comment character configurable. Validate the configuration on load (every pattern must compile) with located error messages.

3b. Demonstrate configurability: provide a second JSON specification in which the comment character is `//` and the assignment operator is `:=`, and show the same `Lexer` class tokenizing a program in that dialect. (Your December language is one configuration file away already.)

## Part 4: Errors and the Test Suite

4a. Implement both error modes: fail-fast (raise on first error, with line, column, and offending text) and collect-all (gather every lexical error in one pass and report together). The mode is a configuration option.

4b. Build the test suite: at least one test per token type, the maximal-munch cases (`<=`, `>=`, `==`, identifiers containing keywords like `iffy` and `whiles`), the string escape cases, and five deliberate error programs with their expected messages.

## Deliverables

Submit a ZIP containing your `Lexer` module, both JSON specifications, the test suite with its output, and a readme writeup of approximately one page documenting the interface for the parser author (who is future you). Ensure reproducibility by listing software version information.

## Reflection Prompts

- Which scanning rule (maximal munch or priority) caused you a real bug, and how did your tests catch it?
- What about your lexer would you change if your language used significant indentation like Python?
- If collaboration with a buddy was permitted, did you work with a buddy on this assignment? If so, who? If not, do you certify that this submission represents your own original work? Please identify any and all portions of your submission that were not originally written by you.
- Approximately how many hours it took you to finish this assignment (I will not judge you for this at all...I am simply using it to gauge if the assignments are too easy or hard)?
