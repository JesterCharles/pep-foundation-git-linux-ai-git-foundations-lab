#!/usr/bin/env bash
set -euo pipefail

# Step 9: Bring main into your branch and resolve the conflict.
# Runs right after step 8: you are on main, which now has the teammate's work.
# TODO: switch to feature/release-notes and merge main into it. The merge
# stops on a conflict in RELEASE_NOTES.md and exits with an error, so follow
# it with "|| true". Then write the resolved file (the lab README shows
# it), stage it and finish the merge commit without an editor.

