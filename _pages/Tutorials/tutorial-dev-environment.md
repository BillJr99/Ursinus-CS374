---
layout: default-standard
permalink: /Tutorials/DevEnvironment
title: "CS374: The Course Development Environment"

info:
  coursenum: CS374
  goals:
    - To build and enter the course Docker container, a single environment that runs every CS374 assignment
    - To bind-mount a GitHub-backed workspace so that all work is versioned and pushable from inside the container
    - To configure git identity and credentials (personal access token or SSH) for use inside a container, and to clear git's dubious-ownership error on a bind-mounted repository
    - To practice the full daily loop end to end: start container, work, test, commit, push
    - To explain why container isolation protects the rest of your machine, and set up the native fallback if Docker is not an option

readings:
  - rtitle: "Docker Get Started Guide"
    rlink: "https://docs.docker.com/get-started/"
  - rtitle: "GitHub: Managing your personal access tokens"
    rlink: "https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens"
  - rtitle: "Shell Skills for Language Development (Tutorial)"
    rlink: "../Tutorials/ShellForLanguageDev"

tags:
  - tools
  - docker
  - git
  - setup
---

# The Course Development Environment

This tutorial sets up **one environment that runs every CS374 assignment**.  It is a Docker container with the whole course toolchain preinstalled: Python 3.11 with `pytest`, `hypothesis`, and `ply` for the language-pipeline assignments, plus `flex`, `bison`, `gcc`, and `make` for the generator-toolchain directions and the mininote scaffold, `uv` for Python environments, and a Scheme (`guile`, and `mit-scheme` where Debian builds it for your machine's CPU) for the Functional Programming with Scheme assignment.  The container is bind-mounted onto a directory on your machine that is itself a **git repository with a GitHub remote**, so everything you write inside the container is versioned and pushed like normal work.

Two ideas do all the heavy lifting here, and they are worth stating up front:

1.  **The image is the environment.**  Instead of installing five tools and hoping the versions match the grader's, you build one image from the course Dockerfile.  Everyone's container is byte-for-byte the same environment.
2.  **The mount is the only door.**  The container can see exactly one directory of your machine: the workspace you mount into it.  Your documents, your other courses, your browser profile: invisible.  Meanwhile, everything you create in that workspace lives on *your* disk and on GitHub, so the container itself is disposable.

Work through the numbered steps in order.  Each practice step shows the command *and the output you should expect*; if yours differs, stop and consult the troubleshooting section at the end.  Budget about an hour, most of it waiting for downloads.

If Docker cannot run on your machine at all, skip to **Step 9: The Native Fallback**; it is a complete route, and not a consolation prize.

---

## Step 1: Install Docker Desktop

Download and install [Docker Desktop](https://www.docker.com/products/docker-desktop/) for macOS or Windows, or [Docker Engine](https://docs.docker.com/engine/install/) on Linux.  Accept the defaults.

**Windows: install Ubuntu on WSL2 first, then check two Docker settings.**  Docker Desktop on Windows does not run containers on Windows itself; it runs them inside **WSL2**, the Windows Subsystem for Linux.  Installing the Linux side first, and confirming Docker is wired to it, prevents most of the Windows trouble in this tutorial.

1.  Open **PowerShell as Administrator** and install Ubuntu:

    ```powershell
    wsl --install -d Ubuntu
    ```

    Reboot if it asks.  Then launch **Ubuntu** from the Start menu and set the UNIX username and password it prompts for; these are new, and separate from your Windows account.  (If `wsl --install` is not recognized, your Windows is too old for the one-liner: update Windows, or follow Microsoft's [manual WSL2 install steps](https://learn.microsoft.com/en-us/windows/wsl/install-manual).)

2.  Install Docker Desktop, start it, then open its **Settings** (the gear icon) and verify both of these:
    - **General**: **Use the WSL 2 based engine** is checked.
    - **Resources -> WSL Integration**: integration with your default distro is enabled, and the **Ubuntu** toggle is switched **on**.  Click **Apply & Restart**.

That second setting is the one students most often miss, and its symptom is confusing: Docker Desktop looks perfectly healthy in its own window, but `docker` is not a command inside Ubuntu.

Do the rest of this tutorial from the **Ubuntu** terminal.  It is the smoothest route on Windows by a wide margin: `~` means what it says, paths are ordinary Linux paths, and a repository kept in your WSL2 home directory bind-mounts far faster than one on the Windows side.

**Disk note:** Docker Desktop plus the course image needs roughly **3-5 GB** of free disk.  If your laptop is tight on space, clear room first; a half-downloaded image is the most confusing failure mode in this tutorial.

Start Docker Desktop (on Linux, ensure the daemon is running and your user is in the `docker` group), then verify from a terminal:

```bash
docker run hello-world
```

Expected output (abridged):

```
Hello from Docker!
This message shows that your installation appears to be working correctly.
```

If you instead see `Cannot connect to the Docker daemon`, Docker Desktop is installed but not *running*; launch the application and wait for the whale icon to settle.

---

## Step 2: Create Your Workspace Repository on GitHub

Your course work lives in a private GitHub repository named `cs374-work`.  This is the directory you will mount into the container, and the remote you will push to all semester.

1.  On [github.com](https://github.com/), click **New repository**.
2.  Name: `cs374-work`.  Visibility: **Private**.  Check **Add a README file** (so the repository is cloneable immediately).
3.  Clone it to your machine.

**First, where to put it, and what `~` means.**  The commands in this tutorial use the Unix shorthand `~` for your home folder.  It resolves in macOS Terminal, Linux shells, WSL2, Git Bash, and PowerShell.  It does **not** resolve in the classic Windows Command Prompt (`cmd.exe`), which will leave you in the wrong directory without printing an error.  On Windows, pick one shell and stay with it:

- **PowerShell** or **Windows Terminal**: `~` works as written, as does `$HOME`.  Your home folder is `C:\Users\YOU`, so `~/cs374-work` is `C:\Users\YOU\cs374-work`.
- **Command Prompt (`cmd.exe`)**: substitute `%USERPROFILE%` for `~`, and backslashes for forward slashes: `cd %USERPROFILE%`, and later `cd %USERPROFILE%\cs374-work\.devcontainer`.
- **WSL2 Ubuntu**, the one you installed in Step 1: `~` works as written and your home is `/home/YOU`.  This is the route the tutorial recommends and the one the native fallback in Step 9 assumes; the other two are here for students who skipped WSL2 or prefer a Windows-side shell.

Keep the clone **under your user profile** (or inside your WSL2 home) either way.  Docker Desktop shares those locations with containers by default; a clone on a second drive or a network share is the most common cause of an empty bind mount later.  Everywhere below that you see `~/cs374-work`, read it as whichever form your shell uses.

```bash
cd ~
git clone https://github.com/YOURUSERNAME/cs374-work.git
cd cs374-work
ls -la
```

On Windows Command Prompt, that first line is `cd %USERPROFILE%` instead; the three `git`/`ls` lines are the same everywhere (`ls -la` becomes `dir` if you are not in PowerShell or Git Bash).

Expected output (abridged):

```
Cloning into 'cs374-work'...
...
.git
README.md
```

The `.git` directory means this folder is a git repository; the clone already knows its GitHub remote.  Confirm:

```bash
git remote -v
```

```
origin  https://github.com/YOURUSERNAME/cs374-work.git (fetch)
origin  https://github.com/YOURUSERNAME/cs374-work.git (push)
```

---

## Step 3: Add the Course Container Files

Download the three course container files and place them in a `.devcontainer/` folder inside your clone:

- [Dockerfile]({{ site.baseurl }}/files/devcontainer/Dockerfile): the recipe for the course image, commented line by line
- [docker-compose.yml]({{ site.baseurl }}/files/devcontainer/docker-compose.yml): one-command build/run with the workspace mount
- [devcontainer.json]({{ site.baseurl }}/files/devcontainer/devcontainer.json): VS Code Dev Containers configuration
- (optional) [README.md]({{ site.baseurl }}/files/devcontainer/README.md): the quickstart version of this tutorial

Your repository should now look like this:

```
cs374-work/
  .devcontainer/
    Dockerfile
    docker-compose.yml
    devcontainer.json
  README.md
```

Open the Dockerfile in an editor and *read it*; it is short and every line is commented.  You built Dockerfiles' conceptual vocabulary in your intro courses' shell work; this one is deliberately simple: a base Python image, an `apt-get` layer for the C toolchain and Scheme, a `pip` layer for the Python packages, a short layer that installs `uv`, a non-root `student` user, and `/workspace` as the working directory.

One layer there is worth a second look, because it breaks the usual rule that any failing command fails the build: `mit-scheme` has no Debian package for *every* CPU architecture, so that single install is allowed to fail and print a note instead.  An Apple Silicon Mac may end up with only `guile`, and the image still builds.  This is what it looks like to design a Dockerfile for hardware you do not own.

**Keeping these files current.**  What you just downloaded is a *copy*.  It lives in your repository now, and it will sit there unchanged until you replace it; when the course adds a tool to the container mid-semester, your copy does not follow.  This is the honest cost of the arrangement, and it buys you something worth having: your environment cannot change under you in the middle of an assignment.

So the image carries a datestamp, and you can read it from the container prompt:

```bash
echo $CS374_IMAGE_VERSION
```

```
2026.09.02
```

That is the current version as of this writing.  If yours prints an older date, or prints nothing at all, your container files predate a course update.  Refreshing them is Step 3 again: download the three files over the ones in `.devcontainer/`, rebuild, and commit the diff.

```bash
cd ~/cs374-work/.devcontainer
# re-download Dockerfile, docker-compose.yml, and devcontainer.json here,
# replacing your copies, then:
docker compose build
git add .devcontainer && git commit -m "Refresh course container files"
```

Announcements will say when there is something to refresh.  Checking the datestamp is also the first thing to do when a command the tutorial promises you turns up missing.

Commit the container files; they are part of your work:

```bash
git add .devcontainer
git commit -m "Add course dev container configuration"
```

---

## Step 4: Build and Enter the Container

You have two equivalent front doors.  Pick one; you can switch anytime because both use the same Dockerfile.

**Option A: VS Code Dev Containers (recommended if you use VS Code).**  Install the **Dev Containers** extension, open the `cs374-work` folder, and run **Dev Containers: Reopen in Container** from the command palette.  VS Code builds the image and reopens your repo inside it, with the Python and GitLens extensions preinstalled.  Any terminal you open in VS Code is now *inside* the container.

**Option B: plain Docker Compose (any editor).**  From the `.devcontainer/` folder:

```bash
cd ~/cs374-work/.devcontainer
docker compose build
docker compose run --rm cs374
```

(Windows: that path works as written in PowerShell, Windows Terminal, Git Bash, and WSL2.  In Command Prompt, `cd %USERPROFILE%\cs374-work\.devcontainer`.  The two `docker compose` lines are identical in every shell.)

The first build takes a few minutes (downloading the base image and packages); rebuilds are nearly instant thanks to layer caching.  When it finishes you land at a prompt like:

```
student@a1b2c3d4e5f6:/workspace$
```

That hostname-looking string is the container ID. You are the non-root user `student`, in `/workspace`, which *is* your `cs374-work` repository.  Prove it:

```bash
ls -la
```

```
.devcontainer
.git
README.md
```

**Verify the toolchain.**  Run each of these and capture the output; this transcript is part of the Overview assignment:

```bash
python3 --version
```

```
Python 3.11.14
```

(The patch number may differ; anything 3.11.x is correct.)

```bash
pytest --version
```

```
pytest 8.x.x
```

```bash
python3 -c "import hypothesis, ply; print('hypothesis', hypothesis.__version__, '| ply OK')"
```

```
hypothesis 6.x.x | ply OK
```

```bash
flex --version
bison --version
```

```
flex 2.6.4
bison (GNU Bison) 3.8.2
```

```bash
uv --version
```

```
uv 0.x.x
```

```bash
echo $CS374_IMAGE_VERSION
```

```
2026.09.02
```

```bash
guile --version
```

```
guile (GNU Guile) 3.0.x
```

```bash
mit-scheme --version
```

```
MIT/GNU Scheme 12.x
```

The Scheme assignment names `mit-scheme`, so it is installed here when Debian has a build for your CPU.  If this last command instead prints `mit-scheme: command not found`, you are almost certainly on an Apple Silicon Mac; nothing is broken, and `guile` is your Scheme for that assignment.  The other eight commands must all produce output, and `echo $CS374_IMAGE_VERSION` must print a date at least as recent as the one in Step 3; an older date or an empty line means your container files are stale, and Step 3 tells you how to refresh them.

If they do, your environment is done.  Exit the container with `exit` or Ctrl-D; the `--rm` flag deletes the container (not the image, and not your files; those live in the mounted repo).

---

## Step 5: Git Identity and Credentials Inside the Container

The container has `git` but knows nothing about *you*.  Inside the container, set your identity (use the email associated with your GitHub account):

```bash
git config --global user.name "Your Name"
git config --global user.email "you@example.com"
```

Because the container is recreated from the image each time, per-container `--global` config does not persist across `docker compose run` sessions.  The clean fix is to set the config **once per repository** instead, which stores it in `/workspace/.git/config`, on your disk, inside the mount:

```bash
cd /workspace
git config user.name "Your Name"
git config user.email "you@example.com"
```

(The VS Code Dev Containers route copies your host `~/.gitconfig` into the container automatically, so Option A students often find this already done.)

**If git refuses to touch `/workspace` at all.**  Sooner or later a git command in the container answers with this instead of doing anything:

```
fatal: detected dubious ownership in repository at '/workspace'
To add an exception for this directory, call:

        git config --global --add safe.directory /workspace
```

Take git's advice; run exactly that, inside the container:

```bash
git config --global --add safe.directory /workspace
```

Then rerun the command that failed and it will work.

The reason is worth understanding, because it is the mount showing through.  `/workspace` is *your host account's* directory, and git compares the repository's owner against the user running the command.  Inside the container that user is `student` (UID 1000 by default), and on a Linux host, or whenever you use the `--user "$(id -u):$(id -g)"` workaround from Step 10, those two numbers do not match.  Git assumes a repository it does not own may have been planted by someone else and stops rather than running hooks or config from it.  Marking `/workspace` **safe** says: I know where this came from, it is my own clone.

Two practical notes.  First, `--global` here means *the container's* `~/.gitconfig`, which is recreated from the image on every `docker compose run --rm`, so expect to run this once per session (the VS Code route keeps one long-lived container, so once is usually enough).  Second, if retyping it gets old, you can mark everything the container can see as safe:

```bash
git config --global --add safe.directory '*'
```

That would be a bad idea on your laptop, where it turns off the check for every repository on the machine.  In here it is a much smaller claim than it looks, and for the reason Step 8 spells out: `/workspace` is the *only* directory of yours this container can see, so "every repository visible to me" and "my own clone" are the same set.

Pushing needs credentials.  Two workable choices:

**Choice 1: HTTPS with a personal access token (PAT).  Recommended default.**

1.  On GitHub: **Settings -> Developer settings -> Personal access tokens -> Fine-grained tokens -> Generate new token.**
2.  Scope it tightly: *Only select repositories* -> `cs374-work`; Repository permissions -> **Contents: Read and write**.  Set an expiration at or beyond the end of the semester.
3.  Copy the token (it is shown once).
4.  When `git push` prompts for a password, paste the token.  To avoid retyping it every session, cache it in memory for the session:

```bash
git config credential.helper 'cache --timeout=7200'
```

The PAT approach is the tighter default because the credential is *scoped to one repository*; even if something inside the container misused it, the blast radius is your `cs374-work` repo, not your whole GitHub account.

**Choice 2: SSH keys, mounted read-only.**

If you already use SSH keys with GitHub, you can expose them to the container by adding one line to the `volumes:` list in `docker-compose.yml`:

```yaml
    volumes:
      - "..:/workspace"
      - "~/.ssh:/home/student/.ssh:ro"
```

The `:ro` suffix makes the mount **read-only**, so the container can use the keys but not alter them.  Then use the SSH remote form (`git@github.com:YOURUSERNAME/cs374-work.git`).

**Security note:** this widens the container's view of your machine.  The whole point of the container is that it sees *only* `/workspace`; mounting `~/.ssh` hands it a credential that can push to **every** repository your key can reach.  It is a reasonable convenience trade-off for keys you already manage carefully, but the per-repo PAT is the tighter default, and it is what the course recommends.

---

## Step 6: Practice, The Full Loop, End to End

Now run the complete workflow once, deliberately: create a file in the container, run it, commit it, push it, and see it on GitHub.  Every command below runs **inside the container** at the `/workspace` prompt.

**6.1.  Create `hello.py`:**

```bash
cat > hello.py <<'PYEOF'
import sys

def main():
    print(f"Hello from CS374, running on Python {sys.version_info.major}.{sys.version_info.minor}")

if __name__ == "__main__":
    main()
PYEOF
```

**6.2.  Run it:**

```bash
python3 hello.py
```

```
Hello from CS374, running on Python 3.11
```

**6.3.  Check what git sees:**

```bash
git status
```

```
On branch main
Untracked files:
  (use "git add <file>..." to include in what will be committed)
        hello.py
```

**6.4.  Stage and commit:**

```bash
git add hello.py
git commit -m "Add hello.py from inside the course container"
```

```
[main 1a2b3c4] Add hello.py from inside the course container
 1 file changed, 8 insertions(+)
 create mode 100644 hello.py
```

**6.5.  Push:**

```bash
git push
```

```
Enumerating objects: 4, done.
...
To https://github.com/YOURUSERNAME/cs374-work.git
   9f8e7d6..1a2b3c4  main -> main
```

(HTTPS users: this is where the PAT prompt appears the first time.)

**6.6.  Verify on GitHub:** open `https://github.com/YOURUSERNAME/cs374-work` in your browser. `hello.py` is there, with your commit message.  The file was created, executed, committed, and pushed entirely from inside the container, and it also exists on your host disk, because `/workspace` *is* your clone.

That double-check (on GitHub *and* on your host) is the whole architecture in one observation.

---

## Step 7: The Daily Workflow

Everything after today is this loop:

> **Daily workflow**
>
> 1.  **Start**: `docker compose run --rm cs374` (from `cs374-work/.devcontainer/`), or "Reopen in Container" in VS Code.
> 2.  **Work**: edit files in `/workspace` (or on the host side; it is the same directory).
> 3.  **Test**: `pytest` (or `make test` in the generator-toolchain directions).
> 4.  **Commit**: `git add -A && git commit -m "what changed and why"`, small commits, at every working stopping point.
> 5.  **Push**: `git push` before you close the laptop.  Unpushed work exists in exactly one place, and laptops know this.
>
> Exit the container freely.  The container is cattle; the workspace is the pet.

---

## Step 8: Why the Isolation Matters

It is worth being precise about what the container buys you, because it will shape how you debug all semester.

The container sees only `/workspace`.  When you are at the container prompt, the *entire visible universe* is the container's own system files (recreated fresh from the image every run) plus your mounted repo.  A runaway `rm -rf`, a misbehaving `make` recipe from a scaffold you are experimenting with, a generated C program with a wild pointer that scribbles over files; the worst any of them can do is damage `/workspace`.  And `/workspace` is a git repository pushed to GitHub, so even that damage is one `git checkout` (or, worst case, one fresh `git clone`) from repaired.  Your photos, your other courses' work, your OS: unreachable, by construction.

The environment is disposable and reproducible.  If you ever wonder "did I break my environment or my code?", the answer is one command away: exit, `docker compose run --rm cs374` again, and you have a factory-fresh environment running your same workspace.  If the bug survives, it is in your code.  This eliminates an entire genus of debugging misery, and it is the same reproducibility property that makes your graded work run identically on the instructor's machine.

Version pinning happens once, for everyone.  The Dockerfile records the environment *as code*, in your repository, under version control, the same discipline the course asks of your language pipeline itself.

That last property has a corollary that catches people, so it is worth saying outright: **do not install things at the container prompt.**  An `apt-get install` or a `curl ... | sh` typed inside a `docker compose run --rm` container works, right up until you exit, at which point it is gone along with the container, and you get to do it again tomorrow.  Worse, it is invisible: your environment now differs from everyone else's in a way no file records, which is exactly the failure mode containers exist to prevent.  If something you need is genuinely missing, there are two correct moves, and installing it by hand is neither.  Add the line to the Dockerfile and `docker compose build` (now it is versioned, and it survives); or, if it is a tool the whole course needs, tell me, and it goes in the image for everybody.  The reflex to build is the point of this course; the reflex to patch a running container is the habit to unlearn.

---

## Step 9: The Native Fallback (No Docker)

If your machine cannot run Docker (unsupported hardware, an administrator lock, or too little disk), install the toolchain natively.  This route is fully supported; you simply take on the version-matching responsibility the container would have handled.

**9.1: Python.**  Install Python **3.11 or later** (3.10+ is the hard course floor, for `match`/`case`): macOS `brew install python@3.12`; Windows from [python.org](https://www.python.org/downloads/) (check "Add to PATH"); Debian/Ubuntu `sudo apt install python3.12`.  Verify with `python3 --version`.

**9.2: Course Python packages with uv.**  In your cloned `cs374-work` repository, using [uv](https://docs.astral.sh/uv/) (the environment manager from the Overview assignment's Part 1.5):

```bash
cd ~/cs374-work
uv venv
uv add pytest hypothesis ply
uv run pytest --version
uv run python -c "import hypothesis, ply; print('OK')"
```

Expected: a pytest version banner and `OK`.  Remember to prefix course commands with `uv run` (or activate the venv) so they see these packages.  (`uv` is installed in the course container too, so these exact commands work in there if you switch routes later.)

**If `uv add` errors here, read the error before you panic.**  This early in the semester your clone holds no Python project: no `pyproject.toml`, no source, no tests.  So `uv add` may stop with something like ``No `pyproject.toml` found in current directory or any parent directory``, and a bare `pytest` would report `no tests ran`.  Neither is a failure of this step.  What you are checking is narrower: that the tools are **installed and on your PATH**.  The errors that would matter are `uv: command not found`, `pytest: command not found`, or `No module named pytest`, which mean the install did not take and 9.1/9.2 need another pass.  Anything that gets far enough to complain about a missing *project* has already told you the tool is there.  If you would rather watch the packages actually install, run `uv init` first to create a `pyproject.toml` and then repeat `uv add`; the first assignment sets up a real project regardless.

**9.3: flex/bison/gcc/make, only if you take those directions.**  The generator-toolchain directions and the mininote scaffold need the C toolchain; the Python-only pipeline directions do not.  Install only if applicable:

- **Debian/Ubuntu (and Windows via WSL2):** `sudo apt install flex bison gcc make`
- **macOS:** `xcode-select --install` (gcc/make), then `brew install flex bison`
- **Windows without WSL2:** strongly consider WSL2 (Ubuntu): it is the path the course instructions assume; native MSYS2 works but you are debugging alone.

Verify with `flex --version` and `bison --version` as in Step 4.

**9.4: Scheme, only if you take the Functional Programming with Scheme assignment.**  Pick one:

- **Debian/Ubuntu (and Windows via WSL2):** `sudo apt install mit-scheme`, or `sudo apt install guile-3.0`
- **macOS:** `brew install mit-scheme`
- **Windows without WSL2:** install `guile` from the Cygwin installer
- **Nothing to install:** [try.scheme.org](https://try.scheme.org) is a full Scheme REPL in a browser tab

Verify with `mit-scheme --version` or `guile --version`.  The [Scheme assignment]({{ site.baseurl }}/Assignments/Scheme) describes these routes and what its write-up asks you to report about the one you chose.

**9.5: Git.**  You already completed the git steps in the Overview assignment's Part 1.5; the Step 6 practice loop above works identically in a native terminal; do it there instead, in your `cs374-work` clone.

---

## Step 10: Troubleshooting

**`Cannot connect to the Docker daemon` / `docker: command not found` after install.**  Docker Desktop is installed but not running (start the app and wait for it to finish launching), or your terminal predates the install (open a new terminal).  On Linux: `sudo systemctl start docker`, and add yourself to the docker group (`sudo usermod -aG docker $USER`, then log out and in).  On Windows, if Docker Desktop is plainly running but Ubuntu says `docker: command not found`, the WSL integration is off: **Settings -> Resources -> WSL Integration**, switch the **Ubuntu** toggle on, **Apply & Restart**, and open a new Ubuntu terminal.  While you are there, confirm **Settings -> General -> Use the WSL 2 based engine** is checked.

Windows: the bind mount is empty or the build cannot find files.  Three classic causes.  (1) Your clone lives on a drive or network share Docker Desktop has not been granted; keep `cs374-work` under your user profile (e.g., `C:\Users\you\cs374-work`) or, better, inside your WSL2 home directory.  (2) You ran `docker compose` from the wrong directory; the `..` in the compose file is relative to `.devcontainer/`, so run it from there.  (3) You typed a `cd ~/cs374-work/...` line into Command Prompt, where `~` is not a home-folder shorthand: `cmd.exe` either errors or lands you somewhere unexpected, and the mount then points at the wrong place.  Use `cd %USERPROFILE%\cs374-work\.devcontainer` there, or run the tutorial's commands from PowerShell, Git Bash, or WSL2, where `~` works as written.  `cd` with no argument prints your current directory in `cmd.exe`, and `pwd` does the same in the others; check it before you build.

**`git push` rejected: `Authentication failed` or `Support for password authentication was removed`.**  GitHub does not accept account passwords over HTTPS; you must paste a **personal access token** at the password prompt.  If a token is rejected, check its scope: fine-grained tokens must list `cs374-work` under *Only select repositories* and have **Contents: Read and write**.  Expired tokens fail the same way; generate a new one.

Line endings: files show as modified everywhere, or a script fails with `\r: command not found`.  Windows editors write CRLF line endings; the Linux container expects LF. Fix it once per repo with a `.gitattributes` file containing `* text=auto eol=lf`, then `git add --renormalize .` and commit.  In VS Code, set the status-bar line-ending indicator to `LF` for files you create.

The build fails partway with a network error.  Usually a flaky connection during the big download layers.  Rerun `docker compose build`; completed layers are cached, so it resumes from the failed step.

**`permission denied` writing files in `/workspace` (Linux hosts).**  The container's `student` user may not match your host UID. Quick check: `id` inside the container vs. on the host.  If they differ, run the container with your UID: `docker compose run --rm --user "$(id -u):$(id -g)" cs374`.

**`fatal: detected dubious ownership in repository at '/workspace'`.**  The same UID mismatch, seen from git's side; it is the usual surprise on Linux hosts, and the `--user` fix just above brings it on.  Inside the container, run `git config --global --add safe.directory /workspace`, then rerun whatever failed.  Step 5 explains what that line claims and why it is a modest claim in here.  It is written to the container's `~/.gitconfig`, so a `--rm` container will want it again next session.

**`curl: command not found`, `uv: command not found`, or anything else from Step 4 is missing.**  Your `.devcontainer/` copy predates a course update, so you are rebuilding an older image.  Confirm it with `echo $CS374_IMAGE_VERSION` inside the container and compare against the date in Step 3: an older date, or an empty line, is the diagnosis.  The fix is to re-download the three container files over your copies, rebuild, and re-run the Step 4 checks:

```bash
cd ~/cs374-work/.devcontainer
# re-download Dockerfile, docker-compose.yml, and devcontainer.json here
docker compose build
docker compose run --rm cs374
```

Commit the refreshed files afterwards; they are part of your work.  A plain `docker compose build` is enough (the changed lines invalidate their own layers); reach for `docker compose build --no-cache` only if it somehow is not.

**You wanted to read a script before running it.**  Good instinct, and worth getting right, because the two pipes look alike and do very different things: `curl -LsSf URL | sh` hands the script straight to a shell and runs it sight unseen, while `curl -LsSf URL | less` only *reads* it, and installs nothing.  For actually inspecting one, save it first and then page it, so you run the same bytes you read:

```bash
curl -LsSf https://example.com/install.sh -o install.sh
less install.sh
sh install.sh     # only after you have read it
```

For `uv` specifically the question does not arise in here: the container already has it, and installing anything at the container prompt does not survive the container anyway (Step 8).

**`mit-scheme: command not found`.**  Expected on CPU architectures Debian does not build MIT/GNU Scheme for, Apple Silicon among them.  Nothing is wrong: the build prints a note and carries on, and `guile` is your Scheme.  Name that route (and its `guile --version` output) in the Scheme assignment's write-up.

Everything is broken and you do not know why.  Nuclear option, in increasing order: exit and rerun (`--rm` gives you a fresh container); `docker compose build --no-cache` (fresh image); fresh `git clone` into a new directory (fresh workspace; this is why you push).  One of these three fixes it, and figuring out *which* tells you where the problem was.

---

## Quick Reference

| Task | Command |
|------|---------|
| Enter the container | `docker compose run --rm cs374` (from `.devcontainer/`) |
| Rebuild the image | `docker compose build` |
| Verify toolchain | `python3 --version && pytest --version && flex --version && bison --version && uv --version && guile --version` |
| Check your image version | `echo $CS374_IMAGE_VERSION` (in the container); compare against Step 3 |
| Refresh the container files | re-download the three Step 3 files over your copies, then `docker compose build` |
| One-repo git identity | `git config user.name "..."` / `git config user.email "..."` (in `/workspace`) |
| Cache the PAT for a session | `git config credential.helper 'cache --timeout=7200'` |
| Clear git's `dubious ownership` error | `git config --global --add safe.directory /workspace` (in the container) |
| The daily loop | start -> work -> `pytest` -> `git add -A && git commit` -> `git push` |
| Fresh environment | exit, then `docker compose run --rm cs374` again |
| Native fallback | `uv venv && uv add pytest hypothesis ply` (+ OS flex/bison only if needed) |
