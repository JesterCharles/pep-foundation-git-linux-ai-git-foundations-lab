"""Trainer-authored tests — restored over the learner checkout at grade time.

One check per step. Each builds the release-day scenario in a temporary folder,
does the earlier steps for you correctly, runs your script for its own step
(src/stepN_*.sh) inside the clone, and inspects the result. Run one step with
`python -m pytest -q -k step6`.
"""

from test.support import (
    DEBUG_LINE,
    DEBUG_SUBJECT,
    FEATURE,
    MAIN,
    MARKERS,
    NOTES_SUBJECT,
    TEAMMATE_BULLET,
    TEAMMATE_SUBJECT,
    YOUR_BULLET,
    scenario_after_step,
)


def test_step4_stash(tmp_path):
    lab = scenario_after_step(tmp_path, 4)
    assert len(lab.stash_entries()) == 1, (
        "Step 4: the stash should hold exactly one entry: your half-written release notes. "
        "Put `git stash` in src/step4_stash.sh."
    )
    assert lab.status() == "", (
        "Step 4: the working copy is not clean after your script. `git stash` saves the "
        "uncommitted RELEASE_NOTES.md change and leaves nothing modified."
    )


def test_step5_revert(tmp_path):
    lab = scenario_after_step(tmp_path, 5)
    assert any(subject.startswith("Revert") for subject in lab.subjects(MAIN)), (
        "Step 5: main has no revert commit. The debug commit was pushed, so undo it with a new "
        "commit: put `git revert --no-edit HEAD` in src/step5_revert.sh."
    )
    assert DEBUG_LINE not in lab.file_at(MAIN, "status_message.py"), (
        f"Step 5: status_message.py on main still contains the debug print. Revert the "
        f"'{DEBUG_SUBJECT}' commit."
    )


def test_step6_release_notes(tmp_path):
    lab = scenario_after_step(tmp_path, 6)
    assert lab.branch_exists(FEATURE), (
        f"Step 6: the branch {FEATURE} does not exist. Start src/step6_release_notes.sh with "
        f"`git switch -c {FEATURE}`."
    )
    assert lab.commit_with_subject(FEATURE, NOTES_SUBJECT), (
        f"Step 6: {FEATURE} has no commit with the subject '{NOTES_SUBJECT}'. Commit with "
        f'`git commit -m "{NOTES_SUBJECT}"`.'
    )
    notes = lab.file_at(FEATURE, "RELEASE_NOTES.md")
    assert "TODO" not in notes, (
        "Step 6: RELEASE_NOTES.md on the feature branch still contains the TODO line. After "
        "`git stash pop`, write the finished file (the lab README shows it), then add and commit it."
    )
    assert YOUR_BULLET in notes, (
        f"Step 6: RELEASE_NOTES.md on the feature branch is missing your v1.1 bullet, word for word: {YOUR_BULLET!r}"
    )


def test_step7_scratch_reset(tmp_path):
    lab = scenario_after_step(tmp_path, 7)
    assert "commit: WIP scratch" in lab.reflog_subjects(FEATURE), (
        "Step 7: the scratch mistake was never made. src/step7_scratch_reset.sh first commits "
        "scratch.tmp as 'WIP scratch', then removes that commit with reset."
    )
    assert lab.out("log", "-1", "--format=%s", FEATURE) == NOTES_SUBJECT, (
        f"Step 7: the newest commit on {FEATURE} should be '{NOTES_SUBJECT}' again. The scratch "
        "commit was never shared, so remove it with `git reset --hard HEAD~1`."
    )


def test_step8_pull_teammate(tmp_path):
    lab = scenario_after_step(tmp_path, 8)
    assert lab.current_branch() == MAIN, (
        f"Step 8: you should end this step on {MAIN}. Start src/step8_pull_teammate.sh with "
        f"`git switch {MAIN}`."
    )
    assert TEAMMATE_SUBJECT in lab.subjects(MAIN), (
        "Step 8: the teammate's commit is not on your main. Run `git fetch origin`, then "
        f"`git pull --no-edit origin {MAIN}`."
    )


def test_step9_resolve_conflict(tmp_path):
    lab = scenario_after_step(tmp_path, 9)
    notes = lab.file_at(FEATURE, "RELEASE_NOTES.md")
    left = [line for line in notes.splitlines() if line.startswith(MARKERS)]
    assert left == [], (
        "Step 9: RELEASE_NOTES.md on the feature branch still contains conflict markers. Write "
        "the resolved file (both v1.1 bullets, no <<<<<<<, ======= or >>>>>>> lines), add it, "
        "then `git commit --no-edit`."
    )
    mine = lab.commit_with_subject(FEATURE, NOTES_SUBJECT)
    theirs = lab.commit_with_subject(FEATURE, TEAMMATE_SUBJECT)
    assert mine and theirs and lab.joining_merge(FEATURE, mine, theirs), (
        f"Step 9: no merge on {FEATURE} joins your release-notes commit with the teammate's. "
        f"Run `git switch {FEATURE}` and `git merge {MAIN} || true`, resolve, add and commit."
    )
    assert YOUR_BULLET in notes and TEAMMATE_BULLET in notes, (
        "Step 9: the resolved RELEASE_NOTES.md must keep both v1.1 bullets: yours and the "
        "teammate's. A resolution keeps the work of both sides."
    )


def test_step10_merge_and_push(tmp_path):
    lab = scenario_after_step(tmp_path, 10)
    assert lab.ok("merge-base", "--is-ancestor", FEATURE, MAIN), (
        f"Step 10: main does not contain {FEATURE}. Run `git switch {MAIN}`, then "
        f"`git merge {FEATURE}`."
    )
    assert lab.out("rev-parse", MAIN) == lab.out("rev-parse", f"refs/heads/{MAIN}", repo=lab.origin), (
        f"Step 10: origin's main does not match your main. Finish with `git push origin {MAIN}`."
    )
