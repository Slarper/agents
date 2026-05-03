---
name: fetch-arxiv
description: Downloads TeX source and PDF of an arxiv paper to local directories
---

# fetch-arxiv

Downloads TeX source and PDF of an arxiv paper to local directories.

## When to Use

Use this skill when asked to download, fetch, or save an arxiv paper.

## Workflow

Given an arxiv URL like `https://arxiv.org/abs/2601.07372`:

### Step 1: Extract arxiv ID

Extract the arxiv ID from the URL (e.g., `2601.07372` from `https://arxiv.org/abs/2601.07372`).

### Step 2: Get paper title

Fetch the abstract page (`https://arxiv.org/abs/{arxiv_id}`) and extract the paper title from the HTML `<h1 class="title mathjax">` element. Normalize the title to a slug (lowercase, replace spaces with hyphens, remove non-alphanumeric characters except hyphens).

Set the output directory to `./{arxiv_id}-{title_slug}/` (relative to the user's working directory). For example: `./2601.07372-efficient-memory-management/`.

Cache the directory name in `{output_dir}/tmp/{arxiv_id}.dir` so that re-running for the same paper reuses the same directory.

### Step 3: Download PDF

Download `https://arxiv.org/pdf/{arxiv_id}.pdf` to `{output_dir}/pdf/{arxiv_id}.pdf`.

Use `curl -fL` and create the `pdf/` subdirectory if it doesn't exist.

### Step 4: Download TeX source

Download `https://arxiv.org/src/{arxiv_id}` (which returns a `.tar.gz`) and extract it to `{output_dir}/source/`.

Steps:
1. Download to `{output_dir}/tmp/{arxiv_id}.tar.gz` (skip if already cached)
2. Extract the `.tar.gz` into `{output_dir}/source/`, overwriting any existing files

### Step 5: Report

Confirm to the user what was downloaded, e.g.:
- PDF: `{output_dir}/pdf/{arxiv_id}.pdf`
- Source: `{output_dir}/source/` (with N files extracted)
