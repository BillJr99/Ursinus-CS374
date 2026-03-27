---
layout: assignment
permalink: /Projects/Final
title: "CS374: Principles of Programming Languages - Final Project"


info:
  coursenum: CS374
  points: 100
  goals:
    - To demonstrate the fundamental concepts of programming languages in a unified project
    - To work effectively as a member of a small group using collaborative tools for software development
  rubric:
    - weight: 40
      description: Algorithm Implementation
      preemerging: The algorithm fails on the test inputs due to major issues, or the program fails to compile and/or run
      beginning: The algorithm fails on the test inputs due to one or more minor issues
      progressing: The algorithm is implemented to solve the problem correctly according to given test inputs, but includes only a single class, or would fail if executed in a general case due to a minor issue or omission in the algorithm design or implementation
      proficient: A reasonable algorithm with at least two peers is implemented to solve the problem which correctly solves the problem according to the given test inputs, and would be reasonably expected to solve the problem in the general case
    - weight: 20
      description: Test Cases
      preemerging: Testing was performed outside of the unit test framework, or not performed at all
      beginning: Trivial test cases are provided in a unit test framework
      progressing: Test cases that cover some, but not all, boundary cases and branches of the program are provided
      proficient: Test cases that cover all boundary cases and branches of the program are provided
    - weight: 20
      description: Code Quality and Documentation
      preemerging: Code commenting and structure are absent, or code structure departs significantly from best practice, and/or the code departs significantly from the style guide
      beginning: Code commenting and structure is limited in ways that reduce the readability of the program, and/or there are minor departures from the style guide
      progressing: Code documentation is present that re-states the explicit code definitions, and/or code is written that mostly adheres to the style guide
      proficient: Code is documented at non-trivial points in a manner that enhances the readability of the program, and code is written according to the style guide
    - weight: 10
      description: Presentation and Participation
      preemerging: No presentation was provided, the presentation could not be viewed, or the presentation was not on the subject of the final project; one or more students did not participate in the project and the matter was not addressed by the team to the instructor
      beginning: A presentation was provided that summarizes the project, but does not provide a demo or discuss broader impacts; each student participated in a meangful way
      progressing: A presentation was provided that summarizes the project, provides a demo, and discusses broader impacts; all students participated in either the project or the presentation
      proficient: A presentation was provided that that summarizes the project, provides a demo, discusses broader impacts, and highlights challenges overcome and methodologies for developing the system as a group; all students participated in both the project and the presentation
    - weight: 10
      description: Writeup and Submission
      preemerging: An incomplete submission is provided
      beginning: The program is submitted, but not according to the directions in one or more ways (for example, because it is lacking a readme writeup)
      progressing: The program is submitted according to the directions with a minor omission or correction needed
      proficient: The program is submitted according to the directions, including a readme writeup describing the solution

tags:
  - project
  
---

In this project, you will propose a topic of your choosing and a group of at least 2 and up to 3 total members.  The project must be approved by the instructor before it may commence, but the topic is entirely up to you.  Multidisciplinary projects with a broader impact are encouraged, and you are welcome to collaborate with a stakeholder outside the department for inspiration on potential projects (this person is not to contribute code, only disciplinary context).

You may use git or another version control system to coordinate between your team.  **Each student shall contribute by checking in meaningful contributions to the project on the version control system.  If a version control system is not used, code sections should be commented with the initials or recognized pseudonym of the student.**

You may design, document, implement a grammar of your choosing, and then develop a scanner and parser that interprets commands from that grammar according to any behavior you choose.  Here are a few example proposals:

* Scan and parse boolean expressions, interpreting to a truth statement, for example:
```
X = TRUE
Y = FALSE
(X OR Y) AND (X AND NOT Y)
# outputs TRUE
```
* Scan, parse, and interpret a set of commands to automate several process, like backing up a directory of your computer, pulling or pushing to a repository, or sending an email to someone with parameters you specify.
* Scan and parse a simple programming language grammar, and generate an abstract syntax tree representing each statement that you encounter.

You may use utilities such as lex and yacc to help you build the underlying components.

Finally, prepare as a team a project presentation that you will present live to the class for final presentations.  **Each student must have a speaking role** at the presentation.

## Group Formation

To form a group, students should draft a text document including the names of all students in the group, a summary of the proposed project, and a breakdown of each student's responsibilities on the team.  **Each student** should send this identical document to me for approval via e-mail.  I will respond via e-mail to the **entire** group notifying them that the project has been approved, and which members are on the team.  If I add or remove members from the team, I will notify the entire group via e-mail.  This shall constitute agreement of the project responsibilities by all members of the team.

Students who do not submit the proposal document described above (even if they are named in another group's proposal) within 3 days of the project hand-out date will be assigned to a group and notified via e-mail.

Should a member of the team fail to participate to the standards set in the proposal document described above, one or more members of the group shall notify that student via e-mail of specific tasks from the proposal document that have been agreed to, along with a deadline to communicate with the group (copy me on the e-mail message).  If the student does not respond within 2 days of that message, the group should notify me via e-mail, and I will investigate and, if appropriate, I may re-organize the team by moving one or more members to other groups (whom I will notify via e-mail), or by removing the student from the group (whom I will notify via e-mail).  