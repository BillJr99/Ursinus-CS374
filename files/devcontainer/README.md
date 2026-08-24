# CS374 Course Development Container

One environment that runs every CS374 assignment: Python 3.11 with `pytest`,
`hypothesis`, and `ply` for the language-pipeline assignments, plus `flex`,
`bison`, `gcc`, and `make` for the generator-toolchain directions and the
mininote scaffold. `git` and `zip` are included so you can commit, push, and
package submissions from inside the container.

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
3.  Copy the three files above into a `.devcontainer/` folder inside the clone:

   ```
   cs374-work/
     .devcontainer/
       Dockerfile
       docker-compose.yml
       devcontainer.json
   ```

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
python3 --version && pytest --version && flex --version && bison --version
```

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

3.  **Only if** you take the generator-toolchain directions (or build the
   mininote scaffold), install the OS packages for flex/bison:
   - Debian/Ubuntu: `sudo apt install flex bison gcc make`
   - macOS: `xcode-select --install` then `brew install flex bison`
   - Windows: use WSL2 (Ubuntu) and the Debian/Ubuntu line above; MSYS2
     works but WSL2 matches the course instructions exactly.

   Students who stay on the Python-only directions do not need flex/bison at all.

## Troubleshooting

- `Cannot connect to the Docker daemon`: Docker Desktop is not running; start it.
- Slow first build: normal; later builds reuse cached layers.
- Push rejected / authentication failures: see the credential section of the
  [Development Environment tutorial](https://www.billmongan.com/Ursinus-CS374-Fall2026/Tutorials/DevEnvironment).
