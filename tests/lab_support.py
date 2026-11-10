"""Shared paths and helpers for the "Release day" lab.

Standard library only. Every Git call uses an argument list, never a shell.
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path

LAB_ROOT = Path(__file__).resolve().parent.parent
FIXTURES = LAB_ROOT / "fixtures"
STARTER = LAB_ROOT / "starter"
REPO = STARTER / "release-day"
ORIGIN = STARTER / "origin.git"

MAIN = "main"
FEATURE = "feature/release-notes"

# Paths the lab creates. Reset and cleanup remove the whole starter folder
# contents and rebuild them from fixtures/, so any file a learner added there
# is removed too.
CREATED_PATHS = [
    REPO,
    ORIGIN,
    LAB_ROOT / "tests" / "__pycache__",
]
EMPTY_EXCLUDES = ".git/info/no-global-excludes"

# Repository-local settings only. Setup never changes the learner's Git config. Its own Git
# calls run with FIXED below: system config is always off, personal config off on Git 2.32+.
LOCAL_CONFIG = [
    ("user.name", "PEP Learner"),
    ("user.email", "learner@example.invalid"),
    ("core.autocrlf", "false"),
    ("commit.gpgsign", "false"),
    ("merge.conflictStyle", "merge"),
    ("pull.rebase", "false"),
    # An empty repository-local excludes file replaces any global one, so a
    # personal ignore rule cannot hide the starting state. Relative to the repository top.
    ("core.excludesFile", EMPTY_EXCLUDES),
]

# Fixed identity and timestamps make every learner's starting history identical.
# GIT_CONFIG_GLOBAL points setup's own commits away from personal hooks or signing settings.
FIXED = {
    "GIT_AUTHOR_NAME": "PEP Lab",
    "GIT_AUTHOR_EMAIL": "lab@example.invalid",
    "GIT_COMMITTER_NAME": "PEP Lab",
    "GIT_COMMITTER_EMAIL": "lab@example.invalid",
    "GIT_CONFIG_GLOBAL": os.devnull,
    "GIT_CONFIG_NOSYSTEM": "1",
}


def inside(path, parent):
    """True when path resolves to parent or somewhere below it."""
    resolved = Path(path).resolve()
    base = Path(parent).resolve()
    return resolved == base or base in resolved.parents


def remove(path):
    """Remove a lab-created path after confirming it is inside the starter or tests folder."""
    path = Path(path)
    if not (inside(path, STARTER) or inside(path, LAB_ROOT / "tests")):
        raise RuntimeError(f"refusing to remove {path}: outside the lab")
    if path.is_dir() and not path.is_symlink():
        if sys.version_info >= (3, 12):
            shutil.rmtree(path, onexc=_retry_writable)
        else:
            shutil.rmtree(path, onerror=_retry_writable)
    elif path.exists() or path.is_symlink():
        path.unlink()


def _retry_writable(func, target, _info):
    # Windows marks Git object files read-only; clear that and retry once.
    os.chmod(target, 0o700)
    func(target)


def write_fixture(source, target):
    """Copy fixture text with LF line endings so history bytes are identical on every OS."""
    data = Path(source).read_bytes().replace(b"\r\n", b"\n")
    Path(target).parent.mkdir(parents=True, exist_ok=True)
    Path(target).write_bytes(data)


def reset_starter():
    """Remove every lab-created path."""
    for path in CREATED_PATHS:
        remove(path)


def restore_starter_files():
    """Write the shipped starter bytes: the working tree exactly as setup leaves it."""
    for source in sorted((FIXTURES / "initial").iterdir()):
        write_fixture(source, REPO / source.name)
    write_fixture(FIXTURES / "debug" / "status_message.py", REPO / "status_message.py")
    write_fixture(FIXTURES / "wip" / "RELEASE_NOTES.md", REPO / "RELEASE_NOTES.md")


def git_env(extra=None):
    env = dict(os.environ)
    # The ceiling stops Git from climbing out of the lab into any enclosing repository.
    env.update(
        {
            "LC_ALL": "C",
            "LANG": "C",
            "GIT_TERMINAL_PROMPT": "0",
            "GIT_CEILING_DIRECTORIES": str(STARTER.resolve()),
        }
    )
    if extra:
        env.update(extra)
    return env


def git(*args, repo=None, env=None, check=True):
    """Run git inside the lab repository (or another lab path) and return the result."""
    where = Path(repo) if repo is not None else REPO
    result = subprocess.run(
        ["git", "-C", str(where), *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
        env=git_env(env),
    )
    if check and result.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} failed: {result.stderr.strip()}")
    return result


def out(*args, repo=None, env=None):
    """Run git and return stripped stdout."""
    return git(*args, repo=repo, env=env).stdout.strip()
