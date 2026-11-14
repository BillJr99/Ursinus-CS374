<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374-Fall2026/gh-pages/_pages/Activities/liascript-calculator-variables.md or locally via https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374-Fall2026/gh-pages/_pages/Activities/liascript-calculator-variables.md

import: https://raw.githubusercontent.com/liascript/CodeRunner/master/README.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

# Calculator with Variables

Our calculator forgets everything between lines, and a language has to remember.  The first step toward that is small: let a program give a value a name, and read it back.  Today you add that step to the calculator two ways, by hand in Python and in Flex and Bison, using a dictionary called a symbol table.

## Learning Goals

By the end of this activity, you will be able to:

- Explain what a symbol table stores, and when a language writes to it and reads from it
- Add assignment and lookup to a hand-written recursive descent calculator
- Trace why the right side of an assignment has to be evaluated before the name is stored
- Read the same two operations as grammar rules and actions in Bison
- Explain why one dictionary cannot give a program two variables with the same name

> **Before You Begin:** This activity assumes you can read a recursive descent parser, and that you have seen a Bison rule with an action, from *Parsing, Part 2*.

---

## Directions and Group Roles

Work in your POGIL team with your rotated roles (**Manager**, **Recorder**, **Presenter**, **Reflector**).  Think each model and question through on your own first, then talk it over with your group.

---

## How Today Runs

| Segment | What your team does |
|---------|---------------------|
| Part I: The Calculator So Far | Run Model 1, and answer CTQs 1.1 and 1.2 |
| Part II: Giving a Value a Name | Run Model 2, and answer CTQs 2.1-2.3 |
| Part III: The Same Idea in Bison | Build Model 3, trace one assignment, and answer CTQs 3.1 and 3.2 |
| Part IV: What One Dictionary Cannot Do | Answer CTQs 4.1 and 4.2 |

---

# Part I: The Calculator So Far

Each level of the grammar is one function.  This parser computes as it reads: when `E` returns, the value is already known.

## Model 1: The Calculator from the Board

<!-- run: id=cs374-liascript-calculator-variables-1 viz=env -->
```python
# The calculator from the board: one function per grammar level.
#   E -> T ( ( + | - ) T )*
#   T -> F ( ( * | / ) F )*
#   F -> ( E ) | number
class Parser:
    def __init__(self, text):
        self.text = text.replace(" ", "")
        self.pos = 0

    def peek(self):
        if self.pos < len(self.text):
            return self.text[self.pos]
        return None

    def match(self, char):
        if self.peek() == char:
            self.pos += 1
            return True
        return False

    def E(self):
        value = self.T()
        while self.peek() in ("+", "-"):
            op = self.peek()
            self.match(op)
            right = self.T()
            value = value + right if op == "+" else value - right
        return value

    def T(self):
        value = self.F()
        while self.peek() in ("*", "/"):
            op = self.peek()
            self.match(op)
            right = self.F()
            value = value * right if op == "*" else value / right
        return value

    def F(self):
        if self.match("("):
            value = self.E()
            self.match(")")
            return value
        number = ""
        while self.peek() is not None and self.peek().isdigit():
            digit = self.peek()
            number += digit
            self.match(digit)
        return int(number)


for text in ["2 + 3 * 4", "(2 + 3) * 4", "7 - 2 - 1"]:
    print(text, "=", Parser(text).E())
```
@LIA.eval(`["main.py"]`, `none`, `python3 main.py`)
[Visualize this example](https://billjr99.github.io/Ursinus-CS374-Fall2026/viz/#cs374-liascript-calculator-variables-1) <!-- code-viz link -->

> **CTQ 1.1** Which function decides that `*` binds tighter than `+`?  Point at the call that does it.

> **CTQ 1.2** Where in this code would a name such as `x` have to be handled?  Say which grammar level it belongs to, and why.

---

# Part II: Giving a Value a Name

A name is a primary value, like a number, so it belongs at the `F` level: when `F` sees a name, it reads the name's value.  Writing a value is a separate job, so it gets its own statement.  Both operations share one dictionary called the **symbol table**.

```text
assignment:   x = 3;     store  symbols["x"] = 3
lookup:       x + 1      read   symbols["x"]
```

## Model 2: Assignment and Lookup with One Dictionary

The calculator keeps its three levels.  A variable needs two new things.  An assignment stores a value under a name, and a lookup reads it back.  Both use one dictionary, the *symbol table*:

```text
stmt -> "print" E ";"  |  NAME "=" E ";"
F    -> "(" E ")"  |  NUMBER  |  NAME
```

The grammar stays LL(1), because the first token of a statement decides which rule applies.  Names have several characters, so this version splits the text into tokens first, where a character at a time was enough for numbers.

<!-- run: id=cs374-liascript-calculator-variables-2 viz=env -->
```python
import re

class Parser:
    def __init__(self, text):
        # Names have several characters, so split the text into tokens first.
        self.tokens = re.findall(r"\d+|[A-Za-z_]\w*|\S", text)
        self.pos = 0
        self.vars = {}                      # the symbol table: name -> value

    def peek(self):
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return None

    def match(self, token):
        if self.peek() == token:
            self.pos += 1
            return True
        return False

    def E(self):
        value = self.T()
        while self.peek() in ("+", "-"):
            op = self.peek()
            self.match(op)
            right = self.T()
            value = value + right if op == "+" else value - right
        return value

    def T(self):
        value = self.F()
        while self.peek() in ("*", "/"):
            op = self.peek()
            self.match(op)
            right = self.F()
            value = value * right if op == "*" else value / right
        return value

    def F(self):
        token = self.peek()
        if self.match("("):
            value = self.E()
            self.match(")")
            return value
        self.match(token)
        if token.isdigit():
            return int(token)
        return self.vars[token]             # lookup: read the name's value

    def statement(self):
        token = self.peek()
        self.match(token)
        if token == "print":
            print(self.E())
        else:
            self.match("=")
            self.vars[token] = self.E()     # assignment: store the value
        self.match(";")

    def parse(self):
        while self.peek() is not None:
            self.statement()


Parser("x = 3; x = x + 4; print x * 2;").parse()      # 14

# Suppose x = 10 was meant to last only for a block.  One dictionary has only
# one x, so the outer value is gone, and the last line still sees 10.
Parser("x = 1; y = 2; x = 10; print x + y; print x + y;").parse()     # 12, 12
```
@LIA.eval(`["main.py"]`, `none`, `python3 main.py`)
[Visualize this example](https://billjr99.github.io/Ursinus-CS374-Fall2026/viz/#cs374-liascript-calculator-variables-2) <!-- code-viz link -->

### Reading the Code

- `self.vars[token] = self.E()` is the assignment, and `return self.vars[token]` in `F` is the lookup.  Those two lines are all the variables need.
- The right side runs first, so `x = x + 4` reads the old `x` and then stores the new one.
- The last line of the output is the problem.  One dictionary has one `x`, so nothing can hold the outer value while a block has its own.

> **CTQ 2.1** In `x = x + 4;`, why must the right side run before the name is stored?  What would happen on the first assignment to a name if it ran after?

> **CTQ 2.2** Run `print z;` with no assignment to `z`.  Which line reports the problem?  Change it so the message names the variable.

> **CTQ 2.3** Assignment here is a statement.  In some languages it is an expression with a value, so `a = b = 2` works.  Which part of this parser would have to change?  (The Parser assignment takes that road, in an LR grammar.)

---

# Part III: The Same Idea in Bison

The two operations look the same in Bison.  Assignment is a rule whose action stores a value, and lookup is a rule whose action reads one.  This small language has only one-letter names, so its whole symbol table can be an array of 26 slots.

## Model 3: Variables as Rules and Actions

Save this as `vars.y`:

```
%{
#include <stdio.h>
#include <ctype.h>
int yylex(void);
void yyerror(const char *s) { fprintf(stderr, "error: %s\n", s); }
int registers[26];          /* one slot per letter: the whole symbol table */
%}
%union { int number; int slot; }
%token <number> NUM
%token <slot>   LETTER
%token LET PRINT
%type  <number> expr
%left '+'
%left '*'
%%
input: /* nothing */ | input stmt '\n' ;
stmt:  LET LETTER '=' expr  { registers[$2] = $4; }   /* assignment */
     | PRINT expr           { printf("%d\n", $2); }
     ;
expr:  expr '+' expr        { $$ = $1 + $3; }
     | expr '*' expr        { $$ = $1 * $3; }
     | NUM                  { $$ = $1; }
     | LETTER               { $$ = registers[$1]; }   /* lookup */
     ;
%%
int yylex(void) {
    int c = getchar();
    while (c == ' ') c = getchar();
    if (isdigit(c)) { ungetc(c, stdin); scanf("%d", &yylval.number); return NUM; }
    if (islower(c)) {
        int next = getchar();
        if (islower(next)) {        /* two or more letters: a keyword */
            int first = c;
            while (islower(next)) next = getchar();
            ungetc(next, stdin);
            return first == 'l' ? LET : PRINT;
        }
        ungetc(next, stdin);
        yylval.slot = c - 'a';
        return LETTER;
    }
    return c == EOF ? 0 : c;
}
int main(void) { return yyparse(); }
```

```bash
bison -d vars.y
gcc vars.tab.c -o vars
printf 'let x = 3\nlet y = x * 2 + 1\nprint y\nlet x = x + 1\nprint x * y\n' | ./vars
```

> **You should see.** `7`, and then `28`.

Follow `let x = x + 1` through it.  The parser reduces `x` to an `expr` with the lookup rule, then `1`, then `expr '+' expr`.  Only when the whole statement has been read does the `LET` rule's action run and store the result.  Because the parser works bottom-up, the right side is always evaluated first.

> **CTQ 3.1** Find the two lines that correspond to `symbols[...] = ...` and `symbols[...]` in Model 2.

> **CTQ 3.2** Why can an array of 26 slots not hold a name such as `total`?  What would you need in its place?  Sketch the fields, and say which operation would have to search it.

---

# Part IV: What One Dictionary Cannot Do

These programs run on this calculator, and they show where it stops being enough.

```text
let x = 1
{ let x = 10   print x }     should print 10
print x                      should print 1, and one dictionary prints 10
```

> **CTQ 4.1** Why is there no way to get `1` on the last line with one dictionary?  We will fix this when we reach *Scope Chains and Closures*.

> **CTQ 4.2** Suppose you want `if`.  This parser computes while it reads.  What happens to the branch that should not run?  Hold on to your answer for *From Calculator to Scheme*.

---

**In-class work stops here.**

The [Flex and Bison tutorial](https://www.billmongan.com/Ursinus-CS374-Fall2026/Tutorials/FlexAndBison) builds a fuller version of this calculator, with named variables and a tree, if you want to read further.  The Parser assignment asks you to add variables to both of its calculators.

# Check Your Understanding

A symbol table maps:

[(X)] Names to their current values
[( )] Tokens to grammar rules
[( )] States to table actions
[( )] Values to their types

---

A name used in an expression belongs at the `F` level of the grammar because:

[(X)] It is a primary value, like a number, and it needs no operators of its own
[( )] Names bind more loosely than `+`
[( )] Only `F` can reach the dictionary
[( )] It keeps the grammar ambiguous

---

**Up next:** *Lambda Calculus I*, and the Lambda Calculus lab soon after.  *From Calculator to Scheme* then answers CTQ 4.2: to run only one branch, the program has to stop computing while it reads.
