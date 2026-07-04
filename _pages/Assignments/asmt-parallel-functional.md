---
layout: assignment
permalink: Assignments/ParallelFunctional
title: "Assignment: Massively Parallel Data Processing with Pure Functions"

info:
  points: 100
  goals:
    - "Demonstrate that pure functions parallelize safely without synchronization."
    - "Implement a complete MapReduce pipeline in Python using multiprocessing."
    - "Measure and explain parallel speedup, efficiency, and scaling behavior."
    - "Identify the bottlenecks that limit parallel speedup (Amdahl's Law)."
    - "Design pure functions for a real dataset of meaningful size."
    - "Connect the functional programming model to distributed computing architectures."
  purpose: "The promise of functional programming is that purity buys you parallelism for free. This assignment cashes that promise on a real dataset: you will implement a complete MapReduce pipeline, parallelize it across all available CPU cores, measure how it scales, and confront the practical limits (serialization overhead, non-parallelizable reduce phases) that constrain real distributed systems. The goal is not just to make a program faster — it is to experience, in a grounded and quantified way, why the design choice of purity has engineering consequences at scale."
  tasks:
    - "Implement a pure map function for text analysis on a corpus of at least 10,000 lines."
    - "Implement a parallel map using Python's multiprocessing.Pool."
    - "Implement a tree-reduce that parallelizes the combining phase."
    - "Measure sequential and parallel times; compute speedup and efficiency."
    - "Implement a second pipeline for a domain of your choice."
    - "Analyze Amdahl's Law bounds on your measured speedup."
    - "Document every design decision with a justification in terms of purity and parallelism."
  rubric:
    - weight: 30
      description: Parallel Map Implementation
      preemerging: The parallel map is absent or is sequential (no actual parallelism).
      beginning: A Pool.map call is present but the function passed is impure (reads or writes shared state), or the results are not verified to match the sequential version.
      progressing: The parallel map uses Pool.map with a demonstrably pure function; results are verified equal to the sequential version; basic timing is measured.
      proficient: The parallel map is correct and verified; timing is measured with the timeit or time module over at least five runs per configuration; chunk size is explored as a parameter with results reported; the function's purity is argued in the writeup.
    - weight: 25
      description: Speedup Analysis and Amdahl's Law
      preemerging: No timing data or analysis is present.
      beginning: Sequential and parallel times are measured but no speedup ratio is computed or discussed.
      progressing: Speedup ratios are computed for the map phase; a scaling experiment uses 1, 2, 4, and 8 (or max available) workers; results are tabulated.
      proficient: Speedup and efficiency (speedup / workers) are computed and plotted or tabulated for all worker counts; Amdahl's Law is applied: the serial fraction f is estimated from measured data; the theoretical maximum speedup is computed and compared to measured results; discrepancies are explained (serialization overhead, process spawn cost, GIL considerations, OS scheduling).
    - weight: 20
      description: Tree-Reduce and Full Pipeline
      preemerging: Only the map phase is implemented; the reduce phase is sequential.
      beginning: A sequential reduce is used after the parallel map; the pipeline produces correct results.
      progressing: The reduce is implemented as a binary tree fold that can parallelize pairs of partial results; the full pipeline (parallel map, tree reduce) is correct on the text analysis task.
      proficient: The tree-reduce is implemented and its parallelism is measured; the report explains why the reduce phase scales less well than the map phase, using the associativity requirement and the data dependency graph as evidence; the pipeline handles edge cases (empty corpus, single document, very large document).
    - weight: 15
      description: Second Pipeline
      preemerging: The second pipeline is absent.
      beginning: A second pipeline is present but is a trivial variation (e.g., same word count with a different corpus).
      progressing: The second pipeline addresses a different domain with a different pure function and demonstrates that the same parallel scaffolding applies.
      proficient: The second pipeline is for a domain the student finds genuinely interesting; the writeup explains why the map function is pure, how parallelism benefits this domain, and what the real-world application would look like at 1000x the data size.
    - weight: 10
      description: Documentation and Analysis Quality
      preemerging: The writeup is absent or consists of code without explanation.
      beginning: The writeup describes what the code does without explaining design choices.
      progressing: The writeup argues for the design choices made (why each function is pure, why chunk size was chosen, why a particular aggregation was used).
      proficient: The writeup is a technical document that a reader unfamiliar with your code could follow; it includes a section on "what I would do differently at 1000x scale" that engages with distributed systems concepts (partitioning, fault tolerance, data locality) at the level of the MapReduce paper.

tags:
  - functional-programming
  - parallelism
  - mapreduce
  - python
  - performance
---

## Assignment: Massively Parallel Data Processing with Pure Functions

The Google MapReduce paper (Dean and Ghemawat, 2004) opens with a single observation: when you write a computation as a map over independent inputs followed by a reduce over results, the framework can parallelize it automatically. You do not coordinate threads. You do not write locks. You describe what to compute, not how to coordinate. This assignment is your personal version of that paper: a real corpus, a real pipeline, real measurements, and a real analysis of why the functional model enables what the imperative model makes hard.

---

### Dataset

You will use the **Project Gutenberg** plain-text version of *Moby Dick* (approximately 21,000 lines) as your primary corpus. Download the text from the course files directory or from Project Gutenberg directly.

Split the text into lines for the map phase. Each line is one "document" in the MapReduce sense.

---

### Part 1: The Sequential Baseline (15 points)

Before parallelizing, implement and test the sequential versions of:

1. `word_frequencies(line: str) -> dict[str, int]` — given a single line, return a dictionary mapping each lowercase alphabetic word to its count. This is your **map function**. Argue in writing that this function is pure: it reads no global state, modifies no shared structure, and returns the same output for the same input regardless of when or where it is called.

2. `merge_counts(a: dict, b: dict) -> dict` — given two word-count dictionaries, return a new dictionary with the combined counts. This is your **reduce function**. Argue that it is pure and associative. Why does associativity matter for parallelism?

3. `top_n(counts: dict, n: int) -> list[tuple[str, int]]` — return the `n` most frequent words as a list of (word, count) pairs, sorted descending by count.

4. Run the full sequential pipeline on *Moby Dick*. Report: total words, unique words, top-20 most frequent words, total runtime.

---

### Part 2: Parallel Map (30 points)

Replace the sequential `map(word_frequencies, lines)` with `Pool.map(word_frequencies, lines)`.

**2a. Implementation.** Use `multiprocessing.Pool`. The `word_frequencies` function must be a module-level function (not a lambda or local function) to be picklable across processes.

**2b. Correctness verification.** Assert that the parallel result equals the sequential result. Report both results and confirm agreement.

**2c. Timing experiment.** Measure wall-clock time for the map phase with the following configurations:

| Workers | Chunk Size | Time (s) | Speedup |
|---------|------------|---------|---------|
| 1 (sequential baseline) | — | | 1.0x |
| 2 | default | | |
| 4 | default | | |
| max available | default | | |
| max available | 10 | | |
| max available | 100 | | |
| max available | 1000 | | |

Use `timeit.timeit` with `number=5` and report the mean.

**2d. Analysis.** Compute efficiency $= \text{speedup} / \text{workers}$ for each configuration. At what worker count does efficiency drop below 0.8? Why? What effect does chunk size have, and why?

---

### Part 3: Tree-Reduce (20 points)

The sequential `reduce(merge_counts, results, {})` processes results one at a time: $O(n)$ sequential operations. A **tree reduce** pairs up results and merges pairs in parallel, then pairs up the merged results, and so on — $O(\log n)$ rounds of parallel work.

**3a. Implement `tree_reduce(merge_fn, results)`.** In each round, pair up adjacent elements, merge each pair (using `Pool.map(merge_fn_pair, pairs)`), and repeat until one result remains. If the number of elements is odd, carry the last element forward unpaired.

**3b. Verify** that `tree_reduce(merge_counts, word_maps)` produces the same result as the sequential reduce.

**3c. Measure and compare** the time for sequential reduce vs. tree-reduce on the full *Moby Dick* word maps.

**3d. Analysis.** The tree-reduce parallelizes the reduce phase, but each round requires synchronization before the next round begins. Draw a diagram showing the dependency graph of a tree-reduce over 8 elements. How many rounds are required? What is the maximum parallel speedup achievable, regardless of how many cores you have? How does this relate to the serial fraction in Amdahl's Law?

---

### Part 4: Amdahl's Law Analysis (included in Part 2 points)

**Amdahl's Law** states that if a fraction $f$ of the computation is serial (cannot be parallelized), the maximum speedup with $n$ processors is:

$$
S(n) = \frac{1}{f + \frac{1-f}{n}}
$$

As $n \to \infty$, $S \to 1/f$. If 10% of your program is serial, the maximum speedup is 10x — even with infinite processors.

From your Part 2 timing data:
- Estimate the serial fraction $f$ of your pipeline. (Hint: use the formula $f \approx \frac{1/S_{\text{max}} - 1/n_{\text{max}}}{1 - 1/n_{\text{max}}}$ where $S_{\text{max}}$ is your best measured speedup and $n_{\text{max}}$ is the worker count.)
- Compute the theoretical maximum speedup for your estimated $f$.
- Identify the serial components: process spawn overhead, pickling/unpickling for IPC, the final sequential reduce, the `top_n` sort.
- If you were to scale to 100 workers, what speedup would Amdahl's Law predict? What does this imply about the viability of your pipeline at datacenter scale?

---

### Part 5: Second Pipeline — Your Domain (15 points)

Choose a domain you care about (biology, music, finance, social science, sports, or another area) and design a second MapReduce pipeline over a real or realistic dataset of at least 1,000 records.

Your pipeline must:
- Have a pure map function that processes one record and returns a value or key-value pair
- Have a pure, associative reduce function
- Produce a useful aggregate result

Include:
- The dataset description and source
- The pure map function, with a written argument for purity
- The pure reduce function, with a written argument for purity and associativity
- Results of running the full parallel pipeline
- A paragraph describing the real-world application at 10,000x the data size

---

### Part 6: Reflection Questions (10 points)

Answer each in 3–5 sentences:

1. **Race conditions.** Your word-frequency function is pure. If you instead maintained a global dictionary and updated it from multiple processes, what specific failure mode would occur? Why does Python's GIL not protect you in this case?

2. **Associativity and correctness.** The word-count merge function is associative. Construct a hypothetical reduce function that is NOT associative and show how a tree-reduce would produce wrong results with it.

3. **Functional design at scale.** The Google MapReduce paper reports that many complex data processing tasks at Google — web indexing, log analysis, machine learning feature extraction — fit naturally into MapReduce. What common property of these tasks makes them good fits for MapReduce, and what kinds of computations would be a poor fit?

---

### Deliverables

- **A written report** (PDF) containing:
  - The purity argument for each function (Parts 1, 5)
  - All timing tables and speedup analyses (Parts 2–4)
  - Amdahl's Law estimates and interpretation (Part 4)
  - Second pipeline description and results (Part 5)
  - Reflection answers (Part 6)
- **Python source files**: `pipeline.py` (Parts 1–4), `second_pipeline.py` (Part 5)
- **A `requirements.txt`** with all dependencies (likely only standard library)
- **A `README`** with exact commands to reproduce every result in the report

List your machine's CPU model and core count prominently; speedup numbers are meaningless without this context.

---

### Submission Instructions

Submit a single ZIP to the course LMS. Did you work with a buddy on this assignment? If so, who? If not, do you certify that this submission represents your own original work? Identify any portions not originally written by you.

Approximately how many hours did this assignment take?

---

### Reflection Prompts (Notebook)

- Your parallel pipeline ran the same word-frequency function thousands of times, on different data, simultaneously. Is there anything about this experience that changes how you think about functions — as mathematical objects that map inputs to outputs — versus functions as code that runs in sequence? Write a paragraph.
- The functional model separates *what* to compute from *how* to coordinate. Imperative parallel code forces you to specify both. Which abstraction level felt more comfortable to reason about, and why? What would you lose if you gave up the other?

---

### Resources

- The in-class module "Parallelism for Free: Functional Programming at Scale."
- Dean, Jeffrey and Sanjay Ghemawat. "MapReduce: Simplified Data Processing on Large Clusters." *OSDI '04*. Read the paper; it is beautifully written and directly applicable.
- Python `multiprocessing` documentation, especially `Pool.map` and the section on pickling requirements.
- Amdahl, Gene M. "Validity of the Single Processor Approach to Achieving Large Scale Computing Capabilities." *AFIPS '67*. The original paper, one page.
- Project Gutenberg plain text files: *Moby Dick* ISBN 2701 or any English-language text of your choice.
