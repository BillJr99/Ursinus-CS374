/*
 * CS374 BNF/EBNF Tester: grammar engine.
 *
 * Pure logic with no DOM access, so the same file runs in the browser (as the
 * global BNFEngine) and under Node (require) for the test suite in
 * .github/scripts/test_bnf_engine.js.
 *
 * Pipeline:
 *   1. lex + parse the grammar text in one of two notations
 *        course: <name> ::= "x" <other> | <empty>, EBNF adds { } [ ] ( )
 *        token : name ::= TOKEN "x" other,       EBNF adds ( ) * + ?
 *   2. desugar EBNF into plain BNF using hidden helper nonterminals
 *   3. analyze (undefined, unused, unreachable, nonproductive, left recursion)
 *   4. recognize an input with an Earley parser, which accepts every
 *      context-free grammar, including left-recursive and ambiguous ones
 *   5. rebuild parse trees in the student's own nonterminals, count up to two
 *      distinct trees (ambiguity), and print a leftmost derivation
 */
(function (root, factory) {
  if (typeof module === 'object' && module.exports) {
    module.exports = factory();
  } else {
    root.BNFEngine = factory();
  }
}(typeof self !== 'undefined' ? self : this, function () {
  'use strict';

  var MAX_ITEMS = 1500000;      // Earley items before we give up
  var MAX_TREE_WORK = 200000;   // tree-building steps before we give up
  var MAX_DERIVATION_STEPS = 400;

  // ------------------------------------------------------------------
  // Errors
  // ------------------------------------------------------------------

  function GrammarError(msg, tok, hint) {
    this.msg = msg;
    this.line = tok ? tok.line : null;
    this.col = tok ? tok.col : null;
    this.hint = hint || '';
  }

  function ebnfError(tok, what, rewrite) {
    return new GrammarError(
      '"' + tok.text + '" is EBNF ' + what + ', and EBNF is turned off.',
      tok,
      'Plain BNF has only sequence, | and recursion. Rewrite it with recursion (' +
        rewrite + '), or tick "Allow EBNF" if this exercise permits EBNF.');
  }

  // ------------------------------------------------------------------
  // Lexer for grammar text
  // ------------------------------------------------------------------

  function lexGrammar(src, notation) {
    var toks = [];
    var i = 0, line = 1, col = 1;
    var n = src.length;

    function adv(k) {
      for (var m = 0; m < k; m++) {
        if (src[i] === '\n') { line++; col = 1; } else { col++; }
        i++;
      }
    }
    function push(kind, text, value, l, c) {
      toks.push({ k: kind, text: text, v: value, line: l, col: c });
    }

    while (i < n) {
      var ch = src[i];
      var l0 = line, c0 = col;

      if (/\s/.test(ch)) { adv(1); continue; }

      // (* comment *) in both notations
      if (src.startsWith('(*', i)) {
        var end = src.indexOf('*)', i + 2);
        if (end < 0) {
          throw new GrammarError('This (* comment is never closed with *).', { line: l0, col: c0 });
        }
        adv(end + 2 - i);
        continue;
      }
      // // comment to end of line (token notation, and harmless in course notation)
      if (src.startsWith('//', i)) {
        while (i < n && src[i] !== '\n') adv(1);
        continue;
      }
      if (src.startsWith('::=', i)) { push('DEF', '::=', null, l0, c0); adv(3); continue; }
      if (src.startsWith(':=', i) || src.startsWith('->', i) || src.startsWith('→', i)) {
        throw new GrammarError('Productions are written with ::= in this course.', { line: l0, col: c0 },
          'Write  <name> ::= ...  rather than  := , -> or →.');
      }
      if (src.startsWith('...', i) || ch === '…') {
        throw new GrammarError('"..." is not grammar notation; the tester cannot fill in the rest for you.',
          { line: l0, col: c0 }, 'Write every alternative out, or put the ... inside a (* comment *).');
      }
      if (ch === '"' || ch === "'") {
        var q = ch, j = i + 1, val = '';
        while (j < n && src[j] !== q && src[j] !== '\n') {
          if (src[j] === '\\' && j + 1 < n) {
            var e = src[j + 1];
            val += e === 'n' ? '\n' : e === 't' ? '\t' : e;
            j += 2;
          } else {
            val += src[j];
            j++;
          }
        }
        if (j >= n || src[j] !== q) {
          throw new GrammarError('This terminal is missing its closing ' + q + '.', { line: l0, col: c0 },
            'Terminals are quoted on one line, like "(" or "define".');
        }
        push('T', src.slice(i, j + 1), val, l0, c0);
        adv(j + 1 - i);
        continue;
      }
      if (ch === 'ε') { push('EMPTY', 'ε', null, l0, c0); adv(1); continue; }

      if (notation === 'course' && ch === '<') {
        var close = src.indexOf('>', i);
        var nl = src.indexOf('\n', i);
        if (close < 0 || (nl >= 0 && nl < close)) {
          throw new GrammarError('This < never closes with >.', { line: l0, col: c0 },
            'Nonterminals are written in angle brackets on one line, like <digit>.');
        }
        var name = src.slice(i + 1, close).trim();
        if (!/^[A-Za-z_][A-Za-z0-9_\-]*$/.test(name)) {
          throw new GrammarError('"' + src.slice(i, close + 1) + '" is not a valid nonterminal name.',
            { line: l0, col: c0 }, 'Use letters, digits, - and _ inside the brackets, like <digit> or <if-expr>.');
        }
        if (name === 'empty') push('EMPTY', '<empty>', null, l0, c0);
        else push('NT', '<' + name + '>', name, l0, c0);
        adv(close + 1 - i);
        continue;
      }
      if (/[A-Za-z_]/.test(ch)) {
        var m = /^[A-Za-z_][A-Za-z0-9_]*/.exec(src.slice(i));
        var word = m[0];
        if (notation === 'course') {
          if (word === 'TODO') {
            throw new GrammarError('This rule still says TODO.', { line: l0, col: c0 },
              'Replace TODO with the rule\'s right-hand side before testing.');
          }
          throw new GrammarError('The bare word ' + word + ' is neither a nonterminal nor a terminal.',
            { line: l0, col: c0 },
            'In the course notation, nonterminals go in angle brackets (<' + word + '>) and terminals go in quotes ("' +
              word + '"). If this grammar uses bare names and UPPERCASE tokens, switch the notation to "Token notation".');
        }
        push('ID', word, word, l0, c0);
        adv(word.length);
        continue;
      }
      var single = { '|': 'BAR', '(': 'LPAREN', ')': 'RPAREN', '{': 'LBRACE', '}': 'RBRACE',
        '[': 'LBRACK', ']': 'RBRACK', '*': 'STAR', '+': 'PLUS', '?': 'QMARK' };
      if (single[ch]) { push(single[ch], ch, null, l0, c0); adv(1); continue; }

      throw new GrammarError('Unexpected character "' + ch + '".', { line: l0, col: c0 },
        notation === 'course'
          ? 'Terminals need quotes: write "' + ch + '" rather than ' + ch + '.'
          : 'Literal symbols need quotes: write "' + ch + '", or use a token name such as PLUS.');
    }
    toks.push({ k: 'EOF', text: 'end of grammar', line: line, col: col });
    return toks;
  }

  // ------------------------------------------------------------------
  // Parser for grammar text -> rules with EBNF ASTs
  //   alt  = { type:'alt', seqs:[seq] }
  //   seq  = { type:'seq', items:[item] }
  //   item = sym | term | empty | group | star | plus | opt
  // ------------------------------------------------------------------

  function parseGrammar(toks, notation, ebnf) {
    var pos = 0;
    var LHS = notation === 'course' ? 'NT' : 'ID';

    function peek(k) { return toks[pos + (k || 0)]; }
    function next() { return toks[pos++]; }
    function isRuleStart(k) {
      return toks[k].k === LHS && toks[k + 1] && toks[k + 1].k === 'DEF';
    }
    function expect(kind, msg, hint) {
      var t = peek();
      if (t.k !== kind) throw new GrammarError(msg + ' Found ' + describe(t) + ' instead.', t, hint);
      return next();
    }
    function describe(t) { return t.k === 'EOF' ? 'the end of the grammar' : '"' + t.text + '"'; }

    function parseAlt(closer) {
      var seqs = [parseSeq(closer)];
      while (peek().k === 'BAR') {
        next();
        seqs.push(parseSeq(closer));
      }
      return { type: 'alt', seqs: seqs };
    }

    function parseSeq(closer) {
      var items = [];
      var startTok = peek();
      for (;;) {
        var t = peek();
        if (t.k === 'EOF' || t.k === 'BAR' || t.k === 'RPAREN' || t.k === 'RBRACE' || t.k === 'RBRACK') break;
        if (t.k === 'DEF') {
          throw new GrammarError('Unexpected ::= here.', t, notation === 'course'
            ? 'A rule starts with one nonterminal, then ::=, like <expr> ::= ...'
            : 'A rule starts with one name, then ::=, like expr ::= ...');
        }
        if (isRuleStart(pos)) break;
        items.push(parsePostfix());
      }
      if (items.length === 0) {
        throw new GrammarError('This alternative is empty: there is nothing between the | (or ::=) and ' +
          describe(peek()) + '.', startTok,
          notation === 'course'
            ? 'If you mean the empty string, write <empty>. Otherwise remove the extra |.'
            : 'If you mean the empty string, write ε. Otherwise remove the extra |.');
      }
      return { type: 'seq', items: items };
    }

    function parsePostfix() {
      var item = parseAtom();
      for (;;) {
        var t = peek();
        if (t.k !== 'STAR' && t.k !== 'PLUS' && t.k !== 'QMARK') break;
        if (notation === 'course') {
          var want = t.k === 'STAR' ? '{ X }' : t.k === 'PLUS' ? 'X { X }' : '[ X ]';
          throw new GrammarError('The postfix "' + t.text + '" is not part of the course notation.', t,
            'This lab writes that as ' + want + ' (with "Allow EBNF" ticked). Postfix * + ? belong to the token notation used by the Grammar Workshop.');
        }
        if (!ebnf) {
          throw ebnfError(t, t.k === 'STAR' ? 'repetition (zero or more)' : t.k === 'PLUS'
            ? 'repetition (one or more)' : 'optionality',
            t.k === 'QMARK' ? 'give the rule one alternative with X and one without' : 'x_list ::= X x_list | ε');
        }
        next();
        item = { type: t.k === 'STAR' ? 'star' : t.k === 'PLUS' ? 'plus' : 'opt', inner: item, tok: t };
      }
      return item;
    }

    function parseAtom() {
      var t = peek();
      switch (t.k) {
        case 'NT':
        case 'ID':
          next();
          return { type: 'sym', name: t.v, tok: t };
        case 'T':
          next();
          if (t.v === '') return { type: 'empty', tok: t };
          return { type: 'term', value: t.v, tok: t };
        case 'EMPTY':
          next();
          return { type: 'empty', tok: t };
        case 'LPAREN':
          if (!ebnf) throw ebnfError(t, 'grouping', 'give each choice its own alternative, or give the group its own nonterminal');
          next();
          var g = parseAlt('RPAREN');
          expect('RPAREN', 'This ( is never closed.', 'Every ( needs a matching ).');
          return { type: 'group', alt: g, tok: t };
        case 'LBRACE':
        case 'LBRACK':
          if (notation === 'token') {
            throw new GrammarError('"' + t.text + '" is course-notation EBNF, not token notation.', t,
              t.k === 'LBRACE' ? 'In token notation write ( X )* for zero or more.' : 'In token notation write ( X )? for optional.');
          }
          if (!ebnf) {
            throw t.k === 'LBRACE'
              ? ebnfError(t, 'repetition (zero or more)', '<xs> ::= <x> <xs> | <empty>')
              : ebnfError(t, 'optionality', 'give the rule one alternative with X and one without');
          }
          next();
          var closeKind = t.k === 'LBRACE' ? 'RBRACE' : 'RBRACK';
          var inner = parseAlt(closeKind);
          expect(closeKind, 'This ' + t.text + ' is never closed.', 'Every ' + t.text + ' needs a matching ' +
            (t.k === 'LBRACE' ? '}' : ']') + '.');
          return { type: t.k === 'LBRACE' ? 'star' : 'opt', inner: { type: 'group', alt: inner, tok: t }, tok: t, bracket: true };
        default:
          throw new GrammarError('Unexpected ' + describe(t) + '.', t,
            t.k === 'EOF' ? 'The rule is incomplete.' : 'Check the symbols around here.');
      }
    }

    var rules = [];
    if (peek().k === 'EOF') throw new GrammarError('The grammar is empty.', peek(), 'Type or load a grammar first.');
    while (peek().k !== 'EOF') {
      var lhsTok = peek();
      if (lhsTok.k !== LHS) {
        throw new GrammarError('Expected the start of a rule, but found ' + describe(lhsTok) + '.', lhsTok,
          notation === 'course'
            ? 'Each rule looks like  <name> ::= ...  and a rule\'s alternatives may continue onto the next lines.'
            : 'Each rule looks like  name ::= ...  and a rule\'s alternatives may continue onto the next lines.');
      }
      next();
      expect('DEF', 'Expected ::= after ' + lhsTok.text + '.', 'A rule looks like ' +
        (notation === 'course' ? '<name> ::= ...' : 'name ::= ...'));
      var alt = parseAlt(null);
      var stray = peek();
      if (stray.k === 'RPAREN' || stray.k === 'RBRACE' || stray.k === 'RBRACK') {
        throw new GrammarError('This ' + stray.text + ' has no matching opening bracket.', stray, '');
      }
      rules.push({ name: lhsTok.v, alt: alt, tok: lhsTok });
    }
    return rules;
  }

  // ------------------------------------------------------------------
  // Printing (for derivation annotations and messages)
  // ------------------------------------------------------------------

  function quote(s) {
    return '"' + s.replace(/\\/g, '\\\\').replace(/"/g, '\\"').replace(/\n/g, '\\n').replace(/\t/g, '\\t') + '"';
  }

  function printItem(it, notation, resolved) {
    switch (it.type) {
      case 'sym':
        if (notation === 'course') return '<' + it.name + '>';
        return it.name;
      case 'term': return quote(it.value);
      case 'empty': return notation === 'course' ? '<empty>' : 'ε';
      case 'group': return '( ' + printAlt(it.alt, notation) + ' )';
      case 'star':
        if (it.bracket) return '{ ' + printAlt(it.inner.alt, notation) + ' }';
        return printItem(it.inner, notation) + '*';
      case 'opt':
        if (it.bracket) return '[ ' + printAlt(it.inner.alt, notation) + ' ]';
        return printItem(it.inner, notation) + '?';
      case 'plus': return printItem(it.inner, notation) + '+';
    }
    return '?';
  }
  function printSeq(seq, notation) {
    return seq.items.map(function (it) { return printItem(it, notation); }).join(' ');
  }
  function printAlt(alt, notation) {
    return alt.seqs.map(function (s) { return printSeq(s, notation); }).join(' | ');
  }
  function ntLabel(name, notation) { return notation === 'course' ? '<' + name + '>' : name; }

  // ------------------------------------------------------------------
  // Compile: parse, resolve, desugar, analyze
  // ------------------------------------------------------------------

  function compile(src, opts) {
    opts = opts || {};
    var notation = opts.notation === 'token' ? 'token' : 'course';
    var ebnf = !!opts.ebnf;
    var result = { ok: false, errors: [], warnings: [], notes: [], notation: notation, ebnf: ebnf };

    var rules;
    try {
      rules = parseGrammar(lexGrammar(src, notation), notation, ebnf);
    } catch (e) {
      if (e instanceof GrammarError) { result.errors.push(e); return result; }
      throw e;
    }

    // Merge repeated left-hand sides, keeping first-definition order.
    var order = [];
    var byName = Object.create(null);
    rules.forEach(function (r) {
      if (byName[r.name]) {
        byName[r.name].alt.seqs = byName[r.name].alt.seqs.concat(r.alt.seqs);
        result.notes.push({ msg: ntLabel(r.name, notation) + ' is defined on more than one line (line ' +
          byName[r.name].tok.line + ' and line ' + r.tok.line + '); the tester treats all of them as alternatives of one rule.' });
      } else {
        byName[r.name] = { name: r.name, alt: r.alt, tok: r.tok };
        order.push(r.name);
      }
    });

    // Resolve every symbol: a defined name is a nonterminal; in token
    // notation an undefined UPPERCASE name is a token; anything else is
    // an undefined nonterminal.
    var undefinedUses = Object.create(null);
    var referenced = Object.create(null);
    var todoTokens = false;
    function resolve(it) {
      switch (it.type) {
        case 'sym':
          if (byName[it.name]) { it.kind = 'nt'; referenced[it.name] = true; return; }
          if (notation === 'token' && /^[A-Z][A-Z0-9_]*$/.test(it.name)) {
            it.kind = 'tok';
            if (it.name === 'TODO') todoTokens = true;
            return;
          }
          it.kind = 'undef';
          (undefinedUses[it.name] = undefinedUses[it.name] || []).push(it.tok.line);
          return;
        case 'group': it.alt.seqs.forEach(function (s) { s.items.forEach(resolve); }); return;
        case 'star': case 'plus': case 'opt': resolve(it.inner); return;
      }
    }
    order.forEach(function (name) { byName[name].alt.seqs.forEach(function (s) { s.items.forEach(resolve); }); });

    Object.keys(undefinedUses).forEach(function (name) {
      var lines = undefinedUses[name].filter(function (v, i, a) { return a.indexOf(v) === i; });
      result.errors.push(new GrammarError(
        ntLabel(name, notation) + ' is used but never defined (line' + (lines.length > 1 ? 's ' : ' ') + lines.join(', ') + ').',
        { line: lines[0], col: null },
        notation === 'course'
          ? 'Every nonterminal on a right-hand side needs its own production: add  <' + name + '> ::= ...'
          : (/[a-z]/.test(name)
            ? 'Every lowercase name on a right-hand side needs its own rule: add  ' + name + ' ::= ...  (UPPERCASE names are tokens).'
            : 'Add a rule for it, or write it in UPPERCASE if it is a token.')));
    });
    if (todoTokens) {
      result.warnings.push({ msg: 'The grammar still contains TODO. The tester is treating TODO as a token, so fill those rules in before trusting the results.' });
    }
    if (result.errors.length) return result;

    // Desugar to plain BNF productions.
    var prods = [];
    var helperCount = Object.create(null);
    function fresh(owner) {
      helperCount[owner] = (helperCount[owner] || 0) + 1;
      return owner + '·' + helperCount[owner];
    }
    function convert(it, owner) {
      switch (it.type) {
        case 'sym': return [it.kind === 'nt' ? { nt: it.name } : { t: it.name, tok: true }];
        case 'term': return [{ t: it.value }];
        case 'empty': return [];
        case 'group':
          if (it.alt.seqs.length === 1) return convertSeq(it.alt.seqs[0], owner);
          var g = fresh(owner);
          it.alt.seqs.forEach(function (s) {
            prods.push({ lhs: g, rhs: convertSeq(s, owner), hidden: true, owner: owner, text: null });
          });
          return [{ nt: g }];
        case 'star':
          var h = fresh(owner);
          var inner = convert(it.inner, owner);
          prods.push({ lhs: h, rhs: inner.concat([{ nt: h }]), hidden: true, owner: owner, text: null });
          prods.push({ lhs: h, rhs: [], hidden: true, owner: owner, text: null });
          return [{ nt: h }];
        case 'plus':
          var hp = fresh(owner);
          var innerP = convert(it.inner, owner);
          prods.push({ lhs: hp, rhs: innerP.concat([{ nt: hp }]), hidden: true, owner: owner, text: null });
          prods.push({ lhs: hp, rhs: innerP.slice(), hidden: true, owner: owner, text: null });
          return [{ nt: hp }];
        case 'opt':
          var ho = fresh(owner);
          prods.push({ lhs: ho, rhs: convert(it.inner, owner), hidden: true, owner: owner, text: null });
          prods.push({ lhs: ho, rhs: [], hidden: true, owner: owner, text: null });
          return [{ nt: ho }];
      }
      return [];
    }
    function convertSeq(seq, owner) {
      var out = [];
      seq.items.forEach(function (it) { out = out.concat(convert(it, owner)); });
      return out;
    }
    order.forEach(function (name) {
      byName[name].alt.seqs.forEach(function (s) {
        prods.push({ lhs: name, rhs: convertSeq(s, name), hidden: false, owner: name, text: printSeq(s, notation) });
      });
    });

    var byLhs = Object.create(null);
    prods.forEach(function (p, i) { (byLhs[p.lhs] = byLhs[p.lhs] || []).push(i); });
    var allNts = Object.keys(byLhs);

    // nullable
    var nullable = Object.create(null);
    var changed = true;
    while (changed) {
      changed = false;
      prods.forEach(function (p) {
        if (!nullable[p.lhs] && p.rhs.every(function (s) { return s.nt && nullable[s.nt]; })) {
          nullable[p.lhs] = true; changed = true;
        }
      });
    }
    // productive (can derive some string of terminals) + minimal height
    var height = Object.create(null);
    changed = true;
    while (changed) {
      changed = false;
      prods.forEach(function (p) {
        var ok = true, h = 0;
        for (var k = 0; k < p.rhs.length; k++) {
          var s = p.rhs[k];
          if (s.nt) {
            if (height[s.nt] === undefined) { ok = false; break; }
            h = Math.max(h, height[s.nt]);
          }
        }
        if (ok && (height[p.lhs] === undefined || h + 1 < height[p.lhs])) {
          height[p.lhs] = h + 1; changed = true;
        }
      });
    }

    var grammar = {
      notation: notation, ebnf: ebnf, userNts: order, prods: prods, byLhs: byLhs,
      nullable: nullable, height: height, rules: byName
    };
    result.grammar = grammar;
    result.ok = true;

    // Analysis on the user's own names (helpers report as their owner).
    var start = order[0];
    var reach = reachableFrom(grammar, start);
    order.forEach(function (name) {
      if (name === start) return;
      if (!referenced[name]) {
        result.warnings.push({ msg: ntLabel(name, notation) + ' is defined but never used on any right-hand side.' });
      } else if (!reach[name]) {
        result.warnings.push({ msg: ntLabel(name, notation) + ' can never be reached from the start symbol ' + ntLabel(start, notation) + '.' });
      }
    });
    order.forEach(function (name) {
      if (height[name] === undefined) {
        result.warnings.push({ msg: ntLabel(name, notation) + ' can never finish: every alternative uses a nonterminal that recurses forever, so it derives no string at all.' +
          ' A recursive rule needs at least one way out (a base case).' });
      }
    });
    var lr = leftRecursive(grammar);
    if (lr.length) {
      result.notes.push({ msg: 'Left recursion: ' + lr.map(function (n) { return ntLabel(n, notation); }).join(', ') +
        '. That is fine for this tester and for LR parsers, but a recursive-descent parser would call itself forever on this rule.' });
    }
    return result;
  }

  function reachableFrom(g, start) {
    var seen = Object.create(null);
    var stack = [start];
    seen[start] = true;
    while (stack.length) {
      var a = stack.pop();
      (g.byLhs[a] || []).forEach(function (pi) {
        g.prods[pi].rhs.forEach(function (s) {
          if (s.nt && !seen[s.nt]) { seen[s.nt] = true; stack.push(s.nt); }
        });
      });
    }
    // Map helpers back to their owners.
    var out = Object.create(null);
    Object.keys(seen).forEach(function (nt) {
      out[nt] = true;
      var p = g.prods[(g.byLhs[nt] || [])[0]];
      if (p) out[p.owner] = true;
    });
    return out;
  }

  function leftRecursive(g) {
    // Edge A -> B when some A production starts with B after nullable symbols.
    var edges = Object.create(null);
    g.prods.forEach(function (p) {
      for (var k = 0; k < p.rhs.length; k++) {
        var s = p.rhs[k];
        if (!s.nt) break;
        (edges[p.lhs] = edges[p.lhs] || []).push(s.nt);
        if (!g.nullable[s.nt]) break;
      }
    });
    var owners = [];
    Object.keys(g.byLhs).forEach(function (a) {
      var seen = Object.create(null);
      var stack = (edges[a] || []).slice();
      var found = false;
      while (stack.length && !found) {
        var b = stack.pop();
        if (b === a) { found = true; break; }
        if (seen[b]) continue;
        seen[b] = true;
        (edges[b] || []).forEach(function (c) { stack.push(c); });
      }
      if (found) {
        var owner = g.prods[g.byLhs[a][0]].owner;
        if (owners.indexOf(owner) < 0) owners.push(owner);
      }
    });
    return owners.filter(function (o) { return g.userNts.indexOf(o) >= 0; });
  }

  // ------------------------------------------------------------------
  // Input handling
  // ------------------------------------------------------------------

  function tokenizeInput(text) {
    // Accept "INT PLUS INT" and the Grammar Workshop's "INT(2) PLUS INT(3)".
    var raw = text.trim() === '' ? [] : text.trim().split(/\s+/);
    return raw.map(function (w) {
      var m = /^([A-Z][A-Z0-9_]*)\(.*\)$/.exec(w);
      return m ? m[1] : w;
    });
  }

  function makeMatcher(g, input, skipWs) {
    if (g.notation === 'token') {
      return {
        n: input.length,
        match: function (t, i) { return input[i] === t ? i + 1 : -1; },
        endOk: function (j) { return j === input.length; },
        visible: function (i) { return i; }
      };
    }
    function skip(i) {
      while (i < input.length && /\s/.test(input[i])) i++;
      return i;
    }
    return {
      n: input.length,
      match: function (t, i) {
        var p = (skipWs && !/^\s/.test(t)) ? skip(i) : i;
        return input.startsWith(t, p) ? p + t.length : -1;
      },
      endOk: function (j) { return (skipWs ? skip(j) : j) === input.length; },
      visible: function (i) { return skipWs ? skip(i) : i; }
    };
  }

  // ------------------------------------------------------------------
  // Earley recognizer
  // ------------------------------------------------------------------

  function earley(g, start, M) {
    var n = M.n;
    var sets = [];
    var keys = [];
    for (var s = 0; s <= n; s++) { sets.push([]); keys.push(new Set()); }
    var completed = new Map();   // "lhs|origin|end" -> Set(prodIdx)
    var ends = new Map();        // "lhs|origin" -> Set(end)
    var count = 0;
    var tooBig = false;

    function add(j, p, d, o) {
      var key = p * 1048576 * 64 + d * 1048576 + o; // unique while d < 64 and o < 2^20
      if (keys[j].has(key)) return;
      keys[j].add(key);
      sets[j].push({ p: p, d: d, o: o });
      if (++count > MAX_ITEMS) tooBig = true;
    }

    (g.byLhs[start] || []).forEach(function (pi) { add(0, pi, 0, 0); });

    for (var j = 0; j <= n && !tooBig; j++) {
      var set = sets[j];
      for (var k = 0; k < set.length && !tooBig; k++) {
        var it = set[k];
        var prod = g.prods[it.p];
        if (it.d < prod.rhs.length) {
          var sym = prod.rhs[it.d];
          if (sym.nt) {
            var alts = g.byLhs[sym.nt] || [];
            for (var a = 0; a < alts.length; a++) add(j, alts[a], 0, j);
            if (g.nullable[sym.nt]) add(j, it.p, it.d + 1, it.o);
          } else {
            var e = M.match(sym.t, j);
            if (e > j) add(e, it.p, it.d + 1, it.o);
          }
        } else {
          var ck = prod.lhs + '|' + it.o + '|' + j;
          if (!completed.has(ck)) completed.set(ck, new Set());
          completed.get(ck).add(it.p);
          var ek = prod.lhs + '|' + it.o;
          if (!ends.has(ek)) ends.set(ek, new Set());
          ends.get(ek).add(j);
          var from = sets[it.o];
          for (var f = 0; f < from.length; f++) {
            var it2 = from[f];
            var p2 = g.prods[it2.p];
            if (it2.d < p2.rhs.length && p2.rhs[it2.d].nt === prod.lhs) add(j, it2.p, it2.d + 1, it2.o);
          }
        }
      }
    }
    return { sets: sets, completed: completed, ends: ends, tooBig: tooBig };
  }

  // ------------------------------------------------------------------
  // Parse trees from the Earley chart
  // ------------------------------------------------------------------

  function treeBuilder(g, M, chart) {
    var memo = new Map();
    var busy = new Set();
    var work = { n: 0, exceeded: false };

    function trees(nt, i, j, limit) {
      var key = nt + '|' + i + '|' + j;
      if (memo.has(key)) return memo.get(key);
      if (busy.has(key)) return [];
      var prodsHere = chart.completed.get(key);
      if (!prodsHere) return [];
      busy.add(key);
      var out = [];
      prodsHere.forEach(function (pi) {
        if (out.length >= limit) return;
        var kids = seqs(g.prods[pi].rhs, 0, i, j, limit - out.length);
        kids.forEach(function (ch) {
          if (out.length < limit) out.push({ p: pi, children: ch });
        });
      });
      busy.delete(key);
      memo.set(key, out);
      return out;
    }

    function seqs(rhs, k, i, j, limit) {
      if (++work.n > MAX_TREE_WORK) { work.exceeded = true; return []; }
      if (k === rhs.length) return i === j ? [[]] : [];
      var sym = rhs[k];
      var out = [];
      if (!sym.nt) {
        var e = M.match(sym.t, i);
        if (e < 0 || e > j) return [];
        var leaf = { t: sym.t, tok: !!sym.tok };
        seqs(rhs, k + 1, e, j, limit).forEach(function (rest) {
          if (out.length < limit) out.push([leaf].concat(rest));
        });
        return out;
      }
      var endSet = chart.ends.get(sym.nt + '|' + i);
      if (!endSet) return [];
      var mids = Array.from(endSet).filter(function (m) { return m <= j; }).sort(function (a, b) { return a - b; });
      for (var x = 0; x < mids.length && out.length < limit; x++) {
        var m = mids[x];
        var rests = seqs(rhs, k + 1, m, j, limit);
        if (!rests.length) continue;
        var subs = trees(sym.nt, i, m, limit);
        for (var a = 0; a < subs.length && out.length < limit; a++) {
          for (var b = 0; b < rests.length && out.length < limit; b++) {
            out.push([subs[a]].concat(rests[b]));
          }
        }
      }
      return out;
    }
    return { trees: trees, work: work };
  }

  // Turn a raw tree into one that shows only the student's nonterminals:
  // helper nodes created by desugaring are spliced into their parent.
  function userTree(g, node) {
    var p = g.prods[node.p];
    return { name: p.lhs, text: p.text, children: spliceKids(g, node.children) };
  }
  function spliceKids(g, kids) {
    var out = [];
    kids.forEach(function (c) {
      if (c.t !== undefined) { out.push({ t: c.t, tok: c.tok }); return; }
      if (g.prods[c.p].hidden) { out = out.concat(spliceKids(g, c.children)); return; }
      out.push(userTree(g, c));
    });
    return out;
  }
  function treeKey(node) {
    if (node.t !== undefined) return JSON.stringify(node.t);
    return '(' + node.name + '=' + node.text + ' ' + node.children.map(treeKey).join(' ') + ')';
  }

  function treeText(node, notation) {
    var lines = [];
    function label(nd) {
      if (nd.t !== undefined) return nd.tok ? nd.t : quote(nd.t);
      return ntLabel(nd.name, notation);
    }
    function walk(nd, prefix, isLast, isRoot) {
      lines.push(isRoot ? label(nd) : prefix + (isLast ? '└── ' : '├── ') + label(nd));
      if (nd.t !== undefined) return;
      var kids = nd.children.length ? nd.children : [{ t: '', empty: true }];
      var childPrefix = isRoot ? '' : prefix + (isLast ? '    ' : '│   ');
      kids.forEach(function (c, idx) {
        if (c.empty) {
          lines.push(childPrefix + '└── ' + (notation === 'course' ? '<empty>' : 'ε'));
          return;
        }
        walk(c, childPrefix, idx === kids.length - 1, false);
      });
    }
    walk(node, '', true, true);
    return lines.join('\n');
  }

  function derivation(root, notation) {
    // Leftmost derivation over the user tree, one production per step,
    // printed like the lab: "=> ( <exprs> )   [<list> ::= "(" <exprs> ")"]".
    function show(form) {
      var parts = form.map(function (x) {
        if (x.t !== undefined) return x.t;
        return ntLabel(x.name, notation);
      });
      var s = parts.join(' ').replace(/\s+/g, ' ').trim();
      return s === '' ? (notation === 'course' ? '(the empty string)' : 'ε') : s;
    }
    var form = [root];
    var steps = [{ form: show(form), rule: null }];
    for (var guard = 0; guard < MAX_DERIVATION_STEPS; guard++) {
      var idx = -1;
      for (var k = 0; k < form.length; k++) { if (form[k].t === undefined) { idx = k; break; } }
      if (idx < 0) return { steps: steps, truncated: false };
      var node = form[idx];
      form = form.slice(0, idx).concat(node.children, form.slice(idx + 1));
      var rhs = node.text === '' ? (notation === 'course' ? '<empty>' : 'ε') : node.text;
      steps.push({ form: show(form), rule: ntLabel(node.name, notation) + ' ::= ' + rhs });
    }
    return { steps: steps, truncated: true };
  }

  // ------------------------------------------------------------------
  // Test an input string
  // ------------------------------------------------------------------

  function test(compiled, text, opts) {
    opts = opts || {};
    var g = compiled.grammar;
    var start = opts.start && g.rules[opts.start] ? opts.start : g.userNts[0];
    var skipWs = opts.skipWs !== false;
    var res = { start: start, accepted: false, notes: [] };

    var input = text;
    if (g.notation === 'token') {
      input = tokenizeInput(text);
      if (usesToken(g, 'EOF') && input[input.length - 1] !== 'EOF') {
        input = input.concat(['EOF']);
        res.notes.push('The grammar ends with the EOF token, so the tester added EOF to the end of your input.');
      }
      res.tokens = input;
    }
    var M = makeMatcher(g, input, skipWs);
    var chart = earley(g, start, M);
    if (chart.tooBig) {
      res.error = { msg: 'The input is too long for the in-browser tester to finish. Try a shorter string.' };
      return res;
    }

    var goodEnds = [];
    for (var j = 0; j <= M.n; j++) {
      if (M.endOk(j) && chart.completed.has(start + '|0|' + j)) goodEnds.push(j);
    }

    if (!goodEnds.length) {
      res.error = diagnose(g, start, M, chart, input);
      return res;
    }
    res.accepted = true;

    var tb = treeBuilder(g, M, chart);
    var raw = [];
    goodEnds.forEach(function (e) {
      if (raw.length < 6) raw = raw.concat(tb.trees(start, 0, e, 6 - raw.length));
    });
    var distinct = [];
    var seen = new Set();
    raw.forEach(function (r) {
      var u = userTree(g, r);
      var key = treeKey(u);
      if (!seen.has(key)) { seen.add(key); distinct.push(u); }
    });
    res.trees = distinct.slice(0, 2);
    res.ambiguous = distinct.length > 1;
    res.treeIncomplete = tb.work.exceeded || !distinct.length;
    res.treeTexts = res.trees.map(function (t) { return treeText(t, g.notation); });
    res.derivations = res.trees.map(function (t) { return derivation(t, g.notation); });
    return res;
  }

  function usesToken(g, name) {
    return g.prods.some(function (p) { return p.rhs.some(function (s) { return s.tok && s.t === name; }); });
  }

  function diagnose(g, start, M, chart, input) {
    var far = 0;
    for (var j = M.n; j >= 0; j--) { if (chart.sets[j].length) { far = j; break; } }
    var expected = [];
    var startDoneHere = false;
    chart.sets[far].forEach(function (it) {
      var p = g.prods[it.p];
      if (it.d < p.rhs.length) {
        var s = p.rhs[it.d];
        if (!s.nt) {
          var label = s.tok ? s.t : quote(s.t);
          if (expected.indexOf(label) < 0) expected.push(label);
        }
      } else if (p.lhs === start && it.o === 0) {
        startDoneHere = true;
      }
    });
    var pos = M.visible(far);
    var err = { pos: pos, expected: expected.slice(0, 15), moreExpected: expected.length > 15 };
    var atEnd = pos >= M.n;
    var what = g.notation === 'token' ? 'token' : 'character';
    if (atEnd) {
      err.msg = 'The input ended too early: every way of parsing it still needs more.';
    } else if (startDoneHere) {
      err.msg = 'A complete ' + ntLabel(start, g.notation) + ' ends before ' + what + ' ' + (pos + 1) +
        ', but there is more input after it that the grammar cannot place.';
    } else {
      var shown = g.notation === 'token' ? input[pos] : JSON.stringify(input[pos]);
      err.msg = 'Stuck at ' + what + ' ' + (pos + 1) + ' (' + shown + '): no rule can continue from here.';
    }
    return err;
  }

  // ------------------------------------------------------------------
  // Random generation
  // ------------------------------------------------------------------

  function generate(compiled, start, rng, skipWs) {
    var g = compiled.grammar;
    rng = rng || Math.random;
    start = start && g.rules[start] ? start : g.userNts[0];
    if (g.height[start] === undefined) return null;
    var out, budget;
    function gen(nt, depth) {
      var alts = (g.byLhs[nt] || []).filter(function (pi) {
        return g.prods[pi].rhs.every(function (s) { return !s.nt || g.height[s.nt] !== undefined; });
      });
      var pick;
      if (depth > 6 || budget <= 0) {
        var best = Infinity;
        alts.forEach(function (pi) {
          var h = 0;
          g.prods[pi].rhs.forEach(function (s) { if (s.nt) h = Math.max(h, g.height[s.nt]); });
          if (h < best) { best = h; pick = pi; }
        });
      } else {
        pick = alts[Math.floor(rng() * alts.length)];
      }
      g.prods[pick].rhs.forEach(function (s) {
        if (s.nt) gen(s.nt, depth + 1);
        else { out.push(s.t); budget--; }
      });
    }
    // An empty string is a legal but unhelpful example, so try a few times
    // for a non-empty one before settling for it.
    for (var attempt = 0; attempt < 12; attempt++) {
      out = [];
      budget = 30;
      gen(start, 0);
      if (out.length) break;
    }
    if (g.notation === 'token') return out.join(' ');
    // Readability: when whitespace between terminals is ignored, separate
    // word-like terminals so "define" "x" does not print as "definex".
    if (skipWs) {
      var s = '';
      out.forEach(function (t) {
        if (s && /[A-Za-z0-9_]$/.test(s) && /^[A-Za-z0-9_]/.test(t) && (t.length > 1 || /[A-Za-z_]{2,}$/.test(s))) s += ' ';
        s += t;
      });
      return s;
    }
    return out.join('');
  }

  return {
    compile: compile,
    test: test,
    generate: generate,
    tokenizeInput: tokenizeInput,
    printAlt: printAlt
  };
}));
