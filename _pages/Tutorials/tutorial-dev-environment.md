---
layout: tutorial
permalink: /Tutorials/DevEnvironment
title: "CS374: The Course Development Environment"

info:
  coursenum: CS374
  goals:
    - To build and enter the course Docker container, a single environment that runs every CS374 assignment
    - To bind-mount a GitHub-backed workspace so that all work is versioned and pushable from inside the container
    - To configure git identity and credentials (personal access token or SSH) for use inside a container
    - To practice the full daily loop - start container, work, test, commit, push - end to end
    - To explain why container isolation protects the rest of your machine, and set up the native fallback if Docker is not an option

readings:
  - rtitle: "Docker Get Started Guide"
    rlink: "https://docs.docker.com/get-started/"
  - rtitle: "GitHub: Managing your personal access tokens"
    rlink: "https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens"
  - rtitle: "Shell Skills for Language Development (Tutorial)"
    rlink: "https://www.billmongan.com/Ursinus-CS374-Fall2026/Tutorials/ShellForLanguageDev"

tags:
  - tools
  - docker
  - git
  - setup
---

# The Course Development Environment

This tutorial sets up **one environment that runs every CS374 assignment**: a Docker container with the whole course toolchain preinstalled — Python 3.11 with `pytest`, `hypothesis`, and `ply` for the language-pipeline assignments, plus `flex`, `bison`, `gcc`, and `make` for the generator-toolchain directions and the mininote scaffold. The container is bind-mounted onto a directory on your machine that is itself a **git repository with a GitHub remote**, so everything you write inside the container is versioned and pushed like normal work.

Two ideas do all the heavy lifting here, and they are worth stating up front:

1. **The image is the environment.** Instead of installing five tools and hoping the versions match the grader's, you build one image from the course Dockerfile. Everyone's container is byte-for-byte the same environment.
2. **The mount is the only door.** The container can see exactly one directory of your machine: the workspace you mount into it. Your documents, your other courses, your browser profile — invisible. Meanwhile, everything you create in that workspace lives on *your* disk and on GitHub, so the container itself is disposable.

Work through the numbered steps in order. Each practice step shows the command *and the output you should expect*; if yours differs, stop and consult the troubleshooting section at the end. Budget about an hour, most of it waiting for downloads.

If Docker cannot run on your machine at all, skip to **Step 9: The Native Fallback** — it is a complete route, not a consolation prize.

---

## Step 1: Install Docker Desktop

Download and install [Docker Desktop](https://www.docker.com/products/docker-desktop/) for macOS or Windows, or [Docker Engine](https://docs.docker.com/engine/install/) on Linux. Accept the defaults.

**Disk note:** Docker Desktop plus the course image needs roughly **3–5 GB** of free disk. If your laptop is tight on space, clear room first — a half-downloaded image is the most confusing failure mode in this tutorial.

Start Docker Desktop (on Linux, ensure the daemon is running and your user is in the `docker` group), then verify from a terminal:

```bash
docker run hello-world
```

Expected output (abridged):

```
Hello from Docker!
This message shows that your installation appears to be working correctly.
```

If you instead see `Cannot connect to the Docker daemon`, Docker Desktop is installed but not *running* — launch the application and wait for the whale icon to settle.

---

## Step 2: Create Your Workspace Repository on GitHub

Your course work lives in a private GitHub repository named `cs374-work`. This is the directory you will mount into the container, and the remote you will push to all semester.

1. On [github.com](https://github.com/), click **New repository**.
2. Name: `cs374-work`. Visibility: **Private**. Check **Add a README file** (so the repository is cloneable immediately).
3. Clone it to your machine:

```bash
cd ~
git clone https://github.com/YOURUSERNAME/cs374-work.git
cd cs374-work
ls -la
```

Expected output (abridged):

```
Cloning into 'cs374-work'...
...
.git
README.md
```

The `.git` directory means this folder is a git repository; the clone already knows its GitHub remote. Confirm:

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

- [Dockerfile]({{ site.baseurl }}/files/devcontainer/Dockerfile) — the recipe for the course image, commented line by line
- [docker-compose.yml]({{ site.baseurl }}/files/devcontainer/docker-compose.yml) — one-command build/run with the workspace mount
- [devcontainer.json]({{ site.baseurl }}/files/devcontainer/devcontainer.json) — VS Code Dev Containers configuration
- (optional) [README.md]({{ site.baseurl }}/files/devcontainer/README.md) — the quickstart version of this tutorial

Your repository should now look like this:

```
cs374-work/
  .devcontainer/
    Dockerfile
    docker-compose.yml
    devcontainer.json
  README.md
```

Open the Dockerfile in an editor and *read it* — it is short and every line is commented. You built Dockerfiles' conceptual vocabulary in your intro courses' shell work; this one is deliberately simple: a base Python image, an `apt-get` layer for the C toolchain, a `pip` layer for the Python packages, a non-root `student` user, and `/workspace` as the working directory.

Commit the container files — they are part of your work:

```bash
git add .devcontainer
git commit -m "Add course dev container configuration"
```

---

## Step 4: Build and Enter the Container

You have two equivalent front doors. Pick one; you can switch anytime because both use the same Dockerfile.

**Option A — VS Code Dev Containers (recommended if you use VS Code).** Install the **Dev Containers** extension, open the `cs374-work` folder, and run **Dev Containers: Reopen in Container** from the command palette. VS Code builds the image and reopens your repo inside it, with the Python and GitLens extensions preinstalled. Any terminal you open in VS Code is now *inside* the container.

**Option B — plain Docker Compose (any editor).** From the `.devcontainer/` folder:

```bash
cd ~/cs374-work/.devcontainer
docker compose build
docker compose run --rm cs374
```

The first build takes a few minutes (downloading the base image and packages); rebuilds are nearly instant thanks to layer caching. When it finishes you land at a prompt like:

```
student@a1b2c3d4e5f6:/workspace$
```

That hostname-looking string is the container ID. You are the non-root user `student`, in `/workspace` — which *is* your `cs374-work` repository. Prove it:

```bash
ls -la
```

```
.devcontainer
.git
README.md
```

**Verify the toolchain.** Run each of these and capture the output — this transcript is part of the Overview assignment:

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

If all five report versions, your environment is done. Exit the container with `exit` or Ctrl-D; the `--rm` flag deletes the container (not the image, and not your files — those live in the mounted repo).

---

## Step 5: Git Identity and Credentials Inside the Container

The container has `git` but knows nothing about *you*. Inside the container, set your identity (use the email associated with your GitHub account):

```bash
git config --global user.name "Your Name"
git config --global user.email "you@example.com"
```

Because the container is recreated from the image each time, per-container `--global` config does not persist across `docker compose run` sessions. The clean fix is to set the config **once per repository** instead, which stores it in `/workspace/.git/config` — on your disk, inside the mount:

```bash
cd /workspace
git config user.name "Your Name"
git config user.email "you@example.com"
```

(The VS Code Dev Containers route copies your host `~/.gitconfig` into the container automatically, so Option A students often find this already done.)

**Pushing needs credentials.** Two workable choices:

**Choice 1 — HTTPS with a personal access token (PAT). Recommended default.**

1. On GitHub: **Settings → Developer settings → Personal access tokens → Fine-grained tokens → Generate new token.**
2. Scope it tightly: *Only select repositories* → `cs374-work`; Repository permissions → **Contents: Read and write**. Set an expiration at or beyond the end of the semester.
3. Copy the token (it is shown once).
4. When `git push` prompts for a password, paste the token. To avoid retyping it every session, cache it in memory for the session:

```bash
git config credential.helper 'cache --timeout=7200'
```

The PAT approach is the tighter default because the credential is *scoped to one repository* — even if something inside the container misused it, the blast radius is your `cs374-work` repo, not your whole GitHub account.

**Choice 2 — SSH keys, mounted read-only.**

If you already use SSH keys with GitHub, you can expose them to the container by adding one line to the `volumes:` list in `docker-compose.yml`:

```yaml
    volumes:
      - "..:/workspace"
      - "~/.ssh:/home/student/.ssh:ro"
```

The `:ro` suffix makes the mount **read-only**, so the container can use the keys but not alter them. Then use the SSH remote form (`git@github.com:YOURUSERNAME/cs374-work.git`).

**Security note:** this widens the container's view of your machine. The whole point of the container is that it sees *only* `/workspace`; mounting `~/.ssh` hands it a credential that can push to **every** repository your key can reach. It is a reasonable convenience trade-off for keys you already manage carefully — but the per-repo PAT is the tighter default, and it is what the course recommends.

---

## Step 6: Practice — The Full Loop, End to End

Now run the complete workflow once, deliberately: create a file in the container, run it, commit it, push it, and see it on GitHub. Every command below runs **inside the container** at the `/workspace` prompt.

**6.1 — Create `hello.py`:**

```bash
cat > hello.py <<'PYEOF'
import sys

def main():
    print(f"Hello from CS374, running on Python {sys.version_info.major}.{sys.version_info.minor}")

if __name__ == "__main__":
    main()
PYEOF
```

**6.2 — Run it:**

```bash
python3 hello.py
```

```
Hello from CS374, running on Python 3.11
```

**6.3 — Check what git sees:**

```bash
git status
```

```
On branch main
Untracked files:
  (use "git add <file>..." to include in what will be committed)
        hello.py
```

**6.4 — Stage and commit:**

```bash
git add hello.py
git commit -m "Add hello.py from inside the course container"
```

```
[main 1a2b3c4] Add hello.py from inside the course container
 1 file changed, 8 insertions(+)
 create mode 100644 hello.py
```

**6.5 — Push:**

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

**6.6 — Verify on GitHub:** open `https://github.com/YOURUSERNAME/cs374-work` in your browser. `hello.py` is there, with your commit message. The file was created, executed, committed, and pushed entirely from inside the container — and it also exists on your host disk, because `/workspace` *is* your clone.

That double-check — on GitHub *and* on your host — is the whole architecture in one observation.

---

## Step 7: The Daily Workflow

Everything after today is this loop:

> **Daily workflow**
>
> 1. **Start** — `docker compose run --rm cs374` (from `cs374-work/.devcontainer/`), or "Reopen in Container" in VS Code.
> 2. **Work** — edit files in `/workspace` (or on the host side; it is the same directory).
> 3. **Test** — `pytest` (or `make test` in the generator-toolchain directions).
> 4. **Commit** — `git add -A && git commit -m "what changed and why"` — small commits, at every working stopping point.
> 5. **Push** — `git push` before you close the laptop. Unpushed work exists in exactly one place, and laptops know this.
>
> Exit the container freely. The container is cattle; the workspace is the pet.

---

## Step 8: Why the Isolation Matters

It is worth being precise about what the container buys you, because it will shape how you debug all semester.

**The container sees only `/workspace`.** When you are at the container prompt, the *entire visible universe* is the container's own system files (recreated fresh from the image every run) plus your mounted repo. A runaway `rm -rf`, a misbehaving `make` recipe from a scaffold you are experimenting with, a generated C program with a wild pointer that scribbles over files — the worst any of them can do is damage `/workspace`. And `/workspace` is a git repository pushed to GitHub, so even that damage is one `git checkout` (or, worst case, one fresh `git clone`) from repaired. Your photos, your other courses' work, your OS: unreachable, by construction.

**The environment is disposable and reproducible.** If you ever wonder "did I break my environment or my code?", the answer is one command away: exit, `docker compose run --rm cs374` again, and you have a factory-fresh environment running your same workspace. If the bug survives, it is in your code. This eliminates an entire genus of debugging misery, and it is the same reproducibility property that makes your graded work run identically on the instructor's machine.

**Version pinning happens once, for everyone.** The Dockerfile records the environment *as code*, in your repository, under version control — the same discipline the course asks of your language pipeline itself.

---

## Step 9: The Native Fallback (No Docker)

If your machine cannot run Docker (unsupported hardware, an administrator lock, or too little disk), install the toolchain natively. This route is fully supported; you simply take on the version-matching responsibility the container would have handled.

**9.1 — Python.** Install Python **3.11 or later** (3.10+ is the hard course floor, for `match`/`case`): macOS `brew install python@3.12`; Windows from [python.org](https://www.python.org/downloads/) (check "Add to PATH"); Debian/Ubuntu `sudo apt install python3.12`. Verify with `python3 --version`.

**9.2 — Course Python packages with uv.** In your cloned `cs374-work` repository, using [uv](https://docs.astral.sh/uv/) (the environment manager from the Overview assignment's Part 1.5):

```bash
cd ~/cs374-work
uv venv
uv add pytest hypothesis ply
uv run pytest --version
uv run python -c "import hypothesis, ply; print('OK')"
```

Expected: a pytest version banner and `OK`. Remember to prefix course commands with `uv run` (or activate the venv) so they see these packages.

**9.3 — flex/bison/gcc/make, only if you take those directions.** The generator-toolchain directions and the mininote scaffold need the C toolchain; the Python-only pipeline directions do not. Install only if applicable:

- **Debian/Ubuntu (and Windows via WSL2):** `sudo apt install flex bison gcc make`
- **macOS:** `xcode-select --install` (gcc/make), then `brew install flex bison`
- **Windows without WSL2:** strongly consider WSL2 (Ubuntu) — it is the path the course instructions assume; native MSYS2 works but you are debugging alone.

Verify with `flex --version` and `bison --version` as in Step 4.

**9.4 — Git.** You already completed the git steps in the Overview assignment's Part 1.5; the Step 6 practice loop above works identically in a native terminal — do it there instead, in your `cs374-work` clone.

---

## Step 10: Troubleshooting

**`Cannot connect to the Docker daemon` / `docker: command not found` after install.** Docker Desktop is installed but not running (start the app and wait for it to finish launching), or your terminal predates the install (open a new terminal). On Linux: `sudo systemctl start docker`, and add yourself to the docker group (`sudo usermod -aG docker $USER`, then log out and in).

**Windows: the bind mount is empty or the build cannot find files.** Two classic causes. (1) Your clone lives on a drive or network share Docker Desktop has not been granted — keep `cs374-work` under your user profile (e.g., `C:\Users\you\cs374-work`) or, better, inside your WSL2 home directory. (2) You ran `docker compose` from the wrong directory — the `..` in the compose file is relative to `.devcontainer/`, so run it from there.

**`git push` rejected: `Authentication failed` or `Support for password authentication was removed`.** GitHub does not accept account passwords over HTTPS — you must paste a **personal access token** at the password prompt. If a token is rejected, check its scope: fine-grained tokens must list `cs374-work` under *Only select repositories* and have **Contents: Read and write**. Expired tokens fail the same way; generate a new one.

**Line endings: files show as modified everywhere, or a script fails with `\r: command not found`.** Windows editors write CRLF line endings; the Linux container expects LF. Fix it once per repo with a `.gitattributes` file containing `* text=auto eol=lf`, then `git add --renormalize .` and commit. In VS Code, set the status-bar line-ending indicator to `LF` for files you create.

**The build fails partway with a network error.** Usually a flaky connection during the big download layers. Rerun `docker compose build` — completed layers are cached, so it resumes from the failed step.

**`permission denied` writing files in `/workspace` (Linux hosts).** The container's `student` user may not match your host UID. Quick check: `id` inside the container vs. on the host. If they differ, run the container with your UID: `docker compose run --rm --user "$(id -u):$(id -g)" cs374`.

**Everything is broken and you do not know why.** Nuclear option, in increasing order: exit and rerun (`--rm` gives you a fresh container); `docker compose build --no-cache` (fresh image); fresh `git clone` into a new directory (fresh workspace — this is why you push). One of these three fixes it, and figuring out *which* tells you where the problem was.

---

## Quick Reference

| Task | Command |
|------|---------|
| Enter the container | `docker compose run --rm cs374` (from `.devcontainer/`) |
| Rebuild the image | `docker compose build` |
| Verify toolchain | `python3 --version && pytest --version && flex --version && bison --version` |
| One-repo git identity | `git config user.name "..."` / `git config user.email "..."` (in `/workspace`) |
| Cache the PAT for a session | `git config credential.helper 'cache --timeout=7200'` |
| The daily loop | start → work → `pytest` → `git add -A && git commit` → `git push` |
| Fresh environment | exit, then `docker compose run --rm cs374` again |
| Native fallback | `uv venv && uv add pytest hypothesis ply` (+ OS flex/bison only if needed) |
