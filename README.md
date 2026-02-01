# Valentine's Day Website

A static Valentine's Day website with an un-clickable "No" button. Built with a Python script that generates HTML from YAML config and Markdown.

## Setup

Requires Python 3 and [Task](https://taskfile.dev).

```bash
task setup    # creates venv and installs dependencies
source init.sh  # activates the venv
```

## Build

```bash
task build
```

Generates static files in `_site/`. Open `_site/index.html` in a browser to preview.

## Deploy

Pushes to `main` automatically build and deploy to GitHub Pages via GitHub Actions.


