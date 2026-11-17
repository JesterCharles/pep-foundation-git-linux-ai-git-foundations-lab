"""Make a practice copy of the release-day scenario, outside this project folder.

    python -m test.sandbox              # the starting state (try step 3 and step 4 here)
    python -m test.sandbox --before 9   # steps 4 to 8 already done for you

It prints the folder to `cd` into. Try the step's commands there by hand, then
put them in that step's script in src/. Each run makes a new folder; nothing in
this project changes. To try your script in the practice copy, run it from
inside the clone: `bash <project>/src/step9_resolve_conflict.sh`.
"""

import argparse
import shutil
import sys
import tempfile
from pathlib import Path

from test.support import FIRST_STEP, LAST_STEP, SCRIPTS, SRC, apply_reference, build_scenario


def main(argv=None):
    parser = argparse.ArgumentParser(prog="python -m test.sandbox", description=__doc__.splitlines()[0])
    parser.add_argument(
        "--before",
        type=int,
        default=FIRST_STEP,
        choices=range(FIRST_STEP, LAST_STEP + 1),
        metavar="STEP",
        help=f"build the state just before this step ({FIRST_STEP}-{LAST_STEP}); default {FIRST_STEP}",
    )
    args = parser.parse_args(argv)
    for tool in ("bash", "git"):
        if shutil.which(tool) is None:
            sys.exit(f"`{tool}` was not found on PATH. Install it, then run this again.")

    root = Path(tempfile.mkdtemp(prefix="release-day-"))
    scenario = build_scenario(root)
    apply_reference(scenario, args.before)
    script = SRC / SCRIPTS[args.before]
    print(f"Practice copy ready, just before step {args.before}.")
    print(f"  your clone: {scenario.repo}")
    print(f"  the remote: {scenario.origin}")
    print(f"Next: cd {scenario.repo}")
    print(f"Try your script there with: bash {script}")


if __name__ == "__main__":
    main()
