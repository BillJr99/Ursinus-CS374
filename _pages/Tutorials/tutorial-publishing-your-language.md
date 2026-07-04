---
layout: tutorial
permalink: /Tutorials/PublishingYourLanguage
title: "CS374: Publishing Your Language — pip, npm, and Docker"

info:
  coursenum: CS374
  goals:
    - To package a Python interpreter for installation via pip
    - To publish an npm package that exposes your transpiler's output
    - To build and push a Docker image of your language runtime to ghcr.io
    - To version your language implementation following semantic versioning
    - To write a usable CLI entry point so others can run your language with a single command

readings:
  - rtitle: "Python Packaging User Guide"
    rlink: "https://packaging.python.org/en/latest/"
  - rtitle: "npm Documentation — Creating a Package"
    rlink: "https://docs.npmjs.com/creating-a-nodejs-package"
  - rtitle: "GitHub Container Registry Documentation"
    rlink: "https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry"

tags:
  - packaging
  - publishing
  - docker
  - final-project
---

## Introduction

By the end of CS374 you have built a real programming language: a lexer, a parser, an evaluator or compiler, and probably a REPL. That implementation lives in a folder on your laptop. This tutorial shows you how to share it with the world so that anyone — without cloning your repository or installing your dependencies by hand — can run programs written in your language.

There are three scenarios, and you only need the one that fits your project:

- **pip** — Your interpreter is written in Python. After publishing, anyone who runs `pip install mylang-cs374` will get the `mylang` command on their PATH and can run `mylang program.ml` directly.
- **npm** — Your transpiler emits JavaScript. After publishing, anyone who runs `npx @yourname/mylang program.ml` will transpile and run the source file using Node.js — no installation required.
- **Docker / ghcr.io** — Your language has native dependencies that are difficult to install (Flex/Bison, LLVM, a custom C runtime). A Docker image bundles everything. After publishing, users run `docker run --rm -v $(pwd):/work ghcr.io/yourname/mylang program.ml` and it just works.

Pick the section that matches your project. The three parts are completely independent.

---

## Semantic Versioning Quick Reference

Before diving into the tooling, agree on version numbers. All three ecosystems (PyPI, npm, Docker) use the same **semantic versioning** convention: `MAJOR.MINOR.PATCH`.

| Change | Version bump | Example |
|---|---|---|
| New feature, backward compatible | Minor | 0.1.0 → 0.2.0 |
| Bug fix | Patch | 0.1.0 → 0.1.1 |
| Breaking change | Major | 0.1.0 → 1.0.0 |

Start at `0.1.0`. You are allowed to break things in the `0.x` range. When you feel the language is stable, bump to `1.0.0`.

---

## Part A: Publishing to PyPI with pip

Use this section if your interpreter is written in Python.

### A1: Project Layout

Before you can publish, your project needs a standard layout. The key file is `pyproject.toml`, which replaces the older `setup.py`. The special `__main__.py` module makes `python3 -m mylang` work as an alternative to the `mylang` command.

```
mylang/
  __init__.py
  lexer.py
  parser.py
  evaluator.py
  __main__.py      # enables: python3 -m mylang program.ml
pyproject.toml
README.md
tests/
  test_arithmetic.py
  test_closures.py
```

`__init__.py` can be empty — it just tells Python that `mylang/` is a package. Your existing source files (`lexer.py`, `parser.py`, `evaluator.py`) stay exactly where they are.

### A2: pyproject.toml

`pyproject.toml` is the single file that describes your package to PyPI, to `pip`, and to the build tool. Create it in the root of your project (next to the `mylang/` directory, not inside it):

```toml
[build-system]
requires = ["setuptools>=68", "wheel"]
build-backend = "setuptools.backends.legacy:build"

[project]
name = "mylang-cs374"
version = "0.1.0"
description = "A small programming language built in CS374"
readme = "README.md"
requires-python = ">=3.10"
license = {text = "MIT"}

[project.scripts]
mylang = "mylang.__main__:main"
```

Key points:

- **`name`** must be unique on PyPI. Append your username or course section if `mylang-cs374` is taken: `mylang-cs374-yourname`.
- **`version`** must be bumped every time you upload. PyPI rejects a new upload with an existing version number.
- **`[project.scripts]`** is what creates the `mylang` command on the user's PATH. The value `"mylang.__main__:main"` means "import `mylang/__main__.py` and call the `main()` function."
- **`requires-python`** tells pip to refuse installation on older Pythons. Use `>=3.10` to match what you developed with.

### A3: \_\_main\_\_.py

This file is the CLI entry point. It reads a source file from the command line, passes its contents to your evaluator, and handles errors gracefully.

```python
import sys
from .evaluator import run, LangError

def main():
    if len(sys.argv) != 2:
        print("Usage: mylang <program.ml>", file=sys.stderr)
        sys.exit(1)
    try:
        with open(sys.argv[1]) as f:
            source = f.read()
        result = run(source)
        if result is not None:
            print(result)
    except FileNotFoundError:
        print(f"Error: file not found: {sys.argv[1]}", file=sys.stderr)
        sys.exit(1)
    except LangError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
```

The relative import (`.evaluator`) works because `mylang` is a proper package. `LangError` should be the base exception class your evaluator raises for runtime and parse errors; define it in `evaluator.py` if you have not already.

### A4: Build and Upload

Install the build and upload tools once:

```bash
pip install build twine
```

Then build your package. This creates two distribution files in `dist/`:

```bash
python3 -m build
# dist/mylang_cs374-0.1.0.tar.gz      (source distribution)
# dist/mylang_cs374-0.1.0-py3-none-any.whl  (wheel)
```

Validate the distributions before uploading — this catches missing files and metadata errors:

```bash
twine check dist/*
```

**Testing on Test PyPI first (recommended)**

Test PyPI is a sandbox that behaves exactly like the real PyPI. Create a free account at [test.pypi.org](https://test.pypi.org) and upload there first:

```bash
twine upload --repository testpypi dist/*
```

Then install from Test PyPI to verify everything works:

```bash
pip install --index-url https://test.pypi.org/simple/ mylang-cs374
mylang tests/hello.ml
```

**Uploading to the real PyPI**

Create an account at [pypi.org](https://pypi.org), then:

```bash
twine upload dist/*
```

After upload, anyone can install your language with:

```bash
pip install mylang-cs374
mylang program.ml
```

### A5: Updating Your Package

When you fix a bug or add a feature, bump `version` in `pyproject.toml`, rebuild, and upload:

```bash
# Edit pyproject.toml: version = "0.1.1"
python3 -m build
twine check dist/*
twine upload dist/*
```

Users get the update by running `pip install --upgrade mylang-cs374`.

---

## Part B: Publishing to npm

Use this section if your transpiler emits JavaScript. Your users will run programs with `npx @yourname/mylang program.ml` — no install step needed for one-off use.

### B1: When to Use npm

The npm ecosystem is the right fit when:

- Your transpiler is written in JavaScript or TypeScript (running under Node.js).
- Your transpiler is written in another language but produces JavaScript output that users want to run directly.
- You want users to be able to run `npx @yourname/mylang program.ml` without any installation.

If your interpreter is written in Python and produces Python-like semantics, use Part A instead.

### B2: package.json

`package.json` is the npm equivalent of `pyproject.toml`. Create it in the root of your project:

```json
{
  "name": "@yourname/mylang",
  "version": "0.1.0",
  "description": "Transpiler for the MyLang language (CS374)",
  "bin": {
    "mylang": "./bin/mylang.js"
  },
  "main": "src/index.js",
  "scripts": {
    "test": "node tests/run_tests.js"
  },
  "keywords": ["language", "transpiler", "cs374"],
  "license": "MIT"
}
```

Key points:

- **`name`** uses a **scope** (`@yourname/`) to avoid name conflicts with existing packages. Replace `yourname` with your npm username.
- **`bin`** declares the CLI command. When a user installs your package globally, npm puts `mylang` on their PATH pointing at `bin/mylang.js`.
- **`main`** is the entry point when another JavaScript file requires your package as a library: `const { transpile } = require('@yourname/mylang')`.

### B3: bin/mylang.js

Create the directory `bin/` and add `mylang.js`. The shebang line (`#!/usr/bin/env node`) tells the OS to run this file with Node.js:

```javascript
#!/usr/bin/env node
'use strict';

const fs = require('fs');
const path = require('path');
const { transpile } = require('../src/index.js');

const file = process.argv[2];

if (!file) {
  console.error('Usage: mylang <program.ml>');
  process.exit(1);
}

const fullPath = path.resolve(file);

if (!fs.existsSync(fullPath)) {
  console.error(`Error: file not found: ${file}`);
  process.exit(1);
}

const source = fs.readFileSync(fullPath, 'utf8');

try {
  const output = transpile(source);
  console.log(output);
} catch (e) {
  console.error(`Error: ${e.message}`);
  process.exit(1);
}
```

Make the file executable so npm can run it:

```bash
chmod +x bin/mylang.js
```

Your `src/index.js` should export a `transpile` function:

```javascript
// src/index.js
function transpile(source) {
  // your lexer → parser → code generator pipeline
  // returns a string of JavaScript (or other target)
}

module.exports = { transpile };
```

### B4: Publishing

Create a free account at [npmjs.com](https://www.npmjs.com), then log in from your terminal:

```bash
npm login
```

**Testing locally before publishing**

Pack the package into a tarball without uploading it. This lets you inspect exactly what will be published and install it locally for testing:

```bash
npm pack
# creates yourname-mylang-0.1.0.tgz

npm install -g ./yourname-mylang-0.1.0.tgz
mylang tests/hello.ml
```

**Publishing to npm**

Scoped packages (`@yourname/...`) must be published with `--access public` unless you are on a paid npm plan:

```bash
npm publish --access public
```

After publishing, anyone can run your transpiler with:

```bash
npx @yourname/mylang program.ml
```

### B5: Updating Your Package

Bump the version in `package.json` and republish:

```bash
# Edit package.json: "version": "0.1.1"
npm publish --access public
```

npm rejects uploads of a version that already exists, so always bump before uploading.

---

## Part C: Docker and GitHub Container Registry (ghcr.io)

Use this section if your language has native dependencies — Flex/Bison, LLVM, a custom C library, or any system package that is painful to install by hand.

### C1: When to Use Docker

Docker is the right choice when:

- Your language runtime requires system packages (`apt-get install flex bison llvm`).
- You want users to run your language on any operating system without installing anything except Docker.
- Your language runtime is compiled (C, C++, Rust) rather than interpreted by Python or Node.

Docker bundles your runtime, system libraries, and everything else into a single image. A user with Docker installed can run your language with one command, regardless of their OS.

### C2: Dockerfile

Create a file named `Dockerfile` in the root of your project. This example starts from a minimal Python image; adapt the base image (`FROM` line) and the system package install step for your project:

```dockerfile
FROM python:3.12-slim

# Set the working directory inside the container
WORKDIR /app

# Install system dependencies if your language needs them.
# Uncomment and modify as needed:
# RUN apt-get update && apt-get install -y --no-install-recommends \
#     flex bison llvm-14 \
#  && rm -rf /var/lib/apt/lists/*

# Copy only the files needed for installation first.
# Copying pyproject.toml before source code lets Docker cache
# the pip install layer and skip it on rebuilds when only source changes.
COPY pyproject.toml README.md ./
COPY mylang/ ./mylang/

# Install the package in the image
RUN pip install --no-cache-dir .

# The ENTRYPOINT is what runs when someone does:
#   docker run --rm mylang:latest program.ml
# The user passes the file path as the argument after the image name.
ENTRYPOINT ["mylang"]
```

If your language is compiled (C/C++ binary), replace the Python-based install with whatever build steps produce your binary, then copy the binary and set `ENTRYPOINT` to it.

### C3: Build and Test Locally

Build the image with a tag:

```bash
docker build -t mylang:latest .
```

Test it by mounting your local `tests/` directory into the container and running a program:

```bash
docker run --rm -v $(pwd)/tests:/tests mylang:latest /tests/fibonacci.ml
```

The `-v $(pwd)/tests:/tests` flag mounts your host's `tests/` directory at `/tests` inside the container. Your `ENTRYPOINT ["mylang"]` receives `/tests/fibonacci.ml` as its argument.

Run your full test suite to verify the image works the same as your local install:

```bash
for f in tests/*.ml; do
  echo "=== $f ==="
  docker run --rm -v "$(pwd)/tests:/tests" mylang:latest "/tests/$(basename $f)"
done
```

### C4: Push to GitHub Container Registry (ghcr.io)

GitHub Container Registry (ghcr.io) is free for public images and integrates directly with your GitHub account — no separate Docker Hub account needed.

**Step 1: Create a Personal Access Token (PAT)**

Go to [github.com/settings/tokens](https://github.com/settings/tokens) and create a new token (classic) with the `write:packages` scope. Copy the token value; you will only see it once.

**Step 2: Log in to ghcr.io**

```bash
echo $GITHUB_TOKEN | docker login ghcr.io -u YOUR_GITHUB_USERNAME --password-stdin
```

Replace `YOUR_GITHUB_USERNAME` with your GitHub username and `$GITHUB_TOKEN` with your PAT (set it as an environment variable or paste it directly).

**Step 3: Tag and push the image**

Tag your image with the registry path, then push both a version tag and `latest`:

```bash
# Tag the image
docker tag mylang:latest ghcr.io/YOUR_GITHUB_USERNAME/mylang:latest
docker tag mylang:latest ghcr.io/YOUR_GITHUB_USERNAME/mylang:0.1.0

# Push both tags
docker push ghcr.io/YOUR_GITHUB_USERNAME/mylang:latest
docker push ghcr.io/YOUR_GITHUB_USERNAME/mylang:0.1.0
```

**Step 4: Make the image public**

By default, new packages on ghcr.io are private. Go to your GitHub profile → Packages → select your image → Package settings → Change visibility → Public.

After making it public, anyone can pull and run your language with:

```bash
docker run --rm -v $(pwd):/work ghcr.io/YOUR_GITHUB_USERNAME/mylang:latest /work/program.ml
```

### C5: Automate with GitHub Actions

Manually building and pushing the image every time you tag a release is tedious. GitHub Actions can do it automatically whenever you push a version tag.

Create the file `.github/workflows/docker-publish.yml` in your repository:

```yaml
name: Publish Docker Image

on:
  push:
    tags:
      - 'v*'   # triggers on: git tag v0.1.0 && git push --tags

jobs:
  push:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write

    steps:
      - name: Check out repository
        uses: actions/checkout@v4

      - name: Log in to ghcr.io
        uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Extract version tag
        id: meta
        run: echo "tag=${GITHUB_REF_NAME}" >> "$GITHUB_OUTPUT"

      - name: Build and push Docker image
        uses: docker/build-push-action@v5
        with:
          context: .
          push: true
          tags: |
            ghcr.io/${{ github.repository }}:latest
            ghcr.io/${{ github.repository }}:${{ steps.meta.outputs.tag }}
```

To publish a new release, bump your version in `pyproject.toml`, commit, tag, and push:

```bash
git add pyproject.toml
git commit -m "Bump version to 0.2.0"
git tag v0.2.0
git push origin main --tags
```

GitHub Actions will detect the `v0.2.0` tag, build the Docker image, and push `ghcr.io/yourname/mylang:v0.2.0` and `ghcr.io/yourname/mylang:latest` automatically. No manual `docker build` or `docker push` needed.

The `${{ secrets.GITHUB_TOKEN }}` is automatically available in every Actions workflow — you do not need to create it manually. It has `write:packages` permission because the workflow declares `packages: write`.

---

## Summary: Which Path Should I Use?

| My situation | Use |
|---|---|
| Interpreter written in Python | Part A (pip / PyPI) |
| Transpiler that emits JavaScript, tooling in JS/TS | Part B (npm) |
| Native dependencies (Flex/Bison, LLVM, C compiler) | Part C (Docker / ghcr.io) |
| I want both pip install and docker run to work | Parts A + C (they are independent) |

The most important thing is that someone who has never seen your language can install it in one command and run a program in under two minutes. Pick the packaging path that makes that true for your project.
