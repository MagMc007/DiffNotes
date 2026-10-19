"""Read and clean git diffs."""

import re
import subprocess

from .errors import EmptyDiffError, InputError

# Lockfiles: changes here are noise for a PR description.
LOCKFILE_PATTERNS = (
    "package-lock.json",
    "yarn.lock",
    "pnpm-lock.yaml",
    "poetry.lock",
    "Cargo.lock",
    "Pipfile.lock",
    "Gemfile.lock",
    "composer.lock",
)

# A new file section starts at column 0. This avoids matching the
# literal string inside file content.
_DIFF_HEADER = re.compile(r"^diff --git ", re.MULTILINE)


def read_git_diff(staged: bool = False, base: str | None = None) -> str:
    """Run git diff and return the raw text."""
    cmd = ["git", "diff"]
    if staged:
        cmd.append("--staged")
    elif base:
        cmd.append(base)

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    except FileNotFoundError as e:
        raise InputError("git is not installed or not on PATH") from e
    except subprocess.CalledProcessError as e:
        raise InputError(f"git diff failed: {e.stderr.strip()}") from e

    return result.stdout


def filter_diff(text: str) -> tuple[str, list[str]]:
    """Drop lockfiles and binary files.

    Returns (kept_text, skipped_filenames). Raises EmptyDiffError
    if nothing survives.
    """
    chunks = _DIFF_HEADER.split(text)
    # First chunk is whatever preceded the first header (usually empty).
    chunks = [c for c in chunks if c.strip()]

    kept: list[str] = []
    skipped: list[str] = []

    for chunk in chunks:
        # Header line: "a/path b/path" -> recover the filename
        first_line = chunk.splitlines()[0]
        path = first_line.split()[-1].removeprefix("b/")

        if any(path.endswith(p) for p in LOCKFILE_PATTERNS):
            skipped.append(f"{path} (lockfile)")
            continue
        if "Binary files " in chunk.split("---")[0] or "\n+++ " not in chunk:
            skipped.append(f"{path} (binary)")
            continue

        kept.append("diff --git " + chunk)  # re-attach the header we split on

    if not kept:
        raise EmptyDiffError("no usable changes after filtering")

    return "\n".join(kept), skipped