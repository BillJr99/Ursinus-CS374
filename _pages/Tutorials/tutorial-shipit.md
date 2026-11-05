---
layout: textbook
permalink: /Tutorials/ShipIt
title: "CS374: The ShipIt Checklist"

info:
  coursenum: CS374
  eyebrow: "Tutorial"
  numbering: false
  objectives:
    - "Publish a repository a stranger can clone and run"
    - "Write a README, package the language, and make a portfolio entry"

tags:
  - final-project
  - release

---
# Shipping Your Language: The ShipIt Checklist

*To turn your team's language repository into a public, professional artifact: one a stranger can run, a recruiter can read, and each teammate can point to from a portfolio, so the semester's work exists in the world under your names.*

### Goals

- To publish the team language repository in a state a stranger can clone, install, and run from the README alone
- To write a README that answers what the language is, how to install it, and how to run a first program in thirty seconds, with each member's contribution credited
- To package the language for installation with pip, npm, or Docker, verified by a teammate who did not do the packaging
- To create a personal portfolio entry: the repository pinned or linked from each member's GitHub profile or portfolio page with a short project story suitable for a resume

### Background Reading and References

- [Publishing Your Language: pip, npm, and Docker]({{ site.baseurl }}/Tutorials/PublishingYourLanguage)
- [CI and TDD for Interpreters]({{ site.baseurl }}/Tutorials/CITDDForInterpreters)
- [Team Language Project]({{ site.baseurl }}/Projects/TeamLanguage)

This guide is not separately graded.  Its checklist is assessed within the Team Language Project's Documentation and Reproducibility dimension.

By Demo Day your team will have built something few undergraduates can claim: a working programming language, designed and implemented end to end.  This guide is required preparation for the final submission.  It makes sure that work *exists in the world* in a form that does it justice: a public repository a stranger can run, a README a recruiter can read in thirty seconds, an installation path that works cold, and a portfolio entry under each of your names.  The self-check rewards a finished job over an ambitious one.  A small language with a spotless repository, a legible README, and a verified install demonstrates more than an ambitious one nobody else can run.  Run the checklist as a team during the release-hardening studio, before Demo Day.

### What Strong Work Looks Like

Strong work has these qualities:

- **A stranger succeeds without you in the room.**  The decisive test for every stage of this guide is the cold test: someone who was not on your team (or the teammate who did *not* do the work) follows the public record alone, and it works.  "Setup was tested by the teammate who did not write it" is already in the project rubric; this guide extends the same discipline to installation and the README.
- **The README opens like an elevator pitch rather than a lab report.**  The first screen answers three questions: what is this language and what is its niche, how do I install it, and what does a first program look like, with its output shown.  Details (the full grammar, the semantics, the extension guides) are linked, not inlined.
- **The repository tells the team's story by itself.**  Issues and pull requests show the sprints, the decision log shows the contested calls, and the README's credits section names who built what.  A visitor (a grader, a recruiter, a future you) can reconstruct the process without asking anyone.
- **The portfolio entry is specific.**  A weak story says "We built a programming language for class."  A strong story says: "Our team of three designed and shipped a query language over in-memory lists with a Hindley-Milner type checker.  I built the parser and the AST layer, property-tested with Hypothesis, and wrote the differential test harness that caught three semantics bugs before Demo Day."

Weak work has a private repository, a README that assumes the reader attended the class, an install path nobody has tried cold, and no trace of the project anywhere under your own name.

### ShipIt Stage 1: Repository Hygiene

Make the repository presentable before making it prominent.

> **Do this.**
> 1. **Make it public**, with a `LICENSE` file (MIT or BSD-3-Clause are fine defaults; agree as a team).  Everything in the project rubric assumes a repository a stranger can reach.
> 2. **Audit the history for secrets and personal data.**  Search the full history (the current tree is not enough) for tokens, passwords, and anything personal that does not belong in public.  If you find any, rotate the credential and consult the instructor before rewriting history.
> 3. **Pin your dependencies** and state your toolchain versions (Python version, `uv` lock file or `requirements.txt` with versions), exactly as the project's reproducibility requirement demands.
> 4. **Clean the top level.**  A visitor should see the README, the license, the source package, the tests, the sample programs, the language reference, and `SEMANTICS.md`, not scratch files, stale experiments, or `old_parser_v2_final.py`.
> 5. **Leave the process visible.**  Do not squash away your issues, pull requests, or decision log.  They are evidence of the professional practice the rubric credits, and they are what makes the repository more than a code dump.

### ShipIt Stage 2: The Recruiter-Legible README

Rewrite the README so its first screen passes the thirty-second test.

> **Do this.**
> 1. **What it is**: the language name, its niche, and a one-paragraph pitch (your proposal already contains this; compress it).
> 2. **Install**: the one command that installs it (see Stage 3).
> 3. **First program**: a small sample program *and its output*, so a reader sees the language run without installing anything.
> 4. Below the fold, add a **CI badge** showing the test suite passing on the submission commit (the [CI and TDD for Interpreters]({{ site.baseurl }}/Tutorials/CITDDForInterpreters) tutorial covers wiring this up).
> 5. Below the fold, link the **language reference**, **`SEMANTICS.md`**, and the sample program suite.
> 6. Below the fold, add a **credits section** naming each teammate and what they built.  Contribution attribution is part of the self-check, and it is what lets each of you point at this repository individually.
> 7. Hand it to the teammate who did not write it for the cold test: fresh clone, follow it top to bottom, and note every place they stall.

### ShipIt Stage 3: Package Your Language

Give your language a real installation path, one of:

- **pip:** package the implementation (a `pyproject.toml` with an entry point so `your-language` runs the REPL and `your-language file.lang` runs a program).  Installing directly from the repository (`pip install git+https://...`) is sufficient; publishing to PyPI is stretch work under the Extensions Menu's *Libraries and Packaging* entry.
- **npm:** for JavaScript implementations, a scoped package with a working `bin`.
- **Docker:** a small image whose default command opens the REPL and which can run a mounted program file.

The step-by-step mechanics live in the [Publishing Your Language: pip, npm, and Docker]({{ site.baseurl }}/Tutorials/PublishingYourLanguage) tutorial.  This guide only insists on the discipline around it.

> **Do this.**
> 1. **Tag the release** with a semantic version (`v1.0.0` for the Demo Day submission) so the installed artifact and the graded commit are the same thing.
> 2. **Verify cold.**  The teammate who did *not* do the packaging installs it on a machine (or in a fresh container) that has never seen the project, following the README alone, and records a one-line confirmation with their name in the report.
> 3. **Audit before you publish.**  Review what the package or image actually contains (a `pip` sdist listing, `npm pack --dry-run`, or the image layer listing): no test fixtures, no secrets, no personal files.

### ShipIt Stage 4: The Portfolio Entry

The last stage is individual.

> **Do this.**  Each teammate:
> 1. **Pins or links the repository** from their GitHub profile (or personal portfolio page).  If you do not have a profile README, this is the moment to create one; it is a ten-minute job with an outsized payoff.
> 2. **Writes a project story of roughly 200 words**: the problem (what niche, why a new language), what the team built (the pipeline, the distinctive feature, any extensions), and the evidence (the repo link, the CI badge, the verified install, a test-suite number).  Name your individual contribution explicitly ("I built X"), because that is the sentence a resume bullet and an interview answer are made from.
> 3. **Reuses the story.**  The same story is your opening move with guests at Demo Day (see the [Demo Day Guide]({{ site.baseurl }}/Tutorials/DemoDayGuide)) and the seed of the resume bullet you will write when you next update your materials.
> 4. **Drafts the post.**  Turn the story into a drafted LinkedIn-style post (150-250 words: the niche, what you built, one concrete number (tests passing, sample programs, the install command), and what you learned) and include the draft in the final submission.  Submitting the draft is required; **publishing it is always optional and never graded: your professional profiles are yours.**  The draft exists so that if you choose to post, the post is already written while the language still runs on your machine.

### ShipIt Frequently Asked Questions

**Q: Do we have to publish to PyPI or npm?**
A: No.  An installation path that works cold from the public repository (`pip install git+...`, a Dockerfile, or an npm install from the repo) satisfies this guide.  A public registry release is stretch work credited through the Extensions Menu's *Libraries and Packaging* entry.

**Q: Our repository has been private all semester.  When should we flip it public?**
A: During the release-hardening studio at the latest, after the Stage 1 hygiene audit, before Demo Day.  Do the secrets audit *first*: public means the full history is public.

**Q: One teammate doesn't want the repository on their profile.  Is that a problem?**
A: The repository-side items (public repo, README credits) are team obligations.  The profile pin is personal, and a link from a portfolio page satisfies the self-check instead.  If someone prefers not to be named publicly at all, talk to the instructor; there is always an accommodation, and the credit lives in the graded report regardless.

**Q: Does the ShipIt self-check add points?**
A: No; it is how you earn the points that already exist.  The Documentation and Reproducibility dimension of the Team Language Project rubric names this checklist.  Running it honestly during release hardening is how you arrive at Demo Day already knowing that score.

### ShipIt Reflection Prompts

Answer these as a team during release hardening, and individually as part of your contribution statement:

- What did the cold test catch that the authors could not see, and why couldn't they see it?
- Read your own 200-word project story as a stranger: what claim in it is best supported by evidence in the repository, and what claim still needs shoring up?

### ShipIt Self-Check

| Criterion | Pre-Emerging | Beginning | Progressing | Proficient |
|---|---|---|---|---|
| Self-Check: Repository Hygiene | Our repository is private or cannot be found, has no license, or has credentials or secrets somewhere in its history | Our repository is public with a license, but dependencies are unpinned, the top level is cluttered with scratch files, or our team process (issues, pull requests, decision log) is invisible in the repository | Our repository is public, licensed, and clean at the top level, with pinned dependencies and visible team process, though a minor gap remains such as a stale branch or an untracked configuration step | Our repository is public with a license and a clean, self-explanatory top-level layout; dependencies and versions are pinned; no secrets or personal data appear anywhere in the history; and our issues, pull requests, and decision log make the team's process legible to an outsider |
| Self-Check: README and Language Reference Quality | Our README is missing, or only an author could follow it | Our README describes the language but a stranger could not install and run a first program from it alone, or no teammate is credited | Our README answers what, install, and first program in thirty seconds and links the language reference, with a minor gap such as a missing sample output or an out-of-date badge | Our README answers what the language is, how to install it, and how to run a first program in thirty seconds; shows a sample program with its output; carries a passing CI badge; links the language reference and SEMANTICS.md; and credits each member's contribution by name |
| Self-Check: Packaging and Distribution | The only way to run our language is to reproduce our development environment by hand | A packaging path (pip, npm, or Docker) exists but has not been verified by anyone who did not build it | Our language installs via pip, npm, or Docker following the README, verified cold by the teammate who did not do the packaging, though a minor gap remains such as a missing version tag | Our language installs via pip, npm, or Docker following the README alone; the installation was verified cold by the teammate who did not do the packaging, and their confirmation is recorded; and the release carries a semantic version tag matching the submission |
| Self-Check: Personal Portfolio and GitHub Profile | Nothing links me to this project outside the course | The repository is linked from my profile or portfolio, but with no story; a visitor cannot tell what I did or why it matters | The repository is pinned or linked from my GitHub profile or portfolio page with a short description, though my individual contribution is not yet legible | The repository is pinned or linked from my GitHub profile or portfolio page with a project story of roughly 200 words (the problem, what we built, and the evidence) that names my individual contribution and is ready to reuse on a resume and at Demo Day |
