---
layout: tutorial
permalink: /Tutorials/AdvancedCpp
title: "CS374: Advanced C++: Modern Memory, Templates, and the STL"

info:
  coursenum: CS374
  goals:
    - "Identified and fixed the three classic memory bugs (double-free, use-after-free, memory leak) using `valgrind` or AddressSanitizer"
    - "Replaced raw-pointer ownership patterns with `std::unique_ptr` and `std::shared_ptr` and explained when each is appropriate"
    - "Written at least one function and one class template, including a template specialization"
    - "Used STL containers (`vector`, `map`, `unordered_map`) and algorithms (`sort`, `find_if`, `transform`) with lambda expressions"
    - "Explained how type erasure in `std::function` achieves runtime polymorphism without virtual dispatch"

tags:
  - cpp
  - project-extension

---
# Advanced C++: Modern Memory, Templates, and the STL

## Learning Goals

By the end of this tutorial, you will have:

- Identified and fixed the three classic memory bugs (double-free, use-after-free, memory leak) using `valgrind` or AddressSanitizer
- Replaced raw-pointer ownership patterns with `std::unique_ptr` and `std::shared_ptr` and explained when each is appropriate
- Written at least one function and one class template, including a template specialization
- Used STL containers (`vector`, `map`, `unordered_map`) and algorithms (`sort`, `find_if`, `transform`) with lambda expressions
- Explained how type erasure in `std::function` achieves runtime polymorphism without virtual dispatch

> **Prerequisites:** C++ fundamentals, basic pointers, classes/structs
> **Goal:** Master modern C++ memory management, generic programming, the STL, and how C++ achieves zero-cost abstractions through templates and type erasure.

---

## Part 1: Raw Pointers and the Three Classic Bugs

### Model 1.1: Stack vs Heap Allocation

C++ gives the programmer explicit control over where memory lives.  Stack memory is managed automatically (LIFO cleanup when scope exits).  Heap memory is managed manually via `new` and `delete`.

```cpp
#include <iostream>
#include <cstring>

void stack_vs_heap() {
    // --- Stack allocation ---
    int x = 42;            // lives until end of stack frame
    int arr[8] = {};       // fixed-size array on the stack

    // --- Heap allocation (scalar) ---
    int* p = new int(99);  // allocate one int on the heap
    std::cout << "heap int: " << *p << "\n";
    delete p;              // must free manually
    p = nullptr;           // best practice: null out after delete

    // --- Heap allocation (array) ---
    int* buf = new int[1024];
    std::memset(buf, 0, 1024 * sizeof(int));
    buf[0] = 7;
    std::cout << "buf[0]: " << buf[0] << "\n";
    delete[] buf;          // array form requires delete[]
}

int main() { stack_vs_heap(); }
```

Stack frames are automatically popped when a function returns; no `delete` needed.  Heap allocations persist until you explicitly `delete` them.  Forgetting, double-deleting, or accessing freed memory are the three canonical bugs.

---

### Model 1.2: Bug 1: Double Free

```cpp
#include <iostream>

void double_free_demo() {
    int* p = new int(10);
    delete p;    // first delete - OK, memory returned to OS/allocator
    delete p;    // second delete - UNDEFINED BEHAVIOUR
                 // runtime may crash, corrupt allocator metadata,
                 // or silently do nothing depending on platform
}
```

**Typical AddressSanitizer output:**

```
==12345==ERROR: AddressSanitizer: heap-use-after-free on address 0x602000000010
WRITE of size 8 at 0x602000000010 thread T0
    #0 0x... in double_free_demo() demo.cpp:6
    #1 0x... in main demo.cpp:9
0x602000000010 is located 0 bytes inside of 8-byte region [0x602000000010,0x602000000018)
freed by thread T0 here:
    #0 0x... in operator delete(void*)
    #1 0x... in double_free_demo() demo.cpp:5
```

The allocator's bookkeeping structures (size, free-list links) live adjacent to heap blocks.  A double-free corrupts them, enabling heap exploitation primitives used in real-world CVEs.

---

### Model 1.3: Bug 2: Use After Free

```cpp
#include <iostream>
#include <string>

struct Node {
    int val;
    Node* next;
};

void use_after_free_demo() {
    Node* n = new Node{42, nullptr};
    Node* alias = n;   // alias points to the same block

    delete n;          // memory returned to allocator
    n = nullptr;       // n is safely nulled...

    // But alias still points to the freed block!
    std::cout << alias->val << "\n";  // UB: reads freed memory
    // The freed block may now hold allocator metadata or a new object.
    // Output might be 42, 0, garbage, or a crash.
}
```

**Typical Valgrind output:**

```
==9876== Invalid read of size 4
==9876==    at 0x10890A: use_after_free_demo() (demo.cpp:17)
==9876==  Address 0x5204e80 is 0 bytes inside a block of size 8 free'd
==9876==    at 0x4C2FB0F: operator delete(void*) (vg_replace_malloc.c:585)
==9876==    at 0x108904: use_after_free_demo() (demo.cpp:13)
==9876==  Block was alloc'd at
==9876==    at 0x4C2FB0F: operator new(unsigned long) (vg_replace_malloc.c:342)
==9876==    at 0x1088E5: use_after_free_demo() (demo.cpp:10)
```

---

### Model 1.4: Bug 3: Memory Leak

```cpp
#include <iostream>
#include <vector>

// Leaks every time called - allocation escapes without deletion
std::vector<int>* make_data(int n) {
    auto* v = new std::vector<int>(n, 0);  // heap-allocated vector
    for (int i = 0; i < n; ++i) (*v)[i] = i * i;
    return v;
    // Caller is responsible for delete - but many callers forget!
}

void leak_demo() {
    auto* data = make_data(1000);
    std::cout << "data[5] = " << (*data)[5] << "\n";
    // Forgot: delete data;
    // 1000 * sizeof(int) + sizeof(vector) bytes are now permanently leaked.
}
```

**Valgrind memory leak summary:**

```
==4321== LEAK SUMMARY:
==4321==    definitely lost: 4,024 bytes in 1 blocks
==4321==    indirectly lost: 0 bytes in 0 blocks
==4321==      possibly lost: 0 bytes in 0 blocks
==4321==    still reachable: 72,704 bytes in 1 blocks
==4321==         suppressed: 0 bytes in 0 blocks
==4321== Rerun with --leak-check=full to see details of leaked memory
```

**Running Valgrind** (for reference, run these in a real terminal):

```bash
g++ -g -O0 demo.cpp -o demo
valgrind --leak-check=full --track-origins=yes ./demo
# For AddressSanitizer (faster, catches more):
g++ -g -fsanitize=address,undefined demo.cpp -o demo_asan && ./demo_asan
```

---

### Critical Thinking Questions, Part 1

1.  **Bug identification.**  For each snippet, identify the bug category (double free, use after free, or memory leak) and explain *why* it is undefined behaviour at the C++ specification level:

   a.
   ```cpp
   char* buf = new char[256];
   strcpy(buf, "hello");
   delete buf;   // note: not delete[]
   ```

   b.
   ```cpp
   int* f() {
       int local = 99;
       return &local;  // pointer to stack variable
   }
   int* p = f();
   std::cout << *p;  // called after f() returned
   ```

   c.
   ```cpp
   Widget* w = new Widget();
   cache.store(w);   // cache holds a copy of the pointer
   delete w;
   // ... later ...
   cache.get()->draw();
   ```

2.  **Why does nulling a pointer after delete (`p = nullptr`) prevent a double-free bug but not a use-after-free via an alias?**  Sketch the memory diagram showing `p`, `alias`, and the heap block after `delete p; p = nullptr;`.

3.  **Valgrind vs ASan.**  Valgrind instruments every memory access at runtime.  AddressSanitizer (`-fsanitize=address`) adds shadow memory at compile time.  Which detects more bugs?  Which has lower overhead?  Look up "redzones" in the ASan documentation and explain in one sentence what they add beyond Valgrind's capabilities.

---

## Part 2: Smart Pointers and RAII

### Model 2.1: RAII: The Core Principle

**Resource Acquisition Is Initialization (RAII):** tie a resource's lifetime to an object's lifetime.  The constructor acquires; the destructor releases.  Since C++ guarantees destructors run when objects go out of scope (even through exceptions), RAII makes resource leaks nearly impossible.

```cpp
#include <fstream>
#include <stdexcept>

void write_log(const std::string& msg) {
    std::ofstream f("app.log", std::ios::app);  // constructor opens file
    if (!f) throw std::runtime_error("cannot open log");
    f << msg << "\n";
    // destructor closes file - even if an exception is thrown above
}
// Without RAII: if an exception fires between open() and close(),
// the file handle leaks and the buffer may not flush.
```

---

### Model 2.2: `unique_ptr<T>`: Sole Ownership

`unique_ptr` models *exclusive* ownership.  It cannot be copied; only moved.  When it goes out of scope, it calls `delete` automatically.

```cpp
#include <iostream>
#include <memory>
#include <fstream>

struct Widget {
    std::string name;
    Widget(std::string n) : name(std::move(n)) {
        std::cout << "Widget(" << name << ") constructed\n";
    }
    ~Widget() { std::cout << "Widget(" << name << ") destroyed\n"; }
    void draw() const { std::cout << "Drawing " << name << "\n"; }
};

// Custom deleter - for C-style resources (FILE*, SDL_Window*, etc.)
struct FileCloser {
    void operator()(FILE* f) const {
        if (f) { std::fclose(f); std::cout << "File closed\n"; }
    }
};

void unique_ptr_demo() {
    // Prefer make_unique - single allocation, exception-safe
    auto w1 = std::make_unique<Widget>("Button");
    w1->draw();

    // Transfer ownership: w1 becomes null, w2 owns the Widget
    auto w2 = std::move(w1);
    if (!w1) std::cout << "w1 is now null\n";
    w2->draw();

    // unique_ptr with custom deleter (manages non-new resources)
    std::unique_ptr<FILE, FileCloser> fp(std::fopen("/dev/null", "r"));

    // w2 and fp destroyed here - Widget destructor + FileCloser called
}

int main() { unique_ptr_demo(); }
```

Expected output:

```
Widget(Button) constructed
Drawing Button
w1 is now null
Drawing Button
File closed
Widget(Button) destroyed
```

---

### Model 2.3: `shared_ptr<T>` and Reference Counting

`shared_ptr` allows multiple owners.  An internal control block tracks the reference count.  When the count reaches zero, the object is deleted.

```cpp
#include <iostream>
#include <memory>

struct Node {
    int val;
    std::shared_ptr<Node> next;  // Caution: creates ownership cycles!
    Node(int v) : val(v) { std::cout << "Node(" << v << ") +\n"; }
    ~Node() { std::cout << "Node(" << val << ") -\n"; }
};

void shared_ptr_demo() {
    auto a = std::make_shared<Node>(1);  // refcount = 1
    {
        auto b = a;   // refcount = 2
        auto c = a;   // refcount = 3
        std::cout << "use_count inside block: " << a.use_count() << "\n";
    }  // b and c destroyed; refcount drops to 1
    std::cout << "use_count after block: " << a.use_count() << "\n";
}  // a destroyed; refcount = 0 -> Node(1) deleted

// --- Cycle problem: two nodes pointing at each other ---
void cycle_demo() {
    auto x = std::make_shared<Node>(10);
    auto y = std::make_shared<Node>(20);
    x->next = y;  // x keeps y alive
    y->next = x;  // y keeps x alive - CYCLE: neither will ever be deleted!
    // use weak_ptr to break the cycle (see below)
}
```

**Breaking cycles with `weak_ptr`:**

```cpp
#include <memory>
#include <iostream>

struct TreeNode {
    int val;
    std::shared_ptr<TreeNode> left, right;
    std::weak_ptr<TreeNode> parent;  // weak_ptr: does NOT increment refcount
    TreeNode(int v) : val(v) {}
};

void weak_ptr_demo() {
    auto root  = std::make_shared<TreeNode>(1);
    auto left  = std::make_shared<TreeNode>(2);
    auto right = std::make_shared<TreeNode>(3);

    root->left  = left;
    root->right = right;
    left->parent  = root;  // weak_ptr: no cycle
    right->parent = root;

    // Promote weak_ptr to shared_ptr to use it
    if (auto p = left->parent.lock()) {
        std::cout << "parent of 2 is " << p->val << "\n";
    }
    // root, left, right all cleanly destroyed - no leak
}
```

---

### Python Interlude, Simulating Reference Counting

The following Python program simulates a reference-counting system similar to what `shared_ptr` does internally.  Run it to see how refcounts change as references are added and removed.

```python
try:
    import sys

    class RCObject:
        """Simulates a C++ shared_ptr control block."""
        _registry = {}  # id -> {'obj': obj, 'refcount': n}

        def __init__(self, value):
            self.value = value
            self._id = id(self)
            RCObject._registry[self._id] = {'obj': self, 'refcount': 1}
            print(f"  [alloc] object({value}) created, refcount=1")

        def addref(self):
            RCObject._registry[self._id]['refcount'] += 1
            rc = RCObject._registry[self._id]['refcount']
            print(f"  [addref] object({self.value}) refcount={rc}")

        def release(self):
            rc = RCObject._registry[self._id]['refcount'] - 1
            RCObject._registry[self._id]['refcount'] = rc
            print(f"  [release] object({self.value}) refcount={rc}")
            if rc == 0:
                print(f"  [destroy] object({self.value}) freed!")
                del RCObject._registry[self._id]

    # Simulate shared_ptr semantics
    print("=== shared_ptr simulation ===")
    obj = RCObject(42)            # make_shared<int>(42)

    ref1 = obj; obj.addref()      # shared_ptr copy: ref1 = ptr
    ref2 = obj; obj.addref()      # shared_ptr copy: ref2 = ptr
    print(f"  [status] refcount={RCObject._registry[obj._id]['refcount']}")

    obj.release()                 # original ptr goes out of scope
    ref1.release()                # ref1 goes out of scope
    ref2.release()                # ref2 goes out of scope -> freed

    print()
    print("=== Python's own refcount (sys.getrefcount adds 1 for the call arg) ===")
    s = "hello world"
    print(f"  sys.getrefcount('hello world') = {sys.getrefcount(s)}")
    s2 = s
    print(f"  after alias s2=s: getrefcount = {sys.getrefcount(s)}")
    del s2
    print(f"  after del s2:     getrefcount = {sys.getrefcount(s)}")

except Exception as e:
    print(f"[rc-demo] {e}")
    import traceback; traceback.print_exc()
```

---

### Critical Thinking Questions, Part 2

1.  **Ownership transfer.**  Why does `unique_ptr` delete its copy constructor and copy assignment operator?  What would happen if two `unique_ptr`s pointed to the same raw pointer and both called `delete` in their destructors?

2.  **Control block layout.**  A `shared_ptr<T>` holds two pointers internally: one to `T` and one to a *control block*.  The control block stores the strong refcount, a weak refcount, and the deleter. `make_shared<T>(args...)` performs a *single* allocation for both `T` and the control block. `shared_ptr<T>(new T(args...))` performs two allocations.  Explain one advantage and one disadvantage of the single-allocation form.

3.  **Weak pointer validity.**  Given the following code, will `wp.lock()` return a valid pointer or an empty pointer?  Explain:
   ```cpp
   std::weak_ptr<int> wp;
   {
       auto sp = std::make_shared<int>(7);
       wp = sp;
   }
   auto p = wp.lock();
   ```

4.  **RAII and exceptions.**  A function creates three resources: a `unique_ptr<A>`, a `unique_ptr<B>`, and a `unique_ptr<C>`.  If the constructor of `C` throws, will `A` and `B` be leaked?  Would the answer change if you used raw `new` instead?

---

### Building and Running These Examples

The C++ snippets above are ordinary programs; each has a `main()`.  To compile and run one yourself, save it (say, the `unique_ptr` demo) as `smartptr.cpp` and drive the build with this `Makefile`:

```makefile
# Makefile - build and run the smart-pointer demo
CXX      := g++
CXXFLAGS := -std=c++17 -Wall -Wextra -g -fsanitize=address
TARGET   := smartptr
SRC      := smartptr.cpp

# Default target: `make` builds the binary
$(TARGET): $(SRC)
	$(CXX) $(CXXFLAGS) -o $(TARGET) $(SRC)

# `make run` builds if needed, then runs
run: $(TARGET)
	./$(TARGET)

# `make clean` removes the built binary
clean:
	rm -f $(TARGET)

.PHONY: run clean
```

Then, from the same directory:

```bash
make         # compiles smartptr.cpp into ./smartptr (the default target)
make run     # compiles if needed, then runs ./smartptr
make clean   # removes the built binary
```

A `Makefile`'s recipe lines must be indented with a **real tab**, not spaces, a classic first-time error.  The `-fsanitize=address` flag links AddressSanitizer, which reports use-after-free, double-free, and leaks at runtime: run `make run` on a raw-pointer (`new`/`delete`) version and on the `unique_ptr` version and compare; the sanitizer stays quiet only when ownership is correct, which is the whole case for smart pointers in one command.

---

## Part 3: Move Semantics and Rvalue References

### Model 3.1: Lvalues and Rvalues

An **lvalue** has an identity: it has a name and an address you can take.  An **rvalue** is a temporary; it will cease to exist at the end of the expression.

```cpp
#include <iostream>
#include <string>

void lvalue_rvalue_demo() {
    int x = 42;          // x is an lvalue; 42 is an rvalue
    int& lr = x;         // lvalue reference - binds to lvalue
    // int& bad = 42;    // ERROR: cannot bind lvalue ref to rvalue
    int&& rr = 42;       // rvalue reference - binds to rvalue
    int&& rr2 = x + 1;   // x+1 is a temporary -> rvalue reference OK

    std::string s = "hello";
    std::string&& rs = s + " world"; // s + " world" is a temporary
    std::cout << rs << "\n";  // "hello world"

    // std::move is a CAST - it does NOT move anything.
    // It converts an lvalue into an rvalue reference,
    // giving permission for move semantics to trigger.
    std::string t = std::move(s);  // s's contents "moved" into t
    std::cout << "t=" << t << "  s='" << s << "'\n";
    // s is now in a valid but unspecified state (typically empty)
}
```

---

### Model 3.2: Copy vs Move Constructor

```cpp
#include <iostream>
#include <algorithm>

class Buffer {
public:
    size_t  size;
    int*    data;

    // Constructor
    explicit Buffer(size_t n) : size(n), data(new int[n]()) {
        std::cout << "Buffer(" << n << ") constructed\n";
    }

    // Destructor
    ~Buffer() { delete[] data; std::cout << "Buffer destroyed\n"; }

    // Copy constructor - deep copy: O(n) allocation + copy
    Buffer(const Buffer& other) : size(other.size), data(new int[other.size]) {
        std::copy(other.data, other.data + size, data);
        std::cout << "Buffer copy-constructed (deep copy, " << size << " ints)\n";
    }

    // Move constructor - steal resources: O(1) pointer swap
    Buffer(Buffer&& other) noexcept
        : size(other.size), data(other.data)
    {
        other.size = 0;
        other.data = nullptr;  // leave source in valid empty state
        std::cout << "Buffer move-constructed (O(1) pointer steal)\n";
    }

    // Copy assignment
    Buffer& operator=(const Buffer& other) {
        if (this == &other) return *this;
        delete[] data;
        size = other.size;
        data = new int[size];
        std::copy(other.data, other.data + size, data);
        std::cout << "Buffer copy-assigned\n";
        return *this;
    }

    // Move assignment
    Buffer& operator=(Buffer&& other) noexcept {
        if (this == &other) return *this;
        delete[] data;
        size  = other.size;  data  = other.data;
        other.size = 0;      other.data = nullptr;
        std::cout << "Buffer move-assigned\n";
        return *this;
    }
};

Buffer make_buffer(size_t n) {
    Buffer b(n);
    b.data[0] = 99;
    return b;  // NRVO may elide the move; with -fno-elide-constructors it fires
}

int main() {
    Buffer a(4);
    Buffer b = a;              // copy constructor (deep copy)
    Buffer c = std::move(a);   // move constructor (O(1))
    Buffer d = make_buffer(8); // move (or NRVO elision)
}
```

**The Rule of Five:** if you define *any* of destructor / copy-ctor / copy-assign / move-ctor / move-assign, you should define *all five*.  The compiler-generated defaults become incorrect once you manage a raw resource.

---

### Model 3.3: `std::vector` Growth and Moves

```cpp
#include <iostream>
#include <vector>

struct Tracker {
    int id;
    static int next_id;
    Tracker() : id(next_id++) { std::cout << "  Tracker#" << id << " default-ctor\n"; }
    Tracker(const Tracker& o) : id(next_id++) {
        std::cout << "  Tracker#" << id << " copy-ctor from #" << o.id << "\n";
    }
    Tracker(Tracker&& o) noexcept : id(o.id) {
        o.id = -1;
        std::cout << "  Tracker#" << id << " move-ctor\n";
    }
    ~Tracker() { if (id >= 0) std::cout << "  Tracker#" << id << " dtor\n"; }
};
int Tracker::next_id = 0;

int main() {
    std::vector<Tracker> v;
    v.reserve(1);   // capacity=1, no reallocation yet
    std::cout << "--- push_back #0 ---\n";
    v.emplace_back();  // construct in-place, no copy/move
    std::cout << "--- push_back #1 (triggers reallocation) ---\n";
    v.emplace_back();
    // When vector grows: if move-ctor is noexcept, elements are MOVED.
    // If not noexcept, they are COPIED (to maintain exception safety).
    // That's why noexcept on move constructors matters for performance!
}
```

---

### Critical Thinking Questions, Part 3

1.  **Lvalue / rvalue classification.**  For each expression, state whether it is an lvalue or rvalue and why:
   - `x` (where `int x = 5;`)
   - `x + 1`
   - `std::string("temp")`
   - `*ptr` (where `int* ptr = new int(3);`)
   - `std::move(x)`

2.  **`noexcept` and `std::vector`.**  Explain why `std::vector` uses the move constructor only when it is marked `noexcept`.  What guarantee would be violated if the move constructor could throw partway through reallocation?

3.  **`std::move` is a cast.**  The declaration `std::string t = std::move(s);` does not immediately move anything.  Trace exactly what happens: (a) what type does `std::move(s)` return, (b) which constructor of `std::string` is called, and (c) what is the state of `s` afterwards according to the C++ standard?

---

## Part 4: Templates and Generic Programming

### Model 4.1: Function Templates

Templates let you write one algorithm that works for any type satisfying the required interface, without runtime overhead.  The compiler **instantiates** a new concrete function for each unique set of template arguments.

```cpp
#include <iostream>
#include <string>
#include <vector>

// Function template: T is a type parameter
template<typename T>
T max_of(T a, T b) {
    return (a > b) ? a : b;
}

// Template with multiple type parameters
template<typename Container, typename Pred>
auto count_if_manual(const Container& c, Pred p) -> typename Container::size_type {
    typename Container::size_type count = 0;
    for (const auto& x : c) if (p(x)) ++count;
    return count;
}

int main() {
    std::cout << max_of(3, 7) << "\n";          // T=int
    std::cout << max_of(3.14, 2.72) << "\n";    // T=double
    std::cout << max_of(std::string("abc"), std::string("xyz")) << "\n"; // T=string

    std::vector<int> v = {1, 2, 3, 4, 5, 6};
    auto evens = count_if_manual(v, [](int x){ return x % 2 == 0; });
    std::cout << "evens: " << evens << "\n";  // 3
}
```

---

### Model 4.2: Class Templates: Generic `Stack<T>`

```cpp
#include <iostream>
#include <vector>
#include <stdexcept>

template<typename T, typename Container = std::vector<T>>
class Stack {
    Container data_;
public:
    void push(T val)  { data_.push_back(std::move(val)); }
    void pop()        {
        if (empty()) throw std::underflow_error("Stack::pop on empty stack");
        data_.pop_back();
    }
    const T& top() const {
        if (empty()) throw std::underflow_error("Stack::top on empty stack");
        return data_.back();
    }
    bool   empty() const noexcept { return data_.empty(); }
    size_t size()  const noexcept { return data_.size(); }
};

int main() {
    Stack<int> si;
    si.push(1); si.push(2); si.push(3);
    std::cout << si.top() << "\n";  // 3
    si.pop();
    std::cout << si.top() << "\n";  // 2

    Stack<std::string> ss;
    ss.push("hello"); ss.push("world");
    std::cout << ss.top() << "\n";  // world
}
```

---

### Model 4.3: Template Specialization and C++20 Concepts

**Full specialization:** provide a completely different implementation for one specific type.

```cpp
#include <iostream>
#include <cstring>

// Primary template
template<typename T>
bool equal(T a, T b) { return a == b; }

// Full specialization for const char* - compare strings, not pointers
template<>
bool equal<const char*>(const char* a, const char* b) {
    return std::strcmp(a, b) == 0;
}

// Partial specialization (on class templates): specialize for T*
template<typename T>
class Printer {
public:
    void print(T val) { std::cout << "value: " << val << "\n"; }
};

template<typename T>
class Printer<T*> {  // partial specialization for pointer types
public:
    void print(T* ptr) {
        if (ptr) std::cout << "ptr->" << *ptr << "\n";
        else     std::cout << "null pointer\n";
    }
};
```

**C++20 Concepts:** express requirements on template arguments directly, giving better error messages and enabling overload selection.

```cpp
#include <concepts>
#include <numeric>
#include <vector>
#include <iostream>

// Constrain T to integral types (int, long, short, ...)
template<std::integral T>
T sum(const std::vector<T>& v) {
    return std::accumulate(v.begin(), v.end(), T{0});
}

// Custom concept: anything with .size() returning a number
template<typename C>
concept Sized = requires(C c) {
    { c.size() } -> std::convertible_to<std::size_t>;
};

template<Sized C>
void print_size(const C& c) {
    std::cout << "size = " << c.size() << "\n";
}

int main() {
    std::vector<int> vi = {1, 2, 3, 4, 5};
    std::cout << sum(vi) << "\n";   // 15
    print_size(vi);                 // size = 5
    // sum(std::vector<double>{1.1, 2.2});  // COMPILE ERROR: nice message:
    // error: 'double' does not satisfy 'integral'
}
```

**SFINAE / `std::enable_if` (pre-C++20 approach):** enable or disable template overloads based on type properties.

```cpp
#include <type_traits>
#include <iostream>

// Only enabled when T is arithmetic
template<typename T,
         typename = std::enable_if_t<std::is_arithmetic_v<T>>>
T square(T x) { return x * x; }

// Only enabled when T is NOT arithmetic
template<typename T,
         typename = std::enable_if_t<!std::is_arithmetic_v<T>>,
         typename = void>  // extra parameter to avoid redefinition
T square(T x) { return x * x; }  // works for types with operator*
```

---

### Critical Thinking Questions, Part 4

1.  **Template instantiation.**  The compiler generates a separate machine-code function for `max_of<int>` and `max_of<double>`.  Why does this not violate the "Don't Repeat Yourself" principle the way copy-pasted code would?  Under what circumstances could it become a code-size problem (hint: look up "template bloat")?

2.  **Specialization vs overloading.**  You can write both `template<> bool equal<const char*>(...)` (full specialization) and a plain overload `bool equal(const char* a, const char* b)`.  Scott Meyers argues you should prefer the overload.  Why?  (Hint: consider what happens with `equal("a", std::string("a"))` and how the compiler selects candidates.)

3.  **Concepts vs SFINAE.** Rewrite the following SFINAE-constrained function signature using a C++20 `requires` clause.  Explain which is easier to read and which gives better compiler error messages:
   ```cpp
   template<typename T, typename = std::enable_if_t<std::is_integral_v<T>>>
   T next_power_of_two(T n);
   ```

---

## Part 5: The Standard Template Library (STL)

### Model 5.1: Sequence Containers

```cpp
#include <iostream>
#include <vector>
#include <deque>
#include <list>

void sequence_containers() {
    // vector: contiguous memory, O(1) amortised push_back, O(n) insert-middle
    std::vector<int> v = {1, 2, 3, 4, 5};
    v.push_back(6);       // O(1) amortized
    v.insert(v.begin()+2, 99);  // O(n) - shifts elements right

    // deque: double-ended queue, O(1) push_front AND push_back
    // but non-contiguous memory -> worse cache performance than vector
    std::deque<int> dq = {10, 20, 30};
    dq.push_front(5);   // O(1)
    dq.push_back(40);   // O(1)

    // list: doubly-linked, O(1) insert anywhere given an iterator
    // but no random access, pointer-per-node overhead
    std::list<int> lst = {1, 2, 3};
    auto it = lst.begin(); ++it;
    lst.insert(it, 99);  // O(1) insert before position
    lst.splice(lst.end(), lst, lst.begin()); // move node without allocation
}
```

**Container complexity comparison:**

| Operation          | `vector`     | `deque`      | `list`       |
|--------------------|:------------:|:------------:|:------------:|
| Random access      | O(1)         | O(1)         | O(n)         |
| push_back          | O(1) amort.  | O(1)         | O(1)         |
| push_front         | O(n)         | O(1)         | O(1)         |
| Insert (middle)    | O(n)         | O(n)         | O(1)*        |
| Iterator valid after insert | No (may reallocate) | Partially | Yes |
| Cache friendliness | Excellent    | Good         | Poor         |

*O(1) given an iterator to the insertion point; finding that iterator is O(n).

---

### Model 5.2: Associative Containers and Unordered Variants

```cpp
#include <iostream>
#include <map>
#include <unordered_map>
#include <set>

void associative_containers() {
    // map: red-black tree, keys sorted, O(log n) operations
    std::map<std::string, int> word_count;
    for (auto& w : {"the","quick","brown","fox","the","fox"})
        ++word_count[w];
    // Iterating gives sorted order:
    for (auto& [k, v] : word_count)
        std::cout << k << ": " << v << "\n";

    // unordered_map: hash table, O(1) average, O(n) worst case
    // Use when you don't need sorted order
    std::unordered_map<std::string, int> fast_count;
    fast_count.reserve(100);              // pre-size the bucket array
    fast_count.max_load_factor(0.7f);     // rehash when 70% full
    fast_count["hello"] = 1;
    fast_count["world"] = 2;

    // set: sorted unique keys, O(log n)
    std::set<int> primes = {2, 3, 5, 7, 11, 13};
    primes.insert(17);
    std::cout << "contains 7: " << primes.count(7) << "\n";
    // lower_bound / upper_bound: range queries in O(log n)
    auto lo = primes.lower_bound(5);   // iterator to first element >= 5
    auto hi = primes.upper_bound(11);  // iterator to first element > 11
    for (auto i = lo; i != hi; ++i) std::cout << *i << " "; // 5 7 11
    std::cout << "\n";
}
```

---

### Model 5.3: Algorithms, Iterators, and Lambdas

```cpp
#include <iostream>
#include <vector>
#include <algorithm>
#include <numeric>
#include <functional>

void stl_algorithms() {
    std::vector<int> v = {5, 2, 8, 1, 9, 3, 7, 4, 6};

    // sort: O(n log n) introsort
    std::sort(v.begin(), v.end());   // ascending
    std::sort(v.begin(), v.end(), std::greater<int>());  // descending

    // find / find_if
    auto it = std::find(v.begin(), v.end(), 5);
    if (it != v.end()) std::cout << "found 5 at offset " << (it - v.begin()) << "\n";

    auto big = std::find_if(v.begin(), v.end(), [](int x){ return x > 6; });
    if (big != v.end()) std::cout << "first >6: " << *big << "\n";

    // transform: map each element through a function into an output range
    std::vector<int> squares(v.size());
    std::transform(v.begin(), v.end(), squares.begin(),
                   [](int x){ return x * x; });

    // accumulate: left fold
    int total = std::accumulate(v.begin(), v.end(), 0);
    std::cout << "sum = " << total << "\n";  // 45

    // Accumulate with custom binary op: product
    long product = std::accumulate(v.begin(), v.end(), 1L, std::multiplies<long>());
    std::cout << "product = " << product << "\n";  // 362880

    // partition: reorder so predicate-true elements come first
    std::vector<int> data = {1, 2, 3, 4, 5, 6, 7, 8};
    auto mid = std::partition(data.begin(), data.end(),
                              [](int x){ return x % 2 == 0; });
    // [mid, end) contains odd numbers; [begin, mid) contains even numbers

    // for_each with stateful lambda (captures by reference)
    int running_sum = 0;
    std::for_each(v.begin(), v.end(), [&running_sum](int x) {
        running_sum += x;
    });
    std::cout << "running sum = " << running_sum << "\n";
}
```

**Iterator categories** (each is a strict superset of the one above it):

| Category        | Read | Write | Multi-pass | Bidirectional | Random |
|-----------------|:----:|:-----:|:----------:|:-------------:|:------:|
| Input           | Yes  | -     | No         | -             | -      |
| Output          | -    | Yes   | No         | -             | -      |
| Forward         | Yes  | Yes   | Yes        | -             | -      |
| Bidirectional   | Yes  | Yes   | Yes        | Yes           | -      |
| Random Access   | Yes  | Yes   | Yes        | Yes           | Yes    |

`vector` and `deque` provide random-access iterators. `list`, `map`, and `set` provide bidirectional iterators. `forward_list` provides forward iterators. `istream_iterator` and `ostream_iterator` are input/output iterators.

---

### Critical Thinking Questions, Part 5

1.  **Container choice.**  For each scenario, choose the best STL container and justify your answer in terms of complexity:
   - A spell-checker needs O(1) average lookup of 100,000 English words.
   - A task scheduler needs to always pop the highest-priority task.
   - A text editor stores a long document where characters are frequently inserted and deleted at the cursor position.
   - A cache needs to iterate in insertion order and do O(1) lookup by key.

2.  **Iterator invalidation.**  What happens to existing iterators into a `std::vector<int>` after you call `push_back`?  How does this differ for `std::list<int>`?  Write a code snippet that exhibits undefined behaviour due to iterator invalidation in a `vector`.

3.  **Lambda capture modes.**  Explain the difference between `[=]`, `[&]`, `[x]`, `[&x]`, and `[this]` lambda captures.  Why can capturing `[&]` in a lambda returned from a function cause use-after-free?

4.  **Algorithm composition.**  Using only `std::transform`, `std::copy_if`, and `std::accumulate` (no raw loops), write the expression to compute the sum of squares of all even numbers in a `vector<int>`.  Name the higher-order programming pattern this represents.

---

## Part 6: Vtables, Polymorphism, and Type Erasure

### Model 6.1: Virtual Functions and the Vtable

When a class has virtual functions, the compiler adds a hidden pointer (the **vptr**) to every object.  This vptr points to the class's **vtable**, a static array of function pointers.

```
Object layout in memory:
+-------------------------------------+
|  vptr ------------------------------+-->  vtable for Shape
|-------------------------------------+       +-------------------------------+
|  member fields...                   |       | [0]  &Shape::area      (pure) |
`-------------------------------------+       | [1]  &Shape::perimeter (pure) |
                                              | [2]  &Shape::describe         |
Object layout for Circle:                     `-------------------------------+
+-------------------------------------+
|  vptr ------------------------------+-->  vtable for Circle
|-------------------------------------+       +-------------------------------+
|  radius (double)                    |       | [0]  &Circle::area            |
`-------------------------------------+       | [1]  &Circle::perimeter       |
                                              | [2]  &Shape::describe         |
                                              `-------------------------------+
```

```cpp
#include <iostream>
#include <cmath>
#include <memory>
#include <vector>

class Shape {
public:
    virtual ~Shape() = default;                   // virtual dtor is essential!
    virtual double area()      const = 0;         // pure virtual
    virtual double perimeter() const = 0;         // pure virtual
    virtual void   describe()  const {            // virtual with default impl
        std::cout << "Shape: area=" << area()
                  << " perimeter=" << perimeter() << "\n";
    }
};

class Circle : public Shape {
    double r_;
public:
    explicit Circle(double r) : r_(r) {}
    double area()      const override { return M_PI * r_ * r_; }
    double perimeter() const override { return 2 * M_PI * r_; }
};

class Rectangle : public Shape {
    double w_, h_;
public:
    Rectangle(double w, double h) : w_(w), h_(h) {}
    double area()      const override { return w_ * h_; }
    double perimeter() const override { return 2 * (w_ + h_); }
    void   describe()  const override {
        std::cout << "Rectangle " << w_ << "x" << h_
                  << ": area=" << area() << "\n";
    }
};

void virtual_dispatch_demo() {
    // Polymorphic collection - vtable lookup at every virtual call
    std::vector<std::unique_ptr<Shape>> shapes;
    shapes.push_back(std::make_unique<Circle>(3.0));
    shapes.push_back(std::make_unique<Rectangle>(4.0, 5.0));

    for (const auto& s : shapes) {
        s->describe();  // dispatched through vtable: O(1) but indirect
    }
}

// dynamic_cast: safe downcast with RTTI check
void rtti_demo(Shape* s) {
    if (auto* c = dynamic_cast<Circle*>(s)) {
        std::cout << "It's a Circle!\n";
    } else if (auto* r = dynamic_cast<Rectangle*>(s)) {
        std::cout << "It's a Rectangle!\n";
    }
    // typeid: get the exact runtime type
    std::cout << "typeid: " << typeid(*s).name() << "\n";
}
```

---

### Model 6.2: Type Erasure: `std::function` and Friends

**Type erasure** hides the concrete type behind a stable interface.  You can store a lambda, a function pointer, a functor, or a member function pointer in the same `std::function` object, without knowing the concrete type at the call site.

```cpp
#include <iostream>
#include <functional>
#include <vector>
#include <string>

// std::function<R(Args...)> - type-erased callable wrapper
void function_demo() {
    // Three very different callables, same std::function type:
    std::function<int(int, int)> op;

    op = [](int a, int b){ return a + b; };   // lambda
    std::cout << op(3, 4) << "\n";            // 7

    op = std::plus<int>{};                    // functor
    std::cout << op(3, 4) << "\n";            // 7

    auto multiply = [factor = 10](int a, int b){ return a * b * factor; };
    op = multiply;                            // capturing lambda
    std::cout << op(3, 4) << "\n";            // 120

    // Store heterogeneous callables in a homogeneous container:
    std::vector<std::function<std::string(const std::string&)>> transforms;
    transforms.push_back([](const std::string& s){ return s + "!"; });
    transforms.push_back([](const std::string& s){
        std::string r = s;
        for (auto& c : r) c = std::toupper(c);
        return r;
    });
    transforms.push_back([](const std::string& s){
        return std::string(s.rbegin(), s.rend());
    });

    std::string input = "hello";
    for (auto& t : transforms)
        std::cout << t(input) << "\n";
    // hello!
    // HELLO
    // olleh
}

// std::any - type-erased value (any CopyConstructible type)
#include <any>
void any_demo() {
    std::any a = 42;
    std::cout << std::any_cast<int>(a) << "\n";  // 42
    a = std::string("hello");
    std::cout << std::any_cast<std::string>(a) << "\n";  // hello
    try {
        std::any_cast<int>(a);  // throws std::bad_any_cast
    } catch (const std::bad_any_cast& e) {
        std::cout << "bad_any_cast: " << e.what() << "\n";
    }
}

// std::variant - type-safe discriminated union (knows which type is active)
#include <variant>
void variant_demo() {
    std::variant<int, double, std::string> v;
    v = 42;
    std::cout << std::get<int>(v) << "\n";  // 42
    v = 3.14;
    // std::get<int>(v) would throw std::bad_variant_access
    std::visit([](auto&& val){
        std::cout << "variant holds: " << val << "\n";
    }, v);
}
```

---

### Python Interlude, Duck Typing vs Explicit Interfaces

In Python, type erasure is the *default*: any callable is accepted anywhere a callable is expected.  This contrast helps clarify *why* C++ needs explicit type erasure machinery.

```python
try:
    # --- Duck typing: no explicit interface needed ---
    class Adder:
        def __call__(self, a, b):
            return a + b

    class Multiplier:
        def __call__(self, a, b):
            return a * b

    def apply_op(op, a, b):
        """Accepts ANY callable - Python erases the type automatically."""
        return op(a, b)

    ops = [Adder(), Multiplier(), lambda a, b: a ** b]
    for op in ops:
        print(f"  {op.__class__.__name__ if hasattr(op, '__class__') else 'lambda'}({3}, {4}) = {apply_op(op, 3, 4)}")

    print()

    # --- Simulating std::function's cost: the vtable lookup ---
    # In C++, std::function stores the callable in an internal buffer
    # and dispatches via a type-erased function pointer (small-buffer optimization).
    # Here we simulate that with a wrapper class.
    class TypeErasedCallable:
        """Simulate what std::function<int(int,int)> does internally."""
        def __init__(self, fn):
            self._fn = fn          # stored callable (any type)
            self._type = type(fn).__name__

        def __call__(self, *args):
            return self._fn(*args) # indirect dispatch (like vtable call)

        def __repr__(self):
            return f"TypeErased<{self._type}>"

    erased = [TypeErasedCallable(f) for f in ops]
    print("Type-erased container (like std::vector<std::function<...>>):")
    for e in erased:
        print(f"  {e!r}(5, 3) = {e(5, 3)}")

    print()

    # --- Python's actual type checking ---
    import inspect
    callable_obj = Adder()
    print(f"  callable(Adder()) = {callable(callable_obj)}")
    print(f"  callable(42)      = {callable(42)}")
    print("  (Python checks for __call__ at runtime; C++ checks at compile time)")

except Exception as e:
    print(f"[type-erasure] {e}")
    import traceback; traceback.print_exc()
```

---

### Critical Thinking Questions, Part 6

1.  **Virtual dispatch cost.**  A non-virtual function call is resolved at compile time (direct call instruction).  A virtual function call requires: (a) load the vptr from the object, (b) index into the vtable, (c) load the function pointer, (d) call indirectly.  In tight loops, this indirect branch can cause branch-misprediction penalties.  Name two techniques used in production code to recover this performance while keeping polymorphic behaviour.

2.  **Why virtual destructors?**  Suppose `Shape` does not have a `virtual` destructor.  You write `Shape* s = new Circle(3.0); delete s;`.  What happens?  Write out the exact sequence of destructor calls in both cases (virtual vs non-virtual).

3.  **`std::function` overhead.** `std::function` uses *small-buffer optimization (SBO)*: callables that fit in ~24-48 bytes are stored inline (no heap allocation).  Larger callables are heap-allocated.  Given `auto big_lambda = [captured_array = std::array<char, 128>{}](int x){ return x; };`, will `std::function<int(int)> f = big_lambda;` trigger a heap allocation?  How would you verify this?

4.  **`std::variant` vs inheritance.** `std::variant<Circle, Rectangle>` and a base-class hierarchy both model "a shape that is either a Circle or a Rectangle".  List two advantages of the `variant` approach and two advantages of the virtual-function approach.  (Hint: open/closed extensibility, separate compilation, pattern matching.)

---

## Part 7: Modern C++ Idioms (C++17/20)

### Model 7.1: Structured Bindings and `std::optional`

```cpp
{% raw %}
#include <iostream>
#include <map>
#include <optional>
#include <string>
#include <tuple>

// Structured bindings (C++17): decompose pairs, tuples, structs
void structured_bindings() {
    std::map<std::string, int> scores = {{"Alice",95},{"Bob",82},{"Carol",90}};

    for (auto& [name, score] : scores) {
        std::cout << name << ": " << score << "\n";
    }

    // Structured binding from tuple
    auto [x, y, z] = std::make_tuple(1, 2.5, std::string("hi"));
    std::cout << x << " " << y << " " << z << "\n";

    // Structured binding from struct (works on aggregates)
    struct Point { double x, y; };
    Point p{3.0, 4.0};
    auto [px, py] = p;
    std::cout << "point: " << px << ", " << py << "\n";
}

// std::optional<T>: a value that may or may not be present
// Replaces: returning -1 as sentinel, returning nullptr, output parameters
std::optional<int> safe_divide(int a, int b) {
    if (b == 0) return std::nullopt;  // no value
    return a / b;
}

std::optional<std::string> find_user(int id) {
    if (id == 42) return std::string("Alice");
    return std::nullopt;
}

void optional_demo() {
    auto result = safe_divide(10, 2);
    if (result) std::cout << "10/2 = " << *result << "\n";

    auto bad = safe_divide(10, 0);
    std::cout << "10/0 has value: " << bad.has_value() << "\n";
    std::cout << "10/0 or -1: " << bad.value_or(-1) << "\n";  // -1

    // Chaining with optional (C++23 monadic ops; here we do it manually)
    auto user = find_user(42);
    if (user) std::cout << "user: " << *user << "\n";
}
{% endraw %}
```

---

### Model 7.2: `std::string_view` and Compile-Time Computation

```cpp
#include <iostream>
#include <string>
#include <string_view>

// string_view: non-owning reference to a contiguous sequence of chars
// No allocation, no copy - just a {pointer, length} pair
size_t count_vowels(std::string_view sv) {   // accepts string, const char*, etc.
    size_t n = 0;
    for (char c : sv)
        if (std::string_view("aeiouAEIOU").find(c) != std::string_view::npos) ++n;
    return n;
}

void string_view_demo() {
    std::string s = "Hello, World!";
    const char* cstr = "Hello, World!";
    std::string_view sv = "Hello, World!";   // string literal

    std::cout << count_vowels(s)    << "\n"; // No copy of s
    std::cout << count_vowels(cstr) << "\n"; // No copy of cstr
    std::cout << count_vowels(sv)   << "\n"; // Same underlying data

    // Substring via string_view - O(1), no allocation
    std::string_view sub = sv.substr(7, 5);  // "World"
    std::cout << sub << "\n";

    // DANGER: string_view lifetime pitfall
    // std::string_view dangle() {
    //     std::string s = "temporary";
    //     return s;   // DANGLING: s is destroyed, view references freed memory
    // }
}

// constexpr: evaluated at compile time when all inputs are constant
constexpr int factorial(int n) {
    return n <= 1 ? 1 : n * factorial(n - 1);
}

// consteval (C++20): MUST be evaluated at compile time - compiler error if not
consteval int fibonacci(int n) {
    if (n <= 1) return n;
    return fibonacci(n-1) + fibonacci(n-2);
}

void compile_time_demo() {
    constexpr int f10 = factorial(10);      // computed at compile time: 3628800
    constexpr int fib8 = fibonacci(8);      // computed at compile time: 21
    std::cout << "10! = " << f10 << "\n";
    std::cout << "fib(8) = " << fib8 << "\n";

    // These values are literally constants in the binary - zero runtime cost.
    static_assert(factorial(5) == 120, "compile-time check");
}
```

---

### Model 7.3: Ranges (C++20) and Fold Expressions

```cpp
#include <iostream>
#include <vector>
#include <string>
#include <ranges>
#include <algorithm>
#include <numeric>

// C++20 Ranges: composable, lazy view pipeline
void ranges_demo() {
    std::vector<int> v = {1, 2, 3, 4, 5, 6, 7, 8, 9, 10};

    // Lazy pipeline: filter evens, square them, take first 4
    auto pipeline = v
        | std::views::filter([](int x){ return x % 2 == 0; })
        | std::views::transform([](int x){ return x * x; })
        | std::views::take(4);

    for (int x : pipeline) std::cout << x << " ";  // 4 16 36 64
    std::cout << "\n";

    // Ranges with strings
    std::string text = "Hello, World! This is C++20 ranges.";
    auto words = text
        | std::views::split(' ')
        | std::views::transform([](auto word){
              return std::string(word.begin(), word.end());
          })
        | std::views::filter([](const std::string& w){ return w.size() > 3; });

    for (auto& w : words) std::cout << w << " ";
    std::cout << "\n";
}

// Variadic templates + fold expressions (C++17)
template<typename... Args>
auto sum_all(Args... args) {
    return (args + ...);   // unary right fold: a + (b + (c + d))
}

template<typename... Args>
void print_all(Args&&... args) {
    ((std::cout << args << " "), ...);  // fold over comma operator
    std::cout << "\n";
}

template<typename T, typename... Args>
bool any_of_equal(T val, Args... args) {
    return ((val == args) || ...);  // short-circuit fold
}

void fold_demo() {
    std::cout << sum_all(1, 2, 3, 4, 5) << "\n";       // 15
    std::cout << sum_all(1.1, 2.2, 3.3) << "\n";       // 6.6
    print_all("hello", 42, 3.14, true);
    std::cout << any_of_equal(5, 1, 2, 5, 8) << "\n";  // 1 (true)
}
```

---

### Model 7.4: Coroutines (C++20): Brief Introduction

Coroutines are functions that can be suspended and resumed.  C++20 provides the machinery; you typically use a library wrapper (`std::generator` in C++23, or a coroutine handle wrapper).

```cpp
// Coroutines require a Promise type and coroutine handle.
// This is a minimal sketch - real use requires a generator library.
// The syntax is standard; execution infrastructure varies by library.

// co_yield expr   - suspend and yield a value to the caller
// co_return expr  - terminate the coroutine
// co_await expr   - suspend until awaitable completes

// Conceptual coroutine generator (requires C++23 std::generator
// or a custom generator<T> type from a library like cppcoro):
//
// generator<int> fibonacci_coro() {
//     int a = 0, b = 1;
//     while (true) {
//         co_yield a;
//         auto c = a + b;
//         a = b;
//         b = c;
//     }
// }
//
// int main() {
//     auto gen = fibonacci_coro();
//     for (auto it = gen.begin(); it != gen.end() && *it < 100; ++it)
//         std::cout << *it << " ";   // 0 1 1 2 3 5 8 13 21 34 55 89
// }

// Key idea: the coroutine frame is heap-allocated, and the
// local variables survive across suspensions. This enables
// lazy infinite sequences, async I/O, and cooperative multitasking
// without explicit state machines.
```

---

### Critical Thinking Questions, Part 7

1.  **`std::optional` vs pointer.**  Both `std::optional<Widget>` and `Widget*` can represent "a Widget or nothing."  List three specific scenarios where `std::optional` is the better choice, and one scenario where a pointer (raw or smart) is the better choice.  What does `optional` communicate about *ownership* that a raw pointer does not?

2.  **`string_view` lifetime pitfalls.**  Consider the following three functions.  For each, state whether the returned `string_view` is safe to use after the function returns, and explain why:

   ```cpp
   // a)
   std::string_view f1() {
       static std::string s = "hello";
       return s;
   }

   // b)
   std::string_view f2(const std::string& s) {
       return s.substr(0, 3);
   }

   // c)
   std::string_view f3() {
       return "compile-time string literal";
   }
   ```

3.  **Ranges vs `<algorithm>`.**  The pre-C++20 way to filter-then-transform is:
   ```cpp
   std::vector<int> evens;
   std::copy_if(v.begin(), v.end(), std::back_inserter(evens), is_even);
   std::vector<int> squares;
   std::transform(evens.begin(), evens.end(), std::back_inserter(squares), square);
   ```
   The ranges way is lazy: `v | filter(is_even) | transform(square)`.  Explain what "lazy" means here in terms of memory allocation and when each element is processed.  Under what conditions is the ranges version both faster and more memory-efficient?

---

## Further Reading

- **C++ Core Guidelines**: [https://isocpp.github.io/CppCoreGuidelines/CppCoreGuidelines](https://isocpp.github.io/CppCoreGuidelines/CppCoreGuidelines)
  The authoritative set of guidelines maintained by Bjarne Stroustrup and Herb Sutter.  Every section in this tutorial has a corresponding guideline.  Read especially: R (resource management), T (templates), and C (classes).

- **cppreference.com**: [https://en.cppreference.com/](https://en.cppreference.com/)
  The definitive online reference for every C++ standard library component.  When the standard says "effects as if," cppreference shows the actual complexity, iterator invalidation rules, and example code.  Bookmark it.

- **Scott Meyers, "Effective Modern C++" (O'Reilly, 2014)**
  42 specific items covering `auto`, smart pointers, move semantics, lambdas, and concurrency.  Items 1-9 (type deduction), 18-22 (smart pointers), and 23-30 (move semantics) map directly to this tutorial.  Read it after you feel comfortable with the concepts here.

- **"C++ Templates: The Complete Guide", Vandevoorde, Josuttis, Gregor (2nd ed.)**
  Deep dive into template mechanics: instantiation, argument deduction, SFINAE, variadic templates, and expression templates.  Essential for library authors.

- **CppCon talks (YouTube)**: Search for:
  - "Back to Basics: Smart Pointers", Arthur O'Dwyer
  - "Type Erasure", Klaus Iglberger
  - "The Most Vexing Parse", Howard Hinnant
  - "What Has My Compiler Done for Me Lately?", Matt Godbolt

---

## Reflection

> **"Which C++ feature most surprised you, and how does it connect to a concept from programming language theory?"**

Write 2-3 paragraphs addressing the following:

1.  **The surprising feature.**  Pick one concept from this tutorial (move semantics, type erasure, `constexpr`, Concepts, RAII, or another) that you did not expect to work the way it does.  Describe precisely what surprised you.

2.  **The PL theory connection.**  Map your chosen feature to a concept from the programming languages theory portion of this course:
   - *Ownership types / affine types*: `unique_ptr`'s move-only semantics correspond to **affine types** (used at most once).  Rust formalizes this as its ownership system.  How does C++'s approach differ from Rust's compile-time enforcement?
   - *Parametric polymorphism*: Templates are C++'s mechanism for parametric polymorphism, the same construct studied in Hindley-Milner type theory (Haskell's `forall a. a -> a`).  But C++ templates use *duck typing at instantiation time* rather than type-class constraints.  How do C++20 Concepts close this gap?
   - *Type erasure and existential types*: `std::function<int(int)>` hides the concrete callable type.  In type theory, this corresponds to an **existential type** `∃T. (T, T->int)`: there exists some type T, along with a value of T and a function from T to int.  How does `std::any` differ; what existential does it represent?
   - *Lazy evaluation*: C++20 ranges are lazy in the same sense as Haskell's list combinators.  Both defer computation until the value is demanded.  What does this say about the relationship between the iterator protocol and **thunks** in lazy languages?

3.  **Design tradeoff.**  Every C++ feature has a cost.  Does your chosen feature introduce runtime overhead?  Compile-time overhead?  Code complexity?  How does the C++ design philosophy of **zero-cost abstractions** justify or limit the feature's design?

---

## Appendix: Foreign Function Interfaces, Crossing Language Boundaries

This appendix supports the Team Language Project's **Foreign Function Interface** extension: it shows how languages call into native code (the C ABI, `ctypes`, C-compatible structs and callbacks, name mangling) and how to design an `ffi(...)` primitive for your own language.

> **Imagine the United Nations General Assembly.**  Each delegate speaks their own language and follows their own parliamentary customs.  A simultaneous interpreter sits in a booth, listening to one language and speaking another in real time, handling not just words but idioms, formal registers, and cultural conventions that do not map one-to-one.  A Foreign Function Interface is exactly that interpreter: it sits between two language runtimes, negotiating the differences in data layout, calling conventions, memory ownership, and error handling so that a function written in C can be invoked transparently from Python, Haskell, or your own mini language.  Without this translator, each language would be an island; with it, every language inherits the vast ecosystem of C libraries built over 50 years.

### Learning Goals

By the end of this section, you will be able to:

- Explain the C Application Binary Interface (ABI) and identify why it serves as the universal interoperability layer between languages
- Use Python's `ctypes` and `cffi` to call C library functions, correctly specifying argument types, return types, and memory ownership
- Identify the challenges FFI introduces (data layout differences, memory ownership, calling conventions, and error handling) and describe how each is addressed
- Trace the lifecycle of a foreign call from the high-level language through marshaling, native execution, and unmarshaling back
- Implement a simple FFI extension mechanism in a mini interpreter that allows it to call pre-registered native functions

> **Prerequisites:** Python programming; basic C syntax; familiarity with the interpreter project
> **Goal:** Understand how languages call into native code (the C ABI, data representation, name mangling, `ctypes`/`cffi`) and implement a simple FFI extension for a mini interpreter.

> **Before You Begin**
>
> This section assumes you are comfortable with:
>
> - Python functions, classes, and the `import` statement
> - Basic C vocabulary: functions, pointers, structs, `sizeof`, `malloc`/`free` (conceptual understanding is enough; you will not write C code)
> - The concept of a *shared library* (`.so` on Linux, `.dylib` on macOS, `.dll` on Windows), a compiled binary that can be loaded at runtime
> - Python's `dataclass` decorator and `isinstance` checks (used in Model 5)
>
> You do **not** need to have written C code before.  When C snippets appear (e.g., `int (*compar)(const void*, const void*)`), they are read-only reference points; the Python code does all the actual work.  If a C type looks unfamiliar, focus on what `ctypes` does with it rather than the C syntax itself.

---

### Preface: Why Every Language Needs to Call C

*Intuition:* Every high-level language you have ever used (Python, JavaScript, Ruby, Java) eventually bottoms out in native code.  When Python opens a file, it calls a C function in the operating system.  When it computes a sine, it calls a C math library.  When it sends a network packet, it calls a C socket API. The FFI is the seam between the comfortable, safe, garbage-collected world of your high-level language and the raw, pointer-filled world of the operating system and hardware.  Understanding that seam makes you a better programmer regardless of which side you spend most of your time on.

No programming language is an island.  The operating system, graphics drivers, cryptography libraries, database engines, and compression algorithms are all written in C (or C++, which uses C's ABI for its C-compatible subset).  To be useful, a language must be able to call into this world.

A **Foreign Function Interface (FFI)** is the mechanism by which one language calls functions written in another.  "Foreign" means "outside the current language runtime."  The most common form is calling C from a high-level language (Python, Haskell, Lua, Julia) because:

1.  **C is the universal ABI:** Nearly all languages can call C; C is the *lingua franca* of system interfaces.
2.  **Performance:** Native code runs without an interpreter loop.
3.  **Library reuse:** Millions of battle-tested C libraries exist.

The challenge: the high-level language's runtime and the C runtime make different assumptions about data layout, memory ownership, error handling, and calling conventions.

---

### Model 1: The C Application Binary Interface (ABI)

*Intuition:* When you call a function, the CPU needs to know: where are the arguments?  (In registers?  On the stack?  Which ones?)  Who cleans up after the call?  What format does the return value come back in?  The ABI is the contract that answers all of these questions.  Think of it as the physical handshake protocol between two programs.  C's ABI has become the universal handshake because C was the first widely-portable systems language, and every other language that wanted to talk to the operating system had to agree to shake hands on C's terms.

> **Watch out!**  You must declare `argtypes` and `restype` on a `ctypes` function object before calling it.  If you skip this step, `ctypes` will guess (usually defaulting to `c_int`) and you will get silent data corruption or crashes instead of a clean error.  Always set both, even for functions whose return type is `void`.

An **ABI (Application Binary Interface)** defines how functions are called at the machine level: which registers hold arguments, who cleans up the stack, how structures are laid out in memory, what calling conventions are used.  C's ABI is the de facto standard because it is stable, documented, and supported by every compiler on every platform.

```python
import ctypes
import sys

# ctypes gives us direct access to the C standard library
# without writing any C code ourselves

# Load the C standard library
if sys.platform == "linux":
    libc = ctypes.CDLL("libc.so.6")
elif sys.platform == "darwin":
    libc = ctypes.CDLL("libc.dylib")
else:
    libc = ctypes.msvcrt   # Windows fallback

print("=== Calling C's strlen via ctypes ===")
# strlen(const char *s) -> size_t
libc.strlen.restype  = ctypes.c_size_t
libc.strlen.argtypes = [ctypes.c_char_p]

s = b"Hello, world!"   # bytes, not str - C expects null-terminated bytes
length = libc.strlen(s)
print(f"  strlen({s!r}) = {length}")
print(f"  Python: len({s!r}) = {len(s)}")
print(f"  Same? {length == len(s)}")

print()
print("=== Calling C's abs and labs ===")
libc.abs.restype  = ctypes.c_int
libc.abs.argtypes = [ctypes.c_int]
libc.labs.restype  = ctypes.c_long
libc.labs.argtypes = [ctypes.c_long]

for v in [-42, 0, 100, -32768]:
    print(f"  abs({v:6d}) = {libc.abs(v)}")

print()
print("=== C data types and their Python equivalents ===")
type_map = [
    ("c_int",    ctypes.c_int,    42),
    ("c_long",   ctypes.c_long,   42),
    ("c_float",  ctypes.c_float,  3.14),
    ("c_double", ctypes.c_double, 3.14),
    ("c_char_p", ctypes.c_char_p, b"hello"),
    ("c_void_p", ctypes.c_void_p, None),
]
for name, ctype, example in type_map:
    obj = ctype(example) if example is not None else ctype()
    print(f"  ctypes.{name:<12} value={obj.value!r:<15} "
          f"sizeof={ctypes.sizeof(ctype)} bytes")
```

**Key insight:** `ctypes` marshals Python values into C-compatible binary representations automatically for simple types.  For complex types (structs, arrays, function pointers), you must describe the layout explicitly.

> **Critical Thinking Questions 1-3**

**CTQ 1.** `strlen` expects a `const char *`, a pointer to a null-terminated byte array.  Why does `ctypes` require `b"Hello"` (bytes) rather than `"Hello"` (str)?  What does Python's str store internally that C's `char *` does not?

**CTQ 2.** `ctypes.c_float` has sizeof 4 bytes; `ctypes.c_double` has sizeof 8 bytes.  Python's `float` is always 64-bit (a C `double`).  What precision loss happens when you pass a Python `float` to a C function declared with `c_float` parameter?

**CTQ 3.**  The ABI specifies how arguments are passed: by register (x86-64 uses rdi, rsi, rdx, rcx, r8, r9 for first 6 integer args) or by stack (7th and beyond).  A language that passes arguments in the wrong order or wrong registers will silently corrupt function calls.  What is the responsibility of `ctypes` in this context?

---

### Model 2: Structs, Pointers, and Memory Layout

*Intuition:* A C struct is just a named chunk of memory.  The compiler decides exactly how many bytes each field occupies and at what offset from the start of the struct, and it follows strict rules about *alignment* (each field must start at an address that is a multiple of its size).  When you pass a struct across an FFI boundary, the receiving side must use *exactly* the same layout, or it will read the wrong bytes. `ctypes.Structure` exists precisely to let Python declare the layout explicitly so the two sides agree.

> **Watch out!**  Struct padding is invisible in the source code but very real in memory.  A struct with fields `uint8, uint32, uint16` (1+4+2 = 7 bytes naively) will actually occupy 8 or more bytes because the `uint32` field must be 4-byte aligned.  Always use `ctypes.sizeof` to check the real size; never compute it by adding field sizes by hand.

C structs have a specific memory layout (with padding).  When calling C functions that take or return structs, the FFI must reproduce the exact layout.

```python
import ctypes

# Define a C-compatible struct in Python
class Point(ctypes.Structure):
    _fields_ = [
        ("x", ctypes.c_double),
        ("y", ctypes.c_double),
    ]

class Rect(ctypes.Structure):
    _fields_ = [
        ("top_left",     Point),
        ("bottom_right", Point),
    ]

print("=== C struct layout ===")
p = Point(3.0, 4.0)
print(f"  Point({p.x}, {p.y})")
print(f"  sizeof(Point) = {ctypes.sizeof(Point)} bytes")
print(f"  offset(x) = {Point.x.offset}, offset(y) = {Point.y.offset}")

r = Rect(Point(0.0, 0.0), Point(10.0, 5.0))
print(f"\n  Rect: ({r.top_left.x},{r.top_left.y}) -> ({r.bottom_right.x},{r.bottom_right.y})")
print(f"  sizeof(Rect) = {ctypes.sizeof(Rect)} bytes")

print()
print("=== Struct with alignment padding ===")
class Padded(ctypes.Structure):
    _fields_ = [
        ("flag",  ctypes.c_uint8),    # 1 byte
        ("value", ctypes.c_uint32),   # 4 bytes - but likely padded to 4-byte boundary
        ("extra", ctypes.c_uint16),   # 2 bytes
    ]

print(f"  Padded: flag@{Padded.flag.offset}, value@{Padded.value.offset}, "
      f"extra@{Padded.extra.offset}")
print(f"  sizeof(Padded) = {ctypes.sizeof(Padded)} bytes  "
      f"(vs naive 1+4+2=7 bytes)")

print()
print("=== Passing structs by pointer ===")
class Vec2(ctypes.Structure):
    _fields_ = [("x", ctypes.c_float), ("y", ctypes.c_float)]

def magnitude_python(v: Vec2) -> float:
    import math
    return math.sqrt(v.x**2 + v.y**2)

# Simulate how an FFI would call a C function that takes a Vec2*
v = Vec2(3.0, 4.0)
ptr = ctypes.byref(v)    # byref creates a pointer to v without copying
print(f"  Vec2(3, 4) at address {id(v):#x}")
print(f"  magnitude = {magnitude_python(v):.4f}")

print()
print("=== C arrays ===")
IntArray5 = ctypes.c_int * 5
arr = IntArray5(10, 20, 30, 40, 50)
print(f"  C array of 5 ints: {list(arr)}")
print(f"  sizeof = {ctypes.sizeof(arr)} bytes ({ctypes.sizeof(ctypes.c_int)} × 5)")
```

> **Critical Thinking Questions 4-6**

**CTQ 4.**  The `Padded` struct has `sizeof` greater than 1+4+2=7.  The compiler adds **padding** between fields to align them to their natural alignment.  Why does alignment matter?  What hardware problem does misaligned access cause on x86?  On ARM?

**CTQ 5.** `ctypes.byref(v)` passes a pointer to `v` without copying.  If the C function modifies the struct through the pointer, the Python object `v` is also modified.  How does this differ from Python's normal parameter passing semantics?  When is this desirable?  When is it dangerous?

**CTQ 6.**  Structs can be passed **by value** (C copies the struct) or **by pointer** (C receives an address).  For large structs, passing by pointer is more efficient.  But it also means the callee can modify the original.  How do languages like Rust use the type system to make this safe?

---

### Model 3: Callbacks, C Calling Back into Python

*Intuition:* The FFI translator analogy runs in both directions.  When you hire an interpreter for a UN session, sometimes the foreign delegate asks the interpreter a question; the interpreter must be able to respond, not just relay.  Callbacks are the same: a C library like `qsort` does not just receive data; it calls back into your code to ask "which of these two items is larger?"  The Python function you provide becomes, for the duration of the C call, a first-class participant in C's execution; it must speak C's calling convention fluently, which is what `ctypes.CFUNCTYPE` arranges.

> **Watch out!**  C holds a raw function pointer to your Python callback, just a memory address.  Python's garbage collector does not know about this.  If the Python object wrapping the callback is collected (because no Python variable refers to it anymore), the memory address becomes invalid, and the next time C calls it your program will crash or produce undefined behavior.  Always store callback objects in a variable that stays alive for as long as C might invoke them.

The FFI is bidirectional: not only can Python call C, but C can call Python functions (callbacks).  This is used for event handlers, sort comparators, and error handlers.

```python
import ctypes

# Define a C-compatible function type for a callback
# int (*comparator)(const void*, const void*)  -- used by qsort
COMPARATOR = ctypes.CFUNCTYPE(
    ctypes.c_int,         # return type
    ctypes.c_void_p,      # arg 1: const void*
    ctypes.c_void_p,      # arg 2: const void*
)

# Load libc for qsort
import sys
libc = ctypes.CDLL("libc.so.6" if sys.platform == "linux" else "libc.dylib")
libc.qsort.argtypes = [
    ctypes.c_void_p,   # base: pointer to array
    ctypes.c_size_t,   # nmemb: number of elements
    ctypes.c_size_t,   # size: size of each element
    COMPARATOR,        # compar: the callback
]
libc.qsort.restype = None

print("=== Python callback called by C's qsort ===")

call_count = [0]

def python_compare(a_ptr, b_ptr):
    """C calls this function with pointers to two ints."""
    call_count[0] += 1
    a = ctypes.cast(a_ptr, ctypes.POINTER(ctypes.c_int)).contents.value
    b = ctypes.cast(b_ptr, ctypes.POINTER(ctypes.c_int)).contents.value
    return (a > b) - (a < b)   # -1, 0, or 1

c_compare = COMPARATOR(python_compare)   # wrap Python fn in C function type

IntArray = ctypes.c_int * 8
data = IntArray(64, 12, 99, 3, 47, 28, 7, 55)
print(f"  Before sort: {list(data)}")

libc.qsort(data, len(data), ctypes.sizeof(ctypes.c_int), c_compare)
print(f"  After sort:  {list(data)}")
print(f"  Comparator called {call_count[0]} times")

print()
print("=== Callback memory management pitfall ===")
# CRITICAL: the C library holds a raw function pointer.
# If the Python callback object is garbage collected, the pointer becomes dangling.
# You MUST keep a reference to c_compare alive as long as C might call it.
print("  Danger: if c_compare is not kept alive, the function pointer is dangling!")
print("  Safe: store callbacks in a list that outlives the C call.")
callbacks = [c_compare]   # this reference keeps the callback alive

print()
print("=== Type-safe callback wrapper ===")
# A safer pattern: wrap in a class that manages the lifetime
class SafeCallback:
    def __init__(self, fn, c_type):
        self._fn = fn
        self._c_fn = c_type(fn)
    @property
    def c_ptr(self):
        return self._c_fn
    def __del__(self):
        print(f"  SafeCallback destroyed: {self._fn.__name__}")

def my_handler(x: int, y: int) -> int:
    return x - y

HANDLER = ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_int, ctypes.c_int)
cb = SafeCallback(my_handler, HANDLER)
print(f"  Direct test of callback: my_handler(10, 3) = {cb.c_ptr(10, 3)}")
```

> **Critical Thinking Questions 7-9**

**CTQ 7.** `COMPARATOR = ctypes.CFUNCTYPE(c_int, c_void_p, c_void_p)` describes the function signature.  What would happen if you passed a Python function with the wrong signature (e.g., one that takes only one argument instead of two)?

**CTQ 8.**  The comment warns: "if c_compare is garbage collected, the pointer becomes dangling."  Why can't Python's garbage collector know that C is holding a reference?  What would a language with linear types (like Rust) do differently?

**CTQ 9.** `qsort` calls the comparator multiple times on different pairs.  The comparator modifies `call_count`, a Python list (mutable container).  This works because Python closures capture by reference.  If the comparator modified a Python integer directly (`count = count + 1`), it would fail due to Python's scoping rules.  Why?  What does this reveal about closures and rebinding?

---

### Model 4: Name Mangling and Symbol Resolution

*Intuition:* When a program links against a library, it looks up function names in the library's *symbol table*, a dictionary inside the compiled binary.  C's symbol for `strlen` is literally the string `"strlen"`.  C++ cannot do this for overloaded functions: `foo(int)` and `foo(double)` both spell `foo`, but they are different functions with different machine code.  C++ solves this by *mangling* the name, encoding the parameter types into the symbol string so that `foo(int)` becomes something like `_ZN3foo1iE`.  This is the "name" the linker actually looks up.  FFI tools must understand mangling to call C++ functions correctly.

C uses simple symbol names (`strlen`, `printf`).  C++ mangles names to encode type signatures.  Understanding this is essential for building FFI tools.

```python
import ctypes
import ctypes.util
import sys

print("=== Finding shared library paths ===")
math_lib_name = ctypes.util.find_library("m")
c_lib_name    = ctypes.util.find_library("c")
print(f"  libm path: {math_lib_name}")
print(f"  libc path: {c_lib_name}")

print()
print("=== Dynamic symbol lookup ===")
if sys.platform != "win32":
    # RTLD_DEFAULT looks up symbols in all loaded libraries
    libc = ctypes.CDLL(None)    # None = look in all currently loaded libraries
    
    # Manually look up a symbol by name
    try:
        printf_ptr = ctypes.cast(
            ctypes.c_void_p.in_dll(libc, "printf") if hasattr(ctypes.c_void_p, 'in_dll')
            else None,
            ctypes.c_void_p
        )
        print(f"  printf found in libc")
    except (OSError, AttributeError):
        print("  (symbol inspection not available on this platform)")

print()
print("=== Python's own C API via ctypes ===")
# CPython exports its C API as a shared library (libpython)
# We can call internal Python C API functions - carefully!
py = ctypes.pythonapi

# PyList_New(Py_ssize_t len) -> PyObject*
py.PyList_New.restype = ctypes.py_object
py.PyList_New.argtypes = [ctypes.c_ssize_t]
new_list = py.PyList_New(0)
print(f"  PyList_New(0) via C API: {new_list!r}  type={type(new_list).__name__}")

# Py_GetVersion() -> const char*
py.Py_GetVersion.restype = ctypes.c_char_p
version_str = py.Py_GetVersion()
print(f"  Py_GetVersion(): {version_str.decode()[:50]}...")

print()
print("=== What C++ name mangling looks like ===")
# C++ compilers mangle function names to encode their full type signatures.
# 'void MyClass::foo(int, double)' might become '_ZN7MyClass3fooEid'
# Tools like 'c++filt' unmangle them.
# In Python, you can see this pattern by simulating it:
def mangle_simple(class_name: str, method_name: str, param_types: list) -> str:
    """Simplified Itanium ABI mangling (GNU/Clang style)."""
    type_codes = {"int": "i", "double": "d", "float": "f", "bool": "b",
                  "char": "c", "void": "v", "long": "l"}
    params = "".join(type_codes.get(t, "?") for t in param_types)
    n = len(class_name)
    m = len(method_name)
    return f"_ZN{n}{class_name}{m}{method_name}E{params}"

examples = [
    ("MyClass", "foo",    ["int", "double"]),
    ("Vector",  "push",   ["int"]),
    ("Matrix",  "mult",   ["double", "double"]),
]
print("  C++ name mangling (simplified):")
for cls, fn, params in examples:
    mangled = mangle_simple(cls, fn, params)
    print(f"    {cls}::{fn}({', '.join(params)}) -> {mangled}")
```

> **Critical Thinking Questions 10-12**

**CTQ 10.**  C's simple symbol names (`strlen`) mean that a shared library can only export one `strlen`.  C++ name mangling allows overloaded functions (`foo(int)` and `foo(double)`) to coexist in the same library.  What does this tell you about C's type system at the ABI level?

**CTQ 11.** `ctypes.CDLL(None)` loads symbols from all currently loaded libraries, including the Python interpreter itself.  Why is calling Python's internal C API this way dangerous?  What invariant must you preserve?

**CTQ 12.**  When writing an FFI for your mini language, you could either (a) call into C at the C ABI level (like ctypes) or (b) call Python functions directly.  Option (b) is simpler.  What would you lose by choosing (b) rather than (a)?  Under what circumstances would (a) be necessary?

---

### Model 5: Implementing a Simple FFI in a Mini Interpreter

*Intuition:* Now that you understand the mechanics of crossing the language boundary, you can add that crossing point to your own interpreter.  The key design decision is: what does an FFI call look like *in your language's syntax*, and how does the interpreter translate that into an actual call?  This model shows the minimum viable implementation: an `FfiCall` AST node carries the library name, function name, type annotations, and arguments.  The interpreter's `eval_node` function dispatches it to a registry that handles the marshaling.  Even a simple version like this is enough to give your mini language access to the entire C standard library.

A language interpreter can support FFI by letting programs call Python built-ins or C functions by name.  Here is a minimal implementation.

```python
from dataclasses import dataclass, field
from typing import Any, Dict, Callable, List, Optional
import ctypes
import sys

@dataclass
class FfiCall:
    """AST node: call a foreign function by name with given arguments."""
    lib_name: str
    func_name: str
    arg_types: List[str]   # e.g., ["int", "int"]
    ret_type: str           # e.g., "int"
    args: List[Any]        # evaluated argument AST nodes

@dataclass
class Num:
    value: float

@dataclass
class Str_:
    value: str

class FFIRegistry:
    """Manages loaded libraries and their function signatures."""
    CTYPES_MAP = {
        "int":    ctypes.c_int,
        "long":   ctypes.c_long,
        "double": ctypes.c_double,
        "float":  ctypes.c_float,
        "str":    ctypes.c_char_p,
        "void":   None,
    }

    def __init__(self):
        self._libs: Dict[str, Any] = {}
        self._python_fns: Dict[str, Callable] = {}
        # Pre-load safe Python built-ins as "python" library
        self._python_fns.update({
            "abs":   abs,
            "len":   len,
            "str":   str,
            "int":   int,
            "float": float,
            "max":   max,
            "min":   min,
        })

    def load_lib(self, name: str, path: str):
        self._libs[name] = ctypes.CDLL(path)

    def call(self, lib_name: str, func_name: str,
             arg_types: List[str], ret_type: str, args: List[Any]) -> Any:
        if lib_name == "python":
            fn = self._python_fns.get(func_name)
            if fn is None:
                raise NameError(f"python.{func_name} not in FFI registry")
            return fn(*args)
        
        lib = self._libs.get(lib_name)
        if lib is None:
            raise ImportError(f"Library {lib_name!r} not loaded")
        
        fn = getattr(lib, func_name)
        fn.argtypes = [self.CTYPES_MAP[t] for t in arg_types]
        fn.restype  = self.CTYPES_MAP.get(ret_type, ctypes.c_int)
        
        # Convert Python values to C values
        c_args = []
        for val, t in zip(args, arg_types):
            if t == "str":
                c_args.append(val.encode() if isinstance(val, str) else val)
            else:
                c_args.append(val)
        
        result = fn(*c_args)
        if isinstance(result, bytes):
            return result.decode()
        return result

def eval_node(node, env, ffi: FFIRegistry):
    if isinstance(node, Num):
        return node.value
    if isinstance(node, Str_):
        return node.value
    if isinstance(node, FfiCall):
        evaluated_args = [eval_node(a, env, ffi) for a in node.args]
        return ffi.call(node.lib_name, node.func_name,
                        node.arg_types, node.ret_type, evaluated_args)
    raise ValueError(f"unknown node: {node!r}")

ffi = FFIRegistry()

# Load libc for math operations
if sys.platform == "linux":
    ffi.load_lib("libc", "libc.so.6")
    ffi.load_lib("libm", "libm.so.6")
elif sys.platform == "darwin":
    ffi.load_lib("libc", "libc.dylib")
    ffi.load_lib("libm", "libm.dylib")

print("=== Mini interpreter FFI calls ===")

env = {}

# call python.abs(-42) -> int
call_abs = FfiCall("python", "abs", ["int"], "int", [Num(-42)])
print(f"  python.abs(-42) = {eval_node(call_abs, env, ffi)}")

# call python.max(3, 7) -> int
call_max = FfiCall("python", "max", ["int", "int"], "int", [Num(3), Num(7)])
print(f"  python.max(3, 7) = {eval_node(call_max, env, ffi)}")

# call libc.strlen("hello") -> int (only on Linux/Mac)
if sys.platform in ("linux", "darwin"):
    call_strlen = FfiCall("libc", "strlen", ["str"], "int", [Str_("hello world")])
    print(f"  libc.strlen('hello world') = {eval_node(call_strlen, env, ffi)}")
    
    call_sqrt = FfiCall("libm" if sys.platform == "linux" else "libc",
                        "sqrt", ["double"], "double", [Num(9.0)])
    try:
        print(f"  sqrt(9.0) = {eval_node(call_sqrt, env, ffi)}")
    except Exception as e:
        print(f"  (sqrt not available: {e})")

print()
print("=== FFI in language syntax (hypothetical) ===")
print("  Your language could expose FFI as a built-in statement:")
print("  ffi load 'libc.so.6' as libc;")
print("  let n = ffi call libc.strlen(str: 'hello');")
print("  print n;   # 5")
```

> **Critical Thinking Questions 13-15**

**CTQ 13.**  The `FFIRegistry` uses a "Python" pseudo-library for safe built-ins and C libraries for native code.  What is the advantage of keeping these in the same `FfiCall` AST node vs. having separate `NativeFn` and `PythonFn` nodes?

**CTQ 14.**  FFI calls bypass your interpreter's type checker.  A language-level type error (e.g., passing a string where `c_int` is expected) will become a ctypes exception rather than a friendly language error.  How would you add a "type gate" to the FFI call path?

**CTQ 15.**  A language with FFI can call any C function, including `malloc`, `free`, `exec`, and `system`.  This breaks memory safety and security.  How do languages like Haskell (via `Foreign.Unsafe`) or Rust (via `unsafe`) signal that FFI code requires special trust?

---

### Multiple Choice Review

**Question 1.** `ctypes.c_char_p` in Python represents:

- A Python `str` object
- A C-style null-terminated `char*` pointer, accepting `bytes`
- A single character (1 byte)
- A wide character (2 bytes) for Unicode

<details><summary>Answer</summary>

A C-style null-terminated `char*` pointer, accepting `bytes`

</details>

**Question 2.**  When a C function takes a struct by value, the caller:

- Copies the entire struct onto the stack (or into registers per ABI)
- Passes a pointer to the struct, which C dereferences automatically
- Converts the struct to a byte string first
- Returns an error unless the struct is marked `extern "C"`

<details><summary>Answer</summary>

Copies the entire struct onto the stack (or into registers per ABI)

</details>

**Question 3.**  C++ name mangling is needed because:

- C++ is compiled to a different object format than C
- C++ allows function overloading, so multiple functions can have the same name but different parameter types
- The linker requires all symbols to be prefixed with the namespace
- C++ uses a garbage collector that must track all function names

<details><summary>Answer</summary>

C++ allows function overloading, so multiple functions can have the same name but different parameter types

</details>

**Question 4.**  Keeping a reference to a `ctypes.CFUNCTYPE` callback alive while C might call it is necessary because:

- ctypes functions are reference-counted independently
- Python's garbage collector will free the callback if no Python reference remains, leaving C with a dangling pointer
- C copies the function body into its own memory on first call
- ctypes registers all callbacks globally and they are never freed

<details><summary>Answer</summary>

Python's garbage collector will free the callback if no Python reference remains, leaving C with a dangling pointer

</details>

---

### Exercises

**Exercise 1.**  Use `ctypes` to call C's `qsort` with a Python comparator that sorts strings by length (shortest first), falling back to lexicographic order for equal-length strings:

```python
import ctypes
import sys

if sys.platform not in ("linux", "darwin"):
    print("Skipping: not Linux/macOS")
else:
    libc = ctypes.CDLL("libc.so.6" if sys.platform == "linux" else "libc.dylib")
    
    # qsort signature: void qsort(void *base, size_t nmemb, size_t size,
    #                             int (*compar)(const void *, const void *))
    COMP = ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_void_p, ctypes.c_void_p)
    
    words = ["banana", "kiwi", "apple", "fig", "cherry", "date"]
    
    # To qsort strings, we'll sort indices and use Python for the comparison
    indices = list(range(len(words)))
    IdxArray = ctypes.c_int * len(indices)
    c_indices = IdxArray(*indices)
    
    def compare_by_length(a_ptr, b_ptr):
        a_idx = ctypes.cast(a_ptr, ctypes.POINTER(ctypes.c_int)).contents.value
        b_idx = ctypes.cast(b_ptr, ctypes.POINTER(ctypes.c_int)).contents.value
        wa, wb = words[a_idx], words[b_idx]
        if len(wa) != len(wb):
            return len(wa) - len(wb)
        return (wa > wb) - (wa < wb)
    
    comp_fn = COMP(compare_by_length)
    libc.qsort.argtypes = [ctypes.c_void_p, ctypes.c_size_t,
                           ctypes.c_size_t, COMP]
    libc.qsort.restype = None
    libc.qsort(c_indices, len(c_indices), ctypes.sizeof(ctypes.c_int), comp_fn)
    
    sorted_words = [words[c_indices[i]] for i in range(len(c_indices))]
    print(f"Sorted by length: {sorted_words}")
```

**Exercise 2.**  Extend the `FFIRegistry` from Model 5 to support type coercion and better error messages.  Add a `validate_and_coerce` method that checks types and converts Python values:

```python
import ctypes
import sys

class SafeFFIRegistry:
    CTYPES_MAP = {
        "int":    ctypes.c_int,
        "double": ctypes.c_double,
        "str":    ctypes.c_char_p,
    }
    PYTHON_TYPES = {
        "int":    (int, float),
        "double": (int, float),
        "str":    (str, bytes),
    }
    
    def __init__(self):
        self._python_fns = {
            "abs": abs, "max": max, "min": min,
            "len": len, "str": str, "int": int,
        }

    def validate_and_coerce(self, val, expected_type: str):
        if expected_type not in self.PYTHON_TYPES:
            raise TypeError(f"Unknown FFI type: {expected_type!r}")
        allowed = self.PYTHON_TYPES[expected_type]
        if not isinstance(val, allowed):
            raise TypeError(
                f"FFI type mismatch: expected {expected_type} "
                f"(Python {allowed}), got {type(val).__name__}"
            )
        if expected_type == "str" and isinstance(val, str):
            return val.encode()
        if expected_type == "int" and isinstance(val, float):
            if val != int(val):
                raise ValueError(f"Cannot coerce {val} to int without precision loss")
            return int(val)
        return val

    def call_python(self, func_name: str, arg_types: list, args: list):
        fn = self._python_fns.get(func_name)
        if fn is None:
            raise NameError(f"python.{func_name} not registered")
        coerced = [self.validate_and_coerce(v, t) for v, t in zip(args, arg_types)]
        return fn(*coerced)

ffi = SafeFFIRegistry()

print("=== Safe FFI with type validation ===")

# Valid calls
for fn, types, args in [
    ("abs",   ["int"],        [-42]),
    ("max",   ["int", "int"], [3, 7]),
    ("len",   ["str"],        ["hello"]),
]:
    result = ffi.call_python(fn, types, args)
    print(f"  python.{fn}({args}) = {result}")

# Invalid calls (should produce clear errors)
bad_calls = [
    ("abs",   ["int"],  ["not_a_number"]),
    ("max",   ["int", "int"], [3.5, 7]),
]
for fn, types, args in bad_calls:
    try:
        ffi.call_python(fn, types, args)
    except (TypeError, ValueError) as e:
        print(f"  python.{fn}({args}) -> {type(e).__name__}: {e}")
```

**Exercise 3.**  Implement a minimal "safe FFI" for your mini language that allows calling Python's `math` module functions.  Add lexer/parser support for the syntax `ffi("math", "sqrt", 9.0)`:

```python
import math
import re
from dataclasses import dataclass
from typing import Any, List

@dataclass
class FfiExpr:
    module: str
    func_name: str
    args: List[Any]

SAFE_MODULES = {
    "math": math,
    "os.path": __import__("os.path"),
}

def eval_ffi(node: FfiExpr):
    mod = SAFE_MODULES.get(node.module)
    if mod is None:
        raise ImportError(f"Module {node.module!r} not in FFI allowlist")
    fn = getattr(mod, node.func_name, None)
    if fn is None:
        raise AttributeError(f"{node.module}.{node.func_name} not found")
    return fn(*node.args)

# Simulate parsing 'ffi("math", "sqrt", 9.0)'
def parse_ffi_call(src: str) -> FfiExpr:
    m = re.match(r'ffi\("([^"]+)",\s*"([^"]+)"((?:,\s*[\d.]+)*)\)', src)
    if not m:
        raise SyntaxError(f"Invalid ffi call: {src!r}")
    module, fn_name = m.group(1), m.group(2)
    args_str = m.group(3)
    args = [float(a.strip()) for a in args_str.split(",") if a.strip()]
    return FfiExpr(module, fn_name, args)

test_calls = [
    'ffi("math", "sqrt", 25.0)',
    'ffi("math", "floor", 3.7)',
    'ffi("math", "pow", 2.0, 10.0)',
]

print("=== Safe FFI for math module ===")
for src in test_calls:
    node = parse_ffi_call(src)
    result = eval_ffi(node)
    print(f"  {src} = {result}")

# Security: try to call an unsafe module
try:
    bad = FfiExpr("os", "system", ["rm -rf /"])
    eval_ffi(bad)
except ImportError as e:
    print(f"\n  Security block: {e}")
```

---

### Reflection

1.  The FFI is fundamentally an "escape hatch" from your language's safety guarantees.  A type-safe language can call unsafe C code via FFI. How do language designers manage this tension?  Name the strategies used by Python, Haskell, and Rust respectively.

2.  Your mini interpreter runs Python as its host language.  This means your "FFI" to Python is essentially free; you can call any Python function.  But if your language was a compiled language generating machine code, FFI would require real ABI compatibility.  What would change in your implementation?

3.  The `SAFE_MODULES` allowlist in Exercise 3 prevents calling `os.system` via FFI. Is a whitelist the right security model for an FFI? What are the limitations of this approach?

---

### Further Reading

- **Python docs:** `ctypes`: A foreign function library for Python
- **Python docs:** `cffi`: C Foreign Function Interface for Python (higher-level alternative to ctypes)
- **Article:** *How Python calls C*: deep dive into CPython's API
- **Rust book:** Chapter, "Unsafe Rust": `extern "C"` and `unsafe fn`
- **Haskell wiki:** `Foreign Function Interface`: `Foreign.Ptr`, `Foreign.Marshal`
- **Paper:** *A Semantic Framework for C (and the Rest)*: Norrish (1998), the formal semantics behind C's ABI behavior
- **Talk:** Brandon Williams, "ctypes Without the Boilerplate": automating struct generation from C headers

---

*End of Tutorial, Advanced C++: Modern Memory, Templates, and the STL*
*CS374 Principles of Programming Languages, Ursinus College, Fall 2026*
