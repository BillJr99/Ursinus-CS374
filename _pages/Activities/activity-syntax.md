---
layout: activity
permalink: /Activities/Syntax
title: "CS374: Programming Language Principles - Syntax and Semantics"


info: 
  goals: 
    - To explain the role of syntax in a programming language
    - To differentiate between syntax and semantics
  models:
    - model: |
        <a title="via Wikimedia Commons" href="https://commons.wikimedia.org/w/index.php?title=Special:Redirect/file/37_Auld_Lang_Syne.png"><img alt="Auld Lang Syne" src="https://commons.wikimedia.org/w/index.php?title=Special:Redirect/file/37_Auld_Lang_Syne.png"></a>
      title: "Semiotics: Signs and Symbols"
      questions:
        - "What word arrangements can you identify in this passage, or in general prose?"
        - "What are the general phrase structures that you can see?"
        - "What are the words of this language?"
        - "How about the musical notation?  What words, phrases, and structures are evident?"
    - model: |
        The quick brown fox jumped over the lazy dog.
        <br>
        They are flying kites.
      title: Semantics
      questions:
        - "What is the subject, verb, and direct object of the first sentence?"
        - "What is the subject and verb of the second sentence?  Is there a direct object?"
    - model: |
        <script type="syntaxhighlighter" class="brush: cpp"><![CDATA[
        public class Main {
            public static void main(String[] args) {
                float income = 60000;
                int age = 67;
                float taxrate = 0.12;
                
                if(income > 12000) 
                    if(age > 65) 
                        taxrate = 0.1;
                else
                    taxrate = 0.15;
                    
                // taxamount = taxrate * income;
            }
        }
        ]]></script> 
      title: Semantics in Programming
      questions:
        - "What is the general syntax of a variable declartaion?"
        - "What is the type of each variable in this program?  Is this idea part of the syntax or at a higher level of abstraction?  How does this relate to seeing a note on a music sheet versus playing a sound at a particular frequency?"
        - "What is the tax rate for a person age 20 with an income of 20000?  What should it be?"
        - "What type should <code>taxamount</code> be? How do you know?"
        
tags:
  - syntax
  
---

