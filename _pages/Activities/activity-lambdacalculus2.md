---
layout: activity
permalink: /Activities/LambdaCalculus2
title: "CS374: Programming Language Principles - The Lambda Calculus"


info: 
  prev: ./LambdaCalculus
  next: ./LambdaCalculus3
  goals: 
    - To derive numeric and recursive structures using the Lambda Calculus, beta-reductions, and the Y Combinator
  models:
    - model: |
        <div align="left">
        <code>let 0 = &lambda;n(&lambda;z.z)</code><br>
        <code>let 1 = &lambda;nz.n(z)</code><br>
        <code>let 2 = &lambda;nz.n(n(z))</code><br>
        <code>...</code><br>
        <code>successor(n) = &lambda;wyx.y(wyx) (n)</code><br>
        <code>successor(0) = &lambda;wyx.y(wyx) (0) = &lambda;wyx.y(wyx) (&lambda;nz.z) = &lambda;nz.n(z) = 1</code><br>
        <code>mul(x, y) = &lambda;xyz.x(yz)</code><br>
        <code>mul(3, 2) = &lambda;xyz.x(yz) 3 2 = &lambda;z.3(2z) = 6</code>
        </div>
      title: "Arithmetic with the Lambda Calculus"
      questions:
        - "How might you define addition using the successor function?"  
    - model: |
        <div align="left">
        <code>Y = &lambda;f.(&lambda;x.f(x x)) (&lambda;x.f(x x))</code><br>
        <code>Y g = &lambda;f.(&lambda;x.f(x x)) (&lambda;x.f(x x)) g</code><br>
        <code>Y g = (&lambda;x.g(x x)) (&lambda;x.g(x x))</code><br>
        <code>Y g = g ((&lambda;x.g(x x)) (&lambda;x.g(x x)))</code><br>
        <code>Y g = g (Y g)</code>
        </div>
      title: "Recursion and the Y Combinator"
      questions:
        - "How can this model be extended to support recursive procedures?"          
        
tags:
  - lambdacalculus
  
---

