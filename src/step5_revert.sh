#!/usr/bin/env bash
set -euo pipefail

# Step 5: Undo the shared debug commit with revert.
# Runs right after step 4: you are on main, your notes are stashed, and the
# newest commit is the debug print that was already pushed.
# TODO: undo that commit with a new commit, without rewriting history and
# without opening an editor.

