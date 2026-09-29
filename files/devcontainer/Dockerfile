# CS374 Course Development Container
# ----------------------------------
# One image that runs every CS374 assignment: the Python language pipeline
# (lexer -> parser -> AST -> environments -> evaluator), its test suites,
# the generator-toolchain directions (flex/bison/gcc/make, including the
# mininote scaffold), and the Scheme assignment.  `uv`, the environment
# manager the course standardizes on, is here too.
#
# Build it (from inside your work repo's .devcontainer/ folder):
#   docker compose build
# Enter it:
#   docker compose run --rm cs374
#
# The container sees ONLY the directory you mount at /workspace (your
# cloned GitHub work repo). Nothing else on your machine is visible to it.

# Start from a small official Python image. 3.11 satisfies the course
# requirement of Python 3.10+ (structural pattern matching, dataclasses).
FROM python:3.11-slim

# The date this image recipe last changed. It is stamped into the image twice:
# as a standard OCI label, and as an environment variable you can read at the
# container prompt with `echo $CS374_IMAGE_VERSION`. That second one exists for
# a specific reason: you keep your own COPY of these container files, so when
# the course updates them, your copy does not follow. Comparing this value
# against the one in the tutorial's Step 3 tells you whether your image is
# current. Bump it whenever this file changes.
ARG CS374_IMAGE_VERSION=2026.09.02

LABEL org.opencontainers.image.title="CS374 course development environment" \
      org.opencontainers.image.description="Python 3.11 with pytest/hypothesis/ply and uv, plus flex, bison, gcc, and make for the CS374 language-pipeline assignments and generator-toolchain directions, and Scheme (guile, and mit-scheme where Debian builds it) for the functional programming assignment" \
      org.opencontainers.image.authors="CS374 course staff" \
      org.opencontainers.image.version="$CS374_IMAGE_VERSION" \
      org.opencontainers.image.url="https://www.billmongan.com/Ursinus-CS374-Fall2026/"

# The same stamp, readable from inside the container without docker commands.
ENV CS374_IMAGE_VERSION=$CS374_IMAGE_VERSION

# System packages (each one earns its place):
#   flex, bison -- the scanner/parser generators used by the
#                  generator-toolchain directions and the mininote scaffold
#   gcc, libc6-dev, make -- compile and drive the C code that flex/bison emit
#   git         -- commit and push your work from inside the container
#   zip         -- package submissions
#   curl        -- fetches the uv installer below; useful on its own
#   less        -- the pager git reaches for; without it `git log`, `git diff`,
#                  and `git show` have nowhere to page, and you cannot read a
#                  long file without dumping the whole thing to the terminal
#   nano        -- an editor at the container prompt. The VS Code route brings
#                  its own; the plain `docker compose` route would otherwise
#                  have no way to fix a single line without leaving
#   guile-3.0   -- a Scheme for the Functional Programming with Scheme
#                  assignment; Debian builds it for every CPU architecture,
#                  so this one is always here
# `--no-install-recommends` and the cache cleanup keep the image small.
RUN apt-get update && apt-get install -y --no-install-recommends \
        flex \
        bison \
        gcc \
        libc6-dev \
        make \
        git \
        zip \
        curl \
        less \
        nano \
        guile-3.0 \
        ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Debian installs the binary as `guile-3.0`; make plain `guile` work too, so
# the command in the tutorial is the command that runs. Written the long way on
# purpose: the one-line version silently becomes `ln -s "" /usr/local/bin/guile`
# if a future Debian renames the binary, and fails the build with a message that
# explains nothing. Say what went wrong instead.
RUN if command -v guile >/dev/null 2>&1; then \
        echo ">>> guile is already on PATH; no symlink needed."; \
    elif GUILE_BIN="$(command -v guile-3.0)"; then \
        ln -s "$GUILE_BIN" /usr/local/bin/guile; \
    else \
        echo ">>> ERROR: no guile binary found after installing guile-3.0." >&2; \
        exit 1; \
    fi

# MIT/GNU Scheme is the implementation the Scheme assignment names for Linux
# and macOS, so install it when it exists. Debian does not build it for every
# CPU architecture (Apple Silicon may not have it), and a missing package for
# a second Scheme is no reason to fail the whole build -- so this one install
# is allowed to fail, loudly, and guile remains your Scheme there. Note that
# `apt-get update` itself is still fatal: a broken package index is a real
# problem, not an architecture difference.
RUN apt-get update \
    && (apt-get install -y --no-install-recommends mit-scheme \
        || echo ">>> mit-scheme is unavailable for this CPU architecture; use guile instead.") \
    && rm -rf /var/lib/apt/lists/*

# Python packages:
#   pytest     -- the test runner you will use in every assignment
#   hypothesis -- property-based testing (see the Property-Based Testing tutorial)
#   ply        -- optional pure-Python lex/yacc, for the PLY direction
RUN pip install --no-cache-dir pytest hypothesis ply

# uv, the Python environment manager the course standardizes on (see Part 1.5
# of the Overview assignment). UV_INSTALL_DIR puts it on a PATH every user
# shares; the default would hide it in root's home, where `student` could not
# see it. INSTALLER_NO_MODIFY_PATH keeps the installer out of shell profiles,
# and the version check makes a misplaced install fail the build here rather
# than surprise you at the prompt.
RUN curl -LsSf https://astral.sh/uv/install.sh \
        | env UV_INSTALL_DIR=/usr/local/bin INSTALLER_NO_MODIFY_PATH=1 sh \
    && uv --version

# Work as a regular (non-root) user, like you would on your own machine.
# Files you create in /workspace keep sane ownership, and a stray command
# cannot modify the container's system directories. /workspace is created and
# handed to `student` here, before the switch: a WORKDIR created afterwards
# would belong to root, and anyone who ran this image without the bind mount
# would land in a directory they cannot write to.
RUN useradd --create-home --shell /bin/bash student \
    && mkdir -p /workspace \
    && chown student:student /workspace
USER student

# All course work happens here; docker-compose.yml bind-mounts your cloned
# GitHub repo at this path.
WORKDIR /workspace

# Default to an interactive shell.
CMD ["bash"]
