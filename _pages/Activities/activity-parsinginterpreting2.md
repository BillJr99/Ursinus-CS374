---
layout: activity
permalink: /Activities/ParserInterpreter2
title: "CS374: Programming Language Principles - Parsers and Interpreters"


info: 
  prev: ./ParserInterpreter
  next: ./ParserInterpreter3
  goals: 
    - To explain the limitations of an LL(1) parser
    - To remove left recursion and to left factor a grammar for LL(1) parsing, where possible
  models:
    - model: |
        <script type="syntaxhighlighter" class="brush: cpp"><![CDATA[
        S -> aS 
        S -> aaS
        ]]></script>
      title: "Limitations of LL(1) parsers: unique first productions and left factoring"
      questions:
        - "Consider each nonterminal as a function call in a recursive descent parser.  Why is this grammar difficult to parse with an LL(1) parser?"
        - "How might we fix this grammar?"
        - "Draw a state machine representing the parse rules of this grammar, and describe the limitations in terms of the state machine."
    - model: |
        <script type="syntaxhighlighter" class="brush: cpp"><![CDATA[
        S -> Ax
        A -> By
        B -> Az
        ]]></script>
      title: "Limitations of LL(1) parsers: no left recursion"
      questions:
        - "Consider each nonterminal as a function call in a recursive descent parser.  Why is this grammar difficult to parse with an LL(1) parser?"
        - "How might we fix this grammar?"
        - "Draw a state machine representing the parse rules of this grammar, and describe the limitations in terms of the state machine."        
    - model: |
        <script type="syntaxhighlighter" class="brush: cpp"><![CDATA[
         /*
          expr: term expr2
          expr2: (addsub term)*
          term: factor term2
          term2: muldiv term | null
          factor: num
                | "(" expr ")"
          addsub: "+" | "-"
          muldiv: "*" | "/"
          num: [0-9]+
         */
        ]]></script> 
      title: "An Alternative Grammar"
      questions:
        - "What is different about this grammar from the original one?"
  additional_reading:
    - link: https://tldp.org/HOWTO/Lex-YACC-HOWTO.html
      title: Lex and YACC primer
      
tags:
  - parser
  - interpreter
  
---

