---
layout: activity
permalink: /Activities/Grammars2
title: "CS374: Programming Language Principles - Grammars"


info: 
  prev: ./Grammars
  
  goals: 
    - To disambiguate a grammar
  models:
    - model: |
        <script type="syntaxhighlighter" class="brush: cpp"><![CDATA[
         selection-statement:
              IF ( expression ) statement
            | IF ( expression ) statement ELSE statement
            
        open_statement: IF '(' expression ')' statement
                      | IF '(' expression ')' closed_statement ELSE open_statement
                      ;

        closed_statement: non_if_statement
                        | IF '(' expression ')' closed_statement ELSE closed_statement
                        ;

        non_if_statement: ...
                        ;
        ]]></script> 
      title: "Ambiguous Grammars"
      questions:
        - "How might <code>selection-statement</code> lead to a dangling else block ambiguity in a nested if statement?"
        - "When your parser reaches en <code>ELSE</code> token, should it resolve the prior <code>IF</code> statement or continue parsing as part of this inner nested <code>IF</code> clause?  This is known as a <strong>shift-reduce</strong> conflict."
        - "How is the ambiguity resolved using the <code>open_statement</code> instead?"
    - model: |
        <script type="syntaxhighlighter" class="brush: cpp"><![CDATA[
        E: N
        E: E + E
        E: E * E
        E: (E)
        N: [0-9]+        
        ]]></script> 
      title: "An Example Grammar with an Ambiguity"
      questions:
        - "What are two different ways in which the expression <code>8*9+5</code> can be parsed into a parse tree?  What does each parse tree look like?  This is another example of a shift-reduce conflict resulting from an ambiguous grammar."
        - "Can the resulting computed values be different as a result of this ambiguity?"
        - "How can we resolve this ambiguity?"
    - model: |
        <script type="syntaxhighlighter" class="brush: cpp"><![CDATA[
          E: T + E
              | T
          T: F * T
              | F
          F: N
              | (E)
          N: [0-9]+       
        ]]></script> 
      title: "An Example Grammar without an Ambiguity"
      questions:
        - "How would the expression <code>8*9+5</code> be parsed into a parse tree?  How about <code>5+8*9</code>?  Draw each parse tree."
        - "Traditional order-of-operations dictates that division and multiplication resolve prior to addition and subtraction.  Where does the multiplication occur within this parse tree, and why is this position important to ensure that these operators resolve prior to the addition?"
        - "Given an ambiguous grammar, is there an algorithm that can disambiguate it, or do we have to design against the ambiguity up front?  Why or why not?"
  additional_reading:
    - title: "Formal Languages Notes"
      link: "https://www.cs.ru.nl/~herman/onderwijs/2016TnA/lecture7.pdf"
      
tags:
  - grammar
  
---

