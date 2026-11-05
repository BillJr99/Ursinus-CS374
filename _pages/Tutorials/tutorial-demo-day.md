---
layout: textbook
permalink: /Tutorials/DemoDayGuide
title: "CS374: Demo Day: External Guests"

info:
  coursenum: CS374
  eyebrow: "Tutorial"
  numbering: false
  objectives:
    - "Prepare a one-page brief"
    - "Present your language to guests"

tags:
  - final-project
  - presentation

---
# Demo Day: External Guests

*To prepare you to present your language to people outside the course (invited guests at Demo Day, and eventually interviewers and colleagues) by practicing the plain-language pitch, the known limitation, and the detailed walk-through of work you actually did.*

### Goals

- To open your project for a non-specialist in ninety seconds: what the language is, why it exists, and what working means, without jargon
- To handle questions honestly, including redirecting a question you cannot answer and disclosing a known limitation without being asked
- To connect the project to what comes next, whether that is a portfolio story, a resume conversation, or venues for presenting student work beyond the course

### Background Reading and References

- [Team Language Project]({{ site.baseurl }}/Projects/TeamLanguage)
- [ShipIt Guide: Repo Hygiene, README, Packaging, and Your Portfolio]({{ site.baseurl }}/Tutorials/ShipIt)

This guide is not separately graded.  The presentation is assessed within the Team Language Project's Demo Day Presentation dimension.

Demo Day is not a private class ritual.  Alumni, industry guests, and faculty from other departments may be in the room as audience members and Q&A panelists, invited as available.  Your grade never depends on who attends.  The skills the day demands are exactly the ones a technical interview demands: explain a system you built, in plain language first and in full depth on request, defend your decisions, and be honest about what does not work.  This guide prepares you for both audiences at once.  Nothing here is extra work; it is rehearsal for work you already owe.

### Demo Day Format and Schedule

All teams present within the final exam period.  Each team has a hard cap of **9 minutes**, followed by a 1-minute transition while the next team plugs in.  Nine minutes rewards a rehearsed demo, so time your run-through and cut material rather than rushing it.  The order of presentation is set by lot: teams draw lots in the release-hardening studio, so you know your slot before the day.

### What Strong Demo Day Work Looks Like

- **The opener lands with someone who has never heard of a parser.**  "We built a small programming language for describing drum patterns.  You type a pattern, our system checks it, understands it, and plays it back as timed events.  I built the part that turns your text into a structure the computer can walk."  Ninety seconds, no jargon, and it ends with what *working* looks like.
- **Keep the depth available on demand, and do not impose it up front.**  When a guest asks "how does it actually work?", the answer walks one line of code through the whole pipeline (characters to tokens to tree to value) at whatever level the asker's follow-ups invite.
- **Volunteer your limitations before anyone has to pull them out of you.**  Strong presenters disclose a known limitation with its triage rationale before anyone asks.  It reads as command of the work, because it is.
- **Questions come back.**  The best conversations at Demo Day are two-way: ask the guest what they build, what languages their team uses, and what they wish new graduates knew.

### The One-Page Brief: Talking to Guests

Have these five moves rehearsed before Demo Day:

1. **The ninety-second opener.**  What the language is, the niche it serves, who would use it, and one sentence on what you personally built.  Write it, say it aloud, and cut every term a non-CS friend would stumble on.
2. **The three-sentence architecture.**  The pipeline in plain words: *text comes in; the lexer breaks it into words; the parser builds the sentence structure; the evaluator walks that structure and produces the answer.*  Then one sentence on where your distinctive feature lives in that pipeline.
3. **The known limitation.**  One known limitation, stated plainly, with why you triaged it as disclose-rather-than-fix.  Practice saying it without apologizing.
4. **The redirect.**  For questions you cannot answer: "I don't know, my teammate built that part, let me hand you to them," or "I don't know, but here's how I'd find out."  Both are strong answers.  Bluffing is the only weak one.
5. **The question back.**  Prepare two real questions to ask a guest, about their work, their team's languages and tools, or their path.  Demo Day is a networking event wearing a final-exam costume; treat the conversation as two-way.

### Taking It Further

The project does not have to end at Demo Day:

- **[CCSC-Eastern](https://sites.google.com/site/ccsceastern/)** and similar regional conferences run student poster sessions.  A team language with a live REPL demo is exactly the kind of work they exist to present.  Talk to the instructor about submitting; the proposal you already wrote is most of the abstract.
- **Campus research and creative-work showcases** welcome course projects of this scope.  Presenting there is a low-stakes rehearsal for any external venue.
- **Your profile.**  The [ShipIt guide]({{ site.baseurl }}/Tutorials/ShipIt)'s Stage 4 (the pinned repository and 200-word project story) is the durable version of everything you rehearsed here.  Update your resume and LinkedIn while the numbers (test counts, sample programs, the verified install) are fresh.

### Demo Day Frequently Asked Questions

**Q: Will there definitely be external guests at Demo Day?**
A: Guests are invited as available.  Some years the room is full; some years it is classmates and faculty.  Prepare the same either way: the rubric's multi-audience expectations do not change.

**Q: Does talking to guests affect my grade?**
A: The Demo Day presentation is graded by its existing rubric dimension.  Guest attendance and guest reactions are never grading conditions.

**Q: What should I wear / bring on Demo Day?**
A: Whatever you present comfortably in.  Bring a machine with the demo rehearsed and a fallback (a recording or transcript of the REPL session) in case of technical trouble.  A rehearsed fallback is professional practice, and nobody will read it as doubt.

### Demo Day Reflection Prompts

Answer individually after Demo Day:

- Which question made you realize you understood something less well than you thought, and what would you do about it next time?

### Demo Day Self-Check

| Criterion | Pre-Emerging | Beginning | Progressing | Proficient |
|---|---|---|---|---|
| Self-Check: Guest-Facing Communication | I cannot explain the project without assuming the listener took this course | I can describe the language, but my opening runs long, leans on jargon, or hides what does not work | I can open the project in about ninety seconds in plain language and disclose a limitation when asked, though my answers to unexpected questions still wobble | I can open the project in ninety seconds in plain language, volunteer one rehearsed limitation with its triage rationale, redirect a question I cannot answer honestly ("I don't know, but here is how I would find out"), and ask a guest a real question back |
| Self-Check: Portfolio Story | I have no way to show this project to anyone outside the course | I can point at the repository but cannot yet tell its story in a way a recruiter would follow | My 200-word project story exists and names my contribution, though it is not yet linked from anywhere or rehearsed aloud | My project story is written, linked from my profile or portfolio per the ShipIt guide, rehearsed aloud as a two-minute narrative, a drafted (publication-optional) LinkedIn-style post exists, and I can produce the evidence behind every claim in it on request |
