# CS374 Course Development Container

One environment that runs every CS374 assignment: Python 3.11 with `pytest`,
`hypothesis`, and `ply` for the language-pipeline assignments, plus `flex`,
`bison`, `gcc`, and `make` for the generator-toolchain directions and the
mininote scaffold, `uv` for Python environments, and Scheme (`guile`, and
`mit-scheme` where Debian builds it for your CPU) for the Functional
Programming with Scheme assignment. `git` and `zip` are included so you can
commit, push, and package submissions from inside the container, and `less`,
`nano`, and `curl` so you can page, edit, and fetch without leaving it.

The full walk-through (with GitHub setup, credential options, practice steps,
and troubleshooting) is the course [Development Environment tutorial](https://www.billmongan.com/Ursinus-CS374-Fall2026/Tutorials/DevEnvironment).
This README is the quickstart version.

## Files

| File | Purpose |
|---|---|
| `Dockerfile` | Recipe for the course image (commented, line by line) |
| `docker-compose.yml` | One-command build/run with the workspace bind mount |
| `devcontainer.json` | VS Code Dev Containers configuration |

## Setup (common to routes A and B)

1.  Install [Docker Desktop](https://www.docker.com/products/docker-desktop/)
   (macOS/Windows) or Docker Engine (Linux) and confirm `docker run hello-world` works.
2.  Create a **private** GitHub repository named `cs374-work` and clone it.
   Keep the clone **under your home folder**: `~/cs374-work` on macOS, Linux,
   and WSL2; `C:\Users\YOU\cs374-work` on Windows.  Docker Desktop shares
   those locations with containers by default, so a clone on another drive or
   a network share is the usual cause of an empty bind mount.  Note that `~`
   is not a home-folder shorthand in the Windows Command Prompt: use
   `%USERPROFILE%\cs374-work` there, or run these commands from PowerShell,
   Git Bash, or WSL2, where `~` works as written.
3.  Copy the three files above into a `.devcontainer/` folder inside the clone:

   ```
   cs374-work/
     .devcontainer/
       Dockerfile
       docker-compose.yml
       devcontainer.json
   ```

These are a **copy**, and they do not update themselves. The image carries a
datestamp you can read from the container prompt with
`echo $CS374_IMAGE_VERSION`; when it is older than the one in Step 3 of the
[tutorial](https://www.billmongan.com/Ursinus-CS374-Fall2026/Tutorials/DevEnvironment),
re-download the three files over your copies, `docker compose build`, and commit.

The bind mount in `docker-compose.yml` (and the `workspaceMount` in
`devcontainer.json`) exposes **your cloned GitHub repo** (and nothing else on
your machine) at `/workspace` inside the container.  You edit, test, commit,
and push there; the files live on your disk and on GitHub, so the container
itself is disposable.

## Route A: VS Code Dev Containers

1.  Install VS Code and the **Dev Containers** extension.
2.  Open the `cs374-work` folder in VS Code.
3.  Run **Dev Containers: Reopen in Container** from the command palette.
4.  VS Code builds the image (first time takes a few minutes) and reopens your
   repo inside it, with the Python and GitLens extensions preinstalled.
5.  Open a terminal in VS Code; you are inside the container at `/workspace`.

## Route B: plain Docker Compose

From the `.devcontainer/` folder of your clone:

```bash
docker compose build            # first time, and after any Dockerfile change
docker compose run --rm cs374   # opens bash inside the container
```

Verify the toolchain from the container prompt:

```bash
python3 --version && pytest --version && flex --version && bison --version \
  && uv --version && guile --version && echo $CS374_IMAGE_VERSION
```

`mit-scheme --version` should work too, except on CPU architectures Debian does
not build it for (Apple Silicon among them), where `guile` is your Scheme.

Exit with `exit` or Ctrl-D. `--rm` discards the container; your work is safe
in the mounted repo.

## Route C: native fallback (no Docker)

If you cannot run Docker, install the tools directly:

1.  Install Python 3.11 or later (any 3.10+ works for the pipeline assignments).
2.  In your cloned `cs374-work` repo, use [uv](https://docs.astral.sh/uv/) to
   create the environment and add the course packages:

   ```bash
   uv venv
   uv add pytest hypothesis ply
   uv run pytest --version
   ```

   With no `pyproject.toml` in the repo yet, `uv add` may stop on the missing
   project (`uv init` first if you want it to complete), and a bare `pytest`
   will report `no tests ran`. Either is fine here; you are only confirming the
   tools are installed. `uv: command not found` or `pytest: command not found`
   is the result that means the install did not take.

3.  **Only if** you take the generator-toolchain directions (or build the
   mininote scaffold), install the OS packages for flex/bison:
   - Debian/Ubuntu: `sudo apt install flex bison gcc make`
   - macOS: `xcode-select --install` then `brew install flex bison`
   - Windows: use WSL2 (Ubuntu) and the Debian/Ubuntu line above; MSYS2
     works but WSL2 matches the course instructions exactly.

   Students who stay on the Python-only directions do not need flex/bison at all.

4.  **Only if** you take the Functional Programming with Scheme assignment,
   install a Scheme: Debian/Ubuntu `sudo apt install mit-scheme` (or
   `guile-3.0`), macOS `brew install mit-scheme`, Windows `guile` from the
   Cygwin installer. [try.scheme.org](https://try.scheme.org) needs no install
   at all. Container users already have this.

## Troubleshooting

- `Cannot connect to the Docker daemon`: Docker Desktop is not running; start it.
- Slow first build: normal; later builds reuse cached layers.
- `curl: command not found`, `uv: command not found`, or any other tool above
  missing: your `.devcontainer/` copy predates a course update. Check with
  `echo $CS374_IMAGE_VERSION`, then re-download the three files, rebuild, and
  commit. Do not install tools at the container prompt; a `--rm` container
  discards them on exit. See Step 3 and Step 8 of the tutorial.
- `fatal: detected dubious ownership in repository at '/workspace'`: the mount is
  owned by your host account, not by the container's `student` user. Run
  `git config --global --add safe.directory /workspace` inside the container and
  retry. It lives in the container's `~/.gitconfig`, so a `--rm` container needs
  it again next session.
- Push rejected / authentication failures: see the credential section of the
  [Development Environment tutorial](https://www.billmongan.com/Ursinus-CS374-Fall2026/Tutorials/DevEnvironment).
