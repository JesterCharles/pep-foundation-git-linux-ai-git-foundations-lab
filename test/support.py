"""Shared helpers for the "Release day" checks.

The checks never touch this project folder. Each one builds the release-day
scenario from test/fixtures in a fresh temporary folder: a bare repository that
stands in for the team's remote (origin.git) and your clone of it
(release-day). It then runs your step scripts from src/ inside the clone with
bash and inspects the result with Git.

To check one step on its own, the earlier steps are first done for you,
correctly, with the commands the lab README shows. Each check therefore
judges only the script for its own step.
"""

import os
import shutil
import subprocess
from pathlib import Path

import pytest

LAB_ROOT = Path(__file__).resolve().parent.parent
SRC = LAB_ROOT / "src"
FIXTURES = Path(__file__).resolve().parent / "fixtures"

MAIN = "main"
FEATURE = "feature/release-notes"
DEBUG_SUBJECT = "Add debug print for support"
TEAMMATE_SUBJECT = "Document the support rotation"
NOTES_SUBJECT = "Finish v1.1 release notes"
DEBUG_LINE = "DEBUG: remove before release"
YOUR_BULLET = "- The deployment name now comes from DEPLOY_ENV, with a development fallback."
TEAMMATE_BULLET = "- The README now documents the support rotation."
V10_BULLET = "- First release of the deploy status helper."
MARKERS = ("<<<<<<<", "=======", ">>>>>>>")

FIRST_STEP = 4
LAST_STEP = 10
SCRIPTS = {
    4: "step4_stash.sh",
    5: "step5_revert.sh",
    6: "step6_release_notes.sh",
    7: "step7_scratch_reset.sh",
    8: "step8_pull_teammate.sh",
    9: "step9_resolve_conflict.sh",
    10: "step10_merge_and_push.sh",
}
SCRIPT_TIMEOUT = 60

# Repository-local settings for the clone, so results do not depend on anyone's
# personal Git setup. The checks also switch personal and system config off.
LOCAL_CONFIG = [
    ("user.name", "PEP Learner"),
    ("user.email", "learner@example.invalid"),
    ("core.autocrlf", "false"),
    ("commit.gpgsign", "false"),
    ("merge.conflictStyle", "merge"),
    ("pull.rebase", "false"),
    ("core.excludesFile", ".git/info/no-global-excludes"),
]

FINISHED_NOTES = f"""# Release notes

## v1.1

{YOUR_BULLET}

## v1.0

{V10_BULLET}
"""

RESOLVED_NOTES = f"""# Release notes

## v1.1

{YOUR_BULLET}
{TEAMMATE_BULLET}

## v1.0

{V10_BULLET}
"""

# The correct commands for each step, exactly as the lab README shows them.
# A check for step N runs these for the steps before N, then your script for N.
REFERENCE = {
    4: "git stash\n",
    5: "git revert --no-edit HEAD\n",
    6: (
        f"git switch -c {FEATURE}\n"
        "git stash pop\n"
        f"cat > RELEASE_NOTES.md <<'EOF'\n{FINISHED_NOTES}EOF\n"
        "git add RELEASE_NOTES.md\n"
        f'git commit -m "{NOTES_SUBJECT}"\n'
    ),
    7: (
        "echo scratch > scratch.tmp\n"
        "git add scratch.tmp\n"
        'git commit -m "WIP scratch"\n'
        "git reset --hard HEAD~1\n"
    ),
    8: (
        f"git switch {MAIN}\n"
        "git fetch origin\n"
        f"git pull --no-edit origin {MAIN}\n"
    ),
    9: (
        f"git switch {FEATURE}\n"
        f"git merge {MAIN} || true\n"
        f"cat > RELEASE_NOTES.md <<'EOF'\n{RESOLVED_NOTES}EOF\n"
        "git add RELEASE_NOTES.md\n"
        "git commit --no-edit\n"
    ),
    10: (
        f"git switch {MAIN}\n"
        f"git merge {FEATURE}\n"
        f"git push origin {MAIN}\n"
    ),
}


def require_tools():
    for tool in ("bash", "git"):
        if shutil.which(tool) is None:
            pytest.fail(
                f"`{tool}` was not found on PATH. These checks run your scripts with bash and "
                "Git on Linux (or macOS, WSL, Git Bash). Install it and run the tests again.",
                pytrace=False,
            )


def git_env(root, stamp, name="PEP Learner", email="learner@example.invalid"):
    """Environment for every Git call: no personal or system config, fixed identity and time."""
    env = {key: value for key, value in os.environ.items() if not key.startswith("GIT_")}
    when = f"{stamp} +0000"
    env.update(
        {
            "LC_ALL": "C",
            "LANG": "C",
            "GIT_CONFIG_GLOBAL": os.devnull,
            "GIT_CONFIG_NOSYSTEM": "1",
            "GIT_CONFIG_COUNT": "1",
            "GIT_CONFIG_KEY_0": "init.defaultBranch",
            "GIT_CONFIG_VALUE_0": MAIN,
            "GIT_CEILING_DIRECTORIES": str(root),
            "GIT_TERMINAL_PROMPT": "0",
            # A command that would open an editor accepts the default message instead
            # of waiting forever; one that would open a pager prints directly.
            "GIT_EDITOR": "true",
            "GIT_SEQUENCE_EDITOR": "true",
            "GIT_PAGER": "cat",
            "PAGER": "cat",
            "GIT_AUTHOR_NAME": name,
            "GIT_AUTHOR_EMAIL": email,
            "GIT_COMMITTER_NAME": name,
            "GIT_COMMITTER_EMAIL": email,
            "GIT_AUTHOR_DATE": when,
            "GIT_COMMITTER_DATE": when,
        }
    )
    return env


def write_fixture(source, target):
    """Copy fixture text with LF line endings so history bytes are identical on every OS."""
    data = Path(source).read_bytes().replace(b"\r\n", b"\n")
    Path(target).parent.mkdir(parents=True, exist_ok=True)
    Path(target).write_bytes(data)


def _git(root, repo, *args, stamp=1767261600, name="PEP Lab", email="lab@example.invalid"):
    result = subprocess.run(
        ["git", "-C", str(repo), *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
        env=git_env(root, stamp, name, email),
        stdin=subprocess.DEVNULL,
    )
    if result.returncode != 0:
        raise RuntimeError(f"building the scenario failed: git {' '.join(args)}: {result.stderr.strip()}")
    return result.stdout


def _commit(root, repo, message, stamp):
    _git(root, repo, "add", "--all", stamp=stamp)
    _git(root, repo, "commit", "--quiet", "--no-verify", "-m", message, stamp=stamp)


class Scenario:
    """The release-day clone and its remote, inside one temporary folder."""

    def __init__(self, root):
        self.root = Path(root)
        self.repo = self.root / "release-day"
        self.origin = self.root / "origin.git"

    # ---- queries -----------------------------------------------------------
    def git(self, *args, repo=None):
        return subprocess.run(
            ["git", "-C", str(repo or self.repo), *args],
            capture_output=True,
            text=True,
            encoding="utf-8",
            env=git_env(self.root, 1767261600),
            stdin=subprocess.DEVNULL,
        )

    def out(self, *args, repo=None):
        return self.git(*args, repo=repo).stdout.strip()

    def ok(self, *args, repo=None):
        return self.git(*args, repo=repo).returncode == 0

    def branch_exists(self, name):
        return self.ok("rev-parse", "--verify", "--quiet", f"refs/heads/{name}")

    def current_branch(self):
        return self.out("symbolic-ref", "--quiet", "--short", "HEAD")

    def subjects(self, ref):
        return self.out("log", "--format=%s", ref).splitlines()

    def file_at(self, ref, path):
        return self.out("show", f"{ref}:{path}")

    def commit_with_subject(self, ref, subject):
        """The newest non-merge commit reachable from ref with exactly this subject, or None."""
        for line in self.out("log", "--no-merges", "--format=%H%x09%s", ref).splitlines():
            sha, _, text = line.partition("\t")
            if text == subject:
                return sha
        return None

    def contains(self, ref, commit):
        return self.ok("merge-base", "--is-ancestor", commit, ref)

    def joining_merge(self, ref, first, second):
        """A merge commit on ref whose two parents bring in `first` and `second` separately."""
        for merge in self.out("rev-list", "--merges", ref).split():
            parents = self.out("rev-list", "--parents", "-n", "1", merge).split()[1:]
            if len(parents) != 2:
                continue
            has = [(self.contains(p, first), self.contains(p, second)) for p in parents]
            if (True, False) in has and (False, True) in has:
                return merge
        return None

    def stash_entries(self):
        return [line for line in self.out("stash", "list").splitlines() if line.strip()]

    def status(self):
        return self.out("status", "--porcelain")

    def reflog_subjects(self, ref):
        return self.out("reflog", "show", "--format=%gs", ref).splitlines()


def build_scenario(root):
    """Create origin.git and the release-day clone exactly as the lab starts.

    main holds the initial commit and the pushed debug commit; origin also has a
    teammate's commit you have not fetched; your half-written release notes are
    uncommitted in the working copy.
    """
    root = Path(root)
    root.mkdir(parents=True, exist_ok=True)
    scenario = Scenario(root)
    repo, origin = scenario.repo, scenario.origin
    repo.mkdir()

    for source in sorted((FIXTURES / "initial").iterdir()):
        write_fixture(source, repo / source.name)
    _git(root, repo, "init", "--quiet")
    _git(root, repo, "symbolic-ref", "HEAD", f"refs/heads/{MAIN}")
    (repo / ".git" / "info").mkdir(parents=True, exist_ok=True)
    (repo / ".git" / "info" / "no-global-excludes").write_bytes(b"")
    for key, value in LOCAL_CONFIG:
        _git(root, repo, "config", "--local", key, value)
    _commit(root, repo, "Add deployment status helper", 1767261600)

    # Someone committed a debug print straight to main and it was pushed.
    write_fixture(FIXTURES / "debug" / "status_message.py", repo / "status_message.py")
    _commit(root, repo, DEBUG_SUBJECT, 1767265200)

    _git(root, root, "init", "--quiet", "--bare", str(origin))
    _git(root, origin, "symbolic-ref", "HEAD", f"refs/heads/{MAIN}")
    _git(root, repo, "remote", "add", "origin", "../origin.git")
    _git(root, repo, "push", "--quiet", "--no-verify", "origin", MAIN)

    # A teammate then pushed a README update with their own v1.1 release-notes
    # line, which this clone has not fetched yet. That line conflicts with yours later.
    teammate = root / "teammate"
    _git(root, root, "-c", "core.autocrlf=false", "clone", "--quiet", str(origin), str(teammate))
    write_fixture(FIXTURES / "teammate" / "README.md", teammate / "README.md")
    write_fixture(FIXTURES / "teammate" / "RELEASE_NOTES.md", teammate / "RELEASE_NOTES.md")
    _commit(root, teammate, TEAMMATE_SUBJECT, 1767268800)
    _git(root, teammate, "push", "--quiet", "--no-verify", "origin", MAIN)
    shutil.rmtree(teammate, ignore_errors=True)

    # Your own half-written release notes wait, uncommitted, in the working copy.
    write_fixture(FIXTURES / "wip" / "RELEASE_NOTES.md", repo / "RELEASE_NOTES.md")
    return scenario


def step_stamp(step):
    return 1767272400 + step * 600


def _run_bash(scenario, step, script_text, label):
    try:
        return subprocess.run(
            ["bash", "-c", script_text, label],
            cwd=scenario.repo,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            env=git_env(scenario.root, step_stamp(step)),
            stdin=subprocess.DEVNULL,
            timeout=SCRIPT_TIMEOUT,
        )
    except subprocess.TimeoutExpired:
        pytest.fail(
            f"Step {step}: {label} did not finish within {SCRIPT_TIMEOUT} seconds. Is a command "
            "waiting for input, such as an editor or a pager?",
            pytrace=False,
        )


def apply_reference(scenario, before):
    """Do every step before `before` correctly, as the lab README shows."""
    for step in range(FIRST_STEP, before):
        result = _run_bash(scenario, step, "set -euo pipefail\n" + REFERENCE[step], f"reference step {step}")
        if result.returncode != 0:
            raise RuntimeError(f"reference step {step} failed: {result.stderr.strip()}")


def script_path(step):
    return SRC / SCRIPTS[step]


def run_step(scenario, step):
    """Run your script for `step` inside the clone; fail with its output if it errors."""
    path = script_path(step)
    if not path.is_file():
        pytest.fail(f"Step {step}: src/{SCRIPTS[step]} is missing. Restore it from the starter.", pytrace=False)
    # Windows checkouts may add CR line endings, which bash cannot run; strip them.
    text = path.read_bytes().decode("utf-8", errors="replace").replace("\r\n", "\n")
    result = _run_bash(scenario, step, text, f"src/{SCRIPTS[step]}")
    if result.returncode != 0:
        tail = "\n".join((result.stdout + result.stderr).strip().splitlines()[-12:])
        pytest.fail(
            f"Step {step}: src/{SCRIPTS[step]} stopped with exit code {result.returncode}. "
            f"Its last output:\n{tail}",
            pytrace=False,
        )
    return result


def scenario_after_step(tmp_path, step):
    """A fresh scenario with steps before `step` done correctly, then your script for `step`."""
    require_tools()
    scenario = build_scenario(tmp_path / "lab")
    apply_reference(scenario, step)
    run_step(scenario, step)
    return scenario


def note_lines(text):
    return [line.strip() for line in text.splitlines() if line.strip()]
