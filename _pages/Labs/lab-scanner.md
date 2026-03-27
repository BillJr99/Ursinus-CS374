---
layout: assignment
permalink: /Labs/Scanner
title: "CS374: Principles of Programming Languages - Scanners"


info:
  coursenum: CS374
  points: 100
  goals:
    - To create a lookahead scanner to identify lexemes in an input text
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
  readings:
    - rtitle: "Scanning Activity"
      rlink: "../Activities/TokensScanning"    
  
tags:
  - scanner
  
---

The purpose of this lab is to implement a scanner that returns a set of predefined tokens.  To do this, write a program that defines a number of constants representing the types of tokens you wish to return.  Then, read from standard input a set of text.  As you read each character of text, determine if it represents one of the tokens, continuing to read until you have identified a token.  When you find that token, add the entire `String` and the token type to a data structure, and append them to an array.  

When you are done, write a function called `getToken` that returns the next item in the array.  Iterate over the entire array and print the set of words and token ID numbers to the screen.

The set of tokens that you decide to implement is up to you, and you can be creative about this.  You should support at least one reserved word, at least one numeric token, at least one operator (*i.e.*, `=`), and at least one textual identifier.