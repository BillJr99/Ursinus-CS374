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
  course_homepage: "https://www.billmongan.com/Ursinus-CS374-Fall2026/"
  ical: files/CS374.ics
  course_prerequisites: "CS174 with a grade of C- or higher."
  course_start_date: "2026/08/24"
  course_end_date: "2026/12/07"
  course_description: "Syntax, processors, representations and styles of programming languages. Study and comparison of several modern programming languages. Prerequisite: A grade of C- or higher in CS-174. Offered in the fall of even years. Three hours per week. Four semester hours."
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
      place: "Pfahler 007"
    - day: "R"
      starttime: "10:00 AM"
      endtime: "11:15 AM"
      place: "Pfahler 007"
  midtermexam: 
    - mdate: "N/A"
      mstarttime: "N/A"
      mendtime: "N/A"
      mroom: "N/A"       
  finalexam: 
    - fdate: "TBD"
      fstarttime: "TBD"
      fendtime: "TBD"
      froom: "Pfahler 007" 
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
    starttime: "10:00 AM"
    endtime: "12:00 PM"
    location: "Pfahler Hall 101L"  
  - day: "R"
    starttime: "10:00 AM"
    endtime: "12:00 PM"
    location: "Pfahler Hall 101L"           
    
textbooks:
- title: "Introduction to Compilers and Language Design"
  authors: "Douglas Thain"
  edition: "2nd Edition"
  link: https://www3.nd.edu/~dthain/compilerbook/
  isrequired: true
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
- category: "Programming Assignments (6)"
  weight: "50%"
- category: "Team Language Project"
  weight: "25%"
- category: "Class Activities and Participation"
  weight: "15%"
- category: "Reflection Notebook"
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
- week: "1"
  date: "0"
  title: "Welcome: Why Study Programming Languages?"
  link: "https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374/gh-pages/_pages/Activities/liascript-welcomepl.md"
  deliverables:
  - dtitle: "Warmup Assignment Handed Out"
    dlink: "Assignments/Warmup"
    points: "25"
    rubricpath: "_pages/Assignments/asmt-warmup.md"
  readings:
  - rtitle: "Thain, Chapter 1"
- week: "1"
  date: "1"
  title: "Programming Paradigms"
  link: "https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374/gh-pages/_pages/Activities/liascript-paradigms.md"
- week: "2"
  date: "0"
  title: "Evaluating Languages: Readability, Writability, Reliability"
  link: "https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374/gh-pages/_pages/Activities/liascript-languageevaluation.md"
- week: "2"
  date: "1"
  title: "Syntax and BNF/EBNF"
  link: "https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374/gh-pages/_pages/Activities/liascript-syntaxbnf.md"
- week: "3"
  date: "0"
  title: "Grammars and the Chomsky Hierarchy"
  link: "https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374/gh-pages/_pages/Activities/liascript-grammars.md"
  deliverables:
  - dtitle: "Warmup Assignment Due"
    dlink: "Assignments/Warmup"
    points: "25"
    rubricpath: "_pages/Assignments/asmt-warmup.md"
- week: "3"
  date: "1"
  title: "Derivations, Parse Trees, Ambiguity, and Precedence"
  link: "https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374/gh-pages/_pages/Activities/liascript-derivationsambiguity.md"
  deliverables:
  - dtitle: "Programming Assignment: Regular Expressions Handed Out"
    dlink: "Assignments/Regex"
    points: "100"
    rubricpath: "_pages/Assignments/asmt-regex.md"
- week: "4"
  date: "0"
  title: "Regular Expressions"
  link: "https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374/gh-pages/_pages/Activities/liascript-regex.md"
- week: "4"
  date: "1"
  title: "Finite Automata: DFAs, NFAs, and Equivalence"
  link: "https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374/gh-pages/_pages/Activities/liascript-automata.md"
- week: "5"
  date: "0"
  title: "Tokens and Scanning: Building a Lexer"
  link: "https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374/gh-pages/_pages/Activities/liascript-tokensscanning.md"
  deliverables:
  - dtitle: "Programming Assignment: Regular Expressions Due"
    dlink: "Assignments/Regex"
    points: "100"
    rubricpath: "_pages/Assignments/asmt-regex.md"
  - dtitle: "Programming Assignment: Automata Handed Out"
    dlink: "Assignments/Automata"
    points: "100"
    rubricpath: "_pages/Assignments/asmt-automata.md"
- week: "5"
  date: "1"
  title: "Recursive Descent Parsing: From Grammar to Code"
  link: "https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374/gh-pages/_pages/Activities/liascript-recursivedescent.md"
- week: "6"
  date: "0"
  title: "Parsing Expressions: Left Factoring, Precedence, and Chained Operators"
  link: "https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374/gh-pages/_pages/Activities/liascript-parsingexpressions.md"
  deliverables:
  - dtitle: "Programming Assignment: Automata Due"
    dlink: "Assignments/Automata"
    points: "100"
    rubricpath: "_pages/Assignments/asmt-automata.md"
  - dtitle: "Programming Assignment: Build a Lexer Handed Out"
    dlink: "Assignments/Lexer"
    points: "100"
    rubricpath: "_pages/Assignments/asmt-lexer.md"
- week: "6"
  date: "1"
  title: "Abstract Syntax Trees"
  link: "https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374/gh-pages/_pages/Activities/liascript-ast.md"
- week: "7"
  date: "0"
  title: "Table-Driven and LR Parsing"
  link: "https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374/gh-pages/_pages/Activities/liascript-parsertable.md"
  readings:
  - rtitle: "Optional: Parser Generators with Flex and Yacc"
    rlink: "https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374/gh-pages/_pages/Activities/liascript-flexyacc.md"
- week: "7"
  date: "1"
  title: "No Class: APEX Experiential Learning Day"
- week: "8"
  date: "0"
  title: "No Class: Fall Break"
- week: "8"
  date: "1"
  title: "Tree-Walking Interpretation: Evaluating the AST"
  link: "https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374/gh-pages/_pages/Activities/liascript-interpretation.md"
  deliverables:
  - dtitle: "Programming Assignment: Build a Lexer Due"
    dlink: "Assignments/Lexer"
    points: "100"
    rubricpath: "_pages/Assignments/asmt-lexer.md"
  - dtitle: "Programming Assignment: Parser and AST Handed Out"
    dlink: "Assignments/Parser"
    points: "100"
    rubricpath: "_pages/Assignments/asmt-parser.md"
- week: "9"
  date: "0"
  title: "Binding and Scope"
  link: "https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374/gh-pages/_pages/Activities/liascript-bindingscope.md"
- week: "9"
  date: "1"
  title: "Environments and Variable Storage"
  link: "https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374/gh-pages/_pages/Activities/liascript-environments.md"
- week: "10"
  date: "0"
  title: "Type Systems"
  link: "https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374/gh-pages/_pages/Activities/liascript-types.md"
  deliverables:
  - dtitle: "Programming Assignment: Parser and AST Due"
    dlink: "Assignments/Parser"
    points: "100"
    rubricpath: "_pages/Assignments/asmt-parser.md"
  - dtitle: "Programming Assignment: Tree-Walking Interpreter Handed Out"
    dlink: "Assignments/Interpreter"
    points: "100"
    rubricpath: "_pages/Assignments/asmt-interpreter.md"
- week: "10"
  date: "1"
  title: "Control Flow and Statement Semantics"
  link: "https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374/gh-pages/_pages/Activities/liascript-controlflowsemantics.md"
- week: "11"
  date: "0"
  title: "Functional Programming and Higher-Order Functions"
  link: "https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374/gh-pages/_pages/Activities/liascript-functional.md"
- week: "11"
  date: "1"
  title: "Scheme and Racket as Objects of Study"
  link: "https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374/gh-pages/_pages/Activities/liascript-scheme.md"
- week: "12"
  date: "0"
  title: "Lambda Calculus I: Syntax and Beta Reduction"
  link: "https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374/gh-pages/_pages/Activities/liascript-lambdacalculus1.md"
- week: "12"
  date: "1"
  title: "Lambda Calculus II: Church Encodings and Combinators"
  link: "https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374/gh-pages/_pages/Activities/liascript-lambdacalculus2.md"
  deliverables:
  - dtitle: "Programming Assignment: Tree-Walking Interpreter Due"
    dlink: "Assignments/Interpreter"
    points: "100"
    rubricpath: "_pages/Assignments/asmt-interpreter.md"
  - dtitle: "Team Language Project Handed Out"
    dlink: "Projects/TeamLanguage"
    points: "100"
    rubricpath: "_pages/Projects/proj-teamlanguage.md"
  - dtitle: "Programming Assignment: Functional Programming Handed Out"
    dlink: "Assignments/Functional"
    points: "100"
    rubricpath: "_pages/Assignments/asmt-functional.md"
- week: "13"
  date: "0"
  title: "Closures and First-Class Functions"
  link: "https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374/gh-pages/_pages/Activities/liascript-closures.md"
- week: "13"
  date: "1"
  title: "Modern Language Features"
  link: "https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374/gh-pages/_pages/Activities/liascript-modernfeatures.md"
  deliverables:
  - dtitle: "Programming Assignment: Functional Programming Due"
    dlink: "Assignments/Functional"
    points: "100"
    rubricpath: "_pages/Assignments/asmt-functional.md"
- week: "14"
  date: "0"
  title: "Language Design Workshop: Project Kickoff (Sprint 0)"
  link: "https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374/gh-pages/_pages/Activities/liascript-languagedesign.md"
  readings:
  - rtitle: "Optional Unit: Music Languages and Live Coding"
    rlink: "https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374/gh-pages/_pages/Activities/liascript-musiclanguages.md"
- week: "14"
  date: "1"
  title: "No Class: Thanksgiving Break"
- week: "15"
  date: "0"
  title: "Sprint Studio and Gallery Walk: Peer Review of Team Languages"
  link: "https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374/gh-pages/_pages/Activities/liascript-sprintstudio.md"
- week: "15"
  date: "1"
  title: "Demo Day: Team Language Presentations"
  deliverables:
  - dtitle: "Team Language Project Due"
    dlink: "Projects/TeamLanguage"
    points: "100"
    rubricpath: "_pages/Projects/proj-teamlanguage.md"
---
