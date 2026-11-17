#!/usr/bin/env bash
set -euo pipefail

# Step 7: Make a local-only mistake and remove it with reset.
# Runs right after step 6: you are on feature/release-notes.
# TODO: commit a file scratch.tmp as "WIP scratch", then remove that commit
# and the file with reset. Nobody else has it, so rewriting is safe here.

