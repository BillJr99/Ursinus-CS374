---
layout: activity
permalink: /Activities/BindingScope
title: "CS374: Programming Language Principles - Binding and Scope"


info: 
  goals: 
    - To define the various ways that names can be bound to items such as variables
    - To explain interpreter or compiler binding of types
    - To differentiate between strongly and weakly typed languages
    - To define variable scope
    - To relate scope to a function call stack
  models:
    - model: |
        <script type="syntaxhighlighter" class="brush: cpp"><![CDATA[
        #import <stdio.h>
        
        void foo() {
            int x = 10;
            
            // float x = 10.0; // what would happen here?
            
            x = x * 2;
        }
        
        int main(void) {
            int x = 5;
            
            foo();
            
            printf("%d\n", x);
        }
        ]]></script> 
      title: Binding
      questions:
        - "Can <code>foo</code> be re-assigned at runtime?  Would you say that it is statically or dynamically bound to its value?  How about <code>x</code>?"
        - "Do you think this is true of every language?"
        - "What do you suppose is the difference between <strong>lexical scope</strong> and <strong>dynamic scope</strong>?"
        - "How many bindings are there of the identifier <code>x</code>?  If <code>x</code> is staically bound, it must be resolved by the compiler at compile time.  How is the correct value obtained at each reference?" 
        - "What would happen if <code>x</code> is re-declared in <code>foo</code> after it has already been declared in languages like C and Java that specify and insist on proper types (these are called strongly typed languages)?"
    - model: |
        <script type="syntaxhighlighter" class="brush: cpp"><![CDATA[
        struct symbol {
            // What goes here?
        };
        ]]></script> 
        <br>
        <script type="syntaxhighlighter" class="brush: cpp"><![CDATA[
        const int TYPE_IVAL = 0;
        struct symbol* symboltable = NULL;

        struct symbol* putsymbol(char* name, int type) {
            struct symbol* sym = (struct symbol *) malloc(sizeof(struct symbol));
            sym->type = type;
            sym->name = malloc(strlen(name)+1);
            strncpy(sym->name, name, strlen(name)+1);

            if(type == TYPE_IVAL) {
                sym->value.ival = 0;
            }
            
            sym->next = symboltable;
            symboltable = sym;
            
            return sym;
        }
        
        struct symbol* getsymbol(char* name) {
            struct symbol* p = symboltable;
            struct symbol* result = NULL;
            
            while(p != NULL) {
                if(strcmp(p->name, name) == 0) {
                    // only catch the first instance, since newer items are placed in the front of the list
                    if(result == NULL) {
                        result = p;
                    }
                    
                    break;
                }
            }
            
            return result;
        }
        ]]></script> 
      title: Tracking Bindings
      questions:
        - "What kinds of information are needed to specify a bound symbol?"    
        - "What kind of data structure would enable a dynamic number of bound variables in a routine?"
        - "What revisions are needed to support additional data types?"
        - "What revisions are needed to support scope, so that variables of the same name can exist in subroutines?"
    - model: |
        <script type="syntaxhighlighter" class="brush: cpp"><![CDATA[
        int max(int a, int b) {
            if(a < b) {
                return b;
            } else {
                return a;
            }        
        }
        
        float max(float a, float b) {
            if(a < b) {
                return b;
            } else {
                return a;
            }
        }
        ]]></script> 
      title: Binding Functions
      questions:
        - "How can polymorphism work in a statically bound language?  How might this differ from a dynamically bound language?"
    - model: |
        <script type="syntaxhighlighter" class="brush: cpp"><![CDATA[
        /* From https://en.wikipedia.org/wiki/Virtual_function */
        class Animal {
         public:
          // Intentionally not virtual:
          void Move(void) {
            std::cout << "This animal moves in some way" << std::endl;
          }
          virtual void Eat(void) = 0;
        };

        // The class "Animal" may possess a definition for Eat if desired.
        class Llama : public Animal {
         public:
          // The non virtual function Move is inherited but not overridden.
          void Eat(void) override {
            std::cout << "Llamas eat grass!" << std::endl;
          }
        };        
        ]]></script> 
      title: Virtual Inheritance
      questions:
        - "A call to <code>x->Eat()</code>, where <code>x</code> is of type <code>Animal</code> but refers to a <code>Llama</code>, would output what?"
        - "How would this differ if <code>Eat</code> was not virtual, and implemented in the class <code>Animal</code>?"
        
tags:
  - binding
  - scope
  
---

