---
layout: default-standard
permalink: /Tools/BNFTester
title: "CS374: BNF/EBNF Tester"
---

# BNF/EBNF Grammar Tester

Type a grammar, then type a string, and the tester tells you whether the grammar can derive that string.  When it can, you see the parse tree and a leftmost derivation written the way the labs write them.  When it cannot, you see where it got stuck and what the grammar would have accepted there.  It runs entirely in your browser: nothing is sent anywhere, and there is no account.

Two settings matter before you start:

- **Notation.**  *Course notation* is the one the BNF Workshop uses: `<name> ::= "x" <other> | <empty>`.  *Token notation* is the one the Grammar and Derivations Workshop and the Parser assignment use: bare lowercase rule names, UPPERCASE token names, and a space-separated token stream as the input.
- **Allow EBNF.**  This is off by default, so a plain-BNF exercise cannot slip into EBNF by accident.  With it off, the tester stops at the first `{ }`, `[ ]`, `( )`, `*`, `+` or `?` and tells you how to write that construct with recursion instead.  Tick it only when the exercise permits EBNF.

<link rel="stylesheet" href="{{ site.baseurl }}/files/tools/bnf-tester/bnf-tester.css">

<div class="bnf-app">

<div class="bnf-panel bnf-controls" role="group" aria-label="Grammar settings">
  <div class="bnf-control">
    <label for="bnf-notation">Notation</label>
    <select id="bnf-notation">
      <option value="course">Course notation: &lt;name&gt; ::= "x"</option>
      <option value="token">Token notation: name ::= TOKEN</option>
    </select>
  </div>
  <div class="bnf-control">
    <input type="checkbox" id="bnf-ebnf">
    <label for="bnf-ebnf">Allow EBNF</label>
    <span id="bnf-badge" class="bnf-badge bnf-badge-bnf">Plain BNF</span>
    <span class="bnf-small">(enables <span id="bnf-ebnfWhat">{ }, [ ], ( )</span>)</span>
  </div>
  <div class="bnf-control" id="bnf-wsRow">
    <input type="checkbox" id="bnf-ws" checked>
    <label for="bnf-ws">Ignore whitespace between terminals</label>
  </div>
  <div class="bnf-control">
    <label for="bnf-example">Load an example</label>
    <select id="bnf-example">
      <option value="">Choose…</option>
    </select>
  </div>
</div>

<div class="bnf-panel">
  <label class="bnf-field-label" for="bnf-grammar">Grammar (the first rule is the start symbol unless you choose another below)</label>
  <textarea id="bnf-grammar" spellcheck="false" autocomplete="off" autocapitalize="off"></textarea>
  <div id="bnf-messages" aria-live="polite"></div>
</div>

<div class="bnf-panel">
  <div class="bnf-row" style="margin-top:0">
    <label class="bnf-field-label" for="bnf-start" style="margin:0">Start symbol</label>
    <select id="bnf-start"></select>
  </div>
  <label class="bnf-field-label" id="bnf-inputLabel" for="bnf-input" style="margin-top:10px">String to test</label>
  <input type="text" id="bnf-input" class="bnf-mono" spellcheck="false" autocomplete="off" autocapitalize="off">
  <div class="bnf-row">
    <button type="button" class="bnf-btn" id="bnf-testBtn">Test string</button>
    <button type="button" class="bnf-btn bnf-btn-secondary" id="bnf-genBtn">Generate a random string</button>
    <button type="button" class="bnf-btn bnf-btn-secondary" id="bnf-shareBtn">Copy share link</button>
    <span id="bnf-shareStatus" class="bnf-small" aria-live="polite"></span>
  </div>
</div>

<div class="bnf-panel" id="bnf-result" aria-live="polite">
  <p class="bnf-muted">Loading the tester…  If this message stays, JavaScript is turned off in your browser.</p>
</div>

</div>

<script src="{{ site.baseurl }}/files/tools/bnf-tester/bnf-engine.js"></script>
<script src="{{ site.baseurl }}/files/tools/bnf-tester/bnf-ui.js"></script>

<div id="bnf-helpCourse" markdown="1">

## Course Notation Cheat Sheet

This is the notation table from the BNF Workshop.  Everything in the top half works in plain BNF; the bottom half needs **Allow EBNF**.

| You write | It means | Example |
|---|---|---|
| `<name> ::= ...` | a production: the nonterminal on the left is defined by the right side | <code>&lt;sign&gt; ::= "+" &#124; "-"</code> |
| `<name>` | a nonterminal, which must have its own production somewhere | `<digit>` |
| `"x"` or `'x'` | a terminal, the literal text that appears in the string | `"("` |
| <code>&#124;</code> | alternation: exactly one of the choices is used | <code>"+" &#124; "-"</code> |
| `<empty>` | the empty string, the BNF way to let a recursive rule stop | <code>&lt;exprs&gt; ::= &lt;expr&gt; &lt;exprs&gt; &#124; &lt;empty&gt;</code> |
| `(* ... *)` | a comment, ignored by the tester | `(* spaces ignored between atoms *)` |
| `{ X }` (EBNF) | zero or more copies of `X` | `{ <digit> }` |
| `[ X ]` (EBNF) | `X` once or not at all | `[ <sign> ]` |
| <code>( X &#124; Y )</code> (EBNF) | grouping inside a larger rule | <code>( "," &#124; ";" )</code> |

A production may continue onto the next line, the way the labs line up long alternatives under the `::=`.

**About whitespace.**  With *Ignore whitespace between terminals* ticked, spaces, tabs and newlines may appear between any two terminals, which is what the labs mean by "spaces ignored between atoms."  The catch is that this also lets a space appear *inside* a token that your grammar spells one character at a time, so `1 2` is accepted as the number `12`.  To test spacing rules exactly, untick the box and write the whitespace into the grammar yourself, for example `<ws> ::= " " <ws> | " "`.

</div>

<div id="bnf-helpToken" markdown="1" hidden>

## Token Notation Cheat Sheet

This is the notation of the Grammar and Derivations Workshop and the Parser assignment.  A grammar here describes a stream of tokens that your lexer has already produced, so the input is a space-separated list of token names such as `INT PLUS INT STAR INT`.  You may also paste the workshop's form `INT(2) PLUS INT(3)`: the tester reads `INT(2)` as `INT`.

| You write | It means | Example |
|---|---|---|
| `name ::= ...` | a production for the lowercase nonterminal `name` | <code>factor ::= INT &#124; LPAREN expr RPAREN</code> |
| `UPPERCASE` | a token from your lexer, matched against one input token | `PLUS`, `INT`, `IDENT` |
| `"x"` | a literal token, matched against an input token spelled `x` | `";"` |
| <code>&#124;</code> | alternation | <code>INT &#124; IDENT</code> |
| `ε` | the empty string | <code>args ::= expr more &#124; ε</code> |
| `// ...` | a comment to the end of the line | `// decide how ELSE attaches` |
| `( ... )` (EBNF) | grouping | `( COLON type )` |
| `X*` `X+` `X?` (EBNF) | zero or more, one or more, optional | `( PLUS term )*` |

If a rule ends with the token `EOF` and your input does not, the tester adds `EOF` for you and says so.  A name that is lowercase and has no rule is reported as undefined, which catches a misspelled nonterminal before it silently becomes a token.

</div>

## What the Results Tell You

- **Accepted** comes with a parse tree built from your own nonterminals.  EBNF shortcuts are expanded in place, so a `{ <digit> }` shows up as however many `<digit>` children the string needed.  Click a node to fold it, or open the plain-text version to paste into a write-up.
- **Leftmost derivation** replaces the leftmost nonterminal at every step and cites the production it used, in the same `=> ... [<expr> ::= <list>]` style as the labs.
- **Ambiguous** means the tester found two different parse trees for the same input.  One such string is enough to prove a grammar ambiguous, and you can switch between the two trees to see exactly where they disagree.
- **Rejected** highlights the first character (or token) the grammar could not get past, and lists the terminals it would have accepted there.  "Ended too early" means your input is a correct beginning that stops before any rule is finished.
- **Grammar messages** appear as you type: undefined nonterminals (the most common lost point in the BNF Workshop), rules that are never used or never reachable from the start symbol, rules that can never finish, and a note when a rule is left-recursive, which is fine here but loops forever in a recursive-descent parser.

The tester accepts every context-free grammar, including left-recursive and ambiguous ones, because it parses with Earley's algorithm rather than with recursive descent.  It checks your grammar; it does not grade it.  An accepted string shows that your grammar *can* derive it, so also test strings that should be *rejected*, which is where most grammar mistakes hide.
