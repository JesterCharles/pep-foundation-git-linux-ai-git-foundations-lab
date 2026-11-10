"""Create (or reset) the lab repository in starter/release-day/ and its local remote.

Run from the lab folder:  python tests/setup_lab.py
Re-running it is the reset path: it replaces all work inside starter/.
"""

import shutil
import sys

from lab_support import (
    EMPTY_EXCLUDES,
    FIXED,
    FIXTURES,
    LOCAL_CONFIG,
    MAIN,
    ORIGIN,
    REPO,
    STARTER,
    git,
    remove,
    reset_starter,
    write_fixture,
)


def run(*args, repo=None):
    """Run one of setup's own Git commands with personal and system Git settings switched off."""
    return git(*args, repo=repo, env=FIXED)


def commit(message, timestamp, repo=None):
    stamp = f"{timestamp} +0000"
    env = dict(FIXED, GIT_AUTHOR_DATE=stamp, GIT_COMMITTER_DATE=stamp)
    run("add", "--all", repo=repo)
    git("commit", "--quiet", "--no-verify", "-m", message, repo=repo, env=env)


def main():
    if shutil.which("git") is None:
        sys.exit("Git was not found. Install Git, check `git --version`, then run setup again.")
    if sys.version_info < (3, 11):
        sys.exit("Python 3.11 or newer is required. Check `python --version`.")

    if (REPO / ".git").exists():
        print("WARNING: resetting the lab. All work inside starter/ is replaced.")
    reset_starter()

    # Initial project on main.
    for source in sorted((FIXTURES / "initial").iterdir()):
        write_fixture(source, REPO / source.name)
    run("init", "--quiet")
    run("symbolic-ref", "HEAD", f"refs/heads/{MAIN}")
    (REPO / EMPTY_EXCLUDES).parent.mkdir(parents=True, exist_ok=True)
    (REPO / EMPTY_EXCLUDES).write_bytes(b"")
    for key, value in LOCAL_CONFIG:
        run("config", "--local", key, value)
    commit("Add deployment status helper", 1767261600)

    # Someone committed a debug print straight to main and it was pushed.
    write_fixture(FIXTURES / "debug" / "status_message.py", REPO / "status_message.py")
    commit("Add debug print for support", 1767265200)

    # The local bare repository stands in for the team's shared remote.
    run("init", "--quiet", "--bare", str(ORIGIN), repo=STARTER)
    run("symbolic-ref", "HEAD", f"refs/heads/{MAIN}", repo=ORIGIN)
    run("remote", "add", "origin", "../origin.git")
    run("push", "--quiet", "--no-verify", "origin", MAIN)

    # A teammate then pushed a README update, with their own v1.1 release-notes line,
    # that this clone has not fetched yet. That line later conflicts with yours.
    teammate = STARTER / "tmp-teammate"
    remove(teammate)
    run("-c", "core.autocrlf=false", "clone", "--quiet", str(ORIGIN), str(teammate), repo=STARTER)
    for key, value in LOCAL_CONFIG[:4]:
        run("config", "--local", key, value, repo=teammate)
    write_fixture(FIXTURES / "teammate" / "README.md", teammate / "README.md")
    write_fixture(FIXTURES / "teammate" / "RELEASE_NOTES.md", teammate / "RELEASE_NOTES.md")
    commit("Document the support rotation", 1767268800, repo=teammate)
    run("push", "--quiet", "--no-verify", "origin", MAIN, repo=teammate)
    remove(teammate)

    # Your own half-written release notes wait, uncommitted, in the working tree.
    write_fixture(FIXTURES / "wip" / "RELEASE_NOTES.md", REPO / "RELEASE_NOTES.md")

    print("Lab ready in starter/release-day/ on branch main, with a local remote in starter/origin.git.")
    print("Next: cd starter/release-day, then run git status.")


if __name__ == "__main__":
    main()
