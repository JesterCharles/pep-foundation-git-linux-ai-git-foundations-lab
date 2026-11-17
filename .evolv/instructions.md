# Release day

The deploy status helper is about to get its v1.1 release. You were halfway through
the release notes when three things happened at once: someone pushed a debug print
straight to `main`, a teammate pushed a README update with their own line in the
release notes, and your half-written notes are still uncommitted.

You use Git to set your work aside, undo the shared mistake safely, finish your notes
on a branch, remove a local-only mistake, bring in the teammate's work, resolve a
merge conflict, merge, and push to the team's remote.

You write each step's Git commands in a small bash script in `src/`. The tests build
the release-day repository and its remote in a temporary folder, run your scripts
there, and check the result with Git.

- **Time:** about 25 minutes.
- **You need:** a terminal with bash and Git 2.23 or newer, and Python 3.12.
- **Offline:** the team's "remote" is a local folder. No account or network.

## Your path

```text
Run Tests: 7 fail -> practice a step -> write its script -> Run Tests -> ... -> 7 pass -> Submit
```

In words: run the tests and see all 7 fail, then for each of steps 4 to 10 try the
commands in a practice copy, put them in that step's script, and run the tests again.
Submit when all 7 visible tests pass.

## Quick start

1. **Open a terminal** with **Terminal > New Terminal**. It starts in the project
   folder, the one that holds `src/` and `test/`. Check your tools with
   `git --version` and `python --version`.
2. **Select Run Tests.** **All 7 tests fail at first. That is expected:** the scripts
   in `src/` are empty. Every failure message starts with its step, such as `Step 5:`.
3. **Open the scripts** in `src/`, one per step:

   | Step | Script |
   |---|---|
   | 4 | `src/step4_stash.sh` |
   | 5 | `src/step5_revert.sh` |
   | 6 | `src/step6_release_notes.sh` |
   | 7 | `src/step7_scratch_reset.sh` |
   | 8 | `src/step8_pull_teammate.sh` |
   | 9 | `src/step9_resolve_conflict.sh` |
   | 10 | `src/step10_merge_and_push.sh` |

   Each starts with `set -euo pipefail`, so it stops at the first command that fails.
   Write your commands below the `TODO` comment. Leave the first two lines as they are.
4. **Work through steps 3 to 10 in order** (the guide below). After each script,
   select **Run Tests** and read the remaining `Step N:` messages.
5. **You are finished when all 7 tests pass.** Then select **Submit**. Submitting also
   runs held-out tests you can't see: they try the edge cases of each step and run
   all your scripts one after another, start to finish.

**How each step is checked.** For the step 6 test, a fresh copy of the scenario is
built, steps 4 and 5 are done for it correctly (with the commands this guide shows),
and then only your `step6_release_notes.sh` runs. So each test judges one script, and
a mistake in one step never hides the others. To run one step's test from the project
folder:

```text
python -m pytest -q -k step6
```

**Practise first.** Make a practice copy of the release-day repository, outside this
project, and try the step's commands by hand before you write them down:

```text
python -m test.sandbox
python -m test.sandbox --before 9
```

**Expect:** `Practice copy ready, just before step 4.` (or 9) and the folder to `cd`
into. With `--before 9`, steps 4 to 8 are already done in that copy. Each run makes a
new copy, so you can always start again. To try your script in a practice copy, run
it from inside the clone, as the last line printed shows:
`bash <project>/src/step9_resolve_conflict.sh`.

## Step-by-step guide

The scripts run inside the release-day clone, one after another. Each section says
where the previous step left you.

### Step 3: See what is going on

This step has no script. In a practice copy (`python -m test.sandbox`, then `cd` into
the folder it prints), run:

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
uncommitted changes and leaves the working copy clean. In `src/step4_stash.sh`:

```bash
git stash
```

**Expect** (in a practice copy): `Saved working directory and index state ...`, then
`git status` shows a clean working copy and `git stash list` one entry. You take it
back in step 6.

### Step 5: Undo the shared debug commit with revert

Explore first, in a practice copy made with `--before 5`:

```text
git show --stat HEAD
git log --oneline origin/main
```

**Expect:** the debug commit is also the tip of `origin/main`. It was pushed, so
teammates may already have it, and rewriting it with `reset` would pull it out from
under them. The safe undo for a shared commit is a **new** commit that does the
opposite. In `src/step5_revert.sh`:

```bash
git revert --no-edit HEAD
```

**Expect:** a new commit `Revert "Add debug print for support"`. The `DEBUG` line is
gone from `status_message.py`, and `git log --oneline -3` still shows the original
debug commit below the revert: history was added to, not rewritten.

### Step 6: Finish the release notes on a branch

Create a branch from `main`, take your notes back, finish them, and commit only that
file. In a script you cannot open an editor, so write the whole finished file with a
heredoc: everything between `<<'EOF'` and the closing `EOF` line becomes the file.
In `src/step6_release_notes.sh`:

```bash
git switch -c feature/release-notes
git stash pop
cat > RELEASE_NOTES.md <<'EOF'
# Release notes

## v1.1

- The deployment name now comes from DEPLOY_ENV, with a development fallback.

## v1.0

- First release of the deploy status helper.
EOF
git add RELEASE_NOTES.md
git commit -m "Finish v1.1 release notes"
```

Your v1.1 bullet replaces the TODO line, word for word. Stage that one file by name,
never `git add .`. **Expect** (in a practice copy): `Switched to a new branch
'feature/release-notes'`, your notes come back, `git stash list` prints nothing, and
`git show --stat HEAD` lists only `RELEASE_NOTES.md`.

### Step 7: Make a local-only mistake and remove it with reset

Commit a scratch file by accident, the way it happens on real release days, then
remove it. Nobody else has that commit, so this is the one case where rewriting
history is safe. `reset --hard` moves the branch back one commit and makes the files
match. In `src/step7_scratch_reset.sh`:

```bash
echo scratch > scratch.tmp
git add scratch.tmp
git commit -m "WIP scratch"
git reset --hard HEAD~1
```

**Expect** (in a practice copy, before the reset): `git log --oneline origin/main..HEAD`
lists `WIP scratch` among the commits the remote does not have. After the reset, the
tip is `Finish v1.1 release notes` again and `scratch.tmp` is gone. (`--soft` would
have kept the file staged. Had `WIP scratch` been pushed, the answer would be
`revert`, as in step 5.)

### Step 8: Fetch, compare, and pull the teammate's work

Switch to `main` and download what is new, without changing your files yet. In a
practice copy made with `--before 8`, compare the two sides:

```text
git switch main
git fetch origin
git log --oneline main..origin/main
git log --oneline origin/main..main
```

**Expect:** the first log shows `Document the support rotation` (the remote has it,
you do not); the second shows your revert (you have it, the remote does not). `main`
is your branch; `origin/main` is your last copy of the remote's branch. The two have
diverged, so merge the teammate's commit in. In `src/step8_pull_teammate.sh`:

```bash
git switch main
git fetch origin
git pull --no-edit origin main
```

**Expect:** a merge line such as `Merge made by the 'ort' strategy.`, and `README.md`
now ends with a `## Support` section. (A rebase could replay your unpushed revert
instead, but this team merges, and you must never rebase commits other people already
have.)

### Step 9: Bring main into your branch and resolve the conflict

The teammate also added a v1.1 line to `RELEASE_NOTES.md`, in the same place as
yours. Settle that on your branch before `main` gets it. Try the merge in a practice
copy made with `--before 9`:

```text
git switch feature/release-notes
git merge main
```

**Expect:** `CONFLICT (content): Merge conflict in RELEASE_NOTES.md`, then
`Automatic merge failed; fix conflicts and then commit the result.` Both sides changed
the same lines, so Git cannot choose. `git status` lists
`both modified:   RELEASE_NOTES.md` under **Unmerged paths**, and the file shows:

```text
<<<<<<< HEAD
- The deployment name now comes from DEPLOY_ENV, with a development fallback.
=======
- The README now documents the support rotation.
>>>>>>> main
```

Above `=======` is your side (the branch you are on); below it is the teammate's line
from `main`. Both are true, so keep both. (In the practice copy, `git merge --abort`
puts the branch back.)

In a script, the conflicted merge exits with an error, and `set -e` would stop the
script there. `|| true` lets the script go on to resolve it. The resolution is the
whole file with both v1.1 bullets and all three marker lines gone; then mark it
resolved and finish the merge. In `src/step9_resolve_conflict.sh`:

```bash
git switch feature/release-notes
git merge main || true
cat > RELEASE_NOTES.md <<'EOF'
# Release notes

## v1.1

- The deployment name now comes from DEPLOY_ENV, with a development fallback.
- The README now documents the support rotation.

## v1.0

- First release of the deploy status helper.
EOF
git add RELEASE_NOTES.md
git commit --no-edit
```

**Expect:** the commit `Merge branch 'main' into feature/release-notes`.

### Step 10: Merge your branch and push

In `src/step10_merge_and_push.sh`:

```bash
git switch main
git merge feature/release-notes
git push origin main
```

**Expect:** the merge prints `Fast-forward`: your branch already contains everything
on `main`, so Git only moves `main` forward. The push prints `main -> main`.

### Step 11: Prove it

Select **Run Tests**. **Expect:** `7 passed`. Then select **Submit**.

## Reference

- **What the tests look at:** the real state of the release-day clone and its remote
  after your script runs: the stash, the revert, your focused notes commit, the removed
  scratch commit, the teammate's merge, the conflict resolution, the merge into
  `main`, and the push. Nothing uses the network.
- **Run Tests** runs `python -m pytest -q` in the project folder.
- **Settings:** the tests switch off your personal and system Git settings and give
  the clone a training name and email, LF line endings, no commit signing, standard
  conflict markers and merge on pull, so results are the same for everyone. A command
  that would open an editor accepts the default message instead.
- **Edit only the scripts in `src/`.** The tests in `test/` are restored to their
  original state before your work is graded, so changes to them do not count.

## Troubleshooting

| Problem | Fix |
|---|---|
| `bash` or `git` was not found | Use a Linux or macOS terminal, WSL, or Git Bash, and check `git --version` (2.23 or newer, for `git switch`). |
| `Step N: ... stopped with exit code 1` | A command in that script failed; its last output is shown under the message. Try the commands in a practice copy made with `--before N`. |
| `CONFLICT` ends your step 9 script | Write the merge line as `git merge main || true`. |
| `$'\r': command not found` in a practice copy | The script has Windows line endings. Switch the file to LF in the editor's status bar. (The tests handle this for you.) |
| An editor opens in a practice copy | The command had no `--no-edit` or `-m`. Save and close the editor to accept the message. |
| `You have unstaged changes` when reverting | Stash first (step 4). |
| The step 9 test says a v1.1 line is missing or doubled | Make the heredoc in `step9_resolve_conflict.sh` match the file shown in step 9 exactly. |
| `WIP scratch` is still the newest commit | Run `git reset --hard HEAD~1` right after the scratch commit (step 7). |
