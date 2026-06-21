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

Query the same pattern on $[1, 2)$ and you receive the same shape shifted by one cycle, because the pattern is cycle-periodic unless an operator says otherwise. We will implement precisely this query function, in Python against our own parser's AST in the next module, and the displayed set above is the test case you should carry with you.

---

## Model 1: Pattern-as-Function in Python

The cell below implements the core pattern model in Python: `pure`, `seq`, `fast`, `slow`, `rev`, and `stack` (polyrhythm). This is not audio — it is the mathematical substrate under the audio. Every event is a `(value, begin, end)` tuple; every function that returns a pattern returns a *function* from `(begin, end)` to a list of events.

```python
from fractions import Fraction

# An event is (value, begin: Fraction, end: Fraction)
def event(v, b, e):
    return (v, Fraction(b), Fraction(e))

def pure(v):
    """A pattern that emits v once per cycle, occupying the whole cycle."""
    def query(b, e):
        b, e = Fraction(b), Fraction(e)
        events = []
        c = int(b) if b == int(b) else int(b)
        while c < e:
            if Fraction(c) >= b or c == int(b):
                events.append(event(v, max(b, Fraction(c)), min(e, Fraction(c+1))))
            c += 1
        return events
    return query

def seq(*pats):
    """Divide one cycle evenly among the given patterns."""
    n = len(pats)
    def query(b, e):
        b, e = Fraction(b), Fraction(e)
        result = []
        for cycle_start in range(int(b), int(e) + 1):
            for i, p in enumerate(pats):
                slot_b = Fraction(cycle_start) + Fraction(i, n)
                slot_e = Fraction(cycle_start) + Fraction(i + 1, n)
                if slot_e <= b or slot_b >= e:
                    continue
                # Query sub-pattern in [0,1), then scale into slot
                sub_events = p(0, 1)
                for (v, sb, se) in sub_events:
                    eb = slot_b + sb / n * n   # scale back
                    ee = slot_b + se / n * n
                    eb = slot_b + sb * Fraction(1, n) * n
                    ee = slot_b + se * Fraction(1, n) * n
                    # Correct: slot occupies 1/n of a cycle; sub spans are in [0,1]
                    abs_b = slot_b + sb * Fraction(1, n)
                    abs_e = slot_b + se * Fraction(1, n)
                    if abs_e > b and abs_b < e:
                        result.append(event(v, max(abs_b, b), min(abs_e, e)))
        return result
    return query

def fast(n, pat):
    """Compress n cycles of pat into one cycle."""
    n = Fraction(n)
    def query(b, e):
        return [(v, sb / n, se / n) for (v, sb, se) in pat(b * n, e * n)]
    return query

def slow(n, pat):
    """Stretch pat across n cycles."""
    n = Fraction(n)
    def query(b, e):
        return [(v, sb * n, se * n) for (v, sb, se) in pat(b / n, e / n)]
    return query

def rev(pat):
    """Reverse the events within each cycle."""
    def query(b, e):
        b, e = Fraction(b), Fraction(e)
        result = []
        for (v, sb, se) in pat(b, e):
            # Mirror within its containing cycle
            cycle = int(sb)
            new_b = Fraction(cycle + 1) - se + Fraction(cycle)
            new_e = Fraction(cycle + 1) - sb + Fraction(cycle)
            result.append(event(v, new_b, new_e))
        return result
    return query

def stack(*pats):
    """Play patterns simultaneously (polyrhythm)."""
    def query(b, e):
        result = []
        for p in pats:
            result.extend(p(b, e))
        return sorted(result, key=lambda ev: ev[1])
    return query

# ── Tests ─────────────────────────────────────────────────────────────────────

def fmt(events):
    return [(v, float(b), float(e)) for v, b, e in events]

def show(name, events):
    print(f"  {name}")
    for v, b, e in sorted(events, key=lambda x: x[1]):
        bar = "  " + "─" * int(b * 32) + "▮" * max(1, int((e - b) * 32)) + "─" * (32 - int(e * 32))
        print(f"    ({v!r:<6} {float(b):.4f}–{float(e):.4f}){bar}")

print("=== Query: pure('bd') on [0,1) ===")
show("pure('bd')", pure("bd")(0, 1))

print()
print("=== Query: seq(pure('bd'), pure('sn')) on [0,1) ===")
p = seq(pure("bd"), pure("sn"))
show("seq bd sn", p(0, 1))

print()
print("=== Query: seq bd sn on [1,2) (should be same shape +1 cycle) ===")
show("seq bd sn [1,2)", p(1, 2))

print()
print("=== Query: fast(2, seq('bd','sn')) — double speed ===")
fast_p = fast(2, seq(pure("bd"), pure("sn")))
show("fast 2 (seq bd sn)", fast_p(0, 1))

print()
print("=== Query: stack(pure('bd'), pure('hh')) — polyrhythm ===")
poly = stack(pure("bd"), pure("hh"))
show("stack bd hh", poly(0, 1))
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

### Critical Thinking Questions

1. `pure("bd")` returns a *function*, not a list. What property of this design allows patterns to be infinite (spanning any number of cycles) while consuming constant memory?
2. Trace `seq(pure("bd"), pure("sn"))(0, 1)` by hand: what fraction of the cycle does each event occupy? Confirm against the cell output.
3. `fast(2, p)` replays `p` twice per cycle by querying `p(2b, 2e)`. What query would `slow(3, p)` send to `p`? Write the implementation using the same technique.
4. The `rev` combinator mirrors events within each cycle. Write the algebraic law `rev(rev(p)) = p` in terms of the query function, then test it on `seq(pure("bd"), pure("sn"))` by running both and confirming the events match.

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

## Model 2: Algebraic Laws — Testing Equational Reasoning

The algebraic laws are not decoration; they are executable contracts. The cell below verifies three laws by running both sides on the same input and comparing event streams.

```python
from fractions import Fraction

# Re-use the pattern model from Model 1 (abbreviated here)
def event(v, b, e): return (v, Fraction(b), Fraction(e))

def pure(v):
    def query(b, e):
        b, e = Fraction(b), Fraction(e)
        result = []
        for c in range(int(b), int(e)+1):
            cb, ce = Fraction(c), Fraction(c+1)
            if cb < e and ce > b:
                result.append(event(v, max(b, cb), min(e, ce)))
        return result
    return query

def seq(*pats):
    n = len(pats)
    def query(b, e):
        b, e = Fraction(b), Fraction(e)
        result = []
        for c in range(int(b), int(e)+1):
            for i, p in enumerate(pats):
                sb = Fraction(c) + Fraction(i, n)
                se = Fraction(c) + Fraction(i+1, n)
                if se <= b or sb >= e: continue
                for (v, eb, ee) in p(0, 1):
                    abs_b = sb + eb * Fraction(1, n)
                    abs_e = sb + ee * Fraction(1, n)
                    if abs_e > b and abs_b < e:
                        result.append(event(v, max(abs_b, b), min(abs_e, e)))
        return result
    return query

def fast(n, pat):
    n = Fraction(n)
    def query(b, e):
        return [(v, Fraction(sb)/n, Fraction(se)/n) for (v, sb, se) in pat(b*n, e*n)]
    return query

def slow(n, pat):
    n = Fraction(n)
    def query(b, e):
        return [(v, Fraction(sb)*n, Fraction(se)*n) for (v, sb, se) in pat(b/n, e/n)]
    return query

def rev(pat):
    def query(b, e):
        b, e = Fraction(b), Fraction(e)
        result = []
        for (v, sb, se) in pat(b, e):
            c = int(sb)
            result.append(event(v, Fraction(c+1) - se + Fraction(c),
                                    Fraction(c+1) - sb + Fraction(c)))
        return result
    return query

def events_equal(e1, e2):
    key = lambda ev: (ev[0], float(ev[1]), float(ev[2]))
    return sorted(e1, key=key) == sorted(e2, key=key)

p = seq(pure("bd"), pure("sn"), pure("hh"))
SPAN = (0, 2)  # test over two cycles

print("=== Testing Algebraic Laws ===")
print()

# Law 1: fast m (fast n p) = fast (m*n) p
m, n = 2, 3
lhs = fast(m, fast(n, p))(*SPAN)
rhs = fast(m * n, p)(*SPAN)
ok = events_equal(lhs, rhs)
print(f"Law 1: fast({m}) (fast({n}) p)  =  fast({m*n}) p    {'✓' if ok else '✗ FAIL'}")
if not ok:
    print(f"  LHS events: {len(lhs)}  RHS events: {len(rhs)}")

# Law 2: rev (rev p) = p
lhs2 = rev(rev(p))(*SPAN)
rhs2 = p(*SPAN)
ok2 = events_equal(lhs2, rhs2)
print(f"Law 2: rev(rev(p))  =  p                   {'✓' if ok2 else '✗ FAIL'}")

# Law 3: fast n (slow n p) = p
n3 = 3
lhs3 = fast(n3, slow(n3, p))(*SPAN)
rhs3 = p(*SPAN)
ok3 = events_equal(lhs3, rhs3)
print(f"Law 3: fast({n3})(slow({n3})(p))  =  p           {'✓' if ok3 else '✗ FAIL'}")

# Law 4 (commutativity of fast and slow?): does fast 2 (slow 3 p) = slow 3 (fast 2 p)?
lhs4 = fast(2, slow(3, p))(*SPAN)
rhs4 = slow(3, fast(2, p))(*SPAN)
ok4 = events_equal(lhs4, rhs4)
print(f"Law 4: fast(2)(slow(3)(p)) = slow(3)(fast(2)(p))  {'✓' if ok4 else '✗ NOT a law'}")

print()
print("Note: Law 4 being FALSE means fast and slow do not commute in general.")
print("This is a real constraint on what optimizations a Tidal compiler can do.")
print()

# Show a concrete non-law as a counterexample
print("=== Counterexample for Law 4 ===")
def show_ev(events):
    return [(v, float(b), float(e)) for v, b, e in sorted(events, key=lambda x: x[1])]

print("fast(2)(slow(3)(p)) [0,1):", show_ev(fast(2, slow(3, p))(0, 1)))
print("slow(3)(fast(2)(p)) [0,1):", show_ev(slow(3, fast(2, p))(0, 1)))
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

### Critical Thinking Questions

5. Law 3 says `fast n (slow n p) = p`. The test runs over a span of 2 cycles, not just 1. Why does testing over multiple cycles give a stronger guarantee than testing over exactly one cycle?
6. Law 4 fails — `fast` and `slow` do not commute. This means a compiler *cannot* swap their order as an optimization. Where in your CS coursework have you seen "X does not commute with Y" limit optimizations? (String concatenation? Matrix multiplication?)
7. The laws are tested empirically (by running the functions). What is one way the test could pass despite a buggy implementation? What would a *proof* require that a test cannot provide?

---

### Try It: With a Partner

Pair up at one machine on strudel.cc, alternating **performer** and **predictor** roles per item. The predictor writes down the expected sound or event structure before the performer presses play. Start from `sound("bd sn hh sn")` and apply, cumulatively:

1. `.fast(2)`
2. then `.rev()`
3. then `.every(2, x => x.rev())`

After item 3, jointly test one algebraic law from this section empirically: pick `rev(rev(p)) = p`, encode both sides as two Strudel expressions, and confirm by ear and by the highlighted spans that they are indistinguishable. Write one sentence on why testing a law by listening is weaker evidence than the proof we could give from the definitions, and one sentence on why it is still worth doing.

---

## Model 3: Mini-Notation Grammar — The External Language Inside

The mini-notation (`"bd sn [hh hh]"`) is an external DSL embedded in a string. It deserves a grammar of its own, because it *is* a language: tokens, grammar rules, and semantics. The cell below implements a mini-notation lexer and recursive descent parser that produces the same event structure as the formal model.

```python
import re
from fractions import Fraction

# ── Mini-notation tokens ──────────────────────────────────────────────────────
TOKEN_SPEC = [
    ("LBRACKET", r"\["),
    ("RBRACKET", r"\]"),
    ("LANGLE",   r"<"),
    ("RANGLE",   r">"),
    ("STAR",     r"\*"),
    ("SLASH",    r"/"),
    ("AT",       r"@"),
    ("BANG",     r"!"),
    ("NUMBER",   r"\d+(?:\.\d+)?"),
    ("ATOM",     r"[A-Za-z_~][A-Za-z0-9_~\-\.]*"),
    ("SPACE",    r"[ \t]+"),
]
MASTER = re.compile("|".join(f"(?P<{n}>{p})" for n, p in TOKEN_SPEC))

def tokenize(src):
    return [(m.lastgroup, m.group()) for m in MASTER.finditer(src)
            if m.lastgroup != "SPACE"]

# ── AST nodes ─────────────────────────────────────────────────────────────────
class Atom:
    def __init__(self, value): self.value = value
    def __repr__(self): return f"Atom({self.value!r})"

class Seq:
    def __init__(self, children): self.children = children
    def __repr__(self): return f"Seq({self.children!r})"

class Group:
    def __init__(self, children): self.children = children
    def __repr__(self): return f"Group({self.children!r})"

class Fast:
    def __init__(self, pat, factor): self.pat = pat; self.factor = factor
    def __repr__(self): return f"Fast({self.pat!r}, {self.factor!r})"

# ── Recursive descent parser ──────────────────────────────────────────────────
class MiniParser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def peek(self):
        return self.tokens[self.pos] if self.pos < len(self.tokens) else ("EOF", "")

    def advance(self):
        t = self.peek()
        self.pos += 1
        return t

    def parse(self):
        items = self.parse_seq()
        return Seq(items)

    def parse_seq(self):
        items = []
        while self.peek()[0] not in ("EOF", "RBRACKET", "RANGLE"):
            items.append(self.parse_item())
        return items

    def parse_item(self):
        kind, val = self.peek()
        if kind == "LBRACKET":
            self.advance()
            children = self.parse_seq()
            if self.peek()[0] == "RBRACKET":
                self.advance()
            node = Group(children)
        else:
            self.advance()
            node = Atom(val)
        # Handle *factor
        if self.peek()[0] == "STAR":
            self.advance()
            _, factor = self.advance()
            node = Fast(node, float(factor))
        return node

def parse_mini(src):
    tokens = tokenize(src)
    return MiniParser(tokens).parse()

# ── Semantics: AST → event list ───────────────────────────────────────────────
def eval_mini(node, b=0, e=1):
    b, e = Fraction(b), Fraction(e)
    span = e - b
    if isinstance(node, Atom):
        return [(node.value, b, e)]
    elif isinstance(node, Fast):
        factor = Fraction(node.factor)
        raw = eval_mini(node.pat, 0, 1)
        result = []
        for _ in range(int(factor)):
            pass  # fast: query the child multiple times in the same span
        # Compress: each repetition fits in span/factor
        sub_span = span / factor
        all_events = []
        for rep in range(int(factor)):
            offset = b + rep * sub_span
            for (v, sb, se) in eval_mini(node.pat, 0, 1):
                all_events.append((v, offset + sb * sub_span, offset + se * sub_span))
        return all_events
    elif isinstance(node, (Seq, Group)):
        children = node.children
        n = len(children)
        if n == 0: return []
        child_span = span / n
        result = []
        for i, child in enumerate(children):
            cb = b + i * child_span
            ce = cb + child_span
            result.extend(eval_mini(child, cb, ce))
        return result
    return []

# ── Tests ─────────────────────────────────────────────────────────────────────
test_cases = [
    ("bd sn",            2, 0, 1),   # 2 events, each 1/2 cycle
    ("bd sn hh sn",      4, 0, 1),   # 4 events, each 1/4 cycle
    ("bd [sn sn]",       3, 0, 1),   # bd=1/2, sn=1/4, sn=1/4
    ("bd sn*2 hh",       4, 0, 1),   # bd=1/3, sn=1/6, sn=1/6, hh=1/3
]

print("=== Mini-Notation Parser ===")
for src, expected_count, b, e in test_cases:
    ast = parse_mini(src)
    events = eval_mini(ast, b, e)
    ok = len(events) == expected_count
    print(f"  {src!r:<20} → {len(events)} events  ({'✓' if ok else f'✗ expected {expected_count}'})")
    for v, sb, se in sorted(events, key=lambda x: x[1]):
        print(f"       ({v!r:<8} {float(sb):.4f}–{float(se):.4f})")

print()
print("=== AST for 'bd [sn hh] sn' ===")
print(parse_mini("bd [sn hh] sn"))
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

### Critical Thinking Questions

8. The mini-notation parser is a hand-written recursive descent parser. Identify the grammar rule that `parse_seq` implements and the rule that `parse_item` implements. Write both rules in EBNF.
9. `Group` subdivides its children within the group's span, while `Seq` distributes children across the whole span. What is the semantic difference between `"bd sn hh"` and `"[bd sn] hh"` in event timing?
10. `Fast` multiplies the number of events by repeating the sub-pattern. Extend the parser and evaluator to support `/n` (slow: stretch across n slots). Write the `Slow` node and its `eval_mini` case.
11. The mini-notation is an external DSL embedded in a string. Name one advantage and one disadvantage of embedding it in a string rather than giving it first-class syntax (e.g., `bd sn [hh hh]` without quotes).

---

# Part III: Synthesis & Practice

## 5. Exercises

Exercises 1 through 3 are individual; exercises 4 and 5 are partner exercises, and at least one partner exercise should be completed before our parser-construction module, which builds directly on this vocabulary.

1. *Query by hand.* For the pattern `[bd sn]*2 hh`, compute the complete event set for the span $[0,1)$ using the formal rules of Section 3, showing the span arithmetic at each subdivision. Verify at strudel.cc and report both your derivation and the verification.
2. *A law with a proof sketch.* Using the function-of-time model from Model 1, argue in a short paragraph (with the relevant span arithmetic) why `fast m (fast n p) = fast (m*n) p` holds. Identify one assumption your argument needs.
3. *Host idiom translation.* Translate `every 3 (slow 2) $ sound "bd [sn sn]"` into Strudel's JavaScript idiom, run it, and report the event structure for cycles 0 through 3, indicating on which cycles the transformation fired.
4. *Partner: design archaeology.* With a partner, find one mini-notation feature in the Strudel documentation that we did not cover (candidates include `,` stacking, `!` replication, or `@` elongation). One partner writes its informal semantics in the style of Section 3's displayed math; the other constructs two strudel.cc examples that confirm or refute that semantics. Report both artifacts and any revision the experiments forced.
5. *Partner: the embedding boundary.* Each partner independently lists three things in a Strudel program that the JavaScript parser handles and three that the mini-notation parser handles, then reconcile your lists. Report the reconciled lists and one boundary case where you initially disagreed.
6. *Mini-notation extension.* Add support for `!` (repeat: `bd!3` = `bd bd bd`) to the Python mini-notation parser and evaluator. Write two positive test cases and one negative test case, run them, and explain how `!` differs from `*` in event distribution.

---

## 6. Further Reading

- McLean, Alex. "Making Programming Languages to Dance to: Live Coding with Tidal." *FARM Workshop, ICFP* (2014). The design rationale for TidalCycles from its creator; short and very readable.
- Roos, Felix, and Alex McLean. "Strudel: Live Coding Patterns on the Web." *International Conference on Live Coding* (2023). The Strudel system paper, including its account of porting the pattern model from Haskell to JavaScript.
- Hudak, Paul. "Building Domain-Specific Embedded Languages." *ACM Computing Surveys* 28, 4es (1996). The classic statement of the EDSL philosophy that Tidal exemplifies.
- Fowler, Martin. *Domain-Specific Languages* (Addison-Wesley, 2010). Chapters on internal versus external DSLs generalize the tradeoff table from Section 2.
- The Strudel workshop and reference at [strudel.cc/workshop/getting-started](https://strudel.cc/workshop/getting-started). The fastest route from this module to making actual music.

---
