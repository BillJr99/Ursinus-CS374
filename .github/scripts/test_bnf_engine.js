#!/usr/bin/env node
/*
 * Tests for the BNF/EBNF Tester engine (files/tools/bnf-tester/bnf-engine.js).
 *
 * Run from the repository root:
 *
 *     node .github/scripts/test_bnf_engine.js
 *
 * Exits non-zero and names every failing case.
 */
'use strict';

const path = require('path');
const E = require(path.join(__dirname, '..', '..', 'files', 'tools', 'bnf-tester', 'bnf-engine.js'));

let failures = 0;
let passes = 0;

function check(label, cond, detail) {
  if (cond) { passes++; return; }
  failures++;
  console.log('FAIL: ' + label + (detail ? '\n      ' + detail : ''));
}

function compileOk(label, src, opts) {
  const c = E.compile(src, opts);
  check(label + ' compiles', c.ok, c.errors.map(e => e.msg + ' ' + e.hint).join(' | '));
  return c;
}

function accepts(c, label, input, opts) {
  if (!c.ok) return;
  const r = E.test(c, input, opts);
  check(label + ' accepts ' + JSON.stringify(input), r.accepted, r.error && r.error.msg);
  return r;
}

function rejects(c, label, input, opts) {
  if (!c.ok) return;
  const r = E.test(c, input, opts);
  check(label + ' rejects ' + JSON.stringify(input), !r.accepted);
  return r;
}

function errorMatches(label, src, opts, re) {
  const c = E.compile(src, opts);
  const text = c.errors.map(e => e.msg + ' ' + e.hint).join(' | ');
  check(label, !c.ok && re.test(text), 'errors were: ' + (text || '(none)'));
}

// --- The BNF Workshop's EBNF warm-up, lab-bnfworkshop.md -----------------
const WARMUP = `
(* Sequence: symbols on the right side must appear in this order. *)
<entry>  ::= <name> ":" <number>
<name>   ::= <letter> { <letter> }
<letter> ::= "a" | "b" | "c" | "x" | "y" | "z"
(* Alternation: | separates choices; exactly one is used. *)
<sign>   ::= "+" | "-"
(* Repetition: { X } means zero or more copies of X. *)
<digits> ::= <digit> { <digit> }
<digit>  ::= "0" | "1" | "2" | "3" | "4" | "5" | "6" | "7" | "8" | "9"
(* Optionality: [ X ] means X appears once or not at all. *)
<number> ::= [ <sign> ] <digits>
(* Grouping: ( X | Y ) treats the alternatives as one unit inside a larger rule. *)
<pair>   ::= <number> ( "," | ";" ) <number>
`;
{
  const c = compileOk('warm-up (EBNF)', WARMUP, { notation: 'course', ebnf: true });
  accepts(c, 'warm-up', 'abc:42');
  accepts(c, 'warm-up', 'x : -7');
  accepts(c, 'warm-up', 'zz:+0');
  rejects(c, 'warm-up', 'abc:');
  rejects(c, 'warm-up', ':42');
  rejects(c, 'warm-up', 'abc:4-2');
  accepts(c, 'warm-up <pair>', '1,-2', { start: 'pair' });
  accepts(c, 'warm-up <pair>', '+10 ; 3', { start: 'pair' });
  rejects(c, 'warm-up <pair>', '1.2', { start: 'pair' });
  rejects(c, 'warm-up exact whitespace', 'x : 7', { skipWs: false });
  accepts(c, 'warm-up exact whitespace', 'x:7', { skipWs: false });
  const r = E.test(c, 'abc:42');
  check('warm-up is unambiguous', r.accepted && !r.ambiguous);
  check('warm-up tree hides EBNF helpers', r.treeTexts && !/·/.test(r.treeTexts[0]), r.treeTexts && r.treeTexts[0]);
  check('warm-up tree names the start symbol', r.treeTexts && r.treeTexts[0].split('\n')[0] === '<entry>');
  // Same grammar with EBNF turned off must refuse, and say why.
  errorMatches('warm-up in BNF mode names the EBNF construct', WARMUP, { notation: 'course', ebnf: false },
    /EBNF repetition.*EBNF is turned off/);
}

// --- Model 1.5, the grammar Part 0 extends -----------------------------
const MODEL15 = `
<expr>  ::= <atom> | <list>
<list>  ::= "(" <exprs> ")"
<exprs> ::= <expr> <exprs> | <empty>
<atom>  ::= <number> | <symbol>
`;
errorMatches('Model 1.5 as given reports the two undefined nonterminals', MODEL15, { notation: 'course' },
  /<number> is used but never defined[\s\S]*<symbol> is used but never defined/);
{
  const full = MODEL15 + `
<number> ::= <digit> | <digit> <number>
<digit>  ::= "0" | "1" | "2" | "3"
<symbol> ::= "+" | "*" | "-"
`;
  const c = compileOk('Model 1.5 completed (BNF)', full, { notation: 'course', ebnf: false });
  const r = accepts(c, 'Model 1.5', '(+ 1 (* 2 3))');
  accepts(c, 'Model 1.5', '()');
  accepts(c, 'Model 1.5', '12');
  rejects(c, 'Model 1.5', '(+ 1 (* 2 3)');
  rejects(c, 'Model 1.5', ')(');
  if (r && r.accepted) {
    const steps = r.derivations[0].steps;
    check('derivation starts at <expr>', steps[0].form === '<expr>', steps[0].form);
    check('derivation step 1 uses <expr> ::= <list>', steps[1].rule === '<expr> ::= <list>', steps[1].rule);
    check('derivation step 2 is ( <exprs> )', steps[2].form === '( <exprs> )', steps[2].form);
    check('derivation ends in terminals only', !/[<>]/.test(steps[steps.length - 1].form), steps[steps.length - 1].form);
    check('derivation cites <empty>', steps.some(s => s.rule === '<exprs> ::= <empty>'));
  }
  const bad = E.test(c, '(+ 1 (* 2 3)');
  check('reject at end of input explains it ended early', bad.error && /ended too early/.test(bad.error.msg), bad.error && bad.error.msg);
  check('reject lists ")" as expected', bad.error && bad.error.expected.indexOf('")"') >= 0, bad.error && bad.error.expected.join(' '));
  const stuck = E.test(c, '(+ 7)');
  check('reject in the middle names the position', stuck.error && /Stuck at character 4/.test(stuck.error.msg), stuck.error && stuck.error.msg);
  // Generated strings must be in the language.
  let rng = 1;
  const seeded = () => { rng = (rng * 16807) % 2147483647; return rng / 2147483647; };
  for (let k = 0; k < 25; k++) {
    const s = E.generate(c, 'expr', seeded, true);
    const t = E.test(c, s);
    check('generated string parses: ' + JSON.stringify(s), t.accepted);
  }
}

// --- A right-linear grammar, strings over {a,b} ending in ab ------------
{
  const c = compileOk('right-linear ends-in-ab', `
<s>  ::= "a" <s> | "b" <s> | "a" <t>
<t>  ::= "b"
`, { notation: 'course' });
  accepts(c, 'ends-in-ab', 'ab');
  accepts(c, 'ends-in-ab', 'babab');
  rejects(c, 'ends-in-ab', 'ba');
  rejects(c, 'ends-in-ab', '');
  const r = E.test(c, 'aab');
  check('ends-in-ab has one parse for aab', r.accepted && !r.ambiguous);
}

// --- Regular vs. context-free examples (Grammars deck, Part II) ---------
// Each grammar is checked against a direct definition of its language on
// every string over its alphabet up to length 8.
{
  const cases = [
    ['a^n b^m', `<s> ::= "a" <s> | <t>\n<t> ::= "b" <t> | <empty>`, 'ab', w => /^a*b*$/.test(w)],
    ['ends in ab, right-linear', `<s> ::= "a" <s> | "b" <s> | "a" <t>\n<t> ::= "b"`, 'ab', w => /ab$/.test(w)],
    ['ends in ab, left-linear', `<s> ::= <a> "b"\n<a> ::= <any> "a"\n<any> ::= <any> "a" | <any> "b" | <empty>`, 'ab', w => /ab$/.test(w)],
    ['palindromes', `<p> ::= "a" <p> "a" | "b" <p> "b" | "a" | "b" | <empty>`, 'ab', w => w === [...w].reverse().join('')],
    ['equal counts', `<s> ::= "a" <s> "b" <s> | "b" <s> "a" <s> | <empty>`, 'ab', w => [...w].filter(c => c === 'a').length * 2 === w.length],
    ['depth <= 2', `<d0> ::= "(" <d1> | <empty>\n<d1> ::= "(" <d2> | ")" <d0>\n<d2> ::= ")" <d1>`, '()',
      w => { let d = 0; for (const c of w) { d += c === '(' ? 1 : -1; if (d < 0 || d > 2) return false; } return d === 0; }],
    ['a+ via <s> <s>', `<s> ::= <s> <s> | "a"`, 'ab', w => /^a+$/.test(w)],
  ];
  cases.forEach(([label, g, alpha, inLang]) => {
    const c = compileOk(label, g, { notation: 'course' });
    if (!c.ok) return;
    let wrong = [];
    for (let len = 0; len <= 8; len++) {
      for (let m = 0; m < (1 << len); m++) {
        let w = '';
        for (let i = 0; i < len; i++) w += alpha[(m >> i) & 1];
        if (E.test(c, w, { skipWs: false }).accepted !== inLang(w)) wrong.push(w);
      }
    }
    check(label + ' generates exactly its language up to length 8', wrong.length === 0, 'wrong on: ' + wrong.slice(0, 5).join(', '));
  });
  const eq = E.compile(`<s> ::= "a" <s> "b" <s> | "b" <s> "a" <s> | <empty>`, { notation: 'course' });
  check('equal-counts grammar is reported ambiguous on abab', E.test(eq, 'abab').ambiguous);
}

// --- Empty string and <empty> -------------------------------------------
{
  const c = compileOk('balanced parens', `<b> ::= "(" <b> ")" <b> | <empty>`, { notation: 'course' });
  accepts(c, 'balanced', '');
  accepts(c, 'balanced', '(()())()');
  rejects(c, 'balanced', '(()');
  const r = E.test(c, '');
  check('empty-string derivation ends in the empty string', r.accepted &&
    r.derivations[0].steps[1].form === '(the empty string)', r.derivations && JSON.stringify(r.derivations[0].steps));
}

// --- Left recursion and ambiguity ----------------------------------------
{
  const c = compileOk('left-recursive sum', `
<sum> ::= <sum> "+" <n> | <n>
<n>   ::= "1" | "2"
`, { notation: 'course' });
  accepts(c, 'left-recursive', '1+2+1');
  rejects(c, 'left-recursive', '1++2');
  check('left recursion is noted', c.notes.some(n => /Left recursion: <sum>/.test(n.msg)));
  const r = E.test(c, '1+2+1');
  check('left-recursive sum is unambiguous', r.accepted && !r.ambiguous);
}
{
  const c = compileOk('ambiguous flat grammar (token)', `
expr ::= expr PLUS expr
       | expr MINUS expr
       | expr STAR expr
       | INT
`, { notation: 'token' });
  const r = accepts(c, 'flat grammar', 'INT PLUS INT STAR INT');
  check('flat grammar is reported ambiguous', r && r.ambiguous);
  check('two different trees are returned', r && r.treeTexts.length === 2 && r.treeTexts[0] !== r.treeTexts[1]);
  const one = E.test(c, 'INT PLUS INT');
  check('one operator is not ambiguous', one.accepted && !one.ambiguous);
  accepts(c, 'flat grammar', 'INT(2) PLUS INT(3)');
  rejects(c, 'flat grammar', 'INT PLUS');
}

// --- Token notation: the Grammar Workshop ladder --------------------------
const LADDER = `
expr    ::= term ( PLUS term )*
term    ::= factor ( STAR factor )*
factor  ::= INT | LPAREN expr RPAREN
`;
{
  const c = compileOk('Grammar Workshop ladder (token, EBNF)', LADDER, { notation: 'token', ebnf: true });
  const r = accepts(c, 'ladder', 'INT PLUS INT STAR INT');
  accepts(c, 'ladder', 'LPAREN INT PLUS INT RPAREN STAR INT');
  rejects(c, 'ladder', 'INT PLUS PLUS INT');
  rejects(c, 'ladder', 'LPAREN INT');
  check('ladder is unambiguous', r && !r.ambiguous);
  check('ladder tree prints tokens bare', r && /INT/.test(r.treeTexts[0]) && !/"INT"/.test(r.treeTexts[0]), r && r.treeTexts[0]);
  errorMatches('ladder in BNF mode names grouping', LADDER, { notation: 'token', ebnf: false }, /EBNF grouping/);
}
{
  const c = compileOk('token notation with literals, ?, + and EOF', `
program ::= stmt+ EOF
stmt    ::= LET IDENT ( COLON type )? EQ INT ";"   // a let statement
type    ::= "int" | "bool"
`, { notation: 'token', ebnf: true });
  const r = accepts(c, 'program', 'LET IDENT EQ INT ; LET IDENT COLON int EQ INT ;');
  check('EOF is added automatically, with a note', r && r.notes.some(n => /EOF/.test(n)));
  rejects(c, 'program', 'LET IDENT EQ INT');
}

// --- Friendly errors -----------------------------------------------------
errorMatches('bare word in course notation suggests brackets or quotes', `<a> ::= b`, { notation: 'course' },
  /<b>.*"b"|"b".*<b>/);
errorMatches('postfix * in course notation points to { X }', `<a> ::= "x"*`, { notation: 'course', ebnf: true },
  /\{ X \}/);
errorMatches('curly braces in token notation point to ( X )*', `a ::= { B }`, { notation: 'token', ebnf: true },
  /\( X \)\*/);
errorMatches('empty alternative suggests <empty>', `<a> ::= "x" | `, { notation: 'course' }, /<empty>/);
errorMatches('trailing | before a comment is caught', `<a> ::= "x" | (* more *)\n<b> ::= "y"`, { notation: 'course' },
  /alternative is empty/);
errorMatches('unclosed quote is caught', `<a> ::= "x`, { notation: 'course' }, /closing "/);
errorMatches('unclosed comment is caught', `<a> ::= "x" (* oops`, { notation: 'course' }, /never closed/);
errorMatches(':= is caught', `<a> := "x"`, { notation: 'course' }, /::=/);
errorMatches('TODO in course notation is caught', `<a> ::= TODO`, { notation: 'course' }, /TODO/);
errorMatches('undefined lowercase name in token notation', `a ::= b C`, { notation: 'token' }, /b is used but never defined/);
errorMatches('unclosed { is caught', `<a> ::= { "x"`, { notation: 'course', ebnf: true }, /never closed/);
{
  const c = E.compile(`<a> ::= "x"\n<b> ::= "y"`, { notation: 'course' });
  check('unused nonterminal is warned', c.ok && c.warnings.some(w => /<b> is defined but never used/.test(w.msg)));
  const d = E.compile(`<a> ::= <b>\n<b> ::= "y" <b>`, { notation: 'course' });
  check('nonproductive nonterminal is warned', d.ok && d.warnings.some(w => /<b> can never finish/.test(w.msg)));
  const t = E.compile(`a ::= TODO`, { notation: 'token' });
  check('TODO in token notation is warned', t.ok && t.warnings.some(w => /TODO/.test(w.msg)));
}

// --- EBNF nesting and nullable repetition --------------------------------
{
  const c = compileOk('nested EBNF', `<l> ::= "[" [ <v> { "," <v> } ] "]"\n<v> ::= "1" | <l>`, { notation: 'course', ebnf: true });
  accepts(c, 'nested', '[]');
  accepts(c, 'nested', '[1,[1,[]],1]');
  rejects(c, 'nested', '[1,]');
  const n = compileOk('repetition of something nullable terminates', `<a> ::= { [ "x" ] }`, { notation: 'course', ebnf: true });
  accepts(n, 'nullable repetition', 'xxx');
  accepts(n, 'nullable repetition', '');
}

console.log(passes + ' passed, ' + failures + ' failed');
process.exit(failures ? 1 : 0);
