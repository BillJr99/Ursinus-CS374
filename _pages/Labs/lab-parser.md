---
layout: assignment
permalink: /Labs/Parser
title: "CS374: Principles of Programming Languages - Parsing"


info:
  coursenum: CS374
  points: 100
  goals:
    - To implement a recursive descent parser for a grammar
    - To use tools like lex to create a scanner for a given set of identifiers from a grammar
    - To use tools like yacc to create a parse table and parser for a grammar
  rubric:
    - weight: 60
      description: Algorithm Implementation
      preemerging: The algorithm fails on the test inputs due to major issues, or the program fails to compile and/or run
      beginning: The algorithm fails on the test inputs due to one or more minor issues
      progressing: The algorithm is implemented to solve the problem correctly according to given test inputs, but would fail if executed in a general case due to a minor issue or omission in the algorithm design or implementation
      proficient: A reasonable algorithm is implemented to solve the problem which correctly solves the problem according to the given test inputs, and would be reasonably expected to solve the problem in the general case
    - weight: 30
      description: Code Quality and Documentation
      preemerging: Code commenting and structure are absent, or code structure departs significantly from best practice, and/or the code departs significantly from the style guide
      beginning: Code commenting and structure is limited in ways that reduce the readability of the program, and/or there are minor departures from the style guide
      progressing: Code documentation is present that re-states the explicit code definitions, and/or code is written that mostly adheres to the style guide
      proficient: Code is documented at non-trivial points in a manner that enhances the readability of the program, and code is written according to the style guide
    - weight: 10
      description: Writeup and Submission
      preemerging: An incomplete submission is provided
      beginning: The program is submitted, but not according to the directions in one or more ways (for example, because it is lacking a readme writeup)
      progressing: The program is submitted according to the directions with a minor omission or correction needed, and with at least superficial responses to the bolded questions throughout
      proficient: The program is submitted according to the directions, including a readme writeup describing the solution, and thoughtful answers to the bolded questions throughout    
  readings:
    - rtitle: "Parsing Activity"
      rlink: "../Activities/ParserInterpreter"    
      
tags:
  - parser
  
---

The purpose of this labs is to implement a recursive descent parser for a simple LL(1) parser, and then to define a lex and yacc parser to create and parse according to a parse table.

## Part 1: Recursive Descent Parser

Consider our recursive descent parser for the following grammar:

```
expr: term (addsub term)*
term: factor muldiv term
    | factor
factor: num
      | "(" expr ")"
addsub: "+" | "-"
muldiv: "*" | "/"
num: [0-9]+
```

Which we implemented as follows \[[^1]\] \[[^2]\]:

### calc.c

```c
#include <stdio.h>
#include <ctype.h>
#include <stdlib.h>
#include <string.h>

int expr(void);
char token;

// remove the next character from the stream
char pop() {
    char ch = getchar();
    printf("Popped %c\n", ch);
    return ch;
}

// check the next character, but don't remove it from the stream
char peek() {
    char ch = pop();
    ungetc(ch, stdin);
    printf("Pushed %c\n", ch);
    return ch;
}

int readint() {
    int numchars = 0;
    char* val = (char*) malloc(1); // for the trailing \0
    
    token = peek();
    while(isdigit(token)) {
        pop(); 
        
        numchars = numchars + 1;
        val = (char*) realloc(val, numchars + 1); // for the trailing \0
        
        val[numchars-1] = token;
        
        token = peek();
    }
    
    val[numchars] = '\0'; // null terminate
    
    int result = atoi(val);
    
    printf("Read int from string %s (length %d): %d\n", val, strlen(val), result);
    
    free(val);
    
    return result;
}

int factor(void) {
    printf("In factor\n");
    
    int value;
    token = peek();

    if (token == '(') { // resolve parens as a whole new expression, resolving to a value, regardless of where they occur in the input (since they are highest precedence)
        pop(); // (
        value = expr();
        token = pop(); // )

        if(token != ')') {
            printf("Error parsing factor, imbalanced parenthesis\n");
            exit(-1);
        }
    } else if (isdigit(token)) {
        value = readint();
    } else {
        printf("Error parsing factor\n");
    }
    
    printf("Factor value: %d\n", value);

    return value;
}

int term(void) {
    printf("In term\n");
    
    // get the mandatory first factor
    int value = factor();
    token = peek();

    // now handle the optional second term
    // there is still a common left prefix that we can try to simplify with left factoring
    if(token == '*') {
        pop(); // *
        value *= term();       
    } else if(token == '/') {
        pop(); // /
        value /= term();
    } // these are optional in the grammar, so no error if this is not found    

    printf("Term value: %d\n", value);
    
    return value;
}

int expr() {
    printf("In expr\n");
    
    // Start with the first term
    int value = term();
    token = peek();

    // Handle all '+' and '-' operators iteratively
    while (token == '+' || token == '-') {
        if (token == '+') {
            pop(); // Consume '+'
            value += term(); // Evaluate the next term and add
        } else if (token == '-') {
            pop(); // Consume '-'
            value -= term(); // Evaluate the next term and subtract
        }
        token = peek();
    }

    printf("Expression value: %d\n", value);
    return value;
}

int main(void) {
    token = peek();
    int result = expr();
    printf("Result: %d\n", result);

    return 0;
}
```

Notice the `term` and `expression` nonterminals require left factoring in order to properly implement repeating expressions.  Revise the grammar to factor these common productions, and include your revised grammar with your submission.  Then, modify the example recursive descent parser to call your new nonterminals.

Your new grammar will look like this:

```
 expr: term expr2
 expr2: addsub expr | null
 term: factor term2
 term2: muldiv term | null
 factor: num
       | "(" expr ")"
 addsub: "+" | "-"
 muldiv: "*" | "/"
 num: [0-9]+

```

To do this, your `expr()` function will call `term` and then immediately call `expr2`.  Add these return values together and return that from `expr`!  If your `addsub` is a minus sign in `expr2`, you can return the negative of the value.  **What should you return if you get null, or in other words, neither a plus nor a minus?**  Repeat this process for `term`, being sure to return the correct values for multiply, divide, and neither (the identity).

## Part 2: A Calculator Parser with Variable Assignments

Consider our `flex` and `bison` scanner and parser definitions for a calculator grammar:

### calc.l
```
%option noyywrap       

%{
#include <stdio.h>

#define YY_DECL int yylex()

#include "calc.tab.h"

%}

%%

[ \t]	                ; // ignore all whitespace
[0-9]+		        {yylval.ival = atoi(yytext); return T_INT;}
"+"		        {return T_PLUS;}
"-"		        {return T_MINUS;}
"*"		        {return T_MULTIPLY;}
"/"		        {return T_DIVIDE;}
"("		        {return T_LEFT;}
")"		        {return T_RIGHT;}
\n                      {return T_NEWLINE;}

%%
```

### calc.y
```
%{

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

extern int yylex();
extern int yyparse();
extern FILE* yyin;

void yyerror(const char* s);

%}

%union {
    int ival;
}

%token<ival> T_INT
%token T_PLUS T_MINUS T_MULTIPLY T_DIVIDE T_LEFT T_RIGHT T_NEWLINE

%type<ival> expr term factor addsub
%start calc

%%

calc:                               
    | calc line                     

line: T_NEWLINE  
    | expr T_NEWLINE                { printf("%d\n", $1); } 

expr: term addsub                   { $$ = $1 + $2; }

addsub:
      { $$ = 0; }
    | T_PLUS term addsub            { $$ = $2 + $3; }
    | T_MINUS term addsub           { $$ = -$2 + $3; }

term: factor T_MULTIPLY term        { $$ = $1 * $3; }
    | factor T_DIVIDE term          { $$ = $1 / $3; }
    | factor                        { $$ = $1; }
    
factor: T_INT                       { $$ = $1; }
      | T_LEFT expr T_RIGHT         { $$ = $2; }
      
%%

int main() {
    yyin = stdin;
    
    do {
        yyparse();
    } while(!feof(yyin));
}

void yyerror(const char* s) {
    fprintf(stderr, "Parse error: %s\n", s);
    exit(1);
}
```

First, modify this scanner and parser to support floating point values instead of integer values.  You will modify your numeric token type to include an optional decimal point, and use the `atof` function to convert it to a floating point value.  You will also modify your types union in the parser to be a `float` type instead of an `int`.  Run your calculator with some test inputs to verify that it is working.  Don't forget to change your calls to `printf` to print `%f` instead of `%d`!

Now, we will modify the grammar to support variable assignments.  To do this, we will support new grammar productions that allow storing an expression into a variable defined by an identifier that you can retrieve like a numeric value.  We will also add a type to our types `union` whose type is a `char*` (the name of the identifier variable).  Create a new token called `T_ID` (the name is arbitrary!) whose lexeme is one or more alphabetical characters, and a new token called `T_ASSIGN` that is the lexeme `:=`.  You'll have two new productions: a new `line` of the form `T_ID T_ASSIGN expr line`, and a new `factor` production that resolves to `T_ID`.  The type of the `T_ID` token will be text, so you can set the token type of whichever `union` element you associated with the `char*`.  

In your scanner, you will add a new regular expression for an ID as follows, which returns the `T_ID` type, and copies the name of the variable into yylval.

```c
[a-zA-Z]+               {yylval.text = malloc(strlen(yytext)+1); strncpy(yylval.text, yytext, strlen(yytext)+1); return T_ID;}
```

Correspondingly, add a token into your parser as follows, right where you first defiend the T_INT token.  We'll define this one as text, assuming your union contains a `char* text` in addition to your numeric value.

```c
%token<text> T_ID
```

### Symbol Table

Let's add a symbol table linked list to the header definitions section of your parser file.  This will be a linked list of structures that contain a name, a type, and a value:

```c
struct symbol {
    char* name;
    int type;
    union {
        int ival; // change this to a float to support floats!
    } value;
    struct symbol* next;
};
```

If you encounter the assignment production, print the expression result like before, but now, also assign the value to the symbol table:

```c
struct symbol* sym = putsymbol($1, TYPE_IVAL); // use TYPE_FVAL if you are using float!
sym->value.ival = $3; // use fval if you are using float!
```

Your `factor: T_ID` production can retrieve this value from the linked list, and resolve to the value that it finds.  Since our example adds items to the list from the front, the most recent value is always bound to the symbol name.  So, you can return the first instance of the symbol.

This will enable you to execute expressions such as:

```
X := 5
X * 2
```

However, you'll need to support multiple expressions.  You can do this by creating a recursive calculator parser, in which `calc` resolves to `calc` followed by an additional line.  This allows the calculator to parse any number of lines:

```c
calc:                               
    | calc line                     

line: T_NEWLINE  
    | expr T_NEWLINE                { printf("%d\n", $1); } // no return value needed, no type
    | T_ID T_ASSIGN expr line       { }  // your code here to create a symbol whose name is T_ID, and whose value is whatever expr resolves to!
```    

The code to manipulate the linked list (insert and search) is provided for you, and can also be included in the header definitions of your parser file.

```c
const int TYPE_IVAL = 0; // make a TYPE_FVAL for float!
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
        
        p = p->next;
    }
    
    return result;
}
```

To build this project, modify and use the makefile in our notes (the link to the activity containing the example makefile is listed on this page!).

## References:

[^1]: https://gist.github.com/mlabbe/81d667bac36aa60787fee60e3647a0a8
[^2]: https://github.com/meyerd/flex-bison-example
