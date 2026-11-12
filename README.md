# Release day

The deploy status helper is about to get its v1.1 release. You were halfway through
the release notes when three things happened at once: someone pushed a debug print
straight to `main`, a teammate pushed a README update with their own line in the
release notes, and your half-written notes are still uncommitted.

You use Git to set your work aside, undo the shared mistake safely, finish your notes
on a branch, remove a local-only mistake, bring in the teammate's work, resolve a
merge conflict, merge, and push to the team's remote.

- **Time:** about 21 minutes. If you pass 25, pause and finish in self-study.
- **You need:** Git 2.23 or newer and Python 3.11 or newer.
- **Offline:** the team's "remote" is a local folder. No account, network, container
  or AI assistant.

## Your path

```text
Open project -> Set up -> Tests: 10 fail -> Steps 3-10 -> Tests: 10 ok -> Stop
```

In words: open the project, set it up and see all 10 checks fail, work through
steps 3 to 10 in order, then run the checks again and stop when all 10 pass.

## Quick start

1. **Open the project.** Open this lab's folder in VS Code. It is already on your
   machine, so you do not need to clone anything. Open a terminal with
   **Terminal > New Terminal**; it starts in the project folder, the one that holds
   this README. Check your tools with `git --version` and `python --version`.
2. **Set up, then run the starter tests:**

   ```text
   python tests/setup_lab.py
   python -m unittest discover -s tests -v
   ```

   **Expect:** `Lab ready in starter/release-day/ on branch main, with a local remote
   in starter/origin.git.`, then all 10 checks `FAIL`. That is normal before you
   start: each failure message names what is missing. Now move into the lab
   repository, where steps 3 to 10 happen: `cd starter/release-day`
3. **See what is going on** with `git status`, `git diff` and `git log`.
4. **Set your work aside with stash.**
5. **Undo the shared debug commit with revert.** Check name: `reverted`.
6. **Finish the release notes on a branch:** take your notes back, replace the TODO
   line in `RELEASE_NOTES.md` with your v1.1 bullet, and commit only that file.
   Check names: `stash`, `finished`, `focused`.
7. **Make a local-only mistake and remove it with reset.** Check name: `scratch`.
8. **Fetch, compare, and pull the teammate's work** into `main`. Check name:
   `teammate`.
9. **Bring main into your branch and resolve the conflict** in `RELEASE_NOTES.md`
   so both v1.1 bullets stay.
10. **Merge your branch and push.** Check names: `conflict`, `merged_into_main`,
    `pushed`.
11. **Prove it:** go back to the project folder and run every check:

    ```text
    cd ../..
    python -m unittest discover -s tests -v
    ```

    **Expect:** all 10 checks report `ok`, then `OK`. You are done: stop here.

**Check one step at a time.** From `starter/release-day`, put the step's check names
after `-k`:

```text
python -m unittest discover -s ../../tests -v -k finished -k focused
```

**Expect:** those checks report `ok`. If one says `FAIL`, read the message under it.
Step 9 has no check of its own: the conflict check reads `main`, so it passes after
step 10.

## Step-by-step guide

Steps 3 to 10 run in the lab repository, `starter/release-day`. Do them in order.

### Step 3: See what is going on

```text
git status
git diff
git log --oneline -3
```

**Expect:** you are `On branch main`; `RELEASE_NOTES.md` is modified but not staged
(your half-written notes, with a TODO line); and the newest commit is
`Add debug print for support`, the mistake someone already pushed.

### Step 4: Set your work aside with stash

The debug print is urgent and your notes are in the way. `git stash` saves your
uncommitted changes and leaves the working copy clean:

```text
git stash
git status
```

**Expect:** `Saved working directory and index state ...`, then a clean working copy.
`git stash list` shows one entry; you take it back in step 6.

### Step 5: Undo the shared debug commit with revert

```text
git show --stat HEAD
git log --oneline origin/main
```

**Expect:** the debug commit is also the tip of `origin/main`. It was pushed, so
teammates may already have it, and rewriting it with `reset` would pull it out from
under them. The safe undo for a shared commit is a **new** commit that does the
opposite:

```text
git revert --no-edit HEAD
```

**Expect:** a new commit `Revert "Add debug print for support"`. The `DEBUG` line is
gone from `status_message.py`, and `git log --oneline -3` still shows the original
debug commit below the revert: history was added to, not rewritten.

### Step 6: Finish the release notes on a branch

Create a branch from `main` and take your notes back:

```text
git switch -c feature/release-notes
git stash pop
```

**Expect:** `Switched to a new branch 'feature/release-notes'`, your
`RELEASE_NOTES.md` edit is back, and `git stash list` prints nothing.

Open `RELEASE_NOTES.md` and replace the whole TODO line with this bullet, word for
word:

```text
- The deployment name now comes from DEPLOY_ENV, with a development fallback.
```

Stage that one file by name (never `git add .` here), check it, and commit:

```text
git add RELEASE_NOTES.md
git status
git diff --staged
git commit -m "Finish v1.1 release notes"
```

**Expect:** one staged file before the commit.

### Step 7: Make a local-only mistake and remove it with reset

Commit a scratch file by accident, the way it happens on real release days:

```text
echo scratch > scratch.tmp
git add scratch.tmp
git commit -m "WIP scratch"
git log --oneline origin/main..HEAD
```

**Expect:** `WIP scratch` is among the commits the remote does not have. Nobody else
has it, so this is the one case where rewriting history is safe. `reset --hard`
moves the branch back one commit and makes the files match:

```text
git reset --hard HEAD~1
git log --oneline -1
```

**Expect:** the tip is `Finish v1.1 release notes` again and `scratch.tmp` is gone.
(`--soft` would have kept the file staged. Had `WIP scratch` been pushed, the answer
would be `revert`, as in step 5.)

### Step 8: Fetch, compare, and pull the teammate's work

Switch to `main` and download what is new, without changing your files yet:

```text
git switch main
git fetch origin
git log --oneline main..origin/main
git log --oneline origin/main..main
```

**Expect:** the first log shows `Document the support rotation` (the remote has it,
you do not); the second shows your revert (you have it, the remote does not).
`main` is your branch; `origin/main` is your last copy of the remote's branch. The
two have diverged, so merge the teammate's commit in:

```text
git pull --no-edit origin main
```

**Expect:** a merge line such as `Merge made by the 'ort' strategy.` (older Git says
`'recursive'`), and `README.md` now ends with a `## Support` section.
`git log --oneline --graph -5` shows the merge commit joining the two lines. (A
rebase could replay your unpushed revert instead, but this team merges, and you must
never rebase commits other people already have.)

### Step 9: Bring main into your branch and resolve the conflict

The teammate also added a v1.1 line to `RELEASE_NOTES.md`, in the same place as
yours. Settle that on your branch before `main` gets it:

```text
git switch feature/release-notes
git merge main
```

**Expect:** `CONFLICT (content): Merge conflict in RELEASE_NOTES.md`, then
`Automatic merge failed; fix conflicts and then commit the result.` Both sides
changed the same lines, so Git cannot choose. `git status` lists
`both modified:   RELEASE_NOTES.md` under **Unmerged paths**.

Open `RELEASE_NOTES.md`. Its v1.1 section looks like this:

```text
<<<<<<< HEAD
- The deployment name now comes from DEPLOY_ENV, with a development fallback.
=======
- The README now documents the support rotation.
>>>>>>> main
```

Above `=======` is your side (the branch you are on); below it is the teammate's
line from `main`. Both are true, so keep both. Edit the file until the v1.1 section
reads exactly like this, with all three marker lines deleted:

```text
## v1.1

- The deployment name now comes from DEPLOY_ENV, with a development fallback.
- The README now documents the support rotation.
```

VS Code may show buttons such as **Accept Both Changes** above the markers. You may
use them; then check the result matches the text above with no marker left.

Save, then mark the conflict resolved and finish the merge:

```text
git add RELEASE_NOTES.md
git status
git commit --no-edit
```

**Expect:** `All conflicts fixed but you are still merging.`, then the commit
`Merge branch 'main' into feature/release-notes`. (Before that commit,
`git merge --abort` puts the branch back so you can start the merge again.)

### Step 10: Merge your branch and push

```text
git switch main
git merge feature/release-notes
git push origin main
```

**Expect:** the merge prints `Fast-forward`: your branch already contains everything
on `main`, so Git only moves `main` forward. The push prints `main -> main`. Now do
step 11.

## Reference

- **What the 10 checks look at:** the real state of the lab repository and its
  remote: the revert, the teammate's merge, your finished and focused notes commit,
  the conflict resolution on `main`, the scratch mistake, the merge into `main`, the
  push, the empty stash, and a clean working copy on `main`. Nothing uses the
  network.
- **Expected output:** when everything passes, the output matches
  `expected/on-completion.txt`; only the run time differs.
- **Lab settings:** setup never changes your own Git settings. It gives the two lab
  repositories a training name and email and a few lab-only settings so results are
  predictable: LF line endings, no commit signing, standard conflict markers, merge
  on pull, and an empty ignore file so your personal ignore rules cannot hide lab
  files. On Git older than 2.32, setup can still read personal settings such as
  hooks.
- **Start again:** from the project folder, `python tests/setup_lab.py` deletes
  `starter/release-day/` and `starter/origin.git/` (including any file you added
  there) and rebuilds them.
- **Clean up when finished:** from the project folder, `python tests/cleanup_lab.py`
  deletes both lab repositories and restores the shipped starter files.
- **Leave these as they are:** `tests/`, `fixtures/` and `expected/`.

## Troubleshooting

| Problem | Fix |
|---|---|
| `python: command not found`, or a version older than 3.11 | Run `python3 --version` (Windows: `py -3 --version`). If it shows 3.11 or newer, type `alias python=python3` once in this terminal (PowerShell: `Set-Alias python py`; cmd: `doskey python=py -3 $*`). |
| A test command fails with `No such file or directory` or finds no tests | Use `-s tests` in the project folder and `-s ../../tests` in `starter/release-day`. |
| `The lab repository is missing` | From the project folder, run `python tests/setup_lab.py`. |
| Windows cmd or PowerShell | Use `cd starter\release-day` and `cd ..\..` in cmd. To create the scratch file in step 7: PowerShell `Set-Content scratch.tmp scratch`; cmd `echo scratch> scratch.tmp`. |
| An editor opens after a Git command | The command had no `--no-edit` or `-m`. Save and close the editor to accept the message. |
| `You have unstaged changes` when reverting | Stash first (step 4). |
| `main` lost the debug commit entirely | You used `reset` on a shared commit. Rerun setup and use `git revert --no-edit` in step 5. |
| The pull in step 8 conflicts in `README.md` or `status_message.py` | You edited a file on `main` by hand. Rerun setup and change only what the steps name. |
| `git switch main` fails with `cannot switch branch while merging` | Finish step 9 first (resolve, `git add`, commit), or `git merge --abort` and start that merge again. |
| A check message gives Git commands | Run them in `starter/release-day`, then rerun the checks. |
| A check says conflict markers remain, or a v1.1 line is missing, doubled or not word for word | On `feature/release-notes`, make the v1.1 section match step 9 exactly, `git add RELEASE_NOTES.md`, `git commit -m "Resolve the release-notes conflict"`, then repeat step 10. |
| `WIP scratch` is still the tip of `feature/release-notes` | Run `git reset --hard HEAD~1` on that branch (step 7). If it already reached `main` or the remote, never reset `main`: rerun setup instead. |
| The push is rejected | Your `main` is behind: repeat step 8. If that pull conflicts in `RELEASE_NOTES.md`, resolve it on `main` as in step 9, then push again. |
| Your lab state is broken | From the project folder, run `python tests/setup_lab.py`, then repeat the steps in order. |

## Optional: work on your own computer

You only need this if you were not given the project. Clone
`https://github.com/JesterCharles/pep-foundation-git-linux-ai-git-foundations-lab`,
open the cloned folder in VS Code or another editor, and start at **Quick start**.
