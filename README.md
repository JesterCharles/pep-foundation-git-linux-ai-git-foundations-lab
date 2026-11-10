# Release day

The deploy status helper from "Ship a safe change" is about to get its v1.1 release.
You were halfway through the release notes when three things landed at once:
someone pushed a debug print straight to `main`, a teammate pushed a README update
you do not have yet (with their own line in the release notes), and your own
half-written notes are sitting uncommitted in the working copy.

Your job: set your unfinished work aside safely, undo the shared mistake the right
way, finish your notes on a branch, remove a local-only mistake, bring in the
teammate's work, resolve the conflict between their release-notes line and yours,
merge, and push the result to the team's remote.

About 21 minutes of your scheduled exercise block (an estimate); if you pass 25,
pause and finish in self-study, using **Troubleshooting** if you are stuck.
Everything runs on your own computer, offline: the "remote" is a local folder.
No account, no network, no container engine, no AI assistant.

## Open the project

This repository is the whole lab. Clone it, then open the cloned folder in VS Code or any
other editor or IDE (in VS Code: **File > Open Folder**). Nothing in this lab runs in a browser.

Run every command below in a terminal at the repository root, the folder that holds this
README: in VS Code use **Terminal > New Terminal**, which opens there; with any other editor,
open a terminal and `cd` into the clone. The steps call this folder the lab folder.

## What you edit

Setup (step 2) builds the repository you work in. Most checks read Git state -
history, branches, the stash, the remote - produced by your commands, and only
one file needs editing:

| You change | How | Why the release needs it |
|---|---|---|
| `starter/release-day/RELEASE_NOTES.md` | replace the TODO line with your v1.1 bullet, on a feature branch (step 6); then resolve the merge conflict so both v1.1 bullets stay (step 9) | v1.1 must not ship with unfinished notes or lose the teammate's line |
| `starter/release-day/status_message.py` | never by hand: `git revert` removes the pushed debug print (step 5) | the deploy helper must stop leaking debug output |
| the repository itself | stash, revert, branch, reset, fetch, pull, merge and push (steps 4-10) | the shared `main` must end clean, merged and pushed |

Leave `tests/`, `fixtures/` and `expected/` as they are: the ten
checks pass only when the repository really reached that state.

One test command proves the lab, run from this lab folder (step 11):

```text
python -m unittest discover -s tests -v
```

Each failing check prints the next action to take.

## 1. Check your tools

Open a terminal at the repository root (the folder that holds this README).
Type each command and press Enter:

```text
git --version
python --version
```

**Expect:** `git version 2.23` or newer, and `Python 3.11` or newer.

Every lab command starts with `python`.
If `python --version` fails, or prints a version older than 3.11, find the launcher that works in your terminal and make `python` mean it for this terminal window:

| Your terminal | Check this works and shows 3.11 or newer | Then type this once |
|---|---|---|
| macOS or Linux (zsh or bash) | `python3 --version` | `alias python=python3` |
| Windows PowerShell | `py -3 --version` | `Set-Alias python py` |
| Windows cmd | `py -3 --version` | `doskey python=py -3 $*` |
| Git Bash on Windows | `py -3 --version` | `alias python='py -3'` |

Run `python --version` again; **expect** `Python 3.11` or newer.
The alias lasts only for this terminal window: type it again if you open a new one.

## 2. Create the lab repository and its remote

From this lab folder, run:

```text
python tests/setup_lab.py
```

**Expect:** `Lab ready in starter/release-day/ on branch main, with a local remote in starter/origin.git.`

Setup builds a small Git repository in `starter/release-day/` and a bare repository
in `starter/origin.git/` that plays the role of the team's shared remote, already
connected as `origin`.
It sets a training name and email for those repositories only. Setup never changes
your own Git settings. Its own Git commands ignore your system Git settings, and on
Git 2.32 or newer your personal ones too (older Git still reads personal settings,
such as hooks, during setup). Each lab repository also gets a few local settings that
keep the exercise predictable: LF line endings, no commit signing, standard conflict
markers, merge on pull, and an empty ignore file in place of your personal one, so
your own ignore rules cannot hide lab files. Everything else in your own commands uses your settings.
Running setup again resets the lab: it deletes both folders, including any file you
added there, and rebuilds them.

Move into the repository:

```text
cd starter/release-day
```

(In Windows cmd, type `cd starter\release-day`.)

## 3. See what is going on

```text
git status
git diff
git log --oneline -3
```

**Expect:** you are `On branch main`; `RELEASE_NOTES.md` is modified but not staged
(your half-written notes, with a TODO line); and the newest commit is
`Add debug print for support` - the mistake someone already pushed.

## 4. Set your work aside with stash

The debug print is the urgent problem, and your notes are in the way.
Plain `git stash` saves changes to tracked files, staged or not, and leaves the
working copy clean:

```text
git stash
git status
```

**Expect:** `Saved working directory and index state ...`, then a clean working copy.
`git stash list` shows one entry. Your notes are safe; you will take them back in step 6.

## 5. Undo the shared debug commit with revert

Look at the damage, then check who already has this commit:

```text
git show --stat HEAD
git log --oneline origin/main
```

**Expect:** the debug commit is also the tip of `origin/main`: it was pushed, so
teammates may already have it. Rewriting shared history with `reset` would rewrite
commits out from under them. The safe undo for a shared commit is a **new** commit
that does the opposite:

```text
git revert --no-edit HEAD
```

**Expect:** a new commit `Revert "Add debug print for support"`.
Open `status_message.py`: the `DEBUG` line is gone, and `git log --oneline -3`
still shows the original debug commit below the revert - history was added to,
not rewritten.

## 6. Finish the release notes on a branch

Now your own task. Create a branch from `main` and take your notes back:

```text
git switch -c feature/release-notes
git stash pop
```

**Expect:** `Switched to a new branch 'feature/release-notes'`, then your
`RELEASE_NOTES.md` edit is back and the stash is empty (`git stash list` prints nothing).

Open `RELEASE_NOTES.md` and replace the whole TODO line with your bullet,
word for word:

```text
- The deployment name now comes from DEPLOY_ENV, with a development fallback.
```

Stage exactly that file by name and check what you are about to commit:

```text
git add RELEASE_NOTES.md
git status
git diff --staged
git commit -m "Finish v1.1 release notes"
```

**Expect:** one staged file before the commit, never `git add .` here.

## 7. Make a local-only mistake and remove it with reset

Create a scratch file and commit it by accident, the way it happens on real release days:

| Shell | Create the file |
|---|---|
| macOS, Linux, Git Bash | `echo scratch > scratch.tmp` |
| PowerShell | `Set-Content scratch.tmp scratch` |
| cmd | `echo scratch> scratch.tmp` |

```text
git add scratch.tmp
git commit -m "WIP scratch"
git log --oneline origin/main..HEAD
```

**Expect:** the log shows `WIP scratch` among the commits origin does not have.
Nobody else has this commit, so this is the one situation where rewriting history
is safe. `git reset --hard HEAD~1` moves the branch back one commit and makes the
working copy match; the scratch commit and the file disappear together:

```text
git reset --hard HEAD~1
git log --oneline -1
```

**Expect:** the tip is `Finish v1.1 release notes` again and `scratch.tmp` is gone.
(`--soft` would have kept the file staged; you wanted it gone entirely.
Had `WIP scratch` been pushed, the answer would be `revert`, as in step 5.)

## 8. Fetch, compare, and pull the teammate's work

Back to the team's work. Your clone has not seen the remote since setup.
Switch to `main` and download what is new, without touching your files yet:

```text
git switch main
git fetch origin
git log --oneline main..origin/main
git log --oneline origin/main..main
```

**Expect:** the first log shows `Document the support rotation` (origin has it,
you do not); the second shows your revert commit (you have it, origin does not).
`main` and `origin/main` are different things: your local branch and your last
known copy of the remote's branch. The two histories have diverged, so bring the
teammate's commit in with a merge:

```text
git pull --no-edit origin main
```

**Expect:** a merge line such as `Merge made by the 'ort' strategy.` (Git
older than 2.34 prints `'recursive'` instead - both are fine), and `README.md`
now ends with a `## Support` section. The teammate also added their own v1.1
line to `RELEASE_NOTES.md`; it merged cleanly here, because your release-notes
commit is still only on your branch. `git log --oneline --graph -5` shows a merge commit joining
the two diverged lines. (A rebase could replay your revert onto origin/main
instead - that is also safe here, because your revert was never pushed - but this
team merges, and you must never rebase commits other people already have.)

## 9. Bring main into your branch and resolve the conflict

Your branch and `main` each have a different v1.1 line in the same place of
`RELEASE_NOTES.md`. Settle that on your branch, before `main` gets it:

```text
git switch feature/release-notes
git merge main
```

**Expect:** `CONFLICT (content): Merge conflict in RELEASE_NOTES.md`, then
`Automatic merge failed; fix conflicts and then commit the result.` Git stopped
because both sides changed the same lines since they split, and it cannot know
which text you want. `git status` lists `both modified:   RELEASE_NOTES.md`
under **Unmerged paths**; `README.md` merged on its own.

Open `RELEASE_NOTES.md`. Its v1.1 section now looks like this:

```text
<<<<<<< HEAD
- The deployment name now comes from DEPLOY_ENV, with a development fallback.
=======
- The README now documents the support rotation.
>>>>>>> main
```

Between `<<<<<<< HEAD` and `=======` is your side, the branch you are on.
Between `=======` and `>>>>>>> main` is the side you are merging in: the
teammate's line, now on `main`. Both lines are true, so the final text keeps
both. Edit the file until the v1.1 section reads exactly like this, with all
three marker lines deleted:

```text
## v1.1

- The deployment name now comes from DEPLOY_ENV, with a development fallback.
- The README now documents the support rotation.
```

Some editors, VS Code among them, show buttons above the markers such as
**Accept Both Changes**. You may use them; then check that the result matches
the text above and that no marker line is left.

Save the file, then mark the conflict resolved and finish the merge:

```text
git add RELEASE_NOTES.md
git status
git commit --no-edit
```

**Expect:** after `git add`, `git status` says `All conflicts fixed but you are
still merging.`; the commit is `Merge branch 'main' into feature/release-notes`.
(Before that commit, `git merge --abort` puts the branch back as it was if you
want to start the merge again.)

## 10. Merge your branch and push

```text
git switch main
git merge feature/release-notes
git push origin main
```

**Expect:** the merge prints `Fast-forward` - your branch already contains
everything on `main`, so Git only moved the `main` pointer forward; compare that
with the real merge commits from steps 8 and 9. The push prints `main -> main`;
`origin/main` now matches your `main`.

## 11. Prove it

Return to the lab folder and run the checks:

```text
cd ../..
python -m unittest discover -s tests -v
```

(In Windows cmd, type `cd ..\..`.)

**Expect:** all ten checks report `ok`, then `OK` (see **Expected output** below).

## How the checks work

The test command is `python -m unittest discover -s tests -v`, run from this lab
folder. It reads the real state of both repositories with Git; it never needs the network.

| Check | What it confirms |
|---|---|
| `test_debug_commit_is_reverted` | a revert commit removed the debug print and the original commit is still in history |
| `test_teammate_update_is_merged` | `Document the support rotation` and the `## Support` section are on your `main` |
| `test_release_notes_are_finished` | on the feature branch, the TODO line became your DEPLOY_ENV bullet |
| `test_release_notes_conflict_is_resolved` | a merge joined your line with the teammate's, and `main` keeps both v1.1 bullets once each, with no conflict markers |
| `test_feature_branch_commit_is_focused` | the release-notes commit changes only `RELEASE_NOTES.md` |
| `test_scratch_mistake_is_fully_removed` | no commit anywhere still contains `scratch.tmp`, and the file is gone |
| `test_feature_is_merged_into_main` | `main` contains the feature branch |
| `test_main_is_pushed_to_origin` | the bare remote's `main` equals your `main` |
| `test_stash_is_empty_after_restore` | the stash entry was popped, not left behind |
| `test_worktree_is_clean_and_on_main` | you finish on `main` with nothing uncommitted |

## Expected output

Right after setup, all ten checks fail, each with a message naming the next action.
On completion the output matches `expected/on-completion.txt`; only the run time differs.

## Offline note

Setup and checks use only Git and the Python standard library.
There is no network call; the "remote" is the bare repository setup created in `starter/origin.git/`.

## Cleanup

When you are finished, run this from the lab folder:

```text
python tests/cleanup_lab.py
```

It deletes `starter/release-day/` and `starter/origin.git/` (including any file you
added there) and the Python cache in `tests/`, then rewrites the shipped starter
files exactly as they were shipped. It touches nothing outside this lab folder.

## Troubleshooting

| Symptom | What to do |
|---|---|
| `python: command not found`, or `python` opens the Microsoft Store | Go back to step 1: make `python` mean your Python 3 launcher for this terminal. |
| `The lab repository is missing` | Run `python tests/setup_lab.py` from the lab folder. |
| An editor opens after a Git command | You ran a commit, merge or revert without `--no-edit` or `-m`. Save and close the editor to accept the message. |
| `You have unstaged changes` when reverting | Stash first (step 4): revert wants a clean working copy. |
| `main` lost the debug commit entirely | You used `reset` on a shared commit. Rerun setup and use `git revert --no-edit` in step 5. |
| The pull in step 8 created a conflict in `README.md` or `status_message.py` | You edited a file on `main` by hand. Rerun setup and change only what the steps name. |
| `git merge main` stops with `CONFLICT` in step 9 | That is the exercise: resolve `RELEASE_NOTES.md` as step 9 shows, then `git add RELEASE_NOTES.md` and `git commit --no-edit`. |
| `git switch main` fails with `cannot switch branch while merging` | The step 9 merge is not finished: resolve the file, `git add` it and commit, or `git merge --abort` to start that merge again. |
| A check message gives Git commands | Run them inside the lab repository: from the lab folder, `cd starter/release-day` (cmd: `cd starter\release-day`). Afterwards, `cd ../..` and rerun the step 11 command. |
| A check says conflict markers remain | `git switch feature/release-notes`, delete every `<<<<<<<`, `=======` and `>>>>>>>` line in `RELEASE_NOTES.md`, `git add RELEASE_NOTES.md`, `git commit -m "Resolve the release-notes conflict"`, then repeat step 10. |
| A check says a v1.1 line is missing, doubled or not word for word | Same fix-forward: on `feature/release-notes`, make the v1.1 section match step 9 exactly, `git add RELEASE_NOTES.md`, commit with `-m`, then repeat step 10. |
| `WIP scratch` is still the tip of `feature/release-notes` | Run `git reset --hard HEAD~1` on that branch (step 7). If it already reached `main` or the remote, never reset `main`: rerun setup and remove it in step 7. |
| The push is rejected | Your `main` is behind: repeat step 8 (`git fetch origin`, then `git pull --no-edit origin main`). If that pull conflicts in `RELEASE_NOTES.md`, resolve it on `main` as step 9 shows (keep both bullets, `git add RELEASE_NOTES.md`, `git commit --no-edit`), then push again. |
| You are lost or past 25 minutes | Pause the exercise block and continue in self-study. If your lab state is broken, rerun `python tests/setup_lab.py` (it resets everything) and repeat the steps in order. |
