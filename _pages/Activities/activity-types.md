---
layout: activity
permalink: /Activities/Types
title: "CS374: Programming Language Principles - Data Types"


info: 
  goals: 
    - To explain the evolution of data types from a bit perspective
    - To explain the storage limitations of primitive data types
    - To compose primitive data types from bits
  models:
    - model: |
        <a title="Verpies, Public domain, via Wikimedia Commons" href="https://commons.wikimedia.org/wiki/File:BMPfileFormat.png"><img width="256" alt="BMPfileFormat" src="https://upload.wikimedia.org/wikipedia/commons/c/c4/BMPfileFormat.png"></a>
      title: "The Bitmap (BMP) File Format"
      questions:
        - "What types of primitives do you see in the BMP file format?"
    - model: |
        <a title="Vectorization:  Stannered, CC BY-SA 3.0 &lt;http://creativecommons.org/licenses/by-sa/3.0/&gt;, via Wikimedia Commons" href="https://commons.wikimedia.org/wiki/File:Float_example.svg"><img width="512" alt="Float example" src="https://upload.wikimedia.org/wikipedia/commons/d/d2/Float_example.svg"></a>
      title: "The IEEE754 Floating Point Standard"
      questions:
        - "What primitive data types do you see in this format?"
        - "What fields make up a single-precision floating point value?"
        - "What do you think changes to make a double-precision floating point value?"
        - "Why do you think floating point values suffer from rounding error?  How can we compare two floating point values?"
        - "What is the bit representation for an <code>int</code> with value 11?"
    - model: |
        <script type="syntaxhighlighter" class="brush: cpp"><![CDATA[
        struct Person {
            int age;
            char name[20];
        };
        
        int arr[4];
        int mat[3][4];
        ]]></script> 
      title: "Complex Types"
      questions:
        - "What is the bit level representation for the <code>Person</code> type (with arbitrary values)?"
        - "How would the representation change if <code>name</code> was a <code>char*</code> in the <code>Person</code> struct or record?  What is the advantage of this?"
        - "What is the bit level representation for the <code>arr</code> type (with arbitrary values)?  How about <code>mat</code> (specifically, are there 3 rows or 3 columns)?"
    - model: |
        <script type="syntaxhighlighter" class="brush: cpp"><![CDATA[
        (define square
          (lambda(n)
            (* n n)
          )
        )

        (define pow
          (lambda(n k)
            (if (= k 0)
              1
              (* n (pow n (- k 1)))
            )
          )
        )
              
        (square (pow 5 3))
        ]]></script> 
      title: "Weakly Typed Languages"
      questions:
        - "What is the type of <code>n</code>?  How about <code>pow</code>?"
        - "What are some weakly typed languages?"
    - model: |
        <script type="syntaxhighlighter" class="brush: cpp"><![CDATA[
        #include <stdlib.h>
        
        int main(void) {
            int x = 1/3;
            int* y = (int*) malloc(sizeof(int));
        }
        ]]></script> 
      title: "Strongly Typed Languages"
      questions:
        - "What is the type of <code>x</code>?  What is its value, and why?  How can we correct this to obtain the value we want?"
        - "Given that other languages would compute 1/3 to 0.33333..., how would you define the concept of type coercion?"
        - "What are some strongly typed languages?"
        - "What is the purpose of the <code>(int*)</code> clause in the <code>malloc</code> statement?  What does <code>malloc</code> actually return, and why?"
    - model: |
        <script type="syntaxhighlighter" class="brush: cpp"><![CDATA[
        /* From: https://en.wikipedia.org/wiki/Operator_overloading */
        Time operator+(const Time& lhs, const Time& rhs) {
          Time temp = lhs;
          temp.seconds += rhs.seconds;
          
          temp.minutes += temp.seconds / 60;
          temp.seconds %= 60;
          
          temp.minutes += rhs.minutes;
          temp.hours += temp.minutes / 60;
          
          temp.minutes %= 60;
          temp.hours += rhs.hours;
          
          return temp;
        }   
        ]]></script> 
      title: "Overloading Operators to Work with Complex Types in C++"
      questions:
        - "How might you use this to add two <code>Time</code> objects together?"
  additional_reading:
    - title: "Weakly and Strongly Typed Languages"
      link: "https://en.wikipedia.org/wiki/Strong_and_weak_typing#Variation_across_programming_languages"
        
tags:
  - types
  
---

