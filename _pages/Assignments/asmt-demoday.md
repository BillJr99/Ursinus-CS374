---
layout: assignment
permalink: /Assignments/DemoDayGuide
title: "CS374: Principles of Programming Languages - Demo Day Guide: External Guests and Technical Interview Practice"

info:
  coursenum: CS374
  purpose: "To prepare you to present your language to people outside the course — invited guests at Demo Day, and eventually interviewers and colleagues — by practicing the plain-language pitch, the honest limitation, and the interview-style deep dive on work you actually did."
  tilt:
    task: "Read the guest-facing brief, take part in the cross-team mock technical interview during the Week 14 sprint studios, and arrive at Demo Day ready to present your language to a mixed audience of classmates, faculty, and invited external guests."
    criteria: "Nothing is separately graded here — the presentation itself is assessed within the Team Language Project's Demo Day Presentation dimension, and the mock-interview rehearsal is credited as class participation. Use the self-check below to know you are ready."
  points: 0
  goals:
    - To open your project for a non-specialist in ninety seconds — what the language is, why it exists, and what working means — without jargon
    - To practice the interview form on your own work - explaining your pipeline, defending a design decision, and telling a real bug story with its fix
    - To handle questions honestly, including redirecting a question you cannot answer and disclosing a known limitation without being asked
    - To connect the project to what comes next - a portfolio story, a resume conversation, and venues for presenting student work beyond the course
  rubric:
    - weight: 40
      description: "Self-Check: Guest-Facing Communication"
      preemerging: I cannot explain the project without assuming the listener took this course
      beginning: I can describe the language, but my opening runs long, leans on jargon, or hides what does not work
      progressing: I can open the project in about ninety seconds in plain language and disclose a limitation when asked, though my answers to unexpected questions still wobble
      proficient: I can open the project in ninety seconds in plain language, volunteer one rehearsed limitation with its triage rationale, redirect a question I cannot answer honestly ("I don't know, but here is how I would find out"), and ask a guest a genuine question back
    - weight: 30
      description: "Self-Check: Mock Technical Interview"
      preemerging: I skipped the rehearsal or could not explain my own component
      beginning: I explained my component but not how it connects to the rest of the pipeline, or I could not tell a single concrete bug story
      progressing: I walked my partner through the pipeline token-to-value, defended one design decision, and told one bug story, though I leaned on notes or slides
      proficient: Without slides, I explained the pipeline end to end, defended a design decision by naming the alternative we rejected and why, told a bug story with its regression test, and asked my partner at least one probing question about their language when roles reversed
    - weight: 30
      description: "Self-Check: Portfolio Story"
      preemerging: I have no way to show this project to anyone outside the course
      beginning: I can point at the repository but cannot yet tell its story in a way a recruiter would follow
      progressing: My 200-word project story exists and names my contribution, though it is not yet linked from anywhere or rehearsed aloud
      proficient: My project story is written, linked from my profile or portfolio per the ShipIt guide, rehearsed aloud as a two-minute narrative, and I can produce the evidence behind every claim in it on request
  readings:
    - rtitle: "Sprint Studio Protocol"
      rlink: "https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS374-Fall2026/gh-pages/_pages/Activities/liascript-sprintstudio.md"
    - rtitle: "Team Language Project"
      rlink: "https://www.billmongan.com/Ursinus-CS374-Fall2026/Projects/TeamLanguage"
    - rtitle: "ShipIt Guide: Repo Hygiene, README, Packaging, and Your Portfolio"
      rlink: "https://www.billmongan.com/Ursinus-CS374-Fall2026/Assignments/ShipIt"

tags:
  - demo-day
  - communication
  - interview
  - portfolio
  - participation

---

This guide is not separately graded; the presentation is assessed within the Team Language Project's **Demo Day Presentation** dimension, and the mock-interview rehearsal is credited as **class participation**.

Demo Day is not a private class ritual. Alumni, industry guests, and faculty from other departments may be in the room as audience members and Q&A panelists — invited **as available**; your grade never depends on who attends — and the skills the day demands are exactly the ones a technical interview demands: explain a system you built, in plain language first and full depth on request, defend your decisions, and be honest about what does not work. This guide prepares you for both audiences at once. Nothing here is extra work — it is rehearsal for work you already owe.

---

## What Strong Work Looks Like

- **The opener lands with someone who has never heard of a parser.** "We built a small programming language for describing drum patterns. You type a pattern, our system checks it, understands it, and plays it back as timed events. I built the part that turns your text into a structure the computer can walk." Ninety seconds, no jargon, ends with what *working* looks like.
- **Depth is available on demand, not imposed up front.** When a guest asks "how does it actually work?", the answer walks one line of code through the whole pipeline — characters to tokens to tree to value — at whatever level the asker's follow-ups invite.
- **The limitation is volunteered, not extracted.** Strong presenters disclose a known limitation with its triage rationale before anyone asks. It reads as command of the work, because it is.
- **Questions come back.** The best conversations at Demo Day are two-way: ask the guest what they build, what languages their team uses, what they wish new graduates knew.

---

## The One-Page Brief: Talking to Guests

Have these five moves rehearsed before Demo Day:

1. **The ninety-second opener.** What the language is, the niche it serves, who would use it, and one sentence on what you personally built. Write it, say it aloud, cut every term a non-CS friend would stumble on.
2. **The three-sentence architecture.** The pipeline in plain words: *text comes in; the lexer breaks it into words; the parser builds the sentence structure; the evaluator walks that structure and produces the answer.* Then one sentence on where your distinctive feature lives in that pipeline.
3. **The honest limitation.** One known limitation, stated plainly, with why you triaged it as disclose-rather-than-fix. Practice saying it without apologizing.
4. **The redirect.** For questions you cannot answer: "I don't know — my teammate built that part, let me hand you to them," or "I don't know, but here's how I'd find out." Both are strong answers. Bluffing is the only weak one.
5. **The question back.** Prepare two genuine questions to ask a guest — about their work, their team's languages and tools, or their path. Demo Day is a networking event wearing a final-exam costume; treat the conversation as two-way.

---

## The Mock Technical Interview (Week 14 Sprint Studios)

During the Week 14 studio sessions, you will pair **across teams** for interview rounds, credited as class participation:

**Format.** Ten minutes per round, then swap roles. The interviewer asks from the question bank below (or invents better ones); the interviewee answers **without slides** — a whiteboard or paper is allowed, your repository is not. Close each round with a feedback card in the gallery-walk vocabulary: one **Strength**, one **Question** the interviewee should be ready for at Demo Day.

**Question bank** (interviewers: pick three or four, follow the answers, dig where they wobble):

- Walk me through what happens when this one line of your language runs — from characters to final value, naming each stage and what it hands to the next.
- Why an environment chain instead of one big dictionary? What breaks in your language if you flatten it?
- How would you add feature X (the interviewer picks something plausible — a `while` loop, string interpolation, a new operator)? Which pipeline stages does it touch, and which one is the risky edit?
- Tell me about a bug that lived *between* two stages — where the fix wasn't in either component but in the contract between them.
- What design decision would you reverse with one more sprint, and what would reversing it cost now?
- Your parser accepts a program your evaluator crashes on. Whose bug is that, and how do you decide?

**Why cross-team pairs:** explaining your language to someone who has never seen it is the whole game — your own teammates know too much to be useful practice, and interviewing *them* about their language teaches you what good interviewer questions feel like from the inside.

---

## Taking It Further

The project does not have to end at Demo Day:

- **[CCSC-Eastern](https://ccscne.org/)** and similar regional conferences run **student poster sessions** — a team language with a live REPL demo is exactly the kind of work they exist to showcase. Talk to the instructor about submitting; the proposal you already wrote is most of the abstract.
- **Campus research and creative-work showcases** welcome course projects of this scope; presenting there is a low-stakes rehearsal for any external venue.
- **Your profile.** The [ShipIt guide](/Assignments/ShipIt)'s Stage 4 — the pinned repository and 200-word project story — is the durable version of everything you rehearsed here. Update your resume and LinkedIn while the numbers (test counts, sample programs, the verified install) are fresh.

---

## Frequently Asked Questions

**Q: Will there definitely be external guests at Demo Day?**
A: Guests are invited as available — some years the room is full, some years it is classmates and faculty. Prepare the same either way: the rubric's multi-audience expectations do not change, and the mock-interview rehearsal happens regardless.

**Q: Does talking to guests affect my grade?**
A: The Demo Day presentation is graded by its existing rubric dimension; guest attendance and guest reactions are never grading conditions. The mock-interview rehearsal is credited as ordinary class participation for the studio session it happens in.

**Q: I get nervous in interview settings. Can I opt out of the mock interview?**
A: Talk to the instructor beforehand — the format can be adjusted (a smaller room, a written walk-through, extra prep time). The rehearsal exists precisely because the tenth time explaining your pipeline is calmer than the first; we want you to spend nervous repetitions here, where they are cheap.

**Q: What should I wear / bring on Demo Day?**
A: Whatever you present comfortably in. Bring a machine with the demo rehearsed and a fallback (a recording or transcript of the REPL session) in case of technical trouble — rehearsed fallbacks are professional practice, not admissions of doubt.

---

## Reflection Prompts

Answer individually after the mock-interview rehearsal:

- Which question made you realize you understood something less well than you thought, and what did you do about it before Demo Day?
- What did you learn from being the *interviewer* that you could not have learned as the interviewee?
- Approximately how many hours did you spend preparing with this guide (I will not judge you for this at all...I am simply using it to gauge if the assignments are too easy or hard)?
