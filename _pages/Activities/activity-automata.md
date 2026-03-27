---
layout: activity
permalink: /Activities/Automata
title: "CS374: Programming Language Principles - Finite Automata"


info: 
  goals: 
    - To define a finite state machine 
    - To relate a finite state machine to the grammar definition of a programming language
  models:
    - model: |
        <code>(A+B)*ABAB</code>
      title: Finite Automata
      questions:
        - "Design a flow chart that reads one character at a time until the sequence <code>ABAB</code> is found."
        - "Using the FSM Designer, draw a finite state machine that accepts the strings in the given by the regular language."
        - "Using the FSM simulator, implement the finite state machine to check and accept the appropriate strings in this language."
        - "Can you determine how many extraneous A and B characters were seen before reaching the accepting state?  If not, what additional information would be needed to do so?"
        - "How does a finite state machine relate to a regular expression?"
        - "What do finite automata have to do with programming languages?  Specifically, how can they help us to connect syntax with semantics?"
        - "Why would it be difficult to design a finite state machine to accept all strings of <code>A</code> and <code>B</code> such that the number of <code>A</code> and <code>B</code> characters are equal?  If it were possible to design such a machine, what would be the corresponding regular expression?"
    - model: |
        <a href="https://docs.oracle.com/cd/A87860_01/doc/appdev.817/a77069/11_ele58.gif"><img alt="Oracle SQL Flowchart" src="https://docs.oracle.com/cd/A87860_01/doc/appdev.817/a77069/11_ele58.gif"></a>
      title: SQL SELECT Language Automata
      questions:
        - "What language is described by this automaton?" 
  additional_reading:
    - title: "FSM Designer"
      link: "http://madebyevan.com/fsm/"
    - title: "FSM Simulator"
      link: "http://ivanzuzak.info/noam/webapps/fsm_simulator/"
      
tags:
  - automata
  
---

