---
layout: assignment
permalink: /Assignments/Automata
title: "CS374: Principles of Programming Languages - Finite Automata"


info:
  coursenum: CS374
  points: 100
  goals:
    - To map the control flow of a program using finite automata
  rubric:
    - weight: 60
      description: Algorithm Implementation
      preemerging: The algorithm fails on the test inputs due to major issues, or the program fails to compile and/or run
      beginning: The algorithm fails on the test inputs due to one or more minor issues
      progressing: The algorithm is implemented to solve the problem correctly according to given test inputs, but would fail if executed in a general case due to a minor issue or omission in the algorithm design or implementation
      proficient: A reasonable algorithm is implemented to solve the problem which correctly solves the problem according to the given test inputs, and would be reasonably expected to solve the problem in the general case
    - weight: 30
      description: Code Quality and Documentation
      preemerging: Code commenting and structure are absent, or code structure departs significantly from best practice, and/or the code departs significantly from the style guide
      beginning: Code commenting and structure is limited in ways that reduce the readability of the program, and/or there are minor departures from the style guide
      progressing: Code documentation is present that re-states the explicit code definitions, and/or code is written that mostly adheres to the style guide
      proficient: Code is documented at non-trivial points in a manner that enhances the readability of the program, and code is written according to the style guide
    - weight: 10
      description: Writeup and Submission
      preemerging: An incomplete submission is provided
      beginning: The program is submitted, but not according to the directions in one or more ways (for example, because it is lacking a readme writeup)
      progressing: The program is submitted according to the directions with a minor omission or correction needed, and with at least superficial responses to the bolded questions throughout
      proficient: The program is submitted according to the directions, including a readme writeup describing the solution, and thoughtful answers to the bolded questions throughout   
  questions:
    - "What states would represent each of the conditions in Part 1?  Hint: there are four of them - how many combinations of even/odd can you have for each character in the alphabet?"  
  
tags:
  - automata
  
---

The purpose of this assignment is to create and implement a finite automata in a computer program.

## Part 1: Defining the Finite Automata
Consider the language `S = {0, 1}, L = { w = strings of S* such that count(0) % 2 == 1 and count(1) % 2 == 1 }`.  In other words, there are an odd number of 0 and 1 characters in a `String` consisting of 1 and 0 characters of arbitrary length.

We can construct a finite state machine (FSM) from this definition.  Specifically, we'll use a Deterministic Finite Automata (DFA), although Non-Deterministic Fintie Automata (NFA) and regular expressions all recognize the same class of languages ("regular languages").

Go to the [FSM Simulator](http://ivanzuzak.info/noam/webapps/fsm_simulator/) and define your state machine for the language above.  Your accepting state will be the condition in which you know there are an odd number of 0 characters and an odd number of 1 characters.  Paste your resulting DFA into your readme document, or otherwise save and include it with your submission.

## Part 2: Implementing the Finite Automata
Write a program in a language of your choice that reads one character at a time from the terminal.  Do not keep track of the actual number of characters that you have read, nor how many of each character you have seen (finite state machines only store their current state, with no additional information!).  Instead, keep a variable that is equal to the state number that you are in.  You can use an `if` statement that checks whether each character is a 0 or a 1, and a nested `if` statement that checks which state you're in now.  The result of these conditionals should be to update the state number to another state.  When you're done reading the string from the console, print out whether or not you are in an accepting state at the end.

## Part 3: Practice Constructing Finite State Machines
Using the [FSM Simulator](http://ivanzuzak.info/noam/webapps/fsm_simulator/), construct some new finite state machines, which you can save and include with your submission.  For each finite state machine, assume a language L consisting of `String`s over `S*` given the alphabet `S = {0, 1}`.

1. All strings in which the character 0 always appears in pairs.  For example: `100111001` but not `1010010`.  The regular expression is: `(1*(00)*1*)*`.
2. All strings in which the count of the character 1 is a multiple of 3.  For example: `1001001` but not `100100`.  The regular expression is `(0*10*10*1)*0*`.

## Part 4: Limitations of Finite Automata
In your readme, describe why it is not possible to define a finite automata to balance parenthesis?  Hint: it has to do with the fact that the FSM can't store additional state, as we saw in Part 2!  This is the same reason why you cannot represent this language with a regular expression.
