---
name: repo-restructure
description: "Organizes messy Python repositories into a clean src/-based layout: moves scripts into src/, toy/examples into scripts/, docs into docs/, generated artifacts into outputs/, and updates imports, .gitignore, AGENTS.md, and pyproject.toml accordingly. Triggers: restructure repo, reorganize project, clean up file structure, src layout, python project structure, organize files, clean repo structure"
---

# Repo Restructure

Standardizes a messy Python repository into a clean, maintainable layout.

## Target Layout

```
├── src/                        # main package
│   ├── __init__.py
│   ├── train.py                # training entrypoint
│   ├── infer.py                # inference / demo entrypoint
│   └── models/                 # model definitions
│       ├── __init__.py
│       └── unet.py
├── scripts/                    # standalone / toy / scratch scripts
│   ├── x2_cuda.py
│   └── x2_nn.py
├── outputs/                    # generated artifacts (gitignored)
│   └── .gitkeep
├── docs/                       # documentation
│   └── uv-setup-guide.md
├── data/                       # downloaded datasets (gitignored)
├── (root)                      # config files only
│   ├── pyproject.toml
│   ├── README.md
│   ├── AGENTS.md
│   ├── .gitignore
│   ├── .python-version
│   └── uv.lock
```

## Migration Steps

### 1. Explore the Repo

Use `read` on the root directory and `pyproject.toml` to understand the current structure.

### 2. Create New Directories

```bash
mkdir -p src/models scripts outputs docs
```

### 3. Move Core Scripts → `src/`

- Rename entry points to clean names (e.g. `train_unet.py` → `src/train.py`)
- Update `from models.unet import ...` → `from src.models.unet import ...`
- Update file save/load paths to use `outputs/` prefix

### 4. Move Model Definitions → `src/models/`

```bash
mv models/unet.py src/models/unet.py
mv models/__init__.py src/models/__init__.py
rm -rf models
```

### 5. Move Toy/Scratch Scripts → `scripts/`

```bash
mv x2_*.py scripts/
```

### 6. Move Generated Artifacts → `outputs/`

```bash
mv *.pth *.png outputs/ 2>/dev/null; true
```

### 7. Move Documentation → `docs/`

```bash
mv *-guide.md docs/ 2>/dev/null; true
rm -f *:Zone.Identifier  # clean Windows NTFS artifacts
```

### 8. Delete Dead Stubs

```bash
rm main.py                           # legacy entrypoint
rm train_unet.py infer_unet.py       # old root-level scripts
```

### 9. Update `.gitignore`

Add entries for generated dirs:

```gitignore
# Generated artifacts (model weights, figures)
outputs/

# Downloaded datasets
data/
```

### 10. Update `AGENTS.md`

- Reflect new file paths in the Structure section
- Update run commands to use `uv run python -m src.train` / `uv run python -m src.infer`

### 11. Update `pyproject.toml`

Fix the `description` field if it's still a placeholder.

### 12. Verify

```bash
uv run python -m src.train    # training works
uv run python -m src.infer    # inference works
```

## When to Use

This skill triggers on user messages about:
- "restructure", "reorganize", "clean up" the repo or project structure
- "src layout" or "better file structure"
- "organize files" or "clean repo"
- Python projects with loose root-level scripts, dead stubs, and mixed artifacts
