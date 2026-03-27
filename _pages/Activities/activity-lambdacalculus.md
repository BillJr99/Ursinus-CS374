---
layout: activity
permalink: /Activities/LambdaCalculus
title: "CS374: Programming Language Principles - The Lambda Calculus"


info: 
  next: ./LambdaCalculus2
  goals: 
    - To relate the Lambda calculus to the Turing Machine abstraction, and to describe their equivalence
    - To derive boolean expressions using the Lambda Calculus and beta-reductions
  models:
    - model: |
        <code>&lambda;x.x</code>
      title: Lambda Calculus
      questions:
        - "The first statement defines a parameter called <code>x</code> and returns <code>x</code>. What does <code>(&lambda;x.x)y</code> do?"
    - model: |
        <code>true = &lambda;xy.x</code><br>
        <code>false = &lambda;xy.y</code><br>
        Here, <code>x</code> and <code>y</code> are <strong>bound variables</strong>.  Variables that appear in the lambda expression that are not defined are referred to as <strong>free</strong> variables.
      title: Fundamental Constructs with the Lambda Calculus
      questions:
        - "In your own words, what does it mean for something to be true in the lambda calculus, when choosing between two alternative parameters?"
    - model: |
        <div align="left">
        <div>
        <code>not x = &lambda;x.x false true</code><br>
        <code>not x = (&lambda;x.x false true) true</code><br>
        Now, substitute <code>true</code> for <code>x</code>:<br>
        <code>not x = (true false true)</code><br>
        Substitute <code>&lambda;xy.x</code> for <code>true</code>:<br>
        <code>not x = (&lambda;xy.x false true)</code><br>
        Given two parameters, select the first one, where the parameters are <code>x = true</code>, <code>y = false</code>:
        <code>not true = false</code>
        </div>
        <br>
        <div>
        <code>equals(x, y) = &lambda;xy.???</code><br>
        Apply one of the parameters to see if it expands to <code>true</code> or <code>false</code>:<br>
        <code>equals(x, y) = &lambda;xy.x ???</code><br>
        If <code>x</code> is <code>true</code>, then they are equal if <code>y</code> is <code>true</code>, and <code>false</code> otherwise.  In other words, the value of <code>y</code> is the result.<br>
        <code>equals(x, y) = &lambda;xy.xy ???</code><br>
        Otherwise, <code>x</code> is <code>false</code>, and so the result is <code>true</code> if <code>y</code> is also <code>false</code>; in other words, the result is <code>not y</code>.<br>
        <code>equals(x, y) = &lambda;xy.xy not y</code><br>
        Which we can expand from our prior definition:
        <code>equals(x, y) = &lambda;xy.xy y false true</code><br>
        Which we expand again to substitute our definitions for <code>true</code> and <code>false</code>:
        <code>equals(x, y) = &lambda;xy.xy y &lambda;xy.y &lambda;xy.x</code><br>
        These substitutions are called <strong>beta-reductions</strong>.
        </div>
        <br>
        <div>
        <code>and(x, y) = y</code> when <code>x = true</code>, and <code>false</code> if <code>x = false</code>.<br>
        <code>&lambda;xy.xy false</code><br>
        Note that when <code>x = true</code>, this corresponds to choosing the first of the two following parameters (<code>y</code> and <code>false</code>) to resolve the boolean expression to <code>y</code>.  When <code>x = false</code>, we choose the second of the two following parameters, and obtain <code>false</code>.<br>
        Finally, substitute <code>&lambda;ab.b</code> for <code>false</code>.
        <code>&lambda;xy.xy &lambda;ab.b</code>
        </div>
        </div>
      title: Boolean Constructions with the Lambda Calculus
      questions:
        - "Verify the behavior of <code>not false</code> using the lambda expression above."     
        - "All boolean expressions can be constructed using the <code>NAND</code> operator.  What is the lambda expression for <code>NAND</code>, which is <code>(NOT AND x y)</code>?" 
        - "Derive the boolean expression for <code>A OR B</code>, given that <code>A OR B</code> is <code>true</code> when <code>A</code> is <code>true</code>, and <code>B</code> otherwise." 
        - "Draw a truth table for the <code>XOR</code> operator.  What is the result when <code>A</code> is <code>true</code>?  How about when <code>A</code> is <code>false</code>?  Derive the lambda expression for <code>XOR</code>."
        - "Draw a truth table for the <code>equals</code> operator.  What is its boolean expression?  Derive its lambda expression."         
  additional_reading:
    - title: "Lambda Calculus"
      link: "https://plato.stanford.edu/entries/lambda-calculus/"
    - title: "Lambda Calculus Notes"
      link: "http://www.cs.unc.edu/~stotts/723/Lambda/"
    - title: "A Tutorial Introduction to the Lambda Calculus"
      link: "https://personal.utdallas.edu/~gupta/courses/apl/lambda.pdf"
        
tags:
  - lambdacalculus
  
---

