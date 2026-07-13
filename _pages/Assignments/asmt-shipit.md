---
layout: assignment
permalink: /Assignments/ShipIt
title: "CS374: Principles of Programming Languages - ShipIt Guide: Repo Hygiene, README, Packaging, and Your Portfolio"

info:
  coursenum: CS374
  purpose: "To turn your team's language repository into a public, professional artifact — one a stranger can run, a recruiter can read, and each teammate can point to from a portfolio — so the semester's work exists in the world under your names."
  tilt:
    task: "Before Demo Day, bring your Team Language Project repository through the four stages below — repository hygiene, a recruiter-legible README, packaging for installation, and a portfolio entry for each teammate — and self-assess against the checklist."
    criteria: "Self-assessed against the checklist below; the same checklist is scored within the Team Language Project's Documentation and Reproducibility dimension — nothing is submitted separately. See the self-check rubric for the full breakdown."
  points: 0
  goals:
    - To publish the team language repository in a state a stranger can clone, install, and run from the README alone
    - To write a README that answers what the language is, how to install it, and how to run a first program in thirty seconds, with each member's contribution credited
    - To package the language for installation with pip, npm, or Docker, verified by a teammate who did not do the packaging
    - To create a personal portfolio entry — the repository pinned or linked from each member's GitHub profile or portfolio page with a short project story suitable for a resume
  rubric:
    - weight: 30
      description: "Self-Check: Repository Hygiene"
      preemerging: Our repository is private or cannot be found, has no license, or has credentials or secrets somewhere in its history
      beginning: Our repository is public with a license, but dependencies are unpinned, the top level is cluttered with scratch files, or our team process (issues, pull requests, decision log) is invisible in the repository
      progressing: Our repository is public, licensed, and clean at the top level, with pinned dependencies and visible team process, though a minor gap remains such as a stale branch or an untracked configuration step
      proficient: Our repository is public with a license and a clean, self-explanatory top-level layout; dependencies and versions are pinned; no secrets or personal data appear anywhere in the history; and our issues, pull requests, and decision log make the team's process legible to an outsider
    - weight: 30
      description: "Self-Check: README and Language Reference Quality"
      preemerging: Our README is missing, or only an author could follow it
      beginning: Our README describes the language but a stranger could not install and run a first program from it alone, or no teammate is credited
      progressing: Our README answers what, install, and first program in thirty seconds and links the language reference, with a minor gap such as a missing sample output or an out-of-date badge
      proficient: Our README answers what the language is, how to install it, and how to run a first program in thirty seconds; shows a sample program with its output; carries a passing CI badge; links the language reference and SEMANTICS.md; and credits each member's contribution by name
    - weight: 25
      description: "Self-Check: Packaging and Distribution"
      preemerging: The only way to run our language is to reproduce our development environment by hand
      beginning: A packaging path (pip, npm, or Docker) exists but has not been verified by anyone who did not build it
      progressing: Our language installs via pip, npm, or Docker following the README, verified cold by the teammate who did not do the packaging, though a minor gap remains such as a missing version tag
      proficient: Our language installs via pip, npm, or Docker following the README alone; the installation was verified cold by the teammate who did not do the packaging, and their confirmation is recorded; and the release carries a semantic version tag matching the submission
    - weight: 15
      description: "Self-Check: Personal Portfolio and GitHub Profile"
      preemerging: Nothing links me to this project outside the course
      beginning: The repository is linked from my profile or portfolio, but with no story — a visitor cannot tell what I did or why it matters
      progressing: The repository is pinned or linked from my GitHub profile or portfolio page with a short description, though my individual contribution is not yet legible
      proficient: The repository is pinned or linked from my GitHub profile or portfolio page with a project story of roughly 200 words — the problem, what we built, and the evidence — that names my individual contribution and is ready to reuse on a resume and at Demo Day
  readings:
    - rtitle: "Publishing Your Language — pip, npm, and Docker"
      rlink: "https://www.billmongan.com/Ursinus-CS374-Fall2026/Tutorials/PublishingYourLanguage"
    - rtitle: "CI and TDD for Interpreters"
      rlink: "https://www.billmongan.com/Ursinus-CS374-Fall2026/Tutorials/CITDDForInterpreters"
    - rtitle: "Team Language Project"
      rlink: "https://www.billmongan.com/Ursinus-CS374-Fall2026/Projects/TeamLanguage"

tags:
  - publishing
  - portfolio
  - documentation
  - team

---

This guide is not separately graded; its checklist is assessed within the Team Language Project's **Documentation and Reproducibility** dimension.

By Demo Day your team will have built something few undergraduates can claim: a working programming language, designed and implemented end to end. This guide — required preparation for the final submission — makes sure that work *exists in the world* in a form that does it justice: a public repository a stranger can run, a README a recruiter can read in thirty seconds, an installation path that works cold, and a portfolio entry under each of your names. The self-check rewards finish, not scope: a small language with a spotless repository, a legible README, and a verified install demonstrates more than an ambitious one nobody else can run. Run the checklist as a team during the release-hardening studio, before Demo Day.

---

## What Strong Work Looks Like

Strong work has these qualities:

- **A stranger succeeds without you in the room.** The decisive test for every stage of this guide is the cold test: someone who was not on your team — or the teammate who did *not* do the work — follows the public record alone and it works. "Setup was tested by the teammate who did not write it" is already in the project rubric; this guide extends the same discipline to installation and the README.
- **The README opens like an elevator pitch, not a lab report.** The first screen answers three questions: what is this language and what is its niche, how do I install it, and what does a first program look like — with its output shown. Details (the full grammar, the semantics, the extension guides) are linked, not inlined.
- **The repository tells the team's story by itself.** Issues and pull requests show the sprints, the decision log shows the contested calls, and the README's credits section names who built what. A visitor — a grader, a recruiter, a future you — can reconstruct the process without asking anyone.
- **The portfolio entry is specific.** A weak story says "We built a programming language for class." A strong story says: "Our team of four designed and shipped a query language over in-memory lists with a Hindley–Milner type checker. I built the parser and the AST layer, property-tested with Hypothesis, and wrote the differential test harness that caught three semantics bugs before Demo Day."

Weak work has a private repository, a README that assumes the reader attended the class, an install path nobody has tried cold, and no trace of the project anywhere under your own name.

---

## Stage 1: Repository Hygiene

Make the repository presentable before making it prominent:

- **Make it public**, with a `LICENSE` file (MIT or BSD-3-Clause are fine defaults; agree as a team). Everything in the project rubric assumes a repository a stranger can reach.
- **Audit the history for secrets and personal data.** Search the full history — not just the current tree — for tokens, passwords, and anything personal that does not belong in public. If you find any, rotate the credential and consult the instructor before rewriting history.
- **Pin your dependencies** and state your toolchain versions (Python version, `uv` lock file or `requirements.txt` with versions), exactly as the project's reproducibility requirement demands.
- **Clean the top level.** A visitor should see the README, the license, the source package, the tests, the sample programs, the language reference, and `SEMANTICS.md` — not scratch files, stale experiments, or `old_parser_v2_final.py`.
- **Leave the process visible.** Do not squash away your issues, pull requests, or decision log — they are evidence of the professional practice the rubric credits, and they are what makes the repository more than a code dump.

---

## Stage 2: The Recruiter-Legible README

Rewrite the README so its first screen passes the thirty-second test:

1. **What it is** — the language name, its niche, and a one-paragraph pitch (your proposal already contains this; compress it).
2. **Install** — the one command that installs it (see Stage 3).
3. **First program** — a small sample program *and its output*, so a reader sees the language run without installing anything.

Then, below the fold:

- A **CI badge** showing the test suite passing on the submission commit (the [CI and TDD for Interpreters](/Tutorials/CITDDForInterpreters) tutorial covers wiring this up).
- Links to the **language reference**, **`SEMANTICS.md`**, and the sample program suite.
- A **credits section** naming each teammate and what they built — contribution attribution is part of the self-check, and it is what lets each of you point at this repository individually.

The teammate who did not write the README performs the cold test: fresh clone, follow it top to bottom, note every place they stall.

---

## Stage 3: Package Your Language

Give your language a real installation path — one of:

- **pip:** package the implementation (a `pyproject.toml` with an entry point so `your-language` runs the REPL and `your-language file.lang` runs a program). Installing directly from the repository (`pip install git+https://...`) is sufficient; publishing to PyPI is stretch work under the Extensions Menu's *Libraries and Packaging* entry.
- **npm:** for JavaScript implementations, a scoped package with a working `bin`.
- **Docker:** a small image whose default command opens the REPL and which can run a mounted program file.

The step-by-step mechanics live in the [Publishing Your Language — pip, npm, and Docker](/Tutorials/PublishingYourLanguage) tutorial; this guide only insists on the discipline around it:

- **Tag the release** with a semantic version (`v1.0.0` for the Demo Day submission) so the installed artifact and the graded commit are the same thing.
- **Verify cold.** The teammate who did *not* do the packaging installs it on a machine (or in a fresh container) that has never seen the project, following the README alone, and records a one-line confirmation with their name in the report.
- **Audit before you publish.** Review what the package or image actually contains (a `pip` sdist listing, `npm pack --dry-run`, or the image layer listing) — no test fixtures, no secrets, no personal files.

---

## Stage 4: The Portfolio Entry

The last stage is individual. Each teammate:

- **Pins or links the repository** from their GitHub profile (or personal portfolio page). If you do not have a profile README, this is the moment to create one — it is a ten-minute job with an outsized payoff.
- **Writes a project story of roughly 200 words**: the problem (what niche, why a new language), what the team built (the pipeline, the distinctive feature, any extensions), and the evidence (the repo link, the CI badge, the verified install, a test-suite number). Name your individual contribution explicitly — "I built X" — because that is the sentence a resume bullet and an interview answer are made from.
- **Reuses the story.** The same story is your opening move with guests at Demo Day (see the [Demo Day Guide](/Assignments/DemoDayGuide)) and the seed of the resume bullet you will write when you next update your materials.

---

## Frequently Asked Questions

**Q: Do we have to publish to PyPI or npm?**
A: No. An installation path that works cold from the public repository (`pip install git+...`, a Dockerfile, or an npm install from the repo) satisfies this guide. A public registry release is stretch work credited through the Extensions Menu's *Libraries and Packaging* entry.

**Q: Our repository has been private all semester. When should we flip it public?**
A: During the release-hardening studio at the latest — after the Stage 1 hygiene audit, before Demo Day. Do the secrets audit *first*: public means the full history is public.

**Q: One teammate doesn't want the repository on their profile. Is that a problem?**
A: The repository-side items (public repo, README credits) are team obligations; the profile pin is personal and the self-check is satisfied by a link from a portfolio page instead. If someone prefers not to be named publicly at all, talk to the instructor — there is always an accommodation, and the credit lives in the graded report regardless.

**Q: Does the ShipIt self-check add points?**
A: No — it is how you earn the points that already exist. The Documentation and Reproducibility dimension of the Team Language Project rubric names this checklist; running it honestly during release hardening is how you arrive at Demo Day already knowing that score.

---

## Reflection Prompts

Answer these as a team during release hardening, and individually as part of your contribution statement:

- What did the cold test catch that the authors could not see, and why couldn't they see it?
- Read your own 200-word project story as a stranger: what claim in it is best supported by evidence in the repository, and what claim still needs shoring up?
- Do you certify that the repository and your portfolio story accurately represent your team's and your own work? Please identify any and all portions that were not originally created by your team.
- AI disclosure: list any generative-AI tools you used, for what, and how you verified the results (or state 'none').
- Approximately how many hours did this guide's checklist take your team (I will not judge you for this at all...I am simply using it to gauge if the assignments are too easy or hard)?
