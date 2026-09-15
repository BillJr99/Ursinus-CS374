---
layout: assignment
permalink: /Assignments/BNFWorkshop
title: "CS374: Principles of Programming Languages - Lab: BNF Workshop"

info:
  coursenum: CS374
  purpose: "To turn the four-production Scheme grammar from the Syntax and BNF/EBNF activity into a real EBNF grammar for the subset of Scheme you have been programming in, and then to say what that grammar can and cannot decide.  Grammar writing is the skill the Parser stretch of the course leans on hardest, and this is the first practice at it, on a language you already know."
  tilt:
    task: "With a partner, grow a given four-production grammar into a complete EBNF grammar for a Scheme subset, classify a set of languages by Chomsky level, and argue prefix notation against infix on the readability, writability, and reliability criteria."
    criteria: "I grade your work on complete and correct EBNF productions with every nonterminal defined, correct Chomsky classifications with structural reasons, and a design argument grounded in the course criteria, weighted 10/45/25/20 across the four parts.  See the rubric below for the full breakdown."
  points: 15
  goals:
    - To extend a given grammar into complete EBNF productions for a subset of Scheme, with every nonterminal defined down to terminals
    - To classify languages by Chomsky hierarchy level and justify each classification by the structural property that forces it
    - To evaluate a syntax design choice against the readability, writability, and reliability criteria
  rubric:
    - weight: 10
      description: "Part 0: Before You Start - The Atoms the Grammar Never Defined"
      preemerging: Neither a number production nor a symbol production is written
      beginning: One of the two is written, or both are described in prose rather than as EBNF productions
      progressing: Both are written in EBNF, but one admits a string it should reject or rejects one it should accept, or the six test strings are not checked against the productions
      proficient: Both the number and symbol productions are complete EBNF down to terminals; the symbol production accepts a bare operator, a comparison operator, and a name ending in a question mark or an exclamation point, and rejects a name beginning with a digit; and every test string is checked with the deciding production named
    - weight: 45
      description: "Building the Scheme Grammar (Goal 1)"
      preemerging: The grammar is not extended past the four productions you were given
      beginning: The EBNF rewrite or the quote and boolean productions are present, but the special forms are not written, or the productions are prose rather than EBNF
      progressing: The grammar covers the special forms, but one production references an undefined nonterminal or does not match the example it was written from, or the derivation is missing or skips steps
      proficient: The list production is rewritten with EBNF repetition; quote and the booleans are added; all five special forms are written in correct EBNF and each one matches the example it came from; every nonterminal appearing on a right-hand side has its own production; the arithmetic expression is derived one cited production per line; and the verification names the blocking production for each rejected string
    - weight: 25
      description: "Chomsky Classification (Goal 2)"
      preemerging: No classifications, or levels are assigned without reasons
      beginning: Some classifications are correct but reasons restate the level name rather than the structural property
      progressing: All classifications are correct but one or two reasons miss the structural property that forces the level, or the classification of your own productions is asserted rather than argued from them
      proficient: Every language is classified correctly with a one-sentence reason naming the structural property that forces its level (finite memory suffices; matching or nesting needs a stack; cross-serial constraints need more); the two classifications drawn from your own Part 0 productions are argued from those productions; and the three closing sentences connect the level the atoms need, the level nested s-expressions need, and why a lexer and a parser are separate programs
    - weight: 20
      description: "Design-Criteria Argument (Goal 3)"
      preemerging: No argument, or the argument does not reference the course criteria
      beginning: The argument names a criterion but does not connect the notation to a concrete consequence for programmers
      progressing: The argument connects the choice to two criteria with concrete consequences but does not engage the case for the side it rejects
      proficient: The argument evaluates prefix s-expressions against infix notation on at least two of readability, writability, and reliability with concrete programmer-facing consequences, states the strongest case for the side it rejects, names the tradeoff plainly, and takes a defensible position
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
    - rtitle: "Evaluating Languages Activity"
      rlink: "Activities/liascript-languageevaluation.md"
      liapage: true

tags:
  - grammars
  - syntax
  - theory
  - languages
  - lab

---

This **lab** is your first practice at writing grammars, and it is a walkthrough rather than a set of exercises: you start from four productions you have already seen and grow them, one step at a time, into a real EBNF grammar for the Scheme you have been programming in for the last three weeks.  A grammar is a set of rules that says which strings belong to a language.  BNF (Backus-Naur Form) is a notation for writing those rules, and EBNF (Extended BNF) adds operators for repetition, optional parts, and grouping, so the same rules take fewer lines.  You then classify five languages by Chomsky level and make one design argument, on paper or in a Markdown file, with a partner.

The language is not a toy chosen at random.  The *Syntax and BNF/EBNF* activity claimed that four productions describe every legal Scheme program ever written, and it is very nearly true.  The claim has a hole in it, though, which Part 0 asks you to find, and the grammar says nothing yet about `define`, `lambda`, `if`, `cond`, `let`, or the quote mark that Part 1 of the [Scheme assignment]({{ site.baseurl }}/Assignments/Scheme) warned you about.  Closing those gaps is the whole lab, and by the end you will have written a grammar for a language whose programs you have already been writing by hand.

**Pair policy.**  You may do this lab in pairs.  One partner proposes a production (a single grammar rule), and the other tries to break it with a string the rule handles wrongly.  Submit one document between you, with each of you naming the other, and you both earn the same grade.  Working alone is fine too.  See the course schedule for the assigned and due dates.

**What this lab deliberately leaves alone.**  Today's session takes apart derivation trees, ambiguity, precedence, and associativity, and you will meet all four properly in the *Grammar and Derivations Workshop*, where you write the grammar for the class language your parser will implement.  Scheme is a good first grammar precisely because it has no ambiguity to resolve and no precedence to encode, so here the job is to write productions that draw the right boundary between strings that belong to the language and strings that do not.  Part 1 ends by noticing where the precedence machinery *would* have gone, and stops there on purpose.

---

## Getting Started

There is nothing to install and nothing to run for this lab.  You need:

- The activities listed under Readings above.  Skim them before you start, and keep the first two open while you work:
  - [Syntax and BNF/EBNF]({{ site.lia_viewer_url }}{{ site.raw_pages_url }}Activities/liascript-syntaxbnf.md), whose Model 1.5 is the grammar you are extending
  - [Grammars and the Chomsky Hierarchy]({{ site.lia_viewer_url }}{{ site.raw_pages_url }}Activities/liascript-grammars.md), which Part 2 draws on
  - [Functional Programming in Scheme, Part 2]({{ site.lia_viewer_url }}{{ site.raw_pages_url }}Activities/liascript-scheme.md) and [Evaluating Languages]({{ site.lia_viewer_url }}{{ site.raw_pages_url }}Activities/liascript-languageevaluation.md), for the Scheme forms and the design criteria respectively
- Your own `recursion.scm` and `evaluate.scm` from the Scheme assignment, or the four guided examples from its Part 1.  Every Scheme form in this lab is one you have already written, and reading your own code is the fastest way to get a production right.
- Pencil and paper, or any text editor for a Markdown file.  Neither is required, but if you want VS Code set up the way the rest of the course uses it, the [dev environment page]({{ site.baseurl }}/Tutorials/DevEnvironment) walks through it and the [shell primer]({{ site.baseurl }}/Tutorials/ShellForLanguageDev) covers making a folder and opening a file from the terminal.

> **Time budget.**  About two hours of grammar work plus the write-up: fifteen minutes for Part 0, about an hour for Part 1 (the special forms in Step 1.3 take longer than the rest of it together), and twenty to thirty minutes each for Parts 2 and 3.  The last reflection prompt asks how long it actually took.

### Your First 15 Minutes

1.  Read the EBNF reference and the grammar you are extending, both below.  Follow the leftmost derivation one line at a time until you can say which production each step used.
2.  Find the hole.  The derivation's sixth line cites `[<symbol> => +]`, but look at the four productions and try to find the one that says what a `<symbol>` is.  It is not there.  Part 0 is writing it.
3.  Write your first draft of `<symbol>` on paper, then hand it to your partner (or play both roles).  Find one string the rule accepts that it should not, or rejects that it should not, and fix the rule.  That loop, write a rule and attack it with a string and fix the rule, is the whole workflow of this lab.
4.  Create `grammars.md` from the skeleton in the submission section below, and copy that first rule into the Part 0 section.

### EBNF Notation Reference

A production has a nonterminal on the left, `::=` in the middle, and a sequence of symbols on the right.  A nonterminal is a name in angle brackets that has its own production, such as `<digit>`.  A terminal is a symbol that appears in the string itself, written in quotes, such as `"-"`.  BNF gives you sequence, alternation, and recursion.  EBNF adds three operators on top of those.

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

Read that derivation once more and notice the two lines that cheat.  `[<symbol> => +]` and `[<number> => 1]` are not productions of this grammar, because no production defines `<symbol>` or `<number>`.  That is your Part 0.  Notice also what never happens anywhere in the derivation: no step has to *decide* what binds to what.  That is the observation Part 3 asks you to argue about.

### How to Prepare and Submit Your Writeup

You submit one file, `grammars.md`, started from the skeleton below.  If you worked on paper, scan or photograph the pages into a single PDF named `grammars.pdf` instead, in the same section order, with both names on the first page.  Either way, put one `## Part N` heading per part, and put every grammar and derivation inside a fenced code block (three backticks on their own line before and after, as under the first Part 0 heading below).  Outside a code block, Markdown treats `<name>` as an HTML tag and `*` as italics, and your grammar vanishes from the rendered page.  Under each heading goes exactly what that part's `> **Do this.**` list produces; the Deliverables table at the end says what I look for in each section.

````text
# CS374 Lab: BNF Workshop
Partners: <your name> and <partner name>   (or: worked alone)

## Part 0: The Atoms the Grammar Never Defined
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
### Step 1.4: Arithmetic, and the ladder that is not there
### Step 1.5: Verification
## Part 2: Chomsky Classification
## Part 3: Design-Criteria Argument
## Reflection
````

---

## Part 0: Before You Start - The Atoms the Grammar Never Defined (10%)

Do this part first, before the rest of the lab, and alone if you like.  It is small, and it is the piece the rest of the grammar rests on: until `<number>` and `<symbol>` are real productions, every derivation you write has to cheat exactly where the activity's derivation did.

Writing `<symbol>` is harder than it looks, and the reason is worth knowing before you start.  In most languages you have used, `+` is punctuation and `sum` is a name, and the two are handled by different parts of the language.  In Scheme they are the same kind of thing.  `(define add +)` from the Scheme assignment's first guided example works precisely because `+` is an ordinary name bound to an ordinary value.  So your `<symbol>` production has to admit `+` and `*` and `<=` alongside `square` and `sumlist`, and it has to admit the trailing punctuation in `null?` and `set!`, while still rejecting anything that should have been a number.

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

That last question is the one to sit with, because the answer is no.  `(1 2 3)` is a perfectly well-formed `<list>`: an open parenthesis, three expressions, a close parenthesis.  Nothing in any grammar of Scheme rejects it, and nothing should, because whether the first element happens to be a procedure is not a fact about the *shape* of the text.  It is a fact about the value that `1` has when the expression is evaluated, and no set of productions can see that.  This is the same reason the course builds a lexer, a parser, and an interpreter as three separate programs: each one can decide a different class of question, and the errors you get in October will tell you which of the three noticed the problem.

### Step 1.3: The Special Forms

Here is the step where you make a real language design decision.  Look at the grammar as it now stands and check it against code you wrote last week:

```scheme
(define square
  (lambda (n)
    (* n n)))
```

That derives fine.  `define` is a `<symbol>`, `square` is a `<symbol>`, and the `lambda` expression is a `<list>` whose first element is the `<symbol>` `lambda`.  The grammar sees an ordinary list of three expressions and is perfectly happy.  So is the grammar finished?

It depends what you want it to catch.  Under the current grammar, `(if)` derives, `(define 5 x)` derives, and `(lambda)` derives, because each one is just a list of expressions.  A grammar that knows about the special forms would reject all three before anything ran.  Writing that grammar is Step 1.3.

> **Do this.**
> 1. Fill in the skeleton below.  Replace every `TODO` with a real right-hand side in EBNF.  Each form is one you have already written, and the example beside it is the one to read your production against: if your production cannot derive the example, the production is wrong.

```ebnf
<expr>        ::= <atom> | <quoted> | <special> | <application>
<special>     ::= <define> | <lambda> | <if> | <cond> | <let>

(* (define square (lambda (n) (* n n)))   -- Scheme assignment, Example 2 *)
<define>      ::= TODO

(* (lambda (n k) (* n k))                 -- Example 2; note zero parameters is legal *)
<lambda>      ::= TODO

(* (if (= k 0) 1 (* n (pow n (- k 1))))   -- Example 2; the else branch is optional *)
<if>          ::= TODO

(* (cond ((< n 0) 'negative) (else 'positive))  -- Example 4 *)
<cond>        ::= TODO

(* (let ((x (+ 2 3))) (* x x))            -- the Part 4 primer; note the doubled parens *)
<let>         ::= TODO

(* (sumlist (list 1 2 3)), (+ 1 2), (map classify '(-3 0 7))  -- everything else *)
<application> ::= TODO
```

> 2. Read each production against its example token by token, the way you checked the six strings in Part 0.  The `<let>` production is the one that usually goes wrong: `let` takes a *list of binding pairs*, so there are two levels of parentheses before you reach the first name, which is exactly the typo the Scheme assignment warned about.
> 3. Name one string your tightened grammar now rejects that the four-production grammar accepted, and trace it to the production that blocks it.
> 4. Name one cost you just paid.  Count the productions you now have against the four you started with, and say what happens to the grammar the next time the language gains a form.
> 5. Answer the awkward question.  `(define x 5)` matches `<define>`, and it also matches `<application>`, since `define` is a `<symbol>` and `x` and `5` are expressions.  Your grammar as written is ambiguous about which one it is.  Say how you would resolve it, in one or two sentences.  You do not have to rewrite the grammar to fix it; you have to notice it and say what you would do.

> **Watch out.**  Do not write productions for `+`, `-`, `*`, and `/`.  Look at `<application>` again: a list whose first element is an expression already covers `(+ 1 2)`, `(* n n)`, and `(- k 1)`, because the operator is just a symbol in the first position.  Step 1.4 is about why that is remarkable.

### Step 1.4: Arithmetic, and the Ladder That Is Not There

The Scheme assignment's Part 4 opened with `(* (+ 2 3) 4)` and the observation that Scheme's source code is already the tree your parser will have to build in October.  Now derive it and watch that happen.

> **Do this.**
> 1. Write a leftmost derivation of `(* (+ 2 3) 4)` against your own grammar, in the format of the worked derivation above: one step per line, always expanding the leftmost nonterminal, with the production cited at the right of each line.  You may stop expanding `<number>` and `<symbol>` once you reach them, citing them as in the worked example, since you defined them in Part 0.
> 2. Count.  How many productions in your grammar mention `+`, `-`, `*`, or `/` by name?
> 3. Open the *Syntax and BNF/EBNF* activity to Derivation 2 and look at the infix grammar there, the one with `<expr>`, `<term>`, and `<factor>`.  Those three nonterminals exist for one reason only, which is to make `3 + 4 * 5` mean 23 rather than 35.  Write two or three sentences on what that machinery buys and what it costs, and name in one sentence what you would have to add to *your* grammar to write `2 + 3 * 4` and get 14.

The answer to question 2 is zero, and it is worth saying out loud.  Your grammar handles every arithmetic operator in the language without mentioning a single one, because prefix notation puts the operator where the grammar already expects an expression, and the parentheses have already said what groups with what.  In four words: the parens are the parse tree.  Drafting your answer to question 3 is drafting Part 3.

> **Not today's business.**  Precedence, associativity, and the ambiguity that makes them necessary are what today's session is about, and the *Grammar and Derivations Workshop* is where you build that ladder for real, in the grammar your own parser will implement.  Here you are only noticing that Scheme does not need one.

### Step 1.5: Verify Your Grammar by Hand

> **Do this.**
> 1. Write out your final grammar, complete, in one code block.  Read every right-hand side and confirm that every name in it has its own production.  This is the single most common way to lose points on this part.
> 2. Choose three strings your grammar accepts, and note the path through the productions in a few words for each.  Make at least one of them hit a boundary: the empty list `()`, a `lambda` with no parameters, or an application nested three deep.
> 3. Choose two strings it rejects, and for each one name the production that blocks it.  Use `(+ 3 4` as one of them, and argue it from the rules rather than from intuition: `<list>` is the only production that introduces a `)`, and it introduces exactly one for every `(`, so no sequence of rule applications terminates without the closing parenthesis.  For the second, use something your Step 1.3 grammar rejects that the four-production grammar would have accepted.

---

## Part 2: Chomsky Classification (25%)

The Chomsky hierarchy ranks languages by how much memory a machine needs to recognize them.  Regular languages need only finite memory, meaning a fixed number of facts the recognizer carries as it reads (a parity bit, or "have I seen a decimal point yet").  Context-free languages need a stack, because they match or nest symbols that must be unwound in reverse order.  Languages with cross-serial constraints, such as equal counts in three separate places, need more than a stack.

Two of the five languages below are grammars you wrote yourself in Part 0, so for those the reason must come from your own productions rather than from a general impression.  For each language, name the lowest Chomsky level that can describe it, with a one-sentence reason that names the structural property forcing that level.

1.  Binary strings with an even number of 1s.
2.  The language of your Part 0 `<symbol>` production.
3.  The language of your Part 0 `<number>` production.
4.  Well-formed s-expressions, as your `<list>` production defines them.
5.  Strings of the form `a^n b^n c^n` (equal counts of all three).

> **Do this.**
> 1. Make a table with three columns: Language, Lowest level, Reason.
> 2. For each language, ask what a recognizer must remember while reading the string, and write that structural property as the reason, in one sentence.  "It is context-free because it is a context-free language" restates the level name; "nested s-expressions need a stack to match each `)` to the `(` that opened it" names the property, and the rubric rewards the second form.
> 3. For languages 2 and 3, point at the specific feature of *your* production that settles it.  A production built only from alternation, concatenation, and `{ }` repetition over terminals is regular, and saying which of your rules are of that form is the argument.  Your Step 1.5 rejection of `(+ 3 4` is the corresponding argument for language 4, so reuse it.
> 4. Close with one sentence for each of these three questions.  Which level do Scheme's atoms (a number, a symbol, a boolean) need?  Which level do nested s-expressions need?  What does that split tell you about why a compiler has both a lexer and a parser?  The third sentence should connect the first two.

Those three sentences are the point of this part, and they are the reason the next two assignments are two assignments.  The *Build a Lexer* assignment asks you for a program that recognizes exactly the level you named first, and the *Parser and AST* assignment asks you for a program that recognizes the level you named second.  They are separate programs because they are separate problems, and you just proved it.

---

## Part 3: Design-Criteria Argument (20%)

You now have direct evidence on both sides of an argument the *Syntax and BNF/EBNF* activity asked you to start drafting.  Scheme's grammar has no notion of precedence anywhere, and you wrote it in an afternoon.  The infix grammar in that activity needs three nonterminals arranged in a hierarchy whose only job is to make multiplication bind tighter than addition, and it is the shape you will spend the *Grammar and Derivations Workshop* building for the class language.

Write one paragraph that evaluates prefix s-expression syntax against conventional infix syntax, for a language a beginner will learn in a week, using at least two of the readability, writability, and reliability criteria from the *Evaluating Languages* session.

> **Do this.**
> 1. Pick at least two of readability, writability, and reliability, and name each one in the paragraph so I can find it.
> 2. For each one, write one concrete consequence for a person using the language: what they gain or lose when the notation is uniform and fully parenthesized rather than infix with a precedence table.  Think about reading a long expression someone else wrote, about the error you get when a parenthesis is missing versus when precedence surprises you, and about how much of the language's syntax you have to hold in your head on day one.
> 3. State the strongest case for the side you are going to reject.  If you land on s-expressions, say plainly what infix wins.  If you land on infix, say plainly what uniformity wins.
> 4. State the tradeoff in one sentence, then take a position and say why it follows from the consequences you named.

> **Watch out.**  Do not conclude that s-expressions are simply better because the grammar is shorter.  A shorter grammar is a fact about the implementer's workload, not about the programmer's, and the two criteria can point in opposite directions.  Infix reads the way people already read arithmetic, and Lisp's uniformity is paid for by everyone counting closing parentheses.  An argument that does not engage that is not finished.

> **Watch out, again.**  "Readability improves" is a criterion name, not an argument.  The rubric wants the consequence: what specifically becomes easier or harder to read, and for whom.

---

## Deliverables

| File or artifact | What it shows | Rubric row |
|------------------|---------------|------------|
| `## Part 0` section | Your `<number>` and `<symbol>` productions down to terminals, the six test strings with the deciding production named for each, and the rule you are least sure about | Part 0 (10%) |
| `## Part 1` section | The EBNF rewrite, the quote and boolean productions with your answer on `(1 2 3)`, the five special forms filled in with their costs and the `(define x 5)` question answered, the derivation of `(* (+ 2 3) 4)`, and the final grammar with three accepted and two rejected strings | Building the Scheme Grammar (45%) |
| `## Part 2` section | Five classifications with structural reasons, two of them argued from your own productions, plus the three sentences on atoms, s-expressions, and the lexer/parser split | Chomsky Classification (25%) |
| `## Part 3` section | One paragraph evaluating prefix against infix on at least two criteria, with the opposing case stated, the tradeoff named, and a position taken | Design-Criteria Argument (20%) |
| `## Reflection` section | Your answers to the Reflection Prompts below | Not weighted; I read them |

## Self-Check Before You Submit

- [ ] Both partners are named at the top of `grammars.md` (or `grammars.pdf`), or the file says "worked alone".
- [ ] Part 0 defines both `<number>` and `<symbol>` down to terminals, and your `<symbol>` accepts `+`, `<=`, and `null?` while rejecting `2x`.
- [ ] In your final grammar, every nonterminal on a right-hand side has its own production, and repetition and optionality use `{ }` and `[ ]`, not words like "one or more".
- [ ] Each of the five special forms derives the example given beside it in the skeleton.
- [ ] The derivation of `(* (+ 2 3) 4)` cites a production on every line, and its last line is the original expression.
- [ ] Three accepted and two rejected strings are checked against the productions by hand, and each rejection names the production that blocks it.
- [ ] Every Part 2 reason names a structural property (finite memory, a stack, cross-serial constraints), languages 2 and 3 are argued from your own productions, and the three tokens-versus-syntax sentences are present.
- [ ] The Part 3 paragraph uses at least two criteria, gives a concrete consequence for each, states the case for the side you rejected, names the tradeoff, and takes a position.
- [ ] The Reflection Prompts are answered, including the AI disclosure and the hours estimate.

## Grading Breakdown

This lab is worth 15 points, as the course schedule states.  Each part's weight below is a percentage of those 15 points, and the rubric rows use the same percentages.

| Component | Weight |
|-----------|--------|
| Part 0: The Atoms the Grammar Never Defined | 10% |
| Part 1: Building the Scheme Grammar | 45% |
| Part 2: Chomsky Classification | 25% |
| Part 3: Design-Criteria Argument | 20% |
| **Total** | **100% (15 points)** |

## Reflection Prompts

- Which string broke your first draft of a production, and what change fixed it?
- Step 1.2 asked whether your grammar rejects `(1 2 3)`.  Before you traced it, what did you expect the answer to be, and did tracing it change how you think about what a parser can catch?
- If you worked in a pair, who did what, and name one thing your partner caught that you would have missed.  If you worked alone, note that instead.
- AI disclosure: list any generative-AI tools you used, for what, and how you verified the results (or state 'none').
- Approximately how many hours it took you to finish this lab (I will not judge you for this at all; I am simply using it to gauge if the labs are too easy or hard)?
