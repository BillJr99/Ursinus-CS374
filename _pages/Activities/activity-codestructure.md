---
layout: activity
permalink: /Activities/CodeStructure
title: "CS374: Programming Language Principles - Code Structure"


info: 
  goals: 
    - To explain the programming language constructs of expressions
    - To explain the programming language constructs of conditionals
    - To explain the programming language constructs of functions
    - To explain the programming language constructs of exceptions
    - To relate complex data structures to their position in memory and pointer- or reference-based representation in memory
  models:
    - model: |
        <script type="syntaxhighlighter" class="brush: cpp"><![CDATA[
        int x = 5;
        
        x = x + 1;
        
        if(x == 6) {
            x = printf("%d\n", x); // is this legal?  
        }
        
        // x + 1 = x;
        ]]></script> 
      title: Assignment Expressions
      questions:
        - "In what contexts do you see <code>x</code> being used in this program?  How about the equals sign?"
        - "Why is there a <code>=</code> in some instances but a <code>==</code> in others?  What would happen if the <code>x == 6</code> were replaced with <code>x = 6</code>?  How does this compare to other languages?"
        - "Which <code>x</code> variable uses would be referred to as l-vals, and which as r-vals?"
    - model: |
        <script type="syntaxhighlighter" class="brush: cpp"><![CDATA[
        int[] heights = {48, 42, 65, 58};
        
        int& height(int i) {
            return heights[i];
        }
        
        int main() {
            height(1) = 44; // person 1 grew!  Is this legal?
        }
        ]]></script> 
      title: "l-val and r-val Semantics"
      questions:
        - "In what contexts is heights an l-val, and in which is it an r-val?"
        - "What does the ampersand mean in this program?"
    - model: |
        <script type="syntaxhighlighter" class="brush: cpp"><![CDATA[
        int main() {
            int x = 5;
            
            if(x < 10) {
                x = x + 1;
            } else {
                x = x - 1;
            }
        }
        ]]></script> 
      title: "Conditionals"
      questions:
        - "Rewrite this code using only <code>GOTO</code> statements for the body of the <code>if</code> and <code>else</code> clauses, like in BASIC."
        - "Which structure do you prefer and why?"
    - model: |
        <script type="syntaxhighlighter" class="brush: cpp"><![CDATA[
        public class Driver {
            public static void main(String[] args) {
                ArrayList<String> people = new ArrayList<String>();
                
                // populate with Strings...
                
                Iterator i = people.iterator();
                
                while(i.hasNext()) {
                    String person = i.next();
                    System.out.println(person);
                }
            }
        }
        ]]></script> 
      title: "Iteration"
      questions:
        - "Re-write this loop with a traditional counter loop.  How might this work using <code>GOTO</code> structures?"
    - model: |
        <script type="syntaxhighlighter" class="brush: cpp"><![CDATA[
        int main() {
            // suppose this returns some pointer that might be NULL
            // and that ListNode is a traditional linked list node
            struct ListNode* ptr = getHead(); 
            
            // Suppose getNext(ListNode* x) returns x->next
            if(ptr != NULL && getNext(ptr) == NULL) {
                printf("I am the only element in this list!\n");
            }
        }
        ]]></script> 
      title: "Functions and Evaluation Strategies"
      questions:
        - "In C, what would happen if <code>ptr</code> is <code>NULL</code>?  Would this program fail?"
        - "From context, what do you think lazy evaluation means?"
        - "Would this outcome be different in an eager evaluation language?"
    - model: |
        <script type="syntaxhighlighter" class="brush: cpp"><![CDATA[
        # From https://wiki.python.org/moin/Generators
        # explicitly write a generator function
        def double(L):
            for x in L:
                yield x*2
        
        # eggs will be a generator
        eggs = double([1, 2, 3, 4, 5])
        
        # the above is equivalent to ("generator comprehension"?)
        eggs = (x*2 for x in [1, 2, 3, 4, 5])
        
        # need to do this if you need a list
        eggs = list(double([1, 2, 3, 4, 5]))
        
        # the above is equivalent to (list comprehension)
        eggs = [x*2 for x in [1, 2, 3, 4, 5]]
        ]]></script> 
      title: "Generator Functions"
      questions:
        - "What, in your own words, does a generator do?"
        - "What do you think are the advantages of using a generator as opposed to creating and returning a list?"
        - "In Python 2, <a href=\"https://www.geeksforgeeks.org/range-vs-xrange-python/\">create a list</a> using <code>range(N)</code> for some large value of <code>N</code>.  Use <code>sys.getsizeof()</code> to get the size of the list you create, and print it to the screen.  Now, repeat this with the <code>xrange(N)</code> function.  How do they compare, and how might you account for the difference?"
    - model: |
        <script type="syntaxhighlighter" class="brush: cpp"><![CDATA[
        ; https://www.cs.trinity.edu/~jhowland/ccsc98/ccsc98/node5.html
        ; scheme < fact.scm

        (define factorial
          (lambda(n)
            (if (= n 0)
              1
              (* n (factorial (- n 1))))))
              
        (factorial 5)        
        ]]></script> 
      title: "Recursive Functions"
      questions:
        - "What do you think is meant by tail recursion?"
        - "Define a recursive approach to find the last item in a list in Scheme.  Note that <code>(if (null? (cdr l))</code> asks if the <code>cdr</code> of list <code>l</code> is <code>null</code>."
        - "Is each call to <code>factorial</code> distinct?  In other words, what is each value of <code>n</code> in each function call?  Based on this, what do you think is the difference between pass-by-reference and pass-by-value in a function call?"
    - model: |
        <script type="syntaxhighlighter" class="brush: cpp"><![CDATA[
        (define (fibonacci n)
            (if (<= n 2)
                1
                (+ (fibonacci (- n 1)) (fibonacci (- n 2)))
            )
        )
        ]]></script> 
      title: "Lazy and Eager Evaluation"
      questions:
        - "How many times is <code>fibonacci(2)</code> called if the initial call was to <code>fibonacci(3)</code>?"
        - "How many times does <code>fibonacci(2)</code> really need to be called?  What could we do to help ensure that this happens?"
    - model: |
        <script type="syntaxhighlighter" class="brush: cpp"><![CDATA[
        #include <stdio.h>
        #include <stdlib.h>
        
        int main() {
            int* x = (int*) malloc(10000000000000*sizeof(int));
            
            if(x == NULL) {
                perror("malloc");
                printf("%d\n", errno);
            }
            
            // printf("%d\n", 5 / 0); // what would happen?
        }
        ]]></script> 
      title: "Old Fashioned Exceptions"
      questions:
        - "What is the value of <code>x</code> if <code>malloc</code> fails?"
        - "What do you think <code>perror</code> does?"
        - "What is <code>errno</code>?"
        - "What would happen if a second syscall fails before checking the value of <code>errno</code>?  Based on this, what can you say about the variable <code>errno</code>?"
        - "In what ways can the <code>read</code> syscall fail?"
        - "What would happen if you divided by 0 in C?"
    - model: |
        <script type="syntaxhighlighter" class="brush: cpp"><![CDATA[
        try:
            foo()
        catch SomeError:
            print("SomeError occurred")
        catch SomeOtherError:
            print("SomeOtherError occurred")
        catch:
            print("Any other type of error occurred")
        ]]></script> 
      title: "Explicit Exception Handling"
      questions:
        - "How might you use this structure to recover and proceed when an exception occurs?"
        - "What might you do if you encounter an exception from which you cannot recover?"
    - model: |
        <script type="syntaxhighlighter" class="brush: cpp"><![CDATA[
        public class Driver {
            public double doSomething(int x) throws Exception {
                if(x == 0) {
                    throw new Exception("Can't divide by 0!");
                }
                
                return 10.0 / x;
            }
            
            public static void main(String[] args) {
                try {
                    System.out.println(doSomething(0));
                catch(Exception e) {
                    Sytstem.out.println(e.getMessage());
                    e.printStackTrace();
                }
            }
        }
        ]]></script> 
      title: "Throwing Exceptions"
      questions:
        - "How can this approach be used to enforce preconditions?"
    - model: |
        <script type="syntaxhighlighter" class="brush: cpp"><![CDATA[
        public class Driver {
            public double doSomething(int x) {
                ArrayList<String> x = new ArrayList<String>();
                
                // work with x
            }
            
            public static void main(String[] args) {
                doSomething();
            }
        }
        ]]></script> 
      title: "Garbage Collection"
      questions:
        - "When is <code>x</code> discarded?"
        - "How does this differ from C++?"
        - "What are some strategies for determining when it is safe to garbage collect a variable?"
  additional_reading:
    - title: "BASIC Syntax Reference"
      link: "https://en.wikipedia.org/wiki/BASIC#Syntax"
    - title: "The <code>read</code> sycall"
      link: "https://man7.org/linux/man-pages/man2/read.2.html"
        
tags:
  - codestructure
  
---

