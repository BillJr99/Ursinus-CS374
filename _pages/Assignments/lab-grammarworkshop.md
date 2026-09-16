---
layout: assignment
permalink: /Assignments/GrammarWorkshop
title: "CS374: Principles of Programming Languages - Lab: Grammar and Derivations Workshop"

info:
  coursenum: CS374
  purpose: "To complete the Parser assignment's grammar work with a partner: write a full EBNF grammar for the class language, derive programs that prove it produces what you expect, and settle precedence decisions you can defend."
  tilt:
    task: "With a partner, write the EBNF grammar the Parser assignment's Part 1 requires, produce leftmost derivations and parse trees for two worked programs, and show how the grammar's shape enforces precedence and associativity."
    criteria: "I grade this on a complete and correct EBNF grammar, correct derivations with matching parse trees, and a demonstrated precedence and ambiguity analysis.  The rubric below has the details."
  points: 15
  goals:
    - To write a complete EBNF grammar for the class language's expressions and statements
    - To construct leftmost derivations and parse trees that verify the grammar against concrete programs
    - To explain how grammar structure (the expression ladder) enforces precedence and associativity and eliminates ambiguity
  rubric:
    - weight: 10
      description: "Part 0: Before You Start - Derivations, Ambiguity, and Precedence"
      preemerging: No parse trees are drawn
      beginning: One parse tree is drawn, so the ambiguity is asserted rather than shown
      progressing: Two distinct parse trees are drawn for one string, but the grammar is not rewritten to remove the ambiguity, or the associativity trees are missing
      proficient: Two distinct parse trees are drawn for one string of an ambiguous grammar; the grammar is rewritten so only one survives, with the place marked where encoding precedence made a rule harder to read; and both the left- and right-associative trees for 2 - 3 - 4 are drawn, with your language's actual choice confirmed in a REPL
    - weight: 45
      description: "EBNF Grammar (Goal 1)"
      preemerging: The grammar is missing most constructs or does not use EBNF notation
      beginning: The grammar covers expressions or statements but not both, or several productions reference undefined nonterminals
      progressing: The grammar is complete but flat, with no precedence levels, so it is ambiguous for arithmetic
      proficient: The grammar covers every expression and statement form of the class language in correct EBNF, with a tiered expression ladder (one production per precedence level) and no undefined nonterminals
    - weight: 23
      description: "Derivations and Parse Trees (Goal 2)"
      preemerging: No derivation is attempted, or the derivations do not follow the submitted grammar
      beginning: One program is derived but with skipped steps, or the parse tree does not match the derivation
      progressing: Both programs are derived with matching trees, but one derivation has a misapplied production
      proficient: Both worked programs have complete leftmost derivations, every step citing the production applied, with parse trees that match the derivations exactly
    - weight: 22
      description: "Precedence and Ambiguity Analysis (Goal 3)"
      preemerging: No analysis, or the analysis restates notes without using the submitted grammar
      beginning: The analysis asserts precedence works but shows no derivation-level evidence
      progressing: The analysis shows the correct tree for the precedence example but does not explain which grammar feature forces it
      proficient: The analysis derives the precedence example, names the exact productions that force multiplication to bind tighter than addition and subtraction to associate left, and shows what a flat one-level grammar would have permitted instead
  readings:
    - rtitle: "Recursive Descent Parsing Activity"
      rlink: "Activities/liascript-recursivedescent.md"
      liapage: true
    - rtitle: "Parsing Expressions Activity"
      rlink: "Activities/liascript-parsingexpressions.md"
      liapage: true

tags:
  - grammars
  - parsing
  - languages
  - lab

---

This **lab** is the Parser assignment's Part 1, done early and with a partner.  You write the EBNF grammar that your recursive-descent parser will transcribe function by function, then prove the grammar does what you think it does by deriving two real programs from it and drawing their parse trees.  Every parsing function you write in the Parser assignment is one production from this document, so getting the grammar right on paper first pays off more than anything else you do there.  You leave with one file, `grammar.md`, that goes straight into the [Parser assignment]({{ site.baseurl }}/Assignments/Parser).

**Pair policy.**  You may do this lab in pairs.  Grammar design benefits from argument: one partner proposes a production (a single grammar rule), and the other tries to break it with a program the rule derives wrongly.  Turn in the same document, each of you naming the other, and you will both get the same grade.  Working alone is allowed.  The Parser assignment remains individual work: you may both build on this shared grammar, but your parsers are your own.

---

## Before You Start

This is a paper lab.  The deliverable is one Markdown file, and the only program you run is a one-line REPL check in Part 0.  You need:

- The two activities linked at the top of this page (Recursive Descent Parsing and Parsing Expressions), read closely enough that production, nonterminal, terminal, and derivation are familiar words.  The worked example below reviews them.
- A text editor that saves plain text.  VS Code or any editor works.
- Python 3.10 or newer for the REPL check.  If your machine isn't set up yet, follow the [dev environment page]({{ site.baseurl }}/Tutorials/DevEnvironment); if the terminal is new to you, read the [shell primer]({{ site.baseurl }}/Tutorials/ShellForLanguageDev) first.

Make a folder for the lab and confirm Python is available.  The last command prints something like `Python 3.11.4`; any version 3.10 or newer is fine.

```bash
mkdir -p cs374-grammar
cd cs374-grammar
python3 --version
```

Now create `grammar.md` in that folder with your editor.  Every part of the lab goes into this one file.  Start it with a title line, a `Partners:` line naming both of you (or saying you worked alone), and four headings, `## Part 0` through `## Part 3`, named as the parts of this page are, so I can find each piece when I grade it.

> **Watch out.**  Two formatting rules that save you points.  Put every grammar in a fence labeled `ebnf` and every derivation and parse tree in a fence labeled `text` (three backticks, the label, your content, three backticks).  A tree drawn outside a fence collapses into a single line when Markdown renders it, and a collapsed tree is not a tree I can grade.  Open the file in your editor's Markdown preview before you submit and confirm the trees still look like trees.

> **Time budget.**  About three hours in two sittings.  See the course schedule for the assigned and due dates: this lab lands inside the Parser assignment's window, and its due date is that assignment's first checkpoint.  On assignment, do Part 0 alone (under an hour) and choose a partner.  By the midpoint, have the Part 1 grammar drafted and attacked by your partner at least once.  By the due date, have Parts 2 and 3 written and `grammar.md` previewed and submitted.  Parts 1 through 3 take one session of about two hours with your partner, most of it on Part 1.

### Your First 15 Minutes

Make one derivation of your own on a grammar smaller than the one you'll write, so the mechanics are settled before the real work.

1. Read the worked example below with a pencil, checking at every line that the nonterminal being rewritten is the leftmost one.
2. Copy its three-line grammar into a scratch section at the bottom of `grammar.md` (delete it before you submit).
3. Derive `2 * 3 + 4` step by step in the same format, and draw its tree.
4. Compare with the example.  The `STAR` should sit under its own `term` and the `PLUS` at the top of the tree, even though the multiplication now comes first in the input.  If it came out that way, Parts 2 and 3 are the same move on a bigger grammar.  If it didn't, reread the example's note on `( ... )*` groups, which is where derivations usually go wrong.

---

## Worked Example: One Derivation and Its Parse Tree

A derivation starts from the grammar's start symbol and rewrites one nonterminal per step until only terminals (tokens) remain.  A leftmost derivation always rewrites the leftmost nonterminal, which makes it unique for an unambiguous grammar and easy to check.  A parse tree is the same information drawn as a tree: each nonterminal becomes a node whose children are the right-hand side you chose for it.  Here is a three-production grammar for sums and products of integers; terminals are token names from your Lexer, in all caps.

```ebnf
expr    ::= term ( PLUS term )*
term    ::= factor ( STAR factor )*
factor  ::= INT | LPAREN expr RPAREN
```

One convention keeps derivations over EBNF clean: when you apply a production that contains a `( ... )*` group, decide how many times the group repeats and write out every copy in that one step, citing the production and the count.  Here is the leftmost derivation of `2 + 3 * 4`:

```text
Input:  2 + 3 * 4
Tokens: INT(2) PLUS INT(3) STAR INT(4)

expr
=> term PLUS term                  expr:    ( PLUS term )* used once
=> factor PLUS term                term:    ( STAR factor )* used zero times
=> INT PLUS term                   factor:  INT                (this INT is 2)
=> INT PLUS factor STAR factor     term:    ( STAR factor )* used once
=> INT PLUS INT STAR factor        factor:  INT                (this INT is 3)
=> INT PLUS INT STAR INT           factor:  INT                (this INT is 4)
```

Check the leftmost rule at line four: the sentential form was `INT PLUS term`, the only nonterminal left was `term`, so `term` is what got rewritten.  The last line is exactly the program's token sequence, which is how you know the derivation is finished.  The matching parse tree records the same six choices as nodes:

```text
                    expr
              ________|________
             /        |        \
           term      PLUS      term
            |              _____|_____
            |             /     |     \
          factor       factor  STAR  factor
            |             |             |
          INT(2)        INT(3)        INT(4)
```

Read the tree from the bottom.  `3 * 4` sits under its own `term` node, one level below the `PLUS`, so the multiplication is grouped before the addition happens.  No rule anywhere says "multiplication first."  The shape of the ladder says it: `PLUS` lives in `expr`, `STAR` lives in `term`, and `expr` is built from `term`s, so a `STAR` can never sit above a `PLUS`.  Part 3 asks you to make this argument for your own grammar and to show what goes wrong without the ladder.

---

## Part 0: Before You Start - Derivations, Ambiguity, and Precedence

Do this part first; you may do it alone even though the rest of the lab is pair work.  A grammar is ambiguous when one string has two different parse trees.  Precedence says which operator binds tighter; associativity says how a chain of the same operator groups.  Ambiguity stops being subtle the moment you have drawn it twice, so draw both trees, then rewrite the grammar until only one drawing survives.  That rewrite is the whole technique.  If it falls apart on you, bring it anyway; where it fell apart is what the discussion is for.

### Step 0.1: Show That a Flat Grammar Is Ambiguous

Use this flat grammar unless the class discussion handed you a different one:

```ebnf
expr ::= expr PLUS expr
       | expr MINUS expr
       | expr STAR expr
       | INT
```

> **Do this.**
> 1. Pick a string with at least three operands and two different operators, for example one that mixes `-` and `*`.  Do not reuse the `a + b * c` string that Part 3 draws for you.
> 2. Draw two distinct parse trees for it in `text` fences under `## Part 0` in `grammar.md`.  Both must follow the grammar above exactly: every node's children are one of its four right-hand sides.  If you can only find one tree, your string probably has a single operator; add a second, different one.
> 3. Under each tree, write the parenthesized expression it stands for and the value it computes.  If the two values differ, you have shown the ambiguity has a cost.

### Step 0.2: Rewrite the Grammar So Only One Tree Survives

> **Do this.**
> 1. Rewrite the grammar in an `ebnf` fence so it encodes precedence and associativity.  The worked example's ladder is the shape to imitate: one production per precedence level, each mentioning only itself (at most on one side) and the level below it.  A rewrite that still has `expr` on both ends of a right-hand side, such as `expr ::= expr PLUS expr`, is still ambiguous no matter how many levels you add.
> 2. Redraw your Step 0.1 string under the new grammar.  Try to draw the second tree again and write one sentence saying which production now forbids it.
> 3. Mark the rule that got harder to read with an EBNF comment (`//` to the end of the line, as the Parser assignment uses) saying what it used to say and why it changed.  That readability cost is the price of an unambiguous grammar, and Part 3 asks you to defend paying it.

### Step 0.3: Draw Both Associativities for 2 - 3 - 4

> **Do this.**
> 1. Draw the left-associative tree, which groups `(2 - 3) - 4`, and the right-associative tree, which groups `2 - (3 - 4)`, in two `text` fences.
> 2. Compute both by hand and write the two values under the trees.
> 3. Ask your favorite language rather than guessing.  For Python, run `python3 -c "print(2 - 3 - 4)"` from the `cs374-grammar` folder; for JavaScript, `node -e "console.log(2 - 3 - 4)"`; for another language, evaluate the same expression in its REPL.  You get a single number: `-5` means the language grouped left, `(2 - 3) - 4`, and `3` means it grouped right, `2 - (3 - 4)`.
> 4. Paste the command and its output into Part 0 with one sentence naming the associativity your language uses and which tree it agreed with.

---

## Part 1: The EBNF Grammar

Write the complete EBNF grammar for the class language used across the Lexer, Parser, and Interpreter assignments.  Cover these constructs:

- `let`, assignment, and `print` statements
- `if`/`else`
- `while` with blocks
- expressions over numbers, strings, booleans, identifiers, calls, and the arithmetic, comparison, and logical operators

Structure the expression productions as a ladder: one production per precedence level, from `or` at the top down through `and`, comparison, additive, multiplicative, unary, and primary.  This is exactly the shape the Parser assignment's Part 2 transcribes into functions, one function per production, so its shape matters more than its length.  EBNF notation, for reference: `*` means zero or more, `+` one or more, `?` zero or one, `|` separates alternatives, and `( )` groups.  Terminals are your Lexer's token names in all caps.  A nonterminal is a rule you define; if a name appears on a right-hand side, it must appear on a left-hand side somewhere in the grammar.

### Step 1.1: Write the Statement Productions

> **Do this.**
> 1. Under `## Part 1` in `grammar.md`, open an `ebnf` fence and start from this skeleton.  Statements are the easier half, and finishing them first gives you a `program` production to hang everything else on.  Replace every `TODO` with a real right-hand side.
> 2. For each statement form, write a two-line program that uses it and read your production against it token by token.  If your Lexer would produce a token that your production doesn't mention, the production is wrong.

```ebnf
program     ::= stmt* EOF
stmt        ::= let_stmt
              | assign_stmt
              | print_stmt
              | if_stmt
              | while_stmt
              | block
let_stmt    ::= TODO   // LET, a name, EQ, an expression, SEMICOLON
assign_stmt ::= TODO
print_stmt  ::= TODO
if_stmt     ::= TODO   // decide how an optional ELSE attaches, and to what
while_stmt  ::= TODO   // WHILE, a condition, then a block
block       ::= TODO   // LBRACE ... RBRACE
```

### Step 1.2: Write the Expression Ladder

> **Do this.**
> 1. Continue the same `ebnf` fence with the ladder below, replacing each `TODO`.  Each level is built out of the level below it and mentions only its own operators.  `or_expr` is filled in to show the pattern; every binary level down to `multiplicative` has the same shape with different operator tokens.
> 2. Put calls where they belong.  A call such as `f(x, 1)` is a primary followed by an argument list in parentheses; give it its own level between `unary` and `primary` or fold it into `primary`, and say which in a comment.
> 3. Add a one-line comment on any other production where you made a design decision: how `else` attaches, whether comparisons chain.
> 4. Read every right-hand side and confirm every name in it is defined.  An undefined nonterminal is the most common way to lose points on this part.

```ebnf
expr           ::= or_expr
or_expr        ::= and_expr ( OR and_expr )*
and_expr       ::= TODO   // same shape, one level down
comparison     ::= TODO   // LT, LE, GT, GE, EQEQ, NEQ; decide whether chaining is allowed
additive       ::= TODO   // PLUS, MINUS
multiplicative ::= TODO   // STAR, SLASH
unary          ::= TODO   // prefix MINUS and NOT, then the level below
primary        ::= TODO   // literals, IDENT, and a parenthesized expr
```

> **Checkpoint.**  Hand the grammar to your partner and have them write a five-token program that the grammar derives wrongly or can't derive at all.  Every production that survives a serious attempt at breaking it is one you won't have to reopen during the Parser assignment.  The first Reflection Prompt asks which production took the most rounds, so keep a tally.

---

## Part 2: Derivations and Parse Trees

Produce a leftmost derivation and the matching parse tree for two programs, citing the production applied at every step: program 1 is `let x = 1 + 2 * 3;` and program 2 is `while x < 10 { x = x + 1; }`.  These derivations use your Part 1 grammar, not the worked example's; they are the proof that the grammar produces what you expect.  A derivation that does not follow the submitted grammar earns nothing, so if a step needs a production you don't have, fix the grammar in Part 1 and note that you did.

### Step 2.1: Derive Both Programs and Draw Their Trees

> **Do this.**
> 1. Under `## Part 2`, write program 1 in a `text` fence with its token sequence on the line below it, using your Lexer's token names (`LET IDENT EQ INT PLUS INT STAR INT SEMICOLON`).  Count the tokens: your derivation's final line must have exactly those nine terminals, in that order.
> 2. Start from `program` and derive it in a `text` fence, one `=>` line per step, in the format of the worked example.  Rewrite the leftmost nonterminal only, and cite the production at the right of each line, including how many times any `( ... )*` group was used.
> 3. Walk the ladder honestly.  Getting from `expr` down to an `INT` passes through every level in between, even the ones with no operator at this input, and each pass is one cited step.  Expect the derivation to run somewhat over a dozen lines because of the ladder; that length is correct.
> 4. Draw the parse tree in a second `text` fence.  Every internal node is a nonterminal from your derivation, every leaf is a token, and the leaves read left to right as the token sequence.
> 5. Write program 2 with its token sequence, then derive it the same way.  This one exercises `while_stmt`, `block`, `assign_stmt`, and the `comparison` level.  When you rewrite `block`, decide how many statements the `stmt*` group produces (here, one) and cite it.
> 6. Draw program 2's tree.  It will be wider than program 1's, so leave room and check it in the Markdown preview.

> **If it fails.**  The three usual problems:
> - The derivation skipped a ladder level.  Every level between `expr` and the leaf must appear, even when it has no operator at this input.
> - The tree has a node the derivation never produced, or is missing one it did.  They must match exactly.
> - The final line has the wrong number of terminals, which almost always means a `SEMICOLON` or a brace was dropped.

---

## Part 3: Precedence and Ambiguity

Using your derivation of program 1, explain which productions force `*` to bind tighter than `+`.  Show the wrong second tree that a flat single-level expression grammar would also permit.  Then state how your grammar makes `1 - 2 - 3` associate left, and verify with a three-line derivation sketch.  Here is what ambiguity looks like, so the "wrong second tree" has a model: under this flat grammar, the string `a + b * c` has two parse trees.

```ebnf
expr ::= expr PLUS expr
       | expr STAR expr
       | IDENT
```

```text
   Tree A: a + (b * c)                    Tree B: (a + b) * c

               expr                                  expr
          _____/|\_____                         _____/|\_____
         /      |      \                       /      |      \
       expr    PLUS    expr                  expr    STAR    expr
        |          ____/|\____           ____/|\____          |
        |         /     |     \         /     |     \         |
    IDENT(a)    expr   STAR   expr    expr   PLUS   expr   IDENT(c)
                 |             |       |             |
             IDENT(b)      IDENT(c)  IDENT(a)    IDENT(b)
```

Same string, same grammar, two trees, two meanings.  Nothing in the flat grammar prefers Tree A, so a parser built from it has no basis for choosing, and that is what ambiguous means.  Your ladder is the fix: with `STAR` confined to a lower level than `PLUS`, Tree B has no derivation at all, because no production ever puts a `STAR` node above a `PLUS` node.

### Step 3.1: Name the Productions That Force Precedence and Draw the Wrong Tree

> **Do this.**
> 1. In your Part 2 derivation of program 1, find the step where `1 + 2 * 3` split at the `PLUS`, and the later step where `2 * 3` split at the `STAR`.
> 2. Write a short paragraph naming those two productions and explaining why the `STAR` step had to happen below the `PLUS` step: which production contains `PLUS`, which contains `STAR`, and which one is built from the other.
> 3. Write a flat one-level grammar for `1 + 2 * 3` (the Part 0 or the example grammar above will do; say which).
> 4. Draw the tree that groups `(1 + 2) * 3` in a `text` fence and write its value next to the correct tree's value.
> 5. State in one sentence which production of your ladder makes this tree impossible.

### Step 3.2: Show That 1 - 2 - 3 Associates Left

> **Do this.**
> 1. State in one or two sentences how your grammar makes `1 - 2 - 3` group as `(1 - 2) - 3`.
> 2. Verify it with a three-line derivation sketch in a `text` fence: start at your additive level, apply its production once to expose both `MINUS` tokens, and show where the left group forms.  Three lines means a sketch, not a full derivation down to tokens.

> **Watch out.**  A `( MINUS multiplicative )*` group produces a flat list of three operands at one level, and a flat list by itself does not say which two group first.  Decide where the left grouping comes from, and say so.  It can come from the grammar's shape: the left-recursive form `additive ::= additive MINUS multiplicative | multiplicative` puts the grouping in the tree.  Or it can come from the parser's left-fold loop that the Parser assignment describes for the `*` form.  Either is defensible, but an analysis that doesn't say which one it relies on isn't finished.

---

## Deliverables

Submit `grammar.md` containing all parts, with both partners named at the top.  Bring it to the Parser assignment: its Part 1 asks you to include (and refine, if the coding surfaces issues) exactly this grammar.

| File or artifact | What it shows | Rubric row |
|------------------|---------------|------------|
| `grammar.md`, `## Part 0` | Two trees for one string with their values, the disambiguated rewrite with the marked rule, both `2 - 3 - 4` trees, and the REPL command with its output | Part 0 |
| `grammar.md`, `## Part 1` | The complete EBNF grammar in one `ebnf` fence, statements then ladder, with design decisions commented and no undefined nonterminals | EBNF Grammar |
| `grammar.md`, `## Part 2` | Each program's token sequence, its leftmost derivation with a production cited on every line, and its matching parse tree | Derivations and Parse Trees |
| `grammar.md`, `## Part 3` | The precedence paragraph naming both productions, the flat grammar's wrong tree with both values, the associativity statement, and the three-line sketch | Precedence and Ambiguity Analysis |

---

## Self-Check Before You Submit

- [ ] Both partners are named at the top of `grammar.md`, or the top says you worked alone.
- [ ] Part 0 has two distinct trees for one string, a rewritten grammar with the harder-to-read rule marked, both `2 - 3 - 4` trees, and the REPL command with its output.
- [ ] The Part 1 ladder has one production per precedence level, `or` through `primary`; the grammar covers every statement form in the Part 1 list; and every nonterminal on a right-hand side is defined on a left-hand side.
- [ ] Both Part 2 derivations rewrite the leftmost nonterminal at every step, cite a production on every line, end in exactly the program's token sequence, and match their parse trees node for node.
- [ ] Part 3 names the productions that force precedence, shows the flat grammar's wrong tree, and includes the three-line `1 - 2 - 3` sketch with a stated source of left grouping.
- [ ] Grammars are in `ebnf` fences, derivations and trees are in `text` fences, and the Markdown preview shows the trees intact.

---

## Reflection Prompts

- Which production went through the most revisions before your partner could no longer break it, and what broke it last?
- If you worked in a pair, who did what, and name one thing your partner caught that you would have missed.  If you worked alone, note that instead.
