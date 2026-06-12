# Names, Binding, and Scope
<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://github.com/BillJr99/Ursinus-CS374-Fall2026/blob/gh-pages/_pages/Activities/liascript-bindingscope.md or locally via https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374/gh-pages/_pages/Activities/liascript-bindingscope.md

import: https://raw.githubusercontent.com/liascript/CodeRunner/master/README.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

# Names, Binding, and Scope

Your interpreter currently stores every variable in one flat dictionary, and that simplicity is about to fail you: what happens when two parts of a program use the same name? Today we develop the vocabulary of **binding** (attaching a name to a meaning) and **scope** (where that attachment is visible), the semantics decisions at the heart of your interpreter assignment. The arc: **binding times $\rightarrow$ static versus dynamic scope $\rightarrow$ lifetime $\rightarrow$ design decisions for your language**.

---

## Directions and Group Roles

Work in your POGIL team with rotated roles (**Manager**, **Recorder**, **Presenter**, **Reflector**). Consider each model and question individually first, then discuss with your group. The Recorder posts answers to the Class Activity Questions discussion board; the Presenter reports out areas of disagreement or alternative approaches. After class, respond to the reflective prompt individually in your notebook.

---

# Part I: Binding

## 1. When Does a Name Get Its Meaning?

**A binding is an association between a name and an attribute** (a value, a type, a memory location), and the central question is *when* it happens. The classical **binding times**, from earliest to latest: language design time (`+` means addition), compile time (a static type), load or startup time (a global's address), and run time (a variable's current value). Earlier binding buys efficiency and checkability; later binding buys flexibility. A language is, in large part, a schedule of binding times.

**Declarations create bindings; scope rules govern their reach.** In `let x = 5;`, the declaration binds `x`; every later mention of `x` is a *use* that must be **resolved** to some binding. When the same name is declared in nested regions, the inner declaration **shadows** the outer: both bindings exist, but the inner one wins within its region.

---

## Model 1: Binding Time Sort

| Fact | Bound when? |
|------|-------------|
| The meaning of the `*` symbol in your language | ? |
| The type of `count` in Java's `int count;` | ? |
| The type of `count` in Python after `count = 3` | ? |
| The value of `count` during a loop | ? |

### Critical Thinking Questions

1. Complete the table, justifying each answer in a clause.
2. Java binds `count`'s type earlier than Python does. Restate the static-versus-dynamic-typing debate from the language evaluation module as a *binding time* decision: what is bought and what is paid at each time?
3. Your project language must decide: may a variable be assigned a number and later a string? State your team's provisional answer and the binding-time language for it.

---

# Part II: Scope

## 2. Where Does a Binding Reach?

**Static (lexical) scope: resolve names by the program's text.** A use of `x` refers to the declaration in the innermost *textually enclosing* region. The resolution can be done by reading the code, without running it, which is why it is called static, and it is the choice of essentially every modern language.

**Dynamic scope: resolve names by the call history.** A use of `x` refers to the most recent declaration *in the chain of active calls*, whatever code that was. Early Lisps worked this way; the behavior is occasionally convenient and chronically surprising, because a function's meaning depends on who called it.

Consider this program in a language with functions:

```
let x = 10;

function show() { print x; }

function demo() {
    let x = 99;
    show();
}

demo();
```

**Static scope prints 10** (`show`'s `x` resolves to the global, its textual surroundings); **dynamic scope prints 99** (`show`'s `x` resolves to `demo`'s, the most recent on the call chain).

---

## Model 2: Be Both Resolvers

### Critical Thinking Questions

4. Trace the program under each rule, writing the chain each resolver follows (textual nesting versus call stack). Confirm the 10 versus 99 split.
5. Argue each side in one sentence: what is genuinely convenient about dynamic scope (think: configuration that functions silently inherit), and what makes it hard to read (think: can you tell what `show` prints by reading `show`?).
6. Which rule lets a compiler resolve every name before the program runs? Connect to the binding-time framework.
7. Python is statically scoped. Predict, then verify in the code cell, what the analogous Python program prints.

---

## Code Cell

```python
# Static scope in action: Python resolves print(x) inside show() textually.

x = 10

def show():
    try:
        print("show sees x =", x)       # resolves to the GLOBAL x: textual nesting
    except Exception as e:
        print(f"[bindingscope:show] {e}")
        import traceback; traceback.print_exc()

def demo():
    x = 99                              # a NEW binding, shadowing locally
    show()                              # does NOT affect what show sees

demo()
print("after demo, global x =", x)

# Shadowing in nested regions:
def outer():
    y = "outer"
    def inner():
        y = "inner"                     # shadows outer's y inside inner only
        return y
    return inner(), y

print(outer())                          # ('inner', 'outer')
```

---

[[MC]]
Under static scoping, the binding that a variable use refers to can be determined:
- ( ) Only by running the program and inspecting the call stack
- (x) By reading the program text and finding the innermost enclosing declaration
- ( ) By checking which function was called most recently
- ( ) By the order of declarations in the global region only

---

# Part III: Lifetime, and Your Language

## 3. Scope Is Space; Lifetime Is Time

**Scope is the region of *text* where a binding is visible; lifetime is the span of *execution* during which its storage exists.** The two usually align (a local lives while its block runs) but can diverge: a C `static` local has tiny scope and program-long lifetime, and, the divergence that matters most for your project, a **closure** (a coming module) keeps a binding *alive* after its scope has ended. Your interpreter assignment implements blocks that create and discard scopes; the environments module gives you the data structure.

## 4. Exercises

1. *Scope archaeology.* Run a three-level nested function experiment in Python (global, enclosing, local all binding `v`) and report which binding each level's print resolves to. Then state Python's resolution order (the LEGB rule) in your own words.
2. *Design memo.* Write your project language's scoping rules in five sentences or fewer: static or dynamic; do blocks create scopes; is shadowing legal; what happens on use of an undeclared name; do loop bodies create a scope. Add it to `SEMANTICS.md`.
3. *Bug forensics.* Construct a program (any language) where shadowing causes a quiet wrong answer rather than an error. Propose one language rule that would have caught it, and what that rule costs.

---

## Reflection Prompt

In your notebook: shadowing lets inner code reuse a name without consulting outer code, which is both modularity and a trap. When you reuse a word with a private meaning in your own notes or conversation, what keeps you from confusing yourself, and is there a language-design lesson in your answer?

---

## 5. Further Reading

- Douglas Thain. *Introduction to Compilers and Language Design*, Chapter 7.
- Robert Nystrom. *Crafting Interpreters*, "Statements and State" (online).
- Robert Sebesta. *Concepts of Programming Languages*, the names/binding/scope chapter (any edition).
