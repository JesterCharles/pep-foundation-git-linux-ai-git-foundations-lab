# Git Foundations lab: release day

The deploy status helper is about to get its v1.1 release, and three things happen
at once: a debug print was pushed straight to `main`, a teammate pushed their own
release-notes line, and your half-written notes are still uncommitted. You use Git
to:
- set your work aside with `stash`;
- undo the shared mistake safely with `revert`;
- finish your notes on a branch and remove a local-only mistake with `reset`;
- fetch and pull the teammate's work;
- resolve a merge conflict, merge, and push to the team's remote.

The team's "remote" is a local folder, so the lab runs offline. 10 checks read the
real state of the lab repository and its remote.

The full learner instructions are in [`.evolv/instructions.md`](.evolv/instructions.md), which the lab platform shows as the lab's instructions.

## Layout

This repository follows the Exa coding-lab scaffold for Python.

| Path | What it is |
|---|---|
| `src/release-day/` | The lab repository the learner works in (setup makes it a Git repository) |
| `src/origin.git/` | The team's remote, created by setup (not committed) |
| `test/test_release_day.py` | Visible checks |
| `test/setup_lab.py` | Creates (or resets) the lab repository and its remote |
| `test/cleanup_lab.py` | Removes both repositories and restores the shipped files |
| `test/lab_support.py` | Paths and Git helpers the scripts and checks share |
| `test/conftest.py` | Counts a check that could not run (lab not set up) as a failure |
| `fixtures/` | The files setup builds the history from |
| `.evolv/instructions.md` | Learner instructions |
| `.evolv/grade.yml` | Grading manifest, used by Run Tests and by the grader |
| `requirements.txt` | pytest, the only Python dependency |
| `Dockerfile` | Grader image with Git and the dependencies baked in |
| `expected/on-completion.txt` | The result of a finished lab |

There are no held-out tests in this lab: every check is visible.

## Run the tests

With Git 2.23 or later and Python 3.11 or later, set the lab up once, then run the
checks:

```
python test/setup_lab.py
python -m pytest -q
```

On the platform, **Run Tests** runs the second command. All 10 checks fail until the
steps are done. That is expected. Grading never runs `test/setup_lab.py`.
