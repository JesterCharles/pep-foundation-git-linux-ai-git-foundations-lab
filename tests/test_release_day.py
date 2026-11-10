"""Checks for the "Release day" lab. Run from the lab folder:

    python -m unittest discover -s tests -v

Each failure message names the next action.
"""

import unittest

from lab_support import FEATURE, MAIN, ORIGIN, REPO, git, out

SETUP_HINT = "Run `python tests/setup_lab.py` from the lab folder first."
DEBUG_LINE = "DEBUG: remove before release"
YOUR_BULLET = "- The deployment name now comes from DEPLOY_ENV, with a development fallback."
TEAMMATE_BULLET = "- The README now documents the support rotation."
MARKERS = ("<<<<<<<", "=======", ">>>>>>>")


def subjects(ref):
    return out("log", "--format=%s", ref).splitlines()


def file_at(ref, path):
    return out("show", f"{ref}:{path}")


def commit_with_subject(ref, subject):
    """The newest non-merge commit reachable from ref with exactly this subject, or None."""
    for line in out("log", "--no-merges", "--format=%H%x09%s", ref).splitlines():
        sha, _, text = line.partition("\t")
        if text == subject:
            return sha
    return None


def contains(ref, commit):
    return git("merge-base", "--is-ancestor", commit, ref, check=False).returncode == 0


def note_lines(text):
    return [line.strip() for line in text.splitlines() if line.strip()]


class ReleaseDayTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not (REPO / ".git").exists() or not ORIGIN.exists():
            raise unittest.SkipTest(f"The lab repository is missing. {SETUP_HINT}")

    def branch_exists(self, name):
        return git("rev-parse", "--verify", "--quiet", f"refs/heads/{name}", check=False).returncode == 0

    def require_feature_branch(self):
        self.assertTrue(
            self.branch_exists(FEATURE),
            f"The branch {FEATURE} does not exist yet. Create it with `git switch -c {FEATURE}`.",
        )

    def test_debug_commit_is_reverted(self):
        main_subjects = subjects(MAIN)
        self.assertIn(
            "Add debug print for support",
            main_subjects,
            "The debug commit is gone from main's history. It was pushed, so it is shared: "
            "undo it with `git revert --no-edit <commit>`, never with reset. Rerun setup and try again.",
        )
        self.assertTrue(
            any(subject.startswith("Revert") for subject in main_subjects),
            "main has no revert commit yet. Undo the shared debug commit with "
            "`git revert --no-edit HEAD` while on main.",
        )
        self.assertNotIn(
            DEBUG_LINE,
            file_at(MAIN, "status_message.py"),
            "status_message.py on main still contains the debug print. "
            "Run `git revert --no-edit <commit of the debug print>`.",
        )

    def test_teammate_update_is_merged(self):
        self.assertIn(
            "Document the support rotation",
            subjects(MAIN),
            "The teammate's commit is not on your main yet. "
            "Run `git fetch origin`, compare with `git log --oneline main..origin/main`, "
            "then `git pull --no-edit origin main`.",
        )
        self.assertIn(
            "## Support",
            file_at(MAIN, "README.md"),
            "README.md on main is missing the Support section the teammate pushed. "
            "Pull origin/main into main.",
        )

    def test_release_notes_are_finished(self):
        self.require_feature_branch()
        notes = file_at(FEATURE, "RELEASE_NOTES.md")
        self.assertNotIn(
            "TODO",
            notes,
            "RELEASE_NOTES.md still contains the TODO line. Pop your stash on the feature branch, "
            "replace the TODO line with your v1.1 bullet from the README, then commit.",
        )
        self.assertIn(
            "DEPLOY_ENV",
            notes,
            "RELEASE_NOTES.md does not mention the DEPLOY_ENV change. Add your v1.1 bullet "
            "from step 6 of the README (Finish the release notes on a branch).",
        )

    def test_feature_branch_commit_is_focused(self):
        self.require_feature_branch()
        own = [
            line.split("\t", 1)[0]
            for line in out("log", "--no-merges", "--format=%H%x09%s", FEATURE).splitlines()
            if line.split("\t", 1)[1] == "Finish v1.1 release notes"
        ]
        self.assertTrue(
            own,
            f"{FEATURE} has no commit with the subject 'Finish v1.1 release notes'. "
            "If your commit is only worded differently and you have not merged yet, fix the "
            'message with `git commit --amend -m "Finish v1.1 release notes"` while it is the '
            "newest commit on the feature branch; otherwise rerun setup and repeat the steps.",
        )
        changed = out("show", "--name-only", "--format=", own[0]).split()
        self.assertEqual(
            ["RELEASE_NOTES.md"],
            changed,
            f"The release-notes commit changed {changed}. Stage only RELEASE_NOTES.md by name, "
            "never `git add .`. Rerun setup if you need a clean start.",
        )

    def test_scratch_mistake_is_fully_removed(self):
        self.require_feature_branch()
        holding = out("rev-list", "--all", "--", "scratch.tmp")
        if holding:
            if out("log", "-1", "--format=%s", FEATURE) == "WIP scratch":
                hint = (
                    "Nobody else has it yet, so remove it with `git reset --hard HEAD~1` "
                    f"while on {FEATURE} (step 7)."
                )
            elif git("merge-base", "--is-ancestor", holding.split()[0], MAIN, check=False).returncode == 0:
                hint = (
                    "It has already reached main (and may be pushed), so never reset main now. "
                    "Rerun `python tests/setup_lab.py` and repeat the steps, removing the scratch "
                    "commit in step 7, before you go back to main in step 8."
                )
            else:
                hint = (
                    "Remove it with `git reset --hard HEAD~1` on the branch whose newest commit "
                    "it is, as long as that branch was never merged or pushed."
                )
            self.fail(f"A commit containing scratch.tmp is still reachable. {hint}")
        self.assertFalse(
            (REPO / "scratch.tmp").exists(),
            "scratch.tmp is still in the working copy. `git reset --hard HEAD~1` removes the "
            "commit and the file it added; if you only created the file, delete it.",
        )

    def test_release_notes_conflict_is_resolved(self):
        self.require_feature_branch()
        repeat = (
            "From the lab folder, `cd starter/release-day` (cmd: `cd starter\\release-day`), "
            "then fix it in a new commit on feature/release-notes "
            "(`git switch feature/release-notes`, edit, `git add RELEASE_NOTES.md`, "
            '`git commit -m "Resolve the release-notes conflict"`), then repeat step 10 '
            "(`git switch main`, `git merge feature/release-notes`, `git push origin main`). "
            "If you resolved the merge directly on main instead, fix and commit on main, "
            "then push. Finally `cd ../..` and rerun the checks (step 11)."
        )
        notes = file_at(MAIN, "RELEASE_NOTES.md")
        left = [line for line in notes.splitlines() if line.startswith(MARKERS)]
        self.assertEqual(
            [],
            left,
            "RELEASE_NOTES.md on main still contains conflict markers. Delete every "
            "<<<<<<<, ======= and >>>>>>> line and keep both v1.1 bullets. " + repeat,
        )
        mine = commit_with_subject(MAIN, "Finish v1.1 release notes")
        theirs = commit_with_subject(MAIN, "Document the support rotation")
        self.assertTrue(
            mine and theirs,
            "main does not yet hold both your 'Finish v1.1 release notes' commit and the "
            "teammate's 'Document the support rotation' commit. Finish steps 6-10 of the README "
            "first; the other failing checks name the missing step.",
        )
        joined = None
        for merge in out("rev-list", "--merges", MAIN).split():
            parents = out("rev-list", "--parents", "-n", "1", merge).split()[1:]
            if len(parents) != 2:
                continue
            has = [(contains(parent, mine), contains(parent, theirs)) for parent in parents]
            if (True, False) in has and (False, True) in has:
                joined = merge
                break
        self.assertIsNotNone(
            joined,
            "No merge on main joins your release-notes commit with the teammate's. From the "
            f"lab folder, `cd starter/release-day`, then run `git switch {FEATURE}` and "
            f"`git merge {MAIN}`, resolve the conflict in RELEASE_NOTES.md and commit it "
            "(step 9 of the README), then merge the branch into main and push (step 10).",
        )
        lines = note_lines(notes)
        for bullet in (YOUR_BULLET, TEAMMATE_BULLET):
            self.assertEqual(
                1,
                lines.count(bullet),
                "RELEASE_NOTES.md on main must contain this v1.1 line exactly once, word for "
                f"word: {bullet!r}. A resolution keeps the work of both sides (step 9). " + repeat,
            )
        self.assertEqual(
            1,
            lines.count("## v1.1"),
            "RELEASE_NOTES.md on main must have exactly one '## v1.1' heading. " + repeat,
        )
        self.assertIn(
            "- First release of the deploy status helper.",
            lines,
            "The v1.0 entry is missing from RELEASE_NOTES.md on main. Keep the lines outside "
            "the conflict as they were. " + repeat,
        )

    def test_feature_is_merged_into_main(self):
        self.require_feature_branch()
        merged = git("merge-base", "--is-ancestor", FEATURE, MAIN, check=False)
        self.assertEqual(
            0,
            merged.returncode,
            f"main does not contain {FEATURE} yet. Run `git switch {MAIN}`, then "
            f"`git merge {FEATURE}` (step 10 of the README).",
        )

    def test_main_is_pushed_to_origin(self):
        local = out("rev-parse", MAIN)
        remote = out("rev-parse", f"refs/heads/{MAIN}", repo=ORIGIN)
        self.assertEqual(
            local,
            remote,
            "origin's main does not match your main. Finish the earlier steps, then run "
            "`git push origin main`.",
        )

    def test_stash_is_empty_after_restore(self):
        self.require_feature_branch()
        if not out("stash", "list"):
            return
        committed = "Finish v1.1 release notes" in subjects(FEATURE)
        self.fail(
            "The stash still holds an entry. "
            + (
                "Your notes are already committed, so the entry is a leftover copy (for "
                "example after `git stash apply`). From the lab folder, "
                "`cd starter/release-day`, remove it with `git stash drop`, then `cd ../..` "
                "and rerun the checks."
                if committed
                else "Pop your release-notes work with `git stash pop` on the feature branch "
                "and finish step 6 of the README (Finish the release notes on a branch)."
            )
        )

    def test_worktree_is_clean_and_on_main(self):
        self.assertEqual(
            MAIN,
            out("symbolic-ref", "--short", "HEAD"),
            f"Finish on branch {MAIN}: run `git switch {MAIN}` after merging.",
        )
        self.assertEqual(
            "",
            out("status", "--porcelain"),
            "Uncommitted or untracked files remain: `git status` shows what is left. "
            "Commit what belongs in the lab commits and remove anything you added by hand.",
        )


if __name__ == "__main__":
    unittest.main()
