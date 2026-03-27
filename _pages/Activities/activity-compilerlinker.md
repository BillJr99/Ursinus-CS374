---
layout: activity
permalink: /Activities/CompilerLinker
title: "CS374: Programming Language Principles - The Compilation and Linking Processes"


info: 
  goals: 
    - To describe the compilation process
    - To define an algorithm to resolve linker dependencies using a multi-pass approach
    - To define possible outcomes of the compilation process, including assembly code, machine code, and intermediate bytecode
    - To describe the role of external libraries in extending the functionality of a programming language and the mechanisms for integrating them
  models:
    - model: |
        <script type="syntaxhighlighter" class="brush: cpp"><![CDATA[
        // file1.c
        double x; 
        
        void a() {
            x = 3.14;
        }
        ]]></script> 
        <br>
        <script type="syntaxhighlighter" class="brush: cpp"><![CDATA[
        // file2.c
        int x = 5;
        
        void b() {
            x = 10;
        }
        ]]></script>
      title: Linker Processes
      questions:
        - "Assume that we compile with <code>gcc file1.c file2.c</code>.  What does the compiler have to do with the variable <code>x</code> in <code>file1.c</code>, since it does not yet know here the variable is declared?"
        - "With what is the variable <code>x</code> updated in <code>file1.c</code> once it can resolve it to <code>int x</code> in <code>file2.c</code>?"
        - "What does the assignment in <code>a()</code> do to the variable in <code>file2.c</code>?"
        - "What if there was a variable in <code>file2.c</code> called <code>a</code>?"
        - "What would happen if the variable <code>x</code> in <code>file1.c</code> was also initialized to a value when it was first declared?"
        - "Under what circumstances do you think a variable is bound to a global, versus a linker error?"
        - "In the C language, what do you think the <code>static</code> keyword does?  How can we use this to protect global variables inside externally linked library functions?"
  additional_reading:
    - title: "Bryant and O'Hallaron Notes on Compiling and Linking"
      link: "https://www.cs.cmu.edu/afs/cs/academic/class/15213-s16/www/lectures/12-linking.pdf"
    - title: "Java Bytecode"
      link: "https://en.wikipedia.org/wiki/Java_bytecode"
    - title: "LLVM Intermediate Representation"
      link: "https://llvm.org/docs/LangRef.html"
      
tags:
  - compiler
  - linker
  - bytecode
  
---

