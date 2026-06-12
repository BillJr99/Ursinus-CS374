# Scanners and Parsers with Flex and Yacc: Building a Mini-Notation Parser

<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://github.com/BillJr99/Ursinus-CS374-Fall2026/blob/main/_pages/Activities/liascript-flexyacc.md or locally if deployed via https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374/main/_pages/Activities/liascript-flexyacc.md

import: https://raw.githubusercontent.com/liascript/CodeRunner/master/README.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

# Scanners and Parsers with Flex and Yacc: Building a Mini-Notation Parser

This module develops **lexical analysis** and **syntax analysis** by building a real scanner and parser, using **flex** and **yacc** (GNU bison), for the **mini-notation** shared by the live coding music languages **TidalCycles** and **Strudel**. We move from **language classes $\rightarrow$ regular expressions and DFAs $\rightarrow$ context-free grammars $\rightarrow$ LALR(1) parsing $\rightarrow$ abstract syntax trees $\rightarrow$ semantics**, so that by the end of the module a string like `bd [sn sn] hh*2 ~` becomes a tree, and that tree becomes a timeline of musical events you can hear in your head, and verify in code.

---

## 0. Environment & Utilities

This module uses the classic C toolchain for language processing. We need `flex` (a scanner generator), `bison` (a parser generator compatible with the original `yacc`), and a C compiler. The commands below verify the environment; no internet access is required once these tools are installed.

---

## Code Cell

```bash
# On Debian/Ubuntu (or the course container):
#   sudo apt-get install flex bison gcc
# On macOS with Homebrew:
#   brew install flex bison

flex --version
bison --version
gcc --version

echo "Environment ready."
```

---

## 1. Why a Music Language Is a Perfect Parsing Target

**Mini-notation is a small external DSL embedded inside a larger host language.** In TidalCycles, the host is Haskell; in Strudel, the host is JavaScript. In both, the string between quotes in an expression such as `sound "bd sn [hh hh] sn"` is not host-language code at all. It is a separate language with its own lexical and syntactic rules, and both systems contain a dedicated parser for it. When you write a mini-notation parser, you are reproducing a component that ships inside real, widely used software, which makes this one of the most honest parsing exercises available to us.

**The language is small enough to master and rich enough to be interesting.** A pattern describes one **cycle** of musical time, conventionally the interval $[0, 1)$. The constructs we will parse in this module are:

| Construct | Example | Informal meaning |
|-----------|---------|------------------|
| Sequence | `bd sn hh` | Divide the cycle evenly among the elements |
| Rest | `~` | Silence occupying one slot |
| Group | `[sn sn]` | A subsequence occupying a single slot |
| Fast | `hh*4` | Repeat the element 4 times within its slot |
| Slow | `bd/2` | Stretch the element across 2 cycles |
| Degrade | `hh?` | Play the element with probability $\tfrac{1}{2}$ |

In the assignment that accompanies this module, you will extend the grammar with alternation `<a b c>`, Euclidean rhythms `bd(3,8)`, and polymeter `{a b, c d e}`.

**Syntax and semantics will be cleanly separated.** The parser's job ends when it produces an **abstract syntax tree (AST)**; a separate evaluator walks that tree and assigns each event a span of musical time. Holding that boundary firmly is the central discipline of this course, and we will see in Section 8 that the evaluator is where the musical meaning lives.

---

## 2. Where Mini-Notation Sits in the Chomsky Hierarchy

**Tokens are regular; structure is context-free.** Recall the language classes from our earlier modules. The individual tokens of mini-notation, sample names like `bd`, integers like `8`, and single-character operators, are each describable by **regular expressions**, so a finite automaton suffices to recognize them. The bracketing structure is another matter: groups nest arbitrarily, as in `[[bd sn] [hh [cp cp]]]`, and we proved earlier in the course that the language of balanced brackets

$$
L = \{\, [^n\, ]^n : n \geq 0 \,\}
$$

is not regular, by a pumping-lemma argument: a DFA with $k$ states cannot distinguish $[^k$ from $[^{k+j}$ for some $j > 0$, so it must accept some unbalanced string if it accepts all balanced ones. Nesting therefore demands at least a **context-free grammar**, and this division of labor is exactly why the classical pipeline has two stages:

$$
\text{characters} \xrightarrow{\ \text{flex (regular)}\ } \text{tokens} \xrightarrow{\ \text{yacc (context-free)}\ } \text{AST}
$$

**This is the same architecture as every production compiler.** Clang, `javac`, and the Strudel mini-notation parser (written with a parsing expression grammar tool in JavaScript) all separate a lexical layer from a syntactic layer. Within the scope of languages whose tokens are regular and whose structure is context-free, which covers nearly every programming language you will encounter, this two-stage design is the standard engineering decomposition.

[[MC]]
A classmate proposes recognizing the entire mini-notation, including arbitrarily nested groups, with one large regular expression. Which statement best evaluates this proposal?
- ( ) It works, because every finite string is regular and all patterns are finite strings.
- (x) It fails in general, because matching arbitrarily nested brackets requires counting that no finite automaton can perform.
- ( ) It works only if the regular expression engine supports the `*` operator.
- ( ) It fails because regular expressions cannot describe multi-character tokens like `bd`.

---

## 3. Lexical Analysis: From Regular Expressions to a Scanner

**A flex specification is a list of (pattern, action) pairs.** Flex compiles each regular expression into an NFA via Thompson's construction, merges them, and applies the subset construction to obtain a single DFA, so the generated scanner runs in time $O(n)$ in the input length $n$, touching each character a constant number of times. Two disambiguation rules govern the merged automaton, and you should commit them to memory because they explain almost every surprising scanner behavior you will ever debug:

**Maximal munch.** The scanner always takes the longest match available. Given input `bd2`, the `WORD` rule consumes all three characters rather than stopping at `bd`.

**Rule priority.** Among rules matching the same longest lexeme, the one listed first in the specification wins. If a keyword rule and an identifier rule both match `if`, listing the keyword first makes it a keyword.

**The token set for our subset.** We need names, numbers, the rest symbol, brackets, and three operator characters:

$$
\texttt{WORD} = [a\text{-}zA\text{-}Z][a\text{-}zA\text{-}Z0\text{-}9]^* \qquad \texttt{NUMBER} = [0\text{-}9]^+
$$

with the single-character tokens `~ [ ] * / ?` passed through directly.

---

## Code Cell

```c
/* mininotation.l : flex specification for the mini-notation subset.
   Each rule pairs a regular expression with a C action.
   Compile chain:  flex mininotation.l  ->  lex.yy.c            */

%{
#include "mininotation.tab.h"   /* token codes generated by bison */
#include <stdlib.h>
#include <string.h>
%}

%option noyywrap

%%

[a-zA-Z][a-zA-Z0-9]*   { yylval.str = strdup(yytext); return WORD;   }
[0-9]+                 { yylval.num = atoi(yytext);   return NUMBER; }
"~"                    { return REST;   }
"["                    { return LBRACK; }
"]"                    { return RBRACK; }
"*"                    { return STAR;   }
"/"                    { return SLASH;  }
"?"                    { return QMARK;  }
[ \t\r\n]+             { /* whitespace separates tokens; discard */  }
.                      { fprintf(stderr, "[lexer] unexpected character '%s'\n", yytext); }

%%
```

The `yylval` union carries each token's **semantic value** (the lexeme string for a `WORD`, the integer for a `NUMBER`) across the interface to the parser, while the return value carries the **token category**. Distinguishing category from value is the lexical analogue of the syntax/semantics boundary we maintain throughout the pipeline.

---

### Try It: Individually

Before reading further, predict the token stream that this scanner emits for the input `bd [sn sn]*2 ~`. Write your answer as a sequence of (category, value) pairs, then check it against the table below.

| Lexeme | Category | Semantic value |
|--------|----------|----------------|
| `bd` | `WORD` | `"bd"` |
| `[` | `LBRACK` | (none) |
| `sn` | `WORD` | `"sn"` |
| `sn` | `WORD` | `"sn"` |
| `]` | `RBRACK` | (none) |
| `*` | `STAR` | (none) |
| `2` | `NUMBER` | `2` |
| `~` | `REST` | (none) |

Notice that whitespace has vanished entirely, and that the scanner has no opinion about whether `]` was ever preceded by a matching `[`. Balance is the parser's problem.

---

## 4. A Grammar for the Mini-Notation

**We now give the structure of patterns as a context-free grammar.** Let $G = (V, \Sigma, R, S)$ with start symbol `pattern`. We write the productions in the notation yacc accepts, where `|` separates alternatives:

```
pattern  -> sequence

sequence -> sequence term
          | term

term     -> term STAR NUMBER
          | term SLASH NUMBER
          | term QMARK
          | atom

atom     -> WORD
          | REST
          | LBRACK sequence RBRACK
```

Three design decisions in this grammar repay close reading, because each one encodes a fact about the language into the shape of the productions.

**Left recursion implements left associativity, and yacc welcomes it.** The production `sequence -> sequence term` grows sequences to the left, so `bd sn hh` parses as `((bd sn) hh)`. A bottom-up LALR parser handles left recursion in constant stack space per reduction, whereas a top-down recursive-descent parser would loop forever on it. This is precisely opposite to the transformation you performed when we built recursive-descent parsers by hand earlier in the semester, and recognizing which parser family you are targeting is part of grammar literacy.

**Postfix operators bind tightly because `term` is recursive through itself.** In `hh*2?`, the derivation forces `(hh*2)?`: degrade applies to the already-sped-up element. The grammar, not a comment in the documentation, is what guarantees this.

**Nesting comes for free.** Because `atom` can derive `LBRACK sequence RBRACK` and `sequence` derives `term` derives `atom`, groups nest to any depth with no further mechanism. Compare the contortions Section 2 showed a regular language would require.

**A derivation, worked in full.** For the input `bd [sn sn]`, one leftmost derivation is:

$$
\begin{aligned}
\texttt{pattern} &\Rightarrow \texttt{sequence} \\
&\Rightarrow \texttt{sequence}\ \texttt{term} \\
&\Rightarrow \texttt{term}\ \texttt{term} \\
&\Rightarrow \texttt{atom}\ \texttt{term} \\
&\Rightarrow \texttt{WORD(bd)}\ \texttt{term} \\
&\Rightarrow \texttt{WORD(bd)}\ \texttt{atom} \\
&\Rightarrow \texttt{WORD(bd)}\ \texttt{LBRACK}\ \texttt{sequence}\ \texttt{RBRACK} \\
&\Rightarrow^{*} \texttt{WORD(bd)}\ \texttt{LBRACK}\ \texttt{WORD(sn)}\ \texttt{WORD(sn)}\ \texttt{RBRACK}
\end{aligned}
$$

---

### Try It: With a Partner

Work in pairs, with one of you serving as **derivation writer** and the other as **verifier**, then swap roles for the second string. For each input below, the writer produces a leftmost derivation on paper while the verifier independently draws the parse tree, and you then reconcile the two artifacts, which must agree.

1. `hh*4 ~ hh*4 ~`
2. `[bd [sn sn]]/2`

When you reconcile, discuss this question and record a one-sentence answer: in string 2, does `/2` apply to the inner group `[sn sn]` or the outer group? Which production in the grammar settles the question?

---

[[MC]]
In the grammar above, the input `bd*2/3` parses with which effective grouping, and why?
- (x) `(bd*2)/3`, because `term` is left-recursive through the postfix operator productions, so operators accumulate left to right.
- ( ) `bd*(2/3)`, because `NUMBER SLASH NUMBER` forms a fraction at the lexical level.
- ( ) The input is a syntax error, because two postfix operators may never apply to one atom.
- ( ) The grouping is ambiguous, and yacc resolves it arbitrarily at run time.

---

## 5. How Yacc Parses: LR Items, States, and the LALR(1) Idea

**Yacc builds a shift-reduce parser driven by a finite automaton over grammar items.** An **LR(0) item** is a production with a dot marking parsing progress, such as

$$
\texttt{term} \rightarrow \texttt{term} \cdot \texttt{STAR}\ \texttt{NUMBER}
$$

which reads "we have parsed a `term` and will accept this production if `STAR NUMBER` comes next." The parser generator closes sets of items into **states**, connects them with transitions on grammar symbols, and emits two tables: an **action** table (shift, reduce, accept, or error, indexed by state and lookahead token) and a **goto** table (next state after a reduction). At run time the parser is breathtakingly simple, which is the point: a loop, a stack, and table lookups, running in $O(n)$ time and using stack space proportional to the deepest nesting in the input.

### Pseudocode

```
function LR-PARSE(tokens):
    push state 0
    a = first token
    loop:
        s = state on top of stack
        if ACTION[s, a] = shift t:
            push a, push state t
            a = next token
        else if ACTION[s, a] = reduce (A -> beta):
            pop 2 * |beta| entries
            t = state now on top
            push A, push GOTO[t, A]
            (run the semantic action for A -> beta here)
        else if ACTION[s, a] = accept:
            return the finished parse
        else:
            report syntax error at a
```

**LALR(1) is LR(1) with merged states.** Full LR(1) tables distinguish states by lookahead and grow large; LALR(1) merges LR(1) states that share the same item cores, keeping the table compact at the cost of accepting a slightly smaller family of grammars. Our mini-notation grammar is comfortably LALR(1): you can verify with `bison -v mininotation.y`, which writes the full automaton, every state and item set, to `mininotation.output`. Reading that file once, slowly, will teach you more about LR parsing than any lecture, and we will do exactly that in the partner activity below.

**Conflicts are the diagnostic signal.** A **shift/reduce conflict** means some state sees a lookahead for which both shifting and reducing are table-legal; a **reduce/reduce conflict** means two completed productions compete. Our grammar produces neither, but you will manufacture one, deliberately, in a moment, because learning to read conflict reports is the practical skill that separates people who can use parser generators from people who fight them.

---

### Try It: With a Partner

One partner is the **saboteur** and the other is the **diagnostician**; swap after the first round. The saboteur makes exactly one of the following edits to the grammar, without telling the diagnostician which:

1. Change `sequence -> sequence term` to the ambiguous `sequence -> sequence sequence | term`.
2. Add a redundant production `atom -> WORD QMARK` alongside the existing `term -> term QMARK`.

Run `bison -v mininotation.y`. The diagnostician must, using only bison's stderr output and the `.output` file, identify which edit was made, name the conflict type, and point to the state and item set where it arises. Record the state number and one sentence of explanation before swapping.

---

## 6. The Yacc Specification: Grammar Plus Semantic Actions

**Each production carries an action that builds one AST node.** In yacc actions, `$$` denotes the semantic value of the left-hand side and `$1, $2, \ldots` the values of the right-hand-side symbols in order. The actions below are deliberately uniform: every production either passes a subtree upward or wraps its children in exactly one new node. When actions stay this disciplined, the AST is a faithful image of the derivation, and debugging the parser reduces to printing trees.

---

## Code Cell

```c
/* mininotation.y : bison/yacc specification with AST-building actions.
   Compile chain:
     bison -d mininotation.y      -> mininotation.tab.c, mininotation.tab.h
     flex  mininotation.l         -> lex.yy.c
     gcc -o mininote mininotation.tab.c lex.yy.c ast.c eval.c -lfl        */

%{
#include <stdio.h>
#include <stdlib.h>
#include "ast.h"

int  yylex(void);
void yyerror(const char *msg) {
    fprintf(stderr, "[parser] %s\n", msg);
}

Node *ast_root = NULL;
%}

%union {
    char *str;
    int   num;
    struct Node *node;
}

%token <str> WORD
%token <num> NUMBER
%token REST LBRACK RBRACK STAR SLASH QMARK

%type <node> pattern sequence term atom

%%

pattern  : sequence                      { ast_root = $1; }
         ;

sequence : sequence term                 { $$ = seq_append($1, $2); }
         | term                          { $$ = seq_new($1);        }
         ;

term     : term STAR NUMBER              { $$ = node_fast($1, $3);  }
         | term SLASH NUMBER             { $$ = node_slow($1, $3);  }
         | term QMARK                    { $$ = node_degrade($1);   }
         | atom                          { $$ = $1;                 }
         ;

atom     : WORD                          { $$ = node_atom($1);      }
         | REST                          { $$ = node_rest();        }
         | LBRACK sequence RBRACK        { $$ = node_group($2);     }
         ;

%%
```

---

**The AST node type is a small tagged union, the C ancestor of the algebraic data types you know from Haskell.** When we study TidalCycles' host language, you will meet the direct analogue, and seeing the C encoding first makes the Haskell version feel like a kindness:

---

## Code Cell

```c
/* ast.h : tagged-union AST for mini-notation.
   Compare with a Haskell ADT, which says the same thing in five lines:
     data Node = Atom String | Rest | Seq [Node] | Group Node
               | Fast Node Int | Slow Node Int | Degrade Node        */

#ifndef AST_H
#define AST_H

typedef enum { N_ATOM, N_REST, N_SEQ, N_GROUP,
               N_FAST, N_SLOW, N_DEGRADE } NodeType;

typedef struct Node {
    NodeType type;
    char *name;              /* N_ATOM: sample name                  */
    int factor;              /* N_FAST / N_SLOW: the integer operand */
    struct Node **children;  /* N_SEQ: ordered children              */
    int nchildren;
    struct Node *child;      /* unary wrappers: GROUP, FAST, SLOW,
                                DEGRADE                              */
} Node;

Node *node_atom(char *name);
Node *node_rest(void);
Node *seq_new(Node *first);
Node *seq_append(Node *seq, Node *next);
Node *node_group(Node *seq);
Node *node_fast(Node *child, int k);
Node *node_slow(Node *child, int k);
Node *node_degrade(Node *child);

#endif
```

---

### Try It: Individually

Draw, by hand, the AST that the actions above construct for the input `bd [sn sn] hh*2 ~`. Label every node with its `NodeType`. Then answer in one sentence each:

1. How many `N_SEQ` nodes does your tree contain, and why is the answer not one?
2. Which node is the parent of the `N_FAST` node, and which production created that parent?

---

## 7. Driving the Pipeline End to End

**A small `main` connects the stages.** The program reads a pattern from standard input, invokes `yyparse()`, which internally calls `yylex()` on demand, and then hands the resulting tree to a printer and an evaluator.

---

## Code Cell

```c
/* main.c : end-to-end driver.
   Example session:
     $ echo "bd [sn sn] hh*2 ~" | ./mininote
     SEQ
       ATOM bd
       GROUP
         SEQ
           ATOM sn
           ATOM sn
       FAST 2
         ATOM hh
       REST
     events in cycle [0,1):
       bd   [0.000, 0.250)
       sn   [0.250, 0.375)
       sn   [0.375, 0.500)
       hh   [0.500, 0.625)
       hh   [0.625, 0.750)                                            */

#include <stdio.h>
#include "ast.h"

extern int yyparse(void);
extern Node *ast_root;

void ast_print(Node *n, int depth);             /* in ast.c  */
void eval_pattern(Node *n, double t0, double t1); /* in eval.c */

int main(void) {
    if (yyparse() != 0 || ast_root == NULL) {
        fprintf(stderr, "[main] parse failed\n");
        return 1;
    }
    ast_print(ast_root, 0);
    printf("events in cycle [0,1):\n");
    eval_pattern(ast_root, 0.0, 1.0);
    return 0;
}
```

---

## 8. Semantics: From Trees to Time

**Now, and only now, do we assign meaning.** The denotation of a pattern is a set of **events**, each a sample name paired with a half-open time span $[t_0, t_1) \subseteq [0, 1)$ within the cycle. We define the evaluation function $\mathcal{E}[\![\, n \,]\!](t_0, t_1)$ by structural recursion on the AST, one clause per node type, and this is your first denotational semantics written in C rather than on a whiteboard:

$$
\mathcal{E}[\![\, \texttt{SEQ}(c_1, \ldots, c_k) \,]\!](t_0, t_1) \;=\; \bigcup_{i=1}^{k}\; \mathcal{E}[\![\, c_i \,]\!]\!\left( t_0 + \tfrac{(i-1)\,\Delta}{k},\; t_0 + \tfrac{i\,\Delta}{k} \right), \quad \Delta = t_1 - t_0
$$

$$
\mathcal{E}[\![\, \texttt{FAST}(c, m) \,]\!](t_0, t_1) \;=\; \bigcup_{j=0}^{m-1}\; \mathcal{E}[\![\, c \,]\!]\!\left( t_0 + \tfrac{j\,\Delta}{m},\; t_0 + \tfrac{(j+1)\,\Delta}{m} \right)
$$

$$
\mathcal{E}[\![\, \texttt{ATOM}(s) \,]\!](t_0, t_1) = \{ (s, t_0, t_1) \} \qquad
\mathcal{E}[\![\, \texttt{REST} \,]\!](t_0, t_1) = \varnothing
$$

A `GROUP` is semantically transparent, evaluating its child on the same span, because the brackets did their work during parsing by controlling how the tree was built. Read that sentence twice: it is the clearest example in this module of syntax and semantics dividing the labor.

---

## Code Cell

```c
/* eval.c : structural recursion implementing the semantics above.
   Each case implements exactly one displayed equation; the SEQ case
   implements the first equation, and the FAST case the second.      */

#include <stdio.h>
#include "ast.h"

void eval_pattern(Node *n, double t0, double t1) {
    double span = t1 - t0;
    switch (n->type) {

    case N_ATOM:                       /* E[[ATOM s]](t0,t1) = {(s,t0,t1)} */
        printf("  %-4s [%.3f, %.3f)\n", n->name, t0, t1);
        break;

    case N_REST:                       /* E[[REST]] = empty set            */
        break;

    case N_SEQ:                        /* subdivide the span evenly        */
        for (int i = 0; i < n->nchildren; i++) {
            double a = t0 + span * i       / n->nchildren;
            double b = t0 + span * (i + 1) / n->nchildren;
            eval_pattern(n->children[i], a, b);
        }
        break;

    case N_GROUP:                      /* transparent: same span           */
        eval_pattern(n->child, t0, t1);
        break;

    case N_FAST:                       /* m copies, each on span/m         */
        for (int j = 0; j < n->factor; j++) {
            double a = t0 + span * j       / n->factor;
            double b = t0 + span * (j + 1) / n->factor;
            eval_pattern(n->child, a, b);
        }
        break;

    case N_SLOW:
        /* Scaffolded for you: SLOW stretches its child across `factor`
           cycles, so within THIS cycle you play a 1/factor "window" of
           the child. Decide which window, and justify your choice in a
           comment. Hint: you will need a notion of the current cycle
           number; consider passing it as a parameter.                  */
        fprintf(stderr, "[eval_pattern:N_SLOW] not yet implemented\n");
        break;

    case N_DEGRADE:
        /* Scaffolded for you: with probability 1/2, evaluate the child;
           otherwise emit nothing. For reproducible grading, seed the
           generator deterministically: srand(42) once in main.         */
        fprintf(stderr, "[eval_pattern:N_DEGRADE] not yet implemented\n");
        break;
    }
}
```

---

**Verification against the reference implementation.** Strudel runs in any browser at [strudel.cc](https://strudel.cc). Enter `sound("bd [sn sn] hh*2 ~")`, press play, and watch the highlighted event spans in the editor; they are the very intervals your evaluator prints. Within the subset we implemented, your C program and a production live coding system now agree on the meaning of every pattern, and that agreement, a hand-built artifact validated against a real language, is the experience this course is designed around.

[[MC]]
For the input `[bd sn]*2`, how many events does the semantics above produce in one cycle, and on what spans?
- ( ) Two events: `bd` on $[0, 0.5)$ and `sn` on $[0.5, 1)$.
- (x) Four events: `bd` on $[0, 0.25)$, `sn` on $[0.25, 0.5)$, `bd` on $[0.5, 0.75)$, `sn` on $[0.75, 1)$.
- ( ) Two events: `bd` on $[0, 0.25)$ and `sn` on $[0.25, 0.5)$, with silence afterward.
- ( ) Eight events, because the group doubles and the sequence doubles again.

---

# Part III: Synthesis & Practice

## 9. Exercises

The first three exercises are designed for individual work in class today; the final two are partner exercises, and you should complete at least one of them with a classmate before the next session.

1. *Trace the tables.* Run `bison -v mininotation.y` and open `mininotation.output`. For the input `bd*2`, list, in order, every shift and reduce action the parser performs, citing state numbers from the file. Report the maximum stack depth reached.
2. *Implement SLOW.* Complete the `N_SLOW` case in `eval.c`, extending `eval_pattern` with a cycle-number parameter. Demonstrate on `bd/2 sn` across cycles 0 and 1, and report the printed event list for both cycles.
3. *Implement DEGRADE reproducibly.* Complete the `N_DEGRADE` case with a deterministic seed, run `hh*8?` three times, and confirm identical output across runs. Report the surviving event spans.
4. *Partner: grammar extension.* With a partner, extend the grammar and lexer to support alternation `<a b c>`, which plays one element per cycle in rotation. One partner writes the flex and yacc changes; the other writes the `N_ALT` evaluator case; integrate and test on `bd <sn cp hh>` across three cycles. Report which design questions required negotiation between the syntax side and the semantics side.
5. *Partner: break it and read the report.* Each partner independently introduces one grammar ambiguity, exchanges files, and diagnoses the other's conflict using only the `.output` file, naming the conflict type and the state where it occurs. Report both diagnoses and confirm them against the original edits.

---

## 10. Further Reading

- Aho, Lam, Sethi, and Ullman. *Compilers: Principles, Techniques, and Tools* (2nd ed., 2006). Chapters 3 and 4 are the canonical treatment of lexical analysis and LR parsing; Section 4.7 covers the LALR construction used by yacc.
- Levine, John. *flex & bison* (O'Reilly, 2009). The practical handbook for the exact tools used in this module, including conflict debugging workflows.
- McLean, Alex. "Making Programming Languages to Dance to: Live Coding with Tidal." *FARM Workshop, ICFP* (2014). The design rationale for TidalCycles and its mini-notation, written by the language's creator.
- The Strudel project, [strudel.cc](https://strudel.cc) and its documentation. The reference implementation against which we validated our evaluator; the mini-notation parser source is openly available and worth reading after this module.
- Johnson, Stephen C. "Yacc: Yet Another Compiler-Compiler." *Bell Laboratories Computing Science Technical Report 32* (1975). The original report; short, readable, and historically grounding.

---
