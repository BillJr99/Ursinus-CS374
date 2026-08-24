---
layout: default-standard
permalink: /Tutorials/
title: "CS374: Tutorials Shelf"
---

# The Tutorials Shelf

These tutorials are where you go for depth on your own schedule.  They are worked paths, toolchain guides, and companions to the assignments and the Team Language Project.  Most are invitations rather than requirements; a few (marked *anchors required work*) are the reference behind a required assignment step or reading, and the assignment itself always contains the full instructions.

## Companions to the Assignments

- [Parser Combinators: Parsers as First-Class Values](ParserCombinators): companion to Recursive Descent Parsing
- [Grammars in Python](GrammarsInPython): CFGs as dictionaries, left-recursion detection, parse trees as data, a derivation tracer, and an ambiguity detector
- [Your Course Development Environment: Docker, Git, and GitHub](DevEnvironment), *anchors required work*, the recommended setup route in the Overview assignment: the course container, a GitHub-backed workspace, and the commit/push workflow
- [Build an Interpreter](BuildAnInterpreter): start-to-finish companion for the Tree-Walking Interpreter assignment
- [Type Inference: Implementing Hindley-Milner](TypeInference): companion to the Interpreter assignment's type-checking direction
- [Property-Based Testing Your Language with Hypothesis](PropertyBasedTesting), *anchors required work*, companion to the Parser (Step 3e) and Interpreter (Step 2e) property-based-testing requirements
- [Typing Disciplines: Strong vs. Weak, Static vs. Dynamic, and Gradual Typing](TypingDisciplines), *anchors required work*, required reading for the Type Systems unit
- [Prolog in the Browser with SWISH](Prolog): companion to the Functional assignment's Logic Programming direction (Direction F)
- [Scheme Essentials](SchemeEssentials): companion to the Functional Programming with Scheme assignment, covering the one syntax rule, list recursion, higher-order functions, and closures
- [Haskell Essentials](HaskellEssentials): companion to the Functional Programming unit
- [Build a Lambda Calculus Reducer](LambdaCalculusReducer): companion to the Lambda Calculus unit
- [Flex and Bison, Complete](FlexAndBison): companion to the generator-toolchain directions of the Lexer and Parser assignments

## Companions to the Team Language Project

- [The Project Language Guide](ProjectLanguageGuide): a complete worked path for the team project
- [A Syntax Highlighter for Your Language with tree-sitter](SyntaxHighlighter): an editor-support extension (tree-sitter grammar + VS Code highlighting, optional diagnostic) with big Demo-Day payoff
- [CI and TDD for Interpreters](CITDDForInterpreters): test suites, GitHub Actions, and coverage for your language
- [Shell Skills for Language Development](ShellForLanguageDev): run, test, and debug confidently from the command line
- [Publishing Your Language: pip, npm, and Docker](PublishingYourLanguage): release hardening and distribution
- [ShipIt: Repo Hygiene, README, Packaging, and Your Portfolio]({{ site.baseurl }}/Projects/TeamLanguage#shipping-your-language-the-shipit-checklist), *anchors required work*, the self-check scored within the project's Documentation and Reproducibility dimension
- [Demo Day Guide: External Guests and Technical Interview Practice]({{ site.baseurl }}/Projects/TeamLanguage#demo-day-external-guests-and-technical-interview-practice): presenting to guests, and the final-sprint-studio mock-interview rehearsal
- [Build a Bytecode VM](BytecodeVM): a compilation-target extension for ambitious teams
- [From AST to Code: Visitors and Transpilers](ASTToCode): expression-oriented design, the Visitor pattern, and transpiling your AST to Python, JavaScript, and Haskell (with source maps)
- [Coroutines and Generators: Pausable Computation](CoroutinesAndGenerators): `yield`, `send`, and `async`/`await` from first principles, ending with generator objects in your interpreter
- [Error Handling: From Return Codes to Algebraic Effects](ErrorHandling): design your language's error story: return codes, exceptions, Option/Maybe, and Result/Either
- [Garbage Collection: Implementing Memory Management](GarbageCollection): a runtime extension for the project
- [Compiling and Linking: From Source to Executable](CompilingAndLinking): what happens below your interpreter
- [Advanced C++ for Language Implementers](AdvancedCpp): for teams implementing in C++
