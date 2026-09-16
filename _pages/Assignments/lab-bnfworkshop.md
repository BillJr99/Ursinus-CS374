---
layout: assignment
permalink: /Assignments/BNFWorkshop
title: "CS374: Principles of Programming Languages - Lab: BNF Workshop"

info:
  coursenum: CS374
  purpose: "To turn the four-production Scheme grammar from the Syntax and BNF/EBNF activity into a real EBNF grammar for the subset of Scheme you have been programming in, then to build a regular grammar from scratch and use the shape of both to place them on the Chomsky hierarchy.  Grammar writing is the skill the Parser stretch of the course leans on hardest, and this is the first practice at it, on a language you already know."
  tilt:
    task: "With a partner, grow a given four-production grammar into a complete EBNF grammar for a Scheme subset, build a right-linear grammar for even-parity binary strings, and classify five languages by Chomsky level using the shape of the grammars that generate them."
    criteria: "I grade your work on complete and correct EBNF productions with every nonterminal defined, a correct right-linear grammar for the warm-up language, and correct Chomsky classifications argued from the productions rather than asserted, weighted 10/45/45 across the three parts.  See the rubric below for the full breakdown."
  points: 15
  goals:
    - To extend a given grammar into complete EBNF productions for a subset of Scheme, with every nonterminal defined down to terminals
    - To construct a right-linear grammar for a regular language, starting from the finite memory its recognizer needs
    - To classify languages by Chomsky hierarchy level and justify each classification from the shape of the grammar that generates it
  rubric:
    - weight: 10
      description: "Part 0: Before You Start - Writing the Number and Symbol Rules"
      preemerging: Neither a number production nor a symbol production is written
      beginning: One of the two is written, or both are described in prose rather than as EBNF productions
      progressing: Both are written in EBNF, but one admits a string it should reject or rejects one it should accept, or the six test strings are not checked against the productions
      proficient: Both the number and symbol productions are complete EBNF down to terminals; the symbol production accepts a bare operator, a comparison operator, and a name ending in a question mark or an exclamation point, and rejects a name beginning with a digit; and every test string is checked with the deciding production named
    - weight: 45
      description: "Building the Scheme Grammar (Goal 1)"
      preemerging: The grammar is not extended past the four productions you were given
      beginning: The EBNF rewrite or the quote and boolean productions are present, but the special forms are not written, or the productions are prose rather than EBNF
      progressing: The grammar covers the special forms, but one production references an undefined nonterminal or does not derive the example it was written from, or the derivation is missing or skips steps
      proficient: The list production is rewritten with EBNF repetition; quote and the booleans are added; the define, lambda, and if productions are correct EBNF and each one derives the example beside it, with the parameter list of lambda parenthesized and the third expression of if optional; every nonterminal appearing on a right-hand side has its own production; the arithmetic expression is derived one cited production per line; and the verification names the blocking production for each rejected string
    - weight: 45
      description: "Grammar Construction and Chomsky Classification (Goals 2, 3)"
      preemerging: The warm-up grammar is not attempted and no classifications are given
      beginning: The warm-up grammar is attempted but generates strings with an odd number of ones, or classifications are assigned without reasons
      progressing: The warm-up grammar is correct and the classifications are correct, but the reasons restate the level name rather than pointing at the shape of the productions, or the empty alternative is placed without saying what would go wrong otherwise
      proficient: The warm-up grammar generates exactly the even-parity strings, with one nonterminal per parity, one terminal consumed per production, the empty alternative on the even nonterminal only, and a line saying what breaks if the odd nonterminal gets one too; every language is classified correctly with a one-sentence reason naming the structural property that forces its level; the regular classifications point at right-linear productions and the s-expression classification reuses the unmatched-parenthesis argument; and the three closing sentences connect the level the atoms need, the level nested s-expressions need, and why a lexer and a parser are separate programs
  readings:
    - rtitle: "Syntax and BNF/EBNF Activity"
      rlink: "Activities/liascript-syntaxbnf.md"
      liapage: true
    - rtitle: "Grammars and the Chomsky Hierarchy Activity"
      rlink: "Activities/liascript-grammars.md"
      liapage: true
    - rtitle: "Functional Programming in Scheme, Part 2 Activity"
      rlink: "Activities/liascript-scheme.md"
      liapage: true

tags:
  - grammars
  - syntax
  - theory
  - languages
  - lab

---

This **lab** is your first practice at writing grammars.  It is a walkthrough, not a problem set.  You start from four productions you have already seen, and you grow them one step at a time into a real grammar for Scheme.  Then you build a second, smaller grammar from scratch and place five languages on the Chomsky hierarchy.  You may work on paper or in a Markdown file, alone or with a partner.

Three words you need before you start:

- A **grammar** is a set of rules that says which strings belong to a language.
- **BNF**, or Backus-Naur Form, is a notation for writing those rules.
- **EBNF**, or Extended BNF, adds operators for repetition, optional parts, and grouping.  The same rules then take fewer lines.

The language here is the Scheme you have been writing for three weeks.  The *Syntax and BNF/EBNF* activity claimed that four productions describe every legal Scheme program ever written.  That is very nearly true, and Part 0 asks you to find the hole in it.  The four productions also say nothing yet about `define`, `lambda`, `if`, or the quote mark that the [Scheme assignment]({{ site.baseurl }}/Assignments/Scheme) warned you about.  Closing those gaps is the whole lab.

**Pair policy.**  You may do this lab in pairs.  One partner proposes a production (a single grammar rule), and the other tries to break it with a string the rule handles wrongly.  Submit one document between you, with each of you naming the other, and you both earn the same grade.  Working alone is fine too.  See the course schedule for the assigned and due dates.

**What this lab leaves alone, on purpose.**  Derivation trees, ambiguity, precedence, and associativity are today's class session.  You will use all four in the *Grammar and Derivations Workshop* later in the term.  You do not need any of them here.  Scheme is a good first grammar precisely because it has no ambiguity to resolve and no precedence to encode.  Your only job in this lab is to write productions that separate the strings in the language from the strings outside it.

---

## Getting Started

There is nothing to install and nothing to run for this lab.  You need:

- The activities listed under Readings above.  Skim them before you start, and keep the first two open while you work:
  - [Syntax and BNF/EBNF]({{ site.lia_viewer_url }}{{ site.raw_pages_url }}Activities/liascript-syntaxbnf.md), whose Model 1.5 is the grammar you are extending
  - [Grammars and the Chomsky Hierarchy]({{ site.lia_viewer_url }}{{ site.raw_pages_url }}Activities/liascript-grammars.md), which Part 2 draws on
  - [Functional Programming in Scheme, Part 2]({{ site.lia_viewer_url }}{{ site.raw_pages_url }}Activities/liascript-scheme.md), for the Scheme forms the grammar has to cover
- Your own `recursion.scm` and `evaluate.scm` from the Scheme assignment, or the four guided examples from its Part 1.  Every Scheme form in this lab is one you have already written, and reading your own code is the fastest way to get a production right.
- Pencil and paper, or any text editor for a Markdown file.  Neither is required, but if you want VS Code set up the way the rest of the course uses it, the [dev environment page]({{ site.baseurl }}/Tutorials/DevEnvironment) walks through it and the [shell primer]({{ site.baseurl }}/Tutorials/ShellForLanguageDev) covers making a folder and opening a file from the terminal.

> **Time budget.**  Expect about two hours, plus the write-up.  Part 0 takes fifteen minutes.  Part 1 takes about an hour, and Step 1.3 takes longer than the rest of Part 1 together.  Part 2 takes forty to fifty minutes, most of it on the warm-up grammar.  The last reflection prompt asks how long it actually took you.

### Your First 15 Minutes

1.  Read the EBNF reference and the grammar you are extending, both below.  Follow the leftmost derivation one line at a time until you can say which production each step used.
2.  Find the hole.  The derivation's sixth line cites `[<symbol> => +]`, but look at the four productions and try to find the one that says what a `<symbol>` is.  It is not there.  Part 0 is writing it.
3.  Write your first draft of `<symbol>` on paper, then hand it to your partner (or play both roles).  Find one string the rule accepts that it should not, or rejects that it should not, and fix the rule.  That loop, write a rule and attack it with a string and fix the rule, is the whole workflow of this lab.
4.  Create `grammars.md` from the skeleton in the submission section below, and copy that first rule into the Part 0 section.

### The EBNF Shortcuts We Use

Every grammar in this course is written the same way, and this is the whole notation.  A production has a nonterminal on the left, `::=` in the middle, and a sequence of symbols on the right.  A **nonterminal** is a name in angle brackets that has its own production, such as `<digit>`.  A **terminal** is a symbol that appears in the string itself, written in quotes, such as `"-"`.  BNF gives you sequence, alternation, and recursion; EBNF adds three operators on top of those, and those three are the shortcuts that do all the work in this lab.

| Shortcut | Means | Example |
|---|---|---|
| `::=` | "is defined as," separating a nonterminal from its definition | <code>&lt;sign&gt; ::= "+" &#124; "-"</code> |
| `<name>` | a nonterminal, which must have its own production somewhere | `<digit>` |
| `"x"` | a terminal, the literal text that appears in the string | `"("` |
| <code>&#124;</code> | alternation: exactly one of these choices is used | <code>"+" &#124; "-"</code> |
| `{ X }` | repetition: **zero or more** copies of `X` | `{ <digit> }` |
| `[ X ]` | optionality: `X` appears once or not at all | `[ <sign> ]` |
| <code>( X &#124; Y )</code> | grouping: treats the alternatives as one unit inside a larger rule | <code>( "," &#124; ";" )</code> |
| `<empty>` | the empty string, the BNF way to let a recursive rule stop | <code>&lt;exprs&gt; ::= &lt;expr&gt; &lt;exprs&gt; &#124; &lt;empty&gt;</code> |
| `(* … *)` | a comment, ignored by the grammar; use it to record a decision | `(* spaces ignored between atoms *)` |

Here is the same notation at work, with each shortcut labeled in a comment:

```ebnf
(* Sequence: symbols on the right side must appear in this order. *)
<entry>  ::= <name> ":" <number>
(* Alternation: | separates choices; exactly one is used. *)
<sign>   ::= "+" | "-"
(* Repetition: { X } means zero or more copies of X. *)
<digits> ::= <digit> { <digit> }
(* Optionality: [ X ] means X appears once or not at all. *)
<number> ::= [ <sign> ] <digits>
(* Grouping: ( X | Y ) treats the alternatives as one unit inside a larger rule. *)
<pair>   ::= <number> ( "," | ";" ) <number>
```

**Three shortcuts we do not use here.**  You will meet them elsewhere, so recognize them.  Many books and tools write repetition and optionality as postfix marks instead of brackets:

| You may see | It means | We write |
|---|---|---|
| `X*` | zero or more | `{ X }` |
| `X+` | one or more | `X { X }` |
| `X?` | optional | `[ X ]` |

You will see that style later in this course.  The grammar in the Parser assignment uses `stmt*` and `( COLON type )?`, with bare uppercase token names instead of angle brackets.  Neither style is more correct.  **Use the bracket style for everything you write in this lab.**  Your grammar will then read the same way as the ones you are extending.

Two habits keep grammars honest.  Every nonterminal that appears on a right side must have its own production; an undefined nonterminal is the most common lost point in Part 1, and it is exactly the flaw Part 0 asks you to find in the grammar you were given.  And "one or more" is `<x> { <x> }`, not `{ <x> }`, which also accepts nothing at all.

### The Grammar You Are Extending

This is Model 1.5 from the *Syntax and BNF/EBNF* activity, reproduced exactly.  It is written in pure BNF, with recursion doing the work that EBNF repetition will do later:

```ebnf
<expr>  ::= <atom> | <list>
<list>  ::= "(" <exprs> ")"
<exprs> ::= <expr> <exprs> | <empty>
<atom>  ::= <number> | <symbol>
```

`<empty>` stands for the empty string, which is how BNF says "and this alternative contributes nothing," and it is what lets `<exprs>` stop.  The terminals are `(`, `)`, and the numbers and symbols themselves; `<expr>` is the start symbol.

A leftmost derivation starts from the start symbol and, at each step, replaces the leftmost nonterminal using one production.  Here is `(+ 1 (* 2 3))`, from the activity, with the production cited at the right of each line:

```text
<expr>
=> <list>                              [<expr> ::= <list>]
=> ( <exprs> )                         [<list> ::= "(" <exprs> ")"]
=> ( <expr> <exprs> )                  [<exprs> ::= <expr> <exprs>]
=> ( <atom> <exprs> )                  [<expr> ::= <atom>]
=> ( <symbol> <exprs> )                [<atom> ::= <symbol>]
=> ( + <exprs> )                       [<symbol> => +]
=> ( + <expr> <exprs> )                [<exprs> ::= <expr> <exprs>]
=> ( + <atom> <exprs> )                [<expr> ::= <atom>]
=> ( + <number> <exprs> )              [<atom> ::= <number>]
=> ( + 1 <exprs> )                     [<number> => 1]
=> ( + 1 <expr> <exprs> )              [<exprs> ::= <expr> <exprs>]
=> ( + 1 <expr> )                      [<exprs> ::= <empty>]
=> ( + 1 <list> )                      [<expr> ::= <list>]
=> ( + 1 ( <exprs> ) )                 [<list> ::= "(" <exprs> ")"]
   ... the same six steps again, one level down ...
=> ( + 1 ( * 2 3 ) )
```

Read that derivation once more and notice the two lines that cheat.  `[<symbol> => +]` and `[<number> => 1]` are not productions of this grammar, because no production defines `<symbol>` or `<number>`.  That is your Part 0.  Notice also what never happens anywhere in the derivation: no step has to *decide* what binds to what.  The parentheses already said it, and Step 1.4 comes back to why that matters.

### How to Prepare and Submit Your Writeup

You submit one file, `grammars.md`, started from the skeleton below.  If you worked on paper, scan or photograph the pages into a single PDF named `grammars.pdf` instead, in the same section order, with both names on the first page.  Either way, put one `## Part N` heading per part, and put every grammar and derivation inside a fenced code block (three backticks on their own line before and after, as under the first Part 0 heading below).  Outside a code block, Markdown treats `<name>` as an HTML tag and `*` as italics, and your grammar vanishes from the rendered page.  Under each heading goes exactly what that part's `> **Do this.**` list produces; the Deliverables table at the end says what I look for in each section.

````text
# CS374 Lab: BNF Workshop
Partners: <your name> and <partner name>   (or: worked alone)

## Part 0: The Number and Symbol Rules
### The number production
```
<grammar here>
```
### The symbol production
### The six test strings
### Rule I am least sure about
## Part 1: Building the Scheme Grammar
### Step 1.1: The EBNF rewrite
### Step 1.2: Booleans and the quote
### Step 1.3: The special forms
### Step 1.4: Arithmetic, without a precedence ladder
### Step 1.5: Verification
## Part 2: Grammar Construction and Chomsky Classification
### Warm-up: the even-parity grammar
### Part 0 productions I am using
### The classification table
### Atoms, s-expressions, and the lexer/parser split
## Reflection
````

---

## Part 0: Before You Start - Writing the Number and Symbol Rules (10%)

Do this part first, before the rest of the lab, and alone if you like.  It is small, and it is the piece the rest of the grammar rests on: until `<number>` and `<symbol>` are real productions, every derivation you write has to cheat exactly where the activity's derivation did.

`<symbol>` is harder than it looks.  Here is why.

In most languages you have used, `+` is punctuation and `sum` is a name.  Different parts of the language handle each one.  In Scheme they are the same kind of thing.  That is why `(define add +)` works in the Scheme assignment's first guided example: `+` is an ordinary name bound to an ordinary value.

So your `<symbol>` production must accept all of these:

- ordinary names, such as `square` and `sumlist`
- bare operators, such as `+` and `*`
- comparison operators, such as `<=`
- names ending in punctuation, such as `null?` and `set!`

It must still reject anything that should have been a number.

> **Do this.**
> 1. Write `<number>` in EBNF, down to terminals.  It needs an optional leading sign, one or more digits, and an optional fractional part (a `.` followed by one or more digits).  Define `<digit>` too; an undefined nonterminal here is the same flaw you are fixing.
> 2. Write `<symbol>` in EBNF, down to terminals.  Decide which characters may *start* a symbol and which may appear after that, and write those as two separate sets so that a leading digit is impossible.  The characters you must account for are the letters, the digits, and the extended set `+ - * / < > = ? !`.
> 3. Check both productions against these six strings: `42`, `-3.5`, `null?`, `<=`, `+`, and `2x`.  For each one, say whether your grammar accepts it, as what, and name the production that decides.  Two of these are the interesting cases, and if all six come out the way you first expected, look at `+` and `2x` again.
> 4. Name the rule you are least sure about, and bring it to class with that uncertainty marked.  Rough edges are expected here, and the uncertain rule is usually the best discussion of the day.

> **Watch out.**  A `<symbol>` production that allows a digit in the first position makes `42` ambiguous: it is now derivable both as a `<number>` and as a `<symbol>`, and your grammar no longer says which.  Keeping the first character and the following characters in separate sets is what prevents that.

---

## Part 1: Building the Scheme Grammar (45%)

Work the five steps in order.  Each one starts from the grammar as it stood at the end of the previous step, so keep one running grammar in your file and show it again whenever it changes.  By Step 1.5 you should have a single EBNF grammar that generates the Scheme you have been writing.

### Step 1.1: The EBNF Rewrite

The grammar you were given is pure BNF, and `<exprs>` is the giveaway: a rule that mentions itself, plus an `<empty>` alternative, is BNF's way of saying "zero or more."  EBNF has an operator for that, and using it makes an entire production disappear.

> **Do this.**
> 1. Rewrite `<list>` using EBNF repetition so that `<exprs>` is no longer needed, and delete `<exprs>` from the grammar.  You should end up with a `<list>` production that reads in one line as "an open parenthesis, zero or more expressions, a close parenthesis."
> 2. Write one sentence naming exactly what the EBNF bought you here: which production disappeared, and which alternative of it collapsed.
> 3. Confirm you have not changed the language.  Name one string the BNF version generates and check that the EBNF version generates it too, and say in one line why `()` is still legal under your rewrite.  If your rewrite makes `()` illegal, you have written `{ }` where you meant it, or `<expr> { <expr> }` where you did not.

### Step 1.2: Booleans and the Quote

Two things you have typed repeatedly are not in the grammar yet.  The booleans `#t` and `#f` are atoms, and adding them is a one-token change.  The quote is more interesting.

> **Do this.**
> 1. Add the booleans to `<atom>`.  Decide whether they belong as a new alternative or inside `<symbol>`, and say which you chose in one line.  (`#t` cannot be a `<symbol>` under most reasonable Part 0 productions, and noticing why is the point of the question.)
> 2. Add a production for the quote.  `'(1 2 3)` is a quote mark followed by any expression, and the quote mark is a terminal, so the production is short.  Add it as a new alternative of `<expr>` and write it out.
> 3. Now the question this step exists for.  The Scheme assignment warned you that `(1 2 3)` produces `application: not a procedure`, and that forgetting the quote is the most common beginner error in the language.  **Does your grammar reject `(1 2 3)`?**  Answer it by tracing the string against your productions, name the production that accepts or rejects it, and then write two or three sentences on what that tells you about the difference between what a grammar can rule out and what it cannot.

**The answer is no, and that is the point.**  `(1 2 3)` is a perfectly well-formed `<list>`.  It is an open parenthesis, three expressions, and a close parenthesis.  No grammar of Scheme rejects it, and none should.

Here is why.  Whether the first element happens to be a procedure is not a fact about the *shape* of the text.  It is a fact about the value `1` has when the expression runs.  No set of productions can see that.

This is why the course builds a lexer, a parser, and an interpreter as three separate programs.  Each one decides a different class of question.  When you hit an error in October, which of the three reported it will tell you what kind of mistake you made.

### Step 1.3: The Special Forms

This is the step where you make a language design decision.  Look at the grammar as it now stands and check it against code you wrote last week:

```scheme
(define square
  (lambda (n)
    (* n n)))
```

That derives fine.  `define` is a `<symbol>`, `square` is a `<symbol>`, and the `lambda` expression is a `<list>` whose first element is the `<symbol>` `lambda`.  The grammar sees an ordinary list of three expressions and is perfectly happy.  So is the grammar finished?

It depends what you want the grammar to catch.  Under the current grammar, all three of these derive:

- `(if)`, an `if` with nothing to test
- `(define 5 x)`, a definition whose name is a number
- `(lambda)`, a function with no parameter list and no body

Each one is just a list of expressions, so the grammar accepts it.  A grammar that knew about these forms would reject all three before the program ran.  Writing that grammar is Step 1.3.

You will do three forms: `define`, `lambda`, and `if`.  Three is enough to see the pattern and to feel the cost.  The same method extends to `cond` and `let` whenever you want them.

**The method.**  Use the same four steps for each form.

1. Write down the example.
2. Sort every piece of it into one of two bins.  A piece is *fixed* if it is always exactly those characters.  It *varies* if a different program could put something else there.
3. Turn each fixed piece into a terminal in quotes.  Turn each varying piece into a nonterminal.
4. Count how many times each varying piece may appear: exactly one, zero or more (`{ }`), or optional (`[ ]`).

That is the whole procedure.  It produces the production almost mechanically.

**Form 1: `define`.**  The example is `(define square (lambda (n) (* n n)))`, and `(define x (+ 3 2))` from Example 1 is the same shape.

| Piece | Fixed or varies | How many |
|---|---|---|
| `(` and `)` | fixed | one each |
| the word `define` | fixed | exactly one |
| the name being defined (`square`, `x`) | varies, and it is always a name | exactly one |
| the value (`(lambda …)`, `(+ 3 2)`) | varies, and it can be any expression | exactly one |

Reading straight down the table gives you the production.  Write it out; it is five symbols between the parentheses.

**Form 2: `lambda`.**  The example is `(lambda (n) (* n n))`, and Example 2's `pow` is `(lambda (n k) …)`.  This one has a wrinkle: the parameters live inside *their own* pair of parentheses, which are part of the syntax and not optional, and there may be one parameter, two, or none at all.  So the parameter list is a fixed `(`, then zero or more names, then a fixed `)`.  Use `{ }` for "zero or more."

**Form 3: `if`.**  The example is `(if (= k 0) 1 (* n (pow n (- k 1))))`.  Three expressions follow the keyword: the test, the value when the test is true, and the value when it is false.  Scheme lets you leave off the last one, so exactly two are required and the third is optional.  Use `[ ]` for the optional piece.

> **Do this.**
> 1. Fill in the skeleton below.  Replace every `TODO` with a real right-hand side in EBNF, using the tables and notes above.  If your production cannot derive the example in the comment beside it, the production is wrong.

```ebnf
<expr>        ::= <atom> | <quoted> | <special> | <application>
<special>     ::= <define> | <lambda> | <if>

(* (define square (lambda (n) (* n n)))   -- Scheme assignment, Example 2 *)
<define>      ::= TODO

(* (lambda (n k) (* n k))                 -- Example 2; zero parameters is legal *)
<lambda>      ::= TODO

(* (if (= k 0) 1 (* n (pow n (- k 1))))   -- Example 2; the last expression is optional *)
<if>          ::= TODO

(* (sumlist (list 1 2 3)), (+ 1 2), (map classify '(-3 0 7))  -- everything else *)
<application> ::= TODO
```

> 2. Read each production against its example token by token, the way you checked the six strings in Part 0.  Start at the leftmost `(` and walk right, ticking off one symbol of the production per piece of the example, and confirm you run out of both at the same moment.
> 3. Name one string your tightened grammar now rejects that the four-production grammar accepted, and trace it to the production that blocks it.  `(if)` and `(define 5 x)` are both fair game.
> 4. Name one cost you just paid.  Count the productions you now have against the four you started with, and say what happens to the grammar the next time the language gains a form such as `cond` or `let`.
> 5. Answer the awkward question.  `(define x 5)` matches `<define>`, and it also matches `<application>`, since `define` is a `<symbol>` and `x` and `5` are expressions.  Your grammar as written is ambiguous about which one it is.  Say how you would resolve it, in one or two sentences.  You do not have to rewrite the grammar to fix it; you have to notice it and say what you would do.

> **Watch out.**  Do not write productions for `+`, `-`, `*`, and `/`.  Look at `<application>` again: a list whose first element is an expression already covers `(+ 1 2)`, `(* n n)`, and `(- k 1)`, because the operator is just a symbol in the first position.  Step 1.4 is about why that works.

### Step 1.4: Arithmetic, Without a Precedence Ladder

The Scheme assignment's Part 4 opened with `(* (+ 2 3) 4)` and the observation that Scheme's source code is already the tree your parser will have to build in October.  Now derive it and watch that happen.

> **Do this.**
> 1. Write a leftmost derivation of `(* (+ 2 3) 4)` against your own grammar, in the format of the worked derivation above: one step per line, always expanding the leftmost nonterminal, with the production cited at the right of each line.  You may stop expanding `<number>` and `<symbol>` once you reach them, citing them as in the worked example, since you defined them in Part 0.
> 2. Count.  How many productions in your grammar mention `+`, `-`, `*`, or `/` by name?
> 3. Name in one sentence what you would have to add to *your* grammar to write `2 + 3 * 4` and have it mean 14.  The *Syntax and BNF/EBNF* activity's Derivation 2 shows the shape of the answer, with its `<expr>`, `<term>`, and `<factor>` ladder.

The answer to question 2 is zero, and that is the whole point of this step.  Your grammar handles every arithmetic operator in the language without mentioning a single one, because prefix notation puts the operator where the grammar already expects an expression, and the parentheses have already said what groups with what.  Put it another way: the parens are the parse tree.

> **Not today's business.**  Precedence, associativity, and the ambiguity that makes them necessary are what today's session is about, and the *Grammar and Derivations Workshop* is where you build that ladder for real, in the grammar your own parser will implement.  Here you are only noticing that Scheme does not need one.

### Step 1.5: Verify Your Grammar by Hand

> **Do this.**
> 1. Write out your final grammar, complete, in one code block.  Read every right-hand side and confirm that every name in it has its own production.  This is the single most common way to lose points on this part.
> 2. Choose three strings your grammar accepts, and note the path through the productions in a few words for each.  Make at least one of them hit a boundary: the empty list `()`, a `lambda` with no parameters, or an application nested three deep.
> 3. Choose two strings it rejects, and for each one name the production that blocks it.  Use `(+ 3 4` as one of them, and argue it from the rules rather than from intuition: `<list>` is the only production that introduces a `)`, and it introduces exactly one for every `(`, so no sequence of rule applications terminates without the closing parenthesis.  For the second, use something your Step 1.3 grammar rejects that the four-production grammar would have accepted.

---

## Part 2: Chomsky Classification (45%)

The Chomsky hierarchy ranks languages by how much memory a machine needs to recognize them.  Three levels matter here:

- **Regular** languages need only **finite memory**.  The recognizer carries a fixed number of facts as it reads.  You decide how many in advance, and the number never grows with the input.
- **Context-free** languages need a **stack**.  They match or nest symbols that must be unwound in reverse order, and you do not know in advance how deep the nesting goes.
- Languages with **cross-serial constraints**, such as equal counts in three separate places, need more than a stack.

Those three descriptions are easy to nod at and hard to use.  So before you classify anything, build one of these grammars yourself.  Then "finite memory" becomes something you can point at on the page.

### Warm-up: Write the Grammar for Even-Parity Binary Strings

The language is every string of `0`s and `1`s containing an even number of `1`s.  `0`, `11`, `1001`, and the empty string all belong to it; `1`, `10`, and `111` do not.  You are going to write a grammar that generates exactly this language, and the route there is four questions.

**Question 1: reading left to right, what is the only thing you must remember?**  Not the string.  Not how many `1`s you have seen.  Only whether the count of `1`s *so far* is even or odd, because that is the only fact that can still change the answer.  Two possibilities, so one bit.  That is what finite memory means, concretely.

**Question 2: give each thing you must remember its own nonterminal.**  Two possibilities, two nonterminals.  Call them `<even>` and `<odd>`, and read each one as "the rest of a string that is legal from here, given the parity I have seen so far."

**Question 3: what does each character do to the thing you remember?**  Reading a `0` changes nothing, so you stay where you are.  Reading a `1` flips the parity, so you cross over.  Each production therefore consumes exactly one terminal and then names the nonterminal for where you have landed:

```ebnf
<even> ::= "0" <even>    (* a zero does not change the parity *)
         | "1" <odd>     (* a one flips it *)
         | TODO          (* question 4 fills this in *)
<odd>  ::= "0" <odd>
         | "1" <even>
```

**Question 4: where are you allowed to stop?**  Only where the string you have produced so far is already legal, which here is only the even state.  So exactly one of these two nonterminals gets an `<empty>` alternative, and the other must not have one, or the grammar would generate strings it should reject.  Fill in the `TODO` and say in one line what would go wrong if you gave `<odd>` an `<empty>` alternative too.

The start symbol is `<even>`, because before you have read anything you have seen zero `1`s, and zero is even.

**Why this settles the classification.**  Look at the shape of every production you just wrote: a terminal, then at most one nonterminal, and that nonterminal is at the far right end.  A grammar in which *every* production has that shape is called **right-linear**, and a language is regular exactly when some right-linear grammar generates it.  So you have not merely asserted that this language is regular; you have exhibited the grammar that proves it.  That is the standard of argument the rest of Part 2 asks for.

### Before You Classify: Check Your Part 0 Productions

Two of the languages below are the productions you wrote in Part 0, so this part goes badly if those productions are not in a shape you can argue about.  Check yours against this before you continue.

What you want is a production built **only** from terminals, alternation (`|`), concatenation, and `{ }` repetition, with no nonterminal ever appearing anywhere except at the end of an alternative.  A production of that kind is regular, and saying so is the whole argument.  What you do *not* want is a production that nests a nonterminal in the middle of a right-hand side, or that refers back to itself around a terminal on both sides, because that is the shape that needs a stack.

If your Part 0 productions do not have that shape, or you are not sure, you may use these as your reference versions for Part 2.  Say in one line that you did, and which of yours you replaced.  This costs you nothing: Part 0 was graded on the work you did there, and this is only so that Part 2 has something clean to reason about.

```ebnf
<digit>   ::= "0" | "1" | "2" | "3" | "4" | "5" | "6" | "7" | "8" | "9"
<number>  ::= [ "-" ] <digit> { <digit> } [ "." <digit> { <digit> } ]
<initial> ::= "a" | "b" | (* ... the rest of the letters ... *)
            | "+" | "-" | "*" | "/" | "<" | ">" | "=" | "?" | "!"
<subseq>  ::= <initial> | <digit>
<symbol>  ::= <initial> { <subseq> }
```

Notice that every one of those is right-linear in the sense above, and notice that `<list>` from Part 1 is not, because `<expr>` appears with a `)` after it.  That difference is the entire content of the next four classifications.

### The Classification

For each language, name the lowest Chomsky level that can describe it, with a one-sentence reason that names the structural property forcing that level.

1.  Binary strings with an even number of `1`s, as you just built it.
2.  The language of your `<symbol>` production.
3.  The language of your `<number>` production.
4.  Well-formed s-expressions, as your `<list>` production defines them.
5.  Strings of the form `a^n b^n c^n` (equal counts of all three).

> **Do this.**
> 1. Make a table with three columns: Language, Lowest level, Reason.
> 2. For each language, ask what a recognizer must remember while reading the string, and write that structural property as the reason, in one sentence.  "It is context-free because it is a context-free language" restates the level name; "nested s-expressions need a stack to match each `)` to the `(` that opened it" names the property, and the rubric rewards the second form.
> 3. For languages 1, 2, and 3, the argument is the one the warm-up gave you: point at the shape of the productions and say that every one of them is right-linear, so a fixed amount of memory suffices.  Name the specific rule you are pointing at.
> 4. For language 4, reuse your Step 1.5 rejection of `(+ 3 4`.  You already argued that `<list>` introduces exactly one `)` for every `(` and that nothing terminates without it.  Say why counting those matches is something no fixed amount of memory can do, given that the nesting can be arbitrarily deep.
> 5. Close with one sentence for each of these three questions.  Which level do Scheme's atoms (a number, a symbol, a boolean) need?  Which level do nested s-expressions need?  What does that split tell you about why a compiler has both a lexer and a parser?  The third sentence should connect the first two.

Those three sentences are the point of this part, and they are the reason the next two assignments are two assignments.  The *Build a Lexer* assignment asks you for a program that recognizes exactly the level you named first, and the *Parser and AST* assignment asks you for a program that recognizes the level you named second.  They are separate programs because they are separate problems, and you just proved it.

---

## Deliverables

| File or artifact | What it shows | Rubric row |
|------------------|---------------|------------|
| `## Part 0` section | Your `<number>` and `<symbol>` productions down to terminals, the six test strings with the deciding production named for each, and the rule you are least sure about | Part 0 (10%) |
| `## Part 1` section | The EBNF rewrite, the quote and boolean productions with your answer on `(1 2 3)`, the three special forms filled in with their cost and the `(define x 5)` question answered, the derivation of `(* (+ 2 3) 4)`, and the final grammar with three accepted and two rejected strings | Building the Scheme Grammar (45%) |
| `## Part 2` section | The even-parity grammar with its empty alternative justified, five classifications with structural reasons, and the three sentences on atoms, s-expressions, and the lexer/parser split | Grammar Construction and Chomsky Classification (45%) |
| `## Reflection` section | Your answers to the Reflection Prompts below | Not weighted; I read them |

## Self-Check Before You Submit

- [ ] Both partners are named at the top of `grammars.md` (or `grammars.pdf`), or the file says "worked alone".
- [ ] Part 0 defines both `<number>` and `<symbol>` down to terminals, and your `<symbol>` accepts `+`, `<=`, and `null?` while rejecting `2x`.
- [ ] In your final grammar, every nonterminal on a right-hand side has its own production, and repetition and optionality use `{ }` and `[ ]`, not words like "one or more".
- [ ] Each of the three special forms derives the example given beside it in the skeleton.
- [ ] The derivation of `(* (+ 2 3) 4)` cites a production on every line, and its last line is the original expression.
- [ ] Three accepted and two rejected strings are checked against the productions by hand, and each rejection names the production that blocks it.
- [ ] The even-parity grammar generates the empty string, `0`, `11`, and `1001`, and generates neither `1` nor `10`.
- [ ] You said in one line what would go wrong if `<odd>` also had an `<empty>` alternative.
- [ ] Every Part 2 reason names a structural property (finite memory, a stack, cross-serial constraints), and the three tokens-versus-syntax sentences are present.
- [ ] The Reflection Prompts are answered.

## Grading Breakdown

This lab is worth 15 points, as the course schedule states.  Each part's weight below is a percentage of those 15 points, and the rubric rows use the same percentages.

| Component | Weight |
|-----------|--------|
| Part 0: Writing the Number and Symbol Rules | 10% |
| Part 1: Building the Scheme Grammar | 45% |
| Part 2: Grammar Construction and Chomsky Classification | 45% |
| **Total** | **100% (15 points)** |

## Reflection Prompts

- Which string broke your first draft of a production, and what change fixed it?
- Step 1.2 asked whether your grammar rejects `(1 2 3)`.  Before you traced it, what did you expect the answer to be, and did tracing it change how you think about what a parser can catch?
- If you worked in a pair, who did what, and name one thing your partner caught that you would have missed.  If you worked alone, note that instead.
