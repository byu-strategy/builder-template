#!/usr/bin/env python3
"""Bring this repo's course skills up to date with the class template, in a few seconds.

Every course skill runs this first. It downloads the template's .claude/skills from GitHub
(byu-strategy/builder-template, main), replaces each course skill folder that differs, adds any that
are missing, and commits only .claude/skills. Skills you wrote yourself, under other names, are never
touched. Nothing else in the repo changes. If GitHub cannot be reached it says so and changes nothing,
so the skill you ran carries on with the copy you have.

Prints one line: UP TO DATE, or UPDATED: <names>, or SKIPPED: <why>.
"""
import io, shutil, subprocess, sys, tarfile, tempfile, urllib.request
from pathlib import Path

TEMPLATE = "https://github.com/byu-strategy/builder-template"
# Download by commit, not by branch name: the branch tarball is cached for minutes after a push.
URL = "https://codeload.github.com/byu-strategy/builder-template/tar.gz/{sha}"


def git(*args, cwd):
    return subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, timeout=30)


def main():
    root = git("rev-parse", "--show-toplevel", cwd=Path.cwd())
    if root.returncode:
        print("SKIPPED: not inside a git repo")
        return
    root = Path(root.stdout.strip())
    origin = git("remote", "get-url", "origin", cwd=root).stdout.strip()
    if origin.rstrip("/").removesuffix(".git").endswith("byu-strategy/builder-template"):
        print("SKIPPED: this is the class template itself")
        return
    skills = root / ".claude" / "skills"
    try:
        head = git("ls-remote", TEMPLATE, "refs/heads/main", cwd=root).stdout.split()
        data = urllib.request.urlopen(URL.format(sha=head[0] if head else "main"), timeout=20).read()
    except Exception as e:
        print(f"SKIPPED: could not reach GitHub ({type(e).__name__}); using the skills you have")
        return
    with tempfile.TemporaryDirectory() as tmp:
        with tarfile.open(fileobj=io.BytesIO(data), mode="r:gz") as tar:
            members = [m for m in tar.getmembers()
                       if "/.claude/skills/" in m.name and (m.isfile() or m.isdir()) and ".." not in m.name]
            tar.extractall(tmp, members=members)
        src = next(Path(tmp).glob("*/.claude/skills"), None)
        if not src:
            print("SKIPPED: the template had no skills folder")
            return
        changed = []
        for s in sorted(p for p in src.iterdir() if p.is_dir()):
            d = skills / s.name
            if d.is_symlink():          # an instructor's hub links to the source; leave it
                continue
            if d.exists() and same(s, d):
                continue
            if d.exists():
                shutil.rmtree(d)
            shutil.copytree(s, d)
            changed.append(s.name)
    if not changed:
        print("UP TO DATE")
        return
    git("add", "--", ".claude/skills", cwd=root)
    git("commit", "-m", "Update course skills", "--", ".claude/skills", cwd=root)
    print("UPDATED: " + ", ".join(changed))


def same(a, b):
    fa = {p.relative_to(a): p for p in a.rglob("*") if p.is_file() and "__pycache__" not in p.parts}
    fb = {p.relative_to(b): p for p in b.rglob("*") if p.is_file() and "__pycache__" not in p.parts}
    return fa.keys() == fb.keys() and all(fa[k].read_bytes() == fb[k].read_bytes() for k in fa)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:     # never stop the skill that called this
        print(f"SKIPPED: refresh failed ({type(e).__name__}: {e}); using the skills you have")
    sys.exit(0)
