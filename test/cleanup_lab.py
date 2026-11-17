"""Remove everything the lab created.

Run from the lab folder:  python test/cleanup_lab.py
It deletes src/release-day/ and src/origin.git/ (including any file you
added there) and the Python cache in test/. It touches nothing outside this lab folder.
"""

import sys
from pathlib import Path

# Run as a script (python test/cleanup_lab.py): put the project folder on the import
# path so the shared helpers load as test.lab_support, the name pytest uses.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from test.lab_support import reset_starter, restore_starter_files


def main():
    reset_starter()
    restore_starter_files()
    print("Lab cleaned: the lab repository, its local remote and your local work are removed.")
    print("The shipped starter files are restored. Run python test/setup_lab.py to start again.")


if __name__ == "__main__":
    main()
