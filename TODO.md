# TODO

- [ ] Break things down into smaller, more frequent deliverables
- [ ] Slow down the Scheme and functional programming unit by about two class days, and shift the later sessions and deliverable dates to match
- [ ] Add functional programming exercises in Python to the Scheme assignment (map, filter, and reduce, lambdas, closures, and recursion written in Python alongside the Scheme versions) so students see the paradigm carry across languages
- [ ] Improve student accountability through firm deliverable schedules and clearer late policies: publish a deliverable calendar students can plan against, state the late penalty and any grace or extension mechanism in plain terms up front, and apply it consistently. (added 2026-10-22)

- [ ] Simplify the language across the course so each page is concise and easy to scan:
  - **Syllabus table:** shorten the wording in the schedule table (titles, reading entries, and deliverable descriptions) to the minimum a student needs; move any longer explanation to the linked page instead of the table.
  - **Assignments:** tighten the assignment pages' wording. Where an assignment has multiple parts or multiple options (for example, a choice of tracks, topics, or deliverables), give each part or option its own page and link to it from the parent assignment page, so no single page has to carry all of them.
  - **Lecture decks:** simplify the language in the LiaScript decks (shorter sentences, fewer asides per slide), and split any deck that covers several distinct topics into focused decks that the syllabus links to individually.
  - When splitting pages, keep the syllabus `dlink` / `rlink` entries, the Canvas deploy (`ursinus_canvas.py` and the inline-change script), and the rubric `rubricpath` references pointing at the right pages, and update the Canvas shell with a dry-run-first inline change if titles or links move.

- [ ] Instructional design pass on the notes and LiaScript templating: shift detailed explanations from the notes into fully worked tutorials, keep the notes concise for live in-class use, and link each tutorial from its notes page (and possibly from the syllabus); structure the notes for learning (objectives up front, short checks for understanding, consistent layout); incorporate Universal Design for Learning (UDL) principles (multiple means of engagement, representation, and action and expression); meet WCAG accessibility guidelines and check each page with the WebAIM WAVE evaluation tool; and improve the LiaScript templates (shared macros and reusable components, consistent deck structure) so new and existing decks stay consistent. (added 2026-10-29)
  - From the session "Access by Design: AI Strategies for Inclusive Course Design in Higher Education" by Loffert and Xie (2026 AAC&U Conference on AI and Higher Education), slide "AI-powered content organization": use AI to organize content clearly, logically, and in multiple formats, with a consistent, predictable layout for course materials and assignment deadlines. Starter prompt: "I am [role] teaching a [specific course, size, level, meeting lengths/times per week] and need help designing a consistent, predictable layout for my course materials and deadlines, with a focus on accessibility and Universal Design for Learning (UDL) principles. Please create a template that I can use for each week of the course. This template should include sections for the following: weekly overview, learning objectives, readings, assignments, etc."
  - From the session "Access by Design: AI Strategies for Inclusive Course Design in Higher Education" by Loffert and Xie (2026 AAC&U Conference on AI and Higher Education), slide "AI-powered scaffolding": use AI to provide clear, step-by-step instructions for existing assignments or projects. Starter prompt: "[copy and paste or attach existing assignment] Rewrite this assignment into a clear, student-facing brief that supports Universal Design for Learning (UDL). Focus on clarity, accessibility, and step-by-step guidance. Use plain, direct language that anticipates confusion and avoids jargon."
  - Consider an autoresearch loop: an agent that audits each notes page, tutorial, and LiaScript deck against WCAG (checked with WAVE) and the UDL principles, applies fixes, re-evaluates, and iterates until the pages pass. (added 2026-10-29)

- [ ] Consider proficiency-based grading standards (for example, standards- or specifications-based grading) that reward on-time submissions and consistent, sustained effort across the term. (added 2026-10-29)

- [ ] Bring back the cross-team mock technical interview next term, with its own class time instead of a slot inside a sprint studio: pair students from different teams for ten-minute rounds on their own pipeline, a design decision, and a bug story, and restore its Demo Day Guide section, self-check row, and reflection prompts. (added 2026-10-31)
- [ ] Bring back a confidential peer pulse at the Sprint 1 boundary, with a named channel (for example a private Canvas survey) and a due date: each member rates themselves and each teammate 1-5 on the CATME dimensions, with a sentence of evidence for any 2 or below. (added 2026-10-31)

- [ ] Align the lectures, tutorials, and activities with the assignments and labs, so that each one prepares students for the assignment it leads to.

- [ ] Simplify the lectures so they build up the scaffolding the assignments need, which then lets the assignments carry less scaffolding themselves.

- [ ] Make the project more defined and project-based, and more practical for groups to execute: clearer coordination (who does what, by when) and a focus on group accountability.

- [ ] Simplify the Overview assignment and streamline its software setup. Leave the Warmup syllabus survey assignment unchanged.

- [ ] Refine the rubrics and the assignment steps: make each rubric row match what the assignment steps ask students to do, and make each step concrete enough to check.

- [ ] Add an ungraded interview with each student (a short one-on-one conversation about their work and progress).

- [ ] Add a grading component tied to on-time submissions.

- [ ] Add more on typing: type systems beyond the current Type Systems session (for example static and dynamic typing, type inference, and gradual typing), with examples students can run. (added 2026-11-16)

- [ ] Add advanced memory management and dynamic pointers: manual allocation and deallocation, pointers and references, dangling pointers and leaks, and how garbage collection and ownership each answer those problems. (added 2026-11-16)

- [ ] Add modern languages such as Rust, using them to show how newer languages handle typing and memory safety (for example Rust's ownership and borrowing). (added 2026-11-16)

- [ ] Add a bit more Prolog at the beginning of the course, so logic programming appears alongside the other paradigms in the opening weeks. (added 2026-11-16)

- [ ] Have students submit any warmup survey in Canvas. This supersedes the earlier instruction to leave the warmup survey unchanged; the Overview assignment TODO is unaffected.
- [ ] Include an updated syllabus quiz based on the current syllabus.
- [ ] Develop POGIL activities for course topics, starting with canonical LR(1) parsing.
- [ ] Expire assignments automatically when the late penalty would bring the score to zero or on the last class day, whichever comes first: update the code/ scripts (Canvas deploy, syllabus tooling) and the course skills that set due and lock dates, and install the updated skills wherever they are used.
- [ ] Consider making the number of on-time submissions and attendance graded Gradebook elements (for example, Canvas assignment groups or columns that count toward the final grade), and update the syllabus grading section and the code/ scripts that build the Gradebook to match.
