---
layout: textbook
permalink: /Tutorials/CForFlexAndBison
title: "CS374: C for Flex and Bison"

info:
  coursenum: CS374
  eyebrow: "Tutorial"
  numbering: false
  objectives:
    - "Read and write a struct, a pointer to a struct, and a linked list in C"
    - "Keep your own copy of a string, and compare two strings"
    - "Read an enum, a switch, and a table of function pointers"
    - "Write a small Makefile, and read the errors gcc and the linker report"

tags:
  - c
  - flex
  - bison
  - reference

---
# Tutorial: C for Flex and Bison

Flex and Bison generate C, so the code you write in their actions is C too.  If your background is Python or Java, most of it will look familiar, and only a few things are new: memory is yours to manage, a string is a pointer, and `->` is everywhere.  Everything below compiles with `gcc`, so type it in and run it.

## Structs and Pointers

A `struct` is a record with named fields, like a Python class with only data.  C has no objects on the heap unless you ask for one.  `malloc` asks for memory and returns a *pointer*, which is the address of that memory.  You read a field through a pointer with `->`, so `e->name` means "the `name` field of the struct that `e` points to."  `NULL` is the pointer that points to nothing, and it plays the role of Python's `None`.

## A Linked List of Records

A phone book is a good first list.  Each entry points to the next one, and the last entry's `next` is `NULL`.  Save this as `phone.c`:

<!-- run: id=cs374-tutorial-c-for-flex-bison-1 viz=c -->
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

typedef struct Entry {
    char *name;
    int extension;
    struct Entry *next;
} Entry;

static Entry *book = NULL;

/* Walk the list.  Return the matching entry, or NULL if there is none. */
static Entry *find(const char *name) {
    for (Entry *e = book; e != NULL; e = e->next) {
        if (strcmp(e->name, name) == 0) {
            return e;
        }
    }
    return NULL;
}

/* Make a new entry, and put it at the front of the list. */
static void add(const char *name, int extension) {
    Entry *e = malloc(sizeof(Entry));
    e->name = strdup(name);
    e->extension = extension;
    e->next = book;
    book = e;
}

int main(void) {
    add("registrar", 3000);
    add("library", 3605);
    Entry *hit = find("registrar");
    if (hit != NULL) {
        printf("%s: %d\n", hit->name, hit->extension);
    }
    printf("found bursar? %s\n", find("bursar") ? "yes" : "no");
    return 0;
}
```
[Visualize this example](https://billjr99.github.io/Ursinus-CS374-Fall2026/viz/#cs374-tutorial-c-for-flex-bison-1) <!-- code-viz link -->

```bash
gcc -Wall -o phone phone.c
./phone
```

> **You should see.**
>
> ```text
> registrar: 3000
> found bursar? no
> ```

Three lines in it are worth reading slowly.

- `for (Entry *e = book; e != NULL; e = e->next)` is how you walk any linked list in C.  It starts at the front, stops at the end, and steps along the `next` links.
- `e->next = book; book = e;` puts the new entry at the front.  Adding to the front takes the same work no matter how long the list is, which is why we do not walk to the end.
- `add` calls `strdup`, because a `char *` is only an address.  If you stored the pointer you were handed, and whoever owns that memory reused it, your entry's name would change underneath you.  Flex does exactly that with `yytext`: it reuses the buffer for the next token.  So keep your own copy.

## Comparing Strings

`==` on two strings compares their addresses, not their letters, so it is almost never what you want.  `strcmp(a, b)` compares the letters, and it returns `0` when they match.  That is why the test reads `strcmp(e->name, name) == 0`.  You get `strcmp` and `strdup` from `#include <string.h>`, and `malloc` from `#include <stdlib.h>`.

## Enums, Switch, and a Table of Functions

Interpreters keep one kind of record that can hold several kinds of value.  An `enum` names the kinds, a field records which kind this one is, and a `switch` does the right thing for each.  A *function pointer* is a variable that holds a function, so a table can list functions by name, which is how you add a new operation without touching the code that uses the table.  Save this as `shape.c`:

<!-- run: id=cs374-tutorial-c-for-flex-bison-2 viz=c -->
```c
#include <stdio.h>
#include <string.h>

typedef enum { CIRCLE, SQUARE } Kind;

typedef struct {
    Kind kind;
    double size;
} Shape;

static double area(Shape s) {
    switch (s.kind) {
        case CIRCLE: return 3.14159 * s.size * s.size;
        case SQUARE: return s.size * s.size;
    }
    return 0;
}

static double twice(double x) { return 2 * x; }
static double square(double x) { return x * x; }

static struct {
    const char *name;
    double (*function)(double);
} TABLE[] = {
    { "twice",  twice },
    { "square", square },
};

int main(void) {
    Shape s = { SQUARE, 3 };
    printf("area: %g\n", area(s));
    for (int i = 0; i < 2; i++) {
        if (strcmp(TABLE[i].name, "square") == 0) {
            printf("%s(5) = %g\n", TABLE[i].name, TABLE[i].function(5));
        }
    }
    return 0;
}
```
[Visualize this example](https://billjr99.github.io/Ursinus-CS374-Fall2026/viz/#cs374-tutorial-c-for-flex-bison-2) <!-- code-viz link -->

```bash
gcc -Wall -o shape shape.c
./shape
```

> **You should see.**
>
> ```text
> area: 9
> square(5) = 25
> ```

`double (*function)(double)` reads from the inside out: `function` is a pointer to a function that takes a `double` and returns a `double`.  `TABLE[i].function(5)` calls whichever function that row holds.  Adding an operation is one new function and one new row.

`static` in front of a function or a variable at the top of a file means that only this file can see it, so two files can each have their own private helper with the same name.

## Make

A Makefile says what to build, what it depends on, and how to build it.  Each rule is a target, a colon, its dependencies, and then the commands, each indented with a **tab**, not spaces.

```make
phone: phone.c
	gcc -o phone phone.c

clean:
	rm -f phone
```

`make` builds the first target, and it runs the command only if `phone.c` is newer than `phone`.  Run it twice, and the second time it says `'phone' is up to date`.  `make clean` deletes what was built.  If Make reports `missing separator`, you indented with spaces.

## Reading the Errors

| What you see | What it usually means |
|---|---|
| `implicit declaration of function 'strdup'` | You forgot the `#include` for it, here `<string.h>` |
| `undefined reference to 'foo'` | The compiler was happy, but no file you linked defines `foo`.  Check the `gcc` line, or run `make clean` and then `make` |
| `dereferencing pointer to incomplete type` or `has no member named` | The struct's definition is not visible here, or a field name is misspelled |
| `Segmentation fault` | Usually `->` on a `NULL` pointer, so check what your walk returned before you use it |

The [Flex and Bison tutorial]({{ site.baseurl }}/Tutorials/FlexAndBison) shows how this C goes inside `.l` and `.y` files, and [Compiling and Linking]({{ site.baseurl }}/Tutorials/CompilingAndLinking) explains what `gcc` does in each stage.
