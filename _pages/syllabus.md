---
layout: syllabus
permalink: /
title: "CS374: Principles of Programming Languages"

info:
  course_number: CS374
  course_sections:
  - section: "A"
  course_title: "Principles of Programming Languages"
  credit_hours: "4 Semester Hours"
  # The one per-term value in this file.  Every relative rlink/dlink below is
  # resolved against it by code/course/syllabus2ical.py and ursinus_canvas.py,
  # so updating this line (and baseurl in _config.yml) re-points the whole schedule.
  course_homepage: "https://www.billmongan.com/Ursinus-CS374-Fall2026/"
  teamshelproom: "https://teams.microsoft.com/l/team/19%3AraoRrj75t_Hao34_QVtu1F2Cg6czbvuGhzWdQz7VbRc1%40thread.tacv2/conversations?groupId=6abc67f1-e0c8-4245-9795-e27108d7af8f&tenantId=921f1c03-8689-4e60-a722-f5ea581e00fe"
  class_notebook: https://ursinuscollege365-my.sharepoint.com/personal/wmongan_ursinus_edu/Documents/Class%20Notebooks/CS374%20Fall%202026
  ical: files/CS374.ics
  course_prerequisites: "CS174 with a grade of C- or higher."
  course_start_date: "2026/08/24"
  course_end_date: "2026/12/08"
  course_description: "Syntax, processors, representations and styles of programming languages.  Study and comparison of several modern programming languages.  Prerequisite: A grade of C- or higher in CS-174.  Offered in the fall of even years.  Three hours per week.  Four semester hours."
  questions: |
    This semester, we build toward a single shared accomplishment: by December, your team will have designed and implemented a programming language of your own. Along the way, we will collectively consider questions like:
    <ul>
    <li>What makes a programming language a language, and how do grammars give precise meaning to syntax?</li>
    <li>How does source text become running behavior, from characters to tokens to trees to values?</li>
    <li>Why do languages differ in their treatment of names, scope, types, and state, and what do those differences cost or buy us?</li>
    <li>What can the lambda calculus, a language with almost nothing in it, teach us about languages that have everything?</li>
    <li>How do the languages we use shape the programs we can imagine writing, and who gets included or excluded by those design choices?</li>
    </ul>
  welcome_message: "Welcome to CS374!"
  class_meets_days:
    isM: false
    isT: true
    isW: false
    isR: true
    isF: false
    isS: false
    isU: false
  class_meets_locations:
  - section:
    - day: "T"
      starttime: "10:00 AM"
      endtime: "11:15 AM"
      place: "Pfahler 012"
    - day: "R"
      starttime: "10:00 AM"
      endtime: "11:15 AM"
      place: "Pfahler 012"
  # No midterm/final in this course.  "TBD" dates are the sentinel that suppresses
  # rendering and .ics events for these blocks, so do not delete them.
  midtermexam:
    - mdate: "TBD"
      mstarttime: "N/A"
      mendtime: "N/A"
      mroom: "N/A"       
  finalexam:
    - fdate: "TBD"
      fstarttime: "TBD"
      fendtime: "TBD"
      froom: "N/A"
  flexible_submission_policy: "In the absence of <a href=\"#accommodations\">accommodations</a> arranged in advance with the instructor or college, all assignments are due at 11:59 PM Eastern Time on the date(s) stated on the schedule.  With prior permission and a reasonable first draft submission by the deliverable deadline, any student may request a three day extension on any deliverable, as often as needed.  Assignments will be accepted without prior permission following the original deadline, or, if requested, following the three-day extension deadline, with a points deduction of 10% per day if submitted before 11:59 PM Eastern Time on the day submitted.  If a student adds the course late, deliverables due prior to or on the day of that student's registration will be due twice the number of days following the first day of the semester that they registered (for example, a student who registers on the third day of the semester shall receive six days to submit assignments from the first three days, and then the remainder of this policy takes effect for those and for all other deliverables).  Under no circumstances (including accommodations) can late work be accepted after the final class meeting, nor during final exams week, nor after the exam."
  late_penalty_per_period: 10
  late_penalty_period: "day"
  attendance: "Students may miss up to 4 classes without justification, although students are encouraged to communicate with me prior to missing class (or immediately after) so that we can discuss what was missed and how to catch up.  Any student who misses more than 4 classes will receive a full letter grade reduction for each subsequent class missed from the final letter grade.  A lateness to class shall count as one-half of an absence for purposes of this policy."  
  banner: |
    <div style="width: 100%; display: table; border-collapse:separate; border-spacing:5px;">
    <div style="width: 100%; display: table-row;">
        <div style="display: table-cell; padding:5px; width:33%;">
            <a title="SBCL team, urxvt team, Public domain, via Wikimedia Commons" href="https://commons.wikimedia.org/wiki/File:SBCL_screenshot.png"><img width="100%" style="display:block;" alt="SBCL screenshot" src="https://commons.wikimedia.org/w/index.php?title=Special:Redirect/file/SBCL_screenshot.png"></a>
        </div>
        <div style="display: table-cell; padding:5px; width:33%;">
            <a title="Dcoetzee, CC0, via Wikimedia Commons" href="https://commons.wikimedia.org/wiki/File:Abstract_syntax_tree_for_Euclidean_algorithm.svg"><img width="100%" style="display:block;" alt="Abstract syntax tree for Euclidean algorithm" src="https://commons.wikimedia.org/w/index.php?title=Special:Redirect/file/Abstract_syntax_tree_for_Euclidean_algorithm.svg"></a>        
        </div>
        <div style="display: table-cell; padding:5px; width:33%;">
            <a title="DevinCook at English Wikipedia, Public domain, via Wikimedia Commons" href="https://commons.wikimedia.org/wiki/File:Parser_Flow%D5%B8.gif"><img width="50%" style="display:block;" alt="Parser Flow" src="https://commons.wikimedia.org/w/index.php?title=Special:Redirect/file/Parser_Flow%D5%B8.gif"></a>
        </div>
    </div>
    </div>
    
university:
  semester: "Fall"
  academicyear: "2026-27"
  fall:
  - kname: "Add Deadline"
    kdate: "2026/09/02"
    kdisplay: true
  - kname: "Mid Semester Grades Posted"
    kdate: "2026/10/09"
    kdisplay: false
  - kname: "Drop with a W Deadline"
    kdate: "2026/11/17"
    kdisplay: true
  - kname: "Reading Day"
    kdate: "2026/12/09"
    kdisplay: true
  - kname: "Finals Week Begins"
    kdate: "2026/12/10"
    kdisplay: false
  - kname: "Finals Week Ends"
    kdate: "2026/12/16"
    kdisplay: false
  spring: []
  fallholidays:
  - date: "2026/09/07"
  - date: "2026/10/08"
  - date: "2026/10/12"
  - date: "2026/10/13"
  - date: "2026/11/25"
  - date: "2026/11/26"
  - date: "2026/11/27"
  springholidays: []

instructors:
- name: William Mongan
  title: Professor
  email: wmongan@ursinus.edu
  phone: "610-409-3268"
  office: "Pfahler Hall 101L"
  webpage_url: "http://www.billmongan.com"
  picture: /images/profile.png
  officehourssignup: "https://cal.com/billmongan/10min"
  officehours:
  - day: "T"
    starttime: "11:20 AM"
    endtime: "11:50 AM"
    location: "Pfahler Hall 101L"
  - day: "R"
    starttime: "11:20 AM"
    endtime: "11:50 AM"
    location: "Pfahler Hall 101L"
  - day: "T"
    starttime: "3:00 PM"
    endtime: "5:30 PM"
    location: "Pfahler Hall 101L"
  - day: "W"
    starttime: "3:00 PM"
    endtime: "5:30 PM"
    location: "Pfahler Hall 101L"
  - day: "R"
    starttime: "3:00 PM"
    endtime: "3:30 PM"
    location: "Pfahler Hall 101L"
  - day: "R"
    starttime: "4:30 PM"
    endtime: "5:30 PM"
    location: "Pfahler Hall 101L"
textbooks:
- title: "Foundations of Computing: An Accessible Introduction to Formal Languages"
  authors: "Chuck Allison"
  link: "https://www.amazon.com/dp/0578944170"
  isrequired: true
  freelyavailable: "https://leanpub.com/foundationsofcomputing"
- title: "Introduction to Compilers and Language Design"
  authors: "Douglas Thain"
  edition: "2nd Edition"
  link: https://www3.nd.edu/~dthain/compilerbook/
  isrequired: false
  freelyavailable: https://www3.nd.edu/~dthain/compilerbook/compilerbook.pdf
- title: "Programming Languages: Application and Interpretation"
  authors: "Shriram Krishnamurthi"
  link: "https://www.plai.org/"
  isrequired: false
  freelyavailable: "https://www.plai.org/"
- title: "Crafting Interpreters"
  authors: "Robert Nystrom"
  link: "https://craftinginterpreters.com/"
  isrequired: false
  freelyavailable: "https://craftinginterpreters.com/contents.html"
  
objectives:
- objective: "Describe and compare the design principles, paradigms, and tradeoffs of modern programming languages."
- objective: "Specify the syntax of a language formally using grammars and regular expressions, and reason about what those formalisms can and cannot express."
- objective: "Construct the front end and evaluator of a programming language, connecting formal specification to working implementation."
- objective: "Evaluate how language design choices affect correctness, expressiveness, accessibility, and the communities that use a language."

goals:
- goal: "Classify languages by paradigm and evaluate them against criteria including readability, writability, and reliability."
- goal: "Write BNF and EBNF grammars, construct derivations and parse trees, and resolve ambiguity using precedence and associativity."
- goal: "Construct regular expressions and finite automata, and explain their equivalence and their limits relative to context-free languages."
- goal: "Implement a scanner, a recursive descent parser producing an abstract syntax tree, and a tree-walking evaluator with environments, in Python."
- goal: "Write idiomatic functional programs in Scheme and Python, and evaluate lambda calculus expressions by hand using beta reduction and Church encodings."
- goal: "Design and implement an original programming language as a team, integrating course components through iterative sprints, peer review, and a public demonstration."

grade_breakdown:
- category: "Programming Assignments"
  weight: "30%"
- category: "Labs"
  weight: "30%"
- category: "Team Language Project"
  weight: "30%"
- category: "Class Activities and Participation"
  weight: "10%"

letter_grades:
- letter: "A+"
  range: "96.9-100"
- letter: "A"
  range: "93-96.89"
- letter: "A-"
  range: "89.5-92.99"
- letter: "B+"
  range: "87-89.49"
- letter: "B"
  range: "83-86.99"
- letter: "B-"
  range: "79.5-82.99"
- letter: "C+"
  range: "77-79.49"
- letter: "C"
  range: "73-76.99"
- letter: "C-"
  range: "69.5-72.99"
- letter: "D+"
  range: "67-69.49"
- letter: "D"
  range: "63-66.99"
- letter: "D-"
  range: "59.5-62.99"
- letter: "F"
  range: "0-59.49"

schedule:
- week: "0"
  date: "0"
  title: "Welcome: Why Study Programming Languages?"
  link: "Activities/liascript-course-arc.md"
  liapage: true
  deliverables:
  - dtitle: "Participation: Warmup Assignment Handed Out"
    dlink: "Assignments/Warmup"
    points: "10"
  readings:
  - rtitle: "Thain, Chapter 1"
  - rtitle: "Allison, Ch. 1: Introduction, Formal Languages and Finite State Machines"
  - rtitle: "Course overview: what CS374 covers, how the term is organized, and what you will have built by December"
    rlink: "https://www.billmongan.com/Ursinus-CS374-Overview"
- week: "0"
  date: "1"
  title: "Programming Paradigms, Evaluating Languages, and Introduction to Functional Programming"
  link: "Activities/liascript-languageevaluation.md"
  liapage: true
  deliverables:
  - dtitle: "Participation: Overview Assignment Handed Out"
    dlink: "Assignments/Overview"
    points: "100"
    rubricpath: "_pages/Assignments/asmt-overview.md"
  - dtitle: "Participation: Exercises Handed Out"
    dlink: "Assignments/ParticipationExercises"
    points: "10"
    module: overarching
  - dtitle: "Participation: Exercise - Evaluating Languages and Paradigms Handed Out"
    dlink: "Assignments/ParticipationExercises/EvaluatingLanguages"
  readings:
  - rtitle: "History of Programming Languages"
    rlink: "https://www.billmongan.com/Ursinus-CS374-History"
  - rtitle: "Compiling and Linking (From Source to Executable)"
    rlink: "Tutorials/CompilingAndLinking"
- week: "1"
  date: "0"
  title: "Functional Programming in Scheme, Part 2"
  link: "Activities/liascript-scheme.md"
  liapage: true
  readings:
  - rtitle: "Continues Part 1.  Please have Scheme running before class, either installed locally or open in a browser tab at try.scheme.org, and bring the expression that would not evaluate."
    rlink: false
  - rtitle: "The Scheme Programming Language (Dybvig), Chapter 2: Getting Started"
    rlink: "https://www.scheme.com/tspl3/start.html"
  - rtitle: "Closures in Scheme (Andy Balaam)"
    rlink: "https://www.artificialworlds.net/presentations/scheme-03-closures/scheme-03-closures.html"
- week: "1"
  date: "1"
  title: "Functional Programming and Higher-Order Functions"
  link: "Activities/liascript-functional.md"
  liapage: true
  deliverables:
  - dtitle: "Participation: Exercise - Functional Programming and Higher-Order Functions Handed Out"
    dlink: "Assignments/ParticipationExercises/FunctionalProgramming"
  readings:
  - rtitle: "In-class taste: the declarative paradigm in Prolog, a 15-minute SWISH warm-up (facts, rules, a query that backtracks).  Previews the Functional assignment's Logic Programming direction"
    rlink: "https://swish.swi-prolog.org/"
  - rtitle: "The Power of Prolog (Markus Triska)"
    rlink: "https://www.metalevel.at/prolog"
  - rtitle: "Haskell Essentials"
    rlink: "Tutorials/HaskellEssentials"
- week: "2"
  date: "0"
  title: "Syntax and BNF/EBNF"
  link: "Activities/liascript-syntaxbnf.md"
  liapage: true
  deliverables:
  - dtitle: "Participation: Warmup Assignment Due"
    dlink: "Assignments/Warmup"
    points: "10"
  - dtitle: "Lab: BNF Workshop Handed Out"
    dlink: "Assignments/BNFWorkshop"
    points: "15"
    rubricpath: "_pages/Assignments/lab-bnfworkshop.md"
  - dtitle: "Participation: Overview Assignment Due"
    dlink: "Assignments/Overview"
    points: "100"
    rubricpath: "_pages/Assignments/asmt-overview.md"
  - dtitle: "Programming Assignment: Functional Programming with Scheme Handed Out"
    dlink: "Assignments/Scheme"
    points: "100"
    rubricpath: "_pages/Assignments/asmt-scheme.md"
  readings:
  - rtitle: "Allison, Ch. 6 §6.1: Context-Free Grammars and Derivations"
- week: "2"
  date: "1"
  title: "Grammars and the Chomsky Hierarchy (Day 1 of 2)"
  link: "Activities/liascript-grammars.md"
  liapage: true
  deliverables:
  - dtitle: "Participation: Exercise - Syntax, BNF/EBNF, and Grammars Handed Out"
    dlink: "Assignments/ParticipationExercises/SyntaxAndGrammars"
  readings:
  - rtitle: "Allison, Ch. 9 §9.3: The Chomsky Hierarchy"
  - rtitle: "Allison, Ch. 6 §6.1: Context-Free Grammars and Derivations"
- week: "3"
  date: "0"
  title: "Grammars, Day 2: Writing Context-Free Grammars"
  link: "Activities/liascript-grammars-day2.md"
  liapage: true
  deliverables:
  - dtitle: "Programming Assignment: Functional Programming with Scheme Due"
    dlink: "Assignments/Scheme"
    points: "100"
    rubricpath: "_pages/Assignments/asmt-scheme.md"
  readings:
  - rtitle: "Continues Day 1.  Bring the grammar you drafted; we build on it."
    rlink: false
- week: "3"
  date: "1"
  title: "Derivations, Parse Trees, Ambiguity, and Precedence"
  link: "Activities/liascript-derivationsambiguity.md"
  liapage: true
  deliverables:
  - dtitle: "Participation: Exercise - Derivations, Parse Trees, Ambiguity, and Precedence Handed Out"
    dlink: "Assignments/ParticipationExercises/DerivationsAndAmbiguity"
  readings:
  - rtitle: "Allison, Ch. 6 §6.2: Derivation Trees and Ambiguous Grammars (Operator Precedence and Associativity)"
- week: "4"
  date: "0"
  title: "Regular Expressions"
  link: "Activities/liascript-regex.md"
  liapage: true
  deliverables:
  - dtitle: "Lab: BNF Workshop Due"
    dlink: "Assignments/BNFWorkshop"
    points: "15"
    rubricpath: "_pages/Assignments/lab-bnfworkshop.md"
  - dtitle: "Programming Assignment: Regular Expressions Handed Out"
    dlink: "Assignments/Regex"
    points: "100"
    rubricpath: "_pages/Assignments/asmt-regex.md"
  - dtitle: "Lab: Regex Workshop Handed Out"
    dlink: "Assignments/RegexWorkshop"
    points: "15"
    rubricpath: "_pages/Assignments/lab-regexworkshop.md"
  - dtitle: "Participation: Exercise - Regular Expressions and Finite Automata Handed Out"
    dlink: "Assignments/ParticipationExercises/RegexAndAutomata"
  readings:
  - rtitle: "Allison, Ch. 3 §3.1-3.2: Regular Expressions and Their Equivalence to Finite Automata"
  - rtitle: "Allison, Ch. 4: The Pumping Lemma, proving a language is not regular (required for the Regex assignment's Part 4 theory questions; we work one example in class today)"
  - rtitle: "The Shell for Language Development, the grep section, which puts today's patterns to work on your own source tree"
    rlink: "Tutorials/ShellForLanguageDev"
- week: "4"
  date: "1"
  title: "Finite Automata (Day 1 of 2): DFAs"
  link: "Activities/liascript-automata.md"
  liapage: true
  readings:
  - rtitle: "Allison, Ch. 2 §2.1-2.2: Deterministic and Non-Deterministic Finite Automata"
  - rtitle: "Allison, Ch. 4 §4.2: Decision Algorithms (Is the Language Empty?)"
- week: "5"
  date: "0"
  title: "Finite Automata, Day 2: Nondeterminism and Equivalence"
  link: "Activities/liascript-automata-day2.md"
  liapage: true
  deliverables:
  - dtitle: "Lab: Finite Automata Simulators Handed Out"
    dlink: "Assignments/Automata"
    points: "15"
    rubricpath: "_pages/Assignments/lab-automata.md"
  - dtitle: "Lab: Regex Workshop Due"
    dlink: "Assignments/RegexWorkshop"
    points: "15"
    rubricpath: "_pages/Assignments/lab-regexworkshop.md"
  readings:
  - rtitle: "Continues Day 1.  Bring your hand-traced DFA from last session."
    rlink: false
- week: "5"
  date: "1"
  title: "Tokens and Scanning: Building a Lexer"
  link: "Activities/liascript-tokensscanning.md"
  liapage: true
  deliverables:
  - dtitle: "Programming Assignment: Build a Lexer Handed Out"
    dlink: "Assignments/Lexer"
    points: "100"
    rubricpath: "_pages/Assignments/asmt-lexer.md"
  - dtitle: "Participation: Exercise - Tokens and Scanning Handed Out"
    dlink: "Assignments/ParticipationExercises/TokensAndScanning"
  readings:
  - rtitle: "Allison, Ch. 2 §2.4: Machines with Output, Lexical Analysis"
- week: "6"
  date: "0"
  title: "Abstract Syntax Trees"
  link: "Activities/liascript-ast.md"
  liapage: true
  deliverables:
  - dtitle: "Participation: Exercise - Abstract Syntax Trees Handed Out"
    dlink: "Assignments/ParticipationExercises/AbstractSyntaxTrees"
  - dtitle: "Programming Assignment: Regular Expressions Due"
    dlink: "Assignments/Regex"
    points: "100"
    rubricpath: "_pages/Assignments/asmt-regex.md"
  readings:
  - rtitle: "Allison, Ch. 6 §6.2: Expression Trees, Operator Precedence, and Associativity"
- week: "7"
  date: "1"
  title: "Recursive Descent Parsing: From Grammar to Code"
  link: "Activities/liascript-recursivedescent.md"
  liapage: true
  deliverables:
  - dtitle: "Lab: Grammar and Derivations Workshop Handed Out"
    dlink: "Assignments/GrammarWorkshop"
    points: "15"
    rubricpath: "_pages/Assignments/lab-grammarworkshop.md"
  - dtitle: "Participation: Exercise - Recursive Descent Parsing Handed Out"
    dlink: "Assignments/ParticipationExercises/RecursiveDescent"
  readings:
  - rtitle: "Parser Combinators (Parsers as First-Class Values)"
    rlink: "Tutorials/ParserCombinators"
- week: "8"
  date: "0"
  title: "Parsing Expressions: Left Factoring, Precedence, and Chained Comparisons"
  link: "Activities/liascript-parsingexpressions.md"
  liapage: true
  deliverables:
  - dtitle: "Lab: Finite Automata Simulators Due"
    dlink: "Assignments/Automata"
    points: "15"
    rubricpath: "_pages/Assignments/lab-automata.md"
  readings:
  - rtitle: "For the Parser assignment (Step 3e): Property-Based Testing with Hypothesis, covering the round-trip property and how to shrink a failing case"
    rlink: "Tutorials/PropertyBasedTesting"
- week: "8"
  date: "1"
  title: "Table-Driven and LR Parsing"
  link: "Activities/liascript-parsertable.md"
  liapage: true
  deliverables:
  - dtitle: "Programming Assignment: Build a Lexer Due"
    dlink: "Assignments/Lexer"
    points: "100"
    rubricpath: "_pages/Assignments/asmt-lexer.md"
  - dtitle: "Programming Assignment: Parser and AST Handed Out"
    dlink: "Assignments/Parser"
    points: "100"
    rubricpath: "_pages/Assignments/asmt-parser.md"
  readings:
  - rtitle: "Allison, Ch. 5: Pushdown Automata, Adding a Stack to Finite Automata"
  - rtitle: "Allison, Ch. 6 §6.3: Equivalence of PDAs and Context-Free Grammars"
- week: "9"
  date: "0"
  title: "Tree-Walking Interpretation (Day 1 of 2): Evaluating the AST"
  link: "Activities/liascript-interpretation.md"
  liapage: true
  deliverables:
  - dtitle: "Lab: Grammar and Derivations Workshop Due"
    dlink: "Assignments/GrammarWorkshop"
    points: "15"
    rubricpath: "_pages/Assignments/lab-grammarworkshop.md"
  - dtitle: "Lab: Parser Skeleton Handed Out"
    dlink: "Assignments/ParserSkeleton"
    points: "15"
    rubricpath: "_pages/Assignments/lab-parserskeleton.md"
  - dtitle: "Team Language Project Handed Out"
    dlink: "Projects/TeamLanguage"
    points: "100"
    rubricpath: "_pages/Projects/proj-teamlanguage.md"
  - dtitle: "Participation: Exercise - Binding and Scope, Part 1: Tree-Walking Interpretation Handed Out"
    dlink: "Assignments/ParticipationExercises/BindingAndScope"
  readings:
  - rtitle: "Allison, Ch. 6 §6.1-6.2: Context-Free Grammars, Derivation Trees, and Expression Trees"
  - rtitle: "PLY Lexer and Parser in Python (the generator-toolchain path through the Lexer and Parser assignments)"
    rlink: "Tutorials/PLYLexerAndParser"
- week: "9"
  date: "1"
  title: "Control Flow and Statement Semantics (Interpretation, Day 2)"
  link: "Activities/liascript-controlflowsemantics.md"
  liapage: true
  readings:
  - rtitle: "This session is Day 2 of tree-walking interpretation: statements change state, where expressions returned values."
    rlink: false
  - rtitle: "For the Tree-Walking Interpreter (Step 2e): Property-Based Testing with Hypothesis, covering the round-trip property, now over evaluation"
    rlink: "Tutorials/PropertyBasedTesting"
  - rtitle: "CI and TDD for Interpreters"
    rlink: "Tutorials/CITDDForInterpreters"
- week: "10"
  date: "0"
  title: "Binding and Scope"
  link: "Activities/liascript-bindingscope.md"
  liapage: true
  deliverables:
  - dtitle: "Lab: Parser Skeleton Due"
    dlink: "Assignments/ParserSkeleton"
    points: "15"
    rubricpath: "_pages/Assignments/lab-parserskeleton.md"
  - dtitle: "Lab: Environments and Scope Handed Out"
    dlink: "Assignments/EnvironmentsLab"
    points: "15"
    rubricpath: "_pages/Assignments/lab-environments.md"
  - dtitle: "Participation: Exercise - Binding and Scope, Part 2: Mystery Scoping Language Handed Out"
    dlink: "Assignments/ParticipationExercises/BindingAndScope"
  readings:
  - rtitle: "Krishnamurthi, PLAI (3rd ed.): the Stacker and SMoL Tutor, which we step through in class, and the chapters on functions, scope, and environments"
    rlink: "https://www.plai.org/"
- week: "10"
  date: "1"
  title: "Environments and Variable Storage"
  link: "Activities/liascript-environments.md"
  liapage: true
  readings:
  - rtitle: "Build an Interpreter (start-to-finish companion for the upcoming assignment)"
    rlink: "Tutorials/BuildAnInterpreter"
  - rtitle: "Garbage Collection (Implementing Memory Management)"
    rlink: "Tutorials/GarbageCollection"
- week: "11"
  date: "0"
  title: "Type Systems"
  link: "Activities/liascript-types.md"
  liapage: true
  deliverables:
  - dtitle: "Programming Assignment: Parser and AST Due"
    dlink: "Assignments/Parser"
    points: "100"
    rubricpath: "_pages/Assignments/asmt-parser.md"
  - dtitle: "Programming Assignment: Tree-Walking Interpreter Handed Out"
    dlink: "Assignments/Interpreter"
    points: "100"
    rubricpath: "_pages/Assignments/asmt-interpreter.md"
  - dtitle: "Team Language Project: Design-Phase Submission (team, niche, design scorecard, draft team charter) Due"
    dlink: "Projects/TeamLanguage"
    points: "3"
    rubricpath: "_pages/Projects/proj-teamlanguage.md"
  - dtitle: "Lab: Type Checker Starter Handed Out"
    dlink: "Assignments/TypeCheckerLab"
    points: "15"
    rubricpath: "_pages/Assignments/lab-typechecker.md"
  - dtitle: "Participation: Exercise - Type Systems Handed Out"
    dlink: "Assignments/ParticipationExercises/TypeSystems"
  - dtitle: "Lab: Environments and Scope Due"
    dlink: "Assignments/EnvironmentsLab"
    points: "15"
    rubricpath: "_pages/Assignments/lab-environments.md"
  readings:
  - rtitle: "Typing Disciplines, going past today's quadrant into structural vs. nominal typing, type erasure, and algebraic data types"
    rlink: "Tutorials/TypingDisciplines"
  - rtitle: "In-class compare: the same buggy snippet under mypy (Python) and TypeScript, gradual typing as an object of study"
    rlink: "https://www.typescriptlang.org/play"
  - rtitle: "Allison, Ch. 10 §10.1: The Halting Problem (Why Some Questions About Programs Are Undecidable)"
  - rtitle: "Type Inference (Implementing Hindley-Milner)"
    rlink: "Tutorials/TypeInference"
- week: "11"
  date: "1"
  title: "Language Design Workshop: Project Kickoff (Sprint 0)"
  link: "Activities/liascript-languagedesign.md"
  liapage: true
  deliverables:
  - dtitle: "Team Language Project: Proposal (with signed team charter) Due"
    dlink: "Projects/TeamLanguage"
    points: "25"
    rubricpath: "_pages/Projects/proj-teamlanguage.md"
  readings:
  - rtitle: "Build a Bytecode VM"
    rlink: "Tutorials/BytecodeVM"
- week: "12"
  date: "0"
  title: "Lambda Calculus I: Syntax and Beta Reduction"
  link: "Activities/liascript-lambdacalculus1.md"
  liapage: true
  deliverables:
  - dtitle: "Lab: Type Checker Starter Due"
    dlink: "Assignments/TypeCheckerLab"
    points: "15"
    rubricpath: "_pages/Assignments/lab-typechecker.md"
  - dtitle: "Lab: Lambda Calculus Handed Out"
    dlink: "Assignments/LambdaCalculusLab"
    points: "15"
    rubricpath: "_pages/Assignments/lab-lambdacalculus.md"
  - dtitle: "Participation: Exercise - Lambda Calculus Handed Out"
    dlink: "Assignments/ParticipationExercises/LambdaCalculus"
  readings:
  - rtitle: "Allison, Ch. 8: Turing Machines and the Church-Turing Thesis"
  - rtitle: "Lambda Calculus - Fundamentals of Lambda Calculus & Functional Programming in JavaScript (Gabriel Lebec)"
    rlink: "https://www.youtube.com/watch?v=3VQ382QG-y4"
  - rtitle: "Build a Lambda Calculus Reducer"
    rlink: "Tutorials/LambdaCalculusReducer"
- week: "12"
  date: "1"
  title: "Lambda Calculus II: Church Encodings and Combinators"
  link: "Activities/liascript-lambdacalculus2.md"
  liapage: true
  deliverables:
  - dtitle: "Programming Assignment: Functional Programming Handed Out"
    dlink: "Assignments/Functional"
    points: "100"
    rubricpath: "_pages/Assignments/asmt-functional.md"
  readings:
  - rtitle: "Church encodings: numerals, booleans, and the arithmetic you reduce by hand in the Lambda Calculus lab (today's activity, Models 2-3)"
  - rtitle: "A Flock of Functions: Combinators, Lambda Calculus, & Church Encodings in JS - Part II (Gabriel Lebec)"
    rlink: "https://www.youtube.com/watch?v=pAnLQ9jwN-E"
- week: "13"
  date: "0"
  title: "Closures and First-Class Functions"
  link: "Activities/liascript-closures.md"
  liapage: true
  deliverables:
  - dtitle: "Programming Assignment: Tree-Walking Interpreter Due"
    dlink: "Assignments/Interpreter"
    points: "100"
    rubricpath: "_pages/Assignments/asmt-interpreter.md"
  - dtitle: "Team Language Project: Sprint 1 Increment Checkpoint Due"
    dlink: "Projects/TeamLanguage"
    points: "3"
    rubricpath: "_pages/Projects/proj-teamlanguage.md"
  readings:
  - rtitle: "Prolog and the declarative paradigm, background for the Functional assignment's Logic Programming direction (Direction F), alongside The Power of Prolog"
    rlink: "Tutorials/Prolog"
  - rtitle: "The open-source contribution direction (Direction G) of the Functional assignment: mal, Strudel/TidalCycles, tree-sitter, or the SWI-Prolog docs, with scope approval needed in the first week"
    rlink: "Assignments/Functional"
- week: "14"
  date: "0"
  title: "Sprint Studio: Sprints 1-2 and Gallery Walk"
  link: "Activities/liascript-sprintstudio.md"
  liapage: true
  deliverables:
  - dtitle: "Lab: Lambda Calculus Due"
    dlink: "Assignments/LambdaCalculusLab"
    points: "15"
    rubricpath: "_pages/Assignments/lab-lambdacalculus.md"
  - dtitle: "Team Language Project: Sprint 2 Gallery Walk (Strength/Question/Risk cards + triage) Due"
    dlink: "Projects/TeamLanguage"
    points: "3"
    rubricpath: "_pages/Projects/proj-teamlanguage.md"
  readings:
  - rtitle: "The Project Language Guide (a complete worked path for the team project)"
    rlink: "Tutorials/ProjectLanguageGuide"
  - rtitle: "Shell Skills for Language Development"
    rlink: "Tutorials/ShellForLanguageDev"
- week: "14"
  date: "1"
  title: "Sprint Studio: Sprint 3 and Release Hardening"
  link: "Activities/liascript-sprintstudio.md"
  liapage: true
  deliverables:
  - dtitle: "Programming Assignment: Functional Programming Due"
    dlink: "Assignments/Functional"
    points: "100"
    rubricpath: "_pages/Assignments/asmt-functional.md"
  - dtitle: "Team Language Project: ShipIt Release Checklist Due"
    dlink: "Projects/TeamLanguage"
    points: "3"
    rubricpath: "_pages/Projects/proj-teamlanguage.md"
  readings:
  - rtitle: "Publishing Your Language (pip, npm, and Docker)"
    rlink: "Tutorials/PublishingYourLanguage"
  - rtitle: "Advanced C++ for Language Implementers"
    rlink: "Tutorials/AdvancedCpp"
- week: "15"
  date: "0"
  title: "Demo Day: Team Language Presentations (Class Switch Day: follows a Thursday schedule)"
  deliverables:
  - dtitle: "Team Language Project: Demo Day Presentations Due"
    dlink: "Projects/TeamLanguage"
    points: "75"
    rubricpath: "_pages/Projects/proj-teamlanguage.md"
  - dtitle: "Participation: Exercises Due"
    dlink: "Assignments/ParticipationExercises"
    points: "10"
---

This semester is a build.  By December, your team will have designed and implemented a programming language of your own, assembled one assignment at a time.  The sections below explain how the pieces fit together, including how the course gives you choices, how to read an assignment, how to prepare for each class, and how I value and evaluate the day-to-day work of participating.  Please read them once now, and come back to the participation and preparation guides throughout the term.

## How This Course Works: Choice and Universal Design

I have built this course on the principle that there is more than one good path through it, and that you should have real say over yours.  The choices here are in the spirit of Universal Design for Learning, which asks for multiple ways to engage with the material and multiple ways to demonstrate what you have learned.  None of these paths is the "remedial" one.

- **A capstone you shape.**  The Team Language Project is yours to design.  A compelling original language is always welcome, and the final project's extension menu lets you go deep wherever your interest lies instead of following one fixed spec.
- **The Music and Live-Coding Directions.**  If you would rather build toward making music than a general-purpose language, several assignments (the Parser and Functional Programming among them) and the Team Language Project each offer a music direction inside the same required deliverable.  The [Music and Live-Coding guide](Projects/TeamLanguage#the-music-and-live-coding-path) maps the whole path, including a text-events-only route that never requires audio.  Choose direction by direction as each assignment arrives; teams commit to a project direction at the kickoff.
- **Depth inside every assignment, and supplemental depth everywhere.**  Each programming assignment offers **directions** you choose inside it (a generator-toolchain lexer, a music-notation parser, a type checker for your interpreter, continuations or Church encodings in the functional assignment), so nothing on the schedule is optional, but every deliverable has room for your interests.  Beyond the assignments, the schedule carries supplemental activities and tutorials on parser combinators, garbage collection, bytecode VMs, and more, and you can browse them on the [Tutorials shelf](Tutorials/).  These are invitations rather than obligations.  Please tell me when one of them becomes the thing you want to go further with.

If a path you want is not on the menu, please propose it.  The choices are here so you can build the language, and the fluency, that you actually care about.

## How Assignments Are Structured: Purpose, Task, and Criteria

I write every assignment in this course to be transparent about three things, so you are never guessing about what I am asking or how I will judge it:

- **Purpose:** *why* the assignment exists and what capability it builds toward.  None of it is busywork.  Each piece is either a stage of the language you are building or a skill that stage depends on.
- **Task:** *what* you will actually do, broken into concrete steps.
- **Criteria:** *how* your work will be evaluated.  Every graded assignment carries a rubric with four levels (pre-emerging, beginning, progressing, proficient) so you can see exactly what proficient work looks like before you start, and can use the rubric to assess your own draft.

When you open an assignment, please read the Purpose first.  It tells you what the assignment is really for, and that is the fastest way to make good decisions when the task gets ambiguous.  Every assignment also closes by asking you to reflect on what you did, what fought you, how long it took, and what grade you would give yourself against the criteria.  I count that reflection as part of the work.

A note on grade categories: the **Overview** (100 points) and **Warmup** (10 points) onboarding assignments are assessed within **Class Activities and Participation**; the five programming assignments (Regular Expressions, Lexer, Parser, Interpreter, and Functional Programming) make up the **Programming Assignments** category.  The **Labs** category comprises eight short labs (BNF Workshop, Regex Workshop, Finite Automata Simulators, Grammar and Derivations Workshop, Parser Skeleton, Environments and Scope, Type Checker Starter, and Lambda Calculus), each scoped to roughly two to three hours.  Labs may be completed **in pairs** (both partners submit, naming each other; both earn the same grade); the programming assignments remain individual work.  Each lab falls mid-assignment and completes a piece of the assignment it scaffolds, so lab work gives you a head start rather than adding to your load.  **There is no midterm or final exam**: Demo Day on the last class meeting (Tuesday, December 8) is the course's terminal event, and no work is accepted after it.  Seven teams present for nine minutes each within our class meeting; external guests visiting both this Demo Day and CS357's (same day) are welcome to stay for both.

## Generative AI Policy

Generative AI tools are part of the professional landscape you are graduating into, and I treat them here the way I would treat any powerful tool.  They are welcome in some roles, corrosive in others, and never a substitute for your own understanding.

- **Permitted uses.**  You may use AI tools to explain concepts you are stuck on, to debug your own code, and to explore alternative approaches to a problem you have already engaged with.  Used this way, they are a tutor on call, and a good complement to the reading routine described below.
- **Required disclosure.**  Each assignment's reflection asks what AI tools you used and how.  Please answer it plainly every time.  "None" is always an acceptable answer, and I never penalize disclosure.
- **Primary authorship.**  You must be the primary author of the code and prose you submit, and you must be able to explain any line of your submission when I ask.  If a tool wrote something you cannot explain, it isn't ready to submit.  The gap will show the moment we discuss your work, because the reflection and the conversation are both part of the assessment.
- **Public work.**  Work that leaves the classroom carries an extra obligation.  For Functional Direction G pull requests and team-project open-source extensions, you must disclose AI-assisted contributions to maintainers according to that project's own policy, and you are accountable for their correctness.  Please do not spend an upstream maintainer's trust casually.

Every assignment here is aimed at the fluency you build rather than the artifact you hand in.  Use these tools in ways that leave you knowing more than you did before, and you will be on the right side of this policy.

## Preparing for Each Class

Our class meetings are hands-on POGIL sessions.  You work in your standing team through activities that build the concepts and the code, rather than sitting through lectures.  That means class works best when you arrive ready, and being ready is a routine you can run rather than a matter of luck.  The **[Preparing for Each Class](Participation/PreparingForClass)** guide lays out that routine: how to read a technical section in passes, how to attempt the participation exercises before class, and how to arrive with a question or a sticking point the session can resolve.  Bringing that prepared question is how I know the reading happened, and it is usually where the best discussion starts.

## Class Activities and Participation (15%)

This is a course you do rather than one you watch, and this component values the daily work of showing up prepared and contributing to the shared build.  I assess it against the rubric on the **[Preparing for Each Class](Participation/PreparingForClass)** guide, across four dimensions: **preparation** (you have done the reading and attempted the exercises), **contribution** (you engage in your POGIL team and in whole-class discussion), **collaboration** (you take your rotating team role seriously and help your teammates succeed), and **reflection** (your activity and assignment reflections show real engagement).

Participation takes more than one form here, and that is deliberate.  In the in-class activities your team rotates the POGIL roles (**Manager, Recorder, Presenter, and Reflector**) so that on different days you facilitate, capture the group's thinking, report out, or step back and synthesize.  In the project phase your team rotates a second set of roles: **Coordinator, Builder, Evaluator, and Scribe**.  Speaking up in whole-class discussion counts, and so does posting your team's answer to the class discussion board, asking a sharp question, or helping a teammate past a bug.  If the spoken room is hard for you, the written and role-based channels are real ways to earn this component.  Please talk with me early and we'll find the path that fits.

From time to time the class agenda sets aside time for **participation exercises and discussion**.  These are short problems tied to the reading, like writing a grammar rule, tracing a tokenizer, or evaluating a language-design tradeoff, and you attempt them beforehand so we can work through them together.  These are marked on the schedule and drawn from the **[Participation Exercises](Assignments/ParticipationExercises)** bank.  The Week 14 **mock-interview rehearsal** (practicing an interview-style explanation of your own interpreter and language with a partner from another team) counts here too; see the [Demo Day Guide](Projects/TeamLanguage#demo-day-external-guests-and-technical-interview-practice).
