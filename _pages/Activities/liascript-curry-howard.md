# The Curry-Howard Correspondence: Programs Are Proofs
<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://github.com/BillJr99/Ursinus-CS374-Fall2026/blob/gh-pages/_pages/Activities/liascript-curry-howard.md or locally via https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374-Fall2026/gh-pages/_pages/Activities/liascript-curry-howard.md

import: https://raw.githubusercontent.com/liascript/CodeRunner/master/README.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

# The Curry-Howard Correspondence: Programs Are Proofs

This is one of the most beautiful results in computer science. The Curry-Howard correspondence reveals that writing a program and proving a theorem are secretly the same activity. Consider the type `A → B`: in a programming language it means "a function from A to B," and you produce a value of that type by writing a function body that takes an A and returns a B. In logic, `A → B` means "A implies B," and you produce a proof of it by assuming A and deriving B — exactly what a function body does. A value of type `A → B` is simultaneously *a function* and *a proof of A implies B*. Every type annotation you write is a logical proposition; every well-typed function you write is a proof of that proposition; and every type error your checker reports is a gap in your proof. This correspondence runs all the way down: conjunction, disjunction, the empty type, and even dependent types all have precise logical counterparts. By the end of this activity you will be able to read a type signature as a logical formula and write a function as a logical proof.

## Learning Goals

By the end of this activity, you will be able to:

- State the Curry-Howard correspondence and map each of its three pillars — propositions-as-types, proofs-as-programs, proof-checking-as-type-checking — to concrete Python examples
- Construct Python type annotations that encode logical conjunction (product types) and disjunction (sum types), and explain why an uninhabited type corresponds to absurdity
- Write a function whose type signature constitutes a proof of a propositional tautology, and identify a function whose type cannot be inhabited
- Connect the Curry-Howard correspondence to practical language features in Rust (ownership types), Haskell (type classes), and proof assistants such as Coq

> **Before You Begin — Prerequisites**
>
> You should be comfortable with the following before starting this activity:
>
> - **Types in Python**: you can read and write type annotations (`int`, `str`, `Tuple[A, B]`, `Callable[[A], B]`, `Optional[A]`) and understand what it means for a value to have a type.
> - **Higher-order functions**: you can pass functions as arguments and return functions as values; you have worked with `map`, `filter`, and function composition.
> - **Lambda calculus basics**: you understand that a lambda `λx.e` takes an argument and substitutes it into a body, and you have seen combinator notation (K, S, I).
> - **Basic logic**: you know what a proposition, an implication (`P → Q`), a conjunction (`P ∧ Q`), and a disjunction (`P ∨ Q`) mean informally.
>
> **Quick Notation Bridge**
>
> | Logic | Type Theory | Meaning |
> |-------|-------------|---------|
> | Proposition P | Type `P` | Something to prove / construct |
> | Proof of P | Value of type `P` | Evidence / witness |
> | P ∧ Q | `(P, Q)` (product type) | Pair of proofs — need both |
> | P ∨ Q | `Either P Q` (sum type) | Proof of one or the other |
> | P → Q | `P -> Q` (function type) | Proof transformer — given P, produce Q |
>
> Keep this table open as you work through the activity; every code cell below illustrates one or more of these rows.

In 1934 Haskell Curry noticed that the type `A → B` resembles the logical implication `A ⊃ B`. In 1969 William Howard made it precise: **types are propositions, programs are proofs, and type-checking is proof-checking**. Every function you write is a proof of its type; every type error is a proof gap. This equivalence — called the **Curry-Howard correspondence** — connects programming language theory to mathematical logic at the deepest level, and it is the reason Rust, Haskell, and proof assistants like Coq and Lean can all be understood from the same foundation. The arc: **propositions-as-types → proof terms → product types as conjunction → sum types as disjunction → the empty type as absurdity → dependent types (a glimpse)**.

---

## Directions and Group Roles

Work in your POGIL team with rotated roles (**Manager**, **Recorder**, **Presenter**, **Reflector**). Every claim today is verified by writing a Python type or function. The Recorder maintains a two-column table: **Logic** | **Programming** — filling it in as each concept arrives. The Presenter explains one correspondence to another team at the end. After class, respond to the reflective prompt individually in your notebook.

---

# Part I: The Correspondence

## 1. Types Are Propositions

**Intuition.** In ordinary mathematics, a proposition is a statement that is either true or false, and a proof is the evidence that makes it true. In type theory, a *type* plays the role of a proposition: it is a specification that says "something of this shape exists." A *value* of that type plays the role of a proof: it is the concrete witness that the specification can be satisfied. The identity function `lambda x: x` has type `A -> A` for any type `A` — and indeed, `A implies A` is always true in logic (it is a tautology). Writing the function IS the proof.

The central table, which you will complete as you work through the activity:

| Logic | Programming |
|---|---|
| Proposition $P$ | Type `P` |
| Proof of $P$ | Value of type `P` |
| $P \Rightarrow Q$ (implication) | `P -> Q` (function type) |
| $P \wedge Q$ (conjunction) | `(P, Q)` (product / pair type) |
| $P \vee Q$ (disjunction) | `Either P Q` (sum / union type) |
| $\bot$ (absurdity / False) | Empty type (uninhabited) |
| $\neg P$ (negation) | `P -> Empty` (function to empty) |
| $\forall x: A.\ P(x)$ (universal) | Dependent function type `(x: A) -> P(x)` |
| $\exists x: A.\ P(x)$ (existential) | Dependent pair type `(x: A, P(x))` |

The row you will use most today: **a function of type `A -> B` is a proof that `A` implies `B`**. To prove `A ⊃ B`, assume `A` and derive `B` — exactly what a function does when it takes an argument of type `A` and returns a value of type `B`.

---

## Model 1: Functions as Proofs

### Critical Thinking Questions

1. The identity function `def identity(x): return x` has type `A -> A`. What logical proposition does this prove? (Write it using the ⊃ symbol.) Give the proof in one sentence: "Given any proof of A, we can produce..."

2. Function composition `compose(f, g)(x) = f(g(x))` has type `(B -> C) -> (A -> B) -> (A -> C)`. Write this as a logical statement using ⊃ and ∧. What famous logical rule does this prove? (Hint: `B ⊃ C`, `A ⊃ B`, therefore `A ⊃ C`.)

3. The K combinator from your lambda calculus work has type `A -> B -> A` (it ignores its second argument). What does this proposition say? Is it a tautology? Prove it in plain English.

4. The S combinator has type `(A -> B -> C) -> (A -> B) -> A -> C`. Identify this as a tautology of propositional logic. (It is the distributivity axiom: if A implies (B implies C), and A implies B, then A implies C.)

---

# Part II: Products and Sums

## 2. Conjunction as Pairs

**Intuition.** When you pair two values together — `(proof_of_P, proof_of_Q)` — you are doing exactly what a logician does when they say "here is a proof of P AND here is a proof of Q, therefore P ∧ Q is proved." The pair constructor IS the introduction rule for conjunction; tuple indexing (`pair[0]`, `pair[1]`) IS the two elimination rules. Once you see tuples this way, commutativity of `∧` becomes obvious: swap the elements of the pair.

> **Watch out!** In Python, `(a, b)` is just a runtime value — the type checker does not enforce that `a` has type `P` and `b` has type `Q` without explicit annotations. In Haskell or Rust the types are checked at compile time, so a pair truly *is* a proof. When you see `Tuple[P, Q]` annotations in the code cells below, pretend you are in a strict language: the annotation is the proposition, and the value is the proof.

In logic, a proof of `P ∧ Q` requires: a proof of `P` and a proof of `Q`. In programming, a value of type `(P, Q)` (a pair) is: a value of type `P` and a value of type `Q`. The correspondence is exact.

The *introduction rule* for `∧` says: if you have proofs of both `P` and `Q`, you have a proof of `P ∧ Q`. In code: `pair = (proof_of_p, proof_of_q)`.

The *elimination rules* say: from a proof of `P ∧ Q`, you can extract a proof of `P` (fst) or `Q` (snd). In code: `proof_of_p = pair[0]`.

---

## Code Cell: Products as Conjunction

```python
try:
    from typing import Tuple, TypeVar, Callable

    A = TypeVar('A')
    B = TypeVar('B')
    C = TypeVar('C')

    # Proof of A ∧ B: a pair
    def conj_intro(a: A, b: B) -> Tuple[A, B]:
        return (a, b)   # introduction rule: pack both proofs

    def conj_elim_left(pair: Tuple[A, B]) -> A:
        return pair[0]  # elimination: extract proof of A

    def conj_elim_right(pair: Tuple[A, B]) -> B:
        return pair[1]  # elimination: extract proof of B

    # Proof of commutativity: A ∧ B ⊃ B ∧ A
    # In code: a function from (A,B) to (B,A)
    def conj_commute(pair: Tuple[A, B]) -> Tuple[B, A]:
        return (conj_elim_right(pair), conj_elim_left(pair))

    # Verify
    p = conj_intro(42, "hello")
    print("pair:", p)
    print("left:", conj_elim_left(p))
    print("right:", conj_elim_right(p))
    print("commuted:", conj_commute(p))

except Exception as e:
    print(f"[ch:product] {e}")
    import traceback; traceback.print_exc()
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

---

## 3. Disjunction as Tagged Unions

**Intuition.** A proof of `P ∨ Q` does not require proofs of *both* — you only need to produce evidence for *one* of the two sides and declare which one it is. That is exactly what a tagged union does: `Left(v)` says "I have a P (here it is)" and `Right(v)` says "I have a Q (here it is)." The tag is the declaration; the value is the evidence. To use a disjunction proof (the elimination rule), you must handle both cases — which is why exhaustive `match` statements are mandatory in Haskell and Rust.

A proof of `P ∨ Q` is: *either* a proof of `P` (tagged "left") *or* a proof of `Q` (tagged "right"). In code, this is a tagged union (also called a sum type or `Either`):

```python
# A simple Either (sum type) in Python
class Left:
    def __init__(self, value): self.value = value
    def __repr__(self): return f"Left({self.value})"

class Right:
    def __init__(self, value): self.value = value
    def __repr__(self): return f"Right({self.value})"
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

The *elimination rule* for `∨` says: to prove `C` from `P ∨ Q`, prove `C` from `P` and prove `C` from `Q` separately (case analysis). In code: pattern-match on the tag.

---

## Code Cell: Sums as Disjunction

```python
try:
    class Left:
        def __init__(self, value): self.value = value
        def __repr__(self): return f"Left({self.value})"

    class Right:
        def __init__(self, value): self.value = value
        def __repr__(self): return f"Right({self.value})"

    # Proof of A ∨ B → C requires a case for each branch
    def disj_elim(either, f_left, f_right):
        if isinstance(either, Left):
            return f_left(either.value)    # case A: apply f_left
        else:
            return f_right(either.value)   # case B: apply f_right

    # Proof of commutativity: A ∨ B ⊃ B ∨ A
    def disj_commute(either):
        return disj_elim(either,
            lambda a: Right(a),   # Left(a) becomes Right(a)
            lambda b: Left(b))    # Right(b) becomes Left(b)

    # A ∧ (B ∨ C) ⊃ (A ∧ B) ∨ (A ∧ C)  — distributivity
    def distrib(pair):
        a, bc = pair
        return disj_elim(bc,
            lambda b: Left((a, b)),
            lambda c: Right((a, c)))

    # Verify
    x = Left(42)
    print("disj commute:", disj_commute(x))
    print("distrib:", distrib((1, Left("hello"))))
    print("distrib:", distrib((1, Right(3.14))))

except Exception as e:
    print(f"[ch:sum] {e}")
    import traceback; traceback.print_exc()
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

---

## Model 2: Proofs as Programs

### Critical Thinking Questions

5. Python's `Optional[A]` (either `A` or `None`) is a sum type. What logical proposition does `Optional[A]` correspond to? What proposition does a function `f: A -> Optional[B]` prove?

6. Haskell's `Either String Int` is used as a return type for functions that might fail: `Left msg` for errors, `Right n` for success. Identify this as the Maybe monad from the previous activity, but with error messages. What logical proposition does "a function that returns `Either String B`" prove about the existence of a `B`?

7. The `disj_elim` function (case analysis) corresponds to the logical elimination rule for `∨`. Pattern matching in Rust, Haskell, or Python 3.10 is syntactic sugar for `disj_elim`. How does this connect to the "pattern matching is exhaustive" requirement in Haskell (the compiler warns on missing cases)? What does a missing case mean *logically*?

8. In Rust, the `match` statement must be exhaustive — every case must be handled. This is enforced by the type system. In logic, this corresponds to the proof obligation: to eliminate a disjunction `P ∨ Q`, you must handle *both* cases. Why can't you omit a case without breaking the logical correspondence?

---

# Part III: The Empty Type and Absurdity

## 4. What Cannot Be Proved

**Intuition.** Not every proposition can be proved. In classical logic, `False` (written `⊥`) has no proof — it is false by definition. The type-theoretic counterpart is a type you can *name* but can never *construct a value of*. Since there is no way to call a function that returns a value of the empty type, a function whose *input* is the empty type is vacuously fine: it can never be called, so it never has to produce anything. This is the programming interpretation of "ex falso quodlibet" — from a contradiction, anything follows.

> **Watch out!** Python's `Never` (from `typing`) and `NoReturn` are only checked by *static type checkers* like mypy. At runtime Python will happily let you ignore them. The code cells below simulate the empty type with a class whose constructor always raises — this makes the constraint observable at runtime, but do not confuse the simulation with a real dependent type guarantee.

The logical proposition `⊥` (False, or absurdity) has no proof — it is uninhabited. Its type-theoretic counterpart is a type with no values: the **empty type** (called `Void` in Haskell, `Never` in Python, `!` in Rust).

Since you can never construct a value of the empty type, **a function of type `Empty -> A` is vacuously true**: the function is never called. This matches the logical principle "from False, anything follows" (ex falso quodlibet).

Negation `¬P` is defined as `P → ⊥`: to disprove `P`, show that assuming `P` leads to contradiction (an empty-type value).

---

## Code Cell: Absurdity

```python
try:
    # In Python we simulate the empty type via an exception that can never succeed
    class Empty:
        def __init__(self):
            raise RuntimeError("Empty type has no values — this should never be called")

    # ex_falso: Empty -> A   (vacuously true; the function body is never reached)
    def ex_falso(empty_value):
        raise AssertionError("ex_falso was called — the empty type was inhabited!?")

    # Python's NoReturn (typing.Never) is the practical Empty type
    from typing import NoReturn

    def always_raises(msg: str) -> NoReturn:
        raise RuntimeError(msg)

    # A function of type (A -> Never) -> A -> B  is "reductio ad absurdum"
    # Given a "proof" that A leads to contradiction, and A, derive anything
    def reductio(neg_a, a):
        return neg_a(a)   # calls neg_a(a) which raises; never returns

    print("Empty type: no constructor exists (test passed if no crash above)")

    # Practical use: type-narrowing in Python
    def exhaustive(x: int | str) -> str:
        if isinstance(x, int):   return f"number: {x}"
        if isinstance(x, str):   return f"string: {x}"
        always_raises(f"unreachable: {x!r}")   # proves: no other type exists

    print(exhaustive(42))
    print(exhaustive("hi"))

except Exception as e:
    if "no constructor" not in str(e):   # suppress the expected test message
        print(f"[ch:empty] {e}")
        import traceback; traceback.print_exc()

print("Empty type: no constructor exists (test passed if no crash above)")
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

---

## Model 3: Negation and Absurdity

### Critical Thinking Questions

9. Rust's `!` (the Never type) is used as the return type of `panic!()`, `return`, and infinite loops. What logical proposition does a function that returns `!` prove? Why does this make sense — what does it mean for a function to prove an unprovable proposition?

10. In Python, `assert False` raises an `AssertionError`. In a dependently-typed language, the compiler would reject code that reaches an `assert False` that can't be ruled out statically. What kind of bugs would this catch that Python's runtime `assert` misses?

11. The `exhaustive` function above calls `always_raises` on a branch that should be unreachable. This is the programmatic counterpart of "we have exhaustively handled all cases, so nothing else can occur." In what way is this the *proof* that `int | str` has no third case? What happens in Haskell/Rust if you forget the `always_raises` equivalent?

---

# Part IV: Dependent Types — A Glimpse

## 5. Types That Depend on Values

**Intuition.** Everything so far has kept types and values in separate worlds: types exist at compile time, values at run time. Dependent types erase that wall. A type like `Vec 3 Int` — "a list of exactly three integers" — mentions the *value* `3` inside the type itself. A function that returns a `Vec n Bool` for any `n` is simultaneously a program and a proof of the logical statement "for every natural number n, there exists a boolean list of length n." The type checker verifying your code is a theorem prover checking your proof. This is why Coq, Lean, and Agda are simultaneously proof assistants and programming languages — they are the same thing.

Standard type systems separate types (compile-time) from values (run-time). **Dependent types** erase that boundary: types can *depend on* values, and propositions about specific values become types. This is the basis of proof assistants like Coq, Lean, and Agda.

Examples:
- `Vec n A` — a list of exactly `n` elements of type `A`; `n` is a value in the type
- `f : (n: Nat) -> Vec n Bool` — a function that returns a list whose length is *provably* equal to `n`
- `Proof (x < y)` — a type that is inhabited only when `x < y` is true

Writing a well-typed term in a dependent language IS writing a proof. The type checker verifies your proof. This is why Coq is both a proof assistant and a programming language.

---

## Code Cell: Simulating Dependent Types in Python

```python
try:
    # Python cannot express dependent types natively, but we can simulate
    # by encoding the "proof" as a runtime check that mypy can partially verify.

    from typing import Generic, TypeVar, Literal
    N = TypeVar('N')

    class Vec:
        def __init__(self, items: list):
            self.items = items
            self.length = len(items)

        def safe_head(self):
            if self.length == 0:
                raise ValueError("head of empty Vec — proof failed: length > 0 required")
            return self.items[0]

        def append(self, x) -> 'Vec':
            return Vec(self.items + [x])

        def __repr__(self): return f"Vec{self.items}"

    # replicate: (n: int) -> A -> Vec (proof: result has exactly n elements)
    def replicate(n: int, x) -> Vec:
        assert n >= 0, "n must be non-negative"
        v = Vec(replicate(n - 1, x).items + [x]) if n > 0 else Vec([])
        assert v.length == n, f"replicate invariant broken: got {v.length}, expected {n}"
        return v

    v = replicate(5, 0)
    print(v, "length:", v.length)
    print("head:", v.safe_head())

    empty = Vec([])
    try:
        empty.safe_head()
    except ValueError as e:
        print("caught:", e)   # the "proof obligation" was violated

except Exception as e:
    print(f"[ch:deptype] {e}")
    import traceback; traceback.print_exc()
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

---

## Model 4: Dependent Types

[[MC]]
In a dependently-typed language, `Vec 3 Int` and `Vec 4 Int` are **different types**. What does this mean for a function `head : Vec n A -> A` (which returns the first element)?
- ( ) The function can be called on any list; the length is ignored
- ( ) The compiler cannot type-check such a function; dependent types are undecidable
- (x) The function's type guarantees it is only called on non-empty lists: n must be > 0, which is enforced at the type level
- ( ) The function must be defined separately for each possible length

### Critical Thinking Questions

12. In the Vec simulation above, the length invariant is checked at runtime with `assert`. In a real dependent type system, this check would happen at *compile time*. What class of runtime errors would disappear if Python had dependent types? Give two concrete examples from bugs you have seen or written.

13. The proposition `∀n. Vec n Bool` (for all n, there is a Vec of booleans of length n) corresponds to a function `(n: Nat) -> Vec n Bool`. The replicate function above proves this proposition. Translate the proof into English: "For any natural number n, we can construct a boolean list of exactly that length by..."

14. Rust's type system tracks ownership and lifetimes — in a sense, it includes a limited form of dependent types over time and ownership. The borrow checker rejects code that would cause use-after-free. What logical proposition does the borrow checker *prove* about memory safety?

---

# Part V: The Curry-Howard Table Completed

## 6. Synthesis

**Intuition.** You have now seen every row of the Curry-Howard table in action. The pattern is always the same: a logical rule for *introducing* a proposition corresponds to a constructor or function that *builds* a value of the corresponding type; a logical rule for *eliminating* a proposition corresponds to pattern matching or function application that *uses* that value. The table below is your complete reference.

> **Watch out!** The Curry-Howard correspondence is exact for *intuitionistic* (constructive) logic, not classical logic. Classical logic includes the law of excluded middle (`P ∨ ¬P`) and double-negation elimination (`¬¬P → P`). These correspond to continuations and control operators — not ordinary functions. If you find yourself trying to write a function of type `Either P (P -> Never)` in pure functional code and getting stuck, that is not a bug — it reflects a genuine distinction between constructive and classical mathematics.

Return to the table from Part I. By now you should be able to fill in the programming column for every logic row:

| Logic | Programming |
|---|---|
| Proposition $P$ | A type |
| Proof of $P$ | A value / term |
| $P \Rightarrow Q$ | A function `P -> Q` |
| $P \wedge Q$ | A product type `(P, Q)` |
| $P \vee Q$ | A sum type `Left P \| Right Q` |
| $\bot$ | The empty / Never type |
| $\neg P = P \Rightarrow \bot$ | `P -> Never` |
| Tautology | A type that is always inhabited |
| Contradiction | A type that is never inhabited |
| $\forall x: A.\ P(x)$ | A dependent function type |
| $\exists x: A.\ P(x)$ | A dependent pair type |

---

## Code Cell: The Full Dictionary in Python

```python
try:
    # The entire Curry-Howard dictionary illustrated in one cell

    # Implication A => B: a function
    def implies(a_proof):     # given proof of A, produce proof of B
        return a_proof        # (identity: A => A)

    # Conjunction A ∧ B: a pair
    and_proof = ("proof_of_A", "proof_of_B")
    fst_proof = and_proof[0]  # extract proof of A

    # Disjunction A ∨ B: tagged union
    or_proof = ("Left", "proof_of_A")   # one-of
    match or_proof:
        case ("Left", p):   result = f"case A: {p}"
        case ("Right", p):  result = f"case B: {p}"
    print(result)

    # Negation ¬A = A -> Never
    def not_a(proof_of_a):
        raise RuntimeError(f"contradiction: A was provable ({proof_of_a}) but ¬A was assumed")

    # Modus ponens: (A => B) and A, therefore B
    def modus_ponens(implication, proof_of_a):
        return implication(proof_of_a)

    result = modus_ponens(lambda x: x * 2, 21)
    print("modus ponens:", result)

    # Hypothetical syllogism (transitivity): (A => B) and (B => C) => (A => C)
    def hyp_syll(f, g):
        return lambda a: g(f(a))

    double = lambda x: x * 2
    add_ten = lambda x: x + 10
    double_then_add = hyp_syll(double, add_ten)
    print("hypothetical syllogism:", double_then_add(5))  # (5*2)+10 = 20

except Exception as e:
    print(f"[ch:dict] {e}")
    import traceback; traceback.print_exc()
```
@LIA.eval(`["main.py"]`, `python3 main.py`, ``)

---

## Exercises

1. **Prove De Morgan's Laws as functions.** De Morgan: `¬(P ∨ Q) ↔ ¬P ∧ ¬Q`. Write Python functions:
   - `demorgan_fwd : (P | Q -> Never) -> (P -> Never, Q -> Never)`
   - `demorgan_rev : (P -> Never, Q -> Never) -> (P | Q -> Never)`
   Hint: both proofs construct functions that raise.

2. **Type your Mini AST nodes.** Each AST node type in your Mini interpreter is a type. Map the Mini expression grammar to Curry-Howard: `BinOp(op, l, r)` — what conjunction does it correspond to? `IfStmt(cond, then, els)` — why is this a product of the condition's "proof" and two continuations? Write one sentence per node type.

3. **Prove `(A → B) → (B → C) → A → C` three ways.** Write the function body in Python, in lambda calculus notation (from the lambda calculus activity), and in English as a logical proof. Confirm all three say the same thing.

4. **Read a Lean proof.** The Lean 4 proof assistant uses the same Curry-Howard correspondence. Translate this Lean snippet to Python by reading it as code:
   ```lean
   theorem and_comm : P ∧ Q → Q ∧ P :=
     fun ⟨hp, hq⟩ => ⟨hq, hp⟩
   ```
   What Python function does this correspond to? (Hint: `⟨hp, hq⟩` is pattern-matching on a pair.)

---

## Reflection Prompt

In your notebook: the Curry-Howard correspondence says that every program you write is secretly a proof of a proposition — its type. When you write a bug-free program, you have proved a theorem (albeit a trivial one). When a type-checker rejects your code, it is saying your proof is incomplete. Does this reframing change how you think about type errors? And: in a language with no type system (Python in dynamic mode, untyped Scheme), what is missing from the "proof" side of the correspondence?

---

## Further Reading

- Howard, William A. "The Formulae-as-Types Notion of Construction" (1980; circulated 1969). The original paper — short and readable. The footnotes alone are worth the read.
- Wadler, Philip. "Propositions as Types" (2015). *Communications of the ACM*. A modern, beautifully written survey that also covers the history; this is the best first read.
- Pierce, Benjamin C. *Types and Programming Languages* (MIT Press, 2002), Chapters 9–11. The rigorous treatment.
- Lean 4 natural number game: https://adam.math.hhu.de/ — prove theorems *as* programs in your browser, fully interactively.
- Coq: https://coq.inria.fr/ — the proof assistant that verified the four-color theorem and the CompCert C compiler.
- Harper, Robert. *Practical Foundations of Mathematics* (online). Chapter on the computational interpretation of logic.
