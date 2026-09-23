/*
 * CS374 BNF/EBNF Tester: page wiring.  All grammar logic lives in
 * bnf-engine.js (global BNFEngine); this file only reads the controls,
 * calls the engine, and renders what comes back.
 */
(function () {
  'use strict';

  var E = window.BNFEngine;
  var STORE_KEY = 'cs374-bnf-tester-v1';

  var EXAMPLES = [
    {
      id: 'warmup',
      label: 'BNF Workshop: the EBNF warm-up (<entry>)',
      notation: 'course', ebnf: true, start: 'entry', input: 'abc:-42',
      grammar:
        '(* The notation example from the BNF Workshop, with <name>, <letter> and <digit>\n' +
        '   added so that every nonterminal is defined. *)\n' +
        '<entry>  ::= <name> ":" <number>\n' +
        '<name>   ::= <letter> { <letter> }\n' +
        '<letter> ::= "a" | "b" | "c" | "x" | "y" | "z"\n' +
        '<sign>   ::= "+" | "-"\n' +
        '<digits> ::= <digit> { <digit> }\n' +
        '<digit>  ::= "0" | "1" | "2" | "3" | "4" | "5" | "6" | "7" | "8" | "9"\n' +
        '<number> ::= [ <sign> ] <digits>\n' +
        '<pair>   ::= <number> ( "," | ";" ) <number>\n'
    },
    {
      id: 'model15',
      label: 'BNF Workshop: Model 1.5, exactly as given',
      notation: 'course', ebnf: false, start: 'expr', input: '(+ 1 (* 2 3))',
      grammar:
        '(* Model 1.5 from the Syntax and BNF/EBNF activity, reproduced exactly.\n' +
        '   The tester will tell you what Part 0 of the lab asks you to fix. *)\n' +
        '<expr>  ::= <atom> | <list>\n' +
        '<list>  ::= "(" <exprs> ")"\n' +
        '<exprs> ::= <expr> <exprs> | <empty>\n' +
        '<atom>  ::= <number> | <symbol>\n'
    },
    {
      id: 'rightlinear',
      label: 'Right-linear (regular): strings over a, b that end in ab',
      notation: 'course', ebnf: false, start: 's', input: 'babab',
      grammar:
        '(* Every production is a terminal followed by at most one nonterminal,\n' +
        '   at the far right: a right-linear grammar, so the language is regular. *)\n' +
        '<s> ::= "a" <s> | "b" <s> | "a" <t>\n' +
        '<t> ::= "b"\n'
    },
    {
      id: 'balanced',
      label: 'Balanced parentheses, using <empty>',
      notation: 'course', ebnf: false, start: 'b', input: '(()())()',
      grammar:
        '(* Context-free but not regular: no finite automaton can count unbounded nesting. *)\n' +
        '<b> ::= "(" <b> ")" <b> | <empty>\n'
    },
    {
      id: 'ladder',
      label: 'Grammar Workshop: the precedence ladder (token notation)',
      notation: 'token', ebnf: true, start: 'expr', input: 'INT(2) PLUS INT(3) STAR INT(4)',
      grammar:
        '// The worked example from the Grammar and Derivations Workshop.\n' +
        '// UPPERCASE names are tokens from your lexer; test with a token stream.\n' +
        'expr    ::= term ( PLUS term )*\n' +
        'term    ::= factor ( STAR factor )*\n' +
        'factor  ::= INT | LPAREN expr RPAREN\n'
    },
    {
      id: 'flat',
      label: 'Grammar Workshop: the flat grammar (ambiguous)',
      notation: 'token', ebnf: false, start: 'expr', input: 'INT PLUS INT STAR INT',
      grammar:
        '// The flat grammar from Step 0.1. Test INT PLUS INT STAR INT and\n' +
        '// compare the two parse trees the tester finds.\n' +
        'expr ::= expr PLUS expr\n' +
        '       | expr MINUS expr\n' +
        '       | expr STAR expr\n' +
        '       | INT\n'
    }
  ];

  function $(id) { return document.getElementById(id); }
  var el = {};
  var compiled = null;
  var currentTree = 0;
  var lastResult = null;

  function el_(tag, attrs, text) {
    var n = document.createElement(tag);
    if (attrs) Object.keys(attrs).forEach(function (k) { n.setAttribute(k, attrs[k]); });
    if (text !== undefined) n.textContent = text;
    return n;
  }

  // ---------------- state: URL hash, local storage ----------------

  function state() {
    return {
      g: el.grammar.value,
      n: el.notation.value,
      e: el.ebnf.checked ? '1' : '0',
      w: el.ws.checked ? '1' : '0',
      s: el.start.value,
      i: el.input.value
    };
  }

  function applyState(s) {
    if (s.n) el.notation.value = s.n === 'token' ? 'token' : 'course';
    el.ebnf.checked = s.e === '1';
    el.ws.checked = s.w !== '0';
    if (typeof s.g === 'string') el.grammar.value = s.g;
    if (typeof s.i === 'string') el.input.value = s.i;
    recompile(s.s);
  }

  function fromHash() {
    var h = window.location.hash.replace(/^#/, '');
    if (!h) return null;
    var out = {};
    h.split('&').forEach(function (kv) {
      var k = kv.split('=')[0];
      var v = kv.slice(k.length + 1);
      try { out[k] = decodeURIComponent(v); } catch (e) { /* ignore a malformed part */ }
    });
    return typeof out.g === 'string' ? out : null;
  }

  function shareUrl() {
    var s = state();
    var h = Object.keys(s).map(function (k) { return k + '=' + encodeURIComponent(s[k]); }).join('&');
    return window.location.href.split('#')[0] + '#' + h;
  }

  function save() {
    try { window.localStorage.setItem(STORE_KEY, JSON.stringify(state())); } catch (e) { /* storage unavailable */ }
  }

  function load() {
    try {
      var raw = window.localStorage.getItem(STORE_KEY);
      return raw ? JSON.parse(raw) : null;
    } catch (e) { return null; }
  }

  // ---------------- compile + messages ----------------

  function modeBadge() {
    var token = el.notation.value === 'token';
    el.badge.textContent = el.ebnf.checked ? 'EBNF on' : 'Plain BNF';
    el.badge.className = 'bnf-badge ' + (el.ebnf.checked ? 'bnf-badge-ebnf' : 'bnf-badge-bnf');
    el.ebnfWhat.textContent = token ? '( ), * + ?' : '{ }, [ ], ( )';
    el.wsRow.hidden = token;
    el.inputLabel.textContent = token
      ? 'Tokens to test, separated by spaces (INT(2) is read as INT)'
      : 'String to test';
    el.input.placeholder = token ? 'INT PLUS INT STAR INT' : '(+ 1 (* 2 3))';
    el.helpCourse.hidden = token;
    el.helpToken.hidden = !token;
  }

  function recompile(preferStart) {
    modeBadge();
    var prevStart = preferStart || el.start.value;
    compiled = E.compile(el.grammar.value, { notation: el.notation.value, ebnf: el.ebnf.checked });
    renderMessages();
    el.start.innerHTML = '';
    if (compiled.ok) {
      compiled.grammar.userNts.forEach(function (name, idx) {
        var label = el.notation.value === 'course' ? '<' + name + '>' : name;
        var o = el_('option', { value: name }, label + (idx === 0 ? '  (first rule)' : ''));
        el.start.appendChild(o);
      });
      if (prevStart && compiled.grammar.rules[prevStart]) el.start.value = prevStart;
    }
    el.start.disabled = !compiled.ok;
    el.testBtn.disabled = !compiled.ok;
    el.genBtn.disabled = !compiled.ok;
    clearResult(compiled.ok ? 'Press "Test string" to check it against the grammar.' : 'Fix the grammar above first.');
    save();
  }

  function renderMessages() {
    var box = el.messages;
    box.innerHTML = '';
    if (compiled.ok) {
      var ok = el_('p', { 'class': 'bnf-msg bnf-msg-ok' });
      var n = compiled.grammar.userNts.length;
      ok.textContent = '✓ Grammar OK: ' + n + ' nonterminal' + (n === 1 ? '' : 's') + ', ' +
        (compiled.ebnf ? 'EBNF on' : 'plain BNF') + ', ' +
        (compiled.notation === 'course' ? 'course notation.' : 'token notation.');
      box.appendChild(ok);
    }
    compiled.errors.forEach(function (e) {
      var p = el_('div', { 'class': 'bnf-msg bnf-msg-error' });
      var where = e.line ? 'Line ' + e.line + (e.col ? ', column ' + e.col : '') + ': ' : '';
      p.appendChild(el_('strong', null, '✗ ' + where));
      p.appendChild(document.createTextNode(e.msg));
      if (e.hint) p.appendChild(el_('div', { 'class': 'bnf-hint' }, e.hint));
      box.appendChild(p);
    });
    compiled.warnings.forEach(function (w) {
      box.appendChild(el_('div', { 'class': 'bnf-msg bnf-msg-warn' }, '⚠ ' + w.msg));
    });
    compiled.notes.forEach(function (w) {
      box.appendChild(el_('div', { 'class': 'bnf-msg bnf-msg-note' }, 'ℹ ' + w.msg));
    });
  }

  // ---------------- results ----------------

  function clearResult(text) {
    el.result.innerHTML = '';
    el.result.appendChild(el_('p', { 'class': 'bnf-muted' }, text));
    lastResult = null;
  }

  function runTest() {
    if (!compiled || !compiled.ok) return;
    save();
    var r = E.test(compiled, el.input.value, { start: el.start.value, skipWs: el.ws.checked });
    lastResult = r;
    currentTree = 0;
    renderResult();
  }

  function renderResult() {
    var r = lastResult;
    var box = el.result;
    box.innerHTML = '';
    var token = compiled.notation === 'token';
    var startLabel = token ? r.start : '<' + r.start + '>';

    (r.notes || []).forEach(function (n) { box.appendChild(el_('p', { 'class': 'bnf-msg bnf-msg-note' }, 'ℹ ' + n)); });

    if (!r.accepted) {
      var v = el_('div', { 'class': 'bnf-verdict bnf-verdict-no' });
      v.appendChild(el_('strong', null, '✗ Rejected. '));
      v.appendChild(document.createTextNode('This input is not in the language of ' + startLabel + '.'));
      box.appendChild(v);
      if (r.error) {
        box.appendChild(el_('p', null, r.error.msg));
        if (typeof r.error.pos === 'number') box.appendChild(markPosition(r));
        if (r.error.expected && r.error.expected.length) {
          box.appendChild(el_('p', null, 'At that point the grammar could accept: ' +
            r.error.expected.join('  ') + (r.error.moreExpected ? '  …' : '')));
        }
      }
      return;
    }

    var ok = el_('div', { 'class': 'bnf-verdict bnf-verdict-yes' });
    ok.appendChild(el_('strong', null, '✓ Accepted. '));
    ok.appendChild(document.createTextNode('The grammar derives this input from ' + startLabel + '.'));
    box.appendChild(ok);

    if (r.ambiguous) {
      var amb = el_('div', { 'class': 'bnf-msg bnf-msg-warn' });
      amb.appendChild(el_('strong', null, 'Ambiguous: '));
      amb.appendChild(document.createTextNode('this input has at least two different parse trees, so the grammar is ambiguous. Compare them: '));
      [0, 1].forEach(function (k) {
        var b = el_('button', { type: 'button', 'class': 'bnf-btn bnf-btn-small' + (k === currentTree ? ' bnf-btn-on' : '') }, 'Tree ' + (k + 1));
        b.addEventListener('click', function () { currentTree = k; renderResult(); });
        amb.appendChild(b);
      });
      box.appendChild(amb);
    }
    if (r.treeIncomplete) {
      box.appendChild(el_('p', { 'class': 'bnf-msg bnf-msg-note' },
        'ℹ The input is accepted, but its parse tree is too large to draw here.'));
      return;
    }

    var tree = r.trees[currentTree];
    box.appendChild(el_('h3', null, 'Parse tree' + (r.ambiguous ? ' ' + (currentTree + 1) + ' of at least 2' : '')));
    var treeWrap = el_('div', { 'class': 'bnf-tree' });
    treeWrap.appendChild(treeHtml(tree, token));
    box.appendChild(treeWrap);
    var textToggle = el_('details');
    textToggle.appendChild(el_('summary', null, 'Show the tree as plain text (to copy into your write-up)'));
    textToggle.appendChild(el_('pre', { 'class': 'bnf-pre' }, r.treeTexts[currentTree]));
    box.appendChild(textToggle);

    var d = r.derivations[currentTree];
    box.appendChild(el_('h3', null, 'Leftmost derivation'));
    var table = el_('table', { 'class': 'bnf-table' });
    var head = el_('tr');
    ['Step', 'Sentential form', 'Production used'].forEach(function (h) { head.appendChild(el_('th', null, h)); });
    table.appendChild(el_('thead')).appendChild(head);
    var body = el_('tbody');
    d.steps.forEach(function (s, k) {
      var tr = el_('tr');
      tr.appendChild(el_('td', null, String(k)));
      tr.appendChild(el_('td', { 'class': 'bnf-code' }, (k ? '=> ' : '') + s.form));
      tr.appendChild(el_('td', { 'class': 'bnf-code' }, s.rule ? '[' + s.rule + ']' : 'start symbol'));
      body.appendChild(tr);
    });
    table.appendChild(body);
    var scroller = el_('div', { 'class': 'bnf-scroll' });
    scroller.appendChild(table);
    box.appendChild(scroller);
    if (d.truncated) box.appendChild(el_('p', { 'class': 'bnf-muted' }, 'The derivation is long, so only its first steps are shown.'));
    if (!token && compiled.ebnf) {
      box.appendChild(el_('p', { 'class': 'bnf-muted' },
        'With EBNF, one step applies a whole production and writes out every copy of a { } repetition and every [ ] choice at once.'));
    }
  }

  function markPosition(r) {
    var pre = el_('pre', { 'class': 'bnf-pre bnf-mark' });
    if (compiled.notation === 'token') {
      var toks = r.tokens || [];
      var before = toks.slice(0, r.error.pos).join(' ');
      var at = r.error.pos < toks.length ? toks[r.error.pos] : '(end of input)';
      pre.appendChild(document.createTextNode(before + (before ? ' ' : '')));
      pre.appendChild(el_('mark', null, at));
      pre.appendChild(document.createTextNode(toks.slice(r.error.pos + 1).length ? ' ' + toks.slice(r.error.pos + 1).join(' ') : ''));
    } else {
      var s = el.input.value;
      pre.appendChild(document.createTextNode(s.slice(0, r.error.pos)));
      pre.appendChild(el_('mark', null, r.error.pos < s.length ? s[r.error.pos] : '(end of input)'));
      pre.appendChild(document.createTextNode(s.slice(r.error.pos + 1)));
    }
    return pre;
  }

  function treeHtml(node, token) {
    var ul = el_('ul');
    ul.appendChild(treeLi(node, token, 0));
    return ul;
  }

  function treeLi(node, token, depth) {
    var li = el_('li');
    if (node.t !== undefined) {
      li.appendChild(el_('span', { 'class': 'bnf-leaf' }, node.tok ? node.t : '"' + node.t + '"'));
      return li;
    }
    var name = token ? node.name : '<' + node.name + '>';
    var det = el_('details');
    if (depth < 12) det.open = true;
    var sum = el_('summary');
    sum.appendChild(el_('span', { 'class': 'bnf-nt' }, name));
    sum.appendChild(el_('span', { 'class': 'bnf-rule' }, '  ::= ' + (node.text || (token ? 'ε' : '<empty>'))));
    det.appendChild(sum);
    var ul = el_('ul');
    if (!node.children.length) {
      var e = el_('li');
      e.appendChild(el_('span', { 'class': 'bnf-leaf bnf-empty' }, token ? 'ε' : '<empty>'));
      ul.appendChild(e);
    }
    node.children.forEach(function (c) { ul.appendChild(treeLi(c, token, depth + 1)); });
    det.appendChild(ul);
    li.appendChild(det);
    return li;
  }

  // ---------------- wiring ----------------

  function loadExample(id) {
    var ex = EXAMPLES.filter(function (x) { return x.id === id; })[0];
    if (!ex) return;
    applyState({ g: ex.grammar, n: ex.notation, e: ex.ebnf ? '1' : '0', w: '1', s: ex.start, i: ex.input });
  }

  function init() {
    ['notation', 'ebnf', 'ws', 'example', 'grammar', 'start', 'input', 'testBtn', 'genBtn', 'shareBtn',
      'badge', 'ebnfWhat', 'wsRow', 'inputLabel', 'messages', 'result', 'helpCourse', 'helpToken', 'shareStatus']
      .forEach(function (id) { el[id] = $('bnf-' + id); });

    EXAMPLES.forEach(function (ex) { el.example.appendChild(el_('option', { value: ex.id }, ex.label)); });

    var timer = null;
    el.grammar.addEventListener('input', function () {
      clearTimeout(timer);
      timer = setTimeout(function () { recompile(); }, 250);
    });
    el.notation.addEventListener('change', function () { recompile(); });
    el.ebnf.addEventListener('change', function () { recompile(); });
    el.ws.addEventListener('change', function () { save(); if (lastResult) runTest(); });
    el.start.addEventListener('change', function () { save(); if (lastResult) runTest(); });
    el.example.addEventListener('change', function () {
      if (el.example.value) loadExample(el.example.value);
      el.example.value = '';
    });
    el.input.addEventListener('keydown', function (ev) { if (ev.key === 'Enter') { ev.preventDefault(); runTest(); } });
    el.testBtn.addEventListener('click', runTest);
    el.genBtn.addEventListener('click', function () {
      var s = E.generate(compiled, el.start.value, Math.random, el.ws.checked);
      if (s === null) {
        clearResult('This start symbol derives no finished string at all, so there is nothing to generate.');
        return;
      }
      el.input.value = s;
      runTest();
    });
    el.shareBtn.addEventListener('click', function () {
      var url = shareUrl();
      try { window.history.replaceState(null, '', url); } catch (e) { /* ignore */ }
      function done(msg) { el.shareStatus.textContent = msg; setTimeout(function () { el.shareStatus.textContent = ''; }, 4000); }
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(url).then(function () { done('Link copied. It holds the grammar, the settings and the input.'); },
          function () { done('The address bar now holds the share link; copy it from there.'); });
      } else {
        done('The address bar now holds the share link; copy it from there.');
      }
    });

    var s = fromHash() || load();
    if (s) applyState(s); else loadExample('warmup');
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
}());
