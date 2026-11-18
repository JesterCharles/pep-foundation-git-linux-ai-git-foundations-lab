"""Held-out tests: graded on submit, never shown to the learner.

Same approach as the visible checks: each builds the scenario, does the earlier
steps correctly, runs the learner's script for one step and checks the edge
cases. The last check runs every learner script in order, start to finish.
"""

import pytest

from test.support import (
    DEBUG_LINE,
    DEBUG_SUBJECT,
    FEATURE,
    FIRST_STEP,
    LAST_STEP,
    MAIN,
    MARKERS,
    NOTES_SUBJECT,
    TEAMMATE_BULLET,
    TEAMMATE_SUBJECT,
    V10_BULLET,
    YOUR_BULLET,
    build_scenario,
    note_lines,
    require_tools,
    run_step,
    scenario_after_step,
)


def test_step4_stash_holds_only_the_notes(tmp_path):
    lab = scenario_after_step(tmp_path, 4)
    assert lab.stash_entries(), "Step 4: the stash is empty. Put `git stash` in src/step4_stash.sh."
    assert lab.out("stash", "show", "--name-only", "stash@{0}").split() == ["RELEASE_NOTES.md"], (
        "Step 4: the stash entry should hold only your RELEASE_NOTES.md change."
    )
    assert lab.current_branch() == MAIN and lab.out("log", "-1", "--format=%s", MAIN) == DEBUG_SUBJECT, (
        "Step 4: stay on main and make no commit in this step: only set your notes aside."
    )


def test_step5_debug_commit_stays_in_history(tmp_path):
    lab = scenario_after_step(tmp_path, 5)
    subjects = lab.subjects(MAIN)
    assert any(subject.startswith("Revert") for subject in subjects), "Step 5: main has no revert commit."
    assert DEBUG_SUBJECT in subjects, (
        "Step 5: the debug commit is gone from main's history. It was pushed, so it is shared: "
        "undo it with `git revert`, never with reset."
    )
    assert DEBUG_LINE not in lab.file_at(MAIN, "status_message.py"), "Step 5: the debug print is still there."


def test_step6_commit_is_focused(tmp_path):
    lab = scenario_after_step(tmp_path, 6)
    own = lab.commit_with_subject(FEATURE, NOTES_SUBJECT) if lab.branch_exists(FEATURE) else None
    assert own, f"Step 6: {FEATURE} has no commit with the subject '{NOTES_SUBJECT}'."
    changed = lab.out("show", "--name-only", "--format=", own).split()
    assert changed == ["RELEASE_NOTES.md"], (
        f"Step 6: the release-notes commit changed {changed}. Stage only RELEASE_NOTES.md by "
        "name, never `git add .`."
    )
    assert any(subject.startswith("Revert") for subject in lab.subjects(FEATURE)), (
        f"Step 6: create {FEATURE} from main after the revert, so it starts from the fixed code."
    )


def test_step6_stash_is_empty(tmp_path):
    lab = scenario_after_step(tmp_path, 6)
    assert lab.stash_entries() == [], (
        "Step 6: the stash still holds an entry. Take your notes back with `git stash pop` "
        "(not `apply`, which leaves a copy behind)."
    )


def test_step7_scratch_is_fully_removed(tmp_path):
    lab = scenario_after_step(tmp_path, 7)
    assert "commit: WIP scratch" in lab.reflog_subjects(FEATURE), "Step 7: the scratch mistake was never made."
    assert lab.out("rev-list", "--all", "--", "scratch.tmp") == "", (
        "Step 7: a commit containing scratch.tmp is still reachable. Remove it with "
        "`git reset --hard HEAD~1`, not with revert: nobody else has it."
    )
    assert not (lab.repo / "scratch.tmp").exists() and lab.status() == "", (
        "Step 7: scratch.tmp is still in the working copy. `git reset --hard HEAD~1` removes "
        "the commit and the file it added."
    )


def test_step8_merge_keeps_both_sides(tmp_path):
    lab = scenario_after_step(tmp_path, 8)
    assert "## Support" in lab.file_at(MAIN, "README.md"), (
        "Step 8: README.md on main is missing the teammate's Support section. Pull origin/main into main."
    )
    subjects = lab.subjects(MAIN)
    assert any(subject.startswith("Revert") for subject in subjects), (
        "Step 8: your unpushed revert is no longer on main. Merge the teammate's work in with "
        "`git pull --no-edit`; do not reset main."
    )
    assert lab.out("rev-list", "--merges", "-n", "1", MAIN), (
        "Step 8: main has diverged from origin/main, so the pull should create a merge commit."
    )


def test_step9_resolution_is_exact(tmp_path):
    lab = scenario_after_step(tmp_path, 9)
    lines = note_lines(lab.file_at(FEATURE, "RELEASE_NOTES.md"))
    for bullet in (YOUR_BULLET, TEAMMATE_BULLET):
        assert lines.count(bullet) == 1, (
            f"Step 9: the resolved RELEASE_NOTES.md must contain this v1.1 line exactly once, "
            f"word for word: {bullet!r}"
        )
    assert lines.count("## v1.1") == 1, "Step 9: the resolved RELEASE_NOTES.md needs exactly one '## v1.1' heading."
    assert V10_BULLET in lines, "Step 9: keep the v1.0 entry as it was; only the conflict changes."
    assert not (lab.repo / ".git" / "MERGE_HEAD").exists() and lab.status() == "", (
        "Step 9: the merge is not finished. After writing the resolved file, "
        "`git add RELEASE_NOTES.md` and `git commit --no-edit`."
    )


def test_step10_finishes_clean_on_main(tmp_path):
    lab = scenario_after_step(tmp_path, 10)
    assert lab.current_branch() == MAIN, f"Step 10: finish on {MAIN}."
    assert lab.status() == "", "Step 10: uncommitted or untracked files remain after your script."
    notes = lab.file_at(MAIN, "RELEASE_NOTES.md")
    assert not [line for line in notes.splitlines() if line.startswith(MARKERS)], (
        "Step 10: RELEASE_NOTES.md on main contains conflict markers."
    )
    assert lab.out("rev-parse", MAIN) == lab.out("rev-parse", f"refs/heads/{MAIN}", repo=lab.origin), (
        "Step 10: origin's main does not match your main."
    )


def test_all_steps_in_order(tmp_path):
    """Run every learner script, start to finish, and check the final state."""
    require_tools()
    lab = build_scenario(tmp_path / "lab")
    for step in range(FIRST_STEP, LAST_STEP + 1):
        run_step(lab, step)
    subjects = lab.subjects(MAIN)
    problems = []
    if lab.current_branch() != MAIN or lab.status() != "":
        problems.append(f"finish on {MAIN} with a clean working copy")
    if DEBUG_SUBJECT not in subjects or DEBUG_LINE in lab.file_at(MAIN, "status_message.py"):
        problems.append("revert the debug commit (step 5)")
    if TEAMMATE_SUBJECT not in subjects or NOTES_SUBJECT not in subjects:
        problems.append("main must hold both your notes commit and the teammate's")
    if lab.stash_entries():
        problems.append("leave the stash empty (step 6)")
    if lab.out("rev-list", "--all", "--", "scratch.tmp"):
        problems.append("remove the scratch commit (step 7)")
    lines = note_lines(lab.file_at(MAIN, "RELEASE_NOTES.md"))
    if lines.count(YOUR_BULLET) != 1 or lines.count(TEAMMATE_BULLET) != 1:
        problems.append("keep both v1.1 bullets exactly once (step 9)")
    if lab.out("rev-parse", MAIN) != lab.out("rev-parse", f"refs/heads/{MAIN}", repo=lab.origin):
        problems.append("push main to origin (step 10)")
    if problems:
        pytest.fail(
            "All steps in order: running steps 4 to 10 one after another did not reach the "
            "finished state: " + "; ".join(problems) + ".",
            pytrace=False,
        )
