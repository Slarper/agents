#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///

"""
git-mastery: credential & PAT auth helpers for git pull/push.

Usage:
  git-mastery.py push    <target-dir> "<commit-message>"
  git-mastery.py pull    <target-dir>          # merge, keep local
  git-mastery.py pull!   <target-dir>          # override local with remote
"""

import os, subprocess, sys
from pathlib import Path


def bail(msg: str):
    print(f"fatal: {msg}", file=sys.stderr)
    sys.exit(1)


def sh(*cmd: str, cwd: str | None = None) -> str:
    r = subprocess.run(cmd, capture_output=True, text=True, cwd=cwd)
    if r.returncode != 0:
        bail(f"{' '.join(cmd)} failed:\n{r.stderr}")
    return r.stdout.strip()


def load_env(target_dir: str) -> str:
    env_path = Path(target_dir) / ".env"
    if env_path.exists():
        for line in env_path.read_text().splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            k, _, v = line.partition("=")
            os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))

    token = os.environ.get("GITHUB_FINE_GRAINED_PERSONAL_ACCESS_TOKEN") or os.environ.get("GITHUB_TOKEN") or ""
    if not token:
        bail("GITHUB_FINE_GRAINED_PERSONAL_ACCESS_TOKEN not set in .env")
    return token


def with_pat(target_dir: str, token: str, fn):
    original = sh("git", "remote", "get-url", "origin", cwd=target_dir)
    askpass = Path("/tmp") / f"git_askpass_{os.getpid()}.sh"
    askpass.write_text(f'#!/bin/sh\necho "{token}"\n')
    askpass.chmod(0o755)
    os.environ["GIT_ASKPASS"] = str(askpass)
    try:
        fn()
    finally:
        askpass.unlink(missing_ok=True)
        os.environ.pop("GIT_ASKPASS", None)
        sh("git", "remote", "set-url", "origin", original, cwd=target_dir)


def cmd_push(target_dir: str, msg: str) -> None:
    token = load_env(target_dir)

    def push():
        sh("git", "add", "-A", cwd=target_dir)
        if not sh("git", "diff", "--cached", "--name-only", cwd=target_dir):
            print("nothing to commit")
            return
        sh("git", "commit", "-m", msg, cwd=target_dir)
        sh("git", "push", "-u", "origin", "main", cwd=target_dir)
        print(f"✓ pushed to origin/main")

    with_pat(target_dir, token, push)


def cmd_pull(target_dir: str, force: bool = False) -> None:
    token = load_env(target_dir)

    def pull():
        sh("git", "fetch", "origin", "main", cwd=target_dir)
        if force:
            sh("git", "reset", "--hard", "origin/main", cwd=target_dir)
            print("✓ reset to origin/main (local changes discarded)")
        else:
            r = subprocess.run(
                ["git", "pull", "origin", "main"],
                capture_output=True, text=True, cwd=target_dir,
            )
            print(r.stdout or r.stderr, end="")
            if r.returncode != 0:
                conflicted = sh("git", "diff", "--name-only", "--diff-filter=U", cwd=target_dir)
                if not conflicted:
                    sys.exit(r.returncode)
                for path in conflicted.splitlines():
                    choice = input(f"CONFLICT {path}: keep (r)emote or (l)ocal? [r/l] ").strip().lower()
                    sh("git", "checkout", "--theirs" if choice == "r" else "--ours", path, cwd=target_dir)
                    sh("git", "add", path, cwd=target_dir)
                sh("git", "commit", "-m", "Merge remote into local", cwd=target_dir)
                print("✓ conflicts resolved and committed")

    with_pat(target_dir, token, pull)


if __name__ == "__main__":
    if len(sys.argv) < 3 or sys.argv[1] in ("-h", "--help"):
        print(__doc__)
        sys.exit(0)

    cmd, target_dir = sys.argv[1], os.path.abspath(sys.argv[2])

    if cmd == "push":
        if len(sys.argv) < 4:
            bail("usage: git-mastery.py push <target-dir> \"<commit-message>\"")
        cmd_push(target_dir, sys.argv[3])
    elif cmd == "pull":
        cmd_pull(target_dir, force=False)
    elif cmd == "pull!":
        print("⚠️  This will discard ALL local uncommitted changes and reset to origin/main")
        if input("Are you sure? (yes/no): ").strip().lower() != "yes":
            print("cancelled")
            sys.exit(0)
        cmd_pull(target_dir, force=True)
    else:
        bail(f"unknown command: {cmd}")
