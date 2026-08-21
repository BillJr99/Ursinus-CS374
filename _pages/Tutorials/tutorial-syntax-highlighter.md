---
layout: tutorial
permalink: /Tutorials/SyntaxHighlighter
title: "CS374: A Syntax Highlighter for Your Language with tree-sitter"

info:
  coursenum: CS374
  goals:
    - To write a small tree-sitter grammar for your team language
    - To generate a parser and test it with tree-sitter's playground and CLI
    - To package a minimal VS Code extension that syntax-highlights your language
    - To (optionally) surface one diagnostic from your own parser as an editor squiggle
    - To demo editor support for a language you invented

readings:
  - rtitle: "tree-sitter: Creating Parsers"
    rlink: "https://tree-sitter.github.io/tree-sitter/creating-parsers"
  - rtitle: "tree-sitter: Playground"
    rlink: "https://tree-sitter.github.io/tree-sitter/playground"
  - rtitle: "VS Code: Syntax Highlight Guide"
    rlink: "https://code.visualstudio.com/api/language-extensions/syntax-highlight-guide"

tags:
  - tooling
  - tree-sitter
  - editor
  - final-project
---

# A Syntax Highlighter for Your Language with tree-sitter

This tutorial is a companion to the **Team Language Project** Extensions Menu. It shows how to give the language your team invented real editor support (syntax highlighting, and optionally a live diagnostic) which is one of the highest-impact things you can show at Demo Day: an audience *immediately* understands "we built a language" when they see it light up with color in a real editor.

Scope this small. Highlighting plus (optionally) one diagnostic is plenty for an undergraduate extension. You do not need a full language server.

---

## Section 1: Two ways to add editor support

There are two common routes, and you can pick based on ambition:

1. **TextMate grammar (simplest).** A JSON/plist file of regular expressions that VS Code uses to color tokens. No parser needed. Good enough for keyword/number/string/comment coloring. Start here if time is tight.
2. **tree-sitter grammar (recommended).** You write a small grammar; tree-sitter generates a fast incremental parser; a `highlights.scm` query maps syntax nodes to color categories. This is what ships in modern editors and gives structure-aware highlighting (e.g., a function name colored differently from a variable). It also compiles to WebAssembly, so it runs anywhere.

The rest of this tutorial uses tree-sitter.

---

## Section 2: A minimal tree-sitter grammar

Install the CLI (via `npm`):

```bash
npm install -g tree-sitter-cli
mkdir tree-sitter-mylang && cd tree-sitter-mylang
tree-sitter init            # scaffolds the project
```

Write `grammar.js`. Here is a tiny grammar for an expression-and-let language; adapt the rules to your team's actual syntax:

```js
module.exports = grammar({
  name: 'mylang',
  rules: {
    source_file: $ => repeat($._statement),
    _statement: $ => choice($.let_stmt, $.print_stmt),
    let_stmt: $ => seq('let', $.identifier, '=', $._expr, ';'),
    print_stmt: $ => seq('print', $._expr, ';'),
    _expr: $ => choice($.number, $.identifier, $.binary),
    binary: $ => choice(
      prec.left(1, seq($._expr, '+', $._expr)),
      prec.left(2, seq($._expr, '*', $._expr)),
    ),
    number: $ => /\d+/,
    identifier: $ => /[a-zA-Z_]\w*/,
  }
});
```

Generate and test the parser:

```bash
tree-sitter generate
echo 'let x = 2 + 3 * 4; print x;' | tree-sitter parse /dev/stdin
```

You should see a parse tree. Iterate in the [tree-sitter playground](https://tree-sitter.github.io/tree-sitter/playground); paste your grammar and type programs to watch the tree update live.

> **Reuse your EBNF:** you already wrote a precedence-annotated grammar in the Parser assignment. Your tree-sitter `prec.left`/`prec.right` annotations mirror the precedence ladder you built there; this is the same knowledge in a new notation.

---

## Section 3: Highlighting queries

Create `queries/highlights.scm` mapping nodes to standard highlight names:

```scheme
"let" @keyword
"print" @keyword
(number) @number
(identifier) @variable
(let_stmt (identifier) @variable.definition)
["+" "*"] @operator
```

Editors that understand tree-sitter (Neovim, Zed, Helix, and the Emscripten/WASM path for VS Code) will color your language using these queries.

---

## Section 4: Package a VS Code extension

For VS Code specifically, the lowest-friction highlighter is a TextMate grammar wrapped in an extension:

```bash
npm install -g yo generator-code
yo code           # choose "New Language Support"
```

Fill in your language id (`mylang`), file extension (`.ml`), and edit the generated `syntaxes/mylang.tmLanguage.json` to add patterns for your keywords, numbers, strings, and comments. Press `F5` in VS Code to launch an Extension Development Host and open a `.ml` file; it should be colored.

To use your tree-sitter grammar inside VS Code instead, compile it to WASM (`tree-sitter build --wasm`) and load it with the `vscode-tree-sitter` integration; this is the more advanced path.

---

## Section 5 (optional): One diagnostic from your own parser

The "wow" upgrade: surface a real error from *your* parser as an editor squiggle. A VS Code extension can run your interpreter on save and publish diagnostics:

```js
// on save: run `python3 mylang.py <file> --check`, parse its "line L, col C: message"
// error output, and push a vscode.Diagnostic at that range.
```

Because your Parser and Interpreter assignments already emit positioned errors (`line L, col C: message`), you have everything you need; you are just piping one line of error output into the editor's diagnostics API. One diagnostic is enough for full credit on this extension.

---

## Section 6: What to demo

At Demo Day, open a sample program from your `examples/` folder in a real editor with your extension active. Show: keyword/number/operator coloring, and (if you did Section 5) a deliberate error producing a red squiggle at the right position. Keep a short README explaining how a grader installs the extension (`code --install-extension mylang-0.0.1.vsix`).

---

## Reference

- [tree-sitter: Creating Parsers](https://tree-sitter.github.io/tree-sitter/creating-parsers)
- [tree-sitter Playground](https://tree-sitter.github.io/tree-sitter/playground)
- [VS Code Syntax Highlight Guide](https://code.visualstudio.com/api/language-extensions/syntax-highlight-guide)
- [VS Code: Programmatic Language Features (diagnostics)](https://code.visualstudio.com/api/language-extensions/programmatic-language-features)
