# CS374 Course Development Container
# ----------------------------------
# One image that runs every CS374 assignment: the Python language pipeline
# (lexer -> parser -> AST -> environments -> evaluator), its test suites,
# and the generator-toolchain directions (flex/bison/gcc/make, including
# the mininote scaffold).
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

LABEL org.opencontainers.image.title="CS374 course development environment" \
      org.opencontainers.image.description="Python 3.11 with pytest/hypothesis/ply plus flex, bison, gcc, and make for the CS374 language-pipeline assignments and generator-toolchain directions" \
      org.opencontainers.image.authors="CS374 course staff" \
      org.opencontainers.image.url="https://www.billmongan.com/Ursinus-CS374-Fall2026/"

# System packages (each one earns its place):
#   flex, bison -- the scanner/parser generators used by the
#                  generator-toolchain directions and the mininote scaffold
#   gcc, libc6-dev, make -- compile and drive the C code that flex/bison emit
#   git         -- commit and push your work from inside the container
#   zip         -- package submissions
# `--no-install-recommends` and the cache cleanup keep the image small.
RUN apt-get update && apt-get install -y --no-install-recommends \
        flex \
        bison \
        gcc \
        libc6-dev \
        make \
        git \
        zip \
        ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Python packages:
#   pytest     -- the test runner you will use in every assignment
#   hypothesis -- property-based testing (see the Property-Based Testing tutorial)
#   ply        -- optional pure-Python lex/yacc, for the PLY direction
RUN pip install --no-cache-dir pytest hypothesis ply

# Work as a regular (non-root) user, like you would on your own machine.
# Files you create in /workspace keep sane ownership, and a stray command
# cannot modify the container's system directories.
RUN useradd --create-home --shell /bin/bash student
USER student

# All course work happens here; docker-compose.yml bind-mounts your cloned
# GitHub repo at this path.
WORKDIR /workspace

# Default to an interactive shell.
CMD ["bash"]
