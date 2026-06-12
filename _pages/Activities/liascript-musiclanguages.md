# Languages for Live Coding Music: Strudel and TidalCycles

<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://github.com/BillJr99/Ursinus-CS374-Fall2026/blob/main/_pages/Activities/liascript-musiclanguages.md or locally if deployed via https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374/main/_pages/Activities/liascript-musiclanguages.md

import: https://raw.githubusercontent.com/liascript/CodeRunner/master/README.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

# Languages for Live Coding Music: Strudel and TidalCycles

This module introduces **domain-specific languages (DSLs)** through two living, performing specimens: **TidalCycles**, a pattern language embedded in Haskell, and **Strudel**, its JavaScript-hosted sibling that runs in any browser. We move from **the live coding problem domain $\rightarrow$ embedded versus external DSL design $\rightarrow$ a formal model of patterns as functions of time $\rightarrow$ combinators and their algebraic laws $\rightarrow$ hands-on performance**, and in doing so we assemble the conceptual vocabulary, syntax versus semantics, host language leverage, denotation, and equational reasoning, that the rest of this unit will exercise when we build a parser for these languages ourselves.

---

## 0. Environment & Utilities

This module requires only a web browser. Strudel runs entirely client-side at [strudel.cc](https://strudel.cc), with no installation or account; open it now in a second tab, because you will be asked to play with it throughout. The code cell below confirms that the JavaScript fragments we study are syntactically ordinary JavaScript, which is itself one of the module's central points.

---

## Code Cell

```javascript
// Strudel expressions are ordinary JavaScript expressions: method
// chains over pattern objects. This cell only demonstrates the shape;
// the audio engine lives at strudel.cc.

const description = 'sound("bd sn [hh hh] sn")';
console.log("A Strudel program is a JS expression, e.g.:", description);
console.log("Environment ready.");
```

---

# Part I: The Problem Domain and Two Language Designs

## 1. Live Coding as a Language Design Problem

**Live coding is the practice of writing and rewriting a running program as a public performance.** A performer projects their editor, the audience watches the code change, and the music changes with it. This domain imposes unusual and instructive requirements on a programming language, and reading those requirements as a language designer would is our first exercise in this module. The program must be **concise**, because every keystroke happens on stage; it must be **modifiable while running**, because stopping the program stops the music; it must be **declarative about time**, because the performer thinks in cycles and beats rather than in callbacks and timestamps; and its errors must be **recoverable**, because a syntax error during a performance should not produce silence.

**TidalCycles and Strudel answer these requirements with the same core design.** TidalCycles, created by Alex McLean, is a library of pattern operations embedded in **Haskell**; Strudel, created by Felix Roos with McLean, reimplements the same pattern model in **JavaScript** so that it runs in a browser with zero installation. Both share a second, smaller language inside themselves: the **mini-notation**, the quoted string language of patterns like `"bd sn [hh hh] sn"`, which we will give a grammar and a parser of our own in the next module. One pattern model, two host languages, one shared inner notation: this triangle is the cleanest case study of DSL architecture you are likely to encounter, and it is why a music language has a home in a principles of programming languages course.

---

## 2. Embedded Versus External DSLs

**An external DSL has its own syntax, lexer, and parser; an embedded DSL borrows all three from a host language.** SQL, regular expressions, and `make` are external: nothing about their syntax is Java or C. An embedded DSL (EDSL) is instead a library designed so artfully that using it feels like writing a new language, while every expression remains a legal host-language expression, parsed by the host's parser and checked by the host's type system.

**Tidal and Strudel are hybrids, and the hybrid is the lesson.** The combinator layer is embedded: `every 4 (fast 2) $ sound "bd sn"` is a legal Haskell expression, and `sound("bd sn").every(4, x => x.fast(2))` is legal JavaScript. The mini-notation layer is external: the string `"bd sn"` is opaque to Haskell and JavaScript alike, and each system ships a hand-built parser for it. The designers chose an external inner language precisely where host syntax would be too noisy, writing a drum pattern as a Haskell list of constructors would be unbearable on stage, and an embedded outer language precisely where the host's powers, higher-order functions, types, and a mature toolchain, are too valuable to give up.

**The tradeoffs generalize far beyond music.** Within the scope of the DSLs you will meet professionally, configuration languages, query builders, infrastructure description languages, the same forces recur:

| Axis | Embedded DSL | External DSL |
|------|--------------|--------------|
| Implementation cost | Low: a library | High: lexer, parser, tooling |
| Syntax freedom | Constrained by host grammar | Unlimited |
| Error messages | Host's, often confusing | Custom, can be excellent |
| Host interop | Free and total | Requires explicit bridges |
| Static checking | Inherited from host types | Must be built by hand |

[[MC]]
Strudel's designers parse `"bd sn [hh hh]"` with a dedicated parser rather than asking performers to write a JavaScript array of objects. Which DSL design consideration most directly justifies that choice?
- (x) Syntax freedom: the domain demands a notation more concise than host-language syntax permits, which is the classic argument for an external DSL layer.
- ( ) Implementation cost: external parsers are cheaper to build than JavaScript libraries.
- ( ) Static checking: strings receive stronger type checking than JavaScript objects.
- ( ) Host interop: strings cannot be passed to JavaScript functions, so a parser is mandatory.

---

### Try It: With a Partner

One partner argues for an **embedded** design and the other for an **external** design of the following hypothetical DSL: a language for describing amateur radio antenna geometries (element lengths, spacings, and feed points) to be consumed by a simulation engine. Take four minutes per side, using the table above as your scorecard, then jointly write a two-sentence recommendation and identify which single axis dominated your decision. Be prepared to report out; different teams legitimately reach different conclusions, and the quality of the argument, not the verdict, is what we will discuss.

---

# Part II: A Formal Model of Patterns

## 3. Patterns as Functions of Time

**The central abstraction of both languages is that a pattern is a function from a span of time to the events occurring within it.** Time is measured in **cycles**, with one cycle conventionally spanning the rational interval $[0, 1)$, the next $[1, 2)$, and so on. Writing $\mathbb{Q}$ for the rationals, a span is a pair $(b, e)$ with $b \leq e$, an event is a value paired with the span it occupies, and a pattern of values of type $a$ is, to a first approximation,

$$
\text{Pattern}\ a \;\approx\; (b, e) \mapsto \{\, (v_i,\, b_i,\, e_i) \,\} \quad \text{with each } [b_i, e_i) \subseteq \text{the queried span}
$$

In Tidal's Haskell source this is nearly literal: a `Pattern a` wraps a query function from a timespan (Tidal calls it an arc) to a list of events. The consequences of choosing **function of time** rather than **list of notes** as the denotation are profound, and each one answers a requirement from Section 1. Patterns are infinite, since you may query cycle 10,000 as easily as cycle 0, yet they occupy constant memory, because nothing is stored, only computed on demand. Patterns are pure values, so transforming one produces a new pattern without mutating a running performance, which is what makes mid-performance code replacement safe. And patterns compose, because functions compose.

**A worked query.** Take the pattern denoted by `"bd sn"` and query the span $[0, 1)$. The sequence rule divides the span evenly, yielding the event set

$$
\{\ (\texttt{bd},\ 0,\ \tfrac{1}{2}),\quad (\texttt{sn},\ \tfrac{1}{2},\ 1)\ \}
$$

Query the same pattern on $[1, 2)$ and you receive the same shape shifted by one cycle, because the pattern is cycle-periodic unless an operator says otherwise. We will implement precisely this query function, in C, against our own parser's AST in the next module, and the displayed set above is the test case you should carry with you.

---

## Code Cell

```javascript
// A miniature, self-contained model of "pattern as function of time."
// pure(v) is the pattern of one event per cycle; seq(...) subdivides.
// Compare each function against the math in Section 3.

const pure = (v) => (b, e) => {
  const events = [];
  for (let c = Math.floor(b); c < e; c++) {
    if (c >= b) events.push({ value: v, begin: c, end: c + 1 });
  }
  return events;
};

const seq = (...pats) => (b, e) => {
  const n = pats.length;
  const events = [];
  for (let c = Math.floor(b); c < e; c++) {
    pats.forEach((p, i) => {
      // Child i owns [c + i/n, c + (i+1)/n); query it scaled into place.
      p(0, 1).forEach((ev) =>
        events.push({
          value: ev.value,
          begin: c + (i + ev.begin) / n,
          end:   c + (i + ev.end) / n,
        })
      );
    });
  }
  return events;
};

const pat = seq(pure("bd"), pure("sn"));
console.log(pat(0, 1));  // expect bd on [0, 0.5), sn on [0.5, 1)
console.log(pat(1, 2));  // expect the same shape, one cycle later
```

---

### Try It: Individually

Before running anything at strudel.cc, predict on paper the event set for one cycle of each pattern below, writing each answer in the set notation of Section 3. Then open strudel.cc, enter each pattern inside `sound("...")`, press play, and check your prediction against the highlighted spans in the editor.

1. `bd sn hh sn`
2. `bd [sn sn sn]`
3. `[bd bd] [sn [hh hh]]`

Record any prediction you got wrong and, in one sentence, which rule you had misapplied. Bring that sentence to class; the wrong answers are the curriculum.

---

## 4. Combinators and Their Laws

**A combinator is a function that builds patterns from patterns, and the important ones obey algebraic laws.** The core transformations in both languages include `fast n` (compress $n$ repetitions into each cycle), `slow n` (stretch across $n$ cycles), `rev` (reverse each cycle), and `every n f` (apply the transformation $f$ on every $n$th cycle only). Because patterns are pure functions, these combinators satisfy equations we can state and test, and equational reasoning about programs is a skill this course returns to repeatedly:

$$
\texttt{fast}\ m\ (\texttt{fast}\ n\ p) \;=\; \texttt{fast}\ (m \cdot n)\ p
\qquad\quad
\texttt{rev}\ (\texttt{rev}\ p) \;=\; p
$$

$$
\texttt{fast}\ n\ (\texttt{slow}\ n\ p) \;=\; p \qquad \text{for } n \neq 0
$$

**Currying is not a curiosity here; it is the performance interface.** In the Haskell expression `every 4 (fast 2) $ sound "bd sn"`, the subexpression `fast 2` is a **partial application**: `fast` has type `Pattern Time -> Pattern a -> Pattern a`, and supplying only the factor yields a function `Pattern a -> Pattern a`, exactly the shape `every` demands for its second argument. A Tidal performance is, syntactically, a stream of partially applied functions being composed live. Strudel, hosted in a language without curried-by-default functions, expresses the same idea with an explicit arrow: `.every(4, x => x.fast(2))`. Same denotation, different host idiom; when we study the lambda calculus in this unit's third module, you will see that the two are formally interchangeable, since currying is itself a lambda-calculus transformation.

[[MC]]
In `every 4 (fast 2) $ sound "bd sn"`, the Haskell type checker accepts `fast 2` as the second argument to `every`. What language feature makes this work?
- (x) Partial application: `fast` applied to one argument yields a function awaiting the pattern, which matches the transformation type `every` expects.
- ( ) Implicit casting: Haskell coerces the number 2 into a pattern transformation.
- ( ) Operator overloading: `fast` is redefined inside `every` to take one argument.
- ( ) Lazy evaluation: the missing argument is supplied later at run time by the audio engine.

---

### Try It: With a Partner

Pair up at one machine on strudel.cc, alternating **performer** and **predictor** roles per item. The predictor writes down the expected sound or event structure before the performer presses play. Start from `sound("bd sn hh sn")` and apply, cumulatively:

1. `.fast(2)`
2. then `.rev()`
3. then `.every(2, x => x.rev())`

After item 3, jointly test one algebraic law from this section empirically: pick `rev(rev(p)) = p`, encode both sides as two Strudel expressions, and confirm by ear and by the highlighted spans that they are indistinguishable. Write one sentence on why testing a law by listening is weaker evidence than the proof we could give from the definitions, and one sentence on why it is still worth doing.

---

# Part III: Synthesis & Practice

## 5. Exercises

Exercises 1 through 3 are individual; exercises 4 and 5 are partner exercises, and at least one partner exercise should be completed before our parser-construction module, which builds directly on this vocabulary.

1. *Query by hand.* For the pattern `[bd sn]*2 hh`, compute the complete event set for the span $[0,1)$ using the formal rules of Section 3, showing the span arithmetic at each subdivision. Verify at strudel.cc and report both your derivation and the verification.
2. *A law with a proof sketch.* Using the function-of-time model from the Code Cell in Section 3, argue in a short paragraph (with the relevant span arithmetic) why `fast m (fast n p) = fast (m*n) p` holds. Identify one assumption your argument needs.
3. *Host idiom translation.* Translate `every 3 (slow 2) $ sound "bd [sn sn]"` into Strudel's JavaScript idiom, run it, and report the event structure for cycles 0 through 3, indicating on which cycles the transformation fired.
4. *Partner: design archaeology.* With a partner, find one mini-notation feature in the Strudel documentation that we did not cover (candidates include `,` stacking, `!` replication, or `@` elongation). One partner writes its informal semantics in the style of Section 3's displayed math; the other constructs two strudel.cc examples that confirm or refute that semantics. Report both artifacts and any revision the experiments forced.
5. *Partner: the embedding boundary.* Each partner independently lists three things in a Strudel program that the JavaScript parser handles and three that the mini-notation parser handles, then reconcile your lists. Report the reconciled lists and one boundary case where you initially disagreed.

---

## 6. Further Reading

- McLean, Alex. "Making Programming Languages to Dance to: Live Coding with Tidal." *FARM Workshop, ICFP* (2014). The design rationale for TidalCycles from its creator; short and very readable.
- Roos, Felix, and Alex McLean. "Strudel: Live Coding Patterns on the Web." *International Conference on Live Coding* (2023). The Strudel system paper, including its account of porting the pattern model from Haskell to JavaScript.
- Hudak, Paul. "Building Domain-Specific Embedded Languages." *ACM Computing Surveys* 28, 4es (1996). The classic statement of the EDSL philosophy that Tidal exemplifies.
- Fowler, Martin. *Domain-Specific Languages* (Addison-Wesley, 2010). Chapters on internal versus external DSLs generalize the tradeoff table from Section 2.
- The Strudel workshop and reference at [strudel.cc/workshop/getting-started](https://strudel.cc/workshop/getting-started). The fastest route from this module to making actual music.

---
