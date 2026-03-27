---
layout: activity
permalink: /Activities/ModernFeatures
title: "CS374: Programming Language Principles - Modern Language Features"


info: 
  goals: 
    - To utilize modern language features for working with memory
    - To explain the concept of scope
    - To explain the purpose of object references
    - To time and compare different architectural approaches
  models: 
    - model: |
        <script type="syntaxhighlighter" class="brush: cpp"><![CDATA[
        #include <iostream>
        #include <memory>

        // Resource class with additional fields
        class Resource {
        public:
          int data;
          std::string name;

          Resource(int d, std::string n) : data(d), name(n) {
            std::cout << "Resource acquired: " << name << "\n";
          }
          ~Resource() { std::cout << "Resource destroyed: " << name << "\n"; }
        };

        // Function that manipulates the resource via a reference to the unique_ptr
        void update_resource(std::unique_ptr<Resource> &res) {
          std::cout << "Manipulating resource: " << res->name << "\n";
          res->data += 10; // Modify the data field
          std::cout << "Updated data: " << res->data << "\n";
          res->name = "Updated " + res->name; // Modify the name field
          std::cout << "Updated name: " << res->name << "\n";
        }

        int main() {
          // Create a unique_ptr to a Resource object
          std::unique_ptr<Resource> resPtr =
              std::make_unique<Resource>(42, "TestResource");

          // Pass the unique_ptr by reference to a function that manipulates it
          // if you'd like resPtr to become deallocated and null after this call, you
          // can pass std::move(resPtr) instead, and not pass by reference; this
          // transfers ownership of the resource to the function
          update_resource(resPtr);

          // The resource can still be accessed in main
          std::cout << "Resource in main after update:\n";
          std::cout << "Name: " << resPtr->name << ", Data: " << resPtr->data << "\n";

          return 0;
        }
        ]]></script> 
      title: "C++ Unique Pointers"
      questions:
        - "What does this code do?"
        - "What does this code have in common with traditional pointers?  What would you have to do differently if you were creating the pointers yourself?"
        - "What do you think <code>std::move</code> does?"
        - "What benefits does <code>std::unique_ptr</code> provide?"
    - model: |
        <script type="syntaxhighlighter" class="brush: cpp"><![CDATA[
        #include <iostream>
        #include <memory>

        // Resource class with additional fields
        class Resource {
        public:
          int data;
          std::string name;

          Resource(int d, std::string n) : data(d), name(n) {
            std::cout << "Resource acquired: " << name << "\n";
          }
          ~Resource() { std::cout << "Resource destroyed: " << name << "\n"; }
        };

        // Function that takes a shared_ptr and updates the resource
        void update_resource_data(std::shared_ptr<Resource> res, int value) {
          std::cout << "Updating resource data in function 1...\n";
          res->data += value; // Modify the data field
          std::cout << "Data after update: " << res->data << "\n";
        }

        // Function that takes a shared_ptr and modifies the name
        void update_resource_name(std::shared_ptr<Resource> res,
                                  const std::string &newName) {
          std::cout << "Updating resource name in function 2...\n";
          res->name = newName; // Modify the name field
          std::cout << "Name after update: " << res->name << "\n";
        }

        int main() {
          std::shared_ptr<Resource> resPtr1;
          {
            // Block scope to show shared_ptr behavior
            std::shared_ptr<Resource> resPtr2 =
                std::make_shared<Resource>(42, "SharedResource");
            resPtr1 = resPtr2; // Now resPtr1 shares ownership with resPtr2

            // Pass resPtr2 to a function that updates the resource data
            update_resource_data(resPtr2, 10);

            // Block ends here, but resource is still alive because resPtr1 also owns it
          }

          // resPtr1 is still valid, even though resPtr2 has gone out of scope
          update_resource_name(resPtr1, "UpdatedResourceName");

          // Print the final state of the resource in main
          std::cout << "Final Resource state in main:\n";
          std::cout << "Name: " << resPtr1->name << ", Data: " << resPtr1->data << "\n";

          return 0;
        }
        ]]></script> 
      title: "C++ Shared Pointers"
      questions:
        - "What is the purpose of the extra curly braces inside <code>main</code>?"
        - "When <code>resPtr1</code> goes out of scope, why is the underlying memory still accessible?"
        - "In your own words, what is the benefit of a <code>std::shared_ptr</code>?"
    - model: |
        <script type="syntaxhighlighter" class="brush: cpp"><![CDATA[
        #include <iostream>
        #include <memory>
        #include <vector>

        class Widget {
        public:
          Widget(int id) : id(id) { std::cout << "Widget " << id << " created.\n"; }

          ~Widget() { std::cout << "Widget " << id << " destroyed.\n"; }

          void display() const { std::cout << "Widget ID: " << id << "\n"; }

        private:
          int id;
        };

        int main() {
          // Create a vector to store shared_ptrs to Widgets
          std::vector<std::shared_ptr<Widget>> widgets;

          // Adding new Widgets to the vector using shared_ptr
          widgets.push_back(std::make_shared<Widget>(1));
          widgets.push_back(std::make_shared<Widget>(2));
          widgets.push_back(std::make_shared<Widget>(3));

          // Displaying all Widgets
          std::cout << "Displaying Widgets:\n";
          for (const auto &widgetPtr : widgets) {
            widgetPtr->display();
          }

          // Simulate shared ownership by copying a shared_ptr from the vector
          std::shared_ptr<Widget> anotherWidgetPtr = widgets[1];

          std::cout << "Removing the second Widget from the vector.\n";
          widgets.erase(widgets.begin() + 1);

          // Despite removing from the vector, the Widget object is still alive
          std::cout << "Widget in anotherWidgetPtr is still alive:\n";
          anotherWidgetPtr->display();

          std::cout << "Remaining Widgets in the vector:\n";
          for (const auto &widgetPtr : widgets) {
            widgetPtr->display();
          }

          // When main exits, all remaining Widgets will be destroyed as their
          // shared_ptr reference counts drop to zero.
          return 0;
        }
        ]]></script> 
      title: "Vectors and the C++ Standard Template Library"
      questions:
        - "What do you think the <code>auto</code> type means?  How do you think it works?"
        - "Why is <code>anotherWidgetPtr</code> still accessible after removing it from the <code>vector</code>?"
    - model: |
        <script type="syntaxhighlighter" class="brush: cpp"><![CDATA[
        #include <chrono>
        #include <iostream>

        // note: set -fconstexpr-steps= in CXXFLAGS to set the number of constexpr
        // compile steps, and -O0 to disable other compiler optimizations

        // Regular function to calculate binomial coefficient
        unsigned long long binomial_coeff_non_constexpr(int n, int k) {
          return (k == 0 || k == n) ? 1
                                    : binomial_coeff_non_constexpr(n - 1, k - 1) +
                                          binomial_coeff_non_constexpr(n - 1, k);
        }

        // Constexpr function to calculate binomial coefficient
        constexpr unsigned long long binomial_coeff_constexpr(int n, int k) {
          return (k == 0 || k == n) ? 1
                                    : binomial_coeff_constexpr(n - 1, k - 1) +
                                          binomial_coeff_constexpr(n - 1, k);
        }

        int main() {
          int n = 25;
          int k = 15;
          constexpr int n_constexpr = 25;
          constexpr int k_constexpr = 15;

          // Timing non-constexpr version
          std::cout << "Testing non-constexpr version...\n";
          auto start_non_constexpr = std::chrono::high_resolution_clock::now();
          unsigned long long result_non_constexpr = binomial_coeff_non_constexpr(n, k);
          auto end_non_constexpr = std::chrono::high_resolution_clock::now();

          std::chrono::duration<double> elapsed_non_constexpr =
              end_non_constexpr - start_non_constexpr;
          std::cout << "Binomial Coefficient (non-constexpr) of " << n << " choose "
                    << k << " is " << result_non_constexpr << "\n";
          std::cout << "Time taken: " << elapsed_non_constexpr.count() << " seconds\n";

          // Displaying constexpr result
          std::cout << "\nDisplaying constexpr result...\n";
          constexpr unsigned long long result_constexpr = binomial_coeff_constexpr(
              n_constexpr, k_constexpr); // Computed at compile-time
          std::cout << "Binomial Coefficient (constexpr) of " << n << " choose " << k
                    << " is " << result_constexpr << "\n";
          std::cout << "Time taken: 0.0 seconds (computed at compile-time)\n";

          return 0;
        }
        ]]></script> 
      title: "C++ Constant Expressions"
      questions:
        - "Try this code for various values of <code>n</code> and <code>k</code>.  Which program is faster?"  
        - "What do you notice when compiling this program?  Why do you think this is?  What is the compromise?"
        - "What, in your own words, does <code>constexpr</code> do?"
        - "What do you think the compiler flag <code>constexpr-steps</code> means?"
        
tags:
  - modernfeatures
  
---

# Smart Pointer Examples: Before and After

<h2>Example 1: Using <code>unique_ptr</code> instead of Raw Pointers</h2>
<table>
  <thead>
    <tr>
      <th>Before: Raw Pointers</th>
      <th>After: <code>unique_ptr</code></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>
        <pre><code>#include &lt;iostream&gt;

class Resource {
public:
    Resource() { std::cout &lt;&lt; "Resource acquired\n"; }
    ~Resource() { std::cout &lt;&lt; "Resource destroyed\n"; }
    void say_hello() const { std::cout &lt;&lt; "Hello from Resource\n"; }
};

void raw_pointer_example() {
    Resource* res = new Resource();
    res-&gt;say_hello();

    // Simulate transferring ownership (forgetting to delete might cause a memory leak)
    Resource* res2 = res;
    res = nullptr;

    // Resource cleanup
    delete res2; // If we forget this, it causes a memory leak.
}

int main() {
    raw_pointer_example();
    return 0;
}
</code></pre>
      </td>
      <td>
        <pre><code>#include &lt;iostream&gt;
#include &lt;memory&gt;  // For std::unique_ptr

class Resource {
public:
    Resource() { std::cout &lt;&lt; "Resource acquired\n"; }
    ~Resource() { std::cout &lt;&lt; "Resource destroyed\n"; }
    void say_hello() const { std::cout &lt;&lt; "Hello from Resource\n"; }
};

void unique_pointer_example() {
    std::unique_ptr&lt;Resource&gt; res = std::make_unique&lt;Resource&gt;();
    res-&gt;say_hello();

    // Transferring ownership with std::move
    std::unique_ptr&lt;Resource&gt; res2 = std::move(res);

    // No need to manually delete, as unique_ptr handles this automatically
    // Resource will be destroyed when res2 goes out of scope
}

int main() {
    unique_pointer_example();
    return 0;
}
</code></pre>
      </td>
    </tr>
  </tbody>
</table>

<h2>Example 2: Using <code>shared_ptr</code> instead of Raw Pointers</h2>
<table>
  <thead>
    <tr>
      <th>Before: Raw Pointers</th>
      <th>After: <code>shared_ptr</code></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>
        <pre><code>#include &lt;iostream&gt;

class Resource {
public:
    Resource() { std::cout &lt;&lt; "Resource acquired\n"; }
    ~Resource() { std::cout &lt;&lt; "Resource destroyed\n"; }
    void say_hello() const { std::cout &lt;&lt; "Hello from Resource\n"; }
};

void raw_pointer_shared_example() {
    Resource* res = new Resource();

    // Multiple "owners" of the same resource
    Resource* res1 = res;
    Resource* res2 = res;

    res1-&gt;say_hello();
    res2-&gt;say_hello();

    // Manually managing cleanup
    delete res1;  // Deleting res1 here makes res2 a dangling pointer
    // delete res2;  // If uncommented, this would cause undefined behavior (double delete)
}

int main() {
    raw_pointer_shared_example();
    return 0;
}
</code></pre>
      </td>
      <td>
        <pre><code>#include &lt;iostream&gt;
#include &lt;memory&gt;  // For std::shared_ptr

class Resource {
public:
    Resource() { std::cout &lt;&lt; "Resource acquired\n"; }
    ~Resource() { std::cout &lt;&lt; "Resource destroyed\n"; }
    void say_hello() const { std::cout &lt;&lt; "Hello from Resource\n"; }
};

void shared_pointer_example() {
    std::shared_ptr&lt;Resource&gt; res = std::make_shared&lt;Resource&gt;();

    // Multiple shared_ptr instances share ownership of the same resource
    std::shared_ptr&lt;Resource&gt; res1 = res;
    std::shared_ptr&lt;Resource&gt; res2 = res;

    res1-&gt;say_hello();
    res2-&gt;say_hello();

    // No need to manually delete; the resource is automatically deleted
    // when the last shared_ptr (res, res1, or res2) goes out of scope
}

int main() {
    shared_pointer_example();
    return 0;
}
</code></pre>
      </td>
    </tr>
  </tbody>
</table>
