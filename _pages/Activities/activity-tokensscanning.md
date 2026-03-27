---
layout: activity
permalink: /Activities/TokensScanning
title: "CS374: Programming Language Principles - Tokens and Scanning Lexemes"


info: 
  goals: 
    - To define a lexeme and to define tokens based on lexemes
    - To differentiate between types, reserved words, and identifiers in a scanner
    - To read a file and identify defined tokens
  models:
    - model: |
        <script type="syntaxhighlighter" class="brush: cpp"><![CDATA[
        %option noyywrap       

        %{
        #include <stdio.h>

        #define YY_DECL int yylex()

        #include "calc.tab.h"

        %}

        %%

        [ \t]	                ; // ignore all whitespace
        [0-9]+		            {yylval.ival = atoi(yytext); return T_INT;}
        "+"		                {return T_PLUS;}
        "-"		                {return T_MINUS;}
        "*"		                {return T_MULTIPLY;}
        "/"		                {return T_DIVIDE;}
        "("		                {return T_LEFT;}
        ")"		                {return T_RIGHT;}
        \n                      {return T_NEWLINE;}

        %%

        // https://github.com/meyerd/flex-bison-example
        // noyywrap assumes that there are no additional files to be parsed
        ]]></script> 
      title: Scanning Lexemes for Tokens with flex
      questions:
        - "What is a lexeme?  What is a token?"
        - "Describe an algorithm to read a <code>String</code> from left to right, returning tokens as they are identified.  What familiar programming construct or paradigm do you see (hint - look at the loop, conditional, and check for the current character!)?"
        - "How would you modify this scanner configuration to support an assignment operator and an identifier (variable) token?"
        - "Notice the actual text of the token is not typically returned directly by the scanner.  Rather, it is stored in a variable (here, <code>yylval</code>).  What is returned instead, and why not simply return <code>yytext</code> directly?"
        - "Sketch the symbol table for the lexemes above.  For each token type, assign a constant value to the type, and describe the type and format of the resulting token value."
      
tags:
  - tokens
  - lexemes
  - scanner
  
---

